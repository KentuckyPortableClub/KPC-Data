#!/usr/bin/env python3
"""Nov 12 (KPC owner, 2026-11-11): in the 2-fer chain, nothing that SAVES (commit, push, release asset, dispatch, run cancel) may run
on a CANCELLED run, and the Save of a line may not run when its upstream build (fetcher / worker) or its verdict failed. Background:
tonight's world key run was cancelled and still committed, because its join job ran on always() (KPC-Links, world-gate-cancel).
The same pattern was in kpc-fers-line.yml (worker / checker jobs, the checker's Save, the pre-line report save, the broke job) and in
kpc-fers-lines.yml (the again job). kpc-fers.yml was already fixed on Nov 8 (6f1fdea; prefix kept by 95e4a78).
Checked here, on the parsed YAML, with a small evaluator of GitHub `if:` expressions (no status function = success() && ...):
  1) every writing job / step of kpc-fers.yml, kpc-fers-line.yml, kpc-fers-lines.yml: its condition is FALSE on a cancelled run for
     every value of the other names it reads (brute force over the literals of the expression); the allow-listed carry-on bundle
     uploads are the only exception (reason below);
  2) it is FALSE when its upstream build / checker / verdict failed;
  3) the verdict (line: Check, which must leave a fresh line-<tag>.json; kpc-fers.yml: key gate + Look) runs BEFORE the Save;
  4) the intended paths still save: all green; an 'out of time, saved, next run carries on' pass (exit 0, or a step time-out under
     continue-on-error); stage=worker / stage=checker by hand; a broken line is recorded; the again job still runs after a failed
     line (the water retry is intended), never after a cancel;
  5) a guard: every always() left in these workflows is on an allow-list with its reason; a new always() fails this test.
Offline: reads files only. Run: python3 -B tests/test_fers_save_not_on_cancel_nov12.py"""
import itertools, pathlib, re, subprocess, sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
WF = ROOT / '.github/workflows'
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


def names_of(expr):
    t = tokens(expr)
    return sorted({v for i, (k, v) in enumerate(t) if k == 'id' and v not in STATUS + ('true', 'false', 'startsWith', 'contains')
                   and not (i + 1 < len(t) and t[i + 1] == ('op', '('))})


def literals(expr): return sorted({v for k, v in tokens(expr) if k == 'str'})


def evaluate(expr, ctx, fn):
    """ctx: dotted name -> value ('' when unknown); fn: status function name -> bool."""
    if isinstance(expr, bool): return expr
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
            if v == 'startsWith': return str(args[0]).lower().startswith(str(args[1]).lower())
            if v == 'contains': return str(args[1]).lower() in str(args[0]).lower()
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


def full(expr):
    e = 'success()' if expr is None or expr == '' else str(expr)
    return e if has_status(e) else f'success() && ({e})'


RESULTS = ('success', 'failure', 'cancelled', 'skipped')


def domain(name, expr):
    if name.endswith('.result') or name.endswith('.outcome') or name.endswith('.conclusion'): return RESULTS
    return tuple(literals(expr)) + ('', 'zz')


def can_be_true(expr, fixed, fns_list):
    """Is there ANY value of the names the expression reads (besides the fixed ones) and any of the status-function sets in
    fns_list that makes it true? Returns the first such assignment, or None."""
    e = full(expr)
    free = [n for n in names_of(e) if n not in fixed]
    for combo in itertools.product(*[domain(n, e) for n in free]):
        ctx = dict(fixed); ctx.update(zip(free, combo))
        for fn in fns_list:
            if evaluate(e, ctx, fn): return ctx, fn
    return None


ON_CANCEL = [{'always': True, 'cancelled': True, 'success': False, 'failure': f} for f in (False, True)]
NOT_CANCELLED = [{'always': True, 'cancelled': False, 'success': s, 'failure': not s} for s in (True, False)]

# ------------------------------------------------------------------ what writes
WRITE_RE = re.compile(r'git push|git commit|kpc_push_data|kpc_save_overwrite|gh release (?:upload|create|delete)|kpc_keep2|gh workflow run|'
                      r'gh run cancel|gh api[^\n]*-X (?:POST|PATCH|PUT|DELETE)|kpc_archive\.sh put|/dispatches')


def step_writes(s): return bool(WRITE_RE.search(str(s.get('run') or '')))
def job_writes(j): return bool(j.get('uses')) or any(step_writes(s) for s in j.get('steps') or [])
def skey(s): return s.get('id') or s.get('name') or s.get('uses')


def load(name, text=None):
    return yaml.safe_load(text if text is not None else (WF / name).read_text(encoding='utf-8'))


CHAIN = ['kpc-fers.yml', 'kpc-fers-line.yml', 'kpc-fers-lines.yml']
D = {n: load(n) for n in CHAIN}

# Steps that write and are allowed to keep always() (they are the line's carry-on: see the report). Key: (workflow, job, step name prefix)
ALLOW_WRITE = {
    ('kpc-fers-line.yml', 'fetcher', 'Bundle up'): 'release asset bundle-<tag> (cache of map answers + this area\'s working files), not git; '
        'the only thing that keeps a fetcher cut by its 355-minute job limit (a GitHub cancel); its old copy stays as .prev; nothing in it '
        'reaches git unless a later checker grades it',
    ('kpc-fers-line.yml', 'worker', 'Bundle up'): 'same: "a worker out of time can be run again alone (stage = worker) from the bundle"; '
        'the checker no longer starts on a cancel, so a cut bundle is never saved to git by this run',
}
# Every other always() left: read-only reports
ALLOW_READ = {'Report hidden failures': 'G8 report: reads the steps and kpc-hidden*.txt, writes the run summary, may exit 1 (red); never writes the repo'}


def holes(docs):
    """Writing jobs / steps whose condition can be true on a cancelled run (allow-list excluded)."""
    out = []
    for wn, d in docs.items():
        for jn, j in (d.get('jobs') or {}).items():
            if job_writes(j):
                r = can_be_true(j.get('if'), {}, ON_CANCEL)
                if r: out.append((wn, jn, '(job)', j.get('if')))
            for s in j.get('steps') or []:
                if not step_writes(s): continue
                if any(wn == a and jn == b and str(s.get('name', '')).startswith(c) for a, b, c in ALLOW_WRITE): continue
                if can_be_true(s.get('if'), {}, ON_CANCEL): out.append((wn, jn, s.get('name') or skey(s), s.get('if')))
    return out


# ------------------------------------------------------------------ 0. every workflow parses; no new trigger, no cron change
bad = []
for f in sorted(WF.glob('*.yml')):
    try: yaml.safe_load(f.read_text(encoding='utf-8'))
    except Exception as e: bad.append(f'{f.name}: {e}')  # noqa: BLE001
check('every workflow parses with PyYAML', not bad)
check('kpc-fers.yml: triggers unchanged (one monthly cron + dispatch)',
      sorted(D['kpc-fers.yml'][True]) == ['schedule', 'workflow_dispatch'] and [c['cron'] for c in D['kpc-fers.yml'][True]['schedule']] == ['23 8 5 * *'])
check('kpc-fers-line.yml: triggers unchanged (dispatch + workflow_call, no schedule)', sorted(D['kpc-fers-line.yml'][True]) == ['workflow_call', 'workflow_dispatch'])
check('kpc-fers-lines.yml: triggers unchanged (dispatch only, no schedule)', sorted(D['kpc-fers-lines.yml'][True]) == ['workflow_dispatch'])

# ------------------------------------------------------------------ 1. nothing that writes can run on a cancelled run
h = holes(D)
for x in h: print('INFO hole:', x)
check('every writing job and step of the 2-fer chain is FALSE on a cancelled run, for every value of what it reads (allow-list apart)', not h)
wr = [(wn, jn, skey(s)) for wn, d in D.items() for jn, j in d['jobs'].items() for s in j.get('steps') or [] if step_writes(s)]
check(f'the brute force saw the writing steps ({len(wr)} of them, at least the 3 Saves, the bundle uploads, the broke record, the again saves)', len(wr) >= 10)

# the old shape (da499ab, before this fix) is caught by the same check: proof that the check sees the hole
old = {}
for n in CHAIN[1:]:
    r = subprocess.run(['git', 'show', f'da499abb53457129e764efde0688d35b2c1e0b3d:.github/workflows/{n}'], cwd=ROOT, capture_output=True, text=True)
    if r.returncode == 0: old[n] = load(n, r.stdout)
if len(old) == 2:
    oh = holes(old)
    for x in oh: print('INFO old hole (da499ab):', x[:3])
    names = {(w, j, s) for w, j, s, _ in oh}
    check('the same check finds the old holes on da499ab: line worker + checker jobs, the line Save, the pre-line report save, broke, again',
          {('kpc-fers-line.yml', 'worker', '(job)'), ('kpc-fers-line.yml', 'checker', '(job)'), ('kpc-fers-line.yml', 'checker', 'Save (once; a failed save = a red run)'),
           ('kpc-fers-line.yml', 'preline', 'Save the pre-line report (only data/status/fers-preline)'), ('kpc-fers-line.yml', 'broke', '(job)'),
           ('kpc-fers-lines.yml', 'again', '(job)')} <= names)
else:
    print('INFO da499ab not in this clone: the old-shape check is skipped')

# ------------------------------------------------------------------ helpers to walk jobs and steps
def job_go(d, jn, results, outputs=None, inputs=None, cancelled=False):
    j = d['jobs'][jn]
    ctx = {f'inputs.{k}': v for k, v in (inputs or {}).items()}
    for n, r in results.items(): ctx[f'needs.{n}.result'] = r
    for n, o in (outputs or {}).items():
        for k, v in o.items(): ctx[f'needs.{n}.outputs.{k}'] = v
    need = j.get('needs') or []; need = [need] if isinstance(need, str) else need
    allok = all(results.get(n) == 'success' for n in need)
    return evaluate(full(j.get('if')), ctx, {'always': True, 'cancelled': cancelled, 'success': allok and not cancelled,
                                             'failure': any(results.get(n) == 'failure' for n in need)}), ctx


def walk(d, jn, ctx, outcome=None, outputs=None, cancel_after=None):
    """Steps through their `if:`; outcome: step key -> 'failure'; a cancel DURING the job (cancel_after) makes success() false."""
    outcome, outputs = outcome or {}, outputs or {}
    ran, failed, cancelled = {}, False, False
    for s in d['jobs'][jn]['steps']:
        k = skey(s)
        go = evaluate(full(s.get('if')), ctx, {'always': True, 'cancelled': cancelled, 'success': not failed and not cancelled, 'failure': failed})
        ran[k] = go
        if s.get('id'):
            ctx[f"steps.{s['id']}.outcome"] = (outcome.get(k, 'success')) if go else 'skipped'
            for kk, v in (outputs.get(k) or {}).items():
                if go: ctx[f"steps.{s['id']}.outputs.{kk}"] = v
        if go and outcome.get(k) == 'failure' and not s.get('continue-on-error'): failed = True
        if cancel_after and k == cancel_after: cancelled = True
    return ran, ('cancelled' if cancelled else 'failure' if failed else 'success')


L, LS, F = D['kpc-fers-line.yml'], D['kpc-fers-lines.yml'], D['kpc-fers.yml']
PRE = {'preline': {'wait': '0', 'go': 'yes', 'verdict': 'GO'}}
ALL = {'stage': 'all', 'tag': 'mi', 'states': 'US-MI'}
SAVE = 'Save (once; a failed save = a red run)'
CHECK_OUT = {'kept_green_10': {'verdict': 'written'}}


def line(stage='all', fetcher='success', worker='success', cancelled=False, pre=PRE, check_outcome=None, check_out=CHECK_OUT, cancel_after=None):
    inp = dict(ALL, stage=stage)
    res = {'preline': 'success', 'fetcher': fetcher}
    w, _ = job_go(L, 'worker', res, pre, inp, cancelled)
    res['worker'] = worker if w else 'skipped'
    c, ctx = job_go(L, 'checker', res, pre, inp, cancelled)
    saved = False
    if c:
        ran, _ = walk(L, 'checker', ctx, check_outcome, check_out, cancel_after)
        saved = ran[SAVE]
    b, _ = job_go(L, 'broke', {'fetcher': fetcher, 'worker': res['worker']}, {}, inp, cancelled)
    return {'worker': w, 'checker': c, 'save': saved, 'broke': b}


# ------------------------------------------------------------------ 2. kpc-fers-line.yml
r = line()
check('line, all green: worker, checker and Save run; no broke', r['worker'] and r['checker'] and r['save'] and not r['broke'])
check('line: a cancel after the fetcher finished green: the worker does not start, nothing is saved', not any(line(cancelled=True).values()))
check('line: a cancel after the worker finished green: the checker does not start, no Save', not line(cancelled=True)['checker'] and not line(cancelled=True)['save'])
r = line(worker='failure')
check('line: a failed worker: no checker, no Save; the break is recorded (broke runs)', not r['checker'] and not r['save'] and r['broke'])
r = line(fetcher='failure')
check('line: a failed fetcher: no worker, no checker, no Save; the break is recorded', not r['worker'] and not r['checker'] and not r['save'] and r['broke'])
check('line: a failed worker on a cancelled run (the queue was stopped): broke does not start', not line(worker='failure', cancelled=True)['broke'])
check('line: a cancelled worker: no checker, no Save, no broke', not any(v for k, v in line(worker='cancelled').items() if k != 'worker'))
check('line: pre-line HOLD: no worker, no checker, no Save', not any(line(pre={'preline': {'wait': '0', 'go': 'no'}}).values()))
check('line: waiting for the saved-copy reader: nothing runs', not any(line(pre={'preline': {'wait': '1', 'go': ''}}).values()))
r = line(stage='checker', fetcher='skipped')
check('line, stage=checker by hand (fetcher + worker skipped): the checker runs and saves', r['checker'] and r['save'] and not r['worker'])
check('line, stage=checker by hand, cancelled: nothing', not any(line(stage='checker', fetcher='skipped', cancelled=True).values()))
r = line(stage='worker', fetcher='skipped')
check('line, stage=worker by hand (fetcher skipped): the worker and the checker run and save', r['worker'] and r['checker'] and r['save'])
ck = [skey(s) for s in L['jobs']['checker']['steps']]
for at in ck[:ck.index(SAVE)]:
    check(f'line: a cancel mid-checker (after step {at}): no Save', not line(cancel_after=at)['save'])
check('line: the Check step (the verdict) failed or was cut: no Save', not line(check_outcome={'kept_green_10': 'failure'})['save']
      and not line(check_outcome={'kept_green_10': 'cancelled'})['save'])
check('line: the Check step left no fresh verdict (line-<tag>.json missing: the line check crashed): no Save', not line(check_out={})['save'])
check('line: the worker\'s bundle could not be read (no bundle): no Save', not line(check_outcome={'The worker\'s bundle (no bundle = a red run)': 'failure'})['save'])
# the out-of-time path: a pass that ran out of its own time (kpc_fers.py exit 0, rows 'waiting for pass N') or hit its step limit
# (continue-on-error) still bundles up, the worker is green, the checker grades it (STOPPED / PART READY) and SAVES
_, wctx = job_go(L, 'worker', {'preline': 'success', 'fetcher': 'success'}, PRE, ALL)
ran, res = walk(L, 'worker', wctx, {'kept_green_8': 'failure', 'kept_green_7': 'failure'})
check('line, out of time: Passes 3 + 5 cut by its step limit (continue-on-error): the bundle still goes up and the worker is green',
      ran[next(skey(s) for s in L['jobs']['worker']['steps'] if str(s.get('name', '')).startswith('Bundle up'))] and res == 'success')
check('line, out of time: ... and the checker then runs and Saves (the next run carries on from the saved rows)', line(worker=res)['save'])
ran, res = walk(L, 'worker', dict(wctx), cancel_after='kept_green_8')
check('line: a cancel mid-worker: the bundle still goes up (allow-listed carry-on), the worker is cancelled, so no checker and no Save',
      ran[next(skey(s) for s in L['jobs']['worker']['steps'] if str(s.get('name', '')).startswith('Bundle up'))] and res == 'cancelled'
      and not line(worker=res)['checker'])
# the pre-line report: the gate's own report; saved after a crash of the check (it says HOLD), never on a cancel
ps = next(s for s in L['jobs']['preline']['steps'] if str(s.get('name', '')).startswith('Save the pre-line report'))
check('line: the pre-line report save is FALSE on a cancel and true after a failed check step (the report says why: HOLD)',
      not can_be_true(ps['if'], {}, ON_CANCEL) and evaluate(full(ps['if']), {'steps.wait.outputs.wait': '0'}, NOT_CANCELLED[1]))
# order + verdict
cs = L['jobs']['checker']['steps']
ci, si = [skey(s) for s in cs].index('kept_green_10'), [skey(s) for s in cs].index(SAVE)
check('line: the verdict (Check, kpc_fers_line_check.py) runs BEFORE the Save', ci < si and 'kpc_fers_line_check.py' in cs[ci]['run'])
G = ['!cancelled()', "steps.kept_green_10.outcome == 'success'", "steps.kept_green_10.outputs.verdict == 'written'"]
check('line: the Save needs !cancelled(), the Check outcome and a fresh verdict, in its own if:', all(g in str(cs[si].get('if')) for g in G))
crun = cs[ci]['run']
check('line: the Check step removes the old verdict first and says verdict=written only when line-<tag>.json was written this run',
      crun.index('rm -f "data/fers/line-$RUN_TAG.json"') < crun.index('kpc_fers_line_check.py')
      and '[ -s "data/fers/line-$RUN_TAG.json" ] && echo "verdict=written" >> "$GITHUB_OUTPUT"' in crun)
for jn in ('worker', 'checker'):
    check(f'line: the {jn} job needs !cancelled() and a green pre-line, no always()',
          '!cancelled()' in L['jobs'][jn]['if'] and "needs.preline.result == 'success'" in L['jobs'][jn]['if'] and 'always()' not in L['jobs'][jn]['if'])
check('line: the checker still needs a green worker unless stage=checker', "(inputs.stage == 'checker' || needs.worker.result == 'success')" in L['jobs']['checker']['if'])
check('line: broke needs !cancelled(), and still runs on a fetcher / worker failure', L['jobs']['broke']['if'].startswith('${{ !cancelled() &&')
      and "needs.fetcher.result == 'failure' || needs.worker.result == 'failure'" in L['jobs']['broke']['if'])
check('line: the two-breaks-in-a-row stop (gh run cancel) is still there', 'gh run cancel "$GITHUB_RUN_ID"' in L['jobs']['broke']['steps'][-2]['run'])
nx = next(s for s in L['jobs']['fetcher']['steps'] if s.get('id') == 'kept_green_6')
check('line: "Start the next area" has no status function (success() && ...): never after a cancel or a lost bundle',
      not has_status(str(nx.get('if'))) and not can_be_true(nx.get('if'), {}, ON_CANCEL))

# ------------------------------------------------------------------ 3. kpc-fers-lines.yml
def again(line_res, plan='success', cancelled=False, rnd='0'):
    return job_go(LS, 'again', {'plan': plan, 'line': line_res}, {'plan': {'lines': '[{"tag":"mi"}]'}}, {'round': rnd}, cancelled)[0]


check('lines: again runs after all lines are green', again('success'))
check('lines: again still runs after a FAILED line (a broken area is recorded and the queue moves on; the water retry is intended)', again('failure'))
check('lines: again does not start on a cancelled run (e.g. broke stopped the queue after two breaks): no save, no retry round',
      not again('failure', cancelled=True) and not again('success', cancelled=True) and not again('cancelled', cancelled=True))
check('lines: again does not start when the plan failed', not again('skipped', plan='failure'))
check('lines: round 1 never starts another round', not again('success', rnd='1'))
check('lines: the again job has no always()', 'always()' not in LS['jobs']['again']['if'] and '!cancelled()' in LS['jobs']['again']['if'])
_, actx = job_go(LS, 'again', {'plan': 'success', 'line': 'success'}, {}, {'round': '0'})
ran, _ = walk(LS, 'again', actx, cancel_after='kept_green_1')
rnd = next(skey(s) for s in LS['jobs']['again']['steps'] if 'one more round' in str(s.get('name', '')))
check('lines: a cancel mid-again (after the layered-list save): no review-list save, no retry round', not ran['kept_green_2'] and not ran[rnd])
ran, _ = walk(LS, 'again', dict(actx), {'kept_green_1': 'failure', 'kept_green_2': 'failure'})
check('lines: a failed (kept green) save step does not stop the retry round (unchanged)', ran[rnd])
check('lines: ahead (water tiles dispatch) and line are success() && ...: not on a cancel',
      not can_be_true(LS['jobs']['ahead'].get('if'), {}, [{'always': True, 'cancelled': True, 'success': False, 'failure': False}])
      and not job_go(LS, 'line', {'plan': 'success'}, {'plan': {'lines': '[1]'}}, {}, True)[0])

# ------------------------------------------------------------------ 4. kpc-fers.yml (fixed Nov 8; checked, not changed)
fs = F['jobs']['fers']['steps']
fk = [skey(s) for s in fs]
SV, BK = 'kept_green_5', next(skey(s) for s in fs if str(s.get('name', '')).startswith('The run broke'))
KP = next(skey(s) for s in fs if str(s.get('name', '')).startswith('Keep the outlines read live'))


def fers(outcome=None, cancel_after=None, region='na'):
    ctx = {'matrix.r.region': region, 'matrix.r.states': 'US-OH', 'matrix.r.tag': 'oh'}
    ran, _ = walk(F, 'fers', ctx, outcome, {'wait': {'wait': '0'}}, cancel_after)
    return ran


r = fers()
check('kpc-fers.yml, all green: Save runs; the break save does not', r[SV] and not r[BK] and r[KP])
r = fers({'kept_green_3': 'failure'})
check('kpc-fers.yml: Look crashed (exit 1) or hit its hard end (exit 3): no Save; the break save keeps only what finished; outlines kept',
      not r[SV] and r[BK] and r[KP])
check('kpc-fers.yml: a world area that broke saves nothing', not fers({'kept_green_3': 'failure'}, region='world')[BK])
for at in fk[:fk.index(SV)]:
    r = fers(cancel_after=at)
    check(f'kpc-fers.yml: a cancel after step {at}: no Save, no break save, no outline upload', not r[SV] and not r[BK] and not r[KP])
r = fers({'key_gate': 'failure'})
check('kpc-fers.yml: a red key gate (stale / incomplete key): no Save, no break save', not r[SV] and not r[BK])
check('kpc-fers.yml: the key gate and Look run BEFORE the Save', fk.index('key_gate') < fk.index('kept_green_3') < fk.index(SV))
look = fs[fk.index('kept_green_3')]['run']
check('kpc-fers.yml, out of time: "no time left for pass N (next run carries on)" ends the loop with break (exit 0), so Look is green and Save runs',
      re.search(r"\[ \$CAP -lt 5 \] && \{ echo \"::notice title=2-fer bot::no time left for pass \$p \(next run carries on\)\"; break; \}", look) is not None)
check('kpc-fers.yml: a crash / hard end ends Look with the script\'s own code (exit $kpc_rc), so it is not taken for out-of-time', look.count('exit $kpc_rc') >= 4)
check('kpc-fers.yml: the fers job is success() && ...: it never starts on a cancelled run', not has_status(str(F['jobs']['fers'].get('if'))))

# ------------------------------------------------------------------ 5. guard: every always() left, with its reason
left = []
for wn, d in D.items():
    for jn, j in d['jobs'].items():
        if 'always()' in str(j.get('if', '')): left.append((wn, jn, '(job)', step_writes({'run': ''}) or job_writes(j)))
        for s in j.get('steps') or []:
            if 'always()' in str(s.get('if', '')): left.append((wn, jn, str(s.get('name', skey(s))), step_writes(s)))
print('INFO always() left in the 2-fer chain:')
unlisted = []
for wn, jn, sn, w in left:
    why = next((v for (a, b, c), v in ALLOW_WRITE.items() if a == wn and b == jn and sn.startswith(c)), None) if w else \
        next((v for p, v in ALLOW_READ.items() if sn.startswith(p)), None)
    print(f'INFO   {wn} {jn}: {sn[:60]} :: {"WRITES" if w else "read-only"} :: {why or "NOT ON THE ALLOW-LIST"}')
    if not why: unlisted.append((wn, jn, sn))
check('every always() left in the 2-fer chain is on the allow-list with a reason (a new one on a writing step fails here)', left and not unlisted)
check('no job of the 2-fer chain has always() in its if:', not [x for x in left if x[2] == '(job)'])
found = {(a, b, c) for a, b, c in ALLOW_WRITE if any(wn == a and jn == b and sn.startswith(c) for wn, jn, sn, _ in left)}
check('the writing allow-list holds only steps that are still there (2 bundle uploads)', found == set(ALLOW_WRITE))
check('the read-only always() steps write nothing', all(not w for wn, jn, sn, w in left if sn.startswith('Report hidden failures')))

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
