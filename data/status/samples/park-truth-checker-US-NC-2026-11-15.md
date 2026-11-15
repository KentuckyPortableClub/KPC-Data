# park truth checker: US-NC random sample of 12 (2026-11-15; seed = date + area, same rows for everyone)

Source file: `data/truth/US-NC.json`

## US-2743 Mayo River State Park
```json
{
 "checked": "2026-11-08",
 "handover": [],
 "n": "Mayo River State Park",
 "official": null,
 "ours": {
  "acres": 3526,
  "dissolved": {
   "after": 5070,
   "before": 10178,
   "copies": 2,
   "families": {
    "padus": 1,
    "sgnca": 3526,
    "sgncd": 1543
   },
   "family_fold": 1544,
   "family_used": "sgnca",
   "parts": 22,
   "records": 32,
   "tracts": 8
  },
  "family_fold": "layers {'sgnca': 3526, 'sgncd': 1543, 'padus': 1}: one land in 3 layers, the sgnca copy used (1,544 ac of copies not added)",
  "manager": "",
  "note": "32 joined records = 8 tracts: 2 copies of a tract (same acres, another layer) and 22 fee tracts under a designation record folded; summed 10178 -> 5070 acres",
  "pieces": [
   [
    "sgnca4332",
    "Mayo River State Park",
    3526,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 2
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-6918 Kerr Scott State Game Land
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-15",
 "n": "Kerr Scott State Game Land",
 "official": null,
 "ours": {
  "acres": 521,
  "dissolved": {
   "after": 521,
   "before": 1562,
   "copies": 1,
   "parts": 6,
   "records": 8,
   "tracts": 1
  },
  "manager": "",
  "note": "8 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 6 fee tracts under a designation record folded; summed 1562 -> 521 acres",
  "pieces": [
   [
    "ncg41",
    "Kerr Scott",
    521,
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
 "t": "State Game Land",
 "verdict": "no size on page"
}
```

## US-6838 Duke Homestead State Historic Site
```json
{
 "checked": "2026-11-08",
 "handover": [
  {
   "date_hint": null,
   "kind": "managed by",
   "line": "vides updates about both DHEHC and the latest activities at Duke Homestead State Historic Site, and is managed by DHEHC. Planning your visit Operating Hours Tuesday through Saturday, 9 am to 5 pm. Admission to the grounds and museum is free of charge, donations are welcom",
   "owner_now": "DHEHC",
   "src": "https://dukehomestead.org/",
   "why": "the park's page (data/parkinfo)"
  }
 ],
 "n": "Duke Homestead State Historic Site",
 "official": null,
 "ours": {
  "acres": 36,
  "dissolved": {
   "after": 45,
   "before": 90,
   "copies": 1,
   "key_union": 36,
   "parts": 0,
   "records": 2,
   "summed": 45,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 90 -> 45 acres",
  "pieces": [
   [
    214559,
    "Duke Homestead State Historic Site",
    45,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": "DHEHC",
 "pct": null,
 "score": 7,
 "t": "State Historic Site",
 "verdict": "no size on page"
}
```

## US-11019 Shining Rock Wilderness Area
```json
{
 "checked": "2026-11-08",
 "handover": [],
 "n": "Shining Rock Wilderness Area",
 "official": null,
 "ours": {
  "acres": 20145,
  "dissolved": {
   "after": 18723,
   "before": 37201,
   "copies": 1,
   "key_union": 20145,
   "parts": 0,
   "records": 2,
   "summed": 18723,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 37201 -> 18723 acres",
  "pieces": [
   [
    "sgnca5878",
    "Pisgah National Forest - Shining Rock Wilderness",
    18723,
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
 "t": "Wilderness Area",
 "verdict": "no size on page"
}
```

## US-6907 Green Swamp State Game Land
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-11-08",
 "handover": [],
 "n": "Green Swamp State Game Land",
 "official": null,
 "ours": {
  "acres": 18577,
  "dissolved": {
   "after": 24806,
   "before": 46158,
   "copies": 1,
   "families": {
    "padus": 3835,
    "sgncb": 18577,
    "sgncc": 2394
   },
   "family_fold": 6229,
   "family_used": "sgncb",
   "parts": 6,
   "records": 13,
   "tracts": 6
  },
  "family_fold": "layers {'sgncb': 18577, 'padus': 3835, 'sgncc': 2394}: one land in 3 layers, the sgncb copy used (6,229 ac of copies not added)",
  "manager": "",
  "note": "13 joined records = 6 tracts: 1 copies of a tract (same acres, another layer) and 6 fee tracts under a designation record folded; summed 46158 -> 24806 acres",
  "pieces": [
   [
    "sgncb30",
    "Green Swamp",
    18577,
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
 "t": "State Game Land",
 "verdict": "unsure"
}
```

## US-0419 Swanquarter National Wildlife Refuge
```json
{
 "cause": "agency smaller: our outline may hold water, a lease or a neighbour tract",
 "checked": "2026-11-08",
 "handover": [],
 "n": "Swanquarter National Wildlife Refuge",
 "official": {
  "acres": 13200.0,
  "as": "13,200 acres",
  "clean": false,
  "line": "prey nesting and colonial nesting birds occur. Refuge habitats consist of irregularly flooded brackish marsh (13,200 acres) and forested wetlands (3,200 acres). The refuge provides habitat for American alligators and bald eagles as",
  "read": "2026-11-08",
  "sent": "Refuge habitats consist of irregularly flooded brackish marsh (13,200 acres) and forested wetlands (3,200 acres).",
  "url": "https://www.fws.gov/refuge/swanquarter/about-us",
  "why": "total-looking"
 },
 "ours": {
  "acres": 18121,
  "dissolved": {
   "after": 16656,
   "before": 49935,
   "copies": 2,
   "key_union": 18121,
   "parts": 0,
   "records": 3,
   "summed": 16656,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 49935 -> 16656 acres",
  "pieces": [
   [
    "sgnca6528",
    "Swanquarter National Wildlife Refuge",
    16656,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 37,
 "same_agency": false,
 "score": 5,
 "t": "National Wildlife Refuge",
 "verdict": "off"
}
```

## US-6928 Needmore State Game Land
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-15",
 "n": "Needmore State Game Land",
 "official": null,
 "ours": {
  "acres": 5630,
  "dissolved": {
   "after": 8593,
   "before": 15561,
   "copies": 2,
   "families": {
    "sgnca": 5093,
    "sgncc": 3500
   },
   "family_fold": 3500,
   "family_used": "sgnca",
   "key_union": 5630,
   "parts": 43,
   "records": 51,
   "summed": 5093,
   "tracts": 6
  },
  "family_fold": "layers {'sgnca': 5093, 'sgncc': 3500}: one land in 2 layers, the sgnca copy used (3,500 ac of copies not added)",
  "manager": "",
  "note": "51 joined records = 6 tracts: 2 copies of a tract (same acres, another layer) and 43 fee tracts under a designation record folded; summed 15561 -> 8593 acres",
  "pieces": [
   [
    "sgnca5288",
    "Needmore Game Land",
    5093,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 3
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "State Game Land",
 "verdict": "no size on page"
}
```

## US-2744 Medoc Mountain State Park
```json
{
 "checked": "2026-11-08",
 "handover": [],
 "n": "Medoc Mountain State Park",
 "official": null,
 "ours": {
  "acres": 4456,
  "dissolved": {
   "after": 8398,
   "before": 12466,
   "copies": 1,
   "families": {
    "padus": 3939,
    "sgnca": 4456,
    "sgncd": 3
   },
   "family_fold": 3942,
   "family_used": "sgnca",
   "parts": 0,
   "records": 5,
   "tracts": 4
  },
  "family_fold": "layers {'sgnca': 4456, 'padus': 3939, 'sgncd': 3}: one land in 3 layers, the sgnca copy used (3,942 ac of copies not added)",
  "manager": "",
  "note": "5 joined records = 4 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 12466 -> 8398 acres",
  "pieces": [
   [
    "sgnca4662",
    "Medoc Mountain State Park",
    4071,
    "name"
   ],
   [
    "sgnca21282",
    "Medoc Mountain State Park Dedicated Nature Preserve",
    385,
    "words"
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

## US-6883 Brinkleyville State Game Land
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-15",
 "n": "Brinkleyville State Game Land",
 "official": null,
 "ours": {
  "acres": 3341,
  "dissolved": {
   "after": 5061,
   "before": 11853,
   "copies": 1,
   "families": {
    "sgnca": 3341,
    "sgncc": 1720
   },
   "family_fold": 1720,
   "family_used": "sgnca",
   "parts": 7,
   "records": 14,
   "tracts": 6
  },
  "family_fold": "layers {'sgnca': 3341, 'sgncc': 1720}: one land in 2 layers, the sgnca copy used (1,720 ac of copies not added)",
  "manager": "",
  "note": "14 joined records = 6 tracts: 1 copies of a tract (same acres, another layer) and 7 fee tracts under a designation record folded; summed 11853 -> 5061 acres",
  "pieces": [
   [
    "sgnca220",
    "Brinkleyville Game Land",
    3341,
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
 "t": "State Game Land",
 "verdict": "no size on page"
}
```

## US-10260 Birkhead Mountains Wilderness Area
```json
{
 "checked": "2026-11-08",
 "handover": [],
 "n": "Birkhead Mountains Wilderness Area",
 "official": null,
 "ours": {
  "acres": 4769,
  "family_fold": "layers {'wld': 5216, 'sgnca': 5084}: one land in 2 layers, the wld copy used (5,084 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "wld50",
    "Birkhead Mountains Wilderness",
    5216,
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
 "t": "Wilderness Area",
 "verdict": "no size on page"
}
```

## US-6846 House in the Horseshoe State Historic Site
```json
{
 "cause": "the agency figure may cover several states; our outline may be this state's share only",
 "checked": "2026-11-08",
 "handover": [],
 "n": "House in the Horseshoe State Historic Site",
 "note": "the agency figure may cover several states; our outline may be this state's share only",
 "official": {
  "acres": 2500.0,
  "as": "2,500 acre",
  "clean": false,
  "line": "ip Alston sold the house and plantation and left the state. Retreat In 1798 Gov. Benjamin Williams bought the 2,500-acre plantation. Besides serving four one-year terms as the state's governor and a colonel under George Washington",
  "read": "2026-11-08",
  "sent": "Benjamin Williams bought the 2,500-acre plantation.",
  "url": "https://historicsites.nc.gov/all-sites/house-horseshoe/history",
  "why": "total-looking"
 },
 "ours": {
  "acres": 12,
  "dissolved": {
   "after": 12,
   "before": 24,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 24 -> 12 acres",
  "pieces": [
   [
    214571,
    "House in the Horseshoe State Historic Site",
    12,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 100,
 "same_agency": false,
 "score": 6,
 "t": "State Historic Site",
 "verdict": "unsure"
}
```

## US-2741 Lake Waccamaw State Park
```json
{
 "checked": "2026-11-08",
 "handover": [],
 "n": "Lake Waccamaw State Park",
 "official": null,
 "ours": {
  "acres": 10525,
  "dissolved": {
   "after": 11497,
   "before": 33997,
   "copies": 1,
   "key_union": 10525,
   "parts": 3,
   "records": 7,
   "summed": 11497,
   "tracts": 3
  },
  "manager": "",
  "note": "7 joined records = 3 tracts: 1 copies of a tract (same acres, another layer) and 3 fee tracts under a designation record folded; summed 33997 -> 11497 acres",
  "pieces": [
   [
    214844,
    "Lake Waccamaw State Park",
    11266,
    "name"
   ],
   [
    "sgnca21246",
    "Lake Waccamaw State Park Proposed Dedicated Nature Preserve",
    199,
    "words"
   ],
   [
    "sgncd294",
    "Lake Waccamaw",
    32,
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
