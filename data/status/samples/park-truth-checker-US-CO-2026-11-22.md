# park truth checker: US-CO random sample of 12 (2026-11-22; seed = date + area, same rows for everyone)

Source file: `data/truth/US-CO.json`

## US-0059 Rocky Mountain National Park
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Rocky Mountain National Park",
 "official": {
  "acres": 265600.0,
  "as": "415 square miles",
  "clean": false,
  "line": "ional Park • Colorado Located in northern Colorado, visitors to Rocky Mountain National Park can explore over 415 square miles (265,807 acres) within the Southern Rocky Mountains. From montane meadows to subalpine forests and mountain p",
  "read": "2026-11-22",
  "sent": "Located in northern Colorado, visitors to Rocky Mountain National Park can explore over 415 square miles (265,807 acres) within the Southern Rocky Mountains.",
  "url": "https://www.nps.gov/romo/index.htm",
  "why": "total-looking"
 },
 "ours": {
  "acres": 265475,
  "manager": "",
  "pieces": [
   [
    3471,
    "Rocky Mountain National Park",
    265475,
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
 "score": 7,
 "t": "National Park",
 "verdict": "agree"
}
```

## US-1243 State Forest State Park
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "State Forest State Park",
 "official": {
  "acres": 70932.0,
  "as": "70,932 acres",
  "clean": false,
  "line": "​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​In the ultimate rugged Colorado, State Forest State Park offers visitors 70,932 acres of forest, jagged peaks, alpine lakes, wildlife and miles of trails. With so much space and natural diversity",
  "read": "2026-11-22",
  "sent": "​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​In the ultimate rugged Colorado, State Forest State Park offers visitors 70,932 acres of forest, jagged peaks, alpine lakes, wildlife and miles of trails.",
  "url": "https://cpw.state.co.us/placestogo/parks/StateForest",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 71228,
  "dissolved": {
   "after": 71228,
   "before": 142422,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 142422 -> 71228 acres",
  "pieces": [
   [
    189450,
    "State Forest State Park",
    71228,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 2
 },
 "owner_now": null,
 "pct": 0,
 "same_agency": false,
 "score": 7,
 "t": "State Park",
 "verdict": "agree"
}
```

## US-12456 Stalker Lake State Wildlife Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Stalker Lake State Wildlife Area",
 "official": {
  "acres": 75.0,
  "as": "75 acres",
  "clean": false,
  "line": "d check current hunting, fishing and land use regulations when planning to visit a State Wildlife Area. Acres 75 acres. Elevation min. 3,548 ft - max 3,614 ft GMU 98 Hunting Opportunities Dove, Waterfowl Fishing Opportunities Wa",
  "read": "2026-11-22",
  "sent": "75 acres.",
  "url": "https://cpw.state.co.us/state-wildlife-areas/stalker-lake-swa",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 71,
  "dissolved": {
   "after": 59,
   "before": 117,
   "copies": 1,
   "key_union": 71,
   "parts": 0,
   "records": 2,
   "summed": 59,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 117 -> 59 acres",
  "pieces": [
   [
    "sgcoa287",
    "Stalker Lake SWA",
    59,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 2
 },
 "owner_now": null,
 "pct": 5,
 "same_agency": false,
 "score": 7,
 "t": "State Wildlife Area",
 "verdict": "agree"
}
```

## US-1218 Elkhead State Park
```json
{
 "cause": "agency smaller: our outline may hold water, a lease or a neighbour tract",
 "checked": "2026-11-22",
 "handover": [],
 "n": "Elkhead State Park",
 "official": {
  "acres": 900.0,
  "as": "900 acre",
  "clean": true,
  "line": "ing the Park's natural resources. Habitats and Plants Habitats and Plants at This Park Elkhead Reservoir is a 900-acre reservoir with riparian habitat above and around the lake. It is located in the sagebrush-shrub community and",
  "read": "2026-11-22",
  "sent": "Elkhead Reservoir is a 900-acre reservoir with riparian habitat above and around the lake.",
  "url": "https://cpw.state.co.us/placestogo/parks/ElkheadReservoir",
  "why": "clean total; the agency's pages disagree: another of its pages says 2,105 acres (that one matches our outline)"
 },
 "ours": {
  "acres": 2105,
  "dissolved": {
   "after": 2105,
   "before": 6322,
   "copies": 1,
   "parts": 2,
   "records": 4,
   "tracts": 1
  },
  "manager": "",
  "note": "4 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 2 fee tracts under a designation record folded; summed 6322 -> 2105 acres",
  "pieces": [
   [
    "sgcob10",
    "Elkhead Reservoir State Park",
    2105,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 134,
 "same_agency": false,
 "score": 6,
 "t": "State Park",
 "verdict": "off"
}
```

## US-11892 Jerry Creek Reservoirs State Wildlife Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Jerry Creek Reservoirs State Wildlife Area",
 "official": {
  "acres": 871.0,
  "as": "871 acres",
  "clean": false,
  "line": "d check current hunting, fishing and land use regulations when planning to visit a State Wildlife Area. Acres 871 acres. Elevation min. 5,221 ft - max 5,566 ft GMU 421 Hunting Opportunities No hunting opportunities available Fish",
  "read": "2026-11-22",
  "sent": "871 acres.",
  "url": "https://cpw.state.co.us/state-wildlife-areas/jerry-creek-reservoirs-swa",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 871,
  "dissolved": {
   "after": 871,
   "before": 1741,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1741 -> 871 acres",
  "pieces": [
   [
    "sgcoa164",
    "Jerry Creek Reservoir SWA",
    871,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 2
 },
 "owner_now": null,
 "pct": 0,
 "same_agency": false,
 "score": 7,
 "t": "State Wildlife Area",
 "verdict": "agree"
}
```

## US-11908 North Fruita Desert BLM Special Recreation Management Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "North Fruita Desert BLM Special Recreation Management Area",
 "official": null,
 "ours": {
  "acres": 11552,
  "dissolved": {
   "after": 11552,
   "before": 23104,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 23104 -> 11552 acres",
  "pieces": [
   [
    "rst10937",
    "North Fruita Desert",
    11552,
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
 "t": "BLM Special Recreation Management Area",
 "verdict": "no size on page"
}
```

## US-11898 Adobe Badlands BLM Wilderness Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Adobe Badlands BLM Wilderness Area",
 "official": {
  "acres": 38000000.0,
  "as": "38 million acres",
  "clean": false,
  "line": "research grounds, and outstanding ecological and cultural resources. These areas are diverse--made up of over 38 million acres of National Monuments, National Conservation Areas, Wilderness Areas, Wilderness Study Areas, Wild and Scenic",
  "read": "2026-11-22",
  "sent": "These areas are diverse--made up of over 38 million acres of National Monuments, National Conservation Areas, Wilderness Areas, Wilderness Study Areas, Wild and Scenic Rivers, National Scenic and Historic Trails, and Conservation Lands of the California Desert.",
  "url": "https://www.blm.gov/programs/national-conservation-lands/about",
  "why": "no total words near it"
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
 "score": 7,
 "t": "BLM Wilderness Area",
 "verdict": "ours unknown"
}
```

## US-7491 Comanche National Grassland
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-09",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Comanche National Grassland",
 "official": {
  "acres": 3000000.0,
  "as": "3 million acres",
  "clean": true,
  "line": "nal Grasslands The Pike-San Isabel National Forests & Cimarron and Comanche National Grasslands covers nearly 3 million acres from western Kansas to Colorado's highest mountain peaks along the Continental Divide. This landscape offers",
  "read": "2026-11-09",
  "sent": "The Pike-San Isabel National Forests & Cimarron and Comanche National Grasslands covers nearly 3 million acres from western Kansas to Colorado's highest mountain peaks along the Continental Divide.",
  "url": "https://www.fs.usda.gov/detail/psicc/about-forest/districts/?cid=fsm9_032695",
  "why": "clean total"
 },
 "ours": {
  "acres": 443611,
  "manager": "",
  "pieces": [
   [
    2722,
    "Comanche National Grassland",
    443611,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 85,
 "same_agency": false,
 "score": 5,
 "t": "National Grassland",
 "verdict": "off"
}
```

## US-9615 Big Thompson Ponds State Wildlife Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Big Thompson Ponds State Wildlife Area",
 "official": null,
 "ours": {
  "acres": 59,
  "family_fold": "layers {'padus': 56, 'sgcoa': 48}: one land in 2 layers, the padus copy used (48 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    189049,
    "Big Thompson Ponds State Wildlife Area",
    56,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 3
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "State Wildlife Area",
 "verdict": "no size on page"
}
```

## US-11915 Hubbard Mesa OHV BLM Special Recreation Management Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Hubbard Mesa OHV BLM Special Recreation Management Area",
 "official": {
  "acres": 2460.0,
  "as": "2,460 acres",
  "clean": false,
  "line": "hicle use. Hubbard Mesa was designated as an Open Area in 2007 in the Roan Plateau Management Plan. It offers 2,460 acres with 50 miles of single track, ATV and Jeep trails. This is a high use area primarily for OHV's but also rece",
  "read": "2026-11-22",
  "sent": "It offers 2,460 acres with 50 miles of single track, ATV and Jeep trails.",
  "url": "https://www.blm.gov/visit/roan-plateau-hubbard-mesa",
  "why": "total-looking"
 },
 "ours": {
  "acres": 2324,
  "dissolved": {
   "after": 2324,
   "before": 6972,
   "copies": 2,
   "parts": 0,
   "records": 3,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 6972 -> 2324 acres",
  "pieces": [
   [
    "rst10934",
    "Hubbard Mesa OHV Area",
    2324,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 6,
 "same_agency": false,
 "score": 8,
 "t": "BLM Special Recreation Management Area",
 "verdict": "agree"
}
```

## US-9641 Devil Creek State Wildlife Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Devil Creek State Wildlife Area",
 "official": null,
 "ours": {
  "acres": 552,
  "dissolved": {
   "after": 552,
   "before": 1103,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1103 -> 552 acres",
  "pieces": [
   [
    "sgcoa89",
    "Devil Creek SWA",
    552,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 2
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "State Wildlife Area",
 "verdict": "no size on page"
}
```

## US-9660 Joe Moore Reservoir State Wildlife Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Joe Moore Reservoir State Wildlife Area",
 "official": null,
 "ours": {
  "acres": 95,
  "family_fold": "layers {'sgcoa': 113, 'padus': 108}: one land in 2 layers, the sgcoa copy used (108 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgcoa166",
    "Joe Moore Reservoir SWA",
    113,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "State Wildlife Area",
 "verdict": "no size on page"
}
```
