"""Owner rule, 2026-11-10: the hourly merge of the KPC-Links release list never brings back a wrong row. A bot row whose layer a bot may
not read and with no direct file a bot may fetch is a person's; an open bot row on an allowed host with no direct file is held (the bot
re-reads it; nobody downloads it); a held row is not reopened; a person's row is never made a bot's. Made-up rows only, no request."""
import pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github/scripts'))
import kpc_needs_download as ND  # noqa: E402

SV5 = 'https://services5.arcgis.com/x/arcgis/rest/services/CPWAdminData/FeatureServer/5/query'
NPS = 'https://mapservices.nps.gov/arcgis/rest/services/cultural_resources/nrhp_locations/MapServer/1/query'
FWS = 'https://services1.arcgis.com/K/ArcGIS/rest/services/US_Fish_and_Wildlife_Service/FeatureServer/7'


def doc(*rows): return {'format': ND.FORMAT, 'rows': [dict({k: '' for k in ND.FIELDS}, **r) for r in rows]}


def test_release_row_cannot_make_a_forbidden_host_a_bots_again():
    old = doc({'id': 'US-CO|sgcoc', 'area': 'US-CO', 'layer': 'sgcoc', 'url': SV5, 'who': 'person', 'status': 'done', 'added': '2026-11-10'})
    new = dict(old['rows'][0], who='bot')
    d, _, _ = ND.merge(old, [new])
    assert d['rows'][0]['who'] == 'person'


def test_open_bot_row_without_a_direct_file_is_held():
    d, _, _ = ND.merge(doc(), [{'id': 'US-AL|sgaki', 'area': 'US-AL', 'layer': 'sgaki', 'url': NPS, 'who': 'bot', 'status': 'open', 'why': 'SHORT', 'source': 'master'}])
    r = d['rows'][0]
    assert r['status'] == 'held' and r['who'] == 'bot' and 'nobody downloads it' in r['why']


def test_held_person_row_stays_held_and_a_bot_row_with_a_direct_file_stays_a_bots():
    old = doc({'id': 'W-AS|h172', 'area': 'W-AS', 'layer': 'h172', 'url': FWS, 'who': 'person', 'status': 'held', 'note': 'direct file: https://iris.fws.gov/f'})
    d, _, _ = ND.merge(old, [dict(old['rows'][0], who='bot', status='open', source='hand-filled list (Nov 10)')])
    assert d['rows'][0]['status'] == 'held' and d['rows'][0]['who'] == 'person'
    d, _, _ = ND.merge(doc(), [{'id': 'W-VI|h172', 'area': 'W-VI', 'layer': 'h172', 'url': FWS, 'who': 'bot', 'status': 'open', 'note': 'direct file: https://iris.fws.gov/f'}])
    assert d['rows'][0]['who'] == 'bot' and d['rows'][0]['status'] == 'open'
