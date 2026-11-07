#!/usr/bin/env python3
"""Offline test, round 4 item 1 (Nov 7): GPS packs follow the NIGHTLY waiting-room run only; fast exit when no area changed.
No network, nothing is run on GitHub: the workflow files are read as YAML; the fast-exit shell is run with stubs."""
import os, pathlib, re, subprocess, sys, tempfile
import yaml

HERE = pathlib.Path(__file__).resolve().parent.parent
WF = HERE / '.github/workflows'
ok = True


def check(c, msg):
    global ok
    print(('PASS ' if c else 'FAIL ') + msg); ok = ok and bool(c)


def y(n):
    d = yaml.safe_load(open(WF / n, encoding='utf-8')); d['on'] = d.pop(True, d.get('on')); return d


g, w = y('kpc-gps-packs.yml'), y('kpc-waiting-room.yml')
wtxt = (WF / 'kpc-waiting-room.yml').read_text(encoding='utf-8')
on = g['on']
check(on.get('workflow_run', {}).get('workflows') == [w['name']], 'GPS packs: workflow_run on the waiting room by its exact name')
check(on['workflow_run'].get('types') == ['completed'], 'GPS packs: types completed')
check('workflow_dispatch' in on, 'GPS packs: still startable by hand')
crons = [c['cron'] for c in on['schedule']]
check(crons == ['29 8 * * 1'], 'GPS packs: no new cron (only the Monday safety net)')
check([c['cron'] for c in w['on']['schedule']] == ['42 */2 * * *', '13 11 * * *'], 'waiting room: crons unchanged')
cond = g['jobs']['run']['if']
check("display_title == 'KPC waiting room (nightly)'" in cond and "event == 'schedule'" in cond, 'job if: only the nightly titled scheduled run')
check("github.event_name != 'workflow_run'" in cond, 'job if: dispatch and Monday cron are not gated')
rn = w['run-name']
nightly = [c for c in [c['cron'] for c in w['on']['schedule']] if c in rn]
check(nightly == ['13 11 * * *'], 'run-name tests the nightly cron string only')
check("'nightly'" in rn and "'every 2 h'" in rn, 'run-name titles: nightly / every 2 h')


def title(schedule, event='schedule', mode=''):   # same logic as the run-name expression
    return 'KPC waiting room (%s)' % ('nightly' if schedule == '13 11 * * *' else 'every 2 h' if event == 'schedule' else mode or 'by hand')


def go(ev, tit, concl='success'):                  # same logic as the job if:
    return ev == 'schedule' and concl != 'cancelled' and tit == 'KPC waiting room (nightly)'


check(go('schedule', title('13 11 * * *')), 'nightly run -> GPS job runs')
check(not go('schedule', title('42 */2 * * *')), 'every-2-hours run -> GPS job skipped')
check(not go('workflow_dispatch', title('', 'workflow_dispatch', 'check')), 'by-hand waiting-room run -> skipped')
check(not go('schedule', title('13 11 * * *'), 'cancelled'), 'cancelled nightly -> skipped')
check('KPC waiting room (nightly)' != 'KPC waiting room (every 2 h)', 'titles differ')
# nothing else reads the waiting room's title
check(not re.search(r'display_title', ''.join((WF / f).read_text(encoding='utf-8') for f in os.listdir(WF) if f not in ('kpc-gps-packs.yml', 'kpc-waiting-room.yml'))), 'no other workflow reads display_title')

# fast exit: run the real step lines with stubs
steps = g['jobs']['run']['steps']
run = next(s['run'] for s in steps if s.get('id') == 'kept_green_1')
check('S0=$(sha256sum ../out/state.json' in run and 'fast exit' in run, 'Build step has the state.json fast exit')
i0, i1 = run.index('S0=$('), run.index('exit 0\nfi') + len('exit 0\nfi')
pre = 'E=0; N=1; MB=1\n'
for name, change, want in (('unchanged', False, 'fast exit'), ('rebuilt', True, 'REACHED')):
    with tempfile.TemporaryDirectory() as t:
        os.makedirs(t + '/work/out'); os.makedirs(t + '/work/k')
        open(t + '/work/out/state.json', 'w').write('{"done": {}}')
        body = run[i0:i1].replace('set +e\npython3 $P', 'X=1\npython3 $P')
        # the step text between S0 and the notice is the real command: replace the python call by a stub
        body = re.sub(r'python3 \$P[^\n]*\n', ('echo changed > ../out/state.json\n' if change else 'true\n'), body, count=1)
        body = body.replace('tail -5 /tmp/gps.txt', 'true').replace('ls ../out/data/gps/*.gpx.zip 2>/dev/null | wc -l', 'echo 1')
        script = 'cd %s/work/k\nP=x\nE=0\n' % t + body + '\necho REACHED\n'
        r = subprocess.run(['bash', '-c', script], capture_output=True, text=True)
        got = 'fast exit' if 'fast exit' in r.stdout else 'REACHED' if 'REACHED' in r.stdout else r.stdout + r.stderr
        check(got == want, 'state.json %s -> %s (got %s)' % (name, want, got))
print('ALL PASS' if ok else 'SOME FAILED'); sys.exit(0 if ok else 1)
