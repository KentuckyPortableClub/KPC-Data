#!/usr/bin/env python3
"""Nov 16: the campground info bot must not read a thousands-separator as a smaller
number ("3,500" is not 500), and must not take a site count from a statewide or
shared camping page for every park. A count comes from the park's own page, or
it is left blank. Offline: synthetic snippets and records only, nothing is
fetched, and nothing in the repo is written."""
import json, os, pathlib, sys, tempfile

HERE = pathlib.Path(__file__).resolve().parent.parent
os.environ['OUT'] = tempfile.mkdtemp(prefix='kpc-site-count-')
sys.path.insert(0, str(HERE / '.github' / 'scripts'))
import kpc_campinfo_bot as C  # noqa: E402

ok = True


def check(cond, msg):
    global ok
    print(('PASS ' if cond else 'FAIL ') + msg)
    ok = ok and bool(cond)


def total_of(text, url, name):
    F = C.facts_from_text(text, url, name)
    return (F.get('sites.total') or {}).get('value')


def tent_of(text, url, name):
    F = C.facts_from_text(text, url, name)
    return (F.get('sites.tent') or {}).get('value')


# (a) thousands separators
check(total_of('Forty-one state parks and historic sites offer more than 3,500 campsites that range from secluded walk-in sites to sites with hookups.',
               'https://example.test/activity/camping', 'Babler Memorial State Park') is None,
      'a statewide "more than 3,500 campsites" is not read as 500, and is not taken as a park total')
check(total_of('Pine Campground has 1,200 sites with water hookups.',
               'https://example.test/parks/pine-campground', 'Pine Campground') == 1200,
      '"1,200 sites" on the park\'s own page is 1200, not 200')
check(total_of('The campground offers 146 sites with electric and water hookups.',
               'https://example.test/parks/pine-campground', 'Pine Campground') == 146,
      'a plain "146 sites" on the park\'s own page is still 146')

# (b) statewide / shared pages, and whole-state phrasing
check(total_of('Green River Reservoir State Park offers 27 remote tent sites scattered along 19 miles of undeveloped shoreline.',
               'https://example.test/camping', 'Allis State Park') is None,
      'a statewide camping page naming another park is not this park\'s site count')
check(tent_of('Green River Reservoir State Park offers 27 remote tent sites scattered along 19 miles of undeveloped shoreline.',
              'https://example.test/camping', 'Allis State Park') is None,
      'the same shared page does not write a tent count for this park either')
check(total_of('Green River Reservoir State Park has 27 remote tent sites, accessible by boat.',
               'https://example.test/parks/green-river-reservoir', 'Green River Reservoir State Park') == 27,
      'the same 27 on that park\'s own page is kept for that park')
check(total_of('Visit for a swim or hike, camp at one of our 27 sites, or kayak on Laurel Lake.',
               'https://example.test/camping-at-state-parks/locations', 'Shawme Forest Campground') is None,
      'a shared locations page ("camp at one of our 27 sites") is not this park\'s site count')
check(total_of('At more than 100 sites across the state, the department enhances education.',
               'https://example.test/', 'Lakeside State Park') is None,
      'a banner "more than 100 sites across the state" on a homepage is not a park site count')
check(total_of('Poplar Point offers 579 sites for RV, tent and trailer camping; 363 sites have electric and water hookups.',
               'https://example.test/state-parks/jordan-lake/camping', 'Poplar Point Campground') == 579,
      'a count on that park\'s own camping page is kept (579 on one park is for the owner to judge)')

# one_camp: a state homepage followed to a statewide camping page must not copy that count
PAGES = {
    'https://example.test/': ('ok', 'Welcome to the state parks. See our camping page.',
                              [('https://example.test/activity/camping', 'Camping')]),
    'https://example.test/activity/camping': (
        'ok',
        'Forty-one state parks and historic sites offer more than 3,500 campsites that range from secluded walk-in sites to sites with hookups.',
        []),
    'https://example.test/parks/pine-campground': (
        'ok', 'Pine Campground has 62 campsites, all with electric hookups.', []),
}


def stub_read(u):
    return PAGES[u]


C.official = lambda url, area, park='': True
C.late = lambda: False
C.elevation = lambda *a, **k: {'value': None, 'src': None}
C.fcc_files = lambda area, state: {'status': 'needs FCC token'}
C.read_page = stub_read

row = {'name': 'Babler Memorial State Park', 'lat': 38.6, 'lon': -90.7, 'park': 'Babler Memorial State Park',
       'agency': 'state', 'kind': 'campground', 'page': 'https://example.test/', 'reserve': '', 'src': 'campstate', 'id': 'babler'}
rec = C.one_camp('US-ZZ', row, {'areas': {}})
check(rec['sites']['total'] is None, 'one_camp: starting from a site homepage, a statewide camping sub-page does not fill the site count')
check('sites.total' not in rec['facts_src'], 'one_camp: no sites.total source line is stored from that statewide sub-page')

row2 = dict(row, name='Pine Campground', park='Pine Park', page='https://example.test/parks/pine-campground', id='pine')
rec2 = C.one_camp('US-ZZ', row2, {'areas': {}})
check(rec2['sites']['total'] == 62, 'one_camp: a count on the park\'s own page is kept')

# a site-count URL used for many different parks is dropped; sub-records of one park are kept
def rec_with(cid, name, url, n):
    r = C.blank_record({'name': name, 'lat': 1, 'lon': 2, 'park': name, 'agency': 'state', 'kind': 'campground',
                        'page': url, 'reserve': '', 'src': 'campstate', 'id': cid})
    r['sites']['total'] = n
    r['facts_src']['sites.total'] = {'url': url, 'date': '2026-11-16', 'line': f'{n} sites'}
    return r


D = {'camps': {
    'p1': rec_with('p1', 'Park One', 'https://example.test/camping', 27),
    'p2': rec_with('p2', 'Park Two', 'https://example.test/camping', 27),
    'p3': rec_with('p3', 'Park Three', 'https://example.test/camping', 27),
    'p4': rec_with('p4', 'Park Four', 'https://example.test/camping', 27),
    'own': rec_with('own', 'Green River', 'https://example.test/parks/green-river-reservoir', 27),
    'j:hq0': rec_with('j:hq0', 'Poplar Point', 'https://example.test/state-parks/jordan-lake/camping', 579),
    'j:hq1': rec_with('j:hq1', 'Poplar Point', 'https://example.test/state-parks/jordan-lake/camping', 579),
    'j:hq2': rec_with('j:hq2', 'Poplar Point', 'https://example.test/state-parks/jordan-lake/camping', 579),
    'j:hq3': rec_with('j:hq3', 'Poplar Point', 'https://example.test/state-parks/jordan-lake/camping', 579),
}}
n_drop = C.drop_shared_site_counts(D)
check(all(D['camps'][k]['sites']['total'] is None for k in ('p1', 'p2', 'p3', 'p4')),
      'a count taken from one URL for more than 3 parks is left blank')
check(n_drop == 4 and D['camps']['own']['sites']['total'] == 27,
      'a count from a park\'s own unique page is not dropped')
check(all(D['camps'][k]['sites']['total'] == 579 for k in ('j:hq0', 'j:hq1', 'j:hq2', 'j:hq3')),
      'four sub-records of one park that share a page keep the count (for the owner to judge)')

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
