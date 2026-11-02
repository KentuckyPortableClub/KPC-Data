"""Round 4 (Nov 1): trail bar, Overlapping boundaries, 2-fer / 3-fer rules, WDPA rule W-10."""
import json
import pytest
from shapely.geometry import box, LineString
from core import rules, rule_g, fers, grading
from core.registry import Registry

LAT, LON = 37.0, -85.0
D = 0.001                                         # ~111 m north-south, ~89 m east-west here


@pytest.fixture(autouse=True)
def _fresh():
    rules.reset(); yield; rules.reset()


def feat(**k):
    f = {'lat': LAT, 'lon': LON, 'name': 'Carter Caves Trail', 'agency': 'National Park Service', 'pin_line_m': 50.0}
    f.update(k); return f


# ---------------------------------------------------------------- trail bar
def test_trail_bar_passes_on_agency_name_and_200m():
    ok, why = rule_g.trail_bar(feat(), 'Carter Caves State Park', 'nps.gov')
    assert ok and not why


def test_trail_bar_each_condition_fails_alone():
    assert not rule_g.trail_bar(feat(agency='Some County'), 'Carter Caves State Park', 'nps.gov')[0]
    assert not rule_g.trail_bar(feat(name='Hayes Branch'), 'Carter Caves State Park', 'nps.gov')[0]
    ok, why = rule_g.trail_bar(feat(pin_line_m=216.0), 'Carter Caves State Park', 'nps.gov')
    assert not ok and 'bar 200 m' in why[0]
    assert not rule_g.trail_bar(feat(pin_line_m=None), 'Carter Caves State Park', 'nps.gov')[0]


def test_trail_pin_distance_is_tunable():
    rules.load(set_=['grader.trail_pin_m=300'])
    assert rule_g.trail_bar(feat(pin_line_m=216.0), 'Carter Caves State Park', 'nps.gov')[0]
    assert any('trail_pin_m' in c[0] for c in rules.changed())


def test_aggregator_is_never_the_agency_own_line():
    assert not rule_g.agency_own(feat(agency='KyGovMaps'), 'kygovmaps')
    assert not rule_g.agency_own(feat(source='USGS Aggregated trails'), 'nps.gov')


def test_nht_marked_approximate_stays_approximate():
    rows = [{'ref': 'US-3791', 'park': 'Trail of Tears National Historic Trail', 'agency_group': 'nps.gov', 'status': 'found',
             'features': [feat(name='Trail of Tears National Historic Trail (approximate route)')]}]
    rule_g.apply_trail_bar(rows)
    assert rows[0]['status'] == 'found' and rows[0]['features'][0]['grade'] == 'approx'


def test_row_not_meeting_bar_becomes_candidate():
    rules.load(disable=['source_policy.state_mapping_compilations'])     # round 5: with the switch on, KyGovMaps can count
    rows = [{'ref': 'US-1', 'park': 'Carter Caves State Park', 'agency_group': 'parks.ky.gov', 'status': 'found',
             'features': [feat(agency='KyGovMaps')]}]
    rule_g.apply_trail_bar(rows)
    assert rows[0]['status'] == 'candidate' and 'trail bar not met' in json.dumps(rows[0]['whynot'])


# ---------------------------------------------------------------- Overlapping boundaries / grading
def _two_park_trail():
    f = lambda: [feat()]
    return [{'ref': r, 'area': 'US-KY', 'park': 'Carter Caves State Park', 'agency_group': 'nps.gov', 'status': 'found', 'features': f()}
            for r in ('US-1', 'US-2')]


def test_trail_overlap_is_not_a_failure_and_never_says_shared():
    rep = grading.report('trail', _two_park_trail())
    assert rep['measured']['overlapping_boundaries'] == 1 and not any('duplicate' in x or 'shared' in x for x in rep['fails'])
    assert 'shared' not in json.dumps(rep).lower()
    assert 'Overlapping boundaries' in grading.BARS['trail'] and 'shared' not in json.dumps(grading.BARS).lower()


def test_trail_overlap_goes_to_waiting_room_never_auto():
    rows = _two_park_trail()
    sug = fers.from_trail_rows(rows)
    assert len(sug) == 1 and sug[0]['auto'] is False and sug[0]['label'] == 'Overlapping boundaries'
    assert 'waiting room' in sug[0]['goes_to'] and rows[0]['features'][0]['overlap'] == 'Overlapping boundaries'


def test_parking_duplicates_still_fail_with_clear_wording():
    rows = [{'ref': r, 'area': 'US-KY', 'status': 'found', 'features': [{'lat': LAT, 'lon': LON, 'name': 'Lot', 'm': 10}]} for r in ('US-1', 'US-2')]
    assert any('duplicate facilities' in f for f in grading.report('parking', rows)['fails'])


def test_old_switch_names_still_work():
    rules.load(disable=['checks.resolve_shared_facilities'])
    assert not rules.on('checks.resolve_duplicate_facilities')
    rules.reset(); rules.load(set_=['grader.docs_shared_file_max=5'])
    assert rules.num('docs_same_file_max') == 5


# ---------------------------------------------------------------- 2-fer / 3-fer geometry
def test_touching_only_parks_do_not_count():
    a = fers.zone(box(LON - D, LAT - D, LON, LAT + D), 'land', LAT, LON)
    b = fers.zone(box(LON, LAT - D, LON + D, LAT + D), 'land', LAT, LON)
    r = fers.two_fer(a, b)
    assert r['relation'] == 'touching only' and not r['suggest']


def test_real_overlap_50yd_suggests_only():
    a = fers.zone(box(LON - 2 * D, LAT - 2 * D, LON + D, LAT + 2 * D), 'land', LAT, LON)
    b = fers.zone(box(LON, LAT - 2 * D, LON + 2 * D, LAT + 2 * D), 'land', LAT, LON)
    r = fers.two_fer(a, b)
    assert r['relation'] == 'overlap' and r['widest_m'] >= fers.YD50_M and r['suggest']


def test_trail_counts_within_100ft_of_line():
    z = fers.zone(LineString([(LON - D, LAT), (LON + D, LAT)]), 'trail', LAT, LON)
    assert z.area > 0 and abs(z.bounds[1] + fers.FT100_M) < 1.0       # 30.48 m either side


def test_wsr_corridor_uses_own_boundary_no_buffer():
    poly = box(LON - D, LAT - D, LON + D, LAT + D)
    assert abs(fers.zone(poly, 'wsr', LAT, LON).area - fers.zone(poly, 'land', LAT, LON).area) < 1e-6


def test_water_trail_uses_water_edge():
    line = LineString([(LON - D, LAT), (LON + D, LAT)])
    water = box(LON - D, LAT - D / 10, LON + D, LAT + D / 10)
    zw = fers.zone(line, 'water_trail', LAT, LON, water=water)
    zl = fers.zone(line, 'trail', LAT, LON)
    assert zw.area > zl.area                                            # water + 100 ft is wider than line + 100 ft


def test_three_fer_needs_trail_spot_in_patch():
    a = fers.zone(box(LON - 2 * D, LAT - 2 * D, LON + D, LAT + 2 * D), 'land', LAT, LON)
    b = fers.zone(box(LON, LAT - 2 * D, LON + 2 * D, LAT + 2 * D), 'land', LAT, LON)
    t_in = fers.zone(LineString([(LON + D / 2, LAT - 2 * D), (LON + D / 2, LAT + 2 * D)]), 'trail', LAT, LON)
    t_out = fers.zone(LineString([(LON - 5 * D, LAT - 2 * D), (LON - 5 * D, LAT + 2 * D)]), 'trail', LAT, LON)
    assert fers.three_fer(t_in, a, b)['suggest'] and not fers.three_fer(t_out, a, b)['suggest']
    assert fers.suggestion(['US-1', 'US-2', 'US-3'], 'x')['kind'] == '3-fer'


def test_fer_line_ft_is_tunable():
    rules.load(set_=['grader.fer_line_ft=50'])
    z = fers.zone(LineString([(LON - D, LAT), (LON + D, LAT)]), 'trail', LAT, LON)
    assert abs(z.bounds[1] + 50 * 0.3048) < 1.0


# ---------------------------------------------------------------- WDPA rule W-10
WD = 'https://services5.arcgis.com/Mj0hjvkNtV7NRhA7/arcgis/rest/services/WDPA_v0/FeatureServer/1 WDPA (last resort)'


def test_w10_wdpa_rejected_on_the_ordinary_path():
    t, why = rule_g.tier_g('Homosassa Springs Wildlife State Park', 'Homosassa Springs Wildlife State Park', True, layer=WD)
    assert t == 'UNLIKELY' and 'W-10' in why


def test_w10_last_resort_is_never_sure():
    t, why = rule_g.tier_g('Homosassa Springs Wildlife State Park', 'Homosassa Springs Wildlife State Park', True, layer=WD, last_resort=True)
    assert t == 'LIKELY' and 'last resort' in why


def test_w10_registry_keeps_wdpa_apart_as_last_resort():
    R = Registry()
    assert not any('wdpa' in (s.get('url') or '').lower() for s in R.sources)
    lr = R.last_resort_for('US-FL')
    assert lr and all(s['grade'] == 'approximate' and s['last_resort'] == 'WDPA (last resort)' for s in lr)


def test_w10_switch_off_means_never():
    rules.load(disable=['source_policy.wdpa_last_resort'])
    assert not rules.wdpa_last_resort_ok() and Registry().last_resort_for('US-FL') == []
    t, _ = rule_g.tier_g('A State Park', 'A State Park', True, layer=WD, last_resort=True)
    assert t == 'UNLIKELY'
    assert any('wdpa_last_resort' in c[0] for c in rules.changed())


def test_w10_rulings_for_the_four_parks():
    d = json.load(open(rules.HERE / 'registry' / 'rulings.json'))['parks']
    for ref in ('US-0896', 'US-6281', 'US-0658', 'US-1879'):
        assert 'W-10' in d[ref]['why'] and d[ref]['official_found'], ref
        assert all('wdpa' not in x['layer'].lower() for x in d[ref]['official_found'])
