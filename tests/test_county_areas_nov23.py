#!/usr/bin/env python3
"""County areas, 23 Nov 2026 5:24 AM (owner: "I dont want key bots to do internet stuff"). The county a park's own page names is
given its middle point and size ON THE PC, by the converter, from the Census Gazetteer county files (the layout read live
that morning), and saved with the page facts; park facts carries it; the key only reads it. Each state's file is fetched
once; a county that is not on the list gives nothing; a failing list never stops the run. Invented parks and counties, no
network. Prints PASS / FAIL, ends ALL PASS or SOME FAILED."""
import importlib.util, json, pathlib, socket, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github/scripts/pc'))


def _no_net(*a, **k): raise RuntimeError('no network in tests')
socket.socket.connect = _no_net
import kpc_geocode_addresses as G  # noqa: E402
spec = importlib.util.spec_from_file_location('pf', ROOT / '.github/scripts/draft/tools/kpc_park_facts/kpc_park_facts.py')
PF = importlib.util.module_from_spec(spec); spec.loader.exec_module(PF)
ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


TXT = ('USPS\tGEOID\tANSICODE\tNAME\tALAND\tAWATER\tALAND_SQMI\tAWATER_SQMI\tINTPTLAT\tINTPTLONG          \n'
       'WI\t55001\t00000001\tOtter County\t1539631459\t25677536\t594.455\t9.914\t44.500000\t-88.50000          \n'
       'WI\t55003\t00000002\tSt. Heron Parish\t3141592653\t0\t1213.0\t0.\t46.000000\t-91.00000          \n')
t = G.parse_counties(TXT)
check('the county file is read by column name: the middle point and the radius of a circle of its size',
      t.get('otter') == [44.5, -88.5, 22.3] and abs(t.get('st heron')[2] - 31.6) < 0.2)


class FakeM:
    def robots_ok(self, u): return True


def park(area, counties, own='own'):
    return {'area': area, 'pota': {'name': 'Invented Marsh State Wildlife Area', 'type': 'State Wildlife Area', 'pin': [44.45, -88.55]}, 'own_page': {'is': own},
            'asked': {'url': 'https://dnr.invented.gov/x'}, 'page': {'kind': 'html', 'read': '2026-11-23', 'host': 'dnr.invented.gov'},
            'name': {'heading': 'Invented Marsh State Wildlife Area', 'vs_pota': 'same'},
            'location': {'coords': [], 'addresses': [], 'directions': None, 'counties': counties}}


with tempfile.TemporaryDirectory() as tmp:
    out = pathlib.Path(tmp) / 'out'; (out / 'facts').mkdir(parents=True)
    parks = {'US-9981': park('US-WI', ['Otter']), 'US-9982': park('US-WI', ['Nowhere']), 'US-9983': park('US-WI', ['Otter', 'Saint Heron']),
             'US-9984': park('US-WI', ['Otter'], own='list')}
    (out / 'facts' / 'US-WI.json').write_text(json.dumps({'area': 'US-WI', 'parks': parks}))
    calls = []
    def cty(files, o, scripts): return G.county_areas(files, o, scripts, manners=lambda s: FakeM(), us_counties=lambda M, st: (calls.append(st) or TXT))
    run = lambda **kw: G.run(str(out), str(ROOT / '.github/scripts'), today='2026-11-23', poster=None, allow=lambda s: False, ca_manners=None, towns=None, **kw)
    rc = run(counties=cty); rc2 = run(counties=cty)
    got = json.loads((out / 'facts' / 'US-WI.json').read_text())['parks']
    ca = lambda r: got[r]['location'].get('county_areas') or []
    check("the county the page names gets its middle point and size", rc == 0 and ca('US-9981') == [{'name': 'Otter', 'lat': 44.5, 'lon': -88.5, 'radius_km': 22.3}])
    check('a county that is not on the list: nothing', ca('US-9982') == [])
    check("two counties, one written 'Saint' where the list says 'St.': both", [c['name'] for c in ca('US-9983')] == ['Otter', 'Saint Heron'])
    check('a list page: nothing', ca('US-9984') == [])
    check("each state's county list is fetched once and kept", calls == ['WI'])
    def boom(files, o, scripts): raise RuntimeError('the county list is down')
    check('a failing county list never stops the run', run(counties=boom) == 0)
    pages, _ = PF.read_pages(str(out / 'facts'))
    check('park facts carries it for the key to read', (pages['US-9981'].get('county_areas') or [{}])[0].get('radius_km') == 22.3)
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
