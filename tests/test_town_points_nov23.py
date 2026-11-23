#!/usr/bin/env python3
"""Town points, 23 Nov 2026 (owner 4:11 AM: "How many 2 miles east of is they ... do all 3"). A page that says '2 miles east of
Otterville' is turned into an APPROXIMATE point: the town's own point from the government town list (US: Census Gazetteer
place files, the layout read live that morning, tabs in 2024 and bars in 2026; Canada: Natural Resources Canada place names),
moved the stated distance in the stated direction. It goes in location.near with how far off it may be, never in
location.coords. The nearest town of that name to POTA's pin is used; a lake of the same name is not a town; a made point
too far from the pin is left out; a failing town list never holds up the address points. Invented parks and towns, no
network. Prints PASS / FAIL, ends ALL PASS or SOME FAILED."""
import json, pathlib, socket, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github/scripts/pc'))


def _no_net(*a, **k): raise RuntimeError('no network in tests')
socket.socket.connect = _no_net
import kpc_geocode_addresses as G  # noqa: E402

ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


T24 = ('USPS\tGEOID\tANSICODE\tNAME\tLSAD\tFUNCSTAT\tALAND\tAWATER\tALAND_SQMI\tAWATER_SQMI\tINTPTLAT\tINTPTLONG          \n'
       'WI\t5500001\t00000001\tOtterville village\t47\tA\t4052951\t272944\t1.565\t0.105\t44.445041\t-88.57645          \n'
       'WI\t5500002\t00000002\tOtterville town\t43\tA\t4052951\t0\t1.5\t0.\t46.900000\t-91.50000          \n'
       'WI\t5500003\t00000003\tSt. Heron city\t25\tA\t4052951\t0\t1.5\t0.\t44.000000\t-89.00000          \n')
T26 = ('USPS|GEOID|GEOIDFQ|ANSICODE|NAME|LSAD|FUNCSTAT|ALAND|AWATER|ALAND_SQMI|AWATER_SQMI|INTPTLAT|INTPTLONG\n'
       'WI|5500001|1600000US5500001|00000001|Otterville village|47|A|4052950|272945|1.565|0.105|44.445041|-88.57645\n')
check('the 2024 layout (tabs) is read by column name', G.parse_places(T24).get('otterville') == [(44.445041, -88.57645), (46.9, -91.5)])
check('the 2026 layout (bars, one more column) is read too', G.parse_places(T26).get('otterville') == [(44.445041, -88.57645)])
check("'St. Heron city' is found as 'Saint Heron'", G.norm_town('Saint Heron') in G.parse_places(T24))
la, lo = G.offset_point(44.445041, -88.57645, 3.2, 'E')
check('3.2 km east: the same latitude, about 3.2 km of longitude further east', abs(la - 44.44504) < 1e-4 and 3.1 < G._km((44.445041, -88.57645), (la, lo)) < 3.3 and lo > -88.57645)


class FakeM:
    def robots_ok(self, u): return True


def park(area, pin, offsets, own='own', coords=()):
    return {'area': area, 'pota': {'name': 'Invented Marsh State Wildlife Area', 'pin': list(pin)}, 'own_page': {'is': own},
            'page': {'kind': 'html', 'read': '2026-11-23'}, 'location': {'coords': list(coords), 'addresses': [], 'offsets': offsets}}


def run(parks, us=lambda M, st: T24, ca=lambda M, town: [], boom=False):
    with tempfile.TemporaryDirectory() as t:
        out = pathlib.Path(t) / 'out'; (out / 'facts').mkdir(parents=True)
        by = {}
        for ref, p in parks.items(): by.setdefault(p['area'], {})[ref] = p
        for area, ps in by.items(): (out / 'facts' / f'{area}.json').write_text(json.dumps({'area': area, 'parks': ps}))
        calls = []
        def us_(M, st): calls.append(st); return us(M, st)
        def towns(files, o, scripts):
            if boom: raise RuntimeError('the town list is down')
            return G.town_points(files, o, scripts, manners=lambda s: FakeM(), us_places=us_, ca_places=ca)
        rc = G.run(str(out), str(ROOT / '.github/scripts'), today='2026-11-23', poster=None, allow=lambda s: False, ca_manners=None, towns=towns)
        got = {}
        for f in (out / 'facts').glob('*.json'): got.update(json.loads(f.read_text())['parks'])
        # a second run must use the saved state file, not ask again
        G.run(str(out), str(ROOT / '.github/scripts'), today='2026-11-23', poster=None, allow=lambda s: False, ca_manners=None, towns=towns)
        return rc, got, calls


OFF = [{'km': 3.2, 'dir': 'E', 'of': 'Otterville', 'quote': 'Find it 2 miles east of Otterville on Highway 54.'}]
rc, got, calls = run({'US-9911': park('US-WI', (44.45, -88.55), OFF, coords=[{'lat': 44.5, 'lon': -88.5, 'role': 'park'}]),
                      'US-9912': park('US-WI', (44.45, -88.55), [{'km': 3.2, 'dir': 'E', 'of': 'Nowhereville'}]),
                      'US-9913': park('US-WI', (44.45, -88.55), [{'km': 120.0, 'dir': 'N', 'of': 'Otterville'}]),
                      'US-9914': park('US-WI', (44.45, -88.55), OFF, own='list'),
                      'US-9915': park('US-WI', (46.95, -91.45), OFF)})
n = (got['US-9911']['location'].get('near') or [{}])[0]
check("'2 miles east of Otterville' becomes one approximate point east of the town, with how far off it may be",
      rc == 0 and abs(n.get('lat', 0) - 44.44504) < 1e-3 and -88.54 < n.get('lon', 0) < -88.53 and n.get('within_km') == 3.0 and 'Otterville' in n.get('from', ''))
check("it never goes among the page's own points", got['US-9911']['location']['coords'] == [{'lat': 44.5, 'lon': -88.5, 'role': 'park'}])
check('a town that is not on the list: no point', not got['US-9912']['location'].get('near'))
check("a made point too far from POTA's pin (the wrong town, or a slip): left out", not got['US-9913']['location'].get('near'))
check('a list page (not the park\'s own page or row): nothing made', not got['US-9914']['location'].get('near'))
n5 = (got['US-9915']['location'].get('near') or [{}])[0]
check("two towns of the same name: the one nearest POTA's pin is used", abs(n5.get('lat', 0) - 46.9) < 0.01)
check("each state's town list is fetched once and kept", calls == ['WI'])

CA = lambda M, town: G.ca_places_live(type('M', (), {'get': lambda self, u: (200, {}, json.dumps([
    {'key': 'geonames', 'name': 'Heronford', 'province': 'Manitoba', 'category': 'Lake', 'lat': 51.28, 'lng': -99.78},
    {'key': 'geonames', 'name': 'Heronford', 'province': 'Manitoba', 'category': 'City', 'lat': 51.149444, 'lng': -100.04944},
    {'key': 'geonames', 'name': 'Bibliotheque Heronford', 'province': 'Quebec', 'category': '', 'lat': 46.1, 'lng': -73.3}]).encode(), u)})(), town)
rc, got, _ = run({'CA-9921': park('CA', (51.4, -100.0), [{'km': 24.0, 'dir': 'N', 'of': 'Heronford'}])}, ca=CA)
n = (got['CA-9921']['location'].get('near') or [{}])[0]
check('Canada: the city is used, the lake and the library of the same name are not',
      abs(n.get('lat', 0) - (51.149444 + 24 / 110.574)) < 0.01 and abs(n.get('lon', 0) + 100.04944) < 0.01 and n.get('within_km') == 12.0)
old_read = park('US-WI', (44.45, -88.55), [])
del old_read['location']['offsets']
old_read['location']['directions'] = {'roads': ['Highway 54'], 'towns': [], 'sent': 'Find it 2 miles east of Otterville on Highway 54.'}   # one string, as the reader saves it
rc, got, _ = run({'US-9941': old_read})
check('a page read before offsets were kept: its saved directions sentence gives the point (no page read again)',
      [(o['dir'], o['of']) for o in got['US-9941']['location'].get('offsets') or []] == [('E', 'Otterville')] and len(got['US-9941']['location'].get('near') or []) == 1)
rc, got, _ = run({'US-9931': park('US-WI', (44.45, -88.55), OFF)}, boom=True)
check('a failing town list never stops the run: the facts are still written, no point made', rc == 0 and 'US-9931' in got and not got['US-9931']['location'].get('near'))
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
