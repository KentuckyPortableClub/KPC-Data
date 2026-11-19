import csv, json, re, collections, urllib.parse
B = '/home/claude/work/in03b/KPC-03B-results/'; A = '/home/claude/work/to/key-quality/2026-11-19/handoff-02/answers-pass1/'
K = json.load(open('/home/claude/work/to/key-quality/2026-11-19/handoff-03/kit-keys/handoff-03B-answer-key.json'))
rd = lambda f: list(csv.DictReader(open(f, encoding='utf-8-sig')))
p2 = rd(B + 'job3-busy-parks-is-there-official-gis.answers.csv'); p1 = {r['ref']: r for r in rd(A + 'job3-pin-only-busiest-100.answers.csv')}
ANS = 'answer (GIS / PICTURE / NOTHING)'
def norm(a): 
    a = (a or '').strip().upper()
    return 'GIS' if a.startswith('GIS') else 'PICTURE' if a.startswith('PIC') else 'NOTHING' if a.startswith('NOTH') else (a or 'OPEN')
def svc(u):
    u = (u or '').strip().split()[0] if (u or '').strip() else ''
    m = re.match(r'https?://([^/]+)(/[^?#]*)?', u)
    if not m: return ''
    host = m.group(1).lower(); path = (m.group(2) or '').lower()
    path = re.sub(r'/(featureserver|mapserver)(/\d+)?.*$', '', path)
    return host + path.rstrip('/')
plants = {x['ref']: x for x in K['job3_plants']}
rows = []; tally = collections.Counter(); plant_res = []
for r in p2:
    ref = r['ref']; a2 = norm(r[ANS]); o = p1.get(ref); a1 = norm(o[ANS]) if o else 'NOT IN PASS 1'
    if ref in plants:
        ok = a2 == 'GIS' and (svc(r['gis_layer_address']) and svc(r['gis_layer_address']) in svc(plants[ref]['known'].split('|')[1].strip()) or svc(plants[ref]['known'].split('|')[1].strip()) in svc(r['gis_layer_address']))
        plant_res.append((r['item'], ref, r['name'][:34], a2, 'RIGHT' if ok else 'CHECK', r['gis_layer_address'][:90])); continue
    same_layer = ''
    if a1 == 'GIS' and a2 == 'GIS':
        s1, s2 = svc(o['gis_layer_address']), svc(r['gis_layer_address'])
        same_layer = 'same layer' if s1 and s1 == s2 else ('same host' if s1.split('/')[0] == s2.split('/')[0] else 'DIFFERENT layer')
    k = (a1, a2, same_layer); tally[k] += 1
    rows.append([r['item'], ref, r['name'], r['area'], r['activations'], a1, a2, same_layer, (o or {}).get('gis_layer_address', ''), r['gis_layer_address'], r['record_name_exactly_as_the_layer_shows_it'], r['record_acres_as_the_layer_shows_it'], r['needs_a_human_download (YES / NO + why)'][:60], r['note'][:300]])
print('JOB 3 plants:'); [print('  ', x) for x in plant_res]
print('JOB 3, pass 1 -> pass 2 (55 real rows):')
for k, v in sorted(tally.items(), key=lambda x: -x[1]): print('  ', v, k)
w = csv.writer(open('/home/claude/work/job3-both-passes.csv', 'w', newline='')); w.writerow(['item', 'ref', 'name', 'area', 'activations', 'pass1', 'pass2', 'layer_match', 'pass1_layer', 'pass2_layer', 'pass2_record_name', 'pass2_record_acres', 'pass2_human_download', 'pass2_note']); w.writerows(rows)
agree_gis = [x for x in rows if x[5] == 'GIS' and x[6] == 'GIS']
print('both say GIS:', len(agree_gis), '| of them same layer:', sum(1 for x in agree_gis if x[7] == 'same layer'), 'same host:', sum(1 for x in agree_gis if x[7] == 'same host'), 'different:', sum(1 for x in agree_gis if x[7] == 'DIFFERENT layer'))
print('\nDISAGREE (pass 1 GIS, pass 2 not):')
for x in rows:
    if x[5] == 'GIS' and x[6] != 'GIS': print(f"  {x[1]:9} {x[2][:40]:40} {x[3]} act {x[4]:>5} | pass 2: {x[6]} | {x[13][:170]}")
print('\nPASS 1 OPEN rows, pass 2 answers:')
for x in rows:
    if x[5] not in ('GIS',): print(f"  {x[1]:9} {x[2][:40]:40} {x[3]} act {x[4]:>5} | pass 1 {x[5]} -> pass 2 {x[6]} | {x[9][:80]}")
