# 2-fer accuracy check: US-MD

Run 2026-11-01T00:56:24Z → 2026-11-01T12:15:37Z (UTC) · tool 0.1.0 (2026-10-31) · complete
Live rows in the file: 155 · checked: 155 · skipped (dropped / merged): 617

| verdict | rows |
|---|---|
| CONFIRMED | 123 |
| SHRUNK | 17 |
| GREW | 10 |
| MOVED | 5 |

| flag | rows |
|---|---|
| small overlap (under 50 yd across) | 75 |
| trail line from the club saved copy (not re-read live) | 116 |
| water-only | 1 |

## For a person to look at

- **SHRUNK** `US-0332+US-4567@river@39.045,-76.211`: live overlap is 27% smaller (137.7 ac vs 188.5 ac stored)
- **SHRUNK** `US-0335+US-4567+US-4581@river@39.598,-76.129`: live overlap is 99% smaller (0.0 ac vs 1.8 ac stored)
- **SHRUNK** `US-0335+US-4567@river@39.598,-76.129`: live overlap is 99% smaller (0.0 ac vs 1.8 ac stored)
- **SHRUNK** `US-0670+US-7778@area@38.967,-77.161`: live overlap is 88% smaller (0.1 ac vs 1.1 ac stored)
- **SHRUNK** `US-10784+US-1568@same land@39.496,-79.310`: only 70% of the stored overlap is still inside the live overlap (10 m tolerance)
- **SHRUNK** `US-1570+US-4564@trail@39.614,-78.013`: live overlap is 95% smaller (0.0 ac vs 0.8 ac stored)
- **SHRUNK** `US-1590+US-4567+US-4581@river@38.060,-76.349`: live overlap is 37% smaller (55.2 ac vs 87.9 ac stored)
- **SHRUNK** `US-1596+US-4564@trail@39.068,-77.352`: live overlap is 90% smaller (0.6 ac vs 6.2 ac stored)
- **SHRUNK** `US-1599+US-4567+US-4581@river@38.211,-76.743`: live overlap is 66% smaller (17.4 ac vs 50.9 ac stored)
- **SHRUNK** `US-1599+US-4581@river@38.211,-76.743`: live overlap is 66% smaller (17.4 ac vs 50.9 ac stored)
- **SHRUNK** `US-1601+US-4567+US-4581@river@39.598,-76.129`: live overlap is 69% smaller (16.7 ac vs 53.1 ac stored)
- **SHRUNK** `US-1601+US-4567@river@39.598,-76.129`: live overlap is 69% smaller (16.7 ac vs 53.1 ac stored)
- **SHRUNK** `US-4567+US-7735@river@37.944,-75.860`: live overlap is 50% smaller (486.4 ac vs 976.0 ac stored)
- **SHRUNK** `US-4567+US-7736@river@38.156,-75.915`: live overlap is 58% smaller (66.8 ac vs 160.2 ac stored)
- **SHRUNK** `US-4567+US-7739@river@38.089,-75.781`: live overlap is 72% smaller (21.1 ac vs 75.7 ac stored)
- **SHRUNK** `US-4567+US-7749@river@37.966,-75.809`: only 74% of the stored overlap is still inside the live overlap (10 m tolerance)
- **SHRUNK** `US-4766+US-7765@area@39.690,-78.428`: live overlap is 31% smaller (1.2 ac vs 1.7 ac stored)
- **GREW** `US-0334+US-4581@river@39.073,-76.756`: live overlap is 74% bigger (61.3 ac vs 35.3 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-0335+US-4567+US-4581@river@39.495,-76.083`: live overlap is 66% bigger (0.8 ac vs 0.5 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-0335+US-4581@river@39.598,-76.129`: live overlap is 39% bigger (0.6 ac vs 0.4 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-1575+US-1598@area@39.529,-77.611`: live overlap is 43% bigger (2.5 ac vs 1.8 ac stored); 90% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-1577+US-4567@river@39.405,-76.379`: live overlap is 54% bigger (37.4 ac vs 24.3 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-1588+US-4567+US-4581@river@39.231,-76.657`: live overlap is 69% bigger (22.6 ac vs 13.4 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-1588+US-4567@river@39.215,-76.703`: live overlap is 52% bigger (31.4 ac vs 20.7 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-1588+US-4581@river@39.215,-76.703`: live overlap is 43% bigger (27.3 ac vs 19.1 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-4564+US-7730@trail@39.071,-77.410`: live overlap is 26% bigger (0.7 ac vs 0.5 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-4567+US-7778@river@39.037,-77.277`: live overlap is 34% bigger (6.1 ac vs 4.6 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **MOVED** `US-0333+US-4567+US-4581@river@38.038,-76.010`: live overlap centre is 3073 m from the stored centre; 5% of the stored overlap is still inside it
- **MOVED** `US-4567+US-7738@river@38.260,-75.827`: live overlap centre is 2078 m from the stored centre; 0% of the stored overlap is still inside it
- **MOVED** `US-4567+US-7740@river@38.375,-75.925`: live overlap centre is 1442 m from the stored centre; 22% of the stored overlap is still inside it
- **MOVED** `US-4581+US-7761@river@38.535,-76.522`: live overlap centre is 825 m from the stored centre; 22% of the stored overlap is still inside it
- **MOVED** `US-6384+US-7779@same land@38.106,-75.497`: live overlap centre is 1709 m from the stored centre; 1% of the stored overlap is still inside it

The 2-fer file was not changed. A person and the club waiting room decide.
