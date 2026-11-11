#!/usr/bin/env python3
"""Brandon, Nov 7: a basemap source whose robots.txt says STOP drops out of the run (no retry, no other route) and the trace goes on
with the allowed sources; every result says '<name> source skipped (robots)'; a partial basemap is never reused from the cache.
Drives fetch_basemap with a fake PoliteHttp. Needs numpy only (geometry libraries stubbed).   python3 -B tests/test_basemap_skip_nov7.py"""
import importlib.util, json, os, pathlib, sys, tempfile, types

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for n, a in [('shapely', {}), ('shapely.geometry', dict(LineString=object, Point=object, Polygon=object, mapping=None)),
             ('shapely.validation', dict(make_valid=None)), ('shapely.ops', dict(unary_union=None)), ('pyproj', dict(Transformer=object)),
             ('sklearn', {}), ('sklearn.cluster', dict(DBSCAN=object, KMeans=object)), ('sklearn.neighbors', dict(KDTree=object))]:
    m = types.ModuleType(n); [setattr(m, k, v) for k, v in a.items()]; sys.modules.setdefault(n, m)
sp = importlib.util.spec_from_file_location('tp', os.path.join(ROOT, '.github/scripts/draft/kpc_trace_picture.py'))
TP = importlib.util.module_from_spec(sp); sp.loader.exec_module(TP)
# the control-point builders need shapely; this test is about which SOURCES are fetched, so they are stubbed to return no points
TP.line_network_nodes = lambda feats, min_degree=3: []
TP.line_crossings = lambda a, b, max_points=3000: []
TP.polygon_corners = lambda feats, min_shared=3: []
bad = []


def check(c, m):
    if not c: bad.append(m); print('FAIL', m)


class FakeHttp:
    """Answers one TIGER road and one PLSS square; the NHD water layer is a robots STOP, like hydro.nationalmap.gov today."""
    def __init__(self, block_water=True, block_all=False):
        self.block_water, self.block_all, self.asked = block_water, block_all, []

    def get_json(self, url, params):
        self.asked.append(url)
        if self.block_all or (self.block_water and url.startswith(TP.NHD)):
            raise RuntimeError('robots: host robots.txt does not allow this (robots.txt answered 403); not read, no other path tried')
        if url.startswith(TP.TIGER):
            return {'features': [{'geometry': {'type': 'LineString', 'coordinates': [[-85.0, 38.0], [-85.01, 38.01]]}}]}
        if url.startswith(TP.PLSS):
            return {'features': [{'geometry': {'type': 'Polygon', 'coordinates': [[[-85, 38], [-85, 38.01], [-85.01, 38.01], [-85.01, 38], [-85, 38]]]}}]}
        return {'features': []}


with tempfile.TemporaryDirectory() as td:
    cache = pathlib.Path(td)
    h = FakeHttp()
    d = TP.fetch_basemap(h, 'US-9999', 38.0, -85.0, 2.0, cache, use_cache=True)
    check(d.get('skipped') == ['water'], f'the water source is recorded as skipped: {d.get("skipped")}')
    check(sum(u.startswith(TP.NHD) for u in h.asked) == 1, f'the water server is asked once (the robots read), never retried: {h.asked}')
    check(any('TIGERweb' in s for s in d['sources']) and not any('NHD' in s for s in d['sources']),
          f'sources list the allowed ones only: {d["sources"]}')
    check(any(l[0] == 'road' for l in d['lines']), 'road lines from the allowed source are still there')
    # a partial basemap is NOT served from the cache on the next run (the water source may be allowed by then)
    h2 = FakeHttp(block_water=False)
    d2 = TP.fetch_basemap(h2, 'US-9999', 38.0, -85.0, 2.0, cache, use_cache=True)
    check(h2.asked and not d2.get('skipped'), f'a cached partial basemap must be refetched, not reused: asked={len(h2.asked)} skipped={d2.get("skipped")}')
    h3 = FakeHttp(block_water=False)
    d3 = TP.fetch_basemap(h3, 'US-9999', 38.0, -85.0, 2.0, cache, use_cache=True)
    check(not h3.asked and d3['fetched'] == d2['fetched'], f'a complete basemap IS reused from the cache (asked={len(h3.asked)})')
    # every allowed source blocked: nothing to match, no crash
    h4 = FakeHttp(block_all=True)
    d4 = TP.fetch_basemap(h4, 'US-9998', 38.0, -85.0, 2.0, cache, use_cache=True)
    check(d4['points'] == [] and set(d4['skipped']) == {'road', 'water', 'census water', 'land survey'}, f'all blocked -> empty basemap, all four skipped: {d4["skipped"]}')
    # any OTHER error still stops the map as before
    class Boom(FakeHttp):
        def get_json(self, url, params): raise RuntimeError('request failed after retries: x')
    try:
        TP.fetch_basemap(Boom(), 'US-9997', 38.0, -85.0, 2.0, cache, use_cache=True)
        bad.append('a non-robots failure must still raise'); print('FAIL a non-robots failure must still raise')
    except RuntimeError:
        pass
src = pathlib.Path(TP.__file__).read_text(encoding='utf-8')
check('source skipped (robots): partial basemap' in src, 'process_one must put the skipped-source note on every result')
print('FAIL' if bad else 'ALL PASS', f'({len(bad)} problems)' if bad else '')
sys.exit(1 if bad else 0)
