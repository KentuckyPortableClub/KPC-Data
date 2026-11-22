# park truth checker: US-IN random sample of 12 (2026-11-22; seed = date + area, same rows for everyone)

Source file: `data/truth/US-IN.json`

## US-6969 Corydon Capitol State Historic Site
```json
{
 "checked": "2026-11-15",
 "handover": [],
 "n": "Corydon Capitol State Historic Site",
 "official": null,
 "ours": {
  "acres": 4,
  "manager": "",
  "pieces": [
   [
    157071,
    "Corydon Capitol State Historic Site",
    4,
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

## US-12011 Falling Timber State Nature Preserve
```json
{
 "cause": "our union: one of our pieces alone matches the agency (double count?)",
 "checked": "2026-11-15",
 "handover": [],
 "n": "Falling Timber State Nature Preserve",
 "official": {
  "acres": 109.0,
  "as": "109 acres",
  "clean": true,
  "line": "Falling Timber Nature Preserve County: Ripley Size: 109 acres Ownership: State Parks - IDNR Location and Access Parking and trail. Falling Timber is located within",
  "read": "2026-11-15",
  "sent": "County: Ripley Size: 109 acres",
  "url": "https://www.in.gov/dnr/nature-preserves/files/Falling_Timber-color.pdf",
  "why": "clean total"
 },
 "ours": {
  "acres": 195,
  "manager": "",
  "pieces": [
   [
    201061,
    "Falling Timber Nature Preserve (Falling Timber)",
    106,
    "name"
   ],
   [
    201062,
    "Falling Timber Nature Preserve (Henderson Bend)",
    72,
    "name"
   ],
   [
    201063,
    "Falling Timber Nature Preserve (High Bluff)",
    17,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 79,
 "same_agency": false,
 "score": 5,
 "t": "State Nature Preserve",
 "verdict": "off"
}
```

## US-12017 Marsh Lake State Nature Preserve
```json
{
 "checked": "2026-11-15",
 "handover": [],
 "n": "Marsh Lake State Nature Preserve",
 "official": {
  "acres": 103.0,
  "as": "103 acres",
  "clean": true,
  "line": "Marsh Lake Nature Preserve County: Steuben Size: 103 acres Ownership: Fish and Wildlife - IDNR Location and Access Parking. No trails. Caution is advised since hu",
  "read": "2026-11-15",
  "sent": "County: Steuben Size: 103 acres",
  "url": "https://www.in.gov/dnr/nature-preserves/files/np-Marsh_Lake.pdf",
  "why": "clean total"
 },
 "ours": {
  "acres": 102,
  "manager": "",
  "pieces": [
   [
    200895,
    "Marsh Lake Nature Preserve",
    102,
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
 "t": "State Nature Preserve",
 "verdict": "agree"
}
```

## US-4168 Frances Slocum on Mississinewa Lake State Recreation Area
```json
{
 "checked": "2026-11-15",
 "handover": [],
 "n": "Frances Slocum on Mississinewa Lake State Recreation Area",
 "official": {
  "acres": 14386.0,
  "as": "14,386 acres",
  "clean": false,
  "line": "ore at www.indianabirdingtrail.com . Miami SRA, Red Bridge SRA w/marina, Frances Slocum SRA, Pearson Mill SRA 14,386 acres - 3,210-acre lake Mississinewa Lake, one of the three Upper Wabash flood-control reservoirs, offers excellent",
  "read": "2026-11-15",
  "sent": "14,386 acres - 3,210-acre lake",
  "url": "https://www.in.gov/dnr/state-parks/parks-lakes/mississinewa-lake/",
  "why": "part (a lake, a purchase, a campground…)"
 },
 "ours": {
  "acres": 15067,
  "manager": "",
  "pieces": [
   [
    2526,
    "Mississinewa Recreation Area",
    15067,
    "reviewed-approx"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 5,
 "same_agency": false,
 "score": 6,
 "t": "State Recreation Area",
 "verdict": "agree"
}
```

## US-12013 Kramer Original Woods State Nature Preserve
```json
{
 "checked": "2026-11-15",
 "handover": [],
 "n": "Kramer Original Woods State Nature Preserve",
 "official": {
  "acres": 220.0,
  "as": "220 acres",
  "clean": true,
  "line": "Kramer Original Woods Nature Preserve ● (Henry Kramer) Count y: Spencer Size: 220 acres Ownership: Nature Preserves - IDNR Location and Access Park along road. No trail. The community of Reo in",
  "read": "2026-11-15",
  "sent": "y: Spencer Size: 220 acres",
  "url": "https://www.in.gov/dnr/nature-preserves/files/np-Kramer_Original_Woods.pdf",
  "why": "clean total"
 },
 "ours": {
  "acres": 225,
  "dissolved": {
   "after": 225,
   "before": 675,
   "copies": 4,
   "parts": 0,
   "records": 6,
   "tracts": 2
  },
  "manager": "",
  "note": "6 joined records = 2 tracts: 4 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 675 -> 225 acres",
  "pieces": [
   [
    "sginb4243",
    "Kramer Woods",
    221,
    "reviewed"
   ],
   [
    "sginb4242",
    "Kramer Woods",
    4,
    "reviewed"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 2,
 "same_agency": false,
 "score": 7,
 "t": "State Nature Preserve",
 "verdict": "agree"
}
```

## US-4197 Fairbanks Landing State Fish and Wildlife Area
```json
{
 "cause": "our union: one of our pieces alone matches the agency (double count?)",
 "checked": "2026-11-15",
 "handover": [
  {
   "date_hint": "2010",
   "kind": "transfer",
   "line": "asses and agriculture in Putnam County. The land that compromises most of Deer Creek was originally transferred from the Putnamville Correctional Facility to the DNR in 2010 and several more parcels have been bought since then. It is open to the public and hunting, fishing, trapping, and other outdo",
   "owner_now": "Putnamville Correctional Facility",
   "src": "https://www.in.gov/dnr/fish-and-wildlife/properties/fairbanks-landing-fwa/",
   "why": "the park's page (data/parkinfo)"
  }
 ],
 "n": "Fairbanks Landing State Fish and Wildlife Area",
 "official": {
  "acres": 5253.0,
  "as": "5,253 acres",
  "clean": false,
  "line": "Fish & Wildlife Area (FWA) in Vigo and Sullivan counties provides quality outdoor recreation opportunities on 5,253 acres of bottomland hardwoods, prairie, and riparian habitat. Fairbanks Landing FWA rests along the Wabash River an",
  "read": "2026-11-15",
  "sent": "Fairbanks Landing Fish & Wildlife Area (FWA) in Vigo and Sullivan counties provides quality outdoor recreation opportunities on 5,253 acres of bottomland hardwoods, prairie, and riparian habitat.",
  "url": "https://www.in.gov/dnr/fish-and-wildlife/properties/fairbanks-landing-fwa/",
  "why": "total-looking"
 },
 "ours": {
  "acres": 8259,
  "dissolved": {
   "after": 8259,
   "before": 16477,
   "copies": 2,
   "parts": 0,
   "records": 5,
   "tracts": 3
  },
  "manager": "",
  "note": "5 joined records = 3 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 16477 -> 8259 acres",
  "pieces": [
   [
    "ind3591",
    "Fairbanks Landing Fish And Wildlife Area",
    5610,
    "name"
   ],
   [
    "ind3590",
    "Fairbanks Landing Fish And Wildlife Area",
    2608,
    "name"
   ],
   [
    78817,
    "Fairbanks Landing Pas",
    41,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": "Putnamville Correctional Facility",
 "pct": 57,
 "same_agency": false,
 "score": 6,
 "t": "State Fish and Wildlife Area",
 "verdict": "off"
}
```

## US-12002 Williams Dam State Fishing Lake
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-22",
 "n": "Williams Dam State Fishing Lake",
 "official": null,
 "ours": {
  "acres": 27,
  "dissolved": {
   "after": 38,
   "before": 76,
   "copies": 1,
   "key_union": 27,
   "parts": 0,
   "records": 2,
   "summed": 38,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 76 -> 38 acres",
  "pieces": [
   [
    201045,
    "Williams Dam Public Fishing Area",
    38,
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
 "t": "State Fishing Lake",
 "verdict": "no size on page"
}
```

## US-4227 Splinter Ridge State Fish and Wildlife Area
```json
{
 "checked": "2026-11-15",
 "handover": [],
 "n": "Splinter Ridge State Fish and Wildlife Area",
 "official": {
  "acres": 3014.0,
  "as": "3,014 acres",
  "clean": false,
  "line": "escription Splinter Ridge Fish & Wildlife Area (FWA) provides quality hunting opportunities while maintaining 3,014 acres of woodland and steep hills. The Splinter Ridge Fish & Wildlife Area, named after the major ridge and histori",
  "read": "2026-11-15",
  "sent": "Splinter Ridge Fish & Wildlife Area (FWA) provides quality hunting opportunities while maintaining 3,014 acres of woodland and steep hills.",
  "url": "https://www.in.gov/dnr/fish-and-wildlife/properties/splinter-ridge-fwa/",
  "why": "total-looking"
 },
 "ours": {
  "acres": 2990,
  "family_fold": "layers {'sgina': 2990, 'padus': 2546}: one land in 2 layers, the sgina copy used (2,546 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgina5204",
    "Splinter Ridge Fish And Wildlife Area",
    2990,
    "reviewed"
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
 "t": "State Fish and Wildlife Area",
 "verdict": "agree"
}
```

## US-4215 Morgan-Monroe State Forest
```json
{
 "checked": "2026-11-15",
 "handover": [],
 "n": "Morgan-Monroe State Forest",
 "official": {
  "acres": 24515.5,
  "as": "24,515.5 acres",
  "clean": true,
  "line": "h Dec. 1, weather permitting, and April 15 through May 30. Description Morgan-Monroe State Forest encompasses 24,515.5 acres in Morgan and Monroe counties in south-central Indiana, featuring many steep ridges and valleys as well as so",
  "read": "2026-11-15",
  "sent": "Morgan-Monroe State Forest encompasses 24,515.5 acres in Morgan and Monroe counties in south-central Indiana, featuring many steep ridges and valleys as well as some of the state's finest hardwoods.",
  "url": "https://www.in.gov/dnr/forestry/properties/morgan-monroe-state-forest/",
  "why": "clean total"
 },
 "ours": {
  "acres": 26474,
  "family_fold": "layers {'padus': 25199, 'sgina': 24439}: one land in 2 layers, the padus copy used (24,439 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    200710,
    "Morgan - Monroe State Forest",
    25199,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 8,
 "same_agency": false,
 "score": 8,
 "t": "State Forest",
 "verdict": "agree"
}
```

## US-4172 Jackson on Patoka Lake State Recreation Area
```json
{
 "checked": "2026-11-15",
 "handover": [],
 "n": "Jackson on Patoka Lake State Recreation Area",
 "official": {
  "acres": 25800.0,
  "as": "25,800 acres",
  "clean": false,
  "line": "t SRA, Jackson SRA, Lick Fork SRA, Little Patoka SRA, Painter Creek SRA, Walls Lake SRA, South Lick Fork SRA. 25,800 acres - 8,800-acre lake With nearly 26,000 acres of land and water, Patoka Lake is a fine example of lake ecology.",
  "read": "2026-11-15",
  "sent": "25,800 acres - 8,800-acre lake",
  "url": "https://www.in.gov/dnr/state-parks/parks-lakes/patoka-lake/",
  "why": "part (a lake, a purchase, a campground…)"
 },
 "ours": {
  "acres": 26122,
  "manager": "",
  "pieces": [
   [
    "ind4773",
    "Patoka Lake",
    26122,
    "reviewed-approx"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 1,
 "same_agency": false,
 "score": 8,
 "t": "State Recreation Area",
 "verdict": "agree"
}
```

## US-10235 Greider's Woods State Nature Preserve
```json
{
 "checked": "2026-11-15",
 "handover": [],
 "n": "Greider's Woods State Nature Preserve",
 "official": {
  "acres": 10.0,
  "as": "10 acres",
  "clean": true,
  "line": "Greider’s Woods Nature Preserve County: Kosciusko Size: 10 acres Ownership: Fish and Wildlife - IDNR Location and Access Parking and trail. Visitors are advised to check",
  "read": "2026-11-15",
  "sent": "County: Kosciusko Size: 10 acres",
  "url": "https://www.in.gov/dnr/nature-preserves/files/np-Greiders.pdf",
  "why": "clean total"
 },
 "ours": {
  "acres": 10,
  "manager": "",
  "pieces": [
   [
    200893,
    "Greider's Woods Nature Preserve",
    10,
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
 "t": "State Nature Preserve",
 "verdict": "agree"
}
```

## US-5682 Moores Creek State Recreation Area
```json
{
 "checked": "2026-11-15",
 "handover": [],
 "n": "Moores Creek State Recreation Area",
 "official": null,
 "ours": {
  "acres": 155,
  "manager": "",
  "pieces": [
   [
    "sginc4577",
    "Moore's Creek State Recreation Area (Monroe Lake)",
    155,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "State Recreation Area",
 "verdict": "no size on page"
}
```
