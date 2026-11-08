"""Nov 8: wild rivers are bounded parks. Corridor/boundary joins are data-only overrides with source_kind; hand rulings kept."""
import gzip, json, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
OV = json.load(open(ROOT / 'data/us-key/overrides.json', encoding='utf-8'))['parks']
WB = json.load(open(ROOT / 'data/waiting/outline-sources/wild-river-bounds-nov8.json', encoding='utf-8'))['parks']


def test_joins_marked():
    joined = {r: v for r, v in WB.items() if v.get('joined')}
    assert len(joined) == 14
    for r, v in joined.items():
        assert set(v['joined']) <= set(OV[r]['join']) and OV[r]['source_kind'] in ('boundary', 'corridor', 'state_boundary')


def test_hand_rulings_not_overridden():
    for r in ('US-8015', 'US-10709', 'US-12234', 'US-12792', 'US-12798'):
        assert OV[r].get('none') is True and not OV[r].get('join') and WB[r].get('held')


def test_check_rows_not_joined():
    for r in ('US-0201', 'US-10106', 'US-10970', 'US-10103', 'US-10107', 'US-10113'):
        assert not WB.get(r, {}).get('joined')


def test_ledger_river_field_not_trail():
    d = json.load(gzip.open(ROOT / 'data/waiting/outline-sources/ledger.json.gz'))
    rows = [r for r in d['rows'].values() if (r.get('river') or {}).get('wild_river_bounds_nov8')]
    assert len(rows) == len(WB)
