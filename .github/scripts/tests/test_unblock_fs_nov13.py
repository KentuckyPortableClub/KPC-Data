#!/usr/bin/env python3
"""KPC owner, 2026-11-13: apps.fs.usda.gov is off the saved-copy-only default (robots.txt answered 403 = no rules file, not a
Disallow line) and is asked at most once every 10 s; gis.blm.gov was never blocked here and the one BLM Nevada sign-in-only
service stays in the registry's blocked.csv. services*.arcgis.com, ncnhde.natureserve.org and the Grant County org stay blocked.
Offline: proxy variables dropped, every socket refused, urlopen stubbed.   Run from the repo root:
    python3 .github/scripts/tests/test_unblock_fs_nov13.py
"""
import csv, io, os, pathlib, socket, sys, urllib.error

for _k in ('HTTPS_PROXY', 'HTTP_PROXY', 'https_proxy', 'http_proxy', 'ALL_PROXY', 'all_proxy', 'KPC_SAVED_ONLY_HOSTS', 'KPC_MANNERS_CACHE'):
    os.environ.pop(_k, None)
ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / '.github' / 'scripts'))
SOCKS = []
def _no_socket(*a, **k):
    SOCKS.append(a); raise OSError('this test makes no network calls')
socket.create_connection = _no_socket
socket.socket.connect = lambda self, *a, **k: _no_socket(*a)
import importlib.util  # noqa: E402
import kpc_host_rules as HR  # noqa: E402
import kpc_manners as K  # noqa: E402
ok = True


def check(cond, msg):
    global ok
    ok &= bool(cond); print(('PASS ' if cond else 'FAIL ') + msg)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


VHR = load(ROOT / '.github/scripts/draft/tools/kpc_engine/vendor/kpc_host_rules.py', 'vendor_host_rules')
FS = 'https://apps.fs.usda.gov/arcx/rest/services/EDW/EDW_Wilderness_02/MapServer/0/query'
BLM = 'https://gis.blm.gov/arcgis/rest/services/range/BLM_Natl_WHB/MapServer/0/query'
STILL = ['https://services.arcgis.com/x/FeatureServer/0', 'https://services1.arcgis.com/x', 'https://services7.arcgis.com/robots.txt',
         'https://services-eu1.arcgis.com/x', 'https://ncnhde.natureserve.org/x.zip', 'https://services.arcgis.com/33TOOklri9xpic7U/x']
for R, nm in ((HR, 'kpc_host_rules'), (VHR, 'vendor kpc_host_rules')):
    check(R.host_ok(FS)[0] and R.host_ok('https://APPS.fs.usda.gov:443/robots.txt')[0], f'{nm}: apps.fs.usda.gov allowed')
    check(R.host_ok(BLM)[0] and R.who_for(BLM)[0] == 'bot', f'{nm}: gis.blm.gov allowed')
    check('apps.fs.usda.gov' not in R.saved_only_hosts() and 'services1.arcgis.com' in R.saved_only_hosts(), f'{nm}: default saved-copy list')
    for u in STILL: check(not R.host_ok(u)[0], f'{nm}: still blocked {u[8:60]}')
    check(R.who_for(STILL[-1])[0] == 'never' and R.who_for(STILL[4])[0] == 'never', f'{nm}: Grant County and ncnhde stay never-contact')
os.environ['KPC_SAVED_ONLY_HOSTS'] = 'apps.fs.usda.gov'
check(not HR.host_ok(FS)[0], 'KPC_SAVED_ONLY_HOSTS can still add apps.fs.usda.gov back (the variable only adds)')
os.environ.pop('KPC_SAVED_ONLY_HOSTS')

rows = [r for r in csv.DictReader(open(ROOT / '.github/scripts/draft/tools/kpc_engine/registry/blocked.csv', encoding='utf-8')) if r['domain'] == 'gis.blm.gov']
check(len(rows) == 1 and 'BLM_Nevada_SNPLMA_Disposal_Boundary' in rows[0]['url'] and 'sign-in' in rows[0]['reason'],
      'registry blocked.csv: the one BLM row is the Nevada SNPLMA service, sign-in only')

# Manners: 10 s between two requests to the Forest Service host; Retry-After over 120 s rests the host instead of a short wait
class Clock:
    def __init__(self): self.t = 1_000_000.0; self.slept = []
    def time(self): return self.t
    def sleep(self, s): self.slept.append(s); self.t += max(0, s)
CLK = Clock(); K.time = CLK
SENT, ANS = [], []
class Resp(io.BytesIO):
    status = 200; headers = {}
    def geturl(self): return SENT[-1]
def fake_urlopen(req, timeout=None):
    u = getattr(req, 'full_url', req); SENT.append((CLK.t, u))
    if u.endswith('/robots.txt'): raise urllib.error.HTTPError(u, 404, 'stub', {}, io.BytesIO(b''))   # stub answer; robots 403 handling is unchanged
    a = ANS.pop(0) if ANS else 200
    if a == 200: return Resp(b'{}')
    raise urllib.error.HTTPError(u, a[0], 'stub', a[1], io.BytesIO(b''))
K.urllib.request.urlopen = fake_urlopen
for mod in (K, load(ROOT / '.github/scripts/draft/tools/kpc_engine/vendor/kpc_manners.py', 'vendor_manners')):
    mod.time = CLK; mod.urllib.request.urlopen = fake_urlopen
    check(mod.SLOW_HOSTS.get('apps.fs.usda.gov', 0) >= 10, f'{mod.__name__}: apps.fs.usda.gov is a 10 s slow host')
    M = mod.Manners('KPC test'); SENT.clear()
    for i in range(3): M.get(FS + f'?n={i}')
    t = [x[0] for x in SENT if 'robots' not in x[1]]
    check(len(t) == 3 and all(b - a >= 10 - 1e-6 for a, b in zip(t, t[1:])), f'{mod.__name__}: Forest Service requests 10 s apart ({[round(b - a, 1) for a, b in zip(t, t[1:])]})')
    check('KPC bot' in M.ua and 'kentuckyportableclub' in M.ua and '@' not in M.ua, f'{mod.__name__}: honest club User-Agent, no email')
    SENT.clear(); ANS[:] = [(429, {'Retry-After': '900'})]
    st = M.get(FS + '?ra=1'); st2 = M.get(FS + '?ra=2')
    check(st[0] == 'rest' and st2[0] == 'rest' and len([x for x in SENT if 'robots' not in x[1]]) == 1, f'{mod.__name__}: a 900 s Retry-After rests the host (no more requests) ({st[0]}, {st2[0]})')
    M2 = mod.Manners('KPC test'); SENT.clear(); ANS[:] = [(429, {}), (429, {}), (429, {})]
    st = M2.get(FS + '?b=1'); st2 = M2.get(FS + '?b=2')
    check(st[0] == 'rest' and st2[0] == 'rest', f'{mod.__name__}: three 429s in a row rest the host for the day ({st[0]}, {st2[0]})')
    M3 = mod.Manners('KPC test'); SENT.clear()
    M3.get(BLM + '?n=1'); M3.get(BLM + '?n=2')
    t = [x[0] for x in SENT if 'robots' not in x[1]]
    check(len(t) == 2 and t[1] - t[0] < 10, f'{mod.__name__}: gis.blm.gov keeps the ordinary 2 s gap ({t[1] - t[0]:.1f} s)')
check(not SOCKS, 'no socket was opened')
print('ALL PASS' if ok else 'SOME FAILED'); sys.exit(0 if ok else 1)
