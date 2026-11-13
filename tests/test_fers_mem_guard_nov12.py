#!/usr/bin/env python3
"""Memory guard for the 2-fer steps (KPC owner, 2026-11-12, run 43205747757). Offline: stand-in child processes, temp folders, no network.
  1 a child that grows past the limit is stopped: polite SIGINT first, then (if it ignores it) SIGKILL after the grace period; exit 86,
    the ::error line, heartbeat lines, the stop file, the step summary
  2 a child under the limit runs to the end and its own exit code passes through unchanged (0, 1, 3, 7, a signal = 128 + N)
  3 the system running low (MemAvailable under the floor) while the child's RSS is moderate also stops it (injected readers)
  4 no orphan is left behind; the child runs with oom_score_adj 1000 (the kernel's OOM killer takes it before the runner)
  5 limits come from MemTotal (16 GB runner: 70 % / 12 %), clamped so the runner keeps room; KPC_MEM_GUARD=off never stops
  6 workflows: every step that starts kpc_fers.py runs under the guard; Bundle-up steps stay always() and run before the memory
    verdict; the Nov 12 !cancelled() conditions are unchanged; no cron added; a memory stop is never 'two breaks in a row' and is
    never retried by the retry round or the chain on the same cut
  7 per-state outcome after a guard stop (fixture): Save does not run, the break save keeps the stopped state's previous file byte
    for byte and saves only a state that finished every pass (main: kpc_fers_areas.py finished; with part C: kpc_fers_states.py pick)"""
import importlib.util, json, os, pathlib, re, shutil, signal, subprocess, sys, tempfile, time

HERE = pathlib.Path(__file__).resolve().parent.parent
G_PATH = HERE / '.github/scripts/kpc_mem_guard.py'
ok = True


def check(c, msg):
    global ok
    print(('PASS ' if c else 'FAIL ') + msg); ok = ok and bool(c)


def mod(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


sys.path.insert(0, str(HERE / '.github/scripts'))
G = mod('kpc_mem_guard', G_PATH)
ENV0 = {k: v for k, v in os.environ.items() if not k.startswith(('GITHUB_', 'KPC_', 'RUNNER_'))}
T = pathlib.Path(tempfile.mkdtemp(prefix='kpc-memguard-'))
MARK = f'kpcmg{os.getpid()}'
ADJ0 = int(open('/proc/self/oom_score_adj').read())


def guard(child, extra=None, timeout=60):
    env = dict(ENV0, KPC_MEM_GUARD_SAMPLE_S='0.1', KPC_MEM_GUARD_BEAT_S='0.3', KPC_MEM_GUARD_GRACE_S='1.5', RUNNER_TEMP=str(T / 'rt'),
               GITHUB_STEP_SUMMARY=str(T / 'summary.md'), STATES='US-FL', RUN_TAG='fl'); env.update(extra or {})
    (T / 'rt').mkdir(exist_ok=True)
    t0 = time.time()
    r = subprocess.run([sys.executable, str(G_PATH), '--', *child], capture_output=True, text=True, env=env, timeout=timeout, cwd=T)
    return r.returncode, r.stdout + r.stderr, time.time() - t0


def py(code):
    p = T / f'c{abs(hash(code))}.py'; p.write_text(code); return [sys.executable, str(p)]


GROW = """
import signal, sys, time
a = []
try:
    while True:
        a.append(bytearray(16 * 1024 * 1024)); time.sleep(0.03)
        if len(a) > 120: time.sleep(60)
except KeyboardInterrupt:
    print('child: got SIGINT, stopping', flush=True); raise
"""
# 1 grows past the limit: polite stop
for f in T.glob('rt/*'): f.unlink()
rc, out, dt = guard(py(GROW), {'KPC_MEM_GUARD_MB': '300'})
check(rc == 86, f'a child past the limit is stopped with the distinct exit code 86 (got {rc})')
check('child: got SIGINT' in out and 'SIGKILL' not in out, 'the polite signal (SIGINT) comes first and was enough here (no kill)')
m = re.search(r'::error title=memory guard::memory guard: (.+?) stopped at ([\d,]+) MB \(limit ([\d,]+), system available ([\d,]+) MB\): this state keeps its previous file; the others are not affected', out)
check(bool(m) and m.group(1).startswith('fl (US-FL)') and int(m.group(3).replace(',', '')) == 300, 'one ::error line: "<state / area> stopped at N MB (limit L, system available A MB): this state keeps its previous file; the others are not affected"')
check(len(re.findall(r'^memory guard: fl \(US-FL\).*: \d+ min, RSS [\d,]+ MB', out, re.M)) >= 1, 'heartbeat lines with RSS and the machine\'s available memory are printed')
sf = T / 'rt/kpc-mem-stop.txt'
check(sf.exists() and 'stopped at' in sf.read_text(), 'the stop is written to $RUNNER_TEMP/kpc-mem-stop.txt (the workflow reads it)')
check('Needs a smaller cut or more memory' in (T / 'summary.md').read_text(), "the step summary says 'needs a smaller cut or more memory'")
rc2, out2, _ = guard(py(GROW), {'KPC_MEM_GUARD_MB': '300', 'STATES': 'US-TN US-NC US-VA', 'RUN_TAG': 'southeast'})
check(rc2 == 86 and 'these 3 states keep their previous files; the others are not affected' in out2, 'a several-state line says its states keep their previous files')

# 1b a busy loop that ignores the polite signal is killed after the grace period
IGN = "import signal, time\nsignal.signal(signal.SIGINT, signal.SIG_IGN)\nprint('child: ignoring SIGINT', flush=True)\nb = bytearray(200 * 1024 * 1024)\nfor i in range(0, len(b), 4096): b[i] = 1\nx = 0\nwhile True: x += 1\n"
rc, out, dt = guard(py(IGN), {'KPC_MEM_GUARD_MB': '120'})
check(rc == 86 and 'killed (SIGKILL)' in out, f'a child that ignores SIGINT (busy loop) is killed after the grace period (exit {rc})')
check(1.4 <= dt < 15, f'... and only after the grace period (1.5 s; took {dt:.1f} s in all)')

# 2 under the limit: the child's own exit code passes through
for want in (0, 1, 3, 7):
    rc, out, _ = guard(py(f'import sys; print("child ran"); sys.exit({want})'), {'KPC_MEM_GUARD_MB': '4000'})
    check(rc == want and 'child ran' in out and '::error' not in out, f'a child under the limit keeps its own exit code {want}')
rc, out, _ = guard(py('import os, signal; os.kill(os.getpid(), signal.SIGTERM)'), {'KPC_MEM_GUARD_MB': '4000'})
check(rc == 128 + signal.SIGTERM, f'a child ended by a signal gives 128 + N like the shell ({rc})')
rc, out, _ = guard(['bash', '-e', '-c', 'python3 -c "import sys; sys.exit(3)" || { r=$?; echo "handler $r"; exit $r; }'], {'KPC_MEM_GUARD_MB': '4000'})
check(rc == 3 and 'handler 3' in out, 'as a step shell (bash -e): the kpc_fers.py exit 3 handler runs and the step ends with 3, as today')
rc, out, _ = guard(['bash', '-e', '-c', f'{sys.executable} {py(GROW)[-1]} || echo "HANDLER RAN"; echo "NEXT PASS STARTED"'], {'KPC_MEM_GUARD_MB': '300'})
check(rc == 86 and 'HANDLER RAN' not in out and 'NEXT PASS STARTED' not in out, 'as a step shell: after a memory stop no later command of the step runs (no next pass)')

# 3 the machine runs low while the child's RSS is moderate
calls = {'n': 0}
def low_system():
    calls['n'] += 1
    return 16000.0, (9000.0 if calls['n'] < 4 else 900.0), 0.0
for f in T.glob('rt/*'): f.unlink()
env = dict(ENV0, RUNNER_TEMP=str(T / 'rt'), STATES='US-FL', RUN_TAG='fl')
rc = G.run(py('import time\ntry:\n  time.sleep(30)\nexcept KeyboardInterrupt:\n  print("child: got SIGINT", flush=True); raise\n'), env, sample=0.1, beat=0.5, grace=2,
           read_system=low_system, read_rss=lambda pids: 500.0)
check(rc == 86, f'MemAvailable under the floor with a moderate RSS (500 MB) also stops it (exit {rc})')
check('system available 900 MB' in (T / 'rt/kpc-mem-stop.txt').read_text(), 'the stop line carries the system\'s available memory')

# 4 no orphans; oom_score_adj
def mine():
    r = subprocess.run(['ps', '-eo', 'args'], capture_output=True, text=True).stdout
    return [l for l in r.splitlines() if MARK in l and 'ps -eo' not in l]
rc, out, _ = guard(['bash', '-c', f'exec -a {MARK}a sleep 300 & (exec -a {MARK}b sleep 300) & {sys.executable} {py(GROW)[-1]}'], {'KPC_MEM_GUARD_MB': '300'})
time.sleep(0.5)
check(rc == 86 and not mine(), f'after a stop no process of the guarded tree is left (left: {mine()})')
rc, out, _ = guard(['bash', '-c', f'(exec -a {MARK}c sleep 300) & exit 0'], {'KPC_MEM_GUARD_MB': '4000'})
time.sleep(0.5)
check(rc == 0 and not mine(), 'after a normal end a background leftover of the step is not left running either')
rc, out, _ = guard(py('print("adj", open("/proc/self/oom_score_adj").read().strip())'), {'KPC_MEM_GUARD_MB': '4000'})
check('adj 1000' in out, 'the child runs with oom_score_adj 1000: in a sudden spike the kernel kills the 2-fer process, not the runner agent')
check(int(open('/proc/self/oom_score_adj').read()) == ADJ0, 'the guard does not raise its OWN score (only the child\'s; G.run ran in this process above)')

# 5 limits
lim, fl = G.limits(16 * 1024.0, {})
check(abs(lim - 11468.8) < 1 and abs(fl - 1966.1) < 1, f'16 GB runner (read from MemTotal): limit {lim:.0f} MB (70 %), floor {fl:.0f} MB (12 %)')
lim7, fl7 = G.limits(7 * 1024.0, {})
check(abs(lim7 - 5017.6) < 1 and fl7 == 1536, f'7 GB runner: limit {lim7:.0f} MB, floor {fl7:.0f} MB')
limx, flx = G.limits(16 * 1024.0, {'KPC_MEM_GUARD_MB': '99999', 'KPC_MEM_GUARD_FLOOR_MB': '10'})
check(limx == 16 * 1024.0 - 2048 and flx == 1024, 'a repo variable can never take the limit past MemTotal - 2,048 MB or the floor under 1,024 MB')
check(6973 < lim * 0.65, 'the 9-state pass 1 peak of the failed run (6,973 MB) is under the 16 GB limit: a normal pass 1 is not stopped')
rc, out, _ = guard(py('import time\na = [bytearray(400 * 1024 * 1024)]\nfor i in range(0, len(a[0]), 4096): a[0][i] = 1\ntime.sleep(1)\n'), {'KPC_MEM_GUARD_MB': '300', 'KPC_MEM_GUARD': 'off'})
check(rc == 0 and 'lines only, no stop' in out, 'KPC_MEM_GUARD=off: heartbeat lines only, never a stop')

# 6 workflows
try:
    import yaml
except ImportError:
    yaml = None
check(yaml is not None, 'PyYAML is available to parse the workflows')
WF = HERE / '.github/workflows'
def load(n):
    return yaml.load((WF / n).read_text(encoding='utf-8'), Loader=yaml.BaseLoader)
GUARD_SHELL = 'python3 kpcdata/.github/scripts/kpc_mem_guard.py -- bash -e {0}'
starts = []
for f in sorted(WF.glob('*.yml')):
    d = load(f.name)
    for jn, j in (d.get('jobs') or {}).items():
        for s in j.get('steps') or []:
            if re.search(r'python3 \.github/scripts/kpc_fers\.py', s.get('run') or ''):
                starts.append((f.name, jn, s.get('name'), s.get('shell')))
check(len(starts) == 3 and all(sh == GUARD_SHELL for *_, sh in starts), f'every step that starts kpc_fers.py runs under the guard ({[(a, b, c[:20]) for a, b, c, _ in starts]})')
crons = {f.name: [c.get('cron') for c in (load(f.name).get('on') or {}).get('schedule') or []] for f in sorted(WF.glob('kpc-fers*.yml'))}
check({k: v for k, v in crons.items() if v} == {'kpc-fers.yml': ['23 8 5 * *'], 'kpc-fers-pending.yml': ['23 10 * * *'], 'kpc-fers-check.yml': ['9 4 * * 0']},
      'no cron added or changed in the 2-fer workflows (the three existing lines only)')
L = load('kpc-fers-line.yml')
for jn in ('fetcher', 'worker'):
    names = [s.get('name') or '' for s in L['jobs'][jn]['steps']]
    bu = next(i for i, n in enumerate(names) if n.startswith('Bundle up'))
    ms = next(i for i, n in enumerate(names) if n.startswith('Did the memory guard stop'))
    check(L['jobs'][jn]['steps'][bu].get('if', '').startswith('always()') and bu < ms, f'{jn}: Bundle up stays always() and runs BEFORE the memory verdict (finished downloads are kept)')
    check(L['jobs'][jn].get('outputs', {}).get('mem') == '${{ steps.memstop.outputs.mem }}', f'{jn}: the job tells broke when the memory guard stopped it')
    red = L['jobs'][jn]['steps'][ms + 1]
    check(red.get('if') == "${{ !cancelled() && steps.memstop.outputs.mem == '1' }}" and 'exit 1' in red.get('run', ''), f'{jn}: a memory stop makes the job red (so the next job of the line does not start)')
check('needs.fetcher.result == \'success\'' in L['jobs']['worker']['if'] and "needs.worker.result == 'success'" in L['jobs']['checker']['if'],
      'a red fetcher starts no worker, a red worker starts no checker: the line saves nothing (Save is only in the checker)')
CANCEL = {('kpc-fers-line.yml', 'worker'): '!cancelled() && needs.preline.result', ('kpc-fers-line.yml', 'checker'): '!cancelled() && needs.preline.result',
          ('kpc-fers-line.yml', 'broke'): "${{ !cancelled() && (needs.fetcher.result == 'failure' || needs.worker.result == 'failure') }}"}
for (fn, jn), want in CANCEL.items():
    check(want in load(fn)['jobs'][jn]['if'], f'{fn} {jn}: the Nov 12 !cancelled() condition is unchanged')
LS = load('kpc-fers-lines.yml')
check(LS['jobs']['again']['if'] == "${{ !cancelled() && needs.plan.result == 'success' && inputs.round == '0' }}", 'kpc-fers-lines.yml again: its !cancelled() condition is unchanged')
F = load('kpc-fers.yml')
fs = {s.get('name', ''): s for s in F['jobs']['fers']['steps']}
look = fs['Look for shared ground']
check(look.get('shell') == GUARD_SHELL and look['env'].get('KPC_MEM_GUARD_MB') == '${{ vars.KPC_MEM_GUARD_MB }}', 'kpc-fers.yml: Look runs under the guard; the limit is a repo variable (blank = from MemTotal)')

# 6b broke: a memory stop is recorded, but is never one of 'two breaks in a row'
broke_py = re.search(r"python3 - <<'PY'\n(.*?)\n\s*PY", L['jobs']['broke']['steps'][2]['run'], re.S).group(1)
broke_py = '\n'.join(l[10:] if l.startswith(' ' * 10) else l for l in broke_py.split('\n'))
def broke(tag, mem, prev):
    d = T / f'broke-{tag}-{mem}'; shutil.rmtree(d, ignore_errors=True); (d / 'kpcdata/data/status').mkdir(parents=True)
    (d / 'kpcdata/data/status/line-breaks.json').write_text(json.dumps(prev))
    e = dict(ENV0, RUN_TAG=tag, STATES='US-FL', STAGE='fetcher', GITHUB_RUN_ID='77', REPO='o/r', MEM='1' if mem else '0')
    subprocess.run([sys.executable, '-c', broke_py], cwd=d, env=e, capture_output=True, text=True)
    return (d / 'stop.flag').read_text(), json.load(open(d / 'kpcdata/data/status/line-breaks.json'))
recent = [{'tag': 'plains', 'stage': 'fetcher', 't': time.time() - 600}]
flag, Lb = broke('southeast', True, recent)
check(flag == '' and Lb[-1].get('why') == 'memory', 'a memory stop after another line\'s break does not stop the queue; it is recorded with why=memory')
flag, _ = broke('plains', False, [{'tag': 'southeast', 'stage': 'fetcher', 't': time.time() - 600, 'why': 'memory'}])
check(flag == '', 'a real break after a memory stop is not "two in a row" either')
flag, _ = broke('plains', False, [{'tag': 'midatlantic', 'stage': 'fetcher', 't': time.time() - 600}])
check(flag == '1', 'two real breaks in a row (different lines, 6 h) still stop everything (C5 unchanged)')

# 6c the retry round skips a memory stop of this run; the chain does not start the same cut again
again_py = re.search(r"python3 - <<'PY' > again.txt\n(.*?)\n\s*PY", LS['jobs']['again']['steps'][4]['run'], re.S).group(1)
again_py = '\n'.join(l[10:] if l.startswith(' ' * 10) else l for l in again_py.split('\n'))
d = T / 'again'; (d / 'data/fers').mkdir(parents=True); (d / 'data/status').mkdir(parents=True)
stopped = {'verdict': 'STOPPED', 'why': ['water service did not answer']}
for tg in ('southeast', 'plains'): (d / f'data/fers/line-{tg}.json').write_text(json.dumps(stopped))
(d / 'data/status/line-breaks.json').write_text(json.dumps([{'tag': 'southeast', 'run': '77', 'why': 'memory', 't': time.time()}]))
r = subprocess.run([sys.executable, '-c', again_py], cwd=d, capture_output=True, text=True,
                   env=dict(ENV0, GITHUB_RUN_ID='77', GITHUB_STEP_SUMMARY=str(d / 'sum.md'), LINES=json.dumps([{'states': 'US-FL', 'tag': 'southeast'}, {'states': 'US-KS', 'tag': 'plains'}])))
check(r.stdout.strip() == 'US-KS|plains@worker' and 'needs a smaller cut or more memory' in (d / 'sum.md').read_text(),
      f'the retry round does not retry a memory-stopped line (it lists it as needing a smaller cut or more memory): {r.stdout.strip()!r}')
check(G.stopped_for_memory(str(d), 'southeast', '2026-01-01 00:00 UTC') and not G.stopped_for_memory(str(d), 'plains') and
      not G.stopped_for_memory(str(d), 'southeast', time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(time.time() + 3600))),
      'stopped_for_memory(): only a memory stop of that tag after the line was planned counts')
CP = mod('kpc_fers_chain_plan', HERE / '.github/scripts/kpc_fers_chain_plan.py')
check(CP.MEM_STOP is G.stopped_for_memory or CP.MEM_STOP.__code__.co_code == G.stopped_for_memory.__code__.co_code,
      'the chain plan uses the guard\'s stopped_for_memory (not the no-op fallback)')
src = (HERE / '.github/scripts/kpc_fers_chain_plan.py').read_text()
check(re.search(r"if int\(a.get\('tries'\) or 0\) >= TRIES:.*\n\s+if MEM_STOP\(data, tag, a.get\('planned'\)\): s\['waiting'\]\[tag\] = 'the memory guard", src) is not None,
      'the chain does not start a memory-stopped area again on the same key files (same fingerprint): a person looks')

# X6: memory-guard import fails closed; area_fp includes outlines
check('fail closed' in src and 'return False' not in src[src.find('except Exception'):src.find('TRIES =')],
      'X6: a failed kpc_mem_guard import raises (fail closed), it does not return False')
td = pathlib.Path(tempfile.mkdtemp())
(td / 'data/us-key').mkdir(parents=True)
(td / 'data/outlines').mkdir(parents=True)
(td / 'data/us-key/US-KY.json').write_bytes(b'{"parks":{}}')
fp1 = CP.area_fp(str(td), 'us-key', ['US-KY'], 'fers-hash')
(td / 'data/outlines/US-KY.geojson.gz').write_bytes(b'outline-bytes')
fp2 = CP.area_fp(str(td), 'us-key', ['US-KY'], 'fers-hash')
check(fp1 != fp2 and len(fp1) == 16 and len(fp2) == 16,
      'X6: area_fp changes when the outline file is added (outlines are in the fingerprint)')
shutil.rmtree(td, ignore_errors=True)


# 7 per-state outcome after a guard stop (fixture)
def cond(expr, ctx):
    """Evaluate a GitHub if: expression of the forms used here (&&, ||, !, ==, !=, success(), cancelled(), dotted names)."""
    e = expr.strip()
    if e.startswith('${{'): e = e[3:-2]
    e = re.sub(r'\bsuccess\(\)', repr(ctx['success']), e); e = re.sub(r'\bcancelled\(\)', repr(ctx['cancelled']), e)
    e = re.sub(r'\b(steps|matrix|inputs|needs)\.[\w.]+', lambda m: repr(ctx.get(m.group(0), '')), e)
    e = e.replace('&&', ' and ').replace('||', ' or ')
    e = re.sub(r'!(?!=)', ' not ', e)
    return bool(eval(e, {}))
ctx = {'success': True, 'cancelled': False, 'steps.wait.outputs.wait': '0', 'steps.kept_green_3.outcome': 'failure', 'matrix.r.region': 'na', 'inputs.pass': 'all'}
save = fs['Save (once, at the end; never on cancel or failed Look)']; brk = fs['The run broke - save only what finished (Nov 9 evening, Brandon t926u)']
keep = fs['Keep the outlines read live for next time (KPC-Archive; fers-cache release only as the fallback, Nov 9 evening)']
check(not cond(save['if'], ctx) and cond(brk['if'], ctx) and cond(keep['if'], ctx),
      'kpc-fers.yml after a guard stop (Look failed): Save does NOT run; the break save and the saved-live upload DO run')
check(not cond(brk['if'], dict(ctx, cancelled=True)), '... and a cancelled run saves nothing (unchanged)')
fx = T / 'job'; (fx / 'kpcdata/data/fers').mkdir(parents=True); (fx / 'data/fers').mkdir(parents=True)
SP = '{"refs":["US-0001","US-0002"],"kind":"area","id":"US-0001+US-0002@area@0","passes":[1,1,1]}'
OLD = {'US-FL': ('{"st":"US-FL","spots":[%s],"pass1":"2026-11-01"}\n' % SP).encode(), 'US-GA': b'{"st":"US-GA","spots":[],"pass1":"2026-11-01"}\n'}
for st, b in OLD.items(): (fx / f'kpcdata/data/fers/{st}.json').write_bytes(b)
today = time.strftime('%Y-%m-%d')
step = (f"echo '{{\"st\":\"US-GA\",\"spots\":[],\"pass1\":\"{today}\",\"pass2\":\"{today}\",\"pass3\":\"{today}\",\"pass5\":\"{today}\",\"passes\":4}}' > data/fers/US-GA.json\n"
        f"echo '{{\"st\":\"US-FL\",\"spots\":[],\"pass1\":\"{today}\"}}' > data/fers/US-FL.json\n"
        f"{sys.executable} {py(GROW)[-1]} || {{ r=$?; echo handler; exit $r; }}\n")
(fx / 'step.sh').write_text(step)
r = subprocess.run([sys.executable, str(G_PATH), '--', 'bash', '-e', str(fx / 'step.sh')], cwd=fx, capture_output=True, text=True,
                   env=dict(ENV0, KPC_MEM_GUARD_MB='300', KPC_MEM_GUARD_SAMPLE_S='0.1', STATES='US-FL US-GA', RUN_TAG='southeast'))
check(r.returncode == 86, 'fixture: the guard stops the job mid pass (US-GA finished every pass, US-FL only pass 1)')
if (HERE / '.github/scripts/kpc_fers_states.py').exists():   # part C (per-state save): the break save is pick ONLY_FINISHED=1
    lk = T / 'links/.github/scripts'; lk.mkdir(parents=True)
    (lk / 'kpc_key_freeze.py').write_text("def rules_hash(kind, root=None):\n    return 'cef323de4c9a'\n")
    (T / 'links/RULES').write_text('cef323de4c9a')
    FS = mod('kpc_fers_states', HERE / '.github/scripts/kpc_fers_states.py')
    import io
    cwd = os.getcwd(); os.chdir(fx)
    try: code, rows = FS.pick(dict(ENV0, STATES='US-FL US-GA', KPCDATA='kpcdata', LINKS=str(T / 'links'), ONLY_FINISHED='1', TODAY=today,
                                   KPC_FERS_NO_BASE_CHECK='1', RUNNER_TEMP=str(T / 'rt')), out=io.StringIO())
    finally: os.chdir(cwd)
    layout = 'with part C (pick ONLY_FINISHED)'
    check(rows['US-FL']['verdict'] == 'not-built' and rows['US-GA']['verdict'] == 'built', f'{layout}: the stopped state is red (not-built), the finished one is built')
else:   # main alone: the break save copies kpc_fers_areas.py finished
    A = mod('kpc_fers_areas', HERE / '.github/scripts/kpc_fers_areas.py')
    for f in A.finished('US-FL US-GA', today, fx): shutil.copy(fx / f, fx / 'kpcdata' / f)
    layout = 'main alone (kpc_fers_areas.py finished)'
check((fx / 'kpcdata/data/fers/US-FL.json').read_bytes() == OLD['US-FL'], f'{layout}: the stopped state keeps its previous file byte for byte')
check((fx / 'kpcdata/data/fers/US-GA.json').read_bytes() != OLD['US-GA'], f'{layout}: the state that finished every pass is saved')

shutil.rmtree(T, ignore_errors=True)
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
