"""Geometry helpers: Esri JSON / GeoJSON / GML -> shapely, metric distances, envelopes, rough acres.
Geometry is never stored in outputs (spec): only envelopes, rough acres and distances."""
import math, re, xml.etree.ElementTree as ET

try:
    from shapely.geometry import Point, Polygon, MultiPolygon, LineString, MultiLineString, shape
    import shapely as _shp

    def _tf(fn, g):
        """Apply a pyproj-style fn(x, y) -> (x, y) to a geometry (shapely >= 2.1 API; falls back to shapely.ops on older ones)."""
        try: return _shp.transform(g, lambda x, y: fn(x, y), interleaved=False)
        except TypeError:                      # shapely < 2.1 has no 'interleaved'
            from shapely.ops import transform as _old
            return _old(fn, g)
    import pyproj
    HAVE = True
except Exception:  # noqa: BLE001
    HAVE = False


def haversine_m(lat1, lon1, lat2, lon2):
    R = 6371008.8; p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def _signed_area(r):
    return sum(r[i][0] * r[i + 1][1] - r[i + 1][0] * r[i][1] for i in range(len(r) - 1)) / 2.0


def esri_to_shape(g):
    """Esri JSON geometry (outSR 4326) -> shapely geometry (or None)."""
    if not HAVE or not g: return None
    try:
        if 'rings' in g:
            outers, holes = [], []
            for r in g['rings']:
                if len(r) < 4: continue
                (outers if _signed_area(r) < 0 else holes).append(r)   # Esri: outer rings clockwise
            if not outers: outers, holes = holes, []
            polys = [[Polygon(o), []] for o in outers]
            for h in holes:
                hp = Polygon(h)
                for p in polys:
                    if p[0].contains(hp.representative_point()): p[1].append(h); break
            ps = [Polygon(p[0].exterior.coords, p[1]).buffer(0) for p in polys]
            return ps[0] if len(ps) == 1 else MultiPolygon([q for p in ps for q in (p.geoms if hasattr(p, 'geoms') else [p])])
        if 'paths' in g:
            ls = [LineString(p) for p in g['paths'] if len(p) > 1]
            return ls[0] if len(ls) == 1 else MultiLineString(ls)
        if 'x' in g: return Point(g['x'], g['y'])
    except Exception: return None  # noqa: BLE001
    return None


def geojson_to_shape(g):
    if not HAVE or not g: return None
    try: return shape(g)
    except Exception: return None  # noqa: BLE001


_GML = '{http://www.opengis.net/gml/3.2}'
_GML_OLD = '{http://www.opengis.net/gml}'


_NF = {}


def northing_first(epsg):
    """True when the official EPSG axis order is latitude / northing first (4326, SWEREF99 TM 3006, Stereo 70 3844 ...)."""
    epsg = str(epsg)
    if epsg not in _NF:
        try:
            ai = pyproj.CRS.from_epsg(int(epsg)).axis_info
            _NF[epsg] = bool(ai) and ai[0].direction.lower() in ('north', 'south')
        except Exception:  # noqa: BLE001
            _NF[epsg] = False
    return _NF[epsg]


def _axis_latlon(srs):
    """True when an srsName in urn / http form lists latitude or northing first (GML 3 follows the EPSG axis order)."""
    s = (srs or '').lower()
    if not ('urn:ogc:def:crs:epsg' in s or 'opengis.net/def/crs/epsg' in s): return False
    m = re.search(r'(\d{4,6})$', s)
    return bool(m) and northing_first(m.group(1))


def gml_to_shape(el, default_srs=None):
    """A GML 3 geometry element (Polygon / MultiSurface / Surface / LineString / MultiCurve) -> shapely in EPSG:4326."""
    if not HAVE or el is None: return None
    srs = el.get('srsName') or default_srs or ''
    def coords(txt, dim=2):
        v = [float(x) for x in txt.replace(',', ' ').split()]
        pts = [tuple(v[i:i + dim]) for i in range(0, len(v) - dim + 1, dim)]
        if _axis_latlon(srs): pts = [(p[1], p[0]) for p in pts]
        return pts
    polys, lines = [], []
    for ns in (_GML, _GML_OLD):
        for pg in el.iter(ns + 'Polygon'):
            ext = pg.find(f'.//{ns}exterior//{ns}posList') or pg.find(f'.//{ns}exterior//{ns}coordinates')
            if ext is None or not ext.text: continue
            dim = int(ext.get('srsDimension') or 2)
            ints = [coords(i.text, dim) for i in pg.findall(f'.//{ns}interior//{ns}posList') if i.text]
            try: polys.append(Polygon(coords(ext.text, dim), ints).buffer(0))
            except Exception: pass  # noqa: BLE001
        for ln in el.iter(ns + 'LineString'):
            pl = ln.find(f'{ns}posList')
            if pl is not None and pl.text: lines.append(LineString(coords(pl.text, int(pl.get('srsDimension') or 2))))
    g = None
    if polys: g = polys[0] if len(polys) == 1 else MultiPolygon([q for p in polys for q in (p.geoms if hasattr(p, 'geoms') else [p])])
    elif lines: g = lines[0] if len(lines) == 1 else MultiLineString(lines)
    if g is None: return None
    epsg = re.search(r'(\d{4,6})\s*$', srs)
    if epsg and epsg.group(1) not in ('4326', '4258', '4269', '4283', '4167', '6668', '4612', '4674', '84'):
        try:
            t = pyproj.Transformer.from_crs(f'EPSG:{epsg.group(1)}', 'EPSG:4326', always_xy=True)
            g = _tf(t.transform, g)
        except Exception: return None  # noqa: BLE001
    return g


def _local(lat, lon):
    return pyproj.Transformer.from_crs('EPSG:4326', pyproj.CRS.from_proj4(f'+proj=aeqd +lat_0={lat} +lon_0={lon} +datum=WGS84 +units=m'), always_xy=True)


def pin_relation(lat, lon, g):
    """(inside: bool, distance in metres from the pin to the shape's edge/line; 0 when inside)."""
    if not HAVE or g is None: return None, None
    try:
        t = _local(lat, lon); gl = _tf(t.transform, g); p = Point(0, 0)
        if gl.geom_type in ('Polygon', 'MultiPolygon'):
            if gl.contains(p): return True, 0.0
            return False, round(gl.exterior.distance(p) if gl.geom_type == 'Polygon' else gl.distance(p), 1)
        return False, round(gl.distance(p), 1)
    except Exception: return None, None  # noqa: BLE001


def acres(g, lat=None, lon=None):
    if not HAVE or g is None or g.geom_type not in ('Polygon', 'MultiPolygon'): return None
    try:
        c = g.centroid; t = _local(lat or c.y, lon or c.x)
        return round(_tf(t.transform, g).area / 4046.8564224, 1)
    except Exception: return None  # noqa: BLE001


def envelope(g):
    if not HAVE or g is None: return None
    b = g.bounds; return [round(b[0], 5), round(b[1], 5), round(b[2], 5), round(b[3], 5)]


def bbox_around(lat, lon, metres):
    dlat = metres / 111320.0; dlon = metres / (111320.0 * max(0.05, math.cos(math.radians(lat))))
    return lon - dlon, lat - dlat, lon + dlon, lat + dlat


def to_crs_bbox(bb, epsg):
    """(minlon, minlat, maxlon, maxlat) in 4326 -> (minx, miny, maxx, maxy) in EPSG:<epsg> (x/y = easting/northing)."""
    if str(epsg) in ('4326', '4258', '4269', '4283'): return bb
    t = pyproj.Transformer.from_crs('EPSG:4326', f'EPSG:{epsg}', always_xy=True)
    xs, ys = [], []
    for x, y in ((bb[0], bb[1]), (bb[0], bb[3]), (bb[2], bb[1]), (bb[2], bb[3])):
        a, b = t.transform(x, y); xs.append(a); ys.append(b)
    return min(xs), min(ys), max(xs), max(ys)


# ---- the 2-fer rule helpers (public land only, a spot >= 50 yd across, trails / rivers 100 ft from the edge) ----
YD50_M, FT100_M = 45.72, 30.48


def fer_spot(a, b, lat, lon, a_is_line=False, b_is_line=False):
    """Where two official shapes overlap, is there room for a 50-yard spot? A line (trail / river) counts as a
    corridor 100 ft either side. Returns {overlap_acres, widest_m, ok} or None. Public-land check is the caller's job
    (it must use the owner layer); this only measures the geometry."""
    if not HAVE or a is None or b is None: return None
    t = _local(lat, lon)
    A, B = _tf(t.transform, a), _tf(t.transform, b)
    if a_is_line: A = A.buffer(FT100_M)
    if b_is_line: B = B.buffer(FT100_M)
    ov = A.intersection(B)
    if ov.is_empty: return {'overlap_acres': 0.0, 'widest_m': 0.0, 'ok': False}
    widest = 0.0
    # the largest inscribed circle radius x2 = how wide the widest spot is
    try:
        from shapely import maximum_inscribed_circle
        parts = ov.geoms if hasattr(ov, 'geoms') else [ov]
        for p in parts:
            if p.geom_type == 'Polygon' and p.area > 1:
                widest = max(widest, 2 * maximum_inscribed_circle(p, tolerance=0.5).length)
    except Exception:  # noqa: BLE001  older shapely: rough fallback
        widest = 2 * math.sqrt(ov.area / math.pi)
    return {'overlap_acres': round(ov.area / 4046.8564224, 2), 'widest_m': round(widest, 1), 'ok': widest >= YD50_M}
