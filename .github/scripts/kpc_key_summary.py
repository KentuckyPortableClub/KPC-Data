#!/usr/bin/env python3
"""BOT C: KEY BEFORE / AFTER + CHAT 11'S SAMPLE (chat 2, Oct 29 2026 11:30 PM; Brandon 11:18 PM 'build it!';
plan KPC-Links .claude/build/research/KPC_Key_And_2fer_Automation_Plan.md).
Runs in the daily copy right after the waiting room diverted a new US / Canada key build into data/waiting/in/. Compares the HELD
build with the LIVE key (data/us-key, data/ca-key here) and writes ONE small file chat 11 can check from alone:
  data/waiting/preview/<key>-changes.json   per-area counts, every park that gained / lost an outline (pieces + Rule G reason),
                                            grade changes, and a SAMPLE of 30 (15 changed by chat 11's own answers = the answers
                                            bot's ledger, 15 changed by new layers / code; one per area first, then the biggest)
No shapes, no network, never fails (exit 0). Nothing is written when nothing is held.
  python3 kpc_key_summary.py            (from the KPC-Data root)
"""
import datetime as dt, glob, json, os, pathlib, sys

HELD = pathlib.Path('data/waiting/in/data')
OUT = pathlib.Path('data/waiting/preview')
LEDGER_URL_HINT = 'KPC-Links data/us-key/answers-applied.json'


def load(p, d=None):
    try: return json.load(open(p))
    except Exception: return d  # noqa: BLE001


def parks_of(folder):
    out = {}
    for f in sorted(glob.glob(str(folder / '*.json'))):
        name = pathlib.Path(f).stem
        if not (name.startswith('US-') or name.startswith('CA-')) or len(name) != 5: continue
        for r, p in ((load(f, {}) or {}).get('parks') or {}).items():
            if isinstance(p, dict): out[(name, r)] = p
    return out


def grade(p): return p.get('g') or ('pin' if not p.get('m') else 'official')


def pieces(p): return [[str(x[0]), x[1], x[2], str(x[3])[:60]] for x in (p.get('m') or [])[:8]]


def held_reason(p): return [str(x[3])[:70] for x in (p.get('c') or []) if 'rule' in str(x[3])][:3]


def one(key):
    held_dir, live_dir = HELD / key, pathlib.Path('data') / key
    if not held_dir.is_dir() or not glob.glob(str(held_dir / '*.json')): return None
    H, L = parks_of(held_dir), parks_of(live_dir)
    if not H: return None
    links = pathlib.Path(os.environ.get('LINKS') or '../links')
    led = load(links / 'data' / key / 'answers-applied.json', {}) or {}
    by_answer = {k.split(':')[1] for k in led}                                  # parks a chat 11 answer touched
    per, gained, lost, regrade = {}, [], [], []
    for k, p in H.items():
        area, ref = k; o = L.get(k)
        if o is None: continue                                                   # an area the build did not redo
        c = per.setdefault(area, {'gained': 0, 'lost': 0, 'pieces_changed': 0, 'grade_changed': 0})
        a = {str(x[0]) for x in o.get('m') or []}; b = {str(x[0]) for x in p.get('m') or []}
        row = {'area': area, 'ref': ref, 'name': p.get('n') or o.get('n'), 'old_grade': grade(o), 'new_grade': grade(p),
               'new_pieces': pieces(p), 'old_pieces': pieces(o), 'held_now': held_reason(p), 'by_answer': ref in by_answer,
               'pota': f'https://pota.app/#/park/{ref}'}
        if b and not a: c['gained'] += 1; gained.append(row)
        elif a and not b: c['lost'] += 1; lost.append(row)
        elif a != b: c['pieces_changed'] += 1
        if grade(o) != grade(p) and not (b and not a) and not (a and not b): c['grade_changed'] += 1; regrade.append(row)
    per = {k: v for k, v in per.items() if any(v.values())}
    changed = gained + lost + regrade
    # the sample: 15 from chat 11's own answers, 15 from the rest; one per area first, then the most pieces
    def pick(rows, n):
        rows = sorted(rows, key=lambda r: -len(r['new_pieces'])); out, seen = [], set()
        for r in rows:
            if len(out) >= n: break
            if r['area'] not in seen: out.append(r); seen.add(r['area'])
        for r in rows:
            if len(out) >= n: break
            if r not in out: out.append(r)
        return out
    sample = pick([r for r in changed if r['by_answer']], 15)
    sample += pick([r for r in changed if not r['by_answer']], 30 - len(sample))
    tot = {k: sum(v[k] for v in per.values()) for k in ('gained', 'lost', 'pieces_changed', 'grade_changed')}
    doc = {'about': f'{key}: the HELD build (data/waiting/in/data/{key}/) vs the LIVE key (data/{key}/). Chat 11: check the sample, then write '
                    "KEY YES or KEY NO: <refs> in data/waiting/approved.json (item 'what': '" + key + "'). Written by kpc_key_summary.py.",
           'made': dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d %H:%M UTC'), 'totals': tot, 'per_area': per,
           'gained': gained, 'lost': lost, 'grade_changed': regrade[:200], 'sample': sample}
    OUT.mkdir(parents=True, exist_ok=True)
    json.dump(doc, open(OUT / f'{key}-changes.json', 'w'), indent=1, ensure_ascii=False)
    return tot, len(sample)


def main():
    for key in ('us-key', 'ca-key'):
        r = one(key)
        if r: print(f'::notice title=Key summary ({key})::held build vs live: {r[0]}; sample of {r[1]} in data/waiting/preview/{key}-changes.json')


if __name__ == '__main__':
    try: main()
    except Exception as e: print(f'::notice title=Key summary::stopped: {str(e)[:200]}')  # noqa: BLE001
    sys.exit(0)
