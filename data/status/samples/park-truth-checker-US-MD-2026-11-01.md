# park truth checker: US-MD random sample of 12 (2026-11-01; seed = date + area, same rows for everyone)

Source file: `data/truth/US-MD.json`

## US-7777 Dierssen Wildlife Management Area
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-11-01",
 "handover": [],
 "n": "Dierssen Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 67,
  "manager": "",
  "pieces": [],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 2
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "Wildlife Management Area",
 "verdict": "unsure"
}
```

## US-1580 Janes Island State Park
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Janes Island State Park",
 "official": {
  "acres": 2900.0,
  "as": "2,900 acres",
  "clean": false,
  "line": "areas, pavilions, and the boat ramp and marina. The island portion of the park – Janes Island – includes over 2,900 acres of saltmarsh, over 30 miles of water trails and miles of isolated pristine beaches. Although people have harv",
  "read": "2026-11-01",
  "sent": "The island portion of the park – Janes Island – includes over 2,900 acres of saltmarsh, over 30 miles of water trails and miles of isolated pristine beaches.",
  "url": "https://dnr.maryland.gov/publiclands/pages/eastern/janesisland.aspx",
  "why": "part (a lake, a purchase, a campground…)"
 },
 "ours": {
  "acres": 2483,
  "manager": "",
  "pieces": [
   [
    56662,
    "Janes Island Sp",
    404,
    "name"
   ],
   [
    56663,
    "Janes Island Sp",
    10,
    "name"
   ],
   [
    56661,
    "Janes Island Sp",
    2,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 3
 },
 "owner_now": null,
 "pct": 14,
 "same_agency": false,
 "score": 8,
 "t": "State Park",
 "verdict": "agree"
}
```

## US-7754 Bowen Wildlife Management Area
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-01",
 "handover": [],
 "n": "Bowen Wildlife Management Area",
 "official": {
  "acres": 313.0,
  "as": "313 acres",
  "clean": false,
  "line": "c enjoyment of the State’s wildlife resources through hunting and other wildlife-dependent recreation. Of the 313 acres, 90 percent of the area is tidal marsh which is a stopover point for migrating and wintering waterfowl. Black",
  "read": "2026-11-01",
  "sent": "Of the 313 acres, 90 percent of the area is tidal marsh which is a stopover point for migrating and wintering waterfowl.",
  "url": "https://dnr.maryland.gov/wildlife/Pages/publiclands/southern/bowen.aspx",
  "why": "total-looking"
 },
 "ours": {
  "acres": 255,
  "manager": "",
  "pieces": [
   [
    56474,
    "Bowen Wma",
    321,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 19,
 "same_agency": false,
 "score": 5,
 "t": "Wildlife Management Area",
 "verdict": "off"
}
```

## US-0670 George Washington Memorial Parkway
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "George Washington Memorial Parkway",
 "note": "whole park compared (POTA lists it in 3 states: {'US-DC': 135, 'US-VA': 7103, 'US-MD': 2052})",
 "official": null,
 "ours": {
  "acres": 9290,
  "acres_by_state": {
   "US-DC": 135,
   "US-MD": 2052,
   "US-VA": 7103
  },
  "manager": "",
  "pieces": [
   [
    3548,
    "George Washington Memorial Parkway",
    2364,
    "name"
   ],
   [
    271110,
    "George Washington Memorial Parkway",
    15,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "states": [
   "US-DC",
   "US-VA",
   "US-MD"
  ],
  "unknown_pieces": 0,
  "whole_park": true
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "Memorial Parkway",
 "verdict": "no size on page"
}
```

## US-4771 St. Inigoes State Forest
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "St. Inigoes State Forest",
 "official": {
  "acres": 938.0,
  "as": "938 acres",
  "clean": false,
  "line": "d DNR Forest Service Box 1509 Carter Building Leonardtown, MD 20650​ St. Inigoes State Forest is comprised of 938 acres located on a peninsula between St. Mary’s River and Smith Creek bordering the Potomac River. There are 324 ac",
  "read": "2026-11-01",
  "sent": "Inigoes State Forest is comprised of 938 acres located on a peninsula between St.",
  "url": "https://dnr.maryland.gov/forests/Pages/publiclands/southern_stinigoesforest.aspx",
  "why": "total-looking"
 },
 "ours": {
  "acres": 875,
  "manager": "",
  "pieces": [
   [
    56836,
    "St Inigoes Sf",
    932,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 7,
 "same_agency": false,
 "score": 8,
 "t": "State Forest",
 "verdict": "agree"
}
```

## US-10759 Green Run Woods Natural Area
```json
{
 "checked": "2026-11-01",
 "handover": [
  {
   "date_hint": null,
   "kind": "managed by",
   "line": "s within Green Run Woods Natural Area during the 2nd Maryland and DC Breeding Bird Atlas. This area is managed by the National Park Service as part of Assateague Island National Seashore It’s Dynamic, Baby! As a result of the sand moving through the former inlet, the",
   "owner_now": "National Park Service",
   "src": "https://dnr.maryland.gov/wildlife/Pages/NaturalAreas/Eastern/Green-Run-Woods.aspx",
   "why": "the park's page (data/parkinfo)"
  }
 ],
 "n": "Green Run Woods Natural Area",
 "official": null,
 "ours": {
  "acres": 0,
  "manager": "",
  "pieces": [],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 1
 },
 "owner_now": "National Park Service",
 "pct": null,
 "score": 6,
 "t": "Natural Area",
 "verdict": "ours unknown"
}
```

## US-7765 Billmeyer Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Billmeyer Wildlife Management Area",
 "official": {
  "acres": 758.0,
  "as": "758 acre",
  "clean": false,
  "line": "spread to adjacent lands. Nearby, the Bellgrove WMA was used exclusively for raising wild turkeys. Today this 758-acre tract in Allegany County is no longer a game bird farm. Forests and fields abound with wildlife, providing na",
  "read": "2026-11-01",
  "sent": "Today this 758-acre tract in Allegany County is no longer a game bird farm.",
  "url": "https://dnr.maryland.gov/wildlife/Pages/publiclands/western/billmeyer.aspx",
  "why": "total-looking"
 },
 "ours": {
  "acres": 812,
  "manager": "",
  "pieces": [
   [
    56471,
    "Billmeyer Wma",
    765,
    "name"
   ],
   [
    9202,
    "Billmeyer Wildlife Management Area",
    47,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 7,
 "same_agency": false,
 "score": 8,
 "t": "Wildlife Management Area",
 "verdict": "agree"
}
```

## US-7770 Indian Springs Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Indian Springs Wildlife Management Area",
 "official": {
  "acres": 6400.0,
  "as": "6,400 acre",
  "clean": true,
  "line": "e Wildlife & Heritage Service​ ​​​​​​​ Indian Springs WMA Main_Content ​ ​ ​​ ​ ​ ​ ​ Indian Springs WMA is a 6,400-acre tract in Washington County near the town of Clear Spring. Pictured above is Blair's Valley Lake, a popular fi",
  "read": "2026-11-01",
  "sent": "Indian Springs WMA is a 6,400-acre tract in Washington County near the town of Clear Spring.",
  "url": "https://dnr.maryland.gov/wildlife/Pages/publiclands/western/indiansprings.aspx",
  "why": "clean total"
 },
 "ours": {
  "acres": 6479,
  "manager": "",
  "pieces": [
   [
    56531,
    "Indian Springs Wma",
    6479,
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

## US-6392 Monocacy River Natural Resources Management Area State Natural Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Monocacy River Natural Resources Management Area State Natural Area",
 "official": {
  "acres": 1800.0,
  "as": "1,800 acres",
  "clean": true,
  "line": "Located in Frederick County, near Dickerson, Monocacy River Natural Resources Management Area is comprised of 1,800 acres of natural areas and farmlands along the Monocacy River. Recreational use is primarily hunting, fishing, hiki",
  "read": "2026-11-01",
  "sent": "Located in Frederick County, near Dickerson, Monocacy River Natural Resources Management Area is comprised of 1,800 acres of natural areas and farmlands along the Monocacy River.",
  "url": "https://dnr.maryland.gov/publiclands/Pages/western/monocacy.aspx",
  "why": "clean total"
 },
 "ours": {
  "acres": 1530,
  "manager": "",
  "pieces": [],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 2
 },
 "owner_now": null,
 "pct": 15,
 "same_agency": false,
 "score": 7,
 "t": "State Natural Area",
 "verdict": "agree"
}
```

## US-1583 Matthew Henson State Park
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Matthew Henson State Park",
 "official": null,
 "ours": {
  "acres": 158,
  "dissolved": {
   "after": 61,
   "before": 122,
   "copies": 0,
   "key_union": 158,
   "parts": 2,
   "records": 3,
   "summed": 61,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 0 copies of a tract (same acres, another layer) and 2 fee tracts under a designation record folded; summed 122 -> 61 acres",
  "pieces": [
   [
    83709,
    "Matthew Henson State Park Unit #4",
    61,
    "words"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 2
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-6395 Sassafras Natural Resources Management Area State Natural Area
```json
{
 "checked": "2026-11-01",
 "handover": [
  {
   "date_hint": null,
   "kind": "managed by",
   "line": "Area is located along the scenic banks of the Sassafras River and Turner's Creek in Kent County and operated by the Maryland Park Service. The area is noted for spectacular views of the Sassafras River and Chesapeake Bay from the high banks that face toward th",
   "owner_now": "Maryland Park Service",
   "src": "https://dnr.maryland.gov/publiclands/pages/eastern/sassafras.aspx",
   "why": "the park's page (data/parkinfo)"
  }
 ],
 "n": "Sassafras Natural Resources Management Area State Natural Area",
 "official": null,
 "ours": {
  "acres": 1197,
  "manager": "",
  "pieces": [
   [
    56711,
    "Sassafrass Nrma",
    971,
    "alias name (pin inside): SASSAFRASS NRMA"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 2
 },
 "owner_now": "Maryland Park Service",
 "pct": null,
 "score": 5,
 "t": "State Natural Area",
 "verdict": "no size on page"
}
```

## US-6397 Wolf Den Run State Park
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Wolf Den Run State Park",
 "official": {
  "acres": 2039.0,
  "as": "2039 acre",
  "clean": true,
  "line": "address: ​ c/o Herrington Manor State Park 222 Herrington Lane Oakland, MD 21550 Wolf Den Run State Park is a 2039 acre multi-use park that offers opportunities for hiking, biking, fishing, birdwatching, hunting, and ORV riding.",
  "read": "2026-11-01",
  "sent": "Wolf Den Run State Park is a 2039 acre multi-use park that offers opportunities for hiking, biking, fishing, birdwatching, hunting, and ORV riding.",
  "url": "https://dnr.maryland.gov/publiclands/pages/western/wolf-den-run.aspx",
  "why": "clean total"
 },
 "ours": {
  "acres": 1984,
  "manager": "",
  "pieces": [
   [
    56749,
    "Wolf Den Run Sp",
    1984,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 6
 },
 "owner_now": null,
 "pct": 3,
 "same_agency": false,
 "score": 8,
 "t": "State Park",
 "verdict": "agree"
}
```
