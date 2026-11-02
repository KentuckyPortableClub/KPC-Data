# 2-fer accuracy check: CA-BC

Run 2026-11-01T11:15:36Z → 2026-11-01T12:04:56Z (UTC) · tool 0.1.0 (2026-10-31) · complete
Live rows in the file: 58 · checked: 58 · skipped (dropped / merged): 585

| verdict | rows |
|---|---|
| CONFIRMED | 24 |
| SHRUNK | 4 |
| GREW | 14 |
| RECORD CHANGED | 15 |
| SOURCE DOWN | 1 |

| flag | rows |
|---|---|
| small overlap (under 50 yd across) | 7 |
| trail line from the club saved copy (not re-read live) | 1 |

## For a person to look at

- **SHRUNK** `CA-3615+CA-4243@area@53.142,-127.463`: live overlap is 41% smaller (0.7 ac vs 1.3 ac stored)
- **SHRUNK** `CA-3724+CA-4065@area@50.792,-128.656`: live overlap is 38% smaller (8501.0 ac vs 13732.7 ac stored)
- **SHRUNK** `CA-3781+CA-3782@same land@50.696,-119.109`: only 51% of the stored overlap is still inside the live overlap (10 m tolerance)
- **SHRUNK** `CA-4100+CA-4101@same land@50.254,-121.508`: only 42% of the stored overlap is still inside the live overlap (10 m tolerance)
- **GREW** `CA-3320+CA-3321@same land@51.219,-121.484`: live overlap is 3558% bigger (351.1 ac vs 9.6 ac stored); 87% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `CA-3348+CA-3349@same land@54.058,-121.020`: live overlap is 232% bigger (1660.0 ac vs 499.5 ac stored); 98% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `CA-3439+CA-3440@same land@58.063,-125.714`: live overlap is 235% bigger (132283.5 ac vs 39467.0 ac stored); 97% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `CA-3465+CA-3466@same land@50.027,-125.299`: live overlap is 88% bigger (1.8 ac vs 1.0 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `CA-3495+CA-3496@same land@54.335,-129.296`: live overlap is 3216% bigger (948.6 ac vs 28.6 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `CA-3522+CA-3523@same land@49.608,-124.058`: live overlap is 233% bigger (208.1 ac vs 62.5 ac stored); 99% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `CA-3789+CA-3790@same land@59.842,-123.251`: live overlap is 430% bigger (6741.2 ac vs 1273.0 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `CA-3838+CA-3839@same land@50.884,-118.500`: live overlap is 52% bigger (309.7 ac vs 204.1 ac stored); 91% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `CA-3899+CA-3900@same land@55.095,-128.947`: live overlap is 29% bigger (26.0 ac vs 20.2 ac stored); 82% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `CA-3932+CA-3933@same land@49.585,-120.775`: live overlap is 3431% bigger (70.2 ac vs 2.0 ac stored); 96% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `CA-3976+CA-3977@same land@59.645,-126.878`: live overlap is 279% bigger (2845.0 ac vs 750.8 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `CA-4142+CA-4143@same land@49.673,-123.144`: live overlap is 3569% bigger (676.2 ac vs 18.4 ac stored); 99% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `CA-4157+CA-4158@same land@53.916,-121.670`: live overlap is 1264% bigger (1034.8 ac vs 75.8 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `CA-4253+CA-4254@same land@49.302,-119.532`: live overlap is 74% bigger (41.7 ac vs 24.0 ac stored); 93% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **RECORD CHANGED** `CA-0697+CA-4080@area@51.094,-118.888`: CA-4080: key record BC recreatio:331807 names a layer prefix not in us-key/layers.json (geometry now: GONE: no overlap between the live official outlines near this spot)
- **RECORD CHANGED** `CA-0748+CA-4282@same land@53.352,-120.577`: CA-0748: key record BC recreatio:1159546 names a layer prefix not in us-key/layers.json | CA-4282: key record BC recreatio:1159546 names a layer prefix not in us-key/layers.json (geometry now: GREW: live overlap is 28% bigger (62038.2 ac vs 48596.1 ac stored); 100% of the stored overlap still inside
- **RECORD CHANGED** `CA-0750+CA-3543@area@49.013,-115.650`: CA-0750: key record BC recreatio:1007826 names a layer prefix not in us-key/layers.json | CA-0750: key record BC recreatio:1510813 names a layer prefix not in us-key/layers.json (geometry now: GONE: no overlap between the live official outlines near this spot)
- **RECORD CHANGED** `CA-3209+CA-4044@area@48.771,-123.401`: CA-4044: key record BC-HP Govern:6121205 names a layer prefix not in us-key/layers.json (geometry now: MOVED: live overlap centre is 286 m from the stored centre; 3% of the stored overlap is still inside it)
- **RECORD CHANGED** `CA-3250+CA-3251@same land@49.489,-124.704`: CA-3250: key record BC local and:3560404 names a layer prefix not in us-key/layers.json | CA-3251: key record BC local and:3560404 names a layer prefix not in us-key/layers.json (geometry now: GREW: live overlap is 2086% bigger (348.1 ac vs 15.9 ac stored); 97% of the stored overlap still inside (10
- **RECORD CHANGED** `CA-3261+CA-3262@same land@49.819,-119.185`: CA-3262: key record BC recreatio:954230 names a layer prefix not in us-key/layers.json (geometry now: SHRUNK: live overlap is 36% smaller (106.6 ac vs 165.5 ac stored))
- **RECORD CHANGED** `CA-3410+CA-3411@same land@49.578,-124.827`: CA-3410: key record BC local and:3560439 names a layer prefix not in us-key/layers.json | CA-3410: key record BC local and:3560472 names a layer prefix not in us-key/layers.json | CA-3411: key record BC local and:3560439 names a layer prefix not in us-key/layers.json | CA-3411: key record BC local a
- **RECORD CHANGED** `CA-3524+CA-3525@same land@53.983,-125.167`: CA-3524: key record BC recreatio:241344 names a layer prefix not in us-key/layers.json | CA-3525: key record BC recreatio:241344 names a layer prefix not in us-key/layers.json (geometry now: GREW: live overlap is 39% bigger (16630.6 ac vs 11981.7 ac stored); 97% of the stored overlap still inside (1
- **RECORD CHANGED** `CA-3542+CA-3543@area@49.013,-115.650`: CA-3542: key record BC recreatio:1510813 names a layer prefix not in us-key/layers.json | CA-3542: key record BC recreatio:1662737 names a layer prefix not in us-key/layers.json (geometry now: GONE: no overlap between the live official outlines near this spot)
- **RECORD CHANGED** `CA-3624+CA-4122@area@49.226,-119.545`: CA-3624: key record BC recreatio:954452 names a layer prefix not in us-key/layers.json (geometry now: GREW: live overlap is 62% bigger (1.9 ac vs 1.2 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, 
- **RECORD CHANGED** `CA-3834+CA-4027@area@49.432,-123.613`: CA-4027: key record BC recreatio:1509403 names a layer prefix not in us-key/layers.json (geometry now: GONE: no overlap between the live official outlines near this spot)
- **RECORD CHANGED** `CA-3840+CA-3841@same land@48.807,-123.517`: CA-3840: key record BC local and:3560463 names a layer prefix not in us-key/layers.json (geometry now: GREW: live overlap is 2282% bigger (578.3 ac vs 24.3 ac stored); 99% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-ap
- **RECORD CHANGED** `CA-3868+CA-3869@same land@49.992,-121.733`: CA-3868: key record BC recreatio:1053599 names a layer prefix not in us-key/layers.json (geometry now: SHRUNK: only 65% of the stored overlap is still inside the live overlap (10 m tolerance))
- **RECORD CHANGED** `CA-3988+CA-3989@same land@53.494,-120.871`: CA-3988: key record BC recreatio:1147781 names a layer prefix not in us-key/layers.json | CA-3989: key record BC recreatio:1147781 names a layer prefix not in us-key/layers.json (geometry now: SHRUNK: live overlap is 27% smaller (8167.0 ac vs 11243.6 ac stored))
- **RECORD CHANGED** `CA-4152+CA-4153@same land@54.625,-124.643`: CA-4153: key record BC recreatio:243165 names a layer prefix not in us-key/layers.json (geometry now: GREW: live overlap is 84% bigger (849.4 ac vs 460.5 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-app
- **SOURCE DOWN** `CA-0032+CA-3393@area@52.734,-132.106`: checker error on this row (retry; report if it repeats): GEOSException: IllegalArgumentException: Overlay input is mixed-dimension

The 2-fer file was not changed. A person and the club waiting room decide.
