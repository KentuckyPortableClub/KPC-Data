#!/usr/bin/env python3
"""Nov 7 2026 (Brandon's trail-match hand test): rivers matched on one shared word were rated high.
The matcher must reject the 3 bad highs and keep the 6 good ones. Offline: no network."""
import pathlib, sys, types
ROOT = pathlib.Path(__file__).resolve().parents[1]
D = ROOT / '.github/scripts/draft/tools/kpc_layers_nov7'
sys.path.insert(0, str(D))
sys.modules.setdefault('convert_layers', types.SimpleNamespace(polite_get=None, BLOCKED=()))
import match_trails as m  # noqa: E402
FAILS = []
WSR = 'National Wild and Scenic River'
CASES = [  # (ref, park, type, feature, spatial, want_high)
    ('US-12788', 'Black River National Wild and Scenic River', WSR, 'Black Mountain Pathway', True, False),
    ('US-12794', 'Paint National Wild and Scenic River', WSR, 'Paint Creek Trail', True, False),
    ('US-12786', 'Au Sable National Wild and Scenic River', WSR, 'Hartwick Pines Au Sable River Trail', True, False),
    ('US-11953', 'St. Francis Scenic Byway National Scenic Trail', 'National Scenic Trail', 'St. Francis Scenic Byway', True, True),
    ('US-8316', 'Scenic 7 Byway State Trail', 'State Trail', 'Arkansas Scenic 7 Byway', True, True),
    ('US-9163', 'Saracen State Trail', 'State Trail', 'Lake Saracen Walking Trail', True, True),
    ('US-10880', 'Paintrock Canyon Trail BLM Recreation Management Area', 'BLM Recreation Management Area', 'Paint Rock Canyon Trail', True, True),
    ('US-10884', 'Red Gulch/Alkali Backcountry Byway BLM Special Recreation Management Area', 'BLM Special Recreation Management Area', 'Red Gulch/Alkali Back Country Byway', True, True),
    ('US-10929', 'Cottonwood Creek Trailhead BLM Recreation Management Area', 'BLM Recreation Management Area', 'Cottonwood Creek Trail', True, True),
]
for ref, park, ty, feat, sp, want in CASES:
    sc, _ = m.name_score(park, ty, [feat])
    got = m.confidence(sc, sp) == 'high'
    ok = got == want
    print(('PASS ' if ok else 'FAIL ') + f'{ref} {feat!r} high={got} (want {want})')
    if not ok: FAILS.append(ref)
sc, _ = m.name_score('Au Sable National Wild and Scenic River', WSR, ['Au Sable River'])
print(('PASS ' if sc >= 0.85 else 'FAIL ') + 'the river itself still matches a WSR park')
if sc < 0.85: FAILS.append('river')
import csv, gzip, json  # noqa: E402
rows = json.loads(gzip.open(ROOT / 'data/waiting/outline-sources/ledger.json.gz').read())['rows']
parks = list(csv.DictReader(open(D / 'inputs/kpc-pota-trail-parks-no-outline-nov7.csv', encoding='utf-8')))
miss = [p['ref'] for p in parks if not any((v.get('trail') or {}).get('status') for k, v in rows.items() if k == p['ref'] or k.startswith(p['ref'] + '|'))]
print(('PASS ' if not miss else 'FAIL ') + f'all {len(parks)} trail parks have a trail status in the ledger (missing {miss[:5]})')
if miss: FAILS.append('ledger')
sys.exit(1 if FAILS else 0)
