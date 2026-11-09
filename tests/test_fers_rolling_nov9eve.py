#!/usr/bin/env python3
"""Nov 9 evening (Brandon t909u-t918u): one monthly cron, saved-live outlines on the fers-cache release, and one full rebuild per
area per cycle (90 days, Brandon confirmed t918u), round-robin, oldest first. Offline."""
import json, os, pathlib, sys, tempfile
HERE = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / '.github/scripts'))
import kpc_fers_areas as A
import yaml
ok = True
def check(c, m):
    global ok
    print(('PASS ' if c else 'FAIL ') + m); ok = ok and bool(c)
cfg = json.load(open(HERE / '.github/fers-areas.json'))
check(cfg.get('full_cycle_days') == 90 and 't918u' in cfg.get('full_cycle_about', ''), 'cycle length: one setting, 90 days, Brandon confirmed (t918u)')
names = list(A.AREAS)
cap = -(-len(names) * 30 // 90)
d0 = A.full_due(names, '2026-11-09', {})
check(len(d0) == cap and d0 == sorted(names)[:cap], f'nothing done yet: {cap} areas a monthly run, in order')
last = {n: '2026-11-01' for n in names}; last['plains'] = '2026-07-01'; last['southwest'] = '2026-06-01'
check(A.full_due(names, '2026-11-09', last) == ['southwest', 'plains'], 'only areas older than the cycle are due, oldest first')
check(A.full_due(names, '2026-11-09', {n: '2026-11-01' for n in names}) == [], 'none due -> no full area this run (only the changed pairs)')
os.environ['REGION'] = 'areas'
os.environ['FULL'] = 'all'; check(all(x['full'] == '1' for x in A.plan('areas')), 'FULL=all: every job in full (emergency)')
os.environ['FULL'] = 'none'; check(not any(x['full'] for x in A.plan('areas')), 'FULL=none: no full area')
os.environ['FULL'] = ''; check(all(x['full'] == '' for x in A.plan('na world')), 'na / world runs: never a round-robin full')
w = yaml.safe_load(open(HERE / '.github/workflows/kpc-fers.yml'))
on = w.get('on') or w.get(True)
check([c['cron'] for c in on.get('schedule') or []] == ['23 8 5 * *'], 'exactly one cron, monthly')
txt = (HERE / '.github/workflows/kpc-fers.yml').read_text()
check("KPC_FERS_FULL: ${{ matrix.r.full }}" in txt and 'KPC_FERS_LIVE_DIR: cache/fers' in txt, 'the job passes its full flag and the saved-live folder')
check("REGION: ${{ inputs.region || 'areas' }}" in txt and "PASS: ${{ inputs.pass || 'all' }}" in txt, 'the monthly run = pass all on every area')
steps = w['jobs']['fers']['steps']
up = [x for x in steps if 'fers-cache' in str(x.get('run', '')) and 'upload' in str(x.get('run', ''))]
check(len(up) == 1 and "steps.kept_green_3.outcome == 'success'" in up[0]['if'], 'saved-live is uploaded only after a good Look')
sv = [x for x in steps if x.get('id') == 'kept_green_5'][0]['run']
check('full-rebuild-${{ matrix.r.tag }}.txt' in sv and sv.index('full-rebuild') < sv.index('kpc_push_data.sh'), 'the full-rebuild date is saved with the results, only after success')
print('ALL PASS' if ok else 'FAILED'); sys.exit(0 if ok else 1)
