"""Nov 10 (owner rule, 2026-11-10): no KPC-Data fetch contacts services*.arcgis.com, apps.fs.usda.gov or ncnhde.natureserve.org:
not data, not robots.txt, not a redirect hop. The host check sees the host really dialled (port / user@ / trailing dot / %-escape),
an address with no plain http(s) host fails closed, KPC_SAVED_ONLY_HOSTS only adds hosts, and an https -> http hop is refused.
convert_layers: a robots.txt 401/403/5xx or no answer = disallow. Offline: a 127.0.0.1 stand-in server, every other dial is trapped."""
import http.server, importlib, importlib.util, os, pathlib, socket, sys, threading, types, urllib.error, urllib.request

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
S = ROOT / '.github/scripts'
sys.path.insert(0, str(S))
import kpc_host_rules as HR  # noqa: E402

BAD = ['https://services1.arcgis.com:443/x', 'https://u@services1.arcgis.com/x', 'https://services1.arcgis.com./x',
       'https://apps.fs.usda.gov:443/x', 'https://u:p@apps.fs.usda.gov./robots.txt', 'https://services1%2earcgis.com/x',
       '//services2.arcgis.com/x', 'https:///x', '', 'ftp://gis.example.gov/x', 'file:///etc/hosts']
GOOD = ['https://api.pota.app/park/US-0001', 'https://www.sciencebase.gov/x', 'https://kygisserver.ky.gov/arcgis/rest/services/x/MapServer/0',
        'https://hub.arcgis.com/api/x', 'https://www.arcgis.com/sharing/rest/x']


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    """No proxy (the stand-in is local); any DNS lookup or connection to a host other than 127.0.0.1 is recorded and refused."""
    for k in list(os.environ):
        if k.lower() in ('http_proxy', 'https_proxy', 'all_proxy', 'no_proxy'): monkeypatch.delenv(k)
    monkeypatch.delenv('KPC_SAVED_ONLY_HOSTS', raising=False)
    dials, gai, cc = [], socket.getaddrinfo, socket.create_connection
    def g(host, *a, **k):
        if host not in ('127.0.0.1', 'localhost'): dials.append(host); raise OSError('test: no network')
        return gai(host, *a, **k)
    def c(addr, *a, **k):
        if addr[0] not in ('127.0.0.1', 'localhost'): dials.append(addr[0]); raise OSError('test: no network')
        return cc(addr, *a, **k)
    monkeypatch.setattr(socket, 'getaddrinfo', g); monkeypatch.setattr(socket, 'create_connection', c)
    return dials


@pytest.fixture
def server():
    class H(http.server.BaseHTTPRequestHandler):
        seen = []
        def log_message(self, *a): pass
        def do_GET(self):
            H.seen.append(self.path)
            to = {'/to-services': 'https://services1.arcgis.com:443/x/arcgis/rest/services/Y/FeatureServer/0?f=json',
                  '/to-fs': 'https://apps.fs.usda.gov./robots.txt', '/to-rel': '//services9.arcgis.com/robots.txt'}.get(self.path)
            if to: self.send_response(302); self.send_header('Location', to); self.end_headers(); return
            code = 500 if self.path == '/robots.txt' and getattr(H, 'robots500', False) else 404 if self.path == '/robots.txt' else 200
            self.send_response(code); self.send_header('Content-Type', 'application/json'); self.end_headers(); self.wfile.write(b'{}')
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f'http://127.0.0.1:{srv.server_address[1]}', H
    srv.shutdown()


# ---- kpc_host_rules (and its engine vendor copy)
@pytest.mark.parametrize('u', BAD)
def test_host_rules_refuse_every_form(u): assert not HR.host_ok(u)[0]


@pytest.mark.parametrize('u', GOOD)
def test_host_rules_allow(u): assert HR.host_ok(u)[0]


def test_saved_only_env_adds_never_drops(monkeypatch):
    monkeypatch.setenv('KPC_SAVED_ONLY_HOSTS', 'gis.example.net')
    assert not HR.host_ok('https://apps.fs.usda.gov/x')[0] and not HR.host_ok('https://services1.arcgis.com/x')[0]
    assert not HR.host_ok('https://gis.example.net/x')[0] and HR.host_ok('https://gis.example.org/x')[0]


def test_vendor_copies_identical():
    for f in ('kpc_host_rules.py', 'kpc_manners.py'):
        assert (S / 'draft/tools/kpc_engine/vendor' / f).read_bytes() == (S / f).read_bytes(), f


# ---- kpc_manners: every redirect hop goes through the host rules before it is followed
def _manners():
    import kpc_manners as K
    K = importlib.reload(K)
    M = K.Manners('test'); M._pace = lambda *a, **k: None
    return K, M


@pytest.mark.parametrize('path', ['/to-services', '/to-fs', '/to-rel'])
def test_manners_redirect_hop_refused_before_any_dial(server, offline, path):
    base, H = server
    K, M = _manners()
    st = M.get(base + path)[0]
    assert st == 'host-rule' and not offline and M.stat['strikes'] == 0, (st, offline)


def test_manners_direct_forbidden_host_no_robots_read(offline):
    K, M = _manners()
    assert M.get('https://services1.arcgis.com./x/arcgis/rest/services/A/FeatureServer/0')[0] == 'host-rule' and not offline and not M.robots


def test_manners_https_to_http_hop_refused():
    K, _ = _manners()
    req = urllib.request.Request('https://gis.example.org/a')
    with pytest.raises(K.HostRuleRefused):
        urllib.request.HTTPRedirectHandler().redirect_request(req, None, 302, 'Found', {}, 'http://gis.example.org/b')
    assert urllib.request.HTTPRedirectHandler().redirect_request(req, None, 302, 'Found', {}, 'https://gis.example.org/b') is not None


def test_manners_allowed_host_still_read(server):
    base, H = server
    K, M = _manners()
    assert M.get(base + '/data.json')[0] == 200


# ---- the shared polite web reader (draft/tools/_common/polite.py, pasted into the built tools)
def _polite():
    ns = {}
    src = (S / 'draft/tools/_common/polite.py').read_text(encoding='utf-8')
    exec('import hashlib, json, os, re, time\nfrom datetime import datetime\nfrom urllib.parse import urlparse\nimport requests\n' + src, ns)
    return ns


@pytest.mark.parametrize('u', BAD + ['https://services.arcgis.com/OtherOrg/arcgis/rest/services/P/FeatureServer/0', 'https://services-eu1.arcgis.com/x'])
def test_polite_banned_forms(u): assert _polite()['banned'](u)


def test_polite_allowed_and_selftest():
    P = _polite()
    assert not any(P['banned'](u) for u in GOOD)
    assert P['polite_selftest']() == []


def test_polite_no_robots_read_for_saved_only_host():
    P = _polite(); w = P['Polite'](cache=None, gap=1.0); w.gap = 0; calls = []
    w._one = lambda url, method='GET', data=None, headers=None: (calls.append(url), (200, {}, b'', url))[1]
    assert w.get('https://services7.arcgis.com/x/arcgis/rest/services/P/FeatureServer/0')[0] == 'banned' and not calls


# ---- kpc_convert_layers (the geo libraries are stubbed when missing: only the polite HTTP part is tested)
def _convert(monkeypatch):
    for name, attrs in (('pyogrio', {}), ('pyogrio.raw', {}), ('shapely', {}), ('shapely.geometry', {'box': None, 'mapping': None, 'Point': None}),
                        ('pyproj', {'CRS': None, 'Transformer': None})):
        try: importlib.import_module(name)
        except ImportError: monkeypatch.setitem(sys.modules, name, types.SimpleNamespace(**attrs))
    if 'pyogrio.raw' in sys.modules and isinstance(sys.modules['pyogrio'], types.SimpleNamespace): sys.modules['pyogrio'].raw = sys.modules['pyogrio.raw']
    spec = importlib.util.spec_from_file_location('kpc_convert_layers_t', S / 'tools/kpc_convert_layers/kpc_convert_layers.py')
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    m.MIN_DELAY_S = 0
    return m


def test_convert_refused_host_gets_no_request_not_even_robots(monkeypatch, offline):
    C = _convert(monkeypatch); P = C.PoliteSession(); asked = []
    monkeypatch.setattr(P.s, 'get', lambda u, **k: asked.append(u))
    for u in ('https://services1.arcgis.com./x/FeatureServer/0', 'https://u@apps.fs.usda.gov:443/x', '//services3.arcgis.com/x'):
        with pytest.raises(C.Refused): P.get(u)
        assert not P.allowed_by_robots(u)
    assert not asked and not offline


@pytest.mark.parametrize('path', ['/to-services', '/to-fs', '/to-rel'])
def test_convert_redirect_hop_refused_before_any_dial(monkeypatch, server, offline, path):
    base, H = server
    C = _convert(monkeypatch); P = C.PoliteSession()
    with pytest.raises(C.Refused): P.get(base + path)
    assert not offline


def test_convert_robots_5xx_and_no_answer_disallow(monkeypatch, server):
    base, H = server
    C = _convert(monkeypatch)
    H.robots500 = True
    try: assert not C.PoliteSession().allowed_by_robots(base + '/data.json')
    finally: H.robots500 = False
    assert C.PoliteSession().allowed_by_robots(base + '/data.json')   # 404 = no robots file = allowed
    P = C.PoliteSession()
    def down(*a, **k): raise C.requests.ConnectionError('no answer')
    monkeypatch.setattr(P.s, 'get', down)
    assert not P.allowed_by_robots('https://gis.example.org/data.json')
