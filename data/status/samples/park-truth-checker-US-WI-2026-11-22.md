# park truth checker: US-WI random sample of 12 (2026-11-22; seed = date + area, same rows for everyone)

Source file: `data/truth/US-WI.json`

## US-4318 New Wood State Wildlife Area
```json
{
 "cause": "our union: one of our pieces alone matches the agency (double count?)",
 "checked": "2026-11-22",
 "handover": [
  {
   "date_hint": "1915",
   "kind": "transfer",
   "line": "uding today's wildlife area. In 1914, 1,600 acres comprising part of the present wildlife area were transferred to the Union Land Company of Merrill and, in 1915, to the Union Tanning Co. of New Jersey. Eastern hemlock bark played an important role in the forest and tanning industries of northern Wi",
   "owner_now": "Union Land Company of Merrill and",
   "src": "https://dnr.wisconsin.gov/topic/Lands/WildlifeAreas/newwood.html",
   "why": "the park's page (data/parkinfo)"
  }
 ],
 "n": "New Wood State Wildlife Area",
 "official": {
  "acres": 4635.0,
  "as": "4,635 acre",
  "clean": true,
  "line": "LinkedIn Search Lands_Content Page_New Wood Wildlife Area New Wood Wildlife Area New Wood Wildlife Area is a 4,635-acre property located in the west central portion of Lincoln County. Find New Wood Wildlife Area approximately 16",
  "read": "2026-11-22",
  "sent": "New Wood Wildlife Area is a 4,635-acre property located in the west central portion of Lincoln County.",
  "url": "https://dnr.wisconsin.gov/topic/Lands/WildlifeAreas/newwood.html",
  "why": "clean total"
 },
 "ours": {
  "acres": 7708,
  "dissolved": {
   "after": 10410,
   "before": 15810,
   "copies": 2,
   "families": {
    "padus": 7708,
    "sgwid": 2702
   },
   "family_fold": 2702,
   "family_used": "padus",
   "parts": 0,
   "records": 69,
   "tracts": 67
  },
  "family_fold": "layers {'padus': 7708, 'sgwid': 2702}: one land in 2 layers, the padus copy used (2,702 ac of copies not added)",
  "manager": "",
  "note": "69 joined records = 67 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 15810 -> 10410 acres",
  "pieces": [
   [
    78191,
    "New Wood Wildlife Area 1",
    5005,
    "name"
   ],
   [
    272687,
    "New Wood Wildlife Area",
    2703,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": "Union Land Company of Merrill and",
 "pct": 66,
 "same_agency": false,
 "score": 6,
 "t": "State Wildlife Area",
 "verdict": "off"
}
```

## US-8216 Osceola Bedrock Glades State Natural Area
```json
{
 "checked": "2026-11-22",
 "handover": [
  {
   "date_hint": "2002",
   "kind": "managed by",
   "line": "in the surrounding area. Of note is the presence of the prairie fame-flower. Osceola Bedrock Glades is owned jointly by the National Park Service and DNR and was designated a State Natural Area in 2002. Very few State Natural Areas have public facilities, but nearly all a",
   "owner_now": "National Park Service and DNR and",
   "src": "https://dnr.wisconsin.gov/topic/statenaturalareas/OsceolaBedrockGlades",
   "why": "the park's page (data/parkinfo)"
  }
 ],
 "n": "Osceola Bedrock Glades State Natural Area",
 "official": {
  "acres": 39.0,
  "as": "39 acres",
  "clean": false,
  "line": "ands, please consult Chapter NR 45 Wis. Admin. Code [exit DNR] . Location Polk County. T33N-R19W, Section 14. 39 acres. Driving directions From the intersection of Highways 35 and 243 in Osceola, go northeast on 35 for 1.8 miles",
  "read": "2026-11-22",
  "sent": "39 acres.",
  "url": "https://dnr.wisconsin.gov/topic/statenaturalareas/OsceolaBedrockGlades",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 36,
  "dissolved": {
   "after": 31,
   "before": 62,
   "copies": 0,
   "key_union": 36,
   "parts": 2,
   "records": 3,
   "summed": 31,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 0 copies of a tract (same acres, another layer) and 2 fee tracts under a designation record folded; summed 62 -> 31 acres",
  "pieces": [
   [
    "sgwic7094",
    "Osceola Bedrock Glades",
    31,
    "reviewed"
   ]
  ],
  "pin": "just outside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": "National Park Service and DNR and",
 "pct": 8,
 "same_agency": false,
 "score": 7,
 "t": "State Natural Area",
 "verdict": "agree"
}
```

## US-1436 Amnicon Falls State Park
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Amnicon Falls State Park",
 "official": null,
 "ours": {
  "acres": 834,
  "dissolved": {
   "after": 1549,
   "before": 2501,
   "copies": 1,
   "families": {
    "padus": 834,
    "sgwid": 715
   },
   "family_fold": 715,
   "family_used": "padus",
   "parts": 9,
   "records": 31,
   "tracts": 21
  },
  "family_fold": "layers {'padus': 834, 'sgwid': 715}: one land in 2 layers, the padus copy used (715 ac of copies not added)",
  "manager": "",
  "note": "31 joined records = 21 tracts: 1 copies of a tract (same acres, another layer) and 9 fee tracts under a designation record folded; summed 2501 -> 1549 acres",
  "pieces": [
   [
    272288,
    "Amnicon Falls State Park",
    834,
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

## US-1442 Brunet Island State Park
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Brunet Island State Park",
 "official": {
  "acres": 1300.0,
  "as": "1,300 acres",
  "clean": false,
  "line": "ties at the property. Read More Brunet Island State Park, on the Chippewa and Fisher rivers, offers more than 1,300 acres of scenic beauty and recreational opportunities. Quiet lagoons and channels are excellent for canoeing and wi",
  "read": "2026-11-22",
  "sent": "Brunet Island State Park, on the Chippewa and Fisher rivers, offers more than 1,300 acres of scenic beauty and recreational opportunities.",
  "url": "https://dnr.wisconsin.gov/topic/parks/brunetisland",
  "why": "total-looking"
 },
 "ours": {
  "acres": 1224,
  "dissolved": {
   "after": 2019,
   "before": 3503,
   "copies": 1,
   "families": {
    "padus": 1224,
    "sgwid": 795
   },
   "family_fold": 795,
   "family_used": "padus",
   "parts": 44,
   "records": 69,
   "tracts": 24
  },
  "family_fold": "layers {'padus': 1224, 'sgwid': 795}: one land in 2 layers, the padus copy used (795 ac of copies not added)",
  "manager": "",
  "note": "69 joined records = 24 tracts: 1 copies of a tract (same acres, another layer) and 44 fee tracts under a designation record folded; summed 3503 -> 2019 acres",
  "pieces": [
   [
    272298,
    "Brunet Island State Park",
    1146,
    "name"
   ],
   [
    78255,
    "Brunet Island State Park",
    78,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 7
 },
 "owner_now": null,
 "pct": 6,
 "same_agency": false,
 "score": 8,
 "t": "State Park",
 "verdict": "agree"
}
```

## US-4336 Totogatic State Wildlife Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Totogatic State Wildlife Area",
 "official": {
  "acres": 2719.0,
  "as": "2,719 acres",
  "clean": false,
  "line": "s. Acquisition of Totogatic Wildlife Area began in 1941 and was completed in 1951. Today, the property covers 2,719 acres. This project was funded originally through the Pittman-Robertson Act as a waterfowl restoration area. A 600-",
  "read": "2026-11-22",
  "sent": "Today, the property covers 2,719 acres.",
  "url": "https://dnr.wisconsin.gov/topic/Lands/WildlifeAreas/totogatic.html",
  "why": "total-looking"
 },
 "ours": {
  "acres": 2665,
  "dissolved": {
   "after": 5326,
   "before": 10646,
   "copies": 2,
   "families": {
    "sgwia": 2661,
    "sgwid": 2665
   },
   "family_fold": 2661,
   "family_used": "sgwid",
   "parts": 0,
   "records": 71,
   "tracts": 69
  },
  "family_fold": "layers {'sgwia': 2661, 'sgwid': 2665}: one land in 2 layers, the sgwid copy used (2,661 ac of copies not added)",
  "manager": "",
  "note": "71 joined records = 69 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 10646 -> 5326 acres",
  "pieces": [
   [
    "sgwid19757431",
    "Totogatic Wildlife Area",
    45,
    "name"
   ],
   [
    "sgwid19757427",
    "Totogatic Wildlife Area",
    44,
    "name"
   ],
   [
    "sgwid19757428",
    "Totogatic Wildlife Area",
    44,
    "name"
   ],
   [
    "sgwid19757416",
    "Totogatic Wildlife Area",
    43,
    "name"
   ],
   [
    "sgwid19758204",
    "Totogatic Wildlife Area",
    43,
    "name"
   ],
   [
    "sgwid19758205",
    "Totogatic Wildlife Area",
    43,
    "name"
   ],
   [
    "sgwid19758201",
    "Totogatic Wildlife Area",
    42,
    "name"
   ],
   [
    "sgwid19758206",
    "Totogatic Wildlife Area",
    42,
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
 "t": "State Wildlife Area",
 "verdict": "agree"
}
```

## US-9838 Colburn State Wildlife Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Colburn State Wildlife Area",
 "official": {
  "acres": 4965.0,
  "as": "4,965 acre",
  "clean": true,
  "line": "ram LinkedIn Search Lands_Content Page_Colburn Wildlife Area Colburn Wildlife Area Colburn Wildlife Area is a 4,965-acre property located in north-central Adams County near the Waushara County border. It is about 13 miles northeas",
  "read": "2026-11-22",
  "sent": "Colburn Wildlife Area is a 4,965-acre property located in north-central Adams County near the Waushara County border.",
  "url": "https://dnr.wisconsin.gov/topic/Lands/WildlifeAreas/colburn.html",
  "why": "clean total"
 },
 "ours": {
  "acres": 5074,
  "dissolved": {
   "after": 9963,
   "before": 20246,
   "copies": 2,
   "families": {
    "padus": 5074,
    "sgwid": 4889
   },
   "family_fold": 4889,
   "family_used": "padus",
   "parts": 9,
   "records": 134,
   "tracts": 123
  },
  "family_fold": "layers {'padus': 5074, 'sgwid': 4889}: one land in 2 layers, the padus copy used (4,889 ac of copies not added)",
  "manager": "",
  "note": "134 joined records = 123 tracts: 2 copies of a tract (same acres, another layer) and 9 fee tracts under a designation record folded; summed 20246 -> 9963 acres",
  "pieces": [
   [
    272498,
    "Colburn Wildlife Area",
    5074,
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
 "t": "State Wildlife Area",
 "verdict": "agree"
}
```

## US-9778 Devil’s River State Trail
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Devil’s River State Trail",
 "official": null,
 "ours": {
  "acres": 288,
  "dissolved": {
   "after": 479,
   "before": 719,
   "copies": 1,
   "families": {
    "padus": 240,
    "sgwid": 239
   },
   "family_fold": 239,
   "family_used": "padus",
   "key_union": 288,
   "parts": 0,
   "records": 103,
   "summed": 240,
   "tracts": 102
  },
  "family_fold": "layers {'padus': 240, 'sgwid': 239}: one land in 2 layers, the padus copy used (239 ac of copies not added)",
  "manager": "",
  "note": "103 joined records = 102 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 719 -> 479 acres",
  "pieces": [
   [
    272317,
    "Devils River State Trail",
    240,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 16
 },
 "owner_now": null,
 "pct": null,
 "score": 5,
 "t": "State Trail",
 "verdict": "no size on page"
}
```

## US-4330 Spring Creek State Wildlife Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Spring Creek State Wildlife Area",
 "official": {
  "acres": 1000.0,
  "as": "1,000 acre",
  "clean": true,
  "line": "arch Lands_Content Page_Spring Creek Wildlife Area Spring Creek Wildlife Area Spring Creek Wildlife Area is a 1,000-acre property located eight miles southwest of Phillips in Price County. The diverse wildlife area includes four w",
  "read": "2026-11-22",
  "sent": "Spring Creek Wildlife Area is a 1,000-acre property located eight miles southwest of Phillips in Price County.",
  "url": "https://dnr.wisconsin.gov/topic/Lands/WildlifeAreas/springcreek.html",
  "why": "clean total"
 },
 "ours": {
  "acres": 919,
  "dissolved": {
   "after": 1799,
   "before": 3671,
   "copies": 3,
   "families": {
    "padus": 919,
    "sgwia": 4,
    "sgwid": 876
   },
   "family_fold": 880,
   "family_used": "padus",
   "parts": 2,
   "records": 30,
   "tracts": 25
  },
  "family_fold": "layers {'padus': 919, 'sgwid': 876, 'sgwia': 4}: one land in 3 layers, the padus copy used (880 ac of copies not added)",
  "manager": "",
  "note": "30 joined records = 25 tracts: 3 copies of a tract (same acres, another layer) and 2 fee tracts under a designation record folded; summed 3671 -> 1799 acres",
  "pieces": [
   [
    272898,
    "Spring Creek Wildlife Area",
    919,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 2
 },
 "owner_now": null,
 "pct": 8,
 "same_agency": false,
 "score": 8,
 "t": "State Wildlife Area",
 "verdict": "agree"
}
```

## US-4266 Ackley State Wildlife Area
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 27,000 acres, no total words near it)",
 "checked": "2026-11-22",
 "handover": [],
 "n": "Ackley State Wildlife Area",
 "official": {
  "acres": 27000.0,
  "as": "27,000 acres",
  "clean": false,
  "line": "ouse, woodcock and waterfowl. Beavers, muskrats, fishers and coyotes are abundant on this property and on the 27,000 acres of surrounding county forest lands. Management Recreation Maps Useful Links Management Objectives Ackley Wild",
  "read": "2026-11-22",
  "sent": "Beavers, muskrats, fishers and coyotes are abundant on this property and on the 27,000 acres of surrounding county forest lands.",
  "url": "https://dnr.wisconsin.gov/topic/Lands/WildlifeAreas/ackley.html",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 1104,
  "dissolved": {
   "after": 2091,
   "before": 4412,
   "copies": 2,
   "families": {
    "padus": 1104,
    "sgwid": 987
   },
   "family_fold": 987,
   "family_used": "padus",
   "parts": 7,
   "records": 36,
   "tracts": 27
  },
  "family_fold": "layers {'padus': 1104, 'sgwid': 987}: one land in 2 layers, the padus copy used (987 ac of copies not added)",
  "manager": "",
  "note": "36 joined records = 27 tracts: 2 copies of a tract (same acres, another layer) and 7 fee tracts under a designation record folded; summed 4412 -> 2091 acres",
  "pieces": [
   [
    272412,
    "Ackley Wildlife Area",
    1104,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 96,
 "same_agency": false,
 "score": 7,
 "t": "State Wildlife Area",
 "verdict": "unsure"
}
```

## US-10646 Willow Creek State Fish and Wildlife Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Willow Creek State Fish and Wildlife Area",
 "official": null,
 "ours": {
  "acres": 685,
  "dissolved": {
   "after": 1364,
   "before": 1891,
   "copies": 1,
   "families": {
    "padus": 87,
    "sgwia": 640,
    "sgwid": 637
   },
   "family_fold": 724,
   "family_used": "sgwia",
   "key_union": 685,
   "parts": 0,
   "records": 76,
   "summed": 640,
   "tracts": 75
  },
  "family_fold": "layers {'sgwia': 640, 'padus': 87, 'sgwid': 637}: one land in 3 layers, the sgwia copy used (724 ac of copies not added)",
  "manager": "",
  "note": "76 joined records = 75 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1891 -> 1364 acres",
  "pieces": [
   [
    "sgwia712751",
    "Willow Creek Fishery Area",
    529,
    "name"
   ],
   [
    "sgwia713971",
    "Willow Creek Fishery Area",
    111,
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
 "t": "State Fish and Wildlife Area",
 "verdict": "no size on page"
}
```

## US-12776 Trout-Nace Creek State Fish and Wildlife Area
```json
{
 "cause": "agency smaller: our outline may hold water, a lease or a neighbour tract",
 "checked": "2026-11-22",
 "handover": [],
 "n": "Trout-Nace Creek State Fish and Wildlife Area",
 "official": {
  "acres": 46.0,
  "as": "46 acre",
  "clean": false,
  "line": "la Millpond. It contains clear, hard water and is rated as a class I trout stream. The Department manages one 46 acre parcel of land at the northwest corner of the intersection of Wasrud and Trout Creek Roads in section 30 of I",
  "read": "2026-11-22",
  "sent": "The Department manages one 46 acre parcel of land at the northwest corner of the intersection of Wasrud and Trout Creek Roads in section 30 of Iola Township.",
  "url": "https://dnr.wisconsin.gov/topic/Lands/FisheriesAreas/2650trout-nace.html",
  "why": "total-looking"
 },
 "ours": {
  "acres": 193,
  "dissolved": {
   "after": 199,
   "before": 386,
   "copies": 1,
   "families": {
    "padus": 45,
    "sgwia": 126,
    "sgwid": 28
   },
   "family_fold": 73,
   "family_used": "sgwia",
   "key_union": 193,
   "parts": 17,
   "records": 23,
   "summed": 126,
   "tracts": 5
  },
  "family_fold": "layers {'sgwia': 126, 'padus': 45, 'sgwid': 28}: one land in 3 layers, the sgwia copy used (73 ac of copies not added)",
  "manager": "",
  "note": "23 joined records = 5 tracts: 1 copies of a tract (same acres, another layer) and 17 fee tracts under a designation record folded; summed 386 -> 199 acres",
  "pieces": [
   [
    "sgwia713963",
    "Trout-Nace Creek Fishery Area",
    126,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 320,
 "same_agency": false,
 "score": 6,
 "t": "State Fish and Wildlife Area",
 "verdict": "off"
}
```

## US-4271 Beaver Brook State Wildlife Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Beaver Brook State Wildlife Area",
 "official": {
  "acres": 1964.0,
  "as": "1,964 acre",
  "clean": true,
  "line": "am LinkedIn Search Lands_Content Page_Beaver Brook Wildlife Area Beaver Brook Wildlife Area Beaver Brook is a 1,964-acre property located in southeast Washburn County. Because it is nestled between the cities of Shell Lake and Spo",
  "read": "2026-11-22",
  "sent": "Beaver Brook is a 1,964-acre property located in southeast Washburn County.",
  "url": "https://dnr.wisconsin.gov/topic/Lands/WildlifeAreas/beaverbrook.html",
  "why": "clean total"
 },
 "ours": {
  "acres": 1914,
  "dissolved": {
   "after": 3232,
   "before": 7703,
   "copies": 19,
   "families": {
    "padus": 40,
    "sgwia": 1914,
    "sgwid": 1278
   },
   "family_fold": 1318,
   "family_used": "sgwia",
   "parts": 21,
   "records": 81,
   "tracts": 41
  },
  "family_fold": "layers {'sgwia': 1914, 'padus': 40, 'sgwid': 1278}: one land in 3 layers, the sgwia copy used (1,318 ac of copies not added)",
  "manager": "",
  "note": "81 joined records = 41 tracts: 19 copies of a tract (same acres, another layer) and 21 fee tracts under a designation record folded; summed 7703 -> 3232 acres",
  "pieces": [
   [
    "sgwia713314",
    "Beaver Brook Wildlife Area",
    1914,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 2
 },
 "owner_now": null,
 "pct": 3,
 "same_agency": false,
 "score": 8,
 "t": "State Wildlife Area",
 "verdict": "agree"
}
```
