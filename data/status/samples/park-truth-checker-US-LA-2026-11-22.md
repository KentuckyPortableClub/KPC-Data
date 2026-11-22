# park truth checker: US-LA random sample of 12 (2026-11-22; seed = date + area, same rows for everyone)

Source file: `data/truth/US-LA.json`

## US-0304 Cameron Prairie National Wildlife Refuge
```json
{
 "cause": "agency smaller: our outline may hold water, a lease or a neighbour tract",
 "checked": "2026-11-22",
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
  "read": "2026-11-22",
  "sent": "This unit, administratively transferred to Cameron Prairie National Wildlife Refuge from Sabine in 2001, consists of 14,927 acres of brackish to intermediate marsh.",
  "url": "https://www.fws.gov/refuge/cameron-prairie",
  "why": "clean total"
 },
 "ours": {
  "acres": 24392,
  "dissolved": {
   "after": 24392,
   "before": 48783,
   "copies": 1,
   "parts": 0,
   "records": 2,
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
 "pct": 63,
 "same_agency": false,
 "score": 6,
 "t": "National Wildlife Refuge",
 "verdict": "off"
}
```

## US-0302 Bogue Chitto National Wildlife Refuge
```json
{
 "cause": "a number 4 parks share from the same sentence (18,000 ac): an agency total, not this park",
 "checked": "2026-11-22",
 "handover": [],
 "n": "Bogue Chitto National Wildlife Refuge",
 "official": null,
 "ours": {
  "acres": 29114,
  "dissolved": {
   "after": 29114,
   "before": 58089,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 58089 -> 29114 acres",
  "pieces": [
   [
    4582,
    "Bogue Chitto National Wildlife Refuge",
    29114,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "same_agency": false,
 "score": 5,
 "t": "National Wildlife Refuge",
 "verdict": "unsure"
}
```

## US-4069 Maurepas Swamp Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Maurepas Swamp Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 116604,
  "dissolved": {
   "after": 297796,
   "before": 410411,
   "copies": 1,
   "families": {
    "padus": 67503,
    "sglaa": 113689,
    "sglac": 116604
   },
   "family_fold": 181192,
   "family_used": "sglac",
   "parts": 0,
   "records": 5,
   "tracts": 4
  },
  "family_fold": "layers {'sglac': 116604, 'sglaa': 113689, 'padus': 67503}: one land in 3 layers, the sglac copy used (181,192 ac of copies not added)",
  "manager": "",
  "note": "5 joined records = 4 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 410411 -> 297796 acres",
  "pieces": [
   [
    "sglac56",
    "Maurepas Swamp WMA",
    116604,
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

## US-0316 Sabine National Wildlife Refuge
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 184,000 acres, no total words near it)",
 "checked": "2026-11-22",
 "handover": [
  {
   "date_hint": "2018",
   "kind": "managed by",
   "line": ", Sabine National Wildlife Refuge is one of over 560 refuges in the National Wildlife Refuge System administered by the U.S. Fish and Wildlife Service. PDF Aug 12, 2018 Name Sabine National Wildlife Refuge Wetland Walkway Brochure This one and one-half mile t",
   "owner_now": "U.S",
   "src": "https://www.fws.gov/refuge/sabine/visit-us",
   "why": "about / history page of the park's site"
  }
 ],
 "n": "Sabine National Wildlife Refuge",
 "official": {
  "acres": 184000.0,
  "as": "184,000 acres",
  "clean": false,
  "line": "ates and U.S. territories, all of which are administered by the U.S. Fish and Wildlife Service. The more than 184,000 acres of land contained within boundaries of the four National Wildlife Refuges in southwest Louisiana supports num",
  "read": "2026-11-22",
  "sent": "The more than 184,000 acres of land contained within boundaries of the four National Wildlife Refuges in southwest Louisiana supports numerous species of both plants and wildlife.",
  "url": "https://www.fws.gov/refuge/sabine/about-us",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 123815,
  "dissolved": {
   "after": 123815,
   "before": 247630,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 247630 -> 123815 acres",
  "pieces": [
   [
    4284,
    "Sabine National Wildlife Refuge",
    123815,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": "U.S",
 "pct": 33,
 "same_agency": false,
 "score": 7,
 "t": "National Wildlife Refuge",
 "verdict": "unsure"
}
```

## US-4057 Elbow Slough Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Elbow Slough Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 162,
  "dissolved": {
   "after": 333,
   "before": 673,
   "copies": 2,
   "families": {
    "padus": 173,
    "sglab": 160
   },
   "family_fold": 160,
   "family_used": "padus",
   "key_union": 162,
   "parts": 0,
   "records": 4,
   "summed": 173,
   "tracts": 2
  },
  "family_fold": "layers {'padus': 173, 'sglab': 160}: one land in 2 layers, the padus copy used (160 ac of copies not added)",
  "manager": "",
  "note": "4 joined records = 2 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 673 -> 333 acres",
  "pieces": [
   [
    203039,
    "Elbow Slough Wildlife Management Area",
    173,
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
 "t": "Wildlife Management Area",
 "verdict": "no size on page"
}
```

## US-0307 D'Arbonne National Wildlife Refuge
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "D'Arbonne National Wildlife Refuge",
 "official": null,
 "ours": {
  "acres": 17639,
  "dissolved": {
   "after": 17639,
   "before": 52917,
   "copies": 2,
   "parts": 0,
   "records": 3,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 52917 -> 17639 acres",
  "pieces": [
   [
    3761,
    "D 'Arbonne National Wildlife Refuge",
    17639,
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
 "verdict": "no size on page"
}
```

## US-0306 Catahoula National Wildlife Refuge
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Catahoula National Wildlife Refuge",
 "official": null,
 "ours": {
  "acres": 62844,
  "dissolved": {
   "after": 63051,
   "before": 88289,
   "copies": 1,
   "families": {
    "fsod": 37813,
    "padus": 25238
   },
   "family_fold": 25238,
   "family_used": "fsod",
   "key_union": 62844,
   "parts": 0,
   "records": 3,
   "summed": 37813,
   "tracts": 2
  },
  "family_fold": "layers {'fsod': 37813, 'padus': 25238}: one land in 2 layers, the fsod copy used (25,238 ac of copies not added)",
  "manager": "",
  "note": "3 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 88289 -> 63051 acres",
  "pieces": [
   [
    "fsod89",
    "Catahoula National Wildlife Refuge",
    37813,
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
 "verdict": "no size on page"
}
```

## US-4081 Sandy Hollow Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Sandy Hollow Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 4706,
  "dissolved": {
   "after": 12797,
   "before": 17452,
   "copies": 1,
   "families": {
    "padus": 3809,
    "sglaa": 4282,
    "sglac": 4706
   },
   "family_fold": 8091,
   "family_used": "sglac",
   "parts": 0,
   "records": 4,
   "tracts": 3
  },
  "family_fold": "layers {'sglac': 4706, 'sglaa': 4282, 'padus': 3809}: one land in 3 layers, the sglac copy used (8,091 ac of copies not added)",
  "manager": "",
  "note": "4 joined records = 3 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 17452 -> 12797 acres",
  "pieces": [
   [
    "sglac42",
    "Sandy Hollow WMA",
    4706,
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

## US-4066 Loggy Bayou Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Loggy Bayou Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 6579,
  "dissolved": {
   "after": 12923,
   "before": 25970,
   "copies": 2,
   "families": {
    "padus": 6579,
    "sglac": 6344
   },
   "family_fold": 6344,
   "family_used": "padus",
   "parts": 0,
   "records": 4,
   "tracts": 2
  },
  "family_fold": "layers {'padus': 6579, 'sglac': 6344}: one land in 2 layers, the padus copy used (6,344 ac of copies not added)",
  "manager": "",
  "note": "4 joined records = 2 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 25970 -> 12923 acres",
  "pieces": [
   [
    203048,
    "Loggy Bayou Wildlife Management Area",
    6579,
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

## US-10455 Rosedown Plantation State Historic Site
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Rosedown Plantation State Historic Site",
 "official": null,
 "ours": {
  "acres": 311,
  "manager": "",
  "pieces": [
   [
    202972,
    "Rosedown Plantation",
    311,
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
 "t": "State Historic Site",
 "verdict": "no size on page"
}
```

## US-0300 Big Branch Marsh National Wildlife Refuge
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Big Branch Marsh National Wildlife Refuge",
 "official": {
  "acres": 18000.0,
  "as": "18,000 acres",
  "clean": false,
  "line": "e is a natural treasure on the northshore of Lake Pontchartrain north of New Orleans, LA. The refuge has over 18,000 acres of freshwater and brackish marsh, bald cypress-tupelo forest, bayous, hardwood forest hammocks, and pine sava",
  "read": "2026-11-22",
  "sent": "The refuge has over 18,000 acres of freshwater and brackish marsh, bald cypress-tupelo forest, bayous, hardwood forest hammocks, and pine savannah.",
  "url": "https://www.fws.gov/refuge/big-branch-marsh",
  "why": "total-looking"
 },
 "ours": {
  "acres": 18319,
  "dissolved": {
   "after": 18319,
   "before": 36635,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 36635 -> 18319 acres",
  "pieces": [
   [
    4561,
    "Big Branch Marsh National Wildlife Refuge",
    18319,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 2,
 "same_agency": false,
 "score": 8,
 "t": "National Wildlife Refuge",
 "verdict": "agree"
}
```

## US-0729 Cane River Creole National Historical Park
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Cane River Creole National Historical Park",
 "official": null,
 "ours": {
  "acres": 63,
  "manager": "",
  "pieces": [
   [
    3189,
    "Cane River Creole National Historical Park",
    63,
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
 "t": "National Historical Park",
 "verdict": "no size on page"
}
```
