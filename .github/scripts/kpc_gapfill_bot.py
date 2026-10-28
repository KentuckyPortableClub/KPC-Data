#!/usr/bin/env python3
"""GAP FILLER (Fable, chat 10 'bot workshop', Oct 28 2026). Brandon: 'a bot that will look at our scoreboard and find the info
to fill it in'. LEADS ONLY: it never adds anything to a key, an outline or a card. For every park on the scoreboard that still
has NO outline it goes looking for the official polygon that should cover it and writes down what it found, so chat 2 (keys)
and chat 8 (research desk) can decide. Nothing it writes is used by the site.

Per missing park, at most ~8 polite requests, stopping at the first SURE find:
  1 LAYERS WE ALREADY READ for that state / province (KPC-Links data/state-gis.json, data/us-key/layers.json,
    data/ca-key/layers.json): one ArcGIS point query at the POTA pin per layer. A polygon under the pin whose name shares the
    park's core words = 'likely a NAME MISMATCH in our matcher' (both names listed for chat 2). A different name = 'different
    land under the pin' (written down, not a find).
  2 THE MANAGING AGENCY'S OWN ArcGIS: the agency hosts from chat 8's OFFICIAL_MAPS survey (OFFICIAL_MAPS_patterns.json) and the
    host of the park's own page (data/parkinfo). An ArcGIS Online org gets a /sharing/rest/search for the park's core name
    (Feature Services only); an agency ArcGIS Server gets its /rest/services?f=json folder list filtered by park / land /
    boundary / recreation words. Then one point query per candidate polygon layer (at most 3).
  3 THE STATE'S OPEN-DATA PORTAL: ArcGIS Hub search (hub.arcgis.com/api/v3/datasets?q=<name>), keeping only datasets whose
    publisher reads like the state's own agency (official_org rule from chat 2's lead tester).
  4 USGS PAD-US at the pin: one point query; Unit_Nm, Mang_Name, Des_Tp, GIS_Acres, Category are REPORTED. A Proclamation or
    Easement record is never offered as an outline (house rule: the park is where the designation legally applies).
  5 nothing -> 'no official layer found' with the list of what was tried.
Each FIND carries: the layer url, publisher, licence + date when the layer names its ArcGIS item (serviceItemId ->
/sharing/rest/content/items/<id>: licenseInfo + accessInformation; else 'terms not read'), the polygon's name and size (its
acres field when it has one) against the park's name / type, whether the pin is inside, and 'sure' = YES only by the house rule
(pin inside + name words match + similar size when both sizes are known), else 'check'.

Output (all review material): data/gapfill/<area>.json, data/gapfill/review.md (finds sorted by layer, the layers that close
the most parks first; the name-mismatch list for chat 2; the 'no layer found' counts), one row per layer found APPENDED to
data/intake/queue.json for the intake bot (from: 'gap-filler', closes: [refs]), and one 'grade me' line per batch for chat 8
(kpc_status.py). A park checked within REFRESH_DAYS (30) is skipped. Manners: kpc_manners.py (robots.txt with the ArcGIS REST
exemption, 1 request / 2 s per host, three strikes = a day's rest). MINUTES per chunk; never fails (exit 0 always).

Env: AREAS='US-KY US-NV' (blank = the next unfinished areas in GAP_QUEUE order) · MINUTES (55) · LINKS (KPC-Links checkout,
     default 'links') · OUT (data/gapfill) · REFRESH_DAYS (30) · MAXREQ (8 per park) · PARKS (cap per area per chunk)
     --selftest = no web: the name-mismatch judgment, the 'sure' rule, the missing-list counts for US-KY and US-NV.
"""
import json, os, pathlib, re, subprocess, sys, time, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kpc_manners import Manners  # noqa: E402
try: from kpc_truth_bot import QUEUE as TRUTH_QUEUE, STATE_NAMES  # noqa: E402
except Exception:  # noqa: BLE001
    TRUTH_QUEUE, STATE_NAMES = [], {}

REPO = pathlib.Path('.').resolve()
OUT = pathlib.Path(os.environ.get('OUT') or 'data/gapfill')
LINKS = pathlib.Path(os.environ.get('LINKS') or 'links')
T0 = time.time(); LIMIT = float(os.environ.get('MINUTES') or 55) * 60
REFRESH_DAYS = int(os.environ.get('REFRESH_DAYS') or 30)
MAXREQ = int(os.environ.get('MAXREQ') or 8)
PARK_CAP = int(os.environ.get('PARKS') or 0)
TODAY = time.strftime('%Y-%m-%d')
VER = 1
SIZE_TOL = 0.25     # 'similar size': within 25% (the observations-log threshold); the truth checker's 15% is for AGREEMENT of a size we already trust
PADUS = 'https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0'   # same as kpc-bounds.js
PADUS_FIELDS = 'OBJECTID,Unit_Nm,Loc_Nm,Mang_Name,Loc_Mang,Des_Tp,Pub_Access,GIS_Acres,Category'
FIRST = ['US-KY', 'US-NV', 'US-ID', 'US-MS', 'US-WA', 'US-UT', 'US-AR', 'US-OR', 'US-NC']
CA_FIRST = ['CA-ON', 'CA-QC', 'CA-NB', 'CA-NS']
GAP_QUEUE = FIRST + [a for a in TRUTH_QUEUE if a.startswith('US-') and a not in FIRST] + CA_FIRST + \
            [a for a in TRUTH_QUEUE if a.startswith('CA-') and a not in CA_FIRST]
if not TRUTH_QUEUE: GAP_QUEUE = FIRST + CA_FIRST
# pin-only / line kinds (copied from chat 2's kpc_candidates.py SKIP_TYPE + the scoreboard note): not 'missing'
SKIP_TYPE = re.compile(r'parkway|byway|scenic (highway|drive|road)|(national|state|scenic|recreation|geologic|historic) trail'
                       r'|blm (backcountry airstrip|interpretive site)|wild and scenic river|scenic river|water trail', re.I)
KINDW = re.compile(r'\b(state|national|provincial|park|parks|forest|wildlife|management|area|areas|recreation|recreational|conservation|nature|natural|preserve|reserve|refuge|historic|historical|site|game|land|lands|wma|sp|srp|sra|sf|shs|nwr|trail|the|of|and|at|county|city|regional|unit|access|public|fishing|lake|hunting|outdoor|memorial|monument|wilderness|road|blm|usfs|nps|resort|boundary|boundaries|polygon|polygons)\b')
CLASS = [('park', r'\b(park|parks|sp|srp|sra|s\.p\.)\b'), ('forest', r'\b(forest|sf|national forest)\b'),
         ('wildlife', r'\b(wildlife|wma|refuge|nwr|game|hunting|waterfowl)\b'), ('historic', r'\b(historic|historical|monument|memorial|battlefield|shs)\b'),
         ('trail', r'\b(trail|trails|greenway)\b'), ('preserve', r'\b(preserve|nature preserve|natural area|conservation area|reserve)\b')]
LAND_WORDS = re.compile(r'park|land|bound|recreat|wildlife|wma|forest|conserv|preserve|refuge|protect|public|trail|outdoor|histor|state|natural|manage|owner|cadast', re.I)
NOT_OFFICIAL = re.compile(r'county|city of|town of|village|township|borough|parish|district|universit|college|school|foundation|club|association|\bllc\b|\binc\b|company|realty|church|tribe\b|student|personal', re.I)
OFFICIAL_ORG = re.compile(r'department|dept|division|\bdnr\b|\bdcr\b|\bdep\b|\bdec\b|\bdeq\b|state parks?|parks (?:and|&) (?:recreation|wildlife|tourism)|natural resources|fish (?:and|&) (?:game|wildlife)|game (?:and|&) fish|wildlife|forestry|commission|agency|ministry|ministère|government|gouvernement|commonwealth|state of|province|parcs|gis office|geographic information|geospatial|open data|national park service|forest service|bureau of land|fish and wildlife service|usgs|army corps', re.I)
FED_ORG = re.compile(r'national park service|\bnps\b|forest service|\busfs\b|bureau of land management|\bblm\b|fish (?:and|&) wildlife service|\bfws\b|army corps|\busace\b|bureau of reclamation|tennessee valley authority|\btva\b|parks canada|environment and climate change canada', re.I)
PAD_NEVER = re.compile(r'proclamation|easement', re.I)
STAT = {'parks': 0, 'checked': 0, 'skipped_fresh': 0, 'finds': 0, 'sure': 0, 'mismatch': 0, 'different_land': 0, 'padus_only': 0, 'nothing': 0, 'requests': 0, 'errors': 0}
M = None
ITEM_CACHE = {}
SERVER_CACHE = {}


def notice(m): print('::notice title=Gap filler::' + str(m).replace('\n', ' ')[:900], flush=True)
def late(): return time.time() - T0 > LIMIT
def load(p, d):
    try: return json.load(open(p, encoding='utf-8'))
    except Exception: return d  # noqa: BLE001
def save(p, obj):
    pathlib.Path(p).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(p).write_text(json.dumps(obj, ensure_ascii=False, indent=1, sort_keys=True) + '\n', encoding='utf-8')
def low(x): return ' '.join(re.sub(r'[^a-z0-9 ]', ' ', str(x or '').lower().replace('&', ' and ').replace("'", '')).split())
def core(x): return ' '.join(KINDW.sub(' ', low(x)).split())
def host_of(u): return urllib.parse.urlparse(u).netloc.lower().split(':')[0]
def layer_url(u): return re.sub(r'/query/?(\?.*)?$', '', (u or '').strip().rstrip('/'))
def in_repo(p):
    try: return str(pathlib.Path(p).resolve()).startswith(str(REPO))
    except Exception: return False  # noqa: BLE001


# ---- judgments (pure, selftested)
def core_words(name): return {w for w in core(name).split() if len(w) > 2 and not w.isdigit()}


def classes(name):
    n = low(name)
    return {c for c, rx in CLASS if re.search(rx, n)}


COMPAT = {'park': {'park', 'historic', 'preserve'}, 'historic': {'park', 'historic', 'preserve'}, 'preserve': {'park', 'historic', 'preserve', 'wildlife'},
          'wildlife': {'wildlife', 'preserve'}, 'forest': {'forest'}, 'trail': {'trail'}}


def judge_name(park, poly):
    """How a polygon's name relates to the park's: 'match' (same core words, same kind of place), 'mismatch' (same place name,
    a different but kindred kind word, or only part of the words: our matcher likely missed it, chat 2 looks at both names),
    'different' (another piece of land under the pin: no shared words, or an unkindred kind such as park vs forest)."""
    a, b = core_words(park), core_words(poly)
    if not a or not b: return 'different'
    shared = a & b
    if not shared: return 'different'
    ca, cb = classes(park), classes(poly)
    kindred = not ca or not cb or any(y in COMPAT.get(x, {x}) for x in ca for y in cb)
    if not kindred: return 'different'     # Green River Lake State Park vs Green River State Forest: same name, another kind of land
    if a == b: return 'match' if (ca == cb or not ca or not cb) else 'mismatch'
    if a <= b or b <= a or len(shared) / len(a | b) >= 0.5: return 'match' if (ca == cb or not ca or not cb) else 'mismatch'
    return 'mismatch'


def similar_size(ours, theirs):
    """None when either size is unknown; else within SIZE_TOL."""
    try: o, t = float(ours or 0), float(theirs or 0)
    except Exception: return None  # noqa: BLE001
    if o <= 0 or t <= 0: return None
    return abs(o - t) / max(o, t) <= SIZE_TOL


def sure_rule(pin_inside, name_rel, size_ok):
    """The house rule: pin inside + name words match + similar size when both sizes are known -> 'YES'; else 'check'."""
    if pin_inside and name_rel == 'match' and size_ok is not False: return 'YES'
    return 'check'


# ---- the missing list
def pins():
    """{ref: (name, type, lat, lon, page url, acres or 0)} from data/parkinfo (US-XX + CA) in KPC-Data, else KPC-Links."""
    P = {}
    for base in (pathlib.Path('data/parkinfo'), LINKS / 'data/parkinfo'):
        for f in list(base.glob('US-*.json')) + [base / 'CA.json']:
            d = load(f, {}).get('parks') or {}
            for r, v in d.items():
                if r in P: continue
                if isinstance(v, list) and len(v) >= 7:
                    P[r] = (v[0], v[2] if len(v) > 2 else '', v[5], v[6], v[1] if len(v) > 1 else '', 0)
                elif isinstance(v, dict):
                    P[r] = (v.get('n') or v.get('name') or '', v.get('t') or v.get('type') or '', v.get('la') or v.get('lat'), v.get('lo') or v.get('lon'), v.get('url') or v.get('page') or '', v.get('a') or 0)
    if not P:   # last resort: the POTA pin list
        for row in (load('data/northam.json', {}) or load(LINKS / 'data/northam.json', {})).get('rows') or []:
            if len(row) >= 5 and row[0] == 'POTA': P[row[1]] = (row[2], '', row[3], row[4], '', 0)
    return P


def key_file(area): return pathlib.Path('data/us-key' if area.startswith('US-') else 'data/ca-key') / f'{area}.json'
KY_LAYERS = [('https://kygisserver.ky.gov/arcgis/rest/services/WGS84WM_Services/Ky_State_Parks_Features_WGS84WM/MapServer/8', 'NAME', 'Kentucky State Parks boundaries (kygisserver)'),
             ('https://kygisserver.ky.gov/arcgis/rest/services/WGS84WM_Services/Ky_Public_Hunting_Areas_WGS84WM/MapServer/1', 'NAME', 'Kentucky public hunting areas / WMAs (kygisserver)'),
             ('https://kygisserver.ky.gov/arcgis/rest/services/WGS84WM_Services/Ky_KNP_State_Nature_Preserves_WGS84WM/MapServer/0', 'NAME', 'Kentucky state nature preserves (kygisserver)'),
             ('https://kygisserver.ky.gov/arcgis/rest/services/WGS84WM_Services/Ky_KNP_Natural_Areas_WGS84WM/MapServer/0', 'NAME', 'Kentucky natural areas (kygisserver)')]


def ky_key():
    """Kentucky has no data/us-key file: its key is KPC-Links data/ky-answer-key.json ('missing' = refs with no tracts) and its
    pins are kpc-ky-data.json. Returned in the us-key shape ({ref: {n, t, m}}) plus {ref: (la, lo, web)}."""
    ak = load(LINKS / 'data/ky-answer-key.json', {})
    K = {r: {'n': v.get('n'), 't': v.get('t'), 'm': v.get('tracts') or []} for r, v in (ak.get('parks') or {}).items()}
    pin = {x['c']: (x.get('la'), x.get('lo'), x.get('web') or x.get('off') or '') for x in load(LINKS / 'kpc-ky-data.json', {}).get('parks', []) if x.get('c')}
    return K, pin


def missing_for(area, P=None):
    """[{ref, n, t, la, lo, a, page}] parks of the area with no outline: the scoreboard's 'missing' rows when
    data/review/scoreboard-parks.json exists, else derived from the key (no 'm' records, not a pin-only / line kind)."""
    P = P if P is not None else pins()
    out = []
    sb = load('data/review/scoreboard-parks.json', None)
    if sb:
        rows = sb.get('parks') or sb.get('rows') or []
        rows = list(rows.items()) if isinstance(rows, dict) else [(r.get('ref') or r.get('r'), r) for r in rows]
        for ref, r in rows:
            if not isinstance(r, dict) or (r.get('outline') or r.get('o')) not in ('missing', 'miss'): continue   # the scoreboard bot's compact rows use o = 'miss'
            ar = r.get('area') or r.get('a') or r.get('st') or ''
            if ar and len(ar) == 2: ar = ('US-' if str(ref).startswith('US-') else 'CA-') + ar
            if ar != area: continue
            v = P.get(ref) or ('', '', None, None, '', 0)
            typ = r.get('type') or r.get('t')
            if isinstance(typ, int): typ = (sb.get('types') or [])[typ] if typ < len(sb.get('types') or []) else ''   # compact rows: t is an index into the 'types' list
            out.append({'ref': ref, 'n': r.get('name') or r.get('n') or v[0], 't': typ or v[1],
                        'la': r.get('lat') if r.get('lat') is not None else v[2], 'lo': r.get('lon') if r.get('lon') is not None else v[3], 'a': r.get('acres') or v[5], 'page': v[4]})
        return [p for p in out if p['la'] is not None and p['lo'] is not None]
    K = load(key_file(area), {}).get('parks') or {}
    kypin = {}
    if area == 'US-KY' and not K: K, kypin = ky_key()
    for ref, p in K.items():
        if p.get('m'): continue
        v = P.get(ref)
        if not v and ref in kypin: v = (p.get('n'), p.get('t'), kypin[ref][0], kypin[ref][1], kypin[ref][2], 0)
        name, t = p.get('n') or (v[0] if v else ''), p.get('t') or (v[1] if v else '')
        if SKIP_TYPE.search(t or '') or SKIP_TYPE.search(name or ''): continue
        if not v or v[2] is None or v[3] is None or not core(name): continue
        out.append({'ref': ref, 'n': name, 't': t, 'la': v[2], 'lo': v[3], 'a': p.get('a') or v[5] or 0, 'page': v[4]})
    return out


# ---- what we already read, who the agency is
def area_layers(area):
    """[(url, name field, label)] polygon layers we already read for this state / province."""
    st = area[3:]
    rows = list(KY_LAYERS) if area == 'US-KY' else []
    seen = {r[0] for r in rows}
    for x in (load(LINKS / 'data/state-gis.json', {}).get('states') or {}).get(st, []) or []:
        u = layer_url(x.get('url'))
        if u and u not in seen: seen.add(u); rows.append((u, x.get('nm') or '', x.get('ag') or ''))
    codes = set()
    for p in (load(key_file(area), {}).get('parks') or {}).values():
        for m in p.get('m') or []:
            if m and isinstance(m[0], str) and ':' in m[0]: codes.add(m[0].split(':')[0])
    L = load('data/us-key/layers.json' if area.startswith('US-') else 'data/ca-key/layers.json', {})
    for code, row in L.items():
        if code not in codes and not any(code.startswith(c) for c in codes): continue
        u = layer_url(row[0] if isinstance(row, list) else row)
        if u and u not in seen: seen.add(u); rows.append((u, row[1] if isinstance(row, list) and len(row) > 1 else '', row[2] if isinstance(row, list) and len(row) > 2 else code))
    return rows


def agency_hosts(area, page):
    """Agency hosts for the area: chat 8's OFFICIAL_MAPS patterns rows + the park's own page host."""
    hosts = []
    for r in load(LINKS / '.claude/build/research/OFFICIAL_MAPS/OFFICIAL_MAPS_patterns.json', []) or []:
        if r.get('state') == area:
            for k in ('agency_site', 'address_pattern', 'list_page'):
                h = host_of('https://' + str(r.get(k) or '').replace('https://', '').replace('http://', '')) if r.get(k) else ''
                if h and '<' not in h and h not in hosts: hosts.append(h)
    h = host_of(page or '')
    if h and h not in hosts and not re.search(r'pota\.app|recreation\.gov|facebook|google', h): hosts.append(h)
    hosts = [h for h in hosts if h not in ('same', 'none', '')]
    return hosts[:4]


def org_ids(area):
    st = area[3:]
    ids = set()
    for x in (load(LINKS / 'data/state-gis.json', {}).get('states') or {}).get(st, []) or []:
        m = re.match(r'https?://services\d*\.arcgis\.com/([A-Za-z0-9]+)/', x.get('url', ''))
        if m: ids.add(m.group(1))
    return sorted(ids)


def agency_servers(area):
    st = area[3:]
    roots = set()
    for x in (load(LINKS / 'data/state-gis.json', {}).get('states') or {}).get(st, []) or []:
        m = re.match(r'(https?://[^/]+/[^/]*/rest/services)', x.get('url', ''))
        if m and 'arcgis.com' not in m.group(1): roots.add(m.group(1))
    if area == 'US-KY': roots.add('https://kygisserver.ky.gov/arcgis/rest/services')
    return sorted(roots)


def official_org(name, area):
    """An org whose NAME says it is the state's / province's own agency or a federal land agency."""
    n = name or ''
    if not n or NOT_OFFICIAL.search(n): return False
    if FED_ORG.search(n): return True
    st = area[3:]; sn = STATE_NAMES.get(st, st)
    return bool((re.search(re.escape(sn), n, re.I) or re.search(r'\b%s\b' % st, n)) and OFFICIAL_ORG.search(n))


# ---- polite JSON
def J(u, params=None, budget=None):
    """One polite GET that returns parsed JSON or None. budget = the park's request counter (a list of one int)."""
    if budget is not None:
        if budget[0] >= MAXREQ: return None
        budget[0] += 1
    STAT['requests'] += 1
    url = u + ('?' + urllib.parse.urlencode(params) if params else '')
    st, _h, body, _f = M.get(url, timeout=45, accept='application/json,*/*;q=0.5')
    if st != 200 or not body:
        if st not in ('rest', 'robots'): STAT['errors'] += 1
        return None
    try: j = json.loads(body.decode('utf-8', 'replace'))
    except Exception: return None  # noqa: BLE001
    if isinstance(j, dict) and j.get('error'): return None
    if budget is not None and len(budget) > 1: budget[1] += 1
    return j


def point_query(lu, la, lo, budget):
    """ArcGIS point query at the pin: [attributes dicts] of the polygons under it (returnGeometry=false)."""
    j = J(lu + '/query', {'geometry': f'{lo},{la}', 'geometryType': 'esriGeometryPoint', 'inSR': 4326, 'spatialRel': 'esriSpatialRelIntersects',
                          'outFields': '*', 'returnGeometry': 'false', 'f': 'json'}, budget)
    if not j or not isinstance(j.get('features'), list): return None
    return [f.get('attributes') or {} for f in j['features']]


def name_field(attrs, hint=''):
    if hint and hint in attrs: return hint
    keys = list(attrs.keys())
    good = [k for k in keys if re.search(r'name|nm|facility|label|site|unit|prop|title', k, re.I)
            and not re.search(r'admin|state|county|office|agency|own|mgr|manag|type|desig|file|url|link|city|region|district|field|short|abbr', k, re.I)
            and isinstance(attrs[k], str) and attrs[k].strip()]
    if good: return good[0]
    strs = [k for k in keys if isinstance(attrs[k], str) and attrs[k].strip() and not re.search(r'objectid|globalid|shape', k, re.I)]
    return strs[0] if strs else ''


def acres_of(attrs):
    for k, v in attrs.items():
        if re.search(r'acre|gis_acres|area_ac|acreage', k, re.I) and not re.search(r'water', k, re.I):
            try:
                a = float(v)
                if a > 0: return round(a)
            except Exception: pass  # noqa: BLE001
    for k, v in attrs.items():
        if re.search(r'^(hectare|ha_|area_ha|hectares)', k, re.I):
            try:
                a = float(v)
                if a > 0: return round(a * 2.47105)
            except Exception: pass  # noqa: BLE001
    return 0


def terms_of(lu, budget):
    """(licence, date, publisher) from the layer's ArcGIS item when it names one; else 'terms not read'."""
    if lu in ITEM_CACHE: return ITEM_CACHE[lu]
    res = ('terms not read', '', '')
    meta = J(lu, {'f': 'json'}, budget)
    if meta:
        iid = meta.get('serviceItemId')
        if iid:
            it = J(f'https://www.arcgis.com/sharing/rest/content/items/{iid}', {'f': 'json'}, budget)
            if it:
                lic = re.sub(r'<[^>]+>', ' ', str(it.get('licenseInfo') or '')); lic = ' '.join(lic.split())[:300]
                res = (lic or 'no licence text on the item', time.strftime('%Y-%m-%d', time.gmtime((it.get('modified') or 0) / 1000)) if it.get('modified') else '',
                       (it.get('accessInformation') or it.get('owner') or '')[:160])
        elif meta.get('copyrightText'): res = (str(meta.get('copyrightText'))[:300], '', str(meta.get('copyrightText'))[:160])
    ITEM_CACHE[lu] = res
    return res


# ---- the hunt
def consider(park, lu, attrs, hint, publisher, where, budget, finds):
    """One polygon under the pin -> a find (and its verdict) appended to finds. Returns the verdict ('sure', 'check', 'mismatch', 'different')."""
    nf = name_field(attrs, hint)
    pname = str(attrs.get(nf) or '').strip() if nf else ''
    rel = judge_name(park['n'], pname) if pname else 'different'
    if rel == 'different':
        finds.append({'where': where, 'layer': lu, 'poly': pname[:120], 'rel': 'different land under the pin', 'acres': acres_of(attrs)})
        return 'different'
    size_ok = similar_size(park.get('a'), acres_of(attrs))
    sure = sure_rule(True, rel, size_ok)
    lic, date, pub2 = terms_of(lu, budget) if rel == 'match' else ('terms not read', '', '')
    f = {'where': where, 'layer': lu, 'poly': pname[:120], 'field': nf, 'acres': acres_of(attrs), 'ours_acres': park.get('a') or 0, 'pin_inside': True,
         'rel': 'name mismatch (likely our matcher)' if rel == 'mismatch' else 'name match', 'sure': sure, 'publisher': publisher or pub2, 'licence': lic, 'date': date}
    finds.append(f)
    return 'sure' if sure == 'YES' else ('mismatch' if rel == 'mismatch' else 'check')


def hunt(park, area, layers, hosts, orgs, servers, budget):
    """The five steps for one park. Returns (tried list, finds list, verdict)."""
    la, lo = park['la'], park['lo']; tried = []; finds = []; verdict = 'nothing'
    # 1 layers we already read
    for lu, nf, label in layers:
        if budget[0] >= MAXREQ - 1: break
        tried.append(f'read-layer {label or lu}')
        hits = point_query(lu, la, lo, budget)
        for a in hits or []:
            v = consider(park, lu, a, nf, label, 'layer we already read', budget, finds)
            if v == 'sure': return tried, finds, 'sure'
            verdict = v if verdict == 'nothing' or v == 'mismatch' else verdict
    q = ' '.join(sorted(core_words(park['n'])))[:80] or core(park['n'])
    # 2 the agency's own ArcGIS: org search + agency servers
    cands = []
    if q and orgs and budget[0] < MAXREQ - 2:
        tried.append('agency org search ' + ','.join(orgs[:2]))
        oq = ' OR '.join(f'orgid:{o}' for o in orgs[:3])
        j = J('https://www.arcgis.com/sharing/rest/search', {'q': f'({q}) AND ({oq}) AND type:"Feature Service"', 'num': 5, 'f': 'json'}, budget)
        for it in (j or {}).get('results') or []:
            if it.get('url'): cands.append((it['url'].rstrip('/'), it.get('owner') or '', it.get('title') or ''))
    for root in servers[:1]:
        if budget[0] >= MAXREQ - 2 or len(cands) >= 3: break
        tried.append('agency server ' + host_of(root))
        if root not in SERVER_CACHE: SERVER_CACHE[root] = J(root, {'f': 'json'}, budget) or {}
        for s in (SERVER_CACHE[root].get('services') or []):
            nm = s.get('name') or ''
            if LAND_WORDS.search(nm) and s.get('type') in ('MapServer', 'FeatureServer'):
                cands.append((f"{root}/{nm}/{s['type']}", host_of(root), nm))
            if len(cands) >= 3: break
    # 3 the open-data portal (ArcGIS Hub)
    if q and budget[0] < MAXREQ - 2 and len(cands) < 3:
        tried.append('hub search')
        sn = STATE_NAMES.get(area[3:], '')
        j = J('https://hub.arcgis.com/api/v3/datasets', {'q': f'{q} {sn}'.strip(), 'filter[type]': 'Feature Layer', 'page[size]': 6, 'f': 'json'}, budget)
        for d in (j or {}).get('data') or []:
            at = d.get('attributes') or {}
            pub = at.get('orgName') or at.get('source') or at.get('owner') or ''
            u = at.get('url') or ''
            if u and (official_org(pub, area) or any(h in u for h in hosts)):
                cands.append((u.rstrip('/'), pub, at.get('name') or ''))
    # one point query per candidate polygon layer (<= 3)
    for svc, pub, title in cands[:3]:
        if budget[0] >= MAXREQ - 1: break
        lu = svc if re.search(r'/(Feature|Map)Server/\d+$', svc) else None
        if not lu:
            meta = J(svc, {'f': 'json'}, budget) or {}
            lays = [l for l in (meta.get('layers') or []) if (l.get('geometryType') or '') in ('esriGeometryPolygon', '')][:1]
            if not lays: continue
            lu = f"{svc}/{lays[0].get('id', 0)}"
        tried.append('candidate ' + (title or lu)[:60])
        hits = point_query(lu, la, lo, budget)
        for a in hits or []:
            v = consider(park, lu, a, '', pub, 'agency / portal search', budget, finds)
            if v == 'sure': return tried, finds, 'sure'
            verdict = v if verdict == 'nothing' or v == 'mismatch' else verdict
    # 4 PAD-US at the pin (reported, never an outline when Proclamation / Easement)
    if budget[0] < MAXREQ:
        tried.append('PAD-US point')
        j = J(PADUS + '/query', {'geometry': f'{lo},{la}', 'geometryType': 'esriGeometryPoint', 'inSR': 4326, 'spatialRel': 'esriSpatialRelIntersects',
                                 'outFields': PADUS_FIELDS, 'returnGeometry': 'false', 'f': 'json'}, budget)
        for ft in (j or {}).get('features') or []:
            a = ft.get('attributes') or {}
            row = {'where': 'PAD-US', 'layer': PADUS, 'poly': str(a.get('Unit_Nm') or '')[:120], 'manager': a.get('Mang_Name'), 'des': a.get('Des_Tp'), 'acres': round(float(a.get('GIS_Acres') or 0)),
                   'category': a.get('Category'), 'ours_acres': park.get('a') or 0, 'pin_inside': True}
            if PAD_NEVER.search(str(a.get('Category') or '') + ' ' + str(a.get('Des_Tp') or '')):
                row['rel'] = 'Proclamation / Easement: never an outline'; row['sure'] = 'no'
            else:
                rel = judge_name(park['n'], row['poly'])
                row['rel'] = {'match': 'name match', 'mismatch': 'name mismatch (likely our matcher)', 'different': 'different land under the pin'}[rel]
                row['sure'] = sure_rule(True, rel, similar_size(park.get('a'), row['acres'])) if rel != 'different' else 'no'
                if rel == 'match' and row['sure'] == 'YES' and verdict != 'sure': verdict = 'padus'
                elif rel == 'mismatch' and verdict in ('nothing', 'different'): verdict = 'mismatch'
            finds.append(row)
    if verdict == 'nothing' and any(f.get('rel') == 'different land under the pin' for f in finds): verdict = 'different'
    return tried, finds, verdict


def run_area(area, state, P):
    f = OUT / f'{area}.json'
    D = load(f, None) or {'area': area, 'about': 'GAP FILLER leads (review only; never a key): per park with no outline, what official layer was found under its pin and how sure. Rules in the script docstring.', 'parks': {}}
    D['read'] = TODAY; D['ver'] = VER
    miss = missing_for(area, P)
    layers, orgs, servers = area_layers(area), org_ids(area), agency_servers(area)
    done = 0; fresh = 0
    for park in miss:
        if late(): break
        if PARK_CAP and done >= PARK_CAP: break
        old = D['parks'].get(park['ref']) or {}
        if old.get('read') and (time.time() - time.mktime(time.strptime(old['read'], '%Y-%m-%d'))) < REFRESH_DAYS * 86400 and old.get('ver') == VER:
            fresh += 1; continue
        budget = [0, 0]   # [requests made, answers that parsed]
        hosts = agency_hosts(area, park.get('page'))
        tried, finds, verdict = hunt(park, area, layers, hosts, orgs, servers, budget)
        best = next((x for x in finds if x.get('sure') == 'YES'), None) or next((x for x in finds if x.get('rel') == 'name match'), None) or \
               next((x for x in finds if 'mismatch' in str(x.get('rel'))), None)
        why = {'sure': 'pin inside + name match' + (' + similar size' if best and similar_size(park.get('a'), best.get('acres')) else ' (size not compared)'),
               'padus': 'PAD-US record matches the name under the pin (fee / designation): chat 2 checks the manager and type',
               'mismatch': 'a polygon under the pin shares the park name: likely a name mismatch in our matcher',
               'check': 'a polygon under the pin matches the name but the size differs or is unknown',
               'different': 'only different land found under the pin', 'nothing': 'no official layer found; tried: ' + ', '.join(tried)[:300]}[verdict]
        if budget[0] and not budget[1]: why = 'no answer from any host this run (rested or errors): tried again next run'; verdict = 'nothing'
        D['parks'][park['ref']] = {'n': park['n'], 't': park['t'], 'la': park['la'], 'lo': park['lo'], 'a': park.get('a') or 0, 'read': TODAY if (budget[1] or not budget[0]) else '', 'ver': VER, 'requests': budget[0], 'answers': budget[1],
                                   'tried': tried, 'finds': finds, 'find': best, 'sure': (best or {}).get('sure', 'no') if best else 'no', 'verdict': verdict, 'why': why}
        done += 1; STAT['checked'] += 1
        STAT[{'sure': 'sure', 'padus': 'padus_only', 'mismatch': 'mismatch', 'check': 'finds', 'different': 'different_land', 'nothing': 'nothing'}[verdict]] += 1
        if verdict == 'sure': STAT['finds'] += 1
    STAT['parks'] += len(miss); STAT['skipped_fresh'] += fresh
    checked = [r for r in D['parks'] if any(p['ref'] == r for p in miss)]
    D['counts'] = {'missing': len(miss), 'checked_ever': len(checked), 'sure': sum(1 for r in checked if D['parks'][r].get('verdict') == 'sure'),
                   'padus_match': sum(1 for r in checked if D['parks'][r].get('verdict') == 'padus'), 'name_mismatch': sum(1 for r in checked if D['parks'][r].get('verdict') == 'mismatch'),
                   'check': sum(1 for r in checked if D['parks'][r].get('verdict') == 'check'), 'different_land': sum(1 for r in checked if D['parks'][r].get('verdict') == 'different'),
                   'nothing': sum(1 for r in checked if D['parks'][r].get('verdict') == 'nothing'), 'layers_read': len(layers)}
    all_done = len(miss) == 0 or all((D['parks'].get(p['ref']) or {}).get('read') for p in miss)
    state['areas'][area] = {'status': 'done' if all_done and not late() else 'partial', 'when': TODAY, 'counts': D['counts']}
    save(f, D)
    queue_append(area, D)
    grade_me(area, f, D['counts'])
    notice(f"{area}: {D['counts']} (this chunk {done} parks, {fresh} fresh)")


# ---- outputs for other people / bots
def queue_append(area, D):
    """One row per layer found APPENDED to data/intake/queue.json (de-duplicated by url) for the intake bot."""
    qp = pathlib.Path('data/intake/queue.json') if in_repo(OUT) else OUT / 'intake-queue.json'
    per = {}
    for ref, p in D['parks'].items():
        for x in p.get('finds') or []:
            if x.get('where') == 'PAD-US' or x.get('rel') not in ('name match', 'name mismatch (likely our matcher)'): continue
            row = per.setdefault(x['layer'], {'url': x['layer'], 'area': area, 'title': '', 'publisher': x.get('publisher') or '', 'licence': x.get('licence') or 'terms not read',
                                              'from': 'gap-filler', 'added': TODAY, 'note': '', 'closes': []})
            if ref not in row['closes']: row['closes'].append(ref)
            if x.get('sure') == 'YES': row['title'] = row['title'] or f"{x.get('publisher') or host_of(x['layer'])} polygons ({x.get('field') or 'name'})"
    if not per: return
    Q = load(qp, None) or {'about': 'KPC intake queue: layers to read (one row per url). Rows from the gap filler carry closes: the parks they would close. Review only.', 'rows': []}
    rows = Q.setdefault('rows', [])
    byurl = {r.get('url'): r for r in rows if isinstance(r, dict)}
    for u, row in per.items():
        row['note'] = f"would close {len(row['closes'])} missing park(s) in {area}; sure finds: {sum(1 for r in row['closes'] if (D['parks'].get(r) or {}).get('sure') == 'YES')}"
        if u in byurl:
            old = byurl[u]
            old.setdefault('closes', [])
            for r in row['closes']:
                if r not in old['closes']: old['closes'].append(r)
            if old.get('from') == 'gap-filler': old['note'] = row['note']; old['added'] = old.get('added') or TODAY
        else: rows.append(row); byurl[u] = row
    save(qp, Q)


def grade_me(area, f, counts):
    if not in_repo(OUT) or os.environ.get('NOSTATUS'): return
    try: subprocess.run([sys.executable, '.github/scripts/kpc_status.py', 'grade-me', 'gap filler', area, f'{f} (+ data/gapfill/review.md)', json.dumps(counts)[:200]], timeout=60)
    except Exception as e: notice(f'status line not written: {e}')  # noqa: BLE001


def review(state):
    L = ['# GAP FILLER: leads for the parks with no outline', '', f'Read {TODAY}. REVIEW ONLY: nothing here is in a key. Per area: the layers found, the ones that would close the most parks first; '
         'the name-mismatch list (chat 2 compares both names); how many parks had nothing. "Sure" = pin inside + name words match + similar size when known (house rule); everything else is "check".', '',
         'ℹ️ Maps and park info are a planning aid, not a guarantee. Always check the official agency map and rules before you go.', '']
    for a in GAP_QUEUE:
        D = load(OUT / f'{a}.json', None)
        if not D: continue
        c = D.get('counts') or {}
        L += [f'## {a}: {c.get("missing", 0)} missing · {c.get("sure", 0)} sure · {c.get("padus_match", 0)} PAD-US name match · {c.get("name_mismatch", 0)} name mismatch · {c.get("check", 0)} check · {c.get("different_land", 0)} different land · {c.get("nothing", 0)} nothing (read {D.get("read")})', '']
        per = {}
        for ref, p in D['parks'].items():
            for x in p.get('finds') or []:
                if x.get('where') == 'PAD-US' or x.get('rel') not in ('name match', 'name mismatch (likely our matcher)'): continue
                per.setdefault(x['layer'], {'pub': x.get('publisher') or '', 'lic': x.get('licence') or '', 'parks': []})['parks'].append((ref, p['n'], x.get('poly'), x.get('sure'), x.get('acres'), p.get('a')))
        if per:
            L.append('### Layers found (parks each would close)')
            for lu, v in sorted(per.items(), key=lambda kv: -len(kv[1]['parks'])):
                L.append(f'- {lu} · {v["pub"] or "publisher not read"} · {v["lic"] or "terms not read"} · closes {len(v["parks"])}')
                for ref, n, poly, sure, ac, ours in v['parks'][:40]:
                    L.append(f'  - {ref} {n} ← "{poly}" {ac or "?"} ac (ours {ours or "?"}) · {"SURE" if sure == "YES" else "check"}')
            L.append('')
        mm = [(ref, p) for ref, p in D['parks'].items() if p.get('verdict') == 'mismatch']
        if mm:
            L.append('### Name mismatches for chat 2 (a polygon under the pin shares the park name)')
            for ref, p in mm[:80]:
                x = p.get('find') or {}
                L.append(f'- {ref} {p["n"]} ({p.get("t")}) ← "{x.get("poly")}" in {x.get("layer")}')
            L.append('')
        pad = [(ref, p) for ref, p in D['parks'].items() if p.get('verdict') == 'padus']
        if pad:
            L.append('### PAD-US name matches under the pin (fee / designation record; chat 2 checks manager + type before any use)')
            for ref, p in pad[:60]:
                x = p.get('find') or {}
                L.append(f'- {ref} {p["n"]} ← "{x.get("poly")}" · {x.get("manager")} · {x.get("des")} · {x.get("acres")} ac')
            L.append('')
        no = [ref for ref, p in D['parks'].items() if p.get('verdict') in ('nothing', 'different')]
        if no:
            L.append(f'### No official layer found: {len(no)} parks ({", ".join(no[:30])}{"…" if len(no) > 30 else ""})')
            L.append('')
    (OUT / 'review.md').write_text('\n'.join(L) + '\n', encoding='utf-8')


# ---- selftest (no web)
def selftest():
    ok = True
    pairs = [('Lake Cumberland State Resort Park', 'LAKE CUMBERLAND SRP', 'match'),
             ('Big Bone Lick State Historic Site', 'Big Bone Lick State Park', 'mismatch'),
             ('Jenny Wiley State Resort Park', 'Dewey Lake WMA', 'different'),
             ('Daniel Boone National Forest', 'Red River Gorge Geological Area', 'different'),
             ('Green River Lake State Park', 'Green River State Forest', 'different'),
             ('Taylorsville Lake WMA', 'Taylorsville Lake Wildlife Management Area', 'match')]
    for a, b, want in pairs:
        got = judge_name(a, b); ok &= got == want
        print(f'name: {a!r} vs {b!r} -> {got} ({"ok" if got == want else "WANT " + want})')
    finds = [(True, 'match', True, 'YES'), (True, 'match', None, 'YES'), (True, 'match', False, 'check'), (False, 'match', True, 'check')]
    for pin, rel, size, want in finds:
        got = sure_rule(pin, rel, size); ok &= got == want
        print(f'sure: pin={pin} name={rel} size={size} -> {got} ({"ok" if got == want else "WANT " + want})')
    print(f'similar_size: 722 vs 896 -> {similar_size(722, 896)} · 100 vs 0 -> {similar_size(100, 0)}')
    P = pins()
    for a in ('US-KY', 'US-NV'):
        m = missing_for(a, P); K = load(key_file(a), {}).get('parks') or (ky_key()[0] if a == 'US-KY' else {})
        print(f'missing {a}: {len(m)} of {len(K)} parks in the key (no outline, not pin-only / line) · layers already read: {len(area_layers(a))} · orgs {org_ids(a)} · servers {len(agency_servers(a))}')
        for p in m[:3]: print('   e.g.', p['ref'], p['n'], p['t'], p['la'], p['lo'], 'hosts', agency_hosts(a, p.get('page')))
    print('SELFTEST ' + ('PASS' if ok else 'FAIL'))
    return ok


def main():
    global M
    OUT.mkdir(parents=True, exist_ok=True)
    state = load(OUT / 'state.json', {'areas': {}, 'hosts': {}})
    M = Manners('gap filler (park outline leads)', state.get('hosts'))
    want = (os.environ.get('AREAS') or '').upper().split()
    areas = [a for a in want if a in GAP_QUEUE or key_file(a).exists()] if want else [a for a in GAP_QUEUE if (state['areas'].get(a) or {}).get('status') != 'done']
    if not areas: notice('no area to do'); print('LEFT=0'); save(OUT / 'state.json', state); review(state); return
    P = pins()
    for area in areas:
        if late(): break
        run_area(area, state, P)
    state['hosts'] = M.resting()
    state['last'] = {'when': TODAY, 'areas': areas[:8], 'stat': STAT, 'manners': M.stat}
    if STAT['checked'] and not state.get('proven') and os.environ.get('PROVEN') == '1': state['proven'] = TODAY
    save(OUT / 'state.json', state)
    review(state)
    left = [a for a in GAP_QUEUE if (state['areas'].get(a) or {}).get('status') != 'done']
    print(f'LEFT={len(left)}')
    notice(f"done this chunk: {STAT} · manners {M.stat} · areas left: {len(left)}" + (f" (next {' '.join(left[:4])})" if left else ''))


if __name__ == '__main__':
    if '--selftest' in sys.argv: sys.exit(0 if selftest() else 1)
    try: main()
    except Exception as e:  # noqa: BLE001
        import traceback; traceback.print_exc()
        notice(f'stopped: {e}')
    sys.exit(0)
