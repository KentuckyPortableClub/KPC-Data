# park truth checker: US-NV random sample of 12 (2026-11-09; seed = date + area, same rows for everyone)

Source file: `data/truth/US-NV.json`

## US-9266 Mount Charleston BLM Wilderness Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Mount Charleston BLM Wilderness Area",
 "official": {
  "acres": 56018.0,
  "as": "56,018 acres",
  "clean": true,
  "line": "es Drive Las Vegas, NV 89103 http://www.blm.gov/nv/st/en/fo/lvfo.1.html Southern Nevada District Office Size: 56,018 acres Elevation Range: 4,440 - 11,916 feet Designation: Clark County Conservation of Public Land and Natural Resou",
  "read": "2026-11-09",
  "sent": "Size: 56,018 acres",
  "url": "https://www.blm.gov/sites/blm.gov/files/uploads/Programs_NationalConservationLands_WildernessAreas_NV_Mt.%20Charleston%20Wilderness%20Fact%20Sheet%20Web%20Opt.pdf",
  "why": "clean total"
 },
 "ours": {
  "acres": 54881,
  "manager": "",
  "pieces": [
   [
    "wld324",
    "Mt. Charleston Wilderness",
    54881,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 2,
 "same_agency": false,
 "score": 8,
 "t": "Wilderness Area",
 "verdict": "agree"
}
```

## US-9248 Far South Egans Wilderness Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Far South Egans Wilderness Area",
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
 "score": 6,
 "t": "Wilderness Area",
 "verdict": "ours unknown"
}
```

## US-13409 Belmont Nevada State Historical Monument
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Belmont Nevada State Historical Monument",
 "official": null,
 "ours": {
  "acres": 2,
  "manager": "",
  "pieces": [
   [
    230124,
    "Belmont Courthouse State Historical Site",
    2,
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
 "t": "State Historical Monument",
 "verdict": "no size on page"
}
```

## US-13154 Illipah Reservoir BLM Recreation Management Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Illipah Reservoir BLM Recreation Management Area",
 "official": null,
 "ours": {
  "acres": 42,
  "dissolved": {
   "after": 116,
   "before": 232,
   "copies": 1,
   "key_union": 42,
   "parts": 0,
   "records": 2,
   "summed": 116,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 232 -> 116 acres",
  "pieces": [
   [
    "rma9762",
    "Ilipah Reservoir Recreation Area",
    116,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 5,
 "t": "BLM Recreation Management Area",
 "verdict": "no size on page"
}
```

## US-4446 Wild Horse State Recreation Area
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 32 acre, no total words near it)",
 "checked": "2026-11-09",
 "handover": [],
 "n": "Wild Horse State Recreation Area",
 "official": {
  "acres": 32.0,
  "as": "32 acre",
  "clean": false,
  "line": "g Creek, Nevada Amenities View Description Full Park Detail Cave Lake A year-round park, Cave Lake features a 32-acre reservoir that provides excellent trout fishing, boating, swimming, hiking and camping. Winter activities inc",
  "read": "2026-11-09",
  "sent": "A year-round park, Cave Lake features a 32-acre reservoir that provides excellent trout fishing, boating, swimming, hiking and camping.",
  "url": "http://parks.nv.gov/parks/wild-horse",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 11714,
  "dissolved": {
   "after": 12400,
   "before": 12600,
   "copies": 2,
   "key_union": 11714,
   "parts": 0,
   "records": 5,
   "summed": 12400,
   "tracts": 3
  },
  "manager": "",
  "note": "5 joined records = 3 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 12600 -> 12400 acres",
  "pieces": [
   [
    "sgakg9802",
    "Wild Horse Reservoir",
    12200,
    "name"
   ],
   [
    230210,
    "Wild Horse Reservoir State Recreation Area",
    120,
    "name"
   ],
   [
    "sgnvb34",
    "Wild Horse Reservoir Recreation Area",
    80,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 36506,
 "same_agency": false,
 "score": 7,
 "t": "State Recreation Area",
 "verdict": "unsure"
}
```

## US-4458 Lake Tahoe Basin Management Unit National Forest
```json
{
 "cause": "whole park compared (POTA lists it in 2 states: {'US-CA': 121320, 'US-NV': 331807})",
 "checked": "2026-11-09",
 "handover": [],
 "n": "Lake Tahoe Basin Management Unit National Forest",
 "note": "whole park compared (POTA lists it in 2 states: {'US-CA': 121320, 'US-NV': 331807})",
 "official": null,
 "ours": {
  "acres": 453127,
  "acres_by_state": {
   "US-CA": 121320,
   "US-NV": 331807
  },
  "family_fold": "layers {'sgnvg': 331807, 'padus': 33859}: one land in 2 layers, the sgnvg copy used (33,859 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgnvg67",
    "Lake Tahoe Basin Management Unit",
    331807,
    "reviewed"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "states": [
   "US-CA",
   "US-NV"
  ],
  "unknown_pieces": 0,
  "whole_park": true
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "National Forest",
 "verdict": "unsure"
}
```

## US-13113 Wheeler Pass BLM Herd Management Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Wheeler Pass BLM Herd Management Area",
 "official": {
  "acres": 275575.0,
  "as": "275,575 acres",
  "clean": false,
  "line": "nsists of 273,898 acres of BLM land and 1,677 acres of a mix of private and other public lands for a total of 275,575 acres. AML: 47-66 wild horses and 20-35 wild burros",
  "read": "2026-11-09",
  "sent": "Size: The area consists of 273,898 acres of BLM land and 1,677 acres of a mix of private and other public lands for a total of 275,575 acres.",
  "url": "https://www.blm.gov/programs/wild-horse-and-burro/herd-management/herd-management-areas/nevada/wheeler-pass",
  "why": "total-looking"
 },
 "ours": {
  "acres": 275980,
  "dissolved": {
   "after": 275980,
   "before": 551960,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 551960 -> 275980 acres",
  "pieces": [
   [
    "hma100",
    "Wheeler Pass",
    275980,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 0,
 "same_agency": false,
 "score": 8,
 "t": "BLM Herd Management Area",
 "verdict": "agree"
}
```

## US-13177 Rhyolite Historic Area-Nevada BLM Historic Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Rhyolite Historic Area-Nevada BLM Historic Area",
 "official": null,
 "ours": {
  "acres": 446,
  "dissolved": {
   "after": 342,
   "before": 684,
   "copies": 1,
   "key_union": 446,
   "parts": 0,
   "records": 2,
   "summed": 342,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 684 -> 342 acres",
  "pieces": [
   [
    "rst9584",
    "Rhyolite Historic Townsite",
    342,
    "reviewed"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "BLM Historic Area",
 "verdict": "no size on page"
}
```

## US-13222 Shooting Gallery BLM Historic Preservation Site
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Shooting Gallery BLM Historic Preservation Site",
 "official": null,
 "ours": {
  "acres": 15603,
  "manager": "",
  "pieces": [
   [
    "sgakh1243",
    "Shooting Gallery",
    15603,
    "reviewed"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "BLM Historic Preservation Site",
 "verdict": "no size on page"
}
```

## US-4441 Lahontan State Recreation Area
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Lahontan State Recreation Area",
 "official": {
  "acres": 30000.0,
  "as": "30,000 acres",
  "clean": false,
  "line": "Carson River Basins to irrigate lands near the town of Fallon and to produce hydroelectric power. Today about 30,000 acres are irrigated from the reservoir; depending on the snow pack. Drainage water from the irrigated lands flows i",
  "read": "2026-11-09",
  "sent": "Today about 30,000 acres are irrigated from the reservoir;",
  "url": "http://parks.nv.gov/parks/lahontan",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 28890,
  "dissolved": {
   "after": 30866,
   "before": 88645,
   "copies": 2,
   "families": {
    "padus": 1976,
    "sgnvb": 28890
   },
   "family_fold": 1976,
   "family_used": "sgnvb",
   "parts": 0,
   "records": 4,
   "tracts": 2
  },
  "family_fold": "layers {'sgnvb': 28890, 'padus': 1976}: one land in 2 layers, the sgnvb copy used (1,976 ac of copies not added)",
  "manager": "",
  "note": "4 joined records = 2 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 88645 -> 30866 acres",
  "pieces": [
   [
    "sgnvb23",
    "Lake Lahontan Recreation Area",
    28890,
    "words"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 4,
 "same_agency": false,
 "score": 7,
 "t": "State Recreation Area",
 "verdict": "agree"
}
```

## US-2627 Cathedral Gorge State Park
```json
{
 "checked": "2026-11-09",
 "handover": [],
 "n": "Cathedral Gorge State Park",
 "official": {
  "acres": 2000.0,
  "as": "2,000 acres",
  "clean": false,
  "line": "of Cathedral Gorge. ( READ MORE ) HISTORY OF CATHEDRAL GORGE STATE PARK &ndash; Established in 1935 Close to 2,000 acres of land that was once home to the Fremont, Anasazi and Southern Paiutes is now a state park preserved for vis",
  "read": "2026-11-09",
  "sent": "Close to 2,000 acres of land that was once home to the Fremont, Anasazi and Southern Paiutes is now a state park preserved for visitors to experience and enjoy.",
  "url": "http://parks.nv.gov/parks/cathedral-gorge",
  "why": "history"
 },
 "ours": {
  "acres": 1757,
  "dissolved": {
   "after": 3388,
   "before": 6901,
   "copies": 2,
   "families": {
    "padus": 1631,
    "sgnvb": 1757
   },
   "family_fold": 1631,
   "family_used": "sgnvb",
   "parts": 0,
   "records": 4,
   "tracts": 2
  },
  "family_fold": "layers {'sgnvb': 1757, 'padus': 1631}: one land in 2 layers, the sgnvb copy used (1,631 ac of copies not added)",
  "manager": "",
  "note": "4 joined records = 2 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 6901 -> 3388 acres",
  "pieces": [
   [
    "sgnvb18",
    "Cathedral Gorge State Park",
    1757,
    "reviewed"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 12,
 "same_agency": false,
 "score": 8,
 "t": "State Park",
 "verdict": "agree"
}
```

## US-13014 Granite Peak BLM Herd Management Area
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-09",
 "handover": [],
 "n": "Granite Peak BLM Herd Management Area",
 "official": {
  "acres": 3981.0,
  "as": "3,981 acres",
  "clean": false,
  "line": "Search Search Twitter YouTube Facebook Instagram Flickr LinkedIn Granite Peak HMA Size: The area consists of 3,981 acres of BLM land and 20 acres of a mix of private and other public lands for a total of 4,001 acres. AML: 11-18",
  "read": "2026-11-09",
  "sent": "Size: The area consists of 3,981 acres of BLM land and 20 acres of a mix of private and other public lands for a total of 4,001 acres.",
  "url": "https://www.blm.gov/programs/wild-horse-and-burro/herd-management/herd-management-areas/nevada/granite-peak",
  "why": "total-looking"
 },
 "ours": {
  "acres": 2917,
  "dissolved": {
   "after": 4053,
   "before": 8106,
   "copies": 1,
   "key_union": 2917,
   "parts": 0,
   "records": 2,
   "summed": 4053,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 8106 -> 4053 acres",
  "pieces": [
   [
    "hma77",
    "Granite Peak",
    4053,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 27,
 "same_agency": false,
 "score": 6,
 "t": "BLM Herd Management Area",
 "verdict": "off"
}
```
