#!/usr/bin/env python3
"""Nov 17: when http robots.txt is unreadable, manners may fetch the https form of
the same URL, but only if https robots allows that page and the https response is
the same page (same host, same path and query). A disallowed https path is never
fetched. If https is a different page, the http URL stays unreadable and is not
replaced. Offline: a local 127.0.0.1 HTTP + HTTPS server only; nothing outside is
fetched, and nothing in the repo is written."""
import http.server, os, pathlib, ssl, subprocess, sys, tempfile, threading

CACHE = tempfile.mkdtemp(prefix='kpc-https-upgrade-')
os.environ['KPC_MANNERS_CACHE'] = CACHE
os.environ.pop('KPC_ARCGIS_ROBOTS_EXEMPT', None)
os.environ.pop('KPC_MANNERS_CACHE_ALL', None)

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github' / 'scripts'))
ssl._create_default_https_context = ssl._create_unverified_context
import kpc_manners as K  # noqa: E402

ok = True


def check(cond, msg):
    global ok
    print(('PASS ' if cond else 'FAIL ') + msg)
    ok = ok and bool(cond)


hits = {}   # (scheme, port, path) -> count
MODE = {}   # port -> mode


class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _scheme(self):
        return 'https' if isinstance(self.connection, ssl.SSLSocket) else 'http'

    def do_GET(self):
        port = self.server.server_address[1]
        hits[(self._scheme(), port, self.path)] = hits.get((self._scheme(), port, self.path), 0) + 1
        m = MODE.get(port, 'allow')
        if self.path == '/robots.txt':
            if m == '500':
                self.send_response(500); self.end_headers(); return
            if m == 'disallow_secret':
                self.send_response(200); self.end_headers()
                self.wfile.write(b'User-agent: *\nDisallow: /secret\nAllow: /\n'); return
            if m == '404':
                self.send_response(404); self.end_headers(); return
            self.send_response(200); self.end_headers()
            self.wfile.write(b'User-agent: *\nAllow: /\n'); return
        if m == 'otherpage' and self.path == '/parks/cabin.htm':
            self.send_response(302)
            self.send_header('Location', '/other/place.htm')
            self.end_headers(); return
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(f'<html><title>{self._scheme()} {self.path}</title><body>ok {self._scheme()} {self.path}</body></html>'.encode())


def serve(mode, tls=False, cert=None, key=None):
    s = http.server.ThreadingHTTPServer(('127.0.0.1', 0), H)
    if tls:
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.load_cert_chain(cert, key)
        s.socket = ctx.wrap_socket(s.socket, server_side=True)
    port = s.server_address[1]
    MODE[port] = mode
    threading.Thread(target=s.serve_forever, daemon=True).start()
    return s, port


tmpdir = tempfile.mkdtemp(prefix='kpc-tls-')
cert, key = str(pathlib.Path(tmpdir) / 'c.pem'), str(pathlib.Path(tmpdir) / 'k.pem')
subprocess.check_call(['openssl', 'req', '-x509', '-newkey', 'rsa:2048', '-keyout', key, '-out', cert,
                       '-days', '1', '-nodes', '-subj', '/CN=127.0.0.1'],
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

http_s, http_port = serve('500', tls=False)
https_s, https_port = serve('allow', tls=True, cert=cert, key=key)
https_dis_s, https_dis_port = serve('disallow_secret', tls=True, cert=cert, key=key)
https_redir_s, https_redir_port = serve('otherpage', tls=True, cert=cert, key=key)
http_ok_s, http_ok_port = serve('404', tls=False)

http_u = f'http://127.0.0.1:{http_port}/parks/cabin.htm'
https_u = f'https://127.0.0.1:{https_port}/parks/cabin.htm'


def fresh(https_port_for_upgrade):
    hits.clear()
    M = K.Manners('https upgrade test')
    M.gap = 0.0
    M.https_port = https_port_for_upgrade
    return M


# --- http robots 500, https allows and is the same page: use https, never fetch http page
M = fresh(https_port)
st, _, body, final = M.get(http_u)
check(st == 200, f'unreadable http robots: https same page is used (got {st!r})')
check(b'ok https /parks/cabin.htm' in body, 'https body of the same path was returned')
check(final.startswith('https://') and final.endswith('/parks/cabin.htm'), f'final URL is the https page (got {final!r})')
check(hits.get(('http', http_port, '/parks/cabin.htm'), 0) == 0, 'the http page was not fetched')
check(hits.get(('http', http_port, '/robots.txt'), 0) == 1, 'http robots.txt was read once')
check(hits.get(('https', https_port, '/parks/cabin.htm'), 0) == 1, 'the https page was fetched once')

# a later http URL on the same host also upgrades (must not be dropped by the unreadable flag)
st2, _, body2, _ = M.get(f'http://127.0.0.1:{http_port}/parks/other.htm')
check(st2 == 200 and b'ok https /parks/other.htm' in body2, 'a later allowed https path on that host also upgrades')

# --- https robots disallows /secret: do not fetch it; http stays unreadable
M = fresh(https_dis_port)
secret = f'http://127.0.0.1:{http_port}/secret/file.htm'
st, _, body, _ = M.get(secret)
check(st == 'robots-unreadable', f'disallowed https path stays robots-unreadable (got {st!r})')
check(hits.get(('https', https_dis_port, '/secret/file.htm'), 0) == 0, 'the disallowed https path was not fetched')

# --- https is a different page (redirect to another path): leave http unreadable, do not use that content
M = fresh(https_redir_port)
st, _, body, final = M.get(http_u)
check(st == 'robots-unreadable', f'https other path is not used (got {st!r})')
check(body == b'', 'the different https page was not returned as the http page')

# --- http robots 404 (no file = allowed): fetch http, do not require https
M = fresh(https_port)
ok_http = f'http://127.0.0.1:{http_ok_port}/parks/cabin.htm'
st, _, body, final = M.get(ok_http)
check(st == 200 and b'ok http /parks/cabin.htm' in body, 'readable-as-no-file http robots still fetches http')
check(final.startswith('http://'), f'no upgrade when http robots is readable (got {final!r})')

for s in (http_s, https_s, https_dis_s, https_redir_s, http_ok_s):
    s.shutdown()

print('ALL PASS' if ok else 'FAILED')
sys.exit(0 if ok else 1)
