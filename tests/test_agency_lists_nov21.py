#!/usr/bin/env python3
"""Agency park lists, 21 Nov 2026: an agency's own list maps its website id to its map id; park facts carries the tie.
Offline, invented agency and parks. Prints PASS / FAIL lines and ends ALL PASS or SOME FAILED.
"""
import argparse, csv, json, os, pathlib, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github/scripts'))
sys.path.insert(0, str(ROOT / '.github/scripts/draft/tools/kpc_park_facts'))
import kpc_agency_lists as AL  # noqa: E402
import kpc_park_facts as F  # noqa: E402

ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


r = subprocess.run([sys.executable, '-B', str(ROOT / '.github/scripts/kpc_agency_lists.py'), '--selftest'], capture_output=True, text=True)
check('the agency lists self-test passes (skips keep the earlier file, never WDPA, deadline and max_time given)',
      r.returncode == 0 and 'SELF-TEST PASSED' in r.stdout)

cfg = json.load(open(ROOT / '.github/agency-lists.json', encoding='utf-8'))
check('no agency is switched on in the shipped config', all(not a.get('enabled') for a in cfg['agencies']))
check('an agency that is on but has no licence may still be read (licence is not a gate)', 'no licence' not in ' '.join(AL.problems(
    {'enabled': True, 'agency': 'X', 'link_kind': 'k', 'source_url': 'https://x.example/l.csv', 'licence': '', 'terms_url': 'https://x.example/t',
     'robots': 'unreadable (403) = no rules',
     'format': 'csv', 'web_id': {'column': 'a'}, 'map': {'layer': 'l', 'field': 'f', 'value': 'v'}})))

with tempfile.TemporaryDirectory() as t:
    t = pathlib.Path(t)
    xw = t / 'xw'
    xw.mkdir()
    json.dump({'agency': 'Invented Parks', 'link_kind': 'ZZ page number', 'source': {'url': 'https://lists.invented.example/p.csv',
               'licence': 'public domain (invented)', 'date': '2026-11-21'},
               'rows': [{'web_id': '77', 'map_layer': 'sgzza', 'map_field': 'UNIT_NO', 'map_id': 'U-77'},
                        {'web_id': '88', 'map_layer': 'sgzza', 'map_field': 'UNIT_NO', 'map_id': 'U-88'},
                        {'web_id': '99', 'map_layer': 'wdpa', 'map_field': 'WDPA_PID', 'map_id': '555'}]}, open(xw / 'invented-parks.json', 'w'))
    json.dump({'agency': 'Invented Other', 'link_kind': 'ZZ page number', 'source': {'url': 'https://other.invented.example/l.json'},
               'rows': [{'web_id': '88', 'map_layer': 'sgzzb', 'map_field': 'ID', 'map_id': 'B-1'}]}, open(xw / 'invented-other.json', 'w'))
    (xw / 'broken.json').write_text('{not json')
    ties, files = F.read_crosswalk(str(xw))
    check('a web id maps to its map id', ties.get(('zz page number', '77'), {}).get('map_id') == 'U-77')
    check('a web id two lists map differently is left out', ('zz page number', '88') not in ties)
    check('a WDPA row is never used', ('zz page number', '99') not in ties)
    check('a file that cannot be read is listed and not used', any(f['file'] == 'broken.json' and f['rows'] == 0 for f in files))
    links = {'US-9001': {'id_kind': 'ZZ page number', 'id_value': '77', 'usable': True},
             'US-9002': {'id_kind': 'ZZ page number', 'id_value': '77', 'usable': False},
             'US-9003': {'id_kind': 'ZZ page number', 'id_value': '12', 'usable': True}}
    n = F.add_map_ties(links, ties)
    check('a usable link id gets its map tie, with its source',
          links['US-9001'].get('map_tie', {}).get('map_layer') == 'sgzza' and links['US-9001']['map_tie']['source_url'])
    check('a link id that is not usable gets no tie', 'map_tie' not in links['US-9002'] and n == 1)
    check('a web id no list holds gets no tie', 'map_tie' not in links['US-9003'])
    check('no crosswalk folder = no ties, not an error', F.read_crosswalk(str(t / 'missing')) == ({}, []))
    check('park facts has a --crosswalk option', '--crosswalk' in subprocess.run(
        [sys.executable, '-B', str(ROOT / '.github/scripts/draft/tools/kpc_park_facts/kpc_park_facts.py'), '--help'],
        capture_output=True, text=True).stdout)

wf = (ROOT / '.github/workflows/kpc-park-facts.yml').read_text()
check('the park facts run passes the keeper\'s crosswalk folder when it exists', 'data/agency-crosswalk' in wf and '$X' in wf)
r = subprocess.run([sys.executable, '-B', str(ROOT / '.github/scripts/draft/tools/kpc_park_facts/kpc_park_facts.py'), '--selftest'],
                   capture_output=True, text=True)
check('the park facts self-test still passes', r.returncode == 0)

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
