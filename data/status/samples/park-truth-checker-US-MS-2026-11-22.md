# park truth checker: US-MS random sample of 12 (2026-11-22; seed = date + area, same rows for everyone)

Source file: `data/truth/US-MS.json`

## US-7085 John W. Starr Wildlife Management Area
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "John W. Starr Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 8268,
  "manager": "",
  "pieces": [
   [
    211196,
    "John W. Starr Wma",
    8268,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 5,
 "t": "Wildlife Management Area",
 "verdict": "no size on page"
}
```

## US-7083 Mahannah Wildlife Management Area
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Mahannah Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 12913,
  "manager": "",
  "pieces": [
   [
    211180,
    "Mahannah Wma",
    11396,
    "name"
   ],
   [
    211174,
    "Mahannah Wildlife Management Area",
    1517,
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

## US-2547 Natchez State Park
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Natchez State Park",
 "official": null,
 "ours": {
  "acres": 3650,
  "dissolved": {
   "after": 3428,
   "before": 10249,
   "copies": 2,
   "key_union": 3650,
   "parts": 0,
   "records": 3,
   "summed": 3428,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 10249 -> 3428 acres",
  "pieces": [
   [
    211162,
    "Natchez State Park",
    3428,
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
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-0747 Natchez National Historical Park
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Natchez National Historical Park",
 "official": null,
 "ours": {
  "acres": 98,
  "manager": "",
  "pieces": [
   [
    3228,
    "Natchez National Historical Park",
    98,
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
 "t": "National Historical Park",
 "verdict": "no size on page"
}
```

## US-2534 Florewood State Park
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Florewood State Park",
 "official": null,
 "ours": {
  "acres": 109,
  "family_fold": "layers {'padus': 99, 'mszp': 103}: one land in 2 layers, the mszp copy used (99 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "mszp6",
    "FLOREWOOD",
    75,
    "name"
   ],
   [
    "mszp5",
    "FLOREWOOD",
    28,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 4,
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-4495 Delta National Forest
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-11-15",
 "handover": [],
 "n": "Delta National Forest",
 "official": null,
 "ours": {
  "acres": 61472,
  "manager": "",
  "pieces": [
   [
    2965,
    "Delta National Forest",
    61472,
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
 "t": "National Forest",
 "verdict": "unsure"
}
```

## US-0395 Yazoo National Wildlife Refuge
```json
{
 "checked": "2026-11-15",
 "handover": [],
 "n": "Yazoo National Wildlife Refuge",
 "official": {
  "acres": 12941.0,
  "as": "12,941 acres",
  "clean": false,
  "line": "introduced in 1970. In 1992, the Service purchased the 470-acre Cox property bringing total refuge acreage to 12,941 acres. Other Facilities in this Complex Yazoo National Wildlife Refuge is one of nine refuges that make up the Theo",
  "read": "2026-11-15",
  "sent": "In 1992, the Service purchased the 470-acre Cox property bringing total refuge acreage to 12,941 acres.",
  "url": "https://www.fws.gov/refuge/yazoo/about-us",
  "why": "part (a lake, a purchase, a campground…)"
 },
 "ours": {
  "acres": 13043,
  "dissolved": {
   "after": 13043,
   "before": 26086,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 26086 -> 13043 acres",
  "pieces": [
   [
    4492,
    "Yazoo National Wildlife Refuge",
    13043,
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
 "t": "National Wildlife Refuge",
 "verdict": "agree"
}
```

## US-2548 Paul B. Johnson State Park
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Paul B. Johnson State Park",
 "official": null,
 "ours": {
  "acres": 511,
  "manager": "",
  "pieces": [
   [
    211163,
    "Paul B. Johnson State Park",
    511,
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
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-2546 Leroy Percy State Park
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Leroy Percy State Park",
 "official": null,
 "ours": {
  "acres": 85,
  "manager": "",
  "pieces": [
   [
    211161,
    "Leroy Percy State Park",
    85,
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
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-2532 Buccaneer State Park
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Buccaneer State Park",
 "official": null,
 "ours": {
  "acres": 443,
  "manager": "",
  "pieces": [
   [
    211148,
    "Buccaneer State Park",
    443,
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
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-7094 Hell Creek Wildlife Management Area
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Hell Creek Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 2354,
  "manager": "",
  "pieces": [
   [
    211219,
    "Hell Creek Wma",
    2354,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 4,
 "t": "Wildlife Management Area",
 "verdict": "no size on page"
}
```

## US-7076 Sky Lake Wildlife Management Area
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Sky Lake Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 4307,
  "manager": "",
  "pieces": [
   [
    211231,
    "Sky Lake Wma",
    4229,
    "name"
   ],
   [
    211230,
    "Sky Lake",
    78,
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
