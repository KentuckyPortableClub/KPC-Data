# 2-fer accuracy check: US-NV

Run 2026-11-01T02:27:20Z → 2026-11-08T12:06:02Z (UTC) · tool 0.1.0 (2026-10-31) · complete
Live rows in the file: 94 · checked: 94 · skipped (dropped / merged): 767

| verdict | rows |
|---|---|
| CONFIRMED | 87 |
| SHRUNK | 5 |
| GREW | 1 |
| RECORD CHANGED | 1 |

| flag | rows |
|---|---|
| small overlap (under 50 yd across) | 8 |
| trail line from the club saved copy (not re-read live) | 34 |

## For a person to look at

- **SHRUNK** `US-4444+US-4566@trail@40.600,-118.338`: live overlap is 94% smaller (0.1 ac vs 1.8 ac stored)
- **SHRUNK** `US-4566+US-4578@trail@42.460,-107.524`: live overlap is 43% smaller (8.3 ac vs 14.5 ac stored)
- **SHRUNK** `US-4566+US-4579@trail@39.018,-94.455`: live overlap is 37% smaller (7.6 ac vs 12.0 ac stored)
- **SHRUNK** `US-4575+US-9278@trail@36.014,-115.495`: live overlap is 80% smaller (0.5 ac vs 2.4 ac stored)
- **SHRUNK** `US-4578+US-9757@trail@37.797,-122.401`: live overlap is 50% smaller (1.7 ac vs 3.3 ac stored)
- **GREW** `US-4566+US-9254@trail@41.473,-119.457`: live overlap is 141% bigger (3.9 ac vs 1.6 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **RECORD CHANGED** `US-0676+US-7887@area@36.292,-114.047`: US-7887: 1 key record id(s) no longer in gis.blm.gov/lands/BLM_Natl_NLCS_NM_NCA_poly/MapServer/0/query: [461] | US-7887: found by name 'Grand Canyon-Parashant' near the spot as new id(s) [None] (geometry now: CONFIRMED: live overlap 692.7 ac vs 691.5 ac stored (+0%), 100% of the stored overlap still

The 2-fer file was not changed. A person and the club waiting room decide.
