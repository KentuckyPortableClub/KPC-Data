#!/usr/bin/env python3
"""kpc_archive_move.py: move bulk, rarely-read files from a KPC-Data checkout into a KPC-Archive checkout (Nov 7 2026).

  python3 kpc_archive_move.py --data . --archive ../archive                  DRY RUN (the default): prints what would move and the MB saved
  python3 kpc_archive_move.py --data . --archive ../archive --apply          copy -> verify sha256 -> write both manifests -> delete from Data
  ... --copy-only          copy + verify + manifests, delete nothing (the rotate workflow pushes KPC-Archive first, then deletes)
  ... --delete-verified    delete from Data only the files whose copy in the archive checkout has the same sha256
  ... --verify             check every manifest entry against the archive checkout (exit 1 on a mismatch)
  --groups previous,archive,fers-review[,sources-review]   (default: the groups marked default below)
  --older-than-days N      only files whose last git change in --data is older than N days (unknown age = kept). The 'previous' group
                           for the rotation uses 14; the one-time move uses 0 (all of it).
  --archive-cap-mb 500     refuse (exit 2) if the archive checkout would end above this size
  --source-commit SHA      recorded in the manifest (default: git rev-parse HEAD of --data, else 'unknown')

Same paths on both sides. archive-manifest.json (path, sha256, bytes, source_commit) is written at the root of the archive checkout and,
as data/archive-manifest.json, in Data (readers use it to know what moved; see kpc_archive.py). Idempotent: a second run copies nothing,
keeps each manifest row that is still right, deletes nothing more. Standard library only; NO network calls (git is run locally, if present).
NEVER moves: anything under data/waiting/ except data/waiting/previous/ (held items wait for grading and approval), the key folders and
rule files (rules hashes), the Event Photo Archive PDF, workflow / script files, and switch files. Exit: 0 ok, 1 verify/copy failure, 2 refused."""
import argparse, datetime as dt, hashlib, json, os, pathlib, shutil, subprocess, sys, time

GROUPS = {   # name: (default?, confidence, folders, why)
    'previous': (True, 'high', ['data/waiting/previous'],
                 'undo copies of files the waiting room replaced; read only by kpc_waiting_room.py undo / undo-bot (falls back to KPC-Archive)'),
    'archive': (True, 'medium', ['archive'],
                'the club\'s own dated archive folder (archive/2026-10: old batches); no reader found in the code handed over'),
    'fers-review': (True, 'medium', ['data/fers/review'],
                    'per-run "needs a human look" dumps; written by kpc-fers-line.yml, no bot reader found (the combined list already lives on tools-out)'),
    'sources-review': (False, 'low', ['data/sources/review'],
                       'review CSVs (no-boundary, inside-other-land); writer and readers are not in the code handed over: OFF unless named in --groups'),
}
NEVER_EXACT = {'pdf/KPC_2026_Event_Archive_Photo_Archive.pdf', 'data/getting-in-switch.json', 'data/tract-switch.json', '.github/key-rules-version.json',
               'data/archive-manifest.json', 'archive-manifest.json'}
NEVER_PREFIX = ('data/waiting/in/', 'data/us-key/', 'data/ca-key/', 'data/world-key/', '.github/', 'pdf/')
KEEP_UNDER_WAITING = 'data/waiting/previous/'
MANIFEST_NAME = 'archive-manifest.json'
DATA_MANIFEST = 'data/archive-manifest.json'


def protected(rel):
    rel = rel.replace('\\', '/')
    while rel.startswith('./'): rel = rel[2:]
    if rel in NEVER_EXACT or any(rel.startswith(p) for p in NEVER_PREFIX): return True
    if rel.startswith('data/waiting/') and not rel.startswith(KEEP_UNDER_WAITING): return True
    if 'switch' in pathlib.PurePosixPath(rel).name.lower(): return True
    return False


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''): h.update(chunk)
    return h.hexdigest()


def tree_bytes(root, skip_git=True):
    n = 0
    for dp, dns, fns in os.walk(root):
        if skip_git and '.git' in dns: dns.remove('.git')
        for f in fns:
            try: n += os.path.getsize(os.path.join(dp, f))
            except OSError: pass
    return n


def git(root, *args):
    try:
        r = subprocess.run(['git', '-C', str(root), *args], capture_output=True, text=True, timeout=300)
        return r.stdout if r.returncode == 0 else None
    except Exception: return None  # noqa: BLE001


def last_change_times(data, folder):
    """{relpath: epoch of the newest commit that touched it} for one folder; {} when --data is not a git checkout."""
    out = git(data, 'log', '--format=@%ct', '--name-only', '--no-renames', '--', folder)
    t, res = None, {}
    for line in (out or '').splitlines():
        if line.startswith('@'): t = int(line[1:]); continue
        if line.strip() and t is not None and line not in res: res[line] = t
    return res


def collect(data, group, older_days, now):
    """-> (files to move [(rel, abs, bytes)], kept [(rel, bytes)]: too new, age unknown, or protected).
    A protected file inside a group folder (say a switch file's undo copy in data/waiting/previous) is SKIPPED with a notice and
    stays in KPC-Data; it never aborts the run, or one such file would block every later rotation (Fable review, Nov 7)."""
    move, kept = [], []
    for folder in GROUPS[group][2]:
        root = pathlib.Path(data) / folder
        if not root.is_dir(): continue
        times = last_change_times(data, folder) if older_days > 0 else {}
        for dp, dns, fns in os.walk(root):
            dns.sort()
            for f in sorted(fns):
                ap = pathlib.Path(dp) / f
                if ap.is_symlink() or not ap.is_file(): continue
                rel = ap.relative_to(data).as_posix()
                size = ap.stat().st_size
                if protected(rel):
                    print(f'::notice title=Archive move::{rel} is protected and stays in KPC-Data (group {group})')
                    kept.append((rel, size)); continue
                if older_days > 0:
                    t = times.get(rel)
                    if t is None or now - t < older_days * 86400: kept.append((rel, size)); continue
                move.append((rel, ap, size))
    return move, kept


def read_manifest(path):
    try: return {r['path']: r for r in json.loads(pathlib.Path(path).read_text(encoding='utf-8')).get('files') or []}
    except Exception: return {}  # noqa: BLE001


def write_manifest(path, rows):
    doc_head = {'about': 'Files moved from KPC-Data to KPC-Archive by kpc_archive_move.py. Same paths on both sides. '
                         'Readers fetch https://raw.githubusercontent.com/KentuckyPortableClub/KPC-Archive/main/<path> and check the sha256.',
                'repo': 'KentuckyPortableClub/KPC-Archive', 'count': len(rows)}
    body = ',\n'.join(' ' + json.dumps(rows[p], sort_keys=True, ensure_ascii=False) for p in sorted(rows))
    text = json.dumps(doc_head, ensure_ascii=False)[:-1] + ',\n"files": [\n' + body + '\n]}\n'
    p = pathlib.Path(path)
    if p.exists() and p.read_text(encoding='utf-8') == text: return False
    p.parent.mkdir(parents=True, exist_ok=True); p.write_text(text, encoding='utf-8'); return True


def mb(n): return f'{n / 1e6:,.1f} MB'


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--data', default='.'); ap.add_argument('--archive', required=True)
    ap.add_argument('--groups', default=''); ap.add_argument('--older-than-days', type=float, default=0)
    ap.add_argument('--archive-cap-mb', type=float, default=500); ap.add_argument('--source-commit', default='')
    ap.add_argument('--now', type=float, default=0, help='epoch seconds (tests)')
    g = ap.add_mutually_exclusive_group()
    g.add_argument('--apply', action='store_true'); g.add_argument('--copy-only', action='store_true')
    g.add_argument('--delete-verified', action='store_true'); g.add_argument('--verify', action='store_true')
    a = ap.parse_args(argv)
    data, arch = pathlib.Path(a.data), pathlib.Path(a.archive)
    names = [x.strip() for x in a.groups.split(',') if x.strip()] or [k for k, v in GROUPS.items() if v[0]]
    bad = [n for n in names if n not in GROUPS]
    if bad: print(f'unknown group(s): {bad}; known: {list(GROUPS)}', file=sys.stderr); return 2
    for n in GROUPS:   # the group folders themselves must never be protected paths
        for f in GROUPS[n][2]:
            if protected(f + '/x'): print(f'REFUSED: group {n} folder {f} is protected', file=sys.stderr); return 2
    mpath_a, mpath_d = arch / MANIFEST_NAME, data / DATA_MANIFEST
    now = a.now or time.time()

    if a.verify:
        rows = read_manifest(mpath_a); badn = 0
        for p, r in rows.items():
            f = arch / p
            if not f.is_file() or sha256(f) != r.get('sha256'): print(f'MISMATCH {p}'); badn += 1
        print(f'verify: {len(rows)} manifest rows, {badn} mismatch(es)'); return 1 if badn else 0

    if a.delete_verified:
        gone = freed = 0
        for n in names:
            move, _ = collect(data, n, a.older_than_days, now)
            for rel, ap_, size in move:
                f = arch / rel
                if f.is_file() and sha256(f) == sha256(ap_): ap_.unlink(); gone += 1; freed += size
            for folder in GROUPS[n][2]:
                for dp, dns, fns in os.walk(data / folder, topdown=False):
                    if not os.listdir(dp): os.rmdir(dp)
        print(f'delete-verified: {gone} files deleted from Data, {mb(freed)} freed'); return 0

    plan, total_move, total_kept, rows_new = {}, 0, 0, 0
    manifest = read_manifest(mpath_a)
    commit = a.source_commit or (git(data, 'rev-parse', 'HEAD') or 'unknown').strip() or 'unknown'
    for n in names:
        move, kept = collect(data, n, a.older_than_days, now)
        plan[n] = (move, kept); total_move += sum(s for _, _, s in move); total_kept += sum(s for _, s in kept)
    start = tree_bytes(arch) if arch.is_dir() else 0
    new_bytes = 0
    for n in names:
        for rel, _, size in plan[n][0]:
            if not (arch / rel).is_file(): new_bytes += size
    data_size = tree_bytes(data)
    print(f'{"APPLY" if (a.apply or a.copy_only) else "DRY RUN"}: groups {names}; older than {a.older_than_days:g} days; source commit {commit[:12]}')
    for n in names:
        move, kept = plan[n]
        print(f'  {n:15s} [{GROUPS[n][1]:6s}] {len(move):5d} files {mb(sum(s for _, _, s in move)):>10s} to move;'
              f' {len(kept):4d} kept (too new / age unknown / protected) {mb(sum(s for _, s in kept))}')
    print(f'KPC-Data now {mb(data_size)} on disk; would shrink by {mb(total_move)} -> {mb(data_size - total_move)}')
    print(f'KPC-Archive starts at {mb(start)}; this run adds {mb(new_bytes)} -> {mb(start + new_bytes)} (cap {a.archive_cap_mb:g} MB)')
    if start + new_bytes > a.archive_cap_mb * 1e6: print('REFUSED: the archive would go over its cap', file=sys.stderr); return 2
    if not (a.apply or a.copy_only): print('(dry run: nothing copied, nothing deleted; add --apply)'); return 0

    arch.mkdir(parents=True, exist_ok=True); copied = 0; fail = 0
    for n in names:
        for rel, ap_, size in plan[n][0]:
            dst = arch / rel; digest = sha256(ap_)
            if dst.is_file() and sha256(dst) == digest: pass
            else:
                dst.parent.mkdir(parents=True, exist_ok=True); tmp = dst.with_name(dst.name + '.part'); shutil.copyfile(ap_, tmp); os.replace(tmp, dst); copied += 1
                if sha256(dst) != digest: print(f'COPY MISMATCH {rel}', file=sys.stderr); fail += 1; continue
            old = manifest.get(rel)
            if not old or old.get('sha256') != digest or old.get('bytes') != size:
                manifest[rel] = {'path': rel, 'sha256': digest, 'bytes': size, 'source_commit': commit}; rows_new += 1
    if fail: return 1
    write_manifest(mpath_a, manifest); write_manifest(mpath_d, manifest)
    print(f'copied {copied} files; manifest has {len(manifest)} rows ({rows_new} new or changed)')
    if a.copy_only: return 0
    return main(['--data', a.data, '--archive', a.archive, '--delete-verified', '--groups', ','.join(names), '--older-than-days', str(a.older_than_days), '--now', str(now)])


if __name__ == '__main__':
    sys.exit(main())
