#!/usr/bin/env python3
"""22 Nov 2026 (owner 3:55 PM, plan P3-P5): the park facts file carries what the keys may weigh for matching from the park's page:
named tracts, the reader's SURE parent unit (never maybe_inside) and https map links. Invented parks. ALL PASS or SOME FAILED."""
import importlib.util, json, pathlib, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('pf', ROOT / '.github/scripts/draft/tools/kpc_park_facts/kpc_park_facts.py')
PF = importlib.util.module_from_spec(spec); spec.loader.exec_module(PF)
ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


with tempfile.TemporaryDirectory() as t:
    (pathlib.Path(t) / 'US-ZZ.json').write_text(json.dumps({'area': 'US-ZZ', 'parks': {
        'US-9001': {'page': {'kind': 'html'}, 'own_page': {'is': 'own'}, 'parts': ['North Unit', 'South Unit'],
                    'inside_of': [{'unit': 'Invented National Forest', 'kind': 'National Forest', 'pota_ref': 'US-9100', 'quote': 'q'}],
                    'maybe_inside': [{'unit': 'Unsure Forest', 'why': 'the sentence is not about this park'}],
                    'maps': [{'url': 'https://maps.example.gov/arcgis/home/item.html?id=1', 'kind': 'web-map', 'names_park': True},
                             {'url': 'http://insecure.example/map.pdf', 'kind': 'pdf'}]},
        'US-9002': {'page': {'kind': 'html'}, 'own_page': {'is': 'own'}}}}), encoding='utf-8')
    pages, _ = PF.read_pages(t)
p1, p2 = pages['US-9001'], pages['US-9002']
check('named tracts are kept', p1.get('parts') == ['North Unit', 'South Unit'])
check('the sure parent unit is kept with its POTA number', p1.get('inside_of') == [{'unit': 'Invented National Forest', 'kind': 'National Forest', 'pota_ref': 'US-9100'}])
check('a maybe-inside unit is never kept', 'Unsure Forest' not in json.dumps(p1))
check('only https map links are kept, with their kind', p1.get('maps') == [{'url': 'https://maps.example.gov/arcgis/home/item.html?id=1', 'kind': 'web-map', 'names_park': True}])
check('a page with none of these has empty lists', (p2.get('parts'), p2.get('inside_of'), p2.get('maps')) == ([], [], []))
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
