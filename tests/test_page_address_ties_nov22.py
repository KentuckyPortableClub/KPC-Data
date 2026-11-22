"""22 Nov 2026 (owner's GO): a park's own page address is an id, so the three agency lists that tie a page address column to a map
id (Florida DEP, Manitoba Parks, Washington State Parks) become real ties. Invented parks and invented addresses only.
Fails without the change: no page_address in either tool, no 'page address' id from the link reader, the list rows are not
cleaned, the three agencies are off, and the packer does not pass an ArcGIS-hosted page-address list to the keeper."""
import importlib.util, json, os, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github/scripts'))
sys.path.insert(0, str(ROOT / '.github/scripts/pc'))
ok = True


def check(msg, cond):
    global ok
    print(('ok   ' if cond else 'FAIL ') + msg)
    ok = ok and bool(cond)


def load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


import kpc_agency_lists as AL  # noqa: E402
LI = load('kpc_link_ids_t', '.github/scripts/draft/tools/kpc_link_ids/kpc_link_ids.py')
PF = load('kpc_park_facts_t', '.github/scripts/draft/tools/kpc_park_facts/kpc_park_facts.py')

# 1. one cleaning, both sides
samples = ['https://www.floridastateparks.org/parks-and-trails/Invented-Springs-State-Park/',
           'http://floridastateparks.org/parks-and-trails/invented-springs-state-park?x=1#top',
           'floridastateparks.org/parks-and-trails/invented-springs-state-park',
           'https://WWW.Parks.WA.gov/9999/Invented-Point', 'https://www.gov.mb.ca/sd/parks/invented-lake/', '',
           'mailto:x@invented.example', 'https://invented.example', 'not a link']
check('both tools clean a page address the same way', all(hasattr(m, 'page_address') for m in (AL, LI)) and
      all(AL.page_address(s) == LI.page_address(s) for s in samples))
check('scheme, www, case, trailing slash, query and #part are dropped', len({AL.page_address(s) for s in samples[:3]}) == 1 and
      AL.page_address(samples[0]) == 'floridastateparks.org/parks-and-trails/invented-springs-state-park')
check('no host+path = no page address', [AL.page_address(s) for s in samples[5:]] == ['', '', '', ''])

# 2. the link reader gives it only to an agency's own page with no known id
r = LI.read_link('https://www.floridastateparks.org/parks-and-trails/invented-springs-state-park', 'Invented Springs State Park', 'State Park', 'US-FL')
check('an own page on an agency site with no id rule is identified by its page address',
      (r['id_kind'], r['id_value'], r['id_grade'], r['page']) ==
      ('page address', 'FLORIDASTATEPARKS.ORG/PARKS-AND-TRAILS/INVENTED-SPRINGS-STATE-PARK', 'known', 'own page'))
r2 = LI.read_link('https://www.floridastateparks.org/things-to-do', 'Invented Springs State Park', 'State Park', 'US-FL')
check('a page that is not the park\'s own gets no page address', r2['id_kind'] != 'page address')
r3 = LI.read_link('https://invented-blog.example.com/invented-springs-state-park', 'Invented Springs State Park', 'State Park', 'US-FL')
check('a page off agency and government sites gets no page address', r3['id_kind'] != 'page address')

# 3. the agency list rows are cleaned the same way, and a clash still means no tie
a = {'link_kind': 'page address', 'web_id': {'column': 'URL', 'regex': '(nothing)'}, 'map': {'layer': 'sgzza', 'field': 'UNIT_ID', 'value': 'UNIT_ID'}}
rows = [{'URL': 'https://www.floridastateparks.org/parks-and-trails/Invented-Springs-State-Park/', 'UNIT_ID': '9001'},
        {'URL': 'https://floridastateparks.org/parks-and-trails/invented-bluff', 'UNIT_ID': '9002'},
        {'URL': 'http://floridastateparks.org/parks-and-trails/invented-bluff/', 'UNIT_ID': '9003'},
        {'URL': '', 'UNIT_ID': '9004'}]
xw, clashes = AL.crosswalk_rows(rows, a)
check('a page-address list gives cleaned web ids (the regex is not used)', [x['web_id'] for x in xw] ==
      ['FLORIDASTATEPARKS.ORG/PARKS-AND-TRAILS/INVENTED-SPRINGS-STATE-PARK'] and xw[0]['map_id'] == '9001')
check('one address on two map ids is a clash, not a tie', clashes == 1)

# 4. the park facts tie the park through the list (the keys read map_tie)
links = {'US-9001': dict(r, usable=True), 'US-9002': dict(r2, usable=True)}
ties = {('page address', x['web_id']): {'layer': x['map_layer'], 'field': x['map_field'], 'id': x['map_id']} for x in xw}
n = PF.add_map_ties(links, ties)
check('the park whose own page is on the list is tied to its map id', n == 1 and links['US-9001'].get('map_tie', {}).get('id') == '9001'
      and 'map_tie' not in links['US-9002'])

# 5. the config: exactly the three tied lists are on, each reads cleanly inside the keeper's jobs only
cfg = json.load(open(ROOT / '.github/agency-lists.json', encoding='utf-8'))
on = [x for x in cfg['agencies'] if x.get('enabled')]
check('exactly the three lists that tie are on', sorted(x['agency'] for x in on) ==
      ['Florida DEP Division of Recreation and Parks (State Parks)', 'Manitoba Parks', 'Washington State Parks'])
check('each is a page-address list with a row tie and no differences', all(x['link_kind'] == 'page address' and
      __import__('re').search(r'\(\d+ same / 0 different', x['status']) for x in on))
check('each asks the layer for the two columns only, no shapes', all('returnGeometry=false' in x['source_url'] and 'f=json' in x['source_url'] for x in on))
old = os.environ.pop('KPC_KEEPER_HOST_RULES', None)
try:
    os.environ['KPC_KEEPER_HOST_RULES'] = 'owner-2026-11-15'
    import kpc_host_rules as HR, importlib
    importlib.reload(HR); importlib.reload(AL)
    check('inside the keeper\'s jobs all three pass every check', all(AL.problems(x) == [] for x in on))
    del os.environ['KPC_KEEPER_HOST_RULES']
    importlib.reload(HR); importlib.reload(AL)
    arc = [x for x in on if 'arcgis.com' in x['source_url']]
    check('outside the keeper\'s jobs the ArcGIS-hosted ones are refused (saved copies only)', arc and all(AL.problems(x) for x in arc))
finally:
    if old is not None: os.environ['KPC_KEEPER_HOST_RULES'] = old

# 6. the PC packer: no approval file = every tied proposal; an untied one is left out; page address set from an address column
import kpc_upload_pack as K  # noqa: E402
check('no approval list means every proposal (agency data needs no approval)', K.approved_agencies('/nonexistent/approved.txt') is None)
r = __import__('subprocess').run([sys.executable, '-B', str(ROOT / '.github/scripts/pc/kpc_upload_pack.py'), '--selftest'], capture_output=True, text=True)
check('the packer self-test passes (tie needed, page address kind)', r.returncode == 0 and 'ALL PASS' in r.stdout)

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
