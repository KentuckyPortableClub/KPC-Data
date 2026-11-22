# park truth checker: US-NV random sample of 12 (2026-11-22; seed = date + area, same rows for everyone)

Source file: `data/truth/US-NV.json`

## US-4441 Lahontan State Recreation Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Lahontan State Recreation Area",
 "official": {
  "acres": 30000.0,
  "as": "30,000 acres",
  "clean": false,
  "line": "Carson River Basins to irrigate lands near the town of Fallon and to produce hydroelectric power. Today about 30,000 acres are irrigated from the reservoir; depending on the snow pack. Drainage water from the irrigated lands flows i",
  "read": "2026-11-22",
  "sent": "Today about 30,000 acres are irrigated from the reservoir;",
  "url": "http://parks.nv.gov/parks/lahontan",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 28890,
  "dissolved": {
   "after": 30866,
   "before": 88645,
   "copies": 2,
   "families": {
    "padus": 1976,
    "sgnvb": 28890
   },
   "family_fold": 1976,
   "family_used": "sgnvb",
   "parts": 0,
   "records": 4,
   "tracts": 2
  },
  "family_fold": "layers {'sgnvb': 28890, 'padus': 1976}: one land in 2 layers, the sgnvb copy used (1,976 ac of copies not added)",
  "manager": "",
  "note": "4 joined records = 2 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 88645 -> 30866 acres",
  "pieces": [
   [
    "sgnvb23",
    "Lake Lahontan Recreation Area",
    28890,
    "words"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 4,
 "same_agency": false,
 "score": 6,
 "t": "State Recreation Area",
 "verdict": "agree"
}
```

## US-13012 Antelope Valley Complex BLM Herd Management Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Antelope Valley Complex BLM Herd Management Area",
 "official": {
  "acres": 502909.0,
  "as": "502,909 acres",
  "clean": false,
  "line": "nsists of 496,356 acres of BLM land and 6,553 acres of a mix of private and other public lands for a total of 502,909 acres. Topography/Vegetation: This region is located in the Great Basin which is one of the largest deserts in the",
  "read": "2026-11-22",
  "sent": "Size: The area consists of 496,356 acres of BLM land and 6,553 acres of a mix of private and other public lands for a total of 502,909 acres.",
  "url": "https://www.blm.gov/programs/wild-horse-and-burro/herd-management/herd-management-areas/nevada/antelope-valley",
  "why": "total-looking"
 },
 "ours": {
  "acres": 509298,
  "dissolved": {
   "after": 509298,
   "before": 1014406,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1014406 -> 509298 acres",
  "pieces": [
   [
    "sgnvi421",
    "Antelope Valley",
    509298,
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
 "t": "BLM Herd Management Area",
 "verdict": "agree"
}
```

## US-13145 Warm Springs Canyon BLM Herd Management Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Warm Springs Canyon BLM Herd Management Area",
 "official": {
  "acres": 91105.0,
  "as": "91,105 acres",
  "clean": false,
  "line": "located in western Humboldt County, approximately 140 miles north of Reno, Nevada. Size: The area consists of 91,105 acres of BLM land and 605 acres of a mix of private and other public lands for a total of 91,710 acres. Topography/",
  "read": "2026-11-22",
  "sent": "Size: The area consists of 91,105 acres of BLM land and 605 acres of a mix of private and other public lands for a total of 91,710 acres.",
  "url": "https://www.blm.gov/programs/wild-horse-and-burro/herd-management/herd-management-areas/nevada/warm-springs",
  "why": "total-looking"
 },
 "ours": {
  "acres": 87735,
  "dissolved": {
   "after": 92695,
   "before": 185390,
   "copies": 1,
   "key_union": 87735,
   "parts": 0,
   "records": 2,
   "summed": 92695,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 185390 -> 92695 acres",
  "pieces": [
   [
    "hma152",
    "Warm Springs Canyon",
    92695,
    "name"
   ]
  ],
  "pin": "well outside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 4,
 "same_agency": false,
 "score": 6,
 "t": "BLM Herd Management Area",
 "verdict": "agree"
}
```

## US-13126 Diamond Complex BLM Herd Management Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Diamond Complex BLM Herd Management Area",
 "official": {
  "acres": 166632.0,
  "as": "166,632 acres",
  "clean": false,
  "line": "sists of 145,341 acres of BLM land and 21,291 acres of a mix of private and other public lands for a total of 166,632 acres. Topography/Vegetation: The terrain across most of the former Shoshone-Eureka planning area managed by the Ba",
  "read": "2026-11-22",
  "sent": "Size: The area consists of 145,341 acres of BLM land and 21,291 acres of a mix of private and other public lands for a total of 166,632 acres.",
  "url": "https://www.blm.gov/programs/wild-horse-and-burro/herd-management/herd-management-areas/nevada/diamond-hma",
  "why": "total-looking"
 },
 "ours": {
  "acres": 166305,
  "dissolved": {
   "after": 166305,
   "before": 332610,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 332610 -> 166305 acres",
  "pieces": [
   [
    "hma28",
    "Diamond",
    166305,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 0,
 "same_agency": false,
 "score": 8,
 "t": "BLM Herd Management Area",
 "verdict": "agree"
}
```

## US-0021 Death Valley National Park
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Death Valley National Park",
 "note": "whole park compared (POTA lists it in 2 states: {'US-NV': 110558, 'US-CA': 3270447})",
 "official": {
  "acres": 3000000.0,
  "as": "3 million acres",
  "clean": false,
  "line": "venture. Heat Safety If visiting Death Valley in the summer, follow these tips to stay safe. The park is over 3 million acres with limited cell service; prepare Fish in Death Valley? These charismatic little fish of Death Valley are fu",
  "read": "2026-11-22",
  "sent": "The park is over 3 million acres with limited cell service;",
  "url": "https://www.nps.gov/deva/index.htm",
  "why": "total-looking"
 },
 "ours": {
  "acres": 3381005,
  "acres_by_state": {
   "US-CA": 3270447,
   "US-NV": 110558
  },
  "dissolved": {
   "after": 110558,
   "before": 110599,
   "copies": 1,
   "parts": 0,
   "records": 3,
   "tracts": 2
  },
  "manager": "",
  "note": "3 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 110599 -> 110558 acres",
  "pieces": [
   [
    3434,
    "Death Valley National Park",
    110517,
    "name"
   ],
   [
    "sgnvb2",
    "Death Valley National Park",
    41,
    "same full name, far from the pin (G-1: the record names the "
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "states": [
   "US-NV",
   "US-CA"
  ],
  "unknown_pieces": 0,
  "whole_park": true
 },
 "owner_now": null,
 "pct": 13,
 "same_agency": false,
 "score": 7,
 "t": "National Park",
 "verdict": "agree"
}
```

## US-13224 South Fork Owyhee River - Nevada BLM Recreation Management Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "South Fork Owyhee River - Nevada BLM Recreation Management Area",
 "official": null,
 "ours": {
  "acres": 14511,
  "manager": "",
  "pieces": [
   [
    "rst9628",
    "South Fork Owyhee River",
    14511,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "BLM Recreation Management Area",
 "verdict": "no size on page"
}
```

## US-13064 Scripps Wildlife Management Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Scripps Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 2382,
  "dissolved": {
   "after": 2382,
   "before": 4724,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 4724 -> 2382 acres",
  "pieces": [
   [
    "sgnva10",
    "Scripps WMA",
    2382,
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
 "t": "Wildlife Management Area",
 "verdict": "no size on page"
}
```

## US-9274 North McCullough Wilderness Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "North McCullough Wilderness Area",
 "official": {
  "acres": 14763.0,
  "as": "14,763 acres",
  "clean": true,
  "line": "es Drive Las Vegas, NV 89103 http://www.blm.gov/nv/st/en/fo/lvfo.1.html Southern Nevada District Office Size: 14,763 acres Elevation Range: 3,000 - 5,000 feet Designation: Clark County Conservation of Public Land and Natural Resour",
  "read": "2026-11-22",
  "sent": "Size: 14,763 acres",
  "url": "https://www.blm.gov/sites/blm.gov/files/uploads/Programs_NationalConservationLands_WildernessAreas_NV_North%20McCullough%20Wilderness%20Fact%20Sheet%20Web%20Opt.pdf",
  "why": "clean total"
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
 "t": "Wilderness Area",
 "verdict": "ours unknown"
}
```

## US-12973 Fernley Wildlife Management Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Fernley Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 13019,
  "family_fold": "layers {'sgnva': 13019, 'padus': 5450}: one land in 2 layers, the sgnva copy used (5,450 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgnva8",
    "Fernley WMA",
    13019,
    "reviewed"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "Wildlife Management Area",
 "verdict": "no size on page"
}
```

## US-13055 Triple B BLM Herd Management Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Triple B BLM Herd Management Area",
 "official": {
  "acres": 1232494.0,
  "as": "1,232,494 acres",
  "clean": false,
  "line": "ists of 1,230,579 acres of BLM land and 1,915 acres of a mix of private and other public lands for a total of 1,232,494 acres. Topography/Vegetation: The Triple B HMA is typical of the Great Basin region, characterized by north-south t",
  "read": "2026-11-22",
  "sent": "Size: The area consists of 1,230,579 acres of BLM land and 1,915 acres of a mix of private and other public lands for a total of 1,232,494 acres.",
  "url": "https://www.blm.gov/programs/wild-horse-and-burro/herd-management/herd-management-areas/nevada/triple-b-hma",
  "why": "a statewide / agency-wide total (over a million acres) on a park that is not a big federal unit"
 },
 "ours": {
  "acres": 1235922,
  "dissolved": {
   "after": 1235922,
   "before": 2471844,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 2471844 -> 1235922 acres",
  "pieces": [
   [
    "hma87",
    "Triple B",
    1235922,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 0,
 "same_agency": false,
 "score": 8,
 "t": "BLM Herd Management Area",
 "verdict": "agree"
}
```

## US-13139 Muddy Mountains BLM Herd Management Area
```json
{
 "cause": "agency smaller: our outline may hold water, a lease or a neighbour tract",
 "checked": "2026-11-22",
 "handover": [],
 "n": "Muddy Mountains BLM Herd Management Area",
 "official": {
  "acres": 78705.0,
  "as": "78,705 acres",
  "clean": false,
  "line": "onsists of 77,196 acres of BLM land and 1,509 acres of a mix of private and other public lands for a total of 78,705 acres. Topography/Vegetation: This area is characterized as Mojave desert surrounded by low, rocky desert mountains",
  "read": "2026-11-22",
  "sent": "Size: The area consists of 77,196 acres of BLM land and 1,509 acres of a mix of private and other public lands for a total of 78,705 acres.",
  "url": "https://www.blm.gov/programs/wild-horse-and-burro/herd-management/herd-management-areas/nevada/muddy-mountains",
  "why": "total-looking"
 },
 "ours": {
  "acres": 236532,
  "dissolved": {
   "after": 316090,
   "before": 503888,
   "copies": 1,
   "families": {
    "hma": 187798,
    "sgakg": 128292
   },
   "family_fold": 128292,
   "family_used": "hma",
   "key_union": 236532,
   "parts": 0,
   "records": 3,
   "summed": 187798,
   "tracts": 2
  },
  "family_fold": "layers {'hma': 187798, 'sgakg': 128292}: one land in 2 layers, the hma copy used (128,292 ac of copies not added)",
  "manager": "",
  "note": "3 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 503888 -> 316090 acres",
  "pieces": [
   [
    "hma181",
    "Muddy Mountains",
    187798,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 201,
 "same_agency": false,
 "score": 6,
 "t": "BLM Herd Management Area",
 "verdict": "off"
}
```

## US-0676 Lake Mead National Recreation Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Lake Mead National Recreation Area",
 "note": "whole park compared (POTA lists it in 2 states: {'US-NV': 581651, 'US-AZ': 710205})",
 "official": {
  "acres": 1500000.0,
  "as": "1.5 million acres",
  "clean": false,
  "line": "tdoor thrills, striking landscapes, and brilliant blue waters. This year-round recreation area spreads across 1.5 million acres of mountains, canyons, valleys and two vast reservoirs. Visitors come here for scenic drives, biking, hiking,",
  "read": "2026-11-22",
  "sent": "This year-round recreation area spreads across 1.5 million acres of mountains, canyons, valleys and two vast reservoirs.",
  "url": "https://www.nps.gov/lake/index.htm",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 1291856,
  "acres_by_state": {
   "US-AZ": 710205,
   "US-NV": 581651
  },
  "dissolved": {
   "after": 1144918,
   "before": 1707957,
   "copies": 1,
   "families": {
    "padus": 581651,
    "sgnvb": 563267
   },
   "family_fold": 563267,
   "family_used": "padus",
   "parts": 0,
   "records": 3,
   "tracts": 2
  },
  "family_fold": "layers {'padus': 581651, 'sgnvb': 563267}: one land in 2 layers, the padus copy used (563,267 ac of copies not added)",
  "manager": "",
  "note": "3 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1707957 -> 1144918 acres",
  "pieces": [
   [
    3508,
    "Lake Mead National Recreation Area",
    581651,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "states": [
   "US-NV",
   "US-AZ"
  ],
  "unknown_pieces": 0,
  "whole_park": true
 },
 "owner_now": null,
 "pct": 14,
 "same_agency": false,
 "score": 7,
 "t": "National Recreation Area",
 "verdict": "agree"
}
```
