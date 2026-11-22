# park truth checker: US-RI random sample of 12 (2026-11-22; seed = date + area, same rows for everyone)

Source file: `data/truth/US-RI.json`

## US-6990 Nicholas Farm Wildlife Management Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Nicholas Farm Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 1504,
  "dissolved": {
   "after": 1545,
   "before": 4052,
   "copies": 3,
   "families": {
    "padus": 705,
    "sgrib": 840
   },
   "family_fold": 705,
   "family_used": "sgrib",
   "key_union": 1504,
   "parts": 0,
   "records": 11,
   "summed": 840,
   "tracts": 8
  },
  "family_fold": "layers {'sgrib': 840, 'padus': 705}: one land in 2 layers, the sgrib copy used (705 ac of copies not added)",
  "manager": "",
  "note": "11 joined records = 8 tracts: 3 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 4052 -> 1545 acres",
  "pieces": [
   [
    "sgrib379",
    "Nicholas Farm",
    840,
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

## US-7865 East State Beach
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "East State Beach",
 "official": null,
 "ours": {
  "acres": 199,
  "dissolved": {
   "after": 199,
   "before": 597,
   "copies": 4,
   "parts": 0,
   "records": 6,
   "tracts": 2
  },
  "manager": "",
  "note": "6 joined records = 2 tracts: 4 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 597 -> 199 acres",
  "pieces": [
   [
    "sgrib264",
    "East Beach",
    134,
    "name"
   ],
   [
    "sgrib121",
    "East Beach",
    65,
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
 "t": "State Beach",
 "verdict": "no size on page"
}
```

## US-5482 Wickaboxet Wildlife Management Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Wickaboxet Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 673,
  "manager": "",
  "pieces": [
   [
    57379,
    "Wickaboxet Management Area",
    434,
    "name"
   ],
   [
    57378,
    "Wickaboxet Management Area",
    239,
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

## US-7719 Misquamicut State Beach
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Misquamicut State Beach",
 "official": null,
 "ours": {
  "acres": 58,
  "dissolved": {
   "after": 66,
   "before": 198,
   "copies": 4,
   "key_union": 58,
   "parts": 0,
   "records": 6,
   "summed": 66,
   "tracts": 2
  },
  "manager": "",
  "note": "6 joined records = 2 tracts: 4 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 198 -> 66 acres",
  "pieces": [
   [
    "sgrib633",
    "Misquamicut State Beach",
    36,
    "name"
   ],
   [
    "sgrib632",
    "Misquamicut State Beach",
    30,
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
 "t": "State Beach",
 "verdict": "no size on page"
}
```

## US-0789 Roger Williams National Memorial
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Roger Williams National Memorial",
 "official": null,
 "ours": {
  "acres": 5,
  "manager": "",
  "pieces": [
   [
    3273,
    "Roger Williams National Memorial",
    5,
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
 "t": "National Memorial",
 "verdict": "no size on page"
}
```

## US-10542 Camp Cronin State Recreation Area
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 33 acres, no total words near it)",
 "checked": "2026-11-22",
 "handover": [],
 "n": "Camp Cronin State Recreation Area",
 "official": {
  "acres": 33.0,
  "as": "33 acres",
  "clean": false,
  "line": "to Harkney Hill Rd., 2 miles on right. Cement slab (S) State-owned & operated None Yes Exeter Breakheart Pond 33 acres. In Arcadia Management Area. Rt. 3, to Rt. 165, to Frosty Hollow Rd., to Austin Farm Rd., ¼ mile. Gravel ramp",
  "read": "2026-11-22",
  "sent": "Breakheart Pond 33 acres.",
  "url": "https://dem.ri.gov/natural-resources-bureau/fish-wildlife/freshwater-fishing/public-boat-launching-sites#salt",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 26,
  "dissolved": {
   "after": 26,
   "before": 78,
   "copies": 2,
   "parts": 0,
   "records": 3,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 78 -> 26 acres",
  "pieces": [
   [
    "sgrib648",
    "Camp Cronin",
    26,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 21,
 "same_agency": false,
 "score": 6,
 "t": "State Recreation Area",
 "verdict": "unsure"
}
```

## US-10541 Gull Cove State Recreation Area
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 33 acres, no total words near it)",
 "checked": "2026-11-22",
 "handover": [],
 "n": "Gull Cove State Recreation Area",
 "official": {
  "acres": 33.0,
  "as": "33 acres",
  "clean": false,
  "line": "to Harkney Hill Rd., 2 miles on right. Cement slab (S) State-owned & operated None Yes Exeter Breakheart Pond 33 acres. In Arcadia Management Area. Rt. 3, to Rt. 165, to Frosty Hollow Rd., to Austin Farm Rd., ¼ mile. Gravel ramp",
  "read": "2026-11-22",
  "sent": "Breakheart Pond 33 acres.",
  "url": "https://dem.ri.gov/natural-resources-bureau/fish-wildlife/freshwater-fishing/public-boat-launching-sites#salt",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 3,
  "dissolved": {
   "after": 3,
   "before": 9,
   "copies": 2,
   "parts": 0,
   "records": 3,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 9 -> 3 acres",
  "pieces": [
   [
    "sgrib678",
    "Gull Cove Fishing Area",
    3,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 91,
 "same_agency": false,
 "score": 6,
 "t": "State Recreation Area",
 "verdict": "unsure"
}
```

## US-6981 Great Swamp Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Great Swamp Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 3698,
  "dissolved": {
   "after": 3347,
   "before": 11803,
   "copies": 2,
   "key_union": 3698,
   "parts": 6,
   "records": 16,
   "summed": 3347,
   "tracts": 8
  },
  "manager": "",
  "note": "16 joined records = 8 tracts: 2 copies of a tract (same acres, another layer) and 6 fee tracts under a designation record folded; summed 11803 -> 3347 acres",
  "pieces": [
   [
    57300,
    "Great Swamp Management Area",
    2838,
    "name"
   ],
   [
    57303,
    "Great Swamp Management Area",
    215,
    "name"
   ],
   [
    57299,
    "Great Swamp",
    99,
    "name"
   ],
   [
    57309,
    "Great Swamp Management Area",
    57,
    "name"
   ],
   [
    57298,
    "Great Swamp",
    54,
    "name"
   ],
   [
    57306,
    "Great Swamp Management Area",
    38,
    "name"
   ],
   [
    57308,
    "Great Swamp Management Area",
    38,
    "name"
   ],
   [
    57301,
    "Great Swamp Management Area",
    8,
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

## US-8293 Sapowet Marsh State Wildlife Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Sapowet Marsh State Wildlife Area",
 "official": null,
 "ours": {
  "acres": 261,
  "dissolved": {
   "after": 389,
   "before": 739,
   "copies": 2,
   "families": {
    "padus": 214,
    "sgrib": 175
   },
   "family_fold": 175,
   "family_used": "padus",
   "key_union": 261,
   "parts": 0,
   "records": 8,
   "summed": 214,
   "tracts": 6
  },
  "family_fold": "layers {'sgrib': 175, 'padus': 214}: one land in 2 layers, the padus copy used (175 ac of copies not added)",
  "manager": "",
  "note": "8 joined records = 6 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 739 -> 389 acres",
  "pieces": [
   [
    57356,
    "Sapowet Marsh Management Area",
    94,
    "name"
   ],
   [
    57355,
    "Sapowet Marsh Management Area",
    67,
    "name"
   ],
   [
    57354,
    "Sapowet Marsh",
    35,
    "name"
   ],
   [
    57358,
    "Sapowet Marsh Management Area",
    12,
    "name"
   ],
   [
    57357,
    "Sapowet Marsh Management Area",
    6,
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
 "t": "State Wildlife Area",
 "verdict": "no size on page"
}
```

## US-0515 Ninigret National Wildlife Refuge
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Ninigret National Wildlife Refuge",
 "official": {
  "acres": 858.0,
  "as": "858 acres",
  "clean": false,
  "line": "benefit of the American people. Jobs About Established in 1970, Ninigret National Wildlife Refuge consists of 858 acres of diverse upland and wetland habitats including grasslands, shrub lands, and wooded swamps. Formerly part of",
  "read": "2026-11-22",
  "sent": "Established in 1970, Ninigret National Wildlife Refuge consists of 858 acres of diverse upland and wetland habitats including grasslands, shrub lands, and wooded swamps.",
  "url": "https://www.fws.gov/refuge/ninigret",
  "why": "history"
 },
 "ours": {
  "acres": 882,
  "dissolved": {
   "after": 882,
   "before": 1764,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1764 -> 882 acres",
  "pieces": [
   [
    4163,
    "Ninigret National Wildlife Refuge",
    882,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 3,
 "same_agency": false,
 "score": 8,
 "t": "National Wildlife Refuge",
 "verdict": "agree"
}
```

## US-6988 Grills State Preserve
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Grills State Preserve",
 "official": null,
 "ours": {
  "acres": 724,
  "dissolved": {
   "after": 724,
   "before": 2172,
   "copies": 6,
   "parts": 0,
   "records": 9,
   "tracts": 3
  },
  "manager": "",
  "note": "9 joined records = 3 tracts: 6 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 2172 -> 724 acres",
  "pieces": [
   [
    "sgrib420",
    "Bradford Dye / Grills Preserve",
    505,
    "words"
   ],
   [
    "sgrib1013",
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
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "State Preserve",
 "verdict": "no size on page"
}
```

## US-4582 Washington-Rochambeau Revolutionary Route National Historic Trail
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Washington-Rochambeau Revolutionary Route National Historic Trail",
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
   "US-VA",
   "US-DE",
   "US-MA",
   "US-MD",
   "US-PA",
   "US-NY",
   "US-NJ",
   "US-RI",
   "US-CT",
   "US-DC"
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
