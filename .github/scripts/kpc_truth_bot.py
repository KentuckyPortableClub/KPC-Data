#!/usr/bin/env python3
"""PARK TRUTH CHECKER (Fable, chat 10 'bot workshop', Oct 28 2026; HQ's job 1). REVIEW LISTS ONLY: it never changes a key,
an outline or a card. For every US + Canada park that HAS an outline it asks three questions and writes the answers for people:

  1 ACREAGE: what size does the MANAGING AGENCY publish for this park (its own page, fact sheet or official map), and does our
    outline's size agree? More than ~15% apart = FLAGGED, with both numbers and the exact source line.
  2 HANDOVERS: does the agency's page or its news releases, or POTA's new / retired lists, say the park was transferred, deeded,
    'now managed by' someone else, or closed permanently? A hint is written down with its source; a person decides.
  3 SECOND-WITNESS SCORE per outline (0-8): POTA pin inside (0-2) + name match (0-2) + size match (0-2) + source agreement (0-2),
    WEAKEST FIRST, as chat 8's checking list.

Where our numbers come from (read, never written): data/us-key/US-XX.json (joined PAD-US / state records with acres; 'far' =
the pin check), data/ca-key/CA-XX.json, KPC-Links data/ky-answer-key.json + the ky-*.geojson files for Kentucky, and
data/boundary-score.json (chat 2's second witness: name / agency / second map). Official pages come from data/parkinfo
(column 1 = the park's page), data/parkinfo-web.json, data/docs/<area>.json (the documents bot's map + rules links, when it has
run), Kentucky's hand-checked 'web' + 'off' links, and data/truth/news-sources.json (agency newsroom pages, verified on first
use; chat 8 adds rows). Federal map-page patterns from chat 8's OFFICIAL_MAPS survey are used to find NPS / FWS unit pages.

Rules of the read (RULES FIRST: this bot decides nothing for members, so no rule sheet is needed; these are the reading rules):
  R1 only the managing agency's own site (or the same government's site) is a source for size; Wikipedia and such never.
  R2 a size 'agrees' when within 15% of ours; 'off' when every size on the page that looks like the park's TOTAL (near the park's
     name, or in a sentence that says encompasses / covers / consists / total / '-acre park') is more than 15% away;
     'unsure' when sizes were found but none is clearly the park's total; 'no size on page' otherwise. Our size 'unknown' when
     the key holds records without acres (state layers that give none): no verdict, listed apart.
  R3 the TOLERANCE is 15% (Brandon: 'more than ~15% off'); G-M5's 25% / 500 acres stays the OBSERVATIONS-LOG threshold.
  R4 handover words are HINTS, written with the sentence and the source; the bot applies nothing (same as the documents bot).
  R5 a park retired by POTA keeps its row, marked 'retired by POTA <date>', so a person can see the outline still exists.
  R6 Kentucky's test cases must pass before the long run: Levi Jackson (US-1264: 722 vs 896 acres) flagged 'off';
     Otter Creek (US-8144) carries a handover hint naming Meade County.
Manners: kpc_manners.py (robots, 2 s per host, back-off, three strikes = a day's rest); PDFs by range (first 400 KB).
Resumable: a park checked within REFRESH_DAYS (7) is skipped; MINUTES (55) per chunk; never fails (exit 0 always).

Env: AREAS='US-KY US-TN' (blank = the next unfinished areas in queue order) · MINUTES · LINKS (KPC-Links checkout, default
     'links') · OUT (data/truth) · REFRESH_DAYS · TEST=1 (Kentucky gate: prints PASS/FAIL as a notice and writes state['test'])
"""
import csv, json, math, os, pathlib, re, sys, time, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kpc_manners import Manners, page_text, links_in, pdf_text  # noqa: E402

OUT = pathlib.Path(os.environ.get('OUT') or 'data/truth')
LINKS = pathlib.Path(os.environ.get('LINKS') or 'links')
T0 = time.time(); LIMIT = float(os.environ.get('MINUTES') or 55) * 60
REFRESH_DAYS = int(os.environ.get('REFRESH_DAYS') or 7)
TOL = 0.15
PDF_FIRST = 400_000
TODAY = time.strftime('%Y-%m-%d')
VER = 1
QUEUE = ['US-KY',
         'US-TN', 'US-NC', 'US-VA', 'US-WV', 'US-GA', 'US-AL', 'US-SC', 'US-FL', 'US-MS',
         'US-IN', 'US-IL', 'US-MO', 'US-WI', 'US-MN', 'US-IA', 'US-ND', 'US-SD',
         'US-PA', 'US-NY', 'US-NJ', 'US-CT', 'US-RI', 'US-MA', 'US-VT', 'US-NH', 'US-ME', 'US-MD', 'US-DE', 'US-DC',
         'US-AR', 'US-LA', 'US-OK', 'US-TX', 'US-KS', 'US-NE',
         'US-CO', 'US-WY', 'US-ID', 'US-MT', 'US-NV', 'US-AZ', 'US-NM',
         'US-CA', 'US-OR', 'US-WA', 'US-AK', 'US-HI', 'US-MI', 'US-OH', 'US-UT',
         'CA-ON', 'CA-QC', 'CA-NB', 'CA-NS', 'CA-PE', 'CA-NL',
         'CA-MB', 'CA-SK', 'CA-AB', 'CA-BC', 'CA-YT', 'CA-NT', 'CA-NU']
STAT = {'parks': 0, 'with_outline': 0, 'size_agree': 0, 'size_off': 0, 'size_unsure': 0, 'no_size': 0, 'ours_unknown': 0,
        'handover_hints': 0, 'retired': 0, 'pages_read': 0, 'skipped_fresh': 0, 'errors': 0}
M = None

# ---- reading sizes
NUM = r'(\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?(?:\s*million)?)'
UNIT = r'(acres?|ac\b|hectares?|\bha\b|square\s+(?:miles?|kilomet(?:er|re)s?)|sq\.?\s*(?:mi|km)\b|km\s*²|km2\b|mi\s*²)'
SIZE = re.compile(NUM + r'\s*[-–\s]?\s*' + UNIT, re.I)
SIZE2 = re.compile(r'(?:acreage|area|size|total area|land area|park area)\s*[:=]?\s*' + NUM + r'\s*' + UNIT + '?', re.I)
TOTALWORD = re.compile(r'encompass|cover|consist|compris|total|spans|protects|includes|spread over|acre (?:park|area|refuge|forest|preserve|reserve|site|tract|property|wma|wildlife|recreation|lake|monument|seashore|lakeshore)|'
                       r'(?:park|area|refuge|forest|preserve|reserve|site|tract|property|monument|seashore|lakeshore|wma|lands?) (?:of|is|has|contains|covers|totals?|encompasses|includes) ', re.I)
NOTTOTAL = re.compile(r'\blake\b.*\bacre|acre[- ]lake|reservoir|pond|campground|campsite|parking|picnic|golf|cemetery|garden|lawn|field|pool|beach|marsh of|wetland of|per acre|acre[- ]feet|acre feet|acres? (?:of|in) (?:water|lake|pond|wetland|crop|timber|hunting|fields?)|'
                       r'burn|harvest|logged|planted|restored|treated|easement|acquired|purchas|added|expansion|donat', re.I)
HANDOVER = re.compile(r'\b((?:transferr?ed|transfer of|handed over|turned over|conveyed|deeded|donated|sold|ceded|leased|given|gift(?:ed)?)\s+(?:[^.;\n]{0,80}?\s)?(?:back )?(?:to|from)\s+(?:the\s+)?(?:city|county|town|village|parish|state|commonwealth|municipality|tribe|nation|district|authority|university|foundation|trust|conservancy|audubon|[A-Z][\w.&\'-]+(?:\s+[A-Z][\w.&\'-]+){0,4})[^.;\n]{0,90})', re.I)
MANAGED = re.compile(r'\b((?:is |are |now |currently |will be |has been )?(?:managed|operated|owned|maintained|administered|run|overseen)\s+(?:and (?:operated|maintained|managed) )?(?:jointly )?by\s+(?:the\s+)?[A-Z][\w.&\'-]+(?:\s+(?:of|and|&|for|the|[A-Z][\w.&\'-]+)){0,7})', re.I)
CLOSED = re.compile(r'\b((?:closed|closing|will close|has closed)\s+permanently|permanently\s+closed|no longer open to the public|is now closed to (?:the )?public|has been decommissioned|ceased operations|no longer (?:a |an )?(?:state |national )?(?:park|refuge|wildlife area|recreation area))[^.;\n]{0,80}', re.I)
NEWNAME = re.compile(r'\b((?:renamed|formerly (?:known as|called)|now (?:known as|called)|new name)[^.;\n]{0,80})', re.I)
KINDW = re.compile(r'\b(state|national|provincial|park|parks|forest|wildlife|management|area|areas|recreation|recreational|conservation|nature|natural|preserve|reserve|refuge|historic|historical|site|game|land|lands|wma|sp|sra|sf|nwr|trail|the|of|and|at|county|city|regional|unit|access|public|fishing|lake|hunting|outdoor|memorial|monument|wilderness|road)\b')
SOFT404 = re.compile(r'page not found|404 error|error 404|the page you (?:requested|are looking for)|no longer available|has been (?:moved|removed)|sign in to continue|log ?in required|access denied', re.I)


def notice(m): print('::notice title=Park truth checker::' + str(m).replace('\n', ' ')[:900], flush=True)
def late(): return time.time() - T0 > LIMIT
def load(p, d):
    try: return json.load(open(p, encoding='utf-8'))
    except Exception: return d  # noqa: BLE001
def save(p, obj):
    pathlib.Path(p).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(p).write_text(json.dumps(obj, ensure_ascii=False, indent=1, sort_keys=True) + '\n', encoding='utf-8')
def low(x): return ' '.join(re.sub(r'[^a-z0-9 ]', ' ', str(x or '').lower().replace('&', ' and ')).split())
def core(x): return ' '.join(KINDW.sub(' ', low(x)).split())
def host_of(u): return urllib.parse.urlparse(u).netloc.lower().split(':')[0]
def base_host(h): return re.sub(r'^(www\d?|m)\.', '', h)


def to_acres(n, unit):
    mult = 1_000_000 if 'million' in str(n).lower() else 1
    try: v = float(re.sub(r'[^0-9.]', '', str(n).lower().replace('million', ''))) * mult
    except Exception: return None  # noqa: BLE001
    u = unit.lower().replace(' ', '')
    if u.startswith('acre') or u == 'ac': return v
    if u.startswith('hectare') or u == 'ha': return v * 2.47105
    if u.startswith('squaremile') or u.startswith('sq.mi') or u.startswith('sqmi') or u.startswith('mi'): return v * 640
    if 'km' in u: return v * 247.105
    return v


def sizes_in(text, name):
    """Every size mention in a page: [(acres, 'n unit', line, looks_total)]. looks_total = near the park's name words or in a
    'total' sentence and NOT an obvious part (a lake, a campground, a purchase)."""
    out = []; seen = set()
    cn = [w for w in core(name).split() if len(w) > 2][:3]
    for rx in (SIZE, SIZE2):
        for m in rx.finditer(text):
            n, unit = m.group(1), (m.group(2) or 'acres')
            a = to_acres(n, unit)
            if a is None or a < 0.5 or a > 50_000_000: continue
            s = max(0, m.start() - 110); e = min(len(text), m.end() + 110)
            line = ' '.join(text[s:e].split())
            key = (round(a), line[:40])
            if key in seen: continue
            seen.add(key)
            near = text[max(0, m.start() - 160):m.end() + 60].lower()
            looks = bool(TOTALWORD.search(near)) or any(w in near for w in cn)
            if NOTTOTAL.search(near): looks = False
            out.append((round(a, 1), f'{n} {unit}', line, looks))
            if len(out) >= 12: return out
    return out


def off_by(ours, theirs):
    if not ours or not theirs: return None
    return abs(ours - theirs) / theirs


def judge(ours, sizes):
    """(verdict, chosen size tuple or None, pct). agree beats everything; else the best 'total-looking' size; else unsure."""
    if not sizes: return 'no size on page', None, None
    if not ours: return 'ours unknown', (sizes[0] if sizes else None), None
    agree = [s for s in sizes if off_by(ours, s[0]) is not None and off_by(ours, s[0]) <= TOL]
    if agree: return 'agree', min(agree, key=lambda s: off_by(ours, s[0])), round(off_by(ours, agree[0][0]) * 100)
    totals = [s for s in sizes if s[3]]
    if totals:
        best = min(totals, key=lambda s: off_by(ours, s[0]))
        return 'off', best, round(off_by(ours, best[0]) * 100)
    best = min(sizes, key=lambda s: off_by(ours, s[0]))
    return 'unsure', best, round(off_by(ours, best[0]) * 100)


# ---- our outlines
def poly_acres(geom):
    """Acres of a GeoJSON polygon / multipolygon (equirectangular equal-area approximation, good to ~1%)."""
    def ring(r):
        if len(r) < 3: return 0.0
        lat0 = sum(p[1] for p in r) / len(r); kx = 111320 * math.cos(math.radians(lat0)); ky = 110540
        a = 0.0
        for i in range(len(r)):
            x1, y1 = r[i][0] * kx, r[i][1] * ky; x2, y2 = r[(i + 1) % len(r)][0] * kx, r[(i + 1) % len(r)][1] * ky
            a += x1 * y2 - x2 * y1
        return abs(a) / 2
    t = geom.get('type'); c = geom.get('coordinates') or []
    polys = c if t == 'MultiPolygon' else [c] if t == 'Polygon' else []
    m2 = 0.0
    for p in polys:
        if not p: continue
        m2 += ring(p[0]) - sum(ring(h) for h in p[1:])
    return m2 / 4046.856


def point_in(la, lo, geom):
    t = geom.get('type'); c = geom.get('coordinates') or []
    polys = c if t == 'MultiPolygon' else [c] if t == 'Polygon' else []
    for p in polys:
        inn = False
        for ri, r in enumerate(p):
            hit = False
            for i in range(len(r)):
                x1, y1 = r[i]; x2, y2 = r[(i + 1) % len(r)]
                if (y1 > la) != (y2 > la) and lo < (x2 - x1) * (la - y1) / ((y2 - y1) or 1e-12) + x1: hit = not hit
            if ri == 0: inn = hit
            elif hit: inn = False
        if inn: return True
    return False


KY_LAYERS = {'ky-state-parks.geojson': 'Kentucky State Parks (DGI)', 'ky-hunting-areas.geojson': 'KDFWR public hunting areas', 'ky-fws.geojson': 'FWS refuges',
             'ky-nps.geojson': 'NPS units', 'ky-nature-preserves.geojson': 'Office of Kentucky Nature Preserves', 'ky-natural-areas.geojson': 'KY natural areas',
             'ky-padus-parks.geojson': 'USGS PAD-US (fallback)', 'ky-usace.geojson': 'Corps of Engineers', 'ky-wilderness.geojson': 'wilderness', 'ky-wild-rivers.geojson': 'KY wild rivers',
             'ky-dbnf-owned.geojson': 'Forest Service Basic Ownership (owned land)', 'ky-pine-mountain.geojson': 'Pine Mountain trail', 'ky-dawkins.geojson': 'Dawkins Line'}
_KYF = None


def ky_features():
    global _KYF
    if _KYF is None:
        _KYF = []
        for f, src in KY_LAYERS.items():
            g = load(LINKS / f, {})
            for x in g.get('features') or []:
                p = x.get('properties') or {}
                _KYF.append((f, src, p, x.get('geometry') or {}))
    return _KYF


def ours_ky(ref, park, ak):
    """Kentucky: the answer key's tracts (acres) + the geojson features (name / ref match, pin check)."""
    tr = [t for t in ((ak.get(ref) or {}).get('tracts') or []) if not re.search(r'proclamation|outer line|purchase', str(t[3] if len(t) > 3 else ''), re.I)]   # the park = owned land, never the outer line
    acres = sum(t[2] for t in tr if len(t) > 2 and isinstance(t[2], (int, float))) if tr else 0
    pieces = [[t[0], t[1], t[2], t[3]] for t in tr if len(t) > 3]
    la, lo = park.get('la'), park.get('lo')
    feats = [(f, src, p, g) for f, src, p, g in ky_features() if p.get('ref') == ref or (tr and any(core(p.get('NAME', '')) == core(t[1]) for t in tr))]
    if not feats and not tr: return None
    pin = None; manager = ''; geo_acres = 0.0
    for f, src, p, g in feats:
        if la is not None and g and point_in(la, lo, g): pin = 'inside'
        manager = manager or p.get('MANAGER') or p.get('MANG') or ''
        try: geo_acres += poly_acres(g) if g.get('type') in ('Polygon', 'MultiPolygon') else 0
        except Exception: pass  # noqa: BLE001
    if pin is None and feats: pin = 'outside'
    if not acres and geo_acres: acres = round(geo_acres)
    return {'acres': round(acres), 'pieces': pieces or [[f, p.get('NAME', ''), round(poly_acres(g)) if g.get('type') in ('Polygon', 'MultiPolygon') else 0, 'name'] for f, s, p, g in feats][:6],
            'src': ', '.join(sorted({KY_LAYERS.get(f, f) for f, s, p, g in feats})) or (tr[0][0] if tr else ''), 'pin': pin or 'not checked', 'manager': manager, 'unknown_pieces': 0}


def ours_key(rec):
    """US / Canada key record -> our outline summary (acres summed from the joined records; 0-acre records counted as unknown)."""
    ms = rec.get('m') or []
    if not ms: return None
    acres = 0.0; unknown = 0; pieces = []
    for r in ms:
        a = r[2] if len(r) > 2 and isinstance(r[2], (int, float)) else 0
        if a and a > 0: acres += a
        else: unknown += 1
        pieces.append([r[0], r[1], a, (r[3] if len(r) > 3 else '')[:60]])
    far = rec.get('far')
    pin = 'inside' if not far else 'just outside' if far == 'edge' else 'well outside' if far in ('well outside', 'outside') else str(far)
    srcs = sorted({str(p[3]).split('·')[-1].strip() for p in pieces if '·' in str(p[3])}) or (['USGS PAD-US'] if any(isinstance(p[0], int) for p in pieces) else [])
    return {'acres': round(acres), 'pieces': pieces[:8], 'src': ', '.join(srcs)[:160], 'pin': pin, 'manager': '', 'unknown_pieces': unknown}


# ---- official pages
NPS_UNIT = re.compile(r'nps\.gov/([a-z]{4})(?:/|$)')
FWS_UNIT = re.compile(r'fws\.gov/refuge/([a-z0-9-]+)')
BAD_PAGE = re.compile(r'pota\.app|wikipedia|facebook|google|tripadvisor|yelp|alltrails|recreation\.gov/camping', re.I)


def candidate_pages(ref, park, web, docs, ky):
    """Official pages for one park, best first, de-duplicated; never anything off an agency / government site."""
    out = []
    def add(u, why):
        u = (u or '').strip()
        if not u.startswith('http') or BAD_PAGE.search(u): return
        if u not in [x[0] for x in out]: out.append((u, why))
    k = ky.get(ref) or {}
    add(k.get('web'), "the park's page (Kentucky answer key)")
    add(park.get('web'), "the park's page (data/parkinfo)")
    d = (docs.get(ref) or {})
    add((d.get('page') or ''), "the park's page (documents bot)")
    w = web.get(ref) or {}
    add(w.get('web'), "the park's page (parkinfo-web)")
    for u, why in ((k.get('off'), 'official map (Kentucky answer key)'), (k.get('off2'), 'second official map (Kentucky answer key)'), (((d.get('map') or {}).get('url')), 'official map (documents bot)'), (w.get('map'), 'official map (parkinfo-web)')):
        if u and str(u).lower().split('?')[0].endswith('.pdf'): add(u, why)
    for u in (((d.get('rules') or {}).get('url')),):
        add(u, 'rules page (documents bot)')
    # federal unit pages chat 8 found readable (OFFICIAL_MAPS FEDERAL_desk: NPS + FWS READY)
    for u, why in list(out):
        m = NPS_UNIT.search(u)
        if m and 'nps.gov' in u:
            add(f'https://www.nps.gov/{m.group(1)}/learn/management/statistics.htm', 'NPS park statistics page')
            add(f'https://www.nps.gov/{m.group(1)}/learn/news/newsreleases.htm', 'NPS news releases')
        m = FWS_UNIT.search(u)
        if m and 'fws.gov' in u:
            add(f'https://www.fws.gov/refuge/{m.group(1)}/about-us', 'FWS refuge about page')
    return out[:6]


def read_page(u):
    """-> (status, kind, text). PDFs by range (first 400 KB)."""
    looks_pdf = u.lower().split('?')[0].endswith('.pdf')
    st, hd, body, final = M.get(u, rng=(0, PDF_FIRST - 1) if looks_pdf else None)
    if st not in (200, 206): return (str(st) if not isinstance(st, int) else f'HTTP {st}'), '', ''
    STAT['pages_read'] += 1
    ct = (hd.get('content-type') or '').lower()
    if body[:5] == b'%PDF-' or 'application/pdf' in ct:
        return 'ok', 'pdf', pdf_text(body, 3)
    if looks_pdf: return 'opened, not a PDF', '', ''
    html = body.decode('utf-8', 'replace')
    t = page_text(html)
    if len(t) < 200 and SOFT404.search(t): return 'soft 404', 'page', ''
    return 'ok', 'page', t


def hints_in(text, name, src, why):
    out = []
    for rx, kind in ((HANDOVER, 'transfer'), (MANAGED, 'managed by'), (CLOSED, 'closed'), (NEWNAME, 'renamed')):
        for m in rx.finditer(text):
            s = max(0, m.start() - 100); e = min(len(text), m.end() + 100)
            line = ' '.join(text[s:e].split())
            if kind == 'managed by' and not re.search(r'(city|county|town|village|parish|municipal|tribe|nation|university|foundation|trust|conservancy|audubon|authority|district|corporation|company|association|club|church)', line, re.I):
                continue   # 'managed by the Division of Parks' is the normal case: only OTHER kinds of owner are hints
            out.append({'kind': kind, 'line': line[:300], 'src': src, 'why': why, 'date_hint': (re.search(r'(?:19|20)\d\d', line) or [None])[0] if re.search(r'(?:19|20)\d\d', line) else None})
            if len(out) >= 6: return out
    return out


# ---- news sources (agency newsrooms; each row verified on first use)
def news_hints(area, parks_by_core, news, nstate):
    """Read each newsroom index for this area once a run; link texts naming a park -> open the article -> handover words."""
    out = {}
    for row in [r for r in news if r.get('area') in (area, area[:2], 'ALL')]:
        u = row.get('url');
        if not u or late(): continue
        if (nstate.get(u) or {}).get('read', '') == TODAY: continue
        st, hd, body, final = M.get(u)
        html_links = []
        if st in (200, 206):
            html = body.decode('utf-8', 'replace'); html_links = links_in(html, final); st = 'ok'
            if len(page_text(html)) < 200 and SOFT404.search(page_text(html)): st = 'soft 404'
        else: st = str(st) if not isinstance(st, int) else f'HTTP {st}'
        nstate[u] = {'read': TODAY, 'status': st, 'links': len(html_links)}
        if st != 'ok': continue
        hits = 0
        for link, txt in html_links:
            c = core(txt)
            if len(c) < 5: continue
            for pc, ref in parks_by_core.items():
                if len(pc) >= 6 and (pc in c or c in pc) and len(c) >= 0.6 * len(pc):
                    if late() or hits > 12: break
                    hits += 1
                    st3, k3, t3 = read_page(link)
                    if st3 != 'ok': continue
                    hs = hints_in(t3, pc, link, f"agency news ({row.get('agency') or host_of(u)})")
                    hs = [h for h in hs if h['kind'] != 'managed by' or 'transfer' in t3.lower() or 'deed' in t3.lower()]
                    if hs: out.setdefault(ref, []).extend(hs[:3])
    return out


# ---- areas
def park_list(area):
    st = area[3:]
    if area.startswith('US-'):
        d = load(f'data/parkinfo/US-{st}.json', {}) or load(LINKS / f'data/parkinfo/US-{st}.json', {})
        P = {r: {'n': v[0], 'web': v[1] if len(v) > 1 else '', 't': v[2] if len(v) > 2 else '', 'la': v[5] if len(v) > 6 else None, 'lo': v[6] if len(v) > 6 else None} for r, v in (d.get('parks') or {}).items()}
        if st == 'KY':
            for x in load(LINKS / 'kpc-ky-data.json', {}).get('parks', []):
                if x.get('c'): P[x['c']] = {'n': x.get('n', ''), 'web': x.get('web') or '', 't': x.get('t', ''), 'la': x.get('la'), 'lo': x.get('lo')}
        return P
    d = load('data/parkinfo/CA.json', {}) or load(LINKS / 'data/parkinfo/CA.json', {})
    return {r: {'n': v[0], 'web': v[1] if len(v) > 1 else '', 't': v[2] if len(v) > 2 else '', 'la': v[5] if len(v) > 6 else None, 'lo': v[6] if len(v) > 6 else None} for r, v in (d.get('parks') or {}).items() if len(v) > 10 and v[10] == st}


def score_of(ours, verdict, bs):
    """0-8: pin (0-2) + name (0-2) + size (0-2) + source agreement (0-2). bs = boundary-score row [score, level, flag, why]."""
    why = (bs or ['', '', '', ''])[3] if bs else ''
    pin = {'inside': 2, 'just outside': 1}.get(ours.get('pin'), 0 if ours.get('pin') in ('well outside', 'outside') else 1)
    m = re.search(r'name (\d)/2', why); name = int(m.group(1)) if m else (2 if any(str(p[3]).startswith('name') for p in ours.get('pieces') or []) else 1)
    size = {'agree': 2, 'unsure': 1, 'no size on page': 1, 'ours unknown': 1, 'not read': 1}.get(verdict, 0)
    m2 = re.search(r'second map (\d)/2', why); m3 = re.search(r'agency (\d)/1', why)
    src = (int(m2.group(1)) if m2 else 0) + (int(m3.group(1)) if m3 else 0)
    src = min(2, src) if (m2 or m3) else 1
    return pin + name + size + src, {'pin': pin, 'name': name, 'size': size, 'source': src}


def one_park(ref, park, ours, web, docs, ky, retired, bs):
    r = {'n': park['n'], 't': park.get('t', ''), 'ours': ours, 'official': None, 'sizes': [], 'verdict': 'not read', 'pct': None,
         'handover': [], 'pages': [], 'checked': TODAY, 'ver': VER}
    if ref in retired:
        r['retired'] = retired[ref]; STAT['retired'] += 1
    pages = candidate_pages(ref, park, web, docs, ky)
    if not pages: r['verdict'] = 'no official page on file'; return r
    found = []
    for u, why in pages:
        if late(): break
        st, kind, text = read_page(u)
        r['pages'].append({'url': u, 'why': why, 'status': st})
        if st != 'ok' or not text: continue
        for s in sizes_in(text, park['n']): found.append(s + (u,))
        r['handover'].extend(hints_in(text, park['n'], u, why))
        if any(s[3] for s in found) and r['handover']: break
        if len(found) >= 4 and 'news' not in why: continue
    r['sizes'] = [{'acres': s[0], 'as': s[1], 'line': s[2], 'total_like': s[3], 'url': s[4]} for s in found[:8]]
    v, chosen, pct = judge(ours['acres'] if ours else 0, found)
    if ours and ours.get('unknown_pieces') and not ours.get('acres'): v = 'ours unknown'
    r['verdict'] = v; r['pct'] = pct
    if chosen: r['official'] = {'acres': chosen[0], 'as': chosen[1], 'line': chosen[2], 'url': chosen[4], 'read': TODAY}
    # a transfer hint from the land record itself: PAD-US says City / County / private while POTA calls it a state park
    mg = (ours or {}).get('manager') or ''
    if mg and re.search(r'city|county|local|private|ngo|non', mg, re.I) and re.search(r'state', park.get('t', ''), re.I):
        r['handover'].append({'kind': 'land record', 'line': f"our outline's land record says manager = {mg}, POTA calls it a {park.get('t')}", 'src': ours.get('src'), 'why': 'the outline source', 'date_hint': None})
    r['score'], r['score_parts'] = score_of(ours or {'pin': 'none', 'pieces': []}, v, bs)
    return r


def run_area(area, state, web, docs_all, ky, ak, retired, bscore, news):
    f = OUT / f'{area}.json'
    D = load(f, {'area': area, 'about': 'Park truth checker: official acreage vs our outline, handover hints, second-witness score. Review lists only: nothing here changes a key or a card.', 'parks': {}})
    parks = park_list(area)
    if not parks: notice(f'{area}: no park list'); state['areas'][area] = {'status': 'done', 'parks': 0, 'updated': TODAY}; return
    key = load(f'data/{"us" if area.startswith("US") else "ca"}-key/{area}.json', {}).get('parks') or {}
    docs = (docs_all.get(area) or {}).get('parks') or {}
    done = fresh = 0
    fresh_cut = time.strftime('%Y-%m-%d', time.gmtime(time.time() - REFRESH_DAYS * 86400))
    parks_by_core = {core(p['n']): ref for ref, p in parks.items()}
    for ref in sorted(parks):
        if late(): break
        old = D['parks'].get(ref)
        if old and old.get('ver', 0) >= VER and old.get('checked', '') >= fresh_cut: fresh += 1; STAT['skipped_fresh'] += 1; continue
        park = parks[ref]
        ours = ours_ky(ref, park, ak) if area == 'US-KY' else ours_key(key.get(ref) or {})
        STAT['parks'] += 1
        if not ours:
            D['parks'][ref] = {'n': park['n'], 't': park.get('t', ''), 'ours': None, 'verdict': 'no outline', 'checked': TODAY, 'ver': VER, 'handover': [], 'score': None}
            continue
        STAT['with_outline'] += 1
        try: D['parks'][ref] = one_park(ref, park, ours, web, docs, ky, retired, bscore.get(ref))
        except Exception as e:  # noqa: BLE001
            STAT['errors'] += 1
            D['parks'][ref] = {'n': park['n'], 'ours': ours, 'verdict': 'bot error: ' + str(e)[:80], 'checked': TODAY, 'ver': VER, 'handover': [], 'score': None}
        v = D['parks'][ref].get('verdict')
        STAT['size_agree' if v == 'agree' else 'size_off' if v == 'off' else 'size_unsure' if v == 'unsure' else 'ours_unknown' if v == 'ours unknown' else 'no_size'] += 1
        done += 1
    if not late():
        nstate = state.setdefault('news', {})
        try:
            for ref, hs in news_hints(area, parks_by_core, news, nstate).items():
                if ref in D['parks']:
                    D['parks'][ref].setdefault('handover', []).extend(hs)
        except Exception as e:  # noqa: BLE001
            STAT['errors'] += 1; notice(f'{area}: news read failed: {str(e)[:100]}')
    for ref, r in D['parks'].items():
        seen = set(); hs = []
        for h in r.get('handover') or []:
            k = (h.get('kind'), h.get('line', '')[:80])
            if k not in seen: seen.add(k); hs.append(h)
        r['handover'] = hs[:8]
    STAT['handover_hints'] += sum(1 for r in D['parks'].values() if r.get('handover'))
    D['read'] = TODAY; D['counts'] = counts(D)
    save(f, D)
    write_checklist(area, D)
    left = sum(1 for r in parks if r not in D['parks'])
    state['areas'][area] = {'status': 'done' if left == 0 else 'partial', 'parks': len(parks), 'checked': len(D['parks']), 'left': left, 'updated': TODAY, 'counts': D['counts']}
    notice(f"{area}: {done} parks checked this chunk ({fresh} fresh, {left} left) · {D['counts']}")


def counts(D):
    c = {'parks': len(D['parks']), 'with_outline': 0, 'agree': 0, 'off': 0, 'unsure': 0, 'no_size': 0, 'ours_unknown': 0, 'no_page': 0, 'handover_hints': 0, 'retired': 0, 'weak': 0}
    for r in D['parks'].values():
        if r.get('ours'): c['with_outline'] += 1
        v = r.get('verdict', '')
        c['agree' if v == 'agree' else 'off' if v == 'off' else 'unsure' if v == 'unsure' else 'ours_unknown' if v == 'ours unknown' else 'no_page' if 'no official page' in v else 'no_size'] += 1 if v != 'no outline' else 0
        if r.get('handover'): c['handover_hints'] += 1
        if r.get('retired'): c['retired'] += 1
        if r.get('score') is not None and r['score'] <= 4: c['weak'] += 1
    return c


def write_checklist(area, D):
    """chat 8's checking list: weakest outline first (CSV), one row per park with an outline."""
    rows = []
    for ref, r in D['parks'].items():
        if not r.get('ours'): continue
        o = r['ours']; of = r.get('official') or {}
        rows.append([r.get('score') if r.get('score') is not None else '', ref, r.get('n', ''), r.get('t', ''), o.get('pin', ''), r.get('verdict', ''), o.get('acres', ''), of.get('acres', ''), r.get('pct', ''),
                     of.get('url', ''), (of.get('line') or '')[:200], ' | '.join(h['kind'] + ': ' + h['line'][:120] for h in (r.get('handover') or [])[:2]), o.get('src', '')[:80],
                     json.dumps(r.get('score_parts') or {})])
    rows.sort(key=lambda x: (x[0] if x[0] != '' else 99, x[1]))
    p = OUT / f'checklist-{area}.csv'
    with open(p, 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh); w.writerow(['score 0-8 (weakest first)', 'ref', 'park', 'POTA type', 'POTA pin', 'size verdict', 'our acres', 'agency acres', 'pct off', 'agency source', 'source line', 'handover hints', 'our outline source', 'score parts'])
        w.writerows(rows)


def review(state):
    """data/truth/review.md: what a person should look at, per area: the flagged sizes, the handover hints, the weakest outlines."""
    L = ['# Park truth checker: review (review lists only; nothing here changes a key or a card)', '',
         f'Updated {TODAY}. Tolerance 15% (R3). Score 0-8 = POTA pin + name + size + source agreement; weakest first in checklist-<area>.csv.', '',
         '| area | parks | with outline | agree | OFF (>15%) | unsure | no size | ours unknown | handover hints | retired | weak (≤4) |', '|---|---|---|---|---|---|---|---|---|---|---|']
    for a in QUEUE:
        s = (state['areas'].get(a) or {})
        c = s.get('counts')
        if not c: continue
        L.append(f"| {a} | {c['parks']} | {c['with_outline']} | {c['agree']} | **{c['off']}** | {c['unsure']} | {c['no_size']} | {c['ours_unknown']} | {c['handover_hints']} | {c['retired']} | {c['weak']} |")
    for a in QUEUE:
        D = load(OUT / f'{a}.json', None)
        if not D: continue
        off = [(ref, r) for ref, r in D['parks'].items() if r.get('verdict') == 'off']
        hov = [(ref, r) for ref, r in D['parks'].items() if r.get('handover')]
        if not off and not hov: continue
        L += ['', f'## {a}', '']
        if off:
            L += ['**Size more than 15% off (our outline vs the agency):**', '']
            for ref, r in sorted(off, key=lambda x: -(x[1].get('pct') or 0))[:60]:
                of = r.get('official') or {}
                L.append(f"- {ref} {r['n']}: ours {r['ours']['acres']:,} ac vs agency {of.get('as', '')} ({r.get('pct')}% off) · [{host_of(of.get('url', ''))}]({of.get('url', '')}) · “{(of.get('line') or '')[:160]}”")
            if len(off) > 60: L.append(f'- … {len(off) - 60} more in {a}.json')
        if hov:
            L += ['', '**Handover / closure hints (a person decides; nothing applied):**', '']
            for ref, r in hov[:60]:
                for h in r['handover'][:2]:
                    L.append(f"- {ref} {r['n']} · {h['kind']}: “{h['line'][:200]}” · [{host_of(h.get('src', ''))}]({h.get('src', '')})")
            if len(hov) > 60: L.append(f'- … {len(hov) - 60} more in {a}.json')
    t = state.get('test')
    if t: L += ['', '## Kentucky test gate', '', f"- {t.get('when')}: **{t.get('result')}** · {t.get('why')}"]
    (OUT / 'review.md').write_text('\n'.join(L) + '\n', encoding='utf-8')


def ky_test(state):
    """R6: Levi Jackson flagged 'off' (722 vs 896) AND Otter Creek carries a Meade County hint."""
    D = load(OUT / 'US-KY.json', {'parks': {}})
    lj = D['parks'].get('US-1264') or {}; oc = D['parks'].get('US-8144') or {}
    a = lj.get('verdict') == 'off' and (lj.get('official') or {}).get('acres') and abs((lj['official']['acres']) - 896) < 60
    b = any(re.search(r'meade', (h.get('line') or ''), re.I) for h in (oc.get('handover') or []))
    why = f"Levi Jackson: verdict {lj.get('verdict')} ours {(lj.get('ours') or {}).get('acres')} agency {(lj.get('official') or {}).get('as')} · Otter Creek hints: {len(oc.get('handover') or [])} ({'Meade found' if b else 'no Meade County line'})"
    res = 'PASS' if (a and b) else 'FAIL'
    state['test'] = {'when': TODAY, 'result': res, 'why': why, 'levi_ok': bool(a), 'otter_ok': bool(b)}
    notice(f'KENTUCKY TEST {res}: {why}')
    print('TEST=' + res)


def main():
    global M
    OUT.mkdir(parents=True, exist_ok=True)
    state = load(OUT / 'state.json', {'areas': {}, 'hosts': {}, 'news': {}})
    M = Manners('park truth checker', state.get('hosts'))
    want = (os.environ.get('AREAS') or '').upper().split()
    areas = [a for a in want if a in QUEUE] if want else [a for a in QUEUE if (state['areas'].get(a) or {}).get('status') != 'done']
    if want and not areas: notice('no known area in AREAS'); return
    web = (load('data/parkinfo-web.json', {}) or load(LINKS / 'data/parkinfo-web.json', {})).get('parks') or {}
    docs_all = {a: load(f'data/docs/{a}.json', {}) for a in areas}
    kyd = {x['c']: x for x in load(LINKS / 'kpc-ky-data.json', {}).get('parks', []) if x.get('c')}
    ak = load(LINKS / 'data/ky-answer-key.json', {}).get('parks') or {}
    retired = {r: v.get('d', '') for r, v in (load(LINKS / 'data/retired-refs.json', {}).get('refs') or {}).items()}
    bscore = (load('data/boundary-score.json', {}) or load(LINKS / 'data/boundary-score.json', {})).get('parks') or {}
    news = load(OUT / 'news-sources.json', {}).get('sources') or []
    for area in areas:
        if late(): break
        run_area(area, state, web, docs_all, kyd, ak, retired, bscore, news)
    if os.environ.get('TEST') == '1': ky_test(state)
    state['hosts'] = M.resting()
    state['last'] = {'when': TODAY, 'areas': areas[:8], 'stat': STAT, 'manners': M.stat}
    save(OUT / 'state.json', state)
    review(state)
    left = [a for a in QUEUE if (state['areas'].get(a) or {}).get('status') != 'done']
    notice(f"done this chunk: {STAT} · manners {M.stat} · areas left: {len(left)}" + (f" (next {' '.join(left[:4])})" if left else ''))


if __name__ == '__main__':
    try: main()
    except Exception as e:  # noqa: BLE001
        import traceback; traceback.print_exc()
        notice(f'stopped: {e}')
    sys.exit(0)
