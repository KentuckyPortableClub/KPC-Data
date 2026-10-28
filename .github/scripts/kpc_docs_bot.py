#!/usr/bin/env python3
"""OFFICIAL-DOCUMENTS BOT (Fable, chat 2, Oct 28 2026; HQ 1:24 AM). A NEW bot, separate from everything else: for every POTA park
in the US + Canada it looks for the agency's OFFICIAL MAP (the link + its date), the RULES page, and who runs the park now, so a
card can one day link 'the official agency map' our notices tell people to check. It writes data/docs/<ST>.json (one file per
state / province) + data/docs/review.md (counts + samples for chat 8). NOTHING reaches a park card from here.

Where the answers come from, in order:
  1 the links already on file: data/parkinfo-web.json 'map' (the link harvester + HQ's hand lists), Kentucky's hand-checked
    'off' links in kpc-ky-data.json (the ANSWER KEY), the park's own page (data/parkinfo, column 1)
  2 the agency's LIST PAGES (data/docs/lists.json, from chat 8's OFFICIAL_MAPS survey): the page is READ and parks are matched by
    name; a file name is never guessed
  3 the park's own agency page, read for links that say 'map' (PDF first) and links that say 'rules / regulations / permits'
  4 federal rules pages by pattern (NPS Superintendent's Compendium, USFS alerts & orders, FWS rules & policies, Corps 36 CFR 327,
    Parks Canada 'Know before you go'), each one OPENED before it is kept
Map DATE (chat 8's date methods, the method is always written down): printed on the map (first page of the PDF, read with a
range request: never the whole file), the upload folder in the address (YYYY-MM), the file's version tail, the server's file
date, else the day we read it. 'Who runs it': the agency behind the host + what the page says ('managed by', 'transferred to'):
a HANDOVER is only ever a hint for a person (Otter Creek -> Meade County, July 2026).
NEEDS-A-BROWSER hosts (chat 8's list + any page that hides its links behind script): a second pass with headless Chromium
(BROWSER=1) clicks 'Download map' and reads script-built pages; download addresses are recorded, files are not kept.

Manners: these are websites, so robots.txt is obeyed everywhere; 1 request / 2 s per host; one area's hosts at a time; back-off
on 429 / 5xx; three strikes = that host rests a day (data/docs/state.json remembers); PDFs read by range (first 400 KB, 2 MB at
most); a User-Agent naming the club site. Resumable: a park checked in the last 30 days is not asked again. Never fails.

Env: AREAS='US-MO US-FL' (blank = the next unfinished areas in queue order) · MINUTES (default 55) · BROWSER=1 (the Chromium pass)
     · LINKS (the KPC-Links checkout, default 'links') · OUT (default data/docs) · SAMPLE=25 (Kentucky finder check size)
"""
import io, json, os, pathlib, re, sys, time, urllib.error, urllib.parse, urllib.request, urllib.robotparser

OUT = pathlib.Path(os.environ.get('OUT') or 'data/docs')
LINKS = pathlib.Path(os.environ.get('LINKS') or 'links')
T0 = time.time(); LIMIT = float(os.environ.get('MINUTES') or 55) * 60
BROWSER = os.environ.get('BROWSER') == '1'
UA = 'KPC park documents (https://kentuckyportableclub.github.io/KPC-Links/; ham radio club; 1 request per 2 s; reads maps and rules pages only)'
GAP = 2.0
STRIKES_OUT = 3
REFRESH_DAYS = 30
PDF_FIRST = 400_000
PDF_MAX = 2_000_000
TODAY = time.strftime('%Y-%m-%d')
STAT = {'requests': 0, 'parks': 0, 'maps_ok': 0, 'maps_found': 0, 'dates': 0, 'rules': 0, 'browser': 0, 'robots': 0, 'strikes': 0, 'errors': 0, 'skipped_fresh': 0}
LAST, ROBOTS, DEAD, STRIKE = {}, {}, {}, {}
ROBOTS_SAID, ROBOTS_REFUSED = {}, {}
QUEUE = ['US-KY',
         'US-TN', 'US-NC', 'US-VA', 'US-WV', 'US-GA', 'US-AL', 'US-SC', 'US-FL', 'US-MS',                     # southeast (2-fer region order)
         'US-IN', 'US-IL', 'US-MO', 'US-WI', 'US-MN', 'US-IA', 'US-ND', 'US-SD',                               # midwest
         'US-PA', 'US-NY', 'US-NJ', 'US-CT', 'US-RI', 'US-MA', 'US-VT', 'US-NH', 'US-ME', 'US-MD', 'US-DE', 'US-DC',   # northeast
         'US-AR', 'US-LA', 'US-OK', 'US-TX', 'US-KS', 'US-NE',                                                 # south central
         'US-CO', 'US-WY', 'US-ID', 'US-MT', 'US-NV', 'US-AZ', 'US-NM',                                        # mountain
         'US-CA', 'US-OR', 'US-WA', 'US-AK', 'US-HI', 'US-MI', 'US-OH', 'US-UT',                               # pacific + the three the regions leave out
         'CA-ON', 'CA-QC', 'CA-NB', 'CA-NS', 'CA-PE', 'CA-NL',                                                 # Canada east
         'CA-MB', 'CA-SK', 'CA-AB', 'CA-BC', 'CA-YT', 'CA-NT', 'CA-NU']                                        # Canada west
# hosts chat 8 found hide their map links behind script or refuse a plain reader (OFFICIAL_MAPS SUMMARY 'NEEDS A BROWSER BOT')
BROWSER_HOSTS = {'floridastateparks.org', 'bcparks.ca', 'pgc.pa.gov', 'dep.nj.gov', 'nj.gov', 'state.nj.us', 'fs.usda.gov', 'blm.gov', 'alapark.com',
                 'arkansasstateparks.com', 'agfc.com', 'apps.agfc.com', 'azstateparks.com', 'azgfd.com', 'gastateparks.org', 'ksoutdoors.com',
                 'michigan.gov', 'dnr.state.mi.us', 'www2.dnr.state.mi.us', 'mdwfp.com', 'fwp.mt.gov', 'nhstateparks.org', 'emnrd.state.nm.us',
                 'vtstateparks.com', 'parks.wa.gov', 'iowadnr.gov', 'dnr.illinois.gov', 'parksandrecreation.idaho.gov', 'dlnr.hawaii.gov',
                 'stateparks.utah.gov', 'mass.gov', 'portal.ct.gov', 'destateparks.com', 'usace.army.mil', 'parks.canada.ca', 'ontarioparks.ca',
                 'albertaparks.ca', 'tpwd.texas.gov', 'stateparks.com'}
MAPWORD = re.compile(r'\bmaps?\b|brochure|trail guide|geopdf|avenza|\bmapa\b|carte', re.I)
NOTMAP = re.compile(r'google\.|bing\.com|apple\.com/maps|mapquest|openstreetmap|waze|sitemap|site-map|\bmap of the site|roadmap|mapping tool|interactive map viewer', re.I)
RULEWORD = re.compile(r'\brules?\b|regulations?|policies|laws? (and|&) policies|compendium|permits?|know before you go|r[èe]glements?|hunting (and|&) fishing regulations|park rules|ordinance', re.I)
HANDOVER = re.compile(r'((?:transferred|handed over|turned over|conveyed|deeded|leased|donated) (?:to|from) (?:the )?(?:city|county|town|village|parish|state|commonwealth|municipality|tribe|nation) (?:of )?[A-Z][\w\s.\'-]{2,50})', re.I)
MANAGED = re.compile(r'((?:is |now |currently )?(?:managed|operated|owned|maintained|administered|run) (?:jointly )?by (?:the )?[A-Z][\w\s.&\'-]{3,70}?)(?=[.,;:(\n]|\s(?:and|which|that|in|for|under)\b)', re.I)
MONTHS = 'january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec'
PRINTED = [
    (re.compile(r'(?:date published|published|publication date|revised|revision|updated|last updated|updated on|map date|date of map|printed|produced|prepared|effective|current as of|as of|issued)\s*[:\-]?\s*((?:' + MONTHS + r')\.?\s+\d{1,2},?\s+(?:19|20)\d\d|\d{1,2}/\d{1,2}/(?:19|20)\d\d|(?:19|20)\d\d-\d\d-\d\d|(?:' + MONTHS + r')\.?\s+(?:19|20)\d\d|\d{1,2}/(?:19|20)\d\d|(?:19|20)\d\d)', re.I), 'printed on the map'),
    (re.compile(r'\b((?:' + MONTHS + r')\.?\s+(?:19|20)\d\d)\b', re.I), 'a month + year printed on the map'),
    (re.compile(r'(?:©|\(c\)|copyright)\s*((?:19|20)\d\d)', re.I), 'a copyright year on the map'),
]
AGENCY = [  # host -> who runs it (families first, then named agencies; states fall back to the host)
    (r'nps\.gov$', 'National Park Service', 'nps'), (r'fws\.gov$', 'U.S. Fish and Wildlife Service', 'fws'),
    (r'fs\.usda\.gov$', 'U.S. Forest Service', 'usfs'), (r'blm\.gov$', 'Bureau of Land Management', 'blm'),
    (r'usace\.army\.mil$|corpslakes\.erdc\.dren\.mil$', 'U.S. Army Corps of Engineers', 'usace'), (r'tva\.(gov|com)$', 'Tennessee Valley Authority', 'tva'),
    (r'parks\.canada\.ca$|pc\.gc\.ca$', 'Parks Canada', 'pc'), (r'canada\.ca$', 'Environment and Climate Change Canada', 'eccc'),
    (r'mdc\.mo\.gov$', 'Missouri Department of Conservation', 'state'), (r'mostateparks\.com$', 'Missouri State Parks', 'state'),
    (r'floridastateparks\.org$', 'Florida State Parks (DEP)', 'state'), (r'myfwc\.com$', 'Florida Fish and Wildlife Conservation Commission', 'state'),
    (r'fdacs\.gov$', 'Florida Forest Service (FDACS)', 'state'), (r'sjrwmd\.com$|swfwmd\.state\.fl\.us$|sfwmd\.gov$|nwfwater\.com$|srwmd\.org$', 'Florida water management district', 'state'),
    (r'fw\.ky\.gov$', 'Kentucky Department of Fish and Wildlife Resources', 'state'), (r'parks\.ky\.gov$|kentuckytourism\.com$', 'Kentucky State Parks', 'state'),
    (r'eec\.ky\.gov$', 'Kentucky Office of Nature Preserves', 'state'), (r'ncparks\.gov$', 'North Carolina State Parks', 'state'),
    (r'ncwildlife\.gov$', 'North Carolina Wildlife Resources Commission', 'state'), (r'dcr\.virginia\.gov$|virginiastateparks\.gov$', 'Virginia State Parks (DCR)', 'state'),
    (r'dwr\.virginia\.gov$', 'Virginia Department of Wildlife Resources', 'state'), (r'wvdnr\.gov$|wvstateparks\.com$', 'West Virginia Division of Natural Resources', 'state'),
    (r'ohiodnr\.gov$|assets\.ohio\.gov$', 'Ohio Department of Natural Resources', 'state'), (r'parks\.ca\.gov$', 'California State Parks', 'state'),
    (r'wildlife\.ca\.gov$', 'California Department of Fish and Wildlife', 'state'), (r'tpwd\.texas\.gov$', 'Texas Parks and Wildlife Department', 'state'),
    (r'gastateparks\.org$|georgiawildlife\.com$', 'Georgia DNR', 'state'), (r'tn\.gov$|tnstateparks\.com$', 'Tennessee state agency', 'state'),
    (r'outdooralabama\.com$|alapark\.com$|alabamaforeverwild\.com$', 'Alabama DCNR', 'state'), (r'albertaparks\.ca$|alberta\.ca$', 'Alberta Parks', 'state'),
    (r'ontarioparks\.ca$|ontario\.ca$', 'Ontario Parks', 'state'), (r'bcparks\.ca$|gov\.bc\.ca$', 'BC Parks', 'state'), (r'sepaq\.com$|quebec\.ca$|gouv\.qc\.ca$', 'Québec (Sépaq / government)', 'state'),
]
FED_RULES = {  # family -> candidate rules pages built from the unit / refuge / forest slug (each one is OPENED before it is kept)
    'nps': ['https://www.nps.gov/{u}/learn/management/lawsandpolicies.htm', 'https://www.nps.gov/{u}/learn/management/superintendents-compendium.htm'],
    'fws': ['https://www.fws.gov/refuge/{u}/visit-us/rules-policies', 'https://www.fws.gov/refuge/{u}/rules-and-policies', 'https://www.fws.gov/refuge/{u}/visit-us/activities'],
    'usfs': ['https://www.fs.usda.gov/{u}/alerts-notices', 'https://www.fs.usda.gov/alerts/{u}/alerts-notices', 'https://www.fs.usda.gov/main/{u}/alerts-notices'],
}
USACE_RULES = 'https://www.ecfr.gov/current/title-36/chapter-III/part-327'


def notice(m): print('::notice title=Documents bot::' + str(m).replace('\n', ' ')[:900], flush=True)
def late(): return time.time() - T0 > LIMIT
def load(p, d):
    try: return json.load(open(p, encoding='utf-8'))
    except Exception: return d  # noqa: BLE001
def save(p, obj):
    pathlib.Path(p).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(p).write_text(json.dumps(obj, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
def host_of(u): return urllib.parse.urlparse(u).netloc.lower().split(':')[0]
def base_host(h): return re.sub(r'^(www\d?|m)\.', '', h)
def low(x): return ' '.join(re.sub(r'[^a-z0-9 ]', ' ', str(x or '').lower().replace('&', ' and ')).split())
KINDW = re.compile(r'\b(state|national|provincial|park|parks|forest|wildlife|management|area|areas|recreation|conservation|nature|natural|preserve|reserve|refuge|historic|historical|site|game|land|lands|wma|sp|sra|sf|nwr|trail|the|of|and|at|county|city|regional|unit|access|public|fishing|lake|hunting)\b')
def core(x): return ' '.join(KINDW.sub(' ', low(x)).split())


# ------------------------------------------------------------------ manners
def robots_ok(u):
    h = host_of(u)
    if h not in ROBOTS:
        rp = urllib.robotparser.RobotFileParser()
        try:
            ru = f'{urllib.parse.urlparse(u).scheme or "https"}://{h}/robots.txt'
            with urllib.request.urlopen(urllib.request.Request(ru, headers={'User-Agent': UA}), timeout=15) as r: txt = r.read(30000).decode('utf-8', 'replace')
            rp.parse(txt.splitlines()); ROBOTS[h] = rp
            ROBOTS_SAID[h] = ' | '.join(l.strip() for l in txt.splitlines() if l.strip() and not l.startswith('#'))[:160]
        except Exception as e: ROBOTS[h] = None; ROBOTS_SAID[h] = 'no robots.txt (' + str(e)[:30] + ')'  # noqa: BLE001  (no robots file = allowed)
    rp = ROBOTS[h]
    try: ok = rp is None or rp.can_fetch(UA, u) or rp.can_fetch('*', u)
    except Exception: ok = True  # noqa: BLE001
    if not ok: STAT['robots'] += 1; ROBOTS_REFUSED[h] = ROBOTS_REFUSED.get(h, 0) + 1
    return ok


def rested(h):
    """Three strikes = the host rests a day; the rest is remembered across runs in state.json."""
    return DEAD.get(h, 0) > time.time()


def get(u, rng=None, timeout=40, head=False):
    """Polite GET: robots, 2 s per host, back-off on 429 / 5xx, three strikes and the host rests a day.
    Returns (status, headers, body bytes, final url). rng = (start, end) reads only that part of a file."""
    h = host_of(u)
    if rested(h): return 'rest', {}, b'', u
    if not robots_ok(u): return 'robots', {}, b'', u
    hdr = {'User-Agent': UA, 'Accept': 'text/html,application/pdf,*/*;q=0.8', 'Accept-Language': 'en-US,en;q=0.8,fr;q=0.5'}
    if rng: hdr['Range'] = f'bytes={rng[0]}-{rng[1]}'
    for attempt in range(3):
        w = GAP * (2 ** STRIKE.get(h, 0)) - (time.time() - LAST.get(h, 0))
        if w > 0: time.sleep(min(w, 20))
        LAST[h] = time.time(); STAT['requests'] += 1
        try:
            req = urllib.request.Request(u, headers=hdr, method='HEAD' if head else 'GET')
            with urllib.request.urlopen(req, timeout=timeout) as r:
                body = b'' if head else r.read(PDF_MAX if rng else 3_000_000)
                return r.status, {k.lower(): v for k, v in r.headers.items()}, body, r.geturl()
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504):
                STRIKE[h] = STRIKE.get(h, 0) + 1; STAT['strikes'] += 1
                if STRIKE[h] >= STRIKES_OUT: DEAD[h] = time.time() + 86400; return 'rest', {}, b'', u
                time.sleep(20 * (attempt + 1)); continue
            if e.code == 416 and rng: return get(u, None, timeout, head)   # the file is smaller than the range
            return e.code, {k.lower(): v for k, v in (e.headers or {}).items()}, b'', u
        except (urllib.error.URLError, TimeoutError, OSError, ValueError) as e:
            STRIKE[h] = STRIKE.get(h, 0) + 1; STAT['strikes'] += 1; STAT['errors'] += 1
            if STRIKE[h] >= STRIKES_OUT: DEAD[h] = time.time() + 86400; return 'rest', {}, b'', u
            if attempt == 2: return 'err:' + str(e)[:60], {}, b'', u
            time.sleep(10 * (attempt + 1))
    return 'err', {}, b'', u


# ------------------------------------------------------------------ reading pages and files
def links_in(html, base):
    """[(absolute url, link text)] from an HTML page (no parser library needed)."""
    out = []
    for m in re.finditer(r'<a\b[^>]*?href\s*=\s*["\']([^"\'#]+)["\'][^>]*>(.*?)</a>', html, re.I | re.S):
        href = m.group(1).strip()
        if href.lower().startswith(('javascript:', 'mailto:', 'tel:')): continue
        txt = re.sub(r'<[^>]+>', ' ', m.group(2)); txt = ' '.join(re.sub(r'&[a-z]+;|&#\d+;', ' ', txt).split())[:80]
        title = re.search(r'(?:title|aria-label)\s*=\s*["\']([^"\']{2,80})', m.group(0), re.I)
        if title and not txt: txt = title.group(1)
        try: out.append((urllib.parse.urljoin(base, href), txt))
        except Exception: pass  # noqa: BLE001
    return out


def page_text(html):
    html = re.sub(r'<(script|style|noscript)\b.*?</\1>', ' ', html, flags=re.I | re.S)
    t = re.sub(r'<[^>]+>', ' ', html)
    t = re.sub(r'&nbsp;|&#160;', ' ', t); t = re.sub(r'&amp;', '&', t)
    return ' '.join(t.split())


def map_score(url, text, agency_host):
    """How much a link looks like THE park's official map: PDF + 'park map' best; off-site and generic things worst."""
    s = 0; u = url.lower(); t = (text or '').lower()
    if NOTMAP.search(u) or NOTMAP.search(t): return -9
    if not (MAPWORD.search(u) or MAPWORD.search(t)): return -9
    if u.endswith('.pdf') or '.pdf' in u: s += 4
    elif re.search(r'\.(jpe?g|png|gif)(\?|$)', u): s += 2
    elif re.search(r'/rest/services/|arcgis|mapserver|featureserver', u): s += 1
    else: s += 1
    if re.search(r'park map|property map|area map|boundary map|trail map|site map(?! of)|facility map|map of the', t): s += 3
    elif re.search(r'\bmap\b', t): s += 2
    if re.search(r'campground|camping|lodge|floor plan|golf|parking only|regional map|directions|driving|location map|vicinity', t + ' ' + u): s -= 2
    if agency_host and base_host(host_of(url)) == base_host(agency_host): s += 1
    return s


def rules_score(url, text):
    t = (text or '').lower(); u = url.lower()
    if not (RULEWORD.search(t) or RULEWORD.search(u)): return -9
    if NOTMAP.search(u): return -9
    s = 1
    if re.search(r'rules|regulations|compendium|laws', t): s += 2
    if re.search(r'rules|regulation|compendium|lawsandpolicies|policies', u): s += 1
    if re.search(r'hunting|fishing|boat', t) and not re.search(r'park|area|property|land', t): s -= 1
    if re.search(r'privacy|terms of use|cookie|accessibility|site policies', t + ' ' + u): return -9
    return s


def family_of(url):
    h = base_host(host_of(url))
    for pat, name, fam in AGENCY:
        if re.search(pat, h): return name, fam
    if h.endswith('.gov') or h.endswith('.gov.on.ca') or h.endswith('.gc.ca') or '.gov.' in h or h.endswith('.ca'):
        return f'government agency ({h})', 'state'
    return f'agency site ({h})', 'other'


def unit_slug(url, fam):
    u = urllib.parse.urlparse(url); p = u.path
    if fam == 'nps':
        m = re.search(r'^/([a-z]{4})(/|$)', p)
        return m.group(1) if m else ''
    if fam == 'fws':
        m = re.search(r'/refuge/([a-z0-9_-]+)', p)
        return m.group(1) if m else ''
    if fam == 'usfs':
        m = re.search(r'^/(?:main/|detail/|recarea/|r\d\d/)?([a-z0-9_-]+)', p)
        return m.group(1) if m and m.group(1) not in ('main', 'detail', 'recarea', 'visit', 'managing-land', 'alerts', 'detailfull') else ''
    return ''


def pdf_first_page_text(body):
    """Text of the first page (or what a partial file gives up): pypdf, else a crude text scrape of the bytes."""
    txt = ''
    try:
        import pypdf
        rd = pypdf.PdfReader(io.BytesIO(body), strict=False)
        for i in range(min(2, len(rd.pages))):
            try: txt += (rd.pages[i].extract_text() or '') + '\n'
            except Exception: break  # noqa: BLE001
    except Exception: pass  # noqa: BLE001
    raw = body.decode('latin-1', 'replace')
    if len(txt.strip()) < 20:
        txt = ' '.join(re.findall(r'\(([^()\\]{2,120})\)', raw)[:600])   # literal strings in the content stream + the Info dictionary
    # the file's own date stamp (Info dictionary; a few writers escape the colon as \072): the LAST resort before the read day
    m = re.search(r'/(?:ModDate|CreationDate)\s*\(D(?::|\\072)((?:19|20)\d\d)(\d\d)(\d\d)', raw)
    if m: txt += f' Document date {m.group(1)}-{m.group(2)}-{m.group(3)}'
    return txt


def plausible(y):
    try: y = int(y)
    except Exception: return False  # noqa: BLE001
    return 1990 <= y <= int(TODAY[:4])


def date_from_text(txt):
    """(date text, method) from printed text; the latest plausible date wins."""
    best = None
    for rx, how in PRINTED:
        for m in rx.finditer(txt):
            d = m.group(1).strip()
            y = re.search(r'(?:19|20)\d\d', d)
            if not y or not plausible(y.group()): continue
            key = (int(y.group()), how == 'printed on the map')
            if best is None or key > best[0]: best = (key, d, how)
    if best: return best[1], best[2]
    m = re.search(r'Document date ((?:19|20)\d\d-\d\d-\d\d)', txt)
    if m and plausible(m.group(1)[:4]): return m.group(1), "the file's own date stamp (PDF info)"
    return '', ''


def date_from_url(u):
    p = urllib.parse.urlparse(u); path = urllib.parse.unquote(p.path); q = p.query
    m = re.search(r'/((?:19|20)\d\d)[-/_](0[1-9]|1[0-2])(?:/|_|-|$)', path)
    if m and plausible(m.group(1)): return f'{m.group(1)}-{m.group(2)}', 'the upload folder in the address (YYYY-MM)'
    m = re.search(r'(?:^|[^0-9])((?:19|20)\d\d)[-_]?(0[1-9]|1[0-2])?(?:[-_]?(?:' + MONTHS + r'))?(?:pdf|\.pdf|[-_]|$)', path.rsplit('/', 1)[-1], re.I)
    if m and plausible(m.group(1)): return m.group(1) + (f'-{m.group(2)}' if m.group(2) else ''), "a year in the file's name"
    m = re.search(r'/((?:19|20)\d\d)/', path)
    if m and plausible(m.group(1)): return m.group(1), 'the upload folder in the address (year)'
    m = re.search(r'(?:^|[?&])(?:v|ver|version|rev|sfvrsn|t|ts)=([^&]{1,20})', q, re.I)
    if m: return m.group(1), "the file's version tail (not a date)"
    return '', ''


def check_url(u, want_text=True):
    """Open an address the polite way. Returns a dict: status, kind (pdf / page / image / arcgis / other), date, date_how, text."""
    r = {'url': u, 'status': '', 'kind': '', 'date': '', 'date_how': '', 'final': u}
    looks_pdf = u.lower().split('?')[0].endswith('.pdf')
    st, hd, body, final = get(u, rng=(0, PDF_FIRST - 1) if looks_pdf else None)
    r['status'] = 'ok' if st in (200, 206) else ('rest' if st == 'rest' else 'robots' if st == 'robots' else f'HTTP {st}' if isinstance(st, int) else str(st))
    r['final'] = final
    if r['status'] != 'ok': return r
    ct = (hd.get('content-type') or '').lower()
    if body[:5] == b'%PDF-' or 'application/pdf' in ct:
        r['kind'] = 'pdf'
        if not looks_pdf and len(body) >= 3_000_000: body = body[:PDF_MAX]
        txt = pdf_first_page_text(body)
        if len(txt.strip()) < 20 and looks_pdf and int(hd.get('content-length', '0') or 0) > PDF_FIRST:
            st2, _, body2, _ = get(u, rng=(0, PDF_MAX - 1))
            if st2 in (200, 206): txt = pdf_first_page_text(body2)
        d, how = date_from_text(txt)
        if d: r['date'], r['date_how'] = d, how
    elif ct.startswith('image/') or re.search(r'\.(jpe?g|png|gif)(\?|$)', u, re.I):
        r['kind'] = 'image'
    elif re.search(r'/rest/services/|mapserver|featureserver', u, re.I):
        r['kind'] = 'arcgis'
    else:
        r['kind'] = 'page'
        html = body.decode('utf-8', 'replace')
        txt = page_text(html)
        r['text'] = txt[:20000]; r['links'] = links_in(html, final)[:400]
        m = re.search(r'(?:last updated|page last updated|updated|last modified|date modified)\s*[:\-]?\s*((?:' + MONTHS + r')\.?\s+\d{1,2},?\s+(?:19|20)\d\d|(?:19|20)\d\d-\d\d-\d\d|\d{1,2}/\d{1,2}/(?:19|20)\d\d)', txt, re.I)
        if m and plausible(re.search(r'(?:19|20)\d\d', m.group(1)).group()): r['date'], r['date_how'] = m.group(1), "the page's 'last updated' line"
        if len(txt) < 300 and re.search(r'enable javascript|loading|<app-root|ng-app|__NEXT_DATA__|data-reactroot', html, re.I): r['shell'] = True
    if not r['date']:
        d, how = date_from_url(final if final else u)
        if d: r['date'], r['date_how'] = d, how
    if not r['date'] and hd.get('last-modified') and r['kind'] in ('pdf', 'image'):
        m = re.search(r'(\d{1,2}) ([A-Za-z]{3}) ((?:19|20)\d\d)', hd['last-modified'])
        if m and plausible(m.group(3)): r['date'], r['date_how'] = f'{m.group(2)} {m.group(1)}, {m.group(3)}', "the server's file date (Last-Modified)"
    if not r['date']: r['date'], r['date_how'] = TODAY, 'the day we read it (no date on the map or in the address)'
    return r


# ------------------------------------------------------------------ the lists (read, matched by name; never a guessed file name)
LIST_INDEX = {}


def list_index(entry):
    """entry = {'pages': [...], 'host': ..., 'pick': 'pdf'|'any'}: every link on the list pages, keyed by the core of its text."""
    k = json.dumps(entry.get('pages'), sort_keys=True)
    if k in LIST_INDEX: return LIST_INDEX[k]
    idx = {}
    for pu in entry.get('pages') or []:
        r = check_url(pu)
        if r['status'] != 'ok' or r['kind'] != 'page': continue
        for u, t in r.get('links') or []:
            if entry.get('pick') == 'pdf' and '.pdf' not in u.lower(): continue
            c = core(t) or core(urllib.parse.unquote(u.rsplit('/', 1)[-1]).replace('_', ' ').replace('-', ' '))
            if len(c) >= 3: idx.setdefault(c, []).append((u, t))
    LIST_INDEX[k] = idx
    return idx


def from_list(name, entry):
    idx = list_index(entry)
    c = core(name)
    if not c: return None
    hit = idx.get(c)
    if not hit:
        cw = set(c.split())
        cands = [(len(cw & set(k.split())) / max(1, len(cw | set(k.split()))), k) for k in idx if len(cw & set(k.split())) >= max(1, len(cw) - 1)]
        cands = [x for x in cands if x[0] >= .6]
        if cands: hit = idx[max(cands)[1]]
    return hit[0] if hit else None


# ------------------------------------------------------------------ one park
def seeds(ref, pinfo, web, ky):
    """What is already on file: the park's own page, a map link (parkinfo-web / Kentucky 'off'), the agency's name."""
    v = pinfo.get(ref) or []
    w = web.get(ref) or {}
    page = (w.get('web') or (v[1] if len(v) > 1 else '') or '').strip()
    if 'pota.app' in page: page = ''
    maps = []
    k = ky.get(ref) or {}
    for m in (k.get('off'), k.get('off2'), w.get('map')):
        if m and str(m).startswith('http') and 'pota.app' not in m and m not in maps: maps.append(m)
    if not page and k.get('web') and 'pota.app' not in k['web']: page = k['web']
    return {'name': v[0] if v else k.get('n', ref), 'type': v[2] if len(v) > 2 else '', 'page': page, 'maps': maps, 'agency': w.get('agency') or k.get('agency') or '',
            'ky_answer': k.get('off') or ''}


def find_on_page(pg, agency_host):
    """Map + rules links on the park's own page."""
    maps, rules = [], []
    for u, t in pg.get('links') or []:
        s = map_score(u, t, agency_host)
        if s > 0: maps.append((s, u, t))
        s2 = rules_score(u, t)
        if s2 > 0: rules.append((s2, u, t))
    maps.sort(key=lambda x: -x[0]); rules.sort(key=lambda x: -x[0])
    return maps, rules


def who_runs(texts, agency_name):
    hints, hand = [], []
    for txt in texts:
        for m in HANDOVER.finditer(txt or ''):
            s = m.group(1).strip()
            if s not in hand: hand.append(s[:120])
        for m in MANAGED.finditer(txt or ''):
            s = ' '.join(m.group(1).split())
            if len(s) < 100 and s not in hints: hints.append(s)
    return hints[:3], hand[:3]


def rules_for(fam, urls, pg_rules, lists_entry):
    """Candidate rules pages in order; the first that OPENS is kept. Federal patterns first, then the page's own links, then the
    agency-wide rules page from lists.json."""
    cands = []
    slug = next((unit_slug(u, fam) for u in urls if unit_slug(u, fam)), '')
    if fam in FED_RULES and slug: cands += [(x.format(u=slug), f'{fam.upper()} rules page (pattern + opened)') for x in FED_RULES[fam]]
    if fam == 'usace': cands.append((USACE_RULES, 'Corps lakes: 36 CFR Part 327 (one national rule book) + the lake page'))
    cands += [(u, f"a link on the park's page ('{t}')") for s, u, t in pg_rules[:3]]
    if lists_entry and lists_entry.get('rules'): cands.append((lists_entry['rules'], 'the agency-wide rules page (chat 8 survey)'))
    seen = set()
    for u, how in cands:
        if u in seen: continue
        seen.add(u)
        st, hd, body, final = get(u, head=False)
        if st in (200, 206):
            return {'url': final or u, 'how': how, 'status': 'ok'}
        if st in ('rest', 'robots'): return {'url': u, 'how': how, 'status': str(st)}
    return {'url': cands[0][0] if cands else '', 'how': cands[0][1] if cands else '', 'status': 'not found' if not cands else 'did not open'}


def one_park(ref, S, lists, area):
    rec = {'n': S['name'], 't': S['type'], 'page': S['page'], 'checked': TODAY, 'map': None, 'rules': None, 'agency': S['agency'], 'runs': [], 'handover': [], 'notes': []}
    texts = []
    agency_host = host_of(S['page']) if S['page'] else (host_of(S['maps'][0]) if S['maps'] else '')
    fam_name, fam = family_of(S['page'] or (S['maps'][0] if S['maps'] else 'https://x.invalid/'))
    if not rec['agency']: rec['agency'] = fam_name if fam != 'other' else ''
    pg = None
    page_rules = []
    # 1 the park's own page (links + text), unless it is a known browser-only host
    if S['page'] and base_host(host_of(S['page'])) not in BROWSER_HOSTS:
        pg = check_url(S['page'])
        if pg['status'] == 'ok' and pg['kind'] == 'page':
            texts.append(pg.get('text', ''))
            if pg.get('shell'): rec['needs_browser'] = 'the page is built by script'
        elif pg['status'] in ('HTTP 403', 'HTTP 406', 'HTTP 503'): rec['needs_browser'] = f"the page refused a plain reader ({pg['status']})"
        elif pg['status'] not in ('ok',): rec['notes'].append(f"park page: {pg['status']}")
    elif S['page']: rec['needs_browser'] = 'host on the browser list'
    # 2 the map: on file first; else from the agency's list page; else from the park's page
    cands = [(u, 'on file (parkinfo-web / Kentucky answer key)') for u in S['maps']]
    le = lists.get(area, {}).get(base_host(agency_host)) if agency_host else None
    if not cands and le and le.get('pages'):
        hit = from_list(S['name'], le)
        if hit: cands.append((hit[0], f"the agency's list page, matched by name ('{hit[1]}')"))
    if pg and pg['status'] == 'ok' and pg['kind'] == 'page':
        pm, page_rules = find_on_page(pg, agency_host)
        for s, u, t in pm[:2]:
            if u not in [c[0] for c in cands]: cands.append((u, f"a link on the park's page ('{t}')"))
    for u, how in cands:
        if late(): break
        r = check_url(u)
        m = {'url': r['final'] or u, 'status': r['status'], 'kind': r['kind'], 'date': r['date'], 'date_how': r['date_how'], 'how': how}
        if r['status'] == 'ok':
            if r['kind'] == 'page':
                texts.append(r.get('text', ''))
                if r.get('shell'): rec['needs_browser'] = 'the map page is built by script'
                # a map PAGE that links a PDF: take the PDF as the map, keep the page as its source
                pm2, pr2 = find_on_page(r, agency_host)
                page_rules = page_rules or pr2
                pdfs = [x for x in pm2 if '.pdf' in x[1].lower()]
                if pdfs and not late():
                    r2 = check_url(pdfs[0][1])
                    if r2['status'] == 'ok': m = {'url': r2['final'], 'status': 'ok', 'kind': r2['kind'], 'date': r2['date'], 'date_how': r2['date_how'], 'how': how + f" -> the page's '{pdfs[0][2]}' file", 'page': r['final']}
            rec['map'] = m; STAT['maps_ok'] += 1
            if how != cands[0][1] or not S['maps']: STAT['maps_found'] += 1
            if m['date_how'] and not m['date_how'].startswith('the day we read it'): STAT['dates'] += 1
            break
        rec['map'] = rec['map'] or m
        if r['status'] in ('HTTP 403', 'HTTP 406') or (r['status'] == 'ok' and r.get('shell')): rec['needs_browser'] = f'the map link refused a plain reader ({r["status"]})'
    if rec['map'] is None and not cands: rec['map'] = {'url': '', 'status': 'no map link on file and none on the park page', 'how': ''}
    if rec['map'] and rec['map'].get('status') == 'ok' and base_host(host_of(rec['map']['url'])) in BROWSER_HOSTS and rec['map'].get('kind') == 'page': rec['needs_browser'] = 'map page on the browser list (a download button may hide the file)'
    # 3 the rules page
    if not late():
        urls = [S['page']] + [c[0] for c in cands]
        rec['rules'] = rules_for(fam, [u for u in urls if u], page_rules, le)
        if rec['rules']['status'] == 'ok': STAT['rules'] += 1
    # 4 who runs it
    hints, hand = who_runs(texts, rec['agency'])
    rec['runs'] = hints; rec['handover'] = hand
    if hand: STAT['handovers'] = STAT.get('handovers', 0) + 1
    if S['ky_answer']: rec['ky_answer'] = S['ky_answer']
    return rec


# ------------------------------------------------------------------ the browser pass
def browser_pass(area, D, parks, budget_s):
    try: from playwright.sync_api import sync_playwright
    except Exception: notice(f'{area}: no browser on this runner (pip install playwright + chromium)'); return 0  # noqa: BLE001
    todo = [r for r, p in D['parks'].items() if p.get('needs_browser') and not p.get('browser_checked')]
    if not todo: return 0
    t0 = time.time(); n = 0; errs = {}
    with sync_playwright() as p:
        b = p.chromium.launch(); ctx = b.new_context(user_agent=UA, accept_downloads=True); pg = ctx.new_page()
        for ref in todo:
            if time.time() - t0 > budget_s or late(): break
            rec = D['parks'][ref]
            url = (rec.get('map') or {}).get('page') or ((rec.get('map') or {}).get('url') if (rec.get('map') or {}).get('kind') == 'page' else '') or rec.get('page') or ''
            if not url or not robots_ok(url): rec['browser_checked'] = TODAY; continue
            h = host_of(url)
            if errs.get(h, 0) >= 4 or rested(h): continue
            w = GAP + 1 - (time.time() - LAST.get(h, 0))
            if w > 0: time.sleep(w)
            LAST[h] = time.time(); STAT['requests'] += 1
            try:
                pg.goto(url, timeout=40000, wait_until='networkidle'); n += 1; STAT['browser'] += 1
                links = pg.eval_on_selector_all('a[href]', 'as => as.map(a => [a.href, (a.innerText || a.getAttribute("aria-label") || a.title || "").trim().slice(0, 80)])')
                text = pg.evaluate('() => document.body ? document.body.innerText.slice(0, 20000) : ""')
            except Exception as e:  # noqa: BLE001
                errs[h] = errs.get(h, 0) + 1; rec['notes'].append(f'browser: {str(e)[:60]}'); time.sleep(3); continue
            agency_host = host_of(url)
            fake = {'links': links}
            pm, pr = find_on_page(fake, agency_host)
            got = None
            if pm:
                got = {'url': pm[0][1], 'how': f"the page in a browser ('{pm[0][2]}')", 'page': url}
            else:
                # a 'Download map' button with no address: click it and read where the download comes from
                try:
                    btn = pg.locator('a, button', has_text=re.compile(r'download.*map|park map|trail map|\bmap\b', re.I)).first
                    if btn.count():
                        with pg.expect_download(timeout=15000) as dl:
                            btn.click()
                        got = {'url': dl.value.url, 'how': "the page's download button (browser)", 'page': url}
                        try: dl.value.cancel()
                        except Exception: pass  # noqa: BLE001
                except Exception: pass  # noqa: BLE001
            if got:
                r = check_url(got['url'])
                rec['map'] = {'url': r['final'] or got['url'], 'status': r['status'], 'kind': r['kind'], 'date': r['date'], 'date_how': r['date_how'], 'how': got['how'], 'page': url}
                if r['status'] == 'ok': STAT['maps_ok'] += 1; STAT['maps_found'] += 1
            if (not rec.get('rules') or rec['rules'].get('status') != 'ok') and pr:
                st, _, _, final = get(pr[0][1])
                if st in (200, 206): rec['rules'] = {'url': final, 'how': f"a link on the page in a browser ('{pr[0][2]}')", 'status': 'ok'}; STAT['rules'] += 1
            hints, hand = who_runs([text], rec.get('agency'))
            rec['runs'] = rec['runs'] or hints; rec['handover'] = rec['handover'] or hand
            rec['browser_checked'] = TODAY
            time.sleep(2)
        b.close()
    return n


# ------------------------------------------------------------------ areas
def park_list(area):
    st = area[3:]
    if area.startswith('US-'):
        d = load(f'data/parkinfo/US-{st}.json', {}) or load(LINKS / f'data/parkinfo/US-{st}.json', {})
        P = {r: v for r, v in (d.get('parks') or {}).items()}
        if not P and st == 'KY':   # Kentucky keeps its own hand-checked list (kpc-ky-data.json: c, n, t, web, off)
            P = {x['c']: [x.get('n', ''), x.get('web') or '', x.get('t', '')] for x in load(LINKS / 'kpc-ky-data.json', {}).get('parks', []) if x.get('c')}
        return P
    d = load('data/parkinfo/CA.json', {}) or load(LINKS / 'data/parkinfo/CA.json', {})
    return {r: v for r, v in (d.get('parks') or {}).items() if len(v) > 10 and v[10] == st}


def ky_answers():
    d = load(LINKS / 'kpc-ky-data.json', {})
    return {x['c']: {'off': x.get('off'), 'off2': x.get('off2'), 'web': x.get('web'), 'n': x.get('n'), 'agency': ''} for x in d.get('parks', []) if x.get('c')}


def run_area(area, state, web, lists, ky):
    f = OUT / f'{area}.json'
    D = load(f, {'area': area, 'about': 'Official map + rules page + who runs it, per park (documents bot). Nothing here reaches a card until chat 8 grades it.', 'parks': {}})
    parks = park_list(area)
    if not parks: notice(f'{area}: no park list (data/parkinfo)'); state['areas'][area] = {'status': 'done', 'parks': 0, 'updated': TODAY}; return
    done = 0; fresh = 0
    for ref in sorted(parks):
        if late(): break
        old = D['parks'].get(ref)
        if old and old.get('checked', '') >= time.strftime('%Y-%m-%d', time.gmtime(time.time() - REFRESH_DAYS * 86400)):
            fresh += 1; STAT['skipped_fresh'] += 1; continue
        S = seeds(ref, parks, web, ky if area == 'US-KY' else {})
        try: D['parks'][ref] = one_park(ref, S, lists, area)
        except Exception as e:  # noqa: BLE001
            D['parks'][ref] = {'n': S['name'], 'checked': TODAY, 'map': {'url': '', 'status': 'bot error: ' + str(e)[:80]}, 'rules': None, 'notes': []}
            STAT['errors'] += 1
        done += 1; STAT['parks'] += 1
    if BROWSER and not late():
        browser_pass(area, D, parks, max(60, LIMIT - (time.time() - T0) - 60))
    if area == 'US-KY' and not late(): ky_finder_check(D, parks, ky, web)
    D['read'] = TODAY; D['counts'] = counts(D)
    save(f, D)
    left = sum(1 for r in parks if r not in D['parks'])
    state['areas'][area] = {'status': 'done' if left == 0 else 'partial', 'parks': len(parks), 'checked': len(D['parks']), 'left': left, 'updated': TODAY}
    notice(f"{area}: {done} parks checked this chunk ({fresh} fresh, {left} left) · {D['counts']}")


def ky_finder_check(D, parks, ky, web):
    """Kentucky answer-key check: for SAMPLE parks that have a hand-checked map link, would the bot have FOUND it from the park's
    page alone (seed hidden)? Written into the file as 'finder_check' for chat 8."""
    n = int(os.environ.get('SAMPLE') or 25)
    refs = [r for r in sorted(parks) if (ky.get(r) or {}).get('off') and (parks[r][1] or '').startswith('http') and 'pota.app' not in parks[r][1]][:n]
    out = {'sample': len(refs), 'same': 0, 'other_map': 0, 'none': 0, 'rows': []}
    norm = lambda u: re.sub(r'^https?://(www\.)?', '', (u or '').lower()).split('?')[0].rstrip('/')
    for r in refs:
        if late(): break
        S = seeds(r, parks, web, {}); S['maps'] = []   # the seed hidden
        rec = one_park(r, S, {}, 'US-KY')
        found = (rec.get('map') or {}).get('url') or ''
        want = ky[r]['off']
        k = 'same' if found and norm(found) == norm(want) else 'other_map' if found and (rec['map'].get('status') == 'ok') else 'none'
        out[k] += 1
        out['rows'].append({'ref': r, 'n': parks[r][0], 'answer': want, 'bot': found, 'verdict': k})
    D['finder_check'] = out
    notice(f"Kentucky finder check (seed hidden): same map {out['same']}, another map {out['other_map']}, none {out['none']} of {out['sample']}")


def counts(D):
    P = D['parks'].values()
    c = {'parks': len(D['parks']), 'map ok': 0, 'map found by the bot': 0, 'date on the map': 0, 'date from the address': 0, 'date = read day': 0, 'no map': 0, 'rules ok': 0,
         'needs browser': 0, 'handover hints': 0, 'runs hints': 0, 'host resting / robots': 0}
    for p in P:
        m = p.get('map') or {}
        if m.get('status') == 'ok':
            c['map ok'] += 1
            if not str(m.get('how', '')).startswith('on file'): c['map found by the bot'] += 1
            dh = m.get('date_how', '')
            if dh.startswith('the day we read it'): c['date = read day'] += 1
            elif 'printed' in dh or 'copyright' in dh or 'month + year' in dh or 'last updated' in dh or 'own date stamp' in dh: c['date on the map'] += 1
            else: c['date from the address'] += 1   # upload folder, file name, version tail, the server's file date
        elif m.get('status') in ('rest', 'robots'): c['host resting / robots'] += 1
        else: c['no map'] += 1
        if (p.get('rules') or {}).get('status') == 'ok': c['rules ok'] += 1
        if p.get('needs_browser') and not p.get('browser_checked'): c['needs browser'] += 1
        if p.get('handover'): c['handover hints'] += 1
        if p.get('runs'): c['runs hints'] += 1
    return c


def review(state):
    L = ['# Official documents bot: review list (hidden; for chat 8)', f'Updated {TODAY}. One file per area in data/docs/<area>.json: per park the official MAP (link, kind, date + how the date was found), the RULES page (link + how), who runs it (hints from the page) and HANDOVER hints. Nothing here reaches a card until chat 8 grades a sample and Brandon says GO.', '',
         '| area | parks | map ok | found by the bot | date on the map | date from the address | read day only | no map | rules ok | needs browser | handover hints |', '|---|---|---|---|---|---|---|---|---|---|---|']
    for area in QUEUE:
        f = OUT / f'{area}.json'
        if not f.exists(): continue
        D = load(f, {}); c = D.get('counts') or counts(D)
        L.append(f"| {area} | {c['parks']} | {c['map ok']} | {c['map found by the bot']} | {c['date on the map']} | {c['date from the address']} | {c['date = read day']} | {c['no map']} | {c['rules ok']} | {c['needs browser']} | {c['handover hints']} |")
    for area in QUEUE:
        f = OUT / f'{area}.json'
        if not f.exists(): continue
        D = load(f, {})
        L += ['', f'## {area} sample (first 12 parks with a map)', '| ref | park | map | kind | date (how) | rules | runs / handover |', '|---|---|---|---|---|---|---|']
        n = 0
        for ref, p in sorted(D['parks'].items()):
            m = p.get('map') or {}
            if m.get('status') != 'ok': continue
            ru = (p.get('rules') or {})
            L.append(f"| {ref} | {p.get('n','')[:40]} | {m.get('url','')[:90]} | {m.get('kind','')} | {m.get('date','')} ({m.get('date_how','')[:45]}) | {(ru.get('url') or '')[:70] + (' ✓' if ru.get('status') == 'ok' else ' ✗') if ru else ''} | {'; '.join((p.get('runs') or [])[:1] + (p.get('handover') or [])[:1])[:90]} |")
            n += 1
            if n >= 12: break
        hand = [(ref, p) for ref, p in D['parks'].items() if p.get('handover')]
        if hand:
            L += ['', f'### {area} HANDOVER hints ({len(hand)}): a person checks each one', *[f"- {ref} {p.get('n','')}: {' / '.join(p['handover'])}" for ref, p in hand[:30]]]
        nomap = [(ref, p) for ref, p in D['parks'].items() if (p.get('map') or {}).get('status') != 'ok']
        if nomap:
            L += ['', f'### {area} no map yet ({len(nomap)}): the reason', *[f"- {ref} {p.get('n','')[:45]}: {(p.get('map') or {}).get('status','')}" + (f" (needs browser: {p['needs_browser']})" if p.get('needs_browser') else '') for ref, p in nomap[:40]]]
        if D.get('finder_check'):
            fc = D['finder_check']
            L += ['', f"### Kentucky FINDER check (seed hidden, {fc['sample']} parks): the bot found the SAME map as the hand-checked answer for {fc['same']}, another official map for {fc['other_map']}, none for {fc['none']}",
                  *[f"- {r['ref']} {r['n'][:40]}: answer {r['answer'][:70]} | bot {r['bot'][:70] or '—'} → {r['verdict']}" for r in fc['rows'][:25]]]
    if ROBOTS_REFUSED: L += ['', '## robots.txt said no (hosts we did not read)', *[f'- {h}: {n} addresses ({ROBOTS_SAID.get(h, "")[:100]})' for h, n in sorted(ROBOTS_REFUSED.items())]]
    rest = {h: t for h, t in DEAD.items() if t > time.time()}
    if rest: L += ['', '## hosts resting a day (three strikes)', *[f'- {h}' for h in sorted(rest)]]
    (OUT / 'review.md').write_text('\n'.join(L) + '\n', encoding='utf-8')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    state = load(OUT / 'state.json', {'areas': {}, 'hosts': {}})
    for h, t in (state.get('hosts') or {}).items():
        if t > time.time(): DEAD[h] = t
    want = (os.environ.get('AREAS') or '').upper().split()
    areas = [a for a in want if a in QUEUE] if want else [a for a in QUEUE if (state['areas'].get(a) or {}).get('status') != 'done']
    if want and not areas: notice('no known area in AREAS'); return
    web = (load('data/parkinfo-web.json', {}) or load(LINKS / 'data/parkinfo-web.json', {})).get('parks') or {}
    lists = load(OUT / 'lists.json', {}).get('areas') or {}
    ky = ky_answers()
    for area in areas:
        if late(): break
        run_area(area, state, web, lists, ky)
    state['hosts'] = {h: t for h, t in DEAD.items() if t > time.time()}
    state['last'] = {'when': TODAY, 'areas': areas[:8], 'stat': STAT}
    save(OUT / 'state.json', state)
    review(state)
    left = [a for a in QUEUE if (state['areas'].get(a) or {}).get('status') != 'done']
    notice(f"done this chunk: {STAT} · areas left in the queue: {len(left)}" + (f" (next {' '.join(left[:4])})" if left else ''))


if __name__ == '__main__':
    try: main()
    except Exception as e:  # noqa: BLE001
        import traceback; traceback.print_exc()
        notice(f'stopped: {e}')
    sys.exit(0)
