#!/usr/bin/env python3
"""Tripwires T1-T5 (KPC owner, 2026-11-17; owner rulings D1-D11; T6 has its own test, test_tripwires_t6_nov17.py). Offline, on a made-up KPC-Links in a temp folder (keys, pins and
saved outlines; the outline reader is the real KPC-Links kpc_master, found by tests/_links_checkout.py):
  1. T1 one record one park: the same record in two parks of one key file is a row; a record every join of which is a person's
     is marked all_person (and puts no park on the not-sure list); world records are told apart by source (equal numbers of two
     layers are not one record), and the 17 Nov census way (plain id) is kept beside it
  2. T2 every piece connects: pieces 0 / 20 / 40 km chain (no cut); 0 / 40 km is cut by a gap over 25 km; a pin in a HOLE is not
     inside (its distance is to the outer ring)
  3. T4 pin at the edge or a person: 50 m outside a small park passes (100 m slack), 300 m outside fails, a 'reviewed' row clears
     it, a big park gets a tenth of its radius as slack
  4. T5 size form: a name-only record of another layer over 3x the pin-holding record and drawn in the saved outline is a row; the
     same layer, a record not drawn, a person's row or a pin not inside are not
  5. T3 is the key build's: no file = 'from the key build (not counted here)'; a key build's tripwire-t3.json count is carried
  6. reports only, binds nothing, never red: a run with every tripwire flagged exits 0, binds false, every input file is
     byte-identical after the run, no web / file address in any output or in the log, a network call is refused; exit 1 only when
     the inputs cannot be read (no locations.json, no key file); one unreadable key file is a warning (exit 0)
  7. the meter: a second run shows the jump and the new pattern; history.csv keeps one line per key per day
  8. D10 not-sure list: refs + reasons (T1 / T2 / T4), a person's clear (with 'by') takes a park off, a clear with no 'by' does not
  9. the workflow: by hand only (no cron line, not even a commented one), writes branch tripwires + data/waiting/tripwires/not-sure.json
     only, never KPC-Links, no new live cron against main
Prints PASS / FAIL lines, ends ALL PASS / SOME FAILED."""
import gzip, hashlib, json, math, os, pathlib, re, socket, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
S = ROOT / '.github/scripts'
sys.path.insert(0, str(S)); sys.path.insert(0, str(ROOT / 'tests'))
import _links_checkout  # noqa: E402
LINKS = pathlib.Path(_links_checkout.use(ROOT))
ok = True


def check(msg, c):
    global ok
    ok &= bool(c)
    print(('PASS ' if c else 'FAIL ') + msg, flush=True)


import kpc_tripwires as T  # noqa: E402

LAT0, LON0 = 37.0, -85.0
KM_LAT = 1 / 110.574
KM_LON = 1 / (111.320 * math.cos(math.radians(LAT0)))


def sq(cx, cy, half_km, hole_km=0.0):
    """A square (lon, lat) centred cx, cy km east / north of (LAT0, LON0), half_km half side; optional square hole in the middle."""
    def ring(h):
        return [[LON0 + (cx + dx * h) * KM_LON, LAT0 + (cy + dy * h) * KM_LAT] for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1), (-1, -1))]
    rings = [ring(half_km)] + ([ring(hole_km)[::-1]] if hole_km else [])
    return rings


def mp(*polys): return {'type': 'MultiPolygon', 'coordinates': list(polys)}


def at(x_km, y_km): return (LAT0 + y_km * KM_LAT, LON0 + x_km * KM_LON)


def world(t, extra_us=None):
    L = pathlib.Path(t) / 'links'
    for d in ('data/us-key', 'data/ca-key', 'data/world-key', 'data/outlines', '.github'):
        (L / d).mkdir(parents=True, exist_ok=True)
    (L / '.github/scripts').symlink_to(LINKS / '.github/scripts')
    pins = {'US-9001': at(0, 0), 'US-9002': at(0, 0), 'US-9003': at(0, 0), 'US-9004': at(0, 0), 'US-9005': at(0, 0),
            'US-9006': at(0, 0), 'US-9007': at(0, 0), 'US-9008': at(0, 0), 'US-9009': at(0, 0), 'US-9010': at(0, 0), 'US-9011': at(0, 0)}
    (L / 'locations.json').write_text(json.dumps([['POTA', r, r, la, lo, 'https://example.org/park/' + r] for r, (la, lo) in pins.items()]))
    us = {
        # T1: record 501 in two parks by name; record 777 in two parks, both reviewed (a person said same land)
        'US-9001': {'n': 'Alpha', 'g': 'official', 'm': [[501, 'Alpha Lands', 100, 'name']], 'bk': [501, 0.0, 'SP', 'des']},
        'US-9002': {'n': 'Beta', 'g': 'official', 'm': [[501, 'Alpha Lands', 100, 'name'], [777, 'Twin', 50, 'reviewed']], 'bk': [501, 0.0, 'SP', 'des']},
        'US-9003': {'n': 'Gamma', 'g': 'official', 'm': [[777, 'Twin', 50, 'reviewed: same land, two numbers']], 'bk': [777, 0.0, 'SP', 'des']},
        # T2
        'US-9004': {'n': 'Chain', 'g': 'official', 'm': [[601, 'Chain', 10, 'name']], 'bk': [601, 0.0, 'SP', 'des']},
        'US-9005': {'n': 'Cut', 'g': 'official', 'm': [[602, 'Cut', 10, 'name']], 'bk': [602, 0.0, 'SP', 'des']},
        # T4
        'US-9006': {'n': 'Near', 'g': 'official', 'm': [[603, 'Near', 1, 'name']], 'bk': [603, 0.05, 'SP', 'des']},
        'US-9007': {'n': 'Off', 'g': 'official', 'm': [[604, 'Off', 1, 'name']], 'bk': [604, 0.3, 'SP', 'des']},
        'US-9008': {'n': 'Off reviewed', 'g': 'official', 'm': [[605, 'Off reviewed', 1, 'reviewed']], 'bk': [605, 0.3, 'SP', 'des']},
        'US-9009': {'n': 'Big', 'g': 'official', 'm': [[606, 'Big', 100000, 'name']], 'bk': [606, 1.0, 'NF', 'des']},
        # T5: holder sgzza1 (100 ac) holds the pin; 900 is PAD-US, name only, 500 ac, drawn -> row; 901 same idea but not drawn;
        # sgzza2 same layer as the holder; 902 reviewed
        'US-9010': {'n': 'Size', 'g': 'official', 'bk': ['sgzza1', 0.0, 'SP', 'des'],
                    'm': [['sgzza1', 'Size SP', 100, 'name'], [900, 'Size Lake', 500, 'name'], [901, 'Size Forest', 900, 'name'],
                          ['sgzza2', 'Size Big', 800, 'name'], [902, 'Size Reviewed', 700, 'reviewed']]},
        'US-9011': {'n': 'Hole', 'g': 'official', 'm': [[607, 'Hole', 1000, 'name']], 'bk': [607, 0.0, 'SP', 'des']},
    }
    us.update(extra_us or {})
    (L / 'data/us-key/US-ZZ.json').write_text(json.dumps({'parks': us}))
    (L / 'data/us-key/index.json').write_text(json.dumps({'build': 'US-1'}))
    (L / 'data/ca-key/CA-ZZ.json').write_text(json.dumps({'parks': {'CA-9001': {'m': [[11, 'X', 1, 'name']]}, 'CA-9002': {'m': [[11, 'X', 1, 'name']]}}}))
    # world: id 5 in two parks but from two sources (not one record); id 6 from one source in two parks (one record)
    (L / 'data/world-key/ZZ.json').write_text(json.dumps({'parks': {
        'ZZ-0001': {'m': [[5, 'A', 'Layer One', 'name'], [6, 'C', 'Layer One', 'name']]},
        'ZZ-0002': {'m': [[5, 'B', 'Layer Two', 'name'], [6, 'C', 'Layer One', 'name']]}}}))
    feats = []
    def f(ref, geom, ids):
        feats.append({'type': 'Feature', 'geometry': geom, 'properties': {'ref': ref, 'name': ref, 'g': 'official', 'layer_url': 'https://gis.example.gov/arcgis/rest/services/Secret/MapServer/3',
                                                                          'record_ids': [str(i) for i in ids]}})
    f('US-9001', mp(sq(0, 0, 1)), [501]); f('US-9002', mp(sq(0, 0, 1)), [501, 777]); f('US-9003', mp(sq(0, 0, 1)), [777])
    f('US-9004', mp(sq(0, 0, 1), sq(20, 0, 1), sq(40, 0, 1)), [601])       # 0 / 19 / 39 km: chained
    f('US-9005', mp(sq(0, 0, 1), sq(40, 0, 1)), [602])                      # 0 / 39 km: a 39 km gap
    f('US-9006', mp(sq(0.1 + 0.05, 0, 0.1)), [603])                         # pin 50 m west of a 200 m square
    f('US-9007', mp(sq(0.1 + 0.3, 0, 0.1)), [604])                          # pin 300 m west
    f('US-9008', mp(sq(0.1 + 0.3, 0, 0.1)), [605])                          # pin 300 m west, reviewed
    f('US-9009', mp(sq(20 + 1.0, 0, 20)), [606])                            # 40 km square, pin 1 km west: slack = 0.1 x radius (~2.26 km)
    f('US-9010', mp(sq(0, 0, 1)), ['sgzza1', 900, 'sgzza2', 902])
    f('US-9011', mp(sq(0, 0, 3, hole_km=1)), [607])                         # pin in the hole: 3 km to the outer ring -> T4
    doc = {'type': 'FeatureCollection', 'kpc': {}, 'features': feats}
    with gzip.GzipFile(L / 'data/outlines/US-ZZ.geojson.gz', 'wb', mtime=0) as g: g.write(json.dumps(doc).encode())
    return L


def tree_hash(d):
    h = hashlib.sha256()
    for p in sorted(pathlib.Path(d).rglob('*')):
        if p.is_file() and '.github' not in p.parts: h.update(str(p.relative_to(d)).encode() + p.read_bytes())
    return h.hexdigest()


def run(args, cwd=None):
    return subprocess.run([sys.executable, str(S / 'kpc_tripwires.py'), 'run'] + args, capture_output=True, text=True, timeout=300, cwd=cwd)


with tempfile.TemporaryDirectory() as t:
    t = pathlib.Path(t)
    L = world(t)
    keys = {'US-ZZ': json.load(open(L / 'data/us-key/US-ZZ.json'))['parks']}
    # 1. T1
    r1, census = T.t1(keys, 'us')
    rec = {r['record']: r for r in r1}
    check('1. T1: record 501 in US-9001 and US-9002 (one key file) is a row', '501' in rec and rec['501']['parks'] == ['US-9001', 'US-9002'] and not rec['501']['all_person'])
    check('1. T1: record 777, every join a person\'s (same land, two numbers), is a row marked all_person', rec.get('777', {}).get('all_person') is True)
    w, wc = T.t1({'ZZ': json.load(open(L / 'data/world-key/ZZ.json'))['parks']}, 'world')
    check('1. T1 world: equal ids of two sources are not one record (only id 6 of Layer One is a row); census way counts 2',
          [r['record'] for r in w] == ['6'] and w[0]['layer'] == 'layer-one' and wc == 2)
    # 2-4 via the whole run on the fixture
    out, ns, cl = t / 'tw', t / 'kpcdata/data/waiting/tripwires/not-sure.json', t / 'kpcdata/data/waiting/tripwires/cleared.json'
    before = tree_hash(L)
    p = run(['--links', str(L), '--out', str(out), '--not-sure', str(ns), '--cleared', str(cl), '--date', '2026-11-17'])
    check(f'6. a run with tripwires flagged exits 0 (got {p.returncode}: {p.stderr[-300:]})', p.returncode == 0)
    rep = json.load(open(out / 'counts/latest.json'))
    rows = {tw: [json.load(open(x)) for x in sorted((out / 'waiting' / tw).glob('*.json'))] for tw in ('T1', 'T2', 'T4', 'T5')}
    refs = {tw: sorted({i.get('ref') for g in v for i in g['items']}) for tw, v in rows.items()}
    check(f"2. T2: 0/19/39 km pieces chain; 0/39 km is cut (flagged {refs['T2']})", refs['T2'] == ['US-9005'])
    t2 = next((i for g in rows['T2'] for i in g['items']), {})   # no T2 row = a FAIL line below, not a crash
    check('2. T2 row: 2 pieces, 1 cut off, gap ~39 km, pattern gap_25-50km', t2.get('pieces') == 2 and t2.get('pieces_cut_off') == 1 and 38 < t2.get('gap_km', 0) < 40 and t2.get('pattern') == 'gap_25-50km')
    # sent back 17 Nov: on a runner without shapely / pyproj the bot counted no T2 / T4. It now needs the standard library only.
    blocker = t / 'noextra'
    for mod in ('shapely', 'pyproj', 'numpy'):
        (blocker / mod).mkdir(parents=True); (blocker / mod / '__init__.py').write_text(f'raise ImportError("{mod} blocked by the test")\n')
    pb = subprocess.run([sys.executable, str(S / 'kpc_tripwires.py'), 'run', '--links', str(L), '--dry-run', '--keys', 'us'], capture_output=True, text=True,
                        timeout=300, env=dict(os.environ, PYTHONPATH=str(blocker)))
    tb = (json.loads(pb.stdout[pb.stdout.index('{'):pb.stdout.rindex('}') + 1]).get('totals') or {}).get('us', {}) if '{' in pb.stdout else {}
    check(f"2/3. standard library only: with shapely, pyproj and numpy blocked the same T2 1 / T4 2 ({pb.returncode}, {tb})",
          pb.returncode == 0 and tb.get('T2') == 1 and tb.get('T4') == 2)
    check('2/3. the plane is exact from the pin: 39 km east and 3 km north come back as ~39000 m and ~3000 m',
          abs(math.hypot(*T._plane(LAT0, LON0)(LON0 + 39 * KM_LON, LAT0)) - 39000) < 200 and abs(T._plane(LAT0, LON0)(LON0, LAT0 + 3 * KM_LAT)[1] - 3000) < 20)
    check(f"3. T4: 300 m off (US-9007) and pin in a hole (US-9011) flagged; 50 m off, reviewed, big park within a tenth of its radius not ({refs['T4']})",
          refs['T4'] == ['US-9007', 'US-9011'])
    hole = next((i for g in rows['T4'] for i in g['items'] if i['ref'] == 'US-9011'), {})
    check('2/3. a pin in a hole is not inside: its distance is to the outer ring (~3 km), not the hole (1 km)', 2.9 < hole.get('pin_km_from_land', 0) < 3.1)
    check(f"2/3. T2 and T4 were counted (nothing left out: {rep.get('not_counted')}, unread {rep.get('unread')})", not rep.get('not_counted') and not rep.get('unread'))
    check('3. edge slack = max(100 m, a tenth of the radius)', T.edge_slack(0) == 100 and abs(T.edge_slack(math.pi * 5000 ** 2) - 500) < 1e-6)
    t5 = [i for g in rows['T5'] for i in g['items']]
    check(f"4. T5 size form: only PAD-US 900 (500 ac, name only, drawn, other layer) over holder sgzza1 (100 ac) ({[(i['ref'], i['big_record']) for i in t5]})",
          [(i['ref'], i['big_record'], i['pattern'], i['times']) for i in t5] == [('US-9010', '900', 'sgzza_to_padus', 5.0)])
    check('5. T3 is the key build\'s: not counted here', rep['totals']['us']['T3'] == 'from the key build (not counted here)')
    check('6. binds nothing: binds false, report_only true, the slack numbers listed as on trial',
          rep['binds'] is False and rep['report_only'] is True and rep['on_trial']['T2_gap_km'] == 25 and rep['on_trial']['T5_size_times'] == 3)
    check('6. every input file is byte-identical after the run (no key, pin or outline changed)', tree_hash(L) == before)
    alltxt = p.stdout + p.stderr + ''.join(x.read_text() for x in out.rglob('*') if x.is_file()) + ns.read_text()
    check('6. no web / file address in any output file or the log (the outline layer_url and the pin links are not copied)',
          '://' not in alltxt and 'gis.example.gov' not in alltxt)
    check('totals: US T1 2, T2 1, T4 2, T5 1; Canada T1 1; world T1 1 (census way 2)',
          {k: rep['totals']['us'][k] for k in ('T1', 'T2', 'T4', 'T5')} == {'T1': 2, 'T2': 1, 'T4': 2, 'T5': 1}
          and rep['totals']['ca']['T1'] == 1 and rep['totals']['world']['T1'] == 1 and rep['totals']['world']['T1_census_method'] == 2)
    # T6 (Handoff 8): this fixture stacks many parks on one square at one pin, so T6 lights up here too; T6 is proven in its own file
    # (tests/test_tripwires_t6_nov17.py), and the T1-T5 checks below look at T1-T5 only.
    check('per-area counts', {k: v for k, v in rep['areas']['US-ZZ'].items() if k != 'T6'} == {'T1': 2, 'T2': 1, 'T4': 2, 'T5': 1})
    # 8. D10 list
    d = json.load(open(ns))
    d15 = {r: [w for w in v if w != 'T6'] for r, v in d['parks'].items() if [w for w in v if w != 'T6']}
    check(f"8. not-sure list: T1 by name (9001, 9002), T2 (9005), T4 (9007, 9011); the person's same-land record (9003) is not on it ({d15})",
          d15 == {'US-9001': ['T1'], 'US-9002': ['T1'], 'US-9005': ['T2'], 'US-9007': ['T4'], 'US-9011': ['T4'],
                         'CA-9001': ['T1'], 'CA-9002': ['T1'], 'ZZ-0001': ['T1'], 'ZZ-0002': ['T1']} and set(d['reasons']) == {'T1', 'T2', 'T4', 'T6'})
    check('8. the list is small (under 1 MB) and LF only', ns.stat().st_size < 1_000_000 and b'\r' not in ns.read_bytes())
    cl.write_text(json.dumps({'parks': {'US-9007': {'by': 'KPC owner', 'date': '2026-11-18', 'why': 'pin checked'}, 'US-9005': {'why': 'no name'}}}))
    # 7. the meter: add a T1 family and run again
    L2 = world(t / 'b', extra_us={'US-9012': {'n': 'New', 'g': 'official', 'm': [['sgqqa9', 'New', 5, 'name']], 'bk': ['sgqqa9', 0.0, 'SP', 'des']},
                                  'US-9013': {'n': 'New2', 'g': 'official', 'm': [['sgqqa9', 'New', 5, 'name']], 'bk': ['sgqqa9', 0.0, 'SP', 'des']}})
    p2 = run(['--links', str(L2), '--out', str(out), '--not-sure', str(ns), '--cleared', str(cl), '--date', '2026-11-18'])
    rep2 = json.load(open(out / 'counts/latest.json'))
    check(f"7. the jump shows the next morning (US T1 +1: {rep2['jump']['us']}) and the new pattern sgqqa_name", p2.returncode == 0 and rep2['jump']['us'] == {'T1': 1}
          and 'sgqqa_name' in rep2['new_patterns'].get('T1', []) and 'T1 +1' in p2.stdout)
    h = (out / 'counts/history.csv').read_text().splitlines()
    check('7. history.csv: one line per key per day (2 days x 3 keys)', h[0] == 'date,key,T1,T2,T3,T4,T5,T6' and len(h) == 7)
    d2 = json.load(open(ns))
    check('8. a person\'s clear (with by) takes US-9007 off; a clear with no by (US-9005) does not', 'US-9007' not in d2['parks'] and 'US-9005' in d2['parks'] and d2['cleared_left_out'] == 1)
    # 5. T3 from a key build file
    (L2 / 'data/us-key/review').mkdir(); (L2 / 'data/us-key/review/tripwire-t3.json').write_text(json.dumps({'count': 7, 'rows': []}))
    check('5. a key build\'s tripwire-t3.json count is carried', T.t3_hook(L2, 'us') == {'T3': 7})
    # 6. dry run writes nothing; never red; red only on unreadable inputs
    o3 = t / 'dry'
    p3 = run(['--links', str(L2), '--out', str(o3), '--dry-run'])
    check('6. a dry run writes nothing', p3.returncode == 0 and not o3.exists() and 'dry run: nothing written' in p3.stdout)
    (L2 / 'data/ca-key/CA-ZZ.json').write_text('{broken')
    p4 = run(['--links', str(L2), '--dry-run'])
    check('6. one unreadable key file is a warning, not red (exit 0)', p4.returncode == 0 and '::warning' in p4.stdout and 'CA-ZZ' in p4.stdout)
    (t / 'empty').mkdir()
    p5 = run(['--links', str(t / 'empty'), '--dry-run'])
    check('6. no KPC-Links checkout (no locations.json) = red (exit 1)', p5.returncode == 1 and '::error' in p5.stdout)
    for k in ('us-key', 'ca-key', 'world-key'):
        for x in (L2 / 'data' / k).glob('*.json'): x.unlink()
    p6 = run(['--links', str(L2), '--dry-run'])
    check('6. no key file at all = red (exit 1)', p6.returncode == 1 and 'no key file' in p6.stdout)
# 6. network refused
code = ('import sys; sys.path.insert(0, %r); import kpc_tripwires as T; T.no_network()\n'
        'import socket\ntry:\n    socket.create_connection(("example.org", 80)); print("CONNECTED")\nexcept T.NoNetwork: print("REFUSED")\n'
        'try:\n    socket.socket().connect(("127.0.0.1", 9)); print("CONNECTED")\nexcept T.NoNetwork: print("REFUSED")\n') % str(S)
r = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True, timeout=60)
check('6. the bot refuses every network call (create_connection and socket.connect)', r.stdout.split() == ['REFUSED', 'REFUSED'])
check('6. the scrub takes web / file / svc addresses out', T.scrub({'a': 'see https://x.gov/a/MapServer/1 and file:US-TN.json.gz', 'b': ['svc:https://y']})
      == {'a': 'see [address withheld] and [address withheld]', 'b': ['[address withheld]']})
# 9. workflow
Y = (ROOT / '.github/workflows/kpc-tripwires.yml').read_text(encoding='utf-8')
import yaml  # noqa: E402
on = yaml.safe_load(Y)[True]
live_cron = [l for l in Y.splitlines() if 'cron:' in l and not l.lstrip().startswith('#')]
check('9. by hand only: workflow_dispatch only and no cron line at all, not even a commented one (a commented cron reads as a paused bot)',
      list(on) == ['workflow_dispatch'] and not live_cron and not re.search(r'^\s*#\s*-?\s*cron:', Y, re.M) and "cron '47 11 * * *'" in Y)
check('9. no extra install step: the bot needs the standard library only', 'pip install' not in Y and 'shapely' not in Y and 'pyproj' not in Y)
check('9. writes only branch tripwires and data/waiting/tripwires/not-sure.json on KPC-Data; KPC-Links is read-only',
      'kpc_push_retry.sh tripwires' in Y and 'kpc_push_retry.sh main 4 "data/waiting/tripwires/not-sure.json"' in Y
      and 'git add data/waiting/tripwires/not-sure.json' in Y and 'persist-credentials: false' in Y and 'git add -A' not in Y.split('cd kpcdata && git add')[1])
check('9. no workflow_run trigger and no other run started', 'workflow_run' not in Y and 'gh workflow run' not in Y)
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
