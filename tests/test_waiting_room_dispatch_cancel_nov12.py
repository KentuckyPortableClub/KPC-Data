#!/usr/bin/env python3
"""Nov 12 (KPC owner, 2026-11-11): the waiting room's "A key went live -> the 2-fers rerun" step (kpc-waiting-room.yml, job waiting,
id kept_green_9) was if: always(). It started kpc-fers-pending.yml with force=yes (which starts 2-fer lines) on a CANCELLED run and
on a run whose Save never reached main, so 2-fer runs started for a key release that was not live. Checked here:
  1) parsed YAML + a small evaluator of GitHub `if:` expressions (no status function = success() && ...): the dispatch step's
     condition is false on a cancel and when Save failed / was cut / was skipped, for every value of what it reads; true on the
     green path and after an unrelated kept-green step failed (kept on purpose);
  2) the step itself, run in a temp git repo with a stand-in `gh` (no network): a release that is on main starts the rerun; a
     release that did not land (main has the old released-key.json) starts nothing; no released key = nothing;
  3) the dispatch is unchanged (kpc-fers-pending.yml, ref main, force=yes); every other step and the triggers are unchanged;
  4) a guard: every always() left in the workflow is on an allow-list with its reason.
Offline: temp folders only. Run: python3 -B tests/test_waiting_room_dispatch_cancel_nov12.py"""
import itertools, os, pathlib, re, shutil, subprocess, sys, tempfile

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
WF = ROOT / '.github/workflows'
NAME = 'kpc-waiting-room.yml'
BASE = 'da499abb53457129e764efde0688d35b2c1e0b3d'   # KPC-Data main before this fix
ok = True


def check(name, cond):
    global ok
    print(('PASS ' if cond else 'FAIL ') + name, flush=True)
    ok = ok and bool(cond)


# ------------------------------------------------------------------ a small evaluator of GitHub `if:` expressions
TOK = re.compile(r"\s*(?:(\$\{\{)|(\}\})|('(?:[^']|'')*')|(&&|\|\||==|!=|!|\(|\)|,)|([A-Za-z_][\w.\-*]*))")
STATUS = ('always', 'success', 'failure', 'cancelled')


def tokens(s):
    out, i, s = [], 0, str(s).strip()
    while i < len(s):
        m = TOK.match(s, i)
        if not m: raise ValueError(f'cannot read {s[i:i + 30]!r}')
        i = m.end()
        if m.group(1) or m.group(2): continue
        if m.group(3) is not None: out.append(('str', m.group(3)[1:-1].replace("''", "'")))
        elif m.group(4): out.append(('op', m.group(4)))
        elif m.group(5): out.append(('id', m.group(5)))
    return out


def has_status(expr): return any(t == ('id', f) for t in tokens(expr) for f in STATUS)
def truthy(v): return v not in ('', False, None, 0, '0') if not isinstance(v, bool) else v
def full(expr):
    e = 'success()' if expr in (None, '') else str(expr)
    return e if has_status(e) else f'success() && ({e})'


def evaluate(expr, ctx, fn):
    t = tokens(str(expr)); pos = [0]
    def peek(): return t[pos[0]] if pos[0] < len(t) else (None, None)
    def take(): pos[0] += 1; return t[pos[0] - 1]
    def prim():
        k, v = take()
        if (k, v) == ('op', '!'): return not truthy(prim())
        if (k, v) == ('op', '('):
            r = orx(); take(); return r
        if k == 'str': return v
        if peek() == ('op', '('):
            take(); args = []
            while peek() != ('op', ')'):
                args.append(orx())
                if peek() == ('op', ','): take()
            take()
            if v in STATUS: return fn[v]
            raise ValueError(v)
        if v in ('true', 'false'): return v == 'true'
        return ctx.get(v, '')
    def cmp():
        a = prim()
        while peek() in (('op', '=='), ('op', '!=')):
            op = take()[1]; b = prim()
            a = (str(a) == str(b)) if op == '==' else (str(a) != str(b))
        return a
    def andx():
        a = cmp()
        while peek() == ('op', '&&'): take(); b = cmp(); a = truthy(a) and truthy(b)
        return a
    def orx():
        a = andx()
        while peek() == ('op', '||'): take(); b = andx(); a = truthy(a) or truthy(b)
        return a
    return truthy(orx())


def names_of(expr):
    t = tokens(expr)
    return sorted({v for i, (k, v) in enumerate(t) if k == 'id' and v not in STATUS + ('true', 'false') and not (i + 1 < len(t) and t[i + 1] == ('op', '('))})


RESULTS = ('success', 'failure', 'cancelled', 'skipped')


def can_be_true(expr, fixed, fns):
    e = full(expr)
    free = [n for n in names_of(e) if n not in fixed]
    dom = [RESULTS if n.endswith(('.outcome', '.result', '.conclusion')) else tuple(sorted({v for k, v in tokens(e) if k == 'str'})) + ('', 'zz') for n in free]
    for combo in itertools.product(*dom):
        ctx = dict(fixed); ctx.update(zip(free, combo))
        if any(evaluate(e, ctx, fn) for fn in fns): return ctx
    return None


ON_CANCEL = [{'always': True, 'cancelled': True, 'success': False, 'failure': f} for f in (False, True)]
LIVE = [{'always': True, 'cancelled': False, 'success': s, 'failure': not s} for s in (True, False)]

text = (WF / NAME).read_text(encoding='utf-8')
W = yaml.safe_load(text)
J = W['jobs']['waiting']
steps = J['steps']
def skey(s): return s.get('id') or s.get('name') or s.get('uses')
DI = next(i for i, s in enumerate(steps) if 'kpc-fers-pending.yml/dispatches' in str(s.get('run', '')))
D = steps[DI]
SI = next(i for i, s in enumerate(steps) if str(s.get('name', '')).startswith('Save (data/waiting'))
S = steps[SI]

# ------------------------------------------------------------------ 0. what it is, unchanged parts
bad = []
for f in sorted(WF.glob('*.yml')):
    try: yaml.safe_load(f.read_text(encoding='utf-8'))
    except Exception as e: bad.append(f'{f.name}: {e}')  # noqa: BLE001
check('every workflow parses with PyYAML', not bad)
check('the dispatch step is the one reported: job waiting, id kept_green_9, "A key went live -> the 2-fers rerun"',
      D.get('id') == 'kept_green_9' and str(D.get('name', '')).startswith('A key went live -> the 2-fers rerun'))
check('it still dispatches kpc-fers-pending.yml on ref main with force=yes, only when /tmp/kpc-key-released exists',
      "gh api -X POST repos/${{ github.repository }}/actions/workflows/kpc-fers-pending.yml/dispatches -f ref=main -f 'inputs[force]=yes'" in D['run']
      and D['run'].lstrip().startswith('[ -f /tmp/kpc-key-released ] || exit 0'))
check('Save has the id kept_green_8 and runs BEFORE the dispatch', S.get('id') == 'kept_green_8' and SI < DI)
check('triggers unchanged: the two crons and workflow_dispatch', sorted(W[True]) == ['schedule', 'workflow_dispatch']
      and [c['cron'] for c in W[True]['schedule']] == ['42 */2 * * *', '13 11 * * *'])
r = subprocess.run(['git', 'show', f'{BASE}:.github/workflows/{NAME}'], cwd=ROOT, capture_output=True, text=True)
if r.returncode == 0:
    O = yaml.safe_load(r.stdout)
    os_ = O['jobs']['waiting']['steps']
    same = len(os_) == len(steps) and all(a == b for i, (a, b) in enumerate(zip(os_, steps)) if i != DI)
    check('every other step, the job settings, the triggers, permissions and concurrency are byte-for-byte the same as on main (da499ab)',
          same and {k: v for k, v in O['jobs']['waiting'].items() if k != 'steps'} == {k: v for k, v in J.items() if k != 'steps'}
          and all(O.get(k) == W.get(k) for k in (True, 'permissions', 'concurrency', 'name', 'run-name')))
    check('the old step was if: always() (the hole this fixes)', os_[DI].get('if') == 'always()')
else:
    print('INFO da499ab not in this clone: the compare with main is skipped')

# ------------------------------------------------------------------ 1. the condition
c = D.get('if')
check('dispatch condition: !cancelled() and Save\'s outcome success by id, no always()',
      '!cancelled()' in str(c) and "steps.kept_green_8.outcome == 'success'" in str(c) and 'always()' not in str(c))
check('dispatch: FALSE on a cancelled run, for every value of what it reads', can_be_true(c, {}, ON_CANCEL) is None)
for o in ('failure', 'cancelled', 'skipped'):
    check(f'dispatch: FALSE when Save\'s outcome is {o} (any other state, run not cancelled)', can_be_true(c, {'steps.kept_green_8.outcome': o}, LIVE) is None)
check('dispatch: TRUE on the green path (Save success, not cancelled)', evaluate(full(c), {'steps.kept_green_8.outcome': 'success'}, LIVE[0]))


def walk(outcome=None, cancel_after=None):
    outcome = outcome or {}; ctx = {'github.event_name': 'schedule'}; ran = {}; failed = cancelled = False   # the nightly / every-2-h run: every step is on
    for s in steps:
        k = skey(s)
        go = evaluate(full(s.get('if')), ctx, {'always': True, 'cancelled': cancelled, 'success': not failed and not cancelled, 'failure': failed})
        ran[k] = go
        if s.get('id'): ctx[f"steps.{s['id']}.outcome"] = outcome.get(k, 'success') if go else 'skipped'
        if go and outcome.get(k) == 'failure' and not s.get('continue-on-error'): failed = True
        if cancel_after == k: cancelled = True
    return ran


check('walk, green run: Save and the dispatch run', walk()['kept_green_8'] and walk()['kept_green_9'])
keys = [skey(s) for s in steps]
for at in keys[:DI]:
    check(f'walk: a cancel after step {at}: no dispatch', not walk(cancel_after=at)['kept_green_9'])
check('walk: Save failed (its outcome failure): no dispatch', not walk({'kept_green_8': 'failure'})['kept_green_9'])
check('walk: a checkout failed before Save (Save skipped): no dispatch',
      not walk({'actions/checkout@v5': 'failure'})['kept_green_9'] and not walk({'actions/checkout@v5': 'failure'})['kept_green_8'])
for k in ('kept_green_1', 'kept_green_3', 'kept_green_4', 'kept_green_5', 'kept_green_6', 'kept_green_7'):
    check(f'walk, kept on purpose: an earlier kept-green step {k} failed, the release was saved: the dispatch still runs', walk({k: 'failure'})['kept_green_9'])

# ------------------------------------------------------------------ 2. the step itself, offline: is the release on main?
run = D['run'].replace('${{ github.repository }}', 'KentuckyPortableClub/KPC-Data')
check('the step checks main (fetch + diff of data/waiting/released-key.json) BEFORE it dispatches',
      -1 < run.find('git -C kpcdata diff --quiet FETCH_HEAD -- data/waiting/released-key.json') < run.find('gh api -X POST'))


def sh(cwd, *a): return subprocess.run(list(a), cwd=cwd, capture_output=True, text=True)


def scenario(saved, flag=True):
    t = pathlib.Path(tempfile.mkdtemp(prefix='wr-dispatch-'))
    try:
        env = dict(os.environ, HOME=str(t), GIT_CONFIG_NOSYSTEM='1', GIT_AUTHOR_NAME='t', GIT_AUTHOR_EMAIL='t@t', GIT_COMMITTER_NAME='t', GIT_COMMITTER_EMAIL='t@t',
                   RUNNER_TEMP=str(t / 'rt'), GH_TOKEN='x', PATH=f"{t / 'bin'}:{os.environ.get('PATH', '')}")
        (t / 'rt').mkdir(); (t / 'bin').mkdir()
        (t / 'bin' / 'gh').write_text(f'#!/bin/sh\necho "$@" >> "{t}/gh-calls.txt"\n'); (t / 'bin' / 'gh').chmod(0o755)
        subprocess.run(['git', 'init', '-q', '--bare', '-b', 'main', str(t / 'origin.git')], env=env, check=True)
        subprocess.run(['git', 'clone', '-q', str(t / 'origin.git'), str(t / 'kpcdata')], env=env, check=True, capture_output=True)
        k = t / 'kpcdata'
        (k / 'data/waiting').mkdir(parents=True)
        (k / 'data/waiting/released-key.json').write_text('{"date": "old", "states": ["US-OH"]}\n')
        for a in (['add', '-A'], ['commit', '-qm', 'old'], ['push', '-q', 'origin', 'HEAD:main']): subprocess.run(['git', *a], cwd=k, env=env, check=True)
        (k / 'data/waiting/released-key.json').write_text('{"date": "new", "states": ["US-KY"]}\n')   # this run's release
        if saved:
            for a in (['add', '-A'], ['commit', '-qm', 'waiting room: release'], ['push', '-q', 'origin', 'HEAD:main']): subprocess.run(['git', *a], cwd=k, env=env, check=True)
        flagf = t / 'kpc-key-released'
        script = run.replace('/tmp/kpc-key-released', str(flagf))
        if flag: flagf.write_text('US-KY')
        p = subprocess.run(['bash', '-e', '-c', script], cwd=t, env=env, capture_output=True, text=True)
        calls = (t / 'gh-calls.txt').read_text() if (t / 'gh-calls.txt').exists() else ''
        return p.returncode, calls, p.stdout + p.stderr
    finally:
        shutil.rmtree(t, ignore_errors=True)


rc, calls, out = scenario(saved=True)
check('step, the release is on main: the 2-fer rerun is started (one gh call: kpc-fers-pending.yml, force=yes)',
      rc == 0 and calls.count('\n') == 1 and 'kpc-fers-pending.yml/dispatches' in calls and 'inputs[force]=yes' in calls)
rc, calls, out = scenario(saved=False)
check('step, the save did not land (main has the old released-key.json): NO rerun started, an error line says why, exit 0',
      rc == 0 and calls == '' and 'is not on main' in out)
rc, calls, out = scenario(saved=True, flag=False)
check('step, no key released this run: nothing started', rc == 0 and calls == '')

# ------------------------------------------------------------------ 3. guard: every always() left
ALLOW = {'Report hidden failures': 'G8 report: reads the steps and kpc-hidden*.txt, writes the run summary; never writes the repo, starts nothing '
                                    '(tests/test_fixbundle_hidden_failures_nov4.py requires exactly if: always() here)'}
left = [(jn, str(s.get('name', skey(s)))) for jn, j in W['jobs'].items() for s in j.get('steps') or [] if 'always()' in str(s.get('if', ''))]
left += [(jn, '(job)') for jn, j in W['jobs'].items() if 'always()' in str(j.get('if', ''))]
print('INFO always() left in kpc-waiting-room.yml:')
miss = []
for jn, sn in left:
    why = next((v for p, v in ALLOW.items() if sn.startswith(p)), None)
    print(f'INFO   {jn}: {sn[:70]} :: {why or "NOT ON THE ALLOW-LIST"}')
    if not why: miss.append(sn)
check('every always() left in the waiting room is on the allow-list with a reason (a new one fails here)', left and not miss)
WRITE_RE = re.compile(r'git push|git commit|kpc_push_data|gh workflow run|gh api[^\n]*-X (?:POST|PATCH|PUT|DELETE)|/dispatches')
check('no step that writes or starts a run is guarded by always()', not [s for s in steps if 'always()' in str(s.get('if', '')) and WRITE_RE.search(str(s.get('run', '')))])

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
