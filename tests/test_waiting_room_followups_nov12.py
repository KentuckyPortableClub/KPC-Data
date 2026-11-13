#!/usr/bin/env python3
"""Nov 12 (KPC owner, 2026-11-11): the two follow-ups Quality asked for after #72 (waiting room: no 2-fer rerun on a cancelled run or
an unsaved release). Checked here:
  1) kpc-fers-pending.yml (job look, step "Waiting parks -> one small batch per area") does nothing while a 2-fer run (kpc-fers.yml)
     is in progress or queued: it asks `gh run list --workflow kpc-fers.yml --status in_progress` and `--status queued` FIRST, exits
     green with a notice when either has a run, and fails CLOSED (red, nothing started) when the look itself errors or answers
     something that is not a count. Run offline with a stand-in `gh`;
  2) kpc-waiting-room.yml's Save (id kept_green_8) calls kpc_push_data.sh with STRICT=1, the way kpc-fers.yml does, and its error
     block ends in exit 1, so a push that did not land turns the step red (outcome failure: the 2-fer rerun after it never starts).
     Run offline with a stand-in kpc_push_data.sh that keeps the real script's contract (STRICT=1 + failed save = exit 1, else 0);
     when LINKS points at a KPC-Links checkout, the real script's STRICT line is checked too;
  3) nothing else moved: every other step, the triggers (no cron change), permissions and concurrency are the same as on main
     before this change (5ab309c9, #72).
Offline: temp folders only. Run: python3 -B tests/test_waiting_room_followups_nov12.py"""
import os, pathlib, re, shutil, subprocess, sys, tempfile

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
WF = ROOT / '.github/workflows'
BASE = '5ab309c9f'   # KPC-Data main before this change (#72 squash)
ok = True


def check(name, cond):
    global ok
    print(('PASS ' if cond else 'FAIL ') + name, flush=True)
    ok = ok and bool(cond)


def load(name): return yaml.safe_load((WF / name).read_text(encoding='utf-8'))
def expr_free(run): return re.sub(r'\$\{\{\s*github\.repository\s*\}\}', 'KentuckyPortableClub/KPC-Data', run)


def old(name):
    r = subprocess.run(['git', 'show', f'{BASE}:.github/workflows/{name}'], cwd=ROOT, capture_output=True, text=True)
    return yaml.safe_load(r.stdout) if r.returncode == 0 else None


def same_but(name, W, job, changed):
    """every step except index `changed` + job settings + triggers + permissions + concurrency equal to BASE; None when BASE is missing"""
    O = old(name)
    if O is None: return None
    a, b = O['jobs'][job]['steps'], W['jobs'][job]['steps']
    return (len(a) == len(b) and all(x == y for i, (x, y) in enumerate(zip(a, b)) if i != changed)
            and {k: v for k, v in O['jobs'][job].items() if k != 'steps'} == {k: v for k, v in W['jobs'][job].items() if k != 'steps'}
            and all(O.get(k) == W.get(k) for k in (True, 'permissions', 'concurrency', 'name', 'run-name', 'env'))
            and sorted(O['jobs']) == sorted(W['jobs']))


def _wr_inputs_ok(O, W):
    """Nov 13: the only allowed waiting-room trigger change is release-areas (mode text + areas/grade inputs)."""
    oi = (O.get(True) or {}).get('workflow_dispatch', {}).get('inputs') or {}
    wi = (W.get(True) or {}).get('workflow_dispatch', {}).get('inputs') or {}
    if set(wi) - set(oi) != {'areas', 'grade'}: return False
    if set(oi) - set(wi): return False
    if 'release-areas' not in (wi.get('mode') or {}).get('description', ''): return False
    if (wi.get('mode') or {}).get('default') != (oi.get('mode') or {}).get('default'): return False
    for k in oi:
        if k == 'mode': continue
        if oi[k] != wi[k]: return False
    return True

def _wr_run_norm(run):
    return re.sub(
        r'^[ \t]*release-areas\) python3 \.github/scripts/kpc_fers_release_areas\.py --areas "\$\{\{ inputs\.areas \}\}" --grade "\$\{\{ inputs\.grade \}\}" ;;\n',
        '', run or '', flags=re.M)

def _wr_on_same(O, W):
    if not _wr_inputs_ok(O, W): return False
    # crons and event types unchanged; dispatch inputs compared above
    o_on, w_on = O.get(True) or {}, W.get(True) or {}
    if sorted(o_on) != sorted(w_on): return False
    if o_on.get('schedule') != w_on.get('schedule'): return False
    return True


# ------------------------------------------------------------------ 1. kpc-fers-pending.yml: no batches while kpc-fers.yml runs
P = load('kpc-fers-pending.yml')
J = P['jobs']['look']
PI = next(i for i, s in enumerate(J['steps']) if str(s.get('name', '')).startswith('Waiting parks -> one small batch per area'))
run = J['steps'][PI]['run']
first = run.find('--workflow kpc-fers.yml')
check('pending: the step asks about kpc-fers.yml runs, in_progress and queued', '--workflow kpc-fers.yml' in run and '"$kpc_st"' in run
      and re.search(r'for kpc_st in in_progress queued; do', run))
check('pending: that look comes FIRST: before the full-queue look, the inline Python and any gh workflow run / git push',
      -1 < first < min(x for x in (run.find('kpc-fers-lines.yml'), run.find("python3 - <<'PY'"), run.find('gh workflow run'), run.find("'gh', 'workflow'"), run.find('git push')) if x > -1))
check('pending: the job token is gh\'s token and the workflow may read Actions runs (actions: read or write)',
      J.get('env', {}).get('GH_TOKEN') == '${{ github.token }}' and (P.get('permissions') or {}).get('actions') in ('read', 'write'))
check('pending: the triggers are unchanged (cron 23 10 * * * + workflow_dispatch force)', [c['cron'] for c in P[True]['schedule']] == ['23 10 * * *']
      and sorted(P[True]) == ['schedule', 'workflow_dispatch'])
r = same_but('kpc-fers-pending.yml', P, 'look', PI)
if r is None: print(f'INFO {BASE} not in this clone: the compare with main is skipped')
else: check(f'pending: every other step, the job, triggers, permissions and concurrency are the same as on main ({BASE})', r)
O = old('kpc-fers-pending.yml')
if O is not None:
    orun = O['jobs']['look']['steps'][PI]['run']
    # KPC owner, 2026-11-12 (2-fers per state): the one later change to this step is the area list, now read from .github/fers-areas.json
    # (the inline copy of the chain's old list is retired; OH / MI / UT are in their areas): normalised here, everything else byte for byte
    def _norm(x):
        x = re.sub(r"( *)R = \{'southeast'.*?\}\n", lambda m: m.group(1) + "R = <area list>\n", x, flags=re.S)
        x = re.sub(r"( *)R = json\.load\(open\('\.github/fers-areas\.json'.*?\n", lambda m: m.group(1) + "R = <area list>\n", x)
        return re.sub(r"( *)OWN = \{'US-KY'.*?\n", lambda m: m.group(1) + "OWN = <own-state runs>\n", x)
    check('pending: the step is main\'s step with only the new look in front (the rest of it byte-for-byte the same, the area list aside)', _norm(run).endswith(_norm(orun)) and len(run) > len(orun) - 2000)
block = expr_free(run[:run.find('if [ -n "$(gh run list -R ${{ github.repository }} --workflow kpc-fers-lines.yml')])


def pending(answers):
    """run the new look with a stand-in gh: answers = {status: (stdout, exit)}; returns (rc, reached_rest, output, gh calls)"""
    t = pathlib.Path(tempfile.mkdtemp(prefix='fers-pending-'))
    try:
        (t / 'bin').mkdir()
        cases = ''.join(f'  *"--status {st}"*) printf "%s" \'{out}\'; exit {rc};;\n' for st, (out, rc) in answers.items())
        (t / 'bin' / 'gh').write_text(f'#!/bin/sh\necho "$@" >> "{t}/gh-calls.txt"\ncase "$*" in\n{cases}  *) echo "unexpected gh call" >&2; exit 9;;\nesac\n')
        (t / 'bin' / 'gh').chmod(0o755)
        env = dict(os.environ, PATH=f"{t / 'bin'}:{os.environ.get('PATH', '')}", GH_TOKEN='x')
        p = subprocess.run(['bash', '--noprofile', '--norc', '-eo', 'pipefail', '-c', block + '\necho KPC-REST-OF-STEP\n'], cwd=t, env=env, capture_output=True, text=True)
        calls = (t / 'gh-calls.txt').read_text() if (t / 'gh-calls.txt').exists() else ''
        return p.returncode, 'KPC-REST-OF-STEP' in p.stdout, p.stdout + p.stderr, calls
    finally:
        shutil.rmtree(t, ignore_errors=True)


rc, rest, out, calls = pending({'in_progress': ('0', 0), 'queued': ('0', 0)})
check('pending, no 2-fer run: the look passes and the step goes on (both statuses asked, kpc-fers.yml, this repo)', rc == 0 and rest
      and calls.count('--workflow kpc-fers.yml') == 2 and '--status in_progress' in calls and '--status queued' in calls and '-R KentuckyPortableClub/KPC-Data' in calls)
rc, rest, out, calls = pending({'in_progress': ('1', 0), 'queued': ('0', 0)})
check('pending, a 2-fer run in progress: green, a notice says so, nothing else in the step runs', rc == 0 and not rest and '::notice' in out and 'in_progress' in out)
rc, rest, out, calls = pending({'in_progress': ('0', 0), 'queued': ('2', 0)})
check('pending, a 2-fer run queued: green, a notice says so, nothing else in the step runs', rc == 0 and not rest and '::notice' in out and 'queued' in out)
rc, rest, out, calls = pending({'in_progress': ('', 1), 'queued': ('0', 0)})
check('pending, gh fails on the in-progress look: fail CLOSED (red, an error line, nothing else runs)', rc != 0 and not rest and '::error' in out and 'fail closed' in out)
rc, rest, out, calls = pending({'in_progress': ('0', 0), 'queued': ('', 4)})
check('pending, gh fails on the queued look: fail CLOSED', rc != 0 and not rest and '::error' in out)
rc, rest, out, calls = pending({'in_progress': ('HTTP 403', 0), 'queued': ('0', 0)})
check('pending, gh answers something that is not a count: fail CLOSED', rc != 0 and not rest and '::error' in out)
rc, rest, out, calls = pending({'in_progress': ('', 0), 'queued': ('0', 0)})
check('pending, gh answers nothing at all: fail CLOSED', rc != 0 and not rest and '::error' in out)

# ------------------------------------------------------------------ 2. kpc-waiting-room.yml: Save with STRICT=1
W = load('kpc-waiting-room.yml')
steps = W['jobs']['waiting']['steps']
SI = next(i for i, s in enumerate(steps) if str(s.get('name', '')).startswith('Save (data/waiting'))
S = steps[SI]
srun = S['run']
calls = [ln for ln in srun.splitlines() if 'kpc_push_data.sh' in ln and not ln.strip().startswith('#')]
check('Save is kept_green_8 and has exactly one kpc_push_data.sh call', S.get('id') == 'kept_green_8' and len(calls) == 1)
check('Save: that call runs with STRICT=1 (as kpc-fers.yml does)', calls and calls[0].strip().startswith('STRICT=1 bash ../links/.github/scripts/kpc_push_data.sh '))
fers = (WF / 'kpc-fers.yml').read_text(encoding='utf-8')
check('kpc-fers.yml (the model) still calls it with STRICT=1', re.search(r'^\s*STRICT=1 bash \.github/scripts/kpc_push_data\.sh ', fers, re.M))
check('Save: its error block still logs the hidden error and then exits 1 (the step goes red)', calls and calls[0].rstrip().endswith('>> "$RUNNER_TEMP/kpc-hidden.txt"; exit 1; }'))
D = next(s for s in steps if 'kpc-fers-pending.yml/dispatches' in str(s.get('run', '')))
check('the 2-fer rerun still needs Save\'s outcome success (so a red Save starts nothing)', "steps.kept_green_8.outcome == 'success'" in str(D.get('if')) and steps.index(D) > SI)
O = old('kpc-waiting-room.yml')
if O is not None:
    os_ = O['jobs']['waiting']['steps']
    DI = steps.index(D)
    skip_ids = {'kept_green_1', 'kept_green_8', 'kept_green_9'}
    skip_names = {'Run the waiting room', 'Owner release (release-approved or release-areas)'}
    wby = {s.get('id') or s.get('name'): s for s in steps}
    same_rest = True
    for a in os_:
        key = a.get('id') or a.get('name')
        if a.get('id') in skip_ids or (a.get('name') or '') in skip_names:
            continue
        b = wby.get(key)
        if b is None or _wr_run_norm(a.get('run')) != _wr_run_norm(b.get('run')) or {k: v for k, v in a.items() if k != 'run'} != {k: v for k, v in b.items() if k != 'run'}:
            same_rest = False
            break
    check(f'waiting room: every step but Save, Run, dispatch, and the new owner-release step is the same as on main ({BASE}); job, permissions, concurrency too',
          same_rest
          and {k: v for k, v in O['jobs']['waiting'].items() if k != 'steps'} == {k: v for k, v in W['jobs']['waiting'].items() if k != 'steps'}
          and _wr_on_same(O, W) and all(O.get(k) == W.get(k) for k in ('permissions', 'concurrency', 'run-name')))
    norm = lambda r: [ln for ln in r.splitlines() if not ln.strip().startswith('#')]
    oD = next(s for s in os_ if s.get('id') == 'kept_green_9')
    check('the rerun step changed only in its comments', norm(oD['run']) == norm(D['run']) and {k: v for k, v in oD.items() if k != 'run'} == {k: v for k, v in D.items() if k != 'run'})
    oS = next(s for s in os_ if s.get('id') == 'kept_green_8')
    def _save_norm(r):
        r = [ln.replace('STRICT=1 bash', 'bash').replace('; exit 1; }', '; }') for ln in norm(r)]
        return [ln.replace("inputs.mode || 'check'", "inputs.mode || 'release-approved'").replace("inputs.mode || 'check (nightly)'", "inputs.mode || 'release-approved (nightly)'") for ln in r]
    check('Save changed only by STRICT=1, exit 1, its comment, and the schedule default mode (check, not release-approved)',
          _save_norm(srun) == norm(oS['run'])
          and {k: v for k, v in oS.items() if k != 'run'} == {k: v for k, v in S.items() if k != 'run'})
check('waiting room: the two crons are unchanged', [c['cron'] for c in W[True]['schedule']] == ['42 */2 * * *', '13 11 * * *'])


def save(push_ok, mode=''):
    """run Save with a stand-in kpc_push_data.sh (STRICT=1 + failed push = exit 1, else exit 0, like the real one)"""
    t = pathlib.Path(tempfile.mkdtemp(prefix='wr-save-'))
    try:
        (t / 'kpcdata').mkdir(); (t / 'rt').mkdir(); sd = t / 'links/.github/scripts'; sd.mkdir(parents=True)
        (sd / 'kpc_push_data.sh').write_text('#!/bin/bash\necho "STRICT=$STRICT args=$*" >> "' + str(t) + '/push-calls.txt"\n'
                                             + ('echo "saved"; exit 0\n' if push_ok else 'echo "::notice::save did not land"; [ "$STRICT" = 1 ] && exit 1\nexit 0\n'))
        script = re.sub(r"\$\{\{\s*inputs\.mode \|\| '([^']*)'\s*\}\}", lambda m: mode or m.group(1), srun)
        script = re.sub(r'\$\{\{\s*inputs\.target\s*\}\}', '', script)
        env = dict(os.environ, RUNNER_TEMP=str(t / 'rt'))
        p = subprocess.run(['bash', '--noprofile', '--norc', '-eo', 'pipefail', '-c', script], cwd=t, env=env, capture_output=True, text=True)
        pc = (t / 'push-calls.txt').read_text() if (t / 'push-calls.txt').exists() else ''
        he = (t / 'rt/kpc-hidden-errors.txt').read_text() if (t / 'rt/kpc-hidden-errors.txt').exists() else ''
        return p.returncode, pc, p.stdout + p.stderr, he
    finally:
        shutil.rmtree(t, ignore_errors=True)


rc, pc, out, he = save(push_ok=True)
check('Save, the push landed: green, one call with STRICT=1 saving data', rc == 0 and pc.count('\n') == 1 and pc.startswith('STRICT=1 ') and pc.rstrip().endswith(' data'))
rc, pc, out, he = save(push_ok=False)
check('Save, the push did not land: RED (exit 1), the ::error line, the hidden-errors file has it', rc == 1 and '::error title=Save::' in out and 'NOT saved' in he)
rc, pc, out, he = save(push_ok=True, mode='replay')
check('Save, replay mode: still only data/waiting data/status, with STRICT=1', rc == 0 and pc.startswith('STRICT=1 ') and pc.rstrip().endswith('data/waiting data/status'))
links = os.environ.get('LINKS')
real = pathlib.Path(links) / '.github/scripts/kpc_push_data.sh' if links else None
if real and real.is_file():
    txt = real.read_text(encoding='utf-8')
    check('the real kpc_push_data.sh (LINKS) exits 1 on a failed save with STRICT=1', '[ "$STRICT" = 1 ] && exit 1' in txt)
else:
    print('INFO LINKS not set (or no kpc_push_data.sh there): the real script\'s STRICT line is not checked')

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
