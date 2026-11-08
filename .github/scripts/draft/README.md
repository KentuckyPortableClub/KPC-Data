# KPC Picture-Map Tracer (`kpc_trace_picture.py`)

Turns a managing agency's **official picture map** of a park (a JPEG rendered from the
agency's PDF) into an **approximate** GeoJSON outline (or route line for trails), for parks
that have no official GIS boundary. Single file, no GDAL.

## Hard rules (enforced in code where code can enforce them)
1. Only the managing agency's own official map of *that* park. Code cannot judge
   officialness: whoever adds the `index.json` row is responsible. Rows without
   `agency`, `source_url` and `page` are refused, and so are OpenStreetMap/Google URLs.
2. At least **3** matched control points.
3. Fit RMS must be **under 50 m**, or no outline is written. The leave-one-out error must
   also be under 50 m, and the match must beat a rotated "decoy" basemap (see below).
4. Output is always graded `"approximate (picture map)"`, with `fit_m`, the source URL and
   the page. It also carries `"official": false` and `"use_for_2fer": false`.
5. Basemaps come only from public government services: US Census TIGERweb roads,
   USGS NHD flowlines and BLM CadNSDI PLSS sections (US), and the StatCan/NRCan National
   Road Network (Canada). The HTTP layer refuses any other host, and never contacts
   OpenStreetMap or Google.
6. **Club rule R-G9U: unofficial maps are a last resort.** Use one only when the park has no
   official GIS layer, no county parcel from the agency, and no official agency map. The
   publisher must be a real, named organisation (a friends group, tourism office, land trust,
   trail association, local club or town newsletter). App and crowd-sourced maps are refused
   for every row, official or not: OpenStreetMap, Google, AllTrails, Gaia GPS, Strava,
   iOverlander, Wikipedia/Wikimedia, Wikiloc, Komoot, Outdooractive, Trailforks, CalTopo,
   onX and similar.
   - Unofficial rows must have `source_org` (the publisher's exact name) and `notes` (why
     nothing official exists and where you looked first), or they become ERROR rows.
   - They go through the same gates: ≥ 3 points, RMS < 50 m, LOO < 50 m and the decoy test.
   - Results are saved separately in `traced_unofficial/`, with status `UNOFFICIAL MAP` and
     grade `"Approximate, from an unofficial map"`. `use_for_2fer` and `official` are always
     false.
   - If a park has an official row, the official row is always used. Its unofficial rows are
     reported as `SKIPPED`, and any earlier unofficial outline for that park is deleted.
     The tool can only see `index.json`; when an official GIS layer or parcel turns up,
     remove the park's unofficial row and output.

## Inputs (in `--base`, default `.`)
- `maps/<REF>_<anything>.jpg`: page image of the agency map (render the PDF page at
  about 2000 px, e.g. `pdftoppm -f N -l N -jpeg -scale-to 2000 map.pdf out`).
- `pins.json`: `{"US-10172": [38.1777, -84.9231], ...}` (the POTA lat/lon).
- `maps/unofficial/<REF>_<anything>.jpg`: page images of unofficial maps (R-G9U).
- `index.json`: a list of rows (a park may have one official and one unofficial row), or a
  dict keyed by ref:

| field | required | meaning |
|---|---|---|
| `ref`, `name`, `source_url`, `page` | yes | park and map source (rules 1/4) |
| `source_type` | no | `official` (default) or `unofficial` (R-G9U) |
| `agency` | official rows | managing agency that published the map |
| `source_org`, `notes` | unofficial rows | publisher's exact name; why nothing official exists and where you looked first |
| `map_file` | no | image file under `maps/` to use, instead of the default `<REF>_*.jpg` lookup |
| `kind` | no | `area` (default) or `trail` (traces a route line) |
| `boundary_rgb`, `color_tol` | no | boundary colour `[r,g,b]` when automatic colour detection fails (tolerance in Lab, default 18) |
| `acres` | no | known size; narrows the scale search and flags an area mismatch |
| `exclude_px`, `roi_px` | no | pixel boxes `[x0,y0,x1,y1]` to ignore, or to restrict control-point search to |

## Run
```bash
python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
export KPC_TRACER_UA="KentuckyPOTA-park-tracer/0.1 (contact: you@example.org)"   # recommended
python kpc_trace_picture.py --base data --refs US-10172 CA-1234
python kpc_trace_picture.py --base data --all --resume --time-budget-min 50     # for a ~55 min CI job
```
Other options: `--max-maps N`, `--refresh` (ignore cached basemaps), `--min-interval 1.0`
(seconds between requests), `--box-km 10` (size of the basemap box around the pin),
`--rot-max 25`, `--min-m-per-px`/`--max-m-per-px`, and `--match-tol-m 75`.

Requests are polite: one at a time, 1 s apart, retried with exponential back-off (Retry-After
is honoured), and sent with a club User-Agent. Basemaps are cached in `cache/`.

## Outputs (in `--out`, default `<base>/traced`)
- `<REF>.json`: a GeoJSON FeatureCollection, written **only** when the status is DRAWN.
  A stale file is deleted on NO FIT or NO LINE.
- `report.csv`: one row per ref (ref, status, fit_m, n_points, why, fit_loo_m, model,
  n_search, decoy_best, search_tol_m, flags, source_url, page, date, source_type,
  source_org, notes).
- `traced_unofficial/` (set with `--out-unofficial`): the same layout (`<REF>.json`,
  `report.csv`, `debug/`) for R-G9U unofficial maps. It is rewritten
  atomically after **every** map, and `--resume` skips refs already in it.
- `debug/<REF>_1_boundary.png` (the detected boundary) and `debug/<REF>_2_controlpoints.png`
  (picture junctions, matched points, and the basemap drawn back onto the picture).

Status values:
- `DRAWN`: an outline was written.
- `NO FIT`: fewer than 3 points, or RMS/LOO ≥ 50 m, or not better than chance.
- `NO LINE`: no boundary or route found on the picture.
- `ERROR`: a bad row, a banned source, a missing pin or map, or an exception. The batch
  carries on.
- `UNOFFICIAL MAP`: an unofficial outline was written (in `traced_unofficial/` only).
- `SKIPPED`: an unofficial row was not used because the park has an official row (in the
  unofficial report).

## Tests (dev only, in `dev/`)
- `dev/synthetic_selftest.py`: three synthetic maps with a known answer (two drawn, one
  refused).
- `dev/synthetic_unofficial_test.py`: the R-G9U path (unofficial drawn and stored separately,
  official wins, missing fields and banned sources rejected).

## How it works
1. **Boundary:** Lab k-means colour clusters. A closed *filled* tint or a *ring* line is
   accepted. Rectangles (frames, legends, insets) are rejected. Several shapes in the same
   colour are kept as parcels.
2. **Picture control points:** LSD line segments, then T/X junctions with ≥ 3 arms near the
   boundary.
3. **Basemap control points:** road and stream network nodes, road×stream crossings, and
   PLSS section corners within `box-km` of the pin.
4. **Matching:** similarity Hough voting (rotation ±25°, scale prior, pin inside the
   boundary box), significance-scored verification, then RANSAC and ICP. The match must
   score at least 1.5× (and +2) better than the same search against the basemap rotated
   90/180/270°. Without this test, random junction coincidences routinely give
   "good-looking" fits of 10–35 m.
5. **Final fit** on correspondences within 75 m: similarity for 3 points, affine for
   4–11, poly2 for ≥ 12 only if its leave-one-out error is better. Gates: n ≥ 3,
   RMS < 50 m, LOO < 50 m.
6. **Output:** transform the outline, keep the parcel containing or nearest the pin (plus
   pieces within 50 m), simplify at 3 m, `make_valid`, and add sanity flags (pin > 1 km
   outside, area outside 0.2–5× `acres`, self-intersection, boundary touching the image
   edge).

## Known limitations
- Small or simple maps often have too few road/stream junctions inside the frame, so
  NO FIT is a common, honest result. Trail-only maps without a boundary give NO LINE.
- Canada uses NRN roads only (no CanVec hydro yet). Prefixes other than US/CA give NO FIT.
- Multi-unit maps (e.g. WMA units) need `boundary_rgb`. Check "kept N shapes" flags by hand.
- Runtime is about 10–30 s per map, plus about 5 web requests per new park.

## Nov 7 gates (held, not flagged)
A picture trace is now held as **NEEDS A PERSON** (no outline written) when any of these is true; every reason is listed in `why` and `flags`
(`kpc_trace_limits.hold_reasons`, in this order):
1. **GeoPDF placement not trusted** (`geopdf_plausible`): residual over 100 m or 2% of the page's long side, scale outside 0.05-500 m/px, x/y scale skew over 15%, a malformed affine, a sheet over 50,000 km2, or the POTA pin outside the page (`pin off page`).
2. **Pin outside**: the POTA pin is more than 1,000 m from the traced outline. The pin is never moved. The text says whether the georeference looked good (the pin may be wrong) or not (placement doubtful).
3. **Clipped**: 3% or more of the outline runs along the picture frame (the park continues off the sheet). Under 3% stays a flag.
4. **Size**: known acres decide as before (0.2x-5x). With **no** known acres the park type's ceiling decides (`TYPE_CEILING_ACRES`; unknown type = 60,000 ac), and on a GeoPDF a trace covering over 60% of the mapped page.
Trail traces over 400 km (120 km for other lines) are held too. The park type comes from parkinfo (`kpc_picture_prep.py` / `kpc_trace_prep.py` copy it into each row as `type`).
Parcel tracer: the 0.2x-2x check is unchanged; new holds are a seed parcel alone over `GROW_CAP` x the known size, and no known size with the trace over the type's ceiling.
The ceilings are sanity bounds, not park sizes: change a line in `kpc_trace_limits.py` if a real park trips one. Report columns added: `acres_traced, acres_known, ceiling_acres, edge_share, pin_dist_m`.
`KPC_NO_NET=1` (set by `kpc_full_suite.py` for every child process): a real HTTP request raises instead of opening a socket.
Tests: `tests/test_trace_limits_nov7.py` (pure Python, fixtures in `tests/fixtures/tracer_nov7/`); the suite also runs the three tracer selftests listed in `NESTED_SELFTESTS`.

## Nov 7 pin mode (which colour is the park)
On a **GeoPDF** page the page's own coordinates are known before the colour is chosen, so the POTA pin's pixel is known too. `detect_boundary`
is then given `pin_px` and chooses the boundary colour **by the pin**, not by total area:
- a shape must contain the pin, or run within `PIN_NEAR_M` (200 m) of it, or its colour is not the park's;
- a colour whose shape **contains** the pin beats one that merely runs near it;
- with an official size (or the park type's expected size) the shape closest to that size wins, and a filled park tint breaks a tie;
- with no size at all, a filled tint beats a boundary ring, then the tightest shape around the pin wins;
- the reason records the pick, its estimated acres, how many shapes in that colour sit at the pin, and the runners-up, so a wrong pick can be
  audited from report.csv alone.
If **no** colour has a shape at the pin the result is `NO LINE` naming the pin's pixel, instead of a confident outline of the wrong thing.
This is what stops a statewide sheet's district ring (US-5460, 25.9 M ac) or a road casing (CA-1248) being traced as the park.
`KPC_TRACE_PIN_PICK=0` restores the old largest-area choice. Without a GeoPDF affine nothing changes: the pin's pixel is not known before the
fit, so those maps still use the old choice and the Nov 7 size/pin/clip gates catch a bad one.
Split maps: after the existing 50 m adjacency growth, a wider gap is bridged only when an official size says the pieces belong (0.5x-1.25x,
nearest first, `kpc_trace_limits.stitch_extra`). Otherwise the further shapes are **listed** in the why for a person, never silently joined or
silently dropped.

## Brandon's calls, Nov 7 evening (in the code)
1. **A robots-blocked basemap source drops out of the run.** `fetch_basemap` asks each source once; a robots STOP (today: USGS NHD water,
   `hydro.nationalmap.gov`) is recorded as skipped, never retried, never reached by another route, and the trace goes on with the allowed
   sources (roads, land survey). Every result then carries `<name> source skipped (robots): partial basemap, matched on the allowed sources
   only`. A partial basemap is never reused from the cache in a later run. All the normal hold gates still apply to whatever comes out. If
   every source is blocked the map is an honest NO FIT, not an ERROR.
2. **Statewide sheets (over 50,000 km2) stay held** until the US-5460 flip is understood.
3. **Size ceilings:** a point-feature word in the name beats the agency ("Trailhead" beats "BLM"; US-6048 now has a 5,000 ac ceiling, not
   1,000,000). A trace **within 5% of its ceiling** (`NEAR_CEILING`) goes to a person as NEEDS A PERSON, not straight through (US-11145 at
   150,958 vs 150,000). Same band in the parcel tracer.
