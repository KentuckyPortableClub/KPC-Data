#!/usr/bin/env python3
"""Nov 17: the documents bot treated an unreadable robots.txt (HTTP 500, a
time-out, no connection) as permission (no file = allowed) and fetched the
page. The house rule is: if we cannot read the rules, nothing is fetched from
that host this run. 404 still means no file = allowed. A parsed Disallow is
still a refusal. Offline: a local 127.0.0.1 server only; nothing outside is
fetched, and nothing in the repo is written."""
import http.server, os, pathlib, sys, tempfile, threading

HERE = pathlib.Path(__file__).resolve().parent.parent
os.environ['OUT'] = tempfile.mkdtemp(prefix='kpc-docs-robots-')
sys.path.insert(0, str(HERE / '.github' / 'scripts'))
import kpc_docs_bot as B  # noqa: E402

ok = True


def check(cond, msg):
    global ok
    print(('PASS ' if cond else 'FAIL ') + msg)
    ok = ok and bool(cond)


hits = {}
MODE = {}


class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        hits[self.path] = hits.get(self.path, 0) + 1
        port = self.server.server_address[1]
        m = MODE.get(port, '500')
        if self.path == '/robots.txt':
            if m == '500':
                self.send_response(500); self.end_headers(); return
            if m == '404':
                self.send_response(404); self.end_headers(); return
            if m == 'rules':
                self.send_response(200); self.end_headers()
                self.wfile.write(b'User-agent: *\nDisallow: /secret\nAllow: /\n')
                return
            self.send_response(200); self.end_headers(); self.wfile.write(b'User-agent: *\nDisallow:\n'); return
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'ok ' + self.path.encode())


srvs = []


def serve(mode):
    s = http.server.ThreadingHTTPServer(('127.0.0.1', 0), H)
    port = s.server_address[1]
    MODE[port] = mode
    threading.Thread(target=s.serve_forever, daemon=True).start()
    srvs.append(s)
    return f'http://127.0.0.1:{port}', port


def reset():
    B.ROBOTS.clear(); B.ROBOTS_SAID.clear(); B.ROBOTS_REFUSED.clear()
    B.LAST.clear(); B.DEAD.clear(); B.STRIKE.clear()
    hits.clear()
    B.GAP = 0.0
    B.STAT['requests'] = 0
    B.STAT['robots'] = 0


# --- HTTP 500: do not fetch the page (this is the case that was wrongly allowed)
reset()
B500, p500 = serve('500')
st1, _, body1, _ = B.get(B500 + '/maps/park.pdf')
st2, _, body2, _ = B.get(B500 + '/rules/page.htm')
check(st1 == 'robots-unreadable', f'500 robots: first page is robots-unreadable (got {st1!r})')
check(st2 == 'robots-unreadable', f'500 robots: second page is robots-unreadable (got {st2!r})')
check(hits.get('/maps/park.pdf', 0) == 0, '500 robots: first page was not fetched')
check(hits.get('/rules/page.htm', 0) == 0, '500 robots: second page was not fetched')
check(hits.get('/robots.txt', 0) == 1, f'500 robots: robots.txt read once (got {hits.get("/robots.txt")})')
check(body1 == b'' and body2 == b'', '500 robots: no page body was returned')
# On the fix, the cache key is scheme+host and the value is False (unreadable).
# The assertion is skipped only so this file still *fails* cleanly on main (no helper yet).
if hasattr(B, 'robots_rkey'):
    rk = B.robots_rkey(B500 + '/')
    check(B.ROBOTS.get(rk) is False, '500 robots: cached as unreadable (False), not as no-file (None)')
    check((f'https://127.0.0.1:{p500}' not in B.ROBOTS),
          '500 robots: https of the same host is not marked unreadable (scheme+host key)')
else:
    check(False, '500 robots: cached as unreadable (False), not as no-file (None)')
    check(False, '500 robots: https of the same host is not marked unreadable (scheme+host key)')

# check_url surfaces the unreadable status (not ok)
reset()
r = B.check_url(B500 + '/maps/park.pdf')
check(r.get('status') == 'robots-unreadable', f'check_url on 500 robots is robots-unreadable (got {r.get("status")!r})')
check(hits.get('/maps/park.pdf', 0) == 0, 'check_url on 500 robots did not fetch the map')

# --- 404: no robots file = allowed, page is fetched
reset()
B404, _ = serve('404')
st, _, body, _ = B.get(B404 + '/maps/park.pdf')
check(st == 200, f'404 robots: page is fetched (got {st!r})')
check(body.startswith(b'ok /maps/park.pdf'), '404 robots: got the page body')
check(hits.get('/maps/park.pdf', 0) == 1, '404 robots: the page was requested once')

# --- parsed Disallow still refuses; other paths are read
reset()
BR, _ = serve('rules')
st_no, _, _, _ = B.get(BR + '/secret/file.pdf')
st_yes, _, body, _ = B.get(BR + '/maps/park.pdf')
check(st_no == 'robots', f'Disallow /secret: status robots (got {st_no!r})')
check(hits.get('/secret/file.pdf', 0) == 0, 'Disallow /secret: page was not fetched')
check(st_yes == 200 and body.startswith(b'ok /maps/park.pdf'), 'allowed path is fetched')

for s in srvs:
    s.shutdown()

print('ALL PASS' if ok else 'FAILED')
sys.exit(0 if ok else 1)
