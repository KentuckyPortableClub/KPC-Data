"""Offline tests for KPC 11 on made-up shapes. Run: python -m pytest tests"""
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)

import kpc_boundary_watch as kw          # noqa: E402
from fakeweb import FakeWeb, square      # noqa: E402

URL = "https://example.test/arcgis/rest/services/Test/Parks/MapServer/0"
FOLDER = "https://example.test/arcgis/rest/services/Test"
LON, LAT, SIZE = -85.0, 37.0, 0.01        # about 250 acres


def make_data(tmp_path):
    d = tmp_path / "club"
    (d / "us-key").mkdir(parents=True)
    (d / "fers").mkdir()
    (d / "us-key" / "layers.json").write_text(json.dumps({"tst": [URL + "/query", "NAME", "Test Agency (made up)"]}))
    parks = {f"US-990{i}": {"n": f"Test Park {i}", "t": "SP", "g": "official",
                            "m": [[f"tst{i}", f"Test Park {i}", 250, "test"]]} for i in range(1, 7)}
    (d / "us-key" / "US-ZZ.json").write_text(json.dumps({"parks": parks}))
    (d / "fers" / "US-ZZ.json").write_text(json.dumps({"spots": [
        {"id": "K4TEST-1", "refs": ["US-9901", "US-9906"], "kind": "2-fer", "status": "live"},
        {"id": "K4TEST-2", "refs": ["US-9901", "US-9902"], "kind": "2-fer", "status": "dropped 2026"}]}))
    return d


def make_web():
    w = FakeWeb(kw.SourceProblem)
    lyr = w.add_layer(URL, "NAME", edit=1000)
    for i in range(1, 7):
        lyr["records"][i] = {"name": f"Test Park {i}", "rings": [square(LON + i * 0.1, LAT, SIZE)]}
    w.folders[FOLDER] = [{"name": "Test/Parks", "type": "MapServer"},
                         {"name": "Test/Parks_2026", "type": "MapServer"}]
    return w


def run(tmp_path, web, monkeypatch, *extra):
    monkeypatch.setattr(kw, "Polite", lambda *a, **k: web)
    d = tmp_path / "club"
    out = tmp_path / "watch"
    code = kw.main(["--data", str(d), "--out", str(out), "--areas", "US-ZZ", *extra])
    rows = {}
    run_dir = out / ".run" / "US-ZZ" / "_result.json"
    if run_dir.exists():
        rows = {r["ref"]: r for r in json.loads(run_dir.read_text())}
    return code, rows, out


# ---------------- small pieces ----------------
def test_round_rel_keeps_0_1_percent():
    assert kw.round_rel(12345.678) == 12350.0
    assert kw.round_rel(0) == 0.0


def test_compare_fp_rules():
    base = {"a": 1000.0, "bb": [-85, 37, -84.99, 37.01], "v": 5}
    assert kw.compare_fp(base, dict(base))[0] == "SAME"
    assert kw.compare_fp(base, {**base, "a": 1030.0})[0] == "GREW"        # 3 %
    assert kw.compare_fp(base, {**base, "a": 1004.0})[0] == "SAME"        # 0.4 %, 4 acres
    assert kw.compare_fp(base, {**base, "a": 994.0})[0] == "SHRANK"       # 6 acres
    moved = {**base, "bb": [-84.999, 37, -84.989, 37.01]}                 # about 90 m east
    assert kw.compare_fp(base, moved)[0] == "MOVED"


def test_kept_share():
    from shapely.geometry import Polygon
    old = Polygon(square(LON, LAT, SIZE))
    assert kw.kept_share(old, old) == 100.0
    half = Polygon(square(LON, LAT, SIZE, dx=SIZE / 2))
    assert 45 < kw.kept_share(old, half) < 56


# ---------------- whole runs ----------------
def test_first_run_then_same(tmp_path, monkeypatch):
    make_data(tmp_path)
    web = make_web()
    code, rows, out = run(tmp_path, web, monkeypatch)
    assert code == 0
    assert {r["verdict"] for r in rows.values()} == {"FIRST LOOK"}
    assert (out / "state.json").exists() and (out / "summary.md").exists()
    st = json.loads((out / "state.json").read_text())
    assert "geom" not in json.dumps(st["parks"])            # numbers only
    before = web.requests_made
    code, rows, out = run(tmp_path, web, monkeypatch)
    assert code == 0
    assert {r["verdict"] for r in rows.values()} == {"SAME"}
    # the layer was not edited: only the layer page and a count were read
    assert web.requests_made - before == 2


def test_changes_are_found(tmp_path, monkeypatch):
    make_data(tmp_path)
    web = make_web()
    run(tmp_path, web, monkeypatch)
    lyr = web.layers[URL]
    lyr["edit"] = 2000
    lyr["records"][1]["rings"] = [square(LON + 0.1, LAT, SIZE * 1.2)]           # grew
    lyr["records"][2]["rings"] = [square(LON + 0.2, LAT, SIZE * 0.8)]           # shrank
    lyr["records"][3]["rings"] = [square(LON + 0.3, LAT, SIZE, dx=0.002)]       # moved ~180 m
    del lyr["records"][4]                                                       # gone
    lyr["records"][5]["name"] = "Test Park Five State Natural Area"             # renamed
    code, rows, out = run(tmp_path, web, monkeypatch)
    assert code == 0
    assert rows["US-9901"]["verdict"] == "GREW"
    assert rows["US-9902"]["verdict"] == "SHRANK"
    assert rows["US-9903"]["verdict"] == "MOVED"
    assert rows["US-9904"]["verdict"] == "RECORD GONE"
    assert rows["US-9905"]["verdict"] == "RENAMED"
    assert rows["US-9906"]["verdict"] == "SAME"
    # changed parks carry the 2-fer rows and the 'still inside' share
    r1 = rows["US-9901"]
    assert {f["id"] for f in r1["fers"]} == {"K4TEST-1", "K4TEST-2"}
    assert [f["live"] for f in sorted(r1["fers"], key=lambda f: f["id"])] == [True, False]
    assert r1["old_still_inside_pct"] == 100.0
    assert rows["US-9902"]["old_still_inside_pct"] < 70
    ch = json.loads(next(out.glob("changes-*.json")).read_text())
    assert {c["ref"] for c in ch["changed"]} == {"US-9901", "US-9902", "US-9903", "US-9904", "US-9905"}


def test_layer_moved_gives_leads(tmp_path, monkeypatch):
    make_data(tmp_path)
    web = make_web()
    run(tmp_path, web, monkeypatch)
    web.layers[URL]["status"] = "moved"
    web.add_layer(FOLDER.replace("/Test", "/Test/Parks_2026/MapServer/0"), "NAME")
    code, rows, out = run(tmp_path, web, monkeypatch)
    assert code == 0
    assert {r["verdict"] for r in rows.values()} == {"LAYER MOVED"}
    leads = rows["US-9901"]["leads"]
    assert leads and leads[0]["url"].endswith("Test/Parks_2026/MapServer/0")
    assert leads[0]["has_name_field"] is True


def test_source_down_is_not_a_change(tmp_path, monkeypatch):
    make_data(tmp_path)
    web = make_web()
    run(tmp_path, web, monkeypatch)
    web.layers[URL]["status"] = "down"
    code, rows, out = run(tmp_path, web, monkeypatch)
    assert code == 0
    assert {r["verdict"] for r in rows.values()} == {"SOURCE DOWN"}
    web.layers[URL]["status"] = "ok"            # next week it answers again: fingerprints were kept
    code, rows, out = run(tmp_path, web, monkeypatch)
    assert {r["verdict"] for r in rows.values()} == {"SAME"}


def test_bad_input_exit_2(tmp_path, monkeypatch):
    d = make_data(tmp_path)
    web = make_web()
    monkeypatch.setattr(kw, "Polite", lambda *a, **k: web)
    assert kw.main(["--data", str(d), "--out", str(tmp_path / "w"), "--areas", "US-QQ"]) == 2
    assert kw.main(["--data", str(tmp_path / "nope"), "--out", str(tmp_path / "w")]) == 2
    # never writes into the club's live folders
    assert kw.main(["--data", str(d), "--out", str(d / "us-key" / "watch"), "--areas", "US-ZZ"]) == 2


def test_out_of_time_then_resume(tmp_path, monkeypatch):
    make_data(tmp_path)
    web = make_web()
    code, rows, out = run(tmp_path, web, monkeypatch, "--max-minutes", "0.001")
    assert code == 3
    code, rows, out = run(tmp_path, web, monkeypatch, "--resume")
    assert code == 0
    assert {r["verdict"] for r in rows.values()} == {"FIRST LOOK"}


def test_renumbered_record_gets_a_lead(tmp_path, monkeypatch):
    make_data(tmp_path)
    web = make_web()
    run(tmp_path, web, monkeypatch)
    lyr = web.layers[URL]
    lyr["edit"] = 3000
    lyr["records"][40] = lyr["records"].pop(4)          # same park, new record number
    code, rows, out = run(tmp_path, web, monkeypatch)
    r = rows["US-9904"]
    assert r["verdict"] == "RECORD GONE"
    assert r["leads"][0]["new_record_ids"] == [40]
    assert "probably renumbered" in r["why"]


def test_unknown_layer_is_cant_tell_not_source_down(tmp_path, monkeypatch):
    d = make_data(tmp_path)
    key = json.loads((d / "us-key" / "US-ZZ.json").read_text())
    key["parks"]["US-9907"] = {"n": "No Layer Park", "g": "official", "m": [["qqq1", "No Layer Park", 10, "test"]]}
    key["parks"]["US-9901"]["m"].append(["qqq2", "Extra piece", 10, "test"])
    (d / "us-key" / "US-ZZ.json").write_text(json.dumps(key))
    web = make_web()
    code, rows, out = run(tmp_path, web, monkeypatch)
    assert code == 0
    assert rows["US-9907"]["verdict"] == "CAN'T TELL"
    assert "no layer address" in rows["US-9907"]["why"]
    # a park with one readable and one unreadable record is still fingerprinted, with a note
    assert rows["US-9901"]["verdict"] == "FIRST LOOK" and "could not be read" in rows["US-9901"]["why"]
