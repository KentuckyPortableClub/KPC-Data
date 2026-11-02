#!/usr/bin/env python3
"""KPC parcel tracer (spec KPC_3_Parcel_Tracer_Spec): an APPROXIMATE park outline from agency-owned parcels.

For a park with no official GIS boundary, start from the parcel under the POTA pin (or the nearest agency-owned
parcel within 500 m), add parcels with the same government owner that touch or lie within 200 m of the growing
shape, stop when none connect, and dissolve them into one outline graded "approximate (agency parcels)".

  python kpc_parcel_trace.py --parks parks.json --all --out out/
  python kpc_parcel_trace.py --parks parks.json --refs US-10172,US-9739 --out out/
  python kpc_parcel_trace.py --selftest            # no network, prints PASS or FAIL

Built on kpc_parcels (T4): its polite web reader (one honest User-Agent, >= 2 s per host, robots.txt,
403 accepted and the host marked blocked), its ArcGIS helpers (Layer, jget, query_point, field picking) and its
owner-type keywords and zoning / damage-assessment refusals are imported, not copied.
It looks for kpc_parcels.py in ../kpc_parcels (or the folder in $KPC_PARCELS_DIR).

In:  parks.json  [{ref, name, state_or_prov, lat, lon, agency_owner_names: [...], parcel_layer_url,
                   known_acres?, county_fips?, owner_field?, pid_field?, owner_source? ("dfrp")}]
     (owner_field / pid_field: name the layer's owner / parcel-id field when the automatic pick gets it wrong)
     owner_aliases.json (optional)  {agency or owner name: [other spellings used on parcels]}
Out: <out>/parcels/<area>.json  FeatureCollection, one feature per DRAWN park (area = state_or_prov, e.g. US-KY)
     <out>/parcels/report.csv   ref,status,why,name,n_parcels,acres,pin_dist_m,acres_check,layer_url,read_date,
                                excluded_by_other_park,known_acres,known_acres_source,size_ratio
                                (pin_dist_m = the pin's distance from the final outline, 0 when inside; written
                                 whenever an outline was computed, including NEEDS A PERSON and PIN FAR rows)
     <out>/state.json            (for --resume; results are saved after every park)
Status: DRAWN / OWNER UNCLEAR / NO PARCEL / PIN FAR / NEEDS A PERSON / ERROR.
NEEDS A PERSON (club decision, Oct 31): the area is outside 0.2x-2x of the known size, or the trace was cut off
at --max-km; no outline is written, the reason is in report.csv. Known size: the official acres list
(--official-acres, kpc_acres acres.json / acres-list.json) first, the round-14 known_acres only when the park is not
in it; the source used is in the why and report.csv known_acres_source (columns known_acres, size_ratio too).
Lake-surface layers: --state-gis (default KPC-Data data/state-gis.json). Kentucky outline files: a second
--official-dir (the club points it at the website repo's folder at install).
Canada: parks with "owner_source": "dfrp" use the federal Directory of Federal Real Property; the custodian is the
owner, used only when it is the park's managing agency (agency_owner_names).
Other parks (club decision, Oct 31): a parcel is never taken in, as the seed or in growth, when at least 50% of its
area (INSIDE_SHARE, measured in UTM) lies inside ANOTHER POTA park's official outline. Only official-graded outlines
count (the 2-fer line's answer keys data/us-key and data/ca-key with g == "official" and no "approx" join and no
lake-surface layer, the Kentucky answer key over the ky-*.geojson files, and official-*.geojson files with grade
"official"); the park's own outline never counts. The other outlines come from --official-dir (default
$KPC_OFFICIAL_DIR, else the KPC-Data data/ folder when this file sits in KPC-Data). Excluded parcel ids and the other
park's ref are in the why, report.csv excluded_by_other_park and the feature property excluded_other_park. When every
agency parcel within 500 m is excluded the park is NEEDS A PERSON. When no official data covers an area, the why says so.
403s: a 403 on robots.txt alone means no robots rules (RFC 9309) and the layer is still read; only a 403 on the
data request itself marks the host blocked (no retry), and that park is an ERROR "blocked: ...".  Exit: 0 done, 3 time ran out (run again with
--resume), 2 bad input.
"""
import argparse, csv, json, math, os, re, sys, time
from urllib.parse import urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
_KP_DIR = os.environ.get('KPC_PARCELS_DIR') or os.path.join(HERE, '..', 'kpc_parcels')
sys.path.insert(0, os.path.abspath(_KP_DIR))
try:
    import kpc_parcels as kp          # the T4 tool: polite reader + ArcGIS parcel-layer helpers
except ImportError as e:              # pragma: no cover
    sys.exit(f'kpc_parcels.py not found next to this tool ({_KP_DIR}); set KPC_PARCELS_DIR. ({e})')

from pyproj import CRS, Transformer
from rapidfuzz import fuzz
import numpy as np
import shapely
from shapely import make_valid
from shapely.geometry import Point, Polygon, MultiPolygon, box, mapping, shape
from shapely.ops import unary_union

GRADE = 'approximate (agency parcels)'      # rule 2: always, never official
SEED_M = 500.0            # nearest agency parcel to the pin, at most this far (rule 3)
ADJ_M = 200.0             # a parcel joins when it touches or lies within 200 m of the growing shape (rule 3)
try:   # Nov 2 review: tracer limits (kpc_trace_limits.py in .github/scripts/draft; switches, defaults = today)
    sys.path.insert(0, os.path.abspath(os.path.join(HERE, '..', '..'))); import kpc_trace_limits as TL
except Exception:  # noqa: BLE001
    TL = None
if TL is not None: ADJ_M = TL.num('KPC_PARCEL_ADJ_M')            # review suggests 30
GROW_CAP = TL.num('KPC_PARCEL_GROW_CAP') if TL else 0.0          # x the official acres; review suggests 1.25; 0 = no cap
SUBTRACT_OTHERS = TL is not None and TL.on('KPC_PARCEL_SUBTRACT')
FIRST_M = 1000.0          # first envelope around the pin
PIN_FAR_M = 1000.0        # rule 4: pin outside the result by more than this -> no output
SLIVER_M2 = 0.1 * 4046.8564224              # 0.1 ac
SIMPLIFY_M = 3.0
MATCH_MIN = 0.90          # rapidfuzz ratio (0..1) needed for an owner match
MAX_FEATURES = 30000      # per park, a guard against ever sweeping a county
HELD = 'NEEDS A PERSON'   # club decision, Oct 31: a failed size check or a cut-off trace is held back (no outline)
SIZE_LO, SIZE_HI = 0.2, 2.0   # club decision, Oct 31 (round 4): more than 2x the official size (or under 0.2x) is held back


def load_official_acres(paths, log=print):
    """The club's official acres list, one size per POTA ref. Reads kpc_acres output: acres.json
    ({ref: {acres, agency, source_url, record_name, flags, ...}}) or acres-list.json ({ref: acres}); also a plain
    list of {ref, acres}. The first file that has a ref wins. Returns {ref: {acres, source, ...}}."""
    out = {}
    for path in paths or []:
        try:
            d = json.load(open(path))
        except (OSError, ValueError) as e:
            log(f'official acres list {path}: not read ({e})')
            continue
        rows = d.get('parks', d) if isinstance(d, dict) else d
        items = rows.items() if isinstance(rows, dict) else ((r.get('ref'), r) for r in rows if isinstance(r, dict))
        n = 0
        for ref, v in items:
            if not ref or ref in out:
                continue
            e = dict(v) if isinstance(v, dict) else {'acres': v}
            try:
                e['acres'] = float(e.get('acres'))
            except (TypeError, ValueError):
                continue
            if e['acres'] <= 0:
                continue
            e['file'] = path
            out[ref] = e
            n += 1
        log(f'official acres list {path}: {n} park sizes')
    return out


def known_size(pk):
    """(acres, source text) for the size check: the official acres list first, the round-14 figure only if the park
    has none there, else (None, why)."""
    oa = pk.get('_official_acres')
    if oa:
        bits = [x for x in (oa.get('agency'), oa.get('record_name') and f'"{oa["record_name"]}"') if x]
        src = (f'official acres list ({os.path.basename(oa["file"])}' + (': ' + ', '.join(bits) if bits else '') + ')'
               + (f' {oa["source_url"]}' if oa.get('source_url') else '')
               + (f'; list flags: {", ".join(map(str, oa["flags"]))}' if oa.get('flags') else ''))
        return oa['acres'], src
    if pk.get('known_acres'):
        return float(pk['known_acres']), ('round-14 figure (parks.json known_acres; the park is not in the official acres '
                                          'list' + ('' if pk.get('_acres_list_loaded') else ', no official acres list given') + ')')
    return None, ('no official size: not in the official acres list' if pk.get('_acres_list_loaded')
                  else 'no official size: no official acres list given') + ' and no round-14 figure'
# Canada (club decision, Oct 31): the federal Directory of Federal Real Property (PSPC / TBS), its public property
# boundaries layer. The custodian is the owner, and it is used ONLY when it is the park's managing agency
# (agency_owner_names). Every DFRP custodian is a federal department, agency or Crown corporation by the register's
# own definition, so a custodian name read from it counts as a government owner.
DFRP_URL = 'https://idgsi-rpgdi-arcgis.spac-pspc.gc.ca/gisserver/rest/services/Hosted/DFRP_PUBLIC/FeatureServer/4'
DFRP_FIELDS = {'owner_field': 'custodian_en', 'pid_field': 'property_number'}
ACRES_M2 = 4046.8564224

# Rule 5: official government parcel sources only. On top of kpc_parcels' banned list (OSM, Google, ...):
NOT_PARCEL_SOURCE = re.compile(
    r'(^|\.)(regrid\.com|landgrid\.com|reportallusa\.com|reportall\.com|loveland\.com|zillow\.com|realtor\.com|'
    r'redfin\.com|trulia\.com|loopnet\.com|landwatch\.com|acrevalue\.com|propertyshark\.com|parcelquest\.com|'
    r'county-?gis\.com|beacon\.schneidercorp\.com|schneidercorp\.com|qpublic\.net|openstreetmap\.org)$', re.I)


# Field picking: these are tried before kpc_parcels' own lists. A full owner name beats a truncated OWNER1
# (WV: OWNER1 'WEST VIRGINIA DIVISION' vs FullOwnerName 'WEST VIRGINIA DIVISION OF NATURAL RESOURCES'), and
# statewide parcel ids (NC parno, VT SPAN, MA MAP_PAR_ID, WV CleanParcelID) beat map / block numbers.
OWNER_FIRST = [re.compile(r'^(full_?owner_?name|owner_?full_?name|ownerfull)$', re.I)]
PID_FIRST = [re.compile(r'^(parno|span|map_par_id|cleanparcelid|parcel_?id|parcelid|parcel_?no|parcelnumb|'
                        r'parcel_number|pin|apn|gispid)$', re.I)]


class Blocked(Exception):
    """The DATA request itself was refused (403): accepted, never retried, the host is marked blocked (club decision 3).
    A 403 on robots.txt alone is not this: it means no robots rules (RFC 9309) and the layer is still read."""


def blocked_msg(u):
    return (f'blocked: the data request was refused (403 Forbidden on {u}); accepted with no retry and the host '
            'marked blocked for this run (club decision 3)')


class TimeUp(Exception):
    pass


def source_refused(url):
    """Why this layer URL may not be a parcel source, or None."""
    if not url:
        return 'no parcel layer URL in the club workbook'
    host = (urlparse(url).hostname or '').lower()
    if kp.banned(url) or NOT_PARCEL_SOURCE.search(host):
        return f'{host} is not an official government parcel source (rule 5)'
    if kp.ZONING.search(url):
        return 'a zoning layer (zoning is not ownership; never a parcel source, club decision Oct 31)'
    if kp.NOT_OWNERSHIP.search(url):
        return 'a damage-assessment / analysis layer, not ownership (club decision Oct 31)'
    if not re.search(r'/(MapServer|FeatureServer)/\d+/?$', url, re.I):
        return 'not an ArcGIS REST layer address (…/MapServer/<n> or …/FeatureServer/<n>); nothing to query'
    return None


# ------------------------------------------------------------------ owner names
_ABBR = [  # (regex on the normalised string, replacement)
    (r'\bDEPTS?\b|\bDEP\b|\bDPT\b', 'DEPARTMENT'), (r'\bDIV\b', 'DIVISION'),
    (r'\bCOMM(N|SN|ISSN|ISS|ISION)?\b|\bCOMMS\b|\bCMSN\b', 'COMMISSION'),
    (r'\bGOVT\b|\bGOV\b', 'GOVERNMENT'), (r'\bNATL\b', 'NATIONAL'), (r'\bNAT\b', 'NATURAL'),
    (r'\bRES\b|\bRESOURCE\b|\bRESRCS\b', 'RESOURCES'), (r'\bWILDL\b|\bWLDLF\b', 'WILDLIFE'),
    (r'\bCONSV\b|\bCONSERV\b', 'CONSERVATION'), (r'\bREC\b', 'RECREATION'), (r'\bAUTH\b', 'AUTHORITY'),
    (r'\bKDFWR\b', 'KENTUCKY DEPARTMENT OF FISH AND WILDLIFE RESOURCES'),
    (r'\bDNR\b', 'DEPARTMENT OF NATURAL RESOURCES'), (r'\bTVA\b', 'TENNESSEE VALLEY AUTHORITY'),
    (r'\bDCR\b', 'DEPARTMENT OF CONSERVATION AND RECREATION'),
    (r'\bU S A\b|\bU S\b|\bUSA\b|\bUNITED STATES OF AMERICA\b|\bUS\b', 'UNITED STATES'),
    (r'\bST OF\b', 'STATE OF'), (r'\bCOMMONWEALTH OF\b|\bCOMWLTH OF\b|\bCMWLTH OF\b', 'COMMONWEALTH OF'),
    (r'\bTWP\b', 'TOWNSHIP'), (r'\bCO OF\b', 'COUNTY OF'), (r'\bCTY OF\b', 'CITY OF'),
]
# postal codes that are also common words (IN, OR, ME, CO, ...) are left alone
_SAFE_POSTAL = {v[0]: v[1].upper() for k, v in kp.STATES.items()
                if v[0] not in ('IN', 'OR', 'ME', 'OK', 'HI', 'DE', 'LA', 'CO', 'AL', 'PA', 'ID', 'MO', 'MS', 'MA', 'GA', 'MT')}
_SAFE_POSTAL.update({'MASS': 'MASSACHUSETTS', 'ARK': 'ARKANSAS', 'TENN': 'TENNESSEE', 'PENN': 'PENNSYLVANIA',
                     'VA': 'VIRGINIA', 'W VA': 'WEST VIRGINIA', 'N C': 'NORTH CAROLINA', 'N CAROLINA': 'NORTH CAROLINA',
                     'BC': 'BRITISH COLUMBIA', 'ONT': 'ONTARIO', 'NB': 'NEW BRUNSWICK', 'NS': 'NOVA SCOTIA',
                     'PEI': 'PRINCE EDWARD ISLAND', 'YT': 'YUKON', 'YTG': 'GOVERNMENT OF YUKON', 'SASK': 'SASKATCHEWAN',
                     'MAN': 'MANITOBA', 'ALTA': 'ALBERTA', 'NFLD': 'NEWFOUNDLAND', 'QUE': 'QUEBEC'})
_POSTAL_RX = re.compile(r'\b(' + '|'.join(sorted((re.escape(k) for k in _SAFE_POSTAL), key=len, reverse=True)) + r')\b')
_TRAIL_OF = re.compile(r'^(.+?) (STATE OF|COMMONWEALTH OF|CITY OF|TOWN OF|COUNTY OF|VILLAGE OF|PROVINCE OF|GOVERNMENT OF)$')


def normalise(name):
    """Upper case, no punctuation, '&' -> AND, abbreviations spelled out, 'VERMONT STATE OF' -> 'STATE OF VERMONT'."""
    if name is None:
        return ''
    s = str(name).upper().replace('&', ' AND ')
    s = re.sub(r'[^A-Z0-9 ]+', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    for rx, rep in _ABBR:
        s = re.sub(rx, rep, s)
    s = _POSTAL_RX.sub(lambda m: _SAFE_POSTAL[m.group(1)], s)
    s = re.sub(r'^THE |\bTHE$', '', s).strip()
    s = re.sub(r'\s+', ' ', s)
    for _ in range(2):
        m = _TRAIL_OF.match(s)
        if m:
            s = f'{m.group(2)} {m.group(1)}'
    s = re.sub(r'\bTHE\b', '', s)
    return re.sub(r'\s+', ' ', s).strip()


def match_score(owner, targets_norm):
    """Best rapidfuzz ratio (0..1) of this owner against the agency names (plain ratio or word-order ratio)."""
    n = normalise(owner)
    if not n:
        return 0.0, None
    best, who = 0.0, None
    st = kp.nr_agency(n)
    for t in targets_norm:
        # club decision, Oct 31 (round 3): NATURAL RESOURCES + the same state word (misspellings allowed, any
        # spelling of DIVISION) is that state's natural resources agency, so it matches the park's agency outright
        if st and kp.nr_agency(t) == st:
            return 1.0, t
        sc = max(fuzz.ratio(n, t), fuzz.token_sort_ratio(n, t)) / 100.0
        if sc > best:
            best, who = sc, t
    return best, who


def agency_targets(pk, aliases):
    names = list(pk.get('agency_owner_names') or [])
    for nm in list(names):
        for k, v in (aliases or {}).items():
            if normalise(k) == normalise(nm) or nm in (v or []):
                names += [k] + list(v or [])
    out = []
    for nm in names:
        t = normalise(nm)
        if t and t not in out:
            out.append(t)
    return out


# ------------------------------------------------------------------ geometry
def utm_for(lon, lat):
    zone = int((lon + 180) // 6) + 1
    epsg = (32600 if lat >= 0 else 32700) + max(1, min(60, zone))
    crs = CRS.from_epsg(epsg)
    fwd = Transformer.from_crs(4326, crs, always_xy=True)
    back = Transformer.from_crs(crs, 4326, always_xy=True)
    return epsg, fwd, back


def reproject(g, tr):
    return shapely.transform(g, lambda c: np.column_stack(tr.transform(c[:, 0], c[:, 1])))


def esri_to_shape(g):
    """ArcGIS JSON rings -> shapely (outer rings clockwise, holes counter-clockwise; fixed with make_valid)."""
    rings = (g or {}).get('rings') or []
    outers, holes = [], []
    for r in rings:
        if len(r) < 4:
            continue
        a = sum(x1 * y2 - x2 * y1 for (x1, y1, *_), (x2, y2, *_) in zip(r, r[1:]))
        (outers if a <= 0 else holes).append([(p[0], p[1]) for p in r])
    if not outers:                       # some servers write every ring counter-clockwise
        outers, holes = holes, []
    polys = []
    for o in outers:
        po = Polygon(o)
        mine = [h for h in holes if po.buffer(0).contains(Point(h[0]))]
        polys.append(Polygon(o, mine))
    if not polys:
        return None
    g2 = polys[0] if len(polys) == 1 else MultiPolygon(polys)
    return g2 if g2.is_valid else make_valid(g2)


def only_polygons(g):
    if g is None or g.is_empty:
        return None
    if isinstance(g, (Polygon, MultiPolygon)):
        return g
    parts = [p for p in getattr(g, 'geoms', []) if isinstance(p, (Polygon, MultiPolygon))]
    return unary_union(parts) if parts else None


def dissolve(geoms_utm):
    """Step 4: dissolve, make_valid, drop slivers (parts and holes < 0.1 ac), simplify to 3 m."""
    g = only_polygons(make_valid(unary_union(geoms_utm)))
    if g is None:
        return None, 0
    parts = list(g.geoms) if isinstance(g, MultiPolygon) else [g]
    kept, dropped = [], 0
    for p in parts:
        if p.area < SLIVER_M2:
            dropped += 1
            continue
        inner = [r for r in p.interiors if Polygon(r).area >= SLIVER_M2]
        dropped += len(p.interiors) - len(inner)
        kept.append(Polygon(p.exterior, inner))
    if not kept:
        return None, dropped
    g = kept[0] if len(kept) == 1 else MultiPolygon(kept)
    g = only_polygons(make_valid(g.simplify(SIMPLIFY_M, preserve_topology=True)))
    return g, dropped


# ------------------------------------------------------------------ the parcel layer
class ParcelLayer:
    """Wraps kpc_parcels.Layer with paging (resultOffset / resultRecordCount, or objectIds when the server has no
    paging), f=geojson with an f=json fallback, and maxRecordCount respected."""

    def __init__(self, web, url, info, deadline):
        self.web, self.deadline = web, deadline
        self.L = kp.Layer(url, info)
        self.info = info
        self.oid_f = info.get('objectIdField') or next(
            (f['name'] for f in info.get('fields') or [] if f.get('type') == 'esriFieldTypeOID'), None)
        mrc = int(info.get('maxRecordCount') or 1000)
        self.page = max(1, min(mrc, 2000))
        aq = info.get('advancedQueryCapabilities') or {}
        self.paging = bool(aq.get('supportsPagination'))
        self.fmt = 'geojson' if 'geojson' in str(info.get('supportedQueryFormats') or '').lower() else 'json'
        self.requests = 0
        self.features = 0

    def _ask(self, params):
        if time.time() > self.deadline:
            raise TimeUp()
        self.requests += 1
        d, st, u = kp.jget(self.web, self.L.url + '/query', params, nocache=True)   # parcel replies are never cached
        if str(st) == '403':
            raise Blocked(blocked_msg(u))
        return d, st, u

    def _feats(self, d):
        out = []
        for f in (d or {}).get('features') or []:
            if 'attributes' in f:                     # esri json
                a, g = f.get('attributes') or {}, esri_to_shape(f.get('geometry'))
            else:                                     # geojson
                a = f.get('properties') or {}
                try:
                    g = shape(f['geometry']) if f.get('geometry') else None
                    g = g if (g is None or g.is_valid) else make_valid(g)
                except Exception:   # noqa: BLE001
                    g = None
            g = only_polygons(g)
            if g is not None:
                out.append((a, g))
        return out

    def envelope(self, x1, y1, x2, y2):
        """Every parcel touching the lon/lat box, all pages. Returns [(attributes, shapely geometry in 4326)]."""
        L = self.L
        fields = [x for x in (self.oid_f, L.owner_f, L.pid_f, L.acre_f) if x]
        base = {'where': '1=1', 'geometry': f'{x1:.7f},{y1:.7f},{x2:.7f},{y2:.7f}',
                'geometryType': 'esriGeometryEnvelope', 'inSR': '4326', 'spatialRel': 'esriSpatialRelIntersects',
                'outFields': ','.join(dict.fromkeys(fields)) or '*', 'returnGeometry': 'true', 'outSR': '4326'}
        out = []
        if self.paging:
            off = 0
            while True:
                p = dict(base, resultOffset=str(off), resultRecordCount=str(self.page), f=self.fmt)
                if self.oid_f:
                    p['orderByFields'] = self.oid_f
                d, st, u = self._ask(p)
                if d is None and self.fmt == 'geojson':
                    self.fmt = 'json'
                    continue
                if d is None:
                    if off == 0:          # paging refused after all: go by object ids
                        self.paging = False
                        return self.envelope(x1, y1, x2, y2)
                    raise RuntimeError(f'parcel query failed at offset {off}: {st} ({u})')
                got = self._feats(d)
                out += got
                self._count(len(got))
                more = d.get('exceededTransferLimit') or (d.get('properties') or {}).get('exceededTransferLimit')
                n = len(d.get('features') or [])
                if not n or (not more and n < self.page):
                    break
                off += n
            return out
        # no paging: ask for the object ids, then fetch them in batches
        d, st, u = self._ask(dict(base, returnIdsOnly='true', f='json'))
        if d is None:
            raise RuntimeError(f'parcel query failed: {st} ({u})')
        ids = sorted(d.get('objectIds') or [])
        batch = min(self.page, 250)
        for i in range(0, len(ids), batch):
            p = dict(base, objectIds=','.join(str(x) for x in ids[i:i + batch]), f=self.fmt)
            p.pop('geometry'); p.pop('geometryType'); p.pop('spatialRel'); p.pop('inSR')
            d, st, u = self._ask(p)
            if d is None and self.fmt == 'geojson':
                self.fmt = 'json'
                d, st, u = self._ask(dict(p, f='json'))
            if d is None:
                raise RuntimeError(f'parcel query by object id failed: {st} ({u})')
            got = self._feats(d)
            out += got
            self._count(len(got))
        return out

    def _count(self, n):
        self.features += n
        if self.features > MAX_FEATURES:
            raise RuntimeError(f'more than {MAX_FEATURES} parcels read for one park: stopped (never sweep a county)')


def gov_type(name):
    """kpc_parcels' owner-type keywords (government / private / unknown), asked on the normalised name so that
    abbreviations count ('ARKANSAS GAME & FISH COMMISSN' -> '... COMMISSION' = government)."""
    return kp.owner_type(normalise(name))[0] if name else 'unknown'


def pick_fields(P, pk):
    """Owner / parcel-id fields: parks.json owner_field / pid_field when given (must exist on the layer), else the
    tracer's preferences, else kpc_parcels' picks. Returns a list of notes for the why."""
    L, notes = P.L, []
    for key, attr_name, first in (('owner_field', 'owner_f', OWNER_FIRST), ('pid_field', 'pid_f', PID_FIRST)):
        want = pk.get(key)
        if want:
            hit = next((f for f in L.fields if f.lower() == str(want).lower()), None)
            if not hit:
                raise ValueError(f'{key} "{want}" is not a field of the layer')
            setattr(L, attr_name, hit)
            notes.append(f'{key} "{hit}" given in parks.json')
            continue
        f = kp.pick_field(L.fields, first)
        if f:
            setattr(L, attr_name, f)
    return notes


def open_layer(web, url, deadline):
    why = source_refused(url)
    if why:
        return None, why
    d, st, u = kp.jget(web, url.rstrip('/'), {'f': 'json'})
    if not d:
        return None, (blocked_msg(url) if str(st) == '403' else f'the parcel layer did not open ({st})')
    if kp.ZONING.search(str(d.get('name') or '') + ' ' + str(d.get('description') or '')[:300]):
        return None, 'a zoning layer (zoning is not ownership; never a parcel source)'
    if kp.NOT_OWNERSHIP.search(str(d.get('name') or '')):
        return None, 'a damage-assessment / analysis layer, not ownership'
    if d.get('geometryType') and d['geometryType'] != 'esriGeometryPolygon':
        return None, f'not a polygon layer ({d.get("geometryType")})'
    if 'query' not in str(d.get('capabilities') or 'query').lower():
        return None, 'the layer has query switched off'
    return ParcelLayer(web, url.rstrip('/'), d, deadline), 'ok'


# ------------------------------------------------------------------ other parks' official outlines (club rule, Oct 31)
# Never take in a parcel that sits inside ANOTHER POTA park's official outline (one owner can hold several parks, e.g.
# a wildlife agency's HQ next door). The outlines are the ones the club's 2-fer line uses as Official: the answer keys'
# joins (us-key / ca-key: grade 'official', no 'approx' join, no lake-surface layer) read by record id from the agency
# layer the key names (PAD-US, FWS or the state / provincial layer in layers.json), and for Kentucky the club's own
# answer key (ky-answer-key.json) over the official Kentucky files the website draws (ky-*.geojson; the forest's
# proclamation line and KPC-drawn outlines are never used). Approximate / parcel-traced outlines are never used, nor
# the park's own outline. INSIDE = at least half of the parcel's area lies inside the other park's official outline.
INSIDE_SHARE = 0.5
OUTLINE_PIN_KM = 80.0     # a state / provincial layer is asked only when one of its keyed parks has a pin this close
PADUS_Q = 'https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0/query'
FWS_Q = ('https://services.arcgis.com/QVENGdaPbd4LUkLV/arcgis/rest/services/FWSInterest_Simplified_Authoritative/'
         'FeatureServer/0/query')
CPCAD_Q = 'https://maps-cartes.ec.gc.ca/arcgis/rest/services/CWS_SCF/CPCAD/MapServer/0/query'
KYF = {'bstate': 'ky-state-parks.geojson', 'bwma': 'ky-hunting-areas.geojson', 'bsnp': 'ky-nature-preserves.geojson',
       'bsna': 'ky-natural-areas.geojson', 'bnps': 'ky-nps.geojson', 'bwild': 'ky-wild-rivers.geojson',
       'bwilder': 'ky-wilderness.geojson', 'bfws': 'ky-fws.geojson', 'bpad': 'ky-padus-parks.geojson',
       'bdbnfo': 'ky-dbnf-owned.geojson'}
KY_NOT_PROOF = ('bdbnf', 'bkpc', 'btrail', 'trl')      # proclamation line, KPC-drawn, trail lines: not area outlines


def _low(x):
    return ' '.join(re.sub(r'[^a-z0-9 ]', ' ', str(x or '').lower()).split())


def _name_ok(want, attrs):
    """The record must still carry the key's record name (a re-numbered server can hand back another park)."""
    w = _low(want)
    if not w:
        return True
    for v in (attrs or {}).values():
        if isinstance(v, str):
            v = _low(v)
            if v and (v == w or (len(v) > 3 and (v in w or w in v))):
                return True
    return False


def _gj_shape(geom):
    try:
        g = shape(geom)
    except Exception:      # noqa: BLE001
        return None
    g = g if g.is_valid else make_valid(g)
    return only_polygons(g) if not isinstance(g, (Polygon, MultiPolygon)) else g


class OfficialOutlines:
    """Other POTA parks' official outlines near a pin. dirs: folders holding any of us-key/, ca-key/, parkinfo/,
    state-gis.json (lake-surface layers), ky-answer-key.json + ky-*.geojson, and official-*.geojson (features with
    properties ref + grade 'official')."""

    def __init__(self, dirs, web=None, log=print, state_gis=None):
        self.dirs = [d for d in (dirs or []) if d and os.path.isdir(d)]
        self.state_gis = state_gis       # path of data/state-gis.json (lake-surface layers), or None to look in dirs
        self.state_gis_used, self.water_layers = None, 0
        self.web, self.log = web, log
        self.keyed = {}          # (query url, oid) -> (ref, record name)
        self.keyed_area = {}     # ref -> key file area ('US-VT', 'CA-YT')
        self.pins = {}           # ref -> (lat, lon)
        self.ky = {}             # ref -> [(file, NAME)]
        self.ky_files = {}       # file -> {NAME: [shapely lon/lat]}
        self.files = []          # (ref, name, shape lon/lat, label) from official-*.geojson
        self.areas = set()       # key areas covered ('US-VT', 'US-KY', 'CA-YT', ...)
        self.notes = []
        self.cache = {}          # (url, oid) -> shapely lon/lat or None
        if self.dirs:
            self._load()

    def _find(self, rel):
        for d in self.dirs:
            p = os.path.join(d, rel)
            if os.path.exists(p):
                return p
        return None

    def _load(self):
        water = set()
        sg = self.state_gis if self.state_gis and os.path.exists(self.state_gis) else self._find('state-gis.json')
        if sg:
            try:
                for lays in json.load(open(sg)).get('states', {}).values():
                    water |= {str(x.get('url') or '').rstrip('/') + '/query' for x in lays if x.get('water')}
                self.state_gis_used, self.water_layers = sg, len(water)
            except (OSError, ValueError) as e:
                self.log(f'state-gis.json {sg}: not read ({e})')
        else:
            self.log('state-gis.json not found (' + (f'{self.state_gis} missing; ' if self.state_gis else '')
                     + 'looked in the official dirs): answer-key parks joined to a lake-surface layer are NOT left out')
        for kind, layers_rel in (('us', 'us-key/layers.json'), ('ca', 'ca-key/layers.json')):
            lp = self._find(layers_rel)
            layers = json.load(open(lp)) if lp else {}
            kdir = self._find(kind + '-key')
            if not kdir:
                continue
            for fn in sorted(os.listdir(kdir)):
                m_ = re.fullmatch(r'((US|CA)-[A-Z0-9]{2})\.json', fn)
                if not m_:
                    continue
                try:
                    parks = json.load(open(os.path.join(kdir, fn))).get('parks') or {}
                except (OSError, ValueError):
                    continue
                if not parks:
                    continue
                self.areas.add(m_.group(1))
                for ref, p in parks.items():
                    m = p.get('m') or []
                    if not m or (p.get('g') and p.get('g') != 'official'):
                        continue
                    if any('approx' in str(x[3]) for x in m if len(x) > 3):
                        continue
                    srcs = [self._source(x[0], kind, layers) for x in m]
                    if any(s is None for s in srcs) or any(s[0] in water for s in srcs):
                        continue     # a record the tool cannot read, or a lake surface: not used (never guessed)
                    for (u, oid), x in zip(srcs, m):
                        self.keyed[(u, oid)] = (ref, x[1])
                    self.keyed_area[ref] = m_.group(1)
        ka = self._find('ky-answer-key.json')
        if ka:
            try:
                for ref, p in (json.load(open(ka)).get('parks') or {}).items():
                    tr = [t for t in p.get('tracts') or [] if t[0] not in KY_NOT_PROOF and t[0] in KYF]
                    if tr:
                        self.ky[ref] = [(KYF[t[0]], t[1]) for t in tr]
                self.areas.add('US-KY')
            except (OSError, ValueError):
                pass
        for d in self.dirs:
            pdir = os.path.join(d, 'parkinfo')
            if os.path.isdir(pdir):
                for fn in os.listdir(pdir):
                    if not re.fullmatch(r'(US-[A-Z0-9]{2}|CA)\.json', fn):
                        continue
                    try:
                        for r, v in (json.load(open(os.path.join(pdir, fn))).get('parks') or {}).items():
                            if len(v) > 6 and v[5] is not None and v[6] is not None:
                                la, lo = float(v[5]), float(v[6])
                                if abs(la) > 90:      # a swapped Canadian pin, as the 2-fer line reads it
                                    la, lo = abs(lo), -abs(la)
                                self.pins.setdefault(r, (la, lo))
                    except (OSError, ValueError, TypeError):
                        continue
            for fn in sorted(os.listdir(d)):
                if re.fullmatch(r'official-.*\.geojson', fn):
                    try:
                        for f in json.load(open(os.path.join(d, fn))).get('features') or []:
                            pr = f.get('properties') or {}
                            if str(pr.get('grade') or '').lower() != 'official' or not pr.get('ref'):
                                continue
                            g = _gj_shape(f.get('geometry'))
                            if g is not None:
                                self.files.append((pr['ref'], pr.get('name') or '', g, fn))
                    except (OSError, ValueError):
                        continue

    @staticmethod
    def _source(rid, kind, layers):
        """(query url, object id) for a key record id, as the 2-fer line reads it; None when it cannot be read by id."""
        if kind == 'ca':
            if isinstance(rid, int):
                return CPCAD_Q, rid
            lab, _, n = str(rid).partition(':')
            urls = [u.rstrip('/') + '/query' for u in layers.get(lab) or [] if re.search(r'/\d+$', u.rstrip('/'))]
            return (urls[0], int(n)) if n.isdigit() and urls else None
        if isinstance(rid, int):
            return PADUS_Q, rid
        m = re.fullmatch(r'([a-z]+)(\d+)', str(rid))
        if not m or m.group(1) == 'trl':
            return None
        if m.group(1) == 'fws':
            return FWS_Q, int(m.group(2))
        lay = layers.get(m.group(1))
        return (lay[0], int(m.group(2))) if lay else None

    def _ky_shapes(self, fn):
        if fn not in self.ky_files:
            idx = {}
            p = self._find(fn)
            try:
                for f in (json.load(open(p)).get('features') if p else None) or []:
                    g = _gj_shape(f.get('geometry'))
                    if g is not None:
                        idx.setdefault(str((f.get('properties') or {}).get('NAME') or ''), []).append(g)
            except (OSError, ValueError):
                pass
            self.ky_files[fn] = idx
        return self.ky_files[fn]

    def near(self, own_ref, lon, lat, bbox_ll, area):
        """([(ref, name, shapely lon/lat, source label)], notes) of OTHER parks' official outlines meeting bbox_ll."""
        out, notes = [], []
        if not self.dirs:
            return out, ['no official outline data given (--official-dir), so the other-park check was not done']
        area = str(area or '').upper()
        bb = box(*bbox_ll)
        covered = area in self.areas
        for ref, nm, g, fn in self.files:
            if ref != own_ref and g.intersects(bb):
                out.append((ref, nm, g, fn))
                covered = True
        if area == 'US-KY' or ('US-KY' in self.areas and bb.intersects(box(-89.6, 36.4, -81.9, 39.2))):
            for ref, tracts in self.ky.items():
                if ref == own_ref:
                    continue
                pin = self.pins.get(ref)
                gs = []
                for fn, nm in tracts:
                    for g in self._ky_shapes(fn).get(nm, []):
                        if pin and not (abs(g.centroid.x - pin[1]) < 0.6 and abs(g.centroid.y - pin[0]) < 0.6):
                            continue       # the same NAME elsewhere in the state (as the 2-fer line reads it)
                        if g.intersects(bb):
                            gs.append(g)
                if gs:
                    out.append((ref, tracts[0][1], unary_union(gs), 'Kentucky official file ' + tracts[0][0]))
        if self.keyed and self.web is not None:
            nat = 'CA' if area.startswith('CA') else 'US'
            want = {}
            for (u, oid), (ref, rn) in self.keyed.items():
                if ref == own_ref or not self.keyed_area.get(ref, '').startswith(nat):
                    continue
                pin = self.pins.get(ref)
                national = u in (PADUS_Q, FWS_Q, CPCAD_Q)
                if not national and not (pin and kp.dist_m(lon, lat, pin[1], pin[0]) <= OUTLINE_PIN_KM * 1000):
                    continue
                want.setdefault(u, {})[oid] = (ref, rn)
            got = {}
            for u, ids in want.items():
                hits, why = self._ids_in(u, bbox_ll)
                if hits is None:
                    notes.append(f'other-park check incomplete: {u} did not answer ({why})')
                    continue
                for oid in sorted(set(hits) & set(ids)):
                    g = self._record(u, oid, ids[oid][1])
                    if g is None:
                        notes.append(f'other-park check incomplete: record {oid} of {u} not read')
                        continue
                    ref, rn = ids[oid]
                    got.setdefault((ref, rn), []).append(g)
                    lab = ('USGS PAD-US' if u == PADUS_Q else 'USFWS' if u == FWS_Q else 'CPCAD' if u == CPCAD_Q
                           else u.split('/rest/services/')[-1].replace('/query', ''))
                    got.setdefault(('label', ref), set()).add(lab)
            for k, gs in got.items():
                if k[0] == 'label':
                    continue
                out.append((k[0], k[1], unary_union(gs), 'answer key join, ' + ' + '.join(sorted(got[('label', k[0])]))))
        if not covered and not out:
            notes.append(f'no official outline data covers {area or "this area"} (no answer key for it), so the '
                         'other-park check could not be done')
        return out, notes

    def _ids_in(self, u, bb):
        d, st, _ = kp.jget(self.web, u, {'geometry': ','.join(f'{v:.6f}' for v in bb), 'geometryType': 'esriGeometryEnvelope',
                                         'inSR': 4326, 'spatialRel': 'esriSpatialRelIntersects', 'returnIdsOnly': 'true',
                                         'f': 'json'})
        if d is None:
            return None, st
        return [int(i) for i in d.get('objectIds') or []], 'ok'

    def _record(self, u, oid, rec_name):
        k = (u, oid)
        if k not in self.cache:
            d, st, _ = kp.jget(self.web, u, {'objectIds': oid, 'outFields': '*', 'returnGeometry': 'true',
                                             'outSR': 4326, 'f': 'json'})
            g = None
            for f in (d or {}).get('features') or []:
                if _name_ok(rec_name, f.get('attributes')):
                    g = esri_to_shape(f.get('geometry'))
            self.cache[k] = g
        return self.cache[k]


def inside_other(g_m, others_m):
    """(ref, share) of the other park holding >= INSIDE_SHARE of this parcel's area, else None."""
    if g_m.is_empty or g_m.area <= 0:
        return None
    best = None
    for ref, o in others_m:
        if not o.intersects(g_m):
            continue
        sh = g_m.intersection(o).area / g_m.area
        if sh >= INSIDE_SHARE and (best is None or sh > best[1]):
            best = (ref, round(sh, 3))
    return best


# ------------------------------------------------------------------ one park
def trace(pk, web, aliases, read_date, deadline, max_km=10.0, log=print, outlines=None):
    """Returns (status, why, feature_or_None, info dict)."""
    ref, lat, lon = pk['ref'], float(pk['lat']), float(pk['lon'])
    ka, ka_src = known_size(pk)
    info = {'n_parcels': 0, 'acres': None, 'pin_dist_m': None, 'layer_url': pk.get('parcel_layer_url'), 'excluded': '',
            'known_acres': ka, 'known_acres_source': ka_src, 'size_ratio': None}
    fips = pk.get('county_fips')
    if not fips and str(pk.get('state_or_prov', '')).upper() == 'US-KY':
        cty, cu, cst = kp.county_at(web, lat, lon)       # only to honour the Warren County skip
        fips = (cty or {}).get('fips')
    if fips and str(fips).zfill(5) in kp.CLUB_SKIP:
        return 'NO PARCEL', kp.CLUB_SKIP[str(fips).zfill(5)], None, info
    targets = agency_targets(pk, aliases)
    if not targets:
        return 'ERROR', 'no agency_owner_names for this park', None, info
    dfrp = str(pk.get('owner_source') or '').lower() == 'dfrp'
    if dfrp:      # Canada: the federal property register; its custodian is the owner
        pk = dict(pk, parcel_layer_url=pk.get('parcel_layer_url') or DFRP_URL, **DFRP_FIELDS)
        info['layer_url'] = pk['parcel_layer_url']
    src = 'federal property (DFRP)' if dfrp else 'parcel'
    src_pl = 'federal properties (DFRP)' if dfrp else 'parcel(s)'
    owner_word = 'custodian' if dfrp else 'owner'
    is_gov = (lambda o: bool(o)) if dfrp else (lambda o: gov_type(o) == 'government')   # noqa: E731
    P, why = open_layer(web, pk.get('parcel_layer_url'), deadline)
    if P is None:
        return 'ERROR', why, None, info
    L = P.L
    field_notes = pick_fields(P, pk)
    if dfrp:
        field_notes = []          # the DFRP fields are fixed by the tool, not given by the park row
    if not L.owner_f:
        return ('OWNER UNCLEAR', f'the layer "{L.name}" has no owner field ({", ".join(L.fields[:12])}), so no parcel can be '
                'matched to the agency by owner name (rule 1)', None, info)
    epsg, fwd, back = utm_for(lon, lat)
    to_m = lambda g: reproject(g, fwd)          # noqa: E731
    to_ll = lambda g: reproject(g, back)        # noqa: E731
    pin = Point(fwd.transform(lon, lat))
    limit = box(pin.x - max_km * 1000, pin.y - max_km * 1000, pin.x + max_km * 1000, pin.y + max_km * 1000)
    parcels = {}       # key -> dict(owner, pid, g, score, inside)
    # other POTA parks' official outlines over the search area (club rule Oct 31): a parcel at least half inside one
    # is never taken in, neither as the seed nor in growth
    # (read once there are parcels near the pin, so a park with none costs no outline requests)
    others_m, other_names, other_notes = None, {}, []
    excluded = {}      # parcel key -> (parcel id, other ref, share inside)

    def usable(k):
        v = parcels[k]
        if v['inside'] is None:
            return True
        excluded[k] = (v['pid'], v['inside'][0], v['inside'][1])
        return False

    def key_of(a, g):
        oid = kp.attr(a, P.oid_f) if P.oid_f else None
        return str(oid) if oid is not None else f'{kp.attr(a, L.pid_f)}|{g.wkb_hex[:64]}'

    def add(feats):
        for a, g in feats:
            k = key_of(a, g)
            if k in parcels:
                continue
            ow = kp.clean(kp.attr(a, L.owner_f))
            sc, _ = match_score(ow, targets)
            gm = to_m(g)
            parcels[k] = {'owner': ow, 'pid': kp.clean(kp.attr(a, L.pid_f)) if L.pid_f else None,
                          'g': gm, 'score': sc,
                          'inside': inside_other(gm, others_m) if sc >= MATCH_MIN and others_m else None}

    def fetch(region):       # region: a UTM polygon; asked as its lon/lat bounding box
        x1, y1, x2, y2 = region.bounds
        lx1, ly1, lx2, ly2 = back.transform_bounds(x1, y1, x2, y2)
        add(P.envelope(lx1, ly1, lx2, ly2))

    # 1a. the parcel(s) under the pin
    under, how = [], ''
    if time.time() > deadline:
        raise TimeUp()
    feats, how, qu = kp.query_point(web, L, lon, lat)
    P.requests += 1
    if feats is None and '403' in str(how):
        raise Blocked(blocked_msg(qu))
    if feats is not None:
        for f in feats:
            g = esri_to_shape(f.get('geometry'))
            if g is not None:
                a = f.get('attributes') or {}
                add([(a, g)])
                under.append(key_of(a, g))
    # 1b. envelope of 1 km around the pin
    covered = box(pin.x - FIRST_M, pin.y - FIRST_M, pin.x + FIRST_M, pin.y + FIRST_M)
    fetch(covered)
    if not parcels:
        return 'NO PARCEL', f'no {src} of the layer under the pin or within {FIRST_M:.0f} m', None, info
    others, loaded = [], any(v['score'] >= MATCH_MIN for v in parcels.values())
    if loaded:        # nothing to leave out when no parcel near the pin matches the agency
        lx1, ly1, lx2, ly2 = back.transform_bounds(*limit.buffer(1000).bounds)
        others, other_notes = (outlines or OfficialOutlines([])).near(ref, lon, lat, (lx1, ly1, lx2, ly2), area_of(pk))
        others_m = [(r, to_m(g)) for r, nm, g, lab in others]
        other_names = {r: (nm, lab) for r, nm, g, lab in others}
        for v in parcels.values():
            if v['score'] >= MATCH_MIN and others_m:
                v['inside'] = inside_other(v['g'], others_m)
    other_bits = other_notes + ([f'other parks\' official outlines in the search area: ' + '; '.join(
        f'{r} {other_names[r][0]} ({other_names[r][1]})' for r in sorted(other_names))] if others else
        ([] if other_notes else ['no other park\'s official outline in the search area'])) if loaded else []

    def excl_text():
        return '; '.join(f'{p or k} in {r} ({sh:.0%} inside)' for k, (p, r, sh) in sorted(excluded.items(), key=lambda kv: str(kv[1][0])))
    # seed: the agency parcel under the pin, else the nearest agency parcel within 500 m
    match = {k: v for k, v in parcels.items() if v['score'] >= MATCH_MIN}
    seed, seed_d = None, None
    for k, v in sorted(match.items(), key=lambda kv: kv[1]['g'].distance(pin)):
        d = v['g'].distance(pin)
        if d > SEED_M:
            break
        if usable(k):
            seed, seed_d = k, d
            break
    if seed is None and excluded:
        info['excluded'] = excl_text()
        refs_in = sorted({r for _, r, _ in excluded.values()})
        pin_in = [r for r, o in others_m if o.covers(pin)]
        return (HELD, f'held back, no outline written: every agency {src} within {SEED_M:.0f} m of the pin lies inside '
                f'another POTA park\'s official outline ({", ".join(f"{r} {other_names[r][0]}" for r in refs_in)}), so none '
                'is taken in (club rule Oct 31)' + (f'; the pin itself is inside {", ".join(pin_in)}: possibly the same '
                'land or a 2-fer, check by hand' if pin_in else '') + ' | ' + '; '.join(other_bits + [f'excluded: {excl_text()}']),
                None, info)
    if seed is None:
        near = [v for v in parcels.values() if v['g'].distance(pin) <= SEED_M]
        if not near:
            far = min(v['g'].distance(pin) for v in parcels.values())
            return ('NO PARCEL', f'no {src} under the pin or within {SEED_M:.0f} m (nearest is {far:.0f} m away)',
                    None, info)
        gov = sorted(((v['score'], v['owner']) for v in near if is_gov(v['owner'])), reverse=True)
        pin_own = [parcels[k]['owner'] for k in under if k in parcels]
        pt = ('government' if is_gov(pin_own[0]) else gov_type(pin_own[0])) if pin_own else 'none'
        bits = [f'{owner_word} field "{L.owner_f}"', f'{len(near)} {src_pl} within {SEED_M:.0f} m, none with a '
                f'{owner_word} matching the managing agency {" / ".join(pk.get("agency_owner_names") or [])} '
                f'at ratio >= {MATCH_MIN}']
        if dfrp and gov:
            bits.append(f'the {owner_word} is not the managing agency, so it is not used (club decision Oct 31)')
        bits.append(f'{owner_word} type at the pin: {pt}' + (f' ("{pin_own[0]}")' if pt == 'government' else ''))
        if gov:
            bits.append(f'closest government {owner_word} names: ' + '; '.join(f'"{o}" ({s:.2f})' for s, o in gov[:3]))
        nm = [v for v in match.values()]
        if nm:
            bits.append(f'nearest matching parcel is {min(v["g"].distance(pin) for v in nm):.0f} m from the pin')
        return 'OWNER UNCLEAR', '; '.join(bits), None, info
    # 3. grow the connected set (200 m adjacency) from the seed
    members = [seed]
    shape_m = parcels[seed]['g']
    hit_limit = False
    size_capped = False
    for _ in range(500):
        need = box(*shape_m.buffer(ADJ_M + 50).bounds)
        clipped = need.intersection(limit)
        if not clipped.equals(need):
            hit_limit = True
        miss = clipped.difference(covered)
        if miss.area > 1.0:
            pieces = list(miss.geoms) if hasattr(miss, 'geoms') else [miss]
            for pc in pieces:
                if pc.area > 1.0:
                    fetch(pc)
            covered = unary_union([covered, clipped])
        zone = shape_m.buffer(ADJ_M)
        new = [k for k, v in parcels.items() if v['score'] >= MATCH_MIN and k not in members and k not in excluded
               and v['g'].intersects(zone) and usable(k)]
        if new and GROW_CAP and ka and TL is not None:   # Nov 2 review: nearest first, never past GROW_CAP x the official size
            new, _capped = TL.capped_growth([(k, parcels[k]['g'].distance(shape_m), parcels[k]['g'].area) for k in new],
                                            shape_m.area, GROW_CAP * float(ka) * ACRES_M2)
            if _capped: size_capped = True
        if not new:
            break
        members += new
        shape_m = unary_union([shape_m] + [parcels[k]['g'] for k in new])
    # 4. dissolve and clean
    g, dropped = dissolve([parcels[k]['g'] for k in members])
    if g is None:
        return 'ERROR', 'the joined parcels left no polygon after cleaning', None, info
    cut_m2 = 0.0
    if SUBTRACT_OTHERS and others_m and TL is not None:   # Nov 2 review: other parks' official land is cut out of this one
        g, cut_m2 = TL.subtract_others(g, others_m)
        if g is None or g.is_empty:
            return HELD, 'held back, no outline written: nothing is left after cutting out other parks\' official outlines', None, info
    acres = round(g.area / ACRES_M2, 2)
    pin_d = round(g.distance(pin), 1)
    owners = list(dict.fromkeys(parcels[k]['owner'] for k in members))
    raw_pids = [parcels[k]['pid'] for k in members]
    pids = list(dict.fromkeys(p for p in raw_pids if p not in (None, '')))
    # one parcel can come back as several records (multi-part parcels, e.g. NC TVA parno 459219616366000 x4)
    n_par = len(pids) if pids and len(pids) + raw_pids.count(None) + raw_pids.count('') == len(pids) else len(members)
    info.update(n_parcels=n_par, acres=acres, pin_dist_m=pin_d)
    # 5. sanity
    if pin_d > PIN_FAR_M:
        return ('PIN FAR', f'the pin is {pin_d:.0f} m outside the joined {len(members)} parcel(s) ({acres} ac); '
                f'more than {PIN_FAR_M:.0f} m, so nothing is output (rule 4; POTA pins never move)', None, info)
    why = ([f'source: {src} register, {owner_word} = managing agency'] if dfrp else []) + field_notes + [f'{owner_word} field "{L.owner_f}"', f'seed {src} {parcels[seed]["pid"]} ' + ('under the pin' if seed in under or seed_d == 0 else f'{seed_d:.0f} m from the pin'),
           f'{n_par} parcel(s) joined with {ADJ_M:g} m adjacency'
           + (f' ({len(members)} records)' if n_par != len(members) else ''), f'{P.features} parcel record(s) read in '
           f'{P.requests} request(s)', f'pin {"inside" if pin_d == 0 else f"{pin_d:.0f} m outside"}']
    if dropped:
        why.append(f'{dropped} sliver(s) / hole(s) under 0.1 ac removed')
    if cut_m2 > 0:
        why.append(f'{cut_m2 / ACRES_M2:.1f} ac inside other POTA parks\' official outlines cut out')
    if size_capped:
        why.append(f'growth stopped at {GROW_CAP:g}x the known size (nearest parcels first)')
    why += other_bits
    info['excluded'] = excl_text()
    if excluded:
        why.append(f'{len(excluded)} agency parcel record(s) left out because they lie inside another POTA park\'s '
                   f'official outline: {info["excluded"]}')
    held = []
    if hit_limit:
        why.append(f'INCOMPLETE: growth reached the {max_km:g} km limit around the pin')
        held.append(f'the trace was cut off: same-{owner_word} land runs past the {max_km:g} km search limit')
    check = None
    rng = f'{SIZE_LO:g}x-{SIZE_HI:g}x'
    if ka:
        r = acres / float(ka)
        info['size_ratio'] = round(r, 2)
        check = 'ok' if SIZE_LO <= r <= SIZE_HI else f'outside {rng}'
        why.append(f'acres {acres} vs known {ka:g} = {r:.2f}x ({check}); known size from the {ka_src}')
        if check != 'ok':
            held.append(f'size check failed: {acres} ac is {r:.2f}x the known {ka:g} ac (allowed {rng})')
    else:
        why.append(ka_src)
    info['acres_check'] = check
    if held:      # club decision, Oct 31: held back, no outline written
        return HELD, 'held back, no outline written: ' + '; '.join(held) + ' | ' + '; '.join(why), None, info
    gov_owners = [o for o in owners if is_gov(o)]
    feat = {'type': 'Feature', 'geometry': mapping(to_ll(g)), 'properties': {
        'ref': ref, 'name': pk.get('name'), 'grade': GRADE,
        'owner': '; '.join(gov_owners) if gov_owners else None,
        'parcel_ids': pids, 'n_parcels': n_par, 'acres': acres,
        'source_url': L.url + '/query', 'read_date': read_date,
        'layer_url': L.url, 'pin_dist_m': pin_d, 'known_acres': ka, 'known_acres_source': ka_src,
        'size_ratio': info['size_ratio'], 'acres_check': check,
        'utm_epsg': epsg,
        'excluded_other_park': [{'parcel_id': p, 'other_ref': r, 'share_inside': sh}
                                for k, (p, r, sh) in sorted(excluded.items(), key=lambda kv: str(kv[1][0]))]}}
    if len(gov_owners) < len(owners):
        feat['properties']['owner_withheld'] = True
        why.append('an owner string whose type is not clearly government is not written (club decision Oct 31)')
    return 'DRAWN', '; '.join(why), feat, info


# ------------------------------------------------------------------ files
def area_of(pk):
    a = str(pk.get('state_or_prov') or pk['ref'].split('-')[0]).upper()
    return re.sub(r'[^A-Z0-9_-]', '_', a)


def write_json(path, d):
    tmp = path + '.tmp'
    with open(tmp, 'w') as f:
        json.dump(d, f, indent=1, ensure_ascii=False)
    os.replace(tmp, path)


def save_park(outdir, pk, status, why, feat, info, read_date, state):
    pdir = os.path.join(outdir, 'parcels')
    os.makedirs(pdir, exist_ok=True)
    ap = os.path.join(pdir, area_of(pk) + '.json')
    fc = json.load(open(ap)) if os.path.exists(ap) else {'type': 'FeatureCollection', 'features': []}
    fc['features'] = [f for f in fc['features'] if f['properties'].get('ref') != pk['ref']]
    if feat:
        fc['features'].append(feat)
        fc['features'].sort(key=lambda f: f['properties']['ref'])
    if fc['features'] or os.path.exists(ap):
        write_json(ap, fc)
    state['results'][pk['ref']] = dict(ref=pk['ref'], status=status, why=why, name=pk.get('name') or '',
                                       read_date=read_date, **info)
    rows = sorted(state['results'].values(), key=lambda r: r['ref'])
    tmp = os.path.join(pdir, 'report.csv.tmp')
    with open(tmp, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['ref', 'status', 'why', 'name', 'n_parcels', 'acres', 'pin_dist_m', 'acres_check', 'layer_url',
                    'read_date', 'excluded_by_other_park', 'known_acres', 'known_acres_source', 'size_ratio'])
        for r in rows:
            w.writerow([r['ref'], r['status'], r['why'], r['name'], r.get('n_parcels'), r.get('acres'),
                        r.get('pin_dist_m'), r.get('acres_check'), r.get('layer_url'), r['read_date'],
                        r.get('excluded') or '', r.get('known_acres'), r.get('known_acres_source') or '',
                        r.get('size_ratio')])
    os.replace(tmp, os.path.join(pdir, 'report.csv'))
    write_json(os.path.join(outdir, 'state.json'), state)


def load_parks(path):
    d = json.load(open(path))
    rows = d.get('parks', d) if isinstance(d, dict) else d
    out = []
    for r in rows:
        try:
            float(r['lat']), float(r['lon'])
            out.append(r)
        except (KeyError, TypeError, ValueError):
            out.append({'ref': str(r.get('ref', '?')), 'bad': True})
    return out


DEFAULT_DATA = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..', '..', 'data'))   # KPC-Data/data, when the tool sits in KPC-Data
DEFAULT_STATE_GIS = os.path.join(DEFAULT_DATA, 'state-gis.json')


def run(args, web=None):
    t0 = time.time()
    deadline = t0 + args.max_minutes * 60
    log = (lambda *a: None) if args.quiet else (lambda *a: print(*a, flush=True))
    try:
        parks = load_parks(args.parks)
        aliases = json.load(open(args.aliases)) if args.aliases and os.path.exists(args.aliases) else {}
    except (OSError, ValueError) as e:
        print(f'bad input: {e}', file=sys.stderr)
        return 2
    if args.refs:
        want = [r.strip() for r in args.refs.split(',') if r.strip()]
        have = {p['ref'] for p in parks}
        for r in want:
            if r not in have:
                print(f'bad input: {r} is not in {args.parks}', file=sys.stderr)
                return 2
        order = {r: i for i, r in enumerate(want)}
        parks = sorted((p for p in parks if p['ref'] in order), key=lambda p: order[p['ref']])
    os.makedirs(args.out, exist_ok=True)
    sp = os.path.join(args.out, 'state.json')
    state = json.load(open(sp)) if args.resume and os.path.exists(sp) else {'results': {}, 'done': {}}
    web = web or kp.Polite(cache=args.cache, log=log, rest_exempt=True)
    web.log = log
    read_date = kp.today()
    left = 0
    od = getattr(args, 'official_dir', None)
    dirs = list(od) if od is not None else [d for d in (os.environ.get('KPC_OFFICIAL_DIR'), DEFAULT_DATA)
                if d and os.path.isdir(d) and (os.path.isdir(os.path.join(d, 'us-key')) or
                                               os.path.isdir(os.path.join(d, 'ca-key')))][:1]
    sg = getattr(args, 'state_gis', None) or (DEFAULT_STATE_GIS if os.path.exists(DEFAULT_STATE_GIS) else None)
    outlines = OfficialOutlines(dirs, web, log, state_gis=sg)
    log(f'official outlines: {", ".join(dirs) or "none given"} ({len(outlines.keyed)} keyed records, '
        f'{len(outlines.ky)} Kentucky parks, {len(outlines.files)} file outlines); state-gis.json: '
        f'{outlines.state_gis_used or "not found"} ({outlines.water_layers} lake-surface layers)')
    oa = getattr(args, 'official_acres', None)
    if oa is None:
        oa = [p for p in [os.environ.get('KPC_OFFICIAL_ACRES')] + [os.path.join(d, rel) for d in dirs + [DEFAULT_DATA]
              for rel in ('acres.json', os.path.join('acres', 'acres.json'))] if p and os.path.isfile(p)][:1]
    acres_list = load_official_acres(oa, log)
    if not oa:
        log('official acres list: none given or found; the round-14 figures are used for the size check')
    for pk in parks:
        ref = pk['ref']
        if args.resume and ref in state['done']:
            continue
        if time.time() > deadline:
            left += 1
            continue
        if pk.get('bad'):
            status, why, feat, info = 'ERROR', 'bad row: needs ref, lat and lon', None, {}
        else:
            log(f'{ref} {pk.get("name", "")}')
            try:
                pk = dict(pk, _official_acres=acres_list.get(ref), _acres_list_loaded=bool(oa))
                status, why, feat, info = trace(pk, web, aliases, read_date, deadline, args.max_km, log, outlines)
            except Blocked as e:
                status, why, feat, info = 'ERROR', str(e), None, {'layer_url': pk.get('parcel_layer_url')}
            except TimeUp:
                left += 1
                log(f'  {ref}: time ran out in the middle; not saved, run again with --resume')
                continue
            except Exception as e:      # noqa: BLE001  (one park never stops the batch)
                status, why, feat, info = 'ERROR', f'{type(e).__name__}: {e}', None, {'layer_url': pk.get('parcel_layer_url')}
        log(f'  {status}: {why}')
        state['done'][ref] = read_date
        save_park(args.out, pk, status, why, feat, info, read_date, state)
    state['requests'] = web.stats
    state['blocked_hosts'] = dict(sorted({**state.get('blocked_hosts', {}), **web.blocked}.items()))
    state['left'] = left
    write_json(sp, state)
    log(f'done in {time.time() - t0:.0f} s; {web.stats["requests"]} requests; {left} left')
    return 3 if left else 0


# ------------------------------------------------------------------ self test (no network)
class _FakeServer(kp.Polite):
    """A parcel layer of 100 x 100 m squares around (lon -85, lat 38): agency squares in a block of 3 x 2 plus one
    150 m away and one 600 m away, a private square under nothing."""

    def __init__(self, owner_at, owner_key='OWNER_NAME', pid_key='PARCEL_ID', robots403=False, data403=False,
                 other_layer=None):
        super().__init__(cache=None, gap=0, rest_exempt=True)
        self.owner_at, self.urls = owner_at, []
        self.other_layer = other_layer or {}      # oid -> (NAME, (i0, j0, i1, j1)): an 'official park' layer /O/MapServer/1
        self.owner_key, self.pid_key, self.robots403, self.data403 = owner_key, pid_key, robots403, data403
        self.log = lambda *a: None
        if not robots403:
            self.robots['fake.example.gov'] = kp.Robots('')
        self.epsg, self.fwd, self.back = utm_for(-85.0, 38.0)
        self.x0, self.y0 = self.fwd.transform(-85.0, 38.0)

    def square(self, i, j):
        x, y = self.x0 + i * 100 - 50, self.y0 + j * 100 - 50
        pts = [self.back.transform(*p) for p in ((x, y), (x, y + 100), (x + 100, y + 100), (x + 100, y), (x, y))]
        return {'rings': [[list(p) for p in pts]]}

    def _raw(self, url, method='GET', data=None, headers=None):
        from urllib.parse import parse_qs, urlparse as up
        self.urls.append(url)
        q = {k: v[0] for k, v in parse_qs(up(url).query).items()}
        if url.split('?')[0].endswith('/robots.txt'):
            return (403 if self.robots403 else 404), {}, b'', url
        if self.data403 and '/query' in url:
            return 403, {}, b'', url
        if '/O/MapServer/1/query' in url:
            if q.get('returnIdsOnly') == 'true':
                return 200, {}, json.dumps({'objectIds': sorted(self.other_layer)}).encode(), url
            fs = []
            for oid in [int(x) for x in q.get('objectIds', '').split(',') if x]:
                nm, (i0, j0, i1, j1) = self.other_layer[oid]
                x1, y1 = self.x0 + i0 * 100 - 50, self.y0 + j0 * 100 - 50
                x2, y2 = self.x0 + i1 * 100 + 50, self.y0 + j1 * 100 + 50
                pts = [self.back.transform(*p) for p in ((x1, y1), (x1, y2), (x2, y2), (x2, y1), (x1, y1))]
                fs.append({'attributes': {'OBJECTID': oid, 'NAME': nm}, 'geometry': {'rings': [[list(p) for p in pts]]}})
            return 200, {}, json.dumps({'features': fs}).encode(), url
        if url.split('?')[0].endswith('/0'):
            info = {'name': 'Parcels', 'geometryType': 'esriGeometryPolygon', 'capabilities': 'Query', 'maxRecordCount': 3,
                    'objectIdField': 'OBJECTID', 'advancedQueryCapabilities': {'supportsPagination': True},
                    'supportedQueryFormats': 'JSON', 'fields': [{'name': 'OBJECTID', 'type': 'esriFieldTypeOID'},
                    {'name': self.owner_key}, {'name': self.pid_key}]}
            return 200, {}, json.dumps(info).encode(), url
        feats = []
        for n, ((i, j), ow) in enumerate(sorted(self.owner_at.items())):
            feats.append({'attributes': {'OBJECTID': n + 1, self.owner_key: ow, self.pid_key: f'P{i}_{j}'},
                          'geometry': self.square(i, j)})
        if q.get('geometryType') == 'esriGeometryPoint':
            lon, lat = (float(v) for v in q['geometry'].split(','))
            x, y = self.fwd.transform(lon, lat)
            feats = [f for f in feats if Polygon(self.fwd.transform(*p) for p in f['geometry']['rings'][0]).contains(Point(x, y))]
            return 200, {}, json.dumps({'features': feats}).encode(), url
        off, cnt = int(q.get('resultOffset', 0)), int(q.get('resultRecordCount', 1000))
        page = feats[off:off + cnt]
        return 200, {}, json.dumps({'features': page, 'exceededTransferLimit': off + cnt < len(feats)}).encode(), url


def selftest():
    import tempfile, shutil
    ok = True
    problems = []
    for a, b in (('VERMONT STATE OF', 'STATE OF VERMONT'), ('ARKANSAS GAME & FISH COMMISSN', 'ARKANSAS GAME AND FISH COMMISSION'),
                 ('ARK GAME & FISH COMM', 'ARKANSAS GAME AND FISH COMMISSION'), ('THE UNITED STATES OF AMERICA', 'UNITED STATES'),
                 ('MASSACHUSETTS COMMONWEALTH OF', 'COMMONWEALTH OF MASSACHUSETTS'), ('W VA DNR', 'WEST VIRGINIA DEPARTMENT OF NATURAL RESOURCES')):
        if normalise(a) != b:
            problems.append(f'normalise("{a}") = "{normalise(a)}", expected "{b}"')
    t = [normalise('Kentucky Department of Fish & Wildlife Resources')]
    if match_score('KY DEPT OF FISH & WILDLIFE RES', t)[0] < MATCH_MIN:
        problems.append('KY DEPT OF FISH & WILDLIFE RES should match KDFWR')
    wv = [normalise('WEST VIRGINIA DIVISION OF NATURAL RESOURCES')]
    for typo in ('WEST VIRGINIA DIVISON OF NATURAL RESOURCES', 'WEST VIRGININA DIVISION OF NATURAL RESOURCES'):
        if match_score(typo, wv)[0] < MATCH_MIN:
            problems.append(f'"{typo}" should match at >= {MATCH_MIN}')
    for typo in ('WEST VIRGINIA DIVSISION OF NATURAL RESOURCES', 'WEST VIRGININA DIVISON OF NATUARL RESOURSES',
                 'W VA DIV OF NAT RES'):
        if match_score(typo, wv)[0] < MATCH_MIN or gov_type(typo) != 'government':
            problems.append(f'"{typo}" is the WV natural resources agency (club decision Oct 31, round 3)')
    if match_score('VIRGINIA DEPARTMENT OF NATURAL RESOURCES', wv)[0] >= MATCH_MIN:
        problems.append('another state\'s natural resources agency must not match')
    if match_score('FORKS OF COAL STATE NATIONAL ETAL', wv)[0] >= MATCH_MIN:
        problems.append('a different owner entity must not match')
    if gov_type('ARKANSAS GAME & FISH COMMISSN') != 'government' or gov_type('SMITH JOHN A') != 'private':
        problems.append('gov_type wrong')
    for n in ('WEST VIRGINIA DIVISION OF NATURAL RESOURCES', 'W.VA. DIV. OF NAT. RES.', 'MO DEPT. OF CONSERVATION',
              'U.S. FISH & WILDLIFE SERVICE', 'PA GAME COMMISSN', 'ST JOHNS RIVER WATER MANAGEMENT DIST',
              'GRAND RIVER CONSERVATION AUTHORITY', 'TOWNSHIP PARKS & REC'):
        if gov_type(n) != 'government':
            problems.append(f'"{n}" should count as a government owner (club decision Oct 31)')
    if match_score('COMMONWEALTH OF KENTUCKY', t)[0] >= MATCH_MIN:
        problems.append('COMMONWEALTH OF KENTUCKY must not match KDFWR by fuzz alone (only via the parcel owner list)')
    for u in ('https://app.regrid.com/us/ky', 'https://www.openstreetmap.org/x', 'https://x.gov/zoning/MapServer/0',
              'https://x.gov/arcgis/rest/services/AssessmentForms_gdb/FeatureServer/0', 'https://x.gov/parcel.aspx?id=1'):
        if not source_refused(u):
            problems.append(f'{u} must be refused as a parcel source')
    if source_refused('https://gis.example.gov/arcgis/rest/services/Parcels/MapServer/0'):
        problems.append('a government REST parcel layer must be accepted')
    # a fake layer: agency block (0..2 x 0..1), one agency square 150 m off the block, one 650 m off, private around
    A = 'STATE OF K4TEST DEPT OF PARKS'
    owners = {(i, j): A for i in range(3) for j in range(2)}
    owners[(4, 0)] = 'K4TEST STATE OF DEPT OF PARKS'      # 100 m gap from (2,0): joins (within 200 m)
    owners[(11, 0)] = A                                    # 600 m gap: must not join
    owners[(3, 0)] = 'SMITH JOHN A'                        # private, between
    owners[(0, 5)] = 'K4TEST COUNTY'                       # other government owner: must not join
    tmp = tempfile.mkdtemp(prefix='kpc_trace_test_')
    try:
        parks = [{'ref': 'K4TEST-01', 'name': 'Block park', 'state_or_prov': 'US-K4', 'lat': 38.0, 'lon': -85.0,
                  'agency_owner_names': [A], 'parcel_layer_url': 'https://fake.example.gov/arcgis/rest/services/P/MapServer/0',
                  'known_acres': 15},
                 {'ref': 'K4TEST-02', 'name': 'Pin 400 m off', 'state_or_prov': 'US-K4', 'lat': 38.0,
                  'lon': -85.0 - 0.0051, 'agency_owner_names': ['STATE OF K4TEST DEPT OF PARKS'],
                  'parcel_layer_url': 'https://fake.example.gov/arcgis/rest/services/P/MapServer/0'},
                 {'ref': 'K4TEST-03', 'name': 'Wrong agency', 'state_or_prov': 'US-K4', 'lat': 38.0, 'lon': -85.0,
                  'agency_owner_names': ['K4TEST WATER DISTRICT'], 'parcel_layer_url': 'https://fake.example.gov/arcgis/rest/services/P/MapServer/0'},
                 {'ref': 'K4TEST-04', 'name': 'Bad row'},
                 {'ref': 'K4TEST-05', 'name': 'Regrid', 'state_or_prov': 'US-K4', 'lat': 38.0, 'lon': -85.0,
                  'agency_owner_names': [A], 'parcel_layer_url': 'https://app.regrid.com/us/k4'}]
        json.dump(parks, open(os.path.join(tmp, 'parks.json'), 'w'))
        web = _FakeServer(owners)
        a = argparse.Namespace(parks=os.path.join(tmp, 'parks.json'), aliases=None, out=tmp, refs=None, all=True,
                               max_minutes=5, resume=False, cache=None, quiet=True, max_km=10.0, official_dir=[], official_acres=[])
        code = run(a, web=web)
        st = json.load(open(os.path.join(tmp, 'state.json')))['results']
        fc = json.load(open(os.path.join(tmp, 'parcels', 'US-K4.json')))
        r1 = st['K4TEST-01']
        if code != 0:
            problems.append(f'exit code {code}')
        if r1['status'] != 'DRAWN' or r1['n_parcels'] != 7:
            problems.append(f'K4TEST-01 should be DRAWN with 7 parcels, got {r1}')
        if r1.get('acres') and abs(r1['acres'] - 7 * 100 * 100 / ACRES_M2) > 0.3:
            problems.append(f'K4TEST-01 acres {r1["acres"]} should be about {7e4 / ACRES_M2:.2f}')
        f1 = [f for f in fc['features'] if f['properties']['ref'] == 'K4TEST-01']
        if not f1 or f1[0]['properties']['grade'] != GRADE or 'P11_0' in f1[0]['properties']['parcel_ids']:
            problems.append('K4TEST-01 feature wrong (grade, or the 600 m parcel joined)')
        txt = open(os.path.join(tmp, 'parcels', 'US-K4.json')).read() + open(os.path.join(tmp, 'parcels', 'report.csv')).read()
        if 'SMITH JOHN' in txt.upper():
            problems.append('a private owner name was written')
        r2 = st['K4TEST-02']
        if r2['status'] != 'DRAWN' or not (350 <= (r2.get('pin_dist_m') or 0) <= 450) or r2['n_parcels'] != 7:
            problems.append(f'K4TEST-02 (pin about 400 m off the block) should be DRAWN, 7 parcels, got {r2}')
        if st['K4TEST-03']['status'] != 'OWNER UNCLEAR':
            problems.append(f'K4TEST-03 should be OWNER UNCLEAR, got {st["K4TEST-03"]}')
        if st['K4TEST-04']['status'] != 'ERROR' or st['K4TEST-05']['status'] != 'ERROR':
            problems.append('bad row and Regrid source must be ERROR and must not stop the batch')
        if any(re.search(r'resultOffset=3', u) for u in web.urls) is False:
            problems.append('paging with resultOffset / resultRecordCount (maxRecordCount 3) was not used')
        owners2 = {(0, 0): A}
        web2 = _FakeServer(owners2)
        pk = dict(parks[0], ref='K4TEST-06', known_acres=None)
        stt, why, feat, info = trace(pk, web2, {}, 'X', time.time() + 60)
        if stt != 'DRAWN' or info['pin_dist_m'] != 0:
            problems.append(f'single-parcel trace wrong: {stt} {why}')
        # held back (club decision Oct 31): a failed size check, and a cut-off trace -> NEEDS A PERSON, no outline,
        # but acres and the pin's distance from the computed outline are still reported
        stt, why, feat, info = trace(dict(parks[0], ref='K4TEST-07', known_acres=1), _FakeServer(owners), {}, 'X',
                                     time.time() + 60)
        if stt != HELD or feat is not None or info.get('pin_dist_m') != 0 or not info.get('acres') \
                or 'size check failed' not in why:
            problems.append(f'a failed size check must be held back as {HELD}: {stt} {why} {info}')
        stt, why, feat, info = trace(dict(parks[0], ref='K4TEST-08', known_acres=None), _FakeServer(owners), {}, 'X',
                                     time.time() + 60, max_km=0.25)
        if stt != HELD or feat is not None or 'cut off' not in why or info.get('pin_dist_m') is None:
            problems.append(f'a cut-off trace must be held back as {HELD}: {stt} {why}')
        # size check (club decision Oct 31, round 4): over 2x (or under 0.2x) the official size is held back; the
        # official acres list wins over the round-14 figure, which is used only when the park is not in the list
        A7 = st['K4TEST-01']['acres']
        off = lambda a, **k: dict(acres=a, agency='K4 Parks', source_url='https://k4.example.gov/list', file='/x/acres.json', **k)  # noqa: E731
        size_cases = [  # (official entry, round-14 figure, list loaded, want status, want words in the source)
            (off(A7 / 2.5), None, True, HELD, 'official acres list (acres.json: K4 Parks)'),
            (off(A7 / 1.9), 1, True, 'DRAWN', 'official acres list'),          # official wins over a bad round-14
            (None, A7 / 3, True, HELD, 'round-14 figure (parks.json known_acres; the park is not in the official'),
            (None, A7 / 1.5, False, 'DRAWN', 'no official acres list given'),
            (off(A7 / 0.15), None, True, HELD, 'official acres list'),         # under 0.2x
            (None, None, True, 'DRAWN', 'no official size: not in the official acres list and no round-14 figure')]
        for i, (oa_, k14, loaded, want, words) in enumerate(size_cases):
            stt, why, feat, info = trace(dict(parks[0], ref=f'K4TEST-S{i}', known_acres=k14, _official_acres=oa_,
                                              _acres_list_loaded=loaded), _FakeServer(owners), {}, 'X', time.time() + 60)
            if stt != want or words not in (info.get('known_acres_source') or '') or words not in why \
                    or (want == HELD and (feat is not None or 'allowed 0.2x-2x' not in why)) \
                    or (feat and feat['properties'].get('known_acres_source') != info['known_acres_source']):
                problems.append(f'size case {i}: want {want} with "{words}", got {stt}: {why} {info}')
        if not (1.85 <= (trace(dict(parks[0], ref='K4TEST-S9', known_acres=None, _official_acres=off(A7 / 1.9)),
                               _FakeServer(owners), {}, 'X', time.time() + 60)[3].get('size_ratio') or 0) <= 1.95):
            problems.append('size_ratio not reported')
        f1, f2 = os.path.join(tmp, 'acres.json'), os.path.join(tmp, 'acres-list.json')
        json.dump({'K4TEST-01': {'acres': 9.5, 'agency': 'K4 Parks', 'source_url': 'https://k4.example.gov/l'},
                   'K4TEST-X': {'acres': 'n/a'}}, open(f1, 'w'))
        json.dump({'K4TEST-01': 99.0, 'K4TEST-02': 12.0}, open(f2, 'w'))
        al = load_official_acres([f1, f2], log=lambda *a: None)
        if al.get('K4TEST-01', {}).get('acres') != 9.5 or al.get('K4TEST-02', {}).get('acres') != 12.0 or 'K4TEST-X' in al:
            problems.append(f'official acres list reading wrong: {al}')
        # Canada: DFRP custodian used only when it is the managing agency
        PCA = 'Parks Canada Agency'
        fed = {(i, 0): PCA for i in range(2)}
        fed[(5, 0)] = 'Public Services and Procurement Canada'
        ca = {'ref': 'K4TEST-CA1', 'name': 'Federal site', 'state_or_prov': 'CA-K4', 'lat': 38.0, 'lon': -85.0,
              'owner_source': 'dfrp', 'parcel_layer_url': 'https://fake.example.gov/arcgis/rest/services/P/MapServer/0'}
        mk = lambda: _FakeServer(fed, owner_key='custodian_en', pid_key='property_number')   # noqa: E731
        stt, why, feat, info = trace(dict(ca, agency_owner_names=[PCA]), mk(), {}, 'X', time.time() + 60)
        if stt != 'DRAWN' or not feat or feat['properties']['owner'] != PCA or feat['properties']['n_parcels'] != 2 \
                or feat['properties']['grade'] != GRADE:
            problems.append(f'DFRP custodian = managing agency should be DRAWN with that owner: {stt} {why}')
        stt, why, feat, info = trace(dict(ca, agency_owner_names=['Government of Yukon']), mk(), {}, 'X', time.time() + 60)
        if stt != 'OWNER UNCLEAR' or feat or 'not the managing agency' not in why:
            problems.append(f'a DFRP custodian that is not the managing agency must not be used: {stt} {why}')
        stt, why, feat, info = trace(dict(ca, agency_owner_names=[PCA]), _FakeServer({(30, 0): PCA}, 'custodian_en',
                                     'property_number'), {}, 'X', time.time() + 60)
        if stt != 'NO PARCEL' or 'federal property (DFRP)' not in why:
            problems.append(f'no DFRP property near the pin must be NO PARCEL: {stt} {why}')
        # 403s: robots.txt alone = no robots rules, the layer is still read; a refused data request = blocked, ERROR
        w403 = _FakeServer(owners, robots403=True)
        try:
            stt, why, feat, info = trace(dict(parks[0], ref='K4TEST-09'), w403, {}, 'X', time.time() + 60)
        except Blocked as e:
            stt, why = 'ERROR', str(e)
        if stt != 'DRAWN' or w403.blocked:
            problems.append(f'a 403 on robots.txt alone must not stop the layer being read: {stt} {w403.blocked}')
        wdat = _FakeServer(owners, data403=True)
        try:
            stt, why = trace(dict(parks[0], ref='K4TEST-10'), wdat, {}, 'X', time.time() + 60)[:2]
        except Blocked as e:
            stt, why = 'ERROR', str(e)
        n_before = len(wdat.urls)
        wdat.get('https://fake.example.gov/arcgis/rest/services/P/MapServer/0/query?f=json')
        if stt != 'ERROR' or 'blocked' not in why or not wdat.blocked or len(wdat.urls) != n_before:
            problems.append(f'a 403 on the data must mark the host blocked, with no retry: {stt} {why} {wdat.blocked}')
        # club rule Oct 31: never take in a parcel inside ANOTHER park's official outline (>= half its area inside)
        od = os.path.join(tmp, 'official')
        os.makedirs(os.path.join(od, 'us-key'))
        os.makedirs(os.path.join(od, 'parkinfo'))
        fk = _FakeServer(owners)

        def sq_ll(i0, j0, i1, j1, shrink=0.0):
            x1, y1 = fk.x0 + i0 * 100 - 50 + shrink, fk.y0 + j0 * 100 - 50
            x2, y2 = fk.x0 + i1 * 100 + 50, fk.y0 + j1 * 100 + 50
            return {'type': 'Polygon', 'coordinates': [[list(fk.back.transform(*p)) for p in
                                                        ((x1, y1), (x1, y2), (x2, y2), (x2, y1), (x1, y1))]]}
        gj = {'type': 'FeatureCollection', 'features': [
            {'type': 'Feature', 'properties': {'ref': 'K4TEST-HQ', 'name': 'Agency HQ park', 'grade': 'official'},
             'geometry': sq_ll(4, 0, 4, 0)},                                  # all of P4_0: excluded
            {'type': 'Feature', 'properties': {'ref': 'K4TEST-EDGE', 'name': 'Edge park', 'grade': 'official'},
             'geometry': sq_ll(2, 1, 2, 1, shrink=70)},                       # 30 % of P2_1: kept
            {'type': 'Feature', 'properties': {'ref': 'K4TEST-APX', 'name': 'Traced park', 'grade': 'approximate (agency parcels)'},
             'geometry': sq_ll(1, 1, 1, 1)},                                  # approximate: never used
            {'type': 'Feature', 'properties': {'ref': 'K4TEST-11', 'name': 'Own outline', 'grade': 'official'},
             'geometry': sq_ll(0, 1, 0, 1)}]}                                 # the park's own: never used
        json.dump(gj, open(os.path.join(od, 'official-test.geojson'), 'w'))
        # an answer-key park joined to record zzz7 of an agency layer covers P0_0 (official); one graded approximate
        # (zzz8) and one with an 'approx' join (zzz9) cover P1_0 and P2_0 and must not count
        json.dump({'zzz': ['https://fake.example.gov/arcgis/rest/services/O/MapServer/1/query', 'NAME', 'test layer']},
                  open(os.path.join(od, 'us-key', 'layers.json'), 'w'))
        json.dump({'parks': {'K4TEST-KEY': {'g': 'official', 'n': 'Key park', 'm': [['zzz7', 'Key park', 2, 'name']]},
                             'K4TEST-KAPX': {'g': 'approximate', 'n': 'Apx', 'm': [['zzz8', 'Apx park', 2, 'name']]},
                             'K4TEST-KAP2': {'g': 'official', 'n': 'Apx2', 'm': [['zzz9', 'Apx2 park', 2, 'approx name']]}}},
                  open(os.path.join(od, 'us-key', 'US-K4.json'), 'w'))
        json.dump({'parks': {r: ['x', '', '', '', '', 38.0, -85.0] for r in ('K4TEST-KEY', 'K4TEST-KAPX', 'K4TEST-KAP2')}},
                  open(os.path.join(od, 'parkinfo', 'US-K4.json'), 'w'))
        fk.other_layer = {7: ('Key park', (0, 0, 0, 0)), 8: ('Apx park', (1, 0, 1, 0)), 9: ('Apx2 park', (2, 0, 2, 0))}
        OO = OfficialOutlines([od], fk, log=lambda *a: None)
        stt, why, feat, info = trace(dict(parks[0], ref='K4TEST-11', known_acres=None, lat=38.0, lon=-85.0 + 0.00115),
                                     fk, {}, 'X', time.time() + 60, outlines=OO)
        ex = {(e['parcel_id'], e['other_ref']) for e in (feat or {}).get('properties', {}).get('excluded_other_park', [])}
        if stt != 'DRAWN' or ex != {('P4_0', 'K4TEST-HQ'), ('P0_0', 'K4TEST-KEY')} or info['n_parcels'] != 5 \
                or 'P4_0 in K4TEST-HQ' not in info['excluded'] or 'P4_0' in feat['properties']['parcel_ids']:
            problems.append(f'parcels inside another park\'s official outline must be left out (and only those): '
                            f'{stt} {ex} {info} {why}')
        if 'P2_1' not in ((feat or {}).get('properties') or {}).get('parcel_ids', []):
            problems.append('a parcel only 30 % inside another park must stay in')
        # state-gis.json (data/state-gis.json, given with --state-gis): its lake-surface layer is not proof, so the key
        # park joined to it (K4TEST-KEY) no longer counts and only P4_0 (HQ file) is left out
        sgp = os.path.join(tmp, 'state-gis.json')
        json.dump({'states': {'K4': [{'url': 'https://fake.example.gov/arcgis/rest/services/O/MapServer/1', 'water': True}]}},
                  open(sgp, 'w'))
        OOw = OfficialOutlines([od], fk, log=lambda *a: None, state_gis=sgp)
        stt, why, feat, info = trace(dict(parks[0], ref='K4TEST-11', known_acres=None, lat=38.0, lon=-85.0 + 0.00115),
                                     fk, {}, 'X', time.time() + 60, outlines=OOw)
        ex = {(e['parcel_id'], e['other_ref']) for e in (feat or {}).get('properties', {}).get('excluded_other_park', [])}
        if OOw.state_gis_used != sgp or OOw.water_layers != 1 or ex != {('P4_0', 'K4TEST-HQ')}:
            problems.append(f'--state-gis lake-surface layers must not count as official outlines: {OOw.state_gis_used} {ex}')
        od2 = os.path.join(tmp, 'official2')
        os.makedirs(od2)
        json.dump({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'geometry': sq_ll(-1, -1, 6, 2),
                   'properties': {'ref': 'K4TEST-BIG', 'name': 'Big park', 'grade': 'official'}}]},
                  open(os.path.join(od2, 'official-big.geojson'), 'w'))
        stt, why, feat, info = trace(dict(parks[0], ref='K4TEST-12', known_acres=None), _FakeServer(owners), {}, 'X',
                                     time.time() + 60, outlines=OfficialOutlines([od2], log=lambda *a: None))
        if stt != HELD or feat is not None or 'K4TEST-BIG' not in why or 'pin itself is inside' not in why \
                or 'P0_0 in K4TEST-BIG' not in info['excluded']:
            problems.append(f'a pin whose agency parcel lies inside another park must be held back: {stt} {why}')
        stt, why = trace(dict(parks[0], ref='K4TEST-13', known_acres=None), _FakeServer(owners), {}, 'X',
                         time.time() + 60, outlines=OfficialOutlines([]))[:2]
        if 'other-park check was not done' not in why:
            problems.append(f'no official outline data must be said in the why: {why}')
        stt, why = trace(dict(parks[0], ref='K4TEST-14', known_acres=None, state_or_prov='US-Q9'), _FakeServer(owners), {},
                         'X', time.time() + 60, outlines=OfficialOutlines([os.path.join(od, 'us-key')], log=lambda *a: None))[:2]
        if 'no official outline data covers US-Q9' not in why:
            problems.append(f'an area no answer key covers must be said in the why: {why}')
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if '21227' not in kp.CLUB_SKIP:
        problems.append('Warren County KY must stay skipped')
    problems += kp.polite_selftest()
    for p in problems:
        ok = False
        print(p)
    print('PASS' if ok else 'FAIL')
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description='KPC parcel tracer: approximate outline from agency-owned parcels')
    ap.add_argument('--parks', help='parks.json (see the README)')
    ap.add_argument('--aliases', help='owner_aliases.json (optional)')
    ap.add_argument('--out', default='.', help='output folder (parcels/<area>.json, parcels/report.csv, state.json)')
    g = ap.add_mutually_exclusive_group()
    g.add_argument('--refs', help='comma-separated park numbers, run in that order')
    g.add_argument('--all', action='store_true', help='every park in parks.json')
    ap.add_argument('--max-minutes', type=float, default=50, help='stop starting new parks after this (default 50)')
    ap.add_argument('--resume', action='store_true', help='skip parks already done in <out>/state.json')
    ap.add_argument('--max-km', type=float, default=10.0, help='growth limit around the pin (default 10 km)')
    ap.add_argument('--cache', help='cache folder for public catalogue replies (parcel replies are never cached)')
    ap.add_argument('--official-dir', action='append',
                    help='folder with the club\'s official outlines (KPC-Data/data: us-key/, ca-key/, parkinfo/; or a folder '
                         'with ky-answer-key.json + ky-*.geojson, state-gis.json, official-*.geojson); repeatable. '
                         'Default: $KPC_OFFICIAL_DIR, else KPC-Data/data when the tool sits in KPC-Data')
    ap.add_argument('--state-gis', help='data/state-gis.json (its lake-surface layers are not proof of an outline). Default: '
                         'state-gis.json in an --official-dir, else KPC-Data/data/state-gis.json when the tool sits in KPC-Data')
    ap.add_argument('--official-acres', action='append',
                    help="the club's official acres list (kpc_acres acres.json or acres-list.json); repeatable, first "
                         'file with a ref wins. Default: $KPC_OFFICIAL_ACRES, else acres.json or acres/acres.json in an '
                         '--official-dir or KPC-Data/data. A park not in it falls back to its round-14 known_acres')
    ap.add_argument('--quiet', action='store_true')
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if not args.parks or not (args.refs or args.all):
        ap.print_usage(sys.stderr)
        print('bad input: --parks and one of --refs / --all are needed', file=sys.stderr)
        return 2
    return run(args)


if __name__ == '__main__':
    sys.exit(main())
