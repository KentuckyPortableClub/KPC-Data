# KPC 9 Map Picture Maker: test report

Run on 2026-10-31 (US Central time), with Python 3.13, shapely 2.2, pyproj 3.8 and Pillow 13. The data was the club's `sample-data/`, which was only read, never written.

## Unit tests (offline, made-up shapes, fake web)
`python -m pytest -q tests` gave **26 passed, 0 failed** (re-run from a fresh unzip of the final zip).

Late fix (found while building KPC 10, which shares this code): when a record comes back as ArcGIS rings, a hole is now given to the *smallest* outline that fully holds it, so an island in a lake (with a pond on the island) reads as valid. The test `test_esri_island_in_lake_is_valid` covers it. The 12 example pictures were made before this fix; it only touches the ArcGIS-rings fallback, and pictures repair shapes before drawing, so at most a small hole could be drawn filled. They were not redrawn.

What they cover:
- **Tile maths:** zoom choice, the shape of the view, and the base map picked from the park number (for example JA- gets the plain background, never OSM).
- **Shapes:**
  - a closed ring is an area and an open line is a stretch;
  - a ring inside a ring is a hole, and ArcGIS clockwise rings are read the right way;
  - pin distance: 0 inside, about 888 m for a pin 0.01° outside;
  - patch width: a 100 m strip measures as 100 m;
  - acres, and the 100 ft (30.48 m) buffer.
- **Acres from several records:** the pieces of one source are added up, and duplicate sources are not added twice.
- **Live 2-fer rows:** rows marked dropped, merged or NOT SURE are left out.
- **The four warnings,** and the "pin inside / N m outside" text.
- **Drawing:**
  - a full offline render on a plain background comes out 900 × 700 and under 150 KB;
  - worst-case noise still squeezes under 150 KB;
  - dashed lines have both dashes and gaps.
- **Polite fetching:**
  - at least 1 s between calls to one host;
  - the KPC User-Agent;
  - back-off on 429 then 503, honouring Retry-After;
  - robots.txt "Disallow" is obeyed, with no call made;
  - the cache keeps the read date;
  - an ArcGIS error answer counts as SOURCE DOWN.
- **Command line:**
  - bad JSON, no input, or `--refs` without `--key` exits 2;
  - `--max-minutes 0` exits 3;
  - a failed item is logged as SOURCE DOWN with status "retry", and the run exits 3;
  - 2-fer ids with commas split on `;`.

## The 12 example pictures (in `examples/`)
Times are for the **first** run, reading live with 1 request per second per host and nothing cached. A cached re-run takes 0.1 to 1.5 s per picture.

| # | Item | What it shows | First-run time | Size |
|---|---|---|---|---|
| 1 | KY 2-fer area US-0019 + US-10164 (Cumberland Gap NHP + Shillalah Creek WMA) | gold and blue outlines, orange patch of 74 ac, 115 yd across | 26.2 s | 138 KB |
| 2 | KY 2-fer area US-0050 + US-10105 (Mammoth Cave NP + Green Wild & Scenic River) | patch of 6,852 ac, 1,509 yd across | 18.2 s | 132 KB |
| 3 | KY 2-fer trail US-0608 + US-4572 (Ohio River Islands NWR + Lewis & Clark NHT) | trail line, dashed 100 ft band from the line, zone patch of 8.1 ac, 66 yd across | 30.2 s | 141 KB |
| 4 | KY 2-fer river US-0703 + US-3791 (Fort Donelson NB + Trail of Tears NHT, water route) | the shared shore stretch (6.6 km) in orange, the **bank band**: dashed 100 ft from the USGS NHD river bank, with the bank in thin blue | 44.0 s | 118 KB |
| 5 | Question YES: US-10258 Ouachita NRT, record 11002565 (USFS trails) | trail record in gold, pin 57 m outside | 36.4 s | 145 KB |
| 6 | Question YES: US-13623 Alum Cove Natural Bridge Trail NRT, record 11032118 | pin 143 m outside | 10.4 s | 81 KB |
| 7 | Question NO: US-12938 Laurel Industrial Forest Land SWA, record 309 (DE Forestry) | 6 scattered tracts with grey neighbours | 41.4 s | 139 KB |
| 8 | Question NO: US-9907 First Landing NRT, record 249102 "First Landing State Park" (USGS Trails) | a 0.1 km line, pin 67 m outside | 131.4 s (slow server) | 84 KB |
| 9 | CA-0006 Big Creek (canada-bounds, CPCAD) | 3 pieces; 1,363 ac record vs 1,951 ac drawn, pin inside | 78.8 s (see tiles below) | 82 KB |
| 10 | CA-0010 Bruce Peninsula (canada-bounds) | 41,297 ac record vs 39,301 ac drawn, neighbour CA-0021 in grey | 34.0 s | 74 KB |
| 11 | CH-0306 Bachsee Mire Landscapes (world-bounds/CH, BAFU) | swisstopo base map, 1,137 ac drawn, pin inside | 42.6 s | 127 KB |
| 12 | CH-0104 Randen (world-bounds/CH, BLN) | 18,030 ac drawn, pin inside | 55.5 s | 132 KB |

- **Average size: 116 KB** (119,000 bytes). The largest is 145 KB, and all 12 are under 150,000 bytes at 900 × 700.
- **Average first-run time: about 46 s per picture.** Most of that is the 1-second-per-host rule, multiplied by the number of map tiles (up to 48 plus 12 for the inset), the record, neighbours, pins and NHD.

## Tile sources
- **USGS The National Map (USGSTopo):** all tiles loaded.
- **swisstopo:** all tiles loaded.
- **NRCan CBMT:**
  - `maps-cartes.services.geo.ca` **failed on every run**. Its robots.txt says `User-agent: * / Disallow: /` (only a named "getmapbot" is allowed), so the tool obeys it and does not fetch tiles there.
  - `geoappext.nrcan.gc.ca` (the other server the spec names) did not answer at first: SSL error or time-out. On the first two CA pictures the tool fell back to a plain background with Natural Earth coastlines and lakes, and wrote a warning.
  - A later run reached geoappext. One tile failed on CA-0006 the first time and loaded on a re-run. The CA pictures in the zip have the real CBMT base map.
- **IGN France and basemap.at:** each answered one test tile (HTTP 200 PNG). No full picture was made, because no French or Austrian park was in the test list.

## Not tested
- **Nothing in Kentucky's key could be read live.** It has no record ids, so Kentucky outlines come from the club's saved `ky-*.geojson` files (the KPC-Links repo root, read-only, passed with `--ky-outlines`). Those files were not in `sample-data/`.
- **CPCAD live reads for Canada** (`maps-cartes.ec.gc.ca`) timed out from here. Canada used the saved `canada-bounds/` outline, which is what the club already has.
- **US agency records with prefixed ids** (for example `sgtne…`) are wired through `us-key/layers.json` but were not part of the 12 pictures.
- **`--clean-older-than`** was not run on real pictures. It is simple code and only deletes inside `--out`.
- **A real `--max-minutes 50` stop in the middle of a long batch** was not run. It was tested with 0 minutes, and `--resume` skipped already-made pictures in a real run.
