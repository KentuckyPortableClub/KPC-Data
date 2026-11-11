#!/usr/bin/env python3
"""kpc_acres - the official acres LIST for the Kentucky Portable Club (KPC).

Reads each agency's OWN published size list (CSV / XLSX / HTML table / ArcGIS layer / Socrata / CKAN /
PDF table, plus the hand-copied sizes in the research file), converts every size to acres, matches each
row to a POTA park with strict rules (park number / record id / same name + same kind in the same
state), and writes one club file:

  <out>/acres.json        {ref: {acres, value_given, unit_given, agency, record_name, how, parts,
                                 source_url, read_date, why, flags: [], ...}}
  <out>/acres-list.json   {ref: acres}      (what the map audit's --acres takes)
  <out>/unmatched.csv     agency,row_name,size,unit,why,area,source_url,read_date
  <out>/report.md         one line per agency
  <out>/state.json        for --resume;  <out>/work/  per-agency working files + download cache

Python 3.12, standard library only (pypdf optional, for PDF tables).  python kpc_acres.py --selftest
"""
import argparse, csv, datetime, hashlib, html.parser, io, json, math, os, re, shutil, sys, tempfile
import time, unicodedata, urllib.error, urllib.parse, urllib.request, urllib.robotparser, zipfile
import xml.etree.ElementTree as ET
import importlib.util as _ilu, os as _os   # noqa: E402  (owner rule, 2026-11-10: the club's one host check, before any request)
_hs = _ilu.spec_from_file_location("kpc_host_rules", _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "..", "..", "kpc_host_rules.py"))
_hr = _ilu.module_from_spec(_hs); _hs.loader.exec_module(_hr); _hr.install()

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from kpc_order import rank  # noqa: E402  (US + Canada first; never drops anything)

VERSION = '1.0.0'
EXIT_DONE, EXIT_TIME, EXIT_BAD_INPUT = 0, 3, 2

# ----------------------------------------------------------------------------------------------------------
# Places
# ----------------------------------------------------------------------------------------------------------
US_STATES = {
    'AL': 'alabama', 'AK': 'alaska', 'AZ': 'arizona', 'AR': 'arkansas', 'CA': 'california', 'CO': 'colorado',
    'CT': 'connecticut', 'DE': 'delaware', 'DC': 'district of columbia', 'FL': 'florida', 'GA': 'georgia',
    'HI': 'hawaii', 'ID': 'idaho', 'IL': 'illinois', 'IN': 'indiana', 'IA': 'iowa', 'KS': 'kansas',
    'KY': 'kentucky', 'LA': 'louisiana', 'ME': 'maine', 'MD': 'maryland', 'MA': 'massachusetts',
    'MI': 'michigan', 'MN': 'minnesota', 'MS': 'mississippi', 'MO': 'missouri', 'MT': 'montana',
    'NE': 'nebraska', 'NV': 'nevada', 'NH': 'new hampshire', 'NJ': 'new jersey', 'NM': 'new mexico',
    'NY': 'new york', 'NC': 'north carolina', 'ND': 'north dakota', 'OH': 'ohio', 'OK': 'oklahoma',
    'OR': 'oregon', 'PA': 'pennsylvania', 'RI': 'rhode island', 'SC': 'south carolina', 'SD': 'south dakota',
    'TN': 'tennessee', 'TX': 'texas', 'UT': 'utah', 'VT': 'vermont', 'VA': 'virginia', 'WA': 'washington',
    'WV': 'west virginia', 'WI': 'wisconsin', 'WY': 'wyoming', 'PR': 'puerto rico', 'VI': 'virgin islands',
    'GU': 'guam', 'AS': 'american samoa', 'MP': 'northern mariana islands'}
CA_PROVS = {'AB': 'alberta', 'BC': 'british columbia', 'MB': 'manitoba', 'NB': 'new brunswick',
            'NL': 'newfoundland and labrador', 'NS': 'nova scotia', 'NT': 'northwest territories',
            'NU': 'nunavut', 'ON': 'ontario', 'PE': 'prince edward island', 'QC': 'quebec',
            'SK': 'saskatchewan', 'YT': 'yukon'}
STATE_FIPS = {'AL': '01', 'AK': '02', 'AZ': '04', 'AR': '05', 'CA': '06', 'CO': '08', 'CT': '09', 'DE': '10',
              'DC': '11', 'FL': '12', 'GA': '13', 'HI': '15', 'ID': '16', 'IL': '17', 'IN': '18', 'IA': '19',
              'KS': '20', 'KY': '21', 'LA': '22', 'ME': '23', 'MD': '24', 'MA': '25', 'MI': '26', 'MN': '27',
              'MS': '28', 'MO': '29', 'MT': '30', 'NE': '31', 'NV': '32', 'NH': '33', 'NJ': '34', 'NM': '35',
              'NY': '36', 'NC': '37', 'ND': '38', 'OH': '39', 'OK': '40', 'OR': '41', 'PA': '42', 'RI': '44',
              'SC': '45', 'SD': '46', 'TN': '47', 'TX': '48', 'UT': '49', 'VT': '50', 'VA': '51', 'WA': '53',
              'WV': '54', 'WI': '55', 'WY': '56', 'PR': '72'}
_NAME2US = {v: k for k, v in US_STATES.items()}
_NAME2CA = {v: k for k, v in CA_PROVS.items()}
_NAME2CA.update({'newfoundland': 'NL', 'pei': 'PE', 'yukon territory': 'YT'})


def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFKD', str(s)) if not unicodedata.combining(c))


def norm_area(v, country_hint=None):
    """'US-KY' / 'KY' / 'Kentucky' / 'CA-ON' / 'ON' / 'Ontario' / 'US' / 'Canada' -> 'US-KY' / 'CA-ON' / 'US-*'."""
    if v is None:
        return None
    s = str(v).strip()
    if not s:
        return None
    u = s.upper().replace('_', '-')
    m = re.match(r'^(US|CA|K|VE)-([A-Z]{2})$', u)
    if m:
        cc = {'K': 'US', 'VE': 'CA'}.get(m.group(1), m.group(1))
        return f'{cc}-{m.group(2)}'
    if u in ('US', 'USA', 'UNITED STATES', 'US-*'):
        return 'US-*'
    if u in ('CANADA', 'CA-*'):
        return 'CA-*'
    hint = (country_hint or '').upper()
    if len(u) == 2:
        if u in CA_PROVS and u not in US_STATES:
            return 'CA-' + u
        if u == 'CA' and hint.startswith('CA') and hint != 'CALIFORNIA':
            return 'CA-*'
        if u in US_STATES:
            return 'US-' + u
    low = strip_accents(s).lower().strip()
    if low in _NAME2US:
        return 'US-' + _NAME2US[low]
    if low in _NAME2CA:
        return 'CA-' + _NAME2CA[low]
    return None


# ----------------------------------------------------------------------------------------------------------
# Units and numbers
# ----------------------------------------------------------------------------------------------------------
UNIT_FACTORS = {'acres': 1.0, 'ha': 2.47105, 'km2': 247.105, 'sqmi': 640.0, 'm2': 0.000247105}
UNIT_LABEL = {'acres': 'acres', 'ha': 'ha', 'km2': 'km²', 'sqmi': 'sq mi', 'm2': 'm²'}


def norm_unit(s):
    """Unit word / column header -> 'acres' | 'ha' | 'km2' | 'sqmi' | 'm2' | None."""
    if s is None:
        return None
    t = strip_accents(str(s).replace('²', '2')).lower().replace('^2', '2')
    t = re.sub(r'[\s_\.\-/]+', ' ', t).strip()
    if not t:
        return None
    if re.search(r'acre|(^| |\()acs?($| |\))', t):
        return 'acres'
    if re.search(r'hectare|(^| |\()ha($| |\))', t):
        return 'ha'
    if re.search(r'km ?2|sq ?km|square kilomet|kilometres? carres?|kilometers? squared', t):
        return 'km2'
    if re.search(r'sq ?mi|square mile|(^| |\()mi ?2|miles? squared', t):
        return 'sqmi'
    if re.search(r'(^| |\()m ?2($| |\))|sq ?m($| |\))|square met|metres? carres?|sq meters?', t):
        return 'm2'
    return None


NUM_RE = re.compile(r"[-+]?\d[\d,\.\u00a0\u202f' ]*")


def parse_size(v):
    """'1,234.5 acres' / '1 234,5' / 12.3 -> (value, unit found in the text or None)."""
    if v is None or isinstance(v, bool):
        return None, None
    if isinstance(v, (int, float)):
        return (float(v) if math.isfinite(v) else None), None
    s = str(v).strip()
    m = NUM_RE.search(s)
    if not m:
        return None, None
    raw = m.group(0).strip().rstrip(',.')
    for ch in ('\u00a0', '\u202f', "'", ' '):
        raw = raw.replace(ch, '')
    if ',' in raw and '.' in raw:
        raw = raw.replace('.', '').replace(',', '.') if raw.rfind(',') > raw.rfind('.') else raw.replace(',', '')
    elif ',' in raw:
        parts = raw.split(',')
        raw = raw.replace(',', '') if (len(parts) > 2 or len(parts[-1]) == 3) else raw.replace(',', '.')
    elif raw.count('.') > 1:
        raw = raw.replace('.', '')
    try:
        val = float(raw)
    except ValueError:
        return None, None
    rest = s[m.end():].strip()
    return val, (norm_unit(rest[:40]) if rest else None)


def to_acres(value, unit):
    return value * UNIT_FACTORS[unit]


# ----------------------------------------------------------------------------------------------------------
# Names and kinds of place  (the key's rule: same name + same kind; generic words dropped)
# ----------------------------------------------------------------------------------------------------------
_KIND_LIST = [  # (kind, alternatives) - most specific first.  Text is accent-free lower case.
    ('nwr', 'national wildlife refuge|nwr'),
    ('national_wildlife_area', 'national wildlife area|reserve nationale de faune'),
    ('migratory_bird_sanctuary', 'migratory bird sanctuary|refuge d oiseaux migrateurs'),
    ('national_trail', 'national (?:scenic|historic) trail'),
    ('national_historic', 'national historic(?:al)? (?:site|park|landmark)|national memorial|lieu historique national'),
    ('national_battlefield', 'national (?:military )?battlefield(?: park| site)?'),
    ('national_recreation_area', 'national river and recreation area|national recreation area'),
    ('national_monument', 'national monument'),
    ('national_shore', 'national (?:sea|lake)shore'),
    ('national_river', 'national (?:wild and )?(?:scenic )?river(?:way)?|wild and scenic river'),
    ('national_forest', 'national forest|national grassland|foret nationale'),
    ('national_park', 'national park reserve|national park|national preserve|parc national'),
    ('wma', 'state wildlife management area|wildlife management area|wma|state wildlife area|'
            'fish and wildlife area|fish wildlife area|wildlife area|state game lands?|state game area|'
            'game lands?|wildlife management unit|wildlife hunting access area|hunting access area'),
    ('wildlife_refuge', 'state wildlife refuge|wildlife refuge|wildlife sanctuary'),
    ('wildlife_reserve', 'wildlife reserve|reserve faunique'),
    ('state_historic_site', 'state historic(?:al)? (?:site|park|shrine)|state shrine|historic site'),
    ('state_recreation_area', 'state recreation area|state rec area'),
    ('state_park', 'state resort park|state recreational park|state recreation park|state park'),
    ('state_forest', 'state forest'),
    ('nature_preserve', 'state nature preserve|nature preserve'),
    ('natural_area', 'state natural area|natural area'),
    ('provincial_park', 'provincial park|parc provincial|parc national du quebec'),
    ('provincial_recreation_area', 'provincial recreation area'),
    ('conservation_reserve', 'conservation reserve'),
    ('ecological_reserve', 'ecological reserve|reserve ecologique|nature reserve'),
    ('conservation_area', 'conservation area'),
    ('regional_park', 'regional park|parc regional'),
    ('fishing_lake', 'state fishing lake|fishing lake'),
    ('recreation_area', 'recreation area|rec area'),
]
KIND_RES = [(k, re.compile(r'(?<![a-z0-9])(?:' + alts + r')s?(?![a-z0-9])')) for k, alts in _KIND_LIST]
ABBR = {'wma': 'wma', 'sp': 'state_park', 'srp': 'state_park', 'snp': 'nature_preserve',
        'shs': 'state_historic_site', 'sf': 'state_forest', 'nwr': 'nwr', 'nf': 'national_forest',
        'sna': 'natural_area', 'pp': 'provincial_park', 'nra': 'national_recreation_area', 'np': 'national_park',
        'sra': 'state_recreation_area'}
# POTA / key "type" words -> kind (used only when the name itself carries no kind words)
TYPE_WORDS = {'wma': 'wma', 'state park': 'state_park', 'nature preserve': 'nature_preserve',
              'state forest': 'state_forest', 'national forest': 'national_forest', 'national park': 'national_park',
              'state fishing lake': 'fishing_lake', 'natural area': 'natural_area',
              'national recreation area': 'national_recreation_area', 'provincial park': 'provincial_park'}
KIND_LABEL = {k: k.replace('_', ' ') for k, _ in _KIND_LIST}
KIND_LABEL.update({'wma': 'WMA', 'nwr': 'national wildlife refuge'})
STOP = {'the', 'of', 'and', 'at', 'on', 'de', 'du', 'des', 'la', 'le', 'les', 'l', 'd', 'a'}
TOKEN_MAP = {'st': 'saint', 'ste': 'sainte', 'mt': 'mount', 'mtn': 'mountain', 'ft': 'fort', 'pt': 'point',
             'lk': 'lake', 'ck': 'creek', 'crk': 'creek', 'n': 'north', 's': 'south', 'e': 'east', 'w': 'west'}
UNIT_SUFFIX = re.compile(r'(?:\s+(?:north|south|east|west|upper|lower|middle|central|ne|nw|se|sw))?'
                         r'\s+(?:unit|units|tract|tracts|section|addition|annex|parcel|portion|block|division)'
                         r'(?:\s+(?:[a-z]|\d{1,3}|[ivx]{1,4}))?$')


def norm_text(s):
    t = strip_accents(s).lower().replace('&', ' and ')
    t = re.sub(r"['\u2019`]", '', t)
    t = re.sub(r'[^a-z0-9]+', ' ', t)
    return re.sub(r'\s+', ' ', t).strip()


def classify(text):
    """-> (kind or None, text with the kind phrase(s) removed)."""
    t = norm_text(text)
    kind, best_end = None, -1
    for k, rx in KIND_RES:  # the kind phrase that ends last wins: "X State Park State Nature Preserve" is a preserve
        ends = [m.end() for m in rx.finditer(t)]
        if ends and max(ends) > best_end:
            kind, best_end = k, max(ends)
    for k, rx in KIND_RES:
        t = rx.sub(' ', t)
    t = re.sub(r'\s+', ' ', t).strip()
    if kind is None and t:
        toks = t.split()
        if toks[-1] in ABBR and len(toks) > 1:
            kind = ABBR[toks[-1]]
            t = ' '.join(toks[:-1])
    return kind, t


def kinds_of(name, kind):
    """A joint name such as "Knobs State Forest and WMA" carries both kinds; any other name carries one."""
    t = norm_text(name)
    found = [k for k, rx in KIND_RES if rx.search(t)]
    if len(found) > 1 and re.search(r'(?<![a-z0-9])and(?![a-z0-9])', t) or '/' in str(name) and len(found) > 1:
        return set(found) | ({kind} if kind else set())
    return {kind} if kind else set()


def core_of(t):
    toks = [TOKEN_MAP.get(x, x) for x in t.split()]
    return ' '.join(x for x in toks if x not in STOP)


def name_kind(name, default_kind=None):
    """'Clay Wildlife Management Area - North Unit' -> ('wma', 'clay north unit', ['clay'])"""
    raw = str(name or '')
    kind, rest = classify(raw)
    kind = kind or default_kind
    no_paren = re.sub(r'\(.*?\)|\[.*?\]', ' ', raw)
    _, rest_np = classify(no_paren)
    full = core_of(rest_np) or core_of(rest)
    variants = []
    head = re.split(r'\s+[-\u2013\u2014:]\s+|:\s*|,\s*', no_paren, maxsplit=1)[0]
    for cand in (core_of(rest), core_of(classify(head)[1])):
        if cand and cand != full and cand not in variants:
            variants.append(cand)
    for base in [full] + list(variants):
        cut = UNIT_SUFFIX.sub('', base).strip()
        if cut and cut != base and cut not in variants and cut != full:
            variants.append(cut)
    return kind, full, variants


def kind_from_type(s):
    if not s:
        return None
    k, _ = classify(s)
    if k:
        return k
    t = norm_text(s)
    for w, k in TYPE_WORDS.items():
        if w in t:
            return k
    return None


# ----------------------------------------------------------------------------------------------------------
# Field-name helpers (the research file's row shape is not fixed)
# ----------------------------------------------------------------------------------------------------------
def nkey(k):
    return re.sub(r'[^a-z0-9]', '', str(k).lower())


def pick(row, *names, want=None):
    """First non-empty value whose key matches one of names (case / punctuation free).
    want=str: strings only; want='num': values that parse as a number; want='col': a column name (not a number)."""
    if not isinstance(row, dict):
        return None
    m = {}
    for k, v in row.items():
        m.setdefault(nkey(k), v)
    for n in names:
        v = m.get(nkey(n))
        if v is None or (isinstance(v, str) and not v.strip()):
            continue
        if want is str and not isinstance(v, str):
            continue
        if want == 'num' and parse_size(v)[0] is None:
            continue
        if want == 'col' and (not isinstance(v, str) or re.fullmatch(r'[\d,\.\s]+', v.strip())):
            continue
        return v
    return None


F_AGENCY = ('agency', 'agency_name', 'agencyname', 'owner', 'organization', 'org', 'department', 'publisher',
            'source_agency', 'managing_agency', 'manager')
F_AREA = ('area', 'area_code', 'areacode', 'state', 'province', 'prov', 'st', 'region', 'jurisdiction', 'code',
          'state_code', 'program', 'pota_area')
F_COUNTRY = ('country', 'nation', 'cc')
F_URL = ('direct_download_csv_xlsx_pdf', 'direct_download', 'list_url', 'download_url', 'data_url', 'download', 'dataset_url', 'api', 'api_url', 'endpoint',
         'layer_url', 'service_url', 'rest_url', 'file_url', 'csv_url', 'xlsx_url', 'pdf_url', 'table_url',
         'list', 'url', 'link', 'href')
F_PAGE = ('official_list_page_acres_hectares', 'official_list_page', 'page', 'page_url', 'list_page', 'source_page', 'home', 'homepage', 'info_url', 'web_page', 'source_url',
          'source')
F_FORMAT = ('format', 'file_format', 'fileformat', 'file_type', 'source_type', 'list_type', 'kind', 'type', 'how',
            'method', 'access')
F_SIZECOL = ('size_column', 'size_col', 'sizecolumn', 'size_field', 'acres_column', 'acres_col', 'acres_field',
             'area_column', 'area_field', 'acreage_column', 'size_header', 'column', 'field', 'size_column_name')
F_UNIT = ('unit_acres_hectares_km', 'unit', 'units', 'size_unit', 'area_unit', 'unit_given', 'uom')
F_NAMECOL = ('name_column', 'name_col', 'name_field', 'namecolumn', 'park_column', 'park_name_column')
F_IDCOL = ('id_column', 'id_col', 'id_field', 'ref_column', 'record_id_column')
F_COUNTYCOL = ('county_column', 'county_col', 'county_field')
F_LATCOL = ('lat_column', 'latitude_column', 'lat_field', 'y_column')
F_LONCOL = ('lon_column', 'longitude_column', 'lon_field', 'lng_column', 'x_column')
F_STATECOL = ('state_column', 'state_col', 'province_column', 'state_field')
F_STATUS = ('status', 'result', 'found', 'list_status', 'finding', 'outcome')
F_KIND = ('park_kind', 'place_kind', 'default_kind', 'kind_of_place', 'designation', 'park_type', 'list_kind')
F_HANDKEYS = ('hand', 'hand_sizes', 'handsizes', 'hand_copies', 'hand_copy', 'manual', 'manual_sizes', 'sizes',
              'acres_not_downloadable', 'not_downloadable', 'copied', 'hand_rows', 'copied_sizes', 'rows_by_hand')
H_NAME = ('park_name_as_the_agency_writes_it', 'park', 'park_name', 'parkname', 'name', 'row_name', 'site', 'site_name', 'unit_name', 'property',
          'place', 'area_name', 'wma', 'preserve', 'title')
H_SIZE = ('acres', 'acreage', 'size', 'value', 'area', 'size_given', 'value_given', 'total_acres', 'hectares',
          'ha', 'km2', 'sq_mi', 'sqmi')
H_UNITKEY = {'acres': 'acres', 'acreage': 'acres', 'totalacres': 'acres', 'hectares': 'ha', 'ha': 'ha',
             'km2': 'km2', 'sqkm': 'km2', 'sqmi': 'sqmi', 'squaremiles': 'sqmi', 'm2': 'm2'}
H_REF = ('park_number_if_matched', 'ref', 'pota', 'pota_ref', 'park_ref', 'reference', 'park_number', 'number')
FORMAT_WORDS = ('csv', 'xlsx', 'xls', 'excel', 'html', 'table', 'arcgis', 'featureserver', 'mapserver',
                'socrata', 'ckan', 'pdf', 'json', 'geojson', 'esri', 'web table', 'download', 'api')


# ----------------------------------------------------------------------------------------------------------
# Polite fetcher (robots.txt, 2 s per host, UA, back-off, cache, banned sources) - transport is injectable
# ----------------------------------------------------------------------------------------------------------
class FetchError(Exception):
    pass


class SkipItem(Exception):
    pass


BANNED_HOST = re.compile(r'(^|\.)(openstreetmap\.(org|fr|de)|osm\.org|overpass-api\.de|geofabrik\.de|'
                         r'alltrails\.com|gaiagps\.com|strava\.com|tripadvisor\.[a-z.]+|yelp\.[a-z.]+|'
                         r'wikipedia\.org|wikimedia\.org|wikidata\.org|protectedplanet\.net|unep-wcmc\.org|'
                         r'google\.[a-z.]+|googleapis\.com|googleusercontent\.com|gstatic\.com|goo\.gl|ggpht\.com)$',
                         re.I)
BANNED_ANY = re.compile(r'wdpa|protectedplanet|overpass|openstreetmap', re.I)
ALLOWED_CLOUD = ('storage.googleapis.com',)


def banned(url):
    host = (urllib.parse.urlsplit(url).hostname or '').lower()
    if host in ALLOWED_CLOUD or host.endswith('.storage.googleapis.com'):
        return False
    return bool(BANNED_HOST.search(host) or BANNED_ANY.search(url))


def urllib_transport(url, headers, timeout=90):
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, dict(r.headers), r.read(200 * 1024 * 1024)
    except urllib.error.HTTPError as e:
        try:
            body = e.read(1024 * 1024)
        except Exception:
            body = b''
        return e.code, dict(e.headers or {}), body


class Fetcher:
    def __init__(self, transport=None, cache_dir=None, gap=2.0, sleep=time.sleep, clock=time.monotonic,
                 contact=None, backoff=(15, 45, 120), offline=False):
        self.transport = transport or urllib_transport
        self.cache_dir = cache_dir
        self.gap, self.sleep, self.clock, self.backoff, self.offline = gap, sleep, clock, backoff, offline
        self.ua = f'KPC park tools ({contact or os.environ.get("KPC_CONTACT", "contact not set")})'
        self.last, self.robots, self.resting, self.requests = {}, {}, set(), 0

    def _wait(self, host, gap):
        last = self.last.get(host)
        if last is not None:
            d = gap - (self.clock() - last)
            if d > 0:
                self.sleep(d)
        self.last[host] = self.clock()

    def _raw(self, url, host, gap):
        if host in self.resting:
            raise FetchError(f'host {host} is resting for this run (429/503)')
        for attempt in range(len(self.backoff) + 1):
            self._wait(host, gap)
            self.requests += 1
            try:
                status, headers, body = self.transport(url, {'User-Agent': self.ua, 'Accept': '*/*'})
            except FetchError:
                raise
            except Exception as e:  # network error
                raise FetchError(f'network error: {type(e).__name__}: {e}'[:200])
            if status in (429, 503):
                if attempt < len(self.backoff):
                    ra = (headers or {}).get('Retry-After') or (headers or {}).get('retry-after')
                    try:
                        w = min(float(ra), 600)
                    except (TypeError, ValueError):
                        w = self.backoff[attempt]
                    self.sleep(w)
                    continue
                self.resting.add(host)
                raise FetchError(f'HTTP {status} after 3 retries; host {host} now resting for this run')
            return status, headers or {}, body or b''
        raise FetchError('unreachable')

    def _robots(self, scheme, host):
        if host in self.robots:
            return self.robots[host]
        rp = urllib.robotparser.RobotFileParser()
        try:
            status, _, body = self._raw(f'{scheme}://{host}/robots.txt', host, self.gap)
        except FetchError as e:
            if 'resting' in str(e):
                raise
            rp.parse(['User-agent: *', 'Disallow: /'])
            rp.kpc_note = f'robots.txt unreachable ({e}), so the host is treated as disallowed'
            self.robots[host] = rp
            return rp
        if status >= 500:  # RFC 9309: unreachable -> assume complete disallow
            rp.parse(['User-agent: *', 'Disallow: /'])
            rp.kpc_note = f'robots.txt unreachable (HTTP {status}), so the host is treated as disallowed'
        elif status >= 400:  # RFC 9309: 4xx -> no rules
            rp.parse([])
        else:
            rp.parse(body.decode('utf-8', 'replace').splitlines())
        self.robots[host] = rp
        return rp

    def get(self, url, use_cache=True):
        if url.startswith('file://'):
            url = urllib.parse.unquote(urllib.parse.urlsplit(url).path)
        if not re.match(r'^https?://', url, re.I):
            if not os.path.exists(url):
                raise FetchError(f'local file not found: {url}')
            with open(url, 'rb') as f:
                return f.read()
        if banned(url):
            raise FetchError('source not allowed by the KPC rules (OSM / Google / WDPA / wiki ...)')
        cpath = None
        if self.cache_dir and use_cache:
            cpath = os.path.join(self.cache_dir, hashlib.sha1(url.encode()).hexdigest() + '.bin')
            if os.path.exists(cpath):
                with open(cpath, 'rb') as f:
                    return f.read()
        if self.offline:
            raise FetchError('offline and not in the cache')
        sp = urllib.parse.urlsplit(url)
        host = (sp.hostname or '').lower()
        rp = self._robots(sp.scheme, host)
        if not rp.can_fetch(self.ua, url):
            raise FetchError(getattr(rp, 'kpc_note', None) or 'blocked by robots.txt')
        gap = self.gap
        try:
            cd = rp.crawl_delay(self.ua)
            if cd and float(cd) > gap:
                gap = min(float(cd), 60.0)
        except Exception:
            pass
        status, headers, body = self._raw(url, host, gap)
        if status in (401, 407):
            raise FetchError(f'needs sign-in (HTTP {status})')
        if status == 403:
            raise FetchError('needs sign-in or forbidden (HTTP 403)')
        if status >= 400:
            raise FetchError(f'HTTP {status}')
        if cpath:
            os.makedirs(self.cache_dir, exist_ok=True)
            with open(cpath + '.tmp', 'wb') as f:
                f.write(body)
            os.replace(cpath + '.tmp', cpath)
        return body

    def get_json(self, url):
        body = self.get(url)
        try:
            return json.loads(body.decode('utf-8-sig'))
        except Exception:
            raise FetchError('answer was not JSON')


# ----------------------------------------------------------------------------------------------------------
# Readers: bytes -> list of records (dicts)
# ----------------------------------------------------------------------------------------------------------
def decode_text(data):
    for enc in ('utf-8-sig', 'cp1252', 'latin-1'):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode('utf-8', 'replace')


def read_csv_rows(data):
    text = decode_text(data)
    try:
        dialect = csv.Sniffer().sniff(text[:20000], delimiters=',;\t|')
    except csv.Error:
        dialect = csv.excel
    return list(csv.reader(io.StringIO(text), dialect))


def read_xlsx_rows(data, sheet=None):
    """Tiny stdlib XLSX reader: first sheet (or the named / numbered one) -> list of rows of strings."""
    z = zipfile.ZipFile(io.BytesIO(data))
    M = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
    R = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
    shared = []
    if 'xl/sharedStrings.xml' in z.namelist():
        for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall(M + 'si'):
            shared.append(''.join(t.text or '' for t in si.iter(M + 't')))
    wb = ET.fromstring(z.read('xl/workbook.xml'))
    rels = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    rmap = {r.get('Id'): r.get('Target') for r in rels}
    sheets = [(s.get('name'), rmap.get(s.get(R + 'id'))) for s in wb.find(M + 'sheets')]
    target = sheets[0][1]
    if sheet is not None:
        for i, (nm, tg) in enumerate(sheets):
            if str(sheet).lower() in (nm.lower(), str(i + 1)):
                target = tg
                break
    target = target.lstrip('/')
    root = ET.fromstring(z.read(target if target.startswith('xl/') else 'xl/' + target))
    rows = []
    for row in root.iter(M + 'row'):
        cells = {}
        for c in row.findall(M + 'c'):
            col = 0
            for ch in re.match(r'[A-Z]*', c.get('r') or '').group(0):
                col = col * 26 + ord(ch) - 64
            t, v = c.get('t'), c.find(M + 'v')
            if t == 's' and v is not None:
                val = shared[int(v.text)]
            elif t == 'inlineStr':
                val = ''.join(x.text or '' for x in c.iter(M + 't'))
            else:
                val = v.text if v is not None else ''
            cells[(col or len(cells) + 1) - 1] = val
        if cells:
            out = [''] * (max(cells) + 1)
            for k, v in cells.items():
                out[k] = v
            rows.append(out)
    return rows


class _TableParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tables, self.stack, self.cell, self.row = [], [], None, None

    def handle_starttag(self, tag, attrs):
        if tag == 'table':
            self.stack.append([])
        elif tag == 'tr' and self.stack:
            self.row = []
        elif tag in ('td', 'th') and self.stack:
            if self.row is None:
                self.row = []
            span = dict(attrs).get('colspan') or '1'
            self.cell = [[], int(span) if str(span).isdigit() else 1]
        elif tag == 'br' and self.cell is not None:
            self.cell[0].append(' ')

    def handle_endtag(self, tag):
        if tag in ('td', 'th') and self.cell is not None and self.row is not None:
            txt = re.sub(r'\s+', ' ', ''.join(self.cell[0])).strip()
            self.row.extend([txt] + [''] * (self.cell[1] - 1))
            self.cell = None
        elif tag == 'tr' and self.stack and self.row is not None:
            if self.row:
                self.stack[-1].append(self.row)
            self.row = None
        elif tag == 'table' and self.stack:
            self.tables.append(self.stack.pop())

    def handle_data(self, d):
        if self.cell is not None:
            self.cell[0].append(d)


def read_html_tables(data):
    p = _TableParser()
    p.feed(decode_text(data))
    p.close()
    return [t for t in p.tables if t]


SIZE_HEADER = re.compile(r'acre|hectare|(^|[^a-z])ha([^a-z]|$)|km ?2|km²|sq ?mi|square|area|size', re.I)
BAD_SIZE_HEADER = re.compile(r'shape|st_area|perimeter|length|len$', re.I)


def _cell_matches(cell, col):
    c, k = nkey(cell), nkey(col)
    return bool(k) and (c == k or (len(k) >= 4 and k in c))


def table_to_records(rows, cfg):
    """Find the header row (first 40 rows), then make dicts. Rows that repeat the header are skipped."""
    rows = [[('' if c is None else str(c)).strip() for c in r] for r in rows]
    hi, want = None, cfg.get('size_col')
    for i, r in enumerate(rows[:40]):
        if len([c for c in r if c]) < 2:
            continue
        if want and any(_cell_matches(c, want) for c in r):
            hi = i
            break
        if not want and any(SIZE_HEADER.search(c) and not BAD_SIZE_HEADER.search(c) and parse_size(c)[0] is None
                            for c in r):
            hi = i
            break
    if hi is None:
        for i, r in enumerate(rows[:40]):
            if len([c for c in r if c]) >= 2:
                hi = i
                break
    if hi is None:
        return []
    header, seen = [], {}
    for j, c in enumerate(rows[hi]):
        c = c or f'col{j + 1}'
        if c in seen:
            seen[c] += 1
            c = f'{c}_{seen[c]}'
        else:
            seen[c] = 1
        header.append(c)
    recs = []
    for r in rows[hi + 1:]:
        if not any(r):
            continue
        if [x.lower() for x in r[:len(header)]] == [x.lower() for x in rows[hi][:len(r)]]:
            continue
        recs.append({header[j] if j < len(header) else f'col{j + 1}': v for j, v in enumerate(r)})
    return recs


def json_to_records(obj):
    if isinstance(obj, list):
        return [x for x in obj if isinstance(x, dict)]
    if isinstance(obj, dict):
        if isinstance(obj.get('features'), list):
            out = []
            for f in obj['features']:
                if isinstance(f, dict):
                    a = f.get('attributes') if isinstance(f.get('attributes'), dict) else f.get('properties')
                    if isinstance(a, dict):
                        out.append(a)
            return out
        for k in ('records', 'rows', 'data', 'items', 'results', 'result', 'parks'):
            v = obj.get(k)
            if isinstance(v, (list, dict)):
                r = json_to_records(v)
                if r:
                    return r
        if obj and all(isinstance(v, dict) for v in obj.values()):
            return [dict(v, **({'name': k} if 'name' not in v else {})) for k, v in obj.items()]
    return []


PDF_LINE = re.compile(r"^(?P<name>[A-Za-z][A-Za-z\.'\u2019&\-/ ]*?[A-Za-z\)\.])\s+(?P<rest>\d[\d,\.\s]*?)"
                      r'\s*(?P<unit>acres?|ac\.?|ha|hectares?)?\s*$')


def parse_pdf_line(line, pos=None):
    """Return (name, size_text, unit) only when the line is surely one name + one number; else None."""
    line = re.sub(r'\s+', ' ', line).strip()
    m = PDF_LINE.match(line)
    if not m:
        return None
    nums = re.findall(r'\d[\d,]*(?:\.\d+)?', m.group('rest'))
    unit = norm_unit(m.group('unit')) if m.group('unit') else None
    if len(nums) == 1:
        return m.group('name').strip(), nums[0], unit
    if pos and 1 <= pos <= len(nums):
        return m.group('name').strip(), nums[pos - 1], unit
    return None


def read_pdf_records(data, cfg):
    try:
        import pypdf  # optional
    except ImportError:
        raise SkipItem('PDF table skipped: pypdf is not installed (pip install pypdf)')
    reader = pypdf.PdfReader(io.BytesIO(data))
    recs, unsure = [], 0
    pos = cfg.get('pdf_column')
    pos = int(pos) if str(pos or '').isdigit() else None
    for page in reader.pages:
        for line in (page.extract_text() or '').splitlines():
            if not re.search(r'\d', line) or not re.search(r'[A-Za-z]{3}', line):
                continue
            got = parse_pdf_line(line, pos)
            if got:
                recs.append({'name': got[0], 'size': got[1], 'unit': got[2] or ''})
            else:
                unsure += 1
    cfg['_pdf_unsure'] = unsure
    return recs


def sniff_format(url, cfg, data=None):
    f = norm_text(cfg.get('fmt') or '')
    u = (url or '').lower()
    for word, fmt in (('arcgis', 'arcgis'), ('featureserver', 'arcgis'), ('mapserver', 'arcgis'),
                      ('esri', 'arcgis'), ('socrata', 'socrata'), ('ckan', 'ckan'), ('xlsx', 'xlsx'),
                      ('excel', 'xlsx'), ('xls', 'xlsx'), ('csv', 'csv'), ('pdf', 'pdf'), ('geojson', 'json'),
                      ('json', 'json'), ('html', 'html'), ('table', 'html')):
        if word in f.split():
            return fmt
    if re.search(r'/(featureserver|mapserver)(/\d+)?(/query)?/?(\?|$)', u):
        return 'arcgis'
    if re.search(r'/(resource|d)/[a-z0-9]{4}-[a-z0-9]{4}', u):
        return 'socrata'
    if '/api/3/action/' in u:
        return 'ckan'
    path = urllib.parse.urlsplit(u).path
    for ext, fmt in (('.csv', 'csv'), ('.xlsx', 'xlsx'), ('.pdf', 'pdf'), ('.geojson', 'json'), ('.json', 'json'),
                     ('.htm', 'html'), ('.html', 'html'), ('.txt', 'csv')):
        if path.endswith(ext):
            return fmt
    if data is not None:
        head = data[:600].lstrip()
        if head.startswith(b'%PDF'):
            return 'pdf'
        if head.startswith(b'PK'):
            return 'xlsx'
        if head[:1] in (b'{', b'['):
            return 'json'
        if head[:1] == b'<' or b'<table' in data[:2000000].lower():
            return 'html'
        return 'csv'
    return None


def arcgis_records(fetcher, url, cfg):
    base = re.sub(r'/query/?$', '', url.split('?')[0].rstrip('/'))
    if re.search(r'/(FeatureServer|MapServer)$', base, re.I):
        base += '/' + str(cfg.get('layer') or 0)
    where = cfg.get('where') or '1=1'

    def q(**kw):
        p = {'where': where, 'outFields': '*', 'returnGeometry': 'false', 'f': 'json'}
        p.update({k: v for k, v in kw.items() if v not in (None, '')})
        return base + '/query?' + urllib.parse.urlencode(p)
    out, offset, pages = [], 0, 0
    while True:
        js = fetcher.get_json(q(resultOffset=offset, resultRecordCount=1000))
        if isinstance(js, dict) and js.get('error'):
            code = (js['error'] or {}).get('code')
            if code in (498, 499, 401, 403):
                raise FetchError('needs sign-in (ArcGIS token required)')
            if offset == 0:
                return arcgis_by_ids(fetcher, base, where)
            raise FetchError(f'ArcGIS error {code}: {(js["error"] or {}).get("message")}')
        feats = json_to_records(js)
        out.extend(feats)
        pages += 1
        if not js.get('exceededTransferLimit') or not feats or pages > 500:
            break
        offset += len(feats)
    return out


def arcgis_by_ids(fetcher, base, where):
    js = fetcher.get_json(base + '/query?' + urllib.parse.urlencode({'where': where, 'returnIdsOnly': 'true',
                                                                     'f': 'json'}))
    if js.get('error'):
        raise FetchError(f'ArcGIS error {js["error"].get("code")}: {js["error"].get("message")}')
    ids, out = js.get('objectIds') or [], []
    for i in range(0, len(ids), 200):
        js = fetcher.get_json(base + '/query?' + urllib.parse.urlencode(
            {'objectIds': ','.join(map(str, ids[i:i + 200])), 'outFields': '*', 'returnGeometry': 'false',
             'f': 'json'}))
        out.extend(json_to_records(js))
    return out


def socrata_records(fetcher, url):
    sp = urllib.parse.urlsplit(url)
    m = re.search(r'/(?:resource|d)/([a-z0-9]{4}-[a-z0-9]{4})', url) or re.search(r'([a-z0-9]{4}-[a-z0-9]{4})', sp.path)
    if not m:
        raise FetchError('Socrata dataset id not found in the url')
    base = f'{sp.scheme}://{sp.netloc}/resource/{m.group(1)}.json'
    out, off = [], 0
    while True:
        js = fetcher.get_json(base + '?' + urllib.parse.urlencode({'$limit': 50000, '$offset': off}))
        if isinstance(js, dict) and js.get('error'):
            raise FetchError(f'Socrata error: {js.get("message")}')
        if not js:
            break
        out.extend(json_to_records(js))
        if len(js) < 50000:
            break
        off += 50000
    return out


def ckan_records(fetcher, url, cfg):
    sp = urllib.parse.urlsplit(url)
    root = f'{sp.scheme}://{sp.netloc}'
    qs = urllib.parse.parse_qs(sp.query)
    if '/api/3/' in sp.path:
        pre = sp.path.split('/api/3/')[0]
        if 'datastore_search' in sp.path:
            return ckan_datastore(fetcher, root + pre, (qs.get('resource_id') or [None])[0])
        pkg = fetcher.get_json(url)
    else:
        m = re.search(r'/dataset/(?:[^/]+/)*?([^/?#]+)/?$', sp.path)
        if not m:
            raise FetchError('CKAN dataset id not found in the url')
        pre = sp.path.split('/dataset/')[0]
        pre = re.sub(r'/(en|fr)$', '', pre)
        pkg = fetcher.get_json(f'{root}{pre}/api/3/action/package_show?id={m.group(1)}')
    res = (pkg.get('result') or {}).get('resources') or []
    want = cfg.get('resource')
    res = [r for r in res if not want or want in (r.get('id'), r.get('name'))]
    for r in res:
        if r.get('datastore_active'):
            return ckan_datastore(fetcher, root + pre, r['id'])
    for fmt in ('csv', 'xlsx', 'xls', 'json', 'geojson'):
        for r in res:
            if (r.get('format') or '').lower() == fmt and r.get('url'):
                return bytes_to_records(fetcher.get(r['url']), {'xls': 'xlsx', 'geojson': 'json'}.get(fmt, fmt), cfg)
    raise FetchError('CKAN dataset has no CSV / XLSX / JSON / datastore resource')


def ckan_datastore(fetcher, base, rid):
    out, off = [], 0
    while True:
        js = fetcher.get_json(f'{base}/api/3/action/datastore_search?' + urllib.parse.urlencode(
            {'resource_id': rid, 'limit': 32000, 'offset': off}))
        recs = ((js.get('result') or {}).get('records')) or []
        out.extend(recs)
        if len(recs) < 32000:
            break
        off += 32000
    return out


def bytes_to_records(data, fmt, cfg):
    if fmt == 'csv':
        return table_to_records(read_csv_rows(data), cfg)
    if fmt == 'xlsx':
        if not data.startswith(b'PK'):
            raise FetchError('old .xls (not .xlsx) is not supported; it needs a CSV/XLSX copy')
        return table_to_records(read_xlsx_rows(data, cfg.get('sheet')), cfg)
    if fmt == 'html':
        tables = read_html_tables(data)
        if not tables:
            raise FetchError('no HTML table on the page')
        ti = cfg.get('table_index')
        if ti is not None and str(ti).lstrip('-').isdigit():
            return table_to_records(tables[int(ti)], cfg)
        best = None
        for t in tables:
            recs = table_to_records(t, cfg)
            if not recs:
                continue
            hdr = list(recs[0].keys())
            ok = any(_cell_matches(h, cfg['size_col']) for h in hdr) if cfg.get('size_col') else \
                any(SIZE_HEADER.search(h) and not BAD_SIZE_HEADER.search(h) for h in hdr)
            if ok and (best is None or len(recs) > len(best)):
                best = recs
        if best is None:
            raise FetchError('no HTML table with a size column')
        return best
    if fmt == 'json':
        return json_to_records(json.loads(decode_text(data)))
    if fmt == 'pdf':
        return read_pdf_records(data, cfg)
    raise FetchError(f'unknown format {fmt}')


def open_list(fetcher, cfg):
    url = cfg['url']
    fmt = sniff_format(url, cfg)
    if fmt == 'arcgis':
        return arcgis_records(fetcher, url, cfg), 'arcgis'
    if fmt == 'socrata':
        return socrata_records(fetcher, url), 'socrata'
    if fmt == 'ckan':
        return ckan_records(fetcher, url, cfg), 'ckan'
    data = fetcher.get(url)
    if data[:4] == b'%PDF':
        fmt = 'pdf'
    elif data[:2] == b'PK':
        fmt = 'xlsx'
    fmt = fmt or sniff_format(url, {}, data)
    return bytes_to_records(data, fmt, cfg), fmt


# ----------------------------------------------------------------------------------------------------------
# Club data: park pins (parkinfo), keys, answer key
# ----------------------------------------------------------------------------------------------------------
REF_RE = re.compile(r'(?<![A-Z0-9])(US|CA|K|VE)-(\d{4,5})(?![0-9])')


def norm_ref(s):
    m = REF_RE.search(str(s or '').upper())
    if not m:
        return None
    cc = {'K': 'US', 'VE': 'CA'}.get(m.group(1), m.group(1))
    return f'{cc}-{m.group(2)}'


def fnum(v):
    try:
        f = float(v)
        return f if math.isfinite(f) else None
    except (TypeError, ValueError):
        return None


def norm_id(v):
    s = str(v).strip().lower()
    if re.fullmatch(r'\d+\.0+', s):
        s = s.split('.')[0]
    return s if len(s) >= 3 else None


class Parks:
    def __init__(self):
        self.p = {}        # ref -> {name, type, lat, lon, area, county, kind, core}
        self.idx = {}      # area -> core -> [(ref, kind, via)]
        self.rec_ids = {}  # area -> record id -> {refs}
        self.outline = {}  # ref -> acres of the current outline (key)

    def add(self, ref, name, typ, lat, lon, area, county=None):
        if not ref or not name:
            return
        ref = norm_ref(ref) or str(ref)
        kind, core, _ = name_kind(name)
        kind = kind or kind_from_type(typ)
        self.p[ref] = {'name': str(name), 'type': typ, 'lat': fnum(lat), 'lon': fnum(lon), 'area': area,
                       'county': county, 'kind': kind, 'core': core}
        if core:
            self.idx.setdefault(area, {}).setdefault(core, []).append((ref, kind, 'park name'))

    def add_alias(self, ref, rname):
        p = self.p.get(ref)
        if not p or not rname or not isinstance(rname, str):
            return
        kind, core, _ = name_kind(rname)
        kind = kind or p['kind']
        if core and kind == p['kind']:  # a record name of another kind is not used as an alias
            lst = self.idx.setdefault(p['area'], {}).setdefault(core, [])
            if not any(r == ref and k == kind for r, k, _ in lst):
                lst.append((ref, kind, 'key record name'))


def load_parkinfo(path, parks):
    """data/parkinfo/US-XX.json {"parks": {ref: [name, website, type, access, access2, lat, lon, ...]}},
    CA.json (column 10 = province), or a POTA-API list [{reference, name, latitude, longitude, locationDesc}]."""
    files = []
    if path and os.path.isdir(path):
        files = sorted(os.path.join(path, f) for f in os.listdir(path) if f.lower().endswith('.json'))
    elif path and os.path.exists(path):
        files = [path]
    for fp in files:
        try:
            with open(fp, encoding='utf-8-sig') as f:
                d = json.load(f)
        except Exception as e:
            print(f'warning: parkinfo {fp} not read: {e}', file=sys.stderr)
            continue
        base = os.path.basename(fp)[:-5].upper()
        fa = {'CA': 'CA-*', 'US': 'US-*'}.get(base) or norm_area(base)
        rows = d.get('parks', d) if isinstance(d, dict) else d
        items = rows.items() if isinstance(rows, dict) else ((None, r) for r in rows)
        for ref, r in items:
            area, county = fa, None
            if isinstance(r, list):
                name = r[0] if r else None
                typ = r[2] if len(r) > 2 else None
                lat = r[5] if len(r) > 5 else None
                lon = r[6] if len(r) > 6 else None
                if area is None or area.endswith('*'):
                    for i in (10, 9):  # CA.json: column 10 = province
                        a2 = norm_area(r[i], 'CA') if len(r) > i and isinstance(r[i], str) else None
                        if a2 and a2.startswith('CA-') and not a2.endswith('*'):
                            area = a2
                            break
            elif isinstance(r, dict):
                ref = ref or pick(r, 'reference', 'ref', 'park', 'code')
                name = pick(r, 'name', 'park_name', 'n')
                typ = pick(r, 'type', 'parktype', 'park_type', 't')
                lat = pick(r, 'lat', 'latitude')
                lon = pick(r, 'lon', 'lng', 'longitude')
                county = pick(r, 'county')
                loc = pick(r, 'locationDesc', 'location', 'state', 'province', 'area')
                if loc:
                    locs = [norm_area(x) for x in re.split(r'[,; ]+', str(loc)) if x]
                    locs = [x for x in locs if x and not x.endswith('*')]
                    area = fa if fa in locs else (locs[0] if locs else fa)
            else:
                continue
            if area is None or area.endswith('*'):
                continue
            parks.add(ref, name, typ, lat, lon, area, county)


def load_keys(path, parks):
    """data/us-key/US-XX.json, data/ca-key/*.json -> {"parks": {ref: {"m": [[record id, name, acres, how]...]}}}.
    The answer-key shape {"parks": {ref: {"tracts": [[layer, name, acres, how, n]]}}} is read too
    (names + acres only; the layer code is not a record id)."""
    files = []
    if path and os.path.isdir(path):
        for root, dirs, fs in os.walk(path):
            if os.path.relpath(root, path).count(os.sep) >= 1:
                dirs[:] = []
            for f in fs:
                if f.lower().endswith('.json') and ('key' in root.lower() or 'key' in f.lower()):
                    files.append(os.path.join(root, f))
    elif path and os.path.exists(path):
        files = [path]
    n = 0
    for fp in sorted(files):
        try:
            with open(fp, encoding='utf-8-sig') as f:
                d = json.load(f)
        except Exception:
            continue
        rows = d.get('parks') if isinstance(d, dict) else None
        if not isinstance(rows, dict):
            continue
        for ref, v in rows.items():
            ref = norm_ref(ref) or ref
            if not isinstance(v, dict) or ref not in parks.p:
                continue
            area = parks.p[ref]['area']
            recs, is_m = v.get('m'), True
            if not isinstance(recs, list):
                recs, is_m = (v.get('tracts') if isinstance(v.get('tracts'), list) else []), False
            tot = 0.0
            for m in recs:
                if not isinstance(m, (list, tuple)) or len(m) < 2:
                    continue
                if is_m and m[0] not in (None, ''):
                    rid = norm_id(m[0])
                    if rid:
                        parks.rec_ids.setdefault(area, {}).setdefault(rid, set()).add(ref)
                parks.add_alias(ref, m[1])
                a = fnum(m[2]) if len(m) > 2 else None
                if a:
                    tot = tot + a if is_m else max(tot, a)
            if tot > 0:
                parks.outline[ref] = max(parks.outline.get(ref, 0), tot)
            n += 1
    return n


def load_answer_key(path):
    """{ref: acres} from ky-answer-key.json ({"parks": {ref: {"acres" | "tracts": ...}}}) or {ref: acres}.
    With tracts, the largest tract is the answer (the tracts of one park are often the same land in two layers)."""
    if not path or not os.path.exists(path):
        return {}
    with open(path, encoding='utf-8-sig') as f:
        d = json.load(f)
    rows = d.get('parks', d) if isinstance(d, dict) else d
    if isinstance(rows, list):
        rows = {pick(r, 'ref', 'reference'): r for r in rows if isinstance(r, dict)}
    out = {}
    for ref, v in (rows or {}).items():
        a = None
        if isinstance(v, (int, float)):
            a = float(v)
        elif isinstance(v, dict):
            a = fnum(pick(v, 'acres', 'official_acres', 'answer_acres', 'size'))
            if a is None and isinstance(v.get('tracts'), list):
                ts = [fnum(t[2]) for t in v['tracts'] if isinstance(t, list) and len(t) > 2 and fnum(t[2])]
                a = max(ts) if ts else None
        if a and ref:
            out[norm_ref(ref) or ref] = a
    return out


# ----------------------------------------------------------------------------------------------------------
# County check (rule c) - county shapes from the Census TIGERweb service, one query per state, cached
# ----------------------------------------------------------------------------------------------------------
TIGER = ('https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/State_County/MapServer/1/query?'
         'where=STATE%3D%27{fips}%27&outFields=NAME&returnGeometry=true&outSR=4326&maxAllowableOffset=0.002&f=json')


def norm_county(s):
    t = norm_text(s or '')
    t = re.sub(r'\b(county|counties|parish|co|borough|census area|municipality|city and borough)\b', ' ', t)
    return re.sub(r'\s+', ' ', t).strip()


def point_in_ring(x, y, ring):
    inside, n = False, len(ring)
    for i in range(n):
        x1, y1 = ring[i][0], ring[i][1]
        x2, y2 = ring[(i + 1) % n][0], ring[(i + 1) % n][1]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / ((y2 - y1) or 1e-30) + x1:
            inside = not inside
    return inside


def haversine_km(lat1, lon1, lat2, lon2):
    r = math.radians
    a = math.sin(r(lat2 - lat1) / 2) ** 2 + math.cos(r(lat1)) * math.cos(r(lat2)) * math.sin(r(lon2 - lon1) / 2) ** 2
    return 6371.0 * 2 * math.asin(min(1.0, math.sqrt(a)))


class Counties:
    def __init__(self, fetcher, enabled=True):
        self.fetcher, self.enabled, self.by_state, self.err = fetcher, enabled, {}, {}

    def _load(self, st):
        if st in self.by_state or st in self.err:
            return
        fips = STATE_FIPS.get(st)
        if not fips:
            self.err[st] = 'no FIPS code'
            return
        try:
            js = self.fetcher.get_json(TIGER.format(fips=fips))
            polys = []
            for f in js.get('features') or []:
                nm = norm_county((f.get('attributes') or {}).get('NAME'))
                rings = (f.get('geometry') or {}).get('rings') or []
                if nm and rings:
                    polys.append((nm, rings))
            if not polys:
                raise FetchError('no county shapes in the answer')
            self.by_state[st] = polys
        except Exception as e:
            self.err[st] = str(e)[:120]

    def county_of(self, area, lat, lon):
        """-> (county name or None, note)"""
        if not self.enabled:
            return None, 'county check turned off'
        if not area or not area.startswith('US-') or lat is None or lon is None:
            return None, 'no county lookup for this area'
        st = area[3:]
        self._load(st)
        if st in self.err:
            return None, f'county lookup failed ({self.err[st]})'
        for nm, rings in self.by_state[st]:
            inside = False
            for ring in rings:
                if point_in_ring(lon, lat, ring):
                    inside = not inside
            if inside:
                return nm, 'ok'
        return None, 'pin not inside any county shape'


# ----------------------------------------------------------------------------------------------------------
# Research file -> work items
# ----------------------------------------------------------------------------------------------------------
def _hand_rows_from(v, agency=None, area=None, page=None):
    out = []
    if isinstance(v, list):
        for r in v:
            if isinstance(r, dict):
                out.append(dict(r, _agency=pick(r, *F_AGENCY) or agency, _area=pick(r, *F_AREA) or area,
                                _page=pick(r, 'page', 'page_url', 'source_url', 'url', 'source') or page))
            elif isinstance(r, (list, tuple)) and len(r) >= 2:  # [name, size, unit?, page?]
                out.append({'name': r[0], 'size': r[1], 'unit': r[2] if len(r) > 2 else None,
                            '_agency': agency, '_area': area, '_page': r[3] if len(r) > 3 else page})
    elif isinstance(v, dict):
        for k, sub in v.items():
            if isinstance(sub, list) or (isinstance(sub, dict) and pick(sub, *H_SIZE, want='num') is None):
                a2 = norm_area(k)
                out.extend(_hand_rows_from(sub, agency if a2 else (agency or k), a2 or area, page))
            elif isinstance(sub, dict):
                out.extend(_hand_rows_from([dict(sub, name=pick(sub, *H_NAME) or k)], agency, area, page))
            else:
                out.append({'name': k, 'size': sub, '_agency': agency, '_area': area, '_page': page})
    return out


def _is_hand_row(r):
    return (pick(r, *H_NAME, want=str) is not None
            and pick(r, 'acres', 'size', 'value', 'hectares', 'ha', 'acreage', 'size_given', 'value_given',
                     want='num') is not None
            and pick(r, *F_SIZECOL, want='col') is None and pick(r, *F_URL[:-4], want=str) is None)


def load_research(path):
    """-> (agency cfgs, hand rows, field names seen).  Accepts a list of rows, {"agencies": [...]},
    a dict of dicts keyed by agency, or a dict of lists keyed by area; hand sizes under any key with
    hand / manual / not downloadable / copied in its name, or nested in an agency row."""
    with open(path, encoding='utf-8-sig') as f:
        d = json.load(f)
    rows, hand = [], []

    def take_rows(lst, area=None):
        for r in lst:
            if isinstance(r, dict):
                rows.append(dict(r, _area_hint=area) if area else r)

    if isinstance(d, list):
        take_rows(d)
    elif isinstance(d, dict):
        used = False
        for k, v in d.items():
            nk = nkey(k)
            if any(nkey(h) == nk for h in F_HANDKEYS) or re.search(r'hand|manual|notdownloadable|copied', nk):
                hand.extend(_hand_rows_from(v))
                used = True
            elif nk == 'sources' and isinstance(v, list) and v and isinstance(v[0], dict) and any(nkey(x) == 'host' for x in v[0]):
                used = True   # chat 10 Nov 1: the KPC file's 'Sources' sheet = hosts tested (OK / BLOCKED), not size lists
            elif nk in ('agencies', 'rows', 'items', 'list', 'lists', 'data', 'results', 'found', 'sources'):
                if isinstance(v, list):
                    take_rows(v)
                elif isinstance(v, dict):
                    take_rows([dict(x, agency=pick(x, *F_AGENCY) or kk) for kk, x in v.items() if isinstance(x, dict)])
                used = True
        if not used:
            for k, v in d.items():
                if isinstance(v, dict):
                    rows.append(dict(v, agency=pick(v, *F_AGENCY) or k))
                elif isinstance(v, list) and norm_area(k):
                    take_rows(v, norm_area(k))
    seen, cfgs = set(), []
    for r in rows:
        seen.update(r.keys())
        if _is_hand_row(r):
            hand.extend(_hand_rows_from([r]))
            continue
        cfg = row_to_cfg(r)
        for hk in dict.fromkeys(nkey(h) for h in F_HANDKEYS):
            v = pick(r, hk)
            if isinstance(v, (list, dict)):
                hand.extend(_hand_rows_from(v, cfg['agency'], cfg['area'], cfg.get('page') or cfg.get('url')))
        cfgs.append(cfg)
    amap = {}   # chat 10 Nov 1: hand rows carry only the agency name: take the area from that agency's own row
    for c in cfgs:
        if c.get('area') and c.get('agency'): amap.setdefault(norm_text(c['agency']), c['area'])
    for h in hand:
        if not h.get('_area') and h.get('_agency'): h['_area'] = amap.get(norm_text(str(h['_agency'])))
        seen.update(h.keys())
    return cfgs, hand, sorted(str(k) for k in seen if not str(k).startswith('_'))


def row_to_cfg(r):
    country = pick(r, *F_COUNTRY, want=str)
    area_raw = pick(r, *F_AREA, want=str) or r.get('_area_hint')
    area = norm_area(area_raw, country) if area_raw else None
    if area is None and country:
        area = norm_area(country)
    fmt, kind_raw = None, pick(r, *F_KIND, want=str)
    for n in F_FORMAT:  # 'kind' / 'type' may hold a file format ("CSV") or a kind of place ("WMA")
        v = pick(r, n, want=str)
        if not v:
            continue
        if any(w in norm_text(v).split() or w == norm_text(v) for w in FORMAT_WORDS):
            fmt = fmt or v
        else:
            kind_raw = kind_raw or v
    agency = str(pick(r, *F_AGENCY) or pick(r, 'name', 'list_name', 'title') or 'unknown agency').strip()
    list_name = pick(r, 'list_name', 'title', 'dataset', 'name', 'what', want=str)
    default_kind = kind_from_type(kind_raw) if kind_raw else None
    if not default_kind:
        default_kind = classify(str(list_name or ''))[0] or classify(agency)[0]
    url = pick(r, *F_URL, want=str)
    page = pick(r, *F_PAGE, want=str)
    status = pick(r, *F_STATUS)
    cfg = {'agency': agency, 'area': area, 'area_raw': area_raw, 'url': url, 'page': page, 'fmt': fmt,
           'size_col': pick(r, *F_SIZECOL, want='col'), 'unit': norm_unit(pick(r, *F_UNIT)),
           'unit_raw': pick(r, *F_UNIT), 'name_col': pick(r, *F_NAMECOL), 'id_col': pick(r, *F_IDCOL),
           'county_col': pick(r, *F_COUNTYCOL), 'lat_col': pick(r, *F_LATCOL), 'lon_col': pick(r, *F_LONCOL),
           'state_col': pick(r, *F_STATECOL), 'status': status, 'kind': default_kind, 'kind_raw': kind_raw,
           'sheet': pick(r, 'sheet', 'sheet_name', 'tab'), 'table_index': pick(r, 'table_index', 'table_no'),
           'layer': pick(r, 'layer', 'layer_id'), 'where': pick(r, 'where', 'filter'),
           'resource': pick(r, 'resource', 'resource_id'), 'pdf_column': pick(r, 'pdf_column', 'pdf_size_position'),
           'list_name': list_name}
    if status is True:
        st = 'found'
    elif status is False:
        st = 'no list'
    else:
        st = norm_text(str(status or ''))
    if re.search(r'no list|not found|^none$|missing|no data', st):
        cfg['skip'] = 'no list (research says so)'
    elif 'page' in st and 'found' not in st:
        cfg['skip'] = 'page only, no list to read (research says so)'
    elif not url:
        cfg['skip'] = 'no list url in the research row'
    return cfg


def item_key(kind, agency, area, extra):
    h = hashlib.sha1(f'{kind}|{agency}|{area}|{extra}'.encode()).hexdigest()[:10]
    return f'{kind}-{re.sub(r"[^a-z0-9]+", "-", norm_text(agency))[:40]}-{h}'


# ----------------------------------------------------------------------------------------------------------
# Row extraction and matching
# ----------------------------------------------------------------------------------------------------------
NAME_HDRS = ('name', 'park', 'park_name', 'parkname', 'unit_name', 'unit_nm', 'site_name', 'sitename', 'area_name',
             'wma_name', 'wmaname', 'property', 'property_name', 'propname', 'site', 'unit', 'label', 'title',
             'loc_nm', 'name_e', 'name_en', 'english_name', 'prot_name', 'park_nm', 'parkname_e', 'facility',
             'preserve', 'preserve_name', 'forest', 'wma', 'location')
ID_HDR = re.compile(r'(^|_)(id|ref|pota|code|uid|unit_?id|site_?id|zone_?id|park_?id|wma_?id|number|num|no|'
                    r'pota_?ref|park_?ref|cpcad_?id|padus_?id)$', re.I)
ID_BAD = re.compile(r'objectid|^fid$|^oid$|globalid|shape|^gid$|^rowid$|^_id$', re.I)
TOTAL_ROW = re.compile(r'^(grand )?(sub)?totals?\b|^all (parks|areas|units)$', re.I)


def resolve(headers, want, auto=None):
    if want:
        for test in (lambda h: str(h).lower() == str(want).lower(), lambda h: nkey(h) == nkey(want),
                     lambda h: len(nkey(want)) >= 3 and nkey(want) in nkey(h)):
            for h in headers:
                if test(h):
                    return h
        return None
    return auto(headers) if auto else None


def auto_name(headers):
    for w in NAME_HDRS:
        for h in headers:
            if nkey(h) == nkey(w):
                return h
    for h in headers:
        if 'name' in str(h).lower() and not re.search(r'county|agency|owner|manag|state|city|contact|file|field|layer',
                                                      str(h), re.I):
            return h
    return None


def auto_size(headers):
    for pat in (r'gis_?acres|^acres$|total_?acres|acreage|acres', r'hectare|(^|_)ha$|area_?ha|^ha$',
                r'km2|sq_?km|km²', r'sq_?mi|square_?mi', r'^size$|^area$|size|area'):
        for h in headers:
            if re.search(pat, str(h), re.I) and not BAD_SIZE_HEADER.search(str(h)):
                return h
    return None


def auto_first(headers, pats):
    for p in pats:
        for h in headers:
            if re.fullmatch(p, str(h), re.I):
                return h
    return None


def extract_rows(recs, cfg):
    """records -> [{name, value, unit, size_text, ids, county, lat, lon, state, text}], columns used."""
    headers = []
    for r in recs[:300]:
        for k in r.keys():
            if k not in headers:
                headers.append(k)
    cols_txt = ', '.join(map(str, headers[:25]))
    name_h = resolve(headers, cfg.get('name_col'), auto_name)
    size_h = resolve(headers, cfg.get('size_col'), auto_size)
    if cfg.get('size_col') and size_h is None:
        raise FetchError(f"size column '{cfg['size_col']}' not found (columns: {cols_txt})")
    if size_h is None:
        raise FetchError(f'no size column found (columns: {cols_txt})')
    if name_h is None:
        raise FetchError(f'no name column found (columns: {cols_txt})')
    unit = cfg.get('unit') or norm_unit(size_h)
    if cfg.get('id_col'):
        id_hs = [h for h in [resolve(headers, cfg['id_col'])] if h]
    else:
        id_hs = [h for h in headers if ID_HDR.search(str(h)) and not ID_BAD.search(str(h))]
    county_h = resolve(headers, cfg.get('county_col'),
                       lambda hs: auto_first(hs, [r'county', r'county_?name', r'counties', r'cnty', r'co_name']))
    lat_h = resolve(headers, cfg.get('lat_col'), lambda hs: auto_first(hs, [r'lat', r'latitude', r'lat_dd']))
    lon_h = resolve(headers, cfg.get('lon_col'), lambda hs: auto_first(hs, [r'lon', r'long', r'lng', r'longitude',
                                                                            r'lon_dd']))
    state_h = resolve(headers, cfg.get('state_col'),
                      lambda hs: auto_first(hs, [r'state', r'st', r'state_?abbr', r'state_?code', r'prov', r'province']))
    out = []
    for i, r in enumerate(recs):
        name = r.get(name_h)
        name = '' if name is None else str(name).strip()
        raw = r.get(size_h)
        val, u_in = parse_size(raw)
        lat = fnum(r.get(lat_h)) if lat_h else None
        lon = fnum(r.get(lon_h)) if lon_h else None
        if lat is None or lon is None or not (-90 <= lat <= 90 and -180 <= lon <= 180):
            lat = lon = None
        row_unit = u_in or cfg.get('unit') or norm_unit(r.get('unit')) or unit  # a unit written in the size text wins
        text = ' | '.join(str(v) for v in r.values() if v not in (None, ''))
        out.append({'i': i, 'name': name, 'value': val, 'size_text': '' if raw is None else str(raw),
                    'unit': row_unit, 'ids': [str(r.get(h)) for h in id_hs if r.get(h) not in (None, '')],
                    'county': (str(r.get(county_h)).strip() if county_h and r.get(county_h) else None),
                    'lat': lat, 'lon': lon, 'state': (r.get(state_h) if state_h else None), 'text': text})
    cols = {'name': name_h, 'size': size_h, 'unit': unit, 'ids': id_hs, 'county': county_h,
            'lat': lat_h, 'lon': lon_h, 'state': state_h}
    return out, cols


class Matcher:
    def __init__(self, parks, counties):
        self.parks, self.counties = parks, counties

    def match(self, row, area, default_kind):
        """-> ([(ref, rule, why)], None) or ([], reason not matched).  Stops at the first rule that matches."""
        P = self.parks
        # a. the park number is written in the row
        refs = []
        for m in REF_RE.finditer(row['text'].upper()):
            ref = norm_ref(m.group(0))
            if ref and ref not in refs:
                refs.append(ref)
        known = [r for r in refs if r in P.p]
        if known:
            return [(r, 'number', f'the list row carries the park number {r}') for r in known], None
        # a. the same record id our key joined
        hits = []
        if area:
            for v in row['ids']:
                rid = norm_id(v)
                for ref in sorted(((P.rec_ids.get(area) or {}).get(rid)) or ()):
                    if self._name_overlaps(row['name'], ref) and ref not in [h[0] for h in hits]:
                        hits.append((ref, 'record id', f'record id {v} is the record the key joined to {ref}'))
        if hits:
            return hits, None
        if refs:
            return [], f'park number {", ".join(refs)} not in the park list'
        # b. same name + same kind, in the same state / province
        if not area or area.endswith('*'):
            return [], 'no state / province for this row'
        kind, core, variants = name_kind(row['name'], default_kind)
        if not core:
            return [], 'no name'
        if not kind:
            return [], 'kind of place unknown (no generic words in the name and no kind for the list)'
        idx = P.idx.get(area) or {}
        kinds = kinds_of(row['name'], kind)
        for cand, note in [(core, '')] + [(v, ' (unit / tract words dropped)') for v in variants]:
            same = sorted({r for r, k, _ in (idx.get(cand) or []) if k in kinds})
            if len(same) > 1:
                return [], f'ambiguous: "{cand}" {KIND_LABEL.get(kind, kind)} fits {", ".join(same)}'
            if len(same) == 1:
                ref = same[0]
                ok, why_c = self._rule_c(row, ref, area)  # c. county / point must agree with the pin
                if not ok:
                    return [], why_c
                pkind = P.p[ref]['kind']
                return [(ref, 'name+kind', f'same name "{cand}" + same kind ({KIND_LABEL.get(pkind, pkind)}'
                                           f'{"; joint name" if len(kinds) > 1 else ""}) '
                                           f'in {area}{note}; {why_c}')], None
        other = sorted({f'{r} ({KIND_LABEL.get(k, k)})' for c in [core] + variants for r, k, _ in (idx.get(c) or [])})
        if other:
            return [], f'same name but different kind (row: {KIND_LABEL.get(kind, kind)}; park {", ".join(other)})'
        return [], f'no POTA park named "{core}" ({KIND_LABEL.get(kind, kind)}) in {area}'

    def _name_overlaps(self, rname, ref):
        if not rname:
            return True
        a = set(name_kind(rname)[1].split())
        b = set((self.parks.p[ref]['core'] or '').split())
        return bool(a & b)

    def _rule_c(self, row, ref, area):
        p = self.parks.p[ref]
        if row['lat'] is not None and p['lat'] is not None and p['lon'] is not None:
            d = haversine_km(row['lat'], row['lon'], p['lat'], p['lon'])
            if d > 25:
                return False, f'name+kind fit {ref} but the list point is {d:.0f} km from the pin (over 25 km)'
            return True, f'list point {d:.1f} km from the pin'
        if row['county']:
            wanted = {norm_county(x) for x in re.split(r'[,;/&]| and ', row['county']) if norm_county(x)}
            pc, note = (norm_county(p['county']), 'ok') if p.get('county') else \
                self.counties.county_of(area, p['lat'], p['lon'])
            if pc:
                if pc in wanted:
                    return True, f'county {pc.title()} agrees with the pin'
                return False, (f'name+kind fit {ref} but the list county ({row["county"]}) is not the pin\'s '
                               f'county ({pc.title()})')
            return True, f'county not checked: {note}'
        return True, 'no county or point on the list'


# ----------------------------------------------------------------------------------------------------------
# One work item -> result dict (saved in work/agencies/<key>.json)
# ----------------------------------------------------------------------------------------------------------
def today():
    return os.environ.get('KPC_TODAY') or datetime.date.today().isoformat()


def new_result(kind, agency, area, src, read_date, status=None):
    return {'kind': kind, 'agency': agency, 'area': area, 'source_url': src, 'read_date': read_date,
            'matches': [], 'unmatched': [], 'status': status, 'rows_read': 0, 'skipped_rows': 0}


def run_list_item(cfg, fetcher, matcher, read_date, areas):
    res = new_result('list', cfg['agency'], cfg['area'], cfg.get('url') or cfg.get('page'), read_date)
    if cfg.get('skip'):
        res['status'] = 'skipped: ' + cfg['skip']
        return res
    try:
        recs, fmt = open_list(fetcher, cfg)
        rows, cols = extract_rows(recs, cfg)
    except (FetchError, SkipItem) as e:
        res['status'] = f'failed: {e}'
        return res
    except Exception as e:  # a bad list never stops the run
        res['status'] = f'failed: {type(e).__name__}: {e}'[:300]
        return res
    res['status'] = f'read OK ({fmt})'
    if cfg.get('_pdf_unsure'):
        res['status'] += f'; {cfg["_pdf_unsure"]} PDF lines skipped as unsure'
    res['columns'] = cols
    for row in rows:
        process_row(res, row, cfg.get('area'), cfg.get('kind'), res['source_url'], matcher, areas, None)
    return res


def process_row(res, row, area, default_kind, src, matcher, areas, how_text):
    if not row['name'] and row['value'] is None:
        return
    if TOTAL_ROW.search(row['name'] or ''):
        res['skipped_rows'] += 1
        return
    if row.get('state'):
        a2 = norm_area(row['state'], (area or '')[:2])
        if a2 and not a2.endswith('*'):
            area = a2
    if areas and area and not area.endswith('*') and area not in areas:
        res['skipped_rows'] += 1
        return
    res['rows_read'] += 1

    def um(why):
        res['unmatched'].append({'agency': res['agency'], 'row_name': row['name'], 'size': row['size_text'],
                                 'unit': row['unit'] or '', 'why': why, 'source_url': src or '',
                                 'read_date': res['read_date'], 'area': area or ''})
    if row['value'] is None:
        return um('no size value')
    if not row['unit']:
        return um('unit unknown (not in the research row, the column header or the size text)')
    hits, why = matcher.match(row, area, default_kind)
    if not hits:
        return um(why)
    acres = to_acres(row['value'], row['unit'])
    for ref, rule, mwhy in hits:
        res['matches'].append({'ref': ref, 'row': row['i'], 'row_name': row['name'], 'acres': acres,
                               'value': row['value'], 'unit': row['unit'], 'rule': rule, 'why': mwhy,
                               'how_text': how_text, 'source_url': src or ''})


def run_hand_item(agency, area, rows, matcher, read_date, areas):
    page = next((r.get('_page') for r in rows if r.get('_page')), None)
    res = new_result('hand', f'{agency} (hand copy)', area, page, read_date, 'read OK (hand sizes)')
    default_kind = classify(agency or '')[0]
    for i, r in enumerate(rows):
        size_v = pick(r, *H_SIZE, want='num')
        val, u_in = parse_size(size_v)
        unit = norm_unit(pick(r, *F_UNIT)) or u_in
        if not unit:
            for k, v in r.items():
                if v is size_v:
                    unit = H_UNITKEY.get(nkey(k))
                    break
        pg = r.get('_page') or page
        ref_txt = pick(r, *H_REF) or ''
        row = {'i': i, 'name': str(pick(r, *H_NAME) or '').strip(), 'value': val,
               'size_text': '' if size_v is None else str(size_v), 'unit': unit, 'ids': [],
               'county': pick(r, 'county'), 'lat': fnum(pick(r, 'lat', 'latitude')),
               'lon': fnum(pick(r, 'lon', 'lng', 'longitude')), 'state': None, 'text': str(ref_txt)}
        if row['lat'] is None or row['lon'] is None:
            row['lat'] = row['lon'] = None
        process_row(res, row, norm_area(r.get('_area')) or area, default_kind, pg, matcher, areas,
                    f'hand copy ({agency}, {pg or "page not given"})')
    return res


# ----------------------------------------------------------------------------------------------------------
# Merge all items -> outputs
# ----------------------------------------------------------------------------------------------------------
RULE_RANK = {'number': 0, 'record id': 1, 'name+kind': 2}


def fmt_num(v):
    return f'{int(v):,}' if float(v).is_integer() else f'{v:,.4f}'.rstrip('0').rstrip('.')


def r2(x):
    return round(x, 2) if x >= 1 else round(x, 4)


def merge(results, parks):
    """Rows of one list that match one park are added (parts).  When several lists give a size for one park,
    the best match wins (number > record id > name+kind, then list > hand copy, then queue order)."""
    final = {}
    for ii, res in enumerate(results):
        groups, row_refs = {}, {}
        for m in res['matches']:
            groups.setdefault(m['ref'], []).append(m)
            row_refs.setdefault(m['row'], set()).add(m['ref'])
        for ref, ms in groups.items():
            units = sorted({m['unit'] for m in ms})
            how = ', '.join(sorted({m['rule'] for m in ms}, key=RULE_RANK.get))
            flags = []
            if any(len(row_refs[m['row']]) > 1 for m in ms):
                flags.append('same row matched to two parks')
            if len(ms) > 1 and len({(m['row_name'].lower(), m['value']) for m in ms}) < len(ms):
                flags.append('possible duplicate rows (same name and size added twice)')
            names = list(dict.fromkeys(m['row_name'] for m in ms))
            unit_label = UNIT_LABEL.get(units[0], units[0]) if len(units) == 1 else 'mixed'
            ag = res['agency'].replace(' (hand copy)', '')
            if len(ms) == 1:
                why = f'{res["agency"]} row "{ms[0]["row_name"]}" ({fmt_num(ms[0]["value"])} {unit_label}): {ms[0]["why"]}'
            else:
                why = (f'{len(ms)} rows of {res["agency"]} added together ({"; ".join(names[:6])}'
                       f'{" ..." if len(names) > 6 else ""}); every row matched {ref} by {how}')
            e = {'acres': sum(m['acres'] for m in ms),
                 'value_given': ms[0]['value'] if len(ms) == 1 else [m['value'] for m in ms],
                 'unit_given': unit_label, 'agency': ag, 'record_name': ' + '.join(names),
                 'how': ms[0]['how_text'] or how, 'match': how, 'parts': len(ms),
                 'source_url': ms[0].get('source_url') or res['source_url'] or '', 'read_date': res['read_date'],
                 'why': why, 'flags': flags,
                 '_rank': (min(RULE_RANK[m['rule']] for m in ms), 1 if res['kind'] == 'hand' else 0, ii),
                 '_others': []}
            old = final.get(ref)
            if old is None:
                final[ref] = e
            elif e['_rank'] < old['_rank']:
                e['_others'] = old.pop('_others') + [old]
                final[ref] = e
            else:
                old['_others'].append(e)
    for ref, e in final.items():
        a = e['acres']
        if a < 0.1:
            e['flags'].append('under 0.1 acres')
        if a > 20_000_000:
            e['flags'].append('over 20 million acres')
        ol = parks.outline.get(ref)
        if ol and a > 50 * ol:
            e['flags'].append(f'over 50x the current outline ({ol:,.0f} ac)')
        others = e.pop('_others')
        if others:
            e['other_sources'] = [{'agency': o['agency'], 'acres': r2(o['acres']), 'how': o['how'],
                                   'source_url': o['source_url']} for o in others]
            if any(abs(o['acres'] - a) > 0.1 * max(a, o['acres']) for o in others):
                e['flags'].append('another official list differs by more than 10%')
        if ol:
            e['outline_acres'] = r2(ol)
        e['acres'] = r2(a)
        e['park_name'] = parks.p.get(ref, {}).get('name', '')
        e.pop('_rank')
    return dict(sorted(final.items(), key=lambda kv: (rank(kv[0]), 0 if kv[0].startswith('US') else 1, kv[0])))


def write_outputs(out, results, parks, meta, answer=None):
    final = merge(results, parks)
    with open(os.path.join(out, 'acres.json'), 'w', encoding='utf-8') as f:
        json.dump(final, f, indent=1, ensure_ascii=False)
    with open(os.path.join(out, 'acres-list.json'), 'w', encoding='utf-8') as f:
        json.dump({r: e['acres'] for r, e in final.items()}, f, indent=1)
    with open(os.path.join(out, 'unmatched.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['agency', 'row_name', 'size', 'unit', 'why', 'area', 'source_url', 'read_date'])
        for res in results:
            for u in res['unmatched']:
                w.writerow([u['agency'], u['row_name'], u['size'], u['unit'], u['why'], u.get('area', ''),
                            u['source_url'], u['read_date']])
    n_unm = sum(len(r['unmatched']) for r in results)
    L = [f'# kpc_acres report ({meta["read_date"]})', '',
         f'- tool version {VERSION}; areas: {meta["areas_label"]}',
         f'- work items: {meta["done"]} done of {meta["total"]}' + (
             f' - **PARTIAL: time ran out, {meta["total"] - meta["done"]} left; run again with --resume**'
             if meta['done'] < meta['total'] else ' - complete'),
         f'- parks with an official size: {len(final)}; flagged: {sum(1 for e in final.values() if e["flags"])}; '
         f'unmatched rows: {n_unm}',
         f'- web requests this run: {meta.get("requests", 0)}', '',
         '## One line per agency', '']
    for ii, res in enumerate(results):
        matched_rows = len({m['row'] for m in res['matches']})
        refs = {m['ref'] for m in res['matches']}
        nflag = sum(1 for r in refs if final.get(r, {}).get('flags'))
        L.append(f'- {res["area"] or "?"} | {res["agency"]} | {res["status"]} | rows read {res["rows_read"]}, '
                 f'matched {matched_rows}, unmatched {len(res["unmatched"])}, flagged {nflag}'
                 + (f' | {res["source_url"]}' if res.get('source_url') else ''))
    wma_sp = 0
    for ref, e in final.items():
        pk = parks.p.get(ref, {}).get('kind')
        for nm in e['record_name'].split(' + '):
            if {pk, name_kind(nm)[0]} == {'wma', 'state_park'} and pk not in kinds_of(nm, name_kind(nm)[0]):
                wma_sp += 1
    fc = {}
    for e in final.values():
        for fl in e['flags']:
            k = re.sub(r' \(.*\)$', '', fl)
            fc[k] = fc.get(k, 0) + 1
    L += ['', '## Checks', '', f'- WMA matched to a state park (must be 0): {wma_sp}',
          '- flags: ' + ('; '.join(f'{k}: {v}' for k, v in sorted(fc.items())) or 'none')]
    if answer:
        common = [r for r in final if r in answer]
        agree = [r for r in common if abs(final[r]['acres'] - answer[r]) <= 0.10 * answer[r]]
        pct = 100.0 * len(agree) / len(common) if common else 0.0
        L.append(f'- answer key: {len(common)} matched parks have a hand-checked size; {len(agree)} agree within '
                 f'10% ({pct:.1f}%; pass mark 95%)')
        for r in [r for r in common if r not in agree][:60]:
            L.append(f'  - {r} {final[r]["park_name"]}: list {final[r]["acres"]:,.0f} ac vs key {answer[r]:,.0f} ac '
                     f'({final[r]["agency"]}, {final[r]["match"]})')
    L += ['', 'These sizes are candidates for the waiting room (kind `acres`); the club\'s rules and chat 11 decide.', '']
    with open(os.path.join(out, 'report.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(L))
    return final


# ----------------------------------------------------------------------------------------------------------
# Main run
# ----------------------------------------------------------------------------------------------------------
def build_queue(cfgs, hand, areas_filter):
    items = [{'kind': 'list', 'key': item_key('list', c['agency'], c['area'], c.get('url')), 'area': c['area'],
              'cfg': c, 'agency': c['agency']} for c in cfgs]
    groups = {}
    for h in hand:
        ar = norm_area(h.get('_area')) if h.get('_area') else None
        groups.setdefault((str(h.get('_agency') or 'unknown agency'), ar), []).append(h)
    for (ag, ar), rows in groups.items():
        items.append({'kind': 'hand', 'key': item_key('hand', ag, ar, len(rows)), 'area': ar, 'agency': ag,
                      'rows': rows})

    def in_areas(a):
        if not areas_filter or a is None:
            return True
        if a.endswith('*'):
            return any(x.startswith(a[:3]) for x in areas_filter)
        return a in areas_filter
    items = [it for it in items if in_areas(it['area'])]

    def order(it):
        a = it['area'] or ''
        return (rank(a) if a else (4, 0), 0 if a.startswith('US') else 1 if a.startswith('CA') else 2,
                areas_filter.index(a) if a in areas_filter else 9999, a, 0 if it['kind'] == 'list' else 1,
                it['agency'])
    items.sort(key=order)
    return items


def run(args, transport=None, sleep=time.sleep, gap=2.0):
    deadline = time.monotonic() + float(args.max_minutes) * 60
    research = args.acres_file or args.inp
    if not research or not os.path.exists(research):
        print(f'error: research file not found: {research}', file=sys.stderr)
        return EXIT_BAD_INPUT
    out = os.path.abspath(args.out)
    work = os.path.join(out, 'work')
    adir = os.path.join(work, 'agencies')
    os.makedirs(adir, exist_ok=True)
    state_path = os.path.join(out, 'state.json')
    state = {'done': {}}
    if args.resume and os.path.exists(state_path):
        with open(state_path) as f:
            state = json.load(f)
    elif not args.resume:
        for fn in os.listdir(adir):
            if fn.endswith('.json'):
                os.remove(os.path.join(adir, fn))
    try:
        cfgs, hand, fields = load_research(research)
    except Exception as e:
        print(f'error: research file not readable: {e}', file=sys.stderr)
        return EXIT_BAD_INPUT
    parks = Parks()
    load_parkinfo(args.parkinfo, parks)
    if args.keys:
        load_keys(args.keys, parks)
    answer = load_answer_key(args.answer_key) if getattr(args, 'answer_key', None) else {}
    all_areas = sorted({p['area'] for p in parks.p.values()} | {c['area'] for c in cfgs if c['area']})
    if args.areas:
        areas = [norm_area(a) or a.strip() for a in args.areas.split(',') if a.strip()]
        areas_label = ','.join(areas)
    else:
        areas = [a for a in all_areas if a.startswith('US-') and not a.endswith('*')] + \
                [a for a in all_areas if a.startswith('CA-') and not a.endswith('*')]
        areas_label = 'all US, then all Canada'
    queue = build_queue(cfgs, hand, areas)
    if args.limit:
        queue = queue[:int(args.limit)]
    fetcher = Fetcher(transport=transport, cache_dir=args.cache or os.path.join(work, 'cache'), gap=gap, sleep=sleep,
                      offline=getattr(args, 'offline', False))
    matcher = Matcher(parks, Counties(fetcher, enabled=not getattr(args, 'no_county_check', False)))
    read_date = today()
    with open(os.path.join(work, 'fields_seen.json'), 'w') as f:
        json.dump({'research_fields': fields, 'agencies': len(cfgs), 'hand_rows': len(hand),
                   'parks_loaded': len(parks.p), 'areas': areas}, f, indent=1)
    timed_out = False
    for n, it in enumerate(queue):
        fp = os.path.join(adir, it['key'] + '.json')
        if it['key'] in state['done'] and os.path.exists(fp):
            continue
        if time.monotonic() > deadline:
            timed_out = True
            break
        try:
            if it['kind'] == 'list':
                res = run_list_item(it['cfg'], fetcher, matcher, read_date, areas)
            else:
                res = run_hand_item(it['agency'], it['area'], it['rows'], matcher, read_date, areas)
        except Exception as e:  # never stop the run for one bad item
            res = new_result(it['kind'], it['agency'], it['area'], (it.get('cfg') or {}).get('url'), read_date,
                             f'failed: {type(e).__name__}: {e}'[:300])
        with open(fp, 'w', encoding='utf-8') as f:
            json.dump(res, f, ensure_ascii=False)
        state['done'][it['key']] = res['status']
        with open(state_path + '.tmp', 'w') as f:
            json.dump(state, f, indent=1)
        os.replace(state_path + '.tmp', state_path)
        if not getattr(args, 'quiet', False):
            print(f'[{n + 1}/{len(queue)}] {res["area"]} {res["agency"]}: {res["status"]} '
                  f'({len(res["matches"])} matched, {len(res["unmatched"])} unmatched)', flush=True)
    results = []
    for it in queue:
        fp = os.path.join(adir, it['key'] + '.json')
        if it['key'] in state['done'] and os.path.exists(fp):
            with open(fp, encoding='utf-8') as f:
                results.append(json.load(f))
    meta = {'read_date': read_date, 'areas_label': areas_label, 'done': len(results), 'total': len(queue),
            'requests': fetcher.requests}
    write_outputs(out, results, parks, meta, answer)
    state['complete'] = len(results) == len(queue)
    with open(state_path, 'w') as f:
        json.dump(state, f, indent=1)
    if timed_out or len(results) < len(queue):
        if not getattr(args, 'quiet', False):
            print(f'time ran out: {len(queue) - len(results)} work items left; run again with --resume', flush=True)
        return EXIT_TIME
    return EXIT_DONE


# ----------------------------------------------------------------------------------------------------------
# Self-test (offline: every web answer comes from tests/fixtures through an injected transport)
# ----------------------------------------------------------------------------------------------------------
def selftest(update=False):
    tdir = os.path.join(HERE, 'tests')
    fx, exp = os.path.join(tdir, 'fixtures'), os.path.join(tdir, 'expected')
    fails = []

    def check(cond, what):
        if not cond:
            fails.append(what)

    # --- units, numbers, names
    check(abs(to_acres(10, 'ha') - 24.7105) < 1e-9, 'ha x 2.47105')
    check(abs(to_acres(1, 'km2') - 247.105) < 1e-9, 'km2 x 247.105')
    check(to_acres(2, 'sqmi') == 1280, 'sq mi x 640')
    check(abs(to_acres(10000, 'm2') - 2.47105) < 1e-9, 'm2 x 0.000247105')
    for s, u in (('Acres', 'acres'), ('GIS_Acres', 'acres'), ('Hectares', 'ha'), ('O_AREA_HA', 'ha'),
                 ('Area (ha)', 'ha'), ('km²', 'km2'), ('AREA_KM2', 'km2'), ('sq mi', 'sqmi'), ('Square Miles', 'sqmi'),
                 ('m²', 'm2'), ('Area (m2)', 'm2'), ('Area', None), ('Shape_Area', None)):
        check(norm_unit(s) == u, f'norm_unit({s!r}) = {norm_unit(s)!r}, want {u!r}')
    for s, v in (('1,234.5', 1234.5), ('1 234,5', 1234.5), ('12,5', 12.5), ('1,500', 1500.0), ('approx. 50 ac', 50.0),
                 ('1.234.567', 1234567.0), (17, 17.0), ('', None), ('n/a', None)):
        check(parse_size(s)[0] == v, f'parse_size({s!r}) = {parse_size(s)[0]!r}, want {v!r}')
    check(parse_size('50 ha')[1] == 'ha', 'unit inside the size text')
    check(name_kind('John James Audubon State Park State Nature Preserve')[0] == 'nature_preserve',
          'last kind phrase wins (a preserve inside a park is a preserve)')
    check(kinds_of('Knobs State Forest and WMA', 'wma') == {'wma', 'state_forest'}, 'joint name carries both kinds')
    check(kinds_of('Clay WMA', 'wma') == {'wma'}, 'plain name carries one kind')
    k1, c1, _ = name_kind('Green River Lake WMA')
    k2, c2, _ = name_kind('Green River Lake State Park')
    check(c1 == c2 == 'green river lake' and k1 == 'wma' and k2 == 'state_park', 'WMA and state park: same name, other kind')
    check(name_kind('Pine Mountain State Resort Park')[0] == 'state_park', 'a resort park is a state park')
    check('clay' in name_kind('Clay WMA - North Unit')[2], 'unit words dropped as a variant')
    check(name_kind('Mt. Vernon Nature Preserve')[1] == 'mount vernon', 'Mt -> Mount')
    check(norm_area('Kentucky') == 'US-KY' and norm_area('ON') == 'CA-ON' and norm_area('K-TN') == 'US-TN', 'areas')
    check(norm_ref('k-1234') == 'US-1234' and norm_ref('VE-0042') == 'CA-0042', 'old K-/VE- refs')
    check(parse_pdf_line('Blanton Forest   3,124 acres') == ('Blanton Forest', '3,124', 'acres'), 'PDF line parser')
    check(parse_pdf_line('Bad Branch 1985 2,639') is None, 'unsure PDF line is skipped')
    check(banned('https://overpass-api.de/api/interpreter') and banned('https://www.google.com/maps/d/x')
          and banned('https://www.protectedplanet.net/x') and banned('https://en.wikipedia.org/wiki/X')
          and not banned('https://storage.googleapis.com/ky-gov/x.csv')
          and not banned('https://kygisserver.ky.gov/arcgis/rest/services/x/MapServer/0'), 'banned sources')
    # --- research file shapes
    cf, hd, fields = load_research(os.path.join(fx, 'research-dict-shape.json'))
    check(len(cf) == 2 and len(hd) == 2 and {h['_agency'] for h in hd} == {'KDFWR'}, 'dict-of-dicts research shape')
    check({c['area'] for c in cf} == {'US-KY'} and any(c['size_col'] == 'ACRES' for c in cf), 'research field aliases')
    check(next(c for c in cf if c['agency'] == 'KDFWR')['kind'] == 'wma', 'kind word in "type" is a kind, not a format')
    # --- polite fetcher with a fake clock
    clock, waits, calls = [0.0], [], []

    def fsleep(s):
        waits.append(s)
        clock[0] += s

    def ftrans(url, headers):
        calls.append((url, headers['User-Agent']))
        if url.endswith('/robots.txt'):
            return 200, {}, b'User-agent: *\nDisallow: /private\n'
        if 'busy' in url:
            return 429, {}, b''
        if 'login' in url:
            return 401, {}, b''
        return 200, {}, b'ok'
    os.environ.setdefault('KPC_CONTACT', 'selftest@example.org')
    fz = Fetcher(transport=ftrans, gap=2.0, sleep=fsleep, clock=lambda: clock[0], backoff=(1, 1, 1))
    check(fz.get('https://a.example/x') == b'ok', 'fetch ok')
    fz.get('https://a.example/y')
    check(waits and all(abs(w - 2.0) < 1e-9 for w in waits), '2 s gap per host')
    check(calls[0][0].endswith('/robots.txt') and calls[0][1] == 'KPC park tools (' + os.environ['KPC_CONTACT'] + ')',
          'robots.txt first, User-Agent from KPC_CONTACT')
    for url, word in (('https://a.example/private/z', 'robots'), ('https://a.example/login', 'sign-in'),
                      ('https://a.example/busy', 'resting'), ('https://a.example/x2', 'resting'),
                      ('https://overpass-api.de/x', 'not allowed')):
        try:
            fz.get(url)
            check(False, f'{url} should fail')
        except FetchError as e:
            check(word in str(e), f'{url}: {e}')
    # --- full offline run on the fixtures
    with open(os.path.join(fx, 'routes.json')) as f:
        routes = json.load(f)

    def transport(url, headers):
        sp = urllib.parse.urlsplit(url)
        if sp.path == '/robots.txt':
            return 200, {}, b'User-agent: *\nDisallow: /secret\n'
        fn = routes.get(sp.netloc + sp.path)
        if isinstance(fn, dict):  # paged answers keyed by the offset parameter
            qs = urllib.parse.parse_qs(sp.query)
            off = (qs.get('resultOffset') or qs.get('offset') or qs.get('$offset') or ['0'])[0]
            fn = fn.get(off) or fn.get('default')
        if not fn:
            return 404, {}, b'not found'
        with open(os.path.join(fx, fn), 'rb') as f:
            return 200, {}, f.read()

    tmp = tempfile.mkdtemp(prefix='kpc_acres_selftest_')
    pdf_note = ''
    try:
        os.environ['KPC_TODAY'] = '2026-10-31'
        ns = argparse.Namespace(inp=os.path.join(fx, 'acres-research.json'), acres_file=None, out=tmp,
                                parkinfo=os.path.join(fx, 'parkinfo'), keys=os.path.join(fx, 'keys'),
                                areas='US-KY,US-TN,CA-ON', max_minutes=5, resume=False, limit=None, cache=None,
                                offline=False, no_county_check=False, quiet=True,
                                answer_key=os.path.join(fx, 'ky-answer-key.json'))
        code = run(ns, transport=transport, sleep=lambda s: None, gap=0.0)
        check(code == 0, f'run exit code {code}')
        got = {}
        for n in ('acres.json', 'acres-list.json', 'unmatched.csv', 'report.md'):
            with open(os.path.join(tmp, n), encoding='utf-8') as f:
                got[n] = f.read()
        acres, lst = json.loads(got['acres.json']), json.loads(got['acres-list.json'])
        unm = list(csv.DictReader(io.StringIO(got['unmatched.csv'])))
        rep = got['report.md']
        uw = lambda name: next((u['why'] for u in unm if u['row_name'] == name), '')
        a = lambda ref, k, d=None: acres.get(ref, {}).get(k, d)
        check(a('US-1001', 'match') == 'name+kind' and a('US-1001', 'acres') == 2187.0, 'CSV: state park by name+kind')
        check('county Barren agrees' in a('US-1001', 'why', ''), 'rule c: county agrees with the pin')
        check(a('US-1002', 'acres') == 2000.0 and a('US-1002', 'parts') == 2, 'HTML: two WMA tracts added (parts=2)')
        check('US-1003' not in acres and 'different kind' in uw('Taylor Lake WMA'),
              '"Taylor Lake WMA" never matches "Taylor Lake State Park"')
        check(a('US-1004', 'match') == 'number', 'HTML: match by park number')
        check(a('US-1005', 'match') == 'record id' and abs(a('US-1005', 'acres') - 863.16) < 0.01,
              'ArcGIS: match by key record id, ha -> acres')
        check(abs(a('US-1006', 'acres', 0) - 247.1) < 0.01, 'ArcGIS second page read (paging)')
        check(a('US-2001', 'acres') == 640.0, 'XLSX: sq mi -> acres')
        check(abs(a('US-2002', 'acres', 0) - 494.21) < 0.01, 'XLSX: m² in the size text -> acres')
        check(abs(a('CA-3001', 'acres', 0) - 2471.05) < 0.01, 'CKAN: km² -> acres (Ontario)')
        check('under 0.1 acres' in a('US-1007', 'flags', []), 'flag: under 0.1 acres')
        check('over 20 million acres' in a('CA-3002', 'flags', []), 'flag: over 20 million acres')
        check(any(f.startswith('over 50x') for f in a('US-1008', 'flags', [])), 'flag: over 50x the outline')
        check('same row matched to two parks' in a('US-1009', 'flags', []) and
              'same row matched to two parks' in a('US-1010', 'flags', []), 'flag: one row matched to two parks')
        check(str(a('US-1011', 'how', '')).startswith('hand copy (KY Office of Nature Preserves, https://'),
              'hand size: how = "hand copy (<agency>, <page>)"')
        check('km from the pin' in uw('Cedar Creek WMA'), 'rule c: point over 25 km -> unmatched')
        check('county' in uw('Rock Bridge WMA'), 'rule c: county disagrees -> unmatched')
        check('ambiguous' in uw('Green Fork Wildlife Management Area'), 'two parks fit -> unmatched')
        check('no POTA park' in uw('Unknown Hollow WMA'), 'no park -> unmatched')
        check(uw('Clay WMA').startswith('unit unknown'), 'unknown unit -> unmatched')
        check(not any(u['row_name'].lower().startswith('total') for u in unm), 'total rows are skipped')
        check('blocked by robots.txt' in rep, 'robots-blocked list is reported, run goes on')
        check('page only' in rep and 'no list' in rep, 'page-only / no-list agencies are reported')
        check('WMA matched to a state park (must be 0): 0' in rep, 'report: no WMA matched to a state park')
        check('answer key: 3 matched parks have a hand-checked size; 2 agree' in rep, 'report: answer-key agreement')
        check(all(e.get('source_url') and e.get('read_date') == '2026-10-31' and e.get('why') for e in acres.values()),
              'every acres row has source_url, read_date, why')
        check(all(u['source_url'] and u['read_date'] and u['why'] for u in unm), 'every unmatched row has its source')
        check(set(lst) == set(acres) and all(lst[r] == acres[r]['acres'] for r in lst), 'acres-list = {ref: acres}')
        check(list(acres)[0].startswith('US-') and list(acres)[-1].startswith('CA-'), 'US first, then Canada')
        outside = [p for p in os.listdir(tmp) if p not in ('acres.json', 'acres-list.json', 'unmatched.csv',
                                                            'report.md', 'state.json', 'work', 'resume')]
        check(not outside, f'unexpected files in --out: {outside}')
        # --- time-out, exit 3, --resume, --limit
        t2 = os.path.join(tmp, 'resume')
        check(run(argparse.Namespace(**dict(vars(ns), out=t2, max_minutes=0)), transport=transport,
                  sleep=lambda s: None, gap=0.0) == 3, 'exit 3 when time runs out')
        check('PARTIAL' in open(os.path.join(t2, 'report.md'), encoding='utf-8').read(), 'partial report says so')
        check(run(argparse.Namespace(**dict(vars(ns), out=t2, resume=True)), transport=transport,
                  sleep=lambda s: None, gap=0.0) == 0, '--resume finishes with exit 0')
        with open(os.path.join(t2, 'acres-list.json')) as f:
            check(json.load(f) == lst, 'resumed run gives the same list')
        t3 = os.path.join(tmp, 'resume', 'limit')
        check(run(argparse.Namespace(**dict(vars(ns), out=t3, limit=2)), transport=transport,
                  sleep=lambda s: None, gap=0.0) == 0, '--limit 2')
        with open(os.path.join(t3, 'state.json')) as f:
            check(len(json.load(f)['done']) == 2, '--limit 2 does 2 items')
        # --- expected files
        cmp = {k: v for k, v in got.items() if k != 'report.md'}
        if update:
            os.makedirs(exp, exist_ok=True)
            for n, txt in got.items():
                with open(os.path.join(exp, n), 'w', encoding='utf-8') as f:
                    f.write(txt)
        else:
            for n, txt in cmp.items():
                p = os.path.join(exp, n)
                ok = os.path.exists(p) and open(p, encoding='utf-8').read() == txt
                check(ok, f'output {n} differs from tests/expected/{n}')
        # --- optional PDF table reader
        try:
            import pypdf  # noqa: F401
            with open(os.path.join(fx, 'preserves.pdf'), 'rb') as f:
                recs = read_pdf_records(f.read(), {})
            check(any(r['name'] == 'Blanton Forest' and r['size'] == '3,124' for r in recs), 'PDF table read with pypdf')
            check(not any(r['name'].startswith('Bad Branch') for r in recs), 'unsure PDF row skipped')
            pdf_note = 'PDF file read with pypdf'
        except ImportError:
            pdf_note = 'pypdf not installed: PDF file test skipped, line parser tested'
    finally:
        os.environ.pop('KPC_TODAY', None)
        shutil.rmtree(tmp, ignore_errors=True)
    if fails:
        print('FAIL')
        for f_ in fails:
            print('  -', f_)
        return 1
    print(f'PASS ({pdf_note})')
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description='KPC official acres list (kpc_acres)')
    ap.add_argument('--in', dest='inp', help='the acres research file (acres-us-ca-oct31.json)')
    ap.add_argument('--acres-file', help='same as --in')
    ap.add_argument('--out', default='acres', help='output folder (default ./acres)')
    ap.add_argument('--parkinfo', default='data/parkinfo', help='POTA park pins folder or file')
    ap.add_argument('--keys', default='data', help='folder holding us-key/ and ca-key/')
    ap.add_argument('--areas', help='US-KY,US-TN,CA-ON (default: every US area, then every Canadian one)')
    ap.add_argument('--max-minutes', type=float, default=50)
    ap.add_argument('--resume', action='store_true')
    ap.add_argument('--limit', type=int)
    ap.add_argument('--cache', help='download cache folder (default <out>/work/cache)')
    ap.add_argument('--answer-key', help='optional ky-answer-key.json: report the agreement within 10%%')
    ap.add_argument('--offline', action='store_true', help='cache only, no network')
    ap.add_argument('--no-county-check', action='store_true', help='skip the Census county lookup (rule c)')
    ap.add_argument('--quiet', action='store_true')
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--update-expected', action='store_true', help=argparse.SUPPRESS)
    a = ap.parse_args(argv)
    if a.selftest or a.update_expected:
        return selftest(update=a.update_expected)
    return run(a)


if __name__ == '__main__':
    sys.exit(main())
