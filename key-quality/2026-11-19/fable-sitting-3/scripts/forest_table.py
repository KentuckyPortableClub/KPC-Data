import json, gzip, csv, sys, collections
sys.path.insert(0, '/home/claude/work/scripts'); import measure as M
cache = '/home/claude/work/cache'
recs = M.load('ID', cache)
key = json.load(open(f'{cache}/held/US-ID.json'))['parks']
fc = json.load(gzip.open('/home/claude/work/to/key-quality/2026-11-19/factcheck-run-44528656941/factcheck-US-ID.json.gz'))['parks']
kc = list(csv.DictReader(open('/home/claude/work/to/key-quality/2026-11-19/kitC-acreage/answers/kitC-usfs-acres.answers.csv')))
adm = collections.defaultdict(dict)
for r in kc:
    if 'Table 28' in r['unit_type']: adm[r['unit_name']][r['acres_kind']] = float(r['official_acres'])
own = {i for i, a in recs.items() if 'BasicOwnership' in str(a.get('Loc_Mang'))}
out = []
for ref, p in key.items():
    ids = [str(x[0]) for x in p.get('m') or [] if str(x[0]) in own]
    if not ids: continue
    r = M.measure(ids, recs, maxpx=3000)
    ac = sorted(((r['rec_ac'][i], i) for i in ids), reverse=True)
    nm = recs[ids[0]].get('Unit_Nm')
    o = adm.get(nm) or {}
    nfs, gross = o.get('NFS acres'), o.get('gross acres')
    rest = sum(a for a, _ in ac[1:])
    out.append([ref, p['n'], (fc.get(ref) or {}).get('act'), nm, round(ac[0][0]), round(nfs) if nfs else '', round(rest), round(gross - nfs) if nfs else '', ' '.join(i for _, i in ac[1:]), (fc.get(ref) or {}).get('class')])
out.sort(key=lambda x: -(x[2] or 0))
w = csv.writer(open('/home/claude/work/id-forest-not-fs.csv', 'w', newline=''))
w.writerow(['ref', 'park', 'activations', 'layer_forest_name', 'largest_record_ac', 'usfs_report_nfs_ac', 'other_records_ac', 'usfs_report_other_ac_gross_minus_nfs', 'other_record_ids', 'class_now'])
w.writerows(out)
for x in out: print(x[0], x[1][:34].ljust(34), 'act', str(x[2]).rjust(4), '| largest', f'{x[4]:>10,}', 'NFS', f'{x[5]:>10,}' if x[5] else '         -', '| others', f'{x[6]:>8,}', 'report other', f'{x[7]:>8,}' if x[7] != '' else '       -', '|', x[8], '|', x[9])
print('parks', len(out), '| other-record acres in all', f"{sum(x[6] for x in out):,}", '| activations', sum(x[2] or 0 for x in out))
