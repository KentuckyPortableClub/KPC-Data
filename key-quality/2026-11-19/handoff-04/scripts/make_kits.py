"""Hand-off 04 kits (Opus, 19 Nov 2026; key-quality.md section 19 items 27-29). Two blind passes of the same rows: different order,
different item numbers, different planted answers. The key (rows -> refs, plants and their known answers) stays apart."""
import csv, json, os, random, sys, pathlib
OUT = pathlib.Path(sys.argv[1]); R = json.load(open(sys.argv[2]))
COLS = {
 'F': ['item', 'ref', 'name', 'area', 'park_type', 'pota_website', 'activations', 'official_page',
       'official_acres_whole_unit (as published)', 'owned_in_fee_acres (as published, or not given)', 'easement_acres (as published, or not given)',
       "other_agencies_land_acres (as published, or not given)", 'open_to_public_note', 'acres_source_table_or_page_and_date',
       'where_the_official_outline_lives (layer address or file)', 'record_name_and_acres_in_that_layer', 'note'],
 'A': ['item', 'ref', 'name', 'area', 'park_type', 'pota_website', 'activations', 'record_id', 'record_name', 'record_acres', 'record_source',
       'is_this_record_the_park (YES / NO / PART / CANNOT TELL)', 'why (what the official source shows)', 'official_page', 'official_acres (as published)',
       'acres_source_and_date', 'where_the_official_outline_lives (layer address or file)', 'note'],
 'B': ['item', 'unit_name', 'state_or_portion', 'table_to_look_in', 'report_edition_and_date', 'table_and_row_exactly_as_shown',
       'NFS_acres (as published)', 'gross_acres (as published)', 'link_to_the_report_file', 'note'],
 'C': ['item', 'ref', 'name', 'area', 'park_type', 'pota_website', 'activations', 'managing_agency', 'official_page',
       'does_the_agency_publish_its_own_boundary (GIS / PICTURE / NOTHING)', 'layer_address_or_file', 'record_name_and_acres_in_that_layer',
       'official_acres (as published)', 'acres_source_and_date', 'licence_line', 'note'],
 'E': ['item', 'ref', 'name', 'area', 'park_type', 'pota_website', 'activations', 'official_page', 'official_acres (as published)',
       'acres_source_and_date', 'where_the_official_outline_lives (layer address or file)', 'record_name_and_acres_in_that_layer',
       'outline_date', 'licence_line', 'note'],
}
FILES = {'F': 'jobF-official-sizes-FIRST', 'A': 'jobA-is-this-record-the-park', 'B': 'jobB-forest-service-acres', 'C': 'jobC-does-the-agency-publish-its-own-outline',
         'E': 'jobE-busiest-new-pins'}
P = R['plants']
key = {'note': 'NEVER give this file to an agent. item -> ref per pass; the planted rows and what is known about them.', 'pass1': {}, 'pass2': {}, 'plants': {}}
for pas, seed in (('pass1', 4101), ('pass2', 4207)):
    rnd = random.Random(seed); d = OUT / f'KPC-hand-off-04-{pas}'; d.mkdir(parents=True, exist_ok=True)
    for job in 'FACEB':
        rows = [dict(zip(['unit_name', 'state_or_portion', 'table_to_look_in', '_ref'], x)) if isinstance(x, list) else dict(x) for x in R[job]]
        for pl in P.get(pas, {}).get(job, []): rows.append(dict(pl['row'], _plant=pl['known']))
        # busiest first stays the rule inside each job; a light shuffle among equals so the two passes differ
        rows.sort(key=lambda r: (-(int(r.get('activations') or 0) // 25), rnd.random()))
        with open(d / f"{FILES[job]}.answers-template.csv", 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f); w.writerow(COLS[job])
            for i, r in enumerate(rows, 1):
                it = f"{job}{'1' if pas == 'pass1' else '2'}-{i:02d}"
                key[pas][it] = r.get('ref') or r.get('_ref') or r.get('unit_name')
                if r.get('_plant'): key['plants'][it] = {'ref': r.get('ref'), 'known': r['_plant']}
                w.writerow([it] + [r.get(c, '') if not c.startswith('is_this') else '' for c in COLS[job][1:]])
json.dump(key, open(OUT / 'handoff-04-answer-key.json', 'w'), indent=1, ensure_ascii=False)
print('pass1', len(key['pass1']), 'pass2', len(key['pass2']), 'plants', len(key['plants']))
