# Waiting room REPLAY TEST
Run 2026-10-29 18:31Z: **PASS** (38 of 38 cases right). Every real bad output must be HELD (or, closures, have its bad rows taken out); every good output must PASS.

| result | case | expect | what the checker said |
|---|---|---|---|
| ok | ACCESS: 178 far points (NY, Oct 28 15:57, the tuned run that still kept on-land far points) | HOLD | HOLD: F-A1 47 points over 100 km from their park pin (not a line park), e.g. US-10284 376 km, US-10284 377 km, US-10284 377 km |
| ok | ACCESS: a timed-out layer shrinks a state (simulated: 70% of NY parks dropped) | HOLD | HOLD: F-A2 points 3164 -> 1383 (more than 40% gone) |
| ok | FED CAMPS: office-address rows + ids in two state files (GA + SC before the Oct 29 sweep) | HOLD | HOLD: F-C2 8 of 101 pins outside GA, e.g. Broyles; F-C3 13 campground ids are also in another state file: US-AL.json 1, US-FL.json 1, US-SC.json 11 / HOLD: F-C3 11 campground ids are also in another state file: US-GA.json 11 |
| ok | POTA LIST: a short answer would retire parks (simulated: 3% fewer parks) | HOLD | HOLD: F-P1 POTA parks 79,866 -> 77,470 (more than 1% or 5 gone): needs a second read |
| ok | 2-FER LINE CHECK: READY with rows not checked (Michigan water lesson, simulated) | HOLD | HOLD: F-S1 status READY with 1 rows STORE NOT READ / not checked (must be STOPPED); no live copy: first time this file is published; F-S1 1 rows where a map did not a |
| ok | DOCS: 83 WV parks on one rules page (Oct 28 11:27) | HOLD | HOLD: F-D1 one map page on 82 of 172 parks: https://wvdnr.gov/lands-waters/stream-access-points/; F-D2 1 map links on a banned host (fire news / map pins / social), e |
| ok | DOCS: VA maps on inciweb (Oct 28 15:08) | HOLD | HOLD: F-D1 one map page on 26 of 184 parks: https://inciweb.wildfire.gov/; F-D2 27 map links on a banned host (fire news / map pins / social), e.g. https://www.google |
| ok | CLOSURES: standing rules, a Virginia row under KY, fee notes, results rows (round 8, Oct 29 01:14): bad rows taken out | HOLD | LIVE-FILTERED: US-0295: a fee / hours / standing note: "Youth Under 16 - Free, no permit needed"; US-10098: a fee / hours / standing note: "Youth under 16: Free, no permit nee |
| ok | HOURS: one statewide fee line on 25 parks (simulated from the live KY file) | HOLD | HOLD: F-H1 the same fees line on 25 parks (statewide / agency-wide text?): "there is no fee to visit wolf creek national fish hatchery"; F-K known answer: US-3828 fee |
| ok | PARKING EXPLORER: a server did not answer and a state lost its leads (simulated: MN wiped) | HOLD | HOLD: F-L1 leads 8 -> 0 (wiped or under half) |
| ok | CAMPGROUND INFO: elevation as RV length (675 / 980 ft) (Oct 28 07:29) | HOLD | HOLD: F-I1 4 RV lengths outside 10-100 ft, e.g. Higginson-Henry WMA designated campsites 675 ft |
| ok | CAMPGROUND INFO: the 877 reservation line as a camp phone (Oct 28 10:47) | HOLD | HOLD: F-I1 4 RV lengths outside 10-100 ft, e.g. Higginson-Henry WMA designated campsites 675 ft; F-I4 4 toll-free reservation numbers kept as a camp phone, e.g. Bandy |
| ok | CAMPGROUND INFO: '$5 Million Renovation' as a fee (Oct 28 15:28) | HOLD | HOLD: F-I5 1 fees that read like news / money totals, e.g. Kentucky Horse Park Campground |
| ok | TRUTH: WV statewide '1.4 million acres' on 76 WMAs (Oct 28 21:48) | HOLD | HOLD: F-R1 76 parks OFF on one number from one page (1,400,000.0 ac, https://wvdnr.gov/lands-waters/wildlife-management-areas/); F-R2 76 OFF rows share the size 1,400 |
| ok | INTAKE: a read error as REJECT + Czech READY on a credit line (Oct 28 07:22) | HOLD | HOLD: F-K known answer: "USACE reservoirs (Army Corps of Engineer" is water surfaces only (rule B6), never READY; F-N1 "SCDNR managed lands (public viewer) on C": a r |
| ok | CANADA KEY: retired CA-2156 still outlined (Oct 28 01:49) | HOLD | HOLD: F-O3 retired parks still outlined: CA-2156 / HOLD: F-O3 retired parks still in the outline index: CA-2045, CA-2156, CA-2160, CA-2161, CA-2266 |
| ok | DOCS: map / rules links that answer an error (simulated: 3 parks pointing at pages that do not exist) | HOLD | HOLD: F-D3 3 of 3 re-tested links dead, e.g. https://www.nps.gov/kpc-replay-dead-link-2.htm; no live copy: first time this file is published |
| ok | 2-FERS: a known pair dropped (simulated: Mammoth Cave x Green River removed from the live KY file) | HOLD | HOLD: F-K known 2-fer missing: US-0050+US-10105@area@37.17,-86.15; F-K known 2-fer missing: US-0050 + US-10105 |
| ok | 2-FERS: live 'same land' wrong joins (NY sister-name state forests 'Lost Nation (St. Lawrence)' + '(Allegany)', 377 km; Robert Moses x2, 503 km) | HOLD | HOLD: F-S3 3 live rows whose two park pins are 100+ km apart (wrong joins), e.g. US-2028+US-2061+US-4374 500 km, US-2028+US-4374 500 km, US-2061+US-4374 500 km; F-S2  |
| ok | GOOD: Kentucky 2-fers (live) | PASS | PASS:  |
| ok | GOOD: Canada key, Ontario (live) | PASS | PASS:  |
| ok | GOOD: Kentucky federal campgrounds (live, after the Oct 29 sweep) | PASS | PASS:  |
| ok | GOOD: NY access after the 100 km fix (Oct 29 02:27 vs the run before) | PASS | PASS:  |
| ok | ATTACK A1 (chat 8): Ohio 2-fers, every candidate pair wrong, same count | HOLD | HOLD: F-2 only 0 of 25 live candidate pairs are still there (under 80%): a person looks (a rule change is released by hand); F-2 25 new candidate pairs since the live |
| ok | ATTACK A1 (chat 8): Indiana 2-fers, pairs rotated | HOLD | HOLD: F-2 only 1 of 51 live candidate pairs are still there (under 80%): a person looks (a rule change is released by hand); F-2 49 new candidate pairs since the live |
| ok | ATTACK A2 (chat 8): Ohio outline key, outlines shuffled to other parks | HOLD | HOLD: F-O2 263 of 270 outlines carry a layer name that shares no word with the park (97%; live 4/270): outlines swapped to other parks?; F-O4 59 of 60 changed outline |
| ok | ATTACK A3 (chat 8): Illinois 2-fers + 20% fake far-apart area rows | HOLD | HOLD: F-2 candidates 12 -> 27 (over 30% change); F-2 15 new candidate pairs since the live file (over 10% of 12): a person looks at them first, e.g. US-0281+US-4112,  |
| ok | ATTACK A4 (chat 8): New Mexico 2-fers wiped (2 candidates) | HOLD | HOLD: F-2 only 0 of 9 live candidate pairs are still there (under 80%): a person looks (a rule change is released by hand); F-2 every row gone (live had 61) |
| ok | ATTACK A5 (chat 8): a .gz twin of live Wisconsin 2-fers with 18% of the rows | HOLD | HOLD: F-4 data/fers/US-WI.json.gz replaces live data/fers/US-WI.json (other format) with 67 rows for 374 (over 10% fewer) |
| ok | ATTACK A6 (chat 8): status PART READY FOR CHAT 8 with 40 unchecked rows | HOLD | HOLD: F-S1 status PART READY FOR CHAT 8 with 40 rows STORE NOT READ / not checked (must be STOPPED) |
| ok | ATTACK A7 (chat 8): truthy pass flags, no pass record on any row | HOLD | HOLD: F-2 pass1 is not a run date (True): the bot's own field, not trusted; F-2 pass2 is not a run date (True): the bot's own field, not trusted; F-2 pass3 is not a r |
| ok | GOOD B1 (chat 8): Kentucky closures naming the Indiana bat, Washington County, the Virginia state line, West Virginia hunters | PASS | PASS:  |
| ok | GOOD B1b (chat 8): the same rows with no park number (word test) | PASS | PASS:  |
| ok | GOOD: Ohio 2-fers unchanged (chat 8 baseline) | PASS | PASS:  |
| ok | ATTACK R1 (chat 8 retest): Ohio 2-fers, 16% of pairs moved to a park within 20 km | HOLD | HOLD: F-2 4 new candidate pairs since the live file (over 10% of 25): a person looks at them first, e.g. US-1935+US-9431, US-1936+US-5641, US-1940+US-1943 |
| ok | ATTACK R2 (chat 8 retest A2d): Ohio key, 10% of outlines swapped AND the parks renamed to fit | HOLD | HOLD: F-O2 27 parks carry a name that is not POTA's (renamed to fit a layer?), e.g. US-0020 'VetoLakeWA', US-0482 'GrtCouncilSP', US-0483 'LAWRENCE WOODS'; F-O4 24 of |
| ok | GOOD: Ohio outline key unchanged | PASS | PASS:  |
| ok | G5: a big-change hold with no stamp still HOLDS (stamps.json empty) | HOLD | HOLD: F-2 4 new candidate pairs since the live file (over 10% of 25): a person looks at them first, e.g. US-1935+US-9431, US-1936+US-5641, US-1940+US-1943 |
