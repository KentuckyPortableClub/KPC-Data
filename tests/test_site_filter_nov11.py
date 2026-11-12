#!/usr/bin/env python3
""".github/scripts/kpc_site_filter.py (KPC owner, 2026-11-11): the 'site' branch carries only allow-listed paths. Offline:
throwaway repos in a temp folder (file:// only); checks the filtered tree, determinism, that main is never touched, every
fail-closed case (no list, empty list, a line without a reader note, a bad pattern, no .nojekyll, too few files, a big loss
against the previous site), a blobless clone that builds and pushes without fetching a file, and the reader check."""
import os, pathlib, shutil, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL = ROOT / '.github' / 'scripts' / 'kpc_site_filter.py'
fails = 0
ENV = dict(os.environ, GIT_AUTHOR_NAME='t', GIT_AUTHOR_EMAIL='t@example.invalid', GIT_COMMITTER_NAME='t',
           GIT_COMMITTER_EMAIL='t@example.invalid', GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM='1', GIT_ALLOW_PROTOCOL='file')
ENV.pop('KPC_SITE_ALLOW_LOSS', None)


def check(name, ok, extra=''):
    global fails
    print(('PASS' if ok else 'FAIL') + ': ' + name + (f' ({str(extra)[-300:]})' if extra and not ok else ''))
    fails += 0 if ok else 1


def git(cwd, *a):
    r = subprocess.run(['git', *a], cwd=cwd, capture_output=True, text=True, env=ENV)
    if r.returncode: raise RuntimeError(f'git {a}: {r.stderr}')
    return r.stdout.strip()


def run(*a, env=None):
    r = subprocess.run([sys.executable, '-B', str(TOOL), *map(str, a)], capture_output=True, text=True, env=env or ENV, timeout=120)
    out = r.stdout + r.stderr
    kv = dict(l.split('=', 1) for l in out.splitlines() if l.split('=', 1)[0] in ('TREE', 'COMMIT', 'PUBLISH'))
    return r.returncode, out, kv


def files_of(repo, rev):
    return set(git(repo, 'ls-tree', '-r', '--name-only', rev).splitlines())


tmp = pathlib.Path(tempfile.mkdtemp(prefix='kpc-site-filter-test-'))
try:
    src = tmp / 'data'; src.mkdir()
    git(src, 'init', '-q', '-b', 'main')
    git(src, 'config', 'uploadpack.allowFilter', 'true'); git(src, 'config', 'uploadpack.allowAnySHA1InWant', 'true')

    def w(rel, txt='x'):
        p = src / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(txt)
    w('.nojekyll', ''); w('index.html', '<p>data</p>'); w('README.md', 'r'); w('.github/scripts/s.py', 'print(1)')
    for i in range(30):
        w(f'data/keep/f{i}.json', '{"i": %d}' % i)
        w(f'data/waiting/in/h{i}.json', '{"held": %d}' % i)
    w('data/fers/US-KY.json', '{}'); w('data/fers/US-OH.json.gz', 'gz'); w('data/fers/reuse-p1-x.json', '{}'); w('data/fers/sub/US-X.json', '{}')
    w('data/deep/a/b/c.json', '{}'); w('data/one.json', '{}'); w('data/other.json', '{}')
    git(src, 'add', '-A'); git(src, 'commit', '-qm', 'main 1')
    allow = tmp / 'allow.txt'
    allow.write_text('# comment\n\n.nojekyll  # pages\ndata/keep/  # page a.js:1\ndata/fers/US-*.json  # page b.js:2\n'
                     'data/fers/US-*.json.gz  # page b.js:3\ndata/deep/**/c.json  # page c.js:4\ndata/one.json  # page d.js:5\n')
    main0 = git(src, 'rev-parse', 'main')

    rc, out, kv = run('build', '--repo', src, '--rev', 'main', '--allow', allow, '--min-files', 5)
    check('build exits 0 and says PUBLISH=yes', rc == 0 and kv.get('PUBLISH') == 'yes', out)
    c = kv.get('COMMIT', '')
    got = files_of(src, c) if c else set()
    want = {'.nojekyll', 'index.html', 'data/fers/US-KY.json', 'data/fers/US-OH.json.gz', 'data/deep/a/b/c.json', 'data/one.json'} | {f'data/keep/f{i}.json' for i in range(30)}
    check('the site tree holds exactly the allow-listed paths (+ index.html, always kept)', got == want, sorted(got ^ want)[:10])
    check("'*' stays inside one name (data/fers/sub/US-X.json not kept)", 'data/fers/sub/US-X.json' not in got)
    check("'**' crosses folders (data/deep/a/b/c.json kept)", 'data/deep/a/b/c.json' in got)
    check('data/waiting, .github and README (not listed) are dropped', not any(p.startswith(('data/waiting/', '.github/')) or p == 'README.md' for p in got))
    check('the site commit sits on top of main (parent = main)', c and git(src, 'rev-parse', c + '^') == main0)
    check('main is not touched', git(src, 'rev-parse', 'main') == main0 and git(src, 'status', '--porcelain') == '')
    check('the file blobs are the same objects as main (no new file content)', all(
        git(src, 'rev-parse', f'{c}:{p}') == git(src, 'rev-parse', f'main:{p}') for p in ('data/one.json', 'data/keep/f3.json')))
    rc2, out2, kv2 = run('build', '--repo', src, '--rev', 'main', '--allow', allow, '--min-files', 5)
    check('deterministic: the same main + list give the same commit sha', kv2.get('COMMIT') == c and c)
    check('prints before / after counts and bytes', 'files' in out and 'MB' in out and '->' in out)

    def obj_count(repo): return git(repo, 'count-objects', '-v')
    before = obj_count(src)
    rc, out, kv = run('build', '--repo', src, '--rev', 'main', '--allow', allow, '--min-files', 5, '--dry-run')
    check('--dry-run reports, writes no object, PUBLISH=no', rc == 0 and kv.get('PUBLISH') == 'no' and not kv.get('COMMIT') and obj_count(src) == before, out)

    # fail closed
    for name, text in (('missing', None), ('empty (comments only)', '# nothing\n\n'), ('a line without a reader note', 'data/keep/\n'),
                       ('a bad pattern (..)', 'data/../x  # r\n'), ('a pattern with a space', 'data/a b  # r\n')):
        f = tmp / f'allow-{abs(hash(name))}.txt'
        if text is not None: f.write_text(text)
        rc, out, kv = run('build', '--repo', src, '--rev', 'main', '--allow', f, '--min-files', 1)
        check(f'fails closed when the allow-list is {name} (exit 3, PUBLISH=no, no commit)', rc == 3 and kv.get('PUBLISH') == 'no' and not kv.get('COMMIT'), out)
    rc, out, kv = run('build', '--repo', src, '--rev', 'main', '--allow', allow, '--min-files', 500)
    check('fails closed when too few files would be published (never an empty or tiny site)', rc == 3 and kv.get('PUBLISH') == 'no', out)
    nj = tmp / 'allow-nonj.txt'; nj.write_text('data/keep/  # r\n')
    (src / '.nojekyll').unlink(); git(src, 'add', '-A'); git(src, 'commit', '-qm', 'no nojekyll')
    rc, out, kv = run('build', '--repo', src, '--rev', 'main', '--allow', nj, '--min-files', 1)
    check('fails closed when .nojekyll would be missing', rc == 3 and '.nojekyll' in out, out)
    git(src, 'revert', '--no-edit', 'HEAD')
    # the loss check against the previous site
    git(src, 'branch', '-f', 'site', c)
    for i in range(10): (src / f'data/keep/f{i}.json').unlink()
    git(src, 'add', '-A'); git(src, 'commit', '-qm', 'main loses a third of a kept folder')
    rc, out, kv = run('build', '--repo', src, '--rev', 'main', '--allow', allow, '--min-files', 5, '--previous', 'site')
    check('fails closed when the new site would lose more than 10 % of the previous site', rc == 3 and kv.get('PUBLISH') == 'no' and 'lose' in out, out)
    rc, out, kv = run('build', '--repo', src, '--rev', 'main', '--allow', allow, '--min-files', 5, '--previous', 'site', '--max-loss', 0.5)
    check('... passes with a higher --max-loss', rc == 0 and kv.get('COMMIT'), out)
    rc, out, kv = run('build', '--repo', src, '--rev', 'main', '--allow', allow, '--min-files', 5, '--previous', 'site', env=dict(ENV, KPC_SITE_ALLOW_LOSS='yes'))
    check('... and once with KPC_SITE_ALLOW_LOSS=yes (a person decides)', rc == 0 and kv.get('COMMIT'), out)
    rc, out, kv = run('build', '--repo', src, '--rev', 'main', '--allow', allow, '--min-files', 5, '--previous', 'no-such-branch')
    check('a missing previous site (first run) is not a failure', rc == 0 and kv.get('COMMIT'), out)

    # a blobless, sparse clone (what the workflow uses): builds without any file content and pushes to the remote
    bare = tmp / 'remote.git'
    git(tmp, 'clone', '-q', '--bare', str(src), str(bare))
    git(bare, 'config', 'uploadpack.allowFilter', 'true')
    bl = tmp / 'blobless'
    git(tmp, 'clone', '-q', '--filter=blob:none', '--no-checkout', '--depth', '1', bare.as_uri(), str(bl))
    git(bl, 'fetch', '-q', '--depth', '1', '--filter=blob:none', 'origin', '+refs/heads/site:refs/remotes/origin/site')
    c0 = obj_count(bl)
    rc, out, kv = run('build', '--repo', bl, '--rev', 'origin/main', '--allow', allow, '--min-files', 5, '--previous', 'origin/site', '--max-loss', 0.5)
    check('builds in a blobless clone (bytes unknown, counts known)', rc == 0 and kv.get('COMMIT') and 'unknown' in out, out)
    lines = lambda s: {l.split(':')[0]: l.split(':')[1].strip() for l in s.splitlines() if ':' in l}
    check('... without fetching any file content (only the new tree + commit objects are added)',
          int(lines(obj_count(bl))['count']) - int(lines(c0)['count']) <= 6 and lines(obj_count(bl)).get('in-pack') == lines(c0).get('in-pack'), obj_count(bl))
    bc = kv.get('COMMIT', '')
    r = subprocess.run(['git', '-C', str(bl), 'push', '-q', '--force', 'origin', f'{bc}:refs/heads/site'], capture_output=True, text=True, env=ENV)
    check('... and the commit pushes to the remote (force-update of site)', r.returncode == 0, r.stderr)
    check('the remote site branch now holds the filtered tree', files_of(bare, 'site') == files_of(src, bc) if r.returncode == 0 else False)
    check("the remote's main is unchanged", git(bare, 'rev-parse', 'main') == git(src, 'rev-parse', 'main'))

    # the reader check
    links = tmp / 'links'; (links / 'js').mkdir(parents=True)
    (links / 'a.js').write_text("KPC.dataUrl('data/keep/f12.json'); KPC.dataUrl('data/fers/' + f + '.json');")
    (links / 'kpc-own.js').write_text("fetch('data/holidays.json')   // a KPC-Links file, not in KPC-Data")
    (links / '.claude').mkdir(); (links / '.claude' / 'n.js').write_text("KPC.dataUrl('data/waiting/in/h1.json')")
    rc, out, _ = run('check-readers', links, '--repo', src, '--rev', 'main', '--allow', allow)
    check('reader check passes when every page path is allow-listed (and ignores .claude/ and KPC-Links-only paths)', rc == 0 and '0 NOT covered' in out, out)
    check("a name built in code ('data/fers/' + f) is a WARN, not a failure", 'WARN' in out and 'data/fers/' in out)
    (links / 'js' / 'new-page.js').write_text("fetch('https://kentuckyportableclub.github.io/KPC-Data/data/waiting/in/h3.json')")
    rc, out, _ = run('check-readers', links, '--repo', src, '--rev', 'main', '--allow', allow)
    check('reader check FAILS when a page reads a KPC-Data path the list drops', rc == 1 and 'new-page.js' in out and 'data/waiting/in/h3.json' in out, out)
    # '!' lines: world 2-fers are kept OFF the public site (owner, 2026-11-11), whatever the other lines say
    d2 = tmp / 'd2'; d2.mkdir(); git(d2, 'init', '-q', '-b', 'main')
    def w2(rel, txt='x'):
        q = d2 / rel; q.parent.mkdir(parents=True, exist_ok=True); q.write_text(txt)
    w2('.nojekyll', ''); [w2(f'data/keep/k{i}.json', str(i)) for i in range(20)]
    for f in ('US-KY.json', 'US-NC.json.gz', 'CA-QC.json', 'W-FR.json', 'W-DE.json.gz', 'missing-ky.json', 'missing-pca.json', 'reuse-p1-x.json'): w2('data/fers/' + f, '{}')
    git(d2, 'add', '-A'); git(d2, 'commit', '-qm', 'd2')
    al2 = tmp / 'allow2.txt'
    al2.write_text('.nojekyll  # p\ndata/keep/  # p\ndata/fers/US-*.json  # gps\ndata/fers/US-*.json.gz  # of\ndata/fers/CA-*.json  # of\n'
                   'data/fers/W-*.json  # an old line someone forgot\ndata/fers/missing-ky.json  # of\n!data/fers/W-*  # world 2-fers: club-room only\n')
    rc, out, kv = run('build', '--repo', d2, '--rev', 'main', '--allow', al2, '--min-files', 5)
    got2 = files_of(d2, kv.get('COMMIT')) if kv.get('COMMIT') else set()
    check("a '!' line wins over an allow line: no data/fers/W-* file is published (.json or .json.gz)", rc == 0 and not any('/W-' in x for x in got2) and 'data/fers/US-KY.json' in got2, out)
    check("... US / CA per-area files and the named missing-* file stay; an unnamed missing-* and reuse-* are dropped",
          {'data/fers/US-KY.json', 'data/fers/US-NC.json.gz', 'data/fers/CA-QC.json', 'data/fers/missing-ky.json'} <= got2 and 'data/fers/missing-pca.json' not in got2 and 'data/fers/reuse-p1-x.json' not in got2)
    check("... and the build says how many files the '!' lines keep off", 'kept OFF the site by the ! lines: 2 file' in out, out)
    only_deny = tmp / 'allow-deny-only.txt'; only_deny.write_text('!data/fers/W-*  # off\n')
    rc, out, kv = run('build', '--repo', d2, '--rev', 'main', '--allow', only_deny, '--min-files', 1)
    check("a list with only '!' lines fails closed", rc == 3 and kv.get('PUBLISH') == 'no', out)
    # a narrowed list against a FILTERED previous site is caught by the loss check
    git(d2, 'branch', '-f', 'site', kv2c := (run('build', '--repo', d2, '--rev', 'main', '--allow', al2, '--min-files', 5)[2]['COMMIT']))
    narrow = tmp / 'allow-narrow.txt'; narrow.write_text('.nojekyll  # p\ndata/keep/k1.json  # p\n')
    rc, out, kv = run('build', '--repo', d2, '--rev', 'main', '--allow', narrow, '--min-files', 1, '--previous', 'site')
    check('narrowing the list a lot against a filtered previous site fails closed (the loss check counts what that site published)', rc == 3 and 'previous filtered site' in out, out)
    # check-readers and the world 2-fers
    l2 = tmp / 'links2'; l2.mkdir()
    (l2 / 'ok.js').write_text("KPC.dataUrl('data/keep/k1.json')")
    rc, out, _ = run('check-readers', l2, '--repo', d2, '--rev', 'main', '--allow', al2)
    check('reader check: a clean page passes', rc == 0, out)
    (l2 / 'gps.js').write_text("var x = 1;\nvar ferP = getJSON('data/fers/' + area + '.json');\n")
    rc, out, _ = run('check-readers', l2, '--repo', d2, '--rev', 'main', '--allow', al2)
    check("reader check FAILS a page that builds 'data/fers/' + area with no world-area guard (it can request data/fers/W-*)",
          rc == 1 and 'gps.js:2' in out and 'data/fers/W-' in out and 'no guard' in out, out)
    (l2 / 'gps.js').write_text("if (/^W-/.test(area)) return [];\nvar ferP = getJSON('data/fers/' + area + '.json');\n")
    rc, out, _ = run('check-readers', l2, '--repo', d2, '--rev', 'main', '--allow', al2)
    check('... and passes once a world-area guard is right above the fetch', rc == 0 and 'world-area guard' in out, out)
    (l2 / 'world.js').write_text("fetch('https://kentuckyportableclub.github.io/KPC-Data/data/fers/W-FR.json')")
    rc, out, _ = run('check-readers', l2, '--repo', d2, '--rev', 'main', '--allow', al2)
    check('reader check FAILS a page that requests a world 2-fer file by name, saying why', rc == 1 and 'world.js' in out and 'kept OFF' in out and 'club-room only' in out, out)
    (l2 / 'world.js').unlink()
    (l2 / 'kpc-fers-regions.json').write_text('{"regions": [{"id": "KY", "files": ["US-KY"], "missing": "missing-ky"}, {"id": "FR", "files": ["W-FR"]}]}')
    rc, out, _ = run('check-readers', l2, '--repo', d2, '--rev', 'main', '--allow', al2)
    check('reader check FAILS a region list that names a world 2-fer file', rc == 1 and 'region FR names W-FR' in out, out)
    (l2 / 'kpc-fers-regions.json').write_text('{"regions": [{"id": "KY", "files": ["US-KY"], "missing": "missing-pca"}]}')
    rc, out, _ = run('check-readers', l2, '--repo', d2, '--rev', 'main', '--allow', al2)
    check('reader check FAILS a region list that names a file the site does not publish', rc == 1 and 'missing-pca' in out and 'not published' in out, out)
    src_txt = TOOL.read_text(encoding='utf-8')
    check('the filter imports no network module', not any(m in src_txt for m in ('import urllib', 'import socket', 'import http', 'import requests')))
    check('the filter never pushes, moves a branch or writes main', not any(f"'{x}'" in src_txt for x in ('push', 'update-ref', 'branch', 'checkout', 'reset', 'merge')))
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print('ALL PASSED' if not fails else f'SOME FAILED ({fails})')
sys.exit(1 if fails else 0)
