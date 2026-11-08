#!/usr/bin/env python3
"""Nov 7 2026 (Brandon 7:30 PM CST 'no reason to look for same park over and over'; 7:36 PM 'everything we're sitting on goes in
FIRST'; 7:39 PM 'Enter everything you got'). Checks the outline-source ledger, the documents rows, the convert list and its licence
holds, the outside agent's converter manners (fake network only: robots 403 = refused, blocked list, hub delay, redirect to a
blocked host, token only for raw.githubusercontent.com) and that its two workflows are manual, read-only and inject-safe."""
import csv, gzip, importlib.util, json, os, pathlib, sys, types
import datetime as dt

ROOT = pathlib.Path(__file__).resolve().parents[1]
os.chdir(ROOT)
sys.path.insert(0, str(ROOT / '.github/scripts'))
FAILS = []


def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: FAILS.append(msg)


# ---- the ledger ----
L = json.loads(gzip.open('data/waiting/outline-sources/ledger.json.gz').read())
rows = L['rows']
us = [k for k in rows if k.startswith('US-')]; ca = [k for k in rows if k.startswith('CA-')]
check(len(us) == 1500 and len(ca) == 1488, f'every sheet park has a ledger row (US {len(us)}/1500, CA {len(ca)}/1488)')
check(os.path.getsize('data/waiting/outline-sources/ledger.json.gz') < 1_000_000, 'ledger stays small (gz)')
need = {'area', 'name', 'type', 'conf', 'verdict', 'src', 'date'}
check(all(need <= set(v) for v in rows.values()), 'every ledger row has area, name, type, conf, verdict, src, date (outline / pdf / parcel only when the sheet had one)')
check(all(v['date'] == '2026-11-07' for v in rows.values()), 'every row dated Nov 7 2026')
BAN = ('33toooklri9xpic7u', 'ncnhde.natureserve.org')
wired = [o for v in rows.values() for o in v.get('outline', []) if 'wired' in (o.get('status') or '')]
check(not any(b in (o.get('url') or '').lower() for o in wired for b in BAN), 'no banned host is marked wired in the ledger')

import kpc_outline_ledger as OL  # noqa: E402
check(OL.needs_search('US-99999', rows), 'a park with no row still needs a search')
some = next(k for k, v in rows.items() if v['verdict'].startswith('source already'))
check(not OL.needs_search(some, rows), f'{some} (already sourced) is skipped')
nf = next(k for k, v in rows.items() if v['verdict'] == 'nothing found' and '|' not in k and len(OL.rows_for(k, rows)) == 1)
check(not OL.needs_search(nf, rows, today=dt.date(2026, 11, 20)) and OL.needs_search(nf, rows, today=dt.date(2027, 3, 1)),
      f'{nf} (nothing found) waits 60 days before another search')
check(OL.load('/nonexistent.json.gz') == {}, 'a missing ledger reads as nothing searched yet')
check('kpc_outline_ledger' in open('.github/scripts/kpc_missing_lists.py').read(), 'the nightly missing lists say when a park was already searched')

# ---- documents rows (kpc_docs_merge shape) ----
D = json.load(open('data/intake/docs-found-outside-nov7.json'))
check(len(D) == 128, f'128 park maps queued for the documents merge ({len(D)})')
check(all({'st', 'page', 'map', 'kind', 'date', 'agency', 'notes'} <= set(v) and len(v['st']) == 2 for v in D.values()),
      'every documents row has st (2 letters), page, map, kind, date, agency, notes')
share = {}
for v in D.values(): share[v['map']] = share.get(v['map'], 0) + 1
check(max(share.values()) <= 3, 'no map shared by more than 3 parks (the merge would keep those as notes only)')

# ---- convert list + licence holds ----
C = list(csv.DictReader(open('data/waiting/outline-sources/convert-list-nov7.csv', newline='')))
check(len(C) == 129, f'convert list has 129 rows ({len(C)})')
T = 'tools/kpc_layers_nov7'
LIC = list(csv.DictReader(open(f'.github/scripts/draft/{T}/licences.csv', newline='')))
held = sorted(int(r['row']) for r in LIC if r['hold'].strip())
check(held == [12, 13, 14, 15, 32, 38, 50, 51, 52, 54], f'licence holds: the 7 unnamed licences + rows 38, 50, 51 ({held})')
plan = list(csv.DictReader(open(f'.github/scripts/draft/{T}/reports/conversion_plan.csv', newline='')))
check(sorted(int(r['row']) for r in plan if r.get('hold_for_check', '').strip().lower() in ('yes', 'true', '1') or
             (r.get('hold_for_check') or '').strip().startswith('hold')) == held, 'conversion plan marks the same rows hold_for_check')

# ---- converter manners (fake network only) ----
calls = []


class Resp:
    def __init__(self, code, text='', headers=None):
        self.status_code, self.text, self.headers = code, text, headers or {}


ROB = {'https://ok.example': (200, 'User-agent: *\nDisallow: /private\n'), 'https://none.example': (404, ''),
       'https://services9.arcgis.com': (403, ''), 'https://www.data.hub.arcgis.com': (404, ''),
       'https://raw.githubusercontent.com': (404, '')}
PAGES = {'https://ok.example/go': Resp(302, headers={'Location': 'https://ncnhde.natureserve.org/x'}),
         'https://ok.example/hop': Resp(302, headers={'Location': 'https://none.example/data'})}


class RE(Exception): pass


def fake_get(url, headers=None, **kw):
    calls.append((url, dict(headers or {})))
    if url.endswith('/robots.txt'):
        c, t = ROB.get(url[:-len('/robots.txt')], (503, ''))
        return Resp(c, t)
    return PAGES.get(url, Resp(200, 'ok'))


fake = types.ModuleType('requests'); fake.get = fake_get; fake.RequestException = RE
fake.compat = types.SimpleNamespace(urljoin=__import__('urllib.parse').parse.urljoin)
sys.modules['requests'] = fake
spec = importlib.util.spec_from_file_location('conv', f'.github/scripts/draft/{T}/convert_layers.py')
CV = importlib.util.module_from_spec(spec); spec.loader.exec_module(CV)
CV.time = types.SimpleNamespace(time=lambda: 0.0, sleep=lambda s: None)
CV.DEFAULT_DELAY = 0.0


def refused(url):
    try: CV.polite_get(url); return False
    except RuntimeError: return True


check(refused('https://services9.arcgis.com/abc/arcgis/rest/services/X/FeatureServer/0'), 'robots.txt 403 = the host is refused')
check(refused('https://down.example/x'), 'robots.txt 5xx = the host is refused')
check(refused('https://ok.example/private/x') and not refused('https://ok.example/open'), 'robots.txt rules are followed')
check(not refused('https://none.example/data'), 'robots.txt 404 = allowed')
check(refused('https://SERVICES.arcgis.com/33TOOKLRI9XPIC7U/x') and refused('https://NCNHDE.natureserve.org/y'), 'blocked list, any case')
n = len(calls); r = refused('https://ok.example/go')
check(r and not any('ncnhde' in u for u, _ in calls[n:]), 'a redirect to a blocked host is refused before it is asked')
check(not refused('https://ok.example/hop') and calls[-1][0] == 'https://none.example/data', 'a redirect to an allowed host is followed')
check(CV._host_delay('https://www.data.hub.arcgis.com/x', CV._robots_for('https://www.data.hub.arcgis.com/x')) >= 60, 'hub portal: 60 s delay')
os.environ['GITHUB_TOKEN'] = 'fake-test-token'
CV.polite_get('https://raw.githubusercontent.com/a/b/c.json'); CV.polite_get('https://none.example/data')
tok = [u for u, h in calls if 'Authorization' in h]
check(tok and all(u.startswith('https://raw.githubusercontent.com/') for u in tok), 'the token only ever goes to raw.githubusercontent.com')
os.environ.pop('GITHUB_TOKEN')

# ---- workflows: manual, read only, no injection, artifact only ----
for wf in ('kpc-convert-sources-nov7.yml', 'kpc-match-trails-nov7.yml'):
    s = open(f'.github/workflows/{wf}').read()
    import yaml  # noqa: E402
    y = yaml.safe_load(s); on = y.get('on') or y.get(True)
    check(list(on) == ['workflow_dispatch'], f'{wf}: workflow_dispatch only (no schedule)')
    check(y.get('permissions') == {'contents': 'read'}, f'{wf}: contents read')
    runs = ' '.join(st.get('run', '') for j in y['jobs'].values() for st in j['steps'])
    check('${{' not in runs, f'{wf}: no ${{{{ }}}} pasted into a shell line')
    check('git push' not in s and 'git commit' not in s, f'{wf}: nothing committed or pushed')

print('ALL PASS' if not FAILS else f'{len(FAILS)} FAILED')
sys.exit(1 if FAILS else 0)
