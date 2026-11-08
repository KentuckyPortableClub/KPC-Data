# Hand-downloaded layers — Quality check (Nov 8, 2026)

Research handoffs 20261108-1740 / 1745 / 1750 / 1755 CST. Brandon downloaded the layers by hand (live hosts are robots-blocked). Pins were never moved. US rules hash a066624520b4 and CA rules hash 8feccbb7d9ee are unchanged (overrides and ledger only).

## Counts

| Set | Polygons | Verified leads | Joined (new) | Held for Brandon | Possible candidates (no pin) | Already outlined |
|---|---|---|---|---|---|---|
| GA state parks | 60 | 56 | 2 (US-2200, US-3722) | — | 3 (Balls Ferry, Mossy Creek, Bush Head Shoals) | rest |
| TX state parks | 116 | 88 | 11 | US-3505 (333 m) | 5 | rest; US-3510 keeps WMA |
| TX WMA | 80 | 46 | 3 | US-6571/6565/6551/6535/6550/6572 | 4 | rest |
| PA SGL | 320 | 308 | 2 (US-8745, US-8911) | — | 0 | 306 |
| GA WMA/PFA | 209 | 132 | 5 | US-3751, US-9770, US-4650, US-3729, US-7896 | 38 | rest |
| MB provincial parks | 93 | 86 | 1 (CA-2373) | CA-0527 (111 km), CA-0558 (69 km), CA-0551 (2.7 km) | 4 | rest |

**Totals:** 24 hand joins · 15 held · 54 possible candidates · 665 already outlined · 1 explicit NO (US-12418 never gets Tallulah Gorge SP polygon).

## Decisions called out

- US-2200 Okefenokee SP → Stephen C. Foster polygon (sggab32).
- US-2199 already Dukes Creek - Smithgall Woods.
- US-12418 Tallulah Gorge WMA: NO on sggab12.
- US-3510 Powderhorn: use existing WMA join, not the state-park polygon.
- CA-0527 / CA-0558: held as likely pin/name problems.
- Manitoba file kept under `data/waiting/outline-sources/hand-layers/ca-mb-provparks.geojson` (replaces missing shapes; no live services.arcgis.com).

Files: `hand-layers-nov8.json`, `hand-layers/`, ledger source `research-hand-layers-nov8`.
