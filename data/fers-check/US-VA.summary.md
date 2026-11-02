# 2-fer accuracy check: US-VA

Run 2026-10-31T21:31:18Z → 2026-11-01T12:15:43Z (UTC) · tool 0.1.0 (2026-10-31) · complete
Live rows in the file: 134 · checked: 134 · skipped (dropped / merged): 387

| verdict | rows |
|---|---|
| CONFIRMED | 105 |
| SHRUNK | 17 |
| GREW | 9 |
| MOVED | 2 |
| GONE | 1 |

| flag | rows |
|---|---|
| US-10507: saved line is only point(s): measured 100 ft from them | 1 |
| small overlap (under 50 yd across) | 42 |
| trail line from the club saved copy (not re-read live) | 109 |
| water-only | 2 |

## For a person to look at

- **SHRUNK** `US-0564+US-4564@trail@38.612,-77.253`: live overlap is 90% smaller (0.1 ac vs 0.8 ac stored)
- **SHRUNK** `US-1310+US-9903@trail@36.797,-80.921`: live overlap is 37% smaller (162.9 ac vs 259.0 ac stored)
- **SHRUNK** `US-4526+US-9950@area@37.434,-80.623`: only 74% of the stored overlap is still inside the live overlap (10 m tolerance)
- **SHRUNK** `US-4556+US-4564@trail@39.330,-77.681`: live overlap is 31% smaller (13.0 ac vs 18.9 ac stored)
- **SHRUNK** `US-4556+US-9904@trail@37.510,-79.524`: live overlap is 31% smaller (1.6 ac vs 2.3 ac stored)
- **SHRUNK** `US-4556+US-9906@trail@37.507,-79.536`: live overlap is 59% smaller (1.0 ac vs 2.4 ac stored)
- **SHRUNK** `US-4556+US-9920@trail@36.658,-81.538`: live overlap is 67% smaller (0.8 ac vs 2.3 ac stored)
- **SHRUNK** `US-4556+US-9923@trail@36.631,-81.783`: live overlap is 40% smaller (4.1 ac vs 6.9 ac stored)
- **SHRUNK** `US-4564+US-4567@trail@38.897,-76.961`: live overlap is 29% smaller (1.6 ac vs 2.3 ac stored)
- **SHRUNK** `US-4564+US-4567@trail@38.924,-77.112`: live overlap is 59% smaller (6.6 ac vs 16.1 ac stored)
- **SHRUNK** `US-4564+US-4582@trail@38.683,-77.217`: live overlap is 52% smaller (2.6 ac vs 5.4 ac stored)
- **SHRUNK** `US-4564+US-4582@trail@38.709,-77.161`: live overlap is 54% smaller (9.6 ac vs 20.9 ac stored)
- **SHRUNK** `US-4567+US-4581@trail@38.915,-76.949`: live overlap is 39% smaller (28.9 ac vs 47.5 ac stored)
- **SHRUNK** `US-4567+US-7788@river@37.256,-76.025`: live overlap is 26% smaller (0.9 ac vs 1.2 ac stored)
- **SHRUNK** `US-4567+US-9934@trail@37.413,-79.136`: live overlap is 36% smaller (5.3 ac vs 8.3 ac stored)
- **SHRUNK** `US-9904+US-9906@trail@37.514,-79.530`: live overlap is 58% smaller (1.0 ac vs 2.5 ac stored)
- **SHRUNK** `US-9920+US-9946@trail@36.660,-81.542`: live overlap is 33% smaller (79.2 ac vs 118.7 ac stored)
- **GREW** `US-0561+US-0671@area@channel@37.908,-75.341`: live overlap is 108% bigger (759.9 ac vs 365.1 ac stored); 99% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-0564+US-4567+US-4581@river@38.612,-77.246`: live overlap is 33% bigger (30.7 ac vs 23.2 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-0569+US-4567+US-4581@river@38.641,-77.242`: live overlap is 27% bigger (44.9 ac vs 35.3 ac stored); 94% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-10015+US-4567@river@38.695,-77.160`: live overlap is 31% bigger (125.0 ac vs 95.6 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-1291+US-4567@river@37.787,-76.595`: live overlap is 28% bigger (2.6 ac vs 2.1 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-1308+US-4564@trail@38.646,-77.170`: live overlap is 26% bigger (4.2 ac vs 3.3 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-1326+US-4567@river@37.419,-76.716`: live overlap is 37% bigger (58.1 ac vs 42.4 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-4564+US-7804@trail@38.977,-77.240`: live overlap is 27% bigger (14.9 ac vs 11.7 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-4567+US-5526@river@37.810,-77.125`: live overlap is 29% bigger (12.6 ac vs 9.7 ac stored); 97% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **MOVED** `US-4526+US-9949@area@37.439,-80.473`: live overlap centre is 2753 m from the stored centre; 1% of the stored overlap is still inside it
- **MOVED** `US-4567+US-7784@river@37.413,-76.256`: live overlap centre is 469 m from the stored centre; 0% of the stored overlap is still inside it
- **GONE** `US-4556+US-9903@trail@36.670,-81.487`: no overlap between the live official outlines near this spot

The 2-fer file was not changed. A person and the club waiting room decide.
