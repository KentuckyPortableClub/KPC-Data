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
file_aware = {'US-3505', 'US-3751', 'US-6535', 'US-6565', 'US-9770'}
accept = {'US-2200', 'CA-2373', 'US-6571', 'US-6550'}
pin_wrong = {'CA-0527', 'CA-0558', 'US-6551'}
check({r['ref'] for r in hs} == file_aware | accept | pin_wrong, '12 SOLVED-JOINs (5 file-aware + 4 accept + 3 pin_wrong)')
check(all(r['verdict'] == 'SOLVED-JOIN' for r in hs), 'hand solved rows are SOLVED-JOIN')
check(file_aware <= {r['ref'] for r in hs}, '5 file-aware SOLVED-JOINs kept')
check(any(r['ref'] == 'US-3729' and r['verdict'] == 'NEEDS-PERSON' for r in hn), 'US-3729 is NEEDS-PERSON (Rule 18)')
check(any(r['ref'] == 'CA-0551' and r['verdict'] == 'NEEDS-PERSON' for r in hn), 'CA-0551 stays NEEDS-PERSON')
check(not any(r['ref'] == 'US-3729' for r in hs), 'US-3729 not in hand solved-join')
check({r['ref'] for r in hs if r.get('pin_flag') == 'POTA pin wrong'} == pin_wrong, '3 pin_wrong flags')
check(any(r['ref'] == 'US-2200' for r in hs), 'US-2200 accept-polygon (rename clears Rule 18)')
check((P / 'hand-layers-ABOUT.md').is_file(), 'ABOUT present')
for name in ('solved-join.csv', 'needs-person.csv', 'run-log.md'):
    check((P / name).is_file(), 'must-keep %s present' % name)

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
