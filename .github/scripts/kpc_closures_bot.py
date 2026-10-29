#!/usr/bin/env python3
"""THE CLOSURES SUPER-BOT (Fable, chat 10 'bot workshop', Oct 28 2026). RULE SHEET D, ruled by Brandon Oct 28 (CL-1..CL-8),
on top of RULE SHEET A (G1-G13), the Georgia sheet (GA1-GA4) and chat 8's fixes D-R1..D-R8.

WHAT IT DOES, in plain words
  For every US state and Canadian province it reads the official closure / alert sources we know, in this order:
    1. the agency's own machine-readable feed (the 10 state feeds copied from KPC-Links kpc_us_closures.py, the Kentucky State
       Parks alert list, the National Park Service alerts API when the NPS_API_KEY secret exists),
    2. the agency's own closures / alerts PAGE read politely as text (KPC-Links data/closure-pages.json's 49 pages, Georgia's
       closures page, Kentucky Fish and Wildlife, the rows chat 8 adds to data/closures/sources.json),
    3. federal units by pattern: Forest Service 'alerts-notices' pages and Fish and Wildlife Service refuge pages found from the
       parks' own web pages in data/parkinfo,
    4. Parks Canada 'Important bulletins' pages (English read; French kept beside it for Quebec and New Brunswick).
  Every notice is cut into sentences. A sentence counts as a CLOSURE only when it has a closing word, an object we can name and
  no 'not / reopened / remains open' in it (D-R1). It is tied to ONE park by name (the US answer key's name rules); a notice
  that fits two parks or none goes to the 'unmatched' list. Then it is classed:
    whole (the park itself) · part (a named road, trail, campground, ramp, unit...) · hunt (closed to all but drawn / quota
    hunters on dates) · seasonal (published with dates every year) · note (vehicles-only, facility closed, permit needed,
    caution, 'may not be public land now', hunting season, camping / fire rule).
  'details' is ALWAYS the agency's own sentence in quotes, never our words. Dates come from the sentence; 'Updated m/d/yy' on a
  page is the agency's date and runs the stale clock (90 days open-ended, 30 for emergencies, a year for named long-term work;
  over a year old = shown with 'may be out of date', GA1).
  A source that fails keeps its last items. An item leaves only after 2 good reads without it, and then says 'notice taken
  down: check the agency page' for a week (A5). The same closure from two sources is merged, both links kept (A6). Eight or
  more parks closed by one notice = one state banner plus the park items (G7).

WHAT IT WRITES (its own folder only; nothing here reaches a card until Brandon's GO, CL-5)
  data/closures/<area>.json   one file per state / province: sources read, items (also in the 'uc-' field shape the cards'
                              merge already takes), banners, the unmatched list
  data/closures/review.md     per area: counts per class, unmatched notices, failed sources; for Kentucky the SIDE-BY-SIDE
                              against Kentucky's own reader (kpc_park_alerts.py) and for the 10 feed states against
                              data/alerts/us-parks.json, so chat 11 can grade it
  data/closures/state.json    what was read when, resting hosts, the Kentucky test, and 'proven' (set by a person)

HOW TO RUN
  env AREAS='US-KY US-TN' (blank = every area not read in the last REFRESH_H hours, Kentucky first) · MINUTES (55) · LINKS (the
  KPC-Links checkout, default 'links') · OUT (data/closures) · TEST=1 (Kentucky gate: PASS when 80% of Kentucky's own reader's
  current closure items are found here on the same park; prints 'TEST=PASS|FAIL') · OFFLINE=1 (no web: plumbing tests) ·
  NPS_API_KEY, RIDB_API_KEY (secrets; skipped with a status line when absent). `--selftest` runs the sentence and matcher tests
  with no web at all. Prints 'LEFT=<n>' (areas still to read this cycle). Never fails (exit 0).
"""
import csv, datetime as dt, email.utils, html as _html, io, json, os, pathlib, re, sys, time, types, urllib.parse
import xml.etree.ElementTree as ET

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from kpc_manners import Manners, page_text, links_in, pdf_text  # noqa: E402
try: from kpc_manners import browser_text  # noqa: E402
except Exception: browser_text = lambda u, M: ''  # noqa: E731,E722

BOT = 'closures super-bot'
OUT = pathlib.Path(os.environ.get('OUT') or 'data/closures')
LINKS = pathlib.Path(os.environ.get('LINKS') or 'links')
T0 = time.time(); LIMIT = float(os.environ.get('MINUTES') or 55) * 60
OFFLINE = os.environ.get('OFFLINE') == '1'
TEST = os.environ.get('TEST') == '1'
REFRESH_H = float(os.environ.get('REFRESH_H') or 5)
NPS_KEY = (os.environ.get('NPS_API_KEY') or '').strip()
RIDB_KEY = (os.environ.get('RIDB_API_KEY') or '').strip()
TODAY = dt.date.today()
NOW = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%MZ')
NEAR_KM = 40            # a feed notice with a location must sit within this of the park's pin (Sheet A rule 2)
RSS_DAYS = 45           # a news-style post older than this is not shown (Sheet A rule 2)
MASS = 8                # G7: this many parks closed by ONE notice = a state banner too
PDF_FIRST = 400_000     # CL-7: PDF lists read by range, first 400 KB
GONE_READS = 2          # A5: an item leaves only after this many good reads without it
TAKEN_DOWN_DAYS = 7     # ... and then says 'notice taken down' for this long
UPCOMING_DAYS = 14      # D9: a future closure shows from 14 days before its start
VER = 4   # v4 chat 11 round-3 grade: protection orders, other-state names first, ended items dropped, title twins merged, sentence-start subjects
VER_OLD = 3   # Oct 28: v2 HQ fixes 1-5 (hunt pages, home parks, state filter, standing rules, safe URLs); v3 chat 11's regrade (named place + close verb, KDFWR wording, debug snippets)

QUEUE = ['US-KY',
         'US-TN', 'US-NC', 'US-VA', 'US-WV', 'US-GA', 'US-AL', 'US-SC', 'US-FL', 'US-MS',
         'US-IN', 'US-IL', 'US-MO', 'US-WI', 'US-MN', 'US-IA', 'US-ND', 'US-SD', 'US-MI', 'US-OH',
         'US-PA', 'US-NY', 'US-NJ', 'US-CT', 'US-RI', 'US-MA', 'US-VT', 'US-NH', 'US-ME', 'US-MD', 'US-DE', 'US-DC',
         'US-AR', 'US-LA', 'US-OK', 'US-TX', 'US-KS', 'US-NE',
         'US-CO', 'US-WY', 'US-ID', 'US-MT', 'US-NV', 'US-AZ', 'US-NM', 'US-UT',
         'US-CA', 'US-OR', 'US-WA', 'US-AK', 'US-HI',
         'CA-ON', 'CA-QC', 'CA-NB', 'CA-NS', 'CA-PE', 'CA-NL', 'CA-MB', 'CA-SK', 'CA-AB', 'CA-BC', 'CA-YT', 'CA-NT', 'CA-NU']
FRENCH_AREAS = {'CA-QC', 'CA-NB'}     # G9 / CL-6: French kept beside the English
M = None
STAT = {'requests': 0, 'pages': 0, 'pdfs': 0, 'sentences': 0, 'items': 0, 'unmatched': 0, 'unreadable': 0, 'sources_failed': 0}


def notice(m): print('::notice title=Closures super-bot::' + str(m).replace('%', '%25').replace('\n', ' ')[:900], flush=True)
def late(): return time.time() - T0 > LIMIT
def load(p, d):
    try: return json.load(open(p, encoding='utf-8'))
    except Exception: return d  # noqa: BLE001
def save(p, obj):
    pathlib.Path(p).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(p).write_text(json.dumps(obj, ensure_ascii=False, indent=1, sort_keys=True) + '\n', encoding='utf-8')
def clean(s, cap=600):
    s = _html.unescape(re.sub(r'<[^>]+>', ' ', str(s or '')))
    return re.sub(r'\s+', ' ', s).strip()[:cap]
def slug(s, n=50): return re.sub(r'[^a-z0-9]+', '-', str(s or '').lower()).strip('-')[:n]
def lowtext(x): return ' '.join(re.sub(r'[^a-z0-9 ]', ' ', str(x or '').lower().replace('&', ' and ')).split())


def km(a, b, c, d):
    import math
    p = math.pi / 180
    h = math.sin((c - a) * p / 2) ** 2 + math.cos(a * p) * math.cos(c * p) * math.sin((d - b) * p / 2) ** 2
    return 12742 * math.asin(math.sqrt(h))


# ======================================================================================= the answer key's name rules
def _key():
    """The US answer key's name rules (norm / kinds / name_ok / same_kind), loaded without running the key itself: copied from
    kpc_us_closures._key(). kpc_match and kpc_save are imported from the KPC-Links checkout."""
    scripts = LINKS / '.github' / 'scripts'
    if str(scripts) not in sys.path: sys.path.insert(0, str(scripts))
    p = scripts / 'kpc_us_key.py'
    src = p.read_text(encoding='utf-8').split('\nidx = {}\n')[0]
    m = types.ModuleType('kpc_us_key'); m.__file__ = str(p)
    so = sys.stdout
    try:
        sys.stdout = io.StringIO()                  # the key prints a line about data/state-gis.json when it is not there
        exec(compile(src, 'kpc_us_key.py', 'exec'), m.__dict__)
    finally:
        sys.stdout = so
    return m


class _PlainKey:
    """Fallback when the KPC-Links checkout is missing: plain name rules (never used on a runner: the workflow checks out links)."""
    GEN = re.compile(r'\b(state|national|park|parks|forest|wildlife|management|area|wma|pfa|refuge|recreation|historic|historical|site|preserve|natural|nature|lake|public|fishing|the|of|and)\b')
    def norm(self, s): return ' '.join(re.sub(r'[^a-z0-9 ]', ' ', str(s or '').lower()).split())
    def kinds(self, s): return set()
    def same_kind(self, a, b): return True
    def name_ok(self, a, b, ka, kb):
        ca, cb = ' '.join(self.GEN.sub(' ', self.norm(a)).split()), ' '.join(self.GEN.sub(' ', self.norm(b)).split())
        return bool(ca) and ca == cb


# the agencies' short forms (copied from kpc_us_closures.SHORT; 'ST' is State Trail, not Saint) + PFA / VPA for Georgia
SHORT = [(r'\bSHP\b', 'State Historical Park'), (r'\bSHS\b', 'State Historic Site'), (r'\bSB\b', 'State Beach'),
         (r'\bSVRA\b', 'State Vehicle Recreational Area'), (r'\bSNR\b', 'State Natural Reserve'), (r'\bSP\b', 'State Park'),
         (r'\bSF\b', 'State Forest'), (r'\bST\b', 'State Trail'), (r'\bSWA\b', 'State Wildlife Area'),
         (r'\bWA\b$', 'Wildlife Area'), (r'\bFAS\b', 'Fishing Access Site'), (r'\bPFA\b', 'Public Fishing Area'),
         (r'\bVPA\b', 'Voluntary Public Access Area'), (r'\bNWR\b', 'National Wildlife Refuge'), (r'\bNF\b', 'National Forest')]
UNIT_RX = re.compile(r"[\s,(]*\b(Unit|Tract|Section|Area|Compartment|Zone)\s+([A-Z0-9][\w-]*)\)?\s*$", re.I)


def unit_split(name):
    """'Peabody WMA Unit 2' -> ('Peabody WMA', 'Unit 2')"""
    m = UNIT_RX.search(str(name or ''))
    if not m: return str(name or ''), ''
    return str(name)[:m.start()].strip(' ,('), f'{m.group(1).capitalize()} {m.group(2)}'


def match(K, row, parks, st=''):
    """Which parks does a row with a 'name' (and maybe a location 'at') belong to? Copied from kpc_us_closures.match():
    the key's name rules + SHORT forms + within NEAR_KM of the pin when the feed gives a location."""
    hit = []
    if row.get('name'):
        nm, _unit = unit_split(str(row['name']))
        for rx, full in SHORT: nm = re.sub(rx, full, nm)
        kn = K.kinds(nm)
        for ref, (pn, typ, la, lo, *_w) in parks.items():
            if row.get('at') and la is not None and km(la, lo, *row['at']) > NEAR_KM: continue
            if K.name_ok(pn, nm, K.kinds(pn) | K.kinds(typ), kn): hit.append(ref)
        if hit or not row.get('at'): return hit
        have = set(K.norm(nm).split())
        for ref, (pn, typ, la, lo, *_w) in parks.items():
            if la is None or km(la, lo, *row['at']) > 15: continue
            core = [w for w in K.norm(pn).split() if w != st.lower()]
            if core and len(' '.join(core)) >= 6 and set(core) <= have and K.same_kind(K.kinds(pn) | K.kinds(typ), kn): hit.append(ref)
        return hit
    return match_hay(K, row.get('hay') or '', parks)


# the park's own name inside free text (copied from kpc_park_alerts.match_parks: a one-word short name only counts when a
# park-ish word follows it, and a place word after the match that is not in our park's name means another place)
NEXTW = ('lake', 'park', 'parks', 'wma', 'forest', 'trail', 'trails', 'campground', 'preserve', 'area', 'site', 'river', 'creek', 'falls', 'refuge')
PLACEN = ('ferry', 'lake', 'river', 'creek', 'fork', 'branch', 'run', 'falls', 'forest', 'park', 'wilderness', 'wma', 'bridge', 'trail',
          'trails', 'campground', 'preserve', 'mountain', 'gorge', 'ridge', 'hollow', 'cave', 'dam', 'reservoir', 'island', 'spring',
          'springs', 'bend', 'knob', 'valley', 'county', 'road', 'rd')
TOOCOMMON = {'kentucky', 'general', 'national', 'federal', 'county', 'state', 'western', 'eastern', 'northern', 'southern', 'north', 'south'}
KINDW = re.compile(r'\b(state resort park|state historic(al)? (site|park)|state nature preserve|state natural area|state park|state forest|'
                   r'national (historical|historic) (park|site|trail)|national (park|forest|preserve|monument|seashore|lakeshore|recreation area|'
                   r'wildlife refuge|battlefield|military park|river|grassland|recreation trail|scenic trail)|wildlife management area|'
                   r'wildlife area|state game (land|lands|area)|public fishing area|state fishing lake|conservation area|recreation area|'
                   r'natural area|nature preserve|wma|pfa|nwr|lake|park)\b')


def _really_ours(phrase, hay, full):
    for m in re.finditer(r' ' + re.escape(phrase) + r' ([a-z0-9]+)', hay):
        nxt = m.group(1)
        if nxt not in PLACEN or re.search(r'\b' + re.escape(nxt) + r'\b', full): return True
    return bool(re.search(r' ' + re.escape(phrase) + r' *$', hay))


def match_hay(K, text, parks):
    hay = ' ' + lowtext(text) + ' '
    hits = []
    for ref, (pn, typ, la, lo, *_w) in parks.items():
        full = lowtext(pn)
        if len(full) >= 8 and f' {full} ' in hay: hits.append(ref); continue
        sh = ' '.join(KINDW.sub(' ', full).split())
        if not sh or sh in TOOCOMMON or len(sh) < 6 or sh == full and len(full) < 8: continue
        if ' ' in sh:
            if f' {sh} ' in hay and _really_ours(sh, hay, full): hits.append(ref)
        elif re.search(r' ' + re.escape(sh) + r' (?:' + '|'.join(NEXTW) + r') ', hay) and _really_ours(sh, hay, full): hits.append(ref)
    return sorted(set(hits))


# ======================================================================================= reading a sentence (D-R1)
CLOSE_RX = re.compile(r"\b(clos(?:ed|ure|ures|ing|es)|ferm(?:é|ée|és|ées|eture|etures)|no entry|not open to the public|prohibited|interdit[es]?|until further notice|jusqu'à nouvel ordre)\b", re.I)
NEG_RX = re.compile(r"\b(not closed|no closures?|is not|are not|reopen(?:ed|s|ing)?|re-?open(?:ed)?|now open|remains? open|has been lifted|lifted|rescinded|"
                    r"is open|are open|back open|has reopened|have reopened|closed captioning|no longer closed|rouvert|réouvert|réouverture|will close (?:at|on|friday|monday|tuesday|wednesday|thursday|saturday|sunday|daily))\b", re.I)
HOURS_RX = re.compile(r"\b(is|are)\s+open\b[^.]*\b(a\.?m\.?|p\.?m\.?)|\bopen (from|daily|year[- ]round)\b|\bgates? (close|closes|closed) at\b|\bclosed (on )?(mondays?|tuesdays?|wednesdays?|thursdays?|fridays?)\b(?![^.]*\b(for|due|until|through)\b)|\b(daylight|dawn|sunrise) to (dark|dusk|sunset)\b|\bhours\b[^.]*\b\d\s*(a\.?m|p\.?m)", re.I)
HUNT_RX = re.compile(r"quota hunt|drawn (hunters?|permit|applicants?)|managed (deer |elk |turkey )?hunts?|controlled hunt|youth(-only)? hunt|except (drawn|permitted|quota|selected) hunters?|closed to all other (public )?use|closed to (non-hunters|the general public|all users? except)|hunters? (with|holding) [^.]{0,40}permits? only|lottery hunt", re.I)
STANDING_RX = re.compile(r"\b(is|are|shall be|will be)\s+(?:strictly\s+|also\s+)?(prohibited|not (?:allowed|permitted)|unlawful|illegal|forbidden)\b|\bshall not\b|\bmust not\b|\bunlicensed vehicles?\b|\bgroups? (?:of more than|over|larger than) \w+\b|\bdischarg\w* (?:a |of )?firearms?\b|\bsteep banks\b|\bnot permitted\b|\bno (?:camping|fires?|campfires?|alcohol|pets|dogs|swimming|glass)\b(?![^.]*\bclos)", re.I)
SEASON_RULE = re.compile(r"\b(season|seasons)\b[^.]{0,60}\b(open|closed)\b|\bclosed to (?:modern gun |archery |muzzleloader |crossbow |firearms? )?(?:deer |turkey |rabbit |squirrel |quail |dove |waterfowl |small game |elk |bear )?(?:hunting|trapping)\b(?! and)", re.I)
HUNT_WORDS = re.compile(r"\bclos(?:ed|ure|es|ing)\b|no public access|except (?:drawn|quota|permitted|selected) hunters?|quota hunt|permit hunt|drawn hunters?|closed to all other|closed to everyone|closed to the public|closed to (?:non-?hunters|public use|all public)", re.I)
# the hunting season a WMA page talks about: Sep-Aug; 'Nov. 7-8' on a page read in October 2026 = Nov 2026; 'Jan. 15' = Jan 2027
SEASON_YEAR = TODAY.year if TODAY.month >= 7 else TODAY.year - 1
HUNT_SEASON_RX = re.compile(r"\b(deer|turkey|dove|waterfowl|duck|small game|archery|firearms?|muzzleloader|modern gun|elk|bear|squirrel|rabbit|quail)\s+(gun |archery )?season\b", re.I)
SEASONAL_RX = re.compile(r"\b(annually|each year|every year|seasonal(ly)?|nesting|plovers?|eagle|bats?\b|hibernat|winter (gate|closure|season)|for the season|peregrine|falcon|closed (each|every) (winter|spring|summer|fall))\b", re.I)
VEHICLE_RX = re.compile(r"closed to (all )?(motor(ized)? )?vehicles?\b|closed to (all )?motorized|vehicle traffic|vehicular (traffic|access)|closed to (cars|trucks|automobiles)|gate (is |will be )?closed to vehicles", re.I)
VEHICLE_NOT = re.compile(r"all access|all traffic|all use|all users|foot traffic|pedestrians?|hikers|closed to all\b|no entry", re.I)
PERMIT_RX = re.compile(r"(?<!driver's )(?<!drivers )permit (is |are )?(required|needed|necessary)|requires? an? [^.]{0,30}permit|user permit|by permit only|permit holders only|must (have|hold|obtain) an? [^.]{0,30}permit|(?<!driver.s )(?<!drivers )licen[cs]e (is )?required", re.I)
LAND_RX = re.compile(r"lease[^.]{0,60}(not (been )?renewed|has ended|ended|expired|terminated)|no longer (open to the public|public|part of|enrolled|available for public)|removed from the (program|wma|system)|has been sold|is now private|reverted to", re.I)
CAUTION_RX = re.compile(r"\b(caution|advisory|be aware|low water|algae|algal|bloom|expect delays|hazard(ous)?|use care|slippery|limited services|services (are |may be )?(limited|not guaranteed)|lapse in appropriations|shutdown|not guaranteed|high water|boil water|out of service|suspended)\b", re.I)
RULES_RX = re.compile(r"\b(camping|campfires?|fires?|open flames?|charcoal|stoves?)\b[^.]{0,80}\b(prohibited|not (allowed|permitted)|banned|restricted)|\bno (camping|campfires?|fires?)\b|\b(burn|fire) (ban|restriction)s?\b", re.I)
FACILITY_RX = re.compile(r"\b(visitor cent(er|re)s?|welcome cent(er|re)|restrooms?|bathrooms?|toilets?|comfort station|vault toilets?|bath ?house|showers?|offices?|front desk|gift shop|museum|concessions?|snack bar|"
                         r"drinking water|water (system|fountains?|is (off|shut))|nature cent(er|re)|lodge|dining|restaurant|pool|splash pad|playground|dump station|interpretive cent(er|re)|contact station|"
                         r"phone service|wifi|wi-fi|internet|pass sales|fee (booth|station)|entrance station|store|laundry|shooting range|archery range|rifle range|education cent(er|re))\b", re.I)
PART_RX = re.compile(r"\b(roads?|rd\.?|routes?|highway|hwy|gates?|trails?|trailheads?|paths?|boardwalks?|bridges?|footbridge|campgrounds?|camping areas?|campsites?|loops?|day[- ]use|picnic areas?|beach(es)?|boat (ramps?|launch(es)?)|ramps?|launch|docks?|marina|"
                     r"lakes?|ponds?|river access|units?|tracts?|sections?|portions?|parcels?|zones?|cliffs?|caves?|overlooks?|shelters?|parking|lots?|islands?|peninsula|coves?|fields?|spur|segment|stretch|ferry|arches?|rock ?shelters?|"
                     r"compartments?|blocks?|wilderness|north(ern)? (side|half|end)|south(ern)? (side|half|end)|east(ern)? (side|half|end)|west(ern)? (side|half|end)|upper|lower|huntable portion|secteur|sentier|chemin|route|camping|plage|stationnement|pont)\b", re.I)
WHOLE_RX = re.compile(r"\b(park|area|refuge|forest|wma|pfa|property|preserve|site|lands?|grounds|entire|whole|all areas|wildlife management area|state park|national forest|recreation area|the (park|area|refuge|property|site|forest|wma) itself)\b", re.I)
WHOLE_PHRASE = re.compile(r"closed to (all|the) (access|visitors|public|public use|entry|users|traffic)|closed to all\b|closed in its entirety|entire (park|area|property|refuge|forest|wma) is closed|is closed to the public|closed to public (access|use)|closed until further notice", re.I)
EMERGENCY_RX = re.compile(r"\b(wild ?fires?|forest fires?|\bfire\b|floods?|flooding|storms?|tornado|hurricane|evacuat\w*|landslide|rock ?slide|ice|snow|high winds?|damage)\b", re.I)
LONGTERM_RX = re.compile(r"\b(bridge|dam\b|construction|repav\w*|rehabilit\w*|renovat\w*|rebuil\w*|replacement|reconstruct\w*|restoration|project)\b", re.I)
SUBJ_RX = re.compile(r"^(?:the\s+|all\s+)?(.{2,160}?)\s+(?:is|are|will be|will remain|remains?|has been|have been|was|were|est|sont|sera|seront|restera|resteront|demeure(?:nt)?)\s+(?:currently\s+|temporarily\s+|now\s+|still\s+|temporairement\s+)?(?:clos|ferm|prohibited|interdit|not open)", re.I)
SUBJ2_RX = re.compile(r"^(?:the\s+)?(.{2,90}?)\s+(?:has\s+a\s+|have\s+a\s+)?(?:temporary\s+|emergency\s+|seasonal\s+)?(?:closure|fermeture)\b", re.I)
SUBJ3_RX = re.compile(r"\b(?:closure|fermeture) (?:of|du|de la|des|de l')\s+(?:the\s+)?(.{2,90}?)(?:[,;.]|\s+(?:due|for|from|until|through|as|is|has|will|beginning|starting|effective)\b|$)", re.I)
SUBJ4_RX = re.compile(r"^(?:the\s+)?(.{2,110}?)\s+(?:clos(?:ed|es)|ferm(?:é|ée|és|ées))\b(?!\s+(?:captioning|to vehicles))", re.I)
FR_RX = re.compile(r"ferm(é|ée|és|ées|eture)|jusqu'à nouvel ordre|interdit|secteur|sentier", re.I)


def classify(sent, ctx=None):
    """ONE sentence -> None (nothing for us), {'skip': why} (a look-alike, logged as unreadable) or
    {'class': whole|part|hunt|seasonal|note, 'note_kind': ..., 'what': ..., 'from': date, 'to': date, 'flags': {...}, 'lang': en|fr}.
    ctx = {'updated': date, 'year': int, 'names': [heading names], 'park': 'name'}. Rules: Sheet D 1-2, D-R1, CL-2, CL-3, GA2, GA3."""
    ctx = ctx or {}
    s = sent.strip()
    if ';' in s:
        for part in s.split(';'):
            r = classify(part, ctx)
            if r is not None and not r.get('skip'): return r
        return classify(s.replace(';', ','), ctx) if not NEG_RX.search(s) else {'skip': 'negation or reopening word in the sentence (D-R1)'}
    low = s.lower()
    has_close = bool(CLOSE_RX.search(s))
    lang = 'fr' if FR_RX.search(s) and not re.search(r'\bclosed?\b', low) else 'en'
    if re.search(r'[“”"]|\bsigns?\b (define|are erected|mark)|^prohibited activities|regulations (are|is) representative', low) and not re.search(r'\bis closed\b|\bare closed\b', low):
        return {'skip': 'a sentence about signs or rules in general, not a closure'}
    if ' | ' in s or s.count('|') >= 2 or len(s.split()) < 4 and not ctx.get('hunt_page'):
        if not ctx.get('hunt_page'): return {'skip': 'a table fragment or a few words, not a notice (chat 11 regrade)'}
    if re.search(r'closed for (?:the )?protection of|in violation of|posted signs', low) and not (frm_has := (D1.search(s) or DNUM.search(s))):
        return {'skip': 'a standing protection order or posted-signs rule, not a dated closure (chat 11 round 3)'}
    if STANDING_RX.search(s) and not re.search(r'\b(is|are|remains?|will be|has been)\s+(?:temporarily\s+)?clos', low) and not ctx.get('hunt_page') \
            and not re.search(r'\b(entering|entry|enter|occupying|access(?:ing)?|going (?:into|onto)|being (?:in|on|upon)|presence)\b', low) and not RULES_RX.search(s):   # CL-3: camping / fire orders stay a note
        return {'skip': 'a standing rule (prohibited / not permitted / shall not): never a closure or a note (chat 11 regrade)'}
    s = re.sub(r'^(?:currently|at this time|at present|presently|please note|note|effective immediately|until further notice|as of now|today)\s*[,:]?\s+', '', s, flags=re.I)
    low = s.lower()
    if re.match(r'^(?:the|this|that|these|those|said)?\s*(?:trail|road|area|bridge|campground|ramp|gate|lake|loop|section|unit|boardwalk|site|route|path)s?\b', low) and ctx.get('head'):
        h = re.sub(r'\s*[-–:]?\s*(?:temporary\s+)?(?:closures?|closed|update|alert|notice)\b.*$', '', ctx['head'].strip(), flags=re.I).strip(' :-') or ctx['head'].strip()
        s = re.sub(r'^(?:the|this|that|these|those|said)?\s*', h + ': ', s, count=1, flags=re.I)                       # 'the trail is closed…' takes its heading as the subject
        low = s.lower()
    if ctx.get('hunt_page') and SEASON_RULE.search(s) and not re.search(r'\b(all|public|everyone|access|entry|non-?hunters|all other (?:public )?use|all users)\b', low):
        return {'skip': 'a hunting-season rule (a game season closed), not a land closure (HQ Oct 28)'}
    if ctx.get('hunt_page') and HUNT_WORDS.search(s) and not NEG_RX.search(s) and (D1.search(s) or DNUM.search(s) or D1FR.search(s)):
        frm0, to0, clear0 = parse_dates(s, ctx.get('updated'), ctx.get('year') or SEASON_YEAR, season=True)
        if frm0 or to0:                                                                 # CL-2 (HQ Oct 28 fix 1): a dated hunt closure on a WMA page = closed to non-hunters
            what = ''
            mu = re.search(r"\b([A-Z][\w'.-]+(?:\s+[A-Z][\w'.-]+){0,3}\s+(?:Unit|Tract|Area|Section|Portion))\b", s)
            if mu and not re.search(r'wildlife management area', mu.group(1), re.I): what = mu.group(1)
            return {'from': frm0, 'to': to0, 'dates_clear': clear0, 'flags': {'emergency': False, 'longterm': False, 'annually': False}, 'lang': 'en',
                    'class': 'hunt', 'what': what or 'closed to non-hunters', 'hunt_item': True}
    only_prohib = has_close and not re.search(r"\b(clos(?:ed|ure|ures|ing|es)|ferm(?:é|ée|és|ées|eture)|until further notice|jusqu'à nouvel ordre|no entry|not open to the public)\b", low)
    if only_prohib and not re.search(r'\b(entering|entry|enter|occupying|access(?:ing)?|going (?:into|onto)|being (?:in|on|upon)|presence|trespass)\b', low) and not RULES_RX.search(s):
        return {'skip': 'a prohibited ACTIVITY (alcohol, ATVs, collecting, metal detecting…) is a standing rule, not a closure'}
    if re.search(r'\bclosed to (?:all )?(?:fishing|boating|hunting|swimming|camping|trapping|horses?|horseback|bikes?|bicycles?|climbing|rappelling|target shooting|shooting|drones?|dogs?|pets?|atvs?|ohvs?|motor(?:ized)? (?:vehicles?|use))\b', low) \
            and not re.search(r'\b(all access|all use|all users|all other|all public|entry|except)\b', low):
        return {'from': None, 'to': None, 'dates_clear': True, 'flags': {'emergency': False, 'longterm': False, 'annually': False}, 'lang': lang,
                'class': 'note', 'note_kind': 'rules', 'what': 'closed to an activity, land open'}        # 'Energy Lake closed to hunting' = a rule, not a part closure
    if not (has_close or PERMIT_RX.search(s) or LAND_RX.search(s) or CAUTION_RX.search(s) or RULES_RX.search(s) or HUNT_SEASON_RX.search(s) or HUNT_RX.search(s)):
        return None
    if NEG_RX.search(s) and not re.search(r'\bremains? closed\b|\bstill closed\b|\bis not open\b|\bremain closed\b', low):
        return {'skip': 'negation or reopening word in the sentence (D-R1)'}
    if HOURS_RX.search(s) and not re.search(r'\b(for|due to|until|through|because)\b', low):
        return None                                                                        # standing hours = park info
    flags = {'emergency': bool(EMERGENCY_RX.search(s)), 'longterm': bool(LONGTERM_RX.search(s)),
             'annually': bool(re.search(r'\b(annually|each year|every year|chaque année|annuellement)\b', low))}
    frm, to, clear = parse_dates(s, ctx.get('updated'), ctx.get('year'))
    base = {'from': frm, 'to': to, 'dates_clear': clear, 'flags': flags, 'lang': lang, 'what': ''}
    if LAND_RX.search(s):
        return {**base, 'class': 'note', 'note_kind': 'land', 'what': 'may not be public land now'}      # GA3
    if HUNT_RX.search(s) and (has_close or re.search(r'\bexcept\b|\bonly\b', low)):
        if frm or to or re.search(r'\b(saturday|sunday|monday|tuesday|wednesday|thursday|friday|weekend|dates?)\b', low):
            what = _object(s, ctx) if PART_RX.search(s) else ''
            return {**base, 'class': 'hunt', 'what': what or 'closed to non-hunters'}                  # CL-2 dated drawn hunt
        return {**base, 'class': 'note', 'note_kind': 'permit', 'what': 'permit needed (drawn)'}         # CL-2 whole-season permit
    if PERMIT_RX.search(s) and not has_close:
        return {**base, 'class': 'note', 'note_kind': 'permit', 'what': 'permit needed'}
    if RULES_RX.search(s) and not re.search(r'\b(entering|occupying|entry|access)\b', low) and not WHOLE_PHRASE.search(s) \
            and not (has_close and re.search(r'\b(road|trail|campground|area|unit|portion)s?\b[^.]{0,30}\bclos', low)):
        return {**base, 'class': 'note', 'note_kind': 'rules', 'what': 'camping or fire rule'}            # CL-3
    if VEHICLE_RX.search(s) and not VEHICLE_NOT.search(s):
        return {**base, 'class': 'note', 'note_kind': 'vehicles', 'what': _object(s, ctx) or 'road closed to vehicles'}   # GA2 / G4
    if not has_close:
        if CAUTION_RX.search(s) and re.search(r'\b(suspended|out of service|closed|closure|limited|not guaranteed|lapse|shutdown|low water|high water|boil water|algae|algal|bloom)\b', low):
            return {**base, 'class': 'note', 'note_kind': 'caution', 'what': 'caution'}
        if CAUTION_RX.search(s): return {'skip': 'a safety tip with no place or service named (chat 11 regrade)'}
        if HUNT_SEASON_RX.search(s): return {**base, 'class': 'note', 'note_kind': 'season', 'what': 'hunting season'}
        return None
    if re.search(r'lapse in appropriations|shutdown', low) and not WHOLE_PHRASE.search(s) and not re.search(r'park (is )?closed|closed to all', low):
        return {**base, 'class': 'note', 'note_kind': 'caution', 'what': 'services limited'}              # D-R7
    what = _object(s, ctx)
    wl = what.lower()
    if what and (len(what) < 4 or wl in ('the', 'this', 'that', 'it', 'they', 'these', 'all', 'closure', 'the closure')
                 or (not re.search(r'[A-Z][a-z]|\d|[A-Z]{2,}', what) and not PART_RX.search(what))) \
            and not any(lowtext(n) and lowtext(n) in lowtext(s) for n in (ctx.get('names') or []) + ([ctx['park']] if ctx.get('park') else [])) \
            and not WHOLE_PHRASE.search(s) and not ctx.get('hunt_page'):
        return {'skip': f'no named place in the sentence ("{what[:40]}"): dropped (chat 11 regrade)'}
    if what and FACILITY_RX.search(what) and not PART_RX.search(re.sub(r'\b(shooting|archery|rifle) range\b', '', what, flags=re.I)):
        return {**base, 'class': 'note', 'note_kind': 'facility', 'what': what}                            # G5
    if not what and FACILITY_RX.search(s) and not PART_RX.search(s) and not WHOLE_PHRASE.search(s):
        return {**base, 'class': 'note', 'note_kind': 'facility', 'what': clean(FACILITY_RX.search(s).group(0), 60)}
    if re.search(r'\b(shooting|archery|rifle) range\b', wl) and not WHOLE_PHRASE.search(s):
        return {**base, 'class': 'note', 'note_kind': 'facility', 'what': what}
    if SEASONAL_RX.search(s) and (frm or to or flags['annually']):
        return {**base, 'class': 'seasonal', 'what': what or 'seasonal closure'}
    # whole or part
    names = [lowtext(n) for n in (ctx.get('names') or []) if n] + ([lowtext(ctx['park'])] if ctx.get('park') else [])
    names_core = [' '.join(KINDW.sub(' ', n).split()) for n in names]
    subj_is_park = bool(what) and (any(c and c in wl for c in names_core if len(c) >= 4) or any(n in wl for n in names if len(n) >= 6)) \
        and not PART_RX.search(KINDW.sub(' ', what)) and not re.search(r'\b(portion|part|section|side|half) of\b', wl)
    if what and PART_RX.search(what) and not re.search(r'^(the )?(park|area|refuge|forest|property|site|wma|preserve)$', wl):
        if re.search(r'\b(entire|whole|all)\b', wl) and WHOLE_RX.search(wl) and not re.search(r'\b(road|trail|campground|unit|ramp|beach|lake)s?\b', wl):
            return {**base, 'class': 'whole', 'what': what}
        return {**base, 'class': 'part', 'what': what}
    if subj_is_park or (what and re.fullmatch(r'(the )?(park|area|refuge|forest|property|site|wma|preserve|grounds|lands?)', wl)) \
            or (not what and WHOLE_PHRASE.search(s)) or (what and not PART_RX.search(what) and WHOLE_PHRASE.search(s)):
        return {**base, 'class': 'whole', 'what': what or 'the park'}
    if what:
        return {**base, 'class': 'part', 'what': what}
    if WHOLE_PHRASE.search(s): return {**base, 'class': 'whole', 'what': 'the park'}
    return {'skip': 'closing word with no object we can name (D-R1 b)'}


def _object(s, ctx):
    """The thing the sentence closes: 'Roads 995E and 955B', 'the boardwalk', 'Lake Margery at Marben PFA' -> 'Lake Margery'."""
    for rx in (SUBJ_RX, SUBJ2_RX, SUBJ3_RX, SUBJ4_RX):
        m = rx.search(s)
        if m:
            w = m.group(1).strip(' ,;:-')
            w = re.sub(r'^(?:entering(?: or occupying)?|occupying|being (?:in|on|upon)|going (?:into|onto)|access to|entry to|use of)\s+', '', w, flags=re.I)
            w = re.sub(r'^(?:part of|portions? of|a portion of|any portion of|all of|the following|please note that|note that)\s+', '', w, flags=re.I)
            w = re.sub(r'\s+(?:at|in|on|within|near|along)\s+(?:the\s+)?[A-Z][\w\'.]+(?:\s+[A-Z][\w\'.]+){0,4}\s*(?:\([^)]*\))?$', '', w)   # 'Lake Margery at Marben PFA' -> Lake Margery
            w = re.sub(r'^(?:effective|beginning|starting|as of)\s+\w+\s+\d+,?\s*', '', w, flags=re.I)
            if 2 < len(w) <= 120: return w
    m = re.search(r"\(([^)]{2,40})\)", s)
    if m and UNIT_RX.search('(' + m.group(1) + ')'): return unit_split(m.group(1) + ' ')[1] or m.group(1)
    for n in (ctx.get('names') or []):
        core, unit = unit_split(n)
        if unit: return unit
    return ''


# ------------------------------------------------------------------------------------- dates (D-R3, CL-4)
MON = {m: i + 1 for i, m in enumerate(['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december'])}
MON.update({m[:3]: i for m, i in list(MON.items())}); MON['sept'] = 9
MON.update({'janvier': 1, 'février': 2, 'fevrier': 2, 'mars': 3, 'avril': 4, 'mai': 5, 'juin': 6, 'juillet': 7, 'août': 8, 'aout': 8, 'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12, 'decembre': 12})
MONRX = r'(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|june?|july?|aug(?:ust)?|sept?(?:ember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?|janvier|février|fevrier|mars|avril|mai|juin|juillet|août|aout|septembre|octobre|novembre|décembre|decembre)\.?'
D1 = re.compile(r'\b' + MONRX + r'\s+(\d{1,2})(?!\d)(?:st|nd|rd|th)?(?:,?\s+(\d{4}))?', re.I)
D1FR = re.compile(r'\b(\d{1,2})(?:er)?\s+' + MONRX + r'(?:\s+(\d{4}))?', re.I)
DNUM = re.compile(r'\b(\d{1,2})/(\d{1,2})/(\d{2,4})\b')
RANGE_SPLIT = re.compile(r'\s*(?:–|—|-|to|through|thru|until|till|au|jusqu\'au|jusqu\'à)\s*', re.I)


def _mk(y, m, d):
    try: return dt.date(y, m, d)
    except ValueError: return None


def _year_for(m, d, explicit, ref, hint):
    """Which year a 'Nov 14' belongs to. Explicit > the page's year > next occurrence from a fresh page date (D-R3: within 60
    days) > None (unclear)."""
    if explicit: return explicit if explicit > 100 else 2000 + explicit
    if hint: return hint
    if ref and abs((TODAY - ref).days) <= 60:
        y = ref.year
        x = _mk(y, m, d) or _mk(y, m, 28)
        if x and x < ref - dt.timedelta(days=45): y += 1
        return y
    return None


def parse_dates(sent, ref=None, hint=None, season=False):
    """-> (from, to, clear). Reads 'Nov 14-21', 'Feb 15 – Jul 31', 'from April 1 through August 31', 'through Nov 15',
    'until Feb. 2027', 'closed Saturday' (no date), '10/08/26'. clear = False when a date is there but its year cannot be told."""
    s = sent.replace('\u2013', '-').replace('\u2014', '-')
    s = re.sub(r'\b(jan|feb|mar|apr|jun|jul|aug|sept?|oct|nov|dec)\.\s*', lambda m: m.group(1) + ' ', s, flags=re.I)   # 'Nov. 7-8' -> 'Nov 7-8'
    low = s.lower()
    found = []     # (start, end, month, day, explicit_year)
    for m in DNUM.finditer(s):
        a, b, c = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if 1 <= a <= 12 and 1 <= b <= 31: found.append((m.start(), m.end(), a, b, c if c > 100 else 2000 + c))
    for m in D1.finditer(s):
        mo = MON.get(m.group(1).lower().rstrip('.'))
        if mo: found.append((m.start(), m.end(), mo, int(m.group(2)), int(m.group(3)) if m.group(3) else None))
    for m in D1FR.finditer(s):
        mo = MON.get(m.group(2).lower().rstrip('.'))
        if mo: found.append((m.start(), m.end(), mo, int(m.group(1)), int(m.group(3)) if m.group(3) else None))
    m2 = re.search(r'\b' + MONRX + r'\s+(\d{1,2})(?!\d)\s*-\s*(\d{1,2})(?!/|\d)(?:,?\s+(\d{4}))?', s, re.I)   # 'Nov 14-21'
    if m2 and MON.get(m2.group(1).lower().rstrip('.')):
        mo = MON[m2.group(1).lower().rstrip('.')]; y = int(m2.group(4)) if m2.group(4) else None
        found = [f for f in found if not (m2.start() <= f[0] < m2.end())]
        cut = m2.start() + len(m2.group(0).split('-')[0])
        found += [(m2.start(), cut, mo, int(m2.group(2)), y), (m2.end() - len(m2.group(3)) - (len(m2.group(4)) + 2 if m2.group(4) else 0), m2.end(), mo, int(m2.group(3)), y)]
    mo_only = re.search(r'\b(?:until|through|thru|till|to the end of|through the end of|end of|jusqu\'en|jusqu\'à la fin)\s+(?:the\s+end\s+of\s+)?' + MONRX + r'(?:\s+(\d{4}))?(?!\s*\d{1,2}\b)', s, re.I)
    found.sort()
    frm = to = None; clear = True
    if found:
        is_range = len(found) >= 2 and (RANGE_SPLIT.fullmatch(s[found[0][1]:found[1][0]]) is not None
                                        or re.search(r'\b(from|between|du|entre)\b', low[:found[0][0]]) is not None)
        if is_range:
            (_, _, m1, d1, y1), (_, _, mb, db, yb) = found[0], found[1]
            Y1 = _year_for(m1, d1, y1, ref, hint); Yb = yb if yb else Y1
            if season and not y1 and hint: Y1 = hint + (1 if m1 < 7 else 0); Yb = yb if yb else hint + (1 if mb < 7 else 0)
            if Y1 and Yb:
                frm, to = _mk(Y1, m1, d1), _mk(Yb, mb, db)
                if frm and to and to < frm: to = _mk(Yb + 1, mb, db)
            else: clear = False
        else:
            _, _, m1, d1, y1 = found[0]
            Y = _year_for(m1, d1, y1, ref, hint)
            if season and not y1 and hint: Y = hint + (1 if m1 < 7 else 0)
            before = low[max(0, found[0][0] - 24):found[0][0]]
            if not Y: clear = False
            elif re.search(r'\b(until|through|thru|till|to|by|before|ending|ends?|jusqu)\b[^a-z]*$', before): to = _mk(Y, m1, d1)
            else: frm = _mk(Y, m1, d1)
    elif mo_only and MON.get(mo_only.group(1).lower().rstrip('.')):
        mo = MON[mo_only.group(1).lower().rstrip('.')]
        y = int(mo_only.group(2)) if mo_only.group(2) else _year_for(mo, 28, None, ref, hint)
        if y:
            to = dt.date(y + (mo == 12), mo % 12 + 1, 1) - dt.timedelta(days=1)
            if ref and to < ref and not mo_only.group(2): to = dt.date(y + 1 + (mo == 12), mo % 12 + 1, 1) - dt.timedelta(days=1)
        else: clear = False
    return frm, to, clear


# ======================================================================================= page reading
UPD_RX = re.compile(r'^(?:last\s+)?(?:updated|posted|as of|effective|mis(?:e)? à jour)\s*:?\s*(\d{1,2})/(\d{1,2})/(\d{2,4})\s*[,:;-]?\s*(.*)$', re.I)
UPD2_RX = re.compile(r'^(?:last\s+)?(?:updated|posted|as of|effective)\s*:?\s*' + MONRX + r'\s+(\d{1,2}),?\s+(\d{4})\s*[,:;-]?\s*(.*)$', re.I)
AREA_WORD = re.compile(r"\b(WMA|PFA|VPA|NWR|SP|SF|SRA|SNA|Park|Parks|Forest|Area|Lake|Refuge|Trail|Preserve|Site|Reserve|Wilderness|Recreation|Management|Battlefield|Monument|Beach|Campground|Hatchery|Center|Centre|Ramp|Range|Unit|Tract|Island|River|Gorge|Mountain|Hollow|Creek|Falls|Cave|Fort|Lands?|Gameland|Game Land)\b", re.I)
VERB = re.compile(r"\b(is|are|was|were|will|has|have|be|remains?|closed|open|please|due|until)\b", re.I)


def html_lines(html):
    """Visible text as lines; headings keep a '# ' mark so a notice's heading (the park name) can be told from its text."""
    t = re.sub(r'(?is)<(script|style|noscript|svg|nav|header|footer|form)\b.*?</\1>', ' ', html)
    t = re.sub(r'(?is)<(h[1-6])\b[^>]*>(.*?)</\1>', lambda m: '\n# ' + re.sub(r'<[^>]+>', ' ', m.group(2)) + '\n', t)
    t = re.sub(r'(?is)<(?:strong|b)\b[^>]*>(.{3,120}?)</(?:strong|b)>\s*(?:<br\s*/?>|</p>|</div>|:)', lambda m: '\n# ' + m.group(1) + '\n', t)
    t = re.sub(r'(?i)</t[dh]>', ' | ', t)                                               # a table row stays ONE line (quota-hunt tables)
    t = re.sub(r'(?i)<br\s*/?>|</(p|div|li|tr|section|article|dd|dt|summary)>|<(li|p|tr|dt|dd)\b[^>]*>', '\n', t)
    t = re.sub(r'<[^>]+>', ' ', t)
    out = []
    for ln in _html.unescape(t).split('\n'):
        ln = re.sub(r'\s+', ' ', ln).strip()
        if ln: out.append(ln)
    return out


def split_sentences(ln):
    parts = re.split(r'(?<=[.!?;])\s+(?=[A-Z"\'(¿¡À-Ü]|[a-z]{0,2}[A-Z])', ln)
    out = []
    for p in parts:
        for q in re.split(r'\s*;\s+', p):
            q = q.strip()
            if len(q) > 8: out.append(q)
    return out


LEAD_DATE = re.compile(r'^(\d{1,2})/(\d{1,2})/(\d{4})\s*[-–:]\s*(.+)$')
HUNT_ROW = re.compile(r'quota|drawn|managed (deer |elk |turkey )?hunt|controlled hunt|youth(-only)? hunt|closed to', re.I)


def entries_from_lines(lines, park_hint=None, hunt=False):
    """-> [{'head', 'names', 'updated', 'sent', 'year'}]: each sentence that may concern us, with the heading above it (the
    place's name), the agency's 'Updated' date and the year the page itself names (for dates without a year)."""
    out, head, names, upd = [], '', [], None
    year = None
    for ln in lines[:40]:
        m = re.search(r'\b(20[2-3]\d)\b', ln)
        if m and re.search(r'(?i)season|hunts?|closures?|alerts?|notices?|-\s*20', ln): year = int(m.group(1)); break
    for ln in lines:
        is_h = ln.startswith('# ')
        if is_h: ln = ln[2:].strip()
        if not ln: continue
        if re.match(r'(?i)^(last updated|page last|this page)', ln) and not UPD_RX.match(ln): continue
        ml = LEAD_DATE.match(ln)
        if ml:
            try: upd = dt.date(int(ml.group(3)), int(ml.group(1)), int(ml.group(2)))
            except ValueError: upd = None
            ln = ml.group(4).strip()
        mu = UPD_RX.match(ln) or UPD2_RX.match(ln)
        if mu:
            try:
                if mu.re is UPD_RX:
                    y = int(mu.group(3)); y += 2000 if y < 100 else 0
                    upd = dt.date(y, int(mu.group(1)), int(mu.group(2))); ln = mu.group(4).strip()
                else:
                    upd = dt.date(int(mu.group(3)), MON.get(mu.group(1).lower().rstrip('.'), 1), int(mu.group(2))); ln = mu.group(4).strip()
            except ValueError: upd = None
            if not ln: continue
        if hunt and ' | ' in ln and HUNT_ROW.search(ln) and (D1.search(ln) or DNUM.search(ln)):      # a quota-hunt TABLE ROW: WMA | hunt | dates
            cells = [c.strip() for c in ln.split(' | ') if c.strip()]
            first = cells[0] if cells and len(cells[0]) < 70 and not D1.search(cells[0]) and not DNUM.search(cells[0]) else ''
            out.append({'head': first or head, 'names': ([first] if first else names), 'updated': upd, 'sent': ln[:400], 'year': year, 'hunt_page': True}); continue
        if (is_h or (len(ln) < 110 and not re.search(r'[.!?]$', ln) and not VERB.search(ln))) and len(ln) < 110 and (AREA_WORD.search(ln) or is_h) \
                and not re.search(r'(?i)^(closures?|cautions?|alerts?|notices?|region \d+|shooting ranges?|education centers?|boat ramps?|wma, pfa|current closures|news|home|menu|search)\b', ln):
            head = ln
            names = [x.strip() for x in re.split(r'\s*/\s*|\s+and\s+(?=[A-Z])', re.sub(r'\(.*?\)', '', ln)) if x.strip()]
            upd = None
            continue
        for sent in split_sentences(ln):
            if CLOSE_RX.search(sent) or PERMIT_RX.search(sent) or LAND_RX.search(sent) or CAUTION_RX.search(sent) or RULES_RX.search(sent) or HUNT_RX.search(sent) or HUNT_SEASON_RX.search(sent):
                out.append({'head': head, 'names': names, 'updated': upd, 'sent': sent[:600], 'year': year, 'hunt_page': hunt})
            elif hunt and HUNT_ROW.search(sent) and (D1.search(sent) or DNUM.search(sent)):
                out.append({'head': head, 'names': names, 'updated': upd, 'sent': sent[:600], 'year': year, 'hunt_page': True})
    return out


SAMPLE_PAGE = """<h1>Alerts</h1><h3>Ballard WMA</h3><p>Updated 10/20/26 The huntable portion is closed to all access except drawn quota hunters Nov 14-21.</p>
<h3>Peabody WMA</h3><p>Part of Peabody WMA (Unit 2) is closed Saturday for a hunt. A Peabody WMA User Permit is required to hunt, fish or trap on the area.</p>
<h3>Buckhorn Lake</h3><p>Buckhorn Lake Dam Ramp Access closed until Feb. 2027</p><h3>Hickory Run</h3><p>The trail is closed.</p>
<table><tr><th>WMA</th><th>Hunt</th><th>Dates</th></tr><tr><td>Clay WMA</td><td>Deer quota hunt</td><td>Nov 7-8, 2026</td></tr><tr><td>Beaver Creek WMA</td><td>Deer quota hunt</td><td>Nov 7-8, 2026</td></tr></table>
<p>Metal detecting is prohibited on all WMAs.</p>"""
SAMPLE_WMA = """<h1>Clay WMA</h1><p>The area is closed to all other hunting Nov. 7-8 for the quota deer hunt. Sauerheber Unit closed to all public access Nov. 1 - Mar. 15 except for quota hunters. ATVs are prohibited.</p>"""


LAST_HTML = {}
BROWSER_LOG = []


def safe_url(u):
    """A path with spaces or control characters is quoted before the fetch (copied from the truth checker's fix 6)."""
    try:
        u = re.sub(r'[\x00-\x1f\x7f]', '', str(u)).strip()
        p = urllib.parse.urlsplit(u)
        return urllib.parse.urlunsplit((p.scheme, p.netloc, urllib.parse.quote(p.path, safe=':/?&=%+@,;!$*()~'), urllib.parse.quote(p.query, safe=':/?&=%+@,;!$*()~'), ''))
    except Exception: return u  # noqa: BLE001


def read(url, pdf=False):
    """-> (ok, kind, body_text_or_html, status). Through Manners: robots obeyed, 1 request / 2 s per host."""
    url = safe_url(url)
    if OFFLINE:
        if 'fw.ky.gov/Hunt' in url: return True, 'html', SAMPLE_PAGE, 'ok'      # plumbing test only: a built-in sample page
        if 'Kdfwr_id=155' in url: LAST_HTML[url] = SAMPLE_WMA; return True, 'html', SAMPLE_WMA, 'ok'
        return False, '', '', 'offline'
    st, hd, body, final = M.get(url, rng=(0, PDF_FIRST - 1) if pdf else None)
    STAT['requests'] += 1
    if st not in (200, 206): return False, '', '', (str(st) if not isinstance(st, int) else f'HTTP {st}')
    ct = (hd.get('content-type') or '').lower()
    if body[:5] == b'%PDF-' or 'application/pdf' in ct:
        STAT['pdfs'] += 1
        txt = pdf_text(body, 6)
        if len(txt.strip()) < 60: return False, 'pdf', '', 'not readable (scanned image PDF?): check the agency'   # CL-7
        return True, 'pdf', txt, 'ok'
    STAT['pages'] += 1
    html = body.decode('utf-8', 'replace')
    if len(LAST_HTML) > 8: LAST_HTML.clear()
    LAST_HTML[url] = html
    return True, 'html', html, 'ok'


def read_json(url):
    ok, kind, body, st = read(url)
    if not ok: return None, st
    try: return json.loads(body), 'ok'
    except Exception as e: return None, f'not JSON ({str(e)[:40]})'  # noqa: BLE001


# ======================================================================================= the sources
# Rows: {'name': park name the agency wrote (or None), 'hay': free text to find the park in, 'title', 'text', 'end': date,
#        'start': date, 'at': (lat, lon), 'link', 'date': the agency's date, 'refs': pinned refs, 'names': heading names}
def F(a, *names):
    low = {k.lower(): v for k, v in a.items()}
    for n in names:
        v = low.get(n.lower())
        if v not in (None, '', ' '): return v
    return None


def day(v):
    if v in (None, ''): return None
    try:
        if isinstance(v, (int, float)) and v > 1e10: return dt.datetime.fromtimestamp(v / 1000, dt.timezone.utc).date()
        s = str(v).strip()
        for f in ('%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y', '%B %d, %Y', '%b %d, %Y'):
            try: return dt.datetime.strptime(s[:len(TODAY.strftime(f)) + 4].strip(), f).date()
            except ValueError: pass
        m = re.match(r'(\d{4})-(\d\d)-(\d\d)', s)
        if m: return dt.date(*map(int, m.groups()))
        m = re.match(r'(\d{1,2})/(\d{1,2})/(\d{2,4})', s)
        if m:
            y = int(m.group(3)); y += 2000 if y < 100 else 0
            return dt.date(y, int(m.group(1)), int(m.group(2)))
    except Exception: return None  # noqa: BLE001
    return None


def xy(g):
    if not g: return None
    if 'x' in g and 'y' in g: return g['y'], g['x']
    pts = [p for r in (g.get('rings') or g.get('paths') or []) for p in r]
    if not pts: return None
    return sum(p[1] for p in pts) / len(pts), sum(p[0] for p in pts) / len(pts)


def arcgis(url, where='1=1'):
    out, off = [], 0
    while True:
        q = urllib.parse.urlencode({'where': where, 'outFields': '*', 'returnGeometry': 'true', 'outSR': 4326, 'f': 'json',
                                    'resultOffset': off, 'resultRecordCount': 1000})
        j, st = read_json(url.rstrip('/') + '/query?' + q)
        if j is None: raise RuntimeError(st)
        if isinstance(j, dict) and j.get('error'): raise RuntimeError(str(j['error'])[:120])
        fs = j.get('features') or []
        out += fs
        if not fs or not j.get('exceededTransferLimit') or off > 20000: return out
        off += len(fs)


def rss(url):
    ok, kind, body, st = read(url)
    if not ok: raise RuntimeError(st)
    root = ET.fromstring(body.encode('utf-8', 'replace') if isinstance(body, str) else body)
    out = []
    for it in root.iter('item'):
        t = lambda k: (it.findtext(k) or '').strip()  # noqa: E731
        try: d = email.utils.parsedate_to_datetime(t('pubDate')).date()
        except Exception: d = None  # noqa: E722
        out.append({'title': clean(t('title'), 200), 'text': clean(t('description'), 600), 'link': t('link'), 'date': d})
    return out


# ---- the 10 state feeds: copied from KPC-Links .github/scripts/kpc_us_closures.py (chat 2, Oct 25-28 2026), credit there.
def src_ca():
    rows = []
    for f in arcgis('https://services2.arcgis.com/AhxrK3F6WM8ECvDi/arcgis/rest/services/CSPParkUnit_CurrentStatus/FeatureServer/0'):
        a = f.get('attributes') or {}
        st = str(F(a, 'Status', 'STATUS', 'CurrentStatus', 'Unit_Status', 'ParkStatus') or '')
        if not st or st.strip().upper() == 'OPEN': continue
        rows.append({'name': F(a, 'UNITNAME', 'UnitName'), 'title': st.title(),
                     'text': ' · '.join(x for x in (clean(F(a, 'closure_reason')), clean(F(a, 'status_notes_pub'))) if x),
                     'end': day(F(a, 'StatusReopenDate')), 'at': xy(f.get('geometry')), 'link': ''})
    return rows


def src_wi():
    rows = []
    for f in arcgis('https://services5.arcgis.com/Ul9AyFFeFTjf08DW/arcgis/rest/services/WI_Park_Closures_PUBLIC_VIEW/FeatureServer/0'):
        a = f.get('attributes') or {}
        if str(F(a, 'Active_Flag') or 'Y').strip().upper() in ('N', 'NO', '0', 'FALSE', 'INACTIVE'): continue
        end = day(F(a, 'Exp_End_Date'))
        if end and end < TODAY: continue
        rows.append({'name': F(a, 'Full_Prop_Name', 'Actual_Prop_Name', 'Property'), 'title': clean(F(a, 'Closure_Name'), 160) or 'Notice',
                     'text': clean(F(a, 'Reason', 'Description', 'Details')), 'end': end, 'at': xy(f.get('geometry')), 'link': ''})
    return rows


def src_fl():
    rows = []
    for lid, what in ((6, ''), (5, 'Campground: ')):
        for f in arcgis(f'https://services1.arcgis.com/nRHtyn3uE1kyzoYc/arcgis/rest/services/Florida_State_Parks_Operational_Status/FeatureServer/{lid}'):
            a = f.get('attributes') or {}
            st = str(F(a, 'PARK_STATUS', 'STATUS', 'CAMP_STATUS') or '')
            if not st or st.strip().lower().startswith('open'): continue
            nm = str(F(a, 'SITE_NAME', 'PARK_NAME') or '')
            rows.append({'name': re.sub(r'\s*[-–:]?\s*(full[- ]facility |primitive |group )?camp(ground|ing|site)s?\b.*$', '', nm, flags=re.I) or nm,
                         'title': what + st, 'text': clean(F(a, 'COMMENTS', 'Comments')), 'end': None, 'at': xy(f.get('geometry')), 'link': ''})
    return rows


def src_mt():
    rows = []
    for f in arcgis('https://services3.arcgis.com/Cdxz8r11hT0MGzg1/arcgis/rest/services/FWPLND_LANDS_CLOSURES_RESTRICTIONS/FeatureServer/0'):
        a = f.get('attributes') or {}
        end = day(F(a, 'DATE_END'))
        if end and end < TODAY: continue
        beg = day(F(a, 'DATE_BEGIN'))
        if beg and beg > TODAY + dt.timedelta(days=UPCOMING_DAYS): continue
        rows.append({'name': F(a, 'SITE_NAME'), 'title': clean(F(a, 'RESTRICTION'), 120) or 'Restriction', 'start': beg,
                     'text': clean(F(a, 'DESCRIPTION')), 'end': end, 'at': xy(f.get('geometry')), 'link': F(a, 'WEBLINK') or ''})
    return rows


def src_mo():
    rows = []
    for f in arcgis('https://gis.dnr.mo.gov/server/rest/services/parks/State_Parks_Status_Viewer/MapServer/0'):
        a = f.get('attributes') or {}
        st = str(F(a, 'STATUS') or '').strip()
        adv = []
        for n in range(1, 11):
            if str(F(a, f'ADVISORY_{n}_SHOW') or '').strip().upper() == 'Y':
                t = clean(F(a, f'ADVISORY_{n}'), 300)
                if t: adv.append(t)
        if (not st or st.lower() == 'open') and not adv: continue
        rows.append({'name': F(a, 'LOC_NAME'), 'title': st if st and st.lower() != 'open' else 'Advisory',
                     'text': ' · '.join(adv), 'end': None, 'at': xy(f.get('geometry')), 'link': F(a, 'URL') or ''})
    return rows


def src_nj():
    rows = []
    for f in arcgis('https://services1.arcgis.com/QWdNfRs7lkPq4g4Q/arcgis/rest/services/New_Jersey_State_Park_Service_Live_Status_Updates_(Public_View)/FeatureServer/0'):
        a = f.get('attributes') or {}
        st = str(F(a, 'Status') or '').strip()
        if not st or st.lower().startswith('open'): continue
        rows.append({'name': F(a, 'ParkName'), 'title': st, 'text': clean(F(a, 'Park_Hours', 'Notes', 'Comments')),
                     'end': None, 'at': xy(f.get('geometry')), 'link': F(a, 'Facility_URL') or ''})
    return rows


def src_or():
    rows = []
    for f in arcgis('https://nrimp.dfw.state.or.us/arcgis/rest/services/ORHAM/ORHAM/MapServer/6', 'alert_enabled=1'):
        a = f.get('attributes') or {}
        end = day(F(a, 'alert_end'))
        if end and end < TODAY: continue
        rows.append({'name': F(a, 'subdivision'), 'title': clean(F(a, 'alert_title'), 160) or 'Alert',
                     'text': clean(F(a, 'alert_text')), 'end': end, 'at': xy(f.get('geometry')), 'link': ''})
    return rows


def src_co():
    ok, kind, body, st = read('https://docs.google.com/spreadsheets/d/e/2PACX-1vQv8-zuZoYsA6jhM2l76icNnlVKK6NR36qeamBg_6s2f0POK6-nA0s66Nt_TcanQeClTXBvBvZGJls9/pub?gid=0&single=true&output=csv')
    if not ok: raise RuntimeError(st)
    rows = []
    for r in csv.DictReader(io.StringIO(body)):
        nm = F(r, 'Name of Location', 'Location')
        if not nm: continue
        end = day(F(r, 'End Date'))
        if end and end < TODAY: continue
        rows.append({'name': nm, 'title': clean(F(r, 'Type of Closure'), 120) or 'Closure',
                     'text': clean(' · '.join(str(v) for k, v in r.items() if k and v and re.search(r'detail|descr|note|reason', k, re.I))),
                     'end': end, 'at': None, 'link': 'https://cpw.state.co.us/'})
    return rows


def _rss_rows(url, keep=r'.'):
    rows = []
    for it in rss(url):
        if it['date'] and (TODAY - it['date']).days > RSS_DAYS: continue
        if not re.search(keep, it['title'] + ' ' + it['text'], re.I): continue
        rows.append({'name': None, 'hay': it['title'] + ' ' + it['text'], 'title': it['title'], 'text': it['text'],
                     'end': None, 'at': None, 'link': it['link'], 'date': it['date']})
    return rows


def src_ar(): return _rss_rows('https://www.agfc.com/category/wma-closure/feed/')
def src_nc(): return _rss_rows('https://www.ncparks.gov/blog-category/alerts/feed', r'clos|status|open|restrict|alert')


FEEDS = {  # area: (id, agency, page for people, reader)   (the 10 feed states of kpc_us_closures.py)
    'US-CA': ('ca-parks', 'California State Parks', 'https://www.parks.ca.gov/?page_id=30009', src_ca),
    'US-WI': ('wi-dnr', 'Wisconsin DNR', 'https://dnr.wisconsin.gov/topic/parks/propertynotices', src_wi),
    'US-FL': ('fl-parks', 'Florida State Parks', 'https://www.floridastateparks.org/', src_fl),
    'US-MT': ('mt-fwp', 'Montana FWP', 'https://fwp.mt.gov/news/current-closures-restrictions', src_mt),
    'US-MO': ('mo-parks', 'Missouri State Parks', 'https://mostateparks.com/basic-page/active-advisories', src_mo),
    'US-NJ': ('nj-parks', 'NJ State Park Service', 'https://dep.nj.gov/parksandforests/', src_nj),
    'US-OR': ('or-odfw', 'Oregon Dept. of Fish & Wildlife', 'https://myodfw.com/', src_or),
    'US-CO': ('co-cpw', 'Colorado Parks & Wildlife', 'https://cpw.state.co.us/', src_co),
    'US-AR': ('ar-agfc', 'Arkansas Game & Fish', 'https://www.agfc.com/category/wma-closure/', src_ar),
    'US-NC': ('nc-parks', 'NC State Parks', 'https://www.ncparks.gov/', src_nc),
}


# ---- Kentucky State Parks' own alert list (the same list kpc_park_alerts.ky_state_parks reads)
def src_ky_parks(url):
    j, st = read_json(url)
    if j is None: raise RuntimeError(st)
    rows = []
    for a in j.get('value') or []:
        title, text = clean(a.get('Title'), 160), clean(a.get('Text'))
        if not title and not text: continue
        rows.append({'name': None, 'hay': title + ' ' + text, 'title': title, 'text': text, 'end': None, 'at': None,
                     'link': clean(a.get('CtaLink'), 300) or 'https://parks.ky.gov/', 'date': day(str(a.get('PublicationDate') or '')[:10])})
    return rows


# ---- the National Park Service alerts API (one call per state; the park code is the agency's own tie)
def src_nps(area, parks):
    st = area[3:]
    j, why = read_json(f'https://developer.nps.gov/api/v1/alerts?stateCode={st}&limit=500&api_key={urllib.parse.quote(NPS_KEY)}')
    if j is None: raise RuntimeError(why)
    codes = {}
    for ref, (pn, typ, la, lo, web) in parks.items():
        m = re.search(r'nps\.gov/([a-z]{4})\b', str(web or '').lower())
        if m: codes.setdefault(m.group(1), []).append(ref)
    rows = []
    for a in j.get('data') or []:
        code = clean(a.get('parkCode'), 10).lower()
        rows.append({'name': None, 'refs': codes.get(code, []), 'title': clean(a.get('title'), 200), 'text': clean(a.get('description')),
                     'end': None, 'at': None, 'link': clean(a.get('url'), 300) or f'https://www.nps.gov/{code}/planyourvisit/conditions.htm',
                     'date': day(str(a.get('lastIndexedDate') or '')[:10]), 'cat': clean(a.get('category'), 40)})
    return rows


# ---- Forest Service 'alerts-notices' pages (the usa-card blocks kpc_park_alerts.forest_alerts reads; else the generic reader)
def src_fs_alerts(url, refs, home=None):
    ok, kind, body, st = read(url)
    if not ok: raise RuntimeError(st)
    rows = []
    for m in re.finditer(r'<li class="usa-card[^"]*wfs-alert-flag ([a-z\-]+)">(.*?)</li>', body, re.S):
        level, block = m.group(1), m.group(2)
        head = re.search(r'<h3[^>]*>\s*<a href="([^"]+)"[^>]*>\s*<span>(.*?)</span>', block, re.S)
        bodym = re.search(r'<div class="usa-card__body">(.*?)</div>', block, re.S)
        if not head: continue
        path = head.group(1)
        rows.append({'name': None, 'refs': list(refs or []), 'home': list(home or []), 'head': clean(head.group(2), 160), 'title': clean(head.group(2), 160), 'text': clean(bodym.group(1) if bodym else ''),
                     'end': None, 'at': None, 'link': ('https://www.fs.usda.gov' + path) if path.startswith('/') else path, 'date': None, 'level': level})
    if rows: return rows
    return page_rows(body, url, refs, home)


def page_rows(body, url, refs=None, home=None, hunt=False):
    """The GENERIC PAGE READER: one row per sentence that may concern us, with its heading and 'Updated' date. refs = pinned
    (the agency's own tie); home = the unit's own park (a forest, a refuge) for notices that name no other POTA park."""
    lines = html_lines(body) if '<' in body[:2000] else [l for l in body.split('\n') if l.strip()]
    rows = []
    for e in entries_from_lines(lines, hunt=hunt):
        rows.append({'name': None, 'names': e['names'], 'head': e['head'], 'refs': list(refs or []), 'home': list(home or []), 'title': e['head'][:160], 'text': e['sent'],
                     'sent': e['sent'], 'end': None, 'at': None, 'link': url, 'date': e['updated'], 'year': e['year'], 'hunt_page': e.get('hunt_page', False)})
    return rows


def src_page(url, refs=None, pdfs=True, home=None, hunt=False):
    ok, kind, body, st = read(url, pdf=url.lower().split('?')[0].endswith('.pdf'))
    if not ok: raise RuntimeError(st)
    if kind == 'html' and not OFFLINE and len(page_text(body)) < 400:                     # a script-built page (fw.ky.gov quota hunts)
        bt, err = '', ''
        try: bt = browser_text(url, M) or ''
        except Exception as e: err = str(e)[:160]  # noqa: BLE001
        try:
            import kpc_manners as _KM
            started = 'pw' in (getattr(_KM, '_BROWSER', {}) or {})
        except Exception: started = False  # noqa: BLE001
        if not err and not bt:
            err = 'browser returned nothing' + ('' if started else (' (BROWSER env is not 1)' if os.environ.get('BROWSER') != '1' else ' (Chromium did not start)'))
        BROWSER_LOG.append({'url': url, 'plain_len': len(page_text(body)), 'browser_len': len(bt), 'started': started, 'error': err})
        STAT['browser'] = STAT.get('browser', 0) + (1 if bt else 0)
        if len(bt) > len(page_text(body)):
            bt = '\n'.join(' | '.join(c.strip() for c in ln.split('\t') if c.strip()) + (' |' if '\t' in ln else '') for ln in bt.split('\n'))
            LAST_HTML[url] = bt
            body = bt
    rows = page_rows(body, url, refs, home, hunt)
    if kind == 'html' and pdfs and not late():                        # CL-7: a PDF closure list linked from the page, by range
        n = 0
        for u, txt in links_in(body, url):
            if n >= 3: break
            if u.lower().split('?')[0].endswith('.pdf') and re.search(r'clos|alert|notice|hunt|order', (txt + ' ' + u).lower()):
                n += 1
                ok2, k2, t2, st2 = read(u, pdf=True)
                if ok2: rows += page_rows(t2, u, refs, home, hunt)
                else: rows.append({'name': None, 'title': 'PDF ' + txt[:60], 'text': '', 'status_only': st2, 'link': u})
    return rows


def src_links(url, refs=None):
    """A list page whose alerts are links (fw.ky.gov/Alerts: a SharePoint list; kpc_park_alerts.kdfwr_alerts reads it the same way)."""
    ok, kind, body, st = read(url)
    if not ok: raise RuntimeError(st)
    rows = []
    for u, label in links_in(body, url):
        if len(label) < 18 or not re.search(r'/Alerts?/|/Pages/', u, re.I): continue
        if re.search(r'(?i)^(home|contact|search|sign in|skip to|stay connected|default)', label): continue
        rows.append({'name': None, 'hay': label, 'title': label, 'text': label, 'sent': label, 'end': None, 'at': None, 'link': u, 'date': None, 'refs': list(refs or [])})
    return rows


# ======================================================================================= one area
STATE_PAGES = None


def closure_pages():
    global STATE_PAGES
    if STATE_PAGES is None:
        d = load(LINKS / 'data' / 'closure-pages.json', {}) or load('data/closure-pages.json', {})
        STATE_PAGES = d.get('pages') or []
    return STATE_PAGES


def park_list(area, scope='all'):
    """{ref: (name, type, lat, lon, web)} for the area. 'state' = no National units (they have their own feeds); 'federal' = only those."""
    st = area[3:]
    P = {}
    if area.startswith('US-'):
        d = load(f'data/parkinfo/US-{st}.json', {}) or load(LINKS / f'data/parkinfo/US-{st}.json', {})
        for r, v in (d.get('parks') or {}).items():
            if len(v) > 6 and v[5] is not None: P[r] = (v[0], v[2] or '', v[5], v[6], v[1] if len(v) > 1 else '')
        if st == 'KY':
            for x in load(LINKS / 'kpc-ky-data.json', {}).get('parks', []):
                if x.get('c'): P[x['c']] = (x.get('n', ''), x.get('t', ''), x.get('la'), x.get('lo'), x.get('web') or '')
    else:
        d = load('data/parkinfo/CA.json', {}) or load(LINKS / 'data/parkinfo/CA.json', {})
        for r, v in (d.get('parks') or {}).items():
            if len(v) > 10 and v[10] == st: P[r] = (v[0], v[2] or '', v[5], v[6], v[1] if len(v) > 1 else '')
    if scope == 'state': P = {r: v for r, v in P.items() if 'National' not in (v[1] or '') and '/ NPS' not in (v[1] or '') and 'Federal' not in (v[1] or '')}
    if scope == 'federal': P = {r: v for r, v in P.items() if 'National' in (v[1] or '') or 'NPS' in (v[1] or '') or 'Federal' in (v[1] or '')}
    return P


_FS_STATES = None


def fs_states():
    """{forest slug: set of states whose park lists give that forest's fs.usda.gov page}: a slug in two states = a multi-state forest."""
    global _FS_STATES
    if _FS_STATES is None:
        _FS_STATES = {}
        import glob
        for f in glob.glob('data/parkinfo/US-*.json') + glob.glob(str(LINKS / 'data/parkinfo/US-*.json')):
            stx = f[-7:-5]
            for r, v in (load(f, {}).get('parks') or {}).items():
                m = re.search(r'fs\.usda\.gov/(?:r\d+/)?([a-z0-9-]+)/?(?:$|\?|#)', str(v[1] if len(v) > 1 else '').lower())
                if m: _FS_STATES.setdefault(m.group(1), set()).add(stx)
        for x in load(LINKS / 'kpc-ky-data.json', {}).get('parks', []):
            m = re.search(r'fs\.usda\.gov/(?:r\d+/)?([a-z0-9-]+)/?(?:$|\?|#)', str(x.get('web') or '').lower())
            if m: _FS_STATES.setdefault(m.group(1), set()).add('KY')
    return _FS_STATES


def sources_for(area):
    """[(id, agency, url, kind, how, scope, refs, home)] in Sheet D's order: feeds, then pages, then federal by pattern, then Canada.
    refs = pinned to those parks (the agency's own tie); home = the unit's own park for notices that name no other POTA park."""
    st = area[3:]
    S = []
    if area in FEEDS:
        sid, agency, page, fn = FEEDS[area]
        S.append((sid, agency, page, 'feed', fn, 'state', [], []))
    extra = (load(OUT / 'sources.json', {}) or load('data/closures/sources.json', {})).get('sources') or []
    for r in extra:
        if r.get('area') in (area, 'ALL') or (r.get('area') == 'US' and area.startswith('US-')):
            if r.get('how') == 'ky-parks': S.append((r['id'], r['agency'], r['url'], 'feed', 'ky-parks', r.get('scope', 'state'), r.get('refs') or [], r.get('home') or []))
            else: S.append((r['id'], r['agency'], r['url'], r.get('kind', 'page'), r.get('how', 'generic'), r.get('scope', 'state'), r.get('refs') or [], r.get('home') or []))
    if NPS_KEY and area.startswith('US-'): S.append((f'nps-{st.lower()}', 'National Park Service', f'https://www.nps.gov/state/{st.lower()}/index.htm', 'feed', 'nps', 'federal', [], []))
    else: S.append((f'nps-{st.lower()}', 'National Park Service', '', 'feed', 'nps-nokey', 'federal', [], []))
    if RIDB_KEY: S.append(('ridb', 'Recreation.gov (RIDB)', 'https://ridb.recreation.gov/', 'feed', 'ridb', 'federal', [], []))
    seen_urls = {s[2] for s in S}
    if area == 'US-KY':                                                              # KDFWR's own WMA pages (Public_Lands_Search), pinned per park
        for ref, v in ((load(LINKS / 'data' / 'ky-hunting.json', {}) or {}).get('wma') or {}).items():
            u = v.get('link') or ''
            if 'fw.ky.gov' in u and u not in seen_urls:
                seen_urls.add(u); S.append((f'ky-wma-{slug(ref, 10)}', 'Kentucky Fish and Wildlife', u, 'page', 'hunt-page', 'state', [ref], []))
    for p in closure_pages():
        if p.get('st') == st and p.get('page') and p['page'] not in seen_urls:
            seen_urls.add(p['page']); S.append((f'{st.lower()}-' + slug(p['agency'], 24), p['agency'], p['page'], 'page', 'generic', 'state', [], []))
    # federal by pattern, from the parks' own pages
    for ref, (pn, typ, la, lo, web) in sorted(park_list(area).items()):
        w = str(web or '')
        m = re.search(r'fs\.usda\.gov/(?:r\d+/)?([a-z0-9-]+)/?(?:$|\?|#)', w.lower())
        if m and m.group(1) not in ('alerts', 'recarea', 'wildflowers', 'main', 'detail', 'visit'):
            u = f'https://www.fs.usda.gov/alerts/{m.group(1)}/alerts-notices'
            if u not in seen_urls: seen_urls.add(u); S.append((f'fs-{m.group(1)}', 'US Forest Service', u, 'page', 'fs-alerts', 'federal', [], [ref]))
        m = re.search(r'fws\.gov/refuge/([a-z0-9-]+)', w.lower())
        if m:
            u = f'https://www.fws.gov/refuge/{m.group(1)}/visit-us'
            if u not in seen_urls: seen_urls.add(u); S.append((f'fws-{m.group(1)}', 'US Fish and Wildlife Service', u, 'page', 'fws', 'federal', [], [ref]))
        m = re.search(r'parks\.canada\.ca/pn-np/([a-z]{2})/([a-z0-9-]+)', w.lower())
        if m and area.startswith('CA-'):
            u = f'https://parks.canada.ca/pn-np/{m.group(1)}/{m.group(2)}/visit/bulletins'
            if u not in seen_urls: seen_urls.add(u); S.append((f'pc-{m.group(2)}', 'Parks Canada', u, 'page', 'parks-canada', 'federal', [], [ref]))
    # a hand row in sources.json with the same url as a pattern source (e.g. ky-fs-dbnf) keeps the hand row: drop the pattern twin
    firsts = {}
    for x in S:
        if x[2] and x[2] in firsts: continue
        firsts[x[2] or x[0]] = x
    return list(firsts.values())


def rows_of(sid, agency, url, kind, how, refs, area, parks, home=None):
    if kind == 'feed' and callable(how): return how()
    if how == 'ky-parks': return src_ky_parks(url)
    if how == 'nps': return src_nps(area, parks)
    if how == 'nps-nokey': raise RuntimeError('needs NPS_API_KEY secret')
    if how == 'ridb': raise RuntimeError('D-R8: RIDB carries no closure text (names and points only); not read')
    if how == 'fs-alerts': return src_fs_alerts(url, refs, home)
    if how == 'links': return src_links(url, refs)
    if how == 'hunt-page': return src_page(url, refs, home=home, hunt=True)
    if how == 'parks-canada':
        rows = src_page(url, refs, pdfs=False, home=home)
        if area in FRENCH_AREAS and not late():                                  # G9 / CL-6: French kept beside the English
            fr = url.replace('parks.canada.ca', 'parcs.canada.ca').replace('/visit/bulletins', '/visite/bulletins')
            try: frows = [r for r in src_page(fr, refs, pdfs=False, home=home) if CLOSE_RX.search(r['sent'])]
            except Exception: frows = []  # noqa: BLE001
            en = [r for r in rows if CLOSE_RX.search(r['sent'])]
            if frows and len(frows) == len(en):
                for r, f in zip(en, frows): r['details_fr'] = f['sent']
            elif frows and not en: rows += frows                                  # a French-only page: shown in French (CL-6)
        return rows
    return src_page(url, refs, home=home)


STATE_RX = re.compile(r'\b(alabama|alaska|arizona|arkansas|california|colorado|connecticut|delaware|florida|georgia|hawaii|idaho|illinois|indiana|iowa|kansas|kentucky|louisiana|maine|maryland|massachusetts|michigan|minnesota|mississippi|missouri|montana|nebraska|nevada|new hampshire|new jersey|new mexico|new york|north carolina|north dakota|ohio|oklahoma|oregon|pennsylvania|rhode island|south carolina|south dakota|tennessee|texas|utah|vermont|virginia|washington|west virginia|wisconsin|wyoming)\b', re.I)
STATE_NAMES = {'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland', 'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina', 'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming', 'DC': 'District of Columbia'}
AREA_CTX = {}


def area_ctx(area):
    """What 'in this state' means for a multi-state unit's notices: the state's name, its counties (Kentucky: from kpc-ky-data),
    and the hand list of ranger districts in sources.json ('districts': {'US-KY': {'gwj': ['Clinch']}})."""
    if area in AREA_CTX: return AREA_CTX[area]
    st = area[3:]
    counties = set()
    if area == 'US-KY':
        for x in load(LINKS / 'kpc-ky-data.json', {}).get('parks', []):
            for c in re.split(r'\s*/\s*', x.get('co') or ''):
                if c and c != 'Multiple': counties.add(c.lower())
    dist = ((load(OUT / 'sources.json', {}) or load('data/closures/sources.json', {})).get('districts') or {}).get(area) or {}
    AREA_CTX[area] = {'state': STATE_NAMES.get(st, st).lower(), 'counties': counties, 'districts': {k: [d.lower() for d in v] for k, v in dist.items()}}
    return AREA_CTX[area]


def in_state(row, area, sid):
    """Rule (HQ Oct 28): a multi-state forest's notice counts for this area only when it names this state, one of its counties,
    one of the unit's ranger districts here, or ties to a park here; a notice naming another state is dropped. Single-state units
    keep every notice (a forest-wide alert belongs to the forest's own park)."""
    text = lowtext((row.get('head') or '') + ' ' + (row.get('title') or '') + ' ' + (row.get('sent') or row.get('text') or ''))
    cx = area_ctx(area)
    slug_ = sid.split('-', 1)[1] if sid.startswith('fs-') else (sid.split('-fs-', 1)[1] if '-fs-' in sid else '')
    multi = slug_ and len(fs_states().get(slug_, set())) > 1
    others = {m.group(1).lower() for m in STATE_RX.finditer(text)} - {cx['state']}
    if 'west virginia' in others and 'virginia' in others and cx['state'] != 'west virginia': pass
    if 'virginia' in others and 'west virginia' in text and cx['state'] == 'west virginia': others.discard('virginia')
    if multi:
        if others and cx['state'] not in text: return False                     # names another state's place (Bath County, Virginia)
        for a2, dd in (((load(OUT / 'sources.json', {}) or load('data/closures/sources.json', {})).get('districts') or {}).items()):
            if a2 != area and isinstance(dd, dict) and any(d.lower() in text for d in dd.get(slug_, []) if d.lower() not in cx['districts'].get(slug_, [])): return False
        if cx['state'] in text: return True
        if any(f' {c} county' in f' {text} ' or f' {c} co ' in f' {text} ' for c in cx['counties']): return True
        if any(d in text for d in cx['districts'].get(slug_, [])): return True
        return None                                    # the caller may still keep it when the text ties to a park HERE
    return not others or cx['state'] in text


def tie(K, row, parks, area, sid=''):
    """-> (refs, part_from_name). Pinned refs win (the agency's own tie); else the name / heading; else the text; two parks or
    none = unmatched (Sheet A rule 4; Sheet A ex. 8 'Hickory Run')."""
    if row.get('refs'): return list(row['refs']), ''
    st = area[3:]
    part = ''
    if row.get('home'):                                                         # a forest / refuge / Parks Canada unit page
        ok = in_state(row, area, sid)
        hits = match_hay(K, (row.get('head') or '') + ' ' + (row.get('sent') or row.get('text') or ''), {r: v for r, v in parks.items() if r not in row['home']})
        if ok is None: ok = len(hits) == 1
        if not ok: return ['OUT-OF-STATE'], ''
        return list(row['home']) + (hits if len(hits) == 1 else []), ''        # Sheet D ex. 5: the WMA on forest land gets it too
    if row.get('name'):
        _, part = unit_split(str(row['name']))
        hits = match(K, row, parks, st)
        return (hits if len(hits) == 1 else ([] if len(hits) > 1 else hits)), part
    names = row.get('names') or []
    sent = row.get('sent') or row.get('text') or ''
    if names:
        cand = {}
        for n in names:
            core, unit = unit_split(n)
            h = match(K, {'name': core}, parks, st)
            if len(h) == 1: cand[n] = (h[0], unit)
        if len(cand) == 1:
            n, (ref, unit) = next(iter(cand.items())); return [ref], unit
        if len(cand) > 1:                                                        # GA rule 4: the sentence decides ('Lake Margery at Marben PFA')
            low = lowtext(sent)
            named = [v for n, v in cand.items() if ' '.join(KINDW.sub(' ', lowtext(n)).split()) and ' '.join(KINDW.sub(' ', lowtext(n)).split()) in low]
            if len(named) == 1: return [named[0][0]], named[0][1]
            return [], ''
    hits = match_hay(K, (row.get('head') or '') + ' ' + sent, parks)
    return (hits if len(hits) == 1 else []), part


KIND_LABEL = {'whole': 'Closure', 'part': 'Closure', 'hunt': 'Hunt closure', 'seasonal': 'Seasonal closure', 'note': 'Park notice'}


def card_line(it):
    """Rule 5 wording, one line (the cards may build their own from the fields)."""
    q = it['details']
    ag = it.get('agency', '')
    when = ''
    if it.get('from') or it.get('to'):
        when = f" {it.get('from') or '…'} – {it.get('to') or 'until further notice'}"
    elif it.get('updated'): when = f" updated {it['updated']}"
    c = it['class']
    if c == 'whole': return f'⚠ CLOSED: {q} ({ag},{when or " dates not given: check the agency page"})'
    if c == 'part': return f'⚠ PART CLOSED ({it.get("what") or "part"}): {q} ({ag},{when or " dates not given: check the agency page"})'
    if c == 'hunt': return f'🦌 HUNT: closed to non-hunters{when}: {q} ({ag})'
    if c == 'seasonal': return f'📅 SEASONAL: {it.get("what") or ""}{when}: {q} ({ag})'
    k = it.get('note_kind')
    return {'permit': f'🎫 Permit needed: {q} ({ag})', 'vehicles': f'🚗 Closed to vehicles, open on foot: {q} ({ag})',
            'land': f'ℹ️ May not be public land now: {q} ({ag})', 'season': f'🦌 Hunting season: {q} ({ag})'}.get(k, f'ℹ️ Note: {q} ({ag})')


def build_item(sid, agency, ref, cl, sent, row, area, first_seen):
    frm, to = cl.get('from'), cl.get('to')
    upd = row.get('date')
    ann = cl['flags'].get('annually')
    stale = None
    if cl['class'] == 'seasonal':                                                   # CL-4
        fresh = upd and (TODAY - upd).days < 395
        if ann or fresh:
            if frm and to and to < TODAY and ann: frm, to = _mk(frm.year + 1, frm.month, frm.day), _mk(to.year + 1, to.month, to.day)
        else: frm = to = None; stale = 'may be out of date: check the agency page'
    if not cl.get('dates_clear', True) and not (frm or to):
        stale = 'dates unclear: check the agency page'                              # D-R3
        if cl['class'] in ('whole', 'part', 'hunt', 'seasonal'): cl = {**cl, 'class': 'note', 'note_kind': 'caution', 'what': cl.get('what') or ''}
    if upd and (TODAY - upd).days >= 365 and not to: stale = stale or 'may be out of date: check the agency page'     # GA1
    base = upd or first_seen or TODAY
    if not to and not stale and cl['class'] != 'note':
        clock = 30 if cl['flags'].get('emergency') else (365 if cl['flags'].get('longterm') else 90)                      # G3
        if (TODAY - base).days > clock: stale = ('may be over: check the agency page' if clock == 30 else 'may be out of date: check the agency page')
    what = cl.get('what') or ''
    key = slug((what + ' ' + sent)[:70], 48)
    iid = f'sc-{sid}-{key}-{ref}'
    if cl.get('hunt_item') and frm: iid = f'sc-ky-fw-wma-{ref}-{frm.isoformat()}' if sid.startswith('ky-') else f'sc-{sid}-hunt-{ref}-{frm.isoformat()}'
    it = {'id': iid, 'ref': ref, 'area': area, 'src': sid, 'agency': agency, 'class': cl['class'],
          'what': what[:90], 'details': f'"{sent.strip()}"', 'from': frm.isoformat() if frm else None, 'to': to.isoformat() if to else None,
          'updated': upd.isoformat() if upd else None, 'stale': stale, 'link': row.get('link') or '', 'link2': '',
          'seen': (first_seen or TODAY).isoformat(), 'confirmed': 1, 'lang': cl.get('lang', 'en'),
          'kind': KIND_LABEL[cl['class']], 'call': 'KPC BOT',
          'expires': (to + dt.timedelta(days=1)).isoformat() if to else (TODAY + dt.timedelta(days=7)).isoformat()}
    if cl['class'] == 'note': it['note_kind'] = cl.get('note_kind', 'caution')
    if row.get('details_fr'): it['details_fr'] = f'"{row["details_fr"]}"'
    if cl['flags'].get('emergency') and cl['class'] in ('whole', 'part'): it['as_of'] = NOW                               # G10
    if frm and frm > TODAY: it['upcoming'] = True; it['show_from'] = (frm - dt.timedelta(days=UPCOMING_DAYS)).isoformat()   # D9
    if row.get('title') and row.get('title') != sent[:160]: it['title'] = row['title'][:160]
    it['label'] = card_line(it)
    return it


def process_area(K, area, state, review):
    out_f = OUT / f'{area}.json'
    prev = load(out_f, {}) or {}
    prev_items = {it['id']: it for it in prev.get('items', []) if (prev.get('ver') or 0) >= VER}   # items made under older rules are not kept alive (A5 applies within one rule version)
    prev_src = prev.get('sources') or {}
    srcs, items, banners, unreadable = {}, [], [], []
    S = sources_for(area)
    stopped = False
    for sid, agency, url, kind, how, scope, refs, home in S:
        if late(): stopped = True; break
        parks = park_list(area, scope if not home else 'all')
        ps = prev_src.get(sid) or {}
        old = [it for it in prev_items.values() if it['src'] == sid]
        try:
            rows = rows_of(sid, agency, url, kind, how, refs, area, parks, home)
            ok = True; why = ''
        except Exception as e:  # noqa: BLE001
            rows, ok, why = [], False, str(e)[:160]
        if not ok:                                                                   # keep the last items: a failed read never reopens a park
            skipped = why.startswith('needs ') or why.startswith('D-R8')
            if not skipped: STAT['sources_failed'] += 1
            items += old
            srcs[sid] = {'agency': agency, 'url': url, 'kind': kind, 'ok': False, 'skipped': skipped, 'why': why, 'n': len(old), 'n_prev': ps.get('n', 0),
                         'unmatched': ps.get('unmatched', []), 'last_ok': ps.get('last_ok'), 'fails': 0 if skipped else (ps.get('fails') or 0) + 1}
            continue
        n, unmatched, now_ids, out_state = 0, [], set(), 0
        page_txt = ''
        if TEST and how == 'hunt-page':
            try: page_txt = page_text(LAST_HTML.get(url, '')) if LAST_HTML.get(url) else ''
            except Exception: page_txt = ''  # noqa: BLE001
        for r in rows:
            if r.get('status_only'):
                unreadable.append({'src': sid, 'why': r['status_only'], 'link': r.get('link')}); continue
            sents = [r['sent']] if r.get('sent') else split_sentences(((r.get('title') or '') + '. ' + (r.get('text') or '')).strip('. '))
            refs_, part = tie(K, r, parks, area, sid)
            if refs_ == ['OUT-OF-STATE']: out_state += 1; continue                 # a multi-state unit's notice about another state
            if not refs_:
                if any(CLOSE_RX.search(x) for x in sents):
                    unmatched.append(clean((r.get('head') or r.get('name') or r.get('title') or sents[0]), 80)); STAT['unmatched'] += 1
                continue
            ctx = {'updated': r.get('date'), 'year': r.get('year'), 'names': r.get('names') or ([r['name']] if r.get('name') else []),
                   'park': parks.get(refs_[0], ('',))[0] if len(refs_) == 1 else '', 'hunt_page': r.get('hunt_page', False),
                   'head': (r.get('head') or r.get('title') or '')[:120] if (r.get('head') or r.get('title') or '').lower() != (r.get('sent') or '').lower()[:120] else ''}
            got = 0
            for sent in sents:
                STAT['sentences'] += 1
                cl = classify(sent, ctx)
                if cl is None: continue
                if cl.get('skip'): unreadable.append({'src': sid, 'why': cl['skip'], 'sent': sent[:160]}); STAT['unreadable'] += 1; continue
                if part and cl['class'] in ('whole', 'hunt') and not cl.get('hunt_item') and not cl.get('what', '').lower().startswith(part.lower()[:4]): cl = {**cl, 'class': 'part', 'what': part}
                if r.get('end') and not cl.get('to'): cl['to'] = r['end']
                if r.get('start') and not cl.get('from'): cl['from'] = r['start']
                if cl.get('to') and cl['to'] < TODAY:
                    unreadable.append({'src': sid, 'why': f"ended {cl['to'].isoformat()}: not shown", 'sent': sent[:160]}); continue      # never re-dated
                for ref in refs_:
                    it = build_item(sid, agency, ref, cl, sent, r, area, None)
                    pit = prev_items.get(it['id'])
                    if pit: it['seen'] = pit.get('seen') or it['seen']; it['confirmed'] = (pit.get('confirmed') or 1) + 1
                    if it['class'] == 'whole' and kind != 'feed' and not (it['from'] or it['to'] or it['updated']) and it['confirmed'] >= 2 and not it.get('as_of'):
                        it['kind'] = 'Park notice'; it['stale'] = 'unverified notice: the agency page says closed, no date. Check the agency page.'   # D-R4
                    now_ids.add(it['id']); items.append(it); got += 1
            if not got and kind == 'feed' and not r.get('sent'):
                # a feed row with a status word only ('Full Closure', 'Partially open'): the status is the agency's sentence
                title = (r.get('title') or '').strip()
                if title and re.search(r'clos|partial|restrict', title, re.I):
                    cl = {'class': 'part' if re.search(r'partial|campground', title, re.I) else 'whole', 'what': ('Campground' if re.search(r'campground', title, re.I) else ('partially open' if re.search(r'partial', title, re.I) else '')),
                          'from': r.get('start'), 'to': r.get('end'), 'dates_clear': True, 'flags': {'emergency': False, 'longterm': False, 'annually': False}, 'lang': 'en'}
                    sent = title + (f' — {r["text"]}' if r.get('text') else '')
                    for ref in refs_:
                        it = build_item(sid, agency, ref, cl, sent[:400], r, area, None)
                        pit = prev_items.get(it['id'])
                        if pit: it['seen'] = pit.get('seen') or it['seen']; it['confirmed'] = (pit.get('confirmed') or 1) + 1
                        now_ids.add(it['id']); items.append(it)
            n += got
        # A5 / D-R5: an old item not in this good read stays until GONE_READS good reads miss it (dated ones until their end)
        for oit in old:
            if oit['id'] in now_ids: continue
            if oit.get('taken_down'):
                if (TODAY - dt.date.fromisoformat(oit['taken_down'])).days <= TAKEN_DOWN_DAYS: items.append(oit)
                continue
            if oit.get('to') and oit['to'] >= TODAY.isoformat(): items.append(oit); continue   # D-R5: dated items keep to their end date
            g = (oit.get('gone') or 0) + 1
            oit = {**oit, 'gone': g}
            if g >= GONE_READS:
                oit.update({'taken_down': TODAY.isoformat(), 'kind': 'Park notice', 'stale': 'notice taken down: check the agency page',
                            'expires': (TODAY + dt.timedelta(days=TAKEN_DOWN_DAYS)).isoformat(), 'label': f'ℹ️ Notice taken down: check the agency page ({oit.get("agency", "")}; was: {oit.get("details", "")[:160]})'})
            items.append(oit)
        srcs[sid] = {'agency': agency, 'url': url, 'kind': kind, 'ok': True, 'rows': len(rows), 'n': n, 'n_prev': ps.get('n', 0), 'out_of_state': out_state,
                     'unmatched': sorted(set(unmatched))[:25], 'last_ok': TODAY.isoformat(), 'fails': 0}
        if how == 'hunt-page' and TEST and not any(it.get('class') == 'hunt' and it['id'] in now_ids for it in items):
            m = re.search(r'closed|quota|drawn', page_txt, re.I)
            srcs[sid]['debug'] = ('…' + page_txt[max(0, m.start() - 200):m.start() + 200].replace('\n', ' ') + '…') if m else ('page text %d chars, no closed / quota word' % len(page_txt))
            if sid in ('ky-fw-quota', 'ky-fw-public-land'): srcs[sid]['debug_full'] = page_txt[:9000]   # Oct 28 night: the whole quota page as the reader saw it (HQ: 'get the real table')
    if stopped:                                                                      # out of time: sources not reached keep their old items
        for sid in {it['src'] for it in prev_items.values()} - set(srcs):
            items += [it for it in prev_items.values() if it['src'] == sid]
            srcs[sid] = {**(prev_src.get(sid) or {}), 'ok': (prev_src.get(sid) or {}).get('ok', False), 'why': 'not reached this run (out of time)'}
    items = drop_title_twins(merge_items(items))
    banners = mass_banners(items, area)
    D = {'area': area, 'read': NOW, 'ver': VER, 'about': 'Closures super-bot (RULE SHEET D). details = the agency\'s own sentence. Nothing here is on a card until Brandon\'s GO (CL-5).',
         'sources': srcs, 'items': sorted(items, key=lambda x: (x['ref'], x['id'])), 'banners': banners,
         'unreadable': unreadable[:80], 'counts': counts(items)}
    save(out_f, D)
    state['areas'][area] = {'status': 'partial' if stopped else 'done', 'read': NOW, 'items': len(items), 'sources': len(srcs),
                            'failed': sum(1 for s in srcs.values() if not s.get('ok')), 'counts': D['counts']}
    review[area] = D
    notice(f"{area}: {len(items)} items from {sum(1 for s in srcs.values() if s.get('ok'))}/{len(srcs)} sources ({sum(1 for s in srcs.values() if s.get('skipped'))} skipped: no secret)" + (' (out of time)' if stopped else '')
           + f"; unmatched {sum(len(s.get('unmatched') or []) for s in srcs.values())}; " + ', '.join(f'{k} {v}' for k, v in D['counts'].items() if v))
    return not stopped


def counts(items):
    c = {'whole': 0, 'part': 0, 'hunt': 0, 'seasonal': 0, 'note': 0, 'taken_down': 0}
    for it in items:
        if it.get('taken_down'): c['taken_down'] += 1
        else: c[it['class']] = c.get(it['class'], 0) + 1
    return c


def drop_title_twins(items):
    """chat 11 round 3: an item whose sentence is only the heading of another item on the same park (or inside its sentence) goes."""
    def t(x): return lowtext(str(x or '').strip('"'))
    out = []
    for it in items:
        d = t(it['details'])
        twin = any(o is not it and o['ref'] == it['ref'] and not o.get('taken_down') and len(t(o['details'])) > len(d)
                   and (d == t(o.get('title')) or d in t(o['details']) or d in t(o.get('title')) + ' ' + t(o['details'])) for o in items)
        if not twin: out.append(it)
    return out


def merge_items(items):
    """A6: the same closure from two sources (same park, same class, same thing, overlapping dates) = one item, both links."""
    out = {}
    for it in sorted(items, key=lambda x: (x['src'], x['id'])):
        k = (it['ref'], it['class'], slug(it.get('what') or it['details'][:40], 24))
        o = out.get(k)
        if o and o['src'] != it['src'] and _overlap(o, it):
            if it.get('link') and it['link'] not in (o.get('link'), o.get('link2')): o['link2'] = o.get('link2') or it['link']
            o['src2'] = it['src']; o['confirmed'] = max(o.get('confirmed', 1), it.get('confirmed', 1)); o['seen'] = min(o['seen'], it['seen'])
            if it.get('to') and (not o.get('to') or it['to'] > o['to']): o['to_alt'] = it['to']
            continue
        if o:
            k = k + (it['src'],)
        out[k] = it
    return list(out.values())


def _overlap(a, b):
    fa, ta, fb, tb = a.get('from') or '0000', a.get('to') or '9999', b.get('from') or '0000', b.get('to') or '9999'
    return fa <= tb and fb <= ta


def mass_banners(items, area):
    """G7: one notice closing MASS or more parks = a state banner too (the park items stay)."""
    by = {}
    for it in items:
        if it['class'] == 'whole' and not it.get('taken_down'): by.setdefault((it['src'], it['details'][:120]), set()).add(it['ref'])
    out = []
    for (src, det), refs in by.items():
        if len(refs) >= MASS:
            ex = next(it for it in items if it['src'] == src and it['details'][:120] == det)
            out.append({'id': f'sc-{src}-banner-{slug(det, 30)}', 'area': area, 'src': src, 'agency': ex.get('agency'), 'kind': 'Closure', 'call': 'KPC BOT',
                        'details': ex['details'], 'parks': sorted(refs), 'link': ex.get('link'), 'seen': ex['seen'], 'expires': ex['expires'],
                        'label': f"⚠ MANY PARKS CLOSED ({len(refs)}): {ex['details']} ({ex.get('agency')})"})
    return out


# ======================================================================================= Kentucky side-by-side + gate (CL-5)
def ky_own_items():
    """Kentucky's own readers' CURRENT closure items: 'pa-' / 'wma-' / 'hc-' entries in KPC-Links kpc-conditions.json, plus the
    announced entries with refs in data/park-alerts-state.json. Only the closure kinds (not 'Burn or forest work')."""
    out = {}
    for c in (load(LINKS / 'kpc-conditions.json', {}) or {}).get('items', []):
        iid = str(c.get('id', ''))
        if iid.startswith(('pa-', 'wma-', 'hc-')) and c.get('ref') and c.get('kind') in ('Park alert', 'Hunt closure', 'Closure', 'WMA closure'):
            out[iid] = {'ref': c['ref'], 'text': c.get('details', ''), 'kind': c.get('kind')}
    st = load(LINKS / 'data' / 'park-alerts-state.json', {}) or {}
    for k, v in (st.get('seen') or {}).items():
        if v.get('announced') and v.get('refs') and not v.get('routine'):
            for ref in v['refs']:
                iid = f'pa-{k}-{ref}'
                if not any(o['ref'] == ref and (v.get('title') or '')[:30].lower() in o['text'].lower() for o in out.values()):
                    out[iid] = {'ref': ref, 'text': f"{v.get('title', '')} — {v.get('text', '')}", 'kind': 'Park alert'}
    return out


def _words(s): return {w for w in lowtext(s).split() if len(w) > 3 and w not in TOOCOMMON}


def side_by_side(area, D, own, label):
    """-> (matched, only_here, only_there) lists for review.md. Matched = same park + the two texts share 2 significant words."""
    mine = [it for it in D.get('items', []) if not it.get('taken_down')]
    matched, only_there = [], []
    used = set()
    for oid, o in own.items():
        hit = None
        ow = _words(o['text'])
        for it in mine:
            if it['ref'] != o['ref']: continue
            if len(ow & _words(it['details'] + ' ' + (it.get('title') or ''))) >= 2: hit = it; break
            if o.get('kind') == 'Hunt closure' and it['class'] == 'hunt':
                m = re.search(r'(\d{4}-\d\d-\d\d)$', oid)
                if not m or not it.get('from') or abs((dt.date.fromisoformat(it['from']) - dt.date.fromisoformat(m.group(1))).days) <= 3: hit = it; break
        if hit: matched.append((oid, hit['id'])); used.add(hit['id'])
        else: only_there.append((oid, o['ref'], o['text'][:100]))
    only_here = [(it['id'], it['ref'], it['class'], it['details'][:100]) for it in mine if it['id'] not in used]
    return matched, only_here, only_there


def ky_test(state, review):
    D = review.get('US-KY') or load(OUT / 'US-KY.json', {})
    own = ky_own_items()
    matched, only_here, only_there = side_by_side('US-KY', D, own, 'Kentucky')
    n = len(own)
    pct = (100 * len(matched) // n) if n else 0
    res = 'PASS' if n and pct >= 80 else 'FAIL'
    why = f"{len(matched)} of {n} of Kentucky's own reader's items found here on the same park ({pct}%); {len(only_here)} only here"
    if not n: why = "Kentucky's own reader has no current closure items to compare (needs KPC-Links kpc-conditions.json)"
    state['test'] = {'when': TODAY.isoformat(), 'result': res, 'why': why, 'matched': len(matched), 'own': n, 'only_here': len(only_here),
                     'only_there': [t[0] for t in only_there][:20]}
    notice(f'KENTUCKY TEST {res}: {why}')
    print('TEST=' + res)
    try:
        import kpc_status
        if res == 'PASS': kpc_status.grade_me(BOT, 'US-KY', str(OUT / 'US-KY.json'), why)
        else: kpc_status.gate(BOT, 'US-KY', 'FAIL', why)
    except Exception as e: print('status helper: ' + str(e)[:120])  # noqa: BLE001
    return res


def write_review(state, review):
    L = [f'# Closures super-bot: review ({TODAY}; RULE SHEET D; compared quietly, nothing on cards until GO)', '',
         f"Run: {NOW} · requests {STAT['requests']} · pages {STAT['pages']} · PDFs {STAT['pdfs']} · sentences read {STAT['sentences']} · unmatched {STAT['unmatched']} · look-alikes skipped {STAT['unreadable']} · sources failed {STAT['sources_failed']}", '']
    t = state.get('test')
    if t: L += [f"## Kentucky gate: **{t['result']}** — {t['why']}", '']
    bl = (state.get('last') or {}).get('browser') or []
    if bl: L += ['## Browser path (pages with under 400 characters of plain text)', ''] + [f"- {b['url']}: plain {b['plain_len']} chars, browser {b['browser_len']} chars, started {b['started']}" + (f", error: {b['error']}" if b.get('error') else '') for b in bl] + ['']
    fl = (state.get('last') or {}).get('failed') or []
    if fl: L += ['## Sources that failed this run', ''] + [f"- {f['area']} {f['src']}: {f['why']} ({f['url']})" for f in fl] + ['']
    us = load('data/alerts/us-parks.json', {}) or load(LINKS / 'data' / 'alerts' / 'us-parks.json', {})
    uc_by_area = {}
    for it in us.get('items', []):
        st = (us.get('sources') or {}).get(it.get('src'), {}).get('st')
        if st: uc_by_area.setdefault(f'US-{st}', {})[it['id']] = {'ref': it['ref'], 'text': it.get('details', ''), 'kind': it.get('kind')}
    for area in sorted(state.get('areas') or {}):
        D = review.get(area) or load(OUT / f'{area}.json', {})
        if not D: continue
        a = state['areas'][area]
        L += [f"## {area} ({a.get('status')}, read {a.get('read', '')[:16]})",
              ' · '.join(f'{k} {v}' for k, v in (D.get('counts') or {}).items()) + f" · {len(D.get('banners') or [])} banners", '']
        bad = [(s, v) for s, v in (D.get('sources') or {}).items() if not v.get('ok') and not v.get('skipped')]
        if bad: L += ['Sources that failed (last items kept): ' + '; '.join(f"{s} ({v.get('why', '')[:60]})" for s, v in bad), '']
        sk = [(s, v) for s, v in (D.get('sources') or {}).items() if v.get('skipped')]
        if sk: L += ['Skipped quietly (a secret is missing): ' + '; '.join(f"{s} ({v.get('why', '')[:50]})" for s, v in sk), '']
        dbg = [(k, v['debug']) for k, v in (D.get('sources') or {}).items() if v.get('debug')]
        if dbg: L += ['KDFWR pages with no hunt item (the real wording, TEST=1): ' + ' ‖ '.join(f'{k}: {d[:300]}' for k, d in dbg[:12]), '']
        oos = sum(v.get('out_of_state') or 0 for v in (D.get('sources') or {}).values())
        if oos: L += [f'Dropped as another state\'s place (multi-state forest): {oos} notices', '']
        um = [(s, u) for s, v in (D.get('sources') or {}).items() for u in (v.get('unmatched') or [])]
        if um: L += ['Unmatched (two parks or none; for chat 8): ' + '; '.join(f'{u} [{s}]' for s, u in um[:30]), '']
        own = ky_own_items() if area == 'US-KY' else uc_by_area.get(area)
        if own is not None:
            who = "Kentucky's own reader (kpc_park_alerts.py + hc-)" if area == 'US-KY' else 'data/alerts/us-parks.json (uc- items)'
            m, h, th = side_by_side(area, D, own, who)
            L += [f'### Side-by-side vs {who}: matched {len(m)} · only here {len(h)} · only there {len(th)}', '']
            for oid, ref, txt in th[:25]: L.append(f'- ONLY THERE: {ref} {oid}: {txt}')
            for iid, ref, cl, txt in h[:25]: L.append(f'- ONLY HERE: {ref} [{cl}] {txt}')
            L.append('')
        for it in [x for x in D.get('items', []) if not x.get('taken_down')][:12]:
            L.append(f"- {it['ref']} · {it['label'][:200]}" + (f" · stale: {it['stale']}" if it.get('stale') else ''))
        L.append('')
    (OUT / 'review.md').write_text('\n'.join(L) + '\n', encoding='utf-8')


# ======================================================================================= self test (no web)
SELFTEST = [  # (sentence, context, expected class, expected note_kind or what-contains, expected dates)
    ("Big Basin Redwoods State Park is closed to all access until further notice.", {'park': 'Big Basin Redwoods State Park'}, 'whole', None, (None, None)),
    ("Roads 995E and 955B are temporarily closed.", {'names': ["John's Mountain WMA"]}, 'part', 'roads 995e', (None, None)),
    ("The campground is closed for the season, Nov 1 - Mar 31.", {'updated': dt.date(2026, 10, 20)}, 'seasonal', 'campground', (dt.date(2026, 11, 1), dt.date(2027, 3, 31))),
    ("The huntable portion is closed to all access except drawn quota hunters Nov 14-21.", {'updated': dt.date(2026, 10, 20)}, 'hunt', None, (dt.date(2026, 11, 14), dt.date(2026, 11, 21))),
    ("The north beach is closed annually from April 1 through August 31 for nesting piping plovers.", {'updated': dt.date(2019, 3, 1)}, 'seasonal', 'north beach', (None, None)),
    ("Hickory Mountain Rd. and Thompson South Rd. are currently closed to vehicle traffic for ongoing roadwork.", {}, 'note', 'vehicles', (None, None)),
    ("Visitor center and restrooms closed; park grounds remain open.", {}, 'note', 'facility', (None, None)),
    ("A Peabody WMA User Permit is required to hunt, fish or trap on the area.", {}, 'note', 'permit', (None, None)),
    ("Use caution: low water at the boat ramp may make launching difficult.", {}, 'note', 'caution', (None, None)),
    ("The lease for Sparks Cut Off VPA has not been renewed for 2026.", {}, 'note', 'land', (None, None)),
    ("The boardwalk is closed until further notice.", {'updated': dt.date(2021, 7, 9), 'names': ['Grand Bay WMA']}, 'part', 'boardwalk', (None, None)),
    ("Le secteur Nord est fermé jusqu'à nouvel ordre.", {}, 'part', 'secteur nord', (None, None)),
    ("Flint Ridge Road is closed for repaving through Nov 15.", {'updated': dt.date(2026, 10, 10)}, 'part', 'flint ridge road', (None, dt.date(2026, 11, 15))),
    ("Entering or occupying any portion of the tornado-damaged National Forest System lands in Pulaski and Laurel Counties is prohibited.", {}, 'part', 'tornado', (None, None)),
    ("Park closed to all visitors.", {}, 'whole', None, (None, None)),
    ("Camping within 300 feet of National Forest System Road 918 is prohibited.", {}, 'note', 'rules', (None, None)),
    # look-alikes: none of these may become a closure (D-R1)
    ("The trail is not closed.", {}, None, None, None),
    ("The Fort Henry Trail has reopened after storm damage.", {}, None, None, None),
    ("No closures are expected this weekend.", {}, None, None, None),
    ("Closed captioning is available on the park film.", {}, None, None, None),
    ("The park is open daily from 8 a.m. to 5 p.m.", {}, None, None, None),
    ("The gift shop will close at 4 p.m. on Fridays.", {}, None, None, None),
    ("Open Wednesday through Sunday, daylight to dark.", {}, None, None, None),
    ("The road was closed last year but is open again.", {}, None, None, None),
    # standing rules (HQ Oct 28): a prohibited ACTIVITY is never a closure
    ("Alcohol is prohibited anywhere in the recreation area.", {}, None, None, None),
    ("ATV's are prohibited.", {}, None, None, None),
    ("Metal detecting and the collection of objects of antiquity are prohibited.", {}, None, None, None),
    # real closures about a PLACE stay
    ("Due to safety concerns the bridge on FS Road 126, Davenport Bay, is temporarily closed.", {}, 'part', 'bridge on fs road 126', (None, None)),
    ("Bolar Mountain Recreation Area - Twin Ridge Road Closure.", {}, 'part', 'twin ridge road', (None, None)),
    ("Grindstone Campground and its parking area will be closed for the remainder of the 2026 season.", {}, 'part', 'grindstone campground', (None, None)),
    ("Hematite Lake and Honker Lake closed to fishing and boating", {}, 'note', 'rules', (None, None)),
    ("Ballard WMA | Deer quota hunt | Nov 7-8", {'updated': dt.date(2026, 10, 20), 'hunt_page': True}, 'hunt', None, (dt.date(2026, 11, 7), dt.date(2026, 11, 8))),
    # KDFWR property-page wording (HQ Oct 28; season year assumed, 'Nov. 15-Jan. 15' spans the year)
    ("The area is closed to all other hunting Nov. 7-8 for the quota deer hunt.", {'hunt_page': True}, 'hunt', None, (dt.date(SEASON_YEAR, 11, 7), dt.date(SEASON_YEAR, 11, 8))),
    ("Sauerheber Unit closed to all public access Nov. 1 - Mar. 15 except for quota hunters.", {'hunt_page': True}, 'hunt', 'sauerheber unit', (dt.date(SEASON_YEAR, 11, 1), dt.date(SEASON_YEAR + 1, 3, 15))),
    ("The WMA is closed to everyone except drawn hunters November 21-24.", {'hunt_page': True}, 'hunt', None, (dt.date(SEASON_YEAR, 11, 21), dt.date(SEASON_YEAR, 11, 24))),
    ("Closed to all public access Nov. 15-Jan. 15 except waterfowl hunters with a drawn permit.", {'hunt_page': True}, 'hunt', None, (dt.date(SEASON_YEAR, 11, 15), dt.date(SEASON_YEAR + 1, 1, 15))),
    # chat 11's regrade: standing rules never notes; subjectless sentence takes the heading; fragments dropped; safety tip dropped
    ("Any unlicensed vehicle is prohibited on all refuge property.", {}, None, None, None),
    ("Groups of more than ten people are prohibited without a permit.", {}, None, None, None),
    ("It is prohibited to discharge a firearm within the forest unless hunting.", {}, None, None, None),
    ("The trail is closed between the two trailheads.", {'head': 'Dog Slaughter Falls Trail Closure'}, 'part', 'dog slaughter falls trail', (None, None)),
    ("Camping | Not permitted. |", {}, None, None, None),
    ("When landing on an island be aware of steep banks and rock dikes.", {}, None, None, None),
    ("The closure will likely last until the end of December 2026", {}, None, None, None),
    # HQ Oct 28 round 4
    ("All other areas of the WMA remain closed due to extensive storm damage; the only areas open to the public are those adjacent to Highway 192.", {'names': ['Cane Creek WMA'], 'hunt_page': True}, 'part', 'areas', (None, None)),
    ("Rabbit season is open Nov. 1-Dec. 31, except closed Nov. 7-8.", {'hunt_page': True}, None, None, None),
    ("Closed to modern gun deer hunting except for the quota hunt.", {'hunt_page': True}, None, None, None),
    ("Camping in violation of posted signs is prohibited.", {}, None, None, None),
    ("Entry into areas closed for protection of threatened and endangered species at Cave Run Lake and Laurel River Lake is prohibited.", {}, None, None, None),
    ("Currently, the trail is closed between the two trailheads.", {'head': 'Cliffside Trail #519 Closure'}, 'part', 'cliffside trail #519', (None, None)),
    ("This road is closed for culvert repair.", {'head': 'Road 214 Temporary Closure'}, 'part', 'road 214', (None, None)),
    ("Ballard WMA | Deer | Nov 7–8 | closed to everyone except drawn hunters (and one helper each) |", {'hunt_page': True}, 'hunt', None, (dt.date(SEASON_YEAR, 11, 7), dt.date(SEASON_YEAR, 11, 8))),
]


def selftest():
    K = _key() if (LINKS / '.github' / 'scripts' / 'kpc_us_key.py').exists() else _PlainKey()
    bad = 0
    for sent, ctx, exp_cl, exp_hint, exp_dates in SELFTEST:
        cl = classify(sent, ctx)
        got = None if (cl is None or cl.get('skip')) else cl['class']
        ok = got == exp_cl
        if ok and cl and not cl.get('skip'):
            if exp_hint and exp_cl == 'note': ok = cl.get('note_kind') == exp_hint
            elif exp_hint: ok = exp_hint in (cl.get('what') or '').lower()
            if exp_dates and ok:
                it = build_item('t', 'Test', 'US-0000', cl, sent, {'date': ctx.get('updated')}, 'US-XX', None)
                ok = (it['from'], it['to']) == tuple(d.isoformat() if d else None for d in exp_dates)
                if exp_cl == 'part' and ctx.get('updated') == dt.date(2021, 7, 9): ok = ok and bool(it.get('stale'))
        print(('ok   ' if ok else 'FAIL ') + f'{exp_cl!s:9} {sent[:70]!r} -> ' + (json.dumps({k: str(v) for k, v in cl.items() if k in ("class", "note_kind", "what", "from", "to", "skip", "lang")}) if cl else 'None'))
        bad += not ok
    # the matcher
    parks = {'P1': ('Hickory Run State Park', 'State Park', 41.0, -75.7, ''), 'P2': ('Hickory Run Natural Area', 'State Natural Area', 41.1, -75.6, ''),
             'P3': ('Big Basin Redwoods State Park', 'State Park', 37.17, -122.2, ''), 'P4': ('Peabody Wildlife Management Area', 'WMA', 37.2, -87.1, ''),
             'P5': ("John's Mountain Wildlife Management Area", 'Wildlife Management Area', 34.6, -85.1, ''), 'P6': ('Marben State Fishing Lake', 'State Fishing Lake', 33.4, -83.7, ''),
             'P7': ('Cybel Wildlife Management Area', 'Wildlife Management Area', 33.5, -83.8, '')}
    P4 = parks
    tests = [({'name': 'Big Basin Redwoods SP'}, ['P3'], ''), ({'name': 'Hickory Run'}, [], ''), ({'name': 'Peabody WMA Unit 2'}, ['P4'], 'Unit 2'),
             ({'name': "John's Mountain WMA"}, ['P5'], ''),
             ({'names': ['Cybel WMA', 'Marben PFA'], 'sent': 'Lake Margery at Marben PFA is currently closed to all access'}, ['P6'], '')]
    for row, exp, exp_part in tests:
        refs, part = tie(K, row, P4, 'US-XX')
        ok = refs == exp and part == exp_part
        print(('ok   ' if ok else 'FAIL ') + f"matcher {row.get('name') or row.get('names')} -> {refs} part={part!r}")
        bad += not ok
    # the Virginia place drop (multi-state forest, area US-KY): names another state's place -> dropped; a Kentucky county or district -> kept
    _FS_STATES_SAVE = fs_states().copy(); fs_states()['gwj'] = {'VA', 'WV', 'KY'}
    AREA_CTX['US-KY'] = {'state': 'kentucky', 'counties': {'pike', 'letcher', 'pulaski'}, 'districts': {'gwj': ['clinch']}}
    pk = {'US-4526': ('George Washington & Jefferson National Forest', 'National Forest', 37.09, -82.73, ''), 'US-11181': ('Sheltowee Trace National Recreation Trail', 'Trail', 37.0, -84.0, '')}
    for row, exp in [({'home': ['US-4526'], 'head': 'Mount Rogers National Recreation Area: Forest Service Road 84 Closed', 'sent': 'Mount Rogers National Recreation Area: Forest Service Road 84 Closed Beginning 9/1/25.'}, ['OUT-OF-STATE']),
                     ({'home': ['US-4526'], 'head': 'Clinch Ranger District road closure', 'sent': 'Forest Road 2097 on the Clinch Ranger District is closed.'}, ['US-4526']),
                     ({'home': ['US-4526'], 'head': 'Pine Mountain', 'sent': 'The Pine Mountain trailhead in Letcher County, Kentucky is closed.'}, ['US-4526']),
                     ({'home': ['US-4526'], 'head': 'Bolar Mountain Recreation Area - Twin Ridge Road Closure', 'sent': 'Twin Ridge Road near Bolar Mountain in Bath County, Virginia is closed until about 9/21/2026.'}, ['OUT-OF-STATE']),
                     ({'home': ['US-4484'], 'head': 'Tornado Damaged Area Closure', 'sent': 'This closure includes a portion of the Sheltowee Trace National Recreation Trail.'}, ['US-4484', 'US-11181'])]:
        refs, _ = tie(K, row, pk, 'US-KY', 'fs-gwj')
        ok = refs == exp
        print(('ok   ' if ok else 'FAIL ') + f"in-state: {row['head'][:50]} -> {refs}"); bad += not ok
    _FS_STATES.clear(); _FS_STATES.update(_FS_STATES_SAVE); AREA_CTX.pop('US-KY', None)
    cl = classify('Twin Ridge Road is closed until 9/21/2026.', {}); ok = bool(cl and cl.get('to') and cl['to'] < TODAY)
    print(('ok   ' if ok else 'FAIL ') + f"ended: to={cl and cl.get('to')} < today = not shown"); bad += not ok
    a = {'ref': 'R', 'details': '"Cliffside Trail #519 Closure"', 'title': ''}; b = {'ref': 'R', 'details': '"Cliffside Trail #519 is closed between Noes and Sawyer ramps."', 'title': 'Cliffside Trail #519 Closure'}
    ok = drop_title_twins([a, b]) == [b]; print(('ok   ' if ok else 'FAIL ') + 'title-only twin merged'); bad += not ok
    # the object of the Marben sentence
    cl = classify('Lake Margery at Marben PFA is currently closed to all access', {'names': ['Cybel WMA', 'Marben PFA']})
    ok = cl and cl['class'] == 'part' and cl['what'].lower().startswith('lake margery')
    print(('ok   ' if ok else 'FAIL ') + f"object: {cl and cl.get('what')} ({cl and cl.get('class')})"); bad += not ok
    print(f'SELFTEST {"PASS" if not bad else "FAIL"}: {len(SELFTEST) + len(tests) + 7 - bad} of {len(SELFTEST) + len(tests) + 7}')
    return bad == 0


# ======================================================================================= main
def main():
    global M
    if '--selftest' in sys.argv:
        selftest(); return
    OUT.mkdir(parents=True, exist_ok=True)
    state = load(OUT / 'state.json', {'areas': {}, 'hosts': {}, 'about': "Closures super-bot state. 'proven' is set BY A PERSON (chat 11 / Brandon) after the Kentucky side-by-side is graded; the 6-hour schedule runs only then."})
    M = Manners(BOT, state.get('hosts'))
    K = _key() if (LINKS / '.github' / 'scripts' / 'kpc_us_key.py').exists() else _PlainKey()
    if isinstance(K, _PlainKey): notice('KPC-Links checkout not found: plain name rules in use (set LINKS)')
    want = (os.environ.get('AREAS') or '').split()
    fresh = lambda a: (state['areas'].get(a) or {}).get('status') == 'done' and (state['areas'][a].get('read') or '') > (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=REFRESH_H)).strftime('%Y-%m-%dT%H:%MZ')  # noqa: E731
    areas = [a for a in want if a in QUEUE] if want else [a for a in QUEUE if not fresh(a)]
    review = {}
    done = []
    for a in areas:
        if late(): break
        try:
            if process_area(K, a, state, review): done.append(a)
        except Exception as e:  # noqa: BLE001
            notice(f'{a}: stopped: {str(e)[:200]}')
            state['areas'][a] = {**(state['areas'].get(a) or {}), 'status': 'error', 'why': str(e)[:160], 'read': NOW}
    if TEST or ('US-KY' in done): ky_test(state, review)
    state['hosts'] = M.resting()
    failed = [{'area': a, 'src': k, 'why': v.get('why'), 'url': v.get('url')} for a in done for k, v in ((load(OUT / f'{a}.json', {}) or {}).get('sources') or {}).items() if not v.get('ok') and not v.get('skipped')]
    state['last'] = {'when': NOW, 'areas': areas[:12], 'done': done, 'stat': STAT, 'manners': M.stat, 'browser': BROWSER_LOG[:40], 'failed': failed[:40]}
    save(OUT / 'state.json', state)
    try: write_review(state, review)
    except Exception as e: notice(f'review not written: {str(e)[:160]}')  # noqa: BLE001
    left = [a for a in QUEUE if not fresh(a)] if not want else [a for a in want if a in QUEUE and (state['areas'].get(a) or {}).get('status') != 'done']
    try:
        import kpc_status
        kpc_status.board(BOT, 'green', f"{len(done)} areas read, {sum(1 for a in done for _ in [0])} saved; see data/closures/review.md", 'chat 11 grades the Kentucky side-by-side; Brandon GO before any merge (CL-5)', f'{len(done)} done, {len(left)} left')
    except Exception as e: print('status helper: ' + str(e)[:120])  # noqa: BLE001
    notice(f"done {len(done)} areas ({', '.join(done[:10])}); {len(left)} left; requests {STAT['requests']}; manners {M.stat}")
    print(f'LEFT={len(left)}')


if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        pass
    except Exception as e:  # noqa: BLE001
        notice(f'stopped: {e}')
    sys.exit(0)
