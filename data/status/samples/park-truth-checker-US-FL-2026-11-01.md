# park truth checker: US-FL random sample of 12 (2026-11-01; seed = date + area, same rows for everyone)

Source file: `data/truth/US-FL.json`

## US-8370 Seminole Ranch State Conservation Area
```json
{
 "cause": "agency smaller: our outline may hold water, a lease or a neighbour tract",
 "checked": "2026-11-01",
 "handover": [],
 "n": "Seminole Ranch State Conservation Area",
 "official": {
  "acres": 6000.0,
  "as": "6,000 acres",
  "clean": true,
  "line": "poonbills, white pelicans, southern bald eagles and sandhill cranes. Recreational activities The southwestern 6,000 acres of this conservation area comprise the Seminole Ranch Wildlife Management Area, which is seasonally hunted. Y",
  "read": "2026-11-01",
  "sent": "The southwestern 6,000 acres of this conservation area comprise the Seminole Ranch Wildlife Management Area, which is seasonally hunted.",
  "url": "https://www.sjrwmd.com/lands/recreation/seminole-ranch/",
  "why": "clean total"
 },
 "ours": {
  "acres": 29545,
  "dissolved": {
   "after": 29545,
   "before": 59042,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 59042 -> 29545 acres",
  "pieces": [
   [
    "sgfle10304",
    "Seminole Ranch Conservation Area",
    29545,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 392,
 "same_agency": false,
 "score": 6,
 "t": "State Conservation Area",
 "verdict": "off"
}
```

## US-3622 Fort Mose State Park
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-01",
 "n": "Fort Mose State Park",
 "official": null,
 "ours": {
  "acres": 41,
  "dissolved": {
   "after": 41,
   "before": 123,
   "copies": 2,
   "parts": 0,
   "records": 3,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 123 -> 41 acres",
  "pieces": [
   [
    191807,
    "Fort Mose Historic State Park",
    41,
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
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-6305 Guana River Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Guana River Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 9139,
  "manager": "",
  "pieces": [
   [
    191742,
    "Guana River Wildlife Management Area",
    9139,
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
 "t": "Wildlife Management Area",
 "verdict": "no size on page"
}
```

## US-5220 Flying Eagle Preserve State Conservation Area
```json
{
 "cause": "agency smaller: our outline may hold water, a lease or a neighbour tract",
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-01",
 "n": "Flying Eagle Preserve State Conservation Area",
 "official": {
  "acres": 10950.0,
  "as": "10950 Acres",
  "clean": false,
  "line": "ee River. Park Details Street Address 11080 East Moccasin Slough Road Inverness , FL 34450 United States Size 10950 Acres Hours of Operation District lands shall be open to the public from 30 minutes prior to sunrise until 30 minut",
  "read": "2026-10-28",
  "url": "https://www.swfwmd.state.fl.us/recreation/flying-eagle-preserve",
  "why": "total-looking"
 },
 "ours": {
  "acres": 16441,
  "dissolved": {
   "after": 16441,
   "before": 32779,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 32779 -> 16441 acres",
  "pieces": [
   [
    190295,
    "Flying Eagle Ranch",
    16441,
    "reviewed"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 50,
 "same_agency": false,
 "score": 6,
 "t": "State Conservation Area",
 "verdict": "off"
}
```

## US-8351 Heart Island State Conservation Area
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-11-01",
 "handover": [],
 "n": "Heart Island State Conservation Area",
 "official": null,
 "ours": {
  "acres": 14249,
  "family_fold": "layers {'padus': 14249, 'sgfle': 13645}: one land in 2 layers, the padus copy used (13,645 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    190335,
    "Heart Island Conservation Area",
    14249,
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
 "t": "State Conservation Area",
 "verdict": "unsure"
}
```

## US-8330 Econfina Creek Water Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Econfina Creek Water Management Area",
 "official": null,
 "ours": {
  "acres": 42310,
  "manager": "",
  "pieces": [
   [
    190220,
    "Econfina Creek Water Management Area",
    42310,
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
 "t": "Water Management Area",
 "verdict": "no size on page"
}
```

## US-4634 Picayune Strand State Forest
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-01",
 "n": "Picayune Strand State Forest",
 "official": null,
 "ours": {
  "acres": 73992,
  "dissolved": {
   "after": 73992,
   "before": 147852,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 147852 -> 73992 acres",
  "pieces": [
   [
    191653,
    "Picayune Strand State Forest",
    73992,
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

## US-8372 Stokes Landing State Conservation Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Stokes Landing State Conservation Area",
 "official": null,
 "ours": {
  "acres": 281,
  "family_fold": "layers {'sgfle': 281, 'padus': 274}: one land in 2 layers, the sgfle copy used (274 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgfle10354",
    "Stokes Landing Conservation Area",
    281,
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
 "t": "State Conservation Area",
 "verdict": "no size on page"
}
```

## US-1880 Honeymoon Island State Park
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-01",
 "n": "Honeymoon Island State Park",
 "official": null,
 "ours": {
  "acres": 2833,
  "dissolved": {
   "after": 2833,
   "before": 5658,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 5658 -> 2833 acres",
  "pieces": [
   [
    191899,
    "Honeymoon Island State Park",
    2833,
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

## US-3609 Bulow Plantation Ruins State Park
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-01",
 "n": "Bulow Plantation Ruins State Park",
 "official": null,
 "ours": {
  "acres": 148,
  "dissolved": {
   "after": 148,
   "before": 444,
   "copies": 2,
   "parts": 0,
   "records": 3,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 444 -> 148 acres",
  "pieces": [
   [
    191803,
    "Bulow Plantation Ruins Historic State Park",
    148,
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

## US-8709 Turner Bridge State Conservation Area
```json
{
 "cause": "our union: one of our pieces alone matches the agency (double count?)",
 "checked": "2026-11-01",
 "handover": [],
 "n": "Turner Bridge State Conservation Area",
 "official": {
  "acres": 207.0,
  "as": "207 acres",
  "clean": false,
  "line": "dpecker Road) 2 miles, turn right on NE 38th Trail to the parking area at the boat ramp. Size Turner Bridge – 207 acres Allowable Activities = Featured Boat Ramp Canoe Launch Fishing Hunting Picnic Area Wildlife Viewing Size TURN",
  "read": "2026-11-01",
  "sent": "Turner Bridge – 207 acres",
  "url": "https://map.mysuwanneeriver.com/tracts/turner-bridge-222/",
  "why": "total-looking"
 },
 "ours": {
  "acres": 349,
  "manager": "",
  "pieces": [
   [
    "sgfld7",
    "TURNER BRIDGE",
    207,
    "name"
   ],
   [
    "sgfld1038",
    "TURNER BRIDGE",
    74,
    "name"
   ],
   [
    "sgfld1500",
    "TURNER BRIDGE",
    61,
    "name"
   ],
   [
    "sgfld1499",
    "TURNER BRIDGE PARK",
    5,
    "name"
   ],
   [
    "sgfld730",
    "TURNER BRIDGE",
    2,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 69,
 "same_agency": false,
 "score": 6,
 "t": "State Conservation Area",
 "verdict": "off"
}
```

## US-4632 Myakka State Forest
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-01",
 "n": "Myakka State Forest",
 "official": null,
 "ours": {
  "acres": 8626,
  "family_fold": "layers {'sgflb': 8626, 'padus': 8232, 'fnl': 137}: one land in 3 layers, the sgflb copy used (8,369 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgflb23",
    "Myakka State Forest",
    8626,
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
