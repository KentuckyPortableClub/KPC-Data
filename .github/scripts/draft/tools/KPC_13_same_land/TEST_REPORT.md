# KPC 13 Same-land finder: test report

Tested 2026-10-31 on the box: Python 3.13.5, shapely 2.2.0, pyproj 3.8.0, rapidfuzz 3.14.6, pytest 9.2.0.
Club files were read from a read-only copy of `sample-data/`. All output went to a scratch folder. No key, outline or
2-fer was edited, and nothing was pushed or posted.

## 1. Offline unit tests (made-up shapes, pretend ArcGIS server): 17 passed, 0 failed

    python -m pytest -q tests      ->  17 passed in 0.23s

| test | what it proves |
|---|---|
| test_s1_same_record | S1: SAME RECORD, SHARES A RECORD, or nothing |
| test_s2_shape_classes | S2: SAME SHAPE (95 % / 80 %), ONE INSIDE THE OTHER, SMALL ONE INSIDE, PART OVERLAP |
| test_s3_name_family | S3: type words and initials dropped, token-set >= 85, or one name inside the other |
| test_s4_pins | S4: pins within 200 m |
| test_s5_agency | S5: same / different / unknown, including vague codes treated as unknown |
| test_decide_rules | every verdict rule, plus the CHECK cap when an outline is not official |
| test_whole_run | a full run on made-up parks: pairs, verdicts, 2-fer rows, questions.json, summary.md |
| test_answers_are_kept | filled-in answers in questions.json survive a re-run |
| test_source_down_uses_nothing_and_says_so | a dead layer falls back to the saved outline and the row says so |
| test_exit_codes | 0 / 2 / 3 and --resume |
| polite tests (7) | User-Agent, 1 request per second per server, back-off, robots.txt, offline, moved layer, tract piece |

## 2. Real data: US-KY, US-TN, CA-ON, CH (live official layers; CH from world-bounds)

Run 1: `python kpc_same_land.py --data sample-data --out sameland --cache cache --areas US-KY,US-TN,CA-ON,CH`
took 12 min 35 s from an empty cache and exited 0.

| area | parks with outline | overlapping pairs | SAME LAND: likely | CHECK | NOT SAME |
|---|---|---|---|---|---|
| US-KY | 187 | 53 | 2 | 1 | 50 |
| US-TN | 257 | 88 | 4 | 13 | 71 |
| CA-ON | 815 | 138 | 12 | 12 | 114 |
| CH | 189 | 59 | 25 | 0 | 34 |

69 questions were written to questions.json. The output folder is 452 KB.

Checks against what we already know:
- **KY**: both club "same land" rows come out SAME LAND: likely. These are US-0703 Fort Donelson + US-3790 Fort
  Heiman (same NPS record; the Fort Heiman tract piece is noted) and US-10139 + US-4526 Jefferson NF. **Carter Caves
  (US-1276)** against Bat Cave SNP (US-12971) and Cascade Caverns SNP (US-12972) is **NOT SAME** (small one inside /
  part overlap), as it should be. One new CHECK: Bad Branch Wild and Scenic River / Bad Branch SNP (same name family,
  pins within 200 m, only part overlap).
- **TN**: of the 52 club "same land" rows (many repeat the same pair), the tool says SAME LAND or CHECK for 49.
  The 3 that disagree:
  - US-2937 + US-7580 and US-2937 + US-7581 (both rows not live): the outlines do not overlap at all.
  - US-3969 Wolf River WMA + US-6245 Ghost River SNA (live): **NOT SAME**. Ghost River is 2,263 acres, 96 % of it is
    inside Wolf River's 17,513 acres, the names differ, and the pins are 7 km apart. Worth a human look.
- **ON**: no club same-land rows in this area. Top finds: Blair Township NR / Blair Township WA, Crane Lake(s) CR,
  Mississippi Lake NWA / MBS, McCrae Lake, Basswood Lake, and Bonnechere PP / Bonnechere River PP. 117 parks were left
  out because they have no outline source (the Ontario conservation-authority parks, the same ones KPC 11 cannot check).
- **CH**: 25 SAME LAND, but 23 of them have POTA pins more than 5 km apart. Several CH park numbers are drawn with the
  same whole BLN outline in world-bounds (Vierwaldstättersee, Säntisgebiet, Speer–Churfirsten–Alvier, Berner
  Hochalpen), so the outlines are identical even though the parks are surely parts of it. **This is a finding about
  world-bounds, not same land.** Treat CH results as "the outline file needs better pieces".

Run 2 (warm cache):
- `--max-minutes 1` stopped after KY and TN with exit 3 (41 s).
- `--resume` printed "Carrying on ... (2/4 areas done)", did ON and CH only, and exited 0 (50 s). The counts were the
  same as run 1.
- A YES answer written into questions.json by hand (checked_by K4TEST) was still there after the re-run.

## 3. Bugs found by the real-data runs and fixed
- Record numbers were missing from the server answers (see KPC 11). Fixed in the shared code.
- PAD-US manager codes (SFW, SDC, SPR, OTHS, UNKL, JNT, ...) did not match agency names. They are now mapped to plain
  agency families, and vague codes count as unknown.
- The summary repeated "same land" up to 21 times for one pair. It now says "same land x21".
- An area with no club same-land rows now says "none in this area".

## 4. Not tested
- The fallback to the saved canada-bounds outline when a live layer is down (only simulated; every live layer
  answered).
- Areas other than US-KY, US-TN, CA-ON and CH, and other world countries.
- Windows/macOS. Only tested on Linux.
- Other agents on the box were reading some of the same servers during the run. Each tool paces itself to 1
  request per second per server, but they cannot pace each other.
