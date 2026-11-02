"""Unit tests for the KPC 2-fer accuracy checker: verdict logic on synthetic geometries (no network)."""
import json
import pathlib
import sys

import pytest
import shapely
from shapely.geometry import LineString, Point, Polygon, box

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import kpc_fers_check as K  # noqa: E402

ACRE = K.ACRE_M2


def sq(x0, y0, w, h=None):
    return box(x0, y0, x0 + w, y0 + (h if h is not None else w))


# ------------------------------------------------------------------ compare(): the geometric verdict
def test_confirmed_same_shape():
    S = sq(0, 0, 400)
    r = K.compare(S, S.centroid, S)
    assert r['verdict'] == 'CONFIRMED'
    assert r['kept_pct'] == 100.0 and r['size_pct'] == 0.0 and r['moved_m'] == 0


def test_confirmed_within_25_percent():
    S = sq(0, 0, 400)
    L = sq(0, 0, 400, 340)            # 15% smaller, same place
    assert K.compare(S, S.centroid, L)['verdict'] == 'CONFIRMED'


def test_shrunk_more_than_25_percent_smaller():
    S = sq(0, 0, 400)
    L = sq(0, 0, 400, 200)            # 50% smaller
    r = K.compare(S, S.centroid, L)
    assert r['verdict'] == 'SHRUNK' and r['size_pct'] == -50.0


def test_shrunk_when_same_size_but_mostly_elsewhere_nearby():
    S = sq(0, 0, 400)
    L = sq(0, 220, 400)               # same size, overlaps 45% of the stored patch, centre 220 m off but touching
    r = K.compare(S, S.centroid, L)
    assert r['verdict'] in ('SHRUNK', 'MOVED')
    assert r['kept_pct'] < 75


def test_grew_more_than_25_percent_bigger():
    S = sq(0, 0, 400)
    L = sq(0, 0, 400, 600)
    r = K.compare(S, S.centroid, L)
    assert r['verdict'] == 'GREW' and r['size_pct'] == 50.0


def test_moved_centre_more_than_200_m_not_touching():
    S = sq(0, 0, 100)
    L = sq(600, 0, 100)               # same size, 600 m east, no contact
    r = K.compare(S, S.centroid, L)
    assert r['verdict'] == 'MOVED' and r['moved_m'] == 600 and r['kept_pct'] == 0.0


def test_not_moved_when_shift_under_200_m():
    S = sq(0, 0, 100)
    L = sq(150, 0, 100)               # 150 m away: < 200 m -> not MOVED (kept 0% -> SHRUNK)
    assert K.compare(S, S.centroid, L)['verdict'] == 'SHRUNK'


def test_gone_when_no_live_overlap():
    S = sq(0, 0, 100)
    assert K.compare(S, S.centroid, Polygon())['verdict'] == 'GONE'
    assert K.compare(S, S.centroid, None)['verdict'] == 'GONE'
    assert K.compare(S, S.centroid, sq(0, 0, 2))['verdict'] == 'GONE'   # 4 m2 < MIN_LIVE_M2: a sliver, not an overlap


def test_position_tolerance_10_m_for_thin_strips():
    S = sq(0, 0, 1000, 30)            # a 30 m strip (trail / river band)
    L = sq(0, 8, 1000, 30)            # drawn 8 m off (club 5 m grid + 5 m inset)
    r = K.compare(S, S.centroid, L)
    assert r['verdict'] == 'CONFIRMED' and r['kept_pct'] >= 99


def test_small_overlap_flag_under_50_yards_across():
    S = sq(0, 0, 1000, 40)            # 40 m across < 45.72 m
    r = K.compare(S, S.centroid, S)
    assert 'small overlap (under 50 yd across)' in r['flags']
    S2 = sq(0, 0, 1000, 60)
    assert 'small overlap (under 50 yd across)' not in K.compare(S2, S2.centroid, S2)['flags']


def test_water_only_flag():
    S = sq(0, 0, 200)
    assert 'water-only' in K.compare(S, S.centroid, S, water_row=True)['flags']


def test_far_away_extra_pieces_are_ignored():
    S = sq(0, 0, 200)
    L = shapely.union_all([sq(0, 0, 200), sq(5000, 0, 900)])   # an unrelated big piece 5 km away in the window
    assert K.compare(S, S.centroid, L)['verdict'] == 'CONFIRMED'


# ------------------------------------------------------------------ R5/R6: 100-ft buffer in metres (UTM), not degrees
def test_trail_buffer_is_100_ft_in_utm():
    lat, lon = 37.0, -84.3
    P = K.Proj(lat, lon)
    line = LineString([(lon, lat), (lon + 0.01, lat)])        # ~890 m east-west
    band = P.to_m(line).buffer(K.TRAIL_BUFFER_M)
    length = P.to_m(line).length
    expect = length * 2 * 30.48 + 3.14159 * 30.48 ** 2
    assert abs(band.area - expect) / expect < 0.01
    assert P.epsg == 32616


def test_utm_zone_selection():
    assert K.utm_for(37.5, -84.5) == 32616    # central Kentucky
    assert K.utm_for(37.5, -83.0) == 32617    # eastern Kentucky (-84 is the zone 16|17 line)
    assert K.utm_for(37.5, -88.5) == 32616
    assert K.utm_for(38.6, -111.0) == 32612   # Utah
    assert K.utm_for(37.5, -77.0) == 32618    # Virginia east


def test_bank_band_excludes_water_and_keeps_100_ft_of_land():
    water = sq(0, 0, 1000, 200)                # a 200 m wide river
    line = LineString([(0, 1500), (1000, 1500)])   # a coarse route line 1.3 km away (within 3 km)
    band = K.bank_band(line, water)
    assert band is not None
    assert band.intersection(water).area < 1
    # two banks x 1000 m x 30.48 m (+ ends)
    assert 2 * 1000 * 30.48 <= band.area <= 2 * 1000 * 30.48 + 2 * 260 * 30.48 + 3000
    assert K.bank_band(LineString([(0, 9000), (10, 9000)]), water) is None   # no water within 3 km -> caller uses the line


# ------------------------------------------------------------------ decide(): reading problems override the geometry
def park(**kw):
    d = {'ref': 'US-1', 'reads': [], 'issues': [], 'down': [], 'not_checked': '', 'records': 1}
    d.update(kw)
    return d


GEO_OK = {'verdict': 'CONFIRMED', 'why': 'ok'}
GEO_SHR = {'verdict': 'SHRUNK', 'why': 'smaller'}


def test_source_down_wins():
    v, why = K.decide(GEO_OK, [park(), park(down=['host: HTTP 503'])])
    assert v == 'SOURCE DOWN' and '503' in why


def test_not_checked_when_no_official_layer():
    v, _ = K.decide(None, [park(not_checked='only outline is traced from OpenStreetMap (not official, refused)')])
    assert v == 'NOT CHECKED'


def test_record_changed_on_rename_even_if_geometry_fine():
    v, _ = K.decide(GEO_OK, [park(issues=["record 12 renamed: key 'A' -> live 'B'"], renamed=True)])
    assert v == 'RECORD CHANGED'


def test_record_changed_when_record_missing():
    v, _ = K.decide({'verdict': 'GONE', 'why': 'none'}, [park(issues=['no record named X'], records=0)])
    assert v == 'RECORD CHANGED'


def test_issue_note_kept_when_geometry_confirmed():
    v, why = K.decide(GEO_OK, [park(issues=['2 key record id(s) no longer in layer'])])
    assert v == 'CONFIRMED' and 'note:' in why


def test_geometry_verdict_passes_through():
    assert K.decide(GEO_SHR, [park(), park()])[0] == 'SHRUNK'


# ------------------------------------------------------------------ input parsing
def test_stored_geometry_unclosed_ring_is_polygon():
    ring = [[-84.0, 37.0], [-83.99, 37.0], [-83.99, 37.01], [-84.0, 37.01]]   # club rings do not repeat the first point
    g = K.stored_geometry(ring)
    assert g.geom_type == 'Polygon' and g.area > 0
    g2 = K.stored_geometry(json.dumps(ring))                                  # shape stored as a JSON string
    assert g2.equals(g)
    assert K.stored_geometry(ring, as_line=True).geom_type == 'LineString'


def test_stored_geometry_rings_and_polygons():
    r1 = [[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]
    r2 = [[2, 2], [3, 2], [3, 3], [2, 3], [2, 2]]
    assert K.stored_geometry([r1, r2]).area == pytest.approx(2.0)
    hole = [[0.25, 0.25], [0.75, 0.25], [0.75, 0.75], [0.25, 0.75], [0.25, 0.25]]
    assert K.stored_geometry([[r1, hole]]).area == pytest.approx(0.75)


def test_trail_zone_falls_back_to_line_when_outline_is_garbled():
    lat, lon = 37.0, -84.0
    line = [[lon, lat], [lon + 0.02, lat]]
    good_zone = [[lon, lat - 0.00027], [lon + 0.02, lat - 0.00027], [lon + 0.02, lat + 0.00027], [lon, lat + 0.00027]]
    P = K.Proj(lat, lon)
    za = P.to_m(K.stored_geometry(good_zone)).area / ACRE
    spot = {'shape': line, 'zone': good_zone, 'zone_acres': za}
    g, note = K.stored_overlap_m(spot, 'trail', P)
    assert note == '' and g.area / ACRE == pytest.approx(za, rel=0.01)
    spot['zone_acres'] = za / 10             # file says 10x smaller: the stored outline is garbled (300-point cap)
    g, note = K.stored_overlap_m(spot, 'trail', P)
    assert 'disagrees' in note and g.area == pytest.approx(P.to_m(K.stored_geometry(line, as_line=True)).buffer(30.48).area)


def test_esri_rings_outer_and_hole():
    outer = [[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]]     # clockwise = outer
    hole = [[2, 2], [8, 2], [8, 8], [2, 8], [2, 2]]          # counter-clockwise = hole
    g = K.esri_to_shape({'rings': [outer, hole]})
    assert g.area == pytest.approx(64.0)
    assert K.esri_to_shape({'paths': [[[0, 0], [1, 1]]]}).geom_type in ('LineString', 'MultiLineString')


def test_row_kind_and_live_status():
    assert K.row_kind({'kind': 'area', 'status': 'water only: boat or kayak'}) == 'water-only'
    assert K.row_kind({'kind': 'trail', 'status': 'candidate'}) == 'trail'
    assert not K.is_live({'status': 'dropped: two owners'})
    assert not K.is_live({'status': 'merged into X'})
    assert K.is_live({'status': 'very tight: under 50 yd'})


def test_names():
    assert K.same_name('Fort Donelson National Battlefield', 'FORT DONELSON NATIONAL BATTLEFIELD')
    assert not K.same_name('Green River WMA', 'Barren River Lake WMA')


# ------------------------------------------------------------------ polite / official-only HTTP
class FakeResp:
    def __init__(self, code, j=None, headers=None):
        self.status_code, self._j, self.headers = code, j, headers or {}

    def json(self):
        if self._j is None:
            raise ValueError
        return self._j


def test_http_refuses_osm_google_and_unlisted(tmp_path):
    h = K.Http(tmp_path)
    for u in ('https://overpass-api.de/api/interpreter', 'https://tile.openstreetmap.org/x',
              'https://maps.googleapis.com/maps/api/x'):
        h.allow(u)
        with pytest.raises(K.Refused):
            h.get_json(u, {'f': 'json'})
    with pytest.raises(K.Refused):
        h.get_json('https://example.com/arcgis/rest/services/x/MapServer/0/query', {'f': 'json'})


def test_http_backoff_then_source_down(tmp_path, monkeypatch):
    sleeps = []
    monkeypatch.setattr(K.time, 'sleep', lambda s: sleeps.append(s))
    h = K.Http(tmp_path, tries=3, min_interval=0)
    url = 'https://x.gov/arcgis/rest/services/a/MapServer/0/query'
    h.allow(url)
    calls = []
    monkeypatch.setattr(h.s, 'get', lambda *a, **k: calls.append(1) or FakeResp(503, headers={'Retry-After': '7'}))
    with pytest.raises(K.SourceDown):
        h.get_json(url, {'f': 'json', 'where': '1=1'})
    assert len(calls) == 3 and 7.0 in sleeps


def test_http_user_agent_and_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(K.time, 'sleep', lambda s: None)
    h = K.Http(tmp_path, min_interval=0)
    assert 'Kentucky Portable Club' in h.s.headers['User-Agent']
    url = 'https://x.gov/arcgis/rest/services/a/MapServer/0/query'
    h.allow(url)
    calls = []
    monkeypatch.setattr(h.s, 'get', lambda *a, **k: calls.append(1) or FakeResp(200, {'features': []}))
    h.get_json(url, {'f': 'json'})
    h2 = K.Http(tmp_path, min_interval=0)        # a new run (resume) reads the disk cache: no second request
    h2.allow(url)
    monkeypatch.setattr(h2.s, 'get', lambda *a, **k: calls.append(1) or FakeResp(200, {'features': []}))
    h2.get_json(url, {'f': 'json'})
    assert len(calls) == 1


# ------------------------------------------------------------------ one row end to end with a stub reader (no network)
class StubReader:
    use_water = False

    def __init__(self, geoms):
        self.geoms = geoms
        self.keys = type('k', (), {'trails': {}})()

    def is_line_park(self, ref, area):
        g = self.geoms.get(ref)
        return g is not None and g.geom_type.endswith('LineString')

    def read_park(self, ref, area, window, center, **kw):
        g = self.geoms.get(ref)
        return {'ref': ref, 'geom': g, 'is_line': g is not None and g.geom_type.endswith('LineString'), 'reads':
                [{'ref': ref, 'layer': 'stub', 'how': 'stub', 'n': 1, 'read': '2026-10-31T00:00:00Z'}],
                'issues': [], 'down': [], 'not_checked': '', 'records': 1 if g is not None else 0}


def test_check_spot_area_and_trail(tmp_path):
    lat, lon = 37.0, -84.0
    ring = [[lon, lat], [lon + 0.005, lat], [lon + 0.005, lat + 0.004], [lon, lat + 0.004]]
    spot = {'id': 'US-1+US-2@area@37.0,-84.0', 'refs': ['US-1', 'US-2'], 'kind': 'area', 'status': 'candidate',
            'center': [lat + 0.002, lon + 0.0025], 'box': [lon, lat, lon + 0.005, lat + 0.004], 'shape': ring, 'acres': 1}
    big = box(lon - 0.01, lat - 0.01, lon + 0.005, lat + 0.02)
    other = box(lon, lat, lon + 0.02, lat + 0.004)
    r = K.check_spot(spot, 'US-KY', StubReader({'US-1': big, 'US-2': other}), tmp_path)
    assert r['verdict'] == 'CONFIRMED', r['why']
    r = K.check_spot(spot, 'US-KY', StubReader({'US-1': big, 'US-2': box(lon + 0.2, lat, lon + 0.3, lat + 0.1)}), tmp_path)
    assert r['verdict'] == 'GONE'
    # trail row: park x 100-ft band of the line
    line = LineString([(lon - 0.01, lat + 0.002), (lon + 0.03, lat + 0.002)])
    tspot = dict(spot, kind='trail', id='US-1+US-9@trail@37.0,-84.0', refs=['US-1', 'US-9'],
                 shape=[[lon, lat + 0.002], [lon + 0.005, lat + 0.002]])
    tspot.pop('acres')
    r = K.check_spot(tspot, 'US-KY', StubReader({'US-1': big, 'US-9': line}), tmp_path)
    assert r['verdict'] in ('CONFIRMED', 'GREW')
    assert r['live_acres'] > 0


def test_check_spot_trail_stretch_is_judged_where_stored(tmp_path):
    """A stored stretch that is one piece of a longer live band is CONFIRMED (not GREW); a line moved 400 m is MOVED."""
    lat, lon = 37.0, -84.5
    big = box(lon - 0.05, lat - 0.05, lon + 0.05, lat + 0.05)
    long_line = LineString([(lon - 0.04, lat), (lon + 0.04, lat)])                 # ~7 km of trail in the park
    spot = {'id': 'US-1+US-9@trail@37.0,-84.5', 'refs': ['US-1', 'US-9'], 'kind': 'trail', 'status': 'candidate',
            'center': [lat, lon], 'box': [lon - 0.005, lat - 0.001, lon + 0.005, lat + 0.001],
            'shape': [[lon - 0.005, lat], [lon + 0.005, lat]]}                    # stored: a ~900 m stretch
    r = K.check_spot(spot, 'US-KY', StubReader({'US-1': big, 'US-9': long_line}), tmp_path)
    assert r['verdict'] == 'CONFIRMED', r['why']
    assert r['live_stretch_acres'] > 5 * r['live_acres']
    moved = LineString([(lon - 0.04, lat + 0.0045), (lon + 0.04, lat + 0.0045)])   # same trail drawn ~500 m north
    r = K.check_spot(spot, 'US-KY', StubReader({'US-1': big, 'US-9': moved}), tmp_path)
    assert r['verdict'] == 'MOVED', r['why']


def test_river_line_band_adds_bank_of_river_area_it_runs_in():
    line = LineString([(0, 0), (1000, 0)])
    river = sq(-100, -60, 1300, 120)          # a 120 m wide NHD river area around the line
    pond = sq(0, 500, 100)                    # a pond 500 m away: never the river's water
    band = K.river_line_band(line, [river])
    assert band.area > line.buffer(30.48).area
    assert band.contains(Point(500, 85))      # 25 m beyond the bank
    assert K.river_line_band(line, [pond]).area == pytest.approx(line.buffer(30.48).area)


def test_water_route_detection():
    spot = {'names': {'US-4572': 'Lewis and Clark National Historic Trail', 'US-10976': 'Kolob Creek BLM Wild and Scenic River'}}
    assert K.is_water_route(spot, 'US-4572', {})
    assert not K.is_water_route(spot, 'US-10976', {})


def test_water_route_from_key_name_when_row_has_no_names():
    assert K.is_water_route({}, 'US-3791', {}, 'Trail of Tears National Historic Trail')


def test_simplified_stored_shape_judged_against_row_acres():
    # stored shape: a 1 km square preview; the row says the overlap is 4 km2; live is 4 km2 and still holds the preview
    S = sq(0, 0, 1000)
    L = sq(0, 0, 2000)
    acres = 4e6 / K.ACRE_M2
    assert K.compare(S, None, L)['verdict'] == 'GREW'
    r = K.compare(S, None, L, stored_acres=acres)
    assert r['verdict'] == 'CONFIRMED' and r['size_vs'] == 'row acres'
    # but row acres never rescue a live overlap that no longer holds the stored shape
    r = K.compare(S, None, sq(1500, 1500, 2000), stored_acres=acres)
    assert r['verdict'] != 'CONFIRMED'
