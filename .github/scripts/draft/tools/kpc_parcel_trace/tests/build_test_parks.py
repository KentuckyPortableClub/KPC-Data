#!/usr/bin/env python3
"""Builds tests/parks.json for the test set from the club workbooks (run on the box; paths are the box's).
US rows: round 14 workbook ('Parcel / layer URL', 'Owner on the parcel', 'Official agency', 'Parcel IDs').
Canada rows: round 13 workbook, sheet '5 Canada parks', Status PARCEL ('Official agency' = the managing agency).
  Club decision, Oct 31: Canadian rows use the federal Directory of Federal Real Property (owner_source "dfrp");
  the round-13 GeoYukon surveyed-parcels layer has no owner field. The custodian counts only when it is the
  managing agency.
Also writes parks_dfrp_demo.json: one federal site (CA-4937 Dredge No. 4 NHS, managed by Parks Canada) to show the
DFRP path drawing; it is not part of the 11-park test set.
Pins: POTA's all-parks export (all_parks_ext.csv), never moved."""
import csv, json, re, sys
import openpyxl

R14 = '/workspace/kpc/r14/KPC_Round14_parcels_maps_done.xlsx'
R13 = '/workspace/kpc/r13/KPC_Round13_boundaries_done.xlsx'
POTA = '/workspace/all_parks_ext.csv'
US = ['US-10172', 'US-9739', 'US-12753', 'US-3118', 'US-8388', 'US-10389']
CA = ['CA-5737', 'CA-0845', 'CA-4610', 'CA-5738', 'CA-4613']


def rows(path, sheet):
    r = list(openpyxl.load_workbook(path, read_only=True)[sheet].iter_rows(values_only=True))
    return [dict(zip(r[0], x)) for x in r[1:]]


def agency_name(s):
    return re.sub(r'\s*\(.*?\)\s*', ' ', s or '').strip()


def known_acres(ids):
    """Acres the round-14 researcher listed for the park's parcels ('132.9 ac', or VT DESCPROP '284A ...')."""
    a = [float(x) for x in re.findall(r'(\d+(?:\.\d+)?)\s*ac\b', ids or '')]
    return round(sum(a), 2) if a else None


# Owner field when kpc_parcels' field picker cannot see it. 1319Parcels (Frankfort / Franklin County PVA, 2019)
# keeps the owner's mailing block in Name / Address1 / City / State / Zip; round 14 read COMMONWEALTH OF KENTUCKY there.
OWNER_FIELD = {'US-10172': 'Name'}
# Known acreage when round 14 put it in the notes rather than in 'Parcel IDs' (the parcel acres it listed).
KNOWN_FROM_NOTES = {
    'US-8388': (1.32, "round 14 notes: MAP_PAR_ID 04-0-0001 0.74 ac + 04-0-0002 0.58 ac"),
    'US-3118': (894.0, "round 14 notes: DESCPROP '284A HALF MOON PARK' + '610A HALF MOON PARK'"),
    'US-10389': (829.32, 'round 14 notes: parno 459219616366000, 829.32 GIS acres'),
}

pins = {r['reference']: r for r in csv.DictReader(open(POTA))}
out = []
r14 = {d['Park number']: d for sh in ('1 Kentucky', '4 US parks') for d in rows(R14, sh)}
for ref in US:
    d = r14[ref]
    assert d['Status'] == 'PARCEL', ref
    p = pins[ref]
    names = [n for n in (d['Owner on the parcel'], agency_name(d['Official agency'])) if n]
    out.append({'ref': ref, 'name': p['name'], 'state_or_prov': p['locationDesc'], 'lat': float(p['latitude']),
                'lon': float(p['longitude']), 'agency_owner_names': names, 'parcel_layer_url': d['Parcel / layer URL'],
                'known_acres': known_acres(d['Parcel IDs']) or KNOWN_FROM_NOTES.get(ref, (None,))[0],
                'known_acres_source': ('round 14 Parcel IDs column' if known_acres(d['Parcel IDs'])
                                       else KNOWN_FROM_NOTES.get(ref, (None, None))[1]),
                'club_source': f'round 14 ({R14.split("/")[-1]}), Status PARCEL; parcel IDs listed: {d["Parcel IDs"]}'})
r13 = {d['Park number']: d for d in rows(R13, '5 Canada parks')}
for ref in CA:
    d = r13[ref]
    assert d['Status'] == 'PARCEL', ref
    p = pins[ref]
    out.append({'ref': ref, 'name': p['name'], 'state_or_prov': p['locationDesc'], 'lat': float(p['latitude']),
                'lon': float(p['longitude']), 'agency_owner_names': [agency_name(d['Official agency'])],
                'owner_source': 'dfrp', 'known_acres': None,
                'club_source': 'round 13 (' + R13.split('/')[-1] + "), Status PARCEL; agency name for it: "
                               + str(d["Agency's name for it"]) + '; round-13 layer (no owner field): ' + str(d['GIS layer URL'])})
for p in out:
    if p['ref'] in OWNER_FIELD:
        p['owner_field'] = OWNER_FIELD[p['ref']]
json.dump(out, open(sys.argv[1] if len(sys.argv) > 1 else 'parks.json', 'w'), indent=1, ensure_ascii=False)
print(len(out), 'parks')
p = pins['CA-4937']
demo = [{'ref': 'CA-4937', 'name': p['name'], 'state_or_prov': p['locationDesc'], 'lat': float(p['latitude']),
         'lon': float(p['longitude']), 'agency_owner_names': ['Parks Canada Agency'], 'owner_source': 'dfrp',
         'known_acres': None, 'club_source': 'DFRP demonstration only (national historic site managed by Parks Canada)'}]
json.dump(demo, open('parks_dfrp_demo.json', 'w'), indent=1, ensure_ascii=False)
print(len(demo), 'demo park')
