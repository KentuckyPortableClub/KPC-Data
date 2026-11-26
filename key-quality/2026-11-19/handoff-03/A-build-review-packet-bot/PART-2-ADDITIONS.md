# Review packet bot, PART 2: go-ahead and five additions (Kentucky Portable Club, 19 Nov 2026, 11:40 AM CST; test inputs corrected 11:45 AM)

**Part 1 is accepted.** Run 44564132024 on KPC-Data (pull request 278, new `ac2ab4c8`, old `8140d35e`, states AK ID CO) wrote
`key-quality/review-packets/pr-278-ac2ab4c/` and it matches the hand figures on every row. Thank you. Build Part 2 now, as the
hand-off README describes it (mode `run`: OLD = KPC-Links `data/us-key` at a given commit, NEW = `data/us-key` at main with the
files of the release asset `key-held.tar.gz` laid over it; no builds; one row per state; folder
`key-quality/review-packets/run-<date>/`). Same rules as Part 1: a draft pull request to KPC-Data, by hand only, read-only except
the save job, never red, nothing started on the club's repos. A club session reads it, merges it and starts it.

**Why the additions.** The first table of a key run counted only outlines that were LOST. A park that keeps an outline but loses
most of its land was on no list (Custer Gallatin National Forest in Montana: 3.4 million acres down to 1.1 million, still
"verified"). The five checks below put those on the table. None needs the network beyond what Part 1 already downloads (the saved
shapes `US-XX.json.gz`); all compare OLD and NEW per park. Areas = the UNION of a park's joined records (`m` rows), never the rows
added up; shapely is fine in this mode (it is already installed for the fact check step). Keep a time budget per state and say so
in the packet when a park was skipped; never guess a number.

1. **Shrinks.** Every park with joined records on both sides whose NEW union is 0.8 x the OLD union or less: area, ref, name,
   activations, old acres, new acres, and the reason text of the check rows (`c`) for the records it lost. One count per state in
   the state table ("keeps an outline, loses 20%+").
2. **New land.** Every park whose NEW union holds 100 acres or more that the OLD union did not (and every park that goes from no
   outline to an outline): the acres added and the names of the records added. One count per state ("new land 100+ ac").
3. **An unused record under a dropped copy.** For every park with a check row whose reason starts `check (D7)`: is there a record
   of the SAME manager (`Mang_Name` of the park's joined records) that is joined to NO park of that state, lies under the dropped
   copy and outside the park's joined land, with 100 acres or more there and at least 5% of the copy? List park, record id, record
   name, acres under the copy.
4. **Acres added up.** For every park whose key says `ac_how: measured` and has two or more `m` rows: the key's `ac` beside the
   true union; list those where `ac` is 1.10 x the union or more.
5. **The agencies' own acres** (optional, only if 1-4 are done): the three tables on `tools-out`
   `key-quality/2026-11-19/kitC-acreage/answers/` (USFS Table 28 rows, FWS Table 3 rows, NPS). For a park whose manager and name
   match a row: list it when the NEW union is under 0.8 x the agency's acres. A name that does not match exactly is left out, not
   guessed.

**Known answers to test against** (OLD = KPC-Links `data/us-key` at `8140d35`; NEW = KPC-Links `data/us-key` at `d5ae6ad3` with the
held files of US key run 44528656941 laid over it. The release asset `key-held.tar.gz` was REPLACED by a later run at 11:16 AM on
19 Nov, so use the saved copy on `tools-out`: `key-quality/2026-11-19/factcheck-run-44528656941/key-held-run-44528656941.tar.gz`.
The 13 held states are AK AR DE FL GA ID MT NC OR RI UT VA WY; the hand lists are on `tools-out` `key-quality/2026-11-19/fable-sitting-3/`;
they were measured on a grid, so allow 2%):
- Shrinks: 60 parks in the 13 held states (AK 4, AR 10, DE 2, FL 8, ID 8, MT 15, OR 5, UT 3, VA 4, WY 1), among them MT US-0070
  2,187,128 -> 160,257; MT US-4501 3,399,571 -> 1,143,001; AR US-1091 35,540 -> 218. File `held-states-every-changed-park.csv`.
- New land: ID US-10429 +44,581; ID US-0890 +15,257; AR US-7184 +190; MT US-0054 a new outline of 196 (OR: 5).
- Unused record under a dropped copy: MT US-4501, record 2660 "Gallatin National Forest", about 1,900,000 acres under the copy.
  Over all 50 states it is the only clear one. File `d7-dropped-copies-160-parks.csv`.
- Acres added up: FL US-6321 67,913 against about 31,850; FL US-6328 189,872 against about 66,000; ID US-4500 2,117,033 against
  about 1,651,000. Over all 50 states: 116 parks, 84 of them 1.10 x or more. File `added-up-acres-116-parks.csv`.
- Agency acres: MT US-4501 at 38% of 3,040,112; MT US-0399 at 45% of 935,617.
If a number of yours differs by more than the 2%, say so in the notes and leave it as it came out. Do not force a match.
