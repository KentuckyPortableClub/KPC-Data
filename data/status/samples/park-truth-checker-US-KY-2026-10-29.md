# park truth checker: US-KY random sample of 12 (2026-10-29; seed = date + area, same rows for everyone)

Source file: `data/truth/US-KY.json`

## US-1252 Columbus Belmont State Park
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Columbus Belmont State Park",
 "official": null,
 "ours": {
  "acres": 159,
  "manager": "",
  "pieces": [
   [
    "bstate",
    "Columbus-Belmont State Park",
    159,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "Kentucky State Parks (DGI)",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-3840 Yellowbank Wildlife Management Area
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Yellowbank Wildlife Management Area",
 "official": {
  "acres": 7555.0,
  "as": "7555 acres",
  "clean": true,
  "line": "Public Land Search | KDFWR --> Yellowbank WMA Get Directions Close Return to Search --> WMA Overview Size: 7555 acres Location: Breckinridge Contact: Office (270) 547-6856 Elevation: minimum 382 feet, maximum 872 feet. Entrance",
  "read": "2026-10-29",
  "sent": "Size: 7555 acres",
  "url": "https://app.fw.ky.gov/public_lands_search/detail.aspx?Kdfwr_id=192",
  "why": "clean total"
 },
 "ours": {
  "acres": 7521,
  "manager": "KDFWR",
  "pieces": [
   [
    "bwma",
    "Yellowbank WMA",
    7521,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "KDFWR public hunting areas",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 0,
 "same_agency": true,
 "score": 7,
 "t": "WMA",
 "verdict": "agree"
}
```

## US-13598 Beaver Lake State Fishing Lake
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Beaver Lake State Fishing Lake",
 "official": {
  "acres": 146.0,
  "as": "146 acre",
  "clean": false,
  "line": "sheries | KDFWR Beaver Lake CLOSE Beaver Lake Fish Attractors in Google maps! Beaver Lake 5 ft Contours Note: 146 acre lake Possession or use of live shad for bait is prohibited. Special Fishing Regulations for Beaver Lake Speci",
  "read": "2026-10-29",
  "sent": "Note: 146 acre lake",
  "url": "https://app.fw.ky.gov/fisheries/waterbodydetail.aspx?wid=49",
  "why": "part (a lake, a purchase, a campground…)"
 },
 "ours": {
  "acres": 149,
  "manager": "Kentucky Fish & Wildlife",
  "pieces": [
   [
    "bpad",
    "Beaver Lake",
    149,
    "file"
   ]
  ],
  "pin": "outside",
  "src": "USGS PAD-US (fallback)",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 2,
 "same_agency": true,
 "score": 4,
 "t": "State Fishing Lake",
 "verdict": "agree"
}
```

## US-9756 Decker Wildlife Management Area
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Decker Wildlife Management Area",
 "official": {
  "acres": 300.0,
  "as": "300 acres",
  "clean": true,
  "line": "Public Land Search | KDFWR --> Decker WMA Get Directions Close Return to Search --> WMA Overview Size: 300 acres Location: Boone Contact: (859) 428-2262 Elevation: minimum 665 feet, maximum 908 feet. Entrance GPS coordinat",
  "read": "2026-10-29",
  "sent": "Size: 300 acres",
  "url": "https://app.fw.ky.gov/Public_Lands_Search/detail.aspx?Kdfwr_id=9717",
  "why": "clean total"
 },
 "ours": {
  "acres": 298,
  "manager": "KDFWR",
  "pieces": [
   [
    "bwma",
    "Decker WMA",
    298,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "KDFWR public hunting areas",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 1,
 "same_agency": true,
 "score": 7,
 "t": "WMA",
 "verdict": "agree"
}
```

## US-3795 Beechy Creek Wildlife Management Area
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Beechy Creek Wildlife Management Area",
 "official": {
  "acres": 119.0,
  "as": "119 acres",
  "clean": false,
  "line": "on Public Hunting Area Location Regional Locator WMA Overview Location & Size: Calloway County, 119 acres. Contact: (270) 753-6913 Elevation: minimum 365 feet, maximum 458 feet. Entrance GPS coordinates: Latit",
  "read": "2026-10-29",
  "sent": "Location & Size: Calloway County, 119 acres.",
  "url": "https://fw.ky.gov/More/Documents/BeechyCreekWMA-ALL.pdf",
  "why": "a map label (no sentence)"
 },
 "ours": {
  "acres": 118,
  "manager": "KDFWR",
  "pieces": [
   [
    "bwma",
    "Beechy Creek WMA",
    118,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "KDFWR public hunting areas",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 1,
 "same_agency": true,
 "score": 7,
 "t": "WMA",
 "verdict": "agree"
}
```

## US-7965 Brigadoon State Nature Preserve
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Brigadoon State Nature Preserve",
 "official": {
  "acres": 187.0,
  "as": "187 acres",
  "clean": false,
  "line": "es were dedicated on June 12, 2001 and a very small tract was dedicated on December 9, 2010. Today a total of 187 acres are protected. The rich woodlands contain an impressive array of spring wildflowers including several species",
  "read": "2026-10-29",
  "sent": "Today a total of 187 acres are protected.",
  "url": "https://eec.ky.gov/Nature-Preserves/Locations/Pages/Brigadoon.aspx",
  "why": "total-looking"
 },
 "ours": {
  "acres": 187,
  "manager": "",
  "pieces": [
   [
    "bsnp",
    "Brigadoon State Nature Preserve",
    187,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "Office of Kentucky Nature Preserves",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 0,
 "same_agency": true,
 "score": 7,
 "t": "Nature Preserve",
 "verdict": "agree"
}
```

## US-7959 Quiet Trails State Nature Preserve
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Quiet Trails State Nature Preserve",
 "official": {
  "acres": 177.0,
  "as": "177 acres",
  "clean": true,
  "line": "ve Main Content ​​​About Quiet Trails State​​ Nature Preserve​ Quiet Trails State Nature Preserve consists of 177 acres of ridges and ravines bordering the Licking River in Harrison County, generously donated to the Commonwealth",
  "read": "2026-10-29",
  "sent": "Quiet Trails State Nature Preserve consists of 177 acres of ridges and ravines bordering the Licking River in Harrison County, generously donated to the Commonwealth by Mr.",
  "url": "https://eec.ky.gov/Nature-Preserves/Locations/Pages/Quiet-Trails.aspx",
  "why": "clean total"
 },
 "ours": {
  "acres": 176,
  "manager": "",
  "pieces": [
   [
    "bsnp",
    "Quiet Trails State Nature Preserve",
    176,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "Office of Kentucky Nature Preserves",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 1,
 "same_agency": true,
 "score": 7,
 "t": "Nature Preserve",
 "verdict": "agree"
}
```

## US-0703 Fort Donelson National Battlefield
```json
{
 "cause": "boundary vs owned: our line may be the authorized boundary, the agency counts owned land (rule 1: use owned land)",
 "checked": "2026-10-29",
 "handover": [
  {
   "date_hint": "2006",
   "kind": "transfer",
   "line": "TN – On Monday, October 30, 2006, the Calloway County Executive Office will officially announce the transfer of properties associated with FortHeiman in Calloway County, Kentucky, to the National Park Service. A news conference hosted by the County Executive Office is scheduled for 1:00 p.m. Last up",
   "owner_now": "National Park Service",
   "src": "https://www.nps.gov/fodo/learn/news/newsreleases.htm",
   "why": "NPS news releases"
  }
 ],
 "n": "Fort Donelson National Battlefield",
 "official": {
  "acres": 1007.0,
  "as": "1007 acres",
  "clean": true,
  "line": "Site All NPS Exiting nps.gov Cancel Fort Donelson National Battlefield Contact Us Park Statistics Park Size: 1007 acres (as of 2010) Annual Visitation: Total Visits: 705,397 (Fiscal Year 2010) Recreational: 208,887 Annual Budget:",
  "read": "2026-10-29",
  "sent": "Park Size: 1007 acres (as of 2010)",
  "stale_year": 2010,
  "url": "https://www.nps.gov/fodo/learn/management/statistics.htm",
  "why": "clean total"
 },
 "ours": {
  "acres": 1295,
  "manager": "",
  "pieces": [
   [
    "bnps",
    "Fort Donelson National Battlefield",
    1295,
    "name"
   ]
  ],
  "pin": "outside",
  "src": "NPS units",
  "unknown_pieces": 0
 },
 "owner_now": "National Park Service",
 "pct": 29,
 "same_agency": true,
 "score": 3,
 "t": "National / NPS",
 "verdict": "off"
}
```

## US-1251 Carr Creek State Park
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Carr Creek State Park",
 "official": null,
 "ours": {
  "acres": 42,
  "manager": "KDFWR",
  "pieces": [
   [
    "bstate",
    "Carr Creek State Park",
    42,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "Corps of Engineers, KDFWR public hunting areas, Kentucky State Parks (DGI)",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-7955 Six Mile Island State Nature Preserve
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Six Mile Island State Nature Preserve",
 "official": {
  "acres": 85.6,
  "as": "85.58 acres",
  "clean": false,
  "line": "nd is 1.5 miles upstream from landing. Access Type: Open to Public County: Jefferson Region: Bluegrass Region Size: 85.58 Owner: Office of Kentucky Nature Preserves Manager: Nature Preseve Manager Office of Kentucky Nature Preserves",
  "read": "2026-10-29",
  "sent": "Size: 85.58 Owner:",
  "url": "https://eec.ky.gov/Nature-Preserves/Locations/Pages/Six-Mile-Island.aspx",
  "why": "total-looking"
 },
 "ours": {
  "acres": 85,
  "manager": "",
  "pieces": [
   [
    "bsnp",
    "Six Mile Island State Nature Preserve",
    85,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "Office of Kentucky Nature Preserves",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 1,
 "same_agency": true,
 "score": 7,
 "t": "Nature Preserve",
 "verdict": "agree"
}
```

## US-1280 Greenbo Lake State Park
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Greenbo Lake State Park",
 "official": null,
 "ours": {
  "acres": 6670,
  "manager": "State",
  "pieces": [
   [
    "bstate",
    "Greenbo Lake State Resort Park",
    3421,
    "name"
   ],
   [
    "bwma",
    "Greenbo Lake State Resort Park",
    3249,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "KDFWR public hunting areas, Kentucky State Parks (DGI)",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-1260 John James Audubon State Park
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "John James Audubon State Park",
 "official": null,
 "ours": {
  "acres": 1626,
  "manager": "",
  "pieces": [
   [
    "bstate",
    "John James Audubon State Park",
    1289,
    "name"
   ],
   [
    "bsnp",
    "John James Audubon State Park State Nature Preserve",
    337,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "Kentucky State Parks (DGI), Office of Kentucky Nature Preserves",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "State Park",
 "verdict": "no size on page"
}
```
