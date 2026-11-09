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
check('kpc_archive.sh put fers' in up[0]['run'] and up[0]['run'].index('kpc_archive.sh put fers') < up[0]['run'].index('gh release upload fers-cache')
      and 'KPC_ARCHIVE_TOKEN' in str(up[0].get('env')), 'saved-live goes to KPC-Archive first; the release only when the archive is not available')
check('kpc_archive.sh get fers-saved-live cache/fers' in txt and txt.index('kpc_archive.sh get fers') < txt.index('gh release download fers-cache'), 'saved-live is read from KPC-Archive first, the release as the fallback')
sv = [x for x in steps if x.get('id') == 'kept_green_5'][0]['run']
check('full-rebuild-${{ matrix.r.tag }}.txt' in sv and sv.index('full-rebuild') < sv.index('kpc_push_data.sh'), 'the full-rebuild date is saved with the results, only after success')
# Nov 9 evening (Brandon t926u): a broken run saves only what finished
with tempfile.TemporaryDirectory() as t:
    t = pathlib.Path(t); (t / 'data/fers').mkdir(parents=True)
    (t / 'data/fers/US-NC.json').write_text(json.dumps({'pass5': '2026-11-09'}))
    (t / 'data/fers/US-SC.json').write_text(json.dumps({'pass5': '2026-11-09', 'incomplete': True}))
    (t / 'data/fers/US-GA.json').write_text(json.dumps({'pass1': '2026-11-09', 'pass5': '2026-11-02'}))
    check(A.finished('US-NC US-SC US-GA US-FL', '2026-11-09', t) == ['data/fers/US-NC.json'], 'after a break: only a state that finished every pass today is saved')
bk = [x for x in steps if 'run broke' in str(x.get('name', ''))]
check(len(bk) == 1 and "steps.kept_green_3.outcome == 'failure'" in bk[0]['if'] and '!cancelled()' in bk[0]['if'], 'a break (crash / time-out) runs the save-what-finished step; a cancel does not')
r = bk[0]['run'] if bk else ''
check('reuse-p*-' in r and 'kpc_fers_areas.py finished' in r and 'STRICT=1' in r and 'data/fers/*' not in r, 'it saves pair answers + fully finished states only (never every file)')
check(txt.index('run broke') > txt.index('kept_green_5') and 'Report hidden failures' in txt[txt.index('run broke'):], 'the job still goes red after it (Report step runs after)')
print('ALL PASS' if ok else 'FAILED'); sys.exit(0 if ok else 1)
