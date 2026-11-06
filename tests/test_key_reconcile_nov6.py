#!/usr/bin/env python3
"""Nov 6 improvements v2 item 3 (AU gap): kpc_key_reconcile.py. Its rule-18 style selftest (15 frozen cases); it reads files only
(no network); Step B3 puts the approved layer labels back BEFORE the waiting room and runs the fail-closed check AFTER it, putting
the stamp (index.json) back for a failed key; no new trigger on the workflow."""
import json, os, pathlib, re, shutil, subprocess, sys, tempfile
ROOT = pathlib.Path(__file__).resolve().parents[1]
ok = True
def check(msg, cond):
    global ok
    ok &= bool(cond); print(('PASS ' if cond else 'FAIL ') + msg)
S = ROOT / '.github/scripts/kpc_key_reconcile.py'
r = subprocess.run([sys.executable, '-B', str(S), '--selftest'], capture_output=True, text=True, timeout=120, cwd=ROOT)
check('kpc_key_reconcile.py --selftest: ' + (r.stdout.strip().splitlines() or ['?'])[-1], r.returncode == 0 and 'SELFTEST PASS' in r.stdout)
src = S.read_text()
check('reads files only (no urllib / requests / http)', not re.search(r'^\s*(import|from)\s+(urllib|requests|http)', src, re.M))
y = (ROOT / '.github/workflows/kpc-copy-from-links.yml').read_text()
i_m, i_d, i_c = y.find('kpc_key_reconcile.py merge-layers'), y.find('kpc_waiting_room.py divert $KDIRS'), y.find('kpc_key_reconcile.py | tee')
check('B3: labels put back before the waiting room, the check after it', 0 <= i_m < i_d < i_c)
blk = y[i_c:i_c + 900]
check('B3: a failed key gets its index.json (the stamp) put back and an error line (fails closed)', 'git checkout -q HEAD -- "data/$k/index.json"' in blk and '::error title=Key reconcile::' in blk and 'kpc-hidden.txt' in blk)
check('no new trigger: the on: block keeps its 3 existing crons (frozen count, Part B base) and adds no workflow_run', y.split('\njobs:', 1)[0].count('cron:') == 3 and 'kpc_key_reconcile' not in y.split('\njobs:', 1)[0])
# v2.1 (Quality MUST-ADD): on a COPY of KPC-Data's real world key, the AU-8945 world 'no' (improvements 05b, applied before this
# patch) is honoured BEFORE the label restore: after merge-layers the shared 'AU: Beach (approved layer 11)' label is back for the
# other beaches, but AU-8945 has no joined record left, so the site (kpc-bounds.js worldKey: draws only m records) draws nothing.
sys.path.insert(0, str(ROOT / '.github/scripts')); import kpc_key_reconcile as R
ov = json.load(open(ROOT / 'data/world-key/overrides.json', encoding='utf-8'))['parks'].get('AU-8945') or {}
check("patch order: the AU-8945 world 'no' is already there (05b before 06)", ov.get('no') == ['805', 'Godwin Beach', 'Scarborough Beach'])
au = json.load(open(ROOT / 'data/world-key/AU.json', encoding='utf-8'))
p0 = au['parks'].get('AU-8945') or {}
if p0.get('m'):
    td = pathlib.Path(tempfile.mkdtemp(prefix='kpc-recon-au8945-'))
    try:
        (td / 'data/world-key').mkdir(parents=True); (td / 'data/waiting/questions').mkdir(parents=True)
        lab = p0['m'][0][2]
        other = {r: v for r, v in au['parks'].items() if isinstance(v, dict) and v.get('approved') and v.get('m') and v['m'][0][2] == lab and r != 'AU-8945'}
        r1 = next(iter(other))
        json.dump({'cc': 'AU', 'parks': {'AU-8945': p0, r1: other[r1]}}, open(td / 'data/world-key/AU.json', 'w'))
        shutil.copy(ROOT / 'data/world-key/overrides.json', td / 'data/world-key/overrides.json')
        json.dump({k: v for k, v in json.load(open(ROOT / 'data/world-key/layers.json')).items() if k != lab}, open(td / 'data/world-key/layers.json', 'w'))
        json.dump({'questions': [{'ref': r, 'answer': 'YES', 'layer': 'https://spatial-gis.information.qld.gov.au/arcgis/rest/services/Location/Places/FeatureServer/11', 'record': x['m'][0][0]}
                                 for r, x in (('AU-8945', p0), (r1, other[r1]))]}, open(td / 'data/waiting/questions/layers.json', 'w'))
        R.merge_layers(str(td), committed={}, links=str(td / 'nolinks'))
        P = json.load(open(td / 'data/world-key/AU.json'))['parks']; L = json.load(open(td / 'data/world-key/layers.json'))
        draws = lambda p: [x for x in p.get('m') or [] if L.get(x[2]) and x[0] is not None]
        check(f"after the restore the shared label is back ({lab[:40]}) and {r1} draws", lab in L and bool(draws(P[r1])))
        check('after the restore AU-8945 does NOT draw: record 805 is out of m (kept in c with the no)', draws(P['AU-8945']) == [] and 805 in [x[0] for x in P['AU-8945']['c']])
    finally: shutil.rmtree(td, ignore_errors=True)
else: check('AU-8945 has no approved join in this KPC-Data copy (nothing can draw)', True)
print('ALL PASS' if ok else 'SOME FAILED'); sys.exit(0 if ok else 1)
