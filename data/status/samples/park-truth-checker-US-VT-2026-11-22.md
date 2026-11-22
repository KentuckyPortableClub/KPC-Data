# park truth checker: US-VT random sample of 12 (2026-11-22; seed = date + area, same rows for everyone)

Source file: `data/truth/US-VT.json`

## US-3111 D.A.R. State Park
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "D.A.R. State Park",
 "official": {
  "acres": 95.0,
  "as": "95 acres",
  "clean": false,
  "line": "erican Revolution purchased the property and opened a museum about early colonial life. In 1955, they donated 95 acres to the State of Vermont, which became D.A.R. State Park. Facilities and Amenities Image The stone pavilion Th",
  "read": "2026-11-22",
  "sent": "In 1955, they donated 95 acres to the State of Vermont, which became D.A.R.",
  "url": "https://vtstateparks.com/dar.html",
  "why": "history"
 },
 "ours": {
  "acres": 92,
  "dissolved": {
   "after": 92,
   "before": 184,
   "copies": 0,
   "parts": 5,
   "records": 6,
   "tracts": 1
  },
  "manager": "",
  "note": "6 joined records = 1 tracts: 0 copies of a tract (same acres, another layer) and 5 fee tracts under a designation record folded; summed 184 -> 92 acres",
  "pieces": [
   [
    "sgvta438",
    "D.A.R. State Park",
    92,
    "name"
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

## US-5527 Arlington State Forest
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Arlington State Forest",
 "official": {
  "acres": 225.0,
  "as": "225 Acres",
  "clean": false,
  "line": "Recreation State Lands Agency Home Project Learning Tree Arlington State Forest Arlington; Bennington County 225 Acres General Description: Established in 1913, Arlington State Forest consists of 225 acres of forest land in the",
  "read": "2026-11-22",
  "sent": "225 Acres",
  "url": "https://fpr.vermont.gov/arlington-state-forest",
  "why": "total-looking"
 },
 "ours": {
  "acres": 212,
  "dissolved": {
   "after": 212,
   "before": 424,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 424 -> 212 acres",
  "pieces": [
   [
    61173,
    "Arlington State Forest",
    212,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 6,
 "same_agency": false,
 "score": 8,
 "t": "State Forest",
 "verdict": "agree"
}
```

## US-3110 Crystal Lake State Park
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Crystal Lake State Park",
 "official": null,
 "ours": {
  "acres": 21,
  "dissolved": {
   "after": 14,
   "before": 28,
   "copies": 1,
   "key_union": 21,
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

## US-5528 Townshend State Forest
```json
{
 "checked": "2026-11-22",
 "handover": [
  {
   "date_hint": null,
   "kind": "managed by",
   "line": "opportunities for swimming and boating on the nearby Townshend Lake Project on the West River which is managed by the U.S. Army Corps of Engineers. Townshend State Forest Recreational Trails Guide Bald Mountain Trail (Trail Finder) Information on hunting, fishing and",
   "owner_now": "U.S",
   "src": "https://fpr.vermont.gov/townshend-state-forest",
   "why": "the park's page (data/parkinfo)"
  }
 ],
 "n": "Townshend State Forest",
 "official": {
  "acres": 1244.0,
  "as": "1,244 Acres",
  "clean": false,
  "line": "rks Recreation State Lands Agency Home Project Learning Tree Townshend State Forest Townshend; Windham County 1,244 Acres For more information about this unit please visit the web page: Townshend State Park Townshend State Park Int",
  "read": "2026-11-22",
  "sent": "1,244 Acres",
  "url": "https://fpr.vermont.gov/townshend-state-forest",
  "why": "total-looking"
 },
 "ours": {
  "acres": 1264,
  "dissolved": {
   "after": 1264,
   "before": 2514,
   "copies": 0,
   "parts": 8,
   "records": 11,
   "tracts": 3
  },
  "manager": "",
  "note": "11 joined records = 3 tracts: 0 copies of a tract (same acres, another layer) and 8 fee tracts under a designation record folded; summed 2514 -> 1264 acres",
  "pieces": [
   [
    "sgvta7",
    "Townshend State Forest",
    1257,
    "name"
   ],
   [
    61436,
    "Townshend State Forest",
    5,
    "name"
   ],
   [
    61440,
    "Townshend State Forest",
    2,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": "U.S",
 "pct": 2,
 "same_agency": false,
 "score": 8,
 "t": "State Forest",
 "verdict": "agree"
}
```

## US-5558 Mathewson State Forest
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Mathewson State Forest",
 "official": {
  "acres": 788.0,
  "as": "788 Acres",
  "clean": false,
  "line": "ds Agency Home Project Learning Tree Mathewson State Forest Sheffield, Sutton, and Wheelock; Caledonia County 788 Acres General Description: Mathewson State Forest lies between the Sutton-Wheelock Road and Town Farm Road. The par",
  "read": "2026-11-22",
  "sent": "788 Acres",
  "url": "https://fpr.vermont.gov/mathewson-state-forest",
  "why": "total-looking"
 },
 "ours": {
  "acres": 808,
  "family_fold": "layers {'sgvta': 808, 'padus': 599}: one land in 2 layers, the sgvta copy used (599 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgvta31",
    "Mathewson State Forest",
    808,
    "reviewed"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 3,
 "same_agency": false,
 "score": 7,
 "t": "State Forest",
 "verdict": "agree"
}
```

## US-3120 Jamaica State Park
```json
{
 "cause": "agency smaller: our outline may hold water, a lease or a neighbour tract",
 "checked": "2026-11-22",
 "handover": [
  {
   "date_hint": null,
   "kind": "managed by",
   "line": "The West River Trail follows the river upstream for about 2.5 miles to the Ball Mountain Dam, which is managed by the U.S. Army Corps of Engineers. The West River is also a favorite spot for many fishermen. The combination of deep slow running water and shallow",
   "owner_now": "U.S",
   "src": "https://vtstateparks.com/jamaica.html",
   "why": "the park's page (data/parkinfo)"
  }
 ],
 "n": "Jamaica State Park",
 "official": {
  "acres": 772.0,
  "as": "772 acres",
  "clean": true,
  "line": "area. Please clean up after your pets. 24 9 6 7 4 11 1 16 2 3 Photo Gallery Welcome Jamaica State Park covers 772 acres and opened to the public in 1969. Before the park was established, the land included several small farms and",
  "read": "2026-11-22",
  "sent": "Jamaica State Park covers 772 acres and opened to the public in 1969.",
  "url": "https://vtstateparks.com/jamaica.html",
  "why": "clean total"
 },
 "ours": {
  "acres": 1133,
  "dissolved": {
   "after": 1918,
   "before": 1934,
   "copies": 0,
   "families": {
    "padus": 785,
    "sgvta": 1133
   },
   "family_fold": 785,
   "family_used": "sgvta",
   "parts": 2,
   "records": 9,
   "tracts": 7
  },
  "family_fold": "layers {'sgvta': 1133, 'padus': 785}: one land in 2 layers, the sgvta copy used (785 ac of copies not added)",
  "manager": "",
  "note": "9 joined records = 7 tracts: 0 copies of a tract (same acres, another layer) and 2 fee tracts under a designation record folded; summed 1934 -> 1918 acres",
  "pieces": [
   [
    "sgvta434",
    "Jamaica State Park",
    1133,
    "reviewed"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": "U.S",
 "pct": 47,
 "same_agency": false,
 "score": 5,
 "t": "State Park",
 "verdict": "off"
}
```

## US-5556 Lyndon State Forest
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Lyndon State Forest",
 "official": {
  "acres": 72.2,
  "as": "72.2 Acres",
  "clean": false,
  "line": "e Parks Recreation State Lands Agency Home Project Learning Tree Lyndon State Forest Lyndon, Caledonia County 72.2 Acres General Description: Lyndon State Forest was one of the first parcels of land acquired by the State of Vermon",
  "read": "2026-11-22",
  "sent": "72.2 Acres",
  "url": "https://fpr.vermont.gov/lyndon-state-forest",
  "why": "total-looking"
 },
 "ours": {
  "acres": 71,
  "dissolved": {
   "after": 71,
   "before": 142,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 142 -> 71 acres",
  "pieces": [
   [
    61333,
    "Lyndon State Forest",
    71,
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
 "t": "State Forest",
 "verdict": "agree"
}
```

## US-3105 Burton Island State Park
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Burton Island State Park",
 "official": {
  "acres": 253.0,
  "as": "253 acre",
  "clean": true,
  "line": "ean up after your pets. 24 2346 26 10 13 9 8 6 5 2341 15 1 16 2 18 3 Photo Gallery Welcome Burton Island is a 253-acre park off the southwestern tip of St. Albans Point in Lake Champlain’s 'Inland Sea'. The park is accessible on",
  "read": "2026-11-22",
  "sent": "Burton Island is a 253-acre park off the southwestern tip of St.",
  "url": "https://vtstateparks.com/burton.html",
  "why": "clean total"
 },
 "ours": {
  "acres": 253,
  "dissolved": {
   "after": 253,
   "before": 507,
   "copies": 0,
   "parts": 2,
   "records": 3,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 0 copies of a tract (same acres, another layer) and 2 fee tracts under a designation record folded; summed 507 -> 253 acres",
  "pieces": [
   [
    "sgvta447",
    "Burton Island State Park",
    253,
    "reviewed"
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
 "t": "State Park",
 "verdict": "agree"
}
```

## US-5540 Aitken State Forest
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Aitken State Forest",
 "official": {
  "acres": 918.0,
  "as": "918 Acres",
  "clean": false,
  "line": "ate Parks Recreation State Lands Agency Home Project Learning Tree Aitken State Forest Mendon; Rutland County 918 Acres General Description: Aitken State Forest is located only minutes from Rutland and can be accessed via the Not",
  "read": "2026-11-22",
  "sent": "918 Acres",
  "url": "https://fpr.vermont.gov/bird-mountain-wildlife-management-area/aitken-state-forest",
  "why": "total-looking"
 },
 "ours": {
  "acres": 911,
  "dissolved": {
   "after": 911,
   "before": 1813,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1813 -> 911 acres",
  "pieces": [
   [
    61172,
    "Aitken State Forest",
    911,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 1,
 "same_agency": false,
 "score": 8,
 "t": "State Forest",
 "verdict": "agree"
}
```

## US-3104 Brighton State Park
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Brighton State Park",
 "official": null,
 "ours": {
  "acres": 631,
  "family_fold": "layers {'sgvta': 631, 'padus': 156}: one land in 2 layers, the sgvta copy used (156 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgvta441",
    "Brighton State Park",
    631,
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

## US-4589 Molly's Falls Pond State Park
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Molly's Falls Pond State Park",
 "official": {
  "acres": 1064.0,
  "as": "1,064 acres",
  "clean": true,
  "line": "15 miles from Barre, Vermont. It is in the rural town of Cabot in north central Vermont. The property covers 1,064 acres and includes a 411 acre pond. U.S. Route 2 runs along the north side. A dam sits at the west end of the pond",
  "read": "2026-11-22",
  "sent": "The property covers 1,064 acres and includes a 411 acre pond.",
  "url": "https://vtstateparks.com/mollysfalls.html",
  "why": "clean total"
 },
 "ours": {
  "acres": 1029,
  "dissolved": {
   "after": 1029,
   "before": 2058,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 2058 -> 1029 acres",
  "pieces": [
   [
    61139,
    "Molly’s Falls Pond State Park",
    1029,
    "name"
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

## US-3140 Sand Bar State Park
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 15 acres, no total words near it)",
 "checked": "2026-11-22",
 "handover": [],
 "n": "Sand Bar State Park",
 "official": {
  "acres": 15.0,
  "as": "15 acres",
  "clean": false,
  "line": "g it between the campground and beach became less safe. In 1970, a land swap expanded the park to its current 15 acres. The former campground became a fishing access area managed by Fish and Wildlife. During this expansion, the",
  "read": "2026-11-22",
  "sent": "In 1970, a land swap expanded the park to its current 15 acres.",
  "url": "https://vtstateparks.com/sandbar.html",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 20,
  "manager": "",
  "pieces": [
   [
    "sgvta430",
    "Sandbar State Park",
    20,
    "reviewed"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 33,
 "same_agency": false,
 "score": 6,
 "t": "State Park",
 "verdict": "unsure"
}
```
