"""Nov 9 2026 weekly batch: an overrides.json release keeps newer KPC-Data hand edits (lost Nov 8 WSR joins)."""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / '.github/scripts'))
import kpc_waiting_room as W  # noqa: E402


def test_missing_park_is_carried():
    live = {'parks': {'US-9758': {'join': ['fwsr6'], 'when': '2026-11-08'}}}
    m, k = W.keep_newer_overrides(live, {'parks': {}})
    assert k == ['US-9758'] and m['parks']['US-9758']['join'] == ['fwsr6']


def test_newer_join_is_merged_older_is_not():
    live = {'parks': {'A': {'join': ['x', 'y'], 'fp': {'y': ['Y', 1]}, 'when': '2026-11-08'},
                      'B': {'join': ['z'], 'when': '2026-11-01'}}}
    new = {'parks': {'A': {'join': ['x'], 'when': '2026-11-02'}, 'B': {'join': [], 'when': '2026-11-09'}}}
    m, k = W.keep_newer_overrides(live, new)
    assert k == ['A'] and m['parks']['A']['join'] == ['x', 'y'] and m['parks']['A']['fp']['y'] == ['Y', 1]
    assert m['parks']['B']['join'] == []          # a later removal in the incoming copy still lands


def test_opposite_decision_not_brought_back():
    live = {'parks': {'A': {'join': ['x'], 'when': '2026-11-08'}}}
    m, k = W.keep_newer_overrides(live, {'parks': {'A': {'no': ['x'], 'when': '2026-11-02'}}})
    assert k == [] and 'join' not in m['parks']['A']


def test_promote_file_applies_it():
    import tempfile
    with tempfile.TemporaryDirectory() as t:
        _promote(pathlib.Path(t))


def _promote(tmp_path):
    old = W.DATA, W.W
    W.DATA, W.W = tmp_path, tmp_path / 'data/waiting'
    try: _promote_body(tmp_path)
    finally: W.DATA, W.W = old


def _promote_body(tmp_path):
    rel = 'data/us-key/overrides.json'
    (tmp_path / 'data/us-key').mkdir(parents=True)
    (tmp_path / rel).write_text(json.dumps({'parks': {'US-1': {'join': ['a'], 'when': '2026-11-08'}}}))
    inc = tmp_path / 'in.json'; inc.write_text(json.dumps({'parks': {'US-2': {'no': ['b'], 'when': '2026-11-09'}}}))
    W.promote_file(rel, None, raw=inc)
    out = json.load(open(tmp_path / rel))['parks']
    assert set(out) == {'US-1', 'US-2'}


if __name__ == '__main__':
    for n, f in list(globals().items()):
        if n.startswith('test_'): f(); print('ok', n)
