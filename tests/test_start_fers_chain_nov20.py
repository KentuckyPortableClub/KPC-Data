#!/usr/bin/env python3
"""Nov 20: starting the 2-fer chain after a site-data copy does not fail when that workflow is disabled."""
import os, pathlib, stat, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github' / 'scripts'))
import kpc_start_fers_chain as S  # noqa: E402

FAILS = []


def check(ok, what):
    print(('PASS ' if ok else 'FAIL ') + what, flush=True)
    if not ok:
        FAILS.append(what)


def fake_gh(td, script):
    p = pathlib.Path(td) / 'gh'
    p.write_text('#!/bin/sh\n' + script, encoding='utf-8')
    p.chmod(p.stat().st_mode | stat.S_IEXEC)
    return [str(p)]


with tempfile.TemporaryDirectory() as td:
    gh = fake_gh(td, 'exit 0\n')
    rc, msg = S.start('KentuckyPortableClub/KPC-Data', gh=gh)
    check(rc == 0 and 'started' in msg, 'a successful dispatch is started')

    gh = fake_gh(td, 'echo \'{"message":"Cannot trigger a workflow_dispatch on a disabled workflow","documentation_url":"https://docs.github.com","status":"422"}\' >&2\nexit 1\n')
    rc, msg = S.start('KentuckyPortableClub/KPC-Data', gh=gh)
    check(rc == 0 and 'disabled' in msg and 'owner turned it off' in msg,
          'a 422 disabled workflow is a notice and a successful exit (the copy is already saved)')

    gh = fake_gh(td, 'echo "HTTP 403 forbidden" >&2\nexit 1\n')
    rc, msg = S.start('KentuckyPortableClub/KPC-Data', gh=gh)
    check(rc == 1 and 'could not start' in msg, 'any other dispatch failure is still an error')

# the workflow calls the script and does not re-enable the chain
wf = (ROOT / '.github' / 'workflows' / 'kpc-copy-from-links.yml').read_text(encoding='utf-8')
check('kpc_start_fers_chain.py' in wf, 'kpc-copy-from-links.yml runs kpc_start_fers_chain.py')
check('enabled: true' not in wf and 'kpc-fers-chain.yml' in wf,
      'the copy workflow never re-enables the 2-fer chain')

print('ALL PASS' if not FAILS else 'SOME FAILED')
sys.exit(1 if FAILS else 0)
