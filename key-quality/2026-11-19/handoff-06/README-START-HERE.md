# KPC hand-off 06: the 2-FER RULES PR (the owner's seven answers + what the 17 Nov shelf left)

From: Kentucky Portable Club (owner Brandon White, KZ4CP), written by the club's reviewer (Fable), 19 Nov 2026.
For: the outside agent. You write DRAFT pull requests; the reviewer reads each one and sends it back with edits until
it is right; the club merges. You merge nothing and start nothing.

Read in this order: this file, `RULE-SHEET.md`, `CODE-MAP.md`, `known-answers/`.

A name to keep straight: this is hand-off **06 of the 19 Nov series**. It is not "Handoff 6" of 17 Nov (an outside
code review of the 2-fer bot) and not "Handoff 9" of 17 Nov (the fix list built from that review, merged as KPC-Links
#269, branch `agent9/fers-fixes`). Both are history you build on.

---

## 1. Where things stand (checked by the reviewer on 19 Nov, on KPC-Links main `5e84846`)

- The 2-fer bot is `KPC-Links/.github/scripts/kpc_fers.py` (5,197 lines) and its helpers. Its rules hash is
  `0637d083bd98` (`kpc_key_freeze.rules_hash('fers')`), the same as the newest 2-fer line in
  `docs/key-rules-change.txt`.
- #269 (17 Nov) is on main. `tests/test_fers_handoff9_nov17.py` ends `ALL PASS` (Python 3.13.18, numpy 2.5.3,
  opencv 5.0.0). It fixed the quiet failures, D10 on the PC runner, the problems list, the world designation note and
  the rulings file. **Do not build any of that again.**
- #269 also built the owner's seven open questions as settings, **all OFF**. On 19 Nov the owner answered all seven
  (`RULE-SHEET.md`). Two of the settings are now wrong as built (the 8 m band, the whole-key age check), two rest on a
  rule he turned down (park beside a forest, the 100 m distance), and one rule he was asked to approve he replaced
  (the thin-shelf fallback).
- The club's own note `.claude/notes/fers-fix-later.md` was written three hours BEFORE #269 was merged and still says
  "nothing below is built". Trust the code, not that note. Section 6 lists what is truly left of it.
- **2-fer runs are parked** (owner, 17 Nov: no public 2-fer run until the keys are good). The US key was rebuilt on
  18 and 19 Nov and its release run was started on 19 Nov (its result is the club's to read). Your work is what has to
  be in before the first fresh 2-fer run on the new keys. You run no area.

## 2. The laws

1. **Rules first, no new numbers.** `RULE-SHEET.md` is the whole brief for what the bot may decide. R-2F0 in it is the
   owner's own summary of POTA's rules. If the sheet does not cover a case, you stop and write the grey area down.
2. **Nothing is ever written saying a pair is NOT a 2-fer.** A row is shown, is NOT SURE with a plain reason, or is
   absent.
3. **Privacy stays exactly as it is.** The write guard, the redaction at the end of a run, the private log, the
   exit-89 refusals and the push check are not yours to touch beyond the one line R-2F6 names.
4. **The same rules on every machine.** A rule the owner made is not something each runner has to remember to pass
   (that is how D10 was silently off on his PC until #269). One file, under the rules hash, read by every run.
5. **Honest and offline.** Every test runs with no network. You open no agency site, start no workflow, run no area,
   and never ask the owner for a key, a token or a file from his private folder.

## 3. What you send, in this order (each part its own draft pull request to KPC-Links)

| Part | What | Branch |
|---|---|---|
| 1 | The seven answers as rules in force: the switch file, R-2F1 to R-2F7 | `prep/fers-owner-answers-part1` |
| 2 | The three things the shelf still holds: the math guard, the byte tests, the test that writes into the repo | `prep/fers-owner-answers-part2` |
| 3 | The bot says what it is not sure of, in the shape of the shared NOT-SURE list | `prep/fers-owner-answers-part3` |
| 4 | A PROPOSAL only (half a page, no code): measuring a near-line spot finer | in your part 1 notes |

Send part 1 when it passes. Do not hold it for the others.

## 4. Part 1: the answers become rules in force

### 4a. One switch file

Copy the pattern the keys got on 17 Nov (`.github/key-switches.json`, `kpc_key_rules.setting()`; `CODE-MAP.md`):

- `.github/fers-switches.json`: one entry per 2-fer rule setting: its value, the rule number of the sheet, the date,
  `ruled_by`, and the owner's words. Every entry needs a date and who ruled, like `.github/fers-rulings.json`.
- A small reader (standard library, its own module so `kpc_fers.py`, `kpc_fers_store.py` and `kpc_fers_age.py` share
  it). An environment variable of the same name still wins (tests, offline proofs). A missing or broken file, or a
  setting the code asks for that the file does not hold, **stops the bot loudly** (exit 4, as `load_rulings()` does):
  never "everything off" in silence.
- Both files are 2-fer rule files: add them to `RULE_FILES['fers']` in `kpc_key_freeze.py`, to the `paths` of
  `.github/workflows/kpc-fers-rules-check.yml`, and the module to `.gitattributes` (line endings: read the note at the
  top of that file).
- The run's receipt records every setting in force and where it came from (`file` or `env`), and the run prints one
  plain notice when an environment variable overrides the file. Two runs can then be compared by their receipts.
- The PC runner and the area runner pass nothing for these: a checkout has the file. Check both and say so.

### 4b. The settings after your change

| Setting today (all OFF) | After | Rule |
|---|---|---|
| `KPC_FERS_SUMMARY_APPROX` | ON | R-2F1 |
| `KPC_FERS_FED_NEIGHBOUR` | **removed** with its code and its test checks | R-2F2 |
| `KPC_FERS_NEAR_LINE_M` (a number of metres; lean 8) | replaced: on / off only, the band is ONE GRID CELL read from `CELL`; ON | R-2F3 |
| `KPC_FERS_CARRY_MAX=key` (compares with the whole key's run id) | replaced by the per-park stamp `made_on`; ON | R-2F4 |
| `KPC_FERS_FINE_ONLY=count` + `KPC_FERS_FINE_100M` | `FINE_ONLY` ON; `FINE_100M` and `FINE_GAP_M` **removed**: a separate piece, no distance | R-2F5 |
| `KPC_FERS_STRIP_HELD` | ON, with the owner's note text | R-2F6 |
| `THIN_SHELF = 0.90` / `KPC_FERS_SHELF_MIN` | **removed** | R-2F7 |

Plus the two labels in `.github/fers-rule-scope.json` (R-2F7).

Where a setting only changes how `decide()` labels a row, nothing has to be measured again (pass 3 decides every row
on every run). R-2F5 can add rows and R-2F4 changes what a file keeps: your scope entry says so, by rule number.

### 4c. What each rule must come with

For each of R-2F1 to R-2F7: the code, a test with made-up parks for the plain case, the trap and the unsure case, and
the checks of `tests/test_fers_handoff9_nov17.py` that the rule changes brought up to date in a NEW test file
(`tests/test_fers_owner_answers_nov19.py`). Keep the Handoff 9 test: delete from it only the checks of rules that no
longer exist (Q2, the 100 m rule, the 8 m band, the whole-key age) and say which, line by line, in your notes.

On the Kentucky path (`REGION == 'ky'`): do not fold it, do not change it. Say in your notes, rule by rule, whether
the rule acts there today.

## 5. Part 2: what the shelf still holds

1. **A change to the measuring math can reuse every saved spot.** Since 9 Nov a pair is measured again only when one of
   its parks changed or a declared scope names it (the owner: "only redo the parts that changed"). That stays. The hole:
   a change to the math marked `scope: none` by mistake keeps yesterday's spots for every pair. `FERS_ALGO` and
   `REUSE_KEY` look like the answer and are dead: nothing reads them (`CODE-MAP.md`).
   - Remove the dead `FERS_ALGO` / `REUSE_KEY` / `KPC_FERS_REUSE_KEY` lines and their comment.
   - Add a **math guard** test: a fingerprint of the source of every function that can move or size a spot (from
     `find_spots()` down) and of the size constants that are not in `pair_fp`, saved in a small fixture with the id of
     the scope entry that last covered it. When the fingerprint changes, the test fails until the same pull request
     adds a scope entry that is NOT `none` and updates the fixture. Put the function list in your notes: the reviewer
     checks it against the call path.
   - Add it to the rules check workflow's test list.
2. **Byte-for-byte tests that break on harmless changes.** `tests/test_fers_area_boxes_time_nov11.py` was reported
   failing on Python 3.13.5; on 3.13.18 it passes (34 checks). Run the hand-off gate (`tests/HANDOFF-GATE.md`) on Python
   3.12 AND 3.13. A 2-fer test that differs between them and compares bytes where the bytes are not the point compares
   meaning instead (parsed JSON). Bytes stay the point for: hash inputs, the privacy "exact copy" rows, the rules check.
   List each test you change and why.
3. **A test that writes into the repo it runs in.** `data/status/test_fers_final_redact_nov17.json` is on KPC-Links
   main (commit `43720d6`, 19 Nov): a 2-fer test's status file with `/tmp/...` paths in it, swept into a notes commit.
   Find which 2-fer tests write under the checkout when run from its root, make them write to their own temp folder,
   delete that file in the pull request, and add the check to your notes ("git status is clean after the suite").

Not in part 2, and not in this hand-off: folding the Kentucky path into the national one; pulling the rules out of the
code comments into one table. Both need a plan from the club first.

## 6. Part 3: the bot says what it is not sure of

The club started one shared NOT-SURE list on 19 Nov (hand-off 05, addendum 1: one row = one park + one doubt + the
reason in plain words + what would settle it). Its module (`kpc_not_sure.py`, KPC-Data) is not on main yet, and you
do not wait for it.

- At the end of a run the 2-fer bot writes `not-sure-rows-<tag>.json` beside its report: rows in that list's shape
  (`ref, area, name, code, how_sure, shows_now, why, wants, found_by: "2-fer bot", evidence`), sorted by park number
  then code, so two runs on the same inputs write the same bytes.
- Rows it writes, its OWN doubts only: (a) every park whose outline is summary-map only (R-2F1):
  `wants: ["official layer"]`; (b) every pair NOT SURE near a size line (R-2F3), one row per park of the pair:
  `wants: ["map", "a person"]`. Not the tripwire parks: the tripwire bot owns those rows.
- Propose the code names and one plain line for each in your notes; the club adds them to the list's README. No
  free-text codes.
- It goes through the same guarded save as every 2-fer file: a withheld park is never in it. Test that.
- It reports. It settles nothing, reads nothing back and holds no pair because of the list. Whether a park on that
  list should be NOT SURE for 2-fers is a question for the owner, not for this hand-off.

## 7. Part 4: a proposal, no code

On the 17 Nov file, 380 rows fall in R-2F3's band: a 5 m grid cannot tell which side of a line they are on. Ruling N3
says the FINE level decides. In a store run every pass reads the same shapes (about 2 m); only the grid is coarse.

Write half a page in your part 1 notes: how the bot could measure just such a spot on a finer grid before it gives
up; what error is left after that and **where that number comes from** (a grid cell, the store's own stated detail:
never a number of yours); what it costs in time and memory; what it would do to the 43 x 16 readings of
`known-answers/grid-readings.csv`. The reviewer answers; only then is it built.

## 8. Tests and the acceptance bar

All offline. Script style of the repo: `PASS` / `FAIL` lines, ending `ALL PASS` / `SOME FAILED`; pytest is not the
suite. Work on a FULL checkout: on a partial one the rules hash comes out wrong (it reads
`.github/key-rules-version.json`) and several tests fail for want of files.

Before you change anything, record the baseline on main: the gate's last lines and the fers rules hash.

What must pass:

1. every rule of the sheet: the plain case, the trap and the unsure case, on made-up parks;
2. `known-answers/known-answers.json`: every row marked `must`;
3. with the switch file as you ship it, `git diff` of the test area's output against main shows only rows you can name
   by rule number; list them in your notes (the rules check workflow does this comparison on your pull request: read
   `tests/test_fers_store_switch_nov15.py` first to see how);
4. with every switch forced off by environment, the test area's output is byte for byte main's, apart from what
   removing Q2 / the 100 m rule / the thin-shelf floor cannot avoid (name it);
5. a missing or broken switch file stops the bot (exit 4); a withheld park appears in no file you add;
6. the hand-off gate: GATE PASS, and `git status` clean after it.

**Honest numbers.** For R-2F1 give the recount and the park list. For R-2F3 give the count on the 472-row file. For
R-2F4 give, on the test fixtures, rows copied before and after. Where you could not measure something offline, say so
in one line; do not estimate.

## 9. What is NOT in this job

No change to a key, a key rule, a saved answer, an outline, the outline store, the public shelf tool, a site page, a
notice, a schedule or any KPC-Data workflow. No world rule (world 2-fers stay club room only and off). No Kentucky
path change. No new number. No run of a real area. No keyed API, no agency site, no `api.pota.app`. No secrets in any
file. Nothing on main over 1 MB.

## 10. Send back

- A **draft** pull request to KPC-Links per part. If you cannot push, a zip of the changed files in their repo paths.
- Each pull request moves the 2-fer rules hash, so it brings what the club's review rule asks for
  (`.claude/notes/key-quality.md` section 13): the rule line in plain words with the owner's ruling (date + his words,
  from the sheet); the new test; a scope entry in `.github/fers-rule-scope.json` with
  `"approved": "WAITING: Reviewed: Fable, <date> + APPROVED, decided_by KPC owner"`; the old and new rules hash; and the
  changelog line for `docs/key-rules-change.txt` in the form of the lines already there, ending "Reviewed: Fable,
  <date>" left for the reviewer to fill.
- `NOTES-fers-owner-answers-part<N>.md` in the pull request: **what is NOT built, first**; the baseline and the gate's
  last lines; the numbers of section 8; every place you had to guess and what you guessed; every grey area, numbered;
  anything in this hand-off you found wrong (the reviewer made it in one sitting: check it against the code).
- Expect edits. The owner's words for this one: "get the agent to make us a draft and you review and have them edit it
  how you want".
