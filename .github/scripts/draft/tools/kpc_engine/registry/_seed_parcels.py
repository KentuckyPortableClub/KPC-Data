#!/usr/bin/env python3
"""Parcel layers for L5 (historic sites and small county / city parks), copied from the club's agency atlas
(tips/agency-atlas/<area>.md, section '## Parcel / ownership maps'). Only full layer URLs written in the notes are kept;
nothing is guessed. A parcel is never an outline: L5 reports it as a WEAK 'PARCEL lead' with its record number.

  python3 registry/_seed_parcels.py [--pack /workspace/pota/sources/sources]  -> registry/parcel_sources.json"""
import argparse, json, os, pathlib, re

HERE = pathlib.Path(__file__).resolve().parent
PROVS = {'AB', 'BC', 'MB', 'NB', 'NL', 'NS', 'NT', 'NU', 'ON', 'PE', 'QC', 'SK', 'YT'}
URL = re.compile(r'https?://[^\s)`\'"<>]+/rest/services/[^\s)`\'"<>]+/(?:MapServer|FeatureServer)/\d+')


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--pack', default=os.environ.get('KPC_SOURCES', '/workspace/pota/sources/sources'))
    a = ap.parse_args()
    out, seen = [], set()
    for f in sorted(pathlib.Path(a.pack, 'tips', 'agency-atlas').glob('*.md')):
        code = f.stem.split('-', 1)[1] if '-' in f.stem else f.stem
        area = ('CA-' if code in PROVS else 'US-') + code
        txt = f.read_text(encoding='utf-8', errors='replace')
        secs = [m.group(0) for m in re.finditer(r'^## Parcel / ownership maps.*?(?=^## |\Z)', txt, re.M | re.S)]
        for line in '\n'.join(secs).splitlines():
            for u in URL.findall(line):
                u = u.rstrip('.,;')
                if u.lower() in seen: continue
                seen.add(u.lower())
                out.append({'id': f'PARCEL-{area}-{len(out)}', 'area': area, 'cc': area[:2], 'use': 'parcel', 'kind': 'arcgis', 'url': u,
                            'geometry': 'polygon', 'grade': 'parcel', 'agency': '', 'official_basis': f'club agency atlas {f.name} (Parcel / ownership maps)',
                            'note': re.sub(r'\s+', ' ', line.strip())[:300],
                            'verified': {'status': 'club', 'why': f'listed in tips/agency-atlas/{f.name}', 'date': '2026-11-01'}})
    json.dump({'sources': out, 'about': __doc__}, open(HERE / 'parcel_sources.json', 'w'), indent=1, ensure_ascii=False)
    print(len(out), 'parcel layers:', sorted({s['area'] for s in out}))


if __name__ == '__main__':
    main()
