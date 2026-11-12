"""Shared by the pile-solver tests (Nov 11): find the KPC-Links checkout they import scripts from, wherever the test is started.

The solver imports kpc_key_rules / kpc_precheck from a KPC-Links checkout. The tests used to default to a scratch folder that only one
machine had (/tmp/kpc-links, /tmp/fers/L), so on any other machine they died with 'No module named kpc_key_rules'. Order tried: the LINKS
environment variable, the folder next to this repo (../links, ../KPC-Links), then the two old scratch folders. The first one that holds
.github/scripts/kpc_key_rules.py wins and is put in LINKS as an absolute path (so the folder the test is started from does not matter).
No checkout anywhere = one plain FAIL line and exit 1 (a test that cannot run must not pass). No network; no module beyond the standard library."""
import os, pathlib, sys

NEEDS = '.github/scripts/kpc_key_rules.py'


def find(root):
    root = pathlib.Path(root)
    for c in (os.environ.get('LINKS'), root.parent / 'links', root.parent / 'KPC-Links', '/tmp/kpc-links', '/tmp/fers/L'):
        if c and (pathlib.Path(c) / NEEDS).is_file():
            return str(pathlib.Path(c).resolve())
    return None


def use(root):
    p = find(root)
    if not p:
        print('FAIL no KPC-Links checkout found (set LINKS=<folder>, or clone it next to this repo as ../links): the pile solver imports its key rules')
        sys.exit(1)
    os.environ['LINKS'] = p
    return p
