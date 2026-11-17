# park truth checker: US-CT random sample of 12 (2026-11-17; seed = date + area, same rows for everyone)

Source file: `data/truth/US-CT.json`

## US-1725 Trimountain State Park
```json
{
 "checked": "2026-11-17",
 "handover": [],
 "n": "Trimountain State Park",
 "official": {
  "acres": 150.0,
  "as": "150 acres",
  "clean": false,
  "line": "te 156, right onto Ferry Road. Follow to the end. Fee: There is no fee at this park. George Waldo State Park (150 acres) - Southbury Activities: Fishing, Hiking, Horseback Riding, Hunting, Mountain Biking, Additional Recreational",
  "read": "2026-11-17",
  "sent": "George Waldo State Park (150 acres) - Southbury",
  "url": "https://portal.ct.gov/DEEP/State-Parks/Locate-Park-Forest/Other-State-Parks-and-Forests",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 165,
  "dissolved": {
   "after": 153,
   "before": 305,
   "copies": 1,
   "key_union": 165,
   "parts": 0,
   "records": 2,
   "summed": 153,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 305 -> 153 acres",
  "pieces": [
   [
    52724,
    "Trimountain State Park Scenic Reserve",
    153,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 2
 },
 "owner_now": null,
 "pct": 10,
 "same_agency": false,
 "score": 7,
 "t": "State Park",
 "verdict": "agree"
}
```

## US-10079 Pootatuck State Forest
```json
{
 "checked": "2026-11-17",
 "handover": [],
 "n": "Pootatuck State Forest",
 "official": null,
 "ours": {
  "acres": 1099,
  "dissolved": {
   "after": 1099,
   "before": 3186,
   "copies": 1,
   "parts": 4,
   "records": 7,
   "tracts": 2
  },
  "manager": "",
  "note": "7 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 4 fee tracts under a designation record folded; summed 3186 -> 1099 acres",
  "pieces": [
   [
    "sgcta4098",
    "Pootatuck State Forest",
    1052,
    "name"
   ],
   [
    8807,
    "Pootatuck State Forest",
    47,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 18
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "State Forest",
 "verdict": "no size on page"
}
```

## US-0329 Silvio O Conte National Wildlife Refuge
```json
{
 "cause": "agency smaller: our outline may hold water, a lease or a neighbour tract",
 "checked": "2026-11-17",
 "handover": [],
 "n": "Silvio O Conte National Wildlife Refuge",
 "note": "whole park compared (POTA lists it in 4 states: {'US-VT': 34983, 'US-MA': 7893, 'US-CT': 7893, 'US-NH': 7893})",
 "official": {
  "acres": 26600.0,
  "as": "26,600 acres",
  "clean": false,
  "line": "ntact station is located in Brunswick (about 10 miles east of Island Pond). Refuge lands consist of more than 26,600 acres of conifer and deciduous forest interspersed with forested wetlands, peatlands and shrub swamps, and contain",
  "read": "2026-11-17",
  "sent": "Refuge lands consist of more than 26,600 acres of conifer and deciduous forest interspersed with forested wetlands, peatlands and shrub swamps, and contain three of the four tributaries of the Nulhegan River.",
  "url": "https://www.fws.gov/refuge/silvio-o-conte",
  "why": "total-looking"
 },
 "ours": {
  "acres": 58662,
  "acres_by_state": {
   "US-CT": 7893,
   "US-MA": 7893,
   "US-NH": 7893,
   "US-VT": 34983
  },
  "manager": "",
  "pieces": [
   [
    5300,
    "Silvio O. Conte National Fish And Wildlife Refuge",
    7893,
    "reviewed"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "states": [
   "US-VT",
   "US-MA",
   "US-CT",
   "US-NH"
  ],
  "unknown_pieces": 0,
  "whole_park": true
 },
 "owner_now": null,
 "pct": 121,
 "same_agency": false,
 "score": 5,
 "t": "National Wildlife Refuge",
 "verdict": "off"
}
```

## US-10952 Paugussett State Forest
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-11-17",
 "handover": [],
 "n": "Paugussett State Forest",
 "official": null,
 "ours": {
  "acres": 2291,
  "dissolved": {
   "after": 3261,
   "before": 6222,
   "copies": 0,
   "families": {
    "padus": 1134,
    "sgcta": 2127
   },
   "family_fold": 1134,
   "family_used": "sgcta",
   "key_union": 2291,
   "parts": 7,
   "records": 13,
   "summed": 2127,
   "tracts": 6
  },
  "family_fold": "layers {'sgcta': 2127, 'padus': 1134}: one land in 2 layers, the sgcta copy used (1,134 ac of copies not added)",
  "manager": "",
  "note": "13 joined records = 6 tracts: 0 copies of a tract (same acres, another layer) and 7 fee tracts under a designation record folded; summed 6222 -> 3261 acres",
  "pieces": [
   [
    "sgcta4096",
    "Paugussett State Forest",
    2127,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 10
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "State Forest",
 "verdict": "unsure"
}
```

## US-6869 Peoples State Forest
```json
{
 "checked": "2026-11-17",
 "handover": [],
 "n": "Peoples State Forest",
 "official": null,
 "ours": {
  "acres": 3108,
  "dissolved": {
   "after": 3108,
   "before": 9314,
   "copies": 2,
   "parts": 0,
   "records": 3,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 9314 -> 3108 acres",
  "pieces": [
   [
    "sgctc12",
    "Peoples State Forest",
    3108,
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
 "t": "State Forest",
 "verdict": "no size on page"
}
```

## US-1661 Dennis Hill State Park
```json
{
 "checked": "2026-11-17",
 "handover": [],
 "n": "Dennis Hill State Park",
 "official": {
  "acres": 240.0,
  "as": "240 acre",
  "clean": false,
  "line": "e all the way to Haystack Mountain, Mount Greylock, the Green Mountains, and even parts of New Hampshire. The 240-acre estate of Dennis Hill State Park was gifted to the State of Connecticut in 1935 by Dr. Frederic Shepard Denni",
  "read": "2026-11-17",
  "sent": "The 240-acre estate of Dennis Hill State Park was gifted to the State of Connecticut in 1935 by Dr.",
  "url": "https://portal.ct.gov/DEEP/State-Parks/Parks/Dennis-Hill-State-Park",
  "why": "total-looking"
 },
 "ours": {
  "acres": 242,
  "dissolved": {
   "after": 242,
   "before": 480,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 480 -> 242 acres",
  "pieces": [
   [
    52530,
    "Dennis Hill State Park",
    242,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 1,
 "same_agency": false,
 "score": 8,
 "t": "State Park",
 "verdict": "agree"
}
```

## US-6872 Salt Rock State Forest
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-11-17",
 "handover": [
  {
   "date_hint": null,
   "kind": "closed",
   "line": "(seasonal) Campground Map Know Before You Go Two pets allowed per site The swimming pools have been permanently closed Camping in Connecticut State Parks & Forests 56 RV/Tent Sites Daily Rates: 33 Standard Sites: $33 r",
   "owner_now": null,
   "src": "https://portal.ct.gov/DEEP/State-Parks/Campgrounds/Salt-Rock-State-Campground",
   "why": "the park's page (data/parkinfo)"
  }
 ],
 "n": "Salt Rock State Forest",
 "official": null,
 "ours": {
  "acres": 138,
  "family_fold": "layers {'sgcta': 93, 'padus': 138}: one land in 2 layers, the padus copy used (93 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    51815,
    "Salt Rock State Park",
    65,
    "reviewed"
   ],
   [
    51813,
    "Salt Rock State Park",
    43,
    "reviewed"
   ],
   [
    51814,
    "Salt Rock State Park",
    30,
    "reviewed"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "State Forest",
 "verdict": "unsure"
}
```

## US-1676 Hammonasset Beach State Beach
```json
{
 "checked": "2026-11-17",
 "handover": [],
 "n": "Hammonasset Beach State Beach",
 "official": null,
 "ours": {
  "acres": 992,
  "manager": "",
  "pieces": [
   [
    51787,
    "Hammonasset Beach State Park",
    5,
    "name"
   ],
   [
    51786,
    "Hammonasset Beach State Park",
    4,
    "name"
   ],
   [
    51785,
    "Hammonasset Beach State Park",
    3,
    "name"
   ],
   [
    51788,
    "Hammonasset Beach State Park",
    3,
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
 "t": "State Beach",
 "verdict": "no size on page"
}
```

## US-7538 Naugatuck State Forest
```json
{
 "cause": "a number 5 parks share from the same sentence (401 ac): an agency total, not this park",
 "checked": "2026-11-17",
 "handover": [],
 "n": "Naugatuck State Forest",
 "official": null,
 "ours": {
  "acres": 5120,
  "dissolved": {
   "after": 6876,
   "before": 11981,
   "copies": 0,
   "families": {
    "padus": 1756,
    "sgcta": 5120
   },
   "family_fold": 1756,
   "family_used": "sgcta",
   "parts": 6,
   "records": 13,
   "tracts": 7
  },
  "family_fold": "layers {'sgcta': 5120, 'padus': 1756}: one land in 2 layers, the sgcta copy used (1,756 ac of copies not added)",
  "manager": "",
  "note": "13 joined records = 7 tracts: 0 copies of a tract (same acres, another layer) and 6 fee tracts under a designation record folded; summed 11981 -> 6876 acres",
  "pieces": [
   [
    "sgcta4089",
    "Naugatuck State Forest",
    5120,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 16
 },
 "owner_now": null,
 "pct": null,
 "same_agency": false,
 "score": 7,
 "t": "State Forest",
 "verdict": "unsure"
}
```

## US-1714 Selden Neck State Park
```json
{
 "checked": "2026-11-17",
 "handover": [],
 "n": "Selden Neck State Park",
 "official": {
  "acres": 607.0,
  "as": "607 acre",
  "clean": false,
  "line": "own as the largest island in the Connecticut River. Except for the tidal marshes, the roadless, uninhabited, 607-acre island is completely blanketed with lush woodland vegetation. The island tops out at nearly 230 feet in eleva",
  "read": "2026-11-17",
  "sent": "Except for the tidal marshes, the roadless, uninhabited, 607-acre island is completely blanketed with lush woodland vegetation.",
  "url": "https://portal.ct.gov/DEEP/State-Parks/Parks/Selden-Neck-State-Park",
  "why": "total-looking"
 },
 "ours": {
  "acres": 566,
  "dissolved": {
   "after": 566,
   "before": 1686,
   "copies": 2,
   "parts": 0,
   "records": 4,
   "tracts": 2
  },
  "manager": "",
  "note": "4 joined records = 2 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1686 -> 566 acres",
  "pieces": [
   [
    "sgcta4154",
    "Selden Neck State Park",
    563,
    "name"
   ],
   [
    51818,
    "Selden Neck State Park",
    3,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 7,
 "same_agency": false,
 "score": 8,
 "t": "State Park",
 "verdict": "agree"
}
```

## US-1692 Macedonia Brook State Park
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-17",
 "handover": [],
 "n": "Macedonia Brook State Park",
 "official": {
  "acres": 2300.0,
  "as": "2,300 acre",
  "clean": false,
  "line": "content Park Finder Park Maps Book Campground Book Picnic Shelter Macedonia Brook State Park Kent, CT Head to 2,300-acre Macedonia Brook State Park for big hikes, big views, and big fish. And with camping available, keep the adven",
  "read": "2026-11-17",
  "sent": "Head to 2,300-acre Macedonia Brook State Park for big hikes, big views, and big fish.",
  "url": "https://portal.ct.gov/DEEP/State-Parks/Parks/Macedonia-Brook-State-Park",
  "why": "total-looking"
 },
 "ours": {
  "acres": 1829,
  "dissolved": {
   "after": 2708,
   "before": 3576,
   "copies": 0,
   "families": {
    "padus": 879,
    "sgcta": 1829
   },
   "family_fold": 879,
   "family_used": "sgcta",
   "parts": 2,
   "records": 6,
   "tracts": 4
  },
  "family_fold": "layers {'sgcta': 1829, 'padus': 879}: one land in 2 layers, the sgcta copy used (879 ac of copies not added)",
  "manager": "",
  "note": "6 joined records = 4 tracts: 0 copies of a tract (same acres, another layer) and 2 fee tracts under a designation record folded; summed 3576 -> 2708 acres",
  "pieces": [
   [
    "sgcta4139",
    "Macedonia Brook State Park",
    1829,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 11
 },
 "owner_now": null,
 "pct": 20,
 "same_agency": false,
 "score": 6,
 "t": "State Park",
 "verdict": "off"
}
```

## US-1723 Sunrise State Park
```json
{
 "checked": "2026-11-17",
 "handover": [],
 "n": "Sunrise State Park",
 "official": {
  "acres": 146.0,
  "as": "146 acre",
  "clean": false,
  "line": "s — first Ted Hilton’s Hideway, then the Frank Davis Resort, and most recently the Sunrise Resort. Today, the 146-acre park is an idyllic spot to set up a picnic, kayak on the Salmon River, watch for bald eagles fly fish, or eve",
  "read": "2026-11-17",
  "sent": "Today, the 146-acre park is an idyllic spot to set up a picnic, kayak on the Salmon River, watch for bald eagles fly fish, or even cross-country ski.",
  "url": "https://portal.ct.gov/DEEP/State-Parks/Parks/Sunrise-State-Park",
  "why": "part (a lake, a purchase, a campground…)"
 },
 "ours": {
  "acres": 145,
  "manager": "",
  "pieces": [
   [
    "sgcta4178",
    "Sunrise State Park",
    145,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 1,
 "same_agency": false,
 "score": 8,
 "t": "State Park",
 "verdict": "agree"
}
```
