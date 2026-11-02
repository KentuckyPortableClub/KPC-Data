# data/campsites: CAMP & ACTIVATE (which campground is in which park)

Written by `.github/scripts/kpc_campsites_bot.py` (workflow `kpc-campsites.yml`). Review lists only: nothing here is linked from the
site yet; the Activators Lounge campgrounds tab and the campground cards read it only after chat 8's grade and Brandon's GO.
Rules: RULE SHEET E + rulings CA-1..CA-6 (KPC-Links `.claude/notes/mapping.md`). Known answers: chat 8's Kentucky desk run
(`KPC_CampActivate_KY_desk.md`): the bot must match it 100% (GATE=PASS) and prints every difference.

## Files
- `<area>.json` (e.g. `US-KY.json`): `{area, read, counts, inside, both, line, nearby, check_first, no_point, dayuse, dispersed, merged, disagree, park_names}`
  - `inside`: `{ref: [{id, name, kind, agency, m_inside, booking, sites, tier: 'inside' | 'at the edge' | 'part inside', notes, outline}]}`: the point is inside the park's OWNED / MANAGED outline; `m_inside` = metres from the edge; 0-15 m = 'at the edge' (also in `check_first`).
  - `both`: `[{id, name, parks: [A, B], park_names, patch_id, patch_acres, patch_tier, booking, hunt_note, notice, show, hidden_for?}]`: 'camp here, activate both' = the point is inside a RULED 2-fer patch (data/fers status `candidate`, main + small tiers). `show` is false during a hunt closure (CA-5) or when two records disagree.
  - `line`: campgrounds within 100 ft of a line park's official line AND on public land.
  - `nearby`: `{ref: [{id, name, kind, miles, note?}]}`: outside the park, within 5 miles straight line of its edge (CA-3); never counts toward an activation. A park with no outline gets `note: 'no official boundary…'`; a geocoded street-address point gets `location approximate`.
  - `check_first`: members-only list with the reason (at the edge, rounded RIDB point, two records that disagree, hunt-area 2-fer with no dates, approximate outline).
  - `no_point`: name-only records (chat 9 finds the real points). `dispersed`: `{ref: note}` camping-info notes (CA-4). `dayuse`: shelters / picnic areas = day-use info, never camping rows (CA-2).
  - `merged`: same-name records within 1 mile joined into one row (RIDB point wins for federal, the state's for state). `disagree`: the list's park field vs the outline test (the outline wins).
- `review.md`: the human list in Sheet E rule 5's wording (⛺ rows, 📍 Nearby, both notices once, 'last checked', outline source label) + the Kentucky known-answer check (GATE=PASS/FAIL with the differences).
- `state.json`: per-area status, the Kentucky `test` result, `proven` (the date the gate first passed).

## Inputs (read, never written)
Campgrounds: Kentucky `data/campinfo/US-KY.json` (job 4's facts) + day-use rows from `data/campfed/US-KY.json`; other states `data/campfed`, `data/campstate`, `data/campstate-manual`.
Outlines: Kentucky = KPC-Links `data/ky-answer-key.json` tracts read from the `ky-*.geojson` layers (proclamation lines out; Daniel Boone = Forest Service-owned land); other states = the US key + the boundary-cache copies (`cache/us/US-XX.json.gz`, downloaded by the workflow; without them the area is a stub).
Patches: `data/fers/<area>.json`. Lines: `ky-sheltowee.geojson`, `data/trails/US-3791.json`, `data/trails/US-4572.json` (Pine Mountain's approximate line is kept out). Closures: `data/closures/<area>.json` (hunt closures hide 'activate both' for their dates).

ℹ️ Maps and park info are a planning aid, not a guarantee. Always check the official agency map and rules before you go.
⚠️ 2-fer rows: Parks' boundaries may overlap here, but we can't confirm it. Check both official boundary maps and make your own call before you count it.
