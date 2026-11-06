#!/usr/bin/env python3
"""Offline test, Nov 4 PM fix bundle PAUSE (Brandon's yes relayed via Super Head Bot, 4:53 PM CST Nov 4): the 9 broken bots no
longer start by themselves (no schedule, so no watchdog restart either; no chain or other bot starts them) and still start by hand
(workflow_dispatch). The bots Brandon said NOT to pause keep their schedules unchanged. No new cron anywhere."""
import os, pathlib, re, subprocess, sys
import yaml

HERE = pathlib.Path(__file__).resolve().parent.parent
os.chdir(HERE)
sys.path.insert(0, '.github/scripts')
import kpc_watchdog as WD   # noqa: E402  (its crons() is what decides restarts)

PAUSED = ['kpc-wdpa-phonebook.yml', 'kpc-collector.yml', 'kpc-intake.yml', 'kpc-docs.yml', 'kpc-docs-merge.yml', 'kpc-gis-hunter.yml',
          'kpc-world-finder.yml', 'kpc-discovery.yml', 'kpc-engine-discover.yml']
KEEP = ['kpc-engine.yml', 'kpc-detective.yml', 'kpc-campsites.yml', 'kpc-camp-weekly.yml', 'kpc-camp-layers.yml', 'kpc-closures.yml',
        'kpc-us-closures.yml', 'kpc-fetch-files.yml']
BASE = os.environ.get('BASE') or ('origin/main' if subprocess.run(['git', 'rev-parse', '-q', '--verify', 'origin/main'], capture_output=True).returncode == 0 else 'HEAD~1')
ok = True


def check(c, msg):
    global ok
    print(('PASS ' if c else 'FAIL ') + msg); ok = ok and bool(c)


def on(txt):
    d = yaml.safe_load(txt); return d.get(True) or d.get('on') or {}


W = pathlib.Path('.github/workflows')
for f in PAUSED:
    o = on((W / f).read_text(encoding='utf-8'))
    check('schedule' not in o and 'workflow_dispatch' in o, f'{f}: no schedule, by hand still works')
    check(WD.crons(str(W / f))[1] == [], f'{f}: the watchdog finds no cron, so it never restarts it')
dispatch = re.compile(r'gh (workflow run |api -X POST "?repos/.+?/actions/workflows/)(' + '|'.join(map(re.escape, PAUSED)) + r')\b')
live = [f'{p.name}:{i}' for p in sorted(W.glob('*.yml')) for i, l in enumerate(p.read_text(encoding='utf-8').split('\n'), 1)
        if dispatch.search(l) and not l.lstrip().startswith('#')]
check(live == [], f'no bot starts a paused bot by itself any more (live starts: {live})')
for f in KEEP:
    if not (W / f).exists(): continue
    before = subprocess.run(['git', 'show', f'{BASE}:.github/workflows/{f}'], capture_output=True, text=True).stdout
    check(before and on(before).get('schedule') == on((W / f).read_text(encoding='utf-8')).get('schedule'), f'{f}: NOT paused, schedule unchanged')
# Crons Brandon OK'd himself (the only way a new cron gets in): Brandon, 7:11 AM CST Nov 6 2026 (relayed by the parent agent, his
# words): "Yes, put the Quality sample on a weekly schedule" -> kpc-quality-sample.yml Mondays 7:41 AM CST.
BRANDON_OK_CRONS = {('kpc-quality-sample.yml', '41 13 * * 1')}
new_crons = []
for p in sorted(W.glob('*.yml')):
    before = subprocess.run(['git', 'show', f'{BASE}:.github/workflows/{p.name}'], capture_output=True, text=True).stdout
    b = set(re.findall(r"^\s*-\s*cron:\s*['\"]([^'\"]+)", before, re.M)); a = set(re.findall(r"^\s*-\s*cron:\s*['\"]([^'\"]+)", p.read_text(encoding='utf-8'), re.M))
    a = {c for c in a if (p.name, c) not in BRANDON_OK_CRONS}
    if a - b: new_crons.append((p.name, sorted(a - b)))
check(new_crons == [], f'no new cron (vs {BASE}): {new_crons}')
for p in sorted(W.glob('*.yml')):
    try: yaml.safe_load(p.read_text(encoding='utf-8'))
    except Exception as e: check(False, f'{p.name} is valid YAML ({e})')
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
