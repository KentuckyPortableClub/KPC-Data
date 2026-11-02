"""Dev-only self-test: draw a fake 'picture map' from the cached government basemap at a
KNOWN scale/rotation/offset, then check the tracer recovers it (DRAWN) and that a
picture with no matching roads is refused (NO FIT). Not a deliverable."""
import json, math, shutil, subprocess, sys
from pathlib import Path
import numpy as np, cv2
sys.path.insert(0, '/workspace/kpc-tracer')
import kpc_trace_picture as K
root = Path('/workspace/kpc-tracer/dev/synth'); shutil.rmtree(root, ignore_errors=True)
(root / 'maps').mkdir(parents=True); (root / 'cache').mkdir()
bm = json.load(open('/workspace/kpc-tracer/test/cache/US-10172_basemap.json'))
lat, lon = bm['pin']; proj = K.LocalProj(lat, lon)
rng = np.random.default_rng(1)

def render(ref, scale, rot_deg, off, roads=True, jitter=0.0):
    W, H = 1800, 1300
    z = scale * np.exp(1j * math.radians(rot_deg))
    c = complex(W / 2, -H / 2)
    def m2px(xy):
        q = xy[:, 0] + 1j * xy[:, 1]
        p = (q - off) / z + c
        return np.c_[p.real, -p.imag]
    img = np.full((H, W, 3), 250, np.uint8)
    for kind, ln in bm['lines']:
        ll = np.array(ln); xm, ym = proj.to_m(ll[:, 0], ll[:, 1])
        pts = m2px(np.c_[xm, ym]) + (rng.normal(0, jitter, 2) if jitter else 0)
        if roads:
            K.draw_poly(img, pts, (60, 60, 60) if kind == 'road' else (200, 120, 40), 3, closed=False)
    # park polygon ~800 m x 600 m around the pin, drawn as a dashed orange line
    ring = np.array([[-500, -300], [300, -350], [450, 200], [-100, 350], [-450, 150]], float)
    pr = m2px(ring)
    for a, b in zip(pr, np.roll(pr, -1, 0)):
        for t in np.arange(0, 1, 0.04):
            p0 = a + (b - a) * t; p1 = a + (b - a) * min(1, t + 0.025)
            cv2.line(img, tuple(map(int, p0)), tuple(map(int, p1)), (0, 120, 255), 6)
    cv2.imwrite(str(root / 'maps' / f'{ref}_synthetic.jpg'), img)
    shutil.copy('/workspace/kpc-tracer/test/cache/US-10172_basemap.json', root / 'cache' / f'{ref}_basemap.json')
    d = json.load(open(root / 'cache' / f'{ref}_basemap.json')); d['ref'] = ref
    json.dump(d, open(root / 'cache' / f'{ref}_basemap.json', 'w'))
    return ring

ring = render('US-90001', 2.0, 4.0, complex(150, -80))
render('US-90002', 2.0, 4.0, complex(150, -80), roads=False)
render('US-90003', 3.5, -8.0, complex(-300, 200), jitter=2.0)
idx = [dict(ref=r, name='synthetic ' + r, agency='TEST (synthetic, not a real agency map)',
            source_url='file://synthetic', page=1) for r in ('US-90001', 'US-90002', 'US-90003')]
json.dump(idx, open(root / 'index.json', 'w'))
json.dump({r['ref']: [lat, lon] for r in idx}, open(root / 'pins.json', 'w'))
subprocess.run([sys.executable, '/workspace/kpc-tracer/kpc_trace_picture.py', '--base', str(root), '--all'], check=True)
print(open(root / 'traced' / 'report.csv').read())
from shapely.geometry import Polygon, shape
true_poly = Polygon(ring)
for r in ('US-90001', 'US-90003'):
    f = root / 'traced' / f'{r}.json'
    if f.exists():
        g = json.load(open(f))['features'][0]
        xy = np.array(g['geometry']['coordinates'][0]); xm, ym = proj.to_m(xy[:, 0], xy[:, 1])
        tp = Polygon(np.c_[xm, ym])
        print(r, 'traced vs true outline: max vertex offset (Hausdorff) %.1f m, IoU %.3f' % (
            tp.hausdorff_distance(true_poly), tp.intersection(true_poly).area / tp.union(true_poly).area),
            'grade:', g['properties']['grade'])
