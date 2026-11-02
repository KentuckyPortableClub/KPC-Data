import json, math, sys
import numpy as np, cv2
sys.path.insert(0, '/workspace/kpc-tracer')
import kpc_trace_picture as K
from sklearn.neighbors import KDTree
ref, scale, rot, off = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), complex(float(sys.argv[4]), float(sys.argv[5]))
root = '/workspace/kpc-tracer/dev/synth'
img = cv2.imread(f'{root}/maps/{ref}_synthetic.jpg'); h, w = img.shape[:2]
bm = json.load(open(f'{root}/cache/{ref}_basemap.json')); proj = K.LocalProj(*bm['pin'])
z = scale * np.exp(1j * math.radians(rot)); c = complex(w / 2, -h / 2)
pts = np.array([[p[1], p[2]] for p in bm['points']]); xm, ym = proj.to_m(pts[:, 0], pts[:, 1])
q = xm + 1j * ym; p = (q - off) / z + c; gp = np.c_[p.real, -p.imag]
ins = (gp[:, 0] > 0) & (gp[:, 0] < w) & (gp[:, 1] > 0) & (gp[:, 1] < h)
print('true junctions in picture:', ins.sum())
P, wts, segs = K.detect_junctions(img, 70)
d, _ = KDTree(gp[ins]).query(P, k=1)
print('candidates', len(P), 'within 6px of truth', (d[:, 0] < 6).sum(), 'within 15px', (d[:, 0] < 15).sum())
Q = np.c_[xm, ym]; order = np.argsort(np.hypot(Q[:, 0], Q[:, 1]))[:300]; Q = Q[order]
qi = (Q[:, 0] + 1j * Q[:, 1] - off) / z + c
print('of 300 nearest-pin basemap pts, inside picture:', ((qi.real > 0) & (qi.real < w) & (-qi.imag > 0) & (-qi.imag < h)).sum())
prior = K.Prior(0.2, 25, 25, (0, 0, w, h))
hy = K.hough_hypotheses(P, Q, np.array([w / 2, h / 2]), prior)
true_u = off  # metric pos of image centre
for rank, (v, zz, t) in enumerate(hy[:250]):
    u = zz * c + t
    if abs(abs(zz) / scale - 1) < 0.1 and abs(u - true_u) < 300:
        print('true hypothesis at rank', rank, 'votes', v); break
else:
    print('true hypothesis not in top 250; top votes', [h_[0] for h_ in hy[:10]])
