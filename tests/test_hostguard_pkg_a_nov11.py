#!/usr/bin/env python3
"""Offline test, Nov 11 2026 (host rules, review package A): blocked hosts are refused BEFORE any request (robots.txt included) and a
blocked source is VISIBLE, never quiet fresh data.
  * WDPA phone book: saved copy only. No saved copy = zero requests, a '::warning' saying it needs the saved copy, LEFT=0 (no chain);
    the phone book is written only OUTSIDE the repo (KPC-Data main is published whole to Pages); facts only, never geometry; the
    workflow starts no other run and has no schedule.
  * closures super-bot: the five services*.arcgis.com feeds (CA, WI, FL, MT, NJ) are never asked; their last items are kept marked
    STALE since the last good read and the source says 'blocked'.
  * world harvester installs the host rules (redirect hops too); the GIS hunter says BLOCKED, not 'no answer'; no stale 'ArcGIS REST
    exempt' text is left in the hunters' docs and no code reads KPC_ARCGIS_ROBOTS_EXEMPT.
Every real connection is blocked in this process (socket level) and counted: the count must stay 0.
Run: python3 -B tests/test_hostguard_pkg_a_nov11.py"""
import importlib.util, io, json, os, pathlib, re, socket, subprocess, sys, tempfile, contextlib
import yaml

R = pathlib.Path(__file__).resolve().parents[1]; S = R / '.github' / 'scripts'
sys.path.insert(0, str(S))
ok = True
TRIES = []


def check(c, msg):
    global ok
    print(('PASS ' if c else 'FAIL ') + msg); ok = ok and bool(c)


def _no_net(*a, **k):
    TRIES.append(a[:1]); raise OSError('no network in this test')


socket.getaddrinfo = socket.create_connection = _no_net
socket.socket.connect = lambda self, *a: _no_net(*a)


def load_mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m; spec.loader.exec_module(m); return m


def run_main(mod):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf): mod.main()
    return buf.getvalue()


tmp = pathlib.Path(tempfile.mkdtemp(prefix='kpc-pkg-a-'))
os.environ['STATUS_DIR'] = str(tmp / 'status')
os.environ.pop('GITHUB_STEP_SUMMARY', None)

# ---------------------------------------------------------------- WDPA phone book
os.environ['KPC_WDPA_SAVED'] = str(tmp / 'none' / 'wdpa-saved.geojson')
os.environ['KPC_WDPA_OUT'] = str(tmp / 'private' / 'wdpa-phonebook.json')
PB = load_mod('kpc_wdpa_phonebook', S / 'kpc_wdpa_phonebook.py')
src = (S / 'kpc_wdpa_phonebook.py').read_text(encoding='utf-8')
check(not re.search(r'https?://\S*arcgis\.com|Manners|urlopen|import requests', src), 'phone book: no WDPA address, no Manners, no urlopen / requests in the script')
cwd = os.getcwd(); os.chdir(tmp)
try:
    n0 = len(TRIES); out = run_main(PB)
    check(len(TRIES) == n0, f'phone book, no saved copy: zero connection attempts ({len(TRIES) - n0})')
    check('::warning' in out and 'needs the saved WDPA copy' in out, 'phone book, no saved copy: a visible warning names the saved copy it needs')
    check('LEFT=0' in out, 'phone book, no saved copy: LEFT=0 (nothing to chain)')
    check(not (tmp / 'private' / 'wdpa-phonebook.json').exists() and not (tmp / 'data' / 'intake').exists(), 'phone book, no saved copy: nothing written')
    brd = json.load(open(tmp / 'status' / 'board.json')) if (tmp / 'status' / 'board.json').exists() else {}
    row = (brd.get('bots') or {}).get('WDPA phone book') or {}
    check(row.get('result') == 'amber' and 'saved WDPA copy' in row.get('made', ''), f'phone book: status board says amber + needs the saved copy ({row.get("result")})')
finally: os.chdir(cwd)

# the private-file rule (the KPC-Links master rule): a path inside the repo is refused, nothing written there
okp, why = PB.private_path_ok(R / 'data' / 'intake' / 'phonebook.json')
check(not okp and 'private' in why, 'phone book: an output path inside the repo is refused')
check(PB.private_path_ok(tmp / 'x.json')[0], 'phone book: a path outside the repo is allowed')
dflt = pathlib.Path(os.path.expanduser('~')) / 'kpc-private' / 'wdpa-phonebook.json'
check(PB.private_path_ok(dflt)[0], 'phone book: the default output (~/kpc-private/) is outside the repo')
os.environ['KPC_WDPA_OUT'] = str(R / 'data' / 'intake' / 'phonebook.json')
PB2 = load_mod('kpc_wdpa_phonebook_in_repo', S / 'kpc_wdpa_phonebook.py')
out = run_main(PB2)
check('inside' in out and not (R / 'data' / 'intake' / 'phonebook.json').exists(), 'phone book: KPC_WDPA_OUT inside the repo = refused with a note, nothing written')

# with a small saved copy: facts only, no geometry, no coordinates
saved = tmp / 'saved' / 'wdpa.geojson'; saved.parent.mkdir(parents=True)
saved.write_text(json.dumps({'type': 'FeatureCollection', 'features': [
    {'type': 'Feature', 'properties': {'WDPAID': 1, 'NAME': 'Test Park', 'MANG_AUTH': 'Test Agency', 'ISO3': 'XXX', 'GIS_AREA': 9},
     'geometry': {'type': 'Polygon', 'coordinates': [[[-85.0, 37.0], [-84.0, 37.0], [-84.0, 38.0], [-85.0, 38.0], [-85.0, 37.0]]]}}]}))
(tmp / 'w' / 'data' / 'pota' / 't').mkdir(parents=True)
(tmp / 'w' / 'data' / 'pota' / 't' / 'x.json').write_text(json.dumps([['US-0001', 'Inside', 37.5, -84.5], ['US-0002', 'Outside', 30.0, -90.0]]))
os.environ['KPC_WDPA_SAVED'] = str(saved); os.environ['KPC_WDPA_OUT'] = str(tmp / 'private2' / 'pb.json'); os.environ['LINKS'] = str(tmp / 'nolinks')
PB3 = load_mod('kpc_wdpa_phonebook_saved', S / 'kpc_wdpa_phonebook.py')
os.chdir(tmp / 'w')
try:
    n0 = len(TRIES); out = run_main(PB3)
finally: os.chdir(cwd)
book = json.load(open(tmp / 'private2' / 'pb.json'))
txt = json.dumps(book)
check(len(TRIES) == n0 and 'no request made' in out, 'phone book, saved copy: lookups made with zero connection attempts')
check(book.get('US-0001', {}).get('h') == [{'id': 1, 'name': 'Test Park', 'auth': 'Test Agency', 'iso3': 'XXX'}] and book.get('US-0002', {}).get('h') == [],
      f'phone book, saved copy: the pin inside gets the agency facts, the pin outside gets none ({book})')
check(not re.search(r'coordinates|geometry|GIS_AREA|-85\.0|37\.0', txt), 'phone book, saved copy: no geometry, coordinates or other fields stored')

# the published paths: KPC-Data main is copied whole to the site branch (Pages); the phone book must not be in the repo at all
# Nov 11 (site filter): the move now lives in .github/scripts/kpc_site_publish.sh; with the filter on, only allow-listed paths are
# published, but with KPC_SITE_FILTER=off (the rollback) every tracked path is again: so the phone book must still never be in the repo
ps = (R / '.github' / 'workflows' / 'kpc-pages-sync.yml').read_text(encoding='utf-8')
pub = R / '.github' / 'scripts' / 'kpc_site_publish.sh'
pubt = pub.read_text(encoding='utf-8') if pub.exists() else ''
check((('git/refs/heads/site -f sha=$M' in ps) or ('kpc_site_publish.sh' in ps and 'git/refs/heads/site" -f sha="$M"' in pubt)) and (R / '.nojekyll').exists(),
      'Pages copy: the site branch can be moved to main (every tracked path published: the filter-off rollback)')
tracked = subprocess.run(['git', 'ls-files', 'data/intake'], cwd=R, capture_output=True, text=True).stdout.split()
check(not [f for f in tracked if 'phonebook' in f or 'wdpa' in f.lower()], f'no WDPA phone book file is tracked in the repo (published paths): {[f for f in tracked if "phonebook" in f]}')
wf_txt = (R / '.github' / 'workflows' / 'kpc-wdpa-phonebook.yml').read_text(encoding='utf-8')
wf = yaml.safe_load(wf_txt); on = wf.get(True) or wf.get('on') or {}
live = [l for l in wf_txt.split('\n') if not l.lstrip().startswith('#')]
check('workflow_dispatch' in on and 'schedule' not in on and wf.get('jobs', {}).get('book'), 'phone book workflow: by hand only, job intact')
check(not any('gh workflow run' in l or 'actions: write' in l for l in live), 'phone book workflow: starts no other run (no self-dispatch, no actions: write)')
check(not any('data/intake/phonebook' in l for l in live), 'phone book workflow: saves no phone book file into the repo')

# ---------------------------------------------------------------- closures super-bot
os.environ.update({'OFFLINE': '1', 'OUT': str(tmp / 'closures'), 'LINKS': str(tmp / 'nolinks'), 'BROWSER': '0'})
CB = load_mod('kpc_closures_bot', S / 'kpc_closures_bot.py')
blocked = {sid for sid in CB.FEED_URLS if CB.feed_blocked(sid)}
check(blocked == {'ca-parks', 'wi-dnr', 'fl-parks', 'mt-fwp', 'nj-parks'}, f'closures: exactly the five services*.arcgis.com feeds are blocked ({sorted(blocked)})')
calls = []


class SpyM:
    stat = {}
    def get(self, u, **k): calls.append(u); return 'offline', {}, b'', u


CB.M = SpyM()
(tmp / 'closures').mkdir(parents=True, exist_ok=True)
old_item = {'id': 'x-ca-1', 'src': 'ca-parks', 'ref': 'US-0001', 'class': 'part', 'kind': 'Closure', 'details': 'The Big Basin Road is closed to all vehicles until further notice.', 'seen': '2026-10-20', 'to': '2099-01-01'}
json.dump({'ver': CB.VER, 'items': [old_item], 'sources': {'ca-parks': {'ok': True, 'last_ok': '2026-10-20', 'n': 1}}}, open(tmp / 'closures' / 'US-CA.json', 'w'))
state, review = {'areas': {}, 'hosts': {}}, {}
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    try: CB.process_area(CB._PlainKey(), 'US-CA', state, review)
    except Exception as e: print('process_area stopped:', type(e).__name__, e)
log = buf.getvalue()
d = json.load(open(tmp / 'closures' / 'US-CA.json'))
s = (d.get('sources') or {}).get('ca-parks') or {}
check(not [u for u in calls if 'arcgis.com' in u], f'closures: the blocked CA feed is never asked, not even through Manners ({[u for u in calls if "arcgis" in u][:2]})')
check(s.get('blocked') is True and s.get('ok') is False and 'STALE since 2026-10-20' in s.get('why', ''), f'closures: the CA source says blocked + STALE since its last good read ({s.get("why")})')
kept = [it for it in d.get('items', []) if it.get('src') == 'ca-parks']
check(kept and all('STALE since 2026-10-20' in (it.get('stale') or '') for it in kept), 'closures: the kept CA item is marked stale, never carried as current')
check('STALE since 2026-10-20' in log, 'closures: the log says STALE since')
check(len(TRIES) == n0, 'closures: zero connection attempts')

# ---------------------------------------------------------------- world harvester, GIS hunter, stale exemption text
r = subprocess.run([sys.executable, '-B', '-c', "import sys, socket, urllib.request; sys.path.insert(0, sys.argv[1]); "
                    "socket.getaddrinfo = socket.create_connection = lambda *a, **k: (_ for _ in ()).throw(SystemExit('NETWORK TRIED')); "
                    "import kpc_world_harvest\n"
                    "try: urllib.request.urlopen('https://services9.arcgis.com/robots.txt', timeout=2); print('NOT REFUSED')\n"
                    "except Exception as e: print('REFUSED', type(e).__name__)", str(S)], capture_output=True, text=True, cwd=str(tmp), timeout=120)
check('REFUSED HostRefused' in r.stdout, f'world harvester: importing it installs the host rules (a services9 robots.txt is refused, no request) {r.stdout.strip()[-80:]} {r.stderr.strip()[-200:]}')
os.environ['LINKS'] = str(tmp / 'nolinks')
try:
    G = load_mod('kpc_gis_hunter', S / 'kpc_gis_hunter.py')
    try: G.arc('https://services1.arcgis.com/abc/arcgis/rest/services/Parks/FeatureServer/0', {'where': '1=1'}); msg = 'no error'
    except RuntimeError as e: msg = str(e)
    check(msg.startswith('BLOCKED') and len(TRIES) == n0, f'GIS hunter: a services1 layer is BLOCKED (not "no answer"), zero requests ({msg[:70]})')
except Exception as e: check(False, f'GIS hunter import: {type(e).__name__}: {e}')
for f in ('kpc_gis_hunter.py', 'kpc_detective_bot.py', 'kpc_intake_bot.py'):
    t = (S / f).read_text(encoding='utf-8')
    check(not re.search(r'ArcGIS REST (API path )?exempt\b|with the ArcGIS REST (API path )?exemption', t), f'{f}: no stale "ArcGIS REST exempt" claim')
READ_RX = re.compile(r"(environ\.get|getenv)\(\s*['\"]KPC_ARCGIS_ROBOTS_EXEMPT|environ\[\s*['\"]KPC_ARCGIS_ROBOTS_EXEMPT['\"]\s*\](?!\s*=)")
readers = [str(p.relative_to(R)) for p in S.rglob('*.py') if READ_RX.search(p.read_text(encoding='utf-8', errors='replace'))]
check(not readers, f'no code reads KPC_ARCGIS_ROBOTS_EXEMPT (the exemption is gone): {readers}')
# the nov7 converter (kpc-convert-sources-nov7.yml, and match_trails.py through it): no robots.txt read of a blocked host
try:
    CV = load_mod('convert_layers', S / 'draft' / 'tools' / 'kpc_layers_nov7' / 'convert_layers.py')
    import requests.adapters as _ra
    sent = []
    _ra.HTTPAdapter.send = (lambda orig: (lambda self, req, *a, **k: (sent.append(req.url), orig(self, req, *a, **k))[1]))(_ra.HTTPAdapter.send) \
        if not getattr(_ra.HTTPAdapter.send, '_pkg_a', False) else _ra.HTTPAdapter.send
    for u in ('https://services3.arcgis.com/abc/arcgis/rest/services/T/FeatureServer/0/query?where=1%3D1',
              'https://apps.fs.usda.gov/arcx/rest/services/EDW/EDW_TrailNFSPublish_01/MapServer/0'):
        try: CV.polite_get(u); r = 'asked'
        except RuntimeError as e: r = str(e)
        check(r.startswith('BLOCKED host') and not sent and not CV._robots and len(TRIES) == n0,
              f'nov7 converter: {u.split("/")[2]} is BLOCKED before any request, robots.txt included ({r[:50]})')
    try: import requests; requests.get('https://services1.arcgis.com/robots.txt', timeout=2); r = 'asked'
    except Exception as e: r = type(e).__name__  # noqa: BLE001
    check('Refused' in r and len(TRIES) == n0, f'nov7 converter: importing it installs the host rules for requests too ({r})')
except ImportError as e: check(False, f'nov7 converter import: {e}')
check(len(TRIES) == 0, f'the whole test made zero connection attempts ({len(TRIES)})')
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
