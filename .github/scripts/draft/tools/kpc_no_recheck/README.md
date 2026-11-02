# KPC 8 NO Rechecker

Re-reads the club's **NO** answers ("this official record is NOT that POTA park") and writes **questions for a person**
where a NO looks wrong. It reads each park from POTA, and each record from the official layer that the row names.

**It never changes an answer.**
* The input files are opened read-only and are never written. A test proves they are byte-identical after a run.
* Every question it writes has `answer: null`, `checked_by: null` and `how: null`, plus `old_answer`, `old_checked_by` and `old_how`.
* A person answers YES or NO after looking at the agency map.
* It is **not wired into any workflow**.

* `kpc_no_recheck.py` is the tool (one file).
* `tests/test_no_recheck.py` holds 40 unit tests. They use synthetic shapes and a fake network, plus the real input files run with `--offline`.
* `sample_input/` holds the four test inputs (`gis-hunter.json`, `layers.json`, `key-pieces.json`, `world-finder-sample.json`).
* `sample_run/<run>/no_recheck/` holds the real-run outputs (`<file>.json`, `questions.json`, `report.csv`, `summary.md`) plus `run.log` for each run: `run_ky_tn_ak`, `run_ca_sk`, `run_world`, `chena` and `run_full` (all 835 NO rows). See `TEST_REPORT.md`.

## Install

Python 3.11+ (it was tested on 3.13.5).

```
pip install -r requirements.txt     # requests, shapely>=2, pyproj, rapidfuzz, numpy (+ pytest for the tests)
python3 -m pytest -q tests
```

## Run

Run it from a checkout of `KentuckyPortableClub/KPC-Data` (question files in `data/waiting/questions/`), or use `--in-dir`:

```
python3 kpc_no_recheck.py --files gis-hunter.json layers.json key-pieces.json --areas US-KY US-TN
python3 kpc_no_recheck.py --files gis-hunter.json layers.json key-pieces.json --resume     # after exit 3
python3 kpc_no_recheck.py --in-dir sample_input --files gis-hunter.json --answers NO "NOT SURE" --refs US-10464
```

| flag | default | |
|---|---|---|
| `--files` | (required) | question files. A bare name is looked up in `--in-dir` |
| `--in-dir` | `data/waiting/questions` | *extra:* where the files are |
| `--areas` | all | only these areas (`US-KY`, `CA-SK`, `W-AU` …) |
| `--limit` | | check at most N rows in this run |
| `--out` | `no_recheck` | output folder. It may not be the input folder. It also holds `state.json` and `cache/` |
| `--resume` | off | keep the rows already done. CAN'T TELL rows are retried |
| `--max-minutes` | 50 | stop cleanly after the current row (exit 3), so a run fits a 55-minute job |
| `--offline` | off | cache only, no network (cache age ignored) |
| `--refs` | | *extra:* only these POTA refs. This also turns the cap off, because a hand-picked list isn't a sample |
| `--answers` | `NO` | *extra:* which answers count. The default is a strict `NO…`. `NOT SURE` isn't a NO, but it can be added |
| `--min-interval` | 1.0 | *extra:* seconds between two requests to one host (it can't go below 1) |
| `--cache-dir` | `<out>/cache` | *extra:* share one cache between runs |

Exit codes:
* 0: finished
* 3: not finished (time limit, or the tool was stopped mid-way); run again with `--resume`
* 2: bad input (a missing or unreadable file, a file that isn't a question list, or `--out` pointing at the input folder)

The NO rows are taken in the club's order of work: KY first, then the rest of the US and Canada, then the rest of North America (MX, Central America, the Caribbean, Greenland), then the world.

## What it does per NO row

1. **POTA's side.** It reads `https://api.pota.app/park/<ref>` for the name, pin, website and park type, cached for 30 days.
   The `<title>` of the website POTA lists is used as one more name. robots.txt is obeyed and each redirect is checked.
   Only the title pieces that share a real word with the park's name are kept, so a site name like "Alaska Department of
   Natural Resources" can't match.
2. **The record.** It runs `<layer>/query?objectIds=<record>&outFields=*&returnGeometry=true&outSR=4326&f=geojson`, with an Esri JSON fallback.
   * **Pin test:** inside, or the distance in metres, measured in a local equal-distance projection centred on the pin.
     Line and point records count as inside within 100 ft (30.48 m).
   * **Name test:** POTA's name, the club's name and the title pieces, each scored against **every** text field of the record.
     Ids, URLs, dates and long notes are skipped. The best pair wins.
   * **Size test:** the record's equal-area acres against the park's acres, when the park's acres are known.
   * **Kind test:** the record's type field (`Des_Tp`, `PRKTYPABRV`, `FET_SUBTYPE` …). If it says nothing, the type words in
     the record's name are used. A conflict means both kinds are known and share nothing (river vs preserve, park vs WMA,
     park vs a tribal statistical area, field office, ranger district, boat launch, World Heritage cultural landscape,
     lighthouse vs the park around it …). The matched record name's own type words must also agree with the park.
   * **Shape test:** a line or point record (a road, a fire break, a boat ramp) is never an area park. It can only match a
     park whose kind is a trail, a river or a road.
3. **Neighbours.** It looks for other records on the same layer within 2 km of the pin. Attributes come first; shapes
   are fetched only for names scoring 0.90 or more. This step is skipped when the row's own record already qualifies.
4. **Verdict** (below).

The name score is based on `kpc_map_links.py`'s normaliser (lower case, `&` becomes `and`, St becomes Saint, punctuation
dropped, park-type words dropped). It is extended with more type words and abbreviations (`SRS`, `WMA`, `NWR`, `ANVSA` …).
* The score is `min(token_set_ratio, share of the park's words found)`.
* If only weak words match (lake, river, creek, mountain, county, a compass word …), the score is capped at 0.60.
* Each record word the park doesn't have costs 0.05 (0.02 for a weak word), up to 0.40. That way "Lake" doesn't match
  "Lake Cumberland WMA", and "Dunvegan" doesn't match a long comment that happens to contain it.

## Verdicts

| verdict | when |
|---|---|
| LOOK AGAIN | POTA's pin is inside the record, there is no kind conflict, the size is within 10× (when known), and the name scores ≥ 0.90, or 0.75–0.90 **with** acres within 3× |
| BETTER RECORD | a neighbour on the same layer has the pin inside, a name ≥ 0.90 and better than the row's record, and no kind conflict; it isn't a record already answered for that ref |
| KEEP NO | anything else. `why` gives the first reason in the spec's order: pin outside, low name, kind conflict, size way off, and so on |
| CAN'T TELL | no layer URL in the row, a record id that isn't an object id, POTA down, the layer down after back-off, the record gone, or no geometry. These rows are retried on `--resume` |

**Safety cap:** a batch is one file, or one area inside a file. It is stopped when it has at least 3 LOOK AGAIN rows and
LOOK AGAIN is more than 15 % of the rows judged so far (CAN'T TELL rows aren't counted).
* The message is `too loose: check the scoring`.
* The stopped batch's questions are **withheld** from `questions.json`.
* The cap is shown in `summary.md` and `report.csv`.
* The rest of a stopped batch is **left unchecked** (no verdict). `--resume` won't restart it, because the cap counts carry over.
  There is deliberately **no override flag**: a trip means the scoring is too loose for that data. Fix the scoring, then run
  again with a fresh `--out`. The cache makes that cheap. Either way, the tool never changes an answer.

## Outputs (in `--out`)

* `<file>.json` has one record per NO row:
  * `ref`, `layer`, `record`, `verdict`, `why`
  * `pin_inside`, `pin_dist_m`, `name_score`, `best_field`, `best_text`, `size_ratio`, `kind_conflict`
  * `better` {id, name, acres, score, pin_inside}, `read_date`
  * plus the evidence fields: `pota_name`, `names_used`, `record_acres`, `park_kind`, `record_kind`, `website_title`, `evidence`
  * the file also records `input_sha256`
* `questions.json` holds **only** the LOOK AGAIN and BETTER RECORD rows, in the input question shape:
  * `answer`, `checked_by` and `how` set to null
  * `old_answer`, `old_checked_by`, `old_how`, `recheck_verdict`, `evidence` (one plain line) and `suggested_record`
  * a park asked on several copies of one layer is one question, with `also_on_layers`
* `report.csv` and `summary.md` hold the verdict counts per file and per area, the flagged rate, the cap, and the
  questions and the CAN'T TELL reasons.

## House rules (in code)

* Layers come **only** from the input rows. OSM, Google, AllTrails and Protected Planet hosts are refused.
* POTA pins are only compared, never moved.
* It uses one thread and at most 1 request per second per host, with the User-Agent
  `KPC-no-recheck (https://github.com/KentuckyPortableClub)`.
* It backs off on 429 and 5xx, honouring Retry-After. Timeouts and connection errors are retried 5 times.
* robots.txt is obeyed for web pages (ArcGIS REST and the POTA API are services, not pages).
* One failure never stops a batch. The row is logged as CAN'T TELL and the run carries on.
* There is a disk cache (30 days; errors are never cached). `--offline` uses it only.

## Known limitations (read before trusting a verdict)

* **The park's acres are almost never known.** POTA's API has no acres, and the rows' `acres_approx` is the *record's*
  size, not the park's. So the size test is mostly not applied, and the 0.75–0.90 name band can't produce LOOK AGAIN without acres.
  This is on purpose: it leans toward KEEP NO.
* **Rows without an ArcGIS layer URL are CAN'T TELL.** That covers all `key-pieces.json` rows (ids like `fws448`, no
  layer) and most world rows (the layer is a name such as `CAPAD (DCCEEW)`). Mapping a layer *name* to a URL would break
  "official layers from the input rows only", so the tool doesn't guess.
* A strict NO only. `NOT SURE` rows (Chena is one now) need `--answers NO "NOT SURE"`.
* "A whole canal vs one section" is only caught where the type words say so (river vs preserve and similar). Two units of
  the same kind with the same name aren't told apart beyond the pin and the name.
* Neighbour shapes are lightly generalised (about 5 m) to keep the responses small. Very big records fall back to a coarser shape.
* Some hosts refuse this box's network (e.g. `maps-cartes.ec.gc.ca` drops the TLS connection). Those rows are CAN'T TELL.
* It needs the network, apart from `--offline`. It hasn't been run as a GitHub Action.
