# park truth checker: US-CT random sample of 12 (2026-11-22; seed = date + area, same rows for everyone)

Source file: `data/truth/US-CT.json`

## US-1648 Bigelow Hollow State Park
```json
{
 "checked": "2026-11-17",
 "handover": [],
 "n": "Bigelow Hollow State Park",
 "official": {
  "acres": 515.0,
  "as": "515 acres",
  "clean": false,
  "line": "y & Environmental Protection - 79 Elm St. - Hartford, CT 06106 - www.ct.gov/deep Location: Union Description: 515 acres. Open for archery deer and fall archery turkey hunting only. Contiguous with Nipmuck State Forest to the east",
  "read": "2026-11-17",
  "sent": "Description: 515 acres.",
  "url": "https://portal.ct.gov/-/media/deep/wildlife/pdf_files/maps/maps_hunting_area/map46.pdf",
  "why": "a map label (no sentence)"
 },
 "ours": {
  "acres": 527,
  "dissolved": {
   "after": 527,
   "before": 1052,
   "copies": 1,
   "parts": 3,
   "records": 6,
   "tracts": 2
  },
  "manager": "",
  "note": "6 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 3 fee tracts under a designation record folded; summed 1052 -> 527 acres",
  "pieces": [
   [
    "sgcta4109",
    "Bigelow Hollow State Park",
    515,
    "name"
   ],
   [
    52514,
    "Bigelow Hollow State Park",
    12,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 4
 },
 "owner_now": null,
 "pct": 2,
 "same_agency": false,
 "score": 8,
 "t": "State Park",
 "verdict": "agree"
}
```

## US-1700 Mooween State Park
```json
{
 "checked": "2026-11-17",
 "handover": [],
 "n": "Mooween State Park",
 "official": null,
 "ours": {
  "acres": 592,
  "family_fold": "layers {'sgcta': 592, 'padus': 575}: one land in 2 layers, the sgcta copy used (575 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgcta4151",
    "Mooween State Park",
    592,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 5
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-1719 Squantz Pond State Park
```json
{
 "checked": "2026-11-17",
 "handover": [],
 "n": "Squantz Pond State Park",
 "official": {
  "acres": 172.0,
  "as": "172 acres",
  "clean": true,
  "line": "nd State Park offers a prized backdrop for boating, swimming, fishing, hiking, and leaf peeping. Encompassing 172 acres on the shore of Squantz Pond, a natural lake off Candlewood Lake, the park is a rare public space on the othe",
  "read": "2026-11-17",
  "sent": "Encompassing 172 acres on the shore of Squantz Pond, a natural lake off Candlewood Lake, the park is a rare public space on the otherwise private 75-mile shoreline.",
  "url": "https://portal.ct.gov/DEEP/State-Parks/Parks/Squantz-Pond-State-Park",
  "why": "clean total"
 },
 "ours": {
  "acres": 179,
  "manager": "",
  "pieces": [
   [
    "sgcta4159",
    "Squantz Pond State Park",
    170,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 3
 },
 "owner_now": null,
 "pct": 4,
 "same_agency": false,
 "score": 8,
 "t": "State Park",
 "verdict": "agree"
}
```

## US-10075 Nepaug State Forest
```json
{
 "checked": "2026-11-17",
 "handover": [],
 "n": "Nepaug State Forest",
 "official": {
  "acres": 1363.0,
  "as": "1,363 acres",
  "clean": false,
  "line": "Nepaug State Forest Location: New Hartford Description: 1,363 acres; mixed hardwoods, pine and spruce plantations; small swampy area. Open for small game, waterfowl, spring and",
  "read": "2026-11-17",
  "sent": "Description: 1,363 acres;",
  "url": "https://portal.ct.gov/-/media/deep/wildlife/pdf_files/maps/maps_hunting_area/map336.pdf",
  "why": "a map label (no sentence)"
 },
 "ours": {
  "acres": 1555,
  "dissolved": {
   "after": 1555,
   "before": 3219,
   "copies": 0,
   "parts": 14,
   "records": 17,
   "tracts": 3
  },
  "manager": "",
  "note": "17 joined records = 3 tracts: 0 copies of a tract (same acres, another layer) and 14 fee tracts under a designation record folded; summed 3219 -> 1555 acres",
  "pieces": [
   [
    "sgcta4091",
    "Nepaug State Forest",
    1525,
    "name"
   ],
   [
    53125,
    "Nepaug State Forest",
    28,
    "name"
   ],
   [
    53133,
    "Nepaug State Forest",
    2,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 19
 },
 "owner_now": null,
 "pct": 14,
 "same_agency": false,
 "score": 8,
 "t": "State Forest",
 "verdict": "agree"
}
```

## US-1660 Day Pond State Park
```json
{
 "checked": "2026-11-17",
 "handover": [],
 "n": "Day Pond State Park",
 "official": null,
 "ours": {
  "acres": 0,
  "manager": "",
  "pieces": [],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "State Park",
 "verdict": "ours unknown"
}
```

## US-1693 Machimoodus State Park
```json
{
 "cause": "agency smaller: our outline may hold water, a lease or a neighbour tract",
 "checked": "2026-11-17",
 "handover": [],
 "n": "Machimoodus State Park",
 "official": {
  "acres": 300.0,
  "as": "300 acres",
  "clean": false,
  "line": "orests Skip to main content Park Finder Park Maps Machimoodus State Park Moodus, CT Machimoodus State Park is 300 acres of uplands, woodlands, meadows, river and cove waterfronts, hiking trails, and scenic vistas overlooking the",
  "read": "2026-11-17",
  "sent": "Machimoodus State Park is 300 acres of uplands, woodlands, meadows, river and cove waterfronts, hiking trails, and scenic vistas overlooking the Salmon River and Salmon River Cove.",
  "url": "https://portal.ct.gov/DEEP/State-Parks/Parks/Machimoodus-State-Park",
  "why": "total-looking"
 },
 "ours": {
  "acres": 428,
  "family_fold": "layers {'sgcta': 300, 'padus': 144}: one land in 2 layers, the sgcta copy used (144 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgcta4175",
    "Machimoodus State Park",
    300,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 43,
 "same_agency": false,
 "score": 6,
 "t": "State Park",
 "verdict": "off"
}
```

## US-1703 Mount Tom State Park
```json
{
 "checked": "2026-11-17",
 "handover": [],
 "n": "Mount Tom State Park",
 "official": null,
 "ours": {
  "acres": 278,
  "family_fold": "layers {'sgcta': 236, 'padus': 243}: one land in 2 layers, the padus copy used (236 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    52659,
    "Mount Tom State Park",
    207,
    "name"
   ],
   [
    52655,
    "Mount Tom State Park",
    15,
    "name"
   ],
   [
    52658,
    "Mount Tom State Park",
    11,
    "name"
   ],
   [
    52656,
    "Mount Tom State Park",
    10,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 6
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-1691 Lovers Leap State Park
```json
{
 "cause": "agency smaller: our outline may hold water, a lease or a neighbour tract",
 "checked": "2026-11-17",
 "handover": [],
 "n": "Lovers Leap State Park",
 "official": {
  "acres": 160.0,
  "as": "160 acre",
  "clean": false,
  "line": "icking Overview Body Lovers Leap is a walk-in park with hiking trails, scenic vistas, and historic ruins. The 160-acre park is divided into three sections, each featuring a different appreciation for the park history. KNOW BEFOR",
  "read": "2026-11-17",
  "sent": "The 160-acre park is divided into three sections, each featuring a different appreciation for the park history.",
  "url": "https://portal.ct.gov/DEEP/State-Parks/Parks/Lovers-Leap-State-Park",
  "why": "total-looking"
 },
 "ours": {
  "acres": 204,
  "family_fold": "layers {'sgcta': 160, 'padus': 189}: one land in 2 layers, the padus copy used (160 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    52626,
    "Lovers Leap State Park Scenic Reserve",
    115,
    "name"
   ],
   [
    52625,
    "Lovers Leap State Park Scenic Reserve",
    74,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 7
 },
 "owner_now": null,
 "pct": 28,
 "same_agency": false,
 "score": 6,
 "t": "State Park",
 "verdict": "off"
}
```

## US-12628 Sessions Woods Wildlife Management Area
```json
{
 "checked": "2026-11-17",
 "handover": [],
 "n": "Sessions Woods Wildlife Management Area",
 "official": {
  "acres": 771.0,
  "as": "771 acres",
  "clean": false,
  "line": "Sessions Woods WMA Location: Burlington Access: Access off of Rt. 69. Description: 771 acres. Waterfowl hunting is not permitted. HUNTING BY DAILY PERMIT ONLY. Permit is available: https://portal.ct.gov",
  "read": "2026-11-17",
  "sent": "Description: 771 acres.",
  "url": "https://portal.ct.gov/-/media/deep/wildlife/pdf_files/maps/maps_hunting_area/map446.pdf",
  "why": "a map label (no sentence)"
 },
 "ours": {
  "acres": 772,
  "dissolved": {
   "after": 772,
   "before": 2316,
   "copies": 1,
   "parts": 2,
   "records": 4,
   "tracts": 1
  },
  "manager": "",
  "note": "4 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 2 fee tracts under a designation record folded; summed 2316 -> 772 acres",
  "pieces": [
   [
    52130,
    "Sessions Woods Wildlife Area",
    772,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 0,
 "same_agency": false,
 "score": 7,
 "t": "Wildlife Management Area",
 "verdict": "agree"
}
```

## US-9894 Topsmead State Forest
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 510 acre, no total words near it)",
 "checked": "2026-11-17",
 "handover": [],
 "n": "Topsmead State Forest",
 "official": {
  "acres": 510.0,
  "as": "510 acre",
  "clean": false,
  "line": "ted in 1925, the English Tudor Revival cottage was the country estate of Edith Morton Chase. Chase gifted the 510-acre state forest to the citizens of Connecticut. The exterior woodwork is of cypress, the downspouts are lead, th",
  "read": "2026-11-17",
  "sent": "Chase gifted the 510-acre state forest to the citizens of Connecticut.",
  "url": "https://portal.ct.gov/DEEP/State-Parks/Forests/Topsmead-State-Forest",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 669,
  "dissolved": {
   "after": 828,
   "before": 1459,
   "copies": 0,
   "families": {
    "padus": 1,
    "sgcta": 634,
    "sgctc": 193
   },
   "family_fold": 194,
   "family_used": "sgcta",
   "key_union": 669,
   "parts": 3,
   "records": 6,
   "summed": 634,
   "tracts": 3
  },
  "family_fold": "layers {'sgcta': 634, 'sgctc': 193, 'padus': 1}: one land in 3 layers, the sgcta copy used (194 ac of copies not added)",
  "manager": "",
  "note": "6 joined records = 3 tracts: 0 copies of a tract (same acres, another layer) and 3 fee tracts under a designation record folded; summed 1459 -> 828 acres",
  "pieces": [
   [
    "sgcta4102",
    "Topsmead State Forest",
    634,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 14
 },
 "owner_now": null,
 "pct": 31,
 "same_agency": false,
 "score": 7,
 "t": "State Forest",
 "verdict": "unsure"
}
```

## US-1674 Haddam Meadows State Park
```json
{
 "checked": "2026-11-17",
 "handover": [],
 "n": "Haddam Meadows State Park",
 "official": null,
 "ours": {
  "acres": 177,
  "manager": "",
  "pieces": [
   [
    "sgcta4123",
    "Haddam Meadows State Park",
    165,
    "name"
   ],
   [
    52558,
    "Haddam Meadows State Park",
    1,
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
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-1697 Millers Pond State Park
```json
{
 "checked": "2026-11-17",
 "handover": [],
 "n": "Millers Pond State Park",
 "official": {
  "acres": 265.0,
  "as": "265 acres",
  "clean": false,
  "line": "ental Protection - 79 Elm St. - Hartford, CT 06106 - www.ct.gov/deep Location: Durham and Haddam Description: 265 acres. Open for all forms of hunting. Access: Parking area off of Foot Hills Rd. Note: This map depicts an approxim",
  "read": "2026-11-17",
  "sent": "Description: 265 acres.",
  "url": "https://portal.ct.gov/-/media/deep/wildlife/pdf_files/maps/maps_hunting_area/map297.pdf",
  "why": "a map label (no sentence)"
 },
 "ours": {
  "acres": 298,
  "family_fold": "layers {'sgcta': 298, 'sgctc': 265, 'padus': 294}: one land in 3 layers, the sgcta copy used (559 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgcta4200",
    "Millers Pond State Park Scenic Reserve",
    298,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 3
 },
 "owner_now": null,
 "pct": 12,
 "same_agency": false,
 "score": 8,
 "t": "State Park",
 "verdict": "agree"
}
```
