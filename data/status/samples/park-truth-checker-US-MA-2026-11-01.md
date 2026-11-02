# park truth checker: US-MA random sample of 12 (2026-11-01; seed = date + area, same rows for everyone)

Source file: `data/truth/US-MA.json`

## US-8398 Southern New England Trunkline Trail State Trail
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Southern New England Trunkline Trail State Trail",
 "official": null,
 "ours": {
  "acres": 371,
  "dissolved": {
   "after": 133,
   "before": 308,
   "copies": 2,
   "key_union": 371,
   "parts": 14,
   "records": 23,
   "summed": 133,
   "tracts": 7
  },
  "manager": "",
  "note": "23 joined records = 7 tracts: 2 copies of a tract (same acres, another layer) and 14 fee tracts under a designation record folded; summed 308 -> 133 acres",
  "pieces": [
   [
    "sgmaa690495",
    "Southern New England Trunkline Trail",
    100,
    "name"
   ],
   [
    "sgmaa700256",
    "Southern New England Trunkline Trail",
    9,
    "name"
   ],
   [
    "sgmaa681486",
    "Southern New England Trunkline Trail",
    6,
    "name"
   ],
   [
    "sgmaa681490",
    "Southern New England Trunkline Trail",
    6,
    "name"
   ],
   [
    "sgmaa646428",
    "Southern New England Trunkline Trail",
    5,
    "name"
   ],
   [
    "sgmaa675464",
    "Southern New England Trunkline Trail",
    5,
    "name"
   ],
   [
    "sgmaa646430",
    "Southern New England Trunkline Trail",
    2,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 15
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "State Trail",
 "verdict": "no size on page"
}
```

## US-11563 Quisset Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Quisset Wildlife Management Area",
 "official": {
  "acres": 425.0,
  "as": "425 acres",
  "clean": false,
  "line": "re open to the public for fishing, hunting, trapping, hiking, and wildlife viewing. Towns: Blackstone, Mendon Acreage: 425 Wildlife Management Zone : 9 Description Quisset WMA contains mixed hardwood and conifer forests. This propert",
  "read": "2026-11-01",
  "sent": "Acreage: 425 Wildlife Management Zone : 9",
  "url": "https://www.mass.gov/info-details/quisset-wma",
  "why": "total-looking"
 },
 "ours": {
  "acres": 488,
  "dissolved": {
   "after": 369,
   "before": 888,
   "copies": 2,
   "families": {
    "padus": 276,
    "sgmaa": 93
   },
   "family_fold": 93,
   "family_used": "padus",
   "key_union": 488,
   "parts": 3,
   "records": 10,
   "summed": 276,
   "tracts": 5
  },
  "family_fold": "layers {'padus': 276, 'sgmaa': 93}: one land in 2 layers, the padus copy used (93 ac of copies not added)",
  "manager": "",
  "note": "10 joined records = 5 tracts: 2 copies of a tract (same acres, another layer) and 3 fee tracts under a designation record folded; summed 888 -> 369 acres",
  "pieces": [
   [
    56057,
    "Quisset Wildlife Management Area",
    242,
    "name"
   ],
   [
    56060,
    "Quisset Wildlife Management Area",
    34,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 2
 },
 "owner_now": null,
 "pct": 15,
 "same_agency": false,
 "score": 8,
 "t": "Wildlife Management Area",
 "verdict": "agree"
}
```

## US-11498 Birch Hill Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Birch Hill Wildlife Management Area",
 "official": {
  "acres": 4560.6,
  "as": "4,560.55 acres",
  "clean": false,
  "line": "public for fishing, hunting, trapping, hiking, and wildlife viewing. Towns: Royalston, Templeton, Winchendon Acreage: 4,560.55 Wildlife Management Zone : 5 Description Birch Hill WMA is made up of several parcels totaling over 4,500 acre",
  "read": "2026-11-01",
  "sent": "Acreage: 4,560.55 Wildlife Management Zone : 5",
  "url": "https://www.mass.gov/info-details/birch-hill-wma",
  "why": "total-looking"
 },
 "ours": {
  "acres": 4468,
  "dissolved": {
   "after": 2573,
   "before": 10291,
   "copies": 29,
   "families": {
    "padus": 1645,
    "sgmaa": 928
   },
   "family_fold": 928,
   "family_used": "padus",
   "key_union": 4468,
   "parts": 51,
   "records": 86,
   "summed": 1645,
   "tracts": 6
  },
  "family_fold": "layers {'padus': 1645, 'sgmaa': 928}: one land in 2 layers, the padus copy used (928 ac of copies not added)",
  "manager": "",
  "note": "86 joined records = 6 tracts: 29 copies of a tract (same acres, another layer) and 51 fee tracts under a designation record folded; summed 10291 -> 2573 acres",
  "pieces": [
   [
    55200,
    "Birch Hill Wildlife Management Area",
    1422,
    "name"
   ],
   [
    55179,
    "Birch Hill Wildlife Management Area",
    139,
    "name"
   ],
   [
    55203,
    "Birch Hill Wildlife Management Area",
    84,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 3
 },
 "owner_now": null,
 "pct": 2,
 "same_agency": false,
 "score": 7,
 "t": "Wildlife Management Area",
 "verdict": "agree"
}
```

## US-4714 Chester-Blandford State Forest
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Chester-Blandford State Forest",
 "official": null,
 "ours": {
  "acres": 3596,
  "dissolved": {
   "after": 4624,
   "before": 5991,
   "copies": 2,
   "families": {
    "padus": 2792,
    "sgmaa": 1832
   },
   "family_fold": 1832,
   "family_used": "padus",
   "key_union": 3596,
   "parts": 27,
   "records": 41,
   "summed": 2792,
   "tracts": 12
  },
  "family_fold": "layers {'padus': 2792, 'sgmaa': 1832}: one land in 2 layers, the padus copy used (1,832 ac of copies not added)",
  "manager": "",
  "note": "41 joined records = 12 tracts: 2 copies of a tract (same acres, another layer) and 27 fee tracts under a designation record folded; summed 5991 -> 4624 acres",
  "pieces": [
   [
    60079,
    "Chester-Blandford State Forest",
    2792,
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
 "t": "State Forest",
 "verdict": "no size on page"
}
```

## US-11551 Moose Hill Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Moose Hill Wildlife Management Area",
 "official": {
  "acres": 594.0,
  "as": "594 acres",
  "clean": false,
  "line": "to the public for fishing, hunting, trapping, hiking, and wildlife viewing. Towns: Leicester, Paxton, Spencer Acreage: 594 Wildlife Management Zone : 8 Description Moose Hill WMA features rolling hardwood ridges and a large wetland c",
  "read": "2026-11-01",
  "sent": "Acreage: 594 Wildlife Management Zone : 8",
  "url": "https://www.mass.gov/info-details/moose-hill-wma",
  "why": "total-looking"
 },
 "ours": {
  "acres": 508,
  "dissolved": {
   "after": 351,
   "before": 1254,
   "copies": 5,
   "families": {
    "padus": 323,
    "sgmaa": 28
   },
   "family_fold": 28,
   "family_used": "padus",
   "key_union": 508,
   "parts": 11,
   "records": 20,
   "summed": 323,
   "tracts": 4
  },
  "family_fold": "layers {'padus': 323, 'sgmaa': 28}: one land in 2 layers, the padus copy used (28 ac of copies not added)",
  "manager": "",
  "note": "20 joined records = 4 tracts: 5 copies of a tract (same acres, another layer) and 11 fee tracts under a designation record folded; summed 1254 -> 351 acres",
  "pieces": [
   [
    55815,
    "Moose Hill Wildlife Management Area",
    309,
    "name"
   ],
   [
    55814,
    "Moose Hill Wildlife Management Area",
    14,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 2
 },
 "owner_now": null,
 "pct": 14,
 "same_agency": false,
 "score": 7,
 "t": "Wildlife Management Area",
 "verdict": "agree"
}
```

## US-11625 Erwin S. Wilder Wildlife Management Area
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-01",
 "handover": [],
 "n": "Erwin S. Wilder Wildlife Management Area",
 "official": {
  "acres": 651.0,
  "as": "651 acres",
  "clean": false,
  "line": ") are open to the public for fishing, hunting, trapping, hiking, and wildlife viewing. Towns: Norton, Taunton Acreage: 651 Wildlife Management Zone : 11 Waterfowl Zone : Central Description The forested upland areas of Erwin S. Wilde",
  "read": "2026-11-01",
  "sent": "Acreage: 651 Wildlife Management Zone : 11",
  "url": "https://www.mass.gov/info-details/erwin-s-wilder-wma",
  "why": "total-looking"
 },
 "ours": {
  "acres": 317,
  "dissolved": {
   "after": 437,
   "before": 935,
   "copies": 7,
   "key_union": 317,
   "parts": 6,
   "records": 20,
   "summed": 437,
   "tracts": 7
  },
  "manager": "",
  "note": "20 joined records = 7 tracts: 7 copies of a tract (same acres, another layer) and 6 fee tracts under a designation record folded; summed 935 -> 437 acres",
  "pieces": [
   [
    54789,
    "Erwin S. Wilder Wildlife Management Area",
    291,
    "name"
   ],
   [
    54793,
    "Erwin S. Wilder Wildlife Management Area",
    69,
    "name"
   ],
   [
    54794,
    "Erwin S. Wilder Wildlife Management Area",
    40,
    "name"
   ],
   [
    54787,
    "Erwin S. Wilder Wildlife Management Area",
    17,
    "name"
   ],
   [
    "sgmaa641758",
    "Erwin S. Wilder WMA",
    14,
    "name"
   ],
   [
    54791,
    "Erwin S. Wilder Wildlife Management Area",
    5,
    "name"
   ],
   [
    "sgmaa641656",
    "Erwin S. Wilder WMA",
    1,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 51,
 "same_agency": false,
 "score": 5,
 "t": "Wildlife Management Area",
 "verdict": "off"
}
```

## US-11596 Hauk Swamp Wildlife Management Area
```json
{
 "cause": "our union: one of our pieces alone matches the agency (double count?)",
 "checked": "2026-11-01",
 "handover": [],
 "n": "Hauk Swamp Wildlife Management Area",
 "official": {
  "acres": 61.0,
  "as": "61 acres",
  "clean": false,
  "line": "s (WMA) are open to the public for fishing, hunting, trapping, hiking, and wildlife viewing. Towns: Dunstable Acreage: 61 Wildlife Management Zone : 9 Waterfowl Zone : Central Description This property is nearly completely spruce/fi",
  "read": "2026-11-01",
  "sent": "Acreage: 61 Wildlife Management Zone : 9",
  "url": "https://www.mass.gov/info-details/hauk-swamp-wma",
  "why": "total-looking"
 },
 "ours": {
  "acres": 82,
  "dissolved": {
   "after": 62,
   "before": 124,
   "copies": 2,
   "key_union": 82,
   "parts": 0,
   "records": 4,
   "summed": 62,
   "tracts": 2
  },
  "manager": "",
  "note": "4 joined records = 2 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 124 -> 62 acres",
  "pieces": [
   [
    54832,
    "Hauk Swamp Wildlife Management Area",
    55,
    "name"
   ],
   [
    54833,
    "Hauk Swamp Wildlife Management Area",
    7,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 34,
 "same_agency": false,
 "score": 5,
 "t": "Wildlife Management Area",
 "verdict": "off"
}
```

## US-0859 Salem Maritime National Historic Site
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Salem Maritime National Historic Site",
 "official": null,
 "ours": {
  "acres": 16,
  "family_fold": "layers {'padus': 9, 'sgmaa': 7}: one land in 2 layers, the padus copy used (7 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    3167,
    "Salem Maritime National Historic Site",
    9,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 3
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "National Historic Site",
 "verdict": "no size on page"
}
```

## US-0748 New Bedford Whaling National Historical Park
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "New Bedford Whaling National Historical Park",
 "official": null,
 "ours": {
  "acres": 20,
  "manager": "",
  "pieces": [],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 2
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "National Historical Park",
 "verdict": "no size on page"
}
```

## US-11604 Squannacook River Wildlife Management Area
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 1,306 acres, no total words near it)",
 "checked": "2026-11-01",
 "handover": [],
 "n": "Squannacook River Wildlife Management Area",
 "official": {
  "acres": 1306.0,
  "as": "1,306 acres",
  "clean": false,
  "line": "public for fishing, hunting, trapping, hiking, and wildlife viewing. Towns: Ashby, Groton, Shirley, Townsend Acreage: 1,306 Wildlife Management Zone : 9 Waterfowl Zone : Central Description Squannacook River WMA is composed of many sc",
  "read": "2026-11-01",
  "sent": "Acreage: 1,306 Wildlife Management Zone : 9",
  "url": "https://www.mass.gov/info-details/squannacook-river-wma",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 1638,
  "dissolved": {
   "after": 2257,
   "before": 3953,
   "copies": 60,
   "families": {
    "padus": 1871,
    "sgmaa": 386
   },
   "family_fold": 386,
   "family_used": "padus",
   "key_union": 1638,
   "parts": 23,
   "records": 127,
   "summed": 1871,
   "tracts": 44
  },
  "family_fold": "layers {'padus': 1871, 'sgmaa': 386}: one land in 2 layers, the padus copy used (386 ac of copies not added)",
  "manager": "",
  "note": "127 joined records = 44 tracts: 60 copies of a tract (same acres, another layer) and 23 fee tracts under a designation record folded; summed 3953 -> 2257 acres",
  "pieces": [
   [
    55024,
    "Squannacook River Wildlife Management Area",
    255,
    "name"
   ],
   [
    9428,
    "Squannacook River Wildlife Management Area",
    157,
    "name"
   ],
   [
    55027,
    "Squannacook River Wildlife Management Area",
    149,
    "name"
   ],
   [
    55010,
    "Squannacook River Wildlife Management Area",
    98,
    "name"
   ],
   [
    55059,
    "Squannacook River Wildlife Management Area",
    88,
    "name"
   ],
   [
    55038,
    "Squannacook River Wildlife Management Area",
    76,
    "name"
   ],
   [
    55050,
    "Squannacook River Wildlife Management Area",
    74,
    "name"
   ],
   [
    55011,
    "Squannacook River Wildlife Management Area",
    70,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 8
 },
 "owner_now": null,
 "pct": 25,
 "same_agency": false,
 "score": 7,
 "t": "Wildlife Management Area",
 "verdict": "unsure"
}
```

## US-11431 Lilly Pond Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Lilly Pond Wildlife Management Area",
 "official": {
  "acres": 383.0,
  "as": "383 acres",
  "clean": false,
  "line": "open to the public for fishing, hunting, trapping, hiking, and wildlife viewing. Towns: Chesterfield, Goshen Acreage: 383 Wildlife Management Zone : 4N Description The Lilly Pond bog is undisturbed and surrounded by extensive intact",
  "read": "2026-11-01",
  "sent": "Acreage: 383 Wildlife Management Zone : 4N",
  "url": "https://www.mass.gov/info-details/lilly-pond-wma",
  "why": "total-looking"
 },
 "ours": {
  "acres": 351,
  "dissolved": {
   "after": 282,
   "before": 720,
   "copies": 4,
   "families": {
    "padus": 210,
    "sgmaa": 72
   },
   "family_fold": 72,
   "family_used": "padus",
   "key_union": 351,
   "parts": 4,
   "records": 12,
   "summed": 210,
   "tracts": 4
  },
  "family_fold": "layers {'padus': 210, 'sgmaa': 72}: one land in 2 layers, the padus copy used (72 ac of copies not added)",
  "manager": "",
  "note": "12 joined records = 4 tracts: 4 copies of a tract (same acres, another layer) and 4 fee tracts under a designation record folded; summed 720 -> 282 acres",
  "pieces": [
   [
    55631,
    "Lilly Pond Wildlife Management Area",
    157,
    "name"
   ],
   [
    55628,
    "Lilly Pond Wildlife Management Area",
    53,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 8,
 "same_agency": false,
 "score": 7,
 "t": "Wildlife Management Area",
 "verdict": "agree"
}
```

## US-8394 Ashuwillticook Rail Trail State Trail
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Ashuwillticook Rail Trail State Trail",
 "official": null,
 "ours": {
  "acres": 1082,
  "dissolved": {
   "after": 140,
   "before": 151,
   "copies": 3,
   "families": {
    "padus": 32,
    "sgmaa": 108
   },
   "family_fold": 32,
   "family_used": "sgmaa",
   "key_union": 1082,
   "parts": 0,
   "records": 9,
   "summed": 108,
   "tracts": 6
  },
  "family_fold": "layers {'sgmaa': 108, 'padus': 32}: one land in 2 layers, the sgmaa copy used (32 ac of copies not added)",
  "manager": "",
  "note": "9 joined records = 6 tracts: 3 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 151 -> 140 acres",
  "pieces": [
   [
    "sgmaa700067",
    "Ashuwillticook Rail Trail",
    90,
    "name"
   ],
   [
    "sgmaa657458",
    "Ashuwillticook Rail Trail",
    14,
    "name"
   ],
   [
    "sgmaa657459",
    "Ashuwillticook Rail Trail",
    4,
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
 "t": "State Trail",
 "verdict": "no size on page"
}
```
