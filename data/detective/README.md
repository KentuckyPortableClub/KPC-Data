# Park detective: answers to park questions + leads for the parks with no outline

Brandon (Oct 28 2026): "a bot that will look at our scoreboard and find the info to fill it in" and, the same morning, "a bot dedicated to
finding missing park information like Boiling Springs … use the bots when we can; if it and chats 11 and 8 can't find it, then I look."
This folder is what that bot (`.github/scripts/kpc_detective_bot.py`, workflow `kpc-detective.yml`; `kpc_gapfill_bot.py` /
`kpc-gapfill.yml` are shims that run it) writes. **Leads and answers only.**
Nothing here goes into a key, an outline or a card by itself: chat 2 (keys) and chat 8 (research desk) read it and decide.

## A. Questions (the detective proper)
Any chat or HQ adds a row to `questions.json`: `{id, ref, park, area, what, note, added, by}` with `what` = outline · tract · acreage ·
owner · who runs it · handover · access point · free text. Put the question's own words in `note` (a tract name such as "Timber Lane",
a number such as 115.75): the bot matches them in pages and PDFs. Every official source in ORDER, stopping at the first answer:
1. our layers (point query at the pin) → 2. the agency's park page + its PDFs (brochures, management plans, land-acquisition reports
such as Kentucky's KHLCF annual reports; `sources.json` `reports` rows are the index pages per area) → 3. the state open-data portal →
4. PAD-US at the pin (owner / manager / acres) → 5. county PVA / parcel sites (`sources.json` `parcels` rows) ONLY where robots.txt and
the page's own terms allow a bot (never accept terms, never log in; a terms or sign-in wall = "blocked by terms") → 6. the agency's news
releases (`data/truth/news-sources.json`).
Answer = `{fact, line (the source's own sentence, ≤ 240 chars), url, date, step}` or "not found" + what was tried, in `answers.json` +
`answers.md` (answered first, then not found). Unanswered → chats 8 / 11 → Brandon. A question is answered once per id (ask again with a
new id); a question whose hosts did not answer is retried next run.
Test case: `US-12752` Green River State Natural Area (Boiling Springs unit): the KHLCF "Timber Lane … 115.75" tract line and the OKNP page;
the Hart County PVA parcel may come back "blocked by terms" (that is fine).

## B. The gap filler (missing outlines)
For every park on the scoreboard that still has no outline (`data/review/scoreboard-parks.json` rows with `outline: missing`;
until that file exists, the keys: `data/us-key/US-XX.json` + `data/ca-key/CA-XX.json` parks with no `m` records that are not
pin-only or line kinds; Kentucky from KPC-Links `data/ky-answer-key.json`), at most ~8 polite requests, stopping at the first sure find:

1. **Layers we already read** for that state / province (KPC-Links `data/state-gis.json`, `data/us-key/layers.json`,
   `data/ca-key/layers.json`): one point query at the POTA pin per layer. A polygon under the pin whose name shares the park's
   words = *likely a name mismatch in our matcher* (both names listed for chat 2). A different name = *different land under the pin*.
2. **The managing agency's own ArcGIS**: its ArcGIS Online org (search for the park's name) or its ArcGIS Server folder list
   (park / land / boundary / recreation services), then one point query per candidate layer (at most 3).
3. **The state open-data portal** (ArcGIS Hub search), keeping only datasets whose publisher reads like the state's own agency.
4. **USGS PAD-US** at the pin: reported (unit name, manager, designation, acres, category). Proclamation and Easement records are
   never offered as an outline.
5. Nothing → *no official layer found* with the list of what was tried.

**Sure** = YES only by the house rule: pin inside + name words match + similar size when both sizes are known (within 25%).
Everything else is **check**. A park checked within 30 days is skipped. A park whose hosts did not answer is tried again next run.

## Files
- `questions.json` (the queue), `sources.json` (report index pages + parcel sites per area), `answers.json` + `answers.md` (the answers).
- `<area>.json`: `{area, about, read, counts, parks: {ref: {n, t, la, lo, a, tried, finds, find, sure, verdict, why}}}`.
  `find` = the best find (the layer url, publisher, licence + date from the ArcGIS item when it names one, the polygon's name and
  acres against ours, pin inside, sure). `verdict` ∈ sure · padus · mismatch · check · different · nothing.
- `review.md`: per area, the layers found sorted by the parks each would close; the name-mismatch list for chat 2; the PAD-US name
  matches; the 'no layer found' count.
- `state.json`: per-area status (queue order: KY NV ID MS WA UT AR OR NC, the rest of the US in the truth checker's order, then
  ON QC NB NS, the other provinces), resting hosts, the last chunk's numbers, and `proven` (set by hand after Brandon's GO: the weekly
  Monday run only works once it is there).
- One row per layer found is **appended** to `data/intake/queue.json` for the intake bot
  (`{url, area, title, publisher, licence, from: 'gap-filler', added, note, closes: [refs]}`, de-duplicated by url).
- One 'grade me' line per area batch goes to chat 8's inbox (`kpc_status.py`), and the bot board gets a line per job.

## Running it
GitHub → Actions → "KPC park detective" → Run workflow: `areas` (blank = next in queue), `chunks` (55-minute chunks, max 5),
`chain` (how many more jobs may follow by themselves), `jobs` (`questions gaps`, any subset). Test on one state first (RULES FIRST): `areas = US-KY` or `US-NV`.
No web here: `python3 .github/scripts/kpc_detective_bot.py --selftest` checks the fact-word extraction, the name judgment, the sure rule and the missing counts.

ℹ️ Maps and park info are a planning aid, not a guarantee. Always check the official agency map and rules before you go.
