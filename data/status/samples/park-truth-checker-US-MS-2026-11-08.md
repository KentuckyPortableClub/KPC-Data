# park truth checker: US-MS random sample of 12 (2026-11-08; seed = date + area, same rows for everyone)

Source file: `data/truth/US-MS.json`

## US-7095 John Bell Williams Wildlife Management Area
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-08",
 "n": "John Bell Williams Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 2467,
  "family_fold": "layers {'padus': 2654, 'mszw': 758}: one land in 2 layers, the padus copy used (758 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    211194,
    "John Bell Williams Wma",
    2654,
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
 "t": "Wildlife Management Area",
 "verdict": "no size on page"
}
```

## US-0384 Grand Bay National Wildlife Refuge
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Grand Bay National Wildlife Refuge",
 "note": "whole park compared (POTA lists it in 2 states: {'US-AL': 2727, 'US-MS': 6542})",
 "official": {
  "acres": 10188.0,
  "as": "10,188 acre",
  "clean": true,
  "line": "nly 3% of wet pine savanna remaining across its originally range, it is considered an endangered habitat. The 10,188 acre refuge partially overlays the Grand Bay National Estuarine Research Reserve. Together, they protect nearly 18",
  "read": "2026-11-01",
  "sent": "The 10,188 acre refuge partially overlays the Grand Bay National Estuarine Research Reserve.",
  "url": "https://www.fws.gov/refuge/grand_bay/",
  "why": "clean total"
 },
 "ours": {
  "acres": 9269,
  "acres_by_state": {
   "US-AL": 2727,
   "US-MS": 6542
  },
  "dissolved": {
   "after": 7667,
   "before": 15334,
   "copies": 1,
   "key_union": 6542,
   "parts": 0,
   "records": 2,
   "summed": 7667,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 15334 -> 7667 acres",
  "pieces": [
   [
    3872,
    "Grand Bay National Wildlife Refuge",
    7667,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "states": [
   "US-AL",
   "US-MS"
  ],
  "unknown_pieces": 0,
  "whole_park": true
 },
 "owner_now": null,
 "pct": 9,
 "same_agency": false,
 "score": 7,
 "t": "National Wildlife Refuge",
 "verdict": "agree"
}
```

## US-0715 Brices Cross Roads National Battlefield
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Brices Cross Roads National Battlefield",
 "official": null,
 "ours": {
  "acres": 1,
  "manager": "",
  "pieces": [
   [
    3109,
    "Brices Cross Roads National Battlefield Site",
    1,
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
 "t": "National Battlefield",
 "verdict": "no size on page"
}
```

## US-0389 Morgan Brake National Wildlife Refuge
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Morgan Brake National Wildlife Refuge",
 "official": {
  "acres": 7400.0,
  "as": "7,400 acres",
  "clean": false,
  "line": "ws Library Species Map About Us Morgan Brake National Wildlife Refuge, established in 1977, encompasses about 7,400 acres in Holmes County along the ecological border between the Mississippi alluvial plain and loessal hills in the",
  "read": "2026-11-01",
  "sent": "Morgan Brake National Wildlife Refuge, established in 1977, encompasses about 7,400 acres in Holmes County along the ecological border between the Mississippi alluvial plain and loessal hills in the biologically and culturally unique Delta region of Mississippi.",
  "url": "https://www.fws.gov/refuge/morgan-brake/about-us",
  "why": "history"
 },
 "ours": {
  "acres": 6338,
  "dissolved": {
   "after": 7569,
   "before": 15138,
   "copies": 1,
   "key_union": 6338,
   "parts": 0,
   "records": 2,
   "summed": 7569,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 15138 -> 7569 acres",
  "pieces": [
   [
    4134,
    "Morgan Brake National Wildlife Refuge",
    7569,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 14,
 "same_agency": false,
 "score": 7,
 "t": "National Wildlife Refuge",
 "verdict": "agree"
}
```

## US-7085 John W. Starr Wildlife Management Area
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-08",
 "n": "John W. Starr Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 8268,
  "manager": "",
  "pieces": [
   [
    211196,
    "John W. Starr Wma",
    8268,
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
 "t": "Wildlife Management Area",
 "verdict": "no size on page"
}
```

## US-0392 St. Catherine Creek National Wildlife Refuge
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-11-01",
 "handover": [],
 "n": "St. Catherine Creek National Wildlife Refuge",
 "official": null,
 "ours": {
  "acres": 26398,
  "manager": "",
  "pieces": [
   [
    4350,
    "St. Catherine Creek National Wildlife Refuge",
    24909,
    "name"
   ],
   [
    5308,
    "St. Catherine Creek National Wildlife Refuge",
    24286,
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

## US-7082 Shipland Wildlife Management Area
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-08",
 "n": "Shipland Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 4101,
  "manager": "",
  "pieces": [
   [
    211229,
    "Shipland Wma",
    4101,
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
 "t": "Wildlife Management Area",
 "verdict": "no size on page"
}
```

## US-7093 Divide Section Wildlife Management Area
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-08",
 "n": "Divide Section Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 19769,
  "family_fold": "layers {'padus': 16145, 'mszw': 14835}: one land in 2 layers, the padus copy used (14,835 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    211178,
    "Divide Section",
    16145,
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
 "t": "Wildlife Management Area",
 "verdict": "no size on page"
}
```

## US-0383 Dahomey National Wildlife Refuge
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Dahomey National Wildlife Refuge",
 "official": {
  "acres": 9691.0,
  "as": "9,691 acre",
  "clean": false,
  "line": "itat for migratory birds and to protect wetlands, with an emphasis on waterfowl and bottomland hardwoods. The 9,691-acre refuge was purchased from The Nature Conservancy, donated by the Mississippi Department of Transportation, an",
  "read": "2026-11-01",
  "sent": "The 9,691-acre refuge was purchased from The Nature Conservancy, donated by the Mississippi Department of Transportation, and leased from the West Bolivar School Board.",
  "url": "https://www.fws.gov/refuge/Dahomey/",
  "why": "part (a lake, a purchase, a campground…)"
 },
 "ours": {
  "acres": 8428,
  "dissolved": {
   "after": 9537,
   "before": 19074,
   "copies": 1,
   "key_union": 8428,
   "parts": 0,
   "records": 2,
   "summed": 9537,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 19074 -> 9537 acres",
  "pieces": [
   [
    3763,
    "Dahomey National Wildlife Refuge",
    9537,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 13,
 "same_agency": false,
 "score": 8,
 "t": "National Wildlife Refuge",
 "verdict": "agree"
}
```

## US-2538 Holmes County State Park
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-08",
 "n": "Holmes County State Park",
 "official": null,
 "ours": {
  "acres": 544,
  "manager": "",
  "pieces": [
   [
    211154,
    "Holmes County State Park",
    544,
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
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-2548 Paul B. Johnson State Park
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-08",
 "n": "Paul B. Johnson State Park",
 "official": null,
 "ours": {
  "acres": 511,
  "manager": "",
  "pieces": [
   [
    211163,
    "Paul B. Johnson State Park",
    511,
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
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-7122 Marion County Wildlife Management Area
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-08",
 "n": "Marion County Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 7362,
  "manager": "",
  "pieces": [
   [
    211223,
    "Marion County Wma",
    7362,
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
 "t": "Wildlife Management Area",
 "verdict": "no size on page"
}
```
