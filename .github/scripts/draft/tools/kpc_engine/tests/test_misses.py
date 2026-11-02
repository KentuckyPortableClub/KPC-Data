"""Chat 11's 18 real misses (GRADING_BAR_chat11.md, Nov 1) as regression tests. Every one must pass."""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from shapely.geometry import box
from core import rule_g as G


def test_monument_blm_rma_not_monument_gs():          # US-10476: 1-acre record of another kind
    t, why = G.tier_g('Monument BLM RMA', 'Monument GS', True, size_ratio=1 / 30000)
    assert t == 'UNLIKELY'


def test_big_south_fork_same_land_copy_merged():       # US-0686: a 30,138-acre copy inside the main outline
    main, copy = box(0, 0, 10, 10), box(1, 1, 9, 9)
    assert G.same_land(main, copy)
    assert not G.same_land(box(0, 0, 1, 1), box(5, 5, 6, 6))


def test_yatesville_state_park_is_not_the_wma():       # SP != WMA
    assert not G.kinds_match('Yatesville Lake State Park', 'Yatesville Lake WMA')
    assert G.tier_g('Yatesville Lake State Park', 'Yatesville Lake Wildlife Management Area', True)[0] == 'UNLIKELY'


def test_little_south_fork_sna_not_the_wild_river():
    assert G.tier_g('Little South Fork State Nature Preserve', 'Little South Fork Wild River', True)[0] == 'UNLIKELY'


def test_salato_parcel_held_over_2x():                  # US-10172: 921 ac vs 229.85 ac
    assert G.parcel_hold(921 / 229.85)
    assert G.size_band(921 / 229.85) == 'OFF'


def test_parcels_inside_another_pota_park_never_taken():   # US-3118 Halfmoon Pond in Bomoseen SP; US-8388 in CT River Greenway SP
    bomoseen = box(0, 0, 10, 10)
    assert G.absorbs_other_park(box(2, 2, 3, 3), [bomoseen])
    assert not G.absorbs_other_park(box(20, 20, 21, 21), [bomoseen])


def test_hiwassee_cutoff_held():                       # US-10389: 9.8x size
    assert G.parcel_hold(9.8) and G.size_band(9.8) == 'WAY OFF'
    assert G.tier_g('Hiwassee Dam', 'Hiwassee Dam', True, size_ratio=9.8)[0] == 'UNLIKELY'


def test_management_district_is_a_container():         # Oxford Slough WMD vs WPA
    assert G.tier_g('Oxford Slough Waterfowl Production Area', 'Southeast Idaho Wetland Management District', True)[0] == 'UNLIKELY'
    assert G.tier_g('Oxford Slough WPA', 'Oxford Slough Wetland Management District', True)[0] == 'UNLIKELY'


def test_other_unit_of_same_refuge_system():           # Halfbreed Lake vs Grass Lake NWR
    assert G.tier_g('Halfbreed Lake National Wildlife Refuge', 'Grass Lake National Wildlife Refuge', True)[0] == 'UNLIKELY'


def test_one_record_under_several_pins_is_a_container():
    rows = [{'ref': 'US-1', 'layer': 'L', 'record': 7}, {'ref': 'US-2', 'layer': 'L', 'record': 7}, {'ref': 'US-3', 'layer': 'L', 'record': 8}]
    assert G.containers(rows) == {('L', '7'): ['US-1', 'US-2']}
    assert G.tier_g('A Park', 'A Park', True, container=True)[0] == 'UNLIKELY'


def test_renamed_alberta_park_is_accepted():           # Prairie Coulees NA = Hargrave Coulees NA since 2020
    assert G.tier_g('Prairie Coulees Natural Area', 'Hargrave Coulees Natural Area', True)[0] == 'SURE'


def test_indigenous_names():                           # Colony Farm = ƛ̓éxətəm; Mount Douglas = Pkols
    assert G.name_level('Colony Farm Regional Park', 'ƛ̓éxətəm Regional Park') == 'equal'
    assert G.name_level('Mount Douglas Park', 'PKOLS') == 'equal'


def test_same_person_different_place():                # Denys Fort NHS (Shippagan) vs Nicholas Denys Site (Bathurst)
    assert G.tier_g('Denys Fort National Historic Site', 'Nicholas Denys Site', False, pin_m=60000)[0] == 'UNLIKELY'


def test_never_the_parent_parcel():                    # Green Gables: the pin's parcel = all of PEI National Park's
    assert G.tier_g('Green Gables Heritage Place', 'Prince Edward Island National Park', True, size_ratio=4000)[0] == 'UNLIKELY'
    assert G.parcel_hold(4000)


def test_mislabelled_layer_not_a_question():           # Lighthouse Park labelled 'Trails Park'
    assert G.tier_g('Lighthouse Park', 'Trails Park', True)[0] == 'UNLIKELY'


def test_fort_providence_pin_typo_never_moves():       # pin 111 km off: latitude 62 for 61
    t = G.pin_typo((62.33, -117.64), (61.35, -117.65))
    assert t and t['rule'] == 'R-G13' and 'latitude' in t['why'] and t['pin_moves'] is False and t['km'] > 100
    assert G.pin_typo((61.35, -117.65), (61.351, -117.651)) is None


def test_cedar_creek_size_tolerance():                 # 789 vs 796 acres is not "off"
    assert G.size_band(789 / 796) == 'PASS'


def test_pin_on_the_road_r_g12():                      # Ganaraska / ABCA / SNC / RRCA: 7-107 m outside
    for m in (7, 107, 150):
        assert G.tier_g('Ganaraska Forest', 'Ganaraska Forest', False, pin_m=m)[0] == 'SURE'
    assert G.tier_g('Ganaraska Forest', 'Ganaraska Forest', False, pin_m=400)[0] == 'UNLIKELY'


def test_alberta_name_field_read_from_layer():         # PARK_NAME gave nothing: the field is NAME
    assert G.pick_name_field([{'name': 'OBJECTID'}, {'name': 'NAME'}, {'name': 'TYPE'}], 'PARK_NAME') == 'NAME'
    assert G.pick_name_field(['PARK_NAME', 'NAME'], 'PARK_NAME') == 'PARK_NAME'


def test_blm_surface_manager_layer_never_matched():    # BLM_Natl_SMA
    url = 'https://gis.blm.gov/arcgis/rest/services/lands/BLM_Natl_SMA_Cached_without_PriUnk/MapServer/1'
    assert G.tier_g('Red Rock Canyon NCA', 'Bureau of Land Management', True, layer=url)[0] == 'UNLIKELY'


def test_line_park_vs_polygon():
    assert G.tier_g('Dawkins Line Rail Trail', 'Dawkins Line Rail Trail', True, rec_line=False)[0] == 'UNLIKELY'
    assert G.tier_g('Dawkins Line Rail Trail', 'Dawkins Line Rail Trail', True, rec_line=True)[0] == 'SURE'


def test_other_bars():
    assert G.point_problems([37.1, 85.2, 'Lot A (KSP)'], 'US-KY') == ['west longitude written as positive']
    assert G.point_problems([37.1, -85.2, 'KY 80'], 'US-KY')
    assert not G.camp_feature_ok('Picnic Shelter 3') and not G.camp_feature_ok('Boat Ramp')
    assert G.hours_line_ok('Marina hours: 8 AM - 6 PM')[0] is False
    assert G.hours_line_ok('10 AM - 4 PM')[0] is False
    assert G.hours_line_ok('Open seasonally for deer hunting season')[0] is False
    assert G.hours_line_ok('The park is open daily from 7 AM to 10 PM.')[0] is True
    assert G.doc_problems({'map': 'https://parks.ky.gov/x/logo.png'})
    assert G.doc_problems({'page': 'https://en.wikipedia.org/wiki/X'})


def test_graders_apply_the_bars():
    from core import grading
    pk = [{'ref': 'US-1', 'area': 'US-KY', 'status': 'found', 'features': [{'lat': 37.0, 'lon': 85.0, 'name': 'Lot', 'm': 10}]}]
    assert grading.report('parking', pk)['verdict'] == 'FAIL'
    sh = [{'ref': r, 'area': 'US-KY', 'status': 'found', 'features': [{'lat': 37.0, 'lon': -85.0, 'name': 'Lot', 'm': 10}]} for r in ('US-1', 'US-2')]
    assert any('duplicate facilities' in f for f in grading.report('parking', sh)['fails'])
    assert not any('shared' in f for f in grading.report('parking', sh)['fails'])
    hr = [{'ref': 'US-1', 'area': 'US-KY', 'status': 'found', 'hours': 'Marina hours: 7 AM - 7 PM', 'url': 'https://parks.ky.gov/x'}]
    assert grading.report('hours', hr)['verdict'] == 'FAIL'
    ol = [{'ref': 'US-1', 'area': 'US-KY', 'status': 'candidate', 'rule_g': 'UNLIKELY', 'url': 'https://kygisserver.ky.gov/x', 'whynot': {'tag': 'x'}}]
    assert grading.report('outline', ol)['verdict'] == 'FAIL'
    cp = [{'ref': 'US-1', 'area': 'US-KY', 'status': 'found', 'features': [{'lat': 37.0, 'lon': -85.0, 'name': 'Picnic Shelter 2', 'm': 10}]}]
    assert grading.report('camping', cp)['verdict'] == 'FAIL'
    assert 'Never automatic' in grading.BARS['2fers']


def test_shared_facility_kept_with_nearest_pin():
    rows = [{'ref': 'US-1287', 'status': 'found', 'features': [{'lat': 37.07379, 'lon': -87.66351, 'm': 300}]},
            {'ref': 'US-4692', 'status': 'found', 'features': [{'lat': 37.07379, 'lon': -87.66351, 'm': 2500}]}]
    assert G.resolve_shared(rows) == 1 and rows[1]['status'] == 'not found' and G.shared_points(rows) == {}
