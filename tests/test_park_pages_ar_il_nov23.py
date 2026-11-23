#!/usr/bin/env python3
"""Page reader, 23 Nov 2026 5:10 AM (owner: "Yea go ahead" on Arkansas and Illinois). Both sites' real pages were opened first;
the shapes below are their markup with invented places.
ARKANSAS GFC: the WMA page draws its own outline from a GeoJSON feature in the page's script, far down a long page: a point
inside each of its largest parts is the page's own point. A page with several outlines (a map of many places) gives none.
ILLINOIS DNR: the park's figures are a field list (the field's name on one line, twice, its value on the next): latitude,
longitude, address, city, zip. The OTHER park's figures in the page's tracking data (the same on every page) are never
read. Prints PASS / FAIL, ends ALL PASS or SOME FAILED."""
import json, pathlib, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


W = '<p>' + 'Words about the place. ' * 340 + '</p>'            # the real pages show about 7,800 characters of text
PAD = '<script>var filler = "' + 'x' * 180000 + '";</script>'       # the real page is 220,000 characters; the outline sits near its end
SQ = lambda x, y, d: [[x, y], [x + d, y], [x + d, y + d], [x, y + d], [x, y]]
FEATURE = lambda coords: 'map.fitBounds(L.geoJson({"type": "Feature", "properties": {}, "geometry": {"type": "MultiPolygon", "coordinates": %s}}).getBounds())' % json.dumps(coords)
AR = ('<html><head><title>Cypress Slough WMA • Invented Game & Fish</title></head><body><h1>Cypress Slough WMA</h1>' + W + PAD +
      '<script>var zoneStyle = { color: "#FF8C00" }; ' + FEATURE([[SQ(-91.92, 35.04, 0.02)], [SQ(-91.80, 35.10, 0.005)]]) + '</script></body></html>')
AR_MANY = ('<html><head><title>Bayou Flats WMA • Invented Game & Fish</title></head><body><h1>Bayou Flats WMA</h1>' + W +
           '<script>' + FEATURE([[SQ(-91.92, 35.04, 0.02)]]) + ';' + FEATURE([[SQ(-93.0, 34.0, 0.02)]]) + '</script></body></html>')
FIELD = lambda cls, name, val: (f'<dl class="cmp-contentfragment__elements"><div class="cmp-contentfragment__element cmp-contentfragment__element--{cls}">'
                                f'<dt class="cmp-contentfragment__element-title hidden"> {name} </dt> <dt class="cmp-contentfragment__element-title hidden"> {name} </dt>'
                                f'<p class="cmp-contentfragment__element-value paragraph">{val}</p></div></dl>')
TRACK = ('<div data-cmp-data-layer="{&#34;xdm:text&#34;:&#34;Lake Front - Park Office&#34;,&#34;xdm:title&#34;:&#34;Park Address&#34;},{&#34;xdm:text&#34;:&#34;Zion&#34;,'
         '&#34;xdm:title&#34;:&#34;Park City&#34;},{&#34;xdm:text&#34;:&#34;60099&#34;,&#34;xdm:title&#34;:&#34;Park Zip&#34;},{&#34;xdm:text&#34;:&#34;42.466&#34;,'
         '&#34;xdm:title&#34;:&#34;Park Latitude&#34;},{&#34;xdm:text&#34;:&#34;-87.810&#34;,&#34;xdm:title&#34;:&#34;Park Longitude&#34;}"></div>')
IL = ('<html><head><title>Silver Creek State Park</title></head><body><h1>Silver Creek State Park</h1>' + W + TRACK + TRACK +
      FIELD('parkAddress', 'Park Address', '13608 Fox Road') + FIELD('parkCity', 'Park City', 'Yorkville') + FIELD('parkZip', 'Park Zip', '60560') +
      FIELD('parkPhone', 'Park Phone', '630-553-6297') + FIELD('parkLatitude', 'Park Latitude', '41.626') + FIELD('parkLongitude', 'Park Longitude', '-88.518') +
      '</body></html>')
H = 'https://parks.invented.gov/p/'
P = {'US-9971': ('Cypress Slough Wildlife Management Area', (35.05, -91.91), 'US-AR', AR),
     'US-9972': ('Bayou Flats Wildlife Management Area', (35.05, -91.91), 'US-AR', AR_MANY),
     'US-9973': ('Silver Creek State Park', (41.63, -88.52), 'US-IL', IL)}

with tempfile.TemporaryDirectory() as t:
    t = pathlib.Path(t)
    data = t / 'data' / 'parkinfo'; data.mkdir(parents=True)
    for area in ('US-AR', 'US-IL'):
        (data / f'{area}.json').write_text(json.dumps({'parks': {r: [n, H + r, 'State Park', '', '', pin[0], pin[1], 0, 0, 1]
                                                               for r, (n, pin, a, _b) in P.items() if a == area}}), encoding='utf-8')
    (t / 'fx.json').write_text(json.dumps({'pages': {H + r: {'status': 200, 'body': b} for r, (_n, _p, _a, b) in P.items()}}), encoding='utf-8')
    out = t / 'out'; out.mkdir()
    r = subprocess.run([sys.executable, '-B', str(ROOT / '.github/scripts/kpc_park_pages.py'), 'read', '--data', str(t / 'data'), '--out', str(out),
                        '--state', str(out / 'state.json'), '--fixtures', str(t / 'fx.json'), '--today', '2026-11-23', '--areas', 'US-AR US-IL', '--quiet'],
                       capture_output=True, text=True)
    if r.returncode: print(r.stderr[-1500:])
    f = {}
    for p in (out / 'facts').glob('*.json'): f.update(json.loads(p.read_text()).get('parks', {}))
    L = lambda ref: (f.get(ref) or {}).get('location') or {}
    c1 = L('US-9971').get('coords') or []
    check('Arkansas: the outline in the page script gives a point inside its largest part, though it sits 180,000 characters down',
          r.returncode == 0 and c1 and abs(c1[0]['lat'] - 35.05) < 1e-3 and abs(c1[0]['lon'] + 91.91) < 1e-3 and c1[0].get('from') == 'outline in the page')
    check('Arkansas: its second part gives a second point', len(c1) == 2 and abs(c1[1]['lat'] - 35.1025) < 1e-3)
    check('a page with several outlines (a map of many places): none is taken', not (L('US-9972').get('coords') or []))
    c3 = L('US-9973').get('coords') or []
    check("Illinois: 'Park Latitude' / 'Park Longitude' as a field list give the park's own point",
          [(round(c['lat'], 3), round(c['lon'], 3)) for c in c3] == [(41.626, -88.518)])
    check("Illinois: the OTHER park's point in the tracking data (42.466, -87.810) is never read",
          not any(abs(c['lat'] - 42.466) < 0.01 for c in c3))
    a3 = L('US-9973').get('addresses') or []
    check("Illinois: 'Park Address' / 'Park City' / 'Park Zip' make one address, with the park's own state",
          [(a.get('text'), a.get('role')) for a in a3] == [('13608 Fox Road, Yorkville, IL 60560', 'park')])
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
