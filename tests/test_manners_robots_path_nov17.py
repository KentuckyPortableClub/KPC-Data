#!/usr/bin/env python3
"""Nov 17: the manners whole-site robots check asked can_fetch on the site root '/', so a host
that allows /parks and then has Disallow: / (dnr.alaska.gov) looked fully blocked. Each URL is
now decided by can_fetch on that page. An unreadable robots.txt (e.g. HTTP 500) still means
nothing is fetched from that host this run. Offline: a local 127.0.0.1 server only; nothing
outside is fetched, and nothing in the repo is written."""
import http.server, os, pathlib, shutil, sys, tempfile, threading

CACHE = tempfile.mkdtemp(prefix='kpc-robots-path-')
os.environ['KPC_MANNERS_CACHE'] = CACHE
os.environ.pop('KPC_ARCGIS_ROBOTS_EXEMPT', None)
os.environ.pop('KPC_MANNERS_CACHE_ALL', None)

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github' / 'scripts'))
import kpc_manners as K  # noqa: E402

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
        m = MODE.get(port, 'alaska')
        if self.path == '/robots.txt':
            if m == 'alaska':
                # Same shape as dnr.alaska.gov: Allow: /parks, then Disallow: /
                body = b'User-agent: *\nAllow: /parks\nDisallow: /\n'
                self.send_response(200)
                self.end_headers()
                self.wfile.write(body)
                return
            if m == 'denyall':
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'User-agent: *\nDisallow: /\n')
                return
            if m == '500':
                self.send_response(500)
                self.end_headers()
                return
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'ok ' + self.path.encode())


srvs = []


def serve(port, mode):
    MODE[port] = mode
    s = http.server.ThreadingHTTPServer(('127.0.0.1', port), H)
    threading.Thread(target=s.serve_forever, daemon=True).start()
    srvs.append(s)
    return f'http://127.0.0.1:{port}'


# --- Alaska-shaped rules: /parks is allowed; other paths are not
BA = serve(18911, 'alaska')
M = K.Manners('robots path test')
M.gap = 0.0
park1 = M.get(BA + '/parks/aspcabins/belugacabin.htm')
park2 = M.get(BA + '/parks/aspcabins/mulcahycabin.htm')
other = M.get(BA + '/mlw/knik-river-pua/')
root = M.get(BA + '/')
check(park1[0] == 200 and park1[2].startswith(b'ok /parks/'),
      'Allow: /parks then Disallow: /: the first allowed parks page is fetched')
check(park2[0] == 200 and hits.get('/parks/aspcabins/mulcahycabin.htm') == 1,
      'a later allowed parks page is also fetched (the old whole-site check blocked this)')
check(other[0] == 'robots' and '/mlw/knik-river-pua/' not in hits,
      'a path that is not allowed is robots and is not fetched')
check(root[0] == 'robots' and hits.get('/') is None,
      'the site root stays robots (Disallow: /) and is not fetched')
check(hits.get('/robots.txt') == 1,
      'robots.txt was read once for that host')
check('127.0.0.1:18911' not in M.blocked,
      'an Allow: /parks plus Disallow: / host is not marked whole-site blocked')

# --- bare Disallow: / still blocks every path (no more-specific Allow)
BD = serve(18912, 'denyall')
M2 = K.Manners('robots denyall test')
M2.gap = 0.0
d1 = M2.get(BD + '/parks/cabin.htm')
d2 = M2.get(BD + '/q/x1')
check(d1[0] == 'robots' and d2[0] == 'robots' and '/parks/cabin.htm' not in hits and '/q/x1' not in hits,
      'a bare Disallow: / still blocks every path; nothing is fetched')

# --- unreadable robots.txt (HTTP 500): do not fetch this run, including allowed-looking paths
B5 = serve(18913, '500')
M3 = K.Manners('robots unreadable test')
M3.gap = 0.0
u1 = M3.get(B5 + '/parks/cabin.htm')
u2 = M3.get(B5 + '/other')
check(u1[0] == 'robots-unreadable' and u2[0] == 'robots-unreadable',
      'robots.txt HTTP 500: both URLs are robots-unreadable this run')
check('/parks/cabin.htm' not in hits and '/other' not in hits,
      'robots.txt HTTP 500: no page is fetched this run')
check(K.next_run('robots-unreadable') and not K.next_run('robots'),
      'unreadable robots is try-next-run; a Disallow is not')

for s in srvs:
    s.shutdown()
shutil.rmtree(CACHE, ignore_errors=True)
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
