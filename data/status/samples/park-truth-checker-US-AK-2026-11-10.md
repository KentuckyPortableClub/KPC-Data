# park truth checker: US-AK random sample of 12 (2026-11-10; seed = date + area, same rows for everyone)

Source file: `data/truth/US-AK.json`

## US-0157 Yukon Flats National Wildlife Refuge
```json
{
 "checked": "2026-11-10",
 "handover": [],
 "n": "Yukon Flats National Wildlife Refuge",
 "official": {
  "acres": 8630000.0,
  "as": "8.63 million acres",
  "clean": true,
  "line": "he third largest wildlife refuge in the United States, encompassing approximately 11.1 million acres of land (8.63 million acres in federal ownership). Extending 220 miles east-west along the Arctic Circle, the refuge lies between the Bro",
  "read": "2026-11-10",
  "sent": "Yukon Flats is the third largest wildlife refuge in the United States, encompassing approximately 11.1 million acres of land (8.63 million acres in federal ownership).",
  "url": "https://www.fws.gov/refuge/yukon-flats/about-us",
  "why": "clean total"
 },
 "ours": {
  "acres": 9097653,
  "dissolved": {
   "after": 9097653,
   "before": 18194251,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 18194251 -> 9097653 acres",
  "pieces": [
   [
    4498,
    "Yukon Flats National Wildlife Refuge",
    9097653,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 5,
 "same_agency": false,
 "score": 7,
 "t": "National Wildlife Refuge",
 "verdict": "agree"
}
```

## US-7205 Buskin River State Recreation Site
```json
{
 "checked": "2026-11-10",
 "handover": [],
 "n": "Buskin River State Recreation Site",
 "official": null,
 "ours": {
  "acres": 124,
  "dissolved": {
   "after": 203,
   "before": 609,
   "copies": 2,
   "key_union": 124,
   "parts": 0,
   "records": 3,
   "summed": 203,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 609 -> 203 acres",
  "pieces": [
   [
    "sgaka14",
    "Buskin River State Recreation Site",
    203,
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
 "t": "State Recreation Site",
 "verdict": "no size on page"
}
```

## US-0644 Bering Land Bridge National Preserve
```json
{
 "checked": "2026-11-10",
 "handover": [],
 "n": "Bering Land Bridge National Preserve",
 "official": null,
 "ours": {
  "acres": 2650935,
  "manager": "",
  "pieces": [
   [
    3295,
    "Bering Land Bridge National Preserve",
    2650935,
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
 "t": "National Preserve",
 "verdict": "no size on page"
}
```

## US-4538 Misty Fjords National Monument
```json
{
 "checked": "2026-11-10",
 "handover": [],
 "n": "Misty Fjords National Monument",
 "official": {
  "acres": 2200000.0,
  "as": "2,200,000 acres",
  "clean": false,
  "line": "s Photos and Videos Recreation Misty Fjords National Monument In 1978, President Jimmy Carter proclaimed over 2,200,000 acres as the Misty Fjords National Monument. In 1980, this acreage got reduced to 2,142,243 acres but was now congr",
  "read": "2026-11-10",
  "sent": "In 1978, President Jimmy Carter proclaimed over 2,200,000 acres as the Misty Fjords National Monument.",
  "url": "https://www.fs.usda.gov/visit/destination/misty-fjords-national-monument",
  "why": "total-looking"
 },
 "ours": {
  "acres": 2294702,
  "family_fold": "layers {'fsod': 2294702, 'wld': 2144883}: one land in 2 layers, the fsod copy used (2,144,883 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "fsod170",
    "Misty Fjords National Monument",
    2294702,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 4,
 "same_agency": false,
 "score": 7,
 "t": "National Monument",
 "verdict": "agree"
}
```

## US-7211 Finger Lake State Recreation Site
```json
{
 "checked": "2026-11-10",
 "handover": [],
 "n": "Finger Lake State Recreation Site",
 "official": null,
 "ours": {
  "acres": 25,
  "dissolved": {
   "after": 48,
   "before": 144,
   "copies": 2,
   "key_union": 25,
   "parts": 0,
   "records": 3,
   "summed": 48,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 144 -> 48 acres",
  "pieces": [
   [
    "sgaka126",
    "Finger Lake State Recreation Site",
    48,
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
 "t": "State Recreation Site",
 "verdict": "no size on page"
}
```

## US-0153 Selawik National Wildlife Refuge
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-11-10",
 "handover": [],
 "n": "Selawik National Wildlife Refuge",
 "official": null,
 "ours": {
  "acres": 2718908,
  "dissolved": {
   "after": 2718908,
   "before": 5437599,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 5437599 -> 2718908 acres",
  "pieces": [
   [
    5280,
    "Selawik National Wildlife Refuge",
    2718908,
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

## US-7212 Independence Mine State Historical Park
```json
{
 "checked": "2026-11-10",
 "handover": [],
 "n": "Independence Mine State Historical Park",
 "official": null,
 "ours": {
  "acres": 1096,
  "dissolved": {
   "after": 1030,
   "before": 2692,
   "copies": 2,
   "families": {
    "padus": 199,
    "sgaka": 831
   },
   "family_fold": 199,
   "family_used": "sgaka",
   "key_union": 1096,
   "parts": 0,
   "records": 4,
   "summed": 831,
   "tracts": 2
  },
  "family_fold": "layers {'sgaka': 831, 'padus': 199}: one land in 2 layers, the sgaka copy used (199 ac of copies not added)",
  "manager": "",
  "note": "4 joined records = 2 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 2692 -> 1030 acres",
  "pieces": [
   [
    "sgaka69",
    "Independence Mine State Historical Park",
    831,
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
 "t": "State Historical Park",
 "verdict": "no size on page"
}
```

## US-7203 Starski State Recreation Site
```json
{
 "checked": "2026-11-10",
 "handover": [],
 "n": "Starski State Recreation Site",
 "official": null,
 "ours": {
  "acres": 15,
  "dissolved": {
   "after": 37,
   "before": 111,
   "copies": 2,
   "key_union": 15,
   "parts": 0,
   "records": 3,
   "summed": 37,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 111 -> 37 acres",
  "pieces": [
   [
    "sgaka41",
    "Stariski State Recreation Site",
    37,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 5,
 "t": "State Recreation Site",
 "verdict": "no size on page"
}
```

## US-7192 Blueberry Lake State Recreation Site
```json
{
 "checked": "2026-11-10",
 "handover": [],
 "n": "Blueberry Lake State Recreation Site",
 "official": null,
 "ours": {
  "acres": 264,
  "dissolved": {
   "after": 511,
   "before": 1533,
   "copies": 2,
   "key_union": 264,
   "parts": 0,
   "records": 3,
   "summed": 511,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1533 -> 511 acres",
  "pieces": [
   [
    "sgaka135",
    "Blueberry Lake State Recreation Site",
    511,
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
 "t": "State Recreation Site",
 "verdict": "no size on page"
}
```

## US-7248 Settler's Cove State Recreation Site
```json
{
 "checked": "2026-11-10",
 "handover": [],
 "n": "Settler's Cove State Recreation Site",
 "official": null,
 "ours": {
  "acres": 124,
  "dissolved": {
   "after": 260,
   "before": 780,
   "copies": 2,
   "key_union": 124,
   "parts": 0,
   "records": 3,
   "summed": 260,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 780 -> 260 acres",
  "pieces": [
   [
    "sgaka53",
    "Settlers Cove State Recreation Site",
    260,
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
 "t": "State Recreation Site",
 "verdict": "no size on page"
}
```

## US-11839 Chena Pump Wayside State Recreation Site
```json
{
 "checked": "2026-11-10",
 "handover": [],
 "n": "Chena Pump Wayside State Recreation Site",
 "official": null,
 "ours": {
  "acres": 16,
  "dissolved": {
   "after": 31,
   "before": 93,
   "copies": 2,
   "key_union": 16,
   "parts": 0,
   "records": 3,
   "summed": 31,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 93 -> 31 acres",
  "pieces": [
   [
    "sgaka58",
    "Chena Pump State Recreation Site",
    31,
    "words"
   ]
  ],
  "pin": "just outside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 5,
 "t": "State Recreation Site",
 "verdict": "no size on page"
}
```

## US-7228 Chena River State Recreation Area
```json
{
 "checked": "2026-11-10",
 "handover": [],
 "n": "Chena River State Recreation Area",
 "official": null,
 "ours": {
  "acres": 242004,
  "dissolved": {
   "after": 242004,
   "before": 958134,
   "copies": 3,
   "parts": 0,
   "records": 4,
   "tracts": 1
  },
  "manager": "",
  "note": "4 joined records = 1 tracts: 3 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 958134 -> 242004 acres",
  "pieces": [
   [
    165901,
    "Chena River State Recreation Area",
    242004,
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
 "t": "State Recreation Area",
 "verdict": "no size on page"
}
```
