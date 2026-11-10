# park truth checker: US-HI random sample of 12 (2026-11-10; seed = date + area, same rows for everyone)

Source file: `data/truth/US-HI.json`

## US-2211 Heeia State Park
```json
{
 "checked": "2026-11-10",
 "handover": [],
 "n": "Heeia State Park",
 "official": null,
 "ours": {
  "acres": 16,
  "dissolved": {
   "after": 31,
   "before": 67,
   "copies": 2,
   "families": {
    "padus": 13,
    "sghia": 18
   },
   "family_fold": 13,
   "family_used": "sghia",
   "key_union": 16,
   "parts": 0,
   "records": 4,
   "summed": 18,
   "tracts": 2
  },
  "family_fold": "layers {'sghia': 18, 'padus': 13}: one land in 2 layers, the sghia copy used (13 ac of copies not added)",
  "manager": "",
  "note": "4 joined records = 2 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 67 -> 31 acres",
  "pieces": [
   [
    "sghia8",
    "HEEIA STATE PARK",
    18,
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
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-2210 Ha'ena State Park
```json
{
 "checked": "2026-11-10",
 "handover": [],
 "n": "Ha'ena State Park",
 "official": null,
 "ours": {
  "acres": 296,
  "dissolved": {
   "after": 236,
   "before": 944,
   "copies": 4,
   "key_union": 296,
   "parts": 2,
   "records": 7,
   "summed": 236,
   "tracts": 1
  },
  "manager": "",
  "note": "7 joined records = 1 tracts: 4 copies of a tract (same acres, another layer) and 2 fee tracts under a designation record folded; summed 944 -> 236 acres",
  "pieces": [
   [
    195375,
    "Ha'ena State Park",
    236,
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

## US-0124 James Campbell National Wildlife Refuge
```json
{
 "checked": "2026-11-10",
 "handover": [
  {
   "date_hint": null,
   "kind": "managed by",
   "line": "ut Us View Our Tours What We Do The National Wildlife Refuge System is a series of lands and waters owned and managed by the U.S. Fish and Wildlife Service. Wildlife conservation is at the heart of the refuge system. It drives everything we do from the purpose a refuge is establis",
   "owner_now": "U.S",
   "src": "https://www.fws.gov/refuge/james_campbell/",
   "why": "the park's page (data/parkinfo)"
  }
 ],
 "n": "James Campbell National Wildlife Refuge",
 "official": {
  "acres": 1100.0,
  "as": "1,100 acres",
  "clean": false,
  "line": "h the Estate of James Campbell. By 2005, Public Law 109-225 authorized expansion of the James Campbell NWR by 1,100 acres and identified management focus areas for the Refuge expansion lands. Other Facilities in this Complex James",
  "read": "2026-11-10",
  "sent": "By 2005, Public Law 109-225 authorized expansion of the James Campbell NWR by 1,100 acres and identified management focus areas for the Refuge expansion lands.",
  "url": "https://www.fws.gov/refuge/james-campbell/about-us",
  "why": "history"
 },
 "ours": {
  "acres": 1070,
  "dissolved": {
   "after": 1070,
   "before": 3208,
   "copies": 2,
   "parts": 0,
   "records": 3,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 3208 -> 1070 acres",
  "pieces": [
   [
    "sghib318",
    "JAMES CAMPBELL NATIONAL WILDLIFE REFUGE",
    1070,
    "reviewed"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": "U.S",
 "pct": 3,
 "same_agency": false,
 "score": 8,
 "t": "National Wildlife Refuge",
 "verdict": "agree"
}
```

## US-6421 Kohala Historical Sites State Preserve
```json
{
 "checked": "2026-11-10",
 "handover": [],
 "n": "Kohala Historical Sites State Preserve",
 "official": {
  "acres": 6.7,
  "as": "6.7 acres",
  "clean": false,
  "line": ". The birthsite is a memorial to Hawaiʻi’s greatest king who united all the island chiefdoms into a kingdom. (6.7 acres) Malama Hawaii-Culture from Hawaii DLNR on Vimeo . Activities Facilities Hazards Prohibited Park Rules Area W",
  "read": "2026-11-10",
  "sent": "(6.7 acres)",
  "url": "https://dlnr.hawaii.gov/dsp/parks/hawaii/kohala-historical-sites-state-monument/",
  "why": "total-looking"
 },
 "ours": {
  "acres": 7,
  "manager": "",
  "pieces": [
   [
    195367,
    "Kohala Historical Sites State Monument",
    7,
    "reviewed"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 4,
 "same_agency": false,
 "score": 6,
 "t": "State Preserve",
 "verdict": "agree"
}
```

## US-2220 Polihale State Park
```json
{
 "checked": "2026-11-10",
 "handover": [],
 "n": "Polihale State Park",
 "official": null,
 "ours": {
  "acres": 87,
  "dissolved": {
   "after": 148,
   "before": 592,
   "copies": 3,
   "key_union": 87,
   "parts": 0,
   "records": 4,
   "summed": 148,
   "tracts": 1
  },
  "manager": "",
  "note": "4 joined records = 1 tracts: 3 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 592 -> 148 acres",
  "pieces": [
   [
    195400,
    "Polihale State Park",
    148,
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

## US-2216 Makapuʻu  Point Wayside State Trail
```json
{
 "checked": "2026-11-10",
 "handover": [],
 "n": "Makapuʻu  Point Wayside State Trail",
 "official": null,
 "ours": {
  "acres": 39,
  "manager": "",
  "pieces": [
   [
    195390,
    "Makapuu Point State Wayside",
    39,
    "reviewed"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 4,
 "t": "State Trail",
 "verdict": "no size on page"
}
```

## US-0037 Hawai'i Volcanoes National Park
```json
{
 "checked": "2026-11-10",
 "handover": [
  {
   "date_hint": null,
   "kind": "managed by",
   "line": "lcanism, rich Hawaiian traditions, and a fascinating history of ranching. Park Store The park store is operated by Hawaiʻi Pacific Parks Association, which supports park programs and projects Last updated: December 8, 2025 Basic Information Learn A",
   "owner_now": "Hawaiʻi Pacific Parks Association",
   "src": "https://www.nps.gov/havo/index.htm",
   "why": "the park's page (data/parkinfo)"
  },
  {
   "date_hint": null,
   "kind": "managed by",
   "line": "c data Management Park planning, laws and policies, management documents. Park Store The park store is operated by Hawaiʻi Pacific Parks Association, which supports park programs and projects Last updated: March 20, 2024 Park footer Contact Info Ma",
   "owner_now": "Hawaiʻi Pacific Parks Association",
   "src": "https://www.nps.gov/havo/learn/index.htm",
   "why": "about / history page of the park's site"
  }
 ],
 "n": "Hawai'i Volcanoes National Park",
 "official": null,
 "ours": {
  "acres": 389611,
  "dissolved": {
   "after": 389611,
   "before": 768335,
   "copies": 1,
   "parts": 0,
   "records": 5,
   "tracts": 4
  },
  "manager": "",
  "note": "5 joined records = 4 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 768335 -> 389611 acres",
  "pieces": [
   [
    "sghib328",
    "HAWAII VOLCANOES NATIONAL PARK",
    379701,
    "name"
   ],
   [
    "sghib134",
    "HAWAII VOLCANOES NATIONAL PARK",
    9706,
    "name"
   ],
   [
    "sghib339",
    "HAWAII VOLCANOES NATIONAL PARK",
    145,
    "name"
   ],
   [
    "sghib340",
    "HAWAII VOLCANOES NATIONAL PARK",
    59,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": "Hawaiʻi Pacific Parks Association",
 "pct": null,
 "score": 7,
 "t": "National Park",
 "verdict": "no size on page"
}
```

## US-0036 Haleakala National Park
```json
{
 "checked": "2026-11-10",
 "handover": [],
 "n": "Haleakala National Park",
 "official": null,
 "ours": {
  "acres": 33915,
  "dissolved": {
   "after": 33915,
   "before": 67727,
   "copies": 1,
   "parts": 0,
   "records": 4,
   "tracts": 3
  },
  "manager": "",
  "note": "4 joined records = 3 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 67727 -> 33915 acres",
  "pieces": [
   [
    "sghib78",
    "HALEAKALA NATIONAL PARK",
    33892,
    "reviewed"
   ],
   [
    "sghib189",
    "HALEAKALA NATIONAL PARK",
    17,
    "name"
   ],
   [
    "sghib190",
    "HALEAKALA NATIONAL PARK",
    6,
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
 "t": "National Park",
 "verdict": "no size on page"
}
```

## US-10904 ʻEwa Forest Reserve
```json
{
 "checked": "2026-11-10",
 "handover": [],
 "n": "ʻEwa Forest Reserve",
 "official": null,
 "ours": {
  "acres": 8340,
  "dissolved": {
   "after": 10588,
   "before": 13358,
   "copies": 1,
   "families": {
    "padus": 2770,
    "sghib": 7818
   },
   "family_fold": 2770,
   "family_used": "sghib",
   "key_union": 8340,
   "parts": 0,
   "records": 5,
   "summed": 7818,
   "tracts": 4
  },
  "family_fold": "layers {'sghib': 7818, 'padus': 2770}: one land in 2 layers, the sghib copy used (2,770 ac of copies not added)",
  "manager": "",
  "note": "5 joined records = 4 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 13358 -> 10588 acres",
  "pieces": [
   [
    "sghib19",
    "EWA FOREST RESERVE (POAMOHO SEC.)",
    4623,
    "name"
   ],
   [
    "sghib25",
    "EWA FOREST RESERVE (WAIMANO SEC.)",
    2549,
    "reviewed"
   ],
   [
    "sghib242",
    "EWA FOREST RESERVE (KALAUAO SEC)",
    646,
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
 "t": "Forest Reserve",
 "verdict": "no size on page"
}
```

## US-10907 Mokuleia Forest Reserve
```json
{
 "checked": "2026-11-10",
 "handover": [],
 "n": "Mokuleia Forest Reserve",
 "official": null,
 "ours": {
  "acres": 3656,
  "family_fold": "layers {'padus': 2960, 'sghib': 3377}: one land in 2 layers, the sghib copy used (2,960 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sghib253",
    "MOKULEIA FOREST RESERVE",
    2813,
    "reviewed"
   ],
   [
    "sghib17",
    "MOKULEIA FOREST RESERVE",
    564,
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
 "t": "Forest Reserve",
 "verdict": "no size on page"
}
```

## US-2213 Kaumahina Wayside State Park
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 7.8 acres, no total words near it)",
 "checked": "2026-11-10",
 "handover": [],
 "n": "Kaumahina Wayside State Park",
 "official": {
  "acres": 7.8,
  "as": "7.8 acres",
  "clean": false,
  "line": "est stop with exotic plants. Picnicking and scenic viewpoint of northeast Maui coastline. No drinking water. (7.8 acres) Activities Facilities Hazards Prohibited Park Rules Area Weather Forecast ABOUT US Contact Us Partners Broch",
  "read": "2026-11-10",
  "sent": "(7.8 acres)",
  "url": "https://dlnr.hawaii.gov/dsp/parks/maui/kaumahina-state-wayside/",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 5,
  "dissolved": {
   "after": 7,
   "before": 21,
   "copies": 2,
   "key_union": 5,
   "parts": 0,
   "records": 3,
   "summed": 7,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 21 -> 7 acres",
  "pieces": [
   [
    195382,
    "Kaumahina State Wayside",
    7,
    "words"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 36,
 "same_agency": false,
 "score": 6,
 "t": "State Park",
 "verdict": "unsure"
}
```

## US-6420 Kiholo  Reserve State Reserve
```json
{
 "checked": "2026-11-10",
 "handover": [],
 "n": "Kiholo  Reserve State Reserve",
 "official": null,
 "ours": {
  "acres": 4214,
  "dissolved": {
   "after": 3,
   "before": 9,
   "copies": 2,
   "key_union": 4214,
   "parts": 0,
   "records": 3,
   "summed": 3,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 9 -> 3 acres",
  "pieces": [
   [
    "sghia65",
    "KIHOLO STATE PARK RESERVE",
    3,
    "reviewed"
   ]
  ],
  "pin": "just outside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "State Reserve",
 "verdict": "no size on page"
}
```
