#!/usr/bin/env python3
"""Nov 11 (KPC owner, 2026-11-11): offline checks of the tracer's line agreement and the TIGERweb water source. No network.

  1. A perfect square grid ties with its 90-degree decoy and stays refused with lines too (it really is ambiguous). An irregular town
     seen through a sparse picture fails today; with the line agreement the true fit clears the SAME gate (ratio 1.5, margin 2.0).
     (60 synthetic towns, dev run Nov 11: right place drawn 37 -> 57, drawn at a wrong transform 1 -> 0, wrong-place pictures drawn 0 -> 0.)
  2. The wrong place: a picture of another town still fails the gate with line agreement on.
  3. LINE_WEIGHT 0 gives exactly the junction score (the Nov 2 behaviour).
  4. fetch_basemap: TIGERweb water lines and shores are read by name from the service's layer list; a robots 'no' on it drops only that
     source; any other failure of it is logged and the map goes on (never stops a map); NHD is asked exactly as before (robots honoured);
     every request goes to a host on the allowed list; no services*.arcgis.com.

Runs with the workflow's requirements (shapely, pyproj). Where they are missing (a box without them), small stand-ins are used for
the two pieces these checks touch (pyproj's Transformer, shapely's import); line_crossings is then checked separately as skipped."""
import math, pathlib, re, sys, tempfile, types
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
stand_in = []
try:
    import shapely  # noqa: F401
except ImportError:
    stand_in.append('shapely')
    sh = types.ModuleType('shapely'); sh.geometry = types.ModuleType('shapely.geometry'); sh.validation = types.ModuleType('shapely.validation')
    sh.ops = types.ModuleType('shapely.ops')
    for n in ('LineString', 'Point', 'Polygon', 'mapping', 'MultiLineString'): setattr(sh.geometry, n, object)
    sh.validation.make_valid = sh.ops.unary_union = sh.unary_union = lambda *a, **k: None
    sys.modules.update({'shapely': sh, 'shapely.geometry': sh.geometry, 'shapely.validation': sh.validation, 'shapely.ops': sh.ops})
try:
    import pyproj  # noqa: F401
except ImportError:
    stand_in.append('pyproj')
    pj = types.ModuleType('pyproj')

    class Transformer:   # equirectangular about the pin: enough for these offline checks (fetch_basemap does not project)
        def __init__(self, fwd, lat0, lon0):
            self.fwd, self.lat0, self.lon0, self.k = fwd, lat0, lon0, 111320.0

        @staticmethod
        def from_crs(a, b, always_xy=True):
            crs = b if str(b).startswith('+proj') else a
            lat0 = float(re.search(r'\+lat_0=(\S+)', crs).group(1)); lon0 = float(re.search(r'\+lon_0=(\S+)', crs).group(1))
            return Transformer(crs is b, lat0, lon0)

        def transform(self, x, y):
            c = self.k * math.cos(math.radians(self.lat0))
            x, y = np.asarray(x, float), np.asarray(y, float)
            return ((x - self.lon0) * c, (y - self.lat0) * self.k) if self.fwd else (x / c + self.lon0, y / self.k + self.lat0)
    pj.Transformer = Transformer
    sys.modules['pyproj'] = pj
import kpc_trace_picture as TP  # noqa: E402
import kpc_trace_edges as LE  # noqa: E402

ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg)


def gate(real, decoy):   # the tracer's better-than-chance gate, unchanged
    return real >= max(TP.CHANCE_RATIO * decoy, decoy + TP.CHANCE_MARGIN)


def town(seed, spacing=200.0, n=12, lake=True):
    """Metric basemap: a square street grid + one winding road + a lake shore. Returns (junctions Q, lines)."""
    rng = np.random.default_rng(seed)
    half = spacing * n / 2
    xs = np.arange(-half, half + 1, spacing)
    lines = [[(x, -half), (x, half)] for x in xs] + [[(-half, y), (half, y)] for y in xs]
    x, y, a = -half, rng.uniform(-half, half), rng.uniform(-0.3, 0.3); wr = [(x, y)]
    while abs(x) <= half and abs(y) <= half:
        a += rng.normal(0, 0.18); x += 40 * math.cos(a); y += 40 * math.sin(a); wr.append((x, y))
    lines.append(wr)
    if lake:
        th = np.linspace(0, 2 * np.pi, 90); r = 260 + 60 * np.sin(3 * th + seed)
        cx, cy = rng.uniform(-half / 2, half / 2, 2)
        lines.append(list(zip(cx + r * np.cos(th), cy + r * np.sin(th))))
    Q = np.array([(x, y) for x in xs for y in xs])
    return Q, lines



def irregular(seed, n=10):
    rng = np.random.default_rng(seed)
    xs = np.cumsum(rng.uniform(120, 320, n)); xs -= xs.mean()
    ys = np.cumsum(rng.uniform(120, 320, n)); ys -= ys.mean()
    hx, hy = abs(xs).max(), abs(ys).max()
    lines, Q = [], []
    for x in xs:
        if rng.random() < 0.8: lines.append([(x + rng.normal(0, 15), -hy), (x + rng.normal(0, 15), hy)])
    for y in ys:
        if rng.random() < 0.8: lines.append([(-hx, y + rng.normal(0, 15)), (hx, y + rng.normal(0, 15))])
    # junctions = crossings of the kept lines
    V = [l for l in lines if abs(l[0][1]) > 1 and l[0][1] == -hy]; H = [l for l in lines if l[0][0] == -hx]
    for v in V:
        for hh in H:
            x = (v[0][0] + v[1][0]) / 2; y = (hh[0][1] + hh[1][1]) / 2
            Q.append((x, y))
    x, y, a = -hx, rng.uniform(-hy, hy), rng.uniform(-0.3, 0.3); wr = [(x, y)]
    while abs(x) <= hx and abs(y) <= hy:
        a += rng.normal(0, 0.18); x += 40 * math.cos(a); y += 40 * math.sin(a); wr.append((x, y))
    lines.append(wr)
    th = np.linspace(0, 2 * np.pi, 90); r = 200 + 50 * np.sin(3 * th + seed); cx, cy = rng.uniform(-hx / 2, hx / 2), rng.uniform(-hy / 2, hy / 2)
    lines.append(list(zip(cx + r * np.cos(th), cy + r * np.sin(th))))
    return np.array(Q), lines


def picture(Q, lines, z, t, w=1000, h=1000, seed=0):
    """What a picture map gives the tracer: junction candidates P (with misses and clutter) and LSD-like segments."""
    rng = np.random.default_rng(seed + 99)
    p = (Q[:, 0] + 1j * Q[:, 1] - t) / z
    P = np.c_[p.real, -p.imag]
    P = P[(P[:, 0] > 5) & (P[:, 0] < w - 5) & (P[:, 1] > 5) & (P[:, 1] < h - 5)]
    P = P[rng.random(len(P)) > 0.35]                      # a third of the junctions are not found on the picture
    P = P + rng.normal(0, 1.2, P.shape)                   # and the rest are a pixel or so off
    P = np.vstack([P, rng.uniform(0, w, (12, 2))])[:70]
    segs = []
    for ln in lines:
        a = np.asarray(ln, float)
        a = LE.sample_lines([a], 30.0)
        q = (a[:, 0] + 1j * a[:, 1] - t) / z
        q = np.c_[q.real, -q.imag]
        segs += [[*q[i], *q[i + 1]] for i in range(len(q) - 1)]
    for _ in range(150):
        x, y = rng.uniform(0, w, 2); ang = rng.uniform(0, np.pi); L = rng.uniform(5, 35)
        segs.append([x, y, x + L * math.cos(ang), y + L * math.sin(ang)])
    return P, np.array(segs)


def run(P, segs, Q, lines, z_true, weight):
    TP.LINE_WEIGHT = weight
    smin, smax = abs(z_true) / 2.5, abs(z_true) * 2.5
    prior = TP.Prior(smin, smax, 30.0, (300, 300, 700, 700))
    c = np.array([500.0, 500.0])
    LS = LE.sample_lines(LE.clip_lines([np.asarray(l, float) for l in lines], 5000.0), max(1.0, smin * LE.CELL_PX / 2))
    ev = LE.LineEvidence((1000, 1000), segs, roi=(0, 0, 1000, 1000))
    fn = (lambda S: (lambda z_, t_: ev.score(z_, t_, S)))
    best = TP.match(P, Q, c, prior, 75.0, line=fn(LS))
    dec = 0.0
    for ang in (90, 180, 270):
        r = np.exp(1j * math.radians(ang)) * (Q[:, 0] + 1j * Q[:, 1])
        d = TP.match(P, np.c_[r.real, r.imag], c, prior, 75.0, line=fn(LE.rotate(LS, ang)))
        if d and d['score'] > dec: dec = d['score']
    return best, dec


z_true = 4.0 * np.exp(1j * math.radians(7.0)); t_true = 0j - z_true * (500 - 500j)   # pin (0, 0) at the picture centre
Q, lines = town(1)
P, segs = picture(Q, lines, z_true, t_true)
b0, d0 = run(P, segs, Q, lines, z_true, 0.0)
check(f'grid town, junctions only: the true fit and its rotated decoy tie (score {b0["score"]:.1f} vs decoy {d0:.1f}): NO FIT, as today',
      b0 is not None and not gate(b0['score'], d0))
check('LINE_WEIGHT 0: the score is the junction score alone (Nov 2 behaviour)', b0 is not None and b0['score'] == b0['score_points'])
b1, d1 = run(P, segs, Q, lines, z_true, 0.25)
check(f'perfect grid with line agreement: still refused (a square grid looks the same turned 90 degrees, lines too; score {b1["score"]:.1f} vs decoy {d1:.1f})',
      b1 is None or not gate(b1['score'], d1))
Qi, li = irregular(1)                                   # an irregular town, sparse picture (few junctions found)
Pi, si = picture(Qi, li, z_true, t_true, seed=1); Pi = Pi[: max(6, len(Pi) // 4)]
bi0, di0 = run(Pi, si, Qi, li, z_true, 0.0)
bi1, di1 = run(Pi, si, Qi, li, z_true, 0.25)
err = abs(bi1['z'] - z_true) / abs(z_true) if bi1 else 9
check(f'irregular town, junctions only: NO FIT (score {bi0["score"] if bi0 else 0:.1f} vs decoy {di0:.1f})', bi0 is None or not gate(bi0['score'], di0))
check(f'irregular town, with line agreement: clears the SAME gate at the true transform (score {bi1["score"]:.1f} vs decoy {di1:.1f}, line z {bi1["line_z"]:.1f}, scale error {100 * err:.1f}%)',
      bi1 is not None and gate(bi1['score'], di1) and err < 0.05 and abs(bi1['t'] - t_true) < 50 and bi1['line_z'] >= TP.LINE_MIN_Z)
Qo, lines_o = town(7)
P2, segs2 = picture(Qo, lines_o, z_true, t_true, seed=7)   # a picture of ANOTHER town against this basemap
b2, d2 = run(P2, segs2, Q, lines, z_true, 0.25)
check(f'wrong place: still refused with line agreement on (score {b2["score"] if b2 else 0:.1f} vs decoy {d2:.1f})',
      b2 is None or not gate(b2['score'], d2) or b2['line_z'] < TP.LINE_MIN_Z)
check('the gate constants are unchanged (ratio 1.5, margin 2.0) and the new line gate only adds a refusal', TP.CHANCE_RATIO == 1.5 and TP.CHANCE_MARGIN == 2.0 and TP.LINE_MIN_Z > 0)
TP.LINE_WEIGHT = 0.25


# ---- 4) fetch_basemap with a fake web client
class FakeHttp:
    def __init__(self, hydro='ok'):
        self.urls, self.hydro = [], hydro

    def get_json(self, url, params):
        TP.PoliteHttp.check_host(url)   # the club's host rule, as in the real client
        self.urls.append(url)
        if 'hydro.nationalmap.gov' in url: raise RuntimeError('robots: hydro.nationalmap.gov robots.txt does not allow it')
        if url.startswith(TP.TIGER_HYDRO):
            if self.hydro == 'robots': raise RuntimeError('robots: tigerweb.geo.census.gov robots.txt does not allow /arcgis/rest/services/TIGERweb/Hydro')
            if self.hydro == 'down': raise RuntimeError('HTTP 503 after 5 tries')
            if url == TP.TIGER_HYDRO: return {'layers': [{'id': 0, 'name': 'Linear Hydrography Labels'}, {'id': 1, 'name': 'Linear Hydrography'}, {'id': 2, 'name': 'Areal Hydrography'}]}   # the real names (TIGERweb/Hydro); a Labels layer first, to prove it is skipped
            if url.endswith('/1/query'): return {'features': [{'geometry': {'type': 'LineString', 'coordinates': [[-85.001, 38.0], [-84.999, 38.0]]}}]}
            if url.endswith('/2/query'): return {'features': [{'geometry': {'type': 'Polygon', 'coordinates': [[[-85.0, 38.0], [-85.0, 38.001], [-84.999, 38.001], [-85.0, 38.0]]]}}]}
        if url.startswith(TP.TIGER):
            return {'features': [{'geometry': {'type': 'LineString', 'coordinates': [[-85.0, 37.999], [-85.0, 38.001]]}}]}
        return {'features': []}


real_cross = TP.line_crossings
if 'shapely' in stand_in: TP.line_crossings = lambda a, b, max_points=3000: []
TP.log = lambda m: None
for mode in ('ok', 'robots', 'down'):
    with tempfile.TemporaryDirectory() as td:
        h = FakeHttp(mode)
        bm = TP.fetch_basemap(h, 'US-0001', 38.0, -85.0, 1.0, pathlib.Path(td), use_cache=False)
        kinds = {k for k, _ in bm['lines']}
        hosts = {u.split('/')[2] for u in h.urls}
        check(f'{mode}: every request on the allowed host list, none to services*.arcgis.com ({sorted(hosts)})',
              hosts <= TP.ALLOWED_BASEMAP_HOSTS and not any('arcgis.com' in x for x in hosts))
        check(f'{mode}: NHD asked only as before, its robots no honoured (water skipped)', 'water' in bm['skipped'] and sum('nationalmap' in u for u in h.urls) == 1)
        check(f'{mode}: the roads are still read and the map goes on', 'road' in kinds and any('Transportation' in s for s in bm['sources']))
        if mode == 'ok':
            check('ok: TIGERweb water lines and shores read by their real layer names (the Labels layer not read)', {'water', 'shore'} <= kinds and not any(u.startswith(TP.TIGER_HYDRO + '/0') for u in h.urls)
                  and any('hydrography' in s for s in bm['sources']))
        if mode == 'robots':
            check('robots: only the Census water source is dropped and named', 'census water' in bm['skipped'] and not ({'water', 'shore'} & kinds))
        if mode == 'down':
            check('down: a failed water read is not a stopped map, and is not called robots', 'census water' not in bm['skipped'] and not ({'water', 'shore'} & kinds))
TP.line_crossings = real_cross
check('the cached basemap version moved (old caches without water are read again once)', TP.__version__ == '0.3.0')
if stand_in: print('NOTE stand-ins used for: ' + ', '.join(stand_in) + ' (the workflow installs the real ones)')
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
