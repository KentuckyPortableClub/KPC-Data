#!/usr/bin/env python3
"""KPC 2-FER ACCURACY CHECKER (build spec: 'KPC 2-fer accuracy checker', Oct 31 2026).

Re-checks every LIVE 2-fer row in the club's data/fers/<area>.json against the LIVE official layers that the club's boundary
keys name, and writes a verdict per row. It NEVER edits the 2-fer files: a person and the club's waiting room decide.

Per live row (rows whose status starts 'dropped' / 'merged' are skipped):
  1. every park of the row is re-read from its official layer: by record id where the key has one (US / Canada keys:
     PAD-US / CPCAD object ids, or '<prefix><id>' ids in data/us-key/layers.json), else by name near the spot (the
     Kentucky key names a layer + an outline name). ArcGIS query, outSR=4326, f=geojson (Esri JSON fallback).
  2. the overlap is recomputed in the spot's UTM zone: area / same-land / water rows = intersection of the parks' outlines;
     trail rows = the park outline(s) intersected with a 100-ft (30.48 m) buffer of the official line (club rules R5 / R6);
     river rows = the same, measured from the river's BANK (USGS NHD river / lake areas): a water-route historic trail
     (Lewis and Clark, Trail of Tears, Star-Spangled Banner, Captain John Smith) = 100 ft of land from the bank of the
     water its coarse line follows; any other river line = 100 ft of its line + 100 ft from the bank of the NHD river area
     it runs in. A trail / river row is one STRETCH: the live band is judged within 50 m of the stored stretch (the whole
     touching live band is reported as live_stretch_acres). Water-only rows = the outlines' overlap intersected with USGS
     NHD water (a Forest Service park is read as its administrative boundary for these, not the owned land).
  3. verdict: CONFIRMED / SHRUNK / MOVED / GONE / SOURCE DOWN / RECORD CHANGED (+ two extra labels this tool needs to be
     honest: GREW = the live overlap is > 25 % BIGGER, so not 'within +-25 %'; NOT CHECKED = the key names no live official
     layer for a park (OpenStreetMap-only outline, a pin-only park, a zipped-file layer...)).
  4. club rule R9 flags: 'small overlap' (live overlap under 50 yards = 45.72 m across = the largest circle that fits),
     'water-only'.
  5. writes <out>/<area>.json, <out>/<area>.summary.md and <out>/report.csv (all areas in <out>).

Polite: one request at a time (the tool is single threaded) and at least --min-interval seconds between two requests to the
same host, a User-Agent naming the club, back-off on errors / 429 / 5xx (Retry-After honoured), every park record cached for
the run (in memory + <out>/.cache, so --resume reuses it). Only hosts named by the keys / this file's official-layer table
are contacted; OpenStreetMap, Google, Protected Planet... are refused outright.

Headless (GitHub Actions friendly): --max-minutes (default 50, under the 55-minute job limit) stops cleanly after the
current row, saves, and a later run with --resume carries on. Exit code 0 unless the inputs cannot be read (2).

Usage:  python3 kpc_fers_check.py --areas US-KY US-UT US-VA [--resume] [--fers-dir data/fers] [--key-dir data]
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import gzip
import hashlib
import json
import math
import os
import pathlib
import re
import sys
import time
import unicodedata
import urllib.parse
from typing import Any, Iterable

import requests
import shapely
from pyproj import Transformer
from shapely.geometry import (GeometryCollection, LineString, MultiLineString, MultiPolygon, Point, Polygon, box as sbox,
                              shape as gj_shape)

VERSION = '0.1.0 (2026-10-31)'
UA = 'KPC 2-fer accuracy checker/0.1 (Kentucky Portable Club ham radio club; kentuckyportableclub.github.io)'

# ---------------------------------------------------------------- club rules (numbers in metres)
TRAIL_BUFFER_M = 30.48        # R5 / R6: 100 ft from the official trail / river line
SMALL_ACROSS_M = 45.72        # R9: under 50 yards across = 'small overlap'
MOVED_M = 200.0               # overlap centre more than 200 m away = MOVED
SIZE_TOL = 0.25               # +-25 % = same size
MIN_LIVE_M2 = 10.0            # less than 10 m2 of live overlap = none (numerical dust)
NEAR_M = 30.0                 # a live overlap piece within 30 m of the stored shape is 'the same spot'
LINEAR_CLIP_M = 50.0          # trail / river rows: the live band is judged within 50 m of the stored stretch
POS_TOL_M = 10.0              # club shapes are drawn on a 5 m grid, 5 m in from the park edge: 'still inside' allows 10 m
WINDOW_M = 1000.0             # live layers are read in the stored row's box grown by 1 km
ACRE_M2 = 4046.8564224

VERDICTS = ['CONFIRMED', 'SHRUNK', 'GREW', 'MOVED', 'GONE', 'RECORD CHANGED', 'SOURCE DOWN', 'NOT CHECKED']

# ---------------------------------------------------------------- official layers
PADUS = 'https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0'      # numeric ids in data/us-key
CPCAD = 'https://maps-cartes.ec.gc.ca/arcgis/rest/services/CWS_SCF/CPCAD/MapServer/0'        # numeric ids in data/ca-key
KYGIS = 'https://kygisserver.ky.gov/arcgis/rest/services/WGS84WM_Services/'
# Kentucky key layer codes (kpc-bounds.js KY table) -> the LIVE official layer that the club's saved ky-*.geojson copy
# comes from (kpc_ky_refine_files.py / kpc_owned.py / ky-fws.geojson 'name'). by: 'name' = outline name near the spot,
# 'box' = every record in the spot's window (the owned-land map). None = never checked live (see 'why').
KY_LAYERS: dict[str, dict | None] = {
    'bstate': {'url': KYGIS + 'Ky_State_Parks_Features_WGS84WM/MapServer/8', 'name': 'PUBLIC_NAM', 'by': 'name'},
    'bwma': {'url': KYGIS + 'Ky_Public_Hunting_Areas_WGS84WM/MapServer/1', 'name': 'AREANAME', 'by': 'name'},
    'bsnp': {'url': KYGIS + 'Ky_KNP_State_Nature_Preserves_WGS84WM/MapServer/0', 'name': 'MANAME', 'by': 'name'},
    'bsna': {'url': KYGIS + 'Ky_KNP_Natural_Areas_WGS84WM/MapServer/0', 'name': 'MANAME', 'by': 'name'},
    'bwild': {'url': KYGIS + 'Ky_KNP_Wild_River_Corridors_WGS84WM/MapServer/0', 'name': 'MANAME', 'by': 'name'},
    'bnps': {'url': 'https://services1.arcgis.com/fBc8EJBxQRMcHlei/arcgis/rest/services/NPS_Land_Resources_Division_Boundary_and_Tract_Data_Service/FeatureServer/2', 'name': 'UNIT_NAME', 'by': 'name'},
    'bfws': {'url': 'https://services.arcgis.com/QVENGdaPbd4LUkLV/arcgis/rest/services/FWSInterest_Simplified_Authoritative/FeatureServer/0', 'name': 'ORGNAME', 'by': 'name'},
    'bwilder': {'url': 'https://apps.fs.usda.gov/arcx/rest/services/EDW/EDW_Wilderness_02/MapServer/0', 'name': 'wildernessname', 'by': 'name'},
    'bdbnfo': {'url': 'https://apps.fs.usda.gov/arcx/rest/services/EDW/EDW_BasicOwnership_02/MapServer/0', 'name': 'forestname', 'by': 'box',
               'where': "ownerclassification = 'USDA FOREST SERVICE'"},
    'bpad': {'url': PADUS, 'name': 'Unit_Nm', 'by': 'name'},
    'bdbnf': None,   # the proclamation (outer) line: never the park (club rule B1)
    'bkpc': None,    # traced from OpenStreetMap: not official, never used
    'btrail': None,  # a pin only, no outline
}
# Water-only ('boat or kayak') rows sit INSIDE both outlines but OFF the owned-land map (club ruling Oct 28): for them the
# Forest Service park is re-read as its administrative forest boundary, not the owned land.
KY_OUTLINE_FOR_WATER: dict[str, dict] = {
    'bdbnfo': {'url': 'https://apps.fs.usda.gov/arcx/rest/services/EDW/EDW_ForestSystemBoundaries_01/MapServer/1', 'name': 'forestname', 'by': 'box'},
}
KY_NOT_LIVE_WHY = {'bdbnf': 'proclamation line only (never the park, club rule B1)',
                   'bkpc': 'only outline is traced from OpenStreetMap (not official, refused)',
                   'btrail': 'trail pin only, no official outline or line'}
# Trail / river LINES re-read live (official agency layers). Others use the club's saved official copy data/trails/<ref>.json
# (marked 'saved copy' in the row). Extend with --trail-layers <json> {ref: {url, where}}.
EDW_TRAILS = 'https://apps.fs.usda.gov/arcx/rest/services/EDW/EDW_TrailNFSPublishWithDataStatus_01/MapServer/0'
TRAIL_LAYERS: dict[str, dict] = {
    'US-11181': {'url': EDW_TRAILS, 'where': "UPPER(trail_name) LIKE 'SHELTOWEE%'", 'by': 'US Forest Service EDW NFS trails'},
    'US-10102': {'url': KYGIS + 'Ky_Recreational_Trails_WGS84WM/MapServer/1', 'where': '1=1',
                 'by': "KY Recreational Trails layer 1 'Pine Mountain Trail (Open)'"},
}
# USGS NHD (official water) for water-only rows
WATER_LAYERS = ['https://hydro.nationalmap.gov/arcgis/rest/services/nhd/MapServer/9',
                'https://hydro.nationalmap.gov/arcgis/rest/services/nhd/MapServer/12']
# the water a river row is measured from: NHDArea StreamRiver (+ lakes / reservoirs / estuaries unless --rivers-only)
RIVER_WATER_QUERIES = [(WATER_LAYERS[0], 'FTYPE = 460'), (WATER_LAYERS[1], 'FTYPE IN (390, 436, 493)')]
REFUSED_HOSTS = re.compile(r'(openstreetmap|osm\.org|overpass|google|googleapis|protectedplanet|wdpa|wikipedia|wikimapia|alltrails)', re.I)


class SourceDown(Exception):
    """A layer did not answer (after retries)."""


class Refused(Exception):
    """A host that is not an official layer named by the keys."""


# ================================================================= polite HTTP
class Http:
    def __init__(self, cache_dir: pathlib.Path | None, min_interval: float = 1.0, cache_hours: float = 20.0,
                 tries: int = 4, timeout: float = 120.0, offline: bool = False, log=None):
        self.s = requests.Session()
        self.s.headers.update({'User-Agent': UA, 'Accept': 'application/json'})
        self.cache_dir, self.min_interval, self.cache_s = cache_dir, min_interval, cache_hours * 3600
        self.tries, self.timeout, self.offline = tries, timeout, offline
        self.last: dict[str, float] = {}
        self.mem: dict[str, Any] = {}
        self.allowed: set[str] = set()
        self.down: dict[str, str] = {}          # layer url -> error (this run): later rows do not hammer a dead host
        self.n_requests = 0
        self.log = log or (lambda *a: None)
        if cache_dir: cache_dir.mkdir(parents=True, exist_ok=True)

    def allow(self, url: str):
        self.allowed.add(layer_base(url))

    def _key(self, url, params):
        return hashlib.sha256((url + '?' + json.dumps(params, sort_keys=True)).encode()).hexdigest()[:24]

    def get_json(self, url: str, params: dict) -> tuple[dict, str]:
        """(json, read time ISO) for an ArcGIS REST call; raises SourceDown / Refused."""
        host = urllib.parse.urlsplit(url).netloc.lower()
        if REFUSED_HOSTS.search(host):
            raise Refused(f'{host} is not an official layer (refused)')
        if layer_base(url) not in self.allowed:
            raise Refused(f'{url} is not a layer named by the keys / official-layer table')
        base = layer_base(url)
        if base in self.down:
            raise SourceDown(self.down[base] + ' (earlier this run)')
        k = self._key(url, params)
        if k in self.mem:
            return self.mem[k]
        f = self.cache_dir / f'{k}.json.gz' if self.cache_dir else None
        if f and f.exists() and (self.offline or time.time() - f.stat().st_mtime < self.cache_s):
            try:
                with gzip.open(f, 'rt', encoding='utf-8') as fh:
                    c = json.load(fh)
                self.mem[k] = (c['j'], c['at'])
                return self.mem[k]
            except Exception:  # noqa: BLE001  (a broken cache file is simply refetched)
                pass
        if self.offline:
            raise SourceDown('offline mode and no cached copy')
        last_err = 'no answer'
        for i in range(self.tries):
            wait = self.min_interval - (time.time() - self.last.get(host, 0))
            if wait > 0:
                time.sleep(wait)
            self.last[host] = time.time()
            self.n_requests += 1
            try:
                body = urllib.parse.urlencode(params)
                if len(body) > 1800:
                    r = self.s.post(url, data=params, timeout=self.timeout)
                    if r.status_code == 405:
                        r = self.s.get(url, params=params, timeout=self.timeout)
                else:
                    r = self.s.get(url, params=params, timeout=self.timeout)
                if r.status_code in (429, 500, 502, 503, 504):
                    ra = r.headers.get('Retry-After')
                    last_err = f'HTTP {r.status_code}'
                    time.sleep(min(float(ra) if ra and ra.isdigit() else 4 * 2 ** i, 120))
                    continue
                if r.status_code != 200:
                    last_err = f'HTTP {r.status_code}'
                    if r.status_code in (400, 401, 403, 404):
                        break
                    time.sleep(4 * 2 ** i)
                    continue
                try:
                    j = r.json()
                except ValueError:
                    last_err = 'answer is not JSON'
                    time.sleep(4 * 2 ** i)
                    continue
                if isinstance(j, dict) and j.get('error'):
                    e = j['error']
                    last_err = f"layer error {e.get('code')}: {str(e.get('message'))[:120]}"
                    if params.get('f') == 'geojson':
                        break  # caller falls back to Esri JSON
                    time.sleep(4 * 2 ** i)
                    continue
                at = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
                self.mem[k] = (j, at)
                if f:
                    tmp = f.with_suffix('.tmp')
                    with gzip.open(tmp, 'wt', encoding='utf-8') as fh:
                        json.dump({'url': url, 'params': params, 'at': at, 'j': j}, fh)
                    os.replace(tmp, f)
                return j, at
            except requests.RequestException as e:
                last_err = type(e).__name__ + ': ' + str(e)[:120]
                time.sleep(4 * 2 ** i)
        raise SourceDown(f'{urllib.parse.urlsplit(url).netloc}: {last_err}')

    def mark_down(self, url, why):
        self.down[layer_base(url)] = why


def layer_base(url: str) -> str:
    u = url.split('?')[0].rstrip('/')
    return u[:-len('/query')] if u.endswith('/query') else u


# ================================================================= geometry helpers
def utm_for(lat: float, lon: float) -> int:
    zone = int((lon + 180) // 6) % 60 + 1
    return (32600 if lat >= 0 else 32700) + zone


class Proj:
    """lon/lat (EPSG:4326) <-> the spot's UTM zone."""

    def __init__(self, lat: float, lon: float):
        self.epsg = utm_for(lat, lon)
        self.fwd = Transformer.from_crs(4326, self.epsg, always_xy=True)
        self.inv = Transformer.from_crs(self.epsg, 4326, always_xy=True)

    def to_m(self, g):
        if g is None or g.is_empty:
            return g
        return shapely.transform(g, lambda xy: _tr(self.fwd, xy))

    def to_ll(self, g):
        if g is None or g.is_empty:
            return g
        return shapely.transform(g, lambda xy: _tr(self.inv, xy))


def _tr(t, xy):
    import numpy as np
    x, y = t.transform(xy[:, 0], xy[:, 1])
    return np.column_stack([x, y])


def polys_of(g) -> list[Polygon]:
    if g is None or g.is_empty:
        return []
    if isinstance(g, Polygon):
        return [g]
    if isinstance(g, MultiPolygon):
        return list(g.geoms)
    if isinstance(g, GeometryCollection):
        return [p for x in g.geoms for p in polys_of(x)]
    return []


def lines_of(g) -> list[LineString]:
    if g is None or g.is_empty:
        return []
    if isinstance(g, LineString):
        return [g]
    if isinstance(g, MultiLineString):
        return list(g.geoms)
    if isinstance(g, GeometryCollection):
        return [p for x in g.geoms for p in lines_of(x)]
    return []


def only_area(g):
    ps = polys_of(g)
    if not ps:
        return Polygon()
    return shapely.make_valid(MultiPolygon(ps)) if len(ps) > 1 else shapely.make_valid(ps[0])


def across_m(g) -> tuple[float, Point | None]:
    """(diameter of the largest circle that fits, its centre) = the club's 'wide_m' and spot centre."""
    ps = polys_of(g)
    if not ps:
        return 0.0, None
    p = max(ps, key=lambda q: q.area)
    try:
        b = p.bounds
        tol = max(0.25, max(b[2] - b[0], b[3] - b[1]) / 2000.0)
        if hasattr(shapely, 'maximum_inscribed_circle'):
            ln = shapely.maximum_inscribed_circle(p, tol)
            c = Point(ln.coords[0])
            return 2.0 * ln.length, c
        from shapely.ops import polylabel
        c = polylabel(p, tol)
        return 2.0 * p.exterior.distance(c) if p.contains(c) else 0.0, c
    except Exception:  # noqa: BLE001
        c = p.representative_point()
        return 2.0 * p.boundary.distance(c), c


def parse_coords(v):
    if isinstance(v, str):
        v = json.loads(v)
    return v


def depth(v) -> int:
    d = 0
    while isinstance(v, list) and v:
        d += 1
        v = v[0]
    return d


def stored_geometry(v, as_line: bool = False):
    """The 2-fer file's 'shape' / 'zone': one ring [[lon, lat], ...] (the club does not repeat the first point), a list of
    rings, or a list of polygons. as_line=True: a single list of points is a LINE (trail rows' 'shape' = the stretch)."""
    v = parse_coords(v)
    if not v:
        return None
    d = depth(v)
    if d == 2:
        if as_line or len(v) < 3:
            return LineString(v) if len(v) >= 2 else None
        return shapely.make_valid(Polygon(v))
    if d == 3:
        parts = [shapely.make_valid(Polygon(r)) for r in v if len(r) >= 4]
        return shapely.union_all(parts) if parts else None
    if d == 4:
        parts = [shapely.make_valid(Polygon(p[0], p[1:])) for p in v if p and len(p[0]) >= 4]
        return shapely.union_all(parts) if parts else None
    return None


def esri_to_shape(g: dict):
    """Esri JSON geometry -> shapely (rings: clockwise = outer, counter-clockwise = hole)."""
    if not g:
        return None
    if 'rings' in g:
        outers, holes = [], []
        for r in g['rings']:
            if len(r) < 4:
                continue
            ring = Polygon(r)
            # Esri outer rings are clockwise = negative signed area in shapely's convention
            (holes if bool(shapely.is_ccw(ring.exterior)) else outers).append(ring)
        if not outers:
            outers, holes = holes, []
        polys = []
        for o in outers:
            hs = [h.exterior.coords for h in holes if o.contains(h.representative_point())]
            polys.append(shapely.make_valid(Polygon(o.exterior.coords, hs)))
        return shapely.union_all(polys) if polys else None
    if 'paths' in g:
        return MultiLineString([p for p in g['paths'] if len(p) >= 2])
    if 'x' in g:
        return Point(g['x'], g['y'])
    return None


# ================================================================= names
GENERIC = re.compile(r'\b(state|national|wildlife|management|area|areas|park|parks|forest|preserve|nature|natural|refuge|'
                     r'recreation|historic|historical|site|resort|wma|nwr|sp|sna|snp|the|of|and|trail|scenic|river|wild|'
                     r'wilderness|study|unit|lake|reservoir|dam|county|public|hunting|access|conservation)\b')


def norm(s: str) -> str:
    s = unicodedata.normalize('NFKD', str(s or '')).encode('ascii', 'ignore').decode().lower().replace('&', ' and ')
    return ' '.join(re.sub(r'[^a-z0-9 ]', ' ', s).split())


def main_words(s: str) -> list[str]:
    return [w for w in GENERIC.sub(' ', norm(s)).split() if len(w) > 1]


def same_name(a: str, b: str) -> bool:
    a2, b2 = norm(a), norm(b)
    if a2 == b2:
        return True
    wa, wb = set(main_words(a)), set(main_words(b))
    return bool(wa) and wa == wb


# ================================================================= keys
class Keys:
    """Reads the club's boundary keys.
    data/us-key/US-XX.json  parks[ref].m = [[id, name, acres, how], ...]; id int = PAD-US OBJECTID; id '<prefix><n>' =
                            data/us-key/layers.json[prefix] = [query url, name field, label], record n
    data/ca-key/CA-XX.json  same shape; int ids = CPCAD OBJECTID
    data/ky-answer-key.json parks[ref].tracts = [[layer code, outline name, acres, how, pieces]]; 'line'/'trl' = trail line
    """

    def __init__(self, key_dir: pathlib.Path, extra_trails: dict | None = None):
        self.dir = key_dir
        self.us_layers = self._load(key_dir / 'us-key' / 'layers.json') or {}
        self.ky = (self._load(key_dir / 'ky-answer-key.json') or {}).get('parks') or {}
        self.area_keys: dict[str, dict] = {}
        self.trails = dict(TRAIL_LAYERS)
        self.trails.update(extra_trails or {})
        self.files_read: list[str] = []
        if self.ky:
            self.files_read.append(str(key_dir / 'ky-answer-key.json'))

    @staticmethod
    def _load(p: pathlib.Path):
        try:
            if p.suffix == '.gz':
                with gzip.open(p, 'rt', encoding='utf-8') as fh:
                    return json.load(fh)
            with open(p, encoding='utf-8') as fh:
                return json.load(fh)
        except (OSError, ValueError):
            return None

    def area_key(self, area: str) -> dict:
        if area not in self.area_keys:
            sub = 'ca-key' if area.startswith('CA-') else 'us-key'
            p = self.dir / sub / f'{area}.json'
            d = self._load(p) or self._load(p.with_suffix('.json.gz')) or {}
            if d:
                self.files_read.append(str(p))
            self.area_keys[area] = d.get('parks') or {}
        return self.area_keys[area]

    def park(self, ref: str, area: str) -> tuple[str, dict | None]:
        """(source, entry): looks in the row's own area key first, then Kentucky, then every other key already loaded."""
        if area == 'US-KY' and ref in self.ky:
            return 'ky', self.ky[ref]
        k = self.area_key(area)
        if ref in k:
            return area, k[ref]
        if ref in self.ky:
            return 'ky', self.ky[ref]
        for a, kk in self.area_keys.items():
            if ref in kk:
                return a, kk[ref]
        return '', None

    def load_neighbours(self, areas: Iterable[str]):
        for a in areas:
            self.area_key(a)

    def layer_for_prefix(self, pre: str) -> tuple[str, str] | None:
        v = self.us_layers.get(pre)
        if not v:
            return None
        return v[0], (v[1] if len(v) > 1 else '')


# ================================================================= reading one park live
class ParkReader:
    def __init__(self, http: Http, keys: Keys, detail_deg: float = 0.00002, trails_dir: pathlib.Path | None = None,
                 water: bool = True):
        self.http, self.keys, self.detail, self.trails_dir, self.use_water = http, keys, detail_deg, trails_dir, water
        self.meta: dict[str, dict] = {}
        for c in list(KY_LAYERS.values()) + list(KY_OUTLINE_FOR_WATER.values()):
            if c:
                http.allow(c['url'])
        for c in keys.trails.values():
            http.allow(c['url'])
        for u in WATER_LAYERS:
            http.allow(u)
        http.allow(PADUS)
        http.allow(CPCAD)
        for v in keys.us_layers.values():
            if isinstance(v, list) and v and str(v[0]).startswith('http'):
                http.allow(v[0])

    # ---- low level
    def layer_meta(self, url: str) -> dict:
        b = layer_base(url)
        if b not in self.meta:
            j, _ = self.http.get_json(b, {'f': 'json'})
            self.meta[b] = j
        return self.meta[b]

    def oid_field(self, url: str, pre: str = '') -> str:
        if url == PADUS or url == CPCAD:
            return 'OBJECTID'
        if pre in ('wld', 'fwsr', 'fsod'):
            return 'objectid'
        m = self.layer_meta(url)
        return m.get('objectIdField') or next((f['name'] for f in m.get('fields') or [] if f.get('type') == 'esriFieldTypeOID'), 'OBJECTID')

    def query(self, url: str, where: str = '1=1', object_ids: list | None = None, window=None, out_fields: str = '*',
              geometry: bool = True, ids_only: bool = False) -> tuple[list[dict], str]:
        """Features as [{'id', 'props', 'geom'(shapely 4326)}], read time. Pages; f=geojson, Esri JSON fallback."""
        b = layer_base(url) + '/query'
        p: dict[str, Any] = {'where': where, 'outFields': out_fields, 'returnGeometry': 'true' if geometry else 'false', 'outSR': 4326}
        if object_ids:
            p['objectIds'] = ','.join(str(i) for i in object_ids)
        if window is not None:
            x0, y0, x1, y1 = window
            p.update({'geometry': f'{x0},{y0},{x1},{y1}', 'geometryType': 'esriGeometryEnvelope', 'inSR': 4326,
                      'spatialRel': 'esriSpatialRelIntersects'})
        if ids_only:
            p = {k: v for k, v in p.items() if k not in ('outFields', 'returnGeometry', 'outSR')}
            p.update({'returnIdsOnly': 'true', 'f': 'json'})
            j, at = self.http.get_json(b, p)
            return [{'id': i} for i in (j.get('objectIds') or [])], at
        if geometry:
            p.update({'maxAllowableOffset': self.detail, 'geometryPrecision': 6})
        feats, at, off = [], '', 0
        fmt = 'geojson'
        for _page in range(50):
            q = dict(p, f=fmt)
            if off:
                q['resultOffset'] = off
            try:
                j, at = self.http.get_json(b, q)
            except SourceDown:
                if fmt == 'geojson':
                    fmt = 'json'
                    j, at = self.http.get_json(b, dict(p, f='json', **({'resultOffset': off} if off else {})))
                else:
                    raise
            if fmt == 'geojson' and j.get('type') != 'FeatureCollection':
                fmt = 'json'
                j, at = self.http.get_json(b, dict(p, f='json', **({'resultOffset': off} if off else {})))
            page = j.get('features') or []
            for ft in page:
                if fmt == 'geojson':
                    g = gj_shape(ft['geometry']) if ft.get('geometry') else None
                    props = ft.get('properties') or {}
                    fid = ft.get('id', props.get('OBJECTID', props.get('objectid')))
                else:
                    g = esri_to_shape(ft.get('geometry') or {})
                    props = ft.get('attributes') or {}
                    fid = props.get('OBJECTID', props.get('objectid'))
                if g is not None and not g.is_valid:
                    g = shapely.make_valid(g)
                feats.append({'id': fid, 'props': props, 'geom': g})
            more = j.get('exceededTransferLimit') or (j.get('properties') or {}).get('exceededTransferLimit')
            if not more or not page:
                break
            off += len(page)
        return feats, at

    # ---- one park
    def read_park(self, ref: str, area: str, window_ll, center_ll, as_line: bool = False, saved_path: str = '',
                  water_row: bool = False) -> dict:
        """{'ref', 'geom' (4326, clipped to the window), 'is_line', 'reads': [...], 'issues': [...], 'down': [...],
        'not_checked': why or '', 'records': n}"""
        src, entry = self.keys.park(ref, area)
        out = {'ref': ref, 'geom': None, 'is_line': False, 'reads': [], 'issues': [], 'down': [], 'not_checked': '',
               'records': 0, 'key': src, 'name': (entry or {}).get('n', '')}
        if entry is None and not as_line:
            out['not_checked'] = 'park is not in any boundary key that was loaded'
            return out
        win = sbox(*window_ll)
        geoms = []
        if as_line:
            # the row itself says this park was measured from its official LINE (line_source / trail row with a live line layer)
            return self._read_line(ref, entry, out, window_ll, saved_path)
        if src == 'ky':
            tracts = entry.get('tracts') or []
            if entry.get('line') or any(t[0] == 'trl' for t in tracts):
                return self._read_line(ref, entry, out, window_ll)
            usable = [t for t in tracts if t[0] in KY_LAYERS and KY_LAYERS[t[0]]]
            if not usable:
                codes = sorted({t[0] for t in tracts})
                out['not_checked'] = '; '.join(KY_NOT_LIVE_WHY.get(c, f'layer {c} has no live official layer in this tool') for c in codes) or 'no outline in the key'
                return out
            done_box = set()
            for t in usable:
                code, nm = t[0], t[1]
                L = KY_OUTLINE_FOR_WATER.get(code) if water_row and code in KY_OUTLINE_FOR_WATER else KY_LAYERS[code]
                try:
                    if L['by'] == 'box':
                        if code in done_box:
                            continue
                        done_box.add(code)
                        feats, at = self.query(L['url'], where=L.get('where', '1=1'), window=window_ll, out_fields=L['name'])
                    else:
                        feats, at = self._by_name(L['url'], L['name'], nm, window_ll)
                        mt = re.search(r'\((.+?) tract\)', str(nm), re.I)
                        if not feats and mt:
                            # the club split this tract out of a whole unit (e.g. 'Fort Heiman (Fort Donelson National
                            # Battlefield tract)'): the agency layer only has the whole unit
                            feats, at = self._by_name(L['url'], L['name'], mt.group(1), window_ll)
                            if feats:
                                out['issues'].append(f"{ref}: '{nm}' is a club-split tract; live layer read as the whole unit '{mt.group(1)}' near the spot")
                        if not feats:
                            out['issues'].append(f"{ref}: no record named '{nm}' in {short(L['url'])} near the spot")
                    out['reads'].append({'ref': ref, 'layer': layer_base(L['url']), 'how': 'box' if L['by'] == 'box' else f'name={nm}',
                                         'n': len(feats), 'read': at})
                    geoms += [f['geom'] for f in feats if f['geom'] is not None]
                    out['records'] += len(feats)
                except SourceDown as e:
                    out['down'].append(f'{ref}: {short(L["url"])}: {e}')
                    self.http.mark_down(L['url'], str(e))
                except Refused as e:
                    out['not_checked'] = str(e)
        else:
            m = entry.get('m') or []
            if not m:
                if self._line_available(ref):
                    return self._read_line(ref, entry, out, window_ll)
                out['not_checked'] = f"key has no joined official outline for {ref} (status '{entry.get('g', '?')}')"
                return out
            groups: dict[tuple[str, str, str], list] = {}
            for piece in m:
                pid, nm = piece[0], piece[1]
                if isinstance(pid, int) or (isinstance(pid, str) and pid.isdigit()):
                    url = CPCAD if area.startswith('CA-') else PADUS
                    nf = 'NAME_E' if url == CPCAD else 'Unit_Nm'
                    groups.setdefault((url, nf, ''), []).append((int(pid), nm))
                else:
                    mm = re.match(r'^([a-z]+)(\d+)$', str(pid))
                    lay = self.keys.layer_for_prefix(mm.group(1)) if mm else None
                    if not lay:
                        out['issues'].append(f'{ref}: key record {pid} names a layer prefix not in us-key/layers.json')
                        continue
                    if not lay[0].startswith('http') or re.search(r'\.zip($|\?)', lay[0], re.I):
                        out['not_checked'] = f'{ref}: layer {mm.group(1)} is a downloaded file, not a live map'
                        continue
                    groups.setdefault((lay[0], lay[1], mm.group(1)), []).append((int(mm.group(2)), nm))
            for (url, nf, pre), items in groups.items():
                try:
                    oidf = self.oid_field(url, pre)
                    ids = [i for i, _ in items]
                    names = {i: n for i, n in items}
                    near, at = [], ''
                    for chunk in chunks(ids, 100):
                        f2, at = self.query(url, object_ids=chunk, window=window_ll, out_fields=f'{oidf},{nf}' if nf else oidf)
                        near += f2
                    exist: set = set()
                    for chunk in chunks(ids, 200):
                        f3, _ = self.query(url, object_ids=chunk, ids_only=True)
                        exist |= {int(x['id']) for x in f3}
                    gone = [i for i in ids if i not in exist]
                    if gone:
                        out['issues'].append(f'{ref}: {len(gone)} key record id(s) no longer in {short(url)}: {gone[:8]}')
                    for ft in near:
                        rid = ft['id'] if ft['id'] is not None else ft['props'].get(oidf)
                        try:
                            rid = int(rid)
                        except (TypeError, ValueError):
                            pass
                        live_nm = ft['props'].get(nf) if nf else None
                        key_nm = names.get(rid)
                        if nf and key_nm and live_nm is not None and not same_name(key_nm, live_nm):
                            out['issues'].append(f"{ref}: record {pre}{rid} renamed: key '{key_nm}' -> live '{live_nm}'")
                            out['renamed'] = True
                        if ft['geom'] is not None:
                            geoms.append(ft['geom'])
                    out['records'] += len(near)
                    if gone and not near:
                        # the ids near the spot may have been renumbered: look for the park's name near the pin
                        nm0 = items[0][1]
                        alt, at2 = self._by_name(url, nf, nm0, window_ll) if nf else ([], at)
                        if alt:
                            out['issues'].append(f"{ref}: found by name '{nm0}' near the spot as new id(s) {[a['id'] for a in alt][:5]}")
                            out['renumbered'] = True
                            geoms += [a['geom'] for a in alt if a['geom'] is not None]
                    out['reads'].append({'ref': ref, 'layer': layer_base(url), 'how': f'{len(ids)} record id(s)', 'n': len(near), 'read': at})
                except SourceDown as e:
                    out['down'].append(f'{ref}: {short(url)}: {e}')
                    self.http.mark_down(url, str(e))
                except Refused as e:
                    out['not_checked'] = str(e)
        g = clip_union(geoms, win)
        lines = lines_of(g)
        if polys_of(g):
            out['geom'] = only_area(g)
        elif lines:
            out['geom'], out['is_line'] = MultiLineString(lines), True
        return out

    def _by_name(self, url, nf, nm, window_ll):
        q = str(nm).replace("'", "''")
        feats, at = self.query(url, where=f"UPPER({nf}) = UPPER('{q}')", window=window_ll, out_fields=nf)
        if not feats:
            words = main_words(nm)
            if words:
                like = '%'.join(w.upper().replace("'", "''") for w in words[:3])
                cand, at = self.query(url, where=f"UPPER({nf}) LIKE '%{like}%'", window=window_ll, out_fields=nf)
                feats = [c for c in cand if same_name(nm, c['props'].get(nf, '')) or set(words) <= set(main_words(c['props'].get(nf, '')))]
        return feats, at

    def _line_available(self, ref):
        return ref in self.keys.trails or bool(self.trails_dir and (self.trails_dir / f'{ref}.json').exists())

    def is_line_park(self, ref: str, area: str) -> bool:
        """A park the club measures from an official LINE: a live line layer is configured, the key marks it as a line,
        or the club keeps a saved line file for it."""
        if ref in self.keys.trails:
            return True
        src, entry = self.keys.park(ref, area)
        if entry and (entry.get('line') or entry.get('trl') or any((t or [None])[0] == 'trl' for t in entry.get('tracts') or [])):
            return True
        return bool(self.trails_dir and (self.trails_dir / f'{ref}.json').exists())

    def _read_line(self, ref, entry, out, window_ll, saved_path: str = ''):
        win = sbox(*window_ll)
        out['is_line'] = True
        cfg = self.keys.trails.get(ref)
        if cfg:
            try:
                feats, at = self.query(cfg['url'], where=cfg.get('where', '1=1'), window=window_ll, out_fields=cfg.get('fields', '*'))
                out['reads'].append({'ref': ref, 'layer': layer_base(cfg['url']), 'how': f"line: {cfg.get('where', '1=1')}", 'n': len(feats), 'read': at})
                g = clip_union([f['geom'] for f in feats if f['geom'] is not None], win)
                ls = lines_of(g)
                out['geom'] = MultiLineString(ls) if ls else None
                out['records'] = len(feats)
                if not feats:
                    out['issues'].append(f'{ref}: official trail line not found near the spot in {short(cfg["url"])}')
                return out
            except SourceDown as e:
                out['down'].append(f'{ref}: {short(cfg["url"])}: {e}')
                self.http.mark_down(cfg['url'], str(e))
                return out
        p = self.trails_dir / f'{ref}.json' if self.trails_dir else None
        if saved_path and self.trails_dir and not (p and p.exists()):
            p = self.trails_dir / pathlib.Path(saved_path).name
        if p and p.exists():
            try:
                d = json.loads(p.read_text(encoding='utf-8'))
                g = gj_shape(d['geometry'] if d.get('type') == 'Feature' else d)
                ls = [l for l in lines_of(g.intersection(win)) if l.length > 0]
                out['geom'] = MultiLineString(ls) if ls else None
                if not ls:
                    # a 'line' saved as zero-length pieces = trailhead points only: measure 100 ft from those points
                    pts = [Point(c) for c in shapely.get_coordinates(g) if win.contains(Point(c))]
                    if pts:
                        out['geom'] = shapely.MultiPoint(pts)
                        out.setdefault('flags', []).append(f'{ref}: saved line is only point(s): measured 100 ft from them')
                out['records'] = 1
                mtime = dt.datetime.fromtimestamp(p.stat().st_mtime, dt.timezone.utc).strftime('%Y-%m-%d')
                out['reads'].append({'ref': ref, 'layer': f'saved copy {p.name}', 'how': 'club saved official line (not re-read live)', 'n': 1, 'read': mtime})
                out['saved_line'] = True
                return out
            except (OSError, ValueError, KeyError) as e:
                out['not_checked'] = f'{ref}: saved trail line unreadable ({e})'
                return out
        out['not_checked'] = f'{ref}: trail / river park with no live official line layer configured and no saved line'
        return out

    def river_water(self, window_ll) -> tuple[list, list, list]:
        """USGS NHD river areas (NHDArea FType 460 StreamRiver) + lakes / reservoirs / estuaries (NHDWaterbody FType 390, 436, 493)
        touching the window: the water a river / water-route row is measured from (100 ft from the BANK, club rule 5).
        Returns ([(water piece clipped to the window, the whole feature's envelope, 'river' | 'lake')], reads, down)."""
        win = sbox(*window_ll)
        parts, reads, down = [], [], []
        for u, where in RIVER_WATER_QUERIES:
            try:
                f, at = self.query(u, where=where, window=window_ll, out_fields='OBJECTID,FTYPE')
                for x in f:
                    g = x['geom']
                    if g is None:
                        continue
                    c = only_area(clip_union([g], win))
                    if c is not None and not c.is_empty:
                        parts.append((c, g.envelope, 'river' if u == WATER_LAYERS[0] else 'lake'))
                reads.append({'ref': 'river water', 'layer': u, 'how': f'USGS NHD {where}', 'n': len(f), 'read': at})
            except (SourceDown, Refused) as e:
                down.append(f'USGS NHD {short(u)}: {e}')
        return parts, reads, down

    def water(self, window_ll, own_river: bool = False) -> tuple[Any, list, list]:
        """R5a COVES (ruled Oct 31): the lake / reservoir waterbody counts with its coves up to the normal water line; a separate
        NHD StreamRiver area (FType 460: a tributary above the lake) is left out unless the row's park IS that river."""
        win = sbox(*window_ll)
        gs, reads, down = [], [], []
        for u in WATER_LAYERS:
            try:
                where = '1=1' if (own_river or u != WATER_LAYERS[0]) else 'FTYPE <> 460'
                f, at = self.query(u, where=where, window=window_ll, out_fields='OBJECTID')
                gs += [x['geom'] for x in f if x['geom'] is not None]
                reads.append({'ref': 'water', 'layer': u, 'how': f'USGS NHD water in the window ({where})', 'n': len(f), 'read': at})
            except (SourceDown, Refused) as e:
                down.append(f'USGS NHD {short(u)}: {e}')
        return (only_area(clip_union(gs, win)) if gs else None), reads, down


def chunks(xs, n):
    for i in range(0, len(xs), n):
        yield xs[i:i + n]


def short(url):
    u = urllib.parse.urlsplit(url)
    path = u.path.replace('/arcgis/rest/services', '').replace('/rest/services', '')
    return u.netloc + path[:70]


def clip_union(geoms, win):
    gs = []
    for g in geoms:
        try:
            c = g.intersection(win)
        except shapely.errors.GEOSException:
            c = shapely.make_valid(g).intersection(win)
        if not c.is_empty:
            gs.append(c)
    if not gs:
        return None
    try:
        return shapely.union_all(gs)
    except shapely.errors.GEOSException:
        return shapely.union_all([shapely.make_valid(g) for g in gs])


# ================================================================= the verdict (pure: unit tested)
def compare(stored_m, stored_center_m: Point | None, live_m, water_row: bool = False, stored_acres: float | None = None) -> dict:
    """stored_m / live_m: the stored overlap and the live overlap, both polygons in metres (UTM).
    Returns {'verdict', 'why', 'live_acres', 'stored_shape_acres', 'kept_pct', 'size_pct', 'moved_m', 'gap_m', 'wide_m', 'flags',
    'live_center_m'}. Never returns SOURCE DOWN / RECORD CHANGED / NOT CHECKED (decided by the caller).
    stored_acres: the row's own 'acres'. The stored shape can be a simplified / one-piece preview of a bigger overlap (the
    club's point cap): when the live size is off against the shape but within +-25 % of the stored acres (and the stored
    shape is still inside), the size is judged against the stored acres instead."""
    S = only_area(stored_m) if stored_m is not None else Polygon()
    if S.is_empty and stored_m is not None and not stored_m.is_empty:
        S = stored_m.buffer(TRAIL_BUFFER_M)      # a stored line: its 100-ft band
    s_area = S.area
    c0 = stored_center_m if stored_center_m is not None else (S.representative_point() if not S.is_empty else None)
    comps = [p for p in polys_of(only_area(live_m) if live_m is not None else None) if p.area > 0]
    res = {'stored_shape_acres': round(s_area / ACRE_M2, 2), 'live_acres': 0.0, 'kept_pct': 0.0, 'size_pct': None,
           'moved_m': None, 'gap_m': None, 'wide_m': 0.0, 'flags': [], 'live_center_m': None}
    if water_row:
        res['flags'].append('water-only')
    total = sum(p.area for p in comps)
    if not comps or total < MIN_LIVE_M2:
        res.update(verdict='GONE', why='no overlap between the live official outlines near this spot')
        return res
    near_zone = S.buffer(NEAR_M) if not S.is_empty else (c0.buffer(NEAR_M) if c0 is not None else None)
    near = [p for p in comps if near_zone is not None and p.intersects(near_zone)]
    touched = bool(near)
    if not near:
        ref_geom = S if not S.is_empty else c0
        near = [min(comps, key=lambda p: p.distance(ref_geom))] if ref_geom is not None else comps
    U = shapely.union_all(near)
    live_area = U.area
    wide, lc = across_m(U)
    kept = (U.buffer(POS_TOL_M).intersection(S).area / s_area) if s_area > 0 else 0.0
    moved = c0.distance(lc) if (c0 is not None and lc is not None) else None
    gap = (S.distance(U) if not S.is_empty else (c0.distance(U) if c0 is not None else None))
    size = (live_area / s_area) if s_area > 0 else None
    by_acres = False
    if (size is not None and abs(size - 1) > SIZE_TOL and stored_acres and stored_acres > 0 and kept >= 1 - SIZE_TOL
            and abs(live_area / (stored_acres * ACRE_M2) - 1) <= SIZE_TOL):
        size, by_acres = live_area / (stored_acres * ACRE_M2), True
        s_area_txt = f'{stored_acres:.1f} ac stored (row acres; the stored shape is a {s_area / ACRE_M2:.1f} ac preview)'
    else:
        s_area_txt = f'{s_area / ACRE_M2:.1f} ac stored'
    res['size_vs'] = 'row acres' if by_acres else 'stored shape'
    res.update(live_acres=round(live_area / ACRE_M2, 2), kept_pct=round(100 * kept, 1), size_pct=None if size is None else round(100 * (size - 1), 1),
               moved_m=None if moved is None else round(moved), gap_m=None if gap is None else round(gap), wide_m=round(wide, 1), live_center_m=lc)
    if wide < SMALL_ACROSS_M:
        res['flags'].append('small overlap (under 50 yd across)')
    if (not touched and moved is not None and moved > MOVED_M) or (touched and kept < 0.25 and moved is not None and moved > MOVED_M):
        res.update(verdict='MOVED', why=f'live overlap centre is {moved:.0f} m from the stored centre; {100 * kept:.0f}% of the stored overlap is still inside it')
    elif size is not None and size < 1 - SIZE_TOL:
        res.update(verdict='SHRUNK', why=f'live overlap is {100 * (1 - size):.0f}% smaller ({live_area / ACRE_M2:.1f} ac vs {s_area / ACRE_M2:.1f} ac stored)')
    elif kept < 1 - SIZE_TOL:
        res.update(verdict='SHRUNK', why=f'only {100 * kept:.0f}% of the stored overlap is still inside the live overlap (10 m tolerance)')
    elif size is not None and size > 1 + SIZE_TOL:
        res.update(verdict='GREW', why=f'live overlap is {100 * (size - 1):.0f}% bigger ({live_area / ACRE_M2:.1f} ac vs {s_area / ACRE_M2:.1f} ac stored); '
                                       f'{100 * kept:.0f}% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch')
    else:
        res.update(verdict='CONFIRMED', why=f'live overlap {live_area / ACRE_M2:.1f} ac vs {s_area_txt} ({res["size_pct"]:+.0f}%), {100 * kept:.0f}% of the stored overlap still inside (10 m tolerance)')
    return res


def decide(geo: dict | None, parks: list[dict]) -> tuple[str, str]:
    """Combine the geometric verdict with what happened reading the layers."""
    down = [d for p in parks for d in p['down']]
    if down:
        return 'SOURCE DOWN', 'layer did not answer (retry later): ' + ' | '.join(down)[:600]
    nc = [p['not_checked'] for p in parks if p['not_checked']]
    if nc:
        return 'NOT CHECKED', ' | '.join(nc)[:600]
    issues = [i for p in parks for i in p['issues']]
    renamed = any(p.get('renamed') or p.get('renumbered') for p in parks)
    no_record = any(p['records'] == 0 for p in parks)
    if issues and (renamed or no_record or (geo and geo['verdict'] != 'CONFIRMED')):
        tail = f" (geometry now: {geo['verdict']}: {geo['why']})" if geo else ''
        return 'RECORD CHANGED', (' | '.join(issues) + tail)[:700]
    return geo['verdict'], geo['why'] + (('; note: ' + ' | '.join(issues)) if issues else '')


# ================================================================= one row
def row_kind(spot: dict) -> str:
    k = str(spot.get('kind') or '').lower()
    st = str(spot.get('status') or '').lower()
    if k in ('water-only', 'water only') or st.startswith('water only'):
        return 'water-only' if k in ('area', 'same land', 'water-only', 'water only', '') else k
    return k


def is_live(spot: dict) -> bool:
    st = str(spot.get('status') or '').strip().lower()
    return not (st.startswith('dropped') or st.startswith('merged'))


def load_heavy(spot: dict, fers_dir: pathlib.Path) -> dict:
    """FERS_SHAPES_SPEC: a spot with 'heavy' keeps its shape / lines / zone in data/fers/<heavy>.json.gz."""
    h = spot.get('heavy')
    if not h or spot.get('shape'):
        return spot
    for p in (fers_dir / f'{h}.json.gz', fers_dir / f'{h}.json'):
        if p.exists():
            d = json.loads(gzip.open(p, 'rt').read() if p.suffix == '.gz' else p.read_text())
            return dict(spot, **{k: d[k] for k in ('shape', 'lines', 'zone') if k in d})
    return spot


def stored_overlap_m(spot: dict, kind: str, P: 'Proj'):
    """The stored overlap in metres. Trail rows: the 'zone' band when its area agrees with the file's zone_acres (within 25%);
    the club caps a shape at 300 points, so a long band can come back as a criss-crossed outline many times too big (> 1.5x): then the
    stored stretch LINE ('shape') + 100 ft is used instead. Returns (geometry or None, note)."""
    note = ''
    if kind == 'trail':
        z = stored_geometry(spot['zone']) if spot.get('zone') else None
        zm = P.to_m(z) if z is not None else None
        za = spot.get('zone_acres')
        # a garbled outline is always far too BIG (3-13x in the club files); small bands read a bit under zone_acres
        if zm is not None and polys_of(zm) and (not za or zm.area / ACRE_M2 <= 1.5 * float(za)):
            return zm, note
        l = stored_geometry(spot.get('shape'), as_line=True)
        if l is not None:
            if zm is not None:
                note = (f"stored zone outline ({zm.area / ACRE_M2:.0f} ac) disagrees with zone_acres ({za}): "
                        f"compared against the stored stretch line + 100 ft instead")
            lm = P.to_m(l)
            return (lm.buffer(TRAIL_BUFFER_M) if not polys_of(lm) else only_area(lm)), note
        return zm, note
    g = stored_geometry(spot.get('shape'))
    g = P.to_m(g) if g is not None else None
    if g is not None and not polys_of(g) and lines_of(g):
        g = g.buffer(TRAIL_BUFFER_M)
    return g, note


RIVER_BOX_M = 1000.0
RIVER_ROUTE_M = 3000.0   # club: water within 3 km of a (coarse, ~1:100,000) water-route line is the route's water


def bank_band(line_m, water_m):
    """Pure: the land within 100 ft of the BANK of the water a river line follows, water excluded. water_m = a geometry or a
    list of (water piece, whole-feature envelope) in metres. A piece is the route's water when it lies within 3 km of the line,
    or its whole feature's box comes within 1 km of it (the club's test, which lets a coarse ~1:100,000 water-route line pick
    the big river / estuary it follows). Nothing qualifies -> None (the caller falls back to the line's own 100-ft band)."""
    if water_m is None:
        return None
    items = water_m if isinstance(water_m, list) else [(w, w.envelope) for w in polys_of(water_m)]
    if not items:
        return None
    zone = line_m.buffer(RIVER_ROUTE_M)
    pieces = [w for w, env in items if not w.is_empty and (w.intersects(zone) or env.distance(line_m) <= RIVER_BOX_M)]
    if not pieces:
        return None
    W = shapely.union_all(pieces)
    return only_area(W.buffer(TRAIL_BUFFER_M).difference(W))


WATER_ROUTE = re.compile(r'lewis (and|&) clark|trail of tears|captain john smith|star.spangled banner', re.I)


def is_water_route(spot: dict, ref: str, line_source: dict, key_name: str = '') -> bool:
    """Club rule 5: a WATER-ROUTE national historic trail follows a river; its coarse line only says WHICH water."""
    names = spot.get('names') or {}
    txt = f"{names.get(ref, '')} {key_name} {(line_source.get(ref) or {}).get('by', '')} {(line_source.get(ref) or {}).get('note', '')}"
    return bool(WATER_ROUTE.search(txt))


def river_line_band(line_m, rivers_m):
    """Pure: an ordinary river LINE (e.g. a wild & scenic river): 100 ft of its line, plus 100 ft from the bank of any NHD
    river area (StreamRiver) the line runs in. rivers_m = list of river-area polygons in metres."""
    band = line_m.buffer(TRAIL_BUFFER_M)
    touching = [w for w in rivers_m if w.intersects(band)]
    if touching:
        W = shapely.union_all(touching)
        band = shapely.union_all([band, W.buffer(TRAIL_BUFFER_M)])
    return only_area(band)


def river_band(line_m, window, reader, P, row, water_route: bool = True):
    parts, reads, down = reader.river_water(window)
    row.setdefault('layers', [])
    row['layers'] += reads
    if down:
        row.setdefault('river_note', 'NHD water did not answer: measured from the river line itself')
        row.setdefault('extra_flags', []).append('river measured from its line (NHD water did not answer)')
        return line_m.buffer(TRAIL_BUFFER_M)
    if not water_route:
        return river_line_band(line_m, [P.to_m(w) for w, e, t in parts if t == 'river'])
    band = bank_band(line_m, [(P.to_m(w), P.to_m(e)) for w, e, t in parts])
    if band is None:
        row.setdefault('extra_flags', []).append('water route measured from its line (no NHD river / lake area near it)')
        return line_m.buffer(TRAIL_BUFFER_M)
    return band


def check_spot(spot: dict, area: str, reader: ParkReader, fers_dir: pathlib.Path) -> dict:
    spot = load_heavy(spot, fers_dir)
    kind = row_kind(spot)
    refs = list(spot.get('refs') or [])
    lat, lon = spot['center']
    P = Proj(lat, lon)
    if spot.get('box'):
        x0, y0, x1, y1 = spot['box']
    else:
        x0 = x1 = lon
        y0 = y1 = lat
    dlat = WINDOW_M / 111320.0
    dlon = WINDOW_M / (111320.0 * max(0.1, math.cos(math.radians(lat))))
    window = (round(x0 - dlon, 6), round(y0 - dlat, 6), round(x1 + dlon, 6), round(y1 + dlat, 6))
    row = {'id': spot.get('id'), 'area': area, 'refs': refs, 'kind': kind, 'stored_status': spot.get('status'),
           'stored_acres': spot.get('acres', spot.get('zone_acres')), 'stored_wide_m': spot.get('wide_m', spot.get('zone_wide_m')),
           'utm_epsg': P.epsg, 'checked_at': dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}
    ls = spot.get('line_source') or {}
    if isinstance(ls, str):
        try:
            ls = json.loads(ls)
        except ValueError:
            ls = {}
    def line_ref(r):
        if r in ls:
            return True
        return kind in ('trail', 'river') and reader.is_line_park(r, area)
    # a water-route line is coarse (~1:100,000, often km off the river): read it in a window 12 km wider (it only picks the water)
    rwin = (round(window[0] - 12 * dlon, 6), round(window[1] - 12 * dlat, 6), round(window[2] + 12 * dlon, 6), round(window[3] + 12 * dlat, 6))
    parks = [reader.read_park(r, area, rwin if (kind == 'river' and line_ref(r)) else window, (lat, lon), as_line=line_ref(r),
                              saved_path=str((ls.get(r) or {}).get('line') or ''), water_row=(kind == 'water-only')) for r in refs]
    row['layers'] = [r for p in parks for r in p['reads']]
    row['saved_lines'] = [p['ref'] for p in parks if p.get('saved_line')]
    row['extra_flags'] = [f for p in parks for f in p.get('flags', [])]
    geo = None
    if not any(p['down'] for p in parks) and not any(p['not_checked'] for p in parks):
        # ---- stored overlap (metres)
        S, s_note = stored_overlap_m(spot, kind, P)
        if s_note:
            row['stored_shape_note'] = s_note
        # ---- live overlap (metres)
        L = None
        for p in parks:
            g = P.to_m(p['geom']) if p['geom'] is not None else None
            if g is None or g.is_empty:
                L = Polygon()
                break
            if (p['is_line'] or not polys_of(g)) and kind == 'river' and reader.use_water:
                g = river_band(g, window, reader, P, row, water_route=is_water_route(spot, p['ref'], ls, p.get('name', '')))
            else:
                g = g.buffer(TRAIL_BUFFER_M) if p['is_line'] or not polys_of(g) else only_area(g)
            L = g if L is None else L.intersection(g)
        if L is None:
            L = Polygon()
        water_row = kind == 'water-only'
        if water_row and reader.use_water and not L.is_empty:
            own = any(re.search(r'\briver\b|\bWSR\b|wild and scenic', str(p.get('name') or ''), re.I) for p in parks)
            W, wreads, wdown = reader.water(window, own_river=own)
            row['layers'] += wreads
            if W is not None and not wdown:
                Wm = P.to_m(W)
                wet = L.intersection(Wm)
                row['live_water_pct'] = round(100 * wet.area / L.area, 1) if L.area > 0 else 0.0
                L = only_area(wet)
            elif wdown:
                row['water_note'] = 'water layer did not answer: overlap not reduced to water; ' + '; '.join(wdown)[:200]
        if kind in ('trail', 'river') and S is not None and not S.is_empty and not L.is_empty:
            # a linear row is one STRETCH of a longer band: judge the stretch where it was stored (live band within
            # LINEAR_CLIP_M of the stored band); the whole touching live band is reported separately
            touching = [q for q in polys_of(L) if q.intersects(S.buffer(NEAR_M))]
            row['live_stretch_acres'] = round(sum(q.area for q in touching) / ACRE_M2, 2)
            Lc = only_area(L.intersection(S.buffer(LINEAR_CLIP_M)))
            if Lc is not None and Lc.area >= MIN_LIVE_M2:
                L = Lc          # else: nothing live near the stored stretch -> judge the whole live band (MOVED / GONE)
        geo = compare(S, P.to_m(Point(lon, lat)), L, water_row=water_row,
                      stored_acres=spot.get('acres') if kind in ('area', 'same land', 'water-only') else None)
        lc = geo.pop('live_center_m')
        if lc is not None:
            c = P.to_ll(lc)
            geo['live_center'] = [round(c.y, 6), round(c.x, 6)]
        if spot.get('info', {}).get('water_pct') is not None:
            row['stored_water_pct'] = spot['info']['water_pct']
        row.update(geo)
        if row['saved_lines']:
            row['flags'].append('trail line from the club saved copy (not re-read live)')
        row['flags'] += sorted(set(row.pop('extra_flags', [])))
    verdict, why = decide(geo, parks)
    row['verdict'], row['why'] = verdict, why
    row.setdefault('flags', [])
    row['flags'] += sorted(set(row.pop('extra_flags', [])))
    if kind == 'water-only' and 'water-only' not in row['flags']:
        row['flags'].append('water-only')
    return row


# ================================================================= area loop, outputs
CSV_COLS = ['id', 'area', 'refs', 'kind', 'stored_acres', 'stored_shape_acres', 'live_acres', 'size_pct', 'kept_pct',
            'distance_moved_m', 'gap_m', 'stored_wide_m', 'live_wide_m', 'verdict', 'flags', 'why', 'layer_read_dates']


def save_json_atomic(p: pathlib.Path, d):
    tmp = p.with_suffix(p.suffix + '.tmp')
    tmp.write_text(json.dumps(d, indent=1, ensure_ascii=False), encoding='utf-8')
    os.replace(tmp, p)


def summarize(rows: dict) -> dict:
    v = {k: 0 for k in VERDICTS}
    fl: dict[str, int] = {}
    for r in rows.values():
        v[r['verdict']] = v.get(r['verdict'], 0) + 1
        for f in r.get('flags') or []:
            fl[f] = fl.get(f, 0) + 1
    return {'rows': len(rows), 'verdicts': v, 'flags': fl}


def write_summary_md(out: pathlib.Path, area: str, doc: dict):
    s = doc['summary']
    lines = [f"# 2-fer accuracy check: {area}", '',
             f"Run {doc['started']} → {doc['updated']} (UTC) · tool {VERSION} · {'complete' if doc['complete'] else 'NOT complete: rerun with --resume'}",
             f"Live rows in the file: {doc['live_rows']} · checked: {s['rows']} · skipped (dropped / merged): {doc['skipped_rows']}", '',
             '| verdict | rows |', '|---|---|']
    lines += [f'| {k} | {n} |' for k, n in s['verdicts'].items() if n]
    if s['flags']:
        lines += ['', '| flag | rows |', '|---|---|'] + [f'| {k} | {n} |' for k, n in sorted(s['flags'].items())]
    look = [r for r in doc['rows'].values() if r['verdict'] not in ('CONFIRMED',)]
    if look:
        lines += ['', '## For a person to look at', '']
        for r in sorted(look, key=lambda r: (VERDICTS.index(r['verdict']) if r['verdict'] in VERDICTS else 99, r['id'] or '')):
            lines.append(f"- **{r['verdict']}** `{r['id']}`: {r['why'][:300]}")
    lines += ['', 'The 2-fer file was not changed. A person and the club waiting room decide.']
    (out / f'{area}.summary.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')


def write_csv(out: pathlib.Path):
    rows = []
    for p in sorted(out.glob('*.json')):
        try:
            d = json.loads(p.read_text(encoding='utf-8'))
        except ValueError:
            continue
        if not isinstance(d, dict) or 'rows' not in d:
            continue
        rows += list(d['rows'].values())
    with open(out / 'report.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(CSV_COLS)
        for r in rows:
            reads = '; '.join(sorted({f"{x['ref']}:{x['read'][:10]}" for x in r.get('layers') or []}))
            w.writerow([r.get('id'), r.get('area'), ' '.join(r.get('refs') or []), r.get('kind'), r.get('stored_acres'),
                        r.get('stored_shape_acres'), r.get('live_acres'), r.get('size_pct'), r.get('kept_pct'), r.get('moved_m'),
                        r.get('gap_m'), r.get('stored_wide_m'), r.get('wide_m'), r.get('verdict'), '; '.join(r.get('flags') or []),
                        r.get('why'), reads])


def run(args) -> int:
    fers_dir = pathlib.Path(args.fers_dir)
    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    extra = json.loads(pathlib.Path(args.trail_layers).read_text()) if args.trail_layers else {}
    keys = Keys(pathlib.Path(args.key_dir), extra)
    if args.neighbour_keys:
        keys.load_neighbours(args.neighbour_keys)
    http = Http(None if args.no_cache else out / '.cache', min_interval=args.min_interval, cache_hours=args.cache_hours,
                offline=args.offline)
    trails_dir = pathlib.Path(args.trails_dir) if args.trails_dir else fers_dir.parent / 'trails'
    reader = ParkReader(http, keys, detail_deg=args.detail_deg, trails_dir=trails_dir, water=not args.no_water)
    t0 = time.time()
    limit_s = args.max_minutes * 60
    stopped = False
    for area in args.areas:
        fp = fers_dir / f'{area}.json'
        if not fp.exists() and (fers_dir / f'{area}.json.gz').exists():
            fp = fers_dir / f'{area}.json.gz'
        try:
            raw = gzip.open(fp, 'rb').read() if fp.suffix == '.gz' else fp.read_bytes()
            data = json.loads(raw)
        except (OSError, ValueError) as e:
            print(f'{area}: cannot read {fp}: {e}', file=sys.stderr)
            return 2
        keys.area_key(area)
        spots = data.get('spots') or []
        live = [s for s in spots if is_live(s)]
        if args.ids:
            live = [s for s in live if s.get('id') in set(args.ids)]
        op = out / f'{area}.json'
        doc = None
        if args.resume and op.exists():
            doc = json.loads(op.read_text(encoding='utf-8'))
            if doc.get('fers_sha256') != hashlib.sha256(raw).hexdigest():
                doc['notes'] = (doc.get('notes') or []) + [f'{dt.date.today()}: the 2-fer file changed since this check started']
            ids_now = {s.get('id') for s in live}
            doc['rows'] = {k: v for k, v in doc['rows'].items() if k in ids_now and v['verdict'] != 'SOURCE DOWN'}
        if doc is None:
            doc = {'area': area, 'tool': f'kpc_fers_check.py {VERSION}', 'fers_file': str(fp), 'rows': {},
                   'started': dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}
        doc.update(fers_sha256=hashlib.sha256(raw).hexdigest(), live_rows=len(live), skipped_rows=len(spots) - len([s for s in spots if is_live(s)]),
                   rules={'trail_buffer_m': TRAIL_BUFFER_M, 'small_across_m': SMALL_ACROSS_M, 'moved_m': MOVED_M, 'size_tol': SIZE_TOL})
        todo = [s for s in live if s.get('id') not in doc['rows']]
        if args.limit:
            todo = todo[:args.limit]
        print(f'{area}: {len(spots)} rows, {len(live)} live, {len(doc["rows"])} already checked, {len(todo)} to check', flush=True)
        for i, s in enumerate(todo, 1):
            if time.time() - t0 > limit_s:
                stopped = True
                break
            try:
                r = check_spot(s, area, reader, fers_dir)
            except Exception as e:  # noqa: BLE001  (one bad row never stops the run)
                r = {'id': s.get('id'), 'area': area, 'refs': s.get('refs'), 'kind': row_kind(s), 'verdict': 'SOURCE DOWN',
                     'why': f'checker error on this row (retry; report if it repeats): {type(e).__name__}: {str(e)[:200]}', 'flags': [], 'layers': []}
            doc['rows'][r['id']] = r
            doc['updated'] = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
            doc['complete'] = len(doc['rows']) >= len(live)
            doc['summary'] = summarize(doc['rows'])
            doc['key_files'] = sorted(set(keys.files_read))
            save_json_atomic(op, doc)
            print(f"  [{i}/{len(todo)}] {r['verdict']:<14} {r['id']}  {r.get('why', '')[:110]}", flush=True)
        doc['updated'] = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        doc['complete'] = len(doc['rows']) >= len(live)
        doc['summary'] = summarize(doc['rows'])
        doc['key_files'] = sorted(set(keys.files_read))
        doc['requests_this_run'] = http.n_requests
        save_json_atomic(op, doc)
        write_summary_md(out, area, doc)
        write_csv(out)
        print(f"{area}: {json.dumps(doc['summary']['verdicts'])}", flush=True)
        if stopped:
            print(f'time limit ({args.max_minutes} min) reached: progress saved, rerun with --resume', flush=True)
            break
    write_csv(out)
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description='KPC 2-fer accuracy checker (read-only: never edits the 2-fer files)')
    ap.add_argument('--areas', nargs='+', required=True, help='e.g. US-KY US-UT US-VA (files <fers-dir>/<area>.json)')
    ap.add_argument('--resume', action='store_true', help='carry on from <out>/<area>.json (SOURCE DOWN rows are retried)')
    ap.add_argument('--fers-dir', default='data/fers')
    ap.add_argument('--key-dir', default='data', help='folder holding us-key/, ca-key/ and ky-answer-key.json')
    ap.add_argument('--trails-dir', default=None, help='saved official trail lines (default: <fers-dir>/../trails)')
    ap.add_argument('--trail-layers', default=None, help='JSON {ref: {url, where}}: more live official trail line layers')
    ap.add_argument('--neighbour-keys', nargs='*', default=[], help='extra area keys to search for parks (e.g. US-TN US-VA)')
    ap.add_argument('--out', default='fers_check')
    ap.add_argument('--max-minutes', type=float, default=50.0)
    ap.add_argument('--limit', type=int, default=0, help='at most N rows per area this run')
    ap.add_argument('--ids', nargs='*', default=None, help='only these row ids')
    ap.add_argument('--min-interval', type=float, default=1.0, help='seconds between two requests to one host')
    ap.add_argument('--cache-hours', type=float, default=20.0)
    ap.add_argument('--detail-deg', type=float, default=0.00002, help='server-side thinning (maxAllowableOffset, degrees; ~2 m)')
    ap.add_argument('--no-water', action='store_true', help='do not read USGS NHD water for water-only rows')
    ap.add_argument('--no-cache', action='store_true')
    ap.add_argument('--offline', action='store_true', help='cache only, no network (tests)')
    return run(ap.parse_args(argv))


if __name__ == '__main__':
    sys.exit(main())
