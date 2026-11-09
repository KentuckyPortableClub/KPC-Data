# park truth checker: US-TX random sample of 12 (2026-11-09; seed = date + area, same rows for everyone)

Source file: `data/truth/US-TX.json`

## US-0545 Brazoria National Wildlife Refuge
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Brazoria National Wildlife Refuge",
 "official": {
  "acres": 44413.0,
  "as": "44,413 acre",
  "clean": false,
  "line": "rflies and dragonflies. While the refuge is managed for the benefit of wildlife, it is also here for you. The 44,413-acre Brazoria National Wildlife Refuge is a place for people to enjoy nature and get outside. Wildlife watching, h",
  "read": "2026-11-09",
  "sent": "The 44,413-acre Brazoria National Wildlife Refuge is a place for people to enjoy nature and get outside.",
  "url": "https://www.fws.gov/refuge/brazoria/visit-us",
  "why": "total-looking"
 },
 "ours": {
  "acres": 50390,
  "dissolved": {
   "after": 81056,
   "before": 140097,
   "copies": 3,
   "families": {
    "padus": 47030,
    "sgtxd": 34026
   },
   "family_fold": 34026,
   "family_used": "padus",
   "key_union": 50390,
   "parts": 41,
   "records": 54,
   "summed": 47030,
   "tracts": 10
  },
  "family_fold": "layers {'padus': 47030, 'sgtxd': 34026}: one land in 2 layers, the padus copy used (34,026 ac of copies not added)",
  "manager": "",
  "note": "54 joined records = 10 tracts: 3 copies of a tract (same acres, another layer) and 41 fee tracts under a designation record folded; summed 140097 -> 81056 acres",
  "pieces": [
   [
    3661,
    "Brazoria National Wildlife Refuge",
    47030,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 13,
 "same_agency": false,
 "score": 8,
 "t": "National Wildlife Refuge",
 "verdict": "agree"
}
```

## US-3031 Lake Tawakoni State Park
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 376 acres, no total words near it)",
 "checked": "2026-11-09",
 "handover": [],
 "n": "Lake Tawakoni State Park",
 "official": {
  "acres": 376.0,
  "as": "376 acres",
  "clean": false,
  "line": ", your hiking shoes and your camping gear - we’re just 50 miles east of Dallas. Things to Do Come explore our 376 acres of oak forest, more than five miles of lakeshore, and the lake itself. Boat, fish or swim on the water; hike,",
  "read": "2026-11-09",
  "sent": "Come explore our 376 acres of oak forest, more than five miles of lakeshore, and the lake itself.",
  "url": "https://tpwd.texas.gov/state-parks/lake-tawakoni",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 437,
  "family_fold": "layers {'sgtxd': 437, 'padus': 395}: one land in 2 layers, the sgtxd copy used (395 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgtxd507",
    "Lake Tawakoni",
    437,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 16,
 "same_agency": false,
 "score": 7,
 "t": "State Park",
 "verdict": "unsure"
}
```

## US-2993 Buescher State Park
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-11-09",
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

## US-6542 Caddo Lake Wildlife Management Area
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-11-09",
 "handover": [],
 "n": "Caddo Lake Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 22729,
  "dissolved": {
   "after": 8921,
   "before": 25684,
   "copies": 2,
   "families": {
    "padus": 8456,
    "sgtxd": 465
   },
   "family_fold": 465,
   "family_used": "padus",
   "key_union": 22729,
   "parts": 0,
   "records": 4,
   "summed": 8456,
   "tracts": 2
  },
  "family_fold": "layers {'padus': 8456, 'sgtxd': 465}: one land in 2 layers, the padus copy used (465 ac of copies not added)",
  "manager": "",
  "note": "4 joined records = 2 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 25684 -> 8921 acres",
  "pieces": [
   [
    261770,
    "Caddo Lake Wildlife Management Area",
    8456,
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
 "t": "Wildlife Management Area",
 "verdict": "unsure"
}
```

## US-4370 Caddo National Grasslands Wildlife Management Area
```json
{
 "cause": "our union: one of our pieces alone matches the agency (double count?)",
 "checked": "2026-11-09",
 "handover": [],
 "n": "Caddo National Grasslands Wildlife Management Area",
 "official": {
  "acres": 13360.0,
  "as": "13,360 acre",
  "clean": false,
  "line": "reement with Texas Parks and Wildlife. The WMA is located in Fannin County and is divided into two units, the 13,360 acre Bois d' Arc Creek Unit and the 2,780 acre Ladonia Unit. The Bois d' Arc Creek Unit comprises six separate lan",
  "read": "2026-11-09",
  "sent": "The WMA is located in Fannin County and is divided into two units, the 13,360 acre Bois d' Arc Creek Unit and the 2,780 acre Ladonia Unit.",
  "url": "https://tpwd.texas.gov/huntwild/hunt/wma/find_a_wma/list/?id=4",
  "why": "total-looking"
 },
 "ours": {
  "acres": 68216,
  "family_fold": "layers {'sgtxd': 52012, 'padus': 17722}: one land in 2 layers, the sgtxd copy used (17,722 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgtxd194",
    "Caddo National Grasslands",
    35654,
    "name"
   ],
   [
    "sgtxd193",
    "Caddo National Grasslands",
    14160,
    "name"
   ],
   [
    "sgtxd189",
    "Caddo National Grasslands",
    1771,
    "name"
   ],
   [
    "sgtxd11227",
    "Caddo National Grasslands",
    157,
    "name"
   ],
   [
    "sgtxd11229",
    "Caddo National Grasslands",
    85,
    "name"
   ],
   [
    "sgtxd11225",
    "Caddo National Grasslands",
    76,
    "name"
   ],
   [
    "sgtxd11155",
    "Caddo National Grasslands",
    60,
    "name"
   ],
   [
    "sgtxd11161",
    "Caddo National Grasslands",
    27,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 411,
 "same_agency": false,
 "score": 6,
 "t": "Wildlife Management Area",
 "verdict": "off"
}
```

## US-2998 Cleburne State Park
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 116 acre, no total words near it)",
 "checked": "2026-11-09",
 "handover": [],
 "n": "Cleburne State Park",
 "official": {
  "acres": 116.0,
  "as": "116 acre",
  "clean": false,
  "line": ", set up camp, look for geocaches , and nature watch. Water Sports The park surrounds the clear blue water of 116-acre Cedar Lake. Enjoy swimming, fishing and no-wake boating. Try your luck fishing from our ADA-accessible, cover",
  "read": "2026-11-09",
  "sent": "The park surrounds the clear blue water of 116-acre Cedar Lake.",
  "url": "https://tpwd.texas.gov/state-parks/cleburne",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 451,
  "dissolved": {
   "after": 534,
   "before": 1068,
   "copies": 1,
   "key_union": 451,
   "parts": 0,
   "records": 2,
   "summed": 534,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1068 -> 534 acres",
  "pieces": [
   [
    261791,
    "Cleburne State Park",
    534,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 289,
 "same_agency": false,
 "score": 7,
 "t": "State Park",
 "verdict": "unsure"
}
```

## US-3003 Davis Mountains State Park
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Davis Mountains State Park",
 "official": null,
 "ours": {
  "acres": 3088,
  "dissolved": {
   "after": 2728,
   "before": 5452,
   "copies": 1,
   "key_union": 3088,
   "parts": 0,
   "records": 2,
   "summed": 2728,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 5452 -> 2728 acres",
  "pieces": [
   [
    "sgtxd11582",
    "Davis Mountains SP",
    2728,
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

## US-3042 Mother Neff State Park
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Mother Neff State Park",
 "official": null,
 "ours": {
  "acres": 431,
  "dissolved": {
   "after": 383,
   "before": 766,
   "copies": 1,
   "key_union": 431,
   "parts": 0,
   "records": 2,
   "summed": 383,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 766 -> 383 acres",
  "pieces": [
   [
    263517,
    "Mother Neff State Park",
    383,
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

## US-2992 Brazos Bend State Park
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-11-09",
 "handover": [],
 "n": "Brazos Bend State Park",
 "official": null,
 "ours": {
  "acres": 5024,
  "family_fold": "layers {'padus': 5298, 'sgtxd': 4997}: one land in 2 layers, the padus copy used (4,997 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    263488,
    "Brazos Bend State Park",
    5298,
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
 "verdict": "unsure"
}
```

## US-3006 Estero Llano Grande State Park
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Estero Llano Grande State Park",
 "official": null,
 "ours": {
  "acres": 225,
  "manager": "",
  "pieces": [
   [
    263495,
    "Estero Llano Grande State ParK",
    225,
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
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-2987 Bentsen-Rio Grande Valley State Park
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Bentsen-Rio Grande Valley State Park",
 "official": null,
 "ours": {
  "acres": 764,
  "manager": "",
  "pieces": [
   [
    261788,
    "Bentsen - Rio Grande Valley State Park",
    764,
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
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-4415 Davy Crockett National Forest
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-09",
 "handover": [],
 "n": "Davy Crockett National Forest",
 "official": {
  "acres": 675000.0,
  "as": "675, 000 acres",
  "clean": false,
  "line": "T T Welcome to National Forests in Texas Discover the National Forests and Grasslands in Texas, spanning over 675, 000 acres, these public lands offer something for everyone. Plan your visit today and explore the best of Texas’s great",
  "read": "2026-11-09",
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
