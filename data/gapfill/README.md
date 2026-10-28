# Gap filler: leads for the parks with no outline

Brandon (Oct 28 2026): "a bot that will look at our scoreboard and find the info to fill it in."
This folder is what that bot (`.github/scripts/kpc_gapfill_bot.py`, workflow `kpc-gapfill.yml`) writes. **Leads only.**
Nothing here goes into a key, an outline or a card by itself: chat 2 (keys) and chat 8 (research desk) read it and decide.

## What the bot does
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
GitHub → Actions → "KPC gap filler" → Run workflow: `areas` (blank = next in queue), `chunks` (55-minute chunks, max 5),
`chain` (how many more jobs may follow by themselves). Test on one state first (RULES FIRST): `areas = US-KY` or `US-NV`.
No web here: `python3 .github/scripts/kpc_gapfill_bot.py --selftest` checks the name judgment, the sure rule and the missing counts.

ℹ️ Maps and park info are a planning aid, not a guarantee. Always check the official agency map and rules before you go.
