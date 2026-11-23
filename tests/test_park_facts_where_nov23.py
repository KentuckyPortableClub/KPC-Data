#!/usr/bin/env python3
"""Park facts 7, 23 Nov 2026: carries what the reader now takes from a page (how far and which way from a town, the
counties, the converter's approximate points) and takes out a point that 3 or more parks' pages of ONE site share (a site
template, as on Illinois DNR where every park page carries the same park's point). A point from the park's own address
is never taken out here. Invented parks. Prints PASS / FAIL, ends ALL PASS or SOME FAILED."""
import importlib.util, json, pathlib, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('pf', ROOT / '.github/scripts/draft/tools/kpc_park_facts/kpc_park_facts.py')
PF = importlib.util.module_from_spec(spec); spec.loader.exec_module(PF)
ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


def park(ref, name, coords, host='dnr.invented.gov', **loc):
    return {'area': 'US-ZZ', 'pota': {'name': name, 'type': 'State Park', 'pin': [41.0, -88.0]}, 'asked': {'url': f'https://{host}/{ref}'},
            'page': {'read': '2026-11-23', 'kind': 'html', 'final_url': f'https://{host}/{ref}', 'host': host}, 'own_page': {'is': 'own'},
            'name': {'heading': name, 'vs_pota': 'same'}, 'location': dict({'coords': coords, 'addresses': [], 'directions': None}, **loc)}


T = {'lat': 42.466, 'lon': -87.810, 'from': 'page data (latitude / longitude)', 'role': 'unknown'}
OWN = {'lat': 41.2001, 'lon': -88.3001, 'from': 'pair on a line', 'role': 'park'}
ADR = {'lat': 42.466, 'lon': -87.810, 'from': 'address (US Census lookup)', 'role': 'park'}
with tempfile.TemporaryDirectory() as t:
    t = pathlib.Path(t)
    parks = {'US-9701': park('US-9701', 'Alpha State Park', [dict(T), dict(OWN)]), 'US-9702': park('US-9702', 'Bravo State Park', [dict(T)]),
             'US-9703': park('US-9703', 'Charlie State Park', [dict(T)]), 'US-9704': park('US-9704', 'Delta State Park', [dict(ADR)]),
             'US-9705': park('US-9705', 'Echo State Park', [dict(T)], host='other.invented.gov',
                             offsets=[{'km': 3.2, 'dir': 'E', 'of': 'Shiocton', 'quote': 'x'}], counties=['Outagamie'],
                             near=[{'lat': 44.45, 'lon': -88.5, 'within_km': 3.0, 'from': 'offset from town (Shiocton)'}])}
    (t / 'US-ZZ.json').write_text(json.dumps({'area': 'US-ZZ', 'parks': parks}), encoding='utf-8')
    pages, _areas = PF.read_pages(str(t))
    pts = lambda r: [(c['lat'], c['lon']) for c in pages[r]['coords']]
    check("a point on 3 parks' pages of one site is taken out of all three", pts('US-9702') == [] and pts('US-9703') == [] and (42.466, -87.810) not in pts('US-9701'))
    check("the park's own different point stays", pts('US-9701') == [(41.2001, -88.3001)])
    check("a point from the park's own address is not taken out here", pts('US-9704') == [(42.466, -87.810)])
    check('the same point on another site is not counted with them', pts('US-9705') == [(42.466, -87.810)])
    check('park facts carries the offset, the county and the approximate point', pages['US-9705'].get('offsets') == [{'km': 3.2, 'dir': 'E', 'of': 'Shiocton'}]
          and pages['US-9705'].get('counties') == ['Outagamie'] and (pages['US-9705'].get('near') or [{}])[0].get('within_km') == 3.0)
    check('the version is 7 or later', int(PF.VERSION.split()[1]) >= 7)
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
