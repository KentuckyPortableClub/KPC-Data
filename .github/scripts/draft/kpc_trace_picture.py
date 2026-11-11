#!/usr/bin/env python3
"""
KPC Picture-Map Tracer
======================

Turns a managing agency's official PICTURE map of a park (a JPEG rendered from
its brochure / PDF; no coordinates) into an APPROXIMATE outline (or trail line)
on the real map, for parks that have no official GIS boundary.

Club Rule G R-G9 hard rules (enforced in code, do not change):
  1. Only the managing agency's OWN official map of THAT park
     (index.json must name the agency and the source URL + page; the tool
     cannot judge officialness, the person adding the row is responsible).
  2. The picture is georeferenced to >= 3 control points that also exist on a
     public government basemap.
  3. RMS fit error of the control points must be < 50 m, else NO outline.
  4. Output is always grade "approximate (picture map)" with fit_m and the
     source URL + page. Never "official". Never used for 2-fers.
  R-G9U (club rule): UNOFFICIAL maps only as a last resort (no official GIS layer, agency
     parcel or agency map). Named publisher (source_org) + notes required; app/crowd maps
     (OSM, Google, AllTrails, Gaia, Strava, iOverlander, Wikipedia ...) are banned. Same gates.
     Saved separately (traced_unofficial/), status "UNOFFICIAL MAP", grade "Approximate, from
     an unofficial map", never for 2-fers; an official row always wins and withdraws it.
  5. The park reference is the key (a later official GIS outline replaces it,
     handled elsewhere).
  6. Basemap = public government sources only: US Census TIGER roads,
     BLM CadNSDI PLSS, USGS NHD; Canada NRN (Statistics Canada / NRCan).
     NEVER OpenStreetMap or Google (hosts are allow-listed below).

Inputs  (relative to --base, default "."):
  maps/<ref>_<short-name>.jpg   picture page that shows the boundary (<= 2000 px)
  index.json                    [{ref, name, agency, source_url, page, ...}]
  pins.json                     {ref: [lat, lon]}   (POTA pin)
Outputs:
  traced/<ref>.json             GeoJSON FeatureCollection (only when DRAWN)
  traced/report.csv             ref,status,fit_m,n_points,why,...
  traced/debug/<ref>_*.png      debug images
  cache/<ref>_basemap.json      cached government basemap features

Usage:
  python kpc_trace_picture.py --refs US-10172 US-2685
  python kpc_trace_picture.py --all --resume --time-budget-min 50
"""

from __future__ import annotations

import argparse
import csv
import datetime as _dt
import glob
import json
import math
import os
import random
import re
import sys
import time
import traceback
from pathlib import Path
from urllib.parse import urljoin, urlparse

import cv2
import numpy as np
import requests
from pyproj import Transformer
from shapely.geometry import LineString, Point, Polygon, mapping
import shapely
from shapely.validation import make_valid
from shapely.ops import unary_union
from sklearn.cluster import DBSCAN, KMeans
from sklearn.neighbors import KDTree
try:   # Nov 2 review: tracer limits (switches + defaults in kpc_trace_limits.py); missing file = today's behaviour
    sys.path.insert(0, str(Path(__file__).resolve().parent)); import kpc_trace_limits as TL
except Exception:  # noqa: BLE001
    TL = None
HONOR_IMAGE = TL is not None and TL.on("KPC_TRACE_HONOR_IMAGE")
try:
    import kpc_trace_marks as TM   # Nov 11 (later): band-road junctions, box masks, dark boundary rings (numpy + OpenCV only)
except ImportError:  # noqa
    TM = None
try:
    import kpc_trace_edges as LE   # Nov 11: line agreement (numpy + OpenCV only)
except ImportError:  # noqa
    LE = None
CHANCE_RATIO = TL.num("KPC_TRACE_CHANCE_RATIO") if TL else 1.5
CHANCE_MARGIN = TL.num("KPC_TRACE_CHANCE_MARGIN") if TL else 2.0
# Nov 11: the match score = junction score + LINE_WEIGHT x line-agreement z (kpc_trace_edges.py), measured the same way on the real
# basemap and on each rotated decoy; the better-than-chance gate above is unchanged. 0 = the junction score alone (the Nov 2 behaviour).
LINE_WEIGHT = (TL.num("KPC_TRACE_LINE_WEIGHT") if TL else 0.25) if LE is not None else 0.0
# Nov 11 (later): matcher input improvements, each ON by default, each switched off alone with --off <name> or its env variable = 0
# (kpc_trace_limits.DEFAULTS), so a before / after run can measure each one. None is a gate; the gates below are unchanged.
SWITCHES = {"band_junctions": "KPC_TRACE_BAND_JUNCTIONS",   # junctions of roads drawn as bands (campground maps)
            "box_mask": "KPC_TRACE_BOX_MASK",               # no junctions in legend / title / inset / icon boxes away from the park
            "dark_ring": "KPC_TRACE_DARK_RING"}             # a thick black boundary RING, tried only when no colour gave a boundary
BAND_JUNCTIONS = TM is not None and (TL.on("KPC_TRACE_BAND_JUNCTIONS") if TL else True)
BOX_MASK = TM is not None and (TL.on("KPC_TRACE_BOX_MASK") if TL else True)
DARK_RING = TM is not None and (TL.on("KPC_TRACE_DARK_RING") if TL else True)
RING_ONLY = "thick dark line"
LINE_MIN_Z = 2.0          # Nov 11 (a NEW gate, stricter only): when the picture box holds line evidence, a fit whose basemap lines do not sit on the picture's lines is refused

__version__ = "0.3.0"   # Nov 11: line agreement + TIGERweb water (a cached basemap of 0.2.0 is re-read once)

# ---------------------------------------------------------------- hard rules
BANNED_ORG_WORDS = ("openstreetmap", "google", "alltrails", "gaiagps", "strava", "ioverlander",
                    "wikipedia", "wikiloc", "komoot", "outdooractive", "trailforks", "caltopo", "onxmaps")
GRADE = "approximate (picture map)"
# Club rule R-G9U: unofficial maps are a LAST RESORT, saved separately and clearly marked.
GRADE_UNOFFICIAL = "Approximate, from an unofficial map"
STATUS_UNOFFICIAL = "UNOFFICIAL MAP"      # status of a drawn unofficial outline
# R-G9U "never use" list (app / crowd-sourced maps) - applies to every source_url, official or not.
BANNED_MAP_SOURCE_WORDS = ("openstreetmap", "osm.org", "google", "goo.gl", "alltrails", "gaiagps",
                           "strava", "ioverlander", "wikipedia", "wikimedia", "wikiloc",
                           "komoot", "outdooractive", "trailforks", "mtbproject", "hikingproject",
                           "onxmaps", "caltopo", "mapcarta", "bing.com", "apple.com/maps", "waze")
MAX_FIT_M = 50.0          # Rule 3: draw only if RMS < 50 m (strict "<")
MIN_POINTS = 3            # Rule 2: at least 3 control points
SIMPLIFY_M = 3.0          # Step 4: Douglas-Peucker tolerance in metres
PIN_MAX_OUTSIDE_M = 1000  # Step 5: pin inside or within 1 km
PIN_NEAR_M = 200.0        # Nov 7 (pin mode): a shape this close to the pin on the page is a candidate for the park's own shape
PIN_MIN_SHAPE_PX = 150.0  # Nov 7 (pin mode): the smallest shape at the pin still worth considering, in pixels (speckle floor)
PIN_PICK = os.environ.get("KPC_TRACE_PIN_PICK", "1") != "0"   # Nov 7: choose the boundary colour by the pin on a GeoPDF page (0 = old behaviour)
AREA_RATIO_RANGE = (0.2, 5.0)  # Step 5 / Nov 6: vs known acreage -> NEEDS A PERSON (no outline)

# Rule 6: only these basemap hosts may ever be queried. Nov 11: the host list and the source addresses live in kpc_trace_hosts.py (standard
# library only), so `--list-hosts` can print every host a run would contact without importing the map libraries or making a request.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from kpc_trace_hosts import (ALLOWED_BASEMAP_HOSTS, FORBIDDEN_HOST_WORDS, TIGER, TIGER_HYDRO, NHD, PLSS, NRN)  # noqa: E402
import kpc_trace_hosts as TH  # noqa: E402
TIGER_HYDRO_LAYERS = (("water", "linear hydrography"), ("shore", "areal hydrography"))   # the service's own names (layers 0 and 1 today), found by name; a "... Labels" layer is never read
NRN_PROVINCES = ["AB", "BC", "MB", "NB", "NL", "NS", "NT", "NU", "ON", "PE", "QC", "SK", "YT"]
NRN_ROAD_GROUP_BASES = {"trans-canada": 34, "national-highway": 48, "major": 62, "local": 76}

DEFAULT_UA = ("KPC-Picture-Map-Tracer/%s (Kentucky POTA club park-boundary project; "
              "polite batch use; set KPC_TRACER_UA to add a contact)" % __version__)

REPORT_FIELDS = ["ref", "status", "fit_m", "n_points", "why",
                 "fit_loo_m", "model", "n_search", "decoy_best", "search_tol_m", "flags", "source_url", "page", "date",
                 "source_type", "source_org", "notes",
                 "acres_traced", "acres_known", "ceiling_acres", "edge_share", "pin_dist_m",   # Nov 7: every gate's input in the report
                 "geo_m_per_px", "geo_page_km2", "geo_lat_down", "pin_px",
                 "line_share", "line_z", "decoy_line_z", "score_points"]   # Nov 11: the line-agreement inputs of the chance gate


def log(msg: str) -> None:
    print(time.strftime("%H:%M:%S"), msg, flush=True)


# ===================================================================== HTTP
def _robots_rules(text: str, token: str) -> list:
    """Allow/Disallow rules of our group (token) or '*' from a robots.txt (RFC 9309 grouping)."""
    groups, cur, last_ua = [], None, False
    for raw in (text or "").splitlines():
        line = raw.split("#", 1)[0].strip()
        if ":" not in line:
            continue
        k, v = (x.strip() for x in line.split(":", 1))
        k = k.lower()
        if k == "user-agent":
            if not last_ua:
                cur = {"agents": [], "rules": []}
                groups.append(cur)
            cur["agents"].append(v.lower())
            last_ua = True
            continue
        last_ua = False
        if cur is not None and k in ("allow", "disallow"):
            cur["rules"].append((k == "allow", v))
    mine = [g for g in groups if any(a != "*" and token.startswith(a) for a in g["agents"])]
    return [r for g in (mine or [g for g in groups if "*" in g["agents"]]) for r in g["rules"]]


def _robots_allowed(rules: list, url: str) -> bool:
    """Longest match wins, Allow wins ties, no match = allowed."""
    p = urlparse(url)
    path = (p.path or "/") + (("?" + p.query) if p.query else "")
    best, ok = -1, True
    for allow, pat in rules:
        if not pat:
            continue
        rx = re.escape(pat).replace(r"\*", ".*")
        if rx.endswith(r"\$"):
            rx = rx[:-2] + "$"
        if re.match(rx, path) and (len(pat) > best or (len(pat) == best and allow)):
            best, ok = len(pat), allow
    return ok


class PoliteHttp:
    """One request at a time, minimum interval, retries with exponential back-off.
    Nov 7 standing rule: robots.txt is read once per host and obeyed on every path (ArcGIS REST included);
    a robots 401/403, 5xx, 429 or no answer is a STOP for that host (nothing is read); 404/410 = no robots file.
    Redirects are never followed (all allowed basemap hosts answer directly)."""
    STOP = [(False, "/")]

    def __init__(self, user_agent: str, min_interval: float = 1.0, retries: int = 5,
                 timeout: float = 90.0):
        self.s = requests.Session()
        self.s.headers.update({"User-Agent": user_agent, "Accept": "application/json"})
        if os.environ.get("KPC_NO_NET") == "1":      # Nov 7: the test gate sets this; a real request raises (mocked tests replace s.get)
            def _no_net(*a, **k):
                raise RuntimeError("network disabled (KPC_NO_NET=1)")
            self.s.get = _no_net
        self.token = (user_agent.split("/", 1)[0].strip() or "*").lower()
        self.min_interval = min_interval
        self.retries = retries
        self.timeout = timeout
        self._last = 0.0
        self.n_requests = 0
        self.robots = {}            # host -> rules
        self.robots_stop = {}       # host -> why

    def _robots(self, url: str) -> list:
        p = urlparse(url)
        host = (p.hostname or "").lower()
        if host in self.robots:
            return self.robots[host]
        rurl, st, text = f"{p.scheme or 'https'}://{p.netloc}/robots.txt", None, ""
        for _hop in range(4):                 # Nov 7 review: follow a robots.txt redirect (www. / https hops) but only within the allowed hosts
            wait = self.min_interval - (time.time() - self._last)
            if wait > 0:
                time.sleep(wait)
            self._last = time.time()
            self.n_requests += 1
            try:
                r = self.s.get(rurl, timeout=self.timeout, allow_redirects=False, headers={"Accept": "text/plain, */*"})
                st, text = r.status_code, r.text
            except requests.RequestException as e:
                st, text = f"err:{type(e).__name__}", ""
                break
            if isinstance(st, int) and 300 <= st < 400 and r.headers.get("Location"):
                nxt = urljoin(rurl, r.headers["Location"])
                nh = (urlparse(nxt).hostname or "").lower()
                if nh not in ALLOWED_BASEMAP_HOSTS or any(wd in nh for wd in FORBIDDEN_HOST_WORDS):
                    st = f"redirect to {nh}"      # a robots.txt that leads off the allowed list = STOP
                    break
                rurl = nxt
                continue
            break
        if st == 200:
            rules = _robots_rules(text, self.token) if "<html" not in text[:500].lower() else []
        elif isinstance(st, int) and 400 <= st < 500 and st not in (401, 403, 429):
            rules = []                                    # no robots file
        else:
            rules = self.STOP                             # 401/403/5xx/429/redirect/no answer = STOP (fail closed)
            self.robots_stop[host] = f"robots.txt answered {st}"
            log(f"   {host}/robots.txt answered {st}: treated as Disallow: / (STOP); nothing is read from this host")
        self.robots[host] = rules
        return rules

    @staticmethod
    def check_host(url: str) -> None:
        host = (urlparse(url).hostname or "").lower()
        if any(w in host for w in FORBIDDEN_HOST_WORDS) or host not in ALLOWED_BASEMAP_HOSTS:
            raise RuntimeError(f"basemap host not allowed by club rule 6: {host}")

    def get_json(self, url: str, params: dict) -> dict:
        self.check_host(url)
        if not _robots_allowed(self._robots(url), url):
            host = (urlparse(url).hostname or "").lower()
            raise RuntimeError(f"robots: {host} robots.txt does not allow {urlparse(url).path} "
                               f"({self.robots_stop.get(host, 'Disallow')}); not read, no other path tried")
        err = None
        for attempt in range(self.retries + 1):
            wait = self.min_interval - (time.time() - self._last)
            if wait > 0:
                time.sleep(wait)
            self._last = time.time()
            self.n_requests += 1
            try:
                r = self.s.get(url, params=params, timeout=self.timeout, allow_redirects=False)
                if 300 <= r.status_code < 400:
                    raise RuntimeError(f"redirect from {url} to {r.headers.get('Location')} not followed (club rule)")
                if r.status_code in (429, 500, 502, 503, 504):
                    ra = r.headers.get("Retry-After")
                    delay = float(ra) if ra and ra.isdigit() else None
                    raise _Retry(f"HTTP {r.status_code}", delay)
                r.raise_for_status()
                j = r.json()
                if isinstance(j, dict) and "error" in j:
                    raise _Retry(f"service error {j['error']}", None)
                return j
            except (requests.RequestException, ValueError, _Retry) as e:
                err = e
                if attempt >= self.retries:
                    break
                delay = getattr(e, "delay", None) or min(120.0, 3.0 * (2 ** attempt))
                delay += random.uniform(0, 1.5)
                log(f"   request failed ({e}); retry {attempt + 1}/{self.retries} in {delay:.0f}s")
                time.sleep(delay)
        raise RuntimeError(f"request failed after retries: {url} ({err})")


class _Retry(Exception):
    def __init__(self, msg, delay):
        super().__init__(msg)
        self.delay = delay


def arcgis_query(http: PoliteHttp, layer_url: str, bbox, max_features: int = 20000,
                 page: int = 2000) -> list:
    """Envelope query on an ArcGIS REST layer, GeoJSON in WGS84, paginated."""
    w, s, e, n = bbox
    feats, offset = [], 0
    while True:
        params = dict(where="1=1", geometry=f"{w},{s},{e},{n}",
                      geometryType="esriGeometryEnvelope", inSR=4326,
                      spatialRel="esriSpatialRelIntersects", outFields="OBJECTID",
                      returnGeometry="true", outSR=4326, f="geojson",
                      resultOffset=offset, resultRecordCount=page)
        j = http.get_json(layer_url + "/query", params)
        fs = j.get("features", []) or []
        feats.extend(fs)
        exceeded = j.get("exceededTransferLimit") or (j.get("properties") or {}).get("exceededTransferLimit")
        if not fs or not exceeded:
            break
        offset += len(fs)
        if len(feats) >= max_features:
            log(f"   capped at {len(feats)} features for {layer_url}")
            break
    return feats


def arcgis_count(http: PoliteHttp, layer_url: str, bbox) -> int:
    w, s, e, n = bbox
    j = http.get_json(layer_url + "/query", dict(
        where="1=1", geometry=f"{w},{s},{e},{n}", geometryType="esriGeometryEnvelope",
        inSR=4326, spatialRel="esriSpatialRelIntersects", returnCountOnly="true", f="json"))
    return int(j.get("count", 0))


# ================================================================ geometry
class LocalProj:
    """Transverse Mercator centred on the pin: metres, x=east, y=north."""

    def __init__(self, lat: float, lon: float):
        self.lat, self.lon = lat, lon
        crs = (f"+proj=tmerc +lat_0={lat} +lon_0={lon} +k=1 +x_0=0 +y_0=0 "
               f"+ellps=GRS80 +units=m +no_defs")
        self.fwd = Transformer.from_crs("EPSG:4326", crs, always_xy=True)
        self.inv = Transformer.from_crs(crs, "EPSG:4326", always_xy=True)

    def to_m(self, lon, lat):
        return self.fwd.transform(lon, lat)

    def to_ll(self, x, y):
        return self.inv.transform(x, y)


def bbox_around(lat, lon, half_km):
    dlat = half_km / 111.32
    dlon = half_km / (111.32 * max(0.05, math.cos(math.radians(lat))))
    return (lon - dlon, lat - dlat, lon + dlon, lat + dlat)


def _iter_lines(geom):
    t = geom.get("type")
    c = geom.get("coordinates")
    if t == "LineString":
        yield c
    elif t == "MultiLineString":
        yield from c
    elif t == "Polygon":
        yield from c
    elif t == "MultiPolygon":
        for poly in c:
            yield from poly


def line_network_nodes(features, min_degree=3):
    """Network junctions: line endpoints shared by >= min_degree line ends."""
    deg = {}
    for f in features:
        g = f.get("geometry")
        if not g:
            continue
        for line in _iter_lines(g):
            if len(line) < 2:
                continue
            for pt in (line[0], line[-1]):
                key = (round(pt[0], 6), round(pt[1], 6))
                deg[key] = deg.get(key, 0) + 1
    return [k for k, d in deg.items() if d >= min_degree]


def line_crossings(features_a, features_b, max_points=3000):
    """Points where two line sets cross (e.g. road over stream: bridges / culverts)."""
    from shapely.geometry import MultiLineString
    from shapely import unary_union
    la = [ln for f in features_a if f.get("geometry") for ln in _iter_lines(f["geometry"]) if len(ln) >= 2]
    lb = [ln for f in features_b if f.get("geometry") for ln in _iter_lines(f["geometry"]) if len(ln) >= 2]
    if not la or not lb:
        return []
    x = unary_union(MultiLineString(la)).intersection(unary_union(MultiLineString(lb)))
    pts = []
    for g in getattr(x, "geoms", [x]):
        if g.geom_type == "Point":
            pts.append((round(g.x, 6), round(g.y, 6)))
        if len(pts) >= max_points:
            break
    return pts


def polygon_corners(features, min_shared=3):
    """PLSS corners: polygon vertices shared by >= 3 section polygons."""
    cnt = {}
    for f in features:
        g = f.get("geometry")
        if not g:
            continue
        for ring in _iter_lines(g):
            seen = set()
            for pt in ring:
                key = (round(pt[0], 5), round(pt[1], 5))
                if key not in seen:
                    seen.add(key)
                    cnt[key] = cnt.get(key, 0) + 1
    return [k for k, d in cnt.items() if d >= min_shared]


def fetch_basemap(http: PoliteHttp, ref: str, lat: float, lon: float, half_km: float,
                  cache_dir: Path, use_cache: bool = True, offline: bool = False) -> dict:
    """Government basemap features + control-point candidates near the pin.
    offline (Nov 11, --offline): the cached basemap only, never a web request; a map with none raises 'offline: ...' (an ERROR row)."""
    cache = cache_dir / f"{safe_name(ref)}_basemap.json"
    d, why = None, "no cached basemap"
    if (use_cache or offline) and cache.exists():
        try:
            d = json.loads(cache.read_text())
        except ValueError:
            d, why = None, "cached basemap is not readable JSON"
        if d is not None:
            if TL is not None:
                ok, why = TL.cached_basemap_ok(d, lat, lon, half_km, __version__, offline=offline)
            else:
                ok = (abs(d.get("half_km", 0) - half_km) < 1e-6 and d.get("pin") == [lat, lon]
                      and d.get("version") == __version__ and not d.get("skipped"))   # a partial basemap is never reused from an older run
                why = "basemap from cache"
            if ok:
                log(f"   {why}")
                return d
    if offline:
        raise RuntimeError(f"offline: {why} ({cache}); fill <base>/cache with one run that has the network, then replay with --offline")
    bbox = bbox_around(lat, lon, half_km)
    prefix = ref.split("-")[0].upper()
    lines, points, sources, skipped = [], [], [], []

    def ask(name: str, layer_url: str):
        """Brandon, Nov 7: a basemap source whose robots.txt says STOP drops out of THIS run - no retry, no other route to it - and the
        trace goes on with the allowed sources that remain. Every result then says '<name> source skipped (robots)'. PoliteHttp keeps the
        STOP per host for the run, so the host is not asked again. Any other failure still stops the map as before."""
        try:
            return arcgis_query(http, layer_url, bbox)
        except RuntimeError as e:
            if not str(e).startswith("robots:"):
                raise
            if name not in skipped:
                skipped.append(name)
                log(f"   {name} source skipped (robots): {e}")
            return []
    if prefix == "US":
        roads = []
        for lid, nm in ((2, "primary"), (6, "secondary"), (8, "local")):
            fs = ask("road", f"{TIGER}/{lid}")
            log(f"   TIGER {nm} roads: {len(fs)}")
            roads += fs
        if "road" not in skipped:
            sources.append("US Census TIGERweb Transportation (roads)")
        rivers = ask("water", f"{NHD}/6")
        log(f"   NHD flowlines: {len(rivers)}")
        if "water" not in skipped:
            sources.append("USGS NHD flowlines (large scale)")
        water, shore = [], []
        try:   # Nov 11: TIGERweb hydrography; a failure here is logged and the map goes on with roads (it never stops a map)
            info = http.get_json(TIGER_HYDRO, {"f": "json"})
            ids = {}
            for lay in info.get("layers") or []:
                nm_ = str(lay.get("name") or "").lower()
                for kind_, want in TIGER_HYDRO_LAYERS:
                    if want in nm_ and 'label' not in nm_ and kind_ not in ids:
                        ids[kind_] = lay.get("id")
            for kind_, _w in TIGER_HYDRO_LAYERS:
                if ids.get(kind_) is None:
                    log(f"   TIGERweb hydrography: no '{_w}' layer listed")
                    continue
                fs = ask("census water", f"{TIGER_HYDRO}/{ids[kind_]}")
                log(f"   TIGERweb {_w}: {len(fs)}")
                (water if kind_ == "water" else shore).extend(fs)
        except RuntimeError as e:
            if str(e).startswith("robots:"):
                if "census water" not in skipped:
                    skipped.append("census water")
                log(f"   census water source skipped (robots): {e}")
            else:
                log(f"   TIGERweb hydrography not read ({str(e)[:160]}): matched without it")
        if water or shore:
            sources.append("US Census TIGERweb hydrography (water lines, shores)")
        plss = ask("land survey", f"{PLSS}/2")
        log(f"   BLM PLSS sections: {len(plss)}")
        if plss:
            sources.append("BLM CadNSDI PLSS sections")
        for kind, fs, pts in (("road", roads, line_network_nodes(roads)),
                              ("stream", rivers, line_network_nodes(rivers)),
                              ("road-stream", [], line_crossings(roads, rivers)),
                              ("water", water, line_network_nodes(water)),
                              ("shore", shore, []),
                              ("road-water", [], line_crossings(roads, water + shore)),
                              ("plss", plss, polygon_corners(plss))):
            for f in fs:
                g = f.get("geometry")
                if g:
                    for ln in _iter_lines(g):
                        lines.append([kind, ln])
            for p in pts:
                points.append([kind, p[0], p[1]])
    elif prefix in ("CA", "VE"):
        provs = []
        for i, pv in enumerate(NRN_PROVINCES):
            try:
                if arcgis_count(http, f"{NRN}/{NRN_ROAD_GROUP_BASES['local'] + i}", bbox) > 0:
                    provs.append(i)
            except RuntimeError:
                pass
        roads = []
        for i in provs:
            for grp, base in NRN_ROAD_GROUP_BASES.items():
                fs = ask("road", f"{NRN}/{base + i}")
                log(f"   NRN {NRN_PROVINCES[i]} {grp}: {len(fs)}")
                roads += fs
        if "road" not in skipped:
            sources.append("Canada National Road Network (NRN), Statistics Canada / NRCan")
        for f in roads:
            g = f.get("geometry")
            if g:
                for ln in _iter_lines(g):
                    lines.append(["road", ln])
        for p in line_network_nodes(roads):
            points.append(["road", p[0], p[1]])
    else:
        sources.append(f"none: no government basemap adapter for prefix {prefix}")
    d = dict(ref=ref, version=__version__, pin=[lat, lon], half_km=half_km, bbox=bbox, sources=sources, skipped=skipped,
             lines=lines, points=points,
             fetched=_dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"))
    atomic_write(cache, json.dumps(d))
    return d


# ===================================================== picture: boundary
def lab_kmeans(img, k, seed=0):
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
    pix = lab.reshape(-1, 3)
    rng = np.random.default_rng(seed)
    idx = rng.choice(len(pix), size=min(60000, len(pix)), replace=False)
    km = KMeans(n_clusters=k, n_init=4, random_state=seed).fit(pix[idx])
    labels = km.predict(pix).reshape(img.shape[:2])
    return labels, km.cluster_centers_, lab


def color_mask_from_rgb(lab, rgb, tol=18.0):
    target = cv2.cvtColor(np.uint8([[rgb[::-1]]]), cv2.COLOR_BGR2LAB).astype(np.float32)[0, 0]
    d = np.linalg.norm(lab - target, axis=2)
    return (d < tol).astype(np.uint8) * 255


def _border_fraction(mask):
    b = np.concatenate([mask[0, :], mask[-1, :], mask[:, 0], mask[:, -1]])
    return float((b > 0).mean())


def _is_rectangle(cnt):
    """True for an (almost) axis-aligned rectangle: frames, legend boxes, insets, photos."""
    area = cv2.contourArea(cnt)
    x, y, bw, bh = cv2.boundingRect(cnt)
    if area < 0.93 * bw * bh:
        return False
    ap = cv2.approxPolyDP(cnt, 0.02 * cv2.arcLength(cnt, True), True)
    return len(ap) <= 6


def _pin_px_from_affine(A, w, h, lat, lon):
    """The POTA pin's pixel on a GeoPDF page. The page's affine maps u = x/w, v = y/h to lon, lat; this is its inverse."""
    det = A[0] * A[4] - A[1] * A[3]
    if abs(det) < 1e-18 or not all(math.isfinite(x) for x in A):
        return None
    u = (A[4] * (lon - A[2]) - A[1] * (lat - A[5])) / det
    v = (-A[3] * (lon - A[2]) + A[0] * (lat - A[5])) / det
    return (u * w, v * h)


def detect_boundary(img, row, k=8, pin_px=None, m_per_px=None, expected_acres=None, max_acres=None):
    """Returns dict(kind, pts_px (n,2), mask_color, cluster, touches_edge, note) or None.

    Nov 7 (pin mode): with pin_px (the POTA pin's pixel on the page, known up front only on a GeoPDF) the colour is chosen BY THE PIN, not
    by total area. Only shapes that contain the pin, or run within PIN_NEAR_M of it, stay; a colour with none is skipped; among the rest a
    filled park tint beats a boundary ring, and the size closest to expected_acres wins (without a size, the tightest shape around the pin).
    Without pin_px nothing changes: the largest total area still wins, as before. This is what stops a statewide sheet's district ring or a
    road casing being traced as the park."""
    h, w = img.shape[:2]
    diag = math.hypot(w, h)
    pin_mode = pin_px is not None
    r_px = (PIN_NEAR_M / m_per_px) if (m_per_px and m_per_px > 0) else 0.02 * diag
    labels, centers, lab = lab_kmeans(img, k)
    kind = (row.get("kind") or "area").lower()
    masks = []
    if row.get("boundary_rgb"):
        masks.append(("boundary_rgb", color_mask_from_rgb(lab, row["boundary_rgb"],
                                                          float(row.get("color_tol", 18)))))
    else:
        for c in range(k):
            L, a, b = centers[c]
            chroma = math.hypot(a - 128, b - 128)
            if chroma < 12:      # greys / black text / white paper are never the boundary colour
                continue
            m = (labels == c).astype(np.uint8) * 255
            if _border_fraction(m) > 0.5:   # page background
                continue
            masks.append((f"cluster{c} Lab=({L:.0f},{a:.0f},{b:.0f})", m))
    best = None

    def _all_masks():
        """The colour masks; then (Nov 11, only when none of them gave a boundary and no boundary_rgb is set) a thick dark line
        (DARK_RING), through the same shape tests below and accepted only as a closed ring."""
        for x in masks:
            yield x
        if best is None and not row.get("boundary_rgb") and kind != "trail" and TM is not None and DARK_RING:
            yield (RING_ONLY + " (no colour gave a boundary)", TM.dark_ring_mask(img))
    # a colour picked by a person (boundary_rgb) may be a small parcel on a large regional map
    min_parcel, min_largest = (0.0005, 0.001) if row.get("boundary_rgb") else (0.002, 0.01)
    if pin_mode:
        # Nov 7: the "too small to be the park" floor exists for pages where we do NOT know where the park is. In pin mode we do, and on a
        # regional or statewide sheet the park is far below that floor: on the Sun Pass (US-5460) page 0.002 of the page is 98,000 acres,
        # while the park is 21,000. A shape AT THE PIN is judged on the shape itself, with only an absolute floor to keep out speckle.
        min_parcel, min_largest = PIN_MIN_SHAPE_PX / float(w * h), 0.0
    ks = max(5, int(round(diag * 0.006)))
    for name, m in _all_masks():
        if kind == "trail":
            cand = _longest_open_line(m, diag)
            if cand is not None and (best is None or cand[1] > best["score"]):
                best = dict(kind="trail", pts_px=cand[0], score=cand[1], mask_name=name)
        else:
            _k = 3 if name.startswith(RING_ONLY) else ks   # Nov 11: a dark boundary line is solid; closing wider would join it to road remnants
            mc = cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (_k, _k)))
            cnts, hier = cv2.findContours(mc, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
            if not cnts:
                continue
            hier = hier[0]
            parcels = []
            for oi in [i for i in range(len(cnts)) if hier[i][3] < 0]:
                area = cv2.contourArea(cnts[oi])
                frac = area / float(w * h)
                if not (min_parcel <= frac <= 0.85):
                    continue
                if _is_rectangle(cnts[oi]):      # map frame, legend swatch, inset or photo box
                    continue
                # accept only a FILLED shape (park tint) or a CLOSED RING (boundary line);
                # tree-like networks (streams, roads) of the same colour are rejected.
                inside = np.zeros_like(mc)
                cv2.drawContours(inside, cnts, oi, 255, -1)
                fill = cv2.countNonZero(cv2.bitwise_and(m, inside)) / max(area, 1.0)   # un-closed mask
                hole_ids = [i for i in range(len(cnts)) if hier[i][3] == oi]
                holes = [cv2.contourArea(cnts[i]) for i in hole_ids]
                ring = (max(holes) if holes else 0.0) / max(area, 1.0)
                if holes and _is_rectangle(cnts[hole_ids[int(np.argmax(holes))]]):
                    continue                     # frame/inset box with a leader line attached
                width = 2.0 * area / max(cv2.arcLength(cnts[oi], True), 1.0)   # mean thickness
                if name.startswith(RING_ONLY):        # Nov 11: a dark-line fallback mask counts only as a closed RING (a dark filled
                    #                                    area is a photo, a lake on an aerial, a drawing or a title bar, never a boundary);
                    #                                    a boundary drawn as two lobes that touch encloses two holes: their sum counts
                    _x, _y, _bw, _bh = cv2.boundingRect(cnts[oi])
                    if sum(holes) / max(area, 1.0) < 0.6 or _x <= 3 or _y <= 3 or _x + _bw >= w - 3 or _y + _bh >= h - 3:
                        continue                       # ... and one that runs off the picture is a road or a frame piece, not a ring
                    how = "ring"
                elif fill >= 0.5 and width >= 0.01 * diag:
                    how = "filled"
                elif ring >= 0.6:
                    how = "ring"
                elif row.get("boundary_rgb") and (fill >= 0.3 or ring >= 0.25):
                    how = "closed shape in the given boundary_rgb"   # thin strips on regional maps
                else:
                    continue
                ap = cv2.approxPolyDP(cnts[oi], 1.0, True).reshape(-1, 2).astype(float)
                parcels.append((frac, ap, how))
            if not parcels:
                continue
            if pin_mode:
                est = (lambda f: f * w * h * m_per_px * m_per_px / 4046.86) if (m_per_px and m_per_px > 0) else None
                exp = float(expected_acres) if expected_acres else None

                near = []
                for frac, ap, how in parcels:
                    d = cv2.pointPolygonTest(np.round(ap).astype(np.int32).reshape(-1, 1, 2),
                                             (float(pin_px[0]), float(pin_px[1])), True)
                    if d >= -r_px:                     # inside (d > 0) or within PIN_NEAR_M of the edge
                        near.append((frac, ap, how, max(0.0, -d)))
                if not near:
                    continue                           # this colour has nothing at the pin: never the park

                def _fit(t):
                    """Lower is better. With a size to aim at, how far this shape is from it decides and a filled tint only breaks a tie;
                    with no size, a filled park tint beats a boundary ring and then the tightest shape around the pin wins."""
                    # Nov 7 (coordinator): a shape bigger than the park type's ceiling ranks last. A size guessed from the TYPE only is
                    # not a target: it made CA-1248 pick the 265 ac shoreline ring over the 29 ac preserve the pin sits in.
                    over = 1 if (est and max_acres and est(t[0]) > float(max_acres)) else 0
                    if est and exp and est(t[0]) > 0:
                        return (over, abs(math.log(est(t[0]) / exp)), 0 if t[2] == "filled" else 1)
                    return (over, 0 if t[2] == "filled" else 1, t[0])
                near.sort(key=lambda t: (0 if t[3] == 0 else 1, _fit(t)))   # a shape containing the pin beats one merely near it
                pick = near[0]
                rest = [t for t in parcels if t[1] is not pick[1]]
                rank = (0 if pick[3] == 0 else 1, _fit(pick))             # lower is better; a colour whose shape CONTAINS the pin beats
                #                                                           one that only runs near it, whatever its size
                if best is None or rank < best.get("rank", (9, (float("inf"), float("inf"), float("inf")))):
                    ea = est(pick[0]) if est else None
                    others = ", ".join(f"{t[2]} ~{est(t[0]):.0f} ac" if est else t[2] for t in near[1:3])
                    best = dict(kind="area", pts_px=pick[1], parcels=[pick[1]] + [t[1] for t in rest], score=sum(t[0] for t in parcels),
                                pin_fit=(_fit(pick)[1] if (est and exp) else None), pin_acres=(est(pick[0]) if est else None),
                                rank=rank, at_pin=len(near), n_shapes=len(parcels),
                                mask_name=(f"{name}, {pick[2]}" + (f", ~{ea:.0f} ac" if ea else "") +
                                           f", {'contains' if pick[3] == 0 else f'{pick[3] * (m_per_px or 1):.0f} m from'} the pin"
                                           f", {len(parcels)} shape(s) in this colour" + (f"; also at the pin: {others}" if others else "")))
                continue
            parcels.sort(key=lambda t: -t[0])
            if parcels[0][0] < min_largest:
                continue
            score = sum(t[0] for t in parcels)
            if best is None or score > best["score"]:
                best = dict(kind="area", pts_px=parcels[0][1], parcels=[t[1] for t in parcels], score=score,
                            mask_name=f"{name}, {parcels[0][2]}, {len(parcels)} parcel(s)")
    if best is None:
        return None
    p = best["pts_px"]
    best["touches_edge"] = bool(((p[:, 0] <= 3) | (p[:, 1] <= 3) | (p[:, 0] >= w - 4) | (p[:, 1] >= h - 4)).any())
    return best


def _skeleton(mask, max_iter=300):
    """Zhang-Suen thinning (connected, 1-px skeleton), vectorised with numpy."""
    img = (mask > 0).astype(np.uint8)
    img = np.pad(img, 1)
    for _ in range(max_iter):
        changed = False
        for step in (0, 1):
            P2 = img[:-2, 1:-1]; P3 = img[:-2, 2:]; P4 = img[1:-1, 2:]; P5 = img[2:, 2:]
            P6 = img[2:, 1:-1]; P7 = img[2:, :-2]; P8 = img[1:-1, :-2]; P9 = img[:-2, :-2]
            nb = [P2, P3, P4, P5, P6, P7, P8, P9]
            B = sum(n.astype(np.int16) for n in nb)
            seq = nb + [P2]
            A = sum(((seq[k] == 0) & (seq[k + 1] == 1)).astype(np.int16) for k in range(8))
            c = img[1:-1, 1:-1] == 1
            if step == 0:
                m = c & (B >= 2) & (B <= 6) & (A == 1) & ((P2 * P4 * P6) == 0) & ((P4 * P6 * P8) == 0)
            else:
                m = c & (B >= 2) & (B <= 6) & (A == 1) & ((P2 * P4 * P8) == 0) & ((P2 * P6 * P8) == 0)
            if m.any():
                img[1:-1, 1:-1][m] = 0
                changed = True
        if not changed:
            break
    return (img[1:-1, 1:-1] * 255).astype(np.uint8)


def _longest_open_line(mask, diag):
    """Longest path through the skeleton of the (dash-closed) route colour."""
    ks = max(3, int(round(diag * 0.004)))
    mc = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (ks, ks)))
    n, lbl, stats, _ = cv2.connectedComponentsWithStats(mc)
    if n <= 1:
        return None
    big = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    comp = (lbl == big).astype(np.uint8) * 255
    sk = _skeleton(comp)
    ys, xs = np.nonzero(sk)
    if len(xs) < 20:
        return None
    nodes = {(int(x), int(y)) for x, y in zip(xs, ys)}

    def bfs(start):
        prev = {start: None}
        q = [start]
        i = 0
        while i < len(q):
            x, y = q[i]
            i += 1
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    nb = (x + dx, y + dy)
                    if nb in nodes and nb not in prev:
                        prev[nb] = (x, y)
                        q.append(nb)
        return q[-1], prev

    a, _ = bfs(next(iter(nodes)))
    b, prev = bfs(a)
    path = []
    cur = b
    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    if len(path) < 0.05 * diag:
        return None
    pts = np.array(path, float)
    pts = cv2.approxPolyDP(pts.astype(np.float32).reshape(-1, 1, 2), 1.0, False).reshape(-1, 2)
    return pts.astype(float), float(len(path))


# ================================================== picture: junctions
def _lsd_candidates(img, exclude=None, roi=None):
    """Road-junction-like points (all of them, unordered): LSD segments -> pairwise crossings -> DBSCAN. Returns (points, weights, arms, segs).
    Crossings of two exactly horizontal/vertical segments are skipped: on picture
    maps those are almost always frames, photo boxes, legends and insets."""
    h, w = img.shape[:2]
    diag = math.hypot(w, h)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    lsd = cv2.createLineSegmentDetector(cv2.LSD_REFINE_STD)
    segs = lsd.detect(gray)[0]
    if segs is None:
        return np.zeros((0, 2)), np.zeros(0), np.zeros(0), np.zeros((0, 4))
    segs = segs.reshape(-1, 4).astype(np.float64)
    ln = np.hypot(segs[:, 2] - segs[:, 0], segs[:, 3] - segs[:, 1])
    segs = segs[ln >= 0.006 * diag]
    if len(segs) > 6000:
        ln = np.hypot(segs[:, 2] - segs[:, 0], segs[:, 3] - segs[:, 1])
        segs = segs[np.argsort(-ln)[:6000]]
    if len(segs) < 2:
        return np.zeros((0, 2)), np.zeros(0), np.zeros(0), segs
    p1 = segs[:, :2]
    d = segs[:, 2:] - segs[:, :2]
    L = np.hypot(d[:, 0], d[:, 1])
    ext = 8.0 / L
    a90 = np.degrees(np.arctan2(d[:, 1], d[:, 0])) % 90.0
    axis = (a90 < 1.5) | (a90 > 88.5)
    sin_min = math.sin(math.radians(35))
    pts = []
    n = len(segs)
    for i in range(n - 1):
        j = np.arange(i + 1, n)
        cr = d[i, 0] * d[j, 1] - d[i, 1] * d[j, 0]
        ok = np.abs(cr) >= sin_min * L[i] * L[j]
        if axis[i]:
            ok &= ~axis[j]
        if not ok.any():
            continue
        j, cr = j[ok], cr[ok]
        r = p1[j] - p1[i]
        ti = (r[:, 0] * d[j, 1] - r[:, 1] * d[j, 0]) / cr
        tj = (r[:, 0] * d[i, 1] - r[:, 1] * d[i, 0]) / cr
        ok = (ti >= -ext[i]) & (ti <= 1 + ext[i]) & (tj >= -ext[j]) & (tj <= 1 + ext[j])
        if ok.any():
            pts.append(p1[i] + ti[ok, None] * d[i])
    if not pts:
        return np.zeros((0, 2)), np.zeros(0), np.zeros(0), segs
    pts = np.vstack(pts)
    if roi is not None:
        x0, y0, x1, y1 = roi
        pts = pts[(pts[:, 0] >= x0) & (pts[:, 0] <= x1) & (pts[:, 1] >= y0) & (pts[:, 1] <= y1)]
    if exclude:
        keep = np.ones(len(pts), bool)
        for x0, y0, x1, y1 in exclude:
            keep &= ~((pts[:, 0] >= x0) & (pts[:, 0] <= x1) & (pts[:, 1] >= y0) & (pts[:, 1] <= y1))
        pts = pts[keep]
    if len(pts) == 0:
        return np.zeros((0, 2)), np.zeros(0), np.zeros(0), segs
    lab = DBSCAN(eps=6.0, min_samples=2).fit(pts).labels_
    cents, wts = [], []
    for c in set(lab) - {-1}:
        sel = pts[lab == c]
        cents.append(sel.mean(0))
        wts.append(len(sel))
    if not cents:
        return np.zeros((0, 2)), np.zeros(0), np.zeros(0), segs
    cents, wts = np.array(cents), np.array(wts, float)
    # A junction needs >= 3 arms leaving it in different directions (T = 3, X = 4).
    # A bend of one road (2 arms) or a line touching a label is rejected.
    arms = np.array([_count_arms(cp, p1, d, L) for cp in cents])
    sel = arms >= 3
    cents, wts, arms = cents[sel], wts[sel], arms[sel]
    if len(cents) == 0:
        return np.zeros((0, 2)), np.zeros(0), np.zeros(0), segs
    return cents, wts, arms, segs


def detect_junctions(img, max_points=70, exclude=None, roi=None, band=None, box_exclude=None):
    """Road-junction-like points for the matcher, best first: LSD crossings with >= 3 arms (as before), plus (Nov 11, BAND_JUNCTIONS) the
    junctions of roads drawn as bands (kpc_trace_marks.band_junctions), which go first; points in exclude boxes (index.json exclude_px)
    and (Nov 11, BOX_MASK) in box_exclude (legend / title / inset / icon boxes the park outline does not run through) are dropped.
    Then non-maximum suppression (15 px) and at most max_points. Returns (points, weights, segs)."""
    band = BAND_JUNCTIONS if band is None else band
    cents, wts, arms, segs = _lsd_candidates(img, exclude=exclude, roi=roi)
    first = np.zeros(len(cents), bool)
    if band and TM is not None:
        bp, ba, _bh, rsegs = TM.band_marks(img, roi=roi)
        if len(rsegs):
            segs = np.vstack([np.asarray(segs, float).reshape(-1, 4), rsegs])   # the bands' middle lines count as picture lines too
        for x0, y0, x1, y1 in (exclude or []):          # the LSD points had index.json's exclude_px applied already
            k_ = ~((bp[:, 0] >= x0) & (bp[:, 0] <= x1) & (bp[:, 1] >= y0) & (bp[:, 1] <= y1)) if len(bp) else np.zeros(0, bool)
            bp, ba = bp[k_], ba[k_]
        if len(bp):
            cents = np.vstack([cents.reshape(-1, 2), bp]) if len(cents) else bp
            wts = np.r_[wts, np.full(len(bp), 1000.0)]
            arms = np.r_[arms, ba.astype(float)]
            first = np.r_[first, np.ones(len(bp), bool)]
    if len(cents) and box_exclude:
        keep = np.ones(len(cents), bool)
        for x0, y0, x1, y1 in box_exclude:
            keep &= ~((cents[:, 0] >= x0) & (cents[:, 0] <= x1) & (cents[:, 1] >= y0) & (cents[:, 1] <= y1))
        cents, wts, arms, first = cents[keep], wts[keep], arms[keep], first[keep]
    if len(cents) == 0:
        return np.zeros((0, 2)), np.zeros(0), segs
    order = np.lexsort((-wts, -arms, ~first))
    keep = []
    for o in order:          # non-maximum suppression, 15 px
        if all(np.hypot(*(cents[o] - cents[k])) >= 15 for k in keep):
            keep.append(o)
        if len(keep) >= max_points:
            break
    return cents[keep], wts[keep], segs


def _count_arms(cp, p1, d, L, near_px=5.0, reach_px=12.0, min_arm_px=12.0):
    v = cp - p1
    t = np.clip((v[:, 0] * d[:, 0] + v[:, 1] * d[:, 1]) / (L * L), 0.0, 1.0)
    foot = p1 + t[:, None] * d
    perp = np.abs(v[:, 0] * d[:, 1] - v[:, 1] * d[:, 0]) / L      # distance to the infinite line
    dist = np.hypot(*(foot - cp).T)                                 # distance to the segment
    cand = np.nonzero((perp <= near_px) & (dist <= reach_px))[0]
    angs = []
    for i in cand:
        a, b = p1[i], p1[i] + d[i]
        for e in (a, b):
            if np.hypot(*(e - cp)) >= min_arm_px:
                angs.append(math.degrees(math.atan2(e[1] - cp[1], e[0] - cp[0])))
    if len(angs) < 3:
        return len(angs)
    angs = sorted(a % 360 for a in angs)
    groups = 1
    for a0, a1 in zip(angs, angs[1:]):
        if a1 - a0 > 25:
            groups += 1
    if groups > 1 and (angs[0] + 360 - angs[-1]) <= 25:
        groups -= 1
    return groups


# ============================================================ matching
def _cplx_img(P):  # image (x, y-down) -> complex with y up
    return P[:, 0] - 1j * P[:, 1]


def fit_similarity_c(p, q):
    pm, qm = p.mean(), q.mean()
    pc, qc = p - pm, q - qm
    den = np.sum(np.abs(pc) ** 2)
    if den <= 0:
        return None
    z = np.sum(np.conj(pc) * qc) / den
    return z, qm - z * pm


class Prior:
    def __init__(self, smin, smax, rot_max_deg, pin_box_px, min_pair_px=60.0):
        self.smin, self.smax = smin, smax
        self.rot = math.radians(rot_max_deg)
        self.pin_box = pin_box_px      # (x0, y0, x1, y1) image box the pin must fall in
        self.min_pair_px = min_pair_px

    def ok(self, z):
        r = abs(z)
        return self.smin <= r <= self.smax and abs(np.angle(z)) <= self.rot


def hough_hypotheses(P, Q, c_img, prior: Prior, top=15000):
    """Similarity hypotheses from (image pair, basemap pair) votes, binned in
    (log scale, rotation, position of the image centre)."""
    p = _cplx_img(P)
    q = Q[:, 0] + 1j * Q[:, 1]
    c = c_img[0] - 1j * c_img[1]
    N, M = len(p), len(q)
    if N < 2 or M < 2:
        return []
    ii, jj = np.triu_indices(N, 1)
    dp = p[jj] - p[ii]
    keep = np.abs(dp) >= prior.min_pair_px
    ii, jj, dp = ii[keep], jj[keep], dp[keep]
    kk, ll = np.nonzero(~np.eye(M, dtype=bool))
    dq = q[ll] - q[kk]
    keep = np.abs(dq) >= prior.min_pair_px * prior.smin
    kk, ll, dq = kk[keep], ll[keep], dq[keep]
    ang_q = np.angle(dq)
    order = np.argsort(ang_q)
    kk, ll, dq, ang_q = kk[order], ll[order], dq[order], ang_q[order]
    len_q = np.abs(dq)
    x0, y0, x1, y1 = prior.pin_box
    keys_all, z_all, u_all = [], [], []
    for a in range(len(dp)):
        ap = np.angle(dp[a])
        lo, hi = ap - prior.rot, ap + prior.rot
        idx = []
        for l_, h_ in ((lo, hi), (lo + 2 * np.pi, hi + 2 * np.pi), (lo - 2 * np.pi, hi - 2 * np.pi)):
            s0, s1 = np.searchsorted(ang_q, [l_, h_])
            if s1 > s0:
                idx.append(np.arange(s0, s1))
        if not idx:
            continue
        idx = np.concatenate(idx)
        lp = abs(dp[a])
        idx = idx[(len_q[idx] >= prior.smin * lp) & (len_q[idx] <= prior.smax * lp)]
        if len(idx) == 0:
            continue
        z = dq[idx] / dp[a]
        u = q[kk[idx]] + z * (c - p[ii[a]])          # metric position of image centre
        pin = c - u / z                                  # pin (0,0) in image (complex, y up)
        px, py = pin.real, -pin.imag
        ok = (px >= x0) & (px <= x1) & (py >= y0) & (py <= y1)
        if not ok.any():
            continue
        z, u = z[ok], u[ok]
        ls = np.floor(np.log(np.abs(z)) / 0.07).astype(np.int64)
        th = np.floor(np.degrees(np.angle(z)) / 4.0).astype(np.int64)
        B = np.maximum(100.0, 60.0 * np.exp((ls + 0.5) * 0.07))
        ux = np.floor(u.real / B).astype(np.int64)
        uy = np.floor(u.imag / B).astype(np.int64)
        key = (((ls + 500) * 1000 + (th + 100)) * 100000 + (ux + 50000)) * 100000 + (uy + 50000)
        keys_all.append(key)
        z_all.append(z)
        u_all.append(u)
    if not keys_all:
        return []
    keys = np.concatenate(keys_all)
    zs = np.concatenate(z_all)
    us = np.concatenate(u_all)
    uk, inv, cnt = np.unique(keys, return_inverse=True, return_counts=True)
    # raw vote counts are biased toward coarse scales (more long basemap pairs);
    # normalise by the mean count of bins with the same scale bin.
    lsb = uk // (1000 * 100000 * 100000)
    _, lsi = np.unique(lsb, return_inverse=True)
    mean_ls = np.bincount(lsi, weights=cnt) / np.bincount(lsi)
    norm = cnt / mean_ls[lsi]
    top_b = np.unique(np.r_[np.argsort(-norm)[:top], np.argsort(-cnt)[:top // 5]])
    zr = np.bincount(inv, weights=zs.real)
    zi = np.bincount(inv, weights=zs.imag)
    ur = np.bincount(inv, weights=us.real)
    ui = np.bincount(inv, weights=us.imag)
    hyps = []
    for b in top_b:
        n = cnt[b]
        z = (zr[b] + 1j * zi[b]) / n
        u = (ur[b] + 1j * ui[b]) / n
        hyps.append((int(n), z, u - z * c))
    return hyps


def refine(P, Q, tree, z, t, prior: Prior, tol_m, iters=400, seed=0):
    """Robust refinement of a rough similarity hypothesis: tentative neighbour pairs
    in a wide radius, 2-point RANSAC over them, then closest-point iterations.
    Returns (one-to-one inlier pairs, z, t)."""
    p = _cplx_img(P)
    q = Q[:, 0] + 1j * Q[:, 1]
    m = z * p + t
    R0 = min(600.0, max(3.0 * tol_m, 70.0 * abs(z)))
    ind, dist = tree.query_radius(np.c_[m.real, m.imag], r=R0, return_distance=True, sort_results=True)
    tp, tq = [], []
    for i, (js, ds) in enumerate(zip(ind, dist)):
        for j in js[:3]:
            tp.append(i)
            tq.append(j)
    if len(tp) < 2:
        return [], z, t
    tp, tq = np.array(tp), np.array(tq)
    rng = np.random.default_rng(seed)
    a = rng.integers(0, len(tp), iters)
    b = rng.integers(0, len(tp), iters)
    ok = (tp[a] != tp[b]) & (tq[a] != tq[b])
    a, b = a[ok], b[ok]
    best_z, best_t, best_n = z, t, -1
    if len(a):
        dp = p[tp[b]] - p[tp[a]]
        good = np.abs(dp) > 1e-6
        a, b, dp = a[good], b[good], dp[good]
        Z = (q[tq[b]] - q[tq[a]]) / dp
        okp = (np.abs(Z) >= prior.smin) & (np.abs(Z) <= prior.smax) & (np.abs(np.angle(Z)) <= prior.rot)
        Z, a = Z[okp], a[okp]
        if len(Z):
            T = q[tq[a]] - Z * p[tp[a]]
            r = np.abs(Z[:, None] * p[tp][None, :] + T[:, None] - q[tq][None, :])
            cnt = (r < tol_m).sum(1)
            k = int(np.argmax(cnt))
            best_z, best_t, best_n = Z[k], T[k], cnt[k]
    z, t = (best_z, best_t) if best_n >= 2 else (z, t)
    for tol in (1.5 * tol_m, tol_m, tol_m):
        m = z * p + t
        dd, idx = tree.query(np.c_[m.real, m.imag], k=1)
        dd, idx = dd[:, 0], idx[:, 0]
        best = {}
        for i in np.nonzero(dd < tol)[0]:        # one-to-one: closest image point wins
            j = idx[i]
            if j not in best or dd[i] < dd[best[j]]:
                best[j] = i
        if len(best) < 2:
            return [], z, t
        pi = np.array(list(best.values()))
        qj = np.array(list(best.keys()))
        res = fit_similarity_c(p[pi], q[qj])
        if res is None or not prior.ok(res[0]):
            return [], z, t
        z, t = res
    m = z * p + t
    dd, idx = tree.query(np.c_[m.real, m.imag], k=1)
    best = {}
    for i in np.nonzero(dd[:, 0] < tol_m)[0]:
        j = idx[i, 0]
        if j not in best or dd[i, 0] < dd[best[j], 0]:
            best[j] = i
    return sorted((i, j) for j, i in best.items()), z, t


def search_tol(z, cap):
    """Correspondence search radius: 8 picture pixels, kept within 20 m .. cap."""
    return max(20.0, min(cap, 8.0 * abs(z)))


def match(P, Q, c_img, prior: Prior, tol_cap, line=None):
    """line: None, or f(z, t) -> (share, z_score, n) (kpc_trace_edges.LineEvidence.score on this basemap's line samples). With it, each
    refined candidate is scored junctions + LINE_WEIGHT x line z (the same on the real basemap and on a decoy); 'score_points' keeps the
    junction part alone."""
    if len(P) < MIN_POINTS or len(Q) < MIN_POINTS:
        return None
    tree = KDTree(Q)
    best = None
    ext = Q.max(0) - Q.min(0)
    rho = len(Q) / max(ext[0] * ext[1], 1.0)      # basemap control points per m^2
    hyps = [h for h in hough_hypotheses(P, Q, c_img, prior) if prior.ok(h[1])]
    if not hyps:
        return None
    # quick verification: inlier count of every hypothesis, refine only the best 40
    p = _cplx_img(P)
    Z = np.array([h[1] for h in hyps])
    T = np.array([h[2] for h in hyps])
    quick = np.zeros(len(hyps), int)
    TOL = np.maximum(20.0, np.minimum(tol_cap, 8.0 * np.abs(Z)))
    for s0 in range(0, len(hyps), 500):
        m = Z[s0:s0 + 500, None] * p[None, :] + T[s0:s0 + 500, None]
        dist, _ = tree.query(np.c_[m.real.ravel(), m.imag.ravel()], k=1)
        quick[s0:s0 + 500] = (dist[:, 0].reshape(m.shape) < TOL[s0:s0 + 500, None]).sum(1)
    lam = len(P) * rho * np.pi * TOL ** 2
    qscore = (quick - lam) / np.sqrt(lam + 1.0)
    for hi in np.argsort(-qscore)[:150]:
        votes, z, t = hyps[hi]
        tol_m = search_tol(z, tol_cap)
        pairs, z2, t2 = refine(P, Q, tree, z, t, prior, tol_m)
        if not pairs:
            continue
        pi = np.array([a for a, _ in pairs])
        qj = np.array([b for _, b in pairs])
        r = np.abs(z2 * p[pi] + t2 - (Q[qj, 0] + 1j * Q[qj, 1]))
        rms = float(np.sqrt(np.mean(r ** 2)))
        # significance: inliers above what chance would give at this radius
        lam = len(P) * rho * math.pi * tol_m ** 2
        score = (len(pairs) - lam) / math.sqrt(lam + 1.0)
        ls, lz, ln_ = line(z2, t2) if (line is not None and LINE_WEIGHT > 0) else (0.0, 0.0, 0)
        cand = dict(pairs=pairs, z=z2, t=t2, n=len(pairs), rms=rms, votes=votes, tol=tol_m,
                    chance=lam, score=score + LINE_WEIGHT * lz, score_points=score, line_share=ls, line_z=lz, line_n=ln_)
        if best is None or (cand["score"], -cand["rms"]) > (best["score"], -best["rms"]):
            best = cand
    return best


# ============================================================= models
class Model:
    """Image (x, y-down px) -> local metres (east, north)."""

    def __init__(self, kind, P, Qm):
        self.kind = kind
        self.mu = P.mean(0)
        self.sd = max(P.std(), 1.0)
        if kind == "similarity":
            z, t = fit_similarity_c(_cplx_img(P), Qm[:, 0] + 1j * Qm[:, 1])
            self.z, self.t = z, t
        else:
            A = self._design(P)
            self.coef, *_ = np.linalg.lstsq(A, Qm, rcond=None)

    def _design(self, P):
        x = (P[:, 0] - self.mu[0]) / self.sd
        y = (P[:, 1] - self.mu[1]) / self.sd
        if self.kind == "affine":
            return np.c_[np.ones_like(x), x, y]
        return np.c_[np.ones_like(x), x, y, x * x, x * y, y * y]

    def __call__(self, P):
        P = np.asarray(P, float).reshape(-1, 2)
        if self.kind == "similarity":
            m = self.z * _cplx_img(P) + self.t
            return np.c_[m.real, m.imag]
        return self._design(P) @ self.coef


MODEL_MIN = {"similarity": 2, "affine": 3, "poly2": 6}


def rms_and_loo(kind, P, Qm):
    mdl = Model(kind, P, Qm)
    res = np.hypot(*(mdl(P) - Qm).T)
    rms = float(np.sqrt(np.mean(res ** 2)))
    loo = []
    for i in range(len(P)):
        k = np.ones(len(P), bool)
        k[i] = False
        if k.sum() < MODEL_MIN[kind]:
            return mdl, rms, float("nan"), res
        m2 = Model(kind, P[k], Qm[k])
        loo.append(np.hypot(*(m2(P[i:i + 1])[0] - Qm[i])))
    return mdl, rms, float(np.sqrt(np.mean(np.square(loo)))), res


def choose_model(P, Qm):
    """Fewest-parameters model that still leaves >= 2 redundant equations:
    n=3 similarity (4 params), 4..11 affine (6), >=12 poly2 (12) if it beats affine
    on leave-one-out error."""
    n = len(P)
    sv = np.linalg.svd(P - P.mean(0), compute_uv=False)
    collinear = sv[-1] < 0.08 * sv[0]
    kinds = ["similarity"]
    if n >= 4 and not collinear:
        kinds = ["affine"]
    if n >= 12 and not collinear:
        kinds = ["affine", "poly2"]
    best = None
    for kd in kinds:
        mdl, rms, loo, res = rms_and_loo(kd, P, Qm)
        score = loo if not math.isnan(loo) else rms
        if best is None or score < best[4]:
            best = (kd, mdl, rms, loo, score, res)
    kd, mdl, rms, loo, _, res = best
    return kd, mdl, rms, loo, res, collinear


def invert_model(mdl, w, h):
    """Approximate metres -> pixels mapping (debug drawing only)."""
    gx, gy = np.meshgrid(np.linspace(0, w, 25), np.linspace(0, h, 25))
    G = np.c_[gx.ravel(), gy.ravel()]
    M = mdl(G)
    A = np.c_[np.ones(len(M)), M, M[:, 0] ** 2, M[:, 0] * M[:, 1], M[:, 1] ** 2]
    mu, sd = M.mean(0), max(M.std(), 1.0)
    Mn = (M - mu) / sd
    A = np.c_[np.ones(len(M)), Mn, Mn[:, 0] ** 2, Mn[:, 0] * Mn[:, 1], Mn[:, 1] ** 2]
    coef, *_ = np.linalg.lstsq(A, G, rcond=None)

    def f(X):
        Xn = (np.asarray(X, float).reshape(-1, 2) - mu) / sd
        return np.c_[np.ones(len(Xn)), Xn, Xn[:, 0] ** 2, Xn[:, 0] * Xn[:, 1], Xn[:, 1] ** 2] @ coef
    return f


# ============================================================== utils
def safe_name(ref):
    return "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in ref)


def atomic_write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text)
    os.replace(tmp, path)


def load_index(base: Path):
    raw = json.loads((base / "index.json").read_text())
    rows = raw if isinstance(raw, list) else [dict(ref=k, **(v if isinstance(v, dict) else {}))
                                              for k, vs in raw.items() for v in (vs if isinstance(vs, list) else [vs])]
    idx = {}
    for r in rows:
        idx.setdefault(r["ref"], []).append(r)
    return idx


def source_type(row):
    return str((row or {}).get("source_type") or "official").strip().lower()


def select_row(rows):
    """R-G9U: an official row always wins; unofficial rows are used only when no official row exists.
    Returns (row to process, list of unofficial rows skipped because an official one exists)."""
    rows = rows or []
    off = [r for r in rows if source_type(r) == "official"]
    other = [r for r in rows if source_type(r) != "official"]
    if off:
        return off[0], [r for r in other if source_type(r) == "unofficial"]
    return (other[0] if other else None), []


def read_report(path: Path):
    if not path.exists():
        return {}
    with path.open(newline="") as f:
        return {r["ref"]: r for r in csv.DictReader(f)}


def write_report(path: Path, rows: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".csv.tmp")
    with tmp.open("w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=REPORT_FIELDS, extrasaction="ignore")
        wr.writeheader()
        for ref in sorted(rows):
            wr.writerow({k: rows[ref].get(k, "") for k in REPORT_FIELDS})
    os.replace(tmp, path)


def find_map(base: Path, ref: str, row=None):
    if row and row.get("map_file"):
        p = base / "maps" / str(row["map_file"])
        return p if p.exists() else None
    if HONOR_IMAGE and TL is not None and TL.chosen_image(row):   # Nov 2 review (fix): the image the prep step chose, not the first jpg
        p = base / "maps" / TL.chosen_image(row)
        return p if p.exists() else None
    sub = base / "maps" / ("unofficial" if source_type(row) == "unofficial" else "")
    hits = sorted(glob.glob(str(sub / f"{glob.escape(ref)}_*.jp*g")))
    return Path(hits[0]) if hits else None


def check_row(row):
    """Rule 1/4 and R-G9U bookkeeping."""
    st = source_type(row)
    if st not in ("official", "unofficial"):
        return f"source_type must be 'official' or 'unofficial', not {row.get('source_type')!r}"
    need = ["ref", "name", "source_url", "page"] + (["agency"] if st == "official" else ["source_org", "notes"])
    missing = [k for k in need if str(row.get(k) or "").strip() == ""]
    if missing:
        why = ("rule 1/4 needs agency + source URL + page" if st == "official" else
               "R-G9U needs source URL + page + source_org (exact publisher name) + notes (why nothing official, where looked)")
        return f"index.json {st} row missing {', '.join(missing)} ({why})"
    url = str(row["source_url"]).lower()
    host = (urlparse(url).hostname or "").lower()
    if not host and not url.startswith("file:"):
        return f"source_url {row['source_url']!r} is not a URL"
    for w in BANNED_MAP_SOURCE_WORDS:
        if w in host or (w.count("/") and w in url):
            return f"source_url host {host} is a banned app / crowd-sourced map service ({w}; rule 1 / R-G9U)"
    if st == "unofficial":
        org = str(row["source_org"]).lower().replace(" ", "").replace("-", "")
        for w in BANNED_ORG_WORDS:
            if w in org:
                return f"source_org {row['source_org']!r} is a banned app / crowd-sourced map service (R-G9U)"
    return None


# ======================================================== debug images
def draw_poly(img, pts, color, thick, closed=True):
    if pts is None or len(pts) < 2:
        return
    cv2.polylines(img, [np.round(pts).astype(np.int32).reshape(-1, 1, 2)], closed, color, thick, cv2.LINE_AA)


def put(img, text, y, color=(0, 0, 0)):
    cv2.putText(img, text, (12, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 4, cv2.LINE_AA)
    cv2.putText(img, text, (12, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2, cv2.LINE_AA)


def _dbg_write(path, im, px=1600):
    """Nov 2: debug pictures go to tools-out: small JPEGs (the sharp 4000 px page made 10 MB PNGs)."""
    h, w = im.shape[:2]
    if max(h, w) > px:
        s = px / float(max(h, w)); im = cv2.resize(im, (int(w * s), int(h * s)), interpolation=cv2.INTER_AREA)
    cv2.imwrite(str(path), im, [int(cv2.IMWRITE_JPEG_QUALITY), 75])


# ======================================================= one map
def process_one(ref, row, base: Path, out: Path, pins, http, args):
    res = dict(ref=ref, status="ERROR", fit_m="", n_points=0, why="", fit_loo_m="", model="",
               decoy_best="", flags="", source_url=row.get("source_url", "") if row else "",
               page=row.get("page", "") if row else "",
               date=_dt.date.today().isoformat(), source_type=source_type(row) if row else "",
               source_org=(row or {}).get("source_org", ""), notes=(row or {}).get("notes", ""))
    dbg = out / "debug"
    dbg.mkdir(parents=True, exist_ok=True)
    sref = safe_name(ref)
    stale = out / f"{sref}.json"
    if row is None:
        res["why"] = "ref not in index.json"
        return res
    bad = check_row(row)
    if bad:
        res["why"] = bad
        return res
    if ref not in pins:
        res["why"] = "no POTA pin in pins.json"
        return res
    lat, lon = map(float, pins[ref])
    mp = find_map(base, ref, row)
    if mp is None:
        res["why"] = (f"map_file maps/{row['map_file']} not found" if row.get("map_file") else
                      f"no maps/{'unofficial/' if source_type(row) == 'unofficial' else ''}{ref}_*.jpg")
        return res
    img = cv2.imread(str(mp), cv2.IMREAD_COLOR)
    if img is None:
        res["why"] = f"cannot read {mp.name}"
        return res
    flags = []
    h, w = img.shape[:2]
    _mx = int(os.environ.get("KPC_TRACE_MAX_PX") or 2000)   # Nov 2 review: the sharp 4000 px page (kpc_picture_geo.py) keeps thin lines
    if max(h, w) > _mx:
        s = float(_mx) / max(h, w)
        img = cv2.resize(img, (int(w * s), int(h * s)), interpolation=cv2.INTER_AREA)
        h, w = img.shape[:2]
        flags.append(f"image downscaled to {_mx} px")

    # ---- Nov 7: on a GeoPDF the page's own coordinates are known BEFORE the colour is chosen, so the pin's pixel is known too. Pass it to
    # detect_boundary (pin mode) so the colour is chosen by the pin instead of by total area. The plausibility result is computed once here
    # and reused by the gate in step 5.
    GEO = (row.get("geo") or {}) if os.environ.get("KPC_TRACE_GEOPDF", "1") != "0" else {}
    geo_why, geo_info, geo_resid_ok = [], {}, None
    _A = None
    if GEO.get("affine"):
        try:
            _A = [float(x) for x in GEO["affine"]]
        except (TypeError, ValueError):
            _A = None
        if TL is not None:
            try:
                _gok, geo_why, geo_info = TL.geopdf_plausible(GEO["affine"], w, h, GEO.get("fit_err_m"), (lat, lon))
            except Exception as e:  # noqa: BLE001
                geo_why, geo_info = [f"geopdf scale: the georeference could not be checked ({type(e).__name__})"], {}
            geo_resid_ok = not any(x.startswith("geopdf residual") for x in geo_why)
    pin_px = m_per_px = None
    if PIN_PICK and _A is not None and geo_info.get("pin_on_page"):
        pin_px = _pin_px_from_affine(_A, w, h, lat, lon)
        m_per_px = geo_info.get("m_per_px_x")
    _acres_row = float(row["acres"]) if row.get("acres") not in (None, "") else None
    # Nov 7 (coordinator): only the park's REAL size is a ranking target; the type gives a ceiling (bigger shapes rank last), not a target
    _expect = _acres_row
    _max_ac = (TL.ceiling_acres(row.get("type")) if TL is not None else None)

    # ---- step 1: boundary / route line
    bnd = detect_boundary(img, row, k=args.k, pin_px=pin_px, m_per_px=m_per_px, expected_acres=_expect, max_acres=_max_ac)
    if pin_px is not None:
        flags.append(f"boundary colour chosen at the POTA pin" + (f" ({bnd['at_pin']} of {bnd['n_shapes']} shapes in that colour "
                     f"are at the pin)" if bnd and bnd.get("at_pin") else ""))
    im1 = img.copy()
    if bnd is not None:
        for pp in (bnd.get("parcels") or [])[1:]:
            draw_poly(im1, pp, (255, 160, 255), 3)
        draw_poly(im1, bnd["pts_px"], (255, 0, 255), 5, closed=bnd["kind"] == "area")
        put(im1, f"{ref} detected {bnd['kind']} ({bnd['mask_name']})", 30)
    else:
        put(im1, f"{ref}: no boundary line found", 30, (0, 0, 255))
    _dbg_write(dbg / f"{sref}_1_boundary.jpg", im1)
    if bnd is None:
        res.update(status="NO LINE", why=("no closed shape in any colour contains or runs within "
                                          f"{PIN_NEAR_M:g} m of the POTA pin on this page (pin at {pin_px[0]:.0f}, {pin_px[1]:.0f} px); "
                                          "the colour may need boundary_rgb in index.json" if pin_px is not None else
                                          "no closed boundary colour / route line found on the picture "
                                          "(try boundary_rgb in index.json)"))
        if stale.exists():
            stale.unlink()
        return res
    if bnd["touches_edge"]:
        flags.append("boundary touches picture edge (map may be clipped)")
    if str(bnd.get("mask_name", "")).startswith(RING_ONLY):
        flags.append("boundary = a thick dark ring line (no colour gave one; Nov 11 dark_ring)")
    bpts = bnd["pts_px"]

    # ---- Nov 2 (review): a GeoPDF page carries its own coordinates (kpc_picture_geo.py wrote row['geo']): place the outline by
    # them and skip the basemap matching. Still Approximate (R-G9); the size and pin checks below still run.
    if GEO.get("affine") and _A is not None:
        proj = LocalProj(lat, lon)
        acres = _acres_row

        def mdl(pts, _w=w, _h=h, _A=_A, _proj=proj):
            pts = np.asarray(pts, float)
            u, v = pts[:, 0] / _w, pts[:, 1] / _h
            xm, ym = _proj.to_m(_A[0] * u + _A[1] * v + _A[2], _A[3] * u + _A[4] * v + _A[5])
            return np.c_[xm, ym]
        best, real_score, decoy_score, n = {"pairs": []}, 0.0, 0.0, 0
        P = np.zeros((0, 2)); Q = np.zeros((0, 2))
        bm = {"sources": [GEO.get("how") or "GeoPDF"], "lines": []}
        res.update(model="GeoPDF", fit_m=GEO.get("fit_err_m", ""), n_points=0)
        flags.append(f"placed by the map's own coordinates ({GEO.get('how') or 'GeoPDF'}), no basemap matching")
    else:
        # ---- step 2a: picture control-point candidates
        allp = np.vstack(bnd.get("parcels") or [bpts])
        bx, by, bw, bh = cv2.boundingRect(np.round(allp).astype(np.int32))
        roi = (bx - 1.0 * bw, by - 1.0 * bh, bx + 2.0 * bw, by + 2.0 * bh) if bnd["kind"] == "area" else None
        if row.get("roi_px"):
            roi = tuple(row["roi_px"])
        boxes_ex = TM.junction_exclusions(img, allp) if (BOX_MASK and TM is not None) else None
        P, wts, segs = detect_junctions(img, max_points=args.max_img_points, exclude=row.get("exclude_px"), roi=roi, box_exclude=boxes_ex)
        if boxes_ex:
            flags.append(f"junctions in {len(boxes_ex)} legend / title / inset / icon box(es) not used")
        log(f"   picture junction candidates: {len(P)} (from {len(segs)} LSD segments)")

        # ---- step 2b: government basemap
        proj = LocalProj(lat, lon)
        acres = float(row["acres"]) if row.get("acres") not in (None, "") else None
        half_km = args.box_km / 2.0
        if acres:
            half_km = max(half_km, 1.5 * math.sqrt(acres * 4046.86) / 1000.0)
        bm = fetch_basemap(http, ref, lat, lon, half_km, base / "cache", use_cache=not args.refresh,
                           offline=bool(getattr(args, "offline", False)))
        for _sk in bm.get("skipped") or []:
            flags.append(f"{_sk} source skipped (robots): partial basemap, matched on the allowed sources only")
        if not bm["points"]:
            res.update(status="NO FIT", why="no basemap control points: " + "; ".join(bm["sources"] or ["every basemap source was skipped (robots)"])
                       + (("; " + "; ".join(flags)) if flags else ""),
                       flags="; ".join(flags))
            if stale.exists():
                stale.unlink()
            return res
        pts_ll = np.array([[p[1], p[2]] for p in bm["points"]])
        ex, ny = proj.to_m(pts_ll[:, 0], pts_ll[:, 1])
        Q = np.c_[ex, ny]
        # merge near-duplicates, keep the closest to the pin
        order = np.argsort(np.hypot(Q[:, 0], Q[:, 1]))
        kept = []
        for o in order:
            if all(np.hypot(*(Q[o] - Q[k])) > 10 for k in kept[-400:]):
                kept.append(o)
            if len(kept) >= args.max_geo_points:
                break
        Q = Q[kept]
        log(f"   basemap control-point candidates: {len(Q)} ({'; '.join(bm['sources'])})")

        # ---- priors
        area_px = cv2.contourArea(np.round(bpts).astype(np.float32).reshape(-1, 1, 2)) if bnd["kind"] == "area" else 0
        if acres and area_px > 0:
            s0 = math.sqrt(acres * 4046.86 / area_px)
            smin, smax = s0 / 2.5, s0 * 2.5
        else:
            smin = args.min_m_per_px
            smax = min(args.max_m_per_px, 4.0 * half_km * 1000.0 / max(bw, bh, 1))
        padx = max(0.25 * bw, 50)
        pady = max(0.25 * bh, 50)
        prior = Prior(smin, smax, args.rot_max, (bx - padx, by - pady, bx + bw + padx, by + bh + pady))
        c_img = np.array([w / 2.0, h / 2.0])
        # search radius = 8 picture px at the hypothesised scale (20..75 m); final
        # correspondences are then re-collected at a fixed 75 m so fit_m is not capped
        # below the 50 m gate by construction.
        cap = args.match_tol_m
        prior_search = prior
        # Nov 11: line agreement - the basemap's road and water lines (metres) against the picture's own line segments in the search box
        line_ev, LS = None, np.zeros((0, 2))
        if LE is not None and LINE_WEIGHT > 0:
            lm = []
            for kind_, ln in bm.get("lines") or []:
                if kind_ in LE.LINE_KINDS and len(ln) >= 2:
                    ll = np.array(ln, float); xm, ym = proj.to_m(ll[:, 0], ll[:, 1]); lm.append(np.c_[xm, ym])
            lm = LE.clip_lines(lm, 1.2 * half_km * 1000.0)   # a big lake / long river: only its part in the search box
            if lm:
                step = max(1.0, smin * LE.CELL_PX / 2.0)
                LS = LE.sample_lines(lm, step)
                if len(LS) > 400000:   # a very dense box: coarser samples (still under one per cell at the largest scale)
                    LS = LE.sample_lines(lm, step * len(LS) / 400000.0)
                line_ev = LE.LineEvidence(img.shape, segs, roi=roi, exclude=row.get("exclude_px"))

        def _line_fn(samples):
            return (lambda z_, t_: line_ev.score(z_, t_, samples)) if line_ev is not None and len(samples) else None
        best = match(P, Q, c_img, prior, cap, line=_line_fn(LS))
        tol_m = best["tol"] if best else search_tol(math.sqrt(smin * smax), cap)
        res["search_tol_m"] = round(tol_m, 1)
        # decoy test: same matcher against the basemap rotated 90/180/270 deg about the pin
        decoy_best, decoy_score, decoy_lz = 0, 0.0, 0.0
        for ang in (90, 180, 270):   # Nov 11: the decoy's lines are rotated with its points, so a decoy gets the same line credit a real fit would
            rot = np.exp(1j * math.radians(ang)) * (Q[:, 0] + 1j * Q[:, 1])
            d = match(P, np.c_[rot.real, rot.imag], c_img, prior_search, cap,
                      line=_line_fn(LE.rotate(LS, ang) if len(LS) else LS))
            if d and d["score"] > decoy_score:
                decoy_best, decoy_score, decoy_lz = d["n"], d["score"], d.get("line_z", 0.0)
        res["decoy_best"] = f"{decoy_best} (score {decoy_score:.1f})"
        res["n_search"] = f"{best['n']} (score {best['score']:.1f}, chance {best['chance']:.1f})" if best else 0
        real_score = best["score"] if best else 0.0
        if line_ev is not None:
            res.update(line_share=round(best["line_share"], 3) if best else "", line_z=round(best["line_z"], 1) if best else "",
                       decoy_line_z=round(decoy_lz, 1), score_points=round(best["score_points"], 1) if best else "")

        # ---- debug image 2: picture candidates, inliers and basemap drawn back on the picture
        im2 = img.copy()
        for (x, y) in P:
            cv2.circle(im2, (int(x), int(y)), 6, (255, 200, 0), 2)
        mdl = None
        n_search = best["n"] if best else 0
        if best is not None and best["n"] >= 2:
            # re-collect correspondences at the fixed final radius under the found transform
            tree = KDTree(Q)
            mm = best["z"] * _cplx_img(P) + best["t"]
            dist, idx = tree.query(np.c_[mm.real, mm.imag], k=1)
            sel = {}
            for i in np.nonzero(dist[:, 0] < args.match_tol_m)[0]:
                j = idx[i, 0]
                if j not in sel or dist[i, 0] < dist[sel[j], 0]:
                    sel[j] = i
            best["pairs"] = sorted((i, j) for j, i in sel.items())
            pi = np.array([a for a, _ in best["pairs"]])
            qj = np.array([b for _, b in best["pairs"]])
            Pin, Qin = P[pi], Q[qj]
            n = len(pi)
            res["n_points"] = n
            if n >= MIN_POINTS:
                kind, mdl, rms, loo, resid, collinear = choose_model(Pin, Qin)
                res.update(fit_m=round(rms, 1), fit_loo_m=("" if math.isnan(loo) else round(loo, 1)), model=kind)
                if collinear:
                    flags.append("control points nearly collinear")
            else:
                mdl = Model("similarity", Pin, Qin)
            inv = invert_model(mdl, w, h)
            for kind_, ln in bm["lines"]:
                ll = np.array(ln, float)
                if len(ll) < 2:
                    continue
                xm, ym = proj.to_m(ll[:, 0], ll[:, 1])
                pix = inv(np.c_[xm, ym])
                col = {"road": (0, 0, 255), "stream": (255, 0, 0), "water": (255, 0, 0), "shore": (255, 120, 0), "plss": (0, 160, 0)}.get(kind_, (0, 0, 255))
                draw_poly(im2, pix, col, 1, closed=False)
            for k, (a, b) in enumerate(best["pairs"]):
                x, y = P[a]
                cv2.circle(im2, (int(x), int(y)), 11, (0, 200, 0), 3)
                gx, gy = inv(Q[b:b + 1])[0]
                cv2.line(im2, (int(x), int(y)), (int(gx), int(gy)), (0, 140, 255), 2)
                cv2.putText(im2, str(k + 1), (int(x) + 12, int(y) - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 120, 0), 2)
            pin_px = inv(np.array([[0.0, 0.0]]))[0]
            cv2.drawMarker(im2, (int(pin_px[0]), int(pin_px[1])), (0, 0, 0), cv2.MARKER_STAR, 30, 3)

        # ---- step 3: gate (hard rules + match significance)
        n = int(res["n_points"] or 0)
        why = []
        if best is None or n < MIN_POINTS:
            why.append(f"only {n} control point(s) matched (need >= {MIN_POINTS})")
        else:
            if not (res["fit_m"] < MAX_FIT_M):
                why.append(f"RMS fit {res['fit_m']} m is not under {MAX_FIT_M:.0f} m")
            if res["fit_loo_m"] != "" and not (res["fit_loo_m"] < MAX_FIT_M):
                why.append(f"leave-one-out RMS {res['fit_loo_m']} m is not under {MAX_FIT_M:.0f} m")
            if real_score < max(CHANCE_RATIO * decoy_score, decoy_score + CHANCE_MARGIN):   # Nov 2: tunable, today 1.5 / 2.0
                why.append(f"match not better than chance ({n_search} points, score {real_score:.1f} vs "
                           f"{decoy_best} points, score {decoy_score:.1f} on a rotated decoy basemap)")
            if best is not None and best.get("line_n", 0) >= (LE.MIN_SAMPLES if LE else 1) and best.get("line_z", 0.0) < LINE_MIN_Z:
                why.append(f"the basemap's roads and water do not sit on the picture's lines (line z {best['line_z']:.1f}, "
                           f"{100 * best['line_share']:.0f}% on a line; need z >= {LINE_MIN_Z:.0f})")
        status = "NO FIT" if why else "DRAWN"
        put(im2, f"{ref} {status}: n={n} fit_m={res['fit_m']} loo={res['fit_loo_m']} score={real_score:.1f} decoy={decoy_score:.1f}", 30,
            (0, 120, 0) if status == "DRAWN" else (0, 0, 255))
        put(im2, "cyan=picture candidates  green=matched  red=TIGER roads  blue=water / shores (back-projected)", 60)
        _dbg_write(dbg / f"{sref}_2_controlpoints.jpg", im2)
        if why:
            res.update(status="NO FIT", why="; ".join(why), flags="; ".join(flags))
            if stale.exists():
                stale.unlink()
            return res

    # ---- step 4: transform, simplify 3 m, valid geometry
    M = mdl(bpts)
    merged = None
    if bnd["kind"] == "area" and len(bnd.get("parcels") or []) > 1:
        # several closed shapes in the park colour (multi-unit WMA maps, a park split by photo
        # boxes or symbols, neighbouring parks): keep the one containing / nearest the POTA pin,
        # plus any shape within 50 m of the kept ones (same park split on the picture).
        polys = [Polygon(mdl(pp)) for pp in bnd["parcels"]]
        polys = [g if g.is_valid else make_valid(g) for g in polys]
        k_best = min(range(len(polys)), key=lambda i: polys[i].distance(Point(0, 0)))
        keep = {k_best}
        grown = True
        while grown:
            grown = False
            cur = unary_union([polys[i] for i in keep])
            for i in range(len(polys)):
                if i not in keep and polys[i].distance(cur) <= MAX_FIT_M:
                    keep.add(i)
                    grown = True
        # Nov 7: a gap wider than the 50 m adjacency is only bridged on evidence (an official size the joined pieces land inside);
        # otherwise the further shapes are LISTED for a person, never silently absorbed or silently dropped.
        n_adj = len(keep)
        extra_txt = ''
        if TL is not None:
            _acres_of = lambda i: polys[i].area / 4046.86
            _cur = unary_union([polys[i] for i in keep])
            cands = [(i, polys[i].distance(_cur), _acres_of(i)) for i in range(len(polys)) if i not in keep]
            add, extra_txt = TL.stitch_extra(sum(_acres_of(i) for i in keep), cands,
                                             float(row["acres"]) if row.get("acres") not in (None, "") else None)
            keep.update(add)
        merged = unary_union([polys[i] for i in keep])
        merged = merged.buffer(0)
        flags.append(f"picture shows {len(polys)} shapes in the boundary colour; kept {len(keep)} "
                     f"({'containing' if polys[k_best].distance(Point(0, 0)) == 0 else 'nearest'} the POTA pin"
                     f"{f' + {n_adj - 1} adjacent piece(s) within 50 m' if n_adj > 1 else ''})"
                     + (f"; {extra_txt}" if extra_txt else " - check this is the whole park"))
    if merged is not None:
        geom = merged.simplify(SIMPLIFY_M, preserve_topology=True)
        if not geom.is_valid:
            geom = make_valid(geom)
    elif bnd["kind"] == "area":
        geom = Polygon(M)
        if not geom.is_valid:
            flags.append("traced outline self-intersected; repaired with make_valid")
            geom = make_valid(geom)
            if geom.geom_type not in ("Polygon", "MultiPolygon"):
                polys = [g for g in getattr(geom, "geoms", []) if g.geom_type in ("Polygon", "MultiPolygon")]
                geom = max(polys, key=lambda g: g.area) if polys else geom
        geom = geom.simplify(SIMPLIFY_M, preserve_topology=True)
        if not geom.is_valid:
            geom = make_valid(geom)
    else:
        geom = LineString(M).simplify(SIMPLIFY_M, preserve_topology=True)
        if not geom.is_simple:
            flags.append("route line self-crosses")

    # ---- step 5: sanity checks. Nov 7: pin outside, clipped at the picture edge, an implausible GeoPDF placement and an oversize trace are
    # HELD as NEEDS A PERSON (no outline written), not just flagged. The pin is never moved. Reasons come from kpc_trace_limits.hold_reasons.
    pin = Point(0, 0)
    dpin = geom.distance(pin)
    if dpin > PIN_MAX_OUTSIDE_M:
        flags.append(f"POTA pin is {dpin:.0f} m outside the traced {'outline' if bnd['kind'] == 'area' else 'line'}")
    area_acres = None
    acres_held = None
    edge_sh = None
    if bnd["kind"] == "area":
        area_acres = geom.area / 4046.86
    if TL is not None:
        if bnd["kind"] == "area" and bnd.get("touches_edge"):
            edge_sh = TL.edge_share(bpts, w, h)
        page_share = None
        if area_acres is not None and geo_info.get("page_km2"):
            page_share = (area_acres * 4046.86 / 1e6) / geo_info["page_km2"]
        held_why = TL.hold_reasons(kind=bnd["kind"], geopdf_why=geo_why, pin_dist_m=dpin, pin_max_m=PIN_MAX_OUTSIDE_M, edge=edge_sh,
                                   traced_acres=area_acres, known_acres=acres, park_type=row.get("type"), page_share=page_share,
                                   length_km=(geom.length / 1000.0 if bnd["kind"] != "area" else None), geopdf_residual_ok=geo_resid_ok)
        res.update(geo_m_per_px=round(geo_info["m_per_px_x"], 3) if geo_info.get("m_per_px_x") else "",
                   geo_page_km2=round(geo_info["page_km2"], 1) if geo_info.get("page_km2") else "",
                   geo_lat_down=("yes" if geo_info.get("lat_down") else "no") if geo_info else "",
                   pin_px=f"{pin_px[0]:.0f},{pin_px[1]:.0f}" if pin_px is not None else "")
        res.update(acres_traced=round(area_acres, 1) if area_acres is not None else "", acres_known=acres if acres else "",
                   ceiling_acres=int(TL.ceiling_acres(row.get("type"))), edge_share=round(edge_sh, 3) if edge_sh is not None else "",
                   pin_dist_m=round(dpin))
        if held_why:
            acres_held = "; ".join(held_why)
            flags.extend(x for x in held_why if x not in flags)
    elif bnd["kind"] == "area" and acres and not (AREA_RATIO_RANGE[0] * acres <= area_acres <= AREA_RATIO_RANGE[1] * acres):
        # kpc_trace_limits.py missing: keep the Nov 6 behaviour (hold back when known acres disagree)
        acres_held = (f"traced area {area_acres:.0f} ac vs known {acres:.0f} ac outside "
                      f"{AREA_RATIO_RANGE[0]:g}x-{AREA_RATIO_RANGE[1]:g}x")
        flags.append(acres_held)
    if not geom.is_valid:
        flags.append("geometry still invalid")

    if acres_held:
        if stale.exists():
            stale.unlink()
        res.update(status="NEEDS A PERSON", why=acres_held, flags="; ".join(flags),
                   fit_m=res.get("fit_m", ""), n_points=res.get("n_points", 0))
        return res

    # ---- step 6: output
    geom_ll = shapely.transform(geom, lambda xy: np.column_stack(proj.to_ll(xy[:, 0], xy[:, 1])))
    cps = []
    for (a, b) in best["pairs"]:
        lo, la = proj.to_ll(Q[b, 0], Q[b, 1])
        cps.append(dict(px=[round(float(P[a, 0]), 1), round(float(P[a, 1]), 1)],
                        lon=round(float(lo), 7), lat=round(float(la), 7)))
    unoff = source_type(row) == "unofficial"
    props = dict(ref=ref, name=row.get("name"), agency=row.get("agency"),
                 grade=GRADE_UNOFFICIAL if unoff else GRADE,
                 status=STATUS_UNOFFICIAL if unoff else "DRAWN", source_type=source_type(row),
                 match_score=round(real_score, 1), decoy_score=round(decoy_score, 1),
                 fit_m=res["fit_m"], fit_loo_m=res["fit_loo_m"] if res["fit_loo_m"] != "" else None,
                 n_points=n, method=(f"{'boundary' if bnd['kind'] == 'area' else 'route'} by Lab k-means ({bnd['mask_name']}); placed by "
                                     f"{GEO.get('how')}; Douglas-Peucker {SIMPLIFY_M:g} m") if GEO.get("affine") else (f"{'boundary' if bnd['kind'] == 'area' else 'route'} by Lab k-means "
                                     f"({bnd['mask_name']}); control points: LSD junctions matched to "
                                     f"government basemap junctions (Hough-voted similarity + ICP); "
                                     f"{res['model']} fit; Douglas-Peucker {SIMPLIFY_M:g} m"),
                 model=res["model"], source_url=row.get("source_url"), page=row.get("page"),
                 basemap_sources=bm["sources"], date=res["date"],
                 area_acres=round(area_acres, 1) if area_acres else None,
                 flags=flags, use_for_2fer=False, official=False,
                 control_points=cps, tool=f"kpc_trace_picture.py {__version__}")
    if unoff:   # R-G9U record: who published it and why nothing official was used
        props.update(source_org=row.get("source_org"), notes=row.get("notes"),
                     replace_when="replace as soon as an official GIS layer, agency parcel or agency map is found")
    fc = dict(type="FeatureCollection",
              features=[dict(type="Feature", properties=props, geometry=_round_geojson(mapping(geom_ll)))])
    atomic_write(out / f"{sref}.json", json.dumps(fc, indent=1))
    _ok_why = ("fit under 50 m with >= 3 control points" if not (GEO.get("affine") and TL is not None) else
               f"placed by the map's own georeference (residual {res.get('fit_m')} m, "
               f"{geo_info.get('m_per_px_x', 0):.2f} m/px); checked: pin on page, scale plausible, size within the limit for the park type")
    res.update(status=STATUS_UNOFFICIAL if unoff else "DRAWN", why=_ok_why + (("; " + "; ".join(flags)) if flags else ""),
               flags="; ".join(flags))
    return res


def _round_geojson(g):
    def r(c):
        if isinstance(c, (list, tuple)) and c and isinstance(c[0], (int, float)):
            return [round(c[0], 7), round(c[1], 7)]
        return [r(x) for x in c]
    return dict(type=g["type"], coordinates=r(g["coordinates"]))



def _http_selftest() -> list:
    """Nov 7: robots 401/403/5xx/no answer = STOP with no data request; Disallow on REST obeyed; no redirects."""
    problems = []

    class _R:
        def __init__(self, st, text="", hd=None):
            self.status_code, self.text, self.headers = st, text, hd or {}

        def raise_for_status(self):
            if self.status_code >= 400:
                raise requests.HTTPError(str(self.status_code))

        def json(self):
            return {"features": []}

    def make(robots_answer, data_answer=None):
        h = PoliteHttp("KPC-Picture-Map-Tracer/test", min_interval=0, retries=0)
        h.calls = []

        def fake_get(url, params=None, timeout=None, allow_redirects=True, headers=None):
            h.calls.append((url, allow_redirects))
            if url.endswith("/robots.txt"):
                if isinstance(robots_answer, Exception):
                    raise robots_answer
                return robots_answer
            return data_answer or _R(200)
        h.s.get = fake_get
        return h

    url = TIGER + "/8/query"
    for ans in (_R(401), _R(403), _R(500), _R(429), requests.ConnectionError("x")):
        h = make(ans)
        try:
            h.get_json(url, {})
            problems.append(f"robots {getattr(ans, 'status_code', ans)} must STOP the basemap read")
        except RuntimeError as e:
            if not str(e).startswith("robots:") or len(h.calls) != 1:
                problems.append(f"robots STOP must make no data request: {e} {h.calls}")
    h = make(_R(200, "User-agent: *\nDisallow: /arcgis/rest/\n"))
    try:
        h.get_json(url, {})
        problems.append("a robots Disallow on an ArcGIS REST path must be obeyed")
    except RuntimeError as e:
        if len(h.calls) != 1:
            problems.append(f"robots Disallow must make no data request: {h.calls}")
    h = make(_R(200, "User-agent: kpc-picture-map-tracer\nDisallow: /\n\nUser-agent: *\nAllow: /\n"))
    try:
        h.get_json(url, {})
        problems.append("our own robots group must win over '*'")
    except RuntimeError:
        pass
    h = make(_R(404))
    if h.get_json(url, {}) != {"features": []} or len(h.calls) != 2:
        problems.append(f"robots 404 = no robots file, the read must go ahead: {h.calls}")
    # a robots.txt redirect: followed within the allowed hosts, a STOP when it leads outside them
    seq = {}

    def make_redirect(target):
        h = PoliteHttp("KPC-Picture-Map-Tracer/test", min_interval=0, retries=0)
        h.calls = []

        def fake_get(u, params=None, timeout=None, allow_redirects=True, headers=None):
            h.calls.append(u)
            if u == "https://tigerweb.geo.census.gov/robots.txt":
                return _R(301, hd={"Location": target})
            if u.endswith("/robots.txt"):
                return _R(404)
            return _R(200)
        h.s.get = fake_get
        return h
    h = make_redirect("https://hydro.nationalmap.gov/robots.txt")
    if h.get_json(url, {}) != {"features": []} or len(h.calls) != 3:
        problems.append(f"a robots.txt redirect within the allowed hosts must be followed: {h.calls}")
    h = make_redirect("https://www.example.com/robots.txt")
    try:
        h.get_json(url, {})
        problems.append("a robots.txt redirect to a host outside the allowed list must STOP")
    except RuntimeError as e:
        if not str(e).startswith("robots:") or any("example.com" in c for c in h.calls):
            problems.append(f"the outside host must not be requested: {e} {h.calls}")
    h = make(_R(404), _R(302, hd={"Location": "https://ncnhde.natureserve.org/x"}))
    try:
        h.get_json(url, {})
        problems.append("a redirect must not be followed")
    except RuntimeError as e:
        if "redirect" not in str(e) or any(a for _, a in h.calls) or len(h.calls) != 2:
            problems.append(f"redirects must be refused with allow_redirects=False: {e} {h.calls}")
    return problems


def picture_selftest():
    """Offline checks for Nov 6 acres gate (no network)."""
    problems = []
    if TL is None:
        problems.append('kpc_trace_limits.py must import')
    else:
        if TL.acres_in_range(134.9, 229.85) is not True:
            problems.append('Salato-sized trace must pass the acres gate')
        if TL.acres_in_range(25895525.4, 5000) is not False:
            problems.append('US-5460-sized wild GeoPDF must fail the acres gate')
        if not (AREA_RATIO_RANGE == (TL.PICTURE_ACRES_LO, TL.PICTURE_ACRES_HI) or AREA_RATIO_RANGE == (0.2, 5.0)):
            problems.append('AREA_RATIO_RANGE must stay 0.2..5')
    problems += _http_selftest()
    if LE is None:
        problems.append('kpc_trace_edges.py must import')
    elif LE.selftest() != 0:
        problems.append('kpc_trace_edges.py selftest failed')
    if TL is not None:      # Nov 7 gates (kpc_trace_limits.hold_reasons): a GeoPDF residual / pin outside / clipped / oversize trace is held
        if not TL.hold_reasons(geopdf_why=["geopdf residual: 6580 m is over 100 m"], traced_acres=10, park_type="State Park"):
            problems.append("a bad GeoPDF residual must be held as NEEDS A PERSON")
        if not TL.hold_reasons(pin_dist_m=27555, traced_acres=142, park_type="State Park"):
            problems.append("a pin 27 km outside the trace must be held")
        if not TL.hold_reasons(edge=0.4, traced_acres=100, park_type="State Park"):
            problems.append("a trace running along the picture edge must be held")
        if not TL.hold_reasons(traced_acres=25895525.4, park_type="State Forest"):
            problems.append("a 25.9 M ac trace with no known acres must be held by the ceiling (US-5460)")
        if TL.hold_reasons(geopdf_why=[], pin_dist_m=0, edge=None, traced_acres=314.6, park_type="Nature Reserve"):
            problems.append("a valid GeoPDF-sized trace (CA-1248) must not be held")
    src = Path(__file__).read_text(encoding='utf-8')
    # Nov 7 pin mode: the pin's pixel from a page affine, and the switch
    _A = [0.01, 0.0, -100.0, 0.0, -0.008, 40.0]      # u -> lon, v -> lat over a small page
    _p = _pin_px_from_affine(_A, 1000, 800, 40.0 - 0.004, -100.0 + 0.005)
    if _p is None or abs(_p[0] - 500) > 1 or abs(_p[1] - 400) > 1:
        problems.append(f"the pin pixel from a page affine is wrong: {_p}")
    if _pin_px_from_affine([0, 0, 0, 0, 0, 0], 100, 100, 1, 1) is not None:
        problems.append("a degenerate affine must give no pin pixel")
    if ("pin_px=" + "pin_px") not in src:      # written in two pieces so this check cannot match itself
        problems.append("process_one must pass the pin pixel to detect_boundary (Nov 7 pin mode)")
    if 'hold_reasons' not in src or 'geopdf_plausible' not in src:
        problems.append('process_one must call TL.geopdf_plausible and TL.hold_reasons (Nov 7 gates)')
    if 'NEEDS A PERSON' not in src or 'acres_held' not in src:
        problems.append('process_one must hold back as NEEDS A PERSON when acres are outside 0.2x-5x')
    problems += _offline_selftest()
    for p_ in problems:
        print(p_)
    print('PASS' if not problems else 'FAIL')
    return 0 if not problems else 1


def _offline_selftest():
    """Nov 11 (--offline): the cached basemap is the only source; no web request of any kind; a missing basemap is an 'offline:' error."""
    import tempfile
    problems = []

    class _Http:
        calls = []

        def get_json(self, url, params):
            self.calls.append(url)
            raise RuntimeError("test: a web request was asked for")      # stops fetch_basemap at its first request
    with tempfile.TemporaryDirectory() as td:
        cdir = Path(td)
        h = _Http()
        try:
            fetch_basemap(h, "US-0001", 38.0, -85.0, 5.0, cdir, use_cache=True, offline=True)
            problems.append("--offline with no cached basemap must raise")
        except RuntimeError as e:
            if not str(e).startswith("offline:"):
                problems.append(f"--offline with no cached basemap must say offline: ({e})")
        part = dict(ref="US-0001", version=__version__, pin=[38.0, -85.0], half_km=5.0, skipped=["water"], sources=["roads"],
                    lines=[], points=[["road", -85.0, 38.0]])
        (cdir / "US-0001_basemap.json").write_text(json.dumps(part))
        got = fetch_basemap(h, "US-0001", 38.0, -85.0, 5.0, cdir, use_cache=True, offline=True)
        if got.get("skipped") != ["water"] or got.get("points") != part["points"]:
            problems.append("--offline must use a partial cached basemap as it is (skipped list kept for the flags)")
        for args_ in (dict(lat=38.0, half_km=5.0), dict(lat=38.5, half_km=5.0), dict(lat=38.0, half_km=7.0)):
            try:
                fetch_basemap(h, "US-0001", args_["lat"], -85.0, args_["half_km"], cdir, use_cache=True, offline=True)
                if args_ != dict(lat=38.0, half_km=5.0):
                    problems.append(f"--offline must refuse a cached basemap for another box {args_}")
            except RuntimeError as e:
                if args_ == dict(lat=38.0, half_km=5.0) or not str(e).startswith("offline:"):
                    problems.append(f"--offline cache check wrong for {args_}: {e}")
        if h.calls:
            problems.append(f"--offline made a web request: {h.calls}")
        # a normal run still never reuses a partial basemap (owner call, Nov 7): it asks the web again
        try:
            fetch_basemap(h, "US-0001", 38.0, -85.0, 5.0, cdir, use_cache=True, offline=False)
        except RuntimeError:
            pass
        if not h.calls:
            problems.append("a normal run must not reuse a partial cached basemap (it must ask again)")
    return problems


# ================================================================ main
def main(argv=None):
    global HONOR_IMAGE, CHANCE_RATIO, CHANCE_MARGIN   # Nov 2 review: set from the flags below
    argv = list(sys.argv[1:] if argv is None else argv)
    if '--selftest' in argv:
        return picture_selftest()
    if '--list-hosts' in argv:      # Nov 11: no request of any kind; reads index.json, pins.json and cache/ only
        b = argv[argv.index('--base') + 1] if '--base' in argv and argv.index('--base') + 1 < len(argv) else '.'
        return TH.main([b] + (['--offline'] if '--offline' in argv else []))
    ap = argparse.ArgumentParser(description="KPC Picture-Map Tracer (approximate outlines from agency picture maps)")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--refs", nargs="+", help="park references to process, e.g. US-10172")
    g.add_argument("--all", action="store_true", help="process every ref in index.json")
    ap.add_argument("--base", default=".", help="folder holding maps/, index.json, pins.json")
    ap.add_argument("--out", default=None, help="output folder (default <base>/traced)")
    ap.add_argument("--out-unofficial", default=None,
                    help="output folder for R-G9U unofficial maps (default <base>/traced_unofficial)")
    ap.add_argument("--resume", action="store_true", help="with --all: skip refs already in report.csv")
    ap.add_argument("--time-budget-min", type=float, default=50.0,
                    help="stop starting new maps after this many minutes (GitHub Actions ~55 min)")
    ap.add_argument("--max-maps", type=int, default=0, help="process at most N maps this run (0 = no limit)")
    ap.add_argument("--refresh", action="store_true", help="ignore cached basemap downloads")
    ap.add_argument("--offline", action="store_true",
                    help="no web request at all: basemaps only from <base>/cache (a before / after replay on the same saved basemaps); "
                         "a map with no cached basemap is an ERROR row. GeoPDF maps need no basemap")
    ap.add_argument("--min-interval", type=float, default=1.0, help="seconds between web requests")
    ap.add_argument("--box-km", type=float, default=10.0, help="basemap box size around the pin (km)")
    ap.add_argument("--k", type=int, default=8, help="k-means colour clusters")
    ap.add_argument("--rot-max", type=float, default=25.0, help="max map rotation from north-up (deg)")
    ap.add_argument("--min-m-per-px", type=float, default=0.2)
    ap.add_argument("--max-m-per-px", type=float, default=25.0)
    ap.add_argument("--match-tol-m", type=float, default=75.0,
                    help="correspondence search radius; the 50 m RMS gate is applied afterwards")
    ap.add_argument("--max-img-points", type=int, default=70)
    ap.add_argument("--max-geo-points", type=int, default=300)
    # Nov 2 review: tracer limits (defaults = today, see kpc_trace_limits.py)
    ap.add_argument("--acres-file", default=(TL.setting("KPC_TRACE_ACRES_FILE") if TL else "") or None,
                    help="official acres list for rows with no acres (sets the scale prior); default none")
    ap.add_argument("--chance-ratio", type=float, default=CHANCE_RATIO, help="better-than-chance gate: real >= ratio x decoy")
    ap.add_argument("--chance-margin", type=float, default=CHANCE_MARGIN, help="better-than-chance gate: real >= decoy + margin")
    ap.add_argument("--no-honor-image", action="store_true", help="old behaviour: take the first <ref>_*.jpg, not the chosen image")
    ap.add_argument("--off", default="", help="matcher-input switches to turn off, comma list: " + ", ".join(SWITCHES) +
                    " (each is also an environment variable, e.g. KPC_TRACE_BAND_JUNCTIONS=0); 'all' = every one (the earlier inputs)")
    ap.add_argument("--list-hosts", action="store_true", help="print every host a run on --base would contact, and stop (no request)")
    args = ap.parse_args(argv)
    CHANCE_RATIO, CHANCE_MARGIN = args.chance_ratio, args.chance_margin
    if args.no_honor_image: HONOR_IMAGE = False
    offs = [x.strip() for x in str(args.off or "").split(",") if x.strip()]
    if offs == ["all"]:
        offs = list(SWITCHES)
    bad_off = [x for x in offs if x not in SWITCHES]
    if bad_off:
        print(f"--off: unknown switch(es) {bad_off}; known: {', '.join(SWITCHES)}", file=sys.stderr)
        return 2
    for x in offs:
        globals()[x.upper()] = False
    log("matcher inputs: " + ", ".join(f"{k} {'on' if globals()[k.upper()] else 'OFF'}" for k in SWITCHES))

    base = Path(args.base)
    out = Path(args.out) if args.out else base / "traced"
    out_unoff = Path(args.out_unofficial) if args.out_unofficial else base / "traced_unofficial"
    out.mkdir(parents=True, exist_ok=True)
    try:
        index = load_index(base)
        pins = json.loads((base / "pins.json").read_text())
    except Exception as e:
        print(f"cannot read index.json / pins.json: {e}", file=sys.stderr)
        return 2
    if args.acres_file and TL is not None:
        n_ac = TL.fill_acres(index, TL.load_acres(args.acres_file))
        log(f"official acres filled in for {n_ac} map row(s) from {args.acres_file}")
    ua = os.environ.get("KPC_TRACER_UA") or DEFAULT_UA
    http = PoliteHttp(ua, min_interval=args.min_interval)
    if args.offline:
        if args.refresh:
            print("--offline and --refresh cannot go together (--refresh asks the web again)", file=sys.stderr)
            return 2

        def _offline(*a, **k):
            raise RuntimeError("offline: no web request is made with --offline")
        http.s.get = _offline          # every request path of PoliteHttp goes through s.get
        log("offline: no web request; basemaps from " + str(base / "cache"))
    report_path = out / "report.csv"
    report = read_report(report_path)
    report_u_path = out_unoff / "report.csv"          # R-G9U: unofficial results kept separately
    report_u = read_report(report_u_path)

    refs = sorted(index) if args.all else list(args.refs)
    if args.all and args.resume:
        refs = [r for r in refs if r not in report and r not in report_u]
    t0 = time.time()
    done, durations = 0, []
    for ref in refs:
        elapsed = time.time() - t0
        est = (sum(durations) / len(durations)) if durations else 90.0
        if elapsed + est > args.time_budget_min * 60:
            log(f"time budget reached after {done} map(s); {len(refs) - done} left for the next run (--resume)")
            break
        if args.max_maps and done >= args.max_maps:
            log(f"--max-maps {args.max_maps} reached; {len(refs) - done} left")
            break
        ts = time.time()
        log(f"== {ref}")
        row, skipped = select_row(index.get(ref))
        unoff = source_type(row) == "unofficial"
        o_dir, o_rep, o_path = (out_unoff, report_u, report_u_path) if unoff else (out, report, report_path)
        o_dir.mkdir(parents=True, exist_ok=True)
        if unoff:
            log(f"   unofficial map (R-G9U last resort): {row.get('source_org')}")
        if skipped:
            # an official map exists: the unofficial one is not used, and any earlier unofficial
            # outline for this park is withdrawn (R-G9U: replaced as soon as anything official is found)
            old = out_unoff / f"{safe_name(ref)}.json"
            if old.exists():
                old.unlink()
            sk = skipped[0]
            report_u[ref] = dict(ref=ref, status="SKIPPED", n_points=0,
                                 why="official agency map row exists; unofficial map not used (R-G9U)",
                                 source_url=sk.get("source_url", ""), page=sk.get("page", ""),
                                 date=_dt.date.today().isoformat(), source_type="unofficial",
                                 source_org=sk.get("source_org", ""), notes=sk.get("notes", ""))
            out_unoff.mkdir(parents=True, exist_ok=True)
            write_report(report_u_path, report_u)
            log(f"   unofficial row(s) skipped: official map row exists")
        try:
            res = process_one(ref, row, base, o_dir, pins, http, args)
        except Exception as e:  # one failure never stops the batch
            traceback.print_exc()
            r0 = row or {}
            res = dict(ref=ref, status="ERROR", why=f"{type(e).__name__}: {e}"[:300],
                       source_url=r0.get("source_url", ""), page=r0.get("page", ""),
                       date=_dt.date.today().isoformat(), source_type=source_type(r0) if row else "",
                       source_org=r0.get("source_org", ""), notes=r0.get("notes", ""))
        if not unoff:   # official map exists -> never keep an unofficial outline (R-G9U)
            old = out_unoff / f"{safe_name(ref)}.json"
            if old.exists():
                old.unlink()
        o_rep[ref] = res
        write_report(o_path, o_rep)        # save after each map
        # a park lives in one report only: drop it from the other one
        other_rep, other_path = (report, report_path) if unoff else (report_u, report_u_path)
        if ref in other_rep and not (not unoff and skipped):
            del other_rep[ref]
            write_report(other_path, other_rep)
        durations.append(time.time() - ts)
        done += 1
        log(f"   -> {res['status']} fit_m={res.get('fit_m', '')} n={res.get('n_points', '')} "
            f"decoy={res.get('decoy_best', '')} | {res.get('why', '')} ({durations[-1]:.0f}s)")
    log(f"done {done} map(s), {http.n_requests} web request(s); reports: {report_path}"
        f"{', ' + str(report_u_path) if report_u_path.exists() else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
