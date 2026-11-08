# park truth checker: US-IL random sample of 12 (2026-11-08; seed = date + area, same rows for everyone)

Source file: `data/truth/US-IL.json`

## US-10093 Rock Island Trail State Park
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-11-08",
 "handover": [
  {
   "date_hint": null,
   "kind": "transfer",
   "line": "late 1950s. Peoria's Forest Park Foundation acquired the abandoned railway corridor in June1965 and deeded the property to the Department of Conservation four years later. Officially dedicated in 1989, the Rock Island Trail is the first railway conversion completed by t",
   "owner_now": "Department of Conservation",
   "src": "https://dnr.illinois.gov/parks/about/park.rockislandtrail.html",
   "why": "about / history page of the park's site"
  }
 ],
 "n": "Rock Island Trail State Park",
 "official": null,
 "ours": {
  "acres": 851,
  "family_fold": "layers {'sgild': 732, 'padus': 341}: one land in 2 layers, the sgild copy used (341 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgild336",
    "Rock Island",
    732,
    "reviewed"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": "Department of Conservation",
 "pct": null,
 "score": 6,
 "t": "State Park",
 "verdict": "unsure"
}
```

## US-4138 Manito PHA State Park
```json
{
 "checked": "2026-11-08",
 "handover": [],
 "n": "Manito PHA State Park",
 "official": null,
 "ours": {
  "acres": 78,
  "dissolved": {
   "after": 78,
   "before": 156,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 156 -> 78 acres",
  "pieces": [
   [
    70867,
    "Manito State Habitat Area",
    78,
    "reviewed"
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

## US-1018 Red Hills State Park
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-08",
 "handover": [],
 "n": "Red Hills State Park",
 "official": {
  "acres": 967.0,
  "as": "967 acres",
  "clean": false,
  "line": "llinois, midway between Olney and Lawrenceville on U.S. 50, Red Hills is a carefully preserved and maintained 967 acres of high wooded hills, deep ravines, captivating meadows, and year-round springs. It's the perfect setting for",
  "read": "2026-11-08",
  "sent": "50, Red Hills is a carefully preserved and maintained 967 acres of high wooded hills, deep ravines, captivating meadows, and year-round springs.",
  "url": "https://dnr.illinois.gov/parks/park.redhills.html",
  "why": "total-looking"
 },
 "ours": {
  "acres": 811,
  "dissolved": {
   "after": 964,
   "before": 1928,
   "copies": 1,
   "key_union": 811,
   "parts": 0,
   "records": 2,
   "summed": 964,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1928 -> 964 acres",
  "pieces": [
   [
    70832,
    "Red Hills State Park",
    964,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 16,
 "same_agency": false,
 "score": 6,
 "t": "State Park",
 "verdict": "off"
}
```

## US-4127 Harry 'Babe' Woodyard State Natural Area
```json
{
 "checked": "2026-11-08",
 "handover": [],
 "n": "Harry 'Babe' Woodyard State Natural Area",
 "official": null,
 "ours": {
  "acres": 1440,
  "dissolved": {
   "after": 1337,
   "before": 2674,
   "copies": 1,
   "key_union": 1440,
   "parts": 0,
   "records": 2,
   "summed": 1337,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 2674 -> 1337 acres",
  "pieces": [
   [
    70770,
    "Harry \"Babe\" Woodyard State Natural Area",
    1337,
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
 "t": "State Natural Area",
 "verdict": "no size on page"
}
```

## US-12184 Heidecke Lake State Fish and Wildlife Area
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-11-08",
 "handover": [],
 "n": "Heidecke Lake State Fish and Wildlife Area",
 "official": null,
 "ours": {
  "acres": 1845,
  "dissolved": {
   "after": 4772,
   "before": 8125,
   "copies": 2,
   "families": {
    "padus": 839,
    "sgila": 1419,
    "sgild": 2514
   },
   "family_fold": 2258,
   "family_used": "sgild",
   "key_union": 1845,
   "parts": 0,
   "records": 5,
   "summed": 2514,
   "tracts": 3
  },
  "family_fold": "layers {'sgild': 2514, 'sgila': 1419, 'padus': 839}: one land in 3 layers, the sgild copy used (2,258 ac of copies not added)",
  "manager": "",
  "note": "5 joined records = 3 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 8125 -> 4772 acres",
  "pieces": [
   [
    "sgild141",
    "Heidecke Lake",
    2514,
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
 "t": "State Fish and Wildlife Area",
 "verdict": "unsure"
}
```

## US-4151 Sand Ridge State Forest
```json
{
 "checked": "2026-11-08",
 "handover": [],
 "n": "Sand Ridge State Forest",
 "official": {
  "acres": 7500.0,
  "as": "7,500 acres",
  "clean": false,
  "line": "ok over management of the site and the area became known as Sand Ridge State Forest. Today, the forest covers 7,500 acres—3,996 acres of native oak-hickory forest, 2,492 acres of pine and the rest in open fields and sand prairies.",
  "read": "2026-11-08",
  "sent": "Today, the forest covers 7,500 acres—3,996 acres of native oak-hickory forest, 2,492 acres of pine and the rest in open fields and sand prairies.",
  "url": "https://dnr.illinois.gov/parks/about/park.sandridge.html",
  "why": "part (a lake, a purchase, a campground…)"
 },
 "ours": {
  "acres": 6717,
  "dissolved": {
   "after": 7557,
   "before": 15112,
   "copies": 1,
   "key_union": 6717,
   "parts": 0,
   "records": 2,
   "summed": 7557,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 15112 -> 7557 acres",
  "pieces": [
   [
    70751,
    "Sand Ridge State Forest",
    7557,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 10,
 "same_agency": false,
 "score": 8,
 "t": "State Forest",
 "verdict": "agree"
}
```

## US-0286 Middle Mississippi River National Wildlife Refuge
```json
{
 "cause": "agency smaller: our outline may hold water, a lease or a neighbour tract",
 "checked": "2026-11-08",
 "handover": [],
 "n": "Middle Mississippi River National Wildlife Refuge",
 "official": {
  "acres": 2643.0,
  "as": "2,643 acres",
  "clean": false,
  "line": "Chester, Illinois Rockwood Island Division - 1,261 acres near Rockwood, Illinois Wilkinson Island Division - 2,643 acres near Gorham, Illinois Middle Mississippi River National Wildlife Refuge lands were purchased in response to t",
  "read": "2026-11-08",
  "sent": "Wilkinson Island Division - 2,643 acres near Gorham, Illinois",
  "url": "https://www.fws.gov/refuge/middle-mississippi-river/about-us",
  "why": "total-looking"
 },
 "ours": {
  "acres": 6755,
  "dissolved": {
   "after": 13812,
   "before": 19990,
   "copies": 1,
   "families": {
    "padus": 6180,
    "sgila": 7632
   },
   "family_fold": 6180,
   "family_used": "sgila",
   "key_union": 6755,
   "parts": 0,
   "records": 3,
   "summed": 7632,
   "tracts": 2
  },
  "family_fold": "layers {'sgila': 7632, 'padus': 6180}: one land in 2 layers, the sgila copy used (6,180 ac of copies not added)",
  "manager": "",
  "note": "3 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 19990 -> 13812 acres",
  "pieces": [
   [
    "sgila1221",
    "Middle Mississippi River National Wildlife Refuge",
    7632,
    "reviewed"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 156,
 "same_agency": false,
 "score": 6,
 "t": "National Wildlife Refuge",
 "verdict": "off"
}
```

## US-0993 Fort Massac State Park
```json
{
 "checked": "2026-11-08",
 "handover": [],
 "n": "Fort Massac State Park",
 "official": {
  "acres": 1500.0,
  "as": "1,500 acre",
  "clean": false,
  "line": "ntire course of American history, and the perfect place to relax in soothing natural surroundings. The nearly 1,500-acre park is perfect for picnics, camping, hiking, fishing, boating, and seasonal hunting programs. The park also",
  "read": "2026-11-08",
  "sent": "The nearly 1,500-acre park is perfect for picnics, camping, hiking, fishing, boating, and seasonal hunting programs.",
  "url": "https://dnr.illinois.gov/parks/park.fortmassac.html",
  "why": "part (a lake, a purchase, a campground…)"
 },
 "ours": {
  "acres": 1389,
  "dissolved": {
   "after": 1389,
   "before": 2778,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 2778 -> 1389 acres",
  "pieces": [
   [
    70841,
    "Fort Massac State Park",
    1389,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 7,
 "same_agency": false,
 "score": 7,
 "t": "State Park",
 "verdict": "agree"
}
```

## US-1013 Morrison-Rockwood State Park
```json
{
 "checked": "2026-11-08",
 "handover": [],
 "n": "Morrison-Rockwood State Park",
 "official": {
  "acres": 1164.0,
  "as": "1,164 acres",
  "clean": true,
  "line": "aris Illinois Beach State Park Page Content Page Content History Morrison-Rockwood State Park is comprised of 1,164 acres, located north of Morrison in Whiteside County. It was established in 1971 and officially opened for day use",
  "read": "2026-11-08",
  "sent": "Morrison-Rockwood State Park is comprised of 1,164 acres, located north of Morrison in Whiteside County.",
  "url": "https://dnr.illinois.gov/parks/about/park.morrisonrockwood.html",
  "why": "clean total"
 },
 "ours": {
  "acres": 1147,
  "manager": "",
  "pieces": [
   [
    "sgila949",
    "Morrison-Rockwood State Park",
    1147,
    "reviewed"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 1,
 "same_agency": false,
 "score": 8,
 "t": "State Park",
 "verdict": "agree"
}
```

## US-1004 Kankakee River State Park
```json
{
 "checked": "2026-11-08",
 "handover": [],
 "n": "Kankakee River State Park",
 "official": {
  "acres": 4000.0,
  "as": "4,000 acres",
  "clean": true,
  "line": "the Kankakee River for 11 miles, in an area 6 miles northwest of Kankakee, the park consists of approximately 4,000 acres. Illinois Rt. 102 on the north and Illinois Rt. 113 on the south frame the park, with I-55 and I-57 both prov",
  "read": "2026-11-08",
  "sent": "Enveloping both sides of the Kankakee River for 11 miles, in an area 6 miles northwest of Kankakee, the park consists of approximately 4,000 acres.",
  "url": "https://dnr.illinois.gov/parks/park.kankakeeriver.html",
  "why": "clean total"
 },
 "ours": {
  "acres": 3686,
  "dissolved": {
   "after": 3686,
   "before": 7350,
   "copies": 1,
   "parts": 0,
   "records": 4,
   "tracts": 3
  },
  "manager": "",
  "note": "4 joined records = 3 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 7350 -> 3686 acres",
  "pieces": [
   [
    "sgila1046",
    "Kankakee River State Park",
    3665,
    "reviewed"
   ],
   [
    "sgilb197",
    "Kankakee River State Park Nature Preserve",
    20,
    "name"
   ],
   [
    71098,
    "Kankakee River Dam",
    1,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 8,
 "same_agency": false,
 "score": 7,
 "t": "State Park",
 "verdict": "agree"
}
```

## US-1020 Sam Parr State Park
```json
{
 "checked": "2026-11-08",
 "handover": [],
 "n": "Sam Parr State Park",
 "official": {
  "acres": 1180.0,
  "as": "1,180 acres",
  "clean": false,
  "line": "OBLONG - 11 miles Sam Parr State Fish & Wildlife Area Sa m Parr Sta te Fish & Wildli fe Area– Totaling 1,180 acres and featuring a 183-acre lake, Sam Parr State Fish & Wildlife Area is located 3 miles northeast of Newton.",
  "read": "2026-11-08",
  "sent": "Totaling 1,180 acres and featuring a 183-acre lake, Sam",
  "url": "https://dnr.illinois.gov/content/dam/soi/en/web/dnr/publications/documents/00000579.pdf",
  "why": "history"
 },
 "ours": {
  "acres": 1164,
  "manager": "",
  "pieces": [
   [
    "sgila1162",
    "Sam Parr State Fish and Wildlife Area",
    1164,
    "reviewed"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 1,
 "same_agency": false,
 "score": 8,
 "t": "State Park",
 "verdict": "agree"
}
```

## US-1015 Pere Marquette State Park
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-11-08",
 "handover": [],
 "n": "Pere Marquette State Park",
 "official": null,
 "ours": {
  "acres": 9494,
  "manager": "",
  "pieces": [
   [
    "sgila1404",
    "Pere Marquette State Park",
    10033,
    "reviewed"
   ],
   [
    71091,
    "Pere Marquette State Park",
    116,
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
 "verdict": "unsure"
}
```
