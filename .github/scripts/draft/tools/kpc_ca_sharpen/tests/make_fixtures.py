import json, math, os
T = 'tests'
os.makedirs(T + '/make_list/canada-bounds', exist_ok=True); os.makedirs(T + '/make_list/ca-key', exist_ok=True)
CP = 'https://maps-cartes.ec.gc.ca/arcgis/rest/services/CWS_SCF/CPCAD/MapServer/0'
PROV = 'https://example.gov.test/arcgis/rest/services/Parks/MapServer/2'
BIG = 'https://example.gov.test/arcgis/rest/services/Big/FeatureServer/0'
BC = 'https://openmaps.gov.bc.ca/geo/pub/wfs'
GJ = 'https://www.donneesquebec.ca/recherche/dataset/578d182d-4897-4c11-aa7f-ee0cfed222a0/resource/5abd7e57-bfeb-49ba-a76c-93d961ae0633/download/sites_classes_pg.geojson'
def sq(x0, y0, d, cw=True):
    r = [[x0, y0], [x0 + d, y0], [x0 + d, y0 + d], [x0, y0 + d], [x0, y0]]
    return r[::-1] if cw else r          # Esri outer = clockwise
def circle(x0, y0, rdeg, n, wig=0.0):
    pts = [[round(x0 + (rdeg + wig * math.sin(i * 0.7)) * math.cos(2 * math.pi * i / n) / math.cos(math.radians(y0)), 6),
            round(y0 + (rdeg + wig * math.sin(i * 0.7)) * math.sin(2 * math.pi * i / n), 6)] for i in range(n)]
    pts.append(pts[0]); return pts[::-1]
fld = lambda *ns: [{'name': 'OBJECTID', 'type': 'esriFieldTypeOID'}] + [{'name': n, 'type': 'esriFieldTypeString'} for n in ns]
fx = {'arcgis': {
  CP: {'info': {'geometryType': 'esriGeometryPolygon', 'objectIdField': 'OBJECTID', 'fields': fld('NAME_E', 'NAME_F')}, 'features': [
      {'attributes': {'OBJECTID': 1, 'NAME_E': 'Alpha Lake Park', 'NAME_F': 'Parc du Lac-Alpha'}, 'geometry': {'rings': [sq(-75.0, 46.0, 0.01)]}},
      {'attributes': {'OBJECTID': 2, 'NAME_E': 'Some Other Place', 'NAME_F': ''}, 'geometry': {'rings': [sq(-74.0, 46.0, 0.01)]}},
      {'attributes': {'OBJECTID': 3, 'NAME_E': 'Beta  Marsh Wildlife Area', 'NAME_F': ''}, 'geometry': {'rings': [sq(-74.5, 46.2, 0.02)]}}]},
  PROV: {'refuse_3m': True, 'info': {'geometryType': 'esriGeometryPolygon', 'objectIdField': 'OBJECTID', 'fields': fld('NOM')}, 'features': [
      {'attributes': {'OBJECTID': 7, 'NOM': 'ALPHA LAKE PARK'}, 'geometry': {'rings': [sq(-74.995, 46.0, 0.01)]}}]},
  BIG: {'info': {'geometryType': 'esriGeometryPolygon', 'objectIdField': 'OBJECTID', 'fields': fld('NAME')}, 'features': [
      {'attributes': {'OBJECTID': 5, 'NAME': 'Very Big Reserve'}, 'geometry': {'rings': [circle(-73.0, 47.0, 0.3, 4000, 0.00003)]}}]}},
  'wfs': [{'type': 'Feature', 'properties': {'PARK_NAME': 'Gamma Park', 'OBJECTID': 99},
           'geometry': {'type': 'Polygon', 'coordinates': [circle(-123.0, 49.2, 0.002, 400, 0.00002)[::-1]]}}],
  'geojson': {GJ: {'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'nom_bien': 'Site patrimonial Delta'},
           'geometry': {'type': 'Polygon', 'coordinates': [sq(-71.2, 46.8, 0.003, cw=False)]}}]}}}
json.dump(fx, open(T + '/fixtures.json', 'w'), ensure_ascii=False)
def row(ref, url, rid, nm, bb, **k):
    return dict({'ref': ref, 'name': nm, 'province': 'QC', 'layer_url': url, 'record_id': rid, 'record_name': nm, 'current_detail_m': None,
                 'old_bbox': bb, 'old_points': 5, 'set': 'no detail_m (the 273)', 'key_id': str(rid)}, **k)
parks = [row('T-1', CP, '1', 'Alpha Lake Park', [-75.0, 46.0, -74.98, 46.01]),
         row('T-1', PROV, '7', 'Alpha Lake Park', [-75.0, 46.0, -74.98, 46.01]),
         row('T-2', CP, '2', 'Beta Marsh Wildlife Area', [-74.51, 46.19, -74.47, 46.23]),
         row('T-3', BIG, '5', 'Very Big Reserve', [-73.5, 46.6, -72.5, 47.4]),
         row('T-4', BC, None, 'Gamma Park', [-123.01, 49.19, -122.99, 49.21], province='BC'),
         row('T-5', GJ, None, 'Site patrimonial Delta', [-71.21, 46.79, -71.19, 46.81]),
         row('T-6', CP, None, 'Nowhere Park', [-60.0, 50.0, -59.9, 50.1]),
         row('T-7', CP, '1', 'Alpha Lake Park', [-75.0, 46.0, -74.98, 46.01]),
         row('T-7', 'https://down.example.test/arcgis/rest/services/X/MapServer/0', '4', 'Alpha Lake Park', [-75.0, 46.0, -74.98, 46.01])]
json.dump(parks, open(T + '/sample_parks.json', 'w'), ensure_ascii=False, indent=1)
# make-list fixture
B = T + '/make_list/canada-bounds/'
gj = lambda d: {'type': 'MultiPolygon', 'coordinates': [[sq(-75.0, 46.0, d, cw=False)]]}
json.dump({'type': 'Feature', 'properties': {'ref': 'CA-0001', 'name': 'Alpha Lake Park', 'cpcad': 'Alpha Lake Park'}, 'geometry': gj(0.01)}, open(B + 'CA-0001.json', 'w'))
json.dump({'type': 'Feature', 'properties': {'ref': 'CA-0002', 'name': 'Fine Park', 'detail_m': 3}, 'geometry': gj(0.01)}, open(B + 'CA-0002.json', 'w'))
json.dump({'type': 'Feature', 'properties': {'ref': 'CA-0003', 'name': 'Coarse Park', 'detail_m': 20, 'cpcad': 'Coarse Park'}, 'geometry': gj(0.02)}, open(B + 'CA-0003.json', 'w'))
json.dump({'parks': {'CA-0001': {'m': [[1, 'Alpha Lake Park', 30, 'name'], ['Prov parks:7', 'ALPHA LAKE PARK', 30, 'name'], ['Prov parks:7', 'ALPHA LAKE PARK', 30, 'name'],
                                       ['QC-SPC Minis:5', 'Site patrimonial Delta', 1, 'name'], ['Québec Zone :n-Zec Test', 'Zec Test', 9, 'name']]},
                     'CA-0002': {'m': [[9, 'Fine Park', 1, 'name']]}, 'CA-0003': {'m': []}}}, open(T + '/make_list/ca-key/CA-QC.json', 'w'), ensure_ascii=False)
json.dump({'Prov parks': [PROV, PROV], 'Québec Zone ': ['https://example.gov.test/arcgis/rest/services/TRQ/MapServer/16'], 'cpcad': [CP]},
          open(T + '/make_list/ca-key/layers.json', 'w'), ensure_ascii=False)
exp = {'detail_m': {'T-1': 5, 'T-2': 3, 'T-3': 6, 'T-4': 3, 'T-5': 3, 'T-6': 'not done', 'T-7': 3},
       'make_list': sorted([['CA-0001', CP, '1'], ['CA-0001', PROV, '7'], ['CA-0001', GJ, None],
                            ['CA-0001', 'https://example.gov.test/arcgis/rest/services/TRQ/MapServer/16', None], ['CA-0003', CP, None]], key=lambda x: (x[0], x[1], x[2] or ''))}
json.dump(exp, open(T + '/expected_summary.json', 'w'), indent=1)
