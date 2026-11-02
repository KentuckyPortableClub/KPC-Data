"""Offline unit tests for KPC 9 on made-up shapes. No network: every web call goes to a fake session."""
import collections
import io
import json
import sys
from pathlib import Path

import pytest
from PIL import Image
from shapely.geometry import LineString, Point, Polygon, box

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import kpc_map_pictures as k  # noqa: E402


# --- a fake web, so nothing leaves the machine
class FakeResp:
    def __init__(self, status=200, body=b"", ctype="application/json", headers=None):
        self.status_code, self.content = status, body
        self.headers = {"content-type": ctype, **(headers or {})}
        self.text = body.decode("utf-8", "ignore") if isinstance(body, bytes) else body

    def json(self):
        return json.loads(self.content)


class FakeSession:
    def __init__(self, answers):
        self.answers, self.calls, self.headers = answers, [], {}

    def get(self, url, params=None, timeout=None):
        self.calls.append(url)
        for key, resp in self.answers:
            if key in url:
                return resp.pop(0) if isinstance(resp, list) else resp
        return FakeResp(404, b"", "text/html")


class Clock:
    def __init__(self):
        self.t, self.slept = 0.0, []

    def __call__(self):
        return self.t

    def sleep(self, s):
        self.slept.append(s)
        self.t += s


def http_with(tmp_path, answers):
    c = Clock()
    s = FakeSession(answers)
    return k.Http(tmp_path / "cache", session=s, sleep=c.sleep, clock=c), s, c


# --- tile maths
def test_tile_range_and_zoom():
    x, y = k.lonlat_to_merc(0, 0)
    assert abs(x) < 1e-6 and abs(y) < 1e-6
    assert k.tile_range(-1, -1, 1, 1, 1) == (0, 0, 1, 1)
    assert k.zoom_for(k.R0 / 2 ** 10, 20) == 10
    assert k.zoom_for(0.01, 16) == 16          # capped at the source's top zoom


def test_view_keeps_picture_shape():
    v = k.view_for((-85.0, 37.0, -84.99, 37.001))
    w, h = v[2] - v[0], v[3] - v[1]
    assert abs(w / h - k.W / k.H) < 1e-6


def test_basemap_by_prefix():
    assert k.basemap_for("US-0001") == "usgs"
    assert k.basemap_for("CA-0006") == "nrcan"
    assert k.basemap_for("CH-0306") == "swisstopo"
    assert k.basemap_for("JA-0001") == "plain"   # no government map known: plain background, never OSM / Google


# --- shapes
def test_club_shape_ring_vs_line():
    ring = [[0, 0], [0.01, 0], [0.01, 0.01], [0, 0.01], [0, 0]]
    assert k.club_shape(ring).area > 0
    assert k.club_shape([[0, 0], [0.01, 0.01]]).geom_type == "LineString"
    assert k.club_shape([]) is None


def test_ring_inside_ring_is_a_hole():
    outer = [[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]
    inner = [[0.4, 0.4], [0.6, 0.4], [0.6, 0.6], [0.4, 0.6], [0.4, 0.4]]
    g = k.rings_to_shape([outer, inner])
    assert abs(g.area - 0.96) < 1e-9


def test_esri_rings_clockwise_outer():
    cw = [[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]          # clockwise = outer
    ccw = [[0.2, 0.2], [0.4, 0.2], [0.4, 0.4], [0.2, 0.4], [0.2, 0.2]]   # counter-clockwise = hole
    g = k.esri_to_shape({"rings": [cw, ccw]})
    assert abs(g.area - 0.96) < 1e-9
    assert k.esri_to_shape({"paths": [[[0, 0], [1, 1]]]}).geom_type == "LineString"


def test_pin_distance():
    sq = box(-85.0, 37.0, -84.99, 37.01)
    assert k.pin_distance_m(sq, -84.995, 37.005) == 0
    d = k.pin_distance_m(sq, -84.98, 37.005)       # 0.01 deg east of the edge ~ 888 m at 37 N
    assert 850 < d < 920


def test_width_and_acres():
    # a 100 m x 1000 m strip near 37 N
    m_lat, m_lon = 1 / 111000, 1 / (111000 * 0.7986)
    strip = box(-85, 37, -85 + 1000 * m_lon, 37 + 100 * m_lat)
    assert 95 < k.width_m(strip) < 105
    assert 24 < k.acres(strip) < 25.5               # 100 000 m2 = 24.7 ac
    assert k.acres(LineString([(0, 0), (1, 1)])) == 0


def test_buffer_100ft():
    line = LineString([(-85, 37), (-84.99, 37)])
    b = k.metric_buffer(line, k.FT100)
    assert 55 < k.width_m(b) < 63                    # 2 x 30.48 m


def test_best_acres_no_double_count():
    assert k.best_acres([(1, 100), (2, 50)]) == 150                    # two pieces of one source add up
    assert k.best_acres([("1", 100), ("sgtne5", 120)]) == 120          # two sources for the same land: the bigger
    assert k.best_acres([("1", None)]) is None


def test_is_live():
    assert k.is_live({"status": "candidate"})
    assert not k.is_live({"status": "dropped: too small"})
    assert not k.is_live({"status": "merged into X"})
    assert not k.is_live({"status": "NOT SURE"})


def test_warnings():
    sq = box(-85.0, 37.0, -84.99, 37.01)
    assert any("outside" in w for w in k.outline_warnings(sq, None, 3000))
    assert any("tiny" in w for w in k.outline_warnings(sq, 50000, 0))
    assert k.outline_warnings(None, 10, 0) == ["the record geometry is empty"]


def test_pin_text():
    assert k.pin_text(0) == "pin inside"
    assert k.pin_text(123.4) == "pin 123 m outside"
    assert k.pin_text(25000) == "pin 25.0 km outside"


# --- drawing
def test_dashed_line_draws():
    img = Image.new("RGB", (100, 20), (255, 255, 255))
    from PIL import ImageDraw
    k.dashed_line(ImageDraw.Draw(img), [(0, 10), (100, 10)], (0, 0, 0))
    row = [img.getpixel((x, 10)) for x in range(100)]
    assert (0, 0, 0) in row and (255, 255, 255) in row     # dashes and gaps


def test_render_offline_plain(tmp_path):
    http = k.Http(tmp_path / "c", offline=True)
    sq = box(-85.0, 37.0, -84.98, 37.02)
    item = {"view_bounds": sq.bounds, "basemap": "plain", "title1": "US-9999 K4TEST Made-up Park", "title2": "test",
            "outlines": [{"geom": sq, "colour": k.GOLD}], "patch": box(-84.995, 37.005, -84.99, 37.01),
            "bands": [{"geom": k.metric_buffer(sq.exterior, k.FT100)}], "pins": [{"lon": -84.99, "lat": 37.01, "label": "US-9999"},
                                                                               {"lon": -80, "lat": 40, "label": "US-9998"}],
            "neighbours": [{"geom": box(-84.97, 37.0, -84.96, 37.01), "name": "Next door"}]}
    jpg = k.render(http, item, collections.Counter())
    assert len(jpg) < k.MAX_BYTES
    assert Image.open(io.BytesIO(jpg)).size == (900, 700)


def test_jpeg_steps_down_to_fit():
    import random
    random.seed(1)
    img = Image.effect_noise((900, 700), 120).convert("RGB")     # worst case for JPEG
    assert len(k.to_jpeg(img)) <= k.MAX_BYTES


# --- polite fetching
def test_one_request_per_second_and_user_agent(tmp_path):
    http, s, c = http_with(tmp_path, [("robots.txt", FakeResp(404, b"", "text/html")), ("/a", FakeResp(200, b'{"x":1}'))])
    http.get("https://example.gov/a", {"q": 1})
    http.get("https://example.gov/a", {"q": 2})
    assert s.headers["User-Agent"].startswith("KPC-") and "github.com/KentuckyPortableClub" in s.headers["User-Agent"]
    assert sum(c.slept) >= 2.0 - 1e-9                 # robots + 2 calls on one host: at least 2 s of waiting


def test_backoff_on_429_then_ok(tmp_path):
    http, s, c = http_with(tmp_path, [("robots.txt", FakeResp(404, b"", "text/html")),
                                      ("/b", [FakeResp(429, b"", headers={"Retry-After": "7"}), FakeResp(503, b""), FakeResp(200, b'{"ok":1}')])])
    data, read = http.get("https://example.gov/b")
    assert data == {"ok": 1} and 7 in c.slept


def test_robots_disallow(tmp_path):
    http, s, c = http_with(tmp_path, [("robots.txt", FakeResp(200, b"User-agent: *\nDisallow: /\n", "text/plain"))])
    with pytest.raises(k.SourceDown, match="robots"):
        http.get("https://example.gov/c")
    assert not any(u.endswith("/c") for u in s.calls)


def test_cache_with_date(tmp_path):
    http, s, c = http_with(tmp_path, [("robots.txt", FakeResp(404, b"", "text/html")), ("/d", FakeResp(200, b'{"v":2}'))])
    http.get("https://example.gov/d")
    off = k.Http(tmp_path / "cache", offline=True)
    data, read = off.get("https://example.gov/d")
    assert data == {"v": 2} and read == k.today()


def test_arcgis_error_is_source_down(tmp_path):
    http, s, c = http_with(tmp_path, [("robots.txt", FakeResp(404, b"", "text/html")),
                                      ("/query", FakeResp(200, b'{"error":{"code":400,"message":"bad"}}'))])
    with pytest.raises(k.SourceDown):
        k.arc_query(http, "https://example.gov/arcgis/rest/services/x/MapServer/0", {"objectIds": "1"})


# --- the command line
def test_bad_input_exits_2(tmp_path):
    bad = tmp_path / "q.json"
    bad.write_text("{not json")
    assert k.main(["--questions", str(bad), "--out", str(tmp_path / "p"), "--offline"]) == 2
    assert k.main(["--out", str(tmp_path / "p")]) == 2
    assert k.main(["--refs", "US-0001", "--out", str(tmp_path / "p")]) == 2      # --refs without --key


def test_time_up_exits_3(tmp_path):
    q = tmp_path / "waiting" / "questions"
    q.mkdir(parents=True)
    (q / "layers.json").write_text(json.dumps({"questions": [{"ref": "US-9999", "record": 1, "layer": "https://example.gov/x/MapServer/0"}]}))
    assert k.main(["--questions", str(q / "layers.json"), "--out", str(tmp_path / "p"), "--max-minutes", "0", "--offline"]) == 3


def test_failed_item_is_logged_and_retried(tmp_path):
    q = tmp_path / "layers.json"
    q.write_text(json.dumps({"questions": [{"ref": "US-9999", "record": 1, "layer": "https://example.gov/x/MapServer/0"}]}))
    out = tmp_path / "p"
    assert k.main(["--questions", str(q), "--out", str(out), "--offline"]) == 3
    idx = json.loads((out / "index.json").read_text())
    assert idx[0]["status"] == "retry" and idx[0]["warnings"][0].startswith("SOURCE DOWN")


def test_live_ids_with_commas_split_on_semicolon(tmp_path):
    f = tmp_path / "fers" / "US-ZZ.json"
    f.parent.mkdir()
    f.write_text(json.dumps({"spots": [{"id": "US-1+US-2@area@37.1,-85.1", "refs": ["US-1", "US-2"], "kind": "area", "status": "dropped"}]}))
    assert k.main(["--fers", str(f), "--ids", "US-1+US-2@area@37.1,-85.1;X", "--out", str(tmp_path / "p"), "--offline"]) == 0


def test_esri_island_in_lake_is_valid():
    cw = lambda x0, y0, x1, y1: [[x0, y0], [x0, y1], [x1, y1], [x1, y0], [x0, y0]]
    ccw = lambda x0, y0, x1, y1: [[x0, y0], [x1, y0], [x1, y1], [x0, y1], [x0, y0]]
    s = k.esri_to_shape({"rings": [cw(0, 0, 10, 10), ccw(2, 2, 8, 8), cw(3, 3, 7, 7), ccw(4, 4, 6, 6)]})
    assert s.is_valid and abs(s.area - (100 - 36 + 16 - 4)) < 1e-9
