# park truth checker: US-WV random sample of 12 (2026-11-01; seed = date + area, same rows for everyone)

Source file: `data/truth/US-WV.json`

## US-7004 Pedlar Wildlife Management Area
```json
{
 "cause": "a number 76 parks share from one page (1,400,000 ac): an agency total, not this park",
 "checked": "2026-10-29",
 "handover": [],
 "n": "Pedlar Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 763,
  "dissolved": {
   "after": 763,
   "before": 1526,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1526 -> 763 acres",
  "pieces": [
   [
    273181,
    "Pedlar Wildlife Management Area",
    763,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "same_agency": false,
 "score": 6,
 "t": "Wildlife Management Area",
 "verdict": "unsure"
}
```

## US-12441 Otter Creek Wilderness Area
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-10-29",
 "n": "Otter Creek Wilderness Area",
 "official": null,
 "ours": {
  "acres": 20705,
  "manager": "",
  "pieces": [
   [
    "wld340",
    "Otter Creek Wilderness",
    20705,
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
 "t": "Wilderness Area",
 "verdict": "no size on page"
}
```

## US-0608 Ohio River Islands National Wildlife Refuge
```json
{
 "cause": "whole park compared (POTA lists it in 1 states: {'US-WV': 2734})",
 "checked": "2026-10-29",
 "handover": [],
 "n": "Ohio River Islands National Wildlife Refuge",
 "note": "whole park compared (POTA lists it in 1 states: {'US-WV': 2734})",
 "official": {
  "acres": 3440.0,
  "as": "3,440 acres",
  "clean": true,
  "line": "est Virginia. The Refuge currently consists of all or part of 22 islands and four mainland units encompassing 3,440 acres of valuable fish and wildlife habitat within one of the nation's busiest waterways. As acquisition progresses",
  "read": "2026-10-29",
  "sent": "The Refuge currently consists of all or part of 22 islands and four mainland units encompassing 3,440 acres of valuable fish and wildlife habitat within one of the nation's busiest waterways.",
  "url": "https://www.fws.gov/refuge/ohio-river-islands/about-us",
  "why": "clean total"
 },
 "ours": {
  "acres": 2734,
  "acres_by_state": {
   "US-WV": 2734
  },
  "dissolved": {
   "after": 2734,
   "before": 5468,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 5468 -> 2734 acres",
  "pieces": [
   [
    4181,
    "Ohio River Islands National Wildlife Refuge",
    2734,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "states": [
   "US-PA",
   "US-WV"
  ],
  "unknown_pieces": 0,
  "whole_park": true
 },
 "owner_now": null,
 "pct": 21,
 "same_agency": false,
 "score": 7,
 "t": "National Wildlife Refuge",
 "verdict": "unsure"
}
```

## US-7061 OBrien Lake Wildlife Management Area
```json
{
 "cause": "a number 76 parks share from one page (1,400,000 ac): an agency total, not this park",
 "checked": "2026-10-29",
 "handover": [],
 "n": "OBrien Lake Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 1090,
  "dissolved": {
   "after": 1090,
   "before": 2179,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 2179 -> 1090 acres",
  "pieces": [
   [
    272121,
    "O'Brien Lake Wildlife Management Area",
    1090,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "same_agency": false,
 "score": 5,
 "t": "Wildlife Management Area",
 "verdict": "unsure"
}
```

## US-0629 Tomlinson Run State Park
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Tomlinson Run State Park",
 "official": {
  "acres": 1398.0,
  "as": "1,398 acres",
  "clean": false,
  "line": "inson Run State Park sits along the Ohio River at the top of West Virginia's Northern Panhandle. The park has 1,398 acres and is divided into two sections: a wilderness area and a developed area with traditional park offerings. Boo",
  "read": "2026-10-29",
  "sent": "The park has 1,398 acres and is divided into two sections: a wilderness area and a developed area with traditional park offerings.",
  "url": "https://wvstateparks.com/park/tomlinson-run-state-park/",
  "why": "total-looking"
 },
 "ours": {
  "acres": 1361,
  "dissolved": {
   "after": 1361,
   "before": 2721,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 2721 -> 1361 acres",
  "pieces": [
   [
    273245,
    "Tomlinson Run State Park",
    1361,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 3,
 "same_agency": false,
 "score": 8,
 "t": "State Park",
 "verdict": "agree"
}
```

## US-7011 Edwards Run Wildlife Management Area
```json
{
 "cause": "a number 76 parks share from one page (1,400,000 ac): an agency total, not this park",
 "checked": "2026-10-29",
 "handover": [],
 "n": "Edwards Run Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 396,
  "dissolved": {
   "after": 396,
   "before": 792,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 792 -> 396 acres",
  "pieces": [
   [
    273159,
    "Edwards Run Wildlife Management Area",
    396,
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

## US-12039 Little Canaan Wildlife Management Area
```json
{
 "cause": "a number 16 parks share from one page (217 ac): an agency total, not this park",
 "checked": "2026-10-29",
 "handover": [],
 "n": "Little Canaan Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 3072,
  "dissolved": {
   "after": 3072,
   "before": 6143,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 6143 -> 3072 acres",
  "pieces": [
   [
    273169,
    "Little Canaan Wildlife Management Area",
    3072,
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

## US-1797 Audra State Park
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Audra State Park",
 "official": null,
 "ours": {
  "acres": 344,
  "dissolved": {
   "after": 344,
   "before": 688,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 688 -> 344 acres",
  "pieces": [
   [
    273218,
    "Audra State Park",
    344,
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

## US-1801 Berkeley Springs State Park
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Berkeley Springs State Park",
 "official": null,
 "ours": {
  "acres": 5,
  "dissolved": {
   "after": 5,
   "before": 10,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 10 -> 5 acres",
  "pieces": [
   [
    273221,
    "Berkeley Springs State Park",
    5,
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

## US-7007 Snake Hill Wildlife Management Area
```json
{
 "cause": "a number 76 parks share from one page (1,400,000 ac): an agency total, not this park",
 "checked": "2026-10-29",
 "handover": [],
 "n": "Snake Hill Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 2959,
  "dissolved": {
   "after": 2959,
   "before": 5916,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 5916 -> 2959 acres",
  "pieces": [
   [
    273194,
    "Snake Hill Wildlife Management Area",
    2959,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "same_agency": false,
 "score": 6,
 "t": "Wildlife Management Area",
 "verdict": "unsure"
}
```

## US-1828 Watters Smith Memorial State Park
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Watters Smith Memorial State Park",
 "official": {
  "acres": 532.0,
  "as": "532 acre",
  "clean": false,
  "line": "West Virginia and the pioneer spirit of Watters Smith are both preserved in the homestead restoration at this 532-acre historical park. This historical park, located in Harrison County, features log cabins, period-accurate build",
  "read": "2026-10-29",
  "sent": "The heritage of early West Virginia and the pioneer spirit of Watters Smith are both preserved in the homestead restoration at this 532-acre historical park.",
  "url": "https://wvstateparks.com/park/watters-smith-memorial-state-park/",
  "why": "total-looking"
 },
 "ours": {
  "acres": 537,
  "dissolved": {
   "after": 537,
   "before": 1074,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1074 -> 537 acres",
  "pieces": [
   [
    273251,
    "Watters Smith Memorial State Park",
    537,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 1,
 "same_agency": false,
 "score": 8,
 "t": "State Park",
 "verdict": "agree"
}
```

## US-7038 Horse Creek Lake Wildlife Management Area
```json
{
 "cause": "a number 76 parks share from one page (1,400,000 ac): an agency total, not this park",
 "checked": "2026-10-29",
 "handover": [],
 "n": "Horse Creek Lake Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 47,
  "dissolved": {
   "after": 47,
   "before": 94,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 94 -> 47 acres",
  "pieces": [
   [
    272123,
    "Horse Creek Wildlife Management Area",
    47,
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
