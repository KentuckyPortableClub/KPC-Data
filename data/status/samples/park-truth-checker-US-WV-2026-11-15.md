# park truth checker: US-WV random sample of 12 (2026-11-15; seed = date + area, same rows for everyone)

Source file: `data/truth/US-WV.json`

## US-7044 Tug Fork Wildlife Management Area
```json
{
 "cause": "a number 76 parks share from one page (1,400,000 ac): an agency total, not this park",
 "checked": "2026-11-08",
 "handover": [],
 "n": "Tug Fork Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 8083,
  "family_fold": "layers {'padus': 6778, 'sgwva': 6520}: one land in 2 layers, the padus copy used (6,520 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    273206,
    "Tug Fork Wildlife Management Area",
    6778,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "same_agency": false,
 "score": 7,
 "t": "Wildlife Management Area",
 "verdict": "unsure"
}
```

## US-7040 Moncove Lake Wildlife Management Area
```json
{
 "cause": "a number 76 parks share from one page (1,400,000 ac): an agency total, not this park",
 "checked": "2026-11-08",
 "handover": [],
 "n": "Moncove Lake Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 631,
  "family_fold": "layers {'sgwva': 870, 'padus': 792}: one land in 2 layers, the sgwva copy used (792 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgwva104",
    "Moncove Lake Wildlife Management Area",
    870,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "same_agency": false,
 "score": 6,
 "t": "Wildlife Management Area",
 "verdict": "unsure"
}
```

## US-7029 Stonecoal Lake Wildlife Management Area
```json
{
 "cause": "a number 76 parks share from one page (1,400,000 ac): an agency total, not this park",
 "checked": "2026-11-08",
 "handover": [],
 "n": "Stonecoal Lake Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 3993,
  "dissolved": {
   "after": 3080,
   "before": 6158,
   "copies": 1,
   "key_union": 3993,
   "parts": 0,
   "records": 2,
   "summed": 3080,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 6158 -> 3080 acres",
  "pieces": [
   [
    272124,
    "Stonecoal Lake Wildlife Management Area",
    3080,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "same_agency": false,
 "score": 6,
 "t": "Wildlife Management Area",
 "verdict": "unsure"
}
```

## US-6993 Bear Rock Lakes Wildlife Management Area
```json
{
 "cause": "a number 76 parks share from one page (1,400,000 ac): an agency total, not this park",
 "checked": "2026-11-08",
 "handover": [],
 "n": "Bear Rock Lakes Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 284,
  "dissolved": {
   "after": 237,
   "before": 474,
   "copies": 1,
   "key_union": 284,
   "parts": 0,
   "records": 2,
   "summed": 237,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 474 -> 237 acres",
  "pieces": [
   [
    273143,
    "Bear Rock Lakes Wildlife Management Area",
    237,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "same_agency": false,
 "score": 7,
 "t": "Wildlife Management Area",
 "verdict": "unsure"
}
```

## US-7033 Wallback Wildlife Management Area
```json
{
 "cause": "a number 76 parks share from one page (1,400,000 ac): an agency total, not this park",
 "checked": "2026-11-08",
 "handover": [],
 "n": "Wallback Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 12560,
  "dissolved": {
   "after": 12560,
   "before": 25088,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 25088 -> 12560 acres",
  "pieces": [
   [
    273211,
    "Wallback Wildlife Management Area",
    12560,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "same_agency": false,
 "score": 7,
 "t": "Wildlife Management Area",
 "verdict": "unsure"
}
```

## US-0632 Monongahela National Forest
```json
{
 "checked": "2026-11-08",
 "handover": [],
 "n": "Monongahela National Forest",
 "official": {
  "acres": 900000.0,
  "as": "900,000 acres",
  "clean": false,
  "line": "ds and trails on the Monongahela National Forest except in designated… Fishing Fishing OverviewWith more than 900,000 acres of National Forest System lands that range in elevation between 1,425 feet and 4,863 feet above… View All Opp",
  "read": "2026-11-08",
  "sent": "Fishing OverviewWith more than 900,000 acres of National Forest System lands that range in elevation between 1,425 feet and 4,863 feet above…",
  "url": "https://www.fs.usda.gov/mnf",
  "why": "part (a lake, a purchase, a campground…)"
 },
 "ours": {
  "acres": 921100,
  "manager": "",
  "pieces": [
   [
    3069,
    "Monongahela National Forest",
    921100,
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
 "score": 7,
 "t": "National Forest",
 "verdict": "agree"
}
```

## US-12035 Dents Run Wildlife Management Area
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-11-08",
 "handover": [],
 "n": "Dents Run Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 1418,
  "dissolved": {
   "after": 1261,
   "before": 2521,
   "copies": 1,
   "key_union": 1418,
   "parts": 0,
   "records": 2,
   "summed": 1261,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 2521 -> 1261 acres",
  "pieces": [
   [
    273252,
    "Dents Run Wildlife Management Area",
    1261,
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

## US-1828 Watters Smith Memorial State Park
```json
{
 "cause": "agency smaller: our outline may hold water, a lease or a neighbour tract",
 "checked": "2026-11-08",
 "handover": [],
 "n": "Watters Smith Memorial State Park",
 "official": {
  "acres": 532.0,
  "as": "532 acre",
  "clean": false,
  "line": "West Virginia and the pioneer spirit of Watters Smith are both preserved in the homestead restoration at this 532-acre historical park. This historical park, located in Harrison County, features log cabins, period-accurate build",
  "read": "2026-11-08",
  "sent": "The heritage of early West Virginia and the pioneer spirit of Watters Smith are both preserved in the homestead restoration at this 532-acre historical park.",
  "url": "https://wvstateparks.com/park/watters-smith-memorial-state-park/",
  "why": "total-looking"
 },
 "ours": {
  "acres": 646,
  "dissolved": {
   "after": 537,
   "before": 1074,
   "copies": 1,
   "key_union": 646,
   "parts": 0,
   "records": 2,
   "summed": 537,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1074 -> 537 acres",
  "pieces": [
   [
    273251,
    "Watters Smith Memorial State Park",
    537,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 21,
 "same_agency": false,
 "score": 6,
 "t": "State Park",
 "verdict": "off"
}
```

## US-1813 Hawks Nest State Park
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-08",
 "handover": [],
 "n": "Hawks Nest State Park",
 "official": {
  "acres": 270.0,
  "as": "270 acre",
  "clean": true,
  "line": "ate Park Hawks Nest State Park Nestled in the heart of whitewater rafting country, Hawks Nest State Park is a 270-acre recreational area with a nature museum, jetboat rides, hiking trails and one of the most challenging whitewat",
  "read": "2026-11-08",
  "sent": "Nestled in the heart of whitewater rafting country, Hawks Nest State Park is a 270-acre recreational area with a nature museum, jetboat rides, hiking trails and one of the most challenging whitewater boating waterways in the nation.",
  "url": "https://wvstateparks.com/park/hawks-nest-state-park/",
  "why": "clean total"
 },
 "ours": {
  "acres": 114,
  "dissolved": {
   "after": 207,
   "before": 414,
   "copies": 1,
   "key_union": 114,
   "parts": 0,
   "records": 2,
   "summed": 207,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 414 -> 207 acres",
  "pieces": [
   [
    273234,
    "Hawks Nest State Park",
    207,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 58,
 "same_agency": false,
 "score": 6,
 "t": "State Park",
 "verdict": "off"
}
```

## US-1824 Twin Falls Resort State Park
```json
{
 "checked": "2026-11-08",
 "handover": [],
 "n": "Twin Falls Resort State Park",
 "official": null,
 "ours": {
  "acres": 3744,
  "dissolved": {
   "after": 3744,
   "before": 7486,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 7486 -> 3744 acres",
  "pieces": [
   [
    273247,
    "Twin Falls Resort State Park",
    3744,
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

## US-7053 McClintic Wildlife Management Area
```json
{
 "cause": "a number 76 parks share from one page (1,400,000 ac): an agency total, not this park",
 "checked": "2026-11-08",
 "handover": [],
 "n": "McClintic Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 3919,
  "family_fold": "layers {'sgwva': 3655, 'padus': 3395}: one land in 2 layers, the sgwva copy used (3,395 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgwva8",
    "McClintic Wildlife Management Area",
    3655,
    "reviewed"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "same_agency": false,
 "score": 7,
 "t": "Wildlife Management Area",
 "verdict": "unsure"
}
```

## US-1801 Berkeley Springs State Park
```json
{
 "checked": "2026-11-08",
 "handover": [],
 "n": "Berkeley Springs State Park",
 "official": null,
 "ours": {
  "acres": 5,
  "dissolved": {
   "after": 5,
   "before": 10,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 10 -> 5 acres",
  "pieces": [
   [
    273221,
    "Berkeley Springs State Park",
    5,
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
 "t": "State Park",
 "verdict": "no size on page"
}
```
