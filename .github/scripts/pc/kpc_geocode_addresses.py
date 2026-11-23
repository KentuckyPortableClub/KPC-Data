#!/usr/bin/env python3
"""kpc_geocode_addresses.py (22 Nov 2026, owner 10:26 PM: "run the address through a script one time and convert it into some
format the matching tool could use"): turns the US street addresses the page reader found into map points, ONE time, and writes
them into the reader's facts as page points, so the key's match checks use them exactly like a map point printed on the page.

How: the US Census Bureau's free address lookup (geocoding.geo.census.gov, batch: up to 10,000 addresses in one request, no
key). robots.txt is read first, through kpc_manners, and wins. Only street addresses with a US state and ZIP are sent (a P.O. box
has no place on the ground and is never sent). Each address is asked once: out\\geocoded.json keeps every answer, and a later run
asks only for new addresses. A point is kept only within 300 km of POTA's pin (the reader's own point_ok rule) and carries the
address's role (park, visitor centre, office, mailing, unknown); the match checks never use an office or mailing point.
Canadian civic addresses go to Natural Resources Canada's free Geolocator, one request per address at the manners pace
(22 Nov 10:35 PM); a postal-code-area answer is never taken.
Counts only, never a park name.
  python kpc_geocode_addresses.py --out out --scripts scripts        (--selftest)"""
import argparse, csv, datetime, io, json, os, pathlib, re, sys, tempfile, uuid

URL = 'https://geocoding.geo.census.gov/geocoder/locations/addressbatch'
BATCH = 9000
SHARED_KM = 5.0     # an address printed on several parks' pages is used only within this distance of the park's pin
STATES = ('AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA '
          'RI SC SD TN TX UT VT VA WA WV WI WY PR VI GU').split()
NAMES = {'alabama': 'AL', 'alaska': 'AK', 'arizona': 'AZ', 'arkansas': 'AR', 'california': 'CA', 'colorado': 'CO',
         'connecticut': 'CT', 'delaware': 'DE', 'district of columbia': 'DC', 'florida': 'FL', 'georgia': 'GA', 'hawaii': 'HI',
         'idaho': 'ID', 'illinois': 'IL', 'indiana': 'IN', 'iowa': 'IA', 'kansas': 'KS', 'kentucky': 'KY', 'louisiana': 'LA',
         'maine': 'ME', 'maryland': 'MD', 'massachusetts': 'MA', 'michigan': 'MI', 'minnesota': 'MN', 'mississippi': 'MS',
         'missouri': 'MO', 'montana': 'MT', 'nebraska': 'NE', 'nevada': 'NV', 'new hampshire': 'NH', 'new jersey': 'NJ',
         'new mexico': 'NM', 'new york': 'NY', 'north carolina': 'NC', 'north dakota': 'ND', 'ohio': 'OH', 'oklahoma': 'OK',
         'oregon': 'OR', 'pennsylvania': 'PA', 'rhode island': 'RI', 'south carolina': 'SC', 'south dakota': 'SD',
         'tennessee': 'TN', 'texas': 'TX', 'utah': 'UT', 'vermont': 'VT', 'virginia': 'VA', 'washington': 'WA',
         'west virginia': 'WV', 'wisconsin': 'WI', 'wyoming': 'WY', 'puerto rico': 'PR'}
TAIL = re.compile(r'^(?P<head>.+?)[,\s]+(?P<state>' + '|'.join(STATES) + '|' + '|'.join(sorted(NAMES, key=len, reverse=True)) +
                  r')\.?,?\s+(?P<zip>\d{5})(?:-\d{4})?\s*$', re.I)
STREET_END = re.compile(r'(?i)^(?P<street>.*?\b(?:road|rd|drive|dr|street|st|avenue|ave|boulevard|blvd|highway|hwy|lane|ln|way|pike|'
                        r'loop|parkway|pkwy|circle|cir|court|ct|trail|trl|route|rte|place|pl|terrace|ter|run|turnpike|tpke|byway|path|'
                        r'row|square|sq|crossing|bypass|cove|hollow|ridge|point|landing|plaza|spur|bend|grade)\.?(?:\s+\d{1,5}[a-z]?)?'
                        r'(?:\s+(?:[NSEW]{1,2}|north|south|east|west))?)\s+(?P<city>[A-Z][\w.\'-]+(?:\s+[A-Z][\w.\'-]+){0,3})$')


_ADDR = [None]


def _clean(t):
    """22 Nov 11:15 PM: an address read before the 22 Nov fixes can carry words around it ('Reservations 800-... Address 122 Test
    Road Testville, GA 30738 Dade County GPS Coordinates'): the reader's own address finder takes out just the address."""
    if not _ADDR[0]:
        try:
            import kpc_park_pages_rules as R
            _ADDR[0] = R.ADDR_RX
        except Exception:  # noqa: BLE001
            _ADDR[0] = None
    t = re.sub(r'\s+,', ',', t)
    t = re.sub(r'\b(?:1[-.\s]?)?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}\b|\b\d{3}-\d{4}\b', ' ', t)   # phone numbers out first
    m = _ADDR[0].search(t) if _ADDR[0] else None
    return ' '.join(m.group(0).split()) if m else t


def split_address(text):
    """'1217 Test Lake Road Testden, IN 47106' -> (street, city, state, zip), or None when it is not a US street address."""
    t = _clean(' '.join(str(text or '').replace('\n', ', ').split()))
    if re.search(r'(?i)\b(?:p\.?\s*o\.?\s*box|box\s+\d)', t):
        return None                                  # a mailbox has no place on the ground
    m = TAIL.match(t)
    if not m:
        return None
    st = m.group('state')
    st = NAMES.get(st.lower(), st.upper())
    head = m.group('head').strip(' ,')
    if ',' in head:
        street, city = head.rsplit(',', 1)
    else:
        s2 = STREET_END.match(head)
        if not s2:
            return None
        street, city = s2.group('street'), s2.group('city')
    street, city = street.strip(' ,'), city.strip(' ,')
    if not re.match(r'^\d', street) or not city:
        return None
    return street, city, st, m.group('zip')


CA_TAIL = re.compile(r'^(?P<head>.+?)[,\s]+\(?(?P<prov>AB|BC|MB|NB|NL|NS|NT|NU|ON|PE|QC|SK|YT|Alberta|British Columbia|Manitoba|New Brunswick|'
                     r'Newfoundland(?: and Labrador)?|Nova Scotia|Northwest Territories|Nunavut|Ontario|Prince Edward Island|Qu[eé]bec|'
                     r'Saskatchewan|Yukon)\)?\.?,?\s+(?P<pc>[A-Z]\d[A-Z][ -]?\d[A-Z]\d)\s*$', re.I)
CA_URL = 'https://geolocator.api.geo.ca/'


def canada_address(text):
    """A Canadian civic address (a number first, a province and a postal code at the end), or None. Never a mailbox."""
    t = ' '.join(str(text or '').replace('\n', ', ').split())
    # 22 Nov 11:20 PM: Ontario prints 'c/o X Provincial Park PO Box 252 4853 Highway 11/17 Town, ON P0T 1W0': the mailbox part is
    # taken out and the street address kept (a text that is ONLY a mailbox still never goes)
    t = re.sub(r'(?i)\b(?:p\.?\s*o\.?\s*box|c\.?\s*p\.?|case postale)\s+\d+\b,?', ' ', t)
    t = _clean(t)
    if re.search(r'(?i)\bbox\s+\d', t) or not re.match(r'^\d', t):
        return None
    return t if CA_TAIL.match(t) else None


def canada_lookup(M, text):
    """Natural Resources Canada's Geolocator (free, government; one address per request, at the manners pace).
    -> (lat, lon, kind) for a street-level answer, else None. A postal-code-area answer (fsa) is never taken."""
    import urllib.parse
    st, _h, body, _f = M.get(CA_URL + '?' + urllib.parse.urlencode({'q': text, 'lang': 'en', 'keys': 'locate'}))
    if st != 200 or not body:
        return None
    try:
        items = json.loads(body.decode('utf-8', 'replace') if isinstance(body, bytes) else body)
    except ValueError:
        return None
    for it in items if isinstance(items, list) else []:
        if not isinstance(it, dict) or str(it.get('key') or 'locate') not in ('locate',):
            continue
        g = it.get('geometry') or {}
        c = g.get('coordinates') if g.get('type') == 'Point' else None
        try:
            lon, lat = (float(c[0]), float(c[1])) if c else (float(it.get('lng', it.get('lon'))), float(it['lat']))
        except (TypeError, ValueError, KeyError, IndexError):
            continue
        kind = str(it.get('qualifier') or it.get('type') or it.get('category') or '')
        if re.search(r'(?i)fsa|postal|province|city|municipal', kind):
            continue
        return round(lat, 6), round(lon, 6), kind[:40]
    return None


def post_batch(rows, timeout=600):
    """rows = [(id, street, city, state, zip)] -> {id: (lat, lon, match type)} from the Census batch lookup."""
    import urllib.request
    buf = io.StringIO()
    w = csv.writer(buf)
    for r in rows: w.writerow(r)
    b = '----KPC' + uuid.uuid4().hex
    body = (f'--{b}\r\nContent-Disposition: form-data; name="benchmark"\r\n\r\nPublic_AR_Current\r\n'
            f'--{b}\r\nContent-Disposition: form-data; name="addressFile"; filename="kpc.csv"\r\nContent-Type: text/csv\r\n\r\n'
            ).encode() + buf.getvalue().encode('utf-8') + f'\r\n--{b}--\r\n'.encode()
    req = urllib.request.Request(URL, data=body, method='POST', headers={
        'Content-Type': f'multipart/form-data; boundary={b}',
        'User-Agent': 'KPC bot: address points (https://kentuckyportableclub.github.io/KPC-Links/; ham radio club; one batch request)'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        text = r.read().decode('utf-8', 'replace')
    return parse_answer(text)


def parse_answer(text):
    out = {}
    for row in csv.reader(io.StringIO(text)):
        if len(row) < 6 or row[2].strip().lower() != 'match':
            continue
        try:
            lon, lat = (float(x) for x in row[5].split(','))
        except ValueError:
            continue
        out[row[0]] = (round(lat, 6), round(lon, 6), row[3].strip())
    return out


def robots_allow(scripts):
    """kpc_manners decides (robots.txt + the host rules). False = nothing is sent this run."""
    sys.path.insert(0, str(pathlib.Path(scripts).resolve()))
    from kpc_manners import Manners
    return Manners('KPC address points').robots_ok(URL)


def _ca_manners(scripts):
    sys.path.insert(0, str(pathlib.Path(scripts).resolve()))
    from kpc_manners import Manners
    return Manners('KPC address points')


# ---------------------------------------------------------------------------------------------------------------------
# 23 Nov 2026 (owner 4:11 AM: "How many 2 miles east of is they ... do all 3"): TOWN POINTS. A page that says '2 miles east of
# Shiocton' gives a town, a distance and a direction (the reader keeps them in location.offsets). The town's own point comes
# from a government town list, checked live that morning:
#   US: the Census Bureau's Gazetteer place files, one small text file per state
#       (www2.census.gov/geo/docs/maps-data/data/gazetteer/2024_Gazetteer/2024_gaz_place_<state number>.txt; columns by name:
#       USPS, NAME, INTPTLAT, INTPTLONG; tabs in 2024, bars in 2026: both are read). Each state's file is fetched once.
#   Canada: Natural Resources Canada's Geolocator place names (keys=geonames: name, province, category, lat, lng). Each town
#       once. Lakes, rivers and other features of the same name are passed over.
# The point made from it is APPROXIMATE (road miles, a town's middle): it goes in location.near with how far off it may be
# (within_km), NEVER in location.coords, so nothing reads it as the page's own point. A made point more than NEAR_MAX_KM from
# POTA's pin is the wrong town and is left out. Any failure here is one printed line: the address points are never held up.
TOWN_URL = 'https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2024_Gazetteer/2024_gaz_place_%s.txt'
FIPS = dict(zip(STATES[:51], '01 02 04 05 06 08 09 10 11 12 13 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 '
                             '39 40 41 42 44 45 46 47 48 49 50 51 53 54 55 56'.split()))
BEARING = {'N': 0, 'NE': 45, 'E': 90, 'SE': 135, 'S': 180, 'SW': 225, 'W': 270, 'NW': 315}
NEAR_MAX_KM = 60.0       # a made point farther than this from POTA's pin: the wrong town of that name
TOWN_MAX_KM = 150.0      # the named town itself must be within this distance of POTA's pin
CA_TOWNS_A_RUN = 1500
PLACE_KIND = re.compile(r'\s+(city and borough|consolidated government|unified government|metropolitan government|metro government|'
                        r'charter township|urban county|municipality|township|borough|village|city|town|CDP|plantation|comunidad|'
                        r'zona urbana|corporation)(\s+\(balance\))?\s*$', re.I)
NOT_A_TOWN = re.compile(r'(?i)lake|river|creek|brook|stream|mount|peak|hill|ridge|island|bay|cove|point|cape|rapids|falls|channel|park|'
                        r'reserve|forest|glacier|valley|marsh|pond|beach|shoal|rock|spring|canal|dam|bridge|railway|school|library|church')


def norm_town(s):
    import unicodedata
    t = unicodedata.normalize('NFKD', str(s or '')).encode('ascii', 'ignore').decode('ascii').lower()
    t = re.sub(r"['’`]", '', t)
    t = re.sub(r'\bsaint\b|\bste?\b\.?', 'st', t)
    t = re.sub(r'\bmount\b|\bmt\b\.?', 'mt', t)
    t = re.sub(r'\bfort\b|\bft\b\.?', 'ft', t)
    return ' '.join(re.sub(r'[^a-z0-9]+', ' ', t).split())


def parse_places(text):
    """A Census Gazetteer place file -> {town name (normalised): [(lat, lon), ...]}. Columns are found by their names, so the
    2024 layout (tabs) and the 2026 layout (bars, one more column) are both read."""
    lines = [ln for ln in str(text or '').splitlines() if ln.strip()]
    if not lines:
        return {}
    sep = '|' if '|' in lines[0] else '\t'
    head = [h.strip().upper() for h in lines[0].split(sep)]
    try:
        ni, la, lo = head.index('NAME'), head.index('INTPTLAT'), head.index('INTPTLONG')
    except ValueError:
        return {}
    out = {}
    for ln in lines[1:]:
        c = ln.split(sep)
        if len(c) <= max(ni, la, lo):
            continue
        try:
            pt = (float(c[la].strip()), float(c[lo].strip()))
        except ValueError:
            continue
        k = norm_town(PLACE_KIND.sub('', c[ni].strip()))
        if k:
            out.setdefault(k, []).append(pt)
    return out


def offset_point(lat, lon, km, direction):
    import math
    b = math.radians(BEARING[direction])
    return (round(lat + km * math.cos(b) / 110.574, 5),
            round(lon + km * math.sin(b) / (111.320 * max(0.2, math.cos(math.radians(lat)))), 5))


def _km(a, b):
    import math
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 6371.0088 * 2 * math.asin(min(1.0, math.sqrt(h)))


def us_places_live(M, st):
    """One state's Census place file, through the manners (robots.txt and pace first). -> text or None."""
    url = TOWN_URL % FIPS[st]
    if not M.robots_ok(url):
        return None
    code, _h, body, _f = M.get(url)
    if code != 200 or not body:
        return None
    return body.decode('utf-8', 'replace') if isinstance(body, bytes) else str(body)


def ca_places_live(M, town):
    """Natural Resources Canada's place names for one town name -> [[lat, lon, category, province], ...] (exact name only)."""
    import urllib.parse
    code, _h, body, _f = M.get(CA_URL + '?' + urllib.parse.urlencode({'q': town, 'lang': 'en', 'keys': 'geonames'}))
    if code != 200 or not body:
        return None
    try:
        items = json.loads(body.decode('utf-8', 'replace') if isinstance(body, bytes) else body)
    except ValueError:
        return None
    want, out = norm_town(town), []
    for it in items if isinstance(items, list) else []:
        if not isinstance(it, dict) or str(it.get('key') or '') != 'geonames' or norm_town(it.get('name')) != want:
            continue
        cat = str(it.get('category') or '')
        if NOT_A_TOWN.search(cat):
            continue
        try:
            out.append([round(float(it['lat']), 5), round(float(it['lng']), 5), cat[:30], str(it.get('province') or '')[:30]])
        except (TypeError, ValueError, KeyError):
            continue
    return out


# 23 Nov 2026 5:24 AM (owner: "I dont want key bots to do internet stuff"): COUNTY AREAS, made HERE on the PC so that no key
# bot ever asks a website. A page that names its county ('is in northcentral Outagamie County') gets that county's middle
# point and size from the Census Bureau's Gazetteer county files, one small text file per state, read live that morning
# (www2.census.gov/geo/docs/maps-data/data/gazetteer/2024_Gazetteer/2024_gaz_counties_<state number>.txt; columns by name:
# NAME, ALAND, AWATER, INTPTLAT, INTPTLONG). It is saved with the page facts (location.county_areas: name, lat, lon,
# radius_km = the radius of a circle of the county's size). The key only reads that saved figure. US only.
COUNTY_URL = 'https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2024_Gazetteer/2024_gaz_counties_%s.txt'
COUNTY_KIND = re.compile(r'\s+(city and borough|census area|municipality|borough|county|parish|municipio|city)\s*$', re.I)


def parse_counties(text):
    """A Census Gazetteer county file -> {county name (normalised, 'County' / 'Parish' left off): [lat, lon, radius_km]}."""
    import math
    lines = [ln for ln in str(text or '').splitlines() if ln.strip()]
    if not lines:
        return {}
    sep = '|' if '|' in lines[0] else '\t'
    head = [h.strip().upper() for h in lines[0].split(sep)]
    try:
        ni, la, lo, al = head.index('NAME'), head.index('INTPTLAT'), head.index('INTPTLONG'), head.index('ALAND')
    except ValueError:
        return {}
    aw = head.index('AWATER') if 'AWATER' in head else None
    out = {}
    for ln in lines[1:]:
        c = ln.split(sep)
        if len(c) <= max(ni, la, lo, al):
            continue
        try:
            area = float(c[al].strip()) + (float(c[aw].strip()) if aw is not None and len(c) > aw and c[aw].strip() else 0.0)
            row = [round(float(c[la].strip()), 5), round(float(c[lo].strip()), 5), round(math.sqrt(max(area, 1.0) / math.pi) / 1000.0, 1)]
        except ValueError:
            continue
        k = norm_town(COUNTY_KIND.sub('', c[ni].strip()))
        if k:
            out[k] = row
    return out


def us_counties_live(M, st):
    url = COUNTY_URL % FIPS[st]
    if not M.robots_ok(url):
        return None
    code, _h, body, _f = M.get(url)
    if code != 200 or not body:
        return None
    return body.decode('utf-8', 'replace') if isinstance(body, bytes) else str(body)


def county_areas(files, out, scripts, manners=_ca_manners, us_counties=us_counties_live):
    """Fill location.county_areas for every US park whose own page (or own list row) names its county.
    -> (parks given a county area, county files fetched)."""
    cache = pathlib.Path(out) / 'towns'
    M, tables, looked, parks = None, {}, 0, 0

    def table(st):
        nonlocal M, looked
        if st in tables:
            return tables[st]
        f = cache / f'us-counties-{st}.json'
        if f.is_file():
            tables[st] = json.loads(f.read_text(encoding='utf-8'))
            return tables[st]
        tables[st] = {}
        if M is None:
            M = (manners(scripts) if manners else None) or False
        if st in FIPS and M:
            text = us_counties(M, st)
            looked += 1
            got = parse_counties(text) if text else {}
            if got:
                cache.mkdir(parents=True, exist_ok=True)
                f.write_text(json.dumps(got), encoding='utf-8')
                tables[st] = got
        return tables[st]

    for f, d in files.items():
        for ref, fact in (d.get('parks') or {}).items():
            if not isinstance(fact, dict) or fact.get('unofficial') or (fact.get('own_page') or {}).get('is') not in ('own', 'list-row'):
                continue
            loc = fact.get('location') or {}
            area = str(fact.get('area') or '')
            names = [str(x) for x in (loc.get('counties') or []) if str(x).strip()]
            if not names or not area.startswith('US-'):
                continue
            t = table(area[3:])
            rows = []
            for nm in names[:4]:
                r = t.get(norm_town(COUNTY_KIND.sub('', nm)))
                if r:
                    rows.append({'name': nm[:40], 'lat': r[0], 'lon': r[1], 'radius_km': r[2]})
            if rows != (loc.get('county_areas') or []):
                loc['county_areas'] = rows
                fact['location'] = loc
            if rows:
                parks += 1
    return parks, looked


def town_points(files, out, scripts, manners=_ca_manners, us_places=us_places_live, ca_places=ca_places_live):
    """Fill location.near from location.offsets for every park's own page (or its own list row). -> (points, parks, looked up)."""
    cache = pathlib.Path(out) / 'towns'
    try:
        sys.path.insert(0, str(pathlib.Path(scripts).resolve()))
        import kpc_park_pages_rules as R
        if not hasattr(R, 'offsets_in'): R = None
    except Exception:  # noqa: BLE001
        R = None
    M = None
    us, ca_path = {}, cache / 'ca.json'
    ca = json.loads(ca_path.read_text(encoding='utf-8')) if ca_path.is_file() else {}
    looked = ca_new = 0

    def the_manners():
        nonlocal M
        if M is None:
            M = manners(scripts) if manners else False
        return M or None

    def us_state(st):
        nonlocal looked
        if st in us:
            return us[st]
        f = cache / f'us-{st}.json'
        if f.is_file():
            us[st] = {k: [tuple(p) for p in v] for k, v in json.loads(f.read_text(encoding='utf-8')).items()}
            return us[st]
        us[st] = {}
        m = the_manners()
        if st in FIPS and m is not None:
            text = us_places(m, st)
            looked += 1
            got = parse_places(text) if text else {}
            if got:
                cache.mkdir(parents=True, exist_ok=True)
                f.write_text(json.dumps(got), encoding='utf-8')
                us[st] = got
        return us[st]

    def ca_town(name):
        nonlocal looked, ca_new
        k = norm_town(name)
        if k in ca:
            return ca[k]
        m = the_manners()
        if m is None or ca_new >= CA_TOWNS_A_RUN or (ca_new == 0 and not m.robots_ok(CA_URL)):
            return []
        got = ca_places(m, name)
        looked += 1; ca_new += 1
        if got is None:
            return []          # no answer this time: asked again on a later run
        ca[k] = got
        if ca_new % 50 == 0:
            cache.mkdir(parents=True, exist_ok=True)
            ca_path.write_text(json.dumps(ca), encoding='utf-8')
            print(f'  {ca_new} Canadian towns looked up', flush=True)
        return got

    points = parks = 0
    for f, d in files.items():
        for ref, fact in (d.get('parks') or {}).items():
            if not isinstance(fact, dict) or fact.get('unofficial') or (fact.get('own_page') or {}).get('is') not in ('own', 'list-row'):
                continue
            loc = fact.get('location') or {}
            if not loc.get('offsets') and R is not None and isinstance(loc.get('directions'), dict):
                # a page read before the reader kept offsets: its saved directions sentences hold them (no page is read again)
                sent = loc['directions'].get('sent')
                said = sent if isinstance(sent, str) else ' '.join(str(x) for x in (sent or []) if isinstance(x, str))
                try:
                    found = R.offsets_in(said) if said else []
                except Exception:  # noqa: BLE001
                    found = []
                if found:
                    loc['offsets'] = found
                    fact['location'] = loc
            offs = [o for o in (loc.get('offsets') or []) if isinstance(o, dict) and o.get('of') and o.get('dir') in BEARING]
            pin = (fact.get('pota') or {}).get('pin') or [None, None]
            if not offs or pin[0] is None:
                continue
            area = str(fact.get('area') or '')
            near = []
            for o in offs[:2]:
                try:
                    km = float(o.get('km'))
                except (TypeError, ValueError):
                    continue
                if area.startswith('US-'):
                    cands = us_state(area[3:]).get(norm_town(o['of'])) or []
                elif area == 'CA' or area.startswith('CA-'):
                    cands = [(c[0], c[1]) for c in ca_town(o['of'])]
                else:
                    cands = []
                cands = [c for c in cands if _km(c, pin) <= TOWN_MAX_KM]
                if not cands:
                    continue
                town = min(cands, key=lambda c: _km(c, pin))
                la, lo = offset_point(town[0], town[1], km, o['dir'])
                far = _km((la, lo), pin)
                if far > NEAR_MAX_KM:
                    continue
                near.append({'lat': la, 'lon': lo, 'within_km': max(3.0, round(0.5 * km, 1)),
                             'from': f"{o.get('km')} km {o['dir']} of {o['of']} (town list)"[:60], 'km_from_pin': round(far, 1)})
            if near != (loc.get('near') or []):
                fact.setdefault('location', {})['near'] = near
            if near:
                points += len(near); parks += 1
    if ca_new:
        cache.mkdir(parents=True, exist_ok=True)
        ca_path.write_text(json.dumps(ca), encoding='utf-8')
    return points, parks, looked


def run(out, scripts, today=None, poster=post_batch, allow=robots_allow, ca_manners=_ca_manners, ca_lookup=canada_lookup, towns=town_points,
        counties=county_areas):
    sys.path.insert(0, str(pathlib.Path(scripts).resolve()))
    import kpc_park_pages_rules as R
    today = today or datetime.date.today().isoformat()
    out = pathlib.Path(out)
    gp = out / 'geocoded.json'
    known = json.loads(gp.read_text(encoding='utf-8')) if gp.is_file() else {}   # address text -> [lat, lon, type] or [] (no match)
    files = {f: json.loads(f.read_text(encoding='utf-8')) for f in sorted((out / 'facts').glob('*.json'))}
    want, sent_ids, want_ca = {}, {}, set()
    # 22 Nov 11 PM (owner: "look at American parks"): an address printed on two or more parks' pages is an office the parks
    # share (WDFW's area manager, Washington State Parks' managing park), not where either park is: it is never used
    shared = {}
    for f, d in files.items():
        for ref, fact in (d.get('parks') or {}).items():
            for a in ((fact or {}).get('location') or {}).get('addresses') or []:
                shared.setdefault(a.get('text'), set()).add(ref)
    shared = {t for t, refs in shared.items() if len(refs) >= 2}
    for f, d in files.items():
        for ref, fact in (d.get('parks') or {}).items():
            if not isinstance(fact, dict) or fact.get('unofficial') or (fact.get('own_page') or {}).get('is') != 'own':
                continue
            for a in (fact.get('location') or {}).get('addresses') or []:
                if a.get('role') in ('office', 'mailing'):
                    continue                          # never a matching point anyway (an office or a mailbox)
                parts = split_address(a.get('text'))
                if parts and a['text'] not in known:
                    want.setdefault(a['text'], parts)
                elif not parts and canada_address(a.get('text')) and a['text'] not in known:
                    want_ca.add(a['text'])          # asked with its cleaned form (canada_address), kept under the text as read
    asked = 0
    if want:
        if not allow(scripts):
            print('The Census address lookup is not allowed right now (robots.txt or the host rules): nothing sent.', flush=True)
        else:
            items = list(want.items())
            for i in range(0, len(items), BATCH):
                chunk = items[i:i + BATCH]
                ids = {str(n): t for n, (t, _) in enumerate(chunk)}
                got = poster([(n, *p) for n, (_, p) in zip(ids, chunk)])
                asked += 1
                for n, t in ids.items():
                    known[t] = list(got[n]) if n in got else []
                gp.write_text(json.dumps(known, indent=0, sort_keys=True), encoding='utf-8')
    if want_ca:
        # 22 Nov 10:35 PM (owner: "I still got to get Canada address"): Canada has no free batch lookup, so one request per
        # address at the manners pace (robots.txt and the host rules first); each address once, like the US ones
        M = ca_manners(scripts) if ca_manners else None
        if M is None or not M.robots_ok(CA_URL):
            print('The Canada address lookup is not allowed right now (robots.txt or the host rules): nothing sent.', flush=True)
        else:
            print(f'Canada: {len(want_ca)} addresses, one request each (about {len(want_ca) * 2 // 60 + 1} minutes)...', flush=True)
            for n, t in enumerate(sorted(want_ca), 1):
                try: g = ca_lookup(M, canada_address(t) or t)
                except Exception: g = None  # noqa: BLE001
                known[t] = list(g) if g else []
                asked += 1
                if n % 50 == 0:
                    gp.write_text(json.dumps(known, indent=0, sort_keys=True), encoding='utf-8')
                    print(f'  {n} of {len(want_ca)} Canadian addresses looked up', flush=True)
            gp.write_text(json.dumps(known, indent=0, sort_keys=True), encoding='utf-8')
    added = parks = 0
    for f, d in files.items():
        for ref, fact in (d.get('parks') or {}).items():
            if not isinstance(fact, dict) or (fact.get('own_page') or {}).get('is') != 'own':
                continue
            loc = fact.setdefault('location', {})
            pin = (fact.get('pota') or {}).get('pin') or [None, None]
            have = {(round(c.get('lat', 0), 4), round(c.get('lon', 0), 4)) for c in loc.get('coords') or [] if isinstance(c, dict)}
            got_one = False
            for a in loc.get('addresses') or []:
                g = known.get(a.get('text'))
                if not g or a.get('role') in ('office', 'mailing'):
                    continue
                lat, lon = g[0], g[1]
                if not R.point_ok(lat, lon, fact.get('area') or '', pin) or (round(lat, 4), round(lon, 4)) in have:
                    continue
                km = R.haversine_km((lat, lon), (pin[0], pin[1])) if pin and pin[0] is not None else None
                if a.get('text') in shared and (km is None or km > SHARED_KM):
                    continue      # 22 Nov 11:15 PM: an address on several parks' pages counts only right by this park's pin (else a shared office)
                loc.setdefault('coords', []).append({'lat': lat, 'lon': lon, 'from': 'address (US Census lookup)' if split_address(a.get('text')) else 'address (Natural Resources Canada lookup)', 'role': a.get('role') or 'unknown',
                                                     'label': '', 'km_from_pin': round(km, 2) if km is not None else None, 'address': a.get('text')})
                have.add((round(lat, 4), round(lon, 4))); added += 1; got_one = True
            if got_one:
                parks += 1
                fact.setdefault('page', {})['read'] = max(str((fact.get('page') or {}).get('read') or ''), today)
    town_line = ''
    if towns:
        try:
            tp, tk, tl = towns(files, out, scripts)
            town_line = f' Town points (approximate, from "so far from a town"): {tp} for {tk} park(s), {tl} town list request(s).'
        except Exception as e:  # noqa: BLE001  (never holds up the address points)
            town_line = f' Town points: not made this run ({type(e).__name__}: {str(e)[:80]}).'
    if counties:
        try:
            cp, cl = counties(files, out, scripts)
            town_line += f' County areas (for the county a page names): {cp} park(s), {cl} county list request(s).'
        except Exception as e:  # noqa: BLE001  (never holds up the address points)
            town_line += f' County areas: not made this run ({type(e).__name__}: {str(e)[:80]}).'
    for f, d in files.items():
        tmp = f.with_name(f.name + '.tmp'); tmp.write_text(json.dumps(d, ensure_ascii=False), encoding='utf-8'); tmp.replace(f)
    matched = sum(1 for v in known.values() if v)
    print(f'Addresses turned into map points: {matched} of {len(known)} looked up ({len(want)} new this run, {asked} request(s)); '
          f'{added} map point(s) added to {parks} park(s).' + town_line, flush=True)
    return 0


def selftest():
    here = pathlib.Path(__file__).resolve().parent
    scripts = next((p for p in (here.parent, here.parent / 'page-reader' / 'scripts') if (p / 'kpc_park_pages_rules.py').is_file()), here.parent)
    sys.path.insert(0, str(scripts))
    ok = (split_address('1217 Test Lake Road Testden, IN 47106') == ('1217 Test Lake Road', 'Testden', 'IN', '47106')
          and split_address('17515 Highway 177, Fargo, GA 31631') == ('17515 Highway 177', 'Fargo', 'GA', '31631')
          and split_address('2680 Test Trace Parkway, Testtown, Mississippi 38804') == ('2680 Test Trace Parkway', 'Testtown', 'MS', '38804')
          and split_address('PO Box 12, Test Park, TX 79000') is None and split_address('4853 Highway 11 Testfalls, ON P0T 1W0') is None)
    calls = []

    def fake(rows):
        calls.append(len(rows))
        return {r[0]: (37.501, -85.001, 'Exact') for r in rows if 'Lake' in r[1]}

    with tempfile.TemporaryDirectory() as t:
        o = pathlib.Path(t); (o / 'facts').mkdir()
        own = {'is': 'own'}
        parks = {'K4-0001': {'area': 'US-KY', 'own_page': own, 'pota': {'pin': [37.5, -85.0]}, 'page': {'read': '2026-11-01'},
                             'location': {'addresses': [{'text': '1217 Test Lake Road Testden, KY 40000', 'role': 'park'}]}},
                 'K4-0002': {'area': 'US-KY', 'own_page': own, 'pota': {'pin': [37.5, -85.0]},
                             'location': {'addresses': [{'text': '9 Far Road Testville, KY 40001', 'role': 'unknown'},
                                                        {'text': 'PO Box 3, Testville, KY 40001', 'role': 'mailing'}]}},
                 'K4-0003': {'area': 'US-KY', 'own_page': {'is': 'list'}, 'pota': {'pin': [37.5, -85.0]},
                             'location': {'addresses': [{'text': '1 Test Lake Way Testo, KY 40002', 'role': 'park'}]}}}
        (o / 'facts' / 'US-KY.json').write_text(json.dumps({'parks': parks}), encoding='utf-8')
        class FakeCA:
            def robots_ok(self, u): return True
        ca_calls = []
        def fake_ca(M, t):
            ca_calls.append(t); return (45.401, -75.701, 'INTERPOLATED_POSITION') if 'Test Road' in t else None
        parks['K4-0004'] = {'area': 'CA-ON', 'own_page': own, 'pota': {'pin': [45.4, -75.7]},
                            'location': {'addresses': [{'text': '4998 Concession Test Road 7 Testton, ON K1A 0B1', 'role': 'park'},
                                                       {'text': 'PO Box 252, Testfalls, ON P0T 1W0', 'role': 'mailing'}]}}
        for r_ in ('K4-0005', 'K4-0006'):
            parks[r_] = {'area': 'US-KY', 'own_page': own, 'pota': {'pin': [37.5, -85.0]},
                         'location': {'addresses': [{'text': '50 Shared Lake Road Testvale, KY 40003', 'role': 'unknown'}]}}
        (o / 'facts' / 'US-KY.json').write_text(json.dumps({'parks': parks}), encoding='utf-8')
        run(o, scripts, '2026-11-22', poster=fake, allow=lambda s: True, ca_manners=lambda s: FakeCA(), ca_lookup=fake_ca)
        d = json.loads((o / 'facts' / 'US-KY.json').read_text(encoding='utf-8'))['parks']
        c = (d['K4-0001']['location'].get('coords') or [{}])[0]
        ok = ok and c.get('lat') == 37.501 and c.get('role') == 'park' and 'Census' in c.get('from', '') and d['K4-0001']['page']['read'] == '2026-11-22'
        ok = ok and not d['K4-0002']['location'].get('coords') and not d['K4-0003']['location'].get('coords') and calls == [3]
        ok = ok and canada_address('c/o Test Falls Provincial Park PO Box 252 4853 Highway 11/17 Testfalls, ON P0T 1W0') == '4853 Highway 11/17 Testfalls, ON P0T 1W0'
        ok = ok and canada_address('PO Box 99 Port Testy, ON N0E 1M0') is None
        ok = ok and len(d['K4-0005']['location'].get('coords') or []) == 1 and len(d['K4-0006']['location'].get('coords') or []) == 1   # shared, but right by both pins
        ok = ok and split_address('Reservations 800-555-0100 Address 122 Test Canyon Park Road Rising Fawn, GA 30738 Dade County GPS Coordinates') == ('122 Test Canyon Park Road', 'Rising Fawn', 'GA', '30738')
        c4 = (d['K4-0004']['location'].get('coords') or [{}])[0]
        ok = ok and c4.get('lat') == 45.401 and 'Canada' in c4.get('from', '') and ca_calls == ['4998 Concession Test Road 7 Testton, ON K1A 0B1']
        run(o, scripts, '2026-11-23', poster=fake, allow=lambda s: True, ca_manners=lambda s: FakeCA(), ca_lookup=fake_ca)  # nothing asked again
        d2 = json.loads((o / 'facts' / 'US-KY.json').read_text(encoding='utf-8'))['parks']
        ok = ok and calls == [3] and len(ca_calls) == 1 and len(d2['K4-0001']['location']['coords']) == 1
    print('selftest', 'ALL PASS' if ok else 'FAIL')
    return 0 if ok else 1


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='out'); ap.add_argument('--scripts', default='scripts'); ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    sys.exit(selftest() if a.selftest else run(a.out, a.scripts))
