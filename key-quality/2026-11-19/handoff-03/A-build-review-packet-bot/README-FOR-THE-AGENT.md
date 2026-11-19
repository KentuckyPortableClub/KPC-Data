# Build job: the "review packet" bot (Kentucky Portable Club, hand-off 03A, 19 Nov 2026)

You are building ONE small tool for a ham radio club's map project. Read this page to the end before you start.
Everything you need is public: github.com/KentuckyPortableClub/KPC-Links (the website and the "key" builders) and
github.com/KentuckyPortableClub/KPC-Data (data and bots; its branch `tools-out` holds tool outputs).

## What the club does, in four lines
- For each park that Parks on the Air (POTA) lists, a builder (`KPC-Links/.github/scripts/kpc_us_key.py`) joins the park to the
  official land records that are its true outline. The result per state is a "key" file, `KPC-Links/data/us-key/US-XX.json`
  (`parks -> {ref: {n: name, m: [[record id, record name, acres, how it was joined], ...], c: [records sent to a person to check]}}`).
- The builder's matching rules change through pull requests. Every such PR must show old against new for the states it touches.
- Today that proof is built by hand inside AI chat sessions: slow, costly, and without the `shapely` package, so size checks do not count.
- Your tool does that proof on GitHub's own runners and writes one small folder, the review packet.

## What to build (three files, all in KPC-Data)
1. `.github/workflows/kpc-key-review-packet.yml`  started BY HAND only (`workflow_dispatch`).
   Inputs: `pr` (a KPC-Links pull request number); optional `head` and `base` (commit shas that override the PR's); optional `states`
   (for example `AK ID`; default = the scope states, see step 2).
2. `.github/scripts/kpc_key_review_packet.py`  the comparing and writing (Python standard library only; `--selftest`).
3. `tests/test_key_review_packet_nov19.py`  offline test of the script's own logic on tiny made-up files (no network).

Why KPC-Data and not KPC-Links: a KPC-Links workflow cannot write to KPC-Data, and the packet lives on KPC-Data's `tools-out`.
KPC-Links is only READ (checkouts at two commits, and its public release `boundary-cache`).
Copy the working pattern of KPC-Data `.github/workflows/kpc-trace-test.yml`: by hand, never red, saves a report folder to
`tools-out` with `.github/scripts/kpc_push_retry.sh`, ends with the "Report hidden failures (G8)" step.

## The steps the workflow runs
1. **The two commits.** NEW = the PR's head sha. OLD = the merge base of that head with the PR's base branch (so unrelated changes
   on main do not show up). Check KPC-Links out twice, in two clean folders (`old/`, `new/`), `persist-credentials: false`.
2. **The scope states.** Read `.github/us-key-rule-scope.json` in both trees. The entries (by `id`) that are in NEW and not in OLD
   are the PR's; the states are the union of their `scope.states` (`US-AK` -> `AK`). No new entry and no `states` input = stop
   with a plain line ("this PR adds no scope entry").
3. **Frozen inputs, the same for both trees.** (a) KPC-Data at ONE commit (this workflow's own checkout). In each KPC-Links tree run
   `bash .github/scripts/kpc_overlay.sh <path to the KPC-Data checkout>`: it lays KPC-Data's park data over the tree (the paths are
   listed in KPC-Links `.github/kpc-moved.txt`). (b) The saved shapes: the assets `US-XX.json.gz` of the KPC-Links release
   `boundary-cache` (`gh release download boundary-cache -R KentuckyPortableClub/KPC-Links -p 'US-AK.json.gz' -D shapes`).
   Record the commit shas and the asset dates in the packet (`inputs.json`).
4. **Build each state twice, offline.** In each tree:
   `KPC_KEY_REMATCH_IDS=1 KPC_KEY_OFFLINE=1 KPC_MASTER_OWNS=1 GEO_CACHE_MODE=only GEO_CACHE=<shapes folder> STATES="AK" python3 .github/scripts/kpc_us_key.py > build.log 2>&1`
   plus the other fixed settings of `KPC-Links/.github/scripts/kpc_key_scorecard.py` (`FIXED_ENV`: GEO_DETAIL, GEO_PAGE,
   KPC_ANSWER_SHEET=off, PYTHONHASHSEED=0, one fixed KPC_BUILD_DATE for both trees). The build rewrites `data/us-key/US-XX.json`
   in its tree, starting from the published file that is there. It makes NO web request in this mode; keep it that way.
   Speed, measured on a 2-core box: Alaska 5 minutes, Idaho 2.5, Oregon over 10, Florida over 30. So: one matrix job per state
   (`fail-fast: false`), old and new built side by side inside it, then ONE last job that gathers the files and writes the packet.
5. **What changed, per state.** (a) Every park whose joined records (`m`) differ: ref, name, records lost, records gained, total
   acres old -> new. (b) Every `::notice title=US key XX::...` line that only the NEW build printed (and those only OLD printed).
   This matters: a rule can act in the middle of a build and leave the final key unchanged; its notice line is the only trace.
6. **Fact check, both sides, same inputs** (run the NEW tree's copy of the tool on both key folders, after `pip install shapely`):
   `python3 new/.github/scripts/kpc_key_factcheck.py run --keys <tree>/data/us-key --cache <shapes> --parkinfo <KPC-Data>/data/parkinfo --truth <KPC-Data>/data/truth --areas US-AK,US-ID --out fc-old`
   It writes `factcheck-summary.txt` and one `factcheck-US-XX.json` per state (`parks -> ref -> class, flags, pin_km, acres`).
   From the two runs list: class and flags old -> new for every park that differs; "verified outlines lost" (verified in OLD, no
   joined record in NEW); "verified got worse" (verified in OLD, any other class in NEW); and `pin_km` old -> new (POTA's own
   pin: 0 means inside the joined land) for every park of 5a.
7. **Gold score, both sides** (`gold-us.json` is on KPC-Data `tools-out`, `key-quality/gold-us.json`):
   `python3 new/.github/scripts/kpc_key_grade.py gold --gold gold-us.json --keys <tree>/data/us-key --cache <shapes> --parkinfo <KPC-Data>/data/parkinfo --out gold-old`
   NEVER pass `--show-sealed`. Put the two `gold-score.txt` files in the packet and say in the summary whether the TUNE and SEALED lines differ.
8. **Write the packet** to KPC-Data `tools-out`, folder `key-quality/review-packets/pr-<n>-<first 7 of the head sha>/`:
   `summary.md` (ONE screen, plain words, a table: state | parks changed | outlines old -> new | verified old -> new | verified
   outlines lost | verified got worse | hard flags old -> new | notice lines only in NEW), then `parks-changed.csv`,
   `factcheck-diff.csv`, `notices-only-new.txt`, `notices-only-old.txt`, `gold-old.txt`, `gold-new.txt`, `inputs.json`.
   Put the same summary in the run's summary page. A state whose build failed or timed out is a ROW that says so, never a silent gap.

## House rules (the club's, not optional)
- By hand only: no `schedule`, no `workflow_run`, it starts no other workflow, it posts no issue or PR comment.
- Never red: a failing step is caught and reported, the run stays green (the owner gets an email for every red run). Use the
  pattern of `kpc-trace-test.yml`: `continue-on-error` on the work steps, every caught failure also appends a line to
  `$RUNNER_TEMP/kpc-hidden.txt`, and the standard "Report hidden failures (G8)" step is the LAST step of every job.
  KPC-Data's tests `tests/test_fixbundle_hidden_failures_nov4.py` and `tests/test_nextround_hidden_failures_nov5.py` read every
  workflow and must still pass (on main today the first has ONE known failure, "no cron line added"; nothing else may fail).
- It writes ONLY to `tools-out` under `key-quality/review-packets/`. Never to `main`, never to KPC-Links, never a key file.
- It talks ONLY to GitHub (the two repos and the release). No agency server, no map server, no POTA site. No tokens or
  passwords in code; the workflow's own `GITHUB_TOKEN` is enough.
- It decides nothing about parks. It reports. Do not change any file of KPC-Links at all, and no other file of KPC-Data.
- Plain words in everything a person reads (the owner is a ham, not a programmer). No real call signs or names in code or tests.

## How you will know it works (the acceptance run)
Run it for KPC-Links pull request 278 with `head=ac2ab4c80723ae3ebf19261339c339b3da6f849c` and `base=8140d35e14923e7fa17cc25254c854d78e3a86c2`
(the PR may have moved on by the time you read this; these two commits are what the figures below were made on).
Hand-made results to match are in `reference/` and on KPC-Data `tools-out`, `key-quality/2026-11-19/r-pp1/`:
- Scope states: AK AL CA CO FL ID KS LA NM NV OR TX WV (13).
- Parks whose joined records change: exactly five. Alaska: US-0026 loses record 3301, US-0044 loses 3304, US-0048 loses 3305,
  US-0069 loses 3314. Idaho: US-0665 loses 3299 (`reference/parks-changed.csv`). No other state changes a park.
- Notice lines only in NEW: Alaska "R-PP1 park and preserve: 7 record(s) to check ...", Idaho "... 1 record(s) ...", Colorado
  "... 2 record(s) to check: US-0033 Great Sand Dunes National Preserve, US-8295 Great Sand Dunes National Park". Colorado's final
  key is the same on both sides (0 of 276 parks differ). The other ten states print no R-PP1 line.
- Fact check, Alaska + Idaho together: outlines 362 -> 362, verified outlines lost 0, one park gets worse: US-0665 verified ->
  flagged (the pin is 22.7 km outside what is left). US-0069's pin_km goes from 0 to about 2.8.
  (The hand runs had no shapely and used the default shape detail, so your size flags and a few counts may differ: say so, do not force a match.)
- Gold score: the same on both sides.
Test in your own fork of KPC-Data (Actions on; the fork needs a `tools-out` branch). Florida is the slow one: let it finish.

## Part 2, only if part 1 is done and passes (same script, second use)
After a full US key run, the club compares the run's files with the published key, state by state. Add a mode `run`: OLD = KPC-Links
`data/us-key` at a given commit (input), NEW = `data/us-key` at main, with the files inside the asset `key-held.tar.gz` of the
KPC-Links release `key-held` laid over it (states the run held back). No builds: steps 5a, 6, 7 and 8 only, one row per state, and
for every park that lost its outline the reason text of its check rows (`c`). Folder: `key-quality/review-packets/run-<date>/`.

## What to send back
- A DRAFT pull request to KPC-Data from branch `prep/key-review-packet` if you can open one; otherwise a zip of the three files
  in their repo paths. Do not merge anything and do not start anything on the club's repos: a club session reviews it first.
- A short NOTES file: the link to your fork's acceptance run, the packet it wrote, what matched and what did not, anything left undone.
- If something here is wrong or cannot be done as written, say so in the NOTES and do the nearest safe thing. Do not guess.
