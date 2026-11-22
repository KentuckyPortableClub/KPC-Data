# park truth checker: US-NY random sample of 12 (2026-11-22; seed = date + area, same rows for everyone)

Source file: `data/truth/US-NY.json`

## US-2122 Pixley Falls State Park
```json
{
 "cause": "a number 3 parks share from the same sentence (1 ac): an agency total, not this park",
 "checked": "2026-11-17",
 "handover": [],
 "n": "Pixley Falls State Park",
 "official": null,
 "ours": {
  "acres": 378,
  "dissolved": {
   "after": 378,
   "before": 755,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 755 -> 378 acres",
  "pieces": [
   [
    237571,
    "Pixley Falls State Park",
    378,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "same_agency": false,
 "score": 7,
 "t": "State Park",
 "verdict": "unsure"
}
```

## US-2130 Roberto Clemente State Park
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-17",
 "handover": [
  {
   "date_hint": "1973",
   "kind": "renamed",
   "line": "s, playgrounds and a waterfront promenade. The park opened in 1973 as the Harlem River Park and was renamed after Clemente, the first Latino-American inducted into the Baseball Hall of Fame. During the year, the park is home to numerous concerts and special events. There is truly someth",
   "owner_now": "Baseball Hall of Fa",
   "src": "https://parks.ny.gov/parks/robertoclemente/details.aspx",
   "why": "the park's page (data/parkinfo)"
  }
 ],
 "n": "Roberto Clemente State Park",
 "official": {
  "acres": 25.0,
  "as": "25 acre",
  "clean": true,
  "line": "ility at this location, please contact us at the number listed on this page. Roberto Clemente State Park is a 25-acre waterfront park located along the Harlem River in the Bronx. The park offers a variety of recreational and cu",
  "read": "2026-11-17",
  "sent": "Roberto Clemente State Park is a 25-acre waterfront park located along the Harlem River in the Bronx.",
  "url": "https://parks.ny.gov/parks/robertoclemente/details.aspx",
  "why": "clean total"
 },
 "ours": {
  "acres": 14,
  "dissolved": {
   "after": 24,
   "before": 48,
   "copies": 0,
   "key_union": 14,
   "parts": 2,
   "records": 3,
   "summed": 24,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 0 copies of a tract (same acres, another layer) and 2 fee tracts under a designation record folded; summed 48 -> 24 acres",
  "pieces": [
   [
    237578,
    "Roberto Clemente State Park",
    24,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": "Baseball Hall of Fa",
 "pct": 44,
 "same_agency": false,
 "score": 5,
 "t": "State Park",
 "verdict": "off"
}
```

## US-9092 NY Fish Creek Wildlife Management Area
```json
{
 "checked": "2026-11-17",
 "handover": [],
 "n": "NY Fish Creek Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 4559,
  "dissolved": {
   "after": 4559,
   "before": 9115,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 9115 -> 4559 acres",
  "pieces": [
   [
    237271,
    "Fish Creek Wma",
    4559,
    "words"
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

## US-10050 Darwin Martin House State Historic Site
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 1.5 acre, a tiny number without size wording)",
 "checked": "2026-11-17",
 "handover": [],
 "n": "Darwin Martin House State Historic Site",
 "official": {
  "acres": 1.5,
  "as": "1.5 acre",
  "clean": false,
  "line": "erpiece by one of America’s most important architects that showcases historic preservation at its finest. The 1.5-acre property includes historic structures designed by Frank Lloyd Wright between 1903-1909 and restored to their",
  "read": "2026-11-17",
  "sent": "The 1.5-acre property includes historic structures designed by Frank Lloyd Wright between 1903-1909 and restored to their original glory, including the main Martin House, Pergola, Conservatory, and Carriage House, the Delta Barton House, the Gardener’s Cottage, as well as",
  "url": "https://parks.ny.gov/historic-sites/darwinmartinhouse/details.aspx",
  "why": "a tiny number without size wording"
 },
 "ours": {
  "acres": 1,
  "manager": "",
  "pieces": [
   [
    237405,
    "Darwin Martin House Complex and Visitor Center",
    1,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 33,
 "same_agency": false,
 "score": 5,
 "t": "State Historic Site",
 "verdict": "unsure"
}
```

## US-4239 North Country Trail National Scenic Trail
```json
{
 "checked": "2026-11-17",
 "handover": [],
 "n": "North Country Trail National Scenic Trail",
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
   "US-ND",
   "US-VT",
   "US-MI",
   "US-PA",
   "US-OH",
   "US-NY",
   "US-WI",
   "US-MN"
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

## US-2082 Irondequoit Bay Marine State Park
```json
{
 "checked": "2026-11-17",
 "handover": [],
 "n": "Irondequoit Bay Marine State Park",
 "official": null,
 "ours": {
  "acres": 69,
  "dissolved": {
   "after": 69,
   "before": 138,
   "copies": 0,
   "parts": 6,
   "records": 7,
   "tracts": 1
  },
  "manager": "",
  "note": "7 joined records = 1 tracts: 0 copies of a tract (same acres, another layer) and 6 fee tracts under a designation record folded; summed 138 -> 69 acres",
  "pieces": [
   [
    237631,
    "Irondequoit Bay Marine Park",
    69,
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

## US-0811 Eleanor Roosevelt National Historic Site
```json
{
 "checked": "2026-11-17",
 "handover": [],
 "n": "Eleanor Roosevelt National Historic Site",
 "official": null,
 "ours": {
  "acres": 177,
  "manager": "",
  "pieces": [
   [
    3121,
    "Eleanor Roosevelt National Historic Site",
    177,
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
 "t": "National Historic Site",
 "verdict": "no size on page"
}
```

## US-5246 Pigeon Hill State Forest
```json
{
 "checked": "2026-11-17",
 "handover": [],
 "n": "Pigeon Hill State Forest",
 "official": null,
 "ours": {
  "acres": 737,
  "dissolved": {
   "after": 737,
   "before": 1473,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1473 -> 737 acres",
  "pieces": [
   [
    236692,
    "Pigeon Hill State Forest",
    737,
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
 "verdict": "no size on page"
}
```

## US-8094 East Bartlett Pine Barrens State Forest
```json
{
 "checked": "2026-11-17",
 "handover": [],
 "n": "East Bartlett Pine Barrens State Forest",
 "official": null,
 "ours": {
  "acres": 105,
  "dissolved": {
   "after": 105,
   "before": 210,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 210 -> 105 acres",
  "pieces": [
   [
    236519,
    "East Bartlett Pine Barrens State Forest",
    105,
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
 "t": "State Forest",
 "verdict": "no size on page"
}
```

## US-5364 West Mountain State Forest
```json
{
 "checked": "2026-11-17",
 "handover": [],
 "n": "West Mountain State Forest",
 "official": null,
 "ours": {
  "acres": 825,
  "dissolved": {
   "after": 825,
   "before": 1650,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1650 -> 825 acres",
  "pieces": [
   [
    236807,
    "West Mountain State Forest",
    825,
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
 "verdict": "no size on page"
}
```

## US-2004 Amherst State Park
```json
{
 "checked": "2026-11-17",
 "handover": [],
 "n": "Amherst State Park",
 "official": {
  "acres": 77.0,
  "as": "77 acres",
  "clean": false,
  "line": "falo, New York. Nature trails are available for the general public. Amherst State Park includes approximately 77 acres of State-owned land and approximately 3 acres of Town-owned land in the Town of Amherst , Erie County, New Yo",
  "read": "2026-11-17",
  "sent": "Amherst State Park includes approximately 77 acres of State-owned land and approximately 3 acres of Town-owned land in the Town of Amherst , Erie County, New York.",
  "url": "http://www.amherststatepark.org/ASP/Welcome.html",
  "why": "total-looking"
 },
 "ours": {
  "acres": 85,
  "dissolved": {
   "after": 79,
   "before": 158,
   "copies": 1,
   "key_union": 85,
   "parts": 0,
   "records": 2,
   "summed": 79,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 158 -> 79 acres",
  "pieces": [
   [
    237444,
    "Amherst State Park",
    79,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 10,
 "same_agency": false,
 "score": 8,
 "t": "State Park",
 "verdict": "agree"
}
```

## US-5429 Mount Pisgah State Forest
```json
{
 "checked": "2026-11-17",
 "handover": [],
 "n": "Mount Pisgah State Forest",
 "official": null,
 "ours": {
  "acres": 652,
  "dissolved": {
   "after": 652,
   "before": 1304,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1304 -> 652 acres",
  "pieces": [
   [
    236652,
    "Mount Pisgah State Forest",
    652,
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
 "verdict": "no size on page"
}
```
