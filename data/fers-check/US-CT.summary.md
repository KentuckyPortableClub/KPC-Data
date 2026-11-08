# 2-fer accuracy check: US-CT

Run 2026-11-01T11:55:42Z → 2026-11-08T06:25:41Z (UTC) · tool 0.1.0 (2026-10-31) · complete
Live rows in the file: 34 · checked: 34 · skipped (dropped / merged): 40

| verdict | rows |
|---|---|
| CONFIRMED | 26 |
| SHRUNK | 4 |
| GREW | 1 |
| MOVED | 3 |

| flag | rows |
|---|---|
| small overlap (under 50 yd across) | 8 |
| trail line from the club saved copy (not re-read live) | 4 |
| water-only | 1 |

## For a person to look at

- **SHRUNK** `US-0882+US-10075@river@41.847,-72.953`: live overlap is 61% smaller (8.9 ac vs 22.6 ac stored)
- **SHRUNK** `US-0882+US-6869@river@41.939,-73.004`: live overlap is 63% smaller (30.5 ac vs 81.5 ac stored)
- **SHRUNK** `US-11013+US-12604@area@41.712,-72.437`: live overlap is 36% smaller (2.9 ac vs 4.5 ac stored)
- **SHRUNK** `US-11013+US-1669@area@41.714,-72.438`: live overlap is 29% smaller (2.0 ac vs 2.9 ac stored)
- **GREW** `US-1651+US-7532@area@41.792,-72.452`: live overlap is 63% bigger (2.5 ac vs 1.5 ac stored); 99% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **MOVED** `US-0881+US-1662@river@41.480,-72.341`: live overlap centre is 498 m from the stored centre; 19% of the stored overlap is still inside it
- **MOVED** `US-0882+US-6857@river@41.936,-73.002`: live overlap centre is 1138 m from the stored centre; 16% of the stored overlap is still inside it
- **MOVED** `US-1660+US-7541@same land@41.555,-72.451`: live overlap centre is 995 m from the stored centre; 0% of the stored overlap is still inside it

The 2-fer file was not changed. A person and the club waiting room decide.
