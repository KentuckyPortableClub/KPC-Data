#!/usr/bin/env python3
"""Nov 8 hand-downloaded layers (Research 1740–1755 CST): GA SP, TX SP, TX WMA, PA SGL, GA WMA, MB provincial parks.
Every lead is in the ledger; 24 hand joins; far/name-mismatch pins held; Tallulah Gorge WMA never gets the SP polygon;
no-pin tracts are possible candidates only; no pin moved."""
import gzip, json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]; bad = 0
def check(ok, msg):
    global bad; bad += not ok; print(('PASS ' if ok else 'FAIL ') + msg)
L = json.loads(gzip.decompress((ROOT / 'data/waiting/outline-sources/ledger.json.gz').read_bytes()))
D = json.loads((ROOT / 'data/waiting/outline-sources/hand-layers-nov8.json').read_text(encoding='utf-8'))
dec = D['decisions']; Ou = json.loads((ROOT / 'data/us-key/overrides.json').read_text(encoding='utf-8'))['parks']
Oc = json.loads((ROOT / 'data/ca-key/overrides.json').read_text(encoding='utf-8'))['parks']
check(any(s.get('id') == 'research-hand-layers-nov8' for s in L['sources']), 'handoffs listed as a ledger source')
check(all('hand_layers_nov8' in (L['rows'].get(k) or {}) for k in dec), 'every lead is in the ledger (%d)' % len(dec))
J = {k: v['ids'] for k, v in dec.items() if v['status'] == 'joined'}
check(len(J) == 24, '24 hand joins (%d)' % len(J))
for k, ids in J.items():
    O = Oc if k.startswith('CA-') else Ou
    check(set(ids) <= set(O[k]['join']) and all(i in O[k].get('fp', {}) for i in ids), k + ' join + fingerprint')
check(Ou['US-2200']['join'] == ['sggab32'] and 'none' not in Ou['US-2200'], 'US-2200 = Stephen C. Foster')
check('sggab12' in Ou['US-12418']['no'] and 'sggab12' not in Ou['US-12418'].get('join', []), 'US-12418 never joins Tallulah Gorge SP')
check(dec['US-2199']['status'] == 'outline already', 'US-2199 already Dukes Creek / Smithgall Woods')
check(dec['US-3510']['status'] == 'outline already', 'US-3510 Powderhorn keeps the WMA polygon')
H = {k for k, v in dec.items() if v['status'] == 'held'}
need = {'US-6571','US-6565','US-6551','US-6535','US-6550','US-3505','US-6572','US-3751','US-9770','US-4650','US-3729','US-7896','CA-0527','CA-0558','CA-0551'}
check(need <= H and not any(k in J for k in H), 'far / name-mismatch pins held, not joined')
C = {c['name'] for c in D['possible_candidates']}
check({'Balls Ferry State Park','Mossy Creek State Park','Bush Head Shoals State Park','Indian Lodge','Chinati Mountains'} <= C, 'no-pin polygons are possible candidates')
check(Oc['CA-2373']['join'] == ['Manitoba Par:32'], 'CA-2373 Primrose hand join')
check((ROOT / 'data/waiting/outline-sources/hand-layers/ca-mb-provparks.geojson').is_file(), 'Manitoba shapes file kept (replaces missing)')
print('ALL PASS' if not bad else 'SOME FAILED'); sys.exit(1 if bad else 0)
