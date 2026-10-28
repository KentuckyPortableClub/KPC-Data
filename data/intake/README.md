# Layer intake line (data/intake)

One queue for every map-layer lead anyone finds; one polite bot (`.github/scripts/kpc_intake_bot.py`, workflow `kpc-intake.yml`) probes each lead and writes a verdict a person can act on. Metadata and counts only: no geometry is ever stored here.

## Files
- `queue.json`: the leads. Anyone (harvester, discovery bot, gap-filler, chat 8, chat 9) adds a row; the bot never edits rows.
- `ready.json`: one result row per probed layer (`approved: null` until chat 9 decides).
- `review.md`: the human page: verdict counts, READY rows first with the parks each would close, then LIVE-ONLY, ASK, REJECT; the test table + `GATE=PASS/FAIL` at the end.
- `state.json`: resume data (per url: date probed + a signature of the queue row), resting hosts, last stats.

## Queue row
```json
{"url": "https://host/arcgis/rest/services/X/FeatureServer/0", "area": "US-KY", "title": "what it is", "publisher": "who",
 "licence": "licence text if known", "from": "harvester | discovery | gap-filler | chat 8 | chat 9", "added": "2026-10-28",
 "note": "why it is here", "expect": "READY or already read"}
```
`area` = `US-XX`, `CA-XX` or a country code (`GB`). A service url without a layer number is split into its polygon layers. `expect` is only for known-answer test rows. A row probed within 30 days is skipped unless its text changed.

## Verdicts
- **READY**: official publisher + OPEN / CREDIT / NON-COMMERCIAL terms + named polygons + closes at least one park with no outline (or a chat 8 / 9 request).
- **LIVE-ONLY**: official, but the terms say viewing only / no redistribution: read live, never stored.
- **ASK-THE-PUBLISHER**: official but nothing stated about use, or hosted for an agency on another account (a university), or the publisher is unsure.
- **REJECT**: not official, no polygons, no name field, already read (`overlap: already read as <id>`), closed terms, or did not open.
Every row carries WHY plus the measured facts: fields, geometry, name field, record count, last edit, extent, terms class + the line that decided it + where it was read (item page / service / queue row), owner / org, overlap, and `closes` {n, by_name, pin_only, parks}.

Terms classes: OPEN (a named open licence) · CREDIT (copyright / credit / disclaimer with no use limits: usable with the credit line, HQ Oct 27) · NON-COMMERCIAL (fine for the club with the credit) · LIVE-ONLY · NOTHING STATED · CLOSED.

## How chat 9 approves
1. Read `review.md` (READY first).
2. In `ready.json`, set `"approved": true` on each row to take (optionally add `"approved_note": "..."`). A re-probe keeps the yes while the verdict holds.
3. The nightly key rebuild reads approved rows later (not built yet). LIVE-ONLY rows are never stored, only read live.

## Running
Actions → "KPC layer intake" → Run: `rows` blank = every unprobed queue row, or a space-separated list of urls; `test` = yes prints the test table and GATE line. Nightly at 08:41 UTC it runs only when the queue holds unprobed rows. After a batch it writes a `grade me` line and the board via `kpc_status.py`.
