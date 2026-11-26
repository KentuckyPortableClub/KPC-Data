import csv, re, collections
K = '/home/claude/work/to/key-quality/2026-11-19/kitC-acreage/answers/'
def norm(s):
    s = s.lower().replace('&', 'and')
    s = re.sub(r'\b(national|wildlife|refuge|forests?|park|preserve|recreation|area|monument|historical|historic|site|grassland|battlefield|seashore|memorial|military|wmd|nwr|nf|np|nra|and)\b', ' ', s)
    return re.sub(r'[^a-z0-9]+', ' ', s).strip()
def num(s):
    try: return float(str(s).replace(',', '').replace(' ', '').replace('|', ''))
    except ValueError: return None
off = collections.defaultdict(dict)
for fn, ag in (('kitC-fws-acres.answers.csv', 'FWS'), ('kitC-usfs-acres.answers.csv', 'USFS'), ('kitC-nps-acres.answers.csv', 'NPS')):
    for r in csv.DictReader(open(K + fn)):
        v = num(r['official_acres'])
        if v is None: continue
        ut = r['unit_type']
        if ag == 'USFS' and 'Table 28' not in ut: continue          # the administrative unit = how POTA names forests
        if ag == 'FWS' and 'Table 3' not in ut: continue             # refuges
        kind = r['acres_kind'] or 'total'
        off[(ag, norm(r['unit_name']))][kind] = max(v, off[(ag, norm(r['unit_name']))].get(kind, 0))
R = list(csv.DictReader(open('/home/claude/work/d7-check.csv')))
f = lambda x: float(x or 0)
hits = []
for r in R:
    ag = r['manager'] if r['manager'] in ('FWS', 'USFS', 'NPS') else None
    if not ag: continue
    o = off.get((ag, norm(r['park'])))
    if not o: continue
    hits.append((r, o))
print(len(R), 'parks with a dropped compilation copy;', len(hits), 'matched to an agency acreage table (kit C)')
print('\nJOINED RECORDS UNDER 80% OF THE AGENCY\'S OWN ACRES after the copy is dropped:')
for r, o in sorted(hits, key=lambda h: -f(h[0]['activations'])):
    best = o.get('NFS acres') or o.get('federal') or o.get('total') or max(o.values())
    j, c = f(r['joined_ac']), f(r['dropped_copy_ac'])
    if j < 0.8 * best:
        print(f"  {r['state']} {r['held_or_saved']:5} {r['ref']:9} {r['park'][:40]:40} act {r['activations']:>5} | agency says {best:>11,.0f} ({'/'.join(o)}) | joined now {j:>11,.0f} ({100*j/best:.0f}%) | dropped copy {c:>11,.0f} ({100*c/best:.0f}%)")
ok = sum(1 for r, o in hits if f(r['joined_ac']) >= 0.8 * (o.get('NFS acres') or o.get('federal') or o.get('total') or max(o.values())))
print('\nmatched parks whose joined records are 80%+ of the agency acres (the drop is right):', ok)
