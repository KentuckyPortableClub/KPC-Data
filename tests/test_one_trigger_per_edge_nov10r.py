"""Owner rule, 2026-11-10: a workflow never has both a workflow_run trigger and an upstream dispatch for the same edge (one start
per upstream run). No network. Run: python3 -B tests/test_one_trigger_per_edge_nov10r.py"""
import pathlib, re, sys
import yaml
W = pathlib.Path(__file__).resolve().parents[1] / '.github/workflows'
ok = True
def check(c, m):
    global ok
    print(('ok   ' if c else 'FAIL ') + m); ok = ok and bool(c)
docs = {}
for f in sorted(W.glob('*.yml')):
    t = f.read_text(encoding='utf-8'); y = yaml.safe_load(t); docs[f.name] = (t, y, y.get('on') or y.get(True) or {})
name_to_file = {y.get('name'): n for n, (t, y, o) in docs.items()}
dispatches = {}   # target -> set of upstream files that dispatch it
for n, (t, y, o) in docs.items():
    for a, b in re.findall(r'workflows/(kpc-[a-z0-9-]+\.yml)/dispatches|gh workflow run "?(kpc-[a-z0-9-]+\.yml)', t):
        dispatches.setdefault(a or b, set()).add(n)
bad = []
for n, (t, y, o) in docs.items():
    for up in (o.get('workflow_run') or {}).get('workflows') or []:
        uf = name_to_file.get(up)
        if uf and uf in dispatches.get(n, set()): bad.append((n, uf))
check(not bad, f'no workflow has both a workflow_run trigger and a dispatch from the same upstream ({bad})')
for n in ('kpc-fers-chain.yml',):
    check('workflow_run' not in docs[n][2], f'{n}: dispatch only')
pl = docs['kpc-fers-postline.yml'][2]
check(docs['kpc-fers-chain.yml'][1]['name'] not in (pl.get('workflow_run') or {}).get('workflows', []), 'kpc-fers-postline.yml does not listen to the chain (the chain dispatches it)')
print('ALL PASS' if ok else 'SOME FAILED'); sys.exit(0 if ok else 1)
