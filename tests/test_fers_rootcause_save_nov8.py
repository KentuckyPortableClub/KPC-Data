#!/usr/bin/env python3
"""Nov 8: kpc-fers.yml save-safety + stale-key gate + world ownership patch (Brandon t802u).
Fails if Save can run on cancel/fail, if the ownership mass-drop block is unpatched by the workflow,
or if the key gate is missing."""
import pathlib, re, sys, tempfile, shutil

ROOT = pathlib.Path(__file__).resolve().parents[1]
Y = (ROOT / '.github/workflows/kpc-fers.yml').read_text(encoding='utf-8')
GATE = (ROOT / '.github/scripts/kpc_fers_key_gate.py').read_text(encoding='utf-8')
PATCH = (ROOT / '.github/scripts/kpc_fers_patch_world_ownership.py').read_text(encoding='utf-8')
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
# Only the step header (before run:) — inline comments may mention the old if: always()
header = save.split('run:', 1)[0]
header_code = '\n'.join(ln for ln in header.splitlines() if not ln.lstrip().startswith('#'))
check('if: always()' not in header_code, 'Save step condition is not if: always()')
check('continue-on-error: true' not in header_code, 'Save is not continue-on-error')
check('STRICT=1' in save and 'kpc_push_data.sh' in save, 'Save uses STRICT=1 push')

# --- Root-cause wiring in workflow ---
check('kpc_fers_key_gate.py' in Y, 'workflow runs stale/incomplete key gate')
check('kpc_fers_patch_world_ownership.py' in Y, 'workflow patches world ownership before the bot')
check("matrix.region == 'world'" in Y and 'kpc_fers_patch_world_ownership' in Y,
      'ownership patch only on world matrix job')
# Waiting-room divert intentionally NOT in this PR
check('divert data/fers' not in Y, 'waiting-room divert left out of this PR (follow-up)')

# --- Gate script behavior ---
check('rules_of_run' in GATE and 'current freeze' in GATE, 'key gate compares rules_of_run to freeze hash')
check('failed' in GATE and 'refusing STATES' in GATE, 'key gate refuses STATES that hit index.failed')

# --- Ownership patch transforms the known-bad block ---
check("no park here owns land (designations only)" in PATCH, 'patch knows the bad Nov-6 block')
check('ownership not checked' in PATCH, 'patch keeps designations-only as ok with ownership-not-checked note')
# Apply to a fixture
fx = tempfile.mkdtemp()
try:
    src = pathlib.Path(fx) / 'kpc_fers.py'
    # minimal stand-in containing the real OLD block
    old_block = '''def ownership_step(s, parks, PIN):
    owners = {}
    real = {}
    if REGION == 'world':
        if real and len(set(real.values())) <= 1 and '?' not in owners.values(): return 'ok', 'one owner (or designations on it): layered'
        return 'not sure', ('owners differ' if real else 'no park here owns land (designations only)') + '; no land register read for this country yet'
    return 'ok', 'x'
'''
    # Use exact OLD from patch module
    import importlib.util
    spec = importlib.util.spec_from_file_location('patch', ROOT / '.github/scripts/kpc_fers_patch_world_ownership.py')
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    src.write_text('REGION = "world"\n' + mod.OLD + '\n', encoding='utf-8')
    rc = mod.main(['x', str(src)])
    check(rc == 0, 'patch returns 0 on the known-bad block')
    out = src.read_text(encoding='utf-8')
    check('ownership not checked' in out, 'patched file has ownership-not-checked ok path')
    check('no park here owns land (designations only)' not in out, 'patched file no longer mass-drops designations-only')
    rc2 = mod.main(['x', str(src)])
    check(rc2 == 0, 'patch is idempotent')
finally:
    shutil.rmtree(fx, ignore_errors=True)

if fails:
    print(f'SOME FAILED ({len(fails)})')
    sys.exit(1)
print('ALL PASSED')
