# Waiting room: morning list (2026-11-28)

For chat 11. Held = checked, not live. Release = your YES (+ chat 2 recheck) in data/waiting/approved.json; the nightly run lets it out.

## Held files: 35 (US + Canada first, then North America, W1-W10, rest; oldest first inside)

| since | days | file | last check | why |
|---|---|---|---|---|
| 2026-11-08 | 20 | data/trails/US-13626.json | HOLD | F-T3 length 16 -> 114 km (outside -25% / +50%) |
| 2026-11-10 | 18 | data/truth/US-UT.json | HOLD | F-R2 6 OFF rows share the size 2,200,000.0 ac |
| 2026-11-10 | 18 | data/truth/US-WA.json | HOLD | F-R2 5 OFF rows share the size 564.0 ac; F-R3 69 of 115 sized parks are OFF (over half: a reading problem?) |
| ? | ? | data/campinfo/US-CO.json | PASS |  |
| ? | ? | data/campinfo/US-GA.json | PASS |  |
| ? | ? | data/campinfo/US-WV.json | PASS |  |
| ? | ? | data/campstate/US-AK.json | PASS |  |
| ? | ? | data/campstate/US-AZ.json | PASS |  |
| ? | ? | data/campstate/US-CO.json | PASS |  |
| ? | ? | data/campstate/US-FL.json | PASS |  |
| ? | ? | data/campstate/US-HI.json | PASS |  |
| ? | ? | data/campstate/US-IA.json | PASS |  |
| ? | ? | data/campstate/US-IN.json | PASS |  |
| ? | ? | data/campstate/US-MN.json | PASS |  |
| ? | ? | data/campstate/US-MT.json | PASS |  |
| ? | ? | data/campstate/US-ND.json | PASS |  |
| ? | ? | data/campstate/US-NH.json | PASS |  |
| ? | ? | data/campstate/US-NM.json | PASS |  |
| ? | ? | data/campstate/US-NV.json | PASS |  |
| ? | ? | data/campstate/US-OH.json | PASS |  |
| ? | ? | data/campstate/US-OR.json | PASS |  |
| ? | ? | data/campstate/US-PA.json | PASS |  |
| ? | ? | data/campstate/US-SD.json | PASS |  |
| ? | ? | data/campstate/US-UT.json | PASS |  |
| ? | ? | data/campstate/US-VA.json | PASS |  |
| ? | ? | data/campstate/US-VT.json | PASS |  |
| 2026-11-20 | 8 | data/acres.json | HOLD | 1 rows without acres or a source (e.g. US-4564) |
| ? | ? | data/us-key/index.json | RELEASE |  |
| ? | ? | data/world-key/AU.json | PASS |  |
| ? | ? | data/wwff/PAFF.json | PASS |  |
| ? | ? | data/wwff/PYFF.json | RELEASE |  |
| ? | ? | data/wwff/S5FF.json | PASS |  |
| ? | ? | data/wwff/SMFF.json | PASS |  |
| ? | ? | data/wwff/VEFF.json | RELEASE |  |
| ? | ? | data/wwff/VKFF.json | PASS |  |

## Questions waiting for an answer

| file | open | total |
|---|---|---|
| aliases-nov1.json | 0 | 0 |
| aliases-nov2.json | 0 | 0 |
| aliases-oct31.json | 0 | 33 |
| gis-hunter.json | 8 | 638 |
| hardlook.json | 0 | 0 |
| key-pieces.json | 0 | 307 |
| layers.json | 490 | 26431 |
| lost-finds-nov1.json | 0 | 0 |
| map-audit.json | 132 | 2096 |
| nearmiss-nov2.json | 45 | 45 |
| no-recheck.json | 0 | 13 |
| not-sure-for-chat9.json | 146 | 146 |
| official-links.json | 0 | 0 |
| outside-intake-nov5.json | 402 | 402 |
| parked.json | 0 | 0 |
| pin-typos.json | 0 | 0 |
| world-finder.json | 37 | 3830 |

## Approvals not used yet: 4

- us-key: chat 11 'KEY NO 2026-11-01 (build of 09:11 UTC, sample read: 29 of 30 fine, trails and aliases look right). One bad join is still in: Milford State Fish Hatchery US-7393 (KS) is joined to 'Milford Wildlife Area' (sgksb27, size 0). A fish hatchery is not the wildlife area. Make it a pin, rebuild, and I will say KEY YES.' by chat 11, chat 2 '-'
- us-key: chat 11 'KEY NO 2026-11-01 11:14 UTC build (+218): sample 20 of 30 fine (67%). The fault class is the new 'same full name, far from the pin' joins (pin NOT inside the record). Bad or doubtful: Walnut Creek SRA US-4036 (NE), Smith River BLM RMA US-12840 (joined to the 329,827 ac Smith River NRA, a bigger parent), Twin Buttes US-10944, Clear Creek BLM RMA US-13581, Long Lake SRA US-4260 (joined to a State Habitat Area), Pine Island SP US-13016, Mt. St. Helens NM US-3385 (0 ac pieces), Salt Creek SRA US-5688 (second piece Salt Creek F&W Area is another place), Fortymile WSR US-11828 (joined to the 247,230 ac SRMA), Julian Price US-12371 (a wetlands heritage area, a part). The Milford hatchery join is gone (good). Fix: no outline when the pin is outside the record unless size and kind also agree, then rebuild.' by chat 11, chat 2 '-'
- fers-US-KY: chat 11 '' by chat 2, chat 2 'rechecked 2026-11-02 8:45 AM (chat 2 G-4): only the river-route rows were redone (Lewis and Clark + Trail of Tears pairs, run of 6:43 AM) with the creek cut (R5a: narrow channels off the main river no longer count) and each row now carries the trail's own 100-ft bank zone (route_zone, drawn on the Finder). Ballard WMA x L&C x Trail of Tears: 9.3 mi of bank -> 5.3 mi, the strip up the creek through the fields is gone (Brandon's Nov 1 screenshot). Every other row is unchanged. Please map-check the Ballard and Boatwright rows.'
- world-key: chat 11 'KEY YES 2026-11-02 (chat 12, names / kinds only, no maps seen; 66 PASS world-key files in grade-queue.md). Checked EVERY join in the queued files (44,203 joins): 42,304 (95.7%) have a park name and record name that share their proper words; I read the other ~140 by hand across 27 files (all of AX BZ CL CV DO GA GL GR GT ID LK MX PA PE PF PR ZA NZ CO, a 9-row sample each of IE IT DE SI PT DK BE HU): all are translations, accents, abbreviations (NSG, TN, AMP) or same-site wider names, EXCEPT these 10, KEEP AS PINS: BZ-0051 (Bird Caye BS joined to Laughing Bird Caye), CV-0012 (Protected Landscape joined to a Natural Monument record), DO-0110 (Costa Azul landscape joined to a scenic road), PR-0057 (Boqueron wildlife refuge joined to the State Forest), NZ-0150 (Lake Sumner Regional Park joined to Lake Sumner Forest Park), NZ-0624 (Atuanui Recreation Site joined to a Scenic Reserve), NZ-0676 (Ecological Park joined to Wildlife Refuge), ID-0060 (Provincial Park joined to the CA Kawah Ijen nature reserve), PA-0001 + PA-0054 (one San Lorenzo record offered to two parks). Sample result 30/30 equivalent after those 10. NOT released by me: CM.json and PY.json are HELD by check F-O2 but all 20 CM and 29 PY joins are right (accents / short names like Faro, Nki: the check compares words badly): chat 2 / chat 10 may release them; FR.json + GB.json are HELD by F-O3: FR-16712 and FR-3744 are retired parks still outlined (drop those two outlines; FR-14241 and GB-2511 have none). Acres not checked. AU / GB / PL / FR / IT old bad lists (carried rows) not re-read.' by chat 12, chat 2 'rechecked 2026-11-02 (chat 2 G-4): OK. The world files were already released at 16:37 UTC with chat 12's 10 KEEP-AS-PIN parks still joined (BZ-0051, CV-0012, DO-0110, PR-0057, NZ-0150, NZ-0624, NZ-0676, ID-0060, PA-0001, PA-0054): turned back into pins in the live files (record moved to 'check') and written as 'no' in data/world-key/overrides.json so the next build keeps them pins. FR + GB: retired parks taken out (live + held) and the world key now drops retired numbers itself. CM + PY: chat 12 read all 49 joins as right, chat 10 fixed the accent check: release.'
