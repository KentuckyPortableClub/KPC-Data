#!/usr/bin/env python3
"""SKIPPED-RUN WATCHDOG (chat 10, Nov 2 2026; chat 2 + Brandon 7:18 AM: GitHub skipped most of last night's scheduled runs, so
things kept stalling; 'everything implements now'). Every 2 hours, for every ACTIVE workflow of THIS repo with a schedule:
the latest time its cron should have fired (in the last 26 h, at least 25 min ago) must have a run (scheduled, by hand or by
another bot) started within 15 min before / any time after it. No run = GitHub skipped it: the watchdog starts it once by hand
(workflow_dispatch; inputs: the workflow's defaults, plus WATCHDOG_INPUTS below where a default would change what the scheduled
run does). (Its own 2-hourly look covers the frequent ones too: GitHub skipped most of the every-2-hours waiting-room runs.) Each restart is
remembered in data/status/watchdog.json (never twice for the same missed time) and listed on the status board. Never fails.
  python3 .github/scripts/kpc_watchdog.py        env GH_TOKEN, GITHUB_REPOSITORY"""
import datetime as dt, json, os, pathlib, re, subprocess, sys

REPO = os.environ.get('GITHUB_REPOSITORY') or 'KentuckyPortableClub/KPC-Data'
STATE = pathlib.Path('data/status/watchdog.json')
NOW = dt.datetime.now(dt.timezone.utc)
SELF = 'kpc-watchdog.yml'
WATCHDOG_INPUTS = {'kpc-new-refs.yml': {'dry_run': 'false'}}   # its dispatch default is a dry run; the scheduled run is not
# Nov 2 review: a restart must do what the SCHEDULED run does. These dispatch defaults would change it:
WATCHDOG_INPUTS.update({
    'kpc-waiting-room.yml': {'mode': 'release-approved'},             # default 'replay' = no release, no key doctor
    'kpc-closures.yml': {'areas': '', 'test': 'no', 'chunks': '5'},  # default = a Kentucky-only TEST run
    'kpc-discovery.yml': {'states': ''},                              # default 'OH' every time; scheduled = the week's 8 states
    'kpc-helpers.yml': {'@37 5 * * 0': {'jobs': 'linkfix sitecheck'}, '@23 10 * * *': {'jobs': 'match'}},
    'kpc-world-key.yml': {'pin_join': ''},                            # default 'JP'; scheduled = no pin
    'kpc-approvals.yml': {'send_now': 'false'},                       # default true = an extra email at the wrong hour
    'kpc-discord-watch.yml': {'mode': 'watch', 'target': ''},         # default 'list' to admin
})
# Restarting these cannot match the scheduled run without posting by hand (their dispatch is a practice run or a different task),
# or they run so often that the next slot comes first: listed on the board as skipped, never restarted.
WATCHDOG_SKIP = {'kpc-youtube-comments.yml', 'kpc-social.yml', 'kpc-club-posts.yml', 'kpc-whats-new.yml', 'kpc-park-alerts.yml',
                 'kpc-fb-comments.yml', 'kpc-discord-relay.yml', 'kpc-research-helpers.yml'}


def restart_inputs(name, cron, path=None):
    """-> the inputs to send for this workflow's missed cron ('@<cron>' keys pick per-schedule inputs).
    Nov 2 review (G11): a workflow that declares the input 'as_schedule' also gets the missed cron, so its 'is this the
    scheduled run?' tests answer yes and the restart does exactly what that scheduled run would have done."""
    spec = WATCHDOG_INPUTS.get(name) or {}
    if any(k.startswith('@') for k in spec):
        out = dict(spec.get('@' + cron) or {})
    else:
        out = dict(spec)
    if path and re.search(r'^\s+as_schedule\s*:', pathlib.Path(path).read_text(encoding='utf-8'), re.M):
        out['as_schedule'] = cron
    return out


def gh(*a):
    r = subprocess.run(['gh', 'api', *a], capture_output=True, text=True)
    return r.returncode, r.stdout


def field(spec, lo, hi):
    out = set()
    for part in spec.split(','):
        step = 1
        if '/' in part: part, step = part.split('/'); step = int(step)
        if part == '*': a, b = lo, hi
        elif '-' in part: a, b = map(int, part.split('-'))
        else: a = b = int(part)
        out.update(range(a, b + 1, step))
    return out


def fires(cron):
    """-> function(datetime) True when the 5-field cron (UTC) fires at that minute."""
    m, h, dom, mon, dow = cron.split()[:5]
    M, H, D, MO = field(m, 0, 59), field(h, 0, 23), field(dom, 1, 31), field(mon, 1, 12)
    W = {x % 7 for x in field(dow, 0, 7)}
    dom_any, dow_any = dom == '*', dow == '*'

    def ok(t):
        if t.minute not in M or t.hour not in H or t.month not in MO: return False
        d_ok, w_ok = t.day in D, (t.isoweekday() % 7) in W
        if dom_any and dow_any: return True
        if dom_any: return w_ok
        if dow_any: return d_ok
        return d_ok or w_ok
    return ok


def last_fire(cron, back_h=26, min_age_min=25):
    ok = fires(cron)
    t = (NOW - dt.timedelta(minutes=min_age_min)).replace(second=0, microsecond=0)
    end = NOW - dt.timedelta(hours=back_h)
    times = []
    while t > end:
        if ok(t): times.append(t)
        t -= dt.timedelta(minutes=1)
    return times


def crons(path):
    txt = pathlib.Path(path).read_text(encoding='utf-8')
    if not re.search(r'^\s*workflow_dispatch\s*:', txt, re.M): return None, []
    return True, re.findall(r"^\s*-\s*cron:\s*['\"]([^'\"]+)['\"]", txt, re.M)


SITE_LAG_MIN = 60        # PR3: 'site' may trail main by this much (the copy bot runs every 20 min) before the watchdog steps in
SITE_FORCE_MIN = 120     # PR3: still behind after this long = the copy bot itself is broken: the watchdog moves 'site' itself
SITE_SKIP = ('.github/', '.claude/')   # changes only here do not change the website, so a lag of these alone is fine


def _t(s):
    return dt.datetime.fromisoformat(str(s).replace('Z', '+00:00'))


def site_check():
    """PR3 (Nov 2, Brandon: 'i never had them check the watcher'): GitHub Pages publishes the branch 'site', which
    kpc-pages-sync.yml moves up to main at most every 20 min. If 'site' is more than SITE_LAG_MIN behind main AND the commits
    it is missing change website files (anything outside .github/ and .claude/), the watchdog says so (::error + a red board
    line) and starts kpc-pages-sync once. Past SITE_FORCE_MIN it moves 'site' to main itself (same commit, no new files).
    It also checks that 'site' still has .nojekyll (and CNAME, if Pages ever gets a custom domain).
    -> (result, words) for the board."""
    rc, m = gh(f'repos/{REPO}/git/ref/heads/main', '--jq', '.object.sha'); M = m.strip()
    rc2, s = gh(f'repos/{REPO}/git/ref/heads/site', '--jq', '.object.sha'); S = s.strip() if rc2 == 0 else ''
    if rc != 0 or not M:
        return 'amber', 'could not read main (GitHub API); next look tries again'
    if not S:
        return 'red', "branch 'site' is missing: the website cannot publish. Run 'KPC site copy for GitHub Pages' by hand"
    probs = []
    rc, nj = gh(f'repos/{REPO}/contents/.nojekyll?ref=site', '--jq', '.name')
    if rc != 0 or nj.strip() != '.nojekyll':
        probs.append("'site' has no .nojekyll (GitHub would run Jekyll and drop files)")
    rc, cn = gh(f'repos/{REPO}/pages', '--jq', '.cname // ""')
    if rc == 0 and cn.strip():
        rc, f = gh(f'repos/{REPO}/contents/CNAME?ref=site', '--jq', '.name')
        if rc != 0: probs.append(f"Pages has the custom domain {cn.strip()} but 'site' has no CNAME file")
    # Nov 11 (KPC owner, storage round 2): a filtered 'site' is one commit ON TOP of the main commit it was made from
    # (kpc_site_filter.py); compare that main commit, not the site commit itself
    rc3, msg = gh(f'repos/{REPO}/git/commits/{S}', '--jq', '.message')
    if rc3 == 0 and msg.startswith('site: published copy of main '):
        rc3, par = gh(f'repos/{REPO}/git/commits/{S}', '--jq', '.parents[0].sha')
        if rc3 == 0 and par.strip(): S = par.strip()
    if M == S:
        return ('red', '; '.join(probs)) if probs else ('green', "site = main: the website has the newest data")
    rc, cmp_ = gh(f'repos/{REPO}/compare/{S}...{M}', '--jq',
                  '{status, ahead_by, first: (.commits[0].commit.committer.date // ""), files: [.files[]?.filename]}')
    try: c = json.loads(cmp_)
    except Exception: c = {}  # noqa: BLE001
    files = c.get('files') or []
    relevant = [f for f in files if not f.startswith(SITE_SKIP)]
    if c.get('status') == 'ahead' and files and not relevant:
        return ('red', '; '.join(probs)) if probs else ('green', 'site trails main only by bot files (.github/.claude): nothing to publish')
    first = c.get('first') or ''
    lag = (NOW - _t(first)).total_seconds() / 60 if first else 9999
    if lag <= SITE_LAG_MIN:
        return ('red', '; '.join(probs)) if probs else ('green', f'site is under {SITE_LAG_MIN} min behind main: the copy bot will catch up')
    words = f"site is {lag:.0f} min behind main ({c.get('ahead_by', '?')} commits, {len(relevant)} website files): "
    if lag > SITE_FORCE_MIN and not os.environ.get('DRY'):
        # Nov 11 (KPC owner): the repair goes through the same script as the copy bot (kpc_site_publish.sh): the filtered site,
        # or site = main only when the repo variable KPC_SITE_FILTER=off. The watchdog never writes 'site' any other way.
        env = dict(os.environ, R=REPO, FILTER='off' if os.environ.get('KPC_SITE_FILTER') == 'off' else 'on')
        rc = subprocess.run(['bash', '.github/scripts/kpc_site_publish.sh', 'watchdog repair: the copy bot did not catch up'], env=env).returncode
        words += ('the copy bot did not catch up, so the watchdog published site itself (kpc_site_publish.sh)' if rc == 0
                  else f'the watchdog could not publish site either (kpc_site_publish.sh exit {rc}): look at kpc-pages-sync.yml')
    else:
        rc, _ = (0, '') if os.environ.get('DRY') else gh('-X', 'POST', f'repos/{REPO}/actions/workflows/kpc-pages-sync.yml/dispatches', '-f', 'ref=main')
        words += 'started the copy bot (kpc-pages-sync) once' if rc == 0 else 'could NOT start the copy bot'
    return 'red', '; '.join([words] + probs)


def main():
    try: sres, swords = site_check()
    except Exception as e: sres, swords = 'amber', f'site check stopped: {type(e).__name__}: {str(e)[:150]}'  # noqa: BLE001
    print(f"::{'notice' if sres == 'green' else 'error'} title=Website copy (site branch)::{swords}", flush=True)
    if os.path.exists('.github/scripts/kpc_status.py') and not os.environ.get('DRY'):
        subprocess.run([sys.executable, '.github/scripts/kpc_status.py', 'board', 'Website copy (site branch)', sres, swords[:300],
                        'nobody (the watchdog restarts the copy bot itself)' if sres == 'green' else 'HQ: look at kpc-pages-sync.yml runs'], check=False)
    st = json.load(open(STATE)) if STATE.exists() else {}
    done = st.setdefault('restarted', {})
    rc, out = gh(f'repos/{REPO}/actions/workflows', '--paginate', '--jq', '.workflows[] | [.path, .state, .id] | @tsv')
    active = {l.split('\t')[0]: l.split('\t')[2] for l in out.splitlines() if '\tactive\t' in l}
    started, checked = [], 0
    for path, wid in sorted(active.items()):
        name = os.path.basename(path)
        if name == SELF or not os.path.exists(path): continue
        can, cs = crons(path)
        if not can or not cs: continue
        ts = sorted({(t, c) for c in cs for t in last_fire(c)}, reverse=True)
        if not ts: continue
        t, cron = ts[0]; key = f'{name}|{t.isoformat()}'   # the newest time ANY of its crons should have fired
        if key in done: continue
        checked += 1
        since = (t - dt.timedelta(minutes=15)).strftime('%Y-%m-%dT%H:%M:%SZ')
        rc, runs = gh(f'repos/{REPO}/actions/workflows/{wid}/runs?created=>={since}&per_page=5', '--jq', '.total_count')
        if rc != 0 or not runs.strip() or int(runs.strip() or 0) > 0: continue
        args = [f'repos/{REPO}/actions/workflows/{wid}/dispatches', '-X', 'POST', '-f', 'ref=main']
        if name in WATCHDOG_SKIP:
            done[key] = NOW.isoformat(timespec='minutes') + ' skipped (not restarted)'
            started.append(f"{name} (missed {t.strftime('%b %d %H:%M')} UTC, NOT restarted: its next scheduled run catches up)"); continue
        for k, v in restart_inputs(name, cron, path).items(): args += ['-f', f'inputs[{k}]={v}']
        rc, _ = (0, '') if os.environ.get('DRY') else gh(*args)
        done[key] = NOW.isoformat(timespec='minutes') + (' started' if rc == 0 else ' could not start')
        started.append(f"{name} (missed {t.strftime('%b %d %H:%M')} UTC{'' if rc == 0 else ', start FAILED'})")
    cut = (NOW - dt.timedelta(days=7)).isoformat()
    before = json.dumps({k: v for k, v in st.items() if k != 'last'}, sort_keys=True)
    st['restarted'] = {k: v for k, v in done.items() if v >= cut}
    st['last_restarted'] = started
    # PR2 (fewer saves, Nov 2): the file is only rewritten when the watchdog restarted something (or a 7-day-old entry dropped off).
    # A quiet look changes nothing, so the save step commits nothing; the time of this look is in the run log and summary.
    changed = json.dumps({k: v for k, v in st.items() if k != 'last'}, sort_keys=True) != before
    STATE.parent.mkdir(parents=True, exist_ok=True)
    if changed:
        st['last'] = NOW.isoformat(timespec='minutes')
        if not os.environ.get('DRY'): json.dump(st, open(STATE, 'w'), indent=1)
    msg = (f'{len(started)} skipped run(s) started again: ' + '; '.join(started)) if started else 'nothing skipped'
    print(f'::notice title=Watchdog::{msg} ({checked} scheduled times checked, {NOW.strftime("%Y-%m-%d %H:%M")} UTC)', flush=True)
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        try: open(os.environ['GITHUB_STEP_SUMMARY'], 'a').write(f"**Watchdog {NOW.strftime('%Y-%m-%d %H:%M')} UTC:** {msg} ({checked} scheduled times checked)\n\n")
        except Exception: pass  # noqa: BLE001
    if os.path.exists('.github/scripts/kpc_status.py') and not os.environ.get('DRY'):
        # PR2: the board line carries the time only when something was restarted, so a quiet look leaves the board as it was
        subprocess.run([sys.executable, '.github/scripts/kpc_status.py', 'board', 'Skipped-run watchdog', 'amber' if started else 'green',
                        (f"{NOW.strftime('%Y-%m-%d %H:%M')} UTC: {msg}" if started else msg)[:300], 'nobody (it restarts them itself)'], check=False)


if __name__ == '__main__':
    try: main()
    except Exception as e: print(f'::error title=Watchdog::stopped early ({type(e).__name__}: {e}); skipped runs were NOT checked')  # noqa: BLE001  PR3: was a quiet ::notice
    sys.exit(0)
