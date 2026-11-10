# park truth checker: CA-NB random sample of 12 (2026-11-10; seed = date + area, same rows for everyone)

Source file: `data/truth/CA-NB.json`

## CA-4459 Mount Tom Protected Area
```json
{
 "checked": "2026-11-10",
 "handover": [],
 "n": "Mount Tom Protected Area",
 "official": null,
 "ours": {
  "acres": 376,
  "dissolved": {
   "after": 697,
   "before": 1073,
   "copies": 1,
   "families": {
    "New Brunswic~1:1068": 321,
    "padus": 376
   },
   "family_fold": 321,
   "family_used": "padus",
   "parts": 0,
   "records": 3,
   "tracts": 2
  },
  "family_fold": "layers {'padus': 376, 'New Brunswic~1:1068': 321}: one land in 2 layers, the padus copy used (321 ac of copies not added)",
  "manager": "",
  "note": "3 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1073 -> 697 acres",
  "pieces": [
   [
    3195,
    "Mount Tom",
    376,
    "name"
   ]
  ],
  "pin": "well outside",
  "src": "New Brunswick Nature Legacy protected areas (GNB), New Brunswick protected natural areas (GNB)",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 4,
 "t": "Protected Area",
 "verdict": "no size on page"
}
```

## CA-4453 Miscou Grande Plaine Protected Area
```json
{
 "checked": "2026-11-10",
 "handover": [],
 "n": "Miscou Grande Plaine Protected Area",
 "official": null,
 "ours": {
  "acres": 297,
  "dissolved": {
   "after": 297,
   "before": 594,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 594 -> 297 acres",
  "pieces": [
   [
    3096,
    "Miscou Grande Plaine",
    297,
    "name"
   ]
  ],
  "pin": "well outside",
  "src": "New Brunswick protected natural areas (GNB)",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 4,
 "t": "Protected Area",
 "verdict": "no size on page"
}
```

## CA-4430 Little Salmon River Protected Area
```json
{
 "checked": "2026-11-10",
 "handover": [],
 "n": "Little Salmon River Protected Area",
 "official": null,
 "ours": {
  "acres": 1859,
  "dissolved": {
   "after": 3698,
   "before": 5487,
   "copies": 1,
   "families": {
    "New Brunswic:131": 1814,
    "New Brunswic~1:41": 1859,
    "padus": 25
   },
   "family_fold": 1839,
   "family_used": "New Brunswic~1:41",
   "parts": 0,
   "records": 4,
   "tracts": 3
  },
  "family_fold": "layers {'New Brunswic~1:41': 1859, 'New Brunswic:131': 1814, 'padus': 25}: one land in 3 layers, the New Brunswic~1:41 copy used (1,839 ac of copies not added)",
  "manager": "",
  "note": "4 joined records = 3 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 5487 -> 3698 acres",
  "pieces": [
   [
    "New Brunswic~1:41",
    "Little Salmon River",
    1859,
    "name · New Brunswick Nature Legacy protected areas (GNB)"
   ]
  ],
  "pin": "inside",
  "src": "New Brunswick Nature Legacy protected areas (GNB), New Brunswick protected natural areas (GNB)",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "Protected Area",
 "verdict": "no size on page"
}
```

## CA-1256 Thomas B. Munro Memorial Shoreline Nature Reserve
```json
{
 "cause": "agency bigger: our outline may miss a tract",
 "checked": "2026-11-10",
 "handover": [
  {
   "date_hint": "2004",
   "kind": "transfer",
   "line": "the landmark points known as Northern Head, The Bishop and Ashburton Head. history Mr. James Munro donated first the conservation easement of the preserve and then full title to the Nature Trust of New Brunswick in 2004. As part of our most successful fundraising year in 2024-25, we acquired one new",
   "owner_now": "Nature Trust of New Brunswick",
   "src": "https://www.naturetrust.nb.ca/en/thomas-b-munro-memorial-shoreline",
   "why": "the park's page (data/parkinfo)"
  }
 ],
 "n": "Thomas B. Munro Memorial Shoreline Nature Reserve",
 "official": {
  "acres": 91.0,
  "as": "91 acres",
  "clean": false,
  "line": "SHORELINE Overview Donated by Mr. James Munro, the Thomas B. Munro Preserve, consisting of over 37 hectares (91 acres), was the Nature Trust’s first conserved area on Grand Manan Island. This preserve is a narrow strip of land",
  "read": "2026-11-10",
  "sent": "Munro Preserve, consisting of over 37 hectares (91 acres), was the Nature Trust’s first conserved area on Grand Manan Island.",
  "url": "https://www.naturetrust.nb.ca/en/thomas-b-munro-memorial-shoreline",
  "why": "total-looking"
 },
 "ours": {
  "acres": 63,
  "manager": "",
  "pieces": [
   [
    3322,
    "Thomas B. Munro Memorial Shoreline",
    63,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": "Nature Trust of New Brunswick",
 "pct": 31,
 "same_agency": false,
 "score": 5,
 "t": "Nature Reserve",
 "verdict": "off"
}
```

## CA-4416 Indian Brook Protected Area
```json
{
 "checked": "2026-11-10",
 "handover": [],
 "n": "Indian Brook Protected Area",
 "official": null,
 "ours": {
  "acres": 807,
  "dissolved": {
   "after": 807,
   "before": 1614,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1614 -> 807 acres",
  "pieces": [
   [
    3167,
    "Indian Brook",
    807,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "New Brunswick protected natural areas (GNB)",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 5,
 "t": "Protected Area",
 "verdict": "no size on page"
}
```

## CA-5184 Henry Park Recreation Park
```json
{
 "checked": "2026-11-10",
 "handover": [],
 "n": "Henry Park Recreation Park",
 "official": {
  "acres": 11.0,
  "as": "11 acres",
  "clean": false,
  "line": ".com/v.php?seo=henry-park-fredericton&id=1613572&yuk=300\" frameborder=\"0\"&gt;&lt;/iframe&gt;&lt;p style=\"font-size:11px;margin-top:5px;\"&gt;&lt;a href=\"https://a-better-place.com/henry-park-fredericton-i1613572/\" target=\"_blank",
  "read": "2026-11-10",
  "sent": "&lt;iframe width=\"450\" height=\"300\" src=\"https://a-better-place.com/v.php?seo=henry-park-fredericton&id=1613572&yuk=300\" frameborder=\"0\"&gt;&lt;/iframe&gt;&lt;p style=\"font-size:11px;margin-top:5px;\"&gt;&lt;a href=\"https://a-better-place.com/henry-park-fredericton-i1613572/\" target=\"_blank\" title=\"H",
  "url": "https://a-better-place.com/d-i/?utm_content=henry-park-fredericton-i1613572",
  "why": "total-looking"
 },
 "ours": {
  "acres": 11,
  "manager": "",
  "pieces": [
   [
    "NB Parks~1:97",
    "Henry Park",
    11,
    "name · NB Parks"
   ]
  ],
  "pin": "just outside",
  "src": "NB Parks",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 0,
 "same_agency": false,
 "score": 6,
 "t": "Recreation Park",
 "verdict": "agree"
}
```

## CA-4389 Downs Gulch Protected Area
```json
{
 "checked": "2026-11-10",
 "handover": [],
 "n": "Downs Gulch Protected Area",
 "official": null,
 "ours": {
  "acres": 2633,
  "dissolved": {
   "after": 3737,
   "before": 4841,
   "copies": 1,
   "families": {
    "New Brunswic~1:819": 2633,
    "padus": 1104
   },
   "family_fold": 1104,
   "family_used": "New Brunswic~1:819",
   "parts": 0,
   "records": 3,
   "tracts": 2
  },
  "family_fold": "layers {'New Brunswic~1:819': 2633, 'padus': 1104}: one land in 2 layers, the New Brunswic~1:819 copy used (1,104 ac of copies not added)",
  "manager": "",
  "note": "3 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 4841 -> 3737 acres",
  "pieces": [
   [
    "New Brunswic~1:819",
    "Downs Gulch",
    2633,
    "name · New Brunswick Nature Legacy protected areas (GNB)"
   ]
  ],
  "pin": "inside",
  "src": "New Brunswick Nature Legacy protected areas (GNB), New Brunswick protected natural areas (GNB)",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "Protected Area",
 "verdict": "no size on page"
}
```

## CA-0014 Cape Jourimain National Wildlife Area
```json
{
 "checked": "2026-11-10",
 "handover": [],
 "n": "Cape Jourimain National Wildlife Area",
 "official": {
  "acres": 1534.5,
  "as": "621 ha",
  "clean": false,
  "line": "cted Area designation NWA Province/territory New Brunswick Latitude/longitude 46°09' North / 63°49' West Size 621 ha Reason for creation of protected area To provide secure protection of the habitats of this coastal site and t",
  "read": "2026-11-10",
  "sent": "621 ha",
  "url": "https://www.canada.ca/en/environment-climate-change/services/national-wildlife-areas/locations/cape-jourimain.html#toc0",
  "why": "no total words near it"
 },
 "ours": {
  "acres": 1318,
  "manager": "",
  "pieces": [
   [
    22110,
    "Cape Jourimain National Wildlife Area",
    690,
    "name"
   ],
   [
    22111,
    "Cape Jourimain National Wildlife Area",
    530,
    "name"
   ],
   [
    22112,
    "Cape Jourimain",
    41,
    "name"
   ],
   [
    22113,
    "Cape Jourimain",
    38,
    "name"
   ],
   [
    22114,
    "Cape Jourimain",
    19,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "USGS PAD-US",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": 14,
 "same_agency": false,
 "score": 7,
 "t": "National Wildlife Area",
 "verdict": "agree"
}
```

## CA-4422 Lake Stream Protected Area
```json
{
 "checked": "2026-11-10",
 "handover": [],
 "n": "Lake Stream Protected Area",
 "official": null,
 "ours": {
  "acres": 6314,
  "dissolved": {
   "after": 7752,
   "before": 14065,
   "copies": 1,
   "families": {
    "New Brunswic~1:1046": 1438,
    "padus": 6314
   },
   "family_fold": 1438,
   "family_used": "padus",
   "parts": 0,
   "records": 3,
   "tracts": 2
  },
  "family_fold": "layers {'padus': 6314, 'New Brunswic~1:1046': 1438}: one land in 2 layers, the padus copy used (1,438 ac of copies not added)",
  "manager": "",
  "note": "3 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 14065 -> 7752 acres",
  "pieces": [
   [
    3169,
    "Lake Stream",
    6314,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "New Brunswick Nature Legacy protected areas (GNB), New Brunswick protected natural areas (GNB)",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "Protected Area",
 "verdict": "no size on page"
}
```

## CA-4464 Nalaisk Mountain Protected Area
```json
{
 "checked": "2026-11-10",
 "handover": [],
 "n": "Nalaisk Mountain Protected Area",
 "official": null,
 "ours": {
  "acres": 1186,
  "dissolved": {
   "after": 1423,
   "before": 2609,
   "copies": 1,
   "families": {
    "New Brunswic~1:912": 237,
    "padus": 1186
   },
   "family_fold": 237,
   "family_used": "padus",
   "parts": 0,
   "records": 3,
   "tracts": 2
  },
  "family_fold": "layers {'padus': 1186, 'New Brunswic~1:912': 237}: one land in 2 layers, the padus copy used (237 ac of copies not added)",
  "manager": "",
  "note": "3 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 2609 -> 1423 acres",
  "pieces": [
   [
    3197,
    "Nalaisk Mountain",
    1186,
    "name"
   ]
  ],
  "pin": "just outside",
  "src": "New Brunswick Nature Legacy protected areas (GNB), New Brunswick protected natural areas (GNB)",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 5,
 "t": "Protected Area",
 "verdict": "no size on page"
}
```

## CA-1259 Williamstown Lake Protected Area
```json
{
 "checked": "2026-11-10",
 "handover": [],
 "n": "Williamstown Lake Protected Area",
 "official": null,
 "ours": {
  "acres": 644,
  "dissolved": {
   "after": 1168,
   "before": 1692,
   "copies": 1,
   "families": {
    "New Brunswic~1:997": 644,
    "padus": 524
   },
   "family_fold": 524,
   "family_used": "New Brunswic~1:997",
   "parts": 0,
   "records": 3,
   "tracts": 2
  },
  "family_fold": "layers {'New Brunswic~1:997': 644, 'padus': 524}: one land in 2 layers, the New Brunswic~1:997 copy used (524 ac of copies not added)",
  "manager": "",
  "note": "3 joined records = 2 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 1692 -> 1168 acres",
  "pieces": [
   [
    "New Brunswic~1:997",
    "Williamstown Lake",
    644,
    "name · New Brunswick Nature Legacy protected areas (GNB)"
   ]
  ],
  "pin": "inside",
  "src": "New Brunswick Nature Legacy protected areas (GNB), New Brunswick protected natural areas (GNB)",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "Protected Area",
 "verdict": "no size on page"
}
```

## CA-4353 Ayers Lake Stream Protected Area
```json
{
 "checked": "2026-11-10",
 "handover": [],
 "n": "Ayers Lake Stream Protected Area",
 "official": null,
 "ours": {
  "acres": 302,
  "dissolved": {
   "after": 302,
   "before": 601,
   "copies": 1,
   "parts": 0,
   "records": 2,
   "tracts": 1
  },
  "manager": "",
  "note": "2 joined records = 1 tracts: 1 copies of a tract (same acres, another layer) and 0 fee tracts under a designation record folded; summed 601 -> 302 acres",
  "pieces": [
   [
    3112,
    "Ayers Lake Stream",
    302,
    "name"
   ]
  ],
  "pin": "inside",
  "src": "New Brunswick protected natural areas (GNB)",
  "unknown_pieces": 0
 },
 "owner_now": null,
 "pct": null,
 "score": 6,
 "t": "Protected Area",
 "verdict": "no size on page"
}
```
