# park truth checker: US-GA random sample of 12 (2026-11-15; seed = date + area, same rows for everyone)

Source file: `data/truth/US-GA.json`

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

## US-3722 New Echota State Historic Site
```json
{
 "checked": "2026-11-08",
 "handover": [],
 "n": "New Echota State Historic Site",
 "official": null,
 "ours": {
  "acres": 193,
  "manager": "",
  "pieces": [
   [
    195105,
    "New Echota Historic Site",
    193,
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
 "t": "State Historic Site",
 "verdict": "no size on page"
}
```

## US-10397 Southern Nantahala Wilderness Area
```json
{
 "checked": "2026-11-08",
 "handover": [],
 "n": "Southern Nantahala Wilderness Area",
 "note": "whole park compared (POTA lists it in 2 states: {'US-GA': 23604, 'US-NC': 23604})",
 "official": null,
 "ours": {
  "acres": 47208,
  "acres_by_state": {
   "US-GA": 23604,
   "US-NC": 23604
  },
  "manager": "",
  "pieces": [
   [
    "wld403",
    "Southern Nantahala Wilderness",
    23604,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "",
  "states": [
   "US-GA",
   "US-NC"
  ],
  "unknown_pieces": 0,
  "whole_park": true
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "Wilderness Area",
 "verdict": "no size on page"
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

## US-12773 Warm Springs National Fish Hatchery
```json
{
 "checked": "2026-11-08",
 "handover": [],
 "n": "Warm Springs National Fish Hatchery",
 "official": null,
 "ours": {
  "acres": 24,
  "manager": "",
  "pieces": [
   [
    4457,
    "Warm Springs National Fish Hatchery",
    59,
    "name"
   ],
   [
    5415,
    "Warm Springs National Fish Hatchery",
    59,
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
 "t": "National Fish Hatchery",
 "verdict": "no size on page"
}
```

## US-12769 Cordele State Fish Hatchery
```json
{
 "checked": "2026-11-08",
 "handover": [],
 "n": "Cordele State Fish Hatchery",
 "official": {
  "acres": 160.0,
  "as": "160 acre",
  "clean": false,
  "line": "hing Guide Now Available HOW TO HUNT AND FISH FOR A LIFETIME Previous Next Cordele Fish Hatchery Cordele is a 160-acre hatchery located in Crisp County. There are 22 ponds that raise channel catfish, shoal bass, largemouth bass,",
  "read": "2026-11-08",
  "sent": "Cordele is a 160-acre hatchery located in Crisp County.",
  "url": "https://georgiawildlife.com/cordele-fish-hatchery",
  "why": "total-looking"
 },
 "ours": {
  "acres": 156,
  "dissolved": {
   "after": 349,
   "before": 519,
   "copies": 1,
   "families": {
    "padus": 178,
    "sggaa": 171
   },
   "family_fold": 171,
   "family_used": "padus",
   "key_union": 156,
   "parts": 0,
   "records": 3,
   "summed": 178,
   "tracts": 2
  },
  "family_fold": "layers {'padus': 178, 'sggaa': 171}: one land in 2 layers, the padus copy used (171 ac of copies not added)",
  "manager": "",
  "note": "3 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 519 -> 349 acres",
  "pieces": [
   [
    195114,
    "Cordele Hatchery",
    178,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 2,
 "same_agency": false,
 "score": 7,
 "t": "State Fish Hatchery",
 "verdict": "agree"
}
```

## US-7896 Standing Boy Creek State Park
```json
{
 "checked": "2026-11-08",
 "handover": [
  {
   "date_hint": "2026",
   "kind": "managed by",
   "line": "dventure Previous Next 1 Standing Boy Creek Park Columbus Park Columbus Previous Next This property is managed by the City of Columbus. Celebrate America's 250th throughout 2026 - View a list of upcoming events . Home Standing Boy Creek Standing Boy Creek",
   "owner_now": "City of Columbus",
   "src": "https://gastateparks.org/StandingBoyCreek",
   "why": "the park's page (data/parkinfo)"
  },
  {
   "date_hint": null,
   "kind": "managed by",
   "line": "Lake Oliver and offers excellent opportunity for hiking, running, biking, and wildlife viewing. It is managed by The City of Columbus via Standing Boy, Inc., an independent 501(c)(3) nonprofit. Quota hunts are held during the fall and spring. All quo",
   "owner_now": "The City of Columbus",
   "src": "https://gastateparks.org/StandingBoyCreek",
   "why": "the park's page (data/parkinfo)"
  }
 ],
 "n": "Standing Boy Creek State Park",
 "official": {
  "acres": 1580.0,
  "as": "1,580 acre",
  "clean": false,
  "line": "Creek Standing Boy Creek Standing Boy Trails is located in the northern portion of the City of Columbus. This 1,580-acre property lies on the shore of Lake Oliver and offers excellent opportunity for hiking, running, biking, and w",
  "read": "2026-11-08",
  "sent": "This 1,580-acre property lies on the shore of Lake Oliver and offers excellent opportunity for hiking, running, biking, and wildlife viewing.",
  "url": "https://gastateparks.org/StandingBoyCreek",
  "why": "total-looking"
 },
 "ours": {
  "acres": 1580,
  "manager": "",
  "pieces": [
   [
    "sggab59",
    "Standing Boy Creek State Park",
    1580,
    "reviewed"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": "City of Columbus",
 "pct": 0,
 "same_agency": false,
 "score": 8,
 "t": "State Park",
 "verdict": "agree"
}
```

## US-2182 Jack Hill State Park
```json
{
 "checked": "2026-11-08",
 "handover": [
  {
   "date_hint": "2020",
   "kind": "renamed",
   "line": ". A 1,500 yard winding bridge connects the original holes with the back nine. In 2020, the park was renamed from Gordonia-Alatamaha to Jack Hill, honoring the late Georgia senator who did much for the community. Hill was instrumental in bringing many facilities to the park, including it",
   "owner_now": "Gordonia-Alatamaha",
   "src": "https://gastateparks.org/JackHill",
   "why": "the park's page (data/parkinfo)"
  }
 ],
 "n": "Jack Hill State Park",
 "official": {
  "acres": 662.0,
  "as": "662 Acres",
  "clean": false,
  "line": "s group shelter, cabins, splash pad, expanded golf course and more. Reservations, Accommodations & Facilities 662 Acres 12 Acre Lake 10 Cottages 29 Tent, Trailer & RV Campsites 1 Walk-In Campsite 4 Picnic Shelters (Before making",
  "read": "2026-11-08",
  "sent": "662 Acres",
  "url": "https://gastateparks.org/JackHill",
  "why": "total-looking"
 },
 "ours": {
  "acres": 683,
  "manager": "",
  "pieces": [
   [
    "sggab23",
    "Jack Hill State Park",
    683,
    "reviewed"
   ]
  ],
  "pin": "just outside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": "Gordonia-Alatamaha",
 "pct": 3,
 "same_agency": false,
 "score": 7,
 "t": "State Park",
 "verdict": "agree"
}
```

## US-3769 River Bend Wildlife Management Area
```json
{
 "checked": "2026-11-08",
 "handover": [],
 "n": "River Bend Wildlife Management Area",
 "official": {
  "acres": 3500.0,
  "as": "3,500 acre",
  "clean": true,
  "line": "unt. Those dates should be listed as a standard hunt. River Bend WMA River Bend Wildlife Management Area is a 3,500-acre property located in Laurens County approximately 8 miles south of East Dublin. River Bend consists of two tra",
  "read": "2026-11-08",
  "sent": "River Bend Wildlife Management Area is a 3,500-acre property located in Laurens County approximately 8 miles south of East Dublin.",
  "url": "https://georgiawildlife.com/river-bend-wma",
  "why": "clean total"
 },
 "ours": {
  "acres": 3454,
  "dissolved": {
   "after": 3676,
   "before": 11014,
   "copies": 2,
   "key_union": 3454,
   "parts": 0,
   "records": 3,
   "summed": 3676,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 11014 -> 3676 acres",
  "pieces": [
   [
    195075,
    "River Bend Wildlife Management Area",
    3676,
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
 "t": "Wildlife Management Area",
 "verdict": "agree"
}
```

## US-9770 Altama Plantation Wildlife Management Area
```json
{
 "cause": "agency smaller: our outline may hold water, a lease or a neighbour tract",
 "checked": "2026-11-08",
 "handover": [],
 "n": "Altama Plantation Wildlife Management Area",
 "official": {
  "acres": 3986.0,
  "as": "3,986 acre",
  "clean": true,
  "line": "T AND FISH FOR A LIFETIME Previous Next Altama Plantation WMA Altama Plantation Wildlife Management Area is a 3,986-acre property in Glynn County. This WMA provides hunting opportunities for deer, turkey, small game and waterfowl.",
  "read": "2026-11-08",
  "sent": "Altama Plantation Wildlife Management Area is a 3,986-acre property in Glynn County.",
  "url": "https://georgiawildlife.com/altama-plantation-wma",
  "why": "clean total"
 },
 "ours": {
  "acres": 4987,
  "dissolved": {
   "after": 8599,
   "before": 12584,
   "copies": 1,
   "families": {
    "sggaa": 3987,
    "sggac": 4612
   },
   "family_fold": 3987,
   "family_used": "sggac",
   "key_union": 4987,
   "parts": 0,
   "records": 3,
   "summed": 4612,
   "tracts": 2
  },
  "family_fold": "layers {'sggac': 4612, 'sggaa': 3987}: one land in 2 layers, the sggac copy used (3,987 ac of copies not added)",
  "manager": "",
  "note": "3 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 12584 -> 8599 acres",
  "pieces": [
   [
    "sggac861",
    "ALTAMA PLANTATION WMA",
    4612,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 25,
 "same_agency": false,
 "score": 5,
 "t": "Wildlife Management Area",
 "verdict": "off"
}
```

## US-0926 Fort Frederica National Monument
```json
{
 "checked": "2026-11-08",
 "handover": [],
 "n": "Fort Frederica National Monument",
 "official": null,
 "ours": {
  "acres": 279,
  "manager": "",
  "pieces": [
   [
    3367,
    "Fort Frederica National Monument",
    279,
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

## US-12770 Richmond Hill State Fish Hatchery
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-11-08",
 "handover": [],
 "n": "Richmond Hill State Fish Hatchery",
 "official": null,
 "ours": {
  "acres": 55,
  "dissolved": {
   "after": 88,
   "before": 264,
   "copies": 2,
   "key_union": 55,
   "parts": 0,
   "records": 3,
   "summed": 88,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 264 -> 88 acres",
  "pieces": [
   [
    195116,
    "Richmond Hill Hatchery",
    88,
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
 "t": "State Fish Hatchery",
 "verdict": "unsure"
}
```
