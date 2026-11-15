# park truth checker: US-SC random sample of 12 (2026-11-15; seed = date + area, same rows for everyone)

Source file: `data/truth/US-SC.json`

## US-8151 Woodbury Wildlife Management Area
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-15",
 "n": "Woodbury Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 25930,
  "dissolved": {
   "after": 25930,
   "before": 77266,
   "copies": 2,
   "parts": 0,
   "records": 4,
   "tracts": 2
  },
  "manager": "",
  "note": "4 joined records = 2 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 77266 -> 25930 acres",
  "pieces": [
   [
    254100,
    "Woodbury Wildlife Management Area",
    25929,
    "name"
   ],
   [
    "sgscd97",
    "Woodbury WMA",
    1,
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

## US-3891 Campbells Crossroads and Angelus Tracts Wildlife Management Area
```json
{
 "checked": "2026-11-08",
 "handover": [],
 "n": "Campbells Crossroads and Angelus Tracts Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 223,
  "dissolved": {
   "after": 349,
   "before": 1045,
   "copies": 2,
   "key_union": 223,
   "parts": 0,
   "records": 3,
   "summed": 349,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1045 -> 349 acres",
  "pieces": [
   [
    254071,
    "Campbells Crossroads Wildlife Management Area",
    349,
    "words"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 5,
 "t": "Wildlife Management Area",
 "verdict": "no size on page"
}
```

## US-2885 Barnwell State Park
```json
{
 "checked": "2026-11-08",
 "handover": [],
 "n": "Barnwell State Park",
 "official": {
  "acres": 307.0,
  "as": "307 acres",
  "clean": false,
  "line": "gatherings 1 Community Building perfect for reunions, weddings and more 3 small park lakes teeming with fish 307 acres to enjoy Golf Cart Policy Important Info Pet Friendly Lodging EXPLORE MORE UPCOMING STATE PARK EVENTS SHARE Y",
  "read": "2026-11-08",
  "sent": "307 acres to enjoy",
  "url": "https://southcarolinaparks.com/barnwell",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 316,
  "family_fold": "layers {'sgscb': 316, 'padus': 309}: one land in 2 layers, the sgscb copy used (309 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgscb4",
    "Barnwell State Park",
    316,
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
 "score": 8,
 "t": "State Park",
 "verdict": "agree"
}
```

## US-3884 Battle of Rivers Bridge State Historic Site
```json
{
 "checked": "2026-11-08",
 "handover": [],
 "n": "Battle of Rivers Bridge State Historic Site",
 "official": null,
 "ours": {
  "acres": 425,
  "family_fold": "layers {'sgscb': 399, 'padus': 376}: one land in 2 layers, the sgscb copy used (376 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgscb41",
    "Rivers Bridge State Historic Site",
    399,
    "words"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "State Historic Site",
 "verdict": "no size on page"
}
```

## US-3914 Cathedral Bay Heritage Preserve
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-15",
 "n": "Cathedral Bay Heritage Preserve",
 "official": null,
 "ours": {
  "acres": 52,
  "family_fold": "layers {'sgscc': 58, 'padus': 52}: one land in 2 layers, the sgscc copy used (52 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgscc44",
    "Cathedral Bay Heritage Preserve",
    58,
    "reviewed"
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

## US-11995 Fort Frederick Heritage Preserve
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-15",
 "n": "Fort Frederick Heritage Preserve",
 "official": null,
 "ours": {
  "acres": 5,
  "dissolved": {
   "after": 3,
   "before": 6,
   "copies": 1,
   "key_union": 5,
   "parts": 0,
   "records": 2,
   "summed": 3,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 6 -> 3 acres",
  "pieces": [
   [
    254108,
    "Fort Frederick Heritage Preserve",
    3,
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

## US-3902 James L. Mason Wildlife Management Area
```json
{
 "checked": "2026-11-08",
 "handover": [],
 "n": "James L. Mason Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 2342,
  "dissolved": {
   "after": 4073,
   "before": 6068,
   "copies": 1,
   "families": {
    "padus": 2078,
    "sgsca": 1995
   },
   "family_fold": 1995,
   "family_used": "padus",
   "key_union": 2342,
   "parts": 0,
   "records": 3,
   "summed": 2078,
   "tracts": 2
  },
  "family_fold": "layers {'padus': 2078, 'sgsca': 1995}: one land in 2 layers, the padus copy used (1,995 ac of copies not added)",
  "manager": "",
  "note": "3 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 6068 -> 4073 acres",
  "pieces": [
   [
    254077,
    "James L. Mason Wildlife Management Area",
    2078,
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

## US-3889 Botany Bay Plantation Heritage Preserve
```json
{
 "checked": "2026-11-08",
 "handover": [],
 "n": "Botany Bay Plantation Heritage Preserve",
 "official": null,
 "ours": {
  "acres": 3239,
  "family_fold": "layers {'sgscc': 4687, 'padus': 3599}: one land in 2 layers, the sgscc copy used (3,599 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgscc47",
    "Botany Bay Heritage Preserve and Wildlife Management Area",
    4687,
    "reviewed"
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

## US-2888 Cheraw State Park
```json
{
 "checked": "2026-11-08",
 "handover": [],
 "n": "Cheraw State Park",
 "official": null,
 "ours": {
  "acres": 8805,
  "dissolved": {
   "after": 7335,
   "before": 14613,
   "copies": 1,
   "key_union": 8805,
   "parts": 0,
   "records": 2,
   "summed": 7335,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 14613 -> 7335 acres",
  "pieces": [
   [
    "sgscb7",
    "Cheraw State Park",
    7335,
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
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-08",
 "handover": [],
 "n": "Pacolet River Heritage Preserve",
 "official": {
  "acres": 258.0,
  "as": "258 acre",
  "clean": false,
  "line": "No Fee No Camping Summary: Located near the confluence of the Pacolet River and the Lawson&rsquo;s Fork, the 258 acre preserve protects two prehistoric soapstone outcrops that date back 3-5,000 years ago and provides habitat fo",
  "read": "2026-11-08",
  "sent": "Located near the confluence of the Pacolet River and the Lawson&rsquo;s Fork, the 258 acre preserve protects two prehistoric soapstone outcrops that date back 3-5,000 years ago and provides habitat for uncommon plant species.",
  "url": "https://www.sctrails.net/trails/trail/pacolet-river-heritage-preserve",
  "why": "total-looking"
 },
 "ours": {
  "acres": 171,
  "dissolved": {
   "after": 278,
   "before": 555,
   "copies": 1,
   "key_union": 171,
   "parts": 0,
   "records": 2,
   "summed": 278,
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
 "pct": 34,
 "same_agency": false,
 "score": 5,
 "t": "Heritage Preserve",
 "verdict": "off"
}
```

## US-2912 Santee State Park
```json
{
 "cause": "agency smaller: our outline may hold water, a lease or a neighbour tract",
 "checked": "2026-11-08",
 "handover": [],
 "n": "Santee State Park",
 "official": {
  "acres": 2500.0,
  "as": "2500 acres",
  "clean": false,
  "line": "picnics and group gatherings 30 modern cabins- 10 located on a pier over Lake Marion and 20 on the lakeshore 2500 acres in the heart of Santee Cooper Country Golf Cart Policy Important Info Pet Friendly Lodging EXPLORE MORE UPCOM",
  "read": "2026-11-08",
  "sent": "2500 acres in the heart of Santee Cooper Country",
  "url": "https://southcarolinaparks.com/santee",
  "why": "total-looking"
 },
 "ours": {
  "acres": 3534,
  "family_fold": "layers {'sgscb': 2952, 'padus': 2828}: one land in 2 layers, the sgscb copy used (2,828 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgscb44",
    "Santee State Park",
    2952,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 41,
 "same_agency": false,
 "score": 6,
 "t": "State Park",
 "verdict": "off"
}
```

## US-5485 Harbison State Forest
```json
{
 "checked": "2026-11-08",
 "handover": [],
 "n": "Harbison State Forest",
 "official": {
  "acres": 2176.0,
  "as": "2,176 acres",
  "clean": true,
  "line": "ever leaving town. Bounded along its northeastern edge by the Broad River, Harbison State Forest encompasses 2,176 acres of forestland only nine miles from the capital city's center. More than 30 miles of roads and trails weave th",
  "read": "2026-11-08",
  "sent": "Bounded along its northeastern edge by the Broad River, Harbison State Forest encompasses 2,176 acres of forestland only nine miles from the capital city's center.",
  "url": "https://www.scfc.gov/state-forests/harbison-state-forest/",
  "why": "clean total"
 },
 "ours": {
  "acres": 1865,
  "dissolved": {
   "after": 1865,
   "before": 2143,
   "copies": 0,
   "parts": 4,
   "records": 11,
   "tracts": 7
  },
  "manager": "",
  "note": "11 joined records = 7 tracts: 0 copies of a tract (same acres, another layer) and 4 fee tracts under a designation record folded; summed 2143 -> 1865 acres",
  "pieces": [
   [
    254406,
    "Harbison State Forest",
    1381,
    "name"
   ],
   [
    254409,
    "Harbison State Forest",
    279,
    "name"
   ],
   [
    254405,
    "Harbison State Forest",
    92,
    "name"
   ],
   [
    254403,
    "Harbison State Forest",
    44,
    "name"
   ],
   [
    254407,
    "Harbison State Forest",
    28,
    "name"
   ],
   [
    254413,
    "Harbison State Forest",
    23,
    "name"
   ],
   [
    254408,
    "Harbison State Forest",
    18,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 14,
 "same_agency": false,
 "score": 8,
 "t": "State Forest",
 "verdict": "agree"
}
```
