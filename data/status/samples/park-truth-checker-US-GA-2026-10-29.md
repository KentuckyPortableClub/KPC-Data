# park truth checker: US-GA random sample of 12 (2026-10-29; seed = date + area, same rows for everyone)

Source file: `data/truth/US-GA.json`

## US-4654 Spirit Creek Forest Wildlife Management Area
```json
{
 "cause": "our union: one of our pieces alone matches the agency (double count?)",
 "checked": "2026-10-29",
 "handover": [],
 "n": "Spirit Creek Forest Wildlife Management Area",
 "official": {
  "acres": 570.0,
  "as": "570 acre",
  "clean": false,
  "line": "Next Spirit Creek Forest WMA Spirit Creek Forest Wildlife Management Area is located in Richmond County. The 570-acre property offers hunting opportunities for deer, turkey and small game hunting. Gates may be closed or opened",
  "read": "2026-10-29",
  "sent": "The 570-acre property offers hunting opportunities for deer, turkey and small game hunting.",
  "url": "https://georgiawildlife.com/spirit-creek-forest-wma",
  "why": "total-looking"
 },
 "ours": {
  "acres": 1205,
  "dissolved": {
   "after": 1205,
   "before": 2337,
   "copies": 2,
   "parts": 0,
   "records": 4,
   "tracts": 2
  },
  "manager": "",
  "note": "4 joined records = 2 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 2337 -> 1205 acres",
  "pieces": [
   [
    195192,
    "Spirit Creek Forest",
    636,
    "name"
   ],
   [
    195189,
    "Spirit Creek Forest Wildlife Management Area",
    569,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 111,
 "same_agency": false,
 "score": 6,
 "t": "Wildlife Management Area",
 "verdict": "off"
}
```

## US-3731 B F Grant Wildlife Management Area
```json
{
 "cause": "agency smaller: our outline may hold water, a lease or a neighbour tract",
 "checked": "2026-10-29",
 "handover": [],
 "n": "B F Grant Wildlife Management Area",
 "official": {
  "acres": 45.0,
  "as": "45 acre",
  "clean": false,
  "line": "Boone & Crockett. This deer was also the largest killed in North America that year. The property is home to a 45-acre waterfowl M.A.R.S.H. (Matching Aid to Restore State’s Habitats) project that was constructed in 1991. The pro",
  "read": "2026-10-29",
  "sent": "The property is home to a 45-acre waterfowl M.A.R.S.H.",
  "url": "https://georgiawildlife.com/bf-grant-wma",
  "why": "total-looking"
 },
 "ours": {
  "acres": 14106,
  "dissolved": {
   "after": 27773,
   "before": 41868,
   "copies": 1,
   "families": {
    "padus": 13667,
    "sggac": 14106
   },
   "family_fold": 13667,
   "family_used": "sggac",
   "parts": 0,
   "records": 3,
   "tracts": 2
  },
  "family_fold": "layers {'sggac': 14106, 'padus': 13667}: one land in 2 layers, the sggac copy used (13,667 ac of copies not added)",
  "manager": "",
  "note": "3 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 41868 -> 27773 acres",
  "pieces": [
   [
    "sggac803",
    "B. F. GRANT WMA",
    14106,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 31247,
 "same_agency": false,
 "score": 6,
 "t": "Wildlife Management Area",
 "verdict": "off"
}
```

## US-7464 Evans County State Fishing Lake
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Evans County State Fishing Lake",
 "official": {
  "acres": 372.0,
  "as": "372 acre",
  "clean": false,
  "line": "able HOW TO HUNT AND FISH FOR A LIFETIME Previous Next Evans County PFA Evans County Public Fishing Area is a 372-acre area encompassing 3 separate lakes, each offering unique fishing and outdoor opportunities to visitors. Bidd",
  "read": "2026-10-29",
  "sent": "Evans County Public Fishing Area is a 372-acre area encompassing 3 separate lakes, each offering unique fishing and outdoor opportunities to visitors.",
  "url": "https://georgiawildlife.com/evans-county-pfa",
  "why": "total-looking"
 },
 "ours": {
  "acres": 376,
  "manager": "",
  "pieces": [
   [
    195176,
    "Evans County Public Fishing Area",
    376,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 1,
 "same_agency": false,
 "score": 7,
 "t": "State Fishing Lake",
 "verdict": "agree"
}
```

## US-2181 Georgia Veterans State Park
```json
{
 "checked": "2026-10-29",
 "handover": [
  {
   "date_hint": null,
   "kind": "managed by",
   "line": "rans State Park & Resort Georgia Veterans State Park & Resort Hi and thanks for visiting. This park is managed and operated by North Georgia Mountains Authority and Coral Hospitality. Visit official website . Locations Reservations Park Accessibility Events Activities Field Trips Gatherin",
   "owner_now": "North Georgia Mountains Authority and Coral Hospitality",
   "src": "https://gastateparks.org/GeorgiaVeterans",
   "why": "the park's page (data/parkinfo)"
  }
 ],
 "n": "Georgia Veterans State Park",
 "official": null,
 "ours": {
  "acres": 1472,
  "dissolved": {
   "after": 1472,
   "before": 2944,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 2944 -> 1472 acres",
  "pieces": [
   [
    195139,
    "Georgia Veterans State Park",
    1472,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": "North Georgia Mountains Authority and Coral Hospitality",
 "pct": null,
 "score": 6,
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-3778 Yuchi Wildlife Management Area
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-10-29",
 "handover": [],
 "n": "Yuchi Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 7703,
  "dissolved": {
   "after": 7703,
   "before": 22959,
   "copies": 2,
   "parts": 0,
   "records": 3,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 22959 -> 7703 acres",
  "pieces": [
   [
    195093,
    "Yuchi Wildlife Management Area",
    7703,
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
 "t": "Wildlife Management Area",
 "verdict": "unsure"
}
```

## US-3768 Phinizy Swamp Wildlife Management Area
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Phinizy Swamp Wildlife Management Area",
 "official": {
  "acres": 1500.0,
  "as": "1,500 acre",
  "clean": false,
  "line": "ME Previous Next Phinizy Swamp WMA Phinizy Swamp Wildlife Management Area is located in Richmond County. This 1,500-acre property offers hunting opportunities for deer, turkey, small game and waterfowl. There are also five ponds t",
  "read": "2026-10-29",
  "sent": "This 1,500-acre property offers hunting opportunities for deer, turkey, small game and waterfowl.",
  "url": "https://georgiawildlife.com/phinizy-swamp-wma",
  "why": "total-looking"
 },
 "ours": {
  "acres": 1609,
  "dissolved": {
   "after": 1609,
   "before": 4814,
   "copies": 2,
   "parts": 0,
   "records": 3,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 4814 -> 1609 acres",
  "pieces": [
   [
    "sggaa24",
    "PHINIZY SWAMP WMA",
    1609,
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
 "t": "Wildlife Management Area",
 "verdict": "agree"
}
```

## US-3758 John's Mountain Wildlife Management Area
```json
{
 "cause": "our union: one of our pieces alone matches the agency (double count?)",
 "checked": "2026-10-29",
 "handover": [],
 "n": "John's Mountain Wildlife Management Area",
 "official": {
  "acres": 23356.0,
  "as": "23,356 acre",
  "clean": false,
  "line": "is located in Walker, Whitfield, Gordon and Floyd counties on property owned by the U.S. Forest Service. This 23,356-acre property offers hunting opportunities for deer, bear, turkey and small game. No ATVs are allowed on the prope",
  "read": "2026-10-29",
  "sent": "This 23,356-acre property offers hunting opportunities for deer, bear, turkey and small game.",
  "url": "https://georgiawildlife.com/johns-mountain-wma",
  "why": "total-looking"
 },
 "ours": {
  "acres": 35608,
  "dissolved": {
   "after": 59319,
   "before": 82960,
   "copies": 1,
   "families": {
    "padus": 35608,
    "sggac": 23711
   },
   "family_fold": 23711,
   "family_used": "padus",
   "parts": 0,
   "records": 6,
   "tracts": 5
  },
  "family_fold": "layers {'sggac': 23711, 'padus': 35608}: one land in 2 layers, the padus copy used (23,711 ac of copies not added)",
  "manager": "",
  "note": "6 joined records = 5 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 82960 -> 59319 acres",
  "pieces": [
   [
    194392,
    "Johns Mountain Wildlife Management Area",
    20883,
    "name"
   ],
   [
    256199,
    "Johns Mountain Wildlife Management Area",
    11464,
    "name"
   ],
   [
    195049,
    "Johns Mountain Wildlife Management Area",
    2667,
    "name"
   ],
   [
    9158,
    "John's Mountain Wildlife Management Area",
    594,
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
 "t": "Wildlife Management Area",
 "verdict": "off"
}
```

## US-2165 A. H. Stephens State Park
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "A. H. Stephens State Park",
 "official": {
  "acres": 1177.0,
  "as": "1,177 Acres",
  "clean": false,
  "line": "is renovated to its 1875 style, fully furnished and open for tours. Reservations, Accommodations & Facilities 1,177 Acres 3 Lakes 4 Cottages 25 Tent, Trailer & RV Campsites 29 Equestrian Campsites 30 Horse Stables 2 Picnic Shelters",
  "read": "2026-10-29",
  "sent": "1,177 Acres",
  "url": "https://gastateparks.org/AHStephens",
  "why": "total-looking"
 },
 "ours": {
  "acres": 1170,
  "dissolved": {
   "after": 1170,
   "before": 2339,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 2339 -> 1170 acres",
  "pieces": [
   [
    195120,
    "A. H. Stephens State Park",
    1170,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
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

## US-9788 Lanahassee Creek Wildlife Management Area
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Lanahassee Creek Wildlife Management Area",
 "official": {
  "acres": 4420.0,
  "as": "4,420 acres",
  "clean": true,
  "line": "in the upper coastal plain physiographic region in west central Georgia near the town of Preston, and totals 4,420 acres. Accommodations & Facilities Primitive Campsites Activities Geocaching — not allowed before 10 a.m. during tu",
  "read": "2026-10-29",
  "sent": "Lanahassee Creek Wildlife Management Area is located in the upper coastal plain physiographic region in west central Georgia near the town of Preston, and totals 4,420 acres.",
  "url": "https://georgiawildlife.com/lanahassee-creek-wma",
  "why": "clean total"
 },
 "ours": {
  "acres": 4391,
  "dissolved": {
   "after": 4391,
   "before": 13167,
   "copies": 2,
   "parts": 0,
   "records": 3,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 13167 -> 4391 acres",
  "pieces": [
   [
    195052,
    "Lanahassee Creek Wildlife Management Area",
    4391,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 1,
 "same_agency": false,
 "score": 8,
 "t": "Wildlife Management Area",
 "verdict": "agree"
}
```

## US-7912 Montezuma Bluffs Wildlife Management Area
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Montezuma Bluffs Wildlife Management Area",
 "official": {
  "acres": 500.0,
  "as": "500 acre",
  "clean": false,
  "line": "Previous Next Montezuma Bluffs WMA Montezuma Bluffs Wildlife Management Area is located in Macon County. This 500-acre property offers a quality buck and antlerless archery-only deer season, turkey hunting and small game opportu",
  "read": "2026-10-29",
  "sent": "This 500-acre property offers a quality buck and antlerless archery-only deer season, turkey hunting and small game opportunities.",
  "url": "https://georgiawildlife.com/montezuma-bluffs-wma",
  "why": "total-looking"
 },
 "ours": {
  "acres": 511,
  "dissolved": {
   "after": 1010,
   "before": 1520,
   "copies": 1,
   "families": {
    "padus": 499,
    "sggaa": 511
   },
   "family_fold": 499,
   "family_used": "sggaa",
   "parts": 0,
   "records": 3,
   "tracts": 2
  },
  "family_fold": "layers {'sggaa': 511, 'padus': 499}: one land in 2 layers, the sggaa copy used (499 ac of copies not added)",
  "manager": "",
  "note": "3 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1520 -> 1010 acres",
  "pieces": [
   [
    "sggaa65",
    "MONTEZUMA BLUFFS WMA",
    511,
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
 "t": "Wildlife Management Area",
 "verdict": "agree"
}
```

## US-12419 Tallapoosa River Wildlife Management Area
```json
{
 "cause": "agency smaller: our outline may hold water, a lease or a neighbour tract",
 "checked": "2026-10-29",
 "handover": [],
 "n": "Tallapoosa River Wildlife Management Area",
 "official": {
  "acres": 3053.0,
  "as": "3,053 acre",
  "clean": true,
  "line": "ow Available HOW TO HUNT AND FISH FOR A LIFETIME Previous Next Tallapoosa River WMA Tallapoosa River WMA is a 3,053-acre property located between Cedartown and Buchanan. Hunting opportunities include deer, turkey (for youth only)",
  "read": "2026-10-29",
  "sent": "Tallapoosa River WMA is a 3,053-acre property located between Cedartown and Buchanan.",
  "url": "https://georgiawildlife.com/tallapoosa-river-wma",
  "why": "clean total"
 },
 "ours": {
  "acres": 5216,
  "family_fold": "layers {'sggac': 5216, 'sggaa': 4830}: one land in 2 layers, the sggac copy used (4,830 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sggac952",
    "TALLAPOOSA RIVER WMA",
    5216,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 71,
 "same_agency": false,
 "score": 6,
 "t": "Wildlife Management Area",
 "verdict": "off"
}
```

## US-3733 Beaverdam Wildlife Management Area
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 5,500 acres, no total words near it)",
 "checked": "2026-10-29",
 "handover": [],
 "n": "Beaverdam Wildlife Management Area",
 "official": {
  "acres": 5500.0,
  "as": "5,500 acres",
  "clean": false,
  "line": "f outdoor activities from hunting to camping. Hunting opportunities include deer, turkey and small game. With 5,500 acres of upland pine, mixed pine hardwoods and bottomland hardwood forests, this site is a great location for all!",
  "read": "2026-10-29",
  "sent": "With 5,500 acres of upland pine, mixed pine hardwoods and bottomland hardwood forests, this site is a great location for all!",
  "url": "https://georgiawildlife.com/beaverdam-wma",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 7956,
  "dissolved": {
   "after": 7956,
   "before": 19142,
   "copies": 2,
   "parts": 0,
   "records": 4,
   "tracts": 2
  },
  "manager": "",
  "note": "4 joined records = 2 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 19142 -> 7956 acres",
  "pieces": [
   [
    195014,
    "Beaverdam Wildlife Management Area",
    5633,
    "name"
   ],
   [
    193918,
    "Beaverdam Wildlife Management Area",
    2323,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 45,
 "same_agency": false,
 "score": 7,
 "t": "Wildlife Management Area",
 "verdict": "unsure"
}
```
