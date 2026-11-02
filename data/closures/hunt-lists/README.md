# Hunt closure lists (one per state per season)
Brandon (Oct 29 2026, 12:08 AM): each state's hunting guide is written once a year and does not change, so the guide becomes a
CHECKED LIST that is the rule for that state until it expires (Kentucky: end of February, until the next guide comes out).
Chat 8 writes the list from the guide; Brandon checks it and sets `checked_by`; the closures bot uses ONLY a checked, unexpired list.

File: `<area>-<season>.json`, e.g. `US-KY-2026-27.json`:
```json
{"state": "US-KY", "season": "2026-27", "expires": "2027-02-28", "source": "<the guide's URL>", "made_by": "chat 8", "checked_by": "",
 "rows": [{"ref": "US-3793", "name": "Ballard WMA", "dates": "Nov. 7-8", "from": "2026-11-07", "to": "2026-11-08",
           "kind": "closed", "what": "deer quota hunt", "page": "<the area's own page or the guide>", "note": ""}]}
```
- `kind`: `closed` = closed to everyone except drawn hunters on those dates; `note` = the hunt happens, the area stays open.
- `checked_by` empty = the bot does not use the list (it says 'not checked yet').
- One row per park number and date range; a hunt on two parks = two rows.
