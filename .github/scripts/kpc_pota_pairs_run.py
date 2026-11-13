#!/usr/bin/env python3
"""Nov 13 (KPC owner): run the POTA-pairs check so Canada is not reported as '0' when there is no CA-XX.json.

For each state in STATES: use data/parkinfo/<ST>.json when it is there; for a CA-XX area, fall back to
data/parkinfo/CA.json filtered to the parks of that province (from data/ca-key/CA-XX.json). If neither
list can be read, print 'not checked' and write a marker file — never a skip that looks like 'POTA pairs
not confirmed 0'. Then, when a list exists, write a temporary parkinfo/<ST>.json if needed and run the
KPC-Links kpc_pota_pairs.py already on the path.

  STATES='CA-AB CA-SK' python3 kpc_pota_pairs_run.py
  LINKS=links (the KPC-Links tree that has kpc_pota_pairs.py). Parkinfo and keys are read from the cwd
  (the overlaid line job) or from DATA= when set.
"""
import json, os, pathlib, shutil, subprocess, sys, tempfile

STATES = (os.environ.get('STATES') or 'US-KY').upper().replace(',', ' ').split()
HERE = pathlib.Path(os.environ.get('DATA') or '.').resolve()
LINKS = pathlib.Path(os.environ.get('LINKS') or '.').resolve()
SCRIPT = LINKS / '.github/scripts/kpc_pota_pairs.py'
OUT = pathlib.Path('data/fers')


def parks_of(path):
    try:
        d = json.loads(pathlib.Path(path).read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return None
    p = d.get('parks') if isinstance(d, dict) else None
    if isinstance(p, dict): return list(p)
    if isinstance(p, list): return list(p)
    return None


def resolve(st):
    """(refs, how) or (None, 'not checked')."""
    direct = pathlib.Path(f'data/parkinfo/{st}.json')
    if not direct.is_file() and HERE != pathlib.Path('.').resolve():
        direct = HERE / 'data/parkinfo' / f'{st}.json'
    refs = parks_of(direct) if direct.is_file() else None
    if refs: return refs, str(direct)
    if st.startswith('CA-'):
        ca = pathlib.Path('data/parkinfo/CA.json')
        if not ca.is_file():
            ca = HERE / 'data/parkinfo/CA.json'
        key = pathlib.Path(f'data/ca-key/{st}.json')
        if not key.is_file():
            key = HERE / 'data/ca-key' / f'{st}.json'
        all_refs = parks_of(ca) if ca.is_file() else None
        key_refs = parks_of(key) if key.is_file() else None
        if all_refs and key_refs:
            hit = [r for r in all_refs if r in set(key_refs)]
            return (hit or list(key_refs)), f'{ca} filtered by {key}'
        if key_refs:
            return list(key_refs), str(key)
        if all_refs:
            # no province filter: do not invent a 5,901-park request; report not checked
            return None, 'not checked'
    return None, 'not checked'


def write_marker(st, why):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f'pota-pairs-{st}.json').write_text(json.dumps({
        'about': 'POTA pairs were not checked for this area.',
        'not_checked': True,
        'why': why,
        'made': '',
        'parks_read': None,
        'complete': False,
        'pairs': {},
        'same_session': [],
    }, indent=0) + '\n')


def main():
    checked, skipped = [], []
    tmp_dir = None
    env_states = []
    try:
        for st in STATES:
            st = st if '-' in st else 'US-' + st
            refs, how = resolve(st)
            if refs is None:
                print(f'::notice title=POTA pairs::{st}: not checked (no park list)', flush=True)
                write_marker(st, how)
                skipped.append(st)
                continue
            dest = pathlib.Path(f'data/parkinfo/{st}.json')
            if not dest.is_file():
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(json.dumps({'parks': {r: {} for r in refs}}, indent=0) + '\n')
                dest_tmp = dest  # leave it for the Links script; the line job does not commit parkinfo
            env_states.append(st)
            checked.append(f'{st} ({how})')
        if not env_states:
            print('::notice title=POTA pairs::no area had a park list: not checked (never 0)', flush=True)
            return 0
        if not SCRIPT.is_file():
            print(f'::notice title=POTA pairs::KPC-Links kpc_pota_pairs.py is not at {SCRIPT}: not checked', flush=True)
            for st in env_states: write_marker(st, 'no kpc_pota_pairs.py')
            return 0
        env = dict(os.environ, STATES=' '.join(env_states))
        r = subprocess.run([sys.executable, str(SCRIPT)], env=env)
        return r.returncode
    finally:
        pass


if __name__ == '__main__':
    sys.exit(main())
