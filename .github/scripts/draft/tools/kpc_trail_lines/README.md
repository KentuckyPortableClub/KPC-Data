# kpc_trail_lines (T7): sharp national trail lines

Reads each national scenic or historic trail's **official** line at full detail. The sources are the NPS, USFS or BLM layer, or the partner layer the agency links to, as named in `trails_list.json`. For each trail it then:

- keeps the land/water route and the segment status (certified, high-potential, auto tour, or the raw value);
- keeps the line within **3 m** of the official one (server thinning of 0.00001° plus a 1.89 m simplify, done in a local metric projection);
- cuts it by state using Census TIGERweb state lines;
- writes one file per trail per state.

**Install:** Python 3.11+ (tested 3.11.18 and 3.13.5), `pip install -r requirements.txt` (wheels only, no apt; now includes requests).

**Run**
```
python kpc_trail_lines.py --selftest                      # no network, prints PASS / FAIL
python kpc_trail_lines.py --trails trails_list.json --state-gis data/state-gis.json \
       --out OUT --max-minutes 50 [--resume] [--limit N] [--areas US-VA,US-TN] [--cache DIR] [--acceptance]
```

**Exit codes:** 0 done, 3 time ran out (run again with `--resume`, which uses `OUT/state.json`), 2 bad input, anything else is a crash. A single bad trail never fails the run; it is listed in `state.json` as failed and retried next run.

**Output**
- `OUT/trails/<ref>/<ST>.geojson`. Each feature carries: name, route_type (`land` or `water`), segment, segment_raw, shape (`line`, or `corridor` for Ala Kahakai's polygon), km, points, detail_m, source_url, read_date and why.
- `OUT/trails/index.json`: per trail, the states, km, water km, segments and why.
- `--acceptance` writes `OUT/acceptance.json`. It compares the Appalachian Trail in Virginia with the unthinned official line at 20 random points, measured both ways.

**Politeness:** obeys robots.txt; at most 1 request every 2 s per host; always the one User-Agent `KPC park tools ($KPC_CONTACT)`. On 429 or 5xx it backs off and retries 3 times, then the host rests for the run. A 403 is accepted with no retry and the host is marked blocked with the reason. There is a dated cache with a 30-day maximum age. It never reads OSM, Google, AllTrails, Gaia, Strava, TripAdvisor, Yelp, Wikipedia or WDPA.

**Water routes:** the why text says the 100-ft rule is measured from the river bank, not from this line (R5).

It decides nothing and writes only inside `--out`. Files bigger than 20 MB are refused; working files go in `OUT/work/`.

## Club decisions applied (Oct 31)
- Always the one User-Agent `KPC park tools (<KPC_CONTACT>)`. This tool never had a second one; nothing to remove.
- At least 2 s between requests to one host. It was already 2 s; it is now a floor in the code (a smaller `gap` is raised to 2 s), checked by `--selftest`.
- **New:** a 403 is accepted with no retry. The host is marked blocked with the reason (`403 Forbidden on <url>`): the item's `why` says `BLOCKED: ...`, the host is not asked again this run (on a shared ArcGIS Online host only that one address), and the run prints a `blocked:` line per host. The live run had no 403s, so its results and acceptance numbers are unchanged.
- Owner names, zoning layers and the Spain WFS decisions do not apply to this tool.
- **robots.txt (round 4, Oct 31):** the web reader is now the shared `_common/polite.py` (requests-based, the same one as kpc_sitemaps, kpc_inspire and kpc_parcels). A 4xx on robots.txt alone (401/403/404/451) means no robots rules (RFC 9309) and the layer is still read; robots rules that exist are obeyed; only a 403 on the data request itself is a block. services1/services3/services9.arcgis.com answer 403 on robots.txt and are read normally.
- **Cache:** the cache format changed with the shared reader, so an old `--cache` folder is not reused (the first run re-reads everything, about 12 min for all 31 trails). Keep the cache folder between runs after that.

## Shared source (`_common`)

The polite web reader (User-Agent, 2 s per host, robots.txt, 403 handling, cache) is one shared file, `_common/polite.py`, built into this tool from `_common/t7_src.py` by `_common/build.py`. The zip carries `_common/`. Edit the source there, never the built `kpc_trail_lines.py`, then run `python3 _common/build.py` (or `--check` to only compare) and this tool's `--selftest`.
