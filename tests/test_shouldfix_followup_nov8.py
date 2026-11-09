#!/usr/bin/env python3
"""Nov 8 should-fix follow-up: honest t786u citation; accept-polygon apply within rules; #50 license URLs."""
import json, pathlib, sys, csv
ROOT = pathlib.Path(__file__).resolve().parents[1]
ok = True
def check(c, m):
    global ok
    print(('PASS ' if c else 'FAIL ') + m)
    ok = ok and bool(c)

us = json.load(open(ROOT / 'data/us-key/overrides.json'))['parks']
ca = json.load(open(ROOT / 'data/ca-key/overrides.json'))['parks']
eight = ['US-3505','US-3751','US-6535','US-6565','US-9770','US-6551','CA-0527','CA-0558']
for ref in eight:
    e = (us if ref.startswith('US-') else ca)[ref]
    check('general ruling' in (e.get('why') or ''), '%s why cites general ruling' % ref)
    check('named set' in (e.get('why') or '') or 'this named set' in (e.get('why') or ''), '%s why says named set' % ref)

# Applied without decided_by
for ref, parks, jid in [
    ('US-2200', us, 'sggab60'),  # sggab32 dropped — labeled-tract proposal
    ('CA-2373', ca, 'Manitoba Par:32'),
]:
    e = parks[ref]
    check(jid in (e.get('join') or []), '%s joined %s' % (ref, jid))
    check(not str(e.get('decided_by') or '').strip(), '%s has no decided_by (unsigned apply)' % ref)
    check(not e.get('none'), '%s none cleared' % ref)
check('sggab32' not in (us['US-2200'].get('join') or []), 'US-2200 does not unsigned-join sggab32 (~25 km)')
check((ROOT / 'data/waiting/in/data/pile-solver/hand-layers-LABELED-TRACT-PROPOSALS.csv').is_file(), 'labeled-tract proposals file present')

# Left as proposals
for ref in ('US-6571', 'US-6550'):
    e = us.get(ref) or {}
    check(not e.get('join'), '%s has no override join (left as proposal)' % ref)

# #50 license URLs
HL = ROOT / 'data/waiting/outline-sources/hand-layers'
for name in ['us-tx-stateparks','us-tx-wma','us-ga-stateparks','us-ga-wma','us-pa-sgl','ca-mb-provparks']:
    d = json.load(open(HL / (name + '.geojson.about.json')))
    check(bool(d.get('license_url')), '%s has license_url' % name)
ga = json.load(open(HL / 'us-ga-wma.geojson.about.json'))
check('CONFIRMED' in (ga.get('layer_confirm') or ''), 'GA WMA layer confirmed')
check('Georgia_Licenses_by_District' in (ga.get('layer_confirm') or '') or 'WMA' in (ga.get('layer_confirm') or ''), 'GA confirm mentions layer/WMA')

# hashes
for path, want in [
    (ROOT / 'data/us-key/index.json', 'a066624520b4'),
    (ROOT / 'data/ca-key/index.json', '8feccbb7d9ee'),
]:
    d = json.load(open(path))
    check((d.get('rules_of_run') or d.get('rules')) == want, '%s hash' % path.name)

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
