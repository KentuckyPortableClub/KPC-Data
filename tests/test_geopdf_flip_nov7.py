"""Nov 7 (coordinator): GeoPDF /VP /BBox written top-to-bottom must not flip the page, and a type-only size guess
must not make pin mode prefer a bigger shape over the tight one the pin sits in. Offline, no network."""
import pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github/scripts/draft'))
import numpy as np, cv2
import kpc_picture_geo as G

fails = []
def check(name, ok):
    print(('ok   ' if ok else 'FAIL ') + name)
    if not ok: fails.append(name)

class D(dict):
    def get_object(self): return self

def page(bbox, gpts, lpts=(0, 1, 0, 0, 1, 0, 1, 1)):
    m = D({'/Subtype': '/GEO', '/GPTS': list(gpts), '/LPTS': list(lpts)})
    return D({'/VP': [D({'/BBox': list(bbox), '/Measure': m})]})

box = (0.0, 0.0, 1000.0, 1000.0)
# US-5460 style: BBox [x0, ytop, x1, ybottom]; LPTS (0,1) is paired with the SOUTH-west corner
g = (42.0, -124.0, 46.0, -124.0, 46.0, -120.0, 42.0, -120.0)
for name, bb in (('top-to-bottom BBox', (0, 1000, 1000, 0)), ('bottom-to-top BBox', (0, 0, 1000, 1000))):
    lp = (0, 1, 0, 0, 1, 0, 1, 1) if bb[1] > bb[3] else (0, 0, 0, 1, 1, 1, 1, 0)
    r = G.geo_iso(page(bb, g, lp), box, 0)
    a = r['affine']
    top_lat = a[3] * 0.5 + a[4] * 0.0 + a[5]; bot_lat = a[3] * 0.5 + a[4] * 1.0 + a[5]
    check(f'{name}: north is at the top of the page (top {top_lat:.2f}, bottom {bot_lat:.2f})', top_lat > bot_lat)
    check(f'{name}: fits its own corners', r['fit_err_m'] < 1)

import kpc_trace_picture as T
# a 400 px wide tint square (the park) inside a much bigger ring of another colour; the pin is in the square
img = np.full((2000, 2000, 3), 245, np.uint8)
ring = np.array([[300, 250], [1750, 400], [1650, 1750], [900, 1850], [250, 1300]], np.int32)
cv2.polylines(img, [ring], True, (200, 60, 230), 18)                         # big magenta ring (~20x the park), not a rectangle
cv2.ellipse(img, (1000, 1000), (230, 170), 20, 0, 360, (60, 200, 120), -1)    # green filled park (not a rectangle)
cv2.circle(img, (1000, 1000), 4, (60, 200, 120), -1)
row = {'kind': 'area'}
mpp = 2.0
b = T.detect_boundary(img, row, pin_px=(1000, 1000), m_per_px=mpp, expected_acres=None, max_acres=5000)
ac = b.get('pin_acres') or 0
check(f'type ceiling only: the tight park at the pin wins (~{ac:.0f} ac picked)', 100 < ac < 300)
b2 = T.detect_boundary(img, row, pin_px=(1000, 1000), m_per_px=mpp, expected_acres=None, max_acres=50)
check('a shape over the ceiling ranks last but is still returned when nothing else fits', b2 is not None)
print('ALL PASS' if not fails else f'{len(fails)} FAILED'); sys.exit(1 if fails else 0)
