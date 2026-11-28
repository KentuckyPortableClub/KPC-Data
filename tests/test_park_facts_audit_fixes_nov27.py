#!/usr/bin/env python3
"""Park facts 11, 27 Nov 2026 (audit-facts-nov26): the fixes, one check each. Offline, invented parks.
  old key   the file is the same with and without --key / --layers; a map-layer size is unknown; the old key's outline
            flag no longer refuses a size, 'under 0.1 acres' still does; outline_acres is gone            (audit section 2)
  km2       a page size written in square kilometres is never stored as acres                               (F1)
  pins      an impossible pin and 0,0 are no pin; POTA's numbers are kept with the reason                     (F2)
  Kentucky  a park not in data/parkinfo gets its link row from POTA's link the page reader saved             (F5)
  fresh     the file says how new each input is; a shrunk input stops the run (exit 3)                       (F7)
  PC        --carry-missing keeps the previous file's facts for what this run did not read                   (F8)
  nps_code  only on an nps.gov page                                                                           (F12)
  names     the file says which name check ran                                                                (F16)
  reader    the fixed page reader's new fields are kept (names, set aside, units, not read, last try)
kpc_link_ids.py is looked for in KPC-Data (this repo, or the folder in KPC_DATA). Prints PASS / FAIL, ends ALL PASS or SOME FAILED."""
import gzip, json, os, pathlib, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL = next(p for p in (ROOT / 'kpc_park_facts', ROOT / '.github/scripts/draft/tools/kpc_park_facts') if p.is_dir())
sys.path.insert(0, str(TOOL))
import kpc_park_facts as F  # noqa: E402

LINK_TOOL = next((p for p in (ROOT / '.github/scripts/draft/tools/kpc_link_ids',
                              pathlib.Path(os.environ.get('KPC_DATA') or '/nonexistent') / '.github/scripts/draft/tools/kpc_link_ids')
                  if (p / 'kpc_link_ids.py').is_file()), None)
ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


def build(t, *extra, out='out'):
    r = subprocess.run([sys.executable, '-B', str(TOOL / 'kpc_park_facts.py'), '--parkinfo', str(t / 'parkinfo'), '--pages', str(t / 'pages'),
                        '--out', str(t / out), '--today', '2026-11-27', *extra], capture_output=True, text=True)
    doc = json.load(open(t / out / 'park-facts.json', encoding='utf-8')) if (t / out / 'park-facts.json').exists() else {}
    return r, doc


LAYER = 'https://gis.invented.example/arcgis/rest/services/Invented_Parks/FeatureServer/2/query'
with tempfile.TemporaryDirectory() as t:
    t = pathlib.Path(t)
    for d in ('parkinfo', 'pages', 'key', 'cw'):
        (t / d).mkdir()
    json.dump({'parks': {
        'US-9301': ['Invented Lake State Park', 'https://parks.invented.gov/lake', 'State Park', '', '', 37.0, -85.0, 1, 1, 1],
        'US-9302': ['Invented Refuge', 'https://www.fws.gov/refuge/invented', 'National Wildlife Refuge', '', '', 37.1, -85.1, 1, 1, 1],
        'US-9303': ['Invented Marsh', '', 'Wildlife Management Area', '', '', 37.2, -85.2, 1, 1, 1],
        'US-9304': ['Invented Dunes', '', 'State Park', '', '', 37.3, -85.3, 1, 1, 1],
        'US-9305': ['Invented Battlefield', 'https://www.nps.gov/zzbf/index.htm', 'National Battlefield', '', '', 36.5, -87.8, 1, 1, 1]}},
        open(t / 'parkinfo' / 'US-ZZ.json', 'w'))
    json.dump({'parks': {'CA-9301': ['Invented WMA', '', 'Wildlife Management Area', '', '', 100.856, -49.514, 1, 1, 1, 'MB'],
                         'CA-9302': ['Invented Reserve', '', 'Ecological Reserve', '', '', 0.0, -0.0, 1, 1, 1, 'QC']}},
              open(t / 'parkinfo' / 'CA.json', 'w'))
    json.dump({'US-9301': {'acres': 100.0, 'how': 'name+kind', 'source_url': LAYER, 'read_date': '2026-11-20', 'outline_acres': 90.0},
               'US-9302': {'acres': 8075.0, 'how': 'name+kind', 'source_url': 'https://www.fws.gov/lands.pdf', 'read_date': '2026-11-24',
                           'flags': ['over 50x the current outline (26 ac)'], 'outline_acres': 26.0},
               'US-9303': {'acres': 0.0, 'how': 'name+kind', 'source_url': 'https://agency.invented.gov/list.xlsx', 'read_date': '2026-11-22',
                           'flags': ['under 0.1 acres']}}, open(t / 'acres.json', 'w'))

    def page(name, url, sizes=(), **kw):
        return dict({'pota': {'name': name, 'type': 'State Park', 'pin': [37.0, -85.0]},
                     'page': {'read': '2026-11-25', 'kind': 'html', 'final_url': url, 'host': url.split('/')[2]},
                     'own_page': {'is': 'own'}, 'name': {'heading': name, 'vs_pota': 'same'}, 'sizes': list(sizes)}, **kw)
    pages = {
        'US-9301': page('Invented Lake State Park', 'https://parks.invented.gov/lake', [
            {'acres': 30000.0, 'as': '30,000 square kilometers', 'total': True, 'clean': True, 'unit': 'km²', 'written': '30 000 square kilometers'},
            {'acres': 1180.0, 'as': '1,180 acres', 'total': True, 'clean': True, 'unit': 'acres', 'written': '1,180 acres',
             'source_url': 'https://parks.invented.gov/lake/brochure.pdf'}]),
        'US-9302': dict(page('Invented Refuge', 'https://www.fws.gov/refuge/invented', [
            {'acres': 6000000.0, 'as': 'over 86,000 acres', 'total': False, 'clean': False},
            {'acres': 12.0, 'as': '606 + 360 acres', 'total': False, 'clean': False},
            {'acres': 1406.6, 'as': '569.2 hectares', 'total': True, 'clean': False, 'unit': 'hectares',
             'ambiguous': {'readings_acres': [1.4, 1406.6], 'why': 'x'}, 'disagrees_with': ['900 acres']}])),
        # Kentucky: not in data/parkinfo; the page reader carries POTA's name, pin and link
        'US-9401': {'area': 'US-ZZ', 'pota': {'name': 'Invented Cave National Park', 'type': 'National Park', 'pin': [37.18, -86.1],
                                              'link': 'https://www.nps.gov/zzcv/index.htm'},
                    'page': {'read': '2026-11-26', 'kind': 'html', 'final_url': 'https://www.nps.gov/zzcv/index.htm', 'host': 'www.nps.gov', 'nps_code': 'zzcv'},
                    'own_page': {'is': 'own'}, 'name': {'heading': 'Invented Cave National Park', 'vs_pota': 'same',
                                                        'names': [{'name': 'Invented Cave National Park', 'from': 'title'}, {'name': 'Invented Cave', 'from': 'page text'}],
                                                        'set_aside': [{'name': 'NPS.gov Homepage', 'from': 'heading', 'rule': 'shared', 'why': 'the site\'s own name'}],
                                                        'offered': [{'name': 'Find a Park', 'from': 'h1', 'set_aside': 'a menu line'},
                                                                    {'name': 'Invented Cave National Park', 'from': 'title', 'set_aside': ''}]}},
        'US-9402': {'area': 'US-ZZ', 'pota': {'name': 'Invented Fort National Battlefield', 'type': 'National Battlefield', 'pin': [36.5, -88.0],
                                              'link': 'https://www.nps.gov/zzbf/index.htm'},
                    'page': {'read': '2026-11-26', 'kind': 'html', 'host': 'www.nps.gov', 'final_url': 'https://www.nps.gov/zzbf/index.htm',
                             'not_read': {'reason': 'stopped', 'why': '403', 'status': 403, 'date': '2026-11-26'},
                             'last_try': {'reason': 'busy', 'status': 503, 'date': '2026-11-27', 'url': 'https://www.nps.gov/zzbf/'},
                             'seen': '2026-11-27', 'browser': True},
                    'own_page': {'is': 'own'}, 'name': {'heading': 'Invented Fort National Battlefield', 'vs_pota': 'same'}},
        'US-9403': {'area': 'US-ZZ', 'pota': {'name': 'Invented No Link Area', 'type': 'WMA', 'pin': [0, 0], 'link': ''},
                    'page': {'read': '2026-11-26', 'kind': 'none'}, 'own_page': {'is': 'none'}, 'name': {}},
        'US-9304': page('Invented Dunes', 'https://www.fws.gov/refuge/hakalau-forest'),
    }
    pages['US-9304']['page']['nps_code'] = 'hakalau-forest'
    json.dump({'area': 'US-ZZ', 'parks': pages}, open(t / 'pages' / 'US-ZZ.json', 'w'))
    json.dump({'US-ZZ': {'parks': {'US-9301': {'src': ['sgzza']}}}}, open(t / 'key' / 'US-ZZ.json', 'w'))
    json.dump({'sgzza': [LAYER, 'NAME', 'x']}, open(t / 'layers.json', 'w'))
    import csv
    with open(t / 'link-ids.csv', 'w', encoding='utf-8-sig', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['park', 'area', 'POTA type', 'website', 'agency', 'site', 'page kind', 'link shared by (parks)', 'id kind', 'id value',
                    'id is', 'id shared by (parks)', 'usable as a link id', 'web name', 'name match', 'web kind', 'kind check', 'state check'])
        w.writerow(['US-9305', 'US-ZZ', 'National Battlefield', 'nps.gov', 'US National Park Service', 'agency (known)', 'own page', '1',
                    'NPS unit code', 'ZZBF', 'known', '1', 'yes', '', '', '', '', ''])
    tools = ['--tools', str(LINK_TOOL)] if LINK_TOOL else []
    tools += ['--links', str(t / 'link-ids.csv')]
    check('kpc_link_ids.py was found for the Kentucky checks (KPC-Data, or set KPC_DATA)', LINK_TOOL is not None)

    # ---- the old key (audit section 2) ----
    r1, d1 = build(t, '--acres', str(t / 'acres.json'), *tools, out='nokey')
    r2, d2 = build(t, '--acres', str(t / 'acres.json'), '--key', str(t / 'key'), '--layers', str(t / 'layers.json'), *tools, out='withkey')
    check('the builder runs with and without --key / --layers', r1.returncode == 0 and r2.returncode == 0)
    check('built with and without the old key, every park row is the same', d1.get('parks') == d2.get('parks') and bool(d1.get('parks')))
    check('--key / --layers given: a plain note, and the file says they were ignored',
          'no longer read' in r2.stdout and 'ignored' in d2['inputs']['old_key'] and 'ignored' not in d1['inputs']['old_key'])
    P = d1['parks']
    check('a map-layer size is unknown and not proof', (P['US-9301']['size']['witness'], P['US-9301']['size']['witness_counts']) == ('unknown', False))
    check("the old key's outline flag ('over 50x the current outline') no longer refuses an agency list size",
          P['US-9302']['size']['witness_counts'] is True and P['US-9302']['size']['flags'] == ['over 50x the current outline (26 ac)'])
    check("'under 0.1 acres' is a size check, not the outline's: it still refuses", P['US-9303']['size']['witness_counts'] is False)
    check("outline_acres (the old key's outline) is not in the file", not any('outline_acres' in (p.get('size') or {}) for p in P.values()))

    # ---- km2 (F1) ----
    s = P['US-9301']['page']['sizes']
    check('30,000 square kilometers is 7,413,150 acres, the read figure kept, total and clean stand',
          (s[0]['acres'], s[0]['acres_read'], s[0]['total'], s[0]['clean']) == (7413150.0, 30000.0, True, True) and 'square kilometres' in s[0]['fixed'])
    check('a size whose acres agree with its words is left alone', 'fixed' not in s[1] and s[1]['acres'] == 1180.0)
    s = P['US-9302']['page']['sizes']
    check("'over 86,000 acres' stored as 6,000,000: the words win and it is not clean", (s[0]['acres'], s[0]['clean'], s[0]['acres_read']) == (86000.0, False, 6000000.0))
    check("two numbers ('606 + 360 acres') are left alone", s[1]['acres'] == 12.0 and 'fixed' not in s[1])
    check('hectares already converted right are left alone', s[2]['acres'] == 1406.6 and 'fixed' not in s[2])
    check('the counts say how many were converted', d1['counts'].get('page sizes in square kilometres converted to acres') == 1)

    # ---- pins (F2) ----
    check('a pin with latitude over 90 is no pin; POTA\'s numbers and why are kept, with the swapped hint',
          P['CA-9301']['pin'] is None and P['CA-9301']['pin_problem']['pota_pin'] == [100.856, -49.514]
          and 'latitude' in P['CA-9301']['pin_problem']['why'] and 'swapped' in P['CA-9301']['pin_problem']['hint'])
    check('0,0 is no pin', P['CA-9302']['pin'] is None and P['CA-9302']['pin_problem']['why'].startswith('0,0'))
    check('a good pin stays, with no problem', P['US-9301']['pin'] == [37.0, -85.0] and 'pin_problem' not in P['US-9301'])
    check("a park taken from the page reader's copy gets the same check (0,0)", P['US-9403']['pin'] is None and 'pin_problem' in P['US-9403'])
    check('pin_check alone', (F.pin_check(45.0, -90.0), F.pin_check(None, 1)[0], F.pin_check(45.0, 200.0)[0]) == (([45.0, -90.0], None), None, None))

    # ---- Kentucky ids (F5) ----
    lk = P['US-9401'].get('link') or {}
    check("a park not in data/parkinfo: its link row from POTA's link the reader saved (NPS code, usable)",
          (lk.get('id_kind'), lk.get('id_value'), lk.get('usable'), lk.get('page_kind')) == ('NPS unit code', 'ZZCV', True, 'own page')
          and lk.get('from') == F.PAGE_LINK_FROM)
    check('an id that a listed park carries too: BOTH not usable',
          (P['US-9402']['link']['usable'], P['US-9305']['link']['usable'], P['US-9402']['link']['id_shared_by']) == (False, False, 2))
    check('POTA lists no link: no row is made', 'link' not in P['US-9403'])
    check('the file names the tool that read the Kentucky links', bool(d1['sources']['link']['from_page_reader']['tool']))
    links = {}
    F.TOOL_DIRS[:] = []
    F.LOADED.pop('kpc_link_ids', None)
    real_load = F._load
    F._load = lambda name, defaults: False
    c = F.add_page_links(links, {'US-9401': {'_pota': {'link': 'https://www.nps.gov/zzcv/'}}})
    F._load = real_load
    check('kpc_link_ids not at hand: the parks are counted, nothing fails', c.get('parks whose link could not be read: kpc_link_ids.py not found') == 1 and links == {})

    # ---- nps_code (F12) ----
    check('nps_code is kept on an nps.gov page and left out on fws.gov',
          (P['US-9401']['page']['nps_code'], P['US-9304']['page']['nps_code']) == ('zzcv', None))

    # ---- the page reader's new fields ----
    pg = P['US-9401']['page']
    check('every name the page offers is kept as plain strings, the shape the key reads (name.names)', pg.get('names') == ['Invented Cave National Park', 'Invented Cave'])
    check('names set aside are kept with why, from set_aside and from offered (not the one that stands)',
          [(x['name'], x['why']) for x in pg.get('name_set_aside') or []] == [('NPS.gov Homepage', "the site's own name"), ('Find a Park', 'a menu line')])
    s = P['US-9301']['page']['sizes'][1]
    check("a size keeps its unit, its words as written, and the page it came from when not the park's page",
          (s.get('unit'), s.get('written'), s.get('source_url')) == ('acres', None, 'https://parks.invented.gov/lake/brochure.pdf')
          and P['US-9301']['page']['sizes'][0]['written'] == '30 000 square kilometers')
    s = P['US-9302']['page']['sizes'][2]
    check('a French-unclear number keeps both readings; a total that disagrees keeps the other figure',
          s.get('ambiguous') == {'readings_acres': [1.4, 1406.6]} and s.get('disagrees_with') == ['900 acres'])
    pg = P['US-9402']['page']
    check('why a page was not read, a later failed try, the day it was seen unchanged and the browser mark are kept',
          pg.get('not_read') == {'reason': 'stopped', 'status': 403, 'date': '2026-11-26'} and pg.get('last_try', {}).get('reason') == 'busy'
          and (pg.get('seen'), pg.get('browser')) == ('2026-11-27', True))
    check('empty new fields are left out (the 3 MB cap)', not any(k in P['US-9304']['page'] for k in ('names', 'name_set_aside', 'not_read', 'last_try', 'seen', 'browser')))

    # ---- freshness (F7) and the name check (F16) ----
    inp = d1['inputs']
    check('the file holds each input fingerprint and its newest read date',
          inp['acres']['sha256'] == F.sha256_of(str(t / 'acres.json')) and inp['acres']['newest_read'] == '2026-11-24'
          and inp['page_facts'][0]['file'] == 'US-ZZ.json' and inp['page_facts'][0]['newest_read'] == '2026-11-26' and inp['page_facts'][0]['parks'] == 6)
    check('newest_input is the newest date of all inputs', d1['newest_input'] == '2026-11-26')
    check('a missing input is named in the file and on the summary', inp['missing'] == ['crosswalk']
          and 'Missing: the agency lists (crosswalk).' in open(t / 'nokey' / 'summary.txt').read())
    check('the link file is fingerprinted with its own parks only (not the Kentucky rows)', inp['link_ids']['parks'] == 1)
    check('no previous file: the file says there was no shrink check', inp['previous'].startswith('not given'))
    check('the file says which name check ran', 'name_check' in d1['sources']['page'])

    # ---- the shrink guard (F7) ----
    with gzip.open(t / 'prev.json.gz', 'wt', encoding='utf-8') as f:
        json.dump(d1, f)
    parks_small = {k: v for k, v in pages.items() if k in ('US-9301', 'US-9302')}
    (t / 'pages2').mkdir()
    json.dump({'area': 'US-ZZ', 'parks': parks_small}, open(t / 'pages2' / 'US-ZZ.json', 'w'))
    r3 = subprocess.run([sys.executable, '-B', str(TOOL / 'kpc_park_facts.py'), '--parkinfo', str(t / 'parkinfo'), '--pages', str(t / 'pages2'),
                         '--acres', str(t / 'acres.json'), '--previous', str(t / 'prev.json.gz'), *tools, '--out', str(t / 'shrunk'), '--today', '2026-11-27'],
                        capture_output=True, text=True)
    check('an area that lost page facts since the previous file stops the run (exit 3) and the summary says STOP',
          r3.returncode == 3 and 'STOP' in open(t / 'shrunk' / 'summary.txt').read())
    r4 = subprocess.run([sys.executable, '-B', str(TOOL / 'kpc_park_facts.py'), '--parkinfo', str(t / 'parkinfo'), '--pages', str(t / 'pages2'),
                         '--acres', str(t / 'acres.json'), '--previous', str(t / 'prev.json.gz'), '--allow-shrink', *tools, '--out', str(t / 'shrunk2'),
                         '--today', '2026-11-27'], capture_output=True, text=True)
    check('--allow-shrink writes it anyway (exit 0)', r4.returncode == 0)
    r5, d5 = build(t, '--acres', str(t / 'acres.json'), '--previous', str(t / 'prev.json.gz'), *tools, out='same')
    check('the same inputs as the previous file: no stop, and the file names the previous one',
          r5.returncode == 0 and d5['inputs']['previous']['file'] == 'prev.json.gz' and d5['compared_with_previous']['shrank'] == [])

    # ---- the PC: carry what this run did not read (F8) ----
    r6, d6 = build(t, '--previous', str(t / 'prev.json.gz'), '--carry-missing', *tools, out='carry')
    P6 = d6.get('parks') or {}
    check('--carry-missing with no size file: the previous sizes are kept, marked carried, tagged again',
          r6.returncode == 0 and P6['US-9302']['size']['acres'] == 8075.0 and 'carried from' in P6['US-9302']['size']['carried']
          and P6['US-9302']['size']['witness_counts'] is True)
    import shutil
    shutil.rmtree(t / 'pages2')
    (t / 'pages2').mkdir()
    weak = dict(pages['US-9301'], page={'read': '2026-11-27', 'kind': 'refused', 'final_url': 'https://parks.invented.gov/lake', 'host': 'parks.invented.gov'})
    newer = dict(pages['US-9302'], page=dict(pages['US-9302']['page'], read='2026-11-27'))
    json.dump({'area': 'US-ZZ', 'parks': {'US-9301': weak, 'US-9302': newer}}, open(t / 'pages2' / 'US-ZZ.json', 'w'))
    r7 = subprocess.run([sys.executable, '-B', str(TOOL / 'kpc_park_facts.py'), '--parkinfo', str(t / 'parkinfo'), '--pages', str(t / 'pages2'),
                         '--previous', str(t / 'prev.json.gz'), '--carry-missing', *tools, '--out', str(t / 'carry2'), '--today', '2026-11-27'],
                        capture_output=True, text=True)
    P7 = json.load(open(t / 'carry2' / 'park-facts.json'))['parks']
    check('a weaker new read (refused) loses to the real read on file', P7['US-9301']['page']['kind'] == 'html' and 'carried' in P7['US-9301']['page'])
    check('an as-strong newer read wins', P7['US-9302']['page']['read'] == '2026-11-27' and 'carried' not in P7['US-9302']['page'])
    check('a park with no read here keeps the previous page, marked carried', 'carried' in P7['US-9401']['page'] and r7.returncode == 0)
    check('--carry-missing without --previous stops', subprocess.run([sys.executable, '-B', str(TOOL / 'kpc_park_facts.py'), '--parkinfo', str(t / 'parkinfo'),
                                                                     '--carry-missing', '--out', str(t / 'x')], capture_output=True, text=True).returncode != 0)
    prev = {'made': '2026-11-24', 'parks': {'US-9501': {'link': {'id_kind': 'park id', 'id_value': 'ab12', 'usable': True,
                                                                  'map_tie': {'agency': 'X', 'map_layer': 'L', 'map_id': '7'}},
                                                         'size': {'acres': 5.0, 'from': 'acreage bot', 'outline_acres': 9.0, 'witness': 'same_record'}}}}
    check('carried agency-list ties are keyed like the crosswalk (kind lower case, id upper case)', F.carry_ties(prev) == {('park id', 'AB12'): {'agency': 'X', 'map_layer': 'L', 'map_id': '7'}})
    check('carried link rows lose their old tie (made again) and say carried', 'map_tie' not in F.carry_links(prev)['US-9501'] and 'carried' in F.carry_links(prev)['US-9501'])
    check("carried sizes lose the old witness and the old key's outline", not {'witness', 'outline_acres'} & set(F.carry_sizes(prev)['US-9501']))
    check('the version is 11 or later', int(F.VERSION.split()[1]) >= 11)
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
