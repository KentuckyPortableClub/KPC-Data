# KPC 8 NO Rechecker: test report (31 Oct 2026)

Tested on Python 3.13.5 with requests, shapely 2, pyproj, rapidfuzz and numpy. The inputs were the four files in `sample_input/`
(the same files as `input/`). All network reads were live on 31 Oct 2026 and went into one shared cache. The sample runs below
were then re-run from that cache, after the last scoring change, so they show what the final code gives.
**The tool never changed an answer.** The input files' SHA-256 values are the same before and after every run (each output records them).
A unit test also checks the files byte for byte.

## Unit tests

`python3 -m pytest -q tests` gives **40 passed**. They are offline and use made-up shapes and a fake network.

* **Geometry:**
  * pin inside / outside (metres away);
  * line records within 100 ft;
  * equal-area acres;
  * Esri rings with holes.
* **Names:**
  * initials;
  * "Lake" vs "Lake Cumberland WMA" (weak words only);
  * the Chena score;
  * every text field read;
  * a long note can't match on one word;
  * website title pieces must share a real word;
  * owner fields (private people) are never used or shown.
* **Kind:**
  * WMA vs park conflicts;
  * the kind taken from the record's name when it has no type field (Aniakchak National Preserve, Alatna ANVSA);
  * the matched pair must agree (Galena Creek Fish Hatchery vs Galena Creek Regional Park, Wolf Creek vs Wolf Creek Falls Trail);
  * a line record (a road or a fire break) is never an area park;
  * facility, World Heritage and lighthouse kinds.
* **Verdict rules:**
  * every LOOK AGAIN / KEEP NO branch;
  * BETTER RECORD from a neighbour;
  * record gone and no geometry give CAN'T TELL.
* **Run behaviour:**
  * the club's order of work (KY → US/CA → rest of North America → world);
  * the 15 % cap, which stops a batch and withholds its questions;
  * a layer that is down gives CAN'T TELL and is retried on `--resume`;
  * exit codes 3, 0 and 2;
  * `--limit` and `--areas`.
* **Politeness:**
  * the User-Agent;
  * back-off with Retry-After;
  * ≤ 1 request per second per host;
  * forbidden hosts (OSM, Google …) refused;
  * robots.txt;
  * `--offline`;
  * a dead website is tried only once per run.
* **Safety:**
  * an end-to-end run with a fake network leaves the input files **byte-identical**;
  * so does a run over the real `sample_input/` files.

## The Chena flip (US-10464 Chena Wayside)

The row's answer is now `NOT SURE` (chat 11), not NO, so the default (strict NO) skips it. To recheck it:
`--files gis-hunter.json --answers NO "NOT SURE" --refs US-10464`.

The real networked read was at 5:22 PM CT on 31 Oct 2026:
* POTA API;
* the Alaska DNR ArcGIS layer, 3 layer copies, record 122;
* the POTA-listed website `dnr.alaska.gov/parks/aspunits/northern/chenariversrs.htm`, which robots.txt allows.

`sample_run/chena/` is the final code run from that cache.

* **Verdict: LOOK AGAIN** on all 3 layer copies. That makes **1 question** (deduplicated, with `also_on_layers`), `answer: null`, `old_answer: "NOT SURE"`.
* **Evidence:** `US-10464 'Chena Wayside State' vs record 122 'Chena River State Recreation Site': POTA pin inside, name 1.00 on PARKNAME='Chena River State Recreation Site', record 27 ac, kinds agree (park).`
* **Scores:**
  * pin inside, 0 m;
  * name 1.00 (the website title "Chena River State Recreation Site"); POTA's own name "Chena Wayside State" alone scores 0.98;
  * record 27.4 ac (the row says 18);
  * size ratio n/a (no park acres);
  * kinds agree: park (`PRKTYPABRV=SRS`).

Nothing about the ref is special-cased. It passes the same rules as every other row.

## Real runs (final code, live data read 31 Oct 2026)

The inputs hold **835 strict NO rows**: 362 in gis-hunter, 157 in layers, 63 in key-pieces and 253 in the world sample.
(An earlier note said 1,052. That was wrong.)

A row is one input row: one ref on one layer. Many refs are repeated on 2–3 copies of the same layer, for example US-7208 on the
AK DNR MapServer/2, FeatureServer/2 and DPOR layers, and CA-2727 on SK FeatureServer/4, FeatureServer/1 and CPCAD.
These are real duplicates in the input, not a batching bug. `questions.json` merges a ref asked on several layer copies into one question.

### Full run D: all four files, every NO row (`sample_run/run_full/`)

The run started with `--max-minutes 20`. It hit exit 3 and carried on with `--resume`. After the scoring fix below, it was
re-run from the cache, with network for anything missing, into a fresh `--out`, then `--resume`. It **finished with exit 0. All 835 rows have a verdict, and no batch was stopped.**

| file | NO rows | LOOK AGAIN | BETTER RECORD | KEEP NO | CAN'T TELL | flagged |
|---|---|---|---|---|---|---|
| gis-hunter.json | 362 | 8 | 0 | 343 | 11 | 2.3 % |
| layers.json | 157 | 1 | 1 | 151 | 4 | 1.3 % |
| key-pieces.json | 63 | 0 | 0 | 0 | 63 | – |
| world-finder-sample.json | 253 | 0 | 0 | 18 | 235 | 0 % |
| **all** | **835** | **9** | **1** | **512** | **313** | **1.9 %** (10 of 522 judged) |

Per area, the flagged rows are:
* gis-hunter: CA-YT 1/8, US-AZ 1/2, US-KS 1/8, US-MD 1/6, US-NC 2/17, US-OR 2/8;
* layers: W-AU 1 BETTER RECORD of 71, W-IE 1/2.

Every other area is 0 flagged. The full per-area table is in `sample_run/run_full/no_recheck/summary.md` and `report.csv`.

**All four input files have the same SHA-256 after the run as before.**

### Runs A, B and C, and Chena (final code, from the same cache)

| run | file | NO rows (unique refs) | LOOK AGAIN | BETTER RECORD | KEEP NO | CAN'T TELL | flagged |
|---|---|---|---|---|---|---|---|
| A: US-KY, US-TN, US-AK | gis-hunter.json | 20 (12) | 0 | 0 | 20 | 0 | 0 % |
| | key-pieces.json | 1 (1) | 0 | 0 | 0 | 1 | – |
| B: CA-SK | layers.json | 10 (4) | 0 | 0 | 10 | 0 | 0 % |
| C: world sample | world-finder-sample.json | 253 (253) | 0 | 0 | 18 | 235 | 0 % |
| Chena: `--refs US-10464 --answers NO "NOT SURE"` | gis-hunter.json | 3 (1) | 3 | 0 | 0 | 0 | 1 question |

* **A:** there are no US-KY or US-TN NO rows in these files, so run A is in practice Alaska.
* **B:** the Environment Canada CPCAD host (`maps-cartes.ec.gc.ca`) dropped TLS connections from this box on the first day's
  first try. That gave CAN'T TELL, and the row was read on a later try.

## The cap event and what was done about it

The first full run, with the earlier scoring, gave 18 LOOK AGAIN and 1 BETTER RECORD (4.0 %).
The cap **stopped batch `layers.json|W-AU`** at 5 LOOK AGAIN of 29 judged (17 %). The rest of that batch was left unchecked.
The flags were:

| ref | park | record it matched | geometry |
|---|---|---|---|
| AU-6992 | Cordalba State Forest | `Internal Roads - Cordalba SF` (name 0.90) | LineString |
| AU-7208 | Borania State Forest | `Internal Roads - Borania SF` | LineString |
| AU-7191 | Auburn State Forest | `Internal Roads - Auburn SF` | LineString |
| AU-7254 | Dyngie State Forest | `Internal Roads - Dyngie SF` | LineString |
| AU-7312 | Borilla State Forest | `Internal Roads - Borilla SF` | LineString |
| AU-7141 (BETTER RECORD) | Traveston State Forest | the row's record was `Traveston Boundary Break - North`; suggested `Internal Roads - Traveston SF` | LineString |

**Judgment: the scoring was too loose. These are not real look-again cases.**
* Each record is a **road or fire-break line** on the Queensland forestry layer, which happens to carry the forest's name.
* A line can't be "the outline of" a state forest. The pin only "fit" because lines count within 100 ft.
* The cap did its job.

Looking at the other first-run flags turned up the same kind of looseness:
* US-12471 Lone Rock matched `Lone Rock Drift Boat Launch` (1 ac).
* CA-6178 Cape George **Lighthouse** matched `Cape George Provincial Park`.
* ID-0044 Gunung Tambora National Park matched `SM Gunung Tambora Selatan`, a *suaka margasatwa*, i.e. a wildlife reserve.
* ZA-0097 Mapungubwe National Park matched the 656,000 ac `Mapungubwe Cultural Landscape`, the World Heritage area.

**The fix is general rules, with no refs special-cased:**
1. **Shape test:** a line or point record (a road, a fire break, a boat ramp) is never an *area* park. It only fits a park
   whose kind is a trail, river or road. This applies to the row's record and to neighbour candidates.
2. **More kind words:**
   * boat launch / boat ramp / trailhead / day-use area (facility);
   * internal roads / boundary break / fire break (road);
   * World Heritage site / cultural landscape (heritage);
   * lighthouse / light station (a lighthouse, not the park around it);
   * *suaka margasatwa* / SM (wildlife reserve), *cagar alam* (nature reserve), *taman nasional* (national park).
3. Robustness: a website that fails to answer is tried twice and then skipped for the rest of the run, rather than retried on every row.
   The extra name is optional. This took the Delaware rows from about 10 minutes each to seconds.

There is no cap override flag, on purpose. A trip means "fix the scoring", which is what was done (see the README).

Results after the fix:
* W-AU: 0 LOOK AGAIN, 1 BETTER RECORD out of 71. The whole batch was checked and the cap did not trip.
* Overall: 9 LOOK AGAIN and 1 BETTER RECORD (1.9 %).
* Chena is still LOOK AGAIN.
* There are 40 unit tests, including new ones for the shape test, the new kinds and the dead-website rule. All pass.

## The 10 flagged rows (with their evidence lines)

These come from the final full run plus Chena. Each one is a **question for a person** (`answer: null`), not an answer.
US-3862 is asked on two layers, and only the first is listed.

1. **US-10464** (US-AK), old NOT SURE: `US-10464 'Chena Wayside State' vs record 122 'Chena River State Recreation Site': POTA pin inside, name 1.00 on PARKNAME='Chena River State Recreation Site', record 27 ac, kinds agree (park).`
2. **AU-10042** (W-AU, BETTER RECORD), old NO: `AU-10042 'Cooloola': answered NO for record 64758 'Cooloola Drive'; record 76055 'Cooloola' on the same layer has POTA's pin inside, name 1.00.`
3. **US-2334** (US-KS), old NO: `US-2334 'Cross Timbers' vs record 577 'Toronto Point': POTA pin inside, name 1.00 on Description2='Cross Timbers State Park', record 693 ac.`
4. **US-10751** (US-MD), old NO: `US-10751 'Idylwild' vs record 16 'Idywild': POTA pin inside, name 0.93 on AREA_NAME='Idywild', record 1497 ac.`
5. **US-3862** (US-NC), old NO: `US-3862 'Nags Head Woods Ecological' vs record 21316 'Nags Head Woods (Town of Nags Head) Registered Heritage Area': POTA pin inside, name 0.95 on MA_NAME='Nags Head Woods (Town of Nags Head) Registered Heritage Area', record 283 ac, kinds agree (natural).`
6. **US-10025** (US-OR), old NO: `US-10025 'Lost Forest/Dunes/Fossil' vs record 10853 'Christmas Valley Sand Dunes': POTA pin inside, name 0.93 on UNIT_NAME='Lost Forest-Sand Dunes-Fossil Lake ACEC', record 9821 ac, kinds agree (blm).`
7. **US-10008** (US-OR), old NO: `US-10008 'Klamath Hills' vs record 111 'Lower Klamath Hills': POTA pin inside, name 0.98 on RMA_NAME='Lower Klamath Hills', record 1596 ac.`
8. **US-12162** (US-AZ), old NO: `US-12162 'Sears Point' vs record 50 'Sears Point Core': POTA pin inside, name 0.95 on ACEC_NAME='Sears Point Core', record 3679 ac.`
9. **CA-6265** (CA-YT), old NO: `CA-6265 'Tagish Bridge' vs record 14 '': POTA pin inside, name 0.91 on REMARKS='LOT 37 TAGISH ( TAGISH BRIDGE TERRITORIAL PARK CAMPGROUND)', record 1 ac.`
10. **IE-0161** (W-IE), old NO: `IE-0161 'Macgillycuddy's Reeks and Caragh River' vs record 90 'Killarney National Park, Macgillycuddy's Reeks and Caragh River Catchment SAC': POTA pin inside, name 1.00 on SITE_NAME='Killarney National Park, Macgillycuddy's Reeks and Caragh River Catchment SAC', record 205349 ac.`

My own read:
* 1, 2, 3, 4 and 5 look like real look-again cases. AU-10042 was answered against a *road* called Cooloola Drive, and the area record "Cooloola" is right there.
* 10 is probably real: the POTA park is the SAC's own name.
* 6, 7 and 8 are BLM units with near names, worth a quick look.
* 9 is a 1-acre lot whose remarks name the campground, probably a correct NO.

## Common CAN'T TELL reasons (full run, 313 rows)

* **296: the row names no layer URL.**
  * 233 world rows name a layer without a URL, e.g. `CAPAD (DCCEEW)`, `EEA nationally designated areas` or `Natural England SSSI`.
  * 63 key-pieces rows have no layer at all (ids like `fws448`).
  * The tool doesn't map layer names to URLs, because layers must come from the input rows.
* **11: the record id is not an object id** (e.g. `None`).
* **6: the record is gone**: the object id is no longer on the layer.
* Layer hosts that drop the connection (`maps-cartes.ec.gc.ca`) give CAN'T TELL when it happens. These rows are retried next run.

## Deviations and unknowns

* **Park acres are almost never known.**
  * POTA's API has no acres, and the rows' `acres_approx` is the record's size.
  * So the size test (within 10×) is rarely applied, and the 0.75–0.90 name band never gives LOOK AGAIN without acres.
  * This leans toward KEEP NO. It is also why a big parent area with the exact same name can still be flagged (it is a question, not an answer).
* `NOT SURE` is not a NO. Chena needs `--answers NO "NOT SURE"`.
* **Extra flags:** `--refs` (which also turns the cap off), `--answers`, `--in-dir`, `--cache-dir` and `--min-interval`.
* **The cap needs at least 3 LOOK AGAIN** in a batch before it can trip, so 1 hit in a 5-row area doesn't stop it.
* **Neighbours** are read only when the row's own record doesn't already qualify. Neighbour shapes are lightly generalised (about 5 m).
* "Whole canal vs one section" is caught only where the type words differ.
* Tested on Python 3.13.5, not 3.11 (no 3.12+ features are used). It hasn't been run as a GitHub Action, and it is **not wired into anything**.
