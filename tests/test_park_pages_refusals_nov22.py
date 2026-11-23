#!/usr/bin/env python3
"""Page reader, 22 Nov 2026 (owner: "U sure we are getting refused"): 3 refused pages put a whole site aside, so 2,335 parks
were never asked (BLM: 3 pages refused, 723 parks skipped). Now a site is put aside only after 10 DIFFERENT pages refused us
(401 / 403 / a wall), and only for 7 days (was 30). Every refusal is still honoured for its own page; nothing gets past a wall.
A state saved under the old rule (3) asks those sites again. Invented parks, offline fixtures. Prints PASS / FAIL, ends ALL PASS
or SOME FAILED."""
import json, pathlib, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
HOST = 'parks.invented.example'
ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


REFS = [f'US-93{i:02d}' for i in range(1, 13)]
U = lambda r: f'https://{HOST}/park/{r}'
BODY = lambda r: f'<html><head><title>Invented Park {r[-2:]}</title></head><body><h1>Invented Park {r[-2:]}</h1><p>' + 'Words about the park. ' * 40 + '</p></body></html>'
n = 0


def run(t, refused, state=None):
    global n
    n += 1
    out = t / f'out{n}'; out.mkdir()
    data = t / 'data' / 'parkinfo'; data.mkdir(parents=True, exist_ok=True)
    (data / 'US-ZZ.json').write_text(json.dumps({'parks': {r: [f'Invented Park {r[-2:]}', U(r), 'State Park', '', '', 38.5, -85.5, 0, 0, 1] for r in REFS}}), encoding='utf-8')
    (t / 'fx.json').write_text(json.dumps({'pages': {U(r): ({'status': 403, 'body': 'no'} if r in refused else {'status': 200, 'body': BODY(r)})
                                                     for r in REFS}}), encoding='utf-8')
    if state is not None: (out / 'state.json').write_text(json.dumps(state), encoding='utf-8')
    r = subprocess.run([sys.executable, '-B', str(ROOT / '.github/scripts/kpc_park_pages.py'), 'read', '--data', str(t / 'data'), '--out', str(out),
                        '--state', str(out / 'state.json'), '--fixtures', str(t / 'fx.json'), '--today', '2026-11-22', '--areas', 'US-ZZ', '--quiet'],
                       capture_output=True, text=True)
    facts = json.loads((out / 'facts' / 'US-ZZ.json').read_text()).get('parks', {}) if (out / 'facts' / 'US-ZZ.json').is_file() else {}
    asked = {ref for ref, f in facts.items() if (f.get('page') or {}).get('requests')}
    return r, facts, asked, json.loads((out / 'state.json').read_text()) if (out / 'state.json').is_file() else {}


with tempfile.TemporaryDirectory() as t:
    t = pathlib.Path(t)
    r, facts, asked, st = run(t, set(REFS[:3]))
    check('3 refused pages: the site is NOT put aside, every park is asked', r.returncode == 0 and asked == set(REFS)
          and HOST not in (st.get('refused') or {}))
    check('3 refused pages: each refused page stays refused, the others are read',
          all((facts[x].get('page') or {}).get('kind') == 'refused' for x in REFS[:3])
          and all((facts[x].get('page') or {}).get('kind') == 'html' for x in REFS[3:]))

    r, facts, asked, st = run(t, set(REFS[:9]))
    check('9 refused pages: still not put aside, the last 3 parks are asked and read', asked == set(REFS)
          and HOST not in (st.get('refused') or {}))

    r, facts, asked, st = run(t, set(REFS[:10]))
    check('10 refused pages: the site is put aside and the last 2 parks are not asked', asked == set(REFS[:10])
          and (st.get('refused') or {}).get(HOST) == '2026-11-22')

    old = {'refused': {HOST: '2026-11-22'}, 'refusal_pages': {HOST: [U(x) for x in REFS[:3]]}, 'refusal_rule': 3}
    r, facts, asked, st = run(t, set(), state=old)
    check('a site set aside under the old 3-page rule is asked again', asked == set(REFS))

    for days_ago, day, want in ((8, '2026-11-14', True), (6, '2026-11-16', False)):
        st0 = {'refused': {HOST: day}, 'refusal_pages': {HOST: [U(x) for x in REFS[:10]]}, 'refusal_rule': 10}
        r, facts, asked, st = run(t, set(), state=st0)
        check(f'a site set aside {days_ago} days ago is ' + ('asked again (rest is 7 days)' if want else 'still resting'),
              (asked == set(REFS)) if want else (not asked))
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
