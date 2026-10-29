#!/usr/bin/env python3
"""WORLD HARVESTER (Fable, chat 2, Oct 27 2026; HQ 10:42 PM). A NEW bot, separate from the Discovery Bot: explores OUTSIDE North
America for legitimate, OFFICIAL park GIS (protected-area and park boundary layers) and writes LEADS for chat 8 to grade. It never
adds anything to the answer key. WDPA is never asked. Historic sites and city / council parks are skipped.

Where it looks, one country at a time (data/harvest/countries.json, built by kpc_world_seed.py from chat 8's scouting):
  A  ArcGIS Online: the country's official organisations (walked whole) + a keyword search in the local language
  B  the national open-data catalog (CKAN / data.gouv.fr / dane.gov.pl): datasets whose resources are a map service or WFS
  C  the agencies' own map servers (folders walked two deep) and WFS endpoints (GetCapabilities = the list of feature types)
  D  Europe: the EEA's official server (bio.discomap.eea.europa.eu), walked once per run and shared by every EU country
Every lead records: the web address FIRST, the publisher, the licence text, the date, what the layer IS (polygons with a name field,
trail lines…), a record count and three sample names (attributes only: never a whole dataset).

Manners: one request every 2 s per server; robots.txt obeyed; a 429 or 5xx = wait 30 / 60 / 120 s and slow that server down;
three strikes = that server is left alone for a day; a User-Agent naming the club site; only metadata and layer lists.
Long run: MINUTES budget per call; resumable (data/harvest/state.json remembers each country's progress); never fails.

Env: COUNTRIES='GB' (blank = the next unfinished countries in queue order) · MINUTES (default 55) · OUT (data/harvest).
"""
import json, os, pathlib, re, sys, time, urllib.parse, urllib.request, urllib.robotparser

OUT = pathlib.Path(os.environ.get('OUT') or 'data/harvest')
LINKS = pathlib.Path(os.environ.get('LINKS') or 'links')
T0 = time.time(); LIMIT = float(os.environ.get('MINUTES') or 55) * 60
UA = 'KPC park mapping (https://kentuckyportableclub.github.io/KPC-Links/; ham radio club; 1 request per 2 s; metadata only)'
GAP = 2.0                 # seconds between requests to one server
STRIKES_OUT = 3           # then the server is left alone for a day
MAX_LAYERS = 40           # layers read per service
STAT = {'requests': 0, 'hits': 0, 'leads': 0, 'already_read': 0, 'skipped': 0, 'not_official': 0, 'robots': 0, 'strikes': 0, 'errors': 0}
LAST, ROBOTS, DEAD = {}, {}, {}
ROBOTS_SAID = {}          # host -> the first lines of its robots.txt (so HQ can see what refused us)
# HQ RULING Oct 27 10:57 PM (narrow, by PATH, not by host): ArcGIS's documented REST API only — the ArcGIS Online search / sharing
# API (/sharing/rest/) and the hosted services' /rest/services/ metadata (?f=json) on arcgis.com hosts — may be read although those
# hosts carry a blanket robots.txt. Metadata only, 1 request / 2 s, back-off and three strikes as everywhere. EVERY other host obeys
# robots.txt. Each exempted host is logged in the run report.
ROBOTS_API = re.compile(r'(^|\.)arcgis\.com$')
ROBOTS_API_PATH = re.compile(r'^/sharing/rest/|/rest/services(/|$)')
ROBOTS_EXEMPTED = {}
RUN = time.strftime('%Y-%m-%d')

SKIP = re.compile(r'historic|heritage site|monument\b|castle|schloss|château|castillo|castello|zamek|cemeter|friedhof|cimeti|church|kirche|'
                  r'cathedral|museum|museo|musée|battlefield|memorial|city park|municipal|stadtpark|parc urbain|parque urbano|parco urbano|'
                  r'playground|spielplatz|golf|cemetery|graveyard|parking|car park|parkplatz|bus stop|school|hospital|airport|zoo\b', re.I)
PARKW = re.compile(r'park|parc|parque|parco|reserv|réserve|reserva|riserva|rezerwat|rezerv|natur|natura|nature|conserv|protect|protég|'
                   r'proteg|schutz|verne|skydd|suoje|kaitse|liegum|draustin|wilderness|wildnis|forest|forêt|bosque|foresta|wald|las\b|lasy|'
                   r'skog|metsä|mets|national|nacional|nazionale|narodow|národn|nemzeti|公園|保護|自然|국립|보호|national trail|ramsar|'
                   r'natura 2000|sssi|ssac|spa\b|sac\b|landscape|landschaft|paysage|paisaje|paesaggio|krajobraz|公园|保护区', re.I)
TRAILW = re.compile(r'\btrail|\bpath|footpath|sentier|sendero|sentiero|wanderweg|szlak|stezka|chemin|way\b|camino|route\b|leden?\b|reitti', re.I)
OFFICIAL_DOM = re.compile(r'\.(gov|gouv|gob|gc|govt|go|gv|gob|bund|admin|edu)\.[a-z]{2}$|\.gov$|\.gov\.[a-z]{2}$|\.gouv\.fr$|\.go\.jp$|\.go\.kr$|'
                          r'\.bund\.de$|\.gv\.at$|\.admin\.ch$|\.gov\.uk$|\.europa\.eu$|\.lasy\.gov\.pl$|\.gios\.gov\.pl$|\.mnhn\.fr$|'
                          r'\.ign\.(fr|es)$|\.bfn\.de$|\.icnf\.pt$|\.slip\.wa\.gov\.au$|\.vic\.gov\.au$|\.nsw\.gov\.au$|\.qld\.gov\.au$|'
                          r'\.naturescot\.gov\.uk$|\.doc\.govt\.nz$|\.rvo\.nl$|\.pdok\.nl$|\.geonorge\.no$|\.lantmateriet\.se$|'
                          r'\.naturvardsverket\.se$|\.miljodirektoratet\.no$|\.env\.go\.jp$|\.biodic\.go\.jp$|\.geoportal\.gov\.pl$', re.I)


def notice(m): print('::notice title=World harvester::' + str(m).replace('\n', ' ')[:900], flush=True)
def late(): return time.time() - T0 > LIMIT
def load(p, d):
    try: return json.load(open(p, encoding='utf-8'))
    except Exception: return d  # noqa: BLE001
def save(p, obj):
    pathlib.Path(p).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(p).write_text(json.dumps(obj, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')


# ------------------------------------------------------------------ manners
def host_of(u): return urllib.parse.urlparse(u).netloc.lower()


def robots_ok(u):
    h = host_of(u)
    if h not in ROBOTS:
        rp = urllib.robotparser.RobotFileParser()
        try:
            ru = f'{urllib.parse.urlparse(u).scheme}://{h}/robots.txt'
            with urllib.request.urlopen(urllib.request.Request(ru, headers={'User-Agent': UA}), timeout=15) as r: txt = r.read(20000).decode('utf-8', 'replace')
            rp.parse(txt.splitlines()); ROBOTS[h] = rp
            ROBOTS_SAID[h] = ' | '.join(l.strip() for l in txt.splitlines() if l.strip() and not l.startswith('#'))[:160]
        except Exception as e: ROBOTS[h] = None; ROBOTS_SAID[h] = 'no robots.txt (' + str(e)[:30] + ')'  # noqa: BLE001  (no robots file = allowed)
    rp = ROBOTS[h]
    try: ok = rp is None or rp.can_fetch(UA, u) or rp.can_fetch('*', u)
    except Exception: ok = True  # noqa: BLE001
    if not ok and ROBOTS_API.search(h) and ROBOTS_API_PATH.search(urllib.parse.urlparse(u).path):
        ok = True; STAT['robots_exempt'] = STAT.get('robots_exempt', 0) + 1; ROBOTS_EXEMPTED[h] = ROBOTS_EXEMPTED.get(h, 0) + 1
    if not ok:
        STAT['robots'] += 1
        ROBOTS_REFUSED[h] = ROBOTS_REFUSED.get(h, 0) + 1
    return ok


ROBOTS_REFUSED = {}


def get(u, params=None, timeout=30, raw=False):
    """Polite GET: 2 s per server, robots, back-off on 429 / 5xx, three strikes and the server is left alone for a day."""
    h = host_of(u)
    if DEAD.get(h, 0) > time.time(): raise RuntimeError('server left alone (strikes)')
    if not robots_ok(u): raise RuntimeError('robots.txt says no')
    q = dict(params or {})
    if not raw: q.setdefault('f', 'json')
    full = u + (('&' if '?' in u else '?') + urllib.parse.urlencode(q) if q else '')
    for attempt in range(3):
        w = GAP * (2 ** STRIKE.get(h, 0)) - (time.time() - LAST.get(h, 0))
        if w > 0: time.sleep(w)
        LAST[h] = time.time(); STAT['requests'] += 1
        try:
            with urllib.request.urlopen(urllib.request.Request(full, headers={'User-Agent': UA, 'Accept': 'application/json, text/xml, */*'}), timeout=timeout) as r:
                body = r.read(30_000_000)
            if raw: return body.decode('utf-8', 'replace')
            try: j = json.loads(body.decode('utf-8', 'replace'))
            except json.JSONDecodeError:
                if attempt == 0: STAT['retried_json'] = STAT.get('retried_json', 0) + 1; time.sleep(5); continue   # Oct 28 (chat 8): 'Unterminated string' = a cut answer: once more
                raise
            if isinstance(j, dict) and j.get('error'): raise RuntimeError('server error: ' + str(j['error'])[:100])
            return j
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504):
                STRIKE[h] = STRIKE.get(h, 0) + 1; STAT['strikes'] += 1
                if STRIKE[h] >= STRIKES_OUT: DEAD[h] = time.time() + 86400; raise RuntimeError(f'HTTP {e.code} three times: left alone for a day')
                time.sleep(30 * (2 ** attempt)); continue
            raise RuntimeError(f'HTTP {e.code}')
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            STRIKE[h] = STRIKE.get(h, 0) + 1; STAT['strikes'] += 1
            if STRIKE[h] >= STRIKES_OUT: DEAD[h] = time.time() + 86400; raise RuntimeError('no answer three times: left alone for a day')
            time.sleep(15 * (attempt + 1)); continue
    raise RuntimeError('gave up')


STRIKE = {}


# ------------------------------------------------------------------ what a layer is
TRUSTED_ORGS = set()   # ArcGIS Online organisations chat 8 names as the agency itself (seed 'official_orgs')


NONGOV = re.compile(r'\bwwf\b|world wide fund|consult|\bltd\b|limited|\bgmbh\b|\binc\b|\bllc\b|\bplc\b|\bnabu\b|foundation|stiftung|'
                    r'\btrust\b|university|universit|college|esri\b|community|volunteer|club\b|\bngo\b|association|verein', re.I)


def official(publisher, url, cc, govwords):
    p = (publisher or '').lower()
    if NONGOV.search(p): return False   # Oct 28 (chat 8): WWF Germany and a consultancy are not the government
    m = re.search(r'arcgis\.com/([A-Za-z0-9]{16,})/', url or '')
    if m and m.group(1) in TRUSTED_ORGS: return True
    return bool(OFFICIAL_DOM.search(host_of(url))) or bool(re.search(govwords, p))


# Oct 28 (chat 8 grade): census areas, photo footprints, fire, air quality, planning, map-sheet grids are never park layers
GENERIC = re.compile(r'census|statistic|\babs[_ ]?20|mesh ?block|orthophoto|aerial|imagery|photo|footprint|bush ?fire|fire[_ ]?prone|wildfire|air[_ ]?quality|'
                     r'\bpm10\b|\bpm2|nitrogen|\bno2\b|ozone|noise|flood|zoning|planning scheme|parcel|cadastr|property|electoral|postcode|post code|'
                     r'map ?index|sheet index|\bindex\b|\bgrid\b|\btiles?\b|lga\b|local government area|suburb|locality|mining|tenement|geolog|soil|elevation|contour|'
                     r'conservation target|capture status|roadside|town reserve|aboriginal communit|common land|access layer|open access land|\bcrow\b|right to roam', re.I)


def classify(name, geom, fields, service='', force=False):
    n = re.sub(r'[_\-/]+', ' ', (name or '') + ' ' + (service or ''))
    ln = re.sub(r'[_\-/]+', ' ', name or '')
    if SKIP.search(n) and not force: return None, 'skipped (' + SKIP.search(n).group(0) + ': historic / city / not a park)'
    if force and 'polygon' in (geom or '').lower(): return 'outline', 'known-good layer (chat 8)'
    if GENERIC.search(ln): return None, 'not a park layer (' + GENERIC.search(ln).group(0) + ')'   # the LAYER's own name (a service called 'Property_and_Planning' still holds park layers)
    if re.search(r'legislated lands|managed lands|public lands|crown reserve|protected lands', ln, re.I) and 'polygon' in (geom or '').lower(): return 'outline', 'agency-managed land polygons'
    g = (geom or '').lower()
    hasname = any(re.search(r'name|nom|nombre|nome|navn|namn|nimi|nazwa|název|naam|bezeichnung|title|label|site|designation|designat', f, re.I) for f in fields or [])
    if TRAILW.search(n) and 'line' in g: return 'trail line', 'trail / path lines'
    if PARKW.search(n) and 'polygon' in g: return 'outline', 'park / protected-area polygons' + (' with a name field' if hasname else ' (no name field seen)')
    if 'polygon' in g and hasname and re.search(r'boundar|grenze|limite|límite|limiti|granic|hranice|boundary|zone|zona|area|gebiet|område|alue', n, re.I): return 'area', 'named area polygons (no park word: never band A)'
    if PARKW.search(n) and 'point' in g: return 'access', 'park points (sites / entrances)'
    return None, 'not a park layer'


def key_of(u):
    u = (u or '').split('?')[0].rstrip('/').lower()
    return re.sub(r'/(feature|map)server(/\d+)?$', '', u)


def already_read():
    seen = set()
    for f in [LINKS / 'data/world-key/layers.json', LINKS / 'data/ca-key/layers.json']:
        for u in re.findall(r'https?://[^"\s\\]+', open(f, encoding='utf-8').read() if f.exists() else ''): seen.add(key_of(u))
    return seen


# ------------------------------------------------------------------ sources
def probe_layer(lu, service='', force=False):
    d = get(lu)
    flds = [x['name'] for x in d.get('fields') or []]
    geom = (d.get('geometryType') or '').replace('esriGeometry', '')
    gap, why = classify(d.get('name') or '', geom, flds, service, force)
    row = {'id': d.get('id'), 'name': (d.get('name') or '')[:70], 'geom': geom, 'gap': gap, 'is': why, 'fields': flds[:20]}
    if gap:
        try: row['records'] = get(lu + '/query', {'where': '1=1', 'returnCountOnly': 'true'}).get('count')
        except Exception as e: row['count_err'] = str(e)[:50]  # noqa: BLE001
        nf = next((f for f in flds if re.search(r'name|nom|nombre|nome|navn|namn|nimi|nazwa|název|naam|bezeichnung|title|label', f, re.I)), '')
        if nf:
            try:
                q = get(lu + '/query', {'where': '1=1', 'outFields': nf, 'returnGeometry': 'false', 'resultRecordCount': 3})
                row['sample'] = [str((x.get('attributes') or {}).get(nf))[:50] for x in q.get('features') or []][:3]; row['name_field'] = nf
            except Exception: pass  # noqa: BLE001
    return row


def add_lead(leads, cc, url, title, publisher, catalog, licence, date, rows, known, govwords, note=''):
    k = key_of(url)
    if k in known: STAT['already_read'] += 1; return None
    gaps = sorted({r['gap'] for r in rows if r.get('gap')})
    if not gaps: STAT['skipped'] += 1; return None
    off = official(publisher, url, cc, govwords)
    kg = key_of(url) in KG_NOW
    if not off and not kg and not ({'outline', 'trail line'} & set(gaps)): STAT['not_official'] += 1; return None
    x = leads.get(k) or {'url': url, 'cc': cc, 'title': (title or '')[:90], 'publisher': (publisher or '')[:80], 'catalog': catalog,
                         'licence': (licence or '')[:200], 'date': date or '', 'found': RUN, 'gaps': gaps, 'layers': [], 'note': note}
    x['layers'] = ([r for r in rows if r.get('gap')] + x.get('layers', []))[:12]
    x['gaps'] = sorted(set(x['gaps']) | set(gaps))
    g = 0
    g += 1                                                       # answers (we read it)
    g += 1 if any(r.get('name_field') for r in x['layers']) else 0
    g += 1 if official(publisher, url, cc, govwords) else 0
    lic = (licence or '').lower()
    g += 1 if re.search(r'cc[- ]?by|cc0|open government|ogl|public domain|odbl|creative commons|open data|datenlizenz|licence ouverte|'
                        r'nlod|inspire|free use|no restriction|unrestricted|libre|aberto|otwart', lic) else 0
    if not lic: x['licence_note'] = 'licence unknown: chat 8 asks'
    elif re.search(r'no derivative|internal|not for|prohibit|all rights reserved|redistribut', lic): x['licence_note'] = 'LICENCE FORBIDS PASSING IT ON: list only, never store'
    g += 1 if 'outline' in gaps else 0
    g += 1 if max([r.get('records') or 0 for r in x['layers']] or [0]) >= 20 else 0
    x['grade'] = g; x['band'] = 'A' if g >= 5 else 'B' if g >= 3 else 'C'
    if not ({'outline', 'trail line', 'access'} & set(x['gaps'])): x['band'] = 'C'; x['band_note'] = 'only generic named areas (no park word): never band A'
    if not off:   # Oct 28 (chat 8): content may be right, publisher is not the government: B at most (a known-good), else C
        x['band'] = 'B' if kg and x['band'] != 'C' else 'C'; x['publisher_note'] = 'not a government publisher: take the agency\'s own copy if one exists'
    if kg: x['known_good'] = True
    if x.get('licence_note', '').startswith('LICENCE FORBIDS'): x['band'] = 'C'
    leads[k] = x; STAT['leads'] += 1
    return x


def walk_service(svc, cc, leads, known, govwords, catalog, publisher='', licence='', date='', note=''):
    """One map / feature service: its layers (at most MAX_LAYERS) classified; a lead when any layer is a park layer."""
    if key_of(svc) in known: STAT['already_read'] += 1; return
    d = get(svc)
    lic = licence or re.sub(r'<[^>]+>', ' ', str(d.get('copyrightText') or '')).strip()
    lays = d.get('layers')
    rows = []
    if lays is None and 'geometryType' in d: rows.append(probe_layer(svc))
    else:
        # Oct 28 (chat 8 fix 1): the layer LIST is read first; park- / trail-named layers are opened wherever they sit (GB
        # Core_Data_Non_WMS layer 50 was past the old 40-layer limit), then other layers up to MAX_LAYERS; generic ones never
        lays = lays or []
        named = [L for L in lays if (PARKW.search(L.get('name') or '') or TRAILW.search(L.get('name') or '')) and not GENERIC.search(L.get('name') or '')]
        want = [L for L in lays if str(L.get('id')) in ONLY_LAYER.get(key_of(svc), set())]
        rest = [L for L in lays if L not in named and L not in want and not GENERIC.search(L.get('name') or '')][:max(0, MAX_LAYERS - len(named))]
        kgs = key_of(svc) in KG_NOW   # Oct 29 (chat 8 + Fable): a seeded known-good service skips the park-word filter (Poland's forest layers were dropped)
        if kgs: rest = [L for L in lays if L not in named and L not in want][:MAX_LAYERS]
        for L in (want + named[:150] + rest):
            if late(): break
            try: rows.append(probe_layer(f"{svc.rstrip('/')}/{L.get('id')}", d.get('name') or svc.split('/services/')[-1], force=(L in want) or kgs))
            except Exception as e: rows.append({'id': L.get('id'), 'error': str(e)[:60]})  # noqa: BLE001
    add_lead(leads, cc, svc, svc.split('/services/')[-1].replace('/FeatureServer', '').replace('/MapServer', ''), publisher or host_of(svc), catalog, lic, date, rows, known, govwords, note)


def walk_server(root, cc, leads, known, govwords, done):
    """Folders two deep, every map / feature service."""
    try: top = get(root)
    except Exception as e: STAT['errors'] += 1; return f'{root}: {str(e)[:60]}'  # noqa: BLE001
    folders = [''] + list(top.get('folders') or [])
    for f in list(folders)[1:]:
        if late(): break
        try: folders += [g if g.startswith(f + '/') else f + '/' + g for g in (get(f'{root}/{f}').get('folders') or [])]
        except Exception: pass  # noqa: BLE001
    n = 0
    for f in folders:
        if late(): break
        try: j = top if f == '' else get(f'{root}/{f}')
        except Exception: continue  # noqa: BLE001
        for s in j.get('services') or []:
            if s.get('type') not in ('MapServer', 'FeatureServer'): continue
            svc = f"{root}/{s['name']}/{s['type']}"
            if svc in done or late(): continue
            try: walk_service(svc, cc, leads, known, govwords, 'agency server ' + host_of(root)); n += 1
            except Exception as e: STAT['errors'] += 1; done.add(svc); continue  # noqa: BLE001
            done.add(svc)
    return f'{root}: {len(folders)} folders, {n} services read'


def wfs_capabilities(u, cc, leads, known, govwords):
    """A WFS / OGC endpoint: GetCapabilities only = the list of feature types (names + titles), never the data."""
    base = u.split('?')[0]
    if re.search(r'ogcapi|/ogc/v\d|/collections$', base, re.I): return ogc_collections(base, cc, leads, known, govwords)   # Oct 29: PDOK's '/ogc/v1' is an OGC API
    try: xml = get(base, {'service': 'WFS', 'version': '2.0.0', 'request': 'GetCapabilities'}, raw=True)
    except Exception as e:  # noqa: BLE001
        try: return ogc_collections(base, cc, leads, known, govwords)   # Oct 28: an OGC API answers /collections, not GetCapabilities
        except Exception: STAT['errors'] += 1; return f'{base}: {str(e)[:60]}'  # noqa: BLE001
    types = []
    for blk in re.findall(r'<(?:\w+:)?FeatureType\b[^>]*>(.*?)</(?:\w+:)?FeatureType>', xml, re.S)[:300]:   # Oct 28 (chat 8): <FeatureType xmlns=…> has attributes
        nm = re.search(r'<(?:\w+:)?Name>([^<]+)</', blk); ti = re.search(r'<(?:\w+:)?Title>([^<]*)</', blk)
        if nm: types.append((nm.group(1).strip(), (ti.group(1).strip() if ti else '')))
    if not types and not re.search(r'wms', base, re.I):   # an endpoint that answered with no WFS feature types may be an OGC API: try /collections
        try: return ogc_collections(base, cc, leads, known, govwords)
        except Exception: pass  # noqa: BLE001
    lic = ' '.join(re.findall(r'<(?:ows:)?(?:AccessConstraints|Fees)>([^<]{0,160})<', xml))[:200]
    prov = ' '.join(re.findall(r'<(?:ows:)?ProviderName>([^<]{0,80})<', xml))
    rows = []
    kgs = key_of(base) in KG_NOW   # Oct 29: a seeded known-good endpoint skips the park-word filter
    for nm, title in types:
        gap, why = classify(title or nm, 'Polygon', ['name'], force=kgs)   # WFS types do not say their geometry up front: assumed polygons, chat 8 checks
        if gap: rows.append({'name': (title or nm)[:70], 'type': nm[:80], 'geom': 'unknown (WFS)', 'gap': gap, 'is': why + ' (geometry not read)'})
    add_lead(leads, cc, base, 'WFS ' + host_of(base), prov or host_of(base), 'WFS capabilities', lic, '', rows, known, govwords, f'{len(types)} feature types listed')
    return f'{base}: {len(types)} feature types, {len(rows)} look like park layers'


def ogc_collections(base, cc, leads, known, govwords):
    """OGC API - Features: /collections lists the collections (id, title); metadata only."""
    j = get(base.rstrip('/') + '/collections', {'f': 'json'}, raw=False)
    cols = j.get('collections') or []
    rows = []
    for c in cols[:300]:
        nm, ti = str(c.get('id') or ''), str(c.get('title') or '')
        gap, why = classify(ti or nm, 'Polygon', ['name'], force=key_of(base) in KG_NOW)
        if gap: rows.append({'name': (ti or nm)[:70], 'type': nm[:80], 'geom': 'unknown (OGC API)', 'gap': gap, 'is': why + ' (geometry not read)'})
    add_lead(leads, cc, base, 'OGC API ' + host_of(base), host_of(base), 'OGC API collections', '', '', rows, known, govwords, f'{len(cols)} collections listed')
    return f'{base}: {len(cols)} OGC API collections, {len(rows)} look like park layers'


def known_goods(c, cc, leads, known, govwords, done, log):
    """Oct 28 (chat 8 fix 1): every seeded known-good is opened DIRECTLY, before any crawl: a layer -> its service with that
    layer forced in; a service -> walked; a WFS / OGC API -> its list; a root that does not answer -> the service itself."""
    for u in c.get('known_good') or []:
        if late(): break
        try:
            if re.search(r'/rest/services/.+/(Feature|Map)Server/\d+$', u):
                svc, lid = u.rsplit('/', 1)
                ONLY_LAYER.setdefault(key_of(svc), set()).add(lid)
                walk_service(svc, cc, leads, known, govwords, 'known-good (chat 8)', note='known-good layer ' + lid); done.add(svc)
            elif re.search(r'/rest/services/.+/(Feature|Map)Server$', u):
                walk_service(u, cc, leads, known, govwords, 'known-good (chat 8)', note='known-good service'); done.add(u)
            elif re.search(r'/rest/services/?$', u): log.append({'step': 'known', 'what': walk_server(u.rstrip('/'), cc, leads, known, govwords, done)})
            else: log.append({'step': 'known', 'what': wfs_capabilities(u, cc, leads, known, govwords)}); done.add(u)
            log.append({'step': 'known', 'what': u, 'found': key_of(u) in leads or key_of(u.rsplit('/', 1)[0]) in leads})
        except Exception as e: STAT['errors'] += 1; log.append({'step': 'known', 'what': u, 'error': str(e)[:80]})  # noqa: BLE001


def agol_org(orgid, cc, leads, known, govwords, done):
    """Every map / feature service an official ArcGIS Online organisation publishes."""
    n = 0
    for start in (1, 101, 201):
        if late(): break
        try: j = get('https://www.arcgis.com/sharing/rest/search', {'q': f'orgid:{orgid} AND (type:"Feature Service" OR type:"Map Service")', 'num': 100, 'start': start})
        except Exception as e: STAT['errors'] += 1; return f'org {orgid}: {str(e)[:60]}'  # noqa: BLE001
        for it in j.get('results') or []:
            u = (it.get('url') or '').split('?')[0]
            if not re.search(r'/(Feature|Map)Server', u, re.I) or u in done or late(): continue
            org = ORG.get(orgid) or org_name(orgid)
            try:
                walk_service(u, cc, leads, known, govwords, 'ArcGIS Online (official org)', org, re.sub(r'<[^>]+>', ' ', it.get('licenseInfo') or '').strip(),
                             time.strftime('%Y-%m-%d', time.gmtime((it.get('modified') or 0) / 1000)) if it.get('modified') else '', it.get('title') or '')
                n += 1
            except Exception: STAT['errors'] += 1  # noqa: BLE001
            done.add(u)
        if len(j.get('results') or []) < 100: break
    return f'org {orgid} ({(ORG.get(orgid) or "")[:30]}): {n} services read'


ONLY_LAYER = {}   # service -> layer ids to open whatever the limit (known-goods)
KG_NOW = set()    # this country's known-good addresses (kept even from a non-government publisher, band B at most)
ORG = {}
def org_name(oid):
    if oid not in ORG:
        try: ORG[oid] = get(f'https://www.arcgis.com/sharing/rest/portals/{oid}').get('name') or ''
        except Exception: ORG[oid] = ''  # noqa: BLE001
    return ORG[oid]


def agol_search(c, cc, leads, known, govwords, done, log):
    names = ' OR '.join(f'"{n}"' for n in c['names'][:4])
    for kw in c['words'][:6]:
        if late(): break
        q = f'("{kw}") AND ({names}) AND (type:"Feature Service" OR type:"Map Service")'
        try: j = get('https://www.arcgis.com/sharing/rest/search', {'q': q, 'num': 50, 'sortField': 'numviews', 'sortOrder': 'desc'})
        except Exception as e: STAT['errors'] += 1; log.append({'agol': kw, 'error': str(e)[:60]}); continue  # noqa: BLE001
        hits = new = 0; rejected = {}
        for it in j.get('results') or []:
            hits += 1
            u = (it.get('url') or '').split('?')[0]
            oid = it.get('orgId') or ''
            if not re.search(r'/(Feature|Map)Server', u, re.I) or u in done: continue
            org = org_name(oid) if oid else ''
            if not official(org, u, cc, govwords): STAT['not_official'] += 1; rejected[org or oid or '?'] = rejected.get(org or oid or '?', 0) + 1; continue
            if SKIP.search(it.get('title') or ''): STAT['skipped'] += 1; continue
            if late(): break
            try:
                walk_service(u, cc, leads, known, govwords, 'ArcGIS Online search', org, re.sub(r'<[^>]+>', ' ', it.get('licenseInfo') or '').strip(),
                             time.strftime('%Y-%m-%d', time.gmtime((it.get('modified') or 0) / 1000)) if it.get('modified') else '', it.get('title') or '')
                new += 1
            except Exception: STAT['errors'] += 1  # noqa: BLE001
            done.add(u)
        log.append({'agol': kw, 'hits': hits, 'read': new, 'rejected_orgs': sorted(rejected.items(), key=lambda kv: -kv[1])[:3]})   # chat 8: who was turned away, so it can be graded


def catalog(kind, base, c, cc, leads, known, govwords, done, log):
    """National open-data catalogs: datasets whose RESOURCES point at a map service or WFS (read those, metadata only); a dataset
    that is only a download is listed as 'download, needs a loader' with its licence and date."""
    for kw in c['words'][:4]:
        if late(): break
        try:
            if kind == 'ckan':
                try: j = get(f'{base}/api/3/action/package_search', {'q': kw, 'rows': 30})
                except RuntimeError as e:
                    if 'HTTP 400' not in str(e): raise
                    j = get(f'{base}/api/3/action/package_search', {'q': ' AND '.join(kw.split()), 'rows': 20})   # Oct 28: data.gov.uk / e-gov answered 400 to the phrase
                items = (j.get('result') or {}).get('results') or []
            elif kind == 'datagouv': j = get(f'{base}/datasets/', {'q': kw, 'page_size': 30}); items = j.get('data') or []
            elif kind == 'dane': j = get(f'{base}/datasets', {'q': kw, 'per_page': 30}); items = [dict((x.get('attributes') or {}), id=x.get('id'), resources=[]) for x in j.get('data') or []]
            else: continue
        except Exception as e: STAT['errors'] += 1; log.append({'catalog': base, 'keyword': kw, 'error': str(e)[:60]}); continue  # noqa: BLE001
        hits = svc = dl = 0
        for p in items:
            hits += 1
            title = p.get('title') or ''
            if SKIP.search(title): STAT['skipped'] += 1; continue
            org = ((p.get('organization') or {}).get('title') if isinstance(p.get('organization'), dict) else p.get('organization')) or p.get('publisher') or ''
            if isinstance(org, dict): org = org.get('name') or ''
            lic = p.get('license_title') or p.get('license') or ''
            if isinstance(lic, dict): lic = lic.get('title') or lic.get('id') or ''
            date = (p.get('metadata_modified') or p.get('last_modified') or p.get('modified') or '')[:10]
            res = p.get('resources') or []
            urls = [r.get('url') or '' for r in res]
            svcs = [u.split('?')[0] for u in urls if re.search(r'/(Feature|Map)Server', u, re.I)]
            wfss = [u for u in urls if re.search(r'service=wfs|/wfs\b|/ows\b|geoserver', u, re.I)]
            if svcs:
                for u in svcs[:2]:
                    if u in done or late(): continue
                    try: walk_service(u, cc, leads, known, govwords, 'catalog ' + host_of(base), str(org), str(lic), date, title); svc += 1
                    except Exception: STAT['errors'] += 1  # noqa: BLE001
                    done.add(u)
            elif wfss:
                for u in wfss[:1]:
                    if u in done or late(): continue
                    wfs_capabilities(u, cc, leads, known, govwords); done.add(u); svc += 1
            elif PARKW.search(title) and official(str(org), base, cc, govwords) and any(re.search(r'shp|shape|gml|wfs|arcgis|geojson|geopackage|gpkg|kml|kmz|esri|zip', str(r.get('format') or '') + ' ' + str(r.get('url') or ''), re.I) for r in res):
                # Oct 28 (chat 8): only datasets whose resources are GIS files (the 13 Polish rows were statistics)
                dl += 1
                k = 'dl:' + (p.get('id') or title)[:60]
                page = p.get('page') or (f"{base.rsplit('/api', 1)[0]}/dataset/{p.get('name')}" if p.get('name') else base)
                leads.setdefault(k, {'url': page, 'cc': cc, 'title': title[:90], 'publisher': str(org)[:80], 'catalog': 'catalog ' + host_of(base), 'licence': str(lic)[:200],
                                     'date': date, 'found': RUN, 'gaps': ['outline?'], 'kind': 'download, needs a loader', 'formats': sorted({str(r.get('format') or '')[:10] for r in res})[:6],
                                     'layers': [], 'grade': 2, 'band': 'C', 'note': 'a file, not a service: chat 8 decides if it is worth a loader'})
        log.append({'catalog': base, 'keyword': kw, 'hits': hits, 'services_read': svc, 'downloads_listed': dl})


# ------------------------------------------------------------------ one country
EEA_CDDA = 'https://bio.discomap.eea.europa.eu/arcgis/rest/services/ProtectedSites/CDDA_Dyna_WM/MapServer'
NOT_EU = ('GB', 'NO', 'CH', 'AU', 'JP', 'NZ', 'AR', 'BR', 'CL', 'CN', 'CO', 'DO', 'KR', 'MX', 'PH', 'RU', 'TH', 'TR', 'ZA')


def run_country(cc, c, cfg, state, known):
    govwords = cfg['govwords']
    TRUSTED_ORGS.clear(); TRUSTED_ORGS.update(c.get('official_orgs') or [])
    st = state['countries'].setdefault(cc, {'status': 'started', 'started': RUN, 'done': [], 'log': [], 'steps': []})
    leads = load(OUT / f'leads-{cc}.json', {}).get('leads') or {}
    done = set(st['done']); log = st['log']
    steps = ['known', 'servers', 'wfs', 'orgs', 'catalogs', 'downloads', 'search', 'eea']
    KG_NOW.clear(); KG_NOW.update(key_of(u) for u in c.get('known_good') or []); KG_NOW.update(key_of(u.rsplit('/', 1)[0]) for u in c.get('known_good') or [] if re.search(r'/\d+$', u))
    for step in steps:
        if step in st['steps'] or late(): continue
        if step == 'known':
            known_goods(c, cc, leads, known, govwords, done, log)
        elif step == 'downloads':
            # Oct 28 (chat 8): official FILE downloads from the survey (Japan's MLIT A10): listed by hand, never fetched
            for dlu in c.get('downloads') or []:
                leads.setdefault('dl:' + dlu['url'], {'url': dlu['url'], 'cc': cc, 'title': dlu.get('title', '')[:90], 'publisher': dlu.get('publisher', ''), 'catalog': 'survey (chat 8)',
                                                     'licence': dlu.get('licence', ''), 'date': dlu.get('date', ''), 'found': RUN, 'gaps': ['outline?'], 'kind': 'download, needs a loader',
                                                     'layers': [], 'grade': 3, 'band': 'B', 'note': 'an official file download, not a service: needs a loader (chat 8 decides)'})
        elif step == 'orgs':
            for o in c.get('agol_orgs') or []:
                if late(): break
                log.append({'step': 'org', 'what': agol_org(o, cc, leads, known, govwords, done)})
        elif step == 'servers':
            for root in c.get('servers') or []:
                if late(): break
                if re.search(r'arcgis\.com', root): continue   # AGOL orgs are walked above
                log.append({'step': 'server', 'what': walk_server(root, cc, leads, known, govwords, done)})
        elif step == 'wfs':
            for u in c.get('ogc') or []:
                if late(): break
                if u in done: continue
                log.append({'step': 'wfs', 'what': wfs_capabilities(u, cc, leads, known, govwords)}); done.add(u)
        elif step == 'catalogs':
            for kind, base in c.get('catalogs') or []:
                if late(): break
                catalog(kind, base, c, cc, leads, known, govwords, done, log)
        elif step == 'search':
            agol_search(c, cc, leads, known, govwords, done, log)
        elif step == 'eea':
            if c.get('stage') == 1 and cc not in NOT_EU:   # Oct 29 (Fable c, chat 8): EVERY EU country gets the EEA nationally designated areas layer as a lead
                restricted = cc in ('EE', 'IE', 'TR')
                leads['eea-cdda:' + cc] = {'url': EEA_CDDA, 'cc': cc, 'title': f"EEA nationally designated areas (CDDA / NatDA): {c['name']} rows", 'publisher': 'European Environment Agency',
                                           'catalog': 'EEA (every member state)', 'licence': 'EEA standard re-use policy (credit the EEA)' if not restricted else 'EEA says some sites of this country may not be redistributed',
                                           'date': '', 'found': RUN, 'gaps': ['outline'], 'layers': [], 'grade': 3 if not restricted else 1, 'band': 'B' if not restricted else 'C',
                                           'note': f"filter the layer by the country code ({cc}); one official layer covers every member state" + ('; LICENCE: list only, never store' if restricted else '')}
            if c.get('stage') == 1 and cc not in ('GB', 'NO', 'CH', 'AU', 'JP') and not state.get('eea_done'):
                log.append({'step': 'eea', 'what': walk_server('https://bio.discomap.eea.europa.eu/arcgis/rest/services', cc, leads, known, govwords, done)})
                state['eea_done'] = RUN
        if not late(): st['steps'].append(step)
        st['done'] = sorted(done)
        save_country(cc, c, leads, st)
    if len(st['steps']) == len(steps):
        seeded = len(c.get('servers') or []) + len(c.get('ogc') or []) + len(c.get('agol_orgs') or []) + len(c.get('known_good') or [])
        own = [k for k in leads if not str(k).startswith('eea-cdda:')]
        errs = [l for l in (st.get('log') or []) if l.get('error') and (l.get('catalog') or l.get('agol'))]
        st['status'] = 'done' if (seeded or own) else ('nothing seeded: not searched (EEA lead only)' if leads else 'nothing seeded: not searched')   # Oct 29 (Fable b): never 'done, 0 leads'
        if not own and errs: st['status'] += f' · {len(errs)} catalog / search errors (see failures)'
        st['finished'] = RUN
    else: st['status'] = 'paused (out of time, will carry on)'
    save_country(cc, c, leads, st)
    return leads, st


def save_country(cc, c, leads, st):
    kg_found, kg_missed = [], []
    for u in c.get('known_good') or []:
        (kg_found if key_of(u) in leads or key_of(u) in KNOWN else kg_missed).append(u)
    bands = {b: sum(1 for v in leads.values() if v.get('band') == b) for b in 'ABC'}
    save(OUT / f'leads-{cc}.json', {'about': f"World harvester leads for {c['name']} (official park GIS only; leads for chat 8, never added to the key by the bot).",
                                    'cc': cc, 'date': RUN, 'status': st['status'], 'steps_done': st['steps'], 'bands': bands,
                                    'failures': [l for l in (st.get('log') or []) if l.get('error')][-20:],   # chat 8: catalog / search errors are FAILURES, never '0 hits'
                                    'rejected_orgs': [l['rejected_orgs'] for l in (st.get('log') or []) if l.get('rejected_orgs')][-6:],
                                    'known_good_found': kg_found, 'known_good_missed': kg_missed, 'known_log': [l for l in (st.get('log') or []) if l.get('step') == 'known'][-30:],
                                    'leads': dict(sorted(leads.items(), key=lambda kv: (-kv[1].get('grade', 0), kv[1].get('title', ''))))})


KNOWN = set()
BEFORE = {}
START_ISO = time.strftime('%Y-%m-%dT%H:%MZ', time.gmtime())


def main():
    cfg = load(OUT / 'countries.json', {})
    if not cfg.get('countries'): notice('no countries.json: run kpc_world_seed.py first'); return
    state = load(OUT / 'state.json', {'about': 'World harvester progress (resumable).', 'countries': {}})
    global KNOWN; KNOWN = already_read()
    want = [x.upper() for x in (os.environ.get('COUNTRIES') or '').replace(',', ' ').split()]
    queue = sorted(cfg['countries'], key=lambda k: cfg['countries'][k].get('order', 99))
    if not want: want = [k for k in queue if state['countries'].get(k, {}).get('status') != 'done']
    done_now = []
    for cc in want:
        if late(): break
        c = cfg['countries'].get(cc)
        if not c: continue
        if os.environ.get('FRESH') == '1' and os.environ.get('COUNTRIES'):   # Oct 28 (chat 8 regrade): redo from nothing under the new rules
            state['countries'][cc] = {'status': 'started', 'started': RUN, 'done': [], 'log': [], 'steps': [], 'redo': RUN}
            save(OUT / f'leads-{cc}.json', {'leads': {}})
        elif state['countries'].get(cc, {}).get('status') == 'done' and os.environ.get('COUNTRIES'): state['countries'][cc]['steps'] = []   # a named country is redone
        for h in list(DEAD): pass
        BEFORE[cc] = len(load(OUT / f'leads-{cc}.json', {}).get('leads') or {})
        leads, st = run_country(cc, c, cfg, state, KNOWN)
        done_now.append(f"{cc} {st['status'].split(' (')[0]}: {len(leads)} leads (A {sum(1 for v in leads.values() if v.get('band')=='A')}), known-good found {len(load(OUT / f'leads-{cc}.json', {}).get('known_good_found') or [])} of {len(c.get('known_good') or [])}")
        save(OUT / 'state.json', state)
    try:
        save(OUT / 'last_run.json', {'about': "One row per harvester run (Fable a / chat 8 wish 6): 'not redone' and 'redone, same answer' look different.",
                                     'run_id': os.environ.get('GITHUB_RUN_ID') or 'local', 'started': START_ISO, 'finished': time.strftime('%Y-%m-%dT%H:%MZ', time.gmtime()),
                                     'countries': {cc: {'leads_before': BEFORE.get(cc), 'leads_after': len(load(OUT / f'leads-{cc}.json', {}).get('leads') or {}),
                                                        'status': state['countries'].get(cc, {}).get('status')} for cc in BEFORE}})
    except Exception as e: notice(f'last_run.json not written: {e}')  # noqa: BLE001
    state['last_run'] = {'date': RUN, 'stats': STAT, 'countries': done_now, 'dead_servers': sorted(DEAD),
                         'robots_refused': ROBOTS_REFUSED, 'robots_said': {h: ROBOTS_SAID.get(h, '') for h in ROBOTS_REFUSED},
                         'robots_exempted_hosts (HQ ruling Oct 27: ArcGIS REST API paths only)': ROBOTS_EXEMPTED}
    save(OUT / 'state.json', state)
    # the people-readable top list across every country
    rows = []
    for f in OUT.glob('leads-*.json'):
        d = load(f, {})
        rows += [(v.get('grade', 0), d.get('cc'), v) for v in (d.get('leads') or {}).values()]
    rows.sort(key=lambda t: (-t[0], t[1]))
    md = ['# World harvester: top leads (official park GIS outside North America)', f'Last run {RUN}. Leads only: chat 8 grades them; nothing here is in the key. WDPA never used.', '',
          '| Band | Country | Title | What it is | Publisher | Licence | Date | Address |', '|---|---|---|---|---|---|---|---|']
    for g, cc, v in rows[:150]:
        md.append(f"| {v.get('band')} | {cc} | {v.get('title', '')[:50].replace('|', '/')} | {'; '.join(r.get('is', '') for r in v.get('layers', [])[:2])[:70].replace('|', '/')} | "
                  f"{v.get('publisher', '')[:36].replace('|', '/')} | {(v.get('licence') or v.get('licence_note') or '')[:40].replace('|', '/')} | {v.get('date', '')} | {v['url']} |")
    md += ['', '## Last run', '```', json.dumps(state['last_run'], ensure_ascii=False, indent=1)[:3000], '```']
    (OUT / 'leads.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    left = [k for k in queue if state['countries'].get(k, {}).get('status') != 'done']
    notice(f"{' · '.join(done_now) or 'nothing to do'} · requests {STAT['requests']} · {round((time.time() - T0) / 60)} min · {len(left)} countries still in the queue")


if __name__ == '__main__':
    try: main()
    except Exception as e:  # noqa: BLE001
        notice(f'stopped: {type(e).__name__}: {str(e)[:200]}')
    sys.exit(0)
