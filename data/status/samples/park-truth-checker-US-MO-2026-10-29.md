# park truth checker: US-MO random sample of 12 (2026-10-29; seed = date + area, same rows for everyone)

Source file: `data/truth/US-MO.json`

## US-11134 P.F. Barnes State Conservation Area
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "P.F. Barnes State Conservation Area",
 "official": {
  "acres": 120.0,
  "as": "120 Acres",
  "clean": false,
  "line": "Barnes (P.F.) Conservation Area Conservation Commission of the State of Missouri © Last Updated - 1/27/2022 120 Acres - Texas County Legend Parking Lot MDC Land Non-MDC Road El evation Contour, 20' Forest MAP DISCLAIMER:",
  "read": "2026-10-29",
  "sent": "120 Acres - Texas County",
  "url": "https://mdc.mo.gov/sites/default/files/2023-02/6406map.pdf",
  "why": "a map label (no sentence)"
 },
 "ours": {
  "acres": 120,
  "dissolved": {
   "after": 120,
   "before": 238,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 238 -> 120 acres",
  "pieces": [
   [
    "sgmoc157",
    "Barnes (P F) CA",
    120,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 0,
 "same_agency": false,
 "score": 6,
 "t": "State Conservation Area",
 "verdict": "agree"
}
```

## US-11078 John Alva Fuson MD State Conservation Area
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "John Alva Fuson MD State Conservation Area",
 "official": {
  "acres": 1534.0,
  "as": "1534 ACRES",
  "clean": false,
  "line": "rk Road Parks Creek Rd. Parks Pleasant RidgeRoad Site Cr. JOHN ALVA FUSON, MD CONSERVATION AREA WRIGHT COUNTY 1534 ACRES LEGEND Boundary\u0003 Paved Road\u0003 Gravel Road\u0003 Dir t Road\u0003 Area Access Trail\u0003 Drainage\u0003 Parking Lot\u0003 Pond\u0003 Forest\u0003",
  "read": "2026-10-29",
  "sent": "1534 ACRES",
  "url": "https://mdc.mo.gov/sites/default/files/2024-06/8831map.pdf",
  "why": "a map label (no sentence)"
 },
 "ours": {
  "acres": 1517,
  "manager": "",
  "pieces": [
   [
    210335,
    "Fuson (John Alva, Md) Conservation Area",
    1517,
    "words"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 1,
 "same_agency": false,
 "score": 5,
 "t": "State Conservation Area",
 "verdict": "agree"
}
```

## US-4838 Busiek State Forest
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Busiek State Forest",
 "official": {
  "acres": 2700.0,
  "as": "2,700 Acres",
  "clean": false,
  "line": "k State Forest and Wildlife Area Conservation Commission of the State of Missouri © Last Updated - 11/2/2021 2,700 Acres - Christian County Legend Parking Lot Primitive Camping Rifle/Pistol Shooting Range M DC Land Non-MDC Road MD",
  "read": "2026-10-29",
  "sent": "2,700 Acres - Christian County",
  "url": "https://mdc.mo.gov/sites/default/files/2023-06/8109map.pdf",
  "why": "a map label (no sentence)"
 },
 "ours": {
  "acres": 2701,
  "family_fold": "layers {'sgmoc': 2701, 'padus': 2496}: one land in 2 layers, the sgmoc copy used (2,496 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgmoc446",
    "Busiek SF and WA",
    2701,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 0,
 "same_agency": false,
 "score": 8,
 "t": "State Forest",
 "verdict": "agree"
}
```

## US-3345 Confederate Memorial State Historic Site
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-10-29",
 "n": "Confederate Memorial State Historic Site",
 "official": null,
 "ours": {
  "acres": 141,
  "family_fold": "layers {'sgmoa': 141, 'padus': 134}: one land in 2 layers, the sgmoa copy used (134 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgmoa1458",
    "Confederate Memorial State Historic Site",
    141,
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
 "t": "State Historic Site",
 "verdict": "no size on page"
}
```

## US-5712 James A. Reed Memorial Wildlife Area
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "James A. Reed Memorial Wildlife Area",
 "official": {
  "acres": 3084.0,
  "as": "3,084 acres",
  "clean": false,
  "line": ". Additional tracts were purchased using federal monies and department funds to bring the area to its present 3,084 acres. Development of the area and construction of lakes began in 1957. Since then, over 252 acres of water have be",
  "read": "2026-10-29",
  "sent": "Additional tracts were purchased using federal monies and department funds to bring the area to its present 3,084 acres.",
  "url": "https://mdc.mo.gov/discover-nature/places/james-reed-memorial-wildlife-area",
  "why": "part (a lake, a purchase, a campground…)"
 },
 "ours": {
  "acres": 3094,
  "manager": "",
  "pieces": [
   [
    210551,
    "Reed (James A.) Memorial Wildlife Area",
    3094,
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
 "score": 5,
 "t": "Wildlife Area",
 "verdict": "agree"
}
```

## US-0870 Ulysses S. Grant National Historic Site
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Ulysses S. Grant National Historic Site",
 "official": null,
 "ours": {
  "acres": 10,
  "manager": "",
  "pieces": [
   [
    3178,
    "Ulysses S. Grant National Historic Site",
    10,
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

## US-10873 White River Trace State Conservation Area
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "White River Trace State Conservation Area",
 "official": {
  "acres": 2044.0,
  "as": "2,044 acre",
  "clean": false,
  "line": "tle Report Illegal Activity White River Trace Conservation Area Area Map 1.37 MB Area Brochure 449.92 KB This 2,044-acre area, which was purchased in 1988, takes its name from an old Indian trail running across the southeast porti",
  "read": "2026-10-29",
  "sent": "This 2,044-acre area, which was purchased in 1988, takes its name from an old Indian trail running across the southeast portion of the area.",
  "url": "https://mdc.mo.gov/discover-nature/places/white-river-trace-conservation-area",
  "why": "history"
 },
 "ours": {
  "acres": 2044,
  "dissolved": {
   "after": 2044,
   "before": 4088,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 4088 -> 2044 acres",
  "pieces": [
   [
    210664,
    "White River Trace Conservation Area",
    2044,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 0,
 "same_agency": false,
 "score": 8,
 "t": "State Conservation Area",
 "verdict": "agree"
}
```

## US-6495 Little Black State Conservation Area
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Little Black State Conservation Area",
 "official": {
  "acres": 2968.0,
  "as": "2,968 Acres",
  "clean": false,
  "line": "Area and Greenville Ford Access Conservation Commission of the State of Missouri © Last Updated - 12/13/2018 2,968 Acres - Ripley County Legend Disabled Accessible Parking Lot Archery Field Target Arch ery Static Target Picnic Are",
  "read": "2026-10-29",
  "sent": "2,968 Acres - Ripley County",
  "url": "https://mdc.mo.gov/sites/default/files/mo_nature/downloads/conservation-areas/7110map.pdf",
  "why": "a map label (no sentence)"
 },
 "ours": {
  "acres": 3093,
  "dissolved": {
   "after": 6051,
   "before": 6449,
   "copies": 1,
   "families": {
    "padus": 2806,
    "sgmoc": 3093,
    "sgmod": 152
   },
   "family_fold": 2958,
   "family_used": "sgmoc",
   "parts": 0,
   "records": 6,
   "tracts": 5
  },
  "family_fold": "layers {'sgmoc': 3093, 'padus': 2806, 'sgmod': 152}: one land in 3 layers, the sgmoc copy used (2,958 ac of copies not added)",
  "manager": "",
  "note": "6 joined records = 5 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 6449 -> 6051 acres",
  "pieces": [
   [
    "sgmoc265",
    "Little Black CA",
    3093,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 4,
 "same_agency": false,
 "score": 8,
 "t": "State Conservation Area",
 "verdict": "agree"
}
```

## US-1765 Jones-Confluence Point State Park
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Jones-Confluence Point State Park",
 "official": null,
 "ours": {
  "acres": 1117,
  "manager": "",
  "pieces": [
   [
    210104,
    "Edward \"ted\" And Pat Jones-confluence Point State Park",
    1117,
    "reviewed"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 5,
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-11052 Twin Borrow Pits State Conservation Area
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Twin Borrow Pits State Conservation Area",
 "official": {
  "acres": 20.0,
  "as": "20 acres",
  "clean": true,
  "line": "edia Title Report Illegal Activity Twin Borrow Pits Conservation Area Area Map 522.64 KB The area consists of 20 acres with two small fishable lakes. Quick Facts Total Acres 20.0 Area Hours Sunday, 04:00 AM - 10:00 PM Monday, Tu",
  "read": "2026-10-29",
  "sent": "The area consists of 20 acres with two small fishable lakes.",
  "url": "https://mdc.mo.gov/discover-nature/places/twin-borrow-pits-conservation-area",
  "why": "clean total"
 },
 "ours": {
  "acres": 20,
  "manager": "",
  "pieces": [
   [
    "sgmoc246",
    "Twin Borrow Pits CA",
    20,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 0,
 "same_agency": false,
 "score": 8,
 "t": "State Conservation Area",
 "verdict": "agree"
}
```

## US-1758 Finger Lakes State Park
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 10 acre, no total words near it)",
 "checked": "2026-10-29",
 "handover": [],
 "n": "Finger Lakes State Park",
 "official": {
  "acres": 10.0,
  "as": "10 acre",
  "clean": false,
  "line": "motocross track. Motocross Track The motocross track has motocross jumps and turns. The course loops around a 10-acre track. Parts of the course go through a wooded area and back in front of the grandstand area. The track is a",
  "read": "2026-10-29",
  "sent": "The course loops around a 10-acre track.",
  "url": "https://mostateparks.com/page/finger-lakes-state-park/road-riding-rules-finger-lakes",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 1059,
  "dissolved": {
   "after": 1059,
   "before": 2109,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 2109 -> 1059 acres",
  "pieces": [
   [
    210106,
    "Finger Lakes State Park",
    1059,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 10490,
 "same_agency": false,
 "score": 7,
 "t": "State Park",
 "verdict": "unsure"
}
```

## US-1789 Thousand Hills State Park
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Thousand Hills State Park",
 "official": null,
 "ours": {
  "acres": 3064,
  "dissolved": {
   "after": 3064,
   "before": 6067,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 6067 -> 3064 acres",
  "pieces": [
   [
    210135,
    "Thousand Hills State Park",
    3064,
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
 "verdict": "no size on page"
}
```
