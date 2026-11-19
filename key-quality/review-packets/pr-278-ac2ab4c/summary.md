# Review packet for KPC-Links pull request 278

New side: commit ac2ab4c80723. Old side: commit 8140d35e1492 (the shared starting point, so later unrelated edits stay out).
New scope entries: 2026-11-19-r-pp1-park-preserve.
The states were typed in by hand.
This report only compares. It does not change a park.

| state | parks changed | outlines old -> new | verified old -> new | verified outlines lost | verified got worse | hard flags old -> new | notice lines only in NEW |
| ----- | ------------- | ------------------- | ------------------- | ---------------------- | ------------------ | --------------------- | ------------------------ |
| AK    | 4             | 135 -> 135          | 100 -> 100          | 0                      | 0                  | 10 -> 10              | 1                        |
| ID    | 1             | 227 -> 227          | 86 -> 85            | 0                      | 1                  | 8 -> 9                | 1                        |
| CO    | 0             | 266 -> 266          | 155 -> 155          | 0                      | 0                  | 40 -> 40              | 1                        |

Parks whose joined records changed (5):
- US-AK US-0026 Gates of the Arctic National Park: lost 3301 Gates of the Arctic National Preserve (945247 acres). Outline acres 8224560 -> 7279313.
- US-AK US-0044 Katmai National Park: lost 3304 Katmai National Preserve (328054 acres). Outline acres 3952224 -> 3624170.
- US-AK US-0048 Lake Clark National Park: lost 3305 Lake Clark National Preserve (1249676 acres). Outline acres 3737532 -> 2487856.
- US-AK US-0069 Wrangell-St. Elias National Park: lost 3314 Wrangell-St. Elias National Preserve (4334094 acres). Outline acres 12284251 -> 7950157.
- US-ID US-0665 Craters of the Moon National Monument: lost 3299 Craters of the Moon National Preserve (411913 acres). Outline acres 466077 -> 54164.

Verified outlines lost: none
Verified got worse: US-ID US-0665 (verified -> flagged (the pin is 22.7 km outside the nearest piece))

Notice lines only in the new build:
- US-AK R-PP1 park and preserve: 7 record(s) to check: US-0003 Aniakchak National Monument, US-0026 Gates of the Arctic National Preserve, US-0029 Glacier Bay National Park, US-0044 Katmai National Preserve, US-0048 Lake Clark National Preserve, US-0069 Wrangell-St. Elias National Preserve, US-0902 Aniakchak National Preserve
- US-ID R-PP1 park and preserve: 1 record(s) to check: US-0665 Craters of the Moon National Preserve
- US-CO R-PP1 park and preserve: 2 record(s) to check: US-0033 Great Sand Dunes National Preserve, US-8295 Great Sand Dunes National Park

Notice lines only in the old build: 2 (see notices-only-old.txt).

Gold score: the TUNE line and the SEALED line are the same on both sides.

Files here: parks-changed.csv, factcheck-diff.csv, notices-only-new.txt, notices-only-old.txt, gold-old.txt, gold-new.txt, inputs.json.
