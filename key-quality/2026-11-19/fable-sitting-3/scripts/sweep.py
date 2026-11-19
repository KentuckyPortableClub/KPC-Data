import json, gzip, glob, sys, csv
sys.path.insert(0, '/home/claude/work/scripts'); import measure as M
cache = '/home/claude/work/cache'; fcd = '/home/claude/work/to/key-quality/2026-11-19/factcheck-run-44528656941'
rows = []
for f in sorted(glob.glob('/home/claude/work/newkeys/US-*.json')):
    k = json.load(open(f)); st = k['st']
    todo = [(r, p) for r, p in k['parks'].items() if p.get('m') and p.get('ac_how') == 'measured' and len(p['m']) > 1]
    if not todo: continue
    recs = M.load(st, cache)
    fc = json.load(gzip.open(f'{fcd}/factcheck-US-{st}.json.gz'))['parks']
    for ref, p in todo:
        ids = [str(x[0]) for x in p['m']]
        r = M.measure(ids, recs, maxpx=2500)
        if r is None: rows.append([st, ref, p['n'], len(ids), p.get('ac'), '', '', '', '', '', '', 'no shapes']); continue
        e = fc.get(ref) or {}
        a = e.get('acres') or {}
        fl = ','.join(x[0] for x in e.get('flags') or [])
        rows.append([st, ref, p['n'], len(ids), p.get('ac'), round(r['union_ac']), round((p.get('ac') or 0) / max(r['union_ac'], 1), 2), a.get('official'), a.get('official_is'),
                     e.get('class'), '+'.join(e.get('witnesses') or []), fl, e.get('act')])
w = csv.writer(open('/home/claude/work/sweep.csv', 'w', newline=''))
w.writerow(['state', 'ref', 'name', 'rows', 'key_ac_added_up', 'true_union_ac', 'key_over_union', 'official_ac', 'official_is', 'class', 'witnesses', 'flags', 'activations'])
w.writerows(rows)
print(len(rows), 'parks measured')
