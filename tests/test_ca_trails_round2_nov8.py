#!/usr/bin/env python3
"""Nov 8 (CA trails round 2, Research handoff 20261108-1317 CST): every one of the 51 parks is in the outline-source ledger;
CA-2897 gets a hand join; CA-0752 stays open (point only) and CA-5042 stays check; no pin moved."""
import gzip, json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]; bad = 0
def check(ok, msg):
    global bad; bad += not ok; print(('PASS ' if ok else 'FAIL ') + msg)
L = json.loads(gzip.decompress((ROOT / 'data/waiting/outline-sources/ledger.json.gz').read_bytes()))
D = json.loads((ROOT / 'data/waiting/outline-sources/ca-trails-round2-nov8.json').read_text(encoding='utf-8'))['decisions']
check(len(D) == 51 and all('ca_trails_r2_nov8' in (L['rows'].get(r) or {}).get('trail', {}) for r in D), 'all 51 parks are in the ledger with a round-2 note')
check(any(s.get('id') == 'ca-trails-round2-nov8' for s in L['sources']), 'the handoff is listed as a ledger source')
check(L['rows']['CA-0752']['trail']['ca_trails_r2_nov8']['status'] == 'open' and 'open' in L['rows']['CA-0752']['trail']['status'], 'CA-0752 stays open (a point does not close the line gap)')
check(L['rows']['CA-5042']['trail']['ca_trails_r2_nov8']['status'] == 'check' and L['rows']['CA-5042']['trail']['status'] == 'check', 'CA-5042 stays check')
O = json.loads((ROOT / 'data/ca-key/overrides.json').read_text(encoding='utf-8'))['parks']
check(O.get('CA-2897', {}).get('join') == ['Wascana Valley Natural Area Recreation Site'] and O['CA-2897'].get('when') == '2026-11-08', 'CA-2897 hand join')
check(O.get('CA-5042', {}).get('approx') is True and 'CA-0752' not in O, 'CA-5042 keeps its approximate join; CA-0752 gets no join')
check(sum(1 for v in D.values() if v['status'] == 'outline already') == 8, 'eight leads were already outlined from the same official record')
print('ALL PASS' if not bad else 'SOME FAILED'); sys.exit(1 if bad else 0)
