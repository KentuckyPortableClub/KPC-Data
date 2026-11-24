#!/usr/bin/env python3
"""24 Nov 2026: two page-reader fixes. (1) Owner 6:57 AM (P-1 'yes'): an https page that sends us to the plain http address of
the SAME site is followed; another site's plain address is still refused. (2) A cut-off .gz sitemap no longer stops the run.
No network. Prints PASS / FAIL, ends ALL PASS or SOME FAILED."""
import gzip, pathlib, socket, sys, urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github/scripts'))
socket.socket.connect = lambda *a, **k: (_ for _ in ()).throw(RuntimeError('no network in tests'))
import kpc_manners as M  # noqa: E402

ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


check('same site: case, www. and port aside', M.same_site('WWW.fs.example.gov', 'fs.example.gov:80') and not M.same_site('fs.example.gov', 'evil.example.com'))
H = urllib.request.HTTPRedirectHandler()
req = urllib.request.Request('https://www.fs.example.gov/forest/x')
try:
    r = H.redirect_request(req, None, 301, 'Moved', {}, 'http://www.fs.example.gov/forest/x')
    same = r is not None and r.full_url == 'http://www.fs.example.gov/forest/x'
except Exception as e:  # noqa: BLE001
    same = False; print('  ', e)
check('https -> http on the same site is followed', same)
try:
    H.redirect_request(req, None, 301, 'Moved', {}, 'http://other.example.com/x'); other = False
except M.HostRuleRefused:
    other = True
check('https -> http on another site is still refused', other)
try:
    r2 = H.redirect_request(req, None, 301, 'Moved', {}, 'https://fs.example.gov/forest/y'); hs = r2 is not None
except Exception:  # noqa: BLE001
    hs = False
check('https -> https is followed as before', hs)

src = (ROOT / '.github/scripts/kpc_park_pages_find.py').read_text(encoding='utf-8')
check('a cut-off .gz sitemap is caught (EOFError), not a crash', 'except (OSError, EOFError, ValueError):' in src)
try:
    gzip.decompress(gzip.compress(b'<urlset/>')[:-6]); cut = False
except (OSError, EOFError, ValueError):
    cut = True
check('a cut-off gzip raises one of the caught errors', cut)
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
