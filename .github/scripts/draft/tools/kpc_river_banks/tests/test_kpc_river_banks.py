"""Offline tests on made-up shapes. No network: every source is faked."""
import csv
import json
import sys
from pathlib import Path

import pytest
from shapely.geometry import LineString, Point, box, shape

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import kpc_river_banks as K  # noqa: E402

LAT, LON = 48.77, -123.75          # a made-up spot (K4TEST country, BC-like)
P = K.Proj(LON, LAT)
X0, Y0 = P.fwd.transform(LON, LAT)


def m2ll(g):
    """Made-up shape in metres around (X0, Y0) -> lon/lat."""
    return P.to_ll(_shift(g))


def _shift(g):
    import shapely
    return shapely.transform(g, lambda xy: xy + [X0, Y0])


def ll2m(g):
    import shapely
    return shapely.transform(P.to_m(g), lambda xy: xy - [X0, Y0])


# A straight river 100 m wide running west-east, 4 km long, centre line y = 0.
RIVER = box(-2000, -50, 2000, 50)
CENTRE = LineString([(-2000, 0), (2000, 0)])
POND = box(-300, 120, -250, 170)          # unnamed pond 70 m from the river edge, within 200 m of the line
FAR_POND = box(0, 700, 50, 750)           # unnamed pond far away
SIDE_ARM = box(500, 50, 560, 140)         # unnamed side channel that touches the river


def stretch(**kw):
    st = {"id": "K4TEST-0001@river@48.770,-123.750", "refs": ["K4TEST-0001"], "river": "Test River",
          "center": [LAT, LON], "bbox": list(m2ll(box(-500, -100, 500, 100)).bounds)}
    st.update(kw)
    return st


def win_for(st):
    w, s, e, n = K.window_for(st, None)
    return P.to_m(box(w, s, e, n)).envelope.buffer(K.PAD_M, join_style="mitre")


def found(polys, lines=(), date="2026-10-31"):
    return K.Found([K.Water(m2ll(g), list(n)) for g, n in polys],
                   [K.Water(m2ll(g), list(n)) for g, n in lines], date)


# ---------------------------------------------------------------- names

def test_names_lake_is_not_river():
    assert not K.names_match(["Cowichan River"], ["Cowichan Lake"])
    assert K.names_match(["Cowichan River"], ["Cowichan River"])


def test_names_accents_and_little_words():
    assert K.names_match(["Rivière Jacques-Cartier"], ["Riviere Jacques-Cartier "])
    assert K.names_match(["la Loire"], ["Loire"])
    assert not K.names_match(["Rivière Jacques-Cartier"], ["Rivière Jacques-Cartier Nord-Ouest"])


def test_split_names_bilingual_and_null():
    assert K.split_names("Aare | L'Aar") == ["Aare", "L'Aar"]
    assert K.names_match(["Aare"], K.split_names("Aare | L'Aar"))
    assert K.split_names("<Nul>") == []
    assert K.split_names(None) == []


# ---------------------------------------------------------------- the band is on the EDGE

def test_band_is_on_waters_edge_not_centre():
    st = stretch()
    det = K.build_bank(st, found([(RIVER, ["Test River"])]), None, P, win_for(st))
    band = det["band_m"]
    edge_pt = P.to_m(m2ll(Point(0, 50)))          # on the north bank
    bank_out = P.to_m(m2ll(Point(0, 50 + 25)))    # 25 m onto land: inside 100 ft of the edge
    bank_far = P.to_m(m2ll(Point(0, 50 + 35)))    # 35 m onto land: outside
    centre = P.to_m(m2ll(Point(0, 0)))            # mid-river, 50 m from each edge: outside
    assert band.contains(edge_pt) and band.contains(bank_out)
    assert not band.contains(bank_far)
    assert not band.contains(centre)
    # a centre-line rule would have wrongly left the bank point out: 75 m from the centre line
    assert P.to_m(m2ll(CENTRE)).distance(bank_out) > K.BAND_M


def test_band_width_both_sides_of_edge():
    st = stretch()
    det = K.build_bank(st, found([(RIVER, ["Test River"])]), None, P, win_for(st))
    b = ll2m(P.to_ll(det["band_m"]))
    # cut across the river at x = 0: band covers y in [-80.48,-19.52] and [19.52,80.48]
    cut = b.intersection(LineString([(0, -200), (0, 200)]))
    assert abs(cut.length - 4 * K.BAND_M) < 1.0


def test_water_clipped_to_window_and_edges_not_invented_at_cut():
    st = stretch()
    win = win_for(st)
    det = K.build_bank(st, found([(RIVER, ["Test River"])]), None, P, win)
    assert det["water_m"].within(win.buffer(0.01))
    # the window cut across the river is not a bank: mid-river at the window edge is not in the band
    east = ll2m(P.to_ll(win)).bounds[2]
    assert not ll2m(P.to_ll(det["band_m"])).contains(Point(east - 5, 0))


# ---------------------------------------------------------------- choosing polygons

def test_named_other_water_left_out():
    st = stretch()
    f = found([(RIVER, ["Test River"]), (box(-100, 60, 100, 200), ["Test Lake"])])
    det = K.build_bank(st, f, None, P, win_for(st))
    assert det["polygons_kept"] == 1
    assert det["named_other_water_left_out"] == ["Test Lake"]


def test_pond_guard_keeps_side_arm_drops_pond():
    st = stretch()
    f = found([(RIVER, ["Test River"]), (POND, []), (SIDE_ARM, []), (FAR_POND, [])],
              lines=[(CENTRE, ["Test River"])])
    det = K.build_bank(st, f, None, P, win_for(st))
    assert det["polygons_kept"] == 2           # river + touching side arm
    assert det["unnamed_ponds_left_out"] == 1  # the near pond
    assert not det["water_m"].intersects(P.to_m(m2ll(POND)).buffer(-1))


def test_unnamed_river_polygon_found_by_trail_line_within_200m():
    st = stretch(river="")
    trail = m2ll(LineString([(-1500, 150), (1500, 150)]))   # paddle route drawn 150 m off (bad digitising)
    f = found([(RIVER, [])])
    det = K.build_bank(st, f, trail, P, win_for(st))
    assert det["polygons_kept"] == 1 and det["name_check_of_unnamed_water"] == "200 m only"
    trail_far = m2ll(LineString([(-1500, 300), (1500, 300)]))  # 250 m from the edge: too far
    det = K.build_bank(st, f, trail_far, P, win_for(st))
    assert det["polygons_kept"] == 0


def test_line_only_when_no_polygon(tmp_path):
    st = stretch(river="Test Creek")
    f = found([(RIVER, ["Big River"])], lines=[(LineString([(-900, 300), (900, 300)]), ["Test Creek"])])
    det = K.build_bank(st, f, None, P, win_for(st))
    r = K.finish(st["id"], st["refs"], st, K.SOURCES["bc_fwa"], f, det, P, tmp_path)
    assert r.status == K.STATUS_LINE
    gj = json.loads(next((tmp_path / "banks").glob("*.geojson")).read_text())
    assert [ft["properties"]["method"] for ft in gj["features"]] == ["line-only"]
    assert all(ft["geometry"]["type"].endswith("LineString") for ft in gj["features"])


def test_ok_geojson_properties(tmp_path):
    st = stretch()
    f = found([(RIVER, ["Test River"])])
    det = K.build_bank(st, f, None, P, win_for(st))
    r = K.finish(st["id"], st["refs"], st, K.SOURCES["bc_fwa"], f, det, P, tmp_path)
    assert r.status == K.STATUS_OK
    gj = json.loads(next((tmp_path / "banks").glob("*.geojson")).read_text())
    parts = {ft["properties"]["part"]: ft for ft in gj["features"]}
    assert set(parts) == {"water", "band_100ft"}
    for ft in gj["features"]:
        p = ft["properties"]
        assert p["method"] == "polygon" and p["read_date"] == "2026-10-31"
        assert p["source"] and p["licence"]
        assert shape(ft["geometry"]).is_valid
    assert r.why.count(".") >= 1 and "\n" not in r.why


# ---------------------------------------------------------------- input, window, parse_line

def test_window_from_centre_only():
    st = stretch()
    del st["bbox"]
    w, s, e, n = K.window_for(st, None)
    assert (w, s) == (LON, LAT) and (e, n) == (LON, LAT)


def test_window_refuses_swapped_bbox():
    with pytest.raises(ValueError):
        K.window_for(stretch(bbox=[48.9, -123.7, 48.7, -123.8]), None)


def test_parse_line_shapes(tmp_path):
    assert K.parse_line([[0, 0], [1, 1]]).length > 0
    assert K.parse_line({"type": "LineString", "coordinates": [[0, 0], [1, 0]]}).length == 1
    p = tmp_path / "trail.json"
    p.write_text(json.dumps({"type": "Feature", "properties": {"ref": "K4TEST-0001"},
                             "geometry": {"type": "MultiLineString", "coordinates": [[[0, 0], [0, 2]]]}}))
    assert K.parse_line("trail.json", tmp_path).length == 2


def test_load_stretches_errors(tmp_path):
    with pytest.raises(K.BadInput):
        K.load_stretches(tmp_path / "missing.json")
    bad = tmp_path / "bad.json"
    bad.write_text("{nope")
    with pytest.raises(K.BadInput):
        K.load_stretches(bad)
    dup = tmp_path / "dup.json"
    dup.write_text(json.dumps([{"id": "a"}, {"id": "a"}]))
    with pytest.raises(K.BadInput):
        K.load_stretches(dup)


def test_live_dir_guard(tmp_path):
    with pytest.raises(K.BadInput):
        K.check_out_dir(tmp_path / "fers")
    K.check_out_dir(tmp_path / "work")


def test_route():
    assert K.route("CA", "CA-BC")[0] == "bc_fwa"
    assert K.route("CA", "CA-AB")[0] == "ca_chn"
    assert K.route("CH", None) == ["ch_tlm"] and K.route("FR", None) == ["fr_bdtopo"]
    assert K.route("DE", None) == ["eu_hydro"] and K.route("NZ", None) == []


# ---------------------------------------------------------------- whole batch with faked sources

@pytest.fixture
def fake_world(monkeypatch):
    state = {"down": True}

    def fake_fetch(src, f, bbox, st):
        if st["river"] == "Down River" and state["down"]:
            raise K.SourceDown("HTTP 503 from example.test")
        return found([(RIVER, [st["river"]])])

    for s in K.SOURCES.values():
        monkeypatch.setattr(s, "fetch", fake_fetch)
    return state


def write_stretches(tmp_path, rows):
    p = tmp_path / "stretches.json"
    p.write_text(json.dumps(rows))
    return p


def test_batch_one_failure_does_not_stop(tmp_path, fake_world):
    rows = [stretch(id="ok1", prov="CA-BC", refs=["CA-9999"]),
            stretch(id="down1", prov="CA-BC", refs=["CA-9999"], river="Down River"),
            stretch(id="nz1", refs=["NZ-0001"]),
            {"id": "broken", "refs": ["CA-9999"], "river": "Test River"},
            stretch(id="ok2", country="CH", refs=["CH-9999"])]
    p = write_stretches(tmp_path, rows)
    out = tmp_path / "out"
    code = K.main(["--stretches", str(p), "--out", str(out), "--cache", str(tmp_path / "c")])
    assert code == K.EXIT_NOT_FINISHED  # SOURCE DOWN row still to do
    rep = list(csv.DictReader(open(out / "banks" / "report.csv")))
    assert list(rep[0].keys()) == ["id", "refs", "source used", "status", "why"]
    st = {r["id"]: r["status"] for r in rep}
    assert st == {"ok1": "OK", "down1": "SOURCE DOWN", "nz1": "NO OFFICIAL BANK SOURCE",
                  "broken": "CAN'T TELL", "ok2": "OK"}
    assert (out / "sources.md").exists()
    # resume: source back up, only the SOURCE DOWN row is redone
    fake_world["down"] = False
    code = K.main(["--stretches", str(p), "--out", str(out), "--cache", str(tmp_path / "c"), "--resume"])
    assert code == K.EXIT_DONE
    rep = {r["id"]: r["status"] for r in csv.DictReader(open(out / "banks" / "report.csv"))}
    assert rep["down1"] == "OK"


def test_max_minutes_zero_is_exit_3(tmp_path, fake_world):
    p = write_stretches(tmp_path, [stretch(id="a", prov="CA-BC", refs=["CA-9999"])])
    code = K.main(["--stretches", str(p), "--out", str(tmp_path / "o"), "--max-minutes", "-1"])
    assert code == K.EXIT_NOT_FINISHED


def test_bad_input_is_exit_2(tmp_path):
    assert K.main(["--stretches", str(tmp_path / "nope.json"), "--out", str(tmp_path / "o")]) == K.EXIT_BAD_INPUT
    p = write_stretches(tmp_path, [stretch(id="a")])
    assert K.main(["--stretches", str(p), "--out", str(tmp_path / "us-key")]) == K.EXIT_BAD_INPUT


# ---------------------------------------------------------------- polite fetching

class FakeResp:
    def __init__(self, code, body=None, headers=None):
        self.status_code, self._b, self.headers = code, body, headers or {}
        self.text = json.dumps(body)

    def json(self):
        return self._b


class FakeSession:
    def __init__(self, answers):
        self.answers, self.calls, self.headers = list(answers), [], {}

    def request(self, method, url, timeout=None, **kw):
        self.calls.append(url)
        return self.answers.pop(0)


def test_fetcher_backoff_cache_and_user_agent(tmp_path, monkeypatch):
    sleeps = []
    monkeypatch.setattr(K.time, "sleep", lambda s: sleeps.append(s))
    f = K.Fetcher(tmp_path, min_gap_s=1.0)
    assert f.s.headers["User-Agent"] == "KPC-river-banks (https://github.com/KentuckyPortableClub)"
    fs = FakeSession([FakeResp(429, {}, {"Retry-After": "5"}), FakeResp(200, {"features": [1]})])
    f.s = fs
    body, read = f.get_json("https://example.test/q", {"a": "1"})
    assert body == {"features": [1]} and len(fs.calls) == 2 and 5.0 in sleeps
    body2, read2 = f.get_json("https://example.test/q", {"a": "1"})   # from the dated cache
    assert body2 == body and read2 == read and len(fs.calls) == 2
    cached = json.loads(next((tmp_path / "http").glob("*.json")).read_text())
    assert "read_at" in cached and cached["url"].startswith("https://example.test/q")


def test_fetcher_gives_up_as_source_down(tmp_path, monkeypatch):
    monkeypatch.setattr(K.time, "sleep", lambda s: None)
    f = K.Fetcher(tmp_path, retries=2)
    f.s = FakeSession([FakeResp(503, {})] * 3)
    with pytest.raises(K.SourceDown):
        f.get_json("https://example.test/x")


def test_offline_without_cache_is_source_down(tmp_path):
    f = K.Fetcher(tmp_path, offline=True)
    with pytest.raises(K.SourceDown):
        f.get_json("https://example.test/y")


def test_one_request_per_second_per_host(tmp_path, monkeypatch):
    sleeps = []
    monkeypatch.setattr(K.time, "sleep", lambda s: sleeps.append(s))
    f = K.Fetcher(tmp_path, min_gap_s=1.0)
    f._wait("https://a.example.test/1")
    f._wait("https://a.example.test/2")   # same host straight away: must wait about 1 s
    f._wait("https://b.example.test/1")   # other host: no wait
    assert len(sleeps) == 1 and 0.9 < sleeps[0] <= 1.0
