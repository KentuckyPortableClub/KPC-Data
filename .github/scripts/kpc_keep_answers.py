#!/usr/bin/env python3
"""KEEP PEOPLE'S ANSWERS when a long bot job saves (chat 10, Oct 30 2026, 1:30 AM CDT).
A bot job checks the repo out once and works for hours; chat 11 may write answers meanwhile. Before the job saves, this reads
the LATEST copy on origin/main and puts back every answer (answer, checked_by, how, rechecked_by_chat2) the job's copy lacks,
keeps every question the job does not know of, and merges state files (the job's areas win, others are kept).
  python3 kpc_keep_answers.py questions data/waiting/questions/world-finder.json [more ...]
  python3 kpc_keep_answers.py state data/world-finder/state.json
Never fails."""
import json, subprocess, sys

KEYS = ('answer', 'checked_by', 'how', 'rechecked_by_chat2', 'auto', 'sample_for_chat11', 'auto_recheck', 'parked')


def origin(path):
    subprocess.run(['git', 'fetch', '-q', 'origin', 'main'], capture_output=True)
    p = subprocess.run(['git', 'show', f'origin/main:{path}'], capture_output=True)
    if p.returncode: return None
    try: return json.loads(p.stdout)
    except ValueError: return None


def k(q): return (q.get('ref'), str(q.get('record')), q.get('layer'))


def questions(path):
    o = origin(path)
    if not o: return
    try: mine = json.load(open(path, encoding='utf-8'))
    except (OSError, ValueError): return
    theirs = {k(q): q for q in o.get('questions') or []}
    have = set()
    put = 0
    for q in mine.get('questions') or []:
        have.add(k(q)); t = theirs.get(k(q))
        if t and t.get('answer') and not q.get('answer'):
            q.update({x: t.get(x) for x in KEYS if x in t}); put += 1
    extra = [q for kk, q in theirs.items() if kk not in have]
    mine['questions'] = (mine.get('questions') or []) + extra
    mine['open'] = sum(1 for q in mine['questions'] if not q.get('answer'))
    json.dump(mine, open(path, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print(f'::notice title=Keep answers::{path}: {put} answers put back, {len(extra)} questions kept from the latest copy')


def state(path):
    o = origin(path) or {}
    try: mine = json.load(open(path, encoding='utf-8'))
    except (OSError, ValueError): mine = {}
    json.dump({**o, **mine}, open(path, 'w', encoding='utf-8'), indent=1)


if __name__ == '__main__':
    try:
        fn = {'questions': questions, 'state': state}[sys.argv[1]]
        for pth in sys.argv[2:]: fn(pth)
    except Exception as e:  # noqa: BLE001
        print(f'::notice title=Keep answers::stopped ({type(e).__name__}: {e})')
    sys.exit(0)
