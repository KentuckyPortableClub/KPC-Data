#!/usr/bin/env python3
"""POTA ACTIVITY, WHOLE WORLD (chat 10, Nov 1 2026; Brandon 7:59 PM: 'make the file download by country in rank of activity in
pota'). POTA's own public lists (api.pota.app /locations, then /location/parks/<location> for every location of every program,
the same calls kpc_state_links / kpc_northam already make) -> data/pota/activity.json {ref: [activations, attempts, location]}
(compact). Used to rank the 'parks still missing a boundary' lists (kpc_missing_lists.py) and any queue by activity.
A location that fails keeps last week's numbers. One request at a time, 0.5 s apart. Weekly. Never fails.
  python3 .github/scripts/kpc_pota_activity.py"""
import json, pathlib, time, urllib.request
import kpc_host_rules; kpc_host_rules.install()

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
    # Nov 11: a location that ANSWERED with an empty list (a 200 with nothing in it) is not a failure, so its parks used to lose their
    # numbers without a word. Same rule as the world POTA bot: a location of 10+ parks that came back under half its size keeps last week's
    # numbers, and a whole answer under 80% of last week's is refused (the file stays as it was, and the log says so).
    oc, nc = {}, {}
    for ref, v in old.items(): oc[v[2]] = oc.get(v[2], 0) + 1
    for ref, v in parks.items(): nc[v[2]] = nc.get(v[2], 0) + 1
    short = sorted(k for k, n in oc.items() if n >= 10 and nc.get(k, 0) < 0.5 * n)
    for ref, v in old.items():
        if ref not in parks and v[2] in short: parks[ref] = v
    if short: print(f'::notice title=POTA activity::{len(short)} location(s) came back much smaller: kept last week\'s numbers for {", ".join(short[:10])}')
    if len(old) >= 1000 and len(parks) < 0.8 * len(old):
        print(f'::warning title=POTA activity::only {len(parks)} parks read vs {len(old)} last week: the answer looks short. Nothing was changed; last week\'s file stays.'); return
    OUT.parent.mkdir(parents=True, exist_ok=True)
    json.dump({'about': 'POTA activations per park (api.pota.app location lists), weekly: {ref: [activations, attempts, location]}',
               'built': time.strftime('%Y-%m-%d'), 'parks': parks}, open(OUT, 'w'), separators=(',', ':'), ensure_ascii=False)
    print(f'::notice title=POTA activity::{len(parks)} parks from {len(set(locs))} locations ({len(failed)} failed, kept last week)')


if __name__ == '__main__':
    try: main()
    except Exception as e: print(f'::notice title=POTA activity::stopped ({type(e).__name__}: {e})')  # noqa: BLE001
