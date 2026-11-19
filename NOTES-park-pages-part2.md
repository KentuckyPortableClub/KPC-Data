# Park pages, part 2

## What is NOT built

- No PC launcher, no person page, no intake, no `pc-kit`. That is part 3.
- No blind kits. That is part 4.
- The club's other bots are not wired to the not-sure list. The key run, the fact check, the size checker, the drop guard, the layer keeper, and the owner's PC tools are the club's to connect after this module is merged.
- Nothing was pushed to `tools-out` or `main`. The save job is written so the club's own run copies `park-pages/` and `not-sure/` onto `tools-out`. It was not started.
- The page reader does not settle a row. It has no call to `settle`.
- The schedule line is in the workflow and commented out. It is not on.

## Addendum 1, built

- `.github/scripts/kpc_not_sure.py`: `add`, `tried`, `settle`, `mark_gone`, `open_rows`, `summary`, `import-seed`. Standard library only. No network.
- The worklist's first step is an open not-sure row that wants page facts, an official size, or a map. Wrong likely comes before unsure. A class row is not handed to the reader.
- After a read, each open row for that park gets a `tried` note (the quote, or page silent / refused / script-built). Each reader question becomes a row, `found_by: park page reader`. A reader row turns `gone` when that question no longer comes up. It is not settled.
- `not-sure/summary.md` is one phone screen: open rows by how sure, the 15 busiest wrong-likely parks, how many closed since last time and by whom, how many no bot can help.
- Tests: add twice is one row; tried and settle keep the story; two writers in either order write the same bytes; an unknown code or wants word is refused; a class row is never handed to a bot; the seed's 104 rows load and split by area with none lost.
- The row shape and two examples are in `docs/park-pages.md`.

## Addendum 1, not built

- No other bot writes a row. That wiring is the club's.
- The seed was not copied onto `tools-out`. The test imports `tests/fixtures/park-pages/not-sure-seed.json` into a temporary folder.

## What is built besides the addendum

The worklist (list drops and a refs file, then check rows or approximate, then pin with a page, then never read by qsos, then facts older than 30 days). A fingerprint that did not change keeps the old facts and only moves the seen date. A real change of name, kind words, a size, or the final host writes one row in `changes.csv`. A footer change does not. `summary.md` for the run, `questions.csv`, `for-a-person.csv`, `evidence-drafts/`, and `lists-done/`. The workflow `kpc-park-pages.yml`.

## The three review items

Checked by `tests/test_park_pages_nov19.py`, which ends ALL PASS.

1. The workflow loads. A loader that refuses a repeated key accepts it. No key is written twice.
2. No step calls `gh`. No step's env holds `GH_TOKEN` or `GITHUB_TOKEN`. The read step also unsets those names before it runs the reader.
3. The workflow's own permission is `contents: read`. The read checkout sets `persist-credentials: false`. The save job is the only one with `contents: write`. It checks out `main` and runs git and `kpc_push_retry.sh`. It does not run `kpc_park_pages.py`.

## Tests

`tests/test_park_pages_nov19.py` prints 74 PASS lines and ends ALL PASS. `tests/test_not_sure_nov19.py` prints 12 PASS lines and ends ALL PASS. `kpc_park_pages.py --selftest` prints 18 PASS lines and SELFTEST PASS. `kpc_not_sure.py --selftest` prints 6 PASS lines and SELFTEST PASS. Wrong facts on the part 1 known answers are still 0.

## Guesses

- A seed wants-phrase that is not on the fixed list is not stored as a want. The row is kept. "location facts" is stored as page facts. "far join" is stored as far-join evidence.
- The first summary says 0 closed since last time, because there is no earlier summary. Already-settled seed rows are not counted as closed by this run.
- A not-sure park that is not in the loaded parkinfo is not placed on the worklist.
- A row the reader adds is `unsure`. The reader does not call a row wrong likely.
- "Busiest" is POTA's qsos from `data/parkinfo`.
- "No bot can help" means an open row whose wants are only a person or the owner, or whose wants are empty.
