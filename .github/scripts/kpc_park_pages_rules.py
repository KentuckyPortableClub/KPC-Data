#!/usr/bin/env python3
"""Reading rules for the park page reader (hand-off 05, RULE SHEET R-PR).

Pure functions. No network. Sizes, name cores, status words, official hosts and the
map-link score come from the truth checker and the documents bot. This file adds
only what those readers do not say: labels, combined names, addresses, and the
questions.
"""
import hashlib, json, math, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kpc_truth_bot as TB  # noqa: E402
from kpc_docs_bot import gov_of, map_score, host_of, base_host, via_of  # noqa: E402
from kpc_manners import page_text, links_in, pdf_text, next_run, robots_block  # noqa: E402

READER = 'v1'
QUOTE_MAX = 200
REFRESH_DAYS = 30
REFUSAL_DAYS = 30
MAX_PER_PARK = 4
PDF_FIRST = 400_000

# Kind phrases, longest first. Built from the type words POTA stores plus the
# rule sheet's closed list. "Wild and Scenic River" is one kind.
KINDS = [
    'National Wild and Scenic River', 'Wild and Scenic River',
    'Special Recreation Management Area', 'Recreation Management Area',
    'Wilderness Study Area', 'National Conservation Area', 'National Recreation Area',
    'National Historical Park', 'National Historic Site', 'National Wildlife Refuge',
    'Wildlife Management Area', 'State Wildlife Area', 'State Fishing Lake',
    'National Battlefield', 'National Seashore', 'National Lakeshore', 'National Monument',
    'National Preserve', 'National Forest', 'National Park', 'State Forest', 'State Park',
    'State Trail', 'Recreation Area', 'Historic Area', 'Conservation Area', 'Wilderness',
]
ONE_KIND = ('national wild and scenic river', 'wild and scenic river', 'fish and wildlife',
            'parks and recreation', 'parks & recreation', 'lake and dam')
KIND_RX = re.compile(r'\b(' + '|'.join(re.escape(k) for k in KINDS) + r')\b', re.I)
COMBINED_RX = re.compile(
    r'\b(?P<a>National\s+(?:Historical\s+Park|Historic\s+Site|Recreation\s+Area|Wildlife\s+Refuge|'
    r'Conservation\s+Area|Battlefield|Seashore|Lakeshore|Monument|Forest|Park|Preserve)|'
    r'State\s+(?:Park|Forest|Wildlife\s+Area|Trail))'
    r'\s*(?P<j>&|and|/)\s*'
    r'(?P<b>(?:National\s+|State\s+)?(?:Historical\s+Park|Historic\s+Site|Recreation\s+Area|'
    r'Wildlife\s+Refuge|Preserve|Park|Monument|Forest|Seashore|Lakeshore))\b', re.I)
AGENCY_LETTERS = re.compile(r'\b(blm|wma|nwr|nps|usfs|usace|nf|sp)\b', re.I)
# KINDW leaves "management" behind in "Recreation Management Area".
MGMT = re.compile(r'\bmanagement\b', re.I)
FILLER = {'national', 'state', 'blm', 'the', 'of', 'and', 'a', 'an', 'for'}
NO_POINT = re.compile(r'\b(national forest|state forest|state trail|wild and scenic river|'
                      r'national river|scenic river)\b', re.I)
SCRIPT_HOST = re.compile(r'(^|\.)((experience|storymaps)\.arcgis\.com)$', re.I)
TAILS = re.compile(
    r'\s*(?:\(U\.S\. National Park Service\)|\|\s*Bureau of Land Management|'
    r'\|\s*U\.S\. Fish\s*(?:&|and)\s*Wildlife Service|\|\s*Forest Service|'
    r'[-|•]\s*(?:Arkansas State Parks|Alabama|Alaska|Arizona|Arkansas|California|Colorado|'
    r'Connecticut|Delaware|Florida|Georgia|Hawaii|Idaho|Illinois|Indiana|Iowa|Kansas|Kentucky|'
    r'Louisiana|Maine|Maryland|Massachusetts|Michigan|Minnesota|Mississippi|Missouri|Montana|'
    r'Nebraska|Nevada|New Hampshire|New Jersey|New Mexico|New York|North Carolina|North Dakota|'
    r'Ohio|Oklahoma|Oregon|Pennsylvania|Rhode Island|South Carolina|South Dakota|Tennessee|Texas|'
    r'Utah|Vermont|Virginia|Washington|West Virginia|Wisconsin|Wyoming|District of Columbia))\s*$', re.I)
INSIDE_RX = re.compile(
    r'\b(?P<how>within|inside|part of|located in|a unit of|an unit of|managed as part of|surrounded by)'
    r'\s+the\s+(?P<name>[A-Z][\w\'’.-]*(?:\s+[A-Z][\w\'’.-]*){0,7}\s+(?:' +
    '|'.join(re.escape(k) for k in KINDS) + r'))\b')
NOT_GEO = re.compile(r'National Park System|National Wildlife Refuge System|Bureau of Land Management|'
                     r'National Forest System|River Basin|Mountain Range', re.I)
BAD_SUBJECT = re.compile(r'\b(trail|campground|campsite|visitor cent(?:er|re)|picnic area|day-use area|'
                         r'boat ramp|overlook)\b', re.I)
HISTORY_IN = re.compile(r'\b(was once|once part of|formerly|historically|used to be|in the past)\b', re.I)
RULE_LINE = re.compile(r'\bas you explore the\b', re.I)
ROUND_RX = re.compile(
    r'\b((?:nearly|about|approximately|roughly|almost|over|more than)\s+[\d,]+\s*-?\s*acres?|'
    r'\d+(?:\.\d+)?-million-acre|\d+\+\s*million\s+acres?)\b', re.I)
LABEL_RX = re.compile(r'(?i)(park|preserve|total area|wilderness|land|water|lake|monument|forest)\s*:\s*$')
INCLUDING = re.compile(r'including\s*$', re.I)
WILD_AFTER = re.compile(r'acres of (?:[\w-]+\s+){0,3}wilderness', re.I)
STREET_WORD = re.compile(r'\b(?:Rd|Road|Dr|Drive|St|Street|Ave|Avenue|Blvd|Boulevard|Hwy|Highway|'
                         r'Lane|Ln|Way|Pike|Loop|Parkway|Pkwy|Circle|Ct|Court)\.?\b')
ZIP_RX = re.compile(r'\b(\d{5})(?:-\d{4})?\b')
PO_RX = re.compile(r'\bP\.?\s*O\.?\s*Box\s+\d+\b', re.I)
OFFICE_WORD = re.compile(r'field office|district office|ranger district|headquarters|supervisor.?s office|'
                         r'\bmailing\b|p\.?\s*o\.?\s*box', re.I)
PARK_ADDR = re.compile(r'park address|physical address|\bentrance\b|visitor cent(?:er|re)|\blocation\b', re.I)
ROAD_RX = [
    re.compile(r'\bI-\d{1,3}\b'),
    re.compile(r'\bexit\s+\d+\b', re.I),
    re.compile(r'\b(?:US|UT|SR|[A-Z]{2})-\d{1,4}\b'),
    re.compile(r'\bOld\s+Highway\s+\d+\b'),
    re.compile(r'\b(?:[A-Z][\w\'.-]+\s+){0,5}(?:Road|Street|Highway|Avenue|Drive|Lane|Boulevard|Parkway)\b'),
]
TOWN_RX = re.compile(r'\b(?:from|toward|to)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)')
SLASH_TOWN = re.compile(r'\b[A-Z]{2}-\d+/([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)')
TOWN_SKIP = {'North', 'South', 'East', 'West', 'The', 'Exit', 'Highway', 'Old', 'Main', 'National', 'State'}
TRACT_RX = re.compile(
    r"\b([A-Z][\w'’.-]*(?:\s+(?!Tract\b|Unit\b|Section\b|Block\b|Division\b|Parcel\b|Corner\b)"
    r"[A-Z][\w'’.-]*){0,4})\s+(Tract|Unit|Section|Block|Division|Parcel|Corner)\b")
AREA_N_RX = re.compile(r"\b([A-Z][\w'’.-]*(?:\s+[A-Z][\w'’.-]*){0,3})\s+Area\s+(\d+)\b")
TRACT_SKIP = re.compile(r'\b(nearby|attraction|legend|formerly|once|historic register)\b', re.I)
WALL = re.compile(r'are you human|sign in to continue|log ?in required|captcha|access denied|just a moment', re.I)
HEADS = {'addresses', 'address', 'directions', 'contact us', 'contact', 'fees', 'getting here',
         'how to get there', 'driving directions', 'mailing address', 'location'}

# Approximate state and province boxes. KPC-Data has no stored area-box table.
# A point is kept when it sits in this box or within 300 km of POTA's pin.
BOX = {
    'AL': (30.1, 35.1, -88.6, -84.8), 'AK': (51.0, 71.6, -170.0, -129.0), 'AZ': (31.3, 37.1, -114.9, -109.0),
    'AR': (33.0, 36.6, -94.7, -89.6), 'CA': (32.5, 42.1, -124.5, -114.1), 'CO': (36.9, 41.1, -109.1, -102.0),
    'CT': (40.9, 42.1, -73.8, -71.8), 'DE': (38.4, 39.9, -75.8, -74.8), 'FL': (24.4, 31.1, -87.7, -79.9),
    'GA': (30.3, 35.1, -85.7, -80.8), 'HI': (18.8, 22.3, -160.3, -154.7), 'ID': (41.9, 49.1, -117.3, -111.0),
    'IL': (36.9, 42.6, -91.6, -87.4), 'IN': (37.7, 41.8, -88.1, -84.7), 'IA': (40.3, 43.6, -96.7, -90.1),
    'KS': (36.9, 40.1, -102.1, -94.6), 'KY': (36.5, 39.2, -89.6, -81.9), 'LA': (28.9, 33.1, -94.1, -88.8),
    'ME': (42.9, 47.5, -71.1, -66.9), 'MD': (37.9, 39.8, -79.5, -75.0), 'MA': (41.2, 42.9, -73.6, -69.9),
    'MI': (41.7, 48.3, -90.5, -82.4), 'MN': (43.4, 49.4, -97.3, -89.5), 'MS': (30.1, 35.0, -91.7, -88.1),
    'MO': (35.9, 40.7, -95.8, -89.1), 'MT': (44.3, 49.1, -116.1, -104.0), 'NE': (39.9, 43.1, -104.1, -95.3),
    'NV': (35.0, 42.1, -120.1, -114.0), 'NH': (42.7, 45.4, -72.6, -70.6), 'NJ': (38.9, 41.4, -75.6, -73.9),
    'NM': (31.3, 37.0, -109.1, -103.0), 'NY': (40.5, 45.1, -79.8, -71.8), 'NC': (33.8, 36.6, -84.4, -75.4),
    'ND': (45.9, 49.1, -104.1, -96.5), 'OH': (38.4, 42.0, -84.9, -80.5), 'OK': (33.6, 37.1, -103.1, -94.4),
    'OR': (41.9, 46.3, -124.6, -116.4), 'PA': (39.7, 42.3, -80.6, -74.7), 'RI': (41.1, 42.1, -71.9, -71.1),
    'SC': (32.0, 35.2, -83.4, -78.5), 'SD': (42.4, 46.0, -104.1, -96.4), 'TN': (34.9, 36.7, -90.4, -81.6),
    'TX': (25.8, 36.6, -106.7, -93.5), 'UT': (36.9, 42.1, -114.1, -109.0), 'VT': (42.7, 45.1, -73.5, -71.5),
    'VA': (36.5, 39.5, -83.7, -75.2), 'WA': (45.5, 49.1, -124.8, -116.9), 'WV': (37.2, 40.7, -82.7, -77.7),
    'WI': (42.5, 47.1, -92.9, -86.8), 'WY': (40.9, 45.1, -111.1, -104.0), 'DC': (38.8, 39.0, -77.2, -76.9),
    'AB': (49.0, 60.1, -120.1, -110.0), 'BC': (48.2, 60.1, -139.1, -114.0), 'ON': (41.6, 56.9, -95.2, -74.3),
    'QC': (45.0, 62.6, -79.8, -57.1),
}
STATE_NAME = {
    'alabama': 'AL', 'alaska': 'AK', 'arizona': 'AZ', 'arkansas': 'AR', 'california': 'CA', 'colorado': 'CO',
    'connecticut': 'CT', 'delaware': 'DE', 'florida': 'FL', 'georgia': 'GA', 'hawaii': 'HI', 'idaho': 'ID',
    'illinois': 'IL', 'indiana': 'IN', 'iowa': 'IA', 'kansas': 'KS', 'kentucky': 'KY', 'louisiana': 'LA',
    'maine': 'ME', 'maryland': 'MD', 'massachusetts': 'MA', 'michigan': 'MI', 'minnesota': 'MN',
    'mississippi': 'MS', 'missouri': 'MO', 'montana': 'MT', 'nebraska': 'NE', 'nevada': 'NV',
    'new hampshire': 'NH', 'new jersey': 'NJ', 'new mexico': 'NM', 'new york': 'NY', 'north carolina': 'NC',
    'north dakota': 'ND', 'ohio': 'OH', 'oklahoma': 'OK', 'oregon': 'OR', 'pennsylvania': 'PA',
    'rhode island': 'RI', 'south carolina': 'SC', 'south dakota': 'SD', 'tennessee': 'TN', 'texas': 'TX',
    'utah': 'UT', 'vermont': 'VT', 'virginia': 'VA', 'washington': 'WA', 'west virginia': 'WV',
    'wisconsin': 'WI', 'wyoming': 'WY',
}
MERC_R = 20037508.342789244


def clip(s, n=QUOTE_MAX):
    s = ' '.join(str(s or '').split())
    if len(s) <= n:
        return s
    cut = s[:n]
    for i in range(len(cut) - 1, 60, -1):
        if cut[i] in '.!?':
            return cut[:i + 1]
    comma = cut.rfind(',')
    if comma >= 80:
        return cut[:comma]
    sp = cut.rfind(' ')
    return cut[:sp] if sp > 40 else cut


def fp_of(text):
    return hashlib.sha256((text or '').encode('utf-8')).hexdigest()[:12]


def name_core(s):
    """Truth checker's core(), after the agency letters POTA writes into names are taken off."""
    t = AGENCY_LETTERS.sub(' ', str(s or ''))
    t = MGMT.sub(' ', t)
    return TB.core(t)


def norm_written(s):
    return ' '.join(re.sub(r'[^a-z0-9]+', ' ', str(s or '').lower()).split())


def canonical_kind(s):
    t = ' '.join(str(s or '').split())
    for k in KINDS:
        if t.lower() == k.lower():
            return k
    return t.title() if t else t


def kinds_in(name):
    found, spans = [], []
    for m in KIND_RX.finditer(name or ''):
        if any(not (m.end() <= a or m.start() >= b) for a, b in spans):
            continue
        spans.append((m.start(), m.end()))
        found.append(canonical_kind(m.group(1)))
    return found


def combined_of(name):
    """Two kinds joined by & / and / / in the page's own name. One-kind phrases do not count."""
    if not name:
        return False, []
    low = name.lower().replace('&', ' and ')
    masked = name
    for phrase in ONE_KIND:
        if phrase in low:
            masked = re.sub(re.escape(phrase), lambda m: ' ' * len(m.group(0)), masked, flags=re.I)
    m = COMBINED_RX.search(masked)
    if not m:
        return False, []
    a, b = canonical_kind(m.group('a')), m.group('b').strip()
    if not re.match(r'(?i)national|state', b):
        prefix = 'National' if a.lower().startswith('national') else 'State'
        b = prefix + ' ' + b
    b = canonical_kind(b)
    if a.lower() == b.lower():
        return False, []
    return True, [a, b]


def sig_words(s):
    return {w for w in re.findall(r'[a-z]+', str(s or '').lower()) if w not in FILLER and len(w) > 2}


def shares_word(kinds, pota_type):
    words = set()
    for k in kinds:
        words |= sig_words(k)
    return words & sig_words(pota_type)


def kind_matches_type(kind, pota_type):
    if not kind or not pota_type:
        return False
    return kind.lower() in pota_type.lower() or canonical_kind(kind).lower() in pota_type.lower()


def compare_names(best, pota_name):
    if not best:
        return 'differs'
    if norm_written(best) == norm_written(pota_name):
        return 'same'
    if name_core(best) and name_core(best) == name_core(pota_name):
        return 'same-core'
    return 'differs'


def cut_tail(s):
    return TAILS.sub('', str(s or '')).strip(' \t-•|')


def official_host(url):
    h = host_of(url or '')
    if not h:
        return False
    if gov_of(h):
        return True
    b = base_host(h)
    return b.endswith('.gov') or b.endswith('.mil') or b.endswith('.gc.ca') or '.gov.' in b


def split_urls(field):
    out = []
    for tok in str(field or '').split():
        if tok.startswith('www.'):
            tok = 'https://' + tok
        if tok.startswith('http://') or tok.startswith('https://'):
            out.append(tok.rstrip('.,);'))
    return out


def is_agency_home(url):
    try:
        import urllib.parse
        p = urllib.parse.urlparse(url or '')
    except Exception:
        return False
    path = (p.path or '').rstrip('/').lower()
    return path in ('', '/index.html', '/index.htm', '/home')


def script_shell(url):
    import urllib.parse
    h = (host_of(url or '') or '').lower()
    path = urllib.parse.urlparse(url or '').path.lower()
    if SCRIPT_HOST.search(h):
        return True
    if h.endswith('.maps.arcgis.com') and '/apps/' in path:
        return True
    return False


def family_of(url):
    h = base_host(host_of(url or ''))
    if h.endswith('nps.gov'):
        m = re.search(r'^/([a-z]{4})(/|$)', urllib_path(url))
        return {'id': 'nps', 'code': m.group(1) if m else '', 'facts': 'nps'}
    if h.endswith('blm.gov'):
        return {'id': 'blm', 'code': '', 'facts': ''}
    if h.endswith('fs.usda.gov') or h == 'usda.gov':
        return {'id': 'usfs', 'code': '', 'facts': 'about'}
    if h.endswith('fws.gov'):
        m = re.search(r'/refuge/([a-z0-9_-]+)', urllib_path(url))
        return {'id': 'fws', 'code': m.group(1) if m else '', 'facts': 'fws'}
    if h.endswith('usace.army.mil') or h.endswith('.army.mil'):
        return {'id': 'usace', 'code': '', 'facts': ''}
    return {'id': 'state' if official_host(url) else 'other', 'code': '', 'facts': ''}


def urllib_path(url):
    import urllib.parse
    return urllib.parse.urlparse(url or '').path or ''


def nps_facts_urls(code):
    if not code:
        return []
    return [f'https://www.nps.gov/{code}/learn/management/statistics.htm',
            f'https://www.nps.gov/{code}/planyourvisit/basicinfo.htm']


def fws_facts_urls(origin, slug):
    if not slug:
        return []
    return [f'{origin}/refuge/{slug}/about-us', f'{origin}/refuge/{slug}/visit-us']


def webmercator(x, y):
    lon = float(x) * 180.0 / MERC_R
    lat = math.atan(math.exp(float(y) * math.pi / MERC_R)) * 360.0 / math.pi - 90.0
    return lat, lon


def haversine_km(a, b):
    if not a or not b:
        return None
    r = 6371.0
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    dlat, dlon = la2 - la1, lo2 - lo1
    h = math.sin(dlat / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin(dlon / 2) ** 2
    return 2 * r * math.asin(min(1.0, math.sqrt(h)))


def area_code(area):
    parts = str(area or '').split('-')
    return parts[-1] if len(parts) >= 2 else ''


def point_ok(lat, lon, area, pin):
    try:
        lat, lon = float(lat), float(lon)
    except (TypeError, ValueError):
        return False
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return False
    box = BOX.get(area_code(area))
    inside = bool(box and box[0] <= lat <= box[1] and box[2] <= lon <= box[3])
    near = False
    if pin and pin[0] is not None:
        d = haversine_km((lat, lon), (pin[0], pin[1]))
        near = d is not None and d <= 300
    if box is None:
        return near or (pin is None)
    return inside or near


def _num(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def address_facts(url, park_name='', pin=None):
    """R-PR9. Facts written in the address. No request. Longitude is first in an ArcGIS marker."""
    import urllib.parse
    raw = urllib.parse.unquote(str(url or ''))
    coords = []
    def add(lat, lon, role, src, label=''):
        if lat is None or lon is None:
            return
        coords.append({'lat': round(lat, 5), 'lon': round(lon, 5), 'role': role, 'from': src,
                       'label': label, 'source': url})
    for m in re.finditer(r'marker[:=](-?\d+(?:\.\d+)?)\s*[, ]\s*(-?\d+(?:\.\d+)?)(?:;;([^,;#]*))?', raw, re.I):
        lon, lat = _num(m.group(1)), _num(m.group(2))
        label = ' '.join((m.group(3) or '').replace('+', ' ').split())
        role = 'unknown'
        if label and park_name and name_core(label) and name_core(label) == name_core(park_name):
            role = 'park'
        add(lat, lon, role, 'map-link marker', label)
    for m in re.finditer(r'center[:=](-?\d+(?:\.\d+)?)\s*[, ]\s*(-?\d+(?:\.\d+)?)(?:\s*[, ]\s*(102100))?', raw, re.I):
        a, b, wm = _num(m.group(1)), _num(m.group(2)), m.group(3)
        if wm or (a is not None and abs(a) > 180):
            lat, lon = webmercator(a, b)
            add(lat, lon, 'unknown', 'map-link center (Web Mercator)')
        else:
            # R-PR9: center=<lon>,<lat> (longitude first, as in an ArcGIS marker). 19 Nov (item 43 fault C): the old test turned
            # every point east of -90 around. Only a second number that cannot be a latitude means the page wrote lat,lon.
            if a is not None and b is not None and abs(b) > 90 and abs(a) <= 90:
                add(a, b, 'unknown', 'map-link center')
            else:
                add(b, a, 'unknown', 'map-link center')
    for m in re.finditer(r'@(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?),\d+(?:\.\d+)?z', raw):
        add(_num(m.group(1)), _num(m.group(2)), 'unknown', 'map-link @')
    q = urllib.parse.parse_qs(urllib.parse.urlparse(raw).query)
    for key, src in (('q', 'map-link q'), ('ll', 'map-link ll'), ('destination', 'map-link destination')):
        for val in q.get(key, []):
            mm = re.match(r'\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)', val)
            if mm:
                add(_num(mm.group(1)), _num(mm.group(2)), 'unknown', src)
    for m in re.finditer(r'[?&#]cp=(-?\d+(?:\.\d+)?)~(-?\d+(?:\.\d+)?)', raw):
        add(_num(m.group(1)), _num(m.group(2)), 'unknown', 'map-link bing')
    if pin and pin[0] is not None:
        for c in coords:
            d = haversine_km((c['lat'], c['lon']), (pin[0], pin[1]))
            c['km_from_pin'] = round(d, 2) if d is not None else None
    return {'coords': coords, 'requests_made': 0}


def _unescape(s):
    s = (s or '').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    s = s.replace('&#39;', "'").replace('&quot;', '"').replace('&nbsp;', ' ')
    return s


def is_menu_chrome(s):
    """A site or section menu (for example 'STATE PARKS MENU') is not a park name."""
    t = re.sub(r'\s+', ' ', str(s or '')).strip().strip('|-•').strip()
    if not t:
        return False
    return t.upper() == 'MENU' or 'MENU' in t.upper().split()


def _heading_and_title(html, text):
    title = heading = og = jname = ''
    if html and '<title' in html.lower():
        m = re.search(r'<title[^>]*>(.*?)</title>', html, re.I | re.S)
        title = _unescape(' '.join(re.sub(r'<[^>]+>', ' ', m.group(1)).split())) if m else ''
        title = cut_tail(title)
        if is_menu_chrome(title):
            title = ''
        for lv, inner in re.findall(r'<h([1-3])[^>]*>(.*?)</h\1>', html, re.I | re.S):
            cand = _unescape(' '.join(re.sub(r'<[^>]+>', ' ', inner).split()))
            cand = cut_tail(cand)
            if cand and not is_menu_chrome(cand):
                heading = cand
                break
        m = re.search(r'property=["\']og:title["\'][^>]*content=["\']([^"\']+)', html, re.I)
        if not m:
            m = re.search(r'content=["\']([^"\']+)["\'][^>]*property=["\']og:title["\']', html, re.I)
        og = m.group(1).strip() if m else ''
        for block in re.findall(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html, re.I | re.S):
            try:
                data = json.loads(block)
            except Exception:
                continue
            rows = data if isinstance(data, list) else [data]
            for row in rows:
                if isinstance(row, dict) and row.get('name'):
                    jname = str(row['name'])
                    break
    if not heading:
        for line in (text or '').splitlines():
            line = line.strip()
            if not line or line.lower().startswith('skip to'):
                continue
            if is_menu_chrome(cut_tail(line)) or is_menu_chrome(line):
                continue
            if '|' in line or '•' in line:
                title = title or line
                heading = cut_tail(line)
                break
            if kinds_in(line) and len(line) < 120:
                heading = line
                title = title or line
                break
    return title, heading, og, jname


CHROME = re.compile(r'^(?:welcome to(?: the)?|home)\b[\s|:-]*', re.I)


def strip_chrome(s):
    """A site tail, then a leading 'Welcome to' or 'Home'. The park's name is what remains."""
    t = cut_tail(s or '')
    t = CHROME.sub('', t).strip(' |-')
    # a title often keeps a second 'Home |' after the first tail is cut
    t = re.sub(r'^(?:home)\b[\s|:-]*', '', t, flags=re.I).strip(' |-')
    return t


def best_name_of(title, heading, og, jname):
    """R-PR2. Heading first. Site tails are cut. Heading and title that disagree: best is null."""
    if is_menu_chrome(title or ''):
        title = ''
    if is_menu_chrome(heading or ''):
        heading = ''
    if is_menu_chrome(og or ''):
        og = ''
    raw_title = title or og or ''
    h = strip_chrome(heading or '')
    t = strip_chrome(raw_title)
    o = strip_chrome(og or '')
    j = strip_chrome(jname or '')
    if is_menu_chrome(h):
        h = ''
    if is_menu_chrome(t):
        t = ''
    # keep a heading that still names a place; a bare 'Welcome' is not a name
    if h and not (kinds_in(h) or len(h.split()) >= 2):
        h = ''
    if h and t and name_core(h) and name_core(t) and name_core(h) != name_core(t):
        return {'title': raw_title or heading, 'heading': h, 'best': None, 'og': o, 'jsonld': j,
                'quote': clip(raw_title or h), 'disagree': True}
    best = h or t or o or j or None
    return {'title': raw_title or (heading or ''), 'heading': h or t or '', 'best': best, 'og': o,
            'jsonld': j, 'quote': clip(raw_title or h or best or ''), 'disagree': False}


def find_other_part(area_parks, ref, page_name, parts, my_type):
    if len(parts) != 2:
        return None
    other = None
    for p in parts:
        if not kind_matches_type(p, my_type):
            other = p
    if other is None:
        other = parts[1]
    core = name_core(page_name)
    if not core:
        return None
    hits = []
    for r, row in area_parks.items():
        if r == ref:
            continue
        if name_core(row.get('name')) != core:
            continue
        if kind_matches_type(other, row.get('type')):
            hits.append(r)
    return hits[0] if len(hits) == 1 else None


def _sentence(text, start):
    a = text.rfind('\n', 0, start)
    b = text.find('\n', start)
    chunk = text[a + 1: b if b >= 0 else len(text)]
    # also stop at a period that ends the sentence
    rel = start - (a + 1)
    left = chunk[:rel]
    dots = list(re.finditer(r'[.!?]\s', left))
    if dots:
        left = left[dots[-1].end():]
    right = chunk[rel:]
    m = re.search(r'[.!?]', right)
    right = right[:m.end()] if m else right
    return ' '.join((left + right).split())


SELF_LEAD = re.compile(r"^\s*(?:[A-Z][a-z]+,\s*)?(?:this|it|we|our|here)\b", re.I)
SELF_THIS = re.compile(r"\bthis\s+[\w-]+", re.I)
SELF_THE = re.compile(r"^\s*(?:[A-Z][a-z]+,\s*)?the\s+(?:park|area|site|refuge|preserve|property|unit|reserve|monument|place|"
                      r"sanctuary|recreation area|wildlife area|management area)\b", re.I)


def _about_this_place(words, park_name):
    """R-PR4: do these words (the start of the sentence) say the subject is this park?"""
    w = ' '.join(str(words or '').split())
    if not w:
        return False
    core = name_core(park_name)
    if core and all(t in name_core(w).split() for t in core.split()):
        return True
    if SELF_LEAD.search(w) or SELF_THE.search(w) and len(w.split()) <= 8:
        return True
    return bool(SELF_THIS.search(w)) and len(w.split()) <= 10


def inside_units(text, park_name):
    """R-PR4. A sentence about THIS place. A trail, a rule line, history, and plain geography do not count."""
    found, maybe = [], []
    for m in INSIDE_RX.finditer(text or ''):
        name = ' '.join(m.group('name').split())
        kind = ''
        ks = kinds_in(name)
        kind = ks[-1] if ks else ''
        sent = _sentence(text, m.start())
        if NOT_GEO.search(name) or NOT_GEO.search(sent):
            continue
        if HISTORY_IN.search(sent) or RULE_LINE.search(sent):
            continue
        left = sent[:max(0, sent.lower().find(name.lower()))]
        if BAD_SUBJECT.search(left):
            maybe.append({'unit': name, 'quote': clip(sent), 'why': 'the subject is a trail, campground, or visitor place'})
            continue
        # 19 Nov (Opus, item 43 fault B): a park is never inside itself. Same core and a kind the park's own name has = this park.
        if park_name and name_core(name) and name_core(name) == name_core(park_name):
            own_kinds = {k.lower() for k in kinds_in(park_name)}
            if own_kinds & {k.lower() for k in kinds_in(name)}:
                continue
            if not own_kinds:
                maybe.append({'unit': name, 'quote': clip(sent), 'why': 'the unit may be this park itself'})
                continue
        # 19 Nov (Opus, item 43 fault A): R-PR4 counts a sentence about THIS place only. The words before the unit must name
        # this park (its core), or say 'this ...', 'it', 'we', 'our', or 'the park / area / site ...'. A river, a neighbour
        # park or another subject goes to maybe_inside for a person.
        # the subject is what stands before the FIRST 'within the / part of the ...' of the sentence (two units share it)
        first = INSIDE_RX.search(sent)
        lead = sent[:first.start()] if first else left
        rest = sent[first.end():] if first else sent[len(left) + len(name):]
        if not _about_this_place(lead, park_name) and not (not lead.strip(' ,') and _about_this_place(rest.lstrip(' ,'), park_name)):
            maybe.append({'unit': name, 'quote': clip(sent), 'why': 'the sentence is not about this park'})
            continue
        # the name must end in a kind (the regex already requires it)
        if not kind:
            maybe.append({'unit': name, 'quote': clip(sent), 'why': 'no kind word'})
            continue
        found.append({'unit': name, 'kind': kind, 'quote': clip(sent), 'how': m.group('how').lower()})
    # two different units: store neither as fact
    units = []
    for row in found:
        if not any(name_core(row['unit']) == name_core(u['unit']) for u in units):
            units.append(row)
    if len(units) >= 2:
        return [], [{'unit': u['unit'], 'quote': u['quote'], 'why': 'two readings'} for u in units]
    return units, [m for m in maybe if m.get('why') != 'no kind word']


def match_unit_ref(area_parks, unit, kind, exclude=None):
    core = name_core(unit)
    if not core:
        return None
    hits = []
    for r, row in area_parks.items():
        if exclude and r == exclude:   # 19 Nov (item 43 fault B): never the park's own number
            continue
        if name_core(row.get('name')) != core:
            continue
        if kind and kind_matches_type(kind, row.get('type')):
            hits.append(r)
    return hits[0] if len(hits) == 1 else None


def _restore_truth(desig, cores):
    TB.DESIG.clear()
    TB.DESIG.update(desig)
    TB.OTHER_CORES.clear()
    TB.OTHER_CORES.update(cores)


def sizes_labelled(text, name, pota_type):
    """R-PR5. sizes_in, plus the label on a labelled line, plus round words kept as said."""
    old_d, old_c = dict(TB.DESIG), set(TB.OTHER_CORES)
    national = bool(re.search(r'\bnational\b', pota_type or '', re.I))
    state = bool(re.search(r'\bstate\b', pota_type or '', re.I)) and not national
    TB.DESIG.clear()
    TB.DESIG.update({'state': state, 'national': national})
    try:
        rows = TB.sizes_in(text or '', name or '')
    finally:
        _restore_truth(old_d, old_c)
    out = []
    used_spans = []
    for s in rows:
        num = str(s.get('as') or '').split()[0]
        idx = (text or '').find(num) if num else -1
        # skip a second hit of the same digits (the truth reader sometimes returns a twin)
        if any(round(s['acres']) == round(prev) and abs((idx or 0) - pidx) < 24 for prev, pidx in used_spans):
            continue
        label, why, total, clean = '', s.get('why') or '', bool(s.get('total')), bool(s.get('clean'))
        said = s.get('as') or ''
        if idx >= 0:
            prefix = text[text.rfind('\n', 0, idx) + 1:idx]
            lm = LABEL_RX.search(prefix[-50:])
            window = text[idx:idx + 90]
            if lm:
                label = 'Total area' if lm.group(1).lower() == 'total area' else lm.group(1).title()
            # "including 2,146,270 acres of wilderness" is a part of the number before it, not a total
            if INCLUDING.search(prefix[-24:]):
                label = 'Wilderness' if WILD_AFTER.search(window) else (label or 'included')
                total, clean = False, False
                why = 'part (included in the figure beside it)'
            rm = ROUND_RX.search(text[max(0, idx - 24):idx + len(num) + 16])
            if rm:
                said = ' '.join(rm.group(1).split())
                clean = False
        # a converted twin of a number on the same line (9,492 square miles beside the acre total)
        if re.search(r'square\s+miles|sq\.?\s*mi', said, re.I):
            if any(abs(s['acres'] - o['acres']) / max(o['acres'], 1) < 0.01 for o in out):
                continue
        out.append({'acres': s['acres'], 'as': said, 'label': label, 'line': clip(s.get('line') or said),
                    'quote': clip(s.get('sent') or s.get('line') or said), 'total': total, 'clean': clean, 'why': why})
        used_spans.append((s['acres'], idx if idx >= 0 else -99999))
        if len(out) >= 12:
            break
    # round phrases sizes_in does not see ("2.4-million-acre")
    have = {round(o['acres']) for o in out}
    for m in ROUND_RX.finditer(text or ''):
        phrase = ' '.join(m.group(1).split())
        acres = _round_acres(phrase)
        if acres is None or round(acres) in have:
            # still mark an existing row not clean
            for o in out:
                if acres is not None and round(o['acres']) == round(acres):
                    o['clean'] = False
                    o['as'] = phrase
            continue
        out.append({'acres': acres, 'as': phrase, 'label': '', 'line': clip(_sentence(text, m.start())),
                    'quote': clip(_sentence(text, m.start())), 'total': False, 'clean': False,
                    'why': 'round words, kept as said'})
        have.add(round(acres))
    return out


def _round_acres(phrase):
    m = re.search(r'(\d+(?:\.\d+)?)\s*\+?\s*-?\s*million', phrase, re.I)
    if m:
        return float(m.group(1)) * 1_000_000
    if re.search(r'million', phrase, re.I):
        return None
    m = re.search(r'[\d,]+', phrase)
    if not m:
        return None
    try:
        return float(m.group(0).replace(',', ''))
    except ValueError:
        return None


def _section(text, names):
    lines = (text or '').splitlines()
    take = False
    buf = []
    for line in lines:
        key = line.strip().lower().rstrip(':')
        if key in HEADS or key in names:
            if take:
                break
            if key in names:
                take = True
                continue
        elif take and key in HEADS:
            break
        if take:
            buf.append(line)
    return '\n'.join(buf).strip()


def addresses_in(text):
    """R-PR7. A street or a P.O. box. The role comes from the heading and the words, never from a geocoder."""
    out = []
    block = _section(text, {'addresses', 'address', 'mailing address', 'location'})
    chunks = [('addresses', block)] if block else []
    # a one-line office address with no heading
    for m in re.finditer(r'.{0,80}(?:P\.?\s*O\.?\s*Box\s+\d+).{0,80}\d{5}', text or '', re.I):
        chunks.append(('line', m.group(0)))
    for m in re.finditer(r'.{0,60}\d{1,6}\s+[A-Z][\w.\'-]+(?:\s+[A-Z0-9][\w.\'-]+){0,5}\s+'
                         r'(?:Ave|Avenue|St|Street|Rd|Road|Dr|Drive|Blvd|Hwy|Highway|Way|Lane)\.?'
                         r'\s+[A-Z][\w.\'-]+(?:\s+[A-Z][\w.\'-]+){0,2},?\s+[A-Z]{2}\s+\d{5}', text or ''):
        chunks.append(('line', m.group(0)))
    seen = set()
    for how, chunk in chunks:
        if not chunk:
            continue
        role, why = _addr_role(chunk, how)
        text_one = ' '.join(chunk.split())
        # prefer a short address, not the whole directions
        if len(text_one) > 180 and how == 'addresses':
            text_one = _tight_address(chunk) or text_one[:180]
        key = norm_written(text_one)[:80]
        if key in seen or not (ZIP_RX.search(text_one) or PO_RX.search(text_one)):
            continue
        if not (STREET_WORD.search(text_one) or PO_RX.search(text_one)):
            continue
        seen.add(key)
        out.append({'text': clip(text_one, 160), 'role': role, 'why': why})
    return out[:6]


def _tight_address(block):
    lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
    for i, ln in enumerate(lines):
        if STREET_WORD.search(ln) or PO_RX.search(ln):
            window = lines[max(0, i - 1):i + 4]
            joined = ' '.join(window)
            if ZIP_RX.search(joined):
                return joined
    return ''


def _addr_role(blob, how):
    b = blob.lower()
    if re.search(r'visitor cent', b):
        return 'visitor-centre', "the words say visitor center"
    if OFFICE_WORD.search(b):
        if re.search(r'\bmailing\b', b) or (PO_RX.search(blob) and not re.search(r'field office|headquarters|supervisor', b)):
            return 'mailing', "a P.O. box or the word mailing"
        return 'office', "under the address heading; the words name an office"
    if how == 'addresses' and PARK_ADDR.search(b):
        return 'park', "the heading says location or park address"
    if PARK_ADDR.search(b) and how == 'location':
        return 'park', "the heading says location"
    return 'unknown', "a street and a ZIP, with no office or park word"


def directions_of(text):
    block = _section(text, {'directions', 'getting here', 'how to get there', 'driving directions'})
    if not block:
        return None
    sent = clip(block, 400)
    roads, seen = [], set()
    for rx in ROAD_RX:
        for m in rx.finditer(block):
            name = ' '.join(m.group(0).split())
            k = name.lower()
            if k in seen:
                continue
            # a state-route match on a word like "AT-1" inside another token is already bounded
            if re.fullmatch(r'[A-Z]{2}-\d+', name) and name[:2] not in (
                    'US', 'SR', 'UT', 'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID',
                    'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE',
                    'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN',
                    'TX', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY', 'NC'):
                continue
            seen.add(k)
            roads.append(name)
    towns, seen_t = [], set()
    for rx in (TOWN_RX, SLASH_TOWN):
        for m in rx.finditer(block):
            town = m.group(1).strip()
            if town.split()[0] in TOWN_SKIP:
                continue
            if town.lower() in seen_t:
                continue
            seen_t.add(town.lower())
            towns.append(town)
    return {'sent': sent, 'roads': roads[:12], 'towns': towns[:8]}


def tracts_in(text):
    """R-PR8. Two or more proper names followed by a tract word. Nearby attractions and legend lines do not count."""
    found, seen = [], set()
    for rx in (TRACT_RX, AREA_N_RX):
        for m in rx.finditer(text or ''):
            sent = _sentence(text, m.start())
            if TRACT_SKIP.search(sent):
                continue
            if rx is AREA_N_RX:
                name = f"{m.group(1)} Area {m.group(2)}"
            else:
                name = f"{m.group(1)} {m.group(2)}"
            name = ' '.join(name.split())
            if len(name.split()) > 6:
                continue
            if name.lower() in seen:
                continue
            seen.add(name.lower())
            found.append(name)
    return found


def status_of(text):
    """Closed, handed over, renamed. An ordinary 'managed by' is the manager, not a status."""
    out = {'closed': None, 'handover': None, 'renamed': None}
    for key, rx in (('closed', TB.CLOSED), ('handover', TB.HANDOVER), ('renamed', TB.NEWNAME)):
        m = rx.search(text or '')
        if m:
            out[key] = clip(m.group(1) if m.lastindex else m.group(0))
    return out


def manager_of(text, host):
    agency = ''
    h = base_host(host_of(host or '') if '://' in str(host or '') else (host or ''))
    if h.endswith('nps.gov'):
        agency = 'National Park Service'
    elif h.endswith('blm.gov'):
        agency = 'Bureau of Land Management'
    elif 'usda.gov' in h:
        agency = 'Forest Service'
    elif h.endswith('fws.gov'):
        agency = 'Fish and Wildlife Service'
    elif 'army.mil' in h:
        agency = 'Army Corps of Engineers'
    m = TB.MANAGED.search(text or '')
    quote = clip(m.group(1)) if m else ''
    office = ''
    om = re.search(r'\b([A-Z][\w.\'-]+(?:\s+[A-Z][\w.\'-]+){0,4}\s+'
                   r'(?:Field Office|District Office|Ranger District|Supervisor\'?s Office|Headquarters))\b', text or '')
    if om:
        office = om.group(1)
    elif m:
        office = clip(m.group(1), 80)
    if not (agency or office or quote):
        return None
    return {'agency': agency, 'office': office, 'quote': quote}


def html_coords(html, text):
    """JSON-LD geo, meta tags, then a labelled line. Map-link points are added by the caller."""
    out = []
    def add(lat, lon, src, role='unknown'):
        lat, lon = _num(lat), _num(lon)
        if lat is None or lon is None:
            return
        out.append({'lat': lat, 'lon': lon, 'from': src, 'role': role, 'label': ''})
    for block in re.findall(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html or '', re.I | re.S):
        try:
            data = json.loads(block)
        except Exception:
            continue
        rows = data if isinstance(data, list) else [data]
        for row in rows:
            if not isinstance(row, dict):
                continue
            geo = row.get('geo') or {}
            if isinstance(geo, dict) and ('latitude' in geo or 'lat' in geo):
                add(geo.get('latitude', geo.get('lat')), geo.get('longitude', geo.get('lon')), 'json-ld')
    if html:
        lat = re.search(r'place:location:latitude["\']?\s*content=["\']([^"\']+)', html, re.I)
        lon = re.search(r'place:location:longitude["\']?\s*content=["\']([^"\']+)', html, re.I)
        if lat and lon:
            add(lat.group(1), lon.group(1), 'meta')
        pos = re.search(r'name=["\']geo\.position["\'][^>]*content=["\']([^"\']+)', html, re.I)
        if pos and ';' in pos.group(1):
            a, b = pos.group(1).split(';', 1)
            add(a, b, 'meta geo.position')
        icbm = re.search(r'name=["\']ICBM["\'][^>]*content=["\']([^"\']+)', html, re.I)
        if icbm and ',' in icbm.group(1):
            a, b = icbm.group(1).split(',', 1)
            add(a, b, 'meta ICBM')
    for m in re.finditer(r'(Geographic Coordinates|GPS|Lat\s*/\s*Long)\s*[:\s]+(-?\d{1,3}\.\d+)\s*[,/]\s*(-?\d{1,3}\.\d+)',
                         text or '', re.I):
        add(m.group(2), m.group(3), 'labelled line', 'park')
    return out


def classify_link(url, text, park_name, agency_host):
    """A map link, judged by the documents bot's map_score. Kind is only the file type."""
    import kpc_docs_bot as DB
    old = dict(DB.CUR)
    DB.CUR.clear()
    DB.CUR.update({'type': '', 'name': park_name or ''})
    try:
        score = map_score(url, text or '', agency_host or '')
    finally:
        DB.CUR.clear()
        DB.CUR.update(old)
    u = (url or '').lower()
    if u.endswith('.pdf') or '.pdf' in u.split('?')[0]:
        kind = 'pdf'
    elif re.search(r'\.(jpe?g|png|gif)(\?|$)', u):
        kind = 'image'
    elif re.search(r'\.(kml|kmz|geojson)(\?|$)', u) or 'featureserver' in u or '/rest/services/' in u:
        kind = 'gis'
    elif script_shell(url) or 'arcgis' in u or 'maps' in u:
        kind = 'web-map'
    else:
        kind = 'web-map'
    words = (text or '') + ' ' + url
    looks = bool(re.search(r'\bmaps?\b|brochure|boundary|\bgis\b|view map', words, re.I)) or kind in ('pdf', 'gis', 'image')
    if score < 0 and not (looks and kind == 'web-map'):
        return None
    if score < 0 and kind != 'web-map':
        return None
    # map_score rejects experience.arcgis.com (it is a viewer). R-PR8 still lists a map app.
    if score < 0 and not script_shell(url) and 'arcgis' not in u:
        return None
    via = via_of(url, agency_host or '', {url}, 'on the page')
    return {'url': url, 'text': text or '', 'kind': kind, 'score': score, 'via': via}


def names_park_link(url, text, park_name, marker_label=''):
    if marker_label and name_core(marker_label) == name_core(park_name):
        return True, ''
    blob = (text or '') + ' ' + (url or '')
    # a different unit's kind in the file name (NCA, refuge) means this is that unit's map
    file_kinds = kinds_in(re.sub(r'[_\-]+', ' ', url or ''))
    park_kinds = kinds_in(park_name or '')
    if file_kinds and park_kinds and not any(k in park_kinds for k in file_kinds):
        return False, ' '.join(file_kinds) + ' (file name)'
    if name_core(park_name) and name_core(park_name) in name_core(blob):
        return True, ''
    return False, ''


def no_single_point(pota_type, page_name=''):
    return bool(NO_POINT.search((pota_type or '') + ' ' + (page_name or '')))


def questions_for(fact):
    """Plain one-line questions. A question is not an answer."""
    qs = []
    def add(code, plain, quote, who='reviewer'):
        qs.append({'code': code, 'for': who, 'plain': plain, 'quote': clip(quote or plain)})
    d = fact.get('designation') or {}
    if d.get('combined'):
        part = (d.get('parts') or ['the other part'])[-1]
        name = (fact.get('name') or {}).get('best') or (fact.get('name') or {}).get('heading') or ''
        if d.get('pota_numbers_part'):
            add('COMBINED_BOTH_NUMBERED',
                f"The page covers '{name}'. POTA lists the {part} as {d['pota_numbers_part']}.",
                name, 'information')
        else:
            add('COMBINED_UNIT',
                f"The page calls this '{name}'. POTA lists no separate park for the {part} here.",
                name)
    for row in fact.get('inside_of') or []:
        extra = f" (POTA {row['pota_ref']})" if row.get('pota_ref') else ''
        add('INSIDE_BIGGER_UNIT', f"The page says this place is within '{row['unit']}'{extra}.", row.get('quote'))
    if (fact.get('name') or {}).get('vs_pota') == 'differs' or (fact.get('name') or {}).get('disagree'):
        add('NAME_DIFFERS',
            f"POTA: '{fact.get('pota', {}).get('name', '')}'. Page: '{(fact.get('name') or {}).get('heading') or (fact.get('name') or {}).get('title') or ''}'.",
            (fact.get('name') or {}).get('quote'))
    if d.get('vs_pota_type') == 'differs':
        add('DESIGNATION_DIFFERS',
            f"POTA says '{fact.get('pota', {}).get('type', '')}'. The page says '{', '.join(d.get('words') or [])}'.",
            (fact.get('name') or {}).get('quote'))
    own = fact.get('own_page') or {}
    if own.get('is') == 'shared':
        refs = own.get('shared_with') or []
        add('SHARED_PAGE', f"{len(refs) + 1} parks use this page: {', '.join([fact['ref']] + refs)}.",
            own.get('why'), 'information')
    if own.get('is') == 'agency-home':
        add('AGENCY_HOME_ONLY', "POTA's link is the agency's front page, not this park's page. Nothing was read from it.",
            fact.get('asked', {}).get('url'), 'person')
    if own.get('is') == 'unofficial-host':
        add('UNOFFICIAL_HOST', f"The link is not an agency page ({own.get('host')}). Facts from it are marked unofficial.",
            fact.get('asked', {}).get('url'), 'information')
    if own.get('is') == 'list':
        add('AGENCY_HOME_ONLY', "POTA's link is a list of parks, not this park's page. Nothing was read from it.",
            fact.get('asked', {}).get('url'), 'person')
    addrs = (fact.get('location') or {}).get('addresses') or []
    if addrs and all(a.get('role') in ('office', 'mailing') for a in addrs):
        office = ''
        for a in addrs:
            m = re.search(r'([A-Z][\w.\'-]+(?:\s+[A-Z][\w.\'-]+){0,4}\s+(?:Field Office|District Office|Supervisor\'?s Office|Headquarters))', a.get('text') or '')
            if m:
                office = m.group(1)
                break
        office = office or 'office'
        add('OFFICE_ADDRESS_ONLY', f"The only address on the page is the {office}, not the park.",
            addrs[0].get('text'), 'information')
    for c in (fact.get('location') or {}).get('coords') or []:
        if c.get('role') == 'park' and c.get('pin_far'):
            add('PIN_FAR_FROM_PAGE', f"The page's map point is {c.get('km_from_pin')} km from POTA's pin.",
                c.get('source') or '', 'reviewer')
            break
    labels = []
    for s in fact.get('sizes') or []:
        if s.get('label') and s['label'] not in [x[0] for x in labels]:
            labels.append((s['label'], s.get('as') or s.get('acres')))
    if len(labels) >= 2:
        bits = ', '.join(f"{a} {b}" for a, b in labels[:6])
        add('SIZE_LISTED_BY_PART', f"The page gives sizes by part: {bits}.",
            (fact.get('sizes') or [{}])[0].get('quote'), 'information')
    parts = fact.get('parts') or []
    if len(parts) >= 2:
        add('MANY_TRACTS', f"{len(parts)} named tracts: {', '.join(parts[:8])}.", ', '.join(parts[:8]))
    page = fact.get('page') or {}
    if page.get('moved'):
        add('LINK_MOVED', f"The link now lands on {page.get('final_host')}.", page.get('final_url'), 'information')
    if page.get('kind') == 'dead' and page.get('dead_twice'):
        add('LINK_DEAD', "The link does not open.", page.get('final_url') or fact.get('asked', {}).get('url'), 'person')
    if page.get('kind') in ('refused', 'robots'):
        add('REFUSED', "The site does not take automated visitors. For a person.",
            fact.get('asked', {}).get('url'), 'person')
    if page.get('kind') == 'script-built':
        add('SCRIPT_BUILT', "The page builds itself in the browser. For a person or a browser run.",
            fact.get('asked', {}).get('url'), 'person')
    if page.get('kind') == 'none' and own.get('is') not in ('agency-home', 'list'):
        add('NO_PAGE', "No page on file for this park.", '', 'person')
    st = fact.get('status_words') or {}
    for key in ('closed', 'handover', 'renamed'):
        if st.get(key):
            add('CLOSED_OR_MOVED_WORDS', st[key], st[key])
            break
    # cap quotes: 12 per park, counting these question quotes plus the fact quotes already stored
    return qs[:12]


def evidence_drafts(fact):
    want = {'COMBINED_UNIT', 'INSIDE_BIGGER_UNIT', 'MANY_TRACTS', 'SIZE_LISTED_BY_PART'}
    rows = []
    for q in fact.get('questions') or []:
        if q['code'] not in want:
            continue
        rows.append({'ref': fact['ref'], 'who': 'bot: park page reader v1', 'source': (fact.get('page') or {}).get('final_url')
                     or (fact.get('asked') or {}).get('url') or '', 'saw': q.get('quote') or '',
                     'date': (fact.get('page') or {}).get('read') or '', 'question': q['code'], 'draft': True})
    return rows


def visible_of(body, headers, url, extra_links=None):
    """Turn a fetched body into text, a title, and links. HTML, plain text, or a PDF."""
    raw = body if isinstance(body, str) else (body or b'').decode('utf-8', 'replace')
    ctype = ''
    if isinstance(headers, dict):
        ctype = str(headers.get('content-type') or headers.get('Content-Type') or '')
    links = list(extra_links or [])
    is_pdf = 'pdf' in ctype.lower() or urllib_path(url).lower().endswith('.pdf')
    if is_pdf:
        text = pdf_text(body if isinstance(body, (bytes, bytearray)) else raw.encode('utf-8', 'replace'), pages=2)
        if not text.strip():
            text = raw
        return {'text': text, 'html': '', 'title': '', 'heading': '', 'links': links, 'pdf': True}
    if raw.lstrip().startswith('<') or '<html' in raw[:500].lower() or '<title' in raw[:800].lower():
        text = page_text(raw)
        links = links_in(raw, url) + [lk for lk in links if lk[0] not in {u for u, _ in links_in(raw, url)}]
        title, heading, og, jname = _heading_and_title(raw, text)
        return {'text': text, 'html': raw, 'title': title, 'heading': heading, 'og': og, 'jsonld': jname,
                'links': links, 'pdf': False}
    # plain text the owner saved, or a fixture. A bare URL line is a link; the line above is its text.
    lines = raw.splitlines()
    for i, line in enumerate(lines):
        m = re.search(r'https?://\S+', line)
        if m:
            prev = lines[i - 1].strip() if i else ''
            links.append((m.group(0).rstrip('.,);'), prev[:120]))
    title, heading, og, jname = _heading_and_title('', raw)
    return {'text': raw, 'html': '', 'title': title, 'heading': heading, 'og': og, 'jsonld': jname,
            'links': links, 'pdf': False}


def _blank_location():
    return {'coords': [], 'dropped_points': 0, 'addresses': [], 'directions': None, 'state_words': []}


def build_facts(ref, area, pota, area_parks, asked, pages, today, shared_with, own_is, own_why, read_blocks=True):
    """One park's facts from pages already fetched. read_blocks False stores nothing but the reason."""
    pin = pota.get('pin') or [None, None]
    main = pages[0] if pages else {}
    text = '\n'.join(p.get('text') or '' for p in pages)
    main_text = (main.get('text') or '') if read_blocks else ''
    title = main.get('title') or ''
    heading = main.get('heading') or ''
    if not heading and not title and main_text:
        title, heading, og, jname = _heading_and_title(main.get('html') or '', main_text)
    else:
        og, jname = main.get('og') or '', main.get('jsonld') or ''
    # a shared page: the heading names THIS park only when the cores meet and the kinds fit
    name = best_name_of(title, heading, og, jname) if read_blocks else {'title': '', 'heading': '', 'best': None, 'quote': '', 'disagree': False}
    if read_blocks and name.get('best') and shared_with:
        h_core, p_core = name_core(name['best']), name_core(pota.get('name'))
        h_kinds = set(kinds_in(name['best']))
        t_words = sig_words(pota.get('type'))
        k_words = set()
        for k in h_kinds:
            k_words |= sig_words(k)
        if h_core and p_core and h_core != p_core and not (k_words & t_words):
            # the heading is a sibling unit. Use a mention of THIS park's kind, or stay silent.
            mention = _mention_of(main_text, pota.get('name'), pota.get('type'))
            if mention:
                name = {'title': title, 'heading': mention, 'best': mention, 'quote': clip(mention), 'disagree': False}
            else:
                name = {'title': title, 'heading': heading, 'best': None, 'quote': clip(title or heading), 'disagree': False,
                        'sibling_heading': True}
    if read_blocks and (main.get('kind') == 'script-built' or (main.get('thin') and script_shell(asked.get('url') or ''))):
        # an empty app shell: invent nothing
        name = {'title': '', 'heading': '', 'best': None, 'quote': '', 'disagree': False}
        main_text = ''
        text = ''
    name['vs_pota'] = compare_names(name.get('best'), pota.get('name')) if name.get('best') else ('differs' if name.get('disagree') else None)
    words = kinds_in(name.get('best') or '') if name.get('best') else []
    combined, parts = combined_of(name.get('best') or '') if name.get('best') else (False, [])
    if combined:
        words = parts
    other_ref = find_other_part(area_parks, ref, name.get('best') or '', parts, pota.get('type')) if combined else None
    share = shares_word(words, pota.get('type'))
    if not words:
        vs_type = None
    elif share:
        shown = ' ... '.join(w.title() for w in sorted(share))
        vs_type = f'shares a word ({shown})'
    else:
        vs_type = 'differs'
    designation = {'words': words, 'combined': combined, 'parts': parts if combined else [],
                   'pota_numbers_part': other_ref if combined else None, 'vs_pota_type': vs_type}
    unofficial = own_is == 'unofficial-host'
    inside, maybe = ([], [])
    contains = []
    sizes = []
    if read_blocks and main_text and not unofficial:
        inside, maybe = inside_units(main_text, pota.get('name'))
        for row in inside:
            row['pota_ref'] = match_unit_ref(area_parks, row['unit'], row.get('kind'), exclude=ref)
        sizes = []
        for p in pages:
            if p.get('kind') == 'script-built':
                continue
            sizes.extend(sizes_labelled(p.get('text') or '', pota.get('name') or name.get('best') or '', pota.get('type') or ''))
        sizes = _dedupe_sizes(sizes)
    elif read_blocks and unofficial and name.get('best'):
        pass
    loc = _blank_location()
    maps, part_names = [], []
    if read_blocks and main_text and not unofficial:
        loc = _location(main, pages, pota, area, pin)
        if no_single_point(pota.get('type'), name.get('best') or ''):
            loc['coords'] = [c for c in loc['coords'] if c.get('role') == 'office']
        maps = _maps(main, pota, pages)
        blob = '\n'.join(p.get('text') or '' for p in pages)
        part_names = tracts_in(blob)
    elif read_blocks and not unofficial:
        loc = _blank_location()
    status = status_of(main_text) if read_blocks and not unofficial else {'closed': None, 'handover': None, 'renamed': None}
    mgr = manager_of(main_text, (main.get('final') or asked.get('url') or '')) if read_blocks else None
    page = _page_block(main, asked, today)
    fact = {
        'ref': ref, 'area': area, 'reader': READER,
        'pota': {'name': pota.get('name'), 'type': pota.get('type'), 'pin': list(pin) if pin[0] is not None else None,
                 'link': pota.get('link'), 'qsos': pota.get('qsos')},
        'asked': {'url': asked.get('url') or '', 'from': asked.get('from') or '', 'others_noted': asked.get('others_noted') or 0},
        'page': page,
        'own_page': {'is': own_is, 'why': own_why, 'shared_with': list(shared_with or []),
                     'host': host_of(asked.get('url') or '') or ''},
        'name': {k: name.get(k) for k in ('title', 'heading', 'best', 'vs_pota', 'quote') if k in name or True},
        'designation': designation,
        'inside_of': [{k: r[k] for k in ('unit', 'kind', 'pota_ref', 'quote') if k in r or k == 'pota_ref'} for r in inside],
        'maybe_inside': maybe,
        'contains': contains,
        'sizes': sizes if not unofficial else [],
        'location': loc if not unofficial else _blank_location(),
        'maps': maps,
        'parts': part_names,
        'manager': mgr,
        'status_words': status,
        'unofficial': unofficial,
    }
    fact['name']['vs_pota'] = name.get('vs_pota')
    fact['questions'] = questions_for(fact)
    drafts = evidence_drafts(fact)
    fact['evidence_draft'] = drafts[0] if drafts else None
    fact['evidence_drafts'] = drafts
    return fact


def _mention_of(text, pota_name, pota_type):
    """A phrase on the page that names THIS park, when the heading names a sibling."""
    if pota_name and re.search(re.escape(pota_name), text or '', re.I):
        return pota_name
    kinds = kinds_in(pota_type or '')
    core = name_core(pota_name)
    if not core or not kinds:
        return ''
    # "Aniakchak Wild and Scenic River" on a monument page
    m = re.search(r'\b([A-Z][\w\'’.-]*(?:\s+[A-Z][\w\'’.-]*){0,4}\s+' + re.escape(kinds[-1]) + r')\b', text or '')
    if m and core.split()[0] in name_core(m.group(1)):
        phrase = m.group(1)
        if not combined_of(phrase)[0]:
            return phrase
    return ''


def _dedupe_sizes(rows):
    out, seen = [], set()
    for s in rows:
        key = (round(s['acres']), s.get('label') or '', (s.get('as') or '')[:40])
        if key in seen:
            continue
        seen.add(key)
        out.append(s)
    return out[:12]


def _page_block(main, asked, today):
    final = main.get('final') or asked.get('url') or ''
    asked_h = host_of(asked.get('url') or '')
    final_h = host_of(final)
    kind = main.get('kind') or 'none'
    return {'final_url': final, 'status': main.get('status'), 'kind': kind, 'read': today, 'by': 'bot',
            'fingerprint': main.get('fingerprint') or '', 'host': final_h, 'family': (main.get('family') or {}).get('id') if isinstance(main.get('family'), dict) else main.get('family') or '',
            'nps_code': (main.get('family') or {}).get('code') if isinstance(main.get('family'), dict) else '',
            'moved': bool(asked_h and final_h and base_host(asked_h) != base_host(final_h)),
            'final_host': final_h, 'dead_twice': bool(main.get('dead_twice')),
            'requests': main.get('requests') or 0}


def _location(main, pages, pota, area, pin):
    loc = _blank_location()
    text = main.get('text') or ''
    html = main.get('html') or ''
    coords = html_coords(html, text)
    for p in pages:
        for url, link_text in p.get('links') or []:
            got = address_facts(url, pota.get('name') or '', pin)
            for c in got['coords']:
                c['link_text'] = link_text
                coords.append(c)
    dropped = 0
    kept = []
    office_zone = _section(text, {'addresses', 'address', 'contact us', 'contact', 'mailing address'})
    for c in coords:
        if not point_ok(c['lat'], c['lon'], area, pin):
            dropped += 1
            continue
        role = c.get('role') or 'unknown'
        src = (c.get('from') or '') + ' ' + (c.get('link_text') or '')
        if re.search(r'office|headquarters|visitor cent', src, re.I):
            role = 'office' if 'visitor' not in src.lower() else 'visitor-centre'
        elif re.search(r'\b(location|map|directions)\b', src, re.I) and role == 'unknown':
            role = 'unknown'  # a center is where the map was looking; only a matching label is park
        if c.get('from') == 'labelled line' and office_zone and str(c.get('lat')) in office_zone:
            role = 'office'
        c['role'] = role
        if pin and pin[0] is not None and c.get('km_from_pin') is None:
            d = haversine_km((c['lat'], c['lon']), (pin[0], pin[1]))
            c['km_from_pin'] = round(d, 2) if d is not None else None
        kept.append(c)
    # pin far: park role, over 5 km AND over twice the park's own radius
    radius = _radius_km(pages, pota)
    for c in kept:
        d = c.get('km_from_pin')
        c['pin_far'] = bool(c.get('role') == 'park' and d is not None and d > 5 and radius and d > 2 * radius)
    loc['coords'] = kept[:8]
    loc['dropped_points'] = dropped
    loc['addresses'] = addresses_in(text)
    loc['directions'] = directions_of(text)
    states = []
    for m in re.finditer(r'\b(' + '|'.join(STATE_NAME) + r')\b', text, re.I):
        name = m.group(1).title()
        if name not in states:
            states.append(name)
    loc['state_words'] = states[:6]
    return loc


def _radius_km(pages, pota):
    acres = None
    for p in pages:
        for s in sizes_labelled(p.get('text') or '', pota.get('name') or '', pota.get('type') or ''):
            if s.get('total') and s.get('clean') and (acres is None or s['acres'] > acres):
                acres = s['acres']
    if not acres:
        return None
    return math.sqrt(acres * 4046.8564224 / math.pi) / 1000.0


def _maps(main, pota, pages):
    agency = host_of(main.get('final') or '')
    rows, seen = [], set()
    for p in pages:
        for url, text in p.get('links') or []:
            if url in seen:
                continue
            row = classify_link(url, text, pota.get('name') or '', agency)
            if not row:
                continue
            seen.add(url)
            marker = ''
            af = address_facts(url, pota.get('name') or '')
            for c in af['coords']:
                if c.get('label'):
                    marker = c['label']
            names, unit = names_park_link(url, text, pota.get('name') or '', marker)
            row.update({'names_park': names, 'names_unit': unit, 'status': 'not opened'})
            if row['kind'] == 'web-map' or script_shell(url):
                row['status'] = 'not opened (script-built app)' if script_shell(url) or 'arcgis' in url else 'not opened'
            rows.append(row)
    return rows[:8]


def park_radius_note():
    return 'radius from a clean total size only; no size means no PIN_FAR question'
