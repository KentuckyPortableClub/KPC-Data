#!/usr/bin/env python3
"""Nov 10 2026 (quiet runs), KPC-Data side. Offline. Checks: every workflow parses; NO new schedule entry versus main (a changed cron
is never more frequent); the Pages copy moves 'site' only for a change the site reads, never over a running Pages build, is
hourly, keeps its concurrency, and is green when it has nothing to do; the quiet-save gate (bookkeeping only + saved recently =
skip; material / alarm = save); the flow board and Europe weather skip same-content saves; the stamp filter still skips stamp-only
saves; fail-safe is narrowed for retry / scoreboard / storage; the storage keeper keeps its ONE intentional red step and a
measure that errored cannot reach it."""
import json, os, pathlib, re, subprocess, sys, tempfile
import yaml

HERE = pathlib.Path(__file__).resolve().parent.parent
WFD = HERE / '.github/workflows'
WF = sorted(WFD.glob('*.yml'))
ok = True


def check(c, m):
    global ok
    print(('PASS ' if c else 'FAIL ') + m); ok = ok and bool(c)


def on_of(d):
    on = d.get(True, d.get('on')) or {}
    if isinstance(on, str): on = {on: None}
    if isinstance(on, list): on = {k: None for k in on}
    return on


def crons(d): return [x.get('cron') for x in (on_of(d).get('schedule') or [])]


def per_day(cron):
    m, h, dom, mon, dow = cron.split()
    def n(field, size):
        out = 0
        for part in field.split(','):
            if part == '*': out += size
            elif part.startswith('*/'): out += len(range(0, size, int(part[2:])))
            elif '-' in part: a, b = part.split('-')[:2]; out += int(b) - int(a) + 1
            else: out += 1
        return out
    f = n(m, 60) * n(h, 24)
    if dom != '*': f *= n(dom, 31) / 30.4
    if dow != '*': f *= n(dow, 7) / 7
    if mon != '*': f *= n(mon, 12) / 12
    return f


def git(*a, cwd=HERE): return subprocess.run(['git', *a], capture_output=True, text=True, cwd=cwd)


ENV = dict(os.environ, GIT_CONFIG_GLOBAL='/dev/null', GIT_AUTHOR_NAME='t', GIT_AUTHOR_EMAIL='t@t', GIT_COMMITTER_NAME='t', GIT_COMMITTER_EMAIL='t@t')


def sh(cmd, cwd, env=None): return subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, env=dict(ENV, **(env or {})))


def step_run(doc, part):
    for job in doc['jobs'].values():
        for s in job['steps']:
            if part in (s.get('name') or ''): return s
    raise KeyError(part)


# 1. every workflow parses
docs, bad = {}, []
for f in WF:
    try:
        d = yaml.safe_load(f.read_text(encoding='utf-8')); assert isinstance(d, dict) and d.get('jobs') and on_of(d)
        docs[f.name] = d
    except Exception as e: bad.append(f'{f.name}: {str(e)[:120]}')  # noqa: BLE001
check(not bad, f'all {len(WF)} workflow files parse and have triggers and jobs {bad[:3]}')

# 2. no new schedule versus main
base = os.environ.get('KPC_BASE_REF', 'origin/main')
if git('rev-parse', '--verify', '-q', base + '^{commit}').returncode != 0:
    print(f'NOTE no {base} in this checkout: the schedule comparison is skipped here')
else:
    new_files, grew, more = [], [], []
    for name, d in docs.items():
        r = git('show', f'{base}:.github/workflows/{name}'); mine = crons(d)
        if r.returncode != 0:
            if mine: new_files.append(name)
            continue
        try: theirs = crons(yaml.safe_load(r.stdout) or {})
        except Exception: theirs = []  # noqa: BLE001
        if len(mine) > len(theirs): grew.append(name)
        added = [c for c in mine if c not in theirs]
        if added and sum(per_day(c) for c in mine) > sum(per_day(c) for c in theirs) + 1e-9: more.append(name)
    check(not new_files and not grew, f'no new schedule entry versus {base} {new_files + grew}')
    check(not more, f'a changed cron fires no more often than before {more}')

# 3. the Pages copy
ps = docs['kpc-pages-sync.yml']
check(ps.get('concurrency', {}).get('group') == 'kpc-pages-sync' and ps['concurrency'].get('cancel-in-progress') is False, 'kpc-pages-sync.yml: concurrency kept (one at a time, none cancelled)')
check(crons(ps) == ['9 * * * *'], f'kpc-pages-sync.yml: hourly (was 3 a time an hour) {crons(ps)}')
mv = step_run(ps, "Move 'site'")
script = mv['run']
with tempfile.TemporaryDirectory() as t:
    t = pathlib.Path(t); binp = t / 'bin'; binp.mkdir()
    (binp / 'gh').write_text('''#!/usr/bin/env python3
import os, sys, json
a = ' '.join(sys.argv[1:]); sc = json.loads(os.environ['SCEN'])
open(os.environ['CALLS'], 'a').write(a + '\\n')
if 'git/ref/heads/main' in a: print('b' * 40); sys.exit(0)
if 'git/ref/heads/site' in a: print('a' * 40); sys.exit(0)
if '/compare/' in a: print('\\n'.join(sc['files'])); sys.exit(0)
if '/commits/' in a: print(sc['site_date']); sys.exit(0)
if 'pages/builds/latest' in a: print(sc['build']); sys.exit(0)
if '-X PATCH' in a: sys.exit(1 if sc.get('patch_fails') else 0)
sys.exit(0)
''')
    (binp / 'gh').chmod(0o755)
    def run_sync(scen, switch=''):
        calls = t / 'calls.txt'; calls.write_text(''); summ = t / 'summary.md'; summ.write_text('')
        env = dict(ENV, PATH=f'{binp}:{os.environ["PATH"]}', SCEN=json.dumps(scen), CALLS=str(calls), R='o/r', RUNNER_TEMP=str(t), GITHUB_STEP_SUMMARY=str(summ), SWITCH=switch, GH_TOKEN='x')
        r = subprocess.run(['bash', '-c', script], capture_output=True, text=True, env=env)
        return r, calls.read_text(), summ.read_text()
    recent = '2099-01-01T00:00:00Z'; old = '2020-01-01T00:00:00Z'
    r, calls, summ = run_sync({'files': ['.github/workflows/x.yml', 'data/status/board.json', 'data/waiting/heartbeat.json', 'tests/t.py'], 'site_date': recent, 'build': 'built'})
    check('-X PATCH' not in calls and r.returncode == 0 and 'bookkeeping' in summ, f'only bookkeeping changed: site left alone, green, said so in the summary {r.stderr[-120:]}')
    r, calls, summ = run_sync({'files': ['.github/workflows/x.yml', 'data/campinfo/US-TX.json'], 'site_date': recent, 'build': 'built'})
    check('-X PATCH' in calls and 'site moved' in summ, 'a data file the site reads changed: site moves')
    r, calls, summ = run_sync({'files': ['data/campinfo/US-TX.json'], 'site_date': recent, 'build': 'building'})
    check('-X PATCH' not in calls and r.returncode == 0 and 'still running' in summ, 'a Pages build is still running: no move on top of it, green')
    r, calls, summ = run_sync({'files': ['data/status/board.json'], 'site_date': old, 'build': 'built'})
    check('-X PATCH' in calls, 'bookkeeping only but the site copy is over 6 h old: moves (the status page reads data/status)')
    r, calls, summ = run_sync({'files': ['data/campinfo/US-TX.json'], 'site_date': recent, 'build': 'built', 'patch_fails': True})
    check('stay stale' in r.stdout and (t / 'kpc-hidden-errors.txt').exists(), 'a move that fails while the site is behind a real change is reported as an error (the only red reason)')
check("KPC_HIDDEN_RED != 'off'" in json.dumps(ps), 'kpc-pages-sync.yml: its fail-safe red (site would stay stale) is kept')

# 4. quiet-save gate on real local repos (Data keeps a copy for the flow board)
GATE = HERE / '.github/scripts/kpc_quiet_gate.py'
with tempfile.TemporaryDirectory() as t:
    t = pathlib.Path(t); origin = t / 'o.git'; sh(f'git init -q --bare -b main {origin}', t)
    w = t / 'w'; sh(f'git clone -q file://{origin} {w}', t)
    (w / 'data/status').mkdir(parents=True)
    def board(c): return json.dumps({'bots': {'flow board': {'result': c}}})
    (w / 'data/status/board.json').write_text(board('green')); (w / 'data/status/flow.json').write_text('{"n": 1}')
    sh('git add -A && git commit -qm "flow board" && git push -q origin HEAD:main', w)
    def gate(msg, hours='3'):
        return sh(f'python3 {GATE}', w, {'KPC_QUIET_MSG': msg, 'KPC_QUIET_HOURS': hours})
    (w / 'data/status/flow.json').write_text('{"n": 2}'); sh('git add -A', w)
    check(gate('flow board').returncode == 3, 'gate: flow board refresh within 3 h of its last save = skip (exit 3)')
    check(gate('other bot').returncode == 0, 'gate: another bot is not held back')
    check(gate('flow board', '0').returncode == 0, 'gate: KPC_QUIET_HOURS=0 = off')
    (w / 'data/status/board.json').write_text(board('red')); sh('git add -A', w)
    check(gate('flow board').returncode == 0, 'gate: a board line turning red is saved at once')
    sh('git reset -q --hard HEAD', w); (w / 'data/status/flow.json').write_text('{"n": 3}'); (w / 'data/campinfo.json').write_text('{}'); sh('git add -A', w)
    check(gate('flow board').returncode == 0, 'gate: a real data file in the save = saved at once')
check('verdicts.jsonl' not in [l for l in GATE.read_text().split('\n') if l.startswith('BOOK')][0], 'gate: the append-only verdicts log is never treated as bookkeeping (a skip would lose lines)')
fl = step_run(docs['kpc-flow.yml'], 'Build the flow board')['run']
check('kpc_quiet_gate.py' in fl and 'kpc_stamp_only.py' in fl, 'kpc-flow.yml: stamp filter, then the quiet gate, before the commit')

# 5. Europe weather: same warnings = not saved again until 12 h
eu = step_run(docs['kpc-eu-alerts.yml'], 'Save')['run']
py = re.search(r"python3 - <<'PY' \|\| true[^\n]*\n(.*?)\n\s*PY\n", eu, re.S)
check(bool(py), 'kpc-eu-alerts.yml: the same-warnings check is in the Save step')
if py:
    code = '\n'.join(l[10:] if l.startswith(' ' * 10) else l for l in py.group(1).split('\n'))
    with tempfile.TemporaryDirectory() as t:
        t = pathlib.Path(t); w = t / 'w'; (w / 'data/alerts').mkdir(parents=True); sh('git init -q -b main .', w)
        def doc(upd, onset, level='yellow'):
            return json.dumps({'updated': upd, 'countries': {'BE': {'items': [{'area': 'Antwerp', 'event': 'fog', 'level': level, 'onset': onset}]}}})
        import datetime as dt
        now = dt.datetime.now(dt.timezone.utc)
        (w / 'data/alerts/eu.json').write_text(doc(now.strftime('%Y-%m-%dT%H:%M+00:00'), '0')); sh('git add -A && git commit -qm a', w)
        (w / 'data/alerts/eu.json').write_text(doc(now.strftime('%Y-%m-%dT%H:%M+00:00'), '5'))
        (t / 'c.py').write_text(code); sh(f'python3 {t / "c.py"}', w)
        check(json.loads((w / 'data/alerts/eu.json').read_text())['countries']['BE']['items'][0]['onset'] == '0', 'Europe: same warning, only the onset moved, saved copy fresh = put back (not saved)')
        (w / 'data/alerts/eu.json').write_text(doc(now.strftime('%Y-%m-%dT%H:%M+00:00'), '5', 'orange')); sh(f'python3 {t / "c.py"}', w)
        check(json.loads((w / 'data/alerts/eu.json').read_text())['countries']['BE']['items'][0]['level'] == 'orange', 'Europe: a warning that changes level is kept (saved)')
        old = (now - dt.timedelta(hours=13)).strftime('%Y-%m-%dT%H:%M+00:00')
        (w / 'data/alerts/eu.json').write_text(doc(old, '0')); sh('git add -A && git commit -qm b', w)
        (w / 'data/alerts/eu.json').write_text(doc(now.strftime('%Y-%m-%dT%H:%M+00:00'), '5')); sh(f'python3 {t / "c.py"}', w)
        check(json.loads((w / 'data/alerts/eu.json').read_text())['countries']['BE']['items'][0]['onset'] == '5', 'Europe: saved copy 12 h or older = saved even if the warnings are the same')

# 6. the stamp filter (shared with KPC-Links) still skips a stamp-only save
STAMP = HERE / '.github/scripts/kpc_stamp_only.py'
with tempfile.TemporaryDirectory() as t:
    w = pathlib.Path(t); sh('git init -q -b main .', w); (w / 'data/status/bots').mkdir(parents=True)
    p = w / 'data/status/bots/campground-info-bot.json'
    p.write_text(json.dumps({'last_run': '2026-11-10', 'run': 'https://github.com/o/r/actions/runs/1', 'result': 'green'})); sh('git add -A && git commit -qm a', w)
    p.write_text(json.dumps({'last_run': '2026-11-10', 'run': 'https://github.com/o/r/actions/runs/2', 'result': 'green'})); sh('git add -A', w)
    sh(f'python3 {STAMP}', w)
    check(sh('git diff --cached --quiet', w).returncode == 0, 'stamp-only (new run link, same day) = nothing left to save')

# 7. fail-safe narrowed; storage keeper keeps its one intentional red
for n in ('kpc-retry-hosts.yml', 'kpc-scoreboard.yml', 'kpc-storage.yml'):
    t = (WFD / n).read_text()
    line = [l for l in t.split('\n') if 'KPC_FAIL_SAFE:' in l][0]
    check("== 'all'" in line and "!= 'off'" not in line, f'{n}: a caught error alone no longer turns the run red (KPC_HIDDEN_RED=all = old way)')
st = docs['kpc-storage.yml']
red = [s for j in st['jobs'].values() for s in j['steps'] if 'Over the line' in (s.get('name') or '')]
check(len(red) == 1 and 'exit 1' in red[0]['run'] and red[0].get('if') == "${{ env.OVER == '1' }}", 'kpc-storage.yml: the one intentional "over the line" red step is intact')
meas = step_run(st, 'The orphan branches')  # noqa: F841
mrun = [s for j in st['jobs'].values() for s in j['steps'] if 'storage_keeper.py measure' in (s.get('run') or '')][0]['run']
check('[ "$rc" = 0 ] && [ -n "$O" ]' in mrun and 'O=0' in mrun, 'kpc-storage.yml: a measure that errored sets OVER=0 (cannot reach the red step)')
# run the measure snippet with a failing measure
frag = mrun.split('python3 .github/scripts/kpc_storage_keeper.py measure', 1)[1]
with tempfile.TemporaryDirectory() as t:
    t = pathlib.Path(t); (t / 'm.txt').write_text('OVER=1\nLINE=STORAGE WARNING: x\n'); envf = t / 'env.txt'; envf.write_text('')
    body = 'rc=1\n' + '\n'.join(l for l in ('L=$(grep ' + frag.split('L=$(grep ', 1)[1]).split('\n') if 'kpc_status.py' not in l)
    body = body.replace('/tmp/m.txt', str(t / 'm.txt'))
    r = subprocess.run(['bash', '-c', body], capture_output=True, text=True, env=dict(ENV, GITHUB_ENV=str(envf), KPC_X='1'))
    check('OVER=0' in envf.read_text() and 'OVER=1' not in envf.read_text(), f'storage measure that exited non-zero reports OVER=0 even if its output said 1 {r.stderr[-100:]}')
    body2 = body.replace('rc=1', 'rc=0'); envf.write_text('')
    subprocess.run(['bash', '-c', body2], capture_output=True, text=True, env=dict(ENV, GITHUB_ENV=str(envf)))
    check('OVER=1' in envf.read_text(), 'storage measure that finished and reads over the line still reports OVER=1 (the intentional red)')

# 8. watchdog: a lost notes-save ends green
check('still ends green' in (WFD / 'kpc-watchdog.yml').read_text(), 'kpc-watchdog.yml: a lost notes-save does not turn the run red')

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
