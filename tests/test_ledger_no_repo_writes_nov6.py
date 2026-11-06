#!/usr/bin/env python3
"""Running the pile-solver selftest and the ledger tests must leave the repo's data/agreement-ledger/ byte-identical
(ledger.csv and state.json). Also: save_state() with no path writes to AL.STATE as set at call time."""
import hashlib, os, pathlib, subprocess, sys, tempfile
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / '.github/scripts'))
os.chdir(ROOT)
import kpc_agreement_ledger as AL
fails = []
def check(name, got, want):
    ok = got == want; print(('PASS ' if ok else 'FAIL ') + name + ('' if ok else f'  got={got!r} want={want!r}'))
    if not ok: fails.append(name)
D = ROOT / 'data/agreement-ledger'
def snap(): return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(D.glob('*')) if p.is_file()}
before = snap()
td = pathlib.Path(tempfile.mkdtemp()); AL.STATE = td / 'state.json'
AL.save_state({'auto': False})
check('save_state() default path = AL.STATE at call time', (td / 'state.json').exists(), True)
env = dict(os.environ, DATA=str(ROOT))
for cmd in (['.github/scripts/kpc_pile_solver.py', '--selftest'],
            ['tests/test_pile_solver_two_agreements_nov6.py'],
            ['tests/test_pile_solver_15km_shortname_nov6.py'],
            ['tests/test_agreement_ledger_nov6.py']):
    if not (ROOT / cmd[0]).exists(): continue
    subprocess.run([sys.executable, '-B'] + cmd, cwd=ROOT, env=env, capture_output=True)
    check(f'{cmd[0]} leaves data/agreement-ledger/ unchanged', snap(), before)
print('ALL PASS' if not fails else 'SOME FAILED'); sys.exit(1 if fails else 0)
