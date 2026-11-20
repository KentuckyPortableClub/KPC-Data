#!/usr/bin/env python3
"""Nov 20: kpc-map-audit.yml saves map-audit-auto.json and .gz with the other question files."""
import pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
WF = (ROOT / '.github' / 'workflows' / 'kpc-map-audit.yml').read_text(encoding='utf-8')
FAILS = []


def check(ok, what):
    print(('PASS ' if ok else 'FAIL ') + what, flush=True)
    if not ok:
        FAILS.append(what)


# The git add that commits questions must name both auto files, next to map-audit.json
check('data/waiting/questions/map-audit-auto.json' in WF
      and 'data/waiting/questions/map-audit-auto.json.gz' in WF,
      'the map-audit workflow names map-audit-auto.json and .gz')
# same git add line as map-audit.json (not only mentioned elsewhere)
for line in WF.splitlines():
    if 'git add' in line and 'map-audit.json' in line and 'data/status' in line:
        add_line = line
        break
else:
    add_line = ''
check('map-audit-auto.json' in add_line and 'map-audit-auto.json.gz' in add_line
      and 'map-audit.json' in add_line and 'map-audit.json.gz' in add_line,
      'those auto files are on the same git add as map-audit.json and data/status')

print('ALL PASS' if not FAILS else 'SOME FAILED')
sys.exit(1 if FAILS else 0)
