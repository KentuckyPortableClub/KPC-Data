# park truth checker: US-IN random sample of 12 (2026-11-01; seed = date + area, same rows for everyone)

Source file: `data/truth/US-IN.json`

## US-6971 Gene Stratton-Porter State Historic Site
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 148 acres, no total words near it)",
 "checked": "2026-11-01",
 "handover": [],
 "n": "Gene Stratton-Porter State Historic Site",
 "official": {
  "acres": 148.0,
  "as": "148 acres",
  "clean": false,
  "line": "wers out from a large cabinet to see different types of rocks and wildlife found throughout Indiana. Relax in 148 acres of loveliness Newly recognized as part of the Old-Growth Forest Network , the Gene Stratton-Porter State Hist",
  "read": "2026-11-01",
  "sent": "Relax in 148 acres of loveliness",
  "url": "https://www.indianamuseum.org/historic-sites/gene-stratton-porter/",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 111,
  "manager": "",
  "pieces": [
   [
    200677,
    "Gene Stratton Porter State Historic Site",
    111,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 25,
 "same_agency": false,
 "score": 5,
 "t": "State Historic Site",
 "verdict": "unsure"
}
```

## US-2258 Indiana Dunes State Park
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Indiana Dunes State Park",
 "official": {
  "acres": 2182.0,
  "as": "2,182 acres",
  "clean": true,
  "line": "cription This property is a stop on the Learn more at www.indianabirdingtrail.com . Indiana Dunes consists of 2,182 acres of primitive, beautiful, historic, and unique Hoosier landscape. It lies at the north end of State Road 49 in",
  "read": "2026-11-01",
  "sent": "Indiana Dunes consists of 2,182 acres of primitive, beautiful, historic, and unique Hoosier landscape.",
  "url": "https://www.in.gov/dnr/state-parks/parks-lakes/indiana-dunes-state-park/",
  "why": "clean total"
 },
 "ours": {
  "acres": 2145,
  "dissolved": {
   "after": 2208,
   "before": 2766,
   "copies": 1,
   "families": {
    "padus": 558,
    "sgina": 1650
   },
   "family_fold": 558,
   "family_used": "sgina",
   "key_union": 2145,
   "parts": 0,
   "records": 4,
   "summed": 1650,
   "tracts": 3
  },
  "family_fold": "layers {'sgina': 1650, 'padus': 558}: one land in 2 layers, the sgina copy used (558 ac of copies not added)",
  "manager": "",
  "note": "4 joined records = 3 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 2766 -> 2208 acres",
  "pieces": [
   [
    "sgina4049",
    "Indiana Dunes State Park",
    1591,
    "name"
   ],
   [
    "sgina4050",
    "Indiana Dunes State Park",
    59,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 2,
 "same_agency": false,
 "score": 8,
 "t": "State Park",
 "verdict": "agree"
}
```

## US-4213 LaSalle State Fish and Wildlife Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "LaSalle State Fish and Wildlife Area",
 "official": {
  "acres": 4511.0,
  "as": "4,511 acres",
  "clean": false,
  "line": "escription LaSalle Fish & Wildlife Area provides quality outdoor recreational opportunities while maintaining 4,511 acres of hardwood forests, cropland and fallow fields, marshes, and open water. The property is dominated by wetlan",
  "read": "2026-11-01",
  "sent": "LaSalle Fish & Wildlife Area provides quality outdoor recreational opportunities while maintaining 4,511 acres of hardwood forests, cropland and fallow fields, marshes, and open water.",
  "url": "https://www.in.gov/dnr/fish-and-wildlife/properties/lasalle-fwa/",
  "why": "part (a lake, a purchase, a campground…)"
 },
 "ours": {
  "acres": 4545,
  "dissolved": {
   "after": 4502,
   "before": 8951,
   "copies": 2,
   "families": {
    "ind": 597,
    "padus": 3,
    "sgina": 3902
   },
   "family_fold": 600,
   "family_used": "sgina",
   "key_union": 4545,
   "parts": 0,
   "records": 5,
   "summed": 3902,
   "tracts": 3
  },
  "family_fold": "layers {'sgina': 3902, 'ind': 597, 'padus': 3}: one land in 3 layers, the sgina copy used (600 ac of copies not added)",
  "manager": "",
  "note": "5 joined records = 3 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 8951 -> 4502 acres",
  "pieces": [
   [
    "sgina4294",
    "Lasalle Fish And Wildlife Area",
    3902,
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
 "t": "State Fish and Wildlife Area",
 "verdict": "agree"
}
```

## US-10404 Galena Wetland Conservation Area
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-11-01",
 "handover": [],
 "n": "Galena Wetland Conservation Area",
 "official": null,
 "ours": {
  "acres": 102,
  "dissolved": {
   "after": 121,
   "before": 363,
   "copies": 2,
   "key_union": 102,
   "parts": 0,
   "records": 3,
   "summed": 121,
   "tracts": 1
  },
  "manager": "",
  "note": "3 joined records = 1 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 363 -> 121 acres",
  "pieces": [
   [
    200854,
    "Galena (Springfield Fen) Wetland Conservation Area",
    121,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 4,
 "t": "Conservation Area",
 "verdict": "unsure"
}
```

## US-4225 Selmier State Forest
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-01",
 "handover": [],
 "n": "Selmier State Forest",
 "official": {
  "acres": 355.0,
  "as": "355 acres",
  "clean": false,
  "line": ". Description Selmier State Forest is two miles northeast of North Vernon on County Road 350 North. There are 355 acres of multi-use woods with hiking trails and access to the Muscatatuck River. The property is open daily, sunris",
  "read": "2026-11-01",
  "sent": "There are 355 acres of multi-use woods with hiking trails and",
  "url": "https://www.in.gov/dnr/forestry/properties/selmier-state-forest/",
  "why": "total-looking"
 },
 "ours": {
  "acres": 291,
  "dissolved": {
   "after": 351,
   "before": 701,
   "copies": 1,
   "key_union": 291,
   "parts": 0,
   "records": 2,
   "summed": 351,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 701 -> 351 acres",
  "pieces": [
   [
    200713,
    "Selmier State Forest",
    351,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 18,
 "same_agency": false,
 "score": 6,
 "t": "State Forest",
 "verdict": "off"
}
```

## US-2251 Brown County State Park
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Brown County State Park",
 "official": {
  "acres": 16000.0,
  "as": "16,000 acres",
  "clean": false,
  "line": "&rdquo; because of the area&rsquo;s resemblance to the Great Smoky Mountains, Brown County encompasses nearly 16,000 acres of rugged hills, ridges, and fog-shrouded ravines. Glaciers from the most recent ice ages stopped short of th",
  "read": "2026-11-01",
  "sent": "because of the area&rsquo;s resemblance to the Great Smoky Mountains, Brown County encompasses nearly 16,000 acres of rugged hills, ridges, and fog-shrouded ravines.",
  "url": "https://www.in.gov/dnr/state-parks/parks-lakes/brown-county-state-park/",
  "why": "total-looking"
 },
 "ours": {
  "acres": 15645,
  "dissolved": {
   "after": 16082,
   "before": 28733,
   "copies": 1,
   "families": {
    "padus": 12705,
    "sgina": 3377
   },
   "family_fold": 3377,
   "family_used": "padus",
   "key_union": 15645,
   "parts": 0,
   "records": 4,
   "summed": 12705,
   "tracts": 3
  },
  "family_fold": "layers {'padus': 12705, 'sgina': 3377}: one land in 2 layers, the padus copy used (3,377 ac of copies not added)",
  "manager": "",
  "note": "4 joined records = 3 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 28733 -> 16082 acres",
  "pieces": [
   [
    201091,
    "Brown County State Park",
    12705,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 2,
 "same_agency": false,
 "score": 8,
 "t": "State Park",
 "verdict": "agree"
}
```

## US-10233 Clifty Canyon State Nature Preserve
```json
{
 "cause": "agency smaller: our outline may hold water, a lease or a neighbour tract",
 "checked": "2026-11-01",
 "handover": [],
 "n": "Clifty Canyon State Nature Preserve",
 "official": {
  "acres": 179.0,
  "as": "179 acres",
  "clean": true,
  "line": "2 maps Clifty Canyon Nature Preserve County: Jefferson Size: 179 acres Ownership: State Parks - IDNR Location and Access Parking and trail. This preserve is located in Clifty F",
  "read": "2026-11-01",
  "sent": "County: Jefferson Size: 179 acres",
  "url": "https://www.in.gov/dnr/nature-preserves/files/Clifty_Canyon-color.pdf",
  "why": "clean total"
 },
 "ours": {
  "acres": 261,
  "manager": "",
  "pieces": [
   [
    201053,
    "Clifty Canyon Nature Preserve",
    261,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 46,
 "same_agency": false,
 "score": 4,
 "t": "State Nature Preserve",
 "verdict": "off"
}
```

## US-4224 Salamonie River and Frances Slocum State Forest
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-01",
 "handover": [],
 "n": "Salamonie River and Frances Slocum State Forest",
 "official": {
  "acres": 950.0,
  "as": "950 acres",
  "clean": false,
  "line": "Hominy Ridge Lake and the large stone shelter house that stands near the lake. Today, the forest encompasses 950 acres offering many recreational opportunities to visitors. Learning about timber harvesting at Salamonie River Sta",
  "read": "2026-11-01",
  "sent": "Today, the forest encompasses 950 acres offering many recreational opportunities to visitors.",
  "url": "https://www.in.gov/dnr/forestry/properties/salamonie-river-state-forest/",
  "why": "total-looking"
 },
 "ours": {
  "acres": 683,
  "dissolved": {
   "after": 950,
   "before": 1900,
   "copies": 1,
   "key_union": 683,
   "parts": 0,
   "records": 2,
   "summed": 950,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1900 -> 950 acres",
  "pieces": [
   [
    "ind5039",
    "Salamonie River State Forest",
    950,
    "words"
   ]
  ],
  "pin": "just outside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 28,
 "same_agency": false,
 "score": 4,
 "t": "State Forest",
 "verdict": "off"
}
```

## US-4217 Owen-Putnam State Forest
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Owen-Putnam State Forest",
 "official": null,
 "ours": {
  "acres": 7587,
  "dissolved": {
   "after": 6850,
   "before": 13444,
   "copies": 1,
   "key_union": 7587,
   "parts": 0,
   "records": 3,
   "summed": 6850,
   "tracts": 2
  },
  "manager": "",
  "note": "3 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 13444 -> 6850 acres",
  "pieces": [
   [
    "sgina4754",
    "Owen-Putnam State Forest",
    6599,
    "name"
   ],
   [
    71144,
    "Owen-Putnam State Forest",
    251,
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

## US-4168 Frances Slocum on Mississinewa Lake State Recreation Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Frances Slocum on Mississinewa Lake State Recreation Area",
 "official": {
  "acres": 14386.0,
  "as": "14,386 acres",
  "clean": false,
  "line": "ore at www.indianabirdingtrail.com . Miami SRA, Red Bridge SRA w/marina, Frances Slocum SRA, Pearson Mill SRA 14,386 acres - 3,210-acre lake Mississinewa Lake, one of the three Upper Wabash flood-control reservoirs, offers excellent",
  "read": "2026-11-01",
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

## US-10206 Hemmer Woods State Nature Preserve
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-01",
 "handover": [],
 "n": "Hemmer Woods State Nature Preserve",
 "official": {
  "acres": 73.0,
  "as": "73 acres",
  "clean": true,
  "line": "Hemmer Woods Nature Preserve County: Gibson Size: 73 acres Ownership: Nature Preserves - IDNR Location and Access Parking and trail. From Buckskin on SR 57 take",
  "read": "2026-11-01",
  "sent": "County: Gibson Size: 73 acres",
  "url": "https://www.in.gov/dnr/nature-preserves/files/np-HemmerWoods_Directory_Page.pdf",
  "why": "clean total"
 },
 "ours": {
  "acres": 47,
  "dissolved": {
   "after": 146,
   "before": 218,
   "copies": 1,
   "families": {
    "padus": 74,
    "sgina": 72
   },
   "family_fold": 72,
   "family_used": "padus",
   "key_union": 47,
   "parts": 0,
   "records": 3,
   "summed": 74,
   "tracts": 2
  },
  "family_fold": "layers {'padus': 74, 'sgina': 72}: one land in 2 layers, the padus copy used (72 ac of copies not added)",
  "manager": "",
  "note": "3 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 218 -> 146 acres",
  "pieces": [
   [
    200793,
    "Hemmer Woods Nature Preserve",
    74,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 36,
 "same_agency": false,
 "score": 6,
 "t": "State Nature Preserve",
 "verdict": "off"
}
```

## US-4211 Kankakee State Fish and Wildlife Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Kankakee State Fish and Wildlife Area",
 "official": {
  "acres": 4554.0,
  "as": "4,554 acres",
  "clean": false,
  "line": "and rules. View statewide trapping regulations in the Hunting & Trapping Guide . Wildlife watching & birding 4,554 acres of riparian woodlands, wetlands, marsh, and farmland attract deer, wild turkey, waterfowl, hawks, owls, bald",
  "read": "2026-11-01",
  "sent": "4,554 acres of riparian woodlands, wetlands, marsh, and farmland attract deer, wild turkey, waterfowl, hawks, owls, bald eagles, and shorebirds.",
  "url": "https://www.in.gov/dnr/fish-and-wildlife/properties/kankakee-fwa/",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 4421,
  "family_fold": "layers {'padus': 4421, 'sgina': 4303}: one land in 2 layers, the padus copy used (4,303 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    200934,
    "Kankakee Fish and Wildlife Area",
    4410,
    "name"
   ],
   [
    71132,
    "Kankakee Fish And Wildlife Area",
    11,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 3,
 "same_agency": false,
 "score": 8,
 "t": "State Fish and Wildlife Area",
 "verdict": "agree"
}
```
