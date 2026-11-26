#!/usr/bin/env python3
"""KPC PC heartbeat (Fable, 19 Nov 2026; Brandon 8:13 AM: "3 yes"). The watchdog's own watchdog.

GitHub sometimes skips timed runs, the watchdog's included (19 Nov: the 5:46 AM US key start and two watchdog looks were all
skipped; a chat had to notice and Brandon had to say go). A run started from OUTSIDE is not skipped. This script, run every 20
minutes by Windows Task Scheduler, looks at when each repo's watchdog last ran and starts it ONCE when that is too long ago.
The watchdog then restarts whatever timed run was missed, as it always does. Nothing else is started, read or changed.

  python kpc_heartbeat.py            look, start a watchdog only if it is overdue, write one line to kpc-heartbeat.log
  python kpc_heartbeat.py --dry-run  look and say what it would do; start nothing
  python kpc_heartbeat.py --selftest

Needs: Python 3 and the GitHub tool `gh`, logged in as the owner (the same login the PC helper uses). It talks to GitHub only.
The watchdogs run at about :04 and :33 of every second hour, so the longest normal gap is about 91 minutes: overdue = 115."""
import datetime, json, os, pathlib, subprocess, sys

WATCHDOGS = (('KentuckyPortableClub/KPC-Links', 'kpc-watchdog.yml'), ('KentuckyPortableClub/KPC-Data', 'kpc-watchdog.yml'))
OVERDUE_MIN = 115
LOG = pathlib.Path(__file__).resolve().parent / 'kpc-heartbeat.log'
NOWIN = getattr(subprocess, 'CREATE_NO_WINDOW', 0) if os.name == 'nt' else 0


def gh(*args):
    try:
        p = subprocess.run(['gh', *args], capture_output=True, text=True, timeout=90, creationflags=NOWIN)
        return p.returncode, (p.stdout or '').strip(), (p.stderr or '').strip()
    except Exception as e:  # noqa: BLE001 (gh missing, no network, time-out: say so, never crash)
        return 99, '', f'{type(e).__name__}: {e}'


def when(s):
    try: return datetime.datetime.strptime(str(s)[:19], '%Y-%m-%dT%H:%M:%S').replace(tzinfo=datetime.timezone.utc)
    except Exception: return None  # noqa: BLE001


def decide(runs, now, overdue=OVERDUE_MIN):
    """('start' | 'ok' | 'busy' | 'unknown', minutes since the newest run or None). runs = GitHub's newest-first run list."""
    if runs is None: return 'unknown', None
    if any(r.get('status') in ('queued', 'in_progress', 'waiting', 'requested', 'pending') for r in runs): return 'busy', 0
    t = max((when(r.get('created_at')) for r in runs if when(r.get('created_at'))), default=None)
    if t is None: return 'start', None                      # never ran: start it
    age = (now - t).total_seconds() / 60
    return ('start' if age > overdue else 'ok'), round(age)


def main(argv):
    dry = '--dry-run' in argv; now = datetime.datetime.now(datetime.timezone.utc); lines = []
    for repo, wf in WATCHDOGS:
        rc, out, err = gh('api', f'repos/{repo}/actions/workflows/{wf}/runs?per_page=5', '-q', '[.workflow_runs[]|{status,created_at}]')
        try: runs = json.loads(out) if rc == 0 else None
        except ValueError: runs = None
        what, age = decide(runs, now)
        if what == 'start' and not dry:
            rc2, _, err2 = gh('workflow', 'run', wf, '-R', repo)
            what = 'STARTED' if rc2 == 0 else f'could not start ({err2[:80]})'
        elif what == 'start': what = 'would start (dry run)'
        elif what == 'unknown': what = f'could not look ({err[:80]})'
        lines.append(f"{repo.split('/')[1]}: last watchdog {age if age is not None else '?'} min ago, {what}")
    line = now.strftime('%Y-%m-%d %H:%M UTC') + ' | ' + ' | '.join(lines)
    print(line)
    try:
        old = LOG.read_text(encoding='utf-8').splitlines()[-400:] if LOG.exists() else []   # the log never grows past 400 lines
        LOG.write_text('\n'.join(old + [line]) + '\n', encoding='utf-8')
    except Exception: pass  # noqa: BLE001
    return 0


def _selftest():
    now = datetime.datetime(2026, 11, 19, 12, 40, tzinfo=datetime.timezone.utc); ok = True
    def chk(c, w):
        nonlocal ok; print(('PASS ' if c else 'FAIL ') + w); ok = ok and c
    r = lambda t, s='completed': {'status': s, 'created_at': t}
    chk(decide([r('2026-11-19T10:38:00Z'), r('2026-11-19T10:09:49Z')], now) == ('start', 122), '19 Nov for real: last watchdog 10:38, both later looks skipped -> start at 12:40')
    chk(decide([r('2026-11-19T10:38:00Z')], now.replace(hour=12, minute=5))[0] == 'ok', 'the normal 91-minute gap (10:33 -> 12:04) is not overdue')
    chk(decide([r('2026-11-19T12:33:10Z')], now)[0] == 'ok', 'a watchdog 7 minutes ago: nothing to do')
    chk(decide([r('2026-11-19T12:39:00Z', 'in_progress'), r('2026-11-19T08:00:00Z')], now)[0] == 'busy', 'one is running now: never start a second')
    chk(decide(None, now)[0] == 'unknown', 'GitHub not reachable: start nothing')
    chk(decide([], now)[0] == 'start', 'no run on record: start it')
    print('ALL PASS' if ok else 'SOME FAILED'); return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(_selftest() if '--selftest' in sys.argv[1:] else main(sys.argv[1:]))
