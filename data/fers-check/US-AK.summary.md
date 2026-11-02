# 2-fer accuracy check: US-AK

Run 2026-11-01T11:31:34Z → 2026-11-01T12:04:59Z (UTC) · tool 0.1.0 (2026-10-31) · complete
Live rows in the file: 39 · checked: 39 · skipped (dropped / merged): 1212

| verdict | rows |
|---|---|
| CONFIRMED | 25 |
| SHRUNK | 2 |
| GREW | 5 |
| GONE | 5 |
| RECORD CHANGED | 2 |

| flag | rows |
|---|---|
| small overlap (under 50 yd across) | 5 |
| trail line from the club saved copy (not re-read live) | 8 |
| water-only | 3 |

## For a person to look at

- **SHRUNK** `US-0149+US-4447@area@60.366,-149.960`: live overlap is 75% smaller (2.1 ac vs 8.2 ac stored)
- **SHRUNK** `US-4447+US-4570@trail@60.625,-149.063`: live overlap is 41% smaller (22.6 ac vs 38.2 ac stored)
- **GREW** `US-0003+US-0902@same land@56.780,-157.556`: live overlap is 37% bigger (586737.2 ac vs 427486.9 ac stored); 97% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-0143+US-1639@area@58.147,-152.108`: live overlap is 192% bigger (1357.1 ac vs 465.2 ac stored); 97% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-0150+US-1639@area@58.342,-152.576`: live overlap is 96% bigger (3.2 ac vs 1.6 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-1638+US-3392@same land@59.345,-151.135`: live overlap is 28% bigger (253151.4 ac vs 198114.6 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-4448+US-4592@area@59.260,-135.165`: live overlap is 191% bigger (104974.9 ac vs 36125.1 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GONE** `US-0149+US-7884@area@60.317,-149.810`: no overlap between the live official outlines near this spot
- **GONE** `US-4447+US-7884@area@60.475,-149.109`: no overlap between the live official outlines near this spot
- **GONE** `US-4448+US-4537@area@57.231,-134.653`: no overlap between the live official outlines near this spot
- **GONE** `US-4570+US-7884@trail@60.624,-149.063`: no overlap between the live official outlines near this spot
- **GONE** `US-4570+US-7884@trail@61.015,-149.088`: no overlap between the live official outlines near this spot
- **RECORD CHANGED** `US-0157+US-11855@area@65.743,-146.261`: US-11855: 1 key record id(s) no longer in gis.blm.gov/lands/BLM_Natl_NLCS_NM_NCA_poly/MapServer/0/query: [417] | US-11855: found by name 'Steese National Conservation Area' near the spot as new id(s) [None] (geometry now: CONFIRMED: live overlap 140.4 ac vs 138.6 ac stored (+1%), 100% of the stored 
- **RECORD CHANGED** `US-11855+US-7886@area@65.114,-143.759`: US-11855: 1 key record id(s) no longer in gis.blm.gov/lands/BLM_Natl_NLCS_NM_NCA_poly/MapServer/0/query: [417] | US-11855: found by name 'Steese National Conservation Area' near the spot as new id(s) [None] (geometry now: CONFIRMED: live overlap 58.5 ac vs 57.5 ac stored (+2%), 100% of the stored ov

The 2-fer file was not changed. A person and the club waiting room decide.
