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


def run(out, scripts, today=None, poster=post_batch, allow=robots_allow, ca_manners=_ca_manners, ca_lookup=canada_lookup):
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
    for f, d in files.items():
        tmp = f.with_name(f.name + '.tmp'); tmp.write_text(json.dumps(d, ensure_ascii=False), encoding='utf-8'); tmp.replace(f)
    matched = sum(1 for v in known.values() if v)
    print(f'Addresses turned into map points: {matched} of {len(known)} looked up ({len(want)} new this run, {asked} request(s)); '
          f'{added} map point(s) added to {parks} park(s).', flush=True)
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
