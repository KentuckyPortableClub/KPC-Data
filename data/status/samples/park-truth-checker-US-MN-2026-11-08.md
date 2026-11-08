# park truth checker: US-MN random sample of 12 (2026-11-08; seed = date + area, same rows for everyone)

Source file: `data/truth/US-MN.json`

## US-2519 Savanna Portage State Park
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Savanna Portage State Park",
 "official": null,
 "ours": {
  "acres": 16266,
  "dissolved": {
   "after": 46485,
   "before": 46742,
   "copies": 0,
   "families": {
    "padus": 15186,
    "sgmnd": 16266,
    "sgmne": 15033
   },
   "family_fold": 30219,
   "family_used": "sgmnd",
   "parts": 26,
   "records": 408,
   "tracts": 382
  },
  "family_fold": "layers {'sgmnd': 16266, 'padus': 15186, 'sgmne': 15033}: one land in 3 layers, the sgmnd copy used (30,219 ac of copies not added)",
  "manager": "",
  "note": "408 joined records = 382 tracts: 0 copies of a tract (same acres, another layer) and 26 fee tracts under a designation record folded; summed 46742 -> 46485 acres",
  "pieces": [
   [
    "sgmnd21",
    "Savanna Portage",
    16266,
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
 "t": "State Park",
 "verdict": "no size on page"
}
```

## US-13633 Talcot Lake Wildlife Management Area
```json
{
 "checked": "2026-11-08",
 "handover": [],
 "n": "Talcot Lake Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 5793,
  "dissolved": {
   "after": 5319,
   "before": 10580,
   "copies": 1,
   "key_union": 5793,
   "parts": 0,
   "records": 2,
   "summed": 5319,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 10580 -> 5319 acres",
  "pieces": [
   [
    "sgmna246",
    "Talcot Lake WMA",
    5319,
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
 "t": "Wildlife Management Area",
 "verdict": "no size on page"
}
```

## US-11148 Hardwood Creek WMA Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Hardwood Creek WMA Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 428,
  "dissolved": {
   "after": 583,
   "before": 1166,
   "copies": 1,
   "key_union": 428,
   "parts": 0,
   "records": 2,
   "summed": 583,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1166 -> 583 acres",
  "pieces": [
   [
    208890,
    "Hardwood Creek State Wildlife Management Area",
    583,
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
 "t": "Wildlife Management Area",
 "verdict": "no size on page"
}
```

## US-6468 Iron Range OHV State Recreation Area
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-01",
 "handover": [],
 "n": "Iron Range OHV State Recreation Area",
 "official": {
  "acres": 1200.0,
  "as": "1,200 acres",
  "clean": false,
  "line": "ghway Vehicle State Recreation Area - Gilbert Trail map | Learn more about GeoPDF maps | Trail closings Enjoy 1,200 acres of off-highway vehicle (OHV) recreation in a northwoods setting. This area was mined until 1981 and contains",
  "read": "2026-11-01",
  "sent": "Enjoy 1,200 acres of off-highway vehicle (OHV) recreation in a northwoods setting.",
  "url": "https://www.dnr.state.mn.us/ohv/gilbert/index.html",
  "why": "total-looking"
 },
 "ours": {
  "acres": 25,
  "manager": "",
  "pieces": [
   [
    "sgmne12212",
    "IRON RANGE OFF HWY VEH",
    34,
    "alias name (pin inside): IRON RANGE OFF HWY VEH"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 1
 },
 "owner_now": null,
 "pct": 98,
 "same_agency": false,
 "score": 5,
 "t": "State Recreation Area",
 "verdict": "off"
}
```

## US-0371 Tamarac National Wildlife Refuge
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-01",
 "handover": [
  {
   "date_hint": null,
   "kind": "managed by",
   "line": "and become inspired What We Do The National Wildlife Refuge System is a series of lands and waters owned and managed by the U.S. Fish and Wildlife Service. Wildlife conservation is at the heart of the refuge system. It drives everything we do from the purpose a refuge is establis",
   "owner_now": "U.S",
   "src": "https://www.fws.gov/refuge/tamarac",
   "why": "the park's page (data/parkinfo)"
  }
 ],
 "n": "Tamarac National Wildlife Refuge",
 "official": {
  "acres": 6784000.0,
  "as": "10,600 square miles",
  "clean": false,
  "line": "central Minnesota, where the pines meet the prairie. Tamarac Wetland Management District stretches more than 10,600 square miles in Beltrami, Cass, Clearwater, Hubbard and Koochiching... National Wildlife Refuge Rochert, MN You are exitin",
  "read": "2026-11-01",
  "sent": "Tamarac Wetland Management District stretches more than 10,600 square miles in Beltrami, Cass, Clearwater, Hubbard and Koochiching...",
  "url": "https://www.fws.gov/refuge/tamarac/about-us",
  "why": "total-looking"
 },
 "ours": {
  "acres": 44895,
  "manager": "",
  "pieces": [
   [
    4385,
    "Tamarac National Wildlife Refuge",
    43425,
    "name"
   ],
   [
    5342,
    "Tamarac National Wildlife Refuge",
    42534,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": "U.S",
 "pct": 99,
 "same_agency": false,
 "score": 6,
 "t": "National Wildlife Refuge",
 "verdict": "off"
}
```

## US-12690 Proehl’s Woods Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Proehl’s Woods Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 70,
  "dissolved": {
   "after": 134,
   "before": 268,
   "copies": 1,
   "key_union": 70,
   "parts": 0,
   "records": 2,
   "summed": 134,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 268 -> 134 acres",
  "pieces": [
   [
    209349,
    "Proehl's Woods State Wildlife Management Area",
    134,
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

## US-12694 Sigler Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Sigler Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 79,
  "dissolved": {
   "after": 74,
   "before": 147,
   "copies": 1,
   "key_union": 79,
   "parts": 0,
   "records": 2,
   "summed": 74,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 147 -> 74 acres",
  "pieces": [
   [
    209516,
    "Sigler State Wildlife Management Area",
    74,
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

## US-7144 La Salle Lake State Recreation Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "La Salle Lake State Recreation Area",
 "official": null,
 "ours": {
  "acres": 820,
  "dissolved": {
   "after": 1557,
   "before": 2697,
   "copies": 1,
   "families": {
    "padus": 988,
    "sgmne": 569
   },
   "family_fold": 569,
   "family_used": "padus",
   "key_union": 820,
   "parts": 8,
   "records": 25,
   "summed": 988,
   "tracts": 16
  },
  "family_fold": "layers {'padus': 988, 'sgmne': 569}: one land in 2 layers, the padus copy used (569 ac of copies not added)",
  "manager": "",
  "note": "25 joined records = 16 tracts: 1 copies of a tract (same acres, another layer) and 8 fee tracts under a designation record folded; summed 2697 -> 1557 acres",
  "pieces": [
   [
    209866,
    "La Salle Lake",
    988,
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
 "t": "State Recreation Area",
 "verdict": "no size on page"
}
```

## US-9379 Sakatah Singing Hills State Trail
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Sakatah Singing Hills State Trail",
 "official": null,
 "ours": {
  "acres": 65,
  "manager": "",
  "pieces": [
   [
    "sgmne4824",
    "SAKATAH SINGING HILLS",
    4,
    "same name (POTA writes the kind into the name) + pin inside"
   ],
   [
    "sgmne4823",
    "SAKATAH SINGING HILLS",
    3,
    "same name (POTA writes the kind into the name) + pin inside"
   ],
   [
    "sgmne4826",
    "SAKATAH SINGING HILLS",
    3,
    "same name (POTA writes the kind into the name) + pin inside"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "State Trail",
 "verdict": "no size on page"
}
```

## US-12810 Choice Wildlife Management Area
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Choice Wildlife Management Area",
 "official": null,
 "ours": {
  "acres": 1664,
  "manager": "",
  "pieces": [
   [
    "sgmna751",
    "Choice WMA",
    1664,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "Wildlife Management Area",
 "verdict": "no size on page"
}
```

## US-12457 Riverlands State Forest
```json
{
 "checked": "2026-11-01",
 "handover": [],
 "n": "Riverlands State Forest",
 "official": null,
 "ours": {
  "acres": 22861,
  "manager": "",
  "pieces": [
   [
    "sgmnb7",
    "Riverlands",
    22861,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 7,
 "t": "State Forest",
 "verdict": "no size on page"
}
```

## US-10278 Inspiration Peak State Wayside State Natural Site
```json
{
 "cause": "a number 5 parks share from one page (26 ac): an agency total, not this park",
 "checked": "2026-11-01",
 "handover": [],
 "n": "Inspiration Peak State Wayside State Natural Site",
 "official": null,
 "ours": {
  "acres": 82,
  "manager": "",
  "pieces": [
   [
    209795,
    "Inspiration Peak State Wayside",
    82,
    "reviewed"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "same_agency": false,
 "score": 6,
 "t": "State Natural Site",
 "verdict": "unsure"
}
```
