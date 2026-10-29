# park truth checker: US-WV random sample of 12 (2026-10-29; seed = date + area, same rows for everyone)

Source file: `data/truth/US-WV.json`

## US-0632 Monongahela National Forest
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-10-29",
 "n": "Monongahela National Forest",
 "official": null,
 "ours": {
  "acres": 921100,
  "manager": "",
  "pieces": [
   [
    3069,
    "Monongahela National Forest",
    921100,
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
 "t": "National Forest",
 "verdict": "no size on page"
}
```

## US-7002 Lewis Wetzel Wildlife Management Area
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-10-29",
 "handover": [],
 "n": "Lewis Wetzel Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 26969,
  "manager": "",
  "pieces": [
   [
    273168,
    "Lewis Wetzel Wildlife Management Area",
    13490,
    "name"
   ],
   [
    "sgwva82",
    "Lewis Wetzel Wildlife Management Area",
    13479,
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

## US-1817 Moncove Lake State Park
```json
{
 "cause": "agency smaller: our outline may hold water, a lease or a neighbour tract",
 "checked": "2026-10-29",
 "handover": [],
 "n": "Moncove Lake State Park",
 "official": {
  "acres": 250.0,
  "as": "250 acre",
  "clean": false,
  "line": "w Home » Explore Parks » Moncove Lake State Park Moncove Lake State Park Hidden among the hills is a peaceful 250-acre park with a 500-acre wildlife management area. Moncove Lake State Park resides on the southeastern edge of We",
  "read": "2026-10-29",
  "url": "https://wvstateparks.com/park/moncove-lake-state-park/",
  "why": "total-looking"
 },
 "ours": {
  "acres": 295,
  "manager": "",
  "pieces": [
   [
    273238,
    "Moncove Lake State Park",
    125,
    "name"
   ],
   [
    "sgwvc32",
    "Moncove Lake State Park",
    124,
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
 "pct": 18,
 "same_agency": false,
 "score": 6,
 "t": "State Park",
 "verdict": "off"
}
```

## US-12045 Sandy Creek Wildlife Management Area
```json
{
 "cause": "a number 20 parks share from one page (10 ac): an agency total, not this park",
 "checked": "2026-10-29",
 "handover": [],
 "n": "Sandy Creek Wildlife Management Area",
 "note": "the agency figure may cover several states; our outline may be this state's share only",
 "official": null,
 "ours": {
  "acres": 4684,
  "manager": "",
  "pieces": [
   [
    273187,
    "Sandy Creek Wildlife Management Area",
    2420,
    "name"
   ],
   [
    "sgwva117",
    "Sandy Creek Wildlife Management Area",
    2264,
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

## US-1798 Babcock State Park
```json
{
 "cause": "our union: one of our pieces alone matches the agency (double count?)",
 "checked": "2026-10-29",
 "handover": [],
 "n": "Babcock State Park",
 "official": {
  "acres": 4127.0,
  "as": "4,127 acres",
  "clean": false,
  "line": "» Babcock State Park Babcock State Park One of West Virginia’s most iconic locations, Babcock State Park has 4,127 acres of stunning scenery. Located 20 miles southeast of the New River Gorge Bridge, the park is known for the Glad",
  "read": "2026-10-29",
  "url": "https://wvstateparks.com/park/babcock-state-park/",
  "why": "total-looking"
 },
 "ours": {
  "acres": 8120,
  "manager": "",
  "pieces": [
   [
    273219,
    "Babcock State Park",
    4062,
    "name"
   ],
   [
    "sgwvc21",
    "Babcock State Park",
    4058,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 97,
 "same_agency": false,
 "score": 6,
 "t": "State Park",
 "verdict": "off"
}
```

## US-5589 Seneca State Forest
```json
{
 "cause": "the agency figure may cover several states; our outline may be this state's share only",
 "checked": "2026-10-29",
 "handover": [],
 "n": "Seneca State Forest",
 "note": "the agency figure may cover several states; our outline may be this state's share only",
 "official": {
  "acres": 12884.0,
  "as": "12,884 acres",
  "clean": false,
  "line": "Virginia's state forests, Seneca is located in rugged Pocahontas County bordering the Greenbrier River. With 12,884 acres of lush woodlands to explore, the forest offers a variety of recreational opportunities, including boating in",
  "read": "2026-10-29",
  "url": "https://wvstateparks.com/park/seneca-state-forest/",
  "why": "total-looking"
 },
 "ours": {
  "acres": 25703,
  "manager": "",
  "pieces": [
   [
    "sgwvb5",
    "Seneca State Forest",
    12858,
    "name"
   ],
   [
    273138,
    "Seneca State Forest",
    12845,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 99,
 "same_agency": false,
 "score": 7,
 "t": "State Forest",
 "verdict": "unsure"
}
```

## US-5585 Coopers Rock State Forest
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-10-29",
 "handover": [],
 "n": "Coopers Rock State Forest",
 "official": null,
 "ours": {
  "acres": 26107,
  "manager": "",
  "pieces": [
   [
    273134,
    "Coopers Rock State Forest",
    13057,
    "name"
   ],
   [
    "sgwvb1",
    "Coopers Rock State Forest",
    13050,
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

## US-1797 Audra State Park
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Audra State Park",
 "official": null,
 "ours": {
  "acres": 688,
  "manager": "",
  "pieces": [
   [
    273218,
    "Audra State Park",
    344,
    "name"
   ],
   [
    "sgwvc35",
    "Audra State Park",
    344,
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
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-7062 Ritchie Mines Wildlife Management Area
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-10-29",
 "handover": [],
 "n": "Ritchie Mines Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 13513,
  "manager": "",
  "pieces": [
   [
    "sgwva77",
    "Ritchie Mines Wildlife Management Area",
    6774,
    "name"
   ],
   [
    273184,
    "Ritchie Mines Wildlife Management Area",
    6739,
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

## US-12032 Burning Springs Wildlife Management Area
```json
{
 "cause": "a number 20 parks share from one page (10 ac): an agency total, not this park",
 "checked": "2026-10-29",
 "handover": [],
 "n": "Burning Springs Wildlife Management Area",
 "note": "the agency figure may cover several states; our outline may be this state's share only",
 "official": null,
 "ours": {
  "acres": 4407,
  "manager": "",
  "pieces": [
   [
    273148,
    "Burning Springs Wildlife Management Area",
    2209,
    "name"
   ],
   [
    "sgwva115",
    "Burning Springs Wildlife Management Area",
    2198,
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

## US-1812 Fairfax Stone State Park
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Fairfax Stone State Park",
 "official": null,
 "ours": {
  "acres": 13,
  "manager": "",
  "pieces": [
   [
    57469,
    "Fairfax Stone State Park",
    4,
    "name"
   ],
   [
    273233,
    "Fairfax Stone State Park",
    4,
    "name"
   ],
   [
    "sgwvc4",
    "Fairfax Stone State Park",
    4,
    "name"
   ],
   [
    9800,
    "Fairfax Stone State Park",
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
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-7038 Horse Creek Lake Wildlife Management Area
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-10-29",
 "handover": [],
 "n": "Horse Creek Lake Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 94,
  "manager": "",
  "pieces": [
   [
    272123,
    "Horse Creek Wildlife Management Area",
    47,
    "name"
   ],
   [
    "sgwva32",
    "Horse Creek Wildlife Management Area",
    47,
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
