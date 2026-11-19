#!/usr/bin/env python3
"""Not-sure list (hand-off 05 addendum 1) and the reader's use of it. Offline.
Prints PASS / FAIL lines and ends ALL PASS or SOME FAILED."""
import json, pathlib, socket, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
S = ROOT / '.github/scripts'
SEED = ROOT / 'tests/fixtures/park-pages/not-sure-seed.json'
sys.path.insert(0, str(S))
ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


def _no_net(*a, **k):
    raise OSError('test: no network')


socket.socket.connect = _no_net
import kpc_not_sure as NS  # noqa: E402
import kpc_park_pages_work as W  # noqa: E402

ran = subprocess.run([sys.executable, '-B', str(S / 'kpc_not_sure.py'), '--selftest'], capture_output=True, text=True)
check('the not-sure selftest passes with no network', ran.returncode == 0 and 'SELFTEST PASS' in ran.stdout)
if ran.returncode != 0:
    print(ran.stdout[-800:])
    print(ran.stderr[-400:])

raw = json.loads(SEED.read_text(encoding='utf-8'))
with tempfile.TemporaryDirectory() as td:
    ns = NS.NotSure(td)
    n = ns.import_seed(SEED, today='2026-11-19')
    stored = ns.all_rows()
    by_area = {}
    for row in stored:
        by_area.setdefault(row['area'], []).append(row)
    check(f'the seed loads whole ({n} stored, {len(raw)} in the file)', n == 104 and len(raw) == 104 and len(stored) == 104)
    check('the seed splits by area and none are lost', sum(len(v) for v in by_area.values()) == 104 and len(by_area) >= 2)
    check('a class row is stored and never handed to a bot',
          sum(1 for r in stored if r['ref'] == '(class)') == 4 and all(r['ref'] != '(class)' for r in ns.open_rows()))
    # two fresh folders, opposite add order, same bytes
    a, b = NS.NotSure(td + '/a'), NS.NotSure(td + '/b')
    rows = [
        {'ref': 'US-10', 'area': 'US-KY', 'name': 'Ten', 'code': 'NAME_DIFFERS', 'how_sure': 'unsure',
         'why': 'names', 'wants': ['page facts'], 'found_by': 'test', 'status': 'open'},
        {'ref': 'US-11', 'area': 'US-KY', 'name': 'Eleven', 'code': 'MANY_TRACTS', 'how_sure': 'wrong likely',
         'why': 'tracts', 'wants': ['map'], 'found_by': 'test', 'status': 'open'},
    ]
    for row in rows:
        a.add(row, today='2026-11-19')
    for row in reversed(rows):
        b.add(row, today='2026-11-19')
    check('two writers in either order write the same bytes',
          (a.root / 'US-KY.json').read_bytes() == (b.root / 'US-KY.json').read_bytes())
    a.tried('US-10', 'NAME_DIFFERS', 'park page reader', 'read', 'Page name.', today='2026-11-19')
    a.tried('US-10', 'NAME_DIFFERS', 'park page reader', 'page silent', '', today='2026-11-20')
    kept = next(r for r in a._load_area('US-KY') if r['ref'] == 'US-10')
    check('tried keeps every note', len(kept['tried']) == 2 and kept['tried'][0]['quote'] == 'Page name.')
    a.settle('US-11', 'MANY_TRACTS', 'a reviewer', 'the map named the tracts', '', today='2026-11-20')
    settled = next(r for r in a._load_area('US-KY') if r['ref'] == 'US-11')
    check('settle keeps the row and does not delete it', settled['status'] == 'settled' and settled['why'] == 'tracts')
    lines = ns.summary(today='2026-11-19', qsos={'US-6063': 2540})
    check('the not-sure summary fits on one phone screen', 1 <= len(lines) <= 40 and lines[0].startswith('Not sure list'))
    # the reader notes a question and does not settle
    from kpc_not_sure import note_from_reader
    box = NS.NotSure(td + '/reader')
    box.add({'ref': 'US-6063', 'area': 'US-UT', 'name': 'Red Cliffs', 'code': 'NAME_VS_LINK', 'how_sure': 'wrong likely',
             'why': 'the name and the link differ', 'wants': ['page facts'], 'found_by': 'key run', 'status': 'open'},
            today='2026-11-19')
    fact = {'ref': 'US-6063', 'unchanged': False, 'page': {'kind': 'html', 'final_url': 'https://www.blm.gov/visit/red-cliffs-recreation-area'},
            'asked': {'url': 'https://www.blm.gov/visit/red-cliffs-recreation-area'},
            'pota': {'name': 'Red Cliffs'},
            'questions': [{'code': 'INSIDE_BIGGER_UNIT', 'plain': "The page says this place is within 'Red Cliffs National Conservation Area'.",
                           'quote': 'within the Red Cliffs National Conservation Area'}]}
    note_from_reader(box, {'US-UT': {'US-6063': fact}}, '2026-11-19')
    inside = next(r for r in box.all_rows() if r['code'] == 'INSIDE_BIGGER_UNIT')
    link = next(r for r in box.all_rows() if r['code'] == 'NAME_VS_LINK')
    check('a reader question becomes an open row and the reader does not settle it',
          inside['found_by'] == 'park page reader' and inside['status'] == 'open' and inside['settled']['by'] == '')
    check('the reader leaves a tried note on the open row', any(t['by'] == 'park page reader' for t in link['tried']))
    # the question is gone on the next read
    fact2 = dict(fact)
    fact2['questions'] = []
    note_from_reader(box, {'US-UT': {'US-6063': fact2}}, '2026-11-20')
    inside2 = next(r for r in box.all_rows() if r['code'] == 'INSIDE_BIGGER_UNIT')
    check('a reader row turns gone when its question no longer comes up, and it is not settled',
          inside2['status'] == 'gone' and inside2['settled']['by'] == '')
    # worklist: wrong likely before unsure, and before a list drop
    areas = {'US-UT': {
        'US-1': {'name': 'One', 'website': 'https://www.nps.gov/a', 'type': 'National Park', 'qsos': 10, 'lat': 37, 'lon': -113},
        'US-2': {'name': 'Two', 'website': 'https://www.nps.gov/b', 'type': 'National Park', 'qsos': 99, 'lat': 37, 'lon': -113},
        'US-3': {'name': 'Three', 'website': 'https://www.nps.gov/c', 'type': 'National Park', 'qsos': 1, 'lat': 37, 'lon': -113},
    }}
    doubt = [
        {'ref': 'US-1', 'status': 'open', 'how_sure': 'unsure', 'wants': ['page facts'], 'why': 'unsure one'},
        {'ref': 'US-2', 'status': 'open', 'how_sure': 'wrong likely', 'wants': ['official size'], 'why': 'likely two'},
        {'ref': '(class)', 'status': 'open', 'how_sure': 'wrong likely', 'wants': ['page facts'], 'why': 'a group'},
    ]
    lists = [{'name': 'keeper.json', 'done': False, 'why': 'list', 'parks': [{'ref': 'US-3', 'why': 'on a list'}]}]
    order = W.build_worklist(areas, lambda ref, row: row.get('website'), {}, lists, [], {}, '2026-11-19', not_sure=doubt)
    check('not-sure rows come first, wrong likely before unsure, and a class row is skipped',
          [r['ref'] for r in order[:3]] == ['US-2', 'US-1', 'US-3'] and order[0]['tier'] == 0 and order[2]['tier'] == 1)

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
