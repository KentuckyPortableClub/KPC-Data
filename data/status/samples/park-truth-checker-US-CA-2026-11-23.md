# park truth checker: US-CA random sample of 12 (2026-11-23; seed = date + area, same rows for everyone)

Source file: `data/truth/US-CA.json`

## US-1190 Richardson Grove State Park
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-11-23",
 "handover": [],
 "n": "Richardson Grove State Park",
 "official": null,
 "ours": {
  "acres": 1805,
  "dissolved": {
   "after": 1805,
   "before": 3610,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 3610 -> 1805 acres",
  "pieces": [
   [
    184064,
    "Richardson Grove State Park",
    1805,
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
 "t": "State Park",
 "verdict": "unsure"
}
```

## US-3466 Malakoff Diggins State Historical Park
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-11-23",
 "handover": [],
 "n": "Malakoff Diggins State Historical Park",
 "official": null,
 "ours": {
  "acres": 3218,
  "dissolved": {
   "after": 3218,
   "before": 6383,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 6383 -> 3218 acres",
  "pieces": [
   [
    "sgcab561",
    "Malakoff Diggins SHP",
    3218,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "State Historical Park",
 "verdict": "unsure"
}
```

## US-3547 Reynolds Wayside Campground Park
```json
{
 "cause": "agency smaller: our outline may hold water, a lease or a neighbour tract",
 "checked": "2026-11-23",
 "handover": [],
 "n": "Reynolds Wayside Campground Park",
 "official": {
  "acres": 38.0,
  "as": "38 acres",
  "clean": false,
  "line": "ng/lodging reservations at this time. About Reynolds Wayside Campground This park unit preserves and protects 38 acres of old-growth coast redwoods and Douglas firs in Mendocino County. View the park accessibility information Pa",
  "read": "2026-11-23",
  "sent": "This park unit preserves and protects 38 acres of old-growth coast redwoods and Douglas firs in Mendocino County.",
  "url": "https://www.parks.ca.gov/?page_id=428",
  "why": "total-looking"
 },
 "ours": {
  "acres": 68,
  "manager": "",
  "pieces": [
   [
    184154,
    "Reynolds Wayside Campgrounds",
    68,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 79,
 "same_agency": false,
 "score": 3,
 "t": "Park",
 "verdict": "off"
}
```

## US-11912 El Mirage BLM Special Recreation Management Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "last_read_failed": "2026-11-23",
 "n": "El Mirage BLM Special Recreation Management Area",
 "official": {
  "acres": 27275.0,
  "as": "27,275 acres",
  "clean": false,
  "line": "verview The El Mirage OHV Recreation Area is managed by the BLM’s Barstow Field Office (BAFO) and encompasses 27,275 acres with recreation opportunities for motorcycles, ATVs, trucks, cars, buggies, land yachts, model airplanes, mod",
  "read": "2026-11-09",
  "sent": "The El Mirage OHV Recreation Area is managed by the BLM’s Barstow Field Office (BAFO) and encompasses 27,275 acres with recreation opportunities for motorcycles, ATVs, trucks, cars, buggies, land yachts, model airplanes, model rockets, ultra-light aircraft, gyrocopters, and parasails.",
  "url": "https://www.blm.gov/visit/el-mirage-ohv-area",
  "why": "part (a lake, a purchase, a campground…)"
 },
 "ours": {
  "acres": 27276,
  "dissolved": {
   "after": 27276,
   "before": 81828,
   "copies": 2,
   "parts": 0,
   "records": 3,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 81828 -> 27276 acres",
  "pieces": [
   [
    "rma9469",
    "El Mirage",
    27276,
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
 "t": "BLM Special Recreation Management Area",
 "verdict": "agree"
}
```

## US-3408 Bethany Reservoir State Recreation Area
```json
{
 "checked": "2026-11-23",
 "handover": [],
 "n": "Bethany Reservoir State Recreation Area",
 "official": null,
 "ours": {
  "acres": 845,
  "dissolved": {
   "after": 845,
   "before": 1453,
   "copies": 1,
   "parts": 0,
   "records": 4,
   "tracts": 3
  },
  "manager": "",
  "note": "4 joined records = 3 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1453 -> 845 acres",
  "pieces": [
   [
    183296,
    "Bethany Reservoir State Recreation Area",
    611,
    "name"
   ],
   [
    183292,
    "Bethany Reservoir State Recreation Area",
    229,
    "name"
   ],
   [
    169015,
    "Bethany Park",
    5,
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
 "t": "State Recreation Area",
 "verdict": "no size on page"
}
```

## US-3444 Hungry Valley State Vehicle Recreational Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "last_read_failed": "2026-11-23",
 "n": "Hungry Valley State Vehicle Recreational Area",
 "official": null,
 "ours": {
  "acres": 19656,
  "dissolved": {
   "after": 19656,
   "before": 39297,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 39297 -> 19656 acres",
  "pieces": [
   [
    184136,
    "Hungry Valley State Vehicular Recreation Area",
    19656,
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
 "t": "State Vehicle Recreational Area",
 "verdict": "no size on page"
}
```

## US-11125 North Table Mountain Ecological Reserve
```json
{
 "checked": "2026-11-23",
 "handover": [],
 "n": "North Table Mountain Ecological Reserve",
 "official": {
  "acres": 3300.0,
  "as": "3,300 acre",
  "clean": false,
  "line": "cilities Accessibility Connectivity Maps and Guides Created by ancient lava (basalt) flows, the approximately 3,300 acre North Table Mountain Ecological Reserve is an elevated basalt mesa with beautiful vistas of spring wildflower",
  "read": "2026-11-23",
  "sent": "Created by ancient lava (basalt) flows, the approximately 3,300 acre North Table Mountain Ecological Reserve is an elevated basalt mesa with beautiful vistas of spring wildflowers, waterfalls, lava outcrops, and a rare type of vernal pool, called Northern Basalt Flow Vernal Pools.",
  "url": "https://wildlife.ca.gov/Lands/Places-to-Visit/North-Table-Mountain-ER",
  "why": "part (a lake, a purchase, a campground…)"
 },
 "ours": {
  "acres": 3293,
  "manager": "",
  "pieces": [
   [
    183541,
    "North Table Mountain Ecological Reserve",
    3240,
    "name"
   ],
   [
    "sgakh576",
    "North Table Mountain",
    53,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 4
 },
 "owner_now": null,
 "pct": 0,
 "same_agency": false,
 "score": 8,
 "t": "Ecological Reserve",
 "verdict": "agree"
}
```

## US-3562 Santa Cruz Mission State Historical Park
```json
{
 "checked": "2026-11-23",
 "handover": [],
 "n": "Santa Cruz Mission State Historical Park",
 "official": null,
 "ours": {
  "acres": 2,
  "dissolved": {
   "after": 2,
   "before": 4,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 4 -> 2 acres",
  "pieces": [
   [
    183892,
    "Santa Cruz Mission State Historic Park",
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
 "score": 7,
 "t": "State Historical Park",
 "verdict": "no size on page"
}
```

## US-3571 Standish-Hickey State Recreation Area
```json
{
 "checked": "2026-11-23",
 "handover": [],
 "n": "Standish-Hickey State Recreation Area",
 "official": {
  "acres": 1000.0,
  "as": "1,000 acres",
  "clean": false,
  "line": "1620, added 500 acres. Subsequent donations from Save the Redwoods League have expanded the park to more than 1,000 acres. A 180-mile drive from San Francisco, Standish-Hickey lies along Highway 101, 1&frac12; miles north of the to",
  "read": "2026-11-23",
  "sent": "Subsequent donations from Save the Redwoods League have expanded the park to more than 1,000 acres.",
  "url": "https://www.parks.ca.gov/?page_id=423",
  "why": "part (a lake, a purchase, a campground…)"
 },
 "ours": {
  "acres": 1011,
  "dissolved": {
   "after": 1011,
   "before": 2022,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 2022 -> 1011 acres",
  "pieces": [
   [
    184161,
    "Standish-Hickey State Recreation Area",
    1011,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 1,
 "same_agency": false,
 "score": 7,
 "t": "State Recreation Area",
 "verdict": "agree"
}
```

## US-0204 Pixley National Wildlife Refuge
```json
{
 "checked": "2026-11-23",
 "handover": [],
 "n": "Pixley National Wildlife Refuge",
 "official": {
  "acres": 6939.0,
  "as": "6,939 acres",
  "clean": false,
  "line": "on kangaroo rat and the endangered San Joaquin kit fox. Established in 1959, the refuge was later expanded to 6,939 acres and is currently managed as part of the Kern National Wildlife Refuge Complex. About Us Rules & Policies Pixl",
  "read": "2026-11-23",
  "sent": "Established in 1959, the refuge was later expanded to 6,939 acres and is currently managed as part of the Kern National Wildlife Refuge Complex.",
  "url": "https://www.fws.gov/refuge/pixley",
  "why": "history"
 },
 "ours": {
  "acres": 7494,
  "dissolved": {
   "after": 7494,
   "before": 14951,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 14951 -> 7494 acres",
  "pieces": [
   [
    5187,
    "Pixley National Wildlife Refuge",
    7494,
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
 "t": "National Wildlife Refuge",
 "verdict": "agree"
}
```

## US-1189 Red Rock Canyon State Park
```json
{
 "checked": "2026-11-23",
 "handover": [],
 "n": "Red Rock Canyon State Park",
 "official": null,
 "ours": {
  "acres": 25352,
  "dissolved": {
   "after": 25352,
   "before": 50702,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 50702 -> 25352 acres",
  "pieces": [
   [
    "sgcab612",
    "Red Rock Canyon SP",
    25352,
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
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-0819 Fort Point National Historic Site
```json
{
 "checked": "2026-11-23",
 "handover": [],
 "n": "Fort Point National Historic Site",
 "official": null,
 "ours": {
  "acres": 25,
  "manager": "",
  "pieces": [
   [
    3129,
    "Fort Point National Historic Site",
    25,
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
 "t": "National Historic Site",
 "verdict": "no size on page"
}
```
