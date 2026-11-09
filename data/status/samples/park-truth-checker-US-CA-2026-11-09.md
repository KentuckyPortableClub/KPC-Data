# park truth checker: US-CA random sample of 12 (2026-11-09; seed = date + area, same rows for everyone)

Source file: `data/truth/US-CA.json`

## US-0648 Santa Monica Mountains National Recreation Area
```json
{
 "checked": "2026-11-09",
 "handover": [
  {
   "date_hint": null,
   "kind": "managed by",
   "line": "rnia. Visitor Center Store The Anthony C. Beilenson Interagency Visitor Center features a bookstore managed by Western National Parks Association . You can purchase memorabilia, guidebooks, puppets and more. Last updated: May 11, 2022 Park foote",
   "owner_now": "Western National Parks Association",
   "src": "https://www.nps.gov/samo/learn/index.htm",
   "why": "about / history page of the park's site"
  },
  {
   "date_hint": null,
   "kind": "managed by",
   "line": "tics Acreage Gross Area within recreation area boundary for FY 2009: 153,785 Acres of Land Property owned and managed by the National Park Service within the recreation area boundary: 23,648 Acres Visitation Total Recreation Visits FY 2023: 759,352 Total Recreation Visits FY 2022:",
   "owner_now": "National Park Service",
   "src": "https://www.nps.gov/samo/learn/management/statistics.htm",
   "why": "NPS park statistics page"
  }
 ],
 "n": "Santa Monica Mountains National Recreation Area",
 "official": {
  "acres": 23648.0,
  "as": "23,648 Acres",
  "clean": false,
  "line": "85 Acres of Land Property owned and managed by the National Park Service within the recreation area boundary: 23,648 Acres Visitation Total Recreation Visits FY 2023: 759,352 Total Recreation Visits FY 2022: 795,217 Total Recreation",
  "read": "2026-11-09",
  "sent": "Property owned and managed by the National Park Service within the recreation area boundary: 23,648 Acres",
  "url": "https://www.nps.gov/samo/learn/management/statistics.htm",
  "why": "total-looking"
 },
 "ours": {
  "acres": 22293,
  "manager": "",
  "pieces": [
   [
    3512,
    "Santa Monica Mountains National Recreation Area",
    23867,
    "name"
   ],
   [
    169062,
    "Santa Monica Mountains National Recreation Area",
    77,
    "name"
   ],
   [
    170188,
    "Santa Monica Mountains National Recreation Area",
    48,
    "name"
   ],
   [
    170191,
    "Santa Monica Mountains National Recreation Area",
    3,
    "name"
   ],
   [
    170189,
    "Santa Monica Mountains National Recreation Area",
    2,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": "Western National Parks Association",
 "pct": 6,
 "same_agency": false,
 "score": 7,
 "t": "National Recreation Area",
 "verdict": "agree"
}
```

## US-1175 Morro Bay State Park
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Morro Bay State Park",
 "official": null,
 "ours": {
  "acres": 2597,
  "family_fold": "layers {'sgcab': 2399, 'padus': 2781}: one land in 2 layers, the padus copy used (2,399 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    184028,
    "Morro Bay State Park",
    1842,
    "name"
   ],
   [
    184029,
    "Morro Bay State Park",
    483,
    "name"
   ],
   [
    183353,
    "Morro Bay State Park",
    456,
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

## US-1122 Andrew Molera State Park
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Andrew Molera State Park",
 "official": {
  "acres": 5000.0,
  "as": "5,000 acres",
  "clean": false,
  "line": "ity No upcoming camping/lodging reservations at this time. About Andrew Molera State Park Encompassing almost 5,000 acres of largely undeveloped diverse coast range terrain with 15 miles of trails and the Big Sur Rivermouth. Cultur",
  "read": "2026-11-09",
  "sent": "Encompassing almost 5,000 acres of largely undeveloped diverse coast range terrain with 15 miles of trails and the Big Sur Rivermouth.",
  "url": "https://www.parks.ca.gov/?page_id=582",
  "why": "total-looking"
 },
 "ours": {
  "acres": 4698,
  "dissolved": {
   "after": 4698,
   "before": 9394,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 9394 -> 4698 acres",
  "pieces": [
   [
    "sgcab468",
    "Andrew Molera SP",
    4698,
    "reviewed"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 6,
 "same_agency": false,
 "score": 8,
 "t": "State Park",
 "verdict": "agree"
}
```

## US-0199 Lower Klamath National Wildlife Refuge
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Lower Klamath National Wildlife Refuge",
 "note": "whole park compared (POTA lists it in 2 states: {'US-CA': 44322, 'US-OR': 7385})",
 "official": {
  "acres": 50092.0,
  "as": "50,092 acre",
  "clean": false,
  "line": "nation, 10 of them on U.S. Fish and Wildlife Service lands. Learn more about National Historic Landmark . The 50,092-acre refuge is a varied mix of intensively managed shallow marshes, open water, grassy uplands, and croplands that",
  "read": "2026-11-09",
  "sent": "The 50,092-acre refuge is a varied mix of intensively managed shallow marshes, open water, grassy uplands, and croplands that provide feeding, resting, nesting, and brood-rearing habitat for waterfowl and other water birds.",
  "url": "https://www.fws.gov/refuge/lower-klamath/about-us",
  "why": "total-looking"
 },
 "ours": {
  "acres": 51707,
  "acres_by_state": {
   "US-CA": 44322,
   "US-OR": 7385
  },
  "dissolved": {
   "after": 44322,
   "before": 88641,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 88641 -> 44322 acres",
  "pieces": [
   [
    4058,
    "Lower Klamath National Wildlife Refuge",
    44322,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "states": [
   "US-CA",
   "US-OR"
  ],
  "unknown_pieces": 0,
  "whole_park": true
 },
 "owner_now": null,
 "pct": 3,
 "same_agency": false,
 "score": 8,
 "t": "National Wildlife Refuge",
 "verdict": "agree"
}
```

## US-4543 Mojave Trails National Monument
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Mojave Trails National Monument",
 "official": {
  "acres": 1600000.0,
  "as": "1.6 million acres",
  "clean": true,
  "line": "Facebook Instagram Flickr LinkedIn Mojave Trails National Monument The Mojave Trails National Monument spans 1.6 million acres of federal lands, including more than 350,000 acres of already Congressionally -designated wilderness, manage",
  "read": "2026-11-09",
  "sent": "The Mojave Trails National Monument spans 1.6 million acres of federal lands, including more than 350,000 acres of already Congressionally -designated wilderness, managed by the Bureau of Land Management between Barstow and Needles, California.",
  "url": "https://www.blm.gov/programs/national-conservation-lands/california/mojave-trails-national-monument",
  "why": "clean total"
 },
 "ours": {
  "acres": 1747102,
  "manager": "",
  "pieces": [],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 4
 },
 "owner_now": null,
 "pct": 9,
 "same_agency": false,
 "score": 7,
 "t": "National Monument",
 "verdict": "agree"
}
```

## US-3561 San Timoteo Canyon State Park
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "San Timoteo Canyon State Park",
 "official": null,
 "ours": {
  "acres": 1196,
  "dissolved": {
   "after": 1068,
   "before": 2114,
   "copies": 1,
   "key_union": 1196,
   "parts": 0,
   "records": 3,
   "summed": 1068,
   "tracts": 2
  },
  "manager": "",
  "note": "3 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 2114 -> 1068 acres",
  "pieces": [
   [
    183910,
    "San Timoteo Canyon",
    1060,
    "name"
   ],
   [
    183911,
    "San Timoteo Canyon",
    8,
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

## US-1192 Russian Gulch State Park
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 150,000 acres, no total words near it)",
 "checked": "2026-11-09",
 "handover": [],
 "n": "Russian Gulch State Park",
 "official": {
  "acres": 150000.0,
  "as": "150,000 acres",
  "clean": false,
  "line": "n't Move Firewood Information Proud Partner Save the Redwoods League has helped permanently protect more than 150,000 acres in 37 of California State Parks redwood parks. Find out more at SaveTheRedwoods.org.",
  "read": "2026-11-09",
  "sent": "Save the Redwoods League has helped permanently protect more than 150,000 acres in 37 of California State Parks redwood parks.",
  "url": "https://www.parks.ca.gov/?page_id=432",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 810,
  "dissolved": {
   "after": 1338,
   "before": 2636,
   "copies": 0,
   "key_union": 810,
   "parts": 2,
   "records": 4,
   "summed": 1338,
   "tracts": 2
  },
  "manager": "",
  "note": "4 joined records = 2 tracts: 0 copies of a tract (same acres, another layer) and 2 fee tracts under a designation record folded; summed 2636 -> 1338 acres",
  "pieces": [
   [
    "sgcab618",
    "Russian Gulch SP",
    1297,
    "reviewed"
   ],
   [
    183355,
    "Russian Gulch State Park",
    41,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 99,
 "same_agency": false,
 "score": 7,
 "t": "State Park",
 "verdict": "unsure"
}
```

## US-3530 Pescadero State Beach
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Pescadero State Beach",
 "official": null,
 "ours": {
  "acres": 412,
  "family_fold": "layers {'sgcab': 1281, 'padus': 91}: one land in 2 layers, the sgcab copy used (91 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgcab593",
    "Pescadero SB",
    698,
    "name"
   ],
   [
    "sgcab673",
    "Pescadero Marsh NP",
    583,
    "words"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "State Beach",
 "verdict": "no size on page"
}
```

## US-0894 Tuolumne National Wild and Scenic River
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-11-09",
 "handover": [],
 "n": "Tuolumne National Wild and Scenic River",
 "official": null,
 "ours": {
  "acres": 6475,
  "manager": "",
  "pieces": [
   [
    "fwsr252",
    "Tuolumne, California National Wild and Scenic River",
    7057,
    "words"
   ],
   [
    "fwsr149",
    "Tuolumne, California National Wild and Scenic River",
    1233,
    "words"
   ],
   [
    "fwsr79",
    "Tuolumne, California National Wild and Scenic River",
    89,
    "words"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "National Wild and Scenic River",
 "verdict": "unsure"
}
```

## US-3447 Indio Hills Palms State Park
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Indio Hills Palms State Park",
 "official": null,
 "ours": {
  "acres": 5146,
  "dissolved": {
   "after": 5707,
   "before": 11364,
   "copies": 1,
   "key_union": 5146,
   "parts": 0,
   "records": 3,
   "summed": 5707,
   "tracts": 2
  },
  "manager": "",
  "note": "3 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 11364 -> 5707 acres",
  "pieces": [
   [
    183908,
    "Indio Hills Palms",
    5703,
    "name"
   ],
   [
    "sgcab770",
    "Indio Hills Palms",
    4,
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

## US-1197 Sinkyone Wilderness State Park
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Sinkyone Wilderness State Park",
 "official": null,
 "ours": {
  "acres": 8035,
  "dissolved": {
   "after": 15110,
   "before": 23100,
   "copies": 1,
   "families": {
    "padus": 8035,
    "sgcab": 7075
   },
   "family_fold": 7075,
   "family_used": "padus",
   "parts": 0,
   "records": 3,
   "tracts": 2
  },
  "family_fold": "layers {'padus': 8035, 'sgcab': 7075}: one land in 2 layers, the padus copy used (7,075 ac of copies not added)",
  "manager": "",
  "note": "3 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 23100 -> 15110 acres",
  "pieces": [
   [
    184165,
    "Sinkyone Wilderness State Park",
    8035,
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

## US-4465 Shasta-Trinity National Forest
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Shasta-Trinity National Forest",
 "official": {
  "acres": 2100000.0,
  "as": "2.1 million acre",
  "clean": false,
  "line": "t is the largest National Forest in the state with a diverse landscape ranging from 1,000 to 14,179 feet. The 2.1 million-acre forest encompasses five wilderness areas, hundreds of mountain lakes and 6,278 miles of streams and rivers. F",
  "read": "2026-11-09",
  "sent": "The 2.1 million-acre forest encompasses five wilderness areas, hundreds of mountain lakes and 6,278 miles of streams and rivers.",
  "url": "https://www.fs.usda.gov/stnf",
  "why": "total-looking"
 },
 "ours": {
  "acres": 2140241,
  "manager": "",
  "pieces": [
   [
    2870,
    "Shasta-Trinity National Forest (Shasta National Forest)",
    1083432,
    "name"
   ],
   [
    2885,
    "Shasta-Trinity National Forest (Trinity National Forest)",
    1056809,
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
 "score": 7,
 "t": "National Forest",
 "verdict": "agree"
}
```
