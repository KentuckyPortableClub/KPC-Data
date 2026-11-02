#!/usr/bin/env python3
"""NEW-PARK PIPELINE (chat 10, Oct 30 2026; HQ 7:40 AM (b), Brandon 7:31 AM 'do it all'). Run by the daily copy (after kpc-new-refs).
For each new US / CA park in KPC-Links kpc-new-refs.json (POTA only) that the key still leaves WITHOUT an official outline, ONCE:
  - its area goes on the GIS hunter's list for one areas-run (the hunter's logic is untouched: Brandon's hold to Nov 6);
  - one look-up 'page' request reads its POTA record (website + agency) for the chats; the answer lands on the lookup branch.
The Fable-book row (fable/US-XX.md, why-not 'new park, no outline yet') is written on the KPC-Links side by kpc-new-refs.yml.
Remembers what it handled in data/gis-hunter/new-parks.json. Prints AREAS=<areas> for the workflow. Never posts, never fails.
  LINKS=links LOOKUP_ROOT=lk python3 kpc_new_park_flow.py"""
import glob, json, os, pathlib, sys, time

L = pathlib.Path(os.environ.get('LINKS') or '../links')
LK = pathlib.Path(os.environ.get('LOOKUP_ROOT') or 'lk')
SEEN = pathlib.Path('data/gis-hunter/new-parks.json')


def load(p, d=None):
    try: return json.load(open(p, encoding='utf-8'))
    except Exception: return d  # noqa: BLE001


def main():
    items = (load(L / 'kpc-new-refs.json', {}) or {}).get('items') or []
    seen = load(SEEN, {}) or {}
    grade, area_of = {}, {}
    for f in glob.glob(str(L / 'data' / 'us-key' / 'US-*.json')) + glob.glob(str(L / 'data' / 'ca-key' / 'CA-*.json')):
        a = pathlib.Path(f).stem
        for r, v in ((load(f, {}) or {}).get('parks') or {}).items():
            grade[r] = (v or {}).get('g') if isinstance(v, dict) else None; area_of[r] = a
    areas, filed = set(), 0
    for it in items:
        r = it.get('ref') or ''
        if it.get('prog') != 'pota' or not r.startswith(('US-', 'CA-')) or r in seen: continue
        st = (it.get('st') or [''])[0]
        area = area_of.get(r) or (f'US-{st}' if r.startswith('US-') and st else '')
        if area == 'US-KY': seen[r] = {'date': time.strftime('%Y-%m-%d'), 'did': 'Kentucky: its own key'}; continue
        if grade.get(r) == 'official': seen[r] = {'date': time.strftime('%Y-%m-%d'), 'did': 'already outlined'}; continue
        did = []
        if area: areas.add(area); did.append(f'hunter {area}')
        if (LK / 'requests').exists():
            json.dump({'chat': 10, 'kind': 'page', 'urls': [f'https://api.pota.app/park/{r}'],
                       'report': f"new park {r} {it.get('name', '')}: its POTA record (website + agency) for the Fable book row"},
                      open(LK / 'requests' / f'10-new-{r}.json', 'w'), indent=1)
            did.append('look-up page'); filed += 1
        seen[r] = {'date': time.strftime('%Y-%m-%d'), 'name': it.get('name'), 'area': area, 'did': ', '.join(did)}
    SEEN.parent.mkdir(parents=True, exist_ok=True)
    json.dump(seen, open(SEEN, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print(f'::notice title=New parks::{len(areas)} areas for the hunter, {filed} look-up reads filed')
    print('AREAS=' + ' '.join(sorted(areas)))


if __name__ == '__main__':
    try: main()
    except Exception as e: print(f'::notice title=New parks::stopped ({type(e).__name__}: {e})')  # noqa: BLE001
    sys.exit(0)
