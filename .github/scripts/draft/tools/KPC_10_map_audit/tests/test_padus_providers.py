"""Offline unit tests (no network). Run: python -m pytest -q"""
import sys
from pathlib import Path

from shapely.geometry import box

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import kpc_map_audit as A  # noqa: E402

LON, LAT = -84.5, 37.5
M = 1 / 111_320


def square(lon, lat, side_m):
    d = side_m * M
    return box(lon, lat, lon + d / 0.7934, lat + d)


# ---- Nov 2 (mapping agent): PAD-US data providers (the doubled official acres)
def test_provider_acres_same_refuge_from_two_providers():
    # A refuge held by FWS PAD-US 3.0 AND FWS PAD-US 4.0 with acres more than 1% apart (Cache River, Felsenthal, St. Marks):
    # the Nov 2 'within 1%' skip does not catch these (copies within 1%, like Arctic NWR's, it already does)
    rows = [("padus", 100_000, "FWS_PADUS3_0Fee"), ("padus", 110_000, "FWS_PADUS4_0Fee")]
    assert A.best_acres(rows) == 210_000                    # added: the land counted twice
    assert A.provider_acres(rows) == 110_000                # each provider once: the biggest
    assert A.provider_acres([("padus", 100), ("padus", 250)]) is None   # no provider given: no second figure


def test_provider_acres_pieces_of_one_provider_still_add():
    rows = [("padus", 100, "NJDEP"), ("padus", 250, "NJDEP"), ("padus", 340, "TNC")]
    assert A.provider_acres(rows) == 350
    assert A.best_acres(rows) == 690


def test_t2_range_between_provider_and_all_providers():
    t = A.t2_size(19_600_000, 39_300_000, "x", 19_660_000)
    assert t["flag"] == "PASS" and t["official_acres_low"] == 19_660_000 and "provider" in t["note"]
    t = A.t2_size(5_000, 39_300, "x", 19_650)               # below the low figure: measured against it (3.9x)
    assert t["flag"] == "OFF" and 3.8 < t["times"] < 4.0
    assert A.t2_size(30_000, 39_300, "x", 19_650)["flag"] == "PASS"   # inside the range
    assert A.t2_size(100, 300, "x", None)["flag"] == "OFF"            # no provider figure: as before
    assert A.t2_size(100, 300, "x", 299.5)["flag"] == "OFF"           # low within 1% of the total: ignored
    assert "official_acres_low" not in A.t2_size(100, 300, "x", 299.5)


def test_nested_preserve_inside_the_park_counts_once():
    # batch 1b (Quality, US-2753 South Mountains SP): the state layer's park (21,342 ac) and its nature preserve (15,079 ac),
    # which lies inside the park, are one piece of land: the official figure is the park's, not the two added
    from shapely.geometry import box
    park, preserve = box(0, 0, 10, 10), box(1, 1, 8, 8)
    rows = [("sgnc", 21342.0, ""), ("sgnc", 15079.0, "")]
    drop = A.nested_same_source(rows, [park, preserve])
    assert drop == {1}
    assert A.best_acres([r for i, r in enumerate(rows) if i not in drop]) == 21342.0


def test_nested_rule_leaves_copies_and_other_sources_alone():
    from shapely.geometry import box
    g = box(0, 0, 10, 10)
    # near-equal copies (the provider range handles those) and another source's record are never dropped here
    assert A.nested_same_source([("main", 100.0, "FWS_PADUS3_0"), ("main", 99.0, "FWS_PADUS3_0")], [g, g]) == set()
    assert A.nested_same_source([("sgnc", 100.0, ""), ("main", 50.0, "")], [g, box(1, 1, 5, 5)]) == set()
    # a smaller record only half inside the bigger one is other land: kept
    assert A.nested_same_source([("sgnc", 100.0, ""), ("sgnc", 50.0, "")], [g, box(5, 0, 15, 10)]) == set()
    assert A.nested_same_source([("sgnc", 100.0, ""), ("sgnc", 50.0, "")], [g, None]) == set()


def test_conservation_group_copies_count_and_are_labeled():
    # Brandon Nov 2 (via Super Head Bot): TNC and Ducks Unlimited copies in PAD-US count, labeled with their source
    rows = [("main", 100.0, "TNC_PADUS2_0_SA2015_Public_gdb"), ("main", 98.0, "DU_PADUS2_1_NCED"), ("main", 99.0, "FWS_PADUS4_0Fee")]
    labs = A.provider_labels(rows)
    assert labs == ["The Nature Conservancy (PAD-US source TNC_PADUS2_0_SA2015_Public_gdb)", "Ducks Unlimited (PAD-US source DU_PADUS2_1_NCED)"]
    assert A.provider_acres(rows) == 100.0   # counted, not thrown out
    assert A.provider_labels([("main", 5.0, "FWS_PADUS4_0Fee"), ("main", 5.0, "")]) == []
