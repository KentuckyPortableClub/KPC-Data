#!/usr/bin/env python3
"""Nov 13 (KPC owner): after a 2-fer line run, before the files are diverted to the waiting room.

  * Every live pair that disappeared gets a dropped or not-sure row with a reason (never a silent '(gone)').
  * A US trail line must not pair on Canadian ground: those rows are marked not sure (or dropped).

  python3 kpc_fers_annotate.py --new DIR --live DIR [--states 'CA-AB CA-SK']
The new files are updated in place. Offline, never fails a run on a read error of one file (that file is left, others go on).
"""
import argparse, json, gzip, os, pathlib, re, sys, time

LIVE = ('candidate', 'very tight', 'water only')
KNOWN = {
    'CA-0109+CA-0691': 'dropped: CA-0109 is a key pin (pin_may_be_wrong) and CA-0691 is not in the CA key',
    'CA-1182+CA-3063': 'not sure: same-land pair vanished; the ids registry still lists it and the key outlines did not change',
    'CA-2956+CA-2957': 'not sure: same-land pair vanished; the ids registry still lists it and the key outlines did not change',
    'CA-2957+CA-2958': 'not sure: same-land pair vanished; the ids registry still lists it and the key outlines did not change',
}
TRAIL_KIND = {'trail', 'line', 'path', 'nst', 'nsb'}


def load(p):
    p = pathlib.Path(p)
    for q in ((p, p.with_suffix(p.suffix + '.gz')) if p.suffix != '.gz' else (p, pathlib.Path(str(p)[:-3]))):
        if not q.is_file(): continue
        try:
            return json.loads(gzip.open(q, 'rt', encoding='utf-8').read() if q.suffix == '.gz' or str(q).endswith('.json.gz') else q.read_text(encoding='utf-8')), q
        except (OSError, ValueError): continue
    return None, p


def save(path, doc):
    path = pathlib.Path(path)
    text = json.dumps(doc, ensure_ascii=False, indent=0) + '\n'
    if str(path).endswith('.gz'):
        path.write_bytes(gzip.compress(text.encode('utf-8'), 9))
    else:
        path.write_text(text, encoding='utf-8')


def pair_key(refs):
    return '+'.join(sorted(map(str, refs or [])))


def pairs_of(doc, live_only=False):
    out = {}
    for s in (doc or {}).get('spots') or []:
        if not isinstance(s, dict): continue
        k = pair_key(s.get('refs') or [])
        if len((s.get('refs') or [])) < 2: continue
        if live_only and not str(s.get('status') or '').startswith(LIVE): continue
        out.setdefault(k, []).append(s)
    return out


def has_row(rows):
    return any(not str(s.get('status') or '').startswith('gone') for s in rows)


def _links_root():
    env = os.environ.get('LINKS') or os.environ.get('RELEASED_KEYS') or ''
    if env: return pathlib.Path(env)
    here = pathlib.Path(__file__).resolve()
    for cand in (here.parents[3] / 'KPC-Links', here.parents[2] / 'links', pathlib.Path('/workspace/KPC-Links')):
        if (cand / 'kpc-us-states.json').is_file():
            return cand
    return None


_US_LAND = None  # list of polygons (list of rings of [lon, lat]); loaded once


def us_land_polygons(links=None):
    """Union of land polygons in Links kpc-us-states.json (field p, including AK). Cached."""
    global _US_LAND
    if _US_LAND is not None:
        return _US_LAND
    root = pathlib.Path(links) if links else _links_root()
    path = (root / 'kpc-us-states.json') if root else None
    out = []
    if path and path.is_file():
        try:
            doc = json.loads(path.read_text(encoding='utf-8'))
        except (ValueError, OSError):
            doc = []
        for st in doc if isinstance(doc, list) else []:
            for poly in (st.get('p') or []) if isinstance(st, dict) else []:
                if isinstance(poly, list) and poly:
                    out.append(poly)
    _US_LAND = out
    return _US_LAND


def _pt_in_ring(lon, lat, ring):
    """Even-odd ray test. ring is [[lon, lat], ...]."""
    n = len(ring)
    if n < 3: return False
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = ring[i][0], ring[i][1]
        xj, yj = ring[j][0], ring[j][1]
        if (yi > lat) != (yj > lat):
            xint = (xj - xi) * (lat - yi) / ((yj - yi) or 1e-21) + xi
            if lon < xint:
                inside = not inside
        j = i
    return inside


def pt_on_us_land(lat, lon, links=None):
    """True when (lat, lon) is inside a US land polygon (AK included). Tries lon and lon±360 for the AK wrap."""
    polys = us_land_polygons(links)
    if not polys:
        return False
    for lo in (lon, lon - 360.0, lon + 360.0):
        for poly in polys:
            outer = poly[0] if poly else None
            if not outer or not _pt_in_ring(lo, lat, outer):
                continue
            if any(_pt_in_ring(lo, lat, hole) for hole in poly[1:]):
                continue
            return True
    return False


def _coords_of_spot(s):
    """(lat, lon) samples for the spot: the center plus vertices of a line/shape, if any."""
    out = []
    c = s.get('center') or s.get('ll')
    if isinstance(c, (list, tuple)) and len(c) >= 2:
        try: out.append((float(c[0]), float(c[1])))
        except (TypeError, ValueError): pass
    shape = s.get('shape') or s.get('line') or s.get('path')
    def walk(x):
        if isinstance(x, (list, tuple)) and len(x) >= 2 and isinstance(x[0], (int, float)):
            # [lat, lon] (same order as center) or [lon, lat] if |x[0]| > 90 and |x[1]| <= 90
            a, b = float(x[0]), float(x[1])
            if abs(a) <= 90 and abs(b) <= 180:
                out.append((a, b))
            elif abs(b) <= 90 and abs(a) <= 180:
                out.append((b, a))
            return
        if isinstance(x, (list, tuple)):
            for y in x:
                walk(y)
        elif isinstance(x, dict):
            walk(x.get('coordinates') or x.get('paths') or x.get('rings'))
    if shape is not None:
        try: walk(shape)
        except (TypeError, ValueError): pass
    return out


def us_trail_on_canada(s, links=None):
    """True when a CA+US trail has a part that is not on US land after clipping to kpc-us-states.json polygons.
    AK in-polygon stays US; eastern Canada below 49 that is outside US land is Canadian. Latitude 49 is not the border."""
    refs = [str(r) for r in (s.get('refs') or [])]
    has_ca = any(r.startswith('CA-') for r in refs)
    has_us = any(r.startswith('US-') for r in refs)
    if not (has_ca and has_us): return False
    ground = str(s.get('ground') or s.get('land') or '').lower()
    if ground in ('canada', 'ca', 'canadian'): return True
    kind = str(s.get('kind') or '').lower()
    blob = ' '.join(str(s.get(k) or '') for k in ('kind', 'name', 'trail', 'line', 'src', 'source', 'tier', 'about', 'note'))
    is_trail = kind in TRAIL_KIND or re.search(r'\b(trail|nst|nsb|cdt|continental divide)\b', blob, re.I)
    if not is_trail: return False
    pts = _coords_of_spot(s)
    if not pts:
        return False
    # clip: any sample that is not on US land means a Canadian remainder
    return any(not pt_on_us_land(lat, lon, links) for lat, lon in pts)


def gone_row(key, live_s, reason):
    refs = key.split('+')
    src = live_s or {}
    status = reason if reason.startswith(('dropped', 'not sure')) else 'dropped: ' + reason
    return {
        'id': src.get('id') or (key + '@dropped'),
        'kind': src.get('kind') or 'area',
        'refs': refs,
        'status': status,
        'reason': reason,
        'passes': src.get('passes') if isinstance(src.get('passes'), list) and len(src.get('passes') or []) >= 3 else [1, 1, 1],
        'center': src.get('center'),
        'found': src.get('found') or time.strftime('%Y-%m-%d'),
        'note': 'written by kpc_fers_annotate.py so a live pair is never silently gone',
    }


def annotate_doc(new, live, area=''):
    """Mutate new. Return {added: n, demoted: n, gone_left: n}."""
    if not isinstance(new, dict): return {'added': 0, 'demoted': 0, 'gone_left': 0}
    new.setdefault('spots', [])
    np_, op = pairs_of(new), pairs_of(live, live_only=True)
    added = demoted = 0
    for k, rows in list(pairs_of(new).items()):
        for s in rows:
            if us_trail_on_canada(s) and str(s.get('status') or '').startswith(LIVE + ('not sure',)):
                if str(s.get('status') or '').startswith(LIVE):
                    s['status'] = 'not sure: US trail line on Canadian ground (US designation does not apply in Canada)'
                    s['reason'] = s['status']
                    demoted += 1
    np_ = pairs_of(new)
    for k, live_rows in op.items():
        if has_row(np_.get(k) or []): continue
        reason = KNOWN.get(k) or 'dropped: live pair is gone and the line run wrote no row'
        new['spots'].append(gone_row(k, live_rows[0], reason))
        added += 1
    np_ = pairs_of(new)
    gone_left = sum(1 for k, live_rows in op.items() if not has_row(np_.get(k) or []))
    return {'added': added, 'demoted': demoted, 'gone_left': gone_left, 'area': area}


def iter_areas(new_dir, states):
    root = pathlib.Path(new_dir)
    if states:
        names = states.replace(',', ' ').split()
        for n in names:
            for f in (root / f'{n}.json', root / f'{n}.json.gz'):
                if f.is_file():
                    yield n, f
                    break
        return
    for f in sorted(root.glob('US-*.json')) + sorted(root.glob('US-*.json.gz')) + sorted(root.glob('CA-*.json')) + sorted(root.glob('CA-*.json.gz')):
        if f.name.endswith('.json.gz'):
            yield f.name[:-8], f
        else:
            yield f.stem, f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--new', required=True, help='folder of the new area files (e.g. data/fers)')
    ap.add_argument('--live', required=True, help='KPC-Data root whose data/fers is the live copy')
    ap.add_argument('--states', default='')
    a = ap.parse_args()
    live_root = pathlib.Path(a.live) / 'data' / 'fers'
    n_add = n_dem = 0
    for area, path in iter_areas(a.new, a.states):
        new, src = load(path)
        live, _ = load(live_root / f'{area}.json')
        r = annotate_doc(new or {}, live or {}, area)
        if new is not None and (r['added'] or r['demoted']):
            save(src, new)
        n_add += r['added']; n_dem += r['demoted']
        if r['added'] or r['demoted']:
            print(f"::notice title=2-fer annotate::{area}: wrote {r['added']} dropped/not-sure row(s), demoted {r['demoted']} US-trail-on-Canada row(s)")
    print(f"::notice title=2-fer annotate::{n_add} dropped/not-sure row(s) written, {n_dem} US-trail-on-Canada row(s) demoted")
    return 0


if __name__ == '__main__':
    sys.exit(main())
