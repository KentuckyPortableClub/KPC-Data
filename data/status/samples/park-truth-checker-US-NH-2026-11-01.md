# park truth checker: US-NH random sample of 12 (2026-11-01; seed = date + area, same rows for everyone)

Source file: `data/truth/US-NH.json`

## US-8020 Franklin Pierce Homestead State Historic Site
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Franklin Pierce Homestead State Historic Site",
 "official": null,
 "ours": {
  "acres": 10,
  "dissolved": {
   "after": 14,
   "before": 28,
   "copies": 1,
   "key_union": 10,
   "parts": 0,
   "records": 2,
   "summed": 14,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 28 -> 14 acres",
  "pieces": [
   [
    56873,
    "Franklin Pierce Homestead Historic Site",
    14,
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
 "t": "State Historic Site",
 "verdict": "no size on page"
}
```

## US-4881 Cape Horn State Forest
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Cape Horn State Forest",
 "official": null,
 "ours": {
  "acres": 2471,
  "dissolved": {
   "after": 2046,
   "before": 4089,
   "copies": 0,
   "key_union": 2471,
   "parts": 2,
   "records": 3,
   "summed": 2046,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 0 copies of a tract (same acres, another layer) and 2 fee tracts under a designation record folded; summed 4089 -> 2046 acres",
  "pieces": [
   [
    56951,
    "Cape Horn State Forest",
    2046,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 5
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "State Forest",
 "verdict": "no size on page"
}
```

## US-4885 Cilley State Forest
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Cilley State Forest",
 "official": null,
 "ours": {
  "acres": 115,
  "manager": "",
  "pieces": [
   [
    "sgnhc1109",
    "Cilley State Forest",
    141,
    "name"
   ],
   [
    "sgnhc1254",
    "Cilley State Forest",
    33,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 2
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "State Forest",
 "verdict": "no size on page"
}
```

## US-2683 Wentworth State Park
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Wentworth State Park",
 "official": {
  "acres": 50.0,
  "as": "50 acres",
  "clean": true,
  "line": "n State Park lands. Activities and amenities Check Beach Advisories About the Park Wentworth State Park spans 50 acres and is located on the shore of scenic Wentworth Lake. Popular activities in the park include swimming, picnic",
  "read": "2026-11-01",
  "sent": "Wentworth State Park spans 50 acres and is located on the shore of scenic Wentworth Lake.",
  "url": "https://www.nhstateparks.org/find-parks-trails/wentworth-state-park",
  "why": "clean total"
 },
 "ours": {
  "acres": 52,
  "dissolved": {
   "after": 52,
   "before": 104,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 104 -> 52 acres",
  "pieces": [
   [
    56931,
    "Wentworth State Park",
    52,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 2
 },
 "owner_now": null,
 "pct": 4,
 "same_agency": false,
 "score": 8,
 "t": "State Park",
 "verdict": "agree"
}
```

## US-2677 Rye Harbor State Park
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Rye Harbor State Park",
 "official": null,
 "ours": {
  "acres": 64,
  "manager": "",
  "pieces": [
   [
    "sgnhc1194",
    "Rye Harbor State Park",
    49,
    "name"
   ],
   [
    "sgnhc1306",
    "Rye Harbor State Park",
    9,
    "name"
   ],
   [
    "sgnhc1312",
    "Rye Harbor State Park",
    6,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 6
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-8018 Fort Constitution State Historic Site
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Fort Constitution State Historic Site",
 "official": null,
 "ours": {
  "acres": 1,
  "manager": "",
  "pieces": [
   [
    "sgnhc1429",
    "Fort Constitution",
    2,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "",
  "unknown_pieces": 2
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "State Historic Site",
 "verdict": "no size on page"
}
```

## US-4868 Annett State Forest
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Annett State Forest",
 "official": null,
 "ours": {
  "acres": 1803,
  "dissolved": {
   "after": 1698,
   "before": 3051,
   "copies": 1,
   "families": {
    "padus": 1356,
    "sgnhc": 342
   },
   "family_fold": 342,
   "family_used": "padus",
   "key_union": 1803,
   "parts": 0,
   "records": 6,
   "summed": 1356,
   "tracts": 5
  },
  "family_fold": "layers {'padus': 1356, 'sgnhc': 342}: one land in 2 layers, the padus copy used (342 ac of copies not added)",
  "manager": "",
  "note": "6 joined records = 5 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 3051 -> 1698 acres",
  "pieces": [
   [
    56939,
    "Annett State Forest",
    1356,
    "name"
   ]
  ],
  "pin": "well outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 4
 },
 "owner_now": null,
 "pct": null,
 "score": 5,
 "t": "State Forest",
 "verdict": "no size on page"
}
```

## US-4880 Bowditch-Runnells State Forest
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Bowditch-Runnells State Forest",
 "official": null,
 "ours": {
  "acres": 122,
  "dissolved": {
   "after": 122,
   "before": 125,
   "copies": 0,
   "parts": 2,
   "records": 5,
   "tracts": 3
  },
  "manager": "",
  "note": "5 joined records = 3 tracts: 0 copies of a tract (same acres, another layer) and 2 fee tracts under a designation record folded; summed 125 -> 122 acres",
  "pieces": [
   [
    "sgnhc719",
    "Bowditch-Runnels State Forest",
    67,
    "name"
   ],
   [
    "sgnhc720",
    "Bowditch-Runnels State Forest",
    52,
    "name"
   ],
   [
    "sgnhc724",
    "Bowditch-Runnels State Forest",
    3,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "",
  "unknown_pieces": 5
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "State Forest",
 "verdict": "no size on page"
}
```

## US-2658 Kingston State Park
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-01",
 "handover": [],
 "n": "Kingston State Park",
 "official": {
  "acres": 44.0,
  "as": "44 acre",
  "clean": true,
  "line": "ties and amenities Check Beach Advisories About the Park Located in Southeastern NH, Kingston State Park is a 44 acre park located on Kingston Pond/Great Pond. It is a quick drive from the seacoast and Boston. Kingston State Pa",
  "read": "2026-11-01",
  "sent": "Located in Southeastern NH, Kingston State Park is a 44 acre park located on Kingston Pond/Great Pond.",
  "url": "https://www.nhstateparks.org/find-parks-trails/kingston-state-park",
  "why": "clean total"
 },
 "ours": {
  "acres": 36,
  "manager": "",
  "pieces": [
   [
    "sgnhc1144",
    "Kingston Lake State Park",
    46,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "",
  "unknown_pieces": 2
 },
 "owner_now": null,
 "pct": 18,
 "same_agency": false,
 "score": 5,
 "t": "State Park",
 "verdict": "off"
}
```

## US-4976 Wade State Forest
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Wade State Forest",
 "official": null,
 "ours": {
  "acres": 451,
  "manager": "",
  "pieces": [
   [
    "sgnhc176",
    "Wade State Forest",
    451,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "",
  "unknown_pieces": 2
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "State Forest",
 "verdict": "no size on page"
}
```

## US-4900 Fay State Forest
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Fay State Forest",
 "official": null,
 "ours": {
  "acres": 184,
  "dissolved": {
   "after": 222,
   "before": 443,
   "copies": 1,
   "key_union": 184,
   "parts": 2,
   "records": 5,
   "summed": 222,
   "tracts": 2
  },
  "manager": "",
  "note": "5 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 2 fee tracts under a designation record folded; summed 443 -> 222 acres",
  "pieces": [
   [
    56971,
    "Fay State Forest",
    214,
    "name"
   ],
   [
    56970,
    "Fay State Forest",
    8,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 4
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "State Forest",
 "verdict": "no size on page"
}
```

## US-4889 Conway Common Lands State Forest
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Conway Common Lands State Forest",
 "official": null,
 "ours": {
  "acres": 469,
  "dissolved": {
   "after": 568,
   "before": 1136,
   "copies": 1,
   "key_union": 469,
   "parts": 0,
   "records": 2,
   "summed": 568,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1136 -> 568 acres",
  "pieces": [
   [
    56959,
    "Conway Common Lands State Forest",
    568,
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
 "t": "State Forest",
 "verdict": "no size on page"
}
```
