#!/usr/bin/env python3
"""POTA ACTIVITY, WHOLE WORLD (chat 10, Nov 1 2026; Brandon 7:59 PM: 'make the file download by country in rank of activity in
pota'). POTA's own public lists (api.pota.app /locations, then /location/parks/<location> for every location of every program,
the same calls kpc_state_links / kpc_northam already make) -> data/pota/activity.json {ref: [activations, attempts, location]}
(compact). Used to rank the 'parks still missing a boundary' lists (kpc_missing_lists.py) and any queue by activity.
A location that fails keeps last week's numbers. One request at a time, 0.5 s apart. Weekly. Never fails.
  python3 .github/scripts/kpc_pota_activity.py"""
import json, pathlib, time, urllib.request

OUT = pathlib.Path('data/pota/activity.json')
UA = 'KPC-Bot/1.0 (Kentucky Portable Club ham radio club; https://github.com/KentuckyPortableClub)'


def get(u):
    req = urllib.request.Request(u, headers={'User-Agent': UA, 'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=60) as r: return json.loads(r.read().decode('utf-8'))


def main():
    try: old = json.load(open(OUT)).get('parks') or {}
    except Exception: old = {}  # noqa: BLE001
    try: locs = [l['locationDesc'] for l in get('https://api.pota.app/locations') if l.get('locationDesc')]
    except Exception as e: print(f'::notice title=POTA activity::locations list failed ({e}): kept last week'); return
    parks, failed = {}, []
    for desc in sorted(set(locs)):
        try:
            for p in get(f'https://api.pota.app/location/parks/{desc}') or []:
                ref = p.get('reference')
                if ref: parks[ref] = [int(p.get('activations') or 0), int(p.get('attempts') or 0), p.get('locationDesc') or desc]
        except Exception: failed.append(desc)  # noqa: BLE001
        time.sleep(0.5)
    for ref, v in old.items():   # a location that failed keeps last week's numbers
        if ref not in parks and v[2] in failed: parks[ref] = v
    OUT.parent.mkdir(parents=True, exist_ok=True)
    json.dump({'about': 'POTA activations per park (api.pota.app location lists), weekly: {ref: [activations, attempts, location]}',
               'built': time.strftime('%Y-%m-%d'), 'parks': parks}, open(OUT, 'w'), separators=(',', ':'), ensure_ascii=False)
    print(f'::notice title=POTA activity::{len(parks)} parks from {len(set(locs))} locations ({len(failed)} failed, kept last week)')


if __name__ == '__main__':
    try: main()
    except Exception as e: print(f'::notice title=POTA activity::stopped ({type(e).__name__}: {e})')  # noqa: BLE001
