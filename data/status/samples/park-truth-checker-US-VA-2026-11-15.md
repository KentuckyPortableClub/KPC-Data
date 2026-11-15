# park truth checker: US-VA random sample of 12 (2026-11-15; seed = date + area, same rows for everyone)

Source file: `data/truth/US-VA.json`

## US-9910 Massanutten National Recreation Trail
```json
{
 "checked": "2026-11-08",
 "handover": [],
 "n": "Massanutten National Recreation Trail",
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
 "score": 5,
 "t": "National Recreation Trail",
 "verdict": "ours unknown"
}
```

## US-0569 Occoquan Bay National Wildlife Refuge
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-08",
 "handover": [],
 "n": "Occoquan Bay National Wildlife Refuge",
 "official": {
  "acres": 642.0,
  "as": "642 acres",
  "clean": false,
  "line": "arn, hunt, fish, or just watch wildlife Occoquan Bay National Wildlife Refuge has opportunities for you. With 642 acres, the refuge has 4 miles of trails, an information center, interpretive kiosks, a photography blind, a gazebo,",
  "read": "2026-11-08",
  "sent": "With 642 acres, the refuge has 4 miles of trails, an information center, interpretive kiosks, a photography blind, a gazebo, and two pavilions.",
  "url": "http://www.fws.gov/refuge/occoquan-bay/visit-us",
  "why": "total-looking"
 },
 "ours": {
  "acres": 460,
  "dissolved": {
   "after": 644,
   "before": 1912,
   "copies": 2,
   "key_union": 460,
   "parts": 0,
   "records": 3,
   "summed": 644,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1912 -> 644 acres",
  "pieces": [
   [
    "sgvae490550",
    "Occoquan Bay National Wildlife Refuge",
    644,
    "reviewed"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 28,
 "same_agency": false,
 "score": 5,
 "t": "National Wildlife Refuge",
 "verdict": "off"
}
```

## US-9929 First Mountain State Forest
```json
{
 "checked": "2026-11-08",
 "handover": [],
 "n": "First Mountain State Forest",
 "official": {
  "acres": 573.0,
  "as": "573 acres",
  "clean": true,
  "line": "orester Upcoming Events First Mountain State Forest &#xA0; &#xA0; Overview First Mountain State Forest covers 573 acres in Rockingham County. Management focuses on demonstration of scientific forest management, applied forest res",
  "read": "2026-11-08",
  "sent": "First Mountain State Forest covers 573 acres in Rockingham County.",
  "url": "https://dof.virginia.gov/education-and-recreation/state-forests/virginia-state-forests/first-mountain-state-forest/",
  "why": "clean total"
 },
 "ours": {
  "acres": 501,
  "dissolved": {
   "after": 1203,
   "before": 2397,
   "copies": 2,
   "families": {
    "padus": 620,
    "sgvae": 583
   },
   "family_fold": 583,
   "family_used": "padus",
   "key_union": 501,
   "parts": 0,
   "records": 4,
   "summed": 620,
   "tracts": 2
  },
  "family_fold": "layers {'padus': 620, 'sgvae': 583}: one land in 2 layers, the padus copy used (583 ac of copies not added)",
  "manager": "",
  "note": "4 joined records = 2 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 2397 -> 1203 acres",
  "pieces": [
   [
    57435,
    "First Mountain State Forest",
    620,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 13,
 "same_agency": false,
 "score": 8,
 "t": "State Forest",
 "verdict": "agree"
}
```

## US-4564 Potomac Heritage Trail National Scenic Trail
```json
{
 "checked": "2026-11-08",
 "handover": [],
 "n": "Potomac Heritage Trail National Scenic Trail",
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
   "US-VA",
   "US-PA",
   "US-DC",
   "US-MD"
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

## US-0573 Wallops Island National Wildlife Refuge
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-15",
 "n": "Wallops Island National Wildlife Refuge",
 "official": null,
 "ours": {
  "acres": 373,
  "dissolved": {
   "after": 733,
   "before": 1093,
   "copies": 1,
   "families": {
    "padus": 360,
    "sgvae": 373
   },
   "family_fold": 360,
   "family_used": "sgvae",
   "parts": 0,
   "records": 3,
   "tracts": 2
  },
  "family_fold": "layers {'sgvae': 373, 'padus': 360}: one land in 2 layers, the sgvae copy used (360 ac of copies not added)",
  "manager": "",
  "note": "3 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1093 -> 733 acres",
  "pieces": [
   [
    "sgvae490625",
    "Wallops Island National Wildlife Refuge",
    373,
    "name"
   ]
  ],
  "pin": "well outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 5,
 "t": "National Wildlife Refuge",
 "verdict": "no size on page"
}
```

## US-7636 Widewater State Park
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 1,089 acres, no total words near it)",
 "checked": "2026-11-08",
 "handover": [],
 "n": "Widewater State Park",
 "official": {
  "acres": 1089.0,
  "as": "1,089 acres",
  "clean": false,
  "line": "one and a half hours; Tidewater-Norfolk-Virginia Beach, two and a half hours; Roanoke, four hours. Park Size 1,089 acres. Share this page Follow us Cabins, camping OVERNIGHT FACILITIES Widewater has no cabins or full-service campi",
  "read": "2026-11-08",
  "sent": "1,089 acres.",
  "url": "https://www.dcr.virginia.gov/state-parks/widewater",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 1284,
  "dissolved": {
   "after": 2258,
   "before": 4428,
   "copies": 2,
   "families": {
    "padus": 1042,
    "sgvad": 1089,
    "sgvae": 127
   },
   "family_fold": 1169,
   "family_used": "sgvad",
   "key_union": 1284,
   "parts": 0,
   "records": 5,
   "summed": 1089,
   "tracts": 3
  },
  "family_fold": "layers {'sgvad': 1089, 'padus': 1042, 'sgvae': 127}: one land in 3 layers, the sgvad copy used (1,169 ac of copies not added)",
  "manager": "",
  "note": "5 joined records = 3 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 4428 -> 2258 acres",
  "pieces": [
   [
    "sgvad180",
    "Widewater State Park",
    1089,
    "reviewed"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 18,
 "same_agency": false,
 "score": 6,
 "t": "State Park",
 "verdict": "unsure"
}
```

## US-5507 Channels State Forest
```json
{
 "checked": "2026-11-08",
 "handover": [],
 "n": "Channels State Forest",
 "official": {
  "acres": 4836.0,
  "as": "4,836 acres",
  "clean": true,
  "line": "rking along Highway 80 is not permitted and violators will be ticketed. Overview Channels State Forest covers 4,836 acres in Washington and Russell counties. Management focuses on demonstration of scientific forest management, appl",
  "read": "2026-11-08",
  "sent": "Channels State Forest covers 4,836 acres in Washington and Russell counties.",
  "url": "https://dof.virginia.gov/education-and-recreation/state-forests/virginia-state-forests/channels-state-forest/",
  "why": "clean total"
 },
 "ours": {
  "acres": 5051,
  "dissolved": {
   "after": 8981,
   "before": 17902,
   "copies": 2,
   "key_union": 5051,
   "parts": 0,
   "records": 5,
   "summed": 8981,
   "tracts": 3
  },
  "manager": "",
  "note": "5 joined records = 3 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 17902 -> 8981 acres",
  "pieces": [
   [
    270433,
    "The Channels State Forest",
    4836,
    "name"
   ],
   [
    57448,
    "The Channels State Forest",
    4115,
    "name"
   ],
   [
    "sgvae486416",
    "The Channels State Forest",
    30,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 4,
 "same_agency": false,
 "score": 7,
 "t": "State Forest",
 "verdict": "agree"
}
```

## US-9948 Little Wilson Creek Wilderness Area
```json
{
 "cause": "a number 17 parks share from one page (1,800,000 ac): an agency total, not this park",
 "checked": "2026-11-08",
 "handover": [],
 "n": "Little Wilson Creek Wilderness Area",
 "official": null,
 "ours": {
  "acres": 4690,
  "dissolved": {
   "after": 5463,
   "before": 10924,
   "copies": 1,
   "key_union": 4690,
   "parts": 0,
   "records": 2,
   "summed": 5463,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 10924 -> 5463 acres",
  "pieces": [
   [
    "sgvae500389",
    "Little Wilson Creek NF Wilderness Area",
    5463,
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

## US-0929 Fort Monroe National Monument
```json
{
 "checked": "2026-11-08",
 "handover": [],
 "n": "Fort Monroe National Monument",
 "official": null,
 "ours": {
  "acres": 446,
  "family_fold": "layers {'sgvae': 565, 'padus': 122}: one land in 2 layers, the sgvae copy used (122 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgvae490590",
    "Fort Monroe National Monument",
    565,
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
 "t": "National Monument",
 "verdict": "no size on page"
}
```

## US-1298 False Cape State Park
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 4,321 acres, no total words near it)",
 "checked": "2026-11-08",
 "handover": [],
 "n": "False Cape State Park",
 "official": {
  "acres": 4321.0,
  "as": "4,321 acres",
  "clean": false,
  "line": "Drive Time: From Virginia Beach's oceanfront to Little Island city parking lot is about 40 minutes. Park Size 4,321 acres. Beach Size: 5.9 miles of beachfront, extending to the North Carolina line. Share this page Follow us Cabins,",
  "read": "2026-11-08",
  "sent": "4,321 acres.",
  "url": "https://www.dcr.virginia.gov/state-parks/false-cape",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 3538,
  "dissolved": {
   "after": 3889,
   "before": 11647,
   "copies": 11,
   "key_union": 3538,
   "parts": 9,
   "records": 24,
   "summed": 3889,
   "tracts": 4
  },
  "manager": "",
  "note": "24 joined records = 4 tracts: 11 copies of a tract (same acres, another layer) and 9 fee tracts under a designation record folded; summed 11647 -> 3889 acres",
  "pieces": [
   [
    270622,
    "False Cape State Park",
    3866,
    "name"
   ],
   [
    "sgvad155",
    "False Cape State Park",
    12,
    "name"
   ],
   [
    "sgvad151",
    "False Cape State Park",
    10,
    "name"
   ],
   [
    "sgvad158",
    "False Cape State Park",
    1,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 8
 },
 "owner_now": null,
 "pct": 18,
 "same_agency": false,
 "score": 6,
 "t": "State Park",
 "verdict": "unsure"
}
```

## US-1315 Seven Bends State Park
```json
{
 "cause": "agency smaller: our outline may hold water, a lease or a neighbour tract",
 "checked": "2026-11-08",
 "handover": [],
 "n": "Seven Bends State Park",
 "official": {
  "acres": 1052.0,
  "as": "1,052 acres",
  "clean": true,
  "line": "ates of operation, please email the park office at sevenbends@dcr.virginia.gov . HISTORY The park consists of 1,052 acres situated in the geographically unique Seven Bends area of the North Fork of the Shenandoah River. The majorit",
  "read": "2026-11-08",
  "sent": "The park consists of 1,052 acres situated in the geographically unique Seven Bends area of the North Fork of the Shenandoah River.",
  "url": "https://www.dcr.virginia.gov/state-parks/seven-bends",
  "why": "clean total"
 },
 "ours": {
  "acres": 1526,
  "dissolved": {
   "after": 1065,
   "before": 4264,
   "copies": 6,
   "key_union": 1526,
   "parts": 3,
   "records": 10,
   "summed": 1065,
   "tracts": 1
  },
  "manager": "",
  "note": "10 joined records = 1 tracts: 6 copies of a tract (same acres, another layer) and 3 fee tracts under a designation record folded; summed 4264 -> 1065 acres",
  "pieces": [
   [
    270667,
    "Seven Bends State Park",
    1065,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 45,
 "same_agency": false,
 "score": 5,
 "t": "State Park",
 "verdict": "off"
}
```

## US-9920 Mount Rogers National Recreation Trail
```json
{
 "checked": "2026-11-08",
 "handover": [],
 "n": "Mount Rogers National Recreation Trail",
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
 "score": 5,
 "t": "National Recreation Trail",
 "verdict": "ours unknown"
}
```
