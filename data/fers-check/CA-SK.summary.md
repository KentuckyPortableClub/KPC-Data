# 2-fer accuracy check: CA-SK

Run 2026-11-01T11:30:22Z → 2026-11-08T06:21:31Z (UTC) · tool 0.1.0 (2026-10-31) · complete
Live rows in the file: 33 · checked: 33 · skipped (dropped / merged): 19

| verdict | rows |
|---|---|
| CONFIRMED | 16 |
| SHRUNK | 1 |
| GREW | 2 |
| RECORD CHANGED | 14 |

| flag | rows |
|---|---|
| CA-6151: saved line is only point(s): measured 100 ft from them | 1 |
| trail line from the club saved copy (not re-read live) | 10 |

## For a person to look at

- **SHRUNK** `CA-6146+CA-6147@trail@53.676,-106.669`: live overlap is 63% smaller (0.8 ac vs 2.3 ac stored)
- **GREW** `CA-0051+CA-2711@same land@51.334,-105.226`: live overlap is 43177% bigger (1036.6 ac vs 2.4 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `CA-2879+CA-2880@same land@51.184,-102.588`: live overlap is 146% bigger (1818.9 ac vs 739.8 ac stored); 98% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **RECORD CHANGED** `CA-0051+CA-1118@area@51.354,-105.214`: CA-1118: key record Saskatchewan~6:43 names a layer prefix not in us-key/layers.json (geometry now: GONE: no overlap between the live official outlines near this spot)
- **RECORD CHANGED** `CA-0075+CA-6148@trail@53.970,-106.292`: CA-0075: key record SK-PT Govern:157 names a layer prefix not in us-key/layers.json (geometry now: SHRUNK: live overlap is 32% smaller (17.3 ac vs 25.3 ac stored))
- **RECORD CHANGED** `CA-0082+CA-1146@same land@52.710,-107.218`: CA-0082: key record Saskatchewan~6:77 names a layer prefix not in us-key/layers.json | CA-1146: key record Saskatchewan~6:77 names a layer prefix not in us-key/layers.json (geometry now: GONE: no overlap between the live official outlines near this spot)
- **RECORD CHANGED** `CA-0082+CA-2819@same land@52.692,-107.162`: CA-0082: key record Saskatchewan~6:77 names a layer prefix not in us-key/layers.json (geometry now: GREW: live overlap is 30% bigger (13022.1 ac vs 10000.8 ac stored); 98% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-ap
- **RECORD CHANGED** `CA-0591+CA-6057@same land@53.960,-102.265`: CA-0591: key record SK-ALL Gover:3281 names a layer prefix not in us-key/layers.json (geometry now: GREW: live overlap is 62% bigger (11.7 ac vs 7.2 ac stored); 85% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or
- **RECORD CHANGED** `CA-0600+CA-6064@same land@53.571,-109.793`: CA-0600: key record SK-ALL Gover:3306 names a layer prefix not in us-key/layers.json (geometry now: GREW: live overlap is 123% bigger (32.5 ac vs 14.6 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply,
- **RECORD CHANGED** `CA-0624+CA-6072@same land@54.041,-109.319`: CA-0624: key record SK-ALL Gover:3379 names a layer prefix not in us-key/layers.json (geometry now: GREW: live overlap is 635% bigger (198.4 ac vs 27.0 ac stored); 90% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply,
- **RECORD CHANGED** `CA-0630+CA-2916@same land@49.318,-106.380`: CA-0630: key record SK-ALL Gover:3402 names a layer prefix not in us-key/layers.json | CA-2916: key record Saskatchewan~6:102 names a layer prefix not in us-key/layers.json | CA-2916: key record SK-ALL Gover:3402 names a layer prefix not in us-key/layers.json (geometry now: MOVED: live overlap centr
- **RECORD CHANGED** `CA-1093+CA-2549@same land@50.277,-108.408`: CA-1093: key record Saskatchewan~6:1 names a layer prefix not in us-key/layers.json | CA-2549: key record Saskatchewan~6:1 names a layer prefix not in us-key/layers.json (geometry now: GONE: no overlap between the live official outlines near this spot)
- **RECORD CHANGED** `CA-1117+CA-2605@area@52.406,-104.306`: CA-1117: key record Saskatchewan~6:41 names a layer prefix not in us-key/layers.json (geometry now: GONE: no overlap between the live official outlines near this spot)
- **RECORD CHANGED** `CA-1118+CA-2711@area@51.354,-105.214`: CA-1118: key record Saskatchewan~6:43 names a layer prefix not in us-key/layers.json (geometry now: GONE: no overlap between the live official outlines near this spot)
- **RECORD CHANGED** `CA-1127+CA-2747@same land@50.300,-109.896`: CA-1127: key record Saskatchewan~6:53 names a layer prefix not in us-key/layers.json | CA-2747: key record Saskatchewan~6:53 names a layer prefix not in us-key/layers.json (geometry now: GONE: no overlap between the live official outlines near this spot)
- **RECORD CHANGED** `CA-1149+CA-2844@same land@50.060,-106.466`: CA-1149: key record Saskatchewan~6:82 names a layer prefix not in us-key/layers.json | CA-2844: key record Saskatchewan~6:82 names a layer prefix not in us-key/layers.json (geometry now: GONE: no overlap between the live official outlines near this spot)
- **RECORD CHANGED** `CA-2644+CA-2645@same land@51.106,-106.600`: CA-2644: key record SK-ALL Gover:3300 names a layer prefix not in us-key/layers.json | CA-2645: key record SK-ALL Gover:3300 names a layer prefix not in us-key/layers.json (geometry now: GREW: live overlap is 36% bigger (765.6 ac vs 564.1 ac stored); 100% of the stored overlap still inside (10 m tol

The 2-fer file was not changed. A person and the club waiting room decide.
