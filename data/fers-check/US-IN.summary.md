# 2-fer accuracy check: US-IN

Run 2026-11-01T00:42:55Z → 2026-11-01T12:15:37Z (UTC) · tool 0.1.0 (2026-10-31) · complete
Live rows in the file: 64 · checked: 64 · skipped (dropped / merged): 171

| verdict | rows |
|---|---|
| CONFIRMED | 60 |
| GREW | 2 |
| MOVED | 1 |
| NOT CHECKED | 1 |

| flag | rows |
|---|---|
| small overlap (under 50 yd across) | 12 |
| water-only | 1 |

## For a person to look at

- **GREW** `US-2264+US-4182@same land@41.707,-85.007`: live overlap is 664% bigger (522.2 ac vs 68.3 ac stored); 99% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-4164+US-5691@area@39.743,-87.076`: live overlap is 113% bigger (195.1 ac vs 91.6 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **MOVED** `US-12020+US-2266@same land@40.510,-86.818`: live overlap centre is 3280 m from the stored centre; 0% of the stored overlap is still inside it
- **NOT CHECKED** `US-10237+US-4218@area@41.678,-85.237`: key has no joined official outline for US-10237 (status 'pin')

The 2-fer file was not changed. A person and the club waiting room decide.
