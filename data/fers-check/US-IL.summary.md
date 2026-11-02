# 2-fer accuracy check: US-IL

Run 2026-11-01T00:41:36Z → 2026-11-01T12:15:37Z (UTC) · tool 0.1.0 (2026-10-31) · complete
Live rows in the file: 24 · checked: 24 · skipped (dropped / merged): 80

| verdict | rows |
|---|---|
| CONFIRMED | 21 |
| SHRUNK | 2 |
| GREW | 1 |

| flag | rows |
|---|---|
| small overlap (under 50 yd across) | 9 |
| trail line from the club saved copy (not re-read live) | 2 |
| water-only | 1 |

## For a person to look at

- **SHRUNK** `US-4573+US-4576@trail@41.332,-110.365`: live overlap is 26% smaller (60.2 ac vs 81.2 ac stored)
- **SHRUNK** `US-4573+US-4576@trail@42.485,-107.428`: live overlap is 48% smaller (793.2 ac vs 1518.8 ac stored)
- **GREW** `US-0282+US-4482@area@37.592,-89.088`: live overlap is 135% bigger (21.0 ac vs 9.0 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch

The 2-fer file was not changed. A person and the club waiting room decide.
