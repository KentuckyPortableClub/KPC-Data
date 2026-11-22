#!/usr/bin/env python3
"""22 Nov 2026 (review F23): the five status files that made most of the KPC-Data churn are not committed
when the only change is a stamp or a clock time, even if another file in the same save is a real change.
heartbeat.json's clock lives under the key 'ok'. A us/ca/world key is rewritten only when its content
changes. Offline, invented files only. Prints PASS / FAIL and ends ALL PASS or SOME FAILED."""
import importlib.util, json, os, pathlib, subprocess, sys, tempfile, time

HERE = pathlib.Path(__file__).resolve().parent.parent
STAMP = HERE / '.github/scripts/kpc_stamp_only.py'
ok = True
ENV = dict(os.environ, GIT_CONFIG_GLOBAL='/dev/null', GIT_AUTHOR_NAME='t', GIT_AUTHOR_EMAIL='t@t',
           GIT_COMMITTER_NAME='t', GIT_COMMITTER_EMAIL='t@t')


def check(cond, msg):
    global ok
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)
    ok = ok and bool(cond)


def sh(cmd, cwd, env=None):
    return subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, env=dict(ENV, **(env or {})))


def staged(w):
    r = sh('git diff --cached --name-only', w)
    return [l for l in r.stdout.splitlines() if l]


# Invented status rows only: no park names.
BOARD = {
    'about': 'test board',
    'updated': '2026-11-22',
    'bots': {
        'demo': {
            'areas': '',
            'last_run': '2026-11-22',
            'made': 'a quiet look',
            'result': 'green',
            'run': 'https://github.com/o/r/actions/runs/1',
            'waiting_on': 'nothing',
        }
    },
}
QUEUE = (
    '# Waiting for a grader (2026-11-22 16:13Z, written by the waiting room)\n'
    'Rows the same as the live copy keep their old YES.\n'
    '- **data/status/demo.json** (info, PASS): 0 new, 0 changed\n'
)
INBOX = (
    '# BOT INBOX FOR THE CHECKERS\n'
    '- FROM BOT demo (2026-11-22): grade me: area data/status/demo.json · [run](https://github.com/o/r/actions/runs/1)\n'
)
VERDICTS = {
    'data/status/demo.json': json.dumps({'kind': 'info', 'path': 'data/status/demo.json',
                                         'verdict': 'PASS', 'run': 'https://github.com/o/r/actions/runs/1'})
}


def seed(w):
    (w / 'data/status').mkdir(parents=True)
    (w / 'data/waiting').mkdir(parents=True)
    (w / 'data/status/board.json').write_text(json.dumps(BOARD, indent=1) + '\n')
    (w / 'data/waiting/heartbeat.json').write_text(json.dumps({'ok': '2026-11-22T16:13Z'}))
    (w / 'data/status/grade-queue.md').write_text(QUEUE)
    (w / 'data/status/inbox-checkers.md').write_text(INBOX)
    (w / 'data/waiting/verdicts-last.json').write_text(json.dumps(VERDICTS, separators=(',', ':')))
    (w / 'data/other.json').write_text('{"n": 1}\n')
    sh('git add -A && git commit -qm a', w)


def time_only(w):
    b = json.loads((w / 'data/status/board.json').read_text())
    b['bots']['demo']['run'] = 'https://github.com/o/r/actions/runs/2'
    (w / 'data/status/board.json').write_text(json.dumps(b, indent=1) + '\n')
    (w / 'data/waiting/heartbeat.json').write_text(json.dumps({'ok': '2026-11-22T16:21Z'}))
    (w / 'data/status/grade-queue.md').write_text(QUEUE.replace('16:13Z', '16:21Z'))
    (w / 'data/status/inbox-checkers.md').write_text(INBOX.replace('/runs/1', '/runs/2'))
    v = dict(VERDICTS)
    v['data/status/demo.json'] = VERDICTS['data/status/demo.json'].replace('/runs/1', '/runs/2')
    (w / 'data/waiting/verdicts-last.json').write_text(json.dumps(v, separators=(',', ':')))


CHURN = [
    'data/status/board.json',
    'data/waiting/heartbeat.json',
    'data/status/grade-queue.md',
    'data/status/inbox-checkers.md',
    'data/waiting/verdicts-last.json',
]


with tempfile.TemporaryDirectory() as t:
    w = pathlib.Path(t); sh('git init -q -b main .', w); seed(w)
    time_only(w); sh('git add -A', w)
    sh(f'python3 {STAMP}', w)
    check(sh('git diff --cached --quiet', w).returncode == 0,
          'all five, only stamps and times (same day) = nothing left to save')

with tempfile.TemporaryDirectory() as t:
    w = pathlib.Path(t); sh('git init -q -b main .', w); seed(w)
    time_only(w)
    (w / 'data/other.json').write_text('{"n": 2}\n')
    sh('git add -A', w)
    sh(f'python3 {STAMP}', w)
    left = staged(w)
    check(left == ['data/other.json'],
          f'time-only churn is put back even when another file has a real change (left: {left})')

with tempfile.TemporaryDirectory() as t:
    w = pathlib.Path(t); sh('git init -q -b main .', w); seed(w)
    b = json.loads((w / 'data/status/board.json').read_text())
    b['bots']['demo']['result'] = 'red'
    (w / 'data/status/board.json').write_text(json.dumps(b, indent=1) + '\n')
    (w / 'data/waiting/heartbeat.json').write_text(json.dumps({'ok': '2026-11-22T16:21Z'}))
    sh('git add -A', w)
    sh(f'python3 {STAMP}', w)
    left = staged(w)
    check(left == ['data/status/board.json'],
          f'a real board change is kept; heartbeat time-only is put back (left: {left})')

# A new day's date on the heartbeat is a real change and is kept.
with tempfile.TemporaryDirectory() as t:
    w = pathlib.Path(t); sh('git init -q -b main .', w); seed(w)
    (w / 'data/waiting/heartbeat.json').write_text(json.dumps({'ok': '2026-11-23T00:01Z'}))
    sh('git add -A', w)
    sh(f'python3 {STAMP}', w)
    left = staged(w)
    check(left == ['data/waiting/heartbeat.json'],
          f"heartbeat's date moving to the next day is still saved (left: {left})")


# F23: a big key file is written only when the content changes.
sys.path.insert(0, str(HERE / '.github/scripts'))
import kpc_waiting_room as WR  # noqa: E402


with tempfile.TemporaryDirectory() as t:
    root = pathlib.Path(t)
    old = WR.DATA, WR.W
    WR.DATA, WR.W = root, root / 'data/waiting'
    try:
        rel = 'data/us-key/ZZ.json'
        live = root / rel
        live.parent.mkdir(parents=True)
        body = {'built': '2026-11-22', 'parks': {}}
        live.write_bytes(json.dumps(body, indent=1, ensure_ascii=False).encode('utf-8'))
        before = live.read_bytes(); mtime = live.stat().st_mtime_ns
        time.sleep(0.02)
        WR.promote_file(rel, body, raw=None)
        check(live.read_bytes() == before and live.stat().st_mtime_ns == mtime,
              'key file, same content: not written again')
        prev = root / 'data/waiting/previous' / rel
        check(not prev.exists(), 'key file, same content: the undo copy is not rotated')
        WR.promote_file(rel, {'built': '2026-11-22', 'parks': {}, 'n': 1}, raw=None)
        check(json.loads(live.read_text())['n'] == 1, 'key file, new content: written')
    finally:
        WR.DATA, WR.W = old

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
