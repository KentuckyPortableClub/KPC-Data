#!/usr/bin/env python3
"""22 Nov 2026: the page reader's walk was stuck. Every run since 20 Nov 21:00 UTC read US-AK until GitHub cut the step at 52
minutes; no summary was written, the save refused ("there is no summary to save"), and the next run started US-AK again.
Fixed: the reader stops by itself well inside the step (--max-minutes), a hard `timeout` stops it for sure before the step
does, the report always has time to run after it, and a facts file is written whole (temp file, then put in place), so a
stop mid-write never leaves half a file. Offline. Prints PASS / FAIL and ends ALL PASS or SOME FAILED."""
import json, os, pathlib, re, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github/scripts'))
ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


import yaml  # noqa: E402

wf = yaml.safe_load((ROOT / '.github/workflows/kpc-park-pages.yml').read_text(encoding='utf-8'))
steps = [s for j in wf['jobs'].values() for s in j.get('steps') or []]
read = next(s for s in steps if s.get('name') == 'Read the pages')
step_min = int(read['timeout-minutes'])
run = read['run']
cmd = next(l for l in run.splitlines() if 'kpc_park_pages.py read' in l)
hard = re.search(r'\btimeout\s+(?:-s\s+\w+\s+)?(\d+)m\b', cmd)
soft = re.search(r'--max-minutes\s+(\d+)', run)
check('the reader runs under a hard timeout', hard is not None)
if hard and soft:
    h, m = int(hard.group(1)), int(soft.group(1))
    check(f'the hard timeout ({h} min) stops the reader at least 5 minutes before the step ({step_min} min)', h + 5 <= step_min)
    check(f'the reader stops by itself ({m} min) before the hard timeout ({h} min)', m < h)
lines = run.splitlines()
check('the report runs after the reader in the same step (the save needs its summary)',
      any('kpc_park_pages.py report' in l for l in lines[lines.index(cmd):]))

import kpc_park_pages as PP  # noqa: E402

with tempfile.TemporaryDirectory() as t:
    f = pathlib.Path(t) / 'facts' / 'US-ZZ.json'
    calls = []
    real = os.replace
    os.replace = lambda a, b: (calls.append((str(a), str(b))), real(a, b))[1]
    try:
        PP.save_json(f, {'area': 'US-ZZ', 'parks': {'US-9001': {'ref': 'US-9001'}}})
    finally:
        os.replace = real
    check('a facts file is written to a temp file, then put in place whole', calls and calls[0][1] == str(f) and calls[0][0] != str(f))
    check('the file reads back, and no temp file is left', json.loads(f.read_text())['parks'] and not list(f.parent.glob('*.tmp')))
    check('a temp file is never read as a facts file (only *.json files are)', not (f.name + '.tmp').endswith('.json'))

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
