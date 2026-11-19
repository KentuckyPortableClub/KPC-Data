import json, gzip, sys
sys.path.insert(0, '/home/claude/repos/KPC-Links/.github/scripts')
import kpc_key_rules as KR
sys.path.insert(0, '/home/claude/work/scripts'); import measure as M
cache = '/home/claude/work/cache'
for st, ref, official, note in (('FL', 'US-6321', 29000, 'FWC page: more than 29,000'), ('FL', 'US-6328', 63000, 'FWC page: more than 63,000'), ('ID', 'US-4500', 743000, 'bad read: the wilderness share')):
    p = json.load(open(f'{cache}/held/US-{st}.json'))['parks'][ref]
    recs = M.load(st, cache)
    got = KR.measured_ac(p['m'], lambda i: recs[i].get('_r') if i in recs else None, p.get('parts'))
    u = M.measure([str(x[0]) for x in p['m']], recs)['union_ac']
    print(f"{ref}: key ac {p['ac']:,} | the key's own adding-up function gives {got[0]:,} ({got[1]} rows measured) | true union {u:,.0f} | official {official:,} ({note}) | key/official {p['ac']/official:.2f}x | union/official {u/official:.2f}x")
