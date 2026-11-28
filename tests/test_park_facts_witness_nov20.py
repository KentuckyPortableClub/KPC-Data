#!/usr/bin/env python3
"""Park facts, 20 Nov 2026: every official size is tagged with where it came from (its witness). Offline, invented parks.
27 Nov 2026: the builder no longer reads the old key, so it writes same_record / other_layer only when a caller gives the layers.

same_record (the map layer the key already joined), other_layer, agency_document, hand_copy, unknown.
Only agency_document and hand_copy count. Prints PASS / FAIL lines and ends ALL PASS or SOME FAILED.
"""
import gzip, json, os, pathlib, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL = next(p for p in (ROOT / 'kpc_park_facts', ROOT / '.github/scripts/draft/tools/kpc_park_facts') if p.is_dir())   # 27 Nov: the work copy, else KPC-Data's
sys.path.insert(0, str(TOOL))
import kpc_park_facts as F  # noqa: E402

ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


LAYER = 'https://services9.arcgis.example/abc/arcgis/rest/services/Invented_Parks/FeatureServer/2/query?where=1%3D1&f=json'
OTHER = 'https://gis.invented.example/arcgis/rest/services/Invented_Wildlife/MapServer/0/query'
with tempfile.TemporaryDirectory() as t:
    t = pathlib.Path(t)
    (t / 'key').mkdir()
    json.dump({'sgzza': [LAYER.split('?')[0], 'NAME', 'Invented Parks (park, state GIS table)']}, open(t / 'layers.json', 'w'))
    json.dump({'parks': {'US-9101': {'n': 'Invented Lake State Park', 'src': ['sgzza']},
                         'US-9102': {'n': 'Invented Marsh', 'src': ['PAD-US']},
                         'US-9105': {'n': 'Invented Bluff', 'src': []}}}, open(t / 'key' / 'US-ZZ.json', 'w'))
    # 27 Nov 2026 (audit section 2): the builder no longer reads the old key (read_key_layers is gone). witness() still takes
    # the joined layers when a caller gives them, so the tag rules below are checked with sets made by hand.
    PADUS = 'https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0/query'
    keyl = {'US-9101': {F.norm_layer(LAYER)}, 'US-9102': {F.norm_layer(PADUS)}, 'US-9105': set()}
    check('the old key reader is gone (27 Nov)', not hasattr(F, 'read_key_layers'))
    cases = [
        ('US-9101', {'how': 'name+kind', 'source_url': LAYER}, 'same_record'),
        ('US-9101', {'how': 'name+kind', 'source_url': LAYER.replace('https://', 'http://').replace('/query?where=1%3D1&f=json', '')},
         'same_record'),
        ('US-9102', {'how': 'name+kind', 'source_url': OTHER}, 'other_layer'),
        ('US-9102', {'how': 'name+kind', 'source_url': 'https://www.invented.example/upload/Acreage-2026.xlsx'}, 'agency_document'),
        ('US-9102', {'how': 'name+kind', 'source_url': 'https://library.invented.example/reports/lands_2024.pdf'}, 'agency_document'),
        ('US-9102', {'how': 'hand copy (unknown agency, page not given)', 'source_url': ''}, 'hand_copy'),
        ('US-9102', {'how': 'name+kind', 'source_url': ''}, 'unknown'),
        ('US-9102', {'how': 'name+kind', 'source_url': 'https://geodata.invented.example/api/download/v1/items/abc/csv?layers=0'},
         'unknown'),
        ('US-9103', {'how': 'name+kind', 'source_url': OTHER}, 'unknown'),       # the key does not have this park
        ('US-9105', {'how': 'name+kind', 'source_url': OTHER}, 'unknown'),       # the key has it with no joined layer
        ('US-9102', {'how': 'name+kind', 'source_url': 'https://www.invented.example/parks/lake'}, 'unknown'),
    ]
    for ref, row, want in cases:
        got, why = F.witness(ref, row, keyl)
        check(f'{ref} {row["source_url"][:60] or row["how"]!r} -> {want}', got == want)
    check('a map layer with the key not read is unknown, never same or other',
          F.witness('US-9101', {'how': 'name+kind', 'source_url': LAYER}, None)[0] == 'unknown')
    check('only agency_document and hand_copy count', F.WITNESS_PROOF == ('agency_document', 'hand_copy'))

    # end to end: the file carries the tag, why, and whether it counts, plus the counts
    (t / 'parkinfo').mkdir(); (t / 'pages').mkdir()
    json.dump({'parks': {'US-9101': ['Invented Lake State Park', '', 'State Park', '', '', 37.0, -85.0, 1, 1, 1],
                         'US-9102': ['Invented Marsh', '', 'Wildlife Refuge', '', '', 37.1, -85.1, 1, 1, 1]}},
              open(t / 'parkinfo' / 'US-ZZ.json', 'w'))
    json.dump({'US-9101': {'acres': 100.0, 'how': 'name+kind', 'source_url': LAYER, 'read_date': '2026-11-02'},
               'US-9102': {'acres': 200.0, 'how': 'name+kind', 'source_url': 'https://www.invented.example/a.xlsx',
                           'read_date': '2026-11-02'}}, open(t / 'acres.json', 'w'))
    r = subprocess.run([sys.executable, str(TOOL / 'kpc_park_facts.py'), '--parkinfo', str(t / 'parkinfo'), '--acres', str(t / 'acres.json'),
                        '--pages', str(t / 'pages'), '--key', str(t / 'key'), '--layers', str(t / 'layers.json'),
                        '--out', str(t / 'out')], capture_output=True, text=True)
    check('the builder still runs when the workflow passes --key / --layers (27 Nov: taken and ignored)', r.returncode == 0)
    doc = json.load(open(t / 'out' / 'park-facts.json'))
    s1, s2 = doc['parks']['US-9101']['size'], doc['parks']['US-9102']['size']
    # 27 Nov 2026: was same_record; the key is not read, so a map-layer size is unknown, and still not counted
    check('the file says unknown for a map-layer size and does not count it', (s1['witness'], s1['witness_counts']) == ('unknown', False))
    check('the file says agency_document and counts it', (s2['witness'], s2['witness_counts']) == ('agency_document', True))
    check('each size says why', bool(s1['witness_why']) and bool(s2['witness_why']))
    check('the counts carry every tag seen', doc['counts'].get('size witness: unknown') == 1
          and doc['counts'].get('size witness: agency_document') == 1)
    check('the file says the old key was not read', doc['inputs']['old_key'].startswith('not read'))

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
