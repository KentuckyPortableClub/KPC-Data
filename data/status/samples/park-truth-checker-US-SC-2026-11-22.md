# park truth checker: US-SC random sample of 12 (2026-11-22; seed = date + area, same rows for everyone)

Source file: `data/truth/US-SC.json`

## US-3906 Old Island Heritage Preserve
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Old Island Heritage Preserve",
 "official": null,
 "ours": {
  "acres": 3160,
  "family_fold": "layers {'sgscc': 3160, 'padus': 3004}: one land in 2 layers, the sgscc copy used (3,004 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgscc17",
    "Old Island Heritage Preserve and Wildlife Management Area",
    3160,
    "reviewed"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "Heritage Preserve",
 "verdict": "no size on page"
}
```

## US-3899 Great Pee Dee River Heritage Preserve
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-22",
 "handover": [],
 "n": "Great Pee Dee River Heritage Preserve",
 "official": {
  "acres": 25668.0,
  "as": "25,668 acres",
  "clean": true,
  "line": "e Lake is about 9 river miles Woodbury Wildlife Management Area and Heritage Preserve – This area consists of 25,668 acres managed for wildlife and recreation and is located at the south end of Marion County between the Great Pee De",
  "read": "2026-11-22",
  "sent": "This area consists of 25,668 acres managed for wildlife and recreation and is located at the south end of Marion County between the Great Pee Dee and Little Pee Dee Scenic Rivers.",
  "url": "https://www.dnr.sc.gov/water/river/scenic/greatpeedee.html",
  "why": "clean total"
 },
 "ours": {
  "acres": 2810,
  "family_fold": "layers {'padus': 2810, 'sgscc': 2725}: one land in 2 layers, the padus copy used (2,725 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    254037,
    "Great Pee Dee River Heritage Preserve / Wildlife Management Area",
    2810,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 89,
 "same_agency": false,
 "score": 4,
 "t": "Heritage Preserve",
 "verdict": "off"
}
```

## US-5487 Poe Creek State Forest
```json
{
 "checked": "2026-11-22",
 "handover": [
  {
   "date_hint": null,
   "kind": "managed by",
   "line": "stretch of the Little Eastatoe Creek along Scenic Highway 11 in northern Pickens County. The park, now managed by Pickens County, is a popular trout fishing site year-round (brook, brown and rainbow), but in summer months visito",
   "owner_now": "Pickens County",
   "src": "https://www.scfc.gov/state-forests/poe-creek-state-forest/",
   "why": "the park's page (data/parkinfo)"
  }
 ],
 "n": "Poe Creek State Forest",
 "official": {
  "acres": 2508.0,
  "as": "2,508 acre",
  "clean": true,
  "line": "nu State Lands Home » State Lands » Poe Creek State Forest Poe Creek State Forest Poe Creek State Forest is a 2,508-acre tract in Oconee and Pickens counties near Lake Jocassee in the upstate of South Carolina. Nestled in the foot",
  "read": "2026-11-22",
  "sent": "Poe Creek State Forest is a 2,508-acre tract in Oconee and Pickens counties near Lake Jocassee in the upstate of South Carolina.",
  "url": "https://www.scfc.gov/state-forests/poe-creek-state-forest/",
  "why": "clean total"
 },
 "ours": {
  "acres": 2466,
  "dissolved": {
   "after": 1762,
   "before": 2502,
   "copies": 0,
   "key_union": 2466,
   "parts": 10,
   "records": 19,
   "summed": 1762,
   "tracts": 9
  },
  "manager": "",
  "note": "19 joined records = 9 tracts: 0 copies of a tract (same acres, another layer) and 10 fee tracts under a designation record folded; summed 2502 -> 1762 acres",
  "pieces": [
   [
    254293,
    "Poe Creek State Forest",
    1251,
    "name"
   ],
   [
    254296,
    "Poe Creek State Forest",
    330,
    "name"
   ],
   [
    254482,
    "Poe Creek State Forest",
    86,
    "name"
   ],
   [
    254297,
    "Poe Creek State Forest",
    19,
    "name"
   ],
   [
    254485,
    "Poe Creek State Forest",
    19,
    "name"
   ],
   [
    254299,
    "Poe Creek State Forest",
    18,
    "name"
   ],
   [
    254483,
    "Poe Creek State Forest",
    17,
    "name"
   ],
   [
    254489,
    "Poe Creek State Forest",
    12,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": "Pickens County",
 "pct": 2,
 "same_agency": false,
 "score": 8,
 "t": "State Forest",
 "verdict": "agree"
}
```

## US-3892 Chestnut Ridge Heritage Preserve
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Chestnut Ridge Heritage Preserve",
 "official": null,
 "ours": {
  "acres": 2267,
  "manager": "",
  "pieces": [
   [
    254029,
    "Chestnut Ridge Heritage Preserve / Wildlife Management Area",
    1739,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 2
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "Heritage Preserve",
 "verdict": "no size on page"
}
```

## US-3880 Lake Wateree State Park
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Lake Wateree State Park",
 "official": null,
 "ours": {
  "acres": 350,
  "family_fold": "layers {'sgscb': 332, 'padus': 296}: one land in 2 layers, the sgscb copy used (296 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgscb28",
    "Lake Wateree State Park",
    332,
    "reviewed"
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

## US-3921 Pacolet River Heritage Preserve
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Pacolet River Heritage Preserve",
 "official": {
  "acres": 270.0,
  "as": "270 acre",
  "clean": false,
  "line": "gh mixed hardwood and pine upland forest and along the banks of the Pacolet River. You will traverse a quiet, 270-acre preserve that protects two ancient soap stone quarries, and provides habitat for uncommon plant species, as w",
  "read": "2026-11-22",
  "sent": "You will traverse a quiet, 270-acre preserve that protects two ancient soap stone quarries, and provides habitat for uncommon plant species, as well as a variety of song birds, snakes, and other wildlife.",
  "url": "https://www.sctrails.net/trails/trail/pacolet-river-heritage-preserve",
  "why": "total-looking"
 },
 "ours": {
  "acres": 278,
  "dissolved": {
   "after": 278,
   "before": 555,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 555 -> 278 acres",
  "pieces": [
   [
    "sgscc5",
    "Pacolet River Heritage Preserve",
    278,
    "reviewed"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 3,
 "same_agency": false,
 "score": 7,
 "t": "Heritage Preserve",
 "verdict": "agree"
}
```

## US-0017 Congaree National Park
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Congaree National Park",
 "official": null,
 "ours": {
  "acres": 26442,
  "manager": "",
  "pieces": [
   [
    3430,
    "Congaree National Park",
    26442,
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
 "t": "National Park",
 "verdict": "no size on page"
}
```

## US-0519 Carolina Sandhills National Wildlife Refuge
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Carolina Sandhills National Wildlife Refuge",
 "official": {
  "acres": 47000.0,
  "as": "47,000 acres",
  "clean": true,
  "line": "estoring habitats for migratory birds and the endangered red-cockaded woodpecker. The refuge encompasses over 47,000 acres of the unique longleaf pine/wiregrass ecosystem in South Carolina&#x27;s Sandhills region. Visitors can explo",
  "read": "2026-11-22",
  "sent": "The refuge encompasses over 47,000 acres of the unique longleaf pine/wiregrass ecosystem in South Carolina&#x27;s Sandhills region.",
  "url": "https://www.fws.gov/refuge/carolina_sandhills/",
  "why": "clean total"
 },
 "ours": {
  "acres": 45917,
  "dissolved": {
   "after": 45917,
   "before": 91834,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 91834 -> 45917 acres",
  "pieces": [
   [
    3697,
    "Carolina Sandhills National Wildlife Refuge",
    45917,
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
 "score": 8,
 "t": "National Wildlife Refuge",
 "verdict": "agree"
}
```

## US-10622 Fish Dam Ford Heritage Preserve
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Fish Dam Ford Heritage Preserve",
 "official": null,
 "ours": {
  "acres": 143,
  "family_fold": "layers {'padus': 143, 'sgscc': 138}: one land in 2 layers, the padus copy used (138 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    254107,
    "Fish Dam Ford Heritage Preserve",
    143,
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
 "t": "Heritage Preserve",
 "verdict": "no size on page"
}
```

## US-2895 Givhans Ferry State Park
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Givhans Ferry State Park",
 "official": {
  "acres": 988.0,
  "as": "988 acres",
  "clean": false,
  "line": "r family or other group outings 1.5 mile River Bluff Nature Trail 10 hike in campsites for tents and hammocks 988 acres of lowcountry splendor PARK DEALS SEE ALL DEALS 2026 Cyber Weekend Deals Givhans Ferry State Park READ MORE D",
  "read": "2026-11-22",
  "sent": "988 acres of lowcountry splendor",
  "url": "https://southcarolinaparks.com/givhans-ferry",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 1036,
  "family_fold": "layers {'sgscb': 1036, 'padus': 1002}: one land in 2 layers, the sgscb copy used (1,002 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgscb15",
    "Givhans Ferry State Park",
    1036,
    "reviewed"
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
 "t": "State Park",
 "verdict": "agree"
}
```

## US-5489 Wee Tee State Forest
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Wee Tee State Forest",
 "official": {
  "acres": 12400.0,
  "as": "12,400 acres",
  "clean": true,
  "line": "ng with legal requirements, and continually improving forest practices. Wee Tee State Forest encompasses over 12,400 acres of productive forest land. Most of the land base is dominated by 92% of bottomland hardwoods, pine/pine-hardw",
  "read": "2026-11-22",
  "sent": "Wee Tee State Forest encompasses over 12,400 acres of productive forest land.",
  "url": "https://www.scfc.gov/state-forests/wee-tee-state-forest/",
  "why": "clean total"
 },
 "ours": {
  "acres": 12082,
  "dissolved": {
   "after": 12082,
   "before": 12419,
   "copies": 0,
   "parts": 3,
   "records": 9,
   "tracts": 6
  },
  "manager": "",
  "note": "9 joined records = 6 tracts: 0 copies of a tract (same acres, another layer) and 3 fee tracts under a designation record folded; summed 12419 -> 12082 acres",
  "pieces": [
   [
    254364,
    "Wee Tee State Forest",
    10448,
    "name"
   ],
   [
    254366,
    "Wee Tee State Forest",
    604,
    "name"
   ],
   [
    254370,
    "Wee Tee State Forest",
    408,
    "name"
   ],
   [
    254363,
    "Wee Tee State Forest",
    339,
    "name"
   ],
   [
    254371,
    "Wee Tee State Forest",
    201,
    "name"
   ],
   [
    254365,
    "Wee Tee State Forest",
    82,
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
 "t": "State Forest",
 "verdict": "agree"
}
```

## US-2890 Colleton State Park
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Colleton State Park",
 "official": null,
 "ours": {
  "acres": 35,
  "family_fold": "layers {'sgscb': 40, 'padus': 34}: one land in 2 layers, the sgscb copy used (34 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgscb9",
    "Colleton State Park",
    40,
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
 "t": "State Park",
 "verdict": "no size on page"
}
```
