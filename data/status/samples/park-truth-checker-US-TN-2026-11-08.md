# park truth checker: US-TN random sample of 12 (2026-11-08; seed = date + area, same rows for everyone)

Source file: `data/truth/US-TN.json`

## US-3947 Jackson Swamp Wildlife Management Area
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-08",
 "n": "Jackson Swamp Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 114,
  "dissolved": {
   "after": 203,
   "before": 812,
   "copies": 3,
   "key_union": 114,
   "parts": 0,
   "records": 4,
   "summed": 203,
   "tracts": 1
  },
  "manager": "",
  "note": "4 joined records = 1 tracts: 3 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 812 -> 203 acres",
  "pieces": [
   [
    255714,
    "Jackson Swamp Wildlife Management Area",
    203,
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

## US-2952 Hiwassee Ocoee State Park
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-08",
 "n": "Hiwassee Ocoee State Park",
 "official": null,
 "ours": {
  "acres": 100,
  "dissolved": {
   "after": 208,
   "before": 299,
   "copies": 1,
   "families": {
    "padus": 117,
    "tnd": 91
   },
   "family_fold": 91,
   "family_used": "padus",
   "key_union": 100,
   "parts": 0,
   "records": 4,
   "summed": 117,
   "tracts": 3
  },
  "family_fold": "layers {'padus': 117, 'tnd': 91}: one land in 2 layers, the padus copy used (91 ac of copies not added)",
  "manager": "",
  "note": "4 joined records = 3 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 299 -> 208 acres",
  "pieces": [
   [
    256174,
    "Hiwassee/Ocoee",
    100,
    "name"
   ],
   [
    255384,
    "Hiwassee/Ocoee",
    17,
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
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-2940 Cummins Falls State Park
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-08",
 "n": "Cummins Falls State Park",
 "official": null,
 "ours": {
  "acres": 372,
  "family_fold": "layers {'sgtnf': 282, 'padus': 211}: one land in 2 layers, the sgtnf copy used (211 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgtnf45",
    "Cummins Falls State Park",
    282,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 3
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-13563 Bear Hollow Mountain Wildlife Management Area
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-08",
 "n": "Bear Hollow Mountain Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 16399,
  "dissolved": {
   "after": 35692,
   "before": 70122,
   "copies": 2,
   "families": {
    "padus": 14805,
    "sgtnc": 16399,
    "sgtne": 4488
   },
   "family_fold": 19293,
   "family_used": "sgtnc",
   "parts": 6,
   "records": 13,
   "tracts": 5
  },
  "family_fold": "layers {'sgtnc': 16399, 'padus': 14805, 'sgtne': 4488}: one land in 3 layers, the sgtnc copy used (19,293 ac of copies not added)",
  "manager": "",
  "note": "13 joined records = 5 tracts: 2 copies of a tract (same acres, another layer) and 6 fee tracts under a designation record folded; summed 70122 -> 35692 acres",
  "pieces": [
   [
    "sgtnc353",
    "Bear Hollow Mountain WMA",
    16399,
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

## US-6246 Hampton Creek Cove State Natural Area
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-08",
 "n": "Hampton Creek Cove State Natural Area",
 "official": null,
 "ours": {
  "acres": 458,
  "dissolved": {
   "after": 684,
   "before": 2043,
   "copies": 2,
   "key_union": 458,
   "parts": 0,
   "records": 4,
   "summed": 684,
   "tracts": 2
  },
  "manager": "",
  "note": "4 joined records = 2 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 2043 -> 684 acres",
  "pieces": [
   [
    "tnd72",
    "Hampton Creek Cove State Natural Area",
    681,
    "name"
   ],
   [
    "sgtnh40",
    "Hampton Creek Cove State Natural Area",
    3,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "State Natural Area",
 "verdict": "no size on page"
}
```

## US-6249 House Mountain State Natural Area
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-08",
 "n": "House Mountain State Natural Area",
 "official": null,
 "ours": {
  "acres": 527,
  "dissolved": {
   "after": 527,
   "before": 1581,
   "copies": 1,
   "parts": 2,
   "records": 4,
   "tracts": 1
  },
  "manager": "",
  "note": "4 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 2 fee tracts under a designation record folded; summed 1581 -> 527 acres",
  "pieces": [
   [
    255658,
    "House Mountain Designated State Natural Area",
    527,
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
 "t": "State Natural Area",
 "verdict": "no size on page"
}
```

## US-6239 Colditz Cove State Natural Area
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-08",
 "n": "Colditz Cove State Natural Area",
 "official": null,
 "ours": {
  "acres": 161,
  "manager": "",
  "pieces": [
   [
    255683,
    "Colditz Cove Designated State Natural Area",
    161,
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
 "t": "State Natural Area",
 "verdict": "no size on page"
}
```

## US-2971 Reelfoot Lake State Park
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-08",
 "n": "Reelfoot Lake State Park",
 "official": null,
 "ours": {
  "acres": 18391,
  "dissolved": {
   "after": 20055,
   "before": 45812,
   "copies": 2,
   "families": {
    "padus": 7171,
    "tnd": 12884
   },
   "family_fold": 7171,
   "family_used": "tnd",
   "key_union": 18391,
   "parts": 0,
   "records": 4,
   "summed": 12884,
   "tracts": 2
  },
  "family_fold": "layers {'tnd': 12884, 'padus': 7171}: one land in 2 layers, the tnd copy used (7,171 ac of copies not added)",
  "manager": "",
  "note": "4 joined records = 2 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 45812 -> 20055 acres",
  "pieces": [
   [
    "tnd128",
    "Reelfoot Lake State Park",
    12884,
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
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-6262 Powell River State Natural Area
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-08",
 "n": "Powell River State Natural Area",
 "official": null,
 "ours": {
  "acres": 12,
  "dissolved": {
   "after": 17,
   "before": 51,
   "copies": 2,
   "key_union": 12,
   "parts": 0,
   "records": 3,
   "summed": 17,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 51 -> 17 acres",
  "pieces": [
   [
    255672,
    "Powell River TNC Preserve Designated State Natural Area",
    17,
    "words"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "State Natural Area",
 "verdict": "no size on page"
}
```

## US-7590 Fourth Fractional Township Wildlife Management Area
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-08",
 "n": "Fourth Fractional Township Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 689,
  "dissolved": {
   "after": 1641,
   "before": 2295,
   "copies": 1,
   "families": {
    "padus": 654,
    "sgtnc": 468,
    "sgtne": 519
   },
   "family_fold": 987,
   "family_used": "padus",
   "key_union": 689,
   "parts": 0,
   "records": 4,
   "summed": 654,
   "tracts": 3
  },
  "family_fold": "layers {'padus': 654, 'sgtne': 519, 'sgtnc': 468}: one land in 3 layers, the padus copy used (987 ac of copies not added)",
  "manager": "",
  "note": "4 joined records = 3 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 2295 -> 1641 acres",
  "pieces": [
   [
    256221,
    "Fourth Fractional Township Wildlife Management Area",
    654,
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

## US-6244 Flat Rock Cedar Glade State Natural Area
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-08",
 "n": "Flat Rock Cedar Glade State Natural Area",
 "official": null,
 "ours": {
  "acres": 744,
  "dissolved": {
   "after": 936,
   "before": 2634,
   "copies": 2,
   "families": {
    "sgtnh": 86,
    "tnd": 850
   },
   "family_fold": 86,
   "family_used": "tnd",
   "key_union": 744,
   "parts": 0,
   "records": 5,
   "summed": 850,
   "tracts": 3
  },
  "family_fold": "layers {'tnd': 850, 'sgtnh': 86}: one land in 2 layers, the tnd copy used (86 ac of copies not added)",
  "manager": "",
  "note": "5 joined records = 3 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 2634 -> 936 acres",
  "pieces": [
   [
    "tnd64",
    "Flat Rock Cedar Glades and Barrens State Natural Area",
    850,
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
 "t": "State Natural Area",
 "verdict": "no size on page"
}
```

## US-2928 Bicentennial Capitol Mall State Park
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-08",
 "n": "Bicentennial Capitol Mall State Park",
 "official": null,
 "ours": {
  "acres": 17,
  "dissolved": {
   "after": 42,
   "before": 62,
   "copies": 1,
   "families": {
    "padus": 22,
    "tnd": 20
   },
   "family_fold": 20,
   "family_used": "padus",
   "key_union": 17,
   "parts": 0,
   "records": 3,
   "summed": 22,
   "tracts": 2
  },
  "family_fold": "layers {'padus': 22, 'tnd': 20}: one land in 2 layers, the padus copy used (20 ac of copies not added)",
  "manager": "",
  "note": "3 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 62 -> 42 acres",
  "pieces": [
   [
    255587,
    "Bicentennial",
    22,
    "words"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 3
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "State Park",
 "verdict": "no size on page"
}
```
