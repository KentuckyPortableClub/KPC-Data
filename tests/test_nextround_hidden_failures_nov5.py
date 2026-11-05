#!/usr/bin/env python3
"""Next round C4 (Nov 5; item 7 next part, Brandon's yes relayed via Super): hidden failures in the KPC-Data workflows.
 * a caught ERROR line is also kept in kpc-hidden-errors.txt (warnings only in kpc-hidden.txt);
 * every G8 step leaves one 'Hidden failures' line (read by the KPC-Links check-up into data/status/hidden-failures.json) and goes
   red on a caught error only where it is safe (KPC_FAIL_SAFE=1: no workflow follows it, no job needs it, it starts no workflow,
   not a matrix that fails fast, not the watchdog); the repo variable KPC_HIDDEN_RED=off turns that off;
 * the paused bots are left exactly as they were (nothing un-paused); no cron changed;
 * the '|| true' forms that hid a real failure (answer-sheet board line, 2-fer post-line, watchdog notes) now record it.
No network, no run. Run: python3 -B tests/test_nextround_hidden_failures_nov5.py"""
import os, pathlib, re, subprocess, sys, tempfile
import yaml
HERE = pathlib.Path(__file__).resolve().parent.parent
WF = HERE / '.github/workflows'
ok = True
def check(c, msg):
    global ok
    print(('PASS ' if c else 'FAIL ') + msg); ok = ok and bool(c)
G8 = 'Report hidden failures'
docs = {f.name: (f.read_text(), yaml.safe_load(f.read_text())) for f in sorted(WF.glob('*.yml'))}
paused = [n for n, (t, d) in docs.items() if 'Paused bot' in t or re.search(r'^\s*#\s*- cron', t, re.M)]
check(len(paused) >= 10 and not any('next round C4' in docs[n][0] or 'kpc-hidden-errors.txt' in docs[n][0] or 'KPC_FAIL_SAFE' in docs[n][0] for n in paused), f'the {len(paused)} paused (or commented-cron) bots are not touched')
listened = set()
for n, (t, d) in docs.items():
    on = d.get(True) or {}
    if isinstance(on, dict) and isinstance(on.get('workflow_run'), dict): listened |= set(on['workflow_run'].get('workflows') or [])
untee = [n for n, (t, d) in docs.items() if n not in paused for m in re.finditer(r'echo "::error title=[^"]*"; echo "[^"]*" >> "\$RUNNER_TEMP/kpc-hidden\.txt"', t)]
check(not untee, f'every recorded ERROR line also goes to kpc-hidden-errors.txt ({untee[:3]})')
syn, beh, safe, notsafe = [], [], [], []
for n, (t, d) in docs.items():
    jobs = d.get('jobs') or {}
    needed = {x for j in jobs.values() for x in ([j.get('needs')] if isinstance(j.get('needs'), str) else (j.get('needs') or []))}
    for jn, j in jobs.items():
        for st in j.get('steps') or []:
            r = st.get('run')
            if not r: continue
            if n not in paused and subprocess.run(['bash', '-n'], input=re.sub(r'\$\{\{.*?\}\}', 'X', r), capture_output=True, text=True).returncode: syn.append(f'{n}:{jn}')
            if not (st.get('name') or '').startswith(G8) or n in paused: continue
            fs = 'KPC_FAIL_SAFE' in (st.get('env') or {})
            (safe if fs else notsafe).append(f'{n}:{jn}')
            if fs:
                stg = j.get('strategy') or {}
                why = [w for w, c in (('followed', (d.get('name') or n) in listened), ('needed', jn in needed), ('dispatches', bool(re.search(r'gh workflow run|/dispatches', t))),
                       ('matrix', bool(stg.get('matrix')) and stg.get('fail-fast', True) is not False), ('watchdog', n == 'kpc-watchdog.yml'),
                       ('not last', not (j['steps'][-1].get('name') or '').startswith(G8)),
                       ('no off switch', st['env']['KPC_FAIL_SAFE'] != "${{ vars.KPC_HIDDEN_RED != 'off' && '1' || '0' }}")) if c]
                if why: beh.append(f'{n}:{jn} marked safe but {why}')
            py = r.split("<<'PY'\n", 1)[1].rsplit('PY', 1)[0]
            with tempfile.TemporaryDirectory() as tmp:
                for case in ('none', 'warn', 'err'):
                    for x in ('kpc-hidden.txt', 'kpc-hidden-errors.txt'):
                        if os.path.exists(os.path.join(tmp, x)): os.remove(os.path.join(tmp, x))
                    if case != 'none': open(os.path.join(tmp, 'kpc-hidden.txt'), 'w').write('t - m\n')
                    if case == 'err': open(os.path.join(tmp, 'kpc-hidden-errors.txt'), 'w').write('t - m\n')
                    e = dict(os.environ, RUNNER_TEMP=tmp, KPC_STEPS='{}', KPC_FAIL_SAFE='1' if fs else '', GITHUB_STEP_SUMMARY=os.path.join(tmp, 's'), GITHUB_JOB=jn)
                    p = subprocess.run([sys.executable, '-B', '-'], input=py, env=e, capture_output=True, text=True)
                    want = 1 if (case == 'err' and fs) else 0
                    line = ('::warning title=Hidden failures::' in p.stdout) == (case != 'none')
                    if p.returncode != want or not line: beh.append(f'{n}:{jn} {case}: exit {p.returncode} (want {want}), line {line}')
check(not syn, f'every run block of the bots not paused is valid bash ({syn[:3]})')
check(not beh, f'every G8 step: red on a caught error only when safe; a Hidden failures line when anything was caught ({beh[:3]})')
check(len(safe) >= 25 and not any(s.startswith(('kpc-fers-line.', 'kpc-fers-regions', 'kpc-watchdog', 'kpc-engine.', 'kpc-waiting-room')) for s in safe), f'{len(safe)} jobs safe to fail, {len(notsafe)} not')
t = docs['kpc-answer-sheet-check.yml'][0]
check('"Mapping / Quality" || { kpc_rc=$?; echo "::error title=kpc_status.py::' in t and '(check not saved)" data/status || { kpc_rc=$?; echo "::error title=Save::' in t, 'answer-sheet check: a red board line that is not written or saved is recorded')
t = docs['kpc-fers-postline.yml'][0]
check(t.count('|| { kpc_rc=$?; echo "::error title=') >= 3 and 'kpc_fers_postline.py || true' not in t, '2-fer post-line: the report, the gate update and the save record a failure')
check('key-bots-errors-and-silence.json || { kpc_rc=$?; echo "::warning title=Watchdog notes::' in docs['kpc-watchdog.yml'][0], 'watchdog: a failed restore of its notes is recorded')
base = next((r for r in ('nr-data-main', 'origin/main', 'main') if subprocess.run(['git', 'rev-parse', '-q', '--verify', r], cwd=HERE, capture_output=True).returncode == 0), None)
if base == 'nr-data-main':
    cr = lambda txt: sorted(re.findall(r"^\s*-\s*cron:\s*'([^']+)'", txt, re.M))
    moved = [n for n, (t, d) in docs.items() if (p := subprocess.run(['git', 'show', f'{base}:.github/workflows/{n}'], cwd=HERE, capture_output=True, text=True)).returncode == 0 and cr(p.stdout) != cr(t)]
    check(not moved, f'no cron line changed vs {base} ({moved[:3]})')
print('ALL PASS' if ok else 'SOME FAILED'); sys.exit(0 if ok else 1)
