# park truth checker: US-SC random sample of 12 (2026-11-01; seed = date + area, same rows for everyone)

Source file: `data/truth/US-SC.json`

## US-2900 Huntington Beach State Park
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Huntington Beach State Park",
 "official": null,
 "ours": {
  "acres": 1627,
  "dissolved": {
   "after": 1627,
   "before": 3252,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 3252 -> 1627 acres",
  "pieces": [
   [
    253935,
    "Huntington Beach State Park",
    1627,
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

## US-3888 Bonneau Ferry Wildlife Management Area
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 100 acres, no total words near it)",
 "checked": "2026-10-29",
 "handover": [],
 "n": "Bonneau Ferry Wildlife Management Area",
 "official": {
  "acres": 100.0,
  "as": "100 acres",
  "clean": false,
  "line": ". General Information Property Location: Highway 402 Cordesville, SC 29434 Latitude: 33.104 Longitude: -79.85 Acreage: 100 County: Berkeley Property Type: Public Fishing Lake Hours of Operation: Thursday - Sunday March 2 - October 31",
  "read": "2026-10-29",
  "sent": "Acreage: 100 County: Berkeley",
  "url": "https://www.dnr.sc.gov/lakes/state/bonneauferry/index.html",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 11112,
  "dissolved": {
   "after": 11112,
   "before": 97199,
   "copies": 12,
   "parts": 0,
   "records": 17,
   "tracts": 5
  },
  "manager": "",
  "note": "17 joined records = 5 tracts: 12 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 97199 -> 11112 acres",
  "pieces": [
   [
    "sgsca1",
    "Bonneau Ferry WMA",
    10712,
    "name"
   ],
   [
    "sgsca186",
    "Bonneau Ferry State Lakes",
    100,
    "name"
   ],
   [
    "sgsca203",
    "Bonneau Ferry State Lakes",
    100,
    "name"
   ],
   [
    "sgsca204",
    "Bonneau Ferry State Lakes",
    100,
    "name"
   ],
   [
    "sgsca205",
    "Bonneau Ferry State Lakes",
    100,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 11012,
 "same_agency": false,
 "score": 6,
 "t": "Wildlife Management Area",
 "verdict": "unsure"
}
```

## US-0522 Savannah National Wildlife Refuge
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Savannah National Wildlife Refuge",
 "note": "whole park compared (POTA lists it in 2 states: {'US-GA': 15461, 'US-SC': 15260})",
 "official": {
  "acres": 30000.0,
  "as": "30,000 acres",
  "clean": true,
  "line": "fowl. The refuge lies in both Georgia and South Carolina, divided by the Savannah River, and encompasses over 30,000 acres of vital wildlife habitat, including tidal freswater marsh and bottomland hardwood forest. Learn More About U",
  "read": "2026-10-29",
  "sent": "The refuge lies in both Georgia and South Carolina, divided by the Savannah River, and encompasses over 30,000 acres of vital wildlife habitat, including tidal freswater marsh and bottomland hardwood forest.",
  "url": "https://www.fws.gov/refuge/savannah/",
  "why": "clean total"
 },
 "ours": {
  "acres": 30721,
  "acres_by_state": {
   "US-GA": 15461,
   "US-SC": 15260
  },
  "dissolved": {
   "after": 15260,
   "before": 30520,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 30520 -> 15260 acres",
  "pieces": [
   [
    4318,
    "Savannah National Wildlife Refuge",
    15260,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "states": [
   "US-GA",
   "US-SC"
  ],
  "unknown_pieces": 0,
  "whole_park": true
 },
 "owner_now": null,
 "pct": 2,
 "same_agency": false,
 "score": 7,
 "t": "National Wildlife Refuge",
 "verdict": "agree"
}
```

## US-3914 Cathedral Bay Heritage Preserve
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-10-29",
 "n": "Cathedral Bay Heritage Preserve",
 "official": null,
 "ours": {
  "acres": 58,
  "family_fold": "layers {'sgscc': 58, 'padus': 52}: one land in 2 layers, the sgscc copy used (52 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgscc44",
    "Cathedral Bay Heritage Preserve",
    58,
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

## US-3902 James L. Mason Wildlife Management Area
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "James L. Mason Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 2078,
  "dissolved": {
   "after": 4073,
   "before": 6068,
   "copies": 1,
   "families": {
    "padus": 2078,
    "sgsca": 1995
   },
   "family_fold": 1995,
   "family_used": "padus",
   "parts": 0,
   "records": 3,
   "tracts": 2
  },
  "family_fold": "layers {'padus': 2078, 'sgsca': 1995}: one land in 2 layers, the padus copy used (1,995 ac of copies not added)",
  "manager": "",
  "note": "3 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 6068 -> 4073 acres",
  "pieces": [
   [
    254077,
    "James L. Mason Wildlife Management Area",
    2078,
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

## US-2902 Kings Mountain State Park
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Kings Mountain State Park",
 "official": null,
 "ours": {
  "acres": 6947,
  "dissolved": {
   "after": 6947,
   "before": 13855,
   "copies": 0,
   "parts": 2,
   "records": 3,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 0 copies of a tract (same acres, another layer) and 2 fee tracts under a designation record folded; summed 13855 -> 6947 acres",
  "pieces": [
   [
    "sgscb24",
    "Kings Mountain State Park",
    6947,
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

## US-0852 Ninety Six National Historic Site
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Ninety Six National Historic Site",
 "official": null,
 "ours": {
  "acres": 995,
  "manager": "",
  "pieces": [
   [
    3161,
    "Ninety Six National Historic Site",
    995,
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
 "t": "National Historic Site",
 "verdict": "no size on page"
}
```

## US-3883 Redcliffe Plantation State Historic Site
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Redcliffe Plantation State Historic Site",
 "official": null,
 "ours": {
  "acres": 367,
  "manager": "",
  "pieces": [
   [
    254537,
    "Redcliffe Plantation State Historic Site",
    367,
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
 "t": "State Historic Site",
 "verdict": "no size on page"
}
```

## US-3896 Edisto River Wildlife Management Area
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Edisto River Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 1542,
  "dissolved": {
   "after": 2935,
   "before": 6019,
   "copies": 2,
   "families": {
    "padus": 1393,
    "sgsca": 1542
   },
   "family_fold": 1393,
   "family_used": "sgsca",
   "parts": 0,
   "records": 4,
   "tracts": 2
  },
  "family_fold": "layers {'sgsca': 1542, 'padus': 1393}: one land in 2 layers, the sgsca copy used (1,393 ac of copies not added)",
  "manager": "",
  "note": "4 joined records = 2 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 6019 -> 2935 acres",
  "pieces": [
   [
    "sgsca105",
    "Edisto River WMA",
    1542,
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

## US-10467 James Ross Wildlife Reservation Wildlife Management Area
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "James Ross Wildlife Reservation Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 305,
  "dissolved": {
   "after": 305,
   "before": 915,
   "copies": 2,
   "parts": 0,
   "records": 3,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 915 -> 305 acres",
  "pieces": [
   [
    254078,
    "James Ross Wildlife Reservation",
    305,
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

## US-10415 Landsford Canal Forest Legacy Area Wildlife Management Area
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Landsford Canal Forest Legacy Area Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 1538,
  "dissolved": {
   "after": 2582,
   "before": 4120,
   "copies": 1,
   "families": {
    "padus": 1044,
    "sgsca": 1538
   },
   "family_fold": 1044,
   "family_used": "sgsca",
   "parts": 0,
   "records": 3,
   "tracts": 2
  },
  "family_fold": "layers {'sgsca': 1538, 'padus': 1044}: one land in 2 layers, the sgsca copy used (1,044 ac of copies not added)",
  "manager": "",
  "note": "3 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 4120 -> 2582 acres",
  "pieces": [
   [
    "sgsca83",
    "Landsford Canal Forest Legacy Area",
    1538,
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
 "t": "Wildlife Management Area",
 "verdict": "no size on page"
}
```
