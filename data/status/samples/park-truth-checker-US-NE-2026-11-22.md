# park truth checker: US-NE random sample of 12 (2026-11-22; seed = date + area, same rows for everyone)

Source file: `data/truth/US-NE.json`

## US-5629 Sherman Reservoir State Recreation Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Sherman Reservoir State Recreation Area",
 "official": null,
 "ours": {
  "acres": 3707,
  "family_fold": "layers {'sgnec': 4386, 'padus': 2710}: one land in 2 layers, the sgnec copy used (2,710 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgnec53",
    "Sherman Reservoir SRA",
    4386,
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
 "t": "State Recreation Area",
 "verdict": "no size on page"
}
```

## US-4030 Bear Creek Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Bear Creek Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 120,
  "dissolved": {
   "after": 120,
   "before": 238,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 238 -> 120 acres",
  "pieces": [
   [
    215676,
    "Bear Creek",
    120,
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

## US-13615 Kirkpatrick Basin South Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Kirkpatrick Basin South Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 417,
  "dissolved": {
   "after": 417,
   "before": 1248,
   "copies": 1,
   "parts": 4,
   "records": 6,
   "tracts": 1
  },
  "manager": "",
  "note": "6 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 4 fee tracts under a designation record folded; summed 1248 -> 417 acres",
  "pieces": [
   [
    "sgneb162",
    "Kirkpatrick Basin South WMA",
    417,
    "reviewed"
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

## US-11868 Pawnee Prairie Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Pawnee Prairie Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 1140,
  "dissolved": {
   "after": 2259,
   "before": 3378,
   "copies": 1,
   "families": {
    "padus": 1119,
    "sgneb": 1140
   },
   "family_fold": 1119,
   "family_used": "sgneb",
   "parts": 0,
   "records": 4,
   "tracts": 3
  },
  "family_fold": "layers {'sgneb': 1140, 'padus': 1119}: one land in 2 layers, the sgneb copy used (1,119 ac of copies not added)",
  "manager": "",
  "note": "4 joined records = 3 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 3378 -> 2259 acres",
  "pieces": [
   [
    "sgneb228",
    "Pawnee Prairie WMA",
    1140,
    "reviewed"
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

## US-5625 Mormon Island State Recreation Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Mormon Island State Recreation Area",
 "official": null,
 "ours": {
  "acres": 168,
  "dissolved": {
   "after": 723,
   "before": 875,
   "copies": 1,
   "families": {
    "padus": 331,
    "sgneb": 240,
    "sgnec": 152
   },
   "family_fold": 392,
   "family_used": "padus",
   "key_union": 168,
   "parts": 0,
   "records": 5,
   "summed": 331,
   "tracts": 4
  },
  "family_fold": "layers {'sgneb': 240, 'padus': 331, 'sgnec': 152}: one land in 3 layers, the padus copy used (392 ac of copies not added)",
  "manager": "",
  "note": "5 joined records = 4 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 875 -> 723 acres",
  "pieces": [
   [
    216055,
    "Mormon Island State Recreation Area",
    166,
    "name"
   ],
   [
    216391,
    "Mormon Island State Recreation Area",
    165,
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
 "t": "State Recreation Area",
 "verdict": "no size on page"
}
```

## US-4578 Pony Express National Historic Trail
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Pony Express National Historic Trail",
 "note": "whole park compared (POTA lists it in 0 states: {})",
 "official": null,
 "ours": {
  "acres": 0,
  "acres_by_state": {},
  "manager": "",
  "pieces": [],
  "pin": "inside",
  "src": "",
  "states": [
   "US-CA",
   "US-CO",
   "US-UT",
   "US-NV",
   "US-NE",
   "US-MO",
   "US-KS",
   "US-WY"
  ],
  "unknown_pieces": 1,
  "whole_park": true
 },
 "owner_now": null,
 "pct": null,
 "score": 4,
 "t": "National Historic Trail",
 "verdict": "ours unknown"
}
```

## US-9365 Rock Creek State Recreation Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Rock Creek State Recreation Area",
 "official": null,
 "ours": {
  "acres": 104,
  "dissolved": {
   "after": 203,
   "before": 307,
   "copies": 1,
   "families": {
    "padus": 99,
    "sgneb": 104
   },
   "family_fold": 99,
   "family_used": "sgneb",
   "parts": 0,
   "records": 3,
   "tracts": 2
  },
  "family_fold": "layers {'sgneb': 104, 'padus': 99}: one land in 2 layers, the sgneb copy used (99 ac of copies not added)",
  "manager": "",
  "note": "3 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 307 -> 203 acres",
  "pieces": [
   [
    "sgneb262",
    "Rock Creek Lake SRA",
    104,
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
 "t": "State Recreation Area",
 "verdict": "no size on page"
}
```

## US-9357 Blue River State Recreation Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Blue River State Recreation Area",
 "official": null,
 "ours": {
  "acres": 19,
  "dissolved": {
   "after": 46,
   "before": 74,
   "copies": 2,
   "families": {
    "padus": 32,
    "sgneb": 14
   },
   "family_fold": 14,
   "family_used": "padus",
   "key_union": 19,
   "parts": 0,
   "records": 5,
   "summed": 32,
   "tracts": 3
  },
  "family_fold": "layers {'padus': 32, 'sgneb': 14}: one land in 2 layers, the padus copy used (14 ac of copies not added)",
  "manager": "",
  "note": "5 joined records = 3 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 74 -> 46 acres",
  "pieces": [
   [
    216038,
    "Blue River State Recreation Area",
    16,
    "name"
   ],
   [
    216374,
    "Blue River State Recreation Area",
    16,
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
 "t": "State Recreation Area",
 "verdict": "no size on page"
}
```

## US-3490 Smith Lagoon National Waterfowl Production Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Smith Lagoon National Waterfowl Production Area",
 "official": null,
 "ours": {
  "acres": 7011,
  "manager": "",
  "pieces": [
   [
    4664,
    "Clay County Waterfowl Production Area Of Ne",
    7011,
    "reviewed-approx"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 4,
 "t": "National Waterfowl Production Area",
 "verdict": "no size on page"
}
```

## US-9363 Medicine Creek State Recreation Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Medicine Creek State Recreation Area",
 "official": null,
 "ours": {
  "acres": 518,
  "dissolved": {
   "after": 1465,
   "before": 2472,
   "copies": 1,
   "families": {
    "sgneb": 458,
    "sgnec": 1007
   },
   "family_fold": 458,
   "family_used": "sgnec",
   "key_union": 518,
   "parts": 0,
   "records": 3,
   "summed": 1007,
   "tracts": 2
  },
  "family_fold": "layers {'sgnec': 1007, 'sgneb': 458}: one land in 2 layers, the sgnec copy used (458 ac of copies not added)",
  "manager": "",
  "note": "3 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 2472 -> 1465 acres",
  "pieces": [
   [
    "sgnec34",
    "Medicine Creek SRA",
    1007,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "State Recreation Area",
 "verdict": "no size on page"
}
```

## US-13434 Wildcat Hills Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Wildcat Hills Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 901,
  "dissolved": {
   "after": 1266,
   "before": 1977,
   "copies": 1,
   "families": {
    "padus": 365,
    "sgneb": 901
   },
   "family_fold": 365,
   "family_used": "sgneb",
   "parts": 0,
   "records": 6,
   "tracts": 5
  },
  "family_fold": "layers {'sgneb': 901, 'padus': 365}: one land in 2 layers, the sgneb copy used (365 ac of copies not added)",
  "manager": "",
  "note": "6 joined records = 5 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1977 -> 1266 acres",
  "pieces": [
   [
    "sgneb350",
    "Wildcat HIlls SRA",
    711,
    "name"
   ],
   [
    "sgneb335",
    "Wildcat Hills WMA",
    190,
    "reviewed"
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

## US-9367 Rockford Lake State Recreation Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Rockford Lake State Recreation Area",
 "official": null,
 "ours": {
  "acres": 436,
  "dissolved": {
   "after": 857,
   "before": 2150,
   "copies": 3,
   "families": {
    "padus": 421,
    "sgneb": 436
   },
   "family_fold": 421,
   "family_used": "sgneb",
   "parts": 0,
   "records": 5,
   "tracts": 2
  },
  "family_fold": "layers {'sgneb': 436, 'padus': 421}: one land in 2 layers, the sgneb copy used (421 ac of copies not added)",
  "manager": "",
  "note": "5 joined records = 2 tracts: 3 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 2150 -> 857 acres",
  "pieces": [
   [
    "sgneb266",
    "Rockford Lake SRA",
    436,
    "reviewed"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "State Recreation Area",
 "verdict": "no size on page"
}
```
