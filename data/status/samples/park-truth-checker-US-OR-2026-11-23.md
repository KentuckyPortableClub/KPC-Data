# park truth checker: US-OR random sample of 12 (2026-11-23; seed = date + area, same rows for everyone)

Source file: `data/truth/US-OR.json`

## US-10736 Cold Springs HMA BLM Herd Management Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "last_read_failed": "2026-11-23",
 "n": "Cold Springs HMA BLM Herd Management Area",
 "official": {
  "acres": 29883.0,
  "as": "29,883 acres",
  "clean": true,
  "line": "s southwest of Harper, Oregon near Star Mountain. It is bordered on the west side by the Rooster Combs. Size: 29,883 acres Topography/Vegetation: Elevation in the HMA varies from 3000 to 4600 feet. Topography of the HMA varies from",
  "read": "2026-11-09",
  "sent": "Size: 29,883 acres",
  "url": "https://www.blm.gov/programs/wild-horse-and-burro/herd-management/herd-management-areas/oregon-washington/cold-springs",
  "why": "clean total"
 },
 "ours": {
  "acres": 29904,
  "manager": "",
  "pieces": [
   [
    "hma111",
    "Cold Springs",
    29904,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 0,
 "same_agency": false,
 "score": 8,
 "t": "BLM Herd Management Area",
 "verdict": "agree"
}
```

## US-10747 Sheepshead/Heath Creek BLM Herd Management Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "last_read_failed": "2026-11-23",
 "n": "Sheepshead/Heath Creek BLM Herd Management Area",
 "official": {
  "acres": 200000.0,
  "as": "200,000 acres",
  "clean": true,
  "line": "as part of the Barren Valley Complex along with Coyote Lake/Alvord-Tule Springs and Sand Springs HMAs. Size: 200,000 acres Topography/Vegetation: Elevation in the HMA varies from 3900 to 6300 feet. West and east portions of the HMA",
  "read": "2026-11-09",
  "sent": "Size: 200,000 acres",
  "url": "https://www.blm.gov/programs/wild-horse-and-burro/herd-management/herd-management-areas/oregon-washington/sheepshead-heath",
  "why": "clean total"
 },
 "ours": {
  "acres": 198966,
  "dissolved": {
   "after": 198966,
   "before": 397936,
   "copies": 0,
   "parts": 2,
   "records": 3,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 0 copies of a tract (same acres, another layer) and 2 fee tracts under a designation record folded; summed 397936 -> 198966 acres",
  "pieces": [
   [
    "hma73",
    "Sheepshead-Heath Creek",
    198966,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 1,
 "same_agency": false,
 "score": 8,
 "t": "BLM Herd Management Area",
 "verdict": "agree"
}
```

## US-10492 Provolt BLM Recreation Management Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "last_read_failed": "2026-11-23",
 "n": "Provolt BLM Recreation Management Area",
 "official": null,
 "ours": {
  "acres": 295,
  "dissolved": {
   "after": 382,
   "before": 556,
   "copies": 2,
   "families": {
    "rma": 87,
    "rst": 295
   },
   "family_fold": 87,
   "family_used": "rst",
   "parts": 0,
   "records": 6,
   "tracts": 4
  },
  "family_fold": "layers {'rst': 295, 'rma': 87}: one land in 2 layers, the rst copy used (87 ac of copies not added)",
  "manager": "",
  "note": "6 joined records = 4 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 556 -> 382 acres",
  "pieces": [
   [
    "rst13628",
    "Provolt Seed Orchard",
    155,
    "words"
   ],
   [
    "rst13599",
    "Provolt Seed Orchard",
    129,
    "words"
   ],
   [
    "rst13677",
    "Provolt Seed Orchard",
    11,
    "words"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 5,
 "t": "BLM Recreation Management Area",
 "verdict": "no size on page"
}
```

## US-13075 Bear Gulch BLM Wilderness Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "last_read_failed": "2026-11-23",
 "n": "Bear Gulch BLM Wilderness Area",
 "official": null,
 "ours": {
  "acres": 350,
  "manager": "",
  "pieces": [
   [
    "sgakh1841",
    "Bear Gulch",
    350,
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
 "t": "BLM Wilderness Area",
 "verdict": "no size on page"
}
```

## US-10390 Sandy State Fish Hatchery
```json
{
 "checked": "2026-11-23",
 "handover": [],
 "n": "Sandy State Fish Hatchery",
 "official": null,
 "ours": {
  "acres": 207,
  "manager": "",
  "pieces": [
   [
    "sgord1353",
    "Sandy Fish Hatchery",
    159,
    "name"
   ],
   [
    "sgord5004",
    "Sandy Fish Hatchery",
    38,
    "name"
   ],
   [
    "sgord5005",
    "Sandy Fish Hatchery",
    10,
    "reviewed"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "State Fish Hatchery",
 "verdict": "no size on page"
}
```

## US-10482 Riverside BLM Recreation Management Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "last_read_failed": "2026-11-23",
 "n": "Riverside BLM Recreation Management Area",
 "official": null,
 "ours": {
  "acres": 1340,
  "dissolved": {
   "after": 686,
   "before": 1422,
   "copies": 2,
   "key_union": 1340,
   "parts": 10,
   "records": 19,
   "summed": 686,
   "tracts": 7
  },
  "manager": "",
  "note": "19 joined records = 7 tracts: 2 copies of a tract (same acres, another layer) and 10 fee tracts under a designation record folded; summed 1422 -> 686 acres",
  "pieces": [
   [
    "sgord2661",
    "Riverside",
    298,
    "name"
   ],
   [
    "sgord6239",
    "Riverside",
    151,
    "name"
   ],
   [
    "sgord627",
    "Riverside",
    144,
    "name"
   ],
   [
    "sgord2516",
    "Riverside",
    42,
    "name"
   ],
   [
    "sgord4848",
    "Riverside",
    19,
    "name"
   ],
   [
    "sgord5948",
    "Riverside",
    19,
    "name"
   ],
   [
    "sgord4851",
    "Riverside",
    13,
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
 "t": "BLM Recreation Management Area",
 "verdict": "no size on page"
}
```

## US-12945 Coquille Valley State Fish and Wildlife Area
```json
{
 "checked": "2026-11-23",
 "handover": [],
 "n": "Coquille Valley State Fish and Wildlife Area",
 "official": null,
 "ours": {
  "acres": 656,
  "manager": "",
  "pieces": [
   [
    "sgorc60",
    "Coquille Valley",
    286,
    "name"
   ],
   [
    "sgorc61",
    "Coquille Valley",
    274,
    "name"
   ],
   [
    "sgorc473",
    "Coquille Valley",
    96,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "State Fish and Wildlife Area",
 "verdict": "no size on page"
}
```

## US-2811 Alfred A Loeb State Park
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-11-23",
 "handover": [],
 "n": "Alfred A Loeb State Park",
 "official": null,
 "ours": {
  "acres": 319,
  "dissolved": {
   "after": 593,
   "before": 1550,
   "copies": 3,
   "families": {
    "padus": 319,
    "sgord": 274
   },
   "family_fold": 274,
   "family_used": "padus",
   "parts": 0,
   "records": 7,
   "tracts": 4
  },
  "family_fold": "layers {'padus': 319, 'sgord': 274}: one land in 2 layers, the padus copy used (274 ac of copies not added)",
  "manager": "",
  "note": "7 joined records = 4 tracts: 3 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1550 -> 593 acres",
  "pieces": [
   [
    241340,
    "Alfred A. Loeb State Park",
    319,
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
 "verdict": "unsure"
}
```

## US-10472 Marmot BLM Recreation Management Area
```json
{
 "checked": "2026-11-23",
 "handover": [],
 "n": "Marmot BLM Recreation Management Area",
 "official": null,
 "ours": {
  "acres": 92,
  "dissolved": {
   "after": 106,
   "before": 318,
   "copies": 6,
   "families": {
    "rma": 14,
    "sgorf": 92
   },
   "family_fold": 14,
   "family_used": "sgorf",
   "parts": 0,
   "records": 9,
   "tracts": 3
  },
  "family_fold": "layers {'sgorf': 92, 'rma': 14}: one land in 2 layers, the sgorf copy used (14 ac of copies not added)",
  "manager": "",
  "note": "9 joined records = 3 tracts: 6 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 318 -> 106 acres",
  "pieces": [
   [
    "sgorf7049",
    "Marmot Recreation Site",
    59,
    "words"
   ],
   [
    "sgorf7044",
    "Marmot Recreation Site",
    33,
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

## US-10499 Lake Creek Falls BLM Recreation Management Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "last_read_failed": "2026-11-23",
 "n": "Lake Creek Falls BLM Recreation Management Area",
 "official": null,
 "ours": {
  "acres": 53,
  "dissolved": {
   "after": 112,
   "before": 228,
   "copies": 2,
   "families": {
    "rma": 58,
    "sgakh": 54
   },
   "family_fold": 54,
   "family_used": "rma",
   "key_union": 53,
   "parts": 0,
   "records": 4,
   "summed": 58,
   "tracts": 2
  },
  "family_fold": "layers {'rma': 58, 'sgakh': 54}: one land in 2 layers, the rma copy used (54 ac of copies not added)",
  "manager": "",
  "note": "4 joined records = 2 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 228 -> 112 acres",
  "pieces": [
   [
    "rma11244",
    "Lake Creek Falls",
    58,
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
 "t": "BLM Recreation Management Area",
 "verdict": "no size on page"
}
```

## US-12347 Grande Ronde National Wild and Scenic River
```json
{
 "checked": "2026-11-23",
 "handover": [],
 "n": "Grande Ronde National Wild and Scenic River",
 "official": null,
 "ours": {
  "acres": 28294,
  "family_fold": "layers {'sgakh': 16971, 'fwsr': 14404}: one land in 2 layers, the sgakh copy used (14,404 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgakh1878",
    "Grande Ronde",
    16971,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "National Wild and Scenic River",
 "verdict": "no size on page"
}
```

## US-9554 Hug Point State Recreation Area
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 1.3 acres, a tiny number without size wording)",
 "checked": "2026-11-23",
 "handover": [],
 "n": "Hug Point State Recreation Area",
 "official": {
  "acres": 1.3,
  "as": "1.3 acres",
  "clean": false,
  "line": "before Memorial Day weekend and Labor Day. For more questions, review our statewide FAQ History The original 1.3 acres of this tract were given to the state by Clatsop County in 1957. In 1968, land was purchased from Elizabeth J",
  "read": "2026-11-23",
  "sent": "The original 1.3 acres of this tract were given to the state by Clatsop County in 1957.",
  "url": "https://stateparks.oregon.gov/index.cfm?do=park.profile&parkId=137",
  "why": "a tiny number without size wording"
 },
 "ours": {
  "acres": 78,
  "dissolved": {
   "after": 100,
   "before": 216,
   "copies": 2,
   "families": {
    "sgorb": 58,
    "sgord": 42
   },
   "family_fold": 42,
   "family_used": "sgorb",
   "key_union": 78,
   "parts": 0,
   "records": 6,
   "summed": 58,
   "tracts": 4
  },
  "family_fold": "layers {'sgorb': 58, 'sgord': 42}: one land in 2 layers, the sgorb copy used (42 ac of copies not added)",
  "manager": "",
  "note": "6 joined records = 4 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 216 -> 100 acres",
  "pieces": [
   [
    "sgorb214",
    "Hug Point State Recreation Site",
    58,
    "words"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 3
 },
 "owner_now": null,
 "pct": 5900,
 "same_agency": false,
 "score": 7,
 "t": "State Recreation Area",
 "verdict": "unsure"
}
```
