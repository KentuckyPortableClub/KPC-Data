# park truth checker: US-CO random sample of 12 (2026-11-01; seed = date + area, same rows for everyone)

Source file: `data/truth/US-CO.json`

## US-11887 Sewemup Mesa BLM Wilderness Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Sewemup Mesa BLM Wilderness Area",
 "official": {
  "acres": 19656.0,
  "as": "19,656 acres",
  "clean": true,
  "line": "located in Mesa and Montrose counties, approximately 11 miles south of Gateway. Visitor Advisory Total Area: 19,656 acres Elevation Range: ~5,741 to ~6,562 feet BLM Field Office: Grand Junction and Uncompahgre Designated: 1980 (Wil",
  "read": "2026-11-01",
  "sent": "Total Area: 19,656 acres",
  "url": "https://www.blm.gov/site-page/programs-national-conservation-lands-colorado-sewemup-wsa",
  "why": "clean total"
 },
 "ours": {
  "acres": 0,
  "manager": "",
  "pieces": [],
  "pin": "just outside",
  "src": "",
  "unknown_pieces": 2
 },
 "owner_now": null,
 "pct": null,
 "same_agency": false,
 "score": 6,
 "t": "BLM Wilderness Area",
 "verdict": "ours unknown"
}
```

## US-12186 Bob Terrell State Wildlife Area
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 7 acres, no total words near it)",
 "checked": "2026-11-01",
 "handover": [],
 "n": "Bob Terrell State Wildlife Area",
 "official": {
  "acres": 7.0,
  "as": "7 acres",
  "clean": false,
  "line": "d check current hunting, fishing and land use regulations when planning to visit a State Wildlife Area. Acres 7 acres. Elevation 5,884 to 6,121 GMU 43 Hunting Opportunities No hunting opportunities available Fishing Opportuniti",
  "read": "2026-11-01",
  "sent": "7 acres.",
  "url": "https://cpw.state.co.us/state-wildlife-areas/bob-terrell-swa",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 9,
  "dissolved": {
   "after": 9,
   "before": 25,
   "copies": 3,
   "parts": 0,
   "records": 5,
   "tracts": 2
  },
  "manager": "",
  "note": "5 joined records = 2 tracts: 3 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 25 -> 9 acres",
  "pieces": [
   [
    "cow139",
    "Bob Terrell SWA",
    7,
    "name"
   ],
   [
    "cow138",
    "Bob Terrell SWA",
    2,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 29,
 "same_agency": false,
 "score": 7,
 "t": "State Wildlife Area",
 "verdict": "unsure"
}
```

## US-11884 The Palisade BLM Wilderness Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "The Palisade BLM Wilderness Area",
 "official": {
  "acres": 26766.0,
  "as": "26,766 acres",
  "clean": true,
  "line": "no developed trail systems; recreation requires the aid of detailed maps and backcountry skills. Total Area: 26,766 acres Elevation Range: ~4,600 to ~9,450 feet BLM Field Office: Grand Junction Designated: 1980 (Wilderness Study Ar",
  "read": "2026-11-01",
  "sent": "Total Area: 26,766 acres",
  "url": "https://www.blm.gov/site-page/programs-national-conservation-lands-colorado-palisade-wsa",
  "why": "clean total"
 },
 "ours": {
  "acres": 0,
  "manager": "",
  "pieces": [],
  "pin": "just outside",
  "src": "",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": null,
 "same_agency": false,
 "score": 6,
 "t": "BLM Wilderness Area",
 "verdict": "ours unknown"
}
```

## US-0921 Dinosaur National Monument
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Dinosaur National Monument",
 "note": "whole park compared (POTA lists it in 2 states: {'US-UT': 52673, 'US-CO': 150749})",
 "official": {
  "acres": 205672.0,
  "as": "205,672 acres",
  "clean": false,
  "line": "added to the National Wilderness Preservation System May 11, 1978 – An enlarged wilderness recommendation for 205,672 acres is sent to Congress, and becomes Dinosaur’s official Recommended Wilderness October 4, 2011 - The Quarry Exhi",
  "read": "2026-11-01",
  "sent": "May 11, 1978 – An enlarged wilderness recommendation for 205,672 acres is sent to Congress, and becomes Dinosaur’s official Recommended Wilderness",
  "url": "https://www.nps.gov/dino/learn/management/statistics.htm",
  "why": "total-looking"
 },
 "ours": {
  "acres": 203422,
  "acres_by_state": {
   "US-CO": 150749,
   "US-UT": 52673
  },
  "manager": "",
  "pieces": [
   [
    3361,
    "Dinosaur National Monument",
    150671,
    "name"
   ],
   [
    189426,
    "Dinosaur National Monument",
    78,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "states": [
   "US-UT",
   "US-CO"
  ],
  "unknown_pieces": 0,
  "whole_park": true
 },
 "owner_now": null,
 "pct": 1,
 "same_agency": false,
 "score": 7,
 "t": "National Monument",
 "verdict": "agree"
}
```

## US-0184 Ramah State Wildlife Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Ramah State Wildlife Area",
 "official": {
  "acres": 400.0,
  "as": "400 acres",
  "clean": false,
  "line": "chThreshold\" : 5, \"useCSS\" : true, \"useTransform\" : true, \"centerPadding\":\"0px\", \"infinite\" : false }'> Acres 400 acres. Elevation min. 6,156 ft - max 6,228 ft GMU 110 Hunting Opportunities Deer, Small game, Waterfowl Fishing Opp",
  "read": "2026-11-01",
  "sent": "400 acres.",
  "url": "https://cpw.state.co.us/state-wildlife-areas/ramah-swa",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 399,
  "dissolved": {
   "after": 399,
   "before": 1596,
   "copies": 3,
   "parts": 0,
   "records": 4,
   "tracts": 1
  },
  "manager": "",
  "note": "4 joined records = 1 tracts: 3 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1596 -> 399 acres",
  "pieces": [
   [
    188949,
    "Ramah Reservoir State Wildlife Area",
    399,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 0,
 "same_agency": false,
 "score": 8,
 "t": "State Wildlife Area",
 "verdict": "agree"
}
```

## US-11898 Adobe Badlands BLM Wilderness Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Adobe Badlands BLM Wilderness Area",
 "official": {
  "acres": 38000000.0,
  "as": "38 million acres",
  "clean": false,
  "line": "research grounds, and outstanding ecological and cultural resources. These areas are diverse--made up of over 38 million acres of National Monuments, National Conservation Areas, Wilderness Areas, Wilderness Study Areas, Wild and Scenic",
  "read": "2026-11-01",
  "sent": "These areas are diverse--made up of over 38 million acres of National Monuments, National Conservation Areas, Wilderness Areas, Wilderness Study Areas, Wild and Scenic Rivers, National Scenic and Historic Trails, and Conservation Lands of the California Desert.",
  "url": "https://www.blm.gov/programs/national-conservation-lands/about",
  "why": "no total words near it"
 },
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
 "same_agency": false,
 "score": 7,
 "t": "BLM Wilderness Area",
 "verdict": "ours unknown"
}
```

## US-0059 Rocky Mountain National Park
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Rocky Mountain National Park",
 "official": {
  "acres": 265600.0,
  "as": "415 square miles",
  "clean": false,
  "line": "ional Park • Colorado Located in northern Colorado, visitors to Rocky Mountain National Park can explore over 415 square miles (265,807 acres) within the Southern Rocky Mountains. From montane meadows to subalpine forests and mountain p",
  "read": "2026-11-01",
  "sent": "Located in northern Colorado, visitors to Rocky Mountain National Park can explore over 415 square miles (265,807 acres) within the Southern Rocky Mountains.",
  "url": "https://www.nps.gov/romo/index.htm",
  "why": "total-looking"
 },
 "ours": {
  "acres": 265475,
  "manager": "",
  "pieces": [
   [
    3471,
    "Rocky Mountain National Park",
    265475,
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
 "score": 7,
 "t": "National Park",
 "verdict": "agree"
}
```

## US-12187 Roaring Fork State Wildlife Area
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 43 acres, no total words near it)",
 "checked": "2026-11-01",
 "handover": [],
 "n": "Roaring Fork State Wildlife Area",
 "official": {
  "acres": 43.0,
  "as": "43 acres",
  "clean": false,
  "line": "d check current hunting, fishing and land use regulations when planning to visit a State Wildlife Area. Acres 43 acres. Elevation min. 5,884 ft - max 6,120 ft GMU 43 Hunting Opportunities No hunting opportunities available Activ",
  "read": "2026-11-01",
  "sent": "43 acres.",
  "url": "https://cpw.state.co.us/state-wildlife-areas/roaring-forkgianinetti-swa-fishing-lease",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 3,
  "manager": "",
  "pieces": [
   [
    189236,
    "Roaring Fork State Wildlife Area - Wheeler Parcel",
    3,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 93,
 "same_agency": false,
 "score": 5,
 "t": "State Wildlife Area",
 "verdict": "unsure"
}
```

## US-11916 Dolores River Canyon BLM Wilderness Area
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-01",
 "handover": [],
 "n": "Dolores River Canyon BLM Wilderness Area",
 "official": {
  "acres": 30119.0,
  "as": "30,119 acres",
  "clean": true,
  "line": "miles west of Naturita; 28 miles north of Dove Creek; two miles south of CO-90. Visitor Advisory Total Area: 30,119 acres Elevation Range: ~5,000 to ~6,400 feet BLM Field Office: Tres Rios and Uncompahgre Designated: 1980 (Wilderne",
  "read": "2026-11-01",
  "sent": "Total Area: 30,119 acres",
  "url": "https://www.blm.gov/site-page/programs-national-conservation-lands-colorado-dolores-river-canyon-wsa",
  "why": "clean total"
 },
 "ours": {
  "acres": 13423,
  "manager": "",
  "pieces": [
   [
    "sgakg10797",
    "Dolores River Canyon, Zone 2",
    8451,
    "name"
   ],
   [
    "sgakg10798",
    "Dolores River Canyon, Zone 1",
    4952,
    "name"
   ],
   [
    "sgakg10796",
    "Dolores River Canyon, Zone 3",
    20,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 2
 },
 "owner_now": null,
 "pct": 55,
 "same_agency": false,
 "score": 6,
 "t": "BLM Wilderness Area",
 "verdict": "off"
}
```

## US-1233 Paonia State Park
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Paonia State Park",
 "official": {
  "acres": 1857.0,
  "as": "1,857 acres",
  "clean": false,
  "line": ", \"touchThreshold\" : 5, \"useCSS\" : true, \"useTransform\" : true, \"centerPadding\":\"0px\", \"infinite\" : false }'> 1,857 acres 334 surface-acre reservoir 2 picnic areas 20 campsites Accessing the Park Directions Directions The park is l",
  "read": "2026-11-01",
  "sent": "1,857 acres",
  "url": "https://cpw.state.co.us/placestogo/parks/Paonia",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 1584,
  "dissolved": {
   "after": 2217,
   "before": 3801,
   "copies": 1,
   "families": {
    "padus": 633,
    "sgcob": 1584
   },
   "family_fold": 633,
   "family_used": "sgcob",
   "parts": 0,
   "records": 4,
   "tracts": 3
  },
  "family_fold": "layers {'sgcob': 1584, 'padus': 633}: one land in 2 layers, the sgcob copy used (633 ac of copies not added)",
  "manager": "",
  "note": "4 joined records = 3 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 3801 -> 2217 acres",
  "pieces": [
   [
    "sgcob32",
    "Paonia State Park",
    1584,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 15,
 "same_agency": false,
 "score": 8,
 "t": "State Park",
 "verdict": "agree"
}
```

## US-0190 Flagler Reservoir State Wildlife Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Flagler Reservoir State Wildlife Area",
 "official": null,
 "ours": {
  "acres": 643,
  "dissolved": {
   "after": 1747,
   "before": 2815,
   "copies": 2,
   "families": {
    "cow": 534,
    "padus": 570,
    "sgcoc": 643
   },
   "family_fold": 1104,
   "family_used": "sgcoc",
   "parts": 0,
   "records": 5,
   "tracts": 3
  },
  "family_fold": "layers {'sgcoc': 643, 'padus': 570, 'cow': 534}: one land in 3 layers, the sgcoc copy used (1,104 ac of copies not added)",
  "manager": "",
  "note": "5 joined records = 3 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 2815 -> 1747 acres",
  "pieces": [
   [
    "sgcoc338",
    "Flagler STL",
    643,
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
 "t": "State Wildlife Area",
 "verdict": "no size on page"
}
```

## US-1234 Pearl Lake State Park
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 3,098 acres, no total words near it)",
 "checked": "2026-11-01",
 "handover": [],
 "n": "Pearl Lake State Park",
 "official": {
  "acres": 3098.0,
  "as": "3,098 acres",
  "clean": false,
  "line": ", \"touchThreshold\" : 5, \"useCSS\" : true, \"useTransform\" : true, \"centerPadding\":\"0px\", \"infinite\" : false }'> 3,098 acres 370+ species of birds 60 picnic sites 21+ miles of trails Accessing the Park Directions Directions From Steam",
  "read": "2026-11-01",
  "sent": "3,098 acres",
  "url": "https://cpw.state.co.us/placestogo/parks/PearlLake",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 298,
  "dissolved": {
   "after": 298,
   "before": 893,
   "copies": 1,
   "parts": 3,
   "records": 5,
   "tracts": 1
  },
  "manager": "",
  "note": "5 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 3 fee tracts under a designation record folded; summed 893 -> 298 acres",
  "pieces": [
   [
    "sgcob33",
    "Pearl Lake State Park",
    298,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 90,
 "same_agency": false,
 "score": 7,
 "t": "State Park",
 "verdict": "unsure"
}
```
