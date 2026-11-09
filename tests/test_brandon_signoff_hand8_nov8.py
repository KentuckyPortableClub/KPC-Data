#!/usr/bin/env python3
"""Nov 8: Brandon t786u sign-off overrides for 8 hand-layer joins (name matches boundary)."""
import json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
ok = True
def check(c, m):
    global ok
    print(('PASS ' if c else 'FAIL ') + m)
    ok = ok and bool(c)

us = json.load(open(ROOT / 'data/us-key/overrides.json'))['parks']
ca = json.load(open(ROOT / 'data/ca-key/overrides.json'))['parks']
want_us = {
    'US-3505': ['sgtxa4942'],
    'US-3751': ['sggaa882', 'sggaa837'],
    'US-6535': ['sgtxc140'],
    'US-6565': ['sgtxc96'],
    'US-9770': ['sggaa861'],
    'US-6551': ['sgtxc112'],
}
want_ca = {
    'CA-0527': ['Manitoba Par:88'],
    'CA-0558': ['Manitoba Par:22'],
}
for ref, joins in want_us.items():
    e = us.get(ref) or {}
    check(e.get('join') == joins, '%s join %s' % (ref, e.get('join')))
    check('t786u' in (e.get('decided_by') or ''), '%s decided_by has t786u' % ref)
    check(e.get('when') == '2026-11-08', '%s when' % ref)
for ref, joins in want_ca.items():
    e = ca.get(ref) or {}
    check(e.get('join') == joins, '%s join %s' % (ref, e.get('join')))
    check('t786u' in (e.get('decided_by') or ''), '%s decided_by has t786u' % ref)

# answer sheet stable ids (no FID:/OBJECTID: alone)
import csv
for path in [
    ROOT / 'data/waiting/in/data/pile-solver/hand-layers-answer-sheet-proposals-US.csv',
    ROOT / 'data/waiting/in/data/pile-solver/hand-layers-answer-sheet-proposals-CA.csv',
]:
    for r in csv.DictReader(open(path, encoding='utf-8')):
        rid = r.get('record_id') or ''
        check('FID:' not in rid and 'OBJECTID:' not in rid, '%s answer-sheet id stable (%s)' % (r['ref'], rid))
        if r['ref'] == 'US-2200':
            check('sggab60' in rid and 'sggab32' in rid, 'US-2200 lists both sggab60 and sggab32')

# rules hashes
for path, want in [
    (ROOT / 'data/us-key/index.json', 'a066624520b4'),
    (ROOT / 'data/ca-key/index.json', '8feccbb7d9ee'),
]:
    d = json.load(open(path))
    r = d.get('rules_of_run') or d.get('rules')
    check(r == want, '%s rules %s' % (path.name, r))

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
