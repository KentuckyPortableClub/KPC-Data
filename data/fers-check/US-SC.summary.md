# 2-fer accuracy check: US-SC

Run 2026-11-01T03:55:33Z → 2026-11-08T12:06:03Z (UTC) · tool 0.1.0 (2026-10-31) · complete
Live rows in the file: 32 · checked: 32 · skipped (dropped / merged): 202

| verdict | rows |
|---|---|
| CONFIRMED | 23 |
| SHRUNK | 1 |
| GREW | 1 |
| GONE | 6 |
| NOT CHECKED | 1 |

| flag | rows |
|---|---|
| small overlap (under 50 yd across) | 4 |
| trail line from the club saved copy (not re-read live) | 8 |

## For a person to look at

- **SHRUNK** `US-3874+US-5488@area@34.564,-79.925`: live overlap is 38% smaller (1059.5 ac vs 1707.7 ac stored)
- **GREW** `US-4577+US-6936@trail@35.786,-82.013`: live overlap is 34% bigger (1.2 ac vs 0.9 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GONE** `US-0518+US-9208@area@33.101,-79.365`: no overlap between the live official outlines near this spot
- **GONE** `US-12589+US-3879@area@34.530,-82.875`: no overlap between the live official outlines near this spot
- **GONE** `US-2911+US-3879@area@34.424,-82.825`: no overlap between the live official outlines near this spot
- **GONE** `US-3879+US-3897@area@34.545,-83.097`: no overlap between the live official outlines near this spot
- **GONE** `US-3879+US-9225@area@34.680,-83.326`: no overlap between the live official outlines near this spot
- **GONE** `US-4522+US-9208@area@33.116,-79.417`: no overlap between the live official outlines near this spot
- **NOT CHECKED** `US-4577+US-6246@trail@36.153,-82.056`: park is not in any boundary key that was loaded

The 2-fer file was not changed. A person and the club waiting room decide.
