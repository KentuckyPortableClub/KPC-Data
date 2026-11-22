# park truth checker: US-GA random sample of 12 (2026-11-22; seed = date + area, same rows for everyone)

Source file: `data/truth/US-GA.json`

## US-3739 Chickasawhatchee Wildlife Management Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Chickasawhatchee Wildlife Management Area",
 "official": {
  "acres": 19700.0,
  "as": "19,700 acre",
  "clean": false,
  "line": "t Chickasawhatchee WMA Chickasawhatchee Wildlife Management Area is located 12 miles southwest of Albany. The 19,700-acre WMA includes the Mike Commander Shooting Range, a managed dove field and campsites for tents and RVs. The pro",
  "read": "2026-11-22",
  "sent": "The 19,700-acre WMA includes the Mike Commander Shooting Range, a managed dove field and campsites for tents and RVs.",
  "url": "https://georgiawildlife.com/chickasawhatchee-wma",
  "why": "part (a lake, a purchase, a campground…)"
 },
 "ours": {
  "acres": 19716,
  "dissolved": {
   "after": 19716,
   "before": 59138,
   "copies": 2,
   "parts": 0,
   "records": 3,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 59138 -> 19716 acres",
  "pieces": [
   [
    195027,
    "Chickasawhatchee Wildlife Management Area",
    19716,
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
 "t": "Wildlife Management Area",
 "verdict": "agree"
}
```

## US-3722 New Echota State Historic Site
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "New Echota State Historic Site",
 "official": null,
 "ours": {
  "acres": 204,
  "family_fold": "layers {'sggab': 204, 'padus': 193}: one land in 2 layers, the sggab copy used (193 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sggab44",
    "New Echtoa Historic Site",
    204,
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
 "t": "State Historic Site",
 "verdict": "no size on page"
}
```

## US-7904 Broad River Wildlife Management Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Broad River Wildlife Management Area",
 "official": {
  "acres": 440.0,
  "as": "440 acre",
  "clean": false,
  "line": "IFETIME Previous Next Broad River WMA Broad River Wildlife Management Area is located in Madison County. This 440-acre property offers hunting opportunities for deer, bear, turkey and small game (no furbearer season). Activities",
  "read": "2026-11-22",
  "sent": "This 440-acre property offers hunting opportunities for deer, bear, turkey and small game (no furbearer season).",
  "url": "https://georgiawildlife.com/broad-river-wma",
  "why": "total-looking"
 },
 "ours": {
  "acres": 433,
  "dissolved": {
   "after": 433,
   "before": 1291,
   "copies": 2,
   "parts": 0,
   "records": 3,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1291 -> 433 acres",
  "pieces": [
   [
    195020,
    "Broad River Wildlife Management Area",
    433,
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

## US-9758 Chattooga National Wild and Scenic River
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Chattooga National Wild and Scenic River",
 "note": "whole park compared (POTA lists it in 3 states: {'US-GA': 16528, 'US-NC': 16568, 'US-SC': 16528})",
 "official": null,
 "ours": {
  "acres": 49624,
  "acres_by_state": {
   "US-GA": 16528,
   "US-NC": 16568,
   "US-SC": 16528
  },
  "manager": "",
  "pieces": [
   [
    "fwsr180",
    "Chattooga, North Carolina, South Carolina and Georgia National Wild and Scenic River",
    10971,
    "reviewed"
   ],
   [
    "fwsr6",
    "Chattooga, North Carolina, South Carolina and Georgia National Wild and Scenic River",
    4651,
    "reviewed"
   ],
   [
    "fwsr95",
    "Chattooga, North Carolina, South Carolina and Georgia National Wild and Scenic River",
    906,
    "reviewed"
   ]
  ],
  "pin": "inside",
  "src": "",
  "states": [
   "US-GA",
   "US-NC",
   "US-SC"
  ],
  "unknown_pieces": 0,
  "whole_park": true
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "National Wild and Scenic River",
 "verdict": "no size on page"
}
```

## US-7138 Chestatee Wildlife Management Area
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-22",
 "handover": [],
 "n": "Chestatee Wildlife Management Area",
 "official": {
  "acres": 27124.0,
  "as": "27,124 acre",
  "clean": false,
  "line": "Previous Next Chestatee WMA Chestatee Wildlife Management Area is located in Lumpkin and White counties. This 27,124-acre property has hunting opportunities for deer, bear, turkey and small game. This property is owned by the U.S.",
  "read": "2026-11-22",
  "sent": "This 27,124-acre property has hunting opportunities for deer, bear, turkey and small game.",
  "url": "https://georgiawildlife.com/chestatee-wma",
  "why": "total-looking"
 },
 "ours": {
  "acres": 21784,
  "dissolved": {
   "after": 41508,
   "before": 63292,
   "copies": 1,
   "families": {
    "padus": 19724,
    "sggaa": 21784
   },
   "family_fold": 19724,
   "family_used": "sggaa",
   "parts": 0,
   "records": 3,
   "tracts": 2
  },
  "family_fold": "layers {'sggaa': 21784, 'padus': 19724}: one land in 2 layers, the sggaa copy used (19,724 ac of copies not added)",
  "manager": "",
  "note": "3 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 63292 -> 41508 acres",
  "pieces": [
   [
    "sggaa15",
    "CHESTATEE WMA",
    21784,
    "reviewed"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 20,
 "same_agency": false,
 "score": 6,
 "t": "Wildlife Management Area",
 "verdict": "off"
}
```

## US-7896 Standing Boy Creek State Park
```json
{
 "checked": "2026-11-22",
 "handover": [
  {
   "date_hint": "2026",
   "kind": "managed by",
   "line": "se Plate Previous Next 1 Standing Boy Creek Park Columbus Park Columbus Previous Next This property is managed by the City of Columbus. Celebrate America's 250th throughout 2026 - View a list of upcoming events . Home Standing Boy Creek Standing Boy Creek",
   "owner_now": "City of Columbus",
   "src": "https://gastateparks.org/StandingBoyCreek",
   "why": "the park's page (data/parkinfo)"
  },
  {
   "date_hint": null,
   "kind": "managed by",
   "line": "Lake Oliver and offers excellent opportunity for hiking, running, biking, and wildlife viewing. It is managed by The City of Columbus via Standing Boy, Inc., an independent 501(c)(3) nonprofit. Quota hunts are held during the fall and spring. All quo",
   "owner_now": "The City of Columbus",
   "src": "https://gastateparks.org/StandingBoyCreek",
   "why": "the park's page (data/parkinfo)"
  }
 ],
 "n": "Standing Boy Creek State Park",
 "official": {
  "acres": 1580.0,
  "as": "1,580 acre",
  "clean": false,
  "line": "Creek Standing Boy Creek Standing Boy Trails is located in the northern portion of the City of Columbus. This 1,580-acre property lies on the shore of Lake Oliver and offers excellent opportunity for hiking, running, biking, and w",
  "read": "2026-11-22",
  "sent": "This 1,580-acre property lies on the shore of Lake Oliver and offers excellent opportunity for hiking, running, biking, and wildlife viewing.",
  "url": "https://gastateparks.org/StandingBoyCreek",
  "why": "total-looking"
 },
 "ours": {
  "acres": 1580,
  "manager": "",
  "pieces": [
   [
    "sggab59",
    "Standing Boy Creek State Park",
    1580,
    "reviewed"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": "City of Columbus",
 "pct": 0,
 "same_agency": false,
 "score": 8,
 "t": "State Park",
 "verdict": "agree"
}
```

## US-3749 Flat Tub Wildlife Management Area
```json
{
 "cause": "agency smaller: our outline may hold water, a lease or a neighbour tract",
 "checked": "2026-11-22",
 "handover": [],
 "n": "Flat Tub Wildlife Management Area",
 "official": {
  "acres": 7141.0,
  "as": "7,141 acres",
  "clean": true,
  "line": "TO HUNT AND FISH FOR A LIFETIME Previous Next Flat Tub WMA The Flat Tub Wildlife Management Area encompasses 7,141 acres of state-owned land. The WMA consists of approximately 5,641 acres of upland pine/hardwood forest and 1,500 a",
  "read": "2026-11-22",
  "sent": "The Flat Tub Wildlife Management Area encompasses 7,141 acres of state-owned land.",
  "url": "https://georgiawildlife.com/flat-tub-wma",
  "why": "clean total"
 },
 "ours": {
  "acres": 8745,
  "family_fold": "layers {'sggac': 8745, 'sggaa': 7056, 'padus': 7150}: one land in 3 layers, the sggac copy used (14,206 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sggac877",
    "FLAT TUB WMA",
    8745,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 22,
 "same_agency": false,
 "score": 6,
 "t": "Wildlife Management Area",
 "verdict": "off"
}
```

## US-7140 Charlie Elliot Wildlife Management Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Charlie Elliot Wildlife Management Area",
 "official": {
  "acres": 6700.0,
  "as": "6,700 acre",
  "clean": false,
  "line": "t of the reason we are there, whether with a camera, gun, fishing rod, or pack sack on.\" -Charlie Elliott The 6,700-acre Charlie Elliott Wildlife Center, managed by the Georgia Department of Natural Resources, offers a variety of",
  "read": "2026-11-22",
  "sent": "The 6,700-acre Charlie Elliott Wildlife Center, managed by the Georgia Department of Natural Resources, offers a variety of activities and programs.",
  "url": "https://georgiawildlife.com/charlie-elliott-wildlife-center",
  "why": "total-looking"
 },
 "ours": {
  "acres": 6273,
  "manager": "",
  "pieces": [
   [
    195024,
    "Charlie Elliott Wildlife Center Clybel Wildlife Management Area Marben Public Fishing Area",
    6273,
    "reviewed"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 6,
 "same_agency": false,
 "score": 7,
 "t": "Wildlife Management Area",
 "verdict": "agree"
}
```

## US-3777 Wilson Shoals Wildlife Management Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Wilson Shoals Wildlife Management Area",
 "official": {
  "acres": 2800.0,
  "as": "2,800 acre",
  "clean": false,
  "line": "ETIME Previous Next Wilson Shoals WMA Wilson Shoals Wildlife Management Area is located in Banks County. This 2,800-acre property offers hunting opportunities for deer, bear, turkey, small game and dove. Accommodations & Facilitie",
  "read": "2026-11-22",
  "sent": "This 2,800-acre property offers hunting opportunities for deer, bear, turkey, small game and dove.",
  "url": "https://georgiawildlife.com/wilson-shoals-wma",
  "why": "total-looking"
 },
 "ours": {
  "acres": 2902,
  "dissolved": {
   "after": 2902,
   "before": 8703,
   "copies": 2,
   "parts": 0,
   "records": 3,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 8703 -> 2902 acres",
  "pieces": [
   [
    "sggaa103",
    "WILSON SHOALS WMA",
    2902,
    "reviewed"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 4,
 "same_agency": false,
 "score": 8,
 "t": "Wildlife Management Area",
 "verdict": "agree"
}
```

## US-7907 Clarks Hill Wildlife Management Area
```json
{
 "cause": "agency smaller: our outline may hold water, a lease or a neighbour tract",
 "checked": "2026-11-22",
 "handover": [
  {
   "date_hint": null,
   "kind": "managed by",
   "line": "nagement Area – East is located in McDuffie, Wilkes and Lincoln counties. This 10,224-acre property is owned by the U.S. Army Corps of Engineers and managed by the Georgia DNR-Wildlife Resources Division. It offers hunting opportunities for deer, turkey, smal",
   "owner_now": "U.S",
   "src": "https://georgiawildlife.com/clarks-hill-east",
   "why": "the park's page (data/parkinfo)"
  }
 ],
 "n": "Clarks Hill Wildlife Management Area",
 "official": {
  "acres": 10224.0,
  "as": "10,224 acre",
  "clean": false,
  "line": "ll-East Clarks Hill Wildlife Management Area – East is located in McDuffie, Wilkes and Lincoln counties. This 10,224-acre property is owned by the U.S. Army Corps of Engineers and managed by the Georgia DNR-Wildlife Resources Divis",
  "read": "2026-11-22",
  "sent": "This 10,224-acre property is owned by the U.S.",
  "url": "https://georgiawildlife.com/clarks-hill-east",
  "why": "total-looking"
 },
 "ours": {
  "acres": 17638,
  "dissolved": {
   "after": 35104,
   "before": 52583,
   "copies": 1,
   "families": {
    "padus": 17638,
    "sggac": 17466
   },
   "family_fold": 17466,
   "family_used": "padus",
   "parts": 0,
   "records": 4,
   "tracts": 3
  },
  "family_fold": "layers {'padus': 17638, 'sggac': 17466}: one land in 2 layers, the padus copy used (17,466 ac of copies not added)",
  "manager": "",
  "note": "4 joined records = 3 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 52583 -> 35104 acres",
  "pieces": [
   [
    194358,
    "Clarks Hill Wildlife Management Area",
    17638,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": "U.S",
 "pct": 73,
 "same_agency": false,
 "score": 6,
 "t": "Wildlife Management Area",
 "verdict": "off"
}
```

## US-7137 Cooper's Creek Wildlife Management Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Cooper's Creek Wildlife Management Area",
 "official": {
  "acres": 30000.0,
  "as": "30,000 acres",
  "clean": false,
  "line": "per's Creek Wildlife Management Area is one of Georgia's larger wildlife management areas. It spans more than 30,000 acres, and lies within the Chattahoochee National Forest. This WMA is located in the extreme northeast corner of Ge",
  "read": "2026-11-22",
  "sent": "It spans more than 30,000 acres, and lies within the Chattahoochee National Forest.",
  "url": "https://georgiawildlife.com/coopers-creek-wma",
  "why": "part (a lake, a purchase, a campground…)"
 },
 "ours": {
  "acres": 29653,
  "dissolved": {
   "after": 29653,
   "before": 87775,
   "copies": 2,
   "parts": 0,
   "records": 4,
   "tracts": 2
  },
  "manager": "",
  "note": "4 joined records = 2 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 87775 -> 29653 acres",
  "pieces": [
   [
    194391,
    "Coopers Creek Wildlife Management Area",
    29360,
    "name"
   ],
   [
    9156,
    "Cooper Creek Wildlife Management Area",
    293,
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
 "t": "Wildlife Management Area",
 "verdict": "agree"
}
```

## US-2194 Red Top Mountain State Park
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Red Top Mountain State Park",
 "official": {
  "acres": 1776.0,
  "as": "1,776 Acres",
  "clean": false,
  "line": "cant battlefield due to the well-preserved trenches and earthworks. Reservations, Accommodations & Facilities 1,776 Acres 12,000 Acre Lake Allatoona 20 Cottages 93 Tent, Trailer & RV Campites 6 Yurts 1 Pioneer Campground (Before ma",
  "read": "2026-11-22",
  "sent": "1,776 Acres",
  "url": "https://gastateparks.org/redtopmountain/",
  "why": "total-looking"
 },
 "ours": {
  "acres": 1643,
  "dissolved": {
   "after": 1643,
   "before": 4929,
   "copies": 2,
   "parts": 0,
   "records": 3,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 4929 -> 1643 acres",
  "pieces": [
   [
    194356,
    "Red Top Mountain State Park",
    1643,
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
 "t": "State Park",
 "verdict": "agree"
}
```
