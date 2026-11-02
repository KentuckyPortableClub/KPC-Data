# 2-fer accuracy check: CA-YT

Run 2026-11-01T11:31:24Z → 2026-11-01T12:04:59Z (UTC) · tool 0.1.0 (2026-10-31) · complete
Live rows in the file: 6 · checked: 6 · skipped (dropped / merged): 88

| verdict | rows |
|---|---|
| CONFIRMED | 1 |
| RECORD CHANGED | 3 |
| SOURCE DOWN | 2 |

## For a person to look at

- **RECORD CHANGED** `CA-0044+CA-0842@area@61.233,-140.516`: CA-0044: key record Yukon parks :22 names a layer prefix not in us-key/layers.json | CA-0044: key record Yukon parks :23 names a layer prefix not in us-key/layers.json | CA-0842: key record Yukon parks :24 names a layer prefix not in us-key/layers.json (geometry now: SHRUNK: only 68% of the stored o
- **RECORD CHANGED** `CA-0106+CA-4623@area@68.375,-138.616`: CA-0106: key record Yukon parks :5 names a layer prefix not in us-key/layers.json | CA-4623: key record Yukon parks :6 names a layer prefix not in us-key/layers.json (geometry now: GONE: no overlap between the live official outlines near this spot)
- **RECORD CHANGED** `CA-0848+CA-4625@same land@61.928,-140.336`: CA-0848: key record Yukon parks :1 names a layer prefix not in us-key/layers.json | CA-4625: key record Yukon parks :1 names a layer prefix not in us-key/layers.json (geometry now: GONE: no overlap between the live official outlines near this spot)
- **SOURCE DOWN** `CA-0039+CA-0106@area@68.558,-140.978`: checker error on this row (retry; report if it repeats): GEOSException: IllegalArgumentException: Overlay input is mixed-dimension
- **SOURCE DOWN** `CA-0039+CA-4623@area@68.564,-140.893`: checker error on this row (retry; report if it repeats): GEOSException: IllegalArgumentException: Overlay input is mixed-dimension

The 2-fer file was not changed. A person and the club waiting room decide.
