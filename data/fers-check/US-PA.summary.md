# 2-fer accuracy check: US-PA

Run 2026-11-01T03:48:56Z → 2026-11-01T12:15:42Z (UTC) · tool 0.1.0 (2026-10-31) · complete
Live rows in the file: 76 · checked: 76 · skipped (dropped / merged): 560

| verdict | rows |
|---|---|
| CONFIRMED | 71 |
| SHRUNK | 4 |
| GREW | 1 |

| flag | rows |
|---|---|
| small overlap (under 50 yd across) | 29 |
| trail line from the club saved copy (not re-read live) | 4 |
| water-only | 2 |

## For a person to look at

- **SHRUNK** `US-0619+US-12235+US-8743@area@41.380,-78.856`: live overlap is 97% smaller (0.0 ac vs 1.1 ac stored)
- **SHRUNK** `US-0619+US-8743@area@41.380,-78.856`: live overlap is 97% smaller (0.0 ac vs 1.2 ac stored)
- **SHRUNK** `US-0684+US-8755@river@40.514,-75.153`: only 67% of the stored overlap is still inside the live overlap (10 m tolerance)
- **SHRUNK** `US-4357+US-5467@area@41.340,-78.154`: live overlap is 57% smaller (0.8 ac vs 1.8 ac stored)
- **GREW** `US-0619+US-12234@area@41.833,-79.264`: live overlap is 26% bigger (384.8 ac vs 304.6 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch

The 2-fer file was not changed. A person and the club waiting room decide.
