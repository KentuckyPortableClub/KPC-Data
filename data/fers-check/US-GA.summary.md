# 2-fer accuracy check: US-GA

Run 2026-11-01T00:27:29Z → 2026-11-08T06:25:42Z (UTC) · tool 0.1.0 (2026-10-31) · complete
Live rows in the file: 55 · checked: 55 · skipped (dropped / merged): 234

| verdict | rows |
|---|---|
| CONFIRMED | 49 |
| SHRUNK | 2 |
| GREW | 2 |
| MOVED | 1 |
| NOT CHECKED | 1 |

| flag | rows |
|---|---|
| small overlap (under 50 yd across) | 5 |

## For a person to look at

- **SHRUNK** `US-3741+US-7899@same land@34.617,-84.638`: live overlap is 52% smaller (4206.1 ac vs 8742.6 ac stored)
- **SHRUNK** `US-7138+US-7447@area@34.700,-83.928`: live overlap is 53% smaller (38.3 ac vs 81.0 ac stored)
- **GREW** `US-2167+US-4473@area@34.911,-83.426`: live overlap is 309% bigger (4.4 ac vs 1.1 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-2197+US-9786@area@30.788,-84.795`: live overlap is 86% bigger (4175.4 ac vs 2241.5 ac stored); 89% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **MOVED** `US-12417+US-4473@area@34.739,-84.340`: live overlap centre is 10429 m from the stored centre; 0% of the stored overlap is still inside it
- **NOT CHECKED** `US-7141+US-7467@same land@33.440,-83.734`: key has no joined official outline for US-7467 (status 'pin')

The 2-fer file was not changed. A person and the club waiting room decide.
