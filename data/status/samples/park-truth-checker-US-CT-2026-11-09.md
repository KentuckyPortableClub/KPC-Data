# park truth checker: US-CT random sample of 12 (2026-11-09; seed = date + area, same rows for everyone)

Source file: `data/truth/US-CT.json`

## US-7541 Salmon River State Forest
```json
{
 "cause": "agency smaller: our outline may hold water, a lease or a neighbour tract",
 "checked": "2026-11-09",
 "handover": [],
 "n": "Salmon River State Forest",
 "official": {
  "acres": 7000.0,
  "as": "7,000 acres",
  "clean": false,
  "line": "a picnic along the Salmon River or walk through one of Connecticut's historical covered bridges. With nearly 7,000 acres sprawling across the towns of Hebron, Marlborough, Colchester, East Haddam, and East Hampton, Salmon River St",
  "read": "2026-11-09",
  "sent": "With nearly 7,000 acres sprawling across the towns of Hebron, Marlborough, Colchester, East Haddam, and East Hampton, Salmon River State Forest is a wonderland of adventure, solitude, nature, and recreation.",
  "url": "https://portal.ct.gov/DEEP/State-Parks/Forests/Salmon-River-State-Forest",
  "why": "total-looking"
 },
 "ours": {
  "acres": 8846,
  "dissolved": {
   "after": 16686,
   "before": 19793,
   "copies": 0,
   "families": {
    "padus": 3083,
    "sgcta": 6623,
    "sgctc": 6980
   },
   "family_fold": 9706,
   "family_used": "sgctc",
   "key_union": 8846,
   "parts": 45,
   "records": 52,
   "summed": 6980,
   "tracts": 7
  },
  "family_fold": "layers {'sgctc': 6980, 'sgcta': 6623, 'padus': 3083}: one land in 3 layers, the sgctc copy used (9,706 ac of copies not added)",
  "manager": "",
  "note": "52 joined records = 7 tracts: 0 copies of a tract (same acres, another layer) and 45 fee tracts under a designation record folded; summed 19793 -> 16686 acres",
  "pieces": [
   [
    "sgctc178",
    "Salmon River State Forest",
    6980,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 76
 },
 "owner_now": null,
 "pct": 26,
 "same_agency": false,
 "score": 6,
 "t": "State Forest",
 "verdict": "off"
}
```

## US-1726 Wadsworth Falls State Park
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Wadsworth Falls State Park",
 "official": null,
 "ours": {
  "acres": 226,
  "family_fold": "layers {'sgcta': 284, 'padus': 177}: one land in 2 layers, the sgcta copy used (177 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgcta4162",
    "Wadsworth Falls State Park",
    284,
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

## US-1686 Kent Falls State Park
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Kent Falls State Park",
 "official": null,
 "ours": {
  "acres": 821,
  "dissolved": {
   "after": 753,
   "before": 987,
   "copies": 0,
   "families": {
    "padus": 526,
    "sgcta": 227
   },
   "family_fold": 227,
   "family_used": "padus",
   "key_union": 821,
   "parts": 5,
   "records": 10,
   "summed": 526,
   "tracts": 5
  },
  "family_fold": "layers {'padus': 526, 'sgcta': 227}: one land in 2 layers, the padus copy used (227 ac of copies not added)",
  "manager": "",
  "note": "10 joined records = 5 tracts: 0 copies of a tract (same acres, another layer) and 5 fee tracts under a designation record folded; summed 987 -> 753 acres",
  "pieces": [
   [
    52600,
    "Kent Falls State Park",
    312,
    "name"
   ],
   [
    52598,
    "Kent Falls State Park",
    160,
    "name"
   ],
   [
    52597,
    "Kent Falls State Park",
    47,
    "name"
   ],
   [
    51798,
    "Kent Falls State Park",
    7,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 11
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-1680 Hopemead State Park
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Hopemead State Park",
 "official": {
  "acres": 31.0,
  "as": "31 acres",
  "clean": false,
  "line": "nnecticut Department of Energy & Environmental Protection Other State Parks and Forests Above All State Park (31 acres) Warren/Litchfield Services: Walk-in Park (Undeveloped) Location: From the junction of Route 45 and Route 341",
  "read": "2026-11-09",
  "sent": "Above All State Park (31 acres) Warren/Litchfield",
  "url": "https://portal.ct.gov/DEEP/State-Parks/Locate-Park-Forest/Other-State-Parks-and-Forests",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 33,
  "manager": "",
  "pieces": [
   [
    "sgcta4193",
    "Hopemead State Park Scenic Reserve",
    59,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 6,
 "same_agency": false,
 "score": 8,
 "t": "State Park",
 "verdict": "agree"
}
```

## US-6869 Peoples State Forest
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Peoples State Forest",
 "official": null,
 "ours": {
  "acres": 3108,
  "dissolved": {
   "after": 3108,
   "before": 9314,
   "copies": 2,
   "parts": 0,
   "records": 3,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 9314 -> 3108 acres",
  "pieces": [
   [
    "sgctc12",
    "Peoples State Forest",
    3108,
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
 "t": "State Forest",
 "verdict": "no size on page"
}
```

## US-11712 Cromwell Meadows WMA Wildlife Management Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Cromwell Meadows WMA Wildlife Management Area",
 "official": {
  "acres": 548.0,
  "as": "548 acres",
  "clean": false,
  "line": "t. - Hartford, CT 06106 - www.ct.gov/dep Cromwell Meadows WMA Location: Cromwell and Middletown Description: 548 acres; mostly marsh, level ditching and some open upland area. Open for small game, waterfowl, pheasant, turkey and",
  "read": "2026-11-09",
  "sent": "Description: 548 acres;",
  "url": "https://portal.ct.gov/-/media/deep/wildlife/pdf_files/maps/maps_hunting_area/map110.pdf",
  "why": "a map label (no sentence)"
 },
 "ours": {
  "acres": 548,
  "family_fold": "layers {'sgctc': 548, 'sgcta': 504}: one land in 2 layers, the sgctc copy used (504 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgctc125",
    "Cromwell Meadows WMA",
    548,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 0,
 "same_agency": false,
 "score": 8,
 "t": "Wildlife Management Area",
 "verdict": "agree"
}
```

## US-1657 Collis P. Huntington State Park
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Collis P. Huntington State Park",
 "official": {
  "acres": 1017.0,
  "as": "1,017 acre",
  "clean": false,
  "line": "res of bears and wolves greet you as you enter the peaceful sanctuary of Collis P. Huntington State Park. The 1,017-acre park spreads across carefully preserved open fields and dense woodlands and features five ponds, a lagoon, 15",
  "read": "2026-11-09",
  "sent": "The 1,017-acre park spreads across carefully preserved open fields and dense woodlands and features five ponds, a lagoon, 15-acre Lake Hopewell, and ten miles of trails, including the Aspectuck Valley Trail which leads to the Centennial Watershed State Forest.",
  "url": "https://portal.ct.gov/DEEP/State-Parks/Parks/Collis-P-Huntington-State-Park",
  "why": "part (a lake, a purchase, a campground…)"
 },
 "ours": {
  "acres": 1043,
  "dissolved": {
   "after": 1043,
   "before": 2083,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 2083 -> 1043 acres",
  "pieces": [
   [
    "sgcta4114",
    "Collis P. Huntington State Park",
    1043,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "",
  "unknown_pieces": 8
 },
 "owner_now": null,
 "pct": 3,
 "same_agency": false,
 "score": 7,
 "t": "State Park",
 "verdict": "agree"
}
```

## US-7548 Pachaug State Forest
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Pachaug State Forest",
 "official": {
  "acres": 26477.0,
  "as": "26,477 acres",
  "clean": false,
  "line": "Maps Book Green Falls Campground Book Mount Misery Campground Pachaug State Forest Voluntown, CT Encompassing 26,477 acres of public lands, access roads, and trails across six towns, Pachaug State Forest is the largest in Connecticu",
  "read": "2026-11-09",
  "sent": "Encompassing 26,477 acres of public lands, access roads, and trails across six towns, Pachaug State Forest is the largest in Connecticut.",
  "url": "https://portal.ct.gov/DEEP/State-Parks/Forests/Pachaug-State-Forest",
  "why": "part (a lake, a purchase, a campground…)"
 },
 "ours": {
  "acres": 27501,
  "dissolved": {
   "after": 71960,
   "before": 72885,
   "copies": 2,
   "families": {
    "padus": 17055,
    "sgcta": 27501,
    "sgctc": 27404
   },
   "family_fold": 44459,
   "family_used": "sgcta",
   "parts": 30,
   "records": 78,
   "tracts": 46
  },
  "family_fold": "layers {'sgctc': 27404, 'sgcta': 27501, 'padus': 17055}: one land in 3 layers, the sgcta copy used (44,459 ac of copies not added)",
  "manager": "",
  "note": "78 joined records = 46 tracts: 2 copies of a tract (same acres, another layer) and 30 fee tracts under a designation record folded; summed 72885 -> 71960 acres",
  "pieces": [
   [
    "sgcta4094",
    "Pachaug State Forest",
    26662,
    "name"
   ],
   [
    "sgcta3986",
    "Pachaug Pond",
    839,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 227
 },
 "owner_now": null,
 "pct": 4,
 "same_agency": false,
 "score": 8,
 "t": "State Forest",
 "verdict": "agree"
}
```

## US-1658 Connecticut Valley Railroad State Park
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Connecticut Valley Railroad State Park",
 "official": null,
 "ours": {
  "acres": 1449,
  "family_fold": "layers {'sgcta': 148, 'padus': 155}: one land in 2 layers, the padus copy used (148 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    52527,
    "Connecticut Valley Railroad State Park Trail",
    102,
    "reviewed"
   ],
   [
    52526,
    "Connecticut Valley Railroad State Park Trail",
    31,
    "reviewed"
   ],
   [
    52528,
    "Connecticut Valley Railroad State Park Trail",
    12,
    "reviewed"
   ],
   [
    51778,
    "Connecticut Valley Railroad State Park Trail",
    6,
    "reviewed"
   ],
   [
    52529,
    "Connecticut Valley Railroad State Park Trail",
    4,
    "reviewed"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 12
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-1688 Killingly Pond State Park
```json
{
 "cause": "a number 4 parks share from one page (150 ac): an agency total, not this park",
 "checked": "2026-11-09",
 "handover": [],
 "n": "Killingly Pond State Park",
 "official": null,
 "ours": {
  "acres": 190,
  "dissolved": {
   "after": 338,
   "before": 512,
   "copies": 1,
   "families": {
    "padus": 164,
    "sgcta": 174
   },
   "family_fold": 164,
   "family_used": "sgcta",
   "key_union": 190,
   "parts": 0,
   "records": 7,
   "summed": 174,
   "tracts": 6
  },
  "family_fold": "layers {'sgcta': 174, 'padus': 164}: one land in 2 layers, the sgcta copy used (164 ac of copies not added)",
  "manager": "",
  "note": "7 joined records = 6 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 512 -> 338 acres",
  "pieces": [
   [
    "sgcta4196",
    "Killingly Pond State Park Scenic Reserve",
    174,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 9
 },
 "owner_now": null,
 "pct": null,
 "same_agency": false,
 "score": 6,
 "t": "State Park",
 "verdict": "unsure"
}
```

## US-1683 Hurd State Park
```json
{
 "cause": "agency smaller: our outline may hold water, a lease or a neighbour tract",
 "checked": "2026-11-09",
 "handover": [],
 "n": "Hurd State Park",
 "official": {
  "acres": 130.0,
  "as": "130 acres",
  "clean": false,
  "line": "ges at the park. The court decision fortunately favored the state and averted the possible desolation of some 130 acres of land! Views from the Park Location 74 Hurd Park Road East Hampton, CT 06424 Get Directions Details Open Da",
  "read": "2026-11-09",
  "sent": "The court decision fortunately favored the state and averted the possible desolation of some 130 acres of land!",
  "url": "https://portal.ct.gov/DEEP/State-Parks/Parks/Hurd-State-Park",
  "why": "total-looking"
 },
 "ours": {
  "acres": 858,
  "dissolved": {
   "after": 1721,
   "before": 1809,
   "copies": 0,
   "families": {
    "padus": 808,
    "sgcta": 913
   },
   "family_fold": 808,
   "family_used": "sgcta",
   "key_union": 858,
   "parts": 2,
   "records": 10,
   "summed": 913,
   "tracts": 8
  },
  "family_fold": "layers {'sgcta': 913, 'padus': 808}: one land in 2 layers, the sgcta copy used (808 ac of copies not added)",
  "manager": "",
  "note": "10 joined records = 8 tracts: 0 copies of a tract (same acres, another layer) and 2 fee tracts under a designation record folded; summed 1809 -> 1721 acres",
  "pieces": [
   [
    "sgcta4131",
    "Hurd State Park",
    913,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 9
 },
 "owner_now": null,
 "pct": 560,
 "same_agency": false,
 "score": 6,
 "t": "State Park",
 "verdict": "off"
}
```

## US-1698 Minnie Island State Park
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 25 acres, no total words near it)",
 "checked": "2026-11-09",
 "handover": [],
 "n": "Minnie Island State Park",
 "official": {
  "acres": 25.0,
  "as": "25 acres",
  "clean": false,
  "line": "ssion.) Fee: There is no parking fee at this park. Bolton Notch State Park Map Brainard Homestead State Park (25 acres) - East Haddam. Learn more about this park on the new CTParks.com page. Activities: Bird Watching, Field Spor",
  "read": "2026-11-09",
  "sent": "Brainard Homestead State Park (25 acres) - East Haddam.",
  "url": "https://portal.ct.gov/DEEP/State-Parks/Locate-Park-Forest/Other-State-Parks-and-Forests",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 1,
  "manager": "",
  "pieces": [
   [
    157497,
    "Minnie Island State Park Scenic Reserve",
    1,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 3
 },
 "owner_now": null,
 "pct": 96,
 "same_agency": false,
 "score": 6,
 "t": "State Park",
 "verdict": "unsure"
}
```
