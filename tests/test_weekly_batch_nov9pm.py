#!/usr/bin/env python3
"""Nov 9 PM weekly batch (Brandon t906u 3:58 PM CST): workflow breakages + staged hand layers. Offline."""
import json, os, pathlib, re, subprocess, sys
HERE = pathlib.Path(__file__).resolve().parent.parent
ok = True
def check(c, msg):
    global ok
    print(('PASS ' if c else 'FAIL ') + msg); ok = ok and bool(c)

# 1) Playwright workflows run on ubuntu-24.04 (no Playwright build for ubuntu 26.04)
import yaml
for wf in sorted((HERE / '.github/workflows').glob('*.yml')):
    y = yaml.safe_load(wf.read_text(encoding='utf-8')) or {}
    for jn, job in (y.get('jobs') or {}).items():
        if re.search(r'playwright', json.dumps(job), re.I):
            check(job.get('runs-on') == 'ubuntu-24.04', f'{wf.name} job {jn}: Playwright job runs on ubuntu-24.04')

# 2) divert with 0 parks is a clean no-op (exit 0), and the scoreboard step no longer fails on an empty list
r = subprocess.run([sys.executable, str(HERE / '.github/scripts/kpc_waiting_room.py'), 'divert'], capture_output=True, text=True, cwd=HERE,
                   env=dict(os.environ, DATA=str(HERE)))
check(r.returncode == 0 and 'nothing to divert' in r.stdout, f'divert with 0 files exits 0 ({r.returncode})')
sb = (HERE / '.github/workflows/kpc-scoreboard.yml').read_text(encoding='utf-8')
check('if [ -n "$F" ]; then python3 .github/scripts/kpc_waiting_room.py divert $F' in sb and 'nothing to divert' in sb, 'scoreboard: empty list = notice, not exit 1')

# 3) staged hand layers: decisions + files, provenance, no banned host
D = HERE / 'data/waiting/outline-sources'
dec = json.load(open(D / 'hand-layers-nov9.json', encoding='utf-8'))
for k, f in dec['files'].items():
    g = json.load(open(D / f)); a = json.load(open(D / (f + '.about.json')))
    check(g['type'] == 'FeatureCollection' and len(g['features']) == a['features'] > 0 and a.get('source_url') and a.get('download_date'), f'{f}: parses, has provenance')
nps = json.load(open(D / dec['files']['nps']))
check(sorted(f['properties']['unit_code'] for f in nps['features']) == sorted(['CACH', 'CECH', 'AMCH', 'HAGR', 'FOSM', 'FOVA', 'MIIN', 'BLSC', 'RORI']),
      'NPS hand layer: the 9 units, Poverty Point left out')
check(dec['decisions']['US-0958']['status'] == 'needs person', 'Poverty Point stays with a person')
txt = json.dumps(dec)
check('33TOOklri9xpic7U' not in txt and 'ncnhde.natureserve.org' not in txt, 'no banned host')
print('ALL PASS' if ok else 'FAILED'); sys.exit(0 if ok else 1)
