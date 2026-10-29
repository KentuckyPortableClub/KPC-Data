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
  R6 Kentucky's test cases (KNOWN_ANSWERS, 10 rows from chat 11's grade) must ALL pass before the long run: Levi Jackson OFF +
     City of London hint, Otter Creek's Meade hint, Green WSR not read off Mammoth Cave's page, '708, 879' read as one number, …
  R7 (V4) a CLEAN official total (a total sentence naming the park, or a labelled 'Park Size:' row) more than 15% off = OFF;
     'unsure' only when no total-looking number exists, and it always carries a cause. Pages of ANOTHER unit (a different NPS code
     or FWS refuge slug, a refuge complex) count only where the sentence names this park. Handover hints come only from the park's
     own pages and must be about the park (its name or 'the park / the refuge…'), with a year >= 2000 or a change word + a new owner.
Manners: kpc_manners.py (robots, 2 s per host, back-off, three strikes = a day's rest); PDFs by range (first 400 KB).
Resumable: a park checked within REFRESH_DAYS (7) is skipped; MINUTES (55) per chunk; never fails (exit 0 always).

Env: AREAS='US-KY US-TN' (blank = the next unfinished areas in queue order) · MINUTES · LINKS (KPC-Links checkout, default
     'links') · OUT (data/truth) · REFRESH_DAYS · TEST=1 (Kentucky gate: prints PASS/FAIL as a notice and writes state['test'])
"""
import csv, json, math, os, pathlib, re, sys, time, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kpc_manners import Manners, page_text, links_in, pdf_text, browser_text  # noqa: E402

OUT = pathlib.Path(os.environ.get('OUT') or 'data/truth')
LINKS = pathlib.Path(os.environ.get('LINKS') or 'links')
T0 = time.time(); LIMIT = float(os.environ.get('MINUTES') or 55) * 60
REFRESH_DAYS = int(os.environ.get('REFRESH_DAYS') or 7)
TOL = 0.15
PDF_FIRST = 400_000
TODAY = time.strftime('%Y-%m-%d')
VER = 9   # Oct 28 (chat 11's KY grade): '708, 879' parse + summed lakes, other-unit pages, history words + stale years, unsure carries a cause, own-page handover hints, quoted URLs, 10-row gate, same-agency label
QUEUE = ['US-KY',
         'US-TN', 'US-NC', 'US-VA', 'US-WV', 'US-GA', 'US-AL', 'US-SC', 'US-FL', 'US-MS',
         'US-IN', 'US-IL', 'US-MO', 'US-WI', 'US-MN', 'US-IA', 'US-ND', 'US-SD',
         'US-PA', 'US-NY', 'US-NJ', 'US-CT', 'US-RI', 'US-MA', 'US-VT', 'US-NH', 'US-ME', 'US-MD', 'US-DE', 'US-DC',
         'US-AR', 'US-LA', 'US-OK', 'US-TX', 'US-KS', 'US-NE',
         'US-CO', 'US-WY', 'US-ID', 'US-MT', 'US-NV', 'US-AZ', 'US-NM',
         'US-CA', 'US-OR', 'US-WA', 'US-AK', 'US-HI', 'US-MI', 'US-OH', 'US-UT',
         'CA-ON', 'CA-QC', 'CA-NB', 'CA-NS', 'CA-PE', 'CA-NL',
         'CA-MB', 'CA-SK', 'CA-AB', 'CA-BC', 'CA-YT', 'CA-NT', 'CA-NU']
STATE_NAMES = {'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland', 'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina', 'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming', 'DC': 'District of Columbia'}
STAT = {'parks': 0, 'with_outline': 0, 'size_agree': 0, 'size_off': 0, 'size_unsure': 0, 'no_size': 0, 'ours_unknown': 0,
        'handover_hints': 0, 'retired': 0, 'pages_read': 0, 'skipped_fresh': 0, 'errors': 0}
M = None

# ---- reading sizes
# V4 fix 1: '708, 879 acres' (a comma, a space and exactly 3 digits) is ONE number, 708,879; the look-behind stops '2019, 100' from reading as 9,100
NUM = r'(\d{1,3}(?:,\s?\d{3}(?!\d))+(?:\.\d+)?|\d+(?:\.\d+)?(?:\s*million)?)'
UNIT = r'(acres?|ac\b|hectares?|\bha\b|square\s+(?:miles?|kilomet(?:er|re)s?)|sq\.?\s*(?:mi|km)\b|km\s*²|km2\b|mi\s*²)'
SIZE = re.compile(r'(?<![\d.,])' + NUM + r'\s*[-–\s]?\s*' + UNIT, re.I)
SIZE2 = re.compile(r'(?:acreage|area|size|total area|land area|park area)\s*[:=]?\s*(?<![\d.,])' + NUM + r'\s*' + UNIT + '?', re.I)
# 'two lakes of 40 and 60 acres' / '21.2 and 13.8 acre lakes': one candidate with the SUM; the parts are not totals
PNUM = r'\d[\d,]*(?:\.\d+)?'
SUMRX = re.compile(r'(?<![\d.,])((?:' + PNUM + r'(?:\s*-?\s*acres?)?\s*,\s*)*' + PNUM + r'(?:\s*-?\s*acres?)?\s*(?:and|&)\s*' + PNUM + r')\s*-?\s*acres?\b', re.I)
TOTALWORD = re.compile(r'encompass|cover|consist|compris|total|spans|protects|includes|spread over|acre (?:park|area|refuge|forest|preserve|reserve|site|tract|property|wma|wildlife|recreation|lake|monument|seashore|lakeshore)|'
                       r'(?:park|area|refuge|forest|preserve|reserve|site|tract|property|monument|seashore|lakeshore|wma|lands?) (?:of|is|has|contains|covers|totals?|encompasses|includes) ', re.I)
# V4 fix 3: HISTORY / marketing words always win (a land grant, a deed, 'of wilderness'); PART words lose to a CLEAN total sentence
HISTORY = re.compile(r'\bgrants?\b|grant of|conveyed|deeded|\bpatent|totall?ing|of wilderness|originally|\bonce\b|land grant|granted|surveyed|'
                     r'(?:established|founded|created|designated|dedicated|opened|acquired|purchased)\b[^.;]{0,60}\b(?:1[6-9]\d\d|20[01]\d)\b|\bgoal\b|\bplans? to\b|\bauthorized\b|\bapproved\b|\bproposed\b|acquisition boundary|\bup to\b|\bwill (?:protect|cover|include)', re.I)   # v9: 'established in 1938 as a 4,589-acre refuge', 'our goal is to protect 20,000 acres'
OLD_YEAR = re.compile(r'in (?:1[6-8]\d\d|19[0-4]\d)', re.I)   # an old year BEFORE the number ('In 1931, 800 acres were donated'): history
PART = re.compile(r'\blake\b.*\bacre|acre[- ]lake|reservoir|pond|campground|campsite|parking|picnic|golf|cemetery|garden|\blawns?\b|\bfields?\b|\bpools?\b|beach|marsh of|wetland of|per acre|acre[- ]feet|acre feet|acres? (?:of|in) (?:water|lake|pond|wetland|crop|timber|hunting|fields?)|'
                  r'burn|harvest|logged|planted|restored|treated|easement|acquired|purchas|added|expansion|donat|'
                  r'included in the|part of the \d|within the \d|lies within|is part of|portion of the \d|complex|together with', re.I)
NOTTOTAL = re.compile(HISTORY.pattern + '|' + PART.pattern, re.I)   # kept for readers of the old name
# HARD parts: never a park total, even in a sentence that names the park (a lake, water, habitat, acre-feet, a campground)
NEAR_PART = re.compile(r'within the park|\bplots?\b|adjacent|surrounding|in the middle of|\bfarm\b|statewide|across the state|state[- ]wide|preserve system|natural area preserves|manages (?:more than |over |about |nearly )?[\d,.]+ (?:million )?acres|acres? of public land|acres? (?:of )?(?:state|public) (?:land|lands|forests?|parks?) (?:statewide|across)', re.I)   # v9: only within 45 chars of the number (not 'surrounding communities' at the far end of the sentence)
HARD_PART = re.compile(r'acre[- ]lake|\blake\b[^.]{0,30}\bacres?\b|acres? (?:of|in) (?:water|lakes?|ponds?|wetlands?|crops?|timber|hunting|fields?|habitat|\w+ habitat|wilderness|forest lands?|national forest)|per acre|acre[- ]?feet|impoundment|campground|campsite|parking|picnic|golf|cemetery|food plots?|moist[- ]soil|\bconserve\b', re.I)
# candidates never chosen as the official number (history, another unit, a page of another unit, a summed part)
EXCLUDED = ('history', 'part of a sum', 'another park / unit named in the sentence', "a page of another unit; the sentence does not name this park",
            'a national unit on a state park page', 'a state unit on a national park page', 'part (a lake, a purchase, a campground…)', 'a map label (no sentence)')   # Oct 28 regrade 2: a lake or a map label is never the guess shown
NO_TOTAL_CAUSE = 'no total-looking sentence: numbers found were parts or other units'
# a CLEAN total: the park's own name in the sentence + a total word, or a labelled size row ('Park Size: 1007 acres')
CLEAN = re.compile(r'consists? of|encompass|compris|\bcovers?\b|\btotals?\b|\bspans\b|is an? [\d,]+(?:\.\d+)?[- ]acre|acre (?:park|forest|refuge|wma|area|preserve|reserve|site|tract|property|monument|battlefield|recreation area)|\bsize\b|total area|park size|land area|acreage', re.I)
LABEL = re.compile(r'(?:park size|total area|land area|size|acreage)\s*[:=]\s*$', re.I)
STALE = re.compile(r'as of (?:\w+ )?((?:19|20)\d\d)', re.I)
# another named unit right before the number ('Fort Donelson National Battlefield … Park Size: 1007 acres' on Fort Heiman's row; 'Hatchie NWR 11,556 acres')
NAMED_UNIT = re.compile(r"((?:[A-Z][\w'’-]+ ){1,4})(?:National (?:Wildlife Refuge|Park|Battlefield|Forest|Monument|Seashore|Lakeshore|Recreation Area|Historical Park|Historic Site|Military Park|River|Preserve)|State (?:Park|Forest|Nature Preserve|Natural Area|Resort Park|Historic Site)|Wildlife Management Area|WMA\b|NWR\b)")
HANDOVER = re.compile(r'\b((?:transferr?ed|transfer of|handed over|turned over|conveyed|deeded|donated|sold|ceded|leased|given|gift(?:ed)?)\s+(?:[^.;\n]{0,80}?\s)?(?:back )?(?:to|from)\s+(?:the\s+)?(?:city|county|town|village|parish|state|commonwealth|municipality|tribe|nation|district|authority|university|foundation|trust|conservancy|audubon|[A-Z][\w.&\'-]+(?:\s+[A-Z][\w.&\'-]+){0,4})[^.;\n]{0,90})', re.I)
MANAGED = re.compile(r'\b((?:is |are |now |currently |will be |has been )?(?:managed|operated|owned|maintained|administered|run|overseen)\s+(?:and (?:operated|maintained|managed) )?(?:jointly )?by\s+(?:the\s+)?[A-Z][\w.&\'-]+(?:\s+(?:of|and|&|for|the|[A-Z][\w.&\'-]+)){0,7})', re.I)
CLOSED = re.compile(r'\b((?:closed|closing|will close|has closed)\s+permanently|permanently\s+closed|no longer open to the public|is now closed to (?:the )?public|has been decommissioned|ceased operations|no longer (?:a |an )?(?:state |national )?(?:park|refuge|wildlife area|recreation area))[^.;\n]{0,80}', re.I)
NEWNAME = re.compile(r'\b((?:renamed|formerly (?:known as|called)|now (?:known as|called)|new name)[^.;\n]{0,80})', re.I)
KINDW = re.compile(r'\b(state|national|provincial|park|parks|forest|wildlife|management|area|areas|recreation|recreational|conservation|nature|natural|preserve|reserve|refuge|historic|historical|site|game|land|lands|wma|sp|sra|sf|nwr|trail|the|of|and|at|county|city|regional|unit|access|public|fishing|lake|hunting|outdoor|memorial|monument|wilderness|road)\b')
OTHER_CORES = set()
DESIG = {}         # {'state': bool, 'national': bool} of the park being read (T4: a State wild river is not the National river of the same name)
SHARED = {}        # url -> how many parks of the area call it their own page (v8: 3+ = an index page, never one park's size)
REF_STATES = {}    # ref -> [areas] for parks POTA lists in several states (v8: compare the WHOLE park)
OURS_WHOLE = {}    # ref -> acres summed over every state's key (v8)
MULTI = {}         # {'area', 'state' (full name), 'ky' (bool)}: set per area   # the other parks of the area (core names), set per area: a sentence naming another park is not this park's size
STATES_RX = re.compile(r'\b(alabama|alaska|arizona|arkansas|california|colorado|connecticut|delaware|florida|georgia|hawaii|idaho|illinois|indiana|iowa|kansas|kentucky|louisiana|maine|maryland|massachusetts|michigan|minnesota|mississippi|missouri|montana|nebraska|nevada|new hampshire|new jersey|new mexico|new york|north carolina|north dakota|ohio|oklahoma|oregon|pennsylvania|rhode island|south carolina|south dakota|tennessee|texas|utah|vermont|virginia|washington|west virginia|wisconsin|wyoming)\b', re.I)
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


def sentence_at(text, s, e, cap=260):
    """The sentence holding text[s:e] (cut at . ; ! ? or a line break), capped at `cap` chars each side."""
    a = max(0, s - cap); b = min(len(text), e + cap)
    left = text[a:s]; right = text[e:b]
    m = list(re.finditer(r'[.;!?]\s|\n', left)); left = left[m[-1].end():] if m else left
    m2 = re.search(r'[.;!?](?:\s|$)|\n', right); right = right[:m2.end()] if m2 else right
    return ' '.join((left + text[s:e] + right).split())


def left_of(text, s, cap=200):
    """The words of the SAME sentence before text[s] (an old year in the previous sentence is not this number's history)."""
    left = text[max(0, s - cap):s]
    m = list(re.finditer(r'[.;!?]\s|\n', left))
    return (left[m[-1].end():] if m else left).lower()


def name_rx(name):
    """A regex for the park's own name as written in a page (so 'Cedar Creek Lake WMA' is not read as a lake)."""
    ws = low(name).split()
    return re.compile(r'\W+'.join(re.escape(w) for w in ws), re.I) if ws else None


def name_core6(name):
    me = core(name)
    return me if len(me.replace(' ', '')) >= 6 else ''


def other_unit_named(sent, me):
    """True when the sentence names a park / unit that is not this one (another key park, or 'Hatchie National Wildlife Refuge')."""
    cs = core(sent)
    if me and me in cs: return False
    if any(oc in cs for oc in OTHER_CORES if len(oc) >= 6 and oc != me): return True
    for m in NAMED_UNIT.finditer(sent):
        c = core(m.group(1))
        if len(c) >= 4 and not (me and (me in c or c in me)): return True
    return False


def sizes_in(text, name, other_unit=False, is_pdf=False):
    """Every size mention in a page: [{'acres','as','line','total','clean','why','stale'}].
    total = looks like the park's whole size (a total word or the park's name near, and not a part / history / another unit);
    clean = a total sentence that names THIS park (or a labelled 'Park Size:' row): a clean number more than 15% off = OFF.
    other_unit = this page belongs to another unit (fix 2): only a sentence naming this park, or a labelled size row with its name, counts."""
    out = []; seen = set()
    me = core(name); me6 = name_core6(name); nrx = name_rx(name)
    cn = [w for w in me.split() if len(w) > 2][:3]
    def strip_name(x): return nrx.sub(' ', x) if nrx else x
    year_now = int(TODAY[:4])
    sums = []   # fix 1b: 'two lakes of 40 and 60 acres' -> one candidate with the sum; the parts are marked not-total
    for m in SUMRX.finditer(text):
        parts = [float(x.replace(',', '')) for x in re.findall(PNUM, m.group(1))]
        if len(parts) < 2 or any(p <= 0 for p in parts) or sum(parts) > 50_000_000: continue
        sent = sentence_at(text, m.start(), m.end()); line = ' '.join(text[max(0, m.start() - 110):m.end() + 110].split())
        hist = bool(HISTORY.search(sent)) or bool(OLD_YEAR.search(left_of(text, m.start())))
        sums.append((m.start(), m.end()))
        out.append({'acres': round(sum(parts), 1), 'as': ' + '.join(f'{p:g}' for p in parts) + ' acres', 'line': line, 'total': not hist and not other_unit_named(sent, me6),
                    'clean': False, 'why': 'history' if hist else 'sum of the pieces named in one sentence', 'stale': None})
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
            sent = sentence_at(text, m.start(), m.end()); sl = sent.lower()
            before = text[max(0, m.start() - 24):m.start()]
            label = bool(LABEL.search(before))
            name_in = bool(me6 and me6 in core(sent)) or (label and bool(me6 and me6 in core(text[max(0, m.start() - 400):m.start()])))
            why = ''
            own_subject = bool(re.match(r'^\s*(?:the|this) (?:park|area|refuge|forest|preserve|sanctuary|site|property|wma|monument|seashore|lakeshore)\b', sent.strip(), re.I)) and not other_unit
            looks = bool(TOTALWORD.search(near)) or any(w in near for w in cn) or label
            if is_pdf and not (label or (name_in and len(sent.split()) >= 6)): looks = False; why = 'a map label (no sentence)'   # Cumberland Gap '15 acres', Taylorsville '248': labels on a map PDF
            if any(a0 <= m.start() < b0 for a0, b0 in sums): looks = False; why = 'part of a sum'
            if HISTORY.search(sl) or OLD_YEAR.search(left_of(text, m.start())): looks = False; why = 'history'
            hard = (bool(HARD_PART.search(strip_name(sl))) or bool(NEAR_PART.search(strip_name(text[max(0, m.start() - 45):m.end() + 45].lower())))) and not label; soft = bool(PART.search(strip_name(sl))) and not label   # the SAME sentence, not the neighbour's
            clean = bool(looks and not why and (label or ((name_in or own_subject) and CLEAN.search(sl))) and not hard)
            if looks and not why and (hard or (soft and not clean)): looks = False; why = 'part (a lake, a purchase, a campground…)'
            if looks and DESIG.get('state') and re.search(r'\bnational\b', near) and not re.search(r'\bstate\b', near): looks = clean = False; why = 'a national unit on a state park page'
            if looks and DESIG.get('national') and re.search(r'\bstate (?:wild river|natural area|nature preserve|park|forest|wma)\b', near) and not re.search(r'\bnational\b', near): looks = clean = False; why = 'a state unit on a national park page'
            if looks and not name_in and not own_subject and other_unit_named(sent, me6): looks = clean = False; why = 'another park / unit named in the sentence'   # a sentence that names THIS park is this park's (Levi Jackson: 'Laurel County' is not Laurel River Lake)
            if looks and other_unit and not name_in: looks = clean = False; why = "a page of another unit; the sentence does not name this park"
            if looks and not why: why = 'clean total' if clean else 'total-looking'
            if not looks and not why: why = 'no total words near it'
            stale = None
            ms = STALE.search(text[m.end():m.end() + 40])
            if ms and year_now - int(ms.group(1)) > 3: stale = int(ms.group(1))
            out.append({'acres': round(a, 1), 'as': f'{n} {unit}', 'line': line, 'total': looks, 'clean': clean, 'why': why, 'stale': stale, 'sent': sent[:300]})
            if len(out) >= 12: return out
    return out


def off_by(ours, theirs):
    if not ours or not theirs: return None
    return abs(ours - theirs) / theirs


UNIT_WHYS = ('another park / unit named in the sentence', "a page of another unit; the sentence does not name this park", 'a national unit on a state park page', 'a state unit on a national park page')


def judge(ours, sizes):
    """(verdict, chosen size dict or None, pct). agree beats everything (any number on the park's own pages within 15%, never one
    tied to another unit); else the best CLEAN total, else the best total-looking size = OFF (fix 4: a clean number more than 15%
    off is never 'unsure'); 'unsure' only when NO total-looking candidate exists (then the nearest usable number is shown as a guess)."""
    if not sizes: return 'no size on page', None, None
    if not ours: return 'ours unknown', (sizes[0] if sizes else None), None
    usable = [s for s in sizes if s['why'] not in UNIT_WHYS]
    agree = [s for s in usable if off_by(ours, s['acres']) is not None and off_by(ours, s['acres']) <= TOL]
    if agree:
        best = min(agree, key=lambda s: off_by(ours, s['acres'])); return 'agree', best, round(off_by(ours, best['acres']) * 100)
    for pool in ([s for s in usable if s.get('clean')], [s for s in usable if s['total']]):
        if pool:
            best = min(pool, key=lambda s: off_by(ours, s['acres']))
            return 'off', best, round(off_by(ours, best['acres']) * 100)
    guess = [s for s in usable if s['why'] not in EXCLUDED] or []
    best = min(guess, key=lambda s: off_by(ours, s['acres'])) if guess else None
    return 'unsure', best, (round(off_by(ours, best['acres']) * 100) if best else None)


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


NPS_GENERIC = {'aboutus', 'subjects', 'learn', 'planyourvisit', 'index', 'articles', 'media', 'orgs', 'places', 'people', 'stories'}
OWN = {}   # the unit slug of THIS park's own page: {'nps': 'maca' | None, 'fws': 'clarks-river' | None, 'core': '...'} (fix 2)


def unit_of(u):
    """('nps', 'maca') / ('fws', 'clarks-river') / None for a URL."""
    m = NPS_UNIT.search(u)
    if m and 'nps.gov' in u and m.group(1) not in NPS_GENERIC: return ('nps', m.group(1))
    m = FWS_UNIT.search(u)
    if m and 'fws.gov' in u: return ('fws', m.group(1))
    return None


def own_unit_of(name, pages):
    """The park's OWN unit slug: the slug of its first own page whose slug fits the park's name (an FWS slug is the name; an NPS code is
    4 letters of it), else the first own page's slug when nothing contradicts it. Green WSR's page on eec.ky.gov gives no unit: the
    NPS 'maca' map is then NOT its own unit (fix 2)."""
    me = core(name); words = me.split()
    own = {'nps': None, 'fws': None}
    for u, why in pages:
        if not why.startswith("the park's page"): continue
        un = unit_of(u)
        if not un: continue
        kind, slug = un
        if kind == 'fws':
            sc = core(slug.replace('-', ' '))
            if sc and (sc in me or me in sc or sum(w in me for w in sc.split()) >= 1): own['fws'] = own['fws'] or slug
        else:   # NPS codes: MAmmoth CAve = maca, CUmberland GAp = cuga, FOrt DOnelson = fodo, GReat SMoky = grsm; Fort Heiman is NOT fodo
            w0 = words[0] if words else ''; rest = ''.join(words[1:])
            fits = bool(w0) and (slug == w0[:4] or (slug[:2] == w0[:2] and (not rest or rest.startswith(slug[2]) or slug[2:4] in rest)))
            if fits: own['nps'] = own['nps'] or slug
    return own


def is_other_unit(u, own):
    """fix 2: the page belongs to a different NPS / FWS unit than the park's own page (or the park has no unit page at all)."""
    un = unit_of(u)
    if not un: return bool(re.search(r'/refuge/[a-z0-9-]*complex', u))
    kind, slug = un
    return own.get(kind) != slug


def candidate_pages(ref, park, web, docs, ky):
    """Official pages for one park, best first, de-duplicated; never anything off an agency / government site.
    -> [(url, why, other_unit)]; also sets OWN (the park's own unit slugs). NPS 'statistics.htm' only for the park's OWN unit;
    'newsreleases' pages are listed for handover hints only (never the size read)."""
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
    own = own_unit_of(park['n'], out)
    for u, why in ((k.get('off'), 'official map (Kentucky answer key)'), (k.get('off2'), 'second official map (Kentucky answer key)'), (((d.get('map') or {}).get('url')), 'official map (documents bot)'), (w.get('map'), 'official map (parkinfo-web)')):
        if u and str(u).lower().split('?')[0].endswith('.pdf'): add(u, why)
    for u in (((d.get('rules') or {}).get('url')),):
        add(u, 'rules page (documents bot)')
    # federal unit pages chat 8 found readable (OFFICIAL_MAPS FEDERAL_desk: NPS + FWS READY), for the park's OWN unit only
    if own.get('nps'):
        add(f"https://www.nps.gov/{own['nps']}/learn/management/statistics.htm", 'NPS park statistics page')
        add(f"https://www.nps.gov/{own['nps']}/learn/news/newsreleases.htm", 'NPS news releases')
    if own.get('fws'):
        add(f"https://www.fws.gov/refuge/{own['fws']}/about-us", 'FWS refuge about page')
    OWN.clear(); OWN.update(own); OWN['core'] = name_core6(park['n'])
    return [(u, why, is_other_unit(u, own)) for u, why in out[:6]]


ABOUT_RX = re.compile(r'\babout\b|history|overview|park info|general info|facts|at a glance|\bthe park\b|welcome', re.I)
_HTML_CACHE = {}


GENERIC_PATH = re.compile(r'^/(about|aboutus|about-us)/?$|/aboutus/|accessibility|privacy|disclaimer|lawsandpolicies|/news|newsreleases|press|regulation|/air/|/waste|careers|employment|contact|faq|sitemap|/orgs/|/subjects/', re.I)


def about_links(u, name=''):
    """Up to 2 'about / history / overview' links of the PARK'S OWN site section (fix 5): a dedicated park site (host carries the
    park's name) may give any about page; on an agency site the link must stay under the park page's first path folder
    (nps.gov/fodo/…, eec.ky.gov/Nature-Preserves/…); the agency's /About, /accessibility, /lawsandpolicies and news never."""
    html = _HTML_CACHE.get(u) or ''
    out = []
    pu = urllib.parse.urlparse(u); seg = [s for s in pu.path.split('/') if s]
    first = seg[0].lower() if seg else ''
    hc = re.sub(r'[^a-z]', '', host_of(u).lower()); me6 = name_core6(name)
    dedicated = bool(me6) and any(w for w in me6.split() if len(w) >= 5 and w in hc)
    for link, txt in links_in(html, u):
        if host_of(link) != host_of(u) or link.rstrip('/') == u.rstrip('/'): continue
        if re.search(r'\.(pdf|jpe?g|png|zip)(\?|$)', link, re.I): continue
        lp = urllib.parse.urlparse(link).path
        if GENERIC_PATH.search(lp): continue
        if not dedicated:
            ls = [s for s in lp.split('/') if s]
            if not first or not ls or ls[0].lower() != first: continue
        if ABOUT_RX.search(txt) or re.search(r'/(about|history|overview|park-info|general-information)', link, re.I):
            if link not in [x[0] for x in out]: out.append((link, "about / history page of the park's site"))
        if len(out) >= 2: break
    return out


def safe_url(u):
    """fix 6: a path with spaces or other unsafe characters is quoted before the fetch; the review keeps the original."""
    try:
        p = urllib.parse.urlsplit(u)
        return urllib.parse.urlunsplit((p.scheme, p.netloc, urllib.parse.quote(p.path, safe=':/?&=%+@,;!$*()~'), urllib.parse.quote(p.query, safe=':/?&=%+@,;!$*()~'), ''))
    except Exception: return u  # noqa: BLE001


def read_page(u):
    """-> (status, kind, text). PDFs by range (first 400 KB)."""
    looks_pdf = u.lower().split('?')[0].endswith('.pdf')
    st, hd, body, final = M.get(safe_url(u), rng=(0, PDF_FIRST - 1) if looks_pdf else None)
    if st not in (200, 206): return (str(st) if not isinstance(st, int) else f'HTTP {st}'), '', ''
    STAT['pages_read'] += 1
    ct = (hd.get('content-type') or '').lower()
    if body[:5] == b'%PDF-' or 'application/pdf' in ct:
        txt = pdf_text(body, 3)
        if not txt and looks_pdf:   # Oct 28: a 400 KB slice of a compressed PDF cannot be parsed: read the whole file (4 MB at most)
            total = int(((hd.get('content-range') or '').rsplit('/', 1)[-1] or 0) if '/' in (hd.get('content-range') or '') else (hd.get('content-length') or 0) or 0)
            if 0 < total <= 4_000_000 or not total:
                st2, hd2, body2, _ = M.get(safe_url(u))
                if st2 in (200, 206) and body2[:5] == b'%PDF-': txt = pdf_text(body2, 3)
        return ('ok' if txt else 'ok, no readable text'), 'pdf', txt
    if looks_pdf: return 'opened, not a PDF', '', ''
    html = body.decode('utf-8', 'replace')
    if len(_HTML_CACHE) > 40: _HTML_CACHE.clear()
    _HTML_CACHE[u] = html
    t = page_text(html)
    if len(t) < 200 and SOFT404.search(t): return 'soft 404', 'page', ''
    if len(t) < 400:   # Oct 28: a script-built page ('Explore | … Skip to Main Content'): one headless-browser read when allowed
        bt = browser_text(u, M)
        if len(bt) > len(t): return 'ok (browser)', 'page', bt
    return 'ok', 'page', t


SUBJECT_RX = re.compile(r'\bthe (?:park|area|refuge|property|site|forest|preserve|battlefield|wma|land|lands|campground)\b', re.I)
CHANGE_RX = re.compile(r'transferr?ed|transfer of|deeded|conveyed|\bnow\b|currently|managed by|operated by|handed over|turned over|renamed|closed|no longer', re.I)
OWNER_RX = re.compile(r'(?:to|by|from)\s+(?:the\s+)?((?:City|County|Town|Village|Commonwealth|State|Department|Division|Office|Kentucky|Tennessee|National|U\.?S\.?|US|United States|[A-Z][\w.&\'’-]+)(?:\s+(?:of|and|&|for|the|[A-Z][\w.&\'’-]+)){0,6})')
MANAGER_KEY = {'kdfwr': 'fish and wildlife', 'fws': 'fish and wildlife service', 'nps': 'national park service', 'usfs': 'forest service', 'fs': 'forest service', 'usace': 'corps of engineers', 'tva': 'tennessee valley',
               'city': 'city', 'county': 'county', 'state': 'state', 'federal': 'federal', 'dgi': 'state parks', 'parks': 'state parks', 'ngo': 'nonprofit'}


def same_owner(owner, manager):
    """True when the owner named in a hint is the manager our land record already names (then a plain 'Owned by X' is not news)."""
    o = low(owner); mg = low(manager)
    if not o or not mg: return False
    if mg in o or o in mg: return True
    for k, v in MANAGER_KEY.items():
        if re.search(r'\b' + k + r'\b', mg) and v in o: return True
    if re.search(r'\bstate\b|kentucky|commonwealth', mg) and re.search(r'\bstate\b|kentucky|commonwealth|department of|division of|office of', o) and not re.search(r'city|county|fiscal court|town', o): return True
    if re.search(r'\bfederal\b|\bus\b|national', mg) and re.search(r'national park service|fish and wildlife service|forest service|corps of engineers|tennessee valley|united states|\bu\.?s\.?\b', o): return True
    return False


def hints_in(text, name, src, why, manager=''):
    """fix 5: a handover hint must be ABOUT this park: the sentence names the park (6-letter core) or says 'the park / the area /
    the refuge / the property / the site'; a plain 'Owned by X' counts only when X is not our land record's manager AND the line
    says transferred / deeded / conveyed / now / currently / managed by / operated by; a hint is kept only with a year >= 2000,
    or with those change words naming an owner different from ours. 'owner_now' = the owner named in the line (or None)."""
    out = []; me6 = name_core6(name)
    for rx, kind in ((HANDOVER, 'transfer'), (MANAGED, 'managed by'), (CLOSED, 'closed'), (NEWNAME, 'renamed')):
        for m in rx.finditer(text):
            s = max(0, m.start() - 100); e = min(len(text), m.end() + 100)
            line = ' '.join(text[s:e].split())
            sent = sentence_at(text, m.start(), m.end(), 300)
            about = (me6 and me6 in core(sent)) or (me6 and me6 in core(text[max(0, m.start() - 350):m.end()])) or SUBJECT_RX.search(sent)
            if not about: continue
            if kind == 'managed by' and not re.search(r'(city|county|town|village|parish|municipal|tribe|nation|university|college|foundation|trust|conservancy|audubon|authority|district|corporation|company|association|club|church|greensource|society|friends of|partnership|nonprofit|non-profit|inc\\b|llc|fiscal court|forest service|tennessee valley|corps of engineers)', line, re.I):
                continue   # 'managed by the Division of Parks' is the normal case: only OTHER kinds of owner are hints
            om = OWNER_RX.search(m.group(0)) or OWNER_RX.search(sent)
            owner = re.split(r'\.\s', om.group(1))[0].strip(' .,') if om else None
            different = bool(owner) and not same_owner(owner, manager)
            change = bool(CHANGE_RX.search(sent))
            if kind == 'managed by' and re.search(r'\bowned by\b', m.group(0), re.I) and not (different and change): continue   # plain ownership, not a handover
            years = [int(y) for y in re.findall(r'\b((?:19|20)\d\d)\b', sent)]
            recent = any(y >= 2000 for y in years)
            if not recent and not (change and different) and kind not in ('closed',): continue
            out.append({'kind': kind, 'line': line[:300], 'src': src, 'why': why, 'date_hint': str(max(years)) if years else None, 'owner_now': owner if (owner and different) else None})
            if len(out) >= 6: return out
    return out


# ---- news sources (agency newsrooms; each row verified on first use)
def news_hints(area, parks_by_core, news, nstate, managers=None):
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
                    hs = hints_in(t3, pc, link, f"agency news ({row.get('agency') or host_of(u)})", (managers or {}).get(ref, ''))
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
    pages = [(u, why, other or SHARED.get(u, 0) >= 3) for u, why, other in pages]   # v8: an agency INDEX page (the 'own page' of 3+ parks) counts only sentences that name this park
    DESIG.clear(); DESIG.update({'state': bool(re.search(r'\bstate\b', park['n'] + ' ' + park.get('t', ''), re.I)), 'national': bool(re.search(r'\bnational\b', park['n'] + ' ' + park.get('t', ''), re.I))})
    if not pages: r['verdict'] = 'no official page on file'; return r
    found = []; mg = (ours or {}).get('manager') or ''
    def has_total(): return any(s['total'] for s in found)
    for u, why, other in pages:
        if late(): break
        st, kind, text = read_page(u)
        r['pages'].append({'url': u, 'why': why, 'status': st, **({'other_unit': True} if other else {})})
        if st != 'ok' or not text: continue
        if 'news' not in why:   # fix 7: news pages never feed the size read
            for s in sizes_in(text, park['n'], other, kind == 'pdf'): s['url'] = u; found.append(s)
        if not other and (why.startswith("the park's page") or why.startswith('about') or 'news' in why or 'statistics' in why or 'about page' in why):
            r['handover'].extend(hints_in(text, park['n'], u, why, mg))   # fix 5: hints only from the park's own pages
        if kind == 'page' and not has_total() and why.startswith("the park's page") and len(r['pages']) < 7:
            for u2, why2 in about_links(u, park['n']):   # the size often sits on 'About the park' / 'History', not the home page
                if late(): break
                st2, k2, t2 = read_page(u2)
                r['pages'].append({'url': u2, 'why': why2, 'status': st2})
                if st2 != 'ok' or not t2: continue
                for s in sizes_in(t2, park['n'], other): s['url'] = u2; found.append(s)
                r['handover'].extend(hints_in(t2, park['n'], u2, why2, mg))
                if has_total(): break
        if has_total() and r['handover']: break
        if len(found) >= 4 and 'news' not in why: continue
    r['sizes'] = [{'acres': s['acres'], 'as': s['as'], 'line': s['line'], 'total_like': s['total'], 'clean': s['clean'], 'why': s['why'], 'url': s['url'], **({'stale_year': s['stale']} if s.get('stale') else {})} for s in found[:8]]
    v, chosen, pct = judge(ours['acres'] if ours else 0, found)
    if v == 'off' and chosen and MULTI.get('area', '').startswith('US-') and STATES_RX.search(chosen['line']) and not re.search(MULTI.get('state', 'zzz'), chosen['line'], re.I):
        v = 'unsure'; r['note'] = 'the agency figure may cover several states; our outline may be this state\'s share only'
    elif v == 'off' and chosen and re.search(r'national (forest|park|refuge|river|recreation|trail|seashore|lakeshore|monument|battlefield)', park.get('t', '') + ' ' + park['n'], re.I) and MULTI.get('ky') and abs(chosen['acres']) > 1.8 * (ours['acres'] or 1):
        v = 'unsure'; r['note'] = 'federal unit: the Kentucky key holds only the Kentucky piece; the agency figure is the whole unit'
    if ours and ours.get('unknown_pieces') and not ours.get('acres'): v = 'ours unknown'
    if ours and ours.get('whole_park'): r['note'] = f"whole park compared (POTA lists it in {len(ours.get('acres_by_state') or {})} states: {ours.get('acres_by_state')})"
    r['verdict'] = v; r['pct'] = pct
    if chosen:
        r['official'] = {'acres': chosen['acres'], 'as': chosen['as'], 'line': chosen['line'], 'url': chosen['url'], 'read': TODAY, 'clean': chosen['clean'], 'why': chosen['why']}
        if chosen.get('stale'): r['official']['stale_year'] = chosen['stale']
        r['same_agency'] = same_agency(chosen['url'], ours or {})   # fix 9: KDFWR outline vs a KDFWR page proves our copy, not KDFWR
    # a transfer hint from the land record itself: PAD-US says City / County / private while POTA calls it a state park
    if mg and re.search(r'city|county|local|private|ngo|non', mg, re.I) and re.search(r'state', park.get('t', ''), re.I):
        r['handover'].append({'kind': 'land record', 'line': f"our outline's land record says manager = {mg}, POTA calls it a {park.get('t')}", 'src': ours.get('src'), 'why': 'the outline source', 'date_hint': None, 'owner_now': mg})
    best_hint = next((h for h in r['handover'] if h.get('owner_now')), None)
    r['owner_now'] = best_hint['owner_now'] if best_hint else None
    if v == 'off' and chosen and ours: r['cause'] = cause_of(ours, chosen['acres'], park)
    elif v == 'unsure' and ours:   # fix 4: unsure always carries a cause
        r['cause'] = r.get('note') or (NO_TOTAL_CAUSE + (f" (nearest number found: {chosen['as']}, {chosen['why']})" if chosen else ''))
    r['score'], r['score_parts'] = score_of(ours or {'pin': 'none', 'pieces': []}, v, bs)
    return r


AGENCY_HOST = (('fw.ky.gov', r'kdfwr|fish\s*(?:&|and)\s*wildlife|hunting areas'), ('nps.gov', r'\bnps\b|national park'), ('fws.gov', r'\bfws\b|fish and wildlife service|refuges'),
               ('fs.usda.gov', r'forest service|usfs|dbnf'), ('parks.ky.gov', r'state parks'), ('eec.ky.gov', r'nature preserves|natural areas|forestry|state forest'), ('usace', r'corps of engineers|usace'))


def same_agency(url, ours):
    """True when the official page's host and our outline's source name the same agency (fix 9)."""
    h = host_of(url or ''); src = str(ours.get('src') or '') + ' ' + str(ours.get('manager') or '')
    for host, rx in AGENCY_HOST:
        if host in h and re.search(rx, src, re.I): return True
    return False


def cause_of(ours, agency, park):
    """T6 (chat 8): one of five causes so a person sees classes, not a pile: our union (one of our pieces alone matches the
    agency) · boundary vs owned (an NPS / FWS unit line bigger than the owned land) · multi-state · agency smaller (we may hold water or
    a lease) · agency bigger (we may miss a tract)."""
    pieces = [p for p in (ours.get('pieces') or []) if isinstance(p[2], (int, float)) and p[2] > 0]
    if len(pieces) > 1 and any(abs(p[2] - agency) / agency <= TOL for p in pieces): return 'our union: one of our pieces alone matches the agency (double count?)'
    if re.search(r'national', park.get('t', '') + ' ' + park['n'], re.I) and ours['acres'] > agency and re.search(r'nps|fws|unit', str(ours.get('src')) + ' ' + str(pieces[:1]), re.I):
        return 'boundary vs owned: our line may be the authorized boundary, the agency counts owned land (rule 1: use owned land)'
    if ours['acres'] > agency: return 'agency smaller: our outline may hold water, a lease or a neighbour tract'
    return 'agency bigger: our outline may miss a tract'


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
    OTHER_CORES.clear(); OTHER_CORES.update(parks_by_core)
    MULTI.clear(); MULTI.update({'area': area, 'state': STATE_NAMES.get(area[3:], 'zzz'), 'ky': area == 'US-KY'})
    SHARED.clear()
    for ref, p in parks.items():
        for u in {p.get('web') or '', (web.get(ref) or {}).get('web') or '', (docs.get(ref) or {}).get('page') or ''}:
            if u.startswith('http'): SHARED[u] = SHARED.get(u, 0) + 1
    for ref in sorted(parks):
        if late(): break
        old = D['parks'].get(ref)
        if old and old.get('ver', 0) >= VER and old.get('checked', '') >= fresh_cut: fresh += 1; STAT['skipped_fresh'] += 1; continue
        park = parks[ref]
        ours = ours_ky(ref, park, ak) if area == 'US-KY' else ours_key(key.get(ref) or {})
        if ours and len(REF_STATES.get(ref) or []) > 1:   # v8: a park POTA lists in several states (Smokies, Big South Fork, Chickamauga): compare the WHOLE park
            whole = 0; parts = {}
            for a2 in REF_STATES[ref]:
                o2 = ours_ky(ref, park, ak) if a2 == 'US-KY' else ours_key((load(f'data/{"us" if a2.startswith("US") else "ca"}-key/{a2}.json', {}).get('parks') or {}).get(ref) or {})
                if o2 and o2.get('acres'): whole += o2['acres']; parts[a2] = o2['acres']
            if whole and whole > (ours.get('acres') or 0): ours = dict(ours, acres=round(whole), acres_by_state=parts, whole_park=True)
        STAT['parks'] += 1
        if not ours:
            D['parks'][ref] = {'n': park['n'], 't': park.get('t', ''), 'ours': None, 'verdict': 'no outline', 'checked': TODAY, 'ver': VER, 'handover': [], 'score': None}
            continue
        STAT['with_outline'] += 1
        try:
            new = one_park(ref, park, ours, web, docs, ky, retired, bscore.get(ref))
            if old and old.get('verdict') not in (None, 'not read', 'no official page on file') and not any(p.get('status') == 'ok' for p in new.get('pages') or []):
                old['last_read_failed'] = TODAY; old['ver'] = VER; new = old   # every page failed (403 / rest): keep what we knew
            D['parks'][ref] = new
        except Exception as e:  # noqa: BLE001
            STAT['errors'] += 1
            D['parks'][ref] = {'n': park['n'], 'ours': ours, 'verdict': 'bot error: ' + str(e)[:80], 'checked': TODAY, 'ver': VER, 'handover': [], 'score': None}
        v = D['parks'][ref].get('verdict')
        STAT['size_agree' if v == 'agree' else 'size_off' if v == 'off' else 'size_unsure' if v == 'unsure' else 'ours_unknown' if v == 'ours unknown' else 'no_size'] += 1
        done += 1
    if not late():
        nstate = state.setdefault('news', {})
        try:
            managers = {ref: ((r.get('ours') or {}).get('manager') or '') for ref, r in D['parks'].items()}
            for ref, hs in news_hints(area, parks_by_core, news, nstate, managers).items():
                if ref in D['parks']:
                    D['parks'][ref].setdefault('handover', []).extend(hs)
        except Exception as e:  # noqa: BLE001
            STAT['errors'] += 1; notice(f'{area}: news read failed: {str(e)[:100]}')
    shared_nums = {}
    for ref, r in D['parks'].items():
        of = r.get('official') or {}
        if r.get('verdict') in ('off', 'unsure') and of.get('acres'): shared_nums.setdefault((of['acres'], of.get('url', '')), []).append(ref)
    for (acres, url), refs in shared_nums.items():
        if len(refs) < 3: continue
        for ref in refs:   # v8 (chat 11, WV/VA): the statewide '1.4 million acres' / a system total taken as every park's size
            r = D['parks'][ref]
            if r.get('verdict') == 'off': STAT['size_off'] -= 1; STAT['size_unsure'] += 1
            r['verdict'] = 'unsure'; r['pct'] = None; r['cause'] = f'a number {len(refs)} parks share from one page ({acres:,.0f} ac): an agency total, not this park'
            r['official'] = None
    for ref, r in D['parks'].items():
        seen = set(); hs = []
        for h in r.get('handover') or []:
            k = (h.get('kind'), h.get('line', '')[:80])
            if k not in seen: seen.add(k); hs.append(h)
        r['handover'] = hs[:8]
    STAT['handover_hints'] += sum(1 for r in D['parks'].values() if r.get('handover'))
    D['read'] = TODAY; D['counts'] = counts(D)
    if os.environ.get('TEST') == '1' and area != 'US-KY':
        res, why = area_test(area, D); state['test'] = {'when': TODAY, 'result': res, 'why': why, 'area': area}
        notice(f'{area} TEST {res}: {why[:600]}'); print('TEST=' + res)
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
        src_line = ('same agency: ' if r.get('same_agency') else '') + (f"stale: as of {of['stale_year']} · " if of.get('stale_year') else '') + (of.get('line') or '')[:200]
        rows.append([r.get('score') if r.get('score') is not None else '', ref, r.get('n', ''), r.get('t', ''), o.get('pin', ''), r.get('verdict', ''), o.get('acres', ''), of.get('acres', ''), r.get('pct', ''),
                     of.get('url', ''), src_line, ' | '.join(h['kind'] + ': ' + h['line'][:120] for h in (r.get('handover') or [])[:2]), o.get('src', '')[:80],
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
        uns = [(ref, r) for ref, r in D['parks'].items() if r.get('verdict') == 'unsure']
        hov = [(ref, r) for ref, r in D['parks'].items() if r.get('handover')]
        agr = [r for r in D['parks'].values() if r.get('verdict') == 'agree']
        if not off and not hov and not uns and not agr: continue
        L += ['', f'## {a}', '']
        if agr:
            same = sum(1 for r in agr if r.get('same_agency'))
            L += [f'**Agree:** {len(agr)} parks: {same} agree (same agency: our outline came from the agency whose page we read, so this proves our copy, not the agency) · {len(agr) - same} agree (second agency).', '']
        if off:
            L += ['**Size more than 15% off (our outline vs the agency):**', '']
            for ref, r in sorted(off, key=lambda x: -(x[1].get('pct') or 0))[:60]:
                of = r.get('official') or {}
                stale = f" · stale: agency figure is 'as of {of['stale_year']}'" if of.get('stale_year') else ''
                L.append(f"- {ref} {r['n']}: ours {r['ours']['acres']:,} ac vs agency {of.get('as', '')} (= {int(of.get('acres') or 0):,} ac; {r.get('pct')}% off) · cause: {r.get('cause', '?')}{stale} · [{host_of(of.get('url', ''))}]({of.get('url', '')}) · “{(of.get('line') or '')[:160]}”")
            if len(off) > 60: L.append(f'- … {len(off) - 60} more in {a}.json')
        if uns:
            L += ['', '**Unsure (no clean total found; the nearest number is only a guess):**', '']
            for ref, r in uns[:60]:
                of = r.get('official') or {}
                L.append(f"- {ref} {r['n']}: ours {r['ours']['acres']:,} ac · cause: {r.get('cause', '?')}" + (f" · [{host_of(of.get('url', ''))}]({of.get('url', '')})" if of.get('url') else ''))
            if len(uns) > 60: L.append(f'- … {len(uns) - 60} more in {a}.json')
        if hov:
            L += ['', '**Handover / closure hints (a person decides; nothing applied):**', '']
            for ref, r in hov[:60]:
                own = f" · owner now: {r['owner_now']}" if r.get('owner_now') else ''
                for h in r['handover'][:2]:
                    L.append(f"- {ref} {r['n']} · {h['kind']}: “{h['line'][:200]}”{own} · [{host_of(h.get('src', ''))}]({h.get('src', '')})")
            if len(hov) > 60: L.append(f'- … {len(hov) - 60} more in {a}.json')
    t = state.get('test')
    if t: L += ['', '## Kentucky test gate', '', f"- {t.get('when')}: **{t.get('result')}** · {t.get('why')}"]
    (OUT / 'review.md').write_text('\n'.join(L) + '\n', encoding='utf-8')


def _hint_names(p, rx): return any(re.search(rx, (h.get('line') or '') + ' ' + str(h.get('owner_now') or ''), re.I) for h in (p.get('handover') or []))
def _off(p): return p.get('official') or {}


KNOWN_ANSWERS = [   # R6 + chat 11's grade (Oct 28): the Kentucky gate; PASS only when every row passes
    ('US-1264', 'Levi Jackson OFF (722 vs ~896) + a hint naming the City of London', lambda p, D: p.get('verdict') == 'off' and _off(p).get('acres') and abs(_off(p)['acres'] - 896) < 60 and _hint_names(p, r'city of london')),
    ('US-8144', 'Otter Creek: a hint naming Meade', lambda p, D: _hint_names(p, r'meade')),
    ('US-10105', "Green WSR: official page is not Mammoth Cave's (/maca/)", lambda p, D: '/maca/' not in str(_off(p).get('url') or '')),
    ('US-10104', 'Red River WSR: official acres is not 879 (the "708, 879" parse)', lambda p, D: _off(p).get('acres') != 879),
    ('US-0295', 'Clarks River NWR: official acres is not the 73,962 land grant', lambda p, D: _off(p).get('acres') != 73962),
    ('US-0703+US-3790', 'Fort Donelson and Fort Heiman do not share one official page', lambda p, D: not (_off(D['parks'].get('US-0703') or {}).get('url')) or _off(D['parks'].get('US-0703') or {}).get('url') != _off(D['parks'].get('US-3790') or {}).get('url')),
    ('US-10098', 'Green River NWR OFF (clean 9,500 vs ours)', lambda p, D: p.get('verdict') == 'off'),
    ('US-4689', 'Kentucky Ridge SF OFF (15,251 vs 11,736 = 23%)', lambda p, D: p.get('verdict') == 'off'),
    ('US-3800', 'Cedar Creek Lake WMA OFF (ours 2,390 vs 796)', lambda p, D: p.get('verdict') == 'off' and (p.get('ours') or {}).get('acres') == 2390 and _off(p).get('acres') == 796),
    ('US-0050', "Mammoth Cave OFF with cause 'boundary vs owned'", lambda p, D: p.get('verdict') == 'off' and 'boundary vs owned' in str(p.get('cause') or '')),
]


def area_test(area, D):
    """v8 generic gate for any area (chat 11's WV / VA / TN / IL grades): no 'off' row may use a number 3+ parks share, a mission /
    about / index page, or a part sentence; cross-state parks carry the whole-park note. Returns (PASS/FAIL, why)."""
    bad = []
    offs = [(ref, r) for ref, r in D['parks'].items() if r.get('verdict') == 'off' and r.get('official')]
    byn = {}
    for ref, r in offs: byn.setdefault((r['official']['acres'], r['official'].get('url')), []).append(ref)
    for k, refs in byn.items():
        if len(refs) >= 3: bad.append(f'{len(refs)} parks share {k[0]:,.0f} ac from {k[1][:60]}')
    for ref, r in offs:
        u = r['official'].get('url', '')
        if re.search(r'/mission|didyouknow|/wildlife-management-areas/?$|/state-forests/?$', u) or (SHARED.get(u, 0) >= 3): bad.append(f'{ref}: an agency-wide page {u[:60]}')
        ln = r['official'].get('line', '').lower(); mm = re.search(r'\d[\d,.]*\s*(?:million\s*)?[- ]?(?:acres?|hectares?)', ln)
        if mm and (HARD_PART.search(ln) or NEAR_PART.search(ln[max(0, mm.start() - 45):mm.end() + 45])): bad.append(f"{ref}: a part sentence: {r['official'].get('line', '')[:80]}")
    for ref, r in D['parks'].items():
        if len(REF_STATES.get(ref) or []) > 1 and r.get('verdict') == 'off' and not (r.get('ours') or {}).get('whole_park'): bad.append(f'{ref}: cross-state park compared one state only')
    res = 'PASS' if not bad else 'FAIL'
    return res, (f'{area}: {len(offs)} off rows, no shared numbers / agency pages / part sentences / one-state cross-state compares' if not bad else f'{area}: ' + ' · '.join(bad[:8]))


def ky_test(state):
    """The Kentucky gate: every KNOWN_ANSWERS row must pass (fix 8)."""
    D = load(OUT / 'US-KY.json', {'parks': {}})
    rows = []; ok_all = True
    for ref, what, check in KNOWN_ANSWERS:
        p = D['parks'].get(ref.split('+')[0]) or {}
        try: ok = bool(check(p, D))
        except Exception: ok = False  # noqa: BLE001
        ok_all = ok_all and ok
        rows.append(f"{ref} {'ok' if ok else 'MISS'} ({what}; verdict {p.get('verdict')}, agency {_off(p).get('as')})")
    why = ' · '.join(rows)
    res = 'PASS' if ok_all else 'FAIL'
    state['test'] = {'when': TODAY, 'result': res, 'why': why, 'rows': [{'ref': r.split(' ')[0], 'ok': ' ok ' in r} for r in rows]}
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
    import glob as _g
    for f in _g.glob('data/parkinfo/US-*.json') + _g.glob(str(LINKS / 'data/parkinfo/US-*.json')):
        a2 = 'US-' + f[-7:-5]
        for ref in (load(f, {}).get('parks') or {}): REF_STATES.setdefault(ref, [])
        for ref in (load(f, {}).get('parks') or {}):
            if a2 not in REF_STATES[ref]: REF_STATES[ref].append(a2)
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
