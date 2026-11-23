#!/usr/bin/env python3
"""Own-page finder, 23 Nov 2026 (rule sheet L; owner 7:41 AM: "Finish the bot so I can do the webpage look up"). A park whose
POTA link is missing, dead or only the agency's front page gets its OWN page from the agency's own site, SURE only with its own
name and a second witness; else unsure (listed) or not found. Then the reader reads the found page in place of the dead link.
Invented parks, offline fixtures, no request. Prints PASS / FAIL, ends ALL PASS or SOME FAILED."""
import json, pathlib, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github/scripts'))
import kpc_park_pages as P  # noqa: E402
import kpc_park_pages_find as FIND  # noqa: E402
ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


H = 'https://parks.zz.invented.gov'
LIST = H + '/parks/'
WORDS = 'Words about the place, its trails and its lake. ' * 12
PIN = (47.0, -101.0)
NEAR = 'data-lat="47.0100" data-lng="-101.0100"'      # about 1.3 km from the pin
FAR = 'data-lat="47.3000" data-lng="-101.3000"'       # about 40 km from the pin


def page(title, point=''):
    return (f'<html><head><title>{title} | Invented Parks</title></head><body><h1>{title}</h1>'
            f'<div class="map" {point}></div><p>{WORDS}</p></body></html>')


PARKS = {   # ref: (name, POTA link, type)
    'US-9601': ('Birch Bay State Park', H + '/parks/birch-bay-state-park', 'State Park'),        # sister, own page
    'US-9602': ('Aspen Ridge State Park', H + '/parks/aspen-ridge-state-park', 'State Park'),    # sister, own page
    'US-9603': ('Heron Marsh State Park', '', 'State Park'),                                    # (a) no link, list + near point = SURE
    'US-9604': ('Red Notch State Park', H + '/parks/old/red-notch.html', 'State Park'),         # (b) dead link, folder above = SURE
    'US-9605': ('Otter Lake State Park', '', 'State Park'),                                     # (c) the list links the state FOREST: refused
    'US-9606': ('Moss Creek City Park', '', 'City Park'),                                       # (f) no sisters, no site: not found
    'US-9607': ('Quail Run State Park', '', 'State Park'),                                      # (g) list + no point, agency table = SURE
    'US-9608': ('Lone Pine State Park', H, 'State Park'),                                       # (h) front page only: its link = SURE
    'US-9609': ('Fox Den State Park', '', 'State Park'),                                        # (i) the page's point is 40 km off: UNSURE
    'US-9610': ('Cedar Point State Park', '', 'State Park'),                                    # (e) the page is another park's link: UNSURE
    'US-9611': ('Cedar Point State Park', H + '/parks/cedar-point', 'State Park'),              #     ... that other park
}
FX = {
    PARKS['US-9601'][1]: page('Birch Bay State Park', NEAR),
    PARKS['US-9602'][1]: page('Aspen Ridge State Park', NEAR),
    LIST: ('<html><head><title>State Parks</title></head><body><h1>State Parks</h1><p>' + WORDS + '</p><ul>'
           + ''.join(f'<li><a href="{H}/parks/{s}">{n}</a></li>' for s, n in (
               ('birch-bay-state-park', 'Birch Bay State Park'), ('aspen-ridge-state-park', 'Aspen Ridge State Park'),
               ('heron-marsh', 'Heron Marsh State Park'), ('otter-lake-sf', 'Otter Lake State Forest'),
               ('quail-run', 'Quail Run State Park'), ('fox-den', 'Fox Den State Park'), ('cedar-point', 'Cedar Point State Park')))
           + '</ul></body></html>'),
    H + '/parks/heron-marsh': page('Heron Marsh State Park', NEAR),
    H + '/parks/otter-lake-sf': page('Otter Lake State Forest', NEAR),
    H + '/parks/quail-run': page('Quail Run State Park'),
    H + '/parks/fox-den': page('Fox Den State Park', FAR),
    H + '/parks/cedar-point': page('Cedar Point State Park', NEAR),
    H + '/parks/old/': ('<html><head><title>Older park pages</title></head><body><h1>Park pages</h1><p>' + WORDS + '</p>'
                        f'<a href="{H}/parks/red-notch-sp">Red Notch State Park</a></body></html>'),
    H + '/parks/red-notch-sp': page('Red Notch State Park', NEAR),
    H: ('<html><head><title>Invented Parks</title></head><body><h1>Welcome</h1><p>' + WORDS + '</p>'
        f'<a href="{H}/parks/lone-pine">Lone Pine State Park</a></body></html>'),
    H + '/parks/lone-pine': page('Lone Pine State Park', NEAR),
}


def setup(t):
    data = t / 'data' / 'parkinfo'; data.mkdir(parents=True)
    (data / 'US-ZZ.json').write_text(json.dumps({'parks': {r: [n, u, k, '', '', PIN[0], PIN[1], 0, 0, 1] for r, (n, u, k) in PARKS.items()}}),
                                     encoding='utf-8')
    (t / 'fx.json').write_text(json.dumps({'pages': {u: {'status': 200, 'body': b} for u, b in FX.items()}}), encoding='utf-8')
    (t / 'table.json').write_text(json.dumps({'hosts': {'zz.invented.gov': {'_parks': 4}}}), encoding='utf-8')


def run(t, *cmd):
    return subprocess.run([sys.executable, '-B', str(ROOT / '.github/scripts/kpc_park_pages.py'), *cmd, '--data', str(t / 'data'),
                           '--out', str(t / 'out'), '--state', str(t / 'out' / 'state.json'), '--fixtures', str(t / 'fx.json'),
                           '--today', '2026-11-23', '--areas', 'US-ZZ', '--quiet'], capture_output=True, text=True)


with tempfile.TemporaryDirectory() as d:
    t = pathlib.Path(d)
    setup(t)
    r = run(t, 'read')
    check('the reader runs first', r.returncode == 0)
    facts = json.loads((t / 'out/facts/US-ZZ.json').read_text())['parks']
    check('before: Heron Marsh has no link, Red Notch a dead one, Lone Pine only the front page',
          FIND.why_needed(facts['US-9603']) == 'no link' and FIND.why_needed(facts['US-9604']) == 'dead link'
          and FIND.why_needed(facts['US-9608']) == 'agency home only')
    check('a park with its own page is not on the list', FIND.why_needed(facts['US-9601']) == '')
    r = run(t, 'find-links', '--agency-table', str(t / 'table.json'))
    check('find-links runs', r.returncode == 0 and not r.stderr.strip())
    if r.returncode or r.stderr.strip():
        print(r.stdout[-1500:], r.stderr[-2500:])
    facts = json.loads((t / 'out/facts/US-ZZ.json').read_text())['parks']
    rows = {x['ref']: x for x in json.loads((t / 'out/found-links.json').read_text())['rows']}
    lv = lambda ref: (rows.get(ref) or {}).get('level')
    check('(a) no link: the sister parks\' list names it, a point within 5 km = SURE', lv('US-9603') == 'sure' and rows['US-9603']['how'] == 'sister')
    check('(a) the found page is read as the park\'s page (name, point, found block)',
          facts['US-9603']['page']['kind'] == 'html' and facts['US-9603']['found']['url'] == H + '/parks/heron-marsh'
          and facts['US-9603']['name']['vs_pota'] in ('same', 'same-core') and facts['US-9603']['location']['coords'])
    check('(b) dead link: the folder above lists it = SURE', lv('US-9604') == 'sure' and rows['US-9604']['how'] == 'up'
          and rows['US-9604']['url'] == H + '/parks/red-notch-sp')
    check('(b) the dead address is remembered', facts['US-9604']['asked'].get('was') == PARKS['US-9604'][1])
    check('(c) a state forest page for a state park is never taken', lv('US-9605') == 'no')
    check('(f) a city park with no sisters and no site: not found, counted', lv('US-9606') == 'no' and rows['US-9606']['url'] == '')
    check('(g) no point, but the sister list on a known agency site = SURE', lv('US-9607') == 'sure' and 'sister parks use' in rows['US-9607']['reason'])
    check('(h) front page only: its one link naming the park = SURE', lv('US-9608') == 'sure' and rows['US-9608']['how'] == 'home')
    check('(i) the page\'s point 40 km off = UNSURE, even on the sister list of a known site', lv('US-9609') == 'unsure'
          and 'km from the pin' in rows['US-9609']['reason'] and facts['US-9609']['page']['kind'] == 'none')
    check('(e) the page is another park\'s own link = UNSURE for the one looking', lv('US-9610') == 'unsure')
    check('an unsure park keeps its old facts, with the found block', facts['US-9610']['found']['level'] == 'unsure'
          and facts['US-9610']['page']['kind'] == 'none')
    summ = (t / 'out/found-links-summary.txt').read_text()
    check('the summary counts sure / unsure / not found', 'sure (taken' in summ and 'US-ZZ:' in summ)
    st = json.loads((t / 'out/state.json').read_text())
    check('state remembers what was found', st['found']['US-9603']['level'] == 'sure' and st['found']['US-9606']['level'] == 'no')
    # the reader's next run: the found page is the park's page; the dead link is not asked again
    r = run(t, 'read')
    facts = json.loads((t / 'out/facts/US-ZZ.json').read_text())['parks']
    check('the next reader run keeps the found page as the park\'s page', facts['US-9604']['page']['kind'] == 'html'
          and facts['US-9604']['found']['level'] == 'sure')
    # the 2e step: the kept pages read again with no site asked; the found page's note must survive it
    keptdir = t / 'pages-kept'; (keptdir / 'aa').mkdir(parents=True)
    import gzip as _gz
    (keptdir / 'aa' / 'rn.gz').write_bytes(_gz.compress(FX[H + '/parks/red-notch-sp'].encode()))
    (keptdir / 'manifest.json').write_text(json.dumps({'pages': {H + '/parks/red-notch-sp': {'file': 'aa/rn.gz', 'status': 200,
                                           'type': 'text/html', 'final': H + '/parks/red-notch-sp', 'date': '2026-11-23'}}}))
    r = subprocess.run([sys.executable, '-B', str(ROOT / '.github/scripts/kpc_park_pages.py'), 'read', '--reextract', '--data', str(t / 'data'),
                        '--out', str(t / 'out'), '--state', str(t / 'out' / 'state.json'), '--keep-pages', str(keptdir),
                        '--today', '2026-11-24', '--areas', 'US-ZZ', '--quiet'], capture_output=True, text=True)
    facts = json.loads((t / 'out/facts/US-ZZ.json').read_text())['parks']
    check('the kept-page re-read (2e) reads the found page and keeps its found note',
          r.returncode == 0 and facts['US-9604']['found']['level'] == 'sure' and facts['US-9604']['asked'].get('url') == H + '/parks/red-notch-sp'
          and facts['US-9604']['asked'].get('was') == PARKS['US-9604'][1] and facts['US-9604']['page']['kind'] == 'html')
    areas, web, docs, _ = P.load_data(str(t / 'data'))
    P.add_found(web, st)
    check('the reader chooses the found page over POTA\'s dead link', P.choose_link('US-9604', areas['US-ZZ']['US-9604'], web, docs)[0] == H + '/parks/red-notch-sp')
    check('a person\'s own link is never covered', P.add_found({'US-9604': {'web': 'https://x.invented.gov/p'}}, st)['US-9604']['web'] == 'https://x.invented.gov/p')
    r2 = run(t, 'find-links', '--agency-table', str(t / 'table.json'))
    rows2 = json.loads((t / 'out/found-links.json').read_text())['rows']
    check('a second run the same day looks at nobody again (30 days)', 'parks looked at' in (t / 'out/found-links-summary.txt').read_text()
          and (t / 'out/found-links-summary.txt').read_text().startswith(f'Own-page finder ({FIND.FIND_RULE}): 0 parks'))
    check('the list keeps every row', len(rows2) == len(rows))
    sys.path.insert(0, str(ROOT / '.github/scripts/draft/tools/kpc_park_facts'))
    import kpc_park_facts as PF
    pages, _areas = PF.read_pages(str(t / 'out/facts'))
    check('park facts carry the found block (sure, with the dead address it replaces)', pages['US-9604']['found']['level'] == 'sure'
          and pages['US-9604']['found']['was'] == PARKS['US-9604'][1] and pages['US-9604']['own_page'] == 'own')
    import kpc_pc_upload as UP, gzip
    facts = json.loads((t / 'out/facts/US-ZZ.json').read_text())['parks']
    pack = {'made': '2026-11-23', 'pages': {'US-ZZ': {'area': 'US-ZZ', 'parks': facts}}}
    c = UP.write_found(pack, str(t / 'to/official-links'), str(t / 'q/official-links.json.gz'))
    lst = json.loads((t / 'to/official-links/found-2026-11-23.json').read_text())['rows']
    q = json.loads(gzip.decompress((t / 'q/official-links.json.gz').read_bytes()))['rows']
    check('upload: the whole list goes to tools-out, sorted by park number', [r['ref'] for r in lst] == sorted(r['ref'] for r in lst)
          and {r['level'] for r in lst} == {'sure', 'unsure', 'no'})
    check('upload: only the unsure finds become waiting-room questions', set(q) == {r['ref'] for r in lst if r['level'] == 'unsure'}
          and c['unsure parks for a person'] == len(q))
    q['US-9609']['answer'] = 'NO'
    (t / 'q/official-links.json.gz').write_bytes(gzip.compress(json.dumps({'rows': q}).encode()))
    UP.write_found(pack, str(t / 'to/official-links'), str(t / 'q/official-links.json.gz'))
    q2 = json.loads(gzip.decompress((t / 'q/official-links.json.gz').read_bytes()))['rows']
    check("upload: a person's answer is kept", q2['US-9609'].get('answer') == 'NO')
    check('park facts carry an unsure find for a person, and the old page kind', pages['US-9609']['found']['level'] == 'unsure'
          and pages['US-9609']['kind'] == 'none')

with tempfile.TemporaryDirectory() as d:
    t = pathlib.Path(d)
    setup(t)
    run(t, 'read')
    areas, web, docs, _ = P.load_data(str(t / 'data'))
    facts = P.W.load_facts(str(t / 'out'))
    calls = []
    getter = P.FixtureGetter(json.loads((t / 'fx.json').read_text()), t)
    rows, written, reqs = FIND.find_links(areas, facts, getter, {}, '2026-11-23', quiet=True, web=web, docs=docs,
                                          on_save=lambda r, w: calls.append(len(r)), save_every=0)
    check('progress is saved while it walks (a window closed part way keeps what was found)', len(calls) >= len(rows) - 1 > 0)
    check('it asks each agency list once, however many parks use it', getter.calls.count(LIST) <= 1)
    st = {}
    busy = P.KeeperCopyGetter({}, t, None)      # every answer 'not in the copy': the sites said nothing
    rows, written, reqs = FIND.find_links(areas, facts, busy, st, '2026-11-23', quiet=True, web=web, docs=docs)
    again = {a[1] for a in FIND.worklist(facts, st, '2026-11-23')}
    check('a park whose sites were busy or not asked is looked for again next run (no 30-day rest)',
          rows and all(r['level'] == 'no' for r in rows) and {'US-9603', 'US-9604', 'US-9608'} <= again
          and all('busy' in r['reason'] for r in rows if r['ref'] in again))
    check('a park with nowhere to look rests 30 days as before', 'US-9606' not in again and st['found']['US-9606']['date'] == '2026-11-23')

# 9:20 AM (the owner's NH trial): a kept page's link on ANOTHER state's site is never offered, however well the name fits
kept = {FIND.R.name_core('Heron Marsh State Park'): {'https://fw.ky.invented.gov/heron-marsh', H + '/parks/heron-marsh'}}
got = list(FIND.candidates_for('US-9603', {'name': 'Heron Marsh State Park'}, {}, 'no link', None, kept, [], {'parks.zz.invented.gov'}))
check("a kept link only from the area's own sites (another state's page is not offered)", got == [('kept', H + '/parks/heron-marsh')])
st0 = {'found': {'US-9606': {'level': 'no', 'date': '2026-11-23', 'rule': 'L 2026-11-23'}}}
fx = {'US-ZZ': {'US-9606': {'asked': {'url': ''}, 'page': {'kind': 'none'}, 'questions': [{'code': 'NO_PAGE'}]}}}
check('a park looked for under the older rule is looked for again', [r for _a, r, _w in FIND.worklist(fx, st0, '2026-11-23')] == ['US-9606'])

# no outside site in the rule: a tourism page never counts (official list only)
check('(d) a tourism site is not official', not FIND.R.official_host('https://www.visitzz.com/heron-marsh'))
row = {'name': 'Anthony Branch State Fish and Wildlife Area', 'type': 'State Fish and Wildlife Area', 'lat': PIN[0], 'lon': PIN[1], 'qsos': 1}
pg = {'kind': 'html', 'url': H + '/fish/anthony-branch', 'final': H + '/fish/anthony-branch', 'text': WORDS, 'title': 'Anthony Branch Fishery Area',
      'heading': 'Anthony Branch Fishery Area', 'html': page('Anthony Branch Fishery Area', NEAR), 'links': []}
lvl, why, _f = FIND.judge('US-9620', 'US-ZZ', row, {'US-9620': row}, pg, {}, '2026-11-23', 'sister')
check('same words, another kind = never sure by itself (unsure)', lvl in ('unsure', 'no') and lvl != 'sure')
lvl, why, _f = FIND.judge('US-9603', 'US-ZZ', {'name': 'Heron Marsh State Park', 'type': 'State Park', 'lat': PIN[0], 'lon': PIN[1]},
                          {}, dict(pg, url='https://www.visitzz.com/heron', final='https://www.visitzz.com/heron', title='Heron Marsh State Park',
                                   heading='Heron Marsh State Park'), {}, '2026-11-23', 'kept')
check('a page on a tourism site is never taken, even with the right name', lvl == 'no' and 'official' in why)
lvl, why, _f = FIND.judge('US-9603', 'US-ZZ', {'name': 'Heron Marsh State Park', 'type': 'State Park', 'lat': PIN[0], 'lon': PIN[1]},
                          {}, dict(pg, kind='pdf'), {}, '2026-11-23', 'kept')
check('a PDF never counts as the park\'s page', lvl == 'no')
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
