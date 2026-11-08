# park truth checker: US-GA random sample of 12 (2026-11-08; seed = date + area, same rows for everyone)

Source file: `data/truth/US-GA.json`

## US-2206 Vogel State Park
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-08",
 "handover": [],
 "n": "Vogel State Park",
 "official": {
  "acres": 242.0,
  "as": "242 Acres",
  "clean": false,
  "line": "before European settlement. Keep Reading Vogel State Park History . Reservations, Accommodations & Facilities 242 Acres 22 Acre Lake 34 Cottages 90 Tent, Trailer & RV Campsites 18 Walk-In Campsites 1 Pioneer Campground (Before ma",
  "read": "2026-11-08",
  "sent": "242 Acres",
  "url": "https://gastateparks.org/Vogel",
  "why": "total-looking"
 },
 "ours": {
  "acres": 191,
  "dissolved": {
   "after": 266,
   "before": 532,
   "copies": 1,
   "key_union": 191,
   "parts": 0,
   "records": 2,
   "summed": 266,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 532 -> 266 acres",
  "pieces": [
   [
    195164,
    "Vogel State Park",
    266,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 21,
 "same_agency": false,
 "score": 5,
 "t": "State Park",
 "verdict": "off"
}
```

## US-7907 Clarks Hill Wildlife Management Area
```json
{
 "cause": "agency smaller: our outline may hold water, a lease or a neighbour tract",
 "checked": "2026-11-08",
 "handover": [
  {
   "date_hint": null,
   "kind": "managed by",
   "line": "nagement Area – East is located in McDuffie, Wilkes and Lincoln counties. This 10,224-acre property is owned by the U.S. Army Corps of Engineers and managed by the Georgia DNR-Wildlife Resources Division. It offers hunting opportunities for deer, turkey, smal",
   "owner_now": "U.S",
   "src": "https://georgiawildlife.com/clarks-hill-east",
   "why": "the park's page (data/parkinfo)"
  }
 ],
 "n": "Clarks Hill Wildlife Management Area",
 "official": {
  "acres": 10224.0,
  "as": "10,224 acre",
  "clean": false,
  "line": "ll-East Clarks Hill Wildlife Management Area – East is located in McDuffie, Wilkes and Lincoln counties. This 10,224-acre property is owned by the U.S. Army Corps of Engineers and managed by the Georgia DNR-Wildlife Resources Divis",
  "read": "2026-11-08",
  "sent": "This 10,224-acre property is owned by the U.S.",
  "url": "https://georgiawildlife.com/clarks-hill-east",
  "why": "total-looking"
 },
 "ours": {
  "acres": 20313,
  "dissolved": {
   "after": 35104,
   "before": 52583,
   "copies": 1,
   "families": {
    "padus": 17638,
    "sggac": 17466
   },
   "family_fold": 17466,
   "family_used": "padus",
   "key_union": 20313,
   "parts": 0,
   "records": 4,
   "summed": 17638,
   "tracts": 3
  },
  "family_fold": "layers {'padus': 17638, 'sggac': 17466}: one land in 2 layers, the padus copy used (17,466 ac of copies not added)",
  "manager": "",
  "note": "4 joined records = 3 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 52583 -> 35104 acres",
  "pieces": [
   [
    194358,
    "Clarks Hill Wildlife Management Area",
    17638,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": "U.S",
 "pct": 99,
 "same_agency": false,
 "score": 6,
 "t": "Wildlife Management Area",
 "verdict": "off"
}
```

## US-2198 Skidaway Island State Park
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 588 Acres, no total words near it)",
 "checked": "2026-11-08",
 "handover": [],
 "n": "Skidaway Island State Park",
 "official": {
  "acres": 588.0,
  "as": "588 Acres",
  "clean": false,
  "line": "Pets are not allowed in camper cabins but are allowed in campsites. Reservations, Accommodations & Facilities 588 Acres 3 Camper Cabins 87 Tent, Trailer & RV Campsites 3 Yurts 3 Pioneer Campgrounds (Before making reservations, ca",
  "read": "2026-11-08",
  "sent": "588 Acres",
  "url": "https://gastateparks.org/SkidawayIsland",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 419,
  "dissolved": {
   "after": 597,
   "before": 1194,
   "copies": 1,
   "key_union": 419,
   "parts": 0,
   "records": 2,
   "summed": 597,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1194 -> 597 acres",
  "pieces": [
   [
    195157,
    "Skidaway Island State Park",
    597,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 29,
 "same_agency": false,
 "score": 7,
 "t": "State Park",
 "verdict": "unsure"
}
```

## US-7457 Chief Vann House State Historic Site
```json
{
 "cause": "our union: one of our pieces alone matches the agency (double count?)",
 "checked": "2026-11-08",
 "handover": [],
 "n": "Chief Vann House State Historic Site",
 "official": {
  "acres": 137.0,
  "as": "137 Acres",
  "clean": false,
  "line": "es beautiful hand carvings, a remarkable “floating” staircase, a 12-foot mantle and fine antiques. Facilities 137 Acres Visitor Center Gift Shop 12 Picnic Tables Bus Parking 360° Tour Things To Do & See ½ Mile Nature Trail one-wa",
  "read": "2026-11-08",
  "sent": "137 Acres",
  "url": "https://gastateparks.org/ChiefVannHouse",
  "why": "total-looking"
 },
 "ours": {
  "acres": 106,
  "manager": "",
  "pieces": [
   [
    195095,
    "Chief Vann House Historic Site",
    122,
    "name"
   ],
   [
    256204,
    "Chief Vann House Historic Site",
    86,
    "name"
   ],
   [
    256203,
    "Chief Vann House Historic Site",
    22,
    "name"
   ],
   [
    194914,
    "Chief Vann House Historic Site",
    10,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 23,
 "same_agency": false,
 "score": 5,
 "t": "State Historic Site",
 "verdict": "off"
}
```

## US-7140 Charlie Elliot Wildlife Management Area
```json
{
 "checked": "2026-11-08",
 "handover": [],
 "n": "Charlie Elliot Wildlife Management Area",
 "official": {
  "acres": 6700.0,
  "as": "6,700 acre",
  "clean": false,
  "line": "t of the reason we are there, whether with a camera, gun, fishing rod, or pack sack on.\" -Charlie Elliott The 6,700-acre Charlie Elliott Wildlife Center, managed by the Georgia Department of Natural Resources, offers a variety of",
  "read": "2026-11-08",
  "sent": "The 6,700-acre Charlie Elliott Wildlife Center, managed by the Georgia Department of Natural Resources, offers a variety of activities and programs.",
  "url": "https://georgiawildlife.com/charlie-elliott-wildlife-center",
  "why": "total-looking"
 },
 "ours": {
  "acres": 6273,
  "manager": "",
  "pieces": [
   [
    195024,
    "Charlie Elliott Wildlife Center Clybel Wildlife Management Area Marben Public Fishing Area",
    6273,
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
 "score": 7,
 "t": "Wildlife Management Area",
 "verdict": "agree"
}
```

## US-7142 Redlands Wildlife Management Area
```json
{
 "checked": "2026-11-08",
 "handover": [],
 "n": "Redlands Wildlife Management Area",
 "official": {
  "acres": 37500.0,
  "as": "37,500 acre",
  "clean": false,
  "line": "spread over Greene, Oglethorpe, Oconee and Morgan counties on property owned by the U.S. Forest Service. The 37,500-acre property offers hunting opportunities for deer, turkey, small game and dove. There is no hunting on Dyars Pas",
  "read": "2026-11-08",
  "sent": "The 37,500-acre property offers hunting opportunities for deer, turkey, small game and dove.",
  "url": "https://georgiawildlife.com/redlands-wma",
  "why": "total-looking"
 },
 "ours": {
  "acres": 34343,
  "dissolved": {
   "after": 64000,
   "before": 95240,
   "copies": 1,
   "families": {
    "padus": 32652,
    "sggaa": 31348
   },
   "family_fold": 31348,
   "family_used": "padus",
   "key_union": 34343,
   "parts": 0,
   "records": 3,
   "summed": 32652,
   "tracts": 2
  },
  "family_fold": "layers {'padus': 32652, 'sggaa': 31348}: one land in 2 layers, the padus copy used (31,348 ac of copies not added)",
  "manager": "",
  "note": "3 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 95240 -> 64000 acres",
  "pieces": [
   [
    194394,
    "Redlands Wildlife Management Area",
    32652,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 8,
 "same_agency": false,
 "score": 8,
 "t": "Wildlife Management Area",
 "verdict": "agree"
}
```

## US-3768 Phinizy Swamp Wildlife Management Area
```json
{
 "checked": "2026-11-08",
 "handover": [],
 "n": "Phinizy Swamp Wildlife Management Area",
 "official": {
  "acres": 1500.0,
  "as": "1,500 acre",
  "clean": false,
  "line": "ME Previous Next Phinizy Swamp WMA Phinizy Swamp Wildlife Management Area is located in Richmond County. This 1,500-acre property offers hunting opportunities for deer, turkey, small game and waterfowl. There are also five ponds t",
  "read": "2026-11-08",
  "sent": "This 1,500-acre property offers hunting opportunities for deer, turkey, small game and waterfowl.",
  "url": "https://georgiawildlife.com/phinizy-swamp-wma",
  "why": "total-looking"
 },
 "ours": {
  "acres": 1609,
  "dissolved": {
   "after": 1609,
   "before": 4814,
   "copies": 2,
   "parts": 0,
   "records": 3,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 4814 -> 1609 acres",
  "pieces": [
   [
    "sggaa24",
    "PHINIZY SWAMP WMA",
    1609,
    "reviewed"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 7,
 "same_agency": false,
 "score": 7,
 "t": "Wildlife Management Area",
 "verdict": "agree"
}
```

## US-9774 Lower Broad River Wildlife Management Area
```json
{
 "checked": "2026-11-08",
 "handover": [],
 "n": "Lower Broad River Wildlife Management Area",
 "official": {
  "acres": 1500.0,
  "as": "1,500 acre",
  "clean": false,
  "line": "River WMA Lower Broad River Wildlife Management Area is located in Wilkes, Elbert and Lincoln counties. This 1,500-acre property has hunting opportunities for deer, turkey, small game, and dove. No camping is allowed on the WMA.",
  "read": "2026-11-08",
  "sent": "This 1,500-acre property has hunting opportunities for deer, turkey, small game, and dove.",
  "url": "https://georgiawildlife.com/lower-broad-river-wma",
  "why": "total-looking"
 },
 "ours": {
  "acres": 1541,
  "dissolved": {
   "after": 3076,
   "before": 4412,
   "copies": 1,
   "families": {
    "padus": 1740,
    "sggaa": 1336
   },
   "family_fold": 1336,
   "family_used": "padus",
   "key_union": 1541,
   "parts": 0,
   "records": 3,
   "summed": 1740,
   "tracts": 2
  },
  "family_fold": "layers {'padus': 1740, 'sggaa': 1336}: one land in 2 layers, the padus copy used (1,336 ac of copies not added)",
  "manager": "",
  "note": "3 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 4412 -> 3076 acres",
  "pieces": [
   [
    194369,
    "Lower Broad River Wildlife Management Area",
    1740,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 3,
 "same_agency": false,
 "score": 8,
 "t": "Wildlife Management Area",
 "verdict": "agree"
}
```

## US-2188 Laura S. Walker State Park
```json
{
 "checked": "2026-11-08",
 "handover": [],
 "n": "Laura S. Walker State Park",
 "official": {
  "acres": 626.0,
  "as": "626 Acres",
  "clean": false,
  "line": "for their preservation. Read the story of Laura Singleton Walker . Reservations, Accommodations & Facilities 626 Acres 120 Acre Lake 6 Cottages 44 Tent, Trailer & RV Campsites 7 Picnic Shelters (Before making reservations, call",
  "read": "2026-11-08",
  "sent": "626 Acres",
  "url": "https://gastateparks.org/LauraSWalker",
  "why": "total-looking"
 },
 "ours": {
  "acres": 718,
  "family_fold": "layers {'sggab': 645, 'padus': 718}: one land in 2 layers, the padus copy used (645 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    195187,
    "Laura Walker State Park",
    395,
    "name"
   ],
   [
    195147,
    "Laura Walker State Park",
    323,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 15,
 "same_agency": false,
 "score": 8,
 "t": "State Park",
 "verdict": "agree"
}
```

## US-3743 Dawson Forest Wildlife Management Area
```json
{
 "checked": "2026-11-08",
 "handover": [],
 "n": "Dawson Forest Wildlife Management Area",
 "official": {
  "acres": 25500.0,
  "as": "25,500 acre",
  "clean": false,
  "line": "April 1, 2026 Dawson Forest WMA The Dawson Forest Wildlife Management Area is located in Dawson County. This 25,500-acre property offers hunting for deer, bear, turkey, small game, dove, and waterfowl. There are five sections (tra",
  "read": "2026-11-08",
  "sent": "This 25,500-acre property offers hunting for deer, bear, turkey, small game, dove, and waterfowl.",
  "url": "https://georgiawildlife.com/dawson-forest-wma",
  "why": "total-looking"
 },
 "ours": {
  "acres": 26849,
  "dissolved": {
   "after": 45018,
   "before": 87447,
   "copies": 5,
   "families": {
    "padus": 15586,
    "sggaa": 19119,
    "sggac": 10313
   },
   "family_fold": 25899,
   "family_used": "sggaa",
   "key_union": 26849,
   "parts": 0,
   "records": 12,
   "summed": 19119,
   "tracts": 7
  },
  "family_fold": "layers {'padus': 15586, 'sggaa': 19119, 'sggac': 10313}: one land in 3 layers, the sggaa copy used (25,899 ac of copies not added)",
  "manager": "",
  "note": "12 joined records = 7 tracts: 5 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 87447 -> 45018 acres",
  "pieces": [
   [
    "sggaa213",
    "DAWSON FOREST WMA",
    10224,
    "name"
   ],
   [
    "sggaa86",
    "DAWSON FOREST WMA",
    5470,
    "name"
   ],
   [
    "sggaa85",
    "DAWSON FOREST WMA",
    3425,
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
 "t": "Wildlife Management Area",
 "verdict": "agree"
}
```

## US-0263 Okefenokee National Wildlife Refuge
```json
{
 "checked": "2026-11-08",
 "handover": [],
 "n": "Okefenokee National Wildlife Refuge",
 "official": {
  "acres": 407000.0,
  "as": "407,000 acres",
  "clean": false,
  "line": "health. More than 600 plant species have been identified on refuge lands. Today, the refuge is approximately 407,000 acres and is the largest National Wildlife Refuge east of the Mississippi River. In addition, the refuge is a Wetla",
  "read": "2026-11-08",
  "sent": "Today, the refuge is approximately 407,000 acres and is the largest National Wildlife Refuge east of the Mississippi River.",
  "url": "https://www.fws.gov/refuge/okefenokee/about-us",
  "why": "total-looking"
 },
 "ours": {
  "acres": 404154,
  "dissolved": {
   "after": 404154,
   "before": 807682,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 807682 -> 404154 acres",
  "pieces": [
   [
    4183,
    "Okefenokee National Wildlife Refuge",
    404154,
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

## US-9793 Ball's Ferry Property Wildlife Management Area
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-08",
 "handover": [],
 "n": "Ball's Ferry Property Wildlife Management Area",
 "official": {
  "acres": 525.0,
  "as": "525 acres",
  "clean": false,
  "line": "T AND FISH FOR A LIFETIME Previous Next Ball's Ferry The Ball's Ferry property is located in Toomsboro and is 525 acres. This property offers hunting opportunities for deer, turkey, small game and waterfowl. There is a boat ramp",
  "read": "2026-11-08",
  "sent": "The Ball's Ferry property is located in Toomsboro and is 525 acres.",
  "url": "https://georgiawildlife.com/balls-ferry",
  "why": "total-looking"
 },
 "ours": {
  "acres": 313,
  "dissolved": {
   "after": 525,
   "before": 1567,
   "copies": 2,
   "key_union": 313,
   "parts": 0,
   "records": 3,
   "summed": 525,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1567 -> 525 acres",
  "pieces": [
   [
    195122,
    "Balls Ferry State Park",
    525,
    "reviewed-approx"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 40,
 "same_agency": false,
 "score": 4,
 "t": "Wildlife Management Area",
 "verdict": "off"
}
```
