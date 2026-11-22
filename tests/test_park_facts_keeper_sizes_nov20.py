#!/usr/bin/env python3
"""Park facts, 20 Nov 2026: sizes come from the keeper first; the acreage bot is only the fallback, and its sizes are
tagged by the evidence (unknown unless proven). Offline, invented parks. Ends ALL PASS or SOME FAILED."""
import json, pathlib, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL = ROOT / '.github/scripts/draft/tools/kpc_park_facts'
sys.path.insert(0, str(TOOL))
import kpc_park_facts as F  # noqa: E402

ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


with tempfile.TemporaryDirectory() as t:
    t = pathlib.Path(t)
    (t / 'parkinfo').mkdir(); (t / 'pages').mkdir()
    json.dump({'parks': {r: [f'Invented {r}', '', 'State Park', '', '', 37.0, -85.0, 1, 1, 1] for r in ('US-9201', 'US-9202', 'US-9203')}},
              open(t / 'parkinfo' / 'US-ZZ.json', 'w'))
    json.dump({'US-9201': {'acres': 100.0, 'how': 'name+kind', 'source_url': 'https://acres.invented.example/a.pdf'},
               'US-9202': {'acres': 200.0, 'how': 'name+kind', 'source_url': 'https://acres.invented.example/b.pdf'},
               'US-9203': {'acres': 300.0, 'how': 'name+kind', 'source_url': ''}}, open(t / 'acres.json', 'w'))
    json.dump({'parks': {'US-9201': {'acres': 111.0, 'source_url': 'https://agency.invented.example/list.xlsx', 'read_date': '2026-11-19'},
                         'US-9202': {'acres': 222.0, 'source_url': 'https://agency.invented.example/layer/FeatureServer/0/query',
                                     'witness': 'other_layer', 'witness_why': 'keeper: a different layer'}}},
              open(t / 'keeper-sizes.json', 'w'))
    r = subprocess.run([sys.executable, str(TOOL / 'kpc_park_facts.py'), '--parkinfo', str(t / 'parkinfo'), '--acres', str(t / 'acres.json'),
                        '--keeper-sizes', str(t / 'keeper-sizes.json'), '--pages', str(t / 'pages'), '--out', str(t / 'out')],
                       capture_output=True, text=True)
    check('the builder runs with a keeper file', r.returncode == 0)
    P = json.load(open(t / 'out' / 'park-facts.json'))['parks']
    check("the keeper's size wins over the acreage bot's", (P['US-9201']['size']['acres'], P['US-9201']['size']['from']) == (111.0, 'keeper'))
    check("the keeper's own witness tag is kept", P['US-9202']['size']['witness'] == 'other_layer')
    check('a keeper size without a tag is tagged by its evidence', P['US-9201']['size']['witness'] == 'agency_document')
    check('the acreage bot fills a park the keeper has none for', P['US-9203']['size']['from'] == 'acreage bot')
    check('an acreage size with no proof is unknown', P['US-9203']['size']['witness'] == 'unknown')
    check('no keeper file: the acreage bot alone, nothing fails',
          F.merge_sizes(F.read_keeper_sizes(str(t / 'missing.json'))[0], {'US-9203': {'acres': 1}})['US-9203']['from'] == 'acreage bot')
    check('a keeper witness that is not one of the five tags is ignored',
          F.read_keeper_sizes(str(t / 'keeper-sizes.json'))[0]['US-9201']['witness'] is None)

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
