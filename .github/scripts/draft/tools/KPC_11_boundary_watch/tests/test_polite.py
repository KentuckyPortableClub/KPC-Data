"""Offline tests for the polite-fetching rules (no network)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import kpc_boundary_watch as tool  # noqa: E402


class Resp:
    def __init__(self, status, data=None, text="", headers=None):
        self.status_code, self._data, self.text, self.headers = status, data, text, headers or {}

    def json(self):
        if self._data is None:
            raise ValueError("not json")
        return self._data


class Session:
    def __init__(self, answers):
        self.answers, self.calls, self.headers = list(answers), [], {}

    def get(self, url, params=None, timeout=None):
        self.calls.append(url)
        return self.answers.pop(0)


def make(tmp_path, answers):
    sleeps = []
    s = Session(answers)
    web = tool.Polite("test", str(tmp_path / "cache"), session=s, sleep=sleeps.append)
    return web, s, sleeps


def test_user_agent():
    web = tool.Polite("13-same-land", "/tmp/x", session=Session([]))
    assert web.session.headers["User-Agent"] == "KPC-13-same-land (https://github.com/KentuckyPortableClub)"


def test_backs_off_on_429_and_5xx_then_caches(tmp_path):
    url = "https://example.test/arcgis/rest/services/A/MapServer/0/query"
    web, s, sleeps = make(tmp_path, [Resp(429, headers={"Retry-After": "7"}), Resp(503), Resp(200, {"count": 3})])
    assert web.get_json(url, {"where": "1=1"})["count"] == 3
    assert 7.0 in sleeps and len(s.calls) == 3
    # second time comes from the dated cache: no new request
    assert web.get_json(url, {"where": "1=1"}, max_age_s=3600)["count"] == 3
    assert len(s.calls) == 3


def test_one_request_per_second_per_host(tmp_path):
    url = "https://example.test/arcgis/rest/services/A/MapServer/0/query"
    web, s, sleeps = make(tmp_path, [Resp(200, {"a": 1}), Resp(200, {"a": 2})])
    web.get_json(url, {"q": 1}, use_cache=False)
    web.get_json(url, {"q": 2}, use_cache=False)
    assert sleeps and 0.5 < sleeps[-1] <= 1.0


def test_404_and_service_not_found_mean_layer_moved(tmp_path):
    url = "https://example.test/arcgis/rest/services/A/MapServer/0"
    web, s, sleeps = make(tmp_path, [Resp(404), Resp(200, {"error": {"code": 500, "message": "Service A/MapServer not found"}})])
    for _ in range(2):
        try:
            web.get_json(url, {"f": "json"}, use_cache=False)
            assert False, "should have raised"
        except tool.SourceProblem as e:
            assert e.kind == "LAYER MOVED"


def test_robots_txt_is_obeyed_for_web_pages(tmp_path):
    web, s, sleeps = make(tmp_path, [Resp(200, text="User-agent: *\nDisallow: /private/\n")])
    try:
        web.get_json("https://example.test/private/page.json")
        assert False, "should have raised"
    except tool.SourceProblem as e:
        assert e.kind == "BLOCKED BY ROBOTS"


def test_offline_mode_never_fetches(tmp_path):
    web, s, sleeps = make(tmp_path, [])
    web.offline = True
    try:
        web.get_json("https://example.test/arcgis/rest/services/A/MapServer/0")
        assert False
    except tool.SourceProblem as e:
        assert e.kind == "SOURCE DOWN"
    assert s.calls == []


def test_tract_piece_is_picked():
    from shapely.geometry import MultiPolygon, Polygon
    big = Polygon([(-85, 37), (-85, 37.02), (-84.98, 37.02), (-84.98, 37)])
    small = Polygon([(-84.9, 37), (-84.9, 37.005), (-84.895, 37.005), (-84.895, 37)])
    a = tool.geo_acres(small)
    g, narrowed = tool.narrow_to_tract(MultiPolygon([big, small]), a, 1)
    assert narrowed and abs(tool.geo_acres(g) - a) < 0.01
    g, narrowed = tool.narrow_to_tract(MultiPolygon([big, small]), a * 3, 1)
    assert not narrowed
