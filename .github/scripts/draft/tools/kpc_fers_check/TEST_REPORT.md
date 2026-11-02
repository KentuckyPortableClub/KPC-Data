# Test report: KPC 2-fer Accuracy Checker 0.1.0

The tests ran on 31 Oct 2026 on the shared box (Python 3.13.5, shapely 2, pyproj, requests). The spec asks for Python
3.11, and nothing used here is newer than 3.11, but **3.11 itself was not tested**.

## 1. Unit tests: verdict logic on synthetic geometries (no network)

`python3 -m pytest -q tests` reports **36 passed**. The tests cover:

* **Verdicts:**
  * CONFIRMED, including the ±25 % edges
  * SHRUNK, by size and by kept share
  * GREW
  * MOVED (over 200 m) vs. not moved (under 200 m)
  * GONE, including the sliver case
  * the 10 m position tolerance
  * far live pieces ignored
  * a simplified stored shape judged against the row's acres, which never rescues a moved overlap
* **R9 flags:** small overlap (under 50 yd across) and water-only.
* **R5/R6:**
  * the 100 ft buffer is measured in UTM
  * UTM zone choice
  * the water-route bank band (lakes and rivers within 3 km, water excluded)
  * an ordinary river line plus the bank of the NHD river it runs in
  * water-route detection, including from the key name
* **`decide()` precedence:** SOURCE DOWN > NOT CHECKED > RECORD CHANGED (a renamed or missing record), plus notes.
* **Parsing:**
  * stored rings that aren't closed
  * JSON-string shapes and rings with holes
  * the fallback for a garbled trail zone
  * Esri rings
  * live vs. dropped/merged rows
* **HTTP politeness:**
  * OpenStreetMap, Google and unlisted hosts are refused
  * back-off honours Retry-After, then gives SOURCE DOWN
  * the club User-Agent is sent
  * the disk cache is reused
* **`check_spot` end to end with a stub reader:** area, trail stretch, and MOVED.

## 2. Fixture run (small real subset, `fixtures/data/`)

```
python3 kpc_fers_check.py --areas US-KY US-UT US-VA --fers-dir fixtures/data/fers \
        --key-dir fixtures/data --trails-dir fixtures/data/trails --out /tmp/fx
```

The run covers 12 live rows, 5 KY, 3 UT and 4 VA: area, same land, trail, water-route river, water-only channel, a BLM pair,
and a trail whose saved line is only points. It also has 3 dropped rows, which were skipped as they should be. All 12 came
out **CONFIRMED** and the exit code was 0.

## 3. Full real run (club's public data, live official layers)

The input is the club's public GitHub data (`KentuckyPortableClub/KPC-Data`: `data/fers`, `data/us-key`,
`data/ky-answer-key.json`, `data/trails`), downloaded once to `/workspace/kpc_testdata/data` and used read-only. Each output
records the SHA-256 of its input fers file, and all three still match, so **the 2-fer files were not changed**. The final
pass started at 4:18 PM CT on 31 Oct 2026 and re-used the layer cache from earlier passes the same day.

Rows were checked in the brief's order. Files are in `sample_run/`.

| area | live rows | CONFIRMED | SHRUNK | GREW | MOVED | GONE | RECORD CHANGED | SOURCE DOWN | NOT CHECKED |
|---|---|---|---|---|---|---|---|---|---|
| US-KY | 90 | 73 | 12 | 5 | 0 | 0 | 0 | 0 | 0 |
| US-VA (trail pairs) | 55 | 44 | 7 | 4 | 0 | 0 | 0 | 0 | 0 |
| US-UT (BLM pairs) | 147 | 122 | 11 | 10 | 4 | 0 | 0 | 0 | 0 |

**R9 flags:**

* small overlap (under 50 yd across): KY 33, VA 15, UT 29
* water-only: KY 6, VA 1, UT 1

The rows that aren't CONFIRMED are almost all **line rows**:

* **KY:** 9 of the 12 SHRUNK rows are Trail of Tears / Lewis & Clark water routes on the Ohio, Mississippi and Tennessee
  rivers and Kentucky Lake. The other 3 are trails: Pine Mountain, Sheltowee and a Trail of Tears stretch. The GREW rows are
  2 water-only channels and 3 water routes.
* **VA:** the rows are Potomac (Captain John Smith) water routes and Appalachian / NRT trail stretches, plus 1 water-only
  channel that came out GREW.
* **UT:** most are tiny wild & scenic river pieces in Zion / Kolob. The rest are a few area rows (US-6045+US-6046 GREW and
  US-6045+US-6049 MOVED 2.2 km) and 2 same-land rows (US-10974+US-6010 and US-6073+US-6074 GREW). **These are worth a
  person's look first.**

## 4. Comparison with the club's own KY checks (`KPC_2fer_spotcheck_KY.xlsx`)

`tools/compare_ky_spotcheck.py` gives the table below. The sheet column is "Overlap on official maps?".

| tool \ sheet | CONFIRMED | NOT THERE | UNCLEAR |
|---|---|---|---|
| CONFIRMED | 51 | 12 | 10 |
| SHRUNK | 7 | 5 | 0 |
| GREW | 2 | 0 | 3 |

The sheet tested the **spot point**: is the pin inside both parks, and within 100 ft of the line? This tool tests the
**overlap shape**. The two methods disagree in predictable ways:

* Most of the 12 "tool CONFIRMED / sheet NOT THERE" rows are water-route rivers. The sheet measured from the coarse NHT
  line, which is 1 to 5 km off the river, so it said NOT THERE. The club's rule measures from the river bank, and the tool
  follows the rule.
* The other "NOT THERE" rows are pins that sit 40 to 80 ft outside one park, or 234 ft from the trail, while the stored
  overlap shape is still on the official layers.
* Most of the "sheet CONFIRMED / tool SHRUNK" rows are water routes too, where the tool's bank band is smaller than the
  club's.

Agreement on plain area rows is very high.

## 5. Resume and time limit

A run with `--max-minutes 0.3` saved 43 KY rows and printed `time limit … rerun with --resume`. A second run with
`--resume` checked only the remaining 47 and marked the file complete. (The log is in
`/workspace/kpc_testdata/resume_demo.log`.)

## 6. Not tested

* Python 3.11 itself, and running as a GitHub Actions job. **Nothing is wired into any workflow.**
* Canada (`ca-key`, CPCAD) and any area other than KY, VA and UT.
* A cold run with no cache against every layer in one go. Earlier passes that day were cold, but the timing wasn't recorded
  as one 55-minute job.
* RECORD CHANGED and SOURCE DOWN on real data: no record had changed and no layer was down. Both are covered only by unit tests.
* Whether the club's private or working copies (if they differ from the public GitHub data) behave the same.
