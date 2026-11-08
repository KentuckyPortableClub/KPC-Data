# park truth checker: US-AL random sample of 12 (2026-11-08; seed = date + area, same rows for everyone)

Source file: `data/truth/US-AL.json`

## US-11026 The Indian Mountain Conservation Area
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-01",
 "handover": [],
 "n": "The Indian Mountain Conservation Area",
 "official": {
  "acres": 1114.0,
  "as": "1,114 acres",
  "clean": true,
  "line": "ed in partnership with The Conservation Fund, the three tract acquisitions that make up Indian Mountain cover 1,114 acres of mountainous upland hardwood forest land in Cherokee County. Within the Indian Mountain Tract, the Pinhoti",
  "read": "2026-11-01",
  "sent": "Purchased in partnership with The Conservation Fund, the three tract acquisitions that make up Indian Mountain cover 1,114 acres of mountainous upland hardwood forest land in Cherokee County.",
  "url": "https://www.alabamaforeverwild.com/indian-mountain",
  "why": "clean total"
 },
 "ours": {
  "acres": 520,
  "dissolved": {
   "after": 600,
   "before": 1709,
   "copies": 3,
   "families": {
    "padus": 80,
    "sgalb": 520
   },
   "family_fold": 80,
   "family_used": "sgalb",
   "parts": 0,
   "records": 5,
   "tracts": 2
  },
  "family_fold": "layers {'sgalb': 520, 'padus': 80}: one land in 2 layers, the sgalb copy used (80 ac of copies not added)",
  "manager": "",
  "note": "5 joined records = 2 tracts: 3 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1709 -> 600 acres",
  "pieces": [
   [
    "sgalb139",
    "Indian Mountain - Simmons Addition",
    520,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 53,
 "same_agency": false,
 "score": 4,
 "t": "Conservation Area",
 "verdict": "off"
}
```

## US-1040 Lake Jackson RV Park at Florala State Park
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-11-08",
 "handover": [
  {
   "date_hint": null,
   "kind": "managed by",
   "line": "Florala, AL 36442 Phone Numbers 334-858-6425 HOURS Lake Jackson RV Campground & Park at Florala is now owned and operated by the City of Florala. To make campground reservations call 334-858-6425 Rates: $34.80 a day for water sites, $30.16 for non-water sites, $208.80 weekly for wa",
   "owner_now": "City of Florala",
   "src": "https://www.alapark.com/parks/lake-jackson-rv-park-florala",
   "why": "the park's page (data/parkinfo)"
  }
 ],
 "n": "Lake Jackson RV Park at Florala State Park",
 "official": null,
 "ours": {
  "acres": 65,
  "manager": "",
  "pieces": [
   [
    166221,
    "Florala State Park",
    65,
    "reviewed"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": "City of Florala",
 "pct": null,
 "score": 6,
 "t": "State Park",
 "verdict": "unsure"
}
```

## US-3682 Cheaha Wilderness Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Cheaha Wilderness Area",
 "official": {
  "acres": 6780.0,
  "as": "6,780 acres",
  "clean": true,
  "line": "essary in wilderness . Contacts Applicable Wilderness Law(s) Public Law 97-411 Date: January 3, 1983 Acreage: 6,780 acres (No official title, designates Cheaha Wilderness) - Public law 97-411 (1/3/1983) To designate the Cheaha Wild",
  "read": "2026-11-01",
  "sent": "Acreage: 6,780 acres",
  "url": "https://wilderness.net/visit-wilderness/?ID=115",
  "why": "clean total"
 },
 "ours": {
  "acres": 7400,
  "manager": "",
  "pieces": [
   [
    "wld77",
    "Cheaha Wilderness",
    7400,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 9,
 "same_agency": false,
 "score": 8,
 "t": "Wilderness Area",
 "verdict": "agree"
}
```

## US-3695 Lauderdale Wildlife Management Area
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-08",
 "n": "Lauderdale Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 21678,
  "dissolved": {
   "after": 35120,
   "before": 41951,
   "copies": 2,
   "families": {
    "padus": 15141,
    "sgalb": 195,
    "sgalc": 19784
   },
   "family_fold": 15336,
   "family_used": "sgalc",
   "key_union": 21678,
   "parts": 8,
   "records": 16,
   "summed": 19784,
   "tracts": 6
  },
  "family_fold": "layers {'sgalc': 19784, 'padus': 15141, 'sgalb': 195}: one land in 3 layers, the sgalc copy used (15,336 ac of copies not added)",
  "manager": "",
  "note": "16 joined records = 6 tracts: 2 copies of a tract (same acres, another layer) and 8 fee tracts under a designation record folded; summed 41951 -> 35120 acres",
  "pieces": [
   [
    "sgalc279",
    "Lauderdale Wildlife Management Area",
    19784,
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
 "t": "Wildlife Management Area",
 "verdict": "no size on page"
}
```

## US-1049 Oak Mountain State Park
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-08",
 "n": "Oak Mountain State Park",
 "official": null,
 "ours": {
  "acres": 12314,
  "manager": "",
  "pieces": [
   [
    166230,
    "Oak Mountain State Park",
    8857,
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
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-3691 Grand Bay Savanna Complex Wildlife Management Area
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-08",
 "n": "Grand Bay Savanna Complex Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 13243,
  "family_fold": "layers {'sgalc': 15062, 'padus': 5233}: one land in 2 layers, the sgalc copy used (5,233 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgalc304",
    "Grand Bay Savanna Wildlife Management Area",
    15062,
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

## US-11033 The Portland Landing Conservation Reserve
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-01",
 "handover": [],
 "n": "The Portland Landing Conservation Reserve",
 "official": {
  "acres": 2473.0,
  "as": "2,473 acres",
  "clean": false,
  "line": "u Search Overview Together the Pine Barren Creek, Rum Creek, and the Portland Landing-Gilmore Addition create 2,473 acres of public hunting opportunity in the black belt prairie area of the State as part of the Portland Landing Spe",
  "read": "2026-11-01",
  "sent": "Together the Pine Barren Creek, Rum Creek, and the Portland Landing-Gilmore Addition create 2,473 acres of public hunting opportunity in the black belt prairie area of the State as part of the Portland Landing Special Opportunity Area.",
  "url": "https://www.alabamaforeverwild.com/pine-barren-and-rum-creek",
  "why": "total-looking"
 },
 "ours": {
  "acres": 317,
  "manager": "",
  "pieces": [
   [
    "sgalb190",
    "Portland Landing - Gilmore Addition",
    317,
    "name"
   ]
  ],
  "pin": "well outside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 87,
 "same_agency": false,
 "score": 3,
 "t": "Conservation Reserve",
 "verdict": "off"
}
```

## US-3696 Lillian Swamp Complex Preserve State Conservation Area
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-11-01",
 "handover": [],
 "n": "Lillian Swamp Complex Preserve State Conservation Area",
 "official": null,
 "ours": {
  "acres": 1852,
  "family_fold": "layers {'padus': 1852, 'sgalb': 486}: one land in 2 layers, the padus copy used (486 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    166068,
    "Lillian Swamp Complex",
    900,
    "name"
   ],
   [
    166173,
    "Lillian Swamp Complex",
    400,
    "name"
   ],
   [
    166067,
    "Lillian Swamp Complex",
    311,
    "name"
   ],
   [
    166066,
    "Lillian Swamp Complex",
    241,
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
 "t": "State Conservation Area",
 "verdict": "unsure"
}
```

## US-3702 Red Hills Wildlife Management Area
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-08",
 "n": "Red Hills Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 18832,
  "family_fold": "layers {'sgalc': 18832, 'padus': 4416}: one land in 2 layers, the sgalc copy used (4,416 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgalc305",
    "Red Hills Wildlife Management Area",
    18832,
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

## US-4598 Little River State Forest
```json
{
 "checked": "2026-11-01",
 "handover": [
  {
   "date_hint": null,
   "kind": "transfer",
   "line": "History of Little River State Forest Originally privately owned land, Little River State Forest was deeded to the Alabama Forestry Commission in the early 1930s. During this time, the Great Depression was taking its toll on America. President Franklin D. Roose",
   "owner_now": "Alabama Forestry Commission",
   "src": "https://forestry.alabama.gov/Pages/Management/LittleRiverSF.aspx",
   "why": "the park's page (data/parkinfo)"
  }
 ],
 "n": "Little River State Forest",
 "official": {
  "acres": 2100.0,
  "as": "2,100 acres",
  "clean": false,
  "line": "County in south Alabama is a little known gem, Little River State Forest (LRSF). Consisting of approximately 2,100 acres of longleaf pine forest, this area provides a unique setting for many outdoor activities such as hiking, camp",
  "read": "2026-11-01",
  "sent": "Consisting of approximately 2,100 acres of longleaf pine forest, this area provides a unique setting for many outdoor activities such as hiking, camping, fishing, and horseback riding.",
  "url": "https://forestry.alabama.gov/Pages/Management/LittleRiverSF.aspx",
  "why": "total-looking"
 },
 "ours": {
  "acres": 2164,
  "family_fold": "layers {'padus': 2164, 'sgalb': 712}: one land in 2 layers, the padus copy used (712 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    166058,
    "Little River State Forest",
    2164,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": "Alabama Forestry Commission",
 "pct": 3,
 "same_agency": false,
 "score": 8,
 "t": "State Forest",
 "verdict": "agree"
}
```

## US-0719 Horseshoe Bend National Military Park
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 23,000,000 acres, a statewide / agency-wide total (over a million acres) on a park that is not a big federal unit)",
 "checked": "2026-11-01",
 "handover": [],
 "n": "Horseshoe Bend National Military Park",
 "official": {
  "acres": 23000000.0,
  "as": "23,000,000 acres",
  "clean": false,
  "line": "oosa River. Over 800 Red Sticks died that day. This battle ended the Creek War, resulted in a land cession of 23,000,000 acres to the United States and created a national hero of Andrew Jackson. Plan your visit About the park Visitors c",
  "read": "2026-11-01",
  "sent": "This battle ended the Creek War, resulted in a land cession of 23,000,000 acres to the United States and created a national hero of Andrew Jackson.",
  "url": "https://www.nps.gov/hobe/index.htm",
  "why": "a statewide / agency-wide total (over a million acres) on a park that is not a big federal unit"
 },
 "ours": {
  "acres": 2079,
  "manager": "",
  "pieces": [
   [
    3287,
    "Horseshoe Bend National Military Park",
    2079,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 100,
 "same_agency": false,
 "score": 5,
 "t": "National Military Park",
 "verdict": "unsure"
}
```

## US-4597 Hauss State Forest
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Hauss State Forest",
 "official": null,
 "ours": {
  "acres": 319,
  "manager": "",
  "pieces": [
   [
    166057,
    "Hauss State Forest",
    319,
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
 "t": "State Forest",
 "verdict": "no size on page"
}
```
