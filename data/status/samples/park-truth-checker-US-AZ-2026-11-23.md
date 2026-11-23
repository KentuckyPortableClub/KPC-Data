# park truth checker: US-AZ random sample of 12 (2026-11-23; seed = date + area, same rows for everyone)

Source file: `data/truth/US-AZ.json`

## US-0815 Fort Bowie National Historic Site
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Fort Bowie National Historic Site",
 "official": null,
 "ours": {
  "acres": 997,
  "manager": "",
  "pieces": [
   [
    3125,
    "Fort Bowie National Historic Site",
    997,
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

## US-7383 Tonto State Fish Hatchery
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Tonto State Fish Hatchery",
 "official": null,
 "ours": {
  "acres": 0,
  "manager": "",
  "pieces": [],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": null,
 "score": 5,
 "t": "State Fish Hatchery",
 "verdict": "ours unknown"
}
```

## US-13332 Sunflower Flat State Wildlife Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Sunflower Flat State Wildlife Area",
 "official": null,
 "ours": {
  "acres": 159,
  "manager": "",
  "pieces": [
   [
    167497,
    "Sunflower Flat Wildlife Area",
    159,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "State Wildlife Area",
 "verdict": "no size on page"
}
```

## US-0057 Petrified Forest National Park
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Petrified Forest National Park",
 "official": null,
 "ours": {
  "acres": 148237,
  "manager": "",
  "pieces": [
   [
    3468,
    "Petrified Forest National Park",
    148237,
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
 "t": "National Park",
 "verdict": "no size on page"
}
```

## US-0676 Lake Mead National Recreation Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Lake Mead National Recreation Area",
 "note": "whole park compared (POTA lists it in 2 states: {'US-NV': 581651, 'US-AZ': 710205})",
 "official": {
  "acres": 1500000.0,
  "as": "1.5 million acres",
  "clean": false,
  "line": "tdoor thrills, striking landscapes, and brilliant blue waters. This year-round recreation area spreads across 1.5 million acres of mountains, canyons, valleys and two vast reservoirs. Visitors come here for scenic drives, biking, hiking,",
  "read": "2026-11-22",
  "sent": "This year-round recreation area spreads across 1.5 million acres of mountains, canyons, valleys and two vast reservoirs.",
  "url": "https://www.nps.gov/lake/index.htm",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 1291856,
  "acres_by_state": {
   "US-AZ": 710205,
   "US-NV": 581651
  },
  "manager": "",
  "pieces": [
   [
    3507,
    "Lake Mead National Recreation Area",
    710205,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "states": [
   "US-NV",
   "US-AZ"
  ],
  "unknown_pieces": 0,
  "whole_park": true
 },
 "owner_now": null,
 "pct": 14,
 "same_agency": false,
 "score": 7,
 "t": "National Recreation Area",
 "verdict": "agree"
}
```

## US-11046 Eagletail Mountains Wilderness Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Eagletail Mountains Wilderness Area",
 "official": {
  "acres": 97880.0,
  "as": "97,880 acre",
  "clean": false,
  "line": "uTube Facebook Instagram Flickr LinkedIn Eagletail Mountains Wilderness | Arizona View Map In Full Screen The 97,880-acre Eagletail Mountains Wilderness in Arizona is managed by the Bureau of Land Management. Known for its striking",
  "read": "2026-11-22",
  "sent": "The 97,880-acre Eagletail Mountains Wilderness in Arizona is managed by the Bureau of Land Management.",
  "url": "https://www.blm.gov/visit/eagletail-mountains-wilderness",
  "why": "total-looking"
 },
 "ours": {
  "acres": 0,
  "manager": "",
  "pieces": [],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": null,
 "same_agency": false,
 "score": 6,
 "t": "Wilderness Area",
 "verdict": "ours unknown"
}
```

## US-0178 Leslie Canyon National Wildlife Refuge
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Leslie Canyon National Wildlife Refuge",
 "official": {
  "acres": 2765.0,
  "as": "2,765 acre",
  "clean": false,
  "line": "while doing something personally satisfying. Learn How To Get Involved Services Special Use Permits About The 2,765-acre Leslie Canyon National Wildlife Refuge was established in 1988 to conserve fish and wildlife species that are",
  "read": "2026-11-22",
  "sent": "The 2,765-acre Leslie Canyon National Wildlife Refuge was established in 1988 to conserve fish and wildlife species that are listed as threatened or endangered.",
  "url": "https://www.fws.gov/refuge/leslie-canyon",
  "why": "history"
 },
 "ours": {
  "acres": 2775,
  "dissolved": {
   "after": 2775,
   "before": 5550,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 5550 -> 2775 acres",
  "pieces": [
   [
    4040,
    "Leslie Canyon National Wildlife Refuge",
    2775,
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
 "t": "National Wildlife Refuge",
 "verdict": "agree"
}
```

## US-1065 Picacho Peak State Park
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Picacho Peak State Park",
 "official": null,
 "ours": {
  "acres": 3724,
  "dissolved": {
   "after": 7185,
   "before": 10905,
   "copies": 1,
   "families": {
    "padus": 3461,
    "sgaze": 3724
   },
   "family_fold": 3461,
   "family_used": "sgaze",
   "parts": 0,
   "records": 3,
   "tracts": 2
  },
  "family_fold": "layers {'sgaze': 3724, 'padus': 3461}: one land in 2 layers, the sgaze copy used (3,461 ac of copies not added)",
  "manager": "",
  "note": "3 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 10905 -> 7185 acres",
  "pieces": [
   [
    "sgaze15",
    "Picacho Peak State Park",
    3724,
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

## US-11986 Wenima State Wildlife Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Wenima State Wildlife Area",
 "official": null,
 "ours": {
  "acres": 353,
  "manager": "",
  "pieces": [
   [
    167490,
    "Wenima Wildlife Area",
    353,
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
 "t": "State Wildlife Area",
 "verdict": "no size on page"
}
```

## US-4432 Tonto National Forest
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-11-09",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Tonto National Forest",
 "official": null,
 "ours": {
  "acres": 2866817,
  "manager": "",
  "pieces": [
   [
    2756,
    "Tonto National Forest",
    2866817,
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

## US-11981 Arivaca Lake State Wildlife Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Arivaca Lake State Wildlife Area",
 "official": null,
 "ours": {
  "acres": 208,
  "manager": "",
  "pieces": [
   [
    167506,
    "Arivaca Land and Lake",
    208,
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
 "t": "State Wildlife Area",
 "verdict": "no size on page"
}
```

## US-11984 Quigley-Achee State Wildlife Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Quigley-Achee State Wildlife Area",
 "official": null,
 "ours": {
  "acres": 610,
  "manager": "",
  "pieces": [
   [
    167486,
    "Quigley Wildlife Area",
    610,
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
 "t": "State Wildlife Area",
 "verdict": "no size on page"
}
```
