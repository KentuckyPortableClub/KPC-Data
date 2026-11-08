# park truth checker: US-AL random sample of 12 (2026-11-08; seed = date + area, same rows for everyone)

Source file: `data/truth/US-AL.json`

## US-11292 Historic Blakeley State Park Historic Site
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-01",
 "handover": [],
 "n": "Historic Blakeley State Park Historic Site",
 "official": {
  "acres": 2000.0,
  "as": "2,000 acres",
  "clean": false,
  "line": "Park is one of the largest and most diverse attractions within the Gulf Coast region. Within these more than 2,000 acres of some of the most biodiverse habitat in North America, the park contains the sites of Alabama's largest Civ",
  "read": "2026-11-01",
  "sent": "Within these more than 2,000 acres of some of the most biodiverse habitat in North America, the park contains the sites of Alabama's largest Civil War battle, the important early Alabama town of Blakeley, and Native American settlements dating back thousands of years.",
  "url": "https://www.blakeleypark.com/",
  "why": "total-looking"
 },
 "ours": {
  "acres": 417,
  "manager": "",
  "pieces": [
   [
    166142,
    "Historic Blakeley State Park",
    417,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 79,
 "same_agency": false,
 "score": 3,
 "t": "Historic Site",
 "verdict": "off"
}
```

## US-1041 Frank Jackson State Park
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-08",
 "n": "Frank Jackson State Park",
 "official": null,
 "ours": {
  "acres": 2847,
  "manager": "",
  "pieces": [
   [
    166222,
    "Frank Jackson State Park",
    2077,
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

## US-3705 Shoal Creek Preserve State Conservation Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Shoal Creek Preserve State Conservation Area",
 "official": {
  "acres": 300.0,
  "as": "300 acre",
  "clean": false,
  "line": "miles give hikers views of Shoal Creek, Indian camp Creek, Lawson Branch, and Jones Branch, all on this small 300-acre property. Parking is located on County Road 61. The National Recreation Trails website has additional informa",
  "read": "2026-11-01",
  "sent": "Two trails totaling 4.3 miles give hikers views of Shoal Creek, Indian camp Creek, Lawson Branch, and Jones Branch, all on this small 300-acre property.",
  "url": "https://www.alabamaforeverwild.com/shoal-creek-preserve",
  "why": "history"
 },
 "ours": {
  "acres": 303,
  "dissolved": {
   "after": 303,
   "before": 601,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 601 -> 303 acres",
  "pieces": [
   [
    166074,
    "Shoal Creek Preserve Tract",
    303,
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
 "score": 8,
 "t": "State Conservation Area",
 "verdict": "agree"
}
```

## US-11032 Old Cahawba Prairie Conservation Reserve
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-11-01",
 "handover": [],
 "n": "Old Cahawba Prairie Conservation Reserve",
 "official": null,
 "ours": {
  "acres": 3078,
  "manager": "",
  "pieces": [
   [
    166161,
    "Old Cahawba Prairie Tract",
    3024,
    "reviewed"
   ],
   [
    "sgalb160",
    "Old Cahawba Prairie - Childers Creek Addition",
    54,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 2
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "Conservation Reserve",
 "verdict": "unsure"
}
```

## US-3712 Wehle State Nature Preserve
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-01",
 "handover": [],
 "n": "Wehle State Nature Preserve",
 "official": {
  "acres": 1505.0,
  "as": "1,505 acres",
  "clean": false,
  "line": "e at Wehle Overview Recreational opportunities abound on the Wehle Tract in Bullock County. Visitors to these 1,505 acres of rolling pine hills and hardwood bottoms can camp, fish, hike, horseback ride and observe wildlife. Additio",
  "read": "2026-11-01",
  "sent": "Visitors to these 1,505 acres of rolling pine hills and hardwood bottoms can camp, fish, hike, horseback ride and observe wildlife.",
  "url": "https://www.alabamaforeverwild.com/wehle-tract",
  "why": "total-looking"
 },
 "ours": {
  "acres": 868,
  "manager": "",
  "pieces": [
   [
    166090,
    "Wehle Nature Preserve",
    868,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 42,
 "same_agency": false,
 "score": 5,
 "t": "State Nature Preserve",
 "verdict": "off"
}
```

## US-3687 Dugger Mountain Wilderness National Forest
```json
{
 "cause": "agency smaller: our outline may hold water, a lease or a neighbour tract",
 "checked": "2026-11-01",
 "handover": [],
 "n": "Dugger Mountain Wilderness National Forest",
 "official": {
  "acres": 5878.0,
  "as": "5,878 acres",
  "clean": false,
  "line": "miles are maintained? 283 How many road miles maintained? 524 How many cultural resources surveys completed? 5,878 acres How many land use permits? 21 with $73,239 collected in land use fees. How many recreation special use permit",
  "read": "2026-11-01",
  "sent": "5,878 acres",
  "url": "https://www.fs.usda.gov/r08/alabama/about-area",
  "why": "total-looking"
 },
 "ours": {
  "acres": 8947,
  "manager": "",
  "pieces": [
   [
    "wld115",
    "Dugger Mountain Wilderness",
    8947,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 52,
 "same_agency": false,
 "score": 5,
 "t": "National Forest",
 "verdict": "off"
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

## US-3714 Yates Lake Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Yates Lake Wildlife Management Area",
 "official": {
  "acres": 5810.0,
  "as": "5,810 acres",
  "clean": false,
  "line": "Lake WMA Road at Yates Lake Overview The Forever Wild Gothard-AWF Yates Lake WMA in Elmore County consists of 5,810 acres of pine-hardwood hills and creek valleys on the western shore of scenic Yates Lake. Habitats include longleaf",
  "read": "2026-11-01",
  "sent": "The Forever Wild Gothard-AWF Yates Lake WMA in Elmore County consists of 5,810 acres of pine-hardwood hills and creek valleys on the western shore of scenic Yates Lake.",
  "url": "https://www.alabamaforeverwild.com/yates-lake-wma",
  "why": "part (a lake, a purchase, a campground…)"
 },
 "ours": {
  "acres": 5506,
  "manager": "",
  "pieces": [
   [
    166141,
    "Yates Lake West Wildlife Management Area",
    3540,
    "name"
   ],
   [
    166140,
    "Yates Lake West Wildlife Management Area",
    1966,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 5,
 "same_agency": false,
 "score": 8,
 "t": "Wildlife Management Area",
 "verdict": "agree"
}
```

## US-3697 Lowndes Wildlife Management Area
```json
{
 "cause": "agency smaller: our outline may hold water, a lease or a neighbour tract",
 "checked": "2026-11-01",
 "handover": [],
 "n": "Lowndes Wildlife Management Area",
 "official": {
  "acres": 1967.0,
  "as": "1,967 acres",
  "clean": true,
  "line": "ty consist of two acquisitions featuring upland and bottomland hardwoods, pine plantations and open fields on 1,967 acres of gently rolling alluvial land within Alabama’s famed Black Belt. Hunting Hunters must possess a valid hunti",
  "read": "2026-11-01",
  "sent": "Managed for public hunting, the Lowndes Wildlife Management Area additions in Lowndes County consist of two acquisitions featuring upland and bottomland hardwoods, pine plantations and open fields on 1,967 acres of gently rolling alluvial land within Alabama’s famed Black Belt.",
  "url": "https://www.alabamaforeverwild.com/lowndes-wma-additions",
  "why": "clean total"
 },
 "ours": {
  "acres": 14472,
  "family_fold": "layers {'sgalc': 14290, 'padus': 14472}: one land in 2 layers, the padus copy used (14,290 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    9537,
    "Lowndes Wildlife Management Area",
    11050,
    "name"
   ],
   [
    166196,
    "Lowndes Wildlife Management Area",
    1417,
    "name"
   ],
   [
    166120,
    "Lowndes Wildlife Management Area",
    1366,
    "name"
   ],
   [
    166119,
    "Lowndes Wildlife Management Area",
    639,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 636,
 "same_agency": false,
 "score": 6,
 "t": "Wildlife Management Area",
 "verdict": "off"
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
