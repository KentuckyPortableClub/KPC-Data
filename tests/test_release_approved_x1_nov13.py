#!/usr/bin/env python3
"""Quality X1 (regrade Nov 13): release-approved is owner-dispatch only (github.actor /
KPC_RELEASE_ACTORS / GITHUB_REPOSITORY_OWNER). Item text such as 'by: chat 11' does not
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

# owner_dispatch_ok
saved = {k: os.environ.pop(k) for k in list(os.environ) if k in ('GITHUB_EVENT_NAME', 'GITHUB_ACTOR', 'GITHUB_REPOSITORY_OWNER', 'KPC_RELEASE_ACTORS')}
try:
    ok1, why1 = RA.owner_dispatch_ok()
    check('no actor / no event is refused', (not ok1) and 'KPC_RELEASE_ACTORS' in why1)
    os.environ['GITHUB_EVENT_NAME'] = 'schedule'
    os.environ['GITHUB_ACTOR'] = 'KZ4CP'
    os.environ['GITHUB_REPOSITORY_OWNER'] = 'KZ4CP'
    ok2, why2 = RA.owner_dispatch_ok()
    check('a schedule run is refused even if the actor is the owner', (not ok2) and 'owner-dispatch' in why2)
    os.environ['GITHUB_EVENT_NAME'] = 'workflow_dispatch'
    os.environ['GITHUB_ACTOR'] = 'kpc-bot'
    os.environ['GITHUB_REPOSITORY_OWNER'] = 'KentuckyPortableClub'
    os.environ['KPC_RELEASE_ACTORS'] = 'KZ4CP'
    ok3, why3 = RA.owner_dispatch_ok()
    check('a bot actor not in KPC_RELEASE_ACTORS is refused', (not ok3) and 'kpc-bot' in why3)
    os.environ['GITHUB_ACTOR'] = 'KZ4CP'
    ok4, why4 = RA.owner_dispatch_ok()
    check('workflow_dispatch by an actor in KPC_RELEASE_ACTORS is allowed', ok4)
    del os.environ['KPC_RELEASE_ACTORS']
    os.environ['GITHUB_REPOSITORY_OWNER'] = 'KZ4CP'
    ok5, _ = RA.owner_dispatch_ok()
    check('workflow_dispatch by GITHUB_REPOSITORY_OWNER is allowed', ok5)
finally:
    for k in ('GITHUB_EVENT_NAME', 'GITHUB_ACTOR', 'GITHUB_REPOSITORY_OWNER', 'KPC_RELEASE_ACTORS'):
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
      and 'KPC_RELEASE_ACTORS' in body)
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
