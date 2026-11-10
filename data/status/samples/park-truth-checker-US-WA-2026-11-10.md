# park truth checker: US-WA random sample of 12 (2026-11-10; seed = date + area, same rows for everyone)

Source file: `data/truth/US-WA.json`

## US-3272 Squak Mountain State Park
```json
{
 "checked": "2026-11-10",
 "handover": [],
 "n": "Squak Mountain State Park",
 "official": null,
 "ours": {
  "acres": 1727,
  "dissolved": {
   "after": 1592,
   "before": 3183,
   "copies": 1,
   "key_union": 1727,
   "parts": 0,
   "records": 2,
   "summed": 1592,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 3183 -> 1592 acres",
  "pieces": [
   [
    271539,
    "Squak Mountain",
    1592,
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

## US-3288 Wenatchee Confluence State Park
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-11-10",
 "handover": [],
 "n": "Wenatchee Confluence State Park",
 "official": null,
 "ours": {
  "acres": 231,
  "family_fold": "layers {'padus': 231, 'sgwaa': 194}: one land in 2 layers, the padus copy used (194 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    271555,
    "Wenatchee Confluence",
    231,
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
 "verdict": "unsure"
}
```

## US-12544 Sinlahekin State Wildlife Area
```json
{
 "checked": "2026-11-10",
 "handover": [],
 "n": "Sinlahekin State Wildlife Area",
 "official": {
  "acres": 23980.0,
  "as": "23, 980 acres",
  "clean": true,
  "line": "rtment of Fish and Wildlife updated the management plan for the Scotch Creek Wildlife Area, which encompasses 23, 980 acres in Okanogan County, and the nearby Sinlahekin Wildlife Area in north central Washington. The plan, called the",
  "read": "2026-11-10",
  "sent": "In 2017, the Washington Department of Fish and Wildlife updated the management plan for the Scotch Creek Wildlife Area, which encompasses 23, 980 acres in Okanogan County, and the nearby Sinlahekin Wildlife Area in north central Washington.",
  "url": "https://wdfw.wa.gov/places-to-go/wildlife-areas/sinlahekin-wildlife-area-unit",
  "why": "clean total"
 },
 "ours": {
  "acres": 25317,
  "manager": "",
  "pieces": [
   [
    271388,
    "Sinlahekin Wildlife Area Complex",
    17951,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 25
 },
 "owner_now": null,
 "pct": 6,
 "same_agency": false,
 "score": 7,
 "t": "State Wildlife Area",
 "verdict": "agree"
}
```

## US-12340 Ebey Island State Wildlife Area
```json
{
 "checked": "2026-11-10",
 "handover": [],
 "n": "Ebey Island State Wildlife Area",
 "official": {
  "acres": 800.0,
  "as": "800 acres",
  "clean": false,
  "line": "ormation updated daily. Conservation This unit consists of approximately 400 acres of forested swamp and over 800 acres of grassland. The forested portion was logged in the 1890s and reforested naturally into one of the few remai",
  "read": "2026-11-10",
  "sent": "This unit consists of approximately 400 acres of forested swamp and over 800 acres of grassland.",
  "url": "https://wdfw.wa.gov/places-to-go/wildlife-areas/ebey-island-wildlife-area-unit",
  "why": "total-looking"
 },
 "ours": {
  "acres": 873,
  "manager": "",
  "pieces": [
   [
    158309,
    "Ebey Island",
    1273,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 2
 },
 "owner_now": null,
 "pct": 9,
 "same_agency": false,
 "score": 7,
 "t": "State Wildlife Area",
 "verdict": "agree"
}
```

## US-3215 Lake Isabella State Park
```json
{
 "checked": "2026-11-10",
 "handover": [],
 "n": "Lake Isabella State Park",
 "official": null,
 "ours": {
  "acres": 268,
  "family_fold": "layers {'padus': 192, 'sgwaa': 188}: one land in 2 layers, the padus copy used (188 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    271471,
    "Lake Isabella",
    192,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "water outline only",
  "unknown_pieces": 2
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-12502 Golden Doe State Wildlife Area
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 242 Acres, no total words near it)",
 "checked": "2026-11-10",
 "handover": [],
 "n": "Golden Doe State Wildlife Area",
 "official": {
  "acres": 242.0,
  "as": "242 Acres",
  "clean": false,
  "line": "d by private property to the southwest. This unit is part of the Methow Wildlife Area . Game Management Unit: 242 Acres: 1,994 Getting there Maps and directions to WDFW-managed access points for this unit. Opens Google Maps in a",
  "read": "2026-11-10",
  "sent": "242 Acres: 1,994",
  "url": "https://wdfw.wa.gov/places-to-go/wildlife-areas/golden-doe-wildlife-area-unit",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 1562,
  "manager": "",
  "pieces": [
   [
    158323,
    "Golden Doe",
    1903,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 2
 },
 "owner_now": null,
 "pct": 545,
 "same_agency": false,
 "score": 7,
 "t": "State Wildlife Area",
 "verdict": "unsure"
}
```

## US-3273 Squilchuck State Park
```json
{
 "checked": "2026-11-10",
 "handover": [],
 "n": "Squilchuck State Park",
 "official": null,
 "ours": {
  "acres": 176,
  "family_fold": "layers {'padus': 254, 'sgwaa': 247}: one land in 2 layers, the padus copy used (247 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    271541,
    "Squilchuck",
    254,
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

## US-12247 Billy Clapp Lake Wildlife Area State Fish and Wildlife Area
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 272 Acres, no total words near it)",
 "checked": "2026-11-10",
 "handover": [],
 "n": "Billy Clapp Lake Wildlife Area State Fish and Wildlife Area",
 "official": {
  "acres": 272.0,
  "as": "272 Acres",
  "clean": false,
  "line": "Road J NE from Stratford Road. This unit is part of the Columbia Basin Wildlife Area . Game Management Unit: 272 Acres: 4,573 Getting there Maps and directions to WDFW-managed access points for this unit. Opens Google Maps in a",
  "read": "2026-11-10",
  "sent": "272 Acres: 4,573",
  "url": "https://wdfw.wa.gov/places-to-go/wildlife-areas/billy-clapp-lake-wildlife-area-unit#recreation-access",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 5584,
  "manager": "",
  "pieces": [
   [
    2304,
    "Billy Clapp Lake",
    955,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "water outline only",
  "unknown_pieces": 5
 },
 "owner_now": null,
 "pct": 1953,
 "same_agency": false,
 "score": 7,
 "t": "State Fish and Wildlife Area",
 "verdict": "unsure"
}
```

## US-10694 Sun Lakes Wildlife Area
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 272 Acres, no total words near it)",
 "checked": "2026-11-10",
 "handover": [],
 "n": "Sun Lakes Wildlife Area",
 "official": {
  "acres": 272.0,
  "as": "272 Acres",
  "clean": false,
  "line": "re rock characterize this unit. This unit is part of the Columbia Basin Wildlife Area . Game Management Unit: 272 Acres: 6,748 Getting there Maps and directions to WDFW-managed access points for this unit. Opens Google Maps in a",
  "read": "2026-11-10",
  "sent": "272 Acres: 6,748",
  "url": "https://wdfw.wa.gov/places-to-go/wildlife-areas/sun-lakes-wildlife-area-unit",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 5901,
  "manager": "",
  "pieces": [],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 2
 },
 "owner_now": null,
 "pct": 2069,
 "same_agency": false,
 "score": 6,
 "t": "Wildlife Area",
 "verdict": "unsure"
}
```

## US-0340 Spring Creek Hatchery State Park
```json
{
 "checked": "2026-11-10",
 "handover": [],
 "n": "Spring Creek Hatchery State Park",
 "official": null,
 "ours": {
  "acres": 35,
  "dissolved": {
   "after": 110,
   "before": 120,
   "copies": 1,
   "key_union": 35,
   "parts": 0,
   "records": 4,
   "summed": 110,
   "tracts": 3
  },
  "manager": "",
  "note": "4 joined records = 3 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 120 -> 110 acres",
  "pieces": [
   [
    4349,
    "Spring Creek National Fish Hatchery",
    50,
    "name"
   ],
   [
    5307,
    "Spring Creek National Fish Hatchery",
    50,
    "name"
   ],
   [
    271399,
    "Spring Creek Hatchery",
    10,
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

## US-3209 Kanaskat-Palmer State Park
```json
{
 "checked": "2026-11-10",
 "handover": [],
 "n": "Kanaskat-Palmer State Park",
 "official": null,
 "ours": {
  "acres": 455,
  "dissolved": {
   "after": 541,
   "before": 1076,
   "copies": 1,
   "key_union": 455,
   "parts": 0,
   "records": 2,
   "summed": 541,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1076 -> 541 acres",
  "pieces": [
   [
    "sgwaa84",
    "Kanaskat-Palmer",
    541,
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

## US-13360 Lake Washington State Fishing Lake
```json
{
 "checked": "2026-11-10",
 "handover": [],
 "n": "Lake Washington State Fishing Lake",
 "official": {
  "acres": 21933.6,
  "as": "21933.60 ac",
  "clean": true,
  "line": "mallmouth bass Sockeye salmon Tench Threespine stickleback Yellow perch View larger map County: King Acreage: 21933.60 ac. Elevation: 17 ft. Geo Code: L9015 Center: 47.601594, -122.275275 Open in Google Maps Fishing resources Emerg",
  "read": "2026-11-10",
  "sent": "Acreage: 21933.60 ac.",
  "url": "https://wdfw.wa.gov/fishing/locations/lowland-lakes/lake-washington",
  "why": "clean total"
 },
 "ours": {
  "acres": 0,
  "manager": "",
  "pieces": [],
  "pin": "inside",
  "src": "water outline only",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": null,
 "same_agency": false,
 "score": 7,
 "t": "State Fishing Lake",
 "verdict": "ours unknown"
}
```
