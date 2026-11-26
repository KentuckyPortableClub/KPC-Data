import json, gzip, sys, csv, collections
import numpy as np
sys.path.insert(0, '/home/claude/work/scripts'); import measure as M
cache = '/home/claude/work/cache'; fcd = '/home/claude/work/to/key-quality/2026-11-19/factcheck-run-44528656941'
fco = '/home/claude/work/to/key-quality/2026-11-19/factcheck-pub'
held = 'AK AR DE FL GA ID MT NC OR RI UT VA WY'.split()
lost = {(x['area'], x['ref']): x for x in json.load(open(f'{fcd}/lost.json'))}
out = []; per = collections.defaultdict(lambda: collections.Counter())
for st in held:
    old = json.load(open(f'/home/claude/work/oldkeys/US-{st}.json'))['parks']; new = json.load(open(f'/home/claude/work/newkeys/US-{st}.json'))['parks']
    fc = json.load(gzip.open(f'{fcd}/factcheck-US-{st}.json.gz'))['parks']
    recs = M.load(st, cache)
    for ref, po in old.items():
        o = [str(x[0]) for x in po.get('m') or []]; n = [str(x[0]) for x in (new.get(ref) or {}).get('m') or []]
        if not o or set(o) == set(n): continue
        how_o = collections.Counter(str(x[3]).split()[0][:16] for x in po.get('m') or [] if str(x[0]) not in n)
        both = [i for i in set(o) | set(n) if i in recs]
        if not both: continue
        r = M.measure(both, recs, maxpx=1500, want_masks=True); cell = r['cell']
        z = np.zeros_like(r['union']); mo = z.copy(); mn = z.copy()
        for i in o:
            if i in r['masks']: mo |= r['masks'][i]
        for i in n:
            if i in r['masks']: mn |= r['masks'][i]
        A = lambda m: float(m.sum() * cell * cell / M.M2_AC)
        ao, an, rem, add = A(mo), A(mn), A(mo & ~mn), A(mn & ~mo)
        trail = any(i.startswith('trl') for i in n)
        kind = 'outline -> pin' if not n else ('to the trail line' if trail else ('same land (copies dropped)' if rem < max(1.0, 0.02 * ao) and add < max(1.0, 0.02 * ao) else ('smaller' if rem >= add else 'bigger')))
        per[st][kind] += 1
        e = fc.get(ref) or {}
        why = collections.Counter()
        for c in (new.get(ref) or {}).get('c') or []:
            if str(c[0]) in o: why[str(c[3]).split(':')[0][:28]] += 1
        out.append([st, ref, po.get('n'), e.get('act'), kind, round(ao, 1), round(an, 1), round(rem, 1), round(add, 1), e.get('class'), (lost.get((f'US-{st}', ref)) or {}).get('cause') or '', '; '.join(f'{k} x{v}' for k, v in why.most_common(2))])
w = csv.writer(open('/home/claude/work/yes-changes.csv', 'w', newline=''))
w.writerow(['state', 'ref', 'park', 'activations', 'kind', 'old_union_ac', 'new_union_ac', 'land_removed_ac', 'land_added_ac', 'class_new', 'planned_cause', 'why_removed'])
w.writerows(out)
kinds = ['outline -> pin', 'smaller', 'bigger', 'to the trail line', 'same land (copies dropped)']
print('state | ' + ' | '.join(kinds))
for st in held: print(st, '|', ' | '.join(str(per[st][k]) for k in kinds))
print('all 13 |', ' | '.join(str(sum(per[s][k] for s in held)) for k in kinds), '| parks', len(out))
sm = sorted([x for x in out if x[4] == 'smaller'], key=lambda x: -(x[3] or 0))
print('\nSMALLER, busiest first (top 25):')
for x in sm[:25]: print(f"{x[0]} {x[1]:9} {x[2][:36]:36} act {str(x[3]):>5} | {x[5]:>12,.0f} -> {x[6]:>12,.0f} (-{100*x[7]/max(x[5],1):.0f}%) | {x[9]:9} | {x[11][:70]}")
