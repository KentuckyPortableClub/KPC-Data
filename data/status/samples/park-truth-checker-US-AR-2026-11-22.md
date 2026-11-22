# park truth checker: US-AR random sample of 12 (2026-11-22; seed = date + area, same rows for everyone)

Source file: `data/truth/US-AR.json`

## US-1084 Herman Davis State Park
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Herman Davis State Park",
 "official": null,
 "ours": {
  "acres": 1,
  "dissolved": {
   "after": 1,
   "before": 2,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 2 -> 1 acres",
  "pieces": [
   [
    157458,
    "Herman Davis State Park",
    1,
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

## US-7347 Loafer's Glory Wildlife Management Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Loafer's Glory Wildlife Management Area",
 "official": {
  "acres": 2720.0,
  "as": "2,720 acres",
  "clean": false,
  "line": "ately to steeply sloped with hardwood and pine. Area is near Buffalo River. Area has 5 parts in all, totaling 2,720 acres. Hunting Opportunities Turkey, deer, squirrel and furbearers. Location The WMA is in Searcy County, 10 miles",
  "read": "2026-11-22",
  "sent": "Area has 5 parts in all, totaling 2,720 acres.",
  "url": "https://www.agfc.com/en/zone-map/729/",
  "why": "history"
 },
 "ours": {
  "acres": 2796,
  "manager": "",
  "pieces": [
   [
    166806,
    "Loafer's Glory",
    2575,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 3,
 "same_agency": false,
 "score": 7,
 "t": "Wildlife Management Area",
 "verdict": "agree"
}
```

## US-7304 McIlroy Madison County Wildlife Management Area
```json
{
 "checked": "2026-11-22",
 "handover": [
  {
   "date_hint": "2008",
   "kind": "renamed",
   "line": "ired): April 19-21, April 24-26, May 1-3 and May 7-9. One legal turkey. About the Name The area was renamed in January 2008 to honor the previous owners of the land. The McIlroy family of Fayetteville owned approximately 15,000 acres in the county where the WMA is",
   "owner_now": null,
   "src": "https://www.agfc.com/en/zone-map/732/",
   "why": "the park's page (data/parkinfo)"
  }
 ],
 "n": "McIlroy Madison County Wildlife Management Area",
 "official": {
  "acres": 15000.0,
  "as": "15,000 acres",
  "clean": false,
  "line": "January 2008 to honor the previous owners of the land. The McIlroy family of Fayetteville owned approximately 15,000 acres in the county where the WMA is now located. Access Major access to area is from state highway 23. To find the",
  "read": "2026-11-22",
  "sent": "The McIlroy family of Fayetteville owned approximately 15,000 acres in the county where the WMA is now located.",
  "url": "https://www.agfc.com/en/zone-map/732/",
  "why": "total-looking"
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
 "t": "Wildlife Management Area",
 "verdict": "ours unknown"
}
```

## US-7268 Brewer Lake Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Brewer Lake Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 2411,
  "manager": "",
  "pieces": [],
  "pin": "inside",
  "src": "water outline only",
  "unknown_pieces": 2
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "Wildlife Management Area",
 "verdict": "ours unknown"
}
```

## US-11127 Arkansas Rocks! Mining & Mineral State Trail
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Arkansas Rocks! Mining & Mineral State Trail",
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
 "score": 4,
 "t": "State Trail",
 "verdict": "ours unknown"
}
```

## US-4424 Ouachita National Forest
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-22",
 "handover": [],
 "n": "Ouachita National Forest",
 "note": "whole park compared (POTA lists it in 1 states: {'US-AR': 1430577})",
 "official": {
  "acres": 1800000.0,
  "as": "1.8 million acres",
  "clean": false,
  "line": "ildfire Dashboard Plan Your Adventure We're the oldest and largest National Forest in the South, encompassing 1.8 million acres in Arkansas and Oklahoma. Come explore T T T Welcome to Ouachita National Forest Located in both Arkansas and",
  "read": "2026-11-22",
  "sent": "We're the oldest and largest National Forest in the South, encompassing 1.8 million acres in Arkansas and Oklahoma.",
  "url": "https://www.fs.usda.gov/r08/ouachita",
  "why": "total-looking"
 },
 "ours": {
  "acres": 1430577,
  "acres_by_state": {
   "US-AR": 1430577
  },
  "manager": "",
  "pieces": [
   [
    3000,
    "Ouachita National Forest",
    1430575,
    "name"
   ],
   [
    3002,
    "Ouachita National Forest",
    2,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "states": [
   "US-OK",
   "US-AR"
  ],
  "unknown_pieces": 0,
  "whole_park": true
 },
 "owner_now": null,
 "pct": 21,
 "same_agency": false,
 "score": 6,
 "t": "National Forest",
 "verdict": "off"
}
```

## US-7280 Dardanelle Wildlife Management Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Dardanelle Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 57991,
  "manager": "",
  "pieces": [],
  "pin": "inside",
  "src": "water outline only",
  "unknown_pieces": 2
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "Wildlife Management Area",
 "verdict": "no size on page"
}
```

## US-9167 Lake Hinkle State Recreation Area
```json
{
 "checked": "2026-11-22",
 "handover": [
  {
   "date_hint": null,
   "kind": "managed by",
   "line": "e heart of the Ouachita National Forest. Lake Hinkle is one of Arkansas’s premier fishing lakes and is managed by the Arkansas Game and Fish Commission. Lake Hinkle camping units includes a table, tent/trailer pad, cooking grill, lantern post and parking spur. Restrooms w",
   "owner_now": "Arkansas Game and Fish Commission",
   "src": "https://lakeouachita.org/lake-hinkle/",
   "why": "the park's page (data/parkinfo)"
  }
 ],
 "n": "Lake Hinkle State Recreation Area",
 "official": {
  "acres": 960.0,
  "as": "960 acre",
  "clean": false,
  "line": "Ouachita National Forest Skip to content Main Menu Lake Hinkle In The Ouachita National Forest Lake Hinkle A 960-acre lake known for its largemouth bass, crappie and catfish. Lake Hinkle is in the heart of the Ouachita National",
  "read": "2026-11-22",
  "sent": "Lake Hinkle A 960-acre lake known for its largemouth bass, crappie and catfish.",
  "url": "https://lakeouachita.org/lake-hinkle/",
  "why": "part (a lake, a purchase, a campground…)"
 },
 "ours": {
  "acres": 0,
  "manager": "",
  "pieces": [],
  "pin": "inside",
  "src": "water outline only",
  "unknown_pieces": 1
 },
 "owner_now": "Arkansas Game and Fish Commission",
 "pct": null,
 "same_agency": false,
 "score": 7,
 "t": "State Recreation Area",
 "verdict": "ours unknown"
}
```

## US-10332 Plantation Agriculture Museum State Historical Park
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Plantation Agriculture Museum State Historical Park",
 "official": null,
 "ours": {
  "acres": 14,
  "manager": "",
  "pieces": [
   [
    "sgarb40",
    "Plantation Agriculture Museum State Park",
    14,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "State Historical Park",
 "verdict": "no size on page"
}
```

## US-12096 Great River Road National Scenic Byway National Historic Trail
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Great River Road National Scenic Byway National Historic Trail",
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
 "score": 4,
 "t": "National Historic Trail",
 "verdict": "ours unknown"
}
```

## US-10333 Arkansas Oak Natural Area
```json
{
 "cause": "a number 17 parks share from the same sentence (80,000 ac): an agency total, not this park",
 "checked": "2026-11-22",
 "handover": [],
 "n": "Arkansas Oak Natural Area",
 "official": null,
 "ours": {
  "acres": 202,
  "manager": "",
  "pieces": [
   [
    166728,
    "Arkansas Oak Natural Area",
    42,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": null,
 "same_agency": false,
 "score": 6,
 "t": "Natural Area",
 "verdict": "unsure"
}
```

## US-7187 Slippery Hollow State Natural Area
```json
{
 "checked": "2026-11-22",
 "handover": [],
 "n": "Slippery Hollow State Natural Area",
 "official": null,
 "ours": {
  "acres": 1416,
  "manager": "",
  "pieces": [
   [
    166758,
    "Slippery Hollow Natural Area",
    320,
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
 "t": "State Natural Area",
 "verdict": "no size on page"
}
```
