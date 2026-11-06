#!/usr/bin/env python3
"""Nov 6 improvements 2: ledger-first flow (kpc_ledger_flow.py). Its selftest (16 frozen cases, temp folder), plus: the new kind
'pile-enter' never counts as a pile exit, a confirmed pile-enter needs two different agents, and the repo's ledger is untouched."""
import hashlib, os, pathlib, subprocess, sys, tempfile
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github/scripts')); os.chdir(ROOT)
import kpc_agreement_ledger as AL
import kpc_ledger_flow as LF
ok = True
def check(msg, cond):
    global ok
    ok &= bool(cond); print(('PASS ' if cond else 'FAIL ') + msg)
D = ROOT / 'data/agreement-ledger'
snap = lambda: {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(D.glob('*')) if p.is_file()}
before = snap()
r = subprocess.run([sys.executable, '-B', '.github/scripts/kpc_ledger_flow.py', '--selftest'], capture_output=True, text=True, timeout=120)
check('kpc_ledger_flow.py --selftest: ' + (r.stdout.strip().splitlines() or ['?'])[-1], r.returncode == 0 and 'SELFTEST PASS' in r.stdout)
td = pathlib.Path(tempfile.mkdtemp()); AL.LEDGER, AL.STATE = td / 'l.csv', td / 's.json'; AL.save_rows([]); AL.save_state({'auto': True})
LF.propose_row('US-0099', 'pile-enter', 'key-health', 'outline lost')
check('pile-enter is a ledger kind', 'pile-enter' in AL.KINDS)
try: AL.confirm('US-0099', 'pile-enter', 'key-health'); same = False
except ValueError: same = True
check('the proposer cannot confirm its own pile-enter', same)
AL.save_rows(AL.confirm('US-0099', 'pile-enter', 'quality'))
check('a confirmed pile-enter is ready as pile-enter', len(AL.ready('pile-enter')) == 1)
check('a confirmed pile-enter never counts as a pile EXIT, even with auto on', AL.exit_candidates(auto=True)['would_exit'] == [])
check("the repo's data/agreement-ledger/ is unchanged", snap() == before)
print('ALL PASS' if ok else 'SOME FAILED'); sys.exit(0 if ok else 1)
