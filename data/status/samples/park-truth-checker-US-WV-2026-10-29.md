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
 "cause": "a number 76 parks share from one page (1,400,000 ac): an agency total, not this park",
 "checked": "2026-10-29",
 "handover": [],
 "n": "Lewis Wetzel Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 13490,
  "dissolved": {
   "after": 13490,
   "before": 26969,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 26969 -> 13490 acres",
  "pieces": [
   [
    273168,
    "Lewis Wetzel Wildlife Management Area",
    13490,
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
 "checked": "2026-10-29",
 "handover": [],
 "n": "Moncove Lake State Park",
 "official": {
  "acres": 250.0,
  "as": "250 acre",
  "clean": false,
  "line": "w Home » Explore Parks » Moncove Lake State Park Moncove Lake State Park Hidden among the hills is a peaceful 250-acre park with a 500-acre wildlife management area. Moncove Lake State Park resides on the southeastern edge of We",
  "read": "2026-10-29",
  "sent": "Hidden among the hills is a peaceful 250-acre park with a 500-acre wildlife management area.",
  "url": "https://wvstateparks.com/park/moncove-lake-state-park/",
  "why": "total-looking"
 },
 "ours": {
  "acres": 171,
  "dissolved": {
   "after": 171,
   "before": 295,
   "copies": 1,
   "parts": 0,
   "records": 3,
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
 "pct": 32,
 "same_agency": false,
 "score": 6,
 "t": "State Park",
 "verdict": "off"
}
```

## US-12045 Sandy Creek Wildlife Management Area
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-10-29",
 "handover": [],
 "n": "Sandy Creek Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 2420,
  "family_fold": "layers {'padus': 2420, 'sgwva': 2264}: one land in 2 layers, the padus copy used (2,264 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    273187,
    "Sandy Creek Wildlife Management Area",
    2420,
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

## US-1798 Babcock State Park
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Babcock State Park",
 "official": {
  "acres": 4127.0,
  "as": "4,127 acres",
  "clean": false,
  "line": "» Babcock State Park Babcock State Park One of West Virginia’s most iconic locations, Babcock State Park has 4,127 acres of stunning scenery. Located 20 miles southeast of the New River Gorge Bridge, the park is known for the Glad",
  "read": "2026-10-29",
  "sent": "One of West Virginia’s most iconic locations, Babcock State Park has 4,127 acres of stunning scenery.",
  "url": "https://wvstateparks.com/park/babcock-state-park/",
  "why": "total-looking"
 },
 "ours": {
  "acres": 4062,
  "dissolved": {
   "after": 4062,
   "before": 8120,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 8120 -> 4062 acres",
  "pieces": [
   [
    273219,
    "Babcock State Park",
    4062,
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
 "t": "State Park",
 "verdict": "agree"
}
```

## US-5589 Seneca State Forest
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Seneca State Forest",
 "official": {
  "acres": 12884.0,
  "as": "12,884 acres",
  "clean": false,
  "line": "Virginia's state forests, Seneca is located in rugged Pocahontas County bordering the Greenbrier River. With 12,884 acres of lush woodlands to explore, the forest offers a variety of recreational opportunities, including boating in",
  "read": "2026-10-29",
  "sent": "With 12,884 acres of lush woodlands to explore, the forest offers a variety of recreational opportunities, including boating in Seneca Lake and hiking or biking 23 miles of trails.",
  "url": "https://wvstateparks.com/park/seneca-state-forest/",
  "why": "total-looking"
 },
 "ours": {
  "acres": 12858,
  "dissolved": {
   "after": 12858,
   "before": 25703,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 25703 -> 12858 acres",
  "pieces": [
   [
    "sgwvb5",
    "Seneca State Forest",
    12858,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 0,
 "same_agency": false,
 "score": 8,
 "t": "State Forest",
 "verdict": "agree"
}
```

## US-5585 Coopers Rock State Forest
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Coopers Rock State Forest",
 "official": null,
 "ours": {
  "acres": 13057,
  "dissolved": {
   "after": 13057,
   "before": 26107,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 26107 -> 13057 acres",
  "pieces": [
   [
    273134,
    "Coopers Rock State Forest",
    13057,
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
 "verdict": "no size on page"
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
  "acres": 344,
  "dissolved": {
   "after": 344,
   "before": 688,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 688 -> 344 acres",
  "pieces": [
   [
    273218,
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
 "cause": "a number 76 parks share from one page (1,400,000 ac): an agency total, not this park",
 "checked": "2026-10-29",
 "handover": [],
 "n": "Ritchie Mines Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 6774,
  "dissolved": {
   "after": 6774,
   "before": 13513,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 13513 -> 6774 acres",
  "pieces": [
   [
    "sgwva77",
    "Ritchie Mines Wildlife Management Area",
    6774,
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

## US-12032 Burning Springs Wildlife Management Area
```json
{
 "cause": "a number 16 parks share from one page (217 ac): an agency total, not this park",
 "checked": "2026-10-29",
 "handover": [],
 "n": "Burning Springs Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 2209,
  "dissolved": {
   "after": 2209,
   "before": 4407,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 4407 -> 2209 acres",
  "pieces": [
   [
    273148,
    "Burning Springs Wildlife Management Area",
    2209,
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
  "acres": 9,
  "dissolved": {
   "after": 9,
   "before": 13,
   "copies": 1,
   "parts": 0,
   "records": 4,
   "tracts": 3
  },
  "manager": "",
  "note": "4 joined records = 3 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 13 -> 9 acres",
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
 "cause": "a number 76 parks share from one page (1,400,000 ac): an agency total, not this park",
 "checked": "2026-10-29",
 "handover": [],
 "n": "Horse Creek Lake Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 47,
  "dissolved": {
   "after": 47,
   "before": 94,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 94 -> 47 acres",
  "pieces": [
   [
    272123,
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
 "same_agency": false,
 "score": 7,
 "t": "Wildlife Management Area",
 "verdict": "unsure"
}
```
