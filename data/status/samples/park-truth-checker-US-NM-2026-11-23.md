# park truth checker: US-NM random sample of 12 (2026-11-23; seed = date + area, same rows for everyone)

Source file: `data/truth/US-NM.json`

## US-0460 Maxwell National Wildlife Refuge
```json
{
 "checked": "2026-11-23",
 "handover": [],
 "n": "Maxwell National Wildlife Refuge",
 "official": {
  "acres": 2800.0,
  "as": "2,800 acres",
  "clean": false,
  "line": "d for the benefit of wildlife and has provided feeding and resting habitat for migratory birds. Approximately 2,800 acres of the lands that make up Maxwell National Wildlife Refuge are owned by the U.S. Fish and Wildlife Service an",
  "read": "2026-11-23",
  "sent": "Approximately 2,800 acres of the lands that make up Maxwell National Wildlife Refuge are owned by the U.S.",
  "url": "https://www.fws.gov/refuge/maxwell/",
  "why": "total-looking"
 },
 "ours": {
  "acres": 2747,
  "dissolved": {
   "after": 2747,
   "before": 5494,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 5494 -> 2747 acres",
  "pieces": [
   [
    4090,
    "Maxwell National Wildlife Refuge",
    2747,
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
 "t": "National Wildlife Refuge",
 "verdict": "agree"
}
```

## US-11817 Haystack Mountain OHV Area BLM Recreation Management Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "last_read_failed": "2026-11-23",
 "n": "Haystack Mountain OHV Area BLM Recreation Management Area",
 "official": {
  "acres": 1920.0,
  "as": "1,920 acres",
  "clean": false,
  "line": "hed on the rugged breaks overlooking the Pecos River, Haystack Mountain Off-Highway Vehicle (OHV) Area offers 1,920 acres of trails to ride. From novices to experts, on bare rock and sandy washes, OHV enthusiasts can find terrain t",
  "read": "2026-11-09",
  "sent": "Perched on the rugged breaks overlooking the Pecos River, Haystack Mountain Off-Highway Vehicle (OHV) Area offers 1,920 acres of trails to ride.",
  "url": "https://www.blm.gov/visit/haystack-mountain-ohv-area",
  "why": "total-looking"
 },
 "ours": {
  "acres": 1934,
  "dissolved": {
   "after": 1934,
   "before": 9670,
   "copies": 4,
   "parts": 0,
   "records": 5,
   "tracts": 1
  },
  "manager": "",
  "note": "5 joined records = 1 tracts: 4 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 9670 -> 1934 acres",
  "pieces": [
   [
    "rma11066",
    "Haystack Mountain OHV Area",
    1934,
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
 "t": "BLM Recreation Management Area",
 "verdict": "agree"
}
```

## US-4558 Continental Divide Trail National Scenic Trail
```json
{
 "checked": "2026-11-23",
 "handover": [],
 "n": "Continental Divide Trail National Scenic Trail",
 "note": "whole park compared (POTA lists it in 0 states: {})",
 "official": null,
 "ours": {
  "acres": 0,
  "acres_by_state": {},
  "manager": "",
  "pieces": [],
  "pin": "inside",
  "src": "",
  "states": [
   "US-MT",
   "US-ID",
   "US-WY",
   "US-NM",
   "US-CO"
  ],
  "unknown_pieces": 1,
  "whole_park": true
 },
 "owner_now": null,
 "pct": null,
 "score": 4,
 "t": "National Scenic Trail",
 "verdict": "ours unknown"
}
```

## US-2692 City of Rocks State Park
```json
{
 "checked": "2026-11-23",
 "handover": [],
 "n": "City of Rocks State Park",
 "official": null,
 "ours": {
  "acres": 2915,
  "family_fold": "layers {'sgnmb': 2915, 'padus': 681}: one land in 2 layers, the sgnmb copy used (681 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgnmb6",
    "CITY OF ROCKS",
    2915,
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

## US-0970 White Sands National Park
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-23",
 "handover": [],
 "n": "White Sands National Park",
 "official": {
  "acres": 176000.0,
  "as": "275 square miles",
  "clean": true,
  "line": "t White Sands. Visitors can experience sunset every day of the year. NPS Photo The dunes at White Sands cover 275 square miles of the Tularosa Basin. NPS Photo The wind shapes and moves the dunes as a whole but gives each individual dun",
  "read": "2026-11-23",
  "sent": "The dunes at White Sands cover 275 square miles of the Tularosa Basin.",
  "url": "https://www.nps.gov/whsa/index.htm",
  "why": "clean total"
 },
 "ours": {
  "acres": 148226,
  "manager": "",
  "pieces": [
   [
    3478,
    "White Sands National Park",
    148226,
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
 "score": 5,
 "t": "National Park",
 "verdict": "off"
}
```

## US-8618 White Ridge National Recreation Trail
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "last_read_failed": "2026-11-23",
 "n": "White Ridge National Recreation Trail",
 "official": null,
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
 "score": 4,
 "t": "National Recreation Trail",
 "verdict": "ours unknown"
}
```

## US-11816 Hackberry Lake OHV Use Area BLM Recreation Management Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "last_read_failed": "2026-11-23",
 "n": "Hackberry Lake OHV Use Area BLM Recreation Management Area",
 "official": {
  "acres": 55000.0,
  "as": "55,000 acres",
  "clean": false,
  "line": "e Area | New Mexico View Map In Full Screen The Hackberry Lake Off-Highway Vehicle (OHV) Use Area offers over 55,000 acres of rolling stabilized dune lands and cliffs. The area is open for intensive use of motorcycles, sand dune bug",
  "read": "2026-11-09",
  "sent": "The Hackberry Lake Off-Highway Vehicle (OHV) Use Area offers over 55,000 acres of rolling stabilized dune lands and cliffs.",
  "url": "https://www.blm.gov/visit/hackberry-lake-ohv-area",
  "why": "part (a lake, a purchase, a campground…)"
 },
 "ours": {
  "acres": 57606,
  "dissolved": {
   "after": 57606,
   "before": 230422,
   "copies": 3,
   "parts": 0,
   "records": 4,
   "tracts": 1
  },
  "manager": "",
  "note": "4 joined records = 1 tracts: 3 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 230422 -> 57606 acres",
  "pieces": [
   [
    "rma14053",
    "Hackberry Lake OHV Area",
    57606,
    "words"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 5,
 "same_agency": false,
 "score": 8,
 "t": "BLM Recreation Management Area",
 "verdict": "agree"
}
```

## US-8620 Ojito Wilderness Area
```json
{
 "cause": "agency smaller: our outline may hold water, a lease or a neighbour tract",
 "checked": "2026-11-09",
 "handover": [],
 "last_read_failed": "2026-11-23",
 "n": "Ojito Wilderness Area",
 "official": {
  "acres": 11000.0,
  "as": "11,000 acres",
  "clean": false,
  "line": "o Wilderness Area | New Mexico Plan Your Visit View Map In Full Screen Ojito Wilderness encompasses more than 11,000 acres of rugged high desert southwest of San Ysidro, New Mexico. Visitors will encounter steep mesas, box canyons,",
  "read": "2026-11-09",
  "sent": "Ojito Wilderness encompasses more than 11,000 acres of rugged high desert southwest of San Ysidro, New Mexico.",
  "url": "https://www.blm.gov/visit/ojito-wilderness-area",
  "why": "total-looking"
 },
 "ours": {
  "acres": 15811,
  "manager": "",
  "pieces": [
   [
    "sgakh1729",
    "Ojito",
    3887,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "",
  "unknown_pieces": 2
 },
 "owner_now": null,
 "pct": 44,
 "same_agency": false,
 "score": 6,
 "t": "Wilderness Area",
 "verdict": "off"
}
```

## US-2712 Rio Grande Nature Center State Park
```json
{
 "checked": "2026-11-23",
 "handover": [],
 "n": "Rio Grande Nature Center State Park",
 "official": null,
 "ours": {
  "acres": 51,
  "family_fold": "layers {'sgnmb': 39, 'padus': 25}: one land in 2 layers, the sgnmb copy used (25 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgnmb23",
    "RIO GRANDE NATURE CENTER",
    39,
    "reviewed"
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

## US-2696 Eagle Nest Lake State Park
```json
{
 "checked": "2026-11-23",
 "handover": [],
 "n": "Eagle Nest Lake State Park",
 "official": null,
 "ours": {
  "acres": 3488,
  "family_fold": "layers {'sgnmb': 3488, 'padus': 1918}: one land in 2 layers, the sgnmb copy used (1,918 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgnmb9",
    "EAGLE NEST LAKE",
    3488,
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

## US-11806 Johnson (Gordy's) Hill BLM Recreation Management Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "last_read_failed": "2026-11-23",
 "n": "Johnson (Gordy's) Hill BLM Recreation Management Area",
 "official": null,
 "ours": {
  "acres": 7738,
  "manager": "",
  "pieces": [
   [
    "rst14034",
    "Johnson (Gordy's) Hill North",
    4583,
    "name"
   ],
   [
    "rst13973",
    "Johnson (Gordy's) Hill South",
    3155,
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

## US-4579 Santa Fe National Historic Trail
```json
{
 "checked": "2026-11-23",
 "handover": [],
 "n": "Santa Fe National Historic Trail",
 "note": "whole park compared (POTA lists it in 0 states: {})",
 "official": null,
 "ours": {
  "acres": 0,
  "acres_by_state": {},
  "manager": "",
  "pieces": [],
  "pin": "inside",
  "src": "",
  "states": [
   "US-KS",
   "US-OK",
   "US-MO",
   "US-NM",
   "US-CO"
  ],
  "unknown_pieces": 1,
  "whole_park": true
 },
 "owner_now": null,
 "pct": null,
 "score": 4,
 "t": "National Historic Trail",
 "verdict": "ours unknown"
}
```
