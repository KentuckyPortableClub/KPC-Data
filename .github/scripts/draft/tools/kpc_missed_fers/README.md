# kpc_missed_fers: missed 2-fer finder (leads only)

**What it does.** It reads POTA's public activation history. It counts pairs of POTA parks that the same activator activated on the same UTC date, then lists the pairs where at least **3 different activators** did this on at least **3 different dates**. It drops rove days, meaning one activator with 5 or more parks on the same date. Each pair's pins must be no more than **15 km** apart, or the bboxes of official outlines no more than **2 km** apart. A pair is listed only if no file under `--fers` already has it. Each pair is routed to `fers-retest` (both outlines official), `check-official-map` (an outline is approximate or pin-only) or `trail-river` (either park is a trail or river). It **never adds a 2-fer**, and **callsigns never appear in the output**. In memory and in the cache, callsigns become salted-hash ids that are used only to count people.

**Endpoints (tested live with curl on 2026-10-31, no key needed):**
- `https://api.pota.app/location/parks/<location>`, e.g. `US-KY` → `[{reference, name, latitude, longitude, locationDesc, attempts, activations, qsos, ...}]`. KY has 193 parks.
- `https://api.pota.app/park/activations/<ref>?count=all` → `[{activeCallsign, qso_date: "YYYYMMDD", totalQSOs, qsosCW, qsosDATA, qsosPHONE, locationDesc}]`. It returns one row per **attempt** (US-0050 gives 698 rows = `attempts`), so the cache key is `attempts/activations`.
- `https://api.pota.app/programs/locations`: used only when `--areas` is not given. The default order is US, then CA, then the rest of the world in API order.
- `https://api.pota.app/robots.txt` answers 403 "Missing Authentication Token". Under RFC 9309 a 4xx means "no rules", so fetching is allowed. A 5xx or no answer closes the host for that run.

**Run.**
```
pip install -r requirements.txt        # nothing: stdlib only
export KPC_CONTACT="you@example.org"    # sent as User-Agent "KPC park tools (you@example.org)"
python kpc_missed_fers.py --areas US-KY,US-TN,US-VA --parkinfo data/parkinfo --keys data \
       --fers data/fers --cache cache/missed-fers --out out/missed-fers --max-minutes 50 [--resume] [--limit N]
python kpc_missed_fers.py --selftest   # offline, prints PASS or FAIL
```
Exit codes: `0` = done. `3` = time ran out (or api.pota.app went "resting" after three 429/503 retries) and work is left, so run again with `--resume`. Anything else = crash. A bad park is written to `problems` with a reason, and the run goes on. The tool sends at most 1 request every 2 s. A park's history is re-read only when its count changes.

**Output (only inside `--out`):** `missed_fers.json` holds one row per pair: `a, b, a_name, b_name, area, activators, dates, first_date, last_date, pin_km, outline_km|null, a_outline, b_outline, route, source_url, read_date (UTC), why`. Run-level problems are listed there too. `summary.md` gives counts per area and route plus the top 50 pairs by activators. The other files are `state.json`, `run.log` and `work/below_threshold.json` (refs and counts only).

**Example.** `python kpc_missed_fers.py --areas US-KY --limit 3 --cache /tmp/c --out /tmp/o` reads the KY park list and 3 histories, then writes `/tmp/o/missed_fers.json` and `/tmp/o/summary.md`.

**Lenient club-file reading.** The exact shape of the `data/fers` files is not known to the builder, so *every* `*.json` under `--fers` is searched, recursively. A pair is found if its two refs appear in any of these shapes: one string (`"US-0050+US-10105"`), a list (`["US-0050","US-10105"]`), sibling string fields (`{"a":..,"b":..}`), a ref-keyed dict (`{"US-0050":{"with":"US-10105"}}`) or an owner ref with child refs. That covers the live lists, `missing-*.json`, both YES and NO in `known-answers.json`, and dropped rows. Pins come from `parkinfo/*.json` plus `../pota/t/*.json`, falling back to the POTA pin. Outline status `g` comes from `us-key/ca-key/world-key`. A park missing from the keys counts as `pin`. The keys have no geometry, so the 2 km outline test runs only when a key row carries an optional `bbox:[w,s,e,n]`. Otherwise `outline_km` is null. Trail/river means the parkinfo type or name matches trail/river/greenway/byway/canal.

**Grey areas (G-M1..G-M3)** are flags: `--min-activators 3 --min-dates 3 --max-pin-km 15 --max-outline-km 2 --rove-parks 5`. The tool does not judge "touching only" pairs (G-M3); they are routed like any other pair.
