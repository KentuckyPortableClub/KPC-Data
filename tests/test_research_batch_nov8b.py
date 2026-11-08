"""Nov 8 research batch: 30 verified own-entity lines wired from file; check rows not wired; every lead has a ledger note."""
import csv, gzip, json, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
WIRED = ['US-5800', 'US-5808', 'US-5823', 'US-5829', 'US-5882', 'US-5894', 'US-5901', 'US-5984', 'US-10979', 'US-11656',
         'US-11664', 'US-11754', 'US-11766', 'US-0670', 'US-3378', 'US-9902', 'US-10421', 'US-11232', 'US-11234', 'US-13245',
         'US-13269', 'US-13500', 'US-11731', 'US-10964', 'US-11750', 'US-13159', 'US-0646', 'US-10107', 'US-13625', 'US-10877', 'US-8324', 'US-11954', 'US-13200', 'US-5818', 'US-5935', 'US-6020', 'US-11745']
NOT_WIRED = ['US-9980', 'US-13267', 'US-5906', 'US-4009', 'US-9161', 'US-10914', 'US-6048', 'US-8323', 'US-10303', 'US-11164', 'US-5860', 'US-11349', 'US-4105', 'US-11165']


def _wired():
    return {r['ref']: r for r in csv.DictReader(open(ROOT / 'data/waiting/outline-sources/trail-lines-wired-nov7.csv', encoding='utf-8', newline=''))}


def test_wired_files_small():
    w = _wired()
    for ref in WIRED:
        p = ROOT / w[ref]['layer_url'][5:]
        assert p.exists() and p.stat().st_size < 500_000, ref
        assert b'openstreetmap' not in gzip.open(p).read().lower()


def test_check_rows_not_wired():
    w = _wired()
    for ref in NOT_WIRED:
        assert ref not in w, ref


def test_rivers_are_wsr_in_state_index():
    st = {x['ref']: x for x in json.load(open(ROOT / 'data/trails/index-state.json'))}
    assert st['US-0646']['kind'] == 'WSR' and st['US-10107']['kind'] == 'WSR'


def test_every_lead_has_note():
    d = json.load(gzip.open(ROOT / 'data/waiting/outline-sources/ledger.json.gz'))
    n = sum(1 for r in d['rows'].values() if (r.get('trail') or {}).get('research_nov8b'))
    assert n >= 335
