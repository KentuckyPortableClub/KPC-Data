# Fact check of US key run 44528656941 (rules 7c6e01e1bc2b), Opus, 19 Nov 2026
OLD = published key at KPC-Links 8140d35; NEW = main d5ae6ad3 (37 saved states) + release `key-held` (13 held states).
Same inputs both sides: boundary-cache US-*.json.gz (unchanged since 18 Nov), KPC-Data parkinfo + truth (unchanged since c4415276).
Lost outlines classified by the key's own reason text; held against the forecast (`../forecast/`).

ALL: outlines 11,715 -> 11,591 | verified 8,304 -> 8,366 | flagged 549 -> 386 | SHARED 278 -> 116 | OTHER_PARK 44 -> 15 | PIN_FAR 225 -> 220 | SIZE_BIG 55 -> 53 | BIG_PIECE 36 -> 31
Lost 126: as planned 125 (Q1 88, contest 18 incl. 2 exact-name, D4 lake surface 15, D3 4, park-preserve 0); NOT in forecast 1 (Tillamook).
`reviewed-approx` rows left in the key: 0.

## HELD states (need Brandon's yes per state)
| state | outlines old -> new | lost as planned | lost and NOT explained | new hard flags (STOP) | new hard flags the forecast had | result |
|---|---|---|---|---|---|---|
| AK | 136 -> 134 | D3 1 Q1 1 | - | - | - | PASS |
| AR | 268 -> 255 | D4 10 contest 3 | - | - | - | PASS |
| DE | 85 -> 84 | contest 1 | - | - | - | PASS |
| FL | 438 -> 435 | Q1 2 contest 1 | - | US-6321 Rotenberger Wildlife Management Area SIZE_BIG; US-6328 Three Lakes Wildlife Management Area SIZE_BIG | - | STOP |
| GA | 227 -> 223 | D3 2 contest 2 | - | - | - | PASS |
| ID | 231 -> 227 | D4 3 Q1 1 | - | US-4500 Bitterroot National Forest SIZE_BIG | - | STOP |
| MT | 246 -> 244 | Q1 3 | - | - | - | PASS |
| NC | 227 -> 225 | Q1 1 contest 1 | - | - | - | PASS |
| OR | 388 -> 378 | D3 1 Q1 8 contest 1 | US-5461 Tillamook State Forest | - | US-0596 Umatilla National Wildlife Refuge PIN_FAR | STOP |
| RI | 58 -> 56 | Q1 1 contest 1 | - | - | - | PASS |
| UT | 422 -> 412 | Q1 8 contest 2 | - | - | - | PASS |
| VA | 177 -> 175 | Q1 2 | - | - | US-9941 Brush Mountain East Wilderness Area PIN_FAR | PASS |
| WY | 213 -> 207 | Q1 3 contest 3 | - | - | - | PASS |

## SAVED states (37, already on main; data/outlines not saved while any state is held)
outlines 8,599 -> 8,536; lost as planned Q1 58, contest 3, D4 2; nothing unexplained; new hard flags all in the forecast: NV: US-13139 Muddy Mountains BLM Herd Management Area PIN_FAR; OK: US-6365 Osage Wildlife Management Area PIN_FAR; WA: US-0596 Umatilla National Wildlife Refuge PIN_FAR

## STOP list for Fable
- US-5461 Tillamook SF (OR): Q1 took the approximate 627,317-acre 'Forest Development Fund' record; the one left (21 acres, 40.3 km from the pin) is held by the standing 15 km rule (5 Nov) -> pin. The offline forecast did not apply that rule (it had a flagged 21-acre piece). Explained; better than the forecast; OR stays held by item 3c until Fable says.
- US-6321 Rotenberger WMA, US-6328 Three Lakes WMA (FL), US-4500 Bitterroot NF (ID): SIZE_BIG, SAME records as the published key. The published key had no `ac` (rows added up); the run measured the union (67,913 / 189,872 / 2,117,033 ac). Not caused by the new rules: the published outlines were already this size. Bitterroot's 743,000 is a bad page read (section 9: that is the wilderness share).

## Gold set on the NEW key (77 parks)
TUNE 65: wrong land 8 -> 2, too big 9 -> 0, missing pieces 19 -> 29 (planned pins: D3 heritage areas, Q1, contest; #277 returns some). SEALED 12: 0 / 0 / 0 on both (count only).
TUNE misses: gold-new.txt. Wrong land left: US-12918 Seven Sisters (MT), US-3933 Cheatham WMA (TN).
