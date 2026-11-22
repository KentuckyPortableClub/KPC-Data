#!/usr/bin/env python3
"""Park page reader, 21 Nov 2026: the facts that confirm a park by more than its name, each with a quote or its address, or
silence. Offline, invented parks only. Prints PASS / FAIL lines and ends ALL PASS or SOME FAILED.
"""
import json, os, pathlib, re, socket, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github/scripts'))
socket.socket.connect = lambda *a, **k: (_ for _ in ()).throw(OSError('test: no network'))
os.environ['KPC_NO_NET'] = '1'
import kpc_park_pages as PP  # noqa: E402
import kpc_park_pages_rules as R  # noqa: E402

ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


POTA = {'name': 'Invented Ridge State Forest', 'type': 'State Forest', 'pin': [42.5, -74.5], 'link': '', 'qsos': 1}
LONG = ' The forest has trails, a pond and a lean-to for walkers who come in every season of the year.' * 6


def page(url, text, links=(), kind='html'):
    return {'url': url, 'final': url, 'status': 200, 'kind': kind, 'text': text, 'html': '', 'title': '',
            'heading': 'Invented Ridge State Forest', 'og': '', 'jsonld': '', 'links': list(links), 'fingerprint': 'x',
            'family': R.family_of(url), 'thin': False}


def facts(pages, url, own='own', mates=()):
    return R.build_facts('US-9001', 'US-NY', dict(POTA, link=url), {'US-9001': POTA}, {'url': url, 'from': 'pota'}, pages,
                         '2026-11-21', list(mates), own, 'test')


DEC = 'https://www.dec.ny.gov/lands/9999.html'

# --- the agency park id ---
f = facts([page(DEC, 'Invented Ridge State Forest' + LONG)], DEC)
check('the id comes from the official address (a known agency rule), with the address it came from',
      f['confirm']['agency_id'] == {'kind': 'NY DEC page number', 'value': '9999', 'from': 'address', 'url': DEC})
f = facts([page(DEC, 'Invented Ridge State Forest\nForest ID: 9999\n' + LONG)], DEC)
check('the page saying the same id adds to it ("address and page")', f['confirm']['agency_id'].get('from') == 'address and page')
f = facts([page(DEC, 'Invented Ridge State Forest\nForest ID: 4521\n' + LONG)], DEC)
check('the page stating another id than its address: unclear, no value kept',
      f['confirm']['agency_id'].get('unclear') and 'value' not in f['confirm']['agency_id'])
EX = 'https://parks.invented.example.gov/ridge'
f = facts([page(EX, 'Invented Ridge State Forest\nPark ID: 4521\n' + LONG)], EX)
check('a labelled id line on the page, quoted', f['confirm']['agency_id'] == {'kind': 'page label: park id', 'value': '4521',
                                                                              'from': 'page', 'quote': 'Park ID: 4521'})
f = facts([page(EX, 'Invented Ridge State Forest\nPark ID: 4521\nPark ID: 4522\n' + LONG)], EX)
check('two different labelled ids: unclear, no value', f['confirm']['agency_id'].get('unclear') and 'value' not in f['confirm']['agency_id'])
f = facts([page(EX, 'Invented Ridge State Forest. Call 555 1234 or see trail 42 near site 7.' + LONG)], EX)
check('no rule and no labelled line: silent (no id field is invented)', f['confirm']['agency_id'] is None)
f = facts([page(DEC, 'Invented Ridge State Forest' + LONG)], DEC, own='shared', mates=['US-9002'])
check('an id on a page two parks share is not kept as this park\'s', 'value' not in (f['confirm']['agency_id'] or {}))

# --- the size, with its quote and the page it came from ---
FACTS = 'https://parks.invented.example.gov/ridge/facts'
f = facts([page(EX, 'Invented Ridge State Forest' + LONG),
           page(FACTS, 'Invented Ridge State Forest\nTotal area: 1,234 acres\n' + LONG)], EX)
s = f['confirm']['size'] or {}
check('a clean total size keeps its quote and the page it came from',
      s.get('acres') == 1234 and 'Total area' in s.get('quote', '') and s.get('source_url') == FACTS)
check('every size row names its source page', all(r.get('source_url') for r in f['sizes']))
nosrc = [dict(r, source_url='') for r in f['sizes']]
check('silent when the figure has no source page', R.confirm_size(nosrc) is None)
two = [dict(f['sizes'][0]), dict(f['sizes'][0], acres=2500.0)]
check('two different clean totals: unclear, no size', (R.confirm_size(two) or {}).get('unclear'))
f = facts([page(EX, 'Invented Ridge State Forest covers about 1,200 acres of hills.' + LONG)], EX)
check('a round figure ("about 1,200 acres") is not a confirming size', f['confirm']['size'] is None)

# --- the manager ---
f = facts([page('https://www.nps.gov/zzzz/index.htm', 'Invented Ridge State Forest' + LONG)], 'https://www.nps.gov/zzzz/index.htm')
check("the agency's own host names the manager", (f['confirm']['manager'] or {}).get('agency') == 'National Park Service')
mgr = R.confirm_manager({'agency': '', 'office': 'Invented County Parks Department',
                         'quote': 'is managed by the Invented County Parks Department'})
check('a managed-by sentence names the manager, quoted', mgr and mgr['agency'] == 'Invented County Parks Department' and mgr['quote'])
check('menu chrome ("STATE PARKS MENU") is never a manager',
      R.confirm_manager({'agency': '', 'office': 'STATE PARKS MENU', 'quote': 'managed by STATE PARKS MENU'}) is None)
check('menu chrome is still not a name either', R.is_menu_chrome('STATE PARKS MENU'))

# --- the address and the coordinates ---
loc = {'addresses': [{'text': 'PO Box 1, Invented, NY 12345', 'role': 'mailing'},
                     {'text': '12 Ridge Road, Invented, NY 12345', 'role': 'park'}],
       'coords': [{'lat': 42.6, 'lon': -74.4, 'role': 'unknown', 'from': 'map center'},
                  {'lat': 42.51, 'lon': -74.49, 'role': 'park', 'from': 'json-ld', 'km_from_pin': 1.2, 'pin_far': False}]}
addr, pt = R.confirm_place(loc)
check('the park address comes before a mailing box', addr == {'text': '12 Ridge Road, Invented, NY 12345', 'role': 'park'})
check('a park point is kept; a map centre (unknown role) never is', pt and pt['role'] == 'park' and pt['lat'] == 42.51)
check('a park point far from POTA\'s pin is not kept',
      R.confirm_place({'coords': [dict(loc['coords'][1], pin_far=True)]})[1] is None)

# --- the official map link ---
maps = [{'url': 'https://blog.invented.example.com/ridge-map.pdf', 'kind': 'pdf', 'names_park': True, 'text': 'map'},
        {'url': 'https://parks.invented.example.gov/ridge-trails', 'kind': 'web-map', 'names_park': True, 'text': 'Trail map'},
        {'url': 'https://parks.invented.example.gov/ridge-map.pdf', 'kind': 'pdf', 'names_park': True, 'text': 'Invented Ridge map'},
        {'url': 'https://parks.invented.example.gov/other.pdf', 'kind': 'pdf', 'names_park': False, 'text': 'Another forest'},
        {'url': 'https://www.protectedplanet.net/9999.pdf', 'kind': 'pdf', 'names_park': True, 'text': 'map'}]
m = R.confirm_map_link(maps)
check('the official map is an agency-host file that names the park', m and m['url'] == 'https://parks.invented.example.gov/ridge-map.pdf')
check('never a WDPA map', R.confirm_map_link(maps[-1:]) is None and R.is_wdpa('https://www.protectedplanet.net/x'))

# --- silent on an unofficial host ---
f = facts([page('https://blog.invented.example.com/ridge', 'Invented Ridge State Forest\nPark ID: 4521\nTotal area: 1,234 acres\n' + LONG)],
          'https://blog.invented.example.com/ridge', own='unofficial-host')
check('an unofficial page confirms nothing', all(v is None for v in f['confirm'].values()))

# --- public counts by state and agency only ---
doc = PP.confirm_counts({'US-NY': {'US-9001': facts([page(DEC, 'Invented Ridge State Forest' + LONG)], DEC)}})
text = json.dumps(doc)
check('the public counts name no park', not re.search(r'US-\d{4}', text) and doc['by_state']['US-NY']['agency_id'] == 1
      and 'dec.ny.gov' in doc['by_agency'])

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
