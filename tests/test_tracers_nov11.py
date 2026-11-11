#!/usr/bin/env python3
"""Tracers, remaining work after Data #62 (KPC owner, 2026-11-11). Offline: no request leaves the machine (a fake session answers).

1. The built tools match their sources (draft/tools/_common/build.py --check). Data #63 had put the never-contact guard into the built
   kpc_parcels.py only, so a rebuild would have quietly removed it; the guard now lives in the shared polite.py.
2. Zero requests to never-contact hosts (services*.arcgis.com, apps.fs.usda.gov, ncnhde.natureserve.org), robots.txt included, through
   every door of the shared polite reader, in every built tool that can be loaded here, and through a whole kpc_parcels park run.
3. kpc_parcels: a search hit on a never-contact host, or a hit that names another state only, no longer uses up --max-tries; the
   right county layer is still found with --max-tries 1. The acceptance rules are the same (government publisher, not zoning, the pin
   falls on one of its parcels): a wrong-state layer the pin does not fall on is still never accepted.
4. The picture tracer's --offline replay: kpc_trace_limits.cached_basemap_ok decides as before for a normal run (a partial basemap is
   asked again) and lets an --offline run use the saved basemap as it is.
5. The hosts list (kpc_trace_hosts.py, kpc_trace_picture.py --list-hosts): every host a run on a fixtures folder can contact, made
   with no network connection; never-contact hosts are named and refused.
6. The matcher-input switches (band-road junctions, box masks, dark boundary rings): on by default, each can be turned off alone, and
   kpc_trace_marks.py's synthetic selftest passes (the end-to-end match checks are dev/marks_match_test.py, run by the workflow).
Prints PASS / FAIL lines, ends ALL PASS / SOME FAILED."""
import importlib.util, json, os, pathlib, subprocess, sys, types

ROOT = pathlib.Path(__file__).resolve().parents[1]
D = ROOT / '.github/scripts/draft'
T = D / 'tools'
ok = True


def check(msg, c):
    global ok
    ok &= bool(c)
    print(('PASS ' if c else 'FAIL ') + msg)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


NEVER = ['https://services1.arcgis.com/a/arcgis/rest/services/P/FeatureServer/0/query?f=json', 'https://services.arcgis.com/b/x',
         'https://SERVICES9.arcgis.com./c/x', 'https://services-eu1.arcgis.com/d/x', 'https://apps.fs.usda.gov/arcx/rest/services/x',
         'https://ncnhde.natureserve.org/x', 'https://services2.arcgis.com/x/robots.txt']


def is_never(u):
    from urllib.parse import urlparse
    h = (urlparse(u).hostname or '').lower().rstrip('.')
    return h.endswith('arcgis.com') and h.startswith('services') or h in ('apps.fs.usda.gov', 'ncnhde.natureserve.org')


class _R:
    def __init__(self, st, body=b'', hd=None, url=''):
        self.status_code, self.headers, self.url, self._b = st, hd or {}, url, body

    def iter_content(self, n):
        return [self._b]

    def close(self):
        pass


# ---- 1. built tools == sources
r = subprocess.run([sys.executable, '-B', str(T / '_common/build.py'), '--check'], capture_output=True, text=True)
check('every built tool matches its source + _common/polite.py (a rebuild cannot drop the #63 guard): ' + r.stdout.strip().replace('\n', '; '),
      r.returncode == 0 and 'DIFFERS' not in r.stdout)
pol = (T / '_common/polite.py').read_text(encoding='utf-8')
check('the never-contact guard sits in the shared polite.py: _one() and robots_for() refuse first',
      pol.count('if banned(url):') >= 3 and 'saved-copy only host (never contacted)' in pol)

# ---- 2. zero requests to never-contact hosts, every door, every loadable built tool
try:
    import requests  # noqa: F401
    HAVE_REQ = True
except ImportError:
    HAVE_REQ = False
    print('NOTE: requests is missing here; the live-door checks are skipped (static checks only)')
if HAVE_REQ:
    tools = {}
    for t in ('kpc_parcels', 'kpc_sitemaps', 'kpc_inspire', 'kpc_trail_lines'):
        try:
            tools[t] = load(T / t / f'{t}.py', t + '_nov11')
        except ImportError as e:   # kpc_trail_lines needs shapely; where it is missing, its copy of the reader is checked by build --check
            print(f'NOTE: {t} not loadable here ({e}); its polite block is identical to the others (build --check above)')
    for t, m in tools.items():
        sent = []

        def rec(method, url, **k):
            sent.append(url)
            if 'hop.example.invalid' in url and not url.endswith('/robots.txt'):
                return _R(302, hd={'Location': 'https://services2.arcgis.com/x/arcgis/rest/services/P/FeatureServer/0?f=json'}, url=url)
            return _R(404, url=url)
        w = m.Polite(cache=None, log=lambda *a: None)
        w.s.request = rec
        w._wait = lambda *a, **k: None
        refused = all(w.get(u)[0] == 'banned' for u in NEVER)
        for u in NEVER:
            w.robots_for(u); w._cached(u); w._raw(u); w._one(u)
        w.get('https://hop.example.invalid/layer')
        bad = [u for u in sent if is_never(u)]
        check(f'{t}: get() refuses every never-contact form, and get / robots_for / _cached / _raw / _one / a redirect hop send '
              f'zero requests to them ({len(sent)} other request(s))', refused and not bad)
        check(f'{t}: its own polite_selftest passes', m.polite_selftest() == [])

# ---- 3. kpc_parcels: a whole park run on a fake web
if HAVE_REQ and 'kpc_parcels' in tools:
    kp = tools['kpc_parcels']
    LAT, LON = 37.75, -87.10       # a made-up Kentucky pin near the Ohio River
    COUNTY = {'features': [{'attributes': {'GEOID': '21059', 'NAME': 'Daviess County', 'STATE': '21', 'BASENAME': 'Daviess'}}]}
    PLACE = {'features': [{'attributes': {'NAME': 'Owensboro city', 'BASENAME': 'Owensboro'}}]}
    EXT = [[-87.5, 37.5], [-86.8, 38.0]]
    HITS = [  # ArcGIS Online search hits, in the order the search gives them
        {'title': 'Daviess County Parcels', 'url': 'https://services5.arcgis.com/AbC123/arcgis/rest/services/Daviess_Parcels/FeatureServer/0',
         'extent': EXT, 'orgId': 'AbC123', 'owner': 'daviess_county_gis', 'accessInformation': 'Daviess County Fiscal Court'},
        {'title': 'Parcel Boundaries of Indiana Current', 'url': 'https://gisdata.in.gov/server/rest/services/Hosted/Parcel_Boundaries_of_Indiana_Current/FeatureServer/0',
         'extent': [[-88.1, 37.7], [-84.7, 41.8]], 'owner': 'in_gio', 'accessInformation': 'State of Indiana, Geographic Information Office'},
        {'title': 'Daviess County PVA Parcels', 'url': 'https://gis.daviesspva.org/server/rest/services/PVA/Parcels/MapServer/0',
         'extent': EXT, 'owner': 'dcgis', 'accessInformation': 'Daviess County PVA'},
    ]
    LAYER = {'name': 'Parcels', 'geometryType': 'esriGeometryPolygon',
             'fields': [{'name': 'PARCELID'}, {'name': 'OWNER'}, {'name': 'ACRES'}]}
    RING = [[LON - .001, LAT - .001], [LON + .001, LAT - .001], [LON + .001, LAT + .001], [LON - .001, LAT + .001], [LON - .001, LAT - .001]]
    PARCEL = {'features': [{'attributes': {'PARCELID': 'P-1', 'OWNER': 'CITY OF OWENSBORO', 'ACRES': 12.5}, 'geometry': {'rings': [RING]}}]}

    def run_park(max_tries, known=None):
        sent = []

        def rec(method, url, **k):
            sent.append(url)
            u = url
            if u.endswith('/robots.txt'):
                return _R(404, url=u)
            body = None
            if 'State_County/MapServer/1/query' in u: body = COUNTY
            elif 'Places_CouSub' in u: body = PLACE
            elif 'sharing/rest/search' in u: body = {'results': HITS}
            elif 'sharing/rest/portals/' in u: body = {'name': 'Daviess County Fiscal Court'}
            elif 'gis.daviesspva.org' in u and '/MapServer/0?' in u: body = LAYER
            elif 'gis.daviesspva.org' in u and '/MapServer/0/query' in u:
                body = PARCEL if 'esriGeometryPoint' in u else {'features': []}
            elif 'gisdata.in.gov' in u and '/FeatureServer/0?' in u: body = LAYER
            elif 'gisdata.in.gov' in u and '/query' in u: body = {'features': []}
            if body is None:
                return _R(404, url=u)
            return _R(200, json.dumps(body).encode(), {'Content-Type': 'application/json'}, u)
        w = kp.Polite(cache=None, log=lambda *a: None)
        w.s.request = rec
        w._wait = lambda *a, **k: None
        args = types.SimpleNamespace(max_tries=max_tries, owner_names='gov')
        layers, no_layer = {}, {}
        row = kp.do_park({'ref': 'TEST-1', 'name': 'Test Park', 'lat': LAT, 'lon': LON, 'county_fips': None}, w,
                         kp.Finder(w, lambda *a: None), known or {}, layers, no_layer, 'X', args, set(), lambda *a: None)
        return row, sent

    row, sent = run_park(1, known={'21059': 'https://services3.arcgis.com/Zz9/arcgis/rest/services/Old/FeatureServer/0'})
    check('kpc_parcels park run: zero requests to never-contact hosts (a --known services3 layer, a services5 search hit; robots.txt '
          f'included); {len(sent)} other request(s)', not [u for u in sent if is_never(u)])
    check('kpc_parcels park run: the other state\'s statewide layer (Indiana, for a Kentucky county) is never asked',
          not [u for u in sent if 'gisdata.in.gov' in u])
    check('kpc_parcels park run with --max-tries 1: the county\'s own government layer is still found (the never-contact and '
          'other-state hits no longer use up the try)', (row or {}).get('layer_url') == HITS[2]['url'] and row.get('parcel_id') == 'P-1')
    # (the order matters: the Indiana hit scores 4 (.gov host + a State office), the services5 copy and the county's own layer 3 each, in
    # that order; before this change those two hits used up --max-tries 1 and 2 and the county's layer was never reached)
    row1, _ = run_park(2)
    check('kpc_parcels: the same answer with --max-tries 2', (row1 or {}).get('layer_url') == HITS[2]['url'])
    row0, _ = run_park(6)
    check('kpc_parcels: the same answer with --max-tries 6', (row0 or {}).get('layer_url') == HITS[2]['url'])
    # the acceptance rules did not move: a wrong-state layer under which the pin has no parcel is still refused, and so is a zoning layer
    HITS[2] = dict(HITS[2], title='Daviess County Zoning', url='https://gis.daviesspva.org/server/rest/services/PVA/Zoning/MapServer/0')
    row2, sent2 = run_park(6)
    check('kpc_parcels: with only a zoning layer and never-contact / other-state hits left, the park is "no layer" (nothing weaker)',
          row2 and row2.get('layer_url') is None and 'zoning' in row2['why'] and not [u for u in sent2 if is_never(u)])
    check('kpc_parcels: the no-layer reason counts the skipped hits (never-contact hosts, another state)',
          row2 and 'saved-copy-only hosts not contacted' in row2['why'] and 'of another state skipped' in row2['why'])
    CASES = (('Parcel_Boundaries_of_Indiana_Current', 'Kentucky', True), ('Ohio County KY Parcels', 'Kentucky', False),
             ('Washington County Parcels', 'Kentucky', False), ('West Virginia parcels', 'Virginia', True),
             ('Virginia Parcels', 'West Virginia', True), ('Kansas City parcels', 'Missouri', False),
             ('Indiana County Parcels', 'Pennsylvania', False), ('Parcels', 'Kentucky', False),
             ('Kentucky and Indiana parcels', 'Kentucky', False))
    for text, own, want in (CASES if hasattr(kp, 'other_state_only') else ()):
        check(f'other_state_only({text!r}, {own!r}) is {want}', kp.other_state_only(text, own) is want)
    check('kpc_parcels has other_state_only()', hasattr(kp, 'other_state_only'))

# ---- 4. picture tracer --offline: the cache rule (pure Python)
sys.path.insert(0, str(D))
TL = load(D / 'kpc_trace_limits.py', 'kpc_trace_limits_nov11')
full = dict(version='0.3.0', pin=[38.0, -85.0], half_km=5.0, skipped=[])
part = dict(full, skipped=['water'])
check('normal run: a full saved basemap for the same box and version is used', TL.cached_basemap_ok(full, 38.0, -85.0, 5.0, '0.3.0')[0])
check('normal run: a partial saved basemap is NOT used (asked again, owner call Nov 7, unchanged)',
      not TL.cached_basemap_ok(part, 38.0, -85.0, 5.0, '0.3.0')[0])
check('--offline: a partial saved basemap is used as it is (its skipped list still reaches the flags)',
      TL.cached_basemap_ok(part, 38.0, -85.0, 5.0, '0.3.0', offline=True)[0])
for what, d, a in (('another pin', part, (38.1, -85.0, 5.0)), ('another box size', part, (38.0, -85.0, 6.0)),
                   ('another tracer version', dict(part, version='0.2.0'), (38.0, -85.0, 5.0)), ('no basemap', None, (38.0, -85.0, 5.0))):
    check(f'--offline still refuses a saved basemap for {what}', not TL.cached_basemap_ok(d, *a, '0.3.0', offline=True)[0])
src = (D / 'kpc_trace_picture.py').read_text(encoding='utf-8')
check('the picture tracer has --offline, sends no request with it (session get replaced) and runs its offline selftest',
      '"--offline"' in src and 'http.s.get = _offline' in src and '_offline_selftest()' in src)
for name, val in (('MAX_FIT_M', '50.0'), ('MIN_POINTS', '3'), ('LINE_MIN_Z', '2.0'), ('PIN_MAX_OUTSIDE_M', '1000')):
    check(f'picture gate {name} = {val} (unchanged)', f'\n{name} = {val}' in src)
check('better-than-chance defaults unchanged (ratio 1.5, margin 2.0)',
      "'KPC_TRACE_CHANCE_RATIO': '1.5', 'KPC_TRACE_CHANCE_MARGIN': '2.0'" in (D / 'kpc_trace_limits.py').read_text(encoding='utf-8'))

# ---- 5. the hosts list (kpc_trace_hosts.py / kpc_trace_picture.py --list-hosts): no request of any kind to make it
import socket, tempfile  # noqa: E402
TH = load(D / 'kpc_trace_hosts.py', 'kpc_trace_hosts_nov11')
dialled = []
_real_connect = socket.socket.connect


def _no_connect(self, addr, *a, **k):
    dialled.append(addr)
    raise OSError('test: no network')
socket.socket.connect = _no_connect
with tempfile.TemporaryDirectory() as td:
    base = pathlib.Path(td)
    (base / 'cache').mkdir()
    idx = {'US-0001': {'ref': 'US-0001', 'source_url': 'https://mdc.mo.gov/a.pdf'},
           'CA-0002': {'ref': 'CA-0002', 'source_url': 'https://open.yukon.ca/b.pdf'},
           'US-0003': {'ref': 'US-0003', 'source_url': 'https://services1.arcgis.com/x/files/c.pdf', 'geo': {'affine': [1, 0, 0, 0, 1, 0]}},
           'US-0004': {'ref': 'US-0004', 'source_url': 'https://apps.fs.usda.gov/d.pdf'},
           'US-0005': {'ref': 'US-0005', 'source_url': 'https://www.fs.usda.gov/e.pdf'}}
    (base / 'index.json').write_text(json.dumps(idx))
    (base / 'pins.json').write_text(json.dumps({k: [38.0, -85.0] for k in idx}))
    (base / 'cache' / 'US-0005_basemap.json').write_text(json.dumps({'skipped': ['water']}))
    txt, p = TH.report(str(base))
    hosts = p['hosts']
    check('hosts list: US maps ask tigerweb, hydro.nationalmap.gov (robots.txt only) and gis.blm.gov; Canada asks geo.statcan.gc.ca',
          set(h for h, e in hosts.items() if e['kind'] == 'basemap') == {'tigerweb.geo.census.gov', 'hydro.nationalmap.gov', 'gis.blm.gov', 'geo.statcan.gc.ca'})
    check('hosts list: a GeoPDF map needs no basemap host; a partial cached basemap is asked again in a normal run',
          p['geopdf'] == 1 and 'US-0003' not in hosts['tigerweb.geo.census.gov']['refs'] and 'US-0005' in hosts['tigerweb.geo.census.gov']['refs'])
    check('hosts list: every basemap host is on the tracer allow list and none is a never-contact host',
          all(e['tracer_allow_list'] and not e['never_contact'] for e in hosts.values() if e['kind'] == 'basemap'))
    check('hosts list: map-file hosts on services*.arcgis.com / apps.fs.usda.gov are named never-contact and refused by kpc_host_rules',
          hosts['services1.arcgis.com']['never_contact'] and hosts['services1.arcgis.com']['host_rules'].startswith('REFUSED')
          and hosts['apps.fs.usda.gov']['never_contact'] and hosts['apps.fs.usda.gov']['host_rules'].startswith('REFUSED')
          and not hosts['www.fs.usda.gov']['never_contact'])
    check('hosts list: the printout names them on its last line', 'services1.arcgis.com' in txt.splitlines()[-1] and 'apps.fs.usda.gov' in txt.splitlines()[-1])
    _t, po = TH.report(str(base), offline=True)
    check('hosts list --offline: no basemap host at all', not [h for h, e in po['hosts'].items() if e['kind'] == 'basemap'])
socket.socket.connect = _real_connect
check(f'hosts list: made no network connection ({dialled})', not dialled)
check('the tracer takes its basemap hosts and addresses from kpc_trace_hosts.py and has --list-hosts',
      'from kpc_trace_hosts import (ALLOWED_BASEMAP_HOSTS' in src and "'--list-hosts' in argv" in src)

# ---- 6. matcher-input switches: on by default, each can be turned off alone, none is a gate
TLs = (D / 'kpc_trace_limits.py').read_text(encoding='utf-8')
for env in ('KPC_TRACE_BAND_JUNCTIONS', 'KPC_TRACE_BOX_MASK', 'KPC_TRACE_DARK_RING'):
    check(f'{env} is on by default and can be set to 0', TL.on(env, {}) and not TL.on(env, {env: '0'}))
check('the tracer has --off for each switch (band_junctions, box_mask, dark_ring)',
      '"band_junctions": "KPC_TRACE_BAND_JUNCTIONS"' in src and '"box_mask": "KPC_TRACE_BOX_MASK"' in src
      and '"dark_ring": "KPC_TRACE_DARK_RING"' in src and 'ap.add_argument("--off"' in src)
try:
    import cv2, numpy  # noqa: F401
    r = subprocess.run([sys.executable, '-B', str(D / 'kpc_trace_marks.py'), '--selftest'], capture_output=True, text=True, timeout=300)
    check('kpc_trace_marks.py --selftest (synthetic band roads, boxes, dark rings): ' + r.stdout.strip().splitlines()[-1],
          r.returncode == 0 and 'ALL PASS' in r.stdout)
except ImportError as e:
    print(f'NOTE: numpy / OpenCV missing here ({e}); kpc_trace_marks.py is checked by the picture-trace workflow')

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
