# Park pages, part 5 (review)

## What is NOT built

- No new reader, worklist, person page, or kit. Those stay as in parts 1 to 4.
- Nothing was pushed to `tools-out` or `main`, and no workflow was started.
- The workflow file did not change.
- No bot is on the list of settlers. That list stays empty until a reviewed rule names one.

## What changed

Three items from the review of 19 Nov 2026.

1. `tests/test_pdf_finder_nov17.py` check 9 no longer reads a git diff. It pins a sha256 of `kpc_manners.py` and of `kpc_host_rules.py`: `frozen: <sha>, reviewed by Fable, 19 Nov 2026`. The check runs with no `origin/main`. A later edit has to change the pin in the same pull request.

2. Pictures. Each one counts against `--max-requests` and stops at `--max-minutes`. A picture is taken only when a question is still open for a reviewer or a person, or the park has no official outline (`pin` in the key). Information-only codes, including `SHARED_PAGE` and `COMBINED_BOTH_NUMBERED`, do not get a picture. If the page has no map part, `browser_picture` returns nothing instead of a shot of the whole window. A saved picture is noted on the park's facts (`picture.file`), the summary counts those notes, and `intake` deletes that file when a person answers.

3. `settle` refuses an empty who, an empty how, the name "park page reader", and any bot, because the bot list is empty. A person or the reviewer can still settle, and only with both a name and a how. One test covers each refusal.

## Tests

`tests/test_pdf_finder_nov17.py` ends ALL PASS, including the two frozen lines. `kpc_not_sure.py --selftest` ends SELFTEST PASS, with the four settle refusals. `tests/test_not_sure_nov19.py`, `tests/test_park_pages_nov19.py`, `tests/test_park_pages_kits_nov19.py`, and the reader selftest end ALL PASS / SELFTEST PASS.
