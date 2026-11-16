#!/usr/bin/env python3
"""KPC owner, 2026-11-16 (handoff 'proof of work', item 7: be polite to POTA), KPC-Data side.
  1. No NEW direct api.pota.app call: every code file (.py .js .mjs .html .yml .sh, not tests/ data/ docs/ notes/) may name
     api.pota.app at most as often as tests/pota-door-baseline.json says (lower a number when a call goes; never raise one).
     POTA is read through the KPC-Links POTA door (kpc_pota_door.py) and its saved copies.
  2. kpc_pota_activity.py reads the saved copy only.
  3. No 2-fer run reads the POTA history (kpc_pota_pairs_run.py is out of kpc-fers.yml and kpc-fers-line.yml).
  4. No schedule changed against main."""
import json, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
FAILS = []


def check(ok, what):
    print(('PASS ' if ok else 'FAIL ') + what, flush=True)
    if not ok: FAILS.append(what)


SKIP = re.compile(r'^(tests|data|docs|notes|node_modules|\.git)/')
EXT = ('.py', '.js', '.mjs', '.html', '.yml', '.yaml', '.sh')


def counts():
    out = {}
    files = subprocess.run(['git', 'ls-files'], cwd=ROOT, capture_output=True, text=True).stdout.split('\n')
    files += subprocess.run(['git', 'ls-files', '--others', '--exclude-standard'], cwd=ROOT, capture_output=True, text=True).stdout.split('\n')
    for rel in sorted(set(f for f in files if f)):
        if SKIP.match(rel) or not rel.endswith(EXT) or not (ROOT / rel).is_file(): continue
        n = (ROOT / rel).read_text(encoding='utf-8', errors='replace').count('api.pota.app')
        if n: out[rel] = n
    return out


if '--write-baseline' in sys.argv[1:]:
    (ROOT / 'tests/pota-door-baseline.json').write_text(json.dumps({'about': 'Item 7 (KPC owner, 2026-11-16): api.pota.app mentions per code file '
        '(host lists, draft tools, a research link). Lower a number when a call goes; never raise one.', 'files': counts()}, indent=1) + '\n', encoding='utf-8')
    print('written'); sys.exit(0)

base = json.loads((ROOT / 'tests/pota-door-baseline.json').read_text(encoding='utf-8'))['files']
now = counts()
grew = sorted(f'{k}: {base.get(k, 0)} -> {v}' for k, v in now.items() if v > base.get(k, 0))
check(not grew, f'1. no new direct api.pota.app call in any code file ({grew})')
s = (ROOT / '.github/scripts/kpc_pota_activity.py').read_text(encoding='utf-8')
check('api.pota.app' not in s and 'urllib' not in s and 'KPC_POTA_SAVED' in s, '2. kpc_pota_activity.py reads the saved copy only')
wf = (ROOT / '.github/workflows/kpc-pota-activity.yml').read_text(encoding='utf-8')
check('repository: KentuckyPortableClub/KPC-Links' in wf and 'sparse-checkout: data/pota/saved' in wf, '2. its workflow checks out only the saved copy folder of KPC-Links')
for f in ('kpc-fers.yml', 'kpc-fers-line.yml'):
    check('kpc_pota_pairs_run.py' not in (ROOT / '.github/workflows' / f).read_text(encoding='utf-8'), f'3. {f}: no POTA history step')


def crons(ref=None):
    out = {}
    if ref:
        for n in subprocess.run(['git', 'ls-tree', '--name-only', ref, '.github/workflows/'], cwd=ROOT, capture_output=True, text=True).stdout.split():
            t = subprocess.run(['git', 'show', f'{ref}:{n}'], cwd=ROOT, capture_output=True, text=True).stdout
            out[n] = [l.strip() for l in t.splitlines() if 'cron:' in l]
    else:
        for p in sorted((ROOT / '.github/workflows').glob('*.y*ml')):
            out[f'.github/workflows/{p.name}'] = [l.strip() for l in p.read_text(encoding='utf-8').splitlines() if 'cron:' in l]
    return out


ref = next((r for r in ('origin/main', 'main') if subprocess.run(['git', 'rev-parse', '--verify', '-q', r], cwd=ROOT, capture_output=True).returncode == 0), None)
if ref: check(crons(ref) == crons(), f'4. no schedule changed and no new workflow (against {ref})')
print('ALL PASS' if not FAILS else 'SOME FAILED')
sys.exit(1 if FAILS else 0)
