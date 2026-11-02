# park truth checker: US-ND random sample of 12 (2026-11-01; seed = date + area, same rows for everyone)

Source file: `data/truth/US-ND.json`

## US-2761 Grahams Island State Park
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Grahams Island State Park",
 "official": null,
 "ours": {
  "acres": 1022,
  "dissolved": {
   "after": 959,
   "before": 2868,
   "copies": 2,
   "key_union": 1022,
   "parts": 0,
   "records": 3,
   "summed": 959,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 2868 -> 959 acres",
  "pieces": [
   [
    "sgndb73",
    "Grahams Island State Park",
    959,
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

## US-8567 Barron Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Barron Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 255,
  "dissolved": {
   "after": 427,
   "before": 854,
   "copies": 2,
   "key_union": 255,
   "parts": 0,
   "records": 4,
   "summed": 427,
   "tracts": 2
  },
  "manager": "",
  "note": "4 joined records = 2 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 854 -> 427 acres",
  "pieces": [
   [
    "ndw163",
    "Barron",
    387,
    "name"
   ],
   [
    "ndw249",
    "Barron",
    40,
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
 "t": "Wildlife Management Area",
 "verdict": "no size on page"
}
```

## US-2767 Rough Rider State Park
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Rough Rider State Park",
 "official": null,
 "ours": {
  "acres": 33,
  "dissolved": {
   "after": 63,
   "before": 126,
   "copies": 1,
   "key_union": 33,
   "parts": 0,
   "records": 2,
   "summed": 63,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 126 -> 63 acres",
  "pieces": [
   [
    "sgndb78",
    "Rough Rider State Park",
    63,
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
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-0438 Tewaukon National Wildlife Refuge
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 35,000 acres, no total words near it)",
 "checked": "2026-11-01",
 "handover": [],
 "n": "Tewaukon National Wildlife Refuge",
 "official": {
  "acres": 35000.0,
  "as": "35,000 acres",
  "clean": false,
  "line": "er wildlife. Managed by the U.S. Fish and Wildlife Service, the District helps conserve wildlife on more than 35,000 acres of land in the heart of the Prairie Pothole Region. These pristine... National Wildlife Refuge Pingree, ND Ch",
  "read": "2026-11-01",
  "sent": "Fish and Wildlife Service, the District helps conserve wildlife on more than 35,000 acres of land in the heart of the Prairie Pothole Region.",
  "url": "https://www.fws.gov/refuge/tewaukon/about-us",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 7010,
  "dissolved": {
   "after": 7010,
   "before": 14020,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 14020 -> 7010 acres",
  "pieces": [
   [
    4392,
    "Tewaukon National Wildlife Refuge",
    7010,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 80,
 "same_agency": false,
 "score": 7,
 "t": "National Wildlife Refuge",
 "verdict": "unsure"
}
```

## US-2760 Fort Stevenson State Park
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Fort Stevenson State Park",
 "official": null,
 "ours": {
  "acres": 493,
  "dissolved": {
   "after": 1110,
   "before": 1696,
   "copies": 1,
   "families": {
    "padus": 523,
    "sgndb": 587
   },
   "family_fold": 523,
   "family_used": "sgndb",
   "key_union": 493,
   "parts": 0,
   "records": 3,
   "summed": 587,
   "tracts": 2
  },
  "family_fold": "layers {'sgndb': 587, 'padus': 523}: one land in 2 layers, the sgndb copy used (523 ac of copies not added)",
  "manager": "",
  "note": "3 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1696 -> 1110 acres",
  "pieces": [
   [
    "sgndb69",
    "Fort Stevenson State Park",
    587,
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

## US-7702 Lone Tree Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Lone Tree Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 34685,
  "dissolved": {
   "after": 32327,
   "before": 96926,
   "copies": 4,
   "key_union": 34685,
   "parts": 3,
   "records": 9,
   "summed": 32327,
   "tracts": 2
  },
  "manager": "",
  "note": "9 joined records = 2 tracts: 4 copies of a tract (same acres, another layer) and 3 fee tracts under a designation record folded; summed 96926 -> 32327 acres",
  "pieces": [
   [
    215512,
    "Lonetree",
    32248,
    "name"
   ],
   [
    "ndw210",
    "Lonetree",
    79,
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

## US-0436 Slade National Wildlife Refuge
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Slade National Wildlife Refuge",
 "official": {
  "acres": 3000.0,
  "as": "3,000 acre",
  "clean": false,
  "line": "able were later removed and used in the war effort during World War II. Mr. Slade died in 1941 and willed his 3,000 acre club to the U.S. Fish and Wildlife Service to be used as a refuge. The Refuge was thus named Slade National W",
  "read": "2026-11-01",
  "sent": "Slade died in 1941 and willed his 3,000 acre club to the U.S.",
  "url": "https://www.fws.gov/refuge/slade/about-us",
  "why": "history"
 },
 "ours": {
  "acres": 2589,
  "dissolved": {
   "after": 2999,
   "before": 5998,
   "copies": 1,
   "key_union": 2589,
   "parts": 0,
   "records": 2,
   "summed": 2999,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 5998 -> 2999 acres",
  "pieces": [
   [
    4346,
    "Slade National Wildlife Refuge",
    2999,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 14,
 "same_agency": false,
 "score": 8,
 "t": "National Wildlife Refuge",
 "verdict": "agree"
}
```

## US-8563 Apple Creek Bottoms Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Apple Creek Bottoms Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 607,
  "dissolved": {
   "after": 1081,
   "before": 2162,
   "copies": 1,
   "key_union": 607,
   "parts": 0,
   "records": 2,
   "summed": 1081,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 2162 -> 1081 acres",
  "pieces": [
   [
    "ndw179",
    "Apple Creek Bottoms",
    1081,
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
 "t": "Wildlife Management Area",
 "verdict": "no size on page"
}
```

## US-0428 J. Clark Salyer Wetland Management District
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 8,354 square miles, a statewide / agency-wide total (over a million acres) on a park that is not a big federal unit)",
 "checked": "2026-11-01",
 "handover": [],
 "n": "J. Clark Salyer Wetland Management District",
 "official": {
  "acres": 5346560.0,
  "as": "8,354 square miles",
  "clean": false,
  "line": "John Clark Salyer II, the \"Father of the National Wildlife Refuge System,\" the district covers approximately 8,354 square miles across six counties. Its mission is to conserve native species and provide permanent secure habitat that sust",
  "read": "2026-11-01",
  "sent": "Named after John Clark Salyer II, the \"Father of the National Wildlife Refuge System,\" the district covers approximately 8,354 square miles across six counties.",
  "url": "https://www.fws.gov/refuge/j_clark_salyer_wmd/",
  "why": "a statewide / agency-wide total (over a million acres) on a park that is not a big federal unit"
 },
 "ours": {
  "acres": 22431,
  "dissolved": {
   "after": 29476,
   "before": 34003,
   "copies": 11,
   "key_union": 22431,
   "parts": 9,
   "records": 165,
   "summed": 29476,
   "tracts": 145
  },
  "manager": "",
  "note": "165 joined records = 145 tracts: 11 copies of a tract (same acres, another layer) and 9 fee tracts under a designation record folded; summed 34003 -> 29476 acres",
  "pieces": [
   [
    "fws2592",
    "Round Lake WPA, Pierce County Waterfowl Production Area",
    1727,
    "reviewed: the district = FWS fee (owned) tracts only, easeme"
   ],
   [
    "fws2580",
    "Horseshoe Lake WPA, Pierce County Waterfowl Production Area",
    1482,
    "reviewed: the district = FWS fee (owned) tracts only, easeme"
   ],
   [
    "fws2631",
    "LaFromboise WPA, Rolette County Waterfowl Production Area",
    959,
    "reviewed: the district = FWS fee (owned) tracts only, easeme"
   ],
   [
    "fws2567",
    "Christenson Lake WPA, Pierce County Waterfowl Production Area",
    907,
    "reviewed: the district = FWS fee (owned) tracts only, easeme"
   ],
   [
    "fws2543",
    "Mikes Peak WPA, Mchenry County Waterfowl Production Area",
    858,
    "reviewed: the district = FWS fee (owned) tracts only, easeme"
   ],
   [
    "fws2620",
    "Baxstrom WPA, Rolette County Waterfowl Production Area",
    839,
    "reviewed: the district = FWS fee (owned) tracts only, easeme"
   ],
   [
    "fws2609",
    "Wolford WPA, Pierce County Waterfowl P
```

## US-2768 Turtle River State Park
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Turtle River State Park",
 "official": null,
 "ours": {
  "acres": 775,
  "dissolved": {
   "after": 1476,
   "before": 2251,
   "copies": 1,
   "families": {
    "padus": 701,
    "sgndb": 775
   },
   "family_fold": 701,
   "family_used": "sgndb",
   "parts": 0,
   "records": 3,
   "tracts": 2
  },
  "family_fold": "layers {'sgndb': 775, 'padus': 701}: one land in 2 layers, the sgndb copy used (701 ac of copies not added)",
  "manager": "",
  "note": "3 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 2251 -> 1476 acres",
  "pieces": [
   [
    "sgndb79",
    "Turtle River State Park",
    775,
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

## US-7707 Maclean Bottoms Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Maclean Bottoms Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 6599,
  "dissolved": {
   "after": 6955,
   "before": 13910,
   "copies": 1,
   "key_union": 6599,
   "parts": 0,
   "records": 2,
   "summed": 6955,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 13910 -> 6955 acres",
  "pieces": [
   [
    "ndw342",
    "MacLean Bottoms",
    6955,
    "name"
   ]
  ],
  "pin": "well outside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 5,
 "t": "Wildlife Management Area",
 "verdict": "no size on page"
}
```

## US-8575 Dawson Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Dawson Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 2937,
  "dissolved": {
   "after": 2937,
   "before": 8800,
   "copies": 2,
   "parts": 0,
   "records": 3,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 8800 -> 2937 acres",
  "pieces": [
   [
    "ndw90",
    "Dawson",
    2937,
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
 "t": "Wildlife Management Area",
 "verdict": "no size on page"
}
```
