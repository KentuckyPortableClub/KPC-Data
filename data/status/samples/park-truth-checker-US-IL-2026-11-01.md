# park truth checker: US-IL random sample of 12 (2026-11-01; seed = date + area, same rows for everyone)

Source file: `data/truth/US-IL.json`

## US-4130 Horseshoe Lake-Alexander State Fish and Wildlife Area
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-10-29",
 "handover": [],
 "n": "Horseshoe Lake-Alexander State Fish and Wildlife Area",
 "official": {
  "acres": 10200.0,
  "as": "10,200 acre",
  "clean": false,
  "line": "e even more enjoyable. Located in Alexander County just east of Illinois Route 3, 7 miles north of Cairo, the 10,200 acre area includes a 2,400 acre shallow lake. In addition to taking in the beauty of the natural features of the a",
  "read": "2026-10-29",
  "sent": "Located in Alexander County just east of Illinois Route 3, 7 miles north of Cairo, the 10,200 acre area includes a 2,400 acre shallow lake.",
  "url": "https://dnr.illinois.gov/parks/park.horseshoelakealexandercounty.html",
  "why": "total-looking"
 },
 "ours": {
  "acres": 8492,
  "dissolved": {
   "after": 8492,
   "before": 16902,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 16902 -> 8492 acres",
  "pieces": [
   [
    "sgila1175",
    "Horseshoe Lake-Alexander State Fish and Wildlife Area",
    8492,
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
 "t": "State Fish and Wildlife Area",
 "verdict": "off"
}
```

## US-0997 Hennepin Canal Parkway State Park
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Hennepin Canal Parkway State Park",
 "official": {
  "acres": 4160.0,
  "as": "4,160 acre",
  "clean": false,
  "line": "by sandbars formed by waves at the mouth of the river, creating a sluggish, marshy habitat.&lt;/p>\\n&lt;p>The 4,160-acre park, consisting of two separate areas (North Unit and South Unit), offers ample opportunities for swimming,",
  "read": "2026-10-29",
  "sent": "idges are crowned by black oak forests with an open, savanna-like appearance.&nbsp;For much of the year, a stream known as Dead River is&nbsp;blocked by sandbars formed by waves at the mouth of the river, creating a sluggish, marshy habitat.&lt;/p>\\n&lt;p>The 4,160-acre park, consisting of two separ",
  "url": "https://dnr.illinois.gov/parks/park.hennepincanal.html",
  "why": "part (a lake, a purchase, a campground…)"
 },
 "ours": {
  "acres": 4322,
  "manager": "",
  "pieces": [
   [
    157220,
    "Hennepin Canal",
    4322,
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
 "score": 7,
 "t": "State Park",
 "verdict": "agree"
}
```

## US-0982 Buffalo Rock State Park
```json
{
 "checked": "2026-10-29",
 "handover": [
  {
   "date_hint": "1928",
   "kind": "transfer",
   "line": "larger area, donating the original site to the state to become a park. The deed to the property was turned over to the State of Illinois on November 15, 1928, with the provision that it would become a permanent state park and that the caretaker Robert Barnett, who was then 72 years of age, be retain",
   "owner_now": "State of Illinois",
   "src": "https://dnr.illinois.gov/parks/about/park.buffalorock.html",
   "why": "about / history page of the park's site"
  }
 ],
 "n": "Buffalo Rock State Park",
 "official": {
  "acres": 298.0,
  "as": "298 acre",
  "clean": false,
  "line": "nt, sweeping view of the Illinois River. Located approximately 3 miles west of Ottawa in LaSalle County, this 298-acre park has long been a favorite picnic area, as well as a nature lovers’ delight. The area of Buffalo Rock was",
  "read": "2026-10-29",
  "sent": "Located approximately 3 miles west of Ottawa in LaSalle County, this 298-acre park has long been a favorite picnic area, as well as a nature lovers’ delight.",
  "url": "https://dnr.illinois.gov/parks/park.buffalorock.html",
  "why": "part (a lake, a purchase, a campground…)"
 },
 "ours": {
  "acres": 295,
  "family_fold": "layers {'padus': 295, 'sgila': 259}: one land in 2 layers, the padus copy used (259 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    71086,
    "Buffalo Rock State Park",
    295,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": "State of Illinois",
 "pct": 1,
 "same_agency": false,
 "score": 7,
 "t": "State Park",
 "verdict": "agree"
}
```

## US-12184 Heidecke Lake State Fish and Wildlife Area
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Heidecke Lake State Fish and Wildlife Area",
 "official": {
  "acres": 1300.0,
  "as": "1,300 acres",
  "clean": false,
  "line": "r the Collins Power Plant, which now is owned and operated by Midwest Generation. The lake provides more than 1,300 acres of prime fishing opportunities. Heidecke Lake Closing Policy : If wind speeds are forecast to be 25mph or abo",
  "read": "2026-10-29",
  "sent": "The lake provides more than 1,300 acres of prime fishing opportunities.",
  "url": "https://dnr.illinois.gov/parks/park.heideckelake.html",
  "why": "part (a lake, a purchase, a campground…)"
 },
 "ours": {
  "acres": 1419,
  "dissolved": {
   "after": 2258,
   "before": 3097,
   "copies": 1,
   "families": {
    "padus": 839,
    "sgila": 1419
   },
   "family_fold": 839,
   "family_used": "sgila",
   "parts": 0,
   "records": 3,
   "tracts": 2
  },
  "family_fold": "layers {'sgila': 1419, 'padus': 839}: one land in 2 layers, the sgila copy used (839 ac of copies not added)",
  "manager": "",
  "note": "3 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 3097 -> 2258 acres",
  "pieces": [
   [
    "sgila1053",
    "Heidecke Lake State Fish and Wildlife Area",
    1419,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 9,
 "same_agency": false,
 "score": 8,
 "t": "State Fish and Wildlife Area",
 "verdict": "agree"
}
```

## US-7872 Stemler Cave Woods State Nature Preserve
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 194.82 acres, no total words near it)",
 "checked": "2026-10-29",
 "handover": [],
 "n": "Stemler Cave Woods State Nature Preserve",
 "official": {
  "acres": 194.8,
  "as": "194.82 acres",
  "clean": false,
  "line": "one-third of these depressions. Ownership Illinois Department of Natural Resources Dedicated April 1986 Size 194.82 acres Topographic Quad Columbia Google Maps For Further Information Illinois Department of Natural Resources - Worl",
  "read": "2026-10-29",
  "sent": "194.82 acres",
  "url": "https://dnr.illinois.gov/inpc/area.area7stclairstemlercavewoods.html",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 386,
  "dissolved": {
   "after": 558,
   "before": 944,
   "copies": 1,
   "families": {
    "padus": 386,
    "sgilb": 172
   },
   "family_fold": 172,
   "family_used": "padus",
   "parts": 0,
   "records": 6,
   "tracts": 5
  },
  "family_fold": "layers {'padus': 386, 'sgilb': 172}: one land in 2 layers, the padus copy used (172 ac of copies not added)",
  "manager": "",
  "note": "6 joined records = 5 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 944 -> 558 acres",
  "pieces": [
   [
    70786,
    "Stemler Cave Woods State Natural Area",
    386,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 98,
 "same_agency": false,
 "score": 7,
 "t": "State Nature Preserve",
 "verdict": "unsure"
}
```

## US-0283 Cypress Creek National Wildlife Refuge
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Cypress Creek National Wildlife Refuge",
 "official": {
  "acres": 15676.0,
  "as": "15,676 acres",
  "clean": false,
  "line": "s during a furbearer hunting season. Closed Areas A variety of wildlife dependent activities are permitted on 15,676 acres of the Cypress Creek National Wildlife Refuge. However, there are two areas closed to public access: Bellrose",
  "read": "2026-10-29",
  "sent": "A variety of wildlife dependent activities are permitted on 15,676 acres of the Cypress Creek National Wildlife Refuge.",
  "url": "https://www.fws.gov/refuge/cypress-creek/visit-us/rules-policies",
  "why": "total-looking"
 },
 "ours": {
  "acres": 16728,
  "dissolved": {
   "after": 16728,
   "before": 50025,
   "copies": 2,
   "parts": 0,
   "records": 3,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 50025 -> 16728 acres",
  "pieces": [
   [
    3760,
    "Cypress Creek National Wildlife Refuge",
    16728,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 7,
 "same_agency": false,
 "score": 8,
 "t": "National Wildlife Refuge",
 "verdict": "agree"
}
```

## US-4098 Lincoln Trail Homestead State Park
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Lincoln Trail Homestead State Park",
 "official": {
  "acres": 82.0,
  "as": "82 acre",
  "clean": true,
  "line": "Park Closure Park Closure Page Content Page Content The Lincoln Trail Homestead State Park and Memorial is a 82 acre (0.65 km²) state park located on the Sangamon River in Macon County near Harristown, Illinois. This important",
  "read": "2026-10-29",
  "sent": "The Lincoln Trail Homestead State Park and Memorial is a 82 acre (0.65 km²) state park located on the Sangamon River in Macon County near Harristown, Illinois.",
  "url": "https://dnr.illinois.gov/parks/park.lincolntrailhomestead.html",
  "why": "clean total"
 },
 "ours": {
  "acres": 71,
  "manager": "",
  "pieces": [
   [
    70907,
    "Lincoln Trail Homestead State Memorial",
    71,
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
 "score": 7,
 "t": "State Park",
 "verdict": "agree"
}
```

## US-4108 Banner Marsh State Fish and Wildlife Area
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Banner Marsh State Fish and Wildlife Area",
 "official": {
  "acres": 4363.0,
  "as": "4,363 acre",
  "clean": false,
  "line": "ricultural purposes and surfaced mined for coal. Today, Banner Marsh State Fish and Wildlife Area serves as a 4,363-acre freshwater marsh. More than 200 water bodies, and its vast acres of grassland and shrubland, provide excellen",
  "read": "2026-10-29",
  "sent": "Today, Banner Marsh State Fish and Wildlife Area serves as a 4,363-acre freshwater marsh.",
  "url": "https://dnr.illinois.gov/parks/about/park.bannermarsh.html",
  "why": "total-looking"
 },
 "ours": {
  "acres": 4359,
  "dissolved": {
   "after": 4359,
   "before": 8720,
   "copies": 0,
   "parts": 2,
   "records": 3,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 0 copies of a tract (same acres, another layer) and 2 fee tracts under a designation record folded; summed 8720 -> 4359 acres",
  "pieces": [
   [
    "sgila945",
    "Banner Marsh State Fish and Wildlife Area",
    4359,
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
 "t": "State Fish and Wildlife Area",
 "verdict": "agree"
}
```

## US-11716 Long Run Seep State Nature Preserve
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Long Run Seep State Nature Preserve",
 "official": {
  "acres": 79.8,
  "as": "79.75 acres",
  "clean": false,
  "line": "e plant communities of the seep. Ownership Illinois Department of Natural Resources Dedicated April 1990 Size 79.75 acres Topo Map: Joliet and Romeoville 7.5 Topographic Quad Joliet Topo Map Google Maps For Further Information Illi",
  "read": "2026-10-29",
  "sent": "79.75 acres Topo Map: Joliet and Romeoville 7.5",
  "url": "https://dnr.illinois.gov/inpc/area.area3willlongrunseep.html",
  "why": "total-looking"
 },
 "ours": {
  "acres": 81,
  "dissolved": {
   "after": 161,
   "before": 241,
   "copies": 1,
   "families": {
    "padus": 80,
    "sgilb": 81
   },
   "family_fold": 80,
   "family_used": "sgilb",
   "parts": 0,
   "records": 5,
   "tracts": 4
  },
  "family_fold": "layers {'padus': 80, 'sgilb': 81}: one land in 2 layers, the sgilb copy used (80 ac of copies not added)",
  "manager": "",
  "note": "5 joined records = 4 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 241 -> 161 acres",
  "pieces": [
   [
    "sgilb36",
    "Long Run Seep Nature Preserve",
    41,
    "name"
   ],
   [
    "sgilb34",
    "Long Run Seep Nature Preserve Addition",
    34,
    "words"
   ],
   [
    "sgilb35",
    "Long Run Seep Nature Preserve Buffer",
    6,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 2,
 "same_agency": false,
 "score": 7,
 "t": "State Nature Preserve",
 "verdict": "agree"
}
```

## US-10091 Powerton Lake State Fish and Wildlife Area
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Powerton Lake State Fish and Wildlife Area",
 "official": {
  "acres": 1426.0,
  "as": "1,426 acre",
  "clean": false,
  "line": "e Content Page Content The actual link for this page is - Powerton Lake Approximately 60% of Powerton Lake, a 1,426 acre cooling reservoir, is open to waterfowl hunting. The remaining is a waterfowl rest area. Active habitat manag",
  "read": "2026-10-29",
  "sent": "Approximately 60% of Powerton Lake, a 1,426 acre cooling reservoir, is open to waterfowl hunting.",
  "url": "https://dnr.illinois.gov/parks/park.powerton-lake.html",
  "why": "part (a lake, a purchase, a campground…)"
 },
 "ours": {
  "acres": 1618,
  "dissolved": {
   "after": 3163,
   "before": 3237,
   "copies": 1,
   "families": {
    "padus": 1545,
    "sgila": 1618
   },
   "family_fold": 1545,
   "family_used": "sgila",
   "parts": 0,
   "records": 4,
   "tracts": 3
  },
  "family_fold": "layers {'sgila': 1618, 'padus': 1545}: one land in 2 layers, the sgila copy used (1,545 ac of copies not added)",
  "manager": "",
  "note": "4 joined records = 3 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 3237 -> 3163 acres",
  "pieces": [
   [
    "sgila1010",
    "Powerton Lake State Fish and Wildlife Area",
    1618,
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
 "t": "State Fish and Wildlife Area",
 "verdict": "agree"
}
```

## US-1026 Spitler Woods State Park
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-10-29",
 "handover": [],
 "n": "Spitler Woods State Park",
 "official": {
  "acres": 146.0,
  "as": "146 acre",
  "clean": true,
  "line": "rk Boundary Paved Road Tr a i l Park Office Parking Restrooms Shelter Spitler Woods State Natural Area IIII A 146-acre forested tract, Spitler Woods State Natural Area is 8 miles southeast of Decatur and 1/2 mile east of Mount Z",
  "read": "2026-10-29",
  "sent": "A 146-acre forested tract, Spitler Woods State Natural Area is",
  "url": "https://dnr.illinois.gov/content/dam/soi/en/web/dnr/publications/documents/00000085.pdf",
  "why": "clean total"
 },
 "ours": {
  "acres": 40,
  "manager": "",
  "pieces": [
   [
    157620,
    "Spitler Woods",
    40,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 73,
 "same_agency": false,
 "score": 4,
 "t": "State Park",
 "verdict": "off"
}
```

## US-4115 Cedar Glen State Natural Area
```json
{
 "cause": "agency smaller: our outline may hold water, a lease or a neighbour tract",
 "checked": "2026-10-29",
 "handover": [],
 "n": "Cedar Glen State Natural Area",
 "official": {
  "acres": 573.9,
  "as": "573.87 acres",
  "clean": false,
  "line": "cularly significant as a roosting site for wintering bald eagles. Ownership IDNR Dedicated February 1975 Size 573.87 acres with an additional 43 acres of buffer Topographic Quad Warsaw Topo Map Google Maps For Further Information Th",
  "read": "2026-10-29",
  "sent": "573.87 acres with an additional 43 acres of buffer",
  "url": "https://dnr.illinois.gov/inpc/area.area4hancockcedarglen.html",
  "why": "total-looking"
 },
 "ours": {
  "acres": 849,
  "dissolved": {
   "after": 1087,
   "before": 1933,
   "copies": 1,
   "families": {
    "padus": 849,
    "sgilb": 238
   },
   "family_fold": 238,
   "family_used": "padus",
   "parts": 0,
   "records": 5,
   "tracts": 4
  },
  "family_fold": "layers {'padus': 849, 'sgilb': 238}: one land in 2 layers, the padus copy used (238 ac of copies not added)",
  "manager": "",
  "note": "5 joined records = 4 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1933 -> 1087 acres",
  "pieces": [
   [
    70798,
    "Cedar Glen State Natural Area",
    849,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 48,
 "same_agency": false,
 "score": 5,
 "t": "State Natural Area",
 "verdict": "off"
}
```
