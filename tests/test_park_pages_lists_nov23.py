#!/usr/bin/env python3
"""Page reader, 23 Nov 2026 (owner: "the ones with several parks can we get on the right page?" and "U sure the not offical
pages are not offical"). (1) A page many parks share is followed to the ONE link whose words are this park's name, and that
page is read as the park's own. (2) A list with no link of its own (a table of every WMA): only the one row naming the park is
read. (3) A park read before this rule is read again, even when the list page did not change. (4) Governments wrongly marked
'not official' (county and town addresses, Quebec towns, agencies' own ArcGIS sites, cities) now count; Wikipedia, plain
arcgis.com and map sites still do not. Invented parks, offline fixtures. Prints PASS / FAIL, ends ALL PASS or SOME FAILED."""
import json, pathlib, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github/scripts'))
import kpc_park_pages_rules as R
ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


H = 'https://dnr.invented.gov'
LIST = H + '/wma/'
TABLE = H + '/wma-listing'
WORDS = 'Words about the place. ' * 40
NAMES = {'US-9501': 'Cedar Hollow Wildlife Management Area', 'US-9502': 'Fox Run Wildlife Management Area',
         'US-9503': 'Elk Bend Wildlife Management Area',
         'US-9511': 'Blue Ridge Wildlife Management Area', 'US-9512': 'Blue Ridge North Wildlife Management Area',
         'US-9513': 'Overlook Wildlife Management Area'}
LINK = {'US-9501': H + '/wma/cedar-hollow', 'US-9502': H + '/wma/fox-run', 'US-9503': H + '/wma/elk-bend'}
LIST_BODY = ('<html><head><title>Wildlife Management Areas</title></head><body><h1>Wildlife Management Areas</h1><p>' + WORDS
             + '</p><ul>' + ''.join(f'<li><a href="{LINK[r]}">{NAMES[r].replace(" Wildlife Management Area", " WMA")}</a></li>' for r in LINK)
             + '</ul></body></html>')
OWN = lambda r: (f'<html><head><title>{NAMES[r]} | Invented DNR</title></head><body><h1>{NAMES[r]}</h1><p>{WORDS}</p>'
                 '<p>The area covers 1,234 acres.</p></body></html>')
TABLE_BODY = ('<html><head><title>WMA Listing</title></head><body><h1>Wildlife Management Areas - Listing</h1><p>' + WORDS + '</p>'
              '<table><tr><th>County</th><th>WMA name</th><th>Location</th></tr>'
              '<tr><td>Divide</td><td>Blue Ridge</td><td>3 miles east of the junction of US Highway 85 and ND Highway 50.</td></tr>'
              '<tr><td>McKenzie</td><td>Overlook</td><td>13 miles west of Watford City.</td></tr>'
              '<tr><td>Burke</td><td>Blue Ridge North</td><td>11 miles north of Columbus.</td></tr></table></body></html>')


def run(t, n, state=None):
    out = t / f'out{n}'; out.mkdir()
    data = t / 'data' / 'parkinfo'; data.mkdir(parents=True, exist_ok=True)
    url = lambda r: LIST if r in LINK else TABLE
    (data / 'US-ZZ.json').write_text(json.dumps({'parks': {r: [NAMES[r], url(r), 'Wildlife Management Area', '', '', 47.0, -101.0, 0, 0, 1]
                                                           for r in NAMES}}), encoding='utf-8')
    pages = {LIST: {'status': 200, 'body': LIST_BODY}, TABLE: {'status': 200, 'body': TABLE_BODY}}
    pages.update({LINK[r]: {'status': 200, 'body': OWN(r)} for r in LINK})
    (t / 'fx.json').write_text(json.dumps({'pages': pages}), encoding='utf-8')
    if state is not None: (out / 'state.json').write_text(json.dumps(state), encoding='utf-8')
    r = subprocess.run([sys.executable, '-B', str(ROOT / '.github/scripts/kpc_park_pages.py'), 'read', '--data', str(t / 'data'), '--out', str(out),
                        '--state', str(out / 'state.json'), '--fixtures', str(t / 'fx.json'), '--today', '2026-11-23', '--areas', 'US-ZZ', '--quiet'],
                       capture_output=True, text=True)
    facts = json.loads((out / 'facts' / 'US-ZZ.json').read_text()).get('parks', {}) if (out / 'facts' / 'US-ZZ.json').is_file() else {}
    st = json.loads((out / 'state.json').read_text()) if (out / 'state.json').is_file() else {}
    return r, facts, st


with tempfile.TemporaryDirectory() as t:
    t = pathlib.Path(t)
    r, f, st = run(t, 1)
    if r.returncode: print(r.stderr[-800:])
    a = f.get('US-9501') or {}
    check('a shared list page is followed to the link that names the park', (a.get('asked') or {}).get('followed') == LINK['US-9501']
          and (a.get('own_page') or {}).get('is') == 'own')
    check('the followed page is read: its name agrees and its size is taken',
          (a.get('name') or {}).get('vs_pota') in ('same', 'same-core') and any(s.get('acres') == 1234 for s in a.get('sizes') or []))
    check('each park on the list gets its own page', all((f.get(x) or {}).get('asked', {}).get('followed') == LINK[x] for x in LINK))
    b = f.get('US-9511') or {}
    check('a table with no links: only the row naming the park is read', (b.get('own_page') or {}).get('is') == 'list-row'
          and 'US Highway 85' in ((b.get('asked') or {}).get('row') or '') and 'Watford' not in ((b.get('asked') or {}).get('row') or ''))
    check('the row confirms the name', (b.get('name') or {}).get('vs_pota') in ('same', 'same-core'))
    c = f.get('US-9512') or {}
    check('a longer name of another park is not mixed up (Blue Ridge vs Blue Ridge North)',
          'Columbus' in ((c.get('asked') or {}).get('row') or '') and 'US Highway 85' not in ((c.get('asked') or {}).get('row') or ''))
    old = {'read': {x: {'url': LIST, 'fingerprint': '', 'date': '2026-11-22', 'kind': 'html'} for x in LINK}}
    # the list page's own fingerprint, as a read under the old rule saved it
    old_fp = (json.loads((t / 'out1' / 'state.json').read_text()).get('fingerprints') or {})
    lf = next((v for k, v in old_fp.items() if k.rstrip('/').endswith('/wma')), '')
    check('the list page keeps its own fingerprint (not the followed page\'s)', bool(lf) and lf not in {st['read'][x].get('fingerprint') for x in LINK})
    for x in LINK:
        old['read'][x]['fingerprint'] = lf
    r, f2, st2 = run(t, 2, state=old)
    check('a park read before this rule is read again and followed, though the list did not change',
          bool(lf) and all((f2.get(x) or {}).get('asked', {}).get('followed') == LINK[x] for x in LINK))

for u, want in (('https://www.co.monroe.pa.us/parks', True), ('https://www.ville.prevost.qc.ca/parc', True),
                ('https://maine.maps.arcgis.com/home/item.html?id=1', True), ('https://www.ottawa.ca/en/parks', True),
                ('https://rigov.sharepoint.com/sites/dem/x.pdf', True), ('https://www.ndow.org/wma/', True),
                ('https://en.wikipedia.org/wiki/X', False), ('https://www.arcgis.com/home/item.html?id=1', False),
                ('https://mapcarta.com/X', False), ('https://www.alltrails.com/x', False)):
    check(f"{'official' if want else 'not official'}: {u.split('/')[2]}", R.official_host(u) == want)
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
