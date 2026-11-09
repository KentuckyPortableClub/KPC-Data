# Hand-layer pile solver hand-run (Nov 8 2026) — SEPARATE from the Nov 4 full pile

**Must-keep:** Nov 4 outputs (`solved-join.csv` 52, `needs-person.csv`, `run-log.md`, area `*.json` 1,381 parks) are **unchanged**. Hand run = `hand-layers-*` only.

- MODE=backfill, 17 parks, **auto stays false.** Pins never moved. Proposals only.
- Research answers `super-questions-answers-20261108-1809-CST` folded in (solver categories, rules judged).

## SOLVED-JOIN (12)
### File-aware (5)
US-3505, US-3751, US-6535, US-6565, US-9770 — Rule 3 + “POTA pin may be off” against #50 hand GeoJSON.

### Research accept-polygon (4)
| ref | record | m | why |
|---|---|---|---|
| US-2200 | FID:60 Stephen C. Foster → Okefenokee SP | 0 | rename eff. 2026-09-01 clears Rule 18; pin inside |
| CA-2373 | OBJECTID:32 Primrose Provincial Park | 47 | no separate Wayside boundary; Rule 1 |
| US-6571 | W211 Las Palomas WMA - Anacua Unit | 1363 | own labeled tract; Rule 18c cleared; Rule 3 |
| US-6550 | W730 Cooper WMA | 1485 | land polygon; Rule 7 cleared (lake is USACE) |

### Research pin_wrong (3) — accept polygon; never move pins
| ref | record | m | flag |
|---|---|---|---|
| CA-0527 | OBJECTID:88 Birch Island PP | 158442 | POTA pin wrong |
| CA-0558 | OBJECTID:22 North Steeprock Lake PP | 110743 | POTA pin wrong (lat ~1° typo) |
| US-6551 | W717 Wintermann WMA | 4728 | POTA pin wrong |

## NEEDS-PERSON (2)
| ref | why |
|---|---|
| US-3729 | Rule 18: State Recreation Area vs Recreation & Public Fishing Area (PAD-US 194918) |
| CA-0551 | Official corridor OK; pin 4,233 m N of edge — person to flag/report pin |

## UNTOUCHED (3)
US-4650, US-6572, US-7896.

## Hashes
US a066624520b4 / CA 8feccbb7d9ee / world 10e4092cc97f — unchanged.

## Brandon sign-off (t786u, Nov 8 2026) — applied in follow-on PR
Name matches boundary; pins are tools not proof. Overrides with decided_by for:
CA-0527, CA-0558, US-6551 (pin_wrong) and US-3505, US-3751, US-6535, US-6565, US-9770 (file-aware).
Answer sheet uses stable key ids (sgtxa/sgtxc/sggaa/sggab/Manitoba Par:); US-2200 lists sggab60 + sggab32.
