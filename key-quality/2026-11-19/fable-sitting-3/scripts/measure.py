"""Raster measure of a park's joined records from the saved shapes (no shapely here).
Even-odd per record (holes), union across records. Local equal-area approx (equirectangular at mid-latitude)."""
import json, gzip, math, sys
import numpy as np
from PIL import Image, ImageDraw
M2_AC = 4046.8564224
def load(st, cache): return {str(a['OBJECTID']): a for a in json.load(gzip.open(f'{cache}/US-{st}.json.gz'))['recs']}
def rings_of(a): return [r for r in (a.get('_r') or []) if len(r) > 2]
def measure(ids, recs, cell=None, maxpx=7000, want_masks=False):
    rr = {i: rings_of(recs[i]) for i in ids if i in recs}
    pts = [p for rs in rr.values() for r in rs for p in r]
    if not pts: return None
    lo0, lo1 = min(p[0] for p in pts), max(p[0] for p in pts); la0, la1 = min(p[1] for p in pts), max(p[1] for p in pts)
    k = math.cos(math.radians((la0 + la1) / 2)); mx, my = 111320.0 * k, 110574.0
    W, H = (lo1 - lo0) * mx, (la1 - la0) * my
    if cell is None: cell = max(10.0, max(W, H) / maxpx)
    w, h = int(W / cell) + 3, int(H / cell) + 3
    def px(p): return ((p[0] - lo0) * mx / cell + 1, (la1 - p[1]) * my / cell + 1)
    union = np.zeros((h, w), bool); out = {}; masks = {}
    for i, rs in rr.items():
        m = np.zeros((h, w), bool)
        for r in rs:
            im = Image.new('1', (w, h), 0); ImageDraw.Draw(im).polygon([px(p) for p in r], fill=1)
            m ^= np.asarray(im, bool)
        out[i] = m.sum() * cell * cell / M2_AC
        union |= m
        if want_masks: masks[i] = m
    return {'cell': cell, 'bbox': (lo0, la0, lo1, la1), 'union_ac': union.sum() * cell * cell / M2_AC, 'rec_ac': out,
            'union': union, 'masks': masks, 'px': px, 'wh': (w, h), 'missing': [i for i in ids if i not in recs]}
