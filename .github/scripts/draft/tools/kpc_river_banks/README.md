# KPC 12: River-Bank Library (Canada + the world)

**What it does, in plain words:** for each water-trail stretch you list, it reads the
government's own map of the river's water, keeps the river the trail follows, and writes:

- the **water polygon** (the river as the government maps it), and
- the **100 ft band**: the strip within 30.48 m of the **water's edge** (the bank), on both
  sides of the edge. Never measured from a centre line (rule R5 for water trails).

If the government only maps the river as a centre line, the answer is **LINE ONLY**: the club uses
the line rule and marks it so. The tool never invents a river width.

It is a helper. It writes only into its own output folder and never touches the club's live files
(keys, outlines, 2-fers, site). It refuses an `--out` inside `us-key`, `ca-key`, `fers`, `trails`, etc.

## Install

    python3 -m pip install -r requirements.txt     # Python 3.11+

## Run

    python3 kpc_river_banks.py --stretches stretches.json --out work/
    python3 kpc_river_banks.py --stretches stretches.json --out work/ --resume   # carry on

Options: `--max-minutes 50` (default; stops cleanly), `--resume`, `--only <id>` (repeatable),
`--cache <dir>` (default `<out>/cache`), `--offline` (cache only), `--cache-days 30`,
`--nhn-gpkg <file>` (optional local NHN GeoPackage for Canada), `--keep-raw`, `-v`.

Exit codes: **0** done, **3** not finished (time ran out or a source was down: run again with
`--resume`), **2** bad input (missing / broken stretches file, same id twice, `--out` in a live folder).

## Input: stretches.json

A list (or `{"stretches": [...]}`). Example with practice refs:

```json
[
  {"id": "K4TEST-0001@river@48.772,-123.750",
   "refs": ["CA-6131", "CA-3379"],
   "river": "Cowichan River",
   "center": [48.7723, -123.75],
   "bbox": [-123.77, 48.765, -123.73, 48.78]}
]
```

- `center` is `[lat, lon]`; `bbox` is `[west, south, east, north]`.
- Instead of `bbox` you may give `line`: a GeoJSON geometry / Feature, a list of `[lon, lat]`
  points, or a path to a club `trails/<ref>.json` file (relative to the stretches file).
- Optional: `also_names` (other official names of the same water, e.g. a "Bassin de ..." on the
  river), `country` and `prov` (else taken from the ref prefix and POTA's park page, cached 30 days).
- `examples/stretches_test.json` holds the 12 test stretches.

## Output (in `--out`)

- `banks/<id>.geojson`: water polygon + `band_100ft` polygon (EPSG:4326), or the official centre
  line for LINE ONLY. Properties: `source`, `licence`, `read_date`, `method` (`polygon` | `line-only`),
  `grade`, `owner`, `source_url`. Characters other than letters, digits and `._+@-` in the id
  become `_` in the file name (so `48.772,-123.750` becomes `48.772_-123.750`).
- `banks/report.csv`: `id, refs, source used, status, why`. Status is OK / LINE ONLY /
  NO OFFICIAL BANK SOURCE / SOURCE DOWN, or CAN'T TELL (house-rule word: official water is there
  but none of it is this river, or the row is broken).
- `banks/_progress.json`: resume state with details (polygons kept, other named water left out).
- `sources.md`: which official source is used per country / province, with its licence.

The geojsons are geometry: put `banks/*.geojson` on the throwaway branch, keep `report.csv` in the main repo.

## How it picks the water

1. Window = bbox (or the line's extent, or the centre) + 1 km.
2. Polygons with a name are kept when the name is the river's (accents, "River/Rivière", "la/le"
   ignored; a lake name never matches a river name: "Cowichan Lake" is not "Cowichan River").
3. Unnamed polygons within 200 m of the trail line (or, with no line, the river's own official
   centre line) are kept when the river's official line runs through them or they join water
   already kept, so a pond that only sits near the trail stays out.
4. Merge, `make_valid`, simplify to 1 m. Band = the water's edge buffered 30.48 m (both sides),
   cut to the window. A cut across the river at the window edge is not a bank and gets no band.

## Sources (finest official first)

BC Freshwater Atlas, Ontario Hydro Network, Québec GRHQ, then NRCan CHN / NHN for the rest of
Canada; swisstopo swissTLM3D (CH); IGN BD TOPO hydro = BD TOPAGE (FR); EU-Hydro (other Europe,
graded "Approximate (EU compilation)"); Geoscience Australia. NZ / JP / others: NO OFFICIAL BANK
SOURCE. Never OSM, Google or imagery-made global sets. See `sources.md`.

## Polite fetching and cache

One request per second per host, User-Agent `KPC-river-banks (https://github.com/KentuckyPortableClub)`,
back-off on 429 / 5xx (honours Retry-After). Every answer is cached with its read date
(`cache/http/*.json`, 30 days). Only data services are read (no web pages), so robots.txt doesn't apply.

**Switzerland:** swisstopo publishes the water polygons only inside the national swissTLM3D
download (3.3 GB zip). The first Swiss stretch reads just the two land-cover files out of it
(about 1 GB, about 3 minutes), cuts them to water only (`cache/big/swisstlm3d/tlm_water.gpkg`,
about 60 MB) and deletes the raw files. Nothing national ever reaches the output.
On GitHub Actions, keep `cache/` with `actions/cache` so this happens once.

## Tests

    python3 -m pytest -q tests     # offline, made-up shapes, no network
