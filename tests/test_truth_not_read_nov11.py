#!/usr/bin/env python3
"""Nov 11 (data-quality review): the park truth checker said 'no size on page' for a park whose agency pages could not be opened at all
(403, robots.txt, host resting). That reads as 'the agency publishes no number'. When no page was read the verdict is 'not read' and the
cause lists the statuses. A page that WAS read and holds no number is still 'no size on page'. Offline: read_page is a stub."""
import os, pathlib, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
os.environ['OUT'] = tempfile.mkdtemp(prefix='kpc-truth-nr-')
sys.path.insert(0, str(ROOT / '.github' / 'scripts'))
import kpc_truth_bot as T   # noqa: E402

ok = True


def check(cond, msg):
    global ok
    print(('PASS ' if cond else 'FAIL ') + msg)
    ok = ok and bool(cond)


PARK = {'n': 'Pine Mountain State Park', 't': 'State Park'}
OURS = {'acres': 1000, 'pin': 'inside', 'pieces': [], 'src': 'fixture', 'manager': ''}
URLS = [('https://parks.example.test/pine', "the park's page", False), ('https://parks.example.test/pine/about', 'about page', False)]
T.candidate_pages = lambda ref, park, web, docs, ky: list(URLS)


def run(pages):
    T.read_page = lambda u: pages[u]
    return T.one_park("US-0001", PARK, OURS, {}, {}, {}, {}, None)


blocked = run({URLS[0][0]: ('HTTP 403', '', ''), URLS[1][0]: ('robots.txt says no', '', '')})
check(blocked['verdict'] == 'not read', f"every page blocked: verdict is 'not read' ({blocked['verdict']})")
check('HTTP 403' in blocked.get('cause', '') and 'robots.txt says no' in blocked['cause'], f"the cause names the statuses ({blocked.get('cause')})")
check(blocked['official'] is None and blocked['pct'] is None, 'no agency number is invented')
check([p['status'] for p in blocked['pages']] == ['HTTP 403', 'robots.txt says no'], 'every try is listed with its status')

page = 'Pine Mountain State Park is a lovely place with trails and a lodge. ' * 10
empty = run({URLS[0][0]: ('ok', 'page', page), URLS[1][0]: ('HTTP 404', '', '')})
check(empty['verdict'] == 'no size on page', f"a page that was read and holds no number: still 'no size on page' ({empty['verdict']})")

sized = run({URLS[0][0]: ('ok', 'page', 'Pine Mountain State Park encompasses 1,020 acres of ridge land. ' * 3), URLS[1][0]: ('HTTP 403', '', '')})
check(sized['verdict'] == 'agree', f"one readable page with a matching size: 'agree' ({sized['verdict']})")

soft = run({URLS[0][0]: ('soft 404', 'page', ''), URLS[1][0]: ('host resting', '', '')})
check(soft['verdict'] == 'not read', f"soft 404 + resting host: 'not read' ({soft['verdict']})")

D = {'parks': {'a': blocked, 'b': empty, 'c': sized}}
c = T.counts(D)
check(c['not_read'] == 1 and c['no_size'] == 1 and c['agree'] == 1, f"counts keep the three apart ({ {k: c[k] for k in ('not_read', 'no_size', 'agree')} })")

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
