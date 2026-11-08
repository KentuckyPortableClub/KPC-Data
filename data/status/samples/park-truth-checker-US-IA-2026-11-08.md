# park truth checker: US-IA random sample of 12 (2026-11-08; seed = date + area, same rows for everyone)

Source file: `data/truth/US-IA.json`

## US-11377 Mink Run Wildlife Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Mink Run Wildlife Area",
 "official": null,
 "ours": {
  "acres": 73,
  "dissolved": {
   "after": 73,
   "before": 219,
   "copies": 2,
   "parts": 0,
   "records": 3,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 219 -> 73 acres",
  "pieces": [
   [
    198885,
    "Mink Run Wildlife Management Area",
    73,
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
 "t": "Wildlife Area",
 "verdict": "no size on page"
}
```

## US-9343 South Pine Creek Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "South Pine Creek Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 239,
  "dissolved": {
   "after": 456,
   "before": 694,
   "copies": 0,
   "families": {
    "padus": 217,
    "sgiaa": 239
   },
   "family_fold": 217,
   "family_used": "sgiaa",
   "parts": 2,
   "records": 4,
   "tracts": 2
  },
  "family_fold": "layers {'sgiaa': 239, 'padus': 217}: one land in 2 layers, the sgiaa copy used (217 ac of copies not added)",
  "manager": "",
  "note": "4 joined records = 2 tracts: 0 copies of a tract (same acres, another layer) and 2 fee tracts under a designation record folded; summed 694 -> 456 acres",
  "pieces": [
   [
    "sgiaa34015",
    "SOUTH PINE CREEK WILDLIFE AREA",
    239,
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
 "t": "Wildlife Management Area",
 "verdict": "no size on page"
}
```

## US-9313 Round Lake Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Round Lake Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 436,
  "dissolved": {
   "after": 436,
   "before": 1308,
   "copies": 2,
   "parts": 0,
   "records": 3,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1308 -> 436 acres",
  "pieces": [
   [
    198941,
    "Round Lake (Harrison) Wildlife Management Area",
    436,
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
 "t": "Wildlife Management Area",
 "verdict": "no size on page"
}
```

## US-12376 Blackburn Wildlife Management Area
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 410,000 acres, no total words near it)",
 "checked": "2026-11-01",
 "handover": [],
 "n": "Blackburn Wildlife Management Area",
 "official": {
  "acres": 410000.0,
  "as": "410,000 acres",
  "clean": false,
  "line": "Department of Natural Resources Search Menu Wildlife Management Areas The DNR's Wildlife Bureau manages over 410,000 acres that are available for public recreational use every day of the year. All of these areas are managed with rev",
  "read": "2026-11-01",
  "sent": "The DNR's Wildlife Bureau manages over 410,000 acres that are available for public recreational use every day of the year.",
  "url": "https://www.iowadnr.gov/places-go/wildlife-management-areas",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 79,
  "dissolved": {
   "after": 79,
   "before": 158,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 158 -> 79 acres",
  "pieces": [
   [
    "sgiaa71763",
    "BLACKBURN WILDLIFE AREA",
    79,
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
 "t": "Wildlife Management Area",
 "verdict": "unsure"
}
```

## US-10953 McCoy Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "McCoy Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 562,
  "family_fold": "layers {'sgiaa': 562, 'sgiac': 525, 'padus': 438}: one land in 3 layers, the sgiaa copy used (963 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgiaa33903",
    "MCCOY WILDLIFE AREA",
    562,
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
 "t": "Wildlife Management Area",
 "verdict": "no size on page"
}
```

## US-2325 Viking Lake State Park
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Viking Lake State Park",
 "official": {
  "acres": 1000.0,
  "as": "1,000 acre",
  "clean": false,
  "line": "rk is a popular lake and camping destination with numerous recreational opportunities. A large portion of the 1,000-acre park has been left in its natural state and is abundant in wildflowers and plants. Beavers, turkeys, ducks an",
  "read": "2026-11-01",
  "sent": "A large portion of the 1,000-acre park has been left in its natural state and is abundant in wildflowers and plants.",
  "url": "https://www.iowadnr.gov/Places-to-Go/State-Parks/Iowa-State-Parks/Viking-Lake-State-Park",
  "why": "part (a lake, a purchase, a campground…)"
 },
 "ours": {
  "acres": 1093,
  "dissolved": {
   "after": 2134,
   "before": 3175,
   "copies": 2,
   "families": {
    "padus": 1093,
    "sgiab": 1041
   },
   "family_fold": 1041,
   "family_used": "padus",
   "parts": 0,
   "records": 5,
   "tracts": 3
  },
  "family_fold": "layers {'padus': 1093, 'sgiab': 1041}: one land in 2 layers, the padus copy used (1,041 ac of copies not added)",
  "manager": "",
  "note": "5 joined records = 3 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 3175 -> 2134 acres",
  "pieces": [
   [
    198579,
    "Viking Lake State Park",
    1093,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 2
 },
 "owner_now": null,
 "pct": 9,
 "same_agency": false,
 "score": 8,
 "t": "State Park",
 "verdict": "agree"
}
```

## US-0268 Desoto National Wildlife Refuge
```json
{
 "checked": "2026-11-01",
 "handover": [
  {
   "date_hint": null,
   "kind": "managed by",
   "line": "Image Details A scenic view of Boyer Chute. Boyer Chute National Wildlife Refuge is another refuge managed by the staff of DeSoto National Wildlife Refuge and is located about one mile south on the Missouri River near Fort Calhoun, Nebraska. At Boyer Chute Nati",
   "owner_now": "National Wildlife Refuge and",
   "src": "https://www.fws.gov/refuge/desoto/about-us",
   "why": "FWS refuge about page"
  }
 ],
 "n": "Desoto National Wildlife Refuge",
 "official": {
  "acres": 8365.0,
  "as": "8,365 acres",
  "clean": false,
  "line": "o National Wildlife Refuge is located along the Missouri River and borders both Iowa and Nebraska. Within its 8,365 acres lies DeSoto Lake, an oxbow lake that used to be a bend in the Missouri River. The refuge contains bottomland",
  "read": "2026-11-01",
  "sent": "Within its 8,365 acres lies DeSoto Lake, an oxbow lake that used to be a bend in the Missouri River.",
  "url": "https://www.fws.gov/refuge/desoto/",
  "why": "total-looking"
 },
 "ours": {
  "acres": 7530,
  "family_fold": "layers {'padus': 7530, 'sgiac': 3420}: one land in 2 layers, the padus copy used (3,420 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    4718,
    "Desoto National Wildlife Refuge",
    3986,
    "name"
   ],
   [
    3778,
    "Desoto National Wildlife Refuge",
    3544,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": "National Wildlife Refuge and",
 "pct": 10,
 "same_agency": false,
 "score": 8,
 "t": "National Wildlife Refuge",
 "verdict": "agree"
}
```

## US-11878 Little Mill Wildlife Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Little Mill Wildlife Area",
 "official": null,
 "ours": {
  "acres": 42,
  "dissolved": {
   "after": 42,
   "before": 126,
   "copies": 2,
   "parts": 0,
   "records": 3,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 126 -> 42 acres",
  "pieces": [
   [
    198853,
    "Little Mill Creek Wildlife Management Area",
    42,
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
 "t": "Wildlife Area",
 "verdict": "no size on page"
}
```

## US-9328 Little Storm Lake Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Little Storm Lake Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 274,
  "dissolved": {
   "after": 274,
   "before": 822,
   "copies": 2,
   "parts": 0,
   "records": 3,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 822 -> 274 acres",
  "pieces": [
   [
    198855,
    "Little Storm Lake Wildlife Management Area",
    274,
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
 "t": "Wildlife Management Area",
 "verdict": "no size on page"
}
```

## US-2306 McIntosh Woods State Park
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "McIntosh Woods State Park",
 "official": {
  "acres": 60.0,
  "as": "60 acre",
  "clean": true,
  "line": "on please visit, Park Alerts and Notices. Park Alerts & Notices About the Park McIntosh Woods State Park is a 60-acre natural enclave on the northwest shore of Clear Lake in northern Iowa. The park, founded in 1944, is a popula",
  "read": "2026-11-01",
  "sent": "McIntosh Woods State Park is a 60-acre natural enclave on the northwest shore of Clear Lake in northern Iowa.",
  "url": "https://www.iowadnr.gov/Places-to-Go/State-Parks/Iowa-State-Parks/McIntosh-Woods-State-Park",
  "why": "clean total"
 },
 "ours": {
  "acres": 65,
  "dissolved": {
   "after": 65,
   "before": 193,
   "copies": 2,
   "parts": 0,
   "records": 3,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 193 -> 65 acres",
  "pieces": [
   [
    198556,
    "McIntosh Woods State Park",
    65,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 8,
 "same_agency": false,
 "score": 8,
 "t": "State Park",
 "verdict": "agree"
}
```

## US-2285 Dolliver Memorial State Park
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Dolliver Memorial State Park",
 "official": {
  "acres": 594.0,
  "as": "594 acres",
  "clean": false,
  "line": "s natural bluffs and geological formations. Dolliver overlooks the Des Moines River Valley and spreads across 594 acres of flatlands and rugged trails. Highlights of the park include Boneyard Hollow, the Copperas Beds and histori",
  "read": "2026-11-01",
  "sent": "Dolliver overlooks the Des Moines River Valley and spreads across 594 acres of flatlands and rugged trails.",
  "url": "https://www.iowadnr.gov/Places-to-Go/State-Parks/Iowa-State-Parks/Dolliver-Memorial-State-Park",
  "why": "total-looking"
 },
 "ours": {
  "acres": 614,
  "dissolved": {
   "after": 614,
   "before": 1828,
   "copies": 2,
   "parts": 0,
   "records": 3,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1828 -> 614 acres",
  "pieces": [
   [
    198529,
    "Dolliver Memorial State Park",
    614,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 3,
 "same_agency": false,
 "score": 8,
 "t": "State Park",
 "verdict": "agree"
}
```

## US-0271 Neal Smith National Wildlife Refuge
```json
{
 "cause": "our union: one of our pieces alone matches the agency (double count?)",
 "checked": "2026-11-01",
 "handover": [
  {
   "date_hint": null,
   "kind": "managed by",
   "line": "ational wildlife refuge A national wildlife refuge is typically a contiguous area of land and water managed by the U.S. Fish and Wildlife Service for the conservation and, where appropriate, restoration of fish, wildlife and plant resources and their habitats for th",
   "owner_now": "U.S",
   "src": "https://www.fws.gov/refuge/neal-smith/about-us",
   "why": "FWS refuge about page"
  }
 ],
 "n": "Neal Smith National Wildlife Refuge",
 "official": {
  "acres": 6000.0,
  "as": "6,000 acres",
  "clean": false,
  "line": "d used local seed sources to plant approximately 4,000 acres of tallgrass prairie. Today, the refuge protects 6,000 acres providing food, cover and breeding habitat for resident and migratory wildlife. The refuge also serves as a m",
  "read": "2026-11-01",
  "sent": "Today, the refuge protects 6,000 acres providing food, cover and breeding habitat for resident and migratory wildlife.",
  "url": "https://www.fws.gov/refuge/neal-smith/about-us",
  "why": "total-looking"
 },
 "ours": {
  "acres": 11917,
  "dissolved": {
   "after": 16386,
   "before": 22075,
   "copies": 0,
   "families": {
    "padus": 11917,
    "sgiac": 4469
   },
   "family_fold": 4469,
   "family_used": "padus",
   "parts": 3,
   "records": 12,
   "tracts": 9
  },
  "family_fold": "layers {'padus': 11917, 'sgiac': 4469}: one land in 2 layers, the padus copy used (4,469 ac of copies not added)",
  "manager": "",
  "note": "12 joined records = 9 tracts: 0 copies of a tract (same acres, another layer) and 3 fee tracts under a designation record folded; summed 22075 -> 16386 acres",
  "pieces": [
   [
    5112,
    "Neal Smith National Wildlife Refuge",
    6177,
    "name"
   ],
   [
    4155,
    "Neal Smith National Wildlife Refuge",
    5692,
    "name"
   ],
   [
    4156,
    "Neal Smith National Wildlife Refuge",
    48,
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
 "t": "National Wildlife Refuge",
 "verdict": "off"
}
```
