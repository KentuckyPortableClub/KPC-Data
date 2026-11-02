# park truth checker: US-SC random sample of 12 (2026-10-29; seed = date + area, same rows for everyone)

Source file: `data/truth/US-SC.json`

## US-2914 Table Rock State Park
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Table Rock State Park",
 "official": null,
 "ours": {
  "acres": 3056,
  "family_fold": "layers {'sgscb': 3056, 'padus': 2850}: one land in 2 layers, the sgscb copy used (2,850 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgscb46",
    "Table Rock State Park",
    3056,
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

## US-9204 McBee Wildlife Management Area
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "McBee Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 1216,
  "dissolved": {
   "after": 1216,
   "before": 3642,
   "copies": 2,
   "parts": 0,
   "records": 3,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 3642 -> 1216 acres",
  "pieces": [
   [
    254092,
    "McBee Wildlife Management Area",
    1216,
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
 "verdict": "no size on page"
}
```

## US-2905 Lee State Park
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Lee State Park",
 "official": null,
 "ours": {
  "acres": 2645,
  "family_fold": "layers {'sgscb': 2645, 'padus': 1860}: one land in 2 layers, the sgscb copy used (1,860 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgscb30",
    "Lee State Park",
    2645,
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

## US-12107 Lake Cherokee State Fishing Lake
```json
{
 "cause": "agency smaller: our outline may hold water, a lease or a neighbour tract",
 "checked": "2026-10-29",
 "handover": [],
 "n": "Lake Cherokee State Fishing Lake",
 "official": {
  "acres": 50.0,
  "as": "50 acres",
  "clean": true,
  "line": "er, and catfish. General Information Property Location: Gaffney, SC 29340 Latitude: 35.042 Longitude: -81.572 Acreage: 50 County: Cherokee Property Type: Public Fishing Lake Hours of Operation: This lake is open 24 hours a day to fi",
  "read": "2026-10-29",
  "sent": "Acreage: 50 County: Cherokee",
  "url": "https://www.dnr.sc.gov/lakes/state/cherokee/index.html",
  "why": "clean total"
 },
 "ours": {
  "acres": 134,
  "dissolved": {
   "after": 184,
   "before": 234,
   "copies": 1,
   "families": {
    "padus": 134,
    "sgsca": 50
   },
   "family_fold": 50,
   "family_used": "padus",
   "parts": 0,
   "records": 3,
   "tracts": 2
  },
  "family_fold": "layers {'padus': 134, 'sgsca': 50}: one land in 2 layers, the padus copy used (50 ac of copies not added)",
  "manager": "",
  "note": "3 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 234 -> 184 acres",
  "pieces": [
   [
    254169,
    "Lake Cherokee",
    134,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 168,
 "same_agency": false,
 "score": 6,
 "t": "State Fishing Lake",
 "verdict": "off"
}
```

## US-3913 Tillman Sand Ridge Heritage Preserve
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-10-29",
 "n": "Tillman Sand Ridge Heritage Preserve",
 "official": null,
 "ours": {
  "acres": 1421,
  "family_fold": "layers {'sgscc': 1421, 'padus': 1317}: one land in 2 layers, the sgscc copy used (1,317 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgscc62",
    "Tillman Sand Ridge Heritage Preserve and Wildlife Management Area",
    1421,
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
 "t": "Heritage Preserve",
 "verdict": "no size on page"
}
```

## US-0521 Santee National Wildlife Refuge
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 350,000 acre, no total words near it)",
 "checked": "2026-10-29",
 "handover": [],
 "n": "Santee National Wildlife Refuge",
 "official": {
  "acres": 350000.0,
  "as": "350,000 acre",
  "clean": false,
  "line": "sin National Wildlife Refuge, steeped in cultural history and natural resources, is located within the larger 350,000-acre Ashepoo-Combahee-Edisto (ACE) Basin System, which represents one of the largest undeveloped wetland ecosystem",
  "read": "2026-10-29",
  "sent": "Hollings ACE Basin National Wildlife Refuge, steeped in cultural history and natural resources, is located within the larger 350,000-acre Ashepoo-Combahee-Edisto (ACE) Basin System, which represents one of the largest undeveloped wetland ecosystems remaining on the Atlantic Coast.",
  "url": "https://www.fws.gov/refuge/santee/about-us",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 4533,
  "dissolved": {
   "after": 4533,
   "before": 9063,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 9063 -> 4533 acres",
  "pieces": [
   [
    4311,
    "Santee National Wildlife Refuge",
    4533,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 99,
 "same_agency": false,
 "score": 6,
 "t": "National Wildlife Refuge",
 "verdict": "unsure"
}
```

## US-2883 Andrew Jackson State Park
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Andrew Jackson State Park",
 "official": null,
 "ours": {
  "acres": 325,
  "dissolved": {
   "after": 325,
   "before": 649,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 649 -> 325 acres",
  "pieces": [
   [
    "sgscb2",
    "Andrew Jackson State Park",
    325,
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

## US-2903 Lake Warren State Park
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Lake Warren State Park",
 "official": null,
 "ours": {
  "acres": 674,
  "family_fold": "layers {'sgscb': 452, 'padus': 674}: one land in 2 layers, the padus copy used (452 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    254565,
    "Lake Warren State Park",
    326,
    "name"
   ],
   [
    254171,
    "Lake George Warren",
    258,
    "words"
   ],
   [
    254564,
    "Lake Warren State Park",
    90,
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

## US-3907 Pee Dee Station Site Wildlife Management Area
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Pee Dee Station Site Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 2701,
  "dissolved": {
   "after": 5309,
   "before": 10711,
   "copies": 2,
   "families": {
    "padus": 2608,
    "sgsca": 2701
   },
   "family_fold": 2608,
   "family_used": "sgsca",
   "parts": 0,
   "records": 4,
   "tracts": 2
  },
  "family_fold": "layers {'sgsca': 2701, 'padus': 2608}: one land in 2 layers, the sgsca copy used (2,608 ac of copies not added)",
  "manager": "",
  "note": "4 joined records = 2 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 10711 -> 5309 acres",
  "pieces": [
   [
    "sgsca44",
    "Pee Dee Station",
    2701,
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
 "verdict": "no size on page"
}
```

## US-8146 Ditch Pond Heritage Preserve
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-10-29",
 "n": "Ditch Pond Heritage Preserve",
 "official": null,
 "ours": {
  "acres": 285,
  "dissolved": {
   "after": 285,
   "before": 568,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 568 -> 285 acres",
  "pieces": [
   [
    "sgscc6",
    "Ditch Pond Heritage Preserve and Wildlife Management Area",
    285,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 5,
 "t": "Heritage Preserve",
 "verdict": "no size on page"
}
```

## US-2894 Edisto Beach State Park
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Edisto Beach State Park",
 "official": {
  "acres": 1255.0,
  "as": "1255 acres",
  "clean": false,
  "line": "ach State Par k or enjoy some of the finest kayaking in South Carolina at Goodale State Park . BY THE NUMBERS 1255 acres make up this special park 4 miles of ADA accessible trails 1.5 miles of beach, laden with seashells 2 oceanfr",
  "read": "2026-10-29",
  "sent": "1255 acres make up this special park",
  "url": "https://southcarolinaparks.com/edisto-beach?gclid=CjwKCAjw9suYBhBIEiwA7iMhNN_FRu-xYosbERrkV81b55GXcG7X9DYg5CULFdNEqdnuAPlIAqrQNRoCbRUQAvD_BwE",
  "why": "total-looking"
 },
 "ours": {
  "acres": 1105,
  "family_fold": "layers {'sgscb': 1105, 'padus': 1024}: one land in 2 layers, the sgscb copy used (1,024 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgscb14",
    "Edisto Beach State Park",
    1105,
    "name"
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
 "t": "State Park",
 "verdict": "agree"
}
```

## US-3905 Marsh Wildlife Management Area
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Marsh Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 8654,
  "dissolved": {
   "after": 8654,
   "before": 34551,
   "copies": 3,
   "parts": 0,
   "records": 4,
   "tracts": 1
  },
  "manager": "",
  "note": "4 joined records = 1 tracts: 3 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 34551 -> 8654 acres",
  "pieces": [
   [
    "sgsca84",
    "Marsh WMA",
    8654,
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
