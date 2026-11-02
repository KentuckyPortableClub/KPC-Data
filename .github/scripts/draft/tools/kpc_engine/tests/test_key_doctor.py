"""v0.5.0 key doctor (core/key_doctor.py, `kpc_engine.py doctor`). Built from small club-shaped checkouts in tmp folders."""
import datetime as dt, gzip, json, pathlib, pytest
from core import key_doctor as KD, rules


@pytest.fixture(autouse=True)
def _clean():
    rules.reset(); yield; rules.reset()


def put(p, obj):
    p = pathlib.Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    b = json.dumps(obj).encode()
    p.write_bytes(gzip.compress(b) if p.suffix == '.gz' else b)
    return p


def park(n, m=None, c=None, **kw):
    return dict(n=n, t='State Park', m=m or [], c=c or [], **kw)


@pytest.fixture
def club(tmp_path):
    L, D = tmp_path / 'links', tmp_path / 'data'
    put(L / 'data/us-key/overrides.json', {'parks': {
        'US-1': {'no': ['111'], 'nofp': {'111': ['Bad Marsh WMA', 50]}},
        'US-2': {'join': ['222']}}})          # chat 11 said NO to 222 but BOT A's save was lost
    put(L / 'data/us-key/layers.json', {'sgksb': ['https://example.gov/arcgis/rest/services/x/MapServer/3']})
    put(D / 'data/waiting/questions/key-pieces.json', {'questions': [
        {'ref': 'US-1', 'record': '111', 'record_name': 'Bad Marsh WMA', 'answer': 'NO', 'checked_by': 'chat 11'},
        {'ref': 'US-2', 'record': '222', 'record_name': 'Capital Park', 'answer': 'NO, a city park', 'checked_by': 'chat 11', 'acres': 12},
        {'ref': 'US-3', 'record': '27', 'layer': 'https://example.gov/arcgis/rest/services/x/MapServer/3', 'record_name': 'Milford WA', 'answer': 'NO'},
        {'ref': 'US-4', 'record': '444', 'record_name': 'Fine SP', 'answer': 'NOT SURE'}]})
    built = {'updated': '2026-11-02', 'parks': {
        'US-1': park('Good SP', [[111, 'Bad Marsh WMA', 50, 'name']]),     # a NO that came back
        'US-2': park('Capitol SP', [[222, 'Capital Park', 12, 'reviewed']]),
        'US-3': park('Milford State Fish Hatchery', [['sgksb27', 'Milford WA', 0, 'name']]),
        'US-5': park('Fine Lake SP', [[555, 'Fine Lake State Park', 300, 'name']])}}
    put(L / 'data/us-key/US-KS.json', built)
    put(D / 'data/waiting/in/data/us-key/US-KS.json', built)
    put(D / 'data/us-key/US-KS.json', {'updated': '2026-11-01', 'parks': {'US-1': park('Good SP', [[999, 'Good State Park', 40, 'name']]),
                                                                       'US-5': park('Fine Lake SP')}})
    put(D / 'data/waiting/approved.json', {'items': [
        {'what': 'us-key', 'path': 'data/waiting/in/data/us-key/', 'chat11': 'KEY YES 2026-10-31 6/6', 'date': '2026-10-31', 'chat2': 'rechecked'},
        {'what': 'us-key', 'chat11': 'KEY NO 2026-11-02 08:16 UTC build: US-2 Capitol SP -> Capital Park; US-3 Milford', 'date': '2026-11-02'},
        {'what': 'ca-key', 'path': 'data/waiting/in/data/ca-key/', 'chat11': 'KEY YES 2026-11-01 Canada key', 'date': '2026-11-01'},
        {'what': 'world-key', 'chat11': 'KEY YES 2026-11-01 11:14 UTC build', 'date': '2026-11-01', 'chat2': 'ok'},
        {'what': 'fers-US-KY', 'path': 'data/waiting/in/data/fers/US-KY.json', 'chat11': 'YES 2026-11-01', 'date': '2026-10-31', 'chat2': 'ok'}]})
    put(D / 'data/waiting/verdicts.json', {'results': [{'path': 'data/us-key/US-KS.json', 'verdict': 'PASS', 'why': []}]})
    return L, D, tmp_path / 'out'


def test_nos_found_missing_and_reapplied_to_a_copy(club):
    L, D, O = club
    before = (L / 'data/us-key/overrides.json').read_bytes()
    r = KD.task_nos(L, D, O)
    assert r['landed'] == 1 and {m['id'] for m in r['missing']} == {'222', 'sgksb27'}
    fx = json.load(open(O / 'overrides.fixed.json'))['parks']
    assert fx['US-2']['no'] == ['222'] and 'join' not in fx['US-2'] and fx['US-2']['nofp']['222'] == ['Capital Park', 12]
    assert fx['US-3']['no'] == ['sgksb27']                          # layer prefix from layers.json, like BOT A
    assert 'US-4' not in fx                                          # NOT SURE changes nothing
    assert {(b['ref'], b['id']) for b in r['came_back']} == {('US-1', '111')}
    assert (L / 'data/us-key/overrides.json').read_bytes() == before   # the checkout is never written


def test_reapply_switch_off_reports_only(club):
    L, D, O = club
    rules.load(disable=['key_doctor.reapply_nos'])
    r = KD.task_nos(L, D, O)
    assert r['missing'] and r['reapplied_copy'] is None and not (O / 'overrides.fixed.json').exists()


def test_yes_clears_a_sole_no_line_129():
    v = {'no': ['7'], 'nofp': {'7': ['X', 1]}}
    KD.apply_answer(v, '7', 'YES', {'record_name': 'X', 'acres': 1})
    assert 'no' not in v and 'nofp' not in v and v['join'] == ['7']


def test_release_is_report_only_by_default(club):
    L, D, O = club
    r = KD.task_release(L, D, O)
    f = r['files'][0]
    assert r['switch_per_park_release'] is False and f['verdict'] == 'LIVE-FILTERED'
    assert set(f['held_parks']) == {'US-1', 'US-2', 'US-3'} and f['pass'] == 1
    assert not (O / 'release').exists()


def test_release_switch_on_writes_filtered_copy(club):
    L, D, O = club
    rules.load(enable=['key_doctor.per_park_release'])
    KD.task_release(L, D, O)
    out = json.load(open(O / 'release/data/us-key/US-KS.json'))['parks']
    assert out['US-1']['m'][0][0] == 999                            # failing park keeps its LIVE version
    assert out['US-2']['m'] == [] and 'held' in out['US-2']         # no live version: a pin
    assert out['US-5']['m'][0][0] == 555                            # passing park goes as built


def test_approvals_missing_fields(club):
    L, D, O = club
    r = KD.task_approvals(D, O)
    got = {f['what']: f['missing'] for f in r['flags']}
    assert got['ca-key'] == ['chat2 (chat 2 recheck, G-4)']
    assert got['world-key'] == ['path (the folder it releases)']
    assert 'us-key' not in got                                      # latest us-key verdict is a NO: nothing to release
    assert 'fers-US-KY' not in got


def test_stable_fer_ids_and_carry_forward():
    s = {'refs': ['US-9', 'US-1'], 'kind': 'area', 'center': [37.123456, -85.987654]}
    assert KD.stable_id(s) == 'US-1+US-9@area@37.12,-85.99'
    old = [{'id': 'US-1+US-9@area@37.12,-85.99', 'refs': ['US-1', 'US-9'], 'kind': 'area', 'center': [37.1234, -85.9876]}]
    new = [{'refs': ['US-9', 'US-1'], 'kind': 'area', 'center': [37.1281, -85.9876]},      # moved ~0.5 km, rounds to 37.13
           {'refs': ['US-1', 'US-9'], 'kind': 'trail', 'center': [37.1234, -85.9876]}]     # other kind: never carried
    m = KD.carry_ids(old, new)
    assert m == {'US-1+US-9@area@37.13,-85.99': 'US-1+US-9@area@37.12,-85.99'}
    assert KD.carry_ids(old, [dict(new[0], center=[37.30, -85.99])]) == {}                  # 20 km away: a new spot


def test_line_order_freeze_and_done(club, tmp_path):
    L, D, O = club
    put(L / 'data/us-key/US-KY.json', {'updated': '2026-11-02', 'parks': {}})
    put(D / 'data/us-key/US-KY.json', {'updated': '2026-11-02', 'parks': {}})      # same bytes: live IS the build
    put(D / 'data/fers/US-KY.json', {'updated': '2026-11-02', 'spots': []})
    r = KD.task_line(L, D, O / 'key-doctor')
    by = {x['area']: x for x in r['areas']}
    assert [x['area'] for x in r['areas']][0] == 'US-KY'           # club order: Kentucky first
    assert by['US-KY']['stage'] == 'review' and by['US-KY']['done']
    assert by['US-KS']['stage'] == 'grade' and by['US-KS']['freeze']['sha']
    # the held copy changes while it is graded -> flagged, not silently re-graded
    put(D / 'data/waiting/in/data/us-key/US-KS.json', {'parks': {'US-5': park('changed')}})
    r2 = KD.task_line(L, D, O / 'key-doctor')
    ks = next(x for x in r2['areas'] if x['area'] == 'US-KS')
    assert ks['stage'] == 'grade' and 'CHANGED while chat 11 was grading' in ks['why']


def test_stuck_list_has_owners(club, monkeypatch):
    L, D, O = club
    r = KD.task_line(L, D, O / 'key-doctor')
    monkeypatch.setattr(KD, 'today', lambda: dt.date.today() + dt.timedelta(days=3))
    s = KD.task_stuck(r, O / 'key-doctor')
    assert s['stuck'] and s['stuck'][0]['owner'] == 'chat 11 (grader)'
    assert 'US-KS' in (O / 'key-doctor' / s['file']).read_text()


def test_size_guard_levels(tmp_path):
    assert KD.size_level(79 * KD.MIB) == 'OK' and KD.size_level(80 * KD.MIB) == 'WARN' and KD.size_level(95 * KD.MIB) == 'RED'
    assert KD.size_level(103_500_000) == 'RED'                      # US-AK.json.gz today: ~1.36 MB under GitHub's 100 MiB
    f = tmp_path / 'data/data/fers/US-AK.json.gz'; f.parent.mkdir(parents=True)
    with open(f, 'wb') as fh: fh.truncate(int(81 * KD.MIB))         # sparse file, no real disk use
    rules.load(set_=['key_doctor.size_red_mib=81'])
    r = KD.task_storage([tmp_path / 'data'], None, tmp_path / 'out')
    assert r['verdict'] == 'RED' and r['red'][0]['file'].endswith('US-AK.json.gz')
    assert KD.exit_code({'storage': r}) == 1


def test_superseded_held_copies_listed(club):
    L, D, O = club
    put(D / 'data/waiting/in/data/docs/US-KY.json', {'a': 1}); put(D / 'data/docs/US-KY.json', {'a': 1})
    r = KD.task_storage([D], D, O)
    assert [x['held'] for x in r['superseded_held']] == ['data/docs/US-KY.json']


def test_cli_doctor_reads_only_and_refuses_out_inside_data(club):
    import kpc_engine
    L, D, O = club
    snap = {p: p.read_bytes() for p in list(L.rglob('*')) + list(D.rglob('*')) if p.is_file()}
    rc = kpc_engine.main(['doctor', '--links', str(L), '--data', str(D), '--out', str(O)])
    assert rc == 1                                                  # NOs missing / came back = red
    assert (O / 'key-doctor/summary.json').exists() and list((O / 'key-doctor').glob('stuck-*.md'))
    assert all(p.read_bytes() == b for p, b in snap.items())       # nothing in either checkout changed
    assert kpc_engine.main(['doctor', '--links', str(L), '--data', str(D), '--out', str(D / 'x')]) == 2
    assert kpc_engine.main(['doctor', '--links', str(L), '--data', str(D), '--out', str(L / 'x')]) == 2


def test_key_doctor_switch_names_are_not_locked_and_default():
    assert rules.changed() == []
    assert rules.on('key_doctor.per_park_release') is False and rules.on('key_doctor.reapply_nos') is True
    for k in rules.DEFAULTS['key_doctor']:
        assert not rules.LOCKED_WORDS.search(k), k
