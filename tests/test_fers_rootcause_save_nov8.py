#!/usr/bin/env python3
"""Nov 8: kpc-fers.yml save-safety + stale/failed-key gate (Brandon t802u; Quality NO on #55 ownership patch).
Ownership monkeypatch removed. Waiting-room divert is a follow-up."""
import pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
Y = (ROOT / '.github/workflows/kpc-fers.yml').read_text(encoding='utf-8')
GATE = (ROOT / '.github/scripts/kpc_fers_key_gate.py').read_text(encoding='utf-8')
fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)
        print('FAIL', msg)
    else:
        print('PASS', msg)


# --- Save safety ---
check("success() && steps.kept_green_3.outcome == 'success'" in Y,
      'Save requires success() and Look step outcome=success (no push on cancel/fail)')
save = Y.split('name: Save (once', 1)[1].split('name: Report', 1)[0]
header = save.split('run:', 1)[0]
header_code = '\n'.join(ln for ln in header.splitlines() if not ln.lstrip().startswith('#'))
check('if: always()' not in header_code, 'Save step condition is not if: always()')
check('continue-on-error: true' not in header_code, 'Save is not continue-on-error')
check('STRICT=1' in save and 'kpc_push_data.sh' in save, 'Save uses STRICT=1 push')

# --- Key gate ---
check('kpc_fers_key_gate.py' in Y, 'workflow runs stale/failed key gate')
check('rules_of_run' in GATE and 'current freeze' in GATE, 'key gate compares rules_of_run to freeze hash')
check('failed' in GATE and 'refusing STATES' in GATE, 'key gate refuses STATES that hit index.failed')

# --- Ownership patch must be gone ---
check('kpc_fers_patch_world_ownership' not in Y, 'workflow does not call ownership patch')
check(not (ROOT / '.github/scripts/kpc_fers_patch_world_ownership.py').exists(),
      'ownership patch script file removed')
check('ownership not checked' not in Y and 'designations-only' not in Y.lower(),
      'no designations-only=ok wording in workflow')

# --- Waiting-room divert: the Nov 8 follow-up, done Nov 9 evening (KZ4CP 5:12 PM CST: 2-fers are hidden beta, never public live files) ---
check('kpc_waiting_room.py divert data/fers' in Y, 'changed live 2-fer files go to the waiting room (the Nov 8 follow-up, done Nov 9 evening)')

if fails:
    print(f'SOME FAILED ({len(fails)})')
    sys.exit(1)
print('ALL PASSED')
