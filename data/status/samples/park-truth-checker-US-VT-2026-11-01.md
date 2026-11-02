# park truth checker: US-VT random sample of 12 (2026-11-01; seed = date + area, same rows for everyone)

Source file: `data/truth/US-VT.json`

## US-3125 Knight Point State Park
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 54 acre, no total words near it)",
 "checked": "2026-11-01",
 "handover": [],
 "n": "Knight Point State Park",
 "official": {
  "acres": 54.0,
  "as": "54 acre",
  "clean": false,
  "line": "e tavern in 1845, has an unusual two-story porch. Grounds / Facilities Expansive lawns are the center of this 54-acre day use park. The lawn becomes meadow west of the developed area, where the forest along the lakeside is a su",
  "read": "2026-11-01",
  "sent": "Expansive lawns are the center of this 54-acre day use park.",
  "url": "https://vtstateparks.com/knightpoint.html",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 35,
  "dissolved": {
   "after": 59,
   "before": 115,
   "copies": 1,
   "key_union": 35,
   "parts": 0,
   "records": 3,
   "summed": 59,
   "tracts": 2
  },
  "manager": "",
  "note": "3 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 115 -> 59 acres",
  "pieces": [
   [
    61121,
    "Knight Point State Park",
    56,
    "name"
   ],
   [
    61120,
    "Knight Point State Park",
    3,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 35,
 "same_agency": false,
 "score": 6,
 "t": "State Park",
 "verdict": "unsure"
}
```

## US-4527 Green Mountain National Forest
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Green Mountain National Forest",
 "official": null,
 "ours": {
  "acres": 409650,
  "manager": "",
  "pieces": [
   [
    3050,
    "Green Mountain National Forest",
    409650,
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

## US-3108 Camp Plymouth State Park
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-01",
 "handover": [
  {
   "date_hint": "1984",
   "kind": "transfer",
   "line": "fire site. In 1984, the property was conserved with assistance from the Ottauquechee Land Trust and transferred to the State of Vermont. Park facilities were built in the following years, and Camp Plymouth State Park opened to the publ",
   "owner_now": "State of Vermont",
   "src": "https://vtstateparks.com/plymouth.html",
   "why": "the park's page (data/parkinfo)"
  }
 ],
 "n": "Camp Plymouth State Park",
 "official": {
  "acres": 295.0,
  "as": "295 acres",
  "clean": false,
  "line": "ic & Group Events Group Camping Cottage Rentals Camp Plymouth State Park Welcome to Camp Plymouth State Park, 295 acres of state lands on the shores of Echo Lake in Plymouth, Vermont. Camp Plymouth is rich in history from the",
  "read": "2026-11-01",
  "sent": "Welcome to Camp Plymouth State Park, 295 acres of state lands on the shores of Echo Lake in",
  "url": "https://www.vtstateparks.com/sites/stateparks/files/documents/Camp-Plymouth-Map-Guide-2025.pdf",
  "why": "total-looking"
 },
 "ours": {
  "acres": 194,
  "dissolved": {
   "after": 311,
   "before": 622,
   "copies": 1,
   "key_union": 194,
   "parts": 0,
   "records": 2,
   "summed": 311,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 622 -> 311 acres",
  "pieces": [
   [
    61062,
    "Camp Plymouth State Park",
    311,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": "State of Vermont",
 "pct": 34,
 "same_agency": false,
 "score": 5,
 "t": "State Park",
 "verdict": "off"
}
```

## US-5563 Black Turn Brook State Forest
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Black Turn Brook State Forest",
 "official": {
  "acres": 592.0,
  "as": "592 Acres",
  "clean": false,
  "line": "s Recreation State Lands Agency Home Project Learning Tree Black Turn Brook State Forest Norton, Essex County 592 Acres General Description: Black Turn Brook State Forest was established in 1994 when the state received 592 acres",
  "read": "2026-11-01",
  "sent": "592 Acres",
  "url": "https://fpr.vermont.gov/black-turn-brook-state-forest",
  "why": "total-looking"
 },
 "ours": {
  "acres": 587,
  "manager": "",
  "pieces": [
   [
    "sgvta45",
    "Black Turn Brook State Forest",
    587,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 1,
 "same_agency": false,
 "score": 6,
 "t": "State Forest",
 "verdict": "agree"
}
```

## US-5550 Boyer State Forest
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Boyer State Forest",
 "official": {
  "acres": 354.6,
  "as": "354.6 Acres",
  "clean": false,
  "line": "e Parks Recreation State Lands Agency Home Project Learning Tree Boyer State Forest Berlin, Washington County 354.6 Acres General Description: Boyer State Forest is located on Crosstown Road in Berlin, Vermont. It ranges in elevati",
  "read": "2026-11-01",
  "sent": "354.6 Acres",
  "url": "https://fpr.vermont.gov/boyer-state-forest",
  "why": "total-looking"
 },
 "ours": {
  "acres": 310,
  "dissolved": {
   "after": 364,
   "before": 728,
   "copies": 0,
   "key_union": 310,
   "parts": 3,
   "records": 4,
   "summed": 364,
   "tracts": 1
  },
  "manager": "",
  "note": "4 joined records = 1 tracts: 0 copies of a tract (same acres, another layer) and 3 fee tracts under a designation record folded; summed 728 -> 364 acres",
  "pieces": [
   [
    "sgvta42",
    "Boyer State Forest",
    364,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 13,
 "same_agency": false,
 "score": 7,
 "t": "State Forest",
 "verdict": "agree"
}
```

## US-5544 Downer State Forest
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Downer State Forest",
 "official": {
  "acres": 705.0,
  "as": "705 Acres",
  "clean": false,
  "line": "ate Parks Recreation State Lands Agency Home Project Learning Tree Downer State Forest Sharon; Windsor County 705 Acres General Description: Downer State Forest was established in 1910 as a gift from Charles Downer for the purpos",
  "read": "2026-11-01",
  "sent": "705 Acres",
  "url": "https://fpr.vermont.gov/downer-state-forest",
  "why": "total-looking"
 },
 "ours": {
  "acres": 733,
  "dissolved": {
   "after": 733,
   "before": 1466,
   "copies": 0,
   "parts": 2,
   "records": 3,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 0 copies of a tract (same acres, another layer) and 2 fee tracts under a designation record folded; summed 1466 -> 733 acres",
  "pieces": [
   [
    "sgvta3",
    "Downer State Forest",
    733,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 4,
 "same_agency": false,
 "score": 8,
 "t": "State Forest",
 "verdict": "agree"
}
```

## US-11966 Mount Independence State Historic Site
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-01",
 "handover": [
  {
   "date_hint": null,
   "kind": "managed by",
   "line": "sites, offering six miles of trails along the archaeological remains of the fortification. Jointly owned and managed by the State of Vermont’s Division for Historic Preservation and The Fort Ticonderoga Association, Mount Independence docum",
   "owner_now": "State of Vermont",
   "src": "https://historicsites.vermont.gov/mount-independence",
   "why": "the park's page (data/parkinfo)"
  }
 ],
 "n": "Mount Independence State Historic Site",
 "official": {
  "acres": 167.7,
  "as": "167.7 acres",
  "clean": false,
  "line": "iconderoga Association. In 1961, the State of Vermont began acquiring the southern parcels of the Mount, with 167.7 acres in total by 1998. Today, history and nature unite over 280 acres at Mount Independence with a one-of-a-kind e",
  "read": "2026-11-01",
  "sent": "In 1961, the State of Vermont began acquiring the southern parcels of the Mount, with 167.7 acres in total by 1998.",
  "url": "https://historicsites.vermont.gov/mount-independence",
  "why": "total-looking"
 },
 "ours": {
  "acres": 80,
  "manager": "",
  "pieces": [
   [
    52105,
    "Mount Independence Historic Site",
    131,
    "name"
   ],
   [
    58785,
    "Mt. Independence",
    12,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": "State of Vermont",
 "pct": 52,
 "same_agency": false,
 "score": 3,
 "t": "State Historic Site",
 "verdict": "off"
}
```

## US-5536 Okemo State Forest
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Okemo State Forest",
 "official": {
  "acres": 7983.0,
  "as": "7,983 Acres",
  "clean": false,
  "line": "me Project Learning Tree Okemo State Forest Andover, Ludlow, Mount Holly & Weston; Windsor & Rutland Counties 7,983 Acres General Description Okemo State Forest is one of southeast Vermont’s largest state forests. It straddles town",
  "read": "2026-11-01",
  "sent": "7,983 Acres",
  "url": "https://fpr.vermont.gov/okemo-state-forest",
  "why": "total-looking"
 },
 "ours": {
  "acres": 8372,
  "dissolved": {
   "after": 13016,
   "before": 13783,
   "copies": 0,
   "families": {
    "padus": 4644,
    "sgvta": 8372
   },
   "family_fold": 4644,
   "family_used": "sgvta",
   "parts": 5,
   "records": 13,
   "tracts": 8
  },
  "family_fold": "layers {'sgvta': 8372, 'padus': 4644}: one land in 2 layers, the sgvta copy used (4,644 ac of copies not added)",
  "manager": "",
  "note": "13 joined records = 8 tracts: 0 copies of a tract (same acres, another layer) and 5 fee tracts under a designation record folded; summed 13783 -> 13016 acres",
  "pieces": [
   [
    "sgvta27",
    "Okemo State Forest",
    8372,
    "name"
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
 "t": "State Forest",
 "verdict": "agree"
}
```

## US-5542 West Rutland State Forest
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-01",
 "handover": [],
 "n": "West Rutland State Forest",
 "official": {
  "acres": 344.0,
  "as": "344 acre",
  "clean": true,
  "line": "State Forest West Rutland; Rutland County 344 Acres General Description: West Rutland State Forest is a hilly 344-acre property in the extreme northwest corner of the Town of West Rutland. It is completely forested, principally",
  "read": "2026-11-01",
  "sent": "West Rutland State Forest is a hilly 344-acre property in the extreme northwest corner of the Town of West Rutland.",
  "url": "https://fpr.vermont.gov/west-rutland-state-forest",
  "why": "clean total"
 },
 "ours": {
  "acres": 286,
  "dissolved": {
   "after": 342,
   "before": 684,
   "copies": 1,
   "key_union": 286,
   "parts": 0,
   "records": 2,
   "summed": 342,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 684 -> 342 acres",
  "pieces": [
   [
    61458,
    "West Rutland State Forest",
    342,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 17,
 "same_agency": false,
 "score": 5,
 "t": "State Forest",
 "verdict": "off"
}
```

## US-3110 Crystal Lake State Park
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Crystal Lake State Park",
 "official": null,
 "ours": {
  "acres": 24,
  "dissolved": {
   "after": 14,
   "before": 28,
   "copies": 1,
   "key_union": 24,
   "parts": 0,
   "records": 2,
   "summed": 14,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 28 -> 14 acres",
  "pieces": [
   [
    61063,
    "Crystal Lake State Park",
    14,
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
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-5543 Mount Carmel State Forest
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-01",
 "handover": [
  {
   "date_hint": null,
   "kind": "transfer",
   "line": "Elevation of the forest range from 2380 to 3365 feet at the summit of Mt. Carmel. While there is no deeded access to the forest it can be accessed by the New Boston Trail, a side trail to the Long Trail. Unique Features: The forests of Mt Carmel State Forest are dominated by Northern hardwoods – sug",
   "owner_now": "New Boston Trail",
   "src": "https://fpr.vermont.gov/mt-carmel-state-forest",
   "why": "the park's page (data/parkinfo)"
  }
 ],
 "n": "Mount Carmel State Forest",
 "official": {
  "acres": 263.0,
  "as": "263 acre",
  "clean": false,
  "line": "l State Forest Chittenden; Rutland County 263.50 Acres General Description: The Mt. Carmel State Forest was a 263-acre gift to the State of Vermont in 1956 from Governor Redfield Proctor. Located in the Town of Chittenden, the f",
  "read": "2026-11-01",
  "sent": "Carmel State Forest was a 263-acre gift to the State of Vermont in 1956 from Governor Redfield Proctor.",
  "url": "https://fpr.vermont.gov/mt-carmel-state-forest",
  "why": "total-looking"
 },
 "ours": {
  "acres": 212,
  "dissolved": {
   "after": 264,
   "before": 528,
   "copies": 1,
   "key_union": 212,
   "parts": 0,
   "records": 2,
   "summed": 264,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 528 -> 264 acres",
  "pieces": [
   [
    61345,
    "Mt. Carmel State Forest",
    264,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": "New Boston Trail",
 "pct": 19,
 "same_agency": false,
 "score": 4,
 "t": "State Forest",
 "verdict": "off"
}
```

## US-3124 Knight Island State Park
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Knight Island State Park",
 "official": {
  "acres": 185.0,
  "as": "185 acres",
  "clean": false,
  "line": "with Burton Island and Woods Island . The State of Vermont bought Knight Island in 1990. The island is about 185 acres. It is about one mile long and nearly half a mile wide. Most of the island is part of the park, except for a",
  "read": "2026-11-01",
  "sent": "The island is about 185 acres.",
  "url": "https://vtstateparks.com/knightisland.html",
  "why": "total-looking"
 },
 "ours": {
  "acres": 170,
  "manager": "",
  "pieces": [
   [
    "sgvta469",
    "Knight Island State Park",
    170,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 8,
 "same_agency": false,
 "score": 6,
 "t": "State Park",
 "verdict": "agree"
}
```
