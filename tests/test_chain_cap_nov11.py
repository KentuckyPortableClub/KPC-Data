#!/usr/bin/env python3
"""Offline test, Nov 11 2026 (fewer runs): the hard look reader and the outside documents merge no longer start hundreds of runs.
  1. kpc_chain.decide: a next run only when rows are left AND the run made progress AND the chain is under its cap AND the 24 h
     brake count could be read and is under the brake AND the bot is not paused; every stop says why in one line.
  2. the hard look reader with a stand-in network (urllib under kpc_manners is replaced; a fake clock: 60 s a request):
     a backlog larger than one run's budget is drained across capped continuations; cap reached = stop with the note, the next
     day's cron goes on; rows that only wait on a host (robots.txt unreadable) = no progress = no next run;
     a row on a never-contact host gets ZERO requests (robots.txt included), is recorded 'blocked host: needs a saved copy', is
     not retried, does not hold the queue, and is read again only when its layer address changes;
     a run stopped part way (Ctrl-C, or the stop signal's SystemExit) keeps every row it read; no pin is ever moved.
  3. the workflows' own shell (the Read / Next run steps, run with bash -e -o pipefail) with stand-in scripts
     (stricter than GitHub's default bash -e) chunks stop on no progress, progress is saved after each chunk, the continuation passes chain+1, the cap / an unreadable
     run count / no progress start nothing; the docs merge, still paused, starts nothing. No cron added or changed.
Zero live network: every request in part 2 goes to the stand-in; nothing else opens a socket."""
import contextlib, gzip, io, json, os, pathlib, re, shutil, stat, subprocess, sys, tempfile, urllib.error, urllib.parse, urllib.request
import yaml

HERE = pathlib.Path(__file__).resolve().parent.parent
SCRIPTS = HERE / '.github/scripts'
sys.path.insert(0, str(SCRIPTS))
ok = True


def check(c, m):
    global ok
    print(('PASS ' if c else 'FAIL ') + m, flush=True); ok = ok and bool(c)


import kpc_chain as C   # noqa: E402

# ---------------------------------------------------------------- 1. the rule
NB = 'the daily cron continues tomorrow'
go, n, line = C.decide(10, 4, 0, 3, runs24=1, brake=6, next_by=NB)
check(go and n == 1 and 'continuation 1 of 3' in line, f'rows left + progress + under the cap = one more run, chain 1 ({line})')
go, n, line = C.decide(10, 4, 3, 3, runs24=1, brake=6, next_by=NB)
check(not go and 'backlog 10 left, cap reached' in line and NB in line, f'cap reached = stop with the note ({line})')
go, n, line = C.decide(10, 0, 0, 3, runs24=1, brake=6, next_by=NB)
check(not go and 'no progress' in line, f'no progress = no next run ({line})')
go, n, line = C.decide(0, 9, 0, 3, next_by=NB)
check(not go and 'drained' in line, f'nothing left = no next run ({line})')
go, n, line = C.decide(10, 4, 0, 3, runs24='', brake=6, next_by=NB)
check(not go and 'fail closed' in line, f'a run count that cannot be read = no next run ({line})')
go, n, line = C.decide(10, 4, 0, 3, runs24=6, brake=6, next_by=NB)
check(not go and 'brake 6' in line, f'6 runs in 24 h = brake ({line})')
go, n, line = C.decide(10, 4, 0, 3, paused=True)
check(not go and 'PAUSED' in line, f'a paused bot starts nothing ({line})')
go, n, line = C.decide('', 4, 0, 3)
check(not go, 'LEFT not readable = no next run')

# ---------------------------------------------------------------- 2. the reader with a stand-in network
BLOCKED_URLS = ['https://services3.arcgis.com/abc/arcgis/rest/services/Parks/FeatureServer/0',
                'https://services-eu1.arcgis.com/xyz/arcgis/rest/services/P/FeatureServer/2',
                'https://services.arcgis.com/33TOOklri9xpic7U/arcgis/rest/services/Parcels/FeatureServer/0',
                'https://apps.fs.usda.gov/arcx/rest/services/EDW/EDW_Admin/MapServer/1',
                'https://ncnhde.natureserve.org/arcgis/rest/services/NHP/MapServer/3']
BLOCKED_HOSTS = {urllib.parse.urlsplit(u).hostname for u in BLOCKED_URLS}
OKURL = 'https://gis.example.org/arcgis/rest/services/Parks/MapServer/0'
DOWN = 'https://down.example.org/arcgis/rest/services/Parks/MapServer/0'


class Clock:
    t = 1_900_000_000.0

    def time(self): return self.t

    def strftime(self, *a): return __import__('time').strftime(*a)


CLOCK = Clock()
CALLS = []          # every url the stand-in network was asked for
STOP = {}           # {'after': n, 'exc': exception} to stop a run part way


class Resp(io.BytesIO):
    def __init__(self, body, url):
        super().__init__(body); self.status = 200; self.headers = {'Content-Type': 'application/json'}; self._u = url

    def geturl(self): return self._u

    def __enter__(self): return self

    def __exit__(self, *a): self.close()


def fake_urlopen(req, timeout=None, **k):
    u = req.full_url if hasattr(req, 'full_url') else str(req)
    CALLS.append(u)
    host = urllib.parse.urlsplit(u).hostname
    if u.endswith('/robots.txt'):
        if host == 'down.example.org': raise urllib.error.URLError('stand-in: no route')
        raise urllib.error.HTTPError(u, 404, 'none', {}, None)
    CLOCK.t += 60   # one layer answer = one minute of the run's budget
    q = sum(1 for x in CALLS if not x.endswith('/robots.txt'))
    if STOP.get('after') and q >= STOP['after']: raise STOP['exc']
    p = dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(u).query))
    oid = int(re.search(r'\d+', p.get('where', '0')).group())
    lat, lon = 37.0 + oid / 1000, -85.0
    d = 0.05 if oid >= 9000 else 0.0   # 9000+ = a record ~5 km from the pin (the R-G13 'PIN OFF' case)
    ring = [[lon - .002 + d, lat - .002], [lon + .002 + d, lat - .002], [lon + .002 + d, lat + .002], [lon - .002 + d, lat + .002], [lon - .002 + d, lat - .002]]
    return Resp(json.dumps({'features': [{'attributes': {'OBJECTID': oid, 'NAME': f'Park {oid}'}, 'geometry': {'rings': [ring]}}]}).encode(), u)


urllib.request.urlopen = fake_urlopen
import kpc_hardlook as H   # noqa: E402
H.time = CLOCK
H.M.gap = 0.0


def rows_file(td, rows):
    p = td / 'data/intake/_in/hardlook/hardlook-test.json'; p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({'rows': rows}, indent=1)); return p


def row(i, url=OKURL, st='ZZ', notes=''):
    return {'status': 'GIS FOUND', 'url': url, 'field': 'NAME', 'record': f'OBJECTID {i}', 'name': f'Park {i}', 'st': st,
            'lat': 37.0 + i / 1000, 'lon': -85.0, 'notes': notes}


def run_once(minutes=40):
    """One reader process with a fresh budget (what one workflow run's single chunk does). -> (LEFT, DONE, log)"""
    H.T0 = CLOCK.t; H.LIMIT = minutes * 60
    H.M = H.Manners('test'); H.M.gap = 0.0   # a new process = a new Manners
    out = io.StringIO()
    with contextlib.redirect_stdout(out): H.main()
    s = out.getvalue()
    g = lambda k: int((re.search(rf'^{k}=(\d+)', s, re.M) or [0, -1])[1])
    return g('LEFT'), g('DONE'), s


def questions(td): return json.load(gzip.open(td / 'data/waiting/questions/hardlook.json.gz'))['rows']


def chain_day(td, cap=3):
    """One day: the cron run (chain 0), then continuations while kpc_chain says so. -> (runs, last line)"""
    chain, runs = 0, 0
    while True:
        left, done, _ = run_once(); runs += 1
        go, chain2, line = C.decide(left, done, chain, cap, next_by=NB)
        if not go: return runs, line, left
        chain = chain2


cwd = os.getcwd()
with tempfile.TemporaryDirectory() as t:
    td = pathlib.Path(t); os.chdir(td)
    # a) 300 rows, ~41 a run: day 1 = 1 + 3 continuations, then the cap; day 2 finishes
    rows_file(td, {f'US-{i:04d}': row(i) for i in range(1, 301)})
    CALLS.clear()
    runs, line, left = chain_day(td)
    read1 = sum(1 for q in questions(td).values() if q.get('read'))
    check(runs == 4 and 'cap reached' in line and NB in line and left == 300 - read1 and read1 == 164,
          f'backlog larger than a run: day 1 = 4 runs (cron + 3 continuations), {read1} read, then stop: "{line}"')
    runs2, line2, left2 = chain_day(td)
    read2 = sum(1 for q in questions(td).values() if q.get('read'))
    check(read2 == 300 and left2 == 0 and 'drained' in line2 and runs2 == 4, f'day 2 drains the rest in {runs2} runs ("{line2}")')
    qcalls = [u for u in CALLS if not u.endswith('/robots.txt')]
    check(len(qcalls) == 300, f'each row asked once ({len(qcalls)} layer requests for 300 rows)')
    check(all(q.get('result') == 'record found' for q in questions(td).values()), 'every row: record found')
    shutil.rmtree(td / 'data')

    # b) rows that only wait on a host: no progress, no next run, no layer request
    rows_file(td, {f'US-{i:04d}': row(i, DOWN) for i in range(1, 21)})
    CALLS.clear()
    left, done, log = run_once()
    go, _, line = C.decide(left, done, 0, 3, next_by=NB)
    check(left == 20 and done == 0 and not go and 'no progress' in line, f'robots.txt unreadable for every row: LEFT {left}, DONE {done}, no next run ("{line}")')
    check([u for u in CALLS if not u.endswith('/robots.txt')] == [] and 'WAITING=20' in log, 'no layer request to a host whose robots.txt could not be read; WAITING=20')
    shutil.rmtree(td / 'data')

    # c) never-contact hosts: zero requests (robots.txt included), visible record, not retried, does not hold the queue
    R0 = {f'CA-{i:04d}': row(i, u, st='AA') for i, u in enumerate(BLOCKED_URLS, 1)}
    R0.update({f'US-{i:04d}': row(i) for i in range(100, 110)})
    rows_file(td, R0)
    CALLS.clear()
    left, done, log = run_once()
    Q = questions(td)
    hit = sorted({urllib.parse.urlsplit(u).hostname for u in CALLS} & BLOCKED_HOSTS)
    check(hit == [], f'zero requests of any kind (robots.txt included) to the never-contact hosts: {hit}')
    blk = [Q[f'CA-{i:04d}'] for i in range(1, len(BLOCKED_URLS) + 1)]
    check(all(str(q.get('result')).startswith('blocked host: needs a saved copy') and q.get('read') and q.get('blocked_host') for q in blk),
          'each blocked row is recorded "blocked host: needs a saved copy (...)", read, with its host')
    check(all(Q[f'US-{i:04d}'].get('result') == 'record found' for i in range(100, 110)) and left == 0,
          f'the rows after them are read in the same run (the queue is not held): LEFT {left}')
    check('blocked host: needs a saved copy 5' in log, 'the run\'s notice counts the blocked rows')
    CALLS.clear()
    left, done, _ = run_once()
    check(CALLS == [] and done == 0 and left == 0, 'next run: a blocked row is not retried (no request, no progress, nothing left)')
    R0['CA-0001'] = row(1, OKURL, st='AA')   # research sends a usable layer for that park
    rows_file(td, R0)
    CALLS.clear()
    left, done, _ = run_once()
    q1 = questions(td)['CA-0001']
    check(done == 1 and q1.get('result') == 'record found' and not q1.get('blocked_host') and len(CALLS) >= 1,
          'a blocked row whose layer address changes is read again (once)')
    check(not ({urllib.parse.urlsplit(u).hostname for u in CALLS} & BLOCKED_HOSTS), 'still no request to a blocked host')
    shutil.rmtree(td / 'data')
    # an older row (read before Nov 10) waiting to be asked again by place + name, on a host that is now blocked
    rows_file(td, {'CA-0042': row(42, BLOCKED_URLS[0])})
    qf = td / 'data/waiting/questions/hardlook.json.gz'; qf.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(qf, 'wt') as f: json.dump({'rows': {'CA-0042': dict(row(42, BLOCKED_URLS[0]), read='2026-11-01', reread='2026-11-02', result='record not found with that id / name', answer='')}}, f)
    CALLS.clear()
    left, done, _ = run_once()
    q = questions(td)['CA-0042']
    check(CALLS == [] and str(q.get('reask_result', '')).startswith('not asked again: blocked host: needs a saved copy') and left == 0 and done == 1,
          f'the place + name re-ask makes no request to a blocked host either and says so ({q.get("reask_result")})')
    shutil.rmtree(td / 'data')

    # d) a run stopped part way keeps what it read (Ctrl-C, and the SystemExit the stop signal raises)
    for exc, name in ((KeyboardInterrupt(), 'Ctrl-C'), (SystemExit(143), 'the stop signal')):
        rows_file(td, {f'US-{i:04d}': row(i) for i in range(1, 101)})
        CALLS.clear(); STOP.update(after=15, exc=exc)
        stopped = False
        try: run_once()
        except (KeyboardInterrupt, SystemExit): stopped = True
        STOP.clear()
        n_read = sum(1 for q in questions(td).values() if q.get('read'))
        check(stopped and n_read == 14, f'{name} on the 15th request: the 14 rows read before it are on disk ({n_read})')
        left, done, _ = run_once()
        check(done > 0 and sum(1 for q in questions(td).values() if q.get('read')) == 14 + done, f'{name}: the next run goes on from row 15')
        shutil.rmtree(td / 'data')
    check('signal.SIGTERM' in (SCRIPTS / 'kpc_hardlook.py').read_text(), 'the reader turns the stop signal into a normal exit (its save runs)')

    # e) the POTA pin never moves: R-G13 lists a typo, the input rows and pins are untouched
    pf = rows_file(td, {'US-9001': row(9001, notes='PIN OFF per the agency map')})
    before = pf.read_bytes()
    run_once()
    P = json.load(gzip.open(td / 'data/waiting/questions/pin-typos.json.gz'))['rows']
    check(P.get('US-9001', {}).get('pota_pin') == [37.0 + 9001 / 1000, -85.0], 'R-G13: the pin typo is listed with the POTA pin as given')
    files = sorted(str(p.relative_to(td)) for p in td.rglob('*') if p.is_file())
    check(pf.read_bytes() == before and all(f.startswith('data/waiting/questions/') or f == str(pf.relative_to(td)) for f in files),
          f'the reader wrote only its question files (no pin file touched): {files}')
    os.chdir(cwd)

# ---------------------------------------------------------------- 3. the workflows' own shell
def steps(wf):
    d = yaml.safe_load((HERE / '.github/workflows' / wf).read_text(encoding='utf-8'))
    return d, {s.get('name'): s for j in d['jobs'].values() for s in j['steps']}


def stub_tree(td, seq):
    sc = td / 'kpcdata/.github/scripts'; sc.mkdir(parents=True)
    (td / 'links/.github/scripts').mkdir(parents=True)
    (td / 'seq.json').write_text(json.dumps(seq))
    for f in ('kpc_intake_reader.py', 'kpc_status.py', 'kpc_waiting_room.py'): (sc / f).write_text('import sys; sys.exit(0)\n')
    body = ("import json, sys, pathlib\nif sys.argv[1:2] == ['merge-main']: sys.exit(0)\np = pathlib.Path(%r)\ns = json.loads(p.read_text())\n"
            "l, d = s.pop(0); p.write_text(json.dumps(s)); print('LEFT=%%d' %% l); print('DONE=%%d' %% d); print('WAITING=0')\n") % str(td / 'seq.json')
    (sc / 'kpc_hardlook.py').write_text(body); (sc / 'kpc_docs_merge.py').write_text(body)
    shutil.copy(SCRIPTS / 'kpc_chain.py', sc / 'kpc_chain.py')
    (td / 'links/.github/scripts/kpc_push_data.sh').write_text(f'echo "$2" >> {td}/saves.txt\n')
    b = td / 'bin'; b.mkdir()
    (b / 'gh').write_text(f'#!/bin/bash\necho "$*" >> {td}/gh.txt\nif [ "$1" = api ]; then [ -f {td}/api-fails ] && exit 1; echo 2; fi\nexit 0\n')
    (b / 'gh').chmod(0o755)
    (b / 'pip').write_text('#!/bin/bash\nexit 0\n'); (b / 'pip').chmod(0o755)


def sh(td, script, env):
    e = dict(os.environ, PATH=f"{td / 'bin'}:{os.environ['PATH']}", GITHUB_OUTPUT=str(td / 'out.txt'), RUNNER_TEMP=str(td),
             GITHUB_STEP_SUMMARY=str(td / 'sum.txt'), **{k: str(v) for k, v in env.items()})
    r = subprocess.run(['bash', '--noprofile', '--norc', '-eo', 'pipefail', '-c', script], cwd=td, env=e, capture_output=True, text=True, timeout=60)
    return r.returncode, r.stdout + r.stderr


def outputs(td):
    return dict(l.split('=', 1) for l in (td / 'out.txt').read_text().split('\n') if '=' in l) if (td / 'out.txt').exists() else {}


for wf, read_name, next_name in (('kpc-hardlook.yml', 'Read', 'Next run'), ('kpc-docs-merge.yml', 'Merge (held in the waiting room)', 'Straight through')):
    d, S = steps(wf)
    ok_expr = all('${{' not in (S[n].get('run') or '') for n in (read_name, next_name))
    check(ok_expr, f'{wf}: the Read / Next steps take every value through env (no expression inside the shell)')
    renv = {k: v for k, v in (S[read_name].get('env') or {}).items()}
    with tempfile.TemporaryDirectory() as t:
        td = pathlib.Path(t); stub_tree(td, [[100, 20], [80, 20], [80, 0], [80, 50]])
        rc, log = sh(td, S[read_name]['run'], dict(renv, LINKS='../links'))
        o = outputs(td); saves = (td / 'saves.txt').read_text().count('\n') if (td / 'saves.txt').exists() else 0
        check(rc == 0 and o.get('left') == '80' and o.get('done') == '40' and json.loads((td / 'seq.json').read_text()) == [[80, 50]],
              f'{wf}: chunks stop at the first chunk that did nothing (3 chunks; left 80, done 40) rc={rc} {o} {log[-300:] if rc else ""}')
        check(saves == 3, f'{wf}: saved after each chunk that did something, and once at the end ({saves} saves)')
    with tempfile.TemporaryDirectory() as t:
        td = pathlib.Path(t); stub_tree(td, [[0, 7]])
        rc, log = sh(td, S[read_name]['run'], dict(renv, LINKS='../links'))
        check(rc == 0 and outputs(td).get('left') == '0', f'{wf}: an emptied backlog ends the run after one chunk')
    nenv = {k: v for k, v in (S[next_name].get('env') or {}).items() if '${{' not in str(v)}
    paused = str(nenv.get('PAUSED', '0')) == '1'
    for case, extra, want in (('progress', {'LEFT': 80, 'DONE': 40, 'CHAIN': 0}, 'start'), ('cap', {'LEFT': 80, 'DONE': 40, 'CHAIN': 3}, 'cap reached'),
                              ('no progress', {'LEFT': 80, 'DONE': 0, 'CHAIN': 0}, 'no progress'), ('count unreadable', {'LEFT': 80, 'DONE': 40, 'CHAIN': 1}, 'fail closed')):
        with tempfile.TemporaryDirectory() as t:
            td = pathlib.Path(t); stub_tree(td, [])
            if case == 'count unreadable': (td / 'api-fails').write_text('x')
            rc, log = sh(td, S[next_name]['run'], dict(nenv, R='KentuckyPortableClub/KPC-Data', **extra))
            gh = (td / 'gh.txt').read_text() if (td / 'gh.txt').exists() else ''
            started = [l for l in gh.split('\n') if l.startswith('workflow run')]
            if paused:
                check(rc == 0 and not started and ('PAUSED' in log or 'nothing left' in log or 'no progress' in log or 'cap reached' in log),
                      f'{wf} (paused) {case}: no run started')
            elif want == 'start':
                check(rc == 0 and len(started) == 1 and '-f chain=1' in started[0], f'{wf} {case}: one next run, chain=1 ({started})')
            else:
                check(rc == 0 and not started and want in log, f'{wf} {case}: no next run, the log says "{want}"')

# ---------------------------------------------------------------- the files themselves
base = 'origin/main' if subprocess.run(['git', 'rev-parse', '-q', '--verify', 'origin/main'], cwd=HERE, capture_output=True).returncode == 0 else 'HEAD~1'
for wf in ('kpc-hardlook.yml', 'kpc-docs-merge.yml'):
    now = yaml.safe_load((HERE / '.github/workflows' / wf).read_text(encoding='utf-8'))
    old = yaml.safe_load(subprocess.run(['git', 'show', f'{base}:.github/workflows/{wf}'], cwd=HERE, capture_output=True, text=True).stdout or '{}') or {}
    on, on0 = now.get(True) or {}, old.get(True) or {}
    check(on.get('schedule') == on0.get('schedule') and 'workflow_dispatch' in on and 'chain' in ((on.get('workflow_dispatch') or {}).get('inputs') or {}),
          f'{wf}: schedule unchanged vs {base}, by hand kept, input chain added')
    check(all(not j.get('if') for j in now['jobs'].values()), f'{wf}: no job-level if (a start always has a job)')
    check([j.get('timeout-minutes') for j in now['jobs'].values()] == [j.get('timeout-minutes') for j in (old.get('jobs') or {}).values()], f'{wf}: job timeout unchanged')
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
