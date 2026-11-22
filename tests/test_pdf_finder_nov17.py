#!/usr/bin/env python3
"""PDF finder, checked with NO network (KPC owner, 2026-11-17; Handoff 3 proof 2 and part of proof 4). The real kpc_manners.Manners
runs (robots.txt per URL path, the host rules, pacing, back-off) against a fake urlopen; every socket connect is refused, so a
request that slipped past the fake would fail the test.
  1. given a saved copy of an agency page (its Maps section filled in by script), the right PDF is queued, with its terms, and
     the page itself costs no request (stored copy first); a save-map request in the picture-maps rule's own format is written
  2. a blocked host (extra-blocked-hosts.txt), a saved-copy-only host and a house never-contact host: no request at all, robots.txt included
  3. a disallowed path: robots.txt Disallow on the map's path -> found but not queued; a robots-disallowed-layers.csv prefix -> no request
  4. a 429: the host is parked for the run, nothing is queued, the next park on that host makes no request; robots.txt 429 / 503 -> nothing fetched
  5. robots.txt 404 / 403 = no rules (RFC 9309 2.3.1.3, the merged Nov 15 rule): the page is read
  6. the chain order inside the finder: stored -> portal -> agency page -> web search; the first hit stops it
  7. the park budget (one or two requests, never a crawl) and the per-host hour cap from fetch-settings.json
  8. fetch-settings.json / the blocked lists missing -> the finder does not start (exit 2)
  9. no manners code of its own: robots is never parsed here, kpc_manners is imported, kpc_manners.py is unchanged against main
Prints PASS / FAIL lines, ends ALL PASS / SOME FAILED."""
import json, os, pathlib, socket, subprocess, sys, tempfile, time, urllib.error, urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
S = ROOT / '.github/scripts'
FX = ROOT / 'tests/fixtures/trace-hold-nov17'
sys.path.insert(0, str(S))
os.environ.pop('KPC_MANNERS_CACHE', None); os.environ.pop('KPC_FINDER_SEARCH_URL', None)
ok = True


def check(msg, c):
    global ok
    ok &= bool(c)
    print(('PASS ' if c else 'FAIL ') + msg, flush=True)


def _no_net(*a, **k): raise OSError('test: no network')
socket.socket.connect = _no_net
socket.create_connection = _no_net
time.sleep = lambda s: None

CALLS = []
ROUTES = {}


class Resp:
    def __init__(self, url, status, body, headers):
        self.url, self.status, self._b, self.headers = url, status, body, headers
    def __enter__(self): return self
    def __exit__(self, *a): return False
    def read(self, n=-1): return self._b if n is None or n < 0 else self._b[:n]
    def geturl(self): return self.url


def fake_urlopen(req, timeout=None):
    u = req.full_url if hasattr(req, 'full_url') else str(req)
    CALLS.append(u)
    st, body, hd = ROUTES.get(u, (404, b'', {}))
    if st >= 400: raise urllib.error.HTTPError(u, st, 'test', hd, None)
    return Resp(u, st, body if isinstance(body, bytes) else body.encode(), dict({'content-type': 'text/html'}, **hd))


urllib.request.urlopen = fake_urlopen
import kpc_manners  # noqa: E402
import kpc_pdf_finder as PF  # noqa: E402

SET = PF.load_settings(FX / 'fetch-settings.json')
BLK = PF.load_blocked_hosts(FX / 'extra-blocked-hosts.txt')
DIS = PF.load_disallowed_layers(FX / 'robots-disallowed-layers.csv')
check(f"fetch-settings.json read: {SET['per_hour']}/h, {SET['per_day']}/day, {SET['gap_s']:g} s, {SET['strikes']} failures, apps.fs.usda.gov {SET['host_gap'].get('apps.fs.usda.gov')} s",
      (SET['per_hour'], SET['per_day'], SET['gap_s'], SET['strikes'], SET['host_gap'].get('apps.fs.usda.gov')) == (200, 1500, 2.0, 3, 10.0))


def finder(saved=None, portals=None, search=None, settings=None, docs=None, pic=None, park_max=6):
    M = kpc_manners.Manners('KPC PDF finder (test)', {}, gap=SET['gap_s'], strikes_out=SET['strikes'])
    return PF.Finder(settings or SET, BLK, DIS, PF.SavedCopies(saved), manners=M, portals=portals or {}, search_url=search or '',
                     picture_maps=pic or {}, docs_dir=docs, state={}, today='2026-11-17', park_max=park_max)


ROBOTS_OK = (200, 'User-agent: *\nDisallow: /private/\n', {'content-type': 'text/plain'})
PINE = {'ref': 'US-9001', 'name': 'Pine Lake State Park', 'area': 'US-ZZ', 'website': 'https://parks.example.gov/pine-lake', 'agency': 'Example State Parks'}

# 1. saved copy of the agency page -> the right PDF queued, no page request
CALLS.clear(); ROUTES.clear(); ROUTES['https://parks.example.gov/robots.txt'] = ROBOTS_OK
f = finder(saved=FX / 'saved')
row = f.find(PINE)
q = row.get('queued') or {}
check(f"1. saved agency page: the park map is queued ({q.get('url')}), not the annual report or the camping rules",
      q.get('url') == 'https://parks.example.gov/maps/pine-lake-park-map.pdf' and q.get('found_by') == 'agency page')
check(f"1. its terms come from the page ({q.get('terms', '')[:60]}...)", 'Terms of use' in (q.get('terms') or ''))
check(f"1. the page came from the stored copy: no page request (calls: {CALLS})", 'https://parks.example.gov/pine-lake' not in CALLS
      and f.r['served_from_stored_copy'] == 1 and CALLS == ['https://parks.example.gov/robots.txt'])
check('1. robots.txt was asked for the queued map path and allows it', q.get('robots') == 'yes')
with tempfile.TemporaryDirectory() as td:
    f.write(td)
    sm = json.load(open(pathlib.Path(td) / 'save-map/pdf-finder-US-9001.json'))
    rc = json.load(open(pathlib.Path(td) / 'receipt.json'))
check(f"1. a save-map request in the picture-maps rule's format ({sm})", sm['kind'] == 'save-map' and sm['ref'] == 'US-9001'
      and sm['url'].endswith('pine-lake-park-map.pdf') and sm['pages'] == 1 and set(sm) >= {'chat', 'name', 'agency', 'hint'})
check(f"1. receipt: queued 1, stored 1, requests {rc['requests_made']}, POTA requests {rc['pota_requests']}", rc['queued'] == 1
      and rc['served_from_stored_copy'] == 1 and rc['pota_requests'] == 0 and rc['requests_made'] == 1)   # the robots.txt read for the map's path

# 2. blocked hosts: no request of any kind
for site, what in (('https://www.blocked.example.gov/park', 'extra-blocked-hosts.txt'), ('https://sub.blocked.example.gov/park', 'a sub-host of a blocked host'),
                   ('https://apps.fs.usda.gov/park', 'saved-copy-only host (kpc_host_rules)'), ('https://services3.arcgis.com/x/park', 'services*.arcgis.com'),
                   ('https://gis.nature.cz/park', 'house never-contact host'), ('https://pota.app/#/park/US-1', 'POTA (door only)')):
    CALLS.clear(); ROUTES.clear()
    f = finder(); row = f.find(dict(PINE, website=site))
    check(f'2. {what}: refused, no request at all, robots.txt included (calls {CALLS})', not CALLS and not row.get('queued')
          and f.r['refused']['blocked host'] >= 1 and f.receipt()['pota_requests'] == 0)

# 3. disallowed path
CALLS.clear(); ROUTES.clear()
ROUTES['https://parks.example.gov/robots.txt'] = (200, 'User-agent: *\nDisallow: /maps/\n', {'content-type': 'text/plain'})
f = finder(saved=FX / 'saved'); row = f.find(PINE)
check(f"3. robots.txt Disallow: /maps/ -> the map is found but NOT queued (log: {row['log'][-1][:90]})", not row.get('queued') and f.r['refused']['disallowed path'] == 1)
CALLS.clear(); ROUTES.clear()
f = finder(); row = f.find(dict(PINE, website='https://parks.example.gov/arcgis/rest/services/Private/MapServer'))
check(f'3. a robots-disallowed-layers.csv prefix: no request (calls {CALLS})', not CALLS and f.r['refused']['disallowed path'] == 1)
CALLS.clear(); ROUTES.clear()
ROUTES['https://parks.example.gov/robots.txt'] = (200, 'User-agent: *\nDisallow: /pine-lake\n', {'content-type': 'text/plain'})
f = finder(); row = f.find(PINE)
check(f'3. the agency page itself disallowed: only robots.txt read, page never asked (calls {CALLS})', CALLS == ['https://parks.example.gov/robots.txt'] and not row.get('queued'))

# 4. 429
CALLS.clear(); ROUTES.clear()
ROUTES['https://parks.example.gov/robots.txt'] = ROBOTS_OK
ROUTES['https://parks.example.gov/pine-lake'] = (429, b'', {'Retry-After': '30'})
f = finder(); row = f.find(PINE)
n1 = len(CALLS)
row2 = f.find(dict(PINE, ref='US-9002', name='Cedar Hollow Natural Area', website='https://parks.example.gov/cedar-hollow'))
check(f'4. a 429: nothing queued, the host is parked for the run ({f.parked.get("parks.example.gov", "")[:60]})', not row.get('queued') and 'parks.example.gov' in f.parked)
check(f'4. the next park on that host makes no request ({len(CALLS) - n1} after the 429)', len(CALLS) == n1 and not row2.get('queued')
      and f.r['refused']['429 / host parked'] == 2)
for code in (429, 503):
    CALLS.clear(); ROUTES.clear(); ROUTES['https://parks.example.gov/robots.txt'] = (code, b'', {})
    f = finder(); row = f.find(PINE)
    check(f'4. robots.txt {code}: rules unknown, the page is not fetched (calls {CALLS})', CALLS == ['https://parks.example.gov/robots.txt'] and not row.get('queued'))

# 5. robots.txt 404 / 403 = no rules
for code in (404, 403):
    CALLS.clear(); ROUTES.clear(); ROUTES['https://parks.example.gov/robots.txt'] = (code, b'', {})
    ROUTES['https://parks.example.gov/pine-lake'] = (200, (FX / 'agency/pine-lake.html').read_bytes(), {})
    f = finder(); row = f.find(PINE)
    check(f'5. robots.txt {code} = "unavailable" = no rules: the page is read and the map queued', (row.get('queued') or {}).get('url', '').endswith('pine-lake-park-map.pdf'))

# 6. the chain order
CALLS.clear(); ROUTES.clear()
ROUTES['https://data.example.gov/robots.txt'] = (404, b'', {}); ROUTES['https://parks.example.gov/robots.txt'] = ROBOTS_OK
portal = {'US-ZZ': {'kind': 'ckan', 'host': 'data.example.gov'}}
pu = 'https://data.example.gov/api/3/action/package_search?q=Pine%20Lake%20State%20Park%20map&rows=10'
ROUTES[pu] = (200, json.dumps({'result': {'results': [{'title': 'Pine Lake State Park', 'license_title': 'Open Government Licence',
             'resources': [{'format': 'PDF', 'name': 'Pine Lake park map', 'url': 'https://parks.example.gov/maps/pine-lake-boundary-map.pdf'}]}]}}), {})
f = finder(portals=portal); row = f.find(PINE)
check(f"6. the portal goes first: its PDF queued (found_by {row.get('queued', {}).get('found_by')}) and the agency page never asked",
      row.get('queued', {}).get('found_by') == 'portal' and 'https://parks.example.gov/pine-lake' not in CALLS and CALLS[0].startswith('https://data.example.gov/'))
check(f"6. the portal's licence is the terms ({row['queued']['terms']})", row['queued']['terms'] == 'Open Government Licence')
CALLS.clear(); ROUTES[pu] = (200, json.dumps({'result': {'results': []}}), {})
ROUTES['https://parks.example.gov/cedar-hollow'] = (200, (FX / 'agency/cedar-hollow.html').read_bytes(), {})
ROUTES['https://parks.example.gov/cedar-hollow/maps'] = (200, (FX / 'agency/cedar-hollow-maps.html').read_bytes(), {})
cedar = dict(PINE, ref='US-9002', name='Cedar Hollow Natural Area', website='https://parks.example.gov/cedar-hollow')
cu = 'https://data.example.gov/api/3/action/package_search?q=Cedar%20Hollow%20Natural%20Area%20map&rows=10'
ROUTES[cu] = (200, json.dumps({'result': {'results': []}}), {})
f = finder(portals=portal); row = f.find(cedar)
order = [c for c in CALLS if not c.endswith('/robots.txt')]
check(f"6. portal empty -> the agency page, then its one Maps sub-page; the agency's own boundary PDF queued, the off-site one not (order {order})",
      order == [cu, 'https://parks.example.gov/cedar-hollow', 'https://parks.example.gov/cedar-hollow/maps']
      and row.get('queued', {}).get('url') == 'https://parks.example.gov/maps/cedar-hollow-boundary.pdf' and f.r['refused']['not the agency site'] == 1)
CALLS.clear()
ROUTES['https://parks.example.gov/cedar-hollow/maps'] = (200, b'<html>nothing</html>', {})
ROUTES['https://search.example.gov/robots.txt'] = (404, b'', {})
su = 'https://search.example.gov/s?q=%22Cedar%20Hollow%20Natural%20Area%22%20map%20pdf%20site%3Aexample.gov'
ROUTES[su] = (200, b'<a href="https://parks.example.gov/maps/cedar-hollow-map.pdf">Cedar Hollow map</a>', {})
f = finder(portals=portal, search='https://search.example.gov/s?q={q}'); row = f.find(cedar)
order = [c for c in CALLS if not c.endswith('/robots.txt')]
check(f"6. only then the web search ({row.get('queued', {}).get('found_by')}), last in the order", order[-1] == su and row.get('queued', {}).get('found_by') == 'web search')
CALLS.clear()
f = finder(portals=portal, search=''); row = f.find(cedar)
check('6. web search off by default (no KPC_FINDER_SEARCH_URL): nothing asked of a search site', not any('search.example.gov' in c for c in CALLS) and f.r['web_search'].startswith('off'))
with tempfile.TemporaryDirectory() as td:
    d = pathlib.Path(td); (d / 'US-ZZ.json').write_text(json.dumps({'parks': {'US-9001': {'page': 'https://parks.example.gov/pine-lake',
                                                        'map': {'url': 'https://parks.example.gov/maps/stored-map.pdf'}}}}))
    CALLS.clear()
    f = finder(portals=portal, docs=d); row = f.find(PINE)
    check(f"6. stored first: the docs bot's stored map link is queued with no request at all (calls {CALLS})",
          row.get('queued', {}).get('found_by') == 'stored' and CALLS == ['https://parks.example.gov/robots.txt'] and f.r['served_from_stored_copy'] == 1)
    CALLS.clear()
    f = finder(portals=portal, docs=d, pic={'US-9001': {'source_url': 'https://parks.example.gov/maps/x.pdf'}}); row = f.find(PINE)
    check(f'6. a park already on picture-maps: nothing to find, no request (calls {CALLS})', not CALLS and row.get('already_saved'))

# 7. budgets
CALLS.clear(); ROUTES.clear(); ROUTES['https://parks.example.gov/robots.txt'] = ROBOTS_OK
ROUTES['https://parks.example.gov/cedar-hollow'] = (200, (FX / 'agency/cedar-hollow.html').read_bytes(), {})
ROUTES['https://parks.example.gov/cedar-hollow/maps'] = (200, b'<html>nothing</html>', {})
f = finder(park_max=2); row = f.find(cedar)
check(f"7. park budget 2: robots + page used it, the Maps sub-page is not asked; listed for a person ({f.r['for_person']})",
      'https://parks.example.gov/cedar-hollow/maps' not in CALLS and f.r['refused']['park budget'] == 1 and f.r['for_person'])
CALLS.clear()
f = finder(settings=dict(SET, per_hour=1)); row = f.find(cedar)
check(f"7. per-host hour cap from fetch-settings.json (1/h here): the second request refused ({f.r['refused']['host caps']})",
      f.r['refused']['host caps'] == 1 and 'https://parks.example.gov/cedar-hollow/maps' not in CALLS)

# 8. missing settings -> no start
with tempfile.TemporaryDirectory() as td:
    pj = pathlib.Path(td) / 'p.json'; pj.write_text('[]')
    r = subprocess.run([sys.executable, '-B', str(S / 'kpc_pdf_finder.py'), 'find', '--parks', str(pj), '--queue-dir', td,
                        '--settings', str(pathlib.Path(td) / 'none.json'), '--blocked', str(FX / 'extra-blocked-hosts.txt'),
                        '--disallowed', str(FX / 'robots-disallowed-layers.csv')], capture_output=True, text=True, env={**os.environ, 'PATH': os.environ.get('PATH', '')})
    check(f'8. fetch-settings.json missing: exit {r.returncode}, nothing written', r.returncode == 2 and not (pathlib.Path(td) / 'queue.json').exists())
    r = subprocess.run([sys.executable, '-B', str(S / 'kpc_pdf_finder.py'), 'find', '--parks', str(pj), '--queue-dir', td,
                        '--settings', str(FX / 'fetch-settings.json'), '--blocked', str(pathlib.Path(td) / 'none.txt'),
                        '--disallowed', str(FX / 'robots-disallowed-layers.csv')], capture_output=True, text=True)
    check(f'8. extra-blocked-hosts.txt missing: exit {r.returncode}', r.returncode == 2)

# 9. no manners code of its own
src = (S / 'kpc_pdf_finder.py').read_text(encoding='utf-8')
check('9. the finder never parses robots.txt itself (no robotparser, no parse_robots) and goes through kpc_manners.Manners',
      'robotparser' not in src and 'parse_robots' not in src and 'kpc_manners.Manners(' in src and 'urlopen' not in src)
import hashlib
def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
# A later edit of either file changes the pin in the same pull request, where a reviewer sees it.
MANNERS_SHA = 'd9254273ef8cfd6f596cfe91bb14d1d2836e1ef8627ae8c490b98e184e37c63f'
HOST_SHA = 'ec7efc5feec25676f89a656106278930d27d33c8467b4b3bd185739ca4818eec'
check(f'9. kpc_manners.py frozen: {MANNERS_SHA}, pin updated 22 Nov 2026',
      _sha(S / 'kpc_manners.py') == MANNERS_SHA)
check(f'9. kpc_host_rules.py frozen: {HOST_SHA}, pin updated 22 Nov 2026 (the keeper reads arcgis, owner)',
      _sha(S / 'kpc_host_rules.py') == HOST_SHA)

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
