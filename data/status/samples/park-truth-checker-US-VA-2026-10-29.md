# park truth checker: US-VA random sample of 12 (2026-10-29; seed = date + area, same rows for everyone)

Source file: `data/truth/US-VA.json`

## US-9946 Lewis Fork Wilderness Area
```json
{
 "cause": "a number 6 parks share from one page (1,800,000 ac): an agency total, not this park",
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-10-29",
 "n": "Lewis Fork Wilderness Area",
 "official": null,
 "ours": {
  "acres": 6080,
  "dissolved": {
   "after": 6080,
   "before": 12155,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 12155 -> 6080 acres",
  "pieces": [
   [
    "sgvae500352",
    "Lewis Fork NF Wilderness Area",
    6080,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "same_agency": false,
 "score": 6,
 "t": "Wilderness Area",
 "verdict": "unsure"
}
```

## US-9940 Brush Mountain Wilderness Area
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-10-29",
 "n": "Brush Mountain Wilderness Area",
 "official": null,
 "ours": {
  "acres": 8540,
  "dissolved": {
   "after": 8540,
   "before": 17079,
   "copies": 2,
   "parts": 0,
   "records": 4,
   "tracts": 2
  },
  "manager": "",
  "note": "4 joined records = 2 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 17079 -> 8540 acres",
  "pieces": [
   [
    "wld46",
    "Brush Mountain Wilderness",
    4795,
    "name"
   ],
   [
    "wld45",
    "Brush Mountain East Wilderness",
    3745,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 5,
 "t": "Wilderness Area",
 "verdict": "unsure"
}
```

## US-9957 Shenandoah Wilderness Area
```json
{
 "cause": "agency smaller: our outline may hold water, a lease or a neighbour tract",
 "checked": "2026-10-29",
 "handover": [],
 "n": "Shenandoah Wilderness Area",
 "official": {
  "acres": 79579.0,
  "as": "79,579 acres",
  "clean": true,
  "line": "otected as wilderness, the highest form of protection for our public lands. Shenandoah National Park contains 79,579 acres of congressionally designated wilderness, nearly 40% of the park’s acreage. This makes the Shenandoah Wildern",
  "read": "2026-10-29",
  "sent": "Shenandoah National Park contains 79,579 acres of congressionally designated wilderness, nearly 40% of the park’s acreage.",
  "url": "https://www.nps.gov/shen/learn/wilderness.htm",
  "why": "clean total"
 },
 "ours": {
  "acres": 195790,
  "manager": "",
  "pieces": [
   [
    3474,
    "Shenandoah National Park",
    195790,
    "reviewed-approx"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 146,
 "same_agency": false,
 "score": 4,
 "t": "Wilderness Area",
 "verdict": "off"
}
```

## US-0707 Petersburg National Battlefield
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Petersburg National Battlefield",
 "official": null,
 "ours": {
  "acres": 2702,
  "dissolved": {
   "after": 3020,
   "before": 6741,
   "copies": 1,
   "families": {
    "padus": 2702,
    "sgvae": 318
   },
   "family_fold": 318,
   "family_used": "padus",
   "parts": 57,
   "records": 64,
   "tracts": 6
  },
  "family_fold": "layers {'padus': 2702, 'sgvae': 318}: one land in 2 layers, the padus copy used (318 ac of copies not added)",
  "manager": "",
  "note": "64 joined records = 6 tracts: 1 copies of a tract (same acres, another layer) and 57 fee tracts under a designation record folded; summed 6741 -> 3020 acres",
  "pieces": [
   [
    3101,
    "Petersburg National Battlefield",
    2702,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 14
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "National Battlefield",
 "verdict": "no size on page"
}
```

## US-9953 Ramseys Draft Wilderness Area
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-10-29",
 "n": "Ramseys Draft Wilderness Area",
 "official": null,
 "ours": {
  "acres": 6577,
  "dissolved": {
   "after": 6577,
   "before": 13150,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 13150 -> 6577 acres",
  "pieces": [
   [
    "wld356",
    "Ramseys Draft Wilderness",
    6577,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "Wilderness Area",
 "verdict": "no size on page"
}
```

## US-7794 Goshen Pass State Natural Area
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Goshen Pass State Natural Area",
 "official": {
  "acres": 936.0,
  "as": "936 acres",
  "clean": false,
  "line": "of local citizens during the previous decades, as well as a grant from the Perry Foundation. In 2002, these 936 acres were dedicated as Goshen Pass Natural Area Preserve. Natural History About 420 million years ago, the area",
  "read": "2026-10-29",
  "sent": "In 2002, these 936 acres were dedicated as Goshen Pass",
  "url": "https://www.dcr.virginia.gov/natural-heritage/document/pggoshenpass.pdf",
  "why": "total-looking"
 },
 "ours": {
  "acres": 1012,
  "dissolved": {
   "after": 1012,
   "before": 3827,
   "copies": 2,
   "parts": 2,
   "records": 7,
   "tracts": 3
  },
  "manager": "",
  "note": "7 joined records = 3 tracts: 2 copies of a tract (same acres, another layer) and 2 fee tracts under a designation record folded; summed 3827 -> 1012 acres",
  "pieces": [
   [
    54448,
    "Goshen Pass State Natural Area Preserve",
    942,
    "words"
   ],
   [
    54447,
    "Goshen Pass State Natural Area Preserve",
    35,
    "words"
   ],
   [
    270564,
    "Goshen Pass State Natural Area Preserve",
    35,
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
 "t": "State Natural Area",
 "verdict": "agree"
}
```

## US-9899 Fort Hunt National Historical Site
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Fort Hunt National Historical Site",
 "official": null,
 "ours": {
  "acres": 19,
  "manager": "",
  "pieces": [
   [
    "sgvae488032",
    "Fort Hunt",
    19,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 4,
 "t": "National Historical Site",
 "verdict": "no size on page"
}
```

## US-9968 Buller State Fish Hatchery
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-10-29",
 "handover": [],
 "n": "Buller State Fish Hatchery",
 "official": {
  "acres": 147.0,
  "as": "147 acres",
  "clean": true,
  "line": "in Smyth County Virginia, 8 miles south of Marion near the community of Thomas Bridge. The property comprises 147 acres of land, of which only 35 acres have been developed. The South Fork of the Holston River that flows through t",
  "read": "2026-10-29",
  "sent": "The property comprises 147 acres of land, of which only 35 acres have been developed.",
  "url": "https://dwr.virginia.gov/fishing/fish-stocking/state-hatcheries/buller-fish-hatchery/",
  "why": "clean total"
 },
 "ours": {
  "acres": 116,
  "dissolved": {
   "after": 148,
   "before": 264,
   "copies": 0,
   "families": {
    "padus": 116,
    "sgvae": 32
   },
   "family_fold": 32,
   "family_used": "padus",
   "parts": 2,
   "records": 4,
   "tracts": 2
  },
  "family_fold": "layers {'padus': 116, 'sgvae': 32}: one land in 2 layers, the padus copy used (32 ac of copies not added)",
  "manager": "",
  "note": "4 joined records = 2 tracts: 0 copies of a tract (same acres, another layer) and 2 fee tracts under a designation record folded; summed 264 -> 148 acres",
  "pieces": [
   [
    270527,
    "Buller Fish Hatchery",
    116,
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
 "t": "State Fish Hatchery",
 "verdict": "off"
}
```

## US-5515 Hawks State Forest
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-10-29",
 "handover": [],
 "n": "Hawks State Forest",
 "official": null,
 "ours": {
  "acres": 244,
  "dissolved": {
   "after": 244,
   "before": 488,
   "copies": 2,
   "parts": 0,
   "records": 4,
   "tracts": 2
  },
  "manager": "",
  "note": "4 joined records = 2 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 488 -> 244 acres",
  "pieces": [
   [
    57436,
    "Hawks State Forest",
    122,
    "name"
   ],
   [
    270422,
    "Hawks State Forest",
    122,
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
 "t": "State Forest",
 "verdict": "unsure"
}
```

## US-9969 Front Royal State Fish Hatchery
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Front Royal State Fish Hatchery",
 "official": null,
 "ours": {
  "acres": 176,
  "dissolved": {
   "after": 176,
   "before": 264,
   "copies": 1,
   "parts": 0,
   "records": 3,
   "tracts": 2
  },
  "manager": "",
  "note": "3 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 264 -> 176 acres",
  "pieces": [
   [
    58212,
    "Front Royal Fish Hatchery",
    88,
    "name"
   ],
   [
    270530,
    "Front Royal Fish Hatchery",
    88,
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
 "t": "State Fish Hatchery",
 "verdict": "no size on page"
}
```

## US-0905 Booker T. Washington National Monument
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-10-29",
 "handover": [],
 "n": "Booker T. Washington National Monument",
 "official": null,
 "ours": {
  "acres": 244,
  "family_fold": "layers {'padus': 244, 'sgvae': 239}: one land in 2 layers, the padus copy used (239 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    3342,
    "Booker T. Washington National Monument",
    244,
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
 "t": "National Monument",
 "verdict": "unsure"
}
```

## US-1326 York River State Park
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "York River State Park",
 "official": {
  "acres": 2954.0,
  "as": "2,954 acres",
  "clean": false,
  "line": "e hour; Tidewater/Norfolk/Virginia Beach, one hour; Fredericksburg, two hours; Roanoke, five hours. Park Size 2,954 acres. Share this page Follow us Cabins, camping OVERNIGHT FACILITIES York River is a day-use park with no overnigh",
  "read": "2026-10-29",
  "sent": "2,954 acres.",
  "url": "https://www.dcr.virginia.gov/state-parks/york-river",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 2910,
  "dissolved": {
   "after": 5286,
   "before": 11573,
   "copies": 7,
   "families": {
    "padus": 2376,
    "sgvad": 2910
   },
   "family_fold": 2376,
   "family_used": "sgvad",
   "parts": 0,
   "records": 12,
   "tracts": 5
  },
  "family_fold": "layers {'sgvad': 2910, 'padus': 2376}: one land in 2 layers, the sgvad copy used (2,376 ac of copies not added)",
  "manager": "",
  "note": "12 joined records = 5 tracts: 7 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 11573 -> 5286 acres",
  "pieces": [
   [
    "sgvad165",
    "York River State Park",
    2509,
    "name"
   ],
   [
    "sgvad293",
    "York River State Park",
    401,
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
