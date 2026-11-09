# park truth checker: US-AZ random sample of 12 (2026-11-09; seed = date + area, same rows for everyone)

Source file: `data/truth/US-AZ.json`

## US-0966 Tonto National Monument
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Tonto National Monument",
 "official": null,
 "ours": {
  "acres": 1122,
  "manager": "",
  "pieces": [
   [
    3410,
    "Tonto National Monument",
    1122,
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
 "t": "National Monument",
 "verdict": "no size on page"
}
```

## US-1057 Dead Horse Ranch State Park
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Dead Horse Ranch State Park",
 "official": null,
 "ours": {
  "acres": 589,
  "dissolved": {
   "after": 335,
   "before": 1005,
   "copies": 2,
   "key_union": 589,
   "parts": 0,
   "records": 3,
   "summed": 335,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1005 -> 335 acres",
  "pieces": [
   [
    167513,
    "Dead Horse Ranch State Park",
    335,
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

## US-0964 Sunset Crater Volcano National Monument
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Sunset Crater Volcano National Monument",
 "official": null,
 "ours": {
  "acres": 3040,
  "manager": "",
  "pieces": [
   [
    3408,
    "Sunset Crater Volcano National Monument",
    3040,
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
 "t": "National Monument",
 "verdict": "no size on page"
}
```

## US-13335 Saddleback Mountain BLM Special Recreation Management Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Saddleback Mountain BLM Special Recreation Management Area",
 "official": null,
 "ours": {
  "acres": 5,
  "dissolved": {
   "after": 19,
   "before": 38,
   "copies": 1,
   "key_union": 5,
   "parts": 0,
   "records": 2,
   "summed": 19,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 38 -> 19 acres",
  "pieces": [
   [
    "rma13825",
    "Saddleback Mountain Facility Area",
    19,
    "words"
   ]
  ],
  "pin": "just outside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 5,
 "t": "BLM Special Recreation Management Area",
 "verdict": "no size on page"
}
```

## US-6071 Little Black Mountain Petroglyph Site State Historic Site
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Little Black Mountain Petroglyph Site State Historic Site",
 "official": null,
 "ours": {
  "acres": 241,
  "manager": "",
  "pieces": [
   [
    "sgakh85",
    "Little Black Mountain",
    241,
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
 "t": "State Historic Site",
 "verdict": "no size on page"
}
```

## US-1059 Kartchner Caverns State Park
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Kartchner Caverns State Park",
 "official": null,
 "ours": {
  "acres": 727,
  "dissolved": {
   "after": 727,
   "before": 2168,
   "copies": 2,
   "parts": 0,
   "records": 3,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 2168 -> 727 acres",
  "pieces": [
   [
    167511,
    "Kartchner Caverns State Park",
    727,
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

## US-0645 Glen Canyon National Recreation Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Glen Canyon National Recreation Area",
 "note": "whole park compared (POTA lists it in 2 states: {'US-AZ': 44648, 'US-UT': 1192449})",
 "official": {
  "acres": 1250000.0,
  "as": "1.25 million acres",
  "clean": true,
  "line": "earch This Site All NPS Exiting nps.gov Cancel Glen Canyon National Recreation Area • AZ,UT Encompassing over 1.25 million acres, Glen Canyon National Recreation Area offers unparalleled opportunities for water-based & backcountry recreat",
  "read": "2026-11-09",
  "sent": "Encompassing over 1.25 million acres, Glen Canyon National Recreation Area offers unparalleled opportunities for water-based & backcountry recreation.",
  "url": "https://www.nps.gov/glca/index.htm",
  "why": "clean total"
 },
 "ours": {
  "acres": 1237097,
  "acres_by_state": {
   "US-AZ": 44648,
   "US-UT": 1192449
  },
  "manager": "",
  "pieces": [
   [
    3503,
    "Glen Canyon National Recreation Area",
    44648,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "states": [
   "US-AZ",
   "US-UT"
  ],
  "unknown_pieces": 0,
  "whole_park": true
 },
 "owner_now": null,
 "pct": 1,
 "same_agency": false,
 "score": 6,
 "t": "National Recreation Area",
 "verdict": "agree"
}
```

## US-11982 Base & Meridian State Wildlife Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Base & Meridian State Wildlife Area",
 "official": null,
 "ours": {
  "acres": 448,
  "manager": "",
  "pieces": [
   [
    167493,
    "Base and Meridian Wildlife Area",
    220,
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

## US-10513 Granite Mountain Hotshots State Park
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Granite Mountain Hotshots State Park",
 "official": null,
 "ours": {
  "acres": 320,
  "manager": "",
  "pieces": [
   [
    "sgaze29",
    "Granite Mountain Hotshots Memorial State Park",
    320,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-0194 Havasu National Wildlife Refuge
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Havasu National Wildlife Refuge",
 "note": "whole park compared (POTA lists it in 2 states: {'US-AZ': 32366, 'US-CA': 6909})",
 "official": {
  "acres": 37515.0,
  "as": "37,515 acres",
  "clean": true,
  "line": "D. Roosevelt in 1941 for the primary purpose of providing migratory bird habitat. The refuge is comprised of 37,515 acres along the lower Colorado River in Arizona and California. The refuge protects 30 river miles and encompasses",
  "read": "2026-11-09",
  "sent": "The refuge is comprised of 37,515 acres along the lower Colorado River in Arizona and California.",
  "url": "https://www.fws.gov/refuge/havasu/about-us",
  "why": "clean total"
 },
 "ours": {
  "acres": 39275,
  "acres_by_state": {
   "US-AZ": 32366,
   "US-CA": 6909
  },
  "dissolved": {
   "after": 32366,
   "before": 64642,
   "copies": 1,
   "parts": 0,
   "records": 3,
   "tracts": 2
  },
  "manager": "",
  "note": "3 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 64642 -> 32366 acres",
  "pieces": [
   [
    3931,
    "Havasu National Wildlife Refuge",
    32282,
    "name"
   ],
   [
    183640,
    "Havasu National Wildlife Refuge",
    84,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "states": [
   "US-AZ",
   "US-CA"
  ],
  "unknown_pieces": 0,
  "whole_park": true
 },
 "owner_now": null,
 "pct": 5,
 "same_agency": false,
 "score": 8,
 "t": "National Wildlife Refuge",
 "verdict": "agree"
}
```

## US-0967 Tuzigoot National Monument
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Tuzigoot National Monument",
 "official": null,
 "ours": {
  "acres": 367,
  "manager": "",
  "pieces": [
   [
    3413,
    "Tuzigoot National Monument",
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
 "t": "National Monument",
 "verdict": "no size on page"
}
```

## US-11047 Trigo Mountain Wilderness Area
```json
{
 "checked": "2026-11-09",
 "handover": [
  {
   "date_hint": "1990",
   "kind": "managed by",
   "line": "lderness | Arizona View Map In Full Screen The Trigo Mountain Wilderness (30,300 acres) in Arizona, is managed by the Bureau of Land Management. In 1990, the Trigo Mountain Wilderness became part of the National Wilderness Preservation System esta",
   "owner_now": "Bureau of Land Management",
   "src": "https://www.blm.gov/visit/trigo-mountain-wilderness",
   "why": "the park's page (data/parkinfo)"
  }
 ],
 "n": "Trigo Mountain Wilderness Area",
 "official": {
  "acres": 30300.0,
  "as": "30,300 acres",
  "clean": false,
  "line": "am Flickr LinkedIn Trigo Mountain Wilderness | Arizona View Map In Full Screen The Trigo Mountain Wilderness (30,300 acres) in Arizona, is managed by the Bureau of Land Management. In 1990, the Trigo Mountain Wilderness became part",
  "read": "2026-11-09",
  "sent": "The Trigo Mountain Wilderness (30,300 acres) in Arizona, is managed by the Bureau of Land Management.",
  "url": "https://www.blm.gov/visit/trigo-mountain-wilderness",
  "why": "total-looking"
 },
 "ours": {
  "acres": 29133,
  "manager": "",
  "pieces": [],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 2
 },
 "owner_now": "Bureau of Land Management",
 "pct": 4,
 "same_agency": false,
 "score": 7,
 "t": "Wilderness Area",
 "verdict": "agree"
}
```
