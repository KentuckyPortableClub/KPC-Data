#!/usr/bin/env python3
"""PICTURE MAPS: THE SHARP PAGE + THE MAP'S OWN COORDINATES (chat 10, Nov 2 2026; outside review of the tracers, Brandon OK 6:34 AM,
HQ 'tracer fixes let 10 try'). Runs in the picture-tracer workflow AFTER kpc_picture_prep.py, on the picture-maps worktree <base>:
  1. for each map whose source is a PDF, the PDF is downloaded (kpc_manners: polite, a 403 / robot check is never bypassed) into a temp
     folder of this run (NEVER saved: the branch keeps its small 2000 px copy by the house rule);
  2. the boundary page is drawn again SHARP (4000 px long side, JPEG quality 85) over <base>/maps/<file> in the worktree only, so the
     tracer sees thin boundary lines the small copy blurs (set KPC_TRACE_MAX_PX=4000 for the tracer);
  3. GeoPDF: when the page carries its own coordinates (ISO 32000 /VP /Measure /GEO with /GPTS + /LPTS, or the older TerraGo
     /LGIDict with a geographic or UTM /Projection), the picture-to-GPS formula is written into index.json as row['geo']
     {affine: [a, b, c, d, e, f], how}: lon = a*u + b*v + c, lat = d*u + e*v + f, with u, v = the pixel's place across / down the
     whole page (0..1), so it holds for any picture size. The tracer then places the outline by the map's own coordinates and skips
     the basemap matching (still Approximate, R-G9; the boundary colour detection is the same).
Never fails.   python3 kpc_picture_geo.py <base> <cache dir>"""
import io, json, math, os, pathlib, re, subprocess, sys, tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
HI_PX, HI_Q = int(os.environ.get('KPC_PIC_HI_PX') or 4000), int(os.environ.get('KPC_PIC_HI_Q') or 85)


def load(p, d):
    try: return json.load(open(p, encoding='utf-8'))
    except Exception: return d  # noqa: BLE001


# ------------------------------------------------------------------ the formula
def fit_affine(uv, ll):
    """Least squares (u, v) -> (lon, lat), 3+ points. -> [a, b, c, d, e, f] and the worst error in metres."""
    import numpy as np
    U = np.array([[u, v, 1.0] for u, v in uv]); L = np.array(ll, float)
    cx, *_ = np.linalg.lstsq(U, L[:, 0], rcond=None); cy, *_ = np.linalg.lstsq(U, L[:, 1], rcond=None)
    pred = U @ np.c_[cx, cy]
    la = math.radians(float(L[:, 1].mean()))
    err = float(np.max(np.hypot((pred[:, 0] - L[:, 0]) * 111320 * math.cos(la), (pred[:, 1] - L[:, 1]) * 110574))) if len(L) > 3 else 0.0
    return [float(x) for x in (*cx, *cy)], err


def _num(x):
    try: return float(x)
    except Exception: return None  # noqa: BLE001


def _arr(o):
    try: return [_num(v) for v in o]
    except Exception: return []  # noqa: BLE001


def page_box(page):
    b = page.get('/CropBox') or page.get('/MediaBox')
    x0, y0, x1, y1 = [_num(v) for v in b]
    return min(x0, x1), min(y0, y1), abs(x1 - x0), abs(y1 - y0)


def to_uv(x, y, box, rot=0):
    mx, my, W, H = box
    u, v = (x - mx) / W, 1.0 - (y - my) / H
    rot = int(rot or 0) % 360
    if rot == 90: u, v = 1.0 - v, u
    elif rot == 180: u, v = 1.0 - u, 1.0 - v
    elif rot == 270: u, v = v, 1.0 - u
    return u, v


def geo_iso(page, box, rot):
    """ISO 32000-2 geospatial: the biggest /VP viewport whose /Measure is /GEO."""
    best = None
    for vp in page.get('/VP') or []:
        try: vp = vp.get_object()
        except Exception: pass  # noqa: BLE001
        m = vp.get('/Measure')
        if m is None: continue
        m = m.get_object()
        if str(m.get('/Subtype')) != '/GEO': continue
        bb = _arr(vp.get('/BBox')); g = _arr(m.get('/GPTS')); lp = _arr(m.get('/LPTS') or [0, 1, 0, 0, 1, 0, 1, 1])
        if len(bb) != 4 or len(g) < 6 or len(lp) != len(g) or None in bb + g + lp: continue
        # LPTS are fractions of the BBox *in the order its corners are written* (ISO 32000-2 12.10).
        # Many exporters (ArcGIS among them) write the BBox top-to-bottom ([x0, ytop, x1, ybottom]);
        # sorting the corners first flips the page upside down (US-5460, CA-1248, US-6048, Nov 7).
        x0, y0, x1, y1 = bb
        uv = [to_uv(x0 + lp[i] * (x1 - x0), y0 + lp[i + 1] * (y1 - y0), box, rot) for i in range(0, len(lp), 2)]
        x0, y0, x1, y1 = min(bb[0], bb[2]), min(bb[1], bb[3]), max(bb[0], bb[2]), max(bb[1], bb[3])
        ll = [(g[i + 1], g[i]) for i in range(0, len(g), 2)]   # GPTS = lat, lon pairs
        area = (x1 - x0) * (y1 - y0)
        if best is None or area > best[0]: best = (area, uv, ll)
    if not best: return None
    aff, err = fit_affine(best[1], best[2])
    return {'affine': aff, 'how': 'GeoPDF (ISO 32000 /GPTS)', 'fit_err_m': round(err, 1)}


def geo_lgi(page, box, rot):
    """The older TerraGo /LGIDict: /CTM (page -> map units) + /Projection (geographic, or UTM with a zone)."""
    d = page.get('/LGIDict')
    if d is None: return None
    d = d.get_object()
    if isinstance(d, list): d = d[0].get_object()
    ctm = _arr(d.get('/CTM')); pj = d.get('/Projection')
    if len(ctm) != 6 or None in ctm or pj is None: return None
    pj = pj.get_object(); typ = str(pj.get('/ProjectionType') or '').strip('/()').upper()
    nl = _arr(d.get('/Neatline')) or [box[0], box[1], box[0] + box[2], box[1], box[0] + box[2], box[1] + box[3], box[0], box[1] + box[3]]
    pts = [(nl[i], nl[i + 1]) for i in range(0, len(nl) - 1, 2)]
    if len(pts) < 3: return None
    a, b, c, dd, e, f = ctm
    mapxy = [(a * x + c * y + e, b * x + dd * y + f) for x, y in pts]
    if typ in ('GEOGRAPHIC', 'GEO'):
        ll = list(mapxy)
    elif typ == 'UT':
        try:
            from pyproj import Transformer
            zone = int(_num(pj.get('/Zone')))
            south = str(pj.get('/Hemisphere') or 'N').strip('/()').upper().startswith('S')
            T = Transformer.from_crs(f"+proj=utm +zone={abs(zone)} {'+south ' if south or zone < 0 else ''}+datum=WGS84 +units=m +no_defs", 'EPSG:4326', always_xy=True)
            ll = [T.transform(x, y) for x, y in mapxy]
        except Exception: return None  # noqa: BLE001
    else:
        return {'skip': f'GeoPDF projection {typ or "?"} not read yet (geographic + UTM only)'}
    if not all(-180 <= lo <= 180 and -90 <= la <= 90 for lo, la in ll): return None
    aff, err = fit_affine([to_uv(x, y, box, rot) for x, y in pts], ll)
    return {'affine': aff, 'how': f'GeoPDF (TerraGo /LGIDict, {typ})', 'fit_err_m': round(err, 1)}


def geo_of(pdf_bytes, page_no):
    from pypdf import PdfReader
    r = PdfReader(io.BytesIO(pdf_bytes))
    if not (1 <= page_no <= len(r.pages)): return None
    pg = r.pages[page_no - 1]
    box = page_box(pg); rot = pg.get('/Rotate') or 0
    for fn in (geo_iso, geo_lgi):
        try:
            g = fn(pg, box, rot)
            if g: return g
        except Exception as e: return {'skip': f'GeoPDF not read ({type(e).__name__}: {str(e)[:60]})'}  # noqa: BLE001
    return None


def sharp(pdf_path, page_no, out_jpg):
    with tempfile.TemporaryDirectory() as td:
        stem = pathlib.Path(td) / 'p'
        subprocess.run(['pdftoppm', '-f', str(page_no), '-l', str(page_no), '-singlefile', '-jpeg', '-jpegopt', f'quality={HI_Q}',
                        '-scale-to', str(HI_PX), str(pdf_path), str(stem)], capture_output=True, timeout=600)
        j = stem.with_suffix('.jpg')
        if j.exists() and j.stat().st_size > 1000:
            j.replace(out_jpg); return True
    return False


def main():
    base, cache = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]) / 'pdf'
    cache.mkdir(parents=True, exist_ok=True)
    idx = load(base / 'index.json', {}) or {}
    if not isinstance(idx, dict): print('::notice title=Picture maps (sharp + GeoPDF)::index.json is not the prep step\'s ref-keyed file'); return
    from kpc_manners import Manners
    M = Manners('KPC picture-map tracer (chat 10): the agency map PDF, once, to draw it sharp', read_max=150_000_000)
    n = {'pdf': 0, 'sharp': 0, 'geo': 0, 'nofile': 0, 'notpdf': 0}; why = []
    for ref, row in idx.items():
        u = str(row.get('source_url') or '')
        pg = row.get('page'); pg = int(pg[0] if isinstance(pg, list) and pg else pg or 1)
        f = cache / (re.sub(r'[^A-Za-z0-9_-]', '_', ref) + '.pdf')
        if not f.exists():
            if not u.startswith('http'): n['nofile'] += 1; continue
            st, hd, body, final = M.get(u, timeout=300, accept='application/pdf,*/*;q=0.5')
            if not (isinstance(st, int) and st < 400 and body[:5] == b'%PDF-'):
                n['notpdf' if isinstance(st, int) and st < 400 else 'nofile'] += 1; continue
            f.write_bytes(body)
        n['pdf'] += 1
        mf = row.get('map_file')
        try:
            if mf and (base / 'maps' / mf).exists() and sharp(f, pg, base / 'maps' / mf): n['sharp'] += 1
        except Exception as e: why.append(f'{ref}: not drawn sharp ({type(e).__name__})')  # noqa: BLE001  (GeoPDF is still read below)
        try: g = geo_of(f.read_bytes(), pg)
        except Exception as e: g = {'skip': f'{type(e).__name__}'}  # noqa: BLE001
        if g and g.get('affine'):
            row['geo'] = g; n['geo'] += 1
        elif g and g.get('skip'): why.append(f"{ref}: {g['skip']}")
    json.dump(idx, open(base / 'index.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print(f"::notice title=Picture maps (sharp + GeoPDF)::{len(idx)} maps: {n['pdf']} PDFs read, {n['sharp']} pages drawn sharp ({HI_PX} px, q{HI_Q}; "
          f"run cache only), {n['geo']} carry their own GeoPDF coordinates; {n['notpdf']} not a PDF (a picture: the small copy is used), "
          f"{n['nofile']} no file" + (f"; {'; '.join(why[:5])}" if why else ''), flush=True)


if __name__ == '__main__':
    try: main()
    except Exception as e: print(f'::notice title=Picture maps (sharp + GeoPDF)::stopped ({type(e).__name__}: {e}); the small copies are used')  # noqa: BLE001
