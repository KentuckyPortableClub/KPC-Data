# TEST_REPORT — kpc_gpspacks (Oct 31 2026)

Everything below was run on the build box (Linux, Python 3.12, lxml 6.1.3, xmllint / libxml2 2.15.4).
**All test data is made up** (parks US-9001…US-9004, US-9101, synthetic US-ZZ). No real KPC files were available.

## 1. `--selftest` (offline) — PASS 71 of 71 (rerun after Brandon's 9:41 PM CT parking-agency ruling)
Run in the dev venv and again in a fresh venv made only from `requirements.txt`: both PASS.
```
  ok    full run exits 0 (got 0)
  ok    packs written: ['US-KY-trails.gpx.zip', 'US-KY.gpx.zip', 'US-KY.kml.zip', 'US-TN.gpx.zip', 'US-TN.kml.zip', 'index.json']
  ok    nothing written outside --out
  ok    file name KPC_<state>_parks_<date>.gpx: ['KPC_US-KY_parks_2026-10-31.gpx']
  ok    US-KY parks GPX passes the GPX 1.1 XSD 
  ok    US-KY trails GPX passes the GPX 1.1 XSD 
  ok    US-TN GPX passes the GPX 1.1 XSD 
  ok    US-KY KML passes the OGC KML 2.2 XSD 
  ok    US-TN KML passes the OGC KML 2.2 XSD 
  ok    GPX description: notice first, then build date and the default site link (KPC-Links page, ruled Oct 31 2026)
  ok    no 2-fers and no 2-fer notice without --include-fers
  ok    every wpt name <= 30 characters
  ok    wpt names unique
  ok    pin: '<ref> <park name>' + POTA pin text
  ok    3 park pins with 'Flag, Green' (broken row left out): 3
  ok    'Parking (from <agency>)'
  ok    no agency named: exact ruled parking label, curly apostrophe
  ok    ruled parking label also in the KML
  ok    Boat ramp + 'Boat Ramp' symbol
  ok    Entrance + 'Information' symbol
  ok    Trailhead + 'Trail Head' symbol
  ok    outside point labelled 'Nearby public access, not the park's own'
  ok    ungraded pull-off candidate left out
  ok    pin-only park says 'No official outline yet'
  ok    outline tracks '<ref> boundary (...)', none for pin-only: ['US-9001 boundary (Official)', 'US-9002 boundary (Approximate)']
  ok    US-9001 boundary (Official): every trkseg closed
  ok    US-9001 boundary (Official): <= 2000 points (1834)
  ok    US-9001 boundary (Official): detail stated in desc
  ok    US-9002 boundary (Approximate): every trkseg closed
  ok    US-9002 boundary (Approximate): <= 2000 points (223)
  ok    US-9002 boundary (Approximate): detail stated in desc
  ok    'Official boundary (<agency>)'
  ok    'Approximate outline (<why>)'
  ok    one trkseg per ring (outer + hole + second piece)
  ok    KML document description starts with the notice
  ok    KML folders, no 2-fers folder without the option: ['Park pins', 'Parking', 'Trails', 'Outline']
  ok    KML official outline: Polygon, yellow line
  ok    KML approximate outline drawn dashed
  ok    KML pin-only: no polygon, label present
  ok    trail label '<trail name> (official line, <agency>)'
  ok    trails pack starts with the notice
  ok    trails pack holds only trail lines
  ok    no OSM / Google / banned-source text in the parks GPX
  ok    no OSM / Google / banned-source text in the KML
  ok    no OSM / Google / banned-source text in the trails GPX
  ok    every pack <= 5 MB zipped: {'US-KY-trails.gpx.zip': 4600, 'US-KY.gpx.zip': 18746, 'US-KY.kml.zip': 18706, 'US-TN.gpx.zip': 829, 'US-TN.kml.zip': 1074}
  ok    broken park row reported with a reason; run not stopped
  ok    index.json carries the notice and the HOLD note
  ok    every pack row has source_url, read_date, why
  ok    --include-fers: 2-fer notice in the description, word for word
  ok    --include-fers: the shared 2-fer spot appears once, with the notice (1)
  ok    --include-fers: KML 2-fers folder with the notice
  ok    --include-fers files pass their XSDs
  ok    --areas US-KY builds only Kentucky
  ok    --max-minutes 0: exit 3 with work left (got 3)
  ok    --resume finishes the work, exit 0
  ok    --resume --changed-only skips unchanged areas
  ok    --changed-only rebuilds when an outline file changes
  ok    --limit 1 writes one park
  ok    260 outlines split into 2 GPX files: ['KPC_US-ZZ_parks_2026-10-31_part1of2.gpx', 'KPC_US-ZZ_parks_2026-10-31_part2of2.gpx']
  ok    every park once, <= 200 tracks per file
  ok    split GPX files pass the XSD
  ok    --site-url still overrides the default site link
  ok    260-park pack <= 5 MB zipped
  ok    outline has an agency, access data none: new wording, outline agency NOT used (GPX+KML) {'US-9050 Parking': 'Parking (from an official access list; check the agency’s map before you go). US-9050 Outline Agency Test Park.', 'US-9051 Parking 1': 'Parking (from Access File Agency). US-9051 File Agency Test Park.', 'US-9051 Parking 2': 'Parking (from Row Agency). US-9051 File Agency Test Park.'}
  ok    outline agency still labels the outline itself
  ok    access file's agency used when the row names none; the row's agency wins
  ok    agency-test pack passes the XSDs
  ok    tiny triangle kept
  ok    1500 small pieces: <= 2000 points, smallest left out (2000 points, 1000 dropped)
  ok    matches tests/expected_output.json
PASS: 71 of 71 checks passed
```

## 2. xmllint (the spec's format check)
The sample run's files, unzipped, checked with `xmllint --schema` against the topografix GPX 1.1 XSD and the OGC KML 2.2 XSD
(bundled in `tests/`):
```
KPC_US-KY_parks_2026-10-31.gpx validates
KPC_US-KY_trails_2026-10-31.gpx validates
KPC_US-TN_parks_2026-10-31.gpx validates
KPC_US-KY_parks_2026-10-31.kml validates
KPC_US-TN_parks_2026-10-31.kml validates
```

## 3. Same output as the site builder (`kpc-gps.js`)
On the same sample parks, the Python pack and the three one-park files from `kpc-gps.js` have identical waypoints
(10 of 10: position, name, desc, symbol), identical outline track names + descriptions, and identical track points
(2,057 of 2,057) — rechecked after the rulings, including the new no-agency parking label. So a park looks the same whether it comes from the pack or from the "⬇ GPS" button.

## 4. Stress run (synthetic, not real data)
500 parks, each with a 20,000-point wiggly outline (10 M points, a 268 MB GeoJSON) + 1,500 access points:
exit 0 in 230 s; the 2,000-point pack was over 5 MB so it retried at 1,000 points per outline (logged in `report.md`);
result `US-ZZ.gpx.zip` 3.8 MB (3 GPX parts of 167/167/166 tracks) and `US-ZZ.kml.zip` 3.8 MB, all pass the XSDs.
Real states will differ; Kentucky's real size is unknown until it runs on the real files.

## 5. NOT tested (be honest before Brandon's GO)
- **Real KPC files.** Input shapes come from the contract's "Club file shapes"; the access file's outside-the-park flag,
  the `data/fers` rows and the outline GeoJSON properties (`ref`, `agency`, `status`, `why`) are **guesses** with tolerant readers.
  Do a run on the real Kentucky files and read `report.md` (skipped rows say why) before trusting it.
- **Real devices:** Garmin BaseCamp / a Garmin unit, a phone map app, Google Earth — none were available. Spec test 2 is still to do.
- **The 10-park label check against the cards** (spec test 3) needs the real site.
- **Online KML validator:** KML was checked against the OGC XSD offline instead.
- The KPC-Data `gps-packs` branch push and the nightly trigger were not built (no access to KPC-Data).
