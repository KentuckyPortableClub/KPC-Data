#!/usr/bin/env python3
"""Nov 17 (storage): a waiting-room check WITHOUT the network must not flip files that the last
networked check already judged. Before: every docs file went PASS -> HOLD 'needs the network' and
back, about 1,400 change-log lines and 40 one-MB saves a day. Also: the change log is one small
file a day now, and the morning list reads the old log plus the daily files.
Offline: a temp waiting room only, judge() is stood in for; nothing in the repo is written."""
import importlib.util, json, os, pathlib, sys, tempfile

HERE = pathlib.Path(__file__).resolve().parent.parent
ok = True


def check(c, msg):
    global ok
    print(('PASS ' if c else 'FAIL ') + msg); ok = ok and bool(c)


def load_mod(data, name, net):
    os.environ['DATA'] = str(data); os.environ['LINKS'] = str(data / 'nolinks')
    if net: os.environ['NET'] = '1'
    else: os.environ.pop('NET', None)
    os.environ.pop('WAITING_ON', None)
    sys.path.insert(0, str(HERE / '.github' / 'scripts'))
    path = HERE / '.github' / 'scripts' / (name + '.py')
    spec = importlib.util.spec_from_file_location(f'{name}_{data.name}_{int(net)}_{len(sys.modules)}', path)
    M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
    return M


NETLESS = 'F-4 unsure: link re-test needs the network (NET=1): not run, so the file waits'
EXTRA = []   # a reason the stand-in judge adds on demand


def run(data, net):
    M = load_mod(data, 'kpc_waiting_room', net)
    def judge(path, new, live, twin=None, ctx=None):
        if M.NET: return {'path': path, 'kind': 'docs', 'verdict': 'PASS', 'why': [], 'notes': ['F-D3 retest 20 links: 20 ok']}
        return {'path': path, 'kind': 'docs', 'verdict': 'HOLD', 'why': [NETLESS] + list(EXTRA), 'notes': []}
    M.judge = judge
    M.mode_tidy = lambda: None
    M.grade_queue = lambda rows: None
    try: M.mode_check(False)
    except SystemExit: pass
    return M


def rows(data):
    return {r['path']: r for r in json.load(open(data / 'data/waiting/verdicts.json'))['results']}


def log_lines(data):
    T = load_mod(data, 'kpc_waiting_today', False)
    return T.verdict_rows()


data = pathlib.Path(tempfile.mkdtemp(prefix='kpc-netless-'))
inn = data / 'data/waiting/in/data/docs'; inn.mkdir(parents=True)
f = inn / 'US-MI.json'; f.write_text(json.dumps({'parks': {'US-1': {'url': 'https://x.example/a'}}}))
rel = 'data/docs/US-MI.json'

run(data, True)
r = rows(data)[rel]
check(r['verdict'] == 'PASS' and r.get('net') is True and r.get('fp'), 'networked check: PASS, marked net + fingerprint')
n1 = len(log_lines(data))
check(n1 == 1, f'one change-log line after the first check (got {n1})')
check((data / 'data/waiting/verdicts-log').is_dir() and not (data / 'data/waiting/verdicts.jsonl.gz').exists(), 'the line went to the daily log file, not the old single log')
last1 = (data / 'data/waiting/verdicts-last.json').read_bytes()

run(data, False)
r = rows(data)[rel]
check(r['verdict'] == 'PASS' and r['why'] == [] and r.get('net') is True, 'no-network check, same file: the networked PASS is kept (no flip to HOLD)')
check(len(log_lines(data)) == n1, 'no new change-log line for it')
check((data / 'data/waiting/verdicts-last.json').read_bytes() == last1, 'verdicts-last.json is byte-for-byte the same')

EXTRA.append('F-D1 a new real problem')
run(data, False)
r = rows(data)[rel]
check(r['verdict'] == 'HOLD' and 'F-D1 a new real problem' in r['why'], 'no-network check that finds a NEW reason: shown at once, not hidden by the old PASS')
EXTRA.clear()

run(data, True)
f.write_text(json.dumps({'parks': {'US-1': {'url': 'https://x.example/CHANGED'}}}))
run(data, False)
r = rows(data)[rel]
check(r['verdict'] == 'HOLD' and r['why'] == [NETLESS], 'the waiting file changed: no row kept, it waits for the network as before')

g = inn / 'US-ZZ.json'; g.write_text('{"parks": {}}')
run(data, False)
r = rows(data)['data/docs/US-ZZ.json']
check(r['verdict'] == 'HOLD', 'a file never checked with the network still waits')

# a live copy that changes also breaks the keep
run(data, True)
live = data / 'data/docs'; live.mkdir(parents=True, exist_ok=True); (live / 'US-MI.json').write_text('{"parks": {"US-9": {}}}')
run(data, False)
check(rows(data)[rel]['verdict'] == 'HOLD', 'the LIVE copy changed: no row kept')

# old single log is still read, before the daily files
(data / 'data/waiting/verdicts.jsonl').write_text(json.dumps({'date': '2026-11-01T00:00Z', 'path': 'old', 'verdict': 'PASS'}) + '\n')
L = log_lines(data)
check(L and L[0].get('path') == 'old' and len(L) > 1, 'the morning list reads the old log first, then the daily files')

# a promoting run never keeps rows
M = load_mod(data, 'kpc_waiting_room', False)
src = (HERE / '.github/scripts/kpc_waiting_room.py').read_text()
check('if not NET and not on:' in src, 'rows are kept only on a run that cannot promote')

print('ALL PASS' if ok else 'SOME FAILED'); sys.exit(0 if ok else 1)
