# kpc_pulloffs — test report (2026-10-31)

Plain summary: the tool is built to the spec and passes its offline selftest. On real
Kentucky data (Clifty Wilderness / KY-715) the first version produced only false
positives. The three fixes below remove them on that sample, but they were tuned on the
same sample, so **precision and recall are still not proven**. Every number below was
measured in a real run. Nothing is estimated unless it says so.

## 1. Offline selftest (synthetic data): PASS

`python kpc_pulloffs.py --selftest`: Python 3.12.16 in a clean venv from `requirements.txt`.
It also passes with the network switched off (`unshare -rn`). Time is about 3 s.

The selftest draws a fake 4-band NAIP photo and TIGER-like roads from `tests/scene.json` and
compares the result with `tests/expected_output.json`. It checks:

- **Found:** an inside lot; an outside lot (~75 m, with the outside label and "About 80 m outside"); and a lot ~320 m outside a park with no access points (ruling G-P2), marked "photo is old (2019)".
- **Kept out with the right reason:** a road shoulder 5 m wide (G-P1), a lot under 300 m², a lot on an interstate, a lot on a private road, a brown field, a farm lane plus a yard with a roof, a house whose outline comes from FEMA, and a patch below the cut. A dry hay field produces no candidate. A lot 0 m from an official pin is dropped as a duplicate.
- **Parks with no output:** a park with no outline, a park whose outline is blocked by robots.txt, and a park in another area.
- **Exit codes and files:** 3 when time runs out, then 0 with `--resume`. Every row has `source_url`/`read_date`/`why`. "Parking" never appears without "possible". Chips are JPEG ≤400 px with red, white and yellow drawing. review.md is sorted best first and carries the notice. report.md has the recall line.
- **Web manners:** robots.txt is obeyed. 429 gets 3 retries, then the host rests. Only allowed hosts were asked. Nothing is written outside --out. The never-use guard holds, and banned names appear only in the guard block of the code.

Full output: see the last section.

## 2. Live Kentucky tests (real servers)

Inputs are in `tests/live_ky715/`:

- **Official outline:** USFS EDW `EDW_Wilderness_01` (Clifty Wilderness, boundary status Final).
- **Access pins:** a stand-in for KPC's `data/access`, which I don't have. These are 9 USFS recreation sites from `EDW_RecreationOpportunities_01`, such as Gladie Visitor Center, Sky Bridge and Copperas Creek.

| Run | What | Result |
|---|---|---|
| A | Whole Clifty outline, `--max-minutes 30` | 84 photo cells planned. It stopped after 35 cells: **exit 3** after 30.3 min, 63 requests. Nothing was written for the park, as designed. The report now names the partial park and the cell count. NAIP took **about 30–90 s per 660 m tile**; the photo-year catalog query took ~2 min. Robots: tigerweb returns a WAF web page and imagery.nationalmap.gov returns 403, so both were treated as allow-all (RFC 9309). |
| B | West part only (the official outline clipped at UTM x < 271300, **test-only clip**, 45 cells), first algorithm | Exit 0 in 11.1 min. **12 candidates; 0 of 12 were real when I checked the chips by eye**: dry hay fields, house yards and driveways, farm yards. One NAIP tile got HTTP 502; it was logged and the run carried on. |
| C | Same area after the fixes, cached | Exit 0 in 2.4 min, 8 new requests, 230 FEMA building outlines. 1 candidate: the KY-715 pavement itself (the TIGER line is offset ~15 m). |
| D | After the road-offset rule | Exit 0. **0 candidates, 18 kept out**: 12 too small, 4 next to FEMA buildings outside the park, 1 strip along the road (the KY-715 pavement from run C), and 1 long-and-thin lane. |

Fixes made because of runs B and C:

1. **Dry grass/hay is not bare.** If NDVI > 0.07 and saturation > 0.33, the pixel is dry grass or hay. Real hay measured NDVI ~0.09, saturation ~0.44, NIR ~190. Gravel measured NDVI ~0, saturation <0.2.
2. **Real roofs are dark, so the photo roof test missed them.** The tool now also uses **FEMA USA Structures** building outlines, a public government layer with no key: `services2.arcgis.com`, ArcGIS Online. A lot next to a building outside the park is dropped and logged.
3. **Long strips along the road** (over 60 m long, under 20 m wide, within 20° of the road) are logged as "probably the road itself".

Seen in the live data:

- **Gladie Visitor Center lot was not found.** The lot sits behind a short entrance drive and does not touch KY-715. The spec's "touching the road" rule skips it. It is an official site, so it would have been dropped as a duplicate anyway, but this is a recall risk for set-back lots.
- **No official pin fell inside the clipped band**, so the live recall line reads 0/0. **Live recall was not measured.**

## 3. Acceptance items

| Item | Status |
|---|---|
| Recall ≥ 60% (official pins next to a road) | **Not measured on real data.** I have no KPC-Data `data/access`. The synthetic test reads 1/2 (50%) by design: one pin sits on a lot and one on a boat ramp. |
| Precision ≥ 80% (chat 11 sample) | **Not measured.** I have no chat-11 sample. On real data: run B was 0/12. Run D has 0 candidates, but its rules were tuned on that same area, so it is not an independent test. |
| Zero farm lanes on the 6 example parks | **Only synthetic** (farm lane + yard rejected). The 6 real example parks were not run, because there is no KPC park list or outlines. In run D, 4 real house/farm yards next to FEMA buildings were rejected. |
| Kentucky in 4 × 50 min | **Not measured; probably not met on a cold cache.** NAIP takes 30–90 s per tile, and Clifty alone needs 84 tiles (~60+ min). `--resume` and the cache make later runs fast: run C re-read 45 cells in 2.4 min. |
| Labels, notice, chips, report, exit codes, robots, rate limit, never-use sources | Tested in the selftest. Rate limit and robots were also seen live. |

## 4. Open issues

- **New source to approve:** FEMA USA Structures is not named in the spec. It is government data hosted on ArcGIS Online and is not on the never-use list. If it is not allowed, delete the `fetch_structures` call; the tool then falls back to the photo roof test, which is weak on real roofs.
- **Speed:** NAIP exportImage is slow (30–90 s). A full Kentucky first pass needs several resumed runs.
- **Set-back lots:** lots reached by a drive are missed unless TIGER has an S1780 lot road. A possible extension is to follow a grey drive up to ~40 m.
- **Missing TIGER flags:** TIGER has no closed, seasonal or divided-highway flags.
- **Picture maps:** they are not georeferenced, so P symbols count only when `p_points` are given.
- **Unknown access format:** the `data/access` format is unknown, so a tolerant reader is used (refs need 3–6 digits, like US-1234).
- **Thresholds:** they are tuned on one Kentucky area in late-summer 2022 NAIP and need checking on the 6 example parks and the chat-11 sample.

## 5. Selftest output (final run)

```
ok   --max-minutes 0: exit 3, work left (got 3)
ok   --resume: finishes with exit 0 (got 0)
ok   parks in pulloffs/US-KY.json ['US-9001', 'US-9003'] (no outline / robots-blocked / other area = nothing)
ok   US-9001: 2 candidate(s), expected 2
ok   US-9001: L1: gravel lot inside the park on Test Hwy 715 is found
ok      inside=True dist_out_m=0 (expected True, 0)
ok      score 1.0 (expected 1.0)
ok      road Test Hwy 715 S1200
ok      photo_year 2024
ok      why has "Possible pull-off (seen on an aerial photo, not official). Inside the park's official boundary."
ok      why has 'S1780'
ok   US-9001: L2: gravel lot ~75 m outside on Ridge Rd is found, labelled outside
ok      inside=False dist_out_m=75 (expected False, 75)
ok      score 1.0 (expected 1.0)
ok      road Ridge Rd S1400
ok      photo_year 2024
ok      why has "Possible pull-off (seen on an aerial photo, not official). Just outside the park's boundary: walk in to activate."
ok      why has 'About 80 m outside the boundary.'
ok      why has 'P (parking) symbol on the agency picture map'
ok   US-9003: 1 candidate(s), expected 1
ok   US-9003: L5: lot ~320 m outside a park with no access points (ruling G-P2) is found, photo marked old
ok      inside=False dist_out_m=319 (expected False, 319)
ok      score 0.9 (expected 0.9)
ok      road Lonely Rd S1400
ok      photo_year 2019
ok      why has "Just outside the park's boundary: walk in to activate."
ok      why has 'About 320 m outside the boundary.'
ok      why has 'photo is old (2019)'
ok   every row has source_url, read_date (YYYY-MM-DD) and why
ok   never says 'parking' without 'possible'
ok   chip chips/US-9001_01.jpg: JPEG (400, 246), red patch 412 px, white road 4943 px, yellow park line 730 px
ok   chip chips/US-9001_02.jpg: JPEG (319, 400), red patch 151 px, white road 5778 px, yellow park line 957 px
ok   chip chips/US-9003_01.jpg: JPEG (400, 400), red patch 873 px, white road 11191 px, yellow park line 0 px
ok   kept out (log only): 'plain road shoulder or strip about 5 m wide'
ok   kept out (log only): 'too small: about 144 m²'
ok   kept out (log only): 'touches only an interstate, ramp, alley or private road'
ok   kept out (log only): 'large bare brown ground'
ok   kept out (log only): 'below the cut (0.45 < 0.5)'
ok   kept out (log only): 'duplicate: an official access point is 0 m away'
ok   kept out (log only): 'next to buildings outside the park: a house, farm or business lot'
ok   kept out (log only): '(building outline from FEMA USA Structures)'
ok   review.md carries the SHORT information notice
ok   review.md is best first [1.0, 1.0, 0.9]
ok   report.md recall line: 'inside the search band: 2; found within 50 m: 1 (50%)'
ok   robots.txt Disallow obeyed (no request to the blocked path) and reported
ok   only TIGERweb, NAIP, FEMA USA Structures and the agency host were asked
ok   nothing written outside --out / --cache
ok   429: 3 retries, then host resting (host busy.example.gov answered 429 after 3 retries; resting this run)
ok   a resting host is not asked again this run
ok   never-use guard refuses a banned host; a government file on cloud storage is allowed
ok   own code: banned source names appear only in the guard list (other lines: [])
ok   access reader: rows keyed by ref and GeoJSON points
PASS
```


## RULED
- FEMA USA Structures building outlines: KEEP (Brandon Oct 31 2026 9:09 PM CT, "yes if it is more accurate"). In the live test it removed house and yard false spots.
