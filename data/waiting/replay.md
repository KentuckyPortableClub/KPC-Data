# Waiting room REPLAY TEST
Run 2026-11-02 16:30Z: **FAIL** (17 of 38 cases right). Every real bad output must be HELD (or, closures, have its bad rows taken out); every good output must PASS.

| result | case | expect | what the checker said |
|---|---|---|---|
| **MISS** | ACCESS: 178 far points (NY, Oct 28 15:57, the tuned run that still kept on-land far points) | HOLD | HOLD: case could not load: data 2c6610ba:data/access/US-NY.json not in the git history (needs fetch-depth 0) |
| **MISS** | ACCESS: a timed-out layer shrinks a state (simulated: 70% of NY parks dropped) | HOLD | HOLD: case could not load: data 1600e869:data/access/US-NY.json not in the git history (needs fetch-depth 0) |
| **MISS** | FED CAMPS: office-address rows + ids in two state files (GA + SC before the Oct 29 sweep) | HOLD | HOLD: case could not load: links 54a2a9410:data/campfed/US-GA.json not in the git history (needs fetch-depth 0) |
| ok | POTA LIST: a short answer would retire parks (simulated: 3% fewer parks) | HOLD | HOLD: F-P1 POTA parks 79,917 -> 77,519 (more than 1% or 5 gone): needs a second read |
| ok | 2-FER LINE CHECK: READY with rows not checked (Michigan water lesson, simulated) | HOLD | HOLD: F-S1 status READY with 1 rows STORE NOT READ / not checked (must be STOPPED); no live copy: first time this file is published; F-S1 1 rows where a map did not a |
| **MISS** | DOCS: 83 WV parks on one rules page (Oct 28 11:27) | HOLD | HOLD: case could not load: data 7a2f9ae1:data/docs/US-WV.json not in the git history (needs fetch-depth 0) |
| **MISS** | DOCS: VA maps on inciweb (Oct 28 15:08) | HOLD | HOLD: case could not load: data cac42d02:data/docs/US-VA.json not in the git history (needs fetch-depth 0) |
| **MISS** | CLOSURES: standing rules, a Virginia row under KY, fee notes, results rows (round 8, Oct 29 01:14): bad rows taken out | HOLD | HOLD: case could not load: data c26e147c:data/closures/US-KY.json not in the git history (needs fetch-depth 0) |
| ok | HOURS: one statewide fee line on 25 parks (simulated from the live KY file) | HOLD | HOLD: F-H1 the same fees line on 25 parks (statewide / agency-wide text?): "there is no fee to visit wolf creek national fish hatchery" |
| ok | PARKING EXPLORER: a server did not answer and a state lost its leads (simulated: MN wiped) | HOLD | HOLD: F-L1 leads 8 -> 0 (wiped or under half) |
| **MISS** | CAMPGROUND INFO: elevation as RV length (675 / 980 ft) (Oct 28 07:29) | HOLD | HOLD: case could not load: data b7b5835e:data/campinfo/US-KY.json not in the git history (needs fetch-depth 0) |
| **MISS** | CAMPGROUND INFO: the 877 reservation line as a camp phone (Oct 28 10:47) | HOLD | HOLD: case could not load: data c5b9e438:data/campinfo/US-KY.json not in the git history (needs fetch-depth 0) |
| **MISS** | CAMPGROUND INFO: '$5 Million Renovation' as a fee (Oct 28 15:28) | HOLD | HOLD: case could not load: data d6769172:data/campinfo/US-KY.json not in the git history (needs fetch-depth 0) |
| **MISS** | TRUTH: WV statewide '1.4 million acres' on 76 WMAs (Oct 28 21:48) | HOLD | HOLD: case could not load: data fdd67e55:data/truth/US-WV.json not in the git history (needs fetch-depth 0) |
| **MISS** | INTAKE: a read error as REJECT + Czech READY on a credit line (Oct 28 07:22) | HOLD | HOLD: case could not load: data 547d47e1:data/intake/ready.json not in the git history (needs fetch-depth 0) |
| **MISS** | CANADA KEY: retired CA-2156 still outlined (Oct 28 01:49) | HOLD | HOLD: case could not load: data fc3bf234:data/ca-key/CA-QC.json not in the git history (needs fetch-depth 0) |
| ok | DOCS: map / rules links that answer an error (simulated: 3 parks pointing at pages that do not exist) | HOLD | HOLD: F-D3 3 of 3 re-tested links dead, e.g. https://www.nps.gov/kpc-replay-dead-link-2.htm; no live copy: first time this file is published |
| ok | 2-FERS: a known pair dropped (simulated: Mammoth Cave x Green River removed from the live KY file) | HOLD | HOLD: F-K known 2-fer missing: US-0050+US-10105@area@37.17,-86.15; F-K known 2-fer missing: US-0050 + US-10105 |
| ok | 2-FERS: live 'same land' wrong joins (NY sister-name state forests 'Lost Nation (St. Lawrence)' + '(Allegany)', 377 km; Robert Moses x2, 503 km) | HOLD | HOLD: F-S3 3 live rows whose two park pins are 100+ km apart (wrong joins), e.g. US-2028+US-2061+US-4374 500 km, US-2028+US-4374 500 km, US-2061+US-4374 500 km; F-S2  |
| ok | GOOD: Kentucky 2-fers (live) | PASS | PASS:  |
| ok | GOOD: Canada key, Ontario (live) | PASS | PASS:  |
| ok | GOOD: Kentucky federal campgrounds (live, after the Oct 29 sweep) | PASS | PASS:  |
| **MISS** | GOOD: NY access after the 100 km fix (Oct 29 02:27 vs the run before) | PASS | HOLD: case could not load: data 1600e869:data/access/US-NY.json not in the git history (needs fetch-depth 0) |
| **MISS** | ATTACK A1 (chat 8): Ohio 2-fers, every candidate pair wrong, same count | HOLD | HOLD: case could not load: 'NoneType' object has no attribute 'get' |
| **MISS** | ATTACK A1 (chat 8): Indiana 2-fers, pairs rotated | HOLD | HOLD: case could not load: 'NoneType' object has no attribute 'get' |
| ok | ATTACK A2 (chat 8): Ohio outline key, outlines shuffled to other parks | HOLD | HOLD: F-O2 263 of 270 outlines carry a layer name that shares no word with the park (97%; live 4/270): outlines swapped to other parks?; F-O4 59 of 60 changed outline |
| ok | ATTACK A3 (chat 8): Illinois 2-fers + 20% fake far-apart area rows | HOLD | HOLD: F-2 candidates 12 -> 27 (over 30% change); F-2 15 new candidate pairs since the live file (over 10% of 12): a person looks at them first, e.g. US-0281+US-4112,  |
| ok | ATTACK A4 (chat 8): New Mexico 2-fers wiped (2 candidates) | HOLD | HOLD: F-2 only 0 of 9 live candidate pairs are still there (under 80%): a person looks (a rule change is released by hand); F-2 every row gone (live had 61); F-K know |
| **MISS** | ATTACK A5 (chat 8): a .gz twin of live Wisconsin 2-fers with 18% of the rows | HOLD | HOLD: case could not load: 'NoneType' object has no attribute 'get' |
| **MISS** | ATTACK A6 (chat 8): status PART READY FOR CHAT 8 with 40 unchecked rows | HOLD | HOLD: case could not load: 'NoneType' object does not support item assignment |
| **MISS** | ATTACK A7 (chat 8): truthy pass flags, no pass record on any row | HOLD | HOLD: case could not load: 'NoneType' object does not support item assignment |
| ok | GOOD B1 (chat 8): Kentucky closures naming the Indiana bat, Washington County, the Virginia state line, West Virginia hunters | PASS | PASS:  |
| ok | GOOD B1b (chat 8): the same rows with no park number (word test) | PASS | PASS:  |
| **MISS** | GOOD: Ohio 2-fers unchanged (chat 8 baseline) | PASS | HOLD: F-4 unsure: the new file does not read as JSON |
| **MISS** | ATTACK R1 (chat 8 retest): Ohio 2-fers, 16% of pairs moved to a park within 20 km | HOLD | HOLD: case could not load: 'NoneType' object has no attribute 'get' |
| ok | ATTACK R2 (chat 8 retest A2d): Ohio key, 10% of outlines swapped AND the parks renamed to fit | HOLD | HOLD: F-O2 27 parks carry a name that is not POTA's (renamed to fit a layer?), e.g. US-0020 'VetoLakeWA', US-0482 'GrtCouncilSP', US-0483 'LAWRENCE WOODS'; F-O4 24 of |
| ok | GOOD: Ohio outline key unchanged | PASS | PASS:  |
| **MISS** | G5: a big-change hold with no stamp still HOLDS (stamps.json empty) | HOLD | HOLD: case could not load: 'NoneType' object has no attribute 'get' |
