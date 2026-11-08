"""Nov 8 WSR pass: new river lines are WSR in index-state; Klamath is the Oregon segment; Scenic 7 / St. Francis have files."""
import csv, gzip, json, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
W = {r['ref']: r for r in csv.DictReader(open(ROOT / 'data/waiting/outline-sources/trail-lines-wired-nov7.csv', encoding='utf-8', newline=''))}
ST = {x['ref']: x for x in json.load(open(ROOT / 'data/trails/index-state.json'))}


def test_new_wsr_lines():
    for ref in ('US-4237', 'US-10104', 'US-10019'):
        assert W[ref]['layer_url'].startswith('file:') and ST[ref]['kind'] == 'WSR'
        assert (ROOT / W[ref]['layer_url'][5:]).stat().st_size < 500_000


def test_klamath_is_oregon_segment():
    assert ST['US-10019']['bbox'][1] > 41.9 and ST['US-10019']['km'] < 50


def test_ar_byways_have_files():
    for ref in ('US-8316', 'US-11953'):
        assert W[ref]['layer_url'].startswith('file:') and (ROOT / f'data/trails/{ref}.json').exists()


def test_check_rows_not_wired_and_noted():
    d = json.load(gzip.open(ROOT / 'data/waiting/outline-sources/ledger.json.gz'))
    n = sum(1 for r in d['rows'].values() if (r.get('trail') or {}).get('wsr_nov8'))
    assert n >= 104
    assert 'US-11800' not in W
