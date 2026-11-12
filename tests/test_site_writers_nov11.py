#!/usr/bin/env python3
"""Nobody writes the Pages branch 'site' except .github/scripts/kpc_site_publish.sh (KPC owner, 2026-11-11). The copy bot and the
watchdog both force-move 'site'; if one of them (or a new workflow) moved it to main's commit again, every file would be published
and the filter would be silently undone. This scans every workflow and script of KPC-Data (and of KPC-Links when LINKS points at a
checkout, or ../links / ../KPC-Links exists) for a WRITE to 'site': an API ref PATCH / POST / DELETE, a git push to it, update-ref,
branch -f / checkout -B. Reading 'site' is fine. Offline, read-only."""
import os, pathlib, re, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
ALLOWED = {'.github/scripts/kpc_site_publish.sh'}
WRITE = [re.compile(r'-X\s*(PATCH|POST|PUT|DELETE)\b.*(heads/site\b|refs/heads/site\b)'),
         re.compile(r"""['"]-X['"]\s*,\s*['"](PATCH|POST|PUT|DELETE)['"].*heads/site\b"""),
         re.compile(r'\bpush\b[^\n#]*(:refs/heads/site\b|:site\b|\s(origin|"\$R"|\S+\.git)\s+site\b)'),
         re.compile(r'update-ref\s+(-\S+\s+)*refs/heads/site\b'),
         re.compile(r'\b(branch\s+-[fFM]|checkout\s+-B|switch\s+-C)\s+site\b')]
fails = 0


def check(name, ok, extra=''):
    global fails
    print(('PASS' if ok else 'FAIL') + ': ' + name + (f' ({extra})' if extra and not ok else ''))
    fails += 0 if ok else 1


def writers(root):
    out = []
    base = pathlib.Path(root) / '.github'
    for f in sorted(base.rglob('*')) if base.is_dir() else []:
        if not f.is_file() or f.suffix in ('.pyc', '.png', '.gz', '.zip') or '__pycache__' in f.parts: continue
        rel = f.relative_to(root).as_posix()
        try: text = f.read_text(encoding='utf-8', errors='replace')
        except OSError: continue
        for n, line in enumerate(text.splitlines(), 1):
            if any(rx.search(line) for rx in WRITE): out.append((rel, n, line.strip()[:140]))
    return out


w = writers(ROOT)
bad = [x for x in w if x[0] not in ALLOWED]
check("KPC-Data: only kpc_site_publish.sh writes the branch 'site'", not bad, '; '.join(f'{a}:{b}' for a, b, _ in bad))
check('... and it does write it (the scan sees the real writer)', any(x[0] in ALLOWED for x in w))
pub = (ROOT / '.github/scripts/kpc_site_publish.sh').read_text()
fi, pu = pub.find('kpc_site_filter.py build'), pub.find('push -q --force origin "$C:refs/heads/site"')
check('kpc_site_publish.sh pushes only the commit the filter built (filter first, then push COMMIT)', 0 <= fi < pu and 'C=$(grep \'^COMMIT=\'' in pub)
check("kpc_site_publish.sh moves site to main's commit only with FILTER=off", re.search(r'if \[ "\$FILTER" = off \]; then\n  if \[ "\$S" = none \]', pub) is not None)
check('kpc-pages-sync.yml publishes through kpc_site_publish.sh', 'bash .github/scripts/kpc_site_publish.sh' in (ROOT / '.github/workflows/kpc-pages-sync.yml').read_text())
check("the watchdog's repair path publishes through kpc_site_publish.sh", "'.github/scripts/kpc_site_publish.sh'" in (ROOT / '.github/scripts/kpc_watchdog.py').read_text())
links = os.environ.get('LINKS') or next((str(p) for p in (ROOT.parent / 'links', ROOT.parent / 'KPC-Links') if (p / '.github').is_dir()), '')
if links:
    lw = writers(links)
    check(f"KPC-Links ({links}): no workflow or script writes KPC-Data's 'site'", not lw, '; '.join(f'{a}:{b}' for a, b, _ in lw))
else: print('NOTE: no KPC-Links checkout next to this one (set LINKS=...): KPC-Links not scanned')
# the scan itself: a planted writer of each kind is caught
with tempfile.TemporaryDirectory() as t:
    p = pathlib.Path(t) / '.github' / 'workflows'; p.mkdir(parents=True)
    plants = ['gh api -X PATCH repos/$R/git/refs/heads/site -f sha=$M -F force=true', 'git push -f origin HEAD:site',
              'git push --force origin main:refs/heads/site', "gh('-X', 'PATCH', f'repos/{REPO}/git/refs/heads/site', '-f', f'sha={M}')",
              'git update-ref refs/heads/site $M', 'git branch -f site main']
    (p / 'x.yml').write_text('\n'.join(plants) + '\n' + 'S=$(gh api repos/$R/git/ref/heads/site --jq .object.sha)\n')
    got = writers(t)
    check('the scan catches every kind of write (6 planted) and not a read', len(got) == len(plants) and all(x[1] <= len(plants) for x in got), got)
print('ALL PASSED' if not fails else f'SOME FAILED ({fails})')
sys.exit(1 if fails else 0)
