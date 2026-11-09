# park truth checker: US-CO random sample of 12 (2026-11-09; seed = date + area, same rows for everyone)

Source file: `data/truth/US-CO.json`

## US-9666 Rosemont State Wildlife Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Rosemont State Wildlife Area",
 "official": null,
 "ours": {
  "acres": 374,
  "dissolved": {
   "after": 356,
   "before": 1068,
   "copies": 2,
   "key_union": 374,
   "parts": 0,
   "records": 3,
   "summed": 356,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1068 -> 356 acres",
  "pieces": [
   [
    188951,
    "Rosemont Reservoir State Wildlife Area",
    356,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "State Wildlife Area",
 "verdict": "no size on page"
}
```

## US-12187 Roaring Fork State Wildlife Area
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 43 acres, no total words near it)",
 "checked": "2026-11-09",
 "handover": [],
 "n": "Roaring Fork State Wildlife Area",
 "official": {
  "acres": 43.0,
  "as": "43 acres",
  "clean": false,
  "line": "d check current hunting, fishing and land use regulations when planning to visit a State Wildlife Area. Acres 43 acres. Elevation min. 5,884 ft - max 6,120 ft GMU 43 Hunting Opportunities No hunting opportunities available Activ",
  "read": "2026-11-09",
  "sent": "43 acres.",
  "url": "https://cpw.state.co.us/state-wildlife-areas/roaring-forkgianinetti-swa-fishing-lease",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 3,
  "manager": "",
  "pieces": [
   [
    189236,
    "Roaring Fork State Wildlife Area - Wheeler Parcel",
    3,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 93,
 "same_agency": false,
 "score": 5,
 "t": "State Wildlife Area",
 "verdict": "unsure"
}
```

## US-11899 South Republican State Wildlife Area
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 18365 acres, no total words near it)",
 "checked": "2026-11-09",
 "handover": [],
 "n": "South Republican State Wildlife Area",
 "official": {
  "acres": 18365.0,
  "as": "18365 acres",
  "clean": false,
  "line": "chThreshold\" : 5, \"useCSS\" : true, \"useTransform\" : true, \"centerPadding\":\"0px\", \"infinite\" : false }'> Acres 18365 acres. Elevation min. 3,509 ft - max 3,867 ft GMU 103, 109 Hunting Opportunities Bobwhite quail, Deer, Dove, Pheasa",
  "read": "2026-11-09",
  "sent": "18365 acres.",
  "url": "https://cpw.state.co.us/state-wildlife-areas/south-republican-swa",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 23448,
  "dissolved": {
   "after": 27505,
   "before": 48925,
   "copies": 1,
   "families": {
    "padus": 6085,
    "sgcoa": 21420
   },
   "family_fold": 6085,
   "family_used": "sgcoa",
   "key_union": 23448,
   "parts": 0,
   "records": 5,
   "summed": 21420,
   "tracts": 4
  },
  "family_fold": "layers {'sgcoa': 21420, 'padus': 6085}: one land in 2 layers, the sgcoa copy used (6,085 ac of copies not added)",
  "manager": "",
  "note": "5 joined records = 4 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 48925 -> 27505 acres",
  "pieces": [
   [
    "sgcoa282",
    "South Republican SWA",
    21420,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 28,
 "same_agency": false,
 "score": 7,
 "t": "State Wildlife Area",
 "verdict": "unsure"
}
```

## US-11940 Simpson Ponds State Wildlife Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Simpson Ponds State Wildlife Area",
 "official": {
  "acres": 44.0,
  "as": "44 acres",
  "clean": false,
  "line": "d check current hunting, fishing and land use regulations when planning to visit a State Wildlife Area. Acres 44 acres. Elevation min. 4,870 ft - max 4,887 ft GMU 20 Hunting Opportunities Dove, Waterfowl Fishing Opportunities Wa",
  "read": "2026-11-09",
  "sent": "44 acres.",
  "url": "https://cpw.state.co.us/state-wildlife-areas/simpson-ponds-swa",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 44,
  "dissolved": {
   "after": 68,
   "before": 204,
   "copies": 2,
   "key_union": 44,
   "parts": 0,
   "records": 3,
   "summed": 68,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 204 -> 68 acres",
  "pieces": [
   [
    189252,
    "Simpson Ponds State Wildlife Area",
    68,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 0,
 "same_agency": false,
 "score": 7,
 "t": "State Wildlife Area",
 "verdict": "agree"
}
```

## US-11915 Hubbard Mesa OHV BLM Special Recreation Management Area
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-09",
 "handover": [],
 "n": "Hubbard Mesa OHV BLM Special Recreation Management Area",
 "official": {
  "acres": 2460.0,
  "as": "2,460 acres",
  "clean": false,
  "line": "hicle use. Hubbard Mesa was designated as an Open Area in 2007 in the Roan Plateau Management Plan. It offers 2,460 acres with 50 miles of single track, ATV and Jeep trails. This is a high use area primarily for OHV's but also rece",
  "read": "2026-11-09",
  "sent": "It offers 2,460 acres with 50 miles of single track, ATV and Jeep trails.",
  "url": "https://www.blm.gov/visit/roan-plateau-hubbard-mesa",
  "why": "total-looking"
 },
 "ours": {
  "acres": 1730,
  "dissolved": {
   "after": 2324,
   "before": 6972,
   "copies": 2,
   "key_union": 1730,
   "parts": 0,
   "records": 3,
   "summed": 2324,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 6972 -> 2324 acres",
  "pieces": [
   [
    "rma10934",
    "Hubbard Mesa OHV Area",
    2324,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 30,
 "same_agency": false,
 "score": 6,
 "t": "BLM Special Recreation Management Area",
 "verdict": "off"
}
```

## US-9614 Big Meadows Reservoir State Wildlife Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Big Meadows Reservoir State Wildlife Area",
 "official": null,
 "ours": {
  "acres": 70,
  "dissolved": {
   "after": 117,
   "before": 351,
   "copies": 2,
   "key_union": 70,
   "parts": 0,
   "records": 3,
   "summed": 117,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 351 -> 117 acres",
  "pieces": [
   [
    "cow109",
    "Big Meadows Reservoir SWA",
    117,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "State Wildlife Area",
 "verdict": "no size on page"
}
```

## US-12172 James Mark Jones State Wildlife Area
```json
{
 "checked": "2026-11-09",
 "handover": [
  {
   "date_hint": "2002",
   "kind": "renamed",
   "line": "te Wildlife Area. In 2002, Reinecker Ridge and Mud Springs SWAs were combined into one property and renamed the James Mark Jones SWA. The name honors Jim Jones, an outstanding Colorado Division of Wildlife employee who passed away i",
   "owner_now": null,
   "src": "https://cpw.state.co.us/state-wildlife-areas/james-mark-jones-swa",
   "why": "the park's page (data/parkinfo)"
  }
 ],
 "n": "James Mark Jones State Wildlife Area",
 "official": {
  "acres": 17429.0,
  "as": "17429 acres",
  "clean": false,
  "line": "nors Jim Jones, an outstanding Colorado Division of Wildlife employee who passed away in February 1999. Acres 17429 acres. Elevation min. 9,006 ft - max 10,532 ft GMU 50 Hunting Opportunities Deer, Elk, Pronghorn, Small game Activi",
  "read": "2026-11-09",
  "sent": "17429 acres.",
  "url": "https://cpw.state.co.us/state-wildlife-areas/james-mark-jones-swa",
  "why": "total-looking"
 },
 "ours": {
  "acres": 17678,
  "dissolved": {
   "after": 22905,
   "before": 40583,
   "copies": 1,
   "families": {
    "padus": 5227,
    "sgcoa": 17678
   },
   "family_fold": 5227,
   "family_used": "sgcoa",
   "parts": 0,
   "records": 3,
   "tracts": 2
  },
  "family_fold": "layers {'sgcoa': 17678, 'padus': 5227}: one land in 2 layers, the sgcoa copy used (5,227 ac of copies not added)",
  "manager": "",
  "note": "3 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 40583 -> 22905 acres",
  "pieces": [
   [
    "sgcoa161",
    "James Mark Jones SWA",
    17678,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 1,
 "same_agency": false,
 "score": 8,
 "t": "State Wildlife Area",
 "verdict": "agree"
}
```

## US-9649 Fort Lyon State Wildlife Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Fort Lyon State Wildlife Area",
 "official": null,
 "ours": {
  "acres": 388,
  "dissolved": {
   "after": 523,
   "before": 1569,
   "copies": 2,
   "key_union": 388,
   "parts": 0,
   "records": 3,
   "summed": 523,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1569 -> 523 acres",
  "pieces": [
   [
    "cow346",
    "Fort Lyon SWA",
    523,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "State Wildlife Area",
 "verdict": "no size on page"
}
```

## US-9670 Sedgwick Bar State Wildlife Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Sedgwick Bar State Wildlife Area",
 "official": null,
 "ours": {
  "acres": 748,
  "dissolved": {
   "after": 895,
   "before": 2685,
   "copies": 2,
   "key_union": 748,
   "parts": 0,
   "records": 3,
   "summed": 895,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 2685 -> 895 acres",
  "pieces": [
   [
    189250,
    "Sedgwick Bar State Wildlife Area",
    895,
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
 "t": "State Wildlife Area",
 "verdict": "no size on page"
}
```

## US-11886 Walker State Wildlife Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Walker State Wildlife Area",
 "official": {
  "acres": 351.0,
  "as": "351 acres",
  "clean": false,
  "line": "contacting Colorado Parks and Wildlife, 711 Independent Dr., Grand Junction, CO 81504, (970) 255-6100. Acres 351 acres. Elevation min. 4,500 ft - max 4,572 ft GMU 30, 40 Hunting Opportunities No hunting opportunities available F",
  "read": "2026-11-09",
  "sent": "351 acres.",
  "url": "https://cpw.state.co.us/state-wildlife-areas/walker-swa",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 299,
  "dissolved": {
   "after": 491,
   "before": 1467,
   "copies": 2,
   "key_union": 299,
   "parts": 0,
   "records": 3,
   "summed": 491,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1467 -> 491 acres",
  "pieces": [
   [
    189277,
    "Walker State Wildlife Area",
    491,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 15,
 "same_agency": false,
 "score": 7,
 "t": "State Wildlife Area",
 "verdict": "agree"
}
```

## US-11908 North Fruita Desert BLM Special Recreation Management Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "North Fruita Desert BLM Special Recreation Management Area",
 "official": null,
 "ours": {
  "acres": 11552,
  "dissolved": {
   "after": 11552,
   "before": 23104,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 23104 -> 11552 acres",
  "pieces": [
   [
    "rst10937",
    "North Fruita Desert",
    11552,
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
 "t": "BLM Special Recreation Management Area",
 "verdict": "no size on page"
}
```

## US-9609 Basalt State Wildlife Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Basalt State Wildlife Area",
 "official": null,
 "ours": {
  "acres": 5853,
  "dissolved": {
   "after": 4802,
   "before": 14376,
   "copies": 4,
   "key_union": 5853,
   "parts": 0,
   "records": 6,
   "summed": 4802,
   "tracts": 2
  },
  "manager": "",
  "note": "6 joined records = 2 tracts: 4 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 14376 -> 4802 acres",
  "pieces": [
   [
    "sgcoa12",
    "Basalt SWA",
    4707,
    "name"
   ],
   [
    "cow92",
    "Basalt SWA - Schuck Unit",
    95,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 2
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "State Wildlife Area",
 "verdict": "no size on page"
}
```
