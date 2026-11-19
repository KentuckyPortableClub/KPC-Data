# Hand-off 06 CODE MAP (KPC-Links main `5e84846`, 19 Nov 2026)

Line numbers are today's and will drift: search by name. Where this page and the code disagree, the code is right and
the disagreement goes in your notes.

## The 2-fer bot

| File | What is in it for this job |
|---|---|
| `.github/scripts/kpc_fers.py` (5,197 lines) | everything below |
| `.github/scripts/kpc_fers_store.py` (2,291) | the outline store reader: `THIN_SHELF` 137, `KPC_FERS_SHELF_MIN` 136 / 404-406 / 2006; `carry_rows()` 659; `keep_old_rows()` 786; `HELD_TAG` 893, `STRIP_HELD` 896, `STRIP_KEYS` 897, `STRIP_NOTE` 898, `carry_held_rows()` 920; the three `_AGE.keep_fresh` calls 670, 819, 934 |
| `.github/scripts/kpc_fers_age.py` (68) | the whole-key age check R-2F4 replaces: `key_build()`, `stamp()`, `too_old()`, `keep_fresh()`, `NOT_CARRIED` |
| `.github/scripts/kpc_fers_receipt.py` (165) | the receipt (proof of work) and its done check: where the settings in force get recorded |
| `.github/scripts/kpc_fers_area_run.py` (254) | the one area driver; passes the D10 list at 61-62 |
| `tools/pc-runner/kpc_pc_run.py` (818) | the owner's PC runner; passes the D10 list at 459 |
| `.github/fers-rulings.json` | decided pairs, each with date + who ruled; `load_rulings()` (kpc_fers.py 83) stops with exit 4 when it is missing or broken: the model for the switch file |
| `.github/fers-rule-scope.json` | every declared rule change; the two entries of R-2F7 are `2026-11-17-thin-shelf` and `2026-11-17-d10-tripwire-not-sure`, both `"approved": "WAITING FOR THE KPC OWNER'S APPROVAL"` |
| `.github/fers-store-areas.json` | which areas a store run reads; its `except` list is NOT the thin-shelf rule and stays |
| `docs/fers-from-store.md` | the store rules; rule 10 "nothing private in a public file or log" is the privacy law of this hand-off |
| `docs/key-rules-change.txt` | the changelog; the newest 2-fer line is #269 (`b4f19e522c34 -> 0637d083bd98`) |

### In `kpc_fers.py`

| Name | Line | Note |
|---|---|---|
| `KEEP_DROPPED_ROWS` | 73 | 17 Nov ruling: a dropped row is not put back (off). Leave it. |
| `load_rulings()` | 83 | exit 4 on a missing / broken file |
| `NEAR_LINE_M` | 101 | R-2F3: a typed number of metres today (0 = off) |
| `SUMMARY_APPROX` | 106 | R-2F1 |
| `FED_NEIGHBOUR` | 108 | R-2F2: goes |
| `private_file()`, `save_problems()` | 188, 203 | the private-folder writers (a folder inside a git work tree is refused) |
| `no_denials()` | 241 | the "never worse" put-back, narrowed on 17 Nov to missing inputs: one of R-2F4's copy paths |
| `CELL` | 312 | the grid per pass: 20 / 10 / 5 m. R-2F3's band is this, at the pass that measured the width |
| `SHRINK`, `SMALL_M`, `TIGHT_M`, `TIGHT_SHRINK`, `STRETCH` | 317-327 | the owner's size lines (25 yd, 100 yd, 50 yd, 12.5 yd in, 25 m). Not yours to change. None of them is in `pair_fp` (part 2's guard covers them) |
| `designation_only()` | 1062 | the "may contain private land" rule of 17 Nov (on; not this job) |
| `LINE_NAMES`, `near_line()` | 1083, 1086 | R-2F3 |
| `SUMMARY_KINDS`, `SUMMARY_PRE`, `SUMMARY_NOTE`, `summary_only()` | 1101-1132 | R-2F1 |
| `FED_LAND`, `FED_FOREST`, `fed_neighbours()` | 1135-1148 | R-2F2: go |
| `area_spots()` | 2292 | the area measure on the pass's grid |
| `FERS_ALGO`, `REUSE_KEY` | 2611, 2612 | dead: assigned, read by nothing (`grep -rn "REUSE_KEY\|FERS_ALGO"` finds only these lines and one test that checks `pair_fp` does NOT hold it) |
| `rule_stamp()`, `pair_fp()` | 2625, 2654 | what makes a pair be measured again: its parks' outlines, lines, pins + the declared scopes. No code, no math version |
| `find_spots()` | 2701 | the top of the measuring call path (part 2's guard starts here) |
| `tripwire_parks()`, `hold_tripwire()` | 3661, 3685 | D10 |
| `decide()` | 3842 | the settings act at 3952-3969: Q1 designation note, `FED_NEIGHBOUR`, `SUMMARY_APPROX`, the very-tight label, `near_line()`, `_AGE.stamp()` at 3970. `_apx` at 3880 is where a key grade of `approximate` reaches a row (R-2F1 item 6) |
| `FINE_ONLY_SWITCH` | 4050 | `KPC_FERS_FINE_ONLY=count`, store runs only (`fine_only_mode()` 4206) |
| `FINE_GAP_M`, `FINE_100M`, `fine_own_row()`, `fine_only_spots()` | 4215-4262 | R-2F5: the 100 m rule goes |
| `write_receipt()` | 4314 | |
| the pass-1 copy paths | 4902, 4907 | `_AGE.keep_fresh` on a small-batch run's other rows and on timed-out / crashed pairs |

## The rules hash and the check

- `.github/scripts/kpc_key_freeze.py`: `RULE_FILES['fers']` (line 50; 14 files today), `rules_hash(kind)` (line 210).
  The hash also reads `.github/key-rules-version.json`: on a checkout without it the hash is wrong.
- `.gitattributes`: line endings for every rule file. Read its first 12 lines before adding a rule file.
- `.github/workflows/kpc-fers-rules-check.yml`: runs on every pull request that touches a 2-fer rule file (Python
  3.12, numpy + opencv-python-headless): main's code against yours on the test area, and nine rule tests. You may edit
  its `paths` and its test list, nothing else. No YAML key twice in one step; `permissions: contents: read` stays.
- `tests/HANDOFF-GATE.md`, `.github/scripts/kpc_full_suite.py`, `tests/known-fail-main.txt`: the gate.
- Test areas: `tests/fixtures/fers-store-v4/` (US-RI), `tests/fixtures/fers-store-v3/` (US-ZA, US-ZB).
- `tests/fixtures/fers-wl3-near-line-rows.csv`: 472 old rows near a size line (230 at 25 yards, 188 at 50 yards, 54 at
  100 yards; 34 of them water only).

## The pattern to copy for the switch file

- `.github/key-switches.json` and `.github/scripts/kpc_key_rules.py`: `DEFAULTS` 137, `switch_file()` 179,
  `setting()` 199. The key file is sliced per area; the 2-fer one does not need that (the owner's answers hold
  everywhere): one value per setting.
- Why the keys got it (changelog, 17 Nov, "The key rule switches in one file"): the switches were read only from the
  build's environment and no workflow passed them, so turning one on did nothing, and a failed import switched every
  rule off in silence.

## What a row is copied from (R-2F4, R-2F6)

- A key file: KPC-Links `data/us-key/US-XX.json`, `parks[ref] = {n, m: [[record id, name, acres, how]], c: [check rows],
  g: official / approximate / pin, ...}`; `data/ca-key/`, `data/world-key/` alike. How the 2-fer loader reads a park:
  `kpc_fers.py` 620-730. Check every field against the code that writes it before you fingerprint it.
- `data/us-key/index.json` on 19 Nov: `build "US-44600381160"`, `built "2026-11-19 20:25 UTC"`, `areas_reused` 39,
  `areas_rebuilt` 0, `failed` 11; per state `area_hash`, `out_sha`, `built_sha`, `rules`. `build` is the RUN, not the
  park: that is the defect of `kpc_fers_age.py`.
- The store index: checksums per park (`kpc_fers_store.py`, `LazyOutlines`; `docs/fers-from-store.md` rules 3-4).
  The reviewer did NOT open a store index: what it holds for a withheld park, on the private store and on the public
  shelf, is yours to find and report (R-2F4 item 3).

## Every path that puts an old row into a new file (R-2F4)

`_AGE.keep_fresh` is called at five places today: `kpc_fers.py` 4902 and 4907, `kpc_fers_store.py` 670, 819 and 934.
The reviewer found NO call on the partial-boundary path (`partial_kept`, `kpc_fers_store.py` about 880) nor in the
never-worse put-back (`no_denials()`, `kpc_fers.py` 241). Search `KEPT_MARKS`, `carry_`, `keep_old`, `partial_kept`,
`not_worse`, `store_held`; list every path in your notes and prove each with a test (an unstamped row never comes
back through it).

## Not yours (named so you can find your way)

- KPC-Data `.github/workflows/kpc-fers*.yml` (eight files: `kpc-fers.yml`, `-chain`, `-check`, `-line`, `-lines`,
  `-pending`, `-postline`, `-water`): the runs. With the switch file they pass nothing new.
- KPC-Data `.github/scripts/kpc_tripwires.py`: writes `data/waiting/tripwires/not-sure.json` (D10's list; not on main
  yet on 19 Nov).
- KPC-Data branch `tools-out`, `not-sure/` and `key-quality/2026-11-19/handoff-05/HANDOFF-05-ADDENDUM-1-not-sure-list.md`:
  the shared NOT-SURE list and its row shape (part 3).
- KPC-Store and `tools/kpc_store_public.py`: the outline store and its public shelf.
