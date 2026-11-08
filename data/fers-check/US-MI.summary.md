# 2-fer accuracy check: US-MI

Run 2026-11-01T01:00:54Z → 2026-11-08T12:05:59Z (UTC) · tool 0.1.0 (2026-10-31) · complete
Live rows in the file: 99 · checked: 99 · skipped (dropped / merged): 313

| verdict | rows |
|---|---|
| CONFIRMED | 71 |
| SHRUNK | 10 |
| GREW | 13 |
| MOVED | 2 |
| GONE | 2 |
| RECORD CHANGED | 1 |

| flag | rows |
|---|---|
| small overlap (under 50 yd across) | 15 |
| trail line from the club saved copy (not re-read live) | 49 |
| water-only | 6 |

## For a person to look at

- **SHRUNK** `US-0346+US-13184@trail@42.100,-83.197`: live overlap is 56% smaller (9.4 ac vs 21.3 ac stored)
- **SHRUNK** `US-12786+US-4488@river@44.637,-83.927`: only 61% of the stored overlap is still inside the live overlap (10 m tolerance)
- **SHRUNK** `US-12788+US-4489@river@46.609,-90.080`: only 58% of the stored overlap is still inside the live overlap (10 m tolerance)
- **SHRUNK** `US-12793+US-13184@trail@46.277,-89.308`: live overlap is 94% smaller (0.9 ac vs 14.9 ac stored)
- **SHRUNK** `US-12796+US-4583@river@44.197,-85.775`: only 44% of the stored overlap is still inside the live overlap (10 m tolerance)
- **SHRUNK** `US-12797+US-13184@trail@46.388,-89.688`: live overlap is 93% smaller (1.2 ac vs 16.6 ac stored)
- **SHRUNK** `US-13174+US-13184@trail@45.633,-84.487`: live overlap is 52% smaller (0.7 ac vs 1.5 ac stored)
- **SHRUNK** `US-13176+US-13184@trail@45.780,-84.731`: live overlap is 55% smaller (0.6 ac vs 1.3 ac stored)
- **SHRUNK** `US-13184+US-1488@trail@46.094,-88.420`: live overlap is 28% smaller (8.6 ac vs 11.9 ac stored)
- **SHRUNK** `US-13184+US-1524@trail@46.676,-85.633`: live overlap is 34% smaller (46.0 ac vs 69.7 ac stored)
- **GREW** `US-12786+US-13172@river@44.643,-83.941`: live overlap is 878% bigger (5.1 ac vs 0.5 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-12789+US-4487@river@46.020,-84.730`: live overlap is 173% bigger (11.4 ac vs 4.2 ac stored); 95% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-12792+US-4583@area@channel@44.261,-86.041`: live overlap is 663% bigger (26.0 ac vs 3.4 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-12793+US-3306@area@channel@46.408,-89.131`: live overlap is 472% bigger (3.1 ac vs 0.5 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-12794+US-13184@river@46.193,-88.995`: live overlap is 1680% bigger (0.9 ac vs 0.1 ac stored); 96% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-12794+US-4489@river@46.253,-88.740`: live overlap is 430% bigger (15.3 ac vs 2.9 ac stored); 98% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-12795+US-6754@area@43.932,-86.416`: live overlap is 823% bigger (520.3 ac vs 56.4 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-13172+US-6797@trail@45.187,-84.153`: live overlap is 50% bigger (1.6 ac vs 1.0 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-13176+US-6826@trail@45.425,-84.848`: live overlap is 842% bigger (8.4 ac vs 0.9 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-13179+US-1555@trail@43.876,-85.508`: live overlap is 663% bigger (1.5 ac vs 0.2 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-13184+US-1513@trail@42.444,-84.180`: live overlap is 303% bigger (1.1 ac vs 0.3 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-13184+US-3383@trail@42.759,-83.206`: live overlap is 681% bigger (8.8 ac vs 1.1 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-3318+US-6816@same land@46.086,-84.064`: live overlap is 114% bigger (7.3 ac vs 3.4 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **MOVED** `US-12790+US-4487@river@46.368,-85.085`: live overlap centre is 1823 m from the stored centre; 16% of the stored overlap is still inside it
- **MOVED** `US-12798+US-13184@trail@45.895,-86.701`: live overlap centre is 220 m from the stored centre; 13% of the stored overlap is still inside it
- **GONE** `US-13184+US-1511@trail@42.411,-86.264`: no overlap between the live official outlines near this spot
- **GONE** `US-6694+US-6729@same land@43.165,-84.464`: no overlap between the live official outlines near this spot
- **RECORD CHANGED** `US-3313+US-6705@area@42.825,-83.497`: US-6705: 1 key record id(s) no longer in services3.arcgis.com/Jdnp1TjADvSDxMAX/DNRWILDLandsOPENDATA/FeatureServer/2/query: [112] | US-6705: found by name 'Holly Wildlife Unit of Holly State Recreation Area' near the spot as new id(s) [None] (geometry now: CONFIRMED: live overlap 1432.8 ac vs 1744.2 

The 2-fer file was not changed. A person and the club waiting room decide.
