"""For every park whose compilation copy went to check (D7): is there agency land under the dropped copy that no joined record covers,
and does an UNJOINED record of the same manager sit there? No network; saved shapes + the would-be keys."""
import json, glob, sys, csv, gzip, collections
import numpy as np
sys.path.insert(0, '/home/claude/work/scripts'); import measure as M
cache = '/home/claude/work/cache'; fcd = '/home/claude/work/to/key-quality/2026-11-19/factcheck-run-44528656941'
held = set('AK AR DE FL GA ID MT NC OR RI UT VA WY'.split())
out = []
for f in sorted(glob.glob('/home/claude/work/newkeys/US-*.json')):
    k = json.load(open(f)); st = k['st']
    todo = [(r, p) for r, p in k['parks'].items() if any('(D7)' in str(c[3]) for c in p.get('c') or [])]
    if not todo: continue
    recs = M.load(st, cache); fc = json.load(gzip.open(f'{fcd}/factcheck-US-{st}.json.gz'))['parks']
    joined_any = {str(x[0]) for p in k['parks'].values() for x in p.get('m') or []}
    bb = {}
    for i, a in recs.items():
        pts = [q for r in M.rings_of(a) for q in r]
        if pts: bb[i] = (min(q[0] for q in pts), min(q[1] for q in pts), max(q[0] for q in pts), max(q[1] for q in pts))
    for ref, p in todo:
        copies = [str(c[0]) for c in p['c'] if '(D7)' in str(c[3]) and str(c[0]) in recs]
        mine = [str(x[0]) for x in p.get('m') or [] if str(x[0]) in recs]
        if not copies: continue
        mgr = collections.Counter(str(recs[i].get('Mang_Name')) for i in mine if i.isdigit()).most_common(1)
        mgr = mgr[0][0] if mgr else ''
        cb = [bb[i] for i in copies if i in bb]
        if not cb: continue
        box = (min(b[0] for b in cb), min(b[1] for b in cb), max(b[2] for b in cb), max(b[3] for b in cb))
        # unjoined PAD-US records of the same manager whose box meets the copy's box
        others = [i for i, a in recs.items() if i.isdigit() and mgr and str(a.get('Mang_Name')) == mgr and i not in joined_any and i in bb
                  and not (bb[i][2] < box[0] or bb[i][0] > box[2] or bb[i][3] < box[1] or bb[i][1] > box[3])][:400]
        r = M.measure(copies + mine + others, recs, maxpx=1500, want_masks=True); cell = r['cell']; A = lambda m: float(m.sum() * cell * cell / M.M2_AC)
        z = np.zeros_like(r['union']); mc = z.copy(); mm = z.copy()
        for i in copies: mc |= r['masks'][i]
        for i in mine: mm |= r['masks'][i]
        gap = mc & ~mm
        best = sorted(((A(r['masks'][i] & gap), i) for i in others), reverse=True)[:3]
        best = [(a, i) for a, i in best if a >= 50]
        e = fc.get(ref) or {}
        out.append([st, 'held' if st in held else 'saved', ref, p.get('n'), e.get('act'), e.get('class'), round(A(mc)), round(A(mm)), round(A(gap)), mgr,
                    round(sum(a for a, _ in best)), '; '.join(f"{i} {str(recs[i].get('Unit_Nm') or recs[i].get('Loc_Nm'))[:40]} ({a:,.0f} ac under the copy)" for a, i in best)])
w = csv.writer(open('/home/claude/work/d7-check.csv', 'w', newline=''))
w.writerow(['state', 'held_or_saved', 'ref', 'park', 'activations', 'class_new', 'dropped_copy_ac', 'joined_ac', 'copy_land_not_covered_ac', 'manager', 'unjoined_same_manager_land_under_copy_ac', 'unjoined_records'])
w.writerows(out)
print(len(out), 'parks with a dropped compilation copy measured')
bad = [x for x in out if x[10] >= 100 and x[10] >= 0.05 * max(x[6], 1)]
print('an UNJOINED record of the same manager lies under the dropped copy (>= 100 ac and >= 5% of the copy):', len(bad))
for x in sorted(bad, key=lambda x: -(x[4] or 0)):
    print(f"{x[0]} {x[1]:5} {x[2]:9} {str(x[3])[:36]:36} act {str(x[4]):>5} {str(x[5]):9} | copy {x[6]:>10,} joined {x[7]:>10,} | uncovered {x[8]:>10,} | {x[9]} | {x[11][:150]}")
