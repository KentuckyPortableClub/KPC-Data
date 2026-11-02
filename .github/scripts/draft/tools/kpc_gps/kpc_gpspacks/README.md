# kpc_gpspacks — state GPS packs (spec part C, chat 10)

**What it does.** Reads the club's own files and writes, **only inside `--out`**:
`data/gps/<area>.gpx.zip` (pins, parking/entrances/boat ramps/trailheads, outlines as closed tracks),
`data/gps/<area>.kml.zip` (same, outlines as real polygons), `data/gps/<area>-trails.gpx.zip` (trail lines only),
plus `data/gps/index.json` (sizes, `source_url` / `read_date` / `why` per file), `report.md` and `state.json`.
Labels, symbols, notices and file names follow `KPC_10_GPS_Download_Spec.md`; the code that writes them is the same
algorithm as the site's `kpc-gps.js` (cross-checked: identical points, names and descriptions on the sample data).
It never fetches anything from the internet and contains no OSM / Google data.

**Install.** Python 3.12. `python3.12 -m pip install -r requirements.txt` (lxml is only for `--selftest`; the build itself is stdlib).

**Run (Kentucky first):**
```
python3.12 kpc_gpspacks.py --parkinfo data/parkinfo --access data/access --keys data/us-key \
   --outlines <outline geojson files/folder> --trails <trail geojson> --areas US-KY \
   --out /tmp/gpsbuild --max-minutes 50          # site link defaults to the KPC-Links page; --site-url overrides
python3.12 kpc_gpspacks.py ... --out /tmp/gpsbuild --resume                    # carry on after exit 3
python3.12 kpc_gpspacks.py ... --out /tmp/gpsbuild --resume --changed-only     # nightly: rebuild only areas whose inputs changed
python3.12 kpc_gpspacks.py --selftest                                          # offline, prints PASS/FAIL
```
Exit 0 = all asked areas done; exit 3 = time ran out, work left (run again with `--resume`). Bad rows are skipped and listed in
`report.md`; they never stop the run. 2-fer spots go in only with `--include-fers --fers data/fers` (then the 2-fer notice is added).
Pull-off candidates go in only with `--pulloffs` and only rows graded YES (for later, after chat 11).

**Size rules.** Each outline ≤ 2,000 points (5 m first, then coarser; the detail is written in the track `<desc>`); if a pack is
over `--max-mb` (5) it retries at 1,000 / 500 / 250 points per outline; GPX files are split into `_partNofM` at `--max-tracks` (200).

**Not done here (see `../GPS_NOTES_README.md`):** pushing to the KPC-Data `gps-packs` branch, the nightly scheduler,
and the "GPS downloads" page (on HOLD until Brandon's GO). Input shapes were inferred from the contract — check `TEST_REPORT.md`.

**Rulings applied (Brandon, Oct 31 2026):** default site link `https://kentuckyportableclub.github.io/KPC-Links/` (`--site-url` /
`KPC_SITE_URL` override); pack name `KPC_US-KY_parks_YYYY-MM-DD.gpx` OK; parking is "Parking (from <agency>)" using the access data's own agency only (row, then access file's
top-level `agency` / `meta.agency` / `source.agency`), **never the outline's** (ruled 9:41 PM CT); if none, exactly
"Parking (from an official access list; check the agency’s map before you go)"; the GPS downloads page notice is a placeholder the club fills in word for word.
