# Park pages, part 4

## What is NOT built

- The other club bots are still not wired to the not-sure list.
- Nothing was pushed to `tools-out` or `main`, and no workflow was started.
- The workflow file did not change.
- No answer key is in this pull request, in a kit folder, or in the pull request body.
- The hand-off 04 answer key on `tools-out` was not opened.

## What is built

`kits` takes parks whose questions are still open (a bot asked, and no person has answered) and writes two blind passes, `pass1` and `pass2`. The same parks are in a different order. Each card has the park number, POTA's name, type, and link, and the same questions as the person page. Four to eight plants are mixed in unmarked when that many known answers exist (a person's row, or a `must` row in `known-answers.json`). Fewer known answers means fewer plants, and the count is in the key only.

The key is written to `kit-keys/key.json`, which the command refuses to place inside the kit folder. `score` prints how many parks the two passes agreed on, how many differed, and how many plants both passes matched.

## Tests

`tests/test_park_pages_kits_nov19.py` prints 7 PASS lines and ends ALL PASS. The two passes hold the same parks in a different order. A plant's answer text is not in either pass. The key file is outside the kit. Score counts an agreement and a difference.

## Guesses

- A person who ticked "could not tell" has not answered, so that park can still be in a kit.
- When fewer than four known answers are on hand, the kit uses all of them instead of inventing plants.
- A plant from `known-answers.json` is judged on the fields that row actually states (combined, inside, name). Empty fields are not judged.
- Pass 2 is shuffled with a different seed. If that shuffle lands in the same order as pass 1, the list is reversed.
