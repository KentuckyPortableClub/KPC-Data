#!/usr/bin/env python3
"""Owner rule, 2026-11-10 (Quality, Data #60): the weekly KPC_* draft tools (kpc-map-audit.yml, kpc-tool-trial.yml,
kpc-map-pictures.yml) refuse services*.arcgis.com and the other saved-copy-only hosts before ANY request, robots.txt
included, and still read a saved (cached) copy. Uses a fake session: no network."""
import importlib.util, pathlib, sys, tempfile
ROOT = pathlib.Path(__file__).resolve().parents[1]
T = ROOT / '.github/scripts/draft/tools'
ok = True
def check(msg, c):
    global ok
    ok &= bool(c); print(('PASS ' if c else 'FAIL ') + msg)
try:
    import numpy, shapely, pyproj, requests  # noqa: F401
except ImportError as e:
    print(f'NOTE: tool libraries missing here ({e}); static checks only')
    for f in sorted(T.glob('KPC_*/kpc_*.py')):
        s = f.read_text(encoding='utf-8')
        check(f'{f.parent.name}: installs kpc_host_rules and asks host_ok', '_hr.install()' in s and '_hr.host_ok(url)' in s)
    sys.exit(0 if ok else 1)

class FakeSession:
    def __init__(self): self.calls, self.headers = [], {}
    def get(self, url, **k):
        self.calls.append(url); raise AssertionError('a request was made: ' + url)

def load(rel):
    p = T / rel; spec = importlib.util.spec_from_file_location(p.stem + '_hg', p)
    m = importlib.util.module_from_spec(spec); sys.modules[spec.name] = m; spec.loader.exec_module(m); return m

BLOCKED = ['https://services.arcgis.com/QVENGdaPbd4LUkLV/arcgis/rest/services/FWSInterest_Simplified_Authoritative/FeatureServer/0/query',
           'https://services1.arcgis.com/jRf8jjFwxedITdFe/arcgis/rest/services/Public_WMA_Boundaries/FeatureServer/1/query',
           'https://services-eu1.arcgis.com/x/arcgis/rest/services/y/FeatureServer/0/query',
           'https://apps.fs.usda.gov/arcx/rest/services/x/MapServer/0/query',
           'https://ncnhde.natureserve.org/x']
for rel, kind in (('KPC_9_map_pictures/kpc_map_pictures.py', 'http'), ('KPC_10_map_audit/kpc_map_audit.py', 'http'),
                  ('KPC_11_boundary_watch/kpc_boundary_watch.py', 'polite'), ('KPC_13_same_land/kpc_same_land.py', 'polite')):
    m = load(rel); name = rel.split('/')[0]
    for u in BLOCKED:
        fs = FakeSession(); d = tempfile.mkdtemp()
        if kind == 'http':
            w = m.Http(pathlib.Path(d), session=fs, sleep=lambda s: None)
            try: w.get(u, {'where': '1=1'}); r = False
            except m.SourceDown as e: r = 'refused' in str(e)
            rob = w.robots_ok(u)
        else:
            w = m.Polite('t', d, session=fs, sleep=lambda s: None)
            try: w.get_json(u, {'where': '1=1'}); r = False
            except m.SourceProblem as e: r = 'refused' in str(e)
            rob = w.robots_ok(u)
        check(f'{name}: {u.split("/")[2]} refused with no request, robots.txt included', r and not rob and not fs.calls)
    # a saved copy (the tool's own cache) of a blocked layer is still read
    fs = FakeSession(); d = tempfile.mkdtemp(); u = BLOCKED[0]
    if kind == 'http':
        w = m.Http(pathlib.Path(d), session=fs, sleep=lambda s: None)
        key = w._key(u, {'where': '1=1'}); sub = pathlib.Path(d) / 'json'; sub.mkdir(parents=True)
        (sub / (key + '.json')).write_text('{"features": [1]}'); (sub / (key + '.date')).write_text(m.today())
        data = w.get(u, {'where': '1=1'})[0]
    else:
        w = m.Polite('t', d, session=fs, sleep=lambda s: None); w._cache_write(u, {'where': '1=1'}, {'features': [1]})
        data = w.get_json(u, {'where': '1=1'})
    check(f'{name}: a saved copy of a blocked layer is still read (no request)', data == {'features': [1]} and not fs.calls)
    # and the install() hook is live in this process: a plain requests call is refused too
    try: requests.get(BLOCKED[1], timeout=1); r = False
    except Exception as e: r = 'saved copies only' in str(e) or type(e).__name__ == '_ReqRefused'
    check(f'{name}: after import, requests.get to services1.arcgis.com is refused before any request', r)
print('ALL PASS' if ok else 'SOME FAILED'); sys.exit(0 if ok else 1)
