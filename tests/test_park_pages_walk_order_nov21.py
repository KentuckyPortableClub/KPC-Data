#!/usr/bin/env python3
"""Park page reader, 21 Nov 2026: the walk picks the next state from the coverage ranking (biggest agencies first), one
area per run, and still skips a state cut off twice. Offline, invented rows. Prints PASS / FAIL and ends ALL PASS or SOME FAILED.
"""
import csv, json, os, pathlib, re, socket, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github/scripts'))
socket.socket.connect = lambda *a, **k: (_ for _ in ()).throw(OSError('test: no network'))
os.environ['KPC_NO_NET'] = '1'
import kpc_park_pages as PP  # noqa: E402

ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


with tempfile.TemporaryDirectory() as t:
    cp = os.path.join(t, 'coverage.csv')
    with open(cp, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['area', 'agency_web_domain', 'pota_parks', 'main_designations', 'example_park_page'])
        w.writerow(['US-YY', '(no web link)', '900', 'State Forest 900', ''])
        w.writerow(['US-ZZ', 'zz.invented.example.gov', '300', 'State Park 300', 'https://zz.invented.example.gov/p'])
        w.writerow(['US-XX', 'xx.invented.example.gov', '500', 'State Park 500', 'https://xx.invented.example.gov/p'])
        w.writerow(['US-ZZ', 'nps.gov', '20', 'National Park 20', ''])
        w.writerow(['US-WW', '(no web link)', '40', 'State Park 40', ''])
    doc = PP.coverage_order(cp)
    check('areas rank by their biggest agency with a web link, then the no-link areas biggest first',
          doc['areas'] == ['US-XX', 'US-ZZ', 'US-YY', 'US-WW'] and doc['ranked_by_agency'] == 2)
    check('the order file holds counts and web domains only', not re.search(r'US-\d{4}', json.dumps(doc))
          and doc['top_agencies']['US-ZZ'][0] == ['zz.invented.example.gov', 300])
    op = os.path.join(t, 'order.json')
    json.dump(doc, open(op, 'w'))
    rank = PP.walk_rank(op)
    areas = ['US-WW', 'US-XX', 'US-YY', 'US-ZZ', 'US-AA']
    out, why, _st = PP.pick_walk_area(areas, set(), {}, {}, rank=rank)
    check('the next state is the top of the ranking', out == 'US-XX' and 'coverage ranking' in why)
    out, why, _st = PP.pick_walk_area(areas, {'US-XX'}, {}, {}, rank=rank)
    check('a state that already has facts is passed over for the next in rank', out == 'US-ZZ')
    out, _w, _st = PP.pick_walk_area(areas, {'US-XX', 'US-ZZ', 'US-YY', 'US-WW'}, {}, {}, rank=rank)
    check('a state the ranking does not name still comes, after it', out == 'US-AA')
    st = {'left': ['US-9101'], 'run': 'in-progress', 'cutoff': {'US-XX': 1}}
    out, why, st2 = PP.pick_walk_area(areas, set(), st, {'US-XX': {'US-9101'}}, rank=rank)
    check('a state cut off twice is skipped and named for a person, even when it ranks first',
          out == 'US-ZZ' and 'skipped after two cut-off runs' in why and 'US-XX' in st2.get('stuck', []))
    out, _w, _st = PP.pick_walk_area(areas, set(), {}, {})
    check('with no ranking the walk keeps its old order', out == 'US-WW')
    check('a missing order file gives no ranking (old order)', PP.walk_rank(os.path.join(t, 'none.json')) == [])

shipped = PP.walk_rank()
check('the shipped order file ranks the coverage areas', len(shipped) >= 50 and shipped[0].startswith(('US-', 'CA-')))
wf = (ROOT / '.github/workflows/kpc-park-pages.yml').read_text(encoding='utf-8')
check('the walk step passes the ranking', 'rank=PP.walk_rank()' in wf)
check('the workflow still adds no timer and keeps its one schedule', wf.count('cron:') == 1)

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
