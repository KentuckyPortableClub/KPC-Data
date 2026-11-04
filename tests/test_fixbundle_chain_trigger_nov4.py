"""Nov 4 PM fix bundle item 3: the 2-fer chain starts right after EVERY key copy (scheduled B3 = workflow_run; a bot-started
B3, e.g. the watchdog's restart, = B3's own 'chain' job dispatches it), and a dispatched chain starts the post-line check.
No new cron. Run: python3 -B tests/test_fixbundle_chain_trigger_nov4.py"""
import pathlib, re, subprocess, sys
import yaml
R = pathlib.Path(__file__).resolve().parents[1]; W = R / '.github/workflows'
ok = True
def check(what, got, want):
    global ok
    good = got == want; ok &= good
    print(('PASS ' if good else 'FAIL ') + f'{what}: got {got!r}' + ('' if good else f', want {want!r}'))
def y(n): d = yaml.safe_load(open(W / n)); d['on'] = d.get('on', d.get(True)); return d
ch, b3, pl = y('kpc-fers-chain.yml'), y('kpc-copy-from-links.yml'), y('kpc-fers-postline.yml')
check('chain still listens to B3 by workflow_run', ch['on']['workflow_run']['workflows'], ['KPC copy site data to KPC-Data (Step B3)'])
check('chain can be dispatched', 'workflow_dispatch' in ch['on'], True)
check('chain has no schedule', 'schedule' in ch['on'], False)
check('chain plan runs on a dispatch too', 'workflow_dispatch' in ch['jobs']['plan']['if'], True)
j = b3['jobs'].get('chain') or {}
check('B3 has a chain job after the copy', j.get('needs'), 'copy')
check('B3 chain job only when the copy succeeded and the run was NOT scheduled (a scheduled run fires workflow_run)',
      ("needs.copy.result == 'success'" in j.get('if', ''), "github.event_name != 'schedule'" in j.get('if', '')), (True, True))
run = '\n'.join(s.get('run', '') for s in j.get('steps', []))
check('B3 chain job dispatches kpc-fers-chain.yml and fails visibly when it cannot',
      ('workflows/kpc-fers-chain.yml/dispatches' in run, 'GITHUB_STEP_SUMMARY' in run, 'exit 1' in run), (True, True, True))
check('B3 permissions allow the dispatch', b3['permissions'].get('actions'), 'write')
check('chain permissions allow the post-line dispatch', ch['permissions'].get('actions'), 'write')
p = ch['jobs'].get('postline') or {}
check('dispatched chain starts the post-line check (only on a dispatch, never twice)',
      ("github.event_name == 'workflow_dispatch'" in p.get('if', ''), 'kpc-fers-postline.yml/dispatches' in str(p.get('steps'))), (True, True))
check('post-line check takes the run url on a dispatch', ('workflow_dispatch' in pl['on'], 'inputs.run_url' in open(W / 'kpc-fers-postline.yml').read(),
      "github.event_name == 'workflow_dispatch'" in pl['jobs']['postline']['if']), (True, True, True))
def crons(rev):
    out = {}
    for n in ('kpc-fers-chain.yml', 'kpc-copy-from-links.yml', 'kpc-fers-postline.yml'):
        t = subprocess.run(['git', '-C', str(R), 'show', f'{rev}:.github/workflows/{n}'], capture_output=True, text=True).stdout if rev else open(W / n).read()
        out[n] = re.findall(r"^\s*-\s*cron:\s*'([^']+)'", t, re.M)
    return out
check('no new cron (same schedules as before the fix)', crons(None), crons('a569c9b35') if subprocess.run(['git', '-C', str(R), 'cat-file', '-e', 'a569c9b35'], capture_output=True).returncode == 0 else crons(None))
print('ALL PASS' if ok else 'SOME FAILED'); sys.exit(0 if ok else 1)
