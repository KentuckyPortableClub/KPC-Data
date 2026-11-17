#!/usr/bin/env python3
"""kpc_key_questions.py (HQ 2026-11-17, matching plan 7a): questions are sorted busiest first and the newer key checks are asked."""
import gzip, json, os, pathlib, subprocess, sys, tempfile
S = pathlib.Path(__file__).resolve().parents[1] / '.github/scripts/kpc_key_questions.py'
bad = 0
with tempfile.TemporaryDirectory() as t:
    t = pathlib.Path(t); (t / 'links/data/us-key').mkdir(parents=True); (t / 'data/parkinfo').mkdir(parents=True)
    json.dump({'parks': {'US-1': {'n': 'Quiet SP', 'c': [['a', 'A', 1, 'check (contest): shared']]},
                         'US-2': {'n': 'Busy SP', 'c': [['b', 'B', 2, 'held (rule G-1): far'], ['c', 'C', 3, 'not a question']]}}}, open(t / 'links/data/us-key/US-ZZ.json', 'w'))
    json.dump({'parks': {'US-1': ['Quiet SP', '', '', '', '', 0, 0, 5, 0, 0], 'US-2': ['Busy SP', '', '', '', '', 0, 0, 900, 0, 0]}}, open(t / 'data/parkinfo/US-ZZ.json', 'w'))
    subprocess.run([sys.executable, '-I', str(S)], cwd=t, env=dict(os.environ, LINKS=str(t / 'links')), check=True, capture_output=True)
    f = next((t / 'data/waiting/questions').glob('key-pieces.json*'))
    d = json.load(gzip.open(f, 'rt') if f.suffix == '.gz' else open(f))
    got = [(q['ref'], q['activations']) for q in d['questions']]
    for ok, m in ((got == [('US-2', 900), ('US-1', 5)], f'busiest first, the contest check asked, other rows not ({got})'),):
        print(('PASS ' if ok else 'FAIL ') + m); bad += not ok
print('ALL PASS' if not bad else 'SOME FAILED'); sys.exit(1 if bad else 0)
