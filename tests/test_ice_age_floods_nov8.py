"""US-3424 Ice Age Floods NGT: official NPS tour-route line wired from file, small, no OSM."""
import csv, gzip, json, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
GZ = ROOT / 'data/waiting/outline-sources/trail-lines/US-3424.geojson.gz'


def test_wired_row_and_file():
    w = {r['ref']: r for r in csv.DictReader(open(ROOT / 'data/waiting/outline-sources/trail-lines-wired-nov7.csv', encoding='utf-8', newline=''))}
    assert w['US-3424']['layer_url'] == 'file:data/waiting/outline-sources/trail-lines/US-3424.geojson.gz'
    assert GZ.stat().st_size < 500_000


def test_no_osm_and_spans_four_states():
    raw = gzip.open(GZ).read()
    assert b'openstreetmap' not in raw.lower() and b'osm' not in raw.lower()
    xs = [p[0] for f in json.loads(raw)['features'] for ln in f['geometry']['coordinates'] for p in ln]
    assert min(xs) < -122 and max(xs) > -114  # Oregon coast side to Montana
