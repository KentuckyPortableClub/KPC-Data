# park truth checker: US-NC random sample of 12 (2026-11-01; seed = date + area, same rows for everyone)

Source file: `data/truth/US-NC.json`

## US-2750 Pilot Mountain State Park
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Pilot Mountain State Park",
 "official": null,
 "ours": {
  "acres": 3933,
  "dissolved": {
   "after": 3933,
   "before": 7857,
   "copies": 1,
   "parts": 0,
   "records": 3,
   "tracts": 2
  },
  "manager": "",
  "note": "3 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 7857 -> 3933 acres",
  "pieces": [
   [
    214863,
    "Pilot Mountain State Park",
    3924,
    "name"
   ],
   [
    "sgnca21381",
    "Pilot Mountain State Park Dedicated Nature Preserve",
    9,
    "words"
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

## US-2730 Fort Macon State Park
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Fort Macon State Park",
 "official": null,
 "ours": {
  "acres": 537,
  "dissolved": {
   "after": 901,
   "before": 1438,
   "copies": 1,
   "families": {
    "padus": 537,
    "sgnca": 364
   },
   "family_fold": 364,
   "family_used": "padus",
   "parts": 0,
   "records": 3,
   "tracts": 2
  },
  "family_fold": "layers {'padus': 537, 'sgnca': 364}: one land in 2 layers, the padus copy used (364 ac of copies not added)",
  "manager": "",
  "note": "3 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1438 -> 901 acres",
  "pieces": [
   [
    214832,
    "Fort Macon State Park",
    537,
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

## US-6839 Fort Dobbs State Historic Site
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Fort Dobbs State Historic Site",
 "official": null,
 "ours": {
  "acres": 58,
  "dissolved": {
   "after": 58,
   "before": 115,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 115 -> 58 acres",
  "pieces": [
   [
    "sgnca3553",
    "Fort Dobbs State Historic Site",
    58,
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

## US-8007 Edenton National Fish Hatchery
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Edenton National Fish Hatchery",
 "official": null,
 "ours": {
  "acres": 122,
  "family_fold": "layers {'sgnca': 66, 'padus': 122}: one land in 2 layers, the padus copy used (66 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    3802,
    "Edenton National Fish Hatchery",
    61,
    "name"
   ],
   [
    4742,
    "Edenton National Fish Hatchery",
    61,
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
 "t": "National Fish Hatchery",
 "verdict": "no size on page"
}
```

## US-6938 Pond Mountain State Game Land
```json
{
 "cause": "agency smaller: our outline may hold water, a lease or a neighbour tract",
 "checked": "2026-10-29",
 "handover": [],
 "n": "Pond Mountain State Game Land",
 "official": {
  "acres": 2900.0,
  "as": "2,900 acre",
  "clean": false,
  "line": "nd Mountain now offers one of the largest public access game land properties in northwest North Carolina. The 2,900 acre game lands allows recreational opportunities such as horseback riding, hiking, fishing, hunting, and cross co",
  "read": "2026-10-29",
  "sent": "The 2,900 acre game lands allows recreational opportunities such as horseback riding, hiking, fishing, hunting, and cross country skiing.",
  "url": "https://blueridgeconservancy.org/pond-mountain-game-lands-1/",
  "why": "total-looking"
 },
 "ours": {
  "acres": 7219,
  "family_fold": "layers {'sgnca': 7219, 'sgncb': 3701, 'padus': 3619}: one land in 3 layers, the sgnca copy used (7,320 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgnca5957",
    "Pond Mountain Game Land",
    3791,
    "name"
   ],
   [
    "sgnca21392",
    "Pond Mountain Game Land Dedicated Nature Preserve",
    3428,
    "words"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 149,
 "same_agency": false,
 "score": 5,
 "t": "State Game Land",
 "verdict": "off"
}
```

## US-6842 Historic Edenton State Historic Site
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Historic Edenton State Historic Site",
 "official": null,
 "ours": {
  "acres": 192,
  "manager": "",
  "pieces": [
   [
    "sgnca3874",
    "Historic Edenton State Historic Site",
    190,
    "name"
   ],
   [
    214566,
    "Historic Edenton State Historic Site",
    2,
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

## US-4858 Mountain Island Educational State Forest
```json
{
 "checked": "2026-10-29",
 "handover": [],
 "n": "Mountain Island Educational State Forest",
 "official": null,
 "ours": {
  "acres": 1680,
  "manager": "",
  "pieces": [
   [
    "sgnca9170",
    "Mountain Island Lakes Educational State Forest",
    1680,
    "words"
   ]
  ],
  "pin": "just outside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 5,
 "t": "State Forest",
 "verdict": "no size on page"
}
```

## US-0566 Great Dismal Swamp National Wildlife Refuge
```json
{
 "checked": "2026-10-29",
 "handover": [
  {
   "date_hint": "1974",
   "kind": "transfer",
   "line": "n of this resource began in 1973, when the Union Camp Corporation (a local forest products company) donated 49,097acres to The Nature Conservancy. The Nature Conservancy conveyed the donated land to the federal government, which, combined with additionally purchased land, was used to establish the G",
   "owner_now": "The Nature Conservancy",
   "src": "https://www.fws.gov/refuge/great-dismal-swamp/about-us",
   "why": "about / history page of the park's site"
  }
 ],
 "n": "Great Dismal Swamp National Wildlife Refuge",
 "note": "whole park compared (POTA lists it in 2 states: {'US-NC': 27628, 'US-VA': 86451})",
 "official": {
  "acres": 113000.0,
  "as": "113,000 acres",
  "clean": false,
  "line": "onal Wildlife Refuge contains some of the most important wildlife habitat in the mid-Atlantic region. At near 113,000 acres, the refuge is the largest intact remnant of a vast swamp that once covered more than one million acres. Lear",
  "read": "2026-10-29",
  "sent": "At near 113,000 acres, the refuge is the largest intact remnant of a vast swamp that once covered more than one million acres.",
  "url": "https://www.fws.gov/refuge/great_dismal_swamp/",
  "why": "history"
 },
 "ours": {
  "acres": 114079,
  "acres_by_state": {
   "US-NC": 27628,
   "US-VA": 86451
  },
  "dissolved": {
   "after": 27628,
   "before": 82768,
   "copies": 2,
   "parts": 0,
   "records": 3,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 82768 -> 27628 acres",
  "pieces": [
   [
    3883,
    "Great Dismal Swamp National Wildlife Refuge",
    27628,
    "name"
   ]
  ],
  "pin": "well outside",
  "src": "USGS PAD-US",
  "states": [
   "US-NC",
   "US-VA"
  ],
  "unknown_pieces": 0,
  "whole_park": true
 },
 "owner_now": "The Nature Conservancy",
 "pct": 1,
 "same_agency": false,
 "score": 6,
 "t": "National Wildlife Refuge",
 "verdict": "agree"
}
```

## US-11020 Middle Prong Wilderness Area
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-10-29",
 "n": "Middle Prong Wilderness Area",
 "official": null,
 "ours": {
  "acres": 7482,
  "dissolved": {
   "after": 7482,
   "before": 14962,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 14962 -> 7482 acres",
  "pieces": [
   [
    "wld286",
    "Middle Prong Wilderness",
    7482,
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

## US-6935 Perkins State Game Land
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-10-29",
 "n": "Perkins State Game Land",
 "official": null,
 "ours": {
  "acres": 1696,
  "dissolved": {
   "after": 1696,
   "before": 5088,
   "copies": 2,
   "parts": 0,
   "records": 3,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 5088 -> 1696 acres",
  "pieces": [
   [
    "ncg61",
    "Perkins",
    1696,
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
 "t": "State Game Land",
 "verdict": "no size on page"
}
```

## US-6928 Needmore State Game Land
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-10-29",
 "n": "Needmore State Game Land",
 "official": null,
 "ours": {
  "acres": 5237,
  "dissolved": {
   "after": 5237,
   "before": 15561,
   "copies": 1,
   "parts": 2,
   "records": 4,
   "tracts": 1
  },
  "manager": "",
  "note": "4 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 2 fee tracts under a designation record folded; summed 15561 -> 5237 acres",
  "pieces": [
   [
    "sgncb53",
    "Needmore",
    5237,
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
 "t": "State Game Land",
 "verdict": "no size on page"
}
```

## US-6917 Juniper Creek State Game Land
```json
{
 "checked": "2026-10-29",
 "handover": [
  {
   "date_hint": null,
   "kind": "closed",
   "line": "esignated Camping Area Disabled Sportsman Blind Gate Open Sep.1 - Mar.1, Apr.1-End Of Turkey Season Permanently Closed Gate Public Parking Bear Management Area Game Land Secondary Road 0 10.5 Miles 211 211 Exum Rd LineRd Ja",
   "owner_now": null,
   "src": "https://www.ncwildlife.gov/media/833/download?attachment",
   "why": "the park's page (data/parkinfo)"
  }
 ],
 "n": "Juniper Creek State Game Land",
 "official": {
  "acres": 20505.0,
  "as": "20,505 acres",
  "clean": false,
  "line": "JUNIPER CREEK GAME LAND N.C. Wildlife Resources Commission Brunswick and Columubs Counties (20,505 acres) Designated Camping Area Disabled Sportsman Blind Gate Open Sep.1 - Mar.1, Apr.1-End Of Turkey Season Permane",
  "read": "2026-10-29",
  "sent": "Brunswick and Columubs Counties (20,505 acres)",
  "url": "https://www.ncwildlife.gov/media/833/download?attachment",
  "why": "a map label (no sentence)"
 },
 "ours": {
  "acres": 20541,
  "dissolved": {
   "after": 20541,
   "before": 81880,
   "copies": 3,
   "parts": 0,
   "records": 4,
   "tracts": 1
  },
  "manager": "",
  "note": "4 joined records = 1 tracts: 3 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 81880 -> 20541 acres",
  "pieces": [
   [
    214742,
    "Juniper Creek Game Land",
    20541,
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
 "t": "State Game Land",
 "verdict": "agree"
}
```
