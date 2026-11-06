#!/usr/bin/env python3
"""Nov 6 improvements 5 (KPC-Data side): the 2-fer self-check is wired into the EXISTING line (kpc-fers-line.yml checker, which
kpc-fers-chain.yml starts after a new key build): before the line check, guarded until the KPC-Links script is merged, never
fails the line, its hold list is saved by the existing '*-<tag>.json' save, and no workflow got a new schedule (no new cron)."""
import pathlib, re, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
ok = True
def check(msg, cond):
    global ok
    ok &= bool(cond); print(('PASS ' if cond else 'FAIL ') + msg)
y = (ROOT / '.github/workflows/kpc-fers-line.yml').read_text()
chk = y.split('  checker:', 1)[1] if '  checker:' in y else y
i, j = chk.find('kpc_fers_selfcheck.py data/fers'), chk.find('kpc_fers_line_check.py')
check('the checker runs the self-check before the line check', 0 <= i < j)
check('guarded until KPC-Links has the script', '[ -f .github/scripts/kpc_fers_selfcheck.py ]' in chk)
check("a stopped self-check is a caught error, never a red line ('|| {')", re.search(r"kpc_fers_selfcheck\.py data/fers \. \|\| \{ kpc_rc=\$\?", chk))
check("the hold list name fers-holds-<tag>.json is saved by the existing '*-$RUN_TAG.json' copy", 'for f in data/fers/*-$RUN_TAG.json' in chk)
chain = (ROOT / '.github/workflows/kpc-fers-chain.yml').read_text()
check('the chain still starts this line (uses: ./.github/workflows/kpc-fers-line.yml)', 'uses: ./.github/workflows/kpc-fers-line.yml' in chain)
check('no schedule in the line or the chain (no new cron)', not re.search(r'^\s*schedule:', y + chain, re.M))
print('ALL PASS' if ok else 'SOME FAILED'); sys.exit(0 if ok else 1)
