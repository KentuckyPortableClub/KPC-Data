# 2-fer accuracy check: CA-YT

Run 2026-11-01T11:31:24Z → 2026-11-08T06:21:45Z (UTC) · tool 0.1.0 (2026-10-31) · complete
Live rows in the file: 6 · checked: 6 · skipped (dropped / merged): 68

| verdict | rows |
|---|---|
| CONFIRMED | 3 |
| RECORD CHANGED | 1 |
| SOURCE DOWN | 2 |

## For a person to look at

- **RECORD CHANGED** `CA-0106+CA-4623@area@68.375,-138.616`: CA-0106: key record Yukon parks :5 names a layer prefix not in us-key/layers.json | CA-4623: key record Yukon parks :6 names a layer prefix not in us-key/layers.json (geometry now: GONE: no overlap between the live official outlines near this spot)
- **SOURCE DOWN** `CA-0039+CA-0106@area@68.569,-140.923`: checker error on this row (retry; report if it repeats): GEOSException: IllegalArgumentException: Overlay input is mixed-dimension
- **SOURCE DOWN** `CA-0039+CA-4623@area@68.566,-140.906`: checker error on this row (retry; report if it repeats): GEOSException: IllegalArgumentException: Overlay input is mixed-dimension

The 2-fer file was not changed. A person and the club waiting room decide.
