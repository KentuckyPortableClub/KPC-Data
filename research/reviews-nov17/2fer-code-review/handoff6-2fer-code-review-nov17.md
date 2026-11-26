# Handoff 6 — 2-fer code review (solo, read-only)

**For:** Brandon (KZ4CP), KPC  **Date:** Tue Nov 17, 2026 (CT)
**Code reviewed:** KPC-Links main at 58545e0d (Nov 17, 11:44 AM CT; includes 712558ab). Old 2-fer files in KPC-Data (main bae08a0d) were used only as examples of what the code made.
**How:** read the code, ran the real `area_spots` measuring step offline on made-up squares, and counted from the key files and the old 2-fer files. No pushes, PRs, Actions runs or comments. No web calls. KPC-Store not touched.

**Read me first:**
- The handoff file named in my brief (attachment 924110…txt) was **not on the box**. My brief listed its 9 topics, so I reviewed against those. If the handoff had extra asks, I missed them.
- Wording: every pair below is a pair whose boundaries **may** overlap in our files. I never say two parks do overlap. Old rows are what the old code made on an older key. They're examples, not proof the new code makes the same row.

---

## The short version (top 3)

1. **"Official" is trusted too far, so neighbours that only touch can still show up.** The bot treats any outline graded "official" as public land, but some of those outlines come from summary maps (compilation copies), historic-register shapes, Michigan project lines or lake-surface layers. 74 US parks get their whole outline from one of these. The old files also show 33 rows where a national park or refuge and the national forest next door show up as possible 2-fers with hundreds of acres where the boundaries may overlap, for example Grand Canyon NP × Kaibab NF (281 ac) and Olympic NP × Olympic NF (1,029 ac). Every check passes them. The row even notes the two different federal owners, but only as information.
2. **The measuring grid is coarser than the rule, and nothing is marked "not sure" near the size lines.** The final pass measures on 5 m squares. In my test on made-up squares, overlaps only 16–20 m wide passed the 25-yard (22.9 m) floor, and a true 46 m overlap came out as 45 m, which drops it to "very tight". Your Nov 16 ruling (N3) says a pair near a line should be NOT SURE. The code never does that. 472 rows in the old files sit within about 5 m of a line.
3. **Some failures end quietly and can still show a pair.** If one pair crashes, it just disappears and the run stays green. If the US water/closed-area check crashes, the row becomes a **candidate** (Canada makes it "not sure"). If the closed-area map doesn't answer, the bot acts as if nothing is closed. Up to 20 parks (or 20% of an area) can fail to load while the area still counts as finished, and their pairs vanish.

---
## 1. Weak links, worst first

Each one says what breaks, a real example, how many it could touch, how sure I am, and how to check it. CSVs are in `handoff6-csv/`.

### WL1. "Official" outlines that aren't really land are taken as public land (wrong 2-fers that pass every check)
**What breaks:** When the key grades a park "official", the 2-fer bot treats its outline as government land. `official_agency_outlines()` turns a blank owner into "public land (official agency outline)" (kpc_fers.py ~3448–3500, used in `ownership_step()` ~1890). The grade itself only means a record was matched (`kpc_fers_key_status._status_of`). It says nothing about whether the layer draws land. The Nov 17 "may contain private land" note only covers the layer prefixes in `DESIG_PRE` plus state layers labelled `designation`, and only when *every* record of every land half is one of those. These kinds of layer get no note and no hold:
- **compilation** layers in data/state-gis.json (other agencies' land re-drawn by a state: Montana "Managed Areas", WA "Non-DNR Major Public Lands", VA conservation lands, NH GRANIT, TX, ME…),
- **register** layers (National Register of Historic Places polygons, Utah NHL, VA historic resources). These are historic-district lines, not ownership,
- **water** layers (lake/reservoir surfaces: AR, ID, WA Ecology NHD waterbodies),
- **Michigan DNR project boundaries** (`mid`, an outer project line) and the **Mississippi zip** (`mszp`, whose own label says "general area, not a legal description").

**Real examples (key files on main):** US-4502 Flathead National Forest. Its *only* record is `sgmtd744`, a 2.65-million-acre shape from Montana's "Managed Areas" compilation layer. In the old files it pairs with US-8004 Swan River NWR (15.4 ac, 59 m wide, "candidate") and with US-0028 Glacier NP. US-6823 William G. Milliken State Harbor uses only a Michigan project line. It pairs with US-1522 Milliken State Park and US-13184 Iron Belle State Trail. US-7974 Harmony Hall uses only an NRHP polygon and has 3 shown pairs. US-11579 Dworshak Reservoir State Fishing Lake uses only a reservoir-surface layer.
**How many:** 74 US parks get their **whole** outline from these layers (17 register, 38 compilation, 7 water, 7 Michigan project, 2 Mississippi zip, plus mixes). 13 of them appear in 25 shown rows of the old/held files. Many more parks have at least one such record mixed in. I didn't count those.
**How sure:** Sure about the mechanism (code + key files). Medium on how many rows are actually wrong.
**Check it:** `WL1-official-but-not-land-outlines.csv`. Open data/us-key/US-MT.json → US-4502 → `m`. Open data/state-gis.json → the `what` field of each layer.

### WL2. Neighbouring federal units of different agencies pass as 2-fers (side-by-side land read as overlap)
**What breaks:** A national park and the national forest next to it, or a refuge and a forest, are normally side by side: each acre belongs to one agency. When their two maps disagree along the shared line, or one outline is really an outer line, the overlap patch can be hundreds of acres. The bot passes it. The row records `mixed_owners: FED:NPS + FED:USFS`, but owners are info only (N1). Nothing asks "two different federal landowners claim the same ground: is one of these an outer line or a map disagreement?"
**Real examples (old public files, Oct 29 key):** US-0030+US-4430 Grand Canyon NP / Kaibab NF, 281 ac, 141 m wide. US-0056+US-4532 Olympic NP / Olympic NF, 1,029 ac, 1,835 m. US-0028+US-4502 Glacier NP / Flathead NF, 140 ac, 547 m at N Fork Rd. US-0055+US-4530 North Cascades NP / Mt Baker-Snoqualmie NF, 598 ac. US-0046+US-4464 Kings Canyon NP / Sequoia NF, 274 ac. One is still in the Nov 14 waiting room: US-0067+US-4491 Voyageurs NP / Superior NF, 10.7 ac.
**How many:** 33 shown rows where a National Park or Refuge pairs with a National Forest (`WL2b-…csv`). 82 shown area rows carry two different federal owners in total (`WL2-…csv`). Some of the 82 are probably real layering (Yosemite NP × Merced Wild & Scenic River; Chincoteague NWR inside Assateague NS) and should stay.
**How sure:** Sure these pass every check today. These rows **may** be map edges, not shared ground, but only a look at the official maps can say. The rows were made on the old key, and I didn't rerun them on the new key.
**Check it:** The CSVs above. Open data/fers/US-AZ.json.gz in KPC-Data, find id `US-0030+US-4430@area…`, and compare its `shape` to the NPS and USFS boundary maps.

### WL3. The final measuring grid is coarser than the size rule, and there's no "not sure" band
**What breaks:** Pass 3 paints both outlines onto 5 m squares and shrinks the overlap (kpc_fers.py `area_spots` ~2167; `CELL=5`, `TIGHT_SHRINK=11.43`). Painting fills every square an edge touches, so each outline grows by up to one square. The width is then rounded to the grid. In my offline test of the real function on two made-up squares (overlap widths 0–50 m, 3 angles, 3 shifts against the grid):
- overlaps of **16 m, 18 m and 20 m passed** the 25-yard (22.86 m) floor at some alignments and were reported as 25 m wide ("very tight"). 0–14 m never passed (good, so touching parks are safe);
- a **true 46 m** overlap was reported as **45 m**, which drops it below the 50-yard line (45.72 m) into "very tight". A true 30 m one was reported as 35 m.

The outlines themselves may be simplified by up to 3 m (R-G6), which adds to this. Your N3 ruling says a pair near a line, on anything but the fine level, is NOT SURE. The code has no such band: it always answers yes or no.
**How many:** 472 rows in the old/held files have a measured width within about 5 m of a size line: 230 near the 25-yard floor, 188 near the 50-yard line, 54 near the 100-yard line (`WL3-rows-within-5m-of-a-size-line.csv`).
**How sure:** Sure. The test is repeatable (`WL3-grid-test-script.py`, results in `WL3-grid-test-made-up-squares.csv`).

### WL4. Failures that end quietly, and one that turns a failure into a "yes"
**What breaks:**
- **US water/closed check crash = candidate.** `decide()` (~3783): `try: lc = land_check(s, G) except Exception: lc = 'ok'`. A crash in the water or closed-area check lets a US row go on to "candidate". The Canada branch right below uses `'not checked'` → NOT SURE. Same kind of failure, opposite answers.
- **Closed-area map down = "nothing is closed".** `land_check()` (~3407): if the PAD-US closed-area query fails, it uses an empty "closed" picture and carries on. Rule 10 is silently skipped on a non-store run. (Store runs do mark it, via `closed_status`.)
- **A pair that crashes just disappears.** `find_spots()` (~2650): any error in the pair test is one log line. The pair counts as tested, no row is made (not even NOT SURE), its old row isn't kept, and the area is saved as finished. The run stays green, and the problem shows only as a notice (first 40 lines kept).
- **Parks whose outline couldn't be read.** The area only stops when **more than 20 parks and more than 20%** fail (~4553). Below that, those parks make no pairs, their old rows go, and the area is saved as finished. The missing check lists them as "never looked at" but "never fails". Pairs skipped for **time** are carried over. Pairs skipped for a **failed read** aren't.
**How many:** Can't count from the files: crashes leave nothing behind. The run report's `problems` field (first 40 lines) is the only trace.
**How sure:** Sure (code reading). I didn't make it crash on purpose.
**Check it:** Make `land_check` raise in a test and see a "candidate". Make `area_spots` raise for one pair and see the run end 0 with the pair gone.

### WL5. Old rows can come back forever, with no age or key check (stale input reused)
**What breaks:** Several "keep the old row" paths copy rows from the *previous public file* unchanged: `carry_held_rows` (a withheld park's rows), `keep_old_rows` (R11: "kept: not checked in a store run"), `carry_rows` partial-view rows, pass-1 time-skipped pairs, and whole areas kept when a pass stops for time or "measured nothing". None of them asks how old the row is or which key built it. The spot files carry only pass dates, with no key, rules or code stamp at the top. `OLD-KEY-QUARANTINE.json` (Oct 29) says those rows must not be used as answers, but no code reads it. It also says reuse is by a code fingerprint, which stopped being true on Nov 9 (see WL6). D10's tripwire hold also skips these kept/carried rows on purpose (`hold_tripwire` → `this_runs_verdict`), so a tripwire park's old row can keep showing.
**Real example:** 42 US/Canada public 2-fer files were made on or before Oct 30, before the Oct 29–30 key rebuild. Together they hold 1,849 shown rows. Examples: US-FL 177, US-MN 157, US-CA 95, US-MI 90. These are the "previous public file" every keep-the-old-row path reads. 33 of these areas have no newer held copy in the waiting room.
**How sure:** Sure about the code paths. How often it fires depends on how many parks end up held or partial once the store is on.
**Check it:** `public-fers-file-ages.csv`. Run `rg -n QUARANTINE .github/scripts` in both repos (no hits).

### WL6. A code or rule change doesn't force a recheck unless someone writes it down correctly
**What breaks:** A pair's saved answer is reused when its fingerprint matches (`pair_fp`, ~2529). The fingerprint holds the outlines, pins, lines, pass grid and the declared rule-change ids. It does **not** hold any code version (`CODE_HASH` and `FERS_ALGO` are computed but never used) or the measuring constants (`SHRINK`, `TIGHT_SHRINK`, `STATION_IN`, `ZONE`, `BANK`, `STRETCH`, the n-fer logic). So a change to the math reuses yesterday's answers unless a scope entry names the parks. The safety net (`kpc-fers-rules-check.yml`) compares main and the change on **one made-up area of 6 squares** (tests/fixtures/fers-store-v4: no river, no near-line overlap, no 3-fer, no same-land, no Canada). Most math changes can't show up there, so the check passes without a scope entry. Also, three declared scopes use flags the code never sets (`blank-owner`, `approximate-tier`, `same-records`; `rule_stamp` only sets bad-pin, line, designation, lease). On their own they would recheck **nothing**. Today they're covered because a later `all` entry (2026-11-10-review-fixes) rechecked everything. Nothing warns about an unknown flag.
**How many:** Every pair reused on the next run ("pairs reused (nothing changed)" in each report).
**How sure:** Sure (code reading).
**Check it:** Change `TIGHT_SHRINK` in a copy, compute `pair_fp` for any pair: same value. `rg -n "blank-owner|approximate-tier|same-records" --type py` finds no code.

### WL7. Real spots the finer grid finds are thrown away (misses)
**What breaks:** In passes 2 and 3, each old row takes at most one new spot of its pair. Any other spot of the same pair is "new here only (not counted)". It's kept only when its pair's row was *dropped* in that pass (`leftover_spots`). In store runs it's also listed (`FINE_ONLY`), and it becomes a row only if the owner switch `KPC_FERS_FINE_ONLY=count` is on (off by default). So a second, separate patch of a pair that pass 1 saw as one blob, or that pass 1's coarser grid missed, is lost.
**How many:** Pass-3 "new here only" across the 95 run reports in KPC-Data data/fers: **20,749** spots, against 127,500 that agreed. Examples: report-mountain Nov 11: 1,752 vs 3,563. canadabc Nov 13: 249. Many are probably pieces of the same patch, but nobody has checked.
**How sure:** Medium (the mechanism is sure; the share of real spots is unknown).
**Check it:** `WL7-pass3-new-here-only-spots.csv`. Turn the switch to `count` on one area offline and compare.

### WL8. D10 tripwire hold can be silently off
**What breaks:** `tripwire_parks()` looks for the list only at `kpcdata/data/waiting/tripwires/not-sure.json` or `data/waiting/tripwires/not-sure.json`, relative to the folder the bot runs in, or at `KPC_FERS_NOT_SURE`. No workflow or runner sets `KPC_FERS_NOT_SURE`. The overlay doesn't copy `data/waiting/` (.github/kpc-moved.txt). On the PC runner, KPC-Data is its own folder (`kpcdata_checkout`), not `<links>/kpcdata`. So there the list is never found, and "no list" is silent by design (no warning, no count line). The list doesn't exist on KPC-Data main yet either (KPC-Data #118 not merged), so D10 is off everywhere today. That's expected, but nothing will say if it stays off after #118.
**How many:** Up to the 4,076 not-sure parks in #118, on every PC run.
**How sure:** Sure about the PC path. The KPC-Store workflow is private, so I couldn't check it.
**Check it:** Run a PC area with the list in KPC-Data: no "rows held: tripwire park" line in the report.

### WL9. Privacy: carried rows re-publish a withheld park's old shapes, and the exit re-check skips what it can't read
**What breaks:**
- `carry_held_rows` copies a withheld park's previous public rows unchanged. Those rows include the spot `shape` and the parks' `lines` (pieces of each park's outline near the spot, as coordinates). So a park withheld *because its record isn't publishable* keeps having pieces of that record's outline in the public file, run after run. It isn't a new leak (it was public before), but it keeps going with no end date.
- `final_redact()` skips any file it can't read as plain JSON (`except (OSError, ValueError): continue`), so a gzipped or broken side file isn't re-checked at exit. The push check would then refuse the whole push: safe, but it blocks good work.
- The name guard only looks for names of 2+ words with at least one uncommon word (`distinctive()`), and not at all when a public park has the same name. The ref guard still covers those cases, so it's a small gap.
- Too strict: HQ already diagnosed the PC's single shared withheld folder (≈112 of ≈125 refusals, ledger 59). I agree with that diagnosis. It's the main reason 24 finished areas from Nov 16 never reached KPC-Data.
**How sure:** Sure (code reading). I didn't look at KPC-Store's keeper code (private).

### WL10. Owner words on rows can be wrong, and the world will call private land "public"
**What breaks:** Owners come from a park's own record or its name (Nov 9 KISS rule), never from the patch. They're info only, but they're printed ("ground"). Examples in old rows: US-4491+US-4806 Superior NF / **Kabetogama State Forest** labelled "FED:NPS + FED:USFS". US-0046+US-0063 **Kings Canyon NP / Sequoia NP** labelled "Forest Service + Park Service". More important for later: `ownership_step()` now runs the US "official agency outline = public land" test **before** the world branch. So when the world opens, a UK National Park × AONB pair (whole-line designations over mostly private farmland) will read "public land (official agency outline)". That contradicts world rule (2) ("publicly accessible land … else NOT SURE").
**How sure:** Sure about the order in the code. The labels are as shown in the old files, and I didn't trace why each was wrong.

## 2. Future problems (what will bite as things grow)

1. **World opening.** The world goes through the US "official outline = public land" test first (WL10). Whole-line designations (UK/European national parks, AONBs, regional parks) hold mostly private land. Without an access-land layer they should be NOT SURE, not "public land". The write guard keeps world rows off the public site today (good). The risk starts the day the club-room-only rule is relaxed.
2. **New countries and agency layer changes.** `DESIG_PRE` and the state-gis `what` labels are US-only lists typed by hand. A new country's designation layer (or a US state relabelling a layer) gets no "may contain private land" note until someone adds its prefix. Better: make the layer's kind (owned / designation / compilation / register / water / outer line) a required field in every key's layers.json, and fail the key build when it's missing.
3. **Store growth.** The shelf is 85% today, and the 90% "except" rule keeps thin areas on the old path. As layers get confirmed, more parks move from "withheld" to "read". At that point every carried row (WL5) is replaced by a fresh answer, and the waiting room will see a wave of changed areas at once. Expect big jump reports, and plan a release batch for it.
4. **More keep-the-old-row paths.** Each new safety rule so far added another way to keep an old row (held, partial, kept, time-skipped, measured-nothing). Without an age limit, the public file slowly becomes a mix of rows made on different keys and rules, and no file says which is which.
5. **Rule changes by hand.** As the scope file grows (26 entries in 9 days), a missed or mistyped scope is more likely (WL6). A wrong scope means stale answers, with no error.
6. **The PC runner as the main engine.** Long runs, memory-guard kills, and a "previous file" base that differs from GitHub's (HQ ledger 59, cause 3). Two places now decide "what the last answer was". They should be one.
7. **D10/T1–T5 slack numbers still on trial.** When they change, the not-sure list changes, but rows are only re-held in pass 3 of a fresh run (carried rows are skipped).

## 3. Good and bad

### What it does well
- **Never writes "not a 2-fer".** Denials are taken out before writing (`no_denials`). Reasons go to a private file. The wording is always "may overlap".
- **Fails closed on privacy.** Every public write goes through `guard_write` (refs, names, world refs, club-room rows, the blocked build US-42797939226). Store runs physically refuse all network calls (`shut_door`). An area whose process left no withheld list is refused. `final_redact` re-checks at exit against the final withheld set.
- **Time-outs are handled with care.** Pass 1 keeps an unfinished area's previous file, marks a new one "incomplete", and carries time-skipped pairs. Pass 3 leaves a row "waiting for pass 3" instead of half-deciding it. "Done" is decided by the receipt, not the log.
- **Touching parks are safe.** In my grid test, overlaps of 0–14 m never passed, so a shared border alone doesn't make a 2-fer. Passes 1–2 only screen, and pass 3 decides.
- **Hand rulings are coded with their reasons** (KNOWN_LIVE, KY_DROP, SAME_LAND_PAIRS, PARTIAL), and Kentucky runs on its own files, never on the store.
- **Waiting-room handling of x.json / x.json.gz twins** (KPC-Data kpc_waiting_room.py) prevents two live copies of one area.
- **Lots of tests.** I ran all 30 tests/test_fers*.py offline on the box (Python 3.13.5, numpy 2.5.5, OpenCV 5.0): **29 pass, 1 fails**. The rules check runs main against the change before merge.

### What is fragile or over-complicated
- **kpc_fers.py is ~5,000 lines with about 190 module-level settings and globals** shared across passes (`chain_snapshot`/`chain_restore` exist just to reset them). Any new pass or store mode can leave a global from the last pass in place. That's hard to review and easy to break.
- **Comments are dated rulings, not a spec.** The rules live in comments with dates and chat names, and some contradict each other (e.g. comments still describe owned-land masks, but `pmask` is now the whole outline and `masked_out` can never be true; the quarantine file describes a code fingerprint that no longer exists). A reader can't tell what's live.
- **Dead machinery still runs:** OWNED / `masked_out` / the "dropped: inside the federal boundary" branch (`pmask` = whole outline since Nov 9), `CODE_HASH`/`FERS_ALGO`/`REUSE_KEY` (computed, never used), and the `KEEP_DROPPED_ROWS` path (off since Q3).
- **Five different "keep the old row" rules**, each with its own mark (`store_held`, `partial_kept`, `kept`, `not_worse`, time carry).
- **Two-step status strings** ("not sure: water not checked …") get rewritten by the store module by matching on text (`closed_status`). A wording change breaks the link.

## 4. Solutions (one per weak link)

| # | Fix in plain words | Bug fix or new rule | File | Proving test |
|---|---|---|---|---|
| WL1 | Give every layer a land kind (owned, designation, compilation, register, water, outer line). Only "owned" (and PAD-US Fee) counts as public land by itself. For any other kind, the row gets the "may contain private land" note, or is NOT SURE when **both** halves are non-owned. | **New rule** (below) | kpc_fers.py `designation_only`, `official_agency_outlines`; data/state-gis.json; layers.json | A made-up pair whose one half is a `register` layer gets the note; one with a `compilation` forest + a refuge is NOT SURE |
| WL2 | When the two parks have **different federal landowners** (NPS, USFS, FWS, BLM, Corps) and neither is a designation laid on the other, the pair is NOT SURE ("two agencies' maps disagree here"), not a candidate. | **New rule** | kpc_fers.py `ownership_step` (uses `mixed_owners` already on the row) | Grand-Canyon-like made-up pair (NPS + USFS area records) → NOT SURE; Yosemite × Merced WSR stays candidate |
| WL3 | Make the size test honest about its grid. Any overlap whose measured width is within one cell plus the simplify allowance (5 m + 3 m ≈ 8 m) of 22.9 m, 45.7 m or 91.4 m is NOT SURE ("near a size line"), unless it was measured on the fine (1 m) level. | **Bug fix** (applies N3 as written) | kpc_fers.py `area_spots` / `decide` | The made-up squares at 16, 20, 46 m → NOT SURE; 30 m and 60 m unchanged |
| WL4 | US `land_check` crash → NOT SURE (same as Canada). PAD-US closed-area query fail → NOT SURE "closed areas not checked". A crashed pair → its old row is carried like a time-skipped pair, and the area is marked incomplete. An unread park → its pairs' old rows carried, marked "outline not read". Any crash → exit code that turns the receipt red. | **Bug fix** | kpc_fers.py `decide` ~3785, `land_check` ~3407, `find_spots` ~2650, main ~4553 | Fault-injection tests: raise in each spot; expect NOT SURE / carried row / red receipt, never a candidate |
| WL5 | Stamp every row with the key build and the rules hash it was made on. A carried/kept row older than the current key build (or older than N days) becomes NOT SURE ("not re-checked since key X"). Delete the stale quarantine file or have the bot read it. | **Bug fix + small rule** | kpc_fers.py, kpc_fers_store.py (`carry_held_rows`, `keep_old_rows`, `carry_rows`) | A previous file stamped with an old key → its carried candidate comes out NOT SURE |
| WL6 | Put a code/maths fingerprint back into `pair_fp`: a hash of the measuring constants plus a hand-bumped `FERS_ALGO`. Fail the rules check when a scope names an unknown flag. Grow the test area to cover a river, a trail, a near-line overlap, a 3-fer, same land, and a Canada pair. | **Bug fix** | kpc_fers.py `pair_fp`, `rule_stamp`; kpc-fers-rules-check.yml; tests/fixtures | Change TIGHT_SHRINK → every pair retested; scope with flag `blank-owner` → check fails |
| WL7 | A pass-3 spot no row took becomes its own row (decided like any other) whenever it's at least 25 yards across and more than ~100 m from the row's spot. Smaller nearby pieces are merged into the row. | **Bug fix** (keeps real spots) | kpc_fers.py `leftover_spots`/`fine_only_spots` | A made-up pair with two separate patches 1 km apart → two rows |
| WL8 | Pass the list path explicitly (`KPC_FERS_NOT_SURE=<kpcdata>/data/waiting/tripwires/not-sure.json`) from `kpc_fers_area_run.py` and the PC runner. Once D10 is switched on, a missing list should be a **warning with a count line**, and the D10 hold should also apply to carried/kept rows. | **Bug fix** | kpc_fers_area_run.py, kpc_pc_run.py, kpc_fers.py `tripwire_parks`/`hold_tripwire` | PC-layout test: KPC-Data in a sibling folder → rows held; list missing → warning printed |
| WL9 | Carried rows of a withheld park keep refs/kind/status/center/size but **drop `lines` and `shape`**. `final_redact` treats an unreadable public file as a failure (fail closed, named in the log). Scope the push check per area (HQ's fix). | **Bug fix** | kpc_fers_store.py `carry_held_rows`, `final_redact`; KPC-Store keeper (HQ) | A carried row has no coordinates of the withheld park; a .json.gz public file at exit → refused loudly |
| WL10 | Run the world branch before the US "official = public" shortcut. In the world, whole-line designations are NOT SURE unless an access layer shows open land. Print the owner word only when it came from a record, never from a name. | **Bug fix** (world rule 2 as written) | kpc_fers.py `ownership_step` | A made-up W-GB national park × AONB → NOT SURE; Kabetogama-style name → no FED:NPS label |

**New rules, written out (for your yes/no):**

*Rule for WL1 (layer land kind).*
- **What counts:** an outline from a layer marked **owned** (the agency's own land/parcels, PAD-US Fee) counts as public land for the 2-fer.
- **What does not:** a layer marked **register** (historic register shapes) or **water** (lake surface) is never proof of land. A **compilation** or **outer/project line** layer is never proof of ownership.
- **When unsure:** if one half is owned land, the pair is shown with the "may contain private land" note. If **neither** half is owned land, the pair is NOT SURE until the agency's own land layer is read.

*Rule for WL2 (two federal landowners).*
- **What counts:** two parks of different federal agencies **where one is a designation laid on the other** (wild & scenic river, wilderness, national trail, NRA inside a forest; a refuge inside a seashore's legislated line).
- **What does not:** two land-owning units of different agencies (national park, national forest, refuge, Corps project) whose outlines meet. That's side-by-side land, even when the maps overlap.
- **When unsure:** if the bot can't tell which kind it is, the pair is NOT SURE, with "two agencies' maps disagree here, check both official maps".

## 5. Questions for you (numbered)

1. **WL1:** Should compilation-copy outlines (e.g. Montana "Managed Areas" for Flathead NF, US-4502) count as the park's official boundary at all, or only until the agency's own layer is found?
2. **WL2:** Do you agree that a national park or refuge sharing ground with the national forest next to it (Grand Canyon NP × Kaibab NF, 281 ac) should be NOT SURE by default, unless one is a designation laid on the other?
3. **WL3:** Is "within about 8 m of a size line = NOT SURE" the right band, or do you want it tied to the fine (1 m) level only, so near-line pairs wait for fine lines?
4. **WL5:** How old can a carried row get before it's NOT SURE: one key build, 30 days, or never carried after a key rebuild?
5. **WL7:** OK to turn on extra rows for separate patches the fine grid finds (switch `KPC_FERS_FINE_ONLY=count` everywhere, plus the 100 m rule)?
6. **WL9:** OK to strip the withheld park's `lines`/`shape` from carried rows, so the public file keeps "there may be a 2-fer here" without the private outline pieces?
7. **Housekeeping:** In .github/fers-rule-scope.json, `2026-11-17-thin-shelf` and `2026-11-17-d10-tripwire-not-sure` still say "WAITING FOR THE KPC OWNER'S APPROVAL", but you said you'd approved them. Do you want those two marked approved there too?
8. **Handoff file:** The Handoff 6 attachment wasn't on the box when I ran. Anything in it beyond the 9 topics my brief listed?

## 6. Anything else
- **One test fails on main on my box:** tests/test_fers_area_boxes_time_nov11.py ("files are byte for byte the ones main (11f908d9) wrote … c8148602acb1b8c5 == 31c900c81c9fa209"). It compares against files frozen from an old commit, so it may just be my library versions (it isn't in the rules-check list, which runs on 3.12). Worth one look on 3.12. Golden "byte for byte" tests like this break on any harmless change and teach people to ignore red.
- **The report's `problems` field keeps only the first 40 lines**, and GitHub keeps only 10 notices per step, so on a big run most failure lines are lost. Write the full problem list to the private folder.
- **Hard-coded pairs in code** (KNOWN_LIVE Mammoth Cave × Green River, KY_DROP, SAME_LAND_PAIRS, MAPFIX) are fine today, but they belong in one data file with the date and who ruled, like overrides.json.

## What I didn't get to
- I didn't read kpc_owned.py, kpc_fers_guard.py, kpc_fers_preline/postline/ready/receipt in full, or the KPC-Data release/grading scripts line by line. I only checked the twin-file handling and the quarantine.
- No full offline area rerun on the new key, so the old-file counts are examples only.
- No fault-injection run (WL4 is from code reading).
- KPC-Store (private) wasn't touched, so the keeper push check and the store workflow weren't reviewed.
- The 100 ft trail/river rule: I read `line_spots` but didn't test it on made-up lines.
