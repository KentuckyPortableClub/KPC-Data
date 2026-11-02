# park truth checker: US-GA random sample of 12 (2026-11-01; seed = date + area, same rows for everyone)

Source file: `data/truth/US-GA.json`

## US-3775 Silver Lake Wildlife Management Area
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Silver Lake Wildlife Management Area",
 "official": {
  "acres": 9200.0,
  "as": "9,200 acre",
  "clean": true,
  "line": "e HOW TO HUNT AND FISH FOR A LIFETIME Previous Next Silver Lake WMA Silver Lake Wildlife Management Area is a 9,200-acre property located in southern Decatur County. This WMA offers hunting opportunities for deer, turkey, small ga",
  "read": "2026-10-29",
  "sent": "Silver Lake Wildlife Management Area is a 9,200-acre property located in southern Decatur County.",
  "url": "https://georgiawildlife.com/silver-lake-wma",
  "why": "clean total"
 },
 "ours": {
  "acres": 9749,
  "dissolved": {
   "after": 18233,
   "before": 27980,
   "copies": 1,
   "families": {
    "padus": 8484,
    "sggac": 9749
   },
   "family_fold": 8484,
   "family_used": "sggac",
   "parts": 0,
   "records": 3,
   "tracts": 2
  },
  "family_fold": "layers {'sggac': 9749, 'padus': 8484}: one land in 2 layers, the sggac copy used (8,484 ac of copies not added)",
  "manager": "",
  "note": "3 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 27980 -> 18233 acres",
  "pieces": [
   [
    "sggac788",
    "SILVER LAKE WMA",
    9749,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 6,
 "same_agency": false,
 "score": 8,
 "t": "Wildlife Management Area",
 "verdict": "agree"
}
```

## US-7135 Blue Ridge Wildlife Management Area
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Blue Ridge Wildlife Management Area",
 "official": {
  "acres": 20900.0,
  "as": "20,900 acre",
  "clean": false,
  "line": "xt Blue Ridge WMA Blue Ridge Wildlife Management Area is located in Fannin, Union, and Lumpkin counties. This 20,900-acre property offers hunting opportunities for deer, bear, turkey and small game. Over 31 miles of hiking trails a",
  "read": "2026-10-29",
  "sent": "This 20,900-acre property offers hunting opportunities for deer, bear, turkey and small game.",
  "url": "https://georgiawildlife.com/blue-ridge-wma",
  "why": "total-looking"
 },
 "ours": {
  "acres": 23191,
  "dissolved": {
   "after": 23191,
   "before": 69194,
   "copies": 2,
   "parts": 0,
   "records": 4,
   "tracts": 2
  },
  "manager": "",
  "note": "4 joined records = 2 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 69194 -> 23191 acres",
  "pieces": [
   [
    "sggaa12",
    "BLUE RIDGE WMA",
    23055,
    "name"
   ],
   [
    9154,
    "Blue Ridge Wildlife Management Area",
    136,
    "name"
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
 "t": "Wildlife Management Area",
 "verdict": "agree"
}
```

## US-3769 River Bend Wildlife Management Area
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "River Bend Wildlife Management Area",
 "official": {
  "acres": 3500.0,
  "as": "3,500 acre",
  "clean": true,
  "line": "unt. Those dates should be listed as a standard hunt. River Bend WMA River Bend Wildlife Management Area is a 3,500-acre property located in Laurens County approximately 8 miles south of East Dublin. River Bend consists of two tra",
  "read": "2026-10-29",
  "sent": "River Bend Wildlife Management Area is a 3,500-acre property located in Laurens County approximately 8 miles south of East Dublin.",
  "url": "https://georgiawildlife.com/river-bend-wma",
  "why": "clean total"
 },
 "ours": {
  "acres": 3676,
  "dissolved": {
   "after": 3676,
   "before": 11014,
   "copies": 2,
   "parts": 0,
   "records": 3,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 11014 -> 3676 acres",
  "pieces": [
   [
    195075,
    "River Bend Wildlife Management Area",
    3676,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 5,
 "same_agency": false,
 "score": 8,
 "t": "Wildlife Management Area",
 "verdict": "agree"
}
```

## US-0259 Banks Lake National Wildlife Refuge
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-10-29",
 "handover": [],
 "n": "Banks Lake National Wildlife Refuge",
 "official": null,
 "ours": {
  "acres": 2981,
  "dissolved": {
   "after": 2981,
   "before": 5962,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 5962 -> 2981 acres",
  "pieces": [
   [
    3606,
    "Banks Lake National Wildlife Refuge",
    2981,
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
 "t": "National Wildlife Refuge",
 "verdict": "unsure"
}
```

## US-3750 Flint River Wildlife Management Area
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Flint River Wildlife Management Area",
 "official": {
  "acres": 2300.0,
  "as": "2,300 acre",
  "clean": false,
  "line": "Flint River Wildlife Management Area is located along the east bank of the Flint River in Dooly County. This 2,300-acre property has opportunities for deer, turkey, small game, dove and feral hog hunting. Accommodations & Facilit",
  "read": "2026-10-29",
  "sent": "This 2,300-acre property has opportunities for deer, turkey, small game, dove and feral hog hunting.",
  "url": "https://georgiawildlife.com/flint-river-wma",
  "why": "total-looking"
 },
 "ours": {
  "acres": 2385,
  "dissolved": {
   "after": 2385,
   "before": 7141,
   "copies": 2,
   "parts": 0,
   "records": 3,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 7141 -> 2385 acres",
  "pieces": [
   [
    195039,
    "Flint River Wildlife Management Area",
    2385,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 4,
 "same_agency": false,
 "score": 8,
 "t": "Wildlife Management Area",
 "verdict": "agree"
}
```

## US-7897 Arrowhead Wildlife Management Area
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Arrowhead Wildlife Management Area",
 "official": {
  "acres": 338.0,
  "as": "338 acre",
  "clean": false,
  "line": "WD Hunting & Fishing Guide Now Available HOW TO HUNT AND FISH FOR A LIFETIME Previous Next Arrowhead WMA This 338-acre Wildlife Management Area is in Northwest Georgia (Floyd County). Mostly mature forest (primarily mixed pine h",
  "read": "2026-10-29",
  "sent": "This 338-acre Wildlife Management Area is in Northwest Georgia (Floyd County).",
  "url": "https://georgiawildlife.com/arrowhead-wma",
  "why": "total-looking"
 },
 "ours": {
  "acres": 348,
  "dissolved": {
   "after": 682,
   "before": 1016,
   "copies": 1,
   "families": {
    "padus": 348,
    "sggaa": 334
   },
   "family_fold": 334,
   "family_used": "padus",
   "parts": 0,
   "records": 3,
   "tracts": 2
  },
  "family_fold": "layers {'padus': 348, 'sggaa': 334}: one land in 2 layers, the padus copy used (334 ac of copies not added)",
  "manager": "",
  "note": "3 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1016 -> 682 acres",
  "pieces": [
   [
    195013,
    "Arrowhead Wildlife Management Area",
    348,
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
 "t": "Wildlife Management Area",
 "verdict": "agree"
}
```

## US-3778 Yuchi Wildlife Management Area
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-10-29",
 "handover": [],
 "n": "Yuchi Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 7703,
  "dissolved": {
   "after": 7703,
   "before": 22959,
   "copies": 2,
   "parts": 0,
   "records": 3,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 22959 -> 7703 acres",
  "pieces": [
   [
    195093,
    "Yuchi Wildlife Management Area",
    7703,
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
 "verdict": "unsure"
}
```

## US-3754 Hart County Wildlife Management Area
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Hart County Wildlife Management Area",
 "official": {
  "acres": 1000.0,
  "as": "1,000 acre",
  "clean": false,
  "line": "Previous Next Hart County WMA Hart County Wildlife Management Area is located just outside of Hartwell. This 1,000-acre property offers hunting opportunities for deer, bear, turkey, small game and dove. Activities Geocaching — no",
  "read": "2026-10-29",
  "sent": "This 1,000-acre property offers hunting opportunities for deer, bear, turkey, small game and dove.",
  "url": "https://georgiawildlife.com/hart-county-wma",
  "why": "total-looking"
 },
 "ours": {
  "acres": 990,
  "dissolved": {
   "after": 990,
   "before": 2962,
   "copies": 2,
   "parts": 0,
   "records": 3,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 2962 -> 990 acres",
  "pieces": [
   [
    195043,
    "Hart County Wildlife Management Area",
    990,
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
 "t": "Wildlife Management Area",
 "verdict": "agree"
}
```

## US-0952 Ocmulgee National Monument
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Ocmulgee National Monument",
 "official": null,
 "ours": {
  "acres": 1748,
  "manager": "",
  "pieces": [
   [
    3234,
    "Ocmulgee Mounds National Historical Park",
    1748,
    "reviewed"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "National Monument",
 "verdict": "no size on page"
}
```

## US-3739 Chickasawhatchee Wildlife Management Area
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Chickasawhatchee Wildlife Management Area",
 "official": {
  "acres": 19700.0,
  "as": "19,700 acre",
  "clean": false,
  "line": "t Chickasawhatchee WMA Chickasawhatchee Wildlife Management Area is located 12 miles southwest of Albany. The 19,700-acre WMA includes the Mike Commander Shooting Range, a managed dove field and campsites for tents and RVs. The pro",
  "read": "2026-10-29",
  "sent": "The 19,700-acre WMA includes the Mike Commander Shooting Range, a managed dove field and campsites for tents and RVs.",
  "url": "https://georgiawildlife.com/chickasawhatchee-wma",
  "why": "part (a lake, a purchase, a campground…)"
 },
 "ours": {
  "acres": 19716,
  "dissolved": {
   "after": 19716,
   "before": 59138,
   "copies": 2,
   "parts": 0,
   "records": 3,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 59138 -> 19716 acres",
  "pieces": [
   [
    195027,
    "Chickasawhatchee Wildlife Management Area",
    19716,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
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

## US-9786 Lake Seminole Wildlife Management Area
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Lake Seminole Wildlife Management Area",
 "official": {
  "acres": 8635.0,
  "as": "8,635 acres",
  "clean": false,
  "line": "Lake Seminole Wildlife Management Area consists of four separate tracts of land in southwest Georgia totaling 8,635 acres. Hunting opportunities include deer, turkey, and small game. No hunting is allowed within 200 yards of a hous",
  "read": "2026-10-29",
  "sent": "Lake Seminole Wildlife Management Area consists of four separate tracts of land in southwest Georgia totaling 8,635 acres.",
  "url": "https://georgiawildlife.com/lake-seminole-wma",
  "why": "history"
 },
 "ours": {
  "acres": 8147,
  "dissolved": {
   "after": 13570,
   "before": 29928,
   "copies": 9,
   "families": {
    "padus": 8147,
    "sggaa": 1556,
    "sggac": 3867
   },
   "family_fold": 5423,
   "family_used": "padus",
   "parts": 4,
   "records": 20,
   "tracts": 7
  },
  "family_fold": "layers {'padus': 8147, 'sggac': 3867, 'sggaa': 1556}: one land in 3 layers, the padus copy used (5,423 ac of copies not added)",
  "manager": "",
  "note": "20 joined records = 7 tracts: 9 copies of a tract (same acres, another layer) and 4 fee tracts under a designation record folded; summed 29928 -> 13570 acres",
  "pieces": [
   [
    194367,
    "Lake Seminole Wildlife Management Area",
    8147,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 6,
 "same_agency": false,
 "score": 8,
 "t": "Wildlife Management Area",
 "verdict": "agree"
}
```

## US-12418 Tallulah Gorge Wildlife Management Area
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Tallulah Gorge Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 2267,
  "dissolved": {
   "after": 2267,
   "before": 4534,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 4534 -> 2267 acres",
  "pieces": [
   [
    "sggaa184",
    "TALLULAH GORGE WMA",
    2267,
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
 "t": "Wildlife Management Area",
 "verdict": "no size on page"
}
```
