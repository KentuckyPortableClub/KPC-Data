#!/usr/bin/env python3
"""Picture tracer: picture marks the LSD junction finder misses or is misled by (KPC owner, 2026-11-11). numpy + OpenCV only.

1. band_junctions(): road junctions of roads DRAWN AS BANDS (a white / grey / coloured strip 5 px or wider, the way campground, day-use and
   many park maps draw roads). LSD sees only the two edges of a band; at a junction the edges bend round in a curve and never cross,
   so the junction itself is never found (Johnson Lake CA-6283 and Deer Creek CA-5612 in the Nov 11 run: the junctions found sat on
   icons and labels, not on one road junction). Here a junction is a point inside a band from which 3 or more arms of the same colour
   leave in different directions and go on (checked on two circles and along each arm), the centre of the band crossing.
2. boxes(): axis-aligned rectangles on the picture: legend, title, inset and photo boxes, and the small icon boxes (P, toilet, ...).
   Every crossing of a letter or a symbol in them is a 'junction' with nothing under it on the ground; they used up the 70 junction
   places on campground maps. junction_exclusions() keeps the boxes the park outline does not run through.
3. dark_ring_mask(): a thick BLACK or dark-grey closed boundary line (New Brunswick protected-area maps draw the boundary this way). The
   colour pick skips every grey (text, roads), so such a boundary was never a candidate. Only strokes clearly thicker than text and
   road lines survive (an opening), and the caller (detect_boundary) accepts it only as a closed ring that is not a rectangle, and only
   when no colour gave a boundary at all.
   (A fourth idea, a thin saturated outline over an aerial photo, was tried on the 32 NO LINE maps of the Nov 11 run: it found no
   real boundary and one wrong one, a trail loop, so it was left out.)
Each part has a switch (kpc_trace_limits.DEFAULTS, also --off on the tracer's command line). None of them is a gate: what they find still
has to pass every gate unchanged (3 points, RMS and leave-one-out under 50 m, better than the rotated decoy, line z, pin, size).
  python3 kpc_trace_marks.py --selftest
"""
import math
import sys

import cv2
import numpy as np


def _cluster_masks(img, k=8, seed=0):
    """Colour masks from OpenCV k-means in Lab (a sample of pixels, then every pixel to its nearest centre)."""
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
    pix = lab.reshape(-1, 3)
    rng = np.random.default_rng(seed)
    idx = rng.choice(len(pix), size=min(40000, len(pix)), replace=False)
    crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.5)
    cv2.setRNGSeed(seed)
    _c, _l, centers = cv2.kmeans(pix[idx], k, None, crit, 3, cv2.KMEANS_PP_CENTERS)
    d = ((pix[:, None, :] - centers[None, :, :]) ** 2).sum(2)
    labels = d.argmin(1).reshape(img.shape[:2])
    return [(labels == c).astype(np.uint8) for c in range(len(centers))], centers


def _circle(cx, cy, r, n):
    a = np.linspace(0, 2 * np.pi, n, endpoint=False)
    return cx[:, None] + r[:, None] * np.cos(a)[None, :], cy[:, None] + r[:, None] * np.sin(a)[None, :], a


def _runs(v):
    """Cyclic runs of 1 in each row of a 0/1 array: (count, list of (start, length))."""
    out = []
    for row in v:
        if row.all() or not row.any():
            out.append([])
            continue
        k = int(np.argmin(row))                       # start the walk on a 0
        r = np.roll(row, -k)
        runs, i, n = [], 0, len(r)
        while i < n:
            if r[i]:
                j = i
                while j < n and r[j]:
                    j += 1
                runs.append(((i + k) % n, j - i))
                i = j
            else:
                i += 1
        out.append(runs)
    return out


def band_junctions(img, roi=None, k=8, min_hw=2.5, max_hw_frac=0.012, masks=None):
    """Junctions of band-drawn roads. Returns (points (n, 2) in picture px, arms (n,), half widths (n,))."""
    return band_marks(img, roi, k, min_hw, max_hw_frac, masks)[:3]


def band_marks(img, roi=None, k=8, min_hw=2.5, max_hw_frac=0.012, masks=None):
    """Junctions of band-drawn roads AND the bands' middle lines as short segments [x1, y1, x2, y2] (for the line agreement: LSD finds only
    a band's two edges, half a band width away from where the basemap's road line falls). Returns (points, arms, half widths, segs)."""
    h, w = img.shape[:2]
    diag = math.hypot(w, h)
    max_hw = max(min_hw + 1.0, max_hw_frac * diag)
    if masks is None:
        masks, _ = _cluster_masks(img, k)
    pts, arms, hws, ridge = [], [], [], []
    for m in masks:
        if m.mean() > 0.6 or m.mean() < 0.002:        # the page background, or almost nothing
            continue
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        # bridge thin lines drawn OVER a road band (the park outline, a trail, a leader line): they cut the band's arms apart
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)))
        dt = cv2.distanceTransform(m, cv2.DIST_L2, 5)
        cand = (dt >= min_hw) & (dt <= max_hw)
        if roi is not None:
            x0, y0, x1, y1 = [int(round(v)) for v in roi]
            box = np.zeros_like(cand)
            box[max(0, y0):max(0, y1), max(0, x0):max(0, x1)] = True
            cand &= box
        # local maxima of the distance (the band's middle line), at most one per 6 x 6 px cell
        mx = cv2.dilate(dt, np.ones((5, 5), np.uint8))
        cand &= dt >= mx - 1e-6
        ys, xs = np.nonzero(cand)
        if len(xs) == 0:
            continue
        cell = (ys // 6) * (w // 6 + 1) + xs // 6
        order = np.lexsort((-dt[ys, xs], cell))
        first = np.r_[True, cell[order][1:] != cell[order][:-1]]
        ys, xs = ys[order][first], xs[order][first]
        r0 = dt[ys, xs].astype(float)
        ok = np.ones(len(xs), bool)
        nar = None
        for f, fmin in ((2.2, 7.0), (3.6, 13.0)):      # two circles: the arms must go on, not stop at a blob edge or a letter
            R = np.maximum(fmin, f * r0)
            cx_, cy_, _a = _circle(xs.astype(float), ys.astype(float), R, 72)
            inside = (cx_ >= 0) & (cx_ < w) & (cy_ >= 0) & (cy_ < h)
            v = np.zeros(cx_.shape, np.uint8)
            v[inside] = m[cy_[inside].astype(int), cx_[inside].astype(int)]
            frac = v.mean(1)
            runs = _runs(v)
            lmin = 2 if nar is None else 1            # an arm: 10 (5 on the outer circle: a narrow site spur) to 150 degrees of the circle
            n_arm = np.array([sum(1 for _s, L in rr if lmin <= L <= 30) for rr in runs])
            if nar is None:                            # the band's middle line: 2 or more arms on the first circle, not inside a blob
                rid = (n_arm >= 2) & (frac < 0.55) & inside.all(1)
                if rid.sum() >= 2:
                    RP = np.c_[xs[rid], ys[rid]].astype(float)
                    for c0 in range(0, len(RP), 1500):           # neighbours on the middle line (cells are 6 px), in chunks
                        d2 = ((RP[c0:c0 + 1500, None, :] - RP[None, :, :]) ** 2).sum(2)
                        aa, bb = np.nonzero(d2 <= 81.0)
                        aa = aa + c0
                        sel_ = bb > aa
                        ridge.extend(np.c_[RP[aa[sel_]], RP[bb[sel_]]].tolist())
            ok &= (n_arm >= 3) & (frac < 0.55) & inside.all(1)
            nar = n_arm if nar is None else np.minimum(nar, n_arm)
        if not ok.any():
            continue
        # each arm must be the band itself running out from the centre (not a separate stroke the circle happens to cut)
        sel = np.nonzero(ok)[0]
        good = []
        for i in sel:
            R = max(13.0, 3.6 * r0[i])
            cx_, cy_, a = _circle(np.array([xs[i]], float), np.array([ys[i]], float), np.array([R]), 72)
            v = m[np.clip(cy_[0].astype(int), 0, h - 1), np.clip(cx_[0].astype(int), 0, w - 1)].astype(np.uint8)[None, :]
            n_conn = 0
            for s, L in _runs(v)[0]:
                if not 1 <= L <= 30:
                    continue
                ang = a[(s + L // 2) % 72]
                t = np.linspace(0.0, R, 14)
                px = np.clip((xs[i] + t * math.cos(ang)).astype(int), 0, w - 1)
                py = np.clip((ys[i] + t * math.sin(ang)).astype(int), 0, h - 1)
                # a road arm: the ray stays in the band, and the band keeps a road's even width along it (its middle is neither a
                # blob opening up, as between letters on a white margin, nor a ragged texture, as in drawn tree cover)
                arm_dt = dt[py[5:], px[5:]]
                if m[py, px].all() and arm_dt.min() >= 0.6 * min_hw and arm_dt.max() <= 1.3 * r0[i] \
                        and arm_dt.max() <= 2.2 * max(arm_dt.min(), 1.0):
                    n_conn += 1
            if n_conn >= 3:
                good.append((i, n_conn))
        for i, n_conn in good:
            pts.append((float(xs[i]), float(ys[i])))
            arms.append(n_conn)
            hws.append(float(r0[i]))
    R = np.array(ridge, float).reshape(-1, 4)
    if not pts:
        return np.zeros((0, 2)), np.zeros(0, int), np.zeros(0), R
    P, A, H = np.array(pts), np.array(arms), np.array(hws)
    # one point per junction: merge detections closer than 2.5 half widths (strongest first)
    order = np.lexsort((-H, -A))
    keep = []
    for o in order:
        if all(math.hypot(*(P[o] - P[j])) > max(6.0, 2.5 * max(H[o], H[j])) for j in keep):
            keep.append(o)
    return P[keep], A[keep], H[keep], R


def boxes(img, min_side=14, max_frac=0.45):
    """Axis-aligned rectangles (x0, y0, x1, y1) drawn on the picture: frames of legends, titles, insets, photos and icon boxes."""
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 40, 120)
    edges = cv2.dilate(edges, np.ones((3, 3), np.uint8))
    cnts, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    out = []
    for c in cnts:
        x, y, bw, bh = cv2.boundingRect(c)
        if bw < min_side or bh < min_side or bw * bh > max_frac * w * h:
            continue
        area = cv2.contourArea(c)
        if area < 0.85 * bw * bh:
            continue
        ap = cv2.approxPolyDP(c, 0.03 * cv2.arcLength(c, True), True)
        if len(ap) > 6:
            continue
        out.append((float(x), float(y), float(x + bw), float(y + bh)))
    # drop boxes inside a bigger kept box only when they are the same box (inner / outer edge of one frame line)
    out.sort(key=lambda b: -(b[2] - b[0]) * (b[3] - b[1]))
    kept = []
    for b in out:
        if not any(abs(b[0] - k[0]) < 6 and abs(b[1] - k[1]) < 6 and abs(b[2] - k[2]) < 6 and abs(b[3] - k[3]) < 6 for k in kept):
            kept.append(b)
    return kept


def junction_exclusions(img, outline_px):
    """The boxes to ignore junctions in: every rectangle the park outline does not run through (fewer than 3% of its points inside)."""
    P = np.asarray(outline_px, float).reshape(-1, 2) if outline_px is not None and len(outline_px) else np.zeros((0, 2))
    out = []
    for x0, y0, x1, y1 in boxes(img):
        if len(P):
            inside = ((P[:, 0] >= x0) & (P[:, 0] <= x1) & (P[:, 1] >= y0) & (P[:, 1] <= y1)).mean()
            if inside >= 0.03:
                continue          # the park itself is drawn in it (the map frame, or a park that fills an inset)
        out.append((x0, y0, x1, y1))
    return out


def dark_ring_mask(img, min_stroke_frac=0.0016):
    """Pixels of dark strokes clearly thicker than text and road lines (an opening the size of min_stroke_frac x the diagonal)."""
    h, w = img.shape[:2]
    diag = math.hypot(w, h)
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
    chroma = np.hypot(lab[..., 1] - 128, lab[..., 2] - 128)
    dark = ((lab[..., 0] < 90) & (chroma < 20)).astype(np.uint8) * 255
    ks = max(3, int(round(min_stroke_frac * diag)))
    return cv2.morphologyEx(dark, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (ks, ks)))


# ------------------------------------------------------------------ synthetic pictures for the checks
def synthetic_campground(seed=0, w=1400, h=1100, band=16, roads_as='band', grid=(4, 3), with_lines=False):
    """A park map drawn the campground way: olive ground, white road bands with T and X junctions, a lake, icon boxes, a legend box
    full of symbols and text, site numbers, and a magenta park outline. Returns (img, true junctions (n, 2) px, outline px)."""
    rng = np.random.default_rng(seed)
    img = np.full((h, w, 3), (140, 170, 150), np.uint8)
    cv2.ellipse(img, (int(w * 0.75), int(h * 0.85)), (260, 120), 10, 0, 360, (225, 190, 130), -1)
    nodes = {}
    gx, gy = grid
    xs = [int(w * (0.12 + 0.62 * i / (gx - 1))) for i in range(gx)]
    ys = [int(h * (0.18 + 0.58 * j / (gy - 1))) for j in range(gy)]
    for i, x in enumerate(xs):
        for j, y in enumerate(ys):
            nodes[(i, j)] = (x + int(rng.integers(-25, 26)), y + int(rng.integers(-25, 26)))
    edges = [((i, j), (i + 1, j)) for i in range(gx - 1) for j in range(gy)] + [((i, j), (i, j + 1)) for i in range(gx) for j in range(gy - 1)]
    drop = set(int(x) for x in rng.choice(len(edges), 2, replace=False))
    edges = [e for n, e in enumerate(edges) if n not in drop]
    deg = {}
    for a_, b_ in edges:
        deg[a_] = deg.get(a_, 0) + 1
        deg[b_] = deg.get(b_, 0) + 1
    for a_, b_ in edges:
        if roads_as == 'band':
            cv2.line(img, nodes[a_], nodes[b_], (70, 80, 75), band + 4, cv2.LINE_AA)
    for a_, b_ in edges:
        if roads_as == 'band':
            cv2.line(img, nodes[a_], nodes[b_], (245, 245, 245), band, cv2.LINE_AA)
        else:
            cv2.line(img, nodes[a_], nodes[b_], (40, 40, 40), 2, cv2.LINE_AA)
    true = [nodes[n] for n, d in deg.items() if d >= 3]
    # site loops (dead-end spurs: each is a real T junction on the picture) and site numbers in circles
    for _ in range(14):
        a_, b_ = edges[int(rng.integers(len(edges)))]
        t = rng.uniform(0.2, 0.8)
        p = (np.array(nodes[a_]) * (1 - t) + np.array(nodes[b_]) * t).astype(int)
        dv = np.array(nodes[b_], float) - np.array(nodes[a_], float)
        nv = np.array([-dv[1], dv[0]]) / max(np.hypot(*dv), 1.0) * rng.choice([-1, 1])
        ang = rng.uniform(-0.35, 0.35)
        nv = np.array([nv[0] * math.cos(ang) - nv[1] * math.sin(ang), nv[0] * math.sin(ang) + nv[1] * math.cos(ang)])
        q = (p + nv * rng.uniform(55, 75)).astype(int)
        cv2.line(img, tuple(int(v) for v in p), tuple(int(v) for v in q), (245, 245, 245), 7, cv2.LINE_AA)
        true.append(tuple(int(v) for v in p))
        cv2.circle(img, tuple(int(v) for v in q), 13, (40, 40, 200), -1, cv2.LINE_AA)
        cv2.putText(img, str(int(rng.integers(1, 40))), (int(q[0]) - 9, int(q[1]) + 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
    true = np.array(true, float)
    # icon boxes on the map
    for _ in range(16):
        x, y = int(rng.integers(60, w - 300)), int(rng.integers(60, h - 60))
        cv2.rectangle(img, (x, y), (x + 30, y + 30), (110, 60, 20), -1)
        cv2.putText(img, 'PS'[int(rng.integers(2))], (x + 6, y + 24), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.line(img, (x + 4, y + 26), (x + 26, y + 4), (255, 255, 255), 2)
    # legend box with symbols and text
    lx, ly = w - 280, 30
    cv2.rectangle(img, (lx, ly), (w - 20, ly + 420), (255, 255, 255), -1)
    cv2.rectangle(img, (lx, ly), (w - 20, ly + 420), (30, 30, 30), 3)
    for r in range(12):
        y = ly + 30 + r * 32
        cv2.rectangle(img, (lx + 12, y - 12), (lx + 36, y + 12), (110, 60, 20), -1)
        cv2.line(img, (lx + 14, y + 10), (lx + 34, y - 10), (255, 255, 255), 2)
        cv2.line(img, (lx + 14, y - 10), (lx + 34, y + 10), (255, 255, 255), 2)
        cv2.putText(img, 'XKTEHF'[r % 6] * 3 + ' site', (lx + 48, y + 7), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (20, 20, 20), 2, cv2.LINE_AA)
    # the park outline (closed, irregular) in magenta
    c = np.array([w * 0.43, h * 0.48])
    th = np.linspace(0, 2 * np.pi, 60, endpoint=False)
    rr = 380 + 50 * np.sin(3 * th + seed) + rng.normal(0, 8, len(th))
    outline = np.c_[c[0] + rr * np.cos(th) * 1.15, c[1] + rr * np.sin(th) * 0.95]
    cv2.polylines(img, [outline.astype(np.int32)], True, (200, 0, 220), 4, cv2.LINE_AA)
    if with_lines:
        return img, true, outline, [[nodes[a_], nodes[b_]] for a_, b_ in edges]
    return img, true, outline


def synthetic_dark_ring(seed=0, w=2000, h=1546, ring_px=10, two_lobes=False):
    """A black-and-white protected-area sheet: thin black roads and streams, black labels, a black frame and legend box, and the area
    outlined with a THICK black line. Returns (img, outline px)."""
    rng = np.random.default_rng(seed)
    img = np.full((h, w, 3), 255, np.uint8)
    for _ in range(14):
        p, q = rng.integers(0, [w, h], 2), rng.integers(0, [w, h], 2)
        cv2.line(img, tuple(int(v) for v in p), tuple(int(v) for v in q), (30, 30, 30), 2, cv2.LINE_AA)
    for _ in range(25):
        x, y = int(rng.integers(20, w - 200)), int(rng.integers(30, h - 20))
        cv2.putText(img, 'BROOK RD', (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.rectangle(img, (8, 8), (w - 8, h - 8), (0, 0, 0), 10)
    cv2.rectangle(img, (40, h - 360), (600, h - 40), (0, 0, 0), 4)
    c = np.array([w * 0.55, h * 0.42])
    th = np.linspace(0, 2 * np.pi, 48, endpoint=False)
    f = w / 1400.0
    rr = f * (260 + 70 * np.sin(2 * th + seed) + rng.normal(0, 10, len(th)))
    outline = np.c_[c[0] + rr * np.cos(th), c[1] + rr * np.sin(th) * 0.8]
    if two_lobes:   # two parcels drawn as two rings that touch (Stony Brook, CA-4522): the closed shape encloses two holes
        rr = f * (170 + rng.normal(0, 8, len(th)))
        a_ = np.c_[c[0] - 170 * f + rr * np.cos(th), c[1] + rr * np.sin(th) * 0.8]
        b_ = np.c_[c[0] + 170 * f + rr * np.cos(th), c[1] + 30 * f + rr * np.sin(th) * 0.8]
        mk = np.zeros((h, w), np.uint8)
        for o in (a_, b_):
            cv2.polylines(img, [o.astype(np.int32)], True, (0, 0, 0), ring_px, cv2.LINE_AA)
            cv2.fillPoly(mk, [o.astype(np.int32)], 1)
        cs, _ = cv2.findContours(mk, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        return img, max(cs, key=cv2.contourArea).reshape(-1, 2).astype(float)
    cv2.polylines(img, [outline.astype(np.int32)], True, (0, 0, 0), ring_px, cv2.LINE_AA)
    return img, outline


def _near(P, T, tol):
    if len(P) == 0 or len(T) == 0:
        return 0
    d = np.hypot(P[:, None, 0] - T[None, :, 0], P[:, None, 1] - T[None, :, 1])
    return int((d.min(0) <= tol).sum())


def selftest():
    ok = True

    def check(msg, c):
        nonlocal ok
        ok &= bool(c)
        print(('PASS ' if c else 'FAIL ') + msg)
    img, true, outline = synthetic_campground(1)
    nodes = true[:-14]                          # the road-network junctions (the rest are the site spurs' T junctions)
    P, A, H = band_junctions(img)
    B = junction_exclusions(img, outline)
    inbox = lambda p: any(b[0] <= p[0] <= b[2] and b[1] <= p[1] <= b[3] for b in B)
    hit = _near(P, nodes, 10.0)
    hit_all = _near(P, true, 12.0)
    check(f'band roads: {hit} of {len(nodes)} road-network junctions found within 10 px ({len(P)} points; an icon or the outline drawn '
          f'right over a junction may hide it)', hit >= 0.6 * len(nodes))
    check(f'band roads: {hit_all} of {len(true)} picture junctions (with the site spurs) found within 12 px', hit_all >= 0.5 * len(true))
    far = [p for p in P if np.hypot(*(true - p).T).min() > 25 and not inbox(p)]
    check(f'band roads: after the box exclusion, at most 3 points away from a picture junction ({len(far)})', len(far) <= 3)
    img2, true2, _ = synthetic_campground(1, roads_as='line')
    P2, _, _ = band_junctions(img2)
    check(f'thin-line roads: no band junction claimed at the road junctions ({_near(P2, true2[:-14], 10.0)}); LSD handles those as before',
          _near(P2, true2[:-14], 10.0) <= 1)
    legend = [b for b in B if b[2] - b[0] > 200]
    icons = [b for b in B if b[2] - b[0] < 60]
    check(f'boxes: the legend box and the icon boxes are found ({len(legend)} legend, {len(icons)} icons)', len(legend) >= 1 and len(icons) >= 10)
    inb = [t for t in true if inbox(t)]
    check(f'boxes: no road junction falls in an excluded box ({len(inb)})', len(inb) == 0)
    dimg, doutline = synthetic_dark_ring(2)
    m = dark_ring_mask(dimg) > 0
    ring = np.zeros(m.shape, np.uint8)
    cv2.polylines(ring, [doutline.astype(np.int32)], True, 1, 5)
    away = np.ones(m.shape, np.uint8)
    cv2.polylines(away, [doutline.astype(np.int32)], True, 0, 31)
    away[:30, :] = away[-30:, :] = 0
    away[:, :30] = away[:, -30:] = 0
    cv2.rectangle(away, (25, dimg.shape[0] - 375), (615, dimg.shape[0] - 25), 0, -1)
    check(f'dark ring: the thick ring is kept ({100 * m[ring > 0].mean():.0f}% of it)', m[ring > 0].mean() > 0.9)
    check(f'dark ring: thin roads and text are opened away ({100 * m[away > 0].mean():.2f}% of the rest of the page)', m[away > 0].mean() < 0.04)
    print('ALL PASS' if ok else 'SOME FAILED')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(selftest() if '--selftest' in sys.argv else 0)
