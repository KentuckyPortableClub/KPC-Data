#!/usr/bin/env python3
"""24 Nov 2026 (owner approved C): the status-only close-match file is IDs first,
has 1,025 unique park ids (55 already confirmed by #365 are listed separately), and omits the excluded parks. No network."""
import json, pathlib, socket, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
ok = True


def _no_net(*a, **k):
    raise RuntimeError('no network in tests')


socket.socket.connect = _no_net


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


path = ROOT / 'data/status-confirms/nov24-close-matches.json'
raw = path.read_text(encoding='utf-8')
data = json.loads(raw)
parks = data.get('parks') or []
excl = {'US-12519', 'US-12715', 'US-9263'}
check('the file loads and lists parks', isinstance(parks, list) and parks)
already = data.get('already_confirmed_by_365') or []
check('1,025 unique park ids, matching the counts field',
      len(parks) == 1025 and len(set(parks)) == 1025 and data.get('counts', {}).get('parks') == 1025)
check('55 parks already confirmed by #365 are marked separately and are not in the 1,025',
      len(already) == 55 and len(set(already)) == 55 and not (set(already) & set(parks))
      and data.get('counts', {}).get('already_confirmed_by_365') == 55
      and data.get('counts', {}).get('previous_list') == 1080
      and all(isinstance(p, str) and p.startswith('US-') for p in already))
check('every id is a US park ref', all(isinstance(p, str) and p.startswith('US-') for p in parks))
check('the three named exclusions are not in the list', not (excl & set(parks)))
check('the file is IDs first: no park display-name field',
      'name' not in data and all(not isinstance(p, dict) for p in parks) and '"name"' not in raw)
check('the held-name dropout count is recorded',
      data.get('counts', {}).get('dropped_held_name_does_not_match') == 88)
check('status only: the about text says nothing was applied',
      'nothing was applied' in (data.get('about') or '').lower())

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
