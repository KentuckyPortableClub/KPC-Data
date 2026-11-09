#!/usr/bin/env python3
"""Nov 8 (#53): unsigned overrides.json joins must NOT exempt far (>5 km) pieces; decided_by ones must.

Links #77's test_signed_override_holds_nov8 said 'an unsigned far join is still held' but used a park with
NO override entry — it did not cover an unsigned override that lists the far piece. approvals() used to
copy every overrides join into ok, so exempt() treated unsigned overrides like signatures. Together with
the builder's ~0.6° override box, that could keep pieces beyond 5 km without decided_by.

This test imports kpc_join_check from LINKS and asserts the gap is closed. Also checks #52's 8 signed
overrides still exempt, and our unsigned applies (US-2200 sggab60, CA-2373) are not far.
"""
import json, os, pathlib, sys, tempfile
ROOT = pathlib.Path(__file__).resolve().parents[1]
LINKS = pathlib.Path(os.environ.get('LINKS') or (ROOT / '../links')).resolve()
sys.path.insert(0, str(LINKS / '.github/scripts'))
import kpc_join_check as J

ok = True
def check(c, m):
    global ok
    print(('PASS ' if c else 'FAIL ') + m)
    ok = ok and bool(c)

# --- Gap closed: unsigned override far piece is HELD; decided_by PASSES ---
with tempfile.TemporaryDirectory() as td:
    td = pathlib.Path(td); (td / 'data/us-key').mkdir(parents=True)
    json.dump({'parks': {
        'US-88888': {'join': ['far-piece-1'], 'why': 'unsigned', 'when': '2026-11-08'},
        'US-88887': {'join': ['signed-piece-1'], 'fp': {'signed-piece-1': ['Signed Land', 10]},
                     'why': 'signed', 'decided_by': 'Brandon (KZ4CP), Nov 8 2026'},
    }}, open(td / 'data/us-key/overrides.json', 'w'))
    okmap, _ = J.approvals(str(td), 'us', {'ANSWER_SHEET': '/nonexistent'})
    check('far-piece-1' not in (okmap.get('US-88888') or set()), 'unsigned override ids not in ok map')
    check(J.exempt('US-88888', {'m': [['far-piece-1', 'Far', 0, 'name']]}, okmap) == '',
          'unsigned override far join is still held')
    check(J.exempt('US-88887', {'m': [['signed-piece-1', 'Signed Land', 0, 'name']]}, okmap).startswith('signed override'),
          'decided_by override far join passes')

# --- #52's 8 signed overrides still pass ---
us = json.load(open(ROOT / 'data/us-key/overrides.json'))['parks']
ca = json.load(open(ROOT / 'data/ca-key/overrides.json'))['parks']
okmap, _ = J.approvals(str(ROOT), 'us', {'ANSWER_SHEET': '/nonexistent'})
okmap_c, _ = J.approvals(str(ROOT), 'ca', {'ANSWER_SHEET': '/nonexistent'})
eight = {
    'US-3505': us, 'US-3751': us, 'US-6535': us, 'US-6565': us, 'US-9770': us, 'US-6551': us,
    'CA-0527': ca, 'CA-0558': ca,
}
for ref, parks in eight.items():
    v = parks[ref]
    check(bool(str(v.get('decided_by') or '').strip()), '%s has decided_by' % ref)
    om = okmap if ref.startswith('US-') else okmap_c
    # refresh SIGNED for ca
    if ref.startswith('CA-'):
        J.approvals(str(ROOT), 'ca', {'ANSWER_SHEET': '/nonexistent'})
    else:
        J.approvals(str(ROOT), 'us', {'ANSWER_SHEET': '/nonexistent'})
    p = {'m': [[x, (v.get('fp') or {}).get(x, ['?'])[0], 0, 'name'] for x in v.get('join') or []]}
    why = J.exempt(ref, p, om if ref.startswith('US-') else okmap_c)
    # re-get okmap after approvals for correct kind
    om2, _ = J.approvals(str(ROOT), 'us' if ref.startswith('US-') else 'ca', {'ANSWER_SHEET': '/nonexistent'})
    why = J.exempt(ref, p, om2)
    check(why.startswith('signed override'), '%s signed far join not held (%s)' % (ref, why or 'HELD'))

# --- Our unsigned applies are within band / not far ---
check(us['US-2200']['join'] == ['sggab60'], 'US-2200 unsigned join is sggab60 only')
check('sggab32' not in us['US-2200']['join'], 'sggab32 not in unsigned US-2200 join')
check(ca['CA-2373']['join'] == ['Manitoba Par:32'], 'CA-2373 unsigned join kept')
check(not str(us['US-2200'].get('decided_by') or '').strip(), 'US-2200 remains unsigned')
check(not str(ca['CA-2373'].get('decided_by') or '').strip(), 'CA-2373 remains unsigned')

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
