# Park pages, part 1

## What is NOT built

- No worklist, no by-hand workflow, no `summary.md` for a chat to fetch later. That is part 2.
- No list-drop folder, no `changes.csv`, no `evidence-drafts/` files, no `questions.csv`. A draft row is carried on the fact. It is not written to a file of its own yet.
- No PC launcher, no person page, no intake. That is part 3.
- No blind kits. That is part 4.
- No change to a key, a rule file, a saved answer, an outline, a schedule, or a site page.
- No geocoder, no search engine, no `api.pota.app`, no keyed API.
- No map file saved. No picture was taken. `browser_picture` exists and returns nothing unless `BROWSER=1`, and this part never set that.
- The truth checker's stored size is loaded with the other stored files and is not yet preferred over a fresh read. Part 2's refresh rule is the place for that.
- `gov_of` does not know `alapark.com` or `arkansasstateparks.com`. Those hosts stay unofficial. I did not add them to the documents bot's list.
- `tests/test_pdf_finder_nov17.py` check 9 used to fail any diff in `kpc_manners.py` against main. It now allows only the picture function this hand-off asks for, and still fails any other manners edit and any host-rules edit.

## What is built

`kpc_park_pages.py read` and `--selftest`, and `kpc_park_pages_rules.py`. One park's facts from the page text, with a quote, or silence. Offline tests in `tests/test_park_pages_nov19.py`. Trimmed fixtures from pages opened by hand, plus the Red Cliffs text the owner saved.

Every must row in `known-answers.json` comes out of its fixture. Wrong facts on those rows: 0.

## Accuracy

The test prints this table. Silent means the reader stored nothing rather than guess. A correct negative (the river is one kind, Red Cliffs has no size) is not counted as silent.

| Block | Fixtures | Expected | Found | Wrong | Silent |
|---|---:|---:|---:|---:|---:|
| name | 4 | 4 | 4 | 0 | 1 |
| combined kind | 10 | 10 | 10 | 0 | 0 |
| inside_of | 1 | 1 | 1 | 0 | 1 |
| sizes | 4 | 4 | 4 | 0 | 1 |
| coordinates | 2 | 2 | 2 | 0 | 2 |
| address role | 2 | 2 | 2 | 0 | 1 |
| tracts | 3 | 3 | 3 | 0 | 1 |

Must rows checked: Denali, Gates of the Arctic, Katmai, Lake Clark, Wrangell-St. Elias, Craters of the Moon, Glacier Bay (preserve US-0029), Great Sand Dunes (preserve US-8295), Aniakchak (shared, preserve US-0003, page fetched once), the Aniakchak river (one kind, second address noted and not opened), Red Cliffs, Laurel's three tracts, the empty ArcGIS app, the Idaho Fish and Game front page (zero requests), the colorado.com article (no size, no inside), Custer Gallatin (no park point, office address, no pin-far question). The address-facts marker and center match, and that test makes no request.

Denali's labelled sizes from the statistics page: Park 4,740,091 acres, Preserve 1,334,118 acres. The 2,146,270 wilderness acres are stored with the label Wilderness and are not a total. The 1917 figure 2,146,000 is kept and is not a total.

## Gate

The park-page test prints 52 PASS lines and ends `ALL PASS`. The reader's own `--selftest` prints 16 PASS lines and `SELFTEST PASS`. Both are PASS in the full gate.

The gate on this machine does not end GATE PASS. Last lines:

```
TOTAL tests: 99/130 pass; with selftests: 109/148 pass; NEW failures: 33 -> GATE FAIL
```

Those 33 are not from this part. I did not change those files. They fail here for a missing module (`cv2`, `requests`, `pytest`, `kpc_key_rules`), for no KPC-Links checkout, or because a workflow test compares this main with an older snapshot. The same failures are not listed in `tests/known-fail-main.txt`, so the gate calls them new. `tests/test_pdf_finder_nov17.py` passes. Its check 9 still refuses a host-rules edit and any manners edit other than `browser_picture` next to `browser_text`, which this hand-off requires.

There is no workflow in this part, so the three review items (the file loads, `gh` steps and their tokens, read-only except one save job) are not in this pull request. They are part 2.

## Guesses

- KPC-Data has no stored state box. A point is kept when it sits in a small built-in state box or within 300 km of the pin. A point that fails both is dropped.
- `core()` leaves the word "management" and does not strip BLM, WMA, NWR. The reader strips those agency letters, then "management", then calls `core()`. Otherwise every BLM name reads as differs. The truth checker's `core()` is unchanged.
- A heading that is only "Welcome to …" or a title that is only "Home | …" loses that chrome before the names are compared. The raw title is still stored.
- "Corner" counts as a tract word because the rule's own Laurel example names Ralph's Corner. The suffix list in the rule text does not include it.
- `sizes_in` marks "including 2,146,270 acres of Federally-designated Wilderness" as total-looking, because words sit between "of" and "wilderness". The label step marks that included figure as a part, not a total. The park figure beside it keeps the label Park.
- `sizes_in` does not see "2.4-million-acre" or "3+ million acres". The reader keeps those phrases, not clean, and does not turn "3+" into 3 acres.
- `map_score` returns -9 for `experience.arcgis.com` (it treats that host as a viewer). The link is still listed as a web map, with that score, and it is not opened. R-PR8 says a map app is a map link.
- An ordinary "managed by" goes to the manager. Status words are the closed, handover, and renamed patterns. A current "managed by" is not a closed-or-moved question. Red Cliffs would have one on every run if it were.
- A shared NPS page: a park whose kind is not in the heading (the river on the monument page) does not inherit the heading's combined name.
- The first 404 is remembered. "The link does not open" is asked only when a second 404 is at least seven days later.
- A page under 400 characters of visible text is treated as script-built. The fixtures are padded with a footer so a trimmed real page is not mistaken for an empty shell. The empty ArcGIS fixture is left short.
- The saved Red Cliffs text has the words "View Map In Full Screen" and the PDF address, and not the experience.arcgis.com href. The manifest attaches the address the owner pasted as that link. The must row does not depend on it. The coordinate block does, and it makes no request.
- Center is 0.09 km from the pin by haversine. The worked example writes 0.08.
- Quotes longer than 200 characters are cut at a comma or a word when the sentence itself is longer than 200.

## Addresses opened by hand

Opened in a browser fetch, then trimmed. The bot did not fetch these.

- https://www.nps.gov/dena/index.htm and https://www.nps.gov/dena/learn/management/statistics.htm
- https://www.nps.gov/gaar/index.htm
- https://www.nps.gov/katm/index.htm
- https://www.nps.gov/lacl/index.htm
- https://www.nps.gov/wrst/index.htm
- https://www.nps.gov/crmo/index.htm
- https://www.nps.gov/glba/index.htm
- https://www.nps.gov/ania/index.htm
- https://www.nps.gov/grsa/index.htm
- https://www.nps.gov/tapr/index.htm
- https://www.nps.gov/jela/index.htm
- https://www.nps.gov/neri/index.htm
- https://www.nps.gov/orca/index.htm
- https://www.fs.usda.gov/flathead
- https://www.fs.usda.gov/main/custergallatin/home
- https://www.fws.gov/refuge/wichita-mountains
- https://www.nwk.usace.army.mil/Locations/District-Lakes/Perry-Lake/
- https://www.alapark.com/parks/bucks-pocket-state-park

Not opened again: https://www.blm.gov/visit/red-cliffs-recreation-area. The owner's saved text is the fixture.

The live headlines match the must rows. Denali, Gates of the Arctic, Katmai, Lake Clark, Wrangell-St. Elias, Craters of the Moon, Glacier Bay, Great Sand Dunes, and Aniakchak all join a park or monument with a preserve. Jean Lafitte joins with "and". New River Gorge and Oregon Caves join with "&". Tallgrass Prairie National Preserve is the heading, and the page says "nearly 11,000 acres". Flathead says "2.4-million-acre". Custer Gallatin's only address is the supervisor's office in Bozeman. Wichita Mountains is a refuge page with an about link and an acre sentence. Perry Lake gives land acres and water acres separately. Buck's Pocket has a street address and no acre total; a nearby line names the Walls of Jericho Forever Wild Tract, which the reader does not take as this park's tract.

## What in the hand-off did not match the code

- `map_score` refuses `experience.arcgis.com`. The worked example still lists that link. Both are kept: the score, and the link, not opened.
- `sizes_in` does not treat "acres of Federally-designated Wilderness" as a part, and it does not parse "2.4-million-acre".
- `gov_of('idfg.idaho.gov')` matches because the pattern `[a-z]{2}.gov` fits the tail "ho.gov". The host is still a .gov host, so the front-page rule is what matters, and it fires.
- There is no area-box table in this repo. The hand-off tells the reader to use one.
- `sample-data/truth-rows.json` is 42 KB. The page fixtures are each under 15 KB. The whole fixture folder is about 105 KB.
