#!/usr/bin/env python3
"""PARK DETECTIVE (Fable, chat 10 'bot workshop', Oct 28 2026; grown from the GAP FILLER the same morning). Brandon: 'a bot
dedicated to finding missing park information like Boiling Springs … use the bots when we can; if it and chats 11 and 8 can't
find it, then I look'. LEADS AND ANSWERS ONLY: it never adds anything to a key, an outline or a card. Two jobs:

A. THE GAP FILLER (missing outlines): for every park on the scoreboard with no outline it looks for the official polygon under
   the POTA pin, at most ~8 polite requests, stopping at the first SURE find:
   1 layers we already read for that state / province (one point query at the pin per layer; a polygon whose name shares the
     park's words = 'likely a NAME MISMATCH in our matcher', both names listed for chat 2; another name = 'different land');
   2 the managing agency's own ArcGIS (org search for the park's name, or its ArcGIS Server folder list), then one point query
     per candidate layer (at most 3);
   3 the state open-data portal (ArcGIS Hub search, publishers that read like the state's own agency only);
   4 USGS PAD-US at the pin (reported; Proclamation / Easement records are never offered as an outline);
   5 nothing -> 'no official layer found' + what was tried.
   'Sure' = YES only by the house rule (pin inside + name words match + similar size when both sizes are known), else 'check'.
B. QUESTIONS (data/detective/questions.json; any chat or HQ adds one: {id, ref, park, what, note, added, by}; what = outline ·
   tract · acreage · owner · who runs it · handover · access point · free text). Every official source in ORDER, stopping at
   the first answer: (1) our layers at the pin -> (2) the agency's park page + its PDFs (brochures, management plans,
   land-acquisition reports such as Kentucky's KHLCF annual reports: PDF text read by range, looking for the park's name or the
   question's own words + the fact words: acres, tract, owned by, managed by, transferred, parking, access) -> (3) the state
   open-data portal -> (4) PAD-US at the pin (owner / manager / acres) -> (5) county PVA / parcel sites ONLY where robots.txt and
   the page's own terms allow a bot (never accept terms, never log in; a terms or sign-in wall = 'blocked by terms') -> (6) the
   agency's news releases (data/truth/news-sources.json rows for the area).
   ANSWER = {fact, line (the quoted sentence, <= 240 chars), url, date, step} or 'not found' + tried: [steps + urls].

Output (review material, never a key): data/detective/<area>.json + review.md (the gap filler), data/detective/answers.json +
answers.md (questions: answered first, then 'not found' with what was tried; unanswered -> chats 8 / 11 -> Brandon), one row
per layer found APPENDED to data/intake/queue.json (from: 'gap-filler', closes: [refs]), a 'grade me' line per batch
(kpc_status.py). A park checked within REFRESH_DAYS (30) is skipped; a question is answered once (ask again with a new id).
Manners: kpc_manners.py (robots.txt with the ArcGIS REST exemption, 1 request / 2 s per host, three strikes = a day's rest).
MINUTES per chunk; never fails (exit 0 always). kpc_gapfill_bot.py is a shim that runs this.

Env: AREAS='US-KY US-NV' (blank = the next unfinished areas in GAP_QUEUE order) · MINUTES (55) · LINKS (KPC-Links checkout,
     default 'links') · OUT (data/detective) · REFRESH_DAYS (30) · MAXREQ (8 per park) · QMAX (14 per question) · PARKS (cap per
     area per chunk) · JOBS='questions gaps' (which jobs, in order; default both)
     --selftest = no web: the fact-word extraction (6 sentences), the name-mismatch judgment, the 'sure' rule, the missing-list
     counts for US-KY and US-NV.
"""
import json, os, pathlib, re, subprocess, sys, time, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kpc_manners import Manners, page_text, links_in, pdf_text  # noqa: E402
try: from kpc_truth_bot import QUEUE as TRUTH_QUEUE, STATE_NAMES  # noqa: E402
except Exception:  # noqa: BLE001
    TRUTH_QUEUE, STATE_NAMES = [], {}

REPO = pathlib.Path('.').resolve()
OUT = pathlib.Path(os.environ.get('OUT') or 'data/detective')
QMAX = int(os.environ.get('QMAX') or 14)
INBOX = pathlib.Path('data/detective')   # questions.json + sources.json always live here (OUT may point elsewhere in a test)
PDF_FIRST = 1_500_000   # land-acquisition reports list tracts deep inside: read the first 1.5 MB / 40 pages
LINKS = pathlib.Path(os.environ.get('LINKS') or 'links')
T0 = time.time(); LIMIT = float(os.environ.get('MINUTES') or 55) * 60
REFRESH_DAYS = int(os.environ.get('REFRESH_DAYS') or 30)
MAXREQ = int(os.environ.get('MAXREQ') or 8)
PARK_CAP = int(os.environ.get('PARKS') or 0)
TODAY = time.strftime('%Y-%m-%d')
VER = 2   # Oct 28 (HQ): step-1 polygons are context, the chain of finds is kept, acreage sums the units, report PDFs are followed
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


def notice(m): print('::notice title=Park detective::' + str(m).replace('\n', ' ')[:900], flush=True)
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
    if sb and isinstance(sb.get('parks'), dict):     # chat 2's scoreboard bot (Oct 28): {ref: {n, a, t (index into types), o: miss|pin|line|off|pad|osm, status, near_miss}}
        types = sb.get('types') or []
        for ref, r in sb['parks'].items():
            if not isinstance(r, dict) or r.get('a') != area or r.get('o') not in ('miss', 'missing'): continue
            t = r.get('t'); t = types[t] if isinstance(t, int) and t < len(types) else (t or '')
            v = P.get(ref)
            if not v and area == 'US-KY':
                K, kypin = ky_key(); kp = kypin.get(ref)
                v = (r.get('n'), t, kp[0], kp[1], kp[2], 0) if kp else None
            if not v or v[2] is None or v[3] is None: continue
            out.append({'ref': ref, 'n': r.get('n') or v[0], 't': t or v[1], 'la': v[2], 'lo': v[3], 'a': v[5], 'page': v[4], 'status': r.get('status'), 'near_miss': r.get('near_miss')})
        return out
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
        if budget[0] >= MAXREQ or late(): return None
        budget[0] += 1
    STAT['requests'] += 1
    url = u + ('?' + urllib.parse.urlencode(params) if params else '')
    st, _h, body, _f = M.get(url, timeout=25, accept='application/json,*/*;q=0.5')
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
    qp = pathlib.Path('data/intake/queue.json') if in_repo(OUT) else OUT / 'intake-queue.json'   # at RUN time only, inside the repo
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
    try: subprocess.run([sys.executable, '.github/scripts/kpc_status.py', 'grade-me', 'park detective', area, f'{f} (+ {OUT}/review.md)', json.dumps(counts)[:200]], timeout=60)
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



# ====================================================================================================================
# B. QUESTIONS: the detective proper
# ====================================================================================================================
FACT_RX = {
    'acreage': re.compile(r'\b\d[\d,]*(?:\.\d+)?\s*(?:-\s*)?(?:acres?|ac\b|hectares?|\bha\b)|^[A-Z][^,\n]{3,80},(?:[^,\n]{1,60},){1,4}\s*\d[\d,]*\.\d+\s*$', re.I | re.M),
    'tract': re.compile(r'\b(tracts?|parcels?|acquisitions?|acquired|addition|purchased|purchase of|donated|donation of|conservation fund|khlcf)\b|^[A-Z][^,\n]{3,80},(?:[^,\n]{1,60},){1,4}\s*\d[\d,]*\.\d+\s*$', re.I | re.M),
    'owner': re.compile(r'\b(owned by|owner(?:ship)?|property of|title to|deeded to|belongs to|state-owned|publicly owned|owned and)\b', re.I),
    'who runs it': re.compile(r'\b(managed by|operated by|administered by|maintained by|run by|manages|operates|management of|jointly managed|under the management)\b', re.I),
    'handover': re.compile(r'\b(transferr?ed|transfer of|deeded|conveyed|handed over|turned over|leased to|now managed|now operated|sold to|donated to|ceded|given to|gift(?:ed)? to)\b', re.I),
    'access point': re.compile(r'\b(parking(?: lot| area)?|access(?: point| road| area| site)?|trailhead|boat ramp|launch|entrance|gate|pull-?off|kiosk)\b', re.I),
}
FACT_RX['outline'] = re.compile(r'\b(boundary|boundaries|map|outline|acres?|units?|tracts?)\b', re.I)
FACT_RX['free text'] = re.compile('|'.join(r.pattern for k, r in FACT_RX.items() if k not in ('outline',)), re.I)
DOC_WORDS = re.compile(r'\.pdf\b|brochure|management plan|master plan|annual report|report|acquisition|khlcf|heritage land|tract|land purchase|property|parcel|trail map|park map|boundary|fact sheet|history', re.I)
TERMS_WALL = re.compile(r'(?:i\s+)?(?:agree|accept)\b.{0,80}(?:terms|conditions|disclaimer)|terms (?:of use|and conditions).{0,80}(?:agree|accept|continue)|click (?:here )?to (?:agree|accept|continue)|sign in|log ?in|password|captcha|access denied|subscription required|robots? (?:are )?not (?:allowed|permitted)|automated (?:access|queries) (?:is|are) (?:not permitted|prohibited)', re.I)
SENT_SPLIT = re.compile(r'(?<=[.!?])\s+(?=[A-Z"(])|\n+')
STATQ = {'questions': 0, 'answered': 0, 'partly': 0, 'not_found': 0, 'blocked': 0, 'skipped_done': 0}


def hints_of(note):
    """The question's own words worth matching: Capitalized phrases (Timber Lane), numbers with a decimal (115.75), quoted bits."""
    h = set(re.findall(r'"([^"]{3,60})"', note or ''))
    h |= {m for m in re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b", note or '') if not re.match(r'^(The|This|That|Is|It|Does|Which|What|Where|Who|Brandon|Chat)\b', m)}
    h |= set(re.findall(r'\b\d+\.\d+\b', note or ''))
    return {x.strip().lower() for x in h if x.strip()}


def kinds_of(sentence):
    """Which fact kinds a sentence carries (selftested)."""
    return {k for k, rx in FACT_RX.items() if k not in ('outline', 'free text') and rx.search(sentence)}


def facts_in(text, name, hints, what, limit=6):
    """Sentences of a page that name the park (or the question's own words) AND carry the fact words asked for.
    -> [(line <= 240 chars, kinds)] best first (hint matches first, then the ones with a number)."""
    cw = core_words(name); need = max(1, min(2, len(cw)))
    out = []
    for sen in SENT_SPLIT.split(text or ''):
        s = ' '.join(sen.split())
        if len(s) < 12: continue
        sl = s.lower()
        hit_h = any(h in sl for h in hints)
        hit_n = sum(1 for w in cw if re.search(r'\b' + re.escape(w) + r'\b', sl)) >= need
        if not (hit_h or hit_n): continue
        ks = kinds_of(s)
        want = ks if what in ('free text', 'outline') else ks & ({what} | ({'acreage'} if what == 'tract' else set()))
        if what == 'outline' and not FACT_RX['outline'].search(s): continue
        if what != 'outline' and not want: continue
        if what == 'tract' and 'tract' not in ks and not hit_h: continue
        line = s if len(s) <= 240 else s[:237] + '…'
        out.append((line, sorted(want or ks), 2 * hit_h + (1 if re.search(r'\d', s) else 0)))
    out.sort(key=lambda x: -x[2])
    return [(a, b) for a, b, _ in out[:limit]]


def read_html(u, budget):
    """Like read_doc but also returns the raw HTML for link picking: (status, text, html)."""
    if budget[0] >= QMAX or late(): return 'budget', '', ''
    budget[0] += 1; STAT['requests'] += 1
    st, hd, body, _f = M.get(u, timeout=25)
    if st not in (200, 206): return (str(st) if not isinstance(st, int) else f'HTTP {st}'), '', ''
    budget[1] += 1
    if body[:5] == b'%PDF-': return 'ok', pdf_text(body, 40), ''
    html = body.decode('utf-8', 'replace')
    return 'ok', page_text(html), html


def park_of(ref, P):
    """(name, type, la, lo, page, county, off) for a ref: Kentucky's hand data first, then parkinfo."""
    for x in load(LINKS / 'kpc-ky-data.json', {}).get('parks', []):
        if x.get('c') == ref: return (x.get('n'), x.get('t'), x.get('la'), x.get('lo'), x.get('web') or '', x.get('co') or '', x.get('off') or '')
    v = P.get(ref)
    if v: return (v[0], v[1], v[2], v[3], v[4], '', '')
    return None


def pick_links(html, base, name, hints, n=4):
    """Document links on a page worth reading for a question: PDFs / plans / reports whose text or url carries a document word,
    the ones that name the park or the question's own words first, newer years first."""
    rows = []
    for u, t in links_in(html, base):
        blob = (t + ' ' + u).lower()
        if not DOC_WORDS.search(blob): continue
        if re.search(r'facebook|twitter|youtube|instagram|mailto|\.(jpg|png|gif|zip|kmz|xlsx?)$', blob): continue
        score = 3 * any(h in blob for h in hints) + 2 * any(w in blob for w in core_words(name)) + (1 if '.pdf' in blob else 0)
        yr = re.findall(r'20[12]\d', blob); score += (int(yr[-1]) - 2000) / 100 if yr else 0
        rows.append((score, u, t))
    rows.sort(key=lambda r: -r[0]); seen = set(); out = []
    for _s, u, t in rows:
        if u in seen: continue
        seen.add(u); out.append((u, t))
        if len(out) >= n: break
    return out


def sources_for(area):
    """data/detective/sources.json rows for the area: {reports: [index pages of land-acquisition / plan documents], parcels: [county parcel sites]}."""
    S = load(INBOX / 'sources.json', {}) or load(OUT / 'sources.json', {}) or {}
    return ([r for r in S.get('reports') or [] if r.get('area') == area], [r for r in S.get('parcels') or [] if r.get('area') == area])


def answer_from(lines, url, step, kind_hint=''):
    line, kinds = lines[0]
    return {'fact': (kind_hint or ', '.join(kinds)) + ': ' + line[:160], 'line': line, 'url': url, 'date': TODAY, 'step': step}


# V2 (Oct 28, HQ after the first Kentucky run answered the Boiling Springs questions with the Rush Island polygon): a step-1 polygon
# is CONTEXT, never the answer, for tract / acreage / owner / who runs it / handover / access point questions, unless its name
# holds the asked tract name or the question is 'outline'. The hunt goes on through steps 2-6; every find is kept (the chain);
# ANSWERED only when a find matches the question's fact words, else PARTLY (context only) + what was tried.
CONTEXT_KINDS = ('tract', 'acreage', 'owner', 'who runs it', 'handover', 'access point')
NEAR_M = 2000
REPORT_LINK = re.compile(r'annual report|20(1[5-9]|[2-9]\d)', re.I)


def answers_question(find, what, hints):
    """Does a find ANSWER the question (its line carries the fact words asked, or the asked tract name)? Selftested."""
    line = (find.get('line') or '').lower()
    if not line: return False
    if what == 'outline': return True
    if what == 'free text': return bool(kinds_of(line))
    if hints and any(h in line for h in hints if len(h) > 3 and not re.fullmatch(r'[\d.]+', h)): return True   # the asked tract name
    ks = kinds_of(line)
    if what == 'tract': return 'tract' in ks and ('acreage' in ks or bool(re.search(r'\d', line)))
    return what in ks


def layer_context(name, hints, what, la, lo, area, budget, tried, finds):
    """Step 1: the polygons with the park's name under the pin (and, for acreage, within NEAR_M) in every layer we read.
    Each is a context find; an 'outline' question or a polygon that names the asked tract is an answer."""
    for lu, nf, label in area_layers(area)[:4]:
        if budget[0] >= 5: break
        tried.append({'step': 1, 'url': lu, 'what': 'point query at the pin' + (f' + within {NEAR_M} m' if what == 'acreage' else '')})
        if what == 'acreage':
            j = J(lu + '/query', {'geometry': f'{lo},{la}', 'geometryType': 'esriGeometryPoint', 'inSR': 4326, 'spatialRel': 'esriSpatialRelIntersects', 'distance': NEAR_M, 'units': 'esriSRUnit_Meter',
                                  'outFields': '*', 'returnGeometry': 'false', 'f': 'json'}, budget)
            hits = [f.get('attributes') or {} for f in (j or {}).get('features') or []] if j else None
        else: hits = point_query(lu, la, lo, budget)
        for a in hits or []:
            pname = str(a.get(name_field(a, nf)) or '')
            named = judge_name(name, pname) in ('match', 'mismatch')
            tract_hit = any(h in pname.lower() for h in hints if len(h) > 3 and not re.fullmatch(r'[\d.]+', h))
            if not (named or tract_hit): continue
            line = '; '.join(f'{k}={v}' for k, v in a.items() if isinstance(v, (str, int, float)) and str(v).strip() and not re.search(r'objectid|shape|globalid', k, re.I))[:240]
            finds.append({'step': '1 our layers', 'role': 'answer' if (what == 'outline' or tract_hit) else 'context', 'fact': f'polygon {"under the pin" if what != "acreage" else "under or near the pin"} in a layer we read: "{pname}"' + (f', {acres_of(a)} ac' if acres_of(a) else ''),
                          'line': line, 'url': lu, 'date': TODAY, 'poly': pname, 'acres': acres_of(a)})


def follow_reports(url, html, name, hints, what, budget, tried, finds, done):
    """Step 2 (V2): from a report index page follow the PDF links whose text has a year >= 2015 or 'annual report' (<= 6, by range,
    first 400 KB) and search the park / tract words."""
    n = 0
    for u, t in links_in(html, url):
        if n >= 6 or budget[0] >= QMAX - 3 or late(): break
        blob = (t + ' ' + u)
        if '.pdf' not in u.lower() or not REPORT_LINK.search(blob) or u in done: continue
        done.add(u); n += 1
        tried.append({'step': 2, 'url': u, 'what': 'report PDF: ' + (t or '')[:60]})
        if budget[0] >= QMAX: break
        budget[0] += 1; STAT['requests'] += 1
        st, hd, body, _f = M.get(u, rng=(0, 400_000 - 1), timeout=30)
        if st not in (200, 206) or body[:5] != b'%PDF-': tried[-1]['result'] = str(st); continue
        budget[1] += 1
        L = facts_in(pdf_text(body, 40), name, hints, what)
        if L:
            for line, kinds in L[:3]:
                f = {'step': '2 agency documents', 'fact': ', '.join(kinds) + ': ' + line[:160], 'line': line, 'url': u, 'date': TODAY}
                f['role'] = 'answer' if answers_question(f, what, hints) else 'context'
                finds.append(f)
            if any(f.get('role') == 'answer' for f in finds): return True
    return False


def add_facts(L, url, step, what, hints, finds):
    """Page facts -> finds (answer or context). Returns True when an answer landed."""
    hit = False
    for line, kinds in L[:3]:
        f = {'step': step, 'fact': ', '.join(kinds) + ': ' + line[:160], 'line': line, 'url': url, 'date': TODAY}
        f['role'] = 'answer' if answers_question(f, what, hints) else 'context'
        hit |= f['role'] == 'answer'
        finds.append(f)
    return hit


def hunt_question(q, P, area):
    """The six steps for one question, every find kept (the chain). -> {'finds', 'answer' (the first answering find) or None,
    'result': ANSWERED | PARTLY | NOT FOUND, 'tried', 'blocked', 'units' (acreage questions)}."""
    ref, what, note = q.get('ref') or '', (q.get('what') or 'free text').lower(), q.get('note') or ''
    pk = park_of(ref, P)
    name = q.get('park') or (pk[0] if pk else '')
    hints = hints_of(note) | hints_of(q.get('park') or '')
    tried = []; budget = [0, 0]; blocked = []; finds = []; done = set()
    if not pk and not name: return {'result': 'NOT FOUND', 'not found': 'park unknown: no pin or page for this reference', 'tried': [], 'finds': []}
    la, lo, page, county, off = (pk[2], pk[3], pk[4], pk[5], pk[6]) if pk else (None, None, '', '', '')
    answered = lambda: any(f.get('role') == 'answer' for f in finds)  # noqa: E731
    # 1 our layers at the pin (context for most kinds)
    if la is not None and what in ('outline', 'free text') + CONTEXT_KINDS:
        layer_context(name, hints, what, la, lo, area, budget, tried, finds)
    # 2 the agency's park page + its documents + the report index pages
    if not answered():
        docs = []
        if page:
            tried.append({'step': 2, 'url': page, 'what': 'agency park page'})
            st, text, html = read_html(page, budget)
            if st == 'ok':
                add_facts(facts_in(text, name, hints, what), page, '2 agency page', what, hints, finds)
                if what == 'acreage':   # the page's own size sentence is kept even when the first find already answered
                    for line, kinds in facts_in(text, name, hints, 'acreage')[:1]:
                        if not any(f.get('line') == line for f in finds): finds.append({'step': '2 agency page', 'role': 'context', 'fact': 'agency page size: ' + line[:160], 'line': line, 'url': page, 'date': TODAY})
                docs += pick_links(html, page, name, hints, 3)
            else: tried[-1]['result'] = st
        if off and off.lower().split('?')[0].endswith('.pdf'): docs.insert(0, (off, 'official map'))
        for r in sources_for(area)[0]:
            if answered() or budget[0] >= QMAX - 3: break
            tried.append({'step': 2, 'url': r['url'], 'what': r.get('kind') or 'report index'})
            st, text, html = read_html(r['url'], budget)
            if st != 'ok': tried[-1]['result'] = st; continue
            add_facts(facts_in(text, name, hints, what), r['url'], '2 agency documents', what, hints, finds)
            if not answered() and html: follow_reports(r['url'], html, name, hints, what, budget, tried, finds, done)
            if not answered(): docs += pick_links(html, r['url'], name, hints, 2)
        for u, t in docs:
            if answered() or u in done or budget[0] >= QMAX - 3: continue
            done.add(u); tried.append({'step': 2, 'url': u, 'what': 'document: ' + (t or '')[:60]})
            st, text, _h = read_html(u, budget)
            if st != 'ok': tried[-1]['result'] = st; continue
            add_facts(facts_in(text, name, hints, what), u, '2 agency documents', what, hints, finds)
    # 3 the state open-data portal
    if not answered() and budget[0] < QMAX - 2:
        sn = STATE_NAMES.get(area[3:], '')
        qn = ' '.join(sorted(core_words(name)))[:60]
        tried.append({'step': 3, 'url': 'https://hub.arcgis.com/api/v3/datasets?q=' + urllib.parse.quote(f'{qn} {sn}'), 'what': 'open-data search'})
        j = J('https://hub.arcgis.com/api/v3/datasets', {'q': f'{qn} {sn}'.strip(), 'page[size]': 6, 'f': 'json'}, budget)
        for d in (j or {}).get('data') or []:
            at = d.get('attributes') or {}
            title = at.get('name') or ''
            if judge_name(name, title) in ('match', 'mismatch') and official_org(at.get('orgName') or at.get('source') or '', area):
                f = {'step': '3 open-data portal', 'fact': f'open-data dataset names the park: "{title}" ({at.get("orgName") or at.get("source")})', 'line': (at.get('description') or '')[:240], 'url': at.get('url') or '', 'date': TODAY}
                f['role'] = 'answer' if what == 'outline' or answers_question(f, what, hints) else 'context'
                finds.append(f); break
    # 4 PAD-US at the pin
    if not answered() and la is not None and budget[0] < QMAX - 1 and what in ('outline', 'free text') + CONTEXT_KINDS:
        tried.append({'step': 4, 'url': PADUS, 'what': 'PAD-US point query'})
        j = J(PADUS + '/query', {'geometry': f'{lo},{la}', 'geometryType': 'esriGeometryPoint', 'inSR': 4326, 'spatialRel': 'esriSpatialRelIntersects', 'outFields': '*', 'returnGeometry': 'false', 'f': 'json'}, budget)
        for ft in (j or {}).get('features') or []:
            a = ft.get('attributes') or {}
            if PAD_NEVER.search(str(a.get('Category') or '') + ' ' + str(a.get('Des_Tp') or '')): continue
            line = f"Unit_Nm={a.get('Unit_Nm')}; Mang_Name={a.get('Mang_Name')}; Own_Name={a.get('Own_Name')}; Own_Type={a.get('Own_Type')}; Des_Tp={a.get('Des_Tp')}; GIS_Acres={a.get('GIS_Acres')}; Category={a.get('Category')}"[:240]
            role = 'answer' if what in ('owner', 'who runs it') and judge_name(name, str(a.get('Unit_Nm') or '')) in ('match', 'mismatch') else 'context'
            finds.append({'step': '4 PAD-US', 'role': role, 'fact': f'PAD-US record under the pin: "{a.get("Unit_Nm")}" managed by {a.get("Mang_Name")}, owner {a.get("Own_Name")}, {round(float(a.get("GIS_Acres") or 0))} acres', 'line': line, 'url': PADUS, 'date': TODAY})
    # 5 county parcel sites, only where allowed
    for r in sources_for(area)[1]:
        if answered() or budget[0] >= QMAX - 1: break
        if county and r.get('county') and low(r['county']) != low(county): continue
        u = r['url']
        tried.append({'step': 5, 'url': u, 'what': 'parcel site (robots + terms checked)'})
        st, text, _h = read_html(u, budget)
        if st == 'robots': blocked.append(u); tried[-1]['result'] = 'blocked by robots.txt'; continue
        if st != 'ok': tried[-1]['result'] = st; continue
        if TERMS_WALL.search(text[:6000]): blocked.append(u); tried[-1]['result'] = 'blocked by terms'; continue
        add_facts(facts_in(text, name, hints, what if what != 'tract' else 'free text'), u, '5 parcel site', what, hints, finds)
    # 6 the agency's news releases
    for r in (load('data/truth/news-sources.json', {}).get('sources') or []):
        if answered() or r.get('area') != area or budget[0] >= QMAX: continue
        tried.append({'step': 6, 'url': r['url'], 'what': 'news releases'})
        st, text, _h = read_html(r['url'], budget)
        if st != 'ok': tried[-1]['result'] = st; continue
        add_facts(facts_in(text, name, hints, what if what != 'tract' else 'free text'), r['url'], '6 news releases', what, hints, finds)
    res = {'finds': finds, 'tried': tried, 'answer': next((f for f in finds if f.get('role') == 'answer'), None)}
    if what == 'acreage':   # every polygon with the park's name under / near the pin, their acres and the sum, vs the agency's sentence
        polys = [f for f in finds if f.get('step') == '1 our layers']
        agency = next((f['line'] for f in finds if f.get('step') == '2 agency page' and 'acre' in f.get('line', '').lower()), '')
        tot = sum(f.get('acres') or 0 for f in polys)
        res['units'] = {'pieces': [(f.get('poly'), f.get('acres')) for f in polys], 'our_acres': tot, 'agency_line': agency,
                        'summary': f'our outline holds {tot} ac in {len(polys)} piece(s)' + (f' vs the agency\'s "{agency[:120]}"' if agency else ' vs the agency: no size sentence found')}
    res['result'] = 'ANSWERED' if res['answer'] else ('PARTLY' if finds else 'NOT FOUND')
    if res['result'] != 'ANSWERED':
        res['not found'] = ('context only: ' if finds else 'no official source answered; ') + 'tried steps ' + ', '.join(sorted({str(t['step']) for t in tried}))
    if blocked: res['blocked'] = blocked
    if budget[0] and not budget[1]: res['retry'] = True; res['result'] = 'NOT FOUND'; res['not found'] = 'no host answered this run (rested or errors): tried again next run'
    return res


def run_questions(state, P, only_areas=None):
    Q = load(INBOX / 'questions.json', {}) or load(OUT / 'questions.json', {}) or {}
    qs = Q.get('questions') or []
    if not qs: return
    A = load(OUT / 'answers.json', None) or {'about': 'PARK DETECTIVE answers (review only, never a key): per question id the answer (fact, quoted line, url, date read, source step) or not found + what was tried. Unanswered -> chats 8 / 11 -> Brandon.', 'answers': {}}
    done = 0
    for q in qs:
        if late(): break
        qid = str(q.get('id') or f"{q.get('ref')}-{q.get('what')}")
        old = A['answers'].get(qid)
        if old and not old.get('retry') and old.get('ver') == VER: STATQ['skipped_done'] += 1; continue   # a new VER asks every question again
        ref = q.get('ref') or ''
        area = q.get('area') or ('US-KY' if any(x.get('c') == ref for x in load(LINKS / 'kpc-ky-data.json', {}).get('parks', [])) else '')
        if not area:
            for f in list(pathlib.Path('data/us-key').glob('US-*.json')) + list(pathlib.Path('data/ca-key').glob('CA-*.json')):
                if ref in (load(f, {}).get('parks') or {}): area = f.stem; break
        if only_areas and area not in only_areas: continue
        r = hunt_question(q, P, area or 'US-KY')
        r.update({'id': qid, 'ref': ref, 'park': q.get('park') or (park_of(ref, P) or [''])[0], 'what': q.get('what'), 'note': q.get('note'), 'by': q.get('by'), 'area': area, 'read': TODAY, 'ver': VER})
        A['answers'][qid] = r
        done += 1; STATQ['questions'] += 1
        STATQ[{'ANSWERED': 'answered', 'PARTLY': 'partly', 'NOT FOUND': 'not_found'}[r['result']]] += 1
        if r.get('blocked'): STATQ['blocked'] += 1
    if done:
        save(OUT / 'answers.json', A)
        answers_md(A)
        if in_repo(OUT) and not os.environ.get('NOSTATUS'):
            try: subprocess.run([sys.executable, '.github/scripts/kpc_status.py', 'grade-me', 'park detective', 'questions', f'{OUT}/answers.md', json.dumps(STATQ)[:200]], timeout=60)
            except Exception as e: notice(f'status line not written: {e}')  # noqa: BLE001
    state['questions'] = {'when': TODAY, 'stat': STATQ, 'open': sum(1 for v in A['answers'].values() if not v.get('answer'))}
    notice(f'questions: {STATQ}')


def answers_md(A):
    L = ['# PARK DETECTIVE: answers', '', f'Read {TODAY}. REVIEW ONLY: nothing here is in a key. ANSWERED first (a find matches the question\'s own fact words), then PARTLY '
         '(context only: polygons under the pin, PAD-US, a size sentence, but not the thing asked), then NOT FOUND with what was tried. Partly and not found go to chats 8 / 11, then Brandon. '
         'Every step\'s find is listed so the chain can be followed; a quoted line is the source\'s own words; check the link before any use.', '',
         'ℹ️ Maps and park info are a planning aid, not a guarantee. Always check the official agency map and rules before you go.', '']
    order = {'ANSWERED': 0, 'PARTLY': 1, 'NOT FOUND': 2}
    for v in sorted(A['answers'].values(), key=lambda v: (order.get(v.get('result') or ('ANSWERED' if v.get('answer') else 'NOT FOUND'), 2), v.get('ref') or '')):
        res = v.get('result') or ('ANSWERED' if v.get('answer') else 'NOT FOUND')
        a = v.get('answer') or {}
        L.append(f'## {v["id"]}: {v.get("ref")} {v.get("park")} · {v.get("what")} · {res}' + (f' (step {a.get("step")})' if a else ''))
        if v.get('note'): L.append(f'- asked: {v["note"]} ({v.get("by")})')
        if a: L += [f'- **{a.get("fact")}**', f'- "{a.get("line")}"', f'- {a.get("url")} (read {a.get("date")})']
        if v.get('not found'): L.append(f'- {v["not found"]}')
        u = v.get('units')
        if u: L.append(f'- units: {u.get("summary")}' + (f' · pieces: {", ".join(f"{p} {ac or "?"} ac" for p, ac in u.get("pieces") or [])}' if u.get('pieces') else ''))
        chain = [f for f in v.get('finds') or [] if f is not a]
        if chain:
            L.append('- the chain:')
            for f in chain[:10]: L.append(f'  - step {f.get("step")} ({f.get("role")}): {f.get("fact")} · "{(f.get("line") or "")[:160]}" · {f.get("url")}')
        if res != 'ANSWERED':
            for t in v.get('tried') or []: L.append(f'  - tried step {t.get("step")}: {t.get("what")} {t.get("url")}' + (f' → {t["result"]}' if t.get('result') else ''))
        if v.get('blocked'): L.append(f'- blocked by terms / robots: {", ".join(v["blocked"])}')
        L.append('')
    (OUT / 'answers.md').write_text('\n'.join(L) + '\n', encoding='utf-8')


def selftest_facts():
    ok = True
    cases = [('Boiling Springs State Nature Preserve covers 440 acres in Hart County.', 'acreage'),
             ('The preserve is owned by the Commonwealth of Kentucky and protects a rare spring.', 'owner'),
             ('In 2019 the property was transferred to the Office of Kentucky Nature Preserves.', 'handover'),
             ('A small gravel parking area at the end of the county road gives access to the preserve.', 'access point'),
             ('Green River State Natural Area, Timber Lane, KNP, Hart, 115.75', 'tract'),
             ('The weather was fine and the volunteers enjoyed the day.', 'nothing')]
    for s, want in cases:
        ks = kinds_of(s)
        got = want in ks if want != 'nothing' else not ks
        ok &= got
        print(f'facts: {want:12} {"ok" if got else "MISSED"} {sorted(ks)} ← {s[:60]}')
    hints = hints_of('the KHLCF Timber Lane 115.75-acre tract: is it part of the preserve?')
    L = facts_in('\n'.join(s for s, _ in cases), 'Boiling Springs State Nature Preserve', hints, 'tract')
    got = bool(L) and 'timber lane' in L[0][0].lower(); ok &= got
    print(f'hints {sorted(hints)} → tract question picks: {L[0][0] if L else None} ({"ok" if got else "MISSED"})')
    rush = {'line': 'NAME=Green River State Natural Area (Rush Island Bottoms); ACRES=139.25; MANAGER=KNP'}
    timber = {'line': 'Green River State Natural Area, Timber Lane, KNP, Hart, 115.75'}
    page = {'line': 'Boiling Springs State Nature Preserve covers 440 acres in Hart County.'}
    for f, what, want in ((rush, 'tract', False), (timber, 'tract', True), (rush, 'acreage', False), (page, 'acreage', True), (rush, 'outline', True), (page, 'owner', False)):
        got = answers_question(f, what, hints); ok &= got == want
        print(f'answers? {what:8} {"ok" if got == want else "WRONG"} ({got}) ← {f["line"][:50]}')
    return ok


# ---- selftest (no web)
def selftest():
    ok = True
    ok &= selftest_facts()
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
    if not areas and not (load(INBOX / 'questions.json', {}) or load(OUT / 'questions.json', {})).get('questions'): notice('no area or question to do'); print('LEFT=0'); save(OUT / 'state.json', state); review(state); return
    P = pins()
    jobs = (os.environ.get('JOBS') or 'questions gaps').split()
    if 'questions' in jobs: run_questions(state, P, areas if want else None)
    if 'gaps' in jobs:
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
