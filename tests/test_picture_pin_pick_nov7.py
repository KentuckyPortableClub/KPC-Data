#!/usr/bin/env python3
"""Nov 7 pin mode (kpc_trace_picture.detect_boundary): on a GeoPDF page the boundary colour is chosen BY THE PIN, not by total area.
Synthetic pages drawn with OpenCV; the colour clustering is replaced by an exact label map, so this tests the SHAPE CHOICE only, not
k-means. Needs numpy + opencv (no shapely / pyproj / scikit-learn / network).   python3 -B tests/test_picture_pin_pick_nov7.py"""
import importlib.util, os, sys, types

import numpy as np
try:
    import cv2
except ImportError:
    print('SKIP-IMPOSSIBLE: opencv is needed for this test'); sys.exit(1)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _stub(name, **attrs):
    m = types.ModuleType(name)
    for k, v in attrs.items(): setattr(m, k, v)
    sys.modules.setdefault(name, m)
    return m


def _load():
    """Import kpc_trace_picture with stand-ins for the geometry libraries: detect_boundary uses only numpy + cv2."""
    if 'shapely' not in sys.modules:
        _stub('shapely', transform=None)
        _stub('shapely.geometry', LineString=object, Point=object, Polygon=object, mapping=None)
        _stub('shapely.validation', make_valid=None); _stub('shapely.ops', unary_union=None)
        _stub('pyproj', Transformer=object)
        _stub('sklearn'); _stub('sklearn.cluster', DBSCAN=object, KMeans=object); _stub('sklearn.neighbors', KDTree=object)
    sp = importlib.util.spec_from_file_location('kpc_trace_picture', os.path.join(ROOT, '.github/scripts/draft/kpc_trace_picture.py'))
    m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    return m


TP = _load()
bad = []


def check(cond, msg):
    if not cond: bad.append(msg); print('FAIL', msg)


WHITE, MAGENTA, BLUE, GREEN, PINK = (255, 255, 255), (255, 0, 255), (200, 120, 0), (60, 170, 60), (190, 150, 230)


def page(w=900, h=700):
    return np.full((h, w, 3), WHITE, np.uint8)


def blob(cx, cy, rx, ry, n=13, wobble=0.08, seed=3):
    """An irregular closed polygon: real park shapes are never axis-aligned rectangles, and detect_boundary rejects rectangles on
    purpose (map frames, legend boxes, inset panels)."""
    rng = np.random.default_rng(seed)       # a gentle wobble: a spiky polygon self-crosses and stops being a closed ring
    a = np.linspace(0, 2 * np.pi, n, endpoint=False)
    r = 1.0 + rng.uniform(-wobble, wobble, n)
    return np.round(np.c_[cx + rx * r * np.cos(a), cy + ry * r * np.sin(a)]).astype(np.int32)


def detect(img, colours, **kw):
    """Run detect_boundary with the page's exact colours standing in for the k-means clustering (labels = index into `colours`), so this
    test is about the shape choice only."""
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
    labels = np.zeros(img.shape[:2], np.int32)
    for i, c in enumerate(colours):
        labels[np.all(img == np.array(c, np.uint8), axis=2)] = i
    centres = np.array([cv2.cvtColor(np.uint8([[c[::-1]]]), cv2.COLOR_BGR2LAB).astype(np.float32)[0, 0] for c in colours], np.float32)
    TP.lab_kmeans = lambda im, k, seed=0: (labels, centres, lab)
    return TP.detect_boundary(img, {'kind': 'area'}, k=len(colours), **kw)


def name_of(bnd):
    return (bnd or {}).get('mask_name', '')


def area_of(bnd):
    return cv2.contourArea(np.round(bnd['pts_px']).astype(np.int32))


# ---- page 1: a statewide sheet (US-5460 Sun Pass). A big magenta DISTRICT RING holds most of the page and the pin sits inside it;
# the park itself is a small blue filled blob at the pin. The old rule traces the ring (25.9 M ac); pin mode must take the blob.
img = page()
cv2.polylines(img, [blob(450, 350, 390, 300, seed=1)], True, MAGENTA, 9)
cv2.fillPoly(img, [blob(520, 480, 48, 40, seed=2)], BLUE)
C1, pin = [WHITE, MAGENTA, BLUE], (520, 480)
old = detect(img, C1)
new = detect(img, C1, pin_px=pin, m_per_px=25.0, expected_acres=5000)
check('cluster1' in name_of(old) and 'ring' in name_of(old), f'the old pick should be the big magenta ring, got {name_of(old)!r}')
check('cluster2' in name_of(new) and 'filled' in name_of(new), f'pin mode must take the blue blob at the pin, got {name_of(new)!r}')
check(area_of(new) < 0.05 * img.shape[0] * img.shape[1], 'the traced shape in pin mode must be the blob, not the sheet ring')
check('contains the pin' in name_of(new), f'the reason must say the shape contains the pin: {name_of(new)!r}')
check('cluster2' in name_of(detect(img, C1, pin_px=pin, m_per_px=25.0)),
      'with no expected size a filled tint at the pin still beats a ring')
check(name_of(detect(img, C1)) == name_of(old), 'without pin_px the old choice is unchanged')

# ---- page 2: a city map (CA-1248 Pagan Point). A green filled preserve holds the pin; a pink road grid makes closed blocks around it.
img2 = page()
cv2.fillPoly(img2, [blob(430, 330, 140, 135, seed=4)], GREEN)
for x in range(80, 860, 120): cv2.line(img2, (x, 60), (x, 640), PINK, 7)
for y in range(60, 660, 120): cv2.line(img2, (80, y), (840, y), PINK, 7)
new2 = detect(img2, [WHITE, GREEN, PINK], pin_px=(430, 330), m_per_px=2.0, expected_acres=300)
check('cluster1' in name_of(new2) and 'filled' in name_of(new2), f'pin mode must take the green preserve, got {name_of(new2)!r}')

# ---- page 3: the park IS a ring (an outline-only map) and a bigger filled tint also covers the pin. With a size to aim at, the ring wins.
img3 = page()
cv2.fillPoly(img3, [blob(450, 350, 340, 270, seed=5)], BLUE)
cv2.polylines(img3, [blob(450, 350, 80, 70, seed=6)], True, MAGENTA, 8)
new3 = detect(img3, [WHITE, BLUE, MAGENTA], pin_px=(450, 350), m_per_px=4.0, expected_acres=25)
big3 = detect(img3, [WHITE, BLUE, MAGENTA])
check(area_of(new3) < 0.25 * area_of(big3), f'with a size to aim at, the small shape around the pin wins, not the page-wide tint '
      f'({area_of(new3):.0f} px vs {area_of(big3):.0f} px; chose {name_of(new3)!r})')
check(area_of(detect(img3, [WHITE, BLUE, MAGENTA], pin_px=(450, 350), m_per_px=4.0)) == area_of(new3),
      'with NO size either, the tightest filled shape around the pin is taken, not the page-wide tint')

# ---- page 4: nothing of any colour at the pin -> no boundary at all (an honest NO LINE), where the old rule traced the far shape.
img4 = page()
cv2.fillPoly(img4, [blob(180, 160, 60, 55, seed=7)], BLUE)
C4 = [WHITE, BLUE]
check(detect(img4, C4) is not None, 'the old path still finds the far shape')
check(detect(img4, C4, pin_px=(800, 600), m_per_px=5.0) is None,
      'pin mode must find nothing when no shape is at the pin (NO LINE, not a wrong outline)')
check(detect(img4, C4, pin_px=(180 + 60 + int(TP.PIN_NEAR_M / 5.0) - 8, 160), m_per_px=5.0) is not None,
      f'a shape within {TP.PIN_NEAR_M:g} m of the pin is still a candidate')
check(detect(img4, C4, pin_px=(180 + 60 + int(TP.PIN_NEAR_M / 5.0) + 60, 160), m_per_px=5.0) is None,
      'a shape further away than that is not')

# ---- page 5: with NO size to aim at, a filled park tint at the pin beats a TIGHTER ring at the pin. On these agency maps the park is
# usually a tint and a tight ring is as often a district or section line; when the tint is the wrong pick the Nov 7 size gates hold it
# rather than drawing it. (With a size to aim at this reverses: see page 3.)
img5 = page()
cv2.fillPoly(img5, [blob(450, 350, 230, 190, seed=8)], GREEN)
cv2.polylines(img5, [blob(452, 352, 55, 48, seed=9)], True, MAGENTA, 7)
C5 = [WHITE, GREEN, MAGENTA]
no_size = detect(img5, C5, pin_px=(450, 350), m_per_px=3.0)
check('cluster1' in name_of(no_size) and '~14 ac' in name_of(no_size),
      f'no size: the tight filled area the ring encloses is taken, not the page-wide tint, got {name_of(no_size)!r}')
check('cluster2' in name_of(detect(img5, C5, pin_px=(450, 350), m_per_px=3.0, expected_acres=20)),
      'a size to aim at picks the ring itself when the ring is what matches that size')
check('~288 ac' in name_of(no_size), 'the runner-up at the pin is named in the reason, so a wrong pick can be audited')

# ---- page 6: a shape CONTAINING the pin beats a better-sized shape that merely lies near it.
img6 = page()
cv2.fillPoly(img6, [blob(450, 350, 120, 100, seed=10)], GREEN)      # contains the pin, bigger
cv2.fillPoly(img6, [blob(508, 350, 40, 36, seed=11)], BLUE)         # well inside PIN_NEAR_M of the pin, and much nearer the expected size
C6, pin6 = [WHITE, GREEN, BLUE], (450, 350)
got6 = detect(img6, C6, pin_px=pin6, m_per_px=6.0, expected_acres=45)
check('cluster1' in name_of(got6) and 'contains the pin' in name_of(got6),
      f'a shape containing the pin wins over a better-sized shape merely near it, got {name_of(got6)!r}')
check('m from the pin' in name_of(detect(img6, C6, pin_px=(240, 350), m_per_px=6.0, expected_acres=45)) or
      detect(img6, C6, pin_px=(240, 350), m_per_px=6.0, expected_acres=45) is None,
      'with the pin outside every shape, only a shape within PIN_NEAR_M may be taken, and the reason says how far it is')

check(TP.PIN_PICK is True, 'KPC_TRACE_PIN_PICK defaults to on')

print('FAIL' if bad else 'ALL PASS', f'({len(bad)} problems)' if bad else '')
sys.exit(1 if bad else 0)
