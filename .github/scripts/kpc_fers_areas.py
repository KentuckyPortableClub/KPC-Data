#!/usr/bin/env python3
"""2-fer areas (Nov 9 2026, Brandon t905u/t906u): one job per area, each with its own time budget.
  plan     REGION='southeast canadaeast' | 'areas' | na | world | ky | both  -> prints  list=[{name, region, states, tag}, ...]
           (the KPC 2-fer bot's matrix; old values na / world / ky / both work as before)
  status   one line per area: the states' last pass dates and any 'incomplete' mark, then the dispatch line for the areas that
           are not finished (run them again by name until every area has a good file). Read only. SINCE=2026-11-10 = a state
           counts as finished only when its pass 5 is that day or later.
Areas: .github/fers-areas.json. Kentucky is its own run (region 'ky'), as before."""
import json, os, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
AREAS = json.load(open(ROOT / '.github/fers-areas.json', encoding='utf-8'))['areas']


def plan(region, states=''):
    words = region.lower().replace(',', ' ').split() or ['both']
    out = []
    for w in words:
        if w == 'areas': out += [{'name': n, 'region': 'na', 'states': s, 'tag': n} for n, s in AREAS.items()]
        elif w in AREAS: out.append({'name': w, 'region': 'na', 'states': AREAS[w], 'tag': w})
        elif w in ('na', 'world', 'ky'): out.append({'name': w, 'region': w, 'states': states if w != 'ky' else '', 'tag': ''})
        elif w == 'both': out += [{'name': 'na', 'region': 'na', 'states': states, 'tag': ''}, {'name': 'world', 'region': 'world', 'states': states, 'tag': ''}]
        else: print(f'::warning title=2-fer areas::unknown area {w!r} (known: {" ".join(AREAS)} areas na world ky both): skipped', file=sys.stderr)
    seen, uniq = set(), []
    for x in out:
        if x['name'] not in seen: seen.add(x['name']); uniq.append(x)
    return uniq


def status(data=ROOT):
    lines, todo = [], []
    for n, sts in AREAS.items():
        bits, done = [], True
        for st in sts.split():
            f = next((p for p in (data / f'data/fers/{st}.json', data / f'data/fers/{st}.json.gz') if p.exists()), None)
            if not f: bits.append(f'{st}: no file'); done = False; continue
            try:
                import gzip
                d = json.load(gzip.open(f, 'rt') if f.suffix == '.gz' else open(f))
            except Exception: bits.append(f'{st}: unreadable'); done = False; continue  # noqa: BLE001
            if d.get('incomplete') or not d.get('pass5') or str(d.get('pass5')) < (os.environ.get('SINCE') or ''): done = False
            bits.append(f"{st}: pass1 {d.get('pass1', '-')} pass5 {d.get('pass5', '-')}" + (' INCOMPLETE' if d.get('incomplete') else ''))
        lines.append(f"{'done' if done else 'TO DO'}  {n}: " + '; '.join(bits))
        if not done: todo.append(n)
    print('\n'.join(lines))
    if todo: print(f"\nRun again: gh workflow run kpc-fers.yml -R KentuckyPortableClub/KPC-Data -f pass=all -f region='{' '.join(todo)}'")
    else: print('\nEvery area has a finished file.')
    return todo


if __name__ == '__main__':
    a = sys.argv[1:] or ['plan']
    if a[0] == 'plan': print('list=' + json.dumps(plan(os.environ.get('REGION') or 'both', os.environ.get('STATES') or '')))
    elif a[0] == 'status': status(pathlib.Path(a[1]) if len(a) > 1 else ROOT)
    else: print(__doc__)
