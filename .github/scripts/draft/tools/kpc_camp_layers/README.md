# kpc_camp_layers

Reads the official campground map layers (ArcGIS REST) listed in the camping intake file
`{"layers": {layer_url: parks_it_covers}}` and writes campground and day-use lists for each state.

- `campgrounds/US-XX.json`: `{"src","read","camps":[[id,name,lat,lon,kind,park,page,reserve,agency,source_url]]}`.
  Kinds are c/cab/prim/grp/horse. The per-row `why`, `read_date`, open status and 3 m polygon loop go in `"extra"`.
- `dayuse/US-XX.json`: activating spots in the same format (kind `day` or `shel`).
- `campgrounds/report.csv`: one line per layer. `duplicates.csv` and `work/left_out.csv` give the reasons.

What it does: reads the layer metadata, decodes domains and subtypes, and pages with `resultOffset`. It keeps the URL's
own `where` (f=html becomes f=json, outSR=4326). Polygons become a centre point. Boat ramps, trailheads and
decommissioned or closed sites are left out. Rows within 150 m of a `--known` row with name similarity ≥0.6 are
dropped as duplicates. States come from the Census 500k outline (downloaded once into the cache). It obeys robots.txt,
waits 2 s per host, backs off on 429/503 and never stops for one bad layer or record.

Exit codes: 0 done, 3 time ran out with layers left (run again with `--resume`), anything else is a crash.

Example:

    export KPC_CONTACT="you@example.org"
    python3 kpc_camp_layers.py --in 'data/intake/_in/camping/camping-*.json' --out out/camp_layers \
        --known data/campfed,data/campstate,data/campstate-manual --max-minutes 50 --resume

Other flags: `--limit N`, `--states US-MN,US-NY`, `--cache DIR`, `--selftest` (offline, prints PASS/FAIL;
fixtures are in `tests/`).
