# 2-fer accuracy check: US-VA

Run 2026-10-31T21:31:18Z → 2026-10-31T21:31:25Z (UTC) · tool 0.1.0 (2026-10-31) · complete
Live rows in the file: 55 · checked: 55 · skipped (dropped / merged): 112

| verdict | rows |
|---|---|
| CONFIRMED | 44 |
| SHRUNK | 7 |
| GREW | 4 |

| flag | rows |
|---|---|
| US-10507: saved line is only point(s): measured 100 ft from them | 1 |
| small overlap (under 50 yd across) | 15 |
| trail line from the club saved copy (not re-read live) | 34 |
| water-only | 1 |

## For a person to look at

- **SHRUNK** `US-0563+US-4581@river@38.630,-77.167`: only 68% of the stored overlap is still inside the live overlap (10 m tolerance)
- **SHRUNK** `US-0564+US-4564@trail@38.612,-77.253`: live overlap is 90% smaller (0.1 ac vs 0.8 ac stored)
- **SHRUNK** `US-10015+US-4581@river@38.683,-77.172`: only 57% of the stored overlap is still inside the live overlap (10 m tolerance)
- **SHRUNK** `US-1308+US-4581@river@38.654,-77.193`: only 57% of the stored overlap is still inside the live overlap (10 m tolerance)
- **SHRUNK** `US-1310+US-9903@trail@36.797,-80.921`: live overlap is 37% smaller (162.9 ac vs 259.0 ac stored)
- **SHRUNK** `US-9904+US-9906@trail@37.514,-79.530`: live overlap is 58% smaller (1.0 ac vs 2.5 ac stored)
- **SHRUNK** `US-9920+US-9946@trail@36.660,-81.542`: live overlap is 33% smaller (79.2 ac vs 118.7 ac stored)
- **GREW** `US-0561+US-0671@area@channel@37.908,-75.341`: live overlap is 108% bigger (759.9 ac vs 365.1 ac stored); 99% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-0569+US-4581@river@38.641,-77.242`: live overlap is 27% bigger (44.9 ac vs 35.3 ac stored); 94% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-1308+US-4564@trail@38.646,-77.170`: live overlap is 26% bigger (4.2 ac vs 3.3 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-4564+US-7804@trail@38.977,-77.240`: live overlap is 27% bigger (14.9 ac vs 11.7 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch

The 2-fer file was not changed. A person and the club waiting room decide.
