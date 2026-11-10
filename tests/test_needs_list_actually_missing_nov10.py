"""Nov 10: the regenerated needs-download list asks a person only for what is actually missing (layers in no saved copy and in
no existing download), an official direct file a bot may fetch makes the row a bot's, and nothing private goes public."""
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
S = ROOT / '.github/scripts'
sys.path.insert(0, str(S))
import kpc_host_rules as HR  # noqa: E402
import kpc_needs_download as ND  # noqa: E402

DOC = json.loads((ROOT / 'data/needs-download.json').read_text(encoding='utf-8'))
ROWS = DOC['rows']
AG = 'https://services.arcgis.com/abc/arcgis/rest/services/X/FeatureServer/0'


def test_schema_and_order():
    assert DOC['format'] == ND.FORMAT
    assert all(set(r) == set(ND.FIELDS) for r in ROWS)
    assert [r['id'] for r in ROWS] == sorted(r['id'] for r in ROWS)
    assert all(r['who'] in ('bot', 'person', 'never') and r['status'] in ('open', 'done', 'held') for r in ROWS)


def test_few_person_rows_left():
    person = [r for r in ROWS if r['status'] == 'open' and r['who'] == 'person']
    assert 0 < len(person) <= 4, [r['id'] for r in person]


def test_never_rows_stay_never_and_bot_rows_have_an_allowed_file():
    for r in ROWS:
        if 'ncnhde.natureserve.org' in r['url']: assert r['who'] == 'never'
        if r['status'] == 'open' and r['who'] == 'bot':
            m = re.search(r'direct file:\s*(\S+)', r['note'] or '')
            assert m and HR.host_ok(m.group(1))[0], r['id']


def test_nothing_private_in_public():
    blob = (ROOT / 'data/needs-download.json').read_text(encoding='utf-8')
    for bad in ('/workspace', 'resale', 'non-commercial', 'noncommercial', 'license_or_terms', 'finder_notes', 'wdpa', 'protected planet'):
        assert bad not in blob.lower(), bad
    assert not re.search(r'\bt\d{3,4}u\b', blob)


def test_who_for_official_file():
    assert HR.who_for(AG)[0] == 'person'
    assert HR.who_for(AG, file_url='https://iris.fws.gov/APPS/ServCat/DownloadFile/1')[0] == 'bot'
    assert HR.who_for(AG, file_url='https://services-eu1.arcgis.com/x/f.zip')[0] == 'person'
    assert HR.who_for(AG, robots_ok=lambda u: False, file_url='https://iris.fws.gov/f')[0] == 'person'
    assert HR.who_for('https://ncnhde.natureserve.org/x', file_url='https://iris.fws.gov/f')[0] == 'never'


def test_vendor_copy_identical():
    assert (S / 'kpc_host_rules.py').read_bytes() == (S / 'draft/tools/kpc_engine/vendor/kpc_host_rules.py').read_bytes()
