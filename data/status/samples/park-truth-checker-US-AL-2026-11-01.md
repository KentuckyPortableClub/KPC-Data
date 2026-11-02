# park truth checker: US-AL random sample of 12 (2026-11-01; seed = date + area, same rows for everyone)

Source file: `data/truth/US-AL.json`

## US-13342 Bibb Country State Public Fishing Lake
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Bibb Country State Public Fishing Lake",
 "official": {
  "acres": 100.0,
  "as": "100 acre",
  "clean": false,
  "line": "c Fishing Lake Bibb County State Public Fishing Lake is located 7.5 miles north of Centreville, Alabama. This 100-acre lake is stocked with largemouth bass, bluegill, redear sunfish, channel catfish, and crappie. Amenities inclu",
  "read": "2026-11-01",
  "sent": "This 100-acre lake is stocked with largemouth bass, bluegill, redear sunfish, channel catfish, and crappie.",
  "url": "https://www.outdooralabama.com/public-fishing-lakes/bibb-county-pfl",
  "why": "part (a lake, a purchase, a campground…)"
 },
 "ours": {
  "acres": 95,
  "manager": "",
  "pieces": [
   [
    166200,
    "Bibb County Public Fishing Lake",
    95,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 5,
 "same_agency": false,
 "score": 7,
 "t": "State Public Fishing Lake",
 "verdict": "agree"
}
```

## US-4600 Weogufka State Forest
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Weogufka State Forest",
 "official": {
  "acres": 240.0,
  "as": "240 acres",
  "clean": true,
  "line": "bama, in Coosa County, and contains a CCC-built lookout tower and shelters. Weogufka State Forest consists of 240 acres of upland hardwood on Flagg Mountain. It is owned by the State of Alabama and Managed by the Alabama Forestry",
  "read": "2026-11-01",
  "sent": "Weogufka State Forest consists of 240 acres of upland hardwood on Flagg Mountain.",
  "url": "https://forestry.alabama.gov/Pages/Management/WeogufkaSF.aspx",
  "why": "clean total"
 },
 "ours": {
  "acres": 242,
  "manager": "",
  "pieces": [
   [
    166061,
    "Weogufka State Forest",
    242,
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
 "t": "State Forest",
 "verdict": "agree"
}
```

## US-12967 Chambers County State Public Fishing Lake
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Chambers County State Public Fishing Lake",
 "official": {
  "acres": 183.0,
  "as": "183 acre",
  "clean": false,
  "line": "shing Lake Chambers County State Public Fishing Lake is located 5 miles southeast of LaFayette, Alabama. This 183-acre lake is stocked with largemouth bass, bluegill, redear sunfish, channel catfish, and crappie. Amenities inclu",
  "read": "2026-11-01",
  "sent": "This 183-acre lake is stocked with largemouth bass, bluegill, redear sunfish, channel catfish, and crappie.",
  "url": "https://www.outdooralabama.com/alabama-public-fishing-lakes-pfls/chambers-county-pfl",
  "why": "part (a lake, a purchase, a campground…)"
 },
 "ours": {
  "acres": 172,
  "manager": "",
  "pieces": [
   [
    166201,
    "Chambers County Public Fishing Lake",
    172,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 6,
 "same_agency": false,
 "score": 8,
 "t": "State Public Fishing Lake",
 "verdict": "agree"
}
```

## US-1037 Cheaha Resort State Park
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-01",
 "n": "Cheaha Resort State Park",
 "official": null,
 "ours": {
  "acres": 3610,
  "manager": "",
  "pieces": [
   [
    166219,
    "Cheaha State Park",
    3610,
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

## US-9916 Blackwater River State Nature Preserve
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-01",
 "n": "Blackwater River State Nature Preserve",
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
 "score": 7,
 "t": "State Nature Preserve",
 "verdict": "ours unknown"
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

## US-3699 Mobile-Tensaw Delta Wildlife Management Area
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-01",
 "n": "Mobile-Tensaw Delta Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 22495,
  "family_fold": "layers {'sgalc': 22495, 'padus': 2079}: one land in 2 layers, the sgalc copy used (2,079 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgalc284",
    "Mobile-Tensaw Delta Wildlife Management Area",
    22495,
    "name"
   ]
  ],
  "pin": "just outside",
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

## US-9874 Mud Creek Management Area
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-01",
 "n": "Mud Creek Management Area",
 "official": null,
 "ours": {
  "acres": 8104,
  "manager": "",
  "pieces": [
   [
    "sgalc285",
    "Mud Creek Management Area",
    8023,
    "reviewed"
   ],
   [
    256228,
    "Mud Creek Management Area",
    81,
    "reviewed"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "Management Area",
 "verdict": "no size on page"
}
```

## US-11272 Mulberry Fork Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Mulberry Fork Wildlife Management Area",
 "official": {
  "acres": 33280.0,
  "as": "33,280 acres",
  "clean": false,
  "line": "ry Fork Wildlife Management Area Tract in Walker and Tuscaloosa counties provides a 94-year hunting lease for 33,280 acres. Mountainous and wooded terrain, host springs and rocky bluffs comprise the landscape, along with early succe",
  "read": "2026-11-01",
  "sent": "The Mulberry Fork Wildlife Management Area Tract in Walker and Tuscaloosa counties provides a 94-year hunting lease for 33,280 acres.",
  "url": "https://www.alabamaforeverwild.com/mulberry-fork-wma",
  "why": "total-looking"
 },
 "ours": {
  "acres": 33251,
  "manager": "",
  "pieces": [
   [
    "sgalc286",
    "Mulberry Fork Wildlife Management Area",
    33251,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 0,
 "same_agency": false,
 "score": 8,
 "t": "Wildlife Management Area",
 "verdict": "agree"
}
```

## US-0161 Wheeler National Wildlife Refuge
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-01",
 "handover": [],
 "n": "Wheeler National Wildlife Refuge",
 "official": {
  "acres": 35000.0,
  "as": "35,000 acre",
  "clean": false,
  "line": "ttracting migratory waterfowl onto a multipurpose impoundment. Although designated as a waterfowl refuge, the 35,000 acre refuge provides for a wide spectrum of wildlife. Its great diversity of habitat includes deep river channels,",
  "read": "2026-11-01",
  "sent": "Although designated as a waterfowl refuge, the 35,000 acre refuge provides for a wide spectrum of wildlife.",
  "url": "https://www.fws.gov/refuge/wheeler/about-us",
  "why": "total-looking"
 },
 "ours": {
  "acres": 26848,
  "dissolved": {
   "after": 26848,
   "before": 34844,
   "copies": 1,
   "parts": 0,
   "records": 4,
   "tracts": 3
  },
  "manager": "",
  "note": "4 joined records = 3 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 34844 -> 26848 acres",
  "pieces": [
   [
    1845,
    "Wheeler National Wildlife Refuge",
    16648,
    "name"
   ],
   [
    4470,
    "Wheeler National Wildlife Refuge",
    7996,
    "name"
   ],
   [
    1846,
    "Wheeler National Wildlife Refuge",
    2204,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 23,
 "same_agency": false,
 "score": 5,
 "t": "National Wildlife Refuge",
 "verdict": "off"
}
```

## US-3690 Geneva State Forest Wildlife Management Area
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-01",
 "n": "Geneva State Forest Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 16475,
  "family_fold": "layers {'sgalc': 16475, 'padus': 7276}: one land in 2 layers, the sgalc copy used (7,276 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgalc274",
    "Geneva State Forest Wildlife Management Area",
    16475,
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

## US-13088 Choctaw Nation Wildlife Refuge National Wildlife Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Choctaw Nation Wildlife Refuge National Wildlife Area",
 "official": {
  "acres": 4218.0,
  "as": "4,218 acres",
  "clean": false,
  "line": "njoy. Learn More About Visiting Location and Contact Information About Us Choctaw National Wildlife Refuge is 4,218 acres acquired by the Corp of Engineers in conjunction with the Coffeeville Lock and Dam project. The refuge encomp",
  "read": "2026-11-01",
  "sent": "Choctaw National Wildlife Refuge is 4,218 acres acquired by the Corp of Engineers in conjunction with the Coffeeville Lock and Dam project.",
  "url": "https://www.fws.gov/refuge/choctaw",
  "why": "part (a lake, a purchase, a campground…)"
 },
 "ours": {
  "acres": 3975,
  "manager": "",
  "pieces": [
   [
    "fws4879",
    "Choctaw National Wildlife Refuge",
    3975,
    "reviewed"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 6,
 "same_agency": false,
 "score": 7,
 "t": "National Wildlife Area",
 "verdict": "agree"
}
```
