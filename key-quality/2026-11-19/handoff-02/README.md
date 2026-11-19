# Hand-off 02: missing layers, the hand-download list, the outside-agent zip (Opus, 19 Nov 2026; key-quality.md section 19 item 9)

## a. What the keeper asked for and what came in
- ASKED: 64 layers (144 layer-and-state rows), written by the KPC-Store keeper 18 Nov 17:30 UTC (store-data
  `store/layer-requests.json`; the public copy `layer-requests.json` is on the KPC-Links boundary-cache release). All 64 are SHORT
  ("the store holds N of the M records the key joins"). Biggest: FWS interests (27 of 2,016, 19 states), USACE recreation areas
  (41 of 129, 14 states), BLM recreation polygons layers 0 and 1, the Forest Service wild and scenic rivers, BLM recreation layer 9,
  NPS NRHP locations (0 of 22), NYS DEC lands (0 of 1,275), Wisconsin DNR (0 of 41,733), Florida state-owned lands (280 of 11,717).
- ARRIVED: 0. The cache side that answers them (KPC-Links kpc-geo-cache.yml, from_requests) last ran 18 Nov 01:16 UTC, before the
  requests; no saved copy on boundary-cache has changed since 18 Nov 01:20 UTC. 30 of the 64 a bot may read (one by-hand cache run
  from the requests); 34 sit on hosts the bots may not contact (services*.arcgis.com, apps.fs.usda.gov, ncnhde.natureserve.org): PC.
- STILL SHORT: 64.
- The keeper's park list (KPC-Data `data/keeper-asks/latest.json`, keeper run 44350357856, 18 Nov): 3,798 parks with no official
  record (2,179 US, 1,619 Canada). It exists, so ledger 92's proof is there; the tracers have not read it yet (T2 waits for the release).
- Master check, suspect baselines (19 Nov 10:10 run): US-CO.sgcoa (Colorado Parks & Wildlife, state wildlife areas, expected 200, the
  file held 324), US-OR.sgorf (BLM recreation SITE polygons, expected 200, held 2,153), US-WA.sgorf (WDFW wildlife area units,
  expected 200, held 228). A read cut off at 200 recorded the baseline; the next verified full read re-records it.

## b. `hand-download-list.csv` (592 rows, busiest parks first)
who: PC = Brandon's PC (bots may not contact the host; 487 rows. Rows from the needs-download list are already in the PC helper,
`python tools\kpc_pc_helper.py`; the keeper's 75 PC rows are not on that list yet). BOT = a bot can read it (81: one by-hand cache
run from the requests). AGENT = nobody knows the official source yet (24: hand-off zip job 1).
Columns: state, agency (host), layer, official page, the file to get, parks it serves (count + busiest five with activations),
why, source row. Downloads land as before: PC files through the PC helper (boundary-cache hand files); agent answers on KPC-Data
branch intake-files `key-quality/handoff-02/`.

## c. `handoff-02-kit.zip` (give this to the outside agent; no keys in it)
job 1 official sources (99 rows + 2 plants), job 2 second look 02 (Tillamook SF, Tallgrass Prairie, Timucuan, Craters of the
Moon, Longview Saline x2, Osage WMA US-6365, Acadia Cliffs US-9442, Diamond HMA US-10844 + 1 plant), job 3 the busiest 100
pin-only parks (+ 2 plants; #277's 13 parks left out), job 4 POTA's own pages for the R-PP1 five (+ 1 plant). The answer key is
`kit-keys/` here: NEVER give it to the agent. One agent is one grader: nothing becomes a saved answer from one pass alone.

## Fable's corrections, 19 Nov 8:20 AM CST
- "the keeper's 75 PC rows are not on that list yet" is WRONG for 31 of the 34 layers: they are on data/needs-download.json already.
- What the 487 PC rows are: 75 keeper rows (34 layers, one row per state) + 412 rows of the needs-download list, 405 of them added
  by the park-info engine on 11-12 Nov with no state. 410 distinct layers on 20 hosts that bots may not contact. Only 118 of the
  410 feed a park in the US key; 123 of the open rows repeat a layer whose state row is already DONE (downloaded 10-11 Nov).
  None is needed for the key release: the key already joins these records; the shortage is in the private outline store.
- NO hand download is uploaded before the release is signed off: a hand file on boundary-cache is merged by the next US key run
  and would change the shapes between the fact check and the release.
- The agent's answers: `answers-pass1/` (READ-FIRST.md there).
- CORRECTION (tested 19 Nov 8:35 AM): being on data/needs-download.json is NOT being in the PC helper. The 406 open rows have no
  state, so `kpc_pc_helper.py --list` shows 0 layers. What must happen first: key-quality.md section 19 item 16.
