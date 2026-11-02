#!/usr/bin/env python3
"""Writes the small synthetic fixtures in tests/fixtures (stdlib only). Run once; the files are committed."""
import json, os, zipfile

FX = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures')
os.makedirs(os.path.join(FX, 'parkinfo'), exist_ok=True)
os.makedirs(os.path.join(FX, 'keys', 'us-key'), exist_ok=True)


def w(name, obj):
    p = os.path.join(FX, name)
    with open(p, 'w', encoding='utf-8', newline='') as f:
        f.write(obj if isinstance(obj, str) else json.dumps(obj, indent=1, ensure_ascii=False))


def row(name, typ, lat, lon):
    return [name, '', typ, '', '', lat, lon]


# park pins: club shape for KY, POTA-API list shape for TN, CA.json with the province in column 10
w('parkinfo/US-KY.json', {'parks': {
    'US-1001': row('Barren River Lake State Resort Park', 'State Park', 37.0, -86.0),
    'US-1002': row('Clay Wildlife Management Area', 'WMA', 38.2, -83.8),
    'US-1003': row('Taylor Lake State Park', 'State Park', 37.5, -85.5),
    'US-1004': row('Blanton Forest State Nature Preserve', 'Nature Preserve', 36.9, -83.2),
    'US-1005': row('Pennyrile Forest State Resort Park', 'State Park', 37.07, -87.66),
    'US-1006': row('Yellowbank WMA', 'WMA', 37.9, -86.4),
    'US-1007': row('Tiny Spring Nature Preserve', 'Nature Preserve', 37.6, -84.6),
    'US-1008': row('Big Bluff WMA', 'WMA', 37.2, -84.2),
    'US-1009': row('Twin Hills WMA', 'WMA', 37.3, -84.3),
    'US-1010': row('Twin Hills Annex State Forest', 'State Forest', 37.31, -84.31),
    'US-1011': row('Bad Branch State Nature Preserve', 'Nature Preserve', 37.07, -82.77),
    'US-1012': row('Cedar Creek WMA', 'WMA', 37.0, -85.0),
    'US-1013': row('Rock Bridge WMA', 'WMA', 37.1, -85.3),
    'US-1014': row('Green Fork WMA', 'WMA', 37.4, -83.4),
    'US-1015': row('Green Fork Wildlife Management Area', 'WMA', 37.45, -83.45),
}})
w('parkinfo/US-TN.json', [
    {'reference': 'US-2001', 'name': 'Frozen Head State Park', 'latitude': 36.13, 'longitude': -84.47,
     'locationDesc': 'US-TN'},
    {'reference': 'US-2002', 'name': 'Short Springs State Natural Area', 'latitude': 35.4, 'longitude': -86.2,
     'locationDesc': 'US-TN'}])
w('parkinfo/CA.json', {'parks': {
    'CA-3001': ['Algonquin Provincial Park', '', 'Provincial Park', '', '', 45.8, -78.4, '', '', '', 'ON'],
    'CA-3002': ['Polar Bear Provincial Park', '', 'Provincial Park', '', '', 54.5, -83.0, '', '', '', 'ON']}})
# key: record ids + outline acres
w('keys/us-key/US-KY.json', {'parks': {
    'US-1005': {'g': 'official', 'm': [['KYSP-0042', 'Pennyrile Forest SRP', 860, 'name']]},
    'US-1008': {'g': 'official', 'm': [['PADUS-777', 'Big Bluff WMA', 100, 'name']]}}})
w('ky-answer-key.json', {'updated': '2026-10-31', 'parks': {
    'US-1001': {'n': 'Barren River Lake State Resort Park', 't': 'State Park',
                'tracts': [['bstate', 'Barren River Lake State Resort Park', 2000, 'name', 1]]},
    'US-1002': {'n': 'Clay Wildlife Management Area', 't': 'WMA', 'tracts': [['bwma', 'Clay WMA', 2050, 'name', 2]]},
    'US-1006': {'n': 'Yellowbank WMA', 't': 'WMA', 'tracts': [['bwma', 'Yellowbank WMA', 300, 'name', 1]]}}})

# the research file: mixed field names on purpose
w('acres-research.json', {
    'updated': '2026-10-31',
    'agencies': [
        {'agency': 'Kentucky State Parks', 'state': 'KY', 'list_url': 'https://parks.ky.example/acreage.csv',
         'format': 'CSV', 'size_column': 'Total Acres', 'unit': 'acres', 'status': 'FOUND', 'park_kind': 'State Park'},
        {'agency': 'KDFWR', 'name': 'KDFWR WMA list', 'area': 'US-KY', 'url': 'https://fw.ky.example/wma-list.html',
         'type': 'HTML table', 'kind': 'WMA', 'size_col': 'Acreage', 'status': 'found'},
        {'agency': 'KDFWR', 'name': 'KDFWR lands layer', 'area': 'Kentucky',
         'layer_url': 'https://gis.ky.example/arcgis/rest/services/KDFWR/Lands/MapServer/0', 'format': 'ArcGIS',
         'size_field': 'AREA_HA', 'id_column': 'UNIT_ID', 'name_column': 'PROP_NAME', 'status': 'FOUND'},
        {'agency': 'KY open data', 'area': 'US-KY', 'url': 'https://data.ky.example/resource/abcd-1234.json',
         'format': 'Socrata', 'acres_column': 'acres', 'kind': 'WMA', 'status': 'FOUND'},
        {'agency': 'Mystery list', 'area': 'US-KY', 'url': 'https://misc.ky.example/list.json', 'kind': 'WMA',
         'status': 'FOUND'},
        {'agency': 'Blocked agency', 'area': 'US-KY', 'url': 'https://blocked.ky.example/secret/list.csv',
         'status': 'FOUND'},
        {'agency': 'Page-only agency', 'area': 'US-KY', 'page': 'https://pageonly.ky.example/', 'status': 'page only'},
        {'agency': 'Tennessee State Parks', 'state': 'Tennessee', 'file_url': 'https://tn.example/park-sizes.xlsx',
         'size_column': 'Area', 'units': 'sq mi', 'status': 'FOUND'},
        {'agency': 'TN no-list agency', 'state': 'TN', 'status': 'no list'},
        {'agency': 'Ontario Parks', 'province': 'Ontario', 'country': 'Canada',
         'api': 'https://data.on.example/api/3/action/datastore_search?resource_id=abc', 'format': 'CKAN',
         'size_column': 'AREA_KM2', 'status': 'FOUND'},
    ],
    'Acres not downloadable': [
        {'agency': 'KY Office of Nature Preserves', 'state': 'KY', 'park': 'Bad Branch State Nature Preserve',
         'acres': 2639, 'page': 'https://eec.ky.example/preserves/bad-branch'},
        {'agency': 'KY Office of Nature Preserves', 'state': 'KY', 'park': 'Tiny Spring Nature Preserve',
         'acres': '0.05', 'page': 'https://eec.ky.example/preserves/tiny-spring'},
    ]})
w('research-dict-shape.json', {
    'KY State Parks': {'state': 'KY', 'url': 'https://x.example/a.csv', 'size_column': 'Acres', 'status': 'FOUND'},
    'KDFWR': {'area': 'US-KY', 'list_url': 'https://x.example/b.csv', 'acres_column': 'ACRES', 'type': 'WMA',
              'hand_sizes': [{'name': 'Clay WMA', 'acres': 5}, ['Big Bluff WMA', '12 ha']]}})

w('ky_state_parks.csv', 'Kentucky State Parks acreage (2025),,\r\n,,\r\nPark,County,Total Acres\r\n'
  'Barren River Lake,Barren,"2,187"\r\nTotal,,"9,999"\r\n')
w('kdfwr_wma.html', '''<html><body><h1>WMA list</h1>
<table><tr><td>menu</td></tr></table>
<table>
<tr><th>WMA Name</th><th>County</th><th>Acreage</th><th>Notes</th></tr>
<tr><td>Clay WMA - North Tract</td><td>Bath</td><td>1,200</td><td></td></tr>
<tr><td>Clay WMA - South Tract</td><td>Bath</td><td>800</td><td></td></tr>
<tr><td>Taylor Lake WMA</td><td></td><td>500</td><td>lake</td></tr>
<tr><td>Big Bluff WMA</td><td></td><td>9,000</td><td></td></tr>
<tr><td>Twin Hills WMA</td><td></td><td>300</td><td>POTA US-1009 / US-1010</td></tr>
<tr><td>Blanton Forest</td><td></td><td>3,124 ac</td><td>US-1004</td></tr>
<tr><td>Total</td><td></td><td>15,000</td><td></td></tr>
</table></body></html>''')
w('arcgis_page0.json', {'objectIdFieldName': 'OBJECTID', 'exceededTransferLimit': True, 'features': [
    {'attributes': {'OBJECTID': 1, 'PROP_NAME': 'Pennyrile Forest', 'UNIT_ID': 'KYSP-0042', 'AREA_HA': 349.31}},
    {'attributes': {'OBJECTID': 2, 'PROP_NAME': 'Nowhere Tract', 'UNIT_ID': 'X-1', 'AREA_HA': 10}}]})
w('arcgis_page2.json', {'objectIdFieldName': 'OBJECTID', 'features': [
    {'attributes': {'OBJECTID': 3, 'PROP_NAME': 'Yellowbank WMA', 'UNIT_ID': 'W-77', 'AREA_HA': 100}}]})
w('socrata.json', [
    {'name': 'Cedar Creek WMA', 'acres': '1500', 'latitude': '37.9', 'longitude': '-82.5'},
    {'name': 'Rock Bridge WMA', 'acres': '700', 'county': 'Pike'},
    {'name': 'Green Fork Wildlife Management Area', 'acres': '400'},
    {'name': 'Unknown Hollow WMA', 'acres': '50'}])
w('mystery.json', {'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'name': 'Clay WMA',
                                                                                                  'size': '77'}}]})
w('ckan_on.json', {'success': True, 'result': {'records': [
    {'_id': 1, 'PARK_NAME': 'Algonquin Provincial Park', 'AREA_KM2': '10'},
    {'_id': 2, 'PARK_NAME': 'Polar Bear Provincial Park', 'AREA_KM2': '90 000'}]}})


def sq(cx, cy, r=0.3):
    return [[[cx - r, cy - r], [cx + r, cy - r], [cx + r, cy + r], [cx - r, cy + r], [cx - r, cy - r]]]


w('tiger_ky.json', {'features': [
    {'attributes': {'NAME': 'Barren County'}, 'geometry': {'rings': sq(-86.0, 37.0)}},
    {'attributes': {'NAME': 'Bath County'}, 'geometry': {'rings': sq(-83.8, 38.2)}},
    {'attributes': {'NAME': 'Adair County'}, 'geometry': {'rings': sq(-85.3, 37.1, 0.1)}}]})
w('routes.json', {
    'parks.ky.example/acreage.csv': 'ky_state_parks.csv',
    'fw.ky.example/wma-list.html': 'kdfwr_wma.html',
    'gis.ky.example/arcgis/rest/services/KDFWR/Lands/MapServer/0/query': {'0': 'arcgis_page0.json',
                                                                         '2': 'arcgis_page2.json'},
    'data.ky.example/resource/abcd-1234.json': 'socrata.json',
    'misc.ky.example/list.json': 'mystery.json',
    'blocked.ky.example/secret/list.csv': 'ky_state_parks.csv',
    'tn.example/park-sizes.xlsx': 'tn_sizes.xlsx',
    'data.on.example/api/3/action/datastore_search': 'ckan_on.json',
    'tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/State_County/MapServer/1/query': 'tiger_ky.json'})

# a minimal XLSX (inline strings), stdlib only
rows = [['Tennessee State Parks', '', ''], ['Park', 'Area', 'Note'], ['Frozen Head State Park', '1', ''],
        ['Short Springs State Natural Area', '2,000,000 m²', 'given in square metres']]


def cell(ref, v):
    if v and v.replace('.', '').isdigit():
        return f'<c r="{ref}"><v>{v}</v></c>'
    return f'<c r="{ref}" t="inlineStr"><is><t>{v}</t></is></c>'


sheet = ''.join('<row r="%d">%s</row>' % (i + 1, ''.join(cell('ABC'[j] + str(i + 1), v) for j, v in enumerate(r)))
                for i, r in enumerate(rows))
with zipfile.ZipFile(os.path.join(FX, 'tn_sizes.xlsx'), 'w') as z:
    z.writestr('[Content_Types].xml', '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>')
    z.writestr('_rels/.rels', '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')
    z.writestr('xl/workbook.xml', '<?xml version="1.0"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Sizes" sheetId="1" r:id="rId1"/></sheets></workbook>')
    z.writestr('xl/_rels/workbook.xml.rels', '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>')
    z.writestr('xl/worksheets/sheet1.xml', '<?xml version="1.0"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>' + sheet + '</sheetData></worksheet>')

# a minimal one-page PDF with a two-line table
lines = ['Kentucky State Nature Preserves', 'Blanton Forest 3,124 acres', 'Bad Branch 1985 2,639']
content = 'BT /F1 12 Tf 72 720 Td 14 TL ' + ' '.join(f'({t}) Tj T*' for t in lines) + ' ET'
objs = ['<< /Type /Catalog /Pages 2 0 R >>', '<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
        '<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>',
        f'<< /Length {len(content)} >>\nstream\n{content}\nendstream',
        '<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>']
out, offs = '%PDF-1.4\n', []
for i, o in enumerate(objs):
    offs.append(len(out))
    out += f'{i + 1} 0 obj\n{o}\nendobj\n'
xref = len(out)
out += f'xref\n0 {len(objs) + 1}\n0000000000 65535 f \n' + ''.join(f'{o:010d} 00000 n \n' for o in offs)
out += f'trailer\n<< /Size {len(objs) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n'
with open(os.path.join(FX, 'preserves.pdf'), 'w', encoding='latin-1', newline='') as f:
    f.write(out)
print('fixtures written to', FX)
