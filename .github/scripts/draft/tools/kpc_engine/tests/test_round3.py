"""Club answers, round 3 (ANSWERS_round3.md, Nov 1): WDPA rejection, forestry != NNR, rulings, EU CDDA approximate, repo config."""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from core import rule_g as G, registry, config
from plugins.outline import apply_ruling

WDPA_COPY = 'https://services5.arcgis.com/Mj0hjvkNtV7NRhA7/arcgis/rest/services/WDPA_v0/FeatureServer/1'


def test_wdpa_copy_never_matches_us0658_us1879():       # Timucuan / US-1879 matched only through a WDPA copy
    assert G.tier_g('Timucuan Ecological and Historic Preserve', 'Timucuan Ecological and Historic', True, layer=WDPA_COPY)[0] == 'UNLIKELY'


def test_wdpa_cited_in_description_licence_or_fields_is_rejected():
    assert G.cites_wdpa({'name': 'Protected Areas', 'copyrightText': 'UNEP-WCMC and IUCN (2025), Protected Planet: The World Database on Protected Areas'})
    assert G.cites_wdpa({'name': 'Areas', 'description': 'Source: protectedplanet.net download'})
    assert G.cites_wdpa({'name': 'Areas', 'licenseInfo': 'WDPA terms of use'})
    assert G.cites_wdpa({'name': 'Areas', 'fields': [{'name': 'WDPAID'}, {'name': 'NAME'}]})
    assert G.cites_wdpa({'url': 'https://x/arcgis/rest/services/Protected_Areas_WDPA_MMA/FeatureServer/0'})
    assert not G.cites_wdpa({'name': 'Florida State Parks', 'description': 'FL DEP Division of Recreation and Parks', 'fields': [{'name': 'SITE_NAME'}]})


def test_registry_holds_no_wdpa_source_and_no_wdpa_yes_row():
    R = registry.Registry()
    assert not any(G.cites_wdpa(s) for s in R.sources)
    assert not any(G.cites_wdpa(str(v)) for v in R.yes_rows.values())


def test_rulings_pin_only_us0658_us1879_and_hold_gb0889():
    R = registry.Registry()
    for ref in ('US-0658', 'US-1879'):
        rl = R.ruling(ref); assert rl['ruling'] == 'pin only' and rl['tag'].startswith('official layer exists (W-10)')   # round 4: W-10
        out = apply_ruling(rl, {'ref': ref, 'status': 'not found', 'whynot': {'tag': 'no-layer'}})
        assert out['status'] == 'pin only' and out['whynot']['tag'] == rl['tag']
        new = apply_ruling(rl, {'ref': ref, 'status': 'found', 'band': 'STRONG'})      # keep looking: a new find is only a candidate
        assert new['status'] == 'candidate' and new['band'] == 'WEAK'
    held = apply_ruling(R.ruling('GB-0889'), {'ref': 'GB-0889', 'status': 'found', 'layer': 'PACK-GB-forest-180', 'record_name': 'Glen Nant'})
    assert held['status'] == 'held' and held['held_find']['record_name'] == 'Glen Nant'


def test_glen_nant_forestry_record_is_wrong_kind_for_nnr():   # GB-0889
    forest = 'https://services6.arcgis.com/JF5BD4Y14a3LnPcJ/arcgis/rest/services/Forest_Blocks_WFS/FeatureServer/0 PACK-GB-forest-180 Forest_Blocks'
    t, why = G.tier_g('Glen Nant National Nature Reserve', 'Glen Nant', True, layer=forest)
    assert t == 'UNLIKELY' and 'forestry' in why
    assert G.tier_g('Glen Nant National Nature Reserve', 'Glen Nant', True, layer='NatureScot Nature Reserves (NNR)')[0] == 'SURE'
    assert G.layer_kind_ok('Daniel Boone National Forest', 'USFS forestry administrative boundaries')[0]       # a forest may match a forestry layer


def test_eu_cdda_stays_approximate_and_ranks_after_national():
    R = registry.Registry()
    eu = [s for s in R.sources if registry.EU_COMPILATION.search(s.get('url') or '')]
    assert eu and all(s['grade'] == 'approximate' for s in eu)
    for area in ('DE', 'AT', 'IE'):
        out = R.for_area(area)
        grades = [s.get('grade', 'official') for s in out]
        if 'approximate' in grades and 'official' in grades:
            assert grades.index('official') < grades.index('approximate')      # the national layer is asked first and replaces it


def test_repo_config():
    assert config.KPC_DATA_REPO == 'KentuckyPortableClub/KPC-Data' and config.RESULTS_BRANCH == 'tools-out'
    assert config.KPC_LINKS_REPO == 'KentuckyPortableClub/KPC-Links' and config.KPC_LINKS_REPO in config.READ_ONLY_REPOS
    assert config.can_write('KentuckyPortableClub/KPC-Data', 'tools-out')
    assert not config.can_write('KentuckyPortableClub/KPC-Data', 'main') and not config.can_write('KentuckyPortableClub/KPC-Links', 'tools-out')


def test_out_inside_links_refused(tmp_path):
    import kpc_engine
    assert kpc_engine.main(['export', '--links', str(tmp_path), '--out', str(tmp_path / 'x')]) == 2
