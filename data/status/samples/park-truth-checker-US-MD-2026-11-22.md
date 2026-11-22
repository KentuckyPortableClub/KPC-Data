# park truth checker: US-MD random sample of 12 (2026-11-22; seed = date + area, same rows for everyone)

Source file: `data/truth/US-MD.json`

## US-10773 Masemore Hemlock Ravines Natural Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Masemore Hemlock Ravines Natural Area",
 "official": {
  "acres": 215.0,
  "as": "215 acres",
  "clean": false,
  "line": "er than 20 stands of eastern hemlock have been documented in the Piedmont portion of Maryland, totaling about 215 acres. While many of these stands are now isolated, it is believed that they were once part of a widespread forest",
  "read": "2026-11-22",
  "sent": "Fewer than 20 stands of eastern hemlock have been documented in the Piedmont portion of Maryland, totaling about 215 acres.",
  "url": "https://dnr.maryland.gov/wildlife/Pages/NaturalAreas/Central/Masemore-Hemlock-Ravines.aspx",
  "why": "history"
 },
 "ours": {
  "acres": 0,
  "manager": "",
  "pieces": [],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": null,
 "same_agency": false,
 "score": 6,
 "t": "Natural Area",
 "verdict": "ours unknown"
}
```

## US-4765 Garrett State Forest
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-22",
 "handover": [],
 "n": "Garrett State Forest",
 "official": {
  "acres": 19000.0,
  "as": "19,000 acres",
  "clean": true,
  "line": ", Trapping, and Permits ​Fore​st M​anage​ment ​ ​ Overview​ Potomac-Garrett State Forest covers approximately 19,000 acres in southwestern Garrett County. The Garrett brothers' 1906 donation of ​ 1,977 acres established the original",
  "read": "2026-11-22",
  "sent": "Potomac-Garrett State Forest covers approximately 19,000 acres in southwestern Garrett County.",
  "url": "https://dnr.maryland.gov/forests/pages/publiclands/western_potomacgarrettforest.aspx",
  "why": "clean total"
 },
 "ours": {
  "acres": 7545,
  "manager": "",
  "pieces": [
   [
    56781,
    "Garrett Sf",
    5192,
    "name"
   ],
   [
    56780,
    "Garrett Sf",
    1242,
    "name"
   ],
   [
    9275,
    "Garrett State Forest",
    998,
    "name"
   ],
   [
    56783,
    "Garrett State Forest",
    821,
    "name"
   ],
   [
    9274,
    "Garrett State Forest",
    62,
    "name"
   ],
   [
    9273,
    "Garrett State Forest",
    10,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 2
 },
 "owner_now": null,
 "pct": 60,
 "same_agency": false,
 "score": 6,
 "t": "State Forest",
 "verdict": "off"
}
```

## US-7738 Ellis Bay Wildlife Management Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Ellis Bay Wildlife Management Area",
 "official": {
  "acres": 3200.0,
  "as": "3,200 acre",
  "clean": true,
  "line": "life & Heritage Service​ ​​​​​​​ Ellis Bay WMA Main_Content Mostly marsh and forested wetland, Ellis Bay is a 3,200-acre wet wonderland. It is perfect habitat for ducks and wading birds, like herons and egrets. White-tailed deer a",
  "read": "2026-11-22",
  "sent": "Mostly marsh and forested wetland, Ellis Bay is a 3,200-acre wet wonderland.",
  "url": "https://dnr.maryland.gov/wildlife/pages/publiclands/eastern/ellisbay.aspx",
  "why": "clean total"
 },
 "ours": {
  "acres": 3061,
  "manager": "",
  "pieces": [
   [
    56502,
    "Ellis Bay Wma",
    2730,
    "name"
   ],
   [
    56504,
    "Ellis Bay Wma",
    322,
    "name"
   ],
   [
    56500,
    "Ellis Bay Wma",
    9,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 6
 },
 "owner_now": null,
 "pct": 4,
 "same_agency": false,
 "score": 8,
 "t": "Wildlife Management Area",
 "verdict": "agree"
}
```

## US-4769 Salem State Forest
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Salem State Forest",
 "official": {
  "acres": 902.0,
  "as": "902 acres",
  "clean": false,
  "line": "he management of the property with other disciplines in the Department of Natural Resources. This property is 902 acres and is entirely wooded with opportunities for hiking, mountain biking and equestrian use. The Salem State For",
  "read": "2026-11-22",
  "sent": "This property is 902 acres and is entirely wooded with opportunities for hiking, mountain biking and equestrian use.",
  "url": "https://dnr.maryland.gov/forests/pages/publiclands/southern_salemforest.aspx",
  "why": "total-looking"
 },
 "ours": {
  "acres": 920,
  "manager": "",
  "pieces": [
   [
    56822,
    "Salem State Forest",
    920,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 2,
 "same_agency": false,
 "score": 8,
 "t": "State Forest",
 "verdict": "agree"
}
```

## US-0669 Piscataway Park
```json
{
 "checked": "2026-11-22",
 "handover": [
  {
   "date_hint": null,
   "kind": "managed by",
   "line": "Check out the boardwalk while there. National Colonial Farm - located in Piscataway Park. The farm is operated by the Accokeek Foundation, a partner of the park. Museum Collections - a sample of what is in the collection of the park. Las",
   "owner_now": "Accokeek Foundation",
   "src": "https://www.nps.gov/pisc/learn/index.htm",
   "why": "about / history page of the park's site"
  }
 ],
 "n": "Piscataway Park",
 "official": null,
 "ours": {
  "acres": 1951,
  "manager": "",
  "pieces": [
   [
    3539,
    "Piscataway Park",
    1937,
    "name"
   ],
   [
    83630,
    "Piscataway Road Park",
    14,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": "Accokeek Foundation",
 "pct": null,
 "score": 5,
 "t": "Park",
 "verdict": "no size on page"
}
```

## US-0735 Harpers Ferry National Historical Park
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Harpers Ferry National Historical Park",
 "note": "whole park compared (POTA lists it in 3 states: {'US-VA': 488, 'US-MD': 798, 'US-WV': 2184})",
 "official": null,
 "ours": {
  "acres": 3470,
  "acres_by_state": {
   "US-MD": 798,
   "US-VA": 488,
   "US-WV": 2184
  },
  "manager": "",
  "pieces": [
   [
    3205,
    "Harpers Ferry National Historical Park",
    798,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "states": [
   "US-VA",
   "US-MD",
   "US-WV"
  ],
  "unknown_pieces": 0,
  "whole_park": true
 },
 "owner_now": null,
 "pct": null,
 "score": 5,
 "t": "National Historical Park",
 "verdict": "no size on page"
}
```

## US-7757 Chicamuxen Wildlife Management Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Chicamuxen Wildlife Management Area",
 "official": {
  "acres": 382.0,
  "as": "382 acre",
  "clean": true,
  "line": "elds Disabled Hunter Access Contact the Wildlife & Heritage Service​ ​​​​​​​ Chicamuxen WMA Main_Content This 382-acre site situated along the Chicamuxen Creek, a Potomac River tributary, in western Charles County consists of pr",
  "read": "2026-11-22",
  "sent": "This 382-acre site situated along the Chicamuxen Creek, a Potomac River tributary, in western Charles County consists of prime marshlands as well as uplands, rolling forested habitats, and agricultural fields.",
  "url": "https://dnr.maryland.gov/wildlife/pages/publiclands/southern/chicamuxen.aspx",
  "why": "clean total"
 },
 "ours": {
  "acres": 382,
  "manager": "",
  "pieces": [
   [
    56489,
    "Chicamuxen Wma",
    382,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 0,
 "same_agency": false,
 "score": 7,
 "t": "Wildlife Management Area",
 "verdict": "agree"
}
```

## US-10768 South Savage Mountain Natural Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "South Savage Mountain Natural Area",
 "official": {
  "acres": 2000.0,
  "as": "2,000 acres",
  "clean": true,
  "line": "tive aquatic species, including fish such as brook trout. South Savage Mountain Natural Area encompasses over 2,000 acres and provides habitat for more than a dozen rare plants and animals. It is contained within Savage River State",
  "read": "2026-11-22",
  "sent": "South Savage Mountain Natural Area encompasses over 2,000 acres and provides habitat for more than a dozen rare plants and animals.",
  "url": "https://dnr.maryland.gov/wildlife/Pages/NaturalAreas/Western/South-Savage-Mountain.aspx",
  "why": "clean total"
 },
 "ours": {
  "acres": 0,
  "manager": "",
  "pieces": [],
  "pin": "just outside",
  "src": "",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": null,
 "same_agency": false,
 "score": 5,
 "t": "Natural Area",
 "verdict": "ours unknown"
}
```

## US-7728 Gwynnbrook Wildlife Management Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Gwynnbrook Wildlife Management Area",
 "official": {
  "acres": 88.0,
  "as": "88 acre",
  "clean": false,
  "line": "s located on Gwynnbrook Avenue, just off Owings Mills Boulevard in Owings Mills. Originally a game farm, this 88 acre tract was purchased by the State in 1919, making it the oldest wildlife management area in Maryland. Click He",
  "read": "2026-11-22",
  "sent": "Originally a game farm, this 88 acre tract was purchased by the State in 1919, making it the oldest wildlife management area in Maryland.",
  "url": "https://dnr.maryland.gov/wildlife/Pages/publiclands/central/gwynnbrook.aspx",
  "why": "history"
 },
 "ours": {
  "acres": 87,
  "manager": "",
  "pieces": [
   [
    56525,
    "Gwynnbrook Wma",
    87,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 1,
 "same_agency": false,
 "score": 8,
 "t": "Wildlife Management Area",
 "verdict": "agree"
}
```

## US-7772 Prathers Neck Wildlife Management Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Prathers Neck Wildlife Management Area",
 "official": {
  "acres": 215.0,
  "as": "215 acre",
  "clean": false,
  "line": "d-growth forests provide important habitat for many rare, threatened, or endangered species. What To See This 215-acre property is dominated by a mixture of oak/poplar forest habitat, with several old fields in early stages of s",
  "read": "2026-11-22",
  "sent": "This 215-acre property is dominated by a mixture of oak/poplar forest habitat, with several old fields in early stages of succession.",
  "url": "https://dnr.maryland.gov/wildlife/pages/publiclands/western/prathersneck.aspx",
  "why": "part (a lake, a purchase, a campground…)"
 },
 "ours": {
  "acres": 215,
  "manager": "",
  "pieces": [
   [
    56570,
    "Prathers Neck Wma",
    215,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 0,
 "same_agency": false,
 "score": 8,
 "t": "Wildlife Management Area",
 "verdict": "agree"
}
```

## US-4766 Green Ridge State Forest
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Green Ridge State Forest",
 "official": {
  "acres": 49012.0,
  "as": "49,012 acres",
  "clean": false,
  "line": "es. ​​ Trail Map ​ Rec​reation and Trails Hunting, Trapping, and Permits ​Fore​st M​anag​ement ​ ​Overview At 49,012 acres, Green Ridge is the largest contiguous block of public land in Maryland and the only state forest in the Ridg",
  "read": "2026-11-22",
  "sent": "At 49,012 acres, Green Ridge is the largest contiguous block of public land in Maryland and the only state forest in the Ridge and Valley physiographic province.",
  "url": "https://dnr.maryland.gov/forests/pages/publiclands/western_greenridgeforest.aspx",
  "why": "total-looking"
 },
 "ours": {
  "acres": 50805,
  "dissolved": {
   "after": 44938,
   "before": 49490,
   "copies": 0,
   "key_union": 50805,
   "parts": 8,
   "records": 14,
   "summed": 44938,
   "tracts": 6
  },
  "manager": "",
  "note": "14 joined records = 6 tracts: 0 copies of a tract (same acres, another layer) and 8 fee tracts under a designation record folded; summed 49490 -> 44938 acres",
  "pieces": [
   [
    56786,
    "Green Ridge Sf",
    39813,
    "name"
   ],
   [
    56788,
    "Green Ridge Sf",
    4564,
    "name"
   ],
   [
    56792,
    "Green Ridge State Forest",
    367,
    "name"
   ],
   [
    9278,
    "Green Ridge State Forest",
    160,
    "name"
   ],
   [
    9276,
    "Green Ridge State Forest",
    32,
    "name"
   ],
   [
    9280,
    "Green Ridge State Forest",
    2,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 5
 },
 "owner_now": null,
 "pct": 4,
 "same_agency": false,
 "score": 8,
 "t": "State Forest",
 "verdict": "agree"
}
```

## US-1566 Cunningham Falls State Park
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 4,400 acre, no total words near it)",
 "checked": "2026-11-22",
 "handover": [],
 "n": "Cunningham Falls State Park",
 "official": {
  "acres": 4400.0,
  "as": "4,400 acre",
  "clean": false,
  "line": "time. No other facility use service charges will be waived. ​​​ Hunting Policy: General hunting permitted in 4,400 acre designated hunting area Nighttime furbearer hunting by permit only Hunting permitted Monday-Saturday Hunt fro",
  "read": "2026-11-22",
  "sent": "General hunting permitted in 4,400 acre designated hunting area",
  "url": "https://dnr.maryland.gov/publiclands/pages/western/cunningham.aspx",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 6411,
  "manager": "",
  "pieces": [
   [
    56626,
    "Cunningham Falls Sp",
    46,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 9
 },
 "owner_now": null,
 "pct": 46,
 "same_agency": false,
 "score": 7,
 "t": "State Park",
 "verdict": "unsure"
}
```
