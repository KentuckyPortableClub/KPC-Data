#!/usr/bin/env python3
"""Nov 8 2026 (Brandon: 'NPS offers trails'). Offline: the NPS park trail puller drops OSM lines, honours robots.txt (404 allowed,
403 refused, Disallow obeyed), never touches the DataStore, sends no key; its workflow is manual and read-only; US-5993's hand-drop
line is wired and the trail parks still all have a status."""
import csv, gzip, importlib.util, json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
FAILS = []


def check(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: FAILS.append(m)


spec = importlib.util.spec_from_file_location('n', ROOT / '.github/scripts/kpc_nps_park_trails.py'); n = importlib.util.module_from_spec(spec); spec.loader.exec_module(n)
check(not n.keep({'MAPSOURCE': 'OpenStreetMap contributors'}) and not n.keep({'MAPSOURCE': 'OSM 2019'}), 'OSM-sourced lines are dropped')
check(n.keep({'MAPSOURCE': 'GPS survey'}) and n.keep({}), 'NPS-surveyed lines are kept')
check(not n.keep({'PUBLICDISPLAY': 'No Public Map Display'}) and not n.keep({'DATAACCESS': 'Internal NPS Only'}), 'non-public lines are dropped')
check(n.robots_ok(n.LAYER, fetch=lambda u: (404, '')), 'robots 404 = allowed')
check(not n.robots_ok(n.LAYER, fetch=lambda u: (403, '')), 'robots 403 = refused')
check(not n.robots_ok(n.LAYER, fetch=lambda u: (200, 'User-agent: *\nDisallow: /arcgis/')), 'robots Disallow obeyed')
src = (ROOT / '.github/scripts/kpc_nps_park_trails.py').read_text()
check('irma.nps.gov/DataStore/DownloadFile' not in src.replace('irma.nps.gov /DataStore/DownloadFile/', '') and 'api_key' not in src.lower() and 'NPS_API_KEY' not in src,
      'no DataStore download, no API key')
fc = n.build([{'properties': {'TRLNAME': 'A', 'MAPSOURCE': 'OSM'}, 'geometry': {'type': 'LineString', 'coordinates': [[0, 0], [1, 1]]}},
              {'properties': {'TRLNAME': 'B'}, 'geometry': {'type': 'LineString', 'coordinates': [[0, 0, 5], [1, 1, 5]]}}], 'TEST')
check([f['properties']['name'] for f in fc['features']] == ['B'], 'build keeps only the non-OSM line (z values allowed)')
y = (ROOT / '.github/workflows/kpc-nps-park-trails.yml').read_text()
check('workflow_dispatch' in y and 'schedule:' not in y and 'contents: read' in y and 'secrets.' not in y, 'workflow is manual, read-only, no secrets')
wired = {w['ref']: w for w in csv.DictReader(open(ROOT / 'data/waiting/outline-sources/trail-lines-wired-nov7.csv', encoding='utf-8'))}
check('US-5993' in wired and (ROOT / wired['US-5993']['layer_url'][5:]).is_file(), 'US-5993 Central Pacific grade line is wired')
rows = json.loads(gzip.open(ROOT / 'data/waiting/outline-sources/ledger.json.gz').read())['rows']
check(rows.get('US-5993', {}).get('trail', {}).get('status') == 'trail line wired', 'ledger: US-5993 wired')
check(n.PACE >= 1.0 and "in ('', 'ALL')" in src, 'no unit codes = all NPS units, about 1 request a second')
check("required: false" in y and "default: ''" in y, 'workflow: blank units = all')
sys.exit(1 if FAILS else 0)
