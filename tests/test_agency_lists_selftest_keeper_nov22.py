#!/usr/bin/env python3
"""Review N15 (KPC owner, 22 Nov 2026): kpc_agency_lists.py --selftest passes both outside the store keeper and inside it
(KPC_KEEPER_HOST_RULES=owner-2026-11-15), and checks the keeper case on its own: ArcGIS / Forest Service hosts may be read there,
a never-contact host never. The kpc_manners.py header no longer says every services*.arcgis.com host is never read. Offline."""
import os, pathlib, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
S = ROOT / '.github/scripts'
ok = True
def check(msg, cond):
    global ok
    ok &= bool(cond); print(('PASS ' if cond else 'FAIL ') + msg, flush=True)
for val in (None, 'owner-2026-11-15'):
    env = dict(os.environ); env.pop('KPC_KEEPER_HOST_RULES', None)
    if val: env['KPC_KEEPER_HOST_RULES'] = val
    r = subprocess.run([sys.executable, '-B', str(S / 'kpc_agency_lists.py'), '--selftest'], capture_output=True, text=True, env=env, cwd=str(ROOT), timeout=300)
    out = r.stdout + r.stderr
    fails = [l.strip() for l in out.splitlines() if l.strip().startswith(('FAIL', 'SELF-TEST FAILED'))]
    check(f'--selftest passes with KPC_KEEPER_HOST_RULES={val or "(unset)"} (exit {r.returncode}, {len(fails)} FAIL: {fails[:2]})', r.returncode == 0 and not fails)
    check(f'--selftest checks the keeper case on its own ({val or "unset"})', 'inside the store keeper an ArcGIS' in out)
head = (S / 'kpc_manners.py').read_text(encoding='utf-8')[:1200]
check('the kpc_manners.py header says the store keeper is the exception', "except inside the store keeper" in head)
print('ALL PASS' if ok else 'SOME FAILED'); sys.exit(0 if ok else 1)
