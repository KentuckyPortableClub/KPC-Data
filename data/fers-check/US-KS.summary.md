# 2-fer accuracy check: US-KS

Run 2026-11-01T00:46:48Z → 2026-11-01T12:15:37Z (UTC) · tool 0.1.0 (2026-10-31) · complete
Live rows in the file: 24 · checked: 24 · skipped (dropped / merged): 38

| verdict | rows |
|---|---|
| CONFIRMED | 18 |
| SHRUNK | 3 |
| GREW | 2 |
| MOVED | 1 |

| flag | rows |
|---|---|
| small overlap (under 50 yd across) | 3 |
| trail line from the club saved copy (not re-read live) | 1 |
| water-only | 1 |

## For a person to look at

- **SHRUNK** `US-0293+US-7935@area@38.226,-94.673`: live overlap is 32% smaller (14.4 ac vs 21.4 ac stored)
- **SHRUNK** `US-2331+US-7920@area@37.743,-97.771`: live overlap is 28% smaller (37.2 ac vs 51.4 ac stored)
- **SHRUNK** `US-2350+US-5718@trail@38.617,-95.270`: live overlap is 43% smaller (0.8 ac vs 1.4 ac stored)
- **GREW** `US-2333+US-7402@same land@37.636,-94.812`: live overlap is 388% bigger (529.3 ac vs 108.4 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-7411+US-7949@same land@37.797,-95.844`: live overlap is 1341% bigger (1738.0 ac vs 120.6 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **MOVED** `US-2336+US-7925@same land@37.914,-96.768`: live overlap centre is 4198 m from the stored centre; 0% of the stored overlap is still inside it

The 2-fer file was not changed. A person and the club waiting room decide.
