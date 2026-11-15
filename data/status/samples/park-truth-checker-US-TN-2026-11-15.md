# park truth checker: US-TN random sample of 12 (2026-11-15; seed = date + area, same rows for everyone)

Source file: `data/truth/US-TN.json`

## US-2933 Booker T Washington State Park
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-15",
 "n": "Booker T Washington State Park",
 "official": null,
 "ours": {
  "acres": 466,
  "family_fold": "layers {'padus': 434, 'sgtnf': 358}: one land in 2 layers, the padus copy used (358 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    1849,
    "Booker T. Washington State Park",
    419,
    "name"
   ],
   [
    256169,
    "Booker T Washington",
    15,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 3
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-6271 Sunk Lake State Natural Area
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-15",
 "n": "Sunk Lake State Natural Area",
 "official": null,
 "ours": {
  "acres": 1873,
  "dissolved": {
   "after": 1873,
   "before": 5620,
   "copies": 1,
   "parts": 4,
   "records": 6,
   "tracts": 1
  },
  "manager": "",
  "note": "6 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 4 fee tracts under a designation record folded; summed 5620 -> 1873 acres",
  "pieces": [
   [
    255657,
    "Sunk Lake Designated State Natural Area",
    1873,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "State Natural Area",
 "verdict": "no size on page"
}
```

## US-2954 Johnsonville State Park
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-15",
 "n": "Johnsonville State Park",
 "official": null,
 "ours": {
  "acres": 1487,
  "dissolved": {
   "after": 2586,
   "before": 3688,
   "copies": 2,
   "families": {
    "padus": 1846,
    "sgtnf": 740
   },
   "family_fold": 740,
   "family_used": "padus",
   "key_union": 1487,
   "parts": 0,
   "records": 6,
   "summed": 1846,
   "tracts": 4
  },
  "family_fold": "layers {'padus': 1846, 'sgtnf': 740}: one land in 2 layers, the padus copy used (740 ac of copies not added)",
  "manager": "",
  "note": "6 joined records = 4 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 3688 -> 2586 acres",
  "pieces": [
   [
    255621,
    "Johnsonville",
    800,
    "name"
   ],
   [
    255622,
    "Johnsonville",
    551,
    "name"
   ],
   [
    1821,
    "Johnsonville State Historic Park",
    495,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 4
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-2965 Paris Landing State Park
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-15",
 "n": "Paris Landing State Park",
 "official": null,
 "ours": {
  "acres": 789,
  "family_fold": "layers {'padus': 789, 'sgtnf': 469}: one land in 2 layers, the padus copy used (469 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    255632,
    "Paris Landing",
    789,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 3
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-4560 Natchez Trace Trail National Scenic Trail
```json
{
 "checked": "2026-11-15",
 "handover": [],
 "n": "Natchez Trace Trail National Scenic Trail",
 "note": "whole park compared (POTA lists it in 3 states: {'US-TN': 31527, 'US-AL': 31527, 'US-MS': 31527})",
 "official": null,
 "ours": {
  "acres": 94581,
  "acres_by_state": {
   "US-AL": 31527,
   "US-MS": 31527,
   "US-TN": 31527
  },
  "manager": "",
  "pieces": [
   [
    3552,
    "Natchez Trace Parkway",
    31527,
    "reviewed-approx"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "states": [
   "US-TN",
   "US-AL",
   "US-MS"
  ],
  "unknown_pieces": 0,
  "whole_park": true
 },
 "owner_now": null,
 "pct": null,
 "score": 5,
 "t": "National Scenic Trail",
 "verdict": "no size on page"
}
```

## US-3934 Chickasaw State Wildlife Area
```json
{
 "checked": "2026-11-15",
 "handover": [],
 "n": "Chickasaw State Wildlife Area",
 "official": null,
 "ours": {
  "acres": 14688,
  "dissolved": {
   "after": 14688,
   "before": 53886,
   "copies": 3,
   "parts": 0,
   "records": 5,
   "tracts": 2
  },
  "manager": "",
  "note": "5 joined records = 2 tracts: 3 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 53886 -> 14688 acres",
  "pieces": [
   [
    255551,
    "Chickasaw State Forest & Wildlife Management Area",
    13301,
    "name"
   ],
   [
    255597,
    "Chickasaw",
    1387,
    "name (designation code ignored)"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "State Wildlife Area",
 "verdict": "no size on page"
}
```

## US-7573 Black Bayou Refuge Wildlife Management Area
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-15",
 "n": "Black Bayou Refuge Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 1374,
  "dissolved": {
   "after": 1374,
   "before": 4846,
   "copies": 4,
   "parts": 0,
   "records": 6,
   "tracts": 2
  },
  "manager": "",
  "note": "6 joined records = 2 tracts: 4 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 4846 -> 1374 acres",
  "pieces": [
   [
    255761,
    "Black Bayou Refuge",
    1049,
    "name"
   ],
   [
    255762,
    "Black Bayou Refuge",
    325,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "Wildlife Management Area",
 "verdict": "no size on page"
}
```

## US-3970 Yanahli Wildlife Management Area
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-15",
 "n": "Yanahli Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 13505,
  "dissolved": {
   "after": 12859,
   "before": 51089,
   "copies": 3,
   "key_union": 13505,
   "parts": 0,
   "records": 4,
   "summed": 12859,
   "tracts": 1
  },
  "manager": "",
  "note": "4 joined records = 1 tracts: 3 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 51089 -> 12859 acres",
  "pieces": [
   [
    "sgtni195",
    "Yanahli WMA",
    12859,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "Wildlife Management Area",
 "verdict": "no size on page"
}
```

## US-6278 Watauga River Bluffs State Natural Area
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-15",
 "n": "Watauga River Bluffs State Natural Area",
 "official": null,
 "ours": {
  "acres": 57,
  "dissolved": {
   "after": 50,
   "before": 100,
   "copies": 1,
   "key_union": 57,
   "parts": 0,
   "records": 2,
   "summed": 50,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 100 -> 50 acres",
  "pieces": [
   [
    255676,
    "Watauga River Bluffs Designated State Natural Area",
    50,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "State Natural Area",
 "verdict": "no size on page"
}
```

## US-7575 Browntown Wildlife Management Area
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-15",
 "n": "Browntown Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 6775,
  "dissolved": {
   "after": 12997,
   "before": 25441,
   "copies": 2,
   "families": {
    "padus": 6222,
    "sgtni": 6775
   },
   "family_fold": 6222,
   "family_used": "sgtni",
   "parts": 0,
   "records": 4,
   "tracts": 2
  },
  "family_fold": "layers {'sgtni': 6775, 'padus': 6222}: one land in 2 layers, the sgtni copy used (6,222 ac of copies not added)",
  "manager": "",
  "note": "4 joined records = 2 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 25441 -> 12997 acres",
  "pieces": [
   [
    "sgtni138",
    "Browntown WMA",
    6775,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "Wildlife Management Area",
 "verdict": "no size on page"
}
```

## US-7607 Nolichucky Wildlife Management Area
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-15",
 "n": "Nolichucky Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 2321,
  "dissolved": {
   "after": 2472,
   "before": 2817,
   "copies": 1,
   "families": {
    "sgtnc": 345,
    "sgtni": 2127
   },
   "family_fold": 345,
   "family_used": "sgtni",
   "key_union": 2321,
   "parts": 0,
   "records": 3,
   "summed": 2127,
   "tracts": 2
  },
  "family_fold": "layers {'sgtni': 2127, 'sgtnc': 345}: one land in 2 layers, the sgtni copy used (345 ac of copies not added)",
  "manager": "",
  "note": "3 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 2817 -> 2472 acres",
  "pieces": [
   [
    "sgtni55",
    "Nolichucky WMA",
    2127,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "Wildlife Management Area",
 "verdict": "no size on page"
}
```

## US-7596 Headwaters Wildlife Management Area
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-15",
 "n": "Headwaters Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 555,
  "dissolved": {
   "after": 555,
   "before": 1665,
   "copies": 2,
   "parts": 0,
   "records": 3,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1665 -> 555 acres",
  "pieces": [
   [
    255712,
    "Headwaters Wildlife Management Area",
    555,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "Wildlife Management Area",
 "verdict": "no size on page"
}
```
