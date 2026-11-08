# park truth checker: US-WV random sample of 12 (2026-11-08; seed = date + area, same rows for everyone)

Source file: `data/truth/US-WV.json`

## US-12050 White Horse Mountain Wildlife Management Area
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-11-08",
 "handover": [],
 "n": "White Horse Mountain Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 1099,
  "dissolved": {
   "after": 1765,
   "before": 3530,
   "copies": 1,
   "key_union": 1099,
   "parts": 0,
   "records": 2,
   "summed": 1765,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 3530 -> 1765 acres",
  "pieces": [
   [
    273213,
    "White Horse Mountain Wildlife Management Area",
    1765,
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
 "verdict": "unsure"
}
```

## US-7025 Handley Wildlife Management Area
```json
{
 "cause": "a number 76 parks share from one page (1,400,000 ac): an agency total, not this park",
 "checked": "2026-11-08",
 "handover": [],
 "n": "Handley Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 869,
  "dissolved": {
   "after": 777,
   "before": 1553,
   "copies": 1,
   "key_union": 869,
   "parts": 0,
   "records": 2,
   "summed": 777,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1553 -> 777 acres",
  "pieces": [
   [
    273164,
    "Handley Wildlife Management Area",
    777,
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
 "score": 7,
 "t": "Wildlife Management Area",
 "verdict": "unsure"
}
```

## US-7047 Big Ugly Wildlife Management Area
```json
{
 "cause": "a number 76 parks share from one page (1,400,000 ac): an agency total, not this park",
 "checked": "2026-11-08",
 "handover": [],
 "n": "Big Ugly Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 6428,
  "dissolved": {
   "after": 5539,
   "before": 11011,
   "copies": 1,
   "key_union": 6428,
   "parts": 0,
   "records": 3,
   "summed": 5539,
   "tracts": 2
  },
  "manager": "",
  "note": "3 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 11011 -> 5539 acres",
  "pieces": [
   [
    272127,
    "Big Ugly Wildlife Management Area",
    5476,
    "name"
   ],
   [
    272086,
    "Big Ugly Wildlife Management Area",
    63,
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
 "score": 7,
 "t": "Wildlife Management Area",
 "verdict": "unsure"
}
```

## US-1809 Cedar Creek State Park
```json
{
 "checked": "2026-11-08",
 "handover": [],
 "n": "Cedar Creek State Park",
 "official": null,
 "ours": {
  "acres": 1428,
  "dissolved": {
   "after": 2507,
   "before": 5012,
   "copies": 1,
   "key_union": 1428,
   "parts": 0,
   "records": 2,
   "summed": 2507,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 5012 -> 2507 acres",
  "pieces": [
   [
    273230,
    "Cedar Creek State Park",
    2507,
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

## US-0015 Chesapeake and Ohio Canal National Historical Park
```json
{
 "checked": "2026-11-08",
 "handover": [],
 "n": "Chesapeake and Ohio Canal National Historical Park",
 "note": "whole park compared (POTA lists it in 2 states: {'US-WV': 118, 'US-MD': 13211})",
 "official": null,
 "ours": {
  "acres": 13329,
  "acres_by_state": {
   "US-MD": 13211,
   "US-WV": 118
  },
  "manager": "",
  "pieces": [
   [
    3194,
    "Chesapeake and Ohio Canal National Historical Park",
    118,
    "name"
   ]
  ],
  "pin": "well outside",
  "src": "USGS PAD-US",
  "states": [
   "US-WV",
   "US-DC",
   "US-MD"
  ],
  "unknown_pieces": 0,
  "whole_park": true
 },
 "owner_now": null,
 "pct": null,
 "score": 4,
 "t": "National Historical Park",
 "verdict": "no size on page"
}
```

## US-1798 Babcock State Park
```json
{
 "checked": "2026-11-08",
 "handover": [],
 "n": "Babcock State Park",
 "official": {
  "acres": 4127.0,
  "as": "4,127 acres",
  "clean": false,
  "line": "» Babcock State Park Babcock State Park One of West Virginia’s most iconic locations, Babcock State Park has 4,127 acres of stunning scenery. Located 20 miles southeast of the New River Gorge Bridge, the park is known for the Glad",
  "read": "2026-11-08",
  "sent": "One of West Virginia’s most iconic locations, Babcock State Park has 4,127 acres of stunning scenery.",
  "url": "https://wvstateparks.com/park/babcock-state-park/",
  "why": "total-looking"
 },
 "ours": {
  "acres": 4407,
  "dissolved": {
   "after": 4062,
   "before": 8120,
   "copies": 1,
   "key_union": 4407,
   "parts": 0,
   "records": 2,
   "summed": 4062,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 8120 -> 4062 acres",
  "pieces": [
   [
    273219,
    "Babcock State Park",
    4062,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 7,
 "same_agency": false,
 "score": 8,
 "t": "State Park",
 "verdict": "agree"
}
```

## US-12442 Roaring Plains West Wilderness Area
```json
{
 "checked": "2026-11-08",
 "handover": [],
 "n": "Roaring Plains West Wilderness Area",
 "official": {
  "acres": 6792.0,
  "as": "6,792 acre",
  "clean": false,
  "line": "and Outdoor Ethics Visitor Maps and Guides Recreation Region: Potomac Ranger District Roaring Plains West The 6,792 acre Roaring Plains West Wilderness area is located approximately 3 miles southwest of the Dolly Sods Wilderness .",
  "read": "2026-11-08",
  "sent": "The 6,792 acre Roaring Plains West Wilderness area is located approximately 3 miles southwest of the Dolly Sods Wilderness .",
  "url": "https://www.fs.usda.gov/r09/monongahela/recreation/roaring-plains-west",
  "why": "total-looking"
 },
 "ours": {
  "acres": 6794,
  "manager": "",
  "pieces": [
   [
    "wld199",
    "Roaring Plains West Wilderness",
    6794,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 0,
 "same_agency": false,
 "score": 7,
 "t": "Wilderness Area",
 "verdict": "agree"
}
```

## US-1811 Droop Mountain Battlefield State Park
```json
{
 "checked": "2026-11-08",
 "handover": [],
 "n": "Droop Mountain Battlefield State Park",
 "official": null,
 "ours": {
  "acres": 214,
  "dissolved": {
   "after": 293,
   "before": 585,
   "copies": 1,
   "key_union": 214,
   "parts": 0,
   "records": 2,
   "summed": 293,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 585 -> 293 acres",
  "pieces": [
   [
    273232,
    "Droop Mountain Battlefield State Park",
    293,
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

## US-1815 Little Beaver State Park
```json
{
 "checked": "2026-11-08",
 "handover": [],
 "n": "Little Beaver State Park",
 "official": {
  "acres": 562.0,
  "as": "562 acres",
  "clean": false,
  "line": "t Cards 1-833-WV-PARKS Book Now Home » Explore Parks » Little Beaver State Park Little Beaver State Park With 562 acres, Little Beaver State Park offers family fun, beautiful scenery and incredible outdoor recreation. The park fe",
  "read": "2026-11-08",
  "sent": "With 562 acres, Little Beaver State Park offers family fun, beautiful scenery and incredible outdoor recreation.",
  "url": "https://wvstateparks.com/park/little-beaver-state-park/",
  "why": "total-looking"
 },
 "ours": {
  "acres": 494,
  "dissolved": {
   "after": 552,
   "before": 1103,
   "copies": 1,
   "key_union": 494,
   "parts": 0,
   "records": 2,
   "summed": 552,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1103 -> 552 acres",
  "pieces": [
   [
    273236,
    "Little Beaver State Park",
    552,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 12,
 "same_agency": false,
 "score": 8,
 "t": "State Park",
 "verdict": "agree"
}
```

## US-0632 Monongahela National Forest
```json
{
 "checked": "2026-11-08",
 "handover": [],
 "n": "Monongahela National Forest",
 "official": {
  "acres": 900000.0,
  "as": "900,000 acres",
  "clean": false,
  "line": "ds and trails on the Monongahela National Forest except in designated… Fishing Fishing OverviewWith more than 900,000 acres of National Forest System lands that range in elevation between 1,425 feet and 4,863 feet above… View All Opp",
  "read": "2026-11-08",
  "sent": "Fishing OverviewWith more than 900,000 acres of National Forest System lands that range in elevation between 1,425 feet and 4,863 feet above…",
  "url": "https://www.fs.usda.gov/mnf",
  "why": "part (a lake, a purchase, a campground…)"
 },
 "ours": {
  "acres": 921100,
  "manager": "",
  "pieces": [
   [
    3069,
    "Monongahela National Forest",
    921100,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 2,
 "same_agency": false,
 "score": 7,
 "t": "National Forest",
 "verdict": "agree"
}
```

## US-1821 Pricketts Fort State Park
```json
{
 "checked": "2026-11-08",
 "handover": [],
 "n": "Pricketts Fort State Park",
 "official": null,
 "ours": {
  "acres": 170,
  "dissolved": {
   "after": 214,
   "before": 428,
   "copies": 1,
   "key_union": 170,
   "parts": 0,
   "records": 2,
   "summed": 214,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 428 -> 214 acres",
  "pieces": [
   [
    273243,
    "Pricketts Fort State Park",
    214,
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

## US-7066 The Jug Wildlife Management Area
```json
{
 "cause": "a number 76 parks share from one page (1,400,000 ac): an agency total, not this park",
 "checked": "2026-11-08",
 "handover": [],
 "n": "The Jug Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 2095,
  "dissolved": {
   "after": 2095,
   "before": 4188,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 4188 -> 2095 acres",
  "pieces": [
   [
    273202,
    "The Jug Wildlife Management Area",
    2095,
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
 "score": 7,
 "t": "Wildlife Management Area",
 "verdict": "unsure"
}
```
