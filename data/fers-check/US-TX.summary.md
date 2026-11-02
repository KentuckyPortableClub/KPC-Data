# 2-fer accuracy check: US-TX

Run 2026-11-01T04:09:30Z → 2026-11-01T12:15:43Z (UTC) · tool 0.1.0 (2026-10-31) · complete
Live rows in the file: 33 · checked: 33 · skipped (dropped / merged): 119

| verdict | rows |
|---|---|
| CONFIRMED | 29 |
| SHRUNK | 1 |
| GREW | 2 |
| MOVED | 1 |

| flag | rows |
|---|---|
| small overlap (under 50 yd across) | 7 |
| trail line from the club saved copy (not re-read live) | 2 |

## For a person to look at

- **SHRUNK** `US-6540+US-6597@river@29.614,-102.739`: only 5% of the stored overlap is still inside the live overlap (10 m tolerance)
- **GREW** `US-0633+US-6542@same land@32.720,-94.119`: live overlap is 78% bigger (14697.4 ac vs 8276.2 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-10509+US-4417@same land@30.633,-95.530`: live overlap is 337% bigger (780.7 ac vs 178.6 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **MOVED** `US-0006+US-6597@river@28.999,-103.286`: live overlap centre is 827 m from the stored centre; 5% of the stored overlap is still inside it

The 2-fer file was not changed. A person and the club waiting room decide.
