# park truth checker: US-LA random sample of 12 (2026-11-01; seed = date + area, same rows for everyone)

Source file: `data/truth/US-LA.json`

## US-0306 Catahoula National Wildlife Refuge
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-11-01",
 "handover": [],
 "n": "Catahoula National Wildlife Refuge",
 "official": null,
 "ours": {
  "acres": 60775,
  "dissolved": {
   "after": 63051,
   "before": 88289,
   "copies": 1,
   "families": {
    "fsod": 37813,
    "padus": 25238
   },
   "family_fold": 25238,
   "family_used": "fsod",
   "key_union": 60775,
   "parts": 0,
   "records": 3,
   "summed": 37813,
   "tracts": 2
  },
  "family_fold": "layers {'fsod': 37813, 'padus': 25238}: one land in 2 layers, the fsod copy used (25,238 ac of copies not added)",
  "manager": "",
  "note": "3 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 88289 -> 63051 acres",
  "pieces": [
   [
    "fsod88",
    "Catahoula National Wildlife Refuge",
    37813,
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
 "t": "National Wildlife Refuge",
 "verdict": "unsure"
}
```

## US-4059 Grassy Lake Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Grassy Lake Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 13246,
  "dissolved": {
   "after": 13246,
   "before": 52680,
   "copies": 3,
   "parts": 0,
   "records": 4,
   "tracts": 1
  },
  "manager": "",
  "note": "4 joined records = 1 tracts: 3 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 52680 -> 13246 acres",
  "pieces": [
   [
    "sglaa22",
    "Grassy Lake WMA",
    13246,
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

## US-4073 Pointe-aux-Chenes Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Pointe-aux-Chenes Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 35730,
  "dissolved": {
   "after": 69218,
   "before": 139800,
   "copies": 2,
   "families": {
    "sglab": 33488,
    "sglac": 35730
   },
   "family_fold": 33488,
   "family_used": "sglac",
   "parts": 0,
   "records": 4,
   "tracts": 2
  },
  "family_fold": "layers {'sglac': 35730, 'sglab': 33488}: one land in 2 layers, the sglac copy used (33,488 ac of copies not added)",
  "manager": "",
  "note": "4 joined records = 2 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 139800 -> 69218 acres",
  "pieces": [
   [
    "sglac57",
    "Pointe aux Chenes WMA",
    35730,
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

## US-6445 St. Tammany Wildlife Refuge
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "St. Tammany Wildlife Refuge",
 "official": null,
 "ours": {
  "acres": 1082,
  "dissolved": {
   "after": 2301,
   "before": 4283,
   "copies": 2,
   "families": {
    "lar": 1310,
    "law": 991
   },
   "family_fold": 991,
   "family_used": "lar",
   "key_union": 1082,
   "parts": 0,
   "records": 4,
   "summed": 1310,
   "tracts": 2
  },
  "family_fold": "layers {'lar': 1310, 'law': 991}: one land in 2 layers, the lar copy used (991 ac of copies not added)",
  "manager": "",
  "note": "4 joined records = 2 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 4283 -> 2301 acres",
  "pieces": [
   [
    "lar5",
    "St Tammany Wildlife Refuge",
    1310,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 5,
 "t": "Wildlife Refuge",
 "verdict": "no size on page"
}
```

## US-0723 Vicksburg National Military Park
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Vicksburg National Military Park",
 "note": "whole park compared (POTA lists it in 2 states: {'US-LA': 3, 'US-MS': 2441})",
 "official": null,
 "ours": {
  "acres": 2444,
  "acres_by_state": {
   "US-LA": 3,
   "US-MS": 2441
  },
  "manager": "",
  "pieces": [
   [
    3292,
    "Vicksburg National Military Park",
    3,
    "name"
   ]
  ],
  "pin": "well outside",
  "src": "USGS PAD-US",
  "states": [
   "US-LA",
   "US-MS"
  ],
  "unknown_pieces": 0,
  "whole_park": true
 },
 "owner_now": null,
 "pct": null,
 "score": 4,
 "t": "National Military Park",
 "verdict": "no size on page"
}
```

## US-10563 Fort Johnson-Vernon Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Fort Johnson-Vernon Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 105885,
  "manager": "",
  "pieces": [
   [
    "sglac21",
    "Fort Johnson-Vernon WMA",
    105885,
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
 "t": "Wildlife Management Area",
 "verdict": "no size on page"
}
```

## US-10454 Rebel State Historic Site
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Rebel State Historic Site",
 "official": null,
 "ours": {
  "acres": 12,
  "manager": "",
  "pieces": [
   [
    203103,
    "Rebel State Historic Site",
    12,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 5,
 "t": "State Historic Site",
 "verdict": "no size on page"
}
```

## US-4080 Timken Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Timken Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 3053,
  "dissolved": {
   "after": 2867,
   "before": 11468,
   "copies": 3,
   "key_union": 3053,
   "parts": 0,
   "records": 4,
   "summed": 2867,
   "tracts": 1
  },
  "manager": "",
  "note": "4 joined records = 1 tracts: 3 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 11468 -> 2867 acres",
  "pieces": [
   [
    "law51",
    "Timken WMA",
    2867,
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
 "t": "Wildlife Management Area",
 "verdict": "no size on page"
}
```

## US-4061 J. C. 'Sonny' Gilbert Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "J. C. 'Sonny' Gilbert Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 7524,
  "dissolved": {
   "after": 7524,
   "before": 30042,
   "copies": 3,
   "parts": 0,
   "records": 4,
   "tracts": 1
  },
  "manager": "",
  "note": "4 joined records = 1 tracts: 3 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 30042 -> 7524 acres",
  "pieces": [
   [
    "sglab22",
    "J. C. “Sonny” Gilbert",
    7524,
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
 "t": "Wildlife Management Area",
 "verdict": "no size on page"
}
```

## US-4486 Kisatchie National Forest
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Kisatchie National Forest",
 "official": {
  "acres": 604000.0,
  "as": "604,000 acres",
  "clean": false,
  "line": "rest Current Fire Information Kisatchie National Forest Come visit Louisiana's ONLY national forest with over 604,000 acres to explore! T T T Welcome to Kisatchie National Forest Located in seven parishes in central and northern Loui",
  "read": "2026-11-01",
  "sent": "Come visit Louisiana's ONLY national forest with over 604,000 acres to explore!",
  "url": "https://www.fs.usda.gov/kisatchie",
  "why": "total-looking"
 },
 "ours": {
  "acres": 608487,
  "manager": "",
  "pieces": [
   [
    2987,
    "Kisatchie National Forest",
    607492,
    "name"
   ],
   [
    2944,
    "Bayou Beouf Purchase Unit",
    995,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 1,
 "same_agency": false,
 "score": 7,
 "t": "National Forest",
 "verdict": "agree"
}
```

## US-4052 Boeuf Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Boeuf Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 52237,
  "dissolved": {
   "after": 103347,
   "before": 207765,
   "copies": 2,
   "families": {
    "padus": 52237,
    "sglab": 51110
   },
   "family_fold": 51110,
   "family_used": "padus",
   "parts": 0,
   "records": 4,
   "tracts": 2
  },
  "family_fold": "layers {'padus': 52237, 'sglab': 51110}: one land in 2 layers, the padus copy used (51,110 ac of copies not added)",
  "manager": "",
  "note": "4 joined records = 2 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 207765 -> 103347 acres",
  "pieces": [
   [
    203036,
    "Boeuf Wildlife Management Area",
    52237,
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

## US-10353 Isle Dernieres Barrier Islands Wildlife Refuge
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Isle Dernieres Barrier Islands Wildlife Refuge",
 "official": null,
 "ours": {
  "acres": 1977,
  "manager": "",
  "pieces": [
   [
    203071,
    "Isles Dernieres Barrier Islands Refuge",
    1745,
    "name"
   ],
   [
    203072,
    "Isles Dernieres Barrier Islands Refuge",
    932,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 4,
 "t": "Wildlife Refuge",
 "verdict": "no size on page"
}
```
