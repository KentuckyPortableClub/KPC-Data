#!/usr/bin/env python3
"""Nov 16: before a bot runs again, a held file used to be copied back in as the working copy,
and the step that keeps facts we already had then compared against that held (possibly damaged)
copy, so losses compounded. The keep-known comparison must read the LIVE (published) file, and
a held copy that failed its checks must not be handed to the bot as the starting file (safer
default; the owner can flip it). Offline: synthetic public test records only, nothing is
fetched, and nothing in the repo is written."""
import contextlib, importlib.util, io, json, os, pathlib, sys, tempfile

HERE = pathlib.Path(__file__).resolve().parent.parent
ok = True


def check(cond, msg):
    global ok
    print(('PASS ' if cond else 'FAIL ') + msg)
    ok = ok and bool(cond)


def load_wr(data):
    os.environ['DATA'] = str(data)
    os.environ['LINKS'] = str(data / 'nolinks')
    os.environ.pop('WAITING_RESUME_FAILED', None)
    spec = importlib.util.spec_from_file_location('wr_keep_live_' + data.name, HERE / '.github/scripts/kpc_waiting_room.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def quiet(fn, *a):
    b = io.StringIO()
    with contextlib.redirect_stdout(b):
        fn(*a)
    return b.getvalue()


def dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1) + '\n', encoding='utf-8')


def verdicts(*rows):
    return {'checked': '2026-11-16T12:00Z', 'switched_on': False, 'results': list(rows)}


# ------------------------------------------------------------------------------------------------ mode_resume
with tempfile.TemporaryDirectory(prefix='kpc-resume-live-') as t:
    R = pathlib.Path(t) / 'data_repo'
    live = {'camps': {'pine': {'name': 'Pine Camp', 'sites': {'total': 42}, 'facts_src': {'sites.total': {'url': 'https://example.test/pine', 'line': '42 sites'}}}}}
    held = {'camps': {'pine': {'name': 'Pine Camp', 'sites': {'total': None}, 'facts_src': {}, 'status': 'robots.txt says no'}}}
    dump(R / 'data/campinfo/US-ZZ.json', live)
    dump(R / 'data/waiting/in/data/campinfo/US-ZZ.json', held)
    dump(R / 'data/waiting/verdicts.json', verdicts({'path': 'data/campinfo/US-ZZ.json', 'kind': 'campinfo', 'verdict': 'HOLD', 'why': ['F-I6 1 -> 0'], 'notes': []}))
    W = load_wr(R)
    before = (R / 'data/campinfo/US-ZZ.json').read_text(encoding='utf-8')
    out = quiet(W.mode_resume, ['data/campinfo'])
    after = (R / 'data/campinfo/US-ZZ.json').read_text(encoding='utf-8')
    check(after == before, 'a held campinfo file that failed its checks is not copied over the live file')
    check((R / 'data/waiting/in/data/campinfo/US-ZZ.json').exists(), 'the failed held file stays in the waiting room (nothing is deleted)')
    check('started from live' in out and 'data/campinfo/US-ZZ.json' in out, f'resume says it started from live ({out.strip()[:200]})')
    check('1 held files taken' not in out and '0 held files taken as the working copy' in out, 'resume counts no failed file as the working copy')

with tempfile.TemporaryDirectory(prefix='kpc-resume-pass-') as t:
    R = pathlib.Path(t) / 'data_repo'
    live = {'camps': {'pine': {'name': 'Pine Camp', 'sites': {'total': 40}}}}
    held = {'camps': {'pine': {'name': 'Pine Camp', 'sites': {'total': 42}, 'facts_src': {'sites.total': {'url': 'https://example.test/pine', 'line': '42 sites'}}}}}
    dump(R / 'data/campinfo/US-ZZ.json', live)
    dump(R / 'data/waiting/in/data/campinfo/US-ZZ.json', held)
    dump(R / 'data/waiting/verdicts.json', verdicts({'path': 'data/campinfo/US-ZZ.json', 'kind': 'campinfo', 'verdict': 'PASS', 'why': [], 'notes': []}))
    W = load_wr(R)
    quiet(W.mode_resume, ['data/campinfo'])
    got = json.loads((R / 'data/campinfo/US-ZZ.json').read_text(encoding='utf-8'))
    check(got['camps']['pine']['sites']['total'] == 42, 'a held file that passed its checks is still the working copy')

with tempfile.TemporaryDirectory(prefix='kpc-resume-flip-') as t:
    R = pathlib.Path(t) / 'data_repo'
    live = {'camps': {'pine': {'name': 'Pine Camp', 'sites': {'total': 42}}}}
    held = {'camps': {'pine': {'name': 'Pine Camp', 'sites': {'total': None}, 'status': 'robots.txt says no'}}}
    dump(R / 'data/campinfo/US-ZZ.json', live)
    dump(R / 'data/waiting/in/data/campinfo/US-ZZ.json', held)
    dump(R / 'data/waiting/verdicts.json', verdicts({'path': 'data/campinfo/US-ZZ.json', 'kind': 'campinfo', 'verdict': 'HOLD', 'why': ['F-I6'], 'notes': []}))
    os.environ['WAITING_RESUME_FAILED'] = '1'
    W = load_wr(R)
    # load_wr pops the env, so set it after the module loads (the function reads it at call time)
    os.environ['WAITING_RESUME_FAILED'] = '1'
    quiet(W.mode_resume, ['data/campinfo'])
    got = json.loads((R / 'data/campinfo/US-ZZ.json').read_text(encoding='utf-8'))
    check(got['camps']['pine'].get('status') == 'robots.txt says no', 'WAITING_RESUME_FAILED=1 flips the default: a failed held copy is handed to the bot')
    os.environ.pop('WAITING_RESUME_FAILED', None)

with tempfile.TemporaryDirectory(prefix='kpc-resume-json-') as t:
    R = pathlib.Path(t) / 'data_repo'
    live = {'camps': {'pine': {'name': 'Pine Camp', 'sites': {'total': 42}}}}
    held = {'camps': {'pine': {'name': 'Pine Camp', 'sites': {'total': None}, 'status': 'robots.txt says no'}}}
    dump(R / 'data/campinfo/US-ZZ.json', live)
    dump(R / 'data/waiting/in/data/campinfo/US-ZZ.json', held)
    dump(R / 'data/waiting/verdicts.json', verdicts({'path': 'data/campinfo/US-ZZ.json', 'kind': 'campinfo', 'verdict': 'HOLD', 'why': ['F-I6'], 'notes': []}))
    dump(R / 'data/waiting/known/resume.json', {'resume_failed': True})
    W = load_wr(R)
    quiet(W.mode_resume, ['data/campinfo'])
    got = json.loads((R / 'data/campinfo/US-ZZ.json').read_text(encoding='utf-8'))
    check(got['camps']['pine'].get('status') == 'robots.txt says no', 'data/waiting/known/resume.json with resume_failed true also flips the default')

with tempfile.TemporaryDirectory(prefix='kpc-resume-fers-') as t:
    R = pathlib.Path(t) / 'data_repo'
    live = {'spots': []}
    held = {'spots': [{'id': 'x'}]}
    dump(R / 'data/fers/US-ZZ.json', live)
    dump(R / 'data/waiting/in/data/fers/US-ZZ.json', held)
    dump(R / 'data/waiting/verdicts.json', verdicts({'path': 'data/fers/US-ZZ.json', 'kind': 'fers', 'verdict': 'HOLD', 'why': ['F-S1'], 'notes': []}))
    W = load_wr(R)
    quiet(W.mode_resume, ['data/fers'])
    got = json.loads((R / 'data/fers/US-ZZ.json').read_text(encoding='utf-8'))
    check(got['spots'] == [{'id': 'x'}], 'a 2-fer file keeps today\'s resume behaviour (a held copy is still the working copy)')

# ------------------------------------------------------------------------------------------------ keep_known reads LIVE
TMP = tempfile.mkdtemp(prefix='kpc-keep-live-')
LIVE = tempfile.mkdtemp(prefix='kpc-keep-live-pub-')
os.environ['OUT'] = TMP
os.environ['LIVE_CAMPINFO'] = LIVE
os.environ.pop('DATA', None)
sys.path.insert(0, str(HERE / '.github' / 'scripts'))
import kpc_campinfo_bot as C  # noqa: E402

ROW = {'name': 'Pine Camp', 'lat': 36.1, 'lon': -85.2, 'park': 'Pine SP', 'agency': 'state', 'kind': 'campground', 'page': 'https://example.test/pine',
       'reserve': '', 'src': 'campstate', 'id': 'pine'}


def good():
    r = C.blank_record(ROW)
    C.apply_facts(r, {'sites.total': C.fact(42, 'https://example.test/pine', 'The campground has 42 sites'),
                      'dump_station': C.fact(True, 'https://example.test/pine', 'dump station on site')})
    r['status'] = 'ok'
    r['checked'] = '2026-09-01'
    return r


def empty_failed():
    r = C.blank_record(ROW)
    r['status'] = 'robots.txt says no'
    r['checked'] = '2026-11-15'
    r['ver'] = C.VER
    return r


# earlier_record: a damaged working copy loses to the live file
work = empty_failed()
pub = good()
picked = C.earlier_record(work, pub)
check(picked is pub and picked['sites']['total'] == 42, 'earlier_record reads the live file when the working copy lost its facts')
# working copy kept live facts and found another: keep the working copy
better = good()
C.apply_facts(better, {'showers': C.fact(True, 'https://example.test/pine', 'hot showers')})
check(C.earlier_record(better, pub) is better, 'earlier_record keeps a working copy that did not lose live facts (and may have found more)')
check(C.earlier_record(work, None) is work, 'earlier_record falls back to the working copy when there is no live record')

# the whole area loop: the working file is the damaged held copy; LIVE_CAMPINFO holds the published file
C.camp_rows = lambda area: {'pine': ROW}
C.one_camp = lambda area, r, state: empty_failed()
C.merge_duplicates = lambda D: None
held_file = {'area': 'US-ZZ', 'camps': {'pine': dict(empty_failed(), ver=C.VER)}}
pathlib.Path(TMP, 'US-ZZ.json').write_text(json.dumps(held_file), encoding='utf-8')
pathlib.Path(LIVE, 'US-ZZ.json').write_text(json.dumps({'area': 'US-ZZ', 'camps': {'pine': good()}}), encoding='utf-8')
C.run_area('US-ZZ', {'areas': {}})
D1 = json.loads(pathlib.Path(TMP, 'US-ZZ.json').read_text(encoding='utf-8'))
rec = D1['camps']['pine']
check(rec['sites']['total'] == 42 and rec['dump_station'] is True, 'run_area keeps the LIVE facts after a failed re-read, even when the working copy was an emptied held file')
check(rec.get('last_read_status') == 'robots.txt says no' and rec.get('checked') == '2026-09-01', 'the failed re-read is noted and the live checked date stays')
check(D1['counts'].get('kept_after_failed_read') == 1, f"counts say the live facts were kept after a failed read ({D1['counts'].get('kept_after_failed_read')})")

# without a live file the bot behaves as before (keeps the working record when it has facts, otherwise the failed read)
os.environ.pop('LIVE_CAMPINFO', None)
pathlib.Path(TMP, 'US-ZZ.json').write_text(json.dumps({'area': 'US-ZZ', 'camps': {'pine': dict(good(), ver=C.VER)}}), encoding='utf-8')
C.run_area('US-ZZ', {'areas': {}})
rec = json.loads(pathlib.Path(TMP, 'US-ZZ.json').read_text(encoding='utf-8'))['camps']['pine']
check(rec['sites']['total'] == 42, 'with no live file, a working copy that still has facts is kept (same as before)')

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
