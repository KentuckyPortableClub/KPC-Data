#!/usr/bin/env python3
"""Park page reader, 21 Nov 2026: a read that says nothing new keeps the earlier facts byte for byte; robots.txt (our own
parser, via kpc_manners) decides before any page is asked; WDPA is never asked; the keeper's saved copy is read first.
Offline: invented parks, fixtures and a local 127.0.0.1 server only. Prints PASS / FAIL and ends ALL PASS or SOME FAILED.
"""
import http.server, json, os, pathlib, shutil, sys, tempfile, threading, time

CACHE = tempfile.mkdtemp(prefix='kpc-pp-skip-')
os.environ['KPC_MANNERS_CACHE'] = CACHE
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github/scripts'))
import kpc_manners as K  # noqa: E402
import kpc_park_pages as PP  # noqa: E402

ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


TEXT = ('<html><head><title>Invented Ridge State Forest</title></head><body><h1>Invented Ridge State Forest</h1>'
        '<p>Total area: 1,234 acres</p>' + '<p>The forest has trails and a pond for walkers in every season.</p>' * 12 + '</body></html>')


def tree(t, url):
    (t / 'parkinfo').mkdir(parents=True, exist_ok=True)
    (t / 'parkinfo' / 'US-ZZ.json').write_text(json.dumps({'parks': {
        'US-9001': ['Invented Ridge State Forest', url, 'State Forest', '', '', 38.5, -85.5, 0, 0, 1]}}), encoding='utf-8')
    return PP.load_data(t)


class Fake:
    """Answers one status (or a page) for every address; records every address asked."""
    def __init__(self, answer):
        self.answer, self.calls = answer, []

    def get(self, url, rng=None, deadline=None, max_time=None):
        self.calls.append(url)
        a = self.answer
        if a == 'page':
            return 200, {'content-type': 'text/html'}, TEXT.encode(), url
        if a == 'thin':
            return 200, {'content-type': 'text/html'}, b'<html><body><div id="app"></div></body></html>', url
        if isinstance(a, int):
            return a, {}, b'no', url
        return a, {}, b'', url


def run(t, url, getter, today, out=None):
    areas, web, docs, truth = tree(t, url)
    out = out or t / 'out'
    sp = out / 'state.json'
    state = PP.load_json(sp, {})
    facts, _r = PP.read_parks(areas, web, docs, truth, getter, state, today, out_dir=str(out), state_path=str(sp), quiet=True)
    PP.merge_unchanged(str(out), facts)
    PP.write_facts(str(out), facts)
    PP.save_json(sp, state)
    return facts, out / 'facts' / 'US-ZZ.json'


URL = 'https://parks.invented.example.gov/ridge'


def no_seen(b):
    """A facts file without the 'seen' dates (27 Nov 2026: a read that is not needed only stamps the date it was seen)."""
    d = json.loads(b)
    for p in (d.get('parks') or {}).values():
        (p.get('page') or {}).pop('seen', None)
    return d
with tempfile.TemporaryDirectory() as td:
    t = pathlib.Path(td)
    _f, path = run(t, URL, Fake('page'), '2026-11-19')
    first = path.read_bytes()
    check('the first read saves the facts', b'"US-9001"' in first and b'1234' in first)
    for answer, day in ((403, '2026-12-20'), ('robots', '2026-12-21'), ('robots-unreadable', '2026-12-22'),
                        ('rest', '2026-12-23'), ('err:timeout', '2026-12-24'), ('thin', '2026-12-25')):
        st = json.loads((t / 'out' / 'state.json').read_text())
        st.get('refused', {}).clear()       # a remembered refusal would skip the ask; each kind is asked here
        (t / 'out' / 'state.json').write_text(json.dumps(st))
        g = Fake(answer)
        run(t, URL, g, day)
        # 27 Nov 2026 (owner, 26 Nov: 'a run reads only what is missing, failed or newly allowed'; NEVER_DAYS): a page read before
        # is not asked again by age, so its good facts stay; the only change is the date it was last seen
        check(f'a page read before is not asked again ({answer} never reached) and its facts stay (only "seen" added)',
              no_seen(path.read_bytes()) == no_seen(first) and g.calls == [])

with tempfile.TemporaryDirectory() as td:
    t = pathlib.Path(td)
    g = Fake('page')
    facts, path = run(t, 'https://www.protectedplanet.net/555555', g, '2026-11-19')
    check('a WDPA address is never asked', g.calls == [] and facts['US-ZZ']['US-9001']['page']['kind'] in ('refused', 'resting'))

# --- robots.txt decides before any page: a Disallow, and a robots.txt that cannot be parsed ---
hits = {}


class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        hits[(self.server.server_address[1], self.path)] = hits.get((self.server.server_address[1], self.path), 0) + 1
        mode = self.server.mode
        if self.path == '/robots.txt':
            if mode == 'deny':
                body = b'User-agent: *\nDisallow: /\n'
            else:   # too long to parse: RFC 9309's limit; our own parser refuses it, so nothing is fetched
                body = b'User-agent: *\n' + b'# ' + b'x' * (K.ROBOTS_MAX + 16) + b'\n'
            self.send_response(200); self.end_headers(); self.wfile.write(body)
            return
        self.send_response(200); self.send_header('Content-Type', 'text/html'); self.end_headers(); self.wfile.write(TEXT.encode())


servers = []
for port, mode in ((18931, 'deny'), (18932, 'unparsable')):
    s = http.server.ThreadingHTTPServer(('127.0.0.1', port), H)
    s.mode = mode
    threading.Thread(target=s.serve_forever, daemon=True).start()
    servers.append(s)
    with tempfile.TemporaryDirectory() as td:
        t = pathlib.Path(td)
        live = PP.LiveGetter({})
        live.M.gap = 0.0
        u = f'http://127.0.0.1:{port}/ridge'
        facts, path = run(t, u, live, '2026-11-19')
        kind = facts['US-ZZ']['US-9001']['page']['kind']
        if mode == 'deny':
            check(f'robots.txt {mode}: the page is never fetched', (port, '/ridge') not in hits and hits.get((port, '/robots.txt')) == 1)
            check(f'robots.txt {mode}: the park is read as refused or resting, with no facts invented',
                  kind in ('refused', 'resting') and not facts['US-ZZ']['US-9001'].get('sizes'))
        else:   # 27 Nov 2026 (RFC 9309 2.5, R-NET1): an oversized robots.txt is read up to its limit; no Disallow line = allowed
            check(f'robots.txt {mode}: its first part is read and the page no Disallow line names is fetched once',
                  hits.get((port, '/ridge')) == 1 and kind == 'html')
for s in servers:
    s.shutdown()
check('our own robots parser is what manners uses (never urllib.robotparser internals)',
      'robotparser' not in (ROOT / '.github/scripts/kpc_park_pages.py').read_text())

# --- the keeper's saved copy first ---
with tempfile.TemporaryDirectory() as td:
    t = pathlib.Path(td)
    kc = t / 'keeper'
    (kc / 'pages').mkdir(parents=True)
    (kc / 'pages' / 'ridge.html').write_text(TEXT, encoding='utf-8')
    man = {'pages': {URL: {'file': 'pages/ridge.html', 'status': 200, 'type': 'text/html'}}}
    live = Fake('page')
    g = PP.KeeperCopyGetter(man, kc, live)
    facts, path = run(t, URL, g, '2026-11-19')
    check("a page the keeper holds is read from its copy, and the agency is not asked",
          live.calls == [] and g.from_copy == 1 and facts['US-ZZ']['US-9001']['confirm']['size']['acres'] == 1234)
    first = path.read_bytes()
    g2 = PP.KeeperCopyGetter({'pages': {}}, kc, None)
    run(t, URL, g2, '2026-12-25')
    check('a page the keeper does not hold, with no live reader: no fetch, and the earlier facts stay', no_seen(path.read_bytes()) == no_seen(first))
    live3 = Fake('page')
    g3 = PP.KeeperCopyGetter({'pages': {}}, kc, live3)
    run(t, 'https://parks.invented.example.gov/other', g3, '2026-12-26', out=t / 'out2')
    check('a page the keeper does not hold goes to the live reader (manners) once', live3.calls == ['https://parks.invented.example.gov/other'])

# --- a park cut off mid-read is not saved; the parks read before it are ---
with tempfile.TemporaryDirectory() as td:
    t = pathlib.Path(td)
    (t / 'parkinfo').mkdir()
    (t / 'parkinfo' / 'US-ZZ.json').write_text(json.dumps({'parks': {
        'US-9001': ['Invented Ridge State Forest', 'https://parks.invented.example.gov/a', 'State Forest', '', '', 38.5, -85.5, 0, 0, 1],
        'US-9002': ['Invented Hollow State Forest', 'https://parks.invented.example.gov/b', 'State Forest', '', '', 38.6, -85.5, 0, 0, 1]}}))
    areas, web, docs, truth = PP.load_data(t)

    class Cut(Fake):
        def get(self, url, rng=None, deadline=None, max_time=None):
            self.calls.append(url)
            if url.endswith('/b'):
                if deadline is not None:   # 21 Nov: the run's own deadline is really reached (a download's cap alone no longer stops a run)
                    time.sleep(max(0, deadline - time.time()))
                return 'err:deadline', {}, b'', url
            return 200, {'content-type': 'text/html'}, TEXT.encode(), url
    out = t / 'out'
    state = {}
    facts, _r = PP.read_parks(areas, web, docs, truth, Cut(None), state, '2026-11-19', out_dir=str(out),
                              state_path=str(out / 'state.json'), quiet=True, deadline=time.time() + 0.5)
    saved = json.loads((out / 'facts' / 'US-ZZ.json').read_text())['parks']
    check('a park cut off mid-read is not saved; the park read before it is',
          'US-9001' in saved and 'US-9002' not in saved and state.get('stopped') == 'minutes')

shutil.rmtree(CACHE, ignore_errors=True)
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
