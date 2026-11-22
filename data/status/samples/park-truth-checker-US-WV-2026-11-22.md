# park truth checker: US-WV random sample of 12 (2026-11-22; seed = date + area, same rows for everyone)

Source file: `data/truth/US-WV.json`

## US-9743 Tomblin Wildlife Management Area
```json
{
 "cause": "a number 76 parks share from the same sentence (1,400,000 ac): an agency total, not this park",
 "checked": "2026-11-22",
 "handover": [],
 "n": "Tomblin Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 25225,
  "manager": "",
  "pieces": [
   [
    273205,
    "Tomblin Wildlife Management Area",
    25225,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "same_agency": false,
 "score": 6,
 "t": "Wildlife Management Area",
 "verdict": "unsure"
}
```

## US-7034 Anawalt Lake Wildlife Management Area
```json
{
 "cause": "a number 76 parks share from the same sentence (1,400,000 ac): an agency total, not this park",
 "checked": "2026-11-22",
 "handover": [],
 "n": "Anawalt Lake Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 1796,
  "dissolved": {
   "after": 1796,
   "before": 3591,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 3591 -> 1796 acres",
  "pieces": [
   [
    273142,
    "Anawalt Lake Wildlife Management Area",
    1796,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "same_agency": false,
 "score": 7,
 "t": "Wildlife Management Area",
 "verdict": "unsure"
}
```

## US-7024 Elk River Wildlife Management Area
```json
{
 "cause": "a number 76 parks share from the same sentence (1,400,000 ac): an agency total, not this park",
 "checked": "2026-11-22",
 "handover": [],
 "n": "Elk River Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 19850,
  "dissolved": {
   "after": 19850,
   "before": 39513,
   "copies": 1,
   "parts": 0,
   "records": 3,
   "tracts": 2
  },
  "manager": "",
  "note": "3 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 39513 -> 19850 acres",
  "pieces": [
   [
    273255,
    "Elk River Wildlife Management Area",
    19808,
    "name"
   ],
   [
    9332,
    "Elk River Wildlife Management Area",
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
 "same_agency": false,
 "score": 7,
 "t": "Wildlife Management Area",
 "verdict": "unsure"
}
```

## US-1817 Moncove Lake State Park
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-22",
 "handover": [],
 "n": "Moncove Lake State Park",
 "official": {
  "acres": 250.0,
  "as": "250 acre",
  "clean": false,
  "line": "w Home » Explore Parks » Moncove Lake State Park Moncove Lake State Park Hidden among the hills is a peaceful 250-acre park with a 500-acre wildlife management area. Moncove Lake State Park resides on the southeastern edge of We",
  "read": "2026-11-22",
  "sent": "Hidden among the hills is a peaceful 250-acre park with a 500-acre wildlife management area.",
  "url": "https://wvstateparks.com/park/moncove-lake-state-park/",
  "why": "total-looking"
 },
 "ours": {
  "acres": 135,
  "dissolved": {
   "after": 171,
   "before": 295,
   "copies": 1,
   "key_union": 135,
   "parts": 0,
   "records": 3,
   "summed": 171,
   "tracts": 2
  },
  "manager": "",
  "note": "3 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 295 -> 171 acres",
  "pieces": [
   [
    273238,
    "Moncove Lake State Park",
    125,
    "name"
   ],
   [
    57470,
    "Moncove Lake State Park",
    46,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 46,
 "same_agency": false,
 "score": 6,
 "t": "State Park",
 "verdict": "off"
}
```

## US-7035 Berwind Lake Wildlife Management Area
```json
{
 "cause": "a number 76 parks share from the same sentence (1,400,000 ac): an agency total, not this park",
 "checked": "2026-11-22",
 "handover": [],
 "n": "Berwind Lake Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 101,
  "dissolved": {
   "after": 182,
   "before": 273,
   "copies": 1,
   "key_union": 101,
   "parts": 0,
   "records": 3,
   "summed": 182,
   "tracts": 2
  },
  "manager": "",
  "note": "3 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 273 -> 182 acres",
  "pieces": [
   [
    57453,
    "Berwind Lake Wildlife Management Area",
    91,
    "name"
   ],
   [
    272103,
    "Berwind Lake Wildlife Management Area",
    91,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "same_agency": false,
 "score": 7,
 "t": "Wildlife Management Area",
 "verdict": "unsure"
}
```

## US-12438 Dolly Sods Wilderness Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Dolly Sods Wilderness Area",
 "official": {
  "acres": 17371.0,
  "as": "17,371 acre",
  "clean": false,
  "line": "d Outdoor Ethics Visitor Maps and Guides Recreation Region: Potomac Ranger District Dolly Sods Wilderness The 17,371 acre Dolly Sods Wilderness in the Monongahela National Forest is part of the National Wilderness Preservation Syst",
  "read": "2026-11-22",
  "sent": "The 17,371 acre Dolly Sods Wilderness in the Monongahela National Forest is part of the National Wilderness Preservation System.",
  "url": "https://www.fs.usda.gov/r09/monongahela/recreation/dolly-sods-wilderness",
  "why": "part (a lake, a purchase, a campground…)"
 },
 "ours": {
  "acres": 17777,
  "manager": "",
  "pieces": [
   [
    "wld110",
    "Dolly Sods Wilderness",
    17777,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 2,
 "same_agency": false,
 "score": 8,
 "t": "Wilderness Area",
 "verdict": "agree"
}
```

## US-7013 Nathaniel Mountain Wildlife Management Area
```json
{
 "cause": "a number 76 parks share from the same sentence (1,400,000 ac): an agency total, not this park",
 "checked": "2026-11-22",
 "handover": [],
 "n": "Nathaniel Mountain Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 11135,
  "dissolved": {
   "after": 11135,
   "before": 22269,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 22269 -> 11135 acres",
  "pieces": [
   [
    "sgwva43",
    "Nathaniel Mountain Wildlife Management Area",
    11135,
    "reviewed"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "same_agency": false,
 "score": 7,
 "t": "Wildlife Management Area",
 "verdict": "unsure"
}
```

## US-1807 Carnifex Ferry Battlefield State Park
```json
{
 "cause": "agency smaller: our outline may hold water, a lease or a neighbour tract",
 "checked": "2026-11-22",
 "handover": [],
 "n": "Carnifex Ferry Battlefield State Park",
 "official": {
  "acres": 156.0,
  "as": "156 acre",
  "clean": false,
  "line": "y Battlefield State Park Carnifex Ferry Battlefield State Park Set on the rim of the Gauley River Canyon, the 156-acre Carnifex Ferry Battlefield State Park is an important Civil War battle site. Book Now Learn More Set on the r",
  "read": "2026-11-22",
  "sent": "Set on the rim of the Gauley River Canyon, the 156-acre Carnifex Ferry Battlefield State Park is an important Civil War battle site.",
  "url": "https://wvstateparks.com/park/carnifex-ferry-battlefield-state-park/",
  "why": "total-looking"
 },
 "ours": {
  "acres": 292,
  "dissolved": {
   "after": 292,
   "before": 584,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 584 -> 292 acres",
  "pieces": [
   [
    273227,
    "Carnifex Ferry Battlefield State Park",
    292,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 87,
 "same_agency": false,
 "score": 6,
 "t": "State Park",
 "verdict": "off"
}
```

## US-7015 Short Mountain Wildlife Management Area
```json
{
 "cause": "a number 76 parks share from the same sentence (1,400,000 ac): an agency total, not this park",
 "checked": "2026-11-22",
 "handover": [],
 "n": "Short Mountain Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 8246,
  "dissolved": {
   "after": 8246,
   "before": 16423,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 16423 -> 8246 acres",
  "pieces": [
   [
    273189,
    "Short Mountain Wildlife Management Area",
    8246,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "same_agency": false,
 "score": 7,
 "t": "Wildlife Management Area",
 "verdict": "unsure"
}
```

## US-12035 Dents Run Wildlife Management Area
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-11-22",
 "handover": [],
 "n": "Dents Run Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 1261,
  "dissolved": {
   "after": 1261,
   "before": 2521,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 2521 -> 1261 acres",
  "pieces": [
   [
    273252,
    "Dents Run Wildlife Management Area",
    1261,
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
 "verdict": "unsure"
}
```

## US-12443 Spice Run Wilderness Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Spice Run Wilderness Area",
 "official": {
  "acres": 6030.0,
  "as": "6,030 acre",
  "clean": false,
  "line": "door Ethics Visitor Maps and Guides Recreation Region: White Sulphur Ranger District Spice Run Wilderness The 6,030 acre Spice Run Wilderness is located south of Calvin Price State Forest. The area is about 2 miles in length and 3",
  "read": "2026-11-22",
  "sent": "The 6,030 acre Spice Run Wilderness is located south of Calvin Price State Forest.",
  "url": "https://www.fs.usda.gov/r09/monongahela/recreation/spice-run-wilderness",
  "why": "total-looking"
 },
 "ours": {
  "acres": 6037,
  "manager": "",
  "pieces": [
   [
    "wld411",
    "Spice Run Wilderness",
    6037,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 0,
 "same_agency": false,
 "score": 8,
 "t": "Wilderness Area",
 "verdict": "agree"
}
```

## US-7046 Beech Fork Lake Wildlife Management Area
```json
{
 "cause": "a number 76 parks share from the same sentence (1,400,000 ac): an agency total, not this park",
 "checked": "2026-11-22",
 "handover": [],
 "n": "Beech Fork Lake Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 9480,
  "dissolved": {
   "after": 9480,
   "before": 18956,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 18956 -> 9480 acres",
  "pieces": [
   [
    272109,
    "Beech Fork Lake Wildlife Management Area",
    9480,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "same_agency": false,
 "score": 7,
 "t": "Wildlife Management Area",
 "verdict": "unsure"
}
```
