# 2-fer accuracy check: US-AZ

Run 2026-11-01T11:47:02Z → 2026-11-08T06:22:05Z (UTC) · tool 0.1.0 (2026-10-31) · complete
Live rows in the file: 42 · checked: 42 · skipped (dropped / merged): 467

| verdict | rows |
|---|---|
| CONFIRMED | 31 |
| SHRUNK | 8 |
| GREW | 1 |
| GONE | 1 |
| RECORD CHANGED | 1 |

| flag | rows |
|---|---|
| small overlap (under 50 yd across) | 4 |
| trail line from the club saved copy (not re-read live) | 30 |

## For a person to look at

- **SHRUNK** `US-0060+US-4557@trail@32.130,-110.645`: only 63% of the stored overlap is still inside the live overlap (10 m tolerance)
- **SHRUNK** `US-11123+US-4557@trail@34.418,-111.318`: live overlap is 27% smaller (13.8 ac vs 19.0 ac stored)
- **SHRUNK** `US-4557+US-9757@trail@32.020,-110.644`: live overlap is 55% smaller (1.1 ac vs 2.5 ac stored)
- **SHRUNK** `US-4557+US-9757@trail@32.020,-110.647`: live overlap is 72% smaller (0.6 ac vs 2.3 ac stored)
- **SHRUNK** `US-4571+US-4575@trail@34.097,-117.745`: live overlap is 48% smaller (3.7 ac vs 7.1 ac stored)
- **SHRUNK** `US-4571+US-4578@trail@38.007,-122.089`: live overlap is 44% smaller (6.8 ac vs 12.2 ac stored)
- **SHRUNK** `US-4571+US-9757@trail@33.087,-112.188`: live overlap is 52% smaller (7.4 ac vs 15.6 ac stored)
- **SHRUNK** `US-4575+US-9757@trail@34.055,-118.225`: live overlap is 48% smaller (3.0 ac vs 5.7 ac stored)
- **GREW** `US-13594+US-4431@trail@34.325,-112.199`: live overlap is 27% bigger (0.3 ac vs 0.2 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GONE** `US-0771+US-4571@trail@31.425,-110.961`: no overlap between the live official outlines near this spot
- **RECORD CHANGED** `US-4430+US-7887@area@36.363,-112.320`: US-7887: 1 key record id(s) no longer in gis.blm.gov/lands/BLM_Natl_NLCS_NM_NCA_poly/MapServer/0/query: [461] (geometry now: GONE: no overlap between the live official outlines near this spot)

The 2-fer file was not changed. A person and the club waiting room decide.
