#!/usr/bin/env python3
"""What the real 5 m grid of pass 3 reads for a known overlap width (made-up squares, as the Handoff 9 test builds them).
Usage: grid_band.py <KPC-Links checkout> [out.json]. Offline; needs numpy + opencv. Run it from a folder that is NOT the checkout."""
import os, sys, math, pathlib, tempfile, io, contextlib, json
HERE = pathlib.Path(sys.argv[1]).resolve()
sys.path.insert(0, str(HERE / '.github/scripts'))
os.environ['PASS'] = '3'; os.environ['HTTP_CACHE'] = ''
for k in list(os.environ):
    if k.startswith('KPC_FERS_'): os.environ.pop(k)
os.chdir(tempfile.mkdtemp(prefix='kpc-band-'))
with contextlib.redirect_stdout(io.StringIO()):
    import kpc_fers as K
LAT0, LON0 = 37.5, -84.0
KX, KY = 111320 * math.cos(math.radians(LAT0)), 110574
def rect(x0, y0, x1, y1, ang=0):
    a = math.radians(ang); out = []
    for x, y in [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]:
        xr, yr = x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)
        out.append([LON0 + xr / KX, LAT0 + yr / KY])
    return [[out]]
def measure(w, ang, off):
    A, B = rect(-2000, -1000, off + w, 1000, ang), rect(off, -1000, 2000, 1000, ang)
    pts = A[0][0] + B[0][0]
    box = [min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts)]
    with contextlib.redirect_stdout(io.StringIO()):
        sp = K.area_spots({'US-9901': A, 'US-9902': B}, ['US-9901', 'US-9902'], box)
    return max((s['wide_m'] for s in sp), default=None)
print('grid', K.CELL, 'm; SHRINK', K.SHRINK)
res = []
for w in list(range(8, 33)) + list(range(38, 56)):
    row = []
    for ang in (0, 17, 30, 45):
        for off in (0, 1.3, 2.6, 3.9):
            row.append(measure(w, ang, off))
    got = [x for x in row if x is not None]
    res.append((w, len(got), len(row), min(got) if got else None, max(got) if got else None))
    print(f'true {w:>2} m: found in {len(got):>2} of {len(row)}; read {min(got) if got else "-"} to {max(got) if got else "-"} m', flush=True)
if len(sys.argv) > 2: json.dump(res, open(sys.argv[2], 'w'))
