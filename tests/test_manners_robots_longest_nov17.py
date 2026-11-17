#!/usr/bin/env python3
"""Nov 17: RFC 9309 says the longest matching robots.txt path wins, and Disallow
wins ties. Python's urllib.robotparser uses the first matching rule, so
"Allow: /a" then "Disallow: /a/b" would allow /a/b/x. Manners and the documents
bot now use longest match. Offline: a local 127.0.0.1 server only; nothing
outside is fetched, and nothing in the repo is written."""
import http.server, os, pathlib, sys, tempfile, threading, urllib.robotparser

CACHE = tempfile.mkdtemp(prefix='kpc-robots-longest-')
os.environ['KPC_MANNERS_CACHE'] = CACHE
os.environ.pop('KPC_ARCGIS_ROBOTS_EXEMPT', None)
os.environ.pop('KPC_MANNERS_CACHE_ALL', None)
os.environ['OUT'] = tempfile.mkdtemp(prefix='kpc-docs-longest-')

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github' / 'scripts'))
import kpc_manners as K  # noqa: E402
import kpc_docs_bot as B  # noqa: E402

ok = True


def check(cond, msg):
    global ok
    print(('PASS ' if cond else 'FAIL ') + msg)
    ok = ok and bool(cond)


def parsed(txt):
    rp = urllib.robotparser.RobotFileParser()
    rp.parse(txt.splitlines())
    return rp


UA = 'KPC bot: longest-match test'

# --- first matching rule would allow /a/b/x; longest match must refuse it
rp = parsed('User-agent: *\nAllow: /a\nDisallow: /a/b\n')
check(urllib.robotparser.RobotFileParser.can_fetch(rp, UA, 'https://ex.test/a/b/x') is True,
      'stdlib first-match would allow /a/b/x (the bug)')
if not hasattr(K, 'robots_allowed'):
    check(False, 'kpc_manners.robots_allowed is missing (the longest-match helper)')
    print('FAILED')
    sys.exit(1)
check(K.robots_allowed(rp, UA, 'https://ex.test/a/b/x') is False,
      'longest match refuses /a/b/x (Disallow: /a/b is longer)')
check(K.robots_allowed(rp, UA, 'https://ex.test/a/x') is True,
      'longest match still allows /a/x')
check(K.robots_allowed(rp, UA, 'https://ex.test/z') is True,
      'a path no rule names is still allowed')

# --- longer Allow wins over a shorter Disallow
rp = parsed('User-agent: *\nDisallow: /a\nAllow: /a/b\n')
check(K.robots_allowed(rp, UA, 'https://ex.test/a/b/x') is True,
      'longer Allow: /a/b wins over Disallow: /a')
check(K.robots_allowed(rp, UA, 'https://ex.test/a/x') is False,
      'Disallow: /a still refuses a shorter path')

# --- equal length: Disallow wins
rp = parsed('User-agent: *\nAllow: /a\nDisallow: /a\n')
check(K.robots_allowed(rp, UA, 'https://ex.test/a/x') is False,
      'at the same path length, Disallow wins')

# --- Allow: /parks after Disallow: /  (order that first-match would get wrong)
rp = parsed('User-agent: *\nDisallow: /\nAllow: /parks\nDisallow: /parks/guides/\n')
check(K.robots_allowed(rp, UA, 'https://ex.test/parks/cabin.htm') is True,
      'Allow: /parks is longer than Disallow: /, even if Disallow is written first')
check(K.robots_allowed(rp, UA, 'https://ex.test/parks/guides/x.htm') is False,
      'Disallow: /parks/guides/ is longer than Allow: /parks')
check(K.robots_allowed(rp, UA, 'https://ex.test/other') is False,
      'Disallow: / still refuses a path with no more specific Allow')

# --- live fetch through Manners: /a/b is not fetched; /a is
hits = {}


class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        hits[self.path] = hits.get(self.path, 0) + 1
        if self.path == '/robots.txt':
            self.send_response(200); self.end_headers()
            self.wfile.write(b'User-agent: *\nAllow: /a\nDisallow: /a/b\n')
            return
        self.send_response(200); self.end_headers()
        self.wfile.write(b'ok ' + self.path.encode())


s = http.server.ThreadingHTTPServer(('127.0.0.1', 0), H)
threading.Thread(target=s.serve_forever, daemon=True).start()
base = f'http://127.0.0.1:{s.server_address[1]}'
M = K.Manners('longest match test'); M.gap = 0.0
st_ok, _, body, _ = M.get(base + '/a/page.htm')
st_no, _, _, _ = M.get(base + '/a/b/secret.htm')
check(st_ok == 200 and body.startswith(b'ok /a/page.htm'), 'Manners fetches /a/page.htm')
check(st_no == 'robots', f'Manners refuses /a/b/secret.htm (got {st_no!r})')
check(hits.get('/a/b/secret.htm', 0) == 0, 'the longer Disallow path was not fetched')

# documents bot uses the same helper on a parsed robots.txt (injected; no extra network)
B.ROBOTS.clear(); B.ROBOTS_SAID.clear(); B.ROBOTS_REFUSED.clear()
B.ROBOTS['127.0.0.1'] = parsed('User-agent: *\nAllow: /a\nDisallow: /a/b\n')
check(B.robots_ok('http://127.0.0.1/a/page.htm') is True, 'documents bot allows /a/page.htm')
check(B.robots_ok('http://127.0.0.1/a/b/secret.htm') is False, 'documents bot refuses /a/b/secret.htm')

s.shutdown()
print('ALL PASS' if ok else 'FAILED')
sys.exit(0 if ok else 1)
