#!/usr/bin/env python3
"""Nov 11 2026 (KPC owner, 2026-11-11): the hand map placer's checker, .github/scripts/draft/kpc_hand_place.py. Offline; every socket
is refused for the checker's own run. Needs numpy + OpenCV (the tracer's requirements); shapely / pyproj are not needed.
  - the shared fixture tests/fixtures/hand-place-cases.json (KPC-Links kpc-map-placer-math.js wrote its numbers) gives the same
    numbers in Python; with node and a KPC-Links checkout (LINKS=...) the JS module is also run live on every case;
  - the gate numbers are the tracer's own; each gate has a passing and a failing click set;
  - a tampered click set (transform edited, a point moved, another picture) fails; the written trace has exactly the automatic
    trace's fields (read from the tracer's own code) plus via + hand; output is deterministic; the pin is never moved; WDPA refused;
  - with LINKS: the trace goes through kpc_fers.py's real approximate-outline path (add_approx_outlines, area_spots, pc_tag) the same
    way as the same trace without the hand marker, inside a bigger park and outside it.
python3 -B tests/test_hand_place_nov11.py"""
import ast, copy, hashlib, importlib.util, json, math, os, pathlib, shutil, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
DRAFT = ROOT / '.github/scripts/draft'
FIX = ROOT / 'tests/fixtures/hand_place/hand-place-cases.json'
sys.path.insert(0, str(DRAFT))
import kpc_hand_place as H   # noqa: E402
import cv2   # noqa: E402
import numpy as np   # noqa: E402

ok = True


def check(c, m):
    global ok
    print(('PASS ' if c else 'FAIL ') + m)
    ok = ok and bool(c)


def near(a, b, t):
    if a is None or b is None:
        return a is b
    if isinstance(a, list):
        return isinstance(b, list) and len(a) == len(b) and all(near(x, y, t) for x, y in zip(a, b))
    return abs(float(a) - float(b)) <= t


DOC = json.loads(FIX.read_text())
PIN = DOC['pin']


def run_case(c):
    """The same outputs the JS test stores, computed by the Python checker's maths."""
    pin = c.get('pin') or PIN
    fit = H.fit_pairs(c['pairs'], pin) if len(c['pairs']) >= 2 else None
    out = dict(n=len(c['pairs']))
    if fit:
        pl = H.place_shape(fit['T'], pin, c['shape']['px'], c['shape']['kind'])
        af = fit['affine']
        out.update(z=[fit['T'][0], fit['T'][1]], t=[fit['T'][2], fit['T'][3]], rms=fit['rms'], residuals=fit['residuals'], loo=fit['loo'],
                   loo_rms=fit['loo_rms'], loo_max=fit['loo_max'], scale=fit['scale'], rotation_deg=fit['rotation_deg'],
                   affine_det_sign=(0 if not af else (1 if af['det'] > 0 else -1)), stretch=af['stretch'] if af else None, spread=fit['spread'],
                   lonlat=pl['lonlat'], area_acres=pl['area_acres'], length_km=pl['length_km'], pin_dist_m=pl['pin_dist_m'])
    out['gates'] = [g['id'] + ':' + ('pass' if g['pass'] else 'fail') for g in H.hand_gates(fit, c['shape'], [q['layer'] for q in c['pairs']], pin)]
    return out


# ---------------------------------------------------------------- 1. the shared fixture, both languages
TOL = dict(lonlat=1.01e-7)
for k, c in DOC['cases'].items():
    got, exp = run_case(c['input']), c['expected']
    diff = [x for x in exp if not (got.get(x) == exp[x] if x in ('gates', 'n') else near(got.get(x), exp[x], TOL.get(x, 1e-6)))]
    check(not diff, f'fixture case {k}: Python gives the numbers the JS module stored' + (f' (differs: {diff})' if diff else ''))
L = DOC['limits']
check(L['MAX_FIT_M'] == H.TP.MAX_FIT_M and L['MIN_POINTS'] == H.TP.MIN_POINTS and L['PIN_MAX_OUTSIDE_M'] == H.TP.PIN_MAX_OUTSIDE_M
      and L['SIMPLIFY_M'] == H.TP.SIMPLIFY_M and tuple(L['SCALE_RANGE']) == tuple(H.TL.GEOPDF_SCALE_RANGE) and L['SKEW_MAX'] == H.TL.GEOPDF_SKEW_MAX,
      "the page's preview numbers are the tracer's own (MAX_FIT_M 50, MIN_POINTS 3, PIN_MAX_OUTSIDE_M 1000, SIMPLIFY_M 3, scale, skew)")
check(L['HAND_MIN_POINTS'] == H.HAND_MIN_POINTS and L['HAND_COLLINEAR_MIN'] == H.HAND_COLLINEAR_MIN and L['HAND_SPREAD_MIN'] == H.HAND_SPREAD_MIN
      and L['HAND_EXTRAP_MAX'] == H.HAND_EXTRAP_MAX and L['HAND_ROT_FLAG_DEG'] == H.HAND_ROT_FLAG_DEG and sorted(DOC['basemaps']) == sorted(H.BASEMAPS),
      'the hand-point gate numbers and the government map list agree between the page and the checker')
check(H.MAX_FIT_M is H.TP.MAX_FIT_M and H.LINE_MIN_Z is H.TP.LINE_MIN_Z and H.CHANCE_RATIO is H.TP.CHANCE_RATIO and H.SKEW_MAX is H.TL.GEOPDF_SKEW_MAX,
      'the checker IMPORTS the tracer constants (same objects, not copies)')
LINKS = pathlib.Path(os.environ.get('LINKS') or ROOT.parent / 'links')
JSM = LINKS / 'kpc-map-placer-math.js'
if JSM.exists() and shutil.which('node'):
    js = ("const M=require(%s);const d=require(%s);const o={};for(const [k,c] of Object.entries(d.cases)){const p=c.input.pin||d.pin;"
          "const f=c.input.pairs.length>=2?M.fitPairs(c.input.pairs,p):null;o[k]=f?{z:[f.T.a,f.T.b],t:[f.T.tx,f.T.ty],rms:f.rms,loo:f.loo,"
          "ll:M.placeShape(f.T,p,c.input.shape.px,c.input.shape.kind).lonlat}:null;}console.log(JSON.stringify(o));") % (json.dumps(str(JSM)), json.dumps(str(FIX)))
    live = json.loads(subprocess.run(['node', '-e', js], capture_output=True, text=True, timeout=60).stdout)
    worst = 0.0
    for k, c in DOC['cases'].items():
        pin = c['input'].get('pin') or PIN
        f = H.fit_pairs(c['input']['pairs'], pin) if len(c['input']['pairs']) >= 2 else None
        if f is None or live[k] is None:
            check(f is None and live[k] is None, f'live JS and Python agree there is no fit for {k}')
            continue
        worst = max(worst, abs(f['rms'] - live[k]['rms']), *[abs(a - b) for a, b in zip(f['T'][2:], live[k]['t'])])
        check(H.place_shape(f['T'], pin, c['input']['shape']['px'], c['input']['shape']['kind'])['lonlat'] == live[k]['ll'],
              f'live JS and Python place {k} on the same rounded coordinates')
    check(worst < 1e-6, f'live JS vs Python: worst difference {worst:.1e} m (shift and fit error)')
    check(LINKS.joinpath('tests/fixtures/hand-place-cases.json').read_bytes() == FIX.read_bytes(), 'the fixture is byte-identical in both repos')
else:
    print('SKIP live JS comparison: no node or no KPC-Links checkout (set LINKS=...)')


# ---------------------------------------------------------------- a synthetic park on disk (the tracer's input folder)
REF, W, Hh = 'US-99001', 1200, 900
Z0 = 1.5 * complex(math.cos(math.radians(15)), math.sin(math.radians(15)))
T0 = (Z0.real, Z0.imag, 0.0, 0.0)
m0 = H.apply_sim(T0, 600, 450)
T0 = (Z0.real, Z0.imag, 30 - m0[0], -20 - m0[1])
RING = [[420, 300], [780, 280], [860, 520], [700, 690], [430, 640], [380, 470]]
PTS = [[150, 120], [1050, 160], [1000, 800], [200, 760], [640, 430]]


def ll_of(T, x, y, pin=PIN):
    m = H.apply_sim(T, x, y)
    la, lo = H.tm_inv(pin[0], pin[1], *m)
    return [round(la, 7), round(lo, 7)]


def make_base(tmp, row_extra=None):
    base = pathlib.Path(tmp) / 'base'
    (base / 'maps').mkdir(parents=True, exist_ok=True)
    img = np.full((Hh, W, 3), 235, np.uint8)
    for a, b in ([(0, 200), (1200, 260)], [(300, 0), (360, 900)], [(800, 0), (900, 900)], [(0, 700), (1200, 650)]):
        cv2.line(img, a, b, (90, 90, 90), 6)
    cv2.polylines(img, [np.array(RING, np.int32)], True, (40, 160, 40), 4)
    cv2.imwrite(str(base / 'maps' / f'{REF}_test-park.jpg'), img, [cv2.IMWRITE_JPEG_QUALITY, 80])
    row = dict(name='Test Lake State Park', agency='Test State Parks', source_url='https://parks.example.gov/maps/test-lake.pdf', page=1,
               source_type='official', image=f'maps/{REF}_test-park.jpg', map_file=f'{REF}_test-park.jpg', type='State Park')
    row.update(row_extra or {})
    (base / 'index.json').write_text(json.dumps({REF: row}))
    (base / 'pins.json').write_text(json.dumps({REF: PIN}))
    return base


def click_set(base, pairs_px=PTS, ring=RING, kind='area', T=T0, layers=None, nudge=None, pin=PIN):
    pic = base / 'maps' / f'{REF}_test-park.jpg'
    pairs = []
    for i, p in enumerate(pairs_px):
        g = ll_of(T, *(nudge[i] if nudge and i in nudge else p))
        pairs.append(dict(n=i + 1, px=list(p), ll=g, layer=(layers or {}).get(i, 'usgs-topo'), zoom=17))
    cs = dict(format=H.FORMAT, tool='test', ref=REF, park=dict(name='Test Lake State Park', type='State Park', pin=list(pin), pin_source='pins.json'),
              picture=dict(file=f'maps/{REF}_test-park.jpg', source_url='https://parks.example.gov/maps/test-lake.pdf', page=1,
                           sha256=hashlib.sha256(pic.read_bytes()).hexdigest(), width=W, height=Hh, loaded_from='test'),
              pairs=pairs, shape=dict(kind=kind, px=[list(p) for p in ring], **{'from': 'hand'}), date='2026-11-11', by='tester')
    f = H.fit_pairs(pairs, PIN) if len(pairs) >= 2 else None   # what the page writes (the page's own sums, mirrored)
    cs['fit'] = dict(model='similarity', z=[f['T'][0], f['T'][1]], t=[f['T'][2], f['T'][3]], scale_m_per_px=f['scale'], rotation_deg=f['rotation_deg'],
                     residuals_m=f['residuals'], rms_m=f['rms'], loo_m=f['loo'], loo_rms_m=f['loo_rms'], loo_max_m=f['loo_max']) if f else dict(model='similarity')
    cs['gates'] = []
    return cs


def place(cs, base, **k):
    try:
        return H.place(cs, base, **k)
    except H.Refused as e:
        return 'REFUSED', [str(e)], None, None, []


tmp = tempfile.mkdtemp(prefix='kpc-hand-')
base = make_base(tmp)

# ---------------------------------------------------------------- 2. a good placement, and the written trace's format
good = click_set(base)
st, why, fc, rep, _ = place(good, base)
check(st == 'DRAWN' and fc is not None, f'a good click set is placed: {st} {why}')
props = fc['features'][0]['properties']
src = (DRAFT / 'kpc_trace_picture.py').read_text()
auto_keys, unoff_keys = None, None
for node in ast.walk(ast.parse(src)):
    if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'props' for t in node.targets) and isinstance(node.value, ast.Call):
        auto_keys = [kw.arg for kw in node.value.keywords]
    if (isinstance(node, ast.Expr) and isinstance(node.value, ast.Call) and getattr(node.value.func, 'attr', '') == 'update'
            and getattr(node.value.func.value, 'id', '') == 'props'):
        unoff_keys = [kw.arg for kw in node.value.keywords]
check(auto_keys and list(props)[:len(auto_keys)] == auto_keys and list(props)[len(auto_keys):] == ['via', 'hand'],
      f'the trace has exactly the automatic trace\'s fields, in its order ({len(auto_keys)} read from kpc_trace_picture.py), plus via and hand')
check(props['grade'] == H.TP.GRADE and props['status'] == 'DRAWN' and props['use_for_2fer'] is False and props['official'] is False
      and props['via'] == 'hand points' and props['model'] == 'similarity', "grade 'approximate (picture map)', DRAWN, use_for_2fer false, official false, via 'hand points'")
check(all(set(c) == {'px', 'lon', 'lat'} for c in props['control_points']) and len(props['control_points']) == 5, 'control_points in the tracer\'s {px, lon, lat} form')
g = fc['features'][0]['geometry']
check(g['type'] == 'Polygon' and g['coordinates'][0][0] == g['coordinates'][0][-1]
      and all(round(v, 7) == v for p in g['coordinates'][0] for v in p), 'a closed Polygon in lon / lat, 7 decimals (the tracer\'s rounding)')
check(props['fit_m'] < 1 and props['fit_loo_m'] < 1 and abs(props['area_acres'] - DOC['cases']['exact']['expected']['area_acres']) < 0.051,
      f"fit {props['fit_m']} m, leave-one-out {props['fit_loo_m']} m, {props['area_acres']} acres")
check(props['hand']['click_set'] == good and props['hand']['click_set_sha256'] == hashlib.sha256(H.canonical(good).encode()).hexdigest(),
      'the whole click set is saved inside the trace with its sha256')
check(rep['status'] == 'DRAWN' and set(rep) <= set(H.TP.REPORT_FIELDS), 'the report row uses the tracer\'s report.csv columns')
out = pathlib.Path(tmp) / 'out'
H.write_outputs(out, fc, rep)
b1 = (out / f'{REF}.json').read_bytes()
H.write_outputs(out, place(copy.deepcopy(good), base)[2], rep)
check((out / f'{REF}.json').read_bytes() == b1, 'deterministic: placing the same click set again writes the same bytes')
check((out / 'report.csv').read_text().splitlines()[0].split(',') == H.TP.REPORT_FIELDS, 'report.csv header is the tracer\'s')
unoff_base = make_base(pathlib.Path(tmp) / 'u', dict(source_type='unofficial', source_org='Friends of Test Lake', notes='no agency map; looked at the state site'))
fcu = place(click_set(unoff_base), unoff_base)[2]
pu = fcu['features'][0]['properties']
check(unoff_keys and list(pu)[:len(auto_keys) + len(unoff_keys)] == auto_keys + unoff_keys and pu['status'] == H.TP.STATUS_UNOFFICIAL
      and pu['grade'] == H.TP.GRADE_UNOFFICIAL, 'an unofficial row gets the tracer\'s unofficial fields, status and grade too')

# ---------------------------------------------------------------- 3. every gate: pass above, fail here
def fails(cs, b=base, **k):
    st, why, fc, rep, _ = place(cs, b, **k)
    return st, ' | '.join(why), fc
st, w, f = fails(click_set(base, pairs_px=PTS[:3]))
check(st == 'NO FIT' and f is None and 'points:' in w, f'3 pairs (the tracer\'s minimum) are not enough by hand: {st}')
st, w, f = fails(click_set(base, pairs_px=PTS[:2]))
check(st == 'NO FIT' and f is None and 'points:' in w and 'leave_one_out' in w, f'2 pairs refused: {st}')
st, w, f = fails(click_set(base, nudge={3: (200 + 60, 760 - 40)}))
check(st == 'NO FIT' and f is None and 'leave_one_out_worst' in w, f'one pair 100 m off: refused on the worst leave-one-out: {w[:120]}')
far = [[100, 100], [1100, 140], [150, 820], [1050, 780]]
st, w, f = fails(click_set(base, pairs_px=far, nudge={0: (100 + 70, 100 + 40), 1: (1100 - 70, 140 - 40), 2: (150 - 60, 820 + 45), 3: (1050 + 60, 780 - 45)}))
check(st == 'NO FIT' and 'fit:' in w, f'fit error over 50 m refused: {w[:100]}')
st, w, f = fails(click_set(base, pairs_px=[[100, 100], [400, 104], [700, 101], [1000, 103]]))
check(st == 'NO FIT' and 'not_on_a_line' in w, 'points on a line refused')
st, w, f = fails(click_set(base, pairs_px=[[600, 420], [640, 430], [620, 470], [660, 460]]))
check(st == 'NO FIT' and 'points_cover_shape' in w and 'no_far_extrapolation' in w, 'bunched points refused')
mir = click_set(base)
for q, p in zip(mir['pairs'], PTS):
    q['px'] = [W - p[0], p[1]]
mf = H.fit_pairs(mir['pairs'], PIN)
mir['fit'].update(z=[mf['T'][0], mf['T'][1]], t=[mf['T'][2], mf['T'][3]], rms_m=mf['rms'], loo_rms_m=mf['loo_rms'])
st, w, f = fails(mir)
check(st == 'NO FIT' and 'not_mirrored' in w, 'a mirrored picture refused')
st, w, f = fails(click_set(base, layers={2: 'osm'}))
check(st == 'NO FIT' and 'government_basemap' in w, 'a point clicked on OpenStreetMap refused (Rule 6)')
pin_far = [PIN[0] + 0.03, PIN[1]]
pf_base = make_base(pathlib.Path(tmp) / 'pf')
(pf_base / 'pins.json').write_text(json.dumps({REF: pin_far}))
cs_pf = click_set(pf_base, pin=pin_far)
pf = H.fit_pairs(cs_pf['pairs'], pin_far)
cs_pf['fit'].update(z=[pf['T'][0], pf['T'][1]], t=[pf['T'][2], pf['T'][3]], rms_m=pf['rms'], loo_rms_m=pf['loo_rms'])
st, w, f = fails(cs_pf, pf_base)
check(st == 'NEEDS A PERSON' and f is None and 'pin' in w, f'the POTA pin 3 km from the outline: held, no trace ({st}; the pin is not moved)')
big = (Z0.real * 15, Z0.imag * 15, T0[2] * 15, T0[3] * 15)   # the same picture at 22.5 m per pixel: about 19,000 acres
ramp = make_base(pathlib.Path(tmp) / 'r', dict(type='Boat Ramp'))
cs_big = click_set(ramp, T=big)
st, w, f = fails(cs_big, ramp)
check(st == 'NEEDS A PERSON' and f is None and 'ceiling' in w, f'an absurd size for the park type (boat ramp, about 19,000 ac): held: {w[-140:]}')
small = make_base(pathlib.Path(tmp) / 's', dict(acres=4))
st, w, f = fails(click_set(small), small)
check(st == 'NEEDS A PERSON' and 'known 4 ac' in w, 'traced 85 ac vs a known 4 ac: held (0.2x-5x, the tracer\'s rule)')
cross = click_set(base, ring=[[420, 300], [860, 520], [780, 280], [430, 640]])
st, w, f = fails(cross)
check(st == 'NO FIT' and 'shape' in w, 'an outline that crosses itself refused')
trail = click_set(base, ring=[[300, 600], [500, 450], [700, 480], [900, 300]], kind='trail')
st, w, f = fails(trail)
check(st == 'DRAWN' and f['features'][0]['geometry']['type'] == 'LineString' and f['features'][0]['properties']['area_acres'] is None, 'a trail line is placed as a LineString')

# ---------------------------------------------------------------- 4. refusals of the input itself
def refused(cs, b=base, **k):
    try:
        H.place(cs, b, **k)
        return ''
    except H.Refused as e:
        return str(e)
e = copy.deepcopy(good); e['fit']['z'][0] *= 1.001
check('edited' in refused(e), 'a click set whose transform was edited is refused')
e = copy.deepcopy(good); e['fit']['rms_m'] = 1.0
check('edited' in refused(e), 'a click set whose fit error was edited is refused')
e = copy.deepcopy(good); e['pairs'][1]['px'][0] += 40
check('edited' in refused(e), 'a click set with a point moved after the fit is refused')
e = copy.deepcopy(good); e['picture']['sha256'] = '0' * 64
check('wrong picture' in refused(e), 'a click set made on another picture (sha256) is refused')
e = copy.deepcopy(good); e['park']['pin'] = [PIN[0] + 0.001, PIN[1]]
check('not the POTA pin' in refused(e), 'a click set with a moved pin is refused (pins are never moved)')
e = copy.deepcopy(good); e['by'] = 'from the WDPA download'
check('WDPA' in refused(e), 'a WDPA-tagged click set is refused')
wd = make_base(pathlib.Path(tmp) / 'w', dict(source_url='https://www.protectedplanet.net/en/thematic-areas/wdpa/map.pdf'))
check('WDPA' in refused(click_set(wd), wd), 'an index row from Protected Planet is refused')
osm = make_base(pathlib.Path(tmp) / 'o', dict(source_url='https://www.openstreetmap.org/export/map.png'))
check('banned' in refused(click_set(osm), osm), "the tracer's own check_row refuses a banned map site")
e = copy.deepcopy(good); e['picture']['file'] = 'maps/US-99001_other.jpg'
check('saved picture' in refused(e), 'a click set naming another picture file is refused')
nopic = make_base(pathlib.Path(tmp) / 'n')
gcs = click_set(nopic)
(nopic / 'maps' / f'{REF}_test-park.jpg').unlink()
check('not here' in refused(gcs, nopic), 'no trace is written when the picture is not there to check its sha256')

# ---------------------------------------------------------------- 5. Quality's re-check (--check)
tr = out / f'{REF}.json'
check(H.check_trace(tr, base) == [], '--check: an untouched trace re-checks identical')
bad_t = json.loads(tr.read_text()); bad_t['features'][0]['properties']['hand']['click_set']['fit']['t'][0] += 5.0
(out / 'b1.json').write_text(json.dumps(bad_t))
p1 = H.check_trace(out / 'b1.json', base)
check(any('sha256' in x for x in p1) and any('edited' in x for x in p1), '--check: an edited transform in the stored click set fails')
bad_t = json.loads(tr.read_text()); bad_t['features'][0]['properties']['hand']['click_set']['pairs'][2]['ll'][0] += 0.0003
(out / 'b2.json').write_text(json.dumps(bad_t))
check(H.check_trace(out / 'b2.json', base) != [], '--check: a moved point in the stored click set fails')
bad_t = json.loads(tr.read_text()); bad_t['features'][0]['geometry']['coordinates'][0][1][0] += 0.0001
(out / 'b3.json').write_text(json.dumps(bad_t))
p3 = H.check_trace(out / 'b3.json', base)
check(p3 and 'geometry' in p3[0], '--check: an edited outline fails (differs from a fresh placement)')
other = pathlib.Path(tmp) / 'other.jpg'
cv2.imwrite(str(other), np.full((Hh, W, 3), 128, np.uint8))
check(any('wrong picture' in x for x in H.check_trace(tr, base, picture=other)), '--check: another picture file (sha256) fails')
r = subprocess.run([sys.executable, '-B', str(DRAFT / 'kpc_hand_place.py'), '--check', str(tr), str(out / 'b1.json'), '--base', str(base)],
                   capture_output=True, text=True, timeout=120)
check(r.returncode == 1 and 'OK   ' in r.stdout and 'FAIL ' in r.stdout, '--check from the command line: exit 1 when any trace differs')

# ---------------------------------------------------------------- 6. no network: the command line with every socket refused
spy = pathlib.Path(tmp) / 'spy'
spy.mkdir()
(spy / 'sitecustomize.py').write_text(
    "import socket, os\nLOG = os.environ['NETLOG']\n"
    "def _no(*a, **k):\n    open(LOG, 'a').write(repr(a[:2]) + '\\n'); raise OSError('network refused in this test')\n"
    "socket.socket.connect = _no\nsocket.create_connection = _no\nsocket.getaddrinfo = _no\n")
cs_file = pathlib.Path(tmp) / 'good.clicks.json'
cs_file.write_text(json.dumps(good))
netlog = pathlib.Path(tmp) / 'net.txt'
env = dict(os.environ, PYTHONPATH=str(spy), NETLOG=str(netlog))
r = subprocess.run([sys.executable, '-B', str(DRAFT / 'kpc_hand_place.py'), str(cs_file), '--base', str(base), '--out', str(pathlib.Path(tmp) / 'out2')],
                   capture_output=True, text=True, timeout=120, env=env)
check(r.returncode == 0 and 'DRAWN' in r.stdout and not netlog.exists(), f'placed with every socket refused, and no connection was tried (exit {r.returncode})')
check((pathlib.Path(tmp) / 'out2' / f'{REF}.json').read_bytes() == b1, 'the command line writes the same bytes as the function')
r = subprocess.run([sys.executable, '-B', str(DRAFT / 'kpc_hand_place.py'), str(pathlib.Path(tmp) / 'nofile.json'), '--base', str(base), '--out', str(out)],
                   capture_output=True, text=True, timeout=60, env=env)
check(r.returncode == 2 and 'REFUSED' in r.stdout, 'a missing / unreadable click set: exit 2, REFUSED')

# ---------------------------------------------------------------- 7. line agreement on a saved basemap (synthetic: the picture's own roads)
roads = [[(0, 200), (1200, 260)], [(300, 0), (360, 900)], [(800, 0), (900, 900)], [(0, 700), (1200, 650)]]
bm = dict(pin=PIN, half_km=3.0, lines=[['road', [[ll_of(T0, *p)[1], ll_of(T0, *p)[0]] for p in [a, b]]] for a, b in roads])
bmf = pathlib.Path(tmp) / f'{REF}_basemap.json'
bmf.write_text(json.dumps(bm))
st, w, f, rp, _ = H.place(good, base, basemap=str(bmf))
le = f['features'][0]['properties']['hand']['checker']['lines'] if f else {}
check(st == 'DRAWN' and le.get('evaluated') and le['line_z'] >= H.LINE_MIN_Z and all(x['pass'] for x in le['gates']),
      f"the tracer's line agreement scores the hand fit on the basemap: z {le.get('line_z')} vs decoy {le.get('decoy_line_z')}")
wrong = dict(bm, lines=[['road', [[ll_of(T0, *p)[1] + 0.004, ll_of(T0, *p)[0] - 0.003] for p in [a, b]]] for a, b in roads])
bmw = pathlib.Path(tmp) / 'wrong_basemap.json'
bmw.write_text(json.dumps(wrong))
st, w, f, rp, _ = H.place(good, base, basemap=str(bmw))
check(st == 'NO FIT' and 'line_agreement' in ' '.join(w), 'roads that do not sit on the picture\'s lines: refused by the line gate')
lt = pathlib.Path(tmp) / 'lt'
H.write_outputs(lt, H.place(good, base, basemap=str(bmf))[2], rp)
check(any('--basemap' in x for x in H.check_trace(lt / f'{REF}.json', base)) and H.check_trace(lt / f'{REF}.json', base, basemap=str(bmf)) == [],
      '--check of a line-scored trace needs the same basemap, and passes with it')

# ---------------------------------------------------------------- 8. the 2-fer path in KPC-Links (kpc_fers.py, not edited), same as an automatic trace
KF = LINKS / '.github/scripts/kpc_fers.py'
if KF.exists():
    sys.path.insert(0, str(KF.parent))
    try:
        import kpc_fers as F
    except Exception as ex:  # noqa: BLE001
        F = None
        check(False, f'kpc_fers.py imports offline ({type(ex).__name__}: {ex})')
    if F is not None:
        hand = json.loads(tr.read_text())
        auto = copy.deepcopy(hand)   # the same trace as the automatic tracer writes it: no via, no hand
        for k in ('via', 'hand'):
            auto['features'][0]['properties'].pop(k)
        eh, ea = H.fers_entry(hand), H.fers_entry(auto)
        check({k: v for k, v in eh.items() if k != 'via'} == ea and eh['via'] == 'hand points', 'the fers-approx-outlines entry is the automatic one plus via')
        BIG, OUTSIDE = 'US-99002', 'US-99003'
        ring = eh['rings'][0]
        lo = [p[0] for p in ring]; la = [p[1] for p in ring]
        big_ring = [[min(lo) - 0.01, min(la) - 0.01], [max(lo) + 0.01, min(la) - 0.01], [max(lo) + 0.01, max(la) + 0.01], [min(lo) - 0.01, max(la) + 0.01], [min(lo) - 0.01, min(la) - 0.01]]
        root = pathlib.Path(tmp) / 'links-root'
        (root / 'data').mkdir(parents=True)
        res = {}
        for name, entry in (('hand', eh), ('auto', ea)):
            (root / 'data/fers-approx-outlines.json').write_text(json.dumps({'parks': {REF: entry, OUTSIDE: dict(entry, rings=[[[x + 0.2, y] for x, y in ring]])}}))
            F.APX_OUT.clear(); F.APX_PARKS.clear()
            PINS = {r: (r, PIN[0], PIN[1], '', 'State Park', 'KY') for r in (REF, BIG, OUTSIDE)}
            parks = {BIG: {'st': 'US-KY', 'ids': [11], 'names': {'11': 'Big Forest'}}}
            skip = {}
            _hs = F.has_official_outline
            F.has_official_outline = lambda ref, parks=None, root=None: bool(((parks or {}).get(ref) or {}).get('ids')) and not ((parks or {}).get(ref) or {}).get('approx')
            try:
                F.add_approx_outlines(parks, PINS, skip, 'na', root=str(root))
            finally:
                F.has_official_outline = _hs
            G = {BIG: [[big_ring]], REF: [parks[REF]['rings']], OUTSIDE: [parks[OUTSIDE]['rings']]}
            box_in = [min(lo) - 0.02, min(la) - 0.02, max(lo) + 0.02, max(la) + 0.02]
            box_out = [box_in[0] + 0.2, box_in[1], box_in[2] + 0.2, box_in[3]]
            sp_in = F.area_spots(G, [BIG, REF], box_in)
            sp_out = F.area_spots(G, [BIG, OUTSIDE], box_out)
            tagged = F.pc_tag({'spots': copy.deepcopy(sp_in)})['spots']
            res[name] = dict(entered={r: {k: v for k, v in parks[r].items()} for r in (REF, OUTSIDE)}, n_in=len(sp_in), n_out=len(sp_out),
                             tag=[{k: x.get(k) for k in ('tier', 'list', 'official_boundary', 'approx_note', 'approx_refs')} for x in tagged])
        h, a = res['hand'], res['auto']
        check(h['entered'][REF].get('approx') and h['entered'] == a['entered'], 'add_approx_outlines enters the hand trace exactly as the automatic one (approx, apx| id, rings)')
        check(h['n_in'] >= 1 and h['n_in'] == a['n_in'], f"inside a bigger park: area_spots finds the overlap ({h['n_in']} spot), same as the automatic trace")
        check(h['n_out'] == 0 and a['n_out'] == 0, 'not inside any park: no spot, for both')
        check(h['tag'] == a['tag'] and all(t['tier'] == 'approximate' and t['official_boundary'] is False and t['approx_note'] == F.APX_NOTE for t in h['tag']),
              f"pc_tag makes it an APPROXIMATE 2-fer with the not-official note, same as the automatic trace: {h['tag'][:1]}")
        try:
            H.fers_entry(json.loads(json.dumps(dict(type='FeatureCollection', features=[dict(fc['features'][0], geometry=dict(type='LineString', coordinates=[[0, 0], [1, 1]]))]))))
            check(False, 'a trail line is not offered as an outline entry')
        except H.Refused:
            check(True, 'a trail line is not offered as an outline entry')
else:
    print('SKIP 2-fer path: no KPC-Links checkout (set LINKS=...)')

check(H.selftest.__code__ is not None and subprocess.run([sys.executable, '-B', str(DRAFT / 'kpc_hand_place.py'), '--selftest'], capture_output=True, text=True).returncode == 0,
      'kpc_hand_place.py --selftest passes')
shutil.rmtree(tmp, ignore_errors=True)
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
