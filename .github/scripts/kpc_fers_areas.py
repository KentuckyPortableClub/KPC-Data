#!/usr/bin/env python3
"""2-fer areas (Nov 9 2026, Brandon t905u/t906u): one job per area, each with its own time budget.
  plan     REGION='southeast canadaeast' | 'areas' | 'US-FL CA-ON' (one state alone) | na | world | ky | both
           -> prints  list=[{name, region, states, tag, full, seed}, ...]
           full='1' = this area is rebuilt in full this run (round-robin, one full rebuild per area per full_cycle_days;
           FULL=all = every job in full (emergency), FULL=none = no full area this run)
           (the KPC 2-fer bot's matrix; old values na / world / ky / both work as before)
  finished STATES='US-NC ...' -> the live files of the states that fully finished every pass today (after a crash: only these are saved)
  status   one line per area: the states' last pass dates and any 'incomplete' mark, then the dispatch line for the areas that
           are not finished (run them again by name until every area has a good file). Read only. SINCE=2026-11-10 = a state
           counts as finished only when its pass 5 is that day or later.
Areas: .github/fers-areas.json. Kentucky is its own run (region 'ky'), as before."""
import json, os, pathlib, re, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
CFG = json.load(open(ROOT / '.github/fers-areas.json', encoding='utf-8'))
AREAS = CFG['areas']
CYCLE = int(os.environ.get('KPC_FERS_FULL_CYCLE_DAYS') or CFG.get('full_cycle_days') or 90)


def full_due(names, today=None, last=None):
    """Nov 9 evening (Brandon t917u/t918u): the areas due for their one full rebuild per cycle (never done or older than the cycle),
    oldest first, at most ceil(all areas x 30 / cycle) per run."""
    import datetime as dt, math
    t = dt.date.fromisoformat(today or dt.date.today().isoformat())
    if last is None:
        last = {f.stem[len('full-rebuild-'):]: f.read_text().strip()[:10] for f in (ROOT / 'data/fers').glob('full-rebuild-*.txt')}
    due = sorted((last.get(n) or '', n) for n in names if not last.get(n) or (t - dt.date.fromisoformat(last[n])).days >= CYCLE)
    return [n for _, n in due[:max(1, math.ceil(len(AREAS) * 30 / CYCLE))]]


def plan(region, states=''):
    words = region.lower().replace(',', ' ').split() or ['both']
    out = []
    for w in words:
        if w == 'areas': out += [{'name': n, 'region': 'na', 'states': s, 'tag': n} for n, s in AREAS.items()]
        elif w in AREAS: out.append({'name': w, 'region': 'na', 'states': AREAS[w], 'tag': w})
        elif re.fullmatch(r'(us|ca)-[a-z]{2}', w) and any(w.upper() in v.split() for v in AREAS.values()):
            # KPC owner, 2026-11-12 (KISS, per state): one state / province alone, its own job; its tag is its own (US-FL -> fl), and it
            # starts from its area's saved pair answers (seed). It writes only its own state file (+ its tag's report files).
            st = w.upper(); area = next(a for a, v in AREAS.items() if st in v.split())
            out.append({'name': st, 'region': 'na', 'states': st, 'tag': st.lower().replace('us-', '').replace('-', ''), 'seed': area})
        elif w in ('na', 'world', 'ky'): out.append({'name': w, 'region': w, 'states': states if w != 'ky' else '', 'tag': ''})
        elif w == 'both': out += [{'name': 'na', 'region': 'na', 'states': states, 'tag': ''}, {'name': 'world', 'region': 'world', 'states': states, 'tag': ''}]
        else: print(f'::warning title=2-fer areas::unknown area {w!r} (known: {" ".join(AREAS)} areas na world ky both): skipped', file=sys.stderr)
    seen, uniq = set(), []
    for x in out:
        if x['name'] not in seen: seen.add(x['name']); uniq.append(x)
    full = os.environ.get('FULL', '').strip().lower()
    pick = set(x['name'] for x in uniq) if full in ('all', '1', 'yes', 'true') else set() if full in ('none', 'no', '0') else set(full_due([x['name'] for x in uniq if x['tag'] and x['name'] in AREAS]))   # a one-state job is never a round-robin full rebuild (FULL=all still is)
    for x in uniq: x['full'] = '1' if x['name'] in pick else ''
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


def finished(states, today, data=pathlib.Path('.')):
    """Nov 9 evening (Brandon t926u, 5:03 PM CST): after a crash / time-out, the live 2-fer files that may still be saved: a state's file
    only when that state FULLY finished every pass today (pass5 == today, not marked incomplete). A partly done state keeps its old file."""
    import gzip
    out = []
    for st in states.split():
        for f in (data / f'data/fers/{st}.json', data / f'data/fers/{st}.json.gz'):
            if not f.exists(): continue
            try: d = json.load(gzip.open(f, 'rt') if f.suffix == '.gz' else open(f))
            except Exception: continue  # noqa: BLE001
            if str(d.get('pass5') or '') == today and not d.get('incomplete'): out.append(str(f.relative_to(data)))
    return out


if __name__ == '__main__':
    a = sys.argv[1:] or ['plan']
    if a[0] == 'plan': print('list=' + json.dumps(plan(os.environ.get('REGION') or 'both', os.environ.get('STATES') or '')))
    elif a[0] == 'status': status(pathlib.Path(a[1]) if len(a) > 1 else ROOT)
    elif a[0] == 'finished': print('\n'.join(finished(os.environ.get('STATES') or '', os.environ.get('TODAY') or __import__('time').strftime('%Y-%m-%d'))))
    else: print(__doc__)
