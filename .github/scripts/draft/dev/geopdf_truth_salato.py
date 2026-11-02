"""Dev-only check (not part of the deliverable): the KDFWR Pea Ridge PDF is an ArcMap
GeoPDF. Its embedded viewport georeference (4 corner lat/lon to 4 decimals, ~10 m) gives
an independent 'truth' to judge what the tracer's picture-only matcher could achieve."""
import sys, json, math
import numpy as np, cv2
sys.path.insert(0, '/workspace/kpc-tracer')
import kpc_trace_picture as K

W_PT, H_PT = 1224, 792
img = cv2.imread('/workspace/kpc-tracer/test/maps/US-10172_salato.jpg'); h, w = img.shape[:2]
s = w / W_PT
x0, y_top, x1, y_bot = 21, 709, 1203, 23           # viewport BBox [21 709 1203 23]
LPTS = [(0, 1), (0, 0), (1, 0), (1, 1)]
GPTS = [(38.174, -84.9442), (38.1849, -84.9441), (38.1848, -84.9203), (38.1739, -84.9204)]
pix = np.array([[(x0 + u * (x1 - x0)) * s, (H_PT - (y_top - v * (y_top - y_bot))) * s] for u, v in LPTS])
lat0, lon0 = 38.1777, -84.9231
proj = K.LocalProj(lat0, lon0)
mx, my = proj.to_m(np.array([g[1] for g in GPTS]), np.array([g[0] for g in GPTS]))
Qm = np.c_[mx, my]
truth = K.Model('affine', pix, Qm)
res = np.hypot(*(truth(pix) - Qm).T)
print('GeoPDF corner px', pix.round(1).tolist())
print('truth affine residuals at corners (m):', res.round(1).tolist())
z = K.Model('similarity', pix, Qm).z
print('scale m/px %.3f  rotation %.2f deg' % (abs(z), math.degrees(np.angle(z))))
bm = json.load(open('/workspace/kpc-tracer/test/cache/US-10172_basemap.json'))
inv = K.invert_model(truth, w, h)
out = img.copy()
for kind, ln in bm['lines']:
    ll = np.array(ln); xm, ym = proj.to_m(ll[:, 0], ll[:, 1])
    K.draw_poly(out, inv(np.c_[xm, ym]), (0, 0, 255) if kind == 'road' else (255, 0, 0), 2, closed=False)
pts = np.array([[p[1], p[2]] for p in bm['points']]); xm, ym = proj.to_m(pts[:, 0], pts[:, 1])
gp = inv(np.c_[xm, ym]); kinds = [p[0] for p in bm['points']]
inside = (gp[:, 0] > 34) & (gp[:, 0] < 1966) & (gp[:, 1] > 135) & (gp[:, 1] < 1256)
print('basemap junctions inside the main map frame:', int(inside.sum()),
      {k: int(sum(1 for i in np.nonzero(inside)[0] if kinds[i] == k)) for k in set(kinds)})
for x, y in gp[inside]:
    cv2.circle(out, (int(x), int(y)), 9, (0, 0, 0), 3)
# what the tracer saw on the picture
bnd = K.detect_boundary(img, {'kind': 'area'})
bx, by, bw, bh = cv2.boundingRect(np.round(bnd['pts_px']).astype(np.int32))
P, wts, segs = K.detect_junctions(img, 70, roi=(bx - .2*bw, by - .2*bh, bx + 1.2*bw, by + 1.2*bh))
for x, y in P:
    cv2.circle(out, (int(x), int(y)), 6, (255, 200, 0), 2)
from sklearn.neighbors import KDTree
d, _ = KDTree(gp[inside]).query(P, k=1)
print('picture candidates within 10 px (~11 m) of a true basemap junction:', int((d[:, 0] < 10).sum()), 'of', len(P))
print('within 25 px (~27 m):', int((d[:, 0] < 25).sum()))
# traced outline under the truth georef, for reference
poly = truth(bnd['pts_px'])
from shapely.geometry import Polygon, Point
pg = Polygon(poly).buffer(0)
print('picture boundary area under GeoPDF truth: %.0f acres; pin distance %.0f m' % (pg.area / 4046.86, pg.distance(Point(0, 0))))
K.put(out, 'GeoPDF truth: red=TIGER roads blue=NHD back-projected; black=true junctions; cyan=picture candidates', 30)
cv2.imwrite('/workspace/kpc-tracer/test/traced/debug/US-10172_geopdf_truth_check.png', out)
