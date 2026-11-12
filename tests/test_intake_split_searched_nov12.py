#!/usr/bin/env python3
"""Offline test, KPC owner 2026-11-12: (1) the intake bot reads split queue files data/intake/queue*.json but never a *hold* file;
(2) searched-park memory: a park whose outline was searched within 90 days is skipped unless a newer queue row exists for its
area; (3) official pin fills only fill a park with no usable pin. Plus the committed files: valid, no never-contact host in a
probe-able row, no WDPA text, every file under 1 MB. No network. Run: python3 -B tests/test_intake_split_searched_nov12.py"""
import datetime, json, os, pathlib, re, socket, sys, tempfile
R = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(R / '.github' / 'scripts'))
socket.socket.connect = lambda *a, **k: (_ for _ in ()).throw(OSError('no network in this test'))
ok = True
def check(c, m):
    global ok; print(('PASS ' if c else 'FAIL ') + m); ok = ok and bool(c)

tmp = pathlib.Path(tempfile.mkdtemp())
W = lambda n, rows: (tmp / n).write_text(json.dumps({'rows': rows}), encoding='utf-8')
W('queue.json', [{'url': 'https://a.gov/x/MapServer/1', 'area': 'US-KY', 'added': '2026-10-01'}])
W('queue-nov12.json', [{'url': 'https://b.gov/wfs', 'area': 'GB', 'added': '2026-11-12'}, {'url': 'https://a.gov/x/MapServer/1?f=json', 'area': 'US-KY'}])
W('queue-hold-nov12.json', [{'url': 'https://c.gov/never', 'area': 'SE', 'added': '2026-11-12'}])
os.environ['QUEUE'] = str(tmp / 'queue.json')
import kpc_intake_bot as IB
got = [r['url'] for r in IB.split_queue_rows(json.loads((tmp / 'queue.json').read_text())['rows'])]
check(got == ['https://b.gov/wfs'], f'split file read, hold file never, duplicate url skipped: {got}')

import kpc_searched as KS
(tmp / 'searched-parks.json').write_text(json.dumps({'parks': {
    'GB-0001': [{'date': '2026-11-11', 'result': 'nothing-found', 'search': 'outline', 'where': 't'}],
    'SE-0001': [{'date': '2026-11-11', 'result': 'nothing-found', 'search': 'outline', 'where': 't'}],
    'NO-0001': [{'date': '2026-06-01', 'result': 'nothing-found', 'search': 'outline', 'where': 't'}],
    'TH-0001': [{'date': '2026-11-11', 'result': 'nothing-found', 'search': 'pin', 'where': 't'}]}}), encoding='utf-8')
S = KS.Searched(file=tmp / 'searched-parks.json', folder=tmp, today=datetime.date(2026, 11, 20))
check(S.skip('SE-0001', 'SE') != '', 'searched 9 days ago, the only new row is in the hold file: skipped')
check(S.skip('GB-0001', 'GB') == '', 'a newer probe-able queue row for GB: searched again')
check(S.skip('NO-0001', 'NO') == '', 'searched over 90 days ago: searched again')
check(S.skip('TH-0001', 'TH') == '' and S.skip('TH-0001', 'TH', kind='pin') != '', 'a pin hunt never blocks an outline hunt')
check(S.skip('US-9999', 'US-KY') == '', 'never searched: searched')

import kpc_official_pins as OP
(tmp / 'official-pins-x.json').write_text(json.dumps({'rows': [
    {'ref': 'CA-1', 'action': 'pin-fill', 'lat': 50.1, 'lon': -60.2, 'pota_pin': None},
    {'ref': 'CA-2', 'action': 'pin-fill', 'lat': 50.1, 'lon': -60.2, 'pota_pin': [50.0, -60.0]},
    {'ref': 'CA-3', 'action': 'point-circle-candidate', 'lat': 50.1, 'lon': -60.2, 'pota_pin': [50.1, -60.2]},
    {'ref': 'CA-4', 'action': 'pin-fill', 'lat': 0, 'lon': 0, 'pota_pin': None}]}), encoding='utf-8')
check(sorted(OP.fills(tmp)) == ['CA-1'], 'only a pin-fill for a park with no POTA pin is used (never moves a pin, never a circle)')

D = R / 'data' / 'intake'
bad = re.compile(r'services\d*\.arcgis\.com|apps\.fs\.usda\.gov|33TOOklri9xpic7U|ncnhde\.natureserve\.org', re.I)
for f in sorted(D.glob('queue-*.json')) + sorted(D.glob('official-pins-*.json')) + [D / 'searched-parks.json']:
    t = f.read_text(encoding='utf-8'); d = json.loads(t)
    check(len(t.encode()) < 1048576, f'{f.name}: under 1 MB ({len(t.encode())} bytes)')
    check(not re.search(r'wdpa|protected ?planet|phone ?book', t, re.I), f'{f.name}: no WDPA text')
    if f.name.startswith('queue-') and 'hold' not in f.name:
        check(not [r for r in d['rows'] if bad.search(r.get('url') or '')], f'{f.name}: no never-contact host in a probe-able row')
real = KS.Searched(); fl = OP.fills()
check(len(real.parks) > 0 and all(isinstance(v, list) for v in real.parks.values()), f'searched-parks.json loads ({len(real.parks)} parks)')
check(all(r.startswith(('CA-', 'AU-', 'US-', 'PF-', 'SE-', 'SI-')) for r in fl), f'official pin fills load ({len(fl)})')
print('ALL PASS' if ok else 'SOME FAILED'); sys.exit(0 if ok else 1)
