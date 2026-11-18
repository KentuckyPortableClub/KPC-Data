# Key quality files, 18 Nov 2026 (read KPC-Links .claude/notes/key-quality.md first)

Made with KPC-Links `.github/scripts/kpc_key_factcheck.py` and `kpc_key_grade.py` on the US key as saved 18 Nov 5:44 AM CT.

- `factcheck-us/`  every US area: summary, one line per flag (busiest first), one file per area (gz).
- `held-states/`   the 17 states the drop guard held: fact check of main's key and of the would-be key, the 44 outlines the
                   would-be key lost (`lost-pick.json`), their blind line-ups (`kit/`), the answer key (`kit-keys/`: never
                   give this folder to a grader), both graders' answers, the score and the findings.
- `pilot/`         the first blind grade: 47 parks of the gold mix + planted answers, two graders, score, the one
                   adjudicated verdict.
- `samples/`       seeded picks for the real runs: 300 per method (random = the only kind a rate may come from), the 25
                   busiest per area, 300 targeted, the 400-park gold mix. Re-draw after a rebuild with the same seeds.
- `../gold-us.json` the gold set so far (61 parks: 49 TUNE, 12 SEALED). SEALED rows score finished builds only.
- `answers-check-nov18.csv.gz`, `ovr_facts.py`: the EARLIER check of the saved answers. It judged the raw file, not the
  key, and by name. A work list only (see the notes, section 0).
