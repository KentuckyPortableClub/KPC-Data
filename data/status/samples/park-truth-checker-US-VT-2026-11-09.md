# park truth checker: US-VT random sample of 12 (2026-11-09; seed = date + area, same rows for everyone)

Source file: `data/truth/US-VT.json`

## US-3153 Woods Island State Park
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Woods Island State Park",
 "official": {
  "acres": 125.0,
  "as": "125 acres",
  "clean": false,
  "line": "Island became Vermont's forty-fifth state park in 1985. It is one mile long and a quarter-mile wide covering 125 acres. Woods Island is home to many kinds of plants, including some that are rare or threatened in Vermont. Part of",
  "read": "2026-11-09",
  "sent": "It is one mile long and a quarter-mile wide covering 125 acres.",
  "url": "https://vtstateparks.com/woodsisland.html",
  "why": "total-looking"
 },
 "ours": {
  "acres": 109,
  "dissolved": {
   "after": 109,
   "before": 218,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 218 -> 109 acres",
  "pieces": [
   [
    61171,
    "Woods Island State Park",
    109,
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
 "t": "State Park",
 "verdict": "agree"
}
```

## US-4588 Taconic Mountains Ramble State Park
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Taconic Mountains Ramble State Park",
 "official": {
  "acres": 204.0,
  "as": "204 acres",
  "clean": false,
  "line": "e park. Please clean up after your pet. 2 Photo Gallery Welcome The Carson Davidson Revocable Trust Fund gave 204 acres in Hubbardton to the Vermont Department of Forests, Parks, and Recreation, creating Taconic Mountains Ramble",
  "read": "2026-11-09",
  "sent": "The Carson Davidson Revocable Trust Fund gave 204 acres in Hubbardton to the Vermont Department of Forests, Parks, and Recreation, creating Taconic Mountains Ramble State Park.",
  "url": "https://vtstateparks.com/taconic.html",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 194,
  "manager": "",
  "pieces": [
   [
    61167,
    "Taconic Mountains Ramble",
    419,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 5,
 "same_agency": false,
 "score": 6,
 "t": "State Park",
 "verdict": "agree"
}
```

## US-5553 Camels Hump State Forest
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-11-09",
 "handover": [],
 "n": "Camels Hump State Forest",
 "official": null,
 "ours": {
  "acres": 2598,
  "dissolved": {
   "after": 2365,
   "before": 4728,
   "copies": 0,
   "key_union": 2598,
   "parts": 7,
   "records": 8,
   "summed": 2365,
   "tracts": 1
  },
  "manager": "",
  "note": "8 joined records = 1 tracts: 0 copies of a tract (same acres, another layer) and 7 fee tracts under a designation record folded; summed 4728 -> 2365 acres",
  "pieces": [
   [
    "sgvta5",
    "Camel's Hump State Forest",
    2365,
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
 "t": "State Forest",
 "verdict": "unsure"
}
```

## US-5550 Boyer State Forest
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Boyer State Forest",
 "official": {
  "acres": 354.6,
  "as": "354.6 Acres",
  "clean": false,
  "line": "e Parks Recreation State Lands Agency Home Project Learning Tree Boyer State Forest Berlin, Washington County 354.6 Acres General Description: Boyer State Forest is located on Crosstown Road in Berlin, Vermont. It ranges in elevati",
  "read": "2026-11-09",
  "sent": "354.6 Acres",
  "url": "https://fpr.vermont.gov/boyer-state-forest",
  "why": "total-looking"
 },
 "ours": {
  "acres": 310,
  "dissolved": {
   "after": 364,
   "before": 728,
   "copies": 0,
   "key_union": 310,
   "parts": 3,
   "records": 4,
   "summed": 364,
   "tracts": 1
  },
  "manager": "",
  "note": "4 joined records = 1 tracts: 0 copies of a tract (same acres, another layer) and 3 fee tracts under a designation record folded; summed 728 -> 364 acres",
  "pieces": [
   [
    "sgvta42",
    "Boyer State Forest",
    364,
    "reviewed"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 13,
 "same_agency": false,
 "score": 7,
 "t": "State Forest",
 "verdict": "agree"
}
```

## US-3107 Camels Hump State Park
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-11-09",
 "handover": [],
 "n": "Camels Hump State Park",
 "official": null,
 "ours": {
  "acres": 24425,
  "dissolved": {
   "after": 27463,
   "before": 42477,
   "copies": 3,
   "families": {
    "padus": 4312,
    "sgvta": 23151
   },
   "family_fold": 4312,
   "family_used": "sgvta",
   "key_union": 24425,
   "parts": 48,
   "records": 54,
   "summed": 23151,
   "tracts": 3
  },
  "family_fold": "layers {'sgvta': 23151, 'padus': 4312}: one land in 2 layers, the sgvta copy used (4,312 ac of copies not added)",
  "manager": "",
  "note": "54 joined records = 3 tracts: 3 copies of a tract (same acres, another layer) and 48 fee tracts under a designation record folded; summed 42477 -> 27463 acres",
  "pieces": [
   [
    "sgvta437",
    "Camel's Hump State Park",
    23151,
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
 "verdict": "unsure"
}
```

## US-0574 Missisquoi National Wildlife Refuge
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Missisquoi National Wildlife Refuge",
 "official": {
  "acres": 6729.0,
  "as": "6,729 acres",
  "clean": false,
  "line": "squoi National Wildlife Refuge was established in 1943 to provide habitat for migratory birds. It consists of 6,729 acres, mostly wetland habitats, which support a variety of migratory birds and other wildlife. Learn More About Us",
  "read": "2026-11-09",
  "sent": "It consists of 6,729 acres, mostly wetland habitats, which support a variety of migratory birds and other wildlife.",
  "url": "https://www.fws.gov/refuge/missisquoi",
  "why": "total-looking"
 },
 "ours": {
  "acres": 6660,
  "dissolved": {
   "after": 7292,
   "before": 14571,
   "copies": 1,
   "key_union": 6660,
   "parts": 0,
   "records": 2,
   "summed": 7292,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 14571 -> 7292 acres",
  "pieces": [
   [
    5080,
    "Missisquoi National Wildlife Refuge",
    7292,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 1,
 "same_agency": false,
 "score": 7,
 "t": "National Wildlife Refuge",
 "verdict": "agree"
}
```

## US-3114 Fort Dummer State Park
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Fort Dummer State Park",
 "official": {
  "acres": 217.0,
  "as": "217 acres",
  "clean": true,
  "line": "on the Sunset Trail Fort Dummer State Park, in the Connecticut River Valley just outside Brattleboro, covers 217 acres of forested land. The park is named for Fort Dummer, Vermont’s first permanent European settlement. Built in",
  "read": "2026-11-09",
  "sent": "Fort Dummer State Park, in the Connecticut River Valley just outside Brattleboro, covers 217 acres of forested land.",
  "url": "https://vtstateparks.com/fortdummer.html",
  "why": "clean total"
 },
 "ours": {
  "acres": 200,
  "dissolved": {
   "after": 269,
   "before": 536,
   "copies": 0,
   "key_union": 200,
   "parts": 5,
   "records": 7,
   "summed": 269,
   "tracts": 2
  },
  "manager": "",
  "note": "7 joined records = 2 tracts: 0 copies of a tract (same acres, another layer) and 5 fee tracts under a designation record folded; summed 536 -> 269 acres",
  "pieces": [
   [
    "sgvta448",
    "Fort Dummer State Park",
    268,
    "reviewed"
   ],
   [
    61093,
    "Fort Dummer State Park",
    1,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 8,
 "same_agency": false,
 "score": 8,
 "t": "State Park",
 "verdict": "agree"
}
```

## US-4590 Muckross State Park
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 1,000 acres, no total words near it)",
 "checked": "2026-11-09",
 "handover": [],
 "n": "Muckross State Park",
 "official": {
  "acres": 1000.0,
  "as": "1,000 acres",
  "clean": false,
  "line": "ate built in the early 1900s by W.D. Woolson, a local industrialist. At that time, the estate included nearly 1,000 acres, two trout ponds, and many buildings, such as a main lodge and cottages. The park may be named after Muckross",
  "read": "2026-11-09",
  "sent": "At that time, the estate included nearly 1,000 acres, two trout ponds, and many buildings, such as a main lodge and cottages.",
  "url": "https://vtstateparks.com/muckross.html",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 89,
  "dissolved": {
   "after": 204,
   "before": 408,
   "copies": 1,
   "key_union": 89,
   "parts": 0,
   "records": 2,
   "summed": 204,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 408 -> 204 acres",
  "pieces": [
   [
    61142,
    "Muckross",
    204,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 91,
 "same_agency": false,
 "score": 6,
 "t": "State Park",
 "verdict": "unsure"
}
```

## US-3152 Woodford State Park
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-09",
 "handover": [],
 "n": "Woodford State Park",
 "official": {
  "acres": 398.0,
  "as": "398 acre",
  "clean": false,
  "line": "feet this map is intended for informational purposes only Cabin Prime lean-to Woodford State Park Welcome to 398-acre Woodford State Park. At 2,400 feet in elevation Woodford is the highest state park in Vermont. Located on",
  "read": "2026-11-09",
  "sent": "Welcome to 398-acre Woodford State Park.",
  "url": "https://www.vtstateparks.com/sites/stateparks/files/documents/Woodford%20Map%20Guide.pdf",
  "why": "total-looking"
 },
 "ours": {
  "acres": 272,
  "dissolved": {
   "after": 395,
   "before": 790,
   "copies": 1,
   "key_union": 272,
   "parts": 0,
   "records": 2,
   "summed": 395,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 790 -> 395 acres",
  "pieces": [
   [
    61170,
    "Woodford State Park",
    395,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 32,
 "same_agency": false,
 "score": 6,
 "t": "State Park",
 "verdict": "off"
}
```

## US-3103 Branbury State Park
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-11-09",
 "handover": [],
 "n": "Branbury State Park",
 "official": null,
 "ours": {
  "acres": 47,
  "dissolved": {
   "after": 66,
   "before": 132,
   "copies": 0,
   "key_union": 47,
   "parts": 2,
   "records": 3,
   "summed": 66,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 0 copies of a tract (same acres, another layer) and 2 fee tracts under a designation record folded; summed 132 -> 66 acres",
  "pieces": [
   [
    "sgvta436",
    "Branbury State Park",
    66,
    "reviewed"
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
 "verdict": "unsure"
}
```

## US-3119 Hazens Notch State Park
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Hazens Notch State Park",
 "official": {
  "acres": 307.0,
  "as": "307 Acres",
  "clean": false,
  "line": "s Recreation State Lands Agency Home Project Learning Tree Hazen's Notch State Park Westfield, Orleans County 307 Acres General Description: Initial acquisitions of property to become Hazen’s Notch State Park took place in 1934 a",
  "read": "2026-11-09",
  "sent": "307 Acres",
  "url": "https://fpr.vermont.gov/hazens-notch-state-park",
  "why": "total-looking"
 },
 "ours": {
  "acres": 294,
  "family_fold": "layers {'sgvta': 422, 'padus': 419}: one land in 2 layers, the sgvta copy used (419 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgvta468",
    "Hazens Notch State Park",
    422,
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
 "t": "State Park",
 "verdict": "agree"
}
```

## US-3104 Brighton State Park
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Brighton State Park",
 "official": null,
 "ours": {
  "acres": 319,
  "family_fold": "layers {'sgvta': 631, 'padus': 156}: one land in 2 layers, the sgvta copy used (156 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgvta441",
    "Brighton State Park",
    631,
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
