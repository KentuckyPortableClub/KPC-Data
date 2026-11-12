#!/usr/bin/env python3
"""WIRED TRAIL LINES -> TRAIL BOT (Nov 7 2026; Brandon 9 PM CST: 'build the rest of it so that dont get forgot about').
Turns data/waiting/outline-sources/trail-lines-wired-nov7.csv (reviewed trail-match lines) into kpc_us_trails.py EXTRA_TRAILS rows
{ref, name, url, layer, where, bbox, by, kind} and appends them to the given JSON list (the kpc_finds_lines.py output), so the weekly
trail bot draws them into data/trails/ like every other trail line. The where filter names the exact feature and the bbox (0.3 deg
around the POTA pin) keeps a same-named line elsewhere out.

File-based wires (layer_url starts with file:) are official extracts already stored in the repo (USGS NTD / FS download /
municipal GeoJSON). They are NOT handed to the ArcGIS fetcher (that would hit a blocked host or a fake URL). Use
  python3 kpc_wired_trails.py --install-files
AFTER kpc_us_trails.py so a weekly trail-bot run that rewrites data/trails/index.json puts those extracts back.

Canada parks CA-5506 and CA-5993 have no pin in the US parks file: the exact name filter alone is handed to the national
trail bot (there is no separate Data-side CA trails workflow; the state-trails CANADA path reads trails-hand.json in Links).

Offline; never fails the job. Not a key rule file (rules hashes unchanged).
  python3 kpc_wired_trails.py /tmp/finds-lines.json
  python3 kpc_wired_trails.py --install-files"""
import csv, gzip, json, os, pathlib, sys

ROOT = pathlib.Path(os.environ.get('DATA') or pathlib.Path(__file__).resolve().parents[2])
WIRED = ROOT / 'data/waiting/outline-sources/trail-lines-wired-nov7.csv'
PARKS = ROOT / '.github/scripts/draft/tools/kpc_layers_nov7/inputs/kpc-pota-trail-parks-no-outline-nov7.csv'
PAD = 0.3


def wired_rows():
    return list(csv.DictReader(open(WIRED, encoding='utf-8')))


def is_arcgis(w):
    u = (w.get('layer_url') or '').rstrip('/')
    return u.startswith('https://') and u.rsplit('/', 1)[-1].isdigit()


def is_file(w):
    return (w.get('layer_url') or '').startswith('file:')


def rows():
    """ArcGIS EXTRA_TRAILS rows only (file-based extracts are installed separately)."""
    pins = {p['ref']: p for p in csv.DictReader(open(PARKS, encoding='utf-8'))}
    out = []
    for w in wired_rows():
        if not is_arcgis(w):
            continue
        svc, _, lid = w['layer_url'].rstrip('/').rpartition('/')
        p = pins.get(w['ref']) or {}
        feat = (w.get('feature') or '').split(' (')[0] if w.get('ref') in {'US-9681', 'US-10426'} else w.get('feature') or ''
        # ArDOT feature names are exact; others that we still fetch are exact too (original 12)
        feat = w['feature'] if is_arcgis(w) else feat
        r = {'ref': w['ref'], 'name': w['park'], 'url': svc, 'layer': int(lid),
             'where': f"{w['name_field']} = '{feat.replace(chr(39), chr(39) * 2)}'",
             'by': w.get('by') or f"trail match Nov 7 (reviewed): {w['feature']}", 'kind': w.get('kind') or 'trail'}
        try:
            la, lo = float(p['lat']), float(p['lon'])
            r['bbox'] = [round(lo - PAD, 4), round(la - PAD, 4), round(lo + PAD, 4), round(la + PAD, 4)]
        except Exception: pass  # noqa: BLE001  (Canada rows have no pin in the file: the exact name filter alone)
        out.append(r)
    return out


def _lines_of(g):
    if not g: return []
    t, c = g.get('type'), g.get('coordinates') or []
    if t == 'LineString': return [c]
    if t == 'MultiLineString': return c
    return []


def install_files(trails_dir=None):
    """Copy file-based wired extracts into data/trails and merge them into index.json (or index-state.json for WSR)."""
    cwd_trails = pathlib.Path(trails_dir or 'data/trails')
    if not cwd_trails.exists():
        cwd_trails = ROOT / 'data/trails'
    n = 0
    for w in wired_rows():
        if not is_file(w):
            continue
        rel = w['layer_url'][5:]  # strip file:
        src = ROOT / rel
        if not src.exists():
            src = pathlib.Path(rel)
        if not src.exists():
            print(f'::warning title=kpc_wired_trails::intake missing for {w["ref"]}: {rel}')
            continue
        raw = gzip.open(src).read() if src.suffix == '.gz' or str(src).endswith('.gz') else src.read_bytes()
        doc = json.loads(raw)
        if doc.get('type') == 'FeatureCollection':
            lines = []
            for f in doc.get('features') or []:
                lines.extend(_lines_of((f or {}).get('geometry') or {}))
            geo = {'type': 'Feature', 'properties': {'ref': w['ref'], 'name': w['park']},
                   'geometry': {'type': 'MultiLineString', 'coordinates': lines}}
        else:
            geo = doc
            lines = _lines_of(geo.get('geometry') or {})
            geo.setdefault('properties', {})
            geo['properties']['ref'] = w['ref']
            geo['properties']['name'] = w['park']
        if not lines:
            print(f'::warning title=kpc_wired_trails::no lines in {w["ref"]}')
            continue
        cwd_trails.mkdir(parents=True, exist_ok=True)
        dest = cwd_trails / f'{w["ref"]}.json'
        dest.write_text(json.dumps(geo, separators=(',', ':')))
        xs = [p[0] for ln in lines for p in ln]; ys = [p[1] for ln in lines for p in ln]
        bb = [round(min(xs), 4), round(min(ys), 4), round(max(xs), 4), round(max(ys), 4)]
        entry = {'ref': w['ref'], 'name': w['park'], 'kind': w.get('kind') or 'trail',
                 'bbox': bb, 'by': w.get('by') or f"reviewed file extract Nov 7: {w['feature']}",
                 'kb': dest.stat().st_size // 1024}
        # Nov 11 (KPC owner, 2026-11-11): a Canadian trail line goes to index-state.json too (official: true): the CA key reads only
        # index-state.json for trail lines (kpc_ca_key.py _CTRL), so a CA row in index.json alone stayed a pin (CA-5506)
        idx_name = 'index-state.json' if (w.get('kind') or '') == 'WSR' or str(w.get('ref') or '').startswith('CA-') else 'index.json'
        idx_path = cwd_trails / idx_name
        try: idx = {x['ref']: x for x in json.loads(idx_path.read_text())}
        except Exception: idx = {}  # noqa: BLE001
        if idx_name == 'index-state.json':
            entry.update({'official': True, 'source': 'official', 'km': entry.get('km'),
                          'st': (w.get('state') or '').replace('US-', ''), 'type': ''})
        idx[w['ref']] = {**idx.get(w['ref'], {}), **entry}
        out = sorted(idx.values(), key=lambda r: r.get('name') or r['ref'])
        idx_path.write_text(json.dumps(out, indent=0) + '\n')
        n += 1
    print(f'wired file extracts: {n} installed into {cwd_trails}')
    return n


if __name__ == '__main__':
    try:
        if '--install-files' in sys.argv:
            install_files()
        else:
            path = next((a for a in sys.argv[1:] if not a.startswith('-')), '/tmp/finds-lines.json')
            try: have = json.load(open(path))
            except Exception: have = []  # noqa: BLE001
            refs = {x.get('ref') for x in have}
            add = [r for r in rows() if r['ref'] not in refs]
            with open(path, 'w', newline='') as f: json.dump(have + add, f, indent=0)
            print(f'wired trail lines: {len(add)} added to {path}')
    except Exception as e:  # noqa: BLE001
        print(f'::warning title=kpc_wired_trails::not added: {e}')
