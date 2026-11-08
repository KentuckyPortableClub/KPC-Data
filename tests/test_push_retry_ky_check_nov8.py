"""Nov 8: small batches + storage keeper push retries; the 2-fer checker reads the Kentucky key (KPC-Links) and saved KY outlines."""
import pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
W = ROOT / '.github/workflows'
sys.path.insert(0, str(ROOT / '.github/scripts/tools/kpc_fers_check'))


def test_pending_skips_empty_push_and_retries():
    s = (W / 'kpc-fers-pending.yml').read_text()
    assert 'git rev-list --count origin/main..HEAD' in s and 'for i in 1 2 3' in s and 'git rebase --abort' in s


def test_storage_rereads_board_on_conflict():
    s = (W / 'kpc-storage.yml').read_text()
    assert 'KPC_BOARD_L' in s and 'git reset -q --hard origin/main' in s and s.count('kpc_status.py board "Storage keeper (weekly)"') == 2


def test_checker_gets_ky_key():
    s = (W / 'kpc-fers-check.yml').read_text()
    assert '/data/ky-answer-key.json' in s and '/ky-*.geojson' in s and '--ky-key ../links/data/ky-answer-key.json' in s


def test_keys_ky_path(tmp_path):
    import json, kpc_fers_check as k
    (tmp_path / 'ky.json').write_text(json.dumps({'parks': {'US-1': {'n': 'X', 'tracts': [['bwild', 'Red River Wild River', 1, 'alias', 1]]}}}))
    keys = k.Keys(tmp_path, None, tmp_path / 'ky.json', None)
    assert keys.park('US-1', 'US-KY')[0] == 'ky' and keys.ky_saved('bwild', 'x', (0, 0, 1, 1)) == []
