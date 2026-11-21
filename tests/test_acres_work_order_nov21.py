#!/usr/bin/env python3
"""The acreage bot's work order, 21 Nov 2026: within each region, the lists of the areas with the most likely-mismatch parks
come first, then the areas with the most parks NOT yet confirmed by their agency id. Both lists are PRIVATE files outside any
git repository (a file inside one is refused). An --areas list a person gives keeps its order. Offline, invented parks."""
import json, pathlib, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
D = ROOT / '.github/scripts/draft/tools/kpc_acres'
sys.path.insert(0, str(D))
import kpc_acres as A  # noqa: E402

ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


cfgs = [{'agency': f'Invented Agency {a}', 'area': a, 'url': f'https://lists.invented.example/{a}.csv'} for a in ('US-KS', 'US-NE', 'US-TX', 'CA-ON')]
areas = ['US-KS', 'US-NE', 'US-TX', 'CA-ON']
plain = [it['area'] for it in A.build_queue(cfgs, [], areas)]
check('no private lists: the order is as before', plain == ['US-KS', 'US-NE', 'US-TX', 'CA-ON'])
w = {'US-TX': (5, 100), 'US-NE': (0, 300), 'US-KS': (0, 10), 'CA-ON': (9, 50)}
got = [it['area'] for it in A.build_queue(cfgs, [], areas, weights=w)]
check('the area with the most likely mismatches goes first, then the most unconfirmed parks', got[:3] == ['US-TX', 'US-NE', 'US-KS'])
check('Canada still follows the US (the region order wins)', got[3] == 'CA-ON')
got = [it['area'] for it in A.build_queue(cfgs, [], areas, weights=w, explicit=True)]
check('an --areas list given by a person keeps its own order', got == ['US-KS', 'US-NE', 'US-TX', 'CA-ON'])


class P:
    p = {'US-9001': {'area': 'US-TX'}, 'US-9002': {'area': 'US-TX'}, 'US-9003': {'area': 'US-NE'}, 'US-9004': {'area': 'US-NE'}}


wt = A.area_weights(P(), [('US-9001', ''), ('US-9003', 'US-NE')], [('US-9002', ''), ('US-9004', '')])
check('weights count mismatches and unconfirmed parks per area', wt['US-TX'] == (1, 1) and wt['US-NE'] == (1, 1))
with tempfile.TemporaryDirectory() as t:
    t = pathlib.Path(t)
    (t / 'm.csv').write_text('park,area,name\nUS-9001,US-TX,x\nUS-9001,US-TX,x\nUS-9003,,y\n', encoding='utf-8')
    check('a private CSV gives each park once, with its area when given', A.private_park_rows(str(t / 'm.csv')) == [('US-9001', 'US-TX'), ('US-9003', '')])
    (t / 'c.json').write_text(json.dumps(['US-9002']), encoding='utf-8')
    check('a private JSON list is read', A.private_park_rows(str(t / 'c.json')) == [('US-9002', '')])
    (t / 'repo' / '.git').mkdir(parents=True)
    (t / 'repo' / 'm.csv').write_text('park\nUS-9001\n', encoding='utf-8')
    try:
        A.private_park_rows(str(t / 'repo' / 'm.csv')); refused = False
    except A.PrivateFileError:
        refused = True
    check('a park list inside a git repository is refused', refused)
    check('no file: no rows', A.private_park_rows('') == [])
r = subprocess.run([sys.executable, '-B', str(D / 'kpc_acres.py'), '--help'], capture_output=True, text=True)
check('the bot takes --priority-file and --confirmed-file', '--priority-file' in r.stdout and '--confirmed-file' in r.stdout)
r = subprocess.run([sys.executable, '-B', str(D / 'kpc_acres.py'), '--selftest'], capture_output=True, text=True, cwd=str(D))
check('the acreage bot self-test still passes', r.returncode == 0)
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
