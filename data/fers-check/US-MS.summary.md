# 2-fer accuracy check: US-MS

Run 2026-11-01T02:11:23Z → 2026-11-01T12:15:39Z (UTC) · tool 0.1.0 (2026-10-31) · complete
Live rows in the file: 15 · checked: 15 · skipped (dropped / merged): 80

| verdict | rows |
|---|---|
| CONFIRMED | 10 |
| SHRUNK | 2 |
| MOVED | 1 |
| NOT CHECKED | 2 |

| flag | rows |
|---|---|
| small overlap (under 50 yd across) | 6 |
| trail line from the club saved copy (not re-read live) | 4 |

## For a person to look at

- **SHRUNK** `US-4495+US-7079@area@32.803,-90.838`: live overlap is 93% smaller (0.2 ac vs 3.2 ac stored)
- **SHRUNK** `US-4560+US-7096@trail@34.506,-88.326`: live overlap is 33% smaller (3.3 ac vs 5.0 ac stored)
- **MOVED** `US-4560+US-7113@trail@32.568,-89.899`: live overlap centre is 209 m from the stored centre; 17% of the stored overlap is still inside it
- **NOT CHECKED** `US-7095+US-7096@area@34.479,-88.347`: US-7095: layer mszw is a downloaded file, not a live map
- **NOT CHECKED** `US-7108+US-7112@area@30.676,-88.602`: US-7108: layer mszw is a downloaded file, not a live map

The 2-fer file was not changed. A person and the club waiting room decide.
