# Bot fixes for KPC-Links and KPC-Data (v0.5.0, Nov 2 2026). LOCAL PATCHES, NOT APPLIED

These patches were made from read-only copies of the two repos. Nothing was pushed, committed or opened as an issue or
PR. Each patch applies on its own, with `-p1` at the root of its repo. `orig/` holds the exact files they were made
against, so the tests can apply them anywhere.

| Patch | Repo | What it fixes |
|---|---|---|
| `KPC-Links-01-save-by-overwrite.patch` | KPC-Links | It adds `.github/scripts/kpc_save_overwrite.sh` and edits `kpc-us-key.yml`. **BOT A's save:** the old save did `git pull --rebase`, hidden by `\|\| true`, so chat 11's NOs were applied and then thrown away on every run since Oct 30. Now BOT A re-runs its writers on the newest `main` and pushes. A save that never lands turns the job red. The Join save uses the same script (`--copy`, never overwriting the hand-edited `overrides.json`). `ref: main` is added on both checkouts. |
| `KPC-Links-02-key-answers.patch` | KPC-Links | `kpc_key_answers.py`: **line 129** (a YES now clears even a *sole* NO). A **NO is stored with its name and acres** (`nofp`). A stop is printed as `::error`, and also exits 1 when `KPC_LOUD_FAIL=1`. |
| `KPC-Links-03-key-rules.patch` | KPC-Links | It adds `kpc_key_rules.py` and edits `kpc_us_key.py`. **NO checks on every join path** (id loop, alias_all, RIDB, alias, name join, keep-last-good, and "found again"). It also adds a NO by saved name, the **name check on id joins**, the **pre-handoff self-checks**, and **confidence sorting** with one-line reasons (`review/unsure-US-XX.json`). |
| `KPC-Links-04-fers-algo.patch` | KPC-Links | `kpc_fers.py`: `FERS_ALGO` as an alternative reuse key to `CODE_HASH`. |
| `KPC-Data-05-waiting-room.patch` | KPC-Data | `kpc_waiting_room.py`: **list guards** in `c_key`, `c_fers`, `c_intake`, `c_pota` and `closures_filter` (a wrong-shape part is now an "unsure" HOLD in plain words, never a crash). It adds the key-file name switch, and **tidy** for held copies, which is off by default. |
| `KPC-Data-06-tracers.patch` | KPC-Data | It adds `draft/kpc_trace_limits.py` and edits the picture prep, the picture tracer and the parcel tracer. The tracer limits: acres passed in, honouring the chosen image, a tunable better-than-chance gate, a tunable `ADJ_M`, a growth cap, and subtracting other parks. |

`kpc_parcel_trace.py` is at an assumed path (`draft/tools/kpc_parcel_trace/`). If it lives somewhere else, apply that
file's part of patch 06 by hand, or move the file in `orig/` and remake the patch.

## Switches (every new rule has one; the defaults match current practice)

Bug fixes are ON by default. New behaviour is OFF, or set to today's value, until Brandon says otherwise.

| Switch (env, or a repo variable) | Default | Meaning |
|---|---|---|
| `KPC_SAVE_MODE` | `overwrite` | `rebase` = the old way (now loud on failure). |
| `KPC_SAVE_TRIES` | `5` | Save attempts (the Join save uses 6). |
| `KPC_LOUD_FAIL` | `0` | `1` = a stopped answers writer also exits 1. |
| `KPC_NO_ALL_PATHS` | `1` | Bug fix: a NO is honoured on every join path. |
| `KPC_NO_BY_NAME` | `0` | `1` = a NO also matches by its saved name and acres (it survives a PAD-US renumbering). |
| `KPC_ID_JOIN_NAME` | `0` | `1` = a join by id whose record no longer looks like the park becomes a candidate, with the reason. |
| `KPC_REFOUND_NEAR` | `0` | `1` = a kept outline is "found again" only near the park's pin. |
| `KPC_SELF_CHECKS` | `0` | `report` = list the problems, `hold` = hold those parks. |
| `KPC_CONF_SORT` | `0` | `1` = write `review/unsure-US-XX.json`, so only unsure parks go to chat 11. |
| `KPC_FERS_REUSE_KEY` | `code` | `algo` = reuse 2-fer results while `FERS_ALGO` is unchanged. |
| `WAITING_KEY_NAMES_ONLY` | `0` | `1` = only `US-XX.json` / `CA-XX.json` are routed to the key checker. |
| `WAITING_TIDY` | `0` | `1` = remove held copies that live already has. |
| `WAITING_KEEP_GENS` | `0` | N > 0 = keep only N `previous-` generations. |
| `KPC_TRACE_HONOR_IMAGE` | `1` | Bug fix: trace the image the prep step chose (`--no-honor-image` = the old first-jpg pick). |
| `KPC_TRACE_ACRES_FILE` | (empty) | An official acres list for rows without acres (`--acres-file`). |
| `KPC_TRACE_CHANCE_RATIO` / `_MARGIN` | `1.5` / `2.0` | The better-than-chance gate (today's numbers). |
| `KPC_PARCEL_ADJ_M` | `200` | Parcel adjacency in metres (**suggested 30**). |
| `KPC_PARCEL_GROW_CAP` | `0` | Growth cap as a multiple of the official acres (**suggested 1.25**). |
| `KPC_PARCEL_SUBTRACT` | `0` | `1` = cut other parks' outlines out of a traced parcel shape. |

## Test them (here, then on a TEST BUILD, never straight on main)

1. **Here:** from the engine folder, run `python3 -m pytest -q patches/patch_tests`. This applies all six patches to a
   tmp copy of `orig/`, compiles everything, parses the workflow, runs `bash -n` on every run block, runs the save script
   against a local bare git repo, and runs BOT A on sample files.
2. **Dry run against the real files:** in a scratch clone of each repo (not the club's checkout), run
   `patch -p1 --dry-run < <patch>`. If the repo moved on since Nov 2, fix any hunk that fails by hand.
3. **Test build on GitHub:** push the patched files to a **test branch in a fork**, or to a test branch Brandon creates.
   Then run `kpc-us-key.yml` with `workflow_dispatch` for one small state:
   - Check that BOT A's save shows `saved (overwrite, try 1)`.
   - Check that the NOs from chat 11 are in `overrides.json`.
   - Run `kpc_engine.py doctor --links <test links> --data <test data> --out OUT`. `nos.json` must show 0 missing and
     0 came back.
4. Turn on one new switch at a time as a **repo variable** on the test branch. Compare the key against the previous
   build, then decide.

## Needs Brandon's OK before anything goes to main

- Applying any of the six patches to the club repos (somebody with write access has to apply them).
- `KPC_SAVE_MODE=overwrite` replacing the rebase save.
- Each new switch: `KPC_NO_BY_NAME`, `KPC_ID_JOIN_NAME`, `KPC_REFOUND_NEAR`, `KPC_SELF_CHECKS`, `KPC_CONF_SORT`,
  `KPC_FERS_REUSE_KEY=algo`, `KPC_LOUD_FAIL`, `WAITING_TIDY` / `WAITING_KEEP_GENS`, and `WAITING_KEY_NAMES_ONLY`.
- The tracer numbers: `ADJ_M` 200 → 30, the growth cap of 1.25×, and subtracting other parks.
- The engine's `key_doctor.per_park_release` (per-park release of a LIVE-FILTERED key).
- The storage plan (`STORAGE_PLAN.md`): splitting files, LFS or a release asset, and squashing `tools-out`.
