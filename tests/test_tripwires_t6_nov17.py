#!/usr/bin/env python3
"""Tripwire T6, same land through different records (KPC owner, 2026-11-17; Handoff 8 Part 3). Offline, on a made-up KPC-Links in a
temp folder (key, pins and saved outlines; the outline reader is the real KPC-Links kpc_master, found by tests/_links_checkout.py):
  1. a pair of parks whose outlines are 95% the same land (over the smaller) and share no record id is listed
  2. a pair at 60% is NOT listed; 89% is not, 91% is (the line is 90%)
  3. a pair on the very same land that shares a record id is NOT listed (that is T1's), also when the id is shared only through a
     key m row and not the saved outline
  4. a small park inside a big one is listed as 'inside'; two parks on one ground as 'twin'; a park in the big park's HOLE is not
     listed (holes are holes); one outline drawn as two records over each other counts its land once (the share never goes over 1)
  5. busiest first by POTA activations (KPC-Data data/parkinfo field 7; a park with no count = 0); the count per area is reported
  6. the not-sure list (D10) gets T6 on both parks of a listed pair; a person's clear (with 'by') takes that park off, the other stays
  7. the scan-line areas agree with plain geometry: two equal squares shifted a known share come back at that share (to 0.5%)
  8. still a report: standard library only (shapely / pyproj / numpy blocked), no network, no web address in any output
Prints PASS / FAIL lines, ends ALL PASS / SOME FAILED."""
import gzip, json, math, os, pathlib, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
S = ROOT / '.github/scripts'
sys.path.insert(0, str(S)); sys.path.insert(0, str(ROOT / 'tests'))
import _links_checkout  # noqa: E402
LINKS = pathlib.Path(_links_checkout.use(ROOT))
import kpc_tripwires as T  # noqa: E402
ok = True


def check(msg, c):
    global ok
    ok &= bool(c)
    print(('PASS ' if c else 'FAIL ') + msg, flush=True)


LAT0, LON0 = 38.0, -92.0
KM_LAT = 1 / 110.574
KM_LON = 1 / (111.320 * math.cos(math.radians(LAT0)))


def ring(cx, cy, half):
    return [[LON0 + (cx + dx * half) * KM_LON, LAT0 + (cy + dy * half) * KM_LAT] for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1), (-1, -1))]


def sq(cx, cy, half, hole=0.0):
    return [ring(cx, cy, half)] + ([ring(cx, cy, hole)[::-1]] if hole else [])


def mp(*polys): return {'type': 'MultiPolygon', 'coordinates': list(polys)}


# (ref, geometry, outline record ids, extra key m ids). Squares are 2 km on a side (half 1 km) unless said; a shift of d km of
# one of two equal squares leaves (2 - d) / 2 of the land in common.
PARKS = [
    ('US-9101', mp(sq(0, 0, 1)), ['sgzza1'], []),             # 1. 95%: shifted 0.1 km
    ('US-9102', mp(sq(0.1, 0, 1)), ['sgzzb1'], []),
    ('US-9103', mp(sq(10, 0, 1)), ['sgzza2'], []),            # 2. 60%: shifted 0.8 km
    ('US-9104', mp(sq(10.8, 0, 1)), ['sgzzb2'], []),
    ('US-9105', mp(sq(20, 0, 1)), ['sgzza3'], []),            # 2. 89%: shifted 0.22 km
    ('US-9106', mp(sq(20.22, 0, 1)), ['sgzzb3'], []),
    ('US-9107', mp(sq(30, 0, 1)), ['sgzza4'], []),            # 2. 91%: shifted 0.18 km
    ('US-9108', mp(sq(30.18, 0, 1)), ['sgzzb4'], []),
    ('US-9109', mp(sq(40, 0, 1)), ['sgzza5', '777'], []),     # 3. same land, record 777 shared (T1's)
    ('US-9110', mp(sq(40, 0, 1)), ['sgzzb5', '777'], []),
    ('US-9111', mp(sq(50, 0, 1)), ['sgzza6'], ['sgzzb6']),    # 3. same land, shared only through the key m row
    ('US-9112', mp(sq(50, 0, 1)), ['sgzzb6'], []),
    ('US-9113', mp(sq(60, 0, 3, hole=1.5)), ['sgzza7'], []),  # 4. big park with a hole ...
    ('US-9114', mp(sq(62, 0, 0.4)), ['sgzzb7'], []),          # ... a small park inside its land: 'inside'
    ('US-9115', mp(sq(60, 0, 0.5)), ['sgzzc7'], []),          # ... a small park in its HOLE: not listed
    ('US-9116', mp(sq(70, 0, 1), sq(70, 0, 1)), ['sgzza8', 'sgzzd8'], []),   # 4. one outline, two records drawn over each other
    ('US-9117', mp(sq(70, 0, 1)), ['sgzzb8'], []),            # ... and a twin of it
]
ACT = {'US-9101': 10, 'US-9102': 5, 'US-9113': 300, 'US-9116': 40}   # US-9114, 9117, 9107, 9108: no count (0)


def build(t):
    L = pathlib.Path(t) / 'links'
    for d in ('data/us-key', 'data/outlines', '.github'):
        (L / d).mkdir(parents=True, exist_ok=True)
    (L / '.github/scripts').symlink_to(LINKS / '.github/scripts')
    (L / 'locations.json').write_text(json.dumps([['POTA', r, r, LAT0, LON0, 'https://example.org/park/' + r] for r, *_ in PARKS]))
    us = {r: {'n': r, 'g': 'official', 'm': [[i, r + ' land', 100, 'name'] for i in ids + extra]} for r, _g, ids, extra in PARKS}
    (L / 'data/us-key/US-ZZ.json').write_text(json.dumps({'parks': us}))
    feats = [{'type': 'Feature', 'geometry': g, 'properties': {'ref': r, 'name': r + ' Park', 'g': 'official', 'layers': sorted({T.layer_of(i) for i in ids}),
              'layer_url': 'https://gis.example.gov/arcgis/rest/services/Secret/MapServer/3', 'record_ids': ids}} for r, g, ids, _e in PARKS]
    with gzip.GzipFile(L / 'data/outlines/US-ZZ.geojson.gz', 'wb', mtime=0) as g:
        g.write(json.dumps({'type': 'FeatureCollection', 'kpc': {}, 'features': feats}).encode())
    K = pathlib.Path(t) / 'kpcdata'
    (K / 'data/parkinfo').mkdir(parents=True)
    (K / 'data/parkinfo/US-ZZ.json').write_text(json.dumps({'parks': {r: ['n', '', 'SP', '', '', LAT0, LON0, ACT.get(r), None, None] for r, *_ in PARKS}}))
    return L, K


def run(args, env=None):
    return subprocess.run([sys.executable, str(S / 'kpc_tripwires.py'), 'run'] + args, capture_output=True, text=True, timeout=300, env=env)


with tempfile.TemporaryDirectory() as t:
    t = pathlib.Path(t)
    L, K = build(t)
    out, ns, cl = t / 'tw', K / 'data/waiting/tripwires/not-sure.json', K / 'data/waiting/tripwires/cleared.json'
    p = run(['--links', str(L), '--out', str(out), '--keys', 'us', '--not-sure', str(ns), '--cleared', str(cl), '--parkinfo', str(K / 'data/parkinfo'), '--date', '2026-11-17'])
    check(f'the run exits 0 ({p.returncode}: {p.stderr[-300:]})', p.returncode == 0)
    rep = json.load(open(out / 'counts/latest.json'))
    rows = [i for f in sorted((out / 'waiting/T6').glob('*.json')) for i in json.load(open(f))['items']]
    pairs = {tuple(r['parks']): r for r in rows}
    check(f"1. the 95% pair (US-9101 / US-9102) is listed at ~0.95 ({pairs.get(('US-9101', 'US-9102'), {}).get('same_land_share')})",
          abs(pairs.get(('US-9101', 'US-9102'), {}).get('same_land_share', 0) - 0.95) < 0.005)
    check('2. the 60% pair (US-9103 / US-9104) is NOT listed', ('US-9103', 'US-9104') not in pairs)
    check('2. the line is 90%: 89% (US-9105 / US-9106) not listed, 91% (US-9107 / US-9108) listed',
          ('US-9105', 'US-9106') not in pairs and ('US-9107', 'US-9108') in pairs)
    check('3. same land sharing record 777 (US-9109 / US-9110) is NOT listed: that is T1\'s', ('US-9109', 'US-9110') not in pairs)
    check('3. same land sharing a record only through the key m row (US-9111 / US-9112) is NOT listed', ('US-9111', 'US-9112') not in pairs)
    ins = pairs.get(('US-9113', 'US-9114'), {})
    check(f"4. a small park inside a big one is listed as 'inside' ({ins.get('kind')}, {ins.get('same_land_share')}, of larger {ins.get('share_of_larger')})",
          ins.get('kind') == 'inside' and ins.get('same_land_share', 0) > 0.99 and ins.get('share_of_larger', 1) < 0.1)
    check('4. a small park in the big park\'s HOLE (US-9115) is not listed', not any('US-9115' in k for k in pairs))
    tw = pairs.get(('US-9116', 'US-9117'), {})
    check(f"4. one outline drawn as two records over each other counts once: twin at 1.0 ({tw.get('kind')}, {tw.get('same_land_share')}, {tw.get('acres')})",
          tw.get('kind') == 'twin' and 0.995 <= tw.get('same_land_share', 0) <= 1.0 and tw.get('acres', [0, 1])[0] == tw.get('acres', [1, 0])[1])
    check(f"exactly the four pairs listed ({sorted(pairs)})", sorted(pairs) == [('US-9101', 'US-9102'), ('US-9107', 'US-9108'), ('US-9113', 'US-9114'), ('US-9116', 'US-9117')])
    order = [tuple(r['parks']) for r in rep.get('t6_busiest') or []]
    check(f'5. busiest first by activations: 300, 40, 15, then 0 ({order})',
          order == [('US-9113', 'US-9114'), ('US-9116', 'US-9117'), ('US-9101', 'US-9102'), ('US-9107', 'US-9108')]
          and pairs[('US-9113', 'US-9114')]['activations'] == [300, 0])
    check(f"5. counted per area and in the totals (US-ZZ T6 {rep['areas'].get('US-ZZ', {}).get('T6')}, totals {rep['totals']['us'].get('T6')}, parks {rep['totals']['us'].get('T6_parks')})",
          rep['areas']['US-ZZ'].get('T6') == 4 and rep['totals']['us']['T6'] == 4 and rep['totals']['us']['T6_parks'] == 8
          and rep['totals']['us']['T6_kinds'] == {'twin': 3, 'inside': 1} and 'US-ZZ 4' in p.stdout)
    d = json.load(open(ns))
    t6 = sorted(r for r, v in d['parks'].items() if 'T6' in v)
    check(f'6. the not-sure list carries T6 on both parks of every listed pair ({t6})',
          t6 == ['US-9101', 'US-9102', 'US-9107', 'US-9108', 'US-9113', 'US-9114', 'US-9116', 'US-9117'] and 'T6' in d['reasons'])
    cl.write_text(json.dumps({'parks': {'US-9101': {'by': 'KPC owner', 'date': '2026-11-18', 'why': 'two park numbers, same land'}}}))
    run(['--links', str(L), '--out', str(out), '--keys', 'us', '--not-sure', str(ns), '--cleared', str(cl), '--parkinfo', str(K / 'data/parkinfo'), '--date', '2026-11-18'])
    d2 = json.load(open(ns))
    check('6. a person\'s clear takes US-9101 off the not-sure list; its pair US-9102 stays', 'US-9101' not in d2['parks'] and d2['parks'].get('US-9102') == ['T6'])
    h = (out / 'counts/history.csv').read_text().splitlines()
    check(f'5. history.csv carries a T6 column ({h[0]}; {h[-1]})', h[0].endswith(',T6') and h[-1].endswith(',4'))
    # 7. the scan-line areas against plain geometry (equal squares, known shift)
    f = T._plane(LAT0, LON0)
    for d_km, want in ((0.1, 0.95), (0.5, 0.75), (1.0, 0.5)):
        a = T._outline_rings({'geometry': mp(sq(0, 0, 1))}, f); b = T._outline_rings({'geometry': mp(sq(d_km, 0.0, 1))}, f)
        ov, ma, mb = T.same_land(a, b)
        check(f'7. squares shifted {d_km} km: share {ov / min(ma, mb):.4f} (want {want}), area {ma / 1e6:.3f} km2 (want 4)', abs(ov / min(ma, mb) - want) < 0.005 and abs(ma / 1e6 - 4) < 0.02)
    # 8. standard library only, offline, no address
    blocker = t / 'noextra'
    for mod in ('shapely', 'pyproj', 'numpy'):
        (blocker / mod).mkdir(parents=True); (blocker / mod / '__init__.py').write_text(f'raise ImportError("{mod} blocked by the test")\n')
    pb = run(['--links', str(L), '--dry-run', '--keys', 'us', '--parkinfo', str(K / 'data/parkinfo')], env=dict(os.environ, PYTHONPATH=str(blocker)))
    tb = (json.loads(pb.stdout[pb.stdout.index('{'):pb.stdout.rindex('}') + 1]).get('totals') or {}).get('us', {}) if '{' in pb.stdout else {}
    check(f"8. standard library only: with shapely, pyproj and numpy blocked T6 still 4 ({pb.returncode}, {tb.get('T6')})", pb.returncode == 0 and tb.get('T6') == 4)
    alltxt = p.stdout + p.stderr + ''.join(x.read_text() for x in out.rglob('*') if x.is_file()) + ns.read_text()
    check('8. no web / file address in any output or the log', '://' not in alltxt and 'gis.example.gov' not in alltxt)
    check('8. still a report: binds false, report_only true, the 90% line listed as on trial', rep['binds'] is False and rep['report_only'] is True and rep['on_trial']['T6_same_land_share'] == 0.9)
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
