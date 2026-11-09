#!/usr/bin/env python3
"""Nov 8: hand-layer pile hand-run lives in separate files; Nov 4 full pile-solver outputs stay intact."""
import csv, json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
P = ROOT / 'data/waiting/in/data/pile-solver'
ok = True
def check(c, m):
    global ok
    print(('PASS ' if c else 'FAIL ') + m)
    ok = ok and bool(c)

sj = list(csv.DictReader(open(P / 'solved-join.csv', encoding='utf-8')))
np = list(csv.DictReader(open(P / 'needs-person.csv', encoding='utf-8')))
check(len(sj) == 52, 'Nov 4 solved-join still has 52 rows (%d)' % len(sj))
check(len(np) == 632, 'Nov 4 needs-person still has 632 rows (%d)' % len(np))
check((P / 'run-log.md').is_file() and (P / 'run-log.md').stat().st_size > 400000, 'Nov 4 run-log.md intact')
parks = 0
for f in P.glob('*.json'):
    d = json.load(open(f, encoding='utf-8'))
    if isinstance(d, dict) and isinstance(d.get('parks'), dict):
        parks += len(d['parks'])
check(parks == 1381, 'Nov 4 area JSONs still hold 1,381 parks (%d)' % parks)

hs = list(csv.DictReader(open(P / 'hand-layers-solved-join.csv', encoding='utf-8')))
hn = list(csv.DictReader(open(P / 'hand-layers-needs-person.csv', encoding='utf-8')))
check({r['ref'] for r in hs} == {'US-3505', 'US-3751', 'US-6535', 'US-6565', 'US-9770'}, '5 file-aware SOLVED-JOINs only')
check(all(r['verdict'] == 'SOLVED-JOIN' for r in hs), 'hand solved rows are SOLVED-JOIN')
check(any(r['ref'] == 'US-3729' and r['verdict'] == 'NEEDS-PERSON' for r in hn), 'US-3729 is NEEDS-PERSON (Rule 18)')
check(not any(r['ref'] == 'US-3729' for r in hs), 'US-3729 not in hand solved-join')
check((P / 'hand-layers-ABOUT.md').is_file(), 'ABOUT present')
# hand files must not replace nov4 names
for name in ('solved-join.csv', 'needs-person.csv', 'run-log.md'):
    check((P / name).is_file(), 'must-keep %s present' % name)

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
