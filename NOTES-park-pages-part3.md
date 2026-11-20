# Park pages, part 3

## What is NOT built

- No blind kits. That is part 4.
- The other club bots are still not wired to the not-sure list.
- Nothing was pushed to `tools-out` or `main`, and the workflow was not started.
- The workflow file did not change, so the three review items are the ones already checked on part 2.
- The person page does not guess. Every answer box starts empty.

## What is built

- `tools/park-pages-pc/`: `run-park-pages.sh`, `run-park-pages.bat`, and `README-PC.txt` (ten lines). The launcher asks "Which state? (blank = continue the list)", prints plain sentences, and writes `park-pages-<date>.zip`. Errors go to `run-log.txt`.
- `pc-kit` builds that zip: the reader, manners, host rules, the rows for the named areas, and the state file. No secrets and not the whole repo.
- `person-page` writes one file, under 300 KB, with no network. One card per park the bot could not read: the park number, POTA's name and type, the link, and the five fields. Save downloads `person-answers.json`. Copy is there for a phone.
- `intake` folds a PC zip or `person-answers.json` into the facts. A person's row is stored with `by: "person"`, `who`, and `date`, and wins for that fact. The bot's row is kept as `bot_saw`. A disagreement is one row in `disagreements.csv`. A picture for that park is deleted once a person has answered.

## Tests

`tests/test_park_pages_person_nov19.py` prints 11 PASS lines and ends ALL PASS. Headless Chrome opened the page at 390 px: the scroll width was not wider than the frame, so it does not scroll sideways. The file the Save button builds loads in `intake`. The person name wins, the bot name is kept, and the picture file is removed. The PC kit contains Utah and not Alaska.

## Guesses

- "Could not tell" is stored and does not replace the bot's facts.
- A picture is deleted when a person sends any row for that park, including "could not tell", because a person has looked.
- The kit also carries the truth checker and the documents bot. The reader imports their size reader and their official-host test. Those two files are not the whole repo.
- A name that differs only by kind words is not a disagreement. The truth checker's core is used.
