"""A blank --areas / AREAS means every area in the club order, never 'do nothing' (club note, Nov 1 2026)."""
import json, pathlib
from core import adapters


def test_order_areas_club_order():
    got = adapters.order_areas(['GB', 'US-TN', 'MX', 'CA-ON', 'US-KY', 'ZA', 'AU'])
    assert got == ['US-KY', 'CA-ON', 'US-TN', 'MX', 'GB', 'AU', 'ZA']


def test_all_areas_from_pota_folder(tmp_path):
    rows = [{'reference': 'US-0001', 'locationDesc': 'US-TN,US-KY'}, {'reference': 'GB-0001', 'locationDesc': 'GB-ENG'},
            {'reference': 'CA-0001', 'locationDesc': 'CA-ON'}, {'reference': 'MX-0001', 'locationDesc': 'MX-ROO'}]
    (tmp_path / 'p.json').write_text(json.dumps(rows))
    c = adapters.Club(data=tmp_path / 'none', links=tmp_path / 'none', pota=tmp_path)
    assert c.all_areas() == ['US-KY', 'CA-ON', 'US-TN', 'MX', 'GB']


def test_blank_areas_not_empty(monkeypatch, tmp_path):
    import kpc_engine
    monkeypatch.delenv('AREAS', raising=False)
    (tmp_path / 'p.json').write_text(json.dumps([{'reference': 'US-0001', 'name': 'Test', 'locationDesc': 'US-KY'}]))
    out = tmp_path / 'o'
    assert kpc_engine.main(['gaps', '--pota', str(tmp_path), '--out', str(out), '--offline']) == 0
    assert list(json.load(open(out / 'gaps.json'))) == ['US-KY']
