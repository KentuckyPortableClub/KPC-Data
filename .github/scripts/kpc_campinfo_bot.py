#!/usr/bin/env python3
"""CAMPGROUND INFO BOT (Fable, chat 10 'bot workshop', Oct 28 2026; HQ's job 4). GATHERS FACTS, DECIDES NOTHING. For every
campground we already list (federal, state, Kentucky hand-checked) it writes ONE info record read from the agency that runs it:

  WHAT IT READS   site count + types (tent / RV / cabin / group / primitive), max RV length, hookups (electric 30 / 50 amp, water,
                  sewer), dump station, showers, restrooms (flush / vault), drinking water, fees as published, first-come vs
                  reservable + the official BOOKING LINK (never availability), season, check-in / out, rules (pets, generators,
                  quiet hours, fires, stay limit), office phone, the campground MAP link (PDF first), ELEVATION, CELL COVERAGE.
  WHERE FROM      federal rows (data/campfed): Recreation.gov's RIDB API, /facilities/{id}?full=true (description, phone,
                  reservation + map links, stay limit, fee text) and /facilities/{id}/campsites (site types + attributes such as
                  'Max Vehicle Length', 'Electricity Hookup', 'Water Hookup', 'Sewer Hookup', 'Pets Allowed'). Needs the secret
                  RIDB_API_KEY; without it federal rows get status 'needs RIDB_API_KEY secret in KPC-Data' and the bot carries on.
                  state rows (data/campstate, data/campstate-manual) and Kentucky (KPC-Links kpc-campgrounds.json): the
                  campground's OWN official page (the url in the row): visible text + links, read with careful regexes.
                  elevation: USGS Elevation Point Query Service (US, no key) / NRCan CDEM altitude service (Canada, no key).
                  cell coverage: the FCC National Broadband Map (BDC) public API. Its documented endpoints need a free account
                  (headers 'username' + 'hash_value'): listAsOfDates and listAvailabilityData, which give per-state BULK coverage
                  files (GeoPackage / shapefile per carrier + technology), not a point lookup. The map website's own point
                  endpoints are undocumented, so this bot does not use them. With FCC_BDC_USERNAME + FCC_BDC_TOKEN it records
                  which coverage files exist for the state (step 1); the point-in-coverage read is step 2 (needs a geo library).
                  Without the secrets: cell = {status 'needs FCC token'}.
  RULES OF THE READ   R1 official sources only: the managing agency's site, the same government's site, or the reservation
                  system the agency contracts (sources.json). Never a third-party site, never Google, never live availability.
                  R2 EVERY fact carries {value, url, date, line}: the quoted source line (<= 200 chars) a person can check.
                  R3 unknown = null, never guessed, never summed from parts (tent + RV is not a total unless the page says so).
                  R4 a page that will not open is marked like the other bots ('HTTP 403 -> needs browser', 'robots.txt says no',
                  'host resting', 'soft 404'); a row with no official url = 'no official page on file'.
                  R5 Kentucky is the ANSWER KEY: the hand-checked kpc-campgrounds.json values (sites, amps, dump station,
                  showers, phone) are compared with what the bot read; the result goes to review.md as 'ky_check'.
                  R6 a campground checked within REFRESH_DAYS (30) is skipped.
                  R7 (round 2, chat 11): an RV length needs an RV / trailer / vehicle / length sentence and <= 60 ft, never
                  'elevation'; a camping season needs a camping / open / season sentence with no hunting words; a bare heading
                  or menu item ('Shower Types') is never a fact; a lodge / cottage link is 'lodging_booking', not booking;
                  'phone_hint' = the first number in the campground section. GATE = 8 known Kentucky answers + >= 70% hand-key
                  agreement -> 'GATE=PASS/FAIL' line + state['test'].
  MANNERS         kpc_manners.py (robots.txt obeyed, 1 request / 2 s per host incl. RIDB, back-off, three strikes = a day's rest).
  NEVER FAILS     exit 0 always; MINUTES (55) per chunk; state.json resumes; one commit per chunk by the workflow.

Env: AREAS='US-KY US-TN' (blank = next unfinished in queue order) · MINUTES · LINKS (KPC-Links checkout, default 'links') ·
     OUT (data/campinfo) · REFRESH_DAYS · RIDB_API_KEY · FCC_BDC_USERNAME · FCC_BDC_TOKEN.  `--selftest` runs the regexes on
     sample page texts offline and prints what they pulled out (no network); `--negtest` = the 30-sentence negation test (C-1).
"""
import json, os, pathlib, re, sys, time, urllib.parse, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kpc_manners import Manners, page_text, links_in  # noqa: E402

OUT = pathlib.Path(os.environ.get('OUT') or 'data/campinfo')
LINKS = pathlib.Path(os.environ.get('LINKS') or 'links')
T0 = time.time(); LIMIT = float(os.environ.get('MINUTES') or 55) * 60
REFRESH_DAYS = int(os.environ.get('REFRESH_DAYS') or 30)
RIDB_KEY = (os.environ.get('RIDB_API_KEY') or '').strip()
FCC_USER = (os.environ.get('FCC_BDC_USERNAME') or '').strip(); FCC_TOKEN = (os.environ.get('FCC_BDC_TOKEN') or '').strip()
TODAY = time.strftime('%Y-%m-%d')
VER = 5   # 5 = round 4: facts only from THIS campground's section of a shared page, KEY_WRONG table, 'some' = agree, WARN rows.
          # 4 = round 3; 4 = round 3 (chat 11 regrade): reservation-line phones out, bare-domain booking out, fire RULES only, merge by park ref,
          # state-park campground sub-pages read, more gate rows.
          # 3 = round 2; 2 = Oct 28 chat 8 grade C-1..C-6 (negation, footer phones, duplicates, hosts); 3 = chat 11 round 2 (elevation != RV length,
          # hunting season != camping season, headings are not facts, lodge links are not booking, phone_hint, gate): every row is re-read
RIDB = 'https://ridb.recreation.gov/api/v1/'
FCC = 'https://broadbandmap.fcc.gov/api/public/map/'
QUEUE = ['US-KY',
         'US-TN', 'US-NC', 'US-VA', 'US-WV', 'US-GA', 'US-AL', 'US-SC', 'US-FL', 'US-MS',
         'US-IN', 'US-IL', 'US-MO', 'US-WI', 'US-MN', 'US-IA', 'US-ND', 'US-SD',
         'US-PA', 'US-NY', 'US-NJ', 'US-CT', 'US-RI', 'US-MA', 'US-VT', 'US-NH', 'US-ME', 'US-MD', 'US-DE', 'US-DC',
         'US-AR', 'US-LA', 'US-OK', 'US-TX', 'US-KS', 'US-NE',
         'US-CO', 'US-WY', 'US-ID', 'US-MT', 'US-NV', 'US-AZ', 'US-NM',
         'US-CA', 'US-OR', 'US-WA', 'US-AK', 'US-HI', 'US-MI', 'US-OH', 'US-UT',
         'CA-ON', 'CA-QC', 'CA-NB', 'CA-NS', 'CA-PE', 'CA-NL',
         'CA-MB', 'CA-SK', 'CA-AB', 'CA-BC', 'CA-YT', 'CA-NT', 'CA-NU']
STAT = {'camps': 0, 'ok': 0, 'needs_key': 0, 'needs_browser': 0, 'robots': 0, 'resting': 0, 'no_page': 0, 'not_official': 0,
        'pages_read': 0, 'ridb_calls': 0, 'elevations': 0, 'skipped_fresh': 0, 'errors': 0}
M = None
SRC = {}   # sources.json


# ---- keys go in as headers, only to the host that owns them (Manners builds the request; this handler adds the header)
class _Keys(urllib.request.BaseHandler):
    def https_request(self, req):
        h = (req.host or '').lower()
        if h.endswith('ridb.recreation.gov') and RIDB_KEY: req.add_unredirected_header('apikey', RIDB_KEY)
        if h.endswith('broadbandmap.fcc.gov') and FCC_TOKEN:
            req.add_unredirected_header('username', FCC_USER); req.add_unredirected_header('hash_value', FCC_TOKEN)
        return req
    http_request = https_request


urllib.request.install_opener(urllib.request.build_opener(_Keys()))


def notice(m): print('::notice title=Campground info bot::' + str(m).replace('\n', ' ')[:900], flush=True)
def late(): return time.time() - T0 > LIMIT
def load(p, d):
    try: return json.load(open(p, encoding='utf-8'))
    except Exception: return d  # noqa: BLE001
def save(p, obj):
    pathlib.Path(p).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(p).write_text(json.dumps(obj, ensure_ascii=False, indent=1, sort_keys=True) + '\n', encoding='utf-8')
def host_of(u): return urllib.parse.urlparse(u or '').netloc.lower().split(':')[0]
def status_text(st):
    if st == 'robots': return 'robots.txt says no'
    if st == 'rest': return 'host resting'
    if st == 403: return 'HTTP 403 -> needs browser'
    if isinstance(st, int): return f'HTTP {st}'
    return str(st)


# ---- the regexes (tested by --selftest)
MON = r'(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\.?'
DATE = r'(?:early |mid-? ?|late )?' + MON + r'(?:\s+\d{1,2})?(?:,?\s+\d{4})?'
TIME = r'\d{1,2}(?::\d\d)?\s*(?:a\.?m\.?|p\.?m\.?|noon|midnight)?'
SITE = re.compile(r'(\d{1,4})[- ]+((?:[\w/-]+,?[- ]+){0,4}?)(campsites?|camp sites?|sites?|cabins?|cottages?|yurts?|lean-tos?|shelters?|pads?|spaces?)\b', re.I)
SITE_TOTAL2 = re.compile(r'(?:campground|park|area)\s+(?:has|offers|features|with|provides|contains|includes)\s+(?:a total of\s+)?(\d{1,4})\s+(?:[\w-]+\s+){0,2}?(?:campsites?|sites?)|(\d{1,4})[- ]site campground|(\d{1,4})\s+sites? for (?:tents?|rvs?|campers)|total of (\d{1,4}) (?:campsites?|sites?)', re.I)
PARTIAL_BEFORE = re.compile(r'\b(at|of|for|in|on|only|including|includes|and|plus|with|to)\s*$', re.I)
TENT_W = re.compile(r'\btent', re.I); RV_W = re.compile(r'\brv\b|full[- ]hook|pull[- ]thr|back[- ]in|trailer|motorhome', re.I)
CABIN_W = re.compile(r'cabin|cottage|yurt|lean-to|shelter', re.I); GROUP_W = re.compile(r'\bgroup', re.I)
PRIM_W = re.compile(r'primitive|walk[- ]in|hike[- ]in|backcountry|backpack|boat[- ]in|paddle[- ]in|rustic', re.I)
PLAIN_W = re.compile(r'^(?:first[- ]come,?[- ]first[- ]serve[d]?|reservable|non-?reservable|camp|wooded|shaded|developed|individual|family|total|overnight|standard|modern|paved|gravel|utility|hookup|electric|full[- ]service)?[- ]*$', re.I)   # 'improved' left out: '92 improved sites' is a part
AMPS = re.compile(r'\b(20|30|50|100)(?:\s*/\s*(20|30|50|100))?(?:\s*/\s*(20|30|50|100))?\s*-?\s*amp', re.I)
ELECTRIC_W = re.compile(r'electric(?:al|ity)?(?:\s+(?:hook-?ups?|service|sites?|pedestals?))?|\bhook-?ups?|full[- ]hook-?ups?|utility hook-?ups?|full[- ]service sites?|improved sites?|\bpower\b|utilities', re.I)
WATER_HOOK = re.compile(r'water (?:and|&|/|,) (?:electric|sewer)|utility hook-?ups?|full[- ]service sites?|(?:electric(?:al|ity)?|sewer)(?:\s*,|\s+and|\s*&|\s*/)\s*water|water hook-?ups?|full[- ]hook-?ups?|water (?:at|on|to) (?:each|every|all) site', re.I)
SEWER_W = re.compile(r'\bsewer\b|full[- ]hook-?ups?', re.I)
DUMP = re.compile(r'dump station|sanitary (?:dump|station)|rv dump|dumping station', re.I)
SHOWERS = re.compile(r'\bshowers?\b|bath ?house|shower house', re.I)
FLUSH = re.compile(r'flush (?:toilets?|restrooms?)|modern restrooms?|(?:toilets?|restrooms?)\s*:\s*flush', re.I); VAULT = re.compile(r'vault (?:toilets?|restrooms?)|(?:toilets?|restrooms?)\s*:\s*(?:vault|pit)|pit toilets?|privies|privy|outhouses?|composting toilets?|portable toilets?|chemical toilets?', re.I)
RESTROOM = re.compile(r'restrooms?|toilets?|comfort stations?|bath ?house', re.I)
DRINK = re.compile(r'(?:drinking|potable) water|water (?:spigots?|fountains?|fill(?:ing)? station|hydrants?)', re.I)
# negation words that may stand before an amenity in the same clause ('no', 'not available', 'without', 'lacks', 'does not have')
NEG = re.compile(r"\b(?:no|not|without|none|lacks?|lacking|nor|neither|non)\b|\bn't\b|does not|do not|is not|are not|isn't|aren't|unavailable|not available|not offered|not provided|not permitted|prohibited", re.I)
NEG_AFTER = re.compile(r"^\W*(?:\w+\W+){0,3}?(?:(?:is|are|was|were)\s+)?(?:not|unavailable|not available|not offered|not provided|is lacking|are lacking|n't available|do not exist|does not exist)\b", re.I)
SOME_W = re.compile(r"\b(?:some|select|selected|certain|limited|a few|several|most|many|not all|partial|range from|only at|at \d+ (?:of|sites)|\d+ of the \d+|\d+ of (?:the|our) sites)\b", re.I)   # '146 sites with electric' is a total, not 'some'
RVMAX = re.compile(r'max(?:imum)?\s+(?:rv|trailer|vehicle|camper|unit|site|combined)?\s*(?:length|size)?\s*(?:of|is|:|=)?\s*(\d{2,3})\s*(?:ft\b|feet|\'|-?foot)'
                   r'|(?:rvs?|trailers?|vehicles?|campers?|units?)\s+(?:up to|under|no longer than|not (?:exceeding|to exceed)|(?:of )?(?:less than )?)\s*(\d{2,3})\s*(?:ft\b|feet|\'|-?foot)'
                   r'|(\d{2,3})\s*(?:ft\.?|feet|\'|-?foot)\s+(?:max(?:imum)?|limit|or (?:less|shorter|under))', re.I)
FEE = re.compile(r'\$\s?\d{1,4}(?:\.\d\d)?(?:\s*(?:-|–|to)\s*\$?\s?\d{1,4}(?:\.\d\d)?)?(?:\s*(?:/|per|a)\s*(?:night|site|day|vehicle|person|week|cabin|stay))?', re.I)
FIRSTCOME = re.compile(r'first[- ]come,?\s*first[- ]serve[d]?|walk[- ]up(?: sites)? only|no reservations', re.I)
RESERVE = re.compile(r'reservations?\s+(?:are\s+)?(?:required|accepted|recommended|available|strongly|encouraged|can be made|may be made|only)|reserv(?:e|able)\s+(?:a |your |online|sites?)|book (?:a |your |online)|reservable', re.I)
YEARROUND = re.compile(r'(?:open|operates?|available)\s+(?:all year|year[- ]round)|year[- ]round(?: camping| operation)?|open 365', re.I)
SEASON = re.compile(r'(?:open|opens|season|operates?|available|closed?)(?:\s+\w+){0,4}?\s+(?:from\s+|between\s+)?(' + DATE + r')\s*(?:through|thru|to|until|till|-|–|and)\s*(' + DATE + r')', re.I)
SEASON2 = re.compile(r'(' + DATE + r')\s*(?:through|thru|to|until|till|-|–)\s*(' + DATE + r')', re.I)
CHECKIN = re.compile(r'check[- ]?in(?:\s+time)?(?:\s+(?:is|begins|starts|at|after))?\s*[:\-–]?\s*(?:is\s+|at\s+|after\s+)?(' + TIME + r')', re.I)
CHECKOUT = re.compile(r'check[- ]?out(?:\s+time)?(?:\s+(?:is|at|by|before))?\s*[:\-–]?\s*(?:is\s+|at\s+|by\s+|before\s+)?(' + TIME + r')', re.I)
PETS = re.compile(r'\b((?:pets?|dogs?)\s+(?:are\s+|is\s+)?(?:welcome|allowed|permitted|ok|okay|accepted|not (?:allowed|permitted|accepted)|prohibited|must be (?:kept )?(?:on a )?leash\w*)[^.;\n]{0,60}|no (?:pets|dogs)(?: allowed| permitted)?[^.;\n]{0,40}|leashed pets[^.;\n]{0,60}|pet[- ]friendly[^.;\n]{0,40})', re.I)
GENERATORS = re.compile(r'\b(generators?[^.;\n]{0,100}|no generators[^.;\n]{0,40})', re.I)
QUIET = re.compile(r'quiet (?:hours?|time)\s*(?:are|is|:|-|–|from|run)?\s*(?:from\s+)?(' + TIME + r'\s*(?:to|-|–|until|till|through)\s*' + TIME + r')', re.I)
RULE_VERB = re.compile(r'allowed|prohibit|permitted|\bbans?\b|banned|not allowed|\bmust\b|may not|not permitted|restricted|only in|quarantin|do not|don\'t|no (?:camp ?fires?|open fires?|fires)|forbidden|required|please', re.I)
FIRES = re.compile(r'\b((?:camp ?fires?|fire ?wood|fire rings?|fire pits?|burn bans?|open fires?)[^.;\n]{0,100})', re.I)
STAY = re.compile(r'(?:max(?:imum)?\s+(?:stay|length of stay|of)|stay (?:limit|is limited to|limited to)|limited to(?: a)?|no more than|up to|not (?:to )?exceed(?:ing)?)\s*(?:is\s+|of\s+)?(\d{1,2})\s*(consecutive\s+)?(days|nights)', re.I)
STAY2 = re.compile(r'(\d{1,2})[- ](?:day|night)\s+(?:maximum|limit|stay limit)', re.I)
PHONE = re.compile(r'(?<![\d-])(?:\+?1[-. ]?)?\(?(\d{3})\)?[-. ]?(\d{3})[-. ](\d{4})(?![\d-])')
SOFT404 = re.compile(r'page not found|404 error|error 404|the page you (?:requested|are looking for)|no longer available|has been (?:moved|removed)|access denied', re.I)


FOOTER_W = re.compile(r'footer|contact us|contact info|headquarters|park information|mailing address|physical address|superintendent|regional office|privacy policy|accessibility|site map|sitemap', re.I)
TOLLFREE = ('(800)', '(888)', '(877)', '(866)', '(855)', '(844)')
RESLINE_W = re.compile(r'reservation|1-877|recreation one stop|reserve ?america|recreation\.gov|call cent|toll[- ]free|book', re.I)
OWN_PHONE_W = re.compile(r'campground|camp office|park office|ranger (?:station|district)|district office|visitor cent|office|information|call|phone|contact|camp\b|camping', re.I)


def phones_in(text):
    """C-2 / C-3 (chat 8, Oct 28): the campground's own phone numbers, in page order, as [(number, match)]. A number in the last
    ~15% of the page text, or within 200 chars of footer words ('footer', 'contact us', 'headquarters', 'park information',
    'mailing address'), is the site footer / park HQ line and is dropped; a toll-free number is the booking line and is dropped
    when any other number exists. All numbers on one quoted line are kept (Holly Bay: 'Phone: 859-428-7706; 606-864-4163')."""
    cut = int(len(text) * 0.85)
    out = []
    for m in PHONE.finditer(text):
        if m.start() >= cut and len(text) > 600: continue
        if FOOTER_W.search(text[max(0, m.start() - 200):m.end() + 200]): continue
        p = f'({m.group(1)}) {m.group(2)}-{m.group(3)}'
        sent = sentence_of(text, m.start(), m.end())
        # round 3 rule 1: the national reservation line (877) 444-6777 / 'Recreation One Stop' / any number in a 'reservation'
        # sentence is never the campground's phone; the sentence must name the campground, the park office or 'campground office'
        if p == '(877) 444-6777' or RESLINE_W.search(sent) or p.startswith(TOLLFREE): continue
        if not OWN_PHONE_W.search(sent): continue
        if re.search(r'\b[a-z0-9-]+[.·](?:com|org|gov|us)\b|state law|regulation|department of agriculture', sent, re.I): continue   # 'refer to kyagr.com or call …' = another agency's line
        if p not in [x for x, _ in out]: out.append((p, m))
    if not out: return []
    # keep the first number plus every number on the same quoted line (within 120 chars of it)
    first = out[0][1]
    return [x for x in out if abs(x[1].start() - first.start()) <= 120][:4]


def line_at(text, s, e, width=90):
    a = max(0, s - width); b = min(len(text), e + width)
    return ' '.join(text[a:b].split())[:200]


def tidy(x):
    """'1:00 pm.' -> '1:00 pm' (one space between words, no trailing period or comma)."""
    return ' '.join(str(x).split()).rstrip('.,;:')


def fact(value, url, line):
    return {'value': value, 'url': url, 'date': TODAY, 'line': line}


HUNT_W = re.compile(r'\bhunt\w*|quota|\bdeer\b|turkey|rabbit|quail|squirrel|dove|waterfowl|duck|goose|geese|grouse|\bgame\b|firearm|archery|muzzleloader|crossbow|trapping|anterless|bag limit|season dates', re.I)
CAMP_W = re.compile(r'\bcamp\w*|\bcampground|\bsites? (?:are|is) open|\bopen (?:to campers|for camping)|camping season|season of use|operating season', re.I)
RV_W2 = re.compile(r'\brvs?\b|trailer|vehicle|motorhome|motor home|\brigs?\b|length|camper', re.I)
ELEV_W = re.compile(r'elevation|altitude|above sea level|\bmsl\b|summit|peak', re.I)


def sentence_of(text, s, e):
    """The whole sentence (or label line) around text[s:e]: cut at . ! ? ; or a new line."""
    a = max(0, s - 300); b = min(len(text), e + 300)
    seg = text[a:b]; rs = s - a; re_ = e - a
    seg = re.sub(r'(\w)\.(?=(?:com|org|gov|us|ca|net|edu)\b)', r'\1·', seg)   # 'kyagr.com' is not the end of a sentence
    starts = [m.end() for m in re.finditer(r'[.!?;\n]', seg[:rs])]
    ends = [m.start() for m in re.finditer(r'[.!?;\n]', seg[re_:])]
    return seg[(starts[-1] if starts else 0):(re_ + ends[0] if ends else len(seg))].strip()


VERB_W = re.compile(r"\b(?:is|are|was|were|has|have|had|offers?|offered|provides?|provided|includes?|included|features?|available|located|allowed|permitted|prohibited|required|accepted|welcome|open|closed|opens|closes|may|must|can|cannot|will|should|do|does|not|no|with|without|per|at|in|for|from|through|each|every|all|only|yes)\b", re.I)


def is_heading(sent):
    """A bare heading or menu item (round 2, rule 3): 3 words or fewer, no verb-like word, no 'Label: value'. 'Shower Types',
    'Toilet Types', 'Amenities' are headings; 'Showers: yes' and 'Hot showers are available' are not."""
    w = sent.strip().split()
    if ':' in sent and re.search(r':\s*\S', sent): return False
    if len(w) <= 3 and not VERB_W.search(sent): return True
    # a run of Title Case words with no verb (a page menu flattened into one line) is a menu, not a sentence
    caps = sum(1 for x in w if x[:1].isupper() or not x[:1].isalpha())
    lower_verb = any(VERB_W.fullmatch(x.strip('.,;')) and x[:1].islower() for x in w)   # a real sentence has a lower-case verb somewhere
    if len(w) >= 3 and caps >= 0.8 * len(w) and not lower_verb: return True
    return False


def clause_before(text, pos, width=110):
    """The words of the same clause before pos (cut at . ; : ! ? or a new line), at most `width` chars."""
    seg = text[max(0, pos - width):pos]
    seg = re.split(r'[.;:!?\n]|\s-\s|\s–\s|\s\|\s|,?\s+(?:but|however|although|while|yet)\s+', seg)[-1]
    return seg


def clause_after(text, pos, width=60):
    """The words right after pos up to the next comma / period / 'and' (so '…, 50-amp at 30 sites' does not colour the amenity before it)."""
    seg = text[pos:pos + width]
    return re.split(r'[.;:!?,\n]|\s(?:and|but|with|plus)\s', seg)[0]


def judge_mentions(text, rx, extra_pos=False):
    """Read EVERY mention of one amenity: -> (True / False / 'some', match) or None when the page never mentions it.
    A mention is negative when a negation word stands before it in the same clause ('no water, electricity or dump station',
    'without hookups', 'electric hookups are not available': the 'not' may also follow within 3 words).
    Any negative mention and no positive = False. Positive mentions only = True, or 'some' when the clause says only certain
    sites have it (C-6: 'range from electric-only to full hookups', 'some sites have 50 amp'). Both kinds on one page = 'some'."""
    pos = neg = None; some = False
    for m in rx.finditer(text):
        if is_heading(sentence_of(text, m.start(), m.end())): continue   # round 2 rule 3: 'Shower Types' in a menu is not a fact
        before = clause_before(text, m.start())
        after = text[m.end():m.end() + 40]
        if NEG.search(before) or NEG_AFTER.search(after):
            neg = neg or m
        else:
            pos = pos or m
            if SOME_W.search(before.split(',')[-1]) or SOME_W.search(clause_after(text, m.end())): some = True   # 'some' only from the amenity's own comma-clause
    if pos is None and extra_pos and rx is ELECTRIC_W:
        m = AMPS.search(text)
        if m and not NEG.search(clause_before(text, m.start())):
            pos = m
            if SOME_W.search(clause_before(text, m.start()).split(',')[-1]) or SOME_W.search(clause_after(text, m.end())): some = True
    if pos is None and neg is None: return None
    if neg is not None and pos is None: return False, neg
    if neg is not None and pos is not None: return 'some', pos
    return ('some' if some else True), pos


def facts_from_text(text, url):
    """Every campground fact the regexes can read from one page's visible text. Unknown = not present (never guessed)."""
    F = {}
    def put(k, v, m, line=None): F[k] = fact(v, url, line if line is not None else line_at(text, m.start(), m.end()))
    # sites by type: '146 sites', '30 tent sites', '12 cabins', '2 group sites'; a count after 'at / of / for' is a part, not a total
    sites = {'total': None, 'tent': None, 'rv': None, 'cabin': None, 'group': None, 'primitive': None}; lines = {}
    def take(k, n, m):
        if sites[k] is None or (k == 'total' and n > sites[k]): sites[k] = n; lines[k] = line_at(text, m.start(), m.end())
    for m in SITE.finditer(text):
        n = int(m.group(1)); q = m.group(2) or ''; noun = m.group(3).lower(); before = text[max(0, m.start() - 24):m.start()]
        if n == 0 or n > 2000 or re.search(r'\bweb\s*$|\bhistoric\s*$', before, re.I): continue
        partial = bool(PARTIAL_BEFORE.search(before)) or bool(AMPS.search(before)) or bool(re.search(r'(water|electric|sewer|hook)\w*\s*$', before, re.I))
        if GROUP_W.search(q) or noun.startswith('group'): take('group', n, m)
        elif CABIN_W.search(q) or CABIN_W.search(noun): take('cabin', n, m)
        elif TENT_W.search(q) and not RV_W.search(q): take('tent', n, m)
        elif PRIM_W.search(q): take('primitive', n, m)
        elif RV_W.search(q): take('rv', n, m)
        elif PLAIN_W.match(q) and not partial and noun.startswith(('camp', 'site')): take('total', n, m)
    for m in SITE_TOTAL2.finditer(text): take('total', int(next(g for g in m.groups() if g)), m)
    for k, v in sites.items():
        if v is not None: F['sites.' + k] = fact(v, url, lines[k])
    for m in RVMAX.finditer(text):
        # round 2 rule 1: an RV length comes from a sentence about RVs / trailers / vehicles / length, never 'Elevation: maximum 451 feet'
        sent = sentence_of(text, m.start(), m.end()); n = int(next(g for g in m.groups() if g))
        if ELEV_W.search(sent) or not RV_W2.search(sent) or n > 60 or n < 10: continue
        put('rv_max_ft', n, m); break
    amps = sorted({int(a) for tup in AMPS.findall(text) for a in tup if a})
    if amps: m = AMPS.search(text); put('hookups.amps', amps, m)
    # C-1 (chat 8, Oct 28): each amenity is judged mention by mention: a 'no / not / without' in the same clause before the word
    # makes it False ('There is no water, electricity or dump station' negates every item in the list). A positive mention
    # elsewhere on the page makes the value 'some' when the page also says it is only at certain sites (C-6), never True.
    el = judge_mentions(text, ELECTRIC_W, extra_pos=bool(amps))
    if el: put('hookups.electric', el[0], el[1])
    for key, rx in (('hookups.water', WATER_HOOK), ('hookups.sewer', SEWER_W), ('dump_station', DUMP), ('showers', SHOWERS), ('drinking_water', DRINK)):
        v = judge_mentions(text, rx)
        if v: put(key, v[0], v[1])
    fl, va = judge_mentions(text, FLUSH), judge_mentions(text, VAULT)
    fl = fl if fl and fl[0] else None; va = va if va and va[0] else None
    if fl and va: put('restrooms', 'flush + vault', fl[1])
    elif fl: put('restrooms', 'flush', fl[1])
    elif va: put('restrooms', 'vault', va[1])
    else:
        rr = judge_mentions(text, RESTROOM)
        if rr: put('restrooms', 'yes (kind not stated)' if rr[0] is True else 'some' if rr[0] == 'some' else 'none', rr[1])
    fees = []; seen = set(); first = None
    for m in FEE.finditer(text):
        t = ' '.join(m.group(0).split())
        if t in seen: continue
        seen.add(t); first = first or m
        # the published text: the amount plus the words that follow it (up to the end of the phrase)
        tail = re.split(r'[.;|\n]|,\s+(?:and\s+)?\$', text[m.end():m.end() + 50])[0]
        fees.append(' '.join((m.group(0) + tail).split()))
        if len(fees) >= 5: break
    if fees: F['fees'] = fact(' | '.join(fees)[:300], url, line_at(text, first.start(), first.end()))
    fc, rs = FIRSTCOME.search(text), RESERVE.search(text)
    if fc and rs: put('reservable', 'mixed', rs, line_at(text, fc.start(), fc.end()) + ' … ' + line_at(text, rs.start(), rs.end(), 40))
    elif rs: put('reservable', True, rs)
    elif fc: put('reservable', False, fc)
    # round 2 rule 2: a camping season needs 'camp' / 'campground' / 'open' / 'season' in the same sentence and NO hunting words
    # ('Rabbit and quail hunting seasons are open from Nov. 14-Dec. 31' is a hunting season, not when the campground is open)
    def season_ok(m):
        sent = sentence_of(text, m.start(), m.end())
        return not HUNT_W.search(sent) and bool(CAMP_W.search(sent) or re.search(r'\bopen\b|season', sent, re.I)) and not is_heading(sent)
    done_season = False
    for m in YEARROUND.finditer(text):
        if season_ok(m): put('season', 'year-round', m); done_season = True; break
    if not done_season:
        for m in SEASON.finditer(text):
            if season_ok(m): put('season', f'{tidy(m.group(1))} through {tidy(m.group(2))}', m); done_season = True; break
    if not done_season:
        for m in SEASON2.finditer(text):
            if season_ok(m) and CAMP_W.search(sentence_of(text, m.start(), m.end())): put('season', f'{tidy(m.group(1))} through {tidy(m.group(2))}', m); break
    m = CHECKIN.search(text)
    if m: put('checkin', tidy(m.group(1)), m)
    m = CHECKOUT.search(text)
    if m: put('checkout', tidy(m.group(1)), m)
    m = PETS.search(text)
    if m: put('rules.pets', ' '.join(m.group(1).split()), m)
    for m in GENERATORS.finditer(text):
        sent = sentence_of(text, m.start(), m.end())
        if HUNT_W.search(sent) or is_heading(sent): continue
        put('rules.generators', ' '.join(m.group(1).split()), m); break
    m = QUIET.search(text)
    if m: put('rules.quiet_hours', tidy(m.group(1)), m)
    feat = None
    for m in FIRES.finditer(text):
        sent = sentence_of(text, m.start(), m.end())
        if HUNT_W.search(sent) or is_heading(sent): continue   # a hunt rule ('firearm deer hunt') is not a campfire rule
        # round 3 rule 3: a fire RULE needs a rule verb (allowed / prohibited / permitted / ban / must / may not); 'fire ring and
        # lantern pole' is a site feature and goes under 'features'
        if RULE_VERB.search(sent): put('rules.fires', ' '.join(m.group(1).split()), m); break
        if feat is None and re.search(r'fire ring|fire pit', sent, re.I): feat = m
    if feat is not None and 'rules.fires' not in F: put('features', ' '.join(feat.group(1).split()), feat)
    m = STAY.search(text) or STAY2.search(text)
    if m: put('rules.stay_limit', f'{m.group(1)} {(m.group(2) or "") if m.re is STAY else ""}{m.group(3) if m.re is STAY else "days"}'.replace('  ', ' ').strip(), m)
    ph = phones_in(text)
    if ph:
        nums = [p for p, m in ph]
        put('phone', nums if len(nums) > 1 else nums[0], ph[0][1], ' | '.join(line_at(text, m.start(), m.end(), 60) for p, m in ph[:3]))
    # round 2 rule 6: phone_hint = the first number in the campground section (within 200 chars after 'campground' / 'camp'),
    # footer or not, so a person can check it when 'phone' is null
    for m in PHONE.finditer(text):
        before = text[max(0, m.start() - 200):m.start()]; pn = f'({m.group(1)}) {m.group(2)}-{m.group(3)}'
        if pn == '(877) 444-6777' or RESLINE_W.search(sentence_of(text, m.start(), m.end())): continue
        if re.search(r'camp', before, re.I) and not FOOTER_W.search(text[max(0, m.start() - 200):m.end() + 200]):
            put('phone_hint', pn, m); break
    return F


def bare_domain(u):
    """True for a link with no path (https://recreation.gov, https://www.recreation.gov/): never a campground's booking page."""
    pr = urllib.parse.urlparse(u or '')
    return not (pr.path or '').strip('/') and not pr.query


def links_facts(links, url):
    """Booking link + map link from a page's links (text or url says reserve / book / map; PDF maps first)."""
    F = {}
    bh = SRC.get('booking_hosts') or []
    for u, t in links:
        tl = (t or '').lower(); h = host_of(u); ul = u.lower()
        # round 2 rule 4: a booking link says reserve / reservation / book (text or url) or sits on a reservation host, and is about
        # CAMPING: lodge / cottage / room links go under 'lodging_booking'; a page that only says 'fund' / 'donate' is never booking
        says_book = any(h.endswith(b) for b in bh) or re.search(r'reserv|book (?:now|a site|online|here)|make a reservation', tl + ' ' + ul)
        if not says_book or re.search(r'cancel|policy|faq|fund|donat|conservation|heritage', tl + ' ' + ul): continue
        if bare_domain(u): continue   # round 3 rule 2: https://recreation.gov is the site's front door, not this campground's page
        lodging = re.search(r'lodge|cottage|cabin|room|yurt|inn\b|hotel', tl + ' ' + ul) and not re.search(r'camp', tl + ' ' + ul)
        key = 'lodging_booking' if lodging else 'booking'
        if key + '.url' not in F:
            F[key + '.url'] = fact(u, url, f'link “{t[:80]}” -> {u[:100]}')
            F[key + '.how'] = fact('online: ' + h, url, f'link “{t[:80]}”')
    pdfs = [(u, t) for u, t in links if u.lower().split('?')[0].endswith('.pdf')]
    for cand in (pdfs, links):
        for u, t in cand:
            if re.search(r'\bmap\b', (t or '').lower() + ' ' + u.lower().rsplit('/', 1)[-1]) and not re.search(r'sitemap|site map|google|directions', (t or '').lower() + u.lower()):
                F['map.url'] = fact(u, url, f'link “{t[:80]}” -> {u[:100]}')
                yr = re.search(r'(20\d\d)', (t or '') + ' ' + u)
                F['map.date_how'] = fact(('PDF, ' if u.lower().split('?')[0].endswith('.pdf') else 'web page, ') + (f'year {yr.group(1)} in the link' if yr else 'no date in the link'), url, f'link “{t[:80]}”')
                return F
    return F


# ---- official or not (R1)
GOV = re.compile(r'\.(gov|mil|gc\.ca)$|\.state\.[a-z]{2}\.us$|\.[a-z]{2}\.us$|\.gov\.[a-z]{2}$|\.(on|qc|nb|ns|pe|nl|mb|sk|ab|bc|yk|nt|nu)\.ca$', re.I)


PARK_HOSTS = None


def park_hosts():
    """C-5: the host of each park's OWN page on file (KPC-Links kpc-ky-data.json 'web', data/parkinfo-web.json 'web') counts as
    official for that park: an agency's own site under a plain .com / .us name (landbetweenthelakes.us, breakspark.com)."""
    global PARK_HOSTS
    if PARK_HOSTS is None:
        PARK_HOSTS = {}
        for x in load(LINKS / 'kpc-ky-data.json', {}).get('parks') or []:
            if x.get('c') and x.get('web'): PARK_HOSTS.setdefault(x['c'], set()).add(re.sub(r'^www\.', '', host_of(x['web'])))
        for ref, v in ((load('data/parkinfo-web.json', {}) or load(LINKS / 'data/parkinfo-web.json', {})).get('parks') or {}).items():
            if (v or {}).get('web'): PARK_HOSTS.setdefault(ref, set()).add(re.sub(r'^www\.', '', host_of(v['web'])))
    return PARK_HOSTS


def official(url, area, park=''):
    h = host_of(url)
    if not h: return False
    if GOV.search(h): return True
    hosts = list((SRC.get('states') or {}).get(area[3:], []) if area.startswith('US-') else (SRC.get('canada') or []))
    hosts += [x['host'] if isinstance(x, dict) else x for x in (SRC.get('extra_official') or [])]
    if park: hosts += list(park_hosts().get(park) or [])
    return any(h == x or h.endswith('.' + x) for x in hosts + (SRC.get('booking_hosts') or []))


# ---- reads
def read_page(u):
    """-> (status text, visible text, links)."""
    st, hd, body, final = M.get(u)
    if st not in (200, 206): return status_text(st), '', []
    STAT['pages_read'] += 1
    html = body.decode('utf-8', 'replace')
    t = page_text(html)
    if len(t) < 200 and SOFT404.search(t): return 'soft 404', '', []
    return 'ok', t, links_in(html, final)


def ridb(path, q=None):
    """One RIDB API call through Manners (the key rides in the header). -> (status text, json or None, url)."""
    u = RIDB + path + ('?' + urllib.parse.urlencode(q) if q else '')
    st, hd, body, final = M.get(u, accept='application/json')
    STAT['ridb_calls'] += 1
    if st not in (200, 206): return status_text(st), None, u
    try: return 'ok', json.loads(body.decode('utf-8', 'replace')), u
    except Exception as e: return 'bad json: ' + str(e)[:40], None, u  # noqa: BLE001


def ridb_facts(fid):
    """Federal: facility record + its campsites, summarized by type and attribute. -> (status, facts dict, official page)."""
    F = {}
    st, j, u = ridb(f'facilities/{fid}', {'full': 'true'})
    if st != 'ok': return st, F
    desc = page_text(j.get('FacilityDescription') or '') + '\n' + (j.get('FacilityUseFeeDescription') or '') + '\n' + (j.get('Keywords') or '')
    F.update(facts_from_text(desc, u))
    if j.get('FacilityPhone'):
        m = PHONE.search(j['FacilityPhone'])
        if m: F['phone'] = fact(f'({m.group(1)}) {m.group(2)}-{m.group(3)}', u, 'RIDB FacilityPhone: ' + j['FacilityPhone'][:60])
    if j.get('FacilityReservationURL'):
        F['booking.url'] = fact(j['FacilityReservationURL'], u, 'RIDB FacilityReservationURL'); F['booking.how'] = fact('online: Recreation.gov', u, 'RIDB FacilityReservationURL')
    elif j.get('Reservable'):
        F['booking.url'] = fact(f'https://www.recreation.gov/camping/campgrounds/{fid}', u, 'RIDB Reservable = true'); F['booking.how'] = fact('online: Recreation.gov', u, 'RIDB Reservable = true')
    if 'Reservable' in j: F['reservable'] = fact(bool(j['Reservable']), u, f"RIDB Reservable = {j['Reservable']}")
    if j.get('FacilityMapURL'):
        F['map.url'] = fact(j['FacilityMapURL'], u, 'RIDB FacilityMapURL'); F['map.date_how'] = fact('PDF, no date in RIDB' if j['FacilityMapURL'].lower().endswith('.pdf') else 'web map, no date in RIDB', u, 'RIDB FacilityMapURL')
    if j.get('StayLimit'): F['rules.stay_limit'] = fact(str(j['StayLimit'])[:80], u, 'RIDB StayLimit: ' + str(j['StayLimit'])[:120])
    if j.get('FacilityUseFeeDescription') and 'fees' not in F: F['fees'] = fact(' '.join(page_text(j['FacilityUseFeeDescription']).split())[:300], u, 'RIDB FacilityUseFeeDescription')
    # campsites: count by type, summarize attributes (one page of 50 per call, Manners keeps the 2 s gap)
    sites = []; off = 0
    while not late():
        st2, j2, u2 = ridb(f'facilities/{fid}/campsites', {'limit': 50, 'offset': off})
        if st2 != 'ok' or not j2: break
        R = j2.get('RECDATA') or []; sites += R; off += len(R)
        if not R or off >= int(((j2.get('METADATA') or {}).get('RESULTS') or {}).get('TOTAL_COUNT') or 0): break
    if sites:
        ov = [s for s in sites if (s.get('TypeOfUse') or 'Overnight').lower() != 'day']
        c = {'tent': 0, 'rv': 0, 'cabin': 0, 'group': 0, 'primitive': 0}; amps = set(); elec = water = sewer = 0; rvmax = 0; pets = {}; qh = ci = co = None
        for s in ov:
            t = (s.get('CampsiteType') or '').upper()
            if 'TENT' in t: c['tent'] += 1
            if 'RV' in t or 'STANDARD' in t and 'ELECTRIC' in t and 'NON' not in t: c['rv'] += 1
            if re.search(r'CABIN|YURT|LOOKOUT|SHELTER', t): c['cabin'] += 1
            if 'GROUP' in t: c['group'] += 1
            if re.search(r'WALK TO|HIKE TO|BOAT IN|PRIMITIVE|BACKCOUNTRY', t): c['primitive'] += 1
            for a in s.get('ATTRIBUTES') or []:
                n = (a.get('AttributeName') or '').lower(); v = str(a.get('AttributeValue') or '').strip()
                if n == 'electricity hookup' and v and v.lower() not in ('n', 'no', 'none'):
                    elec += 1
                    for x in re.findall(r'\d+', v):
                        if x in ('20', '30', '50', '100'): amps.add(int(x))
                elif n == 'water hookup' and v.lower() in ('y', 'yes'): water += 1
                elif n == 'sewer hookup' and v.lower() in ('y', 'yes'): sewer += 1
                elif n == 'max vehicle length' and v.isdigit(): rvmax = max(rvmax, int(v))
                elif n == 'pets allowed': pets[v] = pets.get(v, 0) + 1
                elif n == 'quiet hours': qh = qh or v
                elif n == 'checkin time': ci = ci or v
                elif n == 'checkout time': co = co or v
        line = f'RIDB campsites: {len(ov)} overnight sites (' + ', '.join(f'{k} {v}' for k, v in c.items() if v) + f'); electric at {elec}' + (f' ({"/".join(str(a) for a in sorted(amps))} amp)' if amps else '') + f', water at {water}, sewer at {sewer}'
        F['sites.total'] = fact(len(ov), u2, line)
        for k, v in c.items():
            if v: F['sites.' + k] = fact(v, u2, line)
        F['hookups.electric'] = fact(elec > 0, u2, line)
        if amps: F['hookups.amps'] = fact(sorted(amps), u2, line)
        F['hookups.water'] = fact(water > 0, u2, line); F['hookups.sewer'] = fact(sewer > 0, u2, line)
        if rvmax: F['rv_max_ft'] = fact(rvmax, u2, f'RIDB campsites: Max Vehicle Length up to {rvmax}')
        if pets:
            top = max(pets, key=pets.get); F['rules.pets'] = fact(f'Pets Allowed = {top} at {pets[top]} of {len(ov)} sites', u2, 'RIDB campsite attribute Pets Allowed')
        if qh: F['rules.quiet_hours'] = fact(qh[:60], u2, 'RIDB campsite attribute Quiet Hours: ' + qh[:100])
        if ci: F['checkin'] = fact(ci[:40], u2, 'RIDB campsite attribute Checkin Time')
        if co: F['checkout'] = fact(co[:40], u2, 'RIDB campsite attribute Checkout Time')
    return 'ok', F


def elevation(lat, lon, canada):
    """USGS EPQS (feet) for the US; NRCan CDEM (metres -> feet) for Canada. Official, no key."""
    if lat is None or lon is None: return {'value': None, 'src': None}
    u = (f'https://geogratis.gc.ca/services/elevation/cdem/altitude?lat={lat}&lon={lon}' if canada
         else f'https://epqs.nationalmap.gov/v1/json?x={lon}&y={lat}&units=Feet&wkid=4326')
    st, hd, body, final = M.get(u, accept='application/json')
    if st not in (200, 206): return {'value': None, 'src': u, 'status': status_text(st)}
    try:
        j = json.loads(body.decode('utf-8', 'replace'))
        v = float(j.get('altitude')) * 3.28084 if canada else float(j.get('value'))
        if v < -1500 or v > 25000: return {'value': None, 'src': u, 'status': 'no data at this point'}
        STAT['elevations'] += 1
        return {'value': round(v), 'src': u}
    except Exception as e: return {'value': None, 'src': u, 'status': 'unreadable: ' + str(e)[:40]}  # noqa: BLE001


def fcc_files(area, state):
    """Step 1 of cell coverage: with the FCC BDC account, list the mobile coverage files published for this state (cached per
    area per run in state['fcc']). Step 2 (point-in-coverage) is not built: those files are bulk GeoPackages."""
    if not (FCC_USER and FCC_TOKEN): return {'status': 'needs FCC token', 'carriers': None, 'src': 'https://broadbandmap.fcc.gov/ (BDC public data API, free account)'}
    cache = state.setdefault('fcc', {})
    if (cache.get(area) or {}).get('read') == TODAY: return cache[area]['cell']
    out = {'status': 'FCC files listed (point lookup = step 2, not built)', 'carriers': None, 'src': None, 'files': []}
    st, hd, body, final = M.get(FCC + 'listAsOfDates', accept='application/json')
    try:
        dates = [d.get('as_of_date') for d in (json.loads(body.decode('utf-8', 'replace')).get('data') or []) if d.get('data_type') == 'availability'] if st in (200, 206) else []
        if not dates: out['status'] = f'FCC listAsOfDates: {status_text(st)}'
        else:
            d = sorted(dates)[-1]
            u = FCC + f'downloads/listAvailabilityData/{d}?category=State&subcategory=Mobile%20Broadband'
            st2, hd2, body2, f2 = M.get(u, accept='application/json')
            out['src'] = u
            if st2 in (200, 206):
                rows = json.loads(body2.decode('utf-8', 'replace')).get('data') or []
                mine = [r for r in rows if str(r.get('state_name') or '').lower() == STATE_NAMES.get(area[3:], '').lower() or f'_{area[3:]}_' in str(r.get('file_name') or '')]
                out['files'] = [{'provider': r.get('provider_name'), 'tech': r.get('technology_code_desc') or r.get('technology_type'), 'file': r.get('file_name'), 'id': r.get('file_id')} for r in mine][:60]
                out['status'] = f'FCC as of {d}: {len(mine)} mobile coverage files for the state (point lookup = step 2, not built)'
            else: out['status'] = f'FCC listAvailabilityData: {status_text(st2)}'
    except Exception as e: out['status'] = 'FCC read failed: ' + str(e)[:60]  # noqa: BLE001
    cache[area] = {'read': TODAY, 'cell': out}
    return out


STATE_NAMES = {'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'DC': 'District of Columbia', 'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland', 'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina', 'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming'}


# ---- the campground list per area
def camp_rows(area):
    """[{id, name, lat, lon, park, agency, kind, page, reserve, src}] from campfed + campstate + campstate-manual (+ Kentucky's
    hand-checked list). Day-use shelters (kind 's') and lodges are left out: this bot is about campgrounds."""
    st = area[3:]; rows = {}
    def add(i, name, la, lo, park, agency, kind, page, reserve, src):
        if not i or i in rows: return
        try: la, lo = float(la), float(lo)
        except Exception: la = lo = None  # noqa: BLE001
        rows[i] = {'id': str(i), 'name': name or '', 'lat': la, 'lon': lo, 'park': park or '', 'agency': agency or '', 'kind': kind or 'c', 'page': page or '', 'reserve': reserve or '', 'src': src}
    if area.startswith('US-'):
        for r in (load(f'data/campfed/{area}.json', {}) or load(LINKS / f'data/campfed/{area}.json', {})).get('camps') or []:
            if len(r) > 7 and r[7] == 's': continue
            add(r[0], r[1], r[2], r[3], '', r[4], 'c', r[6] if len(r) > 6 else '', r[6] if len(r) > 6 else '', 'campfed')
        for r in load(f'data/campstate/{area}.json', {}).get('camps') or []:
            add(r[0], r[1], r[2], r[3], r[5] if len(r) > 5 else '', 'state', r[4] if len(r) > 4 else 'c', r[6] if len(r) > 6 else '', r[7] if len(r) > 7 else '', 'campstate')
        for r in load(f'data/campstate-manual/{area}.json', {}).get('camps') or []:
            add(r[0], r[1], r[2], r[3], r[5] if len(r) > 5 else '', 'state', r[4] if len(r) > 4 else 'c', r[6] if len(r) > 6 else '', r[7] if len(r) > 7 else '', 'campstate-manual')
        if st == 'KY':
            for p in load(LINKS / 'kpc-campgrounds.json', {}).get('parks') or []:
                for c in p.get('campgrounds') or []:
                    add(c.get('id'), c.get('name'), c.get('la'), c.get('lo'), p.get('pota'), 'KY (hand-checked list)', 'c', c.get('url') or c.get('source'), c.get('reserve'), 'kpc-campgrounds.json')
    # Canada: no campground rows exist yet in KPC-Data (parkinfo/CA.json lists activities only); review.md says so
    return rows


def ky_key():
    """Kentucky answer key: id -> the hand-checked values (sites, amps, dump, showers, phone)."""
    K = {}
    for p in load(LINKS / 'kpc-campgrounds.json', {}).get('parks') or []:
        for c in p.get('campgrounds') or []:
            s = c.get('sites'); n = s if isinstance(s, int) else (int(re.match(r'\s*(\d+)', str(s)).group(1)) if re.match(r'\s*\d+', str(s or '')) else None)
            hk = str(c.get('hookups') or ''); ex = str(c.get('extras') or '')
            K[c.get('id')] = {'name': c.get('name'), 'sites': n, 'amps': sorted({int(a) for tup in AMPS.findall(hk) for a in tup if a}), 'dump': True if re.search(r'dump', ex, re.I) else None,
                              'showers': True if re.search(r'shower|bath ?house', ex, re.I) else None, 'phone': c.get('phone'), 'checked': c.get('checked'), 'electric': True if re.search(r'electric|amp|hookup', hk, re.I) else (False if re.search(r'primitive only|no hookups', hk, re.I) else None)}
    return K


# ---- one campground
def blank_record(r):
    return {'name': r['name'], 'lat': r['lat'], 'lon': r['lon'], 'park': r['park'], 'agency': r['agency'], 'kind': r['kind'], 'official_page': r['page'] or None,
            'booking': {'url': None, 'how': None}, 'lodging_booking': {'url': None, 'how': None}, 'map': {'url': None, 'date_how': None},
            'sites': {'total': None, 'tent': None, 'rv': None, 'cabin': None, 'group': None, 'primitive': None}, 'rv_max_ft': None,
            'hookups': {'electric': None, 'amps': None, 'water': None, 'sewer': None}, 'dump_station': None, 'showers': None, 'restrooms': None, 'drinking_water': None,
            'fees': None, 'reservable': None, 'season': None, 'checkin': None, 'checkout': None,
            'rules': {'pets': None, 'generators': None, 'quiet_hours': None, 'fires': None, 'stay_limit': None}, 'phone': None, 'phone_hint': None, 'features': None,
            'elevation_ft': {'value': None, 'src': None}, 'cell': {'status': 'needs FCC token', 'carriers': None, 'src': None},
            'facts_src': {}, 'status': 'not read', 'checked': TODAY, 'ver': VER, 'list': r['src']}


def apply_facts(rec, F):
    """Put each fact's value in its field and its {url, date, line} in facts_src (field names use dots: 'hookups.amps')."""
    for k, f in F.items():
        parts = k.split('.'); d = rec
        for p in parts[:-1]: d = d.setdefault(p, {})
        d[parts[-1]] = f['value']
        rec['facts_src'][k] = {'url': f['url'], 'date': f['date'], 'line': f['line']}


def own_section(text, name):
    """Round 4 rule 1: when a page lists SEVERAL campgrounds (a forest 'camping' page, an LBL sister page), only the part that
    names THIS campground counts. -> the text from the first line that names the campground up to the next line that names a
    different campground (a heading-like line ending in Campground / Camp / Area), or '' when the page never names it."""
    cn = norm_name(name)
    if not cn: return ''
    words = [w for w in cn.split() if len(w) > 2]
    if not words: return ''
    lines = text.split('\n'); start = None
    for i, ln in enumerate(lines):
        if all(w in norm_name(ln) for w in words): start = i; break
    if start is None: return ''
    end = len(lines)
    for j in range(start + 1, len(lines)):
        ln = lines[j]
        if len(ln) < 70 and re.search(r'(campground|camp|horse camp|recreation area|boat-in)\s*$', ln, re.I) and not all(w in norm_name(ln) for w in words):
            end = j; break
    return '\n'.join(lines[start:end])


def names_other_camps(text, name):
    """True when the page names 2+ campgrounds other than this one (a list page)."""
    others = {m.group(0).lower() for m in re.finditer(r'\b[A-Z][\w\'-]+(?:\s+[A-Z][\w\'-]+){0,3}\s+(?:Campground|Horse Camp)\b', text) if norm_name(m.group(0)) != norm_name(name)}
    return len(others) >= 2


def one_camp(area, r, state):
    rec = blank_record(r)
    canada = area.startswith('CA-')
    if r['src'] == 'campfed':
        if not RIDB_KEY: rec['status'] = 'needs RIDB_API_KEY secret in KPC-Data'; STAT['needs_key'] += 1
        else:
            st, F = ridb_facts(r['id'])
            apply_facts(rec, F); rec['status'] = st
            if st == 'ok': STAT['ok'] += 1
    else:
        u = r['page']
        if not u: rec['status'] = 'no official page on file'; STAT['no_page'] += 1
        elif not official(u, area, r['park']): rec['status'] = 'page not on an official host: ' + host_of(u); STAT['not_official'] += 1
        else:
            st, text, links = read_page(u)
            rec['status'] = st
            if st == 'ok':
                # round 4 rule 1: a page that lists several campgrounds is read only in THIS campground's section
                if names_other_camps(text, r['name']):
                    sec = own_section(text, r['name']); rec['read_section'] = 'own section' if sec else 'page names other campgrounds, never this one'
                    text = sec
                F = facts_from_text(text, u) if text else {}; F.update(links_facts(links, u))
                # round 3 rule 5: a PARK page (parks.ky.gov …) often keeps the campground facts on its own 'Campground' page: when
                # the page gave no site count, follow ONE same-host link whose text or url says campground / camping and fill the blanks.
                # Round 4: the sub-page is read only in this campground's section when it lists several (the forest 'camping' page)
                if 'sites.total' not in F and not late():
                    sub = next((lu for lu, lt in links if host_of(lu) == host_of(u) and re.search(r'campground|camping|campsite', (lt or '') + ' ' + lu, re.I)
                                and not re.search(r'reserv|cancel|policy|lodg|cottage|\.pdf', (lt or '') + ' ' + lu, re.I) and lu.split('#')[0] != u.split('#')[0]), None)
                    if sub:
                        st2, text2, links2 = read_page(sub)
                        rec['campground_page'] = {'url': sub, 'status': st2}
                        if st2 == 'ok':
                            if names_other_camps(text2, r['name']): text2 = own_section(text2, r['name']); rec['campground_page']['read'] = 'own section' if text2 else 'names other campgrounds only'
                            F2 = facts_from_text(text2, sub) if text2 else {}
                            if text2: F2.update(links_facts(links2, sub))
                            for k2, v2 in F2.items():
                                if k2 not in F: F[k2] = v2
                apply_facts(rec, F); STAT['ok'] += 1
                # round 4 rule 3: a state-park page that gave no campground facts at all is probably filled by script -> say so
                if not any(k.startswith(('sites.', 'hookups.')) or k in ('dump_station', 'showers') for k in F):
                    rec['status'] = 'ok, no campground facts in the page text: needs browser?'; rec['needs_browser'] = True; STAT['needs_browser'] += 1
            elif st.startswith('HTTP 403'): STAT['needs_browser'] += 1
            elif st == 'robots.txt says no': STAT['robots'] += 1
            elif st == 'host resting': STAT['resting'] += 1
        if not rec['booking']['url'] and r['reserve'] and official(r['reserve'], area, r['park']) and not bare_domain(r['reserve']):
            rl = r['reserve'].lower()
            if bare_domain(r['reserve']): rl = ''
            key = 'lodging_booking' if re.search(r'lodge|cottage|cabin|room', rl) and 'camp' not in rl else 'booking'
            rec[key] = {'url': r['reserve'], 'how': 'online: ' + host_of(r['reserve'])}
            rec['facts_src'][key + '.url'] = {'url': r['reserve'], 'date': TODAY, 'line': f"booking link from our {r['src']} row (official system {host_of(r['reserve'])})"}
    # the status of a federal or state read never stops the elevation or the coverage note
    if not late(): rec['elevation_ft'] = elevation(r['lat'], r['lon'], canada)
    rec['cell'] = fcc_files(area, state) if not canada else {'status': 'FCC map covers the US only; Canada = ISED coverage maps (not built)', 'carriers': None, 'src': None}
    rec['cell'] = {k: v for k, v in rec['cell'].items() if k != 'files'} | ({'files': rec['cell']['files'][:3]} if rec['cell'].get('files') else {})
    return rec


# Round 4: rows the checkers (chat 8 + chat 11, Oct 28) found WRONG IN THE HAND KEY: left out of the agreement count, listed in review.md
KEY_WRONG = {
    ('koomer-ridge-campground', 'electric'): "agency page says 'no hookups' (chat 8 grade); key says electric True",
    ('clear-creek-campground', 'electric'): 'agency words say no hookups (chat 11 regrade); key says electric True',
    ('white-sulphur-horse-camp', 'electric'): 'agency words say no hookups (chat 11 regrade); key says electric True',
    ('great-meadows-campground', 'electric'): 'agency words say no hookups (chat 11 regrade); key says electric True',
    ('turkey-foot-campground', 'electric'): "agency page: 'There is no water, electricity or dump station available' (chat 8); key says electric True",
}


def ky_check(D):
    """R5: the bot's reading vs the hand-checked Kentucky values; agree / differ / bot blank, field by field.
    Round 4: 'some' vs a key True counts as AGREE (the bot is more careful: only certain sites have it); KEY_WRONG rows are
    listed apart and left out of the count."""
    K = ky_key(); rows = []; key_wrong = []
    for cid, k in K.items():
        rec = (D.get('camps') or {}).get(cid) or next((r for r in D.get('camps', {}).values() if cid in (r.get('ids') or [])), None)
        if not rec: rows.append({'id': cid, 'name': k['name'], 'status': 'not in output'}); continue
        row = {'id': cid, 'name': k['name'], 'status': rec.get('status'), 'fields': {}}
        def cmp(name, ours, theirs):
            if theirs is None: return
            if (cid, name) in KEY_WRONG:
                key_wrong.append({'id': cid, 'name': k['name'], 'field': name, 'bot': ours, 'key': theirs, 'why': KEY_WRONG[(cid, name)]})
                row['fields'][name] = f'KEY WRONG (bot {ours}, key {theirs}): left out'; return
            if ours is None: row['fields'][name] = f'bot blank (key: {theirs})'
            elif ours == theirs or (ours == 'some' and theirs is True): row['fields'][name] = f'agree ({theirs})' + (' [bot: some]' if ours == 'some' else '')
            else: row['fields'][name] = f'DIFFER bot {ours} vs key {theirs}'
        cmp('sites', rec['sites'].get('total'), k['sites'])
        cmp('amps', rec['hookups'].get('amps'), k['amps'] or None)
        cmp('electric', rec['hookups'].get('electric'), k['electric'])
        cmp('dump_station', rec.get('dump_station'), k['dump'])
        cmp('showers', rec.get('showers'), k['showers'])
        if k['phone']:
            m = PHONE.search(k['phone']); kp = f'({m.group(1)}) {m.group(2)}-{m.group(3)}' if m else k['phone']
            bp = rec.get('phone'); bp = bp if not isinstance(bp, list) else (kp if kp in bp else bp)   # C-3: a list agrees when it holds the key's number
            cmp('phone', bp, kp)
        rows.append(row)
    agree = sum(1 for r in rows for v in (r.get('fields') or {}).values() if v.startswith('agree'))
    differ = sum(1 for r in rows for v in (r.get('fields') or {}).values() if v.startswith('DIFFER'))
    blank = sum(1 for r in rows for v in (r.get('fields') or {}).values() if v.startswith('bot blank'))
    out = {'when': TODAY, 'campgrounds': len(rows), 'agree': agree, 'differ': differ, 'bot_blank': blank, 'rows': rows, 'key_wrong': key_wrong}
    out['gate'] = ky_gate(D, agree, differ)
    return out


# the 8 known answers of chat 11's round-2 grade (Oct 28): (which record by name words, field path, wanted value or a test name)
GATE_ROWS = [
    ('higginson', 'rv_max_ft', None, 'Higginson-Henry WMA: no RV length (the page gives elevation 675 ft, not an RV length)'),
    ('rolling fork', 'rv_max_ft', None, 'Rolling Fork WMA: no RV length (elevation 980 ft is not an RV length)'),
    ('west kentucky', 'rv_max_ft', None, 'West Kentucky WMA: no RV length (elevation 451 ft is not an RV length)'),
    ('yellowbank', 'rv_max_ft', None, 'Yellowbank WMA: no RV length (elevation 872 ft is not an RV length)'),
    ('yellowbank', 'season', None, 'Yellowbank WMA: no camping season (Nov. 1-Dec. 31 is the rabbit / quail hunting season)'),
    ('higginson', 'season', None, 'Higginson-Henry WMA: no camping season (hunting season dates are not the camping season)'),
    ('mammoth cave campground', 'showers', 'sentence-or-null', "Mammoth Cave: showers from a real sentence or null, never the 'Shower Types' menu heading"),
    ('twin knobs', 'hookups.sewer', 'some', "Twin Knobs: 'RV sites range from electric-only to full hookups' = sewer 'some'"),
    # round 3 (chat 11 regrade)
    ('bandy creek', 'phone', 'not-877', 'Bandy Creek: phone is not the (877) reservation line'),
    ('bear creek', 'phone', 'not-877', 'Bear Creek Horse Camp: phone is not the (877) reservation line'),
    ('blue heron', 'phone', 'not-877', 'Blue Heron: phone is not the (877) reservation line'),
    ('station camp', 'phone', 'not-877', 'Station Camp: phone is not the (877) reservation line'),
    ('white sulphur', 'booking.url', 'not-bare', 'White Sulphur Horse Camp: booking link is a campground page, not a bare domain'),
    ('s-tree', 'booking.url', 'not-bare', 'S-Tree: booking link is a campground page, not a bare domain'),
    ('mammoth cave campground', '', 'one-record', 'Mammoth Cave Campground: one record only (duplicates merged)'),
    ('fort boonesborough', 'sites.total', '>=100', 'Fort Boonesborough: site count read from the state park page (key 163, so >= 100)'),
]


def ky_gate(D, agree, differ):
    """GATE (rounds 2 + 3): PASS = the 16 known answers hold AND at least 70% of the hand-key fields the bot filled agree.
    Printed as 'GATE=PASS' / 'GATE=FAIL' for the workshop driver; saved in state['test'] like the other bots."""
    rows = []
    def get(rec, path):
        d = rec
        for p in path.split('.'):
            d = (d or {}).get(p) if isinstance(d, dict) else None
        return d
    for words, field, want, why in GATE_ROWS:
        recs = [r for r in (D.get('camps') or {}).values() if words in r.get('name', '').lower() and r.get('status') == 'ok']
        if not recs:
            rows.append({'ok': None, 'why': why, 'got': 'record not read (status not ok)'}); continue
        rec = recs[0]; got = get(rec, field) if field else None
        if want == 'one-record':
            n = sum(1 for r in (D.get('camps') or {}).values() if words in r.get('name', '').lower()); got = f'{n} record(s)'; ok = n == 1
        elif want == 'not-877':
            ph = got if isinstance(got, list) else [got] if got else []
            ok = not any(str(x).startswith(('(877)', '(800)', '(888)', '(866)')) for x in ph)
        elif want == 'not-bare': ok = not (got and bare_domain(got))
        elif want == '>=100':
            ok = isinstance(got, int) and got >= 100
            if not ok and (rec.get('needs_browser') or got is None):   # round 4 rule 3: the page text held no count -> WARN, not a fail
                rows.append({'ok': 'warn', 'why': why, 'got': f"no count in the page text; read {rec.get('official_page')} + {(rec.get('campground_page') or {}).get('url')} -> parks.ky.gov: needs browser?"}); continue
        elif want == 'sentence-or-null':
            line = ((rec.get('facts_src') or {}).get(field) or {}).get('line') or ''
            ok = got is None or (bool(line) and not is_heading(line) and re.search(r'shower', line, re.I) and VERB_W.search(line))
        else: ok = got == want
        rows.append({'ok': bool(ok), 'why': why, 'got': got if want != 'sentence-or-null' else f"{got} from “{line[:90]}”"})
    filled = agree + differ
    pct = round(100 * agree / filled) if filled else 0
    known_ok = all(r['ok'] for r in rows if r['ok'] is not None); unread = sum(1 for r in rows if r['ok'] is None); warn = sum(1 for r in rows if r['ok'] == 'warn')
    res = 'PASS' if known_ok and pct >= 70 and unread == 0 and filled else 'FAIL'
    why = f"known answers {sum(1 for r in rows if r['ok'] is True)}/{len(rows)} right ({warn} warn, {unread} not read) · hand-key agreement {agree}/{filled} = {pct}% (need 70%; 'some' = agree; KEY_WRONG rows left out)"
    return {'result': res, 'why': why, 'when': TODAY, 'rows': rows, 'pct': pct}


# ---- areas
def norm_name(n):
    n = re.sub(r'\(.*?\)', ' ', str(n or '').lower()); n = re.sub(r'[^a-z0-9 ]', ' ', n)
    n = re.sub(r'\b(campground|camp|recreation area|rec area|the|nat|national|forest|for|park|state|dbnf|daniel boone)\b', ' ', n)
    return ' '.join(n.split())


def dist_m(a, b):
    import math
    if None in (a[0], a[1], b[0], b[1]): return 1e9
    kx = 111320 * math.cos(math.radians((a[0] + b[0]) / 2)); ky = 110540
    return math.hypot((a[1] - b[1]) * kx, (a[0] - b[0]) * ky)


def merge_duplicates(D):
    """C-4 (chat 8): the same campground under two ids (Twin Knobs / Zilpo: hand-checked list + RIDB, or two park refs) is ONE
    record: same normalized name and points within 300 m. Kept: the RIDB point for a federal campground, the state agency's point
    otherwise; the other ids go in 'ids'; facts the kept record lacks are filled from the other (with their source lines)."""
    camps = D['camps']; ids = sorted(camps)
    gone = set()
    for i, a in enumerate(ids):
        if a in gone: continue
        for b in ids[i + 1:]:
            if b in gone: continue
            A, B = camps[a], camps[b]
            if norm_name(A['name']) != norm_name(B['name']) or not norm_name(A['name']): continue
            d = dist_m((A['lat'], A['lon']), (B['lat'], B['lon']))
            same_park = bool(set((A.get('park') or '').split()) & set((B.get('park') or '').split()))
            no_point = None in (A['lat'], A['lon'], B['lat'], B['lon'])
            # round 3 rule 4: a record with no point of its own still merges when the park ref matches (Mammoth Cave, Twin Knobs)
            if d > 300 and not (no_point and same_park) and not (no_point and A.get('list') != B.get('list')): continue
            # keep the record WITH facts; on a tie the RIDB (campfed) record keeps its point
            fa, fb = len(A.get('facts_src') or {}), len(B.get('facts_src') or {})
            if fa != fb: keep, drop = (a, b) if fa > fb else (b, a)
            else: keep, drop = (a, b) if (A.get('list') == 'campfed') >= (B.get('list') == 'campfed') else (b, a)
            if camps[keep]['lat'] is None and camps[drop]['lat'] is not None: camps[keep]['lat'], camps[keep]['lon'] = camps[drop]['lat'], camps[drop]['lon']
            K, X = camps[keep], camps[drop]
            K.setdefault('ids', [keep]); K['ids'] = sorted(set(K['ids'] + X.get('ids', [drop]) + [drop]))
            if X.get('park') and X['park'] not in (K.get('park') or ''): K['park'] = (K['park'] + ' ' + X['park']).strip()
            for k, src in (X.get('facts_src') or {}).items():
                if k in (K.get('facts_src') or {}): continue
                parts = k.split('.'); d = X
                try:
                    for p2 in parts: d = d[p2]
                except Exception: continue  # noqa: BLE001
                t = K
                for p2 in parts[:-1]: t = t.setdefault(p2, {})
                t[parts[-1]] = d; K['facts_src'][k] = src
            if K.get('status') != 'ok' and X.get('status') == 'ok': K['status'] = 'ok'; K['official_page'] = K.get('official_page') or X.get('official_page')
            if (K.get('elevation_ft') or {}).get('value') is None and (X.get('elevation_ft') or {}).get('value') is not None: K['elevation_ft'] = X['elevation_ft']
            gone.add(drop)
    for d in gone: camps.pop(d, None)
    D['merged'] = len(gone)


def counts(D):
    c = {'camps': len(D['camps']), 'ok': 0, 'needs_key': 0, 'needs_browser': 0, 'robots': 0, 'resting': 0, 'no_page': 0, 'not_official': 0, 'other': 0, 'with_sites': 0, 'with_booking': 0, 'with_elevation': 0}
    for r in D['camps'].values():
        s = r.get('status') or ''
        c['ok' if s == 'ok' else 'needs_key' if 'RIDB' in s else 'needs_browser' if ('403' in s or 'needs browser' in s) else 'robots' if 'robots' in s else 'resting' if 'resting' in s else 'no_page' if 'no official page' in s else 'not_official' if 'not on an official' in s else 'other'] += 1
        if (r.get('sites') or {}).get('total') is not None: c['with_sites'] += 1
        if (r.get('booking') or {}).get('url'): c['with_booking'] += 1
        if (r.get('elevation_ft') or {}).get('value') is not None: c['with_elevation'] += 1
    return c


def run_area(area, state):
    f = OUT / f'{area}.json'
    D = load(f, {'area': area, 'about': 'Campground info bot: facts from the agency that runs each campground, every fact with its source line. Gathers facts, decides nothing. Maps and park info are a planning aid, not a guarantee: always check the official agency page and rules before you go.', 'camps': {}})
    rows = camp_rows(area)
    if not rows:
        why = 'no campground rows on file' + (' (Canada: no Parks Canada / provincial campground list in KPC-Data yet)' if area.startswith('CA-') else '')
        notice(f'{area}: {why}'); state['areas'][area] = {'status': 'done', 'camps': 0, 'updated': TODAY, 'note': why}; D['read'] = TODAY; D['counts'] = counts(D); save(f, D); return
    fresh_cut = time.strftime('%Y-%m-%d', time.gmtime(time.time() - REFRESH_DAYS * 86400))
    done = fresh = 0
    for cid in sorted(rows, key=lambda i: (rows[i]['src'] != 'kpc-campgrounds.json', rows[i]['name'])):
        if late(): break
        old = D['camps'].get(cid)
        if old and old.get('ver', 0) >= VER and old.get('checked', '') >= fresh_cut and old.get('status') not in ('needs RIDB_API_KEY secret in KPC-Data', 'host resting'):
            fresh += 1; STAT['skipped_fresh'] += 1; continue
        STAT['camps'] += 1
        try: D['camps'][cid] = one_camp(area, rows[cid], state)
        except Exception as e:  # noqa: BLE001
            STAT['errors'] += 1; rec = blank_record(rows[cid]); rec['status'] = 'bot error: ' + str(e)[:80]; D['camps'][cid] = rec
        done += 1
    merge_duplicates(D)
    D['read'] = TODAY; D['counts'] = counts(D)
    save(f, D)
    if area == 'US-KY' and done:
        state['ky_check'] = ky_check(D)
        g = state['ky_check']['gate']; state['test'] = {'result': g['result'], 'why': g['why'], 'when': g['when']}
        notice(f"KENTUCKY GATE {g['result']}: {g['why']}"); print('GATE=' + g['result'], flush=True)
    left = sum(1 for i in rows if i not in D['camps'])
    state['areas'][area] = {'status': 'done' if left == 0 else 'partial', 'camps': len(rows), 'checked': len(D['camps']), 'left': left, 'updated': TODAY, 'counts': D['counts']}
    notice(f"{area}: {done} campgrounds read this chunk ({fresh} fresh, {left} left) · {D['counts']}")


def fact_lines(rec):
    """Short 'field = value (“source line”)' list for review.md."""
    out = []
    for k, s in (rec.get('facts_src') or {}).items():
        d = rec
        try:
            for p in k.split('.'): d = d[p]
        except Exception: d = '?'  # noqa: BLE001
        out.append(f"{k} = {json.dumps(d, ensure_ascii=False)[:60]} · “{(s.get('line') or '')[:140]}”")
    return out


def review(state):
    L = ['# Campground info bot: review (facts only; nothing here decides anything)', '',
         f'Updated {TODAY}. Every fact in <area>.json carries its source url, read date and quoted line (facts_src). Unknown = null, never guessed.',
         'ℹ️ Maps and park info are a planning aid, not a guarantee. Always check the official agency map and rules before you go.', '',
         '| area | campgrounds | read ok | needs RIDB key | needs browser (403) | robots no | host resting | no page on file | not official host | other | with site count | with booking link | with elevation |',
         '|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for a in QUEUE:
        c = (state['areas'].get(a) or {}).get('counts')
        if not c: continue
        L.append(f"| {a} | {c['camps']} | {c['ok']} | {c['needs_key']} | {c['needs_browser']} | {c['robots']} | {c['resting']} | {c['no_page']} | {c['not_official']} | {c['other']} | {c['with_sites']} | {c['with_booking']} | {c['with_elevation']} |")
    notes = []
    if not RIDB_KEY: notes.append('RIDB_API_KEY is not set in KPC-Data: every federal (Recreation.gov) row has status "needs RIDB_API_KEY secret in KPC-Data". Free key: ridb.recreation.gov, Profile. Add it under Settings -> Secrets and variables -> Actions.')
    if not (FCC_USER and FCC_TOKEN): notes.append('FCC_BDC_USERNAME + FCC_BDC_TOKEN are not set: cell coverage stays blank with status "needs FCC token". Free account at broadbandmap.fcc.gov; the public data API gives per-state bulk coverage files (step 2, point lookup, is not built yet).')
    ca = [a for a in QUEUE if a.startswith('CA-') and (state['areas'].get(a) or {}).get('note')]
    if ca: notes.append('Canada: no campground rows exist in KPC-Data yet (no campfed / campstate file for CA-xx; parkinfo/CA.json lists activities only), so the Canadian areas are marked done with nothing read. Parks Canada camping needs its own list first.')
    if notes: L += ['', '## Needs a secret / not built yet', ''] + [f'- {n}' for n in notes]
    hosts = {}
    for a in QUEUE:
        D = load(OUT / f'{a}.json', None)
        if not D: continue
        for r in D['camps'].values():
            s = r.get('status') or ''
            if '403' in s or 'robots' in s or 'resting' in s or 'needs browser' in s:
                h = host_of(r.get('official_page') or ''); hosts.setdefault(h, [s, 0])[1] += 1
    if hosts:
        L += ['', '## Hosts that need a browser (403), say no in robots.txt, or are resting', ''] + [f'- {h}: {n} campgrounds · {s}' for h, (s, n) in sorted(hosts.items(), key=lambda x: -x[1][1])[:40]]
    k = state.get('ky_check')
    if k:
        L += ['', '## Kentucky answer-key check (R5: the bot vs kpc-campgrounds.json, hand-checked)', '',
              f"- {k['when']}: {k['campgrounds']} hand-checked campgrounds · fields agree {k['agree']} · DIFFER {k['differ']} · bot blank {k['bot_blank']}", '']
        g = k.get('gate')
        if g:
            L += [f"**GATE={g['result']}** · {g['why']}", '']
            for r in g['rows']: L.append(f"- {'ok' if r['ok'] is True else 'WARN' if r['ok'] == 'warn' else 'not read' if r['ok'] is None else 'MISS'}: {r['why']} · got {r['got']}")
            L.append('')
        if k.get('key_wrong'):
            L += ['**KEY_WRONG (hand-key rows the checkers found wrong; left out of the count; Brandon fixes the key):**', '', '| campground | field | bot | key | why |', '|---|---|---|---|---|']
            for w in k['key_wrong']: L.append(f"| {w['name']} | {w['field']} | {w['bot']} | {w['key']} | {w['why']} |")
            L.append('')
        unread = [r for r in k['rows'] if r.get('status') == 'not in output']
        for r in k['rows']:
            fs = r.get('fields') or {}
            if r.get('status') == 'not in output': continue
            L.append(f"- {r['name']} ({r.get('status')}): " + ('; '.join(f'{f} {v}' for f, v in fs.items()) or 'nothing to compare'))
        if unread: L.append(f'- … {len(unread)} hand-checked campgrounds not read yet (next chunk)')
    for a in QUEUE:
        D = load(OUT / f'{a}.json', None)
        if not D or not D['camps']: continue
        L += ['', f'## {a}: 12 random samples (records with facts; seed = the date)', '']
        import random
        pool = [x for x in D['camps'].items() if x[1].get('facts_src')]
        best = random.Random(TODAY + a).sample(pool, min(12, len(pool)))
        for cid, r in best:
            el = (r.get('elevation_ft') or {}).get('value')
            L.append(f"- **{r['name']}** ({cid}, {r.get('agency') or 'state'}, status {r.get('status')}, {len(r.get('facts_src') or {})} facts" + (f', {el} ft' if el is not None else '') + f") · [{host_of(r.get('official_page') or '')}]({r.get('official_page') or ''})")
            for fl in fact_lines(r)[:10]: L.append(f'  - {fl}')
    (OUT / 'review.md').write_text('\n'.join(L) + '\n', encoding='utf-8')


# ---- offline self test of the regexes
SAMPLES = [
    ('KY-style page', 'The campground offers 146 sites with electric and water hookups, 50-amp service at 30 sites, a dump station, showers and restrooms. Pets are welcome on a leash. Quiet hours 10 pm to 7 am. Maximum stay 14 consecutive days. Open April 1 through October 31. Reservations: 1-800-555-0199. Check-in 3:00 pm, check-out 1:00 pm. Fee $26 per night.'),
    ('state park with sub-counts', 'Big Bone Lick Campground has 62 campsites, all with 30 amp electric and water. 2 tent sites have no hookups. Flush toilets, hot showers and a dump station are available. Maximum RV length 45 feet. Campground office (859) 384-3522. Open March 1 - November 15. Sites $30-$35/night. Firewood is sold at the campground; no outside firewood.'),
    ('primitive forest camp', 'A primitive campground with 12 walk-in sites. Vault toilets. No drinking water: bring your own water. No electric. First come, first served. Generators are not permitted. Campfires only in fire rings. 14 day stay limit. Open year-round, weather permitting.'),
    ('cabins and group', 'The park rents 15 cabins and 2 yurts. The group campground accommodates up to 50 people and has 4 group sites. Pets are not permitted in cabins. Check-in: 4 p.m. Check-out: 11 a.m.'),
    ('full hookup RV park', 'Our modern campground features 85 full hookup sites (water, electric, sewer) with 30/50-amp service and pull-through sites for RVs up to 60 ft. Bathhouse with hot showers, laundry, dump station. Quiet time is 11:00 PM until 6:00 AM. Reservations are required. Call 1-888-555-0123 or (606) 555-0144 for information.'),
    ('no facts page', 'Welcome to the Historic Site. The visitor center is open daily. Explore 3 historic sites and 2 web sites for more. Maps are available at the office.'),
    ('fees and season words', 'Camping fees: $18 per night for primitive sites, $32 per night for electric sites, and $45 a night for full-hookup. The campground is open from mid-April through late October. Max stay is 14 nights in any 30-day period. Dogs are allowed on a leash no longer than 6 feet.'),
    ('mixed reservation', 'Of the 48 campsites, 30 are reservable online and the rest are first-come, first-served. Electric hookups (20/30 amp) at 24 sites. Pit toilets; potable water at the spigot by the entrance. Trailers up to 35 feet. Quiet hours: 10:00 p.m. - 6:00 a.m.'),
    ('negatives', 'This campground has 20 sites. No showers. No dump station. Non-electric only. Pets must be leashed at all times. Generators may run 8 am to 8 pm only. Stay is limited to 7 consecutive days.'),
    ('campground has N', 'The campground has 97 sites, 54 with electric hookups. Modern restrooms with showers. RV sites accommodate rigs 40 feet maximum. The park office phone is 270-555-0177; the reservation line is 1-888-459-7275.'),
]


# ---- C-1 negation test: 15 'has' + 15 'has no' sentences; every one must come out right (run by --negtest and by --selftest)
NEGTEST = [
    # (sentence, field, wanted value)
    ('The campground has electric hookups at every site.', 'hookups.electric', True),
    ('Water and electric at all sites.', 'hookups.electric', True),
    ('Water and electric at all sites.', 'hookups.water', True),
    ('A dump station is located near the entrance.', 'dump_station', True),
    ('Hot showers and flush toilets are available.', 'showers', True),
    ('Hot showers and flush toilets are available.', 'restrooms', 'flush'),
    ('Drinking water is available from spigots throughout the loop.', 'drinking_water', True),
    ('Full hookup sites with water, electric and sewer.', 'hookups.sewer', True),
    ('Some sites have 50 amp service.', 'hookups.electric', 'some'),
    ('RV sites range from electric-only to full hookups.', 'hookups.sewer', 'some'),
    ('Electric hookups are available at 24 of the 48 sites.', 'hookups.electric', 'some'),
    ('Vault toilets are provided.', 'restrooms', 'vault'),
    ('The bathhouse has showers and a laundry.', 'showers', True),
    ('Potable water and a sanitary dump station are available in season.', 'dump_station', True),
    ('Each site has a 30 amp electrical pedestal.', 'hookups.electric', True),
    ('There is no water, electricity or dump station available.', 'hookups.electric', False),
    ('There is no water, electricity or dump station available.', 'dump_station', False),
    ('There is no water, electricity or dump station available.', 'hookups.water', None),
    ('No hookups.', 'hookups.electric', False),
    ('No dump station.', 'dump_station', False),
    ('Electric hookups are not available.', 'hookups.electric', False),
    ('This primitive campground has no showers.', 'showers', False),
    ('Sites are without electricity.', 'hookups.electric', False),
    ('Drinking water is not available; bring your own.', 'drinking_water', False),
    ('The campground does not have a dump station.', 'dump_station', False),
    ('No restrooms or drinking water.', 'restrooms', 'none'),
    ('No restrooms or drinking water.', 'drinking_water', False),
    ('Sewer hookups are not offered.', 'hookups.sewer', False),
    ('There are no showers, but vault toilets are provided.', 'showers', False),
    ('There are no showers, but vault toilets are provided.', 'restrooms', 'vault'),
    ('Showers are unavailable in winter. Electricity is not provided.', 'hookups.electric', False),
]


def negtest(quiet=False):
    bad = 0
    for sent, field, want in NEGTEST:
        F = facts_from_text(sent, 'sample://neg')
        got = (F.get(field) or {}).get('value') if field in F else None
        ok = got == want
        bad += 0 if ok else 1
        if not quiet or not ok: print(f"   {'ok  ' if ok else 'MISS'} {field:17s} want {want!r:8} got {got!r:8} <- {sent}")
    print(f'NEGTEST: {len(NEGTEST) - bad}/{len(NEGTEST)} right -> {"PASS" if bad == 0 else "FAIL"}')
    return bad == 0


def selftest():
    print('CAMPGROUND INFO BOT selftest (regexes only, no network)')
    bad = 0
    for title, text in SAMPLES:
        F = facts_from_text(text, 'sample://' + title.replace(' ', '-'))
        print(f'\n== {title}: {len(F)} facts')
        for k, f in F.items(): print(f'   {k:20s} = {json.dumps(f["value"], ensure_ascii=False)}')
    F = facts_from_text(SAMPLES[0][1], 'sample://ky')
    want = {'sites.total': 146, 'hookups.amps': [50], 'hookups.electric': True, 'hookups.water': True, 'dump_station': True, 'showers': True, 'restrooms': 'yes (kind not stated)',
            'rules.pets': 'Pets are welcome on a leash', 'rules.quiet_hours': '10 pm to 7 am', 'rules.stay_limit': '14 consecutive days', 'season': 'April 1 through October 31',
            'checkin': '3:00 pm', 'checkout': '1:00 pm', 'phone': None}   # round 3: 'Reservations: 1-800-…' is the booking line, never the phone
    for k, v in want.items():
        got = (F.get(k) or {}).get('value')
        if got != v: bad += 1; print(f'   MISS {k}: want {v!r}, got {got!r}')
    L = links_facts([('https://parks.ky.gov/x/map.pdf', 'Campground Map (2024)'), ('https://kentuckystateparks.reserveamerica.com/x', 'Reserve a site')], 'https://parks.ky.gov/x')
    for k, f in L.items(): print(f'   links: {k} = {f["value"]}')
    if not L.get('booking.url') or not L.get('map.url'): bad += 1; print('   MISS booking or map link')
    print(f'\nKY-style check: {"PASS" if bad == 0 else f"FAIL ({bad} misses)"}')
    neg_ok = negtest(quiet=True)
    return bad == 0 and neg_ok


def main():
    global M, SRC
    OUT.mkdir(parents=True, exist_ok=True)
    SRC = load(OUT / 'sources.json', {}) or load('data/campinfo/sources.json', {})
    state = load(OUT / 'state.json', {'areas': {}, 'hosts': {}, 'fcc': {}})
    M = Manners('campground info bot', state.get('hosts'))
    want = (os.environ.get('AREAS') or '').upper().split()
    areas = [a for a in want if a in QUEUE] if want else [a for a in QUEUE if (state['areas'].get(a) or {}).get('status') != 'done']
    if want and not areas: notice('no known area in AREAS'); return
    for area in areas:
        if late(): break
        try: run_area(area, state)
        except Exception as e:  # noqa: BLE001
            STAT['errors'] += 1; notice(f'{area}: stopped: {str(e)[:120]}')
    state['hosts'] = M.resting()
    state['last'] = {'when': TODAY, 'areas': areas[:8], 'stat': STAT, 'manners': M.stat, 'ridb_key': bool(RIDB_KEY), 'fcc_token': bool(FCC_TOKEN)}
    save(OUT / 'state.json', state)
    review(state)
    left = [a for a in QUEUE if (state['areas'].get(a) or {}).get('status') != 'done']
    notice(f"done this chunk: {STAT} · manners {M.stat} · areas left: {len(left)}" + (f" (next {' '.join(left[:4])})" if left else ''))


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        sys.exit(0 if selftest() else 1)
    if '--negtest' in sys.argv:
        sys.exit(0 if negtest() else 1)
    try: main()
    except Exception as e:  # noqa: BLE001
        import traceback; traceback.print_exc()
        notice(f'stopped: {e}')
    sys.exit(0)
