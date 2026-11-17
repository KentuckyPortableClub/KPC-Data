#!/usr/bin/env python3
"""Nov 16: the documents bot must not take a link that sits on a site-wide official
page (a home, index, or footer shared by many parks of the state) as each park's
own rules or map, unless that destination clearly names the park. A resting or
unread copy of the wrong page is still dropped: blank beats wrong. Parks that
each have their own page and all link to the same state-wide rules page are not
this case. Offline: synthetic records only, nothing is fetched, and nothing in
the repo is written."""
import os, pathlib, sys, tempfile

HERE = pathlib.Path(__file__).resolve().parent.parent
os.environ['OUT'] = tempfile.mkdtemp(prefix='kpc-docs-shared-')
sys.path.insert(0, str(HERE / '.github' / 'scripts'))
import kpc_docs_bot as B  # noqa: E402

ok = True


def check(cond, msg):
    global ok
    print(('PASS ' if cond else 'FAIL ') + msg)
    ok = ok and bool(cond)


HOME = 'https://www.example-agency.test/'
NAV = 'https://www.example-agency.test/sites/default/files/seasons-rules-big-game-2026.pdf'
HOWN = "a link on the park's page ('Big Game Seasons and Rules')"
REST = 'rules page not read (the site is resting: next run)'
AGENCY = 'https://www.example-agency.test/rules-and-regulations'


def rec(ref, name, page, rules_url, how=HOWN, status=REST, rules_scope=None, mp=None):
    r = {'url': rules_url, 'how': how, 'status': status}
    if rules_scope: r['rules_scope'] = rules_scope
    return {'n': name, 't': 'State Fishing Lake', 'page': page, 'rules': r, 'map': mp or {'url': '', 'status': 'no map link on file and none on the park page', 'how': ''}}


def area(parks):
    return {'area': 'US-XX', 'parks': parks}


# (a) the Idaho-shaped hole: 25 parks share the agency home; the same footer PDF
# is recorded as each park's rules with status "resting". Today's shared_pass
# counted only status==ok, so it left them. After the fix they are blanked.
parks = {f'US-{1000+i}': rec(f'US-{1000+i}', f'Lake {i} Access', HOME, NAV) for i in range(25)}
D = area(parks)
B.shared_pass(D, {})
check(all((p.get('rules') or {}).get('url') == '' for p in D['parks'].values()),
      '25 parks sharing the agency home do not keep a site-wide Big Game PDF as their rules, even when the PDF was not read')
check(all('page shared by 25 parks was dropped' in ((p.get('rules') or {}).get('status') or '') for p in D['parks'].values()),
      'the drop reason says the official page was shared, not that a working rules page was found')

# (b) the same footer link that clearly names one park is kept for that park only
parks = {f'US-{1000+i}': rec(f'US-{1000+i}', f'Lake {i} Access', HOME, NAV) for i in range(25)}
parks['US-1024'] = rec('US-1024', 'Willow Creek Pond', HOME,
                       'https://www.example-agency.test/maps/willow-creek-pond-rules.pdf',
                       how="a link on the park's page ('Willow Creek Pond rules')")
D = area(parks)
B.shared_pass(D, {})
check(all((p.get('rules') or {}).get('url') == '' for k, p in D['parks'].items() if k != 'US-1024'),
      'the other 24 parks on that home still have the site-wide link dropped')
check((D['parks']['US-1024']['rules'] or {}).get('url', '').endswith('willow-creek-pond-rules.pdf'),
      "a link on that shared home that names Willow Creek Pond is kept as that park's rules")

# (c) ME / MO shape: each park has its own official page, all link to the same
# state-wide rules URL, status is not ok, the URL is not in lists.json. Kept.
own = {}
STATEWIDE = 'https://www.example-agency.test/park_passes_fees_rules/index.shtml'
for i in range(25):
    own[f'US-{2000+i}'] = rec(f'US-{2000+i}', f'Coast Park {i}',
                              f'https://www.example-agency.test/parks/coast-park-{i}',
                              STATEWIDE, how="a link on the park's page ('Park Passes, Fees Rules')",
                              status='did not open')
D = area(own)
before = {k: dict(p['rules']) for k, p in D['parks'].items()}
B.shared_pass(D, {})
check(all((p.get('rules') or {}).get('url') == STATEWIDE and (p.get('rules') or {}).get('status') == 'did not open' for p in D['parks'].values()),
      '25 parks that each have their own page and all link to the same unread state-wide rules page keep that page')
check(all(D['parks'][k]['rules'] == before[k] for k in before),
      'those state-wide rows are unchanged (status, how, and URL)')

# (d) the listed agency-wide rules page is kept even when 25 parks share a home
listed = {f'US-{3000+i}': rec(f'US-{3000+i}', f'Lake {i}', HOME, AGENCY,
                              how='the agency-wide rules page (chat 8 survey)', status='ok', rules_scope='agency') for i in range(25)}
D = area(listed)
B.shared_pass(D, {'example-agency.test': {'pages': [], 'rules': AGENCY}})
check(all((p.get('rules') or {}).get('url') == AGENCY and (p.get('rules') or {}).get('rules_scope') == 'agency' for p in D['parks'].values()),
      'the agency-wide rules page on file is kept and still labelled agency when parks share a home')

# (e) a denied-page map on that shared home is left alone
denied = {'url': 'https://www.google.com/maps/place/39N+88W', 'how': "a link on the park's page ('Map')",
          'status': "opened, a government data / policies page, not this park's map (chat 11 regrade 2)", 'kind': 'denied page'}
parks = {f'US-{4000+i}': rec(f'US-{4000+i}', f'Lake {i}', HOME, '', how='', status='not found', mp=dict(denied)) for i in range(25)}
# give them no rules URL so only the map is in play
D = area(parks)
B.shared_pass(D, {})
check(all((p.get('map') or {}).get('kind') == 'denied page' and (p.get('map') or {}).get('url') == denied['url'] for p in D['parks'].values()),
      'a denied-page map on the shared home is left as a denied page (existing handling)')

# (f) 19 parks on a shared home stay under the existing 20-park line
few = {f'US-{5000+i}': rec(f'US-{5000+i}', f'Lake {i}', HOME, NAV) for i in range(19)}
D = area(few)
B.shared_pass(D, {})
check(all((p.get('rules') or {}).get('url') == NAV for p in D['parks'].values()),
      '19 parks on a shared official page are under the 20-park line and are not dropped')

# (g) a site-wide map link on the shared home is also dropped; a map that names the park is kept
parks = {}
for i in range(25):
    parks[f'US-{6000+i}'] = rec(f'US-{6000+i}', f'Lake {i} Access', HOME, '', how='', status='not found',
                                mp={'url': 'https://www.example-agency.test/statewide-map.pdf', 'how': "a link on the park's page ('State map')",
                                    'status': 'rules page not read (the site is resting: next run)', 'kind': 'pdf'})
parks['US-6024']['n'] = 'Willow Creek Pond'
parks['US-6024']['map'] = {'url': 'https://www.example-agency.test/maps/willow-creek-pond-map.pdf',
                           'how': "a link on the park's page ('Willow Creek Pond map')", 'status': 'ok', 'kind': 'pdf'}
D = area(parks)
B.shared_pass(D, {})
check(all((p.get('map') or {}).get('url') == '' for k, p in D['parks'].items() if k != 'US-6024'),
      'a site-wide map on the shared home is not each park\'s map')
check((D['parks']['US-6024']['map'] or {}).get('url', '').endswith('willow-creek-pond-map.pdf'),
      'a map link on that home that names Willow Creek Pond is kept')

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
