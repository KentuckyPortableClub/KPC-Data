#!/usr/bin/env python3
"""KPC 11: Boundary Change Watcher.

Once a week, compares every park's outline on the agency's live layer with
last run's fingerprint (area, box, point count) and lists the parks whose
outline changed. A HELPER: it writes reports only, never a key, an outline or
a 2-fer. Example:  python kpc_boundary_watch.py --data club-data --areas US-KY
"""
# ---------------------------------------------------------------------------
# Shared helpers (the same block is copied into each KPC tool so every tool
# stays one file). Polite fetching, cache, club-file reading, shapes.
# ---------------------------------------------------------------------------
import argparse
import datetime as _dt
import glob
import gzip
import hashlib
import json
import math
import os
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.robotparser

import requests
from pyproj import Geod, Transformer
from shapely import make_valid
from shapely.geometry import (GeometryCollection, LineString, MultiLineString,
                              MultiPolygon, Polygon, mapping, shape)
from shapely.geometry.polygon import orient
import shapely
from shapely.ops import unary_union


def shp_transform(fn, geom):
    """Re-project a shape with a pyproj transform function."""
    return shapely.transform(geom, lambda x, y: fn(x, y), interleaved=False)


EXIT_DONE, EXIT_BAD_INPUT, EXIT_RUN_AGAIN = 0, 2, 3
CLUB_URL = "https://github.com/KentuckyPortableClub"
GEOD = Geod(ellps="WGS84")
SQM_PER_ACRE = 4046.8564224
DEG_PER_M = 1.0 / 111320.0           # rough metres -> degrees (latitude)
LIVE_FOLDERS = ("us-key", "ca-key", "canada-bounds", "world-bounds", "fers",
                "trails", "parkinfo", "ky-answer-key.json", "world-key")


def today():
    return _dt.date.today().isoformat()


def now_iso():
    return _dt.datetime.now().replace(microsecond=0).isoformat()


def log(msg):
    print(msg, flush=True)


class BadInput(Exception):
    """Bad command line or missing club files: exit 2."""


class SourceProblem(Exception):
    """kind = 'SOURCE DOWN' | 'LAYER MOVED' | 'BAD ANSWER' | 'BLOCKED BY ROBOTS'."""

    def __init__(self, kind, why):
        super().__init__(f"{kind}: {why}")
        self.kind, self.why = kind, why


class OutOfTime(Exception):
    """The --max-minutes budget is used up: save and exit 3."""


class Clock:
    def __init__(self, max_minutes):
        self.start = time.time()
        self.limit = max_minutes * 60.0 if max_minutes else None

    def left(self):
        return None if self.limit is None else self.limit - (time.time() - self.start)

    def check(self, need_s=20):
        left = self.left()
        if left is not None and left < need_s:
            raise OutOfTime()


# ----------------------------- polite web ----------------------------------
class Polite:
    """At most 1 request per second per host, a KPC User-Agent, back-off on
    429/5xx, robots.txt for web pages, and a dated cache of what was read."""

    def __init__(self, tool, cache_dir, offline=False, gap_s=1.0, timeout=60,
                 retries=4, session=None, sleep=time.sleep, clock=None):
        self.ua = f"KPC-{tool} ({CLUB_URL})"
        self.cache_dir, self.offline = cache_dir, offline
        self.gap_s, self.timeout, self.retries = gap_s, timeout, retries
        self.session = session or requests.Session()
        self.session.headers["User-Agent"] = self.ua
        self.sleep, self.clock = sleep, clock
        self.last_hit, self.robots = {}, {}
        self.requests_made = 0

    # -- cache --
    def _cache_path(self, url, params):
        key = url + "?" + urllib.parse.urlencode(sorted((params or {}).items()))
        h = hashlib.sha1(key.encode()).hexdigest()
        host = urllib.parse.urlsplit(url).netloc.replace(":", "_")
        return os.path.join(self.cache_dir, host, h[:2], h + ".json.gz")

    def _cache_read(self, url, params, max_age_s):
        p = self._cache_path(url, params)
        if not os.path.exists(p):
            return None
        try:
            with gzip.open(p, "rt", encoding="utf-8") as f:
                rec = json.load(f)
        except (OSError, ValueError):
            return None
        if max_age_s is not None and time.time() - rec.get("t", 0) > max_age_s:
            return None
        return rec

    def _cache_write(self, url, params, data):
        p = self._cache_path(url, params)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        tmp = p + ".tmp"
        with gzip.open(tmp, "wt", encoding="utf-8") as f:
            json.dump({"url": url, "params": params, "read": now_iso(),
                       "t": time.time(), "data": data}, f)
        os.replace(tmp, p)

    # -- manners --
    def _wait_turn(self, host):
        last = self.last_hit.get(host)
        if last is not None:
            wait = self.gap_s - (time.time() - last)
            if wait > 0:
                self.sleep(wait)
        self.last_hit[host] = time.time()

    @staticmethod
    def is_api(url):
        return "/rest/services" in url or "api.pota.app" in url

    def robots_ok(self, url):
        """robots.txt is obeyed for web pages (APIs are not web pages)."""
        if self.is_api(url):
            return True
        parts = urllib.parse.urlsplit(url)
        base = f"{parts.scheme}://{parts.netloc}"
        if base not in self.robots:
            rp = urllib.robotparser.RobotFileParser()
            try:
                self._wait_turn(parts.netloc)
                r = self.session.get(base + "/robots.txt", timeout=self.timeout)
                rp.parse(r.text.splitlines() if r.status_code == 200 else [])
            except requests.RequestException:
                rp.parse([])
            self.robots[base] = rp
        return self.robots[base].can_fetch(self.ua, url)

    def get_json(self, url, params=None, max_age_s=None, use_cache=True):
        """Return parsed JSON. Raises SourceProblem. ArcGIS 'error' bodies
        that say the service is missing become LAYER MOVED."""
        params = dict(params or {})
        if use_cache:
            rec = self._cache_read(url, params, max_age_s)
            if rec is not None:
                return rec["data"]
        if self.offline:
            raise SourceProblem("SOURCE DOWN", "offline mode and nothing saved in the cache for this address")
        if not self.robots_ok(url):
            raise SourceProblem("BLOCKED BY ROBOTS", "the site's robots.txt asks bots not to read this page")
        host = urllib.parse.urlsplit(url).netloc
        delay, last_err = 2.0, ""
        for attempt in range(self.retries + 1):
            if self.clock is not None:
                self.clock.check(need_s=10)
            self._wait_turn(host)
            self.requests_made += 1
            try:
                r = self.session.get(url, params=params, timeout=self.timeout)
            except requests.RequestException as e:
                last_err = f"no answer from {host} ({type(e).__name__})"
                self.sleep(delay)
                delay *= 2
                continue
            if r.status_code == 404:
                raise SourceProblem("LAYER MOVED", f"{host} says this address does not exist (HTTP 404)")
            if r.status_code == 429 or r.status_code >= 500:
                last_err = f"{host} answered HTTP {r.status_code}"
                ra = r.headers.get("Retry-After", "")
                self.sleep(float(ra) if ra.isdigit() else delay)
                delay *= 2
                continue
            if r.status_code >= 400:
                raise SourceProblem("SOURCE DOWN", f"{host} answered HTTP {r.status_code}")
            try:
                data = r.json()
            except ValueError:
                last_err = f"{host} sent something that is not JSON"
                self.sleep(delay)
                delay *= 2
                continue
            err = data.get("error") if isinstance(data, dict) else None
            if err:
                msg = str(err.get("message", "")) + " " + " ".join(map(str, err.get("details") or []))
                code = err.get("code")
                if code == 404 or re.search(r"not found|does not exist|invalid url", msg, re.I):
                    raise SourceProblem("LAYER MOVED", f"the server says: {msg.strip()[:160]}")
                if code in (429, 500, 502, 503, 504) and attempt < self.retries:
                    last_err = f"the server says: {msg.strip()[:160]}"
                    self.sleep(delay)
                    delay *= 2
                    continue
                raise SourceProblem("BAD ANSWER", f"the server says: {msg.strip()[:160]}")
            if use_cache:
                self._cache_write(url, params, data)
            return data
        raise SourceProblem("SOURCE DOWN", last_err or f"{host} did not answer")


# ----------------------------- names ---------------------------------------
TYPE_WORDS = set("""
state national provincial federal park parks nature preserve preserves natural area areas wildlife
management refuge nwr wma sna snp sp srp nhp nhs nm nra wsr nf forest forests recreation recreational historic
historical site sites battlefield monument memorial resort conservation reserve reserves sanctuary
wilderness public hunting fishing access lake lakes trail scenic class unit tract
of the and at on in de du la le les des et di del der am im
canada canadian ontario kentucky tennessee
""".split())
# 'lake' is dropped because "X Lake State Park" and "X Lake WMA" are the usual
# same-name family; 'river' is kept because it is usually part of the name.

ABBREV = {"wma": "wildlife management area", "sna": "state natural area",
          "snp": "state nature preserve", "nwr": "national wildlife refuge",
          "sp": "state park", "nf": "national forest", "nra": "national recreation area",
          "st": "saint", "ste": "sainte", "mt": "mount", "ft": "fort", "pp": "provincial park",
          "ca": "conservation area", "nha": "national historic area"}


def strip_accents(s):
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


def light_name(s):
    """Lower case, no accents, no punctuation, common short forms spelled out."""
    s = strip_accents(str(s or "")).lower().replace("&", " and ")
    s = re.sub(r"[’'`]", "", s)
    s = re.sub(r"[^a-z0-9]+", " ", s)
    out = []
    for t in s.split():
        out.extend(ABBREV.get(t, t).split())
    return " ".join(out)


def core_name(s):
    """Names normalised for S3: initials, accents and type words dropped."""
    raw = strip_accents(str(s or ""))
    raw = re.sub(r"\(.*?\)", " ", raw)                 # drop bracketed notes
    raw = re.sub(r"\b([A-Za-z])\.\s*", " ", raw)       # E.P. -> dropped initials
    toks = light_name(raw).split()
    toks = [t for t in toks if len(t) > 1 and t not in TYPE_WORDS]
    return " ".join(toks)


# ----------------------------- shapes --------------------------------------
def _signed_area(ring):
    a = 0.0
    for (x1, y1), (x2, y2) in zip(ring, ring[1:] + ring[:1]):
        a += x1 * y2 - x2 * y1
    return a / 2.0


def esri_to_shape(g):
    """ArcGIS JSON geometry -> shapely. Outer rings are clockwise in ArcGIS."""
    if not g:
        return None
    if "rings" in g:
        rings = [[tuple(p[:2]) for p in r] for r in g["rings"] if len(r) >= 4]
        outers = [r for r in rings if _signed_area(r) < 0]
        holes = [r for r in rings if _signed_area(r) >= 0]
        if not outers:                       # server ignored the convention
            outers, holes = holes, []
        polys = [[Polygon(o), []] for o in outers]
        for h in holes:
            hp = Polygon(h)
            best = None
            for item in polys:
                if item[0].contains(hp.representative_point()):
                    if best is None or item[0].area < best[0].area:
                        best = item
            if best is None:
                polys.append([hp, []])
            else:
                best[1].append(h)
        parts = [Polygon(p.exterior.coords, hs) for p, hs in polys]
        geom = make_valid(MultiPolygon(parts) if len(parts) > 1 else parts[0]) if parts else None
        return polygon_part(geom)
    if "paths" in g:
        paths = [[tuple(p[:2]) for p in path] for path in g["paths"] if len(path) >= 2]
        return MultiLineString(paths) if paths else None
    if "x" in g and "y" in g:
        return None
    return None


def polygon_part(geom):
    """Keep only the area part of a geometry (make_valid can add lines)."""
    if geom is None or geom.is_empty:
        return None
    if isinstance(geom, (Polygon, MultiPolygon)):
        return geom
    if isinstance(geom, GeometryCollection):
        polys = [g for g in geom.geoms if isinstance(g, (Polygon, MultiPolygon))]
        return unary_union(polys) if polys else None
    return None


def safe_union(geoms):
    geoms = [g for g in geoms if g is not None and not g.is_empty]
    if not geoms:
        return None
    try:
        return unary_union(geoms)
    except Exception:
        return unary_union([make_valid(g) for g in geoms])


def geo_acres(geom):
    """True (on-the-earth) area in acres of a lon/lat shape."""
    if geom is None or geom.is_empty:
        return 0.0
    total = 0.0
    polys = [geom] if isinstance(geom, Polygon) else [g for g in getattr(geom, "geoms", []) if isinstance(g, Polygon)]
    if isinstance(geom, GeometryCollection) and not isinstance(geom, MultiPolygon):
        polys = []
        for g in geom.geoms:
            if isinstance(g, Polygon):
                polys.append(g)
            elif isinstance(g, MultiPolygon):
                polys.extend(g.geoms)
    for p in polys:
        a, _ = GEOD.geometry_area_perimeter(orient(p, 1.0))
        total += abs(a)
    return total / SQM_PER_ACRE


def geo_length_km(geom):
    if geom is None or geom.is_empty:
        return 0.0
    return GEOD.geometry_length(geom) / 1000.0


def narrow_to_tract(geom, acres, count=None):
    """A Kentucky key row like 'Fort Heiman (Fort Donelson National Battlefield
    tract)' names one piece of a many-piece record. Keep the single piece whose
    size is within 15 % of the key's acres. -> (shape, True if narrowed)."""
    if geom is None or not isinstance(geom, MultiPolygon) or not acres or (count not in (None, 1)):
        return geom, False
    best = min(geom.geoms, key=lambda g: abs(geo_acres(g) - acres))
    if abs(geo_acres(best) - acres) <= 0.15 * acres:
        return best, True
    return geom, False


def vertex_count(geom):
    if geom is None or geom.is_empty:
        return 0
    if isinstance(geom, Polygon):
        return len(geom.exterior.coords) + sum(len(i.coords) for i in geom.interiors)
    if isinstance(geom, LineString):
        return len(geom.coords)
    return sum(vertex_count(g) for g in getattr(geom, "geoms", []))


def metres_between(lon1, lat1, lon2, lat2):
    return abs(GEOD.inv(lon1, lat1, lon2, lat2)[2])


def local_metric(geom):
    """Transformers to/from a local equal-distance projection around geom."""
    c = geom.centroid
    proj = f"+proj=aeqd +lat_0={c.y} +lon_0={c.x} +datum=WGS84 +units=m"
    fwd = Transformer.from_crs("EPSG:4326", proj, always_xy=True).transform
    back = Transformer.from_crs(proj, "EPSG:4326", always_xy=True).transform
    return fwd, back


def load_geojson_shape(path):
    """Saved outline (GeoJSON Feature / FeatureCollection / geometry)."""
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    if d.get("type") == "FeatureCollection":
        return safe_union([shape(ft["geometry"]) for ft in d["features"] if ft.get("geometry")])
    if d.get("type") == "Feature":
        return shape(d["geometry"]) if d.get("geometry") else None
    return shape(d)


def world_rings_to_shape(rings):
    """world-bounds 'r' = a list of rings. A ring inside another is a hole."""
    polys = [Polygon(r) for r in rings if len(r) >= 4]
    polys = [make_valid(p) if not p.is_valid else p for p in polys]
    polys.sort(key=lambda p: -p.area)
    shells = []
    for p in polys:
        for s in shells:
            if s[0].contains(p.representative_point()) and s[0].area > p.area:
                s[1].append(p)
                break
        else:
            shells.append([p, []])
    parts = [polygon_part(s.difference(safe_union(h))) if h else polygon_part(s) for s, h in shells]
    return polygon_part(safe_union(parts))


# ----------------------------- club files ----------------------------------
def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_json(path, data, indent=1):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, path)


def write_text(path, text):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def guard_output(out_dir, data_dir):
    """The tool writes reports only. Refuse an output folder that is one of
    the club's live folders (keys, outlines, 2-fers)."""
    out = os.path.realpath(out_dir)
    data = os.path.realpath(data_dir)
    for name in LIVE_FOLDERS:
        live = os.path.join(data, name)
        if out == live or out.startswith(live + os.sep):
            raise BadInput(f"the output folder {out_dir} is inside the club's live files ({name}); pick another folder")


def list_areas(data_dir, include_world=False):
    areas = []
    if os.path.exists(os.path.join(data_dir, "ky-answer-key.json")):
        areas.append("US-KY")
    for p in sorted(glob.glob(os.path.join(data_dir, "us-key", "US-*.json"))):
        a = os.path.basename(p)[:-5]
        if a not in areas:
            areas.append(a)
    for p in sorted(glob.glob(os.path.join(data_dir, "ca-key", "CA-*.json"))):
        areas.append(os.path.basename(p)[:-5])
    if include_world:
        for p in sorted(glob.glob(os.path.join(data_dir, "world-bounds", "*"))):
            if os.path.isdir(p):
                areas.append(os.path.basename(p))
    return areas


def parse_areas(arg, data_dir, include_world=False):
    known = list_areas(data_dir, include_world)
    if not arg or arg.strip().lower() == "all":
        return known
    want = [a.strip() for a in arg.split(",") if a.strip()]
    bad = [a for a in want if a not in known]
    if bad:
        raise BadInput(f"no club file for area(s) {', '.join(bad)}; known areas: {', '.join(known) or 'none'}")
    return want


US_ID = re.compile(r"^([A-Za-z_]+?)(\d+)$")
CA_ID = re.compile(r"^(.+?):(\d+)$")


def load_area_parks(data_dir, area, us_layers):
    """Return {ref: park} where park = {n, t, g, recs:[record dicts], extra}.
    A record dict: {layer, oid (int or None), name, acres, why, by_name, tract, prob}."""
    parks = {}
    if area == "US-KY" and os.path.exists(os.path.join(data_dir, "ky-answer-key.json")):
        key = read_json(os.path.join(data_dir, "ky-answer-key.json"))
        for ref, p in key.get("parks", {}).items():
            recs = []
            for t in p.get("tracts", []):
                code, nm = t[0], t[1]
                why = t[3] if len(t) > 3 else ""
                base = nm
                tract = False
                m = re.match(r"^(.*?)\s*\((.+?)\s+tract\)\s*$", nm)
                if m:
                    base, tract = m.group(2), True
                recs.append({"layer": code, "oid": None, "name": nm, "lookup": base,
                             "acres": t[2] if len(t) > 2 else None, "why": why,
                             "by_name": True, "tract": tract,
                             "count": t[4] if len(t) > 4 else None,
                             "proclamation": "proclamation" in str(why).lower()})
            parks[ref] = {"n": p.get("n", ""), "t": p.get("t", ""), "g": "official" if recs else "pin",
                          "recs": recs, "line": bool(p.get("line")), "trl": p.get("trl")}
        return parks
    if area.startswith("US-"):
        path = os.path.join(data_dir, "us-key", f"{area}.json")
    elif area.startswith("CA-"):
        path = os.path.join(data_dir, "ca-key", f"{area}.json")
    else:
        return load_world_parks(data_dir, area)
    if not os.path.exists(path):
        raise BadInput(f"missing key file {path}")
    key = read_json(path)
    for ref, p in key.get("parks", {}).items():
        recs = []
        for m in p.get("m", []):
            rid = m[0]
            rec = {"name": m[1] if len(m) > 1 else "", "acres": m[2] if len(m) > 2 else None,
                   "why": m[3] if len(m) > 3 else "", "by_name": False, "tract": False,
                   "proclamation": False}
            if isinstance(rid, int):
                rec.update(layer="PAD-US" if area.startswith("US-") else "cpcad", oid=rid)
            else:
                mm = (CA_ID if area.startswith("CA-") else US_ID).match(str(rid))
                if not mm:
                    rec.update(layer=str(rid), oid=None, prob="record id not understood")
                else:
                    rec.update(layer=mm.group(1), oid=int(mm.group(2)))
            recs.append(rec)
        parks[ref] = {"n": p.get("n", ""), "t": p.get("t", ""), "g": p.get("g", ""),
                      "recs": recs, "line": False}
    return parks


def load_world_parks(data_dir, country):
    parks = {}
    for path in sorted(glob.glob(os.path.join(data_dir, "world-bounds", country, "*.json"))):
        for ref, p in read_json(path).items():
            parks[ref] = {"n": p.get("n", ""), "t": "", "g": "official", "recs": [],
                          "world_rings": p.get("r"), "world_src": p.get("s", ""), "line": False}
    return parks


def saved_outline(data_dir, area, ref):
    """The club's saved simplified outline for a park, if any."""
    p = os.path.join(data_dir, "canada-bounds", f"{ref}.json")
    if os.path.exists(p):
        try:
            return polygon_part(make_valid(load_geojson_shape(p)))
        except Exception:
            return None
    return None


def load_fers(data_dir, area):
    p = os.path.join(data_dir, "fers", f"{area}.json")
    if not os.path.exists(p):
        return []
    return read_json(p).get("spots", [])


def fer_is_live(spot):
    st = str(spot.get("status", "")).lower()
    return not (st.startswith("dropped") or st.startswith("merged"))


# ----------------------------- layers --------------------------------------
PADUS = "https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0"
KYGIS = "https://kygisserver.ky.gov/arcgis/rest/services/WGS84WM_Services/"
FSEDW = "https://apps.fs.usda.gov/arcx/rest/services/EDW/"
LIO = "https://ws.lioservices.lrc.gov.on.ca/arcgis2/rest/services/LIO_OPEN_DATA/LIO_Open03/MapServer/"
KY_PARKS_AGENCY = "Kentucky Department of Parks (Tourism, Arts and Heritage Cabinet)"
KY_NP_AGENCY = "Office of Kentucky Nature Preserves (Energy and Environment Cabinet)"

# Layers the keys point to that are not in us-key/layers.json. Each one is an
# official agency layer. 'checked' says whether the name field was confirmed
# live while this tool was built. Override or add with --sources FILE.
BUILTIN_SOURCES = {
    "PAD-US": {"url": PADUS, "name_field": "Unit_Nm", "agency_field": "Mang_Name",
               "about": "USGS PAD-US 4 (fee managers)", "checked": True},
    "cpcad": {"url": "https://maps-cartes.ec.gc.ca/arcgis/rest/services/CWS_SCF/CPCAD/MapServer/0",
              "name_field": "NAME_E", "agency_field": "MGMT_E",
              "about": "CPCAD (Environment and Climate Change Canada)",
              "checked": False},
    "Ontario fede": {"url": LIO + "10", "name_field": "OFFICIAL_NAME",
                     "agency": "Government of Canada (federal protected area)",
                     "about": "Ontario federal protected areas (Land Information Ontario)", "checked": True},
    "Ontario Park": {"url": LIO + "4", "name_field": "PROTECTED_AREA_NAME_ENG", "agency_field": "MANAGEMENT_ENG",
                     "agency": "Ontario Parks", "about": "Ontario Parks, regulated (Land Information Ontario)",
                     "checked": True},
    "Ontario cons": {"url": LIO + "2", "name_field": "PROTECTED_AREA_NAME_ENG", "agency_field": "MANAGEMENT_ENG",
                     "agency": "Ontario Ministry of Natural Resources", "checked": True,
                     "about": "Ontario conservation reserves, regulated (Land Information Ontario)"},
    # Kentucky key layer codes (the KY key names records, it does not give ids)
    "bwma": {"url": KYGIS + "Ky_Public_Hunting_Areas_WGS84WM/MapServer/1", "name_field": "AREANAME",
             "agency_field": "MANAGER", "agency": "Kentucky Department of Fish and Wildlife Resources",
             "about": "KDFWR public hunting areas", "checked": True},
    "bstate": {"url": KYGIS + "Ky_State_Parks_Features_WGS84WM/MapServer/8", "name_field": "PUBLIC_NAM",
               "agency": KY_PARKS_AGENCY, "about": "Kentucky State Park boundaries", "checked": True},
    "bsnp": {"url": KYGIS + "Ky_KNP_State_Nature_Preserves_WGS84WM/MapServer/0", "name_field": "MANAME",
             "agency": KY_NP_AGENCY, "owner_field": "MA_OWNER",
             "about": "Kentucky state nature preserves (OKNP)", "checked": True},
    "bsna": {"url": KYGIS + "Ky_KNP_Natural_Areas_WGS84WM/MapServer/0", "name_field": "MANAME",
             "agency": KY_NP_AGENCY, "owner_field": "MA_OWNER",
             "about": "Kentucky state natural areas (OKNP)", "checked": True},
    "bwild": {"url": KYGIS + "Ky_KNP_Wild_River_Corridors_WGS84WM/MapServer/0", "name_field": "MANAME",
              "agency": KY_NP_AGENCY, "about": "Kentucky Wild River corridors (OKNP)", "checked": True},
    "bnps": {"url": "https://services1.arcgis.com/fBc8EJBxQRMcHlei/ArcGIS/rest/services/"
                    "NPS_Land_Resources_Division_Boundary_and_Tract_Data_Service/FeatureServer/2",
             "name_field": "UNIT_NAME", "agency": "National Park Service",
             "about": "NPS unit boundaries", "checked": True},
    "bfws": {"url": "https://services.arcgis.com/QVENGdaPbd4LUkLV/ArcGIS/rest/services/"
                    "FWSInterest_Simplified_Authoritative/FeatureServer/0",
             "name_field": "ORGNAME", "extra_where": "INTTYPE1='O'", "agency": "U.S. Fish and Wildlife Service",
             "about": "FWS owned land (interest, simplified)", "checked": True},
    "bpad": {"url": PADUS, "name_field": "Unit_Nm", "agency_field": "Mang_Name", "extra_where": "State_Nm='KY'",
             "about": "USGS PAD-US 4 (fee managers), Kentucky", "checked": True},
    "bwilder": {"url": FSEDW + "EDW_Wilderness_01/MapServer/0", "name_field": "wildernessname",
                "agency": "U.S. Forest Service", "about": "Forest Service wilderness", "checked": True},
    "bdbnf": {"url": FSEDW + "EDW_ForestSystemBoundaries_01/MapServer/1", "name_field": "forestname",
              "agency": "U.S. Forest Service", "about": "Forest Service proclamation boundaries", "checked": True},
    "bdbnfo": {"url": FSEDW + "EDW_BasicOwnership_02/MapServer/0", "name_field": "forestname",
               "extra_where": "ownerclassification='USDA FOREST SERVICE'", "agency": "U.S. Forest Service",
               "about": "Forest Service basic ownership (agency-owned land)", "checked": True},
    "trl": {"lines": True, "agency": "", "about": "official trail lines", "checked": True,
            "by_park_name": {
                "trail of tears national historic trail": [
                    "https://services1.arcgis.com/fBc8EJBxQRMcHlei/ArcGIS/rest/services/TRTE_NHT/FeatureServer/0",
                    "1=1", "TRNAME", "National Park Service"],
                "lewis and clark national historic trail": [
                    "https://services1.arcgis.com/fBc8EJBxQRMcHlei/ArcGIS/rest/services/"
                    "Lewis_and_Clark_National_Historic_Trail_Congressionally_Designated_Route/FeatureServer/0",
                    "1=1", "Exped_Seg", "National Park Service"],
                "sheltowee trace national recreation trail": [
                    FSEDW + "EDW_TrailNFSPublish_01/MapServer/0", "trail_name='SHELTOWEE TRACE'", "trail_name",
                    "U.S. Forest Service"]}},
}


def agency_from_description(desc):
    """'Tennessee Wildlife Resources Agency (wild, state GIS table)' -> agency."""
    d = re.sub(r"\(.*?\)", "", str(desc or "")).strip()
    d = re.split(r",\s*published by|\s+lands?,|;", d)[0].strip()
    return d


def load_sources(data_dir, extra_path=None):
    """Merge layers.json (the club's) + built-ins + an optional override file."""
    src = {}
    lp = os.path.join(data_dir, "us-key", "layers.json")
    if os.path.exists(lp):
        for k, v in read_json(lp).items():
            if isinstance(v, list) and len(v) >= 2:
                url = re.sub(r"/query/?$", "", v[0])
                src[k] = {"url": url, "name_field": v[1], "about": v[2] if len(v) > 2 else "",
                          "agency": agency_from_description(v[2] if len(v) > 2 else ""), "checked": False}
    for k, v in BUILTIN_SOURCES.items():
        src[k] = dict(v)
    for k, v in (src.items()):
        if k.startswith(("sgtnc", "sgtne", "sgtni")):
            v.setdefault("agency_field", "MANAGEMENT")
    if extra_path:
        if not os.path.exists(extra_path):
            raise BadInput(f"sources file {extra_path} not found")
        for k, v in read_json(extra_path).items():
            src[k] = {**src.get(k, {}), **v}
    return src


AGENCY_ALIASES = [
    (r"\bnps\b|national park service|park service", "National Park Service"),
    (r"\bfws\b|usfws|fish and wildlife service|fish & wildlife service", "U.S. Fish and Wildlife Service"),
    (r"\busfs\b|forest service|\bfs\b|usda forest", "U.S. Forest Service"),
    (r"\bblm\b|bureau of land management", "Bureau of Land Management"),
    (r"\busace\b|corps of engineers|\bcoe\b", "U.S. Army Corps of Engineers"),
    (r"\btva\b|tennessee valley authority", "Tennessee Valley Authority"),
    (r"\btwra\b|tennessee wildlife resources", "State fish and wildlife agency"),
    (r"^sfw$|kdfwr|kdfwer|kentucky department of fish", "State fish and wildlife agency"),
    (r"kentucky state parks|kentucky department of parks", KY_PARKS_AGENCY),
    (r"nature preserves|\boknp\b|\bknp\b", KY_NP_AGENCY),
    (r"parks canada", "Parks Canada"),
    (r"canadian wildlife service|environment and climate change canada|\beccc\b", "Environment and Climate Change Canada"),
    (r"ontario parks", "Ontario Parks"),
    (r"^sdc$|\btdec\b|tennessee department of environment|tennessee state parks", "State conservation department (TDEC; PAD-US 'SDC')"),
    (r"^spr$", "State parks agency (PAD-US 'SPR')"),
    (r"^sdf$", "State forestry agency (PAD-US 'SDF')"),
    (r"^usbr$|bureau of reclamation", "Bureau of Reclamation"),
    (r"division of forestry|tennessee department of agriculture", "Tennessee Division of Forestry"),
]


def canon_agency(raw):
    if raw is None:
        return None
    s = str(raw).strip()
    # PAD-US catch-all codes and the bare words 'Federal' / 'State' say too little to compare
    if not s or s.lower() in ("unk", "unknown", "none", "null", "other", "n/a", "oths", "othf", "unkl", "jnt",
                              "federal", "state", "private", "pvt"):
        return None
    low = s.lower()
    for pat, name in AGENCY_ALIASES:
        if re.search(pat, low):
            return name
    return s


def layer_meta_url(url):
    return re.sub(r"/query/?$", "", url)


def arcgis_query(web, url, params, max_age_s=None, clock=None):
    p = {"f": "json"}
    p.update(params)
    return web.get_json(layer_meta_url(url) + "/query", p, max_age_s=max_age_s)


def layer_oid_field(web, src, max_age_s=None):
    """The layer's record-number field (asked for by name: some servers leave it
    out of the answer otherwise)."""
    meta = web.get_json(layer_meta_url(src["url"]), {"f": "json"}, max_age_s=max_age_s)
    if meta.get("objectIdField"):
        return meta["objectIdField"]
    for f in meta.get("fields", []):
        if f.get("type") == "esriFieldTypeOID":
            return f.get("name")
    return "OBJECTID"


def fetch_by_ids(web, src, oids, simplify_m=None, max_age_s=None, clock=None, chunk=20):
    """Fetch records by OBJECTID. Returns {oid: {"geom", "attrs"}}; ids not in
    the answer are missing (RECORD GONE)."""
    out = {}
    oid_field = layer_oid_field(web, src, max_age_s)
    fields = ",".join(sorted(f for f in {oid_field, src.get("name_field"), src.get("agency_field"),
                                         src.get("owner_field")} if f))
    oids = sorted(set(int(o) for o in oids))
    for i in range(0, len(oids), chunk):
        if clock:
            clock.check()
        part = oids[i:i + chunk]
        params = {"objectIds": ",".join(map(str, part)), "outFields": fields or "*",
                  "returnGeometry": "true", "outSR": 4326, "geometryPrecision": 6}
        if simplify_m:
            params["maxAllowableOffset"] = round(simplify_m * DEG_PER_M, 8)
        data = arcgis_query(web, src["url"], params, max_age_s=max_age_s)
        oid_field = data.get("objectIdFieldName") or oid_field
        for ft in data.get("features", []):
            attrs = ft.get("attributes", {})
            oid = attrs.get(oid_field)
            if oid is None:
                for k, v in attrs.items():
                    if k.lower() == oid_field.lower() or k.lower() == "objectid":
                        oid = v
            if oid is None:
                continue
            out[int(oid)] = {"geom": esri_to_shape(ft.get("geometry")), "attrs": attrs}
    return out


def _sql(s):
    return str(s).replace("'", "''")


def resolve_by_name(web, src, lookup, max_age_s=None):
    """Find the record(s) a Kentucky key name points to. Returns
    (oids, how, live_name) or ([], why-not, None). Exact first, then the same
    name with type words removed, then a close spelling (all must be unique)."""
    nf = src["name_field"]
    extra = src.get("extra_where")
    where = f"UPPER({nf})=UPPER('{_sql(lookup)}')"
    if extra:
        where = f"({where}) AND {extra}"
    data = arcgis_query(web, src["url"], {"where": where, "returnIdsOnly": "true"}, max_age_s=max_age_s)
    ids = data.get("objectIds") or []
    if ids:
        return sorted(ids), "exact name", lookup
    d2 = arcgis_query(web, src["url"], {"where": extra or "1=1", "outFields": nf, "returnDistinctValues": "true",
                                       "returnGeometry": "false"}, max_age_s=max_age_s)
    names = sorted({str(f["attributes"].get(nf)) for f in d2.get("features", []) if f["attributes"].get(nf)})
    if not names:
        return [], "the layer gave no list of names", None
    want_light, want_core = light_name(lookup), core_name(lookup)
    pick = [n for n in names if light_name(n) == want_light]
    how = "same name, different spelling"
    if not pick and want_core:
        pick = [n for n in names if core_name(n) == want_core]
        how = "same name once type words are dropped"
    if not pick:
        try:
            from rapidfuzz import fuzz
            scored = sorted(((fuzz.ratio(want_light, light_name(n)), n) for n in names), reverse=True)
            if scored and scored[0][0] >= 92 and (len(scored) == 1 or scored[1][0] < scored[0][0] - 3):
                pick, how = [scored[0][1]], f"close spelling ({scored[0][0]:.0f}%)"
        except ImportError:
            pass
    if len(pick) != 1:
        return [], ("more than one record could be this name" if pick else "no record with this name on the layer"), None
    where = f"{nf}='{_sql(pick[0])}'" + (f" AND {extra}" if extra else "")
    data = arcgis_query(web, src["url"], {"where": where, "returnIdsOnly": "true"}, max_age_s=max_age_s)
    ids = data.get("objectIds") or []
    return (sorted(ids), how, pick[0]) if ids else ([], "the name was listed but no record came back", None)


def fetch_line_park(web, spec, max_age_s=None, simplify_m=None):
    """Official trail line for a 'trl' park: [url, where, name field, agency]."""
    url, where, nf, _agency = spec
    data = arcgis_query(web, url, {"where": where, "returnIdsOnly": "true"}, max_age_s=max_age_s)
    ids = sorted(data.get("objectIds") or [])
    src = {"url": url, "name_field": nf}
    recs = fetch_by_ids(web, src, ids, simplify_m=simplify_m, max_age_s=max_age_s, chunk=50) if ids else {}
    return ids, recs

# ---------------------------------------------------------------------------
# KPC 11 itself
# ---------------------------------------------------------------------------
TOOL = "11-boundary-watch"
SIMPLIFY_M = 3.0
GROW_PCT, GROW_ACRES = 2.0, 5.0        # GREW / SHRANK: more than 2 % or 5 acres
MOVE_M = 50.0                          # MOVED: box shifted more than 50 m
LINE_PCT, LINE_KM = 2.0, 0.5           # lines: more than 2 % or 0.5 km longer/shorter
KEEP_TOL_M = 10.0                      # old-inside-new tolerance
EDIT_FIELDS = ("last_edited_date", "EditDate", "ModifiedDate", "DATE_EDIT", "GEOMETRY_UPDATE_DATETIME",
               "SYSTEM_DATETIME", "LAST_EDITED_DATE", "Edit_Date")
CHANGE_VERDICTS = ("GREW", "SHRANK", "MOVED", "RECORD GONE", "RENAMED", "LAYER MOVED")
PROBLEM_VERDICTS = ("SOURCE DOWN", "CAN'T TELL")


def round_rel(x, rel=0.001):
    """Round to 0.1 % (keeps the state small and ignores dust)."""
    if not x:
        return 0.0
    step = 10 ** math.floor(math.log10(abs(x) * rel)) if abs(x) * rel > 0 else 1
    return round(round(x / step) * step, 6)


def fingerprint(geom):
    """Numbers only: rounded area (or length) + box to ~10 m + point count."""
    if geom is None or geom.is_empty:
        return None
    b = geom.bounds
    fp = {"bb": [round(b[0], 4), round(b[1], 4), round(b[2], 4), round(b[3], 4)], "v": vertex_count(geom)}
    if isinstance(geom, (LineString, MultiLineString)):
        fp["km"] = round_rel(geo_length_km(geom))
    else:
        fp["a"] = round_rel(geo_acres(geom))
    return fp


def box_shift_m(bb1, bb2):
    return max(metres_between(bb1[0], bb1[1], bb2[0], bb2[1]),
               metres_between(bb1[2], bb1[3], bb2[2], bb2[3]))


def compare_fp(old, new):
    """-> (verdict, why, numbers). verdict in SAME/GREW/SHRANK/MOVED."""
    if "km" in new or "km" in (old or {}):
        o, n = old.get("km", 0.0), new.get("km", 0.0)
        d = n - o
        pct = 100.0 * d / o if o else 100.0
        if abs(d) > LINE_KM or abs(pct) > LINE_PCT:
            v = "GREW" if d > 0 else "SHRANK"
            return v, f"The official line got {'longer' if d > 0 else 'shorter'}: {o:g} km to {n:g} km ({pct:+.1f}%).", {"old_km": o, "new_km": n}
        shift = box_shift_m(old["bb"], new["bb"])
        if shift > MOVE_M:
            return "MOVED", f"The official line is the same length but sits about {shift:.0f} m away from where it was.", {"shift_m": round(shift)}
        return "SAME", "The official line matches the last run.", {}
    o, n = old.get("a", 0.0), new.get("a", 0.0)
    d = n - o
    pct = 100.0 * d / o if o else 100.0
    if abs(d) > GROW_ACRES or abs(pct) > GROW_PCT:
        v = "GREW" if d > 0 else "SHRANK"
        return v, f"The agency's outline {'grew' if d > 0 else 'shrank'} from {o:,.1f} to {n:,.1f} acres ({pct:+.1f}%).", {"old_acres": o, "new_acres": n}
    shift = box_shift_m(old["bb"], new["bb"])
    if shift > MOVE_M:
        return "MOVED", f"The outline is about the same size but sits about {shift:.0f} m away from where it was.", {"old_acres": o, "new_acres": n, "shift_m": round(shift)}
    note = "" if (d == 0 and old.get("v") == new.get("v")) else " (tiny redraw under the limits)"
    return "SAME", "The agency's outline matches the last run" + note + ".", {}


def kept_share(old_geom, new_geom, tol_m=KEEP_TOL_M):
    """How much of the old outline is still inside the new one (10 m slack)."""
    if old_geom is None or new_geom is None or old_geom.is_empty or new_geom.is_empty:
        return None
    if not isinstance(old_geom, (Polygon, MultiPolygon)):
        return None
    fwd, _ = local_metric(old_geom)
    o = shp_transform(fwd, old_geom)
    n = shp_transform(fwd, new_geom).buffer(tol_m)
    if o.area <= 0:
        return None
    return round(100.0 * o.intersection(n).area / o.area, 1)


def find_layer_leads(web, url, name_field, max_leads=5):
    """The layer's address broke: look in the same server folder for a service
    with a similar name, and check it still has the name field."""
    m = re.match(r"^(https?://.+?/rest/services)/(.+?)/(MapServer|FeatureServer)(?:/(\d+))?", url, re.I)
    if not m:
        return []
    root, svc_path, kind, lyr = m.group(1), m.group(2), m.group(3), m.group(4) or "0"
    folder = svc_path.rsplit("/", 1)[0] if "/" in svc_path else ""
    old_name = svc_path.rsplit("/", 1)[-1]
    try:
        listing = web.get_json(root + ("/" + folder if folder else ""), {"f": "json"}, max_age_s=0)
    except SourceProblem:
        return []
    try:
        from rapidfuzz import fuzz
        sim = lambda a, b: fuzz.token_set_ratio(light_name(a), light_name(b))
    except ImportError:
        sim = lambda a, b: 100.0 if light_name(a) == light_name(b) else 0.0
    cands = []
    for s in listing.get("services", []):
        nm = s.get("name", "")
        short = nm.rsplit("/", 1)[-1]
        if s.get("type") not in ("MapServer", "FeatureServer") or nm == svc_path:
            continue
        score = sim(short.replace("_", " "), old_name.replace("_", " "))
        if score >= 70:
            cands.append((score, nm, s.get("type")))
    cands.sort(reverse=True)
    leads = []
    for score, nm, typ in cands[:max_leads]:
        lead_url = f"{root}/{nm}/{typ}/{lyr}"
        has_field = None
        try:
            meta = web.get_json(lead_url, {"f": "json"}, max_age_s=0)
            has_field = any(f.get("name", "").lower() == str(name_field).lower() for f in meta.get("fields", []))
        except SourceProblem:
            pass
        leads.append({"url": lead_url, "name_match_pct": round(score),
                      "has_name_field": has_field,
                      "why": f"Same server, service named '{nm.rsplit('/', 1)[-1]}'" +
                             (", and it still has the name field." if has_field else ".")})
    return leads


def layer_signature(web, src, max_age_s):
    """-> {'edit', 'edit_src', 'count'} from the layer's own page (cheap)."""
    meta = web.get_json(layer_meta_url(src["url"]), {"f": "json"}, max_age_s=max_age_s)
    if not isinstance(meta, dict) or ("fields" not in meta and "name" not in meta):
        raise SourceProblem("BAD ANSWER", "the layer page did not look like an ArcGIS layer")
    edit = (meta.get("editingInfo") or {}).get("lastEditDate")
    edit_src = "editingInfo.lastEditDate" if edit else None
    if not edit:
        names = {f.get("name", ""): f for f in meta.get("fields", [])}
        for fld in EDIT_FIELDS:
            hit = next((n for n in names if n.lower() == fld.lower()), None)
            if hit and names[hit].get("type") == "esriFieldTypeDate":
                try:
                    st = arcgis_query(web, src["url"], {"where": "1=1", "outStatistics": json.dumps(
                        [{"statisticType": "max", "onStatisticField": hit, "outStatisticFieldName": "mx"}])},
                        max_age_s=max_age_s)
                    feats = st.get("features") or []
                    if feats:
                        edit = list(feats[0]["attributes"].values())[0]
                        edit_src = f"newest {hit}"
                except SourceProblem:
                    pass
                break
    cnt = arcgis_query(web, src["url"], {"where": "1=1", "returnCountOnly": "true"}, max_age_s=max_age_s)
    return {"edit": edit, "edit_src": edit_src, "count": cnt.get("count"),
            "item": meta.get("serviceItemId"), "name": meta.get("name")}


class Watcher:
    def __init__(self, args, web=None):
        self.args = args
        self.data = args.data
        self.out = args.out
        self.state_path = args.state or os.path.join(self.out, "state.json")
        self.run_dir = os.path.join(self.out, ".run")
        self.outline_dir = os.path.join(self.out, "outlines")
        self.clock = Clock(args.max_minutes)
        self.sources = load_sources(self.data, args.sources)
        self.web = web or Polite(TOOL, args.cache, offline=args.offline, clock=self.clock)
        self.state = self._load_state()

    # -- state --
    def _load_state(self):
        if os.path.exists(self.state_path):
            try:
                st = read_json(self.state_path)
            except ValueError as e:
                raise BadInput(f"the state file {self.state_path} is not readable JSON ({e})")
        else:
            st = {}
        st.setdefault("about", "KPC 11 fingerprints: numbers only, no shapes. a = acres (0.1%), km = line length, "
                               "bb = box (about 10 m), v = point count.")
        for k in ("layers", "records", "parks", "resolved"):
            st.setdefault(k, {})
        st.setdefault("runs", [])
        return st

    def save_state(self):
        write_json(self.state_path, self.state, indent=None)

    def run_age_s(self):
        started = self.state.get("run", {}).get("t0", time.time())
        return max(60.0, time.time() - started + 60.0)

    # -- one run --
    def start(self, areas):
        run = self.state.get("run")
        if self.args.resume and run and not run.get("finished"):
            log(f"Carrying on with the run started {run['started']} ({len(run['areas_done'])}/{len(run['areas'])} areas done).")
            return run
        if run and not run.get("finished"):
            log("An unfinished run was found; starting a new one (use --resume to carry on).")
        if os.path.isdir(self.run_dir):
            for p in glob.glob(os.path.join(self.run_dir, "**", "*"), recursive=True):
                if os.path.isfile(p):
                    os.remove(p)
        run = {"started": now_iso(), "date": today(), "t0": time.time(), "areas": areas,
               "areas_done": [], "layer_sig": {}, "layer_decision": {}, "units_done": {}, "finished": False}
        self.state["run"] = run
        return run

    def _unit_path(self, area, lkey):
        safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", lkey)
        return os.path.join(self.run_dir, area, safe + ".json.gz")

    def _save_unit(self, area, lkey, unit):
        p = self._unit_path(area, lkey)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with gzip.open(p + ".tmp", "wt", encoding="utf-8") as f:
            json.dump(unit, f)
        os.replace(p + ".tmp", p)

    def _load_unit(self, area, lkey):
        p = self._unit_path(area, lkey)
        with gzip.open(p, "rt", encoding="utf-8") as f:
            return json.load(f)

    def layer_decision(self, lkey, src):
        """UNCHANGED / CHECK / problem, worked out once per layer per run."""
        run = self.state["run"]
        url = src["url"]
        if url in run["layer_decision"]:
            return run["layer_decision"][url]
        try:
            sig = layer_signature(self.web, src, self.run_age_s())
        except SourceProblem as e:
            dec = {"d": e.kind, "why": e.why}
            if e.kind == "LAYER MOVED":
                dec["leads"] = find_layer_leads(self.web, url, src.get("name_field", ""))
            run["layer_decision"][url] = dec
            return dec
        prev = self.state["layers"].get(url)
        run["layer_sig"][url] = sig
        if prev and sig["edit"] and prev.get("edit") == sig["edit"] and prev.get("count") == sig["count"]:
            dec = {"d": "UNCHANGED", "why": f"not edited since the last run ({sig['edit_src']}, {sig['count']} records)"}
        elif prev and not sig["edit"]:
            dec = {"d": "CHECK", "why": "the layer shows no last-edit date, so every record is checked"}
        else:
            dec = {"d": "CHECK", "why": "first look at this layer" if not prev else "the layer was edited since the last run"}
        run["layer_decision"][url] = dec
        return dec

    def process_area(self, area):
        run = self.state["run"]
        parks = load_area_parks(self.data, area, self.sources)
        by_layer = {}
        for ref, p in parks.items():
            for i, r in enumerate(p["recs"]):
                by_layer.setdefault(r["layer"], []).append((ref, i, r))
        done_units = set(run["units_done"].get(area, []))
        prev_parks = self.state["parks"].get(area, {})
        resolved = self.state["resolved"].setdefault(area, {})
        decisions = {}
        for lkey in sorted(by_layer):
            src = self.sources.get(lkey)
            if not src:
                decisions[lkey] = {"d": "CAN'T TELL", "why": f"no layer address for '{lkey}' in layers.json or the tool's list"}
                continue
            if src.get("lines"):
                decisions[lkey] = {"d": "CHECK", "why": "trail lines are always read"}
                continue
            self.clock.check()
            decisions[lkey] = self.layer_decision(lkey, src)

        # parks whose every layer is UNCHANGED and already fingerprinted: SAME, no download
        skip = set()
        for ref, p in parks.items():
            if not p["recs"] or ref not in prev_parks:
                continue
            if all(decisions.get(r["layer"], {}).get("d") == "UNCHANGED" for r in p["recs"]):
                skip.add(ref)
        for lkey in sorted(by_layer):
            if lkey in done_units:
                continue
            dec = decisions[lkey]
            todo = [(ref, i, r) for ref, i, r in by_layer[lkey] if ref not in skip]
            if dec["d"] in ("UNCHANGED", "CHECK") and todo:
                self.clock.check(need_s=60)
                unit = self.read_layer(area, lkey, self.sources[lkey], todo, resolved)
            else:
                unit = {"problem": None if dec["d"] in ("UNCHANGED", "CHECK") else dec, "recs": {}}
            self._save_unit(area, lkey, unit)
            run["units_done"].setdefault(area, []).append(lkey)
            self.save_state()

        results = self.judge_parks(area, parks, by_layer, decisions, skip, prev_parks)
        write_json(os.path.join(self.run_dir, area, "_result.json"), results)
        run["areas_done"].append(area)
        self.save_state()
        return results

    def read_layer(self, area, lkey, src, todo, resolved):
        """Download the records this area needs from one layer."""
        age = self.run_age_s()
        recs_out, problem = {}, None
        try:
            if src.get("lines"):
                for ref, i, r in todo:
                    spec = src.get("by_park_name", {}).get(light_name(r["name"]))
                    rk = f"{ref}#{i}"
                    if not spec:
                        recs_out[rk] = {"status": "CAN'T TELL", "why": f"no official line address for '{r['name']}'"}
                        continue
                    ids, got = fetch_line_park(self.web, spec, max_age_s=age, simplify_m=SIMPLIFY_M)
                    geom = safe_union([g["geom"] for g in got.values()])
                    recs_out[rk] = {"status": "OK" if geom is not None else "RECORD GONE", "url": spec[0],
                                    "oids": ids, "geom": mapping(geom) if geom is not None else None,
                                    "names": {}, "why": "" if geom is not None else "no line came back"}
                return {"problem": None, "recs": recs_out}
            need = {}
            for ref, i, r in todo:
                rk = f"{ref}#{i}"
                if r.get("by_name"):
                    nk = f"{lkey}|{r['lookup']}"
                    if nk not in resolved:
                        oids, how, live = resolve_by_name(self.web, src, r["lookup"], max_age_s=age)
                        if oids:
                            resolved[nk] = {"layer": lkey, "oids": oids, "how": how, "live_name": live, "on": today()}
                        else:
                            recs_out[rk] = {"status": "CAN'T TELL", "why": f"'{r['lookup']}': {how}"}
                            continue
                    oids = resolved[nk]["oids"]
                else:
                    if r.get("oid") is None:
                        recs_out[rk] = {"status": "CAN'T TELL", "why": r.get("prob", "no record id")}
                        continue
                    oids = [r["oid"]]
                recs_out[rk] = {"status": "OK", "oids": oids}
                for o in oids:
                    need[o] = True
            got = fetch_by_ids(self.web, src, list(need), simplify_m=SIMPLIFY_M, max_age_s=age, clock=self.clock) if need else {}
        except SourceProblem as e:
            problem = {"d": e.kind, "why": e.why}
            if e.kind == "LAYER MOVED":
                problem["leads"] = find_layer_leads(self.web, src["url"], src.get("name_field", ""))
            return {"problem": problem, "recs": {}}
        nf = src.get("name_field")
        url = src["url"]
        by_rk = {f"{ref}#{i}": r for ref, i, r in todo}
        old_recs = self.state["records"].setdefault(url, {})
        rec_fp = {}
        for o, item in got.items():
            nm = None
            if nf:
                for k, v in item["attrs"].items():
                    if k.lower() == nf.lower():
                        nm = v
            fp = fingerprint(item["geom"])
            if fp is not None:
                fp["n"] = nm
            rec_fp[str(o)] = {"fp": fp, "geom": mapping(item["geom"]) if item["geom"] is not None else None}
        for rk, info in recs_out.items():
            if info["status"] != "OK":
                continue
            gone = [o for o in info["oids"] if str(o) not in rec_fp]
            renamed = []
            for o in info["oids"]:
                prev = old_recs.get(str(o))
                cur = rec_fp.get(str(o), {}).get("fp")
                if prev and cur and prev.get("n") is not None and cur.get("n") is not None and prev["n"] != cur["n"]:
                    renamed.append([o, prev["n"], cur["n"]])
            if gone:
                info["gone_leads"] = self.gone_leads(src, by_rk[rk], age)
            info.update(url=url, gone=gone, renamed=renamed,
                        names={str(o): (rec_fp.get(str(o), {}).get("fp") or {}).get("n") for o in info["oids"]},
                        prev_names={str(o): (old_recs.get(str(o)) or {}).get("n") for o in info["oids"]})
        for o, d in rec_fp.items():           # remember record fingerprints
            if d["fp"] is not None:
                self.state["records"][url][o] = d["fp"]
        return {"problem": None, "recs": recs_out, "geoms": {o: d["geom"] for o, d in rec_fp.items()}}

    def gone_leads(self, src, r, age):
        """A record number the key names is gone: is a record with the same name
        on the layer under a new number? (Often the agency re-loaded the layer.)"""
        nm = r.get("lookup") or r.get("name")
        if not nm or not src.get("name_field"):
            return []
        try:
            oids, how, live = resolve_by_name(self.web, src, nm, max_age_s=age)
        except SourceProblem:
            return []
        return [{"new_record_ids": oids, "name_on_layer": live, "how": how}] if oids else []

    def judge_parks(self, area, parks, by_layer, decisions, skip, prev_parks):
        units = {lk: self._load_unit(area, lk) for lk in by_layer}
        fers = load_fers(self.data, area)
        new_parks = self.state["parks"].setdefault(area, {})
        out = []
        for ref in sorted(parks):
            p = parks[ref]
            row = {"ref": ref, "name": p["n"]}
            if not p["recs"]:
                continue                                     # pin only: nothing to watch
            if ref in skip:
                row.update(verdict="SAME", why="The agency's layer has not been edited since the last run, so the outline is the same.")
                out.append(row)
                continue
            problems, gone, renamed, geoms, used, cant = [], [], [], [], [], []
            for i, r in enumerate(p["recs"]):
                u = units[r["layer"]]
                if u.get("problem"):
                    problems.append((r["layer"], u["problem"]))
                    continue
                dec = decisions.get(r["layer"], {})
                if dec.get("d") not in ("UNCHANGED", "CHECK", None):
                    problems.append((r["layer"], dec))
                    continue
                info = u["recs"].get(f"{ref}#{i}")
                if info is None:
                    cant.append(f"{r['layer']}: not read")
                    continue
                if info["status"] == "CAN'T TELL":
                    cant.append(info["why"])
                    continue
                if info["status"] == "RECORD GONE":
                    gone.append(f"the line '{r['name']}'")
                    continue
                if r["layer"] == "trl" or self.sources.get(r["layer"], {}).get("lines"):
                    if info.get("geom"):
                        geoms.append(shape(info["geom"]))
                        used.append(f"trl:{r['name']}")
                    continue
                for o in info["oids"]:
                    if o in info.get("gone", []):
                        nm = info.get("prev_names", {}).get(str(o)) or r["name"]
                        txt = f"record {o} ('{nm}') on {r['layer']}"
                        for lead in info.get("gone_leads", []):
                            txt += (f" (a record named '{lead['name_on_layer']}' is on the layer as number "
                                    f"{', '.join(map(str, lead['new_record_ids']))}: probably renumbered)")
                            row.setdefault("leads", []).append({"layer": r["layer"], "old_record_id": o, **lead})
                        gone.append(txt)
                        continue
                    g = u.get("geoms", {}).get(str(o))
                    if g:
                        g = shape(g)
                        tag = f"{r['layer']}:{o}"
                        if r.get("tract"):
                            g, narrowed = narrow_to_tract(g, r.get("acres"), r.get("count"))
                            tag += " (tract piece)" if narrowed else ""
                        geoms.append(g)
                        used.append(tag)
                for o, a, b in info.get("renamed", []):
                    renamed.append(f"record {o} on {r['layer']} from '{a}' to '{b}'")
            new_geom = safe_union(geoms)
            new_fp = fingerprint(new_geom) if new_geom is not None else None
            prev = prev_parks.get(ref)
            verdicts, whys = [], []
            moved = [d for _, d in problems if d.get("d") == "LAYER MOVED"]
            nolayer = [d for _, d in problems if d.get("d") == "CAN'T TELL"]
            down = [d for _, d in problems if d.get("d") not in ("LAYER MOVED", "CAN'T TELL")]
            for d in nolayer:
                cant.append(d["why"])
            if moved:
                verdicts.append("LAYER MOVED")
                leads = [l for d in moved for l in d.get("leads", [])]
                row["leads"] = leads
                whys.append(f"The agency's layer address stopped working ({moved[0]['why']}); "
                            f"{len(leads)} possible new address(es) found on the same server.")
            if down and not moved:
                verdicts.append("SOURCE DOWN")
                whys.append(f"The agency's server did not give the outline ({down[0]['why']}); it will be tried again next run.")
            if gone:
                verdicts.append("RECORD GONE")
                whys.append("No longer on the agency's layer: " + "; ".join(gone) + ".")
            if renamed:
                verdicts.append("RENAMED")
                whys.append("The agency renamed " + "; ".join(renamed) + ".")
            if new_fp is None and not verdicts:
                verdicts.append("CAN'T TELL")
                whys.append("This park could not be checked: " + "; ".join(list(dict.fromkeys(cant)) or ["no outline came back"]) + ".")
            numbers = {}
            if new_fp is not None and not (moved or down):
                if prev is None:
                    verdicts.append("FIRST LOOK")
                    whys.append("First look at this park: its fingerprint was saved; changes are reported from the next run.")
                else:
                    v, why, numbers = compare_fp(prev, new_fp)
                    if v != "SAME" or not verdicts:
                        verdicts.append(v)
                        whys.append(why)
                    if prev.get("used") and sorted(prev["used"]) != sorted(used) and v != "SAME":
                        whys.append("Note: the set of records read is not the same as last run.")
                if cant:
                    whys.append("Some records could not be read: " + "; ".join(cant) + ".")
                rec = dict(new_fp)
                rec["used"] = used
                new_parks[ref] = rec
                if self.args.keep_outlines:
                    self.save_outline(area, ref, new_geom, prev_geom_needed=False)
            row["verdict"] = verdicts[0] if verdicts else "SAME"
            if len(verdicts) > 1:
                row["also"] = verdicts[1:]
            row["why"] = " ".join(whys) if whys else "The agency's outline matches the last run."
            if row["verdict"] in CHANGE_VERDICTS or set(row.get("also", [])) & set(CHANGE_VERDICTS):
                old_acres = (prev or {}).get("a")
                row["old_acres"] = old_acres
                row["new_acres"] = (new_fp or {}).get("a")
                if "km" in (new_fp or {}) or "km" in (prev or {}):
                    row["old_km"], row["new_km"] = (prev or {}).get("km"), (new_fp or {}).get("km")
                row.update({k: v for k, v in numbers.items() if k == "shift_m"})
                old_geom, old_from = self.old_outline(area, ref)
                if old_geom is not None and new_geom is not None:
                    row["old_still_inside_pct"] = kept_share(old_geom, new_geom)
                    row["old_outline_from"] = old_from
                row["fers"] = [{"id": s.get("id"), "kind": s.get("kind"), "live": fer_is_live(s)}
                               for s in fers if ref in (s.get("refs") or [])]
            out.append(row)
        # replace saved outlines only after the old ones were used
        for ref, g in getattr(self, "_pending_outlines", {}).get(area, {}).items():
            self._write_outline(area, ref, g)
        return out

    # -- outlines kept for the 'how much is still inside' figure --
    def save_outline(self, area, ref, geom, prev_geom_needed=False):
        self.__dict__.setdefault("_pending_outlines", {}).setdefault(area, {})[ref] = geom

    def _write_outline(self, area, ref, geom):
        p = os.path.join(self.outline_dir, area, f"{ref}.geojson.gz")
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with gzip.open(p, "wt", encoding="utf-8") as f:
            json.dump({"type": "Feature", "properties": {"ref": ref, "read": today(),
                       "note": "live outline as read by KPC 11 (simplified ~3 m on the server); a working copy, not a club outline"},
                       "geometry": mapping(geom)}, f)

    def old_outline(self, area, ref):
        g = saved_outline(self.data, area, ref)
        if g is not None:
            return g, "the club's saved outline"
        p = os.path.join(self.outline_dir, area, f"{ref}.geojson.gz")
        if os.path.exists(p):
            with gzip.open(p, "rt", encoding="utf-8") as f:
                return shape(json.load(f)["geometry"]), "last run's live outline"
        return None, None

    # -- wrap up --
    def finish(self):
        run = self.state["run"]
        date = run["date"]
        all_rows = {}
        for area in run["areas"]:
            p = os.path.join(self.run_dir, area, "_result.json")
            all_rows[area] = read_json(p) if os.path.exists(p) else []
        changed, problems, counts = [], [], {}
        for area, rows in all_rows.items():
            c = {}
            for r in rows:
                c[r["verdict"]] = c.get(r["verdict"], 0) + 1
                if r["verdict"] in CHANGE_VERDICTS or set(r.get("also", [])) & set(CHANGE_VERDICTS):
                    changed.append({"area": area, **r})
                elif r["verdict"] in PROBLEM_VERDICTS:
                    problems.append({"area": area, "ref": r["ref"], "name": r["name"], "verdict": r["verdict"], "why": r["why"]})
            counts[area] = c
        first = all(r["verdict"] in ("FIRST LOOK",) + PROBLEM_VERDICTS for rows in all_rows.values() for r in rows)
        for url, sig in run["layer_sig"].items():
            self.state["layers"][url] = {**sig, "checked": date}
        changes = {"tool": "KPC 11 Boundary Change Watcher", "date": date, "areas": run["areas"],
                   "note": ("First run: fingerprints were built; changes are reported from the next run."
                            if first else "Only parks whose agency outline changed. Nothing here edits a key, an outline or a 2-fer."),
                   "changed": changed, "could_not_check": problems,
                   "layers_moved": [{"url": u, **d} for u, d in run["layer_decision"].items() if d.get("d") == "LAYER MOVED"]}
        write_json(os.path.join(self.out, f"changes-{date}.json"), changes)
        write_text(os.path.join(self.out, "summary.md"), self.summary_md(date, counts, changed, problems, first, run))
        run["finished"] = True
        self.state["runs"] = (self.state["runs"] + [{"date": date, "started": run["started"], "areas": run["areas"],
                                                     "changed": len(changed), "could_not_check": len(problems)}])[-12:]
        self.state["run"] = {"finished": True, "date": date, "started": run["started"]}
        self.save_state()
        return changed, problems

    def summary_md(self, date, counts, changed, problems, first, run):
        order = ["SAME", "FIRST LOOK", "GREW", "SHRANK", "MOVED", "RECORD GONE", "RENAMED", "LAYER MOVED",
                 "SOURCE DOWN", "CAN'T TELL"]
        lines = [f"# KPC 11 boundary watch, {date}", ""]
        if first:
            lines += ["First run for these parks: fingerprints were built. Changes are reported from the next run.", ""]
        lines += ["| area | " + " | ".join(order) + " |", "|---|" + "---|" * len(order)]
        for area, c in counts.items():
            lines.append(f"| {area} | " + " | ".join(str(c.get(k, 0)) for k in order) + " |")
        lines += ["", f"## Changed parks ({len(changed)})", ""]
        if not changed:
            lines.append("None.")
        for r in changed:
            extra = ""
            if r.get("old_still_inside_pct") is not None:
                extra = f" {r['old_still_inside_pct']}% of the old outline is still inside the new one."
            frs = r.get("fers") or []
            live = [f["id"] for f in frs if f["live"]]
            if frs:
                extra += f" 2-fer rows using it: {len(frs)} ({len(live)} live)."
            lines.append(f"- **{r['area']} {r['ref']} {r['name']}**: {r['verdict']}. {r['why']}{extra}")
        lines += ["", f"## Could not check ({len(problems)}), tried again next run", ""]
        groups = {}
        for r in problems:
            groups.setdefault((r["verdict"], r["why"]), []).append(f"{r['ref']}")
        for (v, why), refs in sorted(groups.items(), key=lambda kv: -len(kv[1])):
            shown = ", ".join(refs[:8]) + (f" and {len(refs) - 8} more" if len(refs) > 8 else "")
            lines.append(f"- {v} ({len(refs)}): {why} Parks: {shown}.")
        unchanged = sum(1 for d in run["layer_decision"].values() if d.get("d") == "UNCHANGED")
        lines += ["", f"Layers: {len(run['layer_decision'])} looked at, {unchanged} not edited since the last run. "
                      f"Web requests this run: {self.web.requests_made}.", ""]
        return "\n".join(lines)


def build_parser():
    ap = argparse.ArgumentParser(description="KPC 11: weekly check of every park's outline against the agency's live layer.")
    ap.add_argument("--data", default=".", help="folder with the club files (us-key/, ca-key/, ky-answer-key.json, fers/, canada-bounds/)")
    ap.add_argument("--out", default="watch", help="report folder (default watch/)")
    ap.add_argument("--state", default=None, help="fingerprint file (default <out>/state.json)")
    ap.add_argument("--areas", default="all", help="comma list like US-KY,US-TN,CA-ON (default: every key found)")
    ap.add_argument("--resume", action="store_true", help="carry on with an unfinished run")
    ap.add_argument("--max-minutes", type=float, default=50, help="stop cleanly after this many minutes (exit 3)")
    ap.add_argument("--sources", default=None, help="extra layer list (JSON) to add or override layer addresses")
    ap.add_argument("--cache", default=".kpc-cache", help="folder for the dated cache of what was read")
    ap.add_argument("--offline", action="store_true", help="read only from the cache (for testing)")
    ap.add_argument("--no-outlines", dest="keep_outlines", action="store_false",
                    help="do not keep last run's live outlines (then 'still inside' uses saved club outlines only)")
    return ap


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        if not os.path.isdir(args.data):
            raise BadInput(f"club data folder {args.data} not found")
        if args.max_minutes is not None and args.max_minutes <= 0:
            raise BadInput("--max-minutes must be more than 0")
        guard_output(args.out, args.data)
        if args.state:
            guard_output(os.path.dirname(os.path.abspath(args.state)), args.data)
        areas = parse_areas(args.areas, args.data)
        if not areas:
            raise BadInput("no key files found in the data folder")
        w = Watcher(args)
        run = w.start(areas)
        w.save_state()
        for area in run["areas"]:
            if area in run["areas_done"]:
                continue
            log(f"{area}: checking ...")
            try:
                rows = w.process_area(area)
            except OutOfTime:
                raise
            except BadInput:
                raise
            except Exception as e:          # one failure never stops the batch
                log(f"{area}: CAN'T TELL ({type(e).__name__}: {e}); moving on")
                write_json(os.path.join(w.run_dir, area, "_result.json"), [])
                run["areas_done"].append(area)
                w.save_state()
                continue
            c = {}
            for r in rows:
                c[r["verdict"]] = c.get(r["verdict"], 0) + 1
            log(f"{area}: " + ", ".join(f"{k} {v}" for k, v in sorted(c.items())))
        changed, problems = w.finish()
        log(f"Done: {len(changed)} changed park(s), {len(problems)} could not be checked. See {args.out}/summary.md")
        return EXIT_DONE
    except BadInput as e:
        log(f"BAD INPUT: {e}")
        return EXIT_BAD_INPUT
    except OutOfTime:
        try:
            w.save_state()
        except Exception:
            pass
        log("Time is up: progress saved. Run again with --resume to carry on.")
        return EXIT_RUN_AGAIN


if __name__ == "__main__":
    sys.exit(main())
