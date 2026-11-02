# park truth checker: US-TX random sample of 12 (2026-11-01; seed = date + area, same rows for everyone)

Source file: `data/truth/US-TX.json`

## US-0541 Aransas National Wildlife Refuge
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-11-01",
 "handover": [
  {
   "date_hint": null,
   "kind": "managed by",
   "line": "Learn More About Us What We Do The National Wildlife Refuge System is a series of lands and waters owned and managed by the U.S. Fish and Wildlife Service. Wildlife conservation is at the heart of the refuge system. It drives everything we do from the purpose a refuge is establis",
   "owner_now": "U.S",
   "src": "https://www.fws.gov/refuge/aransas",
   "why": "the park's page (data/parkinfo)"
  }
 ],
 "n": "Aransas National Wildlife Refuge",
 "official": null,
 "ours": {
  "acres": 90764,
  "dissolved": {
   "after": 131350,
   "before": 225830,
   "copies": 2,
   "families": {
    "padus": 90764,
    "sgtxd": 40586
   },
   "family_fold": 40586,
   "family_used": "padus",
   "parts": 11,
   "records": 24,
   "tracts": 11
  },
  "family_fold": "layers {'padus': 90764, 'sgtxd': 40586}: one land in 2 layers, the padus copy used (40,586 ac of copies not added)",
  "manager": "",
  "note": "24 joined records = 11 tracts: 2 copies of a tract (same acres, another layer) and 11 fee tracts under a designation record folded; summed 225830 -> 131350 acres",
  "pieces": [
   [
    3586,
    "Aransas National Wildlife Refuge",
    90764,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 4
 },
 "owner_now": "U.S",
 "pct": null,
 "score": 7,
 "t": "National Wildlife Refuge",
 "verdict": "unsure"
}
```

## US-3015 Goliad State Park
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Goliad State Park",
 "official": null,
 "ours": {
  "acres": 148,
  "manager": "",
  "pieces": [
   [
    263504,
    "Goliad State Park",
    275,
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

## US-4415 Davy Crockett National Forest
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-01",
 "handover": [],
 "n": "Davy Crockett National Forest",
 "official": {
  "acres": 675000.0,
  "as": "675, 000 acres",
  "clean": false,
  "line": "T T Welcome to National Forests in Texas Discover the National Forests and Grasslands in Texas, spanning over 675, 000 acres, these public lands offer something for everyone. Plan your visit today and explore the best of Texas’s great",
  "read": "2026-11-01",
  "sent": "Discover the National Forests and Grasslands in Texas, spanning over 675, 000 acres, these public lands offer something for everyone.",
  "url": "https://www.fs.usda.gov/detail/texas/about-forest/districts/?cid=fswdev3_008441",
  "why": "total-looking"
 },
 "ours": {
  "acres": 400950,
  "dissolved": {
   "after": 674541,
   "before": 696927,
   "copies": 9,
   "families": {
    "padus": 161095,
    "sgtxd": 513446
   },
   "family_fold": 161095,
   "family_used": "sgtxd",
   "key_union": 400950,
   "parts": 18,
   "records": 171,
   "summed": 513446,
   "tracts": 144
  },
  "family_fold": "layers {'sgtxd': 513446, 'padus': 161095}: one land in 2 layers, the sgtxd copy used (161,095 ac of copies not added)",
  "manager": "",
  "note": "171 joined records = 144 tracts: 9 copies of a tract (same acres, another layer) and 18 fee tracts under a designation record folded; summed 696927 -> 674541 acres",
  "pieces": [
   [
    "sgtxd322",
    "Davy Crockett National Forest",
    368693,
    "name"
   ],
   [
    "sgtxd11345",
    "Davy Crockett National Forest",
    14099,
    "name"
   ],
   [
    "sgtxd11312",
    "Davy Crockett National Forest",
    13814,
    "name"
   ],
   [
    "sgtxd11194",
    "Davy Crockett National Forest",
    12601,
    "name"
   ],
   [
    "sgtxd11163",
    "Davy Crockett National Forest",
    8980,
    "name"
   ],
   [
    "sgtxd11158",
    "Davy Crockett National Forest",
    8353,
    "name"
   ],
   [
    "sgtxd11293",
    "Davy Crockett National Forest",
    7501,
    "name"
   ],
   [
    "sgtxd11254",
    "Davy Crockett National Forest",
    7204,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 4
 },
 "owner_now": null,
 "pct": 41,
 "same_agency": false,
 "score": 6,
 "t": "National Forest",
 "verdict": "off"
}
```

## US-0633 Caddo Lake National Wildlife Refuge
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-11-01",
 "handover": [],
 "n": "Caddo Lake National Wildlife Refuge",
 "official": null,
 "ours": {
  "acres": 17748,
  "dissolved": {
   "after": 29276,
   "before": 30780,
   "copies": 0,
   "families": {
    "padus": 15041,
    "sgtxd": 14235
   },
   "family_fold": 14235,
   "family_used": "padus",
   "key_union": 17748,
   "parts": 7,
   "records": 17,
   "summed": 15041,
   "tracts": 10
  },
  "family_fold": "layers {'sgtxd': 14235, 'padus': 15041}: one land in 2 layers, the padus copy used (14,235 ac of copies not added)",
  "manager": "",
  "note": "17 joined records = 10 tracts: 0 copies of a tract (same acres, another layer) and 7 fee tracts under a designation record folded; summed 30780 -> 29276 acres",
  "pieces": [
   [
    4618,
    "Caddo Lake National Wildlife Refuge",
    7756,
    "name"
   ],
   [
    3684,
    "Caddo Lake National Wildlife Refuge",
    7285,
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
 "t": "National Wildlife Refuge",
 "verdict": "unsure"
}
```

## US-6536 Atkinson Island Wildlife Management Area
```json
{
 "cause": "agency smaller: our outline may hold water, a lease or a neighbour tract",
 "checked": "2026-11-01",
 "handover": [],
 "n": "Atkinson Island Wildlife Management Area",
 "official": {
  "acres": 90.0,
  "as": "90 acres",
  "clean": false,
  "line": "rmitted in Atkinson Island WMA. There is 40 acres of woodlot composed of mainly hackberry and yaupon. Another 90 acres segment is brackish marsh and then 20 acres is a spoils site left from dredging the channel. Visitors will ne",
  "read": "2026-11-01",
  "sent": "Another 90 acres segment is brackish marsh and then 20 acres is a spoils site left from dredging the channel.",
  "url": "https://tpwd.texas.gov/huntwild/hunt/wma/find_a_wma/list/?id=57",
  "why": "total-looking"
 },
 "ours": {
  "acres": 152,
  "dissolved": {
   "after": 152,
   "before": 304,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 304 -> 152 acres",
  "pieces": [
   [
    261768,
    "Atkinson Island Wildlife Management Area",
    152,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 69,
 "same_agency": false,
 "score": 6,
 "t": "Wildlife Management Area",
 "verdict": "off"
}
```

## US-2993 Buescher State Park
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-11-01",
 "handover": [],
 "n": "Buescher State Park",
 "official": null,
 "ours": {
  "acres": 1178,
  "dissolved": {
   "after": 1073,
   "before": 2137,
   "copies": 1,
   "key_union": 1178,
   "parts": 0,
   "records": 2,
   "summed": 1073,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 2137 -> 1073 acres",
  "pieces": [
   [
    263489,
    "Buescher State Park",
    1073,
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
 "verdict": "unsure"
}
```

## US-3050 Purtis Creek State Park
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-11-01",
 "handover": [],
 "n": "Purtis Creek State Park",
 "official": null,
 "ours": {
  "acres": 1537,
  "dissolved": {
   "after": 1537,
   "before": 3074,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 3074 -> 1537 acres",
  "pieces": [
   [
    263521,
    "Purtis Creek State Park",
    1537,
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
 "verdict": "unsure"
}
```

## US-6588 Nature Center Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Nature Center Wildlife Management Area",
 "official": {
  "acres": 82.0,
  "as": "82 acre",
  "clean": false,
  "line": "center building is available only upon approved reservation. Phone: (903) 566-1626, ext. 2407 Description The 82-acre Nature Center was developed from a former game bird hatchery into an ecological education center. A visitor's",
  "read": "2026-11-01",
  "sent": "The 82-acre Nature Center was developed from a former game bird hatchery into an ecological education center.",
  "url": "https://tpwd.texas.gov/huntwild/hunt/wma/find_a_wma/list/?id=59",
  "why": "total-looking"
 },
 "ours": {
  "acres": 91,
  "dissolved": {
   "after": 86,
   "before": 172,
   "copies": 1,
   "key_union": 91,
   "parts": 0,
   "records": 2,
   "summed": 86,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 172 -> 86 acres",
  "pieces": [
   [
    261767,
    "The Nature Center",
    86,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 11,
 "same_agency": false,
 "score": 8,
 "t": "Wildlife Management Area",
 "verdict": "agree"
}
```

## US-6595 Redhead Pond Wildlife Management Area
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-11-01",
 "handover": [],
 "n": "Redhead Pond Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 31,
  "dissolved": {
   "after": 38,
   "before": 76,
   "copies": 1,
   "key_union": 31,
   "parts": 0,
   "records": 2,
   "summed": 38,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 76 -> 38 acres",
  "pieces": [
   [
    261782,
    "Redhead Pond Wildlife Management Area",
    38,
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
 "t": "Wildlife Management Area",
 "verdict": "unsure"
}
```

## US-3055 Seminole Canyon State Park
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Seminole Canyon State Park",
 "official": null,
 "ours": {
  "acres": 1586,
  "manager": "",
  "pieces": [
   [
    261802,
    "Seminole Canyon State Park",
    2057,
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

## US-3505 Honey Creek Natural State Conservation Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Honey Creek Natural State Conservation Area",
 "official": null,
 "ours": {
  "acres": 1979,
  "dissolved": {
   "after": 2281,
   "before": 4562,
   "copies": 1,
   "key_union": 1979,
   "parts": 0,
   "records": 2,
   "summed": 2281,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 4562 -> 2281 acres",
  "pieces": [
   [
    261750,
    "Honey Creek State Natural Area",
    2281,
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
 "t": "State Conservation Area",
 "verdict": "no size on page"
}
```

## US-3009 Fort Boggy State Park
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Fort Boggy State Park",
 "official": null,
 "ours": {
  "acres": 1726,
  "dissolved": {
   "after": 1726,
   "before": 3452,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 3452 -> 1726 acres",
  "pieces": [
   [
    263497,
    "Fort Boggy State Park",
    1726,
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
