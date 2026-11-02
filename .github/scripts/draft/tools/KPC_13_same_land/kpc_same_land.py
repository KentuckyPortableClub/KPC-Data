#!/usr/bin/env python3
"""KPC 13: "Same land, two park numbers" finder.

For every pair of POTA parks whose outlines overlap, runs five tests (same
record, nearly the same shape, same name family, pins together, same agency)
and lists the pairs that may be one piece of land under two park numbers, as
questions for the checker. A HELPER: it never relabels a 2-fer and never
edits a key, an outline or a 2-fer. Example:
    python kpc_same_land.py --data club-data --areas US-KY
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
# KPC 13 itself
# ---------------------------------------------------------------------------
from shapely.strtree import STRtree

TOOL = "13-same-land"
S2_SMALL, S2_LARGE, S2_INSIDE_LOW = 0.95, 0.80, 0.50
NAME_MIN = 85.0                 # token-set ratio, in percent
PIN_M = 200.0
MIN_OVERLAP_ACRES = 0.25        # smaller than this = touching / drawing noise ...
MIN_OVERLAP_SHARE = 0.01        # ... unless it is at least 1 % of the smaller park
RECORD_CACHE_DAYS = 7
POTA_CACHE_DAYS = 30
SAME, CHECK, NOT_SAME = "SAME LAND: likely", "CHECK", "NOT SAME"
RANK = {SAME: 0, CHECK: 1, NOT_SAME: 2}


# ----------------------------- the five tests -------------------------------
def test_s1(keys_a, keys_b):
    """Same record id(s) on the same layer."""
    a, b = set(keys_a or ()), set(keys_b or ())
    if not a or not b:
        return None, []
    if a == b:
        return "SAME RECORD", sorted(a)
    shared = sorted(a & b)
    return ("SHARES A RECORD", shared) if shared else (None, [])


def test_s2(overlap, area_a, area_b):
    """Overlap / smaller and overlap / larger -> shape class."""
    small, large = min(area_a, area_b), max(area_a, area_b)
    if small <= 0 or large <= 0:
        return "PART OVERLAP", 0.0, 0.0
    rs, rl = overlap / small, overlap / large
    rs, rl = min(rs, 1.0), min(rl, 1.0)
    if rs >= S2_SMALL and rl >= S2_LARGE:
        cls = "SAME SHAPE"
    elif rs >= S2_SMALL and rl >= S2_INSIDE_LOW:
        cls = "ONE INSIDE THE OTHER"
    elif rs >= S2_SMALL:
        cls = "SMALL ONE INSIDE"
    else:
        cls = "PART OVERLAP"
    return cls, round(rs, 3), round(rl, 3)


def test_s3(name_a, name_b):
    """Name family: normalised names, token-set ratio >= 85 or one inside the other."""
    from rapidfuzz import fuzz
    a, b = core_name(name_a), core_name(name_b)
    if not a or not b:
        return False, 0.0, a, b
    score = fuzz.token_set_ratio(a, b)
    contains = (f" {a} " in f" {b} ") or (f" {b} " in f" {a} ")
    return bool(score >= NAME_MIN or contains), round(score, 1), a, b


def test_s4(pin_a, pin_b):
    """Both POTA pins within 200 m. None when a pin is unknown."""
    if not pin_a or not pin_b:
        return None, None
    d = metres_between(pin_a[1], pin_a[0], pin_b[1], pin_b[0])
    return bool(d <= PIN_M), round(d)


def test_s5(ag_a, ag_b):
    a, b = set(x for x in ag_a or () if x), set(x for x in ag_b or () if x)
    if not a or not b:
        return "unknown"
    return "same" if a & b else "different"


def decide(s1, s2, s3, s4, s5, both_official=True):
    """The verdict and one plain sentence."""
    if s1 == "SAME RECORD":
        v, why = SAME, "Both park numbers point to the same agency record, so this looks like one piece of land with two park numbers."
    elif s2 == "SAME SHAPE" and (s3 or s4) and s5 == "same":
        what = "the names are the same family" if s3 else "the POTA pins are within 200 m"
        v, why = SAME, f"The outlines are almost the same shape, {what}, and the same agency runs both."
    elif s2 == "SAME SHAPE" and s5 == "different":
        v, why = CHECK, "The outlines are almost the same shape but different agencies run them, which is usually normal layering: a person should look."
    elif s2 == "SAME SHAPE" and s5 == "unknown":
        v, why = CHECK, "The outlines are almost the same shape but the managing agency could not be read for one of them: a person should look."
    elif s1 == "SHARES A RECORD":
        v, why = CHECK, "The two park numbers share an agency record but not all of their records: a person should look."
    elif s3 and s4 and s2 != "SAME SHAPE":
        how = "only partly overlap" if s2 == "PART OVERLAP" else "are not the same shape (one sits inside the other)"
        v, why = CHECK, f"The names are the same family and the POTA pins are within 200 m, though the outlines {how}: a person should look."
    elif s2 == "SAME SHAPE":
        v, why = NOT_SAME, "The outlines are almost the same shape and one agency runs both, but the names and pins differ, so the rules do not count it as same land."
    elif s2 == "ONE INSIDE THE OTHER":
        v, why = NOT_SAME, "One park sits inside the other and fills a big part of it: normal layering, listed apart."
    elif s2 == "SMALL ONE INSIDE":
        v, why = NOT_SAME, "The smaller park lies inside the bigger one: normal layering, not the same land."
    else:
        v, why = NOT_SAME, "The outlines only partly overlap and the names or pins do not match: not the same land."
    if v == SAME and not both_official:
        v, why = CHECK, why.rstrip(".") + ", but one outline is not graded official: a person should look."
    return v, why


# ----------------------------- outlines -------------------------------------
def record_agency(src, attrs):
    raw = None
    af = (src or {}).get("agency_field")
    if af and attrs:
        for k, v in attrs.items():
            if k.lower() == af.lower():
                raw = v
    return canon_agency(raw) or canon_agency((src or {}).get("agency"))


def world_agency(src_text):
    m = re.match(r"^([A-Z][A-Z0-9&-]{1,})\b", str(src_text or ""))
    return m.group(1) if m else (src_text or None)


class Finder:
    def __init__(self, args, web=None):
        self.args = args
        self.data, self.out = args.data, args.out
        self.clock = Clock(args.max_minutes)
        self.sources = load_sources(self.data, args.sources)
        self.web = web or Polite(TOOL, args.cache, offline=args.offline, clock=self.clock)
        self.progress_path = os.path.join(self.out, ".progress.json")

    # -- outlines for one area --
    def outlines(self, area, parks):
        res, left_out = {}, []
        age = RECORD_CACHE_DAYS * 86400
        if area[:3] not in ("US-", "CA-"):
            for ref, p in parks.items():
                g = world_rings_to_shape(p.get("world_rings") or [])
                if g is None or g.is_empty:
                    left_out.append([ref, "no outline in world-bounds"])
                    continue
                res[ref] = {"geom": g, "keys": [], "agencies": [world_agency(p.get("world_src"))],
                            "official": True, "from": "world-bounds (saved outline)", "notes": []}
            return res, left_out
        # what to read, per layer
        want = {}
        for ref, p in parks.items():
            if p.get("line") or all(r["layer"] == "trl" for r in p["recs"]):
                if p["recs"]:
                    left_out.append([ref, "a trail or river line, not an area"])
                continue
            if not p["recs"]:
                continue                                  # pin only: no outline
            recs = [r for r in p["recs"] if not r.get("proclamation")] or p["recs"]
            for r in recs:
                if r["layer"] == "trl":
                    continue
                want.setdefault(r["layer"], []).append((ref, r))
        got, fails, oids_of = {}, {}, {}
        for lkey in sorted(want):
            src = self.sources.get(lkey)
            if not src or not src.get("url"):
                for ref, r in want[lkey]:
                    fails.setdefault(ref, []).append(f"no layer address for '{lkey}'")
                continue
            try:
                ids = set()
                for ref, r in want[lkey]:
                    self.clock.check()
                    if r.get("by_name"):
                        oids, how, _live = resolve_by_name(self.web, src, r["lookup"], max_age_s=age)
                        if not oids:
                            fails.setdefault(ref, []).append(f"'{r['lookup']}' on {lkey}: {how}")
                            continue
                        oids_of[(ref, lkey, r["lookup"])] = oids
                        ids.update(oids)
                    elif r.get("oid") is not None:
                        ids.add(r["oid"])
                got[lkey] = fetch_by_ids(self.web, src, ids, simplify_m=None, max_age_s=age, clock=self.clock) if ids else {}
            except SourceProblem as e:
                for ref, r in want[lkey]:
                    fails.setdefault(ref, []).append(f"{lkey}: {e.kind.lower()} ({e.why})")
                got[lkey] = None
        for ref, p in parks.items():
            recs = [r for r in p["recs"] if not r.get("proclamation")] or p["recs"]
            recs = [r for r in recs if r["layer"] != "trl"]
            if not recs or p.get("line"):
                continue
            geoms, ags, keys, owners, tract_note = [], [], [], [], []
            for r in recs:
                src = self.sources.get(r["layer"], {})
                keys.append(f"{r['layer']}:{light_name(r['lookup'])}" if r.get("by_name") else f"{r['layer']}:{r.get('oid')}")
                layer_got = got.get(r["layer"])
                if not layer_got:
                    continue
                oids = oids_of.get((ref, r["layer"], r.get("lookup"))) if r.get("by_name") else [r.get("oid")]
                for o in oids or []:
                    item = layer_got.get(int(o)) if o is not None else None
                    if item is None:
                        if r.get("by_name") is False:
                            fails.setdefault(ref, []).append(f"record {o} not on {r['layer']} any more")
                        continue
                    if item["geom"] is not None:
                        g = item["geom"]
                        if r.get("tract"):
                            g, narrowed = narrow_to_tract(g, r.get("acres"), r.get("count"))
                            if narrowed:
                                tract_note.append(f"only the {r['name']} piece of the record is used")
                        geoms.append(g)
                    ags.append(record_agency(src, item["attrs"]))
                    of = src.get("owner_field")
                    if of:
                        owners += [v for k, v in item["attrs"].items() if k.lower() == of.lower() and v]
            geom = polygon_part(safe_union(geoms))
            frm, notes = "live agency layer (full detail)", []
            if fails.get(ref):
                notes = fails[ref]
                saved = saved_outline(self.data, area, ref)
                if saved is not None and (geom is None or len(notes) > 0):
                    geom, frm = saved, "the club's saved simplified outline (the live layer could not be read)"
                elif geom is not None:
                    frm = "live agency layer, but only part of the park's records could be read"
            if geom is None or geom.is_empty:
                left_out.append([ref, "; ".join(notes) or "no outline came back"])
                continue
            res[ref] = {"geom": geom, "keys": keys, "agencies": sorted({a for a in ags if a}),
                        "owners": sorted(set(map(str, owners))),
                        "official": str(p.get("g", "official")).lower() == "official",
                        "from": frm, "notes": notes, "tract": tract_note}
        return res, left_out

    # -- pins --
    def pins(self, area, refs):
        out = {}
        pi = os.path.join(self.data, "parkinfo", f"{area}.json")
        if os.path.exists(pi):
            for ref, row in read_json(pi).get("parks", {}).items():
                try:
                    out[ref] = (float(row[5]), float(row[6]))
                except (IndexError, TypeError, ValueError):
                    pass
        for ref in sorted(refs):
            if ref in out:
                continue
            try:
                self.clock.check()
                d = self.web.get_json(f"https://api.pota.app/park/{ref}", max_age_s=POTA_CACHE_DAYS * 86400)
                if d and d.get("latitude") is not None:
                    out[ref] = (float(d["latitude"]), float(d["longitude"]))
            except SourceProblem:
                pass
        return out

    # -- one area --
    def run_area(self, area):
        parks = load_area_parks(self.data, area, self.sources)
        outl, left_out = self.outlines(area, parks)
        refs = sorted(outl)
        geoms = [outl[r]["geom"] for r in refs]
        acres = {r: geo_acres(outl[r]["geom"]) for r in refs}
        tree = STRtree(geoms)
        pairs = []
        for i, ref in enumerate(refs):
            for j in tree.query(geoms[i], predicate="intersects"):
                j = int(j)
                if j <= i:
                    continue
                pairs.append((ref, refs[j]))
        fers = load_fers(self.data, area)
        pair_rows = []
        overl = {}
        for a, b in pairs:
            ga, gb = outl[a]["geom"], outl[b]["geom"]
            try:
                inter = polygon_part(ga.intersection(gb))
            except Exception:
                inter = polygon_part(make_valid(ga).intersection(make_valid(gb)))
            ov = geo_acres(inter)
            small = min(acres[a], acres[b])
            if ov < MIN_OVERLAP_ACRES and (small <= 0 or ov / small < MIN_OVERLAP_SHARE):
                continue
            overl[(a, b)] = ov
        pins = self.pins(area, {x for ab in overl for x in ab})
        for (a, b), ov in overl.items():
            pa, pb = parks[a], parks[b]
            s1, s1_keys = test_s1(outl[a]["keys"], outl[b]["keys"])
            s2, rs, rl = test_s2(ov, acres[a], acres[b])
            s3, s3_score, na, nb = test_s3(pa["n"], pb["n"])
            s4, s4_m = test_s4(pins.get(a), pins.get(b))
            s5 = test_s5(outl[a]["agencies"], outl[b]["agencies"])
            both_off = outl[a]["official"] and outl[b]["official"]
            v, why = decide(s1, s2, s3, bool(s4), s5, both_off)
            row = {"id": f"{a}+{b}", "refs": [a, b], "names": [pa["n"], pb["n"]],
                   "acres": [round(acres[a], 1), round(acres[b], 1)], "overlap_acres": round(ov, 1),
                   "verdict": v, "why": why,
                   "tests": {"S1": s1, "S1_records": s1_keys,
                             "S2": s2, "S2_of_smaller": rs, "S2_of_larger": rl,
                             "S3": s3, "S3_score": s3_score, "S3_names": [na, nb],
                             "S4": s4, "S4_m": s4_m,
                             "S5": s5, "S5_agencies": [outl[a]["agencies"], outl[b]["agencies"]]},
                   "fers": [{"id": s.get("id"), "kind": s.get("kind"), "live": fer_is_live(s)}
                            for s in fers if a in (s.get("refs") or []) and b in (s.get("refs") or [])]}
            owners = [outl[a].get("owners"), outl[b].get("owners")]
            if any(owners):
                row["tests"]["owner_field"] = owners
            tn = (outl[a].get("tract") or []) + (outl[b].get("tract") or [])
            if tn:
                row["tract_note"] = "; ".join(tn)
            frm = [outl[a]["from"], outl[b]["from"]]
            if any(not f.startswith("live agency layer (full") and not f.startswith("world-bounds") for f in frm):
                row["outline_from"] = frm
            if not both_off:
                row["grades"] = [pa.get("g"), pb.get("g")]
            pair_rows.append(row)
        pair_rows.sort(key=rank_key)
        result = {"tool": "KPC 13 same-land finder", "area": area, "built": today(),
                  "about": "Pairs of POTA parks whose outlines overlap, with the five same-land tests. "
                           "SAME LAND: likely and CHECK rows are questions for the checker; nothing here relabels a 2-fer.",
                  "counts": {"parks": len(parks), "outlines": len(outl), "pairs_overlapping": len(pair_rows),
                             SAME: sum(r["verdict"] == SAME for r in pair_rows),
                             CHECK: sum(r["verdict"] == CHECK for r in pair_rows),
                             NOT_SAME: sum(r["verdict"] == NOT_SAME for r in pair_rows),
                             "one_inside_the_other": sum(r["tests"]["S2"] == "ONE INSIDE THE OTHER" for r in pair_rows)},
                  "left_out": left_out,
                  "pairs": pair_rows}
        result["club_same_land_rows"] = self.compare_with_fers(fers, {r["id"]: r for r in pair_rows}, outl)
        write_json(os.path.join(self.out, f"{area}.json"), result)
        return result

    @staticmethod
    def compare_with_fers(fers, rows, outl):
        """How the tool's verdicts line up with rows the club already calls same land."""
        out = []
        for s in fers:
            if s.get("kind") != "same land":
                continue
            refs = sorted(s.get("refs") or [])
            if len(refs) < 2:
                continue
            pid = f"{refs[0]}+{refs[1]}"
            r = rows.get(pid)
            if r:
                tool = r["verdict"]
            elif refs[0] not in outl or refs[1] not in outl:
                tool = "NO OUTLINE (one park could not be drawn)"
            else:
                tool = "NOT FOUND OVERLAPPING"
            out.append({"fer_id": s.get("id"), "refs": refs, "live": fer_is_live(s), "tool_verdict": tool})
        return out

    # -- questions + summary --
    def write_questions(self, results):
        qp = os.path.join(self.out, "questions.json")
        old = {}
        if os.path.exists(qp):
            try:
                for q in read_json(qp).get("questions", []):
                    old[q["id"]] = q
            except (ValueError, KeyError):
                pass
        qs = []
        for area, res in results.items():
            for r in res["pairs"]:
                if r["verdict"] not in (SAME, CHECK):
                    continue
                q = {"id": r["id"], "area": area, "refs": r["refs"], "names": r["names"], "verdict": r["verdict"],
                     "why": r["why"], "tests": {k: r["tests"][k] for k in ("S1", "S2", "S3", "S4", "S5")},
                     "fers": r["fers"],
                     "question": "Are these two park numbers the same land (to be shown as 'same land, two park numbers', "
                                 "not as an ordinary 2-fer)? YES / NO / NOT SURE",
                     "answer": None, "asked": today()}
                prev = old.get(r["id"])
                if prev and prev.get("answer") is not None:   # never lose a checker's answer
                    q.update({k: prev[k] for k in prev if k in ("answer", "checked_by", "how", "asked", "note")})
                qs.append(q)
        for qid, prev in old.items():                         # keep answered rows from areas not run now
            if prev.get("answer") is not None and not any(q["id"] == qid for q in qs):
                qs.append(prev)
        write_json(qp, {"about": "KPC 13 same-land questions for the checker (chat 11). answer = YES / NO / NOT SURE. "
                                 "Nothing is relabelled until a person answers.",
                        "built": today(), "open": sum(q["answer"] is None for q in qs), "questions": qs})
        return qs

    def write_summary(self, results):
        lines = [f"# KPC 13 same land, two park numbers: {today()}", "",
                 "| area | parks with outline | overlapping pairs | SAME LAND: likely | CHECK | NOT SAME | one inside the other |",
                 "|---|---|---|---|---|---|---|"]
        for area, res in results.items():
            c = res["counts"]
            lines.append(f"| {area} | {c['outlines']} | {c['pairs_overlapping']} | {c[SAME]} | {c[CHECK]} | {c[NOT_SAME]} | {c['one_inside_the_other']} |")
        for area, res in results.items():
            top = [r for r in res["pairs"] if r["verdict"] in (SAME, CHECK)][:10]
            lines += ["", f"## {area}: top candidates", ""]
            if not top:
                lines.append("None.")
            for r in top:
                kinds = {}
                for f in r["fers"]:
                    kinds[f["kind"]] = kinds.get(f["kind"], 0) + 1
                fr = (" (2-fer rows: " + ", ".join(k if n == 1 else f"{k} x{n}" for k, n in kinds.items()) + ")") if kinds else ""
                lines.append(f"- **{r['verdict']}** {r['refs'][0]} {r['names'][0]} / {r['refs'][1]} {r['names'][1]}: {r['why']}{fr}")
            club = res.get("club_same_land_rows") or []
            if not club:
                lines += ["", "Rows the club's 2-fer file already calls same land: none in this area."]
            else:
                ok = sum(1 for c in club if c["tool_verdict"] in (SAME, CHECK))
                lines += ["", f"Rows the club's 2-fer file already calls same land: {len(club)}; this tool says SAME LAND or CHECK for {ok}."]
                for c in club:
                    if c["tool_verdict"] not in (SAME, CHECK):
                        lines.append(f"- {c['fer_id']}: tool says {c['tool_verdict']}")
            if res.get("left_out"):
                lines += ["", f"Parks left out (no area outline): {len(res['left_out'])} (see {area}.json, left_out)."]
        lines.append("")
        write_text(os.path.join(self.out, "summary.md"), "\n".join(lines))


def rank_key(r):
    t = r["tests"]
    return (RANK[r["verdict"]], 0 if t["S1"] == "SAME RECORD" else 1,
            -min(t["S2_of_smaller"], t["S2_of_larger"]), -(t["S3_score"] or 0),
            t["S4_m"] if t["S4_m"] is not None else 10 ** 9)


def build_parser():
    ap = argparse.ArgumentParser(description="KPC 13: find park pairs that may be the same land under two park numbers.")
    ap.add_argument("--data", default=".", help="folder with the club files (us-key/, ca-key/, ky-answer-key.json, world-bounds/, fers/)")
    ap.add_argument("--out", default="sameland", help="report folder (default sameland/)")
    ap.add_argument("--areas", default="all", help="comma list like US-KY,US-TN,CA-ON,CH (default: every key and world-bounds country)")
    ap.add_argument("--resume", action="store_true", help="carry on with an unfinished run")
    ap.add_argument("--max-minutes", type=float, default=50, help="stop cleanly after this many minutes (exit 3)")
    ap.add_argument("--sources", default=None, help="extra layer list (JSON) to add or override layer addresses")
    ap.add_argument("--cache", default=".kpc-cache", help="folder for the dated cache of what was read")
    ap.add_argument("--offline", action="store_true", help="read only from the cache (for testing)")
    return ap


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        if not os.path.isdir(args.data):
            raise BadInput(f"club data folder {args.data} not found")
        if args.max_minutes is not None and args.max_minutes <= 0:
            raise BadInput("--max-minutes must be more than 0")
        guard_output(args.out, args.data)
        areas = parse_areas(args.areas, args.data, include_world=True)
        if not areas:
            raise BadInput("no key or world-bounds files found in the data folder")
        f = Finder(args)
        prog = read_json(f.progress_path) if (args.resume and os.path.exists(f.progress_path)) else None
        if not prog or prog.get("finished"):
            prog = {"started": now_iso(), "areas": areas, "done": [], "finished": False}
        else:
            log(f"Carrying on with the run started {prog['started']} ({len(prog['done'])}/{len(prog['areas'])} areas done).")
        write_json(f.progress_path, prog)
        for area in prog["areas"]:
            if area in prog["done"]:
                continue
            log(f"{area}: looking for same land ...")
            try:
                res = f.run_area(area)
                c = res["counts"]
                log(f"{area}: {c['pairs_overlapping']} overlapping pairs, {c[SAME]} same land likely, {c[CHECK]} to check")
            except OutOfTime:
                raise
            except Exception as e:           # one failure never stops the batch
                log(f"{area}: CAN'T TELL ({type(e).__name__}: {e}); moving on")
            prog["done"].append(area)
            write_json(f.progress_path, prog)
        results = {}
        for area in prog["areas"]:
            p = os.path.join(args.out, f"{area}.json")
            if os.path.exists(p):
                results[area] = read_json(p)
        f.write_questions(results)
        f.write_summary(results)
        prog["finished"] = True
        write_json(f.progress_path, prog)
        log(f"Done. See {args.out}/summary.md and {args.out}/questions.json")
        return EXIT_DONE
    except BadInput as e:
        log(f"BAD INPUT: {e}")
        return EXIT_BAD_INPUT
    except OutOfTime:
        log("Time is up: progress saved. Run again with --resume to carry on.")
        return EXIT_RUN_AGAIN


if __name__ == "__main__":
    sys.exit(main())
