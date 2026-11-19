# Review packet bot, PART 2: catch-up for a new session (Kentucky Portable Club, 19 Nov 2026, 12:30 PM CST)

You are picking up a job another session started. It is gone; this folder holds everything it knew. Read this page, then
`instructions/2-PART-2-ADDITIONS.md` (your actual task). `instructions/1-ORIGINAL-HANDOFF-03A.md` is the first brief: read its
"House rules" section, they still apply word for word.

Everything is public: github.com/KentuckyPortableClub/KPC-Links (website + key builders) and github.com/KentuckyPortableClub/KPC-Data
(data + bots; branch `tools-out` holds tool outputs).

## Where things stand
- **Part 1 is DONE, merged and accepted.** It lives on KPC-Data `main`: `.github/workflows/kpc-key-review-packet.yml`,
  `.github/scripts/kpc_key_review_packet.py`, `tests/test_key_review_packet_nov19.py` (copies in `part1-code/`). Given a KPC-Links
  pull request, it builds the touched states twice (old and new) on GitHub's runners and writes a packet to `tools-out`
  `key-quality/review-packets/pr-<n>-<sha>/`. Two real runs, both green and both matching hand-made figures: `example-packets/`
  (pull request 278: five parks in Alaska and Idaho; pull request 285: one park in Montana).
- **Part 2 is NOT started.** Add a mode `run` to the SAME script and workflow (no new bot): after a full US key run, compare the
  run's files with the published key, state by state, with NO builds. The brief and the five additions are in
  `instructions/2-PART-2-ADDITIONS.md`; addition 1 (shrinks) and 2 (new land) matter most.

## Lessons from part 1's review (do not repeat them)
The club's reviewer sent part 1 back twice before it was merged. In your part 2 code:
1. No key written twice in a workflow step (GitHub refuses the whole file). Keep the test that loads the workflow strictly.
2. Every step that calls `gh` gets `env: GH_TOKEN: ${{ github.token }}`, and NO step that runs code from a KPC-Links tree holds a
   token (download in its own step, or run with `env -u GH_TOKEN -u GITHUB_TOKEN`).
3. Least privilege: top level `permissions: contents: read`; only the final `save` job writes, and it runs no KPC-Links code.
   No `actions: write` anywhere (uploading a run file does not need it).
4. REST field names (`created_at`, not `createdAt`).
5. Never red, by hand only, writes only under `key-quality/review-packets/` on `tools-out`.

## Two things that changed since the brief was written
- The release asset `key-held.tar.gz` was replaced by a later key run. For the known-answer test use the saved copy in
  `known-answers/key-held-run-44528656941.tar.gz` (also on `tools-out`, `key-quality/2026-11-19/factcheck-run-44528656941/`).
  In the live `run` mode, read whatever `key-held` holds and record its date in `inputs.json`.
- Idaho and Oregon were saved to main at 11:16 AM (17:16 UTC) on 19 Nov. For the known-answer test use OLD = KPC-Links
  `data/us-key` at `8140d35` and NEW = `data/us-key` at `d5ae6ad3` with the saved tar laid over it, exactly as
  `2-PART-2-ADDITIONS.md` says; do not use today's main.

## Known answers (in `known-answers/`)
- `held-states-every-changed-park.csv`: every changed park of the 13 held states, with old and new union acres (shrinks: 60 parks
  at 20%+; measured on a grid, so allow 2%).
- `held-states-records-added.csv`: the parks that gain records (new land 100+ ac: ID US-10429, ID US-0890, AR US-7184, MT US-0054).
- `lost.json`: the 126 parks that lost their outline in that run, with the cause.

## How to test, and what to send back
- You may not be able to fork or run jobs on the club's repos. Then test OFFLINE: check out the two commits of KPC-Links and the
  tar, run your script's `run` mode on your own machine against them, and compare with `known-answers/`. Say in NOTES what you ran
  and what matched.
- Send back a DRAFT pull request to KPC-Data from a new branch (`prep/key-review-packet-part2`), or a zip of the changed files in
  their repo paths. Do not merge anything and do not start any workflow on the club's repos: a club session reads it first.
- A short NOTES file: what you built, the offline test and its numbers against the known answers, anything left undone or unsure.
