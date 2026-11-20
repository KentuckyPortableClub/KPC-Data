#!/usr/bin/env python3
"""Park facts workflow, 20 Nov 2026: STRICT. No step may fail quietly (no continue-on-error), a missing input holds the run,
only the save job may write, and the size witness gets the key's joined layers. Offline. Ends ALL PASS or SOME FAILED."""
import pathlib, re, subprocess, sys, tempfile

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
WF = ROOT / '.github/workflows/kpc-park-facts.yml'
ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


txt = WF.read_text(encoding='utf-8')
d = yaml.safe_load(txt)
on = d.get(True) or d.get('on')
jobs = d['jobs']
steps = [s for j in jobs.values() for s in j['steps']]
check('no step or job keeps going on an error (continue-on-error is gone)',
      'continue-on-error' not in txt and not any('continue-on-error' in j for j in jobs.values()))
check('no timer: it runs only after the page reader / tool trial, or by hand', 'schedule' not in on and set(on) == {'workflow_run', 'workflow_dispatch'})
check('the whole workflow can only read', d.get('permissions') == {'contents': 'read'})
writers = [n for n, j in jobs.items() if (j.get('permissions') or {}).get('contents') == 'write']
check('only the save job may write', writers == ['save'])
save_steps = jobs['save']['steps']
check('the save job only saves (checkout, the built file, one save step)', len(save_steps) == 3)
check('every shell step stops on the first error', all(s['run'].lstrip().startswith('set -euo pipefail') for s in steps if 'run' in s))
check('no step hides an error (no "|| warn", "|| true" or "2>/dev/null ||")',
      not re.search(r'\|\|\s*(warn|true)\b|2>/dev/null\s*\|\|', txt))
check('a missing artifact holds the save', any(s.get('with', {}).get('if-no-files-found') == 'error' for s in jobs['build']['steps']))
build = '\n'.join(s.get('run', '') for s in jobs['build']['steps'])
check('the size witness reads the key (--key us-key and ca-key, --layers)',
      '--key "$W/links/data/us-key"' in build and '--key "$W/links/data/ca-key"' in build and '--layers' in build)
check("the keeper's sizes are read when they exist", '--keeper-sizes' in build and 'data/keeper-sizes/latest.json' in build)

# the read step really holds the run when an input is missing (tools-out has no acres/acres.json here)
read = next(s['run'] for s in jobs['build']['steps'] if s.get('name', '').startswith('Read the saved files'))
with tempfile.TemporaryDirectory() as t:
    t = pathlib.Path(t)
    subprocess.run(['git', 'init', '-q', str(t / 'origin')], check=True)
    subprocess.run(['git', '-C', str(t / 'origin'), '-c', 'user.name=t', '-c', 'user.email=t@t', 'commit', '-q', '--allow-empty', '-m', 'x'],
                   check=True)
    subprocess.run(['git', '-C', str(t / 'origin'), 'branch', '-q', 'tools-out'], check=True)
    subprocess.run(['git', 'clone', '-q', str(t / 'origin'), str(t / 'kpcdata')], check=True)
    r = subprocess.run(['bash', '-c', read], cwd=t, env={'RUNNER_TEMP': str(t / 'rt'), 'PATH': '/usr/bin:/bin:/usr/local/bin'},
                       capture_output=True, text=True)
    check('a missing acres/acres.json holds the run (non-zero exit, nothing built)', r.returncode != 0 and not (t / 'rt/pf/out/park-facts.json').exists())

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
