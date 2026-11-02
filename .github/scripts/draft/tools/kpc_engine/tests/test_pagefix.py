"""docs-pagefix hand-back (round 4): the two exact club shapes, US keyed by the hours-fees workbook row, CA by POTA ref."""
import csv
import pytest
from openpyxl import Workbook
from conftest import FIX
from core import export

SAMPLES = FIX / 'handback_samples'
FIXES = [{'ref': 'US-4559', 'area': 'US-FL', 'park': 'Florida Trail National Scenic Trail', 'link': 'https://www.fs.usda.gov/fnst',
          'problem': 'link wrong/dead; correct official page: https://www.fs.usda.gov/r08/florida/x', 'date': '2026-11-01'},
         {'ref': 'US-9999', 'area': 'US-KY', 'park': 'Nowhere State Park', 'link': 'https://parks.ky.gov/old',
          'problem': 'link opens but the page does not name the park', 'date': '2026-11-01'},
         {'ref': 'CA-1427', 'area': 'CA-ON', 'park': 'Greenwood Conservation Reserve', 'link': 'https://www.ontariotrails.on.ca/x',
          'problem': 'link wrong/dead; correct official page: https://ajax.ca/explore/', 'date': '2026-11-01'},
         {'ref': 'GB-0001', 'area': 'GB', 'park': 'X', 'link': 'https://x', 'problem': 'link wrong/dead', 'date': '2026-11-01'}]


def _header(p): return next(csv.reader(open(p, newline='')))


def _book(path, rows):
    wb = Workbook(); ws = wb.active; ws.title = 'Parks'
    ws.append(['State / prov', 'Park number', 'Name', 'Type', 'Activations', 'Official park page (start here)', 'Agency (if known)'])
    for r in rows: ws.append(r)
    wb.save(path); return str(path)


@pytest.fixture
def out(tmp_path, monkeypatch):
    o = tmp_path / 'out'; o.mkdir()
    with open(o / 'fixes.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, ['ref', 'area', 'park', 'link', 'problem', 'date']); w.writeheader(); w.writerows(FIXES)
    us = _book(tmp_path / 'us.xlsx', [['FL', 'US-4559', 'Florida Trail National Scenic Trail', 'NST', 1, 'https://www.fs.usda.gov/fnst', 'USFS']])
    ca = _book(tmp_path / 'ca.xlsx', [['ON', 'CA-0001', 'A', 'PP', 1, 'https://a', None]] + [[None] * 7] * 2
               + [['ON', 'CA-1427', 'Greenwood Conservation Reserve', 'CR', 1, 'https://www.ontariotrails.on.ca/x', None]])
    monkeypatch.setenv('KPC_HF_WORKBOOK_US', us); monkeypatch.setenv('KPC_HF_WORKBOOK_CA', ca)
    export._WB.clear()
    return o


def test_engine_headers_equal_the_club_samples():
    assert export.PAGEFIX_US == _header(SAMPLES / 'docs-pagefix-us.sample.csv')
    assert export.PAGEFIX_CA == _header(SAMPLES / 'docs-pagefix-ca.sample.csv')


def test_export_writes_both_exact_shapes(out):
    wrote, flags = export.export(out, 't')
    hb = out / 'handback'
    us, ca = hb / 'docs-pagefix-us-t.csv', hb / 'docs-pagefix-ca-t.csv'
    assert _header(us) == _header(SAMPLES / 'docs-pagefix-us.sample.csv')
    assert _header(ca) == _header(SAMPLES / 'docs-pagefix-ca.sample.csv')
    assert 'docs-pagefix' not in flags and not (hb / 'docs-pagefix-t.csv').exists()
    U = list(csv.DictReader(open(us, newline=''))); C = list(csv.DictReader(open(ca, newline='')))
    assert wrote['docs-pagefix-us'] == 2 and wrote['docs-pagefix-ca'] == 1         # GB never goes in either file
    a = U[0]
    assert a['row'] == '2' and a['old F URL'] == 'https://www.fs.usda.gov/fnst' and a['correct URL'] == 'https://www.fs.usda.gov/r08/florida/x'
    assert a['why column F was replaced'].startswith('link wrong/dead')
    b = U[1]                                                                      # not in the workbook: ref + mapping-needed note
    assert b['row'].startswith('US-9999') and 'mapping needed' in b['row'] and 'mapping needed' in b['why column F was replaced'] and b['correct URL'] == ''
    c = C[0]
    assert c['row'] == '5' and c['POTA ref'] == 'CA-1427' and c['correct official URL (if found)'] == 'https://ajax.ca/explore/' and c['issue'] == 'link wrong/dead'


def test_no_workbook_writes_ref_and_mapping_needed(out, monkeypatch):
    monkeypatch.setenv('KPC_HF_WORKBOOK_US', ''); monkeypatch.setenv('KPC_HF_WORKBOOK_CA', '')
    us, ca, paths = export.pagefix_rows(out)
    assert paths == {'US': None, 'CA': None}
    assert all(r[0].startswith('US-') and 'mapping needed' in r[0] for r in us)
    assert ca[0][0].startswith('CA-1427') and 'mapping needed' in ca[0][-1]


def test_rows_are_excel_row_numbers():
    import os
    p = export.find_workbook('US')
    if not p or not os.path.exists(p): pytest.skip('club workbook not on this machine')
    m = export.workbook_map(p)
    by_row = {v[0]: (k, v[1], v[2]) for k, v in m.items()}
    for r in csv.DictReader(open(SAMPLES / 'docs-pagefix-us.sample.csv', newline='')):      # the club's own 5 sample rows
        ref, name, F = by_row[int(r['row'])]
        assert name == r['park'] and F == r['old F URL'], (r['row'], ref)
