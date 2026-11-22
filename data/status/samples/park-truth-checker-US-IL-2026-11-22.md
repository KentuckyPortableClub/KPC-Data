# park truth checker: US-IL random sample of 12 (2026-11-22; seed = date + area, same rows for everyone)

Source file: `data/truth/US-IL.json`

## US-4093 Clinton Lake State Recreation Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Clinton Lake State Recreation Area",
 "official": {
  "acres": 9300.0,
  "as": "9,300 acre",
  "clean": false,
  "line": ", visit Clinton Lake State Recreation Area in east central Illinois. Recreational opportunities abound at the 9,300-acre site. Clinton Lake is the cooling lake for the Exelon Power Station, and the IDNR manages recreation on the l",
  "read": "2026-11-22",
  "sent": "Recreational opportunities abound at the 9,300-acre site.",
  "url": "https://dnr.illinois.gov/parks/park.clintonlake.html",
  "why": "total-looking"
 },
 "ours": {
  "acres": 9593,
  "manager": "",
  "pieces": [
   [
    "sgila1077",
    "Clinton State Recreation Area",
    9501,
    "name"
   ],
   [
    "sgila1067",
    "Clinton State Recreation Area",
    49,
    "name"
   ],
   [
    77286,
    "Clinton State Recreation Area",
    43,
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
 "t": "State Recreation Area",
 "verdict": "agree"
}
```

## US-4097 Kickapoo State Recreation Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Kickapoo State Recreation Area",
 "official": {
  "acres": 4160.0,
  "as": "4,160 acre",
  "clean": false,
  "line": "by sandbars formed by waves at the mouth of the river, creating a sluggish, marshy habitat.&lt;/p>\\n&lt;p>The 4,160-acre park, consisting of two separate areas (North Unit and South Unit), offers ample opportunities for swimming,",
  "read": "2026-11-22",
  "sent": "idges are crowned by black oak forests with an open, savanna-like appearance.&nbsp;For much of the year, a stream known as Dead River is&nbsp;blocked by sandbars formed by waves at the mouth of the river, creating a sluggish, marshy habitat.&lt;/p>\\n&lt;p>The 4,160-acre park, consisting of two separ",
  "url": "https://dnr.illinois.gov/parks/park.kickapoo.html",
  "why": "part (a lake, a purchase, a campground…)"
 },
 "ours": {
  "acres": 4254,
  "dissolved": {
   "after": 4254,
   "before": 8385,
   "copies": 0,
   "parts": 2,
   "records": 4,
   "tracts": 2
  },
  "manager": "",
  "note": "4 joined records = 2 tracts: 0 copies of a tract (same acres, another layer) and 2 fee tracts under a designation record folded; summed 8385 -> 4254 acres",
  "pieces": [
   [
    "sgila1070",
    "Kickapoo State Recreation Area",
    4113,
    "reviewed"
   ],
   [
    "sgila2172",
    "Kickapoo State Recreation Area",
    141,
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
 "t": "State Recreation Area",
 "verdict": "agree"
}
```

## US-1024 Silver Springs State Park
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Silver Springs State Park",
 "official": {
  "acres": 1250.0,
  "as": "1,250 acre",
  "clean": true,
  "line": "ay Geo-Karis Illinois Beach State Park Page Content Page Content The State of Illinois purchased the original 1,250-acre area at what is now Silver Springs SFWA in 1969. It is located five miles west of Yorkville in Kendall County",
  "read": "2026-11-22",
  "sent": "The State of Illinois purchased the original 1,250-acre area at what is now Silver Springs SFWA in 1969.",
  "url": "https://dnr.illinois.gov/parks/about/park.silversprings.html",
  "why": "clean total"
 },
 "ours": {
  "acres": 1189,
  "manager": "",
  "pieces": [
   [
    158053,
    "Silver Springs",
    1189,
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
 "score": 7,
 "t": "State Park",
 "verdict": "agree"
}
```

## US-4120 Des Plaines State Fish and Wildlife Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Des Plaines State Fish and Wildlife Area",
 "official": {
  "acres": 5000.0,
  "as": "5,000 acres",
  "clean": false,
  "line": "nature lovers and sportsmen. More than 350,000 people annually visit Des Plaines SFWA - an area of more than 5,000 acres, including approximately 200 acres of water.​​​​​​​ Directions Located ten miles south of Joliet and 55 miles",
  "read": "2026-11-22",
  "sent": "More than 350,000 people annually visit Des Plaines SFWA - an area of more than 5,000 acres, including approximately 200 acres of water.​​​​​​​",
  "url": "https://dnr.illinois.gov/parks/park.desplaines.html",
  "why": "part (a lake, a purchase, a campground…)"
 },
 "ours": {
  "acres": 5356,
  "dissolved": {
   "after": 12597,
   "before": 17095,
   "copies": 1,
   "families": {
    "padus": 4531,
    "sgila": 174,
    "sgild": 7892
   },
   "family_fold": 4705,
   "family_used": "sgild",
   "key_union": 5356,
   "parts": 0,
   "records": 4,
   "summed": 7892,
   "tracts": 3
  },
  "family_fold": "layers {'sgild': 7892, 'padus': 4531, 'sgila': 174}: one land in 3 layers, the sgild copy used (4,705 ac of copies not added)",
  "manager": "",
  "note": "4 joined records = 3 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 17095 -> 12597 acres",
  "pieces": [
   [
    "sgild59",
    "Des Plaines",
    7892,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 2
 },
 "owner_now": null,
 "pct": 7,
 "same_agency": false,
 "score": 8,
 "t": "State Fish and Wildlife Area",
 "verdict": "agree"
}
```

## US-4111 Bohm Woods State Nature Preserve
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Bohm Woods State Nature Preserve",
 "official": {
  "acres": 92.0,
  "as": "92.0 Acres",
  "clean": false,
  "line": "land forest and river bluffs. Ownership Illinois Department of Natural Resources Dedicated November 2006 Size 92.0 Acres Topographic Quad Wood River Google Maps For Further Information Contact: Illinois Department of Natural Resou",
  "read": "2026-11-22",
  "sent": "92.0 Acres",
  "url": "https://dnr.illinois.gov/inpc/area.area7madisonbohmwoods.html",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 91,
  "manager": "",
  "pieces": [
   [
    "sgilb577",
    "Bohm Woods Nature Preserve",
    91,
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
 "t": "State Nature Preserve",
 "verdict": "agree"
}
```

## US-4156 Ten Mile Creek State Fish and Wildlife Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Ten Mile Creek State Fish and Wildlife Area",
 "official": {
  "acres": 5820.0,
  "as": "5,820 acres",
  "clean": false,
  "line": "isillinoisbeach\"> About Adeline Jay Geo-Karis Illinois Beach State Park Page Content Page Content History The 5,820 acres comprising Ten Mile Creek State Fish and Wildlife Area were purchased in 1988. Approximately one third of the",
  "read": "2026-11-22",
  "sent": "The 5,820 acres comprising Ten Mile Creek State Fish and Wildlife Area were purchased in 1988.",
  "url": "https://dnr.illinois.gov/parks/about/park.tenmilecreek.html",
  "why": "history"
 },
 "ours": {
  "acres": 6094,
  "dissolved": {
   "after": 15670,
   "before": 21610,
   "copies": 0,
   "families": {
    "sgila": 5938,
    "sgild": 9732
   },
   "family_fold": 5938,
   "family_used": "sgild",
   "key_union": 6094,
   "parts": 2,
   "records": 4,
   "summed": 9732,
   "tracts": 2
  },
  "family_fold": "layers {'sgild': 9732, 'sgila': 5938}: one land in 2 layers, the sgild copy used (5,938 ac of copies not added)",
  "manager": "",
  "note": "4 joined records = 2 tracts: 0 copies of a tract (same acres, another layer) and 2 fee tracts under a designation record folded; summed 21610 -> 15670 acres",
  "pieces": [
   [
    "sgild58",
    "Ten Mile Creek",
    9732,
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
 "t": "State Fish and Wildlife Area",
 "verdict": "agree"
}
```

## US-0985 Cave-In-Rock State Park
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Cave-In-Rock State Park",
 "official": {
  "acres": 204.0,
  "as": "204 acres",
  "clean": false,
  "line": "ps from the period. In 1929, the State of Illinois acquired 64.5 acres for a park that since has increased to 204 acres. The well-wooded, 60-foot-high hills and the rugged bluffs along the river - commanding expansive views of th",
  "read": "2026-11-22",
  "sent": "In 1929, the State of Illinois acquired 64.5 acres for a park that since has increased to 204 acres.",
  "url": "https://dnr.illinois.gov/parks/about/park.caveinrock.html",
  "why": "history"
 },
 "ours": {
  "acres": 178,
  "dissolved": {
   "after": 188,
   "before": 376,
   "copies": 1,
   "key_union": 178,
   "parts": 0,
   "records": 2,
   "summed": 188,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 376 -> 188 acres",
  "pieces": [
   [
    70894,
    "Cave-In-Rock State Park",
    188,
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
 "t": "State Park",
 "verdict": "agree"
}
```

## US-10093 Rock Island Trail State Park
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-11-22",
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
  "acres": 447,
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

## US-4113 Cape Bend State Fish and Wildlife Area
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-11-22",
 "handover": [],
 "n": "Cape Bend State Fish and Wildlife Area",
 "official": null,
 "ours": {
  "acres": 1413,
  "dissolved": {
   "after": 3278,
   "before": 4667,
   "copies": 1,
   "families": {
    "padus": 1390,
    "sgild": 1888
   },
   "family_fold": 1390,
   "family_used": "sgild",
   "key_union": 1413,
   "parts": 0,
   "records": 3,
   "summed": 1888,
   "tracts": 2
  },
  "family_fold": "layers {'sgild': 1888, 'padus': 1390}: one land in 2 layers, the sgild copy used (1,390 ac of copies not added)",
  "manager": "",
  "note": "3 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 4667 -> 3278 acres",
  "pieces": [
   [
    "sgild3",
    "Cape Bend",
    1888,
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
 "t": "State Fish and Wildlife Area",
 "verdict": "unsure"
}
```

## US-0284 Emiquon National Wildlife Refuge
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-22",
 "handover": [],
 "n": "Emiquon National Wildlife Refuge",
 "official": {
  "acres": 13000.0,
  "as": "13,000 acres",
  "clean": true,
  "line": ". The refuge is managed as part of the Illinois River National Wildlife and Fish Refuge Complex, which totals 13,000 acres across three refuges. About Us Law Enforcement Laws & Regulations Rules & Policies Emiquon National Wildlife",
  "read": "2026-11-22",
  "sent": "The refuge is managed as part of the Illinois River National Wildlife and Fish Refuge Complex, which totals 13,000 acres across three refuges.",
  "url": "https://www.fws.gov/refuge/emiquon",
  "why": "clean total; the agency's pages disagree: another of its pages says 2,631 acres (that one matches our outline)"
 },
 "ours": {
  "acres": 2631,
  "dissolved": {
   "after": 2631,
   "before": 7850,
   "copies": 2,
   "parts": 0,
   "records": 3,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 7850 -> 2631 acres",
  "pieces": [
   [
    3810,
    "Emiquon National Wildlife Refuge",
    2631,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 80,
 "same_agency": false,
 "score": 6,
 "t": "National Wildlife Refuge",
 "verdict": "off"
}
```

## US-7373 Lincoln Trail Memorial State Historic Site
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Lincoln Trail Memorial State Historic Site",
 "official": null,
 "ours": {
  "acres": 2,
  "manager": "",
  "pieces": [
   [
    157626,
    "Lincoln Trail State Memorial",
    2,
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
 "t": "State Historic Site",
 "verdict": "no size on page"
}
```

## US-0984 Castle Rock State Park
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Castle Rock State Park",
 "official": {
  "acres": 2000.0,
  "as": "2,000 acres",
  "clean": true,
  "line": "uisition by the State of Illinois started in 1970. At the present time, Castle Rock consists of approximately 2,000 acres, 710 of which are designated as an Illinois Nature Preserve. The site was dedicated as a state park in 1978.",
  "read": "2026-11-22",
  "sent": "At the present time, Castle Rock consists of approximately 2,000 acres, 710 of which are designated as an Illinois Nature Preserve.",
  "url": "https://dnr.illinois.gov/parks/about/park.castlerock.html",
  "why": "clean total"
 },
 "ours": {
  "acres": 2008,
  "dissolved": {
   "after": 2008,
   "before": 4015,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 4015 -> 2008 acres",
  "pieces": [
   [
    70893,
    "Castle Rock State Park",
    2008,
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
 "t": "State Park",
 "verdict": "agree"
}
```
