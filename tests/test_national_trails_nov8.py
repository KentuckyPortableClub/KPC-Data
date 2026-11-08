"""Nov 8 national trail lines: Tejas/Tierra Adentro swap fixed, wired extracts small, no internal-only features."""
import csv, gzip, json, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
TL = ROOT / 'data/waiting/outline-sources/trail-lines'
REFS = ['US-4568', 'US-4569', 'US-4238', 'US-4562', 'US-3791']


def _bbox(ref):
    xs = []
    for f in json.load(gzip.open(TL / f'{ref}.geojson.gz'))['features']:
        for ln in f['geometry']['coordinates']:
            xs += [p[0] for p in ln]
    return min(xs), max(xs)


def test_wired_and_small():
    wired = {r['ref']: r for r in csv.DictReader(open(ROOT / 'data/waiting/outline-sources/trail-lines-wired-nov7.csv', encoding='utf-8', newline=''))}
    for ref in REFS:
        assert wired[ref]['layer_url'] == f'file:data/waiting/outline-sources/trail-lines/{ref}.geojson.gz'
        assert (TL / f'{ref}.geojson.gz').stat().st_size < 1_000_000


def test_tejas_is_texas_tierra_is_new_mexico():
    assert _bbox('US-4568')[0] > -101   # Tejas: Texas/Louisiana
    assert _bbox('US-4569')[0] < -105   # Tierra Adentro: New Mexico/El Paso


def test_no_internal_only():
    assert b'nternal' not in gzip.open(TL / 'US-3791.geojson.gz').read()


def test_ledger_has_all_31_decisions():
    d = json.load(gzip.open(ROOT / 'data/waiting/outline-sources/ledger.json.gz'))
    n = sum(1 for r in d['rows'].values() if (r.get('trail') or {}).get('national_trails_nov8'))
    assert n == 31
