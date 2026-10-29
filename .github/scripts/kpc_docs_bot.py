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
VER = 7   # Oct 29 (chat 11's NE/MW grade): a map viewer deep-linked by the area's own ID counts as naming the park (names_park 'link'); VER 6 = Oct 29 (Fable's notes, Opus): a raster map PDF (under 300 characters of text) is judged by its FILE NAME, a readable PDF that does not name the park gets the file-name test before it is thrown out ('TeterCreekLakeFinal11x17_300dpi.pdf'), agency-wide rules pages kept but labelled rules_scope 'agency', court-rules / policies-and-links / admincode / stamp-art pages never rules, COUNT line + a >15% map drop keeps the saved copy; v5 = Oct 28 noon: chat 11's chunks 1-3 grade (shared rules pages, inciweb / Google pins / error maps, forest-level maps) + KY regrade 3 (USDA OIG, forest home pages). v4 = Oct 28 6:34 AM: Brandon's 8 rulings DOC-3..DOC-11 (campground / combined / overview / dates / hunting / Avenza / same age); v3 = chat 8 F1-F10 + chat 11's grade. Records made by an older rule set are read again
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
BROWSER_HOSTS = {'tn.gov', 'tnstateparks.com', 'floridastateparks.org', 'bcparks.ca', 'pgc.pa.gov', 'dep.nj.gov', 'nj.gov', 'state.nj.us', 'fs.usda.gov', 'blm.gov', 'alapark.com',
                 'arkansasstateparks.com', 'agfc.com', 'apps.agfc.com', 'azstateparks.com', 'azgfd.com', 'gastateparks.org', 'ksoutdoors.com',
                 'michigan.gov', 'dnr.state.mi.us', 'www2.dnr.state.mi.us', 'mdwfp.com', 'fwp.mt.gov', 'nhstateparks.org', 'emnrd.state.nm.us',
                 'vtstateparks.com', 'parks.wa.gov', 'iowadnr.gov', 'dnr.illinois.gov', 'parksandrecreation.idaho.gov', 'dlnr.hawaii.gov',
                 'stateparks.utah.gov', 'mass.gov', 'portal.ct.gov', 'destateparks.com', 'usace.army.mil', 'parks.canada.ca', 'ontarioparks.ca',
                 'albertaparks.ca', 'tpwd.texas.gov', 'stateparks.com'}
MAPWORD = re.compile(r'\bmaps?\b|brochure|trail guide|geopdf|avenza|\bmapa\b|carte', re.I)
NOTMAP = re.compile(r'google\.|bing\.com|apple\.com/maps|mapquest|openstreetmap|waze|sitemap|site-map|\bmap of the site|roadmap|mapping tool|interactive map viewer|'
                    r'regulations|air-quality|water/gis|/gis/pages/default|gis\.myfwc\.com|recreationmap|public-?lands-?(map|viewer|finder)|statewide|/library$|laws-regulations', re.I)   # chat 8 F2, chat 11 fix 1
VIEWER = re.compile(r'gis\.myfwc\.com|recreationmap|/apps/|webappviewer|experience\.arcgis|mapviewer|portal/apps|statewide', re.I)
PLANW = re.compile(r'\bdraft\b|\bplans?\b|proposed|concept|master ?plan|management plan|environmental assessment', re.I)   # chat 8 F3: not the visitor map
NOTRULES = re.compile(r'air-?quality|laws-regulations|/library|privacy|accessibility|foia|/regulations/pages/default|environmental-protection|water-quality|permitting', re.I)   # chat 11 fix 2
# Oct 28 (chat 11 regrade 2): whole-government policy pages and an agency's data / GIS pages are never a park's rules or map
DENY = re.compile(r'court-rules|policies-and-links|admincode|admin-code|stamp-art|art-contest|inciweb|google\.[a-z.]+/maps|maps\.google|goo\.gl/maps|oversight\.gov|usdaoig|/oig/|kentucky\.gov/policies|/policies/pages/default|eec\.ky\.gov/energy|eec\.ky\.gov/environmental-protection|/data-maps/|/gis/pages/default|fs\.usda\.gov/visit/maps/?$|fs\.usda\.gov/maps/?$|/site-policies|/web-policies', re.I)
RULEWORD = re.compile(r'\brules?\b|regulations?|policies|laws? (and|&) policies|compendium|permits?|know before you go|r[èe]glements?|hunting (and|&) fishing regulations|park rules|ordinance', re.I)
ORG = r'(?:the )?(?:(?:City|County|Town|Village|Commonwealth|State|Parish|Municipality|Township) of [A-Z][\w.\'-]+(?: [A-Z][\w.\'-]+){0,2}|[A-Z][\w.&\'-]*(?: (?:of|and|&|for|the)| [A-Z][\w.&\'-]*){0,6}(?: (?:County|City|Fiscal Court|Parks(?: (?:and|&) Recreation)?|Department|Dept\.?|Division|Office|Service|Commission|Agency|District|Authority|Foundation|Trust|Conservancy|Corporation|Tribe|Nation|Township|Town|Village|Government|Board|Council|State)))\b'
HANDOVER = re.compile(r'((?:transferred|handed (?:over )?to|turned over|conveyed|now (?:managed|operated|owned|run)|will be (?:managed|operated|run)|no longer (?:managed|operated|owned|run)|took over|taken over|assumed (?:management|ownership)|as of (?:19|20)\d\d)[^.;]{0,60}?(?:to |by |from )?' + ORG + r'[^.;]{0,80}?(?:(?:19|20)\d\d|\bnow\b)[^.;]{0,40}[.;]|(?:in |since |as of )(?:20\d\d)[^.;]{0,80}?(?:transferred|handed (?:over )?to|turned over|now (?:managed|operated|owned|run) by|took over|taken over)[^.;]{0,80}?' + ORG + r'[^.;]{0,40}[.;])')
MANAGED = re.compile(r'((?:is |now |currently )?(?:managed|operated|owned|maintained|administered|co-?managed|run) (?:jointly )?by ' + ORG + r')(?=[.,;:(\n]|\s(?:and|which|that|in|for|under|through|as)\b)')
ABBR_END = re.compile(r'\b(?:U\.S|U\. S|St|Dr|Co|Inc|Mr|Mrs|Ms|Jr|Sr|No|Dept|Mt|Ft)\.$')
MONTHS = 'january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec'
PRINTED = [
    (re.compile(r'(?:date published|published|publication date|revised|revision|updated|last updated|updated on|map date|date of map|printed|produced|prepared|effective|current as of|as of|issued)\s*[:\-]?\s*((?:' + MONTHS + r')\.?\s+\d{1,2},?\s+(?:19|20)\d\d|\d{1,2}/\d{1,2}/(?:19|20)\d\d|(?:19|20)\d\d-\d\d-\d\d|(?:' + MONTHS + r')\.?\s+(?:19|20)\d\d|\d{1,2}/(?:19|20)\d\d|(?:19|20)\d\d)', re.I), 'printed on the map'),
    (re.compile(r'\b((?:' + MONTHS + r')\.?\s+(?:19|20)\d\d)\b', re.I), 'a month + year printed on the map'),
]
COPYR = re.compile(r'(?:©|\(c\)|copyright)\s*((?:19|20)\d\d)', re.I)   # Oct 28 (chat 8 B4): a base-map / template year, NEVER the map's date
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
    u = urllib.parse.quote(u, safe=":/?&=%#+~@,;$!*()'[]")   # chat 11: an address with spaces (University of the Cumberlands WMA) is sent escaped
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
    if NOTMAP.search(u) or NOTMAP.search(t) or DENY.search(u): return -9
    if not (MAPWORD.search(u) or MAPWORD.search(t)): return -9
    if VIEWER.search(u): return -9      # chat 8 F2: a statewide viewer is not THE park's map
    if PLANW.search(u) or PLANW.search(t): s -= 6   # chat 8 F3: a plan / draft is never the main map
    if u.endswith('.pdf') or '.pdf' in u: s += 4
    elif re.search(r'\.(jpe?g|png|gif)(\?|$)', u): s += 2
    elif re.search(r'/rest/services/|arcgis|mapserver|featureserver', u): s += 1
    else: s += 1
    if re.search(r'park map|property map|area map|boundary map|trail map|site map(?! of)|facility map|map of the', t): s += 3
    elif re.search(r'\bmap\b', t): s += 2
    if re.search(r'campground|camping|lodge|floor plan|golf|parking only|regional map|directions|driving|location map|vicinity', t + ' ' + u): s -= 2
    if re.search(r'hunt', t + ' ' + u): s += 1 if HUNTLAND.search(CUR.get('type', '') + ' ' + CUR.get('name', '')) else -3   # DOC-8: a hunting map is the park map for WMAs / game lands only, never a state park
    if agency_host and base_host(host_of(url)) == base_host(agency_host): s += 1
    return s


HUNTLAND = re.compile(r'wildlife management|\bwma\b|game land|hunting area|public hunting|wildlife area|\bgma\b|\bwha\b', re.I)
CUR = {}   # the park being read (type + name), for the scores
FORESTHOME = re.compile(r'fs\.usda\.gov/(?:r\d\d/)?[a-z-]+/?(?:home)?/?$', re.I)   # a national forest's home page (chat 11 KY regrade 3)
FORESTLVL = re.compile(r'fs\.usda\.gov/(?:r\d\d/)?[a-z-]+/(?:maps-pubs|visit/maps|maps)', re.I)


def rules_score(url, text):
    t = (text or '').lower(); u = url.lower()
    if not (RULEWORD.search(t) or RULEWORD.search(u)): return -9
    if re.search(r'permit', t + u) and not re.search(r'rules?|regulation', t + u): return -9   # a permit SHOP is not the rules (chat 8 B13)
    if NOTRULES.search(u) or NOTRULES.search(t) or DENY.search(u): return -9   # chat 11: air-quality regulations / a generic laws page / a library are not a park's rules
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
    if m and plausible(m.group(1)[:4]): return m.group(1), "the PDF file's own stamp (may be the print date, weaker than a printed date)"
    return '', ''


def date_from_url(u):
    """Oct 28 (chat 8 B5/B7, HQ): what the ADDRESS says is when the file was POSTED, never the map's own date. Returns
    (posted, how). Version / cache tails (sfvrsn, rev, v, hash) are not dates at all and are ignored."""
    p = urllib.parse.urlparse(u); path = urllib.parse.unquote(p.path)
    m = re.search(r'/((?:19|20)\d\d)[-/_](0[1-9]|1[0-2])(?:/|_|-|$)', path)
    if m and plausible(m.group(1)): return f'{m.group(1)}-{m.group(2)}', 'posted: the upload folder in the address'
    m = re.search(r'(?:^|[^0-9])((?:19|20)\d\d)[-_]?(0[1-9]|1[0-2])?(?:[-_]?(?:' + MONTHS + r'))?(?:pdf|\.pdf|[-_]|$)', path.rsplit('/', 1)[-1], re.I)
    if m and plausible(m.group(1)): return m.group(1) + (f'-{m.group(2)}' if m.group(2) else ''), "a year in the file's name (an edition hint, not a printed date)"
    m = re.search(r'/((?:19|20)\d\d)/', path)
    if m and plausible(m.group(1)): return m.group(1), 'posted: the upload folder in the address (year)'
    return '', ''


SOFT404 = re.compile(r'page not found|404 error|error 404|the page you (?:requested|are looking for)|no longer available|has been (?:moved|removed)|sign in to continue|log ?in required|access denied', re.I)
OVERVIEW = re.compile(r'\bregion(?:al)?\b.*\bmap\b|\boverview map\b|\bstatewide\b|\bparks and forests\b|\blocator map\b|\ball (?:state )?parks\b|\bdistrict map\b', re.I)


def check_url(u, want_text=True, name=''):
    """Open an address the polite way. Returns a dict: status, kind (pdf / page / image / arcgis / region overview),
    date (a PRINTED date only, else None) + date_how, posted (what the address / server says), names_park, text."""
    r = {'url': u, 'status': '', 'kind': '', 'date': None, 'date_how': '', 'final': u, 'posted': '', 'checked': TODAY}
    looks_pdf = u.lower().split('?')[0].endswith('.pdf')
    st, hd, body, final = get(u, rng=(0, PDF_FIRST - 1) if looks_pdf else None)
    r['status'] = 'ok' if st in (200, 206) else ('rest' if st == 'rest' else 'robots' if st == 'robots' else f'HTTP {st}' if isinstance(st, int) else str(st))
    r['final'] = final
    if r['status'] != 'ok': return r
    if VIEWER.search(final or u): r['status'] = 'opened, a statewide map viewer, not this park\'s map (chat 8 F2)'; r['kind'] = 'viewer (statewide)'; return r
    if DENY.search(final or u): r['status'] = 'opened, a government data / policies page, not this park\'s map (chat 11 regrade 2)'; r['kind'] = 'denied page'; return r
    if PLANW.search(urllib.parse.unquote((final or u).rsplit('/', 1)[-1])): r['status'] = 'opened, a plan / draft, not the visitor map (chat 8 F3)'; r['kind'] = 'plan'; return r
    ct = (hd.get('content-type') or '').lower()
    if looks_pdf and body[:5] != b'%PDF-' and 'application/pdf' not in ct:
        r['status'] = 'opened, wrong thing (a .pdf address that is not a PDF: a soft 404 or a login page)'; return r
    if body[:5] == b'%PDF-' or 'application/pdf' in ct:
        r['kind'] = 'pdf'
        if not looks_pdf and len(body) >= 3_000_000: body = body[:PDF_MAX]
        txt = pdf_first_page_text(body)
        if len(txt.strip()) < 20 and looks_pdf and int(hd.get('content-length', '0') or 0) > PDF_FIRST:
            st2, _, body2, _ = get(u, rng=(0, PDF_MAX - 1))
            if st2 in (200, 206): txt = pdf_first_page_text(body2)
        d, how = date_from_text(txt)
        if d: r['date'], r['date_how'] = d, how
        r['covers'] = covers(txt, name)   # DOC-4: a combined map naming several units
        cy = COPYR.search(txt)
        if cy: r['copyright'] = cy.group(1)   # kept apart: a template / base-map year, never the map date
        r['names_park'] = names_park(name, txt) if name else None
        if name and len(txt.strip()) < 300:                       # v6: a RASTER map (the name is in the picture): judge it by the file name only
            r['names_park'] = 'file' if names_park(name, file_words(final or u)) else None
            if r['names_park']: r['status_note'] = 'ok (park named in the file name; raster map)'
        elif name and r['names_park'] is False and names_park(name, file_words(final or u)):
            r['names_park'] = 'file'; r['status_note'] = 'ok (park named in the file name)'
        if OVERVIEW.search(txt[:3000]) and not r['names_park']: r['kind'] = 'region overview'
        if name and r['names_park'] is False and len(txt.strip()) > 80 and r['kind'] == 'pdf':
            r['status'] = 'opened, a readable map that does not name this park (chat 8 F2: another unit / several units)'; return r
        if r['date'] and str(r['date']).startswith(TODAY): r['date'], r['date_how'] = None, 'date unknown (the printed date is the day it was fetched: generated on request)'   # F5
    elif ct.startswith('image/') or re.search(r'\.(jpe?g|png|gif)(\?|$)', u, re.I):
        r['kind'] = 'image'; r['kind_note'] = 'image: the name is known from the file name only, not read from the map (chat 8 F9)'
        r['names_park'] = bool(name and names_park(name, urllib.parse.unquote(u.rsplit('/', 1)[-1]).replace('_', ' ').replace('-', ' ')))
    elif re.search(r'/rest/services/|mapserver|featureserver', u, re.I):
        r['kind'] = 'arcgis'
    else:
        r['kind'] = 'page'
        html = body.decode('utf-8', 'replace')
        txt = page_text(html)
        r['text'] = txt[:20000]; r['links'] = links_in(html, final)[:400]
        if len(txt) < 4000 and SOFT404.search(txt[:1500]):
            r['status'] = 'opened, wrong thing (the page says not found / sign in)'; return r
        m = re.search(r'(?:last updated|page last updated|updated|last modified|date modified)\s*[:\-]?\s*((?:' + MONTHS + r')\.?\s+\d{1,2},?\s+(?:19|20)\d\d|(?:19|20)\d\d-\d\d-\d\d|\d{1,2}/\d{1,2}/(?:19|20)\d\d)', txt, re.I)
        if m and plausible(re.search(r'(?:19|20)\d\d', m.group(1)).group()): r['posted'], r['posted_how'] = m.group(1), "page last updated (the page's own line, not the map's date; chat 8 F4)"
        r['names_park'] = names_park(name, txt) if name else None
        if name and not r['names_park'] and names_park(name, link_id_words(u)):   # v7 (chat 11, Oct 29): a viewer deep-linked by the area's own ID ('Viewer=Public_Access_Lands&ID=CYLON WILDLIFE AREA') IS that area's map
            r['names_park'] = 'link'; r['status_note'] = 'ok (park named in the link: an ID-addressed map viewer)'
        if name and r['names_park'] is False and len(txt) > 300: r['status'] = 'opened, a page that does not name this park (a generic agency page is not its map)'; return r
        if len(txt) < 300 and re.search(r'enable javascript|loading|<app-root|ng-app|__NEXT_DATA__|data-reactroot', html, re.I): r['shell'] = True
    if not r['posted']:
        d, how = date_from_url(final if final else u)
        if d: r['posted'], r['posted_how'] = d, how
    if not r['posted'] and hd.get('last-modified') and r['kind'] in ('pdf', 'image', 'region overview'):
        m = re.search(r'(\d{1,2}) ([A-Za-z]{3}) ((?:19|20)\d\d)', hd['last-modified'])
        if m and plausible(m.group(3)): r['posted'], r['posted_how'] = f'{m.group(2)} {m.group(1)}, {m.group(3)}', "posted: the server's file date"
    if r.get('date') and 'stamp' in str(r.get('date_how')) and r.get('posted'):
        ys, yp = re.search(r'(19|20)\d\d', str(r['date'])), re.search(r'(19|20)\d\d', str(r['posted']))
        if ys and yp and int(yp.group()) - int(ys.group()) > 1: r['date_how'] = f"file stamp {ys.group()} (older than the posting {yp.group()} by more than a year: a re-posted old map, this map may be old; chat 8 F5)"
    if not r['date']: r['date'], r['date_how'] = None, f'date unknown, checked {TODAY}'   # Oct 28 (HQ 3): never 'the day we read it' as a map date
    return r


AREA_NAMES = {}   # core name -> ref, every park of the area being read (DOC-4)
def covers(txt, name):
    """How many of the area's parks (incl. this one) a map's first page names."""
    if not txt or not AREA_NAMES: return 0
    t = low(txt[:20000]); n = 0
    for c in AREA_NAMES:
        if len(c) >= 6 and c in t: n += 1
    return n


def link_id_words(u):
    """v7: the VALUES of the link's ID / name / unit / area / property query parts, as words ('' when none)."""
    try: q = urllib.parse.parse_qsl(urllib.parse.urlparse(html_unescape(u)).query)
    except Exception: return ''
    return ' '.join(v.replace('_', ' ').replace('+', ' ') for k, v in q if k.lower() in ('id', 'name', 'unit', 'unitname', 'area', 'areaname', 'property', 'site', 'park', 'parkname', 'propname') and len(v) > 3)


def html_unescape(u):
    return u.replace('&amp;', '&')


def file_words(u):
    """'TeterCreekLakeFinal11x17_300dpi.pdf' -> 'Teter Creek Lake Final 11x17 300dpi' (the park name is in the file name of raster maps)."""
    b = urllib.parse.unquote(str(u).split('?')[0].rsplit('/', 1)[-1]).rsplit('.', 1)[0]
    b = re.sub(r'(?<=[a-z])(?=[A-Z])|(?<=[A-Za-z])(?=\d)|(?<=\d)(?=[A-Za-z])', ' ', b)
    return ' '.join(re.sub(r'[_\-+.]+', ' ', b).split())


def names_park(name, txt):
    """Does the map's first page name this park? (chat 8 B3: a sister park's or a region's map is not this park's map)"""
    c = core(name); t = low(txt[:8000])
    if not c: return None
    w = [x for x in c.split() if len(x) > 2]
    return bool(w) and sum(1 for x in w if re.search(r'\b' + re.escape(x) + r'\b', t)) >= max(1, len(w) - (1 if len(w) > 2 else 0))


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


def sentences(txt):
    """Whole sentences (an abbreviation list keeps 'U.S.' and 'St.' from ending one): chat 8 F6, never a cut sentence."""
    out, cur = [], ''
    for piece in re.split(r'(?<=[.!?])\s+(?=[A-Z("])', ' '.join((txt or '').split())):
        cur = (cur + ' ' + piece).strip() if cur else piece
        if ABBR_END.search(cur): continue
        out.append(cur); cur = ''
    if cur: out.append(cur)
    return out


def who_runs(texts, agency_name, park=''):
    """'runs' hints = whole sentences with an ORGANISATION after 'by' (never a person, a verb or 'beavers'); a HANDOVER needs a
    change word (transferred / now managed by / took over / as of <year>), an organisation, and a year of 2000 or later or 'now',
    inside one whole sentence that names the park when the park's name is known (chat 8 F6 / F7, chat 11 fix 4)."""
    hints, hand = [], []
    core_w = [w for w in core(park).split() if len(w) > 3][:3]
    for txt in texts:
        for sen in sentences(txt):
            if len(sen) > 400 or len(sen) < 25: continue
            for m in HANDOVER.finditer(sen):
                s = m.group(1).strip()
                yr = re.search(r'(19|20)\d\d', s)
                if yr and int(yr.group()) < 2000: continue
                if core_w and not any(re.search(r'\b' + re.escape(w) + r'\b', low(sen)) for w in core_w): continue
                if s not in hand: hand.append(sen[:300] if len(sen) <= 300 else s[:300])
            for m in MANAGED.finditer(sen):
                s = ' '.join(m.group(1).split())
                if re.search(r'\bby (?:the )?(?:periodic|prescribed|beaver|his |her |their |local |volunteer|a |an )', s, re.I): continue
                if len(s) < 120 and s not in hints: hints.append(s)
    return hints[:3], hand[:2]


AGENCYWIDE = set()


def rules_for(fam, urls, pg_rules, lists_entry):
    """Candidate rules pages in order; the first that OPENS is kept. Federal patterns first, then the page's own links, then the
    agency-wide rules page from lists.json."""
    cands = []
    slug = next((unit_slug(u, fam) for u in urls if unit_slug(u, fam)), '')
    if fam in FED_RULES and slug: cands += [(x.format(u=slug), f'{fam.upper()} rules page (pattern + opened)') for x in FED_RULES[fam]]
    if fam == 'usace': cands.append((USACE_RULES, 'Corps lakes: 36 CFR Part 327 (one national rule book) + the lake page'))
    cands += [(u, f"a link on the park's page ('{t}')") for s, u, t in pg_rules[:3]]
    if lists_entry and lists_entry.get('rules'): cands.append((lists_entry['rules'], 'the agency-wide rules page (chat 8 survey)'))
    AGENCYWIDE.clear(); AGENCYWIDE.update({lists_entry['rules']} if lists_entry and lists_entry.get('rules') else set())
    seen = set()
    cands = [(u, how) for u, how in cands if not DENY.search(u) and not FORESTHOME.search(u)]   # Oct 28 (chat 11): never a whole-government policies page, never a forest's home page
    for u, how in cands:
        if u in seen: continue
        seen.add(u)
        st, hd, body, final = get(u, head=False)
        if st in (200, 206):
            if DENY.search(final or ''): continue   # a redirect onto a site-policies page is not the rules
            out = {'url': final or u, 'how': how, 'status': 'ok'}
            if u in AGENCYWIDE or 'agency-wide' in how: out['rules_scope'] = 'agency'   # v6 (Fable): an agency-wide rules page is kept, labelled
            return out
        if st in ('rest', 'robots'): return {'url': u, 'how': how, 'status': 'rules page not read (the site is resting: next run)' if st == 'rest' else str(st)}
    return {'url': cands[0][0] if cands else '', 'how': cands[0][1] if cands else '', 'status': 'not found' if not cands else 'did not open'}


GOVFAM = [  # Oct 28 (HQ 1, chat 8 A1): hosts of the SAME government as the agency count as official (tourism + asset hosts)
    (r'(^|\.)ky\.gov$|kentuckytourism\.com$', 'Kentucky'), (r'(^|\.)ohio\.gov$|ohiodnr\.gov$', 'Ohio'), (r'(^|\.)nc\.gov$|ncparks\.gov$|ncwildlife\.gov$|ncagr\.gov$|visitnc\.com$', 'North Carolina'),
    (r'(^|\.)mo\.gov$|mostateparks\.com$|visitmo\.com$', 'Missouri'), (r'(^|\.)fl\.gov$|myflorida\.com$|floridastateparks\.org$|myfwc\.com$|fdacs\.gov$|floridadep\.gov$|sjrwmd\.com$|swfwmd\.state\.fl\.us$|sfwmd\.gov$', 'Florida'),
    (r'(^|\.)virginia\.gov$', 'Virginia'), (r'wvdnr\.gov$|wvstateparks\.com$|(^|\.)wv\.gov$', 'West Virginia'), (r'(^|\.)qld\.gov\.au$', 'Queensland'),
    (r'parks\.vic\.gov\.au$|(^|\.)vic\.gov\.au$', 'Victoria'), (r'(^|\.)nps\.gov$', 'NPS'), (r'(^|\.)fws\.gov$', 'FWS'), (r'(^|\.)usda\.gov$', 'USDA'),
    (r'(^|\.)blm\.gov$', 'BLM'), (r'usace\.army\.mil$', 'Army Corps'), (r'(^|\.)canada\.ca$|(^|\.)gc\.ca$', 'Canada'),
]
THIRD = re.compile(r'avenza|gaiagps|alltrails|onxmaps|trailforks|issuu|publuu|yumpu|scribd|dropbox|drive\.google|box\.com', re.I)


def gov_of(h):
    h = base_host(h)
    for pat, g in GOVFAM:
        if re.search(pat, h): return g
    m = re.search(r'\.(state\.[a-z]{2}\.us|[a-z]{2}\.gov)$', h)
    return m.group(1) if m else ''


def via_of(url, agency_host, linked, how):
    """How a map address is official (HQ 1): the agency's own host, a host the agency's page links to, or the same government."""
    h, a = base_host(host_of(url)), base_host(agency_host or '')
    if a and h == a: return 'the agency site'
    if url in linked: return f'third-party host, linked by the agency ({h})' if THIRD.search(h) else f'linked from the agency page ({h})'
    if THIRD.search(h): return 'off the government, not linked by the agency'   # DOC-10: Avenza / Gaia / AllTrails only through the agency's own link
    if a and gov_of(h) and gov_of(h) == gov_of(a): return f'same government ({h})'
    if str(how).startswith('on file'): return f'on file, checked by a person or the link harvester ({h})'
    if gov_of(h): return f'government host ({h})'
    return 'off the government, not linked by the agency'


def year_of(d):
    m = re.search(r'(19|20)\d\d', str(d or ''))
    return int(m.group()) if m else None


def pick_primary(ms):
    """Oct 28 (HQ 2 + chat 8 A2/B3/B10): the map that NAMES the park beats one that does not; a region overview is never primary
    while another map exists; when two printed dates are known and more than 3 years apart, the NEWER wins; otherwise the
    kind order (PDF, image, interactive map, page) and the agency's own host decide. Returns (primary, others)."""
    kind_rank = {'pdf': 4, 'image': 3, 'arcgis': 2, 'page': 1, 'region overview': 0}
    # DOC-11: two official maps of the same age -> the managing agency's own host first, the other as 'also'
    base = lambda m: (m.get('names_park') is not False, m['kind'] != 'region overview', m['via'] == 'the agency site', kind_rank.get(m['kind'], 1))
    best = sorted(ms, key=base, reverse=True)
    prim = best[0]
    for m in best[1:]:
        y1, y2 = year_of(prim.get('date')), year_of(m.get('date'))
        if y1 and y2 and y2 - y1 > 3 and m.get('names_park') is not False and m['kind'] != 'region overview':
            prim = dict(m, why_primary=f'newer map ({y2}) beats the older {prim["kind"]} ({y1}): more than 3 years apart'); break
    if prim['kind'] == 'region overview': prim = dict(prim, why_primary='only a region overview map was found', card_note='Overview map: no map of this park alone was found.')   # DOC-5
    if re.search(r'campground|camping', prim['url'] + ' ' + str(prim.get('how')), re.I): prim = dict(prim, kind_note='campground map (nothing better found)', card_note='Campground map: the agency has no park map.')   # DOC-3
    if prim.get('covers', 0) >= 2: prim = dict(prim, kind_note=f"combined map: covers {prim['covers']} units")   # DOC-4
    if THIRD.search(host_of(prim['url'])): prim = dict(prim, kind_note=(prim.get('kind_note', '') + '; ' if prim.get('kind_note') else '') + f"third-party app host ({base_host(host_of(prim['url']))}), linked by the agency")   # DOC-10
    y = year_of(prim.get('date'))
    if not y: prim = dict(prim, date_label='date unknown')   # DOC-6: never called current
    elif int(TODAY[:4]) - y > 5: prim = dict(prim, date_label=f'{y}: check it is still current')   # DOC-7: shown, never hidden
    else: prim = dict(prim, date_label=str(y))
    return prim, [m for m in best if m is not prim and m['url'] != prim['url']]


def one_park(ref, S, lists, area):
    CUR.clear(); CUR.update({'type': S.get('type', ''), 'name': S.get('name', '')})
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
    linked = {u for u, t in (pg.get('links') or [])} if pg and pg.get('status') == 'ok' else set()
    tried = []
    for u, how in cands[:4]:   # Oct 28 (chat 8 A2 / B3): up to 4 candidates are opened, then the PRIMARY is chosen (never just the first)
        if late(): break
        r = check_url(u, name=S['name'])
        m = {'url': r['final'] or u, 'status': r['status'], 'kind': r['kind'], 'date': r['date'], 'date_how': r['date_how'], 'how': how,
             'posted': r.get('posted', ''), 'posted_how': r.get('posted_how', ''), 'names_park': r.get('names_park'), 'checked': TODAY, 'covers': r.get('covers', 0)}
        if r.get('copyright'): m['copyright'] = r['copyright']
        if r['status'] == 'ok' and r['kind'] == 'page':
            texts.append(r.get('text', ''))
            if r.get('shell'): rec['needs_browser'] = 'the map page is built by script'
            # a map PAGE that links a PDF: take the PDF as the map, keep the page as its source
            pm2, pr2 = find_on_page(r, agency_host)
            page_rules = page_rules or pr2
            linked |= {x[1] for x in pm2}
            pdfs = [x for x in pm2 if '.pdf' in x[1].lower()]
            if pdfs and not late():
                r2 = check_url(pdfs[0][1], name=S['name'])
                if r2['status'] == 'ok':
                    m.update({'url': r2['final'], 'kind': r2['kind'], 'date': r2['date'], 'date_how': r2['date_how'], 'how': how + f" -> the page's '{pdfs[0][2]}' file",
                              'page': r['final'], 'posted': r2.get('posted', ''), 'posted_how': r2.get('posted_how', ''), 'names_park': r2.get('names_park'), 'covers': r2.get('covers', 0)})
        m['via'] = via_of(m['url'], agency_host, linked, how)
        tried.append(m)
        if r['status'] in ('HTTP 403', 'HTTP 406') or (r['status'] == 'ok' and r.get('shell')): rec['needs_browser'] = f'the map link refused a plain reader ({r["status"]})'
        if r['status'] == 'ok' and m['kind'] == 'pdf' and m.get('names_park') and m['via'] != 'off the government, not linked by the agency': break   # a PDF that names the park: good enough
    ok = [m for m in tried if m['status'] == 'ok' and m['via'] != 'off the government, not linked by the agency']
    if ok:
        prim, also = pick_primary(ok)
        rec['map'] = prim
        if also: rec['map_also'] = also[:2]
        STAT['maps_ok'] += 1
        if not str(prim['how']).startswith('on file'): STAT['maps_found'] += 1
        if prim.get('date'): STAT['dates'] += 1
    elif tried:   # Oct 28 (chat 11): a link that answered with an error is never kept as the map; what was tried stays for a person
        rec['map'] = {'url': '', 'status': 'no working map link (tried: ' + '; '.join(f"{t['status']} {t['url'][:70]}" for t in tried[:3]) + ')', 'how': tried[0].get('how', '')}
        rec['map_tried'] = tried[:3]
    if rec['map'] is None and not cands: rec['map'] = {'url': '', 'status': 'no map link on file and none on the park page', 'how': ''}
    if rec['map'] and rec['map'].get('status') == 'ok' and base_host(host_of(rec['map']['url'])) in BROWSER_HOSTS and rec['map'].get('kind') == 'page': rec['needs_browser'] = 'map page on the browser list (a download button may hide the file)'
    # 3 the rules page
    if not late():
        urls = [S['page']] + [c[0] for c in cands]
        rec['rules'] = rules_for(fam, [u for u in urls if u], page_rules, le)
        if rec['rules']['status'] == 'ok': STAT['rules'] += 1
    # 4 who runs it
    hints, hand = who_runs(texts, rec['agency'], S['name'])
    rec['runs'] = hints; rec['handover'] = hand
    if hand:
        STAT['handovers'] = STAT.get('handovers', 0) + 1
        m = re.search(r'(?:to|by) ' + ORG, hand[0])
        new = (m.group(0)[3:] if m else re.sub(r'^.*?(?:to|from|by) (?:the )?', '', hand[0])).strip(' .,')
        new = re.split(r'\s+(?:in|on|since|effective|as of|during|from|which|that)\b|\s+\d', new)[0].strip(' .,') or new
        # Oct 28 (HQ 4, Brandon OK): a POTA-numbered park STAYS on the card; the card warns and names the source
        rec['card_note'] = f'May now be run by {new}: check before you go.'
        rec['handover_src'] = S['page'] or ((rec.get('map') or {}).get('page') or '')
    mn = (rec.get('map') or {}).get('card_note')   # DOC-3 / DOC-5: the map's own note on the card too
    if mn: rec['card_note'] = (rec['card_note'] + ' ' if rec.get('card_note') else '') + mn
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
                rec['map'] = {'url': r['final'] or got['url'], 'status': r['status'], 'kind': r['kind'], 'date': r['date'], 'date_how': r['date_how'], 'how': got['how'], 'page': url,
                              'posted': r.get('posted', ''), 'posted_how': r.get('posted_how', ''), 'checked': TODAY, 'via': via_of(r['final'] or got['url'], agency_host, {got['url']}, got['how'])}
                r = dict(r, final=r['final'] or got['url'])
                if r['status'] == 'ok': STAT['maps_ok'] += 1; STAT['maps_found'] += 1
            if (not rec.get('rules') or rec['rules'].get('status') != 'ok') and pr:
                st, _, _, final = get(pr[0][1])
                if st in (200, 206): rec['rules'] = {'url': final, 'how': f"a link on the page in a browser ('{pr[0][2]}')", 'status': 'ok'}; STAT['rules'] += 1
            hints, hand = who_runs([text], rec.get('agency'), rec.get('n', ''))
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
    AREA_NAMES.clear(); AREA_NAMES.update({core(v[0] if isinstance(v, (list, tuple)) else (v.get('name', '') if isinstance(v, dict) else v)): k for k, v in parks.items()})
    done = 0; fresh = 0
    for ref in sorted(parks):
        if late(): break
        old = D['parks'].get(ref)
        if old and old.get('ver', 1) >= VER and old.get('checked', '') >= time.strftime('%Y-%m-%d', time.gmtime(time.time() - REFRESH_DAYS * 86400)):
            fresh += 1; STAT['skipped_fresh'] += 1; continue
        S = seeds(ref, parks, web, ky if area == 'US-KY' else {})
        try:
            D['parks'][ref] = one_park(ref, S, lists, area); D['parks'][ref]['ver'] = VER
            nm, om = D['parks'][ref].get('map') or {}, (old or {}).get('map') or {}
            if not nm.get('url') and om.get('url') and re.search(r'(?:^|[(;:] )rest https?://', str(nm.get('status') or '')):   # tune Oct 29: kept on rest (no VER bump)
                D['parks'][ref]['map'] = dict(om, kept=f"{TODAY}: kept the last good map: the host was resting (our strikes), not a dead link")   # tune Oct 29 (WI 294 -> 113: dnrmaps.wi.gov rested after 3 strikes)
                STAT['kept_on_rest'] = STAT.get('kept_on_rest', 0) + 1
        except Exception as e:  # noqa: BLE001
            D['parks'][ref] = {'n': S['name'], 'checked': TODAY, 'map': {'url': '', 'status': 'bot error: ' + str(e)[:80]}, 'rules': None, 'notes': []}
            STAT['errors'] += 1
        done += 1; STAT['parks'] += 1
    if BROWSER and not late():
        browser_pass(area, D, parks, max(60, LIMIT - (time.time() - T0) - 60))
    shared_pass(D, lists.get(area, {}))
    if area == 'US-KY' and not late(): ky_finder_check(D, parks, ky, web)
    shared_scope(D)
    before = (load(f, {}) or {}).get('counts') or {}
    D['read'] = TODAY; D['counts'] = counts(D)
    b_maps, b_rules = before.get('map ok'), before.get('rules ok')
    notice(f"{area} COUNT: maps with a link {b_maps if b_maps is not None else '?'} -> {D['counts']['map ok']}, rules {b_rules if b_rules is not None else '?'} -> {D['counts']['rules ok']}, maps named by file name {sum(1 for r in D['parks'].values() if (r.get('map') or {}).get('names_park') == 'file')}")
    if b_maps and b_maps >= 20 and D['counts']['map ok'] < .85 * b_maps:   # v6 (Fable d): a map drop over 15% keeps the saved copy; the new one waits beside it
        save(OUT / 'held' / f'{area}.json', D)
        notice(f"{area} GATE FAIL: maps {b_maps} -> {D['counts']['map ok']} (over 15% fewer): the saved copy is kept, the new file is in data/docs/held/")
        state['areas'][area] = {'status': 'failed', 'parks': len(parks), 'updated': TODAY, 'why': f'maps {b_maps} -> {D["counts"]["map ok"]}'}
        return
    save(f, D)
    left = sum(1 for r in parks if r not in D['parks'])
    state['areas'][area] = {'status': 'done' if left == 0 else 'partial', 'parks': len(parks), 'checked': len(D['parks']), 'left': left, 'updated': TODAY}
    notice(f"{area}: {done} parks checked this chunk ({fresh} fresh, {left} left) · {D['counts']}")


def shared_pass(D, lists_area):
    """Oct 28 (chat 11, chunks 1-3): ONE rules page given to 20+ parks (WV: 83 on a whitewater-commission page; FL: 53 on a shooting-
    range page) is not each park's rules unless it is the agency-wide rules page on file for that park's own agency; ONE map
    file given to 20+ parks (GA: 130 on a flip-book) is not each park's map. Those are dropped with the reason. A map that is a
    national forest's maps page is labelled 'forest map only'."""
    from collections import Counter
    agency_rules = {(e or {}).get('rules') for e in (lists_area or {}).values()} - {None, ''}
    ps = D.get('parks') or {}
    ru = Counter((p.get('rules') or {}).get('url') for p in ps.values() if (p.get('rules') or {}).get('status') == 'ok')
    mp = Counter((p.get('map') or {}).get('url') for p in ps.values() if (p.get('map') or {}).get('status') == 'ok')
    n_r = n_m = n_f = 0
    for p in ps.values():
        r = p.get('rules') or {}
        if r.get('status') == 'ok' and ru[r.get('url')] >= 20 and r.get('url') not in agency_rules:
            p['rules'] = {'url': '', 'status': f"not found (a page shared by {ru[r.get('url')]} parks was dropped: {r.get('url')[:90]})", 'how': r.get('how', '')}; n_r += 1
        m = p.get('map') or {}
        # Oct 29 (chat 11, docs v7 South 83%): ONE map file on 5+ parks (the Indiana Museum map on 10 historic sites, the FWS rivers
        # map on 5 wild and scenic rivers) is the AGENCY's map, not each park's: dropped too, unless it is a real multi-park NPS page
        if m.get('status') == 'ok' and m.get('kind') != 'region overview' and (mp[m.get('url')] >= 20 or (mp[m.get('url')] >= 5 and 'nps.gov' not in (m.get('url') or ''))):
            p['map'] = {'url': '', 'status': f"no map (one file shared by {mp[m.get('url')]} parks was dropped: {m.get('url')[:90]})", 'how': m.get('how', '')}; n_m += 1
        elif m.get('status') == 'ok' and FORESTLVL.search(m.get('url') or ''):
            m['kind_note'] = (m.get('kind_note', '') + '; ' if m.get('kind_note') else '') + 'forest map only'; n_f += 1
    if n_r or n_m or n_f: notice(f"{D.get('area')}: shared pages dropped: rules {n_r}, maps {n_m}; forest-level maps labelled {n_f}")


def ky_finder_check(D, parks, ky, web):
    """Kentucky answer-key check: for SAMPLE parks that have a hand-checked map link, would the bot have FOUND it from the park's
    page alone (seed hidden)? Written into the file as 'finder_check' for chat 8."""
    n = int(os.environ.get('SAMPLE') or 25)
    refs = [r for r in sorted(parks) if (ky.get(r) or {}).get('off') and (parks[r][1] or '').startswith('http') and 'pota.app' not in parks[r][1]][:n]
    out = {'sample': len(refs), 'same': 0, 'other_map': 0, 'other_map (does not name the park)': 0, 'none': 0, 'rows': [], 'rules': f'v{VER}'}
    norm = lambda u: re.sub(r'^https?://(www\.)?', '', (u or '').lower()).split('?')[0].rstrip('/')
    for r in refs:
        if late(): break
        S = seeds(r, parks, web, {}); S['maps'] = []   # the seed hidden
        rec = one_park(r, S, {}, 'US-KY')
        found = (rec.get('map') or {}).get('url') or ''
        want = ky[r]['off']
        k = 'same' if found and norm(found) == norm(want) else 'other_map' if found and (rec['map'].get('status') == 'ok') else 'none'
        if k == 'other_map' and rec['map'].get('names_park') is False: k = 'other_map (does not name the park)'
        out[k] += 1
        out['rows'].append({'ref': r, 'n': parks[r][0], 'answer': want, 'bot': found, 'verdict': k})
    D['finder_check'] = out
    notice(f"Kentucky finder check (seed hidden): same map {out['same']}, another map {out['other_map']}, none {out['none']} of {out['sample']}")


def shared_scope(D):
    """v6: a rules page used by 10+ parks of the area is the agency's page: labelled rules_scope 'agency' (kept, never 'the park's own rules')."""
    from collections import Counter
    c = Counter((r.get('rules') or {}).get('url') for r in D['parks'].values() if (r.get('rules') or {}).get('status') == 'ok')
    for r in D['parks'].values():
        ru = r.get('rules') or {}
        if ru.get('url') and c[ru['url']] >= 10: ru['rules_scope'] = 'agency'


def counts(D):
    P = D['parks'].values()
    c = {'parks': len(D['parks']), 'map ok': 0, 'map found by the bot': 0, 'date on the map': 0, 'posted date only': 0, 'date unknown': 0, 'no map': 0, 'rules ok': 0,
         'needs browser': 0, 'handover hints': 0, 'runs hints': 0, 'host resting / robots': 0, 'map names the park': 0, 'region overview only': 0}
    for p in P:
        m = p.get('map') or {}
        if m.get('status') == 'ok':
            c['map ok'] += 1
            if not str(m.get('how', '')).startswith('on file'): c['map found by the bot'] += 1
            if m.get('date'): c['date on the map'] += 1          # printed on the map, or the PDF's own stamp (labelled weaker)
            elif m.get('posted'): c['posted date only'] += 1     # the upload folder / file name / server date: when it was POSTED
            else: c['date unknown'] += 1
            if m.get('names_park'): c['map names the park'] += 1
            if m.get('kind') == 'region overview': c['region overview only'] += 1
        elif m.get('status') in ('rest', 'robots'): c['host resting / robots'] += 1
        else: c['no map'] += 1
        if (p.get('rules') or {}).get('status') == 'ok': c['rules ok'] += 1
        if p.get('needs_browser') and not p.get('browser_checked'): c['needs browser'] += 1
        if p.get('handover'): c['handover hints'] += 1
        if p.get('runs'): c['runs hints'] += 1
    return c


def review(state):
    L = ['# Official documents bot: review list (hidden; for chat 8)', f'Updated {TODAY}. One file per area in data/docs/<area>.json: per park the official MAP (link, kind, date + how the date was found), the RULES page (link + how), who runs it (hints from the page) and HANDOVER hints. Nothing here reaches a card until chat 8 grades a sample and Brandon says GO.', '',
         'Dates (Oct 28 rules): **date on the map** = printed on it (or the PDF file stamp, labelled weaker); **posted** = when the file was put online (upload folder, file name, server date): never called the map date; **date unknown** = neither (the card says \'date unknown, checked <day>\'). A © year and version tails (sfvrsn) are never dates.', '',
         '| area | parks | map ok | found by the bot | names the park | date on the map | posted only | date unknown | no map | rules ok | needs browser | handover notes |', '|---|---|---|---|---|---|---|---|---|---|---|---|']
    for area in QUEUE:
        f = OUT / f'{area}.json'
        if not f.exists(): continue
        D = load(f, {}); c = D.get('counts') or counts(D)
        L.append(f"| {area} | {c['parks']} | {c['map ok']} | {c['map found by the bot']} | {c.get('map names the park', 0)} | {c['date on the map']} | {c.get('posted date only', 0)} | {c.get('date unknown', 0)} | {c['no map']} | {c['rules ok']} | {c['needs browser']} | {c['handover hints']} |")
    for area in QUEUE:
        f = OUT / f'{area}.json'
        if not f.exists(): continue
        D = load(f, {})
        import random as _rnd
        groups = {}
        for ref, p in sorted(D['parks'].items()):
            if (p.get('map') or {}).get('status') != 'ok': continue
            groups.setdefault(base_host(host_of(p['map'].get('url') or '')).split('.')[-2] if '.' in base_host(host_of(p['map'].get('url') or '')) else 'other', []).append(ref)
        _rnd.seed(28); pick = []
        for g in sorted(groups): pick += _rnd.sample(groups[g], min(12, len(groups[g])))   # chat 8 F10: a random 12 per agency group
        L += ['', f'## {area} sample (random 12 per agency group, seed 28)', '| ref | park | map | kind · via | date (how) · posted / page updated | rules | runs / card note |', '|---|---|---|---|---|---|---|']
        n = 0
        for ref in pick:
            p = D['parks'][ref]; m = p.get('map') or {}
            ru = (p.get('rules') or {})
            L.append(f"| {ref} | {p.get('n','')[:40]} | {m.get('url','')[:90]} | {m.get('kind','')}{' ✓name' if m.get('names_park') else ''}{(' · ' + m['kind_note'][:40]) if m.get('kind_note') else ''} · {str(m.get('via',''))[:40]} | {m.get('date_label') or m.get('date') or '—'} ({m.get('date_how','')[:45]}) · posted {m.get('posted') or '—'} | {(ru.get('url') or '')[:70] + (' ✓' if ru.get('status') == 'ok' else ' ✗') if ru else ''} | {(p.get('card_note') or '; '.join((p.get('runs') or [])[:1]))[:90]} |")
            n += 1
        hand = [(ref, p) for ref, p in D['parks'].items() if p.get('handover')]
        if hand:
            L += ['', f'### {area} HANDOVER notes ({len(hand)}): the park STAYS on the card with the note (HQ Oct 28); a person checks the source', *[f"- {ref} {p.get('n','')}: {' / '.join(p['handover'])} → card: '{p.get('card_note','')}' (source {p.get('handover_src','')})" for ref, p in hand[:30]]]
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
    def stale(a):   # an area whose records were made by an older rule set is read again (VER)
        try: return any((p.get('ver') or 1) < VER for p in (load(OUT / f'{a}.json', {}).get('parks') or {}).values())
        except Exception: return False  # noqa: BLE001
    areas = [a for a in want if a in QUEUE] if want else [a for a in QUEUE if (state['areas'].get(a) or {}).get('status') != 'done' or stale(a)]
    if want and not areas: notice('no known area in AREAS'); return
    web = (load('data/parkinfo-web.json', {}) or load(LINKS / 'data/parkinfo-web.json', {})).get('parks') or {}
    lists = load(OUT / 'lists.json', {}).get('areas') or {}
    ky = ky_answers()
    if os.environ.get('FINDER_ONLY') == '1':   # Oct 28 (HQ): rerun ONLY Kentucky's finder check with the fixed rules
        f = OUT / 'US-KY.json'; D = load(f, {'area': 'US-KY', 'parks': {}})
        ky_finder_check(D, park_list('US-KY'), ky, web); save(f, D); review(state); return
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
