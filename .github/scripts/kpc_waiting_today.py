#!/usr/bin/env python3
"""THE MORNING LIST for chat 11 (chat 10, Oct 30 2026; Brandon Oct 29 11:50 PM: '1 and 3'). One page, written by the nightly
waiting-room run: every file held in data/waiting/in/ (oldest first, how long, why it was held), every questions file with its
open count, and the approvals not yet used. Chat 11 reads it when Brandon types 'inbox' (README line). No alerts.
  python3 kpc_waiting_today.py   -> data/waiting/today.md. Never fails."""
import datetime as dt, json, pathlib, sys

W = pathlib.Path('data/waiting')


def load(p, d=None):
    try: return json.load(open(p, encoding='utf-8'))
    except (OSError, ValueError): return d


def main():
    today = dt.date.today()
    since = load(W / 'held-since.json', {}) or {}
    last = {}
    for line in open(W / 'verdicts.jsonl', encoding='utf-8') if (W / 'verdicts.jsonl').exists() else []:
        try: r = json.loads(line)
        except ValueError: continue
        if r.get('path'): last[r['path']] = r
    held = []
    for f in (W / 'in').rglob('*') if (W / 'in').exists() else []:
        if not f.is_file() or f.name == '.keep': continue
        rel = str(f.relative_to(W / 'in')); key = rel[:-3] if rel.endswith('.gz') else rel
        s = since.get(rel) or since.get(key) or ''
        try: days = (today - dt.date.fromisoformat(s[:10])).days
        except ValueError: days = None
        v = last.get(rel) or last.get(key) or {}
        held.append((s or '9999', rel, days, v.get('verdict') or '?', '; '.join(v.get('why') or [])[:220]))
    held.sort()
    L = [f'# Waiting room: morning list ({today})', '', 'For chat 11. Held = checked, not live. Release = your YES (+ chat 2 recheck) in data/waiting/approved.json; the nightly run lets it out.', '',
         f'## Held files: {len(held)} (oldest first)', '', '| since | days | file | last check | why |', '|---|---|---|---|---|']
    L += [f"| {s if s != '9999' else '?'} | {d if d is not None else '?'} | {rel} | {vd} | {why.replace('|', '/')} |" for s, rel, d, vd, why in held] or ['| - | - | nothing held | - | - |']
    L += ['', '## Questions waiting for an answer', '', '| file | open | total |', '|---|---|---|']
    for q in sorted((W / 'questions').glob('*.json')):
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
