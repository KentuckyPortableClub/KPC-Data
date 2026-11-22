#!/usr/bin/env python3
"""Page reader work order, 21 Nov 2026: a PRIVATE priority list (the likely mismatches) first, parks confirmed by their agency id
last with a yearly re-read, and a private list is never read from inside a repository. Invented parks only.
Prints PASS / FAIL lines and ends ALL PASS or SOME FAILED."""
import json, pathlib, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github/scripts'))
import kpc_park_pages_work as W  # noqa: E402

ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


areas = {'US-ZZ': {r: {'website': f'https://parks.invented.example/{r}', 'qsos': q} for r, q in
                   (('US-9001', 5), ('US-9002', 50), ('US-9003', 1), ('US-9004', 9), ('US-9005', 2))}}
choose = lambda ref, row: row['website']
today = '2026-11-21'
order = W.build_worklist(areas, choose, {}, [], [], {}, today, priority=['US-9003'], confirmed=['US-9002'])
refs = [o['ref'] for o in order]
check('the priority park is read first', refs[0] == 'US-9003' and order[0]['tier'] == 0)
check('its public reason only says "priority list"', order[0]['why'] == 'priority list')
check('a confirmed park never read before comes last', refs[-1] == 'US-9002' and order[-1]['tier'] == 6)
check('the busiest unconfirmed park leads the ordinary tiers', refs[1] == 'US-9004')
state = {'read': {'US-9002': {'date': '2026-06-01'}, 'US-9001': {'date': '2026-09-01'}}}
order = W.build_worklist(areas, choose, {}, [], [], state, today, confirmed=['US-9002'])
check('a confirmed park read under a year ago is not read again', 'US-9002' not in [o['ref'] for o in order])
check('an unconfirmed park read 81 days ago is re-read as before', 'US-9001' in [o['ref'] for o in order])
state = {'read': {'US-9002': {'date': '2025-11-01'}}}
order = W.build_worklist(areas, choose, {}, [], [], state, today, confirmed=['US-9002'])
check('a confirmed park read over a year ago gets its yearly re-read, last', order[-1]['ref'] == 'US-9002' and order[-1]['tier'] == 6)
ns = [{'ref': 'US-9002', 'status': 'open', 'wants': ['page facts'], 'how_sure': 'unsure', 'why': 'two records'}]
order = W.build_worklist(areas, choose, {}, [], [], {}, today, not_sure=ns, confirmed=['US-9002'])
check('a not-sure row on a confirmed park still wins', order[0]['ref'] == 'US-9002' and order[0]['tier'] == 0)
order = W.build_worklist(areas, choose, {}, [], [], {}, today)
check('no lists given: the order is as before (no tier 6)', all(o['tier'] != 6 for o in order) and len(order) == 5)

with tempfile.TemporaryDirectory() as t:
    t = pathlib.Path(t)
    (t / 'mis.csv').write_text('park,area,name\nUS-9003,US-ZZ,x\nUS-9003,US-ZZ,x\nUS-9005,US-ZZ,y\n', encoding='utf-8')
    check('a private CSV gives its park column once each', W.private_refs(str(t / 'mis.csv')) == ['US-9003', 'US-9005'])
    (t / 'c.json').write_text(json.dumps({'parks': ['US-9002']}), encoding='utf-8')
    check('a private JSON list is read', W.private_refs(str(t / 'c.json')) == ['US-9002'])
    repo = t / 'repo'
    (repo / '.git').mkdir(parents=True)
    (repo / 'data').mkdir()
    (repo / 'data' / 'mis.csv').write_text('park\nUS-9003\n', encoding='utf-8')
    try:
        W.private_refs(str(repo / 'data' / 'mis.csv')); refused = False
    except W.PrivateFileError:
        refused = True
    check('a park list inside a git repository is refused', refused)
    try:
        W.private_refs(str(t / 'mis.csv'), repo_root=str(t)); refused = False
    except W.PrivateFileError:
        refused = True
    check('a park list inside the given repo root is refused', refused)
    check('no file given: no parks', W.private_refs('') == [])

order = W.build_worklist(areas, choose, {}, [], [], {}, today, priority=['US-9003'], confirmed=['US-9002'])
pub = W.public_order(order, today)
check('the public worklist names no park from the private lists', not any(o['ref'] in ('US-9003', 'US-9002') for o in pub['order']))
check('the public worklist counts them', pub['private_list_parks'] == {'priority list': 1, 'confirmed by id': 1})
with tempfile.TemporaryDirectory() as t:
    t = pathlib.Path(t)
    data = t / 'data' / 'parkinfo'; data.mkdir(parents=True)
    (data / 'US-ZZ.json').write_text(json.dumps({'parks': {r: {'name': r, 'website': f'https://parks.invented.example/{r}'} for r in
                                                       ('US-9003', 'US-9004')}}), encoding='utf-8')
    (t / 'pri.csv').write_text('park\nUS-9003\n', encoding='utf-8')
    r = subprocess.run([sys.executable, '-B', str(ROOT / '.github/scripts/kpc_park_pages.py'), 'worklist', '--data', str(t / 'data'),
                        '--out', str(t / 'out'), '--priority-file', str(t / 'pri.csv'), '--quiet'], capture_output=True, text=True)
    wl = t / 'out' / 'worklist.json'
    check('the worklist command writes a public worklist with no private park in it',
          r.returncode == 0 and wl.is_file() and 'US-9003' not in wl.read_text() and 'US-9004' in wl.read_text()
          and json.loads(wl.read_text())['private_list_parks'] == {'priority list': 1})
r = subprocess.run([sys.executable, '-B', str(ROOT / '.github/scripts/kpc_park_pages.py'), '--help'], capture_output=True, text=True)
check('the reader takes --priority-file and --confirmed-file', '--priority-file' in r.stdout and '--confirmed-file' in r.stdout)
r = subprocess.run([sys.executable, '-B', str(ROOT / '.github/scripts/kpc_park_pages.py'), '--selftest'], capture_output=True, text=True)
check('the page reader self-test still passes', r.returncode == 0)
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
