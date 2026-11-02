"""Every hand-back export must match the club's real sample files (intake_samples, Nov 1) key for key."""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from core import export

S = pathlib.Path(__file__).resolve().parents[1] / 'fixtures' / 'handback_samples'


def sample(n): return json.load(open(S / f'{n}.sample.json'))['sample']


def _keys_union(rows): return set().union(*[set(r) for r in rows])
def _keys_common(rows): return set.intersection(*[set(r) for r in rows])


def _make(tmp):
    w = tmp / 'work'
    rows = {
        'outline': [{'ref': 'US-0001', 'area': 'US-KY', 'park': 'Test State Park', 'status': 'found', 'rule_g': 'SURE', 'band': 'STRONG', 'date': '2026-11-01',
                     'service_url': 'https://x.ky.gov/arcgis/rest/services/P/MapServer/0', 'url': 'https://x.ky.gov/arcgis/rest/services/P/MapServer/0?f=html',
                     'name_field': 'NAME', 'agency': 'KY Parks', 'record': 3, 'record_name': 'Test State Park', 'acres_approx': 120.4, 'record_link': 'https://x/q'},
                    {'ref': 'GB-0001', 'area': 'GB', 'park': 'Glen Test NNR', 'status': 'candidate', 'rule_g': 'LIKELY', 'date': '2026-11-01',
                     'service_url': 'https://services1.arcgis.com/a/arcgis/rest/services/NNR/FeatureServer/0', 'name_field': 'NAME', 'agency': 'NatureScot'},
                    {'ref': 'GB-0002', 'area': 'GB', 'park': 'Wales NNR', 'status': 'found', 'rule_g': 'SURE', 'date': '2026-11-01',
                     'service_url': 'https://datamap.gov.wales/geoserver/ows', 'url': 'https://datamap.gov.wales/geoserver/ows?service=WFS', 'agency': 'NRW'}],
        'docs': [{'ref': 'US-0001', 'area': 'US-KY', 'status': 'found', 'page': 'https://parks.ky.gov/x', 'map': {'url': 'https://parks.ky.gov/x.pdf', 'page': 1}, 'agency': 'KY Parks', 'date': '2026-11-01'}],
        'parking': [{'ref': 'US-0001', 'area': 'US-KY', 'park': 'Test State Park', 'status': 'found', 'date': '2026-11-01',
                     'features': [{'lat': 37.1, 'lon': -84.1, 'name': 'Lot A', 'type': 'Parking', 'agency': 'KY Parks', 'how': 'place', 'source': 'nope', 'record_link': 'https://x/FeatureServer/0/query?where=1'}]},
                    {'ref': 'US-0002', 'area': 'US-KY', 'park': 'Other WMA', 'status': 'not found', 'date': '2026-11-01', 'whynot': {'tag': 'no point'}}],
        'camping': [{'ref': 'US-0001', 'area': 'US-KY', 'park': 'Test State Park', 'status': 'found', 'date': '2026-11-01',
                     'features': [{'lat': 37.1, 'lon': -84.1, 'name': 'Main CG', 'how': 'place', 'source': 'nope', 'record_link': 'https://y/MapServer/2/query?where=1', 'm': 0}]},
                    {'ref': 'CA-0001', 'area': 'CA-AB', 'park': 'Test Provincial Park', 'status': 'found', 'date': '2026-11-01',
                     'features': [{'lat': 51.1, 'lon': -114.1, 'name': 'CG', 'how': 'near', 'source': 'nope', 'record_link': 'https://z/MapServer/0/query?where=1', 'm': 3000}]}],
    }
    for k, rs in rows.items():
        (w / k).mkdir(parents=True)
        (w / k / 'results-p1-0.jsonl').write_text('\n'.join(json.dumps(r) for r in rs) + '\n')
    export.export(tmp, 't')
    return tmp / 'handback'


def test_export_shapes_match_samples(tmp_path):
    hb = _make(tmp_path)
    J = lambda n: json.load(open(hb / n))
    # external-sources-oct30
    e = J('external-sources-t.json'); assert all(k.split('|')[0] in ('Parks', 'Trail') and isinstance(v, list) for k, v in e.items()) and 'Parks|US-0001' in e
    # world-sources-r15
    ws, s = J('world-sources-t.json'), sample('world-sources-r15')
    assert set(ws) == set(s)
    assert set(ws['rest']['GB-0001']) == _keys_union([v for k, v in s['rest'].items() if k != 'about'])
    assert set(ws['other']['GB-0002']) == _keys_union(list(s['other'].values()))
    # docs-found-us-oct31-v2 (and the Hard Look CA / maplinks files share it)
    d = J('docs-found-t.json')
    for n in ('docs-found-us-oct31-v2', 'docs-found-hardlook-ca-oct31', 'docs-found-maplinks'):
        assert set(d['US-0001']) == _keys_common(list(sample(n).values())), n
    # parking-hunt-oct31
    p, s = J('parking-hunt-t.json'), sample('parking-hunt-oct31')
    assert set(p) == set(s)
    assert set(next(iter(p['layers'].values()))) == _keys_union(list(s['layers'].values()))
    srows = list(s['rows'].values())
    for r in p['rows'].values(): assert _keys_common(srows) <= set(r) <= _keys_union(srows)
    assert list(p['rows']['US-0001'])[:4] == list(srows[0])[:4]
    # camping-us-oct31 / camping-ca-nov1
    c, s = J('camping-t.json'), sample('camping-us-oct31')
    assert set(c) == set(s) and all(isinstance(v, int) for v in c['layers'].values())
    for r in c['rows'].values(): assert set(r) <= _keys_union(list(s['rows'].values())) and 'Camping?' in r and r['Camping?'] != 'NO'
    cc, s = J('camping-ca-t.json'), sample('camping-ca-nov1')
    assert set(cc) == set(s)
    for r in cc['rows'].values(): assert set(r) <= _keys_union(list(s['rows'].values()))
    # acres-us-ca-oct31
    a, s = J('acres-t.json'), sample('acres-us-ca-oct31')
    assert set(a) == set(s)
    assert set(a['Acres not downloadable'][0]) == set(s['Acres not downloadable'][0])
    assert set(a['Sources'][0]) == set(s['Sources'][0])
    assert isinstance(a['Acres not downloadable'][0]['Size'], int)
    # portals-us-ca-oct31
    po, s = J('portals-t.json'), sample('portals-us-ca-oct31')
    assert set(po) == set(s) and po['rows']
    assert list(po['rows'][0]) == list(s['rows'][0])
    # hardlook xlsx: the exact columns from HANDBACK_FORMATS.md
    from openpyxl import load_workbook
    assert [c.value for c in next(load_workbook(hb / 'hardlook-t.xlsx').active.iter_rows(max_row=1))] == export.HARDLOOK_COLS
