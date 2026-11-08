#!/usr/bin/env python3
"""PARKS STILL MISSING A BOUNDARY, ONE LIST PER COUNTRY, MOST ACTIVATED FIRST (chat 10, Nov 1 2026; Brandon 7:59 PM: 'show the
world in other tabs ... download csv for the parks needed ... by country in rank of activity in pota'). Runs right after the
nightly scoreboard bot, from the same facts:
  US + Canada  data/review/scoreboard-parks.json rows with outline 'miss' (the scoreboard's own decision: pin-only and line parks
               are not missing)
  the world    every POTA program in data/pota/index.json; its parks from the POTA tiles; the outline from data/world-key/<CC>.json
               (the scoreboard's outline_kind) when that country has a key, else 'no boundary search done yet'
  activity     data/pota/activity.json (kpc_pota_activity.py, weekly)
Writes data/review/missing/index.json (one row per country: parks, missing, activations of the missing parks; most activity first)
and data/review/missing/<CC>.json ({cols, rows}: ref, name, area, type, activations, attempts, lat, lon, why), the members-only
Map Coverage page turns a country's rows into a CSV. Facts only; never fails.
  python3 .github/scripts/kpc_missing_lists.py          env LINKS (KPC-Links checkout)"""
import collections, glob, json, os, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import kpc_scoreboard_bot as S  # noqa: E402
import kpc_outline_ledger as OL  # noqa: E402  (Nov 7: parks already searched for an outline)

OUT = pathlib.Path(os.environ.get('MISSING_OUT') or 'data/review/missing')   # the nightly job writes to the orphan branch 'missing-lists' (no history kept)
COLS = ['ref', 'name', 'area', 'type', 'activations', 'attempts', 'lat', 'lon', 'why']


def load(p, d):
    try: return json.load(open(p, encoding='utf-8'))
    except Exception: return d  # noqa: BLE001


def main():
    ACT = (load('data/pota/activity.json', {}) or {}).get('parks') or {}
    pins = {}
    for f in glob.glob('data/pota/t/*.json'):
        for r in load(f, []) or []:
            if isinstance(r, list) and len(r) >= 4: pins[r[0]] = (r[1], r[2], r[3])
    for f in glob.glob('data/parkinfo/US-*.json'):   # US pins (the tiles hold the rest of the world)
        for r, v in ((load(f, {}) or {}).get('parks') or {}).items():
            if len(v) > 6 and v[5] is not None: pins.setdefault(r, (v[0], v[5], v[6]))
    for r in (load('data/canada.json', {}) or {}).get('rows') or []:
        if len(r) > 4 and r[0] == 'POTA': pins.setdefault(r[1], (r[2], r[3], r[4]))
    names = {**S.COUNTRY, 'US': 'United States', 'CA': 'Canada'}
    lists = collections.defaultdict(list); totals = collections.Counter()
    # ---- US + Canada: the scoreboard's own park rows
    SB = load('data/review/scoreboard-parks.json', {}) or {}
    LED = OL.load()
    types = SB.get('types') or []
    for ref, v in (SB.get('parks') or {}).items():
        cc = ref.split('-')[0]
        if v.get('o') != 'miss': continue
        t = types[v['t']] if isinstance(v.get('t'), int) and v['t'] < len(types) else (v.get('t') or '')
        a = ACT.get(ref) or [0, 0, '']; p = pins.get(ref) or ('', None, None)
        why = {'no layer': 'no official layer found yet', 'likely name mismatch': 'a near miss: likely a name mismatch'}.get(v.get('status'), 'no official boundary yet')
        if v.get('near_miss'): why += f" (near miss: {v['near_miss']})"
        # Nov 7 (Brandon 7:30 PM CST: 'no reason to look for same park over and over'): say when the park was already searched
        if OL.rows_for(ref, LED): why += ' · already searched: ' + OL.verdict(ref, LED) + ('' if OL.needs_search(ref, LED) else ' (skip)')
        lists[cc].append([ref, v.get('n') or p[0], v.get('a') or '', t, a[0], a[1], p[1], p[2], why])
    for c in ('US', 'CA'): totals[c] = sum(1 for r in (SB.get('parks') or {}) if r.startswith(c + '-'))
    # ---- the world
    programs = (load('data/pota/index.json', {}) or {}).get('programs') or {}
    retired = set((load(pathlib.Path(os.environ.get('LINKS') or '../links') / 'data/retired-refs.json', {}) or {}).get('refs') or {})
    for cc in sorted(programs):
        if cc in ('US', 'CA'): continue
        key = (load(f'data/world-key/{cc}.json', {}) or {}).get('parks') or {}
        refs = [r for r in pins if r.startswith(cc + '-') and r not in retired]
        totals[cc] = len(refs)
        for ref in refs:
            p = key.get(ref)
            if p is not None:
                k = S.outline_kind(p)[0]
                if k != 'missing': continue
                why, t = 'no official boundary yet', p.get('t') or ''
            else: why, t = 'no boundary search done yet' if not key else 'not in the country key yet', ''
            a = ACT.get(ref) or [0, 0, '']; pn = pins.get(ref) or ('', None, None)
            lists[cc].append([ref, pn[0], a[2] or cc, t, a[0], a[1], pn[1], pn[2], why])
    OUT.mkdir(parents=True, exist_ok=True)
    idx = []
    for cc, rows in lists.items():
        rows.sort(key=lambda r: (-(r[4] or 0), -(r[5] or 0), r[0]))
        json.dump({'country': cc, 'name': names.get(cc, cc), 'cols': COLS, 'rows': rows},
                  open(OUT / f'{cc}.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
        idx.append({'cc': cc, 'name': names.get(cc, cc), 'parks': totals.get(cc) or len(rows), 'missing': len(rows),
                    'missing_activations': sum(r[4] or 0 for r in rows), 'top': rows[0][1] if rows else ''})
    for f in OUT.glob('*.json'):   # a country with nothing missing any more: its old list goes
        if f.stem != 'index' and f.stem not in lists: f.unlink()
    idx.sort(key=lambda r: (-r['missing_activations'], -r['missing'], r['cc']))
    json.dump({'about': 'Parks still missing a boundary, per country, most activated first (kpc_missing_lists.py, nightly after the scoreboard)',
               'built': __import__('datetime').date.today().isoformat(), 'activity_built': (load('data/pota/activity.json', {}) or {}).get('built'),
               'countries': idx}, open(OUT / 'index.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print(f"::notice title=Missing lists::{len(idx)} countries, {sum(r['missing'] for r in idx)} parks missing a boundary; top by activity: "
          + ', '.join(f"{r['cc']} {r['missing']}" for r in idx[:8]))


if __name__ == '__main__':
    try: main()
    except Exception as e: print(f'::notice title=Missing lists::stopped ({type(e).__name__}: {e})')  # noqa: BLE001
