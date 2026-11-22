# park truth checker: US-FL random sample of 12 (2026-11-22; seed = date + area, same rows for everyone)

Source file: `data/truth/US-FL.json`

## US-1879 Homosassa Springs Wildlife State Park
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Homosassa Springs Wildlife State Park",
 "official": null,
 "ours": {
  "acres": 201,
  "dissolved": {
   "after": 201,
   "before": 402,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 402 -> 201 acres",
  "pieces": [
   [
    191850,
    "Ellie Schiller Homosassa Springs Wildlife State Park",
    201,
    "words"
   ]
  ],
  "pin": "inside",
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

## US-1846 Cayo Costa State Park
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Cayo Costa State Park",
 "official": null,
 "ours": {
  "acres": 2667,
  "family_fold": "layers {'sgfla': 2667, 'padus': 2449}: one land in 2 layers, the sgfla copy used (2,449 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgfla159",
    "Cayo Costa State Park",
    2667,
    "reviewed"
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

## US-1876 Henderson Beach State Park
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Henderson Beach State Park",
 "official": null,
 "ours": {
  "acres": 251,
  "family_fold": "layers {'sgfla': 251, 'padus': 228}: one land in 2 layers, the sgfla copy used (228 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgfla163",
    "Henderson Beach State Park",
    251,
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
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-3608 Blackwater Heritage State Trail
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Blackwater Heritage State Trail",
 "official": null,
 "ours": {
  "acres": 587,
  "family_fold": "layers {'padus': 587, 'sgfla': 308, 'sgflf': 2}: one land in 3 layers, the padus copy used (310 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    9560,
    "Blackwater Heritage State Trail",
    587,
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
 "t": "State Trail",
 "verdict": "no size on page"
}
```

## US-6327 Tenoroc Wildlife Area
```json
{
 "cause": "agency smaller: our outline may hold water, a lease or a neighbour tract",
 "checked": "2026-11-15",
 "handover": [],
 "n": "Tenoroc Wildlife Area",
 "official": {
  "acres": 242.0,
  "as": "242 acres",
  "clean": true,
  "line": "on to Tenoroc. Tenoroc currently exists as a mostly mined-over site, where lakes ranging in size from five to 242 acres provide quality public fishing. Two types – reclaimed and unreclaimed – offer different fishing challenges. B",
  "read": "2026-11-15",
  "sent": "Tenoroc currently exists as a mostly mined-over site, where lakes ranging in size from five to 242 acres provide quality public fishing.",
  "url": "https://myfwc.com/recreation/lead/tenoroc/",
  "why": "clean total; the agency's pages disagree: another of its pages says 341 acres (that one matches our outline)"
 },
 "ours": {
  "acres": 372,
  "manager": "",
  "pieces": [
   [
    "sgflf74798",
    "Tenoroc State Reserve",
    27,
    "name"
   ],
   [
    "sgflf2908",
    "Tenoroc Fish Management Area",
    13,
    "words"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 3
 },
 "owner_now": null,
 "pct": 54,
 "same_agency": false,
 "score": 5,
 "t": "Wildlife Area",
 "verdict": "off"
}
```

## US-6318 Okaloacoochee Slough Wildlife Management Area
```json
{
 "checked": "2026-11-15",
 "handover": [],
 "n": "Okaloacoochee Slough Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 58459,
  "dissolved": {
   "after": 22377,
   "before": 41831,
   "copies": 0,
   "key_union": 58459,
   "parts": 2,
   "records": 4,
   "summed": 22377,
   "tracts": 2
  },
  "manager": "",
  "note": "4 joined records = 2 tracts: 0 copies of a tract (same acres, another layer) and 2 fee tracts under a designation record folded; summed 41831 -> 22377 acres",
  "pieces": [
   [
    "sgflf30220",
    "Okaloacoochee Slough",
    19454,
    "name"
   ],
   [
    "sgflf59213",
    "Okaloacoochee Slough Wildlife Management Area",
    2923,
    "reviewed"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 2
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "Wildlife Management Area",
 "verdict": "no size on page"
}
```

## US-3651 San Felasco Hammock Preserve State Park
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "San Felasco Hammock Preserve State Park",
 "official": null,
 "ours": {
  "acres": 7363,
  "dissolved": {
   "after": 11208,
   "before": 20256,
   "copies": 1,
   "families": {
    "sgfla": 7363,
    "sgflf": 3845
   },
   "family_fold": 3845,
   "family_used": "sgfla",
   "parts": 4,
   "records": 13,
   "tracts": 8
  },
  "family_fold": "layers {'sgfla': 7363, 'sgflf': 3845}: one land in 2 layers, the sgfla copy used (3,845 ac of copies not added)",
  "manager": "",
  "note": "13 joined records = 8 tracts: 1 copies of a tract (same acres, another layer) and 4 fee tracts under a designation record folded; summed 20256 -> 11208 acres",
  "pieces": [
   [
    "sgfla115",
    "San Felasco Hammock Preserve State Park",
    7363,
    "reviewed"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 8
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-10619 Little River Wildlife Management Area
```json
{
 "cause": "agency smaller: our outline may hold water, a lease or a neighbour tract",
 "checked": "2026-11-15",
 "handover": [],
 "n": "Little River Wildlife Management Area",
 "official": {
  "acres": 2000.0,
  "as": "2,000 acres",
  "clean": false,
  "line": "ng the Middle Suwannee in southwest Suwannee County, north of Branford. This quiet area consists of more than 2,000 acres. Numerous springs along this portion of the Suwannee contribute to the river's flow. You can view a map of th",
  "read": "2026-11-15",
  "sent": "This quiet area consists of more than 2,000 acres.",
  "url": "https://myfwc.com/recreation/cooperative/little-river/",
  "why": "total-looking"
 },
 "ours": {
  "acres": 3475,
  "family_fold": "layers {'padus': 3267, 'sgfld': 2436}: one land in 2 layers, the padus copy used (2,436 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    190433,
    "Little River Conservation Area",
    3267,
    "reviewed"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 74,
 "same_agency": false,
 "score": 6,
 "t": "Wildlife Management Area",
 "verdict": "off"
}
```

## US-3626 Gamble Rogers Memorial State Recreation Area
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Gamble Rogers Memorial State Recreation Area",
 "official": null,
 "ours": {
  "acres": 125,
  "dissolved": {
   "after": 134,
   "before": 268,
   "copies": 1,
   "key_union": 125,
   "parts": 0,
   "records": 2,
   "summed": 134,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 268 -> 134 acres",
  "pieces": [
   [
    191915,
    "Gamble Rogers Memorial State Recreation Area at Flagler Beach",
    134,
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

## US-8374 Thomas Creek State Conservation Area
```json
{
 "checked": "2026-11-15",
 "handover": [],
 "n": "Thomas Creek State Conservation Area",
 "official": null,
 "ours": {
  "acres": 5409,
  "manager": "",
  "pieces": [
   [
    190356,
    "Thomas Creek Conservation Area",
    5409,
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
 "t": "State Conservation Area",
 "verdict": "no size on page"
}
```

## US-8698 Ruth-Springs State Conservation Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Ruth-Springs State Conservation Area",
 "official": {
  "acres": 628.8,
  "as": "628.84 acres",
  "clean": false,
  "line": "oe Launch Fishing Hiking Horseback Riding Hunting Parking Scenic Viewing Wildlife Viewing Size RUTH SPRINGS - 628.84 acres Downloads Map Legend",
  "read": "2026-11-01",
  "sent": "RUTH SPRINGS - 628.84 acres",
  "url": "https://map.mysuwanneeriver.com/tracts/ruth-springs/",
  "why": "total-looking"
 },
 "ours": {
  "acres": 629,
  "manager": "",
  "pieces": [
   [
    "sgfld182",
    "RUTH SPRINGS",
    581,
    "name"
   ],
   [
    "sgfld981",
    "RUTH SPRINGS",
    48,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 0,
 "same_agency": false,
 "score": 8,
 "t": "State Conservation Area",
 "verdict": "agree"
}
```

## US-5520 Chassahowitzka River and Coastal Swamp State Conservation Area
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Chassahowitzka River and Coastal Swamp State Conservation Area",
 "official": null,
 "ours": {
  "acres": 6701,
  "dissolved": {
   "after": 5713,
   "before": 11349,
   "copies": 0,
   "key_union": 6701,
   "parts": 2,
   "records": 5,
   "summed": 5713,
   "tracts": 3
  },
  "manager": "",
  "note": "5 joined records = 3 tracts: 0 copies of a tract (same acres, another layer) and 2 fee tracts under a designation record folded; summed 11349 -> 5713 acres",
  "pieces": [
   [
    190294,
    "Chassahowitzka River and Coastal Swamps",
    5670,
    "name"
   ],
   [
    "sgflf15098",
    "Chassahowitzka River And Coastal Swamps",
    40,
    "name"
   ],
   [
    "sgflf15099",
    "Chassahowitzka River And Coastal Swamps",
    3,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": null,
 "score": 5,
 "t": "State Conservation Area",
 "verdict": "no size on page"
}
```
