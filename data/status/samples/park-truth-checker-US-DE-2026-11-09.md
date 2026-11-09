# park truth checker: US-DE random sample of 12 (2026-11-09; seed = date + area, same rows for everyone)

Source file: `data/truth/US-DE.json`

## US-1734 Delaware Seashore State Park
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-09",
 "n": "Delaware Seashore State Park",
 "official": null,
 "ours": {
  "acres": 1159,
  "manager": "",
  "pieces": [
   [
    "sgdea102",
    "Delaware Seashore State Park",
    1732,
    "reviewed"
   ],
   [
    "sgdea101",
    "Delaware Seashore State Park",
    208,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-0733 First State National Historical Park
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "First State National Historical Park",
 "note": "whole park compared (POTA lists it in 2 states: {'US-PA': 216, 'US-DE': 889})",
 "official": null,
 "ours": {
  "acres": 1105,
  "acres_by_state": {
   "US-DE": 889,
   "US-PA": 216
  },
  "manager": "",
  "pieces": [
   [
    3200,
    "First State National Historical Park",
    889,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "states": [
   "US-PA",
   "US-DE"
  ],
  "unknown_pieces": 0,
  "whole_park": true
 },
 "owner_now": null,
 "pct": null,
 "score": 5,
 "t": "National Historical Park",
 "verdict": "no size on page"
}
```

## US-10675 Garrisons State Fishing Lake
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-09",
 "n": "Garrisons State Fishing Lake",
 "official": null,
 "ours": {
  "acres": 119,
  "manager": "",
  "pieces": [
   [
    76219,
    "Garrisons Lake",
    91,
    "name"
   ],
   [
    57533,
    "Garrisons Lake",
    4,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 4
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "State Fishing Lake",
 "verdict": "no size on page"
}
```

## US-10689 Tussock Pond State Fishing Lake
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-09",
 "n": "Tussock Pond State Fishing Lake",
 "official": null,
 "ours": {
  "acres": 11,
  "manager": "",
  "pieces": [],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 3
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "State Fishing Lake",
 "verdict": "no size on page"
}
```

## US-10686 Portsville Pond State Fishing Lake
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-09",
 "n": "Portsville Pond State Fishing Lake",
 "official": null,
 "ours": {
  "acres": 25,
  "manager": "",
  "pieces": [],
  "pin": "just outside",
  "src": "",
  "unknown_pieces": 3
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "State Fishing Lake",
 "verdict": "no size on page"
}
```

## US-1731 Bellevue State Park
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-09",
 "n": "Bellevue State Park",
 "official": null,
 "ours": {
  "acres": 173,
  "dissolved": {
   "after": 303,
   "before": 304,
   "copies": 1,
   "families": {
    "padus": 273,
    "sgdea": 30
   },
   "family_fold": 30,
   "family_used": "padus",
   "key_union": 173,
   "parts": 0,
   "records": 5,
   "summed": 273,
   "tracts": 4
  },
  "family_fold": "layers {'padus': 273, 'sgdea': 30}: one land in 2 layers, the padus copy used (30 ac of copies not added)",
  "manager": "",
  "note": "5 joined records = 4 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 304 -> 303 acres",
  "pieces": [
   [
    76431,
    "Bellevue State Park",
    272,
    "name"
   ],
   [
    60672,
    "Bellevue State Park",
    1,
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

## US-10668 Andrews State Fishing Lake
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-09",
 "n": "Andrews State Fishing Lake",
 "official": null,
 "ours": {
  "acres": 80,
  "manager": "",
  "pieces": [
   [
    76201,
    "Andrews Lake",
    41,
    "name"
   ],
   [
    57489,
    "Andrews Lake",
    10,
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
 "t": "State Fishing Lake",
 "verdict": "no size on page"
}
```

## US-10685 Mud Mill Pond State Fishing Lake
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-09",
 "n": "Mud Mill Pond State Fishing Lake",
 "official": null,
 "ours": {
  "acres": 55,
  "manager": "",
  "pieces": [
   [
    57568,
    "Mud Mill Pond",
    4,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 2
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "State Fishing Lake",
 "verdict": "no size on page"
}
```

## US-10690 Wagamons Pond State Fishing Lake
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-09",
 "n": "Wagamons Pond State Fishing Lake",
 "official": null,
 "ours": {
  "acres": 52,
  "manager": "",
  "pieces": [
   [
    76243,
    "Wagamons Pond",
    40,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "State Fishing Lake",
 "verdict": "no size on page"
}
```

## US-1738 Fox Point State Park
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-09",
 "n": "Fox Point State Park",
 "official": null,
 "ours": {
  "acres": 151,
  "dissolved": {
   "after": 107,
   "before": 213,
   "copies": 1,
   "key_union": 151,
   "parts": 0,
   "records": 2,
   "summed": 107,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 213 -> 107 acres",
  "pieces": [
   [
    76411,
    "Fox Point State Park",
    107,
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

## US-11811 Records Pond State Fishing Lake
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-09",
 "n": "Records Pond State Fishing Lake",
 "official": null,
 "ours": {
  "acres": 73,
  "manager": "",
  "pieces": [],
  "pin": "just outside",
  "src": "",
  "unknown_pieces": 3
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "State Fishing Lake",
 "verdict": "ours unknown"
}
```

## US-9891 Blackbird Creek National Reserve
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-11-09",
 "handover": [],
 "n": "Blackbird Creek National Reserve",
 "official": null,
 "ours": {
  "acres": 817,
  "dissolved": {
   "after": 522,
   "before": 1632,
   "copies": 1,
   "key_union": 817,
   "parts": 11,
   "records": 14,
   "summed": 522,
   "tracts": 2
  },
  "manager": "",
  "note": "14 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 11 fee tracts under a designation record folded; summed 1632 -> 522 acres",
  "pieces": [
   [
    76054,
    "DNERR Blackbird Creek Reserve",
    520,
    "reviewed"
   ],
   [
    52024,
    "DE National Estuarine Research Reserve Blackbird Creek Reserve",
    2,
    "reviewed"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 3
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "National Reserve",
 "verdict": "unsure"
}
```
