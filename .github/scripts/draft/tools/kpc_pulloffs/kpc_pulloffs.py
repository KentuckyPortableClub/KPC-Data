#!/usr/bin/env python3
"""kpc_pulloffs: Kentucky Portable Club pull-off / parking CANDIDATE finder (version 1).

Looks along public roads in and around a park's OFFICIAL outline for gravel or
paved lots on public-domain USDA NAIP aerial photos, with Census TIGER roads.
It writes candidates and scores only; chat 11 grades them. Python 3.12.

Run:      python kpc_pulloffs.py --parks parks.json --access data/access/US-KY.json --out out
Selftest: python kpc_pulloffs.py --selftest      (no network; prints PASS or FAIL)
"""
from __future__ import annotations

import argparse
import datetime as _dt
import glob
import hashlib
import io
import json
import math
import os
import re
import shutil
import sys
import tempfile
import time
import traceback
import urllib.parse
import urllib.robotparser

import numpy as np
from PIL import Image, ImageDraw
from pyproj import Transformer
from scipy import ndimage
from shapely import contains_xy
from shapely.geometry import (LineString, MultiLineString, MultiPoint, Point, Polygon, box, shape)
from shapely.ops import transform as shp_transform, unary_union

VERSION = "1.0.0"
TOOL_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- sources
TIGER_BASE = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/Transportation/MapServer"
NAIP_BASE = "https://imagery.nationalmap.gov/arcgis/rest/services/USGSNAIPImagery/ImageServer"
# FEMA / ORNL / USGS "USA Structures" building outlines (> 450 sq ft), a public government layer, no key.
STRUCT_BASE = "https://services2.arcgis.com/FiaPA4ga0iQKduv3/arcgis/rest/services/USA_Structures_View/FeatureServer/0"
TIGER_LAYER_NAMES = ("Primary Roads", "Secondary Roads 72_1k scale", "Local Roads")
TIGER_LAYER_FALLBACK = (2, 6, 8)

# Install contract rule 6: sources never used. This is a GUARD list only: any URL whose
# host matches is refused before a request is made. Nothing in this tool reads them.
NEVER_USE_HOSTS = (
    "openstreetmap.org", "openstreetmap.fr", "osm.org", "overpass-api.de", "overpass.kumi.systems",
    "geofabrik.de", "google.com", "maps.googleapis.com", "tile.googleapis.com", "ggpht.com",
    "alltrails.com", "gaiagps.com", "strava.com", "tripadvisor.com", "yelp.com",
    "wikipedia.org", "wikimedia.org", "protectedplanet.net", "unep-wcmc.org",
)
# A government's own file on cloud storage IS allowed (contract rule 6). (WDPA = Protected Planet: never.)
ALLOWED_CLOUD = ("storage.googleapis.com",)
NEVER_USE_WORDS = ("openstreetmap", "overpass", "geofabrik", "google", "alltrails", "gaiagps", "strava",
                   "tripadvisor", "yelp", "wikipedia", "wikimedia", "protectedplanet", "wdpa", "unep")
# ---- end of the never-use guard

# ---------------------------------------------------------------- wording (spec PART 1 #5, RULED G-P2/G-P3)
LABEL_FIRST = "Possible pull-off (seen on an aerial photo, not official)."
LABEL_INSIDE = LABEL_FIRST + " Inside the park's official boundary."
LABEL_OUTSIDE = LABEL_FIRST + " Just outside the park's boundary: walk in to activate."
PILE_LABEL = "seen on an aerial photo"
NOTICE_SHORT = ("ℹ️ Maps and park info are a planning aid, not a guarantee. "
                "Always check the official agency map and rules before you go.")

# ---------------------------------------------------------------- road classes (TIGER MTFCC)
PUBLIC_CLASSES = {"S1200": "primary/secondary road", "S1400": "local road", "S1500": "vehicular trail (4WD)",
                  "S1640": "service drive"}
HINT_CLASSES = {"S1780": "parking lot road"}          # hint only, never a road to touch
OTHER_CAR_CLASSES = {"S1100": "interstate", "S1630": "ramp", "S1740": "private road", "S1730": "alley",
                     "S1750": "internal census road"}
HALF_WIDTH_M = {"S1100": 12.0, "S1200": 6.0, "S1400": 4.0, "S1500": 3.0, "S1640": 4.0, "S1630": 5.0,
                "S1740": 3.0, "S1730": 3.0, "S1750": 3.0, "S1780": 3.0}

# ---------------------------------------------------------------- lot test settings (explainable, v1)
P = dict(
    ndvi_max=0.15,        # vegetation index below this = bare (gravel, pavement, soil)
    dry_ndvi=0.07,        # ... but yellow (saturation > dry_sat) AND index above dry_ndvi = dry grass or hay, not bare
    dry_sat=0.33,
    nir_water=35,         # NIR darker than this = water (or deep shadow)
    dark_max=45,          # mean RGB below this = shadow, not a surface
    grey_sat=0.25,        # colour saturation below this = grey like gravel or pavement
    min_area_m2=300.0,    # room for about 3 cars
    min_width_m=8.0,      # shoulders and lanes narrower than ~8 m are never candidates (G-P1)
    max_elong=6.0,        # long and thin = a lane or road, not a lot
    max_area_m2=30000.0,  # bigger = a field, quarry or bare ground
    contact_m=3.0,        # "touching the road" = within 3 m of the pavement edge
    building_m=15.0,      # buildings this close outside the park = a house, farm or business lot
    sample_step_m=150.0,  # spec: every 150 m along roads
    chip_m=120.0,         # spec: about 120 x 120 m
    res_m=0.6,            # NAIP pixel
    cell_m=500.0,         # one NAIP request covers a 500 m cell + margin (one request is ~30 s)
    margin_m=80.0,
    dup_m=50.0,           # within 50 m of an official access point = duplicate
    recall_road_m=30.0,   # an access pin "sits next to a road" if within 30 m of a public road
    band_m=100.0,         # RULED G-P2
    band_ext_m=400.0,     # RULED G-P2, only for parks with no official access and no approved pull-off
    old_years=5,
)


def today() -> str:
    return _dt.date.today().isoformat()


class FetchError(Exception):
    pass


# =============================================================== polite web client
class Net:
    """Robots, 1 request per 2 s per host, 429/503 back-off, cache, never-use guard."""

    def __init__(self, ua: str, cache_dir: str, transport=None, sleep=time.sleep, clock=time.monotonic,
                 min_gap=2.0):
        self.ua = ua
        self.ua_token = "KPC park tools"
        self.cache_dir = cache_dir
        self.sleep = sleep
        self.clock = clock
        self.min_gap = min_gap
        self.last: dict[str, float] = {}
        self.resting: set[str] = set()
        self.robots: dict[str, object] = {}
        self.notes: list[str] = []
        self.count = 0
        self._session = None
        self.transport = transport or self._http

    def _http(self, url: str, timeout):
        import requests
        if self._session is None:
            self._session = requests.Session()
        r = self._session.get(url, headers={"User-Agent": self.ua}, timeout=timeout)
        return r.status_code, {k.lower(): v for k, v in r.headers.items()}, r.content

    @staticmethod
    def host(url: str) -> str:
        return (urllib.parse.urlsplit(url).hostname or "").lower()

    @staticmethod
    def never_use(url: str) -> bool:
        h = Net.host(url)
        if any(h == a or h.endswith("." + a) for a in ALLOWED_CLOUD):
            return False
        return any(h == b or h.endswith("." + b) for b in NEVER_USE_HOSTS)

    def _raw(self, url: str, timeout=(15, 120)):
        h = self.host(url)
        if h in self.resting:
            raise FetchError(f"host {h} is resting this run (repeated 429/503)")
        busy_tries, err_tries = 0, 0
        while True:
            gap = self.clock() - self.last.get(h, -1e9)
            if gap < self.min_gap:
                self.sleep(self.min_gap - gap)
            self.last[h] = self.clock()
            self.count += 1
            try:
                status, headers, body = self.transport(url, timeout)
            except FetchError:
                raise
            except Exception as e:  # network trouble
                err_tries += 1
                if err_tries > 2:
                    raise FetchError(f"network error: {type(e).__name__}: {str(e)[:120]}")
                self.sleep(5 * err_tries)
                continue
            if status in (429, 503):
                busy_tries += 1
                if busy_tries > 3:
                    self.resting.add(h)
                    self.notes.append(f"{h}: marked resting after 3 retries on HTTP {status}")
                    raise FetchError(f"host {h} answered {status} after 3 retries; resting this run")
                ra = headers.get("retry-after", "")
                wait = float(ra) if ra.strip().isdigit() else (15, 45, 90)[busy_tries - 1]
                self.sleep(min(wait, 120))
                continue
            if status in (500, 502, 504):
                err_tries += 1
                if err_tries > 2:
                    raise FetchError(f"HTTP {status}")
                self.sleep(5 * err_tries)
                continue
            return status, headers, body

    def allowed(self, url: str) -> bool:
        sp = urllib.parse.urlsplit(url)
        h = (sp.hostname or "").lower()
        if h not in self.robots:
            rurl = f"{sp.scheme}://{sp.netloc}/robots.txt"
            rp = urllib.robotparser.RobotFileParser()
            try:
                status, headers, body = self._raw(rurl, timeout=(10, 30))
            except FetchError as e:
                self.robots[h] = False
                self.notes.append(f"{h}: robots.txt could not be read ({e}); host skipped (RFC 9309: unreachable = disallow)")
                return False
            text = body.decode("utf-8", "replace")
            if status == 200 and "<html" not in text[:500].lower():
                rp.parse(text.splitlines())
                self.robots[h] = rp
                self.notes.append(f"{h}: robots.txt read and obeyed")
            elif 400 <= status < 500 or status == 200:
                self.robots[h] = True
                why = (f"HTTP {status}" if status != 200 else "it answered with a web page, not a robots file")
                self.notes.append(f"{h}: no robots rules ({why}); treated as allow-all (RFC 9309)")
            else:
                self.robots[h] = False
                self.notes.append(f"{h}: robots.txt HTTP {status}; host skipped")
        r = self.robots[h]
        if r is True or r is False:
            return bool(r)
        return r.can_fetch(self.ua_token, url)

    def get(self, url: str, params: dict | None = None, kind: str = "misc", validate=None, timeout=(15, 120)):
        """Returns (body bytes, meta{url, read_date, content_type, cached})."""
        full = url + ("?" + urllib.parse.urlencode(params) if params else "")
        if self.never_use(full):
            raise FetchError("source on the never-use list (install contract rule 6)")
        key = hashlib.sha1(full.encode()).hexdigest()
        cdir = os.path.join(self.cache_dir, kind)
        cbin, cmeta = os.path.join(cdir, key + ".bin"), os.path.join(cdir, key + ".json")
        if os.path.exists(cbin) and os.path.exists(cmeta):
            try:
                meta = json.load(open(cmeta))
                body = open(cbin, "rb").read()
                if validate is None or validate(body, meta.get("content_type", "")):
                    meta["cached"] = True
                    return body, meta
            except Exception:
                pass
        if not self.allowed(full):
            raise FetchError(f"robots.txt does not allow {urllib.parse.urlsplit(full).path}")
        status, headers, body = self._raw(full, timeout)
        if status != 200:
            raise FetchError(f"HTTP {status}")
        ctype = headers.get("content-type", "")
        if validate is not None and not validate(body, ctype):
            snippet = body[:160].decode("utf-8", "replace").replace("\n", " ")
            raise FetchError(f"unexpected answer ({ctype or 'no type'}): {snippet}")
        meta = {"url": full, "read_date": today(), "content_type": ctype, "cached": False}
        os.makedirs(cdir, exist_ok=True)
        with open(cbin + ".tmp", "wb") as f:
            f.write(body)
        os.replace(cbin + ".tmp", cbin)
        json.dump(meta, open(cmeta, "w"))
        return body, meta

    def get_json(self, url, params=None, kind="json"):
        def ok(b, ct):
            try:
                d = json.loads(b)
            except Exception:
                return False
            return not (isinstance(d, dict) and "error" in d and len(d) <= 2)
        body, meta = self.get(url, params, kind, ok)
        return json.loads(body), meta


# =============================================================== input readers
REF_RE = re.compile(r"^[A-Z]{1,3}-\d{3,6}$")


def _num(v):
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return float(v)
    if isinstance(v, str):
        try:
            return float(v)
        except ValueError:
            return None
    return None


def _latlon_ok(lat, lon):
    return (lat is not None and lon is not None and -90 <= lat <= 90 and -180 <= lon <= 180
            and not (lat == 0 and lon == 0))


def _kind(d):
    return str(d.get("kind") or d.get("type") or d.get("label") or d.get("name") or "")


def extract_points(obj, ref=None, out=None, depth=0):
    """Tolerant reader for access / hint files whose exact shape may vary.
    Accepts dicts with lat/lon keys, GeoJSON Points, rows like [lat, lon, "label"] keyed by park ref."""
    if out is None:
        out = []
    if depth > 12:
        return out
    if isinstance(obj, dict):
        g = obj.get("geometry") if obj.get("type") == "Feature" else (obj if obj.get("type") == "Point" else None)
        if isinstance(g, dict) and g.get("type") == "Point" and isinstance(g.get("coordinates"), list):
            c = g["coordinates"]
            props = obj.get("properties") or {}
            lon, lat = (_num(c[0]), _num(c[1])) if len(c) > 1 else (None, None)
            if _latlon_ok(lat, lon):
                out.append({"lat": lat, "lon": lon, "ref": props.get("ref") or ref, "kind": _kind(props)})
            return out
        lat = next((_num(obj[k]) for k in ("lat", "latitude", "Lat", "LAT") if k in obj), None)
        lon = next((_num(obj[k]) for k in ("lon", "lng", "long", "longitude", "Lon", "LON") if k in obj), None)
        if _latlon_ok(lat, lon):
            out.append({"lat": lat, "lon": lon, "ref": obj.get("ref") or ref, "kind": _kind(obj)})
            return out
        for k, v in obj.items():
            if isinstance(v, (dict, list)):
                extract_points(v, k if isinstance(k, str) and REF_RE.match(k) else ref, out, depth + 1)
        return out
    if isinstance(obj, list):
        if len(obj) >= 2 and all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in obj[:2]):
            a, b = float(obj[0]), float(obj[1])
            label = next((str(v) for v in obj[2:] if isinstance(v, str)), "")
            if (abs(a) <= 90 < abs(b)) or (_latlon_ok(a, b) and a > 0 > b):   # lat, lon (western hemisphere)
                lat, lon = a, b
            else:
                lon, lat = a, b
            if _latlon_ok(lat, lon):
                out.append({"lat": lat, "lon": lon, "ref": ref, "kind": label})
            return out
        for v in obj:
            if isinstance(v, (dict, list)):
                extract_points(v, ref, out, depth + 1)
    return out


def load_parks(path):
    d = json.load(open(path, encoding="utf-8"))
    if isinstance(d, dict) and isinstance(d.get("parks"), list):
        d = d["parks"]
    if isinstance(d, dict):
        d = [dict(v, ref=k) if isinstance(v, dict) else {"ref": k} for k, v in d.items()]
    parks = []
    for p in d:
        if not isinstance(p, dict) or not p.get("ref"):
            continue
        p = dict(p)
        p["ref"] = str(p["ref"])
        p["_base"] = os.path.dirname(os.path.abspath(path))
        parks.append(p)
    return parks


def esri_to_geojson_geom(g):
    if "rings" in g:
        return {"type": "Polygon", "coordinates": g["rings"]}, (g.get("spatialReference") or {})
    if "paths" in g:
        return {"type": "MultiLineString", "coordinates": g["paths"]}, (g.get("spatialReference") or {})
    return None, {}


def parse_outline(obj):
    """GeoJSON (FeatureCollection / Feature / geometry) or Esri JSON -> shapely polygon in lon/lat."""
    polys, srs = [], {}
    if isinstance(obj, dict) and isinstance(obj.get("features"), list):
        srs = obj.get("spatialReference") or {}
        items = obj["features"]
    else:
        items = [obj]
    for it in items:
        g = it.get("geometry", it) if isinstance(it, dict) else None
        if not isinstance(g, dict):
            continue
        sr = {}
        if "rings" in g:
            g, sr = esri_to_geojson_geom(g)
        if not g or g.get("type") not in ("Polygon", "MultiPolygon"):
            continue
        try:
            s = shape(g)
        except Exception:
            continue
        ref_sr = sr or srs or {}
        wkid = ref_sr.get("latestWkid") or ref_sr.get("wkid")
        if wkid and int(wkid) not in (4326, 4269):
            t = Transformer.from_crs(3857 if int(wkid) == 102100 else int(wkid), 4326, always_xy=True)
            s = shp_transform(t.transform, s)
        polys.append(s if s.is_valid else s.buffer(0))
    if not polys:
        raise ValueError("no polygon in the outline file")
    u = unary_union(polys)
    if u.is_empty or u.area <= 0:
        raise ValueError("outline is empty")
    minx, miny, maxx, maxy = u.bounds
    if not (-180 <= minx <= 180 and -90 <= miny <= 90 and -180 <= maxx <= 180 and -90 <= maxy <= 90):
        raise ValueError("outline coordinates are not longitude/latitude")
    return u


# =============================================================== geometry helpers
def utm_epsg(lon, lat):
    zone = int((lon + 180) // 6) + 1
    return (32600 if lat >= 0 else 32700) + zone


class Proj:
    def __init__(self, epsg):
        self.epsg = epsg
        self.fwd = Transformer.from_crs(4326, epsg, always_xy=True)
        self.inv = Transformer.from_crs(epsg, 4326, always_xy=True)

    def to_m(self, geom):
        return shp_transform(self.fwd.transform, geom)

    def to_ll(self, x, y):
        lon, lat = self.inv.transform(x, y)
        return lat, lon


def iter_lines(g):
    if g is None or g.is_empty:
        return
    if isinstance(g, LineString):
        yield g
    elif hasattr(g, "geoms"):
        for s in g.geoms:
            yield from iter_lines(s)


def iter_rings(g):
    if isinstance(g, Polygon):
        yield g.exterior
        yield from g.interiors
    elif hasattr(g, "geoms"):
        for s in g.geoms:
            yield from iter_rings(s)


# =============================================================== TIGER roads
def tiger_layers(net):
    try:
        d, _ = net.get_json(TIGER_BASE, {"f": "json"}, kind="tiger")
        found = {l.get("name"): l.get("id") for l in d.get("layers", []) if isinstance(l, dict)}
        ids = [found[n] for n in TIGER_LAYER_NAMES if n in found]
        if len(ids) == len(TIGER_LAYER_NAMES):
            return ids
    except FetchError:
        pass
    return list(TIGER_LAYER_FALLBACK)


def fetch_roads(net, bbox_ll, proj, notes):
    """All TIGER road lines in a lon/lat box, projected to metres. The box is split in 0.1 degree chunks."""
    minx, miny, maxx, maxy = bbox_ll
    step = 0.1
    roads, seen = [], set()
    layers = tiger_layers(net)
    xs = np.arange(minx, maxx, step).tolist() or [minx]
    ys = np.arange(miny, maxy, step).tolist() or [miny]
    for lid in layers:
        for x0 in xs:
            for y0 in ys:
                env = f"{x0:.6f},{y0:.6f},{min(x0 + step, maxx):.6f},{min(y0 + step, maxy):.6f}"
                offset = 0
                while True:
                    params = {"where": "1=1", "geometry": env, "geometryType": "esriGeometryEnvelope",
                              "inSR": "4326", "spatialRel": "esriSpatialRelIntersects",
                              "outFields": "MTFCC,NAME,BASENAME,OBJECTID", "returnGeometry": "true",
                              "outSR": "4326", "resultOffset": str(offset), "resultRecordCount": "2000",
                              "f": "json"}
                    d, meta = net.get_json(f"{TIGER_BASE}/{lid}/query", params, kind="tiger")
                    feats = d.get("features") if isinstance(d, dict) else None
                    if not isinstance(feats, list):
                        notes.append(f"TIGER layer {lid}: answer had no 'features' list; skipped")
                        break
                    for f in feats:
                        a = {str(k).upper(): v for k, v in (f.get("attributes") or {}).items()}
                        g = f.get("geometry") or {}
                        paths = [p for p in (g.get("paths") or []) if isinstance(p, list) and len(p) >= 2]
                        if not paths:
                            continue
                        oid = (lid, a.get("OBJECTID"), json.dumps(paths[0][:2]))
                        if oid in seen:
                            continue
                        seen.add(oid)
                        try:
                            geom = MultiLineString(paths)
                        except Exception:
                            continue
                        roads.append({"geom": proj.to_m(geom), "mtfcc": str(a.get("MTFCC") or "").upper(),
                                      "name": str(a.get("NAME") or a.get("BASENAME") or "").strip(),
                                      "source_url": meta["url"], "read_date": meta["read_date"]})
                    if d.get("exceededTransferLimit") and feats:
                        offset += len(feats)
                        continue
                    break
    return roads


def fetch_structures(net, bbox_ll, proj, notes):
    """FEMA USA Structures building outlines in a lon/lat box (0.05 degree chunks), in metres.
    Returns None when the layer could not be read (the roof test on the photo is then the only check)."""
    minx, miny, maxx, maxy = bbox_ll
    step = 0.05
    out = []
    xs = np.arange(minx, maxx, step).tolist() or [minx]
    ys = np.arange(miny, maxy, step).tolist() or [miny]
    try:
        for x0 in xs:
            for y0 in ys:
                env = f"{x0:.6f},{y0:.6f},{min(x0 + step, maxx):.6f},{min(y0 + step, maxy):.6f}"
                offset = 0
                while True:
                    params = {"where": "1=1", "geometry": env, "geometryType": "esriGeometryEnvelope",
                              "inSR": "4326", "spatialRel": "esriSpatialRelIntersects", "outFields": "OBJECTID",
                              "returnGeometry": "true", "outSR": "4326", "resultOffset": str(offset),
                              "resultRecordCount": "2000", "f": "json"}
                    d, _meta = net.get_json(f"{STRUCT_BASE}/query", params, kind="structures")
                    feats = d.get("features") if isinstance(d, dict) else None
                    if not isinstance(feats, list):
                        raise FetchError("answer had no 'features' list")
                    for f in feats:
                        for ring in ((f.get("geometry") or {}).get("rings") or []):
                            try:
                                if isinstance(ring, list) and len(ring) >= 4:
                                    out.append(proj.to_m(Polygon(ring)))
                            except Exception:
                                continue
                    if d.get("exceededTransferLimit") and feats:
                        offset += len(feats)
                        continue
                    break
    except FetchError as e:
        notes.append(f"FEMA USA Structures (building outlines) not read ({e}): only the roof test on the photo was used")
        return None
    return out


def raster_polys(shape_hw, x0, y1, res, polys):
    H, W = shape_hw
    im = Image.new("L", (W, H), 0)
    dr = ImageDraw.Draw(im)
    for g in polys:
        for poly in getattr(g, "geoms", [g]):
            ext = [((x - x0) / res, (y1 - y) / res) for x, y in poly.exterior.coords]
            if len(ext) >= 3:
                dr.polygon(ext, fill=1)
    return np.asarray(im, dtype=bool)


# =============================================================== NAIP
def _is_image(b, ct):
    return len(b) > 100 and (b[:2] in (b"II", b"MM") or b[:4] == b"\x89PNG" or "image" in ct)


def naip_tile(net, epsg, bbox_m, px):
    params = {"bbox": ",".join(f"{v:.2f}" for v in bbox_m), "bboxSR": str(epsg), "imageSR": str(epsg),
              "size": f"{px},{px}", "format": "tiff", "pixelType": "U8", "noData": "0",
              "renderingRule": json.dumps({"rasterFunction": "None"}),
              "interpolation": "RSP_BilinearInterpolation", "f": "image"}
    body, meta = net.get(f"{NAIP_BASE}/exportImage", params, kind="naip", validate=_is_image)
    im = Image.open(io.BytesIO(body))
    arr = np.array(im)
    if arr.ndim != 3 or arr.shape[2] < 4:
        nb = 1 if arr.ndim == 2 else arr.shape[2]
        raise FetchError(f"NAIP answered with {nb} band(s); 4 are needed (with near-infrared)")
    return arr[:, :, :4].astype(np.float32), meta


def naip_years(net, bbox_ll, notes):
    """Footprints of the NAIP photos (catalog), for the photo year. Empty list if it fails."""
    out, offset = [], 0
    for _ in range(40):
        params = {"where": "Category=1", "geometry": ",".join(f"{v:.6f}" for v in bbox_ll),
                  "geometryType": "esriGeometryEnvelope", "inSR": "4326",
                  "spatialRel": "esriSpatialRelIntersects", "outFields": "Year,acquisition_date,State",
                  "returnGeometry": "true", "outSR": "4326", "resultOffset": str(offset),
                  "resultRecordCount": "50", "f": "json"}
        try:
            d, meta = net.get_json(f"{NAIP_BASE}/query", params, kind="naipcat")
        except FetchError as e:
            notes.append(f"NAIP photo-year list not read ({e}); photo year looked up per candidate instead")
            return out
        feats = d.get("features") or []
        for f in feats:
            a = {str(k).lower(): v for k, v in (f.get("attributes") or {}).items()}
            yr = a.get("year")
            if not yr and a.get("acquisition_date"):
                try:
                    yr = _dt.datetime.fromtimestamp(a["acquisition_date"] / 1000, _dt.timezone.utc).year
                except Exception:
                    yr = None
            g, _ = esri_to_geojson_geom(f.get("geometry") or {})
            if yr and g:
                try:
                    out.append((int(yr), shape(g)))
                except Exception:
                    pass
        if d.get("exceededTransferLimit") and feats:
            offset += len(feats)
            continue
        break
    return out


def photo_year_at(years, lat, lon):
    pt = Point(lon, lat)
    ys = [y for y, g in years if g.contains(pt)]
    return max(ys) if ys else None


def identify_year(net, lat, lon, notes):
    params = {"geometry": json.dumps({"x": round(lon, 6), "y": round(lat, 6), "spatialReference": {"wkid": 4326}}),
              "geometryType": "esriGeometryPoint", "returnGeometry": "false", "returnCatalogItems": "true",
              "f": "json"}
    try:
        d, _ = net.get_json(f"{NAIP_BASE}/identify", params, kind="naipcat")
    except FetchError as e:
        notes.append(f"photo year not read ({e})")
        return None
    yrs = []
    for f in ((d.get("catalogItems") or {}).get("features") or []):
        a = {str(k).lower(): v for k, v in (f.get("attributes") or {}).items()}
        if a.get("year") and a.get("category") in (1, None):
            yrs.append(int(a["year"]))
    return max(yrs) if yrs else None


# =============================================================== lot test
def raster_lines(shape_hw, x0, y1, res, geoms_hw):
    """Draw road lines (metres) onto a boolean mask. geoms_hw: list of (geometry, half width in m)."""
    h, w = shape_hw
    im = Image.new("L", (w, h), 0)
    dr = ImageDraw.Draw(im)
    for geom, hw in geoms_hw:
        wpx = max(1, int(round(2 * hw / res)))
        for ln in iter_lines(geom):
            pts = [((x - x0) / res - 0.5, (y1 - y) / res - 0.5) for x, y in ln.coords]
            if len(pts) >= 2:
                dr.line(pts, fill=255, width=wpx, joint="curve")
    return np.array(im) > 0


def _rect_sides(rows, cols, res):
    """Long and short side (m) of the smallest rotated rectangle around the pixels."""
    if len(rows) < 3:
        return res, res
    rect = MultiPoint(list(zip(cols.tolist(), rows.tolist()))).minimum_rotated_rectangle
    if rect.geom_type != "Polygon":
        return (rect.length + 1) * res, res
    c = list(rect.exterior.coords)
    a = math.dist(c[0], c[1]) + 1
    b = math.dist(c[1], c[2]) + 1
    return max(a, b) * res, min(a, b) * res


def _edge_pixels(sub):
    e = sub & ~ndimage.binary_erosion(sub)
    return np.nonzero(e)


def find_roofs(low, bright, res, shadow):
    """Roof = bright, sharp rectangle with a strong shadow on one side (spec step 5)."""
    roofs = np.zeros_like(low)
    lab, n = ndimage.label(low & (bright > 175), structure=np.ones((3, 3)))
    if n == 0:
        return roofs
    for i, s in enumerate(ndimage.find_objects(lab), start=1):
        if s is None:
            continue
        sub = lab[s] == i
        area = float(sub.sum()) * res * res
        if area < 30 or area > 2500:
            continue
        er, ec = _edge_pixels(sub)
        L, S = _rect_sides(er, ec, res)
        if area / max(L * S, 1e-6) < 0.75:
            continue
        r0, r1 = max(0, s[0].start - 6), min(low.shape[0], s[0].stop + 6)
        c0, c1 = max(0, s[1].start - 6), min(low.shape[1], s[1].stop + 6)
        m = lab[r0:r1, c0:c1] == i
        ring = ndimage.binary_dilation(m, iterations=6) & ~m
        sh = shadow[r0:r1, c0:c1]
        my, mx_ = np.nonzero(m)
        cy, cx = my.mean(), mx_.mean()
        ry, rx = np.nonzero(ring)
        ang = np.degrees(np.arctan2(-(ry - cy), rx - cx)) % 360
        sect = ((ang + 45) // 90).astype(int) % 4          # 0=E 1=N 2=W 3=S
        frac = [float(sh[ry[sect == k], rx[sect == k]].mean()) if np.any(sect == k) else 0.0 for k in range(4)]
        k = int(np.argmax(frac))
        if frac[k] >= 0.45 and frac[(k + 2) % 4] <= 0.15:
            roofs[s] |= sub
    return roofs


def lot_test(arr, x0, y1, res, roads_pub, roads_other, roads_hint, core, outline_m, band_m, hints_m, structs=None):
    """The explainable lot test on one NAIP tile (spec step 5). Returns (candidates, kept_out)."""
    H, W = arr.shape[:2]
    R, G, B, N = arr[..., 0], arr[..., 1], arr[..., 2], arr[..., 3]
    valid = (R + G + B + N) > 0
    ndvi = (N - R) / (N + R + 1e-6)
    bright = (R + G + B) / 3.0
    mx = np.maximum(np.maximum(R, G), B)
    mn = np.minimum(np.minimum(R, G), B)
    sat = (mx - mn) / np.maximum(mx, 1.0)
    water = N < P["nir_water"]
    dark = bright < P["dark_max"]
    shadow = (bright < 50) & (N < 110) & valid        # dark in every band (trees are bright in NIR)
    dry_grass = (ndvi > P["dry_ndvi"]) & (sat > P["dry_sat"])   # late-summer hay or dry grass: yellow, still bright in NIR
    low = (ndvi < P["ndvi_max"]) & ~water & ~dark & ~dry_grass & valid

    pub = raster_lines((H, W), x0, y1, res, [(r["geom"], HALF_WIDTH_M.get(r["mtfcc"], 4.0)) for r in roads_pub])
    oth = raster_lines((H, W), x0, y1, res, [(r["geom"], HALF_WIDTH_M.get(r["mtfcc"], 4.0)) for r in roads_other])
    oth &= ~pub
    k = max(1, int(round(P["contact_m"] / res)))
    contact_pub = ndimage.binary_dilation(pub, iterations=k) & ~pub
    contact_oth = ndimage.binary_dilation(oth, iterations=k) & ~oth & ~pub
    lotroad = raster_lines((H, W), x0, y1, res, [(r["geom"], HALF_WIDTH_M["S1780"]) for r in roads_hint])
    if lotroad.any():
        lotroad = ndimage.binary_dilation(lotroad, iterations=max(1, int(5 / res)))
    roofs = find_roofs(low & ~pub & ~oth, bright, res, shadow)
    fema = np.zeros((H, W), bool)
    if structs:
        tile = box(x0, y1 - H * res, x0 + W * res, y1)
        here = [g for g in structs if g.intersects(tile)]
        if here:
            fema = raster_polys((H, W), x0, y1, res, here)
            fema = ndimage.binary_dilation(fema, iterations=max(1, int(2 / res)))
    roofs = roofs | fema
    near_bld = ndimage.binary_dilation(roofs, iterations=max(1, int(P["building_m"] / res))) if roofs.any() else roofs
    near_fema = ndimage.binary_dilation(fema, iterations=max(1, int(P["building_m"] / res))) if fema.any() else fema
    cand = low & ~pub & ~oth & ~roofs
    cand = ndimage.binary_opening(cand, structure=np.ones((3, 3)))
    dist_pub = ndimage.distance_transform_edt(~pub) * res if pub.any() else np.full((H, W), 1e9)
    lab, _ = ndimage.label(cand, structure=np.ones((3, 3)))
    cands, kept_out = [], []
    min_px = int(100 / (res * res))
    outline_edge = outline_m.boundary
    for i, s in enumerate(ndimage.find_objects(lab), start=1):
        if s is None:
            continue
        sub = lab[s] == i
        npx = int(sub.sum())
        if npx < min_px:
            continue
        rr, cc = np.nonzero(sub)
        X = x0 + (float(cc.mean()) + s[1].start + 0.5) * res
        Y = y1 - (float(rr.mean()) + s[0].start + 0.5) * res
        if not (core[0] <= X < core[2] and core[1] <= Y < core[3]):
            continue                                     # the neighbouring tile owns it
        pt = Point(X, Y)
        inside = bool(outline_m.contains(pt))
        dist_out = 0.0 if inside else float(outline_edge.distance(pt))
        if dist_out > band_m:
            continue
        area = npx * res * res
        t_pub = int(contact_pub[s][sub].sum())
        t_oth = int(contact_oth[s][sub].sum())
        base = {"x": X, "y": Y, "area_m2": int(round(area))}
        if t_pub == 0:
            if t_oth > 0 and area >= P["min_area_m2"]:
                kept_out.append(dict(base, reason="touches only an interstate, ramp, alley or private road, not a public road"))
            continue                                     # no public road to it
        if area < P["min_area_m2"]:
            kept_out.append(dict(base, reason=f"too small: about {round(area)} m², less than about 300 m² (3 cars)"))
            continue
        if area > P["max_area_m2"]:
            kept_out.append(dict(base, reason=f"too big for a lot (about {round(area)} m²): a field, quarry or bare ground"))
            continue
        depth = float(np.percentile(dist_pub[s][sub], 95))
        er, ec = _edge_pixels(sub)
        L, S = _rect_sides(er + s[0].start, ec + s[1].start, res)
        grey = float((sat[s][sub] < P["grey_sat"]).mean())
        if depth < P["min_width_m"] or S < P["min_width_m"]:
            kept_out.append(dict(base, reason=f"plain road shoulder or strip about {round(min(depth, S))} m wide "
                                              f"(narrower than about 8 m: never a pull-off, ruling G-P1)"))
            continue
        if L / max(S, 1e-6) > P["max_elong"]:
            kept_out.append(dict(base, reason=f"long and thin ({round(L)} x {round(S)} m): a lane, driveway or road, not a lot"))
            continue
        if L > 60 and L / max(S, 1e-6) > 3 and S < 20:
            ang = _road_angle_diff(rr, cc, roads_pub, pt)
            if ang is not None and ang < 20:
                kept_out.append(dict(base, reason=f"long strip ({round(L)} x {round(S)} m) running along the road: probably "
                                                  "the road itself (the Census road line is off by a few metres) or a wide shoulder"))
                continue
        if area > 5000 and grey < 0.4:
            kept_out.append(dict(base, reason="large bare brown ground (a field?), not gravel or pavement"))
            continue
        nb = bool(near_bld[s][sub].any())
        if nb and not inside:
            src = " (building outline from FEMA USA Structures)" if near_fema[s][sub].any() else ""
            kept_out.append(dict(base, reason="next to buildings outside the park: a house, farm or business lot" + src))
            continue
        best = min(roads_pub, key=lambda r: r["geom"].distance(pt))
        notes, pen = [], 0.0
        if not best["name"]:
            if not inside:
                kept_out.append(dict(base, reason="the road has no name in the road data (could be a farm lane or private drive)"))
                continue
            pen += 0.15
            notes.append("the road has no name in the road data (an agency road?)")
        if nb:
            pen += 0.10
            notes.append("next to a building inside the park (an agency building?)")
        contact_len = t_pub * res * res / P["contact_m"]
        hint_txt = []
        if lotroad[s][sub].any():
            hint_txt.append("a lot road (Census class S1780) runs into it")
        for h in hints_m:
            if math.dist((h["x"], h["y"]), (X, Y)) <= 100:
                hint_txt.append(h["what"])
        s_size = min(1.0, area / 900.0)
        s_contact = min(1.0, contact_len / 20.0)
        s_shape = min(1.0, (S / max(L, 1e-6)) / 0.5)
        s_hint = 1.0 if hint_txt else 0.0
        score = 0.30 * s_size + 0.20 * s_contact + 0.25 * s_shape + 0.15 * grey + 0.10 * s_hint - pen
        score = max(0.0, min(1.0, score))
        cands.append(dict(base, score=round(score, 2), inside=inside, dist_out_m=int(round(dist_out)),
                          road_name=best["name"], road_class=best["mtfcc"], road_src=best["source_url"],
                          road_date=best["read_date"], width_m=int(round(S)), length_m=int(round(L)),
                          contact_m=int(round(contact_len)), grey=round(grey, 2), hint_txt=hint_txt, notes=notes,
                          _mask=(s, sub.copy())))
    return cands, kept_out


def _road_angle_diff(rr, cc, roads_pub, pt):
    """Angle (degrees, 0-90) between a patch's long axis and the nearest public road there."""
    if len(rr) < 5:
        return None
    cov = np.cov(np.vstack([cc.astype(float), -rr.astype(float)]))
    w, v = np.linalg.eigh(cov)
    ax = v[:, int(np.argmax(w))]
    best, bd = None, 1e18
    for r in roads_pub:
        for ln in iter_lines(r["geom"]):
            d = ln.distance(pt)
            if d < bd:
                best, bd = ln, d
    if best is None or best.length < 2:
        return None
    t = best.project(pt)
    a, b = best.interpolate(max(0.0, t - 10)), best.interpolate(min(best.length, t + 10))
    dx, dy = b.x - a.x, b.y - a.y
    n = math.hypot(dx, dy)
    if n < 1e-6:
        return None
    c = abs(ax[0] * dx / n + ax[1] * dy / n)
    return math.degrees(math.acos(min(1.0, c)))


# =============================================================== chips
def make_chip(arr, x0, y1, res, cand, outline_m, roads_pub):
    """JPEG, longest side 400 px: park line yellow, road white, patch red."""
    H, W = arr.shape[:2]
    s, sub = cand["_mask"]
    cx = (cand["x"] - x0) / res
    cy = (y1 - cand["y"]) / res
    half = max(P["chip_m"] / 2 / res, (s[0].stop - s[0].start) / 2 + 25, (s[1].stop - s[1].start) / 2 + 25)
    xs, ys = [cx - half, cx + half], [cy - half, cy + half]
    # widen the view so the park line shows when it is near (up to ~150 m away)
    edge = outline_m.boundary
    q = edge.interpolate(edge.project(Point(cand["x"], cand["y"])))
    if q.distance(Point(cand["x"], cand["y"])) <= 150:
        qx, qy = (q.x - x0) / res, (y1 - q.y) / res
        xs += [qx - 25, qx + 25]
        ys += [qy - 25, qy + 25]
    c0, c1 = int(max(0, min(xs))), int(min(W, max(xs)))
    r0, r1 = int(max(0, min(ys))), int(min(H, max(ys)))
    rgb = arr[r0:r1, c0:c1, :3]
    lo, hi = np.percentile(rgb, 1), np.percentile(rgb, 99)
    rgb = np.clip((rgb - lo) / max(hi - lo, 1) * 235 + 10, 0, 255).astype(np.uint8)
    h, w = rgb.shape[:2]
    scale = 400.0 / max(h, w)
    W2, H2 = max(1, min(400, int(round(w * scale)))), max(1, min(400, int(round(h * scale))))
    im = Image.fromarray(rgb).resize((W2, H2), Image.BILINEAR)
    dr = ImageDraw.Draw(im)

    def tp(x, y):
        return (((x - x0) / res - c0) * scale, ((y1 - y) / res - r0) * scale)
    win = box(x0 + c0 * res - 20, y1 - r1 * res - 20, x0 + c1 * res + 20, y1 - r0 * res + 20)
    for r in roads_pub:
        for ln in iter_lines(r["geom"].intersection(win)):
            dr.line([tp(*c) for c in ln.coords], fill=(255, 255, 255), width=2)
    for ring in iter_rings(outline_m):
        for ln in iter_lines(ring.intersection(win)):
            dr.line([tp(*c) for c in ln.coords], fill=(255, 230, 0), width=3)
    m = np.zeros((H, W), bool)
    m[s] = sub
    m = m[r0:r1, c0:c1]
    mm = np.array(Image.fromarray((m * 255).astype(np.uint8)).resize((W2, H2), Image.NEAREST)) > 0
    edge = mm & ~ndimage.binary_erosion(mm, iterations=2)
    a = np.array(im)
    a[edge] = (255, 0, 0)
    out = io.BytesIO()
    Image.fromarray(a).save(out, "JPEG", quality=70)
    return out.getvalue()


# =============================================================== one park
def load_outline(park, net):
    if park.get("outline_file"):
        f = park["outline_file"]
        p = f if os.path.isabs(f) else os.path.join(park.get("_base", "."), f)
        if not os.path.exists(p) and os.path.exists(f):
            p = f
        obj = json.load(open(p, encoding="utf-8"))
        return parse_outline(obj), {"source": f, "read_date": today()}
    if park.get("outline_url"):
        body, meta = net.get(park["outline_url"], None, kind="outline")
        try:
            obj = json.loads(body)
        except Exception:
            raise ValueError("outline file is not JSON (GeoJSON or Esri JSON expected)")
        return parse_outline(obj), {"source": meta["url"], "read_date": meta["read_date"]}
    raise ValueError("no official outline given")


def _blank_result(park):
    return {"ref": park["ref"], "name": park.get("name", ""), "area": park["_area"], "status": "done", "rows": [],
            "kept_out": [], "notes": [], "errors": [], "recall": {"pins": 0, "found": 0}, "chips": {}}


def process_park(park, ctx):
    net, deadline = ctx["net"], ctx["deadline"]
    ref = park["ref"]
    res = _blank_result(park)
    try:
        outline_ll, osrc = load_outline(park, net)
    except (FetchError, ValueError, OSError, json.JSONDecodeError) as e:
        res["status"] = "no outline"
        res["notes"].append(f"no official outline ({e}): nothing produced (no outline = nothing to measure from)")
        return res
    c = outline_ll.centroid
    proj = Proj(utm_epsg(c.x, c.y))
    outline_m = proj.to_m(outline_ll).simplify(3.0, preserve_topology=True)
    # official access points (all of them for the duplicate drop; this park's for G-P2 and the recall check)
    acc = []
    for a in ctx["access"]:
        x, y = proj.fwd.transform(a["lon"], a["lat"])
        acc.append(dict(a, x=x, y=y))
    near = outline_m.buffer(P["band_m"])
    park_acc = [a for a in acc if a.get("ref") == ref or near.contains(Point(a["x"], a["y"]))]
    approved = [a for a in park_acc if "pull-off" in (a.get("kind") or "").lower()]
    extended = (not park_acc and not approved) or bool(park.get("no_official_access") and park.get("no_approved_pulloff"))
    band_m = P["band_ext_m"] if extended else P["band_m"]
    if extended:
        res["notes"].append("no official access point and no approved pull-off: looking up to 400 m outside (ruling G-P2)")
    band = outline_m.buffer(band_m)
    look = band.buffer(P["margin_m"] + 50)
    lb = shp_transform(proj.inv.transform, look).bounds
    try:
        roads = fetch_roads(net, lb, proj, res["notes"])
    except FetchError as e:
        res["status"] = "error"
        res["errors"].append(f"road data not read: {e}")
        return res
    pub, oth, hint = [], [], []
    for r in roads:
        r["geom"] = r["geom"].intersection(look)
        if r["geom"].is_empty:
            continue
        if r["mtfcc"] in PUBLIC_CLASSES:
            pub.append(r)
        elif r["mtfcc"] in HINT_CLASSES:
            hint.append(r)
        elif r["mtfcc"] in OTHER_CAR_CLASSES or not r["mtfcc"]:
            oth.append(r)
    res["roads"] = {"public": len(pub), "dropped (interstate/ramp/private/alley)": len(oth), "lot-road hints": len(hint)}
    hints_m = []
    for h in ctx["hints"]:
        x, y = proj.fwd.transform(h["lon"], h["lat"])
        if band.contains(Point(x, y)):
            what = f"an official {h.get('kind') or 'turnout, overlook or trailhead'} point is within 100 m"
            hints_m.append({"x": x, "y": y, "what": what})
    pic = ctx["pictures"].get(ref)
    if pic:
        pp = pic.get("p_points") or []
        for m in pp:
            x, y = proj.fwd.transform(float(m[1]), float(m[0]))
            hints_m.append({"x": x, "y": y, "what": "a P (parking) symbol on the agency picture map is within 100 m"})
        if not pp:
            res["notes"].append("an agency picture map exists but is not georeferenced, so its P symbols were not "
                                "scored; chat 11 can look at it")
    # points to look at (spec step 3)
    samples = []
    for r in pub:
        for ln in iter_lines(r["geom"].intersection(band)):
            n = max(1, int(ln.length // P["sample_step_m"]))
            for k in range(n + 1):
                p = ln.interpolate(min(ln.length, k * P["sample_step_m"]))
                samples.append(("road", p.x, p.y))
        ix = r["geom"].intersection(outline_m.boundary)
        for p in getattr(ix, "geoms", [ix]):
            if isinstance(p, Point) and not p.is_empty:
                samples.append(("entry", p.x, p.y))
    for h in hints_m:
        samples.append(("hint", h["x"], h["y"]))
    res["samples"] = {t: sum(1 for s_ in samples if s_[0] == t) for t in ("entry", "road", "hint")}
    if not pub:
        res["notes"].append("no public road inside the outline or within the band: nothing to look at")
        return res
    cm = P["cell_m"]
    cells = sorted({(math.floor(x / cm), math.floor(y / cm)) for _, x, y in samples})
    res["tiles"] = len(cells)
    years = naip_years(net, shp_transform(proj.inv.transform, band).bounds, res["notes"])
    structs = fetch_structures(net, lb, proj, res["notes"])
    res["buildings"] = len(structs) if structs is not None else "not read"
    cands = []
    px = int(round((cm + 2 * P["margin_m"]) / P["res_m"]))
    for k_, (i, j) in enumerate(cells, start=1):
        if time.monotonic() > deadline:
            res["status"] = "partial"
            res["partial_at"] = f"{k_ - 1} of {len(cells)} photo cells looked at"
            return res
        if not ctx.get("quiet"):
            print(f"{ref}: photo cell {k_}/{len(cells)}", file=sys.stderr, flush=True)
        core = (i * cm, j * cm, (i + 1) * cm, (j + 1) * cm)
        bb = (core[0] - P["margin_m"], core[1] - P["margin_m"], core[2] + P["margin_m"], core[3] + P["margin_m"])
        if not box(*bb).intersects(band):
            continue
        tb = box(*bb).buffer(30)
        tp = [dict(r, geom=r["geom"].intersection(tb)) for r in pub if r["geom"].intersects(tb)]
        if not tp:
            continue
        to = [dict(r, geom=r["geom"].intersection(tb)) for r in oth if r["geom"].intersects(tb)]
        th = [r for r in hint if r["geom"].intersects(tb)]
        try:
            arr, meta = naip_tile(net, proj.epsg, bb, px)
        except FetchError as e:
            res["errors"].append(f"NAIP photo for cell {i},{j} not read: {e}")
            continue
        except Exception as e:
            res["errors"].append(f"NAIP photo for cell {i},{j} could not be decoded: {type(e).__name__}: {e}")
            continue
        r_ = (bb[2] - bb[0]) / arr.shape[1]
        try:
            found, out = lot_test(arr, bb[0], bb[3], r_, tp, to, th, core, outline_m, band_m, hints_m, structs)
        except Exception as e:
            res["errors"].append(f"lot test failed on cell {i},{j}: {type(e).__name__}: {e}")
            continue
        for o in out:
            lat, lon = proj.to_ll(o["x"], o["y"])
            res["kept_out"].append({"lat": round(lat, 6), "lon": round(lon, 6), "area_m2": o["area_m2"],
                                    "reason": o["reason"]})
        for cnd in found:
            cnd["src"], cnd["read_date"] = meta["url"], meta["read_date"]
            cnd["chip"] = None
            if cnd["score"] >= ctx["cut"]:
                try:
                    cnd["chip"] = make_chip(arr, bb[0], bb[3], r_, cnd, outline_m, tp)
                except Exception as e:
                    res["errors"].append(f"chip not made: {type(e).__name__}: {e}")
            cnd.pop("_mask", None)
            cands.append(cnd)
    # merge near-duplicates (same lot seen from two cells)
    cands.sort(key=lambda c_: -c_["score"])
    merged = []
    for c_ in cands:
        if all(math.dist((c_["x"], c_["y"]), (m["x"], m["y"])) > 30 for m in merged):
            merged.append(c_)
    above = [c_ for c_ in merged if c_["score"] >= ctx["cut"]]
    for c_ in merged:
        if c_["score"] < ctx["cut"]:
            lat, lon = proj.to_ll(c_["x"], c_["y"])
            res["kept_out"].append({"lat": round(lat, 6), "lon": round(lon, 6), "area_m2": c_["area_m2"],
                                    "score": c_["score"], "reason": f"below the cut ({c_['score']} < {ctx['cut']})"})
    # recall check (acceptance test only): pins next to a public road, found BEFORE the duplicate drop
    pub_union = unary_union([r["geom"] for r in pub])
    for a in park_acc:
        pa = Point(a["x"], a["y"])
        if band.contains(pa) and pub_union.distance(pa) <= P["recall_road_m"]:
            res["recall"]["pins"] += 1
            if any(math.dist((a["x"], a["y"]), (c_["x"], c_["y"])) <= P["dup_m"] for c_ in above):
                res["recall"]["found"] += 1
    # drop duplicates of official access points (spec step 6)
    kept = []
    for c_ in above:
        d = min((math.dist((a["x"], a["y"]), (c_["x"], c_["y"])) for a in acc), default=1e9)
        if d <= P["dup_m"]:
            lat, lon = proj.to_ll(c_["x"], c_["y"])
            res["kept_out"].append({"lat": round(lat, 6), "lon": round(lon, 6), "area_m2": c_["area_m2"],
                                    "score": c_["score"], "reason": f"duplicate: an official access point is {round(d)} m away"})
            continue
        kept.append(c_)
    safe = re.sub(r"[^A-Za-z0-9_-]", "_", ref)
    this_year = _dt.date.today().year
    for n_, c_ in enumerate(kept, start=1):
        lat, lon = proj.to_ll(c_["x"], c_["y"])
        yr = photo_year_at(years, lat, lon) if years else None
        if yr is None:
            yr = identify_year(net, lat, lon, res["notes"])
        label = LABEL_INSIDE if c_["inside"] else LABEL_OUTSIDE
        why = [label]
        if not c_["inside"]:
            why.append(f"About {max(10, int(round(c_['dist_out_m'] / 10.0)) * 10)} m outside the boundary.")
        rd = c_["road_name"] or "an unnamed road"
        why.append(f"A bare patch of about {c_['area_m2']} m² ({c_['width_m']} x {c_['length_m']} m) touches "
                   f"{rd} ({c_['road_class']}, {PUBLIC_CLASSES.get(c_['road_class'], 'road')}) for about "
                   f"{c_['contact_m']} m; {int(round(c_['grey'] * 100))}% of it is grey like gravel or pavement.")
        why += [h[0].upper() + h[1:] + "." for h in c_["hint_txt"]]
        why += [x[0].upper() + x[1:] + "." for x in c_["notes"]]
        old = bool(yr and yr < this_year - P["old_years"])
        if old:
            why.append(f"photo is old ({yr})")
        else:
            why.append(f"NAIP photo {yr}." if yr else "NAIP photo year unknown.")
        chip_name = None
        if c_.get("chip"):
            chip_name = f"chips/{safe}_{n_:02d}.jpg"
            res["chips"][chip_name] = c_["chip"]
        res["rows"].append({
            "lat": round(lat, 6), "lon": round(lon, 6), "score": c_["score"], "inside": c_["inside"],
            "dist_out_m": c_["dist_out_m"], "road_name": c_["road_name"], "road_class": c_["road_class"],
            "photo_year": yr, "photo_old": old, "chip": chip_name, "why": " ".join(why),
            "label": label, "pile": PILE_LABEL, "area_m2": c_["area_m2"], "width_m": c_["width_m"],
            "source_url": c_["src"], "road_source_url": c_["road_src"], "outline_source": osrc["source"],
            "read_date": c_["read_date"],
        })
    return res


# =============================================================== outputs
class Out:
    """Every write goes through here, so nothing lands outside --out."""

    def __init__(self, root):
        self.root = os.path.realpath(root)
        os.makedirs(self.root, exist_ok=True)

    def path(self, *parts):
        p = os.path.realpath(os.path.join(self.root, *parts))
        if not (p == self.root or p.startswith(self.root + os.sep)):
            raise RuntimeError(f"refusing to write outside --out: {p}")
        os.makedirs(os.path.dirname(p), exist_ok=True)
        return p

    def write(self, rel, data, mode="w"):
        p = self.path(*rel.split("/"))
        tmp = p + ".tmp"
        with open(tmp, mode, **({} if "b" in mode else {"encoding": "utf-8"})) as f:
            f.write(data)
        os.replace(tmp, p)
        return p


def _safe(ref):
    return re.sub(r"[^A-Za-z0-9_-]", "_", ref)


def write_outputs(out: Out, parks, info):
    results = []
    for p in parks:
        f = out.path("work", "parks", _safe(p["ref"]) + ".json")
        if os.path.exists(f):
            results.append(json.load(open(f, encoding="utf-8")))
    by_area = {}
    for r in results:
        if r["status"] == "no outline":
            continue                                      # no outline = no output at all
        by_area.setdefault(r["area"], {})[r["ref"]] = r["rows"]
    for area, d in by_area.items():
        out.write(f"pulloffs/{area}.json", json.dumps(d, indent=1, ensure_ascii=False))
    rows = sorted(((r, row) for r in results for row in r["rows"]), key=lambda t: (-t[1]["score"], t[0]["ref"]))
    md = ["# Pull-off candidates for chat 11 (best first)", "", NOTICE_SHORT, "",
          f"Built {today()} by kpc_pulloffs {VERSION}. These are CANDIDATES seen on an aerial photo, not official. "
          "The tool decides nothing: chat 11 grades each one with its chip. They are shown under the official "
          f"access points, never above, in the bot pile ('{PILE_LABEL}'), apart from member reports.", "",
          "Chip colours: yellow = park line, white = public road, red = the patch.", ""]
    if not rows:
        md.append("_No candidates in this run._")
    for k, (r, row) in enumerate(rows, start=1):
        where = "inside" if row["inside"] else f"outside, about {row['dist_out_m']} m"
        photo = f"{row['photo_year'] or 'year unknown'}" + (f" (photo is old ({row['photo_year']}))" if row["photo_old"] else "")
        md += [f"## {k}. {r['ref']} {r['name']} — score {row['score']:.2f}", "",
               f"**{row['label']}**", "", row["why"], "",
               f"- where: {row['lat']}, {row['lon']} ({where})",
               f"- road: {row['road_name'] or '(no name)'} ({row['road_class']})",
               f"- photo: NAIP {photo}",
               f"- sources: [NAIP photo]({row['source_url']}) · [TIGER roads]({row['road_source_url']}) · "
               f"outline: {row['outline_source']} · read {row['read_date']}", ""]
        if row["chip"]:
            md += [f"![chip]({row['chip']})", ""]
    out.write("pulloffs/review.md", "\n".join(md) + "\n")
    pins = sum(r["recall"]["pins"] for r in results)
    found = sum(r["recall"]["found"] for r in results)
    rep = [f"# kpc_pulloffs run report ({today()})", "",
           f"- version {VERSION}; exit code {info['exit']}; ran {info['minutes']:.1f} min; {info['requests']} web requests",
           f"- parks in this input (after --areas / --limit): {len(parks)}; done: {info['done']}; "
           f"left for the next run: {info['left']}",
           f"- candidates for chat 11: {len(rows)}; kept out (log only, work/log/kept_out.jsonl): "
           f"{sum(len(r['kept_out']) for r in results)}", "",
           "## Recall check (acceptance test only, before the duplicate drop)", "",
           f"Official access pins next to a public road (within {int(P['recall_road_m'])} m) inside the search band: "
           f"{pins}; found within 50 m: {found}" + (f" ({100 * found / pins:.0f}%)" if pins else " (no pins to check)"),
           "", "## Parks", ""]
    for r in results:
        rep.append(f"- {r['ref']} {r['name']}: {r['status']}; {len(r['rows'])} candidate(s); {len(r['kept_out'])} kept out; "
                   f"photo cells {r.get('tiles', 0)}; points looked at {r.get('samples', {})}; roads {r.get('roads', {})}; "
                   f"recall {r['recall']['found']}/{r['recall']['pins']}")
        rep += [f"  - note: {n}" for n in r["notes"]]
        rep += [f"  - problem (skipped, run went on): {e}" for e in r["errors"]]
    rep += [f"- {x}" for x in info.get("partial", [])]
    rep += ["", "## Web manners", ""] + [f"- {n}" for n in info["net_notes"]] + [""]
    if info.get("crashes"):
        rep += ["## Items that failed (with reason; the run went on)", ""] + [f"- {c}" for c in info["crashes"]] + [""]
    out.write("report.md", "\n".join(rep))
    lines = [json.dumps(dict(k, ref=r["ref"]), ensure_ascii=False) for r in results for k in r["kept_out"]]
    out.write("work/log/kept_out.jsonl", "\n".join(lines) + ("\n" if lines else ""))


# =============================================================== main run
def run(args, transport=None, sleep=time.sleep):
    t0 = time.monotonic()
    out = Out(args.out)
    deadline = t0 + args.max_minutes * 60.0
    contact = os.environ.get("KPC_CONTACT", "").strip() or "contact not set"
    cache = os.path.abspath(args.cache) if args.cache else out.path("work", "cache", "x")[:-2]
    net = Net(f"KPC park tools ({contact})", cache, transport=transport, sleep=sleep)
    if contact == "contact not set":
        net.notes.append("KPC_CONTACT is not set, so the User-Agent says 'contact not set'")
    areas = [a.strip() for a in (args.areas or "").split(",") if a.strip()]
    sel = []
    for p in load_parks(args.parks):
        p["_area"] = str(p.get("area") or p.get("state") or (areas[0] if len(areas) == 1 else "US"))
        if areas and p["_area"] not in areas:
            continue
        sel.append(p)
    if args.limit:
        sel = sel[: args.limit]
    access, hints, pictures = [], [], {}
    for pat in args.access or []:
        for f in sorted(glob.glob(pat)) or [pat]:
            try:
                access += extract_points(json.load(open(f, encoding="utf-8")))
            except Exception as e:
                net.notes.append(f"access file {f} not read: {e}")
    for f in args.hints or []:
        try:
            hints += extract_points(json.load(open(f, encoding="utf-8")))
        except Exception as e:
            net.notes.append(f"hints file {f} not read: {e}")
    if args.pictures:
        try:
            for m in json.load(open(args.pictures, encoding="utf-8")).get("maps", []):
                if isinstance(m, dict) and m.get("ref"):
                    pictures[m["ref"]] = m
        except Exception as e:
            net.notes.append(f"picture-maps index not read: {e}")
    state_p = out.path("state.json")
    state = {"version": 1, "done": {}}
    if args.resume and os.path.exists(state_p):
        try:
            state = json.load(open(state_p, encoding="utf-8"))
            state.setdefault("done", {})
        except Exception:
            state = {"version": 1, "done": {}}
    else:                                                 # fresh run: forget old per-park results
        shutil.rmtree(os.path.dirname(out.path("work", "parks", "x")), ignore_errors=True)
        shutil.rmtree(os.path.dirname(out.path("pulloffs", "chips", "x")), ignore_errors=True)
    ctx = {"net": net, "deadline": deadline, "access": access, "hints": hints, "pictures": pictures, "cut": args.cut,
           "quiet": transport is not None}
    crashes, left, partial = [], 0, []
    for p in sel:
        if p["ref"] in state["done"]:
            continue
        if time.monotonic() > deadline:                   # stop starting new work
            left += 1
            continue
        try:
            r = process_park(p, ctx)
        except Exception as e:                            # one bad park never stops the run
            r = _blank_result(p)
            r["status"] = "error"
            r["errors"].append(f"{type(e).__name__}: {e}")
            crashes.append(f"{p['ref']}: {type(e).__name__}: {e} ({traceback.format_exc(limit=3).splitlines()[-1]})")
        if r["status"] == "partial":
            left += 1
            partial.append(f"{p['ref']} {p.get('name', '')}: time ran out after {r.get('partial_at', '?')}; "
                           "nothing written for it yet. Run again with --resume (downloads are cached).")
            continue
        for name, data in r.pop("chips", {}).items():
            out.write(f"pulloffs/{name}", data, "wb")
        out.write(f"work/parks/{_safe(p['ref'])}.json", json.dumps(r, ensure_ascii=False))
        state["done"][p["ref"]] = {"status": r["status"], "n": len(r["rows"]),
                                   "at": _dt.datetime.now().isoformat(timespec="seconds")}
        out.write("state.json", json.dumps(state, indent=1))
    code = 3 if left else 0
    out.write("state.json", json.dumps(state, indent=1))
    write_outputs(out, sel, {"exit": code, "minutes": (time.monotonic() - t0) / 60, "requests": net.count,
                             "done": sum(1 for p in sel if p["ref"] in state["done"]), "left": left,
                             "net_notes": net.notes, "crashes": crashes,
                             "partial": partial})
    return code


def parse_args(argv):
    ap = argparse.ArgumentParser(description="KPC pull-off / parking CANDIDATE finder (NAIP photos + TIGER roads).")
    ap.add_argument("--parks", help="parks file: [{ref, name, outline_url or outline_file, lat, lon, area?}]")
    ap.add_argument("--access", nargs="*", help="official access files (data/access/*.json), to drop duplicates")
    ap.add_argument("--pictures", help="picture-maps index.json (optional)")
    ap.add_argument("--hints", nargs="*", help="optional DOT / USGS turnout, overlook or trailhead points (JSON)")
    ap.add_argument("--out", help="output folder (the only place this tool writes)")
    ap.add_argument("--cache", help="download cache kept between runs (default <out>/work/cache)")
    ap.add_argument("--max-minutes", type=float, default=50.0, help="stop starting new work after this (default 50)")
    ap.add_argument("--resume", action="store_true", help="skip parks <out>/state.json says are done")
    ap.add_argument("--limit", type=int, default=0, help="only the first N parks")
    ap.add_argument("--areas", default="", help="e.g. US-KY,US-TN (the parks' 'area' field)")
    ap.add_argument("--cut", type=float, default=0.5, help="score cut; below it = log only (default 0.5)")
    ap.add_argument("--selftest", action="store_true", help="offline test with tests/; prints PASS or FAIL")
    a = ap.parse_args(argv)
    if not a.selftest and (not a.parks or not a.out):
        ap.error("--parks and --out are needed (or --selftest)")
    return a


# =============================================================== selftest (offline)
class FakeWeb:
    """Answers like TIGERweb, the NAIP ImageServer and one agency site, drawn from tests/scene.json."""

    def __init__(self, scene_path):
        self.sc = json.load(open(scene_path, encoding="utf-8"))
        o = self.sc["origin"]
        self.epsg = utm_epsg(o["lon"], o["lat"])
        self.fwd = Transformer.from_crs(4326, self.epsg, always_xy=True)
        self.inv = Transformer.from_crs(self.epsg, 4326, always_xy=True)
        self.ox, self.oy = self.fwd.transform(o["lon"], o["lat"])
        self.calls = []

    def ll(self, x, y):
        return list(self.inv.transform(self.ox + x, self.oy + y))

    def _json(self, d):
        return 200, {"content-type": "application/json"}, json.dumps(d).encode()

    def __call__(self, url, timeout):
        self.calls.append(url)
        sp = urllib.parse.urlsplit(url)
        q = dict(urllib.parse.parse_qsl(sp.query))
        h = sp.hostname
        if h == "busy.example.gov":
            return 429, {}, b"slow down"
        if sp.path == "/robots.txt":
            if h == "data.example.gov":
                return 200, {"content-type": "text/plain"}, b"User-agent: *\nDisallow: /private/\n"
            return 404, {}, b"not found"
        if h == "tigerweb.geo.census.gov":
            if sp.path.endswith("/MapServer"):
                names = ["Primary Roads Interstates 5M scale", "Primary Roads 2_1M scale", "Primary Roads",
                         "Secondary Roads Interstates and US Highways", "Secondary Roads 578k scale",
                         "Secondary Roads 289_144k scale", "Secondary Roads 72_1k scale", "Local Roads 72k scale",
                         "Local Roads", "Railroads"]
                return self._json({"layers": [{"id": i, "name": n} for i, n in enumerate(names)]})
            lid = int(sp.path.split("/")[-2])
            env = box(*map(float, q["geometry"].split(",")))
            feats = []
            for k, r in enumerate(self.sc["roads"]):
                layer = 2 if r["mtfcc"] == "S1100" else 6 if r["mtfcc"] == "S1200" else 8
                path = [self.ll(x, y) for x, y in r["line"]]
                if layer == lid and LineString(path).intersects(env):
                    feats.append({"attributes": {"MTFCC": r["mtfcc"], "NAME": r.get("name") or None, "OBJECTID": k + 1},
                                  "geometry": {"paths": [path]}})
            return self._json({"features": feats})
        if h == "services2.arcgis.com" and sp.path.endswith("/query"):
            env = box(*map(float, q["geometry"].split(",")))
            feats = []
            if int(q.get("resultOffset", "0")) == 0:
                for k, (a, b, c, d) in enumerate(self.sc.get("structures", [])):
                    ring = [self.ll(x, y) for x, y in ((a, b), (c, b), (c, d), (a, d), (a, b))]
                    if Polygon(ring).intersects(env):
                        feats.append({"attributes": {"OBJECTID": k + 1}, "geometry": {"rings": [ring]}})
            return self._json({"features": feats})
        if h == "imagery.nationalmap.gov":
            if sp.path.endswith("/query") or sp.path.endswith("/identify"):
                feats = []
                for fp in self.sc["footprints"]:
                    x0, y0, x1, y1 = fp["box"]
                    ring = [self.ll(x, y) for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0))]
                    feats.append({"attributes": {"Year": fp["year"], "Category": 1}, "geometry": {"rings": [ring]}})
                return self._json({"features": feats})
            if sp.path.endswith("/exportImage"):
                x0, y0, x1, y1 = map(float, q["bbox"].split(","))
                w, hgt = map(int, q["size"].split(","))
                arr = self.render(x0 - self.ox, y0 - self.oy, x1 - self.ox, y1 - self.oy, w, hgt, int(q["imageSR"]))
                b = io.BytesIO()
                Image.fromarray(arr).save(b, "TIFF")
                return 200, {"content-type": "image/tiff"}, b.getvalue()
        return 404, {}, b""

    def render(self, x0, y0, x1, y1, w, hgt, epsg):
        if epsg != self.epsg:
            raise AssertionError("unexpected projection")
        xs = x0 + (np.arange(w) + 0.5) * (x1 - x0) / w
        ys = y1 - (np.arange(hgt) + 0.5) * (y1 - y0) / hgt
        X, Y = np.meshgrid(xs, ys)
        col = self.sc["colours"]
        img = np.zeros((hgt, w, 4), np.float32)
        img[:] = col["veg"]
        for r in self.sc["roads"]:
            poly = LineString(r["line"]).buffer(HALF_WIDTH_M[r["mtfcc"]], cap_style="flat")
            img[contains_xy(poly, X, Y)] = col["asphalt"]
        for f in self.sc["patches"]:
            a, b, c, d = f["box"]
            img[(X >= a) & (X < c) & (Y >= b) & (Y < d)] = col[f["surface"]]
        rng = np.random.default_rng(int(abs(x0) * 7 + abs(y0) * 13) % 2**32)
        img += rng.integers(-4, 5, size=img.shape)
        return np.clip(img, 1, 255).astype(np.uint8)


def selftest():
    tdir = os.path.join(TOOL_DIR, "tests")
    before = sorted(os.listdir(tdir))
    tmp = tempfile.mkdtemp(prefix="kpc_pulloffs_selftest_")
    ok, msgs = True, []

    def check(cond, what):
        nonlocal ok
        msgs.append(("ok   " if cond else "FAIL ") + what)
        ok = ok and bool(cond)

    def no_net(*a, **k):
        raise AssertionError("the selftest tried to use the network")
    import requests
    real_get = requests.Session.get
    requests.Session.get = no_net
    try:
        fake = FakeWeb(os.path.join(tdir, "scene.json"))
        out = os.path.join(tmp, "out")
        base = ["--parks", os.path.join(tdir, "parks.json"), "--access", os.path.join(tdir, "access.json"),
                "--pictures", os.path.join(tdir, "pictures_index.json"), "--out", out, "--areas", "US-KY",
                "--cache", os.path.join(tmp, "cache")]
        nosleep = lambda s: None
        code = run(parse_args(base + ["--max-minutes", "0"]), transport=fake, sleep=nosleep)
        check(code == 3, f"--max-minutes 0: exit 3, work left (got {code})")
        code = run(parse_args(base + ["--resume"]), transport=fake, sleep=nosleep)
        check(code == 0, f"--resume: finishes with exit 0 (got {code})")
        exp = json.load(open(os.path.join(tdir, "expected_output.json"), encoding="utf-8"))
        got_p = os.path.join(out, "pulloffs", "US-KY.json")
        got = json.load(open(got_p, encoding="utf-8")) if os.path.exists(got_p) else {}
        check(sorted(got) == sorted(exp["refs_with_output"]),
              f"parks in pulloffs/US-KY.json {sorted(got)} (no outline / robots-blocked / other area = nothing)")
        for ref, rows_exp in exp["rows"].items():
            rows = got.get(ref, [])
            check(len(rows) == len(rows_exp), f"{ref}: {len(rows)} candidate(s), expected {len(rows_exp)}")
            for e in rows_exp:
                m = [r for r in rows if abs(r["lat"] - e["lat"]) < 7e-5 and abs(r["lon"] - e["lon"]) < 9e-5]
                check(len(m) == 1, f"{ref}: {e['case']}")
                if not m:
                    continue
                r = m[0]
                check(r["inside"] == e["inside"] and abs(r["dist_out_m"] - e["dist_out_m"]) <= 10,
                      f"   inside={r['inside']} dist_out_m={r['dist_out_m']} (expected {e['inside']}, {e['dist_out_m']})")
                check(abs(r["score"] - e["score"]) <= 0.05, f"   score {r['score']} (expected {e['score']})")
                check(r["road_name"] == e["road_name"] and r["road_class"] == e["road_class"],
                      f"   road {r['road_name']} {r['road_class']}")
                check(r["photo_year"] == e["photo_year"], f"   photo_year {r['photo_year']}")
                for phrase in e["why_has"]:
                    check(phrase in r["why"], f"   why has {phrase!r}")
        allrows = [r for v in got.values() for r in v]
        check(bool(allrows) and all(r.get("source_url") and re.match(r"^\d{4}-\d{2}-\d{2}$", r.get("read_date", ""))
                                    and r.get("why") for r in allrows),
              "every row has source_url, read_date (YYYY-MM-DD) and why")
        check(all("parking" not in r["why"].lower() or "possible" in r["why"].lower() for r in allrows),
              "never says 'parking' without 'possible'")
        for r in allrows:
            im = Image.open(os.path.join(out, "pulloffs", r["chip"]))
            a = np.array(im.convert("RGB")).astype(int)
            red = int(((a[..., 0] > 190) & (a[..., 1] < 70) & (a[..., 2] < 70)).sum())
            yel = int(((a[..., 0] > 190) & (a[..., 1] > 170) & (a[..., 2] < 90)).sum())
            wht = int(((a[..., 0] > 230) & (a[..., 1] > 230) & (a[..., 2] > 230)).sum())
            check(im.format == "JPEG" and max(im.size) <= 400 and red > 50 and wht > 50 and (yel > 50 or r["dist_out_m"] > 150),
                  f"chip {r['chip']}: JPEG {im.size}, red patch {red} px, white road {wht} px, yellow park line {yel} px")
        log = open(os.path.join(out, "work", "log", "kept_out.jsonl"), encoding="utf-8").read()
        for phrase in exp["kept_out_has"]:
            check(phrase in log, f"kept out (log only): {phrase!r}")
        rev = open(os.path.join(out, "pulloffs", "review.md"), encoding="utf-8").read()
        check(NOTICE_SHORT in rev, "review.md carries the SHORT information notice")
        sc = [float(x) for x in re.findall(r"— score ([0-9.]+)", rev)]
        check(sc == sorted(sc, reverse=True) and len(sc) == len(allrows), f"review.md is best first {sc}")
        rep = open(os.path.join(out, "report.md"), encoding="utf-8").read()
        check(exp["report_has"] in rep, f"report.md recall line: {exp['report_has']!r}")
        check("robots.txt does not allow" in rep and not any("/private/" in c for c in fake.calls),
              "robots.txt Disallow obeyed (no request to the blocked path) and reported")
        check(all(Net.host(c) in ("tigerweb.geo.census.gov", "imagery.nationalmap.gov", "services2.arcgis.com",
                                  "data.example.gov")
                  for c in fake.calls), "only TIGERweb, NAIP, FEMA USA Structures and the agency host were asked")
        check(sorted(os.listdir(tdir)) == before, "nothing written outside --out / --cache")
        slept = []
        n2 = Net("KPC park tools (selftest)", os.path.join(tmp, "c2"), transport=fake, sleep=slept.append)
        n2.robots["busy.example.gov"] = True
        try:
            n2.get("https://busy.example.gov/x")
            check(False, "429 should fail")
        except FetchError as e:
            check("resting" in str(e) and sum(1 for s in slept if s >= 15) == 3, f"429: 3 retries, then host resting ({e})")
        try:
            n2.get("https://busy.example.gov/y")
            check(False, "resting host asked again")
        except FetchError as e:
            check("resting" in str(e), "a resting host is not asked again this run")
        check(Net.never_use("https://" + NEVER_USE_HOSTS[3] + "/api") and not Net.never_use("https://" + ALLOWED_CLOUD[0] + "/a.zip"),
              "never-use guard refuses a banned host; a government file on cloud storage is allowed")
        src = open(os.path.abspath(__file__), encoding="utf-8").read().splitlines()
        g0 = next(i for i, l in enumerate(src) if l.startswith("# Install contract rule 6"))
        g1 = next(i for i, l in enumerate(src) if l.startswith("# ---- end of the never-use guard"))
        hits = [i + 1 for i, l in enumerate(src) if not (g0 <= i <= g1) and any(w in l.lower() for w in NEVER_USE_WORDS)]
        check(not hits, f"own code: banned source names appear only in the guard list (other lines: {hits})")
        pts = extract_points({"US-0001": [[37.5, -84.1, "Park: Parking"]],
                              "x": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-84.2, 37.6]}}})
        check(len(pts) == 2 and pts[0]["ref"] == "US-0001" and abs(pts[0]["lon"] + 84.1) < 1e-9 and abs(pts[1]["lat"] - 37.6) < 1e-9,
              "access reader: rows keyed by ref and GeoJSON points")
    except Exception:
        ok = False
        msgs.append("FAIL crash: " + traceback.format_exc())
    finally:
        requests.Session.get = real_get
        shutil.rmtree(tmp, ignore_errors=True)
    for m in msgs:
        print(m)
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv=None):
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if args.selftest:
        return selftest()
    try:
        return run(args)
    except KeyboardInterrupt:
        return 130
    except Exception:
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
