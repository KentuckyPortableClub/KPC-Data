#!/usr/bin/env python3
"""THE MORNING LIST for chat 11 (chat 10, Oct 30 2026; Brandon Oct 29 11:50 PM: '1 and 3'). One page, written by the nightly
waiting-room run: every file held in data/waiting/in/ (oldest first, how long, why it was held), every questions file with its
open count, and the approvals not yet used. Chat 11 reads it when Brandon types 'inbox' (README line). No alerts.
  python3 kpc_waiting_today.py   -> data/waiting/today.md. Never fails."""
import datetime as dt, json, os, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from kpc_json_any import glob_json_any, iter_jsonl_any, load_json_any  # noqa: E402

DATA = pathlib.Path(os.environ.get('DATA') or '.')
W = DATA / 'data' / 'waiting'


def load(p, d=None):
    try: return load_json_any(p)
    except (OSError, ValueError): return d


def verdict_rows():
    """One dict per line of verdicts.jsonl (or verdicts.jsonl.gz). The change log only: a line is
    written when a file's verdict changes, so a later PASS can be missing if that write did not land."""
    rows = list(iter_jsonl_any(W / 'verdicts.jsonl'))   # the history up to Nov 17 (one file)
    for p in sorted((W / 'verdicts-log').glob('*.jsonl*')) if (W / 'verdicts-log').is_dir() else []:   # Nov 17 (storage): one small file a day since
        try: rows += list(iter_jsonl_any(p.with_name(p.name[:-3]) if p.name.endswith('.gz') else p))
        except (OSError, ValueError): pass
    return rows


def current_verdicts():
    """The latest complete check (verdicts.json): every waiting file re-checked on that run."""
    rep = load(W / 'verdicts.json', {}) or {}
    out = {}
    if not isinstance(rep, dict): return out
    for r in rep.get('results') or []:
        if isinstance(r, dict) and r.get('path'):
            out[r['path']] = r
    return out


def verdict_for(rel, current, log_last):
    """Prefer the latest check. Fall back to the change log when that file was not in the last run.
    An owner's RELEASE on the change log is kept when the latest check is only a PASS (or
    LIVE-FILTERED): the checker never writes RELEASE, so preferring that check would hide the
    approval and show PASS. A later HOLD still comes from the latest check."""
    key = rel[:-3] if rel.endswith('.gz') else rel
    cur, log = {}, {}
    for k in (rel, key, key + '.gz', rel + '.gz'):
        if k in current:
            cur = current[k]; break
    for k in (rel, key, key + '.gz', rel + '.gz'):
        if k in log_last:
            log = log_last[k]; break
    if log.get('verdict') == 'RELEASE' and (not cur.get('verdict') or cur.get('verdict') in ('PASS', 'LIVE-FILTERED', 'RELEASE')):
        return log
    return cur or log


def main():
    today = dt.date.today()
    since = load(W / 'held-since.json', {}) or {}
    log_last = {}
    for r in verdict_rows():
        if r.get('path'): log_last[r['path']] = r
    current = current_verdicts()
    held = []
    for f in (W / 'in').rglob('*') if (W / 'in').exists() else []:
        if not f.is_file() or f.name == '.keep': continue
        rel = str(f.relative_to(W / 'in')); key = rel[:-3] if rel.endswith('.gz') else rel
        s = since.get(rel) or since.get(key) or ''
        try: days = (today - dt.date.fromisoformat(s[:10])).days
        except ValueError: days = None
        v = verdict_for(rel, current, log_last)
        held.append((s or '9999', rel, days, v.get('verdict') or '?', '; '.join(v.get('why') or [])[:220]))
    try:
        sys.path.insert(0, str(pathlib.Path(__file__).parent)); import kpc_order as O
        held.sort(key=lambda h: (O.rank(h[1]), h))   # US + CA first, then North America, W1-W10 (Brandon Oct 30 12:44 PM); oldest first inside
    except Exception: held.sort()  # noqa: BLE001
    L = [f'# Waiting room: morning list ({today})', '', 'For chat 11. Held = checked, not live. Release = your YES (+ chat 2 recheck) in data/waiting/approved.json; the nightly run lets it out.', '',
         f'## Held files: {len(held)} (US + Canada first, then North America, W1-W10, rest; oldest first inside)', '', '| since | days | file | last check | why |', '|---|---|---|---|---|']
    L += [f"| {s if s != '9999' else '?'} | {d if d is not None else '?'} | {rel} | {vd} | {why.replace('|', '/')} |" for s, rel, d, vd, why in held] or ['| - | - | nothing held | - | - |']
    L += ['', '## Questions waiting for an answer', '', '| file | open | total |', '|---|---|---|']
    for q in glob_json_any(str(W / 'questions' / '*.json')):
        q = pathlib.Path(q)
        d = load(q, {})
        rows = d.get('questions') if isinstance(d, dict) else d
        rows = rows if isinstance(rows, list) else []
        op = sum(1 for r in rows if isinstance(r, dict) and not r.get('answer'))
        L.append(f'| {q.name} | {op} | {len(rows)} |')
    used = load(W / 'approved-used.json', {}) or {}
    items = (load(W / 'approved.json', {}) or {}).get('items') or []
    waiting = [i for i in items if json.dumps(i, sort_keys=True, ensure_ascii=False) not in used]
    L += ['', f'## Approvals not used yet: {len(waiting)}', '']
    L += [f"- {i.get('what') or i.get('path')}: chat 11 '{i.get('chat11')}' by {i.get('by')}, chat 2 '{i.get('chat2') or '-'}'" for i in waiting] or ['- none']
    open(W / 'today.md', 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    print(f'::notice title=Morning list::{len(held)} held, {len(waiting)} approvals waiting: data/waiting/today.md')


if __name__ == '__main__':
    try: main()
    except Exception as e:  # noqa: BLE001
        print(f'::notice title=Morning list::stopped ({type(e).__name__}: {e})')
    sys.exit(0)
