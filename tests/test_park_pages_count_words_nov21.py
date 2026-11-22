#!/usr/bin/env python3
"""Page reader, 21 Nov 2026: the running count says it is the park's place on this run's list and names how many parks were read
before (passed over in a moment), so '1130 of 15000' no longer looks like the reader started over. Invented parks, offline
fixtures. Prints PASS / FAIL lines and ends ALL PASS or SOME FAILED."""
import json, pathlib, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


REFS = ('US-9101', 'US-9102', 'US-9103')
with tempfile.TemporaryDirectory() as t:
    t = pathlib.Path(t)
    data = t / 'data' / 'parkinfo'; data.mkdir(parents=True)
    (data / 'US-ZZ.json').write_text(json.dumps({'parks': {r: {'name': f'Invented Park {r[-1]}', 'website': f'https://parks.invented.example/{r}'}
                                                            for r in REFS}}), encoding='utf-8')
    fx = t / 'fx.json'; fx.write_text(json.dumps({'pages': {}}), encoding='utf-8')
    out = t / 'out'; out.mkdir()
    pri = t / 'PRIVATE'; pri.mkdir(); (pri / 'pri.csv').write_text('park\nUS-9101\n', encoding='utf-8')   # a listed park stays on the list
    (out / 'state.json').write_text(json.dumps({'read': {'US-9101': {'url': 'https://parks.invented.example/US-9101', 'fingerprint': 'ab',
                                                                     'date': '2026-11-20', 'kind': 'html'}}}), encoding='utf-8')
    r = subprocess.run([sys.executable, '-B', str(ROOT / '.github/scripts/kpc_park_pages.py'), 'read', '--data', str(t / 'data'), '--out', str(out),
                        '--state', str(out / 'state.json'), '--fixtures', str(fx), '--today', '2026-11-21', '--areas', 'US-ZZ',
                        '--priority-file', str(pri / 'pri.csv')],
                       capture_output=True, text=True)
    o = r.stdout
    check('the run says how many parks were read before', r.returncode == 0 and 'The list has 3 parks. 1 of them were read before' in o)
    check('each line is the place on the list, and a park read before is marked', 'Park 1 of 3 on the list' in o and '(read before)' in o)
    check('the old "Reading 1 of 3 parks" wording is gone', 'Reading 1 of 3 parks' not in o)
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
