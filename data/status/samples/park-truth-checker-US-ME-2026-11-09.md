# park truth checker: US-ME random sample of 12 (2026-11-09; seed = date + area, same rows for everyone)

Source file: `data/truth/US-ME.json`

## US-0345 Sunkhaze Meadows National Wildlife Refuge
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-09",
 "handover": [],
 "n": "Sunkhaze Meadows National Wildlife Refuge",
 "official": {
  "acres": 30000.0,
  "as": "30,000 acres",
  "clean": false,
  "line": "National Wildlife Refuge is a northern treasure in the National Wildlife Refuge System. It consists of nearly 30,000 acres of federally protected lands in northeastern coastal Maine. The refuge's landscape is varied, with rolling hi",
  "read": "2026-11-09",
  "sent": "It consists of nearly 30,000 acres of federally protected lands in northeastern coastal Maine.",
  "url": "https://www.fws.gov/refuge/sunkhaze-meadows/about-us",
  "why": "total-looking"
 },
 "ours": {
  "acres": 12320,
  "dissolved": {
   "after": 11615,
   "before": 23230,
   "copies": 1,
   "key_union": 12320,
   "parts": 0,
   "records": 2,
   "summed": 11615,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 23230 -> 11615 acres",
  "pieces": [
   [
    4374,
    "Sunkhaze Meadows National Wildlife Refuge",
    11615,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 59,
 "same_agency": false,
 "score": 6,
 "t": "National Wildlife Refuge",
 "verdict": "off"
}
```

## US-2385 Cobscook Bay State Park
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-01",
 "handover": [
  {
   "date_hint": null,
   "kind": "transfer",
   "line": "had created along Whiting Bay. After approval by the Maine Legislature, management of the area was transferred to the State and Cobscook Bay State Park was established. ( back to top ) Activities Beaches Birdwatching Camping Canoeing Sea kayaking Walking (roads and p",
   "owner_now": "State and Cobscook Bay State Park",
   "src": "https://apps.web.maine.gov/cgi-bin/online/doc/parksearch/details.pl?park_id=15",
   "why": "the park's page (data/parkinfo)"
  }
 ],
 "last_read_failed": "2026-11-09",
 "n": "Cobscook Bay State Park",
 "official": {
  "acres": 888.0,
  "as": "888 acre",
  "clean": true,
  "line": "Please check the Bureau's Safety Page . About the Park The wildlife-rich waters of Cobscook Bay surround this 888-acre park on three sides, providing opportunities to watch birds and observe the ebb and flow of the region's impr",
  "read": "2026-11-01",
  "sent": "About the Park The wildlife-rich waters of Cobscook Bay surround this 888-acre park on three sides, providing opportunities to watch birds and observe the ebb and flow of the region's impressive tides.",
  "url": "https://apps.web.maine.gov/cgi-bin/online/doc/parksearch/details.pl?park_id=15",
  "why": "clean total"
 },
 "ours": {
  "acres": 1,
  "manager": "",
  "pieces": [
   [
    207053,
    "Cobscook Bay",
    1,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 2
 },
 "owner_now": "State and Cobscook Bay State Park",
 "pct": 100,
 "same_agency": false,
 "score": 5,
 "t": "State Park",
 "verdict": "off"
}
```

## US-8463 Madawaska Bog Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-09",
 "n": "Madawaska Bog Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 187,
  "dissolved": {
   "after": 292,
   "before": 583,
   "copies": 1,
   "key_union": 187,
   "parts": 0,
   "records": 2,
   "summed": 292,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 583 -> 292 acres",
  "pieces": [
   [
    206042,
    "Madawaska Bog Wildlife Management Area",
    292,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 5,
 "t": "Wildlife Management Area",
 "verdict": "no size on page"
}
```

## US-8487 Caribou Bog Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-09",
 "n": "Caribou Bog Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 1684,
  "dissolved": {
   "after": 2840,
   "before": 5737,
   "copies": 1,
   "families": {
    "padus": 879,
    "sgmeb": 1961
   },
   "family_fold": 879,
   "family_used": "sgmeb",
   "key_union": 1684,
   "parts": 3,
   "records": 11,
   "summed": 1961,
   "tracts": 7
  },
  "family_fold": "layers {'sgmeb': 1961, 'padus': 879}: one land in 2 layers, the sgmeb copy used (879 ac of copies not added)",
  "manager": "",
  "note": "11 joined records = 7 tracts: 1 copies of a tract (same acres, another layer) and 3 fee tracts under a designation record folded; summed 5737 -> 2840 acres",
  "pieces": [
   [
    "sgmeb9",
    "Caribou Bog WMA",
    1961,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 5,
 "t": "Wildlife Management Area",
 "verdict": "no size on page"
}
```

## US-8488 Pond Farm Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-09",
 "n": "Pond Farm Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 256,
  "dissolved": {
   "after": 318,
   "before": 636,
   "copies": 1,
   "key_union": 256,
   "parts": 0,
   "records": 2,
   "summed": 318,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 636 -> 318 acres",
  "pieces": [
   [
    206245,
    "Pond Farm Wildlife Management Area",
    318,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 5,
 "t": "Wildlife Management Area",
 "verdict": "no size on page"
}
```

## US-2390 Grafton Notch State Park
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-09",
 "n": "Grafton Notch State Park",
 "official": {
  "acres": 6400.0,
  "as": "10 square mile",
  "clean": true,
  "line": "of Maine's most beautiful vacation regions, the western mountains. The park consists of 869 remote acres, on 10-square mile Rangeley Lake. The lake is famous for landlocked salmon and trout fishing, and anglers who voluntarily \"catch",
  "read": "2026-11-01",
  "sent": "The park consists of 869 remote acres, on 10-square mile Rangeley Lake.",
  "url": "https://apps.web.maine.gov/cgi-bin/online/doc/parksearch/details.pl?park_id=1",
  "why": "clean total"
 },
 "ours": {
  "acres": 2697,
  "dissolved": {
   "after": 2914,
   "before": 2978,
   "copies": 0,
   "key_union": 2697,
   "parts": 2,
   "records": 11,
   "summed": 2914,
   "tracts": 9
  },
  "manager": "",
  "note": "11 joined records = 9 tracts: 0 copies of a tract (same acres, another layer) and 2 fee tracts under a designation record folded; summed 2978 -> 2914 acres",
  "pieces": [
   [
    207325,
    "Grafton Notch State Park",
    2651,
    "name"
   ],
   [
    207328,
    "Grafton Notch State Park",
    76,
    "name"
   ],
   [
    207332,
    "Grafton Notch State Park",
    64,
    "name"
   ],
   [
    207323,
    "Grafton Notch State Park",
    49,
    "name"
   ],
   [
    207324,
    "Grafton Notch State Park",
    35,
    "name"
   ],
   [
    207326,
    "Grafton Notch State Park",
    31,
    "name"
   ],
   [
    207322,
    "Grafton Notch State Park",
    6,
    "name"
   ],
   [
    207329,
    "Grafton Notch State Park",
    1,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 3
 },
 "owner_now": null,
 "pct": 58,
 "same_agency": false,
 "score": 6,
 "t": "State Park",
 "verdict": "off"
}
```

## US-0338 Cross Island National Wildlife Refuge
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-09",
 "handover": [],
 "n": "Cross Island National Wildlife Refuge",
 "official": {
  "acres": 1700.0,
  "as": "1,700 acres",
  "clean": true,
  "line": "x islands (Cross, Scotch, Outer Double Head Shot, Inner Double Head Shot, Mink, Old Man Islands) encompassing 1,700 acres in Cutler. The six offshore islands are 10 miles southeast of Machias in Machias Bay. Learn More About Visiti",
  "read": "2026-11-09",
  "sent": "Cross Island National Wildlife Refuge is comprised of six islands (Cross, Scotch, Outer Double Head Shot, Inner Double Head Shot, Mink, Old Man Islands) encompassing 1,700 acres in Cutler.",
  "url": "https://www.fws.gov/refuge/cross-island",
  "why": "clean total; the agency's pages disagree: another of its pages says 1,150 acres (that one matches our outline)"
 },
 "ours": {
  "acres": 1127,
  "dissolved": {
   "after": 1726,
   "before": 3452,
   "copies": 1,
   "key_union": 1127,
   "parts": 0,
   "records": 2,
   "summed": 1726,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 3452 -> 1726 acres",
  "pieces": [
   [
    3756,
    "Cross Island National Wildlife Refuge",
    1726,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 34,
 "same_agency": false,
 "score": 6,
 "t": "National Wildlife Refuge",
 "verdict": "off"
}
```

## US-9170 Machias River Corridor State Conservation Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Machias River Corridor State Conservation Area",
 "official": null,
 "ours": {
  "acres": 6782,
  "manager": "",
  "pieces": [
   [
    9752,
    "Machias River Watershed - MDOC",
    6131,
    "reviewed"
   ],
   [
    206758,
    "Machias River Phase I",
    5939,
    "reviewed"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": null,
 "score": 5,
 "t": "State Conservation Area",
 "verdict": "no size on page"
}
```

## US-2389 Fort Point State Park
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-09",
 "n": "Fort Point State Park",
 "official": {
  "acres": 120.0,
  "as": "120 acres",
  "clean": false,
  "line": "nt State Park occupies a long peninsula with panoramic views of the Penobscot River and Penobscot Bay. On its 120 acres, the park features more than a mile of rocky shore, a tidal sandbar, and diverse habitat for a variety of pla",
  "read": "2026-11-01",
  "sent": "On its 120 acres, the park features more than a mile of rocky shore, a tidal sandbar, and diverse habitat for a variety of plants and animals.",
  "url": "https://apps.web.maine.gov/cgi-bin/online/doc/parksearch/details.pl?park_id=33",
  "why": "total-looking"
 },
 "ours": {
  "acres": 100,
  "manager": "",
  "pieces": [
   [
    207320,
    "Fort Point State Park and Fort Pownal",
    147,
    "words"
   ],
   [
    207321,
    "Fort Point State Park and Fort Pownal",
    7,
    "words"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 17,
 "same_agency": false,
 "score": 5,
 "t": "State Park",
 "verdict": "off"
}
```

## US-2409 Sebago Lake State Park
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 1,400 acres, no total words near it)",
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-09",
 "n": "Sebago Lake State Park",
 "official": {
  "acres": 1400.0,
  "as": "1,400 acres",
  "clean": false,
  "line": "r-round recreation for thousands of visitors each year. Near the foothills of the White Mountains, the park's 1,400 acres features sandy beaches, extensive woodlands, ponds, bogs a river and diverse habitat for a wide variety of pl",
  "read": "2026-11-01",
  "sent": "Near the foothills of the White Mountains, the park's 1,400 acres features sandy beaches, extensive woodlands, ponds, bogs a river and diverse habitat for a wide variety of plant and animal life.",
  "url": "https://apps.web.maine.gov/cgi-bin/online/doc/parksearch/details.pl?park_id=26",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 2435,
  "dissolved": {
   "after": 3370,
   "before": 3376,
   "copies": 0,
   "key_union": 2435,
   "parts": 3,
   "records": 7,
   "summed": 3370,
   "tracts": 4
  },
  "manager": "",
  "note": "7 joined records = 4 tracts: 0 copies of a tract (same acres, another layer) and 3 fee tracts under a designation record folded; summed 3376 -> 3370 acres",
  "pieces": [
   [
    203839,
    "Sebago Lake Land Reserve",
    2130,
    "name"
   ],
   [
    207402,
    "Sebago Lake State Park",
    1231,
    "name"
   ],
   [
    207404,
    "Sebago Lake State Park",
    6,
    "name"
   ],
   [
    207406,
    "Sebago Lake State Park",
    3,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 74,
 "same_agency": false,
 "score": 7,
 "t": "State Park",
 "verdict": "unsure"
}
```

## US-2399 Owls Head State Park
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-09",
 "n": "Owls Head State Park",
 "official": null,
 "ours": {
  "acres": 8,
  "manager": "",
  "pieces": [
   [
    60868,
    "Owls Head Light",
    15,
    "name"
   ],
   [
    207363,
    "Owls Head Light State Park",
    15,
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

## US-8289 Bible Point State Historic Site
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-09",
 "n": "Bible Point State Historic Site",
 "official": null,
 "ours": {
  "acres": 60,
  "manager": "",
  "pieces": [
   [
    206979,
    "Bible Point",
    60,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 5,
 "t": "State Historic Site",
 "verdict": "no size on page"
}
```
