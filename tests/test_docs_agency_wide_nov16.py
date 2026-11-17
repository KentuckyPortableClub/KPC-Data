#!/usr/bin/env python3
"""Nov 16 evening: a correctly identified agency-wide maps or publications list
must not be kept as each park's own map, even when the page did not open (Maine's
publications_maps index was HTTP 403 on 33 of 148 parks and tripped F-D1). Maine's
parks fees-and-rules page counts as agency-wide: it is kept and labelled, and URL /
how / status are not rewritten. Missouri's Title 3 law index does not count as
agency-wide (only if it pointed at the public-lands rules section). A statewide
page that is already correctly labelled is left as it was. Offline: synthetic
records only, nothing is fetched, and nothing in the repo is written."""
import os, pathlib, sys, tempfile

HERE = pathlib.Path(__file__).resolve().parent.parent
os.environ['OUT'] = tempfile.mkdtemp(prefix='kpc-docs-agency-')
sys.path.insert(0, str(HERE / '.github' / 'scripts'))
import kpc_docs_bot as B  # noqa: E402

ok = True


def check(cond, msg):
    global ok
    print(('PASS ' if cond else 'FAIL ') + msg)
    ok = ok and bool(cond)


MAPS = 'https://www.maine.gov/dacf/parks/publications_maps/index.shtml'
FEES = 'https://www.maine.gov/dacf/parks/park_passes_fees_rules/index.shtml'
TITLE3 = 'https://www.sos.mo.gov/adrules/csr/current/3csr/3csr.asp'
PARK_RULES = 'https://mostateparks.com/page/55066/rules-and-regulations'
LISTS_ME = {'maine.gov': {'pages': [MAPS], 'pick': 'any', 'rules': FEES}}
LISTS_MO = {
    'mdc.mo.gov': {'pages': [], 'rules': 'https://mdc.mo.gov/discover-nature/places/regulations'},
    'mostateparks.com': {'pages': [], 'rules': PARK_RULES},
}


def rec(name, page, *, rules=None, mp=None):
    return {'n': name, 't': 'State Park', 'page': page,
            'rules': rules or {'url': '', 'how': '', 'status': 'not found'},
            'map': mp or {'url': '', 'status': 'no map link on file and none on the park page', 'how': ''}}


def area(parks):
    return {'area': 'US-XX', 'parks': parks}


# (a) the Maine-shaped hole: 33 parks have the publications/maps index as their
# map (HTTP 403). Today's shared_pass counted only status==ok, so it left them
# and the waiting-room F-D1 check held the file. After the fix the index is not
# each park's map. 25 of those parks also have the fees-and-rules page unread:
# it is on file as agency-wide, so it is kept and labelled; URL, how, and status
# stay as they were.
parks = {}
for i in range(33):
    parks[f'US-{1000+i}'] = rec(
        f'Coast Park {i}', f'https://www.maine.gov/dacf/parks/coast-park-{i}',
        mp={'url': MAPS, 'how': "the page in a browser ('Publications and Maps')", 'status': 'HTTP 403'},
        rules=({'url': FEES, 'how': "a link on the park's page ('Park Passes, Fees Rules')", 'status': 'did not open'}
               if i < 25 else {'url': '', 'how': '', 'status': 'not found'}))
# 15 more parks with no shared map, so the area is 48 parks like Maine's 148-scale
for i in range(33, 48):
    parks[f'US-{1000+i}'] = rec(f'Coast Park {i}', f'https://www.maine.gov/dacf/parks/coast-park-{i}')
D = area(parks)
B.shared_pass(D, LISTS_ME)
maps_left = [k for k, p in D['parks'].items() if (p.get('map') or {}).get('url') == MAPS]
fees = [p for k, p in D['parks'].items() if k < 'US-1025' and int(k.split('-')[1]) < 1025]
# US-1000..1024 are the 25 with fees
fees = [D['parks'][f'US-{1000+i}'] for i in range(25)]
check(maps_left == [],
      f'the publications/maps index is not kept as each park\'s map, even at HTTP 403 (still on {len(maps_left)} parks)')
check(all('agency maps or publications list was dropped' in ((p.get('map') or {}).get('status') or '')
          for p in [D['parks'][f'US-{1000+i}'] for i in range(33)]),
      'the drop reason says it was an agency maps or publications list')
check(all((p.get('rules') or {}).get('url') == FEES
          and (p.get('rules') or {}).get('status') == 'did not open'
          and (p.get('rules') or {}).get('how') == "a link on the park's page ('Park Passes, Fees Rules')"
          and (p.get('rules') or {}).get('rules_scope') == 'agency' for p in fees),
      'Maine fees-and-rules is kept and labelled agency-wide; URL, how, and status are unchanged')

# (b) Missouri Title 3 shape: 25 parks, each with its own page, same unread law
# index, not the agency-wide page on file. Not labelled. Dropped.
mo = {}
for i in range(25):
    mo[f'US-{2000+i}'] = rec(
        f'Ozark Park {i}', f'https://mostateparks.com/park/ozark-{i}',
        rules={'url': TITLE3, 'how': "a link on the park's page ('Missouri Code of State Regulations')",
               'status': 'rules page not read (the site is resting: next run)'})
D = area(mo)
B.shared_pass(D, LISTS_MO)
check(all((p.get('rules') or {}).get('url') == '' for p in D['parks'].values()),
      'Missouri Title 3 is not treated as agency-wide and is not kept as each park\'s rules')
check(all((p.get('rules') or {}).get('rules_scope') != 'agency' for p in D['parks'].values()),
      'Title 3 is not labelled agency-wide')

# (c) a correctly labelled statewide rules page is left as it was (URL, how,
# status, and the agency label stay). 25 parks, unread.
lab = {}
how = 'the agency-wide rules page (chat 8 survey)'
st = 'did not open'
for i in range(25):
    lab[f'US-{3000+i}'] = rec(
        f'Lake {i}', f'https://mostateparks.com/park/lake-{i}',
        rules={'url': PARK_RULES, 'how': how, 'status': st, 'rules_scope': 'agency'})
D = area(lab)
before = {k: dict(p['rules']) for k, p in D['parks'].items()}
B.shared_pass(D, LISTS_MO)
check(all(D['parks'][k]['rules'] == before[k] for k in before),
      'a statewide page that is already correctly labelled is unchanged (URL, how, status, and scope)')

# (d) a list-page URL that clearly names one park is kept as that park's map;
# the same list page on other parks is still dropped.
mix = {}
for i in range(5):
    mix[f'US-{4000+i}'] = rec(
        f'Game Land {i}', f'https://www.example.test/parks/gl-{i}',
        mp={'url': MAPS, 'how': "a link on the park's page ('Publications and Maps')", 'status': 'ok', 'kind': 'pdf'})
mix['US-4004']['n'] = 'Publications Maps'
# names_park via file/url words would need the park name in the URL; the URL is
# publications_maps, so a park literally named to match the file would be kept.
# Use names_park already recorded as True for one park instead, as a prior read.
mix['US-4004']['n'] = 'Willow Creek Pond'
mix['US-4004']['map'] = {'url': MAPS, 'how': "a link on the park's page ('Willow Creek Pond map')",
                         'status': 'ok', 'kind': 'pdf', 'names_park': True}
D = area(mix)
B.shared_pass(D, LISTS_ME)
check(all((p.get('map') or {}).get('url') == '' for k, p in D['parks'].items() if k != 'US-4004'),
      'the same publications list is dropped for parks it does not name')
check((D['parks']['US-4004']['map'] or {}).get('url') == MAPS,
      'a publications-list URL already recorded as naming that park is kept')

# (e) 19 parks sharing an unread rules page stay under the 20-park line
few = {f'US-{5000+i}': rec(f'Park {i}', f'https://www.example.test/parks/{i}',
                           rules={'url': TITLE3, 'how': "a link on the park's page ('Code')", 'status': 'did not open'})
        for i in range(19)}
D = area(few)
B.shared_pass(D, LISTS_MO)
check(all((p.get('rules') or {}).get('url') == TITLE3 for p in D['parks'].values()),
      '19 parks sharing an unread rules page that is not agency-wide stay under the 20-park line')

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
