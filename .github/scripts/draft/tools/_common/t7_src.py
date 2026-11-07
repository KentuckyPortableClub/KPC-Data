#!/usr/bin/env python3
"""KPC sharp trail lines (T7, kpc_trail_lines).

Reads each national scenic / historic trail's OFFICIAL line (the NPS / USFS / BLM / partner ArcGIS layer named in the
trails list) at full detail, keeps the route attributes (land or water route, segment status), keeps it within 3 m of
the official line in a local metric projection, cuts it by state (Census TIGERweb state lines) and saves one GeoJSON
file per trail per state:  <out>/trails/<ref>/<ST>.geojson  +  <out>/trails/index.json.

It is a HELPER: it writes new files only inside --out and never edits the club's files. It decides nothing.
Rules: KPC_HOW_WE_WORK.md + the T3-T8 handoff (Part A). Run  python kpc_trail_lines.py --selftest  (no network).
"""
import argparse, gzip, hashlib, json, math, os, random, re, sys, time, urllib.error, urllib.parse, urllib.request
from datetime import datetime
from urllib.parse import urlparse

import requests

TOOL = 'kpc_trail_lines'
VERSION = '1.0 (2026-10-31)'
NPS = 'https://services1.arcgis.com/fBc8EJBxQRMcHlei/arcgis/rest/services/'
STATES_LAYER = 'https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/State_County/MapServer/0'
TOTAL_BUDGET_M = 3.0        # R-G6: the saved line stays within 3 m of the official line
DEFAULT_FETCH_OFFSET = 0.00001   # server thinning in degrees (spec: <= 0.00003); ~1.1 m at most
M_PER_DEG = 111320.0
MAX_FILE = 20 * 1024 * 1024

#@@POLITE@@


class HostResting(Exception):
    pass


class Web(Polite):
    """kpc_trail_lines' JSON reader on top of the shared polite reader (_common/polite.py, Oct 31): >= 2 s per host
    (or the robots Crawl-delay if longer), robots.txt obeyed, the one User-Agent, 429/503 -> wait and retry 3 times
    then the host rests; 500/502/504 and ArcGIS error bodies -> retried 3 times. A 403 on a data request is accepted,
    never retried, and the host (on a shared ArcGIS Online host, that one address) is marked blocked with the reason.
    A 403 (or any 4xx) on robots.txt alone is NOT a block: RFC 9309 says that means no robots rules. Dated cache,
    30-day maximum age; --offline reads only the cache."""

    def __init__(self, cache_dir, max_age_days=30, offline=False, gap=2.0):
        super().__init__(cache=cache_dir, gap=gap, timeout=180, max_bytes=400_000_000, cache_days=max_age_days,
                         log=lambda *a: print(*a, flush=True))
        self.offline = offline

    @property
    def requests(self):
        return self.stats['requests']

    def block(self, url):
        self._block(url)
        k = self._block_key(url)
        return f'BLOCKED: {k} is blocked ({self.blocked[k]}); accepted, not retried'

    def _cache_date(self, url, method, data):
        if not self.cache:
            return None
        try:
            return json.load(open(self._cache_path(url, method, data) + '.json')).get('date')
        except (OSError, ValueError):
            return None

    def get_json(self, url, params=None, timeout=180, cache=True):
        """returns (json, read_date). Raises on failure (the caller logs the item and goes on)."""
        if banned(url): raise RuntimeError(f'banned source {url}')
        q = urllib.parse.urlencode(dict(params or {}))
        full, method, data = url + ('?' + q if q else ''), 'GET', None
        if len(full) > 1800: full, method, data = url, 'POST', q   # long id lists go by POST
        host = (urlparse(url).hostname or '').lower()
        if self.offline:
            cp = self._cache_path(full, method, data) if self.cache else None
            if not (cache and cp and os.path.exists(cp)): raise RuntimeError('SOURCE DOWN: offline and not in the cache')
            return json.loads(open(cp, 'rb').read().decode('utf-8', 'replace')), self._cache_date(full, method, data) or today()
        self.timeout = timeout
        hd = {'Content-Type': 'application/x-www-form-urlencoded'} if data else None
        for attempt in range(4):
            st, _, body, _ = self.get(full, method, data, hd, nocache=not cache)
            if st == 'banned': raise RuntimeError(f'banned source {url}')
            if st == 'resting': raise HostResting(f'SOURCE DOWN: {host} is resting for this run (it kept saying busy)')
            if st == 'robots': raise RuntimeError(f'robots.txt of {host} says no')
            if st == 403:
                k = self._block_key(full)
                raise RuntimeError(f'BLOCKED: {k} is blocked ({self.blocked.get(k, "403 Forbidden on " + full)}); accepted, not retried')
            if st in (429, 503):
                self.resting.add(host)
                raise HostResting(f'SOURCE DOWN: {host} said {st} four times; resting for this run')
            if st in (500, 502, 504):
                if attempt < 3: time.sleep(10 * (attempt + 1) ** 2); continue
                self.resting.add(host)
                raise HostResting(f'SOURCE DOWN: {host} said {st} four times; resting for this run')
            if not isinstance(st, int): raise RuntimeError(f'SOURCE DOWN: {st}')
            if st != 200: raise RuntimeError(f'SOURCE DOWN: HTTP {st}')
            try:
                j = json.loads(body.decode('utf-8', 'replace'))
            except ValueError:
                self._uncache(full, method, data)
                raise RuntimeError(f'SOURCE DOWN: not JSON from {host}')
            if isinstance(j, dict) and isinstance(j.get('error'), dict):
                self._uncache(full, method, data)        # never keep an error answer in the cache
                code = j['error'].get('code')
                if code in (429, 503, 500, 502, 504) and attempt < 3:
                    time.sleep(10 * (attempt + 1)); continue
                raise RuntimeError(f"server error {code}: {str(j['error'].get('message'))[:120]}")
            return j, (self._cache_date(full, method, data) if cache else None) or today()
        raise RuntimeError(f'SOURCE DOWN: {host} kept failing')

    def _uncache(self, url, method, data):
        if self.cache:
            cp = self._cache_path(url, method, data)
            for p in (cp, cp + '.json'):
                try: os.remove(p)
                except OSError: pass


# ---------------------------------------------------------------- geometry helpers
def lazy_geo():
    global shapely, sgeom, sops, pyproj
    import shapely, shapely.geometry as sgeom, shapely.ops as sops, pyproj   # noqa: F401
    return shapely


def local_tm(lon, lat):
    """a transverse Mercator centred on the piece: metres, distortion well under 1 mm per metre within a state"""
    lazy_geo()
    crs = pyproj.CRS.from_proj4(f'+proj=tmerc +lat_0={lat:.5f} +lon_0={lon:.5f} +k=1 +x_0=0 +y_0=0 +ellps=GRS80 +units=m +no_defs')
    fwd = pyproj.Transformer.from_crs('EPSG:4326', crs, always_xy=True).transform
    back = pyproj.Transformer.from_crs(crs, 'EPSG:4326', always_xy=True).transform
    return fwd, back


def tx(f, geom):
    """apply a pyproj transform to every coordinate (vectorised)"""
    import numpy as np

    def fn(c):
        x, y = f(c[:, 0], c[:, 1])
        return np.column_stack([x, y])
    return shapely.transform(geom, fn)


def as_lines(g):
    """every LineString inside a shapely geometry"""
    if g is None or g.is_empty: return []
    t = g.geom_type
    if t == 'LineString': return [g]
    if t == 'MultiLineString': return list(g.geoms)
    if t in ('GeometryCollection',): return [x for p in g.geoms for x in as_lines(p)]
    if t == 'Polygon': return [sgeom.LineString(g.exterior.coords)] + [sgeom.LineString(r.coords) for r in g.interiors]
    if t == 'MultiPolygon': return [x for p in g.geoms for x in as_lines(p)]
    return []


def esri_to_shape(g, gtype):
    lazy_geo()
    if not g: return None
    if g.get('paths'):
        ls = [[(p[0], p[1]) for p in path if p and len(p) >= 2] for path in g['paths']]
        ls = [l for l in ls if len(l) >= 2]
        return sgeom.MultiLineString(ls) if ls else None
    if g.get('rings'):
        polys = rings_to_polys(g['rings'])
        if not polys: return None
        return sgeom.MultiPolygon(polys).buffer(0) if gtype == 'polygon' else sgeom.MultiPolygon(polys)
    return None


def rings_to_polys(rings):
    """Esri rings: clockwise = outer, others = holes in the outer that holds them"""
    lazy_geo()
    rs = [[(p[0], p[1]) for p in r] for r in rings if len(r) >= 4]

    def sa(r): return sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(r, r[1:] + r[:1])) / 2
    outs = [[r, []] for r in rs if sa(r) < 0] or [[r, []] for r in rs]
    for r in rs:
        if sa(r) >= 0 and any(o[0] is r for o in outs): continue
        if sa(r) >= 0:
            pt = sgeom.Point(r[0])
            host = next((o for o in outs if sgeom.Polygon(o[0]).contains(pt)), None)
            if host: host[1].append(r)
            else: outs.append([r, []])
    out = []
    for o, holes in outs:
        try:
            p = sgeom.Polygon(o, holes)
            if not p.is_valid: p = p.buffer(0)
            if not p.is_empty: out += list(p.geoms) if p.geom_type == 'MultiPolygon' else [p]
        except Exception:
            continue
    return out


def length_m(geom):
    """geodesic length in metres"""
    lazy_geo()
    g = pyproj.Geod(ellps='WGS84')
    return sum(g.geometry_length(l) for l in as_lines(geom))


def round_coords(geom, nd=6):
    lazy_geo()
    return shapely.set_precision(geom, 10 ** -nd) if geom is not None else geom


def simplify_m(geom, tol_m):
    """simplify in a local metric projection, keeping every point of the result within tol_m of the input line"""
    lazy_geo()
    if geom is None or geom.is_empty: return geom
    c = geom.envelope.centroid
    fwd, back = local_tm(c.x, c.y)
    g = tx(fwd, geom)
    s = g.simplify(tol_m, preserve_topology=False) if 'Line' in g.geom_type else g.simplify(tol_m, preserve_topology=True)
    if s.is_empty: s = g
    return tx(back, s)


def npoints(geom):
    lazy_geo()
    if geom is None or geom.is_empty: return 0
    return int(shapely.get_num_coordinates(geom))


# ---------------------------------------------------------------- what the attributes say
WATER_FIELD = re.compile(r'type|route|class|mode|use|water|travel', re.I)
NOT_A_TYPE_FIELD = re.compile(r'name|desc|comment|note|label|link|web|source|journey|leader|seg', re.I)
WATER_VALUE = re.compile(r'\bwater\b|water ?(route|trail)|\briver\b|\bboat|canoe|kayak|paddl|navigable|ferry|keelboat|by water', re.I)
STATUS_FIELD = re.compile(r'cert|high.?pot|stat(us?)?$|_stat|trl_?stat|trail_?stat|auto|public.?use|tour|condcat', re.I)
STATUS_SKIP = re.compile(r'^(update_sta|validationstatus|gps|publish|hist_stat)', re.I)


def route_type(attrs, default='land'):
    """('water' | 'land', why)"""
    for k, v in (attrs or {}).items():
        if isinstance(v, str) and WATER_FIELD.search(k) and not NOT_A_TYPE_FIELD.search(k) and WATER_VALUE.search(v):
            return 'water', f'the official layer says {k} = "{v.strip()}"'
    if default == 'water':
        return 'water', 'the trails list says this whole trail is a water route'
    return 'land', 'the official layer does not mark this part as a water route'


def segment_status(attrs):
    """short plain status from the layer's own fields: certified / high-potential / auto tour / <raw> / not given"""
    raw = []
    for k, v in (attrs or {}).items():
        if v in (None, '', ' ') or not isinstance(v, (str, int)) or isinstance(v, bool): continue
        if STATUS_FIELD.search(k) and not STATUS_SKIP.search(k):
            sv = str(v).strip()
            if sv.lower() in ('none', 'null', 'n/a', 'not applicable', 'unknown', '0'): continue
            raw.append(f'{k}={sv}')
    txt = ' | '.join(raw)
    low = txt.lower()
    tags = []
    if re.search(r'(?<!not )(?<!un)certified|cert_stat=yes|certification=yes', low) and 'not certified' not in low: tags.append('certified')
    if re.search(r'high.?potential(?!.{0,6}=(no|n|false))', low) and not re.search(r'high.?pot\w*=(no|n|false)', low): tags.append('high-potential')
    if 'auto tour' in low or 'autotour' in low or 'auto_tour' in low: tags.append('auto tour')
    seg = ', '.join(tags) if tags else (txt[:120] if txt else 'not given')
    return seg, txt[:300]


# ---------------------------------------------------------------- reading the official layer
def layer_info(web, url):
    """(layer_url, info json) for a FeatureServer / MapServer URL with or without a layer number"""
    url = url.rstrip('/')
    if not re.search(r'/(Feature|Map)Server/\d+$', url):
        svc, _ = web.get_json(url, {'f': 'json'})
        L = svc.get('layers') or []
        lines = [l for l in L if l.get('geometryType') == 'esriGeometryPolyline']
        if not any('geometryType' in l for l in L):   # older servers list layers without the type
            lines = []
            for l in L:
                li, _ = web.get_json(f"{url}/{l['id']}", {'f': 'json'})
                if li.get('geometryType') == 'esriGeometryPolyline': lines.append(l)
        pref = [l for l in lines if re.search(r'trail|centerline|centreline|route|nst|nht|segment|line|alignment', l.get('name', ''), re.I)
                and not re.search(r'connector|mountain bike|bike', l.get('name', ''), re.I)]
        polys = [l for l in L if l.get('geometryType') == 'esriGeometryPolygon']
        pick = (pref or lines or polys or L)
        if not pick: raise RuntimeError("CAN'T TELL: the service lists no layers")
        url = f"{url}/{pick[0]['id']}"
    info, _ = web.get_json(url, {'f': 'json'})
    if info.get('type') not in (None, 'Feature Layer') and not info.get('geometryType'):
        raise RuntimeError(f"CAN'T TELL: layer is a {info.get('type')}, not a map layer")
    return url, info


def read_layer(web, lurl, info, fetch_offset, where='1=1', geometry=None, chunk=100, deadline=None):
    """all features of the layer at full detail: list of (attrs, esri geometry). Paging by object ids."""
    oidf = info.get('objectIdField') or next((f['name'] for f in info.get('fields') or [] if f.get('type') == 'esriFieldTypeOID'), 'OBJECTID')
    p = {'where': where, 'returnIdsOnly': 'true', 'f': 'json'}
    if geometry: p.update(geometry)
    ids, _ = web.get_json(lurl + '/query', p)
    oids = sorted(ids.get('objectIds') or [])
    gtype = 'polygon' if info.get('geometryType') == 'esriGeometryPolygon' else 'line'
    out, read = [], today()
    i = 0
    while i < len(oids):
        if deadline and time.time() > deadline: raise TimeoutError('time ran out while reading')
        part = oids[i:i + chunk]
        q = {'objectIds': ','.join(map(str, part)), 'outFields': '*', 'returnGeometry': 'true', 'returnZ': 'false', 'returnM': 'false',
             'outSR': 4326, 'geometryPrecision': 6, 'f': 'json'}
        if fetch_offset and fetch_offset > 0: q['maxAllowableOffset'] = fetch_offset
        try:
            j, read = web.get_json(lurl + '/query', q, timeout=240)
        except RuntimeError:
            if chunk > 5:
                chunk = max(5, chunk // 4); continue   # a big answer or a refusal: ask for fewer at a time
            raise
        if j.get('exceededTransferLimit') and len(j.get('features') or []) < len(part) and chunk > 1:
            chunk = max(1, chunk // 4); continue
        for f in j.get('features') or []:
            out.append((f.get('attributes') or {}, f.get('geometry')))
        i += len(part)
    return out, gtype, oidf, read


def states_for(web, bbox, fetch_offset=0.0001):
    """{'VA': (name, shapely polygon)} for the Census states touching this box"""
    lazy_geo()
    q = {'where': '1=1', 'geometry': ','.join(f'{v:.5f}' for v in bbox), 'geometryType': 'esriGeometryEnvelope', 'inSR': 4326,
         'spatialRel': 'esriSpatialRelIntersects', 'outFields': 'STUSAB,NAME,OBJECTID', 'returnGeometry': 'false', 'f': 'json'}
    j, _ = web.get_json(STATES_LAYER + '/query', q)
    out = {}
    for f in j.get('features') or []:
        a = f['attributes']
        st = a.get('STUSAB')
        g, _ = web.get_json(STATES_LAYER + '/query', {'where': f"STUSAB='{st}'", 'outFields': 'STUSAB', 'returnGeometry': 'true',
                                                      'outSR': 4326, 'maxAllowableOffset': fetch_offset, 'geometryPrecision': 6, 'f': 'json'})
        fs = g.get('features') or []
        if not fs: continue
        polys = rings_to_polys(fs[0]['geometry']['rings'])
        out[st] = (a.get('NAME'), sops.unary_union(polys))
    return out


# ---------------------------------------------------------------- one trail
def build_trail(web, t, out_dir, areas, fetch_offset, deadline, states_cache):
    lazy_geo()
    ref, name = t['ref'], t.get('name') or t['ref']
    src = t.get('source_url') or t.get('url')
    if not src: raise ValueError('no source_url')
    if not src.startswith('http'): src = NPS + src
    if banned(src): raise RuntimeError(f'banned source: {src}')
    lurl, info = layer_info(web, src)
    feats, gtype, oidf, read = read_layer(web, lurl, info, fetch_offset, deadline=deadline)
    if not feats: raise RuntimeError("CAN'T TELL: the layer gave no features")
    server_m = (fetch_offset or 0) * M_PER_DEG
    tol = max(0.3, TOTAL_BUDGET_M - server_m)
    groups = {}
    for a, g in feats:
        shp = esri_to_shape(g, gtype)
        if shp is None or shp.is_empty: continue
        rt, rwhy = route_type(a, t.get('default_route_type', 'land'))
        seg, raw = segment_status(a)
        k = (rt, seg)
        grp = groups.setdefault(k, {'geoms': [], 'rwhy': rwhy, 'raw': raw, 'ids': []})
        grp['geoms'].append(shp)
        grp['ids'].append(a.get(oidf))
    if not groups: raise RuntimeError("CAN'T TELL: no usable lines came back")
    allg = sops.unary_union([g for v in groups.values() for g in v['geoms']])
    bb = allg.bounds
    pad = 0.01
    sk = tuple(round(v, 3) for v in bb)
    states = states_cache.get(sk)
    if states is None:
        states = states_for(web, (bb[0] - pad, bb[1] - pad, bb[2] + pad, bb[3] + pad))
        states_cache[sk] = states
    if not states: raise RuntimeError("CAN'T TELL: no Census state touches this line")
    union_states = sops.unary_union([p for _, p in states.values()])
    per_state = {}   # st -> list of (key, geom, extra why)
    for k, v in groups.items():
        g = sops.unary_union(v['geoms']) if gtype == 'polygon' else sops.linemerge(sops.unary_union(v['geoms'])) if len(v['geoms']) > 1 else v['geoms'][0]
        for st, (_, sp) in states.items():
            piece = g.intersection(sp)
            piece = sops.unary_union([x for x in ([piece] if gtype == 'polygon' else as_lines(piece))]) if not piece.is_empty else piece
            if not piece.is_empty and (gtype == 'polygon' or piece.length > 0):
                per_state.setdefault(st, []).append((k, piece, ''))
        rest = g.difference(union_states)
        for part in (as_lines(rest) if gtype != 'polygon' else ([rest] if not rest.is_empty else [])):
            if part.is_empty or (gtype != 'polygon' and length_m(part) < 1): continue
            st = min(states, key=lambda s: states[s][1].distance(part))
            per_state.setdefault(st, []).append((k, part, ' This piece lies just outside the Census state line (open water or a border wiggle), so it is kept with the nearest state.'))
    files, total_pts, km_total, km_water = [], 0, 0.0, 0.0
    tdir = os.path.join(out_dir, 'trails', ref)
    for st in sorted(per_state):
        if areas and st not in areas: continue
        fc = {'type': 'FeatureCollection', 'name': f'{ref} {name} ({st})', 'features': []}
        for (rt, seg), piece, extra in per_state[st]:
            s = round_coords(simplify_m(piece, tol))
            if s is None or s.is_empty: continue
            km = length_m(s) / 1000
            v = groups[(rt, seg)]
            why = (f"{name} in {states[st][0]}: the {('official corridor outline' if gtype == 'polygon' else 'official ' + rt + ' route line')} read today from "
                   f"{info.get('name') or 'the agency layer'} and kept within 3 m of it ({v['rwhy']}).")
            if rt == 'water': why += ' Water route: the 100-ft rule is measured from the river bank (water\'s edge), not from this line.'
            if gtype == 'polygon': why += ' This trail has an official corridor polygon, so it is an AREA park (test it like any park).'
            why += extra
            fc['features'].append({'type': 'Feature', 'properties': {
                'ref': ref, 'name': name, 'state': st, 'route_type': rt, 'segment': seg, 'segment_raw': v['raw'],
                'shape': 'corridor' if gtype == 'polygon' else 'line', 'km': round(km, 3), 'points': npoints(s),
                'detail_m': TOTAL_BUDGET_M, 'source_url': lurl, 'read_date': read, 'why': why},
                'geometry': sgeom.mapping(s)})
            total_pts += npoints(s); km_total += km
            if rt == 'water': km_water += km
        if not fc['features']: continue
        os.makedirs(tdir, exist_ok=True)
        fn = os.path.join(tdir, f'{st}.geojson')
        txt = json.dumps(fc, separators=(',', ':'))
        if len(txt) > MAX_FILE: raise RuntimeError(f'{st} file would be {len(txt) // 1048576} MB (over 20 MB)')
        with open(fn, 'w') as f: f.write(txt)
        files.append({'state': st, 'file': f'trails/{ref}/{st}.geojson', 'kb': len(txt) // 1024,
                      'km': round(sum(x['properties']['km'] for x in fc['features']), 2),
                      'water_km': round(sum(x['properties']['km'] for x in fc['features'] if x['properties']['route_type'] == 'water'), 2)})
    return {'ref': ref, 'name': name, 'status': 'done', 'source_url': lurl, 'layer_name': info.get('name'), 'read_date': read,
            'features_read': len(feats), 'shape': 'corridor' if gtype == 'polygon' else 'line', 'states': [f['state'] for f in files],
            'files': files, 'points': total_pts, 'km': round(km_total, 1), 'water_km': round(km_water, 1),
            'route_types': sorted({k[0] for k in groups}), 'segments': sorted({k[1] for k in groups})[:20],
            'detail_m': TOTAL_BUDGET_M, 'server_offset_deg': fetch_offset, 'simplify_m': round(tol, 2),
            'why': (f'Read {len(feats)} official records at full detail and saved {len(files)} state file(s), each within 3 m of the official line.'
                    if files else 'Read the line, but none of it falls in the states asked for.')}


# ---------------------------------------------------------------- the acceptance check (AT across Virginia)
def acceptance_at_va(web, out_dir, n=20, seed=31, ref='US-4556', st='VA'):
    """20 random points on the OFFICIAL Appalachian Trail line in Virginia (read with no thinning at all) -> distance to our
    saved file; and 20 random points on our saved line -> distance to the official line. Metres, local projection."""
    lazy_geo()
    fn = os.path.join(out_dir, 'trails', ref, f'{st}.geojson')
    saved = json.load(open(fn))
    ours = sops.unary_union([sgeom.shape(f['geometry']) for f in saved['features']])
    src = saved['features'][0]['properties']['source_url']
    info, _ = web.get_json(src, {'f': 'json'})
    states = states_for(web, ours.bounds)
    va = states[st][1]
    b = ours.bounds
    feats, gtype, _, read = read_layer(web, src, info, 0, geometry={'geometry': f'{b[0]},{b[1]},{b[2]},{b[3]}', 'geometryType': 'esriGeometryEnvelope',
                                                                      'inSR': 4326, 'spatialRel': 'esriSpatialRelIntersects'})
    off = sops.unary_union([esri_to_shape(g, gtype) for _, g in feats if g]).intersection(va)
    c = ours.envelope.centroid
    fwd, _ = local_tm(c.x, c.y)
    O, S = tx(fwd, off), tx(fwd, ours)
    rnd = random.Random(seed)

    def sample(geom, k):
        ls = as_lines(geom); tot = sum(l.length for l in ls); pts = []
        for _ in range(k):
            d = rnd.uniform(0, tot)
            for l in ls:
                if d <= l.length: pts.append(l.interpolate(d)); break
                d -= l.length
        return pts
    a = [round(S.distance(p), 3) for p in sample(O, n)]
    bb = [round(O.distance(p), 3) for p in sample(S, n)]
    res = {'test': 'Appalachian Trail across Virginia vs the official line (read with no thinning)', 'source_url': src, 'read_date': read,
           'official_points': npoints(O), 'saved_points': npoints(S), 'official_km': round(O.length / 1000, 1), 'saved_km': round(S.length / 1000, 1),
           'official_to_saved_m': a, 'saved_to_official_m': bb, 'max_m': max(a + bb), 'pass': max(a + bb) <= 3.0,
           'why': 'Every sampled point must be within 3 m (R-G6).'}
    return res


# ---------------------------------------------------------------- run
def load_state(out):
    try: return json.load(open(os.path.join(out, 'state.json')))
    except Exception: return {'done': {}, 'failed': {}}


def save_json(path, obj, indent=1):
    tmp = path + '.tmp'
    with open(tmp, 'w') as f: json.dump(obj, f, indent=indent, ensure_ascii=False)
    os.replace(tmp, path)


def read_trails(path):
    j = json.load(open(path))
    if isinstance(j, dict): j = j.get('trails') or []
    rows = []
    for x in j:
        if not isinstance(x, dict) or not x.get('ref'): continue
        if not x.get('source_url') and x.get('url'):
            x = dict(x, source_url=x['url'] if x['url'].startswith('http') else NPS + x['url'])
        rows.append(x)
    return rows


def extra_state_layers(path):
    """state trail LINE layers in data/state-gis.json (kind 'trail' / 'trails'); none are listed today (Oct 31 2026)"""
    try: j = json.load(open(path))
    except Exception: return []
    out = []
    for st, L in (j.get('states') or {}).items():
        for x in L or []:
            if str(x.get('kind', '')).lower() in ('trail', 'trails') and x.get('url'):
                out.append({'state': st, **x})
    return out


def run(args, web=None):
    t0 = time.time()
    deadline = t0 + args.max_minutes * 60
    os.makedirs(args.out, exist_ok=True)
    os.makedirs(os.path.join(args.out, 'trails'), exist_ok=True)
    os.makedirs(os.path.join(args.out, 'work'), exist_ok=True)
    try:
        trails = read_trails(args.trails)
    except Exception as e:
        print(f'FAIL bad --trails file: {e}'); return 2
    if not trails: print('FAIL the --trails file has no rows'); return 2
    if args.limit: trails = trails[:args.limit]
    areas = {a.strip().upper().replace('US-', '') for a in (args.areas or '').split(',') if a.strip()}
    web = web or Web(args.cache or os.path.join(args.out, 'work', 'cache'), offline=False)
    state = load_state(args.out) if args.resume else {'done': {}, 'failed': {}}
    state.setdefault('done', {}); state.setdefault('failed', {})
    idx_fn = os.path.join(args.out, 'trails', 'index.json')
    try: old_index = {r['ref']: r for r in json.load(open(idx_fn)).get('trails', [])} if args.resume else {}
    except Exception: old_index = {}
    index = dict(old_index)
    states_cache = {}
    left = 0
    for t in trails:
        ref = t['ref']
        if args.resume and ref in state['done']: continue
        if time.time() > deadline: left += 1; continue
        try:
            r = build_trail(web, t, args.out, areas, args.fetch_offset, deadline, states_cache)
            index[ref] = r
            state['done'][ref] = {'date': today(), 'files': len(r['files'])}
            state['failed'].pop(ref, None)
            print(f"{ref} {r['name']}: {r['features_read']} records, {len(r['files'])} state files, {r['points']} points, {r['km']} km ({r['water_km']} km water)", flush=True)
        except TimeoutError:
            left += 1; print(f'{ref}: time ran out, the next run carries on', flush=True)
        except Exception as e:   # one bad trail never stops the batch
            why = str(e)[:300]
            if not why.startswith(('SOURCE DOWN', "CAN'T TELL")): why = "CAN'T TELL: " + why
            state['failed'][ref] = {'date': today(), 'why': why}
            index[ref] = {'ref': ref, 'name': t.get('name'), 'status': 'failed', 'source_url': t.get('source_url'), 'read_date': today(),
                          'why': why + ' (tried again next run)'}
            print(f'{ref} FAILED: {why}', flush=True)
        save_json(os.path.join(args.out, 'state.json'), state)
        save_json(idx_fn, {'tool': TOOL, 'version': VERSION, 'read_date': today(), 'trails': sorted(index.values(), key=lambda r: r['ref']),
                           'state_trail_layers': extra_state_layers(args.state_gis) if args.state_gis else [],
                           'why': 'Official trail lines, one file per trail per state, each within 3 m of the official line (R-G6).'})
    if args.state_gis and not extra_state_layers(args.state_gis):
        print('note: data/state-gis.json lists no state trail LINE layers today, so only the national layers were read')
    if args.acceptance:
        try:
            res = acceptance_at_va(web, args.out)
            save_json(os.path.join(args.out, 'acceptance.json'), res)
            print(f"acceptance AT Virginia: max {res['max_m']} m -> {'PASS' if res['pass'] else 'MISSED'}")
        except Exception as e:
            print(f'acceptance check could not run: {e}')
    done = sum(1 for t in trails if t['ref'] in state['done'])
    for k, v in sorted(web.blocked.items()): print(f'blocked: {k} ({v})')
    print(f'{done} of {len(trails)} trails done, {len(state["failed"])} failed (retried next run), {left} left; {web.requests} web requests, {round((time.time() - t0) / 60, 1)} min')
    return 3 if left else 0


# ---------------------------------------------------------------- self test (no network)
class FakeWeb(Web):
    def __init__(self, fixtures):
        super().__init__(None, offline=True)
        self.fx = fixtures

    def get_json(self, url, params=None, timeout=180, cache=True):
        if banned(url): raise RuntimeError('banned')
        p = params or {}
        if url.endswith('/query') and 'STUSAB' in str(p.get('outFields', '')):
            if p.get('returnGeometry') == 'false':
                return {'features': [{'attributes': {'STUSAB': s, 'NAME': v['name']}} for s, v in self.fx['states'].items()]}, '2026-10-31'
            st = re.search(r"STUSAB='(\w+)'", p['where']).group(1)
            return {'features': [{'attributes': {'STUSAB': st}, 'geometry': {'rings': self.fx['states'][st]['rings']}}]}, '2026-10-31'
        if url.endswith('/query') and p.get('returnIdsOnly'):
            return {'objectIds': [f['attributes']['OBJECTID'] for f in self.fx['layer']['features']]}, '2026-10-31'
        if url.endswith('/query'):
            want = {int(x) for x in p['objectIds'].split(',')}
            return {'features': [f for f in self.fx['layer']['features'] if f['attributes']['OBJECTID'] in want]}, '2026-10-31'
        if re.search(r'/FeatureServer/\d+$', url): return self.fx['layer']['info'], '2026-10-31'
        return {'layers': [{'id': 0, 'name': 'Test NHT line', 'geometryType': 'esriGeometryPolyline'}]}, '2026-10-31'


def web_rules_selftest():
    """club decisions (Oct 31): one honest User-Agent, >= 2 s per host, a robots 401/403/429/5xx = STOP (Nov 7 rule);
    404/410 = no robots file (shared polite reader)"""
    problems = list(polite_selftest())
    w = Web(None, gap=1.0)
    if w.gap < 2.0: problems.append(f'gap per host is {w.gap} s, must be >= 2 s')
    if not re.fullmatch(r'KPC park tools \(.+\)', w.ua): problems.append('User-Agent must be "KPC park tools (<KPC_CONTACT>)"')
    w.gap, w.log = 0, (lambda *a: None)
    calls = []

    def fake(url, method='GET', data=None, headers=None):
        calls.append(url)
        return 403, {}, b'', url
    w._raw = fake
    for u in ('https://blocked.example.gov/a/FeatureServer/0/query', 'https://blocked.example.gov/b/FeatureServer/0/query'):
        try:
            w.get_json(u, {'f': 'json'}, cache=False); problems.append('a 403 did not raise')
        except RuntimeError as e:
            if not any(k in str(e).lower() for k in ('robots', 'blocked')): problems.append(f'403 reason missing: {e}')
    # Nov 7 standing rule: robots.txt answered 403 = STOP. Only robots.txt is asked, never the data.
    if len(calls) != 1: problems.append(f'a robots-403 host was asked {len(calls)} times (robots.txt only, then nothing more)')
    for code, stop in ((401, True), (403, True), (429, True), (500, True), (404, False), (410, False)):
        w2, calls2 = Web(None, gap=1.0), []
        w2.gap, w2.log = 0, (lambda *a: None)

        def fake2(url, method='GET', data=None, headers=None, code=code):
            calls2.append(url)
            return (code, {}, b'', url) if url.endswith('/robots.txt') else (200, {}, b'{"layers": []}', url)
        w2._raw = fake2
        try:
            j, _ = w2.get_json('https://robots4xx.example.gov/arcgis/rest/services/T/FeatureServer', {'f': 'json'}, cache=False)
            if stop: problems.append(f'robots.txt {code} must STOP the layer, but it was read ({calls2})')
            elif j != {'layers': []}: problems.append(f'robots.txt {code} (no robots file) should read the layer, got {j}')
        except Exception as e:      # noqa: BLE001
            if not stop: problems.append(f'robots.txt {code} (no robots file) must not block the layer: {e}')
            elif any(not c.endswith('/robots.txt') for c in calls2): problems.append(f'robots.txt {code}: a data request was made after the STOP ({calls2})')
    return problems


def selftest():
    here = os.path.dirname(os.path.abspath(__file__))
    tdir = os.path.join(here, 'tests')
    ok, msgs = True, []

    def check(c, m):
        nonlocal ok
        if not c: ok = False; msgs.append('FAIL ' + m)
        else: msgs.append('ok   ' + m)
    check(route_type({'TRAIL_TYPE': 'RIVER'})[0] == 'water', 'TRAIL_TYPE=RIVER is a water route (Lewis and Clark layer)')
    check(route_type({'TRTYPE': 'Water Trail'})[0] == 'water', 'TRTYPE=Water Trail is a water route (Trail of Tears layer)')
    check(route_type({'TRTYPE': 'Standard Terra Trail', 'NOTES': 'crosses the river'})[0] == 'land', 'a note about a river does not make a land route wet')
    check(segment_status({'NHTCERTSTATUS': 'Certified'})[0] == 'certified', 'certified segment')
    check(segment_status({'NHTCERTSTATUS': 'Not Certified'})[0] != 'certified', 'not-certified segment is not called certified')
    check('high-potential' in segment_status({'NHTHIGHPOTENTIALSEGMENT': 'High Potential Route Segment'})[0], 'high-potential segment')
    check('auto tour' in segment_status({'TRCLASS': 'Auto Tour Route'})[0] or 'auto tour' in segment_status({'ROUTE_STATUS': 'Auto Tour Route'})[0], 'auto tour route')
    check(banned('https://overpass-api.de/api/interpreter') and banned('https://en.wikipedia.org/x') and not banned(NPS), 'banned sources are refused')
    for m in web_rules_selftest(): check(False, m)
    check(True, 'shared polite reader: one honest User-Agent, 2 s per host, a 403 on data accepted and the host marked blocked, a 4xx on robots.txt alone is no robots rules')
    rp = Web(None, offline=True)
    check(rp.ua.startswith('KPC park tools ('), 'User-Agent is "KPC park tools (<KPC_CONTACT>)"')
    fx = json.load(open(os.path.join(tdir, 'sample_layer.json')))
    import tempfile, shutil
    out = tempfile.mkdtemp(prefix='kpc_t7_')
    try:
        trails = os.path.join(out, 'trails_in.json')
        json.dump([{'ref': 'US-0000', 'name': 'Test National Historic Trail (K4TEST)', 'source_url': 'https://example.gov/arcgis/rest/services/TEST/FeatureServer'}], open(trails, 'w'))
        a = argparse.Namespace(trails=trails, out=out, max_minutes=5, resume=False, limit=0, areas='', cache=None,
                               fetch_offset=DEFAULT_FETCH_OFFSET, state_gis=None, acceptance=False)
        code = run(a, web=FakeWeb(fx))
        check(code == 0, f'exit code 0 (got {code})')
        exp = json.load(open(os.path.join(tdir, 'expected_summary.json')))
        got = {}
        for st in exp:
            fn = os.path.join(out, 'trails', 'US-0000', f'{st}.geojson')
            if not os.path.exists(fn): got[st] = None; continue
            fc = json.load(open(fn))
            got[st] = sorted([[f['properties']['route_type'], f['properties']['segment'], f['properties']['points']] for f in fc['features']])
            for f in fc['features']:
                pr = f['properties']
                check(bool(pr['source_url']) and re.match(r'\d{4}-\d\d-\d\d$', pr['read_date']) and len(pr['why']) > 20, f'{st} row has source_url, read_date, why')
        check(got == exp, f'files per state match tests/expected_summary.json (got {json.dumps(got)})')
        # the saved line stays within 3 m of the input line
        lazy_geo()
        srcs = {rt: sops.unary_union([esri_to_shape(f['geometry'], 'line') for f in fx['layer']['features'] if route_type(f['attributes'])[0] == rt])
                for rt in ('land', 'water')}
        mx = 0
        for st in exp:
            fc = json.load(open(os.path.join(out, 'trails', 'US-0000', f'{st}.geojson')))
            for f in fc['features']:
                g = sgeom.shape(f['geometry'])
                fwd, _ = local_tm(g.centroid.x, g.centroid.y)
                stp = sgeom.Polygon(fx['states'][st]['rings'][0])
                S, O = tx(fwd, srcs[f['properties']['route_type']].intersection(stp)), tx(fwd, g)
                for p in shapely.get_coordinates(S):
                    mx = max(mx, O.distance(sgeom.Point(p)))
        check(mx <= 3.0, f'every saved point within 3 m of the source line (max {mx:.2f} m)')
        idx = json.load(open(os.path.join(out, 'trails', 'index.json')))
        check(idx['trails'][0]['status'] == 'done', 'index.json lists the trail as done')
        st = json.load(open(os.path.join(out, 'state.json')))
        check('US-0000' in st['done'], 'state.json marks it done (for --resume)')
        a.resume = True
        check(run(a, web=FakeWeb(fx)) == 0, 'a --resume run skips it and exits 0')
    finally:
        shutil.rmtree(out, ignore_errors=True)
    print('\n'.join(msgs))
    print('PASS' if ok else 'FAIL')
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description='KPC sharp trail lines (T7): official national trail lines, 3 m, one file per trail per state.')
    ap.add_argument('--trails', '--in', dest='trails', help='[{ref, name, source_url}] (built from kpc_us_trails.py list)')
    ap.add_argument('--state-gis', help='data/state-gis.json (its state trail line layers, when it lists any)')
    ap.add_argument('--out', help='output folder (the only place this tool writes)')
    ap.add_argument('--max-minutes', type=float, default=50)
    ap.add_argument('--resume', action='store_true')
    ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--areas', default='', help='US-VA,US-TN: only write these states')
    ap.add_argument('--cache', help='download cache folder kept between runs (default <out>/work/cache)')
    ap.add_argument('--fetch-offset', type=float, default=DEFAULT_FETCH_OFFSET, help='server thinning in degrees (<= 0.00003)')
    ap.add_argument('--acceptance', action='store_true', help='after the run, measure the Appalachian Trail in Virginia against the official line')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args(argv)
    if a.selftest: return selftest()
    if not a.trails or not a.out: ap.print_usage(); print('FAIL need --trails and --out'); return 2
    if a.fetch_offset > 0.00003: print('FAIL --fetch-offset must be <= 0.00003 (spec)'); return 2
    return run(a)


if __name__ == '__main__':
    sys.exit(main())
