"""Nov 8 BLM pass: Bar M wired from file; every BLM lead recorded in the ledger."""
import csv, gzip, json, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_bar_m_wired():
    w = {r['ref']: r for r in csv.DictReader(open(ROOT / 'data/waiting/outline-sources/trail-lines-wired-nov7.csv', encoding='utf-8', newline=''))}
    assert w['US-11661']['layer_url'].startswith('file:')
    assert (ROOT / w['US-11661']['layer_url'][5:]).exists()


def test_ledger_blm_rows():
    d = json.load(gzip.open(ROOT / 'data/waiting/outline-sources/ledger.json.gz'))
    assert sum(1 for r in d['rows'].values() if (r.get('trail') or {}).get('blm_nov8')) >= 48
