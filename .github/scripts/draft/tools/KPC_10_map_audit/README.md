# KPC 10: Whole-map accuracy audit

This tool grades every saved park outline with nine simple tests and ranks the worst first, so a person checks those first.
**It decides nothing: it only ranks.** It never changes a key or an outline, never moves a POTA pin, and never uses OSM, Google or WDPA.

## Setup
```
python3 -m venv venv && . venv/bin/activate
pip install -r requirements.txt
```
Needs Python 3.11 or newer.

## Run
```
python kpc_map_audit.py --areas US-KY US-TN CA-ON CH --data data --ky-outlines club-outlines --out audit
```
| option | what it does |
|---|---|
| `--areas` | `US-xx` (the Kentucky key for US-KY, `us-key/<area>.json` for the others), `CA-xx` (`ca-key/` + `canada-bounds/`), or a country prefix such as `CH` (`world-bounds/CH/`) |
| `--data` | the folder holding `ky-answer-key.json`, `us-key/`, `ca-key/`, `canada-bounds/`, `world-bounds/`, `fers/`, `trails/`, `parkinfo/`. It is only read. |
| `--ky-outlines` | the folder with the club's `ky-*.geojson` outline files (Kentucky only) |
| `--acres acres-list.json` | optional: the club's acreage list (`{ref: acres}`), used when a record has no acres of its own |
| `--out` | where results go (default `audit/`) |
| `--cache` | the disk cache of everything read, with its date (default `.kpc-cache/`) |
| `--max-minutes 50` | stops cleanly when time is up (exit 3) |
| `--resume` | carries on: finished areas are kept, and parks already graded are not graded again |
| `--offline` | cache only, no network |

Exit codes: **0** = done, **3** = not finished (run again with `--resume`), **2** = bad input.
If a source is down, the park is marked `SOURCE DOWN: retry next run`. Its tests show CAN'T TELL and the batch carries on.

## The tests
| # | test | flags |
|---|---|---|
| T1 | Is POTA's pin inside the outline? | PASS (0 m), NEAR (≤ 500 m), OUTSIDE (> 500 m), FAR (> 10 km). For a trail or river line, a pin within 30 m counts as on it. If a park spans several states or provinces, an OUTSIDE or FAR pin becomes a NOTE instead. |
| T2 | Outline acres (geodesic, equal-area) vs the official acres | PASS (within ×1.5), OFF (×1.5–5), WAY OFF (over ×5). The official figure is the record's own acres (PAD-US GIS_Acres or CPCAD O_AREA_HA), then the key's acres, then `--acres`. |
| T3 | The record name vs POTA's current name | PASS (≥ 0.9), WEAK (0.75–0.9), MISMATCH (< 0.75). Names are normalised for case, accents and punctuation; initials are joined and type words dropped. The score is the token-set ratio, capped by how many of the park's own words the record has. |
| T4 | The record's type vs the park's type | CONFLICT for WMA vs state park, a whole lake vs a recreation area on it, a whole canal vs one section, or a proclamation line vs owned land |
| T5 | Shape health, on the shape exactly as the source sent it | INVALID, SELF-INTERSECTION, SLIVERS (under 10 m wide), TINY HOLES (under 100 m²), SCATTERED (more than 50 pieces over more than 50 km), EMPTY |
| T6 | Spill | SPILL when the outline covers more than 30% of another POTA park's pin area, the names differ, and there is no 2-fer row. The pin area is that park's own outline, or 500 m around its pin. |
| T7 | Detail of a saved copy vs the 3 m rule | TOO COARSE over 5 m (a NOTE for world parks). Records read live are N/A. |
| T8 | Duplicate | DUPLICATE when two park numbers use the same record id. These are listed for KPC 13. |
| T9 | Age | STALE CHECK when the source's last edit (from the layer's details) is more than a year older than the club's read date. Sources edited *after* the club read them get a NOTE. |

**Score:** 0 means every test passed. OUTSIDE, WAY OFF, MISMATCH, CONFLICT and SPILL add 3 each, FAR adds 5, and every softer flag adds 1. NOTE, N/A and CAN'T TELL add 0.

## Outputs (in `--out`)
- `<area>.json`: one record per park, with every test result, `score` and `why` (one plain sentence naming the worst flag).
- `worst.csv`: every area together, highest score first (only parks with flags). This is the checker's work list.
- `summary.md`: for each area, how many parks pass and how many have flags, a count of each flag, and the 10 worst.
- `questions.json`: the 50 worst per area as checker questions, in the club's question shape. `answer` is null, and the record link and POTA link are filled in. `picture` is left empty for KPC 9.

## Polite reading
The tool sends at most one request per second to each host, with the User-Agent `KPC-map-audit (https://github.com/KentuckyPortableClub)`. It backs off on 429 and 5xx errors and obeys robots.txt.
Everything it reads is cached with the date. US and Canadian records are read with a 1 m generalisation (`maxAllowableOffset`). If a record looks broken at that detail, it is read again at full detail before T5 flags it.

## Tests
`python -m pytest -q tests` runs offline on made-up shapes.

## Examples
`examples/` holds the `summary.md`, `worst.csv` and `questions.json` from the test run on US-KY, US-TN, CA-ON and CH. The per-area JSON files (4 MB in all) are left out to keep the zip small.
