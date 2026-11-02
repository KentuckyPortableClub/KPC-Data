#!/usr/bin/env python3
"""FETCH BOUNDARY FILES BY THEIR LINK (chat 10, Nov 1 2026; Brandon 8:59 PM sent links-pl.csv: Poland's GDOS shape zips sit on
www.gov.pl/attachment/<id>, a plain download a bot may take; the sdi.gdos.gov.pl WFS copy has a robot check, never bypassed).
A person (or a research chat) drops fetch-<name>.json on KPC-Data's intake-files branch:
  {"items": [{"url": "https://...zip", "area": "PL", "name": "parki-narodowe", "agency": "GDOS", "note": "..."}]}
This bot downloads each one ONCE (kpc_manners: robots.txt obeyed, slow per host; a 403 / robot check / sign-in is reported, never
bypassed), converts it with kpc_handfile_convert (shapefile / GeoJSON / KML / ArcGIS JSON, any Transverse Mercator grid -> GPS,
2 m simplify) into file-<area>-<name>-*.geojson.gz in OUTDIR; the workflow puts those on intake-files, where the layer
collector's hand-file pass matches them at the POTA pins (SURE -> AUTO-1C, LIKELY -> chat 11). A link fetched before with the
same size is skipped (data/intake/fetch-seen.json). Never fails.
  python3 .github/scripts/kpc_fetch_files.py <fetch-*.json ...> OUTDIR"""
import json, os, pathlib, sys, time

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from kpc_manners import Manners  # noqa: E402
import kpc_handfile_convert as HC  # noqa: E402

M = Manners('KPC boundary-file fetch (chat 10): one download per published file', read_max=400_000_000)
SEEN = pathlib.Path('data/intake/fetch-seen.json')


def main():
    *lists, outdir = sys.argv[1:]
    out = pathlib.Path(outdir); out.mkdir(parents=True, exist_ok=True)
    tmp = pathlib.Path('data/intake/_fetch'); tmp.mkdir(parents=True, exist_ok=True)
    try: seen = json.load(open(SEEN))
    except Exception: seen = {}  # noqa: BLE001
    done = []
    for f in lists:
        try: items = (json.load(open(f, encoding='utf-8')) or {}).get('items') or []
        except Exception as e: print(f'::notice title=Fetch files::{f}: not read ({e})'); continue  # noqa: BLE001
        for it in items:
            u, area, name = it.get('url'), it.get('area'), it.get('name')
            if not (u and area and name): continue
            if u in seen and not os.environ.get('REFRESH'): continue   # daily runs take only new links; the monthly run (REFRESH=1) looks for newer files
            st, hd, body, final = M.get(u, timeout=600, accept='application/zip,application/octet-stream,*/*')
            if not (isinstance(st, int) and st < 400 and body):
                done.append(f'{area} {name}: no file ({st}{": refused, not bypassed" if st == 403 else ""})'); continue
            if b'<html' in body[:600].lower():
                done.append(f'{area} {name}: a web page came back, not a file (a person opens it)'); continue
            key = f'{u}|{len(body)}'
            if seen.get(u) == key: done.append(f'{area} {name}: same file as before, skipped'); continue
            p = tmp / f'{name}.zip'; p.write_bytes(body)
            try:
                made = HC.convert(p, area, out, name)
                done.append(f'{area} {name}: {len(body) // 1_000_000} MB -> ' + ', '.join(f'{b} areas' for a, b, _ in made))
                seen[u] = key
            except Exception as e: done.append(f'{area} {name}: not converted ({type(e).__name__}: {e})')  # noqa: BLE001
            p.unlink(missing_ok=True)
            time.sleep(3)
    json.dump(seen, open(SEEN, 'w'), indent=1)
    print('::notice title=Fetch files::' + ('; '.join(done) or 'nothing to fetch')[:900], flush=True)


if __name__ == '__main__':
    try: main()
    except Exception as e: print(f'::notice title=Fetch files::stopped ({type(e).__name__}: {e})')  # noqa: BLE001
