#!/usr/bin/env python3
"""2-fer chain start per AREA (owner rule, 2026-11-10). Offline: fake index / status files in temp folders, no network.
  * an area starts when each of its states was built green on the current rules (per-state 'rules' rows), so one short state
    no longer blocks every US area; a failed, unmarked or missing state never feeds 2-fers
  * 2-fers are US + Canada only: world areas never start
  * an area is remembered by a fingerprint (its key files + the 2-fer rules); it is done only when its line wrote READY; a held
    line may start again after a while, at most twice; a new build id with the same files does not rerun it
  * a park the post-key check lists as a worse grade / outline -> pin holds its area
  * the key gate (kpc_fers_key_gate.py) uses the same per-state test: rules_of_run alone is never a GO"""
import importlib.util, json, os, pathlib, shutil, subprocess, sys, tempfile, time

HERE = pathlib.Path(__file__).resolve().parent.parent
REAL_LINKS = HERE.parent / 'kpc-links'
ok = True


def check(c, msg):
    global ok
    print(('PASS ' if c else 'FAIL ') + msg); ok = ok and bool(c)


spec = importlib.util.spec_from_file_location('kpc_fers_chain_plan', HERE / '.github/scripts/kpc_fers_chain_plan.py')
P = importlib.util.module_from_spec(spec); spec.loader.exec_module(P)
STUB = '''import json, pathlib
def rules_hash(kind, root=None): return 'cur-' + kind
def verdict(kind, bid, items, links_root=None): return None
def graded_no(kind, bid, items, links_root=None): return None
'''


def w(p, d): p = pathlib.Path(p); p.parent.mkdir(parents=True, exist_ok=True); p.write_text(d if isinstance(d, str) else json.dumps(d))


def repo(t, rows, rules='old', failed=(), report=None, ready_module=False):
    D, Lk = pathlib.Path(t) / 'data', pathlib.Path(t) / 'links'
    w(Lk / '.github/scripts/kpc_key_freeze.py', STUB)
    if ready_module and (REAL_LINKS / '.github/scripts/kpc_fers_ready.py').exists():
        shutil.copy(REAL_LINKS / '.github/scripts/kpc_fers_ready.py', Lk / '.github/scripts/kpc_fers_ready.py')
        shutil.copy(REAL_LINKS / '.github/fers-ready-areas.json', Lk / '.github/fers-ready-areas.json')
    w(Lk / 'data/us-key/index.json', {'build': 'US-9', 'rules': rules, 'rules_of_run': 'cur-us-key', 'failed': list(failed), 'states': rows})
    w(Lk / 'data/world-key/index.json', {'build': 'W-9', 'rules': 'cur-world-key'})
    w(Lk / 'data/status/key-check/last-us.json', {'build': 'US-9', **({'report': 'us-X.json'} if report is not None else {})})
    w(Lk / 'data/status/key-check/last-world.json', {'build': 'W-9'})
    if report is not None: w(Lk / 'data/status/key-check/us-X.json', {'changes': report})
    w(Lk / 'data/us-key/US-OH.json', {'parks': {'US-0001': {}, 'US-0002': {}}})
    w(D / 'data/us-key/index.json', {'build': 'US-9'}); w(D / 'data/world-key/index.json', {'build': 'W-9'})
    return D, Lk


def run(D, Lk, now=None):
    for m in ('kpc_key_freeze', 'kpc_fers_ready'): sys.modules.pop(m, None)
    sys.path[:] = [p for p in sys.path if not p.endswith('/links/.github/scripts')]
    return P.main({'DATA': str(D), 'LINKS': str(Lk), 'GATE': 'off', 'GITHUB_OUTPUT': str(D / 'gho')}) if now is None else _plan(D, Lk, now)


def _plan(D, Lk, now):
    for m in ('kpc_key_freeze', 'kpc_fers_ready'): sys.modules.pop(m, None)
    r, seen, n = P.plan(str(D), str(Lk), 'off', 3, now)
    w(D / 'data/status/fers-chain/seen.json', seen)
    return r, seen, n


green = lambda *sts, rules='cur-us-key': {s: {'parks': 1, 'rules': rules} for s in sts}
# KPC owner, 2026-11-12: the chain reads the ONE area list (.github/fers-areas.json); the old one-state chain areas (oh / mi / ut) are
# retired, so these cases use whole areas: greatlakes (OH MI IN) and newyork (NY NJ)
# Nov 13 CHANGED (KPC owner): greatlakes was split for memory (IL and WI are the lakeswest line now), so GL is its three states
GL = ('OH', 'MI', 'IN'); NYA = ('NY', 'NJ')
# ---- the per-state test
idx = {'rules': 'old', 'failed': ['FL'], 'states': {'OH': {'rules': 'cur'}, 'TN': {'rules': 'old'}, 'FL': {'rules': 'cur'}, 'GA': {'rules': 'cur', '_not_built': 1}}}
bad = dict(P.states_not_green(idx, 'us-key', ['US-OH', 'US-TN', 'US-FL', 'US-GA', 'US-MS'], 'cur'))
check(set(bad) == {'US-TN', 'US-FL', 'US-GA', 'US-MS'} and 'failed' in bad['US-FL'] and 'not built' in bad['US-GA'] and 'not built' in bad['US-MS'],
      f'per-state test: only a state built green on the current rules passes ({bad})')
check(P.states_not_green({'rules': 'cur'}, 'ca-key', ['CA-ON'], 'cur') == [] and P.states_not_green({'rules': 'old'}, 'ca-key', ['CA-ON'], 'cur'),
      'a key without per-state rows: the key-wide full-build rules decide')
# ---- a partial US build: the green area starts, the others wait (one short state no longer blocks all)
with tempfile.TemporaryDirectory() as t:
    D, Lk = repo(t, {**green(*GL, *NYA), 'UT': {'rules': 'old'}}, failed=['DE'])
    r, s, n = run(D, Lk)
    tags = [x['tag'] for x in r]
    check(tags == ['newyork', 'greatlakes'], f'a partial build on new rules starts the areas whose states are all green ({tags})')
    wt = s['us-key']['waiting']
    check('southeast' in wt and 'not built' in wt['southeast'] and 'mountain' in wt and 'US-UT (not built on the current rules' in wt['mountain'] and 'US-DE (failed' in wt.get('midatlantic', ''), 'an area with a state not built green waits and says which')
    check(not any(x['key'] == 'world-key' for x in r) and 'world-key' not in s or not (s.get('world-key') or {}).get('ran'), 'world areas never start (2-fers are US + Canada only)')
with tempfile.TemporaryDirectory() as t:
    D, Lk = repo(t, green(*GL), ready_module=True)
    r, s, n = run(D, Lk)
    check([x['tag'] for x in r] == ['greatlakes'] and not (s.get('world-key') or {}).get('ran'), "with KPC-Links' fers-ready-areas.json: greatlakes starts, the world areas are skipped")
# ---- fingerprint + done only on a READY line + retry
with tempfile.TemporaryDirectory() as t:
    D, Lk = repo(t, green(*GL))
    t0 = 1794300000
    r, s, _ = _plan(D, Lk, t0); check([x['tag'] for x in r] == ['greatlakes'] and s['us-key']['areas']['greatlakes']['tries'] == 1, 'first plan starts greatlakes')
    r, s, _ = _plan(D, Lk, t0 + 3600); check(r == [] and 'waiting for its result' in s['us-key']['waiting'].get('greatlakes', ''), 'an hour later: greatlakes waits for its line result (not started twice)')
    w(D / 'data/fers/line-greatlakes.json', {'verdict': 'STOPPED', 'date': time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(t0 + 7200))})
    r, s, _ = _plan(D, Lk, t0 + 7 * 3600); check([x['tag'] for x in r] == ['greatlakes'] and s['us-key']['areas']['greatlakes']['tries'] == 2, 'a line that held (STOPPED) is started again later')
    r, s, _ = _plan(D, Lk, t0 + 14 * 3600); check(r == [] and 'a person looks' in s['us-key']['waiting'].get('greatlakes', ''), 'after two starts without READY: a person looks (no endless reruns)')
    w(D / 'data/waiting/in/data/fers/line-greatlakes.json', {'verdict': 'READY FOR CHAT 8', 'date': time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(t0 + 8 * 3600))})
    r, s, _ = _plan(D, Lk, t0 + 15 * 3600); check(r == [] and 'greatlakes' in s['us-key']['ran'] and 'greatlakes' not in s['us-key']['waiting'], 'a READY line (its waiting-room copy) marks the area done')
    w(Lk / 'data/us-key/index.json', {'build': 'US-10', 'rules': 'old', 'states': green(*GL)}); w(Lk / 'data/status/key-check/last-us.json', {'build': 'US-10'}); w(D / 'data/us-key/index.json', {'build': 'US-10'})
    r, s, _ = _plan(D, Lk, t0 + 16 * 3600); check(r == [], 'a new build id with the same OH key file does not rerun greatlakes')
    w(Lk / 'data/us-key/US-OH.json', {'parks': {'US-0001': {'m': [[1, 'x']]}}})
    r, s, _ = _plan(D, Lk, t0 + 17 * 3600); check([x['tag'] for x in r] == ['greatlakes'] and s['us-key']['areas']['greatlakes']['tries'] == 1, 'a changed OH key file runs greatlakes again (new fingerprint)')
# ---- the post-key check must be clean for the area
with tempfile.TemporaryDirectory() as t:
    D, Lk = repo(t, green(*GL, *NYA), report={'grade_worse': ['US-0002'], 'outline_to_pin': []})
    r, s, _ = run(D, Lk)
    check([x['tag'] for x in r] == ['newyork'] and 'worse grade' in s['us-key']['waiting'].get('greatlakes', ''), 'a park with a worse grade in the post-key check holds its area (greatlakes, US-OH), others start')
with tempfile.TemporaryDirectory() as t:
    D, Lk = repo(t, green(*GL), report={'outline_to_pin': ['US-0001']})
    r, s, _ = run(D, Lk); check(r == [] and 'outline -> pin' in s['us-key']['waiting'].get('greatlakes', ''), 'a park gone outline -> pin holds its area')
with tempfile.TemporaryDirectory() as t:
    D, Lk = repo(t, green(*GL), report={}); (Lk / 'data/status/key-check/us-X.json').write_text('{not json')
    r, s, n = run(D, Lk); check(r == [] and any('could not be read' in x for x in n), 'a post-key check report that cannot be read starts nothing')
# ---- the key gate: same per-state test
G = HERE / '.github/scripts/kpc_fers_key_gate.py'
FREEZE = 'import sys\nif sys.argv[1:2] == ["rules"]: print("cur-" + sys.argv[2])\n'
for name, rows, failed, states, want in [('green state', green('OH'), [], 'US-OH', 0), ('state built on old rules (rules_of_run is current)', {'OH': {'rules': 'old'}}, [], 'US-OH', 1),
                                         ('failed state', green('FL'), ['FL'], 'US-FL', 1), ('state with no row', green('OH'), [], 'US-MS', 1),
                                         ('whole-region run with one state not green', {**green('OH'), 'UT': {'rules': 'old'}}, [], '', 1)]:
    with tempfile.TemporaryDirectory() as t:
        t = pathlib.Path(t); w(t / '.github/scripts/kpc_key_freeze.py', FREEZE)
        w(t / 'data/us-key/index.json', {'build': 'US-9', 'rules': 'old', 'rules_of_run': 'cur-us-key', 'failed': failed, 'states': rows})
        w(t / 'data/ca-key/index.json', {'build': 'CA-9', 'rules': 'cur-ca-key'})
        p = subprocess.run([sys.executable, str(G)], cwd=t, env=dict(os.environ, REGION='na', STATES=states), capture_output=True, text=True)
        check(p.returncode == want, f'key gate: {name} -> {"GO" if want == 0 else "refused"} ({p.stdout.strip().splitlines()[-1][:120] if p.stdout.strip() else p.stderr[-200:]})')
print('ALL_OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
