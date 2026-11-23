#!/usr/bin/env python3
"""Page reader, 21 Nov 2026: one refused page no longer puts its whole site aside. Before, a single 403 (or one robots 'no' for
one path) made the reader skip every other park on that site for 30 days without asking (751 'refused' parks on the PC, about
25 really asked). Now: every refusal is honoured for its own page; a site is put aside only after 3 DIFFERENT pages refused us
(401 / 403 / a wall); a robots 'no' is never remembered for the whole site (robots.txt is read for each address); a state saved
under the old rule asks those sites again. Invented parks, offline fixtures. Prints PASS / FAIL and ends ALL PASS or SOME FAILED."""
import json, pathlib, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


REFS = ['US-9201', 'US-9202', 'US-9203', 'US-9204', 'US-9205']
U = lambda r: f'https://parks.invented.example/park/{r}'
BODY = lambda r: f'<html><head><title>Invented Park {r[-1]}</title></head><body><h1>Invented Park {r[-1]}</h1><p>' + 'Words about the park. ' * 40 + '</p></body></html>'


def run(t, statuses, state=None):
    out = t / ('out-' + '-'.join(str(statuses[r]) for r in REFS)); out.mkdir()
    data = t / 'data' / 'parkinfo'; data.mkdir(parents=True, exist_ok=True)
    (data / 'US-ZZ.json').write_text(json.dumps({'parks': {r: [f'Invented Park {r[-1]}', U(r), 'State Park', '', '', 38.5, -85.5, 0, 0, 1] for r in REFS}}), encoding='utf-8')
    (t / 'fx.json').write_text(json.dumps({'pages': {U(r): ({'status': statuses[r], 'body': 'no'} if statuses[r] != 200 else {'status': 200, 'body': BODY(r)})
                                                     for r in REFS}}), encoding='utf-8')
    if state is not None: (out / 'state.json').write_text(json.dumps(state), encoding='utf-8')
    r = subprocess.run([sys.executable, '-B', str(ROOT / '.github/scripts/kpc_park_pages.py'), 'read', '--data', str(t / 'data'), '--out', str(out),
                        '--state', str(out / 'state.json'), '--fixtures', str(t / 'fx.json'), '--today', '2026-11-21', '--areas', 'US-ZZ', '--quiet'],
                       capture_output=True, text=True)
    facts = json.loads((out / 'facts' / 'US-ZZ.json').read_text()).get('parks', {}) if (out / 'facts' / 'US-ZZ.json').is_file() else {}
    asked = {ref for ref, f in facts.items() if (f.get('page') or {}).get('requests')}
    return r, facts, asked, json.loads((out / 'state.json').read_text()) if (out / 'state.json').is_file() else {}


with tempfile.TemporaryDirectory() as t:
    t = pathlib.Path(t)
    r, facts, asked, st = run(t, {'US-9201': 403, 'US-9202': 200, 'US-9203': 200, 'US-9204': 200, 'US-9205': 200})
    check('one refused page: every other park on the site is still asked and read', r.returncode == 0 and asked == set(REFS)
          and all((facts[x].get('page') or {}).get('kind') == 'html' for x in REFS[1:]))
    check('the refused page itself stays refused', (facts['US-9201'].get('page') or {}).get('kind') == 'refused')
    check('the site is not put aside after one refusal', 'parks.invented.example' not in (st.get('refused') or {}))

    r, facts, asked, st = run(t, {'US-9201': 403, 'US-9202': 403, 'US-9203': 403, 'US-9204': 200, 'US-9205': 200})
    # 22 Nov: three refused pages no longer put the site aside (now 10, test_park_pages_refusals_nov22.py)
    check('three different refused pages: the rest of the site is still asked', asked == set(REFS)
          and 'parks.invented.example' not in (st.get('refused') or {}))

    r, facts, asked, st = run(t, {'US-9201': 'robots', 'US-9202': 200, 'US-9203': 200, 'US-9204': 200, 'US-9205': 200})
    check('a robots "no" for one address is not remembered for the whole site', asked >= set(REFS[1:]) and not (st.get('refused') or {}))

    old = {'refused': {'parks.invented.example': '2026-11-20'}}
    r, facts, asked, st = run(t, {'US-9201': 200, 'US-9202': 200, 'US-9203': 200, 'US-9204': 200, 'US-9205': 200}, state=old)
    check('a state saved under the old rule asks the site again', asked == set(REFS))
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
