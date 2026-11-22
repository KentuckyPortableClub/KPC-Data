# park truth checker: US-OK random sample of 12 (2026-11-22; seed = date + area, same rows for everyone)

Source file: `data/truth/US-OK.json`

## US-11641 Tishomingo National Fish Hatchery
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Tishomingo National Fish Hatchery",
 "official": {
  "acres": 220.0,
  "as": "220 acre",
  "clean": true,
  "line": "to improve our ability to support conservation efforts. Services About Tishomingo National Fish Hatchery is a 220-acre facility in south-central Oklahoma established in the 1930s to provide warm-water fish for stocking. It plays",
  "read": "2026-11-22",
  "sent": "Tishomingo National Fish Hatchery is a 220-acre facility in south-central Oklahoma established in the 1930s to provide warm-water fish for stocking.",
  "url": "https://www.fws.gov/fish-hatchery/tishomingo",
  "why": "clean total"
 },
 "ours": {
  "acres": 232,
  "manager": "",
  "pieces": [
   [
    4398,
    "Tishomingo National Fish Hatchery",
    230,
    "name"
   ],
   [
    5355,
    "Tishomingo National Fish Hatchery",
    230,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 5,
 "same_agency": false,
 "score": 8,
 "t": "National Fish Hatchery",
 "verdict": "agree"
}
```

## US-2787 Hugo Lake State Park
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Hugo Lake State Park",
 "official": null,
 "ours": {
  "acres": 9337,
  "manager": "",
  "pieces": [
   [
    237684,
    "Hugo Lake State Park",
    9337,
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

## US-8135 Optima Wildlife Management Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Optima Wildlife Management Area",
 "official": {
  "acres": 8062.0,
  "as": "8,062 ac",
  "clean": false,
  "line": "ontent Optima WMA Contacts Hunting: (806) 339-5175 Game Warden: 405-593-0463 (Texas) Area Details Area Acres: 8,062 ac. Optima WMA Map WMA Legend Optima WMA Map Attention Hunters: Chronic Wasting Disease has been detected in the",
  "read": "2026-11-22",
  "sent": "8,062 ac.",
  "url": "https://www.wildlifedepartment.com/hunting/wma/northwest/optima",
  "why": "total-looking"
 },
 "ours": {
  "acres": 9015,
  "dissolved": {
   "after": 9015,
   "before": 18030,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 18030 -> 9015 acres",
  "pieces": [
   [
    "odw74",
    "Optima Wildlife Management Area",
    9015,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 12,
 "same_agency": false,
 "score": 8,
 "t": "Wildlife Management Area",
 "verdict": "agree"
}
```

## US-6359 McClellan-Kerr Wildlife Management Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "McClellan-Kerr Wildlife Management Area",
 "official": {
  "acres": 9366.0,
  "as": "9,366 ac",
  "clean": false,
  "line": "equoyah) (918) 625-5796 (Wagoner) (918) 625-5085 (Wagoner) (918) 625-4691 (Muskogee) Area Details Area Acres: 9,366 ac. McClellan-Kerr WMA & WRP - Billy Creek Chouteau Map McClellan-Kerr WMA & WRP - Robert S Kerr Map McClellan-K",
  "read": "2026-11-22",
  "sent": "9,366 ac.",
  "url": "https://www.wildlifedepartment.com/hunting/wma/northeast/mcclellan-kerr",
  "why": "total-looking"
 },
 "ours": {
  "acres": 8210,
  "dissolved": {
   "after": 8210,
   "before": 16420,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 16420 -> 8210 acres",
  "pieces": [
   [
    "odw67",
    "McClellan-Kerr Wildlife Management Area",
    8210,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 3
 },
 "owner_now": null,
 "pct": 12,
 "same_agency": false,
 "score": 8,
 "t": "Wildlife Management Area",
 "verdict": "agree"
}
```

## US-8129 Nanih Waiya State Fishing Lake
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-22",
 "handover": [],
 "n": "Nanih Waiya State Fishing Lake",
 "official": {
  "acres": 1064.0,
  "as": "1064.00 ac",
  "clean": false,
  "line": "Google Map ) is located .5 miles north of US 271 on N4340 Rd. Lake Details Shoreline Length: 2.40 mi. Volume: 1064.00 ac. ft. Max. Depth: 25.00 ft. Surface Area: 131.00 ac. Located Pushmataha County Driving Directions From Clayton",
  "read": "2026-11-22",
  "sent": "Volume: 1064.00 ac.",
  "url": "https://www.wildlifedepartment.com/fishing/wheretofish/southeast/nanih-waiya",
  "why": "total-looking"
 },
 "ours": {
  "acres": 199,
  "dissolved": {
   "after": 199,
   "before": 398,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 398 -> 199 acres",
  "pieces": [
   [
    "odw56",
    "Lake Nanih Waiya",
    199,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 81,
 "same_agency": false,
 "score": 6,
 "t": "State Fishing Lake",
 "verdict": "off"
}
```

## US-2806 Talimena State Park
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Talimena State Park",
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
 "score": 7,
 "t": "State Park",
 "verdict": "ours unknown"
}
```

## US-2782 Great Plains State Park
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 400 acres, no total words near it)",
 "checked": "2026-11-22",
 "handover": [],
 "n": "Great Plains State Park",
 "official": {
  "acres": 400.0,
  "as": "400 acres",
  "clean": false,
  "line": "n foot and take in the scenery at a slower pace. Whether biking or on foot, visitors will have access to over 400 acres of park land. Rock climbing in granite boulder fields is also a favorite activity at Great Plains State Park.",
  "read": "2026-11-22",
  "sent": "Whether biking or on foot, visitors will have access to over 400 acres of park land.",
  "url": "https://www.travelok.com/state-parks/great-plains-state-park",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 2697,
  "manager": "",
  "pieces": [
   [
    237679,
    "Great Plains State Park",
    2357,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 574,
 "same_agency": false,
 "score": 7,
 "t": "State Park",
 "verdict": "unsure"
}
```

## US-4579 Santa Fe National Historic Trail
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Santa Fe National Historic Trail",
 "note": "whole park compared (POTA lists it in 0 states: {})",
 "official": null,
 "ours": {
  "acres": 0,
  "acres_by_state": {},
  "manager": "",
  "pieces": [],
  "pin": "inside",
  "src": "",
  "states": [
   "US-CO",
   "US-NM",
   "US-OK",
   "US-MO",
   "US-KS"
  ],
  "unknown_pieces": 1,
  "whole_park": true
 },
 "owner_now": null,
 "pct": null,
 "score": 4,
 "t": "National Historic Trail",
 "verdict": "ours unknown"
}
```

## US-10203 Quartz Mountain State Park
```json
{
 "cause": "agency smaller: our outline may hold water, a lease or a neighbour tract",
 "checked": "2026-11-22",
 "handover": [
  {
   "date_hint": "2020",
   "kind": "transfer",
   "line": "al lodge in 1995. It was rebuilt and reopened in 2001. Shortly after lodge completion, the park was transferred to the Oklahoma Regents for Higher Education, who ran it for nearly two decades before returning management to Oklahoma State Parks in 2020. Upon resuming control, parks fully renovated th",
   "owner_now": "Oklahoma Regents for Higher Education",
   "src": "https://www.travelok.com/state-parks/quartz-mountain-state-park",
   "why": "the park's page (data/parkinfo)"
  }
 ],
 "n": "Quartz Mountain State Park",
 "official": {
  "acres": 400.0,
  "as": "400 acres",
  "clean": false,
  "line": "Seasonal ATV riding area is available April through October in the North Shore area, featuring approximately 400 acres of land and two miles of trails. Read More Activities Rock Climbing/Rappelling Watchable Wildlife Hiking Fish",
  "read": "2026-11-22",
  "sent": "Seasonal ATV riding area is available April through October in the North Shore area, featuring approximately 400 acres of land and two miles of trails.",
  "url": "https://www.travelok.com/state-parks/quartz-mountain-state-park",
  "why": "total-looking"
 },
 "ours": {
  "acres": 9025,
  "manager": "",
  "pieces": [
   [
    237697,
    "Quartz Mountain State Resort Park",
    9025,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": "Oklahoma Regents for Higher Education",
 "pct": 2156,
 "same_agency": false,
 "score": 5,
 "t": "State Park",
 "verdict": "off"
}
```

## US-2771 Beavers Bend Resort State Park
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-11-22",
 "handover": [],
 "n": "Beavers Bend Resort State Park",
 "official": null,
 "ours": {
  "acres": 5878,
  "manager": "",
  "pieces": [
   [
    237665,
    "Beavers Bend State Resort Park",
    1870,
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
 "verdict": "unsure"
}
```

## US-7684 Blue River State Fishing Lake
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Blue River State Fishing Lake",
 "official": {
  "acres": 3367.0,
  "as": "3,367 acres",
  "clean": false,
  "line": "se issued by the Wildlife Department. For complete conservation passport license info go here . Blue River is 3,367 acres of Postoak and Blackjack timber and scattered openings. Located 8 miles northeast of Tishomingo. Follow us on",
  "read": "2026-11-22",
  "sent": "Blue River is 3,367 acres of Postoak and Blackjack timber and scattered openings.",
  "url": "https://www.wildlifedepartment.com/fishing/wheretofish/southeast/blue-river",
  "why": "total-looking"
 },
 "ours": {
  "acres": 3341,
  "dissolved": {
   "after": 3341,
   "before": 6682,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 6682 -> 3341 acres",
  "pieces": [
   [
    "sgokc10",
    "Blue River",
    3341,
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
 "t": "State Fishing Lake",
 "verdict": "agree"
}
```

## US-0489 Salt Plains National Wildlife Refuge
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-22",
 "handover": [],
 "n": "Salt Plains National Wildlife Refuge",
 "official": {
  "acres": 32197.0,
  "as": "32,197 acres",
  "clean": true,
  "line": "ore About Visiting Location and Contact Information About Us Salt Plains National Wildlife Refuge encompasses 32,197 acres in north-central Oklahoma. The refuge is composed of mixed-grass prairie, rolling sand hills, forested ripari",
  "read": "2026-11-22",
  "sent": "Salt Plains National Wildlife Refuge encompasses 32,197 acres in north-central Oklahoma.",
  "url": "https://www.fws.gov/refuge/salt_plains/",
  "why": "clean total"
 },
 "ours": {
  "acres": 21182,
  "dissolved": {
   "after": 21182,
   "before": 42364,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 42364 -> 21182 acres",
  "pieces": [
   [
    4291,
    "Salt Plains National Wildlife Refuge",
    21182,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 34,
 "same_agency": false,
 "score": 5,
 "t": "National Wildlife Refuge",
 "verdict": "off"
}
```
