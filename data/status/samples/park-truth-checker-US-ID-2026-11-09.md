# park truth checker: US-ID random sample of 12 (2026-11-09; seed = date + area, same rows for everyone)

Source file: `data/truth/US-ID.json`

## US-12233 CJ Strike Reservoir State Fishing Lake
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "CJ Strike Reservoir State Fishing Lake",
 "official": null,
 "ours": {
  "acres": 37560,
  "dissolved": {
   "after": 49859,
   "before": 113333,
   "copies": 2,
   "families": {
    "rst": 31737,
    "sgida": 11363,
    "sgidb": 6759
   },
   "family_fold": 18122,
   "family_used": "rst",
   "key_union": 37560,
   "parts": 0,
   "records": 5,
   "summed": 31737,
   "tracts": 3
  },
  "family_fold": "layers {'rst': 31737, 'sgida': 11363, 'sgidb': 6759}: one land in 3 layers, the rst copy used (18,122 ac of copies not added)",
  "manager": "",
  "note": "5 joined records = 3 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 113333 -> 49859 acres",
  "pieces": [
   [
    "rst13808",
    "C J Strike",
    31737,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "water outline only",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "State Fishing Lake",
 "verdict": "no size on page"
}
```

## US-10343 Hard Trigger HMA BLM Herd Management Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Hard Trigger HMA BLM Herd Management Area",
 "official": null,
 "ours": {
  "acres": 69397,
  "manager": "",
  "pieces": [
   [
    "hma35",
    "Hardtrigger",
    69397,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "BLM Herd Management Area",
 "verdict": "no size on page"
}
```

## US-10429 Middle Fork Clearwater River National Wild and Scenic River
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Middle Fork Clearwater River National Wild and Scenic River",
 "official": null,
 "ours": {
  "acres": 20358,
  "manager": "",
  "pieces": [
   [
    "fwsr214",
    "Middle Fork Clearwater, Idaho National Wild and Scenic River",
    20358,
    "reviewed"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "National Wild & Scenic River",
 "verdict": "no size on page"
}
```

## US-10422 Northwest Passage National Scenic Byway National Parkway
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Northwest Passage National Scenic Byway National Parkway",
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
 "score": 4,
 "t": "National Parkway",
 "verdict": "ours unknown"
}
```

## US-0849 Minidoka National Historic Site
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Minidoka National Historic Site",
 "note": "whole park compared (POTA lists it in 1 states: {'US-ID': 302})",
 "official": null,
 "ours": {
  "acres": 302,
  "acres_by_state": {
   "US-ID": 302
  },
  "manager": "",
  "pieces": [
   [
    3158,
    "Minidoka National Historic Site",
    302,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "states": [
   "US-ID",
   "US-WA"
  ],
  "unknown_pieces": 0,
  "whole_park": true
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "National Historic Site",
 "verdict": "no size on page"
}
```

## US-4584 Ashton-Tetonia Trail State Park
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Ashton-Tetonia Trail State Park",
 "official": {
  "acres": 28.0,
  "as": "28 Acres",
  "clean": false,
  "line": "na Project at Poison Creek on Lake Cascade Mar 15 2024 Idaho Department of Parks and Recreation Purchase Adds 28 Acres to Bear Lake State Park The acquisition will bring 1,200 feet of new shoreline into the popular State Park an",
  "read": "2026-11-09",
  "sent": "Idaho Department of Parks and Recreation Purchase Adds 28 Acres to Bear Lake State Park",
  "url": "https://parksandrecreation.idaho.gov",
  "why": "no total words near it"
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
 "score": 4,
 "t": "State Park",
 "verdict": "ours unknown"
}
```

## US-0054 Nez Perce National Historical Park
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-09",
 "handover": [
  {
   "date_hint": "2021",
   "kind": "renamed",
   "line": "s provide a glimpse into the rich culture and history of the Nez Perce. In 2021 the Nez Perce Tribe renamed a collection of artifacts compiled by Presbyterian missionary Henry Spalding in the 1830s and 40s. This collection, now known as the wetxuuwíitin' collection , is one of the most",
   "owner_now": "Presbyterian",
   "src": "https://www.nps.gov/nepe/learn/historyculture/nez-perce-national-historical-park-virtual-museum.htm",
   "why": "about / history page of the park's site"
  }
 ],
 "n": "Nez Perce National Historical Park",
 "note": "whole park compared (POTA lists it in 2 states: {'US-ID': 1403, 'US-WA': 104})",
 "official": {
  "acres": 4564.9,
  "as": "4564.93 acres",
  "clean": true,
  "line": "erce culture and history. Basic Park Statistics Interior Region(s): Columbia-Pacific Northwest Region 9 Size: 4564.93 acres Staffing: 21 permanent and 1 temporary Annual Visitation: 301,473 Budget: $2,503,000 Economic Benefits to Com",
  "read": "2026-11-09",
  "sent": "Size: 4564.93 acres",
  "url": "https://www.nps.gov/nepe/learn/management/statistics.htm",
  "why": "clean total"
 },
 "ours": {
  "acres": 1507,
  "acres_by_state": {
   "US-ID": 1403,
   "US-WA": 104
  },
  "manager": "",
  "pieces": [
   [
    3230,
    "Nez Perce National Historical Park",
    1403,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "states": [
   "US-ID",
   "US-MT",
   "US-WA",
   "US-OR"
  ],
  "unknown_pieces": 0,
  "whole_park": true
 },
 "owner_now": "Presbyterian",
 "pct": 67,
 "same_agency": false,
 "score": 5,
 "t": "National Historical Park",
 "verdict": "off"
}
```

## US-3424 Ice Age Floods National Geologic Trail
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Ice Age Floods National Geologic Trail",
 "note": "whole park compared (POTA lists it in 0 states: {})",
 "official": {
  "acres": 1920000.0,
  "as": "3,000 square miles",
  "clean": false,
  "line": "st Ice Age, 18,000 to 15,000 years ago, an ice dam in northern Idaho created Glacial Lake Missoula stretching 3,000 square miles around Missoula, Montana. The dam burst and released flood waters across Washington, down the Columbia River",
  "read": "2026-11-09",
  "sent": "At the end of the last Ice Age, 18,000 to 15,000 years ago, an ice dam in northern Idaho created Glacial Lake Missoula stretching 3,000 square miles around Missoula, Montana.",
  "url": "https://www.nps.gov/iafl/index.htm",
  "why": "a statewide / agency-wide total (over a million acres) on a park that is not a big federal unit"
 },
 "ours": {
  "acres": 0,
  "acres_by_state": {},
  "manager": "",
  "pieces": [],
  "pin": "inside",
  "src": "",
  "states": [
   "US-ID",
   "US-MT",
   "US-WA",
   "US-OR"
  ],
  "unknown_pieces": 1,
  "whole_park": true
 },
 "owner_now": null,
 "pct": null,
 "same_agency": false,
 "score": 4,
 "t": "National Geologic Trail",
 "verdict": "ours unknown"
}
```

## US-10005 Steck Park BLM Recreation Management Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Steck Park BLM Recreation Management Area",
 "official": null,
 "ours": {
  "acres": 60,
  "manager": "",
  "pieces": [
   [
    199689,
    "Steck Park Access Site",
    60,
    "name (designation code ignored)"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 5,
 "t": "BLM Recreation Management Area",
 "verdict": "no size on page"
}
```

## US-10346 Saylor Creek HMA BLM Herd Management Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Saylor Creek HMA BLM Herd Management Area",
 "official": null,
 "ours": {
  "acres": 101893,
  "manager": "",
  "pieces": [
   [
    "hma61",
    "Saylor Creek",
    101893,
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
 "t": "BLM Herd Management Area",
 "verdict": "no size on page"
}
```

## US-10441 Springfield State Fish Hatchery
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Springfield State Fish Hatchery",
 "official": null,
 "ours": {
  "acres": 44,
  "manager": "",
  "pieces": [
   [
    199683,
    "Springfield Hatchery & Fishing Access Site",
    73,
    "name"
   ],
   [
    199682,
    "Springfield Hatchery & Fishing Access Site",
    2,
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
 "t": "State Fish Hatchery",
 "verdict": "no size on page"
}
```

## US-11519 Boulder Meadows Reservoir State Fishing Lake
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Boulder Meadows Reservoir State Fishing Lake",
 "official": null,
 "ours": {
  "acres": 31,
  "manager": "",
  "pieces": [
   [
    "sgidb1936384",
    "Boulder Meadows Reservoir",
    31,
    "name · water outline only"
   ]
  ],
  "pin": "inside",
  "src": "water outline only",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "State Fishing Lake",
 "verdict": "no size on page"
}
```
