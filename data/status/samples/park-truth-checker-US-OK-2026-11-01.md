# park truth checker: US-OK random sample of 12 (2026-11-01; seed = date + area, same rows for everyone)

Source file: `data/truth/US-OK.json`

## US-11321 Winding Stair Mountain National Recreation Area
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-11-01",
 "handover": [],
 "n": "Winding Stair Mountain National Recreation Area",
 "official": null,
 "ours": {
  "acres": 26617,
  "manager": "",
  "pieces": [
   [
    "fsod70",
    "Winding Stair Mountain National Recreation Area",
    26617,
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
 "t": "National Recreation Area",
 "verdict": "unsure"
}
```

## US-2773 Black Mesa State Park
```json
{
 "cause": "agency smaller: our outline may hold water, a lease or a neighbour tract",
 "checked": "2026-11-01",
 "handover": [],
 "n": "Black Mesa State Park",
 "official": {
  "acres": 1600.0,
  "as": "1,600 acres",
  "clean": false,
  "line": "ecreation Department in conjunction with Black Mesa State Park. The nature preserve consists of approximately 1,600 acres where visitors can hike and enjoy 23 rare plants and eight rare animal species. The unique area marks the poi",
  "read": "2026-11-01",
  "sent": "The nature preserve consists of approximately 1,600 acres where visitors can hike and enjoy 23 rare plants and eight rare animal species.",
  "url": "https://www.travelok.com/state-parks/black-mesa-state-park-nature-preserve",
  "why": "total-looking"
 },
 "ours": {
  "acres": 2913,
  "manager": "",
  "pieces": [
   [
    237667,
    "Black Mesa State Park & Nature Preserve",
    2646,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 2
 },
 "owner_now": null,
 "pct": 82,
 "same_agency": false,
 "score": 6,
 "t": "State Park",
 "verdict": "off"
}
```

## US-8117 Cimarron Bluff Wildlife Management Area
```json
{
 "cause": "agency smaller: our outline may hold water, a lease or a neighbour tract",
 "checked": "2026-11-01",
 "handover": [],
 "n": "Cimarron Bluff Wildlife Management Area",
 "official": {
  "acres": 3590.0,
  "as": "3,590 acres",
  "clean": true,
  "line": "the Wildlife Department. For complete conservation passport license info go here . Cimarron Bluff WMA covers 3,590 acres in northeastern Harper County. Located north of the city of Woodward. It is four miles south of the junction",
  "read": "2026-11-01",
  "sent": "Cimarron Bluff WMA covers 3,590 acres in northeastern Harper County.",
  "url": "https://www.wildlifedepartment.com/hunting/wma/northwest/cimarron-bluff",
  "why": "clean total"
 },
 "ours": {
  "acres": 7461,
  "family_fold": "layers {'padus': 7461, 'sgokc': 3539}: one land in 2 layers, the padus copy used (3,539 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    237717,
    "Cimarron Bluff Wildlife Management Area",
    7461,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 108,
 "same_agency": false,
 "score": 5,
 "t": "Wildlife Management Area",
 "verdict": "off"
}
```

## US-2788 Keystone State Park
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Keystone State Park",
 "official": null,
 "ours": {
  "acres": 322,
  "manager": "",
  "pieces": [
   [
    237685,
    "Keystone State Park",
    453,
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
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-8661 Washita County Wildlife Management Area
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-01",
 "handover": [],
 "n": "Washita County Wildlife Management Area",
 "official": {
  "acres": 240.0,
  "as": "240 acres",
  "clean": true,
  "line": "the Wildlife Department. For complete conservation passport license info go here . Washita County WMA covers 240 acres in Washita Co. It is located approximately 3 miles northwest of Cordell, Oklahoma (From Jct. of HWY 152 and H",
  "read": "2026-11-01",
  "sent": "Washita County WMA covers 240 acres in Washita Co.",
  "url": "https://www.wildlifedepartment.com/hunting/wma/southwest/washita-county",
  "why": "clean total"
 },
 "ours": {
  "acres": 123,
  "dissolved": {
   "after": 236,
   "before": 472,
   "copies": 1,
   "key_union": 123,
   "parts": 0,
   "records": 2,
   "summed": 236,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 472 -> 236 acres",
  "pieces": [
   [
    "odw101",
    "Washita County Wildlife Management Area",
    236,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 49,
 "same_agency": false,
 "score": 5,
 "t": "Wildlife Management Area",
 "verdict": "off"
}
```

## US-2802 Sequoyah Bay State Park
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Sequoyah Bay State Park",
 "official": null,
 "ours": {
  "acres": 2093,
  "manager": "",
  "pieces": [
   [
    237702,
    "Sequoyah Bay State Park",
    178,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 2
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-2803 Sequoyah State Park
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Sequoyah State Park",
 "official": null,
 "ours": {
  "acres": 2093,
  "manager": "",
  "pieces": [
   [
    237702,
    "Sequoyah Bay State Park",
    178,
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
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-11322 Beech Creek National Scenic Reserve
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 1.8 million acres, a statewide / agency-wide total (over a million acres) on a park that is not a big federal unit)",
 "checked": "2026-11-01",
 "handover": [],
 "n": "Beech Creek National Scenic Reserve",
 "official": {
  "acres": 1800000.0,
  "as": "1.8 million acres",
  "clean": false,
  "line": "ildfire Dashboard Plan Your Adventure We're the oldest and largest National Forest in the South, encompassing 1.8 million acres in Arkansas and Oklahoma. Come explore T T T Welcome to Ouachita National Forest Located in both Arkansas and",
  "read": "2026-11-01",
  "sent": "We're the oldest and largest National Forest in the South, encompassing 1.8 million acres in Arkansas and Oklahoma.",
  "url": "https://www.fs.usda.gov/r08/ouachita",
  "why": "a statewide / agency-wide total (over a million acres) on a park that is not a big federal unit"
 },
 "ours": {
  "acres": 8042,
  "manager": "",
  "pieces": [
   [
    "fsod74",
    "Beech Creek National Scenic Area",
    8042,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 100,
 "same_agency": false,
 "score": 7,
 "t": "Scenic Reserve",
 "verdict": "unsure"
}
```

## US-6343 Canton Wildlife Management Area
```json
{
 "cause": "agency smaller: our outline may hold water, a lease or a neighbour tract",
 "checked": "2026-11-01",
 "handover": [],
 "n": "Canton Wildlife Management Area",
 "official": {
  "acres": 14877.0,
  "as": "14,877 acres",
  "clean": true,
  "line": "ac. Non-Ambulatory Acres: 1,077.80 ac. Canton WMA & WRP Map WMA Legend Canton WMA & WRP Map Canton WMA covers 14,877 acres in Blaine, Dewey, and Major Counties in northwest Oklahoma, located around Canton Lake (northwest of Canton,",
  "read": "2026-11-01",
  "sent": "Canton WMA covers 14,877 acres in Blaine, Dewey, and Major Counties in northwest Oklahoma, located around Canton Lake (northwest of Canton, Oklahoma, or west of Longdale, Oklahoma).",
  "url": "https://www.wildlifedepartment.com/hunting/wma/northwest/canton",
  "why": "clean total"
 },
 "ours": {
  "acres": 20502,
  "dissolved": {
   "after": 29205,
   "before": 46934,
   "copies": 1,
   "families": {
    "odw": 17729,
    "padus": 11476
   },
   "family_fold": 11476,
   "family_used": "odw",
   "key_union": 20502,
   "parts": 0,
   "records": 3,
   "summed": 17729,
   "tracts": 2
  },
  "family_fold": "layers {'odw': 17729, 'padus': 11476}: one land in 2 layers, the odw copy used (11,476 ac of copies not added)",
  "manager": "",
  "note": "3 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 46934 -> 29205 acres",
  "pieces": [
   [
    "odw13",
    "Canton Wildlife Management Area",
    17729,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 38,
 "same_agency": false,
 "score": 6,
 "t": "Wildlife Management Area",
 "verdict": "off"
}
```

## US-12027 Altus-Lugert State Fishing Lake
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Altus-Lugert State Fishing Lake",
 "official": {
  "acres": 5089.0,
  "as": "5089.00 ac",
  "clean": false,
  "line": "WY 44. Lake Details Shoreline Length: 32.00 mi. Volume: 122516.00 ac. ft. Max. Depth: 48.50 ft. Surface Area: 5089.00 ac. Located Kiowa , Greer Counties Recreational Facilities Quartz Mountain State Park manages campgrounds, lodge",
  "read": "2026-11-01",
  "sent": "Surface Area: 5089.00 ac.",
  "url": "https://www.wildlifedepartment.com/fishing/wheretofish/southwest/altus-lugert-reservoir",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 4461,
  "dissolved": {
   "after": 3681,
   "before": 7362,
   "copies": 1,
   "key_union": 4461,
   "parts": 0,
   "records": 2,
   "summed": 3681,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 7362 -> 3681 acres",
  "pieces": [
   [
    "odw1",
    "Altus Lugert Wildlife Management Area",
    3681,
    "name"
   ]
  ],
  "pin": "well outside",
  "src": "",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 12,
 "same_agency": false,
 "score": 6,
 "t": "State Fishing Lake",
 "verdict": "agree"
}
```

## US-6374 Sandy Sanders Wildlife Management Area
```json
{
 "cause": "agency smaller: our outline may hold water, a lease or a neighbour tract",
 "checked": "2026-11-01",
 "handover": [],
 "n": "Sandy Sanders Wildlife Management Area",
 "official": {
  "acres": 29766.0,
  "as": "29,766 acres",
  "clean": true,
  "line": "y the Wildlife Department. For complete conservation passport license info go here . Sandy Sanders WMA covers 29,766 acres of Greer and Beckham counties in southwest Oklahoma. The area is located 26 miles northwest of Mangum and 26",
  "read": "2026-11-01",
  "sent": "Sandy Sanders WMA covers 29,766 acres of Greer and Beckham counties in southwest Oklahoma.",
  "url": "https://www.wildlifedepartment.com/hunting/wma/southwest/sandy-sanders",
  "why": "clean total"
 },
 "ours": {
  "acres": 36669,
  "dissolved": {
   "after": 36669,
   "before": 73338,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 73338 -> 36669 acres",
  "pieces": [
   [
    "odw87",
    "Sandy Sanders Wildlife Management Area",
    36669,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 23,
 "same_agency": false,
 "score": 6,
 "t": "Wildlife Management Area",
 "verdict": "off"
}
```

## US-6346 Hal and Fern Cooper Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Hal and Fern Cooper Wildlife Management Area",
 "official": {
  "acres": 16120.0,
  "as": "16,120 ac",
  "clean": false,
  "line": "nting: (580) 334-0343 Game Warden: (580) 727-5048 (Harper) (580) 334-0353 (Woodward) Area Details Area Acres: 16,120 ac. Non-Ambulatory Acres: 528.00 ac. Cooper WMA Map WMA Legend Cooper WMA Map Conservation Passport Area Conserv",
  "read": "2026-11-01",
  "sent": "16,120 ac.",
  "url": "http://www.wildlifedepartment.com/hunting/wma/northwest/cooper",
  "why": "total-looking"
 },
 "ours": {
  "acres": 16304,
  "dissolved": {
   "after": 16304,
   "before": 32608,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 32608 -> 16304 acres",
  "pieces": [
   [
    "odw35",
    "Hal and Fern Cooper Wildlife Management Area",
    16304,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 1,
 "same_agency": false,
 "score": 8,
 "t": "Wildlife Management Area",
 "verdict": "agree"
}
```
