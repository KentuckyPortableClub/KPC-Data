#!/usr/bin/env python3
"""Nov 9 PM (Quality NO on KPC-Data #57): a kpc_fers.py crash (exit 1) or hard stop (exit 3) must END the 'Look for shared ground'
step with that code, so its outcome is 'failure', Save (if: steps.kept_green_3.outcome == 'success') does not run, and Report goes red.
Runs the step's real shell script with a fake python3. Offline."""
import os, pathlib, stat, subprocess, sys, tempfile
import yaml
HERE = pathlib.Path(__file__).resolve().parent.parent
ok = True
def check(c, msg):
    global ok
    print(('PASS ' if c else 'FAIL ') + msg); ok = ok and bool(c)

wf = yaml.safe_load(open(HERE / '.github/workflows/kpc-fers.yml', encoding='utf-8'))
steps = wf['jobs']['fers']['steps']
by = {s.get('id'): s for s in steps if s.get('id')}
look, save = by['kept_green_3'], by['kept_green_5']
names = [s.get('id') for s in steps]
check(names.index('kept_green_3') < names.index('kept_green_5'), 'Look runs before Save')
check("steps.kept_green_3.outcome == 'success'" in save.get('if', '') and 'always()' not in save.get('if', ''), "Save needs Look's outcome == success, never always()")
check(not save.get('continue-on-error'), 'Save is not continue-on-error')
check(by['key_gate'].get('continue-on-error') in (None, False) and 'exit 1' in by['key_gate']['run'], 'key gate fails the job (Save never runs on a stale key)')
rep = next(s for s in steps if str(s.get('name', '')).startswith('Report hidden failures'))
check("kept_green_3" in rep['run'] and 'sys.exit(1)' in rep['run'] and rep.get('if') == 'always()', 'Report goes red when Look failed')

def run(rc_fers, pass_, region='na', rc_other=0):
    with tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(td); fake = td / 'bin'; fake.mkdir()
        py = fake / 'python3'
        py.write_text(f'#!/bin/bash\necho "fake $@" >> {td}/calls\ncase "$1" in *kpc_fers.py) exit {rc_fers};; *) exit {rc_other};; esac\n')
        py.chmod(py.stat().st_mode | stat.S_IEXEC)
        env = dict(os.environ, PATH=f'{fake}:{os.environ["PATH"]}', RUNNER_TEMP=str(td), PASS=pass_, MINUTES='320', STATES='', REGION=region,
                   RUN_TAG='t', KPC_JOB_T0=str(int(__import__('time').time())))
        r = subprocess.run(['bash', '-e', '-c', look['run']], env=env, capture_output=True, text=True, timeout=60)
        calls = (td / 'calls').read_text().splitlines() if (td / 'calls').exists() else []
        return r.returncode, calls

for p in ('all', '1'):
    rc, calls = run(0, p)
    check(rc == 0, f'pass={p}: a clean run ends the step green (rc {rc})')
    rc, calls = run(1, p)
    check(rc == 1, f'pass={p}: a crash (exit 1) ends the step with 1 (rc {rc})')
    check(sum('kpc_fers.py' in c for c in calls) == 1, f'pass={p}: no later pass runs after a crash ({len(calls)} calls)')
    rc, calls = run(3, p)
    check(rc == 3, f'pass={p}: a hard stop (exit 3) ends the step with 3 (rc {rc})')
rc, calls = run(0, '1', region='ky', rc_other=1)
check(rc == 1, f'ky: a crash in the known / expected checks also ends the step (the files Save copies) (rc {rc})')
print('ALL PASS' if ok else 'FAILED'); sys.exit(0 if ok else 1)
