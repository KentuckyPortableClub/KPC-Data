"""Nov 2 bot fixes: small offline checks for the 2-fer gate, the release gate and the hard look reader.
Run from the repo root:  python3 -m pytest -q .github/scripts/tests"""
import importlib.util, json, pathlib, subprocess, sys

S = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(S))


def mod(name):
    spec = importlib.util.spec_from_file_location(name, S / f'{name}.py')
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


G = mod('kpc_fers_gate')
H = mod('kpc_hardlook')
R = mod('kpc_release_approved')


# ---- 2-fer gate
def test_only_yes_fixed_pin_are_clean():
    for a in ('YES', '**YES** (chat 11, Nov 2): KEEP', 'FIXED by chat 2', 'PIN', 'Pin: held'):
        assert G.clean_answer(a), a
    for a in ('NO', 'NO (chat 11, Nov 2): PIN. two preserves', 'FIX (chat 11): chat 2 repairs', 'NOT SURE', 'YES/NO', '', None):
        assert not G.clean_answer(a), a


def test_pattern_answer_is_not_a_person_look():
    assert G.row_clean({'answer': 'YES'})
    assert not G.row_clean({'answer': 'YES', 'how': "pattern answer 'OFF bigger' (2026-11-02, sample US-1, US-2)"})


def test_gate_waits_for_unlisted_and_old_stamps_and_no_rows(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / 'data/parkinfo').mkdir(parents=True); (tmp_path / 'data/status').mkdir(parents=True)
    (tmp_path / 'data/waiting/questions').mkdir(parents=True)
    for a in ('US-TX', 'US-TN', 'US-ND', 'US-OH', 'US-KY'): (tmp_path / f'data/parkinfo/{a}.json').write_text('{}')
    # TX: old string stamp, no rows (looked 'clean' before). TN: listed, one NO. ND: listed, all YES. OH: listed, source down.
    (tmp_path / 'data/status/audited.json').write_text(json.dumps({'US-TX': '2026-11-01', 'US-TN': {'built': '2026-11-02', 'rows': 1, 'flagged': 1},
                                                                   'US-ND': {'built': '2026-11-02', 'rows': 1, 'flagged': 3}, 'US-OH': {'built': '2026-11-02', 'rows': 0}}))
    (tmp_path / 'data/waiting/questions/map-audit.json').write_text(json.dumps({'questions': [
        {'area': 'US-TN', 'ref': 'US-1', 'answer': 'NO (chat 11): wrong outline'}, {'area': 'US-ND', 'ref': 'US-2', 'answer': 'YES'}]}))
    (tmp_path / 'data/waiting/questions/map-audit-auto.json').write_text(json.dumps({'rows': [{'area': 'US-OH', 'auto': 'source down: the audit reads it again next run'}]}))
    monkeypatch.setattr(G, 'gh', lambda *a: (1, ''))
    monkeypatch.setattr(G.subprocess, 'run', lambda *a, **k: None)
    G.gate()
    st = json.load(open('data/status/fers-ready.json'))['areas']
    assert st['US-TX']['status'] == 'waiting for audit'
    assert st['US-KY']['status'] == 'waiting for audit'
    assert st['US-TN']['status'].startswith('waiting for audit answers (1 open, 1 answered NO')
    assert st['US-OH']['status'].startswith('waiting for audit answers (0 open, 1 source down')
    assert st['US-ND']['status'] == 'ready for 2-fers [1 of 3 flagged parks asked]'


def test_questions_stamps_listed_areas_with_their_own_date(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / 'data/waiting/questions').mkdir(parents=True)
    out = tmp_path / 'audit'; out.mkdir()
    (out / 'questions.json').write_text(json.dumps({'built': '2026-11-08', 'rules': 'x', 'areas': {'US-TX': {'built': '2026-11-07', 'asked': 0, 'flagged': 0}},
                                                    'questions': []}))
    (out / 'US-UT.json').write_text('{}')   # a file left from an old pass is NOT an audit of US-UT
    G.questions(out)
    A = json.load(open('data/status/audited.json'))
    assert A == {'US-TX': {'built': '2026-11-07', 'rows': 0, 'flagged': 0, 'source_down': 0, 'rules': 'x'}}


# ---- release gate (rule 22)
def test_cutoff():
    assert R.before_cutoff({'date': '2026-11-01'})
    assert R.before_cutoff({'date': '2026-11-02'})
    assert R.before_cutoff({'date': '2026-11-02', 'time': '9:36 AM'})
    assert not R.before_cutoff({'date': '2026-11-02', 'time': '9:37 AM'})
    assert not R.before_cutoff({'date': '2026-11-02', 'time': '2026-11-02 8:20 PM CST'})
    assert not R.before_cutoff({'date': '2026-11-02', 'time': '21:05'})
    assert R.before_cutoff({'date': '2026-11-02', 'time': '12:30 AM'})
    assert not R.before_cutoff({'date': '2026-11-03'})
    assert R.before_cutoff({})


def test_build_id_must_be_in_the_build_field_and_the_held_folder_needs_a_stamp(monkeypatch):
    monkeypatch.setattr(R, 'held_build', lambda kind: 'US-abc')
    assert R.build_mismatch({'what': 'us-key', 'chat11': 'KEY YES US-abc'}, 'data/us-key/')   # text only: refused
    assert R.build_mismatch({'what': 'us-key', 'build': 'US-old'}, 'data/us-key/')
    assert R.build_mismatch({'what': 'us-key', 'build': 'US-abc'}, 'data/us-key/') == ''
    monkeypatch.setattr(R, 'held_build', lambda kind: '')
    assert 'no build stamp' in R.build_mismatch({'what': 'world-key', 'build': 'W-1'}, 'data/world-key/')


def test_trust_ignores_old_no_change_and_auto_grades(monkeypatch):
    monkeypatch.setattr(R, 'item_kind', lambda it: it['k'])
    old = [{'k': 'campinfo', 'chat11': 'YES', 'date': '2026-11-01'}] * 5
    nochange = [{'k': 'trails', 'chat11': 'YES: nothing new, changed or gone', 'date': '2026-11-03'}] * 5
    auto = [{'k': 'truth', 'chat11': 'YES', 'by': 'auto (AUTO-1C)', 'date': '2026-11-03'}] * 5
    new = [{'k': 'docs', 'chat11': 'YES', 'date': '2026-11-02', 'time': '10:00 AM'}] * 3
    assert R.trusted_kinds(old + nochange + auto + new) == {'docs'}
    assert R.trusted_kinds(new + [{'k': 'docs', 'chat11': 'NO', 'date': '2026-11-03'}]) == set()


# ---- hard look reader
def test_redo_never_erases_an_answer():
    gap = {'result': 'record not found with that id / name'}
    assert H.redo(dict(gap))
    for a in ('NO PIN', 'PIN', 'NOT SURE', 'YES', 'NO'):
        assert not H.redo(dict(gap, answer=a)), a
    assert not H.redo(dict(gap, checked_by='chat 12'))


def test_keep_old_and_merge_rows():
    old = {'answer': 'NOT SURE', 'checked_by': 'chat 12', 'decision': 'ask Brandon'}
    q = {'ref': 'CA-1', 'answer': '', 'checked_by': '', 'result': 'record found'}
    out = H.keep_old(old, q)
    assert out['answer'] == 'NOT SURE' and out['checked_by'] == 'chat 12' and out['decision'] == 'ask Brandon' and out['result'] == 'record found'
    mine = {'CA-1': {'answer': '', 'result': 'record found'}, 'CA-2': {'answer': 'YES'}}
    theirs = {'CA-1': {'answer': 'NO PIN', 'how': 'chat 11 looked at the map', 'extra': 1}, 'CA-2': {'answer': ''}, 'CA-3': {'answer': 'YES'}}
    assert H.merge_rows(mine, theirs) == 2
    assert mine['CA-1'] == {'answer': 'NO PIN', 'result': 'record found', 'how': 'chat 11 looked at the map', 'extra': 1}
    assert mine['CA-2']['answer'] == 'YES' and mine['CA-3'] == {'answer': 'YES'}


def test_merge_main_reads_origin_main(tmp_path, monkeypatch):
    up = tmp_path / 'up'; up.mkdir()
    def git(*a, cwd): subprocess.run(['git', *a], cwd=cwd, check=True, capture_output=True)
    git('init', '-q', '-b', 'main', cwd=up); git('config', 'user.email', 't@t', cwd=up); git('config', 'user.name', 't', cwd=up)
    (up / 'data/waiting/questions').mkdir(parents=True)
    (up / 'data/waiting/questions/hardlook.json').write_text(json.dumps({'rows': {'CA-1': {'answer': ''}}}))
    git('add', '-A', cwd=up); git('commit', '-qm', 'a', cwd=up)
    me = tmp_path / 'me'; git('clone', '-q', str(up), str(me), cwd=tmp_path)
    (up / 'data/waiting/questions/hardlook.json').write_text(json.dumps({'rows': {'CA-1': {'answer': 'NO PIN', 'checked_by': 'chat 11'}}}))
    git('commit', '-qam', 'chat 11 answers', cwd=up)
    (me / 'data/waiting/questions/hardlook.json').write_text(json.dumps({'rows': {'CA-1': {'answer': '', 'result': 'record found'}}}))
    monkeypatch.chdir(me)
    assert H.merge_main() == 0
    row = H.load('data/waiting/questions/hardlook.json', {})['rows']['CA-1']
    assert row == {'answer': 'NO PIN', 'result': 'record found', 'checked_by': 'chat 11'}
