# park truth checker: US-NM random sample of 12 (2026-11-09; seed = date + area, same rows for everyone)

Source file: `data/truth/US-NM.json`

## US-0547 Grulla National Wildlife Refuge
```json
{
 "checked": "2026-11-09",
 "handover": [
  {
   "date_hint": null,
   "kind": "managed by",
   "line": "Learn More About Us What We Do The National Wildlife Refuge System is a series of lands and waters owned and managed by the U.S. Fish and Wildlife Service. Wildlife conservation is at the heart of the refuge system. It drives everything we do from the purpose a refuge is establis",
   "owner_now": "U.S",
   "src": "https://www.fws.gov/refuge/Grulla/",
   "why": "the park's page (data/parkinfo)"
  },
  {
   "date_hint": "1969",
   "kind": "transfer",
   "line": "About Us Grulla National Wildlife Refuge was officially established as a refuge when the lands were transferred to the U.S. Fish and Wildlife Service from the Bureau of Land Management in 1969. The refuge is 3,236 acres of which the majority is a salt lake. The refuge is a protected roost si",
   "owner_now": "U.S",
   "src": "https://www.fws.gov/refuge/grulla/about-us",
   "why": "about / history page of the park's site"
  }
 ],
 "n": "Grulla National Wildlife Refuge",
 "official": {
  "acres": 3236.0,
  "as": "3,236 acres",
  "clean": false,
  "line": "e transferred to the U.S. Fish and Wildlife Service from the Bureau of Land Management in 1969. The refuge is 3,236 acres of which the majority is a salt lake. The refuge is a protected roost site for lesser sandhill cranes and pro",
  "read": "2026-11-09",
  "sent": "The refuge is 3,236 acres of which the majority is a salt lake.",
  "url": "https://www.fws.gov/refuge/grulla/about-us",
  "why": "total-looking"
 },
 "ours": {
  "acres": 3231,
  "dissolved": {
   "after": 3231,
   "before": 6462,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 6462 -> 3231 acres",
  "pieces": [
   [
    3901,
    "Grulla National Wildlife Refuge",
    3231,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": "U.S",
 "pct": 0,
 "same_agency": false,
 "score": 7,
 "t": "National Wildlife Refuge",
 "verdict": "agree"
}
```

## US-8227 Jemez National Recreation Area
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-11-09",
 "handover": [],
 "n": "Jemez National Recreation Area",
 "official": null,
 "ours": {
  "acres": 57753,
  "manager": "",
  "pieces": [
   [
    "fsod53",
    "Jemez National Recreation Area",
    57753,
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
 "t": "National Recreation Area",
 "verdict": "unsure"
}
```

## US-7479 Kiowa National Grassland
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-11-09",
 "handover": [],
 "n": "Kiowa National Grassland",
 "official": null,
 "ours": {
  "acres": 137291,
  "manager": "",
  "pieces": [
   [
    2760,
    "Kiowa National Grassland",
    137291,
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
 "t": "National Grassland",
 "verdict": "unsure"
}
```

## US-11814 Salinas Pueblo Missions, Quarai unit, National Monument
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Salinas Pueblo Missions, Quarai unit, National Monument",
 "official": null,
 "ours": {
  "acres": 48,
  "manager": "",
  "pieces": [
   [
    3403,
    "Salinas Pueblo Missions NM, Quarai tract (PAD-US fee piece)",
    48,
    "reviewed (official tract: Quarai of Salinas Pueblo Missions "
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 5,
 "t": "National Monument",
 "verdict": "no size on page"
}
```

## US-11807 Simon Canyon ACEC BLM Special Recreation Management Area
```json
{
 "cause": "agency smaller: our outline may hold water, a lease or a neighbour tract",
 "checked": "2026-11-09",
 "handover": [],
 "n": "Simon Canyon ACEC BLM Special Recreation Management Area",
 "official": {
  "acres": 3900.0,
  "as": "3,900 acres",
  "clean": false,
  "line": "cern | New Mexico View Map In Full Screen Simon Canyon Area of Critical Environmental Concern (ACEC) is about 3,900 acres in size and is managed for semi-primitive forms of recreation including fishing, hiking, and backpacking. Dev",
  "read": "2026-11-09",
  "sent": "Simon Canyon Area of Critical Environmental Concern (ACEC) is about 3,900 acres in size and is managed for semi-primitive forms of recreation including fishing, hiking, and backpacking.",
  "url": "https://www.blm.gov/visit/simon-canyon-acec",
  "why": "total-looking"
 },
 "ours": {
  "acres": 4543,
  "dissolved": {
   "after": 3959,
   "before": 7866,
   "copies": 1,
   "key_union": 4543,
   "parts": 0,
   "records": 2,
   "summed": 3959,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 7866 -> 3959 acres",
  "pieces": [
   [
    "sgakh1693",
    "Simon Canyon",
    3959,
    "reviewed"
   ]
  ],
  "pin": "just outside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 16,
 "same_agency": false,
 "score": 5,
 "t": "BLM Special Recreation Management Area",
 "verdict": "off"
}
```

## US-2717 Sumner Lake State Park
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Sumner Lake State Park",
 "official": null,
 "ours": {
  "acres": 1152,
  "family_fold": "layers {'sgnmb': 1467, 'padus': 904}: one land in 2 layers, the sgnmb copy used (904 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgnmb26",
    "SUMNER LAKE",
    1467,
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

## US-11806 Johnson (Gordy's) Hill BLM Recreation Management Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Johnson (Gordy's) Hill BLM Recreation Management Area",
 "official": null,
 "ours": {
  "acres": 8358,
  "manager": "",
  "pieces": [
   [
    "rst14034",
    "Johnson (Gordy's) Hill North",
    4583,
    "name"
   ],
   [
    "rst13973",
    "Johnson (Gordy's) Hill South",
    3155,
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

## US-2701 Hyde Memorial State Park
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Hyde Memorial State Park",
 "official": null,
 "ours": {
  "acres": 352,
  "dissolved": {
   "after": 352,
   "before": 699,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 699 -> 352 acres",
  "pieces": [
   [
    "sgnmb13",
    "HYDE MEMORIAL",
    352,
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

## US-8621 Cabezon Wilderness Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Cabezon Wilderness Area",
 "official": null,
 "ours": {
  "acres": 0,
  "manager": "",
  "pieces": [],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "Wilderness Area",
 "verdict": "ours unknown"
}
```

## US-11866 Rio Bonito Acquired Lands: Salazar Tract, BLM Recreation Management Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Rio Bonito Acquired Lands: Salazar Tract, BLM Recreation Management Area",
 "official": null,
 "ours": {
  "acres": 1104,
  "manager": "",
  "pieces": [
   [
    "rst13994",
    "Rio Bonito Acquired Lands Tract 4",
    474,
    "name"
   ],
   [
    "rst14069",
    "Rio Bonito Acquired Lands Tract 1",
    261,
    "name"
   ],
   [
    "rst14010",
    "Rio Bonito Acquired Lands Tract 2",
    189,
    "name"
   ],
   [
    "rst14006",
    "Rio Bonito Acquired Lands Tract 3",
    180,
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

## US-0752 Pecos National Historical Park
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Pecos National Historical Park",
 "official": null,
 "ours": {
  "acres": 6451,
  "manager": "",
  "pieces": [
   [
    3237,
    "Pecos National Historical Park",
    6451,
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
 "t": "National Historical Park",
 "verdict": "no size on page"
}
```

## US-7878 Red Sands National Recreation Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Red Sands National Recreation Area",
 "official": null,
 "ours": {
  "acres": 33872,
  "dissolved": {
   "after": 33872,
   "before": 135488,
   "copies": 3,
   "parts": 0,
   "records": 4,
   "tracts": 1
  },
  "manager": "",
  "note": "4 joined records = 1 tracts: 3 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 135488 -> 33872 acres",
  "pieces": [
   [
    "sgnmc11047",
    "Red Sands OHV",
    33872,
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
 "t": "National Recreation Area",
 "verdict": "no size on page"
}
```
