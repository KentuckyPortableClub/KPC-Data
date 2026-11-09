# park truth checker: US-RI random sample of 12 (2026-11-09; seed = date + area, same rows for everyone)

Source file: `data/truth/US-RI.json`

## US-6982 Big River Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-09",
 "n": "Big River Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 8380,
  "dissolved": {
   "after": 8380,
   "before": 25140,
   "copies": 2,
   "parts": 0,
   "records": 3,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 25140 -> 8380 acres",
  "pieces": [
   [
    "sgria10848",
    "Big River",
    8380,
    "reviewed"
   ]
  ],
  "pin": "inside",
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

## US-2878 Lincoln Woods State Park
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-09",
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

## US-7508 Pulaski State Park
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 13 acre, no total words near it)",
 "checked": "2026-11-09",
 "handover": [],
 "n": "Pulaski State Park",
 "official": {
  "acres": 13.0,
  "as": "13 acre",
  "clean": false,
  "line": ". From the first class trout fishing in the spring, to enjoying a picnic, a short hike, or a cool swim in the 13 acre Peck Pond in the summer, to cross-country skiing on the 10 miles of groomed trails into the adjacent George W",
  "read": "2026-11-09",
  "sent": "From the first class trout fishing in the spring, to enjoying a picnic, a short hike, or a cool swim in the 13 acre Peck Pond in the summer, to cross-country skiing on the 10 miles of groomed trails into the adjacent George Washington Management area in the winter, Pulaski provides year round enjoym",
  "url": "https://riparks.ri.gov/parks/pulaski-state-park",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 160,
  "dissolved": {
   "after": 343,
   "before": 1029,
   "copies": 2,
   "key_union": 160,
   "parts": 0,
   "records": 3,
   "summed": 343,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1029 -> 343 acres",
  "pieces": [
   [
    "sgria916",
    "Pulaski State Park",
    343,
    "reviewed"
   ]
  ],
  "pin": "just outside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 1131,
 "same_agency": false,
 "score": 6,
 "t": "State Park",
 "verdict": "unsure"
}
```

## US-2876 Goddard Memorial State Park
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-09",
 "n": "Goddard Memorial State Park",
 "official": null,
 "ours": {
  "acres": 268,
  "dissolved": {
   "after": 478,
   "before": 1434,
   "copies": 2,
   "key_union": 268,
   "parts": 0,
   "records": 3,
   "summed": 478,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1434 -> 478 acres",
  "pieces": [
   [
    "sgria94",
    "Goddard Park",
    478,
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
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-2875 Fort Wetherill State Park
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-09",
 "n": "Fort Wetherill State Park",
 "official": null,
 "ours": {
  "acres": 28,
  "dissolved": {
   "after": 61,
   "before": 183,
   "copies": 4,
   "key_union": 28,
   "parts": 0,
   "records": 6,
   "summed": 61,
   "tracts": 2
  },
  "manager": "",
  "note": "6 joined records = 2 tracts: 4 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 183 -> 61 acres",
  "pieces": [
   [
    "sgria567",
    "Fort Wetherill State Park",
    54,
    "name"
   ],
   [
    "sgria566",
    "Fort Wetherill State Park",
    7,
    "reviewed"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-10544 Jerimoth Hill State Recreation Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-09",
 "n": "Jerimoth Hill State Recreation Area",
 "official": null,
 "ours": {
  "acres": 8,
  "manager": "",
  "pieces": [
   [
    57110,
    "Jerimoth Hill - Brown U / Jerimoth Hill",
    6,
    "reviewed-approx"
   ],
   [
    57316,
    "Mosley/Jerimoth Hill",
    5,
    "reviewed-approx"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 4,
 "t": "State Recreation Area",
 "verdict": "no size on page"
}
```

## US-7716 Carolina Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-09",
 "n": "Carolina Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 1452,
  "manager": "",
  "pieces": [
   [
    57275,
    "Carolina Management Area",
    1454,
    "name"
   ],
   [
    57279,
    "Carolina Management Area",
    155,
    "name"
   ],
   [
    57277,
    "Carolina Management Area",
    145,
    "name"
   ],
   [
    57278,
    "Carolina Management Area",
    111,
    "name"
   ],
   [
    57276,
    "Carolina Management Area",
    103,
    "name"
   ],
   [
    57280,
    "Carolina Management Area",
    9,
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

## US-10548 Barber Pond State Recreation Area
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 38 acres, no total words near it)",
 "checked": "2026-11-09",
 "handover": [],
 "n": "Barber Pond State Recreation Area",
 "official": {
  "acres": 38.0,
  "as": "38 acres",
  "clean": false,
  "line": "t road, ramp is on the right. (A) Handicapped Accessible none Yes Cranston John L. Curran Public Fishing Area 38 acres. Fiskville Reservoir. Rt. 295 N to Scituate Ave., west to Seven Mile Rd. pond on left (S) State-owned & opera",
  "read": "2026-11-09",
  "sent": "Curran Public Fishing Area 38 acres.",
  "url": "https://dem.ri.gov/natural-resources-bureau/fish-wildlife/freshwater-fishing/public-boat-launching-sites#salt",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 1,
  "dissolved": {
   "after": 1,
   "before": 2,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 2 -> 1 acres",
  "pieces": [
   [
    "sgrib617",
    "Barbers Pond",
    1,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 97,
 "same_agency": false,
 "score": 5,
 "t": "State Recreation Area",
 "verdict": "unsure"
}
```

## US-6983 Woody Hill Wildlife Management Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Woody Hill Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 1082,
  "manager": "",
  "pieces": [
   [
    57387,
    "Woody Hill Management Area",
    722,
    "name"
   ],
   [
    154077,
    "Woody Hill",
    71,
    "name"
   ],
   [
    57388,
    "Woody Hill Management Area",
    13,
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

## US-0514 John H. Chafee National Wildlife Refuge
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-09",
 "handover": [],
 "n": "John H. Chafee National Wildlife Refuge",
 "official": {
  "acres": 550.0,
  "as": "550 acre",
  "clean": false,
  "line": "tory waterfowl that rely on it, including the largest population of black ducks in Rhode Island. In fact, the 550-acre refuge was established specifically to protect the population of black ducks that winter there. The refuge’s",
  "read": "2026-11-09",
  "sent": "In fact, the 550-acre refuge was established specifically to protect the population of black ducks that winter there.",
  "url": "https://www.fws.gov/refuge/john-h-chafee/about-us",
  "why": "total-looking"
 },
 "ours": {
  "acres": 334,
  "dissolved": {
   "after": 562,
   "before": 1124,
   "copies": 1,
   "key_union": 334,
   "parts": 0,
   "records": 2,
   "summed": 562,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1124 -> 562 acres",
  "pieces": [
   [
    3977,
    "John H. Chafee National Wildlife Refuge",
    562,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 39,
 "same_agency": false,
 "score": 6,
 "t": "National Wildlife Refuge",
 "verdict": "off"
}
```

## US-2870 Brenton Point State Park
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-09",
 "n": "Brenton Point State Park",
 "official": null,
 "ours": {
  "acres": 161,
  "dissolved": {
   "after": 223,
   "before": 347,
   "copies": 2,
   "families": {
    "padus": 161,
    "sgria": 62
   },
   "family_fold": 62,
   "family_used": "padus",
   "parts": 0,
   "records": 4,
   "tracts": 2
  },
  "family_fold": "layers {'padus': 161, 'sgria': 62}: one land in 2 layers, the padus copy used (62 ac of copies not added)",
  "manager": "",
  "note": "4 joined records = 2 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 347 -> 223 acres",
  "pieces": [
   [
    157804,
    "Brenton Point State Park",
    161,
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

## US-6986 Simmons Mill Wildlife Management Area
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-11-09",
 "handover": [],
 "n": "Simmons Mill Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 11,
  "manager": "",
  "pieces": [
   [
    57361,
    "Simmons Mill Management Area",
    34,
    "name"
   ],
   [
    57360,
    "Simmons Mill Management Area",
    7,
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
 "t": "Wildlife Management Area",
 "verdict": "unsure"
}
```
