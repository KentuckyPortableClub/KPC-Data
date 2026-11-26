# Review packet for KPC-Links pull request 286

New side: commit de445bad381a. Old side: commit 576388b47d77 (the shared starting point, so later unrelated edits stay out).
New scope entries: 2026-11-19-r-pp1b-preserve-with-park.
The states were typed in by hand.
This report only compares. It does not change a park.

| state | parks changed | outlines old -> new | verified old -> new | verified outlines lost | verified got worse | hard flags old -> new | notice lines only in NEW |
| ----- | ------------- | ------------------- | ------------------- | ---------------------- | ------------------ | --------------------- | ------------------------ |
| AK    | 4             | 135 -> 135          | 100 -> 100          | 0                      | 0                  | 10 -> 10              | 2                        |
| CO    | 0             | 266 -> 266          | 155 -> 155          | 0                      | 0                  | 40 -> 40              | 0                        |
| ID    | 0             | 228 -> 228          | 87 -> 87            | 0                      | 0                  | 8 -> 8                | 0                        |

Parks whose joined records changed (4):
- US-AK US-0022 Denali National Park: gained 3300 Denali National Preserve (1311169 acres). Outline acres 4680746 -> 5991915.
- US-AK US-0026 Gates of the Arctic National Park: gained 3301 Gates of the Arctic National Preserve (945247 acres). Outline acres 7279313 -> 8224560.
- US-AK US-0044 Katmai National Park: gained 3304 Katmai National Preserve (328054 acres). Outline acres 3624170 -> 3952224.
- US-AK US-0048 Lake Clark National Park: gained 3305 Lake Clark National Preserve (1249676 acres). Outline acres 2487856 -> 3737532.

Verified outlines lost: none
Verified got worse: none

Notice lines only in the new build:
- US-AK R-PP1 park and preserve: 3 record(s) to check: US-0003 Aniakchak National Monument, US-0029 Glacier Bay National Park, US-0902 Aniakchak National Preserve
- US-AK NPS unit codes: 1 record(s) joined by the park's nps.gov code, 0 given back inside a shared unit: US-0022 DENA

Notice lines only in the old build: 3 (see notices-only-old.txt).

Gold score: the TUNE line or the SEALED line differs. Read gold-old.txt and gold-new.txt.

Files here: parks-changed.csv, factcheck-diff.csv, notices-only-new.txt, notices-only-old.txt, gold-old.txt, gold-new.txt, inputs.json.
