# 2-fer accuracy check: US-AR

Run 2026-11-01T11:46:12Z → 2026-11-08T06:22:05Z (UTC) · tool 0.1.0 (2026-10-31) · complete
Live rows in the file: 17 · checked: 17 · skipped (dropped / merged): 129

| verdict | rows |
|---|---|
| CONFIRMED | 14 |
| SHRUNK | 2 |
| GREW | 1 |

| flag | rows |
|---|---|
| small overlap (under 50 yd across) | 6 |
| trail line from the club saved copy (not re-read live) | 3 |
| water-only | 1 |

## For a person to look at

- **SHRUNK** `US-0164+US-7319@area@35.067,-91.314`: live overlap is 39% smaller (0.9 ac vs 1.6 ac stored)
- **SHRUNK** `US-4424+US-8321@trail@34.676,-94.328`: only 60% of the stored overlap is still inside the live overlap (10 m tolerance)
- **GREW** `US-1096+US-12765@same land@33.348,-93.180`: live overlap is 70% bigger (332.9 ac vs 196.2 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch

The 2-fer file was not changed. A person and the club waiting room decide.
