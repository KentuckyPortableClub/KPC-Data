# park truth checker: US-RI random sample of 12 (2026-11-01; seed = date + area, same rows for everyone)

Source file: `data/truth/US-RI.json`

## US-2873 Fishermen's Memorial State Park
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Fishermen's Memorial State Park",
 "official": null,
 "ours": {
  "acres": 170,
  "dissolved": {
   "after": 147,
   "before": 281,
   "copies": 2,
   "families": {
    "padus": 80,
    "sgria": 67
   },
   "family_fold": 67,
   "family_used": "padus",
   "key_union": 170,
   "parts": 0,
   "records": 4,
   "summed": 80,
   "tracts": 2
  },
  "family_fold": "layers {'padus': 80, 'sgria': 67}: one land in 2 layers, the padus copy used (67 ac of copies not added)",
  "manager": "",
  "note": "4 joined records = 2 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 281 -> 147 acres",
  "pieces": [
   [
    57170,
    "Fisherman's",
    80,
    "reviewed"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 4,
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-2874 Fort Adams State Park
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Fort Adams State Park",
 "official": null,
 "ours": {
  "acres": 11,
  "manager": "",
  "pieces": [
   [
    57171,
    "Fort Adams",
    11,
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
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-6979 Arcadia Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Arcadia Management Area",
 "official": null,
 "ours": {
  "acres": 13564,
  "dissolved": {
   "after": 8501,
   "before": 16434,
   "copies": 0,
   "key_union": 13564,
   "parts": 23,
   "records": 29,
   "summed": 8501,
   "tracts": 6
  },
  "manager": "",
  "note": "29 joined records = 6 tracts: 0 copies of a tract (same acres, another layer) and 23 fee tracts under a designation record folded; summed 16434 -> 8501 acres",
  "pieces": [
   [
    57227,
    "Arcadia Management Area",
    4809,
    "name"
   ],
   [
    52077,
    "Arcadia Management Area",
    2278,
    "name"
   ],
   [
    57234,
    "Arcadia Management Area",
    1209,
    "name"
   ],
   [
    57235,
    "Arcadia Management Area",
    137,
    "name"
   ],
   [
    57134,
    "Arcadia Management Area",
    40,
    "name"
   ],
   [
    57228,
    "Arcadia Management Area",
    28,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 5,
 "t": "Management Area",
 "verdict": "no size on page"
}
```

## US-0516 Sachuest Point National Wildlife Refuge
```json
{
 "checked": "2026-11-01",
 "handover": [
  {
   "date_hint": null,
   "kind": "managed by",
   "line": "oint National Wildlife Refuge! This refuge is one of five National Wildlife Refuges in Rhode Island managed by the U.S. Fish and Wildlife Service. There are over 570 National Wildlife Refuges in the United States and its territories, and our mission",
   "owner_now": "U.S",
   "src": "https://www.fws.gov/refuge/sachuest-point/about-us",
   "why": "about / history page of the park's site"
  }
 ],
 "n": "Sachuest Point National Wildlife Refuge",
 "official": {
  "acres": 242.0,
  "as": "242 acre",
  "clean": false,
  "line": "In 1970, a land donation from the Audubon Society of Rhode Island and land transfers from the Navy led to the 242 acre refuge that you see today, which serves as an important stopover and wintering area for migratory birds. Othe",
  "read": "2026-11-01",
  "sent": "In 1970, a land donation from the Audubon Society of Rhode Island and land transfers from the Navy led to the 242 acre refuge that you see today, which serves as an important stopover and wintering area for migratory birds.",
  "url": "https://www.fws.gov/refuge/sachuest-point/about-us",
  "why": "history"
 },
 "ours": {
  "acres": 237,
  "manager": "",
  "pieces": [
   [
    4286,
    "Sachuest Point National Wildlife Refuge",
    244,
    "name"
   ],
   [
    5243,
    "Sachuest Point National Wildlife Refuge",
    244,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": "U.S",
 "pct": 2,
 "same_agency": false,
 "score": 8,
 "t": "National Wildlife Refuge",
 "verdict": "agree"
}
```

## US-7722 Scarborough North State Beach
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Scarborough North State Beach",
 "official": null,
 "ours": {
  "acres": 8,
  "manager": "",
  "pieces": [
   [
    57199,
    "Scarborough State Beach",
    8,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 3,
 "t": "State Beach",
 "verdict": "no size on page"
}
```

## US-7721 Salty Brine State Beach
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Salty Brine State Beach",
 "official": null,
 "ours": {
  "acres": 0,
  "manager": "",
  "pieces": [],
  "pin": "just outside",
  "src": "",
  "unknown_pieces": 3
 },
 "owner_now": null,
 "pct": null,
 "score": 5,
 "t": "State Beach",
 "verdict": "ours unknown"
}
```

## US-6988 Grills State Preserve
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Grills State Preserve",
 "official": null,
 "ours": {
  "acres": 387,
  "dissolved": {
   "after": 724,
   "before": 2158,
   "copies": 4,
   "key_union": 387,
   "parts": 0,
   "records": 7,
   "summed": 724,
   "tracts": 3
  },
  "manager": "",
  "note": "7 joined records = 3 tracts: 4 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 2158 -> 724 acres",
  "pieces": [
   [
    "sgria437",
    "Bradford Dye / Grills Preserve",
    505,
    "words"
   ],
   [
    "sgria33784",
    "Grills Preserve",
    212,
    "name"
   ],
   [
    "sgrib558",
    "Grills",
    7,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 2
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "State Preserve",
 "verdict": "no size on page"
}
```

## US-7714 Buck Hill Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Buck Hill Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 1585,
  "dissolved": {
   "after": 2374,
   "before": 2492,
   "copies": 4,
   "key_union": 1585,
   "parts": 0,
   "records": 10,
   "summed": 2374,
   "tracts": 6
  },
  "manager": "",
  "note": "10 joined records = 6 tracts: 4 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 2492 -> 2374 acres",
  "pieces": [
   [
    57269,
    "Buck Hill Management Area",
    1305,
    "name"
   ],
   [
    57270,
    "Buck Hill Management Area",
    731,
    "name"
   ],
   [
    9329,
    "Buck Hill Management Area",
    259,
    "name"
   ],
   [
    "sgria8587",
    "Buck Hill",
    47,
    "name"
   ],
   [
    57105,
    "Buck Hill Management Area - Perry",
    20,
    "name"
   ],
   [
    "sgria9174",
    "Buck Hill",
    12,
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

## US-2879 Rocky Point State Park
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Rocky Point State Park",
 "official": null,
 "ours": {
  "acres": 88,
  "dissolved": {
   "after": 127,
   "before": 461,
   "copies": 5,
   "families": {
    "padus": 80,
    "sgria": 47
   },
   "family_fold": 47,
   "family_used": "padus",
   "key_union": 88,
   "parts": 0,
   "records": 7,
   "summed": 80,
   "tracts": 2
  },
  "family_fold": "layers {'padus': 80, 'sgria': 47}: one land in 2 layers, the padus copy used (47 ac of copies not added)",
  "manager": "",
  "note": "7 joined records = 2 tracts: 5 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 461 -> 127 acres",
  "pieces": [
   [
    57193,
    "Rocky Point",
    80,
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
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-7865 East State Beach
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "East State Beach",
 "official": null,
 "ours": {
  "acres": 150,
  "dissolved": {
   "after": 377,
   "before": 843,
   "copies": 4,
   "families": {
    "padus": 243,
    "sgria": 134
   },
   "family_fold": 134,
   "family_used": "padus",
   "key_union": 150,
   "parts": 2,
   "records": 10,
   "summed": 243,
   "tracts": 4
  },
  "family_fold": "layers {'padus': 243, 'sgria': 134}: one land in 2 layers, the padus copy used (134 ac of copies not added)",
  "manager": "",
  "note": "10 joined records = 4 tracts: 4 copies of a tract (same acres, another layer) and 2 fee tracts under a designation record folded; summed 843 -> 377 acres",
  "pieces": [
   [
    57165,
    "East Beach",
    160,
    "name (designation code ignored)"
   ],
   [
    57166,
    "East Beach",
    68,
    "name (designation code ignored)"
   ],
   [
    57167,
    "East Beach",
    15,
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
 "t": "State Beach",
 "verdict": "no size on page"
}
```

## US-2878 Lincoln Woods State Park
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Lincoln Woods State Park",
 "official": null,
 "ours": {
  "acres": 538,
  "dissolved": {
   "after": 654,
   "before": 1898,
   "copies": 4,
   "families": {
    "padus": 32,
    "sgria": 622
   },
   "family_fold": 32,
   "family_used": "sgria",
   "key_union": 538,
   "parts": 0,
   "records": 9,
   "summed": 622,
   "tracts": 5
  },
  "family_fold": "layers {'sgria': 622, 'padus': 32}: one land in 2 layers, the sgria copy used (32 ac of copies not added)",
  "manager": "",
  "note": "9 joined records = 5 tracts: 4 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1898 -> 654 acres",
  "pieces": [
   [
    "sgria53",
    "Lincoln Woods State Park",
    598,
    "name"
   ],
   [
    "sgria883",
    "Lincoln Woods State Park",
    24,
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
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-10543 Patriots Park State Historic Site
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Patriots Park State Historic Site",
 "official": null,
 "ours": {
  "acres": 1,
  "dissolved": {
   "after": 1,
   "before": 3,
   "copies": 2,
   "parts": 0,
   "records": 3,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 3 -> 1 acres",
  "pieces": [
   [
    "sgria869",
    "Patriot Park",
    1,
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
 "t": "State Historic Site",
 "verdict": "no size on page"
}
```
