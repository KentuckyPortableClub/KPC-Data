#!/usr/bin/env python3
"""T1 TRACER TEST, THE MEASURING STEP (key-quality.md section 16 T1 points 3-4, section 19 item 6; Opus 19 Nov 2026).
The tracer never sees the official outline or its acres; this script does, AFTER the tracer is done. Standard library only
(plain-Python rasters + point-to-segment distances), so it gives the same numbers on any machine.

For every traced park (the picked list, in order):
  ratio      traced acres / official acres
  covered    share of the official outline the trace covers
  outside    share of the trace that lies outside the official outline
  line_mid / line_worst10   how far the traced line is from the official line, feet: middle (median) and worst tenth (90th pct)
  failure    no trace / the map had no boundary / the wrong feature traced, in plain words
Grade words (the grade's own): WRONG LAND (most of the trace outside: outside > 0.5), TOO BIG (ratio over 1.25),
MISSING PIECES (covered under 0.8), else GOOD. Sum: counts per size class with 95% ranges (Wilson), never single numbers alone.

  python3 kpc_trace_measure.py --list t1-list.json --picked picked.json --traced DIR [--unofficial DIR] \
      --outlines <KPC-Links>/data/outlines --out DIR
  python3 kpc_trace_measure.py --selftest
picked.json: {"picked": [ref, ...], "skipped": [{"ref", "why"}, ...]}  (the T1 workflow's pick step writes it)
OUT/t1-parks.csv, OUT/t1-summary.md, OUT/t1-result.json"""
import argparse, csv, glob, gzip, json, math, os, pathlib, sys

R_EARTH = 6371008.8
SQM_PER_ACRE = 4046.8564224
FT_PER_M = 3.280839895
GRID = 500          # raster cells on the long side of the shared box


# ------------------------------------------------------------------ geometry (lon/lat -> local metres)
def polys_of(geom):
    """GeoJSON Polygon / MultiPolygon / GeometryCollection -> [[ring, ring, ...], ...] (first ring = outside, the rest = holes)."""
    if not geom: return []
    t = geom.get('type')
    if t == 'Polygon': return [geom['coordinates']]
    if t == 'MultiPolygon': return list(geom['coordinates'])
    if t == 'GeometryCollection': return [p for g in geom.get('geometries') or [] for p in polys_of(g)]
    return []


def projector(lat0, lon0):
    k = math.cos(math.radians(lat0))
    return lambda lon, lat: (math.radians(lon - lon0) * R_EARTH * k, math.radians(lat - lat0) * R_EARTH)


def project(polys, f):
    return [[[f(x, y) for x, y, *_ in ring] for ring in poly] for poly in polys]


def bbox(polys):
    xs = [p[0] for poly in polys for ring in poly for p in ring]; ys = [p[1] for poly in polys for ring in poly for p in ring]
    return (min(xs), min(ys), max(xs), max(ys)) if xs else None


def ring_area(r):
    return abs(sum(r[i][0] * r[i + 1][1] - r[i + 1][0] * r[i][1] for i in range(len(r) - 1))) / 2 if len(r) > 2 else 0.0


def raster(polys, box, nx, ny):
    """Set of filled cells (ix, iy): each polygon filled by the even-odd rule over its own rings (holes cut out), polygons OR-ed."""
    x0, y0, x1, y1 = box; dx = (x1 - x0) / nx; dy = (y1 - y0) / ny; out = set()
    for poly in polys:
        edges = [(r[i], r[i + 1]) for r in poly for i in range(len(r) - 1) if r[i][1] != r[i + 1][1]]
        for iy in range(ny):
            yc = y0 + (iy + 0.5) * dy; xs = []
            for (ax, ay), (bx, by) in edges:
                if (ay <= yc < by) or (by <= yc < ay): xs.append(ax + (yc - ay) * (bx - ax) / (by - ay))
            xs.sort()
            for a, b in zip(xs[0::2], xs[1::2]):
                i0 = max(0, math.ceil((a - x0) / dx - 0.5)); i1 = min(nx - 1, math.floor((b - x0) / dx - 0.5))
                for ix in range(i0, i1 + 1): out.add((ix, iy))
    return out


def seg_dist(p, a, b):
    ax, ay = a; bx, by = b; px, py = p; vx, vy = bx - ax, by - ay; L = vx * vx + vy * vy
    t = 0 if L == 0 else max(0.0, min(1.0, ((px - ax) * vx + (py - ay) * vy) / L))
    return math.hypot(px - ax - t * vx, py - ay - t * vy)


def boundary_points(polys, step):
    pts = []
    for poly in polys:
        for r in poly:
            for i in range(len(r) - 1):
                (ax, ay), (bx, by) = r[i], r[i + 1]; n = max(1, int(math.hypot(bx - ax, by - ay) / step))
                pts += [(ax + (bx - ax) * j / n, ay + (by - ay) * j / n) for j in range(n)]
    return pts


def line_distances(trace, official, max_pts=1500):
    """Distance from points along the traced line to the nearest official line, metres (a coarse cell index keeps it quick)."""
    segs = [(r[i], r[i + 1]) for poly in official for r in poly for i in range(len(r) - 1)]
    if not segs: return []
    per = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for poly in trace for r in poly for a, b in zip(r, r[1:]))
    pts = boundary_points(trace, max(per / max_pts, 1.0))
    if not pts: return []
    bx = bbox(official + trace); cell = max((bx[2] - bx[0]), (bx[3] - bx[1])) / 60 or 1.0; idx = {}
    for s in segs:
        (ax, ay), (bx_, by) = s
        for i in range(int(min(ax, bx_) // cell), int(max(ax, bx_) // cell) + 1):
            for j in range(int(min(ay, by) // cell), int(max(ay, by) // cell) + 1): idx.setdefault((i, j), []).append(s)
    out = []
    for p in pts:
        ci, cj = int(p[0] // cell), int(p[1] // cell); best = None; ring = 0
        while best is None or ring * cell < best + cell:
            cand = [s for i in range(ci - ring, ci + ring + 1) for j in range(cj - ring, cj + ring + 1)
                    if max(abs(i - ci), abs(j - cj)) == ring for s in idx.get((i, j), [])]
            for a, b in cand:
                d = seg_dist(p, a, b)
                if best is None or d < best: best = d
            ring += 1
            if ring > 80: break
        out.append(best if best is not None else float('inf'))
    return out


def pct(v, q):
    v = sorted(v)
    if not v: return None
    k = (len(v) - 1) * q; f = math.floor(k); c = math.ceil(k)
    return v[f] if f == c else v[f] + (v[c] - v[f]) * (k - f)


def measure(trace_geom, official_geom):
    """The four numbers of T1 point 3 for one park. Geometries are GeoJSON (lon/lat)."""
    tp, op = polys_of(trace_geom), polys_of(official_geom)
    if not op: return {'failure': 'no official outline on file'}
    if not tp: return {'failure': 'no trace'}
    allb = bbox(op + tp); f = projector((allb[1] + allb[3]) / 2, (allb[0] + allb[2]) / 2)
    T, O = project(tp, f), project(op, f)
    box = bbox(O + T); w, h = box[2] - box[0], box[3] - box[1]
    if w <= 0 or h <= 0: return {'failure': 'empty geometry'}
    pad = 0.01 * max(w, h); box = (box[0] - pad, box[1] - pad, box[2] + pad, box[3] + pad); w, h = box[2] - box[0], box[3] - box[1]
    nx = GRID if w >= h else max(20, round(GRID * w / h)); ny = GRID if h > w else max(20, round(GRID * h / w))
    cell = (w / nx) * (h / ny)
    rt, ro = raster(T, box, nx, ny), raster(O, box, nx, ny)
    inter = len(rt & ro)
    ta = sum(ring_area(p[0]) - sum(ring_area(r) for r in p[1:]) for p in T); oa = sum(ring_area(p[0]) - sum(ring_area(r) for r in p[1:]) for p in O)
    d = line_distances(T, O)
    res = {'traced_acres': round(ta / SQM_PER_ACRE, 1), 'official_acres': round(oa / SQM_PER_ACRE, 1),
           'ratio': round(ta / oa, 3) if oa else None,
           'covered': round(inter / len(ro), 3) if ro else None, 'outside': round((len(rt) - inter) / len(rt), 3) if rt else None,
           'line_mid_ft': round(pct(d, 0.5) * FT_PER_M) if d else None, 'line_worst10_ft': round(pct(d, 0.9) * FT_PER_M) if d else None,
           'cell_m': round(math.sqrt(cell), 1)}
    if res['covered'] == 0 and res['outside'] and res['outside'] > 0.9: res['failure'] = 'the wrong feature traced (no overlap with the official outline)'
    return res


def grade(m):
    if m.get('failure'): return 'FAILED'
    if (m.get('outside') or 0) > 0.5: return 'WRONG LAND'
    if (m.get('ratio') or 0) > 1.25: return 'TOO BIG'
    if (m.get('covered') or 0) < 0.8: return 'MISSING PIECES'
    return 'GOOD'


def wilson(k, n, z=1.96):
    if not n: return (0.0, 0.0)
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; e = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - e), min(1.0, c + e))


# ------------------------------------------------------------------ files
def load_outlines(d, areas):
    out = {}
    for a in sorted(areas):
        for f in sorted(glob.glob(os.path.join(d, f'{a}.geojson.gz')) + glob.glob(os.path.join(d, f'{a}.p*.geojson.gz'))):
            for ft in (json.load(gzip.open(f, 'rt', encoding='utf-8')).get('features') or []):
                pr = ft.get('properties') or {}; r = pr.get('ref') or ft.get('ref')
                if r and ft.get('geometry'): out.setdefault(r, []).append(ft['geometry'])
    return {r: (g[0] if len(g) == 1 else {'type': 'GeometryCollection', 'geometries': g}) for r, g in out.items()}


def safe_name(ref): return ''.join(ch if ch.isalnum() or ch in '-_.' else '_' for ch in ref)


def load_trace(dirs, ref):
    for d in dirs:
        if not d: continue
        p = pathlib.Path(d) / f'{safe_name(ref)}.json'
        if p.exists():
            try:
                fc = json.loads(p.read_text(encoding='utf-8')); fs = fc.get('features') or []
                if fs and fs[0].get('geometry'): return fs[0]['geometry'], pathlib.Path(d).name
            except Exception: pass  # noqa: BLE001
    return None, None


def report_rows(d):
    p = pathlib.Path(d or '') / 'report.csv'
    return {r['ref']: r for r in csv.DictReader(open(p, encoding='utf-8'))} if d and p.exists() else {}


def pick(list_file, index_file, finder_log, out_file, per_class=10):
    """Walk the list in order; a park is picked when the finder found an official picture map for it AND the saver kept a map page
    (index.json row with files, page_pick.map_page_found not False); the first `per_class` per size class. Every other park walked
    is a result too (skipped + why). Filters index.json to the picked parks (the tracer traces only those). Returns the pick."""
    L = json.load(open(list_file, encoding='utf-8'))
    idx = json.load(open(index_file, encoding='utf-8')) if os.path.exists(index_file) else {'maps': []}
    maps = idx.get('maps') if isinstance(idx, dict) else idx
    have = {}
    for m in maps or []:
        if m.get('ref') and m.get('files') and (m.get('page_pick') or {}).get('map_page_found') is not False: have.setdefault(m['ref'], m)
    nomap = {m.get('ref'): (m.get('page_pick') or {}).get('why') or 'no map page in the document' for m in maps or [] if m.get('ref') and m['ref'] not in have}
    flog = {}
    try:
        for r in json.load(open(finder_log, encoding='utf-8')) or []:
            if isinstance(r, dict) and r.get('ref'): flog[r['ref']] = r
    except Exception: pass  # noqa: BLE001
    took = {'small': [], 'middle': [], 'large': []}; skipped = []; walked = 0
    for p in L['parks']:
        if all(len(v) >= per_class for v in took.values()): break
        if len(took.get(p['size'], [])) >= per_class: continue
        walked += 1
        if p['ref'] in have: took[p['size']].append(p['ref']); continue
        fl = flog.get(p['ref']) or {}
        why = nomap.get(p['ref']) or ('; '.join(str(x) for x in (fl.get('_log') or fl.get('log') or [])[-2:]) or 'the finder found no official picture map')
        skipped.append({'ref': p['ref'], 'size': p['size'], 'why': str(why)[:300]})
    picked = [r for p in L['parks'] for r in [p['ref']] if r in took.get(p['size'], [])]
    found = sum(len(v) for v in took.values())
    res = {'picked': picked, 'skipped': skipped, 'walked': walked, 'find_rate': f'{found} of {walked} parks walked ({found / walked:.0%})' if walked else '0 of 0',
           'per_class': {k: len(v) for k, v in took.items()}}
    json.dump(res, open(out_file, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    if isinstance(idx, dict): idx['maps'] = [m for m in maps if m.get('ref') in set(picked)]
    else: idx = [m for m in maps if m.get('ref') in set(picked)]
    json.dump(idx, open(index_file, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print(f"::notice title=T1 pick::{found} parks picked ({res['per_class']}); find rate {res['find_rate']}")
    return res


def blind(index_file):
    """The tracer gets the picture map and the pin, never the official outline or its acres: drop any size the prep put in."""
    d = json.load(open(index_file, encoding='utf-8')); n = 0
    for v in (d.values() if isinstance(d, dict) else d):
        if isinstance(v, dict):
            for k in ('acres', 'acres_known', 'official_acres'):
                if k in v: v.pop(k); n += 1
    json.dump(d, open(index_file, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print(f'::notice title=T1 blind::{n} size fields taken out of the tracer input')
    return n


def main(argv):
    if argv[:1] == ['pick']:
        ap = argparse.ArgumentParser(); ap.add_argument('cmd'); ap.add_argument('--list', required=True); ap.add_argument('--index', required=True)
        ap.add_argument('--finder-log', default=''); ap.add_argument('--out', required=True); ap.add_argument('--per-class', type=int, default=10)
        a = ap.parse_args(argv); pick(a.list, a.index, a.finder_log, a.out, a.per_class); return 0
    if argv[:1] == ['blind']:
        blind(argv[1]); return 0
    ap = argparse.ArgumentParser()
    ap.add_argument('--list', required=True); ap.add_argument('--picked', required=True); ap.add_argument('--traced', required=True)
    ap.add_argument('--unofficial'); ap.add_argument('--outlines', required=True); ap.add_argument('--out', required=True)
    a = ap.parse_args(argv)
    L = json.load(open(a.list, encoding='utf-8')); parks = {p['ref']: p for p in L['parks']}
    P = json.load(open(a.picked, encoding='utf-8'))
    rep = {**report_rows(a.unofficial), **report_rows(a.traced)}
    official = load_outlines(a.outlines, {parks[r]['area'] for r in P.get('picked') or [] if r in parks})
    out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True); rows = []
    for ref in P.get('picked') or []:
        p = parks.get(ref) or {'ref': ref}; rr = rep.get(ref) or {}
        g, where = load_trace([a.traced, a.unofficial], ref)
        m = measure(g, official.get(ref)) if g else {'failure': 'no trace' + (f" ({rr.get('status')}: {str(rr.get('why') or '')[:160]})" if rr else ' (the tracer wrote no row)')}
        if not g and rr and 'boundary' in str(rr.get('why') or '').lower(): m['failure'] = f"the map had no boundary the tracer could read ({str(rr.get('why'))[:160]})"
        rows.append({'order': p.get('order'), 'ref': ref, 'area': p.get('area'), 'name': p.get('name'), 'size': p.get('size'), 'agency': p.get('agency'),
                     'tracer_status': rr.get('status', ''), 'kept_by_tracer': where == pathlib.Path(a.traced).name,
                     **{k: m.get(k) for k in ('traced_acres', 'official_acres', 'ratio', 'covered', 'outside', 'line_mid_ft', 'line_worst10_ft', 'cell_m')},
                     'grade': grade(m), 'failure': m.get('failure', '')})
    keys = list(rows[0]) if rows else ['ref']
    with open(out / 't1-parks.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(rows)
    words = ['WRONG LAND', 'TOO BIG', 'MISSING PIECES', 'GOOD', 'FAILED']
    summ = {}
    for cls in ('small', 'middle', 'large', 'all'):
        rs = [r for r in rows if cls == 'all' or r['size'] == cls]; n = len(rs)
        summ[cls] = {'n': n, **{wd: {'k': sum(1 for r in rs if r['grade'] == wd), 'range': [round(x, 3) for x in wilson(sum(1 for r in rs if r['grade'] == wd), n)]} for wd in words}}
    res = {'picked': len(rows), 'skipped': P.get('skipped') or [], 'find_rate': P.get('find_rate'), 'summary': summ}
    json.dump(res, open(out / 't1-result.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    md = ['# T1 tracer accuracy test: result', '',
          f"Parks traced: {len(rows)} (list {a.list}). Skipped while walking the list: {len(P.get('skipped') or [])}"
          + (f"; picture-map find rate {P['find_rate']}" if P.get('find_rate') else '') + '.', '',
          'Grade words: WRONG LAND = most of the trace outside the official outline; TOO BIG = over 1.25 x the official acres; '
          'MISSING PIECES = covers under 0.8 of it; FAILED = no trace, no boundary on the map, or the wrong feature. Ranges are 95% (Wilson).', '',
          '| size | n | ' + ' | '.join(words) + ' |', '|---|---|' + '---|' * len(words)]
    for cls, s in summ.items():
        md.append(f"| {cls} | {s['n']} | " + ' | '.join(f"{s[wd]['k']} ({s[wd]['range'][0]:.0%}-{s[wd]['range'][1]:.0%})" for wd in words) + ' |')
    md += ['', 'Line distance (feet, traced line to official line), per size class: middle of the parks\' middles / worst tenth', '']
    for cls in ('small', 'middle', 'large'):
        mids = [r['line_mid_ft'] for r in rows if r['size'] == cls and r['line_mid_ft'] is not None]
        w10 = [r['line_worst10_ft'] for r in rows if r['size'] == cls and r['line_worst10_ft'] is not None]
        if mids: md.append(f"- {cls}: middle {round(pct(mids, 0.5))} ft (range {min(mids)}-{max(mids)}); worst tenth {round(pct(w10, 0.5))} ft (range {min(w10)}-{max(w10)})")
    md += ['', 'Every park: `t1-parks.csv`. Skipped parks and why: `t1-result.json` (skipped). Nothing here touches a map or a key.']
    (out / 't1-summary.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(f"::notice title=T1 measure::{len(rows)} parks: " + ', '.join(f"{wd} {summ['all'][wd]['k']}" for wd in words))
    return 0


def _selftest():
    sq = lambda x0, y0, s: {'type': 'Polygon', 'coordinates': [[[x0, y0], [x0 + s, y0], [x0 + s, y0 + s], [x0, y0 + s], [x0, y0]]]}
    ok = True
    def chk(c, w):
        nonlocal ok; print(('PASS ' if c else 'FAIL ') + w); ok = ok and c
    m = measure(sq(-85, 37, 0.01), sq(-85, 37, 0.01))
    chk(m['ratio'] == 1.0 and m['covered'] > 0.98 and m['outside'] < 0.02 and m['line_mid_ft'] == 0 and grade(m) == 'GOOD', f'the same square: GOOD {m}')
    m = measure(sq(-85, 37, 0.02), sq(-85, 37, 0.01))
    chk(3.9 < m['ratio'] < 4.1 and grade(m) == 'WRONG LAND', f'a trace 4x the park, 3/4 outside: WRONG LAND {m["ratio"]} {m["outside"]}')
    m = measure(sq(-85, 37, 0.011), sq(-85, 37, 0.01))
    chk(grade(m) == 'GOOD' and 1.15 < m['ratio'] < 1.25, f'a trace 1.21x: GOOD (not TOO BIG) {m["ratio"]}')
    m = measure(sq(-85, 37, 0.0115), sq(-85, 37, 0.01))
    chk(grade(m) == 'TOO BIG', f'a trace 1.32x: TOO BIG {m["ratio"]}')
    m = measure(sq(-85, 37, 0.008), sq(-85, 37, 0.01))
    chk(grade(m) == 'MISSING PIECES' and 0.6 < m['covered'] < 0.68, f'a trace covering 0.64: MISSING PIECES {m["covered"]}')
    m = measure(sq(-84.9, 37, 0.01), sq(-85, 37, 0.01))
    chk(grade(m) == 'FAILED' and 'wrong feature' in m['failure'], 'a trace with no overlap: the wrong feature')
    m = measure(sq(-85.0005, 37, 0.01), sq(-85, 37, 0.01))
    chk(100 < m['line_worst10_ft'] < 200, f"a trace 0.0005 deg (44 m = 146 ft) off to the west: worst tenth {m['line_worst10_ft']} ft")
    holed = {'type': 'Polygon', 'coordinates': [sq(-85, 37, 0.01)['coordinates'][0], [[-84.9975, 37.0025], [-84.9925, 37.0025], [-84.9925, 37.0075], [-84.9975, 37.0075], [-84.9975, 37.0025]]]}
    m = measure(sq(-85, 37, 0.01), holed)
    chk(1.3 < m['ratio'] < 1.36 and 0.22 < m['outside'] < 0.28, f'a hole in the official outline counts as outside {m["ratio"]} {m["outside"]}')
    chk(measure(None, sq(-85, 37, 0.01)).get('failure') == 'no trace', 'no trace: a failure')
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        lst = {'parks': [{'ref': f'US-{i}', 'size': ('small', 'middle', 'large')[i % 3], 'order': i + 1} for i in range(12)]}
        json.dump(lst, open(f'{td}/l.json', 'w'))
        json.dump({'maps': [{'ref': 'US-0', 'files': ['maps/a.jpg']}, {'ref': 'US-3', 'files': ['maps/b.jpg'], 'page_pick': {'map_page_found': False, 'why': 'cover only'}},
                            {'ref': 'US-6', 'files': ['maps/c.jpg']}, {'ref': 'US-1', 'files': ['maps/d.jpg'], 'acres': 5}, {'ref': 'US-9', 'files': ['maps/e.jpg']}]}, open(f'{td}/i.json', 'w'))
        r = pick(f'{td}/l.json', f'{td}/i.json', '', f'{td}/p.json', per_class=2)
        chk(r['picked'] == ['US-0', 'US-1', 'US-6'] and r['per_class'] == {'small': 2, 'middle': 1, 'large': 0}, f"pick walks in order, 2 per class: {r['picked']}")
        chk(any(x['ref'] == 'US-3' and 'cover only' in x['why'] for x in r['skipped']), 'a document with no map page is skipped, with its reason')
        chk([m['ref'] for m in json.load(open(f'{td}/i.json'))['maps']] == ['US-0', 'US-6', 'US-1'], 'the tracer input holds only the picked parks')
        json.dump({'US-1': {'name': 'x', 'acres': 5, 'type': 'State Park'}}, open(f'{td}/t.json', 'w')); blind(f'{td}/t.json')
        chk(json.load(open(f'{td}/t.json')) == {'US-1': {'name': 'x', 'type': 'State Park'}}, 'blind: the size is taken out, the park type stays')
    chk(wilson(0, 30)[1] > 0.1 and wilson(30, 30)[0] < 0.9, 'ranges, not single numbers')
    print('ALL PASS' if ok else 'SOME FAILED'); return 0 if ok else 1


if __name__ == '__main__':
    if '--selftest' in sys.argv[1:]: sys.exit(_selftest())
    sys.exit(main(sys.argv[1:]))
