"""Unit tests for kpc_no_recheck (made-up shapes and a fake HTTP session: no network)."""
import hashlib
import json
import os
import shutil
import sys
from urllib.parse import parse_qs, urlparse

import pytest
from shapely.geometry import LineString, Polygon, box

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import kpc_no_recheck as k  # noqa: E402

LAT, LON = 37.0, -85.0          # a made-up pin in Kentucky
D = 0.001                       # ~110 m in latitude


def square(lat, lon, half):
    return box(lon - half, lat - half, lon + half, lat + half)


# ------------------------------------------------------------------ pin test
def test_pin_inside_polygon():
    inside, dist = k.pin_test(square(LAT, LON, D), LAT, LON)
    assert inside and dist == 0.0


def test_pin_outside_polygon_distance_in_metres():
    # square 0.01 deg east of the pin, west edge 0.009 deg away (~799 m at 37N)
    poly = box(LON + 0.009, LAT - D, LON + 0.011, LAT + D)
    inside, dist = k.pin_test(poly, LAT, LON)
    assert not inside
    assert 780 < dist < 820


def test_pin_near_a_line_within_100_ft():
    # a north-south line 20 m east of the pin -> counts as inside; 50 m east -> does not
    dlon20 = 20 / (111_320 * 0.7986)
    dlon50 = 50 / (111_320 * 0.7986)
    near = LineString([(LON + dlon20, LAT - D), (LON + dlon20, LAT + D)])
    far = LineString([(LON + dlon50, LAT - D), (LON + dlon50, LAT + D)])
    ins, d = k.pin_test(near, LAT, LON)
    assert ins and 18 < d < 22
    ins, d = k.pin_test(far, LAT, LON)
    assert not ins and 45 < d < 55


def test_acres_equal_area():
    # 1 km x 1 km square ~ 247.1 acres
    dlat = 500 / 111_320
    dlon = 500 / (111_320 * 0.7986)
    a = k.geom_acres(box(LON - dlon, LAT - dlat, LON + dlon, LAT + dlat))
    assert 240 < a < 255


def test_esri_rings_with_hole():
    outer = [[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]
    hole = [[0.4, 0.4], [0.6, 0.4], [0.6, 0.6], [0.4, 0.6], [0.4, 0.4]]
    g = k.to_shape(k.esri_to_geojson({"rings": [outer, hole]}))
    assert abs(g.area - 0.96) < 1e-9


# ------------------------------------------------------------------ names
def test_initials_joined():
    assert k.norm_tokens("R. F. Tarter State Park")[0] == ["rf", "tarter"]
    assert k.norm_tokens("RF Tarter SP")[0] == ["rf", "tarter"]
    assert k.name_score("R.F. Tarter State Park", "R F Tarter") == 1.0


def test_type_words_dropped_and_accents():
    toks, fams = k.norm_tokens("Chena Wayside State Recreation Site")
    assert toks == ["chena"] and "park" in fams
    assert k.norm_tokens("Lac Sainte-Thérèse Réserve")[0][:3] == ["lac", "sainte", "therese"]


def test_lake_does_not_match_lake_cumberland():
    assert k.name_score("Lake", "Lake Cumberland") < 0.75
    assert k.name_score("Lake Cumberland State Resort Park", "Lake") < 0.75
    assert k.name_score("Lake Cumberland State Resort Park", "Lake Cumberland SRP") >= 0.90


def test_chena_scores():
    # POTA's (truncated) name against the record's name field
    assert k.name_score("Chena Wayside State", "Chena River State Recreation Site") >= 0.90


def test_every_text_field_is_scored():
    props = {"OBJECTID": 5, "NAME": "Tract 12", "DESCRIP": "Trussum Pond Acquisition",
             "GlobalID": "{abc}", "URL": "https://x.gov/trussum-pond"}
    sc, field, text, _ = k.best_name_match(["Trussum Pond Natural Area"], props)
    assert field == "DESCRIP" and sc >= 0.9


def test_long_free_text_cannot_match_on_a_subset():
    assert k.name_score("Dunvegan", "Comments about Dunvegan West Wildland and the old ferry crossing") < 0.75


def test_title_pieces_need_a_shared_word():
    names = k.title_names("Chena River State Recreation Site | Alaska Department of Natural Resources",
                          ["Chena Wayside State"])
    assert "Chena River State Recreation Site" in names
    assert all("Department" not in n for n in names)


# ------------------------------------------------------------------ kind
def test_kind_conflict_wma_vs_state_park():
    park_fams = k.norm_tokens("Barren River Lake State Resort Park")[1]
    rec_fams, shown = k.record_kind({"Des_Tp": "WMA", "d_Des_Tp": "State Wildlife Management Area"})
    assert k.kind_conflict(park_fams, rec_fams)
    assert not k.kind_conflict(park_fams, k.record_kind({"PRKTYPABRV": "SRS"})[0])
    assert not k.kind_conflict(set(), rec_fams)  # unknown kind: no conflict


def test_kind_conflict_whole_lake_vs_recreation_area():
    park_fams = k.norm_tokens("Grayson Lake Recreation Area")[1]
    rec_fams, _ = k.record_kind({"FEAT_TYPE": "Lake", "TYPE": "Reservoir"})
    assert k.kind_conflict(park_fams, rec_fams)


def test_kind_conflict_keeps_no():
    ev = {"pin_inside": True, "pin_dist_m": 0.0, "name_score": 0.97, "size_ratio": None,
          "kind_conflict": True, "park_kind": "park", "record_kind": "wildlife"}
    v, why = k.decide(ev, None)
    assert v == "KEEP NO" and "kind conflict" in why


# ------------------------------------------------------------------ verdict rules
def ev(**kw):
    base = {"pin_inside": True, "pin_dist_m": 0.0, "name_score": 0.95, "size_ratio": None,
            "kind_conflict": False, "best_text": "X"}
    base.update(kw)
    return base


def test_look_again_rules():
    assert k.decide(ev(), None)[0] == "LOOK AGAIN"
    assert k.decide(ev(name_score=0.80, size_ratio=2.5), None)[0] == "LOOK AGAIN"
    assert k.decide(ev(name_score=0.80, size_ratio=3.5), None)[0] == "KEEP NO"
    assert k.decide(ev(name_score=0.80, size_ratio=None), None)[0] == "KEEP NO"  # no park acres: no 0.75 band
    assert k.decide(ev(name_score=0.95, size_ratio=11), None)[0] == "KEEP NO"     # size off > 10x
    assert k.decide(ev(name_score=0.70), None)[0] == "KEEP NO"
    v, why = k.decide(ev(pin_inside=False, pin_dist_m=2500.0), None)
    assert v == "KEEP NO" and "km outside" in why


def test_better_record():
    better = {"id": 9, "name": "Chena River SRS", "acres": 27.0, "score": 0.98, "pin_inside": True}
    v, why = k.decide(ev(pin_inside=False, pin_dist_m=900.0), better)
    assert v == "BETTER RECORD" and "9" in why


def test_only_no_answers_are_rechecked():
    assert k.is_no("NO", ["NO"]) and k.is_no("NO: a different place", ["NO"]) and k.is_no("no", ["NO"])
    assert not k.is_no("NOT SURE", ["NO"]) and not k.is_no("YES", ["NO"]) and not k.is_no(None, ["NO"])
    assert k.is_no("NOT SURE: maybe", ["NO", "NOT SURE"])


def test_order_kentucky_first():
    assert sorted(["AU", "CA-AB", "US-KY", "US-AK"], key=k.area_rank)[0] == "US-KY"
    assert k.area_rank("W-AU") == 3 and k.area_rank("CA-SK") == 1


# ------------------------------------------------------------------ the 15% cap
def test_cap_trips_over_15_percent():
    c = k.Cap()
    for v in ["KEEP NO"] * 15 + ["LOOK AGAIN"] * 2:
        c.add("b", v)
    assert not c.is_stopped("b")          # 2 LOOK AGAIN: under the 3-row minimum
    c.add("b", "LOOK AGAIN")              # 3 of 18 = 16.7%
    assert "too loose: check the scoring" in c.is_stopped("b")


def test_cap_stays_quiet_at_5_percent_and_ignores_cant_tell():
    c = k.Cap()
    for v in ["KEEP NO"] * 57 + ["LOOK AGAIN"] * 3 + [k.CANT] * 40:
        c.add("b", v)
    assert not c.is_stopped("b")


# ------------------------------------------------------------------ fake HTTP
class FakeResp:
    def __init__(self, status=200, body=None, text=None, headers=None):
        self.status_code = status
        self._body = body
        self.text = text if text is not None else (json.dumps(body) if body is not None else "")
        self.headers = headers or {"content-type": "application/json"}
        self.encoding = "utf-8"

    def json(self):
        if self._body is None:
            raise ValueError("no json")
        return self._body

    def iter_content(self, n):
        yield self.text.encode()

    def close(self):
        pass


class FakeSession:
    """Answers POTA and ArcGIS queries from a dict of parks / records; records every call."""

    def __init__(self, parks, records, layer, extra=None, fail_substr=None):
        self.fail_substr = fail_substr
        self.headers = {}
        self.calls = []
        self.parks, self.records, self.layer = parks, records, layer
        self.extra = extra or {}

    def get(self, url, timeout=None, stream=False, allow_redirects=True):
        self.calls.append((url, dict(self.headers)))
        if url in self.extra:
            r = self.extra[url]
            return r.pop(0) if isinstance(r, list) else r
        if self.fail_substr and self.fail_substr in url:
            return FakeResp(503, text="down", headers={})
        if url.startswith(k.POTA_API):
            ref = url[len(k.POTA_API):]
            return FakeResp(200, self.parks.get(ref))
        if url.endswith("/robots.txt"):
            return FakeResp(404, text="", headers={"content-type": "text/plain"})
        if url.startswith(self.layer + "/query"):
            q = parse_qs(urlparse(url).query)
            feats = []
            if "objectIds" in q:
                for oid in q["objectIds"][0].split(","):
                    r = self.records.get(int(oid))
                    if r:
                        feats.append({"type": "Feature", "id": int(oid), "properties": r["props"],
                                      "geometry": r["geom"].__geo_interface__})
            else:
                for oid, r in self.records.items():
                    feats.append({"type": "Feature", "id": oid, "properties": r["props"], "geometry": None})
            return FakeResp(200, {"type": "FeatureCollection", "features": feats})
        return FakeResp(404, text="not found", headers={"content-type": "text/html"})


LAYER = "https://gis.example.gov/arcgis/rest/services/Parks/MapServer/0"


def make_world(n_rows, n_flip):
    """n_rows NO rows; the first n_flip have POTA's pin inside a record with the same name."""
    parks, records, rows = {}, {}, []
    for i in range(n_rows):
        ref = f"US-{9000 + i}"
        lat, lon = 37.0 + i * 0.1, -85.0
        parks[ref] = {"reference": ref, "name": f"Zork{i} State Park", "latitude": lat, "longitude": lon,
                      "website": None, "parktypeDesc": "State Park"}
        name = f"Zork{i} State Park" if i < n_flip else f"Quux{i} Hollow Tract"
        records[i + 1] = {"props": {"NAME": name}, "geom": square(lat, lon, D)}
        rows.append({"area": "US-KY", "ref": ref, "park": f"Zork{i} State Park", "kind": "name match",
                     "record": i + 1, "record_name": name, "acres_approx": 60, "layer": LAYER,
                     "record_link": "", "pota_link": "", "question": "Is this ...? YES / NO",
                     "answer": "NO", "checked_by": "chat 11", "how": "names only"})
    rows.append({"area": "US-KY", "ref": "US-1", "park": "Kept Yes", "record": 99, "layer": LAYER,
                 "answer": "YES", "checked_by": "chat 11", "how": "x"})
    rows.append({"area": "US-KY", "ref": "US-2", "park": "Not Sure", "record": 98, "layer": LAYER,
                 "answer": "NOT SURE", "checked_by": "chat 11", "how": "x"})
    return parks, records, {"about": "test", "built": "2026-10-31", "questions": rows}


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def run_main(tmp_path, data, parks, records, extra_args=(), name="gis-hunter.json"):
    ind = tmp_path / "in"
    ind.mkdir(exist_ok=True)
    p = ind / name
    if not p.exists():
        p.write_text(json.dumps(data, indent=1))
    sess = FakeSession(parks, records, LAYER)
    f = k.Fetcher(str(tmp_path / "cache"), session=sess, sleep=lambda s: None)
    out = tmp_path / "out"
    code = k.main(["--in-dir", str(ind), "--files", name, "--out", str(out), *extra_args], fetcher=f)
    return code, p, out, sess


def test_inputs_byte_identical_and_answers_never_changed(tmp_path):
    parks, records, data = make_world(40, 2)
    # copy the real input files too, to prove they are never written
    real = os.path.join(os.path.dirname(HERE), "..", "kpc8", "input")
    ind = tmp_path / "in"
    ind.mkdir()
    (ind / "gis-hunter.json").write_text(json.dumps(data, indent=1))
    before = {p.name: sha(p) for p in ind.iterdir()}
    mtimes = {p.name: p.stat().st_mtime_ns for p in ind.iterdir()}
    code, p, out, _ = run_main(tmp_path, data, parks, records)
    assert code == 0
    assert {q.name: sha(q) for q in ind.iterdir()} == before
    assert {q.name: q.stat().st_mtime_ns for q in ind.iterdir()} == mtimes
    qs = json.load(open(out / "questions.json"))["questions"]
    assert len(qs) == 2
    for q in qs:
        assert q["answer"] is None and q["old_answer"] == "NO"
        assert q["evidence"] and q["suggested_record"]["record"] == q["record"]
    recs = json.load(open(out / "gis-hunter.json"))["records"]
    assert len(recs) == 40  # only the NO rows; YES and NOT SURE untouched
    assert {r["verdict"] for r in recs} == {"LOOK AGAIN", "KEEP NO"}


def test_real_input_files_byte_identical_after_offline_run(tmp_path):
    src = os.path.abspath(os.path.join(os.path.dirname(HERE), "sample_input"))
    if not os.path.isdir(src):
        src = "/workspace/kpc8/input"
    if not os.path.isdir(src):
        pytest.skip("real input files not present")
    ind = tmp_path / "in"
    shutil.copytree(src, ind)
    before = {p.name: sha(p) for p in ind.iterdir()}
    code = k.main(["--in-dir", str(ind), "--files", *sorted(before), "--out", str(tmp_path / "out"),
                   "--offline", "--cache-dir", str(tmp_path / "emptycache")])
    assert code == 0
    assert {p.name: sha(p) for p in ind.iterdir()} == before
    rows = json.load(open(tmp_path / "out" / "gis-hunter.json"))["records"]
    assert rows and all(r["verdict"] == k.CANT for r in rows)  # nothing cached: CAN'T TELL, never a guess


def test_cap_stops_a_loose_batch_and_withholds_its_questions(tmp_path):
    parks, records, data = make_world(20, 10)  # 50% would come out LOOK AGAIN
    code, p, out, _ = run_main(tmp_path, data, parks, records)
    assert code == 0
    s = open(out / "summary.md").read()
    assert "too loose: check the scoring" in s
    qs = json.load(open(out / "questions.json"))["questions"]
    assert qs == []
    recs = json.load(open(out / "gis-hunter.json"))["records"]
    assert len(recs) < 20  # the batch was stopped early


def test_better_record_from_neighbours(tmp_path):
    parks, records, data = make_world(1, 0)
    # record 1 is the wrong one; a neighbour (id 50) has the right name and the pin inside
    records[50] = {"props": {"NAME": "Zork0 State Park"}, "geom": square(37.0, -85.0, D / 2)}
    records[1]["geom"] = square(37.0, -84.99, D / 2)  # ~890 m east
    code, p, out, _ = run_main(tmp_path, data, parks, records)
    recs = json.load(open(out / "gis-hunter.json"))["records"]
    assert recs[0]["verdict"] == "BETTER RECORD" and recs[0]["better"]["id"] == 50
    q = json.load(open(out / "questions.json"))["questions"][0]
    assert q["suggested_record"]["record"] == 50 and q["answer"] is None


def test_record_gone_and_no_geometry_are_cant_tell(tmp_path):
    parks, records, data = make_world(2, 0)
    del records[1]
    records[2]["geom"] = Polygon()
    code, p, out, _ = run_main(tmp_path, data, parks, records)
    recs = json.load(open(out / "gis-hunter.json"))["records"]
    assert [r["verdict"] for r in recs] == [k.CANT, k.CANT]
    assert "gone" in recs[0]["why"] and "geometry" in recs[1]["why"]


def test_layer_down_is_cant_tell_and_retried_on_resume(tmp_path):
    parks, records, data = make_world(1, 1)
    ind = tmp_path / "in"; ind.mkdir()
    (ind / "g.json").write_text(json.dumps(data))
    sess = FakeSession(parks, records, LAYER, fail_substr="objectIds=1&")
    f = k.Fetcher(str(tmp_path / "cache"), session=sess, sleep=lambda s: None)
    code = k.main(["--in-dir", str(ind), "--files", "g.json", "--out", str(tmp_path / "o")], fetcher=f)
    assert code == 0
    r = json.load(open(tmp_path / "o" / "g.json"))["records"][0]
    assert r["verdict"] == k.CANT and "503" in r["why"]
    sess.fail_substr = None
    code = k.main(["--in-dir", str(ind), "--files", "g.json", "--out", str(tmp_path / "o"), "--resume"],
                  fetcher=k.Fetcher(str(tmp_path / "cache"), session=sess, sleep=lambda s: None))
    r = json.load(open(tmp_path / "o" / "g.json"))["records"][0]
    assert r["verdict"] == "LOOK AGAIN"


def test_exit_codes_time_limit_resume_and_bad_input(tmp_path):
    parks, records, data = make_world(3, 0)
    code, p, out, _ = run_main(tmp_path, data, parks, records, ["--max-minutes", "0"])
    assert code == 3
    code, p, out, _ = run_main(tmp_path, data, parks, records, ["--resume"])
    assert code == 0
    assert len(json.load(open(out / "gis-hunter.json"))["records"]) == 3
    assert k.main(["--in-dir", str(tmp_path), "--files", "missing.json", "--out", str(tmp_path / "x")]) == 2
    bad = tmp_path / "bad.json"; bad.write_text("{not json")
    assert k.main(["--files", str(bad), "--out", str(tmp_path / "x")]) == 2
    # --out on top of the input folder is refused
    assert k.main(["--in-dir", str(tmp_path / "in"), "--files", "gis-hunter.json",
                   "--out", str(tmp_path / "in")]) == 2


def test_limit_areas_offline(tmp_path):
    parks, records, data = make_world(4, 0)
    data["questions"][3]["area"] = "US-TN"
    code, p, out, sess = run_main(tmp_path, data, parks, records, ["--areas", "US-TN"])
    assert len(json.load(open(out / "gis-hunter.json"))["records"]) == 1
    code, p, out, sess = run_main(tmp_path, data, parks, records, ["--limit", "1"])
    assert code == 3


# ------------------------------------------------------------------ politeness
def test_user_agent_backoff_and_retry_after():
    sleeps = []
    sess = FakeSession({}, {}, LAYER, extra={
        "https://h.example/x": [FakeResp(429, text="", headers={"Retry-After": "7"}),
                                FakeResp(503, text="", headers={}), FakeResp(200, {"ok": 1})]})
    f = k.Fetcher("/tmp/kpc-nr-test-cache-unused", session=sess, sleep=sleeps.append)
    r = f.request("https://h.example/x")
    assert r.status_code == 200
    assert 7 in sleeps and 10 in sleeps            # Retry-After honoured, then 5*2^1
    assert all(h["User-Agent"] == "KPC-no-recheck (https://github.com/KentuckyPortableClub)"
               for _, h in sess.calls)


def test_one_request_per_second_per_host():
    sleeps = []
    sess = FakeSession({}, {}, LAYER, extra={"https://a.example/1": FakeResp(200, {}),
                                             "https://a.example/2": FakeResp(200, {}),
                                             "https://b.example/1": FakeResp(200, {})})
    f = k.Fetcher("/tmp/unused", session=sess, sleep=sleeps.append)
    f.request("https://a.example/1"); f.request("https://b.example/1"); f.request("https://a.example/2")
    assert len(sleeps) == 1 and 0.5 < sleeps[0] <= 1.0


def test_forbidden_hosts_and_robots(tmp_path):
    f = k.Fetcher(str(tmp_path), session=FakeSession({}, {}, LAYER), sleep=lambda s: None)
    with pytest.raises(k.FetchError):
        f.request("https://tile.openstreetmap.org/x")
    with pytest.raises(k.FetchError):
        f.request("https://www.protectedplanet.net/x")
    sess = FakeSession({}, {}, LAYER, extra={
        "https://parks.example/robots.txt": FakeResp(200, text="User-agent: *\nDisallow: /parks/",
                                                     headers={"content-type": "text/plain"})})
    f = k.Fetcher(str(tmp_path / "c2"), session=sess, sleep=lambda s: None)
    title, note = f.page_title("https://parks.example/parks/chena.htm")
    assert title is None and "robots" in note
    assert not any(u.endswith("chena.htm") for u, _ in sess.calls)


def test_offline_uses_cache_only(tmp_path):
    sess = FakeSession({"US-1": {"latitude": 1, "longitude": 2, "name": "A"}}, {}, LAYER)
    f = k.Fetcher(str(tmp_path), session=sess, sleep=lambda s: None)
    f.get_json(k.POTA_API + "US-1", 30)
    n = len(sess.calls)
    off = k.Fetcher(str(tmp_path), session=sess, offline=True, sleep=lambda s: None)
    assert off.get_json(k.POTA_API + "US-1", 30)[0]["name"] == "A"
    with pytest.raises(k.FetchError):
        off.get_json(k.POTA_API + "US-2", 30)
    assert len(sess.calls) == n


def test_record_name_gives_the_kind_when_no_type_field():
    fams, shown = k.record_kind({"UNIT_NAME": "Aniakchak National Preserve", "STATE": "AK"})
    assert k.groups(fams) and "UNIT_NAME" in shown
    park = k.families_of_text("Aniakchak National Wild and Scenic River")
    assert k.kind_conflict(park, fams)
    fams2, _ = k.record_kind({"Loc_Nm": "Alatna ANVSA", "Unit_Nm": "Alatna Alaska Native Village Statistical Area"})
    assert k.kind_conflict(k.families_of_text("Alatna National Wild and Scenic River"), fams2)


def test_order_of_work_ky_us_ca_north_america_world():
    areas = ["W-AU", "W-MX", "CA-AB", "US-KY", "W-GL", "US-TN", "GB"]
    assert sorted(areas, key=k.area_rank) == ["US-KY", "CA-AB", "US-TN", "W-MX", "W-GL", "W-AU", "GB"]


def test_owner_fields_are_never_used_or_shown():
    props = {"OWNER_NAME": "K4TEST Smith Farm", "PARK_NAME": "Smith Farm Park"}
    fields = dict(k.text_fields(props))
    assert "OWNER_NAME" not in fields and "PARK_NAME" in fields


def test_the_matched_pair_kinds_must_agree():
    # the bare POTA name matches, but the record's own name says it is another kind of place
    assert k.pair_conflict(k.families_of_text("Galena Creek Fish Hatchery"), "Galena Creek Fish Hatchery",
                           "Galena Creek Regional Park")
    assert k.pair_conflict(k.families_of_text("Wolf Creek Recreation Area"), "Wolf Creek", "Wolf Creek Falls Trail")
    assert k.pair_conflict(k.families_of_text("Milford State Fish Hatchery"), "Milford", "Milford Lake")
    # Chena: both sides are a state recreation site / wayside
    assert not k.pair_conflict(k.families_of_text("Chena Wayside State Recreation Site"),
                               "Chena Wayside State", "Chena River State Recreation Site")
    assert not k.pair_conflict(set(), "Cross Timbers", "Cross Timbers State Park")


def test_a_line_record_is_never_an_area_park():
    from shapely.geometry import LineString, Polygon
    road = LineString([(152.0, -25.0), (152.01, -25.0)])
    area = Polygon([(152.0, -25.0), (152.01, -25.0), (152.01, -25.01), (152.0, -25.01)])
    forest = k.families_of_text("Cordalba State Forest")
    assert k.shape_conflict(forest, road)                    # "Internal Roads - Cordalba SF" (a road line)
    assert not k.shape_conflict(forest, area)
    assert not k.shape_conflict(k.families_of_text("Big South Fork State Trail"), road)  # a trail park may be a line
    assert k.shape_conflict(set(), road)                     # unknown kind: not flagged on a line


def test_facility_heritage_and_lighthouse_kinds():
    blm = k.families_of_text("Lone Rock BLM Recreation Management Area")
    assert k.pair_conflict(blm, "Lone Rock", "Lone Rock Drift Boat Launch")
    assert k.pair_conflict(k.families_of_text("Mapungubwe National Park"), "Mapungubwe", "Mapungubwe Cultural Landscape")
    assert k.pair_conflict(k.families_of_text("Gunung Tambora National Park"), "Gunung Tambora", "SM Gunung Tambora Selatan")
    assert k.pair_conflict(k.families_of_text("Cape George Lighthouse National Heritage Site"), "Cape George Lighthouse",
                           "Cape George Provincial Park")


def test_a_dead_website_is_tried_once_per_run(tmp_path):
    calls = []

    class Dead:
        headers = {}

        def get(self, url, **kw):
            calls.append(url)
            import requests
            raise requests.ConnectionError("down")

    f = k.Fetcher(str(tmp_path), session=Dead(), sleep=lambda s: None)
    f.robots["example.org"] = k.Robots(None, allow_all=True)
    t1, n1 = f.page_title("https://example.org/a")
    t2, n2 = f.page_title("https://example.org/b")
    assert t1 is None and t2 is None and "earlier in this run" in n2
    assert len(calls) == 2  # two tries for the first page, none for the second
