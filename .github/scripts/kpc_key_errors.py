#!/usr/bin/env python3
"""KEY-BOT ERRORS AND SILENCE (PR3 'key bots reliable', Nov 2 2026; Brandon: bots must stop hiding their errors).
The club's bots are built never to go red, because a red run emails Brandon. The price: a real failure only showed up as an
::error note inside a green run, and nobody read those. This sweep, run by the watchdog every 2 hours, reads the last LOOK_H hours
of the KEY bots in both repos and puts ONE line on the status board (data/status/board.json, the Bot Control Panel):
  red    a key bot had a failed run, or an ::error note (a step that failed but was kept green, a save that never landed, a
         script that stopped early), or it has not finished a run in far longer than its schedule (it went silent);
  amber  the sweep could not read a repo's runs;
  green  every key bot ran and said nothing wrong.
The line names the bots only (not times), so a quiet repeat saves nothing. The full list (run links, the error titles) is in
this run's summary page. Read-only: it never starts, stops or changes a bot. No email.
  python3 .github/scripts/kpc_key_errors.py        env GH_TOKEN (DRY=1: print only, no board line)"""
import datetime as dt, json, os, subprocess, sys

ORG = 'KentuckyPortableClub'
LOOK_H = 3   # the watchdog looks every 2 h; 3 h overlaps so nothing falls between two looks
# workflow file -> (short name, hours without a FINISHED run before it counts as silent; 0 = runs only when started)
KEY = {
    'KPC-Links': {
        'kpc-pota-discord.yml': ('POTA spots to Discord', 3),
        'kpc-hunters.yml': ('hunter counts', 4),
        'kpc-discord-relay.yml': ('Discord relay (club posts)', 1),
        'kpc-park-alerts.yml': ('KY park alerts', 8),
        'kpc-us-closures.yml': ('US closures (site copy)', 0),   # OFF since Oct 29 (Kentucky only): by hand
        'kpc-band-alerts.yml': ('band alerts (NOAA)', 3),
        'kpc-reports.yml': ('member reports + conditions', 8),
        'kpc-boards.yml': ('activation / CW boards', 3),
        'kpc-watchdog.yml': ('KPC-Links watchdog', 5),
    },
    'KPC-Data': {
        'kpc-engine.yml': ('park-info engine', 30),
        'kpc-map-audit.yml': ('map audit', 0),
        'kpc-closures.yml': ('closures super-bot', 0),
        'kpc-us-closures.yml': ('US closures', 0),   # OFF since Oct 29 (Kentucky only): by hand
        'kpc-eu-alerts.yml': ('Europe weather warnings', 14),
        'kpc-pages-sync.yml': ('website copy (site branch)', 3),
        'kpc-watchdog.yml': ('KPC-Data watchdog', 5),
        'kpc-waiting-room.yml': ('waiting room', 6),
        'kpc-copy-from-links.yml': ('copy from KPC-Links', 3),
        'kpc-flow.yml': ('flow board', 26),
    },
}
# ::error notes that are DATA findings with their own board line (not a broken bot): not counted twice here
IGNORE_TITLES = {'Key doctor NOs'}
NOW = dt.datetime.now(dt.timezone.utc)


def gh(*a):
    r = subprocess.run(['gh', 'api', *a], capture_output=True, text=True)
    return r.returncode, r.stdout


def ts(s):
    return dt.datetime.fromisoformat(str(s).replace('Z', '+00:00'))


def sweep():
    since = (NOW - dt.timedelta(hours=LOOK_H)).strftime('%Y-%m-%dT%H:%M:%SZ')
    bad, unread, detail = {}, [], []
    for repo, wfs in KEY.items():
        for wf, (name, max_h) in wfs.items():
            rc, out = gh(f'repos/{ORG}/{repo}/actions/workflows/{wf}/runs?status=completed&per_page=1', '--jq',
                         '.workflow_runs[0] | {created_at, conclusion, html_url}')
            if rc != 0:
                if 'Not Found' in out or '404' in out: continue   # workflow gone / renamed: not this sweep's business
                unread.append(f'{repo}/{wf}'); continue
            try: last = json.loads(out or 'null') or {}
            except ValueError: last = {}
            why = []
            if max_h and (not last.get('created_at') or (NOW - ts(last['created_at'])).total_seconds() > max_h * 3600):
                age = f"{(NOW - ts(last['created_at'])).total_seconds() / 3600:.0f} h" if last.get('created_at') else 'ever'
                why.append(f'silent: no finished run in {age} (expected every {max_h} h or less)')
                detail.append(f'- {repo} **{name}**: silent ({age}); last run {last.get("html_url", "none")}')
            rc, out = gh(f'repos/{ORG}/{repo}/actions/workflows/{wf}/runs?status=completed&created=>={since}&per_page=30', '--jq',
                         '.workflow_runs[] | [.id, .conclusion, .html_url] | @tsv')
            if rc != 0: unread.append(f'{repo}/{wf}'); continue
            for line in out.splitlines():
                rid, concl, url = (line.split('\t') + ['', '', ''])[:3]
                if concl in ('cancelled', 'skipped'): continue
                titles = []
                if concl in ('failure', 'timed_out', 'startup_failure'): titles.append(f'run {concl}')
                rc, jobs = gh(f'repos/{ORG}/{repo}/actions/runs/{rid}/jobs', '--jq', '.jobs[].id')
                for jid in jobs.split():
                    rc, ann = gh(f'repos/{ORG}/{repo}/check-runs/{jid}/annotations', '--jq',
                                 '.[] | select(.annotation_level == "failure") | (.title // "error")')
                    titles += [t for t in ann.splitlines() if t.strip() and t.strip() not in IGNORE_TITLES]
                if titles:
                    why.append(titles[0])
                    detail.append(f'- {repo} **{name}**: {", ".join(sorted(set(titles)))[:300]} ({url})')
            if why: bad[f'{name}'] = why[0]
    return bad, unread, detail


def main():
    bad, unread, detail = sweep()
    if bad:
        res = 'red'
        made = f'{len(bad)} key bot(s) with errors or gone silent: ' + '; '.join(f'{k} ({v[:60]})' for k, v in sorted(bad.items()))
    elif unread:
        res, made = 'amber', 'could not read the runs of: ' + ', '.join(unread[:6])
    else:
        res, made = 'green', 'every key bot ran in the last few hours with no errors'
    print(f"::{'notice' if res == 'green' else 'error'} title=Key bots::{made[:900]}", flush=True)
    for d in detail: print(d)
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as f:
            f.write(f'### Key bots: {res}\n\n{made}\n\n' + '\n'.join(detail) + '\n\n')
    if not os.environ.get('DRY') and os.path.exists('.github/scripts/kpc_status.py'):
        subprocess.run([sys.executable, '.github/scripts/kpc_status.py', 'board', 'Key bots: errors and silence', res, made[:300],
                        'nobody' if res == 'green' else 'HQ: open the watchdog run summary for the run links'], check=False)


if __name__ == '__main__':
    try: main()
    except Exception as e: print(f'::error title=Key bots::the sweep stopped early ({type(e).__name__}: {e})')  # noqa: BLE001
    sys.exit(0)
