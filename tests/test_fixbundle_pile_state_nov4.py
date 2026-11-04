#!/usr/bin/env python3
"""Offline test, Nov 4 PM fix bundle item 8 (Brandon's yes relayed via Super Head Bot, 4:53 PM CST Nov 4):
data/pile-solver/state.json exists with auto=false; an automatic (B3-follow) run ends at once; nothing in the repo sets auto=true
(Brandon turns it on by hand after he checks the first full run). Needs LINKS (a KPC-Links checkout) for the solver import."""
import json, os, pathlib, re, sys
HERE = pathlib.Path(__file__).resolve().parent.parent
os.chdir(HERE)
sys.path.insert(0, '.github/scripts')
ok = True
def check(c, msg):
    global ok
    print(('PASS ' if c else 'FAIL ') + msg); ok = ok and bool(c)
st = json.load(open('data/pile-solver/state.json', encoding='utf-8'))
check(st.get('auto') is False and st.get('refs') == {} and st.get('version') == '1', 'state.json: auto=false, nothing solved yet, version 1')
import kpc_pile_solver as S   # noqa: E402
rows, stats, _ = S.run(HERE, [], None, mode='auto')
check(stats == {'skipped': 'auto off'}, f'an automatic run ends at once: {stats}')
setters = [f'{p}:{i}' for p in list(pathlib.Path('.github').rglob('*.py')) + list(pathlib.Path('.github/workflows').glob('*.yml'))
           for i, l in enumerate(p.read_text(encoding='utf-8', errors='replace').split('\n'), 1)
           if re.search(r"""\[['"]auto['"]\]\s*=\s*True|"auto"\s*:\s*true|'auto':\s*True""", l) and 'pile-solver' in p.read_text(encoding='utf-8', errors='replace')
           and not l.lstrip().startswith('#')]
check(setters == [], f'nothing in the repo sets auto=true: {setters}')
wf = open('.github/workflows/kpc-pile-solver.yml', encoding='utf-8').read()
check(".get('auto') is True" in wf, 'the workflow gate needs auto to be exactly true')
print('ALL PASS' if ok else 'SOME FAILED'); sys.exit(0 if ok else 1)
