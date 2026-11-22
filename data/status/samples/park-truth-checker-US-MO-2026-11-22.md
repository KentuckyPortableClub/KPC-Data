# park truth checker: US-MO random sample of 12 (2026-11-22; seed = date + area, same rows for everyone)

Source file: `data/truth/US-MO.json`

## US-1781 Robertsville State Park
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Robertsville State Park",
 "official": null,
 "ours": {
  "acres": 1236,
  "dissolved": {
   "after": 1236,
   "before": 2467,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 2467 -> 1236 acres",
  "pieces": [
   [
    210126,
    "Robertsville State Park",
    1236,
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

## US-10874 Gerhild and Graham Brown State Conservation Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Gerhild and Graham Brown State Conservation Area",
 "official": null,
 "ours": {
  "acres": 191,
  "dissolved": {
   "after": 191,
   "before": 569,
   "copies": 2,
   "parts": 0,
   "records": 3,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 569 -> 191 acres",
  "pieces": [
   [
    210220,
    "Brown (Gerhild And Graham) Conservation Area",
    191,
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
 "t": "State Conservation Area",
 "verdict": "no size on page"
}
```

## US-5711 Pony Express Lake State Conservation Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Pony Express Lake State Conservation Area",
 "official": null,
 "ours": {
  "acres": 3342,
  "dissolved": {
   "after": 3342,
   "before": 9922,
   "copies": 2,
   "parts": 0,
   "records": 3,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 9922 -> 3342 acres",
  "pieces": [
   [
    210534,
    "Pony Express Lake Conservation Area",
    3342,
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
 "t": "State Conservation Area",
 "verdict": "no size on page"
}
```

## US-0375 Clarence Cannon National Wildlife Refuge
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Clarence Cannon National Wildlife Refuge",
 "official": {
  "acres": 3750.0,
  "as": "3,750 acres",
  "clean": false,
  "line": "to provide a feeding and resting area for migratory birds. Named after Congressman Clarence Cannon, it covers 3,750 acres of Mississippi River floodplain comprised of moist soil units, open water, and bottomland forests. The refuge",
  "read": "2026-11-22",
  "sent": "Named after Congressman Clarence Cannon, it covers 3,750 acres of Mississippi River floodplain comprised of moist soil units, open water, and bottomland forests.",
  "url": "https://www.fws.gov/refuge/clarence_cannon/",
  "why": "part (a lake, a purchase, a campground…)"
 },
 "ours": {
  "acres": 3735,
  "dissolved": {
   "after": 3735,
   "before": 7470,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 7470 -> 3735 acres",
  "pieces": [
   [
    3724,
    "Clarence Cannon National Wildlife Refuge",
    3735,
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
 "score": 8,
 "t": "National Wildlife Refuge",
 "verdict": "agree"
}
```

## US-7676 Hardin Conservation Reserve
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Hardin Conservation Reserve",
 "official": null,
 "ours": {
  "acres": 242,
  "dissolved": {
   "after": 242,
   "before": 718,
   "copies": 2,
   "parts": 0,
   "records": 3,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 718 -> 242 acres",
  "pieces": [
   [
    210365,
    "Hardin Conservation Area",
    242,
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
 "t": "Conservation Reserve",
 "verdict": "no size on page"
}
```

## US-1753 Cuivre River State Park
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Cuivre River State Park",
 "official": null,
 "ours": {
  "acres": 6363,
  "family_fold": "layers {'sgmoa': 6363, 'padus': 4371}: one land in 2 layers, the sgmoa copy used (4,371 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgmoa1478",
    "Cuivre River State Park",
    6333,
    "reviewed"
   ],
   [
    "sgmoa1577",
    "Cuivre River State Park",
    30,
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

## US-12583 Merrill Horse Access State Conservation Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Merrill Horse Access State Conservation Area",
 "official": null,
 "ours": {
  "acres": 80,
  "dissolved": {
   "after": 154,
   "before": 302,
   "copies": 2,
   "families": {
    "padus": 80,
    "sgmoc": 74
   },
   "family_fold": 74,
   "family_used": "padus",
   "parts": 0,
   "records": 4,
   "tracts": 2
  },
  "family_fold": "layers {'padus': 80, 'sgmoc': 74}: one land in 2 layers, the padus copy used (74 ac of copies not added)",
  "manager": "",
  "note": "4 joined records = 2 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 302 -> 154 acres",
  "pieces": [
   [
    210974,
    "Merrill Horse Access",
    80,
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
 "t": "State Conservation Area",
 "verdict": "no size on page"
}
```

## US-3340 Battle of Pilot Knob State Historic Site
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Battle of Pilot Knob State Historic Site",
 "official": null,
 "ours": {
  "acres": 67,
  "dissolved": {
   "after": 71,
   "before": 119,
   "copies": 0,
   "families": {
    "padus": 48,
    "sgmoa": 23
   },
   "family_fold": 23,
   "family_used": "padus",
   "key_union": 67,
   "parts": 2,
   "records": 6,
   "summed": 48,
   "tracts": 4
  },
  "family_fold": "layers {'padus': 48, 'sgmoa': 23}: one land in 2 layers, the padus copy used (23 ac of copies not added)",
  "manager": "",
  "note": "6 joined records = 4 tracts: 0 copies of a tract (same acres, another layer) and 2 fee tracts under a designation record folded; summed 119 -> 71 acres",
  "pieces": [
   [
    210069,
    "Fort Davidson State Historic Site",
    48,
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
 "t": "State Historic Site",
 "verdict": "no size on page"
}
```

## US-7516 White Memorial State Conservation Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "White Memorial State Conservation Area",
 "official": null,
 "ours": {
  "acres": 821,
  "manager": "",
  "pieces": [
   [
    210661,
    "White (Wm. G. And E. P.) Memorial Wildlife Area",
    821,
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
 "t": "State Conservation Area",
 "verdict": "no size on page"
}
```

## US-8286 Hornersville State Conservation Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Hornersville State Conservation Area",
 "official": null,
 "ours": {
  "acres": 3194,
  "dissolved": {
   "after": 3194,
   "before": 3224,
   "copies": 3,
   "parts": 0,
   "records": 5,
   "tracts": 2
  },
  "manager": "",
  "note": "5 joined records = 2 tracts: 3 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 3224 -> 3194 acres",
  "pieces": [
   [
    210386,
    "Hornersville Swamp Conservation Area",
    3184,
    "name"
   ],
   [
    210385,
    "Hornersville Swamp Conservation Area",
    10,
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
 "t": "State Conservation Area",
 "verdict": "no size on page"
}
```

## US-5700 Grand Pass State Conservation Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Grand Pass State Conservation Area",
 "official": null,
 "ours": {
  "acres": 5344,
  "dissolved": {
   "after": 10645,
   "before": 15946,
   "copies": 1,
   "families": {
    "padus": 5344,
    "sgmoc": 5301
   },
   "family_fold": 5301,
   "family_used": "padus",
   "parts": 0,
   "records": 4,
   "tracts": 3
  },
  "family_fold": "layers {'sgmoc': 5301, 'padus': 5344}: one land in 2 layers, the padus copy used (5,301 ac of copies not added)",
  "manager": "",
  "note": "4 joined records = 3 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 15946 -> 10645 acres",
  "pieces": [
   [
    210348,
    "Grand Pass Conservation Area",
    5127,
    "name"
   ],
   [
    210349,
    "Grand Pass Conservation Area",
    217,
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
 "t": "State Conservation Area",
 "verdict": "no size on page"
}
```

## US-8256 Monkey Mountain State Conservation Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Monkey Mountain State Conservation Area",
 "official": null,
 "ours": {
  "acres": 1582,
  "dissolved": {
   "after": 2516,
   "before": 4098,
   "copies": 1,
   "families": {
    "padus": 934,
    "sgmoc": 1582
   },
   "family_fold": 934,
   "family_used": "sgmoc",
   "parts": 0,
   "records": 3,
   "tracts": 2
  },
  "family_fold": "layers {'sgmoc': 1582, 'padus': 934}: one land in 2 layers, the sgmoc copy used (934 ac of copies not added)",
  "manager": "",
  "note": "3 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 4098 -> 2516 acres",
  "pieces": [
   [
    "sgmoc345",
    "Monkey Mountain CA",
    1582,
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
 "t": "State Conservation Area",
 "verdict": "no size on page"
}
```
