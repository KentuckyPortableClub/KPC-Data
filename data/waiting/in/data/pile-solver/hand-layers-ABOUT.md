# Hand-layer pile solver hand-run (Nov 8 2026) — SEPARATE from the Nov 4 full pile

**Must-keep:** the Nov 4 full outputs in this folder (`solved-join.csv` 52 SOLVED-JOIN, `needs-person.csv`, `run-log.md`, area `*.json`, etc.) are **unchanged**. This hand run writes only the `hand-layers-*` files below.

- **MODE=backfill**, 17 parks from PR #50 holds (+ Rule-18 unjoins). **auto stays false.**
- Pins never moved. No cron. Proposals only.
- File-aware pass: 5 robots-blocked parks re-checked against `#50` hand-layer GeoJSON (no live ArcGIS).
- Quality NO on #51 @aa6975fd addressed: no overwrite of Nov 4 outputs; US-3729 is NEEDS-PERSON (Rule 18).

## Files (this hand run only)
| file | contents |
|---|---|
| `hand-layers-solved-join.csv` | 5 SOLVED-JOIN (file-aware Rule 3) |
| `hand-layers-needs-person.csv` | US-3729 (Rule 18) + 8 other NEEDS-PERSON |
| `hand-layers-untouched.csv` | 3 already decided in overrides |
| `hand-layers-answer-sheet-proposals-US.csv` | YES proposals for the 5 |
| `hand-layers-pile.csv` | input pile (if present) |

## SOLVED-JOIN (5)
| ref | record | m | flag |
|---|---|---|---|
| US-3505 | sgtxa4942 Honey Creek | 334.3 | POTA pin may be off |
| US-3751 | sggaa882 GRAND BAY WMA | 638.6 | POTA pin may be off |
| US-6535 | sgtxc140 Angelina Neches/Dam B WMA | 855.8 | POTA pin may be off |
| US-6565 | sgtxc96 J. D. Murphree WMA | 808.8 | POTA pin may be off |
| US-9770 | sggaa861 ALTAMA PLANTATION WMA | 648.3 | POTA pin may be off |

## NEEDS-PERSON
| ref | why |
|---|---|
| **US-3729** | Rule 18: State Recreation Area vs Recreation & Public Fishing Area (PAD-US 194918) — not SOLVED-JOIN |
| US-6571 | Rule 18 tract (Anacua Unit) |
| US-6550 | Rule 7 water-only question |
| US-6551, US-2200, CA-0527, CA-0558, CA-0551, CA-2373 | pin / no join / Rule-18 unjoin (see CSV) |

## UNTOUCHED (3)
US-4650, US-6572, US-7896 — existing overrides joins (not Brandon sign-offs).
