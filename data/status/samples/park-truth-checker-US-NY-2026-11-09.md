# park truth checker: US-NY random sample of 12 (2026-11-09; seed = date + area, same rows for everyone)

Source file: `data/truth/US-NY.json`

## US-5030 Gillies Hill State Forest
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Gillies Hill State Forest",
 "official": {
  "acres": 2332.0,
  "as": "2,332 acre",
  "clean": false,
  "line": "Management Unit : 9P Map: Gillies Hill State Forest Map (GeoPDF) - GeoPDF Instructions || DECinfo Locator The 2,332-acre Gillies Hill State Forest is named after one of the early settlers on the long north-south ridge that separat",
  "read": "2026-11-09",
  "sent": "The 2,332-acre Gillies Hill State Forest is named after one of the early settlers on the long north-south ridge that separates the Black Creek and Baker Creek drainages.",
  "url": "https://www.dec.ny.gov/lands/53584.html",
  "why": "total-looking"
 },
 "ours": {
  "acres": 2328,
  "dissolved": {
   "after": 2328,
   "before": 4654,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 4654 -> 2328 acres",
  "pieces": [
   [
    "sgnya65896",
    "Gillies Hill State Forest",
    2328,
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

## US-2082 Irondequoit Bay Marine State Park
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Irondequoit Bay Marine State Park",
 "official": null,
 "ours": {
  "acres": 70,
  "family_fold": "layers {'padus': 70, 'sgnyb': 66}: one land in 2 layers, the padus copy used (66 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    237631,
    "Irondequoit Bay Marine Park",
    69,
    "name"
   ],
   [
    157183,
    "Irondequoit Bay Marine Park",
    1,
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

## US-5350 Turkey Hill State Forest
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Turkey Hill State Forest",
 "official": {
  "acres": 1119.0,
  "as": "1,119 acres",
  "clean": true,
  "line": "Hill State Forest Map (GeoPDF) - GeoPDF Instructions || DECinfo Locator Turkey Hill State Forest encompasses 1,119 acres. It is a popular area for recreational activities including hunting, trapping, snowmobiling, bird watching, a",
  "read": "2026-11-09",
  "sent": "Turkey Hill State Forest encompasses 1,119 acres.",
  "url": "https://www.dec.ny.gov/lands/37388.html",
  "why": "clean total"
 },
 "ours": {
  "acres": 1064,
  "dissolved": {
   "after": 1134,
   "before": 2253,
   "copies": 1,
   "key_union": 1064,
   "parts": 0,
   "records": 2,
   "summed": 1134,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 2253 -> 1134 acres",
  "pieces": [
   [
    236794,
    "Turkey Hill State Forest",
    1134,
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

## US-5003 East Branch Fish Creek State Forest
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "East Branch Fish Creek State Forest",
 "official": {
  "acres": 1350.0,
  "as": "1,350 acre",
  "clean": false,
  "line": "Unit : 6N Map: East Branch Fish Creek State Forest Map (GeoPDF) - GeoPDF Instructions || DECinfo Locator The 1,350-acre East Branch Fish Creek State Forest was purchased to establish a corridor along the East Branch of Fish Creek",
  "read": "2026-11-09",
  "sent": "The 1,350-acre East Branch Fish Creek State Forest was purchased to establish a corridor along the East Branch of Fish Creek.",
  "url": "https://www.dec.ny.gov/lands/8052.html",
  "why": "part (a lake, a purchase, a campground…)"
 },
 "ours": {
  "acres": 1522,
  "dissolved": {
   "after": 1400,
   "before": 2799,
   "copies": 0,
   "key_union": 1522,
   "parts": 2,
   "records": 3,
   "summed": 1400,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 0 copies of a tract (same acres, another layer) and 2 fee tracts under a designation record folded; summed 2799 -> 1400 acres",
  "pieces": [
   [
    236520,
    "East Branch Fish Creek State Forest",
    1400,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 13,
 "same_agency": false,
 "score": 8,
 "t": "State Forest",
 "verdict": "agree"
}
```

## US-9045 Genesee River Wildlife Management Area
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-09",
 "handover": [],
 "n": "Genesee River Wildlife Management Area",
 "official": {
  "acres": 310.0,
  "as": "310 acre",
  "clean": false,
  "line": "management, and wildlife-dependent recreation, such as hunting, fishing, trapping, and wildlife viewing. This 310 acre parcel is located on the west bank of the Genesee River and west of River Road in the Town of Willing in Alle",
  "read": "2026-11-09",
  "sent": "This 310 acre parcel is located on the west bank of the Genesee River and west of River Road in the Town of Willing in Allegany County.",
  "url": "https://www.dec.ny.gov/outdoor/123169.html",
  "why": "total-looking"
 },
 "ours": {
  "acres": 219,
  "dissolved": {
   "after": 318,
   "before": 635,
   "copies": 1,
   "key_union": 219,
   "parts": 0,
   "records": 2,
   "summed": 318,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 635 -> 318 acres",
  "pieces": [
   [
    "sgnya66908",
    "Genesee River Wildlife Management Area",
    318,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 29,
 "same_agency": false,
 "score": 6,
 "t": "Wildlife Management Area",
 "verdict": "off"
}
```

## US-2057 Franny Reese State Park
```json
{
 "checked": "2026-11-09",
 "handover": [
  {
   "date_hint": "2009",
   "kind": "transfer",
   "line": "memory of environmentalist Frances \"Franny\" Reese (1917-2003). In 2009, shortly after ownership was transferred to the Office of Parks, Recreation and Historic Preservation, the park officially opened. Please note: Deer ticks, which can transmit Lyme disease, are a growing problem in this area. Take",
   "owner_now": "Office of Parks",
   "src": "https://parks.ny.gov/parks/192/details.aspx",
   "why": "the park's page (data/parkinfo)"
  }
 ],
 "n": "Franny Reese State Park",
 "official": {
  "acres": 251.0,
  "as": "251 acres",
  "clean": false,
  "line": "ark to the Walkway Loop Trail and Walkway Over the Hudson State Historic Park . Scenic Hudson protected these 251 acres in 2003 and continues to manage this stunning landscape, named in memory of environmentalist Frances \"Franny\"",
  "read": "2026-11-09",
  "sent": "Scenic Hudson protected these 251 acres in 2003 and continues to manage this stunning landscape, named in memory of environmentalist Frances \"Franny\" Reese (1917-2003).",
  "url": "https://parks.ny.gov/parks/192/details.aspx",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 284,
  "dissolved": {
   "after": 251,
   "before": 501,
   "copies": 1,
   "key_union": 284,
   "parts": 0,
   "records": 2,
   "summed": 251,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 501 -> 251 acres",
  "pieces": [
   [
    237501,
    "Franny Reese Preserve State Park",
    251,
    "words"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": "Office of Parks",
 "pct": 13,
 "same_agency": false,
 "score": 8,
 "t": "State Park",
 "verdict": "agree"
}
```

## US-5297 Skyline Drive State Forest
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Skyline Drive State Forest",
 "official": {
  "acres": 533.0,
  "as": "533 acres",
  "clean": true,
  "line": "ne Drive State Forest Map (GeoPDF) - GeoPDF Instructions || DECinfo Locator Skyline Drive State Forest covers 533 acres and is ideal for hunting, trapping and fishing. No formal trails exist on the forest, however, a 2.3-mile pub",
  "read": "2026-11-09",
  "sent": "Skyline Drive State Forest covers 533 acres and is ideal for hunting, trapping and fishing.",
  "url": "https://www.dec.ny.gov/lands/8117.html",
  "why": "clean total"
 },
 "ours": {
  "acres": 534,
  "dissolved": {
   "after": 534,
   "before": 1067,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1067 -> 534 acres",
  "pieces": [
   [
    236739,
    "Skyline Drive State Forest",
    534,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 0,
 "same_agency": false,
 "score": 7,
 "t": "State Forest",
 "verdict": "agree"
}
```

## US-5084 Albert J. Woodford State Forest
```json
{
 "cause": "agency smaller: our outline may hold water, a lease or a neighbour tract",
 "checked": "2026-11-09",
 "handover": [],
 "n": "Albert J. Woodford State Forest",
 "official": {
  "acres": 2664.0,
  "as": "2,664 acres",
  "clean": false,
  "line": "Forest Map (GeoPDF) - GeoPDF Instructions || DECinfo Locator The Albert J. Woodford Memorial Forest contains 2,664 acres, and as with most state forests, the majority of this land was pasture and cropland at one time. Tassel Hill,",
  "read": "2026-11-09",
  "sent": "Woodford Memorial Forest contains 2,664 acres, and as with most state forests, the majority of this land was pasture and cropland at one time.",
  "url": "https://www.dec.ny.gov/lands/83241.html",
  "why": "total-looking"
 },
 "ours": {
  "acres": 3071,
  "dissolved": {
   "after": 2651,
   "before": 5300,
   "copies": 1,
   "key_union": 3071,
   "parts": 0,
   "records": 2,
   "summed": 2651,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 5300 -> 2651 acres",
  "pieces": [
   [
    236399,
    "Albert J. Woodford Memorial State Forest",
    2651,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 15,
 "same_agency": false,
 "score": 6,
 "t": "State Forest",
 "verdict": "off"
}
```

## US-2022 Burnham Point State Park
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 1,100 acres, no total words near it)",
 "checked": "2026-11-09",
 "handover": [],
 "n": "Burnham Point State Park",
 "official": {
  "acres": 1100.0,
  "as": "1,100 acres",
  "clean": false,
  "line": "more . Maps Hunting Map Nearby Properties Robert G. Wehle State Park Thousand Islands Region The park boasts 1,100 acres and spectacular Lake Ontario shorefront. Available for rent, the compounds private setting accommodates eight",
  "read": "2026-11-09",
  "sent": "The park boasts 1,100 acres and spectacular Lake Ontario shorefront.",
  "url": "https://parks.ny.gov/parks/burnhampoint/maps.aspx",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 11,
  "dissolved": {
   "after": 12,
   "before": 24,
   "copies": 1,
   "key_union": 11,
   "parts": 0,
   "records": 2,
   "summed": 12,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 24 -> 12 acres",
  "pieces": [
   [
    237465,
    "Burnham Point State Park",
    12,
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
 "t": "State Park",
 "verdict": "unsure"
}
```

## US-5045 Hammond Hill State Forest
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Hammond Hill State Forest",
 "official": {
  "acres": 3697.0,
  "as": "3,697 acres",
  "clean": false,
  "line": "Hammond Hill State Forest Map (GeoPDF) - GeoPDF Instructions || DECinfo Locator Hammond Hill State Forest is 3,697 acres and is a popular area for recreation. The 20-mile multiple-use trail system has been designed to offer family",
  "read": "2026-11-09",
  "sent": "Hammond Hill State Forest is 3,697 acres and is a popular area for recreation.",
  "url": "https://www.dec.ny.gov/lands/8204.html",
  "why": "total-looking"
 },
 "ours": {
  "acres": 4198,
  "dissolved": {
   "after": 3702,
   "before": 7401,
   "copies": 1,
   "key_union": 4198,
   "parts": 0,
   "records": 2,
   "summed": 3702,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 7401 -> 3702 acres",
  "pieces": [
   [
    "sgnya66082",
    "Hammond Hill State Forest",
    3702,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 14,
 "same_agency": false,
 "score": 8,
 "t": "State Forest",
 "verdict": "agree"
}
```

## US-5260 Popple Pond State Forest
```json
{
 "cause": "agency smaller: our outline may hold water, a lease or a neighbour tract",
 "checked": "2026-11-09",
 "handover": [],
 "n": "Popple Pond State Forest",
 "official": {
  "acres": 2461.0,
  "as": "2,461 acres",
  "clean": true,
  "line": "Pond State Forest Map (GeoPDF) - GeoPDF Instructions || DECinfo Locator Popple Pond State Forest encompasses 2,461 acres of land and offers a broad range of outdoor recreational opportunities. The majority of the land that makes u",
  "read": "2026-11-09",
  "sent": "Popple Pond State Forest encompasses 2,461 acres of land and offers a broad range of outdoor recreational opportunities.",
  "url": "https://www.dec.ny.gov/lands/107767.html",
  "why": "clean total"
 },
 "ours": {
  "acres": 2876,
  "dissolved": {
   "after": 2457,
   "before": 4912,
   "copies": 1,
   "key_union": 2876,
   "parts": 0,
   "records": 2,
   "summed": 2457,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 4912 -> 2457 acres",
  "pieces": [
   [
    236706,
    "Popple Pond State Forest",
    2457,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 17,
 "same_agency": false,
 "score": 6,
 "t": "State Forest",
 "verdict": "off"
}
```

## US-5152 California Road State Forest
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "California Road State Forest",
 "official": {
  "acres": 1410.0,
  "as": "1,410 acre",
  "clean": false,
  "line": "agement Unit : 6C Map: California Road State Forest Map (GeoPDF) - GeoPDF Instructions || DECinfo Locator The 1,410-acre California Road State Forest's topography is very hilly with thin soils and rocky exposed ridge tops predomin",
  "read": "2026-11-09",
  "sent": "The 1,410-acre California Road State Forest's topography is very hilly with thin soils and rocky exposed ridge tops predominating.",
  "url": "https://www.dec.ny.gov/lands/82768.html",
  "why": "total-looking"
 },
 "ours": {
  "acres": 1527,
  "dissolved": {
   "after": 1415,
   "before": 2829,
   "copies": 1,
   "key_union": 1527,
   "parts": 0,
   "records": 2,
   "summed": 1415,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 2829 -> 1415 acres",
  "pieces": [
   [
    236461,
    "California Road State Forest",
    1415,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 8,
 "same_agency": false,
 "score": 8,
 "t": "State Forest",
 "verdict": "agree"
}
```
