# park truth checker: US-OR random sample of 12 (2026-11-09; seed = date + area, same rows for everyone)

Source file: `data/truth/US-OR.json`

## US-9523 Agate Beach State Recreation Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Agate Beach State Recreation Area",
 "official": null,
 "ours": {
  "acres": 15,
  "dissolved": {
   "after": 51,
   "before": 129,
   "copies": 3,
   "families": {
    "padus": 26,
    "sgord": 25
   },
   "family_fold": 25,
   "family_used": "padus",
   "key_union": 15,
   "parts": 0,
   "records": 5,
   "summed": 26,
   "tracts": 2
  },
  "family_fold": "layers {'padus': 26, 'sgord': 25}: one land in 2 layers, the padus copy used (25 ac of copies not added)",
  "manager": "",
  "note": "5 joined records = 2 tracts: 3 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 129 -> 51 acres",
  "pieces": [
   [
    241482,
    "Agate Beach State Recreation Site",
    26,
    "words"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 3
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "State Recreation Area",
 "verdict": "no size on page"
}
```

## US-12473 Scaredman BLM Recreation Management Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Scaredman BLM Recreation Management Area",
 "official": null,
 "ours": {
  "acres": 11,
  "dissolved": {
   "after": 23,
   "before": 69,
   "copies": 4,
   "families": {
    "rma": 13,
    "rst": 10
   },
   "family_fold": 10,
   "family_used": "rma",
   "key_union": 11,
   "parts": 0,
   "records": 6,
   "summed": 13,
   "tracts": 2
  },
  "family_fold": "layers {'rma': 13, 'rst': 10}: one land in 2 layers, the rma copy used (10 ac of copies not added)",
  "manager": "",
  "note": "6 joined records = 2 tracts: 4 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 69 -> 23 acres",
  "pieces": [
   [
    "rma11220",
    "Scaredman Recreation Site",
    13,
    "words"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "BLM Recreation Management Area",
 "verdict": "no size on page"
}
```

## US-2822 Catherine Creek State Park
```json
{
 "checked": "2026-11-09",
 "handover": [
  {
   "date_hint": null,
   "kind": "transfer",
   "line": "E. S. Collins, a prominent Portland lumber man, it was known as Collins Park. In 1932, Mr. Collins deeded the tract to Union County for park purposes. Partly due to problems in maintenance funding, the county deeded the land to the state. The area was developed for day use and primitive camping in t",
   "owner_now": "Union County for",
   "src": "https://stateparks.oregon.gov/index.cfm?do=park.profile&parkId=11",
   "why": "the park's page (data/parkinfo)"
  }
 ],
 "n": "Catherine Creek State Park",
 "official": null,
 "ours": {
  "acres": 161,
  "dissolved": {
   "after": 314,
   "before": 794,
   "copies": 3,
   "families": {
    "osp": 161,
    "sgord": 153
   },
   "family_fold": 153,
   "family_used": "osp",
   "parts": 0,
   "records": 5,
   "tracts": 2
  },
  "family_fold": "layers {'osp': 161, 'sgord': 153}: one land in 2 layers, the osp copy used (153 ac of copies not added)",
  "manager": "",
  "note": "5 joined records = 2 tracts: 3 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 794 -> 314 acres",
  "pieces": [
   [
    "osp214",
    "Catherine Creek",
    161,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": "Union County for",
 "pct": null,
 "score": 7,
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-2843 Milo McIver State Park
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Milo McIver State Park",
 "official": null,
 "ours": {
  "acres": 1080,
  "dissolved": {
   "after": 1519,
   "before": 4895,
   "copies": 3,
   "families": {
    "padus": 977,
    "sgord": 542
   },
   "family_fold": 542,
   "family_used": "padus",
   "key_union": 1080,
   "parts": 6,
   "records": 15,
   "summed": 977,
   "tracts": 6
  },
  "family_fold": "layers {'padus': 977, 'sgord': 542}: one land in 2 layers, the padus copy used (542 ac of copies not added)",
  "manager": "",
  "note": "15 joined records = 6 tracts: 3 copies of a tract (same acres, another layer) and 6 fee tracts under a designation record folded; summed 4895 -> 1519 acres",
  "pieces": [
   [
    241365,
    "Milo McIver State Park",
    977,
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
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-10494 Millpond BLM Recreation Management Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Millpond BLM Recreation Management Area",
 "official": null,
 "ours": {
  "acres": 28,
  "dissolved": {
   "after": 31,
   "before": 93,
   "copies": 2,
   "key_union": 28,
   "parts": 0,
   "records": 3,
   "summed": 31,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 93 -> 31 acres",
  "pieces": [
   [
    "rma11269",
    "Millpond Recreation Site",
    31,
    "words"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "BLM Recreation Management Area",
 "verdict": "no size on page"
}
```

## US-9999 Coyote Springs State Fish and Wildlife Area
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-11-09",
 "handover": [],
 "n": "Coyote Springs State Fish and Wildlife Area",
 "official": null,
 "ours": {
  "acres": 117,
  "dissolved": {
   "after": 171,
   "before": 342,
   "copies": 1,
   "key_union": 117,
   "parts": 0,
   "records": 2,
   "summed": 171,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 342 -> 171 acres",
  "pieces": [
   [
    241318,
    "Coyote Springs Wildlife Area",
    171,
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
 "t": "State Fish and Wildlife Area",
 "verdict": "unsure"
}
```

## US-10479 Oasis BLM Recreation Management Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Oasis BLM Recreation Management Area",
 "official": null,
 "ours": {
  "acres": 2,
  "dissolved": {
   "after": 3,
   "before": 6,
   "copies": 1,
   "key_union": 2,
   "parts": 0,
   "records": 2,
   "summed": 3,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 6 -> 3 acres",
  "pieces": [
   [
    "rma11297",
    "Oasis Campground",
    3,
    "reviewed-approx"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "BLM Recreation Management Area",
 "verdict": "no size on page"
}
```

## US-7361 Hells Canyon National Recreation Area
```json
{
 "cause": "whole park compared (POTA lists it in 2 states: {'US-ID': 661553, 'US-OR': 661553})",
 "checked": "2026-11-09",
 "handover": [],
 "n": "Hells Canyon National Recreation Area",
 "note": "whole park compared (POTA lists it in 2 states: {'US-ID': 661553, 'US-OR': 661553})",
 "official": null,
 "ours": {
  "acres": 1323106,
  "acres_by_state": {
   "US-ID": 661553,
   "US-OR": 661553
  },
  "manager": "",
  "pieces": [
   [
    "fsod52",
    "Hells Canyon National Recreation Area",
    661553,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "",
  "states": [
   "US-ID",
   "US-OR"
  ],
  "unknown_pieces": 0,
  "whole_park": true
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "National Recreation Area",
 "verdict": "unsure"
}
```

## US-9533 Clay Myers State Natural Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Clay Myers State Natural Area",
 "official": null,
 "ours": {
  "acres": 155,
  "dissolved": {
   "after": 527,
   "before": 859,
   "copies": 2,
   "families": {
    "osp": 166,
    "padus": 182,
    "sgord": 179
   },
   "family_fold": 345,
   "family_used": "padus",
   "key_union": 155,
   "parts": 0,
   "records": 7,
   "summed": 182,
   "tracts": 5
  },
  "family_fold": "layers {'padus': 182, 'osp': 166, 'sgord': 179}: one land in 3 layers, the padus copy used (345 ac of copies not added)",
  "manager": "",
  "note": "7 joined records = 5 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 859 -> 527 acres",
  "pieces": [
   [
    241388,
    "Clay Myers State Natural Area",
    182,
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

## US-10358 Shotgun Creek BLM Recreation Management Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Shotgun Creek BLM Recreation Management Area",
 "official": null,
 "ours": {
  "acres": 212,
  "dissolved": {
   "after": 308,
   "before": 896,
   "copies": 4,
   "families": {
    "rma": 278,
    "rst": 30
   },
   "family_fold": 30,
   "family_used": "rma",
   "key_union": 212,
   "parts": 0,
   "records": 9,
   "summed": 278,
   "tracts": 5
  },
  "family_fold": "layers {'rma': 278, 'rst': 30}: one land in 2 layers, the rma copy used (30 ac of copies not added)",
  "manager": "",
  "note": "9 joined records = 5 tracts: 4 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 896 -> 308 acres",
  "pieces": [
   [
    "rma11349",
    "Shotgun Creek Recreation Site",
    278,
    "words"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "BLM Recreation Management Area",
 "verdict": "no size on page"
}
```

## US-9530 Benson State Recreation Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Benson State Recreation Area",
 "official": null,
 "ours": {
  "acres": 270,
  "dissolved": {
   "after": 498,
   "before": 1440,
   "copies": 3,
   "families": {
    "padus": 314,
    "sgord": 184
   },
   "family_fold": 184,
   "family_used": "padus",
   "key_union": 270,
   "parts": 0,
   "records": 6,
   "summed": 314,
   "tracts": 3
  },
  "family_fold": "layers {'padus': 314, 'sgord': 184}: one land in 2 layers, the padus copy used (184 ac of copies not added)",
  "manager": "",
  "note": "6 joined records = 3 tracts: 3 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1440 -> 498 acres",
  "pieces": [
   [
    241458,
    "Benson State Recreation Area",
    314,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 5
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "State Recreation Area",
 "verdict": "no size on page"
}
```

## US-9529 Beachside State Recreation Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Beachside State Recreation Area",
 "official": null,
 "ours": {
  "acres": 31,
  "dissolved": {
   "after": 65,
   "before": 163,
   "copies": 3,
   "families": {
    "osp": 33,
    "sgord": 32
   },
   "family_fold": 32,
   "family_used": "osp",
   "key_union": 31,
   "parts": 0,
   "records": 5,
   "summed": 33,
   "tracts": 2
  },
  "family_fold": "layers {'osp': 33, 'sgord': 32}: one land in 2 layers, the osp copy used (32 ac of copies not added)",
  "manager": "",
  "note": "5 joined records = 2 tracts: 3 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 163 -> 65 acres",
  "pieces": [
   [
    "osp74",
    "Beachside",
    33,
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
 "t": "State Recreation Area",
 "verdict": "no size on page"
}
```
