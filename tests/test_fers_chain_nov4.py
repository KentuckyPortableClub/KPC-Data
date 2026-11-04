#!/usr/bin/env python3
"""Offline test for the 2-fer chain (data-05; the chain: per Brandon via Super Head Bot (relayed), 4:55 AM CST Nov 4) and the
pre-line gate in the 2-fer line (Brandon, directly (Mapping chat), 4:52 AM CST Nov 4). No network, no gh, NO workflow is run: the workflow files are read as YAML and their steps
are run with stubs in temp folders.
  * trigger wiring: chain = workflow_run on the copy workflow (by its real name), post-line = workflow_run on the line + the chain,
    the chain calls kpc-fers-line.yml with key=build; no new cron anywhere (every schedule equals main's)
  * the pre-line check stops the line: fetcher / worker / checker need preline and run only on go == 'yes'; a missing check = HOLD
  * no release / publish: nothing in the chain releases 2-fers, writes approved.json, starts kpc-fers-publish or a release workflow;
    the checker still diverts the 2-fers into the waiting room before it saves
  * the chain plan (kpc_fers_chain_plan.py): runs an area once per new current-rules, post-checked, copied, not-NO build; keeps the
    map-audit gate; at most 3 at a time; Canada waits for its own build; Kentucky never
  * the gate: default OFF (one line), it turns ON by itself (a Brandon / KZ4CP GOOD on a 2-fer run, or 3 clean post-key + post-line
    checks in a row), stays on, and only the repo variable set by hand turns it off (per Brandon via Super Head Bot (relayed), 5:48 AM CST Nov 4)
env LINKS=<KPC-Links checkout with links-04> also runs the plan against the real kpc_key_freeze.py."""
import glob, importlib.util, json, os, pathlib, re, subprocess, sys, tempfile
import yaml

HERE = pathlib.Path(__file__).resolve().parent.parent
WF = HERE / '.github/workflows'
ok = True


def check(c, msg):
    global ok
    print(('PASS ' if c else 'FAIL ') + msg); ok = ok and bool(c)


def y(name):
    d = yaml.safe_load(open(WF / name, encoding='utf-8')); d['on'] = d.pop(True, d.get('on')); return d


line, chain, post, copy = y('kpc-fers-line.yml'), y('kpc-fers-chain.yml'), y('kpc-fers-postline.yml'), y('kpc-copy-from-links.yml')
# ---- trigger wiring
check(set(chain['on']) == {'workflow_run'} and chain['on']['workflow_run']['workflows'] == [copy['name']] and chain['on']['workflow_run']['types'] == ['completed'],
      f"chain: only workflow_run on '{copy['name']}' (the copy's real name), completed")
check(chain['jobs']['plan']['if'].replace(' ', '') == "${{github.event.workflow_run.conclusion=='success'}}", 'chain: only after a SUCCESSFUL copy')
L = chain['jobs']['line']
check(L['uses'] == './.github/workflows/kpc-fers-line.yml' and L['with']['key'] == 'build' and L['with']['force'] == 'no' and L['with']['next'] == '' and L['strategy']['max-parallel'] <= 2,
      'chain: calls kpc-fers-line.yml (workflow_call) with key=build, force=no, no next, at most 2 at a time')
check(set(post['on']) == {'workflow_run'} and post['on']['workflow_run']['workflows'] == [line['name'], chain['name']], f"post-line: only workflow_run on '{line['name']}' + '{chain['name']}' (a called line fires only its caller's name)")
check(post['jobs']['postline'].get('continue-on-error') is True and all(s.get('continue-on-error') for s in post['jobs']['postline']['steps'] if 'run' in s), 'post-line: never fails (job + steps continue on error)')
check(post['permissions'] == {'contents': 'write'} and all(re.sub(r'\s+', ' ', s['run'].split('"', 2)[2]).strip().startswith('data/status/fers-postline data/status/fers-chain ||') for s in post['jobs']['postline']['steps'] if 'kpc_push_data' in s.get('run', '')), 'post-line: saves only data/status/fers-postline + the gate state (data/status/fers-chain)')
for trig in ('workflow_dispatch', 'workflow_call'):
    i = line['on'][trig]['inputs']; check(i.get('key', {}).get('default') == 'live' and i.get('force', {}).get('default') == 'no', f'line {trig}: inputs key (default live) + force (default no)')
BASE = next((r for r in ('origin/main', 'main') if subprocess.run(['git', 'rev-parse', '-q', '--verify', r], cwd=HERE, capture_output=True).returncode == 0), 'main')   # in an apply-check clone 'main' has the patches
main_crons, now_crons = {}, {}
for f in sorted(glob.glob(str(WF / '*.yml'))):
    d = yaml.safe_load(open(f)); on = d.get(True, d.get('on')) or {}
    now_crons[os.path.basename(f)] = sorted(c['cron'] for c in (on.get('schedule') or []) if isinstance(on, dict))
for f in subprocess.run(['git', 'ls-tree', '--name-only', BASE, '.github/workflows/'], cwd=HERE, capture_output=True, text=True).stdout.split():
    d = yaml.safe_load(subprocess.run(['git', 'show', f'{BASE}:{f}'], cwd=HERE, capture_output=True, text=True).stdout); on = d.get(True, d.get('on')) or {}
    main_crons[os.path.basename(f)] = sorted(c['cron'] for c in (on.get('schedule') or []) if isinstance(on, dict))
check({k: v for k, v in now_crons.items() if v} == {k: v for k, v in main_crons.items() if v}, f'no new cron: every schedule equals {BASE}\'s (chain + post-line have none)')
# ---- the pre-line check stops the line
J = line['jobs']
check(list(J)[0] == 'preline' and J['preline']['outputs']['go'] == '${{ steps.check.outputs.go }}', 'line: preline is the first job and gives go')
for j in ('fetcher', 'worker', 'checker'):
    n = J[j]['needs']; n = [n] if isinstance(n, str) else n
    check('preline' in n and "needs.preline.outputs.go == 'yes'" in J[j]['if'], f'line: {j} needs preline and runs only on go == yes')
check('preline' not in str(J['broke'].get('needs')) and "failure" in J['broke']['if'], 'line: a HOLD (skipped jobs) is not a break (no red mail, no queue stop)')
step = next(s for s in J['preline']['steps'] if s.get('id') == 'check')['run']
for name, script, want in [('missing check (links-05 not merged)', None, 'go=no'), ('check says HOLD', 'go=no\nverdict=HOLD', 'go=no'), ('check says GO', 'go=yes\nverdict=GO', 'go=yes'), ('check crashes without output', '', '')]:
    with tempfile.TemporaryDirectory() as t:
        if script is not None:
            os.makedirs(f'{t}/.github/scripts'); open(f'{t}/.github/scripts/kpc_fers_preline.py', 'w').write(f"import os\nopen(os.environ['GITHUB_OUTPUT'],'a').write({script!r}+'\\n') if {bool(script)} else None\nraise SystemExit(0)\n")
        env = dict(os.environ, GITHUB_OUTPUT=f'{t}/o', GITHUB_STEP_SUMMARY=f'{t}/s', STATES='US-TN', RUN_TAG='tn', KEY_SOURCE='build', FORCE='no')
        subprocess.run(['bash', '-e', '-c', step], cwd=t, env=env, capture_output=True, text=True)
        out = open(f'{t}/o').read() if os.path.exists(f'{t}/o') else ''
        go = re.findall(r'^go=(\w+)', out, re.M)
        check((go[-1] if go else '') != 'yes' if want != 'go=yes' else go[-1:] == ['yes'], f'preline step: {name} -> {"GO" if want == "go=yes" else "the line does not build (go is not yes)"}')
src = open(WF / 'kpc-fers-line.yml').read()
check(src.count('[ "$KEY_SOURCE" = build ] && [ "$k" = "$BUILD_KIND" ] && continue') == 3 and '[ "$KEY_SOURCE" = build ] || cp -f kpcdata/data/us-key/$st.json' in src,
      'key=build: the 3 jobs keep the new build for its own key only; the other keys stay live (last good)')
check("KEY_SOURCE: ${{ inputs.key == 'build' && 'build' || 'live' }}" in src, 'any key value but build = live (the old behaviour)')
# ---- no release / publish
texts = {n: open(WF / n).read() for n in ('kpc-fers-chain.yml', 'kpc-fers-postline.yml', 'kpc-fers-line.yml')}
texts['kpc_fers_chain_plan.py'] = open(HERE / '.github/scripts/kpc_fers_chain_plan.py').read()
texts['kpc_fers_chain_gate.py'] = open(HERE / '.github/scripts/kpc_fers_chain_gate.py').read()
code = {n: '\n'.join(l for l in t.splitlines() if not l.lstrip().startswith('#')) for n, t in texts.items()}
for n, t in code.items():
    check(not re.search(r'kpc_release_approved|kpc-fers-publish|release-approved|WAITING_ON|approved\.json.*["\']w["\']', t), f'{n}: no release step (kpc_release_approved / release-approved / fers-publish / approved.json write)')
    for m in re.findall(r'gh workflow run (\S+)', t): check(m == 'kpc-fers-line.yml', f'{n}: the only workflow it can start is the 2-fer line itself ({m})')
    for m in sorted(set(re.findall(r'gh release (\w+) (\S+)', t))): check((m[0] in ('download', 'view') and m[1] in ('boundary-cache', 'fers-bundles')) or (m[0] in ('upload', 'create', 'view') and m[1] == 'fers-bundles'), f'{n}: gh release {m[0]} {m[1]} is the hidden bot bundle / cache, not a published 2-fer release')
sv = next(s for s in J['checker']['steps'] if s.get('name', '').startswith('Save'))['run']
check(0 < sv.find('kpc_waiting_room.py divert data/fers') < sv.find('kpc_push_data.sh'), 'checker: the 2-fers are diverted into the waiting room (HELD) before the save')
pre = next(s for s in J['preline']['steps'] if s.get('name', '').startswith('Save'))['run']
check(pre.strip().endswith('|| echo "::warning title=2-fer pre-line check::report not saved (the verdict above still holds)"') and 'data/status/fers-preline' in pre, 'preline saves only data/status/fers-preline')
# ---- the chain plan
spec = importlib.util.spec_from_file_location('plan', HERE / '.github/scripts/kpc_fers_chain_plan.py'); P = importlib.util.module_from_spec(spec); spec.loader.exec_module(P)
STUB = '''import hashlib, json, pathlib
def rules_hash(kind, root=None): return 'rules-' + kind
def verdict(kind, bid, items, links_root=None):
    f = pathlib.Path(links_root or '.') / 'data/status/key-check/verdicts' / f'{bid}.json'
    try: v = json.load(open(f)); return v['verdict'], v['by']
    except Exception: return None
'''
GNO = '''
def graded_no(kind, bid, items, links_root=None):
    v = verdict(kind, bid, items, links_root)
    return v if v and v[0].upper().startswith(('NO', 'FAIL', 'WITHDRAWN')) else None
'''


def w(p, d): p = pathlib.Path(p); p.parent.mkdir(parents=True, exist_ok=True); p.write_text(d if isinstance(d, str) else json.dumps(d))


def repo(t, kind='us-key', short='us', rules=True, post=True, arrived=True, ready=(), stub=True, bid='US-200', verdict=None, by='Quality', dirty=None):
    """ready = states whose MAP AUDIT is clean (audited.json lists them, every map-audit row answered YES / FIXED / PIN by a person).
    fers-ready.json says 'waiting for key' for EVERY state, as it does on the real repo while the new build is held: it must be ignored."""
    D, Lk = pathlib.Path(t) / 'data', pathlib.Path(t) / 'links'
    if stub: w(Lk / '.github/scripts/kpc_key_freeze.py', STUB)
    w(Lk / f'data/{kind}/index.json', {'build': bid, 'rules': f'rules-{kind}' if rules else 'old'})
    if post: w(Lk / f'data/status/key-check/last-{short}.json', {'build': bid})
    if arrived: w(D / f'data/waiting/in/data/{kind}/index.json', {'build': bid})
    w(D / 'data/status/fers-ready.json', {'areas': {a: {'status': 'waiting for key'} for v in P.R.values() for a in v.split()}})
    w(D / 'data/status/audited.json', {a: {'built': '2026-11-03', 'rows': 1, 'flagged': 1, 'source_down': 0} for a in ready})
    rows = [{'area': a, 'ref': f'{a}-1', 'record': 'x', 'answer': 'YES', 'checked_by': 'chat 2'} for a in ready]
    for a, ans in (dirty or {}).items(): rows.append({'area': a, 'ref': f'{a}-2', 'record': 'y', **({'answer': ans} if ans else {})})
    w(D / 'data/waiting/questions/map-audit.json', {'questions': rows})
    if verdict: w(Lk / f'data/status/key-check/verdicts/{bid}.json', {'verdict': verdict, 'by': by})
    return D, Lk


def run(D, Lk, gate='on'):
    sys.modules.pop('kpc_key_freeze', None); sys.path[:] = [p for p in sys.path if not p.endswith('/links/.github/scripts')]
    return P.main({'DATA': str(D), 'LINKS': str(Lk), 'GATE': gate, 'GITHUB_OUTPUT': str(D / 'gho')})


SE = P.R['southeast'].split()
ALLUS = [a for k, v in P.R.items() if not v.startswith('CA-') for a in v.split()]
# ---- FINAL-v2 (Brandon's choice, per Brandon via Super Head Bot (relayed), 5:48 AM CST Nov 4): the one default line = OFF
dl = [l for l in open(HERE / '.github/scripts/kpc_fers_chain_plan.py').read().splitlines() if l.startswith('GATE_DEFAULT')]
check(len(dl) == 1 and dl[0].startswith("GATE_DEFAULT = 'off'") and '5:48 AM CST Nov 4' in dl[0], f'the gate default is ONE line, off, citing Brandon via Super 5:48 ({dl[0][:60] if dl else "missing"})')
check(P.GATE_DEFAULT == 'off' and P.gate_mode('') == 'off' and P.gate_mode(None) == 'off', 'unset KPC_FERS_CHAIN_GATE = GATE_DEFAULT = off')
check([P.gate_mode(x) for x in ('on', 'ON', 'audit', 'off', 'Off', 'maybe', 'pending')] == ['on', 'on', 'on', 'off', 'off', 'PENDING', 'PENDING'], 'gate values: on / audit = on, off = off, anything else = PENDING')
st = chain['jobs']['plan']['steps']; ge = next(s for s in st if s.get('id') == 'plan')['env']['GATE']
check(ge.strip() == '${{ vars.KPC_FERS_CHAIN_GATE }}', f'the workflow passes the repo variable KPC_FERS_CHAIN_GATE with no default of its own ({ge})')
# ---- the key checks stop the chain in every gate mode
for g in ('on', 'off'):
    for name, kw in [('build not on the current rules', {'rules': False}), ('no links-01 post-key check yet', {'post': False}), ('build not copied to KPC-Data yet', {'arrived': False}),
                     ('graded NO by Quality', {'verdict': 'NO'}), ('graded WITHDRAWN by Brandon', {'verdict': 'WITHDRAWN', 'by': 'Brandon'})]:
        with tempfile.TemporaryDirectory() as t:
            D, Lk = repo(t, ready=ALLUS, **kw); r, s, n = run(D, Lk, g); check(r == [] and 'run=no' in (D / 'gho').read_text(), f'plan (gate {g}): nothing starts when the {name}')
# ---- gate ON: the map audit only; 'waiting for key' (the build that just finished, held) is ignored
with tempfile.TemporaryDirectory() as t:
    D, Lk = repo(t, ready=SE); r, s, n = run(D, Lk, 'on')
    check([x['tag'] for x in r] == ['southeast'] and r[0]['key'] == 'us-key' and r[0]['build'] == 'US-200', "plan (gate on): the area whose map audit is clean starts, although fers-ready.json says 'waiting for key' (the chain CAN start)")
    check(len(s['us-key']['waiting']) == 8 and all('map audit not clean' in v and 'not audited' in v for v in s['us-key']['waiting'].values()), 'plan (gate on): every other US area waits, naming its unaudited states')
    r2, s2, _ = run(D, Lk, 'on'); check(r2 == [], 'plan: the same build never starts an area twice (seen.json)')
    w(Lk / 'data/us-key/index.json', {'build': 'US-201', 'rules': 'rules-us-key'}); w(Lk / 'data/status/key-check/last-us.json', {'build': 'US-201'}); w(D / 'data/waiting/in/data/us-key/index.json', {'build': 'US-201'})
    r3, s3, _ = run(D, Lk, 'on'); check([x['tag'] for x in r3] == ['southeast'] and s3['us-key']['build'] == 'US-201', 'plan: a NEW build runs its areas again')
for name, dirty in [('an open row (no answer)', {'US-TN': None}), ("a row answered NO", {'US-TN': 'NO: outline wrong'}), ('a row answered only by a pattern', None)]:
    with tempfile.TemporaryDirectory() as t:
        D, Lk = repo(t, ready=SE, dirty=dirty)
        if dirty is None:
            Q = json.load(open(D / 'data/waiting/questions/map-audit.json')); Q['questions'][0].update(how="pattern answer 'OFF bigger'"); w(D / 'data/waiting/questions/map-audit.json', Q)
        r, s, n = run(D, Lk, 'on'); check(r == [] and 'not clean' in s['us-key']['waiting']['southeast'], f'plan (gate on): {name} keeps the area waiting')
with tempfile.TemporaryDirectory() as t:
    D, Lk = repo(t, ready=SE); w(D / 'data/waiting/questions/map-audit-auto.json', {'rows': [{'area': 'US-GA', 'auto': 'source down: the audit reads it again next run'}]})
    r, s, n = run(D, Lk, 'on'); check(r == [] and 'source down' in s['us-key']['waiting']['southeast'], 'plan (gate on): a source-down row keeps the area waiting')
with tempfile.TemporaryDirectory() as t:
    D, Lk = repo(t); r, s, n = run(D, Lk, 'on')
    check(r == [] and len(s['us-key']['waiting']) == 9, 'plan (gate on): nothing audited = every US area waits')
# ---- gate OFF: the map audit is not read
with tempfile.TemporaryDirectory() as t:
    D, Lk = repo(t); tags = []
    for i in range(4): r, s, n = run(D, Lk, gate='off'); tags.append([x['tag'] for x in r])
    flat = [x for g in tags for x in g]
    check(all(len(g) <= 3 for g in tags) and sorted(flat) == sorted(k for k, v in P.R.items() if not v.startswith('CA-')) and len(flat) == len(set(flat)), 'plan (gate off): at most 3 areas per start, every US area once, none twice')
    check('ky' not in flat and not any('US-KY' in P.R[x] for x in flat), 'plan: Kentucky (its own key) is never in the chain')
    check(not any(P.R[x].startswith('CA-') for x in flat), 'plan: a US build starts no Canada area (Canada waits for its own build)')
with tempfile.TemporaryDirectory() as t:
    D, Lk = repo(t, kind='ca-key', short='ca', bid='CA-300'); r, s, n = run(D, Lk, gate='off')
    check({x['tag'] for x in r} == {'canadaeast', 'canadawest'} and 'us-key' not in s, 'plan: a new Canada build starts the Canada areas only')
# ---- unset (the default) = off: the areas start without the map audit (still at most 3, still HELD by the line)
with tempfile.TemporaryDirectory() as t:
    D, Lk = repo(t); r, s, n = run(D, Lk, '')
    check(len(r) == 3 and any('map-audit gate off (GATE_DEFAULT' in x for x in n), 'plan (gate unset = default off): 3 areas start although nothing is audited; the log names the source of the gate')
# ---- PENDING (a repo variable that is not on / off): both answers reported, NOTHING starts, nothing remembered as run
for g in ('PENDING', 'maybe'):
    with tempfile.TemporaryDirectory() as t:
        D, Lk = repo(t, ready=SE); r, s, n = run(D, Lk, g)
        msg = ' '.join(n)
        check(r == [] and 'run=no' in (D / 'gho').read_text() and s['us-key']['ran'] == [] and 'PENDING' in msg and "if 'on': southeast;" in msg and "if 'off': southeast midwest northeast" in msg,
              f'plan (gate {g or "unset"} = PENDING): nothing starts; the run log says what on / off would start')
        r2, s2, _ = run(D, Lk, 'on'); check([x['tag'] for x in r2] == ['southeast'], f'plan: after PENDING ({g or "unset"}), setting the gate on starts the clean area (PENDING remembered nothing)')
with tempfile.TemporaryDirectory() as t:
    D, Lk = repo(t, stub=False); w(Lk / '.github/scripts/kpc_key_freeze.py', 'def check(): pass\n'); r, s, n = run(D, Lk, gate='off')
    check(r == [] and any('links-04' in x for x in n), 'plan: KPC-Links without links-04 (no rules hash) = the chain waits')
with tempfile.TemporaryDirectory() as t:
    D, Lk = repo(t, ready=SE, stub=False); w(Lk / '.github/scripts/kpc_key_freeze.py', STUB + GNO); w(Lk / 'data/status/key-check/verdicts/US-200.json', {'verdict': 'YES', 'by': 'Quality'})
    r, s, n = run(D, Lk, 'on'); check([x['tag'] for x in r] == ['southeast'], 'plan with graded_no (links-04 FINAL-v2): a YES is not a NO, the clean area starts')
    w(Lk / 'data/status/key-check/verdicts/US-200.json', {'verdict': 'FAIL', 'by': 'chat 11'}); w(D / 'data/status/fers-chain/seen.json', {})
    r, s, n = run(D, Lk, 'on'); check(r == [] and any('graded FAIL' in x for x in n), 'plan with graded_no: an old chat 11 FAIL still holds (a NO is the safe direction)')
# ---- the AUTOMATIC RE-ENABLE (kpc_fers_chain_gate.py; per Brandon via Super Head Bot (relayed), 5:48 AM CST Nov 4)
spec = importlib.util.spec_from_file_location('kpc_fers_chain_gate', HERE / '.github/scripts/kpc_fers_chain_gate.py'); CG = importlib.util.module_from_spec(spec); spec.loader.exec_module(CG)
KSTUB = STUB + GNO + '''
import datetime, re
def signed_when(rec):
    try: return datetime.datetime.strptime(str(rec.get('date')), '%Y-%m-%d %H:%M UTC').replace(tzinfo=datetime.timezone.utc)
    except Exception: return None
def is_person(by):
    names = {n.strip().lower() for n in re.split(r'[,;+&]|\band\b', str(by or '')) if n.strip()}
    return bool(names & {'brandon', 'kz4cp'})
def signoff_why(rec, now=None):
    if not str(rec.get('verdict') or '').strip(): return 'no verdict'
    if not is_person(rec.get('by')): return 'not a person'
    return '' if signed_when(rec) else 'no date'
'''
NOWT = 1793800000   # 2026-11-04 ~12:26 UTC


def grepo(t, links_real=None):
    D, Lk = repo(t, stub=False); w(Lk / '.github/scripts/kpc_key_freeze.py', KSTUB)
    if links_real: Lk = links_real
    return D, Lk


def gupd(D, Lk, now=NOWT):
    sys.modules.pop('kpc_key_freeze', None); sys.path[:] = [p for p in sys.path if not p.endswith('/links/.github/scripts')]
    return CG.update(str(D), str(Lk), now)


def postline(D, run, areas=('US-TN',), stale=(), pre='GO', held=(), error=None):
    rep = {'checked': '2026-11-05 10:00 UTC', 'run': run, 'areas': {a: {'gained': [], 'lost': [], 'touch_held': list(held), 'stale_inputs': list(stale), 'preline': {'verdict': pre}} for a in areas}}
    if error: rep['error'] = error
    w(D / 'data/status/fers-postline/latest.json', rep)
    for ar in areas: w(D / f'data/waiting/in/data/fers/{ar}.json', {'made_by': run})   # each run = a new held output (FINAL-v2 self-check)


def postkey(Lk, short='us', bad=0):
    w(Lk / f'data/status/key-check/last-{short}.json', {'build': 'US-200', 'report': f'{short}-X.json'})
    w(Lk / f'data/status/key-check/{short}-X.json', {'build': 'X', 'summary': {'0,0 / impossible pins': 0, 'signed sheet answers not followed': bad, 'must-be-pin not yet pin': 0}, 'notes': []})


check(CG.STREAK_N == 3 and sum(1 for l in open(HERE / '.github/scripts/kpc_fers_chain_gate.py') if l.startswith('STREAK_N =')) == 1, 'N = 3 clean checks in a row (one line: STREAK_N)')
pv = lambda D, name, **kw: w(D / f'data/status/fers-chain/verdicts/{name}.json', dict({'run': 'run-1', 'verdict': 'GOOD', 'by': 'Brandon', 'date': '2026-11-04 11:00 UTC'}, **kw))
with tempfile.TemporaryDirectory() as t:
    D, Lk = grepo(t); s, ch = gupd(D, Lk)
    check(s['mode'] == 'off' and CG.effective('', str(D), P.GATE_DEFAULT)[0] == 'off', 'gate state: starts off (no gate.json yet)')
    for name, kw in [('Quality', {'by': 'Quality'}), ('Super', {'by': 'Super'}), ('Brandon via Super', {'by': 'Brandon via Super'}), ('a bot', {'by': 'Mapping bot'}),
                     ('Brandon NO', {'verdict': 'NO: pairs wrong'}), ('Brandon NOT GOOD', {'verdict': 'NOT GOOD'}), ('Brandon, no date', {'date': ''}),
                     ('Brandon, dated before Nov 4 (old 2-fer approvals)', {'date': '2026-10-30 15:00 UTC'})]:
        pv(D, 'v', **kw); s, ch = gupd(D, Lk); check(s['mode'] == 'off', f'gate: a GOOD from {name} does NOT turn it on')
    w(D / 'data/waiting/approved.json', {'items': [{'what': 'fers-US-HI', 'chat11': 'YES 2026-11-05', 'by': 'chat 11', 'date': '2026-11-04 11:00 UTC'}]})
    s, ch = gupd(D, Lk); check(s['mode'] == 'off', 'gate: an old chat 11 YES in approved.json does NOT turn it on')
    pv(D, 'v', by='Brandon'); s, ch = gupd(D, Lk)
    check(s['mode'] == 'on' and ch and 'Brandon graded a 2-fer run good' in s['why'] and len(s['history']) == 1, 'gate: the first Brandon GOOD on a 2-fer run turns it ON (one status line in gate.json)')
    log = (D / CG.LOG).read_text(); check(log.count('turned ON by itself') == 1 and 'only Brandon turns it off by hand' in log and 'stay held' in log, 'gate: the flip writes ONE status line to gate-log.md')
    check(CG.effective('', str(D), P.GATE_DEFAULT) == ('on', f'turned on by itself ({CG.STATE})'), 'effective gate: unset variable + gate.json on = on')
    r, s2, n = run(D, Lk, ''); check(r == [] and any('map-audit gate on (turned on by itself' in x for x in n), 'plan after the flip: the gate is on (nothing audited = nothing starts)')
    pv(D, 'v', verdict='NO'); postline(D, 'bad', stale=['x']); s, ch = gupd(D, Lk)
    check(s['mode'] == 'on' and not ch and (D / CG.LOG).read_text().count('turned ON') == 1, 'gate: once on it STAYS on (a later NO / a dirty report never turns it off; no second line)')
    check(CG.effective('off', str(D), P.GATE_DEFAULT)[0] == 'off' and CG.effective('OFF', str(D), P.GATE_DEFAULT)[1].endswith('(set by hand)'), "gate: Brandon's repo variable KPC_FERS_CHAIN_GATE=off (by hand) always wins over gate.json")
    r, s2, n = run(D, Lk, 'off'); check(len(r) == 3, 'plan: manual off by the repo variable starts areas without the audit even after the flip')
    check(json.load(open(D / CG.STATE))['mode'] == 'on', 'manual off does not rewrite gate.json (removing the variable puts the gate back on)')
with tempfile.TemporaryDirectory() as t:
    D, Lk = grepo(t); w(D / 'data/waiting/approved.json', {'items': [{'what': 'fers-US-TN', 'verdict': 'YES', 'by': 'KZ4CP', 'date': '2026-11-04 11:00 UTC'}]})
    s, ch = gupd(D, Lk); check(s['mode'] == 'on' and 'KZ4CP' in s['why'], 'gate: a KZ4CP YES on a fers- item in approved.json turns it on')
with tempfile.TemporaryDirectory() as t:
    D, Lk = grepo(t); postkey(Lk)
    streak = []
    for rid, kw in [('r1', {}), ('r1', {}), ('r2', {}), ('r3', {'stale': ['key newer']}), ('r4', {}), ('r5', {'areas': ()}), ('r6', {'pre': 'HOLD'}), ('r7', {}), ('r8', {'held': ['US-1+US-2']}), ('r9', {'error': 'boom'})]:
        postline(D, rid, **kw); s, ch = gupd(D, Lk); streak.append(s['streak'])
    check(streak == [1, 1, 2, 0, 1, 1, 0, 1, 0, 0] and s['mode'] == 'off', f'gate: the streak counts each post-line run once; stale / not GO / held-park pairs / an error put it back to 0; an empty report does not count ({streak})')
    # FINAL-v2 self-check: the chain runs after every hourly copy and the post-line check after every chain run, so ONE unchanged
    # held output is re-checked every hour under a new run link: that must count once, not three times
    postline(D, 's1'); s0 = gupd(D, Lk)[0]['streak']; rep = json.load(open(D / 'data/status/fers-postline/latest.json'))
    hourly = []
    for rid in ('s1-hour2', 's1-hour3', 's1-hour4'):
        rep['run'] = rid; w(D / 'data/status/fers-postline/latest.json', rep); s, ch = gupd(D, Lk); hourly.append((s['streak'], ch))
    check(s0 == 1 and hourly == [(1, False), (1, False), (1, False)] and s['mode'] == 'off',
          f'gate: the same held 2-fer output re-checked hourly (new run link, no new output) counts ONCE and saves nothing ({s0} {hourly})')
    postkey(Lk, bad=2)
    for rid in ('p1', 'p2', 'p3', 'p4'): postline(D, rid); s, ch = gupd(D, Lk)
    check(s['mode'] == 'off' and s['streak'] == 0 and 'signed sheet answers not followed 2' in s['last_check']['why'], 'gate: a post-key check that is not clean (links-01) is not a clean check: it never turns on')
    postkey(Lk)
    for i, rid in enumerate(('c1', 'c2', 'c3')):
        postline(D, rid); s, ch = gupd(D, Lk); check(s['mode'] == ('on' if i == 2 else 'off'), f'gate: clean check {i + 1} of 3 -> {s["mode"]}')
    check('3 clean post-key + 2-fer post-line checks in a row' in s['why'] and len(s['history']) == 1, 'gate: 3 clean in a row turned it on (its status line names why)')
with tempfile.TemporaryDirectory() as t:
    D, Lk = grepo(t); postkey(Lk)
    for rid in ('k1', 'k2', 'k3'): postline(D, rid, areas=('CA-ON',)); s, _ = gupd(D, Lk)
    check(s['mode'] == 'off' and 'ca: no post-key check report' in s['last_check']['why'], 'gate: a Canada area needs the Canada post-key check')
with tempfile.TemporaryDirectory() as t:
    D, Lk = grepo(t); pv(D, 'v')
    sys.modules.pop('kpc_key_freeze', None); P.main({'DATA': str(D), 'LINKS': str(Lk), 'GATE': '', 'GITHUB_OUTPUT': str(D / 'gho')})
    check('gate_changed=yes' in (D / 'gho').read_text() and json.load(open(D / CG.STATE))['mode'] == 'on', 'plan main(): a flip is saved (gate_changed=yes -> the workflow pushes data/status/fers-chain)')
pst = next(s for s in chain['jobs']['plan']['steps'] if 'kpc_push_data' in s.get('run', ''))
check("steps.plan.outputs.gate_changed == 'yes'" in pst['if'] and 'data/status/fers-chain' in pst['run'], 'chain workflow: saves data/status/fers-chain when the gate state changed')
ps = post['jobs']['postline']['steps']; iu = next(i for i, s in enumerate(ps) if 'kpc_fers_chain_gate.py update' in s.get('run', '')); isv = next(i for i, s in enumerate(ps) if 'kpc_push_data' in s.get('run', ''))
check(iu < isv and 'data/status/fers-chain' in ps[isv]['run'] and ps[iu].get('continue-on-error'), 'post-line workflow: counts each report (gate update) before the save, and saves the gate state; never fails')
gsrc = '\n'.join(l for l in open(HERE / '.github/scripts/kpc_fers_chain_gate.py').read().split('"""', 2)[2].splitlines() if not l.lstrip().startswith('#'))   # the code (no docstring, no comments)
check(not re.search(r"kpc_release_approved|kpc-fers-publish|gh workflow run|['\"]mode['\"]:\s*['\"]off|mode='off', since", gsrc) and "s['mode'] = 'off'" in gsrc and gsrc.count("mode='on'") == 1,
      'gate module: releases nothing, starts nothing, never writes off over on (only an unset state is written as off)')
if os.environ.get('LINKS'):
    real = pathlib.Path(os.environ['LINKS'])
    with tempfile.TemporaryDirectory() as t:
        D = pathlib.Path(t) / 'data'
        for who, want in (('Brandon', 'on'), ('KZ4CP', 'on'), ('Quality', 'off'), ('Brandon via Super', 'off')):
            sh = pathlib.Path(t) / who.replace(' ', '_'); pv(sh, 'v', by=who); s, _ = gupd(sh, real)
            check(s['mode'] == want, f'gate with the REAL kpc_key_freeze person rules: a GOOD by {who} -> {want}')
if os.environ.get('LINKS'):
    real = pathlib.Path(os.environ['LINKS'])
    with tempfile.TemporaryDirectory() as t:
        D = pathlib.Path(t) / 'data'; w(D / 'data/status/fers-ready.json', {'areas': {}})
        sys.modules.pop('kpc_fers_gate', None)
        for k in ('us-key', 'ca-key'): w(D / f'data/waiting/in/data/{k}/index.json', json.load(open(real / f'data/{k}/index.json')))
        r, s, n = run(D, real, gate='off')
        check(r == [] and any('not a full build on the current rules' in x for x in n), f'plan with the REAL KPC-Links (today): the old builds are not on the current rules, nothing starts ({"; ".join(n)[:160]})')
print('ALL PASS' if ok else 'SOME FAILED'); sys.exit(0 if ok else 1)
