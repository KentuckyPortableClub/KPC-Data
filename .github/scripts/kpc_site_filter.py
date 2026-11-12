#!/usr/bin/env python3
"""KPC-Data: build the tree the Pages branch 'site' publishes, holding ONLY the paths .github/site-allow-list.txt keeps.
KPC owner, 2026-11-11 (storage round 2: the owner's go for 'site carries only what the pages read').

  python3 .github/scripts/kpc_site_filter.py build [--repo .] [--rev origin/main] [--allow .github/site-allow-list.txt]
          [--previous origin/site] [--max-loss 0.10] [--min-files 500] [--dry-run] [--json FILE]
  python3 .github/scripts/kpc_site_filter.py check-readers LINKS_CHECKOUT [APP_CHECKOUT ...] [--repo .] [--rev origin/main] [--allow ...]

build: reads the commit REV's tree (git ls-tree; works on a blobless or sparse clone, never needs file contents), keeps the
  allow-listed paths, and (unless --dry-run) writes ONE tree and ONE commit object: parent = REV, author / committer
  github-actions[bot], dates = REV's commit date, message 'site: published copy of main <sha> (allow-list <hash>)'. The same main +
  the same allow-list always give the same commit sha. Prints before / after file counts and bytes (bytes 'unknown' when the
  clone has no file contents) and the last lines  TREE=<sha>  COMMIT=<sha>  PUBLISH=yes|no. It never moves a branch and never
  touches main: pushing COMMIT to 'site' is the workflow's job.
  FAIL CLOSED (exit 3, PUBLISH=no, nothing written): the allow-list is missing, empty, or has a line it cannot read (every pattern
  needs a '# reader' note); .nojekyll would be missing; fewer than --min-files files would be published; or, compared with
  --previous, more than --max-loss of the previous site's files (or bytes, when known) would disappear: every file of a filtered
  previous site, so a narrowed allow-list is caught as well; only the allow-listed ones of an old whole-main site.
  (--min-files defaults to 500, or KPC_SITE_MIN_FILES; KPC-Data publishes about 20,500.)
  KPC_SITE_ALLOW_LOSS=yes lets a deliberate big drop through once (a person decides).
check-readers: re-reads the pages and scripts that fetch from the KPC-Data Pages site (every .html / .js / .css / small .json of
  the given checkouts outside .claude/ tests/ docs/, plus any file of theirs or of this repo naming the Data Pages host) and pulls out
  every 'data/...', 'pdf/...' and 'locations-*.json' string. A string naming a file or folder that exists in REV but is not
  allow-listed = FAIL (exit 1): a page would 404. A folder string only partly allow-listed = WARN (a name built in code: check it).

Patterns (one per line, '#' starts the reader note; blank and comment lines are skipped). A line starting with '!' keeps the
matching paths OFF the site whatever the other lines say (e.g. '!data/fers/W-*  # world 2-fers: club-room only'); check-readers
then FAILS any page that requests such a path, or builds a name into it without a world-area guard in the 8 lines above.
  folder/            the folder and everything under it
  path/file.json     that one file
  data/fers/US-*.json    '*' matches inside one name (not '/'), '**' matches across folders
Always kept when they exist: .nojekyll (required), CNAME, index.html, 404.html, robots.txt, favicon.ico.
Standard library only, no network (git runs with no transport allowed)."""
import argparse, collections, hashlib, json, os, re, subprocess, sys, tempfile

ALWAYS = ('.nojekyll', 'CNAME', 'index.html', '404.html', 'robots.txt', 'favicon.ico')
GITENV = dict(os.environ, GIT_ALLOW_PROTOCOL='kpc-none', GIT_NO_LAZY_FETCH='1', GIT_TERMINAL_PROMPT='0', LC_ALL='C')
HOST = 'kentuckyportableclub.github.io/KPC-Data/'
PAT_OK = re.compile(r'^[A-Za-z0-9_.*/@+-]+$')


class Fail(Exception): pass


def git(repo, *a, inp=None, env=None, binary=False):
    r = subprocess.run(['git', '-C', repo, *a], input=inp, capture_output=True, env=env or GITENV)
    if r.returncode: raise Fail(f"git {' '.join(a)[:60]}: {r.stderr.decode('utf-8', 'replace').strip()[:200]}")
    return r.stdout if binary else r.stdout.decode('utf-8', 'replace')


def parse_allow(path):
    """[(pattern, regex, reader note)]; Fail on a missing / empty / unreadable list."""
    try: text = open(path, encoding='utf-8').read()
    except OSError as e: raise Fail(f'allow-list {path} cannot be read ({e.strerror})')
    out = []
    for n, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith('#'): continue
        pat, sep, note = line.partition('#')
        pat, note = pat.strip(), note.strip()
        if not sep or not note: raise Fail(f'allow-list line {n}: {line[:80]!r} has no "# reader" note')
        deny = pat.startswith('!')
        if deny: pat = pat[1:]
        if ' ' in pat or not pat or not PAT_OK.match(pat) or pat.startswith('/') or '..' in pat.split('/'):
            raise Fail(f'allow-list line {n}: {pat[:80]!r} is not a path pattern')
        rx = ''
        i = 0
        while i < len(pat):
            if pat.startswith('**', i): rx += '.*'; i += 2
            elif pat[i] == '*': rx += '[^/]*'; i += 1
            else: rx += re.escape(pat[i]); i += 1
        rx = '^' + rx + ('.*' if pat.endswith('/') else '') + '$'
        out.append((('!' if deny else '') + pat, re.compile(rx), note))
    if not [x for x in out if not x[0].startswith('!')]: raise Fail(f'allow-list {path} has no pattern')
    return out


def denied(path, pats):
    """The '!' line that keeps this path OFF the public site (it wins over every allow line), or None."""
    return next(((p, note) for p, rx, note in pats if p.startswith('!') and rx.match(path)), None)


def allowed(path, pats):
    if denied(path, pats): return False
    return path in ALWAYS or any(rx.match(path) for p, rx, _ in pats if not p.startswith('!'))


def deny_prefix(p):
    """The literal start of a '!' pattern (before its first '*'), e.g. '!data/fers/W-*' -> 'data/fers/W-'."""
    return p[1:].split('*', 1)[0]


GUARD = re.compile(r"""/\^?W-|['"]W-['"]|\(US\|CA\)|\^\(\?:US\|CA\)""")   # an area test that keeps world names out


def tree(repo, rev):
    """{path: (mode, sha, size or None)} of the commit's tree, without reading file contents."""
    try:
        out = git(repo, 'ls-tree', '-r', '-l', '-z', rev)
        sized = True
    except Fail:   # a blobless clone: sizes need contents; names and ids do not
        out = git(repo, 'ls-tree', '-r', '-z', rev); sized = False
    files = {}
    for rec in out.split('\0'):
        if '\t' not in rec: continue
        meta, p = rec.split('\t', 1); f = meta.split()
        if f[1] != 'blob' and f[1] != 'commit': continue
        size = int(f[3]) if sized and len(f) > 3 and f[3].isdigit() else None
        files[p] = (f[0], f[2], size)
    return files


def sums(files):
    known = [s for _, _, s in files.values() if s is not None]
    return len(files), (sum(known) if len(known) == len(files) else None)


def mb(b): return 'unknown' if b is None else f'{b / 1e6:,.1f} MB'


def groups(files):
    g = collections.defaultdict(lambda: [0, 0])
    for p, (_, _, s) in files.items():
        parts = p.split('/')
        k = (parts[0] + '/' + parts[1] + '/') if parts[0] == 'data' and len(parts) > 2 else (parts[0] + '/' if len(parts) > 1 else '(root files)')
        g[k][0] += 1; g[k][1] += s or 0
    return g


def build(a):
    repo = a.repo
    pats = parse_allow(a.allow)
    rev = git(repo, 'rev-parse', '--verify', a.rev + '^{commit}').strip()
    src = tree(repo, rev)
    if not src: raise Fail(f'{a.rev} has no files')
    keep = {p: v for p, v in src.items() if allowed(p, pats)}
    if '.nojekyll' not in keep: raise Fail('.nojekyll would be missing: GitHub would run Jekyll on the site')
    if len(keep) < a.min_files: raise Fail(f'only {len(keep)} files would be published (minimum {a.min_files})')
    n0, b0 = sums(src); n1, b1 = sums(keep)
    say = []
    say.append(f'main {rev[:12]}: {n0:,} files, {mb(b0)}  ->  site: {n1:,} files, {mb(b1)}  (dropped {n0 - n1:,} files'
               + (f', {mb(b0 - b1)})' if b0 is not None and b1 is not None else ')'))
    unused = [p for p, rx, _ in pats if not p.startswith('!') and not any(rx.match(x) for x in src)]
    leak = [p for p in keep if denied(p, pats)]
    if leak: raise Fail(f'a denied path would be published: {leak[:5]}')
    nden = sum(1 for p in src if denied(p, pats))
    if nden: say.append(f'kept OFF the site by the ! lines: {nden} file(s) (' + '; '.join(f'{p} = {note}' for p, _, note in pats if p.startswith('!')) + ')')
    if unused: say.append(f'note: {len(unused)} allow-list pattern(s) match nothing in main: {" ".join(unused[:10])}')
    prev_info = {}
    if a.previous:
        try: prev_sha = git(repo, 'rev-parse', '--verify', a.previous + '^{commit}').strip()
        except Fail: prev_sha = ''
        if prev_sha:
            prev = tree(repo, prev_sha)
            # a filtered previous site: everything it published counts (so narrowing the list is caught too); the old whole-main site:
            # only what the list keeps (the first filtered publish drops the rest on purpose)
            was_filtered = git(repo, 'log', '-1', '--format=%s', prev_sha).startswith('site: published copy of main ')
            pk = dict(prev) if was_filtered else {p: v for p, v in prev.items() if allowed(p, pats)}
            lost = {p: v for p, v in pk.items() if p not in keep}
            share_n = len(lost) / max(len(pk), 1)
            pb = sum(s or 0 for _, _, s in pk.values()); lb = sum(s or 0 for _, _, s in lost.values())
            known = all(s is not None for _, _, s in pk.values())
            share_b = (lb / pb) if known and pb else 0.0
            prev_info = {'previous': prev_sha, 'previous_files': len(prev), 'previous_allowed': len(pk), 'lost': len(lost),
                         'lost_share_files': round(share_n, 4), 'lost_share_bytes': round(share_b, 4) if known else None}
            say.append(f'previous site {prev_sha[:12]} ({"filtered" if was_filtered else "whole main"}): {len(prev):,} files, {len(pk):,} of them counted; '
                       f'{len(lost):,} of those would disappear ({share_n:.1%} of files' + (f', {share_b:.1%} of bytes)' if known else ')'))
            if (share_n > a.max_loss or share_b > a.max_loss) and os.environ.get('KPC_SITE_ALLOW_LOSS') != 'yes':
                ex = ' '.join(sorted(lost)[:8])
                raise Fail(f'the new site would lose {share_n:.1%} of the files (or {share_b:.1%} of the bytes) the previous '
                           f'{"filtered" if was_filtered else "whole-main"} site '
                           f'published under the allow-list (limit {a.max_loss:.0%}), e.g. {ex}. Nothing published. '
                           'If that drop is meant, a person runs once with KPC_SITE_ALLOW_LOSS=yes.')
    g0, g1 = groups(src), groups(keep)
    rows = sorted(g0, key=lambda k: -g0[k][1])
    allow_hash = hashlib.sha256(open(a.allow, 'rb').read()).hexdigest()[:12]
    result = {'main': rev, 'files_before': n0, 'bytes_before': b0, 'files_after': n1, 'bytes_after': b1, 'allow_list': allow_hash,
              'folders': {k: {'before': g0[k], 'after': g1.get(k, [0, 0])} for k in rows}, **prev_info}
    tree_sha = commit = ''
    if not a.dry_run:
        with tempfile.TemporaryDirectory(prefix='kpc-site-') as tmp:
            env = dict(GITENV, GIT_INDEX_FILE=os.path.join(tmp, 'index'))
            info = ''.join(f'{m} {s}\t{p}\0' for p, (m, s, _) in sorted(keep.items()))
            git(repo, 'update-index', '-z', '--index-info', inp=info.encode('utf-8'), env=env)
            tree_sha = git(repo, 'write-tree', '--missing-ok', env=env).strip()
        when = git(repo, 'log', '-1', '--format=%cI', rev).strip()
        cenv = dict(GITENV, GIT_AUTHOR_NAME='github-actions[bot]', GIT_AUTHOR_EMAIL='41898282+github-actions[bot]@users.noreply.github.com',
                    GIT_COMMITTER_NAME='github-actions[bot]', GIT_COMMITTER_EMAIL='41898282+github-actions[bot]@users.noreply.github.com',
                    GIT_AUTHOR_DATE=when, GIT_COMMITTER_DATE=when)
        msg = f'site: published copy of main {rev} (allow-list {allow_hash}; {n1} of {n0} files)\n'
        commit = git(repo, 'commit-tree', tree_sha, '-p', rev, inp=msg.encode(), env=cenv).strip()
        result.update(tree=tree_sha, commit=commit)
    for line in say: print(line)
    print('by folder (before -> after):')
    for k in rows[:40]:
        b, f = g0[k], g1.get(k, [0, 0])
        print(f'  {k:<34} {b[0]:>6} files {mb(b[1] if b0 is not None else None):>10}  ->  {f[0]:>6} files' + ('' if f[0] else '   DROPPED'))
    if a.json:
        with open(a.json, 'w', encoding='utf-8') as fh: json.dump(result, fh, indent=1)
    print(f'TREE={tree_sha}'); print(f'COMMIT={commit}'); print(f'PUBLISH={"no" if a.dry_run else "yes"}')
    return 0


STR = re.compile(r'''(["'`])((?:(?!\1)[^\\\n]|\\.){1,400})\1''')
REFS = re.compile(r'(?:^|[^A-Za-z0-9_-])((?:data|pdf)/[A-Za-z0-9_./@+-]*|locations-[a-z]+\.json)')
SKIP_DIRS = ('.claude/', 'tests/', 'docs/', 'node_modules/', '.git/')


def reader_files(root):
    allf = []
    for d, subs, names in os.walk(root):
        subs[:] = [s for s in subs if s not in ('.git', 'node_modules', '__pycache__')]
        for n in names:
            if n.endswith(('.pyc', '.pyo')) or n in ('kpc_site_filter.py', 'site-allow-list.txt'): continue   # never the filter's own files
            rel = os.path.relpath(os.path.join(d, n), root).replace(os.sep, '/')
            allf.append(rel)
    for rel in allf:
        low = rel.lower(); full = os.path.join(root, rel)
        try: size = os.path.getsize(full)
        except OSError: continue
        if size > 3_000_000: continue
        page = low.endswith(('.html', '.htm', '.js', '.mjs', '.css', '.webmanifest')) and not rel.startswith(SKIP_DIRS + ('.github/',))
        # a JSON file is a reader only when a page uses it as a list of names: the root page configs (kpc-fers-regions.json ...);
        # the bots' own JSON outputs under data/ name paths but fetch nothing
        small_json = low.endswith(('.json', '.webmanifest')) and '/' not in rel and size <= 300_000
        try: text = open(full, encoding='utf-8', errors='replace').read()
        except OSError: continue
        if page or small_json or (HOST in text and not rel.startswith(SKIP_DIRS)):
            yield rel, text


def refs_in(text):
    """[(line, ref)] of data/ pdf/ locations- strings: the text up to the first ${ or quote is the known part of the name."""
    out = []
    for m in STR.finditer(text):
        s = m.group(2)
        if '${' in s: s = s.split('${', 1)[0]
        s = s.split('?', 1)[0].split('#', 1)[0]
        if HOST in s: s = s.split(HOST, 1)[1]
        elif '../KPC-Data/' in s: s = s.split('../KPC-Data/', 1)[1]
        for r in REFS.finditer(s):
            ref = r.group(1).rstrip('.')
            if ref in ('data/', 'pdf/') or len(ref) > 3: out.append((text.count('\n', 0, m.start()) + 1, ref))
    return out


def check_readers(a):
    pats = parse_allow(a.allow)
    rev = git(a.repo, 'rev-parse', '--verify', a.rev + '^{commit}').strip()
    data = set(tree(a.repo, rev))
    roots = [(r, os.path.basename(os.path.abspath(r))) for r in a.checkouts]
    if os.path.isdir(a.repo): roots.append((a.repo, 'KPC-Data'))
    fails, warns, ok = [], [], 0
    seen = set()
    dpats = [(p, note) for p, _, note in pats if p.startswith('!')]
    for root, label in roots:
        if label == 'KPC-Data': continue
        reg = os.path.join(root, 'kpc-fers-regions.json')   # the Overlap Finder's region list: every file it names must be published
        if os.path.isfile(reg):
            try: regions = json.load(open(reg, encoding='utf-8')).get('regions') or []
            except (OSError, ValueError): regions = None; fails.append(f'FAIL {label}:kpc-fers-regions.json cannot be read')
            for r in regions or []:
                for f in (r.get('files') or []) + ([r['missing']] if r.get('missing') else []):
                    cands = [f'data/fers/{f}.json', f'data/fers/{f}.json.gz']
                    d = next((denied(c, pats) for c in cands if denied(c, pats)), None)
                    if d: fails.append(f'FAIL {label}:kpc-fers-regions.json region {r.get("id")} names {f}: kept off the public site ({d[1]})')
                    elif not any(c in data and allowed(c, pats) for c in cands):
                        fails.append(f'FAIL {label}:kpc-fers-regions.json region {r.get("id")} names {f}: not published (data/fers/{f}.json(.gz) not kept)')
                    else: ok += 1
    for root, label in roots:
        for rel, text in reader_files(root):
            if label == 'KPC-Data' and not (rel.count('/') == 0 and rel.endswith(('.html', '.js'))) and HOST not in text: continue
            for line, ref in refs_in(text):
                key = (label, rel, line, ref)
                if key in seen: continue
                seen.add(key)
                exact = ref in data
                under = [p for p in data if p.startswith(ref)] if not exact else []
                where = f'{label}:{rel}:{line}'
                if label != 'KPC-Data':
                    hit = next(((p, note) for p, note in dpats if (exact and denied(ref, pats)) or ref.startswith(deny_prefix(p))), None)
                    if hit:
                        fails.append(f'FAIL {where} reads {ref}: kept OFF the public site by {hit[0]} ({hit[1]}); the page must not request it'); continue
                    dn = [p for p in under if denied(p, pats)]
                    # only CODE that builds a name at least as deep as a '!' line's folder ('data/fers/' + area): not JSON text,
                    # not a bare 'data/fers' label, not the generic 'data/' (those stay WARNs, resolved by hand in the list)
                    deep = any(ref.startswith(deny_prefix(p).rsplit('/', 1)[0] + '/') for p, _ in dpats)
                    if dn and not exact and deep and not rel.endswith(('.json', '.webmanifest')):
                        lines = text.splitlines()[max(0, line - 9):line]
                        if 'kpc-fers-regions.json' in text:
                            warns.append(f'WARN {where} builds a name from {ref!r}: names come from kpc-fers-regions.json (checked above)')
                        elif GUARD.search('\n'.join(lines)):
                            warns.append(f'WARN {where} builds a name from {ref!r}: a world-area guard is in the lines above (check it by eye)')
                        else:
                            fails.append(f'FAIL {where} builds a name from {ref!r} with no guard against world areas in the 8 lines above: it can request '
                                         f'{deny_prefix(next(p for p, _ in dpats if any(denied(x, pats) for x in dn)))}* files, which the public site does not '
                                         f'carry ({len(dn)} of {len(under)} files under {ref} are kept off). Skip those areas before the fetch '
                                         "(e.g. if (/^W-/.test(area)) ...) or read the names from a checked list.")
                        continue
                if not exact and not under: continue          # not a KPC-Data path (a KPC-Links file, a name built further)
                if exact:
                    if allowed(ref, pats): ok += 1
                    else: fails.append(f'FAIL {where} reads {ref}: not on the allow-list (the page would 404)')
                    continue
                kept = [p for p in under if allowed(p, pats)]
                if len(kept) == len(under): ok += 1
                elif not kept and ref.count('/') >= 2:
                    fails.append(f'FAIL {where} reads {ref}* ({len(under)} files in KPC-Data): none of them is on the allow-list')
                else: warns.append(f'WARN {where} builds a name from {ref!r}: {len(kept)} of {len(under)} KPC-Data files under it are kept')
    for w in sorted(set(warns))[:200]: print(w)
    for f in sorted(set(fails)): print(f)
    print(f'reader check: {ok} references covered, {len(set(warns))} partial (names built in code), {len(set(fails))} NOT covered')
    return 1 if fails else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    for name in ('build', 'check-readers'):
        p = sub.add_parser(name)
        p.add_argument('--repo', default='.'); p.add_argument('--rev', default='origin/main')
        p.add_argument('--allow', default='.github/site-allow-list.txt')
        if name == 'build':
            p.add_argument('--previous', default=''); p.add_argument('--max-loss', type=float, default=0.10)
            p.add_argument('--min-files', type=int, default=int(os.environ.get('KPC_SITE_MIN_FILES') or 500)); p.add_argument('--dry-run', action='store_true'); p.add_argument('--json', default='')
        else:
            p.add_argument('checkouts', nargs='+')
    a = ap.parse_args(argv)
    try: return build(a) if a.cmd == 'build' else check_readers(a)
    except Fail as e:
        print(f'::error title=Site filter::{e}')
        print('TREE='); print('COMMIT='); print('PUBLISH=no')
        return 3


if __name__ == '__main__':
    sys.exit(main())
