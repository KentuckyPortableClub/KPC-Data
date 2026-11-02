# KPC 12 River-Bank Library: test report

Run on 2026-10-31 (America/Chicago), Python 3.13.5, shapely 2.2.0, pyproj 3.8.0,
pyogrio 0.13.0 (GDAL 3.12.4), requests 2.34.2. Test files are in `examples/`.

## 1. Offline unit tests (made-up shapes, no network)

`python3 -m pytest -q tests` gives **24 passed, 0 failed**. They cover:

- **Names:** "Cowichan Lake" does not match "Cowichan River"; accents and "la/Rivière" are ignored;
  "Jacques-Cartier Nord-Ouest" does not match "Jacques-Cartier"; "Aare | L'Aar" is read as two names; "<Nul>" means no name.
- **The band is on the water's edge, not the centre:** on a 100 m wide made-up river,
  - a point 25 m onto land is inside the band;
  - a point 35 m onto land is outside it;
  - mid-river (50 m from each edge) is outside it.
  - A centre-line rule would have wrongly left the 25 m point out.
  - A cut across the river is 4 × 30.48 m of band.
  - The window's cut across the river is not treated as a bank.
- **Picking polygons:**
  - other named water ("Test Lake") is left out and listed;
  - an unnamed side channel touching the river is kept;
  - an unnamed pond 70 m away is left out;
  - an unnamed river polygon is found by a trail line 150 m off, and not by one 250 m off (the 200 m rule).
- **LINE ONLY:** only the official centre line is written (`method: line-only`), with no band and no width.
- **Outputs:**
  - the GeoJSON carries source / licence / read_date / method;
  - geometries are valid;
  - report.csv has exactly the 5 spec columns.
- **Batch rules:**
  - one SOURCE DOWN, one NZ row, and one broken row do not stop the others;
  - a SOURCE DOWN row gives exit 3 and is redone by `--resume`, which then gives exit 0;
  - running out of time gives exit 3;
  - a missing file or an `--out` inside `us-key` gives exit 2.
- **Polite fetching** (faked web):
  - KPC User-Agent;
  - a 429 with Retry-After is waited out and retried;
  - repeated 503s become SOURCE DOWN;
  - the dated cache answers the second time;
  - same host waits about 1 s, another host doesn't wait;
  - offline with no cache gives SOURCE DOWN.

## 2. Live run on official sources (the spec's test list + extras)

Command: `python3 kpc_river_banks.py --stretches examples/stretches_test.json --out run6 --cache cache`. **Exit 0** after about 20 s; the cache was warm from earlier runs, and the first Swiss run took about 2.5 min (see below).

| Stretch | Source used | Status | Polygons kept | Unnamed ponds left out | Water m² / band m² | GeoJSON |
|---|---|---|---|---|---|---|
| BC: Cowichan River, CA-6131 + CA-3379 | BC Freshwater Atlas | **OK** | 2 | 0 | 273,450 / 689,670 | 28 KB |
| Ontario: Mattawa River, CA-0294 + CA-0373 | Ontario Hydro Network | **OK** | 1 | 0 | 607,487 / 816,332 | 95 KB |
| Québec: Rivière Jacques-Cartier, CA-0502 | GRHQ | **OK** | 1 | 0 | 422,820 / 744,254 | 45 KB |
| Swiss: Doubs at Saint-Ursanne, CH-0007 | swissTLM3D | **OK** | 1 | 4 | 253,681 / 674,010 | 36 KB |
| French: Loire at Saumur, FR-2228 | IGN BD TOPO hydro (BD TOPAGE) | **OK** | 6 (river + islands' channels) | 4 | 3,089,593 / 1,311,269 | 77 KB |
| Line only: Inwood Creek, BC (near CA-6131) | BC Freshwater Atlas | **LINE ONLY** ✔ | 0 | 1 | line only | 5 KB |
| Extra: Cowichan with a made-up paddle line drawn 80 m off the centre, no bbox | BC Freshwater Atlas | OK | 2 | 0 | 246,537 / 621,416 | 25 KB |
| Extra: US-4572 using `sample-data/trails/US-4572.json` | none | NO OFFICIAL BANK SOURCE (US uses NHD, not this tool) | - | - | - | - |
| Extra: Murray River at Albury (K4TEST-AU ref, country AU) | Geoscience Australia | OK | 1 | 0 | 1,137,275 / 2,193,853 | 64 KB |
| Extra: Rhein at Bonn (K4TEST-DE ref, country DE) | EU-Hydro | OK, graded Approximate (EU compilation) | 1 | 0 | 1,876,874 / 581,270 | 10 KB |
| Extra: NZ ref | none | NO OFFICIAL BANK SOURCE (LINZ needs a key) | - | - | - | - |
| Extra: a row with no center | none | CAN'T TELL ("Bad row ... no center") | - | - | - | - |

**Checks on the results:**

- **Cowichan / CA-6131:** CA-6131's POTA pin (48.7723, -123.75) is **inside** the official FWA water polygon, 17.2 m from the water's edge, and so inside the 100 ft band. The river here averages about 39 m wide.
- **Inwood Creek:** this BC creek joins the Cowichan. The named Cowichan polygon nearby was correctly *not* used for it, and the answer is LINE ONLY with the FWA centre line only.
- **Québec:** a first try with a centre point about 1.5 km off the river gave CAN'T TELL ("water here, but none of it is named Rivière Jacques-Cartier"). That is the correct honest answer; the point was moved onto the river for the test.
- **Validity:** every written polygon is valid. Ids with a comma get `_` in the file name.
- **Offline rerun:** `--offline` from the cache gave an identical report.csv (exit 0).
- **Live exit codes:**
  - `--max-minutes 0` gives exit 3, then `--resume` gives exit 0;
  - a missing stretches file gives exit 2;
  - `--out .../fers` gives exit 2;
  - giving `sample-data/fers/US-KY.json` as `--stretches` gives exit 2 ("must be a list of ...").
- **swissTLM3D:**
  - the first run range-read the WEST + OST land-cover files (about 1.4 GB uncompressed) out of the 3.3 GB national zip in about 2.5 minutes;
  - it kept 19,136 water polygons (8,153 + 10,983) in a 60 MB cache GeoPackage and deleted the raw files;
  - the field names (UUID, OBJEKTART) and values ("Fliessgewaesser", "Stehende Gewaesser") were checked on the real file.
- **sample-data:** nothing in `sample-data/` was changed, and nothing was written there.

## 3. Not tested / known limits (honest)

- **Not checked by eye on a map:**
  - The Murray (AU) and Rhein (DE) results were not checked by eye: the AU water area is larger than a single 100 m channel would give (billabongs / anabranches named Murray River are likely included).
  - The Loire, Doubs, Mattawa and Jacques-Cartier outputs were checked by numbers only (areas, validity, kept / left-out lists), not on a map.
- **Not run live:**
  - **NRCan CHN** (fallback for AB, MB and the other provinces) was not run live in a stretch; its layer ids and fields were read from the service.
  - **Local NHN GeoPackage** (`--nhn-gpkg`): not tested (the national file is 3.5 GB).
- **A real SOURCE DOWN** (a live 5xx) was only tested with a faked web.
- **The final Swiss GeoPackage writer** (crs "EPSG:2056") was rerun only on a made-up file. The live cache was built by the earlier version of the same lines, which wrote the file's own LV95 CRS.
- **No real club `stretches.json` exists yet**, and sample-data has no Canadian water-trail rows, so the test stretches were built by hand from POTA's park list. The spec says the club will send its real list when wiring.
