#!/usr/bin/env python3
"""PICTURE-MAP TRACER INPUT (chat 10, Nov 1 2026; Brandon 2:00 AM 'hook it up, lets see what 11 thinks'). Turns the picture-maps
branch (checked out at <base>: maps/<ref>_*.jpg + index.json {maps: [{ref, source_url, page: [n], files, agency, name}]}) into the
draft tracer's inputs in the same folder: index.json as a ref-keyed dict with name + agency + page filled in, and pins.json (POTA pins).
US + Canada only (the tracer's basemaps are TIGERweb / NHD / PLSS / the Canadian road network). Agency = the documents bot's agency
for that park, else the map file's own web host (the saver only keeps maps from the managing agency). Never fails.
  python3 kpc_picture_prep.py <base> <links dir>"""
import glob, json, os, pathlib, sys, urllib.parse

base, links = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])


def load(p, d):
    try: return json.load(open(p, encoding='utf-8'))
    except Exception: return d  # noqa: BLE001


idx = load(base / 'index.json', {}) or {}
rows = idx.get('maps') if isinstance(idx, dict) else idx
pins, names, ag = {}, {}, {}
for f in glob.glob('data/parkinfo/US-*.json'):
    for r, a in ((load(f, {}) or {}).get('parks') or {}).items(): pins[r] = [a[5], a[6]]; names[r] = a[0]
for r, a in ((load('data/parkinfo/CA.json', {}) or {}).get('parks') or {}).items(): pins[r] = [a[5], a[6]]; names[r] = a[0]
for p in (load(links / 'kpc-ky-data.json', {}) or {}).get('parks') or []:
    try: pins[p['c']] = [float(p['la']), float(p['lo'])]; names[p['c']] = p.get('n')
    except Exception: pass  # noqa: BLE001
acres = {}   # Nov 2 review: the club's official acres list (data/acres.json, kpc_acres: {ref: {acres, ...}} or {ref: acres})
_ad = load('data/acres.json', None) or load(os.environ.get('KPC_TRACE_ACRES_FILE') or '../out/acres/acres.json', {}) or {}   # main's list, else the acres bot's tools-out copy
_ad = _ad.get('parks', _ad) if isinstance(_ad, dict) else {}
for r, v in (_ad.items() if isinstance(_ad, dict) else []):
    try: a = float(v.get('acres') if isinstance(v, dict) else v)
    except (TypeError, ValueError): continue
    if a > 0: acres[r] = a
for f in glob.glob('data/docs/*.json'):
    for r, v in ((load(f, {}) or {}).get('parks') or {}).items():
        if isinstance(v, dict) and v.get('agency'): ag[r] = v['agency']
out, used = {}, {}
for m in rows or []:
    ref = m.get('ref') or ''
    if not ref.startswith(('US-', 'CA-')) or ref not in pins: continue
    files = [x for x in m.get('files') or [] if (base / x).exists()]
    if not files: continue
    pg = m.get('page'); pg = pg[0] if isinstance(pg, list) and pg else (pg or 1)
    out[ref] = {'name': m.get('name') or names.get(ref) or ref, 'agency': m.get('agency') or ag.get(ref) or urllib.parse.urlsplit(m.get('source_url') or '').hostname or '',
                'source_url': m.get('source_url'), 'page': pg, 'date': m.get('date'), 'source_type': 'official', 'image': files[0],
                'map_file': files[0][5:] if files[0].startswith('maps/') else files[0],   # Nov 2 review: the tracer reads map_file, never image
                **({'acres': acres[ref]} if acres.get(ref) else {})}   # Nov 2 review: the tracer's scale prior needs the size (0.2-25 m/px without it)
    used[ref] = pins[ref]
json.dump(out, open(base / 'index.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
json.dump(used, open(base / 'pins.json', 'w'), indent=0)
print(f'::notice title=Picture tracer input::{len(out)} US + Canada picture maps with a pin (of {len(rows or [])} saved)')
