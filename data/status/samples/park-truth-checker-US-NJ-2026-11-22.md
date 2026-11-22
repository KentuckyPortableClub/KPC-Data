# park truth checker: US-NJ random sample of 12 (2026-11-22; seed = date + area, same rows for everyone)

Source file: `data/truth/US-NJ.json`

## US-8054 Thundergut Pond Wildlife Management Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Thundergut Pond Wildlife Management Area",
 "official": {
  "acres": 2511.2,
  "as": "2511.17 Acres",
  "clean": false,
  "line": "Thundergut Pond Wildlife Management Area Salem County - Alloway Township 2511.17 Acres Access to Sycamore Lake prohibited Jan 1st through July 31st for protection of Endangered Species Content may",
  "read": "2026-11-22",
  "sent": "2511.17 Acres",
  "url": "https://www.nj.gov/dep/fgw/pdf/wmaroadmaps/thundergut_pond_rd.pdf",
  "why": "a map label (no sentence)"
 },
 "ours": {
  "acres": 2222,
  "dissolved": {
   "after": 3529,
   "before": 6660,
   "copies": 1,
   "families": {
    "padus": 1307,
    "sgnjb": 2222
   },
   "family_fold": 1307,
   "family_used": "sgnjb",
   "parts": 8,
   "records": 16,
   "tracts": 7
  },
  "family_fold": "layers {'sgnjb': 2222, 'padus': 1307}: one land in 2 layers, the sgnjb copy used (1,307 ac of copies not added)",
  "manager": "",
  "note": "16 joined records = 7 tracts: 1 copies of a tract (same acres, another layer) and 8 fee tracts under a designation record folded; summed 6660 -> 3529 acres",
  "pieces": [
   [
    "sgnjb222",
    "Thundergut Pond Wildlife Management Area",
    2222,
    "reviewed"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 12,
 "same_agency": false,
 "score": 8,
 "t": "Wildlife Management Area",
 "verdict": "agree"
}
```

## US-11338 Stow Creek State Park
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Stow Creek State Park",
 "official": null,
 "ours": {
  "acres": 1040,
  "dissolved": {
   "after": 1040,
   "before": 3117,
   "copies": 1,
   "parts": 8,
   "records": 10,
   "tracts": 1
  },
  "manager": "",
  "note": "10 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 8 fee tracts under a designation record folded; summed 3117 -> 1040 acres",
  "pieces": [
   [
    76478,
    "Stow Creek State Park",
    1040,
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

## US-8051 Sparta Mountain Wildlife Management Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Sparta Mountain Wildlife Management Area",
 "official": {
  "acres": 3461.2,
  "as": "3,461.20 Acres",
  "clean": false,
  "line": "ta Mountain Wildlife Management Area Morris County - Jefferson Township Sussex - Hardyston & Sparta Townships 3,461.20 Acres 0120.5 Miles Department of Environmental Protection New Jersey Division of Fish and Wildlife WMA Boundary Par",
  "read": "2026-11-22",
  "sent": "3,461.20 Acres",
  "url": "https://www.nj.gov/dep/fgw/pdf/wmaroadmaps/sparta_mountain_rd.pdf",
  "why": "a map label (no sentence)"
 },
 "ours": {
  "acres": 3373,
  "dissolved": {
   "after": 5253,
   "before": 6746,
   "copies": 0,
   "families": {
    "padus": 1880,
    "sgnjb": 3373
   },
   "family_fold": 1880,
   "family_used": "sgnjb",
   "parts": 5,
   "records": 11,
   "tracts": 6
  },
  "family_fold": "layers {'sgnjb': 3373, 'padus': 1880}: one land in 2 layers, the sgnjb copy used (1,880 ac of copies not added)",
  "manager": "",
  "note": "11 joined records = 6 tracts: 0 copies of a tract (same acres, another layer) and 5 fee tracts under a designation record folded; summed 6746 -> 5253 acres",
  "pieces": [
   [
    "sgnjb272",
    "Sparta Mountain Wildlife Management Area",
    3373,
    "reviewed"
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
 "t": "Wildlife Management Area",
 "verdict": "agree"
}
```

## US-8050 Salem River Wildlife Management Area
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-11-22",
 "handover": [],
 "n": "Salem River Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 2735,
  "dissolved": {
   "after": 3405,
   "before": 8470,
   "copies": 2,
   "key_union": 2735,
   "parts": 18,
   "records": 25,
   "summed": 3405,
   "tracts": 5
  },
  "manager": "",
  "note": "25 joined records = 5 tracts: 2 copies of a tract (same acres, another layer) and 18 fee tracts under a designation record folded; summed 8470 -> 3405 acres",
  "pieces": [
   [
    76269,
    "Salem River Wildlife Management Area",
    2763,
    "name"
   ],
   [
    228803,
    "Salem River Wildlife Management Area",
    517,
    "name"
   ],
   [
    228811,
    "Salem River Wildlife Management Area",
    111,
    "name"
   ],
   [
    228801,
    "Salem River Wildlife Management Area",
    9,
    "name"
   ],
   [
    228818,
    "Salem River Wildlife Management Area",
    5,
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
 "t": "Wildlife Management Area",
 "verdict": "unsure"
}
```

## US-13149 Beaver Brook Wildlife Management Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Beaver Brook Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 654,
  "dissolved": {
   "after": 654,
   "before": 1957,
   "copies": 1,
   "parts": 5,
   "records": 8,
   "tracts": 2
  },
  "manager": "",
  "note": "8 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 5 fee tracts under a designation record folded; summed 1957 -> 654 acres",
  "pieces": [
   [
    "sgnjb271",
    "Beaver Brook Wildlife Management Area",
    653,
    "reviewed"
   ],
   [
    227900,
    "Beaver Brook Wildlife Management Area",
    1,
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

## US-8038 Egg Island Wildlife Management Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Egg Island Wildlife Management Area",
 "official": {
  "acres": 8992.0,
  "as": "8,991.96 Acres",
  "clean": false,
  "line": "Egg Island Wildlife Management Area Cumberland County - Downe Township 8,991.96 Acres 0120.5 Miles Content may not reflect National Geographic's current map policy. Sources: National Geographic,",
  "read": "2026-11-22",
  "sent": "8,991.96 Acres",
  "url": "https://www.nj.gov/dep/fgw/pdf/wmaroadmaps/egg_island_rd.pdf",
  "why": "a map label (no sentence)"
 },
 "ours": {
  "acres": 8139,
  "dissolved": {
   "after": 14457,
   "before": 17446,
   "copies": 1,
   "families": {
    "padus": 6318,
    "sgnjb": 8139
   },
   "family_fold": 6318,
   "family_used": "sgnjb",
   "parts": 5,
   "records": 16,
   "tracts": 10
  },
  "family_fold": "layers {'sgnjb': 8139, 'padus': 6318}: one land in 2 layers, the sgnjb copy used (6,318 ac of copies not added)",
  "manager": "",
  "note": "16 joined records = 10 tracts: 1 copies of a tract (same acres, another layer) and 5 fee tracts under a designation record folded; summed 17446 -> 14457 acres",
  "pieces": [
   [
    "sgnjb263",
    "Egg Island Wildlife Management Area",
    8139,
    "reviewed"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 9,
 "same_agency": false,
 "score": 8,
 "t": "Wildlife Management Area",
 "verdict": "agree"
}
```

## US-1629 Rancocas State Park
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Rancocas State Park",
 "official": null,
 "ours": {
  "acres": 1479,
  "dissolved": {
   "after": 1479,
   "before": 4426,
   "copies": 1,
   "parts": 6,
   "records": 9,
   "tracts": 2
  },
  "manager": "",
  "note": "9 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 6 fee tracts under a designation record folded; summed 4426 -> 1479 acres",
  "pieces": [
   [
    "sgnjb177",
    "Rancocas State Park",
    1478,
    "reviewed"
   ],
   [
    227292,
    "Rancocas State Park",
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

## US-0746 Morristown National Historical Park
```json
{
 "checked": "2026-11-22",
 "handover": [
  {
   "date_hint": null,
   "kind": "managed by",
   "line": "mprovements, get links to detailed policies and regulations, and more. Bookstore The park bookstore is operated by Eastern National, a non-profit cooperating association which operates stores at over 150 National Park Service sites",
   "owner_now": "Eastern National",
   "src": "https://www.nps.gov/morr/learn/index.htm",
   "why": "about / history page of the park's site"
  }
 ],
 "n": "Morristown National Historical Park",
 "official": null,
 "ours": {
  "acres": 1685,
  "manager": "",
  "pieces": [
   [
    3227,
    "Morristown National Historical Park",
    1685,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": "Eastern National",
 "pct": null,
 "score": 6,
 "t": "National Historical Park",
 "verdict": "no size on page"
}
```

## US-1607 Allaire State Park
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Allaire State Park",
 "official": null,
 "ours": {
  "acres": 3439,
  "dissolved": {
   "after": 6209,
   "before": 6840,
   "copies": 0,
   "families": {
    "padus": 2770,
    "sgnjb": 3439
   },
   "family_fold": 2770,
   "family_used": "sgnjb",
   "parts": 12,
   "records": 20,
   "tracts": 8
  },
  "family_fold": "layers {'sgnjb': 3439, 'padus': 2770}: one land in 2 layers, the sgnjb copy used (2,770 ac of copies not added)",
  "manager": "",
  "note": "20 joined records = 8 tracts: 0 copies of a tract (same acres, another layer) and 12 fee tracts under a designation record folded; summed 6840 -> 6209 acres",
  "pieces": [
   [
    "sgnjb311",
    "Allaire State Park",
    3439,
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

## US-1622 Kittatinny Valley State Park
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Kittatinny Valley State Park",
 "official": null,
 "ours": {
  "acres": 3537,
  "dissolved": {
   "after": 4519,
   "before": 9147,
   "copies": 0,
   "families": {
    "padus": 982,
    "sgnjb": 3537
   },
   "family_fold": 982,
   "family_used": "sgnjb",
   "parts": 17,
   "records": 20,
   "tracts": 3
  },
  "family_fold": "layers {'sgnjb': 3537, 'padus': 982}: one land in 2 layers, the sgnjb copy used (982 ac of copies not added)",
  "manager": "",
  "note": "20 joined records = 3 tracts: 0 copies of a tract (same acres, another layer) and 17 fee tracts under a designation record folded; summed 9147 -> 4519 acres",
  "pieces": [
   [
    "sgnjb258",
    "Kittatinny Valley State Park",
    3537,
    "reviewed"
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

## US-1614 Double Trouble State Park
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Double Trouble State Park",
 "official": null,
 "ours": {
  "acres": 8865,
  "dissolved": {
   "after": 13943,
   "before": 17732,
   "copies": 0,
   "families": {
    "padus": 5078,
    "sgnjb": 8865
   },
   "family_fold": 5078,
   "family_used": "sgnjb",
   "parts": 4,
   "records": 14,
   "tracts": 10
  },
  "family_fold": "layers {'sgnjb': 8865, 'padus': 5078}: one land in 2 layers, the sgnjb copy used (5,078 ac of copies not added)",
  "manager": "",
  "note": "14 joined records = 10 tracts: 0 copies of a tract (same acres, another layer) and 4 fee tracts under a designation record folded; summed 17732 -> 13943 acres",
  "pieces": [
   [
    "sgnjb324",
    "Double Trouble State Park",
    8865,
    "reviewed"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 8
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-1628 Princeton Battlefield State Park
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Princeton Battlefield State Park",
 "official": null,
 "ours": {
  "acres": 88,
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
   "key_union": 88,
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
