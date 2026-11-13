#!/usr/bin/env python3
"""Quality X1 (regrade Nov 13): release-approved is owner-dispatch only (triggered by KentuckyPortableClub only; D2 Nov 13). Item text such as 'by: chat 11' does not
authorize a release. Dead auto_trusted / source_ok regex paths are gone. The waiting-room
schedule defaults to check, never release-approved, and the watchdog does not restart it
as release-approved. release-areas is not inside continue-on-error.
"""
import os, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / '.github/scripts'))
import kpc_release_approved as RA  # noqa: E402

ok = True
def check(msg, cond):
    global ok
    if cond: print('  PASS', msg)
    else: ok = False; print('  FAIL', msg)

# no regex-on-own-text, no auto self-release
src = pathlib.Path(__file__).resolve().parents[1].joinpath('.github/scripts/kpc_release_approved.py').read_text()
check('source_ok regex path is gone', 'def source_ok' not in src and 'OWNER_SRC_RE' not in src)
check('auto_trusted is gone', 'def auto_trusted' not in src and 'TRUST_RUN' not in src)

# owner_dispatch_ok (Quality D2, Brandon Nov 13 8:34 AM CT: KentuckyPortableClub only, triggering actor, no owner fallback)
KEYS = ('GITHUB_EVENT_NAME', 'GITHUB_ACTOR', 'GITHUB_TRIGGERING_ACTOR', 'GITHUB_REPOSITORY_OWNER', 'KPC_RELEASE_ACTORS')
saved = {k: os.environ.pop(k) for k in list(os.environ) if k in KEYS}
try:
    ok1, why1 = RA.owner_dispatch_ok()
    check('no triggering actor is refused', (not ok1) and 'KentuckyPortableClub' in why1)
    os.environ['GITHUB_EVENT_NAME'] = 'schedule'
    os.environ['GITHUB_TRIGGERING_ACTOR'] = 'KentuckyPortableClub'
    ok2, why2 = RA.owner_dispatch_ok()
    check('a schedule run is refused even if triggered by KentuckyPortableClub', (not ok2) and 'owner-dispatch' in why2)
    os.environ['GITHUB_EVENT_NAME'] = 'workflow_dispatch'
    os.environ['GITHUB_TRIGGERING_ACTOR'] = 'someone-else'
    os.environ['KPC_RELEASE_ACTORS'] = 'someone-else'
    ok3, why3 = RA.owner_dispatch_ok()
    check('another account is refused, even if listed in KPC_RELEASE_ACTORS', (not ok3) and 'KentuckyPortableClub' in why3)
    os.environ['GITHUB_ACTOR'] = 'KentuckyPortableClub'
    ok3b, _ = RA.owner_dispatch_ok()
    check('github.actor=KentuckyPortableClub does not help when the triggering actor is someone else', not ok3b)
    os.environ['GITHUB_TRIGGERING_ACTOR'] = 'KentuckyPortableClub'
    ok4, _ = RA.owner_dispatch_ok()
    check('workflow_dispatch triggered by KentuckyPortableClub is allowed', ok4)
finally:
    for k in KEYS:
        os.environ.pop(k, None)
    os.environ.update(saved)

# waiting-room: schedule defaults to check; release-approved / release-areas owner-dispatch, not continue-on-error
ROOT = pathlib.Path(__file__).resolve().parents[1]
yml = (ROOT / '.github/workflows/kpc-waiting-room.yml').read_text()
check("schedule default mode is check, not release-approved",
      "inputs.mode || 'check'" in yml and "inputs.mode || 'release-approved'" not in yml)
# the owner release step has no continue-on-error
block = yml[yml.find('- name: Owner release'):]
nxt = block.find('\n      - name:', 10)
body = block if nxt < 0 else block[:nxt]
check('owner release step is workflow_dispatch only and has no continue-on-error',
      "github.event_name == 'workflow_dispatch'" in body
      and 'continue-on-error' not in body
      and 'kpc_release_approved.py' in body
      and 'kpc_fers_release_areas.py' in body
      and 'github.triggering_actor' in body and '"KentuckyPortableClub"' in body
      and 'repository_owner' not in body and 'KPC_RELEASE_ACTORS' not in body)
# the continue-on-error run step does not itself invoke the release scripts
run1 = yml[yml.find('- name: Run the waiting room'):yml.find('- name: Owner release')]
check('the continue-on-error waiting-room step does not run release-approved or release-areas',
      'kpc_release_approved.py' not in run1 and 'kpc_fers_release_areas.py' not in run1
      and 'continue-on-error: true' in run1)

wd = (ROOT / '.github/scripts/kpc_watchdog.py').read_text()
check("watchdog does not restart waiting-room as mode=release-approved",
      "'kpc-waiting-room.yml': {'mode': 'release-approved'}" not in wd
      and "'kpc-waiting-room.yml': {'mode': 'check'}" in wd)

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
