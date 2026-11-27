#!/usr/bin/env python3
"""Nov 17: RFC 9309 longest-match robots.txt (Disallow wins ties), parsed without
urllib.robotparser (its internals changed in Python 3.13.18 and a helper that
read them failed open). Our UA group is used if present, else '*'. '*' and '$'
wildcards are supported. A parse error means do not fetch. Offline: a local
127.0.0.1 server only; nothing outside is fetched, and nothing in the repo is
written."""
import http.server, os, pathlib, sys, tempfile, threading

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
PY = sys.version.split()[0]


def check(cond, msg):
    global ok
    print(('PASS ' if cond else 'FAIL ') + msg)
    ok = ok and bool(cond)


def rules(txt):
    return K.parse_robots(txt)


UA = 'KPC bot: longest-match test'

# --- no fail-open on this Python (the 3.13.18 bug: Disallow paths were allowed)
check(K.robots_allowed(rules('User-agent: *\nDisallow: /\n'), UA, 'https://ex.test/q') is False,
      f'Disallow: / is refused on Python {PY} (no fail-open)')
check(K.robots_allowed(rules('User-agent: *\nDisallow: /secret\n'), UA, 'https://ex.test/secret/x') is False,
      f'Disallow: /secret is refused on Python {PY} (no fail-open)')

# --- a RobotFileParser or any foreign object must not fail open
# 27 Nov 2026 (owner's site rule R-NET1, kpc_net_rule): only a real Disallow line is a no; an object with no rules shows none
check(K.robots_allowed(object(), UA, 'https://ex.test/') is True,
      'an unknown rules object shows no Disallow line: allowed (only a real Disallow line is a no)')

# --- longest match: Allow: /a then Disallow: /a/b refuses /a/b/x
rp = rules('User-agent: *\nAllow: /a\nDisallow: /a/b\n')
check(K.robots_allowed(rp, UA, 'https://ex.test/a/b/x') is False,
      'longest match refuses /a/b/x (Disallow: /a/b is longer)')
check(K.robots_allowed(rp, UA, 'https://ex.test/a/x') is True,
      'longest match still allows /a/x')
check(K.robots_allowed(rp, UA, 'https://ex.test/z') is True,
      'a path no rule names is still allowed')

# --- longer Allow wins over a shorter Disallow
rp = rules('User-agent: *\nDisallow: /a\nAllow: /a/b\n')
check(K.robots_allowed(rp, UA, 'https://ex.test/a/b/x') is True,
      'longer Allow: /a/b wins over Disallow: /a')
check(K.robots_allowed(rp, UA, 'https://ex.test/a/x') is False,
      'Disallow: /a still refuses a shorter path')

# --- equal length: Allow wins (RFC 9309 2.2.2; 27 Nov 2026, the page reader fix: this test said Disallow before)
rp = rules('User-agent: *\nAllow: /a\nDisallow: /a\n')
check(K.robots_allowed(rp, UA, 'https://ex.test/a/x') is True,
      'at the same path length, Allow wins (RFC 9309)')

# --- Allow: /parks after Disallow: /  (order that first-match would get wrong)
rp = rules('User-agent: *\nDisallow: /\nAllow: /parks\nDisallow: /parks/guides/\n')
check(K.robots_allowed(rp, UA, 'https://ex.test/parks/cabin.htm') is True,
      'Allow: /parks is longer than Disallow: /, even if Disallow is written first')
check(K.robots_allowed(rp, UA, 'https://ex.test/parks/guides/x.htm') is False,
      'Disallow: /parks/guides/ is longer than Allow: /parks')
check(K.robots_allowed(rp, UA, 'https://ex.test/other') is False,
      'Disallow: / still refuses a path with no more specific Allow')

# --- wildcards * and $
rp = rules('User-agent: *\nAllow: /\nDisallow: /*.pdf$\n')
check(K.robots_allowed(rp, UA, 'https://ex.test/maps/trail.pdf') is False,
      'Disallow: /*.pdf$ refuses a PDF at the end of the path')
check(K.robots_allowed(rp, UA, 'https://ex.test/maps/trail.pdf.backup') is True,
      '/* .pdf$ does not refuse a longer suffix')
rp = rules('User-agent: *\nAllow: /parks\nDisallow: /*?*\nDisallow: /\n')
# /parks is longer than /*?* (6 vs 4), so a parks URL with a query is still allowed
check(K.robots_allowed(rp, UA, 'https://ex.test/parks/cabin.htm?x=1') is True,
      'a longer Allow: /parks wins over Disallow: /*?*')
check(K.robots_allowed(rp, UA, 'https://ex.test/other?x=1') is False,
      'Disallow: /*?* (or Disallow: /) refuses a non-parks query URL')

# --- our UA group, else *
rp = rules('User-agent: KPC\nDisallow: /private\n\nUser-agent: *\nAllow: /\n')
check(K.robots_allowed(rp, UA, 'https://ex.test/private/x') is False,
      'the KPC user-agent group is used when it matches our UA')
check(K.robots_allowed(rp, 'OtherBot/1.0', 'https://ex.test/private/x') is True,
      'a different UA falls back to the * group')

# --- no file vs unreadable vs parse error
check(K.robots_allowed(None, UA, 'https://ex.test/') is True, 'no robots file = allowed')
# 27 Nov 2026 (R-NET1 in kpc_net_rule): a 5xx / unreachable robots.txt stops the site for the RUN inside Manners.get; the rules
# object itself carries no Disallow line, so robots_allowed has nothing to refuse
check(K.robots_allowed(False, UA, 'https://ex.test/') is True, 'robots_allowed(False) has no Disallow line (the run stop lives in Manners.get)')

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
check(isinstance(M.robots.get(M.rkey(base + '/')), K.RobotsRules),
      'Manners stored our own rules object, not a robotparser')

# --- Disallow: / through get() (the 3.13 fail-open case)
class H2(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        hits[('denyall', self.path)] = hits.get(('denyall', self.path), 0) + 1
        if self.path == '/robots.txt':
            self.send_response(200); self.end_headers()
            self.wfile.write(b'User-agent: *\nDisallow: /\n')
            return
        self.send_response(200); self.end_headers(); self.wfile.write(b'should-not-be-read')


s2 = http.server.ThreadingHTTPServer(('127.0.0.1', 0), H2)
threading.Thread(target=s2.serve_forever, daemon=True).start()
base2 = f'http://127.0.0.1:{s2.server_address[1]}'
M2 = K.Manners('fail-open test'); M2.gap = 0.0
st, _, body, _ = M2.get(base2 + '/parks/cabin.htm')
check(st == 'robots', f'Disallow: / through get() is robots on Python {PY} (got {st!r})')
check(body == b'' and hits.get(('denyall', '/parks/cabin.htm'), 0) == 0,
      f'Disallow: / page was not fetched on Python {PY}')

# documents bot uses the same helper on parsed rules (injected; no extra network)
B.ROBOTS.clear(); B.ROBOTS_SAID.clear(); B.ROBOTS_REFUSED.clear()
B.ROBOTS[B.robots_rkey('http://127.0.0.1/a/page.htm')] = rules('User-agent: *\nAllow: /a\nDisallow: /a/b\n')
check(B.robots_ok('http://127.0.0.1/a/page.htm') is True, 'documents bot allows /a/page.htm')
check(B.robots_ok('http://127.0.0.1/a/b/secret.htm') is False, 'documents bot refuses /a/b/secret.htm')


# --- duplicate groups are merged (RFC 9309 2.2.1)
rp = rules('User-agent: *\nDisallow: /a\n\nUser-agent: *\nDisallow: /private')
check(K.robots_allowed(rp, UA, 'https://ex.test/private/x') is False,
      'duplicate * groups are merged: Disallow: /private refuses /private/x')
check(K.robots_allowed(rp, UA, 'https://ex.test/a/x') is False,
      'duplicate * groups are merged: the first group\'s Disallow: /a still applies')
check(K.robots_allowed(rp, UA, 'https://ex.test/ok') is True,
      'a path neither merged * group names is still allowed')
rp = rules('User-agent: kpc\nDisallow: /a\n\nUser-agent: KPC\nDisallow: /private\n\nUser-agent: *\nAllow: /\n')
check(K.robots_allowed(rp, UA, 'https://ex.test/private/x') is False,
      'duplicate groups for our product token are merged (and * is not mixed in)')
check(K.robots_allowed(rp, UA, 'https://ex.test/ok') is True,
      'a named match is not merged with the * Allow: /')

# --- product token only, whole token (not a substring of the whole UA string)
# Our UA is 'KPC bot: ...'; the product token is 'kpc'. 'User-agent: bot' must not match.
rp = rules('User-agent: bot\nAllow: /\n\nUser-agent: *\nDisallow: /\n')
check(K.robots_allowed(rp, UA, 'https://ex.test/q') is False,
      "User-agent: bot does not match our product token; * Disallow: / still applies")
rp = rules('User-agent: KPC\nDisallow: /private\n\nUser-agent: *\nAllow: /\n')
check(K.robots_allowed(rp, UA, 'https://ex.test/private/x') is False,
      'User-agent: KPC matches the product token (case-insensitive whole token)')
rp = rules('User-agent: kp\nAllow: /\n\nUser-agent: *\nDisallow: /\n')
check(K.robots_allowed(rp, UA, 'https://ex.test/q') is False,
      'User-agent: kp is not a whole-token match for kpc; * Disallow: / still applies')
check(K._product_token(UA) == 'kpc', 'product token of our UA is kpc')

# --- percent-encoding: decode unreserved %XX, keep reserved encoded (RFC 9309 2.2.2)
rp = rules('User-agent: *\nDisallow: /~joe/\n')
check(K.robots_allowed(rp, UA, 'https://ex.test/%7Ejoe/x') is False,
      'Disallow: /~joe/ also refuses /%7Ejoe/x (unreserved %7E is ~)')
check(K.robots_allowed(rp, UA, 'https://ex.test/~joe/x') is False,
      'Disallow: /~joe/ refuses /~joe/x')
check(K.robots_allowed(rp, UA, 'https://ex.test/other') is True,
      'Disallow: /~joe/ does not refuse an unrelated path')
rp = rules('User-agent: *\nDisallow: /%7Ejoe/\n')
check(K.robots_allowed(rp, UA, 'https://ex.test/~joe/x') is False,
      'Disallow: /%7Ejoe/ also refuses /~joe/x')
rp = rules('User-agent: *\nAllow: /\nDisallow: /a%2Fb\n')
check(K.robots_allowed(rp, UA, 'https://ex.test/a/b') is True,
      'Disallow: /a%2Fb (reserved slash stays encoded) does not refuse /a/b')
check(K.robots_allowed(rp, UA, 'https://ex.test/a%2Fb') is False,
      'Disallow: /a%2Fb does refuse the encoded path /a%2Fb')

# --- self-audit: consecutive User-agent lines share one group
rp = rules('User-agent: kpc\nUser-agent: otherbot\nDisallow: /private\n')
check(K.robots_allowed(rp, UA, 'https://ex.test/private/x') is False,
      'consecutive User-agent lines share Disallow: /private')
rp = rules('User-agent: kpc\n\nUser-agent: otherbot\nDisallow: /private\n')
check(K.robots_allowed(rp, UA, 'https://ex.test/private/x') is False,
      'a blank line between User-agent lines still shares the group')
rp = rules('User-agent: kpc\nCrawl-delay: 5\nUser-agent: otherbot\nDisallow: /private\n')
check(K.robots_allowed(rp, UA, 'https://ex.test/private/x') is False,
      'Crawl-delay between User-agent lines does not start a new group')

# --- self-audit: directive names are case-insensitive
rp = rules('USER-AGENT: *\nDisAllow: /private\nALLOW: /private/ok\n')
check(K.robots_allowed(rp, UA, 'https://ex.test/private/x') is False,
      'USER-AGENT / DisAllow are honoured (directive names are case-insensitive)')
check(K.robots_allowed(rp, UA, 'https://ex.test/private/ok') is True,
      'ALLOW is honoured as Allow (case-insensitive)')

# --- self-audit: leading BOM and CRLF line endings
rp = rules('\ufeffUser-agent: *\nDisallow: /private\n')
check(K.robots_allowed(rp, UA, 'https://ex.test/private/x') is False,
      'a leading BOM does not hide Disallow: /private')
rp = rules('User-agent: *\r\nDisallow: /private\r\n')
check(K.robots_allowed(rp, UA, 'https://ex.test/private/x') is False,
      'CRLF line endings still apply Disallow: /private')
rp = rules(b'\xef\xbb\xbfUser-agent: *\r\nDisallow: /private\r\n')
check(K.robots_allowed(rp, UA, 'https://ex.test/private/x') is False,
      'UTF-8 BOM bytes plus CRLF still apply Disallow: /private')

# --- self-audit: a very long file or a NUL is a parse error (do not fetch)
# A file over ROBOTS_MAX must not be silently truncated: a Disallow past the cap would fail open.
long_err = None
try:
    K.parse_robots('User-agent: *\nDisallow: /\n' + '#' * (K.ROBOTS_MAX + 1))
except Exception as e:  # noqa: BLE001
    long_err = e
check(long_err is None, f'a robots.txt longer than ROBOTS_MAX: the first part is read (RFC 9309 2.5; got {long_err!r})')
nul_err = None
try:
    K.parse_robots('User-agent: *\nDisallow: /\n\x00')
except Exception as e:  # noqa: BLE001
    nul_err = e
check(nul_err is None, f'a robots.txt with a NUL is read, not a parse error (only a Disallow line is a no; got {nul_err!r})')

# Through Manners: an oversized robots.txt is unreadable, so the page is not fetched
class Hlong(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        hits[('long', self.path)] = hits.get(('long', self.path), 0) + 1
        if self.path == '/robots.txt':
            self.send_response(200); self.end_headers()
            self.wfile.write(b'User-agent: *\nDisallow: /secret\n' + b'#' * (K.ROBOTS_MAX + 1))
            return
        self.send_response(200); self.end_headers(); self.wfile.write(b'should-not-be-read')


sl = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Hlong)
threading.Thread(target=sl.serve_forever, daemon=True).start()
basel = f'http://127.0.0.1:{sl.server_address[1]}'
Ml = K.Manners('too-long robots test'); Ml.gap = 0.0
st_long, _, body_long, _ = Ml.get(basel + '/ok.htm')
check(st_long == 200, f'oversized robots.txt through get(): its first part is read and /ok.htm is not disallowed (got {st_long!r})')
check(body_long == b'should-not-be-read' and hits.get(('long', '/ok.htm'), 0) == 1,
      'an oversized robots.txt: the page no Disallow line names is fetched once')
sl.shutdown()

s.shutdown(); s2.shutdown()
print('ALL PASS' if ok else 'FAILED')
print('Python', PY)
sys.exit(0 if ok else 1)
