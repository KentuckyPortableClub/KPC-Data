"""Offline tests (no network): python -m pytest -q tests   or   python kpc_engine.py selftest"""
import json, pathlib, re, sys
import pytest
from conftest import FIX, ROOT
from core import adapters, gaps, geo, gis, names, scope, workers, checks, registry
from core.notes import Notes, confidence_of
from core.polite import Polite


@pytest.fixture
def club(): return adapters.Club(FIX / 'data', FIX / 'links', FIX / 'pota')


def test_adapter_shapes(club):
    tn = club.parks('US-TN'); assert tn['US-0019']['n'].startswith('Cumberland Gap') and tn['US-0019']['lat'] == 36.6038
    assert club.parks('CA-BC')['CA-0001']['n'] == 'Alaksen National Wildlife Area'
    ky = club.parks('US-KY'); assert set(ky) == {'US-0050', 'US-1284'}
    assert set(club.parks('CH')) == {'CH-0001', 'CH-0002'}           # POTA fallback list
    assert club.outline_status('US-TN', 'US-0019') == 'official'
    assert club.outline_status('US-TN', 'US-11241') == 'approx'
    assert club.outline_status('US-KY', 'US-0050') == 'official'      # KY answer key tracts
    assert club.outline_status('CH', 'CH-0001') == 'approx' and club.outline_status('CH', 'CH-0002') == 'official'
    assert club.has_map('US-TN', 'US-0019')


def test_access_labels(club):
    a = club.access_points('US-TN', 'US-11241')
    assert [x[3] for x in a] == ['Tennessee Wildlife Resources Agency', 'TWRA']    # KPC-made and work-in-progress dropped
    k = club.access_points('US-KY', 'US-0050'); assert len(k) == 1 and k[0][3] == 'NPS'


def test_gaps(club, tmp_path):
    G, parks = gaps.build(club, ['US-TN', 'US-KY', 'CH', 'CA-BC'], tmp_path)
    assert 'outline' not in G['US-TN'].get('US-0019', {}).get('kinds', [])
    assert 'outline' in G['US-TN']['US-11241']['kinds'] and 'parking' not in G['US-TN']['US-11241']['kinds']
    assert 'camping' in G['US-TN']['US-12345']['kinds']                 # 'Camp' word, no campground row
    assert 'hours' in G['US-KY']['US-1284']['kinds']
    for area, rows in G.items():                                         # scope: hours/fees/closures only in KY
        for r in rows.values():
            if area != 'US-KY': assert not {'hours', 'fees', 'closures'} & set(r['kinds'])
            if not area.startswith(('US-', 'CA-')): assert not {'parking', 'camping', 'trail'} & set(r['kinds'])
    assert (tmp_path / 'gaps.json').exists() and (tmp_path / 'gaps-summary.md').exists()


def test_scope_guard():
    from plugins.ky_info import Hours
    assert not Hours().wants({'area': 'US-TN', 'kinds': ['hours']})
    assert Hours().wants({'area': 'US-KY', 'kinds': ['hours']})
    with pytest.raises(scope.ScopeError): scope.guard('closures', {'area': 'CA-ON'})
    with pytest.raises(scope.ScopeError): scope.guard('parking', {'area': 'GB'})


def test_names_tiers():
    assert names.tier('Mammoth Cave National Park', 'Mammoth Cave National Park', {}, True, 0)[0] == 'T-1'
    assert names.tier('Trail of Tears National Historic Trail', 'Trail Of Tears Park', {}, True, 0)[0] in ('T-3', 'T-4', 'T-6')
    assert names.kind_clash('Trail of Tears National Historic Trail', 'Trail Of Tears Park')
    assert not names.kind_clash('Carter Caves State Park', 'Carter Caves State Resort Park')


def test_geo_axis_and_pin():
    assert geo.northing_first(3006) and geo.northing_first(3844) and not geo.northing_first(3857)
    from shapely.geometry import box
    inside, d = geo.pin_relation(37.0, -85.0, box(-85.1, 36.9, -84.9, 37.1)); assert inside
    inside, d = geo.pin_relation(37.0, -85.0, box(-84.999, 36.9, -84.9, 37.1)); assert not inside and 50 < d < 150


def test_kml_parse():
    k = (b'<kml><Placemark><name>Test Park</name><Polygon><outerBoundaryIs><LinearRing><coordinates>-85,37 -84,37 -84,38 -85,38 -85,37'
         b'</coordinates></LinearRing></outerBoundaryIs></Polygon></Placemark></kml>')
    r = gis._kml_or_geojson(k, {'url': 'x'}); assert r[0]['name'] == 'Test Park' and r[0]['geom'].area == 1.0


def test_notes_blocked_is_not_not_found():
    n = Notes().looked('a', 'blocked (TLS)').looked('b', 'blocked (robots)'); assert n.blocked_only()
    n.looked('c', 'no hit'); assert not n.blocked_only()
    assert confidence_of('T-1', 'STRONG', 'approximate')[0] == 'weak'          # approximate is never a full YES


def test_polite_offline_and_honest_ua(tmp_path):
    P = Polite(cache_dir=tmp_path, offline=True)
    r = P.get('https://example.gov/x'); assert r.blocked and 'offline' in r.blocked
    assert 'KPC' in P.m.ua and 'Mozilla' not in P.m.ua and 'Chrome' not in P.m.ua


def test_workers_resume(tmp_path):
    groups = [('A', [{'area': 'X', 'ref': f'X-{i}'} for i in range(30)]), ('B', [{'area': 'X', 'ref': f'Y-{i}'} for i in range(10)])]
    seen = []
    res, t = workers.run(groups, lambda ag, row, i: seen.append(row['ref']) or {'ref': row['ref'], 'area': 'X', 'status': 'found'}, tmp_path, 't', n=2)
    assert len(res) == 40 and not t
    seen.clear()
    res2, t = workers.run(groups, lambda ag, row, i: seen.append(row['ref']) or {'ref': row['ref'], 'area': 'X'}, tmp_path, 't', n=2, resume=True)
    assert seen == [] and len(res2) == 40                                     # nothing redone, results kept


def test_registry_rules():
    R = registry.Registry()
    for s in R.sources:                                                       # official sources only
        assert not re.search(r'openstreetmap|overpass|geofabrik|protectedplanet|wdpa|unep-wcmc|google\.|wikidata|wikipedia|alltrails', s.get('url', ''), re.I), s['id']
        assert 'token=' not in s.get('url', '')
    us = R.for_area('US-KY', 'outline', include_unverified=True)
    assert us and not any(s.get('cc') == 'EU' for s in us)
    assert all((s.get('area') or s.get('cc')) in ('US-KY', 'US') for s in us)
    ky_first = [s for s in us if s.get('grade') == 'official']
    assert (ky_first[0].get('area') or ky_first[0].get('cc')) == 'US-KY'


def test_checks_identity_and_boiler():
    parks = {'US-TN': {'US-0019': {'n': 'Cumberland Gap National Historical Park'}}}
    rows = [{'ref': 'US-0019', 'area': 'US-TN', 'park': 'Cumberland Gap National Historical Park', 'hours': 'Open daily 8 am - 5 pm'},
            {'ref': 'US-0019', 'area': 'US-TN', 'park': 'Wrong Name', 'hours': 'x'},
            {'ref': 'US-0019', 'area': 'US-TN', 'park': 'Cumberland Gap National Historical Park', 'hours': 'Please enable JavaScript to view this page'}]
    kept, prob = checks.check_rows(None, rows, parks, check_urls=False)
    assert len(kept) == 1 and len(prob) == 2


def test_outline_bands():
    from plugins.outline import Outline
    from shapely.geometry import box
    class E:  # a tiny fake engine
        _shapes = {}
        def pin_typo_check(self, *a): return None
    g = box(-86.2, 37.1, -86.0, 37.3)
    src = {'id': 'NPS', 'url': 'https://example.gov/MapServer/2', 'kind': 'arcgis', 'grade': 'official', 'name_field': 'UNIT_NAME', 'agency': 'NPS'}
    c = {'src': src, 'hit': {'id': 7, 'geom': g, 'attrs': {}}, 'name': 'Mammoth Cave National Park', 'tier': 'T-1', 'sim': 1, 'inside': True, 'pin_m': None, 'step': 'L0', 'acres': 50000}
    row = {'area': 'US-KY', 'ref': 'US-0050'}; p = {'ref': 'US-0050', 'n': 'Mammoth Cave National Park'}
    r = Outline()._finish(E(), row, p, 37.2, -86.1, {'ref': 'US-0050', 'area': 'US-KY'}, Notes(), [c], [], 'L0')
    assert r['status'] == 'found' and r['band'] == 'STRONG' and r['answer'] == '' and r['checked_by'] == ''
    for k in ('ref', 'st', 'url', 'name_field', 'agency', 'kind', 'licence'): assert k in r
    c2 = dict(c, inside=False, pin_m=90, tier='T-2')
    r = Outline()._finish(E(), row, p, 37.2, -86.1, {'ref': 'US-0050', 'area': 'US-KY'}, Notes(), [c2], [], 'L0')
    assert r['rule'] == 'R-G12' and r['status'] == 'candidate'
    c3 = dict(c, src=dict(src, grade='approximate'))
    r = Outline()._finish(E(), row, p, 37.2, -86.1, {'ref': 'US-0050', 'area': 'US-KY'}, Notes(), [c3], [], 'L0')
    assert r['status'] == 'candidate' and r['notes']['confidence']['level'] == 'weak'
    nb = Notes().looked('x', 'blocked (TLS)')
    r = Outline()._finish(E(), row, p, 37.2, -86.1, {'ref': 'US-0050', 'area': 'US-KY'}, nb, [], [('x', 'blocked (TLS)')], 'L0')
    assert r['status'] == 'blocked'


def test_docs_slug():
    from plugins.docs import Docs
    assert Docs._slug_score('https://parks.ky.gov/olive-hill/parks/resort/carter-caves-state-resort-park', ['Carter', 'Caves']) == 1


def test_offline_run(tmp_path):
    """End to end on the fixtures with no network: every row ends as blocked / not found, files are written, exit 0."""
    import kpc_engine
    rc = kpc_engine.main(['run', '--data', str(FIX / 'data'), '--links', str(FIX / 'links'), '--pota', str(FIX / 'pota'), '--out', str(tmp_path),
                          '--areas', 'US-TN,US-KY,CH', '--offline', '--workers', '2', '--steps', 'L0,L4'])
    assert rc == 0
    for f in ('board.md', 'blocked.csv', 'fixes.csv', 'pin-typos.json', 'spot-check.md', 'questions.json', 'whynot.json', 'gaps.json', 'findings.jsonl'):
        assert (tmp_path / f).exists(), f
    q = json.load(open(tmp_path / 'questions.json'))['questions']; assert q == []
    # the engine wrote nothing outside --out
    assert not (FIX / 'data' / 'questions.json').exists()


def test_pack_registry_rules():
    from core.registry import Registry, norm_url
    R = Registry()
    if not R.no_rows: return                                     # pack not seeded on this machine
    ref, lay, rec = next(iter(R.no_rows))
    assert R.is_no(ref, 'https://' + lay + '/query', rec)        # NO rows are matched on the normalised layer URL
    assert all('wdpa' not in s['url'].lower() for s in R.sources)
    assert not any(s.get('cc') == 'EU' for s in R.for_area('MX'))  # the EU compilation is for EU / EEA countries only
    assert not any('Staff_Directory' in s['id'] for s in R.for_area('US-TN'))
    assert norm_url('HTTPS://a.gov/x/MapServer/3/query') == 'a.gov/x/mapserver/3'


def test_site_codes_and_local_words():
    from core import names
    assert names.core_words('ROSCI0123 Pădurea Trivalea') == ['padurea', 'trivalea']
    assert names.core_words('Naturschutzgebiet Lüneburger Heide') == ['luneburger', 'heide']


def test_eu_compilation_always_approximate():
    from core.registry import Registry
    r = Registry(files=[], extra_found_layers=[{'id': 'x', 'url': 'https://bio.discomap.eea.europa.eu/arcgis/rest/services/ProtectedSites/CDDA_Dyna_WM/MapServer/4',
                                               'grade': 'official', 'verified': {'status': 'approved'}, 'area': 'DE', 'cc': 'DE', 'use': 'outline'}])
    assert [s for s in r.sources if s['id'] == 'x'][0]['grade'] == 'approximate'


def test_us_ca_work_order():
    from core.priority import park_class, order_groups
    assert park_class({'area': 'US-KY', 'park': 'Dawkins Line Rail Trail'})[0] == 1
    assert park_class({'area': 'US-KY', 'park': 'Sheltowee Trace National Recreation Trail'})[0] == 7
    assert park_class({'area': 'US-KY', 'park': 'Cumberland Falls State Resort Park'})[0] == 2
    assert park_class({'area': 'US-KY', 'park': 'Perryville Battlefield State Historic Site'})[0] == 3
    assert park_class({'area': 'US-KY', 'park': 'Jefferson County Memorial Forest'})[0] == 5
    assert park_class({'area': 'GB', 'park': 'Peak District National Park'})[0] == 4
    g = order_groups([('blm', [{'area': 'US-NV', 'park': 'Red Rock Canyon National Conservation Area'}]),
                      ('kytrails', [{'area': 'US-KY', 'park': 'Dawkins Line Rail Trail'}])])
    assert g[0][0] == 'kytrails'


def test_grade_shape_for_chat11():
    from core import grading
    rows = [{'ref': 'US-0001', 'area': 'US-KY', 'status': 'found', 'url': 'https://x.ky.gov/a'},
            {'ref': 'US-0002', 'area': 'US-KY', 'status': 'not found', 'whynot': {'tag': 'no-layer: nothing at the pin'}}]
    for k in ('outline', 'docs', 'parking', 'camping', 'trail', 'hours'):
        g = grading.report(k, rows)
        assert set(g) >= {'verdict', 'bar', 'top_miss_reasons', 'examples'} and len(g['examples']) <= 5
    assert grading.report('parking', rows)['verdict'].startswith('PASS')


def test_export_handback_shapes(tmp_path):
    import json as _j
    from core import export
    w = tmp_path / 'work' / 'outline'; w.mkdir(parents=True)
    rows = [{'ref': 'US-1', 'area': 'US-KY', 'status': 'found', 'rule_g': 'SURE', 'band': 'STRONG', 'service_url': 'https://x.ky.gov/arcgis/rest/services/P/MapServer/0', 'name_field': 'NAME', 'acres_approx': 10.0, 'date': '2026-11-01'},
            {'ref': 'US-2', 'area': 'US-KY', 'status': 'evidence', 'rule_g': 'UNLIKELY', 'service_url': 'https://x/MapServer/1'},
            {'ref': 'GB-1', 'area': 'GB', 'status': 'candidate', 'rule_g': 'LIKELY', 'service_url': 'https://y/FeatureServer/0', 'name_field': 'NAME'}]
    (w / 'results-p1-0.jsonl').write_text('\n'.join(_j.dumps(r) for r in rows))
    wrote, flags = export.export(tmp_path, 't')
    ext = _j.load(open(tmp_path / 'handback' / 'external-sources-t.json'))
    assert ext == {'Parks|US-1': ['https://x.ky.gov/arcgis/rest/services/P/MapServer/0']}       # UNLIKELY never exported
    g = _j.load(open(tmp_path / 'handback' / 'world-sources-t.json'))['rest']['GB-1']
    assert g['layer'] == 'https://y/FeatureServer/0' and g['field'] == 'NAME' and g['status'].startswith('POSSIBLE MATCH')
    assert (tmp_path / 'handback' / 'hardlook-t.xlsx').exists() and flags == []      # round 4: docs-pagefix has club samples now
