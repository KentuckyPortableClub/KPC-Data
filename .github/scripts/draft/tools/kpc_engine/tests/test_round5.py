"""Round 5 (Nov 1): master-workbook import (read only), retry list, seeded work order, HDX = WDPA (W-10), game reserves,
US-6281 description-field fix, club trail rulings (official tie for a named piece; state mapping agency compilations)."""
import json, pathlib
import pytest
from core import rules, rule_g, priority
from core.registry import Registry, HERE as REG

ENGINE = pathlib.Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def _fresh():
    rules.reset(); yield; rules.reset()


def feat(**k):
    f = {'lat': 37.0, 'lon': -85.0, 'name': 'Dawkins Line Rail Trail', 'agency': 'KyGovMaps', 'source': 'US-KY-trail-KYTC_Multi_Use_Paths-0', 'pin_line_m': 50.0}
    f.update(k); return f


# ---------------------------------------------------------------- (a) master workbook import
def test_master_import_is_read_only_and_counted():
    d = json.load(open(REG / 'master_nov1.json'))
    assert d['workbook']['sha256'] and d['counts']['_total']['new'] > 0 and d['counts']['_total']['duplicate (ours)'] > 0
    src = (ENGINE / 'registry' / 'import_master.py').read_text()
    assert 'read_only=True' in src and '.save(' not in src and 'merge.py' not in src.replace('world_keys/merge.py or', '')


def test_master_sources_rank_after_ours_and_keep_wb_status():
    R = Registry()
    s = [x for x in R.sources if x.get('id', '').startswith('WB-')]
    assert s and all('wb_status' in x for x in s)
    assert any('wb' in x for x in R.sources if not x.get('id', '').startswith('WB-'))          # duplicates: ours keeps winning
    fl = R.for_area('US-WA')
    ours = [i for i, x in enumerate(fl) if not x.get('id', '').startswith('WB-')]
    mine = [i for i, x in enumerate(fl) if x.get('id', '').startswith('WB-') and x.get('grade') == 'official']
    if ours and mine: assert min(ours) < min(mine)


def test_master_never_imports_never_use_or_wdpa_as_ordinary():
    d = json.load(open(REG / 'master_nov1.json'))
    for s in d['sources']:
        assert not rules.forbidden(' '.join(str(s.get(k) or '') for k in ('url', 'agency', 'layer')))


def test_state_host_listed_as_country_gets_its_state():
    d = json.load(open(REG / 'master_nov1.json'))
    s = [x for x in d['sources'] if 'wdfw.wa.gov' in x['url']]
    assert s and all(x['area'] == 'US-WA' for x in s)


# ---------------------------------------------------------------- (b) retry list
def test_retry_list_tagged_and_enp_is_person_download():
    R = Registry()
    assert len(R.retry) == 24 and all(i['tag'] == 'retry from GitHub network' for i in R.retry)
    enp = [i for i in R.retry if i['id'] == 'RETRY-ES-enp'][0]
    assert enp['kind'] == 'person downloads' and enp['automatic'] is False
    for i in R.retry:
        if i['kind'] in ('needs sign-in', 'person', 'person downloads'): assert not i['automatic']
    assert R.retry_for('TR-0001')[0]['cc'] == 'TR'


# ---------------------------------------------------------------- (c) seeded work order
def test_seeds_reorder_inside_club_class_only():
    assert priority.seed_of({'area': 'US-UT', 'park': 'X Trail'}, 'trail')[1] == 'T-UT'
    assert priority.seed_of({'area': 'US-KY', 'park': 'X Trail'}, 'trail')[1] is None
    assert priority.seed_of({'area': 'CA-ON', 'ref': 'CA-5993', 'park': 'Burgess'}, 'trail')[1] == 'T-ON-retry'
    assert priority.seed_of({'area': 'FR', 'park': 'X'}, 'trail')[1] == 'W-trails'
    assert priority.seed_of({'area': 'GB', 'park': 'X'}, 'trail')[1] is None                    # GB trails were searched
    g = priority.order_groups([('ky', [{'area': 'US-KY', 'park': 'Green River Lake State Park'}]),
                               ('ut', [{'area': 'US-UT', 'park': 'Goblin Valley State Park'}])], 'outline')
    assert g[0][0] == 'ut'
    g = priority.order_groups([('blm', [{'area': 'US-NV', 'park': 'Red Rock Canyon National Conservation Area'}]),
                               ('kytrails', [{'area': 'US-KY', 'park': 'Dawkins Line Rail Trail'}])], 'outline')
    assert g[0][0] == 'kytrails'                                                                # the club class order still wins


# ---------------------------------------------------------------- (e) rules
def test_hdx_copies_follow_w10():
    u = 'https://data.humdata.org/dataset/kenya-protected-areas'
    assert rules.forbidden(u) == 'WDPA' and rules.forbidden(u, allow_wdpa=True) == ''
    assert rule_g.cites_wdpa(u)
    assert not rules.forbidden('https://data.humdata.org/dataset/kenya-roads')


def test_game_reserve_is_not_a_pota_park():
    t, why = rule_g.tier_g('Kruger National Park', 'Sabi Sand Game Reserve', True, 0, False, False, 1.0, False, 'x')
    assert t == 'UNLIKELY' and 'game reserve' in why
    t, _ = rule_g.tier_g('Kruger National Park', 'Kruger National Park', True, 0, False, False, 1.0, False, 'Hunting reserves (cotos de caza)')
    assert t == 'UNLIKELY'
    rules.load(disable=['checks.game_reserve_not_park'])
    t, _ = rule_g.tier_g('Kruger National Park', 'Sabi Sand Game Reserve', True, 0, False, False, 1.0, False, 'x')
    assert 'game reserve' not in _


# ---------------------------------------------------------------- (f) US-6281
def test_description_sentence_is_not_a_name():
    from plugins.outline import _best_field
    a = {'MANAME': 'Jonathan Dickinson State Park', 'DESC1': "This park includes sand pine scrub, river swamp on the Loxahatchee River, "
                                                                 "Florida's only federally-designated Wild and Scenic River."}
    s, k, v = _best_field('Loxahatchee River National Wild and Scenic River', a)
    assert k != 'DESC1'


def test_florida_lists_the_wsr_segment_layer_first_for_its_url():
    R = Registry()
    fl = R.for_area('US-FL')
    w = [s for s in fl if 'WildScenicRiverSegments' in s['url']]
    assert w and w[0]['id'] == 'US-FL-USFS-WSR-segments' and w[0]['name_field'] == 'wsr_river_name'


# ---------------------------------------------------------------- steering: club trail rulings
def test_named_piece_needs_an_official_tie_never_location():
    f = feat(name='Clifty Creek', agency='Kentucky Department of Parks', pin_line_m=5.0)
    assert not rule_g.trail_bar(f, 'Sheltowee Trace', 'Kentucky Department of Parks')[0]          # location alone: no
    f2 = dict(f, system_names=['Sheltowee Trace National Recreation Trail'])
    ok, _ = rule_g.trail_bar(f2, 'Sheltowee Trace', 'Kentucky Department of Parks')
    assert ok and 'trail-system field' in f2['name_tie']
    f3 = dict(f, agency_page_lists='https://www.fs.usda.gov/example-page')
    assert rule_g.trail_bar(f3, 'Sheltowee Trace', 'Kentucky Department of Parks')[0]


def test_state_mapping_compilation_counts_until_the_agency_line_turns_up():
    rows = [{'ref': 'US-1253', 'park': 'Dawkins Line Rail Trail State Park', 'agency_group': 'parks.ky.gov', 'status': 'found', 'features': [feat()]}]
    rule_g.apply_trail_bar(rows)
    assert rows[0]['trail_bar'] == 'PASS' and 'state mapping agency' in rows[0]['basis']
    own = feat(agency='parks.ky.gov', source='US-KY-parks-trails', pin_line_m=500.0)          # the agency's own line (fails on distance)
    rows = [{'ref': 'US-1253', 'park': 'Dawkins Line Rail Trail State Park', 'agency_group': 'parks.ky.gov', 'status': 'found', 'features': [feat(), own]}]
    rule_g.apply_trail_bar(rows)
    assert rows[0]['trail_bar'] != 'PASS' and "agency's own line wins" in rows[0]['features'][-1]['trail_bar'] + rows[0]['features'][0]['trail_bar']
    rules.load(disable=['source_policy.state_mapping_compilations'])
    rows = [{'ref': 'US-1253', 'park': 'Dawkins Line Rail Trail State Park', 'agency_group': 'parks.ky.gov', 'status': 'found', 'features': [feat()]}]
    rule_g.apply_trail_bar(rows)
    assert rows[0]['trail_bar'] != 'PASS'


def test_stream_compilation_only_for_river_parks():
    s = feat(name='Beaver Creek', source='US-KY-river-NHD_Subset_of_Blueline_Streams_in_Kentuc-0')
    assert not rule_g.state_compilation(s, 'Beaver Creek Wildlife Management Area')
    assert rule_g.state_compilation(dict(s, name='Bad Branch'), 'Bad Branch National Wild and Scenic River')
