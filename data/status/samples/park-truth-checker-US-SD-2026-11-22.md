# park truth checker: US-SD random sample of 12 (2026-11-22; seed = date + area, same rows for everyone)

Source file: `data/truth/US-SD.json`

## US-10324 Whetstone Bay State Recreation Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Whetstone Bay State Recreation Area",
 "official": null,
 "ours": {
  "acres": 93,
  "manager": "",
  "pieces": [
   [
    255378,
    "Whetstone Bay Recreation Area",
    79,
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
 "t": "State Recreation Area",
 "verdict": "no size on page"
}
```

## US-5645 Spirit Mound Historic Prairie State Park
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Spirit Mound Historic Prairie State Park",
 "official": null,
 "ours": {
  "acres": 318,
  "manager": "",
  "pieces": [
   [
    255363,
    "Spirit Mound",
    318,
    "words"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-8177 Mina Lake State Recreation Area
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 38 acres, no total words near it)",
 "checked": "2026-11-22",
 "handover": [],
 "n": "Mina Lake State Recreation Area",
 "official": {
  "acres": 38.0,
  "as": "38 acres",
  "clean": false,
  "line": "s may be closed. Please contact the park directly for current status. Vault toilets usually remain open. Park Size: 38 campsites, 1 camping cabin and 1 modern cabin Directions: 12 miles west of Aberdeen off US Hwy 12 Nearest Town",
  "read": "2026-11-22",
  "sent": "Park Size: 38 campsites, 1 camping cabin and 1 modern cabin",
  "url": "https://gfp.sd.gov/parks/detail/mina-lake-recreation-area/",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 376,
  "manager": "",
  "pieces": [
   [
    254917,
    "Mina",
    72,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 2
 },
 "owner_now": null,
 "pct": 889,
 "same_agency": false,
 "score": 7,
 "t": "State Recreation Area",
 "verdict": "unsure"
}
```

## US-8175 Little Moreau State Recreation Area
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 5 acres, no total words near it)",
 "checked": "2026-11-22",
 "handover": [],
 "n": "Little Moreau State Recreation Area",
 "official": {
  "acres": 5.0,
  "as": "5 acres",
  "clean": false,
  "line": "1 and April 30, please contact the park directly for current status. Vault toilets usually remain open. Park Size: 5 campsites available on a first-come, first-served basis Directions: 6 miles south of Timber Lake off SD Hwy 20",
  "read": "2026-11-22",
  "sent": "Park Size: 5 campsites available on a first-come, first-served basis",
  "url": "https://gfp.sd.gov/parks/detail/little-moreau-recreation-area/",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 2973,
  "manager": "",
  "pieces": [
   [
    254892,
    "Little Moreau",
    2820,
    "name"
   ],
   [
    255325,
    "Little Moreau",
    153,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 2
 },
 "owner_now": null,
 "pct": 59360,
 "same_agency": false,
 "score": 7,
 "t": "State Recreation Area",
 "verdict": "unsure"
}
```

## US-0525 Huron Wetland Management District
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-11-22",
 "handover": [],
 "n": "Huron Wetland Management District",
 "official": null,
 "ours": {
  "acres": 12611,
  "dissolved": {
   "after": 12611,
   "before": 16257,
   "copies": 7,
   "parts": 4,
   "records": 59,
   "tracts": 48
  },
  "manager": "",
  "note": "59 joined records = 48 tracts: 7 copies of a tract (same acres, another layer) and 4 fee tracts under a designation record folded; summed 16257 -> 12611 acres",
  "pieces": [
   [
    "fws2330",
    "Harter WPA, Hyde County Waterfowl Production Area",
    1417,
    "reviewed: the district = FWS fee (owned) tracts only, easeme"
   ],
   [
    "fws2329",
    "Cowan WPA, Hyde County Waterfowl Production Area",
    967,
    "reviewed: the district = FWS fee (owned) tracts only, easeme"
   ],
   [
    "fws2295",
    "Mills WPA, Buffalo County Waterfowl Production Area",
    919,
    "reviewed: the district = FWS fee (owned) tracts only, easeme"
   ],
   [
    "fws2268",
    "Bauer WPA, Beadle County Waterfowl Production Area",
    795,
    "reviewed: the district = FWS fee (owned) tracts only, easeme"
   ],
   [
    "fws2289",
    "Weaver WPA, Beadle County Waterfowl Production Area",
    646,
    "reviewed: the district = FWS fee (owned) tracts only, easeme"
   ],
   [
    "fws2317",
    "Spring Lake WPA, Hand County Waterfowl Production Area",
    620,
    "reviewed: the district = FWS fee (owned) tracts only, easeme"
   ],
   [
    "fws2276",
    "LeClaire WPA, Beadle County Waterfowl Production Area",
    522,
    "reviewed: the district = FWS fee (owned) tracts only, easeme"
   ],
   [
    "fws2307",
    "Campbell WPA, Hand County Waterfowl Production Area",
    481,
    "reviewed: the district = FWS fee (owned) tracts only, easeme"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 3,
 "t": "Wetland Management District",
 "verdict": "unsure"
}
```

## US-0850 Minuteman Missile National Historic Site
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Minuteman Missile National Historic Site",
 "official": null,
 "ours": {
  "acres": 39,
  "manager": "",
  "pieces": [
   [
    3159,
    "Minuteman Missile National Historic Site",
    39,
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

## US-7488 Fort Pierre National Grassland
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Fort Pierre National Grassland",
 "official": null,
 "ours": {
  "acres": 115811,
  "manager": "",
  "pieces": [
   [
    2724,
    "Fort Pierre National Grassland",
    115811,
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
 "t": "National Grassland",
 "verdict": "no size on page"
}
```

## US-8169 Lake Hiddenwood State Recreation Area
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 13 acres, no total words near it)",
 "checked": "2026-11-22",
 "handover": [],
 "n": "Lake Hiddenwood State Recreation Area",
 "official": {
  "acres": 13.0,
  "as": "13 acres",
  "clean": false,
  "line": "s may be closed. Please contact the park directly for current status. Vault toilets usually remain open. Park Size: 13 campsites Directions: 5 miles Northeast of Selby off Hwy 12/83 Nearest Town: Selby Show More Make Reservations",
  "read": "2026-11-22",
  "sent": "Park Size: 13 campsites",
  "url": "https://gfp.sd.gov/parks/detail/lake-hiddenwood-recreation-area/",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 331,
  "manager": "",
  "pieces": [
   [
    255315,
    "Lake Hiddenwood",
    331,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 2
 },
 "owner_now": null,
 "pct": 2446,
 "same_agency": false,
 "score": 7,
 "t": "State Recreation Area",
 "verdict": "unsure"
}
```

## US-8194 Snake Creek State Recreation Area
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 2 acres, a tiny number without size wording)",
 "checked": "2026-11-22",
 "handover": [],
 "n": "Snake Creek State Recreation Area",
 "official": {
  "acres": 2.0,
  "as": "2 acres",
  "clean": false,
  "line": "s may be closed. Please contact the park directly for current status. Vault toilets usually remain open. Park Size: 2 campgrounds with 115 campsites and 10 camping cabins Directions: 14 miles west of Platte off SD Hwy 44 Nearest",
  "read": "2026-11-22",
  "sent": "Park Size: 2 campgrounds with 115 campsites and 10 camping cabins",
  "url": "https://gfp.sd.gov/parks/detail/snake-creek-recreation-area/",
  "why": "a tiny number without size wording"
 },
 "ours": {
  "acres": 705,
  "manager": "",
  "pieces": [
   [
    255359,
    "Snake Creek State Recreation Area",
    705,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 2
 },
 "owner_now": null,
 "pct": 35150,
 "same_agency": false,
 "score": 7,
 "t": "State Recreation Area",
 "verdict": "unsure"
}
```

## US-8181 Okobojo Point State Recreation Area
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 18 acres, no total words near it)",
 "checked": "2026-11-22",
 "handover": [],
 "n": "Okobojo Point State Recreation Area",
 "official": {
  "acres": 18.0,
  "as": "18 acres",
  "clean": false,
  "line": "s may be closed. Please contact the park directly for current status. Vault toilets usually remain open. Park Size: 18 campsites, first-come, first-served basis. Directions: 17 miles northwest of Pierre off SD 1804 Nearest Town:",
  "read": "2026-11-22",
  "sent": "Park Size: 18 campsites, first-come, first-served basis.",
  "url": "https://gfp.sd.gov/parks/detail/okobojo-point-recreation-area/",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 124,
  "manager": "",
  "pieces": [
   [
    255338,
    "Okobojo Point Recreation Area",
    135,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 2
 },
 "owner_now": null,
 "pct": 589,
 "same_agency": false,
 "score": 7,
 "t": "State Recreation Area",
 "verdict": "unsure"
}
```

## US-8163 Farm Island State Recreation Area
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 2 acres, a tiny number without size wording)",
 "checked": "2026-11-22",
 "handover": [],
 "n": "Farm Island State Recreation Area",
 "official": {
  "acres": 2.0,
  "as": "2 acres",
  "clean": false,
  "line": "s may be closed. Please contact the park directly for current status. Vault toilets usually remain open. Park Size: 2 campground with 90 campsites and 4 camping cabins Directions: 4 miles east of Pierre off SD Highway 34 Nearest",
  "read": "2026-11-22",
  "sent": "Park Size: 2 campground with 90 campsites and 4 camping cabins",
  "url": "https://gfp.sd.gov/parks/detail/farm-island-recreation-area/",
  "why": "a tiny number without size wording"
 },
 "ours": {
  "acres": 1289,
  "manager": "",
  "pieces": [
   [
    255297,
    "Farm Island",
    1154,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 2
 },
 "owner_now": null,
 "pct": 64350,
 "same_agency": false,
 "score": 7,
 "t": "State Recreation Area",
 "verdict": "unsure"
}
```

## US-8187 Randall Creek State Recreation Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Randall Creek State Recreation Area",
 "official": null,
 "ours": {
  "acres": 168,
  "manager": "",
  "pieces": [
   [
    255346,
    "Randall Creek Recreation Area",
    182,
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
 "t": "State Recreation Area",
 "verdict": "no size on page"
}
```
