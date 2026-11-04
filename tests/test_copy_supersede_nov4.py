#!/usr/bin/env python3
"""Offline test for data-03 (Nov 4; per Brandon via Super Head Bot (relayed), 4:51 AM CST Nov 4): kpc-copy-from-links.yml's held-key step lets a NEW
key build replace a held build that KPC-Links' kpc_key_freeze.not_blocking() calls superseded (other rules / no rules hash / too
old), overwrites the held files (deletes nothing), and keeps the old behaviour otherwise. The step's own Python is cut out of the
workflow and run in a temp git repo. Uses a stub kpc_key_freeze.py; with LINKS=<KPC-Links checkout> (links-04 applied) it runs
the real one too. No network."""
import json, os, pathlib, re, shutil, subprocess, sys, tempfile

HERE = pathlib.Path(__file__).resolve().parent.parent
wf = (HERE / '.github/workflows/kpc-copy-from-links.yml').read_text()
m = re.search(r"KD=\$\(cd kpcdata && python3 - <<'PY'\n(.*?)\n\s*PY\n\s*\)", wf, re.S)
CODE = '\n'.join(l[10:] for l in m.group(1).split('\n'))
ok = True


def check(c, msg):
    global ok
    print(('PASS ' if c else 'FAIL ') + msg); ok = ok and bool(c)


STUB = '''
def not_blocking(stamp, kind, now=None, rules=None):
    r = str((stamp or {}).get('rules') or '')
    return '' if r == 'CURRENT' else ('no rules hash: superseded' if not r else 'other rules: superseded')
'''


def setup(t, held_index, freeze=STUB, approved=None):
    D, L = pathlib.Path(t) / 'kpcdata', pathlib.Path(t) / 'links'
    for d in (D / 'data/us-key', D / 'data/waiting/in/data/us-key', L / 'data/us-key', L / '.github/scripts'): d.mkdir(parents=True, exist_ok=True)
    w = lambda p, o: open(p, 'w').write(json.dumps(o))
    w(D / 'data/us-key/US-TN.json', {'parks': {'US-1': 'live'}}); w(D / 'data/us-key/index.json', {'build': 'US-live'})
    w(D / 'data/waiting/in/data/us-key/US-TN.json', {'parks': {'US-1': 'old held'}}); w(D / 'data/waiting/in/data/us-key/US-OH.json', {'parks': {'US-2': 'old held'}})
    w(D / 'data/waiting/in/data/us-key/US-AK.json', {'parks': {'US-3': 'old held, not in the new build'}})
    w(D / 'data/waiting/in/data/us-key/index.json', held_index); w(D / 'data/waiting/approved.json', approved or {'items': []})
    w(L / 'data/us-key/US-TN.json', {'parks': {'US-1': 'new build'}}); w(L / 'data/us-key/US-OH.json', {'parks': {'US-2': 'new build'}})
    w(L / 'data/us-key/index.json', {'build': 'US-new', 'rules': 'CURRENT'})
    if freeze is not None: open(L / '.github/scripts/kpc_key_freeze.py', 'w').write(freeze)
    # key-files-seen.json: the Links files as they were BEFORE this build (so US-TN / US-OH count as changed by a build)
    w(D / 'data/waiting/key-files-seen.json', {'data/us-key/US-TN.json': 'x', 'data/us-key/US-OH.json': 'y'})
    subprocess.run('git init -q && git add -A && git -c user.name=t -c user.email=t@t commit -qm base', shell=True, cwd=D, check=True)
    # the workflow rsyncs the Links key over KPC-Data's copy first
    for f in ('US-TN.json', 'US-OH.json', 'index.json'): shutil.copy2(L / 'data/us-key' / f, D / 'data/us-key' / f)
    return D, L


def run(D):
    p = subprocess.run([sys.executable, '-c', CODE], cwd=D, capture_output=True, text=True)
    return p.stdout + p.stderr


held = lambda f, D: json.load(open(D / 'data/waiting/in/data/us-key' / f))['parks']
with tempfile.TemporaryDirectory() as t:
    D, L = setup(t, {'build': 'US-f3d48d30899'})   # the real Nov 4 held build: no rules hash
    out = run(D)
    check('DIRS=data/us-key' in out and 'SUPERSEDED' in out, 'a held build with no rules hash (US-f3d48d30899) is superseded: the new US build comes over (DIRS=data/us-key)')
    check(held('US-TN.json', D) == {'US-1': 'new build'} and held('US-OH.json', D) == {'US-2': 'new build'}, 'its held files are overwritten by the new build (no stale old-rules file left beside the new index)')
    check((D / 'data/waiting/in/data/us-key/US-AK.json').exists() and 'US-AK.json' in out, 'a held file the new build does not have is NOT deleted, and is named for a person')
    rp = D / 'data/status/key-copy/dropped-us-key.json'
    rep = json.load(open(rp)) if rp.exists() else {}
    check(rep.get('count') == 1 and [r['file'] for r in rep.get('files', [])] == ['data/waiting/in/data/us-key/US-AK.json'] and rep.get('old_build') == 'US-f3d48d30899' and rep.get('new_build') == 'US-new',
          f'FINAL-v2: the dropped held file is LISTED in data/status/key-copy/dropped-us-key.json (old / new build named) ({json.dumps(rep)[:120]})')
    md = (D / 'data/status/key-copy/dropped-us-key.md')
    check(md.exists() and 'US-AK.json' in md.read_text() and "Brandon's yes" in md.read_text(), 'FINAL-v2: the same list as a .md for a person; it says nothing is deleted without Brandon\'s yes')
    st = subprocess.run(['git', 'status', '--porcelain'], cwd=D, capture_output=True, text=True).stdout
    check(not re.search(r'^ ?D ', st, re.M), f'nothing in the repo was deleted by the step ({st.strip()[:100]!r})')
with tempfile.TemporaryDirectory() as t:
    D, L = setup(t, {'build': 'US-1001', 'rules': 'CURRENT'})
    out = run(D)
    check('DIRS=' in out and 'data/us-key' not in out.split('DIRS=')[1] and 'not replaced' in out and held('US-TN.json', D) == {'US-1': 'old held'},
          'a held build on the current rules, ungraded: kept, not replaced (Quality grades it first)')
    check(not (D / 'data/status/key-copy').exists(), 'a held build that is kept (not superseded) writes no dropped-files report')
with tempfile.TemporaryDirectory() as t:
    D, L = setup(t, {'build': 'US-f3d48d30899'}, freeze=None)
    out = run(D)
    check('data/us-key' not in out.split('DIRS=')[1] and held('US-TN.json', D) == {'US-1': 'old held'}, 'KPC-Links without links-04 (no kpc_key_freeze.not_blocking): the old behaviour, the held build is kept')
real = os.environ.get('LINKS') and pathlib.Path(os.environ['LINKS']) / '.github/scripts/kpc_key_freeze.py'
if real and real.exists() and 'def not_blocking' in real.read_text():
    with tempfile.TemporaryDirectory() as t:
        D, L = setup(t, {'build': 'US-f3d48d30899'}, freeze=real.read_text())
        out = run(D)
        check('SUPERSEDED' in out and 'DIRS=data/us-key' in out, f'with the REAL KPC-Links kpc_key_freeze.py ({real}): US-f3d48d30899 is superseded')
else: print('SKIP the real KPC-Links kpc_key_freeze.py (set LINKS=<KPC-Links checkout with links-04>)')
print('ALL PASS' if ok else 'SOME FAILED'); sys.exit(0 if ok else 1)
