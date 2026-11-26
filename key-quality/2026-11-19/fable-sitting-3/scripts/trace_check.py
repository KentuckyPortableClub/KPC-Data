import json, sys, math
sys.path.insert(0, '/home/claude/work/scripts'); import measure as M
import numpy as np
from PIL import Image, ImageDraw
ref, st = sys.argv[1], sys.argv[2]
t = json.load(open(f'/home/claude/work/to/key-quality/2026-11-19/t1/run-44542262740/traces/{ref}.json'))
g = t['features'][0]['geometry']; polys = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
recs = M.load(st, '/home/claude/work/cache'); key = json.load(open(f'/home/claude/work/newkeys/US-{st}.json'))['parks'][ref]
ids = [str(x[0]) for x in key['m']]
orr = [r for i in ids for r in M.rings_of(recs[i])]
pts = [p for r in orr for p in r] + [p for pg in polys for r in pg for p in r]
lo0, lo1 = min(p[0] for p in pts), max(p[0] for p in pts); la0, la1 = min(p[1] for p in pts), max(p[1] for p in pts)
k = math.cos(math.radians((la0+la1)/2)); mx, my = 111320*k, 110574; cell = max((lo1-lo0)*mx, (la1-la0)*my)/1400
w, h = int((lo1-lo0)*mx/cell)+3, int((la1-la0)*my/cell)+3
px = lambda p: ((p[0]-lo0)*mx/cell+1, (la1-p[1])*my/cell+1)
def mask(rings):
    m = np.zeros((h, w), bool)
    for r in rings:
        im = Image.new('1', (w, h), 0); ImageDraw.Draw(im).polygon([px(p) for p in r], fill=1); m ^= np.asarray(im, bool)
    return m
off = np.zeros((h, w), bool)
for i in ids: off |= mask(M.rings_of(recs[i]))
tr = np.zeros((h, w), bool)
for pg in polys: tr |= mask(pg)
A = lambda m: m.sum()*cell*cell/M.M2_AC
print(f"{ref}: traced {A(tr):,.1f} ac | official outline {A(off):,.1f} ac | ratio {A(tr)/A(off):.3f} | covered {A(tr&off)/A(off):.3f} | share of the trace outside {A(tr&~off)/A(tr):.3f} | official rows {len(ids)} | props {dict(list(t['features'][0]['properties'].items())[:6])}")
img = np.full((h, w, 3), 255, np.uint8)
img[off & ~tr] = (60, 120, 200); img[tr & ~off] = (220, 80, 60); img[tr & off] = (120, 170, 110)
Image.fromarray(img).save(f'/home/claude/work/trace-{ref}.png')
