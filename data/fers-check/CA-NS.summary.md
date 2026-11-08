# 2-fer accuracy check: CA-NS

Run 2026-11-08T11:45:59Z → 2026-11-08T12:04:01Z (UTC) · tool 0.1.0 (2026-10-31) · complete
Live rows in the file: 15 · checked: 15 · skipped (dropped / merged): 207

| verdict | rows |
|---|---|
| CONFIRMED | 12 |
| GREW | 1 |
| MOVED | 1 |
| NOT CHECKED | 1 |

| flag | rows |
|---|---|
| small overlap (under 50 yd across) | 1 |
| water-only | 1 |

## For a person to look at

- **GREW** `CA-0935+CA-1822@same land@43.865,-64.951`: live overlap is 58% bigger (104.9 ac vs 66.2 ac stored); 95% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **MOVED** `CA-0935+CA-1824@same land@43.839,-65.001`: live overlap centre is 1144 m from the stored centre; 0% of the stored overlap is still inside it
- **NOT CHECKED** `CA-1843+CA-6136@same land@44.245,-65.282`: key has no joined official outline for CA-6136 (status 'pin')

The 2-fer file was not changed. A person and the club waiting room decide.
