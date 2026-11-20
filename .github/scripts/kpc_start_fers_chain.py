#!/usr/bin/env python3
"""Start kpc-fers-chain.yml after a site-data copy.

If that workflow is disabled (the owner turned the 2-fer chain off), this is a notice
and a successful exit: the copy itself is already saved. Never re-enables the chain.
Any other dispatch failure is still an error.

KPC owner, Nov 20 2026
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys


WORKFLOW = 'kpc-fers-chain.yml'


def start(repo: str, ref: str = 'main', gh=None, env=None) -> tuple[int, str]:
    """Return (exit_code, message). 0 = started, or the chain is disabled as the owner required."""
    cmd = list(gh or ['gh']) + [
        'api', '-X', 'POST', f'repos/{repo}/actions/workflows/{WORKFLOW}/dispatches',
        '-f', f'ref={ref}',
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, env=env or os.environ)
    err = ((r.stderr or '') + (r.stdout or '')).strip()
    low = err.lower()
    if r.returncode == 0:
        return 0, 'started after this copy'
    if 'disabled workflow' in low or ('cannot trigger a workflow_dispatch on a disabled workflow' in low):
        return 0, ('not started: the 2-fer chain workflow is disabled (the owner turned it off); '
                   'the copy itself is saved')
    return 1, f'could not start the 2-fer chain (exit {r.returncode}); start {WORKFLOW} by hand' + (f': {err[:200]}' if err else '')


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--repo', default=os.environ.get('GITHUB_REPOSITORY') or '', help='owner/name')
    p.add_argument('--ref', default='main')
    a = p.parse_args(argv)
    if not a.repo:
        print('::error title=2-fer chain::no repo given (GITHUB_REPOSITORY or --repo)')
        return 1
    rc, msg = start(a.repo, a.ref)
    kind = 'notice' if rc == 0 else 'error'
    print(f'::{{kind}} title=2-fer chain::{msg}'.format(kind=kind))
    return rc


if __name__ == '__main__':
    sys.exit(main())
