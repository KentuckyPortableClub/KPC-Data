"""The club's switches (config/rules.json + --enable / --disable / --scope / --set). Round 3 steering, Nov 1 2026."""
import json, pytest
from conftest import FIX
from core import rules, scope, rule_g, grading


@pytest.fixture(autouse=True)
def _clean():
    rules.reset(); yield; rules.reset()


AREAS = ['US-KY', 'US-TN', 'US-FL', 'CA-ON', 'GB', 'CH', 'DE', 'JP', '']
OLD_KY, OLD_NA, OLD_WORLD = {'hours', 'fees', 'closures'}, {'parking', 'camping', 'trail'}, {'outline', 'docs', 'map', 'page'}


def _old_allowed(kind, area):                         # the rule before the switches existed (core/scope.py, round 2)
    if kind in OLD_KY: return area == 'US-KY'
    if kind in OLD_NA: return area.startswith(('US-', 'CA-'))
    return kind in OLD_WORLD


def test_defaults_are_todays_rules_exactly():
    assert rules.changed() == []
    for k in sorted(OLD_KY | OLD_NA | OLD_WORLD | {'2fers', 'nonsense'}):
        for a in AREAS: assert scope.allowed(k, a) == _old_allowed(k, a), (k, a)
    assert rules.load() and rules.changed() == []
    for name in ('hours_rules.separate_marina_scuba', 'hours_rules.reject_fragments', 'hours_rules.hunting_hours_apart',
                 'source_policy.wdpa_guard', 'source_policy.two_fers_never_auto', 'source_policy.eu_compilation_approximate',
                 'source_policy.parcels_approximate', 'source_policy.unofficial_docs_kept_apart', 'checks.containers'):
        assert rules.on(name), name
    assert all(rules.on(f'source_policy.never_use.{n}') for n in rules.NEVER_USE)
    assert rule_g.size_band(1.4) == 'PASS' and rule_g.size_band(4) == 'OFF' and rule_g.size_band(6) == 'WAY OFF'
    assert rule_g.parcel_hold(0.19) and not rule_g.parcel_hold(1.0) and rule_g.parcel_hold(2.1)
    assert 'Rules: all club defaults' in rules.banner_md()


def test_default_hours_parsing_same_as_before():
    cases = {'Marina hours 7 AM - 7 PM': False, '10 AM - 4 PM': False, 'Hunting hours 5 AM - 8 PM, open seasonally': False,
             'Park open daily 6 AM - 10 PM': True}
    for line, ok in cases.items(): assert rule_g.hours_line_ok(line, 'hours')[0] is ok, line


def test_expand_hours_to_tennessee():
    rules.load(scope=['hours=US-KY,US-TN'])
    assert scope.allowed('hours', 'US-TN') and scope.allowed('hours', 'US-KY')
    assert not scope.allowed('fees', 'US-TN') and not scope.allowed('hours', 'US-FL')
    assert any(n == 'plugins.hours.areas' for n, _, _ in rules.changed())
    assert 'RULES CHANGED' in rules.banner_text() and 'WARNING' in rules.banner_md()


def test_expand_hours_gaps_on_a_tennessee_park():
    from core import gaps

    class Club:
        outline_status = lambda s, a, r: 'official'; has_map = has_page = lambda s, a, r: True
        access_points = campgrounds = has_trail_line = lambda s, a, r: True
        docs_row = lambda s, a, r: {}; hours_row = lambda s, a, r: {}; closures_checked = lambda s, a: {}
    p = {'ref': 'US-1234', 'n': 'Some State Park', 't': 'State Park'}
    assert gaps.park_gaps(Club(), 'US-TN', p)[0] == []
    rules.load(scope=['hours=US-KY,US-TN'])
    assert gaps.park_gaps(Club(), 'US-TN', p)[0] == ['hours']


def test_turn_off_a_plugin():
    rules.load(disable=['closures'])
    assert not scope.allowed('closures', 'US-KY') and scope.allowed('hours', 'US-KY')
    rules.load(disable=['docs'])
    assert not scope.allowed('map', 'GB') and not scope.allowed('page', 'US-KY')


def test_disable_a_parsing_rule():
    rules.load(disable=['hours_rules.reject_fragments'])
    assert rule_g.hours_line_ok('10 AM - 4 PM', 'hours')[0]
    assert not rule_g.hours_line_ok('Marina hours 7 AM - 7 PM', 'hours')[0]         # the other rules stay on
    rules.load(disable=['hours_rules.separate_marina_scuba,hours_rules.hunting_hours_apart'])
    assert rule_g.hours_line_ok('Marina hours 7 AM - 7 PM', 'hours')[0]
    assert rule_g.hours_line_ok('Hunting hours 5 AM - 8 PM, open seasonally', 'hours')[0]


def test_grader_numbers_switchable():
    rules.load(set_=['grader.size_pass_max=2', 'grader.rg12_m=300'])
    assert rule_g.size_band(1.8) == 'PASS' and rules.num('rg12_m') == 300


def _row(url, **kw):
    r = {'ref': 'US-0001', 'area': 'US-FL', 'status': 'found', 'grade': 'official', 'band': 'STRONG', 'url': url}
    r.update(kw); return r


def test_wdpa_guard_off_stamps_rows_non_official():
    lay = 'https://services.arcgis.com/x/arcgis/rest/services/WDPA_v0/FeatureServer/1'
    assert rule_g.tier_g({}, {}, True, layer=lay)[0] == 'UNLIKELY'
    r = _row(lay); assert rules.stamp_rows('outline', [r]) == 0 and 'source_policy' not in r      # guard on: nothing to stamp
    rules.load(disable=['source_policy.wdpa_guard'])
    assert 'wdpa_guard' in rules.banner_text()
    r = _row(lay); assert rules.stamp_rows('outline', [r]) == 1
    assert r['source_policy'] == 'non-official: WDPA' and r['grade'] == 'approx' and r['g'] == 'approx'
    assert r['band'] == 'WEAK' and r['status'] == 'candidate'


def test_never_use_switch_off_stamps_and_on_rejects():
    u = 'https://www.google.com/maps/d/viewer?mid=abc'
    assert rules.forbidden(u) == 'google' and rule_g.tier_g({}, {}, True, layer=u)[0] == 'UNLIKELY'
    assert any('not official' in x for x in rule_g.doc_problems({'map': u}))
    rules.load(disable=['source_policy.never_use.google'])
    assert rules.forbidden(u) == '' and rules.forbidden('https://overpass-api.de/x') == 'openstreetmap'
    r = _row(u); rules.stamp_rows('docs', [r]); assert r['source_policy'] == 'non-official: google' and r['grade'] == 'approx'
    rules.load(disable=['source_policy.never_use'])                  # the whole list
    assert all(not rules.on(f'source_policy.never_use.{n}') for n in rules.NEVER_USE)


def test_eu_and_parcels_and_docs_switches_stamp():
    rules.load(disable=['source_policy.eu_compilation_approximate', 'source_policy.parcels_approximate'])
    r = _row('https://bio.discomap.eea.europa.eu/arcgis/rest/services/ProtectedSites/CDDA_Dyna_WM/MapServer/0')
    rules.stamp_rows('outline', [r]); assert 'EU compilation' in r['source_policy'] and r['grade'] == 'approx'
    r = _row('https://gis.example.gov/parcels/0', parcel_record=12)
    rules.stamp_rows('outline', [r]); assert 'parcel' in r['source_policy']
    rules.load(disable=['source_policy.unofficial_docs_kept_apart'])
    r = _row('', page='https://www.someblog.com/park', map='https://www.someblog.com/map.pdf')
    rules.stamp_rows('docs', [r]); assert 'unofficial doc' in r['source_policy']


def test_two_fers_switch_keeps_waiting_room():
    assert 'auto' not in grading.bar('2fers').lower() or 'never' in grading.bar('2fers').lower()
    rules.load(disable=['source_policy.two_fers_never_auto'])
    assert 'waiting room' in grading.bar('2fers')


def test_locked_rules_cannot_be_switched(tmp_path):
    for n in rules.LOCKED:
        with pytest.raises(rules.RulesError): rules.load(disable=[n])
    for bad in ({'honest_user_agent': False}, {'source_policy': {'verify_tls': False}}, {'checks': {'bypass_cloudflare': True}},
                {'politeness': {'user_agent': 'Mozilla/5.0'}}, {'source_policy': {'use_found_tokens': True}}):
        p = tmp_path / 'r.json'; p.write_text(json.dumps(bad))
        with pytest.raises(rules.RulesError): rules.load(str(p))
    with pytest.raises(rules.RulesError): rules.load(disable=['source_policy.no_such_switch'])
    with pytest.raises(rules.RulesError): rules.load(scope=['nosuchplugin=US-KY'])


def test_cli_logs_active_config(tmp_path):
    import kpc_engine
    rc = kpc_engine.main(['run', '--data', str(FIX / 'data'), '--links', str(FIX / 'links'), '--pota', str(FIX / 'pota'), '--out', str(tmp_path),
                          '--areas', 'US-TN,US-KY', '--offline', '--workers', '2', '--steps', 'L0', '--scope', 'hours=US-KY,US-TN',
                          '--disable', 'closures'])
    assert rc == 0
    a = json.load(open(tmp_path / 'active-config.json'))
    assert a['scope']['hours'] == ['US-KY', 'US-TN'] and a['scope']['closures'] == 'OFF'
    assert {c['switch'] for c in a['changed_from_default']} == {'plugins.hours.areas', 'plugins.closures.enabled'}
    if (tmp_path / 'grades.md').exists(): assert 'WARNING' in (tmp_path / 'grades.md').read_text()
    assert 'RULES CHANGED' in (tmp_path / 'board.md').read_text() or 'WARNING' in (tmp_path / 'board.md').read_text()
    g = json.load(open(tmp_path / 'gaps.json'))
    assert 'closures' not in json.dumps(g['parks'] if isinstance(g, dict) and 'parks' in g else g).replace('"closures_', '')
