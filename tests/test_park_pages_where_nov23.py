#!/usr/bin/env python3
"""Page reader, 23 Nov 2026 (owner: "get information off the websites to help confirm and match parks, using real names,
addresses and directions and maps"). The shapes below are the markup of real agency pages opened that night (Washington
parks, WDFW, Indiana, Ontario Parks, Tourism Saskatchewan, Manitoba, Wisconsin DNR, Arkansas GFC, Illinois DNR), with
invented places. Before: none of them gave a point, an address or directions. Now each gives what its page holds; a page
with several different points (a site template, a map of many places) gives none. Every fetched page is kept, and
--reextract reads the kept pages again without asking a site. Prints PASS / FAIL, ends ALL PASS or SOME FAILED."""
import json, os, pathlib, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


W = '<p>' + 'Words about the place. ' * 40 + '</p>'
page = lambda title, h1, body: f'<html><head><title>{title}</title></head><body><h1>{h1}</h1>{W}{body}</body></html>'
H = 'https://parks.invented.gov/p/'
P = {  # ref: (POTA name, pin, page)
    'US-9601': ('Cedar Point State Park', (47.73, -122.25), page('Cedar Point State Park | Invented State Parks', 'Cedar Point State Park',
        '<div><span>14445 Juanita Drive NE</span><br/><span>Kenmore, WA 98028</span></div>'
        '<div class="geolocation" data-lat="47.733289" data-lng="-122.256337"></div>')),
    'US-9602': ('Otter Lake State Fishing Lake', (47.78, -117.10), page('Otter Lake | Invented Fish & Wildlife', 'Otter Lake',
        '<p>Twelve miles northeast of Spokane about a mile from the border.</p><div>County: Spokane</div><div>Center: 47.777189, -117.100543</div>')),
    'US-9603': ('Chain O Hills State Park', (41.33, -85.38), page('State Parks: Chain O Hills State Park', 'Chain O Hills State Park',
        '<p><strong>Address:</strong><br /> 2355 E. 75 S.<br /> Albion, IN 46701</p><p><strong>Link to this page:</strong><br />on.IN.gov/x</p>')),
    'US-9604': ('Springbrook Provincial Park', (44.44, -79.75), page('Springbrook Provincial Park', 'Springbrook Provincial Park',
        '<div><p><strong>Mailing Address/Physical Address:</strong></p> <p>1331 ON-26</p> <p>Minesing, ON</p> <p>L9X 0G1</p></div>')),
    'US-9605': ('Prairie Landing Provincial Park', (50.66, -107.96), page('Prairie Landing Provincial Park | Invented Tourism', 'Prairie Landing Provincial Park',
        '<script>window.__D="{\\\\"sciId\\\\":312}],\\\\"longitude\\\\":\\\\"-107.9639054\\\\",\\\\"latitude\\\\":\\\\"50.659512\\\\"}";</script>')),
    'US-9606': ('Goose Mountain Provincial Park', (51.67, -100.9),
        '<html><head><title>Parks and Protected Spaces | Environment and Climate Change | Province of Invented</title></head><body>'
        '<h1>Environment and Climate Change</h1><h1>Goose Mountain Provincial Park</h1>' + W +
        '<p><strong>Park Directions </strong></p> <p>Leaving Dauphin, follow PTH 5 west 50 km/31.1 mi. to PR 366, drive north 35 km/21.7 mi. to the park.</p>'
        '<p><strong>Resources </strong></p></body></html>'),
    'US-9607': ('Marsh State Wildlife Area', (44.45, -88.55), page('Marsh Wildlife Area | | Invented DNR', 'MARSH WILDLIFE AREA',
        '<p>Marsh Wildlife Area is in northcentral Outagamie County. The property is approximately 1,350 acres in size.</p>'
        '<p>Find Marsh Wildlife Area 2 miles east of Shiocton on Highway 54.</p>')),
    'US-9608': ('Cypress Slough Wildlife Management Area', (35.0, -91.9), page('Cypress Slough WMA • Invented Game & Fish', 'Cypress Slough WMA',
        '<p>Cypress Slough WMA encompasses 1,503 acres in northern Lonoke and southern White counties.</p>')),
    # the Illinois DNR trap: every park's page carries the SAME other park's point, and a map of many places
    'US-9609': ('Silver Creek State Park', (41.63, -88.52), page('Silver Creek State Park', 'Silver Creek State Park',
        '<script>var parks=[{"latitude":"42.466","longitude":"-87.810"},{"latitude":"41.100","longitude":"-88.900"},{"lat":40.5,"lng":-89.5}];</script>')),
}


def run(t, extra, env=None):
    data = t / 'data' / 'parkinfo'; data.mkdir(parents=True, exist_ok=True)
    (data / 'US-ZZ.json').write_text(json.dumps({'parks': {r: [n, H + r, 'State Park', '', '', pin[0], pin[1], 0, 0, 1] for r, (n, pin, _b) in P.items()}}), encoding='utf-8')
    (t / 'fx.json').write_text(json.dumps({'pages': {H + r: {'status': 200, 'body': b} for r, (_n, _p, b) in P.items()}}), encoding='utf-8')
    out = t / 'out'; out.mkdir(exist_ok=True)
    r = subprocess.run([sys.executable, '-B', str(ROOT / '.github/scripts/kpc_park_pages.py'), 'read', '--data', str(t / 'data'), '--out', str(out),
                        '--state', str(out / 'state.json'), '--today', '2026-11-23', '--areas', 'US-ZZ', '--quiet'] + extra,
                       capture_output=True, text=True, env=dict(os.environ, **(env or {})))
    f = json.loads((out / 'facts' / 'US-ZZ.json').read_text()).get('parks', {}) if (out / 'facts' / 'US-ZZ.json').is_file() else {}
    return r, f


with tempfile.TemporaryDirectory() as t:
    t = pathlib.Path(t)
    r, f = run(t, ['--fixtures', str(t / 'fx.json'), '--keep-pages', str(t / 'pages-kept')])
    if r.returncode: print(r.stderr[-1500:])
    L = lambda ref: (f.get(ref) or {}).get('location') or {}
    pts = lambda ref: [(round(c['lat'], 4), round(c['lon'], 4)) for c in L(ref).get('coords') or []]
    adr = lambda ref: [a.get('text') for a in L(ref).get('addresses') or []]
    check('a point in the page data (data-lat / data-lng) is taken', pts('US-9601') == [(47.7333, -122.2563)])
    check('a street and "Town, WA ZIP" on two lines is one address', any('14445 Juanita Drive NE' in a and '98028' in a for a in adr('US-9601')))
    check('"Center: 47.777189, -117.100543" alone on its line is a point', pts('US-9602') == [(47.7772, -117.1005)])
    check('"Twelve miles northeast of Spokane" is kept as how far and which way from a town',
          [(o['dir'], o['of'], round(o['km'])) for o in L('US-9602').get('offsets') or []] == [('NE', 'Spokane', 19)])
    check('"County: Spokane" is the county', L('US-9602').get('counties') == ['Spokane'])
    check('an address under "Address:" with no street word (2355 E. 75 S.)', adr('US-9603') == ['2355 E. 75 S., Albion, IN 46701'])
    a4 = (L('US-9604').get('addresses') or [{}])[0]
    check('"Mailing Address/Physical Address:" over three lines is the park\'s address, not a mailbox',
          a4.get('text') == '1331 ON-26, Minesing, ON, L9X 0G1' and a4.get('role') == 'park')
    check('"latitude" / "longitude" in a script (quoted with backslashes, longitude first) is a point', pts('US-9605') == [(50.6595, -107.9639)])
    d6 = L('US-9606').get('directions') or {}
    check('"Park Directions" with no colon: its roads and town are read', 'PTH 5' in (d6.get('roads') or []) and 'PR 366' in (d6.get('roads') or [])
          and 'Dauphin' in (d6.get('towns') or []))
    n6 = (f.get('US-9606') or {}).get('name') or {}
    check('the park name in a second heading agrees (the first is the department)', n6.get('vs_pota') in ('same', 'same-core'))
    check('"2 miles east of Shiocton on Highway 54": the offset, the road and the county',
          [(o['dir'], o['of'], o['km']) for o in L('US-9607').get('offsets') or []] == [('E', 'Shiocton', 3.2)]
          and 'Highway 54' in ((L('US-9607').get('directions') or {}).get('roads') or []) and L('US-9607').get('counties') == ['Outagamie'])
    check('"in northern Lonoke and southern White counties": both', L('US-9608').get('counties') == ['Lonoke', 'White'])
    check('several different points in the page data (a template, a map of many places): none is taken', pts('US-9609') == [])
    man = json.loads((t / 'pages-kept' / 'manifest.json').read_text()) if (t / 'pages-kept' / 'manifest.json').is_file() else {}
    kept = man.get('pages') or {}
    check('every fetched page is kept, packed, with its date', len(kept) == len(P) and all((t / 'pages-kept' / v['file']).is_file()
          and v.get('date') == '2026-11-23' for v in kept.values()))
    # an older reader's facts: wipe one park's location, then read the KEPT pages again. No fixtures, the network closed.
    fp = t / 'out' / 'facts' / 'US-ZZ.json'
    d = json.loads(fp.read_text()); d['parks']['US-9601']['location'] = {'coords': [], 'addresses': [], 'directions': None}
    fp.write_text(json.dumps(d))
    r2, f2 = run(t, ['--reextract'], env={'KPC_NO_NET': '1'})
    if r2.returncode: print(r2.stderr[-1500:])
    c2 = ((f2.get('US-9601') or {}).get('location') or {}).get('coords') or []
    check('--reextract reads the kept pages again with no site asked: the point is back',
          r2.returncode == 0 and [(round(c['lat'], 4), round(c['lon'], 4)) for c in c2] == [(47.7333, -122.2563)])
    check('the read date stays the day the page was really read', ((f2.get('US-9601') or {}).get('page') or {}).get('read') == '2026-11-23')
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
