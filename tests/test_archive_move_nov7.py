#!/usr/bin/env python3
"""Archive split (Nov 7 2026): kpc_archive_move.py, the kpc_archive.py reader fallback and the waiting-room undo that uses it.
Offline: a fake KPC-Data and KPC-Archive are built in temp folders; the download is stubbed; nothing touches the network or a real repo."""
import contextlib, hashlib, io, json, os, pathlib, subprocess, sys, tempfile, time
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github/scripts'))
ok = True


def check(c, msg):
    global ok
    ok &= bool(c)
    print(('PASS ' if c else 'FAIL ') + msg)


import kpc_archive_move as M
import kpc_archive as KA


def run(argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        try: rc = M.main(argv)
        except SystemExit as e: rc = e.code if isinstance(e.code, int) else 2; buf.write(str(e.code))
    return rc, buf.getvalue()


def put(base, rel, data):
    p = pathlib.Path(base) / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(data); return p


def tree(base):
    return {p.relative_to(base).as_posix(): p.read_bytes() for p in sorted(pathlib.Path(base).rglob('*')) if p.is_file() and '.git' not in p.parts}


# ---- protection rules
for rel in ('data/waiting/in/data/fers/US-AK.json.gz', 'data/waiting/approved.json', 'data/waiting/questions/x.json', 'data/us-key/tracts/US-MA.json',
            'data/world-key/FR.json', 'data/ca-key/index.json', 'pdf/KPC_2026_Event_Archive_Photo_Archive.pdf', '.github/scripts/kpc_us_key.py',
            'data/getting-in-switch.json', './data/waiting/in/x.json'):
    check(M.protected(rel), f'protected: {rel}')
for rel in ('data/waiting/previous/data/fers/US-CO.json', 'archive/2026-10/x.json', 'data/fers/review/south.json'):
    check(not M.protected(rel), f'movable: {rel}')
check(all(not M.protected(f + '/x') for g in M.GROUPS.values() for f in g[2]), 'no group folder is a protected path')
check(not M.GROUPS['sources-review'][0], 'sources-review (writer unknown) is OFF unless named')
check(not M.GROUPS['fers-review'][0], 'fers-review is OFF by default (kpc-fers-lines.yml combine step reads data/fers/review/*.json)')

with tempfile.TemporaryDirectory() as td:
    D, A = pathlib.Path(td, 'data'), pathlib.Path(td, 'archive')
    files = {
        'data/waiting/previous/data/fers/US-CO.json': b'{"old":1}' * 1000,
        'data/waiting/previous/data/us-key/US-VA.json': b'{"old":2}' * 500,
        'data/waiting/in/data/fers/US-AK.json.gz': b'HELD' * 700,          # must never move
        'data/waiting/approved.json': b'{"approved":1}',                     # must never move
        'archive/2026-10/world-sources-batch86.json': b'{"b":86}' * 900,
        'archive/2026-10/southeast.json': b'{"r":1}' * 800,
        'data/fers/US-KY.json': b'{"live":1}' * 100,                         # live 2-fer data: stays
        'data/sources/review/no-boundary.csv': b'a,b\n' * 500,               # off by default
        'data/us-key/tracts/US-MA.json': b'{"t":1}' * 300,                   # tracts: stay
        'pdf/KPC_2026_Event_Archive_Photo_Archive.pdf': b'%PDF' * 300,       # stays
    }
    for k, v in files.items(): put(D, k, v)
    before = tree(D)

    # ---- dry run changes nothing and prints the MB
    rc, out = run(['--data', str(D), '--archive', str(A)])
    check(rc == 0 and 'DRY RUN' in out and 'would shrink by' in out and 'nothing copied' in out, 'dry run prints the MB saved')
    check(tree(D) == before and not A.exists(), 'dry run: Data unchanged, Archive not created')
    check('data/waiting/in' not in out.replace('data/waiting/previous', ''), 'dry run never lists held items')

    # ---- unknown group / cap
    check(run(['--data', str(D), '--archive', str(A), '--groups', 'nope'])[0] == 2, 'unknown group refused (exit 2)')
    rc, out = run(['--data', str(D), '--archive', str(A), '--archive-cap-mb', '0.001', '--apply'])
    check(rc == 2 and 'over its cap' in out and tree(D) == before, 'archive cap: refused, nothing deleted')

    # ---- copy-only: copies + manifests, deletes nothing
    rc, out = run(['--data', str(D), '--archive', str(A), '--copy-only', '--source-commit', 'abc123'])
    check(rc == 0 and tree(D) == {**before, 'data/archive-manifest.json': tree(D)['data/archive-manifest.json']}, 'copy-only: Data keeps every file (plus the manifest)')
    arch_files = tree(A)
    moved_expected = {k for k in files if k.startswith(('data/waiting/previous/', 'archive/', 'data/fers/review/'))}
    check(set(arch_files) == moved_expected | {'archive-manifest.json'}, 'copy-only: Archive has exactly the movable groups, same paths, plus its manifest')
    man = json.loads(arch_files['archive-manifest.json'])
    rows = {r['path']: r for r in man['files']}
    check(set(rows) == moved_expected and all(r['source_commit'] == 'abc123' for r in rows.values()), 'manifest: every moved path, source commit recorded')
    check(all(r['sha256'] == hashlib.sha256(files[p]).hexdigest() and r['bytes'] == len(files[p]) for p, r in rows.items()), 'manifest: sha256 and bytes are right')
    check(tree(D)['data/archive-manifest.json'] == arch_files['archive-manifest.json'], 'Data keeps an identical copy of the manifest')
    check(run(['--data', str(D), '--archive', str(A), '--verify'])[0] == 0, '--verify passes')

    # ---- delete-verified: a changed archive copy is NOT trusted
    (A / 'fers-note.txt').write_text('x')
    (A / 'archive/2026-10/southeast.json').write_bytes(b'tampered')
    rc, out = run(['--data', str(D), '--archive', str(A), '--delete-verified'])
    after = tree(D)
    check((D / 'archive/2026-10/southeast.json').exists(), 'delete-verified keeps a file whose archive copy differs')
    check(not (D / 'data/waiting/previous').exists() and sorted(str(x.relative_to(D)) for x in (D / 'archive').rglob('*') if x.is_file()) == ['archive/2026-10/southeast.json'], 'delete-verified removed the verified files and the empty folders')
    check(run(['--data', str(D), '--archive', str(A), '--verify'])[0] == 1, '--verify catches the tampered archive copy')
    (A / 'archive/2026-10/southeast.json').write_bytes(files['archive/2026-10/southeast.json'])

    # ---- full apply (idempotent) on the rest
    rc, out = run(['--data', str(D), '--archive', str(A), '--apply', '--source-commit', 'def456'])
    check(rc == 0 and not (D / 'archive/2026-10/southeast.json').exists(), 'apply: finishes the move')
    man2 = json.loads((A / 'archive-manifest.json').read_text())
    check(all(r['source_commit'] == 'abc123' for r in man2['files']), 'idempotent: rows that are still right keep their first source commit')
    survivors = tree(D); survivors.pop('data/archive-manifest.json')
    check(set(survivors) == set(files) - moved_expected, 'what stayed: held items, approved.json, live fers, sources-review, tracts, the Event Photo PDF')
    check(all(survivors[k] == files[k] for k in survivors), 'what stayed is byte-identical')
    snap = tree(A); snapd = tree(D)
    rc, out = run(['--data', str(D), '--archive', str(A), '--apply'])
    check(rc == 0 and tree(A) == snap and tree(D) == snapd and 'copied 0 files' in out, 'second apply: copies 0 files, changes nothing')
    check(run(['--data', str(D), '--archive', str(A), '--verify'])[0] == 0, '--verify passes after the move')

    # ---- reader fallback (download stubbed)
    calls = []
    def fake_get(u, timeout):
        calls.append(u); rel = u.split('/main/', 1)[1]; return (A / rel).read_bytes()
    KA._get = fake_get
    rel = 'data/waiting/previous/data/fers/US-CO.json'
    check(KA.is_archived(rel, D) and KA.fetch(rel, D) == files[rel], 'reader: an archived path is fetched and its sha256 matches')
    check(calls == ['https://raw.githubusercontent.com/KentuckyPortableClub/KPC-Archive/main/' + rel], 'reader: the raw.githubusercontent.com URL is the same path')
    check(KA.fetch('data/fers/US-KY.json', D) is None and len(calls) == 1, 'reader: a path that never moved is not fetched (no network)')
    check(KA.listing('data/waiting/previous/data/us-key/', D) == ['data/waiting/previous/data/us-key/US-VA.json'], 'reader: listing comes from the manifest')
    KA._get = lambda u, t: b'wrong bytes'
    check(KA.fetch(rel, D) is None, 'reader: bytes that do not match the sha256 are skipped')
    def boom(u, t): raise OSError('offline')
    KA._get = boom
    check(KA.fetch(rel, D) is None, 'reader: offline -> None (skips cleanly)')
    os.environ['KPC_ARCHIVE_FETCH'] = 'off'; KA._get = fake_get; n = len(calls)
    check(KA.fetch(rel, D) is None and len(calls) == n, 'reader: KPC_ARCHIVE_FETCH=off turns the fetch off')
    del os.environ['KPC_ARCHIVE_FETCH']
    check(KA.fetch(rel, A) is None, 'reader: no manifest in that root -> None, no network')

    # ---- the waiting-room undo uses it
    os.environ['DATA'] = str(D)
    import kpc_waiting_room as W
    check(W.DATA == D, 'waiting room reads DATA from the environment')
    live = D / 'data/fers/US-CO.json'; live.parent.mkdir(parents=True, exist_ok=True); live.write_bytes(b'{"live":"new"}')
    KA._get = fake_get
    with contextlib.redirect_stdout(io.StringIO()):
        done = W.mode_undo('data/fers/US-CO.json')
    check(done and live.read_bytes() == files[rel], 'undo: puts back the copy that moved to KPC-Archive')
    check((D / rel).read_bytes() == b'{"live":"new"}', 'undo: the replaced live copy becomes "previous" again (undo of the undo)')
    with contextlib.redirect_stdout(io.StringIO()) as so:
        no = W.mode_undo('data/fers/US-ZZ.json')
    check(no is False, 'undo: a file that was never archived still says "no copy" and returns False')
    KA._get = boom
    (D / rel).unlink()
    with contextlib.redirect_stdout(io.StringIO()):
        off = W.mode_undo('data/fers/US-CO.json')
    check(off is False and live.read_bytes() == files[rel], 'undo: archive unreachable -> skips cleanly, live file untouched')
    KA._get = fake_get
    live2 = D / 'data/us-key/US-VA.json'; live2.parent.mkdir(parents=True, exist_ok=True); live2.write_bytes(b'{"live":"va"}')
    with contextlib.redirect_stdout(io.StringIO()):
        W.mode_undo_bot('us-key', 'US-VA')
    check(live2.read_bytes() == files['data/waiting/previous/data/us-key/US-VA.json'], 'undo-bot: finds an archived copy through the manifest')

# ---- a protected file inside a group folder is skipped, never an abort (Fable review: a switch's undo copy must not block rotation)
with tempfile.TemporaryDirectory() as td:
    D, A = pathlib.Path(td, 'data'), pathlib.Path(td, 'archive')
    put(D, 'data/waiting/previous/data/getting-in-switch.json', b'{"on":false}')
    put(D, 'data/waiting/previous/data/fers/US-CO.json', b'{"x":1}' * 50)
    rc, out = run(['--data', str(D), '--archive', str(A), '--groups', 'previous', '--apply', '--source-commit', 't'])
    check(rc == 0 and 'is protected and stays' in out, 'switch undo copy: run finishes with a notice (no abort)')
    check((D / 'data/waiting/previous/data/getting-in-switch.json').exists(), 'switch undo copy stays in KPC-Data')
    check(not (D / 'data/waiting/previous/data/fers/US-CO.json').exists() and (A / 'data/waiting/previous/data/fers/US-CO.json').exists(),
          'the rest of the group still moves')
    check([r['path'] for r in json.loads((A / 'archive-manifest.json').read_text())['files']] == ['data/waiting/previous/data/fers/US-CO.json'],
          'manifest never lists the protected file')

# ---- the age filter (a real git repo; commit dates set by hand)
with tempfile.TemporaryDirectory() as td:
    D, A = pathlib.Path(td, 'data'), pathlib.Path(td, 'archive'); D.mkdir()
    env = {**os.environ, 'GIT_AUTHOR_NAME': 'x', 'GIT_AUTHOR_EMAIL': 'x@x', 'GIT_COMMITTER_NAME': 'x', 'GIT_COMMITTER_EMAIL': 'x@x'}
    def g(*a, **k): subprocess.run(['git', '-C', str(D), *a], check=True, capture_output=True, env={**env, **k})
    g('init', '-q', '-b', 'main')
    put(D, 'data/waiting/previous/data/a/old.json', b'{"o":1}'); g('add', '-A')
    g('commit', '-qm', 'old', GIT_AUTHOR_DATE='2026-10-01T00:00:00Z', GIT_COMMITTER_DATE='2026-10-01T00:00:00Z')
    put(D, 'data/waiting/previous/data/a/new.json', b'{"n":1}'); g('add', '-A')
    g('commit', '-qm', 'new', GIT_AUTHOR_DATE='2026-11-06T00:00:00Z', GIT_COMMITTER_DATE='2026-11-06T00:00:00Z')
    put(D, 'data/waiting/previous/data/a/untracked.json', b'{"u":1}')
    now = time.mktime(time.strptime('2026-11-07', '%Y-%m-%d'))
    rc, out = run(['--data', str(D), '--archive', str(A), '--groups', 'previous', '--older-than-days', '14', '--now', str(now), '--copy-only'])
    got = sorted(tree(A))
    check(rc == 0 and got == ['archive-manifest.json', 'data/waiting/previous/data/a/old.json'], 'older-than-14-days: moves only the old tracked file; new and untracked (age unknown) stay')
    check('2 kept' in out or ' 2 kept' in out, 'older-than-14-days: reports what was kept')
    head = subprocess.run(['git', '-C', str(D), 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
    check(json.loads((A / 'archive-manifest.json').read_text())['files'][0]['source_commit'] == head, 'manifest records the git HEAD of Data as the source commit')

# ---- the rotate workflow: by hand only, a secret NAME only, safe order
import re
try:
    import yaml
    wf_path = ROOT / '.github/workflows/kpc-archive-rotate.yml'
    wf = yaml.safe_load(wf_path.read_text(encoding='utf-8')); wf['on'] = wf.pop(True, wf.get('on'))
    txt = wf_path.read_text(encoding='utf-8')
    check(sorted(wf['on']) == ['schedule', 'workflow_dispatch'] and [c['cron'] for c in wf['on']['schedule']] == ['27 15 * * 3'], 'rotate workflow: weekly (Brandon Nov 7) + by hand, no workflow_run')
    check(wf['on']['workflow_dispatch']['inputs']['dry_run']['default'] == 'true' and wf['on']['workflow_dispatch']['inputs']['older_than_days']['default'] == '14',
          'rotate workflow: dry run and 14 days are the defaults')
    check(set(re.findall(r'secrets\.(\w+)', txt)) == {'KPC_ARCHIVE_TOKEN'} and not re.search(r'gh[pous]_[A-Za-z0-9]{10,}|github_pat_', txt), 'rotate workflow: only the secret NAME KPC_ARCHIVE_TOKEN, no token value')
    names = [st.get('name') or '' for st in wf['jobs']['rotate']['steps']]
    order = [next(i for i, n in enumerate(names) if k in n) for k in ('Copy into', 'Push KPC-Archive', 'Delete from KPC-Data', 'Push KPC-Data')]
    check(order == sorted(order), 'rotate workflow: copy -> push archive -> delete -> push data (nothing deleted before the archive push)')
    check(wf['concurrency']['group'] == 'kpc-waiting-room', 'rotate workflow: shares the waiting room lock')
    check('data/waiting/in' not in txt.replace('data/waiting/in/ are never touched', '').replace('data/waiting/in/', ''), 'rotate workflow: never names the held folder as a target')
except ImportError:
    print('SKIP rotate workflow checks (PyYAML not installed)')

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
