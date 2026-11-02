# park truth checker: US-VA random sample of 12 (2026-11-01; seed = date + area, same rows for everyone)

Source file: `data/truth/US-VA.json`

## US-0016 Colonial National Historical Park
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Colonial National Historical Park",
 "official": null,
 "ours": {
  "acres": 10244,
  "dissolved": {
   "after": 18125,
   "before": 19530,
   "copies": 0,
   "families": {
    "padus": 7881,
    "sgvae": 10244
   },
   "family_fold": 7881,
   "family_used": "sgvae",
   "parts": 10,
   "records": 18,
   "tracts": 8
  },
  "family_fold": "layers {'padus': 7881, 'sgvae': 10244}: one land in 2 layers, the sgvae copy used (7,881 ac of copies not added)",
  "manager": "",
  "note": "18 joined records = 8 tracts: 0 copies of a tract (same acres, another layer) and 10 fee tracts under a designation record folded; summed 19530 -> 18125 acres",
  "pieces": [
   [
    "sgvae490681",
    "Colonial National Historical Park",
    7296,
    "name"
   ],
   [
    "sgvae490554",
    "Colonial National Historical Park",
    1485,
    "name"
   ],
   [
    "sgvae490569",
    "Colonial National Historical Park",
    1389,
    "name"
   ],
   [
    "sgvae490553",
    "Colonial National Historical Park",
    68,
    "name"
   ],
   [
    "sgvae490572",
    "Colonial National Historical Park",
    4,
    "name"
   ],
   [
    "sgvae490571",
    "Colonial National Historical Park",
    1,
    "name"
   ],
   [
    "sgvae490578",
    "Colonial National Historical Park",
    1,
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
 "t": "National Historical Park",
 "verdict": "no size on page"
}
```

## US-11672 Harrison Lake National Fish Hatchery
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Harrison Lake National Fish Hatchery",
 "official": {
  "acres": 444.0,
  "as": "444 acre",
  "clean": true,
  "line": "sion 11110 Kimages Road Charles City, VA 23030-2844 Plan Your Visit Harrison Lake National Fish Hatchery is a 444-acre facility of the U.S. Fish and Wildlife Service located in the quiet rural setting of Virginia&#x27;s historic",
  "read": "2026-10-29",
  "sent": "Harrison Lake National Fish Hatchery is a 444-acre facility of the U.S.",
  "url": "https://www.fws.gov/fish-hatchery/harrison-lake",
  "why": "clean total"
 },
 "ours": {
  "acres": 400,
  "dissolved": {
   "after": 733,
   "before": 1129,
   "copies": 1,
   "families": {
    "padus": 400,
    "sgvae": 333
   },
   "family_fold": 333,
   "family_used": "padus",
   "parts": 0,
   "records": 7,
   "tracts": 6
  },
  "family_fold": "layers {'padus': 400, 'sgvae': 333}: one land in 2 layers, the padus copy used (333 ac of copies not added)",
  "manager": "",
  "note": "7 joined records = 6 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1129 -> 733 acres",
  "pieces": [
   [
    3926,
    "Harrison Lake National Fish Hatchery",
    400,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 10,
 "same_agency": false,
 "score": 8,
 "t": "National Fish Hatchery",
 "verdict": "agree"
}
```

## US-1324 Westmoreland State Park
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Westmoreland State Park",
 "official": {
  "acres": 1321.0,
  "as": "1,321 acres",
  "clean": false,
  "line": "half hours; Tidewater/Norfolk/Virginia Beach, two and a half hours; Roanoke, five and a half hours Park Size 1,321 acres. Share this page Follow us Cabins, camping OVERNIGHT FACILITIES Cabins, camping, group camp, camping cabins.",
  "read": "2026-10-29",
  "sent": "1,321 acres.",
  "url": "https://www.dcr.virginia.gov/state-parks/westmoreland",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 1328,
  "dissolved": {
   "after": 1328,
   "before": 5290,
   "copies": 3,
   "parts": 0,
   "records": 4,
   "tracts": 1
  },
  "manager": "",
  "note": "4 joined records = 1 tracts: 3 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 5290 -> 1328 acres",
  "pieces": [
   [
    270687,
    "Westmoreland State Park",
    1328,
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
 "t": "State Park",
 "verdict": "agree"
}
```

## US-9899 Fort Hunt National Historical Site
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Fort Hunt National Historical Site",
 "official": null,
 "ours": {
  "acres": 19,
  "manager": "",
  "pieces": [
   [
    "sgvae488032",
    "Fort Hunt",
    19,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 4,
 "t": "National Historical Site",
 "verdict": "no size on page"
}
```

## US-0670 George Washington Memorial Parkway
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "George Washington Memorial Parkway",
 "note": "whole park compared (POTA lists it in 3 states: {'US-DC': 135, 'US-MD': 2379, 'US-VA': 6253})",
 "official": null,
 "ours": {
  "acres": 8767,
  "acres_by_state": {
   "US-DC": 135,
   "US-MD": 2379,
   "US-VA": 6253
  },
  "manager": "",
  "pieces": [
   [
    3549,
    "George Washington Memorial Parkway",
    3477,
    "name"
   ],
   [
    271111,
    "George Washington Memorial Parkway",
    2776,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "states": [
   "US-DC",
   "US-MD",
   "US-VA"
  ],
  "unknown_pieces": 1,
  "whole_park": true
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "Memorial Parkway",
 "verdict": "no size on page"
}
```

## US-5509 Chilton Woods State Forest
```json
{
 "checked": "2026-10-29",
 "handover": [
  {
   "date_hint": null,
   "kind": "transfer",
   "line": "ed to release her interest in the property in consideration of her late husband&#x2019;s wishes and deeded the property to the Virginia Department of Forestry . This gift from the Chilton family became the 15th state forest property and the only one in the No",
   "owner_now": "Virginia Department of Forestry",
   "src": "https://dof.virginia.gov/education-and-recreation/state-forests/virginia-state-forests/chilton-woods-state-forest/",
   "why": "the park's page (data/parkinfo)"
  }
 ],
 "n": "Chilton Woods State Forest",
 "official": {
  "acres": 397.0,
  "as": "397 acre",
  "clean": true,
  "line": "zzleloader seasons. Dogs will not be allowed to chase bear or deer on the forest. Overview Chilton Woods is a 397-acre state forest in Lancaster County. Management focuses on demonstration of sustainable forest management practi",
  "read": "2026-10-29",
  "sent": "Chilton Woods is a 397-acre state forest in Lancaster County.",
  "url": "https://dof.virginia.gov/education-and-recreation/state-forests/virginia-state-forests/chilton-woods-state-forest/",
  "why": "clean total"
 },
 "ours": {
  "acres": 399,
  "dissolved": {
   "after": 399,
   "before": 1596,
   "copies": 3,
   "parts": 0,
   "records": 4,
   "tracts": 1
  },
  "manager": "",
  "note": "4 joined records = 1 tracts: 3 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1596 -> 399 acres",
  "pieces": [
   [
    57426,
    "Chilton Woods State Forest",
    399,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": "Virginia Department of Forestry",
 "pct": 1,
 "same_agency": false,
 "score": 7,
 "t": "State Forest",
 "verdict": "agree"
}
```

## US-9902 Colonial National Parkway
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-10-29",
 "handover": [],
 "n": "Colonial National Parkway",
 "official": null,
 "ours": {
  "acres": 7881,
  "manager": "",
  "pieces": [
   [
    3195,
    "Colonial National Historical Park",
    7881,
    "reviewed-approx"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 5,
 "t": "National Parkway",
 "verdict": "unsure"
}
```

## US-7636 Widewater State Park
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Widewater State Park",
 "official": {
  "acres": 1089.0,
  "as": "1,089 acres",
  "clean": false,
  "line": "one and a half hours; Tidewater-Norfolk-Virginia Beach, two and a half hours; Roanoke, four hours. Park Size 1,089 acres. Share this page Follow us Cabins, camping OVERNIGHT FACILITIES Widewater has no cabins or full-service campi",
  "read": "2026-10-29",
  "sent": "1,089 acres.",
  "url": "https://www.dcr.virginia.gov/state-parks/widewater",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 1089,
  "dissolved": {
   "after": 2258,
   "before": 5517,
   "copies": 3,
   "families": {
    "padus": 1042,
    "sgvad": 1089,
    "sgvae": 127
   },
   "family_fold": 1169,
   "family_used": "sgvad",
   "parts": 0,
   "records": 6,
   "tracts": 3
  },
  "family_fold": "layers {'sgvad': 1089, 'padus': 1042, 'sgvae': 127}: one land in 3 layers, the sgvad copy used (1,169 ac of copies not added)",
  "manager": "",
  "note": "6 joined records = 3 tracts: 3 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 5517 -> 2258 acres",
  "pieces": [
   [
    "sgvad180",
    "Widewater State Park",
    1089,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 0,
 "same_agency": false,
 "score": 7,
 "t": "State Park",
 "verdict": "agree"
}
```

## US-0935 George Washington Birthplace National Monument
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "George Washington Birthplace National Monument",
 "official": {
  "acres": 551.0,
  "as": "551 acres",
  "clean": false,
  "line": "ia George Washington Birthplace National Monument is located in the Northern Neck of Virginia. It encompasses 551 acres of land where seven generations of the Washington family lived and where George Washington was born in 1732.",
  "read": "2026-10-29",
  "sent": "It encompasses 551 acres of land where seven generations of the Washington family lived and where George Washington was born in 1732.",
  "url": "https://www.nps.gov/gewa/index.htm",
  "why": "total-looking"
 },
 "ours": {
  "acres": 556,
  "family_fold": "layers {'padus': 556, 'sgvae': 475}: one land in 2 layers, the padus copy used (475 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    3376,
    "George Washington Birthplace National Monument",
    556,
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
 "t": "National Monument",
 "verdict": "agree"
}
```

## US-5518 Moore's Creek State Forest
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-10-29",
 "handover": [],
 "n": "Moore's Creek State Forest",
 "official": null,
 "ours": {
  "acres": 2354,
  "dissolved": {
   "after": 2354,
   "before": 9403,
   "copies": 3,
   "parts": 0,
   "records": 4,
   "tracts": 1
  },
  "manager": "",
  "note": "4 joined records = 1 tracts: 3 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 9403 -> 2354 acres",
  "pieces": [
   [
    270425,
    "Moore's Creek State Forest",
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
 "score": 7,
 "t": "State Forest",
 "verdict": "unsure"
}
```

## US-0563 Elizabeth Hartwell Mason Neck National Wildlife Refuge
```json
{
 "cause": "agency smaller: our outline may hold water, a lease or a neighbour tract",
 "checked": "2026-10-29",
 "handover": [
  {
   "date_hint": null,
   "kind": "managed by",
   "line": "ational wildlife refuge A national wildlife refuge is typically a contiguous area of land and water managed by the U.S. Fish and Wildlife Service for the conservation and, where appropriate, restoration of fish, wildlife and plant resources and their habitats for th",
   "owner_now": "U.S",
   "src": "https://www.fws.gov/refuge/elizabeth-hartwell-mason-neck/about-us",
   "why": "about / history page of the park's site"
  }
 ],
 "n": "Elizabeth Hartwell Mason Neck National Wildlife Refuge",
 "official": {
  "acres": 207.0,
  "as": "207 acre",
  "clean": false,
  "line": "ively remote area of upland forests and freshwater marshes that extend into the Potomac River. Great Marsh, a 207-acre tidal freshwater marsh, is a valuable feature of the refuge, and is home to one of Virginia’s largest great b",
  "read": "2026-10-29",
  "sent": "Great Marsh, a 207-acre tidal freshwater marsh, is a valuable feature of the refuge, and is home to one of Virginia’s largest great blue heron breeding colonies.",
  "url": "https://www.fws.gov/refuge/elizabeth-hartwell-mason-neck/about-us",
  "why": "total-looking"
 },
 "ours": {
  "acres": 1468,
  "dissolved": {
   "after": 2633,
   "before": 5418,
   "copies": 1,
   "families": {
    "padus": 1468,
    "sgvae": 1165
   },
   "family_fold": 1165,
   "family_used": "padus",
   "parts": 24,
   "records": 35,
   "tracts": 10
  },
  "family_fold": "layers {'padus': 1468, 'sgvae': 1165}: one land in 2 layers, the padus copy used (1,165 ac of copies not added)",
  "manager": "",
  "note": "35 joined records = 10 tracts: 1 copies of a tract (same acres, another layer) and 24 fee tracts under a designation record folded; summed 5418 -> 2633 acres",
  "pieces": [
   [
    3808,
    "Elizabeth Hartwell Mason Neck National Wildlife Refuge",
    1468,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 4
 },
 "owner_now": "U.S",
 "pct": 609,
 "same_agency": false,
 "score": 6,
 "t": "National Wildlife Refuge",
 "verdict": "off"
}
```

## US-1299 First Landing State Park
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "First Landing State Park",
 "official": {
  "acres": 2888.0,
  "as": "2,888 acres",
  "clean": false,
  "line": "rfolk/Virginia Beach, 20-30 minutes (this facility is in the area); Roanoke, five and a half hours. Park Size 2,888 acres; 1.5 miles of Chesapeake Bay beach Share this page Follow us Cabins, camping OVERNIGHT FACILITIES For informa",
  "read": "2026-10-29",
  "sent": "2,888 acres;",
  "url": "https://www.dcr.virginia.gov/state-parks/first-landing",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 2916,
  "dissolved": {
   "after": 5632,
   "before": 11264,
   "copies": 2,
   "families": {
    "padus": 2916,
    "sgvad": 2716
   },
   "family_fold": 2716,
   "family_used": "padus",
   "parts": 0,
   "records": 4,
   "tracts": 2
  },
  "family_fold": "layers {'padus': 2916, 'sgvad': 2716}: one land in 2 layers, the padus copy used (2,716 ac of copies not added)",
  "manager": "",
  "note": "4 joined records = 2 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 11264 -> 5632 acres",
  "pieces": [
   [
    54565,
    "First Landing State Park",
    2916,
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
 "t": "State Park",
 "verdict": "agree"
}
```
