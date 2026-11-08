"""Nov 8 (Brandon): KY ONP Wild_River_Corridors = official STATE boundary for Kentucky wild rivers; BLM trailheads pass is ledger only."""
import gzip, json, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
WB = json.load(open(ROOT / 'data/waiting/outline-sources/wild-river-bounds-nov8.json', encoding='utf-8'))['parks']
LED = json.load(gzip.open(ROOT / 'data/waiting/outline-sources/ledger.json.gz'))['rows']
ROW = {k.split('|')[0]: v for k, v in LED.items()}
KY = ('US-10104', 'US-10105', 'US-10108', 'US-10111', 'US-10112')


def test_ky_state_boundary():
    for r in KY:
        ky = [n for n in WB[r]['notes'] if n.startswith('ky:')]
        assert WB[r]['ky_source_kind'] == 'state_boundary' and ky and all('source_kind=corridor' not in n for n in ky)
        assert 'state_boundary' in ROW[r]['river']['wild_river_bounds_nov8'] and ROW[r]['river']['ky_state_boundary_nov8']
    assert 'check' in WB['US-10106']['notes'][0] and 'ky_source_kind' not in WB['US-10106']


def test_blm_pass_ledger_only():
    for r in ('US-13214', 'US-13206', 'US-11815'):
        assert 'KEPT existing line' in ROW[r]['trail']['blm_trailheads_nov8'] and (ROOT / f'data/trails/{r}.json').exists()
    assert sum(1 for v in ROW.values() if (v.get('trail') or {}).get('blm_trailheads_nov8')) == 22


def test_ca_trails_pass():
    assert (ROOT / 'data/trails/CA-5506.json').exists() and 'wired' in ROW['CA-5506']['trail']['ca_trails_nov8']
    assert 'ledger only' in ROW['CA-6141']['trail']['ca_trails_nov8'] and not (ROOT / 'data/trails/CA-6141.json').exists()
    assert '8.40 km' in ROW['CA-6211']['trail']['ca_trails_nov8'] and not (ROOT / 'data/trails/CA-6211.json').exists()
    assert sum(1 for v in ROW.values() if (v.get('trail') or {}).get('ca_trails_nov8')) == 52
    assert sum(1 for v in ROW.values() if (v.get('trail') or {}).get('qc_trq_nov8')) >= 200
    raw = (ROOT / 'data/waiting/outline-sources/trail-lines-wired-nov7.csv').read_bytes()
    assert raw.count(b'\r\n') == raw.count(b'\n')
