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


# ---- Nov 2 (mapping agent): impossible POTA pins
def test_pin_ok():
    assert A.pin_ok(37.5, -84.5)
    assert not A.pin_ok(92.595, -57.056)                    # POTA CA-2395 Churchill WMA (Nov 2): the CA-MB run stopped on it
    assert not A.pin_ok(45, 181)
    assert not A.pin_ok(None, 3) and not A.pin_ok("x", 3) and not A.pin_ok(float("nan"), 3)


def test_grade_park_impossible_pin_is_flagged_not_a_crash():
    P = A.Audit.blank("CA-2395", "CA-MB")
    P["geom"] = square(LON, LAT, 1000)
    tests = A.grade_park(P, {"name": "Churchill WMA", "lat": 92.595, "lon": -57.056}, {}, False)
    assert tests["T1"]["flag"] == "CAN'T TELL" and tests["T1"]["bad_pin"] == [92.595, -57.056]


# ---- Nov 2 bot fixes (Quality + Mapping reviews): blank pins, no crash, merged outputs, a real start-over
import json  # noqa: E402

import pytest  # noqa: E402


def test_zero_zero_pin_is_refused_and_never_measured():
    assert not A.pin_ok(0, 0) and not A.pin_ok("0", "0.0")
    assert A.pin_ok(0, 10) and A.pin_ok(10, 0)                  # only the exact 0, 0 blank
    assert A.pin_distance_m(square(LON, LAT, 1000), -57.056, 92.595) != A.pin_distance_m(square(LON, LAT, 1000), -57.056, 92.595)  # nan
    with pytest.raises(ValueError):
        A.local_proj(-57.056, 92.595)


def _rec(ref, score, repair=None):
    t5 = {"flag": "SLIVERS", "flags": ["SLIVERS"]}
    if repair:
        t5["repair"] = repair
    return {"ref": ref, "name": ref, "records": [{"id": "1"}], "tests": {"T5": t5}, "score": score, "why": "x", "status": "graded"}


def test_write_outputs_twice_with_an_ok_repair_and_all_areas(tmp_path):
    rp = {"ok": True, "area_change_pct": 0.1, "holes": 1, "pieces": 0, "geojson": {"type": "Polygon", "coordinates": []}}
    res = {"US-AA": [_rec("US-0001", 3, rp)], "US-BB": [_rec("US-0002", 0)]}
    A.write_outputs(tmp_path, res, {"US-AA": "2026-11-01", "US-BB": "2026-11-02"})
    A.write_outputs(tmp_path, res, {"US-AA": "2026-11-01", "US-BB": "2026-11-02"})   # was a KeyError on 'geojson'
    q = json.loads((tmp_path / "questions.json").read_text())
    assert set(q["areas"]) == {"US-AA", "US-BB"} and q["areas"]["US-BB"]["asked"] == 0 and q["areas"]["US-AA"]["built"] == "2026-11-01"
    assert [x["area"] for x in q["questions"]] == ["US-AA"]
    assert "geojson" not in json.dumps(json.loads((tmp_path / "US-AA.json").read_text()))
    assert json.loads((tmp_path / "repairs" / "US-AA.json").read_text())["parks"]["US-0001"]["geojson"]["type"] == "Polygon"
    assert res["US-AA"][0]["tests"]["T5"]["repair"]["geojson"]                       # the results in memory are not changed


class _Dummy:
    def __init__(self, *a, **k):
        pass


def _main(tmp_path, monkeypatch, run_area, *extra):
    monkeypatch.setattr(A, "Audit", _Dummy)
    monkeypatch.setattr(A, "run_area", run_area)
    (tmp_path / "data").mkdir(exist_ok=True)
    return A.main(["--areas", "US-AA", "US-BB", "US-CC", "--data", str(tmp_path / "data"), "--out", str(tmp_path / "out"),
                   "--cache", str(tmp_path / "cache"), "--offline", *extra])


def test_one_area_crash_does_not_stop_the_others_and_ends_red(tmp_path, monkeypatch):
    seen = []

    def ra(audit, ar, acres, deadline, prog):
        seen.append(ar)
        if ar == "US-BB":
            raise Exception("aeqd: Invalid value for lat_0")   # like pyproj's CRSError on CA-MB
        return [_rec(ar.replace("US-", "US-00"), 3)], True
    assert _main(tmp_path, monkeypatch, ra, "--resume") == 4
    assert seen == ["US-AA", "US-BB", "US-CC"]
    st = json.loads((tmp_path / "cache" / "audit-state.json").read_text())
    assert set(st["done"]) == {"US-AA", "US-CC"} and "US-BB" in st["failed"]
    q = json.loads((tmp_path / "out" / "questions.json").read_text())
    assert set(q["areas"]) == {"US-AA", "US-CC"}                    # every finished area, not the last one only
    seen.clear()
    assert _main(tmp_path, monkeypatch, ra, "--resume") == 4        # a chained job skips the failed area and redoes nothing
    assert seen == []
    seen.clear()
    assert _main(tmp_path, monkeypatch, ra, "--resume", "--fresh") == 4   # a real start over
    assert seen == ["US-AA", "US-BB", "US-CC"]


def test_time_out_then_resume_then_old_rules_start_fresh(tmp_path, monkeypatch):
    calls, timed_out = [], []

    def ra(audit, ar, acres, deadline, prog):
        calls.append(ar)
        if ar == "US-BB" and not timed_out:
            timed_out.append(1)
            return None, False
        return [_rec(ar.replace("US-", "US-00"), 0)], True
    assert _main(tmp_path, monkeypatch, ra, "--resume") == 3
    assert _main(tmp_path, monkeypatch, ra, "--resume") == 0
    assert calls == ["US-AA", "US-BB", "US-BB", "US-CC"]
    f = tmp_path / "cache" / "audit-state.json"
    st = json.loads(f.read_text()); st["rules"] = "older"; f.write_text(json.dumps(st))
    calls.clear()
    assert _main(tmp_path, monkeypatch, ra, "--resume") == 0
    assert calls == ["US-AA", "US-BB", "US-CC"]                     # progress from older audit rules is never resumed
    (tmp_path / "out" / "US-AA.json").unlink()
    calls.clear()
    assert _main(tmp_path, monkeypatch, ra, "--resume") == 0
    assert calls == ["US-AA"]                                       # a 'done' mark without its results file is audited again
