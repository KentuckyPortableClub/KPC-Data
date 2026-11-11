#!/usr/bin/env python3
"""LINE AGREEMENT for the picture-map tracer (Nov 11 2026, KPC owner, 2026-11-11). numpy + OpenCV only.

The point matcher counts how many picture junctions land near basemap junctions. On grid towns and sparse rural maps a 90-degree
rotated basemap often scores the same (the 'not better than chance' NO FITs). This adds the second half of the evidence: under a
candidate transform, how much of the basemap's ROAD and WATER LINES, drawn back on the picture, sit on lines the picture really has.
A true fit puts the roads and shorelines on the drawn roads and shorelines along their whole length; a rotated decoy only crosses them.

  mask  = the picture's line pixels (the LSD segments the junction detector already found), inside the search box
  dist  = distance from every pixel to the nearest picture line
  share = of the basemap line samples that fall inside the box, the part within NEAR_PX of a picture line
  base  = the part of the box within NEAR_PX of a picture line (what a random line would get)
  z     = (share - base) / sqrt(base * (1 - base) / n), with n = samples thinned to one per CELL_PX cell (about independent), capped

The score is measured the same way on the real basemap and on every rotated decoy, so the better-than-chance gate (ratio 1.5, margin
2.0) is applied unchanged to stronger evidence on both sides. It never moves a pin and never decides anything by itself.
Run `python3 kpc_trace_edges.py --selftest` (synthetic, offline)."""
import math
import sys

import cv2
import numpy as np

NEAR_PX = 4.0        # a basemap line sample counts as 'on a picture line' within this many picture pixels
CELL_PX = 10.0       # thinning cell: at most one sample per 10 x 10 px (neighbouring samples are not independent)
N_CAP = 150          # at most this many thinned samples count (bounds z near 48; the tracer weights it, KPC_TRACE_LINE_WEIGHT)
MIN_SAMPLES = 25     # fewer thinned samples inside the box: no line evidence (z = 0)
LINE_KINDS = ("road", "stream", "water", "shore")   # what picture maps draw; PLSS section lines are not drawn on them


def line_mask(shape, segs, roi=None, exclude=None, thick=2):
    """uint8 mask (255 = picture line) from LSD segments [x1, y1, x2, y2], limited to the roi box, minus excluded boxes (legends)."""
    h, w = shape[:2]
    m = np.zeros((h, w), np.uint8)
    for x1, y1, x2, y2 in np.asarray(segs, float).reshape(-1, 4):
        cv2.line(m, (int(round(x1)), int(round(y1))), (int(round(x2)), int(round(y2))), 255, thick)
    box = np.zeros((h, w), bool)
    if roi is None:
        box[:] = True
    else:
        x0, y0, x1, y1 = [int(round(v)) for v in roi]
        box[max(0, y0):max(0, min(h, y1)), max(0, x0):max(0, min(w, x1))] = True
    for x0, y0, x1, y1 in exclude or []:
        box[max(0, int(y0)):max(0, int(y1)), max(0, int(x0)):max(0, int(x1))] = False
    m[~box] = 0
    return m, box


class LineEvidence:
    """Built once per picture; score(z, t, lines_m) for any similarity m = z * p + t (p = x - i*y, image px, y up; m metres)."""

    def __init__(self, shape, segs, roi=None, exclude=None):
        self.h, self.w = shape[:2]
        mask, self.box = line_mask(shape, segs, roi, exclude)
        self.dist = cv2.distanceTransform(255 - mask, cv2.DIST_L2, 3)
        inside = self.box.sum()
        self.base = float(((self.dist <= NEAR_PX) & self.box).sum()) / inside if inside else 0.0

    def score(self, z, t, samples_m):
        """(share, z_score, n_thinned) of metric line samples (N, 2) under the transform. No samples / no lines -> (0, 0, n)."""
        S = np.asarray(samples_m, float)
        if len(S) == 0 or z == 0 or not (0.0 < self.base < 1.0):
            return 0.0, 0.0, 0
        p = (S[:, 0] + 1j * S[:, 1] - t) / z
        x, y = p.real, -p.imag
        ok = (x >= 0) & (x < self.w - 1) & (y >= 0) & (y < self.h - 1)
        x, y = x[ok], y[ok]
        xi, yi = x.astype(np.int64), y.astype(np.int64)
        inb = self.box[yi, xi]
        xi, yi = xi[inb], yi[inb]
        if len(xi) == 0:
            return 0.0, 0.0, 0
        cell = (yi // int(CELL_PX)) * (self.w // int(CELL_PX) + 1) + (xi // int(CELL_PX))
        _, first = np.unique(cell, return_index=True)
        if len(first) > N_CAP:
            first = first[np.linspace(0, len(first) - 1, N_CAP).astype(np.int64)]
        n = len(first)
        if n < MIN_SAMPLES:
            return 0.0, 0.0, n
        share = float((self.dist[yi[first], xi[first]] <= NEAR_PX).mean())
        zsc = (share - self.base) / math.sqrt(self.base * (1.0 - self.base) / n)
        return share, float(zsc), n


def sample_lines(lines_m, step_m):
    """Points every step_m metres along metric polylines [[(x, y), ...], ...] -> (N, 2)."""
    out = []
    for ln in lines_m:
        a = np.asarray(ln, float)
        if len(a) < 2:
            continue
        seg = np.diff(a, axis=0)
        L = np.hypot(seg[:, 0], seg[:, 1])
        for (x0, y0), (dx, dy), l in zip(a[:-1], seg, L):
            k = max(1, int(l // step_m))
            s = np.arange(k) / k
            out.append(np.c_[x0 + s * dx, y0 + s * dy])
        out.append(a[-1:])
    return np.vstack(out) if out else np.zeros((0, 2))


def clip_lines(lines_m, half_m):
    """Keep only the runs of each polyline whose vertices lie within the box |x|, |y| <= half_m (metres about the pin); a big lake
    or a long river is not sampled along its whole length. A run that leaves the box is split there."""
    out = []
    for ln in lines_m:
        a = np.asarray(ln, float)
        if len(a) < 2:
            continue
        inb = (np.abs(a[:, 0]) <= half_m) & (np.abs(a[:, 1]) <= half_m)
        if inb.all():
            out.append(a); continue
        idx = np.nonzero(inb)[0]
        if len(idx) < 2:
            continue
        for run in np.split(idx, np.nonzero(np.diff(idx) > 1)[0] + 1):
            if len(run) >= 2:
                out.append(a[run])
    return out


def rotate(samples_m, deg):
    """The same samples rotated about the pin (0, 0): the decoy basemap's lines."""
    r = np.exp(1j * math.radians(deg)) * (samples_m[:, 0] + 1j * samples_m[:, 1])
    return np.c_[r.real, r.imag]


# ------------------------------------------------------------------------------------------------------------- selftest
def _synthetic(seed=0):
    """A rural-ish road net + a lake shore in metres, drawn on a 'picture' at 5 m/px rotated 12 degrees, with clutter."""
    rng = np.random.default_rng(seed)
    lines = []
    for _ in range(9):   # winding roads
        x, y = rng.uniform(-1500, 1500, 2); a = rng.uniform(0, 2 * np.pi); pts = [(x, y)]
        for _ in range(25):
            a += rng.normal(0, 0.25); x += 60 * np.cos(a); y += 60 * np.sin(a); pts.append((x, y))
        lines.append(pts)
    th = np.linspace(0, 2 * np.pi, 120)   # lake shore
    r = 380 + 70 * np.sin(3 * th) + 40 * np.cos(5 * th)
    lines.append(list(zip(250 + r * np.cos(th), -300 + r * np.sin(th))))
    z = 5.0 * np.exp(1j * np.radians(12.0)); t = 30 - 20j          # image -> metres
    w = h = 900
    img = np.full((h, w, 3), 255, np.uint8)
    segs = []
    for ln in lines:
        a = np.asarray(ln); p = (a[:, 0] + 1j * a[:, 1] - t) / z
        q = np.c_[p.real, -p.imag]
        for (x1, y1), (x2, y2) in zip(q[:-1], q[1:]):
            segs.append([x1 + rng.normal(0, 1), y1 + rng.normal(0, 1), x2 + rng.normal(0, 1), y2 + rng.normal(0, 1)])
    for _ in range(120):   # clutter: text, symbols, a frame
        x, y = rng.uniform(0, w, 2); a = rng.uniform(0, np.pi); L = rng.uniform(5, 40)
        segs.append([x, y, x + L * np.cos(a), y + L * np.sin(a)])
    segs += [[5, 5, w - 5, 5], [w - 5, 5, w - 5, h - 5], [w - 5, h - 5, 5, h - 5], [5, h - 5, 5, 5]]
    return img, np.array(segs), lines, z, t


def selftest():
    ok = True

    def check(msg, cond):
        nonlocal ok
        ok &= bool(cond)
        print(("PASS " if cond else "FAIL ") + msg)

    img, segs, lines, z, t = _synthetic()
    ev = LineEvidence(img.shape, segs, roi=(20, 20, 880, 880))
    S = sample_lines(lines, 10.0)
    sh, zs, n = ev.score(z, t, S)
    check(f"true transform: most basemap line samples sit on picture lines (share {sh:.2f}, base {ev.base:.2f}, z {zs:.1f}, n {n})",
          sh > 0.85 and zs > 10 and n >= MIN_SAMPLES)
    worst = max(ev.score(z, t, rotate(S, d))[1] for d in (90, 180, 270))
    check(f"rotated decoys score far lower (best decoy z {worst:.1f} vs true {zs:.1f})", worst < zs / 3)
    off = ev.score(z, t + 60 + 40j, S)[1]
    check(f"a transform 70 m off (14 px) loses most of the evidence (z {off:.1f})", off < zs / 2)
    scl = ev.score(z * 1.15, t, S)[1]
    check(f"a 15% scale error loses most of the evidence (z {scl:.1f})", scl < zs / 2)
    check("no samples -> no evidence", ev.score(z, t, np.zeros((0, 2))) == (0.0, 0.0, 0))
    far = ev.score(z, t + 1e6, S)
    check("lines entirely outside the picture -> no evidence", far[1] == 0.0)
    few = ev.score(z, t, S[:3])
    check("fewer than MIN_SAMPLES thinned samples -> z 0 (no claim)", few[1] == 0.0)
    ev2 = LineEvidence(img.shape, np.zeros((0, 4)))
    check("a picture with no lines -> no evidence (base 0)", ev2.score(z, t, S) == (0.0, 0.0, 0))
    big = [[(-1e5, 0.0), (0.0, 0.0), (10.0, 5.0), (1e5, 0.0)], [(5e4, 5e4), (6e4, 6e4)]]
    cl = clip_lines(big, 2000.0)
    check("clip_lines keeps only the in-box run of a long line and drops a line outside the box",
          len(cl) == 1 and len(cl[0]) == 2 and abs(cl[0][:, 0]).max() <= 2000.0)
    ex = LineEvidence(img.shape, segs, roi=(20, 20, 880, 880), exclude=[(0, 0, 900, 900)])
    check("an excluded legend box removes its lines from the evidence", ex.score(z, t, S)[2] == 0)
    zs_n = [ev.score(z, t, S)[2]] + [LineEvidence(*(_synthetic(s)[0].shape,), _synthetic(s)[1]).score(*_synthetic(s)[3:5], sample_lines(_synthetic(s)[2], 10.0))[2] for s in (1, 2)]
    check(f"the thinned sample count is capped at {N_CAP}, so z is bounded (about 48 at most; the tracer weights it 0.25): {zs_n}", max(zs_n) <= N_CAP)
    stable = [round(_s, 6) for _s in ev.score(z, t, S)[:2]] == [round(_s, 6) for _s in ev.score(z, t, S)[:2]]
    check("deterministic: the same inputs give the same score", stable)
    print("ALL PASS" if ok else "SOME FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    print(__doc__)
