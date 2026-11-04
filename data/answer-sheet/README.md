# data/answer-sheet: park ref → official record (KPC-Data main)

There is one CSV per country (US.csv, CA.csv, world.csv), with one row per (park, record). The columns and rules are in the Mapping inbox
`2026-11-03-answer-sheet/DESIGN.md`.

- **Words in `status`** are the shared answer words (`.github/scripts/kpc_answer_words.py`): **YES / NO / PIN / FIXED / NOT SURE**.
  - **YES** joins. By default (option B) it also needs a person's sign-off: `approved_by` names Brandon or KZ4CP as a whole name, and `approved_date` is a real date (YYYY-MM-DD).
  - **NO** is not used. Also put the id in `data/us-key/overrides.json` `no`.
  - **PIN, FIXED, NOT SURE** (and any typo) make the park a NOT SURE question. The builder never falls back to its own guess for that park.
  - **PROPOSED** is a bot's suggestion and is not used. **APPROVED** is the old word for YES, and **CAN'T TELL** / **STALE** are old words for NOT SURE.
- **Who writes it:** Super, through a PR from an inbox batch. No bot or engine writes this folder.
- **Where a person answers a NOT SURE line:** in an inbox batch (YES or NO per row). Quality then writes the word on the row.
- **`check/<XX>.json`** is written each night by `kpc_answer_sheet_check.py`. It is read only, never uses a cache, and never edits the sheet.
- **`check/<XX>-proposals.csv`** lists changes the check proposes, such as unit ids, fp acres and re-found record ids.
  - It has `answer` and `answered_by` columns, and an answer written there is carried over each night.
  - Decisions still go into an inbox batch; Quality applies them to the sheet.
- **Overrides still win:** `data/us-key/overrides.json` `no` (by id or name) / `join` (Brandon's decisions) always beat this sheet.

**Seed of Nov 3, 2026, fixed after Quality's grade (S1–S4).** Every row is PROPOSED. Each row rests on a YES (a hand-join audit KEEP, a Quality YES on the approved list, a person's YES in the key, or the drops-27 ruling), and none is signed yet.

`US-new-rows-for-Quality.csv` holds US-13606 Bullock Pen and US-13607 Boltz Lake. They are new rows for Quality to grade, and their record ids are not this layer's OBJECTIDs.
