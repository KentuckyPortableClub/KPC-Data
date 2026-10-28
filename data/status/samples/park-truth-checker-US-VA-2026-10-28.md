# park truth checker: US-VA random sample of 12 (2026-10-28; seed = date + area, same rows for everyone)

Source file: `data/truth/US-VA.json`

## US-0730 Cedar Creek and Belle Grove National Historical Park
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "n": "Cedar Creek and Belle Grove National Historical Park",
 "official": null,
 "ours": {
  "acres": 240,
  "manager": "",
  "pieces": [
   [
    3190,
    "Cedar Creek and Belle Grove National Historical Park",
    128,
    "name"
   ],
   [
    "sgvae491102",
    "Cedar Creek and Belle Grove National Historical Park",
    43,
    "name"
   ],
   [
    "sgvae491827",
    "Cedar Creek and Belle Grove National Historical Park",
    15,
    "name"
   ],
   [
    "sgvae491103",
    "Cedar Creek and Belle Grove National Historical Park",
    12,
    "name"
   ],
   [
    "sgvae491514",
    "Cedar Creek and Belle Grove National Historical Park",
    12,
    "name"
   ],
   [
    "sgvae491843",
    "Cedar Creek and Belle Grove National Historical Park",
    10,
    "name"
   ],
   [
    "sgvae491113",
    "Cedar Creek and Belle Grove National Historical Park",
    8,
    "name"
   ],
   [
    "sgvae491798",
    "Cedar Creek and Belle Grove National Historical Park",
    5,
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
 "t": "National Historical Park",
 "verdict": "no size on page"
}
```

## US-9949 Mountain Lake Wilderness Area
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "n": "Mountain Lake Wilderness Area",
 "official": null,
 "ours": {
  "acres": 29890,
  "manager": "",
  "pieces": [
   [
    "wld288",
    "Mountain Lake Wilderness",
    16585,
    "name"
   ],
   [
    "sgvae500353",
    "Mountain Lake NF Wilderness Area",
    13305,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "Wilderness Area",
 "verdict": "no size on page"
}
```

## US-0717 Fredericksburg and Spotsylvania National Military Park
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "n": "Fredericksburg and Spotsylvania National Military Park",
 "official": null,
 "ours": {
  "acres": 7640,
  "manager": "",
  "pieces": [
   [
    3284,
    "Fredericksburg and Spotsylvania County Battlefields Memorial National Military Park",
    7640,
    "reviewed"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 4,
 "t": "National Military Park",
 "verdict": "no size on page"
}
```

## US-5506 Browne State Forest
```json
{
 "cause": "our union: one of our pieces alone matches the agency (double count?)",
 "checked": "2026-10-28",
 "handover": [
  {
   "date_hint": null,
   "kind": "transfer",
   "line": "to this property (in the courthouse records) dates back to October 13, 1892, when Andrew C. Browne transferred the property to James R. Browne of Baltimore, Maryland. How long the property was in the Browne family before that is unknown, but a gravesite adjacent to",
   "owner_now": "James R",
   "src": "https://dof.virginia.gov/education-and-recreation/state-forests/virginia-state-forests/browne-state-forest/",
   "why": "the park's page (data/parkinfo)"
  }
 ],
 "n": "Browne State Forest",
 "official": {
  "acres": 128.0,
  "as": "128 acre",
  "clean": true,
  "line": "am Area Contacts Find a Forester Upcoming Events Browne State Forest &#xA0; Overview Browne State Forest is a 128-acre property in Essex County, consisting of mostly loblolly pine forest, with some wetlands along Dragon Run Swam",
  "read": "2026-10-28",
  "url": "https://dof.virginia.gov/education-and-recreation/state-forests/virginia-state-forests/browne-state-forest/",
  "why": "clean total"
 },
 "ours": {
  "acres": 516,
  "manager": "",
  "pieces": [
   [
    10578,
    "Browne State Forest",
    129,
    "name"
   ],
   [
    268712,
    "Browne State Forest",
    129,
    "name"
   ],
   [
    "sgvaa31",
    "Browne State Forest",
    129,
    "name"
   ],
   [
    "sgvae486663",
    "Browne State Forest",
    129,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": "James R",
 "pct": 303,
 "same_agency": false,
 "score": 6,
 "t": "State Forest",
 "verdict": "off"
}
```

## US-9927 Charlotte State Forest
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 2,531 acres, no total words near it)",
 "checked": "2026-10-28",
 "handover": [],
 "n": "Charlotte State Forest",
 "official": {
  "acres": 2531.0,
  "as": "2,531 acres",
  "clean": false,
  "line": "roperties of Stanley Land and Lumber were purchased in 2019 by The Conservation Fund, and in 2020, a portion (2,531 acres) of the properties were sold to the Commonwealth of Virginia &#x2013; Department of Forestry for what would b",
  "read": "2026-10-28",
  "url": "https://dof.virginia.gov/education-and-recreation/state-forests/virginia-state-forests/charlotte-state-forest/",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 22196,
  "manager": "",
  "pieces": [
   [
    "sgvaa27",
    "Charlotte State Forest",
    6503,
    "name"
   ],
   [
    270714,
    "Charlotte State Forest",
    5002,
    "name"
   ],
   [
    "sgvae487043",
    "Charlotte State Forest",
    2531,
    "name"
   ],
   [
    57425,
    "Charlotte State Forest",
    2529,
    "name"
   ],
   [
    57424,
    "Charlotte State Forest",
    2474,
    "name"
   ],
   [
    "sgvae487046",
    "Charlotte State Forest",
    2474,
    "name"
   ],
   [
    "sgvae487066",
    "Charlotte State Forest",
    360,
    "name"
   ],
   [
    "sgvae487068",
    "Charlotte State Forest",
    323,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 777,
 "same_agency": false,
 "score": 7,
 "t": "State Forest",
 "verdict": "unsure"
}
```

## US-1320 Southwest Virginia Museum State Park
```json
{
 "cause": "agency smaller: our outline may hold water, a lease or a neighbour tract",
 "checked": "2026-10-28",
 "handover": [],
 "n": "Southwest Virginia Museum State Park",
 "official": {
  "acres": 1.5,
  "as": "1.5 acres",
  "clean": false,
  "line": "anoke, 4 hours; Knoxville, Tenn., 2 hours; Lexington, Ky., 2.5 hours; Winston-Salem, N.C., 3 hours. Park Size 1.5 acres. Share this page Follow us Cabins, camping OVERNIGHT FACILITIES Poplar Hill Cottage is the perfect mountain g",
  "read": "2026-10-28",
  "url": "https://www.dcr.virginia.gov/state-parks/southwest-virginia-museum",
  "why": "total-looking"
 },
 "ours": {
  "acres": 5,
  "manager": "",
  "pieces": [
   [
    271176,
    "Southwest Virginia Museum Historical State Park",
    1,
    "name"
   ],
   [
    "sgvad328",
    "Southwest Virginia Museum Historical State Park",
    1,
    "name"
   ],
   [
    "sgvad357",
    "Southwest Virginia Museum Historical State Park",
    1,
    "name"
   ],
   [
    "sgvae487052",
    "Southwest Virginia Museum State Park",
    1,
    "name"
   ],
   [
    "sgvae487081",
    "Southwest Virginia Museum State Park",
    1,
    "name"
   ],
   [
    54668,
    "Southwest Virginia Museum State Park",
    0,
    "name"
   ],
   [
    54669,
    "Southwest Virginia Museum State Park",
    0,
    "name"
   ],
   [
    54670,
    "Southwest Virginia Museum State Park",
    0,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 17
 },
 "owner_now": null,
 "pct": 233,
 "same_agency": false,
 "score": 6,
 "t": "State Park",
 "verdict": "off"
}
```

## US-0560 Back Bay National Wildlife Refuge
```json
{
 "cause": "agency smaller: our outline may hold water, a lease or a neighbour tract",
 "checked": "2026-10-28",
 "handover": [],
 "n": "Back Bay National Wildlife Refuge",
 "official": {
  "acres": 4589.0,
  "as": "4,589 acre",
  "clean": true,
  "line": "ed on June 6, 1938 in the southeastern corner of the City of Virginia Beach (then Princess Anne County), as a 4,589-acre refuge. The original 1938 Executive Order established Back Bay NWR “….as a refuge and breeding ground for mig",
  "read": "2026-10-28",
  "url": "https://www.fws.gov/refuge/back-bay/about-us",
  "why": "clean total"
 },
 "ours": {
  "acres": 26226,
  "manager": "",
  "pieces": [
   [
    4530,
    "Back Bay National Wildlife Refuge",
    8798,
    "name"
   ],
   [
    3600,
    "Back Bay National Wildlife Refuge",
    8658,
    "name"
   ],
   [
    "sgvae491104",
    "Back Bay National Wildlife Refuge",
    8605,
    "name"
   ],
   [
    "sgvae491100",
    "Back Bay National Wildlife Refuge",
    46,
    "name"
   ],
   [
    "sgvae491101",
    "Back Bay National Wildlife Refuge",
    37,
    "name"
   ],
   [
    "sgvae491099",
    "Back Bay National Wildlife Refuge",
    28,
    "name"
   ],
   [
    "sgvae491483",
    "Back Bay National Wildlife Refuge",
    18,
    "name"
   ],
   [
    "sgvae491098",
    "Back Bay National Wildlife Refuge",
    10,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 471,
 "same_agency": false,
 "score": 6,
 "t": "National Wildlife Refuge",
 "verdict": "off"
}
```

## US-1298 False Cape State Park
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 4,321 acres, no total words near it)",
 "checked": "2026-10-28",
 "handover": [],
 "n": "False Cape State Park",
 "official": {
  "acres": 4321.0,
  "as": "4,321 acres",
  "clean": false,
  "line": "Drive Time: From Virginia Beach's oceanfront to Little Island city parking lot is about 40 minutes. Park Size 4,321 acres. Beach Size: 5.9 miles of beachfront, extending to the North Carolina line. Share this page Follow us Cabins,",
  "read": "2026-10-28",
  "url": "https://www.dcr.virginia.gov/state-parks/false-cape",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 11659,
  "manager": "",
  "pieces": [
   [
    270622,
    "False Cape State Park",
    3866,
    "name"
   ],
   [
    "sgvad144",
    "False Cape State Park",
    3496,
    "name"
   ],
   [
    "sgvae486601",
    "False Cape State Park",
    3496,
    "name"
   ],
   [
    "sgvad153",
    "False Cape State Park",
    251,
    "name"
   ],
   [
    "sgvae486610",
    "False Cape State Park",
    251,
    "name"
   ],
   [
    "sgvad149",
    "False Cape State Park",
    54,
    "name"
   ],
   [
    "sgvae486606",
    "False Cape State Park",
    54,
    "name"
   ],
   [
    54564,
    "False Cape State Park",
    41,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 2
 },
 "owner_now": null,
 "pct": 170,
 "same_agency": false,
 "score": 6,
 "t": "State Park",
 "verdict": "unsure"
}
```

## US-1293 Caledon State Park
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 2,587 acres, no total words near it)",
 "checked": "2026-10-28",
 "handover": [],
 "n": "Caledon State Park",
 "official": {
  "acres": 2587.0,
  "as": "2,587 acres",
  "clean": false,
  "line": "r, 30 minutes; Tidewater/Norfolk/Virginia Beach, 3 hours, 30 minutes; Roanoke, 3 hours, 30 minutes. Park Size 2,587 acres. Share this page Follow us Cabins, camping OVERNIGHT FACILITIES Enjoy a unique and peaceful camping experienc",
  "read": "2026-10-28",
  "url": "https://www.dcr.virginia.gov/state-parks/caledon",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 11337,
  "manager": "",
  "pieces": [
   [
    "sgvae486621",
    "Caledon State Park",
    2587,
    "name"
   ],
   [
    54551,
    "Caledon State Park",
    2574,
    "name"
   ],
   [
    270613,
    "Caledon State Park",
    2573,
    "name"
   ],
   [
    "sgvad390",
    "Caledon State Park",
    2529,
    "name"
   ],
   [
    "sgvad405",
    "Caledon State Park",
    276,
    "name"
   ],
   [
    "sgvae487161",
    "Caledon State Park",
    276,
    "name"
   ],
   [
    "sgvad406",
    "Caledon State Park",
    195,
    "name"
   ],
   [
    "sgvae487163",
    "Caledon State Park",
    195,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 338,
 "same_agency": false,
 "score": 7,
 "t": "State Park",
 "verdict": "unsure"
}
```

## US-7789 Chub Sandhill State Natural Area
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-10-28",
 "handover": [],
 "n": "Chub Sandhill State Natural Area",
 "official": {
  "acres": 66000.0,
  "as": "66,000 acres",
  "clean": false,
  "line": "ved from voluntary contributions through a state income tax check-off. Sixty nine preserves encompassing over 66,000 acres now comprise the Virginia Natural Area Preserves System . Natural area conservation does not end with land pr",
  "read": "2026-10-28",
  "url": "https://www.dcr.virginia.gov/natural-heritage/mission",
  "why": "total-looking"
 },
 "ours": {
  "acres": 4272,
  "manager": "",
  "pieces": [
   [
    "sgvab18",
    "Chub Sandhill",
    1066,
    "name"
   ],
   [
    270553,
    "Chub Sandhill State Natural Area Preserve",
    513,
    "name"
   ],
   [
    54424,
    "Chub Sandhill State Natural Area Preserve",
    467,
    "words"
   ],
   [
    "sgvae486828",
    "Chub Sandhill State Natural Area Preserve",
    467,
    "words"
   ],
   [
    54421,
    "Chub Sandhill State Natural Area Preserve",
    391,
    "words"
   ],
   [
    270551,
    "Chub Sandhill State Natural Area Preserve",
    391,
    "name"
   ],
   [
    "sgvae486695",
    "Chub Sandhill State Natural Area Preserve",
    387,
    "words"
   ],
   [
    54422,
    "Chub Sandhill State Natural Area Preserve",
    166,
    "words"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 94,
 "same_agency": false,
 "score": 6,
 "t": "State Natural Area",
 "verdict": "off"
}
```

## US-5526 Zoar State Forest
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 4 acre, no total words near it)",
 "checked": "2026-10-28",
 "handover": [],
 "n": "Zoar State Forest",
 "official": {
  "acres": 4.0,
  "as": "4 acre",
  "clean": false,
  "line": "ding opportunities in education and recreation, and a variety of wildlife habitats. Water resources include a 4-acre pond, 2,000 feet of waterfront on Herring Creek, and 6,600 feet of waterfront on the Mattaponi River. The pro",
  "read": "2026-10-28",
  "url": "https://dof.virginia.gov/education-and-recreation/state-forests/virginia-state-forests/zoar-state-forest/",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 1578,
  "manager": "",
  "pieces": [
   [
    "sgvaa52",
    "Zoar State Forest",
    378,
    "name"
   ],
   [
    "sgvae486638",
    "Zoar State Forest",
    378,
    "name"
   ],
   [
    57450,
    "Zoar State Forest",
    376,
    "name"
   ],
   [
    270435,
    "Zoar State Forest",
    376,
    "name"
   ],
   [
    "sgvae486637",
    "Zoar State Forest",
    70,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 39350,
 "same_agency": false,
 "score": 6,
 "t": "State Forest",
 "verdict": "unsure"
}
```

## US-1296 Douthat State Park
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 6,500 acres, no total words near it)",
 "checked": "2026-10-28",
 "handover": [],
 "n": "Douthat State Park",
 "official": {
  "acres": 6500.0,
  "as": "6,500 acres",
  "clean": false,
  "line": "n Roanoke. Also be sure to tour the Dixie Caverns. White Sulphur Springs, W. Va .: The Greenbrier, nestled in 6,500 acres of the Alleghany Mountains, features golf, tennis, horseback riding, mineral baths and spacious accommodation",
  "read": "2026-10-28",
  "url": "https://www.dcr.virginia.gov/state-parks/douthat",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 18212,
  "manager": "",
  "pieces": [
   [
    "sgvad175",
    "Douthat State Park",
    4502,
    "name"
   ],
   [
    "sgvae486660",
    "Douthat State Park",
    4502,
    "name"
   ],
   [
    270618,
    "Douthat State Park",
    4499,
    "name"
   ],
   [
    54560,
    "Douthat State Park",
    4497,
    "name"
   ],
   [
    54561,
    "Douthat State Park",
    53,
    "name"
   ],
   [
    270619,
    "Douthat State Park",
    53,
    "name"
   ],
   [
    "sgvad16",
    "Douthat State Park",
    53,
    "name"
   ],
   [
    "sgvae486268",
    "Douthat State Park",
    53,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 180,
 "same_agency": false,
 "score": 7,
 "t": "State Park",
 "verdict": "unsure"
}
```
