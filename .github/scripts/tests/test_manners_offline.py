#!/usr/bin/env python3
"""Offline tests for kpc_manners (Nov 3: bots-first patch 01 + Quality grade-bots-first A1-A12).
Local http server on 127.0.0.1 only: no outside request. A fake clock stands in for time.sleep, so the 30 s 403 pause and the
3 s Crawl-delay are checked without waiting.   Run from the repo root:  python3 .github/scripts/tests/test_manners_offline.py
"""
import glob, http.server, json, os, shutil, sys, tempfile, threading, time as _rt
CACHE = tempfile.mkdtemp(prefix='kpc_manners_cache_')
os.environ.update({'KPC_MANNERS_CACHE': CACHE, 'KPC_SLOW_HOST_DELAY': '3', 'KPC_SLOW_HOST_BUDGET': '4'})
os.environ.pop('KPC_ARCGIS_ROBOTS_EXEMPT', None); os.environ.pop('KPC_MANNERS_CACHE_ALL', None)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import kpc_manners as K  # noqa: E402


class Clock:   # virtual time: sleep() moves the clock, so waits can be measured exactly
    def __init__(self): self.t = _rt.time(); self.slept = []
    def time(self): return self.t
    def sleep(self, s): self.slept.append(s); self.t += max(0, s)
CLK = Clock(); K.time = CLK

hits = {}
MODE = {'robots': 'normal'}
class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        hits[self.path] = hits.get(self.path, 0) + 1
        port = self.server.server_address[1]
        if self.path == '/robots.txt':
            m = MODE.get(port, 'normal')
            if m == 'normal':
                b = b"User-agent: *\nCrawl-delay: 3\nDisallow: /arcgis/rest/services/secret/\nDisallow: /private/\n"
                self.send_response(200); self.end_headers(); self.wfile.write(b); return
            if m == '404': self.send_response(404); self.end_headers(); return
            if m == 'denyall':
                self.send_response(200); self.end_headers(); self.wfile.write(b"User-agent: *\nDisallow: /\n"); return
            if m == 'slowcd':
                self.send_response(200); self.end_headers(); self.wfile.write(b"User-agent: *\nCrawl-delay: 500\n"); return
            self.send_response(int(m)); self.end_headers(); return
        if self.path.startswith('/deny-long'):
            self.send_response(403); self.send_header('Retry-After', '3600'); self.end_headers(); return
        if self.path.startswith('/deny'): self.send_response(403); self.end_headers(); return
        if self.path == '/big': self.send_response(200); self.end_headers(); self.wfile.write(b'x' * 50); return
        self.send_response(200); self.send_header('Content-Type', 'text/plain'); self.end_headers(); self.wfile.write(b'ok ' + self.path.encode())
H.server_version = 'test'
srvs = []
def serve(port, mode):
    MODE[port] = mode
    s = http.server.ThreadingHTTPServer(('127.0.0.1', port), H); threading.Thread(target=s.serve_forever, daemon=True).start(); srvs.append(s)
    return f'http://127.0.0.1:{port}'
B = serve(18799, 'normal'); B503 = serve(18802, '503'); B403 = serve(18803, '403'); B401 = serve(18804, '401')
B404 = serve(18805, '404'); BCD = serve(18806, 'slowcd')
bad = []
def check(name, ok, extra=''):
    print(('PASS ' if ok else 'FAIL ') + name, extra)
    if not ok: bad.append(name)
def cache_files(): return [json.load(open(f)) for f in glob.glob(CACHE + '/*.json')]

# --- the 8 checks of the first version of patch 01 ---
M = K.Manners('offline test'); M.gap = 0.1
check('UA names the club, no email', 'KPC bot' in M.ua and '@' not in M.ua, M.ua)
t = CLK.t; a = M.get(B + '/a'); b = M.get(B + '/b'); dt = CLK.t - t
check('Crawl-delay 3 s obeyed between two live reads', a[0] == 200 and b[0] == 200 and dt >= 3.0, f'{dt:.1f}s')
t = CLK.t; a2 = M.get(B + '/a')
check('second read of /a comes from the cache (no request, no wait)', a2[0] == 200 and a2[2] == b'ok /a' and hits['/a'] == 1 and CLK.t == t)
check('robots.txt obeyed on an ArcGIS REST path (exemption off by default)', M.get(B + '/arcgis/rest/services/secret/x')[0] == 'robots' and '/arcgis/rest/services/secret/x' not in hits)
t = CLK.t; d = M.get(B + '/deny'); dt = CLK.t - t
check('403 retried exactly once, then handed to a person (URL listed)', d[0] == 403 and hits.get('/deny') == 2 and M.stat.get('for_person') == 1 and M.for_person[-1][0] == B + '/deny', str(M.for_person))
check('the 403 pause is at least the Crawl-delay and 30 s', dt >= 30, f'{dt:.1f}s')
s0 = dict(M.strike); t = CLK.t; c = M.get(B + '/c')
check('A9 slow-host budget counts requests (/a,/b,/deny x2 = 4): next read is deferred at once, not a strike', c[0] == 'deferred' and '/c' not in hits and CLK.t == t and M.strike == s0, str(M.slow_used))
check('next_run() says deferred / crawl-delay / rest mean "try next run"', all(K.next_run(x) for x in K.NEXT_RUN) and not K.next_run(403) and not K.next_run('robots'))
M2 = K.Manners('offline test, next night'); M2.gap = 0.1
a3 = M2.get(B + '/a')
check('next run: /a still from the disk cache and robots.txt not re-read', a3[0] == 200 and hits['/a'] == 1 and hits['/robots.txt'] == 1, f"robots reads {hits['/robots.txt']}")

# --- A1: robots.txt that fails = do not fetch; never cached; only 404/410 = no rules ---
for base, code in ((B503, '503'), (B403, '403'), (B401, '401')):
    Mx = K.Manners('a1'); Mx.gap = 0.1; r = Mx.get(base + '/x')
    # Nov 10: a robots.txt 401 / 403 counts as a Disallow ('robots'); only 5xx / unreachable stays 'robots-unreadable' (next run)
    want = 'robots' if code in ('401', '403') else 'robots-unreadable'
    check(f'A1 robots.txt {code} -> nothing fetched ({want}), listed for a person', r[0] == want and Mx.for_person and 'robots.txt answered ' + code in Mx.for_person[-1][1], str((r[0], Mx.for_person)))
check('A1 a failed robots.txt is never cached', not any(c['key'].startswith('robots ') and c['st'] not in (200, 404, 410) for c in cache_files()), str([(c['key'], c['st']) for c in cache_files()]))
Mx = K.Manners('a1 404'); Mx.gap = 0.1; r = Mx.get(B404 + '/x')
check('A1 robots.txt 404 -> no rules, allowed; cached with the real status 404', r[0] == 200 and any(c['key'] == 'robots ' + B404 + '/robots.txt' and c['st'] == 404 for c in cache_files()))
Mx = K.Manners('a1 dead'); Mx.gap = 0.1; r = Mx.get('http://127.0.0.1:18899/x')   # nothing listens there
check('A1 robots.txt unreachable -> nothing fetched', r[0] == 'robots-unreadable' and 'unreachable' in Mx.for_person[-1][1])
check('A13 a robots.txt that could not be read is a next-run status, a Disallow is not', K.next_run('robots-unreadable') and not K.next_run('robots'))
check('A1 robots Disallow still obeyed', K.Manners('a1b').get(B + '/private/x')[0] == 'robots' and '/private/x' not in hits)

# --- A2: a 403 on a host that already has 2 strikes still gets its one retry and goes to a person ---
M3 = K.Manners('a2'); M3.gap = 0.1; M3.strike['127.0.0.1'] = 2; M3.slow_used = {}
d = M3.get(B + '/deny2')
check('A2 403 with 2 strikes already -> retried once, 403 returned, URL for a person', d[0] == 403 and hits.get('/deny2') == 2 and M3.stat.get('for_person') == 1 and M3.for_person[-1][0] == B + '/deny2', str(M3.for_person))
check('A2 ...and then the host rests (no third request this run)', M3.get(B + '/after')[0] == 'rest' and '/after' not in hits)

# --- A3: secrets never reach the disk cache; keyed APIs are never cached ---
K.CACHE_ALL = True
M4 = K.Manners('a3'); M4.gap = 0.1
r = M4.get(B404 + '/q?api_key=SECRETVALUE&x=1')
blob = ''.join(open(f).read() for f in glob.glob(CACHE + '/*.json'))
check('A3 with CACHE_ALL a ?api_key= value is not in any cache file', r[0] == 200 and 'SECRETVALUE' not in blob and 'x=1' in blob)
check('A3 safe_url drops key/token/signature parameters', K.safe_url('https://h/p?a=1&key=s&token=t&signature=z&Api_Key=q') == 'https://h/p?a=1')
check('A3 KEYED_API urls are never cacheable', M4.keyed('https://developer.nps.gov/api/v1/alerts?api_key=x') and not M4.keyed('https://www.nps.gov/api/x'))

# --- A5: the robots read is paced and counted ---
M5 = K.Manners('a5'); M5.gap = 0.1; CLK.slept.clear(); n0 = M5.stat['requests']
B405 = serve(18807, '404'); M5.get(B405 + '/one')
check('A5 the robots.txt read counts as a request (robots + GET = 2)', M5.stat['requests'] - n0 == 2, str(M5.stat['requests'] - n0))
check('A5 the first GET waits the gap after the robots read', any(abs(s - 0.1) < 0.02 or s >= 0.09 for s in CLK.slept), str(CLK.slept))

# --- A6: browser_text obeys Crawl-delay limits (no Playwright needed: it returns before the browser) ---
os.environ['BROWSER'] = '1'
M6 = K.Manners('a6'); M6.gap = 0.1
check('A6 browser read of a host asking Crawl-delay 500 is skipped and listed', K.browser_text(BCD + '/page', M6) == '' and any('Crawl-delay 500' in w for _, w in M6.for_person) and '/page' not in hits)
os.environ.pop('BROWSER')

# --- A7: Retry-After longer than the cap -> to a person at once, no early retry ---
M7 = K.Manners('a7'); M7.gap = 0.1; M7.slow_used = {}
d = M7.get(B404 + '/deny-long')
check('A7 403 with Retry-After 3600 -> no retry, listed for a person', d[0] == 403 and hits.get('/deny-long') == 1 and 'Retry-After 3600' in M7.for_person[-1][1], str(M7.for_person))

# --- A8: a body cut off at read_max is not cached ---
M8 = K.Manners('a8', read_max=10); M8.gap = 0.1
r = M8.get(B404 + '/big')
check('A8 cut-off body (10 of 50 bytes) is not cached', len(r[2]) == 10 and not any(c['key'] == 'GET ' + B404 + '/big' for c in cache_files()))
K.CACHE_ALL = False

# --- A10: robots rules are kept per host:port ---
M10 = K.Manners('a10'); M10.gap = 0.1
M10.get(B + '/z1'); r = M10.get(B404 + '/private/y')
check('A10 rules read on :18799 are not used for :18805', r[0] == 200 and set(M10.robots) >= {'127.0.0.1:18799', '127.0.0.1:18805'}, str(list(M10.robots)))

# --- A12: pacing under threads ---
M12 = K.Manners('a12'); M12.gap = 0.5; K.time = _rt   # real clock for the thread test
starts = []
orig = M12._pace
def rec(h, cd, strike=0): orig(h, cd, strike); starts.append(_rt.time())
M12._pace = rec
B12 = serve(18808, '404')
ts = [threading.Thread(target=M12.get, args=(B12 + f'/t{i}',)) for i in range(3)]
[x.start() for x in ts]; [x.join() for x in ts]
starts.sort(); gaps = [b - a for a, b in zip(starts, starts[1:])]
check('A12 three threads on one host are still 0.5 s apart', len(starts) == 4 and all(g >= 0.45 for g in gaps), str([round(g, 2) for g in gaps]))
K.time = CLK

# Q8 (Brandon, relayed by Super 6:52 PM CST Nov 3): the robots.txt exception stays NARROW: only the written APIs of RIDB
# (recreation.gov) and NPS, and only under /api/. Any other host or path must read robots.txt.
check('Q8 KEYED_API is only RIDB + NPS, /api/ only', K.KEYED_API == {'ridb.recreation.gov': '/api/', 'developer.nps.gov': '/api/'}, str(K.KEYED_API))

# --- addendum (Nov 3, Quality spot-check slip): a queued request to a host whose robots.txt said no / could not be read is DROPPED ---
BQ403 = serve(18809, '403'); BQNO = serve(18810, 'denyall')
for k in [k for k in list(hits) if k.startswith('/q/')]: hits.pop(k)
MQ = K.Manners('queue'); MQ.gap = 0.1
before = dict(hits)
out = list(MQ.fetch_all([BQ403 + '/q/park/CA-2123', BQ403 + '/q/park/CA-2359', B + '/q/ok1', BQ403 + '/q/park/CA-2131']))
st = [r[0] for _, r in out]
check('Q-drop robots.txt 403: the first read and the 2 queued reads to that host make NO request',
      not any(k.startswith('/q/park') for k in hits) and st[0] == 'robots' and st[1] == st[3] == 'robots', str(st))   # Nov 10: a 403 robots.txt = a Disallow
check('Q-drop another host in the same queue is still read', st[2] == 200 and hits.get('/q/ok1') == 1)
check('Q-drop the dropped reads are listed for a person with the count', len(MQ.dropped) >= 2 and any('2 queued request(s) dropped' in w for _, w in MQ.for_person), str(MQ.for_person[-1:]))
r = MQ.get(BQ403 + '/q/park/CA-9999')
check('Q-drop a later single get() to the same host is dropped before any pacing (status robots: a 403 = a Disallow)', r[0] == 'robots' and '/q/park/CA-9999' not in hits and MQ.stat.get('dropped_queued', 0) >= 3)
out = list(MQ.fetch_all([BQNO + '/q/x1', BQNO + '/q/x2']))
check('Q-drop robots.txt "Disallow: /" blocks the whole site: status robots, no request', [r[0] for _, r in out] == ['robots', 'robots'] and '/q/x1' not in hits and '/q/x2' not in hits)
out = list(MQ.fetch_all([B + '/private/q1', B + '/q/ok2', B + '/q/ok3']))
check('Q-drop a Disallow for one PATH drops only the queued urls it matches; the host\'s other urls are read (Quality grade, 7:33 PM CST)',
      [r[0] for _, r in out] == ['robots', 200, 200] and hits.get('/q/ok2') == 1 and hits.get('/q/ok3') == 1 and '/private/q1' not in hits, str([r[0] for _, r in out]))
out = list(MQ.fetch_all([B + '/private/q4', B + '/q/ok4', B + '/private/q5']))
check('Q-drop path Disallow: a later queued url on the same disallowed path is still refused, no request', [r[0] for _, r in out] == ['robots', 200, 'robots'] and '/private/q5' not in hits, str([r[0] for _, r in out]))
check('robots_block() is True for both robots words (Quality: the old A1 checks expect "robots")', K.robots_block('robots') and K.robots_block('robots-unreadable') and not K.robots_block(200) and not K.robots_block('rest'))

for s in srvs: s.shutdown()
shutil.rmtree(CACHE, ignore_errors=True)
print('ALL PASS' if not bad else f'{len(bad)} FAILED: {bad}')
sys.exit(1 if bad else 0)
