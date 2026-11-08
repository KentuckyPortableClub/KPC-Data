# park truth checker: US-VA random sample of 12 (2026-11-08; seed = date + area, same rows for everyone)

Source file: `data/truth/US-VA.json`

## US-1308 Mason Neck State Park
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 1,856 acres, no total words near it)",
 "checked": "2026-11-08",
 "handover": [],
 "n": "Mason Neck State Park",
 "official": {
  "acres": 1856.0,
  "as": "1,856 acres",
  "clean": false,
  "line": "Tidewater/Norfolk/Virginia Beach, three hours; Richmond, one and a half hours; Roanoke, four hours. Park Size 1,856 acres. Share this page Follow us Cabins, camping OVERNIGHT FACILITIES None - day-use park. For information on the a",
  "read": "2026-11-08",
  "sent": "1,856 acres.",
  "url": "https://www.dcr.virginia.gov/state-parks/mason-neck",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 1493,
  "dissolved": {
   "after": 1815,
   "before": 7347,
   "copies": 12,
   "families": {
    "padus": 1222,
    "sgvad": 593
   },
   "family_fold": 593,
   "family_used": "padus",
   "key_union": 1493,
   "parts": 8,
   "records": 24,
   "summed": 1222,
   "tracts": 4
  },
  "family_fold": "layers {'padus': 1222, 'sgvad': 593}: one land in 2 layers, the padus copy used (593 ac of copies not added)",
  "manager": "",
  "note": "24 joined records = 4 tracts: 12 copies of a tract (same acres, another layer) and 8 fee tracts under a designation record folded; summed 7347 -> 1815 acres",
  "pieces": [
   [
    270647,
    "Mason Neck State Park",
    1222,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 20,
 "same_agency": false,
 "score": 7,
 "t": "State Park",
 "verdict": "unsure"
}
```

## US-9908 Hoop Hole National Recreation Trail
```json
{
 "checked": "2026-11-08",
 "handover": [],
 "n": "Hoop Hole National Recreation Trail",
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

## US-9951 Priest Wilderness Area
```json
{
 "cause": "a number 17 parks share from one page (1,800,000 ac): an agency total, not this park",
 "checked": "2026-11-08",
 "handover": [],
 "n": "Priest Wilderness Area",
 "official": null,
 "ours": {
  "acres": 7131,
  "dissolved": {
   "after": 6011,
   "before": 12002,
   "copies": 1,
   "key_union": 7131,
   "parts": 0,
   "records": 2,
   "summed": 6011,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 12002 -> 6011 acres",
  "pieces": [
   [
    "sgvae500344",
    "The Priest NF Wilderness Area",
    6011,
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

## US-7788 Cape Charles State Natural Area
```json
{
 "cause": "a number 12 parks share from one page (66,000 ac): an agency total, not this park",
 "checked": "2026-11-08",
 "handover": [],
 "n": "Cape Charles State Natural Area",
 "official": null,
 "ours": {
  "acres": 40,
  "dissolved": {
   "after": 71,
   "before": 192,
   "copies": 1,
   "families": {
    "padus": 21,
    "sgvab": 50
   },
   "family_fold": 21,
   "family_used": "sgvab",
   "key_union": 40,
   "parts": 4,
   "records": 7,
   "summed": 50,
   "tracts": 2
  },
  "family_fold": "layers {'sgvab': 50, 'padus': 21}: one land in 2 layers, the sgvab copy used (21 ac of copies not added)",
  "manager": "",
  "note": "7 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 4 fee tracts under a designation record folded; summed 192 -> 71 acres",
  "pieces": [
   [
    "sgvab12",
    "Cape Charles",
    50,
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
 "score": 6,
 "t": "State Natural Area",
 "verdict": "unsure"
}
```

## US-1326 York River State Park
```json
{
 "cause": "agency smaller: our outline may hold water, a lease or a neighbour tract",
 "checked": "2026-11-08",
 "handover": [],
 "n": "York River State Park",
 "official": {
  "acres": 525.0,
  "as": "525 acre",
  "clean": false,
  "line": "AUNDRY None at this park. ENVIRONMENTAL EDUCATION CENTER Under development. SPECIAL FEATURES Taskinas Creek's 525-acre watershed is one of four sites along the York River designated as a Chesapeake Bay National Estuarine Researc",
  "read": "2026-11-08",
  "sent": "Taskinas Creek's 525-acre watershed is one of four sites along the York River designated as a Chesapeake Bay National Estuarine Research Reserve.",
  "url": "https://www.dcr.virginia.gov/state-parks/york-river",
  "why": "total-looking"
 },
 "ours": {
  "acres": 2341,
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
   "key_union": 2341,
   "parts": 0,
   "records": 12,
   "summed": 2910,
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
 "pct": 346,
 "same_agency": false,
 "score": 6,
 "t": "State Park",
 "verdict": "off"
}
```

## US-1320 Southwest Virginia Museum State Park
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 1.5 acres, a tiny number without size wording)",
 "checked": "2026-11-08",
 "handover": [],
 "n": "Southwest Virginia Museum State Park",
 "official": {
  "acres": 1.5,
  "as": "1.5 acres",
  "clean": false,
  "line": "anoke, 4 hours; Knoxville, Tenn., 2 hours; Lexington, Ky., 2.5 hours; Winston-Salem, N.C., 3 hours. Park Size 1.5 acres. Share this page Follow us Cabins, camping OVERNIGHT FACILITIES Poplar Hill Cottage is the perfect mountain g",
  "read": "2026-11-08",
  "sent": "1.5 acres.",
  "url": "https://www.dcr.virginia.gov/state-parks/southwest-virginia-museum",
  "why": "a tiny number without size wording"
 },
 "ours": {
  "acres": 4,
  "dissolved": {
   "after": 1,
   "before": 5,
   "copies": 4,
   "key_union": 4,
   "parts": 0,
   "records": 5,
   "summed": 1,
   "tracts": 1
  },
  "manager": "",
  "note": "5 joined records = 1 tracts: 4 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 5 -> 1 acres",
  "pieces": [
   [
    271176,
    "Southwest Virginia Museum Historical State Park",
    1,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 17
 },
 "owner_now": null,
 "pct": 167,
 "same_agency": false,
 "score": 7,
 "t": "State Park",
 "verdict": "unsure"
}
```

## US-9901 Civil War Defenses of Washington National Historic Trail
```json
{
 "checked": "2026-11-08",
 "handover": [],
 "n": "Civil War Defenses of Washington National Historic Trail",
 "note": "whole park compared (POTA lists it in 0 states: {})",
 "official": {
  "acres": 130.0,
  "as": "130 acres",
  "clean": false,
  "line": "y. Places to visit Today 18 fort sites are administered by the National Park Service located on approximately 130 acres. The Battle of Fort Stevens Join us each July for the annual commemoration of the Battle of Fort Stevens and",
  "read": "2026-11-08",
  "sent": "Today 18 fort sites are administered by the National Park Service located on approximately 130 acres.",
  "url": "https://www.nps.gov/cwdw/index.htm",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 0,
  "acres_by_state": {},
  "manager": "",
  "pieces": [],
  "pin": "inside",
  "src": "",
  "states": [
   "US-VA",
   "US-DC",
   "US-MD"
  ],
  "unknown_pieces": 1,
  "whole_park": true
 },
 "owner_now": null,
 "pct": null,
 "same_agency": false,
 "score": 4,
 "t": "National Historic Trail",
 "verdict": "ours unknown"
}
```

## US-1297 Fairy Stone State Park
```json
{
 "checked": "2026-11-08",
 "handover": [],
 "n": "Fairy Stone State Park",
 "official": {
  "acres": 4741.0,
  "as": "4,741 acres",
  "clean": false,
  "line": "ington, DC); Richmond, four hours; Tidewater/ Norfolk/Virginia Beach, five hours; Roanoke, one hour Park Size 4,741 acres, 168-acre lake adjoining the Philpott Reservoir. Share this page Follow us Cabins, camping OVERNIGHT FACILITI",
  "read": "2026-11-08",
  "sent": "4,741 acres, 168-acre lake adjoining the Philpott Reservoir.",
  "url": "https://www.dcr.virginia.gov/state-parks/fairy-stone",
  "why": "part (a lake, a purchase, a campground…)"
 },
 "ours": {
  "acres": 5446,
  "dissolved": {
   "after": 10085,
   "before": 20272,
   "copies": 4,
   "families": {
    "padus": 5446,
    "sgvad": 4639
   },
   "family_fold": 4639,
   "family_used": "padus",
   "parts": 0,
   "records": 7,
   "tracts": 3
  },
  "family_fold": "layers {'padus': 5446, 'sgvad': 4639}: one land in 2 layers, the padus copy used (4,639 ac of copies not added)",
  "manager": "",
  "note": "7 joined records = 3 tracts: 4 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 20272 -> 10085 acres",
  "pieces": [
   [
    54562,
    "Fairy Stone State Park",
    5344,
    "name"
   ],
   [
    270620,
    "Fairy Stone State Park",
    102,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 15,
 "same_agency": false,
 "score": 8,
 "t": "State Park",
 "verdict": "agree"
}
```

## US-1302 Holliday Lake State Park
```json
{
 "checked": "2026-11-08",
 "handover": [],
 "n": "Holliday Lake State Park",
 "official": {
  "acres": 560.0,
  "as": "560 acres",
  "clean": false,
  "line": "a half hours; Richmond, two hours; Tidewater/Norfolk/Virginia Beach, four hours; Roanoke, two hours Park Size 560 acres. Lake: 119 acres. Share this page Follow us Cabins, camping OVERNIGHT FACILITIES For information on the avail",
  "read": "2026-11-08",
  "sent": "560 acres.",
  "url": "https://www.dcr.virginia.gov/state-parks/holliday-lake",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 624,
  "dissolved": {
   "after": 560,
   "before": 2800,
   "copies": 6,
   "key_union": 624,
   "parts": 2,
   "records": 9,
   "summed": 560,
   "tracts": 1
  },
  "manager": "",
  "note": "9 joined records = 1 tracts: 6 copies of a tract (same acres, another layer) and 2 fee tracts under a designation record folded; summed 2800 -> 560 acres",
  "pieces": [
   [
    270630,
    "Holliday Lake State Park",
    560,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 11,
 "same_agency": false,
 "score": 8,
 "t": "State Park",
 "verdict": "agree"
}
```

## US-10507 Rock Castle Gorge National Recreation Trail
```json
{
 "checked": "2026-11-08",
 "handover": [],
 "n": "Rock Castle Gorge National Recreation Trail",
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

## US-0935 George Washington Birthplace National Monument
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-08",
 "handover": [],
 "n": "George Washington Birthplace National Monument",
 "official": {
  "acres": 551.0,
  "as": "551 acres",
  "clean": false,
  "line": "ia George Washington Birthplace National Monument is located in the Northern Neck of Virginia. It encompasses 551 acres of land where seven generations of the Washington family lived and where George Washington was born in 1732.",
  "read": "2026-11-08",
  "sent": "It encompasses 551 acres of land where seven generations of the Washington family lived and where George Washington was born in 1732.",
  "url": "https://www.nps.gov/gewa/index.htm",
  "why": "total-looking"
 },
 "ours": {
  "acres": 468,
  "family_fold": "layers {'padus': 556, 'sgvae': 475}: one land in 2 layers, the padus copy used (475 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    3376,
    "George Washington Birthplace National Monument",
    556,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 15,
 "same_agency": false,
 "score": 6,
 "t": "National Monument",
 "verdict": "off"
}
```

## US-5514 Dragon Run State Forest
```json
{
 "checked": "2026-11-08",
 "handover": [],
 "n": "Dragon Run State Forest",
 "official": {
  "acres": 9563.0,
  "as": "9,563 acres",
  "clean": false,
  "line": "ea Contacts Find a Forester Upcoming Events Dragon Run State Forest Overview Dragon Run State Forest occupies 9,563 acres in King and Queen County. This forest of mostly loblolly pine is managed for multiple uses: watershed protect",
  "read": "2026-11-08",
  "sent": "Dragon Run State Forest occupies 9,563 acres in King and Queen County.",
  "url": "https://dof.virginia.gov/education-and-recreation/state-forests/virginia-state-forests/dragon-run-state-forest/",
  "why": "total-looking"
 },
 "ours": {
  "acres": 9719,
  "dissolved": {
   "after": 19282,
   "before": 38407,
   "copies": 1,
   "families": {
    "padus": 9563,
    "sgvae": 9719
   },
   "family_fold": 9563,
   "family_used": "sgvae",
   "parts": 2,
   "records": 7,
   "tracts": 4
  },
  "family_fold": "layers {'padus': 9563, 'sgvae': 9719}: one land in 2 layers, the sgvae copy used (9,563 ac of copies not added)",
  "manager": "",
  "note": "7 joined records = 4 tracts: 1 copies of a tract (same acres, another layer) and 2 fee tracts under a designation record folded; summed 38407 -> 19282 acres",
  "pieces": [
   [
    "sgvae486814",
    "Dragon Run State Forest",
    5383,
    "name"
   ],
   [
    "sgvae486766",
    "Dragon Run State Forest",
    2410,
    "name"
   ],
   [
    "sgvae486765",
    "Dragon Run State Forest",
    1926,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 2,
 "same_agency": false,
 "score": 7,
 "t": "State Forest",
 "verdict": "agree"
}
```
