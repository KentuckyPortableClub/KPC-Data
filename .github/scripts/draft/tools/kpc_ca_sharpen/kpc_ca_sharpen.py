#!/usr/bin/env python3
"""KPC Canada outline sharpener (T8, kpc_ca_sharpen).

Re-reads Canadian park outlines that are saved at coarse detail from their OFFICIAL source at <= 3 m (never coarser than
5 m) and writes one file per park:  <out>/canada/<ref>.json = {ref, rings, detail_m, source_url, read_date, why, ...}.
  * ArcGIS layers (CPCAD + provincial / conservation-authority layers): objectIds query at maxAllowableOffset 0.00003 deg;
    if the server refuses, 0.00005 deg and stop.
  * BC local / regional parks: BC Data Catalogue WFS (openmaps.gov.bc.ca), full detail, then simplified by 3 m.
  * Quebec heritage sites (QC-SPC / QC-IPC): the Donnees Quebec GeoJSON downloads, full detail, simplified by 3 m.
  * Grand River CA (ON-GRCA): GRCA's open-data shapefile download, full detail, simplified by 3 m.
  * Quebec ZEC / reserves fauniques / parcs regionaux: the MRNF TRQ map service (a Donnees Quebec resource) by name.
  * ALL of a park's official records are merged into one shape (R-G6). Records saved without a number are found by name
    near the old outline. A park is written only when EVERY record answered; otherwise it is listed with the reason.
  * Very big parks (Brandon Oct 31 cap rule): each piece at 3 m if it fits 1,500 points, else 6 / 12 / 24 m, labelled.
    The uncapped copy is kept in <out>/work/full/<ref>.json.gz (2-fers must use full detail).
It is a HELPER: it writes only inside --out and never edits the club's files. It decides nothing.
Build the parks list:  python kpc_ca_sharpen.py --make-list --bounds data/canada-bounds --key data/ca-key --out OUT
Run:                   python kpc_ca_sharpen.py --parks OUT/parks.json --out OUT
Self test (no network): python kpc_ca_sharpen.py --selftest
"""
import argparse, glob, gzip, hashlib, json, math, os, re, sys, time, unicodedata, urllib.error, urllib.parse, urllib.request
import urllib.robotparser
import importlib.util as _ilu, os as _os   # noqa: E402  (owner rule, 2026-11-10: the club's one host check, before any request)
_hs = _ilu.spec_from_file_location("kpc_host_rules", _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "..", "..", "kpc_host_rules.py"))
_hr = _ilu.module_from_spec(_hs); _hs.loader.exec_module(_hr); _hr.install()

TOOL = 'kpc_ca_sharpen'
VERSION = '1.0 (2026-10-31)'
CPCAD = 'https://maps-cartes.ec.gc.ca/arcgis/rest/services/CWS_SCF/CPCAD/MapServer/0'
BC_WFS = 'https://openmaps.gov.bc.ca/geo/pub/wfs'
BC_TYPE = 'pub:WHSE_BASEMAPPING.GBA_LOCAL_REG_GREENSPACES_SP'
QC_SPC = 'https://www.donneesquebec.ca/recherche/dataset/578d182d-4897-4c11-aa7f-ee0cfed222a0/resource/5abd7e57-bfeb-49ba-a76c-93d961ae0633/download/sites_classes_pg.geojson'
QC_IPC = 'https://www.donneesquebec.ca/recherche/dataset/33a72ee0-4af3-4d76-8a13-0338e10cdaeb/resource/a82a8015-d06a-45bc-bedc-7e03399f71a8/download/terrains_protege_pg.geojson'
GRCA = 'https://data.grandriver.ca/downloads/gis/GRCA_Parks.zip'   # GRCA open data (the layer named in data/state-gis.json)
# key prefixes whose layer is not (exactly) in data/ca-key/layers.json
EXTRA_LAYERS = {'BC local and': BC_WFS, 'QC-SPC Minis': QC_SPC, 'QC-IPC Minis': QC_IPC, 'ON-GRCA Gran': GRCA}
OFFSETS = [(0.00003, 3), (0.00005, 5)]      # spec step 1: never coarser than 5 m
CAP_POINTS = 1500
CAP_STEPS = [6, 12, 24]
M_PER_DEG = 111320.0
MAX_FILE = 20 * 1024 * 1024
PROV_WORDS = {'AB': ('Alberta', 'AB-'), 'BC': ('BC',), 'MB': ('Manitoba', 'MB-'), 'NB': ('New Brunswic', 'NB'), 'NL': ('Newfoundland', 'NL'),
              'NS': ('Nova Scotia', 'NS-'), 'NT': ('NT', 'Northwest'), 'NU': ('NU', 'Nunavut'), 'ON': ('Ontario', 'ON-'), 'PE': ('PE',),
              'QC': ('Québec', 'QC-'), 'SK': ('Saskatchewan', 'SK-'), 'YT': ('Yukon', 'YT')}

# ---------------------------------------------------------------- sources we never use (Part A 6)
BANNED = ('openstreetmap.org', 'openstreetmap.fr', 'overpass-api.de', 'overpass', 'geofabrik.de', 'osm.org',
          'google.com/maps', 'maps.google', 'mymaps', 'googleapis.com/maps', 'mt0.google', 'mt1.google', 'khms',
          'alltrails.com', 'gaiagps.com', 'strava.com', 'tripadvisor.', 'yelp.', 'wikipedia.org', 'wikimedia.org',
          'protectedplanet.net', 'wdpa', 'unep-wcmc.org')


def banned(url):
    u = url.lower()
    return any(b in u for b in BANNED)


def today():
    return time.strftime('%Y-%m-%d')


# ---------------------------------------------------------------- polite web reader (Part A 5)
class HostResting(Exception):
    pass


class Web:
    """1 request every 2 s per host (or the robots Crawl-delay if longer), robots.txt obeyed, our User-Agent,
    429/503 (and other 5xx) -> wait and retry 3 times, then the host rests for the rest of the run. Cache with a date."""

    def __init__(self, cache_dir, max_age_days=30, offline=False, gap=2.0):
        contact = os.environ.get('KPC_CONTACT') or 'https://github.com/KentuckyPortableClub'
        self.ua = f'KPC park tools ({contact})'
        self.cache_dir = cache_dir
        self.max_age = max_age_days * 86400
        self.offline = offline
        self.gap = max(gap, 2.0)   # club decision (Oct 31): at least 2 s between two requests to one host
        self.blocked = {}          # club decision (Oct 31): a 403 is accepted, never retried; host -> "403 Forbidden on <url>"
        self.last = {}
        self.robots = {}
        self.resting = set()
        self.requests = 0
        if cache_dir: os.makedirs(cache_dir, exist_ok=True)

    def _wait(self, host):
        gap = max(self.gap, self.robots.get(host, (None, 0))[1] or 0)
        w = gap - (time.time() - self.last.get(host, 0))
        if w > 0: time.sleep(w)
        self.last[host] = time.time()

    def _raw(self, url, data=None, timeout=180):
        req = urllib.request.Request(url, data=data, headers={'User-Agent': self.ua, 'Accept-Encoding': 'gzip'})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            b = r.read()
            if r.headers.get('Content-Encoding') == 'gzip': b = gzip.decompress(b)
            return r.status, b, r.headers.get('Content-Type', '')

    def bkey(self, url):
        """the host; on a shared ArcGIS Online / cloud-storage host a 403 belongs to that one address only"""
        p = urllib.parse.urlparse(url)
        h = (p.hostname or '').lower()
        return h + p.path if re.search(r'(^|\.)(arcgis\.com|storage\.googleapis\.com)$', h) else p.netloc

    def block(self, url):
        k = self.bkey(url)
        self.blocked.setdefault(k, f'403 Forbidden on {url}')
        return f'BLOCKED: {k} is blocked ({self.blocked[k]}); accepted, not retried'

    def allowed(self, url):
        p = urllib.parse.urlparse(url)
        host = p.netloc
        if host not in self.robots:
            rp, delay = None, 0
            if not self.offline:
                try:
                    self._wait(host)
                    self.requests += 1
                    st, b, ct = self._raw(f'{p.scheme}://{host}/robots.txt', timeout=30)
                    t = b.decode('utf-8', 'replace')
                    # only a real robots file counts (some hosts answer every unknown path with an HTML or JSON page)
                    if st == 200 and '<html' not in t[:500].lower() and not t.lstrip().startswith('{') and re.search(r'(?im)^\s*(user-agent|disallow|allow|sitemap|crawl-delay)\s*:', t):
                        rp = urllib.robotparser.RobotFileParser()
                        rp.parse(t.splitlines())
                        try: delay = float(rp.crawl_delay(self.ua) or 0)
                        except Exception: delay = 0
                except urllib.error.HTTPError as e:
                    if e.code == 403: self.block(f'{p.scheme}://{host}/robots.txt')
                    rp = None
                except Exception:
                    rp = None   # no robots file = no rules
            self.robots[host] = (rp, min(delay, 30))
        rp = self.robots[host][0]
        return True if rp is None else rp.can_fetch(self.ua, url)

    def key(self, url, params):
        return hashlib.sha1((url + '?' + urllib.parse.urlencode(sorted((params or {}).items()))).encode()).hexdigest()

    def get_json(self, url, params=None, timeout=180, cache=True):
        """returns (json, read_date). Raises on failure (the caller logs the item and goes on)."""
        if banned(url): raise RuntimeError(f'banned source {url}')
        params = dict(params or {})
        k = self.key(url, params)
        fn = os.path.join(self.cache_dir, k[:2], k + '.json.gz') if self.cache_dir else None
        if cache and fn and os.path.exists(fn) and (self.offline or time.time() - os.path.getmtime(fn) < self.max_age):
            with gzip.open(fn, 'rt', encoding='utf-8') as f: c = json.load(f)
            return c['body'], c['read_date']
        if self.offline: raise RuntimeError('SOURCE DOWN: offline and not in the cache')
        host = urllib.parse.urlparse(url).netloc
        if host in self.resting: raise HostResting(f'SOURCE DOWN: {host} is resting for this run (it kept saying busy)')
        if not self.allowed(url): raise RuntimeError(f'robots.txt of {host} says no')
        q = urllib.parse.urlencode(params)
        full = url + ('?' + q if q else '')
        if self.bkey(url) in self.blocked: raise RuntimeError(f'BLOCKED: {self.bkey(url)} is blocked ({self.blocked[self.bkey(url)]})')
        data = None
        if len(full) > 1800: full, data = url, q.encode()   # long id lists go by POST
        err = None
        for attempt in range(4):
            self._wait(host)
            self.requests += 1
            try:
                st, b, ct = self._raw(full, data=data, timeout=timeout)
                j = json.loads(b.decode('utf-8', 'replace'))
                if isinstance(j, dict) and isinstance(j.get('error'), dict):
                    code = j['error'].get('code')
                    if code in (429, 503, 500, 502, 504) and attempt < 3:
                        time.sleep(10 * (attempt + 1)); continue
                    raise RuntimeError(f"server error {code}: {str(j['error'].get('message'))[:120]}")
                if cache and fn:
                    os.makedirs(os.path.dirname(fn), exist_ok=True)
                    with gzip.open(fn, 'wt', encoding='utf-8') as f: json.dump({'url': full, 'read_date': today(), 'body': j}, f)
                return j, today()
            except urllib.error.HTTPError as e:
                err = e
                if e.code == 403: raise RuntimeError(self.block(full))
                if e.code in (429, 500, 502, 503, 504):
                    if attempt < 3:
                        ra = e.headers.get('Retry-After') if e.headers else None
                        try: wait = min(float(ra), 120) if ra else 10 * (attempt + 1) ** 2
                        except ValueError: wait = 10 * (attempt + 1) ** 2
                        time.sleep(wait); continue
                    self.resting.add(host)
                    raise HostResting(f'SOURCE DOWN: {host} said {e.code} four times; resting for this run')
                raise RuntimeError(f'SOURCE DOWN: HTTP {e.code}')
            except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as e:
                err = e
                if attempt < 2: time.sleep(5 * (attempt + 1)); continue
                raise RuntimeError(f'SOURCE DOWN: {str(e)[:120]}')
        raise RuntimeError(f'SOURCE DOWN: {str(err)[:120]}')


def _get_bytes(self, url, timeout=300):
    """a file download (zip), same politeness and cache as get_json. Returns (bytes, read_date)."""
    if banned(url): raise RuntimeError(f'banned source {url}')
    k = self.key(url, {})
    fn = os.path.join(self.cache_dir, k[:2], k + '.bin') if self.cache_dir else None
    if fn and os.path.exists(fn) and (self.offline or time.time() - os.path.getmtime(fn) < self.max_age):
        return open(fn, 'rb').read(), time.strftime('%Y-%m-%d', time.localtime(os.path.getmtime(fn)))
    if self.offline: raise RuntimeError('SOURCE DOWN: offline and not in the cache')
    host = urllib.parse.urlparse(url).netloc
    if host in self.resting: raise HostResting(f'SOURCE DOWN: {host} is resting for this run')
    if not self.allowed(url): raise RuntimeError(f'robots.txt of {host} says no')
    if self.bkey(url) in self.blocked: raise RuntimeError(f'BLOCKED: {self.bkey(url)} is blocked ({self.blocked[self.bkey(url)]})')
    for attempt in range(4):
        self._wait(host)
        self.requests += 1
        try:
            st, b, ct = self._raw(url, timeout=timeout)
            if fn:
                os.makedirs(os.path.dirname(fn), exist_ok=True)
                open(fn, 'wb').write(b)
            return b, today()
        except urllib.error.HTTPError as e:
            if e.code == 403: raise RuntimeError(self.block(url))
            if e.code in (429, 500, 502, 503, 504) and attempt < 3: time.sleep(10 * (attempt + 1) ** 2); continue
            if e.code in (429, 503): self.resting.add(host)
            raise RuntimeError(f'SOURCE DOWN: HTTP {e.code}')
        except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as e:
            if attempt < 2: time.sleep(5 * (attempt + 1)); continue
            raise RuntimeError(f'SOURCE DOWN: {str(e)[:120]}')


Web.get_bytes = _get_bytes


# ---------------------------------------------------------------- geometry helpers
def lazy_geo():
    global shapely, sgeom, pyproj
    import shapely, shapely.geometry as sgeom, pyproj   # noqa: F401
    return shapely


def local_tm(lon, lat):
    lazy_geo()
    crs = pyproj.CRS.from_proj4(f'+proj=tmerc +lat_0={lat:.5f} +lon_0={lon:.5f} +k=1 +x_0=0 +y_0=0 +ellps=GRS80 +units=m +no_defs')
    fwd = pyproj.Transformer.from_crs('EPSG:4326', crs, always_xy=True).transform
    back = pyproj.Transformer.from_crs(crs, 'EPSG:4326', always_xy=True).transform
    return fwd, back


def tx(f, geom):
    import numpy as np

    def fn(c):
        x, y = f(c[:, 0], c[:, 1])
        return np.column_stack([x, y])
    return shapely.transform(geom, fn)


def rings_to_polys(rings):
    """Esri rings: clockwise = outer, others = holes in the outer that holds them"""
    lazy_geo()
    rs = [[(p[0], p[1]) for p in r] for r in rings if len(r) >= 4]

    def sa(r): return sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(r, r[1:] + r[:1])) / 2
    outs = [[r, []] for r in rs if sa(r) < 0] or [[r, []] for r in rs]
    for r in rs:
        if any(o[0] is r for o in outs): continue
        pt = sgeom.Point(r[0])
        host = next((o for o in outs if sgeom.Polygon(o[0]).contains(pt)), None)
        if host: host[1].append(r)
        else: outs.append([r, []])
    out = []
    for o, holes in outs:
        try:
            p = sgeom.Polygon(o, holes)
            if not p.is_valid: p = shapely.make_valid(p)
            out += polys_of(p)
        except Exception:
            continue
    return out


def polys_of(g):
    if g is None or g.is_empty: return []
    if g.geom_type == 'Polygon': return [g]
    if g.geom_type in ('MultiPolygon', 'GeometryCollection'): return [p for x in g.geoms for p in polys_of(x)]
    return []


def esri_polys(g):
    return rings_to_polys((g or {}).get('rings') or [])


def gj_polys(g):
    lazy_geo()
    if not g: return []
    try:
        s = sgeom.shape(g)
        if not s.is_valid: s = shapely.make_valid(s)
        return polys_of(s)
    except Exception:
        return []


def merge(polys):
    lazy_geo()
    if not polys: return None
    ps = [p if p.is_valid else shapely.make_valid(p) for p in polys]
    try:
        u = shapely.union_all(ps)
    except Exception:  # noqa: BLE001  GEOS side-location conflicts on near-touching copies: snap to a 1 cm grid
        try:
            u = shapely.union_all(ps, grid_size=1e-7)
        except Exception:  # noqa: BLE001
            u = shapely.union_all([shapely.make_valid(shapely.set_precision(p, 1e-7)) for p in ps], grid_size=1e-7)
    ps = polys_of(u)
    return sgeom.MultiPolygon(ps) if ps else None


def simplify_m(geom, tol_m):
    """simplify in a local metric projection (topology kept), every new edge within tol_m of the old line"""
    lazy_geo()
    if geom is None or geom.is_empty or tol_m <= 0: return geom
    c = geom.envelope.centroid
    fwd, back = local_tm(c.x, c.y)
    g = tx(fwd, geom)
    t = tol_m
    for _ in range(8):   # GEOS can drift a little past the tolerance at a ring's start point: check and tighten
        s = g.simplify(t, preserve_topology=True)
        if s.is_empty: return geom
        if shapely.hausdorff_distance(g.boundary, s.boundary) <= tol_m: break
        t *= 0.85
    else:
        s = g
    return tx(back, s)


def round6(mp):
    """6 decimals (~0.1 m), piece by piece (pieces simplified on their own may touch, which GEOS will not snap as one)"""
    lazy_geo()
    parts = []
    for p in polys_of(mp):
        try:
            q = shapely.set_precision(p, 1e-6)
        except Exception:  # noqa: BLE001
            q = shapely.set_precision(p, 1e-6, mode='pointwise')
            if not q.is_valid: q = shapely.make_valid(q)
        parts += polys_of(q)
    return sgeom.MultiPolygon(parts)


def npoints(geom):
    lazy_geo()
    return 0 if geom is None or geom.is_empty else int(shapely.get_num_coordinates(geom))


def acres(geom):
    lazy_geo()
    if geom is None or geom.is_empty: return 0.0
    return abs(pyproj.Geod(ellps='WGS84').geometry_area_perimeter(geom)[0]) / 4046.8564224


def bbox_of_gj(g):
    xs, ys = [], []

    def walk(c):
        if c and isinstance(c[0], (int, float)): xs.append(c[0]); ys.append(c[1])
        else:
            for x in c or []: walk(x)
    walk((g or {}).get('coordinates'))
    return [min(xs), min(ys), max(xs), max(ys)] if xs else None


def near(bbox, pad=0.1):
    return None if not bbox else [bbox[0] - pad, bbox[1] - pad, bbox[2] + pad, bbox[3] + pad]


def touches_bbox(geom, bbox):
    if not bbox or geom is None: return True
    lazy_geo()
    return geom.intersects(sgeom.box(*bbox))


def esri_rings(mp, nd=6):
    """rings in Esri order: each outer ring clockwise, then its holes counter-clockwise"""
    lazy_geo()
    out = []
    for p in polys_of(mp):
        p = shapely.geometry.polygon.orient(p, sign=-1.0)
        out.append([[round(x, nd), round(y, nd)] for x, y in p.exterior.coords])
        out += [[[round(x, nd), round(y, nd)] for x, y in r.coords] for r in p.interiors]
    return out


# ---------------------------------------------------------------- names
DESIG = re.compile(r'\b(national|provincial|regional|municipal|wildlife|management|conservation|ecological|nature|natural|protected|'
                   r'migratory|bird|sanctuary|area|areas|reserve|reserves|park|parks|parc|regional|site|patrimonial|historic|historique|'
                   r'zec|zone|d exploitation|controlee|reserve faunique|faunique|refuge|recreation|forest|of|canada|the|de|du|des|la|le|les|'
                   r'l|d|et|and|ca|c a|pp|wma|nwa|mbs|er|cr|islets?)\b')


def low(x):
    s = unicodedata.normalize('NFKD', str(x or '')).encode('ascii', 'ignore').decode().lower()
    return ' '.join(re.sub(r'[^a-z0-9 ]', ' ', s).split())


def core(x):
    c = ' '.join(DESIG.sub(' ', low(x)).split())
    return c or low(x)


def name_ok(want, attrs, fields=None):
    """the record's own name says it is this park (same core name, or one holds the other)"""
    w, cw = low(want), core(want)
    if not w: return True
    for k, v in (attrs or {}).items():
        if fields and k not in fields: continue
        if not isinstance(v, str) or not v.strip(): continue
        lv, cv = low(v), core(v)
        if lv == w or cv == cw: return True
        if len(cv) > 3 and len(cw) > 3 and (cv in cw or cw in cv) and min(len(cv), len(cw)) / max(len(cv), len(cw)) >= 0.6: return True
    return False


def sq(s):
    return str(s).replace("'", "''")


# ---------------------------------------------------------------- ArcGIS
class Arc:
    def __init__(self, web, deadline=None):
        self.web, self.info, self.deadline = web, {}, deadline

    def layer(self, url):
        if url not in self.info:
            j, _ = self.web.get_json(url, {'f': 'json'})
            if not j.get('geometryType') and not j.get('fields'): raise RuntimeError("CAN'T TELL: not a map layer")
            self.info[url] = j
        return self.info[url]

    def oidf(self, url):
        i = self.layer(url)
        return i.get('objectIdField') or next((f['name'] for f in i.get('fields') or [] if f.get('type') == 'esriFieldTypeOID'), 'OBJECTID')

    def name_fields(self, url):
        fs = [f['name'] for f in self.layer(url).get('fields') or [] if f.get('type') == 'esriFieldTypeString']
        pref = ['NAME_E', 'NAME_F', 'NOM_OFFICIEL', 'NOM', 'NAME', 'PARK_NAME', 'NOM_BIEN', 'TOPONYME']
        disp = self.layer(url).get('displayField') or ''
        out = [f for p in pref for f in fs if f.upper() == p]
        out += [f for f in fs if f not in out and f == disp]
        out += [f for f in fs if f not in out and re.search(r'nam|nom|topon', f, re.I) and not re.search(r'(_id|code|file|date|user|by)$', f, re.I)]
        return out[:5]

    def geoms(self, url, oids, where=None):
        """(features [(attrs, polys)], detail_m, offset, read_date): 0.00003 deg, then 0.00005 if the server refuses.
        where= reads by a name query instead of object ids (some map servers renumber their ids between queries)"""
        err = None
        for off, dm in OFFSETS:
            try:
                feats, read = [], today()
                for i in range(0, len(oids) if not where else 1, 50):
                    if self.deadline and time.time() > self.deadline: raise TimeoutError('time ran out')
                    q = {'outFields': '*', 'returnGeometry': 'true', 'returnZ': 'false',
                         'returnM': 'false', 'outSR': 4326, 'maxAllowableOffset': off, 'geometryPrecision': 6, 'f': 'json'}
                    if where: q['where'] = where
                    else: q['objectIds'] = ','.join(map(str, oids[i:i + 50]))
                    j, read = self.web.get_json(url.rstrip('/') + '/query', q, timeout=240)
                    if 'features' not in j: raise RuntimeError('the map gave no features')
                    feats += [(f.get('attributes') or {}, esri_polys(f.get('geometry'))) for f in j['features']]
                return feats, dm, off, read
            except (HostResting, TimeoutError):
                raise
            except RuntimeError as e:
                if 'robots.txt' in str(e) or 'banned' in str(e): raise
                err = e
                continue
        raise RuntimeError(f'the map refused at 3 m and at 5 m ({str(err)[:100]})')

    def ids(self, url, where='1=1', bbox=None):
        p = {'where': where, 'returnIdsOnly': 'true', 'f': 'json'}
        if bbox:
            p.update({'geometry': ','.join(f'{v:.5f}' for v in bbox), 'geometryType': 'esriGeometryEnvelope', 'inSR': 4326,
                      'spatialRel': 'esriSpatialRelIntersects'})
        j, _ = self.web.get_json(url.rstrip('/') + '/query', p)
        return sorted(j.get('objectIds') or [])

    def by_name(self, url, name, bbox):
        """object ids whose name field says this park, near the old outline"""
        nf = self.name_fields(url)
        if not nf: raise RuntimeError("CAN'T TELL: the layer has no name field")
        found, names = [], set()
        for where in (' OR '.join(f"UPPER({f}) = UPPER('{sq(name)}')" for f in nf), ' OR '.join(f"{f} = '{sq(name)}'" for f in nf)):
            try:
                found = self.ids(url, where, near(bbox))
                if found: return found, 'by name', {name}
            except (HostResting, TimeoutError):
                raise
            except RuntimeError:
                continue
        if not bbox: return [], '', set()
        # names are written differently (accents, spaces, 'C.A.'): read the names of everything near the old outline
        cand = self.ids(url, '1=1', near(bbox, 0.05))[:3000]
        oidf = self.oidf(url)
        for i in range(0, len(cand), 200):
            j, _ = self.web.get_json(url.rstrip('/') + '/query', {'objectIds': ','.join(map(str, cand[i:i + 200])), 'outFields': ','.join([oidf] + nf),
                                                                  'returnGeometry': 'false', 'f': 'json'})
            for f in j.get('features') or []:
                a = f.get('attributes') or {}
                if name_ok(name, a, nf) and a.get(oidf) is not None:
                    found.append(int(a[oidf]))
                    names |= {a[f] for f in nf if isinstance(a.get(f), str) and name_ok(name, {f: a[f]})}
        return sorted(set(found)), 'by name near the old outline', names


# ---------------------------------------------------------------- one record
def kind_of(url):
    u = (url or '').lower()
    if 'openmaps.gov.bc.ca/geo' in u and 'wfs' in u: return 'wfs'
    if u.endswith('.geojson') or u.endswith('.json'): return 'geojson'
    if u.endswith('.zip'): return 'shpzip'
    return 'arcgis'


def read_record(web, arc, rec, bbox):
    """(polys, detail_m, source_url, read_date, how) for one official record. Raises with a plain reason."""
    try:
        return read_one(web, arc, rec, bbox)
    except (HostResting, TimeoutError):
        raise
    except Exception as first:  # noqa: BLE001
        for alt in rec.get('alt_layers') or []:   # a park the key does not join: try the province's own layers by name
            if kind_of(alt) != 'arcgis': continue
            try:
                ps, dm, src, read, how = read_one(web, arc, dict(rec, layer_url=alt, record_id=None), bbox)
                return ps, dm, src, read, how + ' (not in CPCAD; found on the province layer)'
            except (HostResting, TimeoutError):
                raise
            except Exception:  # noqa: BLE001
                continue
        raise first


def read_one(web, arc, rec, bbox):
    url, rid, name = rec['layer_url'], str(rec.get('record_id') or ''), rec.get('record_name') or rec.get('name')
    k = kind_of(url)
    if k == 'arcgis':
        oid = int(rid) if rid.isdigit() else None
        if oid is not None:
            feats, dm, off, read = arc.geoms(url, [oid])
            good = [p for a, ps in feats if name_ok(name, a, arc.name_fields(url) or None) for p in ps]
            if good:
                return good, dm, f"{url}/query?objectIds={oid}&maxAllowableOffset={off}&outSR=4326&f=json", read, 'by record number (name checked)'
        oids, how, names = arc.by_name(url, name, bbox)
        if not oids: raise RuntimeError(f'no record named "{name}" on {short(url)}' + (' (the old record number now holds another name)' if oid is not None else ''))
        nf = arc.name_fields(url)
        feats, dm, off, read = arc.geoms(url, oids)
        src = f"{url}/query?objectIds={','.join(map(str, oids))}&maxAllowableOffset={off}&outSR=4326&f=json"
        polys = [p for a, ps in feats if name_ok(name, a, nf) for p in ps]
        if not polys and nf:
            # the server's object ids did not hold (seen on the MRNF TRQ map): read by the name itself
            feats = []
            where = ' OR '.join(f"{f} = '{sq(v)}'" for f in nf for v in sorted(names or {name}))
            feats, dm, off, read = arc.geoms(url, [], where=where)
            polys = [p for a, ps in feats if name_ok(name, a, nf) for p in ps]
            src = f"{url}/query?where={urllib.parse.quote(where)}&maxAllowableOffset={off}&outSR=4326&f=json"
        if bbox: polys = [p for p in polys if touches_bbox(p, near(bbox, 0.2))]
        if not polys: raise RuntimeError(f'the records found on {short(url)} do not carry the name "{name}" near the saved outline')
        if bbox and not any(touches_bbox(p, near(bbox, 0.2)) for p in polys): raise RuntimeError('the record found is far from the saved outline')
        return polys, dm, src, read, how
    if k == 'wfs':
        base = {'service': 'WFS', 'version': '2.0.0', 'request': 'GetFeature', 'typeName': BC_TYPE, 'outputFormat': 'application/json',
                'srsName': 'EPSG:4326', 'count': 50}
        feats, read, used = [], today(), None
        for flt in (f"PARK_NAME ILIKE '{sq(name)}'", f"PARK_NAME ILIKE '%{sq(core(name))}%'" if core(name) and len(core(name)) > 3 else None):
            if not flt: continue
            p = dict(base, CQL_FILTER=flt)
            j, read = web.get_json(url, p)
            feats = [f for f in j.get('features') or [] if name_ok(name, f.get('properties') or {}, ['PARK_NAME'])]
            if bbox: feats = [f for f in feats if touches_bbox(sgeom.box(*bbox_of_gj(f.get('geometry'))) if bbox_of_gj(f.get('geometry')) else None, near(bbox, 0.05))]
            if feats: used = p; break
        if not feats: raise RuntimeError(f'no BC greenspace named "{name}" near the saved outline')
        polys = [p for f in feats for p in gj_polys(f.get('geometry'))]
        return [simplify_m(p, 3.0) for p in polys], 3, url + '?' + urllib.parse.urlencode(used), read, 'BC Data Catalogue WFS by name (full detail, simplified by 3 m)'
    if k == 'shpzip':
        feats, read = shp_features(web, url)
        pick = []
        if rid.isdigit() and int(rid) < len(feats) and name_ok(name, feats[int(rid)][0]): pick = [feats[int(rid)]]
        if not pick: pick = [f for f in feats if name_ok(name, f[0])]
        if bbox: pick = [f for f in pick if any(touches_bbox(p, near(bbox, 0.05)) for p in f[1])]
        if not pick: raise RuntimeError(f'no feature named "{name}" in the download')
        return [simplify_m(p, 3.0) for f in pick for p in f[1]], 3, url, read, 'agency shapefile download (full detail, simplified by 3 m)'
    # geojson download
    j, read = web.get_json(url, None, timeout=300)
    feats = [f for f in j.get('features') or [] if name_ok(name, f.get('properties') or {})]
    if bbox: feats = [f for f in feats if any(touches_bbox(p, near(bbox, 0.05)) for p in gj_polys(f.get('geometry')))]
    if not feats: raise RuntimeError(f'no feature named "{name}" in the download')
    polys = [p for f in feats for p in gj_polys(f.get('geometry'))]
    return [simplify_m(p, 3.0) for p in polys], 3, url, read, 'Donnees Quebec download by name (full detail, simplified by 3 m)'


_SHP = {}


def shp_features(web, url):
    """[(attrs, polys in lon/lat)] from a zipped shapefile, in file order (record numbers count from 0)"""
    if url in _SHP: return _SHP[url]
    import io, zipfile, shapefile
    lazy_geo()
    b, read = web.get_bytes(url)
    z = zipfile.ZipFile(io.BytesIO(b))
    names = z.namelist()
    shp = next(n for n in names if n.lower().endswith('.shp'))
    stem = shp[:-4]
    prj = next((n for n in names if n.lower() == stem.lower() + '.prj'), None)
    r = shapefile.Reader(shp=io.BytesIO(z.read(shp)), dbf=io.BytesIO(z.read(stem + '.dbf')), shx=io.BytesIO(z.read(stem + '.shx')))
    fwd = None
    if prj:
        crs = pyproj.CRS.from_wkt(z.read(prj).decode('utf-8', 'replace'))
        if not crs.equals(pyproj.CRS('EPSG:4326')): fwd = pyproj.Transformer.from_crs(crs, 'EPSG:4326', always_xy=True).transform
    fields = [f[0] for f in r.fields[1:]]
    out = []
    for sr in r.iterShapeRecords():
        g = sgeom.shape(sr.shape.__geo_interface__)
        if fwd: g = tx(fwd, g)
        out.append((dict(zip(fields, list(sr.record))), polys_of(g if g.is_valid else shapely.make_valid(g))))
    _SHP[url] = (out, read)
    return _SHP[url]


def short(url):
    return url.split('/rest/services/')[-1][:60] if '/rest/services/' in url else urllib.parse.urlparse(url).netloc


# ---------------------------------------------------------------- the cap rule
def cap_pieces(mp, base_detail, old_detail=None):
    """each piece at base detail if it fits CAP_POINTS, else 6 / 12 / 24 m. -> (MultiPolygon, detail_m, notes).
    Never as coarse as the outline saved today (old_detail): a cap that would undo the sharpening stops one step finer."""
    lazy_geo()
    steps = [x for x in CAP_STEPS if not old_detail or x < old_detail]
    out, worst, notes = [], base_detail, []
    for p in polys_of(mp):
        n = npoints(p)
        if not CAP_POINTS or n <= CAP_POINTS:
            out.append(p); continue
        got, step = p, base_detail
        for s in steps:
            q = simplify_m(p, s)
            got, step = q, s
            if npoints(q) <= CAP_POINTS: break
        out += polys_of(got)
        worst = max(worst, step)
        notes.append(f'a piece of {n} points simplified to about {step} m ({npoints(got)} points): a very big park'
                     + ('' if npoints(got) <= CAP_POINTS else f' (still over {CAP_POINTS:,} points at {step} m, the coarsest step allowed here'
                        + (f', finer than the {old_detail} m outline saved today' if old_detail and step < 24 else '') + ')'))
    return sgeom.MultiPolygon(out), worst, notes


# ---------------------------------------------------------------- one park
def sharpen(web, arc, ref, recs, out_dir):
    lazy_geo()
    bbox = recs[0].get('old_bbox')
    polys, srcs, dets, hows, reads, used, missed = [], [], [], [], [], [], []
    for r in recs:
        try:
            ps, dm, src, read, how = read_record(web, arc, r, bbox)
            if not ps: raise RuntimeError('no shape')
        except TimeoutError:
            raise
        except Exception as e:  # noqa: BLE001
            missed.append((r, str(e)[:160])); continue
        polys += ps; srcs.append(src); dets.append(dm); hows.append(how); reads.append(read); used.append(r)
    twins = []
    for r, e in missed:
        # the same land published on two layers under the same name (R-G6: no copy counted twice): the twin that answered stands in
        t = next((u for u in used if u['layer_url'] != r['layer_url'] and core(u.get('record_name')) == core(r.get('record_name'))), None)
        if not t:
            return None, f"record {r.get('key_id') or r.get('record_id')} ({r.get('record_name') or ''}): {e}"
        twins.append(f"record {r.get('key_id')} could not be read ({e[:90]}); the same-named record {t.get('key_id')} on {short(t['layer_url'])} stands in for it")
    recs_all, recs = recs, used
    full = merge(polys)
    if full is None or full.is_empty: return None, 'the records merged into nothing'
    base = max(dets)
    capped, detail, notes = cap_pieces(full, base, recs[0].get('current_detail_m'))
    capped = round6(capped)
    rings = esri_rings(capped)
    a_new = acres(capped)
    old_pts = recs[0].get('old_points')
    why = (f"Re-read from {len(recs)} official record(s) ({'; '.join(sorted(set(short(r['layer_url']) for r in recs)))}), "
           f"{'all merged into one shape, ' if len(recs) > 1 else ''}at {base} m detail"
           f"{' (the map refused 3 m, so 5 m)' if base == 5 else ''}. "
           + (('Cap rule: ' + '; '.join(notes) + '. ') if notes else '')
           + f"The old saved outline had {old_pts} points at {str(recs[0].get('current_detail_m')) + ' m' if recs[0].get('current_detail_m') else 'coarse (unrecorded)'} detail; this one has {npoints(capped)} points, "
           f"{a_new:,.0f} acres.")
    if twins: why += ' ' + '. '.join(twins) + '.'
    ka = recs[0].get('acres_key')
    if ka and a_new and abs(a_new - ka) / max(ka, 1) > 0.25:
        why += f" Acreage differs from the Canada key's {ka:,.0f} acres by more than 25%: worth a look."
    rec = {'ref': ref, 'name': recs[0].get('name'), 'rings': rings,
           'geometry': {'type': 'MultiPolygon', 'coordinates': [[[list(c) for c in p.exterior.coords]] + [[list(c) for c in i.coords] for i in p.interiors] for p in polys_of(capped)]},
           'detail_m': detail, 'detail_label': f'simplified to about {detail} m: a very big park' if detail > base else f'{detail} m',
           'points': npoints(capped), 'pieces': len(polys_of(capped)), 'acres': round(a_new, 1), 'old_points': old_pts,
           'old_detail_m': recs[0].get('current_detail_m'), 'source_url': srcs[0], 'sources': srcs, 'how': hows,
           'read_date': min(reads), 'why': why}
    os.makedirs(os.path.join(out_dir, 'work', 'full'), exist_ok=True)
    with gzip.open(os.path.join(out_dir, 'work', 'full', ref + '.json.gz'), 'wt') as f:
        json.dump({'ref': ref, 'detail_m': base, 'why': 'uncapped copy (use for 2-fers)', 'geometry': sgeom.mapping(round6(full))}, f)
    return rec, None


# ---------------------------------------------------------------- the parks list (from data/canada-bounds + data/ca-key)
def make_list(bounds_dir, key_dir, out):
    key, prov = {}, {}
    for f in glob.glob(os.path.join(key_dir, 'CA-*.json')):
        pv = os.path.basename(f)[3:5]
        for r, v in (json.load(open(f, encoding='utf-8')).get('parks') or {}).items():
            key[r] = v; prov[r] = pv
    layers = json.load(open(os.path.join(key_dir, 'layers.json'), encoding='utf-8'))
    rows, notes = [], {}
    files = sorted(glob.glob(os.path.join(bounds_dir, 'CA-*.json')))
    if not files: raise ValueError(f'no CA-*.json files in {bounds_dir}')
    for fn in files:
        ft = json.load(open(fn, encoding='utf-8'))
        p = ft.get('properties') or {}
        d = p.get('detail_m')
        if d is not None and d <= 5: continue
        ref = p.get('ref') or os.path.basename(fn)[:-5]
        g = ft.get('geometry') or {}
        common = {'ref': ref, 'name': p.get('name'), 'province': prov.get(ref), 'current_detail_m': d, 'old_bbox': bbox_of_gj(g),
                  'old_points': sum(1 for _ in re.finditer(r'\[\s*-?\d', json.dumps(g.get('coordinates')))) // 1,
                  'set': 'no detail_m (the 273)' if d is None else 'detail_m over 5'}
        m, seen = (key.get(ref) or {}).get('m') or [], set()
        for x in m:
            rid = str(x[0])
            if rid in seen: continue
            seen.add(rid)
            if rid.isdigit():
                url, num = CPCAD, rid
            else:
                pre, _, num = rid.rpartition(':')
                urls = list(dict.fromkeys(layers.get(pre) or []))
                url = EXTRA_LAYERS.get(pre) or (urls[0] if len(urls) == 1 else None)
                if num.startswith('n-'): num = ''
                if pre in ('BC local and', 'QC-SPC Minis', 'QC-IPC Minis'): num = ''   # old record numbers do not match these sources
                if not url:
                    notes[ref] = f'record {rid}: layer not known'; continue
            rows.append(dict(common, layer_url=url, record_id=num or None, record_name=x[1], acres_key=x[2] if len(x) > 2 else None, key_id=rid))
        if not m:   # old matcher file: CPCAD by its saved name; if CPCAD has no such record, the province's own layers
            words = PROV_WORDS.get(prov.get(ref) or '', ())
            alt = list(dict.fromkeys(u for k, us in layers.items() if any(k.startswith(w) for w in words) for u in us))
            rows.append(dict(common, layer_url=CPCAD, record_id=None, record_name=p.get('cpcad') or p.get('name'), acres_key=None,
                             key_id='cpcad-by-name', alt_layers=alt))
    os.makedirs(out, exist_ok=True)
    save_json(os.path.join(out, 'parks.json'), rows)
    refs = {r['ref'] for r in rows}
    print(f'parks list: {len(refs)} parks ({sum(1 for r in {x["ref"]: x for x in rows}.values() if r["current_detail_m"] is None)} with no detail_m), '
          f'{len(rows)} records -> {out}/parks.json; {len(notes)} records with no known layer')
    return rows


# ---------------------------------------------------------------- run
def save_json(path, obj, indent=None):
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f: json.dump(obj, f, ensure_ascii=False, indent=indent)
    if os.path.getsize(tmp) > MAX_FILE: os.remove(tmp); raise ValueError(f'{path} would be over 20 MB')
    os.replace(tmp, path)


def run(args, web=None):
    try:
        rows = json.load(open(args.parks, encoding='utf-8'))
        assert isinstance(rows, list) and all('ref' in r and 'layer_url' in r for r in rows)
    except Exception as e:  # noqa: BLE001
        print(f'bad --parks file: {e}'); return 2
    out = args.out
    os.makedirs(os.path.join(out, 'canada'), exist_ok=True)
    deadline = time.time() + args.max_minutes * 60
    web = web or Web(args.cache or os.path.join(out, 'work', 'cache'))
    arc = Arc(web, deadline)
    st_fn = os.path.join(out, 'state.json')
    state = json.load(open(st_fn)) if args.resume and os.path.exists(st_fn) else {'done': {}, 'failed': {}}
    groups = {}
    for r in rows: groups.setdefault(r['ref'], []).append(r)
    areas = {a.strip().upper().replace('CA-', '') for a in (args.areas or '').split(',') if a.strip()}
    todo = [g for g, rs in groups.items() if (not areas or (rs[0].get('province') or '').upper() in areas) and g not in state['done']]
    if args.limit: todo = todo[:args.limit]
    left = False
    for i, ref in enumerate(todo):
        if time.time() > deadline: left = True; break
        try:
            rec, why = sharpen(web, arc, ref, groups[ref], out)
        except TimeoutError:
            left = True; break
        except HostResting as e:
            rec, why = None, str(e)
        except Exception as e:  # noqa: BLE001  one bad park never stops the run
            rec, why = None, f'crash on this park: {type(e).__name__}: {str(e)[:150]}'
        if rec:
            try:
                save_json(os.path.join(out, 'canada', ref + '.json'), rec)
                state['done'][ref] = {'detail_m': rec['detail_m'], 'points': rec['points'], 'set': groups[ref][0].get('set')}
                state['failed'].pop(ref, None)
            except ValueError as e:
                state['failed'][ref] = {'why': str(e), 'set': groups[ref][0].get('set')}
        else:
            state['failed'][ref] = {'why': why, 'set': groups[ref][0].get('set'), 'read_date': today()}
        print(f"{ref}: {'detail ' + str(rec['detail_m']) + ' m, ' + str(rec['points']) + ' points' if rec else 'NOT DONE: ' + why}", flush=True)
        if i % 5 == 0: save_json(st_fn, state)
    save_json(st_fn, state)
    write_index(out, groups, state)
    for k, v in sorted(web.blocked.items()): print(f'blocked: {k} ({v})')
    if left:
        print('time ran out: run again with --resume'); return 3
    return 0


def write_index(out, groups, state):
    s273 = [g for g, rs in groups.items() if rs[0].get('current_detail_m') is None]
    done = state['done']
    n5 = sum(1 for g in s273 if g in done and done[g]['detail_m'] <= 5)
    idx = {'tool': TOOL, 'version': VERSION, 'read_date': today(),
           'counts': {'parks_in_list': len(groups), 'set_no_detail_m': len(s273), 'set_no_detail_m_written': sum(1 for g in s273 if g in done),
                      'set_no_detail_m_at_or_under_5m': n5,
                      'set_no_detail_m_at_or_under_5m_before_cap': sum(1 for g in s273 if g in done),
                      'written_total': len(done), 'capped': sum(1 for v in done.values() if v['detail_m'] > 5), 'not_done': len(state['failed'])},
           'parks': [dict(ref=g, **done[g]) for g in sorted(done)],
           'not_done': [dict(ref=g, **v) for g, v in sorted(state['failed'].items())],
           'why': 'Each written park was re-read from its official records (see each file). Parks under not_done keep their old outline; '
                  'the reason is given. This tool decides nothing: the waiting room does.'}
    save_json(os.path.join(out, 'canada', 'index.json'), idx, indent=1)
    return idx


# ---------------------------------------------------------------- self test (no network)
class FakeWeb(Web):
    """answers like an ArcGIS server / the BC WFS / a GeoJSON download, from tests/fixtures.json"""

    def __init__(self, fx):
        super().__init__(None, offline=True)
        self.fx = fx

    def get_json(self, url, params=None, timeout=180, cache=True):
        if banned(url): raise RuntimeError('banned')
        p = dict(params or {})
        if url in self.fx['geojson']: return self.fx['geojson'][url], '2026-10-31'
        if url == BC_WFS:
            m = re.match(r"PARK_NAME ILIKE '(.*)'$", p.get('CQL_FILTER', ''))
            pat = re.compile('^' + re.escape(m.group(1).replace("''", "'")).replace('%', '.*') + '$', re.I)
            return {'type': 'FeatureCollection', 'features': [f for f in self.fx['wfs'] if pat.match(f['properties']['PARK_NAME'])]}, '2026-10-31'
        base = url[:-6] if url.endswith('/query') else url
        L = self.fx['arcgis'].get(base)
        if not L: raise RuntimeError('SOURCE DOWN: HTTP 404')
        if not url.endswith('/query'): return L['info'], '2026-10-31'
        feats = L['features']
        if p.get('returnIdsOnly') == 'true':
            w = p.get('where', '1=1')
            names = [v.replace("''", "'") for v in re.findall(r"'((?:[^']|'')*)'\)?(?: OR |$)", w)]
            sel = [f for f in feats if w == '1=1' or any(str(v).upper() == n.upper() for n in names for k, v in f['attributes'].items() if isinstance(v, str))]
            if 'geometry' in p:
                b = [float(x) for x in p['geometry'].split(',')]
                sel = [f for f in sel if any(b[0] <= x <= b[2] and b[1] <= y <= b[3] for r in f['geometry']['rings'] for x, y in r)]
            return {'objectIds': [f['attributes']['OBJECTID'] for f in sel]}, '2026-10-31'
        if L.get('refuse_3m') and str(p.get('maxAllowableOffset')) == '3e-05':
            raise RuntimeError('server error 400: Unable to complete operation.')
        ids = {int(x) for x in str(p.get('objectIds', '')).split(',') if x}
        out = [{'attributes': f['attributes'], **({'geometry': f['geometry']} if p.get('returnGeometry') != 'false' else {})} for f in feats if f['attributes']['OBJECTID'] in ids]
        return {'objectIdFieldName': 'OBJECTID', 'features': out}, '2026-10-31'


def web_rules_selftest():
    """club decisions (Oct 31): one honest User-Agent, >= 2 s per host, a 403 accepted and the host marked blocked"""
    import io
    problems = []
    w = Web(None, gap=1.0)
    if w.gap < 2.0: problems.append(f'gap per host is {w.gap} s, must be >= 2 s')
    if not re.fullmatch(r'KPC park tools \(.+\)', w.ua): problems.append('User-Agent must be "KPC park tools (<KPC_CONTACT>)"')
    calls = []

    def fake(url, data=None, timeout=180):
        calls.append(url)
        raise urllib.error.HTTPError(url, 403, 'Forbidden', {}, io.BytesIO(b''))
    w._raw, w._wait = fake, (lambda host: None)
    for u in ('https://blocked.example.gov/a/FeatureServer/0/query', 'https://blocked.example.gov/b/FeatureServer/0/query'):
        try:
            w.get_json(u, {'f': 'json'}, cache=False); problems.append('a 403 did not raise')
        except RuntimeError as e:
            if 'BLOCKED' not in str(e) or '403 Forbidden on https://blocked.example.gov/' not in str(e): problems.append(f'403 reason missing: {e}')
    if len(calls) != 1: problems.append(f'a 403 host was asked {len(calls)} times (robots.txt, then nothing more)')
    if not w.blocked.get('blocked.example.gov', '').startswith('403 Forbidden on '): problems.append(f'host not marked blocked: {w.blocked}')
    return problems


def selftest():
    here = os.path.dirname(os.path.abspath(__file__))
    fx = json.load(open(os.path.join(here, 'tests', 'fixtures.json'), encoding='utf-8'))
    exp = json.load(open(os.path.join(here, 'tests', 'expected_summary.json'), encoding='utf-8'))
    import tempfile
    ok = True

    def check(c, m):
        nonlocal ok
        print(('  ok   ' if c else '  FAIL ') + m)
        ok = ok and bool(c)
    with tempfile.TemporaryDirectory() as td:
        rows = make_list(os.path.join(here, 'tests', 'make_list', 'canada-bounds'), os.path.join(here, 'tests', 'make_list', 'ca-key'), os.path.join(td, 'ml'))
        check(sorted((r['ref'], r['layer_url'], r['record_id']) for r in rows) == [tuple(x) for x in exp['make_list']], 'parks list built from canada-bounds + ca-key')
        a = argparse.Namespace(parks=os.path.join(here, 'tests', 'sample_parks.json'), out=os.path.join(td, 'o'), max_minutes=5, resume=False,
                               limit=0, areas='', cache=None)
        code = run(a, web=FakeWeb(fx))
        check(code == 0, f'exit code 0 (got {code})')
        idx = json.load(open(os.path.join(td, 'o', 'canada', 'index.json')))
        got = {p['ref']: p['detail_m'] for p in idx['parks']}
        got.update({p['ref']: 'not done' for p in idx['not_done']})
        check(got == exp['detail_m'], f'detail per park {got}')
        for ref in got:
            fn = os.path.join(td, 'o', 'canada', ref + '.json')
            if got[ref] == 'not done':
                check(not os.path.exists(fn), f'{ref}: no file when a record did not answer'); continue
            r = json.load(open(fn))
            check(all(r.get(k) not in (None, '') for k in ('ref', 'rings', 'detail_m', 'source_url', 'read_date', 'why')), f'{ref}: has ref, rings, detail_m, source_url, read_date, why')
            check(re.match(r'^\d{4}-\d{2}-\d{2}$', r['read_date']) is not None, f'{ref}: read_date is YYYY-MM-DD')
            check(not re.search(r'\b(YES|NO)\b', json.dumps(r)), f'{ref}: decides nothing (no YES / NO)')
        big = json.load(open(os.path.join(td, 'o', 'canada', 'T-3.json')))
        check(all(npoints(sgeom.Polygon(big['rings'][0])) <= CAP_POINTS for _ in [0]) and 'very big park' in big['why'], 'cap rule: big piece fits 1,500 points and says so')
        check(os.path.exists(os.path.join(td, 'o', 'work', 'full', 'T-3.json.gz')), 'cap rule: full-detail copy kept in work/')
        two = json.load(open(os.path.join(td, 'o', 'canada', 'T-1.json')))
        check(len(two['sources']) == 2 and two['pieces'] == 1, 'all records merged into one shape')
        tw = json.load(open(os.path.join(td, 'o', 'canada', 'T-7.json')))
        check('stands in' in tw['why'], 'a record that cannot be read is covered only by its same-named twin, and the why says so')
        # 3 m check: every source vertex of the full-detail WFS park lies within 3 m of the saved line
        g = json.load(open(os.path.join(td, 'o', 'canada', 'T-4.json')))
        src = sgeom.shape(fx['wfs'][0]['geometry'])
        sv = sgeom.MultiPolygon([sgeom.Polygon(g['rings'][0])])
        fwd, _ = local_tm(src.centroid.x, src.centroid.y)
        a1, b1 = tx(fwd, src.exterior), tx(fwd, sv.geoms[0].exterior)
        dmax = max(b1.distance(sgeom.Point(c)) for c in a1.coords)
        check(dmax <= 3.0, f'simplified line within 3 m of the source ({dmax:.2f} m)')
        check(all(not banned(u) for u in [CPCAD, BC_WFS, QC_SPC, QC_IPC, GRCA]), 'no banned source')
        for m in web_rules_selftest(): check(False, m)
        check(True, 'one honest User-Agent, 2 s per host, a 403 is accepted and the host marked blocked')
    print('PASS' if ok else 'FAIL')
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--parks', '--in', dest='parks', help='parks list [{ref, layer_url, record_id, current_detail_m, ...}]')
    ap.add_argument('--out', help='output folder (the only place this tool writes)')
    ap.add_argument('--max-minutes', type=float, default=50)
    ap.add_argument('--resume', action='store_true', help='skip parks already in <out>/state.json')
    ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--areas', default='', help='provinces, e.g. QC,BC')
    ap.add_argument('--cache', default=None, help='cache folder (default <out>/work/cache)')
    ap.add_argument('--make-list', action='store_true', help='build <out>/parks.json from --bounds and --key')
    ap.add_argument('--bounds', help='data/canada-bounds folder (for --make-list)')
    ap.add_argument('--key', help='data/ca-key folder (for --make-list)')
    ap.add_argument('--cap-points', type=int, default=CAP_POINTS, help='cap rule: points a piece may keep at 3 m (0 = no cap); default 1500')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args(argv)
    globals()['CAP_POINTS'] = a.cap_points
    if a.selftest: return selftest()
    if not a.out: print('--out is needed'); return 2
    if a.make_list:
        try:
            make_list(a.bounds, a.key, a.out)
        except Exception as e:  # noqa: BLE001
            print(f'bad input: {e}'); return 2
        if not a.parks: return 0
    if not a.parks: print('--parks is needed'); return 2
    return run(a)


if __name__ == '__main__':
    sys.exit(main())
