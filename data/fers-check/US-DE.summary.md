# 2-fer accuracy check: US-DE

Run 2026-11-01T12:00:54Z → 2026-11-01T12:05:31Z (UTC) · tool 0.1.0 (2026-10-31) · complete
Live rows in the file: 38 · checked: 38 · skipped (dropped / merged): 107

| verdict | rows |
|---|---|
| CONFIRMED | 27 |
| SHRUNK | 4 |
| GREW | 5 |
| MOVED | 1 |
| NOT CHECKED | 1 |

| flag | rows |
|---|---|
| small overlap (under 50 yd across) | 10 |
| trail line from the club saved copy (not re-read live) | 15 |
| water-only | 3 |

## For a person to look at

- **SHRUNK** `US-0898+US-4582@trail@39.707,-75.654`: live overlap is 48% smaller (2.2 ac vs 4.1 ac stored)
- **SHRUNK** `US-4567+US-4581@trail@39.472,-75.968`: live overlap is 63% smaller (4.1 ac vs 10.9 ac stored)
- **SHRUNK** `US-4567+US-4582@trail@39.608,-75.828`: live overlap is 55% smaller (1.3 ac vs 2.9 ac stored)
- **SHRUNK** `US-4582+US-9878@trail@39.777,-75.490`: live overlap is 48% smaller (2.0 ac vs 3.9 ac stored)
- **GREW** `US-0229+US-9882@area@39.185,-75.439`: live overlap is 28% bigger (5.7 ac vs 4.5 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-10659+US-7646@same land@39.459,-75.593`: live overlap is 71% bigger (1401.4 ac vs 818.2 ac stored); 99% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-10671+US-4567@river@38.642,-75.544`: live overlap is 26% bigger (14.0 ac vs 11.1 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-10682+US-5722@same land@39.035,-75.519`: live overlap is 47% bigger (148.1 ac vs 101.0 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-11812+US-1742@same land@38.523,-75.471`: live overlap is 33% bigger (1300.0 ac vs 981.0 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **MOVED** `US-11811+US-4567@river@38.557,-75.560`: live overlap centre is 376 m from the stored centre; 0% of the stored overlap is still inside it
- **NOT CHECKED** `US-0898+US-6433@area@39.767,-75.763`: park is not in any boundary key that was loaded

The 2-fer file was not changed. A person and the club waiting room decide.
