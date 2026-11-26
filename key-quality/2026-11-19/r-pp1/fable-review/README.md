# Fable's review of #278 (R-PP1), 19 Nov 2026: NOT YET, two changes (the comment on the PR has the verdict)
Checks made apart from the PR's own files, all on the PR's commit ac2ab4c:
- `exact-scan.txt`: the rule's own test (a joined row on a Park Service-managed record, not a person's, park and record disagree on
  'preserve') on the published key, all 50 areas, against the saved shapes: 442 such rows, the test is true for 8, all AK + ID.
- `scope-builds.txt`: the other 11 scope states built on the PR's rules (re-match on, offline). No R-PP1 line = the rule did
  nothing in that state. Colorado has one (Great Sand Dunes); `co-old-vs-new.txt`: 0 of 276 parks differ in joined records.
- `pins.txt`: POTA's own pin against the park record and the preserve record of the five parks (+ Denali).
- `changelog-gate.txt`: kpc_preflight.check_hash_pair on the PR's changelog line.
Limit: built in the chat box (default GEO_DETAIL, no shapely); the same on both sides, so the differences stand.
