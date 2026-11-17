#!/usr/bin/env python3
"""Nov 17: Kentucky docs were held by the waiting room (F-D3) for two dead rules
links. (1) lists.json sent all Kentucky State Parks to https://parks.ky.gov/park-rules,
which is HTTP 404; the statewide page is now https://parks.ky.gov/info/things-to-know.
The same KY block sent 18 Fish & Wildlife areas to fw.ky.gov/Hunt/Pages/Public-Hunting-Areas.aspx
(HTTP 404); the renamed page is fw.ky.gov/Hunt/Pages/Public-Land-Hunting.aspx.
(2) The FWS rules pattern built https://www.fws.gov/refuge/green-river/visit-us/rules-policies,
which is HTTP 404: FWS moved that refuge to /locations/green-river-national-wildlife-refuge,
and its rules page is .../rules-and-policies. The bot must try the new FWS address,
keep the old one first where it still opens (no churn), and read a /locations/ page
address as the refuge's slug. Offline: the network is mocked, nothing in the repo is written."""
import json, os, pathlib, sys, tempfile

HERE = pathlib.Path(__file__).resolve().parent.parent
os.environ['OUT'] = tempfile.mkdtemp(prefix='kpc-docs-ky404-')
sys.path.insert(0, str(HERE / '.github' / 'scripts'))
import kpc_docs_bot as B  # noqa: E402

ok = True


def check(cond, msg):
    global ok
    print(('PASS ' if cond else 'FAIL ') + msg)
    ok = ok and bool(cond)


OLD_KY = 'https://parks.ky.gov/park-rules'
NEW_KY = 'https://parks.ky.gov/info/things-to-know'
OLD_GR = 'https://www.fws.gov/refuge/green-river/visit-us/rules-policies'
NEW_GR = 'https://www.fws.gov/locations/green-river-national-wildlife-refuge/rules-and-policies'
YAZOO = 'https://www.fws.gov/refuge/yazoo/visit-us/rules-policies'           # old address still opens
COLDWATER_NEW = 'https://www.fws.gov/locations/coldwater-river-national-wildlife-refuge/rules-and-policies'
LIVE = {NEW_KY, NEW_GR, YAZOO, COLDWATER_NEW}   # everything else answers 404, like the live sites did on Nov 17
CALLS = []


def fake_get(u, rng=None, timeout=40, head=False):
    CALLS.append(u)
    if u in LIVE: return 200, {}, b'<html><title>Rules</title></html>', u
    return 404, {}, b'', u


B.get = fake_get

# (1) lists.json: the Kentucky State Parks rules page is the live statewide page, not the 404
lists = json.loads((HERE / 'data' / 'docs' / 'lists.json').read_text(encoding='utf-8'))['areas']
ky = lists.get('US-KY', {}).get('parks.ky.gov', {})
check(ky.get('rules') == NEW_KY, f'lists.json US-KY parks.ky.gov rules is {NEW_KY} (got {ky.get("rules")!r})')
check(OLD_KY not in json.dumps(lists), 'the dead parks.ky.gov/park-rules address is gone from lists.json')
# the same KY block's Fish & Wildlife rules page was also HTTP 404 (18 WMAs); its renamed page is live
fw = lists.get('US-KY', {}).get('fw.ky.gov', {})
check(fw.get('rules') == 'https://fw.ky.gov/Hunt/Pages/Public-Land-Hunting.aspx', f'lists.json US-KY fw.ky.gov rules is the live Public Land Hunting page (got {fw.get("rules")!r})')
check('Public-Hunting-Areas.aspx' not in json.dumps(lists), 'the dead fw.ky.gov Public-Hunting-Areas.aspx address is gone from lists.json')

CALLS.clear()
r = B.rules_for('state', ['https://parks.ky.gov/campbellsville/parks/recreation/green-river-lake-state-park'], [], ky)
check(r.get('status') == 'ok' and r.get('url') == NEW_KY, f'a Kentucky state park gets the statewide rules page, opened ok (got {r})')
check(r.get('rules_scope') == 'agency', 'the statewide page is labelled rules_scope=agency')
check(OLD_KY not in CALLS, 'the dead KY address is never fetched')

# (2) Green River NWR: the park page on file is an old /refuge/green-river/... address
CALLS.clear()
page = 'https://www.fws.gov/refuge/green-river/visit-us/locations/green-river-national-wildlife-refuge'
r = B.rules_for('fws', [page], [], None)
check(r.get('status') == 'ok' and r.get('url') == NEW_GR, f'Green River gets the live FWS rules page (got {r})')
check(r.get('url') != OLD_GR, 'the dead /visit-us/rules-policies address is not kept')

# (3) a park page already on the new /locations/ address gives the same slug and page
check(B.unit_slug('https://www.fws.gov/locations/green-river-national-wildlife-refuge', 'fws') == 'green-river',
      'a /locations/<name>-national-wildlife-refuge page reads as slug green-river')
r = B.rules_for('fws', ['https://www.fws.gov/locations/green-river-national-wildlife-refuge'], [], None)
check(r.get('url') == NEW_GR and r.get('status') == 'ok', f'/locations/ page -> live rules page (got {r})')

# (4) a refuge whose old address still opens keeps it (no churn in other states)
CALLS.clear()
r = B.rules_for('fws', ['https://www.fws.gov/refuge/yazoo/'], [], None)
check(r.get('url') == YAZOO and CALLS[:1] == [YAZOO], f'Yazoo keeps the old address that still opens, tried first (got {r}, calls {CALLS})')

# (5) an underscore slug from an old page address becomes hyphens in the new address
r = B.rules_for('fws', ['https://www.fws.gov/refuge/coldwater_river/'], [], None)
check(r.get('url') == COLDWATER_NEW, f'coldwater_river -> coldwater-river in the /locations/ address (got {r})')

# (6) a fresh record (checked today-ish, ver 7) whose rules page did not open under the old candidates is read
#     again on the next run; a fresh record with ok rules is still skipped; a skipped read keeps the old record
#     exactly and gets no rules_ver, so it is tried again next run
import time  # noqa: E402
today = time.strftime('%Y-%m-%d')
OUTD = pathlib.Path(os.environ['OUT']); B.OUT = OUTD
dead = {'n': 'Dead Rules Park', 't': 'State Park', 'page': 'https://parks.ky.gov/x/dead-rules-park', 'checked': today, 'ver': B.VER,
        'map': {'url': '', 'status': 'none'}, 'rules': {'url': OLD_KY, 'how': 'the agency-wide rules page (chat 8 survey)', 'status': 'did not open'}}
good = {'n': 'Good Rules Park', 't': 'State Park', 'page': 'https://parks.ky.gov/x/good-rules-park', 'checked': today, 'ver': B.VER,
        'map': {'url': '', 'status': 'none'}, 'rules': {'url': NEW_KY, 'how': 'x', 'status': 'ok'}}
rest = dict(dead, n='Resting Park', page='https://parks.ky.gov/x/resting-park')
(OUTD / 'US-XX.json').write_text(json.dumps({'area': 'US-XX', 'parks': {'US-0001': dead, 'US-0002': good, 'US-0003': rest}}))
B.park_list = lambda a: {'US-0001': ['Dead Rules Park', '', 'State Park'], 'US-0002': ['Good Rules Park', '', 'State Park'], 'US-0003': ['Resting Park', '', 'State Park']}
B.no_outline = lambda: set(); B.fable_links = lambda: {'_': []}
READ = []


def fake_one(ref, S, lists_, area_):
    READ.append(ref)
    if ref == 'US-0003':
        return {'n': S['name'], 't': '', 'page': S['page'], 'checked': today, 'map': {'url': '', 'status': 'none'},
                'rules': {'url': NEW_KY, 'how': 'x', 'status': 'rules page not read (the site is resting: next run)'}, 'notes': []}
    return {'n': S['name'], 't': '', 'page': S['page'], 'checked': today, 'map': {'url': '', 'status': 'none'},
            'rules': {'url': NEW_KY, 'how': 'the agency-wide rules page (chat 8 survey)', 'status': 'ok'}, 'notes': []}


B.one_park = fake_one
state = {'areas': {}, 'hosts': {}}
B.run_area('US-XX', state, {}, {}, {})
out = json.loads((OUTD / 'US-XX.json').read_text())['parks']
check('US-0001' in READ and 'US-0002' not in READ, f'fresh record with dead rules is read again, fresh ok record is skipped (read {READ})')
check(out['US-0001']['rules']['url'] == NEW_KY and out['US-0001'].get('rules_ver') == B.RULES_VER, 're-read record has the live rules page and rules_ver')
check(out['US-0002'] == good, 'the fresh ok record is left exactly as it was')
check(all(out['US-0003']['rules'].get(k) == rest['rules'][k] for k in ('url', 'how', 'status')) and 'rules_ver' not in out['US-0003'],
      'a skipped (resting) read keeps the old rules URL / how / status exactly, no rules_ver')
READ.clear(); B.run_area('US-XX', state, {}, {}, {})
check(READ == ['US-0003'], f'second run: only the still-unread park is tried again (read {READ})')

print('ALL PASS' if ok else 'FAILED')
sys.exit(0 if ok else 1)
