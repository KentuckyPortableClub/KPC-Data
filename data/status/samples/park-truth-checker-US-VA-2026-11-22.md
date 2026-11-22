# park truth checker: US-VA random sample of 12 (2026-11-22; seed = date + area, same rows for everyone)

Source file: `data/truth/US-VA.json`

## US-0726 Appomattox Court House National Historical Park
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Appomattox Court House National Historical Park",
 "official": null,
 "ours": {
  "acres": 1702,
  "dissolved": {
   "after": 2951,
   "before": 3518,
   "copies": 0,
   "families": {
    "padus": 1702,
    "sgvae": 1249
   },
   "family_fold": 1249,
   "family_used": "padus",
   "parts": 28,
   "records": 35,
   "tracts": 7
  },
  "family_fold": "layers {'padus': 1702, 'sgvae': 1249}: one land in 2 layers, the padus copy used (1,249 ac of copies not added)",
  "manager": "",
  "note": "35 joined records = 7 tracts: 0 copies of a tract (same acres, another layer) and 28 fee tracts under a designation record folded; summed 3518 -> 2951 acres",
  "pieces": [
   [
    3185,
    "Appomattox Court House National Historical Park",
    1702,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 3
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "National Historical Park",
 "verdict": "no size on page"
}
```

## US-9970 Marion Trout State Fish Hatchery
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Marion Trout State Fish Hatchery",
 "official": null,
 "ours": {
  "acres": 176,
  "dissolved": {
   "after": 281,
   "before": 528,
   "copies": 1,
   "families": {
    "padus": 176,
    "sgvae": 105
   },
   "family_fold": 105,
   "family_used": "padus",
   "parts": 2,
   "records": 6,
   "tracts": 3
  },
  "family_fold": "layers {'padus': 176, 'sgvae': 105}: one land in 2 layers, the padus copy used (105 ac of copies not added)",
  "manager": "",
  "note": "6 joined records = 3 tracts: 1 copies of a tract (same acres, another layer) and 2 fee tracts under a designation record folded; summed 528 -> 281 acres",
  "pieces": [
   [
    270532,
    "Marion Fish Hatchery",
    176,
    "words"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "State Fish Hatchery",
 "verdict": "no size on page"
}
```

## US-5517 Matthews State Forest
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Matthews State Forest",
 "official": {
  "acres": 566.0,
  "as": "566 acre",
  "clean": false,
  "line": "hed map are closed until further notice. Treatments will occur intermittently throughout August. Overview The 566-acre Matthews State Forest is located in Grayson County, just west of Galax. The mixed hardwood and white pine sta",
  "read": "2026-11-22",
  "sent": "The 566-acre Matthews State Forest is located in Grayson County, just west of Galax.",
  "url": "https://dof.virginia.gov/education-and-recreation/state-forests/virginia-state-forests/matthews-state-forest/",
  "why": "total-looking"
 },
 "ours": {
  "acres": 569,
  "dissolved": {
   "after": 734,
   "before": 2269,
   "copies": 2,
   "families": {
    "padus": 569,
    "sgvae": 165
   },
   "family_fold": 165,
   "family_used": "padus",
   "parts": 2,
   "records": 8,
   "tracts": 4
  },
  "family_fold": "layers {'padus': 569, 'sgvae': 165}: one land in 2 layers, the padus copy used (165 ac of copies not added)",
  "manager": "",
  "note": "8 joined records = 4 tracts: 2 copies of a tract (same acres, another layer) and 2 fee tracts under a designation record folded; summed 2269 -> 734 acres",
  "pieces": [
   [
    270423,
    "Judge Matthews State Forest",
    569,
    "words"
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
 "t": "State Forest",
 "verdict": "agree"
}
```

## US-3378 Blue Ridge National Parkway
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Blue Ridge National Parkway",
 "note": "whole park compared (POTA lists it in 2 states: {'US-VA': 35237, 'US-NC': 55449})",
 "official": null,
 "ours": {
  "acres": 90686,
  "acres_by_state": {
   "US-NC": 55449,
   "US-VA": 35237
  },
  "dissolved": {
   "after": 37910,
   "before": 39256,
   "copies": 0,
   "families": {
    "padus": 35237,
    "sgvae": 2673
   },
   "family_fold": 2673,
   "family_used": "padus",
   "parts": 32,
   "records": 38,
   "tracts": 6
  },
  "family_fold": "layers {'padus': 35237, 'sgvae': 2673}: one land in 2 layers, the padus copy used (2,673 ac of copies not added)",
  "manager": "",
  "note": "38 joined records = 6 tracts: 0 copies of a tract (same acres, another layer) and 32 fee tracts under a designation record folded; summed 39256 -> 37910 acres",
  "pieces": [
   [
    3546,
    "Blue Ridge Parkway",
    35237,
    "reviewed"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "states": [
   "US-VA",
   "US-NC"
  ],
  "unknown_pieces": 10,
  "whole_park": true
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "National Parkway",
 "verdict": "no size on page"
}
```

## US-9949 Mountain Lake Wilderness Area
```json
{
 "cause": "a number 17 parks share from one page (1,800,000 ac): an agency total, not this park",
 "checked": "2026-11-08",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Mountain Lake Wilderness Area",
 "note": "the agency figure may cover several states; our outline may be this state's share only",
 "official": null,
 "ours": {
  "acres": 16585,
  "family_fold": "layers {'wld': 16585, 'sgvae': 13305}: one land in 2 layers, the wld copy used (13,305 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "wld288",
    "Mountain Lake Wilderness",
    16585,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "same_agency": false,
 "score": 7,
 "t": "Wilderness Area",
 "verdict": "unsure"
}
```

## US-7789 Chub Sandhill State Natural Area
```json
{
 "cause": "a number 10 parks share from the same sentence (66,000 ac): an agency total, not this park",
 "checked": "2026-11-22",
 "handover": [],
 "n": "Chub Sandhill State Natural Area",
 "official": null,
 "ours": {
  "acres": 1066,
  "dissolved": {
   "after": 1745,
   "before": 4272,
   "copies": 5,
   "families": {
    "padus": 679,
    "sgvab": 1066
   },
   "family_fold": 679,
   "family_used": "sgvab",
   "parts": 3,
   "records": 12,
   "tracts": 4
  },
  "family_fold": "layers {'sgvab': 1066, 'padus': 679}: one land in 2 layers, the sgvab copy used (679 ac of copies not added)",
  "manager": "",
  "note": "12 joined records = 4 tracts: 5 copies of a tract (same acres, another layer) and 3 fee tracts under a designation record folded; summed 4272 -> 1745 acres",
  "pieces": [
   [
    "sgvab18",
    "Chub Sandhill",
    1066,
    "reviewed"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "same_agency": false,
 "score": 6,
 "t": "State Natural Area",
 "verdict": "unsure"
}
```

## US-1326 York River State Park
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "York River State Park",
 "official": {
  "acres": 2954.0,
  "as": "2,954 acres",
  "clean": false,
  "line": "e hour; Tidewater/Norfolk/Virginia Beach, one hour; Fredericksburg, two hours; Roanoke, five hours. Park Size 2,954 acres. Share this page Follow us Cabins, camping OVERNIGHT FACILITIES York River is a day-use park with no overnigh",
  "read": "2026-11-22",
  "sent": "2,954 acres.",
  "url": "https://www.dcr.virginia.gov/state-parks/york-river",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 2910,
  "dissolved": {
   "after": 5286,
   "before": 11573,
   "copies": 7,
   "families": {
    "padus": 2376,
    "sgvad": 2910
   },
   "family_fold": 2376,
   "family_used": "sgvad",
   "parts": 0,
   "records": 12,
   "tracts": 5
  },
  "family_fold": "layers {'sgvad': 2910, 'padus': 2376}: one land in 2 layers, the sgvad copy used (2,376 ac of copies not added)",
  "manager": "",
  "note": "12 joined records = 5 tracts: 7 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 11573 -> 5286 acres",
  "pieces": [
   [
    "sgvad165",
    "York River State Park",
    2509,
    "name"
   ],
   [
    "sgvad293",
    "York River State Park",
    401,
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

## US-9937 Meadowood BLM Special Recreation Management Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Meadowood BLM Special Recreation Management Area",
 "official": {
  "acres": 800.0,
  "as": "800 acres",
  "clean": false,
  "line": "miles of mountain biking trails. It is the site of 2 fishing ponds (one of which is universally accessible), 800 acres of forest and meadows, environmental education programs, equestrian facilities, geocaching, and bird watching",
  "read": "2026-11-22",
  "sent": "It is the site of 2 fishing ponds (one of which is universally accessible), 800 acres of forest and meadows, environmental education programs, equestrian facilities, geocaching, and bird watching.",
  "url": "https://www.blm.gov/visit/meadowood-special-recreation-management-area",
  "why": "part (a lake, a purchase, a campground…)"
 },
 "ours": {
  "acres": 751,
  "manager": "",
  "pieces": [
   [
    "sgvae491120",
    "Meadowood Farm",
    751,
    "name + Recreation.gov point inside (G-1, id 4112)"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 6,
 "same_agency": false,
 "score": 6,
 "t": "BLM Special Recreation Management Area",
 "verdict": "agree"
}
```

## US-0929 Fort Monroe National Monument
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Fort Monroe National Monument",
 "official": null,
 "ours": {
  "acres": 526,
  "family_fold": "layers {'sgvae': 565, 'padus': 122}: one land in 2 layers, the sgvae copy used (122 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgvae490590",
    "Fort Monroe National Monument",
    565,
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
 "t": "National Monument",
 "verdict": "no size on page"
}
```

## US-9948 Little Wilson Creek Wilderness Area
```json
{
 "cause": "a number 17 parks share from one page (1,800,000 ac): an agency total, not this park",
 "checked": "2026-11-08",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Little Wilson Creek Wilderness Area",
 "official": null,
 "ours": {
  "acres": 5463,
  "dissolved": {
   "after": 5463,
   "before": 10924,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 10924 -> 5463 acres",
  "pieces": [
   [
    "sgvae500389",
    "Little Wilson Creek NF Wilderness Area",
    5463,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "same_agency": false,
 "score": 6,
 "t": "Wilderness Area",
 "verdict": "unsure"
}
```

## US-0905 Booker T. Washington National Monument
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-11-22",
 "handover": [],
 "n": "Booker T. Washington National Monument",
 "official": null,
 "ours": {
  "acres": 244,
  "family_fold": "layers {'padus': 244, 'sgvae': 239}: one land in 2 layers, the padus copy used (239 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    3342,
    "Booker T. Washington National Monument",
    244,
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
 "t": "National Monument",
 "verdict": "unsure"
}
```

## US-9906 Cornelius Creek National Recreation Trail
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Cornelius Creek National Recreation Trail",
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
 "score": 4,
 "t": "National Recreation Trail",
 "verdict": "ours unknown"
}
```
