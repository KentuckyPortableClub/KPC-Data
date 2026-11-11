#!/usr/bin/env python3
"""Owner rule, 2026-11-10: every KPC-Data script that makes a web request goes through the one host check (kpc_host_rules.py):
directly (host_ok), through kpc_manners (which asks it before robots.txt and every request), or by installing it
(kpc_host_rules.install() wraps urlopen and requests). A NEW fetcher without one of these fails here. No network."""
import ast, pathlib, re, sys, urllib.request
ROOT = pathlib.Path(__file__).resolve().parents[1]
S = ROOT / '.github/scripts'
ok = True
def check(msg, c):
    global ok
    ok &= bool(c); print(('PASS ' if c else 'FAIL ') + msg)
FETCH = re.compile(r'urlopen\(|build_opener\(|urlretrieve\(|http\.client\.|\brequests\.(get|post|head|Session)\(')
def imports(tree):
    out = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import): out |= {a.name.split('.')[0] for a in n.names}
        elif isinstance(n, ast.ImportFrom) and n.module: out.add(n.module.split('.')[0])
    return out
bad = []
for p in sorted(S.glob('*.py')):
    src = p.read_text(encoding='utf-8', errors='replace')
    code = '\n'.join(l for l in src.split('\n') if not l.lstrip().startswith('#'))
    if not FETCH.search(code): continue
    try: tree = ast.parse(src)
    except SyntaxError: continue
    imp = imports(tree)
    covered = ('kpc_manners' in imp or 'kpc_host_rules' in imp or 'kpc_host_pace' in imp or 'kpc_http_cache' in imp or 'kpc_net_guard' in imp
               or 'kpc_host_rules' in src and 'host_ok' in src)
    if not covered: bad.append(p.name)
check(f'every fetcher in .github/scripts uses the host check ({bad})', not bad)
bad = []
for p in sorted((S / 'tools').glob('*/*.py')) + sorted((S / 'draft/tools').glob('kpc_*/kpc_*.py')):
    src = p.read_text(encoding='utf-8', errors='replace')
    if FETCH.search('\n'.join(l for l in src.split('\n') if not l.lstrip().startswith('#'))) and 'kpc_host_rules' not in src and 'NEVER_LIVE' not in src and 'host_ok' not in src:
        bad.append(str(p.relative_to(S)))
check(f'every tool that fetches has the host check (kpc_host_rules, host_ok or the polite reader\'s NEVER_LIVE) ({bad})', not bad)
# the installer really refuses, offline
sys.path.insert(0, str(S))
import kpc_host_rules as HR
HR.install(); HR.install()
for u in ('https://services3.arcgis.com/robots.txt', 'https://apps.fs.usda.gov/x', 'ftp://example.org/x'):
    try: urllib.request.urlopen(u, timeout=1); r = False
    except HR.HostRefused: r = True
    check(f'install(): urlopen refuses {u} before any request', r)
try:
    import requests
    try: requests.get('https://services1.arcgis.com/x', timeout=1); r = False
    except HR.HostRefused: r = True
    check('install(): requests refuses a services*.arcgis.com host before any request', r)
except ImportError: print('NOTE: requests not installed here')
print('ALL PASS' if ok else 'SOME FAILED'); sys.exit(0 if ok else 1)
