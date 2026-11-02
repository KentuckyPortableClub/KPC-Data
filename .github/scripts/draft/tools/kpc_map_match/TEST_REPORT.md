# kpc_map_match (T1): test report

Run on 2026-10-31 (America/Chicago) on the shared Linux box with Python 3.12 and the pinned requirements.txt.
The answered rows come from KPC-Data `data/waiting/questions/layers.json` (chat 11's YES/NO, read only).
Every number below comes from those runs. The band rules are the spec's, word for word.

## Self test (offline)
`python kpc_map_match.py --selftest` prints **PASS** (17 ok lines, 0 FAIL). It runs on `tests/fake_layer.json`
with 5 K4TEST rows (STRONG, pin-outside CONFLICT, ×124 size CONFLICT, partial-name WEAK, better-record-nearby
CONFLICT). It also checks:
- the name rules: type words dropped, half a name is not enough, "Lake" alone is not a match;
- the banned sources (Overpass, Google My Maps, Wikipedia, Protected Planet), while a government file on cloud
  storage is allowed;
- the robots.txt longest-match rule;
- reading acres from a park page;
- that a write outside --out is refused.

## Test: 20 answered rows (10 YES, 10 NO), `tests/live20_keys.txt`
| band | YES | NO |
|---|---|---|
| STRONG | 9 | **0** |
| WEAK | 1 | 10 |
| CONFLICT | **0** | 0 |

**STRONG has no NO and CONFLICT has no YES: passed.** CONFLICT is empty on this set, though. Five of the NO rows
are Queensland road/firebreak records: the name is capped at 0.6, so they land in WEAK, not CONFLICT.
The result was the same before and after the name-rule change below (`runs/t1_live20`, `runs/t1_live20_v2`).

## Acceptance: 200 answered rows, `tests/acceptance200_keys.txt`
The set has 145 YES and 55 NO. None of them are in the 20-row set. 172 come from the half of layers.json that was
held out while the rules were built; the rest are rows with no record id that are matched by record name.

**Run 1** (`runs/t1_acc200`, the rules as built):

| band | YES | NO |
|---|---|---|
| STRONG (121) | 119 | 2 |
| WEAK (71) | 23 | 48 |
| CONFLICT (8) | 3 | 5 |

- STRONG agrees with YES: 119/121 = **98.3%** (target ≥97%): met.
- CONFLICT agrees with NO: 5/8 = **62.5%** (target ≥95%): **not met.**

The two NO rows in STRONG were "First Landing National Recreation Trail" matched to the record "First Landing State
Park" (trails were exempt from the designation check) and "Columbia River Gorge National Forest" matched to "…
National Scenic Area" ("scenic area" had no designation family). I made one rule change after seeing this run,
and it follows the club's own rule (same name **and** same kind of place):
- added a "scenic area" designation family;
- a trail park vs a non-trail record now counts as a different kind of place.

I then re-ran the same 200 rows (mostly from cache, 38 requests).

**Run 2** (`runs/t1_acc200_v2`, the shipped code):

| band | YES | NO |
|---|---|---|
| STRONG (119) | 119 | **0** |
| WEAK (72) | 23 | 49 |
| CONFLICT (9) | 3 | 6 |

- STRONG agrees with YES: 119/119 = **100%**: met. Note that this rule was tuned after seeing run 1 on this set,
  so run 1's 98.3% is the fairer held-out number.
- CONFLICT agrees with NO: 6/9 = **66.7%**: **not met.** The three YES rows in CONFLICT are:
  - GB-0729 Thames Path and GB-0766 Hadrian's Wall Path: the POTA pin is 57 km and 83 km from the official
    line. A long national trail's pin is a single point, often nowhere near the line.
  - CR-0025 Parque Metropolitano La Sabana: the pin is 822 m outside the record.

  The spec says "the pin is outside = CONFLICT", so the tool follows it. A possible rule change for chat 10: a
  pin far from a LINE record with a full name match → WEAK. On this set that would give 6/7 = 86%, which is still
  under 95%, so I did not add it. The CONFLICT sample is also small (8–9 rows), and 49 of the 55 NO rows land in
  WEAK, not CONFLICT.

Bands overall: 60% STRONG (119), 36% WEAK (72), 4.5% CONFLICT (9).

## Speed and politeness
Run 1 was started cold, interrupted twice, and finished with `--resume`. The last part did 185 rows in 17.7 min
using 612 requests in total. Two hosts went "resting" after 3 retries:
- www.nrtdatabase.org (HTTP 522; the National Recreation Trails layer), so its rows could not be scored on the
  pin or the neighbours and stay WEAK;
- www.fs.usda.gov (HTTP 500).

The 200-row runs used `--no-pictures`, because pictures don't change the band. The 20-row run made pictures: 1
side-by-side JPEG (1600×830, 176 KB), because only 1 of those 20 parks has a picture-maps entry.

## Known gaps / not tested
- **CONFLICT ≥95% is not met** (see above).
- **IoU (step 6) has not been tested live.** There are no georeferenced agency outlines (GeoPDF / world file) in
  the club data to feed `--agency-outlines`. That code path has not been run by any test.
- Acres from the park page: only 11 of the 200 rows got a page acreage, so the size test rarely fires.
- Satellite imagery for the pictures is USGS National Map imagery (US only). Outside the US, the picture shows the
  outline on a plain background.
- Rows whose layer host is down (resting) stay WEAK, and `why` says "could not be checked".
