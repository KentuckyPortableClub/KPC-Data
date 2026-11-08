# park truth checker: US-IN random sample of 12 (2026-11-08; seed = date + area, same rows for everyone)

Source file: `data/truth/US-IN.json`

## US-2259 Lincoln State Park
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Lincoln State Park",
 "official": {
  "acres": 1747.0,
  "as": "1,747 acre",
  "clean": false,
  "line": "e Colonel Jones Home, the historic home of the merchant and Civil War officer who employed young Lincoln. The 1,747-acre park was established in 1932 as a memorial to Lincoln's mother, Nancy Hanks. The Little Pigeon Creek Baptist",
  "read": "2026-11-01",
  "sent": "The 1,747-acre park was established in 1932 as a memorial to Lincoln's mother, Nancy Hanks.",
  "url": "https://www.in.gov/dnr/state-parks/parks-lakes/lincoln-state-park/",
  "why": "history"
 },
 "ours": {
  "acres": 1874,
  "dissolved": {
   "after": 3898,
   "before": 3999,
   "copies": 1,
   "families": {
    "ind": 101,
    "padus": 1756,
    "sgina": 2041
   },
   "family_fold": 1857,
   "family_used": "sgina",
   "key_union": 1874,
   "parts": 0,
   "records": 7,
   "summed": 2041,
   "tracts": 6
  },
  "family_fold": "layers {'sgina': 2041, 'padus': 1756, 'ind': 101}: one land in 3 layers, the sgina copy used (1,857 ac of copies not added)",
  "manager": "",
  "note": "7 joined records = 6 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 3999 -> 3898 acres",
  "pieces": [
   [
    "sgina4348",
    "Lincoln State Park",
    1912,
    "name"
   ],
   [
    "sgina4349",
    "Lincoln State Park",
    129,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 7,
 "same_agency": false,
 "score": 8,
 "t": "State Park",
 "verdict": "agree"
}
```

## US-4177 Dora-New Holland on Salamonie Lake State Recreation Area
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units",
 "checked": "2026-11-01",
 "handover": [],
 "n": "Dora-New Holland on Salamonie Lake State Recreation Area",
 "official": null,
 "ours": {
  "acres": 10768,
  "manager": "",
  "pieces": [
   [
    "ind5037",
    "Salamonie Lake",
    10768,
    "reviewed-approx"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "State Recreation Area",
 "verdict": "unsure"
}
```

## US-12000 Moraine State Nature Preserve
```json
{
 "cause": "agency smaller: our outline may hold water, a lease or a neighbour tract",
 "checked": "2026-11-01",
 "handover": [],
 "n": "Moraine State Nature Preserve",
 "official": {
  "acres": 474.0,
  "as": "474 acres",
  "clean": true,
  "line": "● Moraine Nature Preserve County: Porter Size: 474 acres Ownership: Nature Preserves - IDNR Location and Access Parking and trails. From Valparaiso, go north",
  "read": "2026-11-01",
  "sent": "County: Porter Size: 474 acres",
  "url": "https://www.in.gov/dnr/nature-preserves/files/np-Moraine.pdf",
  "why": "clean total"
 },
 "ours": {
  "acres": 1055,
  "dissolved": {
   "after": 1448,
   "before": 2403,
   "copies": 2,
   "families": {
    "padus": 466,
    "sgina": 955,
    "sginb": 27
   },
   "family_fold": 493,
   "family_used": "sgina",
   "key_union": 1055,
   "parts": 0,
   "records": 6,
   "summed": 955,
   "tracts": 4
  },
  "family_fold": "layers {'sgina': 955, 'padus': 466, 'sginb': 27}: one land in 3 layers, the sgina copy used (493 ac of copies not added)",
  "manager": "",
  "note": "6 joined records = 4 tracts: 2 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 2403 -> 1448 acres",
  "pieces": [
   [
    "sgina4591",
    "Moraine Nature Preserve",
    883,
    "name"
   ],
   [
    "sgina4590",
    "Moraine Natural Area",
    72,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 123,
 "same_agency": false,
 "score": 6,
 "t": "State Nature Preserve",
 "verdict": "off"
}
```

## US-4230 Twin Swamps State Nature Preserve
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Twin Swamps State Nature Preserve",
 "official": {
  "acres": 598.0,
  "as": "598 acres",
  "clean": true,
  "line": "Twin Swamps Nature Preserve County: Posey Size: 598 acres Ownership: Nature Preserves - IDNR Location and Access Parking and trail. West of Mt. Vernon. Take SR 6",
  "read": "2026-11-01",
  "sent": "County: Posey Size: 598 acres",
  "url": "https://www.in.gov/dnr/nature-preserves/files/np-TwinSwamps_Directory_Page.pdf",
  "why": "clean total"
 },
 "ours": {
  "acres": 622,
  "dissolved": {
   "after": 622,
   "before": 2451,
   "copies": 5,
   "parts": 0,
   "records": 7,
   "tracts": 2
  },
  "manager": "",
  "note": "7 joined records = 2 tracts: 5 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 2451 -> 622 acres",
  "pieces": [
   [
    200826,
    "Twin Swamps Nature Preserve",
    600,
    "name"
   ],
   [
    "ind5409",
    "Twin Swamps",
    22,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 4,
 "same_agency": false,
 "score": 8,
 "t": "State Nature Preserve",
 "verdict": "agree"
}
```

## US-13082 Jug Rock State Nature Preserve
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-08",
 "n": "Jug Rock State Nature Preserve",
 "official": null,
 "ours": {
  "acres": 28,
  "dissolved": {
   "after": 71,
   "before": 107,
   "copies": 1,
   "families": {
    "padus": 35,
    "sgina": 36
   },
   "family_fold": 35,
   "family_used": "sgina",
   "key_union": 28,
   "parts": 0,
   "records": 3,
   "summed": 36,
   "tracts": 2
  },
  "family_fold": "layers {'sgina': 36, 'padus': 35}: one land in 2 layers, the sgina copy used (35 ac of copies not added)",
  "manager": "",
  "note": "3 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 107 -> 71 acres",
  "pieces": [
   [
    "sgina4142",
    "Jug Rock Nature Preserve",
    36,
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
 "t": "State Nature Preserve",
 "verdict": "no size on page"
}
```

## US-10177 Ogle Hollow State Nature Preserve
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Ogle Hollow State Nature Preserve",
 "official": {
  "acres": 41.0,
  "as": "41 acres",
  "clean": true,
  "line": "Ogle Hollow Nature Preserve County: Brown Size: 41 acres Ownership: State Parks - IDNR Location and Access Parking and trail. Located near the youth campground in",
  "read": "2026-11-01",
  "sent": "County: Brown Size: 41 acres",
  "url": "https://www.in.gov/dnr/nature-preserves/files/Ogle_Hollow-color.pdf",
  "why": "clean total"
 },
 "ours": {
  "acres": 42,
  "manager": "",
  "pieces": [
   [
    201076,
    "Ogle Hollow Nature Preserve",
    42,
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
 "score": 7,
 "t": "State Nature Preserve",
 "verdict": "agree"
}
```

## US-4169 Miami on Mississinewa Lake State Recreation Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Miami on Mississinewa Lake State Recreation Area",
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

## US-10405 Wabash River Conservation Area
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-01",
 "handover": [
  {
   "date_hint": "2010",
   "kind": "transfer",
   "line": "asses and agriculture in Putnam County. The land that compromises most of Deer Creek was originally transferred from the Putnamville Correctional Facility to the DNR in 2010 and several more parcels have been bought since then. It is open to the public and hunting, fishing, trapping, and other outdo",
   "owner_now": "Putnamville Correctional Facility",
   "src": "https://www.in.gov/dnr/fish-and-wildlife/properties/wabash-river-conservation-area/#Maps",
   "why": "the park's page (data/parkinfo)"
  },
  {
   "date_hint": null,
   "kind": "managed by",
   "line": "a Alerts None at this time. Description & Amenities Activities Interactive Map --> Other Properties Managed by Deer Creek Fish & Wildlife Area Physical Addresses For a list of available parking lots, please see the maps below. Mailing Address 2001 W County Road",
   "owner_now": "Deer Creek Fish & Wildlife Area\nPhysical",
   "src": "https://www.in.gov/dnr/fish-and-wildlife/properties/wabash-river-conservation-area/#Maps",
   "why": "the park's page (data/parkinfo)"
  }
 ],
 "n": "Wabash River Conservation Area",
 "official": {
  "acres": 2452.0,
  "as": "2,452 acres",
  "clean": true,
  "line": "sh; 3 p.m. Link to this page on.IN.gov/wabash-river-ca Description Wabash River Conservation Area consists of 2,452 acres of bottomland and floodplain along the Wabash River. It stretches across three counties &ndash; Parke, Vermil",
  "read": "2026-11-01",
  "sent": "Wabash River Conservation Area consists of 2,452 acres of bottomland and floodplain along the Wabash River.",
  "url": "https://www.in.gov/dnr/fish-and-wildlife/properties/wabash-river-conservation-area/#Maps",
  "why": "clean total"
 },
 "ours": {
  "acres": 886,
  "dissolved": {
   "after": 1697,
   "before": 3394,
   "copies": 1,
   "key_union": 886,
   "parts": 0,
   "records": 2,
   "summed": 1697,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 3394 -> 1697 acres",
  "pieces": [
   [
    "ind5456",
    "Wabash River Conservation Area",
    1697,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": "Putnamville Correctional Facility",
 "pct": 64,
 "same_agency": false,
 "score": 5,
 "t": "Conservation Ar
```

## US-2264 Pokagon State Park
```json
{
 "cause": "no total-looking sentence: numbers found were parts or other units (nearest number found: 200 acre, no total words near it)",
 "checked": "2026-11-01",
 "handover": [
  {
   "date_hint": "2007",
   "kind": "transfer",
   "line": "ng with the purchase. The Trines bought the property in 2006, paying $2.8 million. The property was transferred to DNR in 2007 with financial support from the Trines, DNR&rsquo;s Indiana Heritage Trust, the Indiana Chapter of the Nature Conservancy, ACRES Land Trust, Steuben",
   "owner_now": "DNR",
   "src": "https://www.in.gov/dnr/state-parks/parks-lakes/pokagon-state-parktrine-state-recreation-area/",
   "why": "the park's page (data/parkinfo)"
  }
 ],
 "n": "Pokagon State Park",
 "official": {
  "acres": 200.0,
  "as": "200 acre",
  "clean": false,
  "line": "serve water quality. In 2006 a group of citizens and groups formed a committee to discuss the purchase of the 200-acre Oak Hill Conference and Retreat Center, which was to be auctioned at a sheriff&rsquo;s sale. The group believ",
  "read": "2026-11-01",
  "sent": "In 2006 a group of citizens and groups formed a committee to discuss the purchase of the 200-acre Oak Hill Conference and Retreat Center, which was to be auctioned at a sheriff&rsquo;s sale.",
  "url": "https://www.in.gov/dnr/state-parks/parks-lakes/pokagon-state-parktrine-state-recreation-area/",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 1233,
  "family_fold": "layers {'sgina': 1233, 'padus': 939}: one land in 2 layers, the sgina copy used (939 ac of copies not added)",
  "manager": "",
  "pieces": [
   [
    "sgina4850",
    "Pokagon State Park",
    975,
    "name"
   ],
   [
    "sgina4851",
    "Pokagon State Park",
    258,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": "DNR",
 "pct": 516,
 "same_agency": false,
 "score": 7,
 "t": "State Park",
 "verdict": "unsure"
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

## US-6978 Vincennes State Historic Site
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Vincennes State Historic Site",
 "official": null,
 "ours": {
  "acres": 21,
  "manager": "",
  "pieces": [
   [
    200679,
    "Vincennes State Historic Site - Fort Knox",
    35,
    "reviewed"
   ],
   [
    157074,
    "Vincennes State Historic Site",
    9,
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
 "t": "State Historic Site",
 "verdict": "no size on page"
}
```

## US-13104 Three Rivers State Fishing Lake
```json
{
 "checked": "2026-10-28",
 "handover": [],
 "last_read_failed": "2026-11-08",
 "n": "Three Rivers State Fishing Lake",
 "official": null,
 "ours": {
  "acres": 2,
  "dissolved": {
   "after": 9,
   "before": 18,
   "copies": 1,
   "key_union": 2,
   "parts": 0,
   "records": 2,
   "summed": 9,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 18 -> 9 acres",
  "pieces": [
   [
    "ind5342",
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
