#!/usr/bin/env python3
"""Nov 7 tracer gates (kpc_trace_limits.py): per-type ceilings, GeoPDF plausibility, clipped-map edge share, hold_reasons. Pure Python:
no shapely / cv2 / network. Plain script: prints PASS/FAIL lines, exit 1 on a failure.   python3 -B tests/test_trace_limits_nov7.py"""
import csv, importlib.util, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FX = os.path.join(HERE, 'fixtures', 'tracer_nov7')
sp = importlib.util.spec_from_file_location('kpc_trace_limits', os.path.join(ROOT, '.github', 'scripts', 'draft', 'kpc_trace_limits.py'))
TL = importlib.util.module_from_spec(sp); sp.loader.exec_module(TL)
bad = []


def check(cond, msg):
    if not cond: bad.append(msg); print('FAIL', msg)


lim = json.load(open(os.path.join(FX, 'limits-cases.json')))
for t, want in lim['ceiling_acres']:
    check(TL.ceiling_acres(t) == want, f'ceiling_acres({t!r}) = {TL.ceiling_acres(t)}, want {want}')
check(TL.ceiling_acres('International Park') < 1e6, '"International Park" must not match the national tier (word boundary)')
for c in lim['geopdf_checks']:
    ok, why = TL.geopdf_checks(c['fit_err_m'], c['m_per_px'], c['page_km2'], c['pin_off_km'])
    check(ok == c['expect'], f'geopdf_checks {c}: got {ok} {why}')
    if not c['expect']: check(why and why[0].startswith(c['first']), f'geopdf_checks first reason {c["first"]!r}: {why}')

# affine route: a clean 1.2 km page, the pin on it, then 55 km away, then a malformed matrix
lat = 40.0; kx = 111320 * math.cos(math.radians(lat)); ky = 110540
a = [1200 / kx, 0, -100 - 0.5 * 1200 / kx, 0, -960 / ky, lat + 0.5 * 960 / ky]
ok, why, info = TL.geopdf_plausible(a, 1000, 800, 0.3, (40.0, -100.0))
check(ok and abs(info['m_per_px_x'] - 1.2) < 0.01 and info['pin_on_page'], f'clean affine: {ok} {why} {info}')
ok, why, info = TL.geopdf_plausible(a, 1000, 800, 0.3, (40.5, -100.0))
check(not ok and why[0].startswith('pin off page') and info['pin_off_km'] > 50, f'far pin: {why} {info}')
for bad_a in ([1, 0, 0], [0, 0, 0, 0, 0, 0], ['x'] * 6, [float('nan')] * 6):
    ok, why, _ = TL.geopdf_plausible(bad_a, 1000, 800, 0.3, (40, -100))
    check(not ok and 'malformed' in why[0], f'malformed affine {bad_a}: {why}')

# edge share: inside = 0, one side on the frame = 0.25, a tiny nick = under the 3% flag line
sq_in = [(100, 100), (400, 100), (400, 400), (100, 400)]
sq_side = [(0, 100), (300, 100), (300, 400), (0, 400)]
check(TL.edge_share(sq_in, 1000, 800) == 0.0, 'a shape well inside the frame has edge share 0')
check(abs(TL.edge_share(sq_side, 1000, 800) - 0.25) < 0.03, f'one side on the frame is about 0.25, got {TL.edge_share(sq_side, 1000, 800):.3f}')
nick = [(2, 400), (900, 100), (900, 700), (300, 700)]
check(TL.edge_share(nick, 1000, 800) < TL.EDGE_SHARE_FLAG, f'a corner nick stays under the flag line, got {TL.edge_share(nick, 1000, 800):.3f}')

# the recorded Nov 2 rows
for r in json.load(open(os.path.join(FX, 'expected-outcomes.json')))['rows']:
    if r['expect'] in ('undetermined', 'no_fit'): continue   # no_fit: nothing is drawn, so there are no gates to run (checked below)
    gok, gwhy = TL.geopdf_checks(r['fit_err_m'], (1.0, 1.0), None, 0.0)
    got = TL.hold_reasons(geopdf_why=gwhy, pin_dist_m=r['pin_dist_m'], traced_acres=r['traced_acres'], known_acres=r['known_acres'],
                          park_type=r['type'], geopdf_residual_ok=gok)
    check((('hold' if got else 'ok') == r['expect']), f'{r["ref"]} ({r.get("note", "")}): want {r["expect"]}, got {got}')
    for want in r.get('reasons', []):
        check(any(want in g for g in got), f'{r["ref"]}: expected a reason containing {want!r}, got {got}')

# the 33-row acres table: with the tracts switch ON the seven passers stay and exactly two are held
rows = list(csv.DictReader(open(os.path.join(FX, 'drawn-vs-known-acres.csv'))))
held = sorted(r['ref'] for r in rows if r['tracer'] == 'picture' and r['tract_side_files_acres']
              and TL.size_verdict(r['traced_acres'], r['tract_side_files_acres'], None)[0] == 'hold')
check(held == ['US-5265', 'US-7519'], f'with tracts on only US-5265 and US-7519 are held by the 0.2x gate: {held}')
# with NO known acres, the default 60,000 ac ceiling alone holds exactly the four giants
pic = [r for r in rows if r['tracer'] == 'picture']
big = sorted(r['ref'] for r in pic if TL.size_verdict(r['traced_acres'], None, None)[0] == 'hold')
check(big == ['US-11145', 'US-5460', 'US-5815', 'US-6048'], f'default ceiling holds the four giants: {big}')
check(len(pic) == 25, f'25 picture DRAWN rows in the table, got {len(pic)}')

# Nov 7 evening (Quality item C): the #31/#32 outcomes are in the fixture, not only in the PR text
_ex = {r['ref']: r for r in json.load(open(os.path.join(FX, 'expected-outcomes.json')))['rows'] if r['ref'] in ('CA-1248', 'US-10787')}
check(_ex['CA-1248']['traced_acres'] == 28.9 and _ex['CA-1248']['expect'] == 'ok' and _ex['CA-1248'].get('outcome') == 'DRAWN',
      f"CA-1248 fixture: DRAWN 28.9 ac, ok: {_ex['CA-1248']}")
_g = TL.geopdf_checks(0.3, (1.0, 1.0), None, 0.0)
check(TL.hold_reasons(geopdf_why=_g[1], pin_dist_m=0, traced_acres=28.9, known_acres=None, park_type='Nature Reserve', geopdf_residual_ok=_g[0]) == [],
      'CA-1248 at 28.9 ac (Nature Reserve, pin inside) passes every gate')
check(_ex['US-10787']['expect'] == 'no_fit' and _ex['US-10787'].get('outcome') == 'NO FIT'
      and any('water source skipped' in x for x in _ex['US-10787'].get('reasons', [])), f"US-10787 fixture: NO FIT, water skipped: {_ex['US-10787']}")

# order and wording of reasons
got = TL.hold_reasons(geopdf_why=['geopdf residual: 352 m is over 100 m'], pin_dist_m=5000, edge=0.4, traced_acres=1e6, park_type='State Park')
check(len(got) == 4, f'four reasons expected: {got}')
check(got[0].startswith('geopdf residual') and got[1].startswith('pin outside') and got[2].startswith('clipped'), f'reason order: {got}')
check(TL.hold_reasons(edge=0.01, traced_acres=100, park_type='State Park') == [], 'an edge share under 3% is a flag, not a hold')
check(TL.hold_reasons(kind='trail', length_km=900) != [] and TL.hold_reasons(kind='trail', length_km=20) == [], 'trail length ceiling')
# known acres still decide first when present
check(TL.size_verdict(134.9, 229.85, 'State Park')[0] == 'ok' and TL.size_verdict(25895525.4, 5000, 'State Forest')[0] == 'hold', 'Nov 6 behaviour kept')
check(TL.size_verdict(None, None, None)[0] == 'ok', 'no traced area = no size verdict')

# parcel tracer: seed alone over the cap; no known size = ceiling; known size leaves the existing 0.2x-2x check alone
check(TL.parcel_new_holds(80000, None, 'Recreation Park') != [], 'parcel 80,000 ac, no known size, 60,000 ceiling: held')
check(TL.parcel_new_holds(19199.45, None, 'Recreation Park') == [], 'parcel 19,199 ac under the 60,000 ceiling: no NEW hold (CA-5926 is not asserted wrong)')
check(TL.parcel_new_holds(437.67, None, 'Regional Park') == [], 'CA-4952 sized parcel passes')
check(TL.parcel_new_holds(4500, 4000, 'State Park', seed_acres=6000, grow_cap=1.25) != [], 'seed 6,000 ac vs known 4,000 (cap 5,000): held')
check(TL.parcel_new_holds(4500, 4000, 'State Park', seed_acres=4900, grow_cap=1.25) == [], 'seed under the cap: nothing new')
check(TL.parcel_new_holds(900000, 4000, 'State Park', seed_acres=100, grow_cap=1.25) == [], 'known size present: the existing 0.2x-2x check decides, not the ceiling')
check(TL.parcel_new_holds(10, None, None, grow_cap=0) == [], 'no ceiling trip, no cap')

# split-unit maps: a gap wider than the 50 m adjacency is bridged only on an official size, never silently
C = [(1, 400.0, 120.0), (2, 2500.0, 80.0)]
add, txt = TL.stitch_extra(100.0, C, None)
check(add == [] and 'not joined' in txt and '400-2500 m' in txt, f'no official size: nothing is joined and both are listed, got {add} {txt!r}')
add, txt = TL.stitch_extra(100.0, C, 300.0)
check(add == [1] and '220 ac of 300 ac' in txt and 'not joined' in txt, f'with a size: the nearest piece joins, the far one is listed, got {add} {txt!r}')
check(TL.stitch_extra(100.0, C, 1000.0)[0] == [], 'pieces that still do not make the official size are not joined')
check(TL.stitch_extra(280.0, C, 300.0)[0] == [], 'a pin piece already the size of the park gains nothing')
check(TL.stitch_extra(100.0, [(1, 400.0, 900.0)], 300.0)[0] == [], 'a piece that would overshoot 1.25x is not joined')
check(TL.stitch_extra(100.0, [], None) == ([], ''), 'one shape only: nothing to say')
check(TL.stitch_extra(100.0, C, 'x')[0] == [], 'a bad known size is treated as no size')

# Brandon's Nov 7 calls: Trailhead beats BLM; within 5% of a ceiling = a person looks
check(TL.ceiling_acres('Notch Peak Trailhead BLM Recreation Management Area') == 5000, 'Trailhead must beat BLM (US-6048)')
check(TL.ceiling_acres('Grand Staircase-Escalante National Monument') == 20000000, 'a National Monument is not a point feature')
for c in lim['near_ceiling']:
    st, why = TL.size_verdict(c['traced'], None, c['type'])
    check(st == c['expect'] and (not c.get('within') or 'within 5%' in why), f'near-ceiling {c}: got {st} {why!r}')
check(TL.parcel_new_holds(57500, None, 'Recreation Park') != [] and TL.parcel_new_holds(50000, None, 'Recreation Park') == [],
      'the parcel tracer applies the same 5% band (60,000 ceiling)')
check(TL.size_verdict(93853, None, 'Notch Peak Trailhead BLM Recreation Management Area')[0] == 'hold',
      'US-6048 at 93,853 ac is now over its 5,000 ac trailhead ceiling: held by size, not only by the edge rule')

print('FAIL' if bad else 'ALL PASS', f'({len(bad)} problems)' if bad else '')
sys.exit(1 if bad else 0)
