#!/usr/bin/env python3
"""Compare two fact-check output folders (old vs new) over all areas present in both.
Usage: fccompare.py OLD_FC NEW_FC OUT_PREFIX [--parks REF,REF]  -> OUT_PREFIX.txt (summary) + OUT_PREFIX-parks.csv (every changed park)"""
import json, glob, os, sys, csv, collections
old, new, outp = sys.argv[1:4]
HARD = ('PIN_FAR', 'SIZE_BIG', 'BIG_PIECE', 'SHARED', 'OTHER_PARK')
CL = ('verified', 'two', 'one', 'none', 'flagged', 'pin')
def ids(p): return sorted(str(x[0]) for x in p.get('m') or [])
def hard(p): return sorted(f[0] for f in p.get('flags') or [] if f[0] in HARD)
areas = sorted(os.path.basename(f)[10:-5] for f in glob.glob(os.path.join(new, 'factcheck-*.json')) if 'summary' not in f)
lines, rows = [], []
tot = collections.Counter()
for a in areas:
    fo = os.path.join(old, f'factcheck-{a}.json')
    if not os.path.exists(fo): lines.append(f'{a}: no old fact check'); continue
    O = json.load(open(fo))['parks']; N = json.load(open(os.path.join(new, f'factcheck-{a}.json')))['parks']
    c = collections.Counter()
    for ref in sorted(set(O) | set(N)):
        po, pn = O.get(ref) or {}, N.get(ref) or {}
        co, cn = po.get('class', 'pin'), pn.get('class', 'pin')
        c['old_' + co] += 1; c['new_' + cn] += 1
        c['old_outline'] += bool(po.get('m')); c['new_outline'] += bool(pn.get('m'))
        for f in hard(po): c['old_' + f] += 1
        for f in hard(pn): c['new_' + f] += 1
        if ids(po) == ids(pn) and co == cn and hard(po) == hard(pn): continue
        what = []
        if ids(po) != ids(pn):
            what.append('outline lost' if po.get('m') and not pn.get('m') else 'outline gained' if pn.get('m') and not po.get('m') else 'records changed')
        if co != cn: what.append(f'class {co} -> {cn}')
        if hard(po) != hard(pn): what.append(f"hard flags {'/'.join(hard(po)) or '-'} -> {'/'.join(hard(pn)) or '-'}")
        if po.get('m') and not pn.get('m') and co == 'verified': c['verified_lost'] += 1; what.append('VERIFIED OUTLINE LOST')
        rows.append([a, ref, (pn or po).get('n'), (pn or po).get('act') or 0, co, cn, ' '.join(ids(po))[:200], ' '.join(ids(pn))[:200], '; '.join(what)])
    tot.update(c)
    lines.append(f"{a}: outlines {c['old_outline']} -> {c['new_outline']} | verified {c['old_verified']} -> {c['new_verified']} | two {c['old_two']} -> {c['new_two']} | one/none {c['old_one']+c['old_none']} -> {c['new_one']+c['new_none']} | flagged {c['old_flagged']} -> {c['new_flagged']} | verified outlines lost {c['verified_lost']}"
                 + ' | ' + ' '.join(f"{f} {c['old_'+f]}->{c['new_'+f]}" for f in HARD if c['old_'+f] or c['new_'+f]))
c = tot
lines.append(f"ALL ({len(areas)} areas): outlines {c['old_outline']} -> {c['new_outline']} | verified {c['old_verified']} -> {c['new_verified']} | two {c['old_two']} -> {c['new_two']} | one/none {c['old_one']+c['old_none']} -> {c['new_one']+c['new_none']} | flagged {c['old_flagged']} -> {c['new_flagged']} | verified outlines lost {c['verified_lost']}"
             + ' | ' + ' '.join(f"{f} {c['old_'+f]}->{c['new_'+f]}" for f in HARD))
lines.append(f'parks that changed (outline, class or hard flags): {len(rows)}')
open(outp + '.txt', 'w').write('\n'.join(lines) + '\n')
with open(outp + '-parks.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['area', 'ref', 'name', 'activations', 'old class', 'new class', 'old records', 'new records', 'what changed'])
    for r in sorted(rows, key=lambda r: -int(r[3] or 0)): w.writerow(r)
print('\n'.join(lines[-3:]))
