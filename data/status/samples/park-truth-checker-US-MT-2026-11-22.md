# park truth checker: US-MT random sample of 12 (2026-11-22; seed = date + area, same rows for everyone)

Source file: `data/truth/US-MT.json`

## US-2589 Missouri Headwaters State Park
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Missouri Headwaters State Park",
 "official": {
  "acres": 532.0,
  "as": "532 acres",
  "clean": true,
  "line": "ng, picnicking, bicycling, hiking, interpretive programs, and photography are popular activities. The park is 532 acres in size and is 4,045 feet in elevation. Events Alerts & Closures Restrictions and Closures See a current list",
  "read": "2026-11-22",
  "sent": "The park is 532 acres in size and is 4,045 feet in elevation.",
  "url": "https://fwp.mt.gov/stateparks/missouri-headwaters/",
  "why": "clean total"
 },
 "ours": {
  "acres": 590,
  "dissolved": {
   "after": 1150,
   "before": 2330,
   "copies": 2,
   "families": {
    "padus": 560,
    "sgmta": 590
   },
   "family_fold": 560,
   "family_used": "sgmta",
   "parts": 0,
   "records": 4,
   "tracts": 2
  },
  "family_fold": "layers {'sgmta': 590, 'padus': 560}: one land in 2 layers, the sgmta copy used (560 ac of copies not added)",
  "manager": "",
  "note": "4 joined records = 2 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 2330 -> 1150 acres",
  "pieces": [
   [
    "sgmta6615",
    "Missouri Headwaters",
    590,
    "reviewed"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 11,
 "same_agency": false,
 "score": 8,
 "t": "State Park",
 "verdict": "agree"
}
```

## US-12888 Loch Leven State Fish and Wildlife Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Loch Leven State Fish and Wildlife Area",
 "official": null,
 "ours": {
  "acres": 76,
  "dissolved": {
   "after": 76,
   "before": 304,
   "copies": 3,
   "parts": 0,
   "records": 4,
   "tracts": 1
  },
  "manager": "",
  "note": "4 joined records = 1 tracts: 3 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 304 -> 76 acres",
  "pieces": [
   [
    211566,
    "Loch Leven Fishing Access Site",
    76,
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
 "t": "State Fish and Wildlife Area",
 "verdict": "no size on page"
}
```

## US-7990 Lee Metcalf BLM Wilderness Area
```json
{
 "cause": "our union: one of our pieces alone matches the agency (double count?)",
 "checked": "2026-11-09",
 "handover": [],
 "n": "Lee Metcalf BLM Wilderness Area",
 "official": {
  "acres": 6347.0,
  "as": "6,347 acre",
  "clean": false,
  "line": "nits of the Lee Metcalf Wilderness. The Bear Trap is the first wilderness areas to be managed by the BLM. The 6,347-acre area offers beautiful wilderness scenery plus exciting whitewater rafting featuring the famous Class IV - V K",
  "read": "2026-11-09",
  "sent": "The 6,347-acre area offers beautiful wilderness scenery plus exciting whitewater rafting featuring the famous Class IV - V Kitchen Sink rapid.",
  "url": "https://www.blm.gov/visit/lee-metcalf-wilderness",
  "why": "total-looking"
 },
 "ours": {
  "acres": 244109,
  "manager": "",
  "pieces": [
   [
    "wld186",
    "Lee Metcalf Wilderness",
    237774,
    "name"
   ],
   [
    "sgmtd248",
    "Lee Metcalf Wilderness",
    6335,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 3746,
 "same_agency": false,
 "score": 6,
 "t": "BLM Wilderness Area",
 "verdict": "off"
}
```

## US-12871 Forks State Fish and Wildlife Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Forks State Fish and Wildlife Area",
 "official": null,
 "ours": {
  "acres": 5,
  "dissolved": {
   "after": 6,
   "before": 24,
   "copies": 3,
   "key_union": 5,
   "parts": 0,
   "records": 4,
   "summed": 6,
   "tracts": 1
  },
  "manager": "",
  "note": "4 joined records = 1 tracts: 3 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 24 -> 6 acres",
  "pieces": [
   [
    211449,
    "Forks Fishing Access Site",
    6,
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
 "t": "State Fish and Wildlife Area",
 "verdict": "no size on page"
}
```

## US-4507 Lolo National Forest
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-11-09",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Lolo National Forest",
 "official": null,
 "ours": {
  "acres": 2622441,
  "family_fold": "layers {'sgmtd': 2622441, 'padus': 2265532}: one land in 2 layers, the sgmtd copy used (2,265,532 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgmtd746",
    "Lolo National Forest",
    2622441,
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
 "t": "National Forest",
 "verdict": "unsure"
}
```

## US-12879 Harper Lake State Fish and Wildlife Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Harper Lake State Fish and Wildlife Area",
 "official": null,
 "ours": {
  "acres": 208,
  "dissolved": {
   "after": 208,
   "before": 832,
   "copies": 3,
   "parts": 0,
   "records": 4,
   "tracts": 1
  },
  "manager": "",
  "note": "4 joined records = 1 tracts: 3 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 832 -> 208 acres",
  "pieces": [
   [
    211453,
    "Harpers Lake Fishing Access Site",
    208,
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
 "t": "State Fish and Wildlife Area",
 "verdict": "no size on page"
}
```

## US-12934 Whitebird State Fish and Wildlife Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Whitebird State Fish and Wildlife Area",
 "official": null,
 "ours": {
  "acres": 21,
  "dissolved": {
   "after": 23,
   "before": 92,
   "copies": 3,
   "key_union": 21,
   "parts": 0,
   "records": 4,
   "summed": 23,
   "tracts": 1
  },
  "manager": "",
  "note": "4 joined records = 1 tracts: 3 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 92 -> 23 acres",
  "pieces": [
   [
    211731,
    "Whitebird Fishing Access Site",
    23,
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
 "t": "State Fish and Wildlife Area",
 "verdict": "no size on page"
}
```

## US-12941 Judith Landing State Park
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Judith Landing State Park",
 "official": {
  "acres": 109.4,
  "as": "109.43 acre",
  "clean": false,
  "line": "site amenities at this time. # About the park In January of 2025, Montana Fish, Wildlife & Parks acquired the 109.43-acre Judith Landing property at the confluence of the Missouri and Judith Rivers in Central Montana. Judith Landin",
  "read": "2026-11-22",
  "sent": "In January of 2025, Montana Fish, Wildlife & Parks acquired the 109.43-acre Judith Landing property at the confluence of the Missouri and Judith Rivers in Central Montana.",
  "url": "https://fwp.mt.gov/stateparks/judith-landing",
  "why": "part (a lake, a purchase, a campground…)"
 },
 "ours": {
  "acres": 97,
  "dissolved": {
   "after": 109,
   "before": 327,
   "copies": 2,
   "key_union": 97,
   "parts": 0,
   "records": 3,
   "summed": 109,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 327 -> 109 acres",
  "pieces": [
   [
    "sgmta6642",
    "Judith Landing State Park",
    109,
    "reviewed"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 11,
 "same_agency": false,
 "score": 8,
 "t": "State Park",
 "verdict": "agree"
}
```

## US-4851 Thompson River State Forest
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Thompson River State Forest",
 "official": {
  "acres": 14628.0,
  "as": "14,628 acres",
  "clean": false,
  "line": "rest\". (5) A state forest containing all lands owned or hereafter acquired by the state, now comprising about 14,628 acres, situated in the west half of township 25 north, range 26 west; and township 23 north, range 27 west; and wes",
  "read": "2026-11-22",
  "sent": "(5) A state forest containing all lands owned or hereafter acquired by the state, now comprising about 14,628 acres, situated in the west half of township 25 north, range 26 west;",
  "url": "https://archive.legmt.gov/bills/mca/title_0770/chapter_0050/part_0010/section_0020/0770-0050-0010-0020.html",
  "why": "part (a lake, a purchase, a campground…)"
 },
 "ours": {
  "acres": 13744,
  "dissolved": {
   "after": 13744,
   "before": 27472,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 27472 -> 13744 acres",
  "pieces": [
   [
    211331,
    "Thompson River State Forest",
    13744,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 6,
 "same_agency": false,
 "score": 7,
 "t": "State Forest",
 "verdict": "agree"
}
```

## US-12905 Pelican State Fish and Wildlife Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Pelican State Fish and Wildlife Area",
 "official": null,
 "ours": {
  "acres": 122,
  "dissolved": {
   "after": 122,
   "before": 488,
   "copies": 3,
   "parts": 0,
   "records": 4,
   "tracts": 1
  },
  "manager": "",
  "note": "4 joined records = 1 tracts: 3 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 488 -> 122 acres",
  "pieces": [
   [
    211722,
    "Pelican Fishing Access Site",
    122,
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
 "t": "State Fish and Wildlife Area",
 "verdict": "no size on page"
}
```

## US-0399 Charles M. Russell National Wildlife Refuge
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Charles M. Russell National Wildlife Refuge",
 "official": {
  "acres": 1100000.0,
  "as": "1.1 million acres",
  "clean": false,
  "line": "2026 to December 2, 2026. Comments may be emailed to cmr@fws.gov . Plan Your Visit Encompassing approximately 1.1 million acres, Charles M. Russell National Wildlife Refuge is the second largest national wildlife refuge in the lower 48 s",
  "read": "2026-11-22",
  "sent": "Encompassing approximately 1.1 million acres, Charles M.",
  "url": "https://www.fws.gov/refuge/charles_m_russell/",
  "why": "total-looking"
 },
 "ours": {
  "acres": 955247,
  "dissolved": {
   "after": 1349623,
   "before": 1743375,
   "copies": 1,
   "families": {
    "padus": 394376,
    "sgmtd": 955247
   },
   "family_fold": 394376,
   "family_used": "sgmtd",
   "parts": 0,
   "records": 4,
   "tracts": 3
  },
  "family_fold": "layers {'sgmtd': 955247, 'padus': 394376}: one land in 2 layers, the sgmtd copy used (394,376 ac of copies not added)",
  "manager": "",
  "note": "4 joined records = 3 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1743375 -> 1349623 acres",
  "pieces": [
   [
    "sgmtd1659",
    "Charles M. Russell National Wildlife Refuge",
    935823,
    "name"
   ],
   [
    "sgmtd1153",
    "Charles M. Russell National Wildlife Refuge Wilderness Study Area",
    19424,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 13,
 "same_agency": false,
 "score": 8,
 "t": "National Wildlife Refuge",
 "verdict": "agree"
}
```

## US-4504 Helena - Lewis and Clark National Forest
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Helena - Lewis and Clark National Forest",
 "official": {
  "acres": 2800000.0,
  "as": "2.8 million acres",
  "clean": true,
  "line": "T T T Welcome to the Helena-Lewis and Clark National Forest The Helena–Lewis and Clark National Forest spans 2.8 million acres across the heart of central and north‑central Montana, showcasing some of the state’s most iconic landscapes.",
  "read": "2026-11-09",
  "sent": "The Helena–Lewis and Clark National Forest spans 2.8 million acres across the heart of central and north‑central Montana, showcasing some of the state’s most iconic landscapes.",
  "url": "https://www.fs.usda.gov/hlcnf/",
  "why": "clean total"
 },
 "ours": {
  "acres": 3174124,
  "family_fold": "layers {'sgmtd': 3174124, 'padus': 2857363}: one land in 2 layers, the sgmtd copy used (2,857,363 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgmtd742",
    "Helena-Lewis & Clark National Forest",
    3174124,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 13,
 "same_agency": false,
 "score": 8,
 "t": "National Forest",
 "verdict": "agree"
}
```
