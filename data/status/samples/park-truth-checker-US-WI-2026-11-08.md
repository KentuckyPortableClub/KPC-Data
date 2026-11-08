# park truth checker: US-WI random sample of 12 (2026-11-08; seed = date + area, same rows for everyone)

Source file: `data/truth/US-WI.json`

## US-10650 Nevin Springs State Fish and Wildlife Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Nevin Springs State Fish and Wildlife Area",
 "official": null,
 "ours": {
  "acres": 331,
  "manager": "",
  "pieces": [
   [
    272683,
    "Nevin Hatchery",
    331,
    "reviewed-approx"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 4,
 "t": "State Fish and Wildlife Area",
 "verdict": "no size on page"
}
```

## US-10189 Lundy Pond State Wildlife Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Lundy Pond State Wildlife Area",
 "official": {
  "acres": 35.0,
  "as": "35 acre",
  "clean": true,
  "line": "dIn Search Lands_Content Page_Lundy Pond Wildlife Area Lundy Pond Wildlife Area Lundy Pond Wildlife Area is a 35-acre property in northern St. Croix County. The property was purchased in 1973 to protect the large shallow lake w",
  "read": "2026-11-01",
  "sent": "Lundy Pond Wildlife Area is a 35-acre property in northern St.",
  "url": "https://dnr.wisconsin.gov/topic/Lands/WildlifeAreas/lundypond.html",
  "why": "clean total"
 },
 "ours": {
  "acres": 35,
  "manager": "",
  "pieces": [
   [
    272645,
    "Lundy Pond State Habitat Area-Western Prairie Habitat Restoration Area",
    35,
    "words"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 0,
 "same_agency": false,
 "score": 5,
 "t": "State Wildlife Area",
 "verdict": "agree"
}
```

## US-1463 Mill Bluff State Park
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Mill Bluff State Park",
 "official": null,
 "ours": {
  "acres": 1446,
  "dissolved": {
   "after": 3057,
   "before": 6439,
   "copies": 2,
   "families": {
    "sgwid": 1444,
    "wid": 1613
   },
   "family_fold": 1444,
   "family_used": "wid",
   "key_union": 1446,
   "parts": 26,
   "records": 74,
   "summed": 1613,
   "tracts": 46
  },
  "family_fold": "layers {'wid': 1613, 'sgwid': 1444}: one land in 2 layers, the wid copy used (1,444 ac of copies not added)",
  "manager": "",
  "note": "74 joined records = 46 tracts: 2 copies of a tract (same acres, another layer) and 26 fee tracts under a designation record folded; summed 6439 -> 3057 acres",
  "pieces": [
   [
    "wid710129",
    "Mill Bluff State Park",
    1613,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 8
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-4262 Pemene Falls Unit of Menominee River State Recreation Area
```json
{
 "cause": "whole park compared (POTA lists it in 1 states: {'US-WI': 4059})",
 "checked": "2026-11-01",
 "handover": [],
 "n": "Pemene Falls Unit of Menominee River State Recreation Area",
 "note": "whole park compared (POTA lists it in 1 states: {'US-WI': 4059})",
 "official": null,
 "ours": {
  "acres": 4059,
  "acres_by_state": {
   "US-WI": 4059
  },
  "manager": "",
  "pieces": [
   [
    272355,
    "Menominee River State Recreation Area",
    4785,
    "reviewed-approx"
   ],
   [
    78268,
    "Menominee River State Park & Recreation Area",
    41,
    "reviewed-approx"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "states": [
   "US-MI",
   "US-WI"
  ],
  "unknown_pieces": 0,
  "whole_park": true
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "State Recreation Area",
 "verdict": "unsure"
}
```

## US-13515 Eagle Lake State Fish and Wildlife Area
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-11-01",
 "handover": [],
 "n": "Eagle Lake State Fish and Wildlife Area",
 "official": null,
 "ours": {
  "acres": 114,
  "dissolved": {
   "after": 146,
   "before": 372,
   "copies": 4,
   "families": {
    "padus": 97,
    "sgwid": 49
   },
   "family_fold": 49,
   "family_used": "padus",
   "key_union": 114,
   "parts": 4,
   "records": 14,
   "summed": 97,
   "tracts": 6
  },
  "family_fold": "layers {'padus': 97, 'sgwid': 49}: one land in 2 layers, the padus copy used (49 ac of copies not added)",
  "manager": "",
  "note": "14 joined records = 6 tracts: 4 copies of a tract (same acres, another layer) and 4 fee tracts under a designation record folded; summed 372 -> 146 acres",
  "pieces": [
   [
    272530,
    "Eagle Lake Fishery Area",
    97,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 146
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "State Fish and Wildlife Area",
 "verdict": "unsure"
}
```

## US-12029 Alta State Fish and Wildlife Area
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-11-01",
 "handover": [],
 "n": "Alta State Fish and Wildlife Area",
 "official": null,
 "ours": {
  "acres": 139,
  "manager": "",
  "pieces": [
   [
    272418,
    "Alta Springs Fishery Area",
    139,
    "reviewed"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 5,
 "t": "State Fish and Wildlife Area",
 "verdict": "unsure"
}
```

## US-1440 Big Foot Beach State Park
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Big Foot Beach State Park",
 "official": null,
 "ours": {
  "acres": 253,
  "dissolved": {
   "after": 333,
   "before": 777,
   "copies": 1,
   "families": {
    "sgwia": 268,
    "sgwid": 65
   },
   "family_fold": 65,
   "family_used": "sgwia",
   "key_union": 253,
   "parts": 13,
   "records": 18,
   "summed": 268,
   "tracts": 4
  },
  "family_fold": "layers {'sgwia': 268, 'sgwid': 65}: one land in 2 layers, the sgwia copy used (65 ac of copies not added)",
  "manager": "",
  "note": "18 joined records = 4 tracts: 1 copies of a tract (same acres, another layer) and 13 fee tracts under a designation record folded; summed 777 -> 333 acres",
  "pieces": [
   [
    "sgwia710047",
    "Big Foot Beach State Park",
    268,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 27
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-4263 Piers Gorge Unit of Menominee River State Recreation Area
```json
{
 "cause": "whole park compared (POTA lists it in 2 states: {'US-MI': 596, 'US-WI': 5198})",
 "checked": "2026-11-01",
 "handover": [],
 "n": "Piers Gorge Unit of Menominee River State Recreation Area",
 "note": "whole park compared (POTA lists it in 2 states: {'US-MI': 596, 'US-WI': 5198})",
 "official": null,
 "ours": {
  "acres": 5794,
  "acres_by_state": {
   "US-MI": 596,
   "US-WI": 5198
  },
  "dissolved": {
   "after": 9418,
   "before": 14327,
   "copies": 1,
   "families": {
    "padus": 4785,
    "sgwid": 4633
   },
   "family_fold": 4633,
   "family_used": "padus",
   "key_union": 5198,
   "parts": 10,
   "records": 121,
   "summed": 4785,
   "tracts": 110
  },
  "family_fold": "layers {'padus': 4785, 'sgwid': 4633}: one land in 2 layers, the padus copy used (4,633 ac of copies not added)",
  "manager": "",
  "note": "121 joined records = 110 tracts: 1 copies of a tract (same acres, another layer) and 10 fee tracts under a designation record folded; summed 14327 -> 9418 acres",
  "pieces": [
   [
    272355,
    "Menominee River State Recreation Area",
    4785,
    "reviewed-approx"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "states": [
   "US-MI",
   "US-WI"
  ],
  "unknown_pieces": 4,
  "whole_park": true
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "State Recreation Area",
 "verdict": "unsure"
}
```

## US-9809 Oconto River State Trail
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Oconto River State Trail",
 "official": null,
 "ours": {
  "acres": 951,
  "dissolved": {
   "after": 140,
   "before": 325,
   "copies": 2,
   "families": {
    "padus": 88,
    "sgwid": 52
   },
   "family_fold": 52,
   "family_used": "padus",
   "key_union": 951,
   "parts": 6,
   "records": 27,
   "summed": 88,
   "tracts": 19
  },
  "family_fold": "layers {'padus': 88, 'sgwid': 52}: one land in 2 layers, the padus copy used (52 ac of copies not added)",
  "manager": "",
  "note": "27 joined records = 19 tracts: 2 copies of a tract (same acres, another layer) and 6 fee tracts under a designation record folded; summed 325 -> 140 acres",
  "pieces": [
   [
    272371,
    "Oconto River State Trail",
    88,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 13
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "State Trail",
 "verdict": "no size on page"
}
```

## US-4270 Balsam Branch State Wildlife Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Balsam Branch State Wildlife Area",
 "official": {
  "acres": 180.0,
  "as": "180 acre",
  "clean": true,
  "line": "h Lands_Content Page_Balsam Branch Wildlife Area Balsam Branch Wildlife Area Balsam Branch Wildlife Area is a 180-acre parcel in Polk County. It features a 20-acre lake surrounded by extensive cattail, sedge and other wetland ve",
  "read": "2026-11-01",
  "sent": "Balsam Branch Wildlife Area is a 180-acre parcel in Polk County.",
  "url": "https://dnr.wisconsin.gov/topic/Lands/WildlifeAreas/balsam.html",
  "why": "clean total"
 },
 "ours": {
  "acres": 175,
  "dissolved": {
   "after": 175,
   "before": 696,
   "copies": 2,
   "parts": 6,
   "records": 10,
   "tracts": 2
  },
  "manager": "",
  "note": "10 joined records = 2 tracts: 2 copies of a tract (same acres, another layer) and 6 fee tracts under a designation record folded; summed 696 -> 175 acres",
  "pieces": [
   [
    272430,
    "Balsam Branch Wildlife Area",
    174,
    "name"
   ],
   [
    "sgwid19673453",
    "Balsam Branch Wildlife Area",
    1,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 3,
 "same_agency": false,
 "score": 7,
 "t": "State Wildlife Area",
 "verdict": "agree"
}
```

## US-8673 La Crosse River State Trail
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "La Crosse River State Trail",
 "official": null,
 "ours": {
  "acres": 2063,
  "dissolved": {
   "after": 581,
   "before": 1255,
   "copies": 26,
   "families": {
    "padus": 326,
    "sgwid": 254,
    "wid": 1
   },
   "family_fold": 255,
   "family_used": "padus",
   "key_union": 2063,
   "parts": 0,
   "records": 111,
   "summed": 326,
   "tracts": 85
  },
  "family_fold": "layers {'padus': 326, 'sgwid': 254, 'wid': 1}: one land in 3 layers, the padus copy used (255 ac of copies not added)",
  "manager": "",
  "note": "111 joined records = 85 tracts: 26 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1255 -> 581 acres",
  "pieces": [
   [
    272348,
    "La Crosse River State Trail",
    326,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 69
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "State Trail",
 "verdict": "no size on page"
}
```

## US-10783 Bear Creek State Fish and Wildlife Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Bear Creek State Fish and Wildlife Area",
 "official": null,
 "ours": {
  "acres": 1006,
  "dissolved": {
   "after": 1390,
   "before": 3212,
   "copies": 3,
   "families": {
    "sgwid": 573,
    "wid": 817
   },
   "family_fold": 573,
   "family_used": "wid",
   "key_union": 1006,
   "parts": 31,
   "records": 53,
   "summed": 817,
   "tracts": 19
  },
  "family_fold": "layers {'wid': 817, 'sgwid': 573}: one land in 2 layers, the wid copy used (573 ac of copies not added)",
  "manager": "",
  "note": "53 joined records = 19 tracts: 3 copies of a tract (same acres, another layer) and 31 fee tracts under a designation record folded; summed 3212 -> 1390 acres",
  "pieces": [
   [
    "wid709062",
    "Bear Creek Fishery Area",
    763,
    "name"
   ],
   [
    "wid710351",
    "Bear Creek Fishery Area",
    54,
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
 "t": "State Fish and Wildlife Area",
 "verdict": "no size on page"
}
```
