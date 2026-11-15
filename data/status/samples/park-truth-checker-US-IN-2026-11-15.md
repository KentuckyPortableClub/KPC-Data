# park truth checker: US-IN random sample of 12 (2026-11-15; seed = date + area, same rows for everyone)

Source file: `data/truth/US-IN.json`

## US-5688 Salt Creek State Recreation Area
```json
{
 "checked": "2026-11-15",
 "handover": [],
 "n": "Salt Creek State Recreation Area",
 "official": null,
 "ours": {
  "acres": 313,
  "manager": "",
  "pieces": [
   [
    "sginc4580",
    "Salt Creek State Recreation Area (Monroe Lake)",
    313,
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

## US-0734 George Rogers Clark National Historical Park
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "last_read_failed": "2026-11-15",
 "n": "George Rogers Clark National Historical Park",
 "official": null,
 "ours": {
  "acres": 24,
  "manager": "",
  "pieces": [
   [
    3203,
    "George Rogers Clark National Historical Park",
    24,
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
 "t": "National Historical Park",
 "verdict": "no size on page"
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

## US-5693 Cataract Falls State Recreation Area
```json
{
 "checked": "2026-11-15",
 "handover": [],
 "n": "Cataract Falls State Recreation Area",
 "official": null,
 "ours": {
  "acres": 250,
  "family_fold": "layers {'sginc': 250, 'padus': 221}: one land in 2 layers, the sginc copy used (221 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sginc3225",
    "Cataract Falls State Recreation Area (Cagles Mill Lake)",
    250,
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
 "t": "State Recreation Area",
 "verdict": "no size on page"
}
```

## US-12005 Rocky Hollow-Falls Canyon State Nature Preserve
```json
{
 "checked": "2026-11-15",
 "handover": [],
 "n": "Rocky Hollow-Falls Canyon State Nature Preserve",
 "official": {
  "acres": 1609.0,
  "as": "1609 acres",
  "clean": true,
  "line": "Rocky Hollow-Falls Canyon Nature Preserve County: Parke Size: 1609 acres Ownership: State Parks - IDNR Location and Access Parking and trails. This preserve lies on the north si",
  "read": "2026-11-15",
  "sent": "County: Parke Size: 1609 acres",
  "url": "https://www.in.gov/dnr/nature-preserves/files/np-Rocky_Hollow-color.pdf",
  "why": "clean total"
 },
 "ours": {
  "acres": 1452,
  "manager": "",
  "pieces": [
   [
    201081,
    "Rocky Hollow-Falls Canyon Nature Preserve",
    1452,
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
 "score": 7,
 "t": "State Nature Preserve",
 "verdict": "agree"
}
```

## US-10248 Warbler Woods State Nature Preserve
```json
{
 "checked": "2026-11-15",
 "handover": [],
 "n": "Warbler Woods State Nature Preserve",
 "official": {
  "acres": 136.0,
  "as": "136 acres",
  "clean": true,
  "line": "Warbler Woods Nature Preserve County: Marion Size: 136 acres Ownership: State Parks - IDNR ● Location and Access Parking and trail. In Fort Harrison State Park. From",
  "read": "2026-11-15",
  "sent": "County: Marion Size: 136 acres",
  "url": "https://www.in.gov/dnr/nature-preserves/files/np-Warbler_Woods.pdf",
  "why": "clean total"
 },
 "ours": {
  "acres": 136,
  "manager": "",
  "pieces": [
   [
    201087,
    "WarblerWoods Nature Preserve",
    136,
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
 "score": 6,
 "t": "State Nature Preserve",
 "verdict": "agree"
}
```

## US-12312 Busseron Creek State Fish and Wildlife Area
```json
{
 "checked": "2026-11-15",
 "handover": [
  {
   "date_hint": "2020",
   "kind": "transfer",
   "line": "oxbow lake bordering the West Fork of the White River in southwestern Greene County. In 2020, INDOT transferred the property to the DNR Division of Fish & Wildlife, and restoration work was completed as part of Interstate 69 mitigation. The property provides excellent hunting opportunities for deer,",
   "owner_now": "DNR Division of Fish & Wildlife",
   "src": "https://www.in.gov/dnr/fish-and-wildlife/properties/busseron-creek-fish-and-wildlife-area/",
   "why": "the park's page (data/parkinfo)"
  }
 ],
 "n": "Busseron Creek State Fish and Wildlife Area",
 "official": {
  "acres": 3950.0,
  "as": "3,950 acres",
  "clean": false,
  "line": "on Creek Fish & Wildlife Area (FWA) in Sullivan County provides quality outdoor recreational opportunities on 3,950 acres of bottomland forest, marshland, and upland habitats. The property is a popular destination for hunting, fora",
  "read": "2026-11-15",
  "sent": "Busseron Creek Fish & Wildlife Area (FWA) in Sullivan County provides quality outdoor recreational opportunities on 3,950 acres of bottomland forest, marshland, and upland habitats.",
  "url": "https://www.in.gov/dnr/fish-and-wildlife/properties/busseron-creek-fish-and-wildlife-area/",
  "why": "total-looking"
 },
 "ours": {
  "acres": 3950,
  "dissolved": {
   "after": 3950,
   "before": 7900,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 7900 -> 3950 acres",
  "pieces": [
   [
    "ind5689",
    "Busseron Creek Fish and Wildlife Area",
    3950,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": "DNR Division of Fish & Wildlife",
 "pct": 0,
 "same_agency": false,
 "score": 8,
 "t": "State Fish and Wildlife Area",
 "verdict": "agree"
}
```

## US-13104 Three Rivers State Fishing Lake
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-15",
 "n": "Three Rivers State Fishing Lake",
 "official": null,
 "ours": {
  "acres": 9,
  "manager": "",
  "pieces": [
   [
    "sgina5342",
    "Three Rivers Public Fishing Area",
    9,
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
 "t": "State Fishing Lake",
 "verdict": "no size on page"
}
```

## US-4232 Wilbur Wright State Fish and Wildlife Area
```json
{
 "checked": "2026-11-15",
 "handover": [
  {
   "date_hint": "1974",
   "kind": "transfer",
   "line": ", originally part of the Indiana Department of Mental Health&rsquo;s New Castle State Hospital, was transferred to the DNR Division of State Parks. In 1974, the property was reassigned to the DNR Division of Fish & Wildlife, marking the beginning of active wildlife management. At that time, efforts ",
   "owner_now": "DNR Division of State Parks",
   "src": "https://www.in.gov/dnr/fish-and-wildlife/properties/wilbur-wright-fwa/",
   "why": "the park's page (data/parkinfo)"
  }
 ],
 "n": "Wilbur Wright State Fish and Wildlife Area",
 "official": {
  "acres": 1070.0,
  "as": "1,070 acres",
  "clean": false,
  "line": "lly if there is a draw. Please call property for questions. Description Wilbur Wright Fish & Wildlife Area is 1,070 acres of river valleys and associated uplands in Henry County. The Big Blue River is the western boundary, and the",
  "read": "2026-11-15",
  "sent": "Wilbur Wright Fish & Wildlife Area is 1,070 acres of river valleys and associated uplands in Henry County.",
  "url": "https://www.in.gov/dnr/fish-and-wildlife/properties/wilbur-wright-fwa/",
  "why": "total-looking"
 },
 "ours": {
  "acres": 1038,
  "dissolved": {
   "after": 1038,
   "before": 2073,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 2073 -> 1038 acres",
  "pieces": [
   [
    200948,
    "Wilbur Wright Fish And Wildlife Area",
    1038,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": "DNR Division of State Parks",
 "pct": 3,
 "same_agency": false,
 "score": 8,
 "t": "State Fish and Wildlife Area",
 "verdict": "agree"
}
```

## US-12025 Goose Creek State Game Land
```json
{
 "checked": "2026-11-15",
 "handover": [],
 "n": "Goose Creek State Game Land",
 "official": {
  "acres": 375.0,
  "as": "375 acre",
  "clean": false,
  "line": "Goose Creek Game Bird Area Benton County, Indiana Go ose Creek Game Bird Area is a 375-acre property. It was purchased by the Division of Fish & Wildlife in 2015 using a combination of funding sources",
  "read": "2026-11-15",
  "sent": "ose Creek Game Bird Area is a 375-acre property.",
  "url": "https://www.in.gov/dnr/fish-and-wildlife/files/fw-gba-goosecreek.pdf",
  "why": "a map label (no sentence)"
 },
 "ours": {
  "acres": 376,
  "manager": "",
  "pieces": [
   [
    "sgina3804",
    "Goose Creek Gamebird Habitat Area",
    376,
    "words"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 0,
 "same_agency": false,
 "score": 7,
 "t": "State Game Land",
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

## US-2252 Chain O' Lakes State Park
```json
{
 "checked": "2026-11-15",
 "handover": [],
 "n": "Chain O' Lakes State Park",
 "official": null,
 "ours": {
  "acres": 2974,
  "dissolved": {
   "after": 2951,
   "before": 8105,
   "copies": 3,
   "families": {
    "padus": 2215,
    "sgina": 736
   },
   "family_fold": 736,
   "family_used": "padus",
   "key_union": 2974,
   "parts": 0,
   "records": 5,
   "summed": 2215,
   "tracts": 2
  },
  "family_fold": "layers {'padus': 2215, 'sgina': 736}: one land in 2 layers, the padus copy used (736 ac of copies not added)",
  "manager": "",
  "note": "5 joined records = 2 tracts: 3 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 8105 -> 2951 acres",
  "pieces": [
   [
    201093,
    "Chain O' Lakes State Park",
    2215,
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
