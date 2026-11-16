#!/usr/bin/env python3
"""Offline test, Nov 14 2026: the Kentucky State Parks alert feed (src_ky_parks) goes through the bot's Manners: robots.txt
check + 2 s gap per host. robots 200 = obey; 404/410 = allowed; Nov 15: 401/403 = no rules (the engine 3.6.2 rule); a Disallow = not read; 5xx / no answer = not read
this run. A refused read is never a clean read: the source is recorded as failed/skipped and its last items stay.
The real Manners runs; only urlopen is replaced (robots.txt answers per case, the feed answers one alert). No real network.
Run: python3 -B tests/test_closures_ky_robots_nov14.py"""
import contextlib, importlib.util, io, json, os, pathlib, socket, sys, tempfile, time, urllib.error, urllib.request

R = pathlib.Path(__file__).resolve().parents[1]; S = R / '.github' / 'scripts'
sys.path.insert(0, str(S))
ok = True


def check(c, msg):
    global ok
    print(('PASS ' if c else 'FAIL ') + msg); ok = ok and bool(c)


def _no_net(*a, **k): raise OSError('no network in this test')


socket.getaddrinfo = socket.create_connection = _no_net
socket.socket.connect = lambda self, *a: _no_net(*a)

tmp = pathlib.Path(tempfile.mkdtemp(prefix='kpc-ky-robots-'))
os.environ.update({'OFFLINE': '1', 'OUT': str(tmp / 'closures'), 'LINKS': str(tmp / 'nolinks'), 'BROWSER': '0', 'KPC_MANNERS_CACHE': ''})
spec = importlib.util.spec_from_file_location('kpc_closures_bot', S / 'kpc_closures_bot.py')
CB = importlib.util.module_from_spec(spec); sys.modules['kpc_closures_bot'] = CB; spec.loader.exec_module(CB)
CB.OFFLINE = False   # this test reaches src_ky_parks' Manners gate; urlopen below is the only "network"

FEED = 'https://parks.ky.gov/api/alerts'
ROBOTS = {'st': 200, 'txt': b''}
ASKED = []


class _Resp(io.BytesIO):
    def __init__(self, body, url, status=200):
        super().__init__(body); self.status = status; self.headers = {}; self._u = url
    def geturl(self): return self._u
    def __enter__(self): return self
    def __exit__(self, *a): return False


def fake_urlopen(req, timeout=None):
    u = req.full_url if hasattr(req, 'full_url') else str(req)
    ASKED.append((time.time(), u))
    if u.endswith('/robots.txt'):
        st = ROBOTS['st']
        if st == 'unreachable': raise urllib.error.URLError('no route')
        if st != 200: raise urllib.error.HTTPError(u, st, 'x', {}, None)
        return _Resp(ROBOTS['txt'], u)
    body = json.dumps({'value': [{'Title': 'Test Park campground closed', 'Text': 'The campground is closed for repairs.', 'CtaLink': 'https://parks.ky.gov/x', 'PublicationDate': '2026-11-13'}]}).encode()
    return _Resp(body, u)


urllib.request.urlopen = fake_urlopen
CB.urllib.request.urlopen = fake_urlopen

# a Kentucky area with only this source (sources.json), one item kept from an earlier good read
(tmp / 'closures').mkdir(parents=True, exist_ok=True)
json.dump({'sources': [{'id': 'ky-parks', 'agency': 'Kentucky State Parks', 'url': FEED, 'how': 'ky-parks', 'area': 'US-KY'}]}, open(tmp / 'closures' / 'sources.json', 'w'))
_orig_sources_for = CB.sources_for
CB.sources_for = lambda area: [x for x in _orig_sources_for(area) if x[0] == 'ky-parks']   # only the feed under test


def run(robots_st, robots_txt=b''):
    """one process_area on US-KY with a fresh Manners; -> (source record, kept ky-parks items, feed asked?, seconds robots->feed)"""
    ROBOTS.update(st=robots_st, txt=robots_txt); ASKED.clear()
    old = {'id': 'ky-old-1', 'src': 'ky-parks', 'ref': 'US-1234', 'class': 'part', 'kind': 'Closure', 'details': 'The lodge is closed until further notice.',
           'seen': '2026-11-01', 'to': '2099-01-01'}
    json.dump({'ver': CB.VER, 'items': [old], 'sources': {'ky-parks': {'ok': True, 'last_ok': '2026-11-01', 'n': 1}}}, open(tmp / 'closures' / 'US-KY.json', 'w'))
    CB.M = CB.Manners(CB.BOT, {})
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try: CB.process_area(CB._PlainKey(), 'US-KY', {'areas': {}, 'hosts': {}}, {})
        except Exception as e: print('process_area stopped:', type(e).__name__, e)
    d = json.load(open(tmp / 'closures' / 'US-KY.json'))
    s = (d.get('sources') or {}).get('ky-parks') or {}
    kept = [it for it in d.get('items', []) if it.get('src') == 'ky-parks']
    feed = [t for t, u in ASKED if u == FEED]; rob = [t for t, u in ASKED if u.endswith('/robots.txt')]
    gap = (feed[0] - rob[0]) if feed and rob else None
    return s, kept, bool(feed), gap, buf.getvalue()


check([x[0] for x in CB.sources_for('US-KY')] == ['ky-parks'], 'setup: US-KY has the parks.ky.gov feed source')

# robots.txt 200 that allows: the feed is read, AFTER the robots read and at least the 2 s gap later; a clean read
s, kept, asked, gap, log = run(200, b'User-agent: *\nAllow: /\n')
check(asked and s.get('ok') is True, f'robots 200 allow: the feed is read and the source is clean ({s.get("why")!r})')
check(gap is not None and gap >= 1.9, f'robots 200 allow: 2 s gap between robots.txt and the feed on the same host ({gap})')

# robots.txt 404 / 410: no rules, allowed; Nov 15: 401 / 403 = "unavailable" = no rules too (the store engine 3.6.2 rule, one rule everywhere)
for st in (404, 410, 401, 403):
    s, kept, asked, gap, log = run(st)
    check(asked and s.get('ok') is True, f'robots {st}: allowed, the feed is read ({s.get("why")!r})')

# robots.txt 200 with a Disallow for the feed path: not read, failed (not clean), old item kept
for st, txt, name in ((200, b'User-agent: *\nDisallow: /api/\n', 'Disallow /api/'), (200, b'User-agent: *\nDisallow: /\n', 'Disallow whole site')):
    s, kept, asked, gap, log = run(st, txt)
    check(not asked, f'robots {name}: the feed is NOT asked')
    check(s.get('ok') is False and s.get('why', '').startswith('robots') and s.get('skipped') is False and s.get('fails') == 1,
          f'robots {name}: recorded as a failed source (why {s.get("why")!r}, skipped {s.get("skipped")}, fails {s.get("fails")})')
    check([it['id'] for it in kept] == ['ky-old-1'] and s.get('last_ok') == '2026-11-01', f'robots {name}: the old item stays, last good read unchanged')

# robots.txt 5xx / unreachable: not read this run, skipped (read again next run), old item kept, no clean read
for st in (500, 503, 'unreachable'):
    s, kept, asked, gap, log = run(st)
    check(not asked, f'robots {st}: the feed is NOT asked')
    check(s.get('ok') is False and s.get('skipped') is True and s.get('why', '').startswith('robots-unreadable'),
          f'robots {st}: recorded as skipped, read again next run (why {s.get("why")!r})')
    check([it['id'] for it in kept] == ['ky-old-1'] and s.get('last_ok') == '2026-11-01', f'robots {st}: the old item stays, last good read unchanged')

# a stub Manners that says 'robots-unreadable' / 'robots' without any request (the bot only asks it, never urlopen)
class StubM(CB.Manners):
    def __init__(self, word): super().__init__(CB.BOT, {}); self.word = word
    def robots_ok(self, u):
        rk = self.rkey(u); self.robots[rk] = False
        if self.word == 'robots': self.robots_disallow = {rk}
        return False
for word in ('robots-unreadable', 'robots'):
    ASKED.clear()
    json.dump({'ver': CB.VER, 'items': [{'id': 'ky-old-1', 'src': 'ky-parks', 'ref': 'US-1234', 'class': 'part', 'kind': 'Closure', 'details': 'The lodge is closed until further notice.', 'seen': '2026-11-01', 'to': '2099-01-01'}],
               'sources': {'ky-parks': {'ok': True, 'last_ok': '2026-11-01', 'n': 1}}}, open(tmp / 'closures' / 'US-KY.json', 'w'))
    CB.M = StubM(word)
    with contextlib.redirect_stdout(io.StringIO()): CB.process_area(CB._PlainKey(), 'US-KY', {'areas': {}, 'hosts': {}}, {})
    d = json.load(open(tmp / 'closures' / 'US-KY.json')); s = d['sources']['ky-parks']
    check(not ASKED and s.get('ok') is False and s.get('why', '').startswith(word) and [it['id'] for it in d['items'] if it['src'] == 'ky-parks'] == ['ky-old-1'],
          f'stub Manners {word!r}: no request, source not clean, old item kept ({s.get("why")!r})')

check(not [u for t, u in ASKED if 'parks.ky.gov' not in u], 'no host but parks.ky.gov was asked')
print('ALL PASS' if ok else 'SOME FAILED'); sys.exit(0 if ok else 1)
