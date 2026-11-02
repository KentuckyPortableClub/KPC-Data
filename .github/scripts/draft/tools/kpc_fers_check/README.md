# KPC 2-fer Accuracy Checker

Re-checks every **live** 2-fer row in the club's `data/fers/<area>.json` against the **live official layers**
the club's boundary keys name, then writes a verdict per row. The tool is read-only. It **never edits the
2-fer files** and is **not wired into any workflow**. A person reviews the report, and the club's waiting
room decides what happens next.

* `kpc_fers_check.py` is the tool (one file).
* `tests/test_verdicts.py` holds the unit tests of the verdict logic, using synthetic geometries (no network).
* `schema/fers_input.schema.json` and `schema/fers_input.example.json` cover the input format the tool reads.
* `fixtures/data/` is a small real subset of the club data (5 KY, 3 UT and 4 VA live rows, plus one dropped row per area).
* `sample_run/` holds the outputs of the full KY, VA and UT run on 31 Oct 2026.
* `tools/compare_ky_spotcheck.py` is a test helper. It compares a US-KY run with the club's KY spot-check sheet (it needs openpyxl).
* `TEST_REPORT.md` has the results.

## Install

Python 3.11+ (it was tested on 3.13.5).

```
pip install -r requirements.txt          # requests, shapely>=2, pyproj (+ pytest for the tests)
```

## Run

Run it from a checkout of `KentuckyPortableClub/KPC-Data` (or point the flags at the folders):

```
python3 kpc_fers_check.py --areas US-KY                 # Kentucky first
python3 kpc_fers_check.py --areas US-UT US-VA           # then the others
python3 kpc_fers_check.py --areas US-UT US-VA --resume  # carry on after a time-limit stop
```

| flag | default | |
|---|---|---|
| `--areas` | (required) | area codes; reads `<fers-dir>/<area>.json` |
| `--resume` | off | keep rows already written to `<out>/<area>.json`. SOURCE DOWN rows are retried |
| `--fers-dir` | `data/fers` | 2-fer files |
| `--key-dir` | `data` | holds `ky-answer-key.json`, `us-key/<area>.json`, `us-key/layers.json` (and `ca-key/`) |
| `--trails-dir` | `<fers-dir>/../trails` | the club's saved official trail and river lines |
| `--out` | `fers_check` | output folder (also holds `.cache/`) |
| `--max-minutes` | 50 | stop cleanly after the current row, so a run stays under a 55-minute job |
| `--min-interval` | 1.0 | seconds between two requests to one host |
| `--ids`, `--limit` | | check only some rows |
| `--offline` | | cache only, no network |
| `--no-water` | | skip USGS NHD (water rows and river banks fall back to lines) |

Exit code: 0 normally (including after a time-limit stop, which prints `rerun with --resume`), and 2 when the inputs can't be read.

### Running it as a job (not set up)

The tool is ready for one job per area or chunk: `--max-minutes 50`, then a second step with `--resume`, keeping `<out>/` between steps.
**Nothing has been wired into any workflow.** Adding that is the club's call.

## Outputs

* `<out>/<area>.json` has one record per live row:
  * `verdict` and `why`
  * `flags`: R9 `small overlap (under 50 yd across)` and `water-only`, plus honesty flags such as `trail line from the club saved copy`
  * `stored_shape_acres` and `live_acres`
  * `size_pct` and `kept_pct` (the share of the stored overlap still inside the live one, with 10 m tolerance)
  * `moved_m` (how far the centre moved) and `gap_m`
  * `wide_m`, the width of the live overlap as the largest circle that fits
  * `layers`, which records every layer URL, the query and the number of features read for each park
  * `issues`
* `<out>/<area>.summary.md` holds the verdict counts plus a table of every row that isn't CONFIRMED.
* `<out>/report.csv` has one line per row for all areas in the run.

## Verdicts (in precedence order)

| verdict | when |
|---|---|
| SOURCE DOWN | an official layer didn't answer after back-off, so the row is undecided (retried on `--resume`) |
| RECORD CHANGED | the key's record id is gone, or the live record's name no longer matches the key |
| NOT CHECKED | *extra:* the key names no live official layer for a park (OSM-only outline, pin-only park, zipped file), so the tool won't guess |
| GONE | the live outlines no longer overlap near the spot (less than 10 m² of live overlap counts as none) |
| MOVED | the live overlap's centre is more than 200 m from the stored centre |
| SHRUNK | the live overlap is more than 25 % smaller |
| GREW | *extra:* the live overlap is more than 25 % bigger (the spec's CONFIRMED is "within ±25 %", so a big gain isn't confirmation) |
| CONFIRMED | within ±25 % and the centre within 200 m |

Size is judged against the stored shape. There is one exception for area and same-land rows. The stored shape can be a simplified or one-piece preview of a much bigger overlap (because of the club's point cap). If the live size is within ±25 % of the row's own `acres`, and at least 75 % of the stored shape is still inside, the size is judged against `acres` instead. That row's `size_vs` is set to `row acres`.

The R9 flags are added on top of any verdict.

## Rules used (from the spec and the club's `kpc_fers.py`)

* Only **live** rows are checked. Rows whose status starts with `dropped` or `merged` are skipped.
* Each park is re-read from its **official** layer only:
  * by record id where the key has one (PAD-US / CPCAD object ids, or `<prefix><id>` via `layers.json`)
  * otherwise by name near the spot (the KY key names a layer and an outline name)
  * Queries are ArcGIS `query` with `outSR=4326`, `f=geojson`, with an Esri JSON fallback.
  * Hosts are allowlisted. **OpenStreetMap, Google and similar hosts are refused in code.**
* All geometry is done in the spot's **UTM zone** (EPSG 326xx), using pyproj.
* **area / same land rows** use the intersection of the parks' outlines.
* **trail rows (R5)** use the park outline ∩ a **100 ft (30.48 m) buffer** of the official line.
* **river rows (R6)** are measured from the bank:
  * A *water-route* historic trail (Lewis & Clark, Trail of Tears, Star-Spangled Banner, Captain John Smith) gives 100 ft of
    land from the **bank** of the USGS NHD river or lake water that its coarse line follows (water within 3 km of the line).
  * Any other river line gives 100 ft of the line plus 100 ft from the bank of the NHD river area it runs in.
  * If NHD is down or has no water there, the line itself is used and the row is flagged.
* A trail or river row is one **stretch**. The live band is judged within 50 m of the stored stretch.
  `live_stretch_acres` reports the whole touching band.
* **water-only rows** use the outlines' overlap ∩ NHD water. For these rows a Forest Service park is read as its
  administrative boundary, because the owned-land layer leaves the channel out.
* Kentucky Daniel Boone NF is read as FS-owned land only (EDW Basic Ownership), as the club does.
* Requests are polite:
  * single-threaded
  * at least `--min-interval` between requests to one host
  * club User-Agent
  * back-off on errors, 429 and 5xx (Retry-After honoured)
  * every park record cached per run, in memory and in `<out>/.cache`

## Known limitations (read before trusting a verdict)

* A **wild & scenic river row in Zion / Kolob** (UT) can come out SHRUNK or MOVED with almost none of the stored piece inside. These stored pieces are tiny (some are 5 m long) and sit on the park edge, and the club read the Zion boundary from a downloaded NPS file, while this tool reads PAD-US. Check these rows by hand.

* **Lines are mostly the club's saved copies.** Most trail and NHT lines come from `data/trails/<ref>.json`, so they aren't
  re-read live. Live line layers are read only where the tool knows one (the EDW national forest trails and the KYGIS trail
  layers). Those rows say so in `flags`. The park outlines *are* read live.
* **The river bank method is approximate.** The club measures on a 5 m grid with a 5 m inset. This tool uses exact
  30.48 m buffers in UTM, so a few percent of difference is normal and the 10 m tolerance absorbs it. On wide rivers with
  islands, locks or reservoirs, the NHD water chosen can differ from the club's, which shows as SHRUNK or GREW. Water-route
  rows are the least certain verdicts.
* **Water-only rows usually come out GREW.** The live overlap with water includes FS-owned water that the club's channel
  piece left out. Treat GREW on a water-only row as "still there".
* Ownership or "same land" masks that the club applied on top of an outline (for example "layered on Park Service land") are
  **not** re-applied, apart from the KY Daniel Boone ownership layer.
* Stored trail zones that the club's 300-point cap garbled (area > 1.5 × `zone_acres`) are replaced by the stored line
  buffered 100 ft. This is noted in `stored_shape_note`.
* Canada (`ca-key`, CPCAD) code paths exist but are **untested**.
* It needs the network. It hasn't been run as a GitHub Action.
