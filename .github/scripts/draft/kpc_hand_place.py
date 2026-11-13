#!/usr/bin/env python3
"""HAND PLACER CHECKER (Nov 11 2026, KPC owner, 2026-11-11). OFFLINE: no request of any kind.

A person places a park's saved picture map BY HAND on the members' page kpc-map-placer.html (KPC-Links): matching spots clicked in
pairs (picture <-> USGS map), then the boundary or trail traced on the picture. The page saves a "click set" JSON. This script:

  1. re-computes everything from the click set's point pairs and traced shape (it never trusts the numbers the page wrote, and
     refuses a click set whose own numbers do not match its points);
  2. re-applies the picture tracer's gates with the tracer's OWN constants and functions (kpc_trace_picture.py, kpc_trace_limits.py,
     kpc_trace_edges.py are imported, no number is copied), plus the hand-point gates below;
  3. checks the picture's sha256 and pixel size, the index row (agency, source, page, banned map sites) and the POTA pin (pins.json:
     the click set's pin must BE the POTA pin; a pin is never moved);
  4. writes the trace in exactly the format of an accepted automatic picture trace (traced/<ref>.json), plus `via: "hand points"` and
     the whole click set inside it (`hand.click_set`, with its sha256), so Quality can re-check any placement; and a report.csv row
     in the tracer's own columns. A refused click set writes no trace and says why, one line per failed gate.

  python3 kpc_hand_place.py <click-set.json> --base <fixtures> --out <folder> [--picture FILE] [--basemap FILE]
  python3 kpc_hand_place.py --check <trace.json ...> --base <fixtures> [--picture FILE] [--basemap FILE]   (Quality's re-check;
          exit 1 on any difference)
  python3 kpc_hand_place.py --fers-entry <trace.json>     (the data/fers-approx-outlines.json entry, printed, for after grading)
  python3 kpc_hand_place.py --selftest

<fixtures> is the tracer's own input folder after .github/scripts/kpc_picture_prep.py (index.json, pins.json, maps/). Exit codes:
0 placed / re-check identical, 2 refused (gates), 1 re-check found a difference or the input is broken.

Gates that cannot apply to hand points as they are (they test whether a MACHINE's match beats chance) are replaced by stricter
geometry gates: 4+ pairs, leave-one-out RMS AND worst single point under the tracer's 50 m, points not on one line, points that span
the traced shape, no far extrapolation, not mirrored, not stretched, a sane scale, every real-map point clicked on a government map.
When the tracer's saved basemap for the park is given (--basemap, the tracer's cache/<ref>_basemap.json), the tracer's own line
agreement is scored for the hand fit and must pass LINE_MIN_Z and beat the rotated decoys by the same ratio / margin.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib
import json
import math
import re
import sys
import types
from pathlib import Path

__version__ = "1.0"
HERE = Path(__file__).resolve().parent
FORMAT = "kpc-click-set 1"

# ---------------------------------------------------------------- the tracer's own modules (constants + gate functions)
_STUBBED = []


def _placeholder(name):
    """A stand-in for a heavy module the checker never calls (shapely / pyproj / sklearn / requests when not installed): it only lets
    `import kpc_trace_picture` run for its constants and pure helpers. Calling anything from it raises."""
    m = types.ModuleType(name)

    def _missing(*_a, **_k):
        raise RuntimeError(f"{name} is not installed here; kpc_hand_place.py does not need it")

    class _Missing:
        def __init__(self, *a, **k): _missing()
    m.__getattr__ = lambda attr: _Missing if attr[:1].isupper() else _missing   # noqa: E731
    m.__path__ = []
    return m


def _import_tracer():
    sys.path.insert(0, str(HERE))
    heavy = ["shapely", "shapely.geometry", "shapely.validation", "shapely.ops", "pyproj", "sklearn", "sklearn.cluster",
             "sklearn.neighbors", "requests", "cv2"]
    for name in heavy:
        if name in sys.modules:
            continue
        try:
            importlib.import_module(name)
        except ImportError:
            sys.modules[name] = _placeholder(name)
            _STUBBED.append(name)
    import kpc_trace_picture as tp   # noqa: E402
    import kpc_trace_limits as tl    # noqa: E402
    try:
        import kpc_trace_edges as le  # noqa: E402  (numpy + OpenCV)
    except Exception:  # noqa: BLE001
        le = None
    return tp, tl, le


TP, TL, LE = _import_tracer()
HAVE_CV2 = "cv2" not in _STUBBED

# The tracer's gate constants, imported (never copied).
MAX_FIT_M, MIN_POINTS, PIN_MAX_OUTSIDE_M, SIMPLIFY_M = TP.MAX_FIT_M, TP.MIN_POINTS, TP.PIN_MAX_OUTSIDE_M, TP.SIMPLIFY_M
CHANCE_RATIO, CHANCE_MARGIN, LINE_MIN_Z = TP.CHANCE_RATIO, TP.CHANCE_MARGIN, TP.LINE_MIN_Z
SCALE_RANGE, SKEW_MAX = TL.GEOPDF_SCALE_RANGE, TL.GEOPDF_SKEW_MAX

# Hand-point gates (new; the owner may tune each, one line).
HAND_MIN_POINTS = 4          # one more than the tracer's 3: every point can then be left out and checked by the others
HAND_COLLINEAR_MIN = 0.15    # smallest / largest spread of the picture points (the tracer only FLAGS < 0.08 as nearly collinear)
HAND_SPREAD_MIN = 0.5        # the points' box must be at least half the traced shape's size (diagonal)
HAND_EXTRAP_MAX = 0.5        # no part of the shape further outside the points' box than half the points' spread
HAND_ROT_FLAG_DEG = 25.0     # the tracer's --rot-max default; a hand fit turned more than this is FLAGGED (not refused)
PIN_SAME_DEG = 1e-6          # the click set's pin must be the POTA pin to within this (about 0.1 m)
PAGE_TOL_M = 0.01            # the page's own numbers must match the re-computation to within this
# The real-map layers a point may be clicked on (the page's list, kpc-map-placer-math.js BASEMAPS): government maps only (Rule 6).
BASEMAPS = {
    "usgs-topo": ("USGS The National Map: Topo", "https://basemap.nationalmap.gov/arcgis/rest/services/USGSTopo/MapServer/tile/{z}/{y}/{x}"),
    "usgs-imagery-topo": ("USGS The National Map: Imagery Topo",
                          "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryTopo/MapServer/tile/{z}/{y}/{x}"),
}
WDPA_RX = re.compile(r"wdpa|protected.?planet|unep-?wcmc|world_database_of_protected", re.I)
ACRE_M2 = 4046.86
RAW_PICTURE = "https://raw.githubusercontent.com/KentuckyPortableClub/KPC-Data/picture-maps/"

# ---------------------------------------------------------------- the maths (mirror of kpc-map-placer-math.js; same order of sums)
_A, _F = 6378137.0, 1 / 298.257222101
_N = _F / (2 - _F)
_E = math.sqrt(_F * (2 - _F))
_n = [_N ** k for k in range(7)]
_AA = _A / (1 + _N) * (1 + _n[2] / 4 + _n[4] / 64 + _n[6] / 256)
_ALPHA = [0,
          _n[1] / 2 - 2 * _n[2] / 3 + 5 * _n[3] / 16 + 41 * _n[4] / 180 - 127 * _n[5] / 288 + 7891 * _n[6] / 37800,
          13 * _n[2] / 48 - 3 * _n[3] / 5 + 557 * _n[4] / 1440 + 281 * _n[5] / 630 - 1983433 * _n[6] / 1935360,
          61 * _n[3] / 240 - 103 * _n[4] / 140 + 15061 * _n[5] / 26880 + 167603 * _n[6] / 181440,
          49561 * _n[4] / 161280 - 179 * _n[5] / 168 + 6601661 * _n[6] / 7257600,
          34729 * _n[5] / 80640 - 3418889 * _n[6] / 1995840,
          212378941 * _n[6] / 319334400]
_BETA = [0,
         _n[1] / 2 - 2 * _n[2] / 3 + 37 * _n[3] / 96 - _n[4] / 360 - 81 * _n[5] / 512 + 96199 * _n[6] / 604800,
         _n[2] / 48 + _n[3] / 15 - 437 * _n[4] / 1440 + 46 * _n[5] / 105 - 1118711 * _n[6] / 3870720,
         17 * _n[3] / 480 - 37 * _n[4] / 840 - 209 * _n[5] / 4480 + 5569 * _n[6] / 90720,
         4397 * _n[4] / 161280 - 11 * _n[5] / 504 - 830251 * _n[6] / 7257600,
         4583 * _n[5] / 161280 - 108847 * _n[6] / 3991680,
         20648693 * _n[6] / 638668800]


def _xi_eta(lat, dlon):
    phi, lam = math.radians(lat), math.radians(dlon)
    s = math.sin(phi)
    t = math.sinh(math.atanh(s) - _E * math.atanh(_E * s))
    xi1, eta1 = math.atan2(t, math.cos(lam)), math.atanh(math.sin(lam) / math.sqrt(1 + t * t))
    xi, eta = xi1, eta1
    for j in range(1, 7):
        xi += _ALPHA[j] * math.sin(2 * j * xi1) * math.cosh(2 * j * eta1)
        eta += _ALPHA[j] * math.cos(2 * j * xi1) * math.sinh(2 * j * eta1)
    return xi, eta


def tm_fwd(lat0, lon0, lat, lon):
    """lat, lon -> (east, north) metres, transverse Mercator centred on (lat0, lon0), GRS80, k0 = 1 (the tracer's LocalProj)."""
    o, p = _xi_eta(lat0, 0.0), _xi_eta(lat, lon - lon0)
    return _AA * p[1], _AA * (p[0] - o[0])


def tm_inv(lat0, lon0, x, y):
    o = _xi_eta(lat0, 0.0)
    xi, eta = y / _AA + o[0], x / _AA
    xi1, eta1 = xi, eta
    for j in range(1, 7):
        xi1 -= _BETA[j] * math.sin(2 * j * xi) * math.cosh(2 * j * eta)
        eta1 -= _BETA[j] * math.cos(2 * j * xi) * math.sinh(2 * j * eta)
    tau1 = math.sin(xi1) / math.sqrt(math.sinh(eta1) ** 2 + math.cos(xi1) ** 2)
    lam, tau = math.atan2(math.sinh(eta1), math.cos(xi1)), tau1
    e2 = _E * _E
    for _ in range(8):
        sig = math.sinh(_E * math.atanh(_E * tau / math.sqrt(1 + tau * tau)))
        t1 = tau * math.sqrt(1 + sig * sig) - sig * math.sqrt(1 + tau * tau)
        dt = (tau1 - t1) / math.sqrt(1 + t1 * t1) * (1 + (1 - e2) * tau * tau) / ((1 - e2) * math.sqrt(1 + tau * tau))
        tau += dt
        if abs(dt) < 1e-15:
            break
    return math.degrees(math.atan(tau)), lon0 + math.degrees(lam)


def fit_similarity(P, Q):
    """The tracer's fit_similarity_c in plain floats: m = z * p + t, p = x - i*y. -> (a, b, tx, ty) or None."""
    k = len(P)
    if k < 2 or len(Q) != k:
        return None
    pr = sum(p[0] for p in P) / k
    pi = sum(-p[1] for p in P) / k
    qr = sum(q[0] for q in Q) / k
    qi = sum(q[1] for q in Q) / k
    den = nr = ni = 0.0
    for p, q in zip(P, Q):
        ar, ai, br, bi = p[0] - pr, -p[1] - pi, q[0] - qr, q[1] - qi
        den += ar * ar + ai * ai
        nr += ar * br + ai * bi
        ni += ar * bi - ai * br
    if not den > 0:
        return None
    a, b = nr / den, ni / den
    return a, b, qr - (a * pr - b * pi), qi - (a * pi + b * pr)


def apply_sim(T, x, y):
    a, b, tx, ty = T
    return a * x - b * (-y) + tx, a * (-y) + b * x + ty


def fit_affine(P, Q):
    k = len(P)
    if k < 3:
        return None
    mx = sum(p[0] for p in P) / k
    my = sum(-p[1] for p in P) / k
    me = sum(q[0] for q in Q) / k
    mn = sum(q[1] for q in Q) / k
    sxx = sxy = syy = sxe = sye = sxn = syn = 0.0
    for p, q in zip(P, Q):
        x, y, e, n = p[0] - mx, -p[1] - my, q[0] - me, q[1] - mn
        sxx += x * x; sxy += x * y; syy += y * y; sxe += x * e; sye += y * e; sxn += x * n; syn += y * n   # noqa: E702
    det = sxx * syy - sxy * sxy
    if not abs(det) > 1e-9 * max(1.0, sxx * syy):
        return None
    a11, a12 = (syy * sxe - sxy * sye) / det, (sxx * sye - sxy * sxe) / det
    a21, a22 = (syy * sxn - sxy * syn) / det, (sxx * syn - sxy * sxn) / det
    dA = a11 * a22 - a12 * a21
    s = a11 * a11 + a12 * a12 + a21 * a21 + a22 * a22
    q = math.sqrt(max(0.0, s * s - 4 * dA * dA))
    s1, s2 = math.sqrt((s + q) / 2), math.sqrt(max(0.0, (s - q) / 2))
    return dict(A=[[a11, a12], [a21, a22]], det=dA, s1=s1, s2=s2, stretch=(s1 - s2) / s1 if s1 > 0 else 1.0)


def spread_ratio(P):
    k = len(P)
    if k < 2:
        return 0.0
    mx, my = sum(p[0] for p in P) / k, sum(p[1] for p in P) / k
    a = b = c = 0.0
    for p in P:
        x, y = p[0] - mx, p[1] - my
        a += x * x; b += x * y; c += y * y   # noqa: E702
    tr, q = a + c, math.sqrt(max(0.0, (a - c) ** 2 + 4 * b * b))
    l1, l2 = (tr + q) / 2, max(0.0, (tr - q) / 2)
    return math.sqrt(l2 / l1) if l1 > 0 else 0.0


def fit_pairs(pairs, pin):
    P = [(float(q["px"][0]), float(q["px"][1])) for q in pairs]
    Q = [tm_fwd(pin[0], pin[1], float(q["ll"][0]), float(q["ll"][1])) for q in pairs]
    T = fit_similarity(P, Q)
    if T is None:
        return None
    res = []
    for p, q in zip(P, Q):
        m = apply_sim(T, *p)
        res.append(math.hypot(m[0] - q[0], m[1] - q[1]))
    rms = math.sqrt(sum(r * r for r in res) / len(res))
    loo = None
    if len(P) >= 3:
        loo = []
        for i in range(len(P)):
            T2 = fit_similarity([p for j, p in enumerate(P) if j != i], [q for j, q in enumerate(Q) if j != i])
            if T2 is None:
                loo.append(math.inf)
                continue
            m = apply_sim(T2, *P[i])
            loo.append(math.hypot(m[0] - Q[i][0], m[1] - Q[i][1]))
    return dict(T=T, P=P, Q=Q, residuals=res, rms=rms, loo=loo,
                loo_rms=math.sqrt(sum(r * r for r in loo) / len(loo)) if loo else None, loo_max=max(loo) if loo else None,
                scale=math.hypot(T[0], T[1]), rotation_deg=math.degrees(math.atan2(T[1], T[0])),
                affine=fit_affine(P, Q), spread=spread_ratio(P))


def _o(p, q, r):
    v = (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    return 0 if abs(v) < 1e-12 else (1 if v > 0 else -1)


def _on(p, q, r):
    return (min(p[0], r[0]) - 1e-12 <= q[0] <= max(p[0], r[0]) + 1e-12) and (min(p[1], r[1]) - 1e-12 <= q[1] <= max(p[1], r[1]) + 1e-12)


def _seg_x(a, b, c, d):
    o1, o2, o3, o4 = _o(a, b, c), _o(a, b, d), _o(c, d, a), _o(c, d, b)
    if o1 != o2 and o3 != o4:
        return True
    return (o1 == 0 and _on(a, c, b)) or (o2 == 0 and _on(a, d, b)) or (o3 == 0 and _on(c, a, d)) or (o4 == 0 and _on(c, b, d))


def self_crosses(pts, closed):
    k = len(pts)
    m = k if closed else k - 1
    for i in range(m):
        for j in range(i + 1, m):
            if j == i + 1 or (closed and i == 0 and j == m - 1):
                continue
            if _seg_x(pts[i], pts[(i + 1) % k], pts[j], pts[(j + 1) % k]):
                return True
    return False


def _seg_dist(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = dx * dx + dy * dy
    t = ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L if L > 0 else 0.0
    t = max(0.0, min(1.0, t))
    return math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy)


def simplify(pts, tol, closed):
    """Douglas-Peucker at the tracer's SIMPLIFY_M (a closed ring keeps its first vertex). Same steps as the page's module."""
    line = list(pts) + [pts[0]] if closed else list(pts)
    if len(line) < 3:
        return list(pts)
    keep = [False] * len(line)
    keep[0] = keep[-1] = True
    stack = [(0, len(line) - 1)]
    while stack:
        s0, s1 = stack.pop()
        best, bi = -1.0, -1
        for i in range(s0 + 1, s1):
            d = _seg_dist(line[i], line[s0], line[s1])
            if d > best:
                best, bi = d, i
        if best > tol:
            keep[bi] = True
            stack.append((s0, bi))
            stack.append((bi, s1))
    out = [p for p, k in zip(line, keep) if k]
    if closed:
        out.pop()
    return list(pts) if (closed and len(out) < 3) or len(out) < 2 else out


def _inside(p, ring):
    c, j = False, len(ring) - 1
    for i in range(len(ring)):
        a, b = ring[i], ring[j]
        if (a[1] > p[1]) != (b[1] > p[1]) and p[0] < (b[0] - a[0]) * (p[1] - a[1]) / (b[1] - a[1]) + a[0]:
            c = not c
        j = i
    return c


def _shoelace(ring):
    s, j = 0.0, len(ring) - 1
    for i in range(len(ring)):
        s += (ring[j][0] + ring[i][0]) * (ring[j][1] - ring[i][1])
        j = i
    return abs(s) / 2


def pin_distance(M, closed):
    if closed and _inside((0.0, 0.0), M):
        return 0.0
    k = len(M)
    m = k if closed else k - 1
    return min(_seg_dist((0.0, 0.0), M[i], M[(i + 1) % k]) for i in range(m))


def place_shape(T, pin, shape_px, kind):
    closed = kind == "area"
    M0 = [apply_sim(T, float(p[0]), float(p[1])) for p in shape_px]
    M = simplify(M0, SIMPLIFY_M, closed)
    ll = []
    for m in M:
        la, lo = tm_inv(pin[0], pin[1], m[0], m[1])
        ll.append([round(lo, 7), round(la, 7)])
    if closed:
        ll.append(list(ll[0]))
    n = len(M)
    length = sum(math.hypot(M[(i + 1) % n][0] - M[i][0], M[(i + 1) % n][1] - M[i][1]) for i in range(n - (0 if closed else 1)))
    return dict(metres=M, lonlat=ll, area_acres=_shoelace(M) / ACRE_M2 if closed else None, length_km=None if closed else length / 1000.0,
                pin_dist_m=pin_distance(M, closed), crosses=self_crosses(M, closed), n_in=len(M0), n_out=len(M))


def _bbox(P):
    return [min(p[0] for p in P), min(p[1] for p in P), max(p[0] for p in P), max(p[1] for p in P)]


def _dist_box(p, b):
    return math.hypot(max(b[0] - p[0], 0.0, p[0] - b[2]), max(b[1] - p[1], 0.0, p[1] - b[3]))


def canonical(v):
    """Sorted keys, no spaces: the bytes the click set's sha256 is taken over (the page uses the same rule)."""
    return json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def sha256_text(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------- the gates
def hand_gates(fit, shape, layers, pin):
    """The page's gates, re-done here (ids and order as kpc-map-placer-math.js gates()). -> [{id, pass, why}]"""
    out = []

    def g(i, ok, why):
        out.append(dict(id=i, **{"pass": bool(ok)}, why=why))
    n = len(fit["P"]) if fit else 0
    g("points", n >= HAND_MIN_POINTS and n >= MIN_POINTS, f"{n} point pair(s); hand placements need at least {HAND_MIN_POINTS}")
    if not fit:
        return out
    g("fit", fit["rms"] < MAX_FIT_M, f"fit error (RMS) {fit['rms']:.1f} m; must be under {MAX_FIT_M:g} m")
    lr, lm = fit["loo_rms"], fit["loo_max"]
    g("leave_one_out", lr is not None and lr < MAX_FIT_M,
      f"leave-one-out error (RMS) {'n/a' if lr is None else f'{lr:.1f} m'}; must be under {MAX_FIT_M:g} m")
    g("leave_one_out_worst", lm is not None and lm < MAX_FIT_M,
      f"worst single point left out misses by {'n/a' if lm is None else f'{lm:.1f} m'}; must be under {MAX_FIT_M:g} m")
    g("not_on_a_line", fit["spread"] >= HAND_COLLINEAR_MIN,
      f"the points spread {fit['spread']:.2f} across their line (need {HAND_COLLINEAR_MIN:g}): points nearly on one line cannot fix the turn")
    af = fit["affine"]
    g("not_mirrored", bool(af) and af["det"] > 0,
      ("the points keep the picture the right way round" if af["det"] > 0 else
       "the points only fit a MIRRORED picture: a pair is swapped or wrong") if af else "cannot check: points on a line")
    g("not_stretched", bool(af) and af["stretch"] <= SKEW_MAX,
      f"the points stretch the picture {100 * af['stretch']:.1f}% one way more than the other (limit {100 * SKEW_MAX:g}%)" if af
      else "cannot check: points on a line")
    g("scale", SCALE_RANGE[0] <= fit["scale"] <= SCALE_RANGE[1],
      f"scale {fit['scale']:.3f} m per picture pixel (plausible {SCALE_RANGE[0]:g} to {SCALE_RANGE[1]:g})")
    bad = [x for x in layers if x not in BASEMAPS]
    g("government_basemap", len(layers) == n and not bad,
      f"{len(bad)} point(s) were clicked on a map that is not a government basemap" if bad else "every point was clicked on a USGS map")
    if shape and shape.get("px"):
        sb, pb = _bbox(shape["px"]), _bbox(fit["P"])
        sd, pd = math.hypot(sb[2] - sb[0], sb[3] - sb[1]), math.hypot(pb[2] - pb[0], pb[3] - pb[1])
        worst = max(_dist_box(p, pb) for p in shape["px"])
        g("points_cover_shape", sd > 0 and pd / sd >= HAND_SPREAD_MIN,
          f"the points span {(100 * pd / sd if sd > 0 else 0):.0f}% of the traced shape’s size (need {100 * HAND_SPREAD_MIN:g}%)")
        g("no_far_extrapolation", pd > 0 and worst <= HAND_EXTRAP_MAX * pd,
          f"the shape reaches {(100 * worst / pd if pd > 0 else math.inf):.0f}% of the points’ spread beyond them (limit {100 * HAND_EXTRAP_MAX:g}%)")
        need = 3 if shape["kind"] == "area" else 2
        pl = place_shape(fit["T"], pin, shape["px"], shape["kind"])
        g("shape", len(shape["px"]) >= need and not pl["crosses"],
          f"trace at least {need} corners" if len(shape["px"]) < need else
          (f"the traced {'outline' if shape['kind'] == 'area' else 'line'} crosses itself" if pl["crosses"] else "traced shape is clean"))
        g("pin", pl["pin_dist_m"] <= PIN_MAX_OUTSIDE_M,
          "the POTA pin is inside the outline" if pl["pin_dist_m"] == 0 else
          f"the POTA pin is {pl['pin_dist_m']:.0f} m from the traced shape (limit {PIN_MAX_OUTSIDE_M} m)")
    return out


def line_evidence(fit, picture_path, basemap_path, row, shape_px, kind):
    """The tracer's line agreement for the HAND fit (kpc_trace_edges.LineEvidence.score with the hand z, t) on the tracer's saved
    basemap, against the same basemap turned 90 / 180 / 270 degrees about the pin. -> dict (evaluated False when it cannot run)."""
    if not basemap_path:
        return dict(evaluated=False, why="no saved basemap for this park was given (--basemap): line agreement not scored")
    if LE is None or not HAVE_CV2 or "sklearn.cluster" in _STUBBED:
        return dict(evaluated=False, why="OpenCV / scikit-learn / kpc_trace_edges not available here: line agreement not scored")
    import numpy as np
    import cv2
    raw = Path(basemap_path).read_bytes()
    bm = json.loads(raw)
    pin = bm.get("pin")
    img = cv2.imread(str(picture_path), cv2.IMREAD_COLOR)
    if img is None:
        return dict(evaluated=False, why="picture could not be read for the line agreement")
    xs, ys = [p[0] for p in shape_px], [p[1] for p in shape_px]
    bx, by, bw, bh = min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)
    roi = (bx - 1.0 * bw, by - 1.0 * bh, bx + 2.0 * bw, by + 2.0 * bh) if kind == "area" else None   # the tracer's search box
    if row.get("roi_px"):
        roi = tuple(row["roi_px"])
    # the tracer's own picture lines: LSD segments, plus the middle lines of roads drawn as bands when its band switch is on
    _p, _w, segs = TP.detect_junctions(img, max_points=70, exclude=row.get("exclude_px"), roi=roi)
    ev = LE.LineEvidence(img.shape, segs, roi=roi, exclude=row.get("exclude_px"))
    lm = []
    for kind_, ln in bm.get("lines") or []:
        if kind_ in LE.LINE_KINDS and len(ln) >= 2:
            lm.append(np.array([tm_fwd(pin[0], pin[1], float(q[1]), float(q[0])) for q in ln], float))
    lm = LE.clip_lines(lm, 1.2 * float(bm.get("half_km") or 5.0) * 1000.0)
    a, b, tx, ty = fit["T"]
    z, t = complex(a, b), complex(tx, ty)
    LS = LE.sample_lines(lm, max(1.0, fit["scale"] * LE.CELL_PX / 2.0)) if lm else np.zeros((0, 2))
    share, lz, ln_ = ev.score(z, t, LS)
    decoys = [ev.score(z, t, LE.rotate(LS, ang))[1] if len(LS) else 0.0 for ang in (90, 180, 270)]
    dz = max(decoys)
    out = dict(evaluated=True, basemap_sha256=hashlib.sha256(raw).hexdigest(), line_share=round(share, 3), line_z=round(lz, 2),
               n_samples=int(ln_), decoy_line_z=round(dz, 2), min_samples=LE.MIN_SAMPLES)
    if ln_ < LE.MIN_SAMPLES:
        out["why"] = f"only {ln_} basemap line samples inside the box (the tracer needs {LE.MIN_SAMPLES}): no line evidence either way"
        out["gates"] = []
        return out
    out["gates"] = [
        dict(id="line_agreement", **{"pass": lz >= LINE_MIN_Z},
             why=f"the government roads / water sit on the picture's lines with z {lz:.1f} (need >= {LINE_MIN_Z:g})"),
        dict(id="line_better_than_chance", **{"pass": TL.better_than_chance(lz, dz, CHANCE_RATIO, CHANCE_MARGIN)},
             why=f"line z {lz:.1f} vs {dz:.1f} for the basemap turned 90/180/270 degrees (need {CHANCE_RATIO:g}x and +{CHANCE_MARGIN:g})")]
    return out


# ---------------------------------------------------------------- inputs
class Refused(Exception):
    pass


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def validate(cs):
    """Shape of the click set; raises Refused with the reason."""
    if not isinstance(cs, dict) or cs.get("format") != FORMAT:
        raise Refused(f"not a click set (format must be {FORMAT!r})")
    for k in ("ref", "park", "picture", "pairs", "shape", "fit", "date", "by"):
        if k not in cs:
            raise Refused(f"click set has no {k!r}")
    if not re.fullmatch(r"[A-Z]{1,3}-\d{4,5}", str(cs["ref"])):
        raise Refused(f"ref {cs['ref']!r} is not a POTA reference")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(cs["date"])):
        raise Refused("date must be YYYY-MM-DD")
    pin = (cs.get("park") or {}).get("pin")
    if not (isinstance(pin, list) and len(pin) == 2 and all(_num(v) for v in pin)):
        raise Refused("park.pin must be [lat, lon]")
    for i, q in enumerate(cs["pairs"] or []):
        if not (isinstance(q, dict) and isinstance(q.get("px"), list) and isinstance(q.get("ll"), list) and len(q["px"]) == 2
                and len(q["ll"]) == 2 and all(_num(v) for v in q["px"] + q["ll"])):
            raise Refused(f"pair {i + 1} must have px [x, y] and ll [lat, lon]")
        if not (-90 <= q["ll"][0] <= 90 and -180 <= q["ll"][1] <= 180):
            raise Refused(f"pair {i + 1}: lat / lon out of range")
    sh = cs["shape"] or {}
    if sh.get("kind") not in ("area", "trail") or not isinstance(sh.get("px"), list) or not all(
            isinstance(p, list) and len(p) == 2 and all(_num(v) for v in p) for p in sh["px"]):
        raise Refused("shape must be {kind: 'area' | 'trail', px: [[x, y], ...]}")
    pic = cs["picture"] or {}
    if not re.fullmatch(r"[0-9a-f]{64}", str(pic.get("sha256") or "")):
        raise Refused("picture.sha256 missing")
    if not (_num(pic.get("width")) and _num(pic.get("height"))):
        raise Refused("picture.width / height missing")
    if WDPA_RX.search(canonical(cs)):
        raise Refused("WDPA / Protected Planet material is never used for outlines or 2-fers (house rule): click set refused")


def _same(a, b, tol):
    return a is not None and b is not None and abs(float(a) - float(b)) <= tol


def page_numbers_match(cs, fit):
    """The click set carries the page's own fit; it must be what its points give (an edited transform or error is refused)."""
    f = cs.get("fit") or {}
    z, t = f.get("z") or [None, None], f.get("t") or [None, None]
    a, b, tx, ty = fit["T"]
    why = []
    if f.get("model") != "similarity":
        why.append(f"page model {f.get('model')!r} (the hand placer fits a similarity)")
    if not (_same(z[0], a, 1e-9 * max(1.0, abs(a)) + 1e-12) and _same(z[1], b, 1e-9 * max(1.0, abs(b)) + 1e-12)):
        why.append("the page's scale / turn does not match its points")
    if not (_same(t[0], tx, PAGE_TOL_M) and _same(t[1], ty, PAGE_TOL_M)):
        why.append("the page's shift does not match its points")
    if not _same(f.get("rms_m"), fit["rms"], PAGE_TOL_M):
        why.append("the page's fit error does not match its points")
    if fit["loo_rms"] is not None and not _same(f.get("loo_rms_m"), fit["loo_rms"], PAGE_TOL_M):
        why.append("the page's leave-one-out error does not match its points")
    return why


def load_base(base, ref):
    idx = TP.load_index(base)
    row, _skipped = TP.select_row(idx.get(ref))
    pins = json.loads((base / "pins.json").read_text()) if (base / "pins.json").exists() else {}
    return row, pins.get(ref)


def picture_file(row):
    mf = (row or {}).get("map_file") or (TL.chosen_image(row) if row else None)
    return f"maps/{mf}" if mf else None


def file_sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def picture_size(p):
    if HAVE_CV2:
        import cv2
        im = cv2.imread(str(p), cv2.IMREAD_UNCHANGED)
        if im is not None:
            return int(im.shape[1]), int(im.shape[0])
    return None


# ---------------------------------------------------------------- one placement
def place(cs, base, picture=None, basemap=None, need_picture=True):
    """-> (status, why list, trace FeatureCollection or None, report row dict, notes list). Never writes."""
    notes = []
    validate(cs)
    ref = cs["ref"]
    row, pin = load_base(Path(base), ref)
    report = dict(ref=ref, status="ERROR", fit_m="", n_points=0, why="", date=cs["date"], model="similarity")
    if row is None:
        raise Refused(f"{ref} is not in the tracer's index.json (run kpc_picture_prep.py first)")
    bad = TP.check_row(row)
    if bad:
        raise Refused(bad)
    if WDPA_RX.search(canonical(row)):
        raise Refused("the index row names WDPA / Protected Planet: refused")
    if pin is None:
        raise Refused("no POTA pin in pins.json")
    pin = [float(pin[0]), float(pin[1])]
    cpin = cs["park"]["pin"]
    if abs(cpin[0] - pin[0]) > PIN_SAME_DEG or abs(cpin[1] - pin[1]) > PIN_SAME_DEG:
        raise Refused(f"the click set's pin {cpin} is not the POTA pin {pin} (pins are never moved)")
    pic = cs["picture"]
    want_file = picture_file(row)
    if pic.get("file") != want_file:
        raise Refused(f"the click set's picture {pic.get('file')!r} is not the park's saved picture {want_file!r}")
    if str(pic.get("source_url") or "") != str(row.get("source_url") or "") or str(pic.get("page")) != str(row.get("page")):
        raise Refused("the click set's source address / page differ from the index row")
    ppath = Path(picture) if picture else (Path(base) / want_file)
    if ppath.exists():
        if file_sha256(ppath) != pic["sha256"]:
            raise Refused(f"wrong picture: {ppath.name} sha256 differs from the click set's (picture changed or another file)")
        sz = picture_size(ppath)
        if sz and sz != (int(pic["width"]), int(pic["height"])):
            raise Refused(f"picture size {sz[0]} x {sz[1]} px differs from the click set's {pic['width']} x {pic['height']}")
    elif need_picture:
        raise Refused(f"the picture {ppath} is not here: its sha256 must be checked before a trace is written")
    else:
        notes.append("picture not available here: its sha256 was not re-checked (the stored hash is unchanged)")
    W, H = float(pic["width"]), float(pic["height"])
    for i, q in enumerate(cs["pairs"]):
        if not (0 <= q["px"][0] <= W and 0 <= q["px"][1] <= H):
            raise Refused(f"pair {i + 1} is off the picture")
    for p in cs["shape"]["px"]:
        if not (0 <= p[0] <= W and 0 <= p[1] <= H):
            raise Refused("the traced shape leaves the picture")

    fit = fit_pairs(cs["pairs"], pin) if len(cs["pairs"]) >= 2 else None
    if fit:
        mism = page_numbers_match(cs, fit)
        if mism:
            raise Refused("the click set's numbers were edited or come from another tool: " + "; ".join(mism))
    shape = cs["shape"]
    layers = [q.get("layer") for q in cs["pairs"]]
    gates = hand_gates(fit, shape, layers, pin)
    report["n_points"] = len(cs["pairs"])
    if fit:
        report.update(fit_m=round(fit["rms"], 1), fit_loo_m="" if fit["loo_rms"] is None else round(fit["loo_rms"], 1))
    if not fit:
        lines = dict(evaluated=False, why="fewer than 2 point pairs: nothing to score")
    elif basemap and not ppath.exists():
        lines = dict(evaluated=False, why="picture not available: line agreement not scored")
    else:
        lines = line_evidence(fit, ppath, basemap, row, shape["px"], shape["kind"])
    gates += lines.get("gates") or []
    fails = [x for x in gates if not x["pass"]]
    flags = []
    held = []
    pl = None
    if fit and not any(x["id"] == "shape" and not x["pass"] for x in gates):
        pl = place_shape(fit["T"], pin, shape["px"], shape["kind"])
        edge = None
        if shape["kind"] == "area":
            b = 4
            if any(p[0] <= b or p[1] <= b or p[0] >= W - 1 - b or p[1] >= H - 1 - b for p in shape["px"]):
                edge = TL.edge_share([tuple(p) for p in shape["px"]], W, H)
        held = TL.hold_reasons(kind=shape["kind"], pin_dist_m=pl["pin_dist_m"], pin_max_m=PIN_MAX_OUTSIDE_M, edge=edge,
                               traced_acres=pl["area_acres"], known_acres=row.get("acres"), park_type=row.get("type"),
                               length_km=pl["length_km"])
        report.update(pin_dist_m=round(pl["pin_dist_m"]), acres_traced=round(pl["area_acres"], 1) if pl["area_acres"] is not None else "",
                      acres_known=row.get("acres") or "", ceiling_acres=int(TL.ceiling_acres(row.get("type"))),
                      edge_share=round(edge, 3) if edge is not None else "")
        gates.append(dict(id="tracer_holds", **{"pass": not held},
                          why="; ".join(held) if held else "pin, clipped edge and size: nothing to hold (kpc_trace_limits.hold_reasons)"))
    if fit and abs(fit["rotation_deg"]) > HAND_ROT_FLAG_DEG:
        flags.append(f"picture turned {fit['rotation_deg']:.0f} degrees from north-up (more than the automatic tracer searches)")
    if lines.get("evaluated") and lines.get("gates"):
        report.update(line_share=lines["line_share"], line_z=lines["line_z"], decoy_line_z=lines["decoy_line_z"])
    else:
        flags.append("line agreement not scored: " + lines.get("why", ""))
    fails = [x for x in gates if not x["pass"]]
    if fails:
        holds_only = all(x["id"] in ("tracer_holds", "pin") for x in fails)
        report.update(status="NEEDS A PERSON" if holds_only else "NO FIT", why="; ".join(x["why"] for x in fails), flags="; ".join(flags))
        return report["status"], [f"{x['id']}: {x['why']}" for x in fails], None, report, notes

    unoff = TP.source_type(row) == "unofficial"
    gname = sorted({BASEMAPS[x][0] for x in layers})
    flags.insert(0, f"placed by hand: {len(cs['pairs'])} point pairs clicked on {', '.join(gname)}; "
                    f"picture turned {fit['rotation_deg']:.1f} degrees, {fit['scale']:.3f} m per pixel")
    cps = [dict(px=[round(float(q["px"][0]), 1), round(float(q["px"][1]), 1)], lon=round(float(q["ll"][1]), 7), lat=round(float(q["ll"][0]), 7))
           for q in cs["pairs"]]
    kind_word = "boundary" if shape["kind"] == "area" else "route"
    props = dict(ref=ref, name=row.get("name"), agency=row.get("agency"),
                 grade=TP.GRADE_UNOFFICIAL if unoff else TP.GRADE,
                 status=TP.STATUS_UNOFFICIAL if unoff else "DRAWN", source_type=TP.source_type(row),
                 match_score=0.0, decoy_score=0.0,
                 fit_m=round(fit["rms"], 1), fit_loo_m=round(fit["loo_rms"], 1),
                 n_points=len(cs["pairs"]),
                 method=(f"{kind_word} traced by hand on the picture ({len(shape['px'])} corners); control points: {len(cs['pairs'])} pairs "
                         f"clicked by hand on the picture and on a government map ({', '.join(gname)}); similarity fit; "
                         f"Douglas-Peucker {SIMPLIFY_M:g} m"),
                 model="similarity", source_url=row.get("source_url"), page=row.get("page"),
                 basemap_sources=[f"{x} (points clicked by a person)" for x in gname], date=cs["date"],
                 area_acres=round(pl["area_acres"], 1) if pl["area_acres"] else None,
                 flags=flags, use_for_2fer=False, official=False,
                 control_points=cps, tool=f"kpc_hand_place.py {__version__} (tracer {TP.__version__})")
    if unoff:
        props.update(source_org=row.get("source_org"), notes=row.get("notes"),
                     replace_when="replace as soon as an official GIS layer, agency parcel or agency map is found")
    a, b, tx, ty = fit["T"]
    props["via"] = "hand points"
    props["hand"] = dict(
        click_set_sha256=sha256_text(canonical(cs)), click_set=copy.deepcopy(cs),
        checker=dict(version=__version__, tracer_version=TP.__version__,
                     transform=dict(model="similarity", z=[a, b], t=[tx, ty], frame="transverse Mercator on the POTA pin, GRS80",
                                    scale_m_per_px=round(fit["scale"], 6), rotation_deg=round(fit["rotation_deg"], 4)),
                     residuals_m=[round(r, 2) for r in fit["residuals"]], loo_m=[round(r, 2) for r in fit["loo"]],
                     loo_max_m=round(fit["loo_max"], 2), gates=gates, lines=lines))
    if shape["kind"] == "area":
        geom = dict(type="Polygon", coordinates=[pl["lonlat"]])
    else:
        geom = dict(type="LineString", coordinates=pl["lonlat"])
    fc = dict(type="FeatureCollection", features=[dict(type="Feature", properties=props, geometry=geom)])
    report.update(status=props["status"], why="placed by hand points: fit under 50 m, leave-one-out under 50 m, every hand gate passed"
                  + ("; " + "; ".join(flags) if flags else ""), flags="; ".join(flags), source_url=row.get("source_url"),
                  page=row.get("page"), source_type=props["source_type"], source_org=row.get("source_org", ""), notes=row.get("notes", ""))
    return props["status"], [], fc, report, notes


def dump_trace(fc):
    return json.dumps(fc, indent=1, ensure_ascii=False) + "\n"


def write_outputs(out, fc, report):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    ref = report["ref"]
    if fc is not None:
        TP.atomic_write(out / f"{TP.safe_name(ref)}.json", dump_trace(fc))
    rows = TP.read_report(out / "report.csv")
    rows[ref] = report
    TP.write_report(out / "report.csv", rows)


def check_trace(path, base, picture=None, basemap=None):
    """Quality's re-check: re-place the stored click set; the result must be the stored trace, byte for byte. -> list of problems."""
    probs = []
    stored = json.loads(Path(path).read_text(encoding="utf-8"))
    try:
        props = stored["features"][0]["properties"]
        cs = props["hand"]["click_set"]
    except (KeyError, IndexError, TypeError):
        return [f"{path}: not a hand-placed trace (no hand.click_set)"]
    if props.get("via") != "hand points":
        probs.append("via is not 'hand points'")
    if props["hand"].get("click_set_sha256") != sha256_text(canonical(cs)):
        probs.append("the stored click set does not match its sha256 (a point, the shape or a number was edited)")
    lines_used = (props["hand"].get("checker") or {}).get("lines", {}).get("evaluated")
    if lines_used and not basemap:
        probs.append("this trace was scored on a saved basemap; give the same file with --basemap to re-check it")
    try:
        status, why, fc, _rep, notes = place(cs, base, picture=picture, basemap=basemap, need_picture=False)
    except Refused as e:
        return probs + [f"the click set is refused now: {e}"]
    for n in notes:
        print(f"NOTE {n}")
    if fc is None:
        return probs + [f"the click set no longer passes ({status}): " + "; ".join(why)]
    if dump_trace(fc) != dump_trace(stored):
        new_p = fc["features"][0]["properties"]
        diff = sorted(k for k in set(new_p) | set(props) if new_p.get(k) != props.get(k))
        if fc["features"][0]["geometry"] != stored["features"][0]["geometry"]:
            diff.append("geometry")
        probs.append("the stored trace differs from a fresh placement of its own click set: " + ", ".join(diff or ["formatting"]))
    return probs


def fers_entry(trace, parkinfo_dir=None):
    """The data/fers-approx-outlines.json entry (KPC-Links) for a graded trace: the same fields an automatic picture trace's entry has
    (name, st, src, approx, rings), plus via. 'why' is written by the person who grades it, as today."""
    f = trace["features"][0]
    p, g = f["properties"], f["geometry"]
    if g["type"] == "Polygon":
        rings = [g["coordinates"][0]]
    elif g["type"] == "MultiPolygon":
        rings = [poly[0] for poly in g["coordinates"]]
    else:
        raise Refused("a trail line is not an outline: fers-approx-outlines.json holds areas only")
    if p.get("use_for_2fer") is not False or p.get("official") is not False or WDPA_RX.search(canonical(p.get("source_url") or "")):
        raise Refused("not an approximate picture trace")
    e = dict(name=p.get("name") or p["ref"], src="picture trace of an official map", approx=True, rings=rings)
    st = state_of(p["ref"], parkinfo_dir)
    if st:
        e["st"] = st
    if p.get("via"):
        e["via"] = p["via"]
    return e


def state_of(ref, parkinfo_dir=None):
    d = Path(parkinfo_dir) if parkinfo_dir else HERE.parents[2] / "data" / "parkinfo"
    if ref.startswith("CA-") and (d / "CA.json").exists():
        a = (json.loads((d / "CA.json").read_text()).get("parks") or {}).get(ref)
        return f"CA-{a[10]}" if a and len(a) > 10 else None
    for f in sorted(d.glob("US-*.json")):
        if ref in (json.loads(f.read_text()).get("parks") or {}):
            return f.stem
    return None


# ---------------------------------------------------------------- self test (synthetic, offline)
def selftest():
    ok = True

    def check(c, m):
        nonlocal ok
        print(("PASS " if c else "FAIL ") + m)
        ok = ok and bool(c)
    lat0, lon0 = 37.5, -84.3
    e, n = tm_fwd(lat0, lon0, 37.53, -84.25)
    la, lo = tm_inv(lat0, lon0, e, n)
    check(abs(la - 37.53) < 1e-11 and abs(lo + 84.25) < 1e-11, "transverse Mercator round trip")
    z, t = 2.5 * complex(math.cos(0.3), math.sin(0.3)), complex(-400.0, 250.0)
    P = [(100.0, 100.0), (900.0, 150.0), (500.0, 800.0), (150.0, 700.0), (820.0, 760.0)]
    Q = []
    for x, y in P:
        m = z * complex(x, -y) + t
        Q.append((m.real, m.imag))
    T = fit_similarity(P, Q)
    check(abs(T[0] - z.real) < 1e-12 and abs(T[1] - z.imag) < 1e-12 and abs(T[2] - t.real) < 1e-9, "exact similarity recovered")
    check(fit_affine(P, Q)["det"] > 0 and fit_affine([(x, -y) for x, y in P], Q)["det"] < 0, "mirror seen by the affine check")
    check(spread_ratio([(0, 0), (10, 0.1), (20, 0.05), (30, 0.0)]) < HAND_COLLINEAR_MIN, "points on a line seen")
    check(self_crosses([(0, 0), (10, 10), (10, 0), (0, 10)], True) and not self_crosses([(0, 0), (10, 0), (10, 10), (0, 10)], True),
          "a bow-tie crosses itself, a square does not")
    check(MAX_FIT_M == 50.0 and MIN_POINTS == 3 and PIN_MAX_OUTSIDE_M == 1000 and LINE_MIN_Z == 2.0, "the tracer's gate numbers are imported")
    print("ALL PASS" if ok else "SOME FAILED")
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("click_set", nargs="?", help="a click set JSON from kpc-map-placer.html")
    ap.add_argument("--base", help="the tracer's prepared input folder (index.json, pins.json, maps/)")
    ap.add_argument("--out", help="output folder for <ref>.json + report.csv (e.g. a tools-out checkout's picture-trace/hand)")
    ap.add_argument("--picture", help="the picture file, when it is not <base>/maps/<map_file>")
    ap.add_argument("--basemap", help="the tracer's saved basemap for this park (cache/<ref>_basemap.json): scores the line agreement")
    ap.add_argument("--check", nargs="+", metavar="TRACE", help="re-check stored hand traces from their own click sets")
    ap.add_argument("--fers-entry", metavar="TRACE", help="print the fers-approx-outlines.json entry for a graded trace")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if _STUBBED:
        print(f"NOTE not installed here (not needed by this checker): {', '.join(_STUBBED)}", file=sys.stderr)
    if a.selftest:
        return selftest()
    if a.fers_entry:
        print(json.dumps(fers_entry(json.loads(Path(a.fers_entry).read_text(encoding="utf-8"))), ensure_ascii=False))
        return 0
    if a.check:
        if not a.base:
            ap.error("--check needs --base")
        bad = 0
        for p in a.check:
            probs = check_trace(p, a.base, picture=a.picture, basemap=a.basemap)
            print(("OK   " if not probs else "FAIL ") + p + ("" if not probs else ": " + " | ".join(probs)))
            bad += bool(probs)
        print(f"{len(a.check) - bad} of {len(a.check)} hand trace(s) re-checked identical")
        return 1 if bad else 0
    if not (a.click_set and a.base and a.out):
        ap.error("give a click set, --base and --out (or --check / --fers-entry / --selftest)")
    try:
        cs = json.loads(Path(a.click_set).read_text(encoding="utf-8"))
        status, why, fc, report, notes = place(cs, a.base, picture=a.picture, basemap=a.basemap)
    except Refused as e:
        print(f"REFUSED {Path(a.click_set).name}: {e}")
        return 2
    except (OSError, ValueError, KeyError, TypeError) as e:
        print(f"REFUSED {Path(a.click_set).name}: unreadable click set ({type(e).__name__}: {e})")
        return 2
    write_outputs(a.out, fc, report)
    if fc is None:
        print(f"{status} {report['ref']}: no trace written")
        for w in why:
            print(f"  - {w}")
        return 2
    print(f"{status} {report['ref']}: {Path(a.out) / (TP.safe_name(report['ref']) + '.json')} (fit {report['fit_m']} m, "
          f"leave-one-out {report['fit_loo_m']} m, {report['n_points']} pairs)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
