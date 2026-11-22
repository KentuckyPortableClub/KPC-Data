# park truth checker: US-MN random sample of 12 (2026-11-22; seed = date + area, same rows for everyone)

Source file: `data/truth/US-MN.json`

## US-0370 Sherburne National Wildlife Refuge
```json
{
 "checked": "2026-11-22",
 "handover": [
  {
   "date_hint": null,
   "kind": "managed by",
   "line": "rn How to Get Involved Services The National Wildlife Refuge System is a series of lands and waters owned and managed by the U.S. Fish and Wildlife Service. Wildlife conservation is at the heart of the refuge system, which uses management tools like prescribed fire, invasive speci",
   "owner_now": "U.S",
   "src": "https://www.fws.gov/refuge/sherburne",
   "why": "the park's page (data/parkinfo)"
  }
 ],
 "n": "Sherburne National Wildlife Refuge",
 "official": {
  "acres": 30700.0,
  "as": "30,700 acres",
  "clean": true,
  "line": "s & Regulations About Sherburne National Wildlife Refuge is located in east central Minnesota and encompasses 30,700 acres of oak savanna, prairie, forest, and wetland habitats. Established in 1965, it serves as an inviolate sanctua",
  "read": "2026-11-22",
  "sent": "Sherburne National Wildlife Refuge is located in east central Minnesota and encompasses 30,700 acres of oak savanna, prairie, forest, and wetland habitats.",
  "url": "https://www.fws.gov/refuge/sherburne",
  "why": "clean total"
 },
 "ours": {
  "acres": 30670,
  "dissolved": {
   "after": 30670,
   "before": 61340,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 61340 -> 30670 acres",
  "pieces": [
   [
    4333,
    "Sherburne National Wildlife Refuge",
    30670,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": "U.S",
 "pct": 0,
 "same_agency": false,
 "score": 8,
 "t": "National Wildlife Refuge",
 "verdict": "agree"
}
```

## US-12395 St. Croix Boom Site Unique Area
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-11-22",
 "handover": [],
 "n": "St. Croix Boom Site Unique Area",
 "official": null,
 "ours": {
  "acres": 91,
  "family_fold": "layers {'sgmnf': 12, 'sgmne': 11}: one land in 2 layers, the sgmnf copy used (11 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgmnf4156",
    "Saint Croix Boom Site",
    12,
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
 "t": "Unique Area",
 "verdict": "unsure"
}
```

## US-12390 Flood Bay Unique Area
```json
{
 "cause": "a number 7 parks share from the same sentence (26 ac): an agency total, not this park",
 "checked": "2026-11-22",
 "handover": [],
 "n": "Flood Bay Unique Area",
 "official": null,
 "ours": {
  "acres": 93,
  "dissolved": {
   "after": 47,
   "before": 94,
   "copies": 1,
   "families": {
    "sgmne": 19,
    "sgmnf": 28
   },
   "family_fold": 19,
   "family_used": "sgmnf",
   "key_union": 93,
   "parts": 3,
   "records": 7,
   "summed": 28,
   "tracts": 3
  },
  "family_fold": "layers {'sgmnf': 28, 'sgmne': 19}: one land in 2 layers, the sgmnf copy used (19 ac of copies not added)",
  "manager": "",
  "note": "7 joined records = 3 tracts: 1 copies of a tract (same acres, another layer) and 3 fee tracts under a designation record folded; summed 94 -> 47 acres",
  "pieces": [
   [
    "sgmnf4217",
    "Flood Bay",
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
 "same_agency": false,
 "score": 6,
 "t": "Unique Area",
 "verdict": "unsure"
}
```

## US-2506 Lake Vermilion State Park
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Lake Vermilion State Park",
 "official": null,
 "ours": {
  "acres": 4094,
  "manager": "",
  "pieces": [
   [
    209838,
    "Lake Vermilion-Soudan Underground Mine State Park",
    4094,
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
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-4830 Solana State Forest
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Solana State Forest",
 "official": null,
 "ours": {
  "acres": 68143,
  "family_fold": "layers {'sgmnb': 68143, 'padus': 57520}: one land in 2 layers, the sgmnb copy used (57,520 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgmnb31",
    "Solana",
    68143,
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
 "t": "State Forest",
 "verdict": "no size on page"
}
```

## US-4812 Lyons State Forest
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Lyons State Forest",
 "official": null,
 "ours": {
  "acres": 14789,
  "family_fold": "layers {'sgmnb': 14789, 'padus': 6512}: one land in 2 layers, the sgmnb copy used (6,512 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgmnb3",
    "Lyons",
    14789,
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
 "t": "State Forest",
 "verdict": "no size on page"
}
```

## US-4780 Badoura State Forest
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Badoura State Forest",
 "official": null,
 "ours": {
  "acres": 41207,
  "family_fold": "layers {'sgmnb': 41207, 'padus': 4568}: one land in 2 layers, the sgmnb copy used (4,568 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgmnb56",
    "Pillsbury",
    25672,
    "reviewed"
   ],
   [
    "sgmnb10",
    "Badoura",
    15535,
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
 "t": "State Forest",
 "verdict": "no size on page"
}
```

## US-2493 Interstate State Park
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Interstate State Park",
 "official": null,
 "ours": {
  "acres": 844,
  "dissolved": {
   "after": 653,
   "before": 830,
   "copies": 0,
   "families": {
    "padus": 272,
    "sgmnd": 281,
    "sgmne": 100
   },
   "family_fold": 372,
   "family_used": "sgmnd",
   "key_union": 844,
   "parts": 14,
   "records": 19,
   "summed": 281,
   "tracts": 5
  },
  "family_fold": "layers {'sgmnd': 281, 'padus': 272, 'sgmne': 100}: one land in 3 layers, the sgmnd copy used (372 ac of copies not added)",
  "manager": "",
  "note": "19 joined records = 5 tracts: 0 copies of a tract (same acres, another layer) and 14 fee tracts under a designation record folded; summed 830 -> 653 acres",
  "pieces": [
   [
    "sgmnd49",
    "Interstate",
    281,
    "reviewed"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 7
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-4794 Emily State Forest
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Emily State Forest",
 "official": null,
 "ours": {
  "acres": 640,
  "dissolved": {
   "after": 640,
   "before": 1280,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1280 -> 640 acres",
  "pieces": [
   [
    207816,
    "Emily State Forest",
    640,
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
 "t": "State Forest",
 "verdict": "no size on page"
}
```

## US-2498 Kilen Woods State Park
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Kilen Woods State Park",
 "official": null,
 "ours": {
  "acres": 690,
  "dissolved": {
   "after": 864,
   "before": 969,
   "copies": 0,
   "families": {
    "padus": 215,
    "sgmnd": 553,
    "sgmne": 96
   },
   "family_fold": 311,
   "family_used": "sgmnd",
   "key_union": 690,
   "parts": 8,
   "records": 14,
   "summed": 553,
   "tracts": 6
  },
  "family_fold": "layers {'sgmnd': 553, 'padus': 215, 'sgmne': 96}: one land in 3 layers, the sgmnd copy used (311 ac of copies not added)",
  "manager": "",
  "note": "14 joined records = 6 tracts: 0 copies of a tract (same acres, another layer) and 8 fee tracts under a designation record folded; summed 969 -> 864 acres",
  "pieces": [
   [
    "sgmnd13",
    "Kilen Woods",
    553,
    "reviewed"
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

## US-12388 Caribou Falls Unique Area
```json
{
 "cause": "a number 7 parks share from the same sentence (26 ac): an agency total, not this park",
 "checked": "2026-11-22",
 "handover": [],
 "n": "Caribou Falls Unique Area",
 "official": null,
 "ours": {
  "acres": 444,
  "dissolved": {
   "after": 179,
   "before": 358,
   "copies": 1,
   "families": {
    "padus": 91,
    "sgmnf": 88
   },
   "family_fold": 88,
   "family_used": "padus",
   "key_union": 444,
   "parts": 3,
   "records": 6,
   "summed": 91,
   "tracts": 2
  },
  "family_fold": "layers {'padus': 91, 'sgmnf': 88}: one land in 2 layers, the padus copy used (88 ac of copies not added)",
  "manager": "",
  "note": "6 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 3 fee tracts under a designation record folded; summed 358 -> 179 acres",
  "pieces": [
   [
    209792,
    "Caribou Falls State Wayside",
    91,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 2
 },
 "owner_now": null,
 "pct": null,
 "same_agency": false,
 "score": 6,
 "t": "Unique Area",
 "verdict": "unsure"
}
```

## US-12457 Riverlands State Forest
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Riverlands State Forest",
 "official": null,
 "ours": {
  "acres": 22861,
  "manager": "",
  "pieces": [
   [
    "sgmnb39",
    "Riverlands",
    22861,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "State Forest",
 "verdict": "no size on page"
}
```
