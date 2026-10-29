# Waiting room REPLAY TEST
Run 2026-10-29 02:37Z: **PASS** (20 of 20 cases right). Every real bad output must be HELD (or, closures, have its bad rows taken out); every good output must PASS.

| result | case | expect | what the checker said |
|---|---|---|---|
| ok | ACCESS: 178 far points (NY, Oct 28 15:57, the tuned run that still kept on-land far points) | HOLD | HOLD: F-A1 47 points over 100 km from their park pin (not a line park), e.g. US-10284 376 km, US-10284 377 km, US-10284 377 km |
| ok | ACCESS: a timed-out layer shrinks a state (simulated: 70% of NY parks dropped) | HOLD | HOLD: F-A2 points 3164 -> 1383 (more than 40% gone) |
| ok | FED CAMPS: office-address rows + ids in two state files (GA + SC before the Oct 29 sweep) | HOLD | HOLD: F-C2 8 of 101 pins outside GA, e.g. Broyles; F-C3 13 campground ids are also in another state file: US-AL.json 1, US-FL.json 1, US-SC.json 11 / HOLD: F-C3 11 campground ids are also in another state file: US-GA.json 11 |
| ok | POTA LIST: a short answer would retire parks (simulated: 3% fewer parks) | HOLD | HOLD: F-P1 POTA parks 79,853 -> 77,457 (more than 1% or 5 gone): needs a second read |
| ok | 2-FER LINE CHECK: READY with rows not checked (Michigan water lesson, simulated) | HOLD | HOLD: F-S1 status READY with 2 rows not checked / unanswered (must be STOPPED); no live copy: first time this file is published |
| ok | DOCS: 83 WV parks on one rules page (Oct 28 11:27) | HOLD | HOLD: F-D1 one map page on 82 of 172 parks: https://wvdnr.gov/lands-waters/stream-access-points/; F-D2 1 map links on a banned host (fire news / map pins / social), e |
| ok | DOCS: VA maps on inciweb (Oct 28 15:08) | HOLD | HOLD: F-D1 one map page on 26 of 184 parks: https://inciweb.wildfire.gov/; F-D2 27 map links on a banned host (fire news / map pins / social), e.g. https://www.google |
| ok | CLOSURES: standing rules, a Virginia row under KY, fee notes, results rows (round 8, Oct 29 01:14): bad rows taken out | HOLD | LIVE-FILTERED: US-0295: a fee / hours / standing note: "Youth Under 16 - Free, no permit needed"; US-10098: a fee / hours / standing note: "Youth under 16: Free, no permit nee |
| ok | HOURS: one statewide fee line on 25 parks (simulated from the live KY file) | HOLD | HOLD: F-H1 the same fees line on 25 parks (statewide / agency-wide text?): "there is no fee to visit wolf creek national fish hatchery"; F-H3 32 of 107 hours lines ha |
| ok | PARKING EXPLORER: a server did not answer and a state lost its leads (simulated: MN wiped) | HOLD | HOLD: F-L1 leads 8 -> 0 (wiped or under half) |
| ok | CAMPGROUND INFO: elevation as RV length (675 / 980 ft) (Oct 28 07:29) | HOLD | HOLD: F-I1 4 RV lengths outside 10-100 ft, e.g. Higginson-Henry WMA designated campsites 675 ft |
| ok | CAMPGROUND INFO: the 877 reservation line as a camp phone (Oct 28 10:47) | HOLD | HOLD: F-I1 4 RV lengths outside 10-100 ft, e.g. Higginson-Henry WMA designated campsites 675 ft; F-I4 4 toll-free reservation numbers kept as a camp phone, e.g. Bandy |
| ok | CAMPGROUND INFO: '$5 Million Renovation' as a fee (Oct 28 15:28) | HOLD | HOLD: F-I5 1 fees that read like news / money totals, e.g. Kentucky Horse Park Campground |
| ok | TRUTH: WV statewide '1.4 million acres' on 76 WMAs (Oct 28 21:48) | HOLD | HOLD: F-R1 76 parks OFF on one number from one page (1,400,000.0 ac, https://wvdnr.gov/lands-waters/wildlife-management-areas/); F-R2 76 OFF rows share the size 1,400 |
| ok | INTAKE: a read error as REJECT + Czech READY on a credit line (Oct 28 07:22) | HOLD | HOLD: F-K known answer: "USACE reservoirs (Army Corps of Engineer" is water surfaces only (rule B6), never READY; F-N1 "SCDNR managed lands (public viewer) on C": a r |
| ok | CANADA KEY: retired CA-2156 still outlined (Oct 28 01:49) | HOLD | HOLD: F-O3 retired parks still outlined: CA-2156 / HOLD: F-O3 retired parks still in the outline index: CA-2156 |
| ok | GOOD: Kentucky 2-fers (live) | PASS | PASS:  |
| ok | GOOD: Canada key, Ontario (live) | PASS | PASS:  |
| ok | GOOD: Kentucky federal campgrounds (live, after the Oct 29 sweep) | PASS | PASS:  |
| ok | GOOD: NY access after the 100 km fix (Oct 29 02:27 vs the run before) | PASS | PASS:  |
