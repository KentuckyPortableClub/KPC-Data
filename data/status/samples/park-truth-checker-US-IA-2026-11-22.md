# park truth checker: US-IA random sample of 12 (2026-11-22; seed = date + area, same rows for everyone)

Source file: `data/truth/US-IA.json`

## US-5737 Volga River State Recreation Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Volga River State Recreation Area",
 "official": null,
 "ours": {
  "acres": 5920,
  "dissolved": {
   "after": 5920,
   "before": 23447,
   "copies": 4,
   "parts": 0,
   "records": 7,
   "tracts": 3
  },
  "manager": "",
  "note": "7 joined records = 3 tracts: 4 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 23447 -> 5920 acres",
  "pieces": [
   [
    "sgiaa34334",
    "VOLGA RIVER STATE RECREATION AREA",
    5867,
    "reviewed"
   ],
   [
    198595,
    "Volga River Access",
    45,
    "name"
   ],
   [
    198359,
    "Volga River Access",
    8,
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
 "t": "State Recreation Area",
 "verdict": "no size on page"
}
```

## US-2312 Pikes Point State Park
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Pikes Point State Park",
 "official": null,
 "ours": {
  "acres": 11,
  "dissolved": {
   "after": 20,
   "before": 38,
   "copies": 3,
   "families": {
    "padus": 12,
    "sgiab": 8
   },
   "family_fold": 8,
   "family_used": "padus",
   "key_union": 11,
   "parts": 0,
   "records": 6,
   "summed": 12,
   "tracts": 3
  },
  "family_fold": "layers {'sgiab': 8, 'padus': 12}: one land in 2 layers, the padus copy used (8 ac of copies not added)",
  "manager": "",
  "note": "6 joined records = 3 tracts: 3 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 38 -> 20 acres",
  "pieces": [
   [
    198565,
    "Pikes Pointt State Park",
    7,
    "name"
   ],
   [
    198564,
    "Pikes Point State Park",
    5,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 2
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-11324 Wapsi Wildlife Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Wapsi Wildlife Area",
 "official": null,
 "ours": {
  "acres": 99,
  "dissolved": {
   "after": 99,
   "before": 297,
   "copies": 1,
   "parts": 2,
   "records": 4,
   "tracts": 1
  },
  "manager": "",
  "note": "4 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 2 fee tracts under a designation record folded; summed 297 -> 99 acres",
  "pieces": [
   [
    199034,
    "Wapsi Wildlife Management Area",
    99,
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
 "t": "Wildlife Area",
 "verdict": "no size on page"
}
```

## US-10318 Chichaqua Wildlife Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Chichaqua Wildlife Area",
 "official": null,
 "ours": {
  "acres": 3808,
  "dissolved": {
   "after": 4774,
   "before": 10242,
   "copies": 1,
   "families": {
    "sgiaa": 2719,
    "sgiac": 2055
   },
   "family_fold": 2055,
   "family_used": "sgiaa",
   "key_union": 3808,
   "parts": 16,
   "records": 25,
   "summed": 2719,
   "tracts": 8
  },
  "family_fold": "layers {'sgiaa': 2719, 'sgiac': 2055}: one land in 2 layers, the sgiaa copy used (2,055 ac of copies not added)",
  "manager": "",
  "note": "25 joined records = 8 tracts: 1 copies of a tract (same acres, another layer) and 16 fee tracts under a designation record folded; summed 10242 -> 4774 acres",
  "pieces": [
   [
    "sgiaa34121",
    "CHICHAQUA WILDLIFE AREA - CCB",
    1817,
    "name"
   ],
   [
    "sgiaa33719",
    "CHICHAQUA WILDLIFE AREA",
    902,
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
 "t": "Wildlife Area",
 "verdict": "no size on page"
}
```

## US-9319 Goose Lake Wildlife Management Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Goose Lake Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 1290,
  "dissolved": {
   "after": 1290,
   "before": 3869,
   "copies": 2,
   "parts": 0,
   "records": 3,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 3869 -> 1290 acres",
  "pieces": [
   [
    "sgiaa33811",
    "GOOSE LAKE WILDLIFE AREA",
    1290,
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
 "t": "Wildlife Management Area",
 "verdict": "no size on page"
}
```

## US-12191 Turin Preserve Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Turin Preserve Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 1107,
  "dissolved": {
   "after": 1912,
   "before": 3235,
   "copies": 1,
   "families": {
    "padus": 805,
    "sgiaa": 1107
   },
   "family_fold": 805,
   "family_used": "sgiaa",
   "parts": 2,
   "records": 5,
   "tracts": 2
  },
  "family_fold": "layers {'sgiaa': 1107, 'padus': 805}: one land in 2 layers, the sgiaa copy used (805 ac of copies not added)",
  "manager": "",
  "note": "5 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 2 fee tracts under a designation record folded; summed 3235 -> 1912 acres",
  "pieces": [
   [
    "sgiaa38924",
    "TURIN PRESERVE WILDLIFE AREA",
    1107,
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
 "t": "Wildlife Management Area",
 "verdict": "no size on page"
}
```

## US-9342 Coon Creek Wildlife Management Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Coon Creek Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 1713,
  "dissolved": {
   "after": 1713,
   "before": 5139,
   "copies": 1,
   "parts": 2,
   "records": 4,
   "tracts": 1
  },
  "manager": "",
  "note": "4 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 2 fee tracts under a designation record folded; summed 5139 -> 1713 acres",
  "pieces": [
   [
    198717,
    "Coon Creek Wildlife Management Area",
    1713,
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
 "verdict": "no size on page"
}
```

## US-5735 Lower Gar State Recreation Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Lower Gar State Recreation Area",
 "official": null,
 "ours": {
  "acres": 304,
  "dissolved": {
   "after": 315,
   "before": 390,
   "copies": 3,
   "families": {
    "padus": 63,
    "sgiac": 252
   },
   "family_fold": 63,
   "family_used": "sgiac",
   "key_union": 304,
   "parts": 2,
   "records": 9,
   "summed": 252,
   "tracts": 4
  },
  "family_fold": "layers {'sgiac': 252, 'padus': 63}: one land in 2 layers, the sgiac copy used (63 ac of copies not added)",
  "manager": "",
  "note": "9 joined records = 4 tracts: 3 copies of a tract (same acres, another layer) and 2 fee tracts under a designation record folded; summed 390 -> 315 acres",
  "pieces": [
   [
    "sgiac106708",
    "Lower Gar Lake",
    252,
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
 "t": "State Recreation Area",
 "verdict": "no size on page"
}
```

## US-11323 Syracuse Wildlife Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Syracuse Wildlife Area",
 "official": null,
 "ours": {
  "acres": 724,
  "dissolved": {
   "after": 1433,
   "before": 2157,
   "copies": 1,
   "families": {
    "padus": 709,
    "sgiaa": 724
   },
   "family_fold": 709,
   "family_used": "sgiaa",
   "parts": 0,
   "records": 3,
   "tracts": 2
  },
  "family_fold": "layers {'sgiaa': 724, 'padus': 709}: one land in 2 layers, the sgiaa copy used (709 ac of copies not added)",
  "manager": "",
  "note": "3 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 2157 -> 1433 acres",
  "pieces": [
   [
    "sgiaa89857",
    "SYRACUSE WILDLIFE AREA",
    724,
    "reviewed"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 5,
 "t": "Wildlife Area",
 "verdict": "no size on page"
}
```

## US-5736 Templar State Recreation Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Templar State Recreation Area",
 "official": null,
 "ours": {
  "acres": 81,
  "dissolved": {
   "after": 111,
   "before": 135,
   "copies": 1,
   "families": {
    "padus": 87,
    "sgiab": 24
   },
   "family_fold": 24,
   "family_used": "padus",
   "key_union": 81,
   "parts": 0,
   "records": 4,
   "summed": 87,
   "tracts": 3
  },
  "family_fold": "layers {'padus': 87, 'sgiab': 24}: one land in 2 layers, the padus copy used (24 ac of copies not added)",
  "manager": "",
  "note": "4 joined records = 3 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 135 -> 111 acres",
  "pieces": [
   [
    157638,
    "Templar State Recreation Area",
    61,
    "name"
   ],
   [
    198606,
    "Templar State Recreation Area",
    26,
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
 "t": "State Recreation Area",
 "verdict": "no size on page"
}
```

## US-2293 Honey Creek State Park
```json
{
 "cause": "our union: one of our pieces alone matches the agency (double count?)",
 "checked": "2026-11-22",
 "handover": [],
 "n": "Honey Creek State Park",
 "official": {
  "acres": 828.0,
  "as": "828 acres",
  "clean": false,
  "line": "ark Alerts and Notices. Park Alerts & Notices About the Park Honey Creek State Park in southern Iowa features 828 acres of rolling, timbered hills with the beautiful backdrop of Iowa’s second largest lake, Rathbun Lake. Many wood",
  "read": "2026-11-22",
  "sent": "Honey Creek State Park in southern Iowa features 828 acres of rolling, timbered hills with the beautiful backdrop of Iowa’s second largest lake, Rathbun Lake.",
  "url": "https://www.iowadnr.gov/Places-to-Go/State-Parks/Iowa-State-Parks/Honey-Creek-State-Park",
  "why": "total-looking"
 },
 "ours": {
  "acres": 1549,
  "dissolved": {
   "after": 1578,
   "before": 4728,
   "copies": 8,
   "families": {
    "padus": 364,
    "sgiab": 1214
   },
   "family_fold": 364,
   "family_used": "sgiab",
   "key_union": 1549,
   "parts": 0,
   "records": 12,
   "summed": 1214,
   "tracts": 4
  },
  "family_fold": "layers {'sgiab': 1214, 'padus': 364}: one land in 2 layers, the sgiab copy used (364 ac of copies not added)",
  "manager": "",
  "note": "12 joined records = 4 tracts: 8 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 4728 -> 1578 acres",
  "pieces": [
   [
    "sgiab105661",
    "Honey Creek State Park",
    760,
    "reviewed"
   ],
   [
    "sgiab105658",
    "Honey Creek Resort",
    454,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 4
 },
 "owner_now": null,
 "pct": 87,
 "same_agency": false,
 "score": 6,
 "t": "State Park",
 "verdict": "off"
}
```

## US-9315 Three Mile Lake Wildlife Management Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Three Mile Lake Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 3095,
  "dissolved": {
   "after": 3130,
   "before": 8480,
   "copies": 2,
   "families": {
    "padus": 2677,
    "sgiaa": 453
   },
   "family_fold": 453,
   "family_used": "padus",
   "key_union": 3095,
   "parts": 0,
   "records": 4,
   "summed": 2677,
   "tracts": 2
  },
  "family_fold": "layers {'padus': 2677, 'sgiaa': 453}: one land in 2 layers, the padus copy used (453 ac of copies not added)",
  "manager": "",
  "note": "4 joined records = 2 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 8480 -> 3130 acres",
  "pieces": [
   [
    198985,
    "Three Mile Lake Wildlife Management Area",
    2677,
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
 "verdict": "no size on page"
}
```
