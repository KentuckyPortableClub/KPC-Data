#!/usr/bin/env python3
"""KPC owner, 2026-11-16 (proof of work item 1, round 1 fix): in kpc-fers-line.yml a red receipt STOPS the line.
The pass steps are continue-on-error, so the receipt check alone would only be a hidden-failure warning. This checks the wiring:
  - both pass steps (Passes 1 + 2 in the fetcher, Passes 3 + 5 in the worker) run kpc_fers_receipt.py check and, when it is red,
    write the step output receipt=red (the snippet is also run in bash with a stand-in check that exits 2 / 0);
  - the fetcher and the worker hand it on as the job output 'receipt', and each has a step that ends the job red on it;
  - the worker does not start, the checker does not start, and the checker's Save does not run when either says red;
  - no schedule changed against origin/main.
Static and offline."""
import os, pathlib, re, subprocess, sys, tempfile
import yaml
ROOT = pathlib.Path(__file__).resolve().parents[1]
WF = ROOT / '.github/workflows/kpc-fers-line.yml'
ok = True


def check(c, msg):
    global ok
    print(('PASS ' if c else 'FAIL ') + msg); ok = ok and bool(c)


text = WF.read_text(encoding='utf-8')
d = yaml.safe_load(text)
J = d['jobs']
on = d.get(True) or d.get('on') or {}


def step(job, sid):
    return next((s for s in J[job]['steps'] if s.get('id') == sid), None)


for job, sid, passes in (('fetcher', 'kept_green_4', '$RAN'), ('worker', 'kept_green_8', '3,5')):
    st = step(job, sid)
    run = (st or {}).get('run', '')
    line = next((l for l in run.split('\n') if 'kpc_fers_receipt.py check' in l), '')
    check(st is not None and st.get('continue-on-error') is True, f'{job}: the pass step {sid} is still continue-on-error (why the output is needed)')
    check(f'--passes "{passes}"' in line and '--allow-time-stop' in line and 'echo "receipt=red" >> "$GITHUB_OUTPUT"' in line,
          f'{job}: {sid} checks the receipt of its passes and writes receipt=red when it is red')
    check(J[job].get('outputs', {}).get('receipt') == f'${{{{ steps.{sid}.outputs.receipt }}}}', f'{job}: the job output receipt comes from {sid}')
    names = [s.get('name', '') for s in J[job]['steps']]
    stop = next((s for s in J[job]['steps'] if s.get('name', '').startswith('A red receipt ends this line here')), None)
    check(stop is not None and f"steps.{sid}.outputs.receipt == 'red'" in str(stop.get('if')) and not stop.get('continue-on-error')
          and re.search(r'\bexit 1\b', stop.get('run', '')) and names.index(stop['name']) > names.index(st['name']),
          f'{job}: a later step ends the job red when {sid} says receipt=red')
    # the snippet itself, in bash, with a stand-in receipt check
    with tempfile.TemporaryDirectory() as t:
        tp = pathlib.Path(t); (tp / '.github/scripts').mkdir(parents=True)
        res = {}
        for rc in (2, 0):
            (tp / '.github/scripts/kpc_fers_receipt.py').write_text(f'import sys; sys.exit({rc})\n')
            out = tp / f'out{rc}'; out.write_text('')
            env = {**os.environ, 'GITHUB_OUTPUT': str(out), 'RUNNER_TEMP': t, 'RAN': '1,2'}
            p = subprocess.run(['bash', '-c', line], cwd=t, env=env, capture_output=True, text=True)
            res[rc] = (p.returncode, out.read_text().strip())
        check(res[2] == (2, 'receipt=red') and res[0] == (0, ''), f'{job}: in bash, a red check exits 2 and writes receipt=red; a done one writes nothing ({res})')

wif = str(J['worker'].get('if'))
cif = str(J['checker'].get('if'))
save = next((s for s in J['checker']['steps'] if str(s.get('name', '')).startswith('Save')), {})
check("needs.fetcher.outputs.receipt != 'red'" in wif, 'the worker does not start when the fetcher receipt is red')
check("needs.fetcher.outputs.receipt != 'red'" in cif and "needs.worker.outputs.receipt != 'red'" in cif, 'the checker does not start when either receipt is red')
check("needs.fetcher.outputs.receipt != 'red'" in str(save.get('if')) and "needs.worker.outputs.receipt != 'red'" in str(save.get('if')),
      "the checker's Save does not run when either receipt is red")
check(set(J['checker'].get('needs') or []) >= {'fetcher', 'worker'} and 'fetcher' in (J['worker'].get('needs') or []), 'the jobs that read the outputs need the jobs that write them')
try:
    main = subprocess.run(['git', 'show', 'origin/main:.github/workflows/kpc-fers-line.yml'], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    cron = lambda s: re.findall(r'cron:.*', s)
    check(cron(main) == cron(text), 'no schedule changed against origin/main')
except subprocess.CalledProcessError:
    print('SKIP no origin/main to compare the schedule with')
print('ALL PASS' if ok else 'SOME FAILED'); sys.exit(0 if ok else 1)
