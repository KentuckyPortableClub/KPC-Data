# kpc_parcel_trace: an approximate park outline from agency parcels

For a park with no official GIS boundary, this tool draws an **approximate** outline from the government's own parcel map. It follows spec KPC_3_Parcel_Tracer_Spec.

1. **Seed.** Use the parcel under the POTA pin. If that parcel is not the agency's, use the nearest agency-owned parcel within 500 m.
2. **Grow.** Add every parcel with the same government owner that touches the growing shape or lies within 200 m of it. Stop when nothing new connects. The tool only queries boxes around the shape, so it never sweeps a whole county. It also stops at `--max-km` (10 km) around the pin and marks the result INCOMPLETE.
3. **Owner match.** Owner names are normalised (case, punctuation, `&`→AND, DEPT/COMMISSN/NATL/ST OF…, "VERMONT STATE OF"→"STATE OF VERMONT"). A parcel matches when the rapidfuzz score, max(ratio, token_sort_ratio), is ≥ 0.90 against the park's `agency_owner_names` or their aliases. If nothing near the pin matches, the status is OWNER UNCLEAR.
4. **Clean.** Run `make_valid`, drop parts and holes under 0.1 ac, and simplify to 3 m in UTM (the zone comes from the pin). The result is one (Multi)Polygon graded `approximate (agency parcels)`.
5. **Sanity checks.**
   - If the pin is more than 1 km outside the final outline, the status is PIN FAR and nothing is written. POTA pins never move.
   - **Size check (club decision, Oct 31, round 4).** The traced area must lie between **0.2× and 2×** the park's known size (`SIZE_LO, SIZE_HI = 0.2, 2.0`). More than 2× is NEEDS A PERSON with no outline: it usually means same-owner land next door was taken in (Salato: 921 ac against 229.85 ac; the club thinks the Fish & Wildlife headquarters land next door was taken in). The lower bound stays 0.2× (nothing in the club's decisions changed it; a trace far smaller than the park usually means the seed was a stray agency lot).
     - **Known size, in order:** (1) the **official acres list** (`--official-acres FILE`, repeatable; default `$KPC_OFFICIAL_ACRES`, else the first `acres.json` / `acres/acres.json` found in the `--official-dir` folders or KPC-Data `data/`); (2) only when the park is not in that list, the round-14 `known_acres` from parks.json; (3) otherwise no size check, and the why says so.
     - Accepted list formats: kpc_acres `acres.json` (`{ref: {acres, agency, record_name, source_url, flags…}}`), kpc_acres `acres-list.json` (`{ref: acres}`), or a list of `{ref, acres}`. The first file that has a ref wins.
     - **Which source was used** is written for every park: why ("known size from the official acres list (acres.json: <agency>, "<record>") <url>" / "known size from the round-14 figure (parks.json known_acres; the park is not in the official acres list)"), report.csv columns `known_acres`, `known_acres_source`, `size_ratio`, and the same feature properties.
     - As of Oct 31 neither KPC-Data nor the box holds a club-approved per-ref official acres list; kpc_acres (KPC-Data `.github/scripts/draft/tools/kpc_acres`) builds one from the agencies' lists. The round-4 run used kpc_acres' Kentucky smoke output (131 KY parks, `runs/official_acres/acres.json`); none of the test parks is in it, so all fell back to round-14.
   - **Held back (club decision, Oct 31):** a failed size check, or a trace cut off at `--max-km`, gets status **NEEDS A PERSON**. No outline is written; report.csv gives the reason, the acres and the pin distance.
   - The pin's distance from the final outline (`pin_dist_m`, 0 when inside) is written in every result that computed an outline: feature properties and report.csv, including NEEDS A PERSON and PIN FAR rows.
6. **Other parks (club decision, Oct 31).** A parcel is never taken in, as the seed or during growth, when it sits inside **another** POTA park's official outline. The same owner can hold several parks (a wildlife agency's HQ next door, a state park beside a state forest), so owner matching alone is not enough.
   - **Inside test:** at least 50% of the parcel's area (`INSIDE_SHARE = 0.5`) lies inside the other park's outline, both measured in the park's UTM zone. A parcel only partly over the line (under 50%) is kept.
   - **Only official-graded outlines count**, using the same definition as the 2-fer line (kpc_fers `official_parks`): a park in the answer keys `data/us-key` / `data/ca-key` with `g == "official"`, no join whose method says "approx", and no join on a lake-surface (water) layer listed in `state-gis.json`; Kentucky parks from `ky-answer-key.json` over the `ky-*.geojson` files (the trail, bkpc and Daniel Boone NF non-proof entries are left out); and any `official-*.geojson` file whose features carry `ref` and `grade: "official"`. Approximate outlines (including this tool's own output) never exclude anything. The park's own ref never counts.
   - **Where the shapes come from:** answer-key ids are fetched from the source the key names: PAD-US (USGS, `edits.nationalmap.gov/.../PAD-US/PAD_US/MapServer/0`), the USFWS refuge layer, CPCAD (ECCC) for Canada, or the state layer listed in the key's `layers.json`. Each record must still carry the key's record name, or it is not used. State layers are asked only when one of their keyed parks' pins is within 80 km of this park's pin; the national layers are always asked. Requests use the same polite reader (2 s per host, robots.txt, one User-Agent).
   - **`--official-dir DIR`** (repeatable) gives the folders holding those files. Default: `$KPC_OFFICIAL_DIR`, else the KPC-Data `data/` folder when this file sits in KPC-Data (`.github/scripts/draft/tools/kpc_parcel_trace`). KPC-Data's `data/` has us-key, ca-key and parkinfo but **not** the Kentucky outline files.
   - **Kentucky outlines:** `ky-answer-key.json` and the `ky-*.geojson` files live in the club's website repo. The club passes that folder with a second `--official-dir` when it installs the tool (for example `--official-dir ../../../../../data --official-dir <website repo>/<folder with ky-*.geojson>`). Nothing is copied into KPC-Data. The Oct 31 runs used `runs/official_extra` as a stand-in.
   - **`--state-gis FILE`** (lake-surface layers, which are not proof): default KPC-Data `data/state-gis.json` when it exists on disk, else the first `state-gis.json` in the `--official-dir` folders. When none is found the log says so and lake-surface joins are not left out. Note: in a sparse checkout limited to `data/` sub-folders, `data/state-gis.json` is tracked in git but not on disk; check out the full `data/` folder (or pass `--state-gis`).
   - Outlines are only fetched once an agency parcel has been found near the pin, so NO PARCEL parks cost nothing extra.
   - **Recorded:** `why` lists the other official outlines in the search area (or "no other park's official outline in the search area") and every excluded parcel as `<parcel id> in <other ref> (<share>% inside)`. report.csv has a column `excluded_by_other_park`; features carry `excluded_other_park: [{parcel_id, other_ref, share_inside}]`.
   - **No data:** when no `--official-dir` is given, or no answer key covers the area, or an outline request fails, the `why` says so ("the other-park check was not done" / "no official outline data covers …" / "other-park check incomplete: …"); the trace goes on.
   - **Every candidate excluded:** when every agency parcel within 500 m of the pin is inside another park, nothing is taken in and the park is **NEEDS A PERSON** (no outline); the why names the other park and says when the pin itself is inside it ("possibly the same land or a 2-fer, check by hand").
7. **Output.**
   - `parcels/<state_or_prov>.json`: a FeatureCollection. A park's feature is replaced on a re-run.
   - `parcels/report.csv`.
   - `state.json`.
   - All three are saved after **every** park. One park failing (ERROR) never stops the batch.

```
pip install -r requirements.txt               # Python 3.11+
export KPC_CONTACT="K4XXX <club-email>"        # goes into the one User-Agent
python kpc_parcel_trace.py --parks parks.json --refs US-10172,US-9739 --out out/ --cache cache/
python kpc_parcel_trace.py --parks parks.json --all --out out/ --cache cache/ --official-dir ../../../../../data --official-dir <website repo KY folder>/ --official-acres acres.json
python kpc_parcel_trace.py --parks parks.json --all --out out/ --cache cache/            # chunked: stops starting parks at 50 min
python kpc_parcel_trace.py --parks parks.json --all --resume --out out/ --cache cache/   # next chunk
python kpc_parcel_trace.py --selftest          # no network, prints PASS or FAIL
```

**Contact.** The User-Agent is always `KPC park tools (<contact>)`. The default contact is `https://github.com/KentuckyPortableClub`; the club sets `KPC_CONTACT` when installing the tool, and that value replaces the default.

The tool needs `kpc_parcels.py` from the sibling folder `../kpc_parcels`, or from `$KPC_PARCELS_DIR`. It imports that tool's polite web reader, ArcGIS layer helpers, field picking, owner-type keywords and zoning refusals rather than copying them.

Exit codes:
- 0: every park is done.
- 3: time ran out. Run again with `--resume`.
- 2: bad input.

Each chunk is designed to finish inside 55 minutes:
- New parks stop being started at `--max-minutes` (50).
- A park still running at the deadline is stopped and left for `--resume`.
- **Keep the cache between runs** (`--cache`). The club keeps it, so the slow first run is paid once. The 11-park test set (Oct 31, round 3): the first run with an empty outline cache took 955 s / 523 requests (that run still fetched outlines for NO PARCEL parks; they are now fetched only when an agency parcel is found); the re-runs with the cache filled took 88–93 s / 58 requests (round 4: 93 s). The other-park outlines are most of the extra cost.

## Input: parks.json

```json
[{"ref": "US-10172", "name": "Salato Wildlife Refuge", "state_or_prov": "US-KY", "lat": 38.1777, "lon": -84.9231,
  "agency_owner_names": ["COMMONWEALTH OF KENTUCKY", "Kentucky Department of Fish and Wildlife Resources"],
  "parcel_layer_url": "https://services2.arcgis.com/.../1319Parcels/FeatureServer/0",
  "known_acres": 229.85, "owner_field": "Name"}]
```

- `parcel_layer_url` must be an ArcGIS REST `MapServer/<n>` or `FeatureServer/<n>` polygon layer from an official government source. These are refused with ERROR:
  - Regrid, OSM, Google and real-estate sites
  - zoning layers
  - damage-assessment layers
- `owner_field` and `pid_field` are optional. Use them when the automatic pick misses the owner field: Salato's layer keeps the owner in a plain `Name` field.
- `known_acres` and `county_fips` are optional.
- **Canada: `"owner_source": "dfrp"`** (club decision, Oct 31). The tool reads the federal Directory of Federal Real Property, property boundaries layer (`DFRP_PUBLIC/FeatureServer/4`, PSPC / Treasury Board, official). The **custodian** (`custodian_en`) is the owner, and it is used **only when it is the park's managing agency** (`agency_owner_names`, matched at ≥ 0.90). Grade stays `approximate (agency parcels)`.
  - Custodian is not the managing agency (for example a Yukon territorial park on land with a federal custodian): OWNER UNCLEAR, with the custodian named in `why`.
  - No DFRP property under the pin or within 500 m: NO PARCEL, with the reason.
  - Every DFRP custodian is a federal department, agency or Crown corporation by the register's definition, so the matched custodian's name is written as the owner.
- `--aliases owner_aliases.json` is optional: `{"name": ["other spelling", …]}`.
- `tests/build_test_parks.py` builds the test `parks.json` from the round 13 and 14 workbooks and the POTA park export.

## Output

- **Feature properties.**
  - Spec fields: `ref`, `name`, `grade`, `owner`, `parcel_ids`, `n_parcels`, `acres`, `source_url`, `read_date`.
  - Extra fields: `layer_url`, `pin_dist_m`, `known_acres`, `known_acres_source`, `size_ratio`, `acres_check`, `utm_epsg`, `excluded_other_park` and, when it applies, `owner_withheld`.
- **report.csv columns.**
  - Spec columns: `ref, status, why`.
  - Extra columns: `name, n_parcels, acres, pin_dist_m, layer_url, read_date, excluded_by_other_park`.
- Extra report.csv columns `acres_check` (`ok` / `outside 0.2x-2x` / empty when no known size), `known_acres`, `known_acres_source`, `size_ratio`.
- **Status** is one of DRAWN / OWNER UNCLEAR / NO PARCEL / PIN FAR / NEEDS A PERSON / ERROR. A park whose data request was refused is ERROR with `why` starting `blocked:`.

## Club decisions applied (Oct 31)

1. **Owner names.** Only government owner names are written. An owner counts as government when kpc_parcels' keyword test says so on the normalised name (case, punctuation, `&`/AND and abbreviations like DIV, DEPT, NAT RES, COMMISSN count). Since Oct 31 the keyword list (shared, in kpc_parcels) also includes Division of Natural Resources, Department of Conservation, Fish and Wildlife, Game Commission, Water Management District, Conservation Authority and Parks and Recreation.
   - A private owner is written only as "private".
   - An owner whose type is unknown is not written; `owner_withheld: true` is set instead.
   - The OWNER UNCLEAR `why` quotes government names only.
   - **Natural Resources + a state word (Oct 31, round 3).** An owner name with NATURAL RESOURCES next to a state or province name is that state's agency, however DIVISION is spelled, and misspellings are allowed (kpc_parcels `nr_agency()`: 1 wrong letter in 6–7-letter words, 2 in 8+, same first letter; exact for 5 letters or fewer). It is written as a government owner and matches the park's agency name when both name the same state (so WEST VIRGININA DIVISON OF NATURAL RESOURCES matches WV DNR, but Virginia DNR does not).
2. **User-Agent.** There is always the one honest User-Agent `KPC park tools (<contact>)`: default `https://github.com/KentuckyPortableClub`, replaced by `KPC_CONTACT` (set by the club at install). It never retries with a crawler or browser User-Agent.
3. **403s.** "Blocked" means the **data request itself** was refused with 403. That is accepted, never retried, the host is marked blocked for the run, and the park is ERROR `blocked: …`. A 403 (or any 4xx) on **robots.txt alone is not a block**: under RFC 9309 an unavailable robots.txt means there are no robots rules, so the layer is still read. services1/services2.arcgis.com answer 403 on robots.txt; their layers are read normally.
4. **Pacing.** Requests to the same host are at least 2 s apart. robots.txt is read and obeyed.
5. **Refused sources.** Zoning and damage-assessment layers are never a parcel source. Warren County, KY (21227) stays skipped.

Other rules:
- Official government parcel sources only.
- POTA pins never move.
- This tool is **not** wired into any GitHub workflow.

## Shared source (`_common`)

This tool has no copy of the polite web reader: it imports kpc_parcels, which is built from `_common/t4_src.py` + `_common/polite.py` by `_common/build.py`. The zip carries `_common/` and `kpc_parcels/`. Edit the source in `_common`, run `python3 _common/build.py`, then both tools' `--selftest`.
