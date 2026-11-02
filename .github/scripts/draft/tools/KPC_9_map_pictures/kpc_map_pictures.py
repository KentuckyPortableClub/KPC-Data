#!/usr/bin/env python3
"""KPC 9: Map Picture Maker for the checkers.

Makes one small JPEG (about 900 x 700 px, under 150 KB) per item so the checker (chat 11) can grade by LOOKING:
  --questions <file>   one picture per waiting-room question (record read live from its layer)
  --fers <file>        one picture per live 2-fer row (stored patch + both parks' outlines)
  --refs A,B --key K   one picture per park outline from a key (US key, Kentucky key, Canada key or a world-bounds folder)

It is a HELPER: it only writes into --out (default pictures/). It never edits a key, an outline, a 2-fer file or the site.
Exit codes: 0 = done, 3 = not finished (run again with --resume), 2 = bad input.
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import hashlib
import io
import json
import math
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlencode, urlparse
from urllib.robotparser import RobotFileParser

import numpy as np
import requests
import shapely
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from pyproj import Geod, Transformer
from shapely.geometry import LineString, MultiLineString, MultiPolygon, Point, Polygon, box, shape
from shapely.ops import unary_union

TOOL = "KPC-map-pictures"
UA = f"{TOOL} (https://github.com/KentuckyPortableClub)"
W, H = 900, 700
MAX_BYTES = 150_000   # 'under 150 KB', counted the strict way
FT100 = 30.48            # R5: 100 ft in metres
YARDS50 = 45.72          # R9: 50 yards in metres
M_PER_YARD = 0.9144
ACRE_M2 = 4046.8564224
GEOD = Geod(ellps="WGS84")
TO_MERC = Transformer.from_crs(4326, 3857, always_xy=True)
FROM_MERC = Transformer.from_crs(3857, 4326, always_xy=True)
R0 = 156543.03392804097  # web mercator metres per pixel at zoom 0 (256 px tiles)
ORIGIN = 20037508.342789244

PADUS = "https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0"
CPCAD = "https://maps-cartes.ec.gc.ca/arcgis/rest/services/CWS_SCF/CPCAD/MapServer/0"
NHD = "https://hydro.nationalmap.gov/arcgis/rest/services/nhd/MapServer"   # USGS National Hydrography Dataset
NHD_WATER_LAYERS = (9, 12)   # Area - Large Scale (wide rivers), Waterbody - Large Scale (lakes / reservoirs)
POTA_PARK = "https://api.pota.app/park/{ref}"
NATURAL_EARTH = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_coastline.geojson"
NATURAL_EARTH_LAKES = NATURAL_EARTH.replace("ne_50m_coastline", "ne_50m_lakes")

# Agency layers the US key may name by id prefix (the same table the club's map uses); us-key/layers.json adds more.
XMAP = {
    "fws": ["https://services.arcgis.com/QVENGdaPbd4LUkLV/arcgis/rest/services/FWSInterest_Simplified_Authoritative/FeatureServer/0/query", "ORGNAME", "U.S. Fish & Wildlife Service"],
    "wld": ["https://apps.fs.usda.gov/arcx/rest/services/EDW/EDW_Wilderness_02/MapServer/0/query", "wildernessname", "National Wilderness Preservation System"],
    "hma": ["https://gis.blm.gov/arcgis/rest/services/range/BLM_Natl_WHB/MapServer/0/query", "HMA_NAME", "Bureau of Land Management"],
    "rma": ["https://gis.blm.gov/arcgis/rest/services/recreation/BLM_Natl_Recreation/MapServer/9/query", "FET_NAME", "Bureau of Land Management"],
    "rst": ["https://gis.blm.gov/arcgis/rest/services/recreation/BLM_Natl_Recs_poly/MapServer/0/query", "FET_NAME", "Bureau of Land Management"],
    "nca": ["https://gis.blm.gov/arcgis/rest/services/lands/BLM_Natl_NLCS_NM_NCA_poly/MapServer/0/query", "NCA_NAME", "Bureau of Land Management"],
    "wsa": ["https://gis.blm.gov/arcgis/rest/services/lands/BLM_Natl_NLCS_WLD_WSA/MapServer/1/query", "NLCS_NAME", "Bureau of Land Management"],
    "wbl": ["https://gis.blm.gov/arcgis/rest/services/lands/BLM_Natl_NLCS_WLD_WSA/MapServer/0/query", "NLCS_NAME", "Bureau of Land Management"],
    "odw": ["https://services1.arcgis.com/jRf8jjFwxedITdFe/arcgis/rest/services/Public_WMA_Boundaries/FeatureServer/1/query", "WMANAME", "Oklahoma Dept. of Wildlife Conservation"],
}

# Kentucky key layer keys -> the club's saved Kentucky outline files (same table as the club's map, kpc-bounds.js).
KY_FILES = {
    "bstate": "ky-state-parks.geojson", "bwma": "ky-hunting-areas.geojson", "bsnp": "ky-nature-preserves.geojson",
    "bsna": "ky-natural-areas.geojson", "bdbnf": "ky-dbnf.geojson", "bdbnfo": "ky-dbnf-owned.geojson",
    "bnps": "ky-nps.geojson", "bwild": "ky-wild-rivers.geojson", "bwilder": "ky-wilderness.geojson",
    "bfws": "ky-fws.geojson", "bpad": "ky-padus-parks.geojson",
}
KY_PROCLAMATION = {"bdbnf"}   # rule 3: a proclamation line is never the park

# Government basemaps only (never OSM / Google).
TILES = {
    "usgs": {"url": "https://basemap.nationalmap.gov/arcgis/rest/services/USGSTopo/MapServer/tile/{z}/{y}/{x}",
             "credit": "Base map: USGS The National Map (USGSTopo)", "maxz": 16},
    "usgs-imagery": {"url": "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryTopo/MapServer/tile/{z}/{y}/{x}",
                     "credit": "Base map: USGS The National Map (USGSImageryTopo)", "maxz": 16},
    "nrcan": {"url": "https://maps-cartes.services.geo.ca/server2_serveur2/rest/services/BaseMaps/CBMT_CBCT_GEOM_3857/MapServer/tile/{z}/{y}/{x}",
              "credit": "Base map: Natural Resources Canada CBMT", "maxz": 15,
              "alt": ["https://geoappext.nrcan.gc.ca/arcgis/rest/services/BaseMaps/CBMT_CBCT_GEOM_3857/MapServer/tile/{z}/{y}/{x}"]},
    "swisstopo": {"url": "https://wmts.geo.admin.ch/1.0.0/ch.swisstopo.pixelkarte-farbe/default/current/3857/{z}/{x}/{y}.jpeg",
                  "credit": "Base map: (c) swisstopo", "maxz": 18},
    "ign-fr": {"url": "https://data.geopf.fr/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=GEOGRAPHICALGRIDSYSTEMS.PLANIGNV2&STYLE=normal&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&FORMAT=image/png",
               "credit": "Base map: (c) IGN France Geoplateforme", "maxz": 18},
    "basemap-at": {"url": "https://mapsneu.wien.gv.at/basemap/geolandbasemap/normal/google3857/{z}/{y}/{x}.png",
                   "credit": "Base map: basemap.at", "maxz": 19},
}
PLAIN_CREDIT = "Plain background; coastlines and lakes: Natural Earth"
COUNTRY_TILES = {"US": "usgs", "K": "usgs", "CA": "nrcan", "VE": "nrcan", "VA": "nrcan", "CH": "swisstopo", "HB": "swisstopo",
                 "FR": "ign-fr", "F": "ign-fr", "AT": "basemap-at", "OE": "basemap-at"}

GOLD, BLUE, GREEN, PURPLE = (230, 170, 0), (30, 100, 230), (20, 150, 60), (150, 60, 190)
PARK_COLOURS = [GOLD, BLUE, GREEN, PURPLE]
GREY, RED, ORANGE, BAND = (110, 110, 110), (220, 20, 20), (255, 140, 0), (200, 0, 120)


class SourceDown(Exception):
    """A source could not be read (logged as SOURCE DOWN, retried next run)."""


class BadInput(Exception):
    """The input files are missing or not in the club's shape (exit 2)."""


def today() -> str:
    return dt.date.today().isoformat()


def log(msg: str) -> None:
    print(msg, flush=True)


# ------------------------------------------------------------------ polite web reading
class Http:
    """At most 1 request per second per host, our User-Agent, back-off on 429 / 5xx, robots.txt obeyed, disk cache with a date."""

    def __init__(self, cache_dir: Path, offline: bool = False, min_gap: float = 1.0, session=None, sleep=time.sleep, clock=time.monotonic):
        self.cache = Path(cache_dir)
        self.offline = offline
        self.min_gap = min_gap
        self.s = session or requests.Session()
        self.s.headers["User-Agent"] = UA
        self.sleep, self.clock = sleep, clock
        self.last: dict = {}
        self.robots: dict = {}
        self.failed_hosts: collections.Counter = collections.Counter()

    def _wait(self, host: str) -> None:
        now = self.clock()
        gap = self.last.get(host, -1e9) + self.min_gap - now
        if gap > 0:
            self.sleep(gap)
        self.last[host] = self.clock()

    def robots_ok(self, url: str) -> bool:
        u = urlparse(url)
        base = f"{u.scheme}://{u.netloc}"
        if base not in self.robots:
            rp = None
            if not self.offline:
                try:
                    self._wait(u.netloc)
                    r = self.s.get(base + "/robots.txt", timeout=20)
                    if r.status_code == 200 and "html" not in r.headers.get("content-type", "").lower():
                        rp = RobotFileParser()
                        rp.parse(r.text.splitlines())
                except requests.RequestException:
                    rp = None   # no robots file we can read = allowed (RFC 9309)
            self.robots[base] = rp
        rp = self.robots[base]
        return rp is None or rp.can_fetch(UA, url)

    @staticmethod
    def _key(url: str, params) -> str:
        full = url + ("?" + urlencode(sorted((params or {}).items())) if params else "")
        return hashlib.sha1(full.encode()).hexdigest()

    def get(self, url: str, params: dict | None = None, kind: str = "json", max_age_days: float = 30, tries: int = 4, timeout: int = 60):
        """Returns (data, read_date). Raises SourceDown."""
        key = self._key(url, params)
        sub = self.cache / ("tiles" if kind == "bytes" else "json")
        f = sub / (key + (".bin" if kind == "bytes" else ".json"))
        meta = sub / (key + ".date")
        if f.exists() and meta.exists():
            read = meta.read_text().strip()
            try:
                age = (dt.date.today() - dt.date.fromisoformat(read)).days
            except ValueError:
                age = 1e9
            if age <= max_age_days:
                return (f.read_bytes() if kind == "bytes" else json.loads(f.read_text())), read
        if self.offline:
            raise SourceDown(f"offline and not in the cache: {url}")
        host = urlparse(url).netloc
        if self.failed_hosts[host] >= 3:   # this host already failed 3 times this run: don't keep knocking
            raise SourceDown(f"{host}: down for this run (failed 3 times)")
        if not self.robots_ok(url):
            raise SourceDown(f"robots.txt asks bots not to read {url}")
        err = ""
        for i in range(tries):
            self._wait(host)
            try:
                r = self.s.get(url, params=params, timeout=timeout)
            except requests.RequestException as e:
                err = type(e).__name__
                self.sleep(min(60, 2 * 2 ** i))
                continue
            if r.status_code == 429 or r.status_code >= 500:
                err = f"HTTP {r.status_code}"
                ra = str(r.headers.get("Retry-After", ""))
                self.sleep(min(120, float(ra)) if ra.replace(".", "", 1).isdigit() else min(60, 2 * 2 ** i))
                continue
            if r.status_code != 200:
                err = f"HTTP {r.status_code}"
                break
            if kind == "bytes":
                data = r.content
                if not data or r.headers.get("content-type", "").startswith(("text/", "application/json")):
                    err = "not a picture tile"
                    break
                sub.mkdir(parents=True, exist_ok=True)
                f.write_bytes(data)
            else:
                try:
                    data = r.json()
                except ValueError:
                    err = "answer was not JSON"
                    break
                if isinstance(data, dict) and "error" in data and not data.get("features"):
                    e = data["error"]
                    err = f"layer said: {e.get('message', e) if isinstance(e, dict) else e}"
                    break
                sub.mkdir(parents=True, exist_ok=True)
                f.write_text(json.dumps(data))
            meta.write_text(today())
            return data, today()
        self.failed_hosts[host] += 1
        raise SourceDown(f"{host}: {err or 'no answer'}")


# ------------------------------------------------------------------ geometry helpers
def depth(x) -> int:
    d = 0
    while isinstance(x, (list, tuple)) and x:
        d += 1
        x = x[0]
    return d


def ring_area(r) -> float:
    return 0.5 * sum(r[i][0] * r[(i + 1) % len(r)][1] - r[(i + 1) % len(r)][0] * r[i][1] for i in range(len(r)))


def esri_to_shape(g: dict):
    """ArcGIS JSON geometry (rings / paths) -> shapely. Outer rings run clockwise, holes counter-clockwise."""
    if not g:
        return None
    if "rings" in g:
        outers, holes = [], []
        for r in g["rings"]:
            if len(r) < 4:
                continue
            (outers if ring_area(r) < 0 else holes).append(r)
        if not outers and holes:          # some servers send counter-clockwise outers
            outers, holes = holes, []
        polys = [[Polygon(o), []] for o in outers]
        polys.sort(key=lambda p: abs(p[0].area))   # a hole belongs to the SMALLEST outer around it (islands in lakes)
        for h in holes:
            hp = Polygon(h)
            for p in polys:
                try:
                    inside = p[0].covers(hp) if p[0].is_valid and hp.is_valid else p[0].contains(hp.representative_point())
                except shapely.errors.GEOSException:
                    inside = p[0].contains(hp.representative_point())
                if inside:
                    p[1].append(h)
                    break
        out = [Polygon(p[0].exterior.coords, p[1]) for p in polys]
        if not out:
            return None
        return out[0] if len(out) == 1 else MultiPolygon(out)
    if "paths" in g:
        ls = [LineString(p) for p in g["paths"] if len(p) >= 2]
        return ls[0] if len(ls) == 1 else MultiLineString(ls)
    if "x" in g and "y" in g:
        return Point(g["x"], g["y"])
    return None


def to_shape(g):
    """GeoJSON geometry or ArcGIS geometry -> valid shapely geometry (or None)."""
    if not g:
        return None
    try:
        s = shape(g) if "type" in g else esri_to_shape(g)
    except Exception:
        return None
    if s is None or s.is_empty:
        return None
    if not s.is_valid:
        s = shapely.make_valid(s)
    return s


def rings_to_shape(rings):
    """A club 'r' / 'shape' list: one ring, a list of rings, or a list of polygons. A ring inside another ring is a hole."""
    d = depth(rings)
    if d == 2:
        rings = [rings]
    elif d == 4:
        polys = [rings_to_shape(p) for p in rings]
        polys = [p for p in polys if p is not None]
        return unary_union(polys) if polys else None
    polys = []
    for r in rings:
        if len(r) < 4:
            continue
        p = Polygon(r)
        if not p.is_valid:
            p = shapely.make_valid(p)
        hole_of = next((i for i, q in enumerate(polys) if q.contains(p.representative_point()) and q.area > p.area), None)
        if hole_of is not None:
            polys[hole_of] = polys[hole_of].difference(p)
        else:
            polys.append(p)
    if not polys:
        return None
    return unary_union(polys)


def club_shape(coords):
    """A 2-fer row's 'shape': a closed ring = an area patch; an open list of points = a line (trail stretch)."""
    if not coords:
        return None
    d = depth(coords)
    if d == 2:
        if len(coords) >= 4 and list(coords[0]) == list(coords[-1]):
            return rings_to_shape(coords)
        return LineString(coords) if len(coords) >= 2 else None
    if d == 3:
        if all(len(r) >= 4 and list(r[0]) == list(r[-1]) for r in coords):
            return rings_to_shape(coords)
        return MultiLineString([c for c in coords if len(c) >= 2])
    return rings_to_shape(coords)


def local_proj(lon: float, lat: float):
    """Metric projection centred on a spot (azimuthal equidistant): good for distances and buffers near that spot."""
    crs = f"+proj=aeqd +lat_0={lat} +lon_0={lon} +datum=WGS84 +units=m"
    return Transformer.from_crs(4326, crs, always_xy=True), Transformer.from_crs(crs, 4326, always_xy=True)


def tx(geom, transformer):
    def f(a):
        x, y = transformer.transform(a[:, 0], a[:, 1])
        return np.column_stack([x, y])
    return shapely.transform(geom, f)


def acres(geom) -> float:
    if geom is None or geom.is_empty or geom.area == 0:
        return 0.0
    polys = polys_of(geom)
    return sum(abs(GEOD.geometry_area_perimeter(p)[0]) for p in polys) / ACRE_M2


def pin_distance_m(geom, lon: float, lat: float) -> float:
    """0 when the pin is inside the outline, else metres to the nearest edge."""
    if geom is None or geom.is_empty:
        return float("nan")
    if geom.covers(Point(lon, lat)):
        return 0.0
    fwd, _ = local_proj(lon, lat)
    return tx(geom, fwd).distance(Point(0, 0))


def width_m(geom) -> float:
    """How wide the patch is across at its widest point (2 x the biggest circle that fits), in metres."""
    if geom is None or geom.is_empty or geom.area == 0:
        return 0.0
    c = geom.centroid
    fwd, _ = local_proj(c.x, c.y)
    g = tx(geom, fwd)
    best = 0.0
    for p in sorted(polys_of(g), key=lambda p: -p.area)[:5]:
        if hasattr(shapely, "maximum_inscribed_circle"):
            r = shapely.maximum_inscribed_circle(p, 0.5).length
        else:   # binary search on an inward buffer
            lo, hi = 0.0, math.sqrt(p.area)
            for _ in range(20):
                mid = (lo + hi) / 2
                lo, hi = (mid, hi) if not p.buffer(-mid).is_empty else (lo, mid)
            r = lo
        best = max(best, 2 * r)
    return best


def metric_buffer(geom, metres: float):
    c = geom.centroid
    fwd, back = local_proj(c.x, c.y)
    return tx(tx(geom, fwd).buffer(metres, 8), back)


def lines_of(g):
    """Every line in a geometry: polygon edges and lines (as coordinate lists)."""
    out = []
    if g is None or g.is_empty:
        return out
    if isinstance(g, Polygon):
        out.append(list(g.exterior.coords))
        out += [list(r.coords) for r in g.interiors]
    elif isinstance(g, LineString):
        out.append(list(g.coords))
    elif hasattr(g, "geoms"):
        for p in g.geoms:
            out += lines_of(p)
    return out


def polys_of(g):
    if g is None or g.is_empty:
        return []
    if isinstance(g, Polygon):
        return [g]
    if hasattr(g, "geoms"):
        return [q for p in g.geoms for q in polys_of(p)]
    return []


# ------------------------------------------------------------------ tile maths
def lonlat_to_merc(lon, lat):
    return TO_MERC.transform(lon, max(-85.0, min(85.0, lat)))


def zoom_for(res_m_per_px: float, maxz: int) -> int:
    z = math.ceil(math.log2(R0 / max(res_m_per_px, 1e-6)))
    return max(0, min(maxz, z))


def tile_range(x0, y0, x1, y1, z):
    """Tile columns / rows (XYZ scheme) covering a mercator box at zoom z."""
    n = 2 ** z
    size = 2 * ORIGIN / n
    clamp = lambda v: max(0, min(n - 1, v))
    return (clamp(int(math.floor((x0 + ORIGIN) / size))), clamp(int(math.floor((ORIGIN - y1) / size))),
            clamp(int(math.floor((x1 + ORIGIN) / size))), clamp(int(math.floor((ORIGIN - y0) / size))))


def view_for(bounds_lonlat, min_size_m: float = 600.0, pad: float = 0.15, w: int = W, h: int = H):
    """A mercator view (x0, y0, x1, y1, metres-per-pixel) around a lon/lat box, padded, keeping the picture's shape."""
    lo0, la0, lo1, la1 = bounds_lonlat
    x0, y0 = lonlat_to_merc(lo0, la0)
    x1, y1 = lonlat_to_merc(lo1, la1)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    k = 1 / max(0.05, math.cos(math.radians((la0 + la1) / 2)))   # ground metres -> mercator metres
    bw = max((x1 - x0) * (1 + 2 * pad), min_size_m * k)
    bh = max((y1 - y0) * (1 + 2 * pad), min_size_m * k)
    res = max(bw / w, bh / h)
    return (cx - res * w / 2, cy - res * h / 2, cx + res * w / 2, cy + res * h / 2, res)


def view_lonlat(view):
    a = FROM_MERC.transform(view[0], view[1])
    b = FROM_MERC.transform(view[2], view[3])
    return (a[0], a[1], b[0], b[1])


def basemap_for(ref: str) -> str:
    return COUNTRY_TILES.get((ref or "").split("-")[0].upper(), "plain")


# ------------------------------------------------------------------ drawing
def font(size: int, bold: bool = False):
    names = ["DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf", "LiberationSans-Bold.ttf" if bold else "LiberationSans-Regular.ttf"]
    for d in ["/usr/share/fonts/truetype/dejavu", "/usr/share/fonts/truetype/liberation", "/usr/share/fonts/dejavu", "/Library/Fonts", "C:/Windows/Fonts"]:
        for n in names:
            p = Path(d) / n
            if p.exists():
                return ImageFont.truetype(str(p), size)
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def dashed_line(draw, pts, colour, width=2, dash=9.0, gap=6.0):
    """Draw a dashed polyline (pixel coordinates)."""
    on, left = True, dash
    for (xa, ya), (xb, yb) in zip(pts[:-1], pts[1:]):
        seg = math.hypot(xb - xa, yb - ya)
        pos = 0.0
        while seg - pos > 1e-9:
            step = min(left, seg - pos)
            t0, t1 = pos / seg, (pos + step) / seg
            if on:
                draw.line([(xa + (xb - xa) * t0, ya + (yb - ya) * t0), (xa + (xb - xa) * t1, ya + (yb - ya) * t1)], fill=colour, width=width)
            pos += step
            left -= step
            if left <= 1e-9:
                on = not on
                left = dash if on else gap


def nice_scale(ground_m_per_px: float, max_px: float = 180):
    """A round scale-bar length (metres) and its width in pixels."""
    target = ground_m_per_px * max_px
    p = 10 ** math.floor(math.log10(target))
    for m in (5, 2, 1):
        if m * p <= target:
            return m * p, m * p / ground_m_per_px
    return p, p / ground_m_per_px


def fmt_dist(m: float) -> str:
    if m >= 1000:
        return f"{m / 1000:g} km ({m / 1609.344:.2g} mi)"
    return f"{m:g} m ({m / 0.3048:.0f} ft)"


class Canvas:
    def __init__(self, view, w=W, h=H):
        self.view, self.w, self.h = view, w, h
        self.x0, self.y1, self.res = view[0], view[3], view[4]

    def px(self, geom_ll):
        """lon/lat geometry -> pixel geometry."""
        def f(a):
            x, y = TO_MERC.transform(a[:, 0], np.clip(a[:, 1], -85, 85))
            return np.column_stack([(x - self.x0) / self.res, (self.y1 - y) / self.res])
        return shapely.transform(geom_ll, f)

    def pt(self, lon, lat):
        x, y = lonlat_to_merc(lon, lat)
        return (x - self.x0) / self.res, (self.y1 - y) / self.res

    def clip(self, geom_ll, margin=0.6):
        lo0, la0, lo1, la1 = view_lonlat(self.view)
        dx, dy = (lo1 - lo0) * margin, (la1 - la0) * margin
        b = box(lo0 - dx, la0 - dy, lo1 + dx, la1 + dy)
        try:
            return geom_ll.intersection(b)
        except Exception:
            return shapely.make_valid(geom_ll).intersection(b)


def draw_basemap(http: Http, view, source: str, w: int, h: int, warnings: list, failed_sources: collections.Counter, max_tiles: int = 48):
    """Stitch government tiles for the view; falls back to a plain background (with Natural Earth coastlines)."""
    x0, y0, x1, y1, res = view
    if source in TILES:
        t = TILES[source]
        z = zoom_for(res, t["maxz"])
        while z > 0:
            a, b, c, d = tile_range(x0, y0, x1, y1, z)
            if (c - a + 1) * (d - b + 1) <= max_tiles:
                break
            z -= 1
        a, b, c, d = tile_range(x0, y0, x1, y1, z)
        size = 2 * ORIGIN / 2 ** z
        whys = []
        for url in [t["url"]] + t.get("alt", []):   # the agency's main tile server, then its other server
            mosaic = Image.new("RGB", ((c - a + 1) * 256, (d - b + 1) * 256), (240, 240, 236))
            got = bad = 0
            why = ""
            for ty in range(b, d + 1):
                for tcol in range(a, c + 1):
                    try:
                        data, _ = http.get(url.format(z=z, x=tcol, y=ty), kind="bytes", max_age_days=30, tries=3, timeout=30)
                        tile = Image.open(io.BytesIO(data)).convert("RGB")
                        if tile.size != (256, 256):
                            tile = tile.resize((256, 256))
                        mosaic.paste(tile, ((tcol - a) * 256, (ty - b) * 256))
                        got += 1
                    except Exception as e:
                        bad += 1
                        why = why or (str(e) if isinstance(e, SourceDown) else type(e).__name__)
                        if "robots.txt" in why or (got == 0 and bad >= 3):   # robots says no, or the server is down: stop knocking
                            bad += (c - a + 1) * (d - b + 1) - got - bad
                            break
                if "robots.txt" in why or (got == 0 and bad >= 3):
                    break
            if got and bad <= got:
                mx0, my1, scale = -ORIGIN + a * size, ORIGIN - b * size, 256 / size
                crop = ((x0 - mx0) * scale, (my1 - y1) * scale, (x1 - mx0) * scale, (my1 - y0) * scale)
                img = mosaic.resize((w, h), Image.LANCZOS, box=crop)
                if bad:
                    warnings.append(f"{bad} map tiles from {source} did not load")
                return img, t["credit"]
            host = urlparse(url).netloc
            why = why[len(host) + 2:] if why.startswith(host + ": ") else why
            whys.append(f"{host}: " + ("its robots.txt asks bots not to read it" if "robots.txt" in why else why or "no answer"))
        failed_sources[source] += 1
        warnings.append(f"tile source {source} failed ({'; '.join(whys)}), so a plain background is used")
    img = Image.new("RGB", (w, h), (244, 242, 234))
    try:
        feats = []
        for src in (NATURAL_EARTH, NATURAL_EARTH_LAKES):   # sea coasts + big lakes (the Great Lakes are not "coast")
            ne, _ = http.get(src, max_age_days=365, tries=2)
            feats += ne.get("features", [])
        cv = Canvas(view, w, h)
        dr = ImageDraw.Draw(img)
        vb = box(*view_lonlat(view)).buffer(0.5)
        for f in feats:
            g = to_shape(f.get("geometry"))
            if g is None or not g.intersects(vb):
                continue
            for ln in lines_of(cv.px(g.intersection(vb))):
                dr.line(ln, fill=(70, 110, 160), width=1)
    except Exception:
        warnings.append("Natural Earth coastlines / lakes did not load")
    return img, PLAIN_CREDIT


def fit_text(draw, text: str, fnt, max_w: int) -> str:
    if draw.textlength(text, font=fnt) <= max_w:
        return text
    while text and draw.textlength(text + "...", font=fnt) > max_w:
        text = text[:-1]
    return text + "..."


def to_jpeg(img: Image.Image) -> bytes:
    """JPEG under 150 KB: lower the quality step by step until it fits."""
    out = img.convert("RGB")
    data = b""
    for q in (82, 72, 62, 52, 42, 32):
        buf = io.BytesIO()
        out.save(buf, "JPEG", quality=q, optimize=True, progressive=True)
        data = buf.getvalue()
        if len(data) <= MAX_BYTES:
            return data
    soft = out   # still too big (very busy map): soften the fine detail a little, never shrink the picture
    for radius in (0.6, 1.0, 1.6, 2.4):
        soft = out.filter(ImageFilter.GaussianBlur(radius))
        buf = io.BytesIO()
        soft.save(buf, "JPEG", quality=40, optimize=True, progressive=True)
        data = buf.getvalue()
        if len(data) <= MAX_BYTES:
            break
    return data


def render(http: Http, item: dict, failed_sources: collections.Counter, inset: bool = True) -> bytes:
    """Draw one picture. item keys: view_bounds, basemap, title1, title2, outlines, neighbours, patch, bands, lines, water, pins."""
    warnings = item.setdefault("warnings", [])
    view = view_for(item["view_bounds"], item.get("min_size_m", 600))
    img, credit = draw_basemap(http, view, item.get("basemap", "plain"), W, H, warnings, failed_sources)
    cv = Canvas(view)
    over = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    f_lab, f_small = font(12), font(11)

    if item.get("patch") is not None:   # the 2-fer patch: orange at 40 %
        mask = Image.new("L", (W, H), 0)
        md = ImageDraw.Draw(mask)
        for p in polys_of(cv.px(cv.clip(item["patch"]))):
            if len(p.exterior.coords) >= 3:
                md.polygon(list(p.exterior.coords), fill=255)
            for r in p.interiors:
                md.polygon(list(r.coords), fill=0)
        fill = Image.new("RGBA", (W, H), ORANGE + (0,))
        fill.putalpha(mask.point(lambda v: int(v * 0.4)))
        over = Image.alpha_composite(over, fill)
    od = ImageDraw.Draw(over)
    if item.get("patch") is not None:
        for ln in lines_of(cv.px(cv.clip(item["patch"]))):
            od.line(ln, fill=ORANGE + (255,), width=1)
    for nb in item.get("neighbours", []):          # neighbours: thin grey
        for ln in lines_of(cv.px(cv.clip(nb["geom"]))):
            od.line(ln, fill=GREY + (230,), width=1)
    for wg in item.get("water", []):               # the water's edge (river bank): thin blue
        for ln in lines_of(cv.px(cv.clip(wg))):
            od.line(ln, fill=(40, 120, 220, 220), width=1)
    for band in item.get("bands", []):             # the 100 ft band: dashed
        for ln in lines_of(cv.px(cv.clip(band["geom"]))):
            dashed_line(od, ln, band.get("colour", BAND) + (255,), width=2)
    for li in item.get("lines", []):
        for ln in lines_of(cv.px(cv.clip(li["geom"]))):
            od.line(ln, fill=li["colour"] + (255,), width=li.get("width", 2))
    for o in item.get("outlines", []):             # outline being graded: gold 2 px (blue / green for the other 2-fer parks)
        for ln in lines_of(cv.px(cv.clip(o["geom"]))):
            od.line(ln, fill=o["colour"] + (255,), width=o.get("width", 2), joint="curve")
    img = Image.alpha_composite(img.convert("RGBA"), over)
    d = ImageDraw.Draw(img)
    placed = []
    for nb in item.get("neighbours", [])[:25]:     # neighbour names
        try:
            rp = cv.clip(nb["geom"], margin=0).representative_point()
        except Exception:
            continue
        if rp.is_empty:
            continue
        x, y = cv.pt(rp.x, rp.y)
        if 0 < x < W - 40 and 60 < y < H - 30 and not (x < 90 and y < 115) and all(abs(x - a) > 60 or abs(y - b) > 14 for a, b in placed):
            d.text((x, y), fit_text(d, nb.get("name") or "", f_small, 170), font=f_small, fill=(70, 70, 70), anchor="mm", stroke_width=2, stroke_fill=(255, 255, 255))
            placed.append((x, y))
    for p in item.get("pins", []):                 # POTA pins: red dot + park number (never moved)
        x, y = cv.pt(p["lon"], p["lat"])
        if -5 <= x <= W + 5 and -5 <= y <= H + 5:
            d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=RED, outline=(255, 255, 255), width=2)
            d.text((x + 8, y - 8), p["label"], font=f_lab, fill=RED, stroke_width=2, stroke_fill=(255, 255, 255))
        else:                                      # pin off the picture: an arrow on the edge pointing at it
            cx, cy = W / 2, H / 2
            ang = math.atan2(y - cy, x - cx)
            ex = max(30, min(W - 30, cx + math.cos(ang) * (W / 2 - 24)))
            ey = max(80, min(H - 44, cy + math.sin(ang) * (H / 2 - 24)))
            d.polygon([(ex + 12 * math.cos(ang), ey + 12 * math.sin(ang)), (ex + 8 * math.cos(ang + 2.4), ey + 8 * math.sin(ang + 2.4)),
                       (ex + 8 * math.cos(ang - 2.4), ey + 8 * math.sin(ang - 2.4))], fill=RED)
            lab = p["label"] + " pin off picture"
            tw = d.textlength(lab, font=f_small)
            lx = max(4 + tw / 2, min(W - 4 - tw / 2, ex - 14 * math.cos(ang)))
            d.text((lx, ey - 14 * math.sin(ang)), lab, font=f_small, fill=RED, anchor="mm", stroke_width=2, stroke_fill=(255, 255, 255))
    d.rectangle([0, 0, W, 50], fill=(255, 255, 255, 235))   # title band
    d.text((8, 5), fit_text(d, item["title1"], font(15, True), W - 16), font=font(15, True), fill=(0, 0, 0))
    d.text((8, 28), fit_text(d, item["title2"], font(13), W - 16), font=font(13), fill=(30, 30, 30))
    nx, ny = 26, 62                                 # north arrow
    d.polygon([(nx, ny), (nx - 8, ny + 20), (nx, ny + 15), (nx + 8, ny + 20)], fill=(0, 0, 0))
    d.text((nx, ny + 30), "N", font=font(13, True), fill=(0, 0, 0), anchor="mm", stroke_width=2, stroke_fill=(255, 255, 255))
    ll = view_lonlat(view)                          # scale bar (ground distance at the centre)
    gm = view[4] * math.cos(math.radians((ll[1] + ll[3]) / 2))
    L, Lpx = nice_scale(gm)
    sx, sy = 12, H - 26
    d.rectangle([sx - 4, sy - 18, sx + max(Lpx, d.textlength(fmt_dist(L), font=f_small)) + 8, sy + 8], fill=(255, 255, 255, 220))
    d.rectangle([sx, sy - 3, sx + Lpx, sy + 3], fill=(0, 0, 0))
    d.rectangle([sx + Lpx / 2, sy - 3, sx + Lpx, sy + 3], fill=(255, 255, 255), outline=(0, 0, 0))
    d.text((sx, sy - 16), fmt_dist(L), font=f_small, fill=(0, 0, 0))
    tw = d.textlength(credit, font=f_small)         # tile credit in the corner
    d.rectangle([W - tw - 12, H - 18, W, H], fill=(255, 255, 255, 220))
    d.text((W - tw - 6, H - 16), credit, font=f_small, fill=(40, 40, 40))
    if inset:                                       # inset at 4x zoom-out, so the checker sees where it is
        try:
            iw, ih = 216, 168
            cxm, cym = (view[0] + view[2]) / 2, (view[1] + view[3]) / 2
            res4 = view[4] * 4 * W / iw
            v4 = (cxm - res4 * iw / 2, cym - res4 * ih / 2, cxm + res4 * iw / 2, cym + res4 * ih / 2, res4)
            ins, _ = draw_basemap(http, v4, item.get("basemap", "plain"), iw, ih, [], failed_sources, max_tiles=12)
            idr = ImageDraw.Draw(ins)
            cv4 = Canvas(v4, iw, ih)
            a, b = cv4.pt(ll[0], ll[3]), cv4.pt(ll[2], ll[1])
            idr.rectangle([a[0], a[1], b[0], b[1]], outline=RED, width=2)
            idr.rectangle([0, 0, iw - 1, ih - 1], outline=(0, 0, 0), width=1)
            img.paste(ins.convert("RGBA"), (W - iw - 8, 58))
        except Exception:
            warnings.append("the small locator map could not be drawn")
    return to_jpeg(img)


# ------------------------------------------------------------------ reading records
def arc_query(http: Http, layer: str, params: dict):
    """Query an ArcGIS layer; returns ([(shapely, properties)], read_date). GeoJSON first, ArcGIS JSON if the server can't."""
    url = layer.rstrip("/")
    if not url.endswith("/query"):
        url += "/query"
    base = {"outSR": 4326, "returnGeometry": "true", "outFields": "*"}
    base.update(params)
    try:
        j, read = http.get(url, dict(base, f="geojson"))
        if isinstance(j, dict) and "features" in j:
            return [(to_shape(f.get("geometry")), f.get("properties") or {}) for f in j["features"]], read
    except SourceDown as e:
        if "layer said" not in str(e) and "not JSON" not in str(e):
            raise
    j, read = http.get(url, dict(base, f="json"))
    return [(to_shape(f.get("geometry")), f.get("attributes") or {}) for f in j.get("features", [])], read


def layer_of(url: str) -> str:
    return re.sub(r"/query/?$", "", (url or "").rstrip("/"))


def name_from(props: dict, name_field=None) -> str:
    for k in [name_field, "Unit_Nm", "NAME_E", "NAME", "Name", "name", "ORGNAME", "PARK_NAME", "Loc_Nm"]:
        if k and props.get(k):
            return str(props[k])
    return ""


def acres_from(props: dict):
    for k in ["GIS_Acres", "ACRES", "Acres", "acres", "GISACRES", "GIS_ACRES", "TOTAL_ACRES", "O_AREA_HA"]:
        v = props.get(k)
        if isinstance(v, (int, float)) and v > 0:
            return v * 2.4710538 if k.endswith("_HA") else float(v)
    return None


def best_acres(rows):
    """Official acres from several records: add the pieces from the same source, then take the biggest source total
    (two sources describing the same park are not added together)."""
    by = collections.defaultdict(float)
    for rid, ac in rows:
        if not isinstance(ac, (int, float)) or ac <= 0:
            continue
        rid = str(rid)
        m = re.match(r"^[a-z]+", rid)
        src = rid.split(":")[0] if ":" in rid else (m.group(0) if m else "main")
        by[src] += ac
    return max(by.values()) if by else None


class Club:
    """Read-only access to the club's files (keys, outlines, trails, park info). Nothing here ever writes."""

    def __init__(self, data: Path, ky_outlines, http: Http):
        self.data, self.http, self.ky_dir = Path(data), http, (Path(ky_outlines) if ky_outlines else None)
        self._json: dict = {}
        self.layers = dict(XMAP)
        lp = self.data / "us-key" / "layers.json"
        if lp.exists():
            for k, v in self.load(lp).items():
                if isinstance(v, list) and v and k not in self.layers:
                    self.layers[k] = v
        self.parkinfo = {}
        if (self.data / "parkinfo").exists():
            for f in sorted((self.data / "parkinfo").glob("*.json")):
                for ref, row in (self.maybe(f) or {}).get("parks", {}).items():
                    self.parkinfo.setdefault(ref, (row, f.stem))

    def load(self, p):
        p = Path(p)
        if p not in self._json:
            try:
                self._json[p] = json.loads(p.read_text(encoding="utf-8"))
            except FileNotFoundError:
                raise BadInput(f"file not found: {p}")
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                raise BadInput(f"not readable JSON: {p} ({e})")
        return self._json[p]

    def maybe(self, p):
        try:
            return self.load(p) if Path(p).exists() else None
        except BadInput:
            return None

    def pin(self, ref: str):
        """POTA's own pin (never moved): POTA's park page first (cached 30 days), the club's parkinfo file if POTA is down."""
        try:
            j, read = self.http.get(POTA_PARK.format(ref=ref), max_age_days=30)
            if isinstance(j, dict) and j.get("latitude") is not None:
                return {"lat": float(j["latitude"]), "lon": float(j["longitude"]), "name": j.get("name", ""), "type": j.get("parktypeDesc", ""),
                        "src": POTA_PARK.format(ref=ref), "read": read}
        except SourceDown:
            pass
        if ref in self.parkinfo:
            row, st = self.parkinfo[ref]
            return {"lat": float(row[5]), "lon": float(row[6]), "name": row[0], "type": row[2], "src": f"parkinfo/{st}.json", "read": ""}
        return None

    def key_kind(self, key) -> str:
        if isinstance(key, dict) and isinstance(key.get("parks"), dict):
            first = next(iter(key["parks"].values()), {})
            if "tracts" in first:
                return "ky"
            return "ca" if "prov" in key else "us"
        return "world"

    def trail(self, ref: str):
        j = self.maybe(self.data / "trails" / f"{ref}.json")
        if not j:
            return None
        return to_shape(j.get("geometry") if j.get("type") == "Feature" else j)

    def ky_outline(self, ref: str, park: dict, sources: list, warnings: list):
        """Kentucky: the key's tracts -> the club's saved Kentucky outline files (never a proclamation line, rule 3)."""
        geoms, recs = [], []
        for t in park.get("tracts", []):
            lk, nm = t[0], t[1]
            if lk == "trl":
                tl = self.trail(ref)
                if tl is not None:
                    geoms.append(tl)
                    recs.append((nm, 0, "trail line"))
                    sources.append(f"trails/{ref}.json")
                continue
            if lk in KY_PROCLAMATION:
                continue
            fn = KY_FILES.get(lk)
            if not fn or not self.ky_dir or not (self.ky_dir / fn).exists():
                warnings.append(f"Kentucky outline file for '{lk}' not found (give --ky-outlines)")
                continue
            fc = self.load(self.ky_dir / fn)
            hits = [f for f in fc.get("features", []) if (f.get("properties") or {}).get("ref") == ref or
                    str((f.get("properties") or {}).get("NAME", "")).strip().lower() == nm.strip().lower()]
            for f in hits:
                g = to_shape(f.get("geometry"))
                if g is not None:
                    geoms.append(g)
            if hits:
                recs.append((nm, t[2], lk))
                sources.append(f"club file {fn}")
        return geoms, recs

    def us_records(self, m: list, sources: list, warnings: list, envelope=None, offset=None):
        """US key records read live: integer ids = PAD-US OBJECTIDs, prefixed ids = the agency layer (layers.json)."""
        groups = collections.defaultdict(list)
        for row in m:
            s = str(row[0])
            mm = re.match(r"^[a-z]+", s)
            pre = mm.group(0) if mm else ""
            groups[pre].append(s[len(pre):])
        out = []
        for pre, ids in groups.items():
            if pre and pre not in self.layers:
                warnings.append(f"no layer known for record prefix '{pre}'")
                continue
            url = self.layers[pre][0] if pre else PADUS
            for i in range(0, len(ids), 40):
                params = {"objectIds": ",".join(ids[i:i + 40])}
                if offset:
                    params["maxAllowableOffset"] = offset
                if envelope:
                    params.update({"geometry": ",".join(f"{v:.5f}" for v in envelope), "geometryType": "esriGeometryEnvelope", "inSR": 4326,
                                   "spatialRel": "esriSpatialRelIntersects"})
                try:
                    feats, read = arc_query(self.http, url, params)
                    sources.append(layer_of(url))
                    out += [(g, p, layer_of(url), read) for g, p in feats if g is not None]
                except SourceDown as e:
                    warnings.append(f"SOURCE DOWN: {e}")
        return out

    def ca_bounds(self, ref: str):
        j = self.maybe(self.data / "canada-bounds" / f"{ref}.json")
        if not j:
            return None, {}
        return to_shape(j.get("geometry")), j.get("properties", {})

    def park_outline(self, ref: str, sources: list, warnings: list, envelope=None, offset=None, key_hint=None):
        """(outline in lon/lat or None, info). Kentucky key -> US keys (live) -> trail line; Canada bounds -> CPCAD live."""
        info = {"name": "", "grade": "", "type": "", "records": [], "record_acres": None, "key_acres": None}
        geoms = []
        if ref.startswith("US-"):
            ky = self.maybe(self.data / "ky-answer-key.json")
            if ky and ref in ky.get("parks", {}) and key_hint in (None, "ky"):
                p = ky["parks"][ref]
                gs, recs = self.ky_outline(ref, p, sources, warnings)
                geoms += gs
                info.update(name=p.get("n", ""), type=p.get("t", ""), grade="Kentucky key", records=[r[0] for r in recs],
                            record_acres=max([r[1] for r in recs if r[1]] or [0]) or None)
            if not geoms and (self.data / "us-key").exists():
                for f in sorted((self.data / "us-key").glob("US-*.json")):
                    k = self.maybe(f)
                    p = (k or {}).get("parks", {}).get(ref)
                    if p and p.get("m"):
                        recs = self.us_records(p["m"], sources, warnings, envelope, offset)
                        geoms += [r[0] for r in recs]
                        info.update(name=p.get("n", ""), type=p.get("t", ""), grade=p.get("g", ""), records=sorted({r[1] for r in p["m"]}),
                                    record_acres=best_acres([(str(r[0]), r[2]) for r in p["m"]]), key_acres=p.get("ac"))
                        break
            if not geoms:
                tl = self.trail(ref)
                if tl is not None:
                    geoms.append(tl)
                    info["records"].append("trail line (club file)")
                    sources.append(f"trails/{ref}.json")
        elif ref.startswith("CA-"):
            g, props = self.ca_bounds(ref)
            if g is not None:
                geoms.append(g)
                sources.append(f"canada-bounds/{ref}.json ({props.get('srcShort') or props.get('src', '')})")
                info.update(name=props.get("name", ""), type=props.get("type", ""), records=[props.get("cpcad", "")])
            for f in sorted((self.data / "ca-key").glob("CA-*.json")) if (self.data / "ca-key").exists() else []:
                p = (self.maybe(f) or {}).get("parks", {}).get(ref)
                if not p:
                    continue
                info.update(name=info["name"] or p.get("n", ""), type=info["type"] or p.get("t", ""), grade=p.get("g", ""),
                            record_acres=best_acres([(str(r[0]), r[2]) for r in p.get("m", [])]))
                info["records"] = [r for r in info["records"] if r] or sorted({r[1] for r in p.get("m", [])})
                ids = [str(r[0]) for r in p.get("m", []) if isinstance(r[0], int)]
                if not geoms and ids:
                    try:
                        feats, _ = arc_query(self.http, CPCAD, {"objectIds": ",".join(ids)})
                        geoms += [g for g, _ in feats if g is not None]
                        sources.append(CPCAD)
                    except SourceDown as e:
                        warnings.append(f"SOURCE DOWN: CPCAD ({e})")
                break
        return (unary_union(geoms) if geoms else None), info


# ------------------------------------------------------------------ captions + checks
def pin_text(dist: float) -> str:
    if dist != dist:
        return "pin: no outline to test"
    if dist == 0:
        return "pin inside"
    return f"pin {dist:,.0f} m outside" if dist < 10000 else f"pin {dist / 1000:,.1f} km outside"


def outline_warnings(geom, rec_acres, dist) -> list:
    """Warnings when something looks wrong: pin > 2 km outside, outline tiny vs the record acres, empty geometry."""
    w = []
    if geom is None or geom.is_empty:
        return ["the record geometry is empty"]
    if dist == dist and dist > 2000:
        w.append(f"POTA's pin is {dist / 1000:.1f} km outside the outline")
    a = acres(geom)
    if rec_acres and geom.area > 0 and a < rec_acres / 5:
        w.append(f"the outline is tiny ({fmt_ac(a)} ac) next to the record's {fmt_ac(rec_acres)} ac")
    return w


def is_live(row: dict) -> bool:
    """A live 2-fer row: not dropped, not merged into another row, not 'not sure' (NOT SURE = kept out)."""
    return not str(row.get("status", "")).lower().startswith(("dropped", "merged", "not sure"))


def safe_id(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9._+-]+", "_", s).strip("_")[:120]


def fmt_ac(a) -> str:
    return "?" if not a else (f"{a:,.0f}" if a >= 10 else f"{a:,.1f}")


def pin_in_view(bounds, pin, dist, geom):
    """Stretch the view to show the pin, unless it is so far off that the outline would become a dot."""
    if not pin or geom is None or dist != dist:
        return bounds
    size = max(1000.0, math.sqrt(max(acres(geom), 1) * ACRE_M2), math.hypot(bounds[2] - bounds[0], bounds[3] - bounds[1]) * 111000)
    if dist < 1.5 * size:
        return (min(bounds[0], pin["lon"]), min(bounds[1], pin["lat"]), max(bounds[2], pin["lon"]), max(bounds[3], pin["lat"]))
    return bounds


# ------------------------------------------------------------------ item builders
def neighbours(http: Http, layer: str, name_field, item: dict, exclude=None, limit: int = 40) -> list:
    """Other records on the same layer inside the view (thin grey, with names)."""
    env = view_lonlat(view_for(item["view_bounds"], item.get("min_size_m", 600)))
    res_deg = (env[2] - env[0]) / W
    params = {"geometry": ",".join(f"{v:.5f}" for v in env), "geometryType": "esriGeometryEnvelope", "inSR": 4326,
              "spatialRel": "esriSpatialRelIntersects", "maxAllowableOffset": f"{res_deg:.6f}", "resultRecordCount": limit}
    try:
        try:
            feats, _ = arc_query(http, layer, params)
        except SourceDown as e:
            if "layer said" not in str(e):
                raise
            params.pop("resultRecordCount")
            feats, _ = arc_query(http, layer, params)
    except SourceDown as e:
        item["warnings"].append(f"neighbours not read ({e})")
        return []
    out = []
    for g, p in feats[:limit]:
        oid = str(p.get("OBJECTID", p.get("objectid", p.get("FID", ""))))
        if g is None or (exclude is not None and oid == str(exclude)):
            continue
        out.append({"geom": g, "name": name_from(p, name_field)})
    return out


def build_question(club: Club, q: dict) -> dict:
    sources, warnings = [], []
    ref = q.get("ref", "")
    layer = layer_of(q.get("layer") or q.get("url") or "")
    rec = q.get("record")
    if not layer or rec in (None, ""):
        raise BadInput(f"question for {ref} has no layer / record")
    feats, read = arc_query(club.http, layer, {"objectIds": str(rec)})
    sources.append(f"{layer}/query?objectIds={rec}")
    geom = unary_union([g for g, _ in feats if g is not None]) if any(g is not None for g, _ in feats) else None
    props = feats[0][1] if feats else {}
    pin = club.pin(ref)
    if pin:
        sources.append(pin["src"])
    dist = pin_distance_m(geom, pin["lon"], pin["lat"]) if (pin and geom is not None) else float("nan")
    rec_ac = q.get("acres_approx") or acres_from(props)
    warnings += outline_warnings(geom, rec_ac, dist)
    if geom is not None:
        bounds = pin_in_view(geom.bounds, pin, dist, geom)
    elif pin:
        bounds = (pin["lon"] - 0.01, pin["lat"] - 0.01, pin["lon"] + 0.01, pin["lat"] + 0.01)
    else:
        raise SourceDown("no outline and no pin to centre the picture on")
    item = {"view_bounds": bounds, "basemap": basemap_for(ref), "warnings": warnings, "sources": sources, "read_date": read}
    item["neighbours"] = neighbours(club.http, layer, q.get("name_field"), item, exclude=rec)
    item["outlines"] = [{"geom": geom, "colour": GOLD}] if geom is not None else []
    item["pins"] = [{"lon": pin["lon"], "lat": pin["lat"], "label": ref}] if pin else []
    a = acres(geom) if geom is not None else 0
    size_txt = f"{fmt_ac(a)} ac drawn"
    if geom is not None and geom.area == 0:   # a trail record: give its length, acres mean nothing
        size_txt = f"line {tx(geom, local_proj(*geom.centroid.coords[0])[0]).length / 1000:,.1f} km drawn"
    rname = q.get("record_name") or name_from(props, q.get("name_field"))
    item["title1"] = f"{ref} {q.get('park', '')} | question, answer: {q.get('answer') or 'none yet'}"
    item["title2"] = f"record: {rname} | " + (f"{fmt_ac(rec_ac)} ac record vs " if rec_ac else "") + f"{size_txt} | {pin_text(dist)}"
    item["caption"] = (f"{ref} {q.get('park', '')}: record {rec} '{rname}' ({q.get('agency') or layer}); "
                       f"{size_txt}" + (f" vs {fmt_ac(rec_ac)} ac in the question" if rec_ac else "") + f"; {pin_text(dist)}; answer {q.get('answer') or 'none yet'}.")
    item["id"] = safe_id(f"{ref}_r{rec}_{hashlib.sha1(layer.encode()).hexdigest()[:6]}")
    item["kind"] = "questions"
    return item


def river_bank(http: Http, bounds, warnings: list, sources: list) -> list:
    """The water's edge (R5 water trails): USGS NHD water polygons (wide rivers + waterbodies) in the view."""
    out = []
    env = ",".join(f"{v:.5f}" for v in bounds)
    for lid in NHD_WATER_LAYERS:
        try:
            feats, _ = arc_query(http, f"{NHD}/{lid}", {"geometry": env, "geometryType": "esriGeometryEnvelope", "inSR": 4326,
                                                         "spatialRel": "esriSpatialRelIntersects", "outFields": "OBJECTID"})
            sources.append(f"{NHD}/{lid}")
            out += [g for g, _ in feats if g is not None and g.area > 0]
        except SourceDown as e:
            warnings.append(f"river bank not read from USGS NHD ({e})")
    return out


def envelope_is_whole(club: Club, ref: str) -> bool:
    """Only Kentucky club files give the WHOLE outline in a 2-fer picture (live records are cut to the view)."""
    ky = club.maybe(club.data / "ky-answer-key.json")
    return bool(ky and ref in ky.get("parks", {}))


def build_fer(club: Club, row: dict, area: str) -> dict:
    sources, warnings = [], []
    refs = row.get("refs") or []
    kind = row.get("kind", "area")
    patch_shape = club_shape(row.get("shape"))
    zone = club_shape(row.get("zone")) if row.get("zone") else None
    if kind == "trail" and zone is not None and zone.area > 0:
        patch = zone
    else:
        patch = patch_shape if (patch_shape is not None and patch_shape.area > 0) else None
    stretch = patch_shape if (patch_shape is not None and patch_shape.area == 0) else None
    b = row.get("box")
    if b and len(b) == 4:
        bounds = tuple(b)
    elif patch_shape is not None:
        bounds = patch_shape.bounds
    else:
        c = row.get("center") or [0, 0]
        bounds = (c[1] - 0.005, c[0] - 0.005, c[1] + 0.005, c[0] + 0.005)
    item = {"view_bounds": bounds, "basemap": basemap_for(area or (refs[0] if refs else "")), "warnings": warnings, "sources": sources,
            "read_date": today(), "min_size_m": 900}
    env = view_lonlat(view_for(bounds, 900))
    dx, dy = env[2] - env[0], env[3] - env[1]
    env_big = (env[0] - dx, env[1] - dy, env[2] + dx, env[3] + dy)
    res_deg = dx / W
    outlines, pins, lines, bands, trail_parks = [], [], [], [], []
    names = row.get("names") or {}
    for i, ref in enumerate(refs):
        colour = PARK_COLOURS[i % len(PARK_COLOURS)]
        geom, info = club.park_outline(ref, sources, warnings, envelope=env_big, offset=f"{res_deg / 2:.7f}")
        stored = (row.get("lines") or {}).get(ref)
        if geom is None and stored:
            geom = MultiLineString([l for l in stored if len(l) >= 2])
            warnings.append(f"{ref}: drawn from the outline edges saved on the row (record not read)")
        if geom is None:
            warnings.append(f"{ref}: the record geometry is empty (no outline found)")
            continue
        names.setdefault(ref, info.get("name", ""))
        is_line = geom.area == 0
        if is_line:
            trail_parks.append((ref, geom, colour))
            lines.append({"geom": geom, "colour": colour, "width": 2})
        else:
            outlines.append({"geom": geom, "colour": colour, "width": 2})
        pin = club.pin(ref)
        if pin:
            pins.append({"lon": pin["lon"], "lat": pin["lat"], "label": ref})
            sources.append(pin["src"])
            if not is_line and envelope_is_whole(club, ref):
                dist = pin_distance_m(geom, pin["lon"], pin["lat"])
                if dist == dist and dist > 2000:
                    warnings.append(f"{ref}: POTA's pin is {dist / 1000:.1f} km outside its outline")
    # R5 bands: land trail = 100 ft from the trail LINE; water trail = 100 ft from the river BANK (never from a centre line)
    water = []
    if kind == "river" or row.get("water_route"):
        water = [w.intersection(box(*env_big)) for w in river_bank(club.http, env_big, warnings, sources)]
        water = [w for w in water if not w.is_empty]
        if water:
            bands.append({"geom": metric_buffer(unary_union(water), FT100), "colour": BAND})
        else:
            warnings.append("no river bank found in view, so the 100 ft bank band is not drawn (it is never drawn from the centre line)")
    elif kind == "trail":
        for ref, g, colour in trail_parks:
            gl = g.intersection(box(*env_big))
            if not gl.is_empty:
                bands.append({"geom": metric_buffer(gl, FT100), "colour": BAND})
    if stretch is not None:
        lines.append({"geom": stretch, "colour": ORANGE, "width": 4})
    item.update(outlines=outlines, pins=pins, lines=lines, bands=bands, water=water, patch=patch, neighbours=[])
    wide = row.get("wide_m") or row.get("zone_wide_m") or row.get("strip_wide_m")
    if not wide and patch is not None:
        wide = width_m(patch)
    if wide and wide < YARDS50:
        warnings.append(f"the 2-fer patch is only {wide / M_PER_YARD:.0f} yards across (under 50 yards)")
    pa = row.get("acres") or row.get("zone_acres") or (acres(patch) if patch is not None else 0)
    wtxt = f"{wide / M_PER_YARD:,.0f} yd across" if wide else "width ?"
    if patch is None and stretch is not None:   # a water / trail stretch saved as a line, not an area
        ln = row.get("len_m") or tx(stretch, local_proj(*stretch.centroid.coords[0])[0]).length
        what = f"orange line = shared stretch, {ln / 1000:,.1f} km"
        cap_what = what
    else:
        what = f"orange patch {fmt_ac(pa)} ac, {wtxt}"
        cap_what = f"patch {fmt_ac(pa)} ac, {wtxt} ({(wide or 0):.0f} m)"
    band_txt = {"river": "; dashed = 100 ft from the river bank", "trail": "; dashed = 100 ft from the trail line"}.get(kind, "")
    item["title1"] = f"{' + '.join(refs)} | {kind} 2-fer | {str(row.get('status', ''))[:70]}"
    item["title2"] = f"{what}{band_txt}; " + ", ".join(
        f"{('gold', 'blue', 'green', 'purple')[i % 4]} = {r} {names.get(r, '')}" for i, r in enumerate(refs))
    nm = " + ".join(f"{r} {names.get(r, '')}".strip() for r in refs)
    item["caption"] = f"{nm}: {kind} 2-fer ({row.get('status', '')}); {cap_what}."
    item["id"] = safe_id(row.get("id") or f"{'+'.join(refs)}@{kind}")
    item["kind"] = "fers"
    return item


def build_ref(club: Club, ref: str, key_path: Path) -> dict:
    sources, warnings = [], []
    item = {"warnings": warnings, "sources": sources, "read_date": today(), "basemap": basemap_for(ref)}
    nbs, rec_ac = [], None
    if key_path.is_dir():   # world-bounds/<country>: {ref: {n, r, s}}
        geom, info, others = None, {}, []
        for f in sorted(key_path.glob("*.json")):
            for r, p in club.load(f).items():
                if not isinstance(p, dict):
                    continue
                if r == ref:
                    geom = rings_to_shape(p.get("r") or [])
                    info = {"name": p.get("n", ""), "grade": f"saved world outline ({p.get('s', '')})", "records": [p.get("n", "")]}
                    sources.append(f"world-bounds/{key_path.name}/{f.name} ({p.get('s', '')})")
                else:
                    others.append((r, p))
        if not info:
            raise SourceDown(f"{ref} is not in {key_path}")
        if geom is not None:
            vb = box(*geom.bounds).buffer(max(geom.bounds[2] - geom.bounds[0], geom.bounds[3] - geom.bounds[1], 0.02))
            for r, p in others:
                g = rings_to_shape(p.get("r") or [])
                if g is not None and g.intersects(vb):
                    nbs.append({"geom": g, "name": f"{r} {p.get('n', '')}"})
    else:
        key = club.load(key_path)
        if ref not in key.get("parks", {}):
            raise SourceDown(f"{ref} is not in {key_path.name}")
        geom, info = club.park_outline(ref, sources, warnings, key_hint=club.key_kind(key))
        rec_ac = info.get("record_acres")
    pin = club.pin(ref)
    if pin:
        sources.append(pin["src"])
    dist = pin_distance_m(geom, pin["lon"], pin["lat"]) if (pin and geom is not None) else float("nan")
    warnings += outline_warnings(geom, rec_ac, dist)
    if geom is None:
        if not pin:
            raise SourceDown("no outline and no pin")
        bounds = (pin["lon"] - 0.01, pin["lat"] - 0.01, pin["lon"] + 0.01, pin["lat"] + 0.01)
    else:
        bounds = pin_in_view(geom.bounds, pin, dist, geom)
    item["view_bounds"] = bounds
    if not key_path.is_dir():
        if ref.startswith("CA-") and (club.data / "canada-bounds").exists():
            vb = box(*view_lonlat(view_for(bounds)))
            for f in sorted((club.data / "canada-bounds").glob("CA-*.json")):
                if f.stem != ref:
                    g, props = club.ca_bounds(f.stem)
                    if g is not None and g.intersects(vb):
                        nbs.append({"geom": g, "name": f"{f.stem} {props.get('name', '')}"})
        elif ref.startswith("US-"):
            nbs = [n for n in neighbours(club.http, PADUS, "Unit_Nm", item) if n["name"] not in info.get("records", [])]
    item["neighbours"] = nbs
    item["outlines"] = [{"geom": geom, "colour": GOLD}] if geom is not None else []
    item["pins"] = [{"lon": pin["lon"], "lat": pin["lat"], "label": ref}] if pin else []
    a = acres(geom) if geom is not None else 0
    recs = "; ".join([r for r in info.get("records", []) if r][:2]) or "none"
    pota_name = (pin or {}).get("name") or info.get("name", "")
    ka = info.get("key_acres")
    acre_txt = (f"{fmt_ac(rec_ac)} ac record vs " if rec_ac else "") + (f"{fmt_ac(ka)} ac key vs " if ka else "") + f"{fmt_ac(a)} ac drawn"
    if geom is not None and geom.area == 0:
        acre_txt = f"line {tx(geom, local_proj(*geom.centroid.coords[0])[0]).length / 1000:,.1f} km drawn"
    item["title1"] = f"{ref} {pota_name} | grade: {info.get('grade') or '?'}"
    item["title2"] = f"record: {recs} | {acre_txt} | {pin_text(dist)}"
    item["caption"] = f"{ref} {pota_name}: outline from {', '.join([x for x in dict.fromkeys(sources) if 'pota.app' not in x and 'parkinfo' not in x][:2]) or 'nowhere'}; {acre_txt}; {pin_text(dist)}."
    item["id"] = safe_id(ref)
    item["kind"] = "outlines"
    return item


# ------------------------------------------------------------------ run
def load_index(out: Path) -> dict:
    p = out / "index.json"
    if p.exists():
        try:
            return {e["id"]: e for e in json.loads(p.read_text())}
        except (ValueError, KeyError, TypeError):
            return {}
    return {}


def save_index(out: Path, idx: dict) -> None:
    out.mkdir(parents=True, exist_ok=True)
    tmp = out / "index.json.tmp"
    tmp.write_text(json.dumps(sorted(idx.values(), key=lambda e: (e.get("kind", ""), e["id"])), indent=1, ensure_ascii=False))
    tmp.replace(out / "index.json")


def clean_older(out: Path, days: float) -> int:
    """Delete pictures (only inside --out) older than DAYS, and their index lines."""
    idx = load_index(out)
    cutoff = time.time() - days * 86400
    n = 0
    for e in list(idx.values()):
        f = out / e["file"] if e.get("file") else None
        if f is not None and f.exists() and f.stat().st_mtime < cutoff:
            f.unlink()
            cap = f.with_suffix(".json")
            if cap.exists():
                cap.unlink()
            n += 1
            idx.pop(e["id"])
        elif f is None or not f.exists():
            idx.pop(e["id"])
    save_index(out, idx)
    return n


def find_data_dir(p: Path) -> Path:
    """The club's data folder: the nearest folder above the input that holds the club's files."""
    p = p.resolve()
    for d in [p] + list(p.parents)[:4]:
        if d.is_dir() and any((d / n).exists() for n in ("us-key", "ca-key", "ky-answer-key.json", "fers", "trails", "canada-bounds")):
            return d
    return p.parent


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="KPC 9 map picture maker: one small picture per item for the checker.")
    ap.add_argument("--questions", type=Path, help="a question file (data/waiting/questions/*.json)")
    ap.add_argument("--fers", type=Path, help="a 2-fer area file (data/fers/US-XX.json)")
    ap.add_argument("--refs", help="park numbers, comma separated (needs --key)")
    ap.add_argument("--key", type=Path, help="key file (us-key/US-XX.json, ca-key/CA-XX.json, ky-answer-key.json) or a world-bounds/<country> folder")
    ap.add_argument("--data", type=Path, help="the club's data folder (us-key/, ca-key/, canada-bounds/, trails/, parkinfo/, ky-answer-key.json); default: found from the input")
    ap.add_argument("--ky-outlines", type=Path, help="folder with the club's Kentucky outline files (ky-*.geojson); default: the folder above --data")
    ap.add_argument("--answer", help="questions only: keep this answer (YES / NO / NOT SURE)")
    ap.add_argument("--ref-prefix", help="questions only: keep refs that start with this (e.g. US-)")
    ap.add_argument("--kind", help="2-fers only: keep these kinds, comma separated (area,trail,river,water-only,same land)")
    ap.add_argument("--ids", help="keep only these ids: 2-fer row ids or question refs (separated by ';', or @file with one per line)")
    ap.add_argument("--limit", type=int, default=0, help="at most this many pictures this run")
    ap.add_argument("--out", type=Path, default=Path("pictures"))
    ap.add_argument("--cache", type=Path, default=None, help="cache folder (default: .kpc-cache next to --out)")
    ap.add_argument("--resume", action="store_true", help="skip pictures already made; redo ones that failed")
    ap.add_argument("--max-minutes", type=float, default=50)
    ap.add_argument("--clean-older-than", type=float, metavar="DAYS", help="delete pictures older than DAYS (only in --out), then stop")
    ap.add_argument("--imagery", action="store_true", help="US: use USGS Imagery Topo instead of USGS Topo")
    ap.add_argument("--no-inset", action="store_true", help="leave out the small 4x zoomed-out locator map")
    ap.add_argument("--offline", action="store_true", help="read only from the cache (for tests)")
    a = ap.parse_args(argv)
    t_start = time.monotonic()

    if a.clean_older_than is not None:
        n = clean_older(a.out, a.clean_older_than)
        log(f"Removed {n} pictures older than {a.clean_older_than:g} days from {a.out}.")
        return 0
    if not (a.questions or a.fers or a.refs):
        log("Nothing to do: give --questions, --fers or --refs (see --help).")
        return 2
    if a.refs and not a.key:
        log("--refs needs --key.")
        return 2
    for p in (a.questions, a.fers, a.key):
        if p is not None and not p.exists():
            log(f"Bad input: not found: {p}")
            return 2
    data = a.data or find_data_dir(a.questions or a.fers or a.key)
    ky_dir = a.ky_outlines or data.parent
    http = Http(a.cache or (a.out.resolve().parent / ".kpc-cache"), offline=a.offline)
    if a.imagery:
        COUNTRY_TILES["US"] = COUNTRY_TILES["K"] = "usgs-imagery"
    ids = None
    if a.ids:
        raw = Path(a.ids[1:]).read_text() if a.ids.startswith("@") else a.ids
        # 2-fer row ids hold a comma ("...@36.501,-88.068"), so ids are split on ";" or new lines; plain refs may also use ","
        ids = set(re.split(r"[;\n]", raw) if ("@" in raw or ";" in raw) else raw.split(","))
        ids = {i.strip() for i in ids if i.strip()}

    jobs = []   # (job id, builder)
    try:
        club = Club(data, ky_dir, http)
        if a.questions:
            qf = club.load(a.questions)
            qs = qf.get("questions") if isinstance(qf, dict) else qf
            if not isinstance(qs, list):
                raise BadInput("the question file has no 'questions' list")
            for q in qs:
                if not isinstance(q, dict) or "ref" not in q or "record" not in q:
                    raise BadInput("a question has no 'ref' or 'record'")
                if a.answer and str(q.get("answer")).upper() != a.answer.upper():
                    continue
                if a.ref_prefix and not str(q["ref"]).startswith(a.ref_prefix):
                    continue
                if ids and q["ref"] not in ids:
                    continue
                jobs.append((f"questions:{q['ref']}:{q.get('record')}:{layer_of(q.get('layer', ''))}", lambda q=q: build_question(club, q)))
        if a.fers:
            ff = club.load(a.fers)
            if not isinstance(ff, dict) or not isinstance(ff.get("spots"), list):
                raise BadInput("the 2-fer file has no 'spots' list")
            kinds = {k.strip() for k in a.kind.split(",")} if a.kind else None
            area = ff.get("st") or a.fers.stem
            for row in ff["spots"]:
                if not isinstance(row, dict) or "refs" not in row:
                    raise BadInput("a 2-fer row has no 'refs'")
                if not is_live(row) or (kinds and row.get("kind") not in kinds) or (ids and row.get("id") not in ids):
                    continue
                jobs.append((f"fers:{row.get('id')}", lambda row=row: build_fer(club, row, area)))
        if a.refs:
            club.load(a.key) if a.key.is_file() else None
            for ref in [r.strip() for r in a.refs.split(",") if r.strip()]:
                jobs.append((f"outlines:{ref}", lambda ref=ref: build_ref(club, ref, a.key)))
    except BadInput as e:
        log(f"Bad input: {e}")
        return 2

    a.out.mkdir(parents=True, exist_ok=True)
    idx = load_index(a.out)
    done_jobs = {e.get("job") for e in idx.values() if e.get("status") == "done" and e.get("file") and (a.out / e["file"]).exists()}
    failed_sources: collections.Counter = collections.Counter()
    made = failed = skipped = 0
    times, sizes = [], []
    unfinished = False
    for job, build in jobs:
        if a.resume and job in done_jobs:
            skipped += 1
            continue
        if a.limit and made + failed >= a.limit:
            unfinished = True
            break
        if (time.monotonic() - t_start) / 60 >= a.max_minutes:
            unfinished = True
            log("Time is up: stopping cleanly. Run again with --resume to carry on.")
            break
        t0 = time.monotonic()
        try:
            item = build()
            jpg = render(http, item, failed_sources, inset=not a.no_inset)
            rel = f"{item['kind']}/{item['id']}.jpg"
            f = a.out / rel
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_bytes(jpg)
            secs = round(time.monotonic() - t0, 1)
            warn = list(dict.fromkeys(item["warnings"]))
            idx.pop(safe_id(job.split(":", 1)[1].replace(":", "_")), None)
            idx[item["id"]] = {"id": item["id"], "job": job, "kind": item["kind"], "file": rel, "caption": item["caption"],
                               "read_date": item.get("read_date") or today(), "sources": sorted(set(item["sources"])), "warnings": warn,
                               "status": "done", "seconds": secs, "bytes": len(jpg)}
            f.with_suffix(".json").write_text(json.dumps({"id": item["id"], "caption": item["caption"], "warnings": warn}, ensure_ascii=False))
            made += 1
            times.append(secs)
            sizes.append(len(jpg))
            log(f"OK   {rel}  {len(jpg) // 1024} KB  {secs}s" + (f"  warnings: {'; '.join(warn)}" if warn else ""))
        except BadInput as e:
            log(f"Bad input: {e}")
            save_index(a.out, idx)
            return 2
        except Exception as e:   # one failure never stops a batch: log the reason, retry next run
            failed += 1
            why = f"SOURCE DOWN: {e}" if isinstance(e, SourceDown) else f"CAN'T TELL: {type(e).__name__}: {e}"
            iid = safe_id(job.split(":", 1)[1].replace(":", "_"))
            idx[iid] = {"id": iid, "job": job, "kind": job.split(":")[0], "file": "", "caption": "", "read_date": today(), "sources": [],
                        "warnings": [why], "status": "retry"}
            log(f"SKIP {job}: {why}; will retry next run")
        save_index(a.out, idx)
    save_index(a.out, idx)
    avg_kb = (sum(sizes) / len(sizes) / 1024) if sizes else 0
    avg_s = (sum(times) / len(times)) if times else 0
    log(f"Done: {made} pictures made, {failed} to retry, {skipped} already made. Average {avg_kb:.0f} KB and {avg_s:.1f} s per picture."
        + (f" Tile sources that failed: {dict(failed_sources)}." if failed_sources else " No tile source failed."))
    return 3 if (unfinished or failed) else 0


if __name__ == "__main__":
    sys.exit(main())
