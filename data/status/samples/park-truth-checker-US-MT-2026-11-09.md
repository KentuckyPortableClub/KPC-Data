# park truth checker: US-MT random sample of 12 (2026-11-09; seed = date + area, same rows for everyone)

Source file: `data/truth/US-MT.json`

## US-12923 Stuart Mill Bay State Fish and Wildlife Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Stuart Mill Bay State Fish and Wildlife Area",
 "official": null,
 "ours": {
  "acres": 232,
  "dissolved": {
   "after": 356,
   "before": 1424,
   "copies": 3,
   "key_union": 232,
   "parts": 0,
   "records": 4,
   "summed": 356,
   "tracts": 1
  },
  "manager": "",
  "note": "4 joined records = 1 tracts: 3 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1424 -> 356 acres",
  "pieces": [
   [
    211480,
    "Stuart Mill Bay Fishing Access Site",
    356,
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
 "t": "State Fish and Wildlife Area",
 "verdict": "no size on page"
}
```

## US-0407 Red Rock Lakes National Wildlife Refuge
```json
{
 "cause": "agency smaller: our outline may hold water, a lease or a neighbour tract",
 "checked": "2026-11-09",
 "handover": [],
 "n": "Red Rock Lakes National Wildlife Refuge",
 "official": {
  "acres": 32350.0,
  "as": "32,350 acres",
  "clean": false,
  "line": "Refuge is designated as wilderness. Some important information about the Refuge wilderness: Established 1976 32,350 acres Why Wilderness? The Wilderness Act of 1964 created the National Wilderness Preservation System \"in order to a",
  "read": "2026-11-09",
  "sent": "32,350 acres",
  "url": "https://www.fws.gov/refuge/red-rock-lakes/about-us",
  "why": "total-looking"
 },
 "ours": {
  "acres": 85482,
  "dissolved": {
   "after": 136888,
   "before": 188236,
   "copies": 1,
   "families": {
    "padus": 51406,
    "sgmtd": 85482
   },
   "family_fold": 51406,
   "family_used": "sgmtd",
   "parts": 0,
   "records": 3,
   "tracts": 2
  },
  "family_fold": "layers {'sgmtd': 85482, 'padus': 51406}: one land in 2 layers, the sgmtd copy used (51,406 ac of copies not added)",
  "manager": "",
  "note": "3 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 188236 -> 136888 acres",
  "pieces": [
   [
    "sgmtd208",
    "Red Rock Lakes National Wildlife Refuge",
    85482,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 164,
 "same_agency": false,
 "score": 6,
 "t": "National Wildlife Refuge",
 "verdict": "off"
}
```

## US-12648 Canyon Ferry Wildlife Management Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Canyon Ferry Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 29659,
  "dissolved": {
   "after": 29659,
   "before": 41499,
   "copies": 2,
   "parts": 0,
   "records": 4,
   "tracts": 2
  },
  "manager": "",
  "note": "4 joined records = 2 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 41499 -> 29659 acres",
  "pieces": [
   [
    2349,
    "Canyon Ferry Lake",
    23732,
    "name"
   ],
   [
    211499,
    "Canyon Ferry Wildlife Management Area",
    5927,
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

## US-12851 Castle Rock State Fish and Wildlife Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Castle Rock State Fish and Wildlife Area",
 "official": null,
 "ours": {
  "acres": 75,
  "dissolved": {
   "after": 81,
   "before": 324,
   "copies": 3,
   "key_union": 75,
   "parts": 0,
   "records": 4,
   "summed": 81,
   "tracts": 1
  },
  "manager": "",
  "note": "4 joined records = 1 tracts: 3 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 324 -> 81 acres",
  "pieces": [
   [
    211701,
    "Castle Rock Fishing Access Site",
    81,
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

## US-12903 Ninemile Prairie State Fish and Wildlife Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Ninemile Prairie State Fish and Wildlife Area",
 "official": null,
 "ours": {
  "acres": 15,
  "dissolved": {
   "after": 14,
   "before": 56,
   "copies": 3,
   "key_union": 15,
   "parts": 0,
   "records": 4,
   "summed": 14,
   "tracts": 1
  },
  "manager": "",
  "note": "4 joined records = 1 tracts: 3 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 56 -> 14 acres",
  "pieces": [
   [
    211466,
    "Ninemile Prairie Fishing Access Site",
    14,
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

## US-12657 Sun River Wildlife Management Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Sun River Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 19767,
  "dissolved": {
   "after": 19767,
   "before": 59257,
   "copies": 2,
   "parts": 0,
   "records": 3,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 59257 -> 19767 acres",
  "pieces": [
   [
    211616,
    "Sun River Wildlife Management Area",
    19767,
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

## US-12911 River Junction State Fish and Wildlife Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "River Junction State Fish and Wildlife Area",
 "official": null,
 "ours": {
  "acres": 864,
  "dissolved": {
   "after": 179,
   "before": 710,
   "copies": 3,
   "key_union": 864,
   "parts": 0,
   "records": 4,
   "summed": 179,
   "tracts": 1
  },
  "manager": "",
  "note": "4 joined records = 1 tracts: 3 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 710 -> 179 acres",
  "pieces": [
   [
    211471,
    "River Junction Fishing Access Site",
    179,
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
 "t": "State Fish and Wildlife Area",
 "verdict": "no size on page"
}
```

## US-12892 Manuel Lisa State Fish and Wildlife Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Manuel Lisa State Fish and Wildlife Area",
 "official": null,
 "ours": {
  "acres": 21,
  "dissolved": {
   "after": 33,
   "before": 132,
   "copies": 3,
   "key_union": 21,
   "parts": 0,
   "records": 4,
   "summed": 33,
   "tracts": 1
  },
  "manager": "",
  "note": "4 joined records = 1 tracts: 3 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 132 -> 33 acres",
  "pieces": [
   [
    211719,
    "Manuel Lisa Fishing Access Site",
    33,
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

## US-11217 Bluewater Springs Trout State Fish Hatchery
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Bluewater Springs Trout State Fish Hatchery",
 "official": {
  "acres": 51.1,
  "as": "51.1 acres",
  "clean": true,
  "line": "d Discharge of weapons prohibited year round. Location Region 5 Latitude/Longitude: 45.33109 -108.80016 Size: 51.1 acres Elevation: 3,970 ft Open: Jan 1 to Directions: Bluewater Springs Hatchery is located 8.5 miles east of Bridge",
  "read": "2026-11-09",
  "sent": "51.1 acres",
  "url": "https://myfwp.mt.gov/fwpPub/landsMgmt/siteDetail.action?lmsId=39753798",
  "why": "clean total"
 },
 "ours": {
  "acres": 51,
  "manager": "",
  "pieces": [
   [
    "sgmtd2999",
    "Bluewater Springs Trout Hatchery",
    51,
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
 "t": "State Fish Hatchery",
 "verdict": "agree"
}
```

## US-12864 Ennis State Fish and Wildlife Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Ennis State Fish and Wildlife Area",
 "official": null,
 "ours": {
  "acres": 43,
  "dissolved": {
   "after": 49,
   "before": 196,
   "copies": 3,
   "key_union": 43,
   "parts": 0,
   "records": 4,
   "summed": 49,
   "tracts": 1
  },
  "manager": "",
  "note": "4 joined records = 1 tracts: 3 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 196 -> 49 acres",
  "pieces": [
   [
    211542,
    "Ennis Fishing Access Site",
    49,
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
 "t": "State Fish and Wildlife Area",
 "verdict": "no size on page"
}
```

## US-0028 Glacier National Park
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Glacier National Park",
 "official": null,
 "ours": {
  "acres": 1007843,
  "dissolved": {
   "after": 1007843,
   "before": 2015597,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 2015597 -> 1007843 acres",
  "pieces": [
   [
    3442,
    "Glacier National Park",
    1007843,
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
 "t": "National Park",
 "verdict": "no size on page"
}
```

## US-12658 Blackleaf Wildlife Management Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Blackleaf Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 10764,
  "dissolved": {
   "after": 10764,
   "before": 32272,
   "copies": 2,
   "parts": 0,
   "records": 3,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 32272 -> 10764 acres",
  "pieces": [
   [
    211610,
    "Blackleaf Wildlife Management Area",
    10764,
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
