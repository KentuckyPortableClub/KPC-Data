#!/usr/bin/env python3
"""Nov 11 (KPC owner, 2026-11-11, later): end-to-end synthetic checks of the matcher-input switches (kpc_trace_marks.py), through the
tracer's OWN detect_boundary, detect_junctions, match, choose_model and the unchanged gates (3 points, RMS and leave-one-out under 50 m,
better than the rotated decoy by 1.5x and +2, line z >= 2). No network.

  1. A campground map with its roads drawn as bands: with the Nov 11 inputs OFF it is NO FIT (as in the Nov 11 run on CA-6283 /
     CA-5612 / US-7858); ON, the same gates pass at the true place (scale error < 5%, place error < 30 m).
  2. Wrong placements are still refused with the switches ON: the same picture against another campground's basemap, against the true
     basemap turned 90 degrees, and against the true basemap with every junction moved 90-160 m (beyond the 75 m tolerance).
  3. A thick black boundary line (New Brunswick sheets): no boundary with the switch OFF (NO LINE today); found ON, and it is the drawn
     outline (overlap over 85%). Pages without such a line, and a filled dark area, still give none.
  4. Each switch alone off gives back the old result for its part (the switches are separable for the owner's measurement).
Uses the workflow's requirements; where shapely / pyproj are missing, the stand-ins of line_score_test.py are used (nothing here
projects or builds a polygon)."""
import math, os, pathlib, sys, types
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
    pj = types.ModuleType('pyproj'); pj.Transformer = object; sys.modules['pyproj'] = pj
import cv2  # noqa: E402
import kpc_trace_picture as TP  # noqa: E402
import kpc_trace_marks as TM  # noqa: E402
import kpc_trace_edges as LE  # noqa: E402

TP.log = lambda m: None
ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg)


def switches(**kw):
    for k, v in kw.items():
        setattr(TP, k.upper(), bool(v))


def to_m(P, z, t):
    p = P[:, 0] - 1j * P[:, 1]
    m = z * p + t
    return np.c_[m.real, m.imag]


def basemap(seed, z, t, extra=60):
    """Basemap junctions (metres) = the picture's road-network junctions under (z, t) + junctions of roads outside the picture."""
    img, true, outline, lines_px = TM.synthetic_campground(seed, grid=(5, 4), with_lines=True)
    nodes = true[:len(true) - 14]
    Q = to_m(nodes, z, t)
    rng = np.random.default_rng(seed + 50)
    Q = np.vstack([Q, rng.uniform(-2500, 2500, (extra, 2))])
    L = [to_m(np.array(l, float), z, t) for l in lines_px]
    return img, outline, Q, L


def trace(img, Q, lines_m, outline):
    """The tracer's matching steps on one picture (process_one, without the network and the polygon output). Returns (verdict, best)."""
    h, w = img.shape[:2]
    row = {}
    bnd = TP.detect_boundary(img, row, k=8)
    if bnd is None:
        return 'NO LINE', None
    allp = np.vstack(bnd.get('parcels') or [bnd['pts_px']])
    bx, by, bw, bh = cv2.boundingRect(np.round(allp).astype(np.int32))
    roi = (bx - bw, by - bh, bx + 2 * bw, by + 2 * bh)
    bex = TM.junction_exclusions(img, allp) if TP.BOX_MASK else None
    P, _w, segs = TP.detect_junctions(img, max_points=70, roi=roi, box_exclude=bex)
    smin, smax = 0.2, min(25.0, 4.0 * 5.0 * 1000.0 / max(bw, bh, 1))
    padx, pady = max(0.25 * bw, 50), max(0.25 * bh, 50)
    prior = TP.Prior(smin, smax, 25.0, (bx - padx, by - pady, bx + bw + padx, by + bh + pady))
    c = np.array([w / 2.0, h / 2.0])
    LS = LE.sample_lines(LE.clip_lines([np.asarray(l, float) for l in lines_m], 6000.0), max(1.0, smin * LE.CELL_PX / 2.0))
    ev = LE.LineEvidence(img.shape, segs, roi=roi)
    fn = (lambda S: (lambda z_, t_: ev.score(z_, t_, S)))
    best = TP.match(P, Q, c, prior, 75.0, line=fn(LS))
    dec = 0.0
    for ang in (90, 180, 270):
        r = np.exp(1j * math.radians(ang)) * (Q[:, 0] + 1j * Q[:, 1])
        d = TP.match(P, np.c_[r.real, r.imag], c, prior, 75.0, line=fn(LE.rotate(LS, ang)))
        if d and d['score'] > dec:
            dec = d['score']
    if best is None:
        return 'NO FIT (no match)', None
    from sklearn.neighbors import KDTree
    tree = KDTree(Q)
    mm = best['z'] * (P[:, 0] - 1j * P[:, 1]) + best['t']
    dist, idx = tree.query(np.c_[mm.real, mm.imag], k=1)
    sel = {}
    for i in np.nonzero(dist[:, 0] < 75.0)[0]:
        j = idx[i, 0]
        if j not in sel or dist[i, 0] < dist[sel[j], 0]:
            sel[j] = i
    pi = np.array(list(sel.values())); qj = np.array(list(sel.keys()))
    why = []
    if len(pi) < TP.MIN_POINTS:
        why.append(f'only {len(pi)} points')
    else:
        _k, _m, rms, loo, _r, _c = TP.choose_model(P[pi], Q[qj])
        if not rms < TP.MAX_FIT_M: why.append(f'RMS {rms:.0f}')
        if not (math.isnan(loo) or loo < TP.MAX_FIT_M): why.append(f'LOO {loo:.0f}')
        if best['score'] < max(TP.CHANCE_RATIO * dec, dec + TP.CHANCE_MARGIN):
            why.append(f'not better than the decoy ({best["score"]:.1f} vs {dec:.1f})')
        if best.get('line_n', 0) >= LE.MIN_SAMPLES and best.get('line_z', 0.0) < TP.LINE_MIN_Z:
            why.append(f'line z {best["line_z"]:.1f}')
    best['decoy'] = dec
    best['n_final'] = len(pi)
    return ('DRAWN' if not why else 'NO FIT: ' + '; '.join(why)), best


z_true = 2.2 * np.exp(1j * math.radians(6.0))       # 2.2 m per picture pixel, map turned 6 degrees
img, outline, Q, L = basemap(4, z_true, 0j)
pin = outline.mean(0)
t_true = -z_true * (pin[0] - 1j * pin[1])           # the pin (in the park) is metre (0, 0)
img, outline, Q, L = basemap(4, z_true, t_true)

switches(band_junctions=0, box_mask=0, dark_ring=0)
v_old, b_old = trace(img, Q, L, outline)
check(f'campground, roads drawn as bands, Nov 11 inputs OFF: {v_old} (the Nov 11 run: NO FIT)', v_old != 'DRAWN')
switches(band_junctions=1, box_mask=1, dark_ring=1)
v_new, b_new = trace(img, Q, L, outline)
err_s = abs(abs(b_new['z']) / abs(z_true) - 1) if b_new else 9
err_t = abs(b_new['t'] - t_true) if b_new else 9e9
check(f'campground, inputs ON: {v_new} at the true place (scale error {100 * err_s:.1f}%, place error {err_t:.0f} m, '
      f'{b_new["n_final"] if b_new else 0} points, score {b_new["score"] if b_new else 0:.1f} vs decoy {b_new["decoy"] if b_new else 0:.1f}, '
      f'line z {b_new["line_z"] if b_new else 0:.1f})', v_new == 'DRAWN' and err_s < 0.05 and err_t < 30)
for name in ('band_junctions', 'box_mask'):
    switches(band_junctions=1, box_mask=1, dark_ring=1)
    setattr(TP, name.upper(), False)
    v1, b1 = trace(img, Q, L, outline)
    print(f'NOTE campground with only {name} off: {v1}')
switches(band_junctions=1, box_mask=1, dark_ring=1)

# ---- 1b. box_mask alone: a thin-line road map whose legend box (inside the search area) is full of crossing symbols. Each symbol is
# a 'junction' with 4 arms, so they outrank the roads' T junctions and fill the 70 places (seen on CA-5612, US-7858, US-10387).
def legend_clutter(seed):
    im, true_, outline_, lines_px = TM.synthetic_campground(seed, grid=(6, 2), with_lines=True, roads_as='line')
    x0, y0 = 1080, 470
    cv2.rectangle(im, (x0, y0), (x0 + 300, y0 + 560), (255, 255, 255), -1)
    cv2.rectangle(im, (x0, y0), (x0 + 300, y0 + 560), (20, 20, 20), 3)
    for r_ in range(13):
        for c_ in range(5):
            cx, cy = x0 + 30 + c_ * 55, y0 + 30 + r_ * 41
            for d_ in (-7, 7):
                for a_ in (math.radians(30), math.radians(120)):
                    ox, oy = d_ * math.cos(a_ + math.pi / 2), d_ * math.sin(a_ + math.pi / 2)
                    p0 = (int(cx + ox - 16 * math.cos(a_)), int(cy + oy - 16 * math.sin(a_)))
                    p1 = (int(cx + ox + 16 * math.cos(a_)), int(cy + oy + 16 * math.sin(a_)))
                    cv2.line(im, p0, p1, (20, 20, 20), 2, cv2.LINE_AA)
    return im, true_, outline_, lines_px
imc, true_c, outline_c, lines_c = legend_clutter(4)
Qc = np.vstack([to_m(true_c[:len(true_c) - 14], z_true, t_true), np.random.default_rng(54).uniform(-2500, 2500, (60, 2))])
Lc = [to_m(np.array(l, float), z_true, t_true) for l in lines_c]
switches(band_junctions=1, box_mask=0, dark_ring=1)
v_c0, _b = trace(imc, Qc, Lc, outline_c)
switches(band_junctions=1, box_mask=1, dark_ring=1)
v_c1, b_c1 = trace(imc, Qc, Lc, outline_c)
err_c = abs(b_c1['t'] - t_true) if b_c1 else 9e9
check(f'thin-line road map with a symbol-filled legend: box_mask OFF {v_c0}; ON {v_c1} at the true place (place error {err_c:.0f} m)',
      v_c0 != 'DRAWN' and v_c1 == 'DRAWN' and err_c < 30)

# ---- 2. wrong placements stay refused with every switch ON
img_b, outline_b, Q_b, L_b = basemap(9, z_true, t_true)            # another campground's basemap, same place
v, _b = trace(img, Q_b, L_b, outline)
check(f'wrong place (another campground\'s basemap): {v}', v != 'DRAWN')
r90 = np.exp(1j * math.radians(90))
Qr = (Q[:, 0] + 1j * Q[:, 1]) * r90
Lr = [np.c_[((l[:, 0] + 1j * l[:, 1]) * r90).real, ((l[:, 0] + 1j * l[:, 1]) * r90).imag] for l in L]
v, _b = trace(img, np.c_[Qr.real, Qr.imag], Lr, outline)
check(f'wrong place (the true basemap turned 90 degrees): {v}', v != 'DRAWN')
rng = np.random.default_rng(77)                                       # the right place, but every basemap junction 90-160 m off
ang = rng.uniform(0, 2 * np.pi, len(Q)); rad = rng.uniform(90, 160, len(Q))
v, _b = trace(img, Q + np.c_[rad * np.cos(ang), rad * np.sin(ang)], L, outline)
check(f'basemap junctions all moved beyond the 75 m tolerance (90-160 m, random directions): {v}', v != 'DRAWN')

# ---- 3. boundaries that were NO LINE
for label, (pic, drawn) in (('thick black boundary line (New Brunswick sheets)', TM.synthetic_dark_ring(5)),
                            ('thick black boundary line, a two-lobe park', TM.synthetic_dark_ring(8, two_lobes=True))):
    switches(band_junctions=1, box_mask=1, dark_ring=0)
    b0 = TP.detect_boundary(pic, {}, k=8)
    switches(band_junctions=1, box_mask=1, dark_ring=1)
    b1 = TP.detect_boundary(pic, {}, k=8)
    a_true = cv2.contourArea(drawn.astype(np.float32))
    a_got = cv2.contourArea(np.asarray(b1['pts_px'], np.float32)) if b1 else 0.0
    inter = 0.0
    if b1:
        m1 = np.zeros(pic.shape[:2], np.uint8); m2 = np.zeros_like(m1)
        cv2.fillPoly(m1, [drawn.astype(np.int32)], 1); cv2.fillPoly(m2, [np.round(b1['pts_px']).astype(np.int32)], 1)
        inter = float((m1 & m2).sum()) / float((m1 | m2).sum())
    check(f'{label}: OFF {"no boundary" if b0 is None else "a boundary"} (Nov 11 run: NO LINE); ON the drawn outline '
          f'(overlap {100 * inter:.0f}%, area {a_got:.0f} vs {a_true:.0f} px)', b0 is None and b1 is not None and inter > 0.85)
for label, pic in (('a black photo-like blob (a filled dark area is never a boundary)', None),):
    pic = np.full((1100, 1400, 3), 255, np.uint8)
    cv2.circle(pic, (700, 550), 300, (20, 20, 20), -1)
    check(label + ': no boundary', TP.detect_boundary(pic, {}, k=8) is None)
switches(band_junctions=1, box_mask=1, dark_ring=1)
plain = TM.synthetic_dark_ring(5)[0].copy()
cv2.rectangle(plain, (450, 200), (1850, 1300), (255, 255, 255), -1)        # the same sheet with the thick outline painted out
for _i in range(10):
    p_, q_ = np.random.default_rng(_i).integers(0, [2000, 1546], 2), np.random.default_rng(_i + 40).integers(0, [2000, 1546], 2)
    cv2.line(plain, tuple(int(v) for v in p_), tuple(int(v) for v in q_), (30, 30, 30), 2, cv2.LINE_AA)
check('a black-and-white sheet with only thin lines, text and frames: still no boundary', TP.detect_boundary(plain, {}, k=8) is None)
check('the gate constants are unchanged', TP.MAX_FIT_M == 50.0 and TP.MIN_POINTS == 3 and TP.LINE_MIN_Z == 2.0 and TP.CHANCE_RATIO == 1.5
      and TP.CHANCE_MARGIN == 2.0 and TP.PIN_MAX_OUTSIDE_M == 1000)
if stand_in: print('NOTE stand-ins used for: ' + ', '.join(stand_in) + ' (the workflow installs the real ones)')
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
