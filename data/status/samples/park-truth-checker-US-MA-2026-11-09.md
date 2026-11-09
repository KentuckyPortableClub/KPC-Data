# park truth checker: US-MA random sample of 12 (2026-11-09; seed = date + area, same rows for everyone)

Source file: `data/truth/US-MA.json`

## US-11676 Mattapoisett River Wildlife Management Area
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-09",
 "handover": [],
 "n": "Mattapoisett River Wildlife Management Area",
 "official": {
  "acres": 163.0,
  "as": "163 acres",
  "clean": false,
  "line": "as (WMA) are open to the public for fishing, hunting, trapping, hiking, and wildlife viewing. Town: Rochester Acreage: 163 Wildlife Management Zone : 11 Waterfowl Zone : Central Description Mattapoisett River WMA consists of mixed up",
  "read": "2026-11-09",
  "sent": "Acreage: 163 Wildlife Management Zone : 11",
  "url": "https://www.mass.gov/info-details/mattapoisett-river-wma",
  "why": "total-looking"
 },
 "ours": {
  "acres": 104,
  "dissolved": {
   "after": 162,
   "before": 324,
   "copies": 1,
   "key_union": 104,
   "parts": 0,
   "records": 2,
   "summed": 162,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 324 -> 162 acres",
  "pieces": [
   [
    55684,
    "Mattapoisett River Wildlife Management Area",
    162,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 36,
 "same_agency": false,
 "score": 6,
 "t": "Wildlife Management Area",
 "verdict": "off"
}
```

## US-0325 Nantucket National Wildlife Refuge
```json
{
 "cause": "our union: one of our pieces alone matches the agency (double count?)",
 "checked": "2026-11-09",
 "handover": [],
 "n": "Nantucket National Wildlife Refuge",
 "official": {
  "acres": 24.0,
  "as": "24 acre",
  "clean": true,
  "line": "st be purchased through The Trustees of Reservations. Purchase Over-sand vehicle permit here . Activities The 24-acre refuge is on the tip of Great Point, the most northern part of Nantucket Island, on Coskata-Coatue Peninsula.",
  "read": "2026-11-09",
  "sent": "The 24-acre refuge is on the tip of Great Point, the most northern part of Nantucket Island, on Coskata-Coatue Peninsula.",
  "url": "https://www.fws.gov/refuge/nantucket/visit-us",
  "why": "clean total"
 },
 "ours": {
  "acres": 17,
  "manager": "",
  "pieces": [
   [
    4146,
    "Nantucket National Wildlife Refuge",
    21,
    "name"
   ],
   [
    5102,
    "Nantucket National Wildlife Refuge",
    21,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 29,
 "same_agency": false,
 "score": 6,
 "t": "National Wildlife Refuge",
 "verdict": "off"
}
```

## US-11631 Hartley Reservoir Wildlife Management Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Hartley Reservoir Wildlife Management Area",
 "official": {
  "acres": 70.0,
  "as": "70 acres",
  "clean": false,
  "line": "as (WMA) are open to the public for fishing, hunting, trapping, hiking, and wildlife viewing. Town: Rochester Acreage: 70 Wildlife Management Zone : 11 Waterfowl Zone : Central Description The majority of Hartley Reservoir WMA is ma",
  "read": "2026-11-09",
  "sent": "Acreage: 70 Wildlife Management Zone : 11",
  "url": "https://www.mass.gov/info-details/hartley-reservoir-wma",
  "why": "total-looking"
 },
 "ours": {
  "acres": 61,
  "dissolved": {
   "after": 76,
   "before": 152,
   "copies": 1,
   "key_union": 61,
   "parts": 0,
   "records": 2,
   "summed": 76,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 152 -> 76 acres",
  "pieces": [
   [
    55515,
    "Hartley Reservoir Wildlife Management Area",
    76,
    "name"
   ]
  ],
  "pin": "well outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 13,
 "same_agency": false,
 "score": 6,
 "t": "Wildlife Management Area",
 "verdict": "agree"
}
```

## US-2427 Cochituate State Park
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Cochituate State Park",
 "official": null,
 "ours": {
  "acres": 1414,
  "dissolved": {
   "after": 604,
   "before": 1845,
   "copies": 2,
   "families": {
    "padus": 395,
    "sgmaa": 209
   },
   "family_fold": 209,
   "family_used": "padus",
   "key_union": 1414,
   "parts": 40,
   "records": 47,
   "summed": 395,
   "tracts": 5
  },
  "family_fold": "layers {'padus': 395, 'sgmaa': 209}: one land in 2 layers, the padus copy used (209 ac of copies not added)",
  "manager": "",
  "note": "47 joined records = 5 tracts: 2 copies of a tract (same acres, another layer) and 40 fee tracts under a designation record folded; summed 1845 -> 604 acres",
  "pieces": [
   [
    59500,
    "Cochituate State Park",
    395,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 18
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-11397 Ashfield Hawley Wildlife Management Area
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-09",
 "handover": [],
 "n": "Ashfield Hawley Wildlife Management Area",
 "official": {
  "acres": 284.0,
  "as": "284 acres",
  "clean": false,
  "line": "are open to the public for fishing, hunting, trapping, hiking, and wildlife viewing. Towns: Ashfield, Hawley Acreage: 284 Wildlife Management Zone : 2 Description The Ashfield Hawley WMA contains a mix of Hemlock-Spruce-Fir wetlands",
  "read": "2026-11-09",
  "sent": "Acreage: 284 Wildlife Management Zone : 2",
  "url": "https://www.mass.gov/info-details/ashfield-hawley-wma",
  "why": "total-looking"
 },
 "ours": {
  "acres": 176,
  "dissolved": {
   "after": 284,
   "before": 568,
   "copies": 0,
   "key_union": 176,
   "parts": 2,
   "records": 3,
   "summed": 284,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 0 copies of a tract (same acres, another layer) and 2 fee tracts under a designation record folded; summed 568 -> 284 acres",
  "pieces": [
   [
    55170,
    "Ashfield Hawley Wildlife Management Area",
    284,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 38,
 "same_agency": false,
 "score": 6,
 "t": "Wildlife Management Area",
 "verdict": "off"
}
```

## US-11570 Thayer Pond Wildlife Management Area
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-09",
 "handover": [],
 "n": "Thayer Pond Wildlife Management Area",
 "official": {
  "acres": 131.0,
  "as": "131 acres",
  "clean": false,
  "line": "eas (WMA) are open to the public for fishing, hunting, trapping, hiking, and wildlife viewing. Towns: Rutland Acreage: 131 Wildlife Management Zone : 8 Description Almost all of Thayer Pond is contained within the eastern part of the",
  "read": "2026-11-09",
  "sent": "Acreage: 131 Wildlife Management Zone : 8",
  "url": "https://www.mass.gov/info-details/thayer-pond-wma",
  "why": "total-looking"
 },
 "ours": {
  "acres": 108,
  "manager": "",
  "pieces": [
   [
    "sgmaa681753",
    "Thayer Pond WMA",
    49,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 2
 },
 "owner_now": null,
 "pct": 18,
 "same_agency": false,
 "score": 6,
 "t": "Wildlife Management Area",
 "verdict": "off"
}
```

## US-11558 Popple Camp Wildlife Management Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Popple Camp Wildlife Management Area",
 "official": {
  "acres": 1052.0,
  "as": "1,052 acres",
  "clean": false,
  "line": "pen to the public for fishing, hunting, trapping, hiking, and wildlife viewing. Towns: Petersham, Phillipston Acreage: 1,052 Wildlife Management Zone : 5 Description This property consists of old apple orchards, reclaimed fields, agric",
  "read": "2026-11-09",
  "sent": "Acreage: 1,052 Wildlife Management Zone : 5",
  "url": "https://www.mass.gov/info-details/popple-camp-wma",
  "why": "total-looking"
 },
 "ours": {
  "acres": 1001,
  "dissolved": {
   "after": 1087,
   "before": 2905,
   "copies": 6,
   "families": {
    "padus": 1001,
    "sgmaa": 86
   },
   "family_fold": 86,
   "family_used": "padus",
   "parts": 11,
   "records": 23,
   "tracts": 6
  },
  "family_fold": "layers {'padus': 1001, 'sgmaa': 86}: one land in 2 layers, the padus copy used (86 ac of copies not added)",
  "manager": "",
  "note": "23 joined records = 6 tracts: 6 copies of a tract (same acres, another layer) and 11 fee tracts under a designation record folded; summed 2905 -> 1087 acres",
  "pieces": [
   [
    55988,
    "Popple Camp Wildlife Management Area",
    677,
    "name"
   ],
   [
    55991,
    "Popple Camp Wildlife Management Area",
    269,
    "name"
   ],
   [
    55990,
    "Popple Camp Wildlife Management Area",
    55,
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
 "t": "Wildlife Management Area",
 "verdict": "agree"
}
```

## US-11462 Facing Rock Wildlife Management Area
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-09",
 "handover": [],
 "n": "Facing Rock Wildlife Management Area",
 "official": {
  "acres": 3000.0,
  "as": "3,000 acres",
  "clean": true,
  "line": "7 Description Facing Rock WMA is part of a complex of lands with public access easements that total more than 3,000 acres. The rolling terrain is predominately upland central hardwood forest of oak, hickory, and white pine with a f",
  "read": "2026-11-09",
  "sent": "Facing Rock WMA is part of a complex of lands with public access easements that total more than 3,000 acres.",
  "url": "https://www.mass.gov/info-details/facing-rock-wma",
  "why": "clean total"
 },
 "ours": {
  "acres": 1069,
  "dissolved": {
   "after": 717,
   "before": 1627,
   "copies": 3,
   "key_union": 1069,
   "parts": 10,
   "records": 16,
   "summed": 717,
   "tracts": 3
  },
  "manager": "",
  "note": "16 joined records = 3 tracts: 3 copies of a tract (same acres, another layer) and 10 fee tracts under a designation record folded; summed 1627 -> 717 acres",
  "pieces": [
   [
    "sgmaa665715",
    "Facing Rock WMA",
    699,
    "name"
   ],
   [
    "sgmaa657275",
    "Facing Rock WMA",
    10,
    "name"
   ],
   [
    "sgmaa643873",
    "Facing Rock WMA",
    8,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 2
 },
 "owner_now": null,
 "pct": 64,
 "same_agency": false,
 "score": 6,
 "t": "Wildlife Management Area",
 "verdict": "off"
}
```

## US-11677 Meetinghouse Swamp Wildlife Management Area
```json
{
 "cause": "agency smaller: our outline may hold water, a lease or a neighbour tract",
 "checked": "2026-11-09",
 "handover": [],
 "n": "Meetinghouse Swamp Wildlife Management Area",
 "official": {
  "acres": 123.0,
  "as": "123 acres",
  "clean": false,
  "line": "WMA) are open to the public for fishing, hunting, trapping, hiking, and wildlife viewing. Town: Middleborough Acreage: 123 Wildlife Management Zone : 11 Waterfowl Zone : Central Description Meetinghouse Swamp WMA lies north of Route",
  "read": "2026-11-09",
  "sent": "Acreage: 123 Wildlife Management Zone : 11",
  "url": "https://www.mass.gov/info-details/meetinghouse-swamp-wma",
  "why": "total-looking"
 },
 "ours": {
  "acres": 148,
  "manager": "",
  "pieces": [
   [
    "sgmaa642080",
    "Meetinghouse Swamp WMA",
    190,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 20,
 "same_agency": false,
 "score": 6,
 "t": "Wildlife Management Area",
 "verdict": "off"
}
```

## US-0843 Longfellow House National Historic Site
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Longfellow House National Historic Site",
 "official": null,
 "ours": {
  "acres": 7,
  "manager": "",
  "pieces": [
   [
    3153,
    "Longfellow House-Washington's Headquarters National Historic Site",
    2,
    "words"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "National Historic Site",
 "verdict": "no size on page"
}
```

## US-4697 Shawme-Crowell State Forest
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Shawme-Crowell State Forest",
 "official": {
  "acres": 700.0,
  "as": "700 acre",
  "clean": false,
  "line": "tern MA Adult Walking Club Get Directions to Shawme-Crowell State Forest in Google Maps Details Overview This 700-acre pitch pine and scrub oak forest is located on the western end of Cape Cod, and offers more than 15 miles of t",
  "read": "2026-11-09",
  "sent": "This 700-acre pitch pine and scrub oak forest is located on the western end of Cape Cod, and offers more than 15 miles of trails for hiking and horseback riding.",
  "url": "https://www.mass.gov/locations/shawme-crowell-state-forest",
  "why": "total-looking"
 },
 "ours": {
  "acres": 805,
  "dissolved": {
   "after": 426,
   "before": 1221,
   "copies": 3,
   "families": {
    "padus": 387,
    "sgmaa": 39
   },
   "family_fold": 39,
   "family_used": "padus",
   "key_union": 805,
   "parts": 39,
   "records": 46,
   "summed": 387,
   "tracts": 4
  },
  "family_fold": "layers {'padus': 387, 'sgmaa': 39}: one land in 2 layers, the padus copy used (39 ac of copies not added)",
  "manager": "",
  "note": "46 joined records = 4 tracts: 3 copies of a tract (same acres, another layer) and 39 fee tracts under a designation record folded; summed 1221 -> 426 acres",
  "pieces": [
   [
    60509,
    "Shawme-Crowell State Forest",
    387,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 5
 },
 "owner_now": null,
 "pct": 15,
 "same_agency": false,
 "score": 8,
 "t": "State Forest",
 "verdict": "agree"
}
```

## US-11411 Green River Williamstown Wildlife Management Area
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-09",
 "handover": [],
 "n": "Green River Williamstown Wildlife Management Area",
 "official": {
  "acres": 597.0,
  "as": "597 acres",
  "clean": false,
  "line": "WMA) are open to the public for fishing, hunting, trapping, hiking, and wildlife viewing. Towns: Williamstown Acreage: 597 Wildlife Management Zone : 1 Description This WMA consists of multiple parcels of land along the Green River i",
  "read": "2026-11-09",
  "sent": "Acreage: 597 Wildlife Management Zone : 1",
  "url": "https://www.mass.gov/info-details/green-river-wma-williamstown",
  "why": "total-looking"
 },
 "ours": {
  "acres": 479,
  "dissolved": {
   "after": 458,
   "before": 1088,
   "copies": 2,
   "families": {
    "padus": 340,
    "sgmaa": 118
   },
   "family_fold": 118,
   "family_used": "padus",
   "key_union": 479,
   "parts": 6,
   "records": 15,
   "summed": 340,
   "tracts": 7
  },
  "family_fold": "layers {'padus': 340, 'sgmaa': 118}: one land in 2 layers, the padus copy used (118 ac of copies not added)",
  "manager": "",
  "note": "15 joined records = 7 tracts: 2 copies of a tract (same acres, another layer) and 6 fee tracts under a designation record folded; summed 1088 -> 458 acres",
  "pieces": [
   [
    55511,
    "Green River Wildlife Management Area - Williamstown",
    262,
    "name"
   ],
   [
    55506,
    "Green River Wildlife Management Area - Williamstown",
    33,
    "name"
   ],
   [
    55508,
    "Green River Wildlife Management Area - Williamstown",
    31,
    "name"
   ],
   [
    55507,
    "Green River Wildlife Management Area - Williamstown",
    14,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 20,
 "same_agency": false,
 "score": 5,
 "t": "Wildlife Management Area",
 "verdict": "off"
}
```
