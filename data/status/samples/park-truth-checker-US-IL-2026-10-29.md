# park truth checker: US-IL random sample of 12 (2026-10-29; seed = date + area, same rows for everyone)

Source file: `data/truth/US-IL.json`

## US-1013 Morrison-Rockwood State Park
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Morrison-Rockwood State Park",
 "official": {
  "acres": 1164.0,
  "as": "1,164 acres",
  "clean": true,
  "line": "aris Illinois Beach State Park Page Content Page Content History Morrison-Rockwood State Park is comprised of 1,164 acres, located north of Morrison in Whiteside County. It was established in 1971 and officially opened for day use",
  "read": "2026-10-29",
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
    "name"
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

## US-4124 Fults Hill Prairie State Nature Preserve
```json
{
 "cause": "agency smaller: our outline may hold water, a lease or a neighbour tract",
 "checked": "2026-10-29",
 "handover": [],
 "n": "Fults Hill Prairie State Nature Preserve",
 "official": {
  "acres": 532.0,
  "as": "532 acres",
  "clean": true,
  "line": "e found, some common and some found nowhere else in the state. Fults Hill Prairie Nature Preserve consists of 532 acres of uplands and includes woodland, prairie and glade communities. It has the largest complex of high-quality l",
  "read": "2026-10-29",
  "sent": "Fults Hill Prairie Nature Preserve consists of 532 acres of uplands and includes woodland, prairie and glade communities.",
  "url": "https://dnr.illinois.gov/parks/park.fultshillprairie.html",
  "why": "clean total; the agency's pages disagree: another of its pages says 800 acre (that one matches our outline)"
 },
 "ours": {
  "acres": 810,
  "dissolved": {
   "after": 1238,
   "before": 2048,
   "copies": 1,
   "families": {
    "padus": 810,
    "sgilb": 428
   },
   "family_fold": 428,
   "family_used": "padus",
   "parts": 0,
   "records": 4,
   "tracts": 3
  },
  "family_fold": "layers {'padus': 810, 'sgilb': 428}: one land in 2 layers, the padus copy used (428 ac of copies not added)",
  "manager": "",
  "note": "4 joined records = 3 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 2048 -> 1238 acres",
  "pieces": [
   [
    70806,
    "Fults Hill Prairie State Natural Area",
    810,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 52,
 "same_agency": false,
 "score": 6,
 "t": "State Nature Preserve",
 "verdict": "off"
}
```

## US-7372 Halfway Tavern State Historic Site
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Halfway Tavern State Historic Site",
 "official": null,
 "ours": {
  "acres": 4,
  "manager": "",
  "pieces": [
   [
    "sgila1533",
    "Halway Tavern State Historic Site",
    4,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 5,
 "t": "State Historic Site",
 "verdict": "no size on page"
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

## US-12368 Hooper Branch Savanna State Nature Preserve
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Hooper Branch Savanna State Nature Preserve",
 "official": {
  "acres": 562.0,
  "as": "562 acres",
  "clean": false,
  "line": "dpecker and plains pocket gopher. Ownership Illinois Department of Natural Resources Dedicated June 1986 Size 562 acres with buffer Topographic Quad Donovan Topo Map Google Maps For Further Information Illinois Nature Preserves C",
  "read": "2026-10-29",
  "sent": "562 acres with buffer",
  "url": "https://dnr.illinois.gov/inpc/area.area3iroquoishooperbranchsavanna.html",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 554,
  "manager": "",
  "pieces": [
   [
    "sgilb793",
    "Hooper Branch Savanna Nature",
    480,
    "name"
   ],
   [
    "sgilb794",
    "Hooper Branch Savanna Nature Addition",
    72,
    "words"
   ],
   [
    "sgilb967",
    "Hooper Branch Savanna Nature Preserve Buffer",
    2,
    "name"
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

## US-4137 Lowden-Miller State Forest
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Lowden-Miller State Forest",
 "official": {
  "acres": 2291.0,
  "as": "2,291 acres",
  "clean": true,
  "line": "and preserving its beauty for future generations. Named for the family, Lowden-Miller State Forest now totals 2,291 acres. It is located across the Rock River from another DNR property, Castle Rock Sate Park, which oversees its dai",
  "read": "2026-10-29",
  "sent": "Named for the family, Lowden-Miller State Forest now totals 2,291 acres.",
  "url": "https://dnr.illinois.gov/parks/about/park.lowdenmiller.html",
  "why": "clean total"
 },
 "ours": {
  "acres": 2347,
  "dissolved": {
   "after": 2347,
   "before": 4692,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 4692 -> 2347 acres",
  "pieces": [
   [
    70753,
    "Lowden-Miller State Forest",
    2347,
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

## US-0285 Meredosia National Wildlife Refuge
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Meredosia National Wildlife Refuge",
 "official": {
  "acres": 3645.0,
  "as": "3,645 acres",
  "clean": false,
  "line": "ibrary Species Map https://www.facebook.com/IllinoisRiverNWFR/ About Us Meredosia National Wildlife Refuge is 3,645 acres and is located in an area that was historically known for its ability to sustain fish and wildlife along the",
  "read": "2026-10-29",
  "sent": "Meredosia National Wildlife Refuge is 3,645 acres and is located in an area that was historically known for its ability to sustain fish and wildlife along the east side of the Illinois River in Morgan and Cass counties, near the town of Meredosia, Illinois.",
  "url": "https://www.fws.gov/refuge/meredosia/about-us",
  "why": "total-looking"
 },
 "ours": {
  "acres": 4141,
  "dissolved": {
   "after": 7839,
   "before": 11537,
   "copies": 1,
   "families": {
    "padus": 3698,
    "sgila": 4141
   },
   "family_fold": 3698,
   "family_used": "sgila",
   "parts": 0,
   "records": 3,
   "tracts": 2
  },
  "family_fold": "layers {'sgila': 4141, 'padus': 3698}: one land in 2 layers, the sgila copy used (3,698 ac of copies not added)",
  "manager": "",
  "note": "3 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 11537 -> 7839 acres",
  "pieces": [
   [
    "sgila1487",
    "Meredosia National Wildlife Refuge",
    4141,
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
 "t": "National Wildlife Refuge",
 "verdict": "agree"
}
```

## US-7259 Fort Kaskaskia State Historic Site
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Fort Kaskaskia State Historic Site",
 "official": null,
 "ours": {
  "acres": 248,
  "manager": "",
  "pieces": [
   [
    "sgila1464",
    "Fort Kaskaskia State Historic Site",
    248,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "State Historic Site",
 "verdict": "no size on page"
}
```

## US-4149 Piney Creek Ravine State Natural Area
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Piney Creek Ravine State Natural Area",
 "official": {
  "acres": 198.0,
  "as": "198 acre",
  "clean": true,
  "line": "ontent Site Brochure West of DuQuoin and south of Steeleville on the Randolph-Jackson County line is a unique 198-acre area known as Piney Creek Ravine State Natural Area. Purchased in 1972 for its rare plant species and other n",
  "read": "2026-10-29",
  "sent": "West of DuQuoin and south of Steeleville on the Randolph-Jackson County line is a unique 198-acre area known as Piney Creek Ravine State Natural Area.",
  "url": "https://dnr.illinois.gov/parks/park.pineycreek.html",
  "why": "clean total"
 },
 "ours": {
  "acres": 208,
  "family_fold": "layers {'sgila': 208, 'padus': 202, 'sgilb': 205}: one land in 3 layers, the sgila copy used (407 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgila1460",
    "Piney Creek Ravine State Natural Area",
    208,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 5,
 "same_agency": false,
 "score": 7,
 "t": "State Natural Area",
 "verdict": "agree"
}
```

## US-1023 Siloam Springs State Park
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-10-29",
 "handover": [
  {
   "date_hint": null,
   "kind": "transfer",
   "line": "ontent Page Content Originally part of the military tract of western Illinois (land set aside to be given to combat veterans), the area that is now Siloam Springs State Park was acquired in 1852 by George Meyers for his service in the Black Hawk and Mexican wars. He died in 1882 at the age of 102. L",
   "owner_now": "George Meyers",
   "src": "https://dnr.illinois.gov/parks/about/park.siloamsprings.html",
   "why": "about / history page of the park's site"
  }
 ],
 "n": "Siloam Springs State Park",
 "official": null,
 "ours": {
  "acres": 6033,
  "family_fold": "layers {'sgila': 6033, 'padus': 5854}: one land in 2 layers, the sgila copy used (5,854 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgila1569",
    "Siloam Springs State Park",
    6033,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": "George Meyers",
 "pct": null,
 "score": 6,
 "t": "State Park",
 "verdict": "unsure"
}
```

## US-1017 Ramsey Lake State Park
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Ramsey Lake State Park",
 "official": {
  "acres": 1980.0,
  "as": "1,980 acres",
  "clean": false,
  "line": "ed citizens, and civic groups actively helped secure land and upgrade and maintain the area, which now totals 1,980 acres. &lt;div id=\\\"ParksSecondaryPageNarrative\\\">&lt;div id=\\\"ctl00_PlaceHolderMain_ctl01__ControlWrapper_RichHtml",
  "read": "2026-10-29",
  "sent": "Throughout the years, county and township officials, concerned citizens, and civic groups actively helped secure land and upgrade and maintain the area, which now totals 1,980 acres.",
  "url": "https://dnr.illinois.gov/parks/about/park.ramseylake.html",
  "why": "total-looking"
 },
 "ours": {
  "acres": 1759,
  "dissolved": {
   "after": 1759,
   "before": 3518,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 3518 -> 1759 acres",
  "pieces": [
   [
    70844,
    "Ramsey Lake State Recreation Area",
    1759,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 11,
 "same_agency": false,
 "score": 8,
 "t": "State Park",
 "verdict": "agree"
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
