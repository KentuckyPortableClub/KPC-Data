# 2-fer accuracy check: US-MO

Run 2026-11-01T02:07:46Z → 2026-11-01T12:15:39Z (UTC) · tool 0.1.0 (2026-10-31) · complete
Live rows in the file: 55 · checked: 55 · skipped (dropped / merged): 307

| verdict | rows |
|---|---|
| CONFIRMED | 48 |
| SHRUNK | 1 |
| GREW | 3 |
| MOVED | 2 |
| GONE | 1 |

| flag | rows |
|---|---|
| small overlap (under 50 yd across) | 11 |
| trail line from the club saved copy (not re-read live) | 10 |

## For a person to look at

- **SHRUNK** `US-1777+US-3355@area@39.791,-93.233`: live overlap is 75% smaller (11.6 ac vs 47.2 ac stored)
- **GREW** `US-0831+US-11015@same land@38.901,-94.530`: live overlap is 82% bigger (11.1 ac vs 6.1 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-1772+US-3356@same land@39.493,-91.786`: live overlap is 64% bigger (1.8 ac vs 1.1 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-1788+US-7836@trail@37.567,-90.724`: live overlap is 100% bigger (1.9 ac vs 1.0 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **MOVED** `US-11138+US-1780@same land@36.597,-93.824`: live overlap centre is 3035 m from the stored centre; 0% of the stored overlap is still inside it
- **MOVED** `US-13161+US-1780@area@36.582,-93.852`: live overlap centre is 3476 m from the stored centre; 0% of the stored overlap is still inside it
- **GONE** `US-11138+US-13161@same land@36.594,-93.818`: no overlap between the live official outlines near this spot

The 2-fer file was not changed. A person and the club waiting room decide.
