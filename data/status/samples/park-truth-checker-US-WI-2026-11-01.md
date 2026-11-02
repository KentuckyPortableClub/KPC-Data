# park truth checker: US-WI random sample of 12 (2026-11-01; seed = date + area, same rows for everyone)

Source file: `data/truth/US-WI.json`

## US-4271 Beaver Brook State Wildlife Area
```json
{
 "cause": "agency smaller: our outline may hold water, a lease or a neighbour tract",
 "checked": "2026-11-01",
 "handover": [],
 "n": "Beaver Brook State Wildlife Area",
 "official": {
  "acres": 1964.0,
  "as": "1,964 acre",
  "clean": true,
  "line": "am LinkedIn Search Lands_Content Page_Beaver Brook Wildlife Area Beaver Brook Wildlife Area Beaver Brook is a 1,964-acre property located in southeast Washburn County. Because it is nestled between the cities of Shell Lake and Spo",
  "read": "2026-11-01",
  "sent": "Beaver Brook is a 1,964-acre property located in southeast Washburn County.",
  "url": "https://dnr.wisconsin.gov/topic/Lands/WildlifeAreas/beaverbrook.html",
  "why": "clean total"
 },
 "ours": {
  "acres": 2507,
  "dissolved": {
   "after": 3156,
   "before": 7660,
   "copies": 19,
   "families": {
    "padus": 40,
    "sgwid": 1202,
    "wid": 1914
   },
   "family_fold": 1242,
   "family_used": "wid",
   "key_union": 2507,
   "parts": 21,
   "records": 77,
   "summed": 1914,
   "tracts": 37
  },
  "family_fold": "layers {'wid': 1914, 'padus': 40, 'sgwid': 1202}: one land in 3 layers, the wid copy used (1,242 ac of copies not added)",
  "manager": "",
  "note": "77 joined records = 37 tracts: 19 copies of a tract (same acres, another layer) and 21 fee tracts under a designation record folded; summed 7660 -> 3156 acres",
  "pieces": [
   [
    "wid709794",
    "Beaver Brook Wildlife Area",
    1914,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 6
 },
 "owner_now": null,
 "pct": 28,
 "same_agency": false,
 "score": 6,
 "t": "State Wildlife Area",
 "verdict": "off"
}
```

## US-10643 Blue River State Fish and Wildlife Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Blue River State Fish and Wildlife Area",
 "official": null,
 "ours": {
  "acres": 801,
  "dissolved": {
   "after": 717,
   "before": 1395,
   "copies": 3,
   "families": {
    "padus": 242,
    "sgwid": 328,
    "wid": 147
   },
   "family_fold": 389,
   "family_used": "sgwid",
   "key_union": 801,
   "parts": 22,
   "records": 48,
   "summed": 328,
   "tracts": 23
  },
  "family_fold": "layers {'padus': 242, 'wid': 147, 'sgwid': 328}: one land in 3 layers, the sgwid copy used (389 ac of copies not added)",
  "manager": "",
  "note": "48 joined records = 23 tracts: 3 copies of a tract (same acres, another layer) and 22 fee tracts under a designation record folded; summed 1395 -> 717 acres",
  "pieces": [
   [
    "sgwid19714485",
    "Rem-Blue River",
    40,
    "reviewed"
   ],
   [
    "sgwid19714486",
    "Rem-Blue River",
    40,
    "reviewed"
   ],
   [
    "sgwid19714487",
    "Rem-Blue River",
    40,
    "reviewed"
   ],
   [
    "sgwid19714488",
    "Rem-Blue River",
    40,
    "reviewed"
   ],
   [
    "sgwid19714489",
    "Rem-Blue River",
    40,
    "reviewed"
   ],
   [
    "sgwid19714490",
    "Rem-Blue River",
    40,
    "reviewed"
   ],
   [
    "sgwid19688556",
    "Rem-Blue River",
    10,
    "reviewed"
   ],
   [
    "sgwid19682458",
    "Rem-Blue River",
    7,
    "reviewed"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 18
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "State Fish and Wildlife Area",
 "verdict": "no size on page"
}
```

## US-9790 Gandy Dancer State Trail
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Gandy Dancer State Trail",
 "official": null,
 "ours": {
  "acres": 6410,
  "dissolved": {
   "after": 2204,
   "before": 3084,
   "copies": 2,
   "families": {
    "padus": 868,
    "sgwid": 456,
    "wid": 880
   },
   "family_fold": 1324,
   "family_used": "wid",
   "key_union": 6410,
   "parts": 0,
   "records": 118,
   "summed": 880,
   "tracts": 116
  },
  "family_fold": "layers {'padus': 868, 'wid': 880, 'sgwid': 456}: one land in 3 layers, the wid copy used (1,324 ac of copies not added)",
  "manager": "",
  "note": "118 joined records = 116 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 3084 -> 2204 acres",
  "pieces": [
   [
    "wid710144",
    "Gandy Dancer State Trail",
    850,
    "name"
   ],
   [
    "wid710788",
    "Gandy Dancer State Trail",
    30,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 17
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "State Trail",
 "verdict": "no size on page"
}
```

## US-1461 Lakeshore State Park
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Lakeshore State Park",
 "official": null,
 "ours": {
  "acres": 90,
  "dissolved": {
   "after": 63,
   "before": 173,
   "copies": 1,
   "families": {
    "sgwia": 52,
    "sgwid": 11
   },
   "family_fold": 11,
   "family_used": "sgwia",
   "key_union": 90,
   "parts": 6,
   "records": 11,
   "summed": 52,
   "tracts": 4
  },
  "family_fold": "layers {'sgwia': 52, 'sgwid': 11}: one land in 2 layers, the sgwia copy used (11 ac of copies not added)",
  "manager": "",
  "note": "11 joined records = 4 tracts: 1 copies of a tract (same acres, another layer) and 6 fee tracts under a designation record folded; summed 173 -> 63 acres",
  "pieces": [
   [
    "sgwia710122",
    "Lakeshore State Park",
    52,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 10
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-10196 St. Croix Islands State Wildlife Area
```json
{
 "cause": "agency smaller: our outline may hold water, a lease or a neighbour tract",
 "checked": "2026-11-01",
 "handover": [],
 "n": "St. Croix Islands State Wildlife Area",
 "official": {
  "acres": 1082.0,
  "as": "1,082 acre",
  "clean": false,
  "line": "Page_St. Croix Islands Wildlife Area St. Croix Islands Wildlife Area The St. Croix Islands Wildlife Area is a 1,082-acre property located in northwestern St. Croix County. This unique property includes numerous islands and wetland",
  "read": "2026-11-01",
  "sent": "Croix Islands Wildlife Area is a 1,082-acre property located in northwestern St.",
  "url": "https://dnr.wisconsin.gov/topic/Lands/WildlifeAreas/stcroixislands.html",
  "why": "total-looking"
 },
 "ours": {
  "acres": 1464,
  "dissolved": {
   "after": 2225,
   "before": 4980,
   "copies": 5,
   "families": {
    "padus": 1244,
    "sgwid": 981
   },
   "family_fold": 981,
   "family_used": "padus",
   "key_union": 1464,
   "parts": 26,
   "records": 57,
   "summed": 1244,
   "tracts": 26
  },
  "family_fold": "layers {'padus': 1244, 'sgwid': 981}: one land in 2 layers, the padus copy used (981 ac of copies not added)",
  "manager": "",
  "note": "57 joined records = 26 tracts: 5 copies of a tract (same acres, another layer) and 26 fee tracts under a designation record folded; summed 4980 -> 2225 acres",
  "pieces": [
   [
    272904,
    "St Croix Islands Wildlife Area",
    1244,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 3
 },
 "owner_now": null,
 "pct": 35,
 "same_agency": false,
 "score": 5,
 "t": "State Wildlife Area",
 "verdict": "off"
}
```

## US-1443 Buckhorn State Park
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-01",
 "handover": [],
 "n": "Buckhorn State Park",
 "official": {
  "acres": 8000.0,
  "as": "8,000 acres",
  "clean": true,
  "line": "s, hunters, hikers, campers and nature lovers. The park and two adjacent state wildlife areas cover more than 8,000 acres on a peninsula in the Castle Rock Flowage of the Wisconsin River. Family and group campsites, unique cart-in",
  "read": "2026-11-01",
  "sent": "The park and two adjacent state wildlife areas cover more than 8,000 acres on a peninsula in the Castle Rock Flowage of the Wisconsin River.",
  "url": "https://dnr.wisconsin.gov/topic/parks/buckhorn",
  "why": "clean total"
 },
 "ours": {
  "acres": 5222,
  "dissolved": {
   "after": 10785,
   "before": 14779,
   "copies": 1,
   "families": {
    "padus": 6802,
    "sgwid": 3983
   },
   "family_fold": 3983,
   "family_used": "padus",
   "key_union": 5222,
   "parts": 0,
   "records": 166,
   "summed": 6802,
   "tracts": 165
  },
  "family_fold": "layers {'padus': 6802, 'sgwid': 3983}: one land in 2 layers, the padus copy used (3,983 ac of copies not added)",
  "manager": "",
  "note": "166 joined records = 165 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 14779 -> 10785 acres",
  "pieces": [
   [
    272299,
    "Buckhorn State Park",
    3999,
    "name"
   ],
   [
    272470,
    "Buckhorn Wildlife Area",
    1677,
    "name"
   ],
   [
    78256,
    "Buckhorn State Park 3",
    926,
    "words"
   ],
   [
    78247,
    "Buckhorn State Park",
    200,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 24
 },
 "owner_now": null,
 "pct": 35,
 "same_agency": false,
 "score": 6,
 "t": "State Park",
 "verdict": "off"
}
```

## US-9867 Tiffany State Wildlife Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Tiffany State Wildlife Area",
 "official": {
  "acres": 13000.0,
  "as": "13,000 acre",
  "clean": true,
  "line": "LinkedIn Search Lands_Content Page_Tiffany Wildlife Area Tiffany Wildlife Area --> Tiffany Wildlife Area is a 13,000-acre property in Buffalo and Pepin counties and features diverse, abundant wildlife habitat. Split by the lower Ch",
  "read": "2026-11-01",
  "sent": "Tiffany Wildlife Area is a 13,000-acre property in Buffalo and Pepin counties and features diverse, abundant wildlife habitat.",
  "url": "https://dnr.wisconsin.gov/topic/Lands/WildlifeAreas/tiffany.html",
  "why": "clean total"
 },
 "ours": {
  "acres": 14011,
  "dissolved": {
   "after": 41279,
   "before": 55434,
   "copies": 14,
   "families": {
    "padus": 13485,
    "sgwid": 13783,
    "wid": 14011
   },
   "family_fold": 27268,
   "family_used": "wid",
   "parts": 0,
   "records": 458,
   "tracts": 444
  },
  "family_fold": "layers {'wid': 14011, 'padus': 13485, 'sgwid': 13783}: one land in 3 layers, the wid copy used (27,268 ac of copies not added)",
  "manager": "",
  "note": "458 joined records = 444 tracts: 14 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 55434 -> 41279 acres",
  "pieces": [
   [
    "wid709990",
    "Tiffany Wildlife Area",
    14004,
    "name"
   ],
   [
    "wid710728",
    "Tiffany Wildlife Area",
    7,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 29
 },
 "owner_now": null,
 "pct": 8,
 "same_agency": false,
 "score": 8,
 "t": "State Wildlife Area",
 "verdict": "agree"
}
```

## US-10642 Big Spring Creek State Fish and Wildlife Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Big Spring Creek State Fish and Wildlife Area",
 "official": null,
 "ours": {
  "acres": 253,
  "dissolved": {
   "after": 292,
   "before": 1159,
   "copies": 3,
   "key_union": 253,
   "parts": 11,
   "records": 16,
   "summed": 292,
   "tracts": 2
  },
  "manager": "",
  "note": "16 joined records = 2 tracts: 3 copies of a tract (same acres, another layer) and 11 fee tracts under a designation record folded; summed 1159 -> 292 acres",
  "pieces": [
   [
    "wid709259",
    "Rem-Big Spring Creek",
    287,
    "reviewed"
   ],
   [
    "wid710485",
    "Rem-Big Spring Creek",
    5,
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
 "t": "State Fish and Wildlife Area",
 "verdict": "no size on page"
}
```

## US-4254 Chimney Rock Oak Savanna State Natural Area
```json
{
 "cause": "our union: one of our pieces alone matches the agency (double count?)",
 "checked": "2026-11-01",
 "handover": [],
 "n": "Chimney Rock Oak Savanna State Natural Area",
 "official": {
  "acres": 30.0,
  "as": "30 acres",
  "clean": false,
  "line": ". Code [exit DNR] . Location Within the Chimney Rock Wildlife Area, Trempealeau County. T23N-R9W, Section 10. 30 acres. Driving directions From the intersection of County Highways D and V in Strum, go west on V for 3.2 miles, th",
  "read": "2026-11-01",
  "sent": "30 acres.",
  "url": "https://dnr.wisconsin.gov/topic/statenaturalareas/ChimneyRockOakSavanna",
  "why": "total-looking"
 },
 "ours": {
  "acres": 571,
  "manager": "",
  "pieces": [
   [
    272488,
    "Chimney Rock Wildlife Area",
    627,
    "reviewed-approx"
   ],
   [
    "sgwic7343",
    "Chimney Rock Oak Savanna",
    30,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 1803,
 "same_agency": false,
 "score": 6,
 "t": "State Natural Area",
 "verdict": "off"
}
```

## US-11937 Mecan River State Fish and Wildlife Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Mecan River State Fish and Wildlife Area",
 "official": null,
 "ours": {
  "acres": 6706,
  "dissolved": {
   "after": 13322,
   "before": 26789,
   "copies": 5,
   "families": {
    "padus": 6706,
    "sgwid": 6593,
    "wid": 23
   },
   "family_fold": 6616,
   "family_used": "padus",
   "parts": 0,
   "records": 294,
   "tracts": 289
  },
  "family_fold": "layers {'padus': 6706, 'sgwid': 6593, 'wid': 23}: one land in 3 layers, the padus copy used (6,616 ac of copies not added)",
  "manager": "",
  "note": "294 joined records = 289 tracts: 5 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 26789 -> 13322 acres",
  "pieces": [
   [
    272661,
    "Mecan River Fishery Area",
    6706,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 35
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "State Fish and Wildlife Area",
 "verdict": "no size on page"
}
```

## US-8209 Dewey Marsh State Natural Area
```json
{
 "cause": "agency smaller: our outline may hold water, a lease or a neighbour tract",
 "checked": "2026-11-01",
 "handover": [],
 "n": "Dewey Marsh State Natural Area",
 "official": {
  "acres": 801.0,
  "as": "801 acres",
  "clean": false,
  "line": "de [exit DNR] . Location Within Dewey Marsh Wildlife Area, Portage County. T25N-R8E, Sections 10, 11, 14, 15. 801 acres. Driving directions From the intersection of I-39 and Business Highway 51 on the north end of Stevens Point,",
  "read": "2026-11-01",
  "sent": "801 acres.",
  "url": "https://dnr.wisconsin.gov/topic/statenaturalareas/DeweyMarsh",
  "why": "total-looking"
 },
 "ours": {
  "acres": 5591,
  "family_fold": "layers {'padus': 6048, 'sgwic': 1222}: one land in 2 layers, the padus copy used (1,222 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    272522,
    "Dewey Marsh Wildlife Area",
    6048,
    "reviewed-approx"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 598,
 "same_agency": false,
 "score": 5,
 "t": "State Natural Area",
 "verdict": "off"
}
```

## US-4238 Ice Age National Scenic Trail
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Ice Age National Scenic Trail",
 "official": null,
 "ours": {
  "acres": 5095,
  "manager": "",
  "pieces": [
   [
    72062,
    "Ice Age Trail",
    5793,
    "reviewed"
   ],
   [
    272343,
    "Ice Age Trail - Wd",
    2453,
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
 "t": "National Scenic Trail",
 "verdict": "no size on page"
}
```
