# park truth checker: US-ME random sample of 12 (2026-11-22; seed = date + area, same rows for everyone)

Source file: `data/truth/US-ME.json`

## US-8444 Moxie Falls Property State Preserve
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Moxie Falls Property State Preserve",
 "official": null,
 "ours": {
  "acres": 229,
  "manager": "",
  "pieces": [
   [
    207472,
    "Moxie Falls",
    229,
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
 "t": "State Preserve",
 "verdict": "no size on page"
}
```

## US-11808 Saint Croix Island International Historic Site
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Saint Croix Island International Historic Site",
 "official": null,
 "ours": {
  "acres": 7,
  "manager": "",
  "pieces": [
   [
    3092,
    "Saint Croix Island International Historic Site",
    7,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 4,
 "t": "Historic Site",
 "verdict": "no size on page"
}
```

## US-8474 Chesterville Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Chesterville Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 2033,
  "dissolved": {
   "after": 1902,
   "before": 3588,
   "copies": 0,
   "families": {
    "padus": 757,
    "sgmeb": 1145
   },
   "family_fold": 757,
   "family_used": "sgmeb",
   "key_union": 2033,
   "parts": 8,
   "records": 13,
   "summed": 1145,
   "tracts": 5
  },
  "family_fold": "layers {'sgmeb': 1145, 'padus': 757}: one land in 2 layers, the sgmeb copy used (757 ac of copies not added)",
  "manager": "",
  "note": "13 joined records = 5 tracts: 0 copies of a tract (same acres, another layer) and 8 fee tracts under a designation record folded; summed 3588 -> 1902 acres",
  "pieces": [
   [
    "sgmeb10",
    "Chesterville WMA",
    1145,
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

## US-8488 Pond Farm Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Pond Farm Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 318,
  "dissolved": {
   "after": 318,
   "before": 636,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 636 -> 318 acres",
  "pieces": [
   [
    206245,
    "Pond Farm Wildlife Management Area",
    318,
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
 "t": "Wildlife Management Area",
 "verdict": "no size on page"
}
```

## US-8465 St. Albans Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "St. Albans Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 417,
  "dissolved": {
   "after": 417,
   "before": 834,
   "copies": 0,
   "parts": 4,
   "records": 5,
   "tracts": 1
  },
  "manager": "",
  "note": "5 joined records = 1 tracts: 0 copies of a tract (same acres, another layer) and 4 fee tracts under a designation record folded; summed 834 -> 417 acres",
  "pieces": [
   [
    "sgmeb59",
    "St. Albans WMA",
    417,
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

## US-0342 Pond Island National Wildlife Refuge
```json
{
 "cause": "agency smaller: our outline may hold water, a lease or a neighbour tract",
 "checked": "2026-11-22",
 "handover": [
  {
   "date_hint": "1973",
   "kind": "transfer",
   "line": "t Guard automated the station and removed the buildings leaving only the lighthouse. The island was transferred from the Coast Guard to the Fish and Wildlife Service in 1973 establishing Pond Island National Wildlife Refuge. Pond Island National Wildlife Refuge is a 10-acre island in the mouth of th",
   "owner_now": "Coast Guard",
   "src": "https://www.fws.gov/refuge/pond-island/about-us",
   "why": "FWS refuge about page"
  }
 ],
 "n": "Pond Island National Wildlife Refuge",
 "official": {
  "acres": 10.0,
  "as": "10 acre",
  "clean": true,
  "line": "About Us What We Do Contact Us Visit Us Locations News Species Map Pond Island National Wildlife Refuge is a 10-acre island in the mouth of the Kennebec River adjacent to Popham Beach. The refuge was created to safeguard and e",
  "read": "2026-11-22",
  "sent": "Pond Island National Wildlife Refuge is a 10-acre island in the mouth of the Kennebec River adjacent to Popham Beach.",
  "url": "https://www.fws.gov/refuge/pond-island",
  "why": "clean total"
 },
 "ours": {
  "acres": 51,
  "manager": "",
  "pieces": [
   [
    60782,
    "Island",
    67,
    "name"
   ],
   [
    4239,
    "Pond Island National Wildlife Refuge",
    17,
    "name"
   ],
   [
    5197,
    "Pond Island National Wildlife Refuge",
    17,
    "name"
   ],
   [
    207147,
    "Island",
    1,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": "Coast Guard",
 "pct": 410,
 "same_agency": false,
 "score": 5,
 "t": "National Wildlife Refuge",
 "verdict": "off"
}
```

## US-7981 Whaleback Shell Midden State Historic Site
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Whaleback Shell Midden State Historic Site",
 "official": null,
 "ours": {
  "acres": 6,
  "manager": "",
  "pieces": [
   [
    207503,
    "Whaleback Shell Midden",
    6,
    "name (designation code ignored)"
   ],
   [
    207235,
    "Whaleback Shell Midden",
    3,
    "name"
   ],
   [
    207414,
    "Whaleback Shell Midden",
    1,
    "name (designation code ignored)"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 2
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "State Historic Site",
 "verdict": "no size on page"
}
```

## US-8452 Vernon S Walker Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Vernon S Walker Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 5849,
  "dissolved": {
   "after": 9949,
   "before": 15135,
   "copies": 1,
   "families": {
    "padus": 4100,
    "sgmeb": 5849
   },
   "family_fold": 4100,
   "family_used": "sgmeb",
   "parts": 30,
   "records": 39,
   "tracts": 8
  },
  "family_fold": "layers {'sgmeb': 5849, 'padus': 4100}: one land in 2 layers, the sgmeb copy used (4,100 ac of copies not added)",
  "manager": "",
  "note": "39 joined records = 8 tracts: 1 copies of a tract (same acres, another layer) and 30 fee tracts under a designation record folded; summed 15135 -> 9949 acres",
  "pieces": [
   [
    "sgmeb66",
    "Vernon S. Walker WMA",
    5849,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": null,
 "score": 5,
 "t": "Wildlife Management Area",
 "verdict": "no size on page"
}
```

## US-7982 Fort Halifax State Historic Site
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Fort Halifax State Historic Site",
 "official": null,
 "ours": {
  "acres": 0,
  "manager": "",
  "pieces": [],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": null,
 "score": 5,
 "t": "State Historic Site",
 "verdict": "ours unknown"
}
```

## US-8484 Booming Ground Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Booming Ground Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 593,
  "family_fold": "layers {'sgmeb': 593, 'padus': 575}: one land in 2 layers, the sgmeb copy used (575 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgmeb5",
    "Booming Ground WMA",
    593,
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
 "t": "Wildlife Management Area",
 "verdict": "no size on page"
}
```

## US-8490 Pollard Flat Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Pollard Flat Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 520,
  "family_fold": "layers {'padus': 520, 'sgmeb': 243}: one land in 2 layers, the padus copy used (243 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    206244,
    "Pollard Flat Wildlife Management Area",
    283,
    "name"
   ],
   [
    206243,
    "Pollard Flat Wildlife Management Area",
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
 "score": 6,
 "t": "Wildlife Management Area",
 "verdict": "no size on page"
}
```

## US-8291 Fort Knox State Historic Site
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Fort Knox State Historic Site",
 "official": null,
 "ours": {
  "acres": 124,
  "manager": "",
  "pieces": [
   [
    206996,
    "Fort Knox State Historic Site",
    124,
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
 "t": "State Historic Site",
 "verdict": "no size on page"
}
```
