# 2-fer accuracy check: US-OK

Run 2026-11-01T02:42:37Z → 2026-11-08T06:28:17Z (UTC) · tool 0.1.0 (2026-10-31) · complete
Live rows in the file: 44 · checked: 44 · skipped (dropped / merged): 126

| verdict | rows |
|---|---|
| CONFIRMED | 40 |
| SHRUNK | 3 |
| GREW | 1 |

| flag | rows |
|---|---|
| small overlap (under 50 yd across) | 9 |
| trail line from the club saved copy (not re-read live) | 4 |
| water-only | 4 |

## For a person to look at

- **SHRUNK** `US-12684+US-8321@trail@34.709,-94.682`: live overlap is 47% smaller (69.7 ac vs 131.1 ac stored)
- **SHRUNK** `US-2795+US-6361@area@34.359,-95.888`: live overlap is 66% smaller (0.8 ac vs 2.2 ac stored)
- **SHRUNK** `US-6341+US-6360@area@34.324,-94.699`: live overlap is 25% smaller (1.7 ac vs 2.2 ac stored)
- **GREW** `US-12684+US-6366@area@34.770,-94.762`: live overlap is 29% bigger (4748.2 ac vs 3681.5 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch

The 2-fer file was not changed. A person and the club waiting room decide.
