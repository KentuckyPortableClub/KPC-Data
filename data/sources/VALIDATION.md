# Validation – GIS sources and review-list CSV import (2026-11-04)

Checked by Grok Bot against the CSV spec Brandon gave the outside agent. Files are byte-identical to the zip; **no fixes were needed** (no BOM, no CRLF, no stray whitespace, all valid UTF-8, no formula-like cells).

## Layout
- `gis/` – source lists (GIS column layout) plus `pota-kind-map.csv` (own 5-column layout).
- `review/` – park lists (park column layout) plus patterns / duplicates / key-builder-fixes summary tables (own layouts, as the README says).
- Not placed under `data/review/` because `kpc-scoreboard.yml` watches that folder.

## Results
- Headers: every GIS and park file matches the spec exactly; 8 summary files use their own documented headers.
- Row counts: all 19 match README.txt.
- Field counts: every row has the header's field count. No exact duplicate rows in any file.
- Refs: all park refs match `XX-NNNN(N)`. No ref appears in more than one dropped-list file.
- Coordinates: all present values are numeric and in range.
- Enums: `decision` only blank/NO; `format` and `has_boundaries` only spec values or blank; all URLs present are well-formed http(s).

## Things to know (not errors)
- `no-boundary.csv`: 6 refs appear twice (e.g. US-5965, US-5749, US-10421) – cross-state parks, 15 rows marked "conflict" in notes as the spec asks.
- `pota-bad-pin.csv`: pin_lat/pin_lon blank on all 65 rows (source sheet had no pins).
- `distance_km` blank on every park row (source lists had no candidate distance).
- GIS `url`/`format` blank: sources-by-country 207/207 (suggestions, never checked live), proposed-new-layers 15/85, japan-source-plan 5/5.
- `pota-kind-map.csv`: 4 rows are marked "guess" – never used for a MATCH.

## Decisions
- `decided_by` and `decided_date` are blank on every row. No row carries a person's sign-off.
- `override-no.csv`: 1,581 rows with `decision=NO` copied from overrides.json, unsigned. These are **not** new decisions and nothing here feeds overrides.json. This PR does not touch overrides.json.
- "PROPOSED" answers are only in notes, not in `decision`.
