#!/usr/bin/env python3
"""LAYER INTAKE LINE (Fable, chat 10 'bot workshop', Oct 28 2026; HQ item B: chat 9's assembly line). ONE polite bot that takes
every map-layer LEAD anyone finds (the world harvester, the discovery bot, the gap-filler, chat 8, chat 9) from one queue
(data/intake/queue.json) and answers, per lead, the five questions a person would have to look up by hand before we read it:

  1 PROBE      what is it? An ArcGIS REST layer (fields, polygons or not, a name field, how many records, last edit, its item
               id), a service (then each polygon layer becomes its own row), a WFS (title + feature types), or a FILE (.zip /
               .geojson / .gdb: HEAD only, size + date, 'needs a download'; this bot never downloads).
  2 TERMS      what does the PUBLISHER'S OWN item page say we may do with it (the Nevada lesson: read the terms where the
               agency wrote them, not where a catalog copied them): the ArcGIS Online item's licenseInfo / accessInformation,
               else the service's copyrightText / description. Classified: OPEN (a named open licence) · CREDIT (copyright or
               credit or disclaimer line with NO use limits = usable with the credit line; HQ Oct 27) · NON-COMMERCIAL (fine
               for a club, with the credit) · LIVE-ONLY (no redistribution / display only / may not be stored: read live,
               never stored) · NOTHING STATED (ask the publisher) · CLOSED (internal, sign-in, by request only).
  3 PUBLISHER  is it the agency itself (government words in owner / org / credit / host, FED_ORG, countries.json trusted
               organisations, .gov / .gc.ca / provincial hosts), unsure, or not official (a consultant, a hobby account, a
               university hosting for an agency = 'hosted for an agency: ask').
  4 OVERLAP    do we already read this layer (same host + service path as data/us-key/layers.json, data/ca-key/layers.json or
               KPC-Links data/state-gis.json) → 'already read as <id>'; same host, another service → 'same publisher as <id>'.
  5 CLOSES     which of the area's parks WITHOUT an outline have their POTA pin inside one of its polygons (up to 60 point
               queries, attributes only), the polygon's name, and whether the name words match the park's name.
  VERDICT      READY (official + OPEN / CREDIT / NON-COMMERCIAL + polygons + a name field + closes >= 1 park, or a chat 8 / 9
               request) · LIVE-ONLY · ASK-THE-PUBLISHER (official + nothing stated, or hosted for an agency) · REJECT (not
               official, no polygons, no name field, already read, closed terms), each with a one-sentence WHY and every
               measured fact. A row with 'expect' (a known answer) also gets test: ok / MISS.

Nothing here decides anything for members and nothing is stored but metadata and counts (never geometry). Chat 9 reads
data/intake/review.md, sets approved: true on the rows it wants in data/intake/ready.json, and the nightly key rebuild reads
approved rows later. Manners: kpc_manners.py (robots obeyed with the ArcGIS REST API path exemption, 1 request / 2 s per
host, back-off, three strikes = a day's rest). About 70 requests per row at most. A row probed within 30 days is skipped
unless its queue row changed (url, title, publisher, licence or note). MINUTES per chunk; never fails (exit 0 always).

Env: ROWS='url url' (blank = every unprobed queue row) · MINUTES (55) · LINKS (KPC-Links checkout, default 'links') ·
     OUT (data/intake) · REFRESH_DAYS (30) · TEST=1 (print the test table + GATE line) · --selftest (no web: the terms
     classifier, the verdict logic, the name-field guess).
"""
import json, math, os, pathlib, re, sys, time, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kpc_manners import Manners  # noqa: E402

OUT = pathlib.Path(os.environ.get('OUT') or 'data/intake')
QUEUE_FILE = pathlib.Path(os.environ.get('QUEUE') or 'data/intake/queue.json')
LINKS = pathlib.Path(os.environ.get('LINKS') or 'links')
T0 = time.time(); LIMIT = float(os.environ.get('MINUTES') or 55) * 60
REFRESH_DAYS = int(os.environ.get('REFRESH_DAYS') or 30)
TEST = os.environ.get('TEST') == '1'
TODAY = time.strftime('%Y-%m-%d')
VER = 1
MAX_REQ = 70          # polite requests per row
MAX_POINTS = 60       # missing parks tested per layer
MAX_LAYERS = 8        # polygon layers taken from one service url
M = None
STAT = {'rows': 0, 'probed': 0, 'skipped_fresh': 0, 'ready': 0, 'water_only': 0, 'live_only': 0, 'ask': 0, 'reject': 0, 'did_not_open': 0, 'tests_ok': 0, 'tests_miss': 0}

# ---- words
KINDW = re.compile(r'\b(state|national|provincial|park|parks|forest|wildlife|management|area|areas|recreation|recreational|conservation|nature|natural|preserve|reserve|refuge|historic|historical|site|game|land|lands|wma|sp|sra|sf|nwr|trail|the|of|and|at|county|city|regional|unit|access|public|fishing|lake|hunting|outdoor|memorial|monument|wilderness|road)\b')
FED_ORG = re.compile(r'bureau of land management|\bblm\b|forest service|\busfs\b|national park service|\bnps\b|fish (?:and|&) wildlife service|'
                     r'\busfws\b|army corps of engineers|\busace\b|u\.?s\.? geological survey|\busgs\b|bureau of reclamation|natural resources canada|'
                     r'parks canada|environment and climate change canada|statistics canada|government of (?:canada|alberta|british columbia|ontario|'
                     r'quebec|manitoba|saskatchewan|nova scotia|new brunswick|newfoundland|prince edward island|yukon|northwest territories|nunavut)', re.I)
GOV_WORDS = re.compile(r'\b(department|dept\.?|division|bureau|agency|commission|ministry|minist[eè]re|ministerio|ministerium|ministero|office of|'
                       r'state of|commonwealth of|province of|government|gouvernement|gobierno|governo|regierung|state parks?|parks (?:and|&) (?:recreation|wildlife)|'
                       r'fish (?:and|&) (?:wildlife|game)|natural resources|conservation|environmental protection|forestry|forest service|land management|'
                       r'national park service|parks canada|natural england|naturescot|natural resources wales|defra|environment agency|'
                       r'county|city of|town of|parish|district|authority|tribe|nation|first nation|'
                       r'dnr|dnrec|dcnr|dec|dep|fwp|fwc|tpwd|twra|ndow|odfw|wdfw|idfg|cdfw|agfc|kdwp|cpw|wgfd|mdc|odnr|idnr|wdnr|dwr|usace|aopk|npu|chko)\b', re.I)
NOT_OFFICIAL = re.compile(r'\b(university|college|school|institute|consult\w*|llc|inc\.?|ltd\.?|gmbh|corp\w*|company|associates|solutions|'
                          r'hobby|personal|my ?maps?|student|class project|test account|demo|sandbox|volunteer|enthusiast|club|society|foundation|trust|'
                          r'conservancy|audubon|nonprofit|non-profit|esri|geospatial services)\b', re.I)
UNIVERSITY = re.compile(r'\b(university|college|\.edu\b|clemson|institute of technology)\b', re.I)
GOV_HOST = re.compile(r'\.(gov|gc\.ca|gov\.uk|gouv\.fr|gob\.es|gov\.au|govt\.nz|go\.jp|gov\.br|gob\.mx|bund\.de|gv\.at|admin\.ch|mil)$|'
                      r'\.(state|us)\.[a-z]{2}\.us$|\.[a-z]{2}\.us$|\.(ca|on|qc|bc|ab|sk|mb|ns|nb|nl|pe|yt|nt|nu)\.ca$|gov\.[a-z]{2}\.ca$|'
                      r'\.(alberta|ontario|gov\.bc|gnb|novascotia|princeedwardisland|gov\.nl|gov\.sk|gov\.mb|gov\.yk|gov\.nt|gov\.nu)\.ca$|'
                      r'(^|\.)(nature\.cz|mzp\.cz|cuzk\.cz|gov\.pl|gov\.si|gov\.sk|gov\.hu|gov\.ro|gov\.lt|gov\.lv|gov\.ee|gov\.ie|gov\.pt|gov\.it|'
                      r'gov\.gr|gov\.hr|gov\.rs|gov\.za|gov\.in|gov\.ar|gov\.cl|gov\.co|gob\.pe|gov\.tr|gov\.il|gov\.kr|gov\.tw|gov\.sg|gov\.my|gov\.ph)$', re.I)

OPEN_RX = re.compile(r'open government licen[cs]e|\bOGL\b|creative commons|\bCC[- ]?BY\b|\bCC0\b|\bCC-BY|public domain|licence ouverte|open data commons|'
                     r'\bODbL\b|\bODC\b|datenlizenz deutschland|no restrictions? on (?:use|access)|free(?:ly)? (?:available|to use)|open data|'
                     r'no (?:use )?(?:limitations?|restrictions)|publicly available|unrestricted', re.I)
LIVE_RX = re.compile(r'no(?:t for)? redistribut\w*|may not be (?:re)?distributed|not (?:to )?be (?:re)?distributed|display (?:purposes )?only|'
                     r'view(?:ing)? (?:purposes )?only|for viewing only|may not be (?:stored|downloaded|copied|saved)|not (?:to )?be (?:stored|downloaded|copied)|'
                     r'do not (?:store|download|copy|cache)|no (?:bulk )?download|pouze (?:k |pro )?prohl[ií][žz]en[ií]|pro prohl[ií][žz]en[ií]|zobrazen[ií] pouze|live (?:access|use) only|'
                     r'cannot be (?:re)?distributed|not permitted to (?:re)?distribute', re.I)
CLOSED_RX = re.compile(r'internal (?:use )?only|not for public (?:use|release|distribution)|for official use only|\bFOUO\b|login required|sign[- ]in required|'
                       r'requires? (?:a )?(?:login|sign[- ]in|authentication|credentials)|by request only|available (?:up)?on request only|restricted (?:access|data|use)|'
                       r'confidential|authorized users? only|not (?:to be )?released|do not (?:share|distribute) (?:outside|externally)|private', re.I)
NONCOM_RX = re.compile(r'non[- ]?commercial|not (?:for|to be used for) commercial|no commercial use|commercial use (?:is )?(?:prohibited|not (?:permitted|allowed))|'
                       r'cc[- ]?by[- ]?nc|educational (?:use|purposes) only|personal (?:use|purposes) only', re.I)
CREDIT_RX = re.compile(r'copyright|\(c\)|©|all rights reserved|credit|courtesy|acknowledg\w*|attribut\w*|cite|citation|source:|disclaimer|'
                       r'no warrant\w*|as[- ]is|not (?:be )?(?:liable|responsible)|without warranty|accuracy|intended for|provided by|produced by|'
                       r'prepared by|compiled by|developed by|maintained by|data from|property of|liability', re.I)
PIN_ONLY_KINDS = re.compile(r'trail|river|byway|airstrip|hatchery|rec(?:reation)? site|roadside|boat (?:ramp|launch|access)|fishing (?:access|pier|lake)|'
                            r'scenic (?:drive|overlook)|lighthouse|dam\b|marina|harbor|harbour|campground|picnic|memorial\b|monument\b(?! valley)', re.I)
POLY = re.compile(r'polygon', re.I)
# Oct 28 (chat 9's review of run 1): a copyrightText credit line is NOT proof of open terms when the agency states its terms
# elsewhere. host or org-id fragment → (class, note a person sees). Chat 8 keeps the sources (OFFICIAL_MAPS/WORLD/<CC>_desk.md).
KNOWN_TERMS = [
    (r'gis\.nature\.cz|aopk', 'LIVE-ONLY', "AOPK ČR's own pages say the map services are for viewing only (chat 8 WORLD/CZ_desk.md); the service copyrightText is only a credit"),
    (r'kort\.vd\.dk|miljoegis|naturstyrelsen', 'NOTHING STATED', 'Danish Nature Agency (kort.vd.dk): no terms stated on the service → ask, or read live only'),
    (r'metsa\.fi|metsahallitus|paikkatieto\.ymparisto\.fi|syke', 'CLOSED', 'Metsähallitus / Finnish environmental administration: the services are for environmental-administration use only'),
]
# ArcGIS Online org ids we know (the host services*.arcgis.com says nothing; the org id is the publisher)
AGOL_ORGS = {'x5wCko8UnSi4h0CB': ('Clemson University (hosts layers for SCDNR)', 'hosted for an agency'),
             'acgZYxoN5Oj8pDLa': ("South Carolina DNR's own ArcGIS Online organisation", 'official'),
             'JJzESW51TqeY9uat': ('Defra group (Natural England / Environment Agency / Forestry Commission)', 'official'),
             'Cdxz8r11hT0MGzg1': ('Montana Fish, Wildlife & Parks', 'official'),
             '5hLFVlePaucIMGhw': ('Nevada Division of State Parks', 'official'),
             'n1YM8pTrFmm7L4hs': ('U.S. Army Corps of Engineers', 'official')}
WATER_RX = re.compile(r'reservoir|\blake|\bpool\b|water ?bod|\bwater\b|\brez\b|_rez|hydro|wetland|pond|river|stream|\bbay\b|lagoon|impoundment|nhd\b', re.I)


def known_terms(url, words):
    """(class, note) from the KNOWN_TERMS table for this host / publisher, or (None, '')."""
    blob = (host_of(url) + ' ' + str(words or '')).lower()
    for rx, cls, note in KNOWN_TERMS:
        if re.search(rx, blob, re.I): return cls, note
    return None, ''


def agol_org(url):
    m = re.match(r'https?://services\d*(?:-eu\d*)?\.arcgis\.com/([A-Za-z0-9]+)/', url or '')
    return m.group(1) if m else ''


def water_layer(probe, url):
    """True when the layer's features are lakes / reservoirs / water bodies (name, name field, service path): never READY for the key."""
    blob = ' '.join(str(x or '') for x in (probe.get('layer_name'), probe.get('name_field'), (probe.get('service') or {}).get('service_name'), re.sub(r'.*/rest/services/', '', url or '')))
    sample = ' '.join(str(x) for x in (probe.get('sample') or []))
    return bool(WATER_RX.search(blob)) or (sample and len(re.findall(r'lake|reservoir|pond|pool', sample, re.I)) >= 2)


def notice(m): print('::notice title=Layer intake::' + str(m).replace('\n', ' ')[:900], flush=True)
def late(): return time.time() - T0 > LIMIT
def load(p, d):
    try: return json.load(open(p, encoding='utf-8'))
    except Exception: return d  # noqa: BLE001
def save(p, obj):
    pathlib.Path(p).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(p).write_text(json.dumps(obj, ensure_ascii=False, indent=1, sort_keys=True) + '\n', encoding='utf-8')
def low(x): return ' '.join(re.sub(r'[^a-z0-9 ]', ' ', str(x or '').lower().replace('&', ' and ')).split())
def core(x): return ' '.join(KINDW.sub(' ', low(x)).split())
def host_of(u): return urllib.parse.urlparse(u or '').netloc.lower().split(':')[0]
def days_ago(d):
    try: return (time.time() - time.mktime(time.strptime(d[:10], '%Y-%m-%d'))) / 86400
    except Exception: return 1e9  # noqa: BLE001
def sig(row): return '|'.join(str(row.get(k) or '') for k in ('url', 'title', 'publisher', 'licence', 'note', 'expect'))


# ---- the terms classifier (pure text, tested by --selftest)
def classify_terms(text):
    """One of OPEN · CREDIT · NON-COMMERCIAL · LIVE-ONLY · NOTHING STATED · CLOSED, plus the line that decided it."""
    t = re.sub(r'<[^>]+>', ' ', str(text or '')); t = re.sub(r'&nbsp;|&amp;|&#\d+;', ' ', t); t = ' '.join(t.split())
    if not t: return 'NOTHING STATED', ''
    def line(rx):
        m = rx.search(t); s = max(0, m.start() - 70); e = min(len(t), m.end() + 90)
        return t[s:e].strip()
    if CLOSED_RX.search(t) and not OPEN_RX.search(t): return 'CLOSED', line(CLOSED_RX)
    if LIVE_RX.search(t): return 'LIVE-ONLY', line(LIVE_RX)
    if NONCOM_RX.search(t): return 'NON-COMMERCIAL', line(NONCOM_RX)
    if OPEN_RX.search(t): return 'OPEN', line(OPEN_RX)
    if CLOSED_RX.search(t): return 'CLOSED', line(CLOSED_RX)
    if CREDIT_RX.search(t): return 'CREDIT', line(CREDIT_RX)
    return 'CREDIT', t[:160]     # words were written and none limits use: a credit / description line


# ---- the name-field guess (kpc_leadtest.name_field, re-implemented so the import stays clean)
def name_field(flds):
    strs = [f['name'] for f in flds if f.get('type') in ('esriFieldTypeString', None, 'string') and f.get('name')]
    good = [f for f in strs if re.search(r'name|nm$|^nm|facility|label|site|unit|prop|park|title|nazev|název|bezeichnung|nom\b|nombre', f, re.I)
            and not re.search(r'admin|state|county|office|agency|own|mgr|manag|type|desig|file|url|link|city|region|district|short|abbr|alt|first|last|contact|email|phone|code', f, re.I)]
    best = sorted(good, key=lambda f: (0 if re.search(r'^(unit_?)?name$|^(park|site|prop(erty)?|land|area|facility)_?name$|^nazev$|^label$', f, re.I) else 1, len(f)))
    return best[0] if best else ''


# ---- who we already read
def layer_key(u):
    """('host/service/path/<layer n>', 'host/service/path') of a layer or service url."""
    p = urllib.parse.urlparse(u or ''); path = re.sub(r'/query/?$', '', p.path.rstrip('/'))
    svc = re.sub(r'/\d+$', '', path)
    return (p.netloc.lower() + path.lower()), (p.netloc.lower() + svc.lower())


def known_layers():
    """{'host/service/layer': id} + {'host/service': id} for every layer we read now, plus {host: id} for the same-publisher test."""
    out, hosts = {}, {}
    def add(u, i):
        if not u: return
        lk, sk = layer_key(u)
        out.setdefault(lk, i); out.setdefault('svc:' + sk, i); hosts.setdefault(urllib.parse.urlparse(u).netloc.lower(), i)
    for i, v in load('data/us-key/layers.json', {}).items(): add(v[0] if isinstance(v, list) and v else '', i)
    for i, v in load('data/ca-key/layers.json', {}).items(): add(v[0] if isinstance(v, list) and v else '', i)
    for st, rows in (load(LINKS / 'data/state-gis.json', {}).get('states') or {}).items():
        for r in rows or []:
            if isinstance(r, dict): add(r.get('url'), f"state-gis {st} {r.get('kind') or ''}".strip())
    return out, hosts


def overlap(url, known, hosts):
    p = urllib.parse.urlparse(url); lk, sk = layer_key(url)
    if lk in known: return 'already read as ' + known[lk], known[lk]
    if ('svc:' + sk) in known: return 'same service as ' + known['svc:' + sk] + ' (another layer of it)', ''
    h = p.netloc.lower()
    if h in hosts and not re.search(r'services\d*\.arcgis\.com|services-eu\d*\.arcgis\.com', h): return 'same publisher as ' + hosts[h], ''
    m = re.match(r'/([A-Za-z0-9]{10,})/', p.path)   # AGOL cloud: the org id is the publisher, not the shared host
    if m and re.search(r'arcgis\.com$', h):
        for k, i in known.items():
            if k.startswith(h + '/' + m.group(1).lower() + '/') or k.startswith('svc:' + h + '/' + m.group(1).lower() + '/'): return 'same publisher as ' + i, ''
    return '', ''


# ---- parks with no outline, per area
def trusted_orgs():
    c = load('data/harvest/countries.json', {}); T = {}
    for cc, v in (c.get('countries') or {}).items():
        T[cc] = [low(x.get('name') if isinstance(x, dict) else x) for x in (v.get('official_orgs') or []) if x]
    return T, c.get('govwords') or ''


def pins(area):
    """{ref: (name, lat, lon, type)} for the area's parks, from data/parkinfo."""
    P = {}
    if area.startswith('US-'): f = pathlib.Path('data/parkinfo') / f'{area}.json'
    elif area.startswith('CA'): f = pathlib.Path('data/parkinfo/CA.json')
    else: f = pathlib.Path('data/parkinfo') / f'{area[:2]}.json'
    d = load(f, {})
    for ref, v in (d.get('parks') or {}).items():
        if isinstance(v, list) and len(v) > 6 and v[5] is not None:
            if area.startswith('CA-') and len(v) > 10 and v[10] and v[10] != area[3:]: continue
            P[ref] = (v[0], v[5], v[6], v[2] if len(v) > 2 else '')
    return P


def missing(area):
    """[(ref, name, lat, lon)] parks of the area with no outline yet and a kind that wants one. 'US' / 'CA' = every state / province."""
    if area in ('US', 'CA'):
        out = []
        for f in sorted(pathlib.Path(f'data/{area.lower()}-key').glob(f'{area}-*.json')):
            if re.fullmatch(r'(US|CA)-[A-Z]{2}', f.stem): out += missing(f.stem)
        return out
    P = pins(area); out = []
    if area == 'US-KY':
        key = load(LINKS / 'data/ky-answer-key.json', {}).get('parks') or {}
        for ref, p in key.items():
            if not isinstance(p, dict) or p.get('tracts'): continue
            if ref in P and not PIN_ONLY_KINDS.search(p.get('t') or P[ref][3] or ''): out.append((ref, p.get('n') or P[ref][0], P[ref][1], P[ref][2]))
        return out
    if area.startswith('US-'): key = load(pathlib.Path('data/us-key') / f'{area}.json', {}).get('parks') or {}
    elif area.startswith('CA-'): key = load(pathlib.Path('data/ca-key') / f'{area}.json', {}).get('parks') or {}
    else:
        key = load(pathlib.Path('data/world-key') / f'{area[:2]}.json', {}).get('parks') or {}
        if not key or not all(isinstance(v, dict) and 'm' in v for v in list(key.values())[:5]): return []   # shape unclear: skip
    for ref, p in key.items():
        if not isinstance(p, dict) or p.get('m'): continue
        if ref not in P or PIN_ONLY_KINDS.search(p.get('t') or P[ref][3] or ''): continue
        out.append((ref, p.get('n') or P[ref][0], P[ref][1], P[ref][2]))
    return out


# ---- fetching
def jget(url, budget):
    """Polite JSON GET within the row's request budget → (dict or None, status)."""
    if budget[0] <= 0: return None, 'budget'
    budget[0] -= 1
    st, hd, body, _ = M.get(url, timeout=40, accept='application/json,*/*;q=0.8')
    if st != 200: return None, st
    try: j = json.loads(body.decode('utf-8', 'replace'))
    except Exception: return None, 'not json'  # noqa: BLE001
    if isinstance(j, dict) and j.get('error'): return None, 'error ' + str((j['error'].get('message') or j['error'].get('code') or ''))[:80]
    return j, 200


def strip_query(u): return re.sub(r'\?.*$', '', (u or '').strip()).rstrip('/')


def probe_rest_layer(lu, budget):
    """ArcGIS REST layer: fields, geometry, name field, extent, counts, last edit, item id."""
    j, st = jget(lu + '?f=json', budget)
    if not j: return {'opened': False, 'status': str(st)}
    flds = j.get('fields') or []
    r = {'opened': True, 'kind': 'arcgis-layer', 'layer_name': j.get('name'), 'geometry': j.get('geometryType') or ('table' if j.get('type') == 'Table' else ''),
         'polygons': bool(POLY.search(str(j.get('geometryType') or ''))), 'fields': [f.get('name') for f in flds][:40], 'name_field': name_field(flds),
         'service_item': j.get('serviceItemId') or '', 'copyright': (j.get('copyrightText') or '')[:400], 'description': re.sub(r'<[^>]+>', ' ', j.get('description') or '')[:400]}
    ed = (j.get('editingInfo') or {}).get('lastEditDate')
    if ed:
        try: r['last_edit'] = time.strftime('%Y-%m-%d', time.gmtime(int(ed) / 1000))
        except Exception: pass  # noqa: BLE001
    ex = j.get('extent') or {}
    if ex and ex.get('xmin') is not None: r['extent'] = [round(float(ex[k]), 3) for k in ('xmin', 'ymin', 'xmax', 'ymax')] + [(ex.get('spatialReference') or {}).get('latestWkid') or (ex.get('spatialReference') or {}).get('wkid')]
    c, st = jget(lu + '/query?where=1%3D1&returnCountOnly=true&f=json', budget)
    r['count'] = c.get('count') if c else None
    if r['name_field'] and r['polygons']:
        s, st = jget(lu + '/query?' + urllib.parse.urlencode({'where': '1=1', 'outFields': r['name_field'], 'returnGeometry': 'false', 'resultRecordCount': 3, 'f': 'json'}), budget)
        if s: r['sample'] = [str((f.get('attributes') or {}).get(r['name_field']))[:60] for f in s.get('features') or []][:3]
    return r


def service_layers(su, budget):
    """A service url without a layer number → its polygon layer urls (at most MAX_LAYERS) + what the service says."""
    j, st = jget(su + '?f=json', budget)
    if not j: return None, {'opened': False, 'status': str(st)}
    layers = []
    for L in (j.get('layers') or []):
        gt = L.get('geometryType') or ''
        if L.get('subLayerIds'): continue
        if gt and not POLY.search(gt): continue
        layers.append((L.get('id'), L.get('name'), gt))
    info = {'opened': True, 'kind': 'arcgis-service', 'service_name': j.get('serviceDescription') or j.get('description') or '', 'service_item': j.get('serviceItemId') or '',
            'copyright': (j.get('copyrightText') or '')[:400], 'layers_listed': len(j.get('layers') or []), 'polygon_layers': [[i, n] for i, n, g in layers][:MAX_LAYERS]}
    # MapServers often list no geometryType at the service level: the layer probe decides later
    return [f'{su}/{i}' for i, n, g in layers[:MAX_LAYERS]], info


def probe_wfs(u, budget):
    cap = u + ('&' if '?' in u else '?') + 'service=WFS&request=GetCapabilities'
    if budget[0] <= 0: return {'opened': False, 'status': 'budget'}
    budget[0] -= 1
    st, hd, body, _ = M.get(cap, timeout=40, accept='application/xml,text/xml,*/*;q=0.8')
    if st != 200: return {'opened': False, 'status': str(st), 'kind': 'wfs'}
    x = body.decode('utf-8', 'replace')
    title = re.search(r'<(?:ows:)?Title>([^<]{1,200})</', x)
    types = re.findall(r'<FeatureType>.*?<Name>([^<]{1,120})</Name>', x, re.S)[:40]
    terms = re.search(r'<(?:ows:)?(?:AccessConstraints|Fees)>([^<]{1,600})</', x)
    return {'opened': True, 'kind': 'wfs', 'title': title.group(1).strip() if title else '', 'feature_types': types, 'polygons': None, 'name_field': '',
            'copyright': terms.group(1).strip() if terms else '', 'note': 'WFS: feature types listed; polygons and name field not probed (needs a DescribeFeatureType read later)'}


def probe_file(u, budget):
    if budget[0] <= 0: return {'opened': False, 'status': 'budget'}
    budget[0] -= 1
    st, hd, body, final = M.get(u, timeout=40, head=True)
    r = {'kind': 'file', 'opened': st == 200, 'status': str(st), 'polygons': None, 'name_field': '', 'note': 'needs a download (this bot never downloads)'}
    if st == 200:
        r['size'] = hd.get('content-length'); r['last_modified'] = hd.get('last-modified'); r['content_type'] = hd.get('content-type')
    return r


def server_iteminfo(lu, budget):
    """Agency ArcGIS Servers keep their item terms at <service>/info/iteminfo (Nevada State Parks' licence was there; chat 9)."""
    svc = re.sub(r'/\d+/?$', '', (lu or '').rstrip('/'))
    j, st = jget(svc + '/info/iteminfo?f=json', budget)
    if not j or not (j.get('licenseInfo') or j.get('accessInformation') or j.get('description') or j.get('title')): return {}
    return {'item_url': svc + '/info/iteminfo', 'title': j.get('title'), 'licence_text': re.sub(r'<[^>]+>', ' ', j.get('licenseInfo') or '')[:800],
            'credit': re.sub(r'<[^>]+>', ' ', j.get('accessInformation') or '')[:300], 'about': ' '.join(re.sub(r'<[^>]+>', ' ', (j.get('description') or '') + ' ' + (j.get('snippet') or '')).split())[:300]}


def item_search(title, url, budget):
    """A 'did not open' lead gets ONE more chance: search the publisher's org for a Feature Service by title → its url or ''."""
    if not title: return ''
    h = host_of(url); oid = agol_org(url)
    base = 'https://www.arcgis.com' if re.search(r'arcgis\.com$', h) else f'https://{h}'
    q = re.sub(r'[_\-]+', ' ', re.sub(r'\(.*?\)', '', title)).strip()[:80]
    if oid: q += f' orgid:{oid}'
    j, st = jget(f'{base}/sharing/rest/search?' + urllib.parse.urlencode({'q': q + ' type:"Feature Service"', 'num': 10, 'f': 'json'}), budget)
    for r in (j or {}).get('results') or []:
        u = r.get('url') or ''
        if not u or not re.search(r'/rest/services/', u): continue
        if oid and oid not in u: continue
        if re.search(r'/\d+$', url or ''): u = u.rstrip('/') + '/' + url.rstrip('/').rsplit('/', 1)[-1]
        return u
    return ''


def item_terms(item_id, host, budget):
    """The publisher's OWN item page: licenseInfo, accessInformation, owner, orgId, modified, title, tags."""
    if not item_id: return {}
    portal = 'https://www.arcgis.com' if re.search(r'arcgis\.com$', host) else f'https://{host}'
    for base in dict.fromkeys([portal, 'https://www.arcgis.com']):
        j, st = jget(f'{base}/sharing/rest/content/items/{item_id}?f=json', budget)
        if j and (j.get('title') or j.get('owner')):
            out = {'item_url': f'{base}/home/item.html?id={item_id}', 'title': j.get('title'), 'owner': j.get('owner'), 'org_id': j.get('orgId'),
                   'licence_text': re.sub(r'<[^>]+>', ' ', j.get('licenseInfo') or '')[:800], 'credit': (j.get('accessInformation') or '')[:300],
                   'tags': (j.get('tags') or [])[:12], 'access': j.get('access')}
            try: out['modified'] = time.strftime('%Y-%m-%d', time.gmtime(int(j.get('modified') or 0) / 1000)) if j.get('modified') else ''
            except Exception: pass  # noqa: BLE001
            if j.get('orgId'):
                o, st2 = jget(f'{base}/sharing/rest/portals/{j["orgId"]}?f=json', budget)
                if o: out['org_name'] = o.get('name') or ''; out['org_url'] = o.get('urlKey') or ''
            return out
    return {}


# ---- the publisher test
def publisher_test(row, probe, terms, trusted, govwords):
    """'official' · 'unsure' · 'not official' · 'hosted for an agency' with the reason."""
    h = host_of(row.get('url')); cc = (row.get('area') or '')[:2]
    words = ' '.join(str(x or '') for x in (row.get('publisher'), terms.get('owner'), terms.get('org_name'), terms.get('credit'), probe.get('copyright'), terms.get('title')))
    oid = agol_org(row.get('url'))
    if oid in AGOL_ORGS: return AGOL_ORGS[oid][1], f'ArcGIS Online org {oid} = {AGOL_ORGS[oid][0]}'
    if UNIVERSITY.search(words) or UNIVERSITY.search(h):
        if GOV_WORDS.search(words) or FED_ORG.search(words) or re.search(r'\b(dnr|wildlife|parks?|forestry|natural resources)\b', words, re.I): return 'hosted for an agency', 'a university account holds an agency layer'
        return 'not official', 'a university account'
    if GOV_HOST.search(h) and not re.search(r'arcgis\.com$', h): return 'official', f'government host {h}'
    if FED_ORG.search(words): return 'official', 'a federal / national agency named'
    for t in trusted.get(cc) or []:
        if t and t in low(words): return 'official', f'trusted organisation ({t})'
    if NOT_OFFICIAL.search(words) and not re.search(r'department|ministry|government|state of|province of|parks canada|forest service', words, re.I):
        return 'not official', NOT_OFFICIAL.search(words).group(0) + ' in the publisher words'
    if GOV_WORDS.search(words): return 'official', 'government words: ' + GOV_WORDS.search(words).group(0)
    gw = re.compile(govwords, re.I) if govwords else None
    if gw and gw.search(words): return 'official', 'a government word of the country: ' + gw.search(words).group(0)
    if words.strip(): return 'unsure', 'no government word in the publisher, owner, organisation or credit'
    return 'unsure', 'no publisher words at all'


# ---- which missing parks the layer would close
def in_extent(ext, lat, lon):
    """True when the pin falls in the layer's extent (WGS84 or Web Mercator); True when the extent is unknown."""
    if not ext or len(ext) < 5: return True
    x0, y0, x1, y1, wkid = ext
    try:
        if wkid in (102100, 3857, 102113):
            x = lon * 20037508.34 / 180; y = math.log(math.tan((90 + lat) * math.pi / 360)) * 20037508.34 / math.pi
        elif wkid in (4326, 4269, 4152, 4617, None): x, y = lon, lat
        else: return True
        return x0 - 0.05 * abs(x1 - x0) <= x <= x1 + 0.05 * abs(x1 - x0) and y0 - 0.05 * abs(y1 - y0) <= y <= y1 + 0.05 * abs(y1 - y0)
    except Exception: return True  # noqa: BLE001


def closes(lu, nf, miss, budget, ext=None):
    out = {'n': 0, 'by_name': 0, 'pin_only': 0, 'parks': [], 'tested': 0}
    inside = [m for m in miss if in_extent(ext, m[2], m[3])]
    out['in_extent'] = len(inside)
    for ref, name, lat, lon in inside[:MAX_POINTS]:
        if late() or budget[0] <= 0: out['note'] = 'stopped early (time or request budget)'; break
        q = lu + '/query?' + urllib.parse.urlencode({'geometry': f'{lon},{lat}', 'geometryType': 'esriGeometryPoint', 'inSR': '4326', 'spatialRel': 'esriSpatialRelIntersects',
                                                     'outFields': nf, 'returnGeometry': 'false', 'f': 'json'})
        j, st = jget(q, budget); out['tested'] += 1
        if not j: continue
        f = j.get('features') or []
        if not f: continue
        pname = str((f[0].get('attributes') or {}).get(nf) or '')
        pc, cn = set(core(pname).split()), set(core(name).split())
        by_name = bool(pc and cn and (pc & cn) and len(pc & cn) >= max(1, min(len(pc), len(cn)) // 2))
        out['n'] += 1; out['by_name' if by_name else 'pin_only'] += 1
        out['parks'].append([ref, name, pname[:80]])
    return out


# ---- the verdict
def verdict(row, probe, terms_class, pub, over, cl):
    """READY · LIVE-ONLY · ASK-THE-PUBLISHER · REJECT with a one-sentence WHY."""
    if not probe.get('opened'): return 'REJECT', f"did not open ({probe.get('status')}) and no item search hit on the publisher: url to confirm"
    if over.startswith('already read'): return 'REJECT', over + ': nothing new to take'
    if pub == 'not official': return 'REJECT', 'not an official publisher: we take outlines only from the managing agency'
    if terms_class == 'CLOSED': return 'REJECT', 'the publisher closed it (internal / sign-in / by request)'
    if probe.get('kind') == 'file': return 'ASK-THE-PUBLISHER' if pub == 'official' and terms_class in ('NOTHING STATED',) else ('REJECT' if pub != 'official' else 'READY'), 'a file: needs a download by a person (polygons and name field not probed)'
    if probe.get('kind') == 'wfs':
        if pub != 'official': return 'REJECT', 'WFS from an unsure publisher'
        return ('LIVE-ONLY' if terms_class == 'LIVE-ONLY' else 'ASK-THE-PUBLISHER'), 'WFS: official, but polygons and name field need a second read'
    if probe.get('polygons') is False: return 'REJECT', f"no polygons ({probe.get('geometry') or 'no geometry'})"
    if not probe.get('name_field'): return 'REJECT', 'no name field: an outline needs a name to match a park'
    if pub == 'hosted for an agency': return 'ASK-THE-PUBLISHER', 'hosted for an agency on another account: ask who owns and licenses it'
    if terms_class == 'LIVE-ONLY': return ('LIVE-ONLY' if pub == 'official' else 'REJECT'), 'terms allow viewing only: read live, never stored'
    if terms_class == 'NOTHING STATED': return ('ASK-THE-PUBLISHER' if pub == 'official' else 'REJECT'), 'nothing stated about use on the item page or the service'
    if pub == 'unsure': return 'ASK-THE-PUBLISHER', 'publisher unsure: no government word found, ask who publishes it'
    requested = (row.get('from') or '') in ('chat 8', 'chat 9')
    if (cl or {}).get('n', 0) >= 1 or requested:
        return 'READY', f"official, {terms_class.lower()} terms, named polygons" + (f", closes {cl['n']} missing park(s)" if (cl or {}).get('n') else ', requested by ' + row.get('from'))
    if cl and cl.get('tested', 0) == 0: return 'ASK-THE-PUBLISHER', 'official and usable, but no missing parks were tested (none listed for the area or no time)'
    return 'REJECT', 'official and usable, but it closes none of the area\'s missing parks (nothing to gain yet)'


def test_result(row, v, over):
    e = row.get('expect')
    if not e: return ''
    got = v
    alts = [a.strip().upper() for a in re.split(r'\s*(?:-or-|\bor\b|/)\s*', e) if a.strip()]
    ok = any(got == a or (a == 'ALREADY READ' and over.startswith('already read')) or (a == 'ALREADY-READ' and over.startswith('already read')) for a in alts)
    return 'ok' if ok else f'MISS {e} vs {got}'


# ---- one row
def probe_row(row, known, hosts, trusted, govwords, miss_cache):
    url = strip_query(row.get('url')); budget = [MAX_REQ]
    area = row.get('area') or ''
    base = {'url': url, 'area': area, 'title': row.get('title') or '', 'publisher': row.get('publisher') or '', 'from': row.get('from') or '', 'queue_note': row.get('note') or '',
            'queue_licence': (row.get('licence') or '')[:300], 'probed': TODAY, 'ver': VER, 'sig': sig(row), 'approved': None}
    if row.get('expect'): base['expect'] = row['expect']
    results = []
    layer_urls = [url]
    is_rest = bool(re.search(r'/rest/services/', url, re.I))
    svc_info = {}
    if re.search(r'\.(zip|geojson|gdb|gpkg|shp|kml|kmz|json|csv|gml)(\?|$)', url, re.I) or re.search(r'/download', url, re.I):
        p = probe_file(url, budget); terms = {}
        tclass, tline = classify_terms(row.get('licence') or '')
        pub, why_pub = publisher_test(row, p, terms, trusted, govwords)
        over, _ = overlap(url, known, hosts)
        v, why = verdict(row, p, tclass, pub, over, None)
        r = dict(base, probe=p, terms={'class': tclass, 'line': tline, 'source': 'queue row' if row.get('licence') else 'none'}, publisher_test=[pub, why_pub], overlap=over, closes='not probed: needs a download', verdict=v, why=why)
        r['test'] = test_result(row, v, over); return [r]
    if re.search(r'service=wfs|/wfs\b|/ows\b|wfs', url, re.I) and not is_rest:
        p = probe_wfs(url, budget); terms = {}
        tclass, tline = classify_terms((p.get('copyright') or '') + ' ' + (row.get('licence') or ''))
        pub, why_pub = publisher_test(row, p, terms, trusted, govwords)
        over, _ = overlap(url, known, hosts)
        v, why = verdict(row, p, tclass, pub, over, None)
        r = dict(base, probe=p, terms={'class': tclass, 'line': tline, 'source': 'GetCapabilities + queue row'}, publisher_test=[pub, why_pub], overlap=over, closes='not probed: WFS point query not built', verdict=v, why=why)
        r['test'] = test_result(row, v, over); return [r]
    if is_rest and not re.search(r'/(FeatureServer|MapServer)/\d+$', url, re.I):
        su = re.sub(r'/(FeatureServer|MapServer)/?.*$', r'/\1', url, flags=re.I) if re.search(r'/(FeatureServer|MapServer)', url, re.I) else url
        layer_urls, svc_info = service_layers(su, budget)
        if layer_urls is None:
            r = dict(base, probe=svc_info, terms={'class': 'NOTHING STATED', 'line': '', 'source': 'none'}, publisher_test=['unsure', 'did not open'], overlap=overlap(url, known, hosts)[0], closes={}, verdict='REJECT', why=f"did not open ({svc_info.get('status')}): url to confirm")
            r['test'] = test_result(row, 'REJECT', r['overlap']); return [r]
        if not layer_urls:
            # MapServers list layers without geometryType: try the first few layers anyway
            j, st = jget(su + '?f=json', budget)
            layer_urls = [f"{su}/{L.get('id')}" for L in ((j or {}).get('layers') or []) if not L.get('subLayerIds')][:MAX_LAYERS]
        if not layer_urls:
            r = dict(base, probe=svc_info, terms={'class': 'NOTHING STATED', 'line': '', 'source': 'none'}, publisher_test=['unsure', 'no layers'], overlap=overlap(url, known, hosts)[0], closes={}, verdict='REJECT', why='the service lists no polygon layers')
            r['test'] = test_result(row, 'REJECT', r['overlap']); return [r]
    elif not is_rest:
        # an unknown page (an item page link or a web page): try the ArcGIS item id if there is one
        m = re.search(r'[?&]id=([0-9a-f]{32})', url, re.I)
        if m:
            terms = item_terms(m.group(1), host_of(url), budget)
            tclass, tline = classify_terms((terms.get('licence_text') or '') + ' ' + (terms.get('credit') or ''))
            pub, why_pub = publisher_test(row, {}, terms, trusted, govwords)
            r = dict(base, probe={'opened': bool(terms), 'kind': 'arcgis-item', 'status': 'item page only', 'polygons': None, 'name_field': ''}, terms=dict(terms, **{'class': tclass, 'line': tline, 'source': 'item page'}),
                     publisher_test=[pub, why_pub], overlap='', closes='not probed: no service url (add the layer url to the queue)', verdict='ASK-THE-PUBLISHER' if pub == 'official' and terms else 'REJECT', why='an item page without a service url: a person adds the layer url')
            r['test'] = test_result(row, r['verdict'], ''); return [r]
        p = probe_file(url, budget); p['note'] = 'not an ArcGIS REST, WFS or file url: HEAD only'
        r = dict(base, probe=p, terms={'class': 'NOTHING STATED', 'line': '', 'source': 'none'}, publisher_test=list(publisher_test(row, p, {}, trusted, govwords)), overlap='', closes='not probed: unknown url kind', verdict='REJECT', why='unknown url kind: not a layer, service, WFS or file')
        r['test'] = test_result(row, 'REJECT', ''); return [r]
    # ArcGIS REST layers
    item_cache = {}
    if layer_urls == [url]:
        p0 = probe_rest_layer(url, budget)
        if not p0.get('opened') and not late():
            found = item_search(row.get('title'), url, budget)
            if found and found != url:
                base['searched'] = f'did not open; found by item search on the publisher: {found}'; layer_urls = [found]
        else: base['_first'] = p0
    for lu in layer_urls:
        if late(): break
        p = base.pop('_first', None) if lu == url and base.get('_first') else probe_rest_layer(lu, budget)
        if svc_info: p['service'] = {k: svc_info.get(k) for k in ('service_name', 'layers_listed', 'polygon_layers')}
        over, _ = overlap(lu, known, hosts)
        iid = p.get('service_item') or svc_info.get('service_item') or ''
        if iid not in item_cache: item_cache[iid] = (item_terms(iid, host_of(lu), budget) or server_iteminfo(lu, budget)) if p.get('opened') else {}
        terms = dict(item_cache[iid])
        text = ' '.join(x for x in (terms.get('licence_text'), terms.get('credit'), p.get('copyright') or svc_info.get('copyright')) if x)
        tclass, tline = classify_terms(text)
        source = 'item page' if terms.get('item_url') else ('service copyrightText' if (p.get('copyright') or svc_info.get('copyright')) else 'none')
        if tclass == 'NOTHING STATED' and row.get('licence'):   # the publisher's own words first (the Nevada lesson); the catalog's / the chat's text only as a fallback
            tclass, tline = classify_terms(row['licence']); source = 'queue row (not the publisher\'s page)'
        kcls, knote = known_terms(lu, ' '.join(str(x or '') for x in (row.get('publisher'), terms.get('owner'), terms.get('org_name'))))
        if kcls:
            terms['terms_note'] = f"KNOWN_TERMS override: {tclass} read on the service → {kcls}. {knote}"; tclass = kcls; source = 'known-terms table (the agency states its terms elsewhere)'
        terms.update({'class': tclass, 'line': tline, 'source': source})
        pub, why_pub = publisher_test(row, p, terms, trusted, govwords)
        cl = None
        if p.get('opened') and p.get('polygons') and p.get('name_field') and not over.startswith('already read') and pub != 'not official' and tclass not in ('CLOSED',):
            if area not in miss_cache: miss_cache[area] = missing(area) if area else []
            cl = closes(lu, p['name_field'], miss_cache[area], budget, p.get('extent'))
            cl['missing_in_area'] = len(miss_cache[area])
        v, why = verdict(row, p, tclass, pub, over, cl)
        flag = ''
        if p.get('opened') and water_layer(p, lu) and v in ('READY', 'ASK-THE-PUBLISHER', 'LIVE-ONLY'):
            flag = 'water only: for the 2-fer owner step only'; why = f'{flag} (lakes / reservoirs / water bodies never go in the key as a park outline); otherwise {v}: {why}'; v = 'WATER-ONLY'
        r = dict(base, url=lu, probe=p, terms=terms, publisher_test=[pub, why_pub], overlap=over, closes=cl if cl is not None else 'not probed', verdict=v, why=why, requests_used=MAX_REQ - budget[0])
        if flag: r['flag'] = flag
        r['test'] = test_result(row, v, over)
        results.append(r)
    for r in results:
        st = str((r.get('probe') or {}).get('status') or '')
        if not (r.get('probe') or {}).get('opened') and (st in ('rest', 'budget', 'out of time', 'not json', 'robots') or st.startswith('err')): r['retry'] = True
    if not results:
        over, _ = overlap(url, known, hosts)
        r = dict(base, probe={'opened': False, 'status': 'out of time'}, terms={}, publisher_test=['unsure', ''], overlap=over, closes={}, verdict='REJECT', why='out of time before the first layer was probed (will retry)', retry=True)
        r['test'] = test_result(row, 'REJECT', over)
        results.append(r)
    return results


# ---- the review page
ORDER = ['READY', 'WATER-ONLY', 'LIVE-ONLY', 'ASK-THE-PUBLISHER', 'REJECT']


def write_review(rows, state):
    counts = {v: sum(1 for r in rows if r.get('verdict') == v) for v in ORDER}
    L = [f'# Layer intake review ({TODAY})', '',
         'Every lead in data/intake/queue.json, probed politely (metadata and counts only, never geometry). Chat 9 approves a READY row by setting '
         '`approved: true` in ready.json; the nightly key rebuild reads approved rows later. LIVE-ONLY = read live, never stored. ASK = the publisher must '
         'be asked (nothing stated, or hosted for an agency). WATER-ONLY = lakes / reservoirs: for the 2-fer owner step only, never a park outline. Terms are read on the publisher\'s OWN item page first (the Nevada lesson).', '',
         '| verdict | rows |', '|---|---|'] + [f'| {v} | {counts[v]} |' for v in ORDER] + ['']
    for v in ORDER:
        sub = [r for r in rows if r.get('verdict') == v]
        if not sub: continue
        L += [f'## {v} ({len(sub)})', '']
        for r in sorted(sub, key=lambda r: -(r['closes'].get('n', 0) if isinstance(r.get('closes'), dict) else 0)):
            p = r.get('probe') or {}; t = r.get('terms') or {}; cl = r.get('closes')
            L.append(f"### {r.get('title') or p.get('layer_name') or r['url']}  ·  {r.get('area')}  ·  from {r.get('from') or '?'}")
            L.append(f"- url: {r['url']}")
            L.append(f"- WHY: {r.get('why')}")
            L.append(f"- publisher: {r.get('publisher') or '?'} → {r.get('publisher_test', ['', ''])[0]} ({r.get('publisher_test', ['', ''])[1]})")
            if r.get('flag'): L.append(f"- FLAG: {r['flag']}")
            if r.get('searched'): L.append(f"- {r['searched']}")
            if t.get('terms_note'): L.append(f"- terms note: {t['terms_note']}")
            L.append(f"- terms: {t.get('class') or '?'} · source {t.get('source') or '?'}" + (f" · \"{(t.get('line') or '')[:200]}\"" if t.get('line') else '') + (f" · item {t.get('item_url')}" if t.get('item_url') else '') + (f" · owner {t.get('owner')}" if t.get('owner') else '') + (f" · org {t.get('org_name')}" if t.get('org_name') else ''))
            facts = []
            if p.get('kind'): facts.append(p['kind'])
            if p.get('geometry'): facts.append(str(p['geometry']))
            if p.get('name_field'): facts.append(f"name field {p['name_field']}")
            if p.get('count') is not None: facts.append(f"{p['count']} records")
            if p.get('last_edit'): facts.append(f"last edit {p['last_edit']}")
            if p.get('sample'): facts.append('sample ' + ' / '.join(str(s) for s in p['sample']))
            if p.get('size'): facts.append(f"{p['size']} bytes")
            if p.get('last_modified'): facts.append(f"modified {p['last_modified']}")
            if p.get('feature_types'): facts.append(f"{len(p['feature_types'])} feature types")
            if p.get('status') and not p.get('opened'): facts.append(f"status {p['status']}")
            if facts: L.append('- facts: ' + ' · '.join(facts))
            if r.get('overlap'): L.append(f"- overlap: {r['overlap']}")
            if isinstance(cl, dict) and cl:
                L.append(f"- closes: {cl.get('n', 0)} of {cl.get('tested', 0)} tested missing parks (by name {cl.get('by_name', 0)}, pin only {cl.get('pin_only', 0)}; {cl.get('in_extent', '?')} of the area's {cl.get('missing_in_area', '?')} missing parks lie in the layer's extent)")
                for ref, name, pn in (cl.get('parks') or [])[:25]: L.append(f"  - {ref} {name} → polygon \"{pn}\"")
            elif isinstance(cl, str): L.append(f"- closes: {cl}")
            if r.get('test'): L.append(f"- TEST: {r['test']}")
            L.append('')
    tests = [r for r in rows if r.get('test')]
    if tests:
        L += ['## Known-answer test rows', '', '| row | expect | got | result |', '|---|---|---|---|']
        for r in tests: L.append(f"| {r.get('title') or r['url']} | {r.get('expect')} | {r.get('verdict')} | {r['test']} |")
        gate = 'PASS' if all(r['test'] == 'ok' for r in tests) else 'FAIL'
        L += ['', f'GATE={gate}', '']
        state['gate'] = gate
    (OUT / 'review.md').write_text('\n'.join(L), encoding='utf-8')
    return counts


# ---- self test (no web)
def selftest():
    bad = []
    T = [('Use of this data is subject to the Open Government Licence v3.0', 'OPEN'), ('Licensed under CC BY 4.0', 'OPEN'), ('Public domain', 'OPEN'),
         ('Copyright State of Nevada, no warranty', 'CREDIT'), ('This data is not for redistribution', 'LIVE-ONLY'), ('', 'NOTHING STATED'),
         ('internal use only, login required', 'CLOSED'), ('may be used for non-commercial purposes with attribution', 'NON-COMMERCIAL')]
    for text, want in T:
        got = classify_terms(text)[0]
        if got != want: bad.append(f'terms: "{text}" → {got}, wanted {want}')
    F = [([{'name': 'OBJECTID', 'type': 'esriFieldTypeOID'}, {'name': 'LandName', 'type': 'esriFieldTypeString'}, {'name': 'County', 'type': 'esriFieldTypeString'}], 'LandName'),
         ([{'name': 'Shape', 'type': 'esriFieldTypeGeometry'}, {'name': 'AdminName', 'type': 'esriFieldTypeString'}, {'name': 'PARK', 'type': 'esriFieldTypeString'}], 'PARK'),
         ([{'name': 'ID', 'type': 'esriFieldTypeInteger'}, {'name': 'Acres', 'type': 'esriFieldTypeDouble'}], '')]
    for flds, want in F:
        got = name_field(flds)
        if got != want: bad.append(f'name field: {[f["name"] for f in flds]} → {got!r}, wanted {want!r}')
    base = {'opened': True, 'kind': 'arcgis-layer', 'polygons': True, 'name_field': 'NAME'}
    V = [((dict(base), 'CREDIT', 'official', '', {'n': 3, 'tested': 10}), 'READY'),
         ((dict(base), 'LIVE-ONLY', 'official', '', {'n': 3, 'tested': 10}), 'LIVE-ONLY'),
         ((dict(base), 'NOTHING STATED', 'official', '', {'n': 3, 'tested': 10}), 'ASK-THE-PUBLISHER'),
         ((dict(base), 'OPEN', 'not official', '', {'n': 3, 'tested': 10}), 'REJECT'),
         ((dict(base), 'OPEN', 'official', 'already read as sgmta', {'n': 3, 'tested': 10}), 'REJECT'),
         ((dict(base, polygons=False, geometry='esriGeometryPoint'), 'OPEN', 'official', '', None), 'REJECT'),
         ((dict(base), 'CREDIT', 'hosted for an agency', '', {'n': 3, 'tested': 10}), 'ASK-THE-PUBLISHER')]
    for (p, tc, pub, over, cl), want in V:
        got = verdict({'from': 'harvester'}, p, tc, pub, over, cl)[0]
        if got != want: bad.append(f'verdict: {tc}/{pub}/{over or "-"} → {got}, wanted {want}')
    K = [(('https://gis.nature.cz/arcgis/rest/services/ObecnaOchrana/PrirodniPark/MapServer/0', 'AOPK'), 'LIVE-ONLY'),
         (('https://kort.vd.dk/arcgis/rest/services/x/MapServer/0', ''), 'NOTHING STATED'),
         (('https://services.arcgis.com/JJzESW51TqeY9uat/arcgis/rest/services/x/FeatureServer/0', 'Defra'), None)]
    for (u, w), want in K:
        got = known_terms(u, w)[0]
        if got != want: bad.append(f'known terms: {u} → {got}, wanted {want}')
    W = [({'layer_name': 'usace_rez', 'name_field': 'NAME'}, 'https://services7.arcgis.com/n1YM8pTrFmm7L4hs/arcgis/rest/services/usace_rez/FeatureServer/0', True),
         ({'layer_name': 'State Parks', 'name_field': 'NAME', 'sample': ['Big Lake State Park']}, 'https://x/arcgis/rest/services/FWPLND_STATEPARKS/FeatureServer/0', False)]
    for p, u, want in W:
        if water_layer(p, u) != want: bad.append(f'water: {u} → {not want}')
    P = [('https://services1.arcgis.com/x5wCko8UnSi4h0CB/arcgis/rest/services/SCDNR_Managed_Lands_Public_Viewer/FeatureServer/0', 'hosted for an agency'),
         ('https://services.arcgis.com/acgZYxoN5Oj8pDLa/arcgis/rest/services/SCDNR_Managed_Lands_Public_Viewer/FeatureServer/0', 'official')]
    for u, want in P:
        got = publisher_test({'url': u, 'publisher': '', 'area': 'US-SC'}, {}, {}, {}, '')[0]
        if got != want: bad.append(f'publisher: {u} → {got}, wanted {want}')
    n = len(T) + len(F) + len(V) + len(K) + len(W) + len(P)
    for b in bad: print('SELFTEST FAIL ' + b)
    print(f'SELFTEST {"PASS" if not bad else "FAIL"}: {n - len(bad)} of {n} checks ok')
    return 0


# ---- main
def main():
    global M
    OUT.mkdir(parents=True, exist_ok=True)
    state = load(OUT / 'state.json', {'hosts': {}, 'rows': {}})
    ready = load(OUT / 'ready.json', {'about': 'Layer intake results: one row per probed layer (metadata and counts only, never geometry). approved: null until chat 9 sets true; the nightly key rebuild reads approved rows later. Written by kpc_intake_bot.py.',
                                       'read': ['data/intake/queue.json', 'data/us-key/layers.json', 'data/ca-key/layers.json', 'KPC-Links data/state-gis.json', 'data/harvest/countries.json', 'data/parkinfo', 'data/us-key', 'data/ca-key', 'data/world-key', 'KPC-Links data/ky-answer-key.json'], 'rows': []})
    M = Manners('layer intake line (probes map-layer leads: metadata and counts only)', state.get('hosts'))
    queue = load(QUEUE_FILE, {}).get('rows') or []
    want = [strip_query(u) for u in (os.environ.get('ROWS') or '').split() if u.strip()]
    old = {r['url']: r for r in ready.get('rows') or [] if isinstance(r, dict) and r.get('url')}
    known, hosts = known_layers(); trusted, govwords = trusted_orgs(); miss_cache = {}
    todo = []
    for row in queue:
        u = strip_query(row.get('url'))
        if not u: continue
        STAT['rows'] += 1
        if want and u not in want: continue
        prev = state['rows'].get(u) or {}
        fresh = prev.get('probed') and days_ago(prev['probed']) < REFRESH_DAYS and prev.get('sig') == sig(row) and not prev.get('retry')
        if fresh and not want: STAT['skipped_fresh'] += 1; continue
        todo.append(row)
    notice(f'{len(todo)} queue rows to probe ({STAT["skipped_fresh"]} probed within {REFRESH_DAYS} days skipped; {len(known)} layers already read)')
    done = 0
    for row in todo:
        if late(): break
        u = strip_query(row.get('url'))
        try: results = probe_row(row, known, hosts, trusted, govwords, miss_cache)
        except Exception as e:  # noqa: BLE001
            results = [{'url': u, 'area': row.get('area'), 'title': row.get('title'), 'from': row.get('from'), 'probed': TODAY, 'sig': sig(row), 'approved': None, 'probe': {'opened': False, 'status': 'bot error ' + str(e)[:120]},
                        'terms': {}, 'publisher_test': ['unsure', ''], 'overlap': '', 'closes': {}, 'verdict': 'REJECT', 'why': 'the bot hit an error on this row (will retry)', 'retry': True, 'test': test_result(row, 'REJECT', '') if row.get('expect') else ''}]
        for r in results:
            keep = old.get(r['url']) or {}
            if keep.get('approved') is True and r.get('verdict') == keep.get('verdict'): r['approved'] = True   # a re-probe keeps chat 9's yes while the verdict holds
            if keep.get('approved_note'): r['approved_note'] = keep['approved_note']
            old[r['url']] = r
            STAT['probed'] += 1
            if not (r.get('probe') or {}).get('opened'): STAT['did_not_open'] += 1
            k = {'READY': 'ready', 'WATER-ONLY': 'water_only', 'LIVE-ONLY': 'live_only', 'ASK-THE-PUBLISHER': 'ask', 'REJECT': 'reject'}.get(r.get('verdict'))
            if k: STAT[k] += 1
            if r.get('test') == 'ok': STAT['tests_ok'] += 1
            elif r.get('test'): STAT['tests_miss'] += 1
        state['rows'][u] = {'probed': TODAY, 'sig': sig(row), 'verdicts': [r.get('verdict') for r in results], 'retry': any(r.get('retry') for r in results)}
        done += 1
        if done % 5 == 0:
            ready['rows'] = list(old.values()); save(OUT / 'ready.json', ready); state['hosts'] = M.resting(); save(OUT / 'state.json', state)
    ready['rows'] = list(old.values()); ready['updated'] = TODAY
    save(OUT / 'ready.json', ready)
    counts = write_review(ready['rows'], state)
    state['hosts'] = M.resting(); state['last_run'] = TODAY; state['stat'] = STAT; state['manners'] = M.stat
    left = sum(1 for row in queue if strip_query(row.get('url')) and not (state['rows'].get(strip_query(row.get('url'))) or {}).get('probed') or (state['rows'].get(strip_query(row.get('url'))) or {}).get('retry'))
    save(OUT / 'state.json', state)
    notice(f'probed {done} rows this run: ' + ' · '.join(f'{v} {counts[v]}' for v in ORDER) + f' (whole list); did not open {STAT["did_not_open"]}; manners {M.stat}')
    if TEST or STAT['tests_ok'] or STAT['tests_miss']:
        tests = [r for r in ready['rows'] if r.get('test')]
        gate = state.get('gate') or ('PASS' if tests and all(r['test'] == 'ok' for r in tests) else 'FAIL')
        for r in tests: print(f"TEST {r['test']:<40} {r.get('expect')} → {r.get('verdict')}  {r.get('title') or r['url']}")
        notice(f'test rows: {STAT["tests_ok"]} ok, {STAT["tests_miss"]} miss → GATE={gate}')
        print(f'GATE={gate}')
    print(f'LEFT={left}')
    return 0


if __name__ == '__main__':
    if '--selftest' in sys.argv: sys.exit(selftest())
    try: sys.exit(main())
    except Exception as e:  # noqa: BLE001
        notice(f'bot error: {e}')
        try: save(OUT / 'state.json', dict(load(OUT / 'state.json', {}), error=str(e)[:300], last_run=TODAY))
        except Exception: pass  # noqa: BLE001
        print('LEFT=0'); sys.exit(0)
