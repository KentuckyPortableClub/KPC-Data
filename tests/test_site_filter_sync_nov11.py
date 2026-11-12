#!/usr/bin/env python3
"""kpc-pages-sync.yml with the site filter (KPC owner, 2026-11-11): runs the workflow's real 'Move site' step (read from the YAML)
against a throwaway bare repo standing in for GitHub (a stub 'gh' answers from it), in a blobless sparse clone like the workflow's
checkout. Checks: the first run publishes the filtered commit; a second run publishes nothing; a data change republishes; a
bookkeeping-only change does not; an allow-list change does; a broken allow-list publishes NOTHING and is an error; FILTER=off
puts back the old way (site = main, API move, no pages/builds request); a filtered publish calls POST pages/builds after the
push (a failed request makes the run red, the site ref already moved); and the watchdog reads a filtered site as up to date
and never moves it to main. Offline."""
import json, os, pathlib, shutil, subprocess, sys, tempfile
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
WF = yaml.safe_load(open(ROOT / '.github/workflows/kpc-pages-sync.yml', encoding='utf-8'))
STEP = [s for s in WF['jobs']['sync']['steps'] if s.get('id') == 'kept_green_1'][0]['run']
fails = 0
ENV = dict(os.environ, GIT_AUTHOR_NAME='t', GIT_AUTHOR_EMAIL='t@example.invalid', GIT_COMMITTER_NAME='t', GIT_COMMITTER_EMAIL='t@example.invalid',
           GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM='1', GIT_ALLOW_PROTOCOL='file')


def check(name, ok, extra=''):
    global fails
    print(('PASS' if ok else 'FAIL') + ': ' + name + (f' ({str(extra)[-400:]})' if extra and not ok else ''))
    fails += 0 if ok else 1


def git(cwd, *a):
    r = subprocess.run(['git', *a], cwd=cwd, capture_output=True, text=True, env=ENV)
    if r.returncode: raise RuntimeError(f'git {a}: {r.stderr}')
    return r.stdout.strip()


GH = r'''#!/usr/bin/env python3
import os, subprocess, sys
B = os.environ['BARE']; a = sys.argv[1:]
open(os.environ['CALLS'], 'a').write(' '.join(a) + '\n')
def g(*x):
    r = subprocess.run(['git', '-C', B, *x], capture_output=True, text=True)
    if r.returncode: sys.exit(1)
    return r.stdout.strip()
if a[0] == 'api': a = a[1:]
s = ' '.join(a)
if a[0] == '-X':
    if a[1] in ('PATCH', 'POST') and 'git/refs' in s:
        sha = [x[4:] for x in a if x.startswith('sha=')][0]; ref = 'refs/heads/site'
        g('update-ref', ref, sha); sys.exit(0)
    if a[1] == 'POST' and 'pages/builds' in s:
        if os.environ.get('PAGES_BUILDS_FAIL'):
            sys.stderr.write('pages builds failed\n'); sys.exit(1)
        sys.exit(0)
    sys.exit(0)
p = a[0]
if '/git/ref/heads/' in p: print(g('rev-parse', '--verify', 'refs/heads/' + p.split('/git/ref/heads/')[1])); sys.exit(0)
if '/git/commits/' in p:
    c = p.split('/git/commits/')[1]
    print(g('rev-parse', c + '^') if 'parents' in s else g('log', '-1', '--format=%B', c)); sys.exit(0)
if '/compare/' in p:
    x, y = p.split('/compare/')[1].split('?')[0].split('...'); print(g('diff', '--name-only', x, y)); sys.exit(0)
if '/commits/' in p: print(g('log', '-1', '--format=%cI', p.split('/commits/')[1])); sys.exit(0)
if 'pages/builds/latest' in p: print('built'); sys.exit(0)
if '/contents/.nojekyll' in p: print('.nojekyll' if g('ls-tree', '--name-only', 'site', '.nojekyll') else ''); sys.exit(0)
if p.endswith('/pages'): print(''); sys.exit(0)
if 'dispatches' in s: sys.exit(0)
sys.exit(1)
'''

tmp = pathlib.Path(tempfile.mkdtemp(prefix='kpc-site-sync-test-'))
try:
    src = tmp / 'src'; src.mkdir(); git(src, 'init', '-q', '-b', 'main')
    def w(rel, txt='x'):
        p = src / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(txt)
    w('.nojekyll', ''); w('index.html', 'i'); w('.github/scripts/kpc_site_filter.py', (ROOT / '.github/scripts/kpc_site_filter.py').read_text())
    w('.github/scripts/kpc_site_publish.sh', (ROOT / '.github/scripts/kpc_site_publish.sh').read_text())
    w('.github/site-allow-list.txt', '.nojekyll  # pages\ndata/keep/  # page a.js:1\n')
    for i in range(12): w(f'data/keep/k{i}.json', str(i)); w(f'data/waiting/in/h{i}.json', str(i))
    git(src, 'add', '-A'); git(src, 'commit', '-qm', 'main 1')
    bare = tmp / 'remote.git'; git(tmp, 'clone', '-q', '--bare', str(src), str(bare))
    git(bare, 'config', 'uploadpack.allowFilter', 'true'); git(bare, 'config', 'uploadpack.allowAnySHA1InWant', 'true')
    git(bare, 'update-ref', 'refs/heads/site', git(bare, 'rev-parse', 'main'))       # today: site = main's commit
    binp = tmp / 'bin'; binp.mkdir(); (binp / 'gh').write_text(GH); (binp / 'gh').chmod(0o755)

    def push_main(change):
        change(); git(src, 'add', '-A'); git(src, 'commit', '-qm', 'main change'); git(src, 'push', '-q', str(bare), 'main')

    def run(filt='on', extra=None):
        wk = tmp / 'wk'; shutil.rmtree(wk, ignore_errors=True)
        git(tmp, 'clone', '-q', '--depth', '1', '--filter=blob:none', '--sparse', bare.as_uri(), str(wk))   # like actions/checkout: sparse .github
        git(wk, 'sparse-checkout', 'set', '.github')
        calls = tmp / 'calls.txt'; calls.write_text(''); summ = tmp / 'summary.md'; summ.write_text('')
        (tmp / 'kpc-hidden-errors.txt').unlink(missing_ok=True)
        env = dict(ENV, PATH=f'{binp}:{os.environ["PATH"]}', BARE=str(bare), CALLS=str(calls), R='o/r', GITHUB_REPOSITORY='o/r',
                   RUNNER_TEMP=str(tmp), GITHUB_STEP_SUMMARY=str(summ), SWITCH='', GH_TOKEN='x', FILTER=filt, KPC_SITE_MIN_FILES='5')
        if extra: env.update(extra)
        r = subprocess.run(['bash', '-c', STEP], cwd=wk, capture_output=True, text=True, env=env, timeout=300)
        return r, summ.read_text(), (tmp / 'kpc-hidden-errors.txt').exists()

    site = lambda: git(bare, 'rev-parse', 'site'); main = lambda: git(bare, 'rev-parse', 'main')
    files = lambda rev: set(git(bare, 'ls-tree', '-r', '--name-only', rev).splitlines())
    def requested_build(text=None):
        text = (tmp / 'calls.txt').read_text() if text is None else text
        return any('-X POST' in ln and 'pages/builds' in ln and 'latest' not in ln for ln in text.splitlines())
    r, summ, err = run()
    check('first run: site becomes the filtered commit on top of main', git(bare, 'rev-parse', 'site^') == main() and 'filtered copy' in summ and not err, r.stdout + r.stderr)
    check('... and after the push it requests POST pages/builds', requested_build() and 'a Pages build was requested' in summ)
    check('... holding only the allow-listed paths (data/waiting and .github gone)', files('site') == {'.nojekyll', 'index.html'} | {f'data/keep/k{i}.json' for i in range(12)})
    s1 = site()
    r, summ, err = run()
    check('second run: nothing to publish, site unchanged', site() == s1 and 'nothing to publish' in summ and not err, summ + r.stderr)
    check('... and it does not request a Pages build', not requested_build())
    push_main(lambda: w('data/keep/k1.json', 'changed'))
    r, summ, err = run()
    check('a kept data file changed: a new filtered site is published', site() != s1 and git(bare, 'rev-parse', 'site^') == main() and not err, summ + r.stderr)
    s2 = site()
    push_main(lambda: w('data/waiting/in/h1.json', 'changed'))
    r, summ, err = run()
    check('only data/waiting (bookkeeping) changed: site left as it is', site() == s2 and 'bookkeeping' in summ and not err, summ + r.stderr)
    check('... and it does not request a Pages build', not requested_build())
    push_main(lambda: w('.github/site-allow-list.txt', '.nojekyll  # pages\ndata/keep/  # page a.js:1\ndata/waiting/in/h1.json  # test reader\n'))
    r, summ, err = run()
    check('an allow-list change alone republishes the site', site() != s2 and 'data/waiting/in/h1.json' in files('site') and not err, summ + r.stderr)
    s3 = site()
    push_main(lambda: (w('.github/site-allow-list.txt', 'data/keep/\n'), w('data/keep/k2.json', 'changed')))
    r, summ, err = run()
    check('a broken allow-list: NOTHING is published, site stays the last good one, and it is an error (red)', site() == s3 and err and 'refused' in r.stdout, r.stdout[-500:])
    check('... and site is never moved to main (no PATCH to main)', '-X PATCH' not in (tmp / 'calls.txt').read_text())
    check('... and a refused filter does not request a Pages build', not requested_build())
    r, summ, err = run(filt='off')
    off_calls = (tmp / 'calls.txt').read_text()
    check('FILTER=off (the repo variable KPC_SITE_FILTER=off): site = main again, everything published (the rollback)', site() == main() and 'filter off' in summ and not err, summ + r.stderr)
    check('FILTER=off path is unchanged: API move of site to main, no git push, no pages/builds request',
          '-X PATCH' in off_calls and 'git/refs/heads/site' in off_calls and not requested_build(off_calls))
    push_main(lambda: w('.github/site-allow-list.txt', '.nojekyll  # pages\ndata/keep/  # page a.js:1\n'))
    r, summ, err = run()
    check('filter back on: the filtered site comes back', git(bare, 'rev-parse', 'site^') == main() and 'data/waiting/in/h1.json' not in files('site'), summ + r.stderr)
    check('... and it requests POST pages/builds after the push', requested_build())

    # the watchdog reads the filtered site as up to date, and never moves it to main
    wd = ROOT / '.github/scripts'
    code = ("import sys; sys.path.insert(0, sys.argv[1]); import kpc_watchdog as W; print(W.site_check())")
    env = dict(ENV, PATH=f'{binp}:{os.environ["PATH"]}', BARE=str(bare), CALLS=str(tmp / 'calls.txt'), GITHUB_REPOSITORY='o/r', DRY='1')
    r = subprocess.run([sys.executable, '-B', '-c', code, str(wd)], capture_output=True, text=True, env=env, cwd=tmp)
    check('watchdog: a filtered site on top of main = green (site = main)', "'green'" in r.stdout and 'site = main' in r.stdout, r.stdout + r.stderr)
    # the watchdog's repair path: site far behind main -> it publishes through kpc_site_publish.sh (the filtered site, never main's tree)
    old_site = site()
    def late():
        w('data/keep/k5.json', 'late change')
    late(); git(src, 'add', '-A')
    subprocess.run(['git', 'commit', '-qm', 'an old main change'], cwd=src, env=dict(ENV, GIT_COMMITTER_DATE='2020-01-01T00:00:00Z', GIT_AUTHOR_DATE='2020-01-01T00:00:00Z'), check=True)
    git(src, 'push', '-q', str(bare), 'main')
    wk = tmp / 'wk'; shutil.rmtree(wk, ignore_errors=True)
    git(tmp, 'clone', '-q', '--depth', '1', bare.as_uri(), str(wk))      # the watchdog's checkout is a normal one
    env2 = dict(ENV, PATH=f'{binp}:{os.environ["PATH"]}', BARE=str(bare), CALLS=str(tmp / 'calls.txt'), GITHUB_REPOSITORY='o/r', KPC_SITE_FILTER='on',
                KPC_SITE_MIN_FILES='5', RUNNER_TEMP=str(tmp), GH_TOKEN='x')
    (tmp / 'calls.txt').write_text('')
    r = subprocess.run([sys.executable, '-B', '-c', code, str(wd)], capture_output=True, text=True, env=env2, cwd=wk)
    check('watchdog repair: site far behind -> it publishes the FILTERED site via kpc_site_publish.sh',
          site() != old_site and git(bare, 'rev-parse', 'site^') == main() and 'data/waiting/in/h1.json' not in files('site'), r.stdout[-400:] + r.stderr[-400:])
    check('... and never PATCHes site to main', '-X PATCH' not in (tmp / 'calls.txt').read_text())
    check('... and after the filtered push it requests POST pages/builds', requested_build())

    # a failed pages/builds request after a successful push makes the run red (site already moved; never silent)
    s_before = site()
    push_main(lambda: w('data/keep/k1.json', 'after failed build request'))
    r, summ, err = run(extra={'PAGES_BUILDS_FAIL': '1'})
    check('when POST pages/builds fails after a filtered push: site already moved, the run is red, no silent success',
          site() != s_before and git(bare, 'rev-parse', 'site^') == main() and err and 'requesting a Pages build failed' in r.stdout, r.stdout[-500:] + r.stderr[-300:])
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print('ALL PASSED' if not fails else f'SOME FAILED ({fails})')
sys.exit(1 if fails else 0)
