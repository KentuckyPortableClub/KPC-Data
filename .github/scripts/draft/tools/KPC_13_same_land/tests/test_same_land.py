"""Offline tests for KPC 13 on made-up shapes. Run: python -m pytest tests"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)

import kpc_same_land as ks              # noqa: E402
from fakeweb import FakeWeb, square     # noqa: E402

URL = "https://example.test/arcgis/rest/services/Test/Parks/MapServer/0"
LON, LAT, S = -85.0, 37.0, 0.01


# ---------------- the five tests ----------------
def test_s1_same_record():
    assert ks.test_s1(["PAD-US:5"], ["PAD-US:5"])[0] == "SAME RECORD"
    assert ks.test_s1(["PAD-US:5", "PAD-US:6"], ["PAD-US:5"])[0] == "SHARES A RECORD"
    assert ks.test_s1(["PAD-US:5"], ["PAD-US:6"])[0] is None
    assert ks.test_s1([], ["PAD-US:6"])[0] is None


def test_s2_shape_classes():
    assert ks.test_s2(98, 100, 100)[0] == "SAME SHAPE"
    assert ks.test_s2(96, 100, 115)[0] == "SAME SHAPE"           # 0.96 / 0.83
    assert ks.test_s2(96, 100, 160)[0] == "ONE INSIDE THE OTHER"  # 0.96 / 0.60
    assert ks.test_s2(10, 10, 1000)[0] == "SMALL ONE INSIDE"
    assert ks.test_s2(50, 100, 100)[0] == "PART OVERLAP"


def test_s3_name_family():
    assert ks.test_s3("Fort Donelson National Battlefield", "Fort Donelson NB")[0]
    assert ks.test_s3("Carter Caves State Resort Park", "Carter Caves")[0]          # one inside the other
    assert not ks.test_s3("Carter Caves State Resort Park", "Bat Cave State Nature Preserve")[0]
    assert not ks.test_s3("Jefferson National Forest", "Daniel Boone National Forest")[0]


def test_s4_pins():
    near = ks.test_s4((37.0, -85.0), (37.001, -85.0))      # about 111 m
    far = ks.test_s4((37.0, -85.0), (37.01, -85.0))        # about 1.1 km
    assert near[0] is True and 100 < near[1] < 120
    assert far[0] is False
    assert ks.test_s4(None, (37.0, -85.0)) == (None, None)


def test_s5_agency():
    assert ks.test_s5(["National Park Service"], ["National Park Service", "U.S. Forest Service"]) == "same"
    assert ks.test_s5(["National Park Service"], ["U.S. Forest Service"]) == "different"
    assert ks.test_s5([], ["U.S. Forest Service"]) == "unknown"
    assert ks.canon_agency("NPS") == ks.canon_agency("National Park Service")


def test_decide_rules():
    assert ks.decide("SAME RECORD", "PART OVERLAP", False, False, "unknown")[0] == ks.SAME
    assert ks.decide(None, "SAME SHAPE", True, False, "same")[0] == ks.SAME
    assert ks.decide(None, "SAME SHAPE", False, True, "same")[0] == ks.SAME
    assert ks.decide(None, "SAME SHAPE", True, True, "different")[0] == ks.CHECK
    assert ks.decide(None, "PART OVERLAP", True, True, "different")[0] == ks.CHECK
    assert ks.decide(None, "ONE INSIDE THE OTHER", True, True, "same")[0] == ks.CHECK      # S3 + S4 without S2
    assert ks.decide(None, "ONE INSIDE THE OTHER", True, False, "same")[0] == ks.NOT_SAME
    assert ks.decide(None, "SMALL ONE INSIDE", False, False, "different")[0] == ks.NOT_SAME
    assert ks.decide(None, "SAME SHAPE", False, False, "same")[0] == ks.NOT_SAME
    # an outline that is not graded official never gets more than CHECK
    assert ks.decide(None, "SAME SHAPE", True, True, "same", both_official=False)[0] == ks.CHECK


# ---------------- a whole run ----------------
def make_data(tmp_path):
    d = tmp_path / "club"
    for sub in ("us-key", "fers", "parkinfo"):
        (d / sub).mkdir(parents=True)
    (d / "us-key" / "layers.json").write_text(json.dumps({"tst": [URL + "/query", "NAME", "Test Agency (made up)"]}))
    P = lambda n, ids, g="official": {"n": n, "t": "", "g": g, "m": [[i, n, 100, "test"] for i in ids]}
    parks = {
        "US-9901": P("Fort Test National Battlefield", ["tst1"]),           # same record as 9902
        "US-9902": P("Fort Test (battlefield tract)", ["tst1"]),
        "US-9903": P("Big Woods Wildlife Management Area", ["tst3"]),      # same shape + name, same agency
        "US-9904": P("Big Woods WMA", ["tst4"]),
        "US-9905": P("Carter Test State Resort Park", ["tst5"]),           # holds two small preserves
        "US-9906": P("Bat Test State Nature Preserve", ["tst6"]),
        "US-9907": P("Big River National Wildlife Refuge", ["tst7"]),      # same shape, another agency
        "US-9908": P("Big River State Forest", ["tst8"]),
        "US-9909": P("Pin Only Park", []),
    }
    (d / "us-key" / "US-ZZ.json").write_text(json.dumps({"parks": parks}))
    # layers.json does not say which field holds the agency: tell the tool with --sources
    (tmp_path / "sources.json").write_text(json.dumps({"tst": {"agency_field": "MANAGER"}}))
    pins = {"US-9901": (37.005, -84.995), "US-9902": (37.0051, -84.995), "US-9903": (37.005, -84.795),
            "US-9904": (37.005, -84.795), "US-9905": (37.005, -84.595), "US-9906": (37.001, -84.599),
            "US-9907": (37.005, -84.395), "US-9908": (37.02, -84.37)}
    (d / "parkinfo" / "US-ZZ.json").write_text(json.dumps(
        {"parks": {r: ["n", "", "", "", "", la, lo] for r, (la, lo) in pins.items()}}))
    (d / "fers" / "US-ZZ.json").write_text(json.dumps({"spots": [
        {"id": "K4TEST-1", "refs": ["US-9901", "US-9902"], "kind": "same land", "status": "live"},
        {"id": "K4TEST-2", "refs": ["US-9905", "US-9906"], "kind": "2-fer", "status": "live"}]}))
    return d


def make_web():
    w = FakeWeb(ks.SourceProblem)
    lyr = w.add_layer(URL, "NAME", agency_field="MANAGER")
    R = lyr["records"]
    R[1] = {"name": "Fort Test", "agency": "NPS", "rings": [square(LON, LAT, S)]}
    R[3] = {"name": "Big Woods WMA", "agency": "TWRA", "rings": [square(LON + 0.2, LAT, S)]}
    R[4] = {"name": "Big Woods", "agency": "TWRA", "rings": [square(LON + 0.2, LAT, S * 0.99)]}
    R[5] = {"name": "Carter Test", "agency": "Kentucky State Parks", "rings": [square(LON + 0.4, LAT, S)]}
    R[6] = {"name": "Bat Test", "agency": "OKNP", "rings": [square(LON + 0.4, LAT, S * 0.2)]}
    R[7] = {"name": "Big River NWR", "agency": "FWS", "rings": [square(LON + 0.6, LAT, S)]}
    R[8] = {"name": "Big River SF", "agency": "Division of Forestry", "rings": [square(LON + 0.6, LAT, S * 0.99)]}
    return w


def run(tmp_path, monkeypatch, web, *extra):
    monkeypatch.setattr(ks, "Polite", lambda *a, **k: web)
    out = tmp_path / "sameland"
    code = ks.main(["--data", str(tmp_path / "club"), "--out", str(out), "--areas", "US-ZZ",
                    "--sources", str(tmp_path / "sources.json"), *extra])
    res = json.loads((out / "US-ZZ.json").read_text()) if (out / "US-ZZ.json").exists() else None
    return code, res, out


def test_whole_run(tmp_path, monkeypatch):
    make_data(tmp_path)
    code, res, out = run(tmp_path, monkeypatch, make_web())
    assert code == 0
    v = {r["id"]: r["verdict"] for r in res["pairs"]}
    assert v["US-9901+US-9902"] == ks.SAME
    assert v["US-9903+US-9904"] == ks.SAME
    assert v["US-9905+US-9906"] == ks.NOT_SAME
    assert v["US-9907+US-9908"] == ks.CHECK
    assert len(v) == 4                       # no pair between far-apart parks; pin-only park left alone
    club = res["club_same_land_rows"]
    assert club == [{"fer_id": "K4TEST-1", "refs": ["US-9901", "US-9902"], "live": True, "tool_verdict": ks.SAME}]
    q = json.loads((out / "questions.json").read_text())
    assert {x["id"] for x in q["questions"]} == {"US-9901+US-9902", "US-9903+US-9904", "US-9907+US-9908"}
    assert all(x["answer"] is None for x in q["questions"])
    assert "top candidates" in (out / "summary.md").read_text()


def test_answers_are_kept(tmp_path, monkeypatch):
    make_data(tmp_path)
    code, res, out = run(tmp_path, monkeypatch, make_web())
    qp = out / "questions.json"
    q = json.loads(qp.read_text())
    q["questions"][0]["answer"] = "YES"
    q["questions"][0]["checked_by"] = "K4TEST"
    qp.write_text(json.dumps(q))
    run(tmp_path, monkeypatch, make_web())
    q2 = {x["id"]: x for x in json.loads(qp.read_text())["questions"]}
    assert q2[q["questions"][0]["id"]]["answer"] == "YES"
    assert q2[q["questions"][0]["id"]]["checked_by"] == "K4TEST"


def test_source_down_uses_nothing_and_says_so(tmp_path, monkeypatch):
    make_data(tmp_path)
    web = make_web()
    web.layers[URL]["status"] = "down"
    code, res, out = run(tmp_path, monkeypatch, web)
    assert code == 0
    assert res["pairs"] == [] and len(res["left_out"]) == 8


def test_exit_codes(tmp_path, monkeypatch):
    d = make_data(tmp_path)
    web = make_web()
    monkeypatch.setattr(ks, "Polite", lambda *a, **k: web)
    assert ks.main(["--data", str(d), "--out", str(tmp_path / "o"), "--areas", "US-QQ"]) == 2
    assert ks.main(["--data", str(d), "--out", str(d / "fers" / "x"), "--areas", "US-ZZ"]) == 2
    assert ks.main(["--data", str(d), "--out", str(tmp_path / "o"), "--areas", "US-ZZ", "--max-minutes", "0.001"]) == 3
    assert ks.main(["--data", str(d), "--out", str(tmp_path / "o"), "--areas", "US-ZZ", "--resume"]) == 0
