import json, gzip, sys, csv, collections
sys.path.insert(0, '/home/claude/work/scripts'); import measure as M
cache = '/home/claude/work/cache'; fcd = '/home/claude/work/to/key-quality/2026-11-19/factcheck-run-44528656941'
held = 'AK AR DE FL GA ID MT NC OR RI UT VA WY'.split()
out = []
for st in held:
    old = json.load(open(f'/home/claude/work/oldkeys/US-{st}.json'))['parks']; new = json.load(open(f'/home/claude/work/newkeys/US-{st}.json'))['parks']
    fc = json.load(gzip.open(f'{fcd}/factcheck-US-{st}.json.gz'))['parks']
    recs = None
    for ref, p in new.items():
        n = [str(x[0]) for x in p.get('m') or []]; o = [str(x[0]) for x in (old.get(ref) or {}).get('m') or []]
        add = [i for i in n if i not in o]
        if not add: continue
        if recs is None: recs = M.load(st, cache)
        both = [i for i in set(o) | set(n) if i in recs]
        if not both: 
            out.append([st, ref, p['n'], (fc.get(ref) or {}).get('act'), len(o), len(n), len(add), '', '', '', '', (fc.get(ref) or {}).get('class'), 'records not in the saved shapes: ' + ' '.join(add[:4])]); continue
        r = M.measure(both, recs, maxpx=1800, want_masks=True)
        import numpy as np
        cell = r['cell']; z = np.zeros_like(r['union'])
        mo = z.copy(); mn = z.copy()
        for i in o:
            if i in r['masks']: mo |= r['masks'][i]
        for i in n:
            if i in r['masks']: mn |= r['masks'][i]
        A = lambda m: m.sum() * cell * cell / M.M2_AC
        e = fc.get(ref) or {}
        pin = e.get('pin'); inside = ''
        if pin:
            x, y = r['px']((pin[1], pin[0])); xi, yi = int(round(x)), int(round(y))
            inside = bool(0 <= yi < mn.shape[0] and 0 <= xi < mn.shape[1] and mn[yi, xi])
        layers = collections.Counter((''.join(ch for ch in i if not ch.isdigit()) or 'PAD-US') for i in add)
        names = collections.Counter((recs[i].get('Unit_Nm') or recs[i].get('Loc_Nm') or '?') for i in add if i in recs)
        out.append([st, ref, p['n'], e.get('act'), len(o), len(n), len(add), round(A(mo), 1), round(A(mn), 1), round(A(mn & ~mo), 1), round(A(mo & ~mn), 1), e.get('class'),
                    'pin inside new: %s | added from %s | names: %s' % (inside, dict(layers), '; '.join(f'{k} x{v}' for k, v in names.most_common(3)))])
w = csv.writer(open('/home/claude/work/yes-adds.csv', 'w', newline=''))
w.writerow(['state', 'ref', 'park', 'activations', 'rows_old', 'rows_new', 'rows_added', 'old_union_ac', 'new_union_ac', 'new_land_ac', 'removed_land_ac', 'class_new', 'notes'])
w.writerows(out)
print(len(out), 'parks gain at least one record in the held states')
grow = [x for x in out if isinstance(x[9], float) and x[9] >= 1 and (x[7] == 0 or x[9] / max(x[7], 1) >= 0.02)]
print('of them, the drawn land really grows (new land >= 1 acre and >= 2% of the old outline):', len(grow))
for x in sorted(grow, key=lambda x: -(x[9] or 0)): print(f"{x[0]} {x[1]:9} {x[2][:36]:36} act {str(x[3]):>5} | old {x[7]:>12,.1f} new {x[8]:>12,.1f} | NEW LAND {x[9]:>11,.1f} | removed {x[10]:>10,.1f} | {x[11]:9} | {x[12][:150]}")
import collections as C
print(C.Counter(x[0] for x in out), C.Counter(x[0] for x in grow))
