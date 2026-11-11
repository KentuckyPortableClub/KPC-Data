"""Owner rule, 2026-11-10: the 2-fer chain starts ONCE per key copy that really copied a key, by B3's own 'chain' job (dispatch
only, for every event type; no workflow_run), and the chain starts the post-line check itself (the post-line workflow does not
listen to the chain). No new cron. Run: python3 -B tests/test_fixbundle_chain_trigger_nov4.py"""
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
check('chain has no workflow_run trigger', 'workflow_run' in ch['on'], False)
check('chain can be dispatched', 'workflow_dispatch' in ch['on'], True)
check('chain has no schedule', 'schedule' in ch['on'], False)
check('chain plan has no event condition', 'if' in ch['jobs']['plan'], False)
j = b3['jobs'].get('chain') or {}
check('B3 has a chain job after the copy', j.get('needs'), 'copy')
check('B3 chain job: every event type, but only when the copy succeeded AND copied a key',
      ("needs.copy.result == 'success'" in j.get('if', ''), 'github.event_name' in j.get('if', ''), "needs.copy.outputs.keys != ''" in j.get('if', '')), (True, False, True))
check('B3 copy job exposes the keys it copied', 'keys' in (b3['jobs']['copy'].get('outputs') or {}), True)
check('the post-line workflow does not listen to the chain', ch['name'] in (pl['on'].get('workflow_run') or {}).get('workflows', []), False)
run = '\n'.join(s.get('run', '') for s in j.get('steps', []))
check('B3 chain job dispatches kpc-fers-chain.yml and fails visibly when it cannot',
      ('workflows/kpc-fers-chain.yml/dispatches' in run, 'GITHUB_STEP_SUMMARY' in run, 'exit 1' in run), (True, True, True))
check('B3 permissions allow the dispatch', b3['permissions'].get('actions'), 'write')
check('chain permissions allow the post-line dispatch', ch['permissions'].get('actions'), 'write')
p = ch['jobs'].get('postline') or {}
check('chain starts the post-line check itself (the only start for a chain run)',
      ("needs.plan.outputs.run == 'yes'" in p.get('if', ''), 'kpc-fers-postline.yml/dispatches' in str(p.get('steps'))), (True, True))
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
