#!/usr/bin/env python3
"""POTA ACTIVITY, WHOLE WORLD (chat 10, Nov 1 2026; Brandon 7:59 PM: 'make the file download by country in rank of activity in
pota'). POTA's own public lists (/locations, then /location/parks/<location> for every location of every program,
the same calls kpc_state_links / kpc_northam already make) -> data/pota/activity.json {ref: [activations, attempts, location]}
(compact). Used to rank the 'parks still missing a boundary' lists (kpc_missing_lists.py) and any queue by activity.
A location that fails keeps last week's numbers. Weekly. Never fails.
KPC owner, 2026-11-16 (handoff item 7, be polite to POTA): this script NEVER calls POTA. It reads the SAVED copy that the one
park-list job of KPC-Links (kpc_pota_parklists.py, through its POTA door) keeps in KPC-Links data/pota/saved: locations.json and
parks/<location>.json.gz. KPC_POTA_SAVED names that folder (the workflow checks out only that folder of the public KPC-Links).
A location with no saved list counts as failed (it keeps last week's numbers). v4 (Nov 16): the saved lists come from POTA's
all-parks export, which has no activation counts; a park whose saved row has none keeps last week's numbers (new parks: 0 until
the park-list job reads that location's own list).
  KPC_POTA_SAVED=links/data/pota/saved python3 .github/scripts/kpc_pota_activity.py"""
import gzip, json, os, pathlib, time

OUT = pathlib.Path('data/pota/activity.json')
SAVED = pathlib.Path(os.environ.get('KPC_POTA_SAVED') or 'links/data/pota/saved')


def saved_locations():
    return json.load(open(SAVED / 'locations.json', encoding='utf-8'))['data']


def saved_park_list(loc):
    with gzip.open(SAVED / 'parks' / f'{loc}.json.gz', 'rt', encoding='utf-8') as f: return json.load(f)['data']


def main():
    try: old = json.load(open(OUT)).get('parks') or {}
    except Exception: old = {}  # noqa: BLE001
    try: locs = [l['locationDesc'] for l in saved_locations() if l.get('locationDesc')]
    except Exception as e: print(f'::notice title=POTA activity::no saved locations list ({e}): kept last week'); return
    parks, failed, kept_n = {}, [], 0
    for desc in sorted(set(locs)):
        try:
            for p in saved_park_list(desc) or []:
                ref = p.get('reference')
                if not ref: continue
                if 'activations' not in p and 'attempts' not in p:   # v4: a list rewritten from the all-parks export has no counts yet
                    o = old.get(ref)
                    parks[ref] = [o[0], o[1], p.get('locationDesc') or desc] if o else [0, 0, p.get('locationDesc') or desc]; kept_n += 1
                    continue
                parks[ref] = [int(p.get('activations') or 0), int(p.get('attempts') or 0), p.get('locationDesc') or desc]
        except Exception: failed.append(desc)  # noqa: BLE001
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
    json.dump({'about': 'POTA activations per park (POTA\'s location lists, the club\'s saved copy), weekly: {ref: [activations, attempts, location]}',
               'built': time.strftime('%Y-%m-%d'), 'parks': parks}, open(OUT, 'w'), separators=(',', ':'), ensure_ascii=False)
    print(f'::notice title=POTA activity::{len(parks)} parks from {len(set(locs))} locations ({len(failed)} failed, kept last week;'
          f' {kept_n} parks had no counts in the saved list and kept last week\'s numbers)')


if __name__ == '__main__':
    try: main()
    except Exception as e: print(f'::notice title=POTA activity::stopped ({type(e).__name__}: {e})')  # noqa: BLE001
