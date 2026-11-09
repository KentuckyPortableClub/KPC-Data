# park truth checker: US-NJ random sample of 12 (2026-11-09; seed = date + area, same rows for everyone)

Source file: `data/truth/US-NJ.json`

## US-4556 Appalachian Trail National Scenic Trail
```json
{
 "checked": "2026-11-09",
 "handover": [
  {
   "date_hint": "1937",
   "kind": "managed by",
   "line": "ian Mountains. Conceived in 1921, built by private citizens, and completed in 1937, today the trail is managed by the National Park Service, US Forest Service, Appalachian Trail Conservancy, numerous state agencies and thousands of volunte",
   "owner_now": "National Park Service",
   "src": "https://www.nps.gov/appa/index.htm",
   "why": "the park's page (data/parkinfo)"
  }
 ],
 "n": "Appalachian Trail National Scenic Trail",
 "note": "whole park compared (POTA lists it in 0 states: {})",
 "official": null,
 "ours": {
  "acres": 0,
  "acres_by_state": {},
  "manager": "",
  "pieces": [],
  "pin": "inside",
  "src": "",
  "states": [
   "US-CT",
   "US-VA",
   "US-WV",
   "US-MA",
   "US-PA",
   "US-ME",
   "US-GA",
   "US-TN",
   "US-NY",
   "US-VT",
   "US-MD",
   "US-NH",
   "US-NJ",
   "US-NC"
  ],
  "unknown_pieces": 1,
  "whole_park": true
 },
 "owner_now": "National Park Service",
 "pct": null,
 "score": 5,
 "t": "National Scenic Trail",
 "verdict": "ours unknown"
}
```

## US-8032 Black River Wildlife Management Area
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-11-09",
 "handover": [],
 "n": "Black River Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 2554,
  "dissolved": {
   "after": 3265,
   "before": 6295,
   "copies": 0,
   "families": {
    "padus": 223,
    "sgnjb": 3042
   },
   "family_fold": 223,
   "family_used": "sgnjb",
   "key_union": 2554,
   "parts": 7,
   "records": 12,
   "summed": 3042,
   "tracts": 5
  },
  "family_fold": "layers {'sgnjb': 3042, 'padus': 223}: one land in 2 layers, the sgnjb copy used (223 ac of copies not added)",
  "manager": "",
  "note": "12 joined records = 5 tracts: 0 copies of a tract (same acres, another layer) and 7 fee tracts under a designation record folded; summed 6295 -> 3265 acres",
  "pieces": [
   [
    "sgnjb27",
    "Black River Wildlife Management Area",
    3042,
    "reviewed"
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

## US-8052 Stafford Forge Wildlife Management Area
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-11-09",
 "handover": [],
 "n": "Stafford Forge Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 16622,
  "dissolved": {
   "after": 22681,
   "before": 39983,
   "copies": 4,
   "families": {
    "padus": 6059,
    "sgnjb": 16622
   },
   "family_fold": 6059,
   "family_used": "sgnjb",
   "parts": 22,
   "records": 34,
   "tracts": 8
  },
  "family_fold": "layers {'sgnjb': 16622, 'padus': 6059}: one land in 2 layers, the sgnjb copy used (6,059 ac of copies not added)",
  "manager": "",
  "note": "34 joined records = 8 tracts: 4 copies of a tract (same acres, another layer) and 22 fee tracts under a designation record folded; summed 39983 -> 22681 acres",
  "pieces": [
   [
    "sgnjb300",
    "Stafford Forge Wildlife Management Area",
    16622,
    "reviewed"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 2
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "Wildlife Management Area",
 "verdict": "unsure"
}
```

## US-1628 Princeton Battlefield State Park
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Princeton Battlefield State Park",
 "official": null,
 "ours": {
  "acres": 75,
  "dissolved": {
   "after": 161,
   "before": 168,
   "copies": 0,
   "families": {
    "padus": 80,
    "sgnjb": 81
   },
   "family_fold": 80,
   "family_used": "sgnjb",
   "key_union": 75,
   "parts": 2,
   "records": 5,
   "summed": 81,
   "tracts": 3
  },
  "family_fold": "layers {'sgnjb': 81, 'padus': 80}: one land in 2 layers, the sgnjb copy used (80 ac of copies not added)",
  "manager": "",
  "note": "5 joined records = 3 tracts: 0 copies of a tract (same acres, another layer) and 2 fee tracts under a designation record folded; summed 168 -> 161 acres",
  "pieces": [
   [
    "sgnjb171",
    "Princeton Battlefield State Park",
    81,
    "reviewed"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 3
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-8039 Forked River Mt Wildlife Management Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Forked River Mt Wildlife Management Area",
 "official": {
  "acres": 2120.8,
  "as": "2,120.78 Acres",
  "clean": false,
  "line": "NOAA, increment P Corp. Forked River Mountain Wildlife Management Area Ocean County - Lacey & Ocean Townships 2,120.78 Acres 0 1 20.5 Miles Department of Environmental Protection New Jersey Division of Fish and Wildlife WMA Boundary",
  "read": "2026-11-09",
  "sent": "Townships 2,120.78 Acres",
  "url": "https://www.nj.gov/dep/fgw/pdf/wmaroadmaps/forked_river_mt_rd.pdf",
  "why": "a map label (no sentence)"
 },
 "ours": {
  "acres": 2310,
  "dissolved": {
   "after": 3906,
   "before": 4570,
   "copies": 0,
   "families": {
    "padus": 1596,
    "sgnjb": 2310
   },
   "family_fold": 1596,
   "family_used": "sgnjb",
   "parts": 5,
   "records": 10,
   "tracts": 5
  },
  "family_fold": "layers {'sgnjb': 2310, 'padus': 1596}: one land in 2 layers, the sgnjb copy used (1,596 ac of copies not added)",
  "manager": "",
  "note": "10 joined records = 5 tracts: 0 copies of a tract (same acres, another layer) and 5 fee tracts under a designation record folded; summed 4570 -> 3906 acres",
  "pieces": [
   [
    "sgnjb305",
    "Forked River Mountain Wildlife Management Area",
    2310,
    "reviewed"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 4
 },
 "owner_now": null,
 "pct": 9,
 "same_agency": false,
 "score": 6,
 "t": "Wildlife Management Area",
 "verdict": "agree"
}
```

## US-1636 Wawayanda State Park
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Wawayanda State Park",
 "official": null,
 "ours": {
  "acres": 15107,
  "dissolved": {
   "after": 22754,
   "before": 39829,
   "copies": 2,
   "families": {
    "padus": 7647,
    "sgnjb": 15107
   },
   "family_fold": 7647,
   "family_used": "sgnjb",
   "parts": 41,
   "records": 47,
   "tracts": 4
  },
  "family_fold": "layers {'sgnjb': 15107, 'padus': 7647}: one land in 2 layers, the sgnjb copy used (7,647 ac of copies not added)",
  "manager": "",
  "note": "47 joined records = 4 tracts: 2 copies of a tract (same acres, another layer) and 41 fee tracts under a designation record folded; summed 39829 -> 22754 acres",
  "pieces": [
   [
    "sgnjb239",
    "Wawayanda State Park",
    15107,
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

## US-8036 Dennis Creek Wildlife Management Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Dennis Creek Wildlife Management Area",
 "official": {
  "acres": 8679.7,
  "as": "8,679.69 Acres",
  "clean": false,
  "line": "CO, NOAA, increment P Corp. Dennis Creek Wildlife Management Area Cape May County - Dennis & Middle Townships 8,679.69 Acres Boat Ramp IA Parking WMA Boundary 0 0.7 1.40.35 Miles Department of Environmental Protection New Jersey Divis",
  "read": "2026-11-09",
  "sent": "8,679.69 Acres",
  "url": "https://www.nj.gov/dep/fgw/pdf/wmaroadmaps/dennis_creek_rd.pdf",
  "why": "a map label (no sentence)"
 },
 "ours": {
  "acres": 7667,
  "dissolved": {
   "after": 10697,
   "before": 24077,
   "copies": 3,
   "families": {
    "padus": 3030,
    "sgnjb": 7667
   },
   "family_fold": 3030,
   "family_used": "sgnjb",
   "parts": 23,
   "records": 32,
   "tracts": 6
  },
  "family_fold": "layers {'sgnjb': 7667, 'padus': 3030}: one land in 2 layers, the sgnjb copy used (3,030 ac of copies not added)",
  "manager": "",
  "note": "32 joined records = 6 tracts: 3 copies of a tract (same acres, another layer) and 23 fee tracts under a designation record folded; summed 24077 -> 10697 acres",
  "pieces": [
   [
    "sgnjb357",
    "Dennis Creek Wildlife Management Area",
    7667,
    "reviewed"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 12,
 "same_agency": false,
 "score": 7,
 "t": "Wildlife Management Area",
 "verdict": "agree"
}
```

## US-12100 Amwell Lake Wildlife Management Area
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-11-09",
 "handover": [],
 "n": "Amwell Lake Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 27,
  "dissolved": {
   "after": 23,
   "before": 46,
   "copies": 1,
   "key_union": 27,
   "parts": 0,
   "records": 2,
   "summed": 23,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 46 -> 23 acres",
  "pieces": [
   [
    227848,
    "Amwell Lake Wildlife Management Area",
    23,
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

## US-8060 Winslow Wildlife Management Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Winslow Wildlife Management Area",
 "official": {
  "acres": 8405.7,
  "as": "8,405.72 Acres",
  "clean": false,
  "line": "GIS User Community Winslow Wildlife Management Area Camden & Gloucester Counties; Winslow & Monroe Townships 8,405.72 Acres 0 0.75 1.5 2.25 30.375 Miles ± NJ Department of Environmental Protection NJ Division of Fish & Wildlife IA P",
  "read": "2026-11-09",
  "sent": "8,405.72 Acres",
  "url": "https://www.nj.gov/dep/fgw/pdf/wmaroadmaps/winslow_rd.pdf",
  "why": "a map label (no sentence)"
 },
 "ours": {
  "acres": 8507,
  "dissolved": {
   "after": 10984,
   "before": 17119,
   "copies": 0,
   "families": {
    "padus": 2477,
    "sgnjb": 8507
   },
   "family_fold": 2477,
   "family_used": "sgnjb",
   "parts": 26,
   "records": 30,
   "tracts": 4
  },
  "family_fold": "layers {'sgnjb': 8507, 'padus': 2477}: one land in 2 layers, the sgnjb copy used (2,477 ac of copies not added)",
  "manager": "",
  "note": "30 joined records = 4 tracts: 0 copies of a tract (same acres, another layer) and 26 fee tracts under a designation record folded; summed 17119 -> 10984 acres",
  "pieces": [
   [
    "sgnjb359",
    "Winslow Wildlife Management Area",
    8507,
    "reviewed"
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
 "t": "Wildlife Management Area",
 "verdict": "agree"
}
```

## US-0886 Maurice River National Wild and Scenic River
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Maurice River National Wild and Scenic River",
 "official": null,
 "ours": {
  "acres": 13983,
  "manager": "",
  "pieces": [
   [
    "wsrc23",
    "Maurice Wild and Scenic River",
    13983,
    "words"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "National Wild and Scenic River",
 "verdict": "no size on page"
}
```

## US-12104 Pohatcong Creek Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-09",
 "n": "Pohatcong Creek Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 123,
  "dissolved": {
   "after": 123,
   "before": 246,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 246 -> 123 acres",
  "pieces": [
   [
    228745,
    "Pohatcong Wildlife Management Area",
    123,
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
 "t": "Wildlife Management Area",
 "verdict": "no size on page"
}
```

## US-1611 Cheesequake State Park
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Cheesequake State Park",
 "official": null,
 "ours": {
  "acres": 1652,
  "dissolved": {
   "after": 4128,
   "before": 5033,
   "copies": 0,
   "families": {
    "padus": 2223,
    "sgnjb": 1905
   },
   "family_fold": 1905,
   "family_used": "padus",
   "key_union": 1652,
   "parts": 12,
   "records": 19,
   "summed": 2223,
   "tracts": 7
  },
  "family_fold": "layers {'sgnjb': 1905, 'padus': 2223}: one land in 2 layers, the padus copy used (1,905 ac of copies not added)",
  "manager": "",
  "note": "19 joined records = 7 tracts: 0 copies of a tract (same acres, another layer) and 12 fee tracts under a designation record folded; summed 5033 -> 4128 acres",
  "pieces": [
   [
    54252,
    "Cheesequake State Park",
    1221,
    "name"
   ],
   [
    227026,
    "Cheesequake State Park",
    786,
    "name"
   ],
   [
    227031,
    "Cheesequake State Park",
    195,
    "name"
   ],
   [
    227027,
    "Cheesequake State Park",
    11,
    "name"
   ],
   [
    227032,
    "Cheesequake State Park",
    9,
    "name"
   ],
   [
    227034,
    "Cheesequake State Park",
    1,
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
 "t": "State Park",
 "verdict": "no size on page"
}
```
