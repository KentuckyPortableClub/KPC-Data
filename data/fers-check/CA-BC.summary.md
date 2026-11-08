# 2-fer accuracy check: CA-BC

Run 2026-11-08T11:16:13Z → 2026-11-08T12:04:01Z (UTC) · tool 0.1.0 (2026-10-31) · complete
Live rows in the file: 97 · checked: 97 · skipped (dropped / merged): 564

| verdict | rows |
|---|---|
| CONFIRMED | 29 |
| SHRUNK | 13 |
| GREW | 21 |
| MOVED | 4 |
| GONE | 24 |
| RECORD CHANGED | 5 |
| SOURCE DOWN | 1 |

| flag | rows |
|---|---|
| small overlap (under 50 yd across) | 19 |
| trail line from the club saved copy (not re-read live) | 1 |

## For a person to look at

- **SHRUNK** `CA-1204+CA-3247@area@49.353,-123.341`: live overlap is 72% smaller (0.4 ac vs 1.3 ac stored)
- **SHRUNK** `CA-3215+CA-4060@area@49.344,-122.867`: only 0% of the stored overlap is still inside the live overlap (10 m tolerance)
- **SHRUNK** `CA-3245+CA-5548@area@49.057,-122.873`: live overlap is 89% smaller (0.2 ac vs 1.7 ac stored)
- **SHRUNK** `CA-3261+CA-3262@same land@49.819,-119.185`: live overlap is 35% smaller (107.0 ac vs 165.5 ac stored)
- **SHRUNK** `CA-3328+CA-5346@area@49.081,-121.883`: live overlap is 43% smaller (1.6 ac vs 2.7 ac stored)
- **SHRUNK** `CA-3615+CA-4243@area@53.142,-127.463`: live overlap is 41% smaller (0.7 ac vs 1.3 ac stored)
- **SHRUNK** `CA-3617+CA-5498@area@49.335,-123.120`: only 0% of the stored overlap is still inside the live overlap (10 m tolerance)
- **SHRUNK** `CA-3724+CA-4065@area@50.792,-128.656`: live overlap is 38% smaller (8504.2 ac vs 13732.7 ac stored)
- **SHRUNK** `CA-3781+CA-3782@same land@50.696,-119.109`: only 51% of the stored overlap is still inside the live overlap (10 m tolerance)
- **SHRUNK** `CA-3868+CA-3869@same land@49.992,-121.733`: only 65% of the stored overlap is still inside the live overlap (10 m tolerance)
- **SHRUNK** `CA-3988+CA-3989@same land@53.494,-120.871`: live overlap is 27% smaller (8169.6 ac vs 11243.6 ac stored)
- **SHRUNK** `CA-4100+CA-4101@same land@50.254,-121.508`: only 42% of the stored overlap is still inside the live overlap (10 m tolerance)
- **SHRUNK** `CA-4258+CA-5539@area@48.439,-123.294`: live overlap is 95% smaller (0.3 ac vs 7.4 ac stored)
- **GREW** `CA-0748+CA-4282@same land@53.352,-120.577`: live overlap is 28% bigger (62048.6 ac vs 48596.1 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `CA-3250+CA-3251@same land@49.489,-124.704`: live overlap is 2098% bigger (350.0 ac vs 15.9 ac stored); 98% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `CA-3320+CA-3321@same land@51.219,-121.484`: live overlap is 3628% bigger (357.8 ac vs 9.6 ac stored); 88% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `CA-3348+CA-3349@same land@54.058,-121.020`: live overlap is 232% bigger (1660.3 ac vs 499.5 ac stored); 98% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `CA-3410+CA-3411@same land@49.579,-124.829`: live overlap is 524% bigger (694.3 ac vs 111.3 ac stored); 96% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `CA-3439+CA-3440@same land@58.063,-125.714`: live overlap is 235% bigger (132286.8 ac vs 39467.0 ac stored); 97% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `CA-3465+CA-3466@same land@50.027,-125.299`: live overlap is 124% bigger (2.2 ac vs 1.0 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `CA-3495+CA-3496@same land@54.335,-129.296`: live overlap is 3217% bigger (948.7 ac vs 28.6 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `CA-3522+CA-3523@same land@49.608,-124.058`: live overlap is 234% bigger (208.7 ac vs 62.5 ac stored); 99% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `CA-3524+CA-3525@same land@53.983,-125.167`: live overlap is 39% bigger (16637.2 ac vs 11981.7 ac stored); 97% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `CA-3624+CA-4122@area@49.226,-119.545`: live overlap is 71% bigger (2.0 ac vs 1.2 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `CA-3789+CA-3790@same land@59.842,-123.251`: live overlap is 430% bigger (6741.2 ac vs 1273.0 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `CA-3838+CA-3839@same land@50.884,-118.500`: live overlap is 52% bigger (310.9 ac vs 204.1 ac stored); 91% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `CA-3840+CA-3841@same land@48.807,-123.517`: live overlap is 2285% bigger (579.1 ac vs 24.3 ac stored); 99% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `CA-3899+CA-3900@same land@55.095,-128.947`: live overlap is 30% bigger (26.2 ac vs 20.2 ac stored); 83% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `CA-3932+CA-3933@same land@49.585,-120.775`: live overlap is 3446% bigger (70.5 ac vs 2.0 ac stored); 97% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `CA-3976+CA-3977@same land@59.645,-126.878`: live overlap is 279% bigger (2846.1 ac vs 750.8 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `CA-4142+CA-4143@same land@49.673,-123.144`: live overlap is 3573% bigger (676.9 ac vs 18.4 ac stored); 99% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `CA-4152+CA-4153@same land@54.625,-124.643`: live overlap is 85% bigger (850.5 ac vs 460.5 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `CA-4157+CA-4158@same land@53.916,-121.670`: live overlap is 1266% bigger (1035.9 ac vs 75.8 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `CA-4253+CA-4254@same land@49.302,-119.532`: live overlap is 75% bigger (41.9 ac vs 24.0 ac stored); 93% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **MOVED** `CA-3245+CA-5497@area@49.085,-122.885`: live overlap centre is 817 m from the stored centre; 0% of the stored overlap is still inside it
- **MOVED** `CA-3275+CA-3840@area@48.799,-123.523`: live overlap centre is 414 m from the stored centre; 0% of the stored overlap is still inside it
- **MOVED** `CA-3850+CA-3943@area@49.322,-122.973`: live overlap centre is 221 m from the stored centre; 0% of the stored overlap is still inside it
- **MOVED** `CA-5501+CA-5503@area@49.403,-123.081`: live overlap centre is 422 m from the stored centre; 10% of the stored overlap is still inside it
- **GONE** `CA-0723+CA-1214+CA-3537@area@50.081,-122.864`: no overlap between the live official outlines near this spot
- **GONE** `CA-0723+CA-3231+CA-3537@area@49.738,-122.799`: no overlap between the live official outlines near this spot
- **GONE** `CA-0723+CA-3537+CA-3810@area@50.230,-122.585`: no overlap between the live official outlines near this spot
- **GONE** `CA-0723+CA-3537@area@49.914,-122.793`: no overlap between the live official outlines near this spot
- **GONE** `CA-1214+CA-3537@area@50.081,-122.864`: no overlap between the live official outlines near this spot
- **GONE** `CA-3200+CA-3278@area@49.290,-122.936`: no overlap between the live official outlines near this spot
- **GONE** `CA-3231+CA-3537@area@49.738,-122.865`: no overlap between the live official outlines near this spot
- **GONE** `CA-3245+CA-4031+CA-5901@area@49.028,-122.870`: no overlap between the live official outlines near this spot
- **GONE** `CA-3245+CA-4031@area@49.028,-122.868`: no overlap between the live official outlines near this spot
- **GONE** `CA-3245+CA-5901@area@49.028,-122.868`: no overlap between the live official outlines near this spot
- **GONE** `CA-3453+CA-4071+CA-4106@area@49.239,-122.783`: no overlap between the live official outlines near this spot
- **GONE** `CA-3453+CA-4071@area@49.239,-122.783`: no overlap between the live official outlines near this spot
- **GONE** `CA-3453+CA-4106@area@49.239,-122.783`: no overlap between the live official outlines near this spot
- **GONE** `CA-3498+CA-5327@area@49.202,-121.785`: no overlap between the live official outlines near this spot
- **GONE** `CA-3508+CA-3509@area@49.142,-122.781`: no overlap between the live official outlines near this spot
- **GONE** `CA-3514+CA-3792@area@49.167,-122.651`: no overlap between the live official outlines near this spot
- **GONE** `CA-3537+CA-3810@area@50.230,-122.580`: no overlap between the live official outlines near this spot
- **GONE** `CA-3797+CA-4097+CA-5343@area@49.443,-119.556`: no overlap between the live official outlines near this spot
- **GONE** `CA-3797+CA-5343@area@49.438,-119.538`: no overlap between the live official outlines near this spot
- **GONE** `CA-3918+CA-4251@area@49.239,-123.128`: no overlap between the live official outlines near this spot
- **GONE** `CA-3965+CA-5504@area@49.310,-122.691`: no overlap between the live official outlines near this spot
- **GONE** `CA-4031+CA-5901@area@49.028,-122.869`: no overlap between the live official outlines near this spot
- **GONE** `CA-4071+CA-4106@area@49.239,-122.783`: no overlap between the live official outlines near this spot
- **GONE** `CA-4097+CA-5343@area@49.431,-119.560`: no overlap between the live official outlines near this spot
- **RECORD CHANGED** `CA-0117+CA-4798@area@51.544,-116.532`: CA-4798: 1 key record id(s) no longer in maps.gov.bc.ca/whse/bcgw_pub_whse_human_cultural_economic/MapServer/82: [6165326] (geometry now: GONE: no overlap between the live official outlines near this spot)
- **RECORD CHANGED** `CA-3209+CA-4044@area@48.771,-123.401`: CA-4044: 1 key record id(s) no longer in maps.gov.bc.ca/whse/bcgw_pub_whse_human_cultural_economic/MapServer/82: [6164576] (geometry now: SHRUNK: live overlap is 99% smaller (0.2 ac vs 15.1 ac stored))
- **RECORD CHANGED** `CA-3245+CA-6382@area@49.065,-122.844`: CA-6382: 1 key record id(s) no longer in maps.gov.bc.ca/whse/bcgw_pub_whse_human_cultural_economic/MapServer/82: [6164522] (geometry now: MOVED: live overlap centre is 321 m from the stored centre; 0% of the stored overlap is still inside it)
- **RECORD CHANGED** `CA-3944+CA-4012@area@49.317,-124.251`: CA-4012: 1 key record id(s) no longer in maps.gov.bc.ca/whse/bcgw_pub_whse_human_cultural_economic/MapServer/82: [6165727] (geometry now: SHRUNK: live overlap is 100% smaller (0.0 ac vs 1.9 ac stored))
- **RECORD CHANGED** `CA-4787+CA-4789@area@48.431,-123.449`: CA-4787: 1 key record id(s) no longer in maps.gov.bc.ca/whse/bcgw_pub_whse_human_cultural_economic/MapServer/82: [6160614] | CA-4789: 1 key record id(s) no longer in maps.gov.bc.ca/whse/bcgw_pub_whse_human_cultural_economic/MapServer/82: [6166104] (geometry now: GONE: no overlap between the live off
- **SOURCE DOWN** `CA-0032+CA-3393@area@52.734,-132.106`: checker error on this row (retry; report if it repeats): GEOSException: IllegalArgumentException: Overlay input is mixed-dimension

The 2-fer file was not changed. A person and the club waiting room decide.
