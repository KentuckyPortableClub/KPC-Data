"""Offline unit tests on made-up shapes (no network). Run: python -m pytest -q"""
import json
import sys
from pathlib import Path

import pytest
from shapely.geometry import LineString, MultiPolygon, Point, Polygon, box

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import kpc_map_audit as A  # noqa: E402

LON, LAT = -84.5, 37.5
M = 1 / 111_320  # about 1 m in degrees of latitude


def square(lon, lat, side_m):
    d = side_m * M
    dx = d / 0.7934  # cos(37.5)
    return box(lon, lat, lon + dx, lat + d)


# ---- T1 pin
def test_t1_bands():
    assert A.t1_pin(0)["flag"] == "PASS"
    assert A.t1_pin(300)["flag"] == "NEAR"
    assert A.t1_pin(501)["flag"] == "OUTSIDE"
    assert A.t1_pin(10_001)["flag"] == "FAR"
    assert A.t1_pin(float("nan"))["flag"] == "NO OUTLINE"


def test_t1_distance_from_shape():
    g = square(LON, LAT, 1000)
    assert A.pin_distance_m(g, LON + 0.001, LAT + 0.001) == 0
    d = A.pin_distance_m(g, LON, LAT - 2000 * M)
    assert 1950 < d < 2050


# ---- T2 size
def test_t2_bands_and_acres():
    g = square(LON, LAT, 1000)          # 1 km2 = 247.1 acres
    ac = A.acres(g)
    assert 240 < ac < 255
    assert A.t2_size(ac, 247)["flag"] == "PASS"
    assert A.t2_size(ac, 100)["flag"] == "OFF"
    assert A.t2_size(ac, 40)["flag"] == "WAY OFF"
    assert A.t2_size(ac, 2000)["flag"] == "WAY OFF"
    assert A.t2_size(ac, None)["flag"] == "NO FIGURE"


# ---- T3 names
def test_t3_names():
    assert A.t3_name("Green River Lake State Park", ["Green River Lake SP"])["flag"] == "PASS"
    assert A.t3_name("J. W. Smith Memorial WMA", ["JW Smith Wildlife Management Area"])["flag"] == "PASS"
    assert A.t3_name("Horse Mill Branch WMA", ["Horsemill Branch Wildlife Management Area"])["flag"] == "PASS"
    assert A.t3_name("Lac Été Provincial Park", ["Lac Ete Park"])["flag"] == "PASS"
    assert A.t3_name("Pine Mountain State Resort Park", ["Kingdom Come State Park"])["flag"] == "MISMATCH"
    r = A.t3_name("Big Bone Lick State Historic Site", ["Big Bone State Park"])
    assert r["flag"] in ("WEAK", "MISMATCH")


def test_norm_tokens():
    assert A.norm_tokens("Mt. St. Helens") == ["mount", "saint", "helens"]
    assert A.norm_tokens("A. B. Chandler") == ["ab", "chandler"]


# ---- T4 kinds
def test_t4_conflicts():
    assert A.t4_kind("Kentucky Dam Village State Resort Park", "State Park", "Kentucky Dam WMA", "Wildlife Management Area")["flag"] == "CONFLICT"
    assert A.t4_kind("X National Forest", "National Forest", "X NF", "", "Proclamation")["flag"] == "CONFLICT"
    assert A.t4_kind("Cave Run Lake Recreation Area", "Recreation Area", "Cave Run Lake", "")["flag"] == "CONFLICT"
    assert A.t4_kind("C&O Canal Section 3", "", "Chesapeake and Ohio Canal", "")["flag"] == "CONFLICT"
    assert A.t4_kind("Carter Caves State Resort Park", "State Park", "Carter Caves State Park", "State Park")["flag"] == "PASS"
    assert A.t4_kind("Big Creek National Wildlife Area", "National Wildlife Area", "Big Creek", "National Wildlife Area")["flag"] == "PASS"


# ---- T5 shape health
def test_t5_health():
    good = square(LON, LAT, 500)
    assert A.t5_health([good], good)["flag"] == "PASS"
    bow = Polygon([(LON, LAT), (LON + 0.01, LAT + 0.01), (LON + 0.01, LAT), (LON, LAT + 0.01), (LON, LAT)])
    r = A.t5_health([bow], A.shapely.make_valid(bow))
    assert "SELF-INTERSECTION" in r["flags"]
    sliver = square(LON, LAT, 500).union(box(LON + 0.02, LAT, LON + 0.03, LAT + 5 * M))
    assert "SLIVERS" in A.t5_health([sliver], sliver)["flags"]
    outer = square(LON, LAT, 500)
    hole = square(LON + 100 * M, LAT + 100 * M, 5)
    holed = Polygon(outer.exterior.coords, [hole.exterior.coords])
    assert "TINY HOLES" in A.t5_health([holed], holed)["flags"]
    bits = MultiPolygon([square(LON + i * 0.02, LAT, 100) for i in range(60)])   # 60 pieces over ~100 km
    assert "SCATTERED" in A.t5_health([bits], bits)["flags"]
    assert A.t5_health([], None)["flag"] == "EMPTY"


# ---- T6 spill
def test_t6_spill():
    big = square(LON, LAT, 3000)
    inside = A.disc(LON + 1000 * M / 0.79, LAT + 1000 * M)
    others = [("US-0002", "Other Creek State Natural Area", inside), ("US-0003", "Far Away Park", A.disc(LON + 1, LAT + 1))]
    r = A.t6_spill("US-0001", "Big Woods WMA", big, others, set())
    assert r["flag"] == "SPILL" and r["parks"][0]["ref"] == "US-0002"
    assert A.t6_spill("US-0001", "Big Woods WMA", big, others, {frozenset(("US-0001", "US-0002"))})["flag"] == "PASS"
    same = [("US-0002", "Big Woods Wildlife Management Area", inside)]
    assert A.t6_spill("US-0001", "Big Woods WMA", big, same, set())["flag"] == "PASS"
    tree = A.STRtree([o[2] for o in others])
    assert A.t6_spill("US-0001", "Big Woods WMA", big, others, set(), tree)["flag"] == "SPILL"


# ---- T7 detail
def test_t7_detail():
    assert A.coord_step_m([1.123456, 2.123456], 0) < 1
    step4 = A.coord_step_m([8.1234, 46.1234], 46.5)
    assert 7 < step4 < 8.5
    assert A.t7_detail(None, 0.9, 40, world=False)["flag"] == "PASS"
    assert A.t7_detail(None, step4, 40, world=False)["flag"] == "TOO COARSE"
    assert A.t7_detail(None, step4, 40, world=True)["flag"] == "NOTE"
    r = A.t7_detail(5, 0.9, 40, world=False)
    assert r["flag"] == "PASS" and "3 and 5" in r["note"]
    assert A.t7_detail(None, 0, 0, world=False, live=True)["flag"] == "N/A"


# ---- T8 duplicates
def test_t8_duplicates():
    d = A.t8_duplicates({"US-1": ["padus#5", "padus#6"], "US-2": ["padus#6"], "US-3": ["padus#7"]})
    assert d == {"US-1": {"US-2": ["padus#6"]}, "US-2": {"US-1": ["padus#6"]}}


# ---- T9 age + score + why
def test_t9_and_score():
    assert A.t9_age("2020-01-01", "2026-10-30")["flag"] == "STALE CHECK"
    assert A.t9_age("2026-06-01", "2026-10-30")["flag"] == "PASS"
    assert A.t9_age("2026-10-31", "2026-10-30")["flag"] == "NOTE"
    assert A.t9_age(None, "2026-10-30")["flag"] == "CAN'T TELL"
    tests = {"T1": {"flag": "FAR", "metres": 20000}, "T2": {"flag": "OFF"}, "T3": {"flag": "PASS"},
             "T6": {"flag": "SPILL", "parks": [{"ref": "US-9", "name": "Y", "share": 0.5}]}}
    assert A.score_of(tests) == 5 + 1 + 3
    assert A.why_of("US-1", tests).startswith("FAR: POTA's pin is 20.0 km")
    assert A.score_of({"T1": {"flag": "PASS"}}) == 0
    assert A.why_of("US-1", {"T1": {"flag": "PASS"}}) == "All tests pass."


# ---- a whole made-up world area, offline, end to end
def test_world_area_end_to_end(tmp_path, monkeypatch):
    data = tmp_path / "data"
    (data / "world-bounds" / "ZZ").mkdir(parents=True)
    ring = [[8.1, 46.1], [8.2, 46.1], [8.2, 46.2], [8.1, 46.2], [8.1, 46.1]]
    (data / "world-bounds" / "ZZ" / "0.json").write_text(json.dumps({"ZZ-0001": {"n": "Testberg", "r": [ring], "s": "made up"}}))
    pota = {"ZZ-0001": {"name": "Testberg Nature Park", "lat": 46.15, "lon": 8.15, "locs": ["ZZ-AA"]}}
    monkeypatch.setattr(A.Audit, "pota_parks", lambda self, area: dict(pota))
    out = tmp_path / "audit"
    rc = A.main(["--areas", "ZZ", "--data", str(data), "--out", str(out), "--cache", str(tmp_path / "c"), "--offline"])
    assert rc == 0
    rec = json.loads((out / "ZZ.json").read_text())["parks"][0]
    assert rec["tests"]["T1"]["flag"] == "PASS"
    assert rec["tests"]["T7"]["flag"] == "NOTE"   # 1 decimal: very coarse, world = report only
    q = json.loads((out / "questions.json").read_text())
    assert all(x["answer"] is None and x["picture"] == "" for x in q["questions"])
    assert (out / "worst.csv").exists() and (out / "summary.md").exists()


def test_bad_input_exit_2(tmp_path):
    assert A.main(["--areas", "US-KY", "--data", str(tmp_path / "nope")]) == 2
    assert A.main(["--areas", "not an area", "--data", str(tmp_path)]) == 2


def test_esri_island_in_lake_is_valid():
    # big park (clockwise) with a lake (hole), an island in the lake, and a pond on the island
    cw = lambda x0, y0, x1, y1: [[x0, y0], [x0, y1], [x1, y1], [x1, y0], [x0, y0]]
    ccw = lambda x0, y0, x1, y1: [[x0, y0], [x1, y0], [x1, y1], [x0, y1], [x0, y0]]
    g = {"rings": [cw(0, 0, 10, 10), ccw(2, 2, 8, 8), cw(3, 3, 7, 7), ccw(4, 4, 6, 6)]}
    s = A.esri_to_shape(g)
    assert s.is_valid and abs(s.area - (100 - 36 + 16 - 4)) < 1e-9


def test_coord_step_empty():
    assert A.coord_step_m([], 40) == 0.0
