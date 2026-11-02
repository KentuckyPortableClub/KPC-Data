# park truth checker: US-IA random sample of 12 (2026-11-01; seed = date + area, same rows for everyone)

Source file: `data/truth/US-IA.json`

## US-9354 Fox Hills Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Fox Hills Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 1452,
  "dissolved": {
   "after": 2805,
   "before": 4257,
   "copies": 0,
   "families": {
    "padus": 1344,
    "sgiaa": 1452,
    "sgiac": 9
   },
   "family_fold": 1353,
   "family_used": "sgiaa",
   "parts": 2,
   "records": 5,
   "tracts": 3
  },
  "family_fold": "layers {'sgiaa': 1452, 'padus': 1344, 'sgiac': 9}: one land in 3 layers, the sgiaa copy used (1,353 ac of copies not added)",
  "manager": "",
  "note": "5 joined records = 3 tracts: 0 copies of a tract (same acres, another layer) and 2 fee tracts under a designation record folded; summed 4257 -> 2805 acres",
  "pieces": [
   [
    "sgiaa58928",
    "FOX HILLS WILDLIFE AREA",
    1452,
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

## US-0269 Driftless Area National Wildlife Refuge
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Driftless Area National Wildlife Refuge",
 "official": {
  "acres": 1238.0,
  "as": "1,238 acres",
  "clean": true,
  "line": "egulations available. Visit our rules and policies page for maps and unit regulations. The refuge encompasses 1,238 acres of the Driftless Area in Iowa - a small portion of the entire Driftless Area. This area is also known as the",
  "read": "2026-11-01",
  "sent": "The refuge encompasses 1,238 acres of the Driftless Area in Iowa - a small portion of the entire Driftless Area.",
  "url": "https://www.fws.gov/refuge/driftless-area",
  "why": "clean total"
 },
 "ours": {
  "acres": 1220,
  "dissolved": {
   "after": 1818,
   "before": 3598,
   "copies": 4,
   "families": {
    "padus": 1220,
    "sgiaa": 560,
    "sgiac": 38
   },
   "family_fold": 598,
   "family_used": "padus",
   "parts": 0,
   "records": 9,
   "tracts": 5
  },
  "family_fold": "layers {'padus': 1220, 'sgiaa': 560, 'sgiac': 38}: one land in 3 layers, the padus copy used (598 ac of copies not added)",
  "manager": "",
  "note": "9 joined records = 5 tracts: 4 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 3598 -> 1818 acres",
  "pieces": [
   [
    3793,
    "Driftless Area National Wildlife Refuge",
    1220,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 1,
 "same_agency": false,
 "score": 7,
 "t": "National Wildlife Refuge",
 "verdict": "agree"
}
```

## US-2308 Nine Eagles State Park
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Nine Eagles State Park",
 "official": {
  "acres": 1100.0,
  "as": "1,100 acre",
  "clean": false,
  "line": "s and nine miles of hiking trails. Shaded picnic spots with tables and fireplaces can be found throughout the 1,100-acre park. Plan Your Visit Hike or bike the three-mile trail that winds around the lake and connects to the campgr",
  "read": "2026-11-01",
  "sent": "Shaded picnic spots with tables and fireplaces can be found throughout the 1,100-acre park.",
  "url": "https://www.iowadnr.gov/Places-to-Go/State-Parks/Iowa-State-Parks/Nine-Eagles-State-Park",
  "why": "part (a lake, a purchase, a campground…)"
 },
 "ours": {
  "acres": 1166,
  "dissolved": {
   "after": 2262,
   "before": 3358,
   "copies": 1,
   "families": {
    "padus": 1166,
    "sgiab": 1096
   },
   "family_fold": 1096,
   "family_used": "padus",
   "parts": 0,
   "records": 3,
   "tracts": 2
  },
  "family_fold": "layers {'padus': 1166, 'sgiab': 1096}: one land in 2 layers, the padus copy used (1,096 ac of copies not added)",
  "manager": "",
  "note": "3 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 3358 -> 2262 acres",
  "pieces": [
   [
    198558,
    "Nine Eagles State Park",
    1166,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
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

## US-2309 Okamanpedan (Tuttle) State Park
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Okamanpedan (Tuttle) State Park",
 "official": null,
 "ours": {
  "acres": 28,
  "dissolved": {
   "after": 55,
   "before": 83,
   "copies": 1,
   "families": {
    "padus": 27,
    "sgiab": 28
   },
   "family_fold": 27,
   "family_used": "sgiab",
   "parts": 0,
   "records": 3,
   "tracts": 2
  },
  "family_fold": "layers {'sgiab': 28, 'padus': 27}: one land in 2 layers, the sgiab copy used (27 ac of copies not added)",
  "manager": "",
  "note": "3 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 83 -> 55 acres",
  "pieces": [
   [
    "sgiab97112",
    "Okamanpedan State Park",
    28,
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
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-9339 Cardinal Marsh Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Cardinal Marsh Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 1173,
  "dissolved": {
   "after": 1173,
   "before": 3519,
   "copies": 2,
   "parts": 0,
   "records": 3,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 3519 -> 1173 acres",
  "pieces": [
   [
    198696,
    "Cardinal Marsh Wildlife Management Area",
    1173,
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

## US-2278 Banner Lakes at Summerset State Park
```json
{
 "checked": "2026-11-01",
 "handover": [
  {
   "date_hint": null,
   "kind": "managed by",
   "line": "or any size motor at “no wake” speed. Practice shooting skills at the nearby Banner Shooting Range, managed by the DNR. The range is adjacent to the park and a popular destination for gun and archery shooting. The renovated range has sheltered shooting",
   "owner_now": "DNR",
   "src": "https://www.iowadnr.gov/Places-to-Go/State-Parks/Iowa-State-Parks/Banner-Lakes-at-Summerset-State-Park",
   "why": "the park's page (data/parkinfo)"
  }
 ],
 "n": "Banner Lakes at Summerset State Park",
 "official": null,
 "ours": {
  "acres": 224,
  "dissolved": {
   "after": 442,
   "before": 666,
   "copies": 2,
   "families": {
    "padus": 218,
    "sgiab": 224
   },
   "family_fold": 218,
   "family_used": "sgiab",
   "parts": 0,
   "records": 5,
   "tracts": 3
  },
  "family_fold": "layers {'padus': 218, 'sgiab': 224}: one land in 2 layers, the sgiab copy used (218 ac of copies not added)",
  "manager": "",
  "note": "5 joined records = 3 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 666 -> 442 acres",
  "pieces": [
   [
    "sgiab93061",
    "Banner Lakes At Summerset State Park",
    207,
    "name"
   ],
   [
    "sgiab93060",
    "Banner Lakes At Summerset State Park",
    17,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 2
 },
 "owner_now": "DNR",
 "pct": null,
 "score": 7,
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-9353 Cone Marsh Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Cone Marsh Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 728,
  "dissolved": {
   "after": 728,
   "before": 2184,
   "copies": 2,
   "parts": 0,
   "records": 3,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 2184 -> 728 acres",
  "pieces": [
   [
    198716,
    "Cone Marsh Wildlife Management Area",
    728,
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

## US-4663 White Pine Hollow State Forest
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "White Pine Hollow State Forest",
 "official": null,
 "ours": {
  "acres": 227,
  "dissolved": {
   "after": 227,
   "before": 305,
   "copies": 2,
   "parts": 0,
   "records": 4,
   "tracts": 2
  },
  "manager": "",
  "note": "4 joined records = 2 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 305 -> 227 acres",
  "pieces": [
   [
    199166,
    "White Pine Hollow State Forest",
    188,
    "name"
   ],
   [
    198493,
    "White Pine Hollow State Forest",
    39,
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
 "t": "State Forest",
 "verdict": "no size on page"
}
```

## US-11378 Rock Creek Island State Preserve
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Rock Creek Island State Preserve",
 "official": null,
 "ours": {
  "acres": 31,
  "dissolved": {
   "after": 31,
   "before": 93,
   "copies": 2,
   "parts": 0,
   "records": 3,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 93 -> 31 acres",
  "pieces": [
   [
    198641,
    "Rock Creek Island State Preserve",
    31,
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
 "t": "State Preserve",
 "verdict": "no size on page"
}
```

## US-7564 Riverton Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Riverton Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 4071,
  "dissolved": {
   "after": 8060,
   "before": 12131,
   "copies": 1,
   "families": {
    "padus": 3989,
    "sgiaa": 4071
   },
   "family_fold": 3989,
   "family_used": "sgiaa",
   "parts": 0,
   "records": 3,
   "tracts": 2
  },
  "family_fold": "layers {'sgiaa': 4071, 'padus': 3989}: one land in 2 layers, the sgiaa copy used (3,989 ac of copies not added)",
  "manager": "",
  "note": "3 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 12131 -> 8060 acres",
  "pieces": [
   [
    "sgiaa101900",
    "RIVERTON WILDLIFE AREA",
    4071,
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

## US-0271 Neal Smith National Wildlife Refuge
```json
{
 "cause": "our union: one of our pieces alone matches the agency (double count?)",
 "checked": "2026-11-01",
 "handover": [
  {
   "date_hint": null,
   "kind": "managed by",
   "line": "ational wildlife refuge A national wildlife refuge is typically a contiguous area of land and water managed by the U.S. Fish and Wildlife Service for the conservation and, where appropriate, restoration of fish, wildlife and plant resources and their habitats for th",
   "owner_now": "U.S",
   "src": "https://www.fws.gov/refuge/neal-smith/about-us",
   "why": "FWS refuge about page"
  }
 ],
 "n": "Neal Smith National Wildlife Refuge",
 "official": {
  "acres": 6000.0,
  "as": "6,000 acres",
  "clean": false,
  "line": "d used local seed sources to plant approximately 4,000 acres of tallgrass prairie. Today, the refuge protects 6,000 acres providing food, cover and breeding habitat for resident and migratory wildlife. The refuge also serves as a m",
  "read": "2026-11-01",
  "sent": "Today, the refuge protects 6,000 acres providing food, cover and breeding habitat for resident and migratory wildlife.",
  "url": "https://www.fws.gov/refuge/neal-smith/about-us",
  "why": "total-looking"
 },
 "ours": {
  "acres": 11917,
  "dissolved": {
   "after": 16386,
   "before": 22075,
   "copies": 0,
   "families": {
    "padus": 11917,
    "sgiac": 4469
   },
   "family_fold": 4469,
   "family_used": "padus",
   "parts": 3,
   "records": 12,
   "tracts": 9
  },
  "family_fold": "layers {'padus': 11917, 'sgiac': 4469}: one land in 2 layers, the padus copy used (4,469 ac of copies not added)",
  "manager": "",
  "note": "12 joined records = 9 tracts: 0 copies of a tract (same acres, another layer) and 3 fee tracts under a designation record folded; summed 22075 -> 16386 acres",
  "pieces": [
   [
    5112,
    "Neal Smith National Wildlife Refuge",
    6177,
    "name"
   ],
   [
    4155,
    "Neal Smith National Wildlife Refuge",
    5692,
    "name"
   ],
   [
    4156,
    "Neal Smith National Wildlife Refuge",
    48,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": "U.S",
 "pct": 99,
 "same_agency": false,
 "score": 6,
 "t": "National Wildlife Refuge",
 "verdict": "off"
}
```

## US-4664 Yellow River State Forest
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Yellow River State Forest",
 "official": null,
 "ours": {
  "acres": 6778,
  "dissolved": {
   "after": 8762,
   "before": 35255,
   "copies": 29,
   "families": {
    "padus": 6778,
    "sgiaa": 1790,
    "sgiab": 194
   },
   "family_fold": 1984,
   "family_used": "padus",
   "parts": 15,
   "records": 51,
   "tracts": 7
  },
  "family_fold": "layers {'padus': 6778, 'sgiaa': 1790, 'sgiab': 194}: one land in 3 layers, the padus copy used (1,984 ac of copies not added)",
  "manager": "",
  "note": "51 joined records = 7 tracts: 29 copies of a tract (same acres, another layer) and 15 fee tracts under a designation record folded; summed 35255 -> 8762 acres",
  "pieces": [
   [
    198496,
    "Yellow River State Forest",
    5805,
    "name"
   ],
   [
    198497,
    "Yellow River State Forest",
    777,
    "name"
   ],
   [
    198495,
    "Yellow River State Forest",
    196,
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
 "t": "State Forest",
 "verdict": "no size on page"
}
```
