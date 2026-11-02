# The park-info engine: how it is installed and run (chat 10, Nov 1 2026)

**What it is.** The outside coder's "do it all" engine (spec: KPC-Links `.claude/build/research/KPC_10_Engine_Spec.md`):
- it builds a nightly MISSING list per park and kind;
- it works agency by agency;
- it reads sites politely (plain read → structured data → browser → blocked log);
- it keeps one shared findings log;
- it does 2 passes.

Plug-ins: outline, map, page, parking, camping, trail, and Kentucky-only hours / fees / closures.

**Where it goes.** Put the engine folder in `.github/scripts/draft/tools/kpc_engine/` (with `kpc_engine.py`, `requirements.txt`, tests). Nothing else is needed: the workflow `kpc-engine.yml` finds it by itself.

**How it runs.**
- **First 24 hours** after the folder lands: every 3 hours (Brandon Nov 1 4:37 AM, "leave test running 24 hours").
- **After that:** nightly at 04:07 UTC.
- **Each run:**
  1. pulls the drop-off files (intake reader: hardlook, camping, parking, docs, portals, acres, layers);
  2. builds Kentucky in the club's shapes;
  3. runs the engine's `--selftest`;
  4. runs the areas (default `US-KY,US-TN,US-RI,CA-ON,CH`) for 50 minutes, chaining with `--resume` until done.
- Never red: one status-board line per run ("Park-info engine").

**Command line it is called with:**
`python3 kpc_engine.py run --areas <steer areas first, then US-KY,US-TN,US-RI,CA-ON,CH> --data . --links ../links --out ../out/engine --cache .engine_cache --max-minutes 50 --resume` (v0.4.0; the 2 big registry files come from branch engine-registry)
If the engine's own options differ, change the one line in `kpc-engine.yml`.

**Inputs it can read** (all read-only):
- KPC-Data `data/` (keys, parkinfo, docs, access, campsites, camp lists, pota tiles);
- KPC-Links: `kpc-ky-data.json`, `ky-*.geojson`, `data/ky-answer-key.json`, `data/world-key/`, the Agency Atlas, `world_agencies.json`;
- `../prep`: Kentucky as `parkinfo/US-KY.json`, `access/US-KY.json`, `outlines/US-KY.geojson`;
- the drop-off copies in `data/intake/_in/<kind>/`, including the Mapping agent's bundle.

**Outputs.**
- **Where:** everything goes on the side branch `tools-out`, folder `engine/` (BRANCH FIRST): `board.md` plus one file per kind, in the club's own file shapes.
- **Board copy:** `board.md` is copied to `data/status/engine-board.md` for the Bot Control Panel.
- **Nothing goes live from here.** Chat 10 moves each kind into its usual folder through the waiting room, and chat 11 grades it (bars: KPC-Links `.claude/build/research/KPC_10_Grading_Bars.md`). A kind that passes 3 times in a row then releases its own PASS files, with chat 11 checking 1 in 10.

**Steering (Brandon).** Open an issue in KPC-Data with the label `engine-steer` and a title like `steer: US-TN trail` or `steer: NZ outline`. The next run puts those areas and kinds first (`data/engine/steer.json`). Close the issue to stop. The bot never comments on these issues.

**Rules it must keep:**
- **Official sources first.** WDPA is a last resort only (rule W-10): APPROXIMATE, credit shown, never stored or downloadable.
- **Never:** OpenStreetMap, Google, AllTrails, Wikipedia geometry, sign-in layers, tokens hidden in public maps, getting around robot checks.
- **Pins:** POTA pins never move. R-G12: a record just outside the pin = a candidate. R-G13: pin typos are listed, not fixed.
- **Kentucky only:** hours / fees / closures.
- **Bots:** 2 s per host, at most 2 jobs on one agency host.

**Switch-over** (after chat 11 passes a kind): documents → parking → camping → outlines (after Nov 6) → Kentucky hours / fees / closures last. For each one: a side-by-side run with the old bot, chat 11 grades it, then the old bot retires.
