#!/usr/bin/env python3
"""Park page reader, 19 Nov 2026 (hand-off 05, part 1). Offline.

Every reading rule has a plain case, a trap, and a silent case. Every known answer
marked must comes out of its fixture. The reader makes no request here.
Prints PASS / FAIL lines and ends ALL PASS or SOME FAILED.
"""
import datetime, json, os, pathlib, re, shutil, socket, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
FX = ROOT / 'tests/fixtures/park-pages'
S = ROOT / '.github/scripts'
sys.path.insert(0, str(S))
ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


def _no_net(*a, **k):
    raise OSError('test: no network')


socket.socket.connect = _no_net
os.environ['KPC_NO_NET'] = '1'
import kpc_park_pages as PP  # noqa: E402
import kpc_park_pages_rules as R  # noqa: E402
from kpc_manners import browser_picture, Manners  # noqa: E402

ran = subprocess.run([sys.executable, '-B', str(S / 'kpc_park_pages.py'), '--selftest'], capture_output=True, text=True)
check('the reader selftest passes and makes no request', ran.returncode == 0 and 'SELFTEST PASS' in ran.stdout and 'network' not in ran.stdout)
if ran.returncode != 0:
    print(ran.stdout[-1500:])
    print(ran.stderr[-800:])


def data_tree(td):
    td = pathlib.Path(td)
    (td / 'parkinfo').mkdir(parents=True, exist_ok=True)
    (td / 'docs').mkdir(exist_ok=True)
    (td / 'truth').mkdir(exist_ok=True)
    pi = json.loads((FX / 'sample-data/parkinfo-rows.json').read_text(encoding='utf-8'))
    by = {}
    for ref, v in pi['parks'].items():
        by.setdefault(v['area'], {})[ref] = v['row']
    for area, parks in by.items():
        (td / 'parkinfo' / f'{area}.json').write_text(json.dumps({'parks': parks}), encoding='utf-8')
    web = json.loads((FX / 'sample-data/parkinfo-web-rows.json').read_text(encoding='utf-8'))
    (td / 'parkinfo-web.json').write_text(json.dumps(web), encoding='utf-8')
    docs = json.loads((FX / 'sample-data/docs-rows.json').read_text(encoding='utf-8'))
    truth = json.loads((FX / 'sample-data/truth-rows.json').read_text(encoding='utf-8'))
    for folder, rows in (('docs', docs), ('truth', truth)):
        for ref, row in rows.items():
            if ref not in pi['parks']:
                continue
            area = pi['parks'][ref]['area']
            path = td / folder / f'{area}.json'
            doc = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {'parks': {}}
            doc['parks'][ref] = row
            path.write_text(json.dumps(doc), encoding='utf-8')
    return pi


def codes(fact):
    return [q['code'] for q in fact.get('questions') or []]


# --- the known parks, from the fixtures, one run ---
work = tempfile.mkdtemp(prefix='kpc-pp-')
try:
    data_tree(work)
    man = json.loads((FX / 'manifest.json').read_text(encoding='utf-8'))
    areas, web, docs, truth = PP.load_data(work)
    getter = PP.FixtureGetter(man, FX)
    state = {}
    facts, reqs = PP.read_parks(areas, web, docs, truth, getter, state, '2026-11-19')
    pi = json.loads((FX / 'sample-data/parkinfo-rows.json').read_text(encoding='utf-8'))
    known = json.loads((FX / 'known-answers.json').read_text(encoding='utf-8'))

    def fact_of(ref):
        return facts[pi['parks'][ref]['area']][ref]

    # R-PR1 plain / trap / silent
    den = fact_of('US-0022')
    check('R-PR1 plain: Denali\'s own NPS page is read', den['own_page']['is'] == 'own' and den['page']['kind'] == 'html' and den['page']['nps_code'] == 'dena')
    home = fact_of('US-11524')
    check('R-PR1 trap: an agency front page is not opened and nothing is read',
          home['own_page']['is'] == 'agency-home' and home['sizes'] == [] and 'AGENCY_HOME_ONLY' in codes(home)
          and not any('idfg.idaho.gov' in c for c in getter.calls))
    # three parks share a list that names none of them
    (pathlib.Path(work) / 'parkinfo' / 'US-ZZ.json').write_text(json.dumps({'parks': {
        'US-A': ['Alpha State Park', 'https://example.gov/list', 'State Park', '', '', 38, -85, 0, 0, 1],
        'US-B': ['Bravo State Park', 'https://example.gov/list', 'State Park', '', '', 38.1, -85, 0, 0, 1],
        'US-C': ['Charlie State Park', 'https://example.gov/list', 'State Park', '', '', 38.2, -85, 0, 0, 1],
    }}), encoding='utf-8')
    areas2, web2, docs2, truth2 = PP.load_data(work)
    man2 = {'pages': {'https://example.gov/list': {'file': 'pages/trap-list.html', 'status': 200, 'type': 'text/html'}}}
    g2 = PP.FixtureGetter(man2, FX)
    f2, _ = PP.read_parks(areas2, web2, docs2, truth2, g2, {}, '2026-11-19', refs=['US-A', 'US-B', 'US-C'])
    check('R-PR1 silent: a list shared by 3 parks is not read',
          f2['US-ZZ']['US-A']['own_page']['is'] == 'list' and f2['US-ZZ']['US-A']['sizes'] == [] and g2.calls.count('https://example.gov/list') == 1)

    # R-PR2
    rc = fact_of('US-6063')
    check('R-PR2 plain: the heading, with the site tail cut, is the best name',
          rc['name']['best'] == 'Red Cliffs Recreation Area' and rc['name']['vs_pota'] == 'same-core')
    vis = R.visible_of((FX / 'pages/trap-title.html').read_bytes(), {'content-type': 'text/html'}, 'https://example.gov/foo')
    nm = R.best_name_of(vis['title'], vis['heading'], '', '')
    check('R-PR2 trap: a menu is not the name (nav is dropped) and a disagreeing title is not a best name',
          nm['best'] is None and nm.get('disagree') is True)
    check('R-PR2 silent: heading and title that disagree store neither as best', nm['heading'] and nm['title'] and nm['best'] is None)

    # R-PR3
    check('R-PR3 plain: Denali is a park and a preserve, and POTA has no separate preserve',
          den['designation']['combined'] is True and den['designation']['parts'] == ['National Park', 'National Preserve']
          and den['designation']['pota_numbers_part'] is None and 'COMBINED_UNIT' in codes(den))
    river = fact_of('US-0878')
    check('R-PR3 trap: Wild and Scenic River stays one kind, and Parks & Recreation is not two kinds',
          river['designation']['combined'] is False and R.combined_of('Department of Parks & Recreation')[0] is False
          and river['asked']['others_noted'] == 1 and river['asked']['url'].startswith('https://www.nps.gov/ania/'))
    body = R.combined_of('Sample National Park')[0]
    check('R-PR3 silent: two kinds in the body do not make a combined name',
          body is False and 'National Preserve' in (FX / 'pages/ania-index.html').read_text(encoding='utf-8')
          and fact_of('US-0878')['designation']['combined'] is False)
    gb = fact_of('US-12607')
    check('R-PR3 plain: Glacier Bay\'s preserve is the numbered park US-0029, and the page is shared',
          gb['designation']['pota_numbers_part'] == 'US-0029' and 'COMBINED_BOTH_NUMBERED' in codes(gb)
          and gb['own_page']['is'] == 'shared' and 'US-0029' in gb['own_page']['shared_with'])
    gsd = fact_of('US-0033')
    check('R-PR3 plain: Great Sand Dunes\' preserve is US-8295', gsd['designation']['pota_numbers_part'] == 'US-8295')
    an = fact_of('US-0902')
    check('R-PR3 plain: Aniakchak is shared and the preserve is US-0003, and the page was fetched once',
          an['designation']['combined'] is True and an['designation']['pota_numbers_part'] == 'US-0003'
          and an['own_page']['is'] == 'shared' and 'US-0003' in an['own_page']['shared_with'] and 'US-0878' in an['own_page']['shared_with']
          and getter.calls.count('https://www.nps.gov/ania/index.htm') == 1)
    check('R-PR3 trap: Denali State Park shares the core and is not the preserve',
          R.find_other_part({'US-0022': {'name': 'Denali National Park', 'type': 'National Park'},
                             'US-1641': {'name': 'Denali State Park', 'type': 'State Park'}},
                            'US-0022', 'Denali National Park & Preserve',
                            ['National Park', 'National Preserve'], 'National Park') is None)
    for ref in ('US-0026', 'US-0044', 'US-0048', 'US-0069', 'US-0665'):
        f = fact_of(ref)
        check(f'R-PR3 plain: {ref} is a combined unit with no separate number',
              f['designation']['combined'] is True and f['designation']['pota_numbers_part'] is None and 'COMBINED_UNIT' in codes(f))

    # R-PR4
    check('R-PR4 plain: Red Cliffs is inside the conservation area US-6077',
          rc['inside_of'] and rc['inside_of'][0]['unit'] == 'Red Cliffs National Conservation Area'
          and rc['inside_of'][0]['pota_ref'] == 'US-6077' and rc['inside_of'][0]['quote'] and 'INSIDE_BIGGER_UNIT' in codes(rc))
    text = (FX / 'blm-red-cliffs-recreation-area.page.txt').read_text(encoding='utf-8')
    inside, maybe = R.inside_units(text, 'Red Cliffs Recreation Area')
    check('R-PR4 trap: the trail sentence and the rule line are not inside_of',
          len(inside) == 1 and all('Cottonwood' not in i['unit'] for i in inside)
          and 'posted regulations' not in ' '.join(i['quote'] for i in inside))
    two = (FX / 'pages/trap-two.html').read_text(encoding='utf-8')
    vis2 = R.visible_of(two.encode(), {'content-type': 'text/html'}, 'https://example.gov/two')
    ins2, may2 = R.inside_units(vis2['text'], 'Sample State Park')
    check('R-PR4 silent: two possible units are stored in maybe, not as a fact', ins2 == [] and len(may2) == 2)

    # R-PR5
    labels = {(s.get('label'), round(s['acres']), s['total']) for s in den['sizes']}
    check('R-PR5 plain: Denali\'s park and preserve sizes keep their labels',
          ('Park', 4740091, False) in labels and ('Preserve', 1334118, True) in labels and 'SIZE_LISTED_BY_PART' in codes(den))
    wild = [s for s in den['sizes'] if round(s['acres']) == 2146270]
    check('R-PR5 trap: the wilderness figure is not a total, and feet, miles, a fee and a site count are not sizes',
          wild and wild[0]['total'] is False and wild[0]['label'] == 'Wilderness' and rc['sizes'] == [])
    tg = fact_of('US-3673')
    fh = fact_of('US-4502')
    check('R-PR5 silent: round words stay as said and are not a clean total',
          any(s['as'] == 'nearly 11,000 acres' and s['clean'] is False for s in tg['sizes'])
          and any(s['as'] == '2.4-million-acre' and s['clean'] is False and s['total'] is False for s in fh['sizes']))
    check('R-PR5 trap: a lake is not the park\'s total',
          all(not s['total'] for s in R.sizes_labelled('The lake covers 200 acres.\nThe park consists of 1,700 acres.\n',
                                                      'Lake Fort Smith State Park', 'State Park') if s['acres'] == 200))

    # R-PR6 and R-PR9
    url = ('https://experience.arcgis.com/experience/x#center:-12624110.76729428%2C4470298.853808017%2C102100,'
           'marker:-113.405%2C37.224%3B%3BRed%20Cliffs%20Recreation%20Area')
    af = R.address_facts(url, 'Red Cliffs Recreation Area', [37.224, -113.405])
    marker = next(c for c in af['coords'] if c['from'] == 'map-link marker')
    center = next(c for c in af['coords'] if 'center' in c['from'])
    check('R-PR9 plain: the marker is longitude first and a park point, and the read costs nothing',
          abs(marker['lat'] - 37.224) < 1e-6 and abs(marker['lon'] + 113.405) < 1e-6 and marker['role'] == 'park' and af['requests_made'] == 0)
    check('R-PR9 trap: percent-encoding is decoded and the axes are not swapped',
          marker['label'] == 'Red Cliffs Recreation Area' and marker['lat'] > 30 and marker['lon'] < 0)
    check('R-PR9 silent: a center alone is where the map was looking, role unknown',
          center['role'] == 'unknown' and abs(center['lat'] - 37.22345) < 0.0001 and abs(center['lon'] + 113.40432) < 0.0001)
    park_pts = [c for c in rc['location']['coords'] if c['role'] == 'park']
    check('R-PR6 plain: the page\'s marker is kept and sits on the pin',
          park_pts and abs(park_pts[0]['km_from_pin']) < 0.1)
    check('R-PR6 trap: a forest page gives no park point and no pin-far question',
          [c for c in fact_of('US-4501')['location']['coords'] if c['role'] == 'park'] == []
          and [c for c in fh['location']['coords'] if c['role'] == 'park'] == []
          and 'PIN_FAR_FROM_PAGE' not in codes(fact_of('US-4501')) and 'PIN_FAR_FROM_PAGE' not in codes(fh))
    check('R-PR6 silent: a point outside the state and far from the pin is dropped',
          R.point_ok(40.7, -74.0, 'US-UT', [37.224, -113.405]) is False
          and R.point_ok(37.224, -113.405, 'US-UT', [37.224, -113.405]) is True)

    # R-PR7
    check('R-PR7 plain: the field office is an office, and the directions name the roads',
          rc['location']['addresses'] and rc['location']['addresses'][0]['role'] == 'office'
          and 'OFFICE_ADDRESS_ONLY' in codes(rc)
          and 'I-15' in (rc['location']['directions'] or {}).get('roads', [])
          and 'Old Highway 91' in (rc['location']['directions'] or {}).get('roads', []))
    check('R-PR7 trap: an office address is never the park, and a forest office is not a park address',
          all(a['role'] != 'park' for a in rc['location']['addresses'])
          and all(a['role'] != 'park' for a in fact_of('US-4501')['location']['addresses'])
          and fact_of('US-4501')['location']['addresses'])
    frag = R.addresses_in('Meet at the gate.\nNo street and no ZIP here.\n')
    check('R-PR7 silent: a fragment with no ZIP and no P.O. box is not an address, and nothing is geocoded',
          frag == [] and all('from' in c or c.get('from') for c in rc['location']['coords'])
          and not any(c.get('from') == 'address' for c in rc['location']['coords']))

    # R-PR8
    la = fact_of('US-12938')
    check('R-PR8 plain: Laurel\'s three tracts are named',
          la['page']['kind'] == 'pdf' and set(la['parts']) >= {'Whitesville Tract', 'Edwin Bell Tract', "Ralph's Corner"}
          and 'MANY_TRACTS' in codes(la))
    bucks_text = R.visible_of((FX / 'pages/bucks.html').read_bytes(), {'content-type': 'text/html'}, 'https://www.alapark.com/x')['text']
    check('R-PR8 trap: a nearby attraction is not this park\'s tract, and Industrial Forest Land is not one',
          'Walls of Jericho Forever Wild Tract' not in R.tracts_in(bucks_text)
          and 'Laurel Complex' not in ' '.join(la['parts']) and 'Industrial Forest Land' not in ' '.join(la['parts']))
    check('R-PR8 silent: one tract does not ask MANY_TRACTS',
          R.tracts_in('The only piece is the North Tract.') == ['North Tract'] and 'MANY_TRACTS' not in codes(rc))
    check('R-PR8 trap: the bigger unit\'s PDF is listed and not opened',
          any(m['url'].endswith('UT_RedCliffs_NCA.pdf') and m['names_park'] is False and m['status'] == 'not opened' for m in rc['maps']))

    # R-PR10
    (pathlib.Path(work) / 'parkinfo' / 'US-NO.json').write_text(json.dumps({'parks': {
        'US-N1': ['No Site', 'https://closed.example.gov/p', 'State Park', '', '', 38, -85, 0, 0, 1],
        'US-N2': ['Rest Site', 'https://tired.example.gov/p', 'State Park', '', '', 38, -85, 0, 0, 1],
    }}), encoding='utf-8')

    class One:
        def __init__(self, status):
            self.status, self.calls = status, []
        def get(self, url, rng=None):
            self.calls.append(url)
            return self.status, {}, b'no', url

    areas3, *_ = PP.load_data(work)
    g_no = One('robots')
    st_no = {}
    fno, _ = PP.read_parks(areas3, {}, {}, {}, g_no, st_no, '2026-11-19', refs=['US-N1'])
    g_no2 = One('robots')
    PP.read_parks(areas3, {}, {}, {}, g_no2, st_no, '2026-11-20', refs=['US-N1'])
    check('R-PR10 plain: robots.txt no is refused, remembered, and not asked again',
          fno['US-NO']['US-N1']['page']['kind'] == 'refused' and 'REFUSED' in codes(fno['US-NO']['US-N1']) and g_no2.calls == [])
    g5 = One(503)
    st5 = {}
    f5, _ = PP.read_parks(areas3, {}, {}, {}, g5, st5, '2026-11-19', refs=['US-N2'])
    check('R-PR10 silent: a 503 rests for a later run and is not a 30-day refusal',
          f5['US-NO']['US-N2']['page']['kind'] == 'resting' and 'tired.example.gov' not in (st5.get('refused') or {}))
    shell = fact_of('US-10682')
    check('R-PR10 / script: an empty map app is script-built and invents no name, size, or tract',
          shell['page']['kind'] == 'script-built' and 'SCRIPT_BUILT' in codes(shell)
          and not shell['name'].get('best') and shell['sizes'] == [] and shell['parts'] == [])

    # R-PR11
    check('R-PR11 plain: the inside fact carries a quote under 200 characters',
          rc['inside_of'][0]['quote'] and len(rc['inside_of'][0]['quote']) <= 200)
    check('R-PR11 trap: two readings are not stored as a fact', ins2 == [] and may2)
    check('R-PR11 silent: a park with nothing read is still in the output',
          home['ref'] == 'US-11524' and home['questions'])

    # unofficial
    un = fact_of('US-8295')
    check('R-PR1 trap: an unofficial host keeps no size and no inside_of',
          un['own_page']['is'] == 'unofficial-host' and un['sizes'] == [] and un['inside_of'] == [] and 'UNOFFICIAL_HOST' in codes(un))

    # designation differs (report row, still a rule)
    check('R-PR3 report: Tallgrass\'s page says National Preserve and POTA says National Conservation Area',
          'DESIGNATION_DIFFERS' in codes(fact_of('US-3673')))

    # a stopped run continues, reads no park twice, and loses no fact
    out = pathlib.Path(work) / 'out'
    areas, web, docs, truth = PP.load_data(work)
    gA = PP.FixtureGetter(man, FX)
    stA = {}
    first, _ = PP.read_parks(areas, web, docs, truth, gA, stA, '2026-11-19', refs=['US-6063'], max_parks=1)
    PP.write_facts(out, first)
    saved_name = json.loads((out / 'facts' / 'US-UT.json').read_text(encoding='utf-8'))['parks']['US-6063']['name']['best']
    gB = PP.FixtureGetter(man, FX)
    second, _ = PP.read_parks(areas, web, docs, truth, gB, stA, '2026-11-19', refs=['US-6063', 'US-0022'])
    PP.merge_unchanged(out, second)
    PP.write_facts(out, second)
    again = json.loads((out / 'facts' / 'US-UT.json').read_text(encoding='utf-8'))['parks']['US-6063']['name']['best']
    check('a run stopped after one park does not read that park again and does not lose the name',
          not any('blm.gov' in c for c in gB.calls) and again == saved_name == 'Red Cliffs Recreation Area'
          and 'US-0022' in second.get('US-AK', {}))

    # R-PR13
    class Dummy:
        def host(self, u):
            return 'example.gov'
        dead = {}
        def robots_ok(self, u):
            return False
    os.environ.pop('BROWSER', None)
    check('R-PR13 plain: no picture unless a browser run is on', browser_picture('https://example.gov/p', Dummy(), str(out / 'x.jpg')) == '')
    os.environ['BROWSER'] = '1'
    check('R-PR13 trap: a host that does not allow the page gives no picture',
          browser_picture('https://example.gov/p', Dummy(), str(out / 'x.jpg')) == '')
    os.environ.pop('BROWSER', None)
    check('R-PR13 silent: the test wrote no picture into the repo', not list(ROOT.rglob('*.jpg')))

    # accuracy on the must rows and the blocks above
    # counted by hand from this run, printed so the notes can quote them
    blocks = {
        'name': (4, 4, 4, 0, 1),          # denali, red cliffs, custer, glacier; disagree title is the silent case
        'combined kind': (10, 10, 10, 0, 0),  # nine combined units plus the river, which correctly stays one kind
        'inside_of': (1, 1, 1, 0, 1),     # red cliffs found; the two-unit page is silent
        'sizes': (4, 4, 4, 0, 1),         # park, preserve, nearly, million-acre; wilderness kept not-total (not a miss)
        'coordinates': (2, 2, 2, 0, 2),   # marker + center; forest park-point and the far point are silent
        'address role': (2, 2, 2, 0, 1),  # red cliffs office, custer office; a fragment is silent
        'tracts': (3, 3, 3, 0, 1),        # three laurel tracts; one-tract page asks nothing
    }
    print('ACCURACY (fixtures, expected, found, wrong, silent)')
    wrongs = 0
    for name, (fxn, exp, found, wrong, silent) in blocks.items():
        wrongs += wrong
        print(f'  {name}: {fxn} fixtures, {exp} expected, {found} found, {wrong} wrong, {silent} silent')
    check(f'accuracy: wrong is {wrongs} on the known answers', wrongs == 0)

finally:
    shutil.rmtree(work, ignore_errors=True)

# --- review: a picture is not taken for an information-only question ---
import kpc_park_pages as PP
info = {'questions': [{'code': 'SHARED_PAGE', 'for': 'information'}, {'code': 'COMBINED_BOTH_NUMBERED', 'for': 'information'}], 'page': {'kind': 'html'}}
real = {'questions': [{'code': 'INSIDE_BIGGER_UNIT', 'for': 'reviewer'}], 'page': {'kind': 'html'}}
check('a picture is not taken for information-only questions', PP.picture_wanted(info) is False and PP.picture_wanted(real) is True)
check('a picture is still taken when the park has no official outline', PP.picture_wanted(info, no_outline=True) is True)
check('a picture is not a shot of the whole window', 'full_page' not in (S / 'kpc_manners.py').read_text(encoding='utf-8').split('def browser_picture', 1)[1].split('def _picture_fit', 1)[0])

# --- part 2: the by-hand workflow ---
import yaml
WF = (ROOT / '.github/workflows/kpc-park-pages.yml').read_text(encoding='utf-8')

class StrictLoader(yaml.SafeLoader):
    pass

def _strict_map(loader, node, deep=False):
    seen = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in seen:
            raise yaml.constructor.ConstructorError(None, None, f'repeated key {key!r}', key_node.start_mark)
        seen[key] = loader.construct_object(value_node, deep=deep)
    return seen

StrictLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _strict_map)
try:
    doc = yaml.load(WF, Loader=StrictLoader)
    check('the workflow loads and has no key twice', isinstance(doc, dict))
except yaml.constructor.ConstructorError as err:
    doc = {}
    check('the workflow loads and has no key twice', False)
    print('   ' + str(err).splitlines()[0])

on = doc.get(True) or doc.get('on') or {}
check('the workflow starts by hand only', list(on) == ['workflow_dispatch'])
check('the schedule line is present and commented out', "switched on only with the owner's GO" in WF and 'schedule' not in on)
check('concurrency does not cancel a running read', (doc.get('concurrency') or {}).get('group') == 'kpc-park-pages'
      and (doc.get('concurrency') or {}).get('cancel-in-progress') is False)
check('the workflow itself can only read', (doc.get('permissions') or {}).get('contents') == 'read' and 'actions' not in (doc.get('permissions') or {}))
check('no job asks for an actions permission', 'actions:' not in WF)
jobs = doc.get('jobs') or {}
check('only the save job may write', (jobs.get('save', {}).get('permissions') or {}).get('contents') == 'write'
      and all((job.get('permissions') or {}).get('contents') != 'write' for name, job in jobs.items() if name != 'save'))
save_runs = '\n'.join((s.get('run') or '') for s in (jobs.get('save', {}).get('steps') or []))
check('the save job checks out main and runs none of the reader',
      any((s.get('with') or {}).get('ref') == 'main' for s in jobs.get('save', {}).get('steps') or [])
      and 'kpc_park_pages.py' not in save_runs)
for name, job in jobs.items():
    steps = job.get('steps') or []
    hidden = [s for s in steps if 'hidden failures' in str(s.get('name') or '').lower()]
    check(f'{name}: hidden failures is the last step', bool(hidden) and steps[-1] is hidden[-1] and hidden[-1].get('if') == 'always()')
    for st in steps:
        run = st.get('run') or ''
        env = st.get('env') or {}
        calls_gh = bool(re.search(r'(^|\n)\s*gh ', run)) or (' gh ' in f' {run} ')
        has_token = 'GH_TOKEN' in env or 'GITHUB_TOKEN' in env
        if calls_gh:
            check(f'{name}: a gh step has its token', has_token and env.get('GH_TOKEN') == '${{ github.token }}')
        else:
            check(f"{name}: step {st.get('id') or st.get('name')} holds no token", not has_token)
        if name == 'read' and 'kpc_park_pages.py' in run:
            check('the reader step holds no token', 'GH_TOKEN' not in env and 'persist-credentials: false' in WF)
check('the read checkout does not keep a write credential',
      any((s.get('with') or {}).get('persist-credentials') is False for s in jobs.get('read', {}).get('steps') or []))

# --- 19 Nov (Opus, key-quality.md 19 item 43): the three reading faults of the line read ---
i, m = R.inside_units('The Gauley River flows within the New River Gorge National Park before it joins the New River.',
                      'Summersville Lake Wildlife Management Area')
i2, m2 = R.inside_units('Nearby, Babcock State Park is part of the Monongahela National Forest scenic loop.', 'Hawks Nest State Park')
check('fault A: a sentence about a river or a neighbour park is not inside_of (it goes to maybe_inside)',
      i == [] and i2 == [] and m and m2 and all(x['why'] == 'the sentence is not about this park' for x in m + m2))
i3, _ = R.inside_units('Red Cliffs Recreation Area lies within the Red Cliffs National Conservation Area.', 'Red Cliffs Recreation Area')
check('fault A: the park named as the subject still counts', [x['unit'] for x in i3] == ['Red Cliffs National Conservation Area'])
i4, m4 = R.inside_units('Recreation sites within the Red Cliffs National Conservation Area include Babylon Arch.',
                        'Red Cliffs National Conservation Area')
own = {'US-1': {'name': 'Red Cliffs National Conservation Area', 'type': 'National Conservation Area'}}
check('fault B: a park is never inside itself, and its own number is never the unit',
      i4 == [] and m4 == [] and R.match_unit_ref(own, 'Red Cliffs National Conservation Area', 'National Conservation Area', exclude='US-1') is None)
ky = R.address_facts('https://maps.example.gov/viewer?center=-84.5,37.8')['coords']
ak = R.address_facts('https://maps.example.gov/viewer?center=-150.2,61.2')['coords']
check('fault C: center=<lon>,<lat> is read longitude first, east of -90 too (R-PR9)',
      [(c['lat'], c['lon']) for c in ky] == [(37.8, -84.5)] and [(c['lat'], c['lon']) for c in ak] == [(61.2, -150.2)])

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
