# park truth checker: US-LA random sample of 12 (2026-11-09; seed = date + area, same rows for everyone)

Source file: `data/truth/US-LA.json`

## US-10454 Rebel State Historic Site
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-09",
 "n": "Rebel State Historic Site",
 "official": null,
 "ours": {
  "acres": 12,
  "manager": "",
  "pieces": [
   [
    203103,
    "Rebel State Historic Site",
    12,
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

## US-4046 Bayou Pierre Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-09",
 "n": "Bayou Pierre Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 3129,
  "dissolved": {
   "after": 5108,
   "before": 10740,
   "copies": 2,
   "families": {
    "padus": 2271,
    "sglaa": 2837
   },
   "family_fold": 2271,
   "family_used": "sglaa",
   "key_union": 3129,
   "parts": 0,
   "records": 4,
   "summed": 2837,
   "tracts": 2
  },
  "family_fold": "layers {'sglaa': 2837, 'padus': 2271}: one land in 2 layers, the sglaa copy used (2,271 ac of copies not added)",
  "manager": "",
  "note": "4 joined records = 2 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 10740 -> 5108 acres",
  "pieces": [
   [
    "sglaa6",
    "Bayou Pierre WMA",
    2837,
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
 "t": "Wildlife Management Area",
 "verdict": "no size on page"
}
```

## US-4080 Timken Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-09",
 "n": "Timken Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 3053,
  "dissolved": {
   "after": 2867,
   "before": 11468,
   "copies": 3,
   "key_union": 3053,
   "parts": 0,
   "records": 4,
   "summed": 2867,
   "tracts": 1
  },
  "manager": "",
  "note": "4 joined records = 1 tracts: 3 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 11468 -> 2867 acres",
  "pieces": [
   [
    "law51",
    "Timken WMA",
    2867,
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

## US-4073 Pointe-aux-Chenes Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-09",
 "n": "Pointe-aux-Chenes Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 35730,
  "dissolved": {
   "after": 69218,
   "before": 139800,
   "copies": 2,
   "families": {
    "sglab": 33488,
    "sglac": 35730
   },
   "family_fold": 33488,
   "family_used": "sglac",
   "parts": 0,
   "records": 4,
   "tracts": 2
  },
  "family_fold": "layers {'sglac': 35730, 'sglab': 33488}: one land in 2 layers, the sglac copy used (33,488 ac of copies not added)",
  "manager": "",
  "note": "4 joined records = 2 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 139800 -> 69218 acres",
  "pieces": [
   [
    "sglac57",
    "Pointe aux Chenes WMA",
    35730,
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

## US-0304 Cameron Prairie National Wildlife Refuge
```json
{
 "cause": "agency smaller: our outline may hold water, a lease or a neighbour tract",
 "checked": "2026-11-09",
 "handover": [
  {
   "date_hint": "2001",
   "kind": "transfer",
   "line": "at, was established in 1937 as part of Sabine National Wildlife Refuge. This unit, administratively transferred to Cameron Prairie National Wildlife Refuge from Sabine in 2001, consists of 14,927 acres of brackish to intermediate marsh. These marshes are managed as a nursery for brown and white shri",
   "owner_now": "Cameron Prairie National Wildlife Refuge",
   "src": "https://www.fws.gov/refuge/cameron-prairie",
   "why": "the park's page (data/parkinfo)"
  }
 ],
 "n": "Cameron Prairie National Wildlife Refuge",
 "official": {
  "acres": 14927.0,
  "as": "14,927 acres",
  "clean": true,
  "line": "it, administratively transferred to Cameron Prairie National Wildlife Refuge from Sabine in 2001, consists of 14,927 acres of brackish to intermediate marsh. These marshes are managed as a nursery for brown and white shrimp, blue cr",
  "read": "2026-11-09",
  "sent": "This unit, administratively transferred to Cameron Prairie National Wildlife Refuge from Sabine in 2001, consists of 14,927 acres of brackish to intermediate marsh.",
  "url": "https://www.fws.gov/refuge/cameron-prairie",
  "why": "clean total"
 },
 "ours": {
  "acres": 25904,
  "dissolved": {
   "after": 24392,
   "before": 48783,
   "copies": 1,
   "key_union": 25904,
   "parts": 0,
   "records": 2,
   "summed": 24392,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 48783 -> 24392 acres",
  "pieces": [
   [
    4622,
    "Cameron Prairie National Wildlife Refuge",
    24392,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": "Cameron Prairie National Wildlife Refuge",
 "pct": 74,
 "same_agency": false,
 "score": 6,
 "t": "National Wildlife Refuge",
 "verdict": "off"
}
```

## US-4062 Joyce Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-09",
 "n": "Joyce Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 43003,
  "dissolved": {
   "after": 59363,
   "before": 144574,
   "copies": 2,
   "families": {
    "padus": 16360,
    "sglac": 43003
   },
   "family_fold": 16360,
   "family_used": "sglac",
   "parts": 0,
   "records": 4,
   "tracts": 2
  },
  "family_fold": "layers {'sglac': 43003, 'padus': 16360}: one land in 2 layers, the sglac copy used (16,360 ac of copies not added)",
  "manager": "",
  "note": "4 joined records = 2 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 144574 -> 59363 acres",
  "pieces": [
   [
    "sglac55",
    "Joyce WMA",
    43003,
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

## US-0314 Mandalay National Wildlife Refuge
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Mandalay National Wildlife Refuge",
 "official": {
  "acres": 4212.0,
  "as": "4,212 acres",
  "clean": true,
  "line": "nting. Located approximately five miles southwest of Houma, LA, Mandalay National Wildlife Refuge encompasses 4,212 acres of freshwater marsh, cypress-tupelo swamp and man-made canals, and is bisected by the Gulf Intracoastal Water",
  "read": "2026-11-09",
  "sent": "Located approximately five miles southwest of Houma, LA, Mandalay National Wildlife Refuge encompasses 4,212 acres of freshwater marsh, cypress-tupelo swamp and man-made canals, and is bisected by the Gulf Intracoastal Waterway.",
  "url": "https://www.fws.gov/refuge/mandalay/visit-us",
  "why": "clean total"
 },
 "ours": {
  "acres": 4735,
  "dissolved": {
   "after": 4390,
   "before": 8780,
   "copies": 1,
   "key_union": 4735,
   "parts": 0,
   "records": 2,
   "summed": 4390,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 8780 -> 4390 acres",
  "pieces": [
   [
    4070,
    "Mandalay National Wildlife Refuge",
    4390,
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
 "t": "National Wildlife Refuge",
 "verdict": "agree"
}
```

## US-10456 Esler Field Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-09",
 "n": "Esler Field Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 12594,
  "manager": "",
  "pieces": [
   [
    "sglac14",
    "Esler Field WMA",
    12594,
    "reviewed"
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

## US-4061 J. C. 'Sonny' Gilbert Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-09",
 "n": "J. C. 'Sonny' Gilbert Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 7524,
  "dissolved": {
   "after": 7524,
   "before": 30042,
   "copies": 3,
   "parts": 0,
   "records": 4,
   "tracts": 1
  },
  "manager": "",
  "note": "4 joined records = 1 tracts: 3 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 30042 -> 7524 acres",
  "pieces": [
   [
    "sglab22",
    "J. C. “Sonny” Gilbert",
    7524,
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

## US-4085 Tangipahoa Parish School Board Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-09",
 "n": "Tangipahoa Parish School Board Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 1142,
  "dissolved": {
   "after": 1665,
   "before": 6638,
   "copies": 3,
   "key_union": 1142,
   "parts": 0,
   "records": 4,
   "summed": 1665,
   "tracts": 1
  },
  "manager": "",
  "note": "4 joined records = 1 tracts: 3 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 6638 -> 1665 acres",
  "pieces": [
   [
    "law50",
    "Tangipahoa Parish School Board WMA",
    1665,
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

## US-4055 Clear Creek Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-09",
 "n": "Clear Creek Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 52629,
  "dissolved": {
   "after": 52629,
   "before": 210433,
   "copies": 3,
   "parts": 0,
   "records": 4,
   "tracts": 1
  },
  "manager": "",
  "note": "4 joined records = 1 tracts: 3 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 210433 -> 52629 acres",
  "pieces": [
   [
    "law15",
    "Clear Creek WMA",
    52629,
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

## US-6445 St. Tammany Wildlife Refuge
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-09",
 "n": "St. Tammany Wildlife Refuge",
 "official": null,
 "ours": {
  "acres": 1082,
  "dissolved": {
   "after": 2301,
   "before": 4283,
   "copies": 2,
   "families": {
    "lar": 1310,
    "law": 991
   },
   "family_fold": 991,
   "family_used": "lar",
   "key_union": 1082,
   "parts": 0,
   "records": 4,
   "summed": 1310,
   "tracts": 2
  },
  "family_fold": "layers {'lar': 1310, 'law': 991}: one land in 2 layers, the lar copy used (991 ac of copies not added)",
  "manager": "",
  "note": "4 joined records = 2 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 4283 -> 2301 acres",
  "pieces": [
   [
    "lar5",
    "St Tammany Wildlife Refuge",
    1310,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 5,
 "t": "Wildlife Refuge",
 "verdict": "no size on page"
}
```
