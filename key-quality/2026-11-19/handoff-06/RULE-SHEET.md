# Hand-off 06 RULE SHEET: the seven owner answers for 2-fers (R-2F1 to R-2F7)

Written by the club's reviewer (Fable), 19 Nov 2026, from the owner's own words. Rules first: nothing below is yours to
change, add to or soften. A case this sheet does not cover = stop, write it in your notes as a numbered grey area, build
nothing for it.

## R-2F0. The principle every rule answers to

The owner, 19 Nov 2026 3:42 PM (his words, as typed):

> "Pota 2fer rules ...paraphrased 2 or more overlapping parks most be public lands and you and all of your equipment
> most be in it.... a trail on a river has 100' both sides of edge of the water...a trail 100' both sides of trail is
> boundaries....wilder river have offical gis boundaries fyi....pota gives no size requirement other then you and all the
> equipment most be in it and public land....so basically any 2 parks with a pota park number where they and overlap
> greater then a few feet is a 2fer....we need to be a touch stricter to account for map errors being off a little"

And 17 Nov 4:04 PM: "We need not make up rules: we made little stricter rules to help from having map errors, but we
dont add rules to POTA."

So:

- Official boundaries that overlap are a 2-fer. The bot never guesses an owner and never asks whether a park "should"
  be a park (rulings of 17 Nov 11:14 to 11:47 AM, already in the code).
- The ONLY reasons the club is stricter than POTA are map error and measuring error. Every number in the 2-fer code must
  be one of: POTA's own (100 ft), the owner's (25 yards, 50 yards, 100 yards, the 25 m stretch), or the measuring tool's
  own error (a grid cell, a shape's stated detail). **You add no new number.** If you think one is needed, it is a grey
  area for the owner.
- The 25-yard floor, the "very tight" list (25 to 50 yards) and the "small overlap" label (50 to 100 yards) stay exactly
  as they are (ruling N4, 16 Nov: "we are little stricter to account for map errors").
- A 2-fer file says only what the club believes IS an overlap. No row ever says a pair is NOT a 2-fer (15 Nov).

---

## R-2F1. An outline from a summary map gives an APPROXIMATE 2-fer (question 1)

**Ruling:** the owner, 19 Nov 2026 about 3:35 PM, picked "Yes, approximate".

1. **What counts:** a US park whose EVERY joined record comes from a layer that is not the managing agency's own land:
   a layer labelled `compilation`, `register` or `water` in `data/state-gis.json`, a Michigan project line (`mid`), the
   Mississippi general-area file (`mszp`). This is `summary_only()` as merged in #269. A pair with such a park is an
   approximate 2-fer with the note already in the code (`SUMMARY_NOTE`), until the agency's own map is found.
2. **What does not:** a park with at least one record of its agency's own land. A park that is a designation line only
   (that is the "may contain private land" note of 17 Nov, a different rule, already on).
3. **Sources:** the layer labels of `data/state-gis.json` (ruling D11). Never a name guess.
4. **Unsure:** a record whose layer has no label = not a summary map (today's behaviour); list such layers in your notes.
5. **What people see:** the approximate tier as it exists (drawn as approximate, the note). No new wording.
6. **Check and report:** a park the KEY already grades `approximate` (key rule D7: a state layer's copy of a federal
   unit) must also give an approximate 2-fer. Say in your notes which line makes that so today (look at how
   `decide()` builds `_apx`), with a test. If it is not so, that is a bug to fix in this part.
7. **Examples:** the 17 Nov count was 74 parks. The key was rebuilt on 19 Nov, so recount on main's key files and put
   the park list (number, name, the layer kind) in your notes. Do not reuse the old test's example US-4502 as "summary
   only" in new tests with its real name: Flathead National Forest got its Forest Service record on 19 Nov.

## R-2F2. A park beside a national forest is NOT held back (question 2)

**Ruling:** the owner, 17 Nov 2026 4:04 PM (recorded by HQ): overlapping official lines are a 2-fer; "we dont add rules
to POTA". Repeated 19 Nov 3:42 PM (R-2F0).

- Remove the setting `KPC_FERS_FED_NEIGHBOUR`, `fed_neighbours()`, `FED_LAND`, `FED_FOREST` and the NOT SURE text that
  goes with them. A rule the owner turned down does not stay in the code behind a switch someone could flip.
- Test: two made-up overlapping parks named "Grand Canyon National Park" and "Kaibab National Forest" are decided like
  any other pair.

## R-2F3. Near a size line the grid cannot tell: NOT SURE (question 3)

**Ruling:** N3, the owner 16 Nov ("I agree with fine lines for 2fers": a pair near a threshold on anything but the fine
level is NOT SURE), kept on 17 Nov 4:04 PM with the band at the grid's own step.

1. **What counts:** an AREA row whose measured width is within ONE GRID CELL of the 25-yard line (22.86 m) or the
   50-yard line (45.72 m), on the grid it was measured on. Pass 3's cell is 5 m, so today the band is 5 m.
2. **What does not:** line rows (trails, rivers). Any row measured wider than one cell from both lines. The 100-yard
   line (it only changes a label between two shown lists).
3. **The number is not made up:** the band is the tool's own error and is read from `CELL`, never typed as a number.
   HQ's lean in the code and its test was 8 m; that goes. Measured by the reviewer on 19 Nov with the real grid
   (`known-answers/grid-readings.csv`, 43 widths x 16 placements): every too-narrow overlap the grid lets past the floor
   (true 16 to 22 m) reads 23 to 27 m; a true 42 to 45 m reads up to 49 m; a true 46 to 49 m reads as low as 45 m. One
   cell catches every one of them, at both lines.
4. **Unsure:** that is the rule. Status `not sure: near a size line ...` with the plain reason already in `near_line()`.
5. **What people see:** NOT SURE rows are kept out of the shown lists, as today.
6. **Known answers:** on the saved 472-row file (`tests/fixtures/fers-wl3-near-line-rows.csv`), leaving out water-only
   rows: 226 of 226 rows at the 25-yard line and 154 of 159 at the 50-yard line are NOT SURE with a 5 m band (380 rows).
7. **Do not** widen the band to make a test pass, and do not move the 25-yard floor.

Part 4 of the hand-off asks you for a PROPOSAL (no code) on measuring such a spot finer, so fewer rows end up NOT SURE.

## R-2F4. Only rows the new system made are copied forward (question 4)

**Ruling:** the owner, 19 Nov 2026 about 3:36 PM: "Need yo be from the new better system we are building now...old efee
data is not trustworthy pre rebuild....after rebuild i trust this system more sp yeah maybe?" Then, asked whether the
rule is the two lines below: "Yes, that's it".

1. **What counts as a row that may be copied forward** (every "keep the old row" path: a pair skipped for time or
   crashed in pass 1, a small-batch run, a withheld park's rows, the store's keep-the-old-row and partial-boundary
   rows, a row put back because an input went missing):
   - (a) it carries a stamp saying what it was made on (below); AND
   - (b) for BOTH of its parks, that stamp still matches today: the park's key entry and the outline it was measured
     from are unchanged.
2. **What does not:** a row with no stamp. Every row that exists today has none, so no row made before this rule is
   ever copied forward: the new system measures the pair again. A stamped row where either park changed.
3. **The stamp** (field `made_on` on every row the bot decides, always, not only while a setting is on): per park, a
   short fingerprint of (i) the park's key entry as the 2-fer loader reads it (its joined records and their rows, its
   grade, its line record for a line park) and (ii) the outline it was measured from (store run: the store index's own
   checksums of the park's records; other runs: the same outline hash `pair_fp` uses). For a park this run did NOT
   read (a withheld park) it must be checkable without reading the outline. Find out what the store index holds for
   such a park (the private store, and the public shelf) and say it in your notes: where its outline cannot be
   fingerprinted at all, its stamp checks the key entry only, and your notes say so. The stamp must NOT hold a date, a
   run id, a count, a check row or anything that changes while the park's land does not.
4. **The defect you are replacing:** `kpc_fers_age.py` compares a row with the WHOLE key's `build` and `built` in
   `data/us-key/index.json`. That is the id of the last key RUN, new on every run. Main's index on 19 Nov:
   `build US-44600381160`, `built 2026-11-19 20:25 UTC`, 39 areas reused, **0 rebuilt**. With the setting on as built,
   every copied row would be thrown away after any key run, twice a day, whether or not a single park changed.
5. **Unsure / fail closed:** a key file or store index that cannot be read, or a park missing from it = not copied,
   with that reason.
6. **What people see:** nothing new on a row. A row that is not copied is simply not in the file (never "not a 2-fer").
   Every row not copied is listed for a person in the private folder with its plain reason, and counted in the report.
7. **Also report, change nothing:** the bot does not touch the file of an area it does not run. The run report lists
   the areas of this run's region whose public file was made before this rule (count and area codes), so the club
   knows what is still old-system data.
8. **Tests (made-up parks):** a key run id that changes while nothing was rebuilt: the stamped row is still copied. One
   park's key entry changes: that pair's row is not copied, another pair of the same area still is. An unstamped row is
   never copied, by every path. A store checksum of one record changes: not copied. Unreadable key file: not copied,
   reason given.

## R-2F5. A separate overlap piece is its own spot (question 5)

**Ruling:** the owner, 17 Nov 2026 4:04 PM (recorded by HQ): the 100 m distance is OUT (made up). "A separate overlap
piece that passes the 25-yard test is its own spot; a piece joined to a listed spot is that spot."

1. **What counts:** in a store run, a spot a finer grid finds that no row of its pair took, when it (a) passes the same
   size test every row passes (an area spot at least 25 yards across; a line stretch by the stretch rule as it is) and
   (b) is a SEPARATE piece: it does not touch or overlap any listed spot of the same pair.
2. **What does not:** a piece that touches or overlaps a listed spot (it is that spot: listed in the private folder
   only, as today). A piece under 25 yards across.
3. **No distance:** `FINE_GAP_M` and `KPC_FERS_FINE_100M` are removed. "Joined" means the two patches are connected on
   the ground as measured, nothing else. Say in your notes exactly how you test that from what rows carry.
4. **Unsure:** a listed row with nothing to test connection against (no shape, no box) = the new piece is NOT made a
   row; it is listed in the private folder with that reason. Silent beats wrong.
5. **What people see:** a row like any other (pass 3 decides it), with the mark `fine_only` it has today.
6. **Tests (rows with shapes):** two patches of one pair 1 km apart, both 30 m across: two rows. A 30 m patch 44 m
   from a listed spot and not touching it: its own row (under the old 100 m rule it was not: that check in the Handoff 9
   test flips). A patch touching a listed spot: no new row. A 15 m patch: never a row. A listed row with no shape: no
   new row, listed with the reason.
7. The 17 Nov review counted 20,749 passing spots that were found and not counted. That number is the review's; it was
   not re-measured. Do not test against it.

## R-2F6. A park whose boundary cannot be shown: no drawing, the owner's words (question 6)

**Ruling:** the owner, 19 Nov 2026 about 3:36 PM: "Say we are missing this boundary possible 2fer check for offical
missing boundary or something like thay". Asked what happens to the old rows of such parks: "Drop until re-checked".

1. **What counts:** a row copied forward (so: stamped, R-2F4) that names a park the run withheld. The drawn pieces of
   the overlap (`shape`, `lines`) leave the public row. The row keeps the two parks, the kind, the status, the centre
   point and the size, and carries this note, word for word:
   **"Possible 2-fer. We are missing an official boundary here: check both official boundary maps before you count it."**
2. **What does not:** an unstamped (old-system) row of a withheld park. It is dropped like every other old row
   (R-2F4). Nothing replaces it.
3. **Privacy is not yours to redesign.** The write guard, the redaction, the private log and the exit-89 refusals stay
   exactly as they are. The only change is the one #269 built behind `KPC_FERS_STRIP_HELD` (now on) and the note text.
   Your test reads the written public file and proves it holds no coordinate list from the withheld park's row.
4. **Unsure:** anything about a withheld park that this sheet does not say = nothing is written about it.
5. The club's two public notices are not touched. The row never says the parks DO overlap.

## R-2F7. The paperwork, and the thin-shelf fallback goes (question 7)

**Ruling:** the owner, 19 Nov 2026 about 3:41 PM: "D10 yes ...shelf i trust the new shelf more theb the old system".

- **D10:** scope entry `2026-11-17-d10-tripwire-not-sure` gets
  `"approved": "APPROVED, decided_by KPC owner, 2026-11-19 (\"D10 yes\"; ruling D10, 17 Nov 2026)"`. Nothing else in
  that entry changes and no code changes.
- **Thin shelf:** NOT approved as written. The rule left an area on the OLD 2-fer path, with its old files, when under
  90% of its parks were on the public shelf. The owner trusts the new shelf more than the old system, and with R-2F4
  the reason the floor existed is gone (a thin area can no longer carry rows unchecked: nothing unchecked is copied).
  So: the 0.90 floor (`THIN_SHELF`) goes; a store run reads every area the shelf holds, however thin; a park the shelf
  does not hold is not tested and is counted, as today. Entry `2026-11-17-thin-shelf` is not deleted: it gets
  `"approved": "NOT APPROVED: replaced by <your new entry id> (KPC owner, 2026-11-19: \"shelf i trust the new shelf more theb the old system\")"`.
- **What people see:** the shelf's index carries each area's coverage block (`parks_in_store`, `parks_on_shelf`,
  `share`). The run report gets one plain line for EVERY store area, counts only: "<area>: <n> of <m> parks on the
  shelf; 2-fers are measured only between those." No floor, no percentage rule.
- **Unsure:** an area the store does not hold at all, or whose index is stale or damaged, is left out of a store run
  with its reason, exactly as today. That is not the thin-shelf rule and it stays.
