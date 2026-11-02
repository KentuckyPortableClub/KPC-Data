# KPC 10 Map Accuracy Audit: test report

Run on 2026-10-31 (US Central time) with Python 3.13, shapely 2, pyproj and rapidfuzz.
The data was the club's `sample-data/`, which was only read, never written. The Kentucky outlines were the club's `ky-*.geojson` files from the public KPC-Links repo, also only read.
Nothing was changed in any key or outline, no POTA pin was moved, and nothing came from OSM, Google or WDPA.

## Unit tests (offline, made-up shapes)
`python -m pytest -q tests` gave **15 passed, 0 failed**. They cover:
- **T1:** the pin bands, and the distance to a square.
- **T2:** geodesic acres of a 1 km² square, and the PASS / OFF / WAY OFF / NO FIGURE results.
- **T3:** short forms (SP, WMA), joined initials (J. W.), joined words (Horsemill / Horse Mill), accents, and a true mismatch.
- **T4:** WMA vs state park, a proclamation line, a whole lake vs a recreation area, a whole canal vs one section, and two passes.
- **T5:** a bow-tie (self-intersection), a 5 m sliver, a 25 m² hole, 60 pieces over about 100 km, and an empty shape.
- **T6:** a spill, the same pair excused by a 2-fer row, a same-name neighbour (no flag), and the STRtree path.
- **T7:** the coordinate step (6 vs 4 decimals), TOO COARSE, a world NOTE, the 3–5 m note, and live = N/A.
- **T8:** one shared record id between two parks.
- **T9 and the score:** the T9 dates, the score (FAR + OFF + SPILL = 9), and the why sentence.
- **Whole runs:** a whole made-up world area run end to end offline (exit 0, empty `picture`, null `answer`), and bad input giving exit 2.
- **ArcGIS rings:** a park with a lake, an island in the lake and a pond on the island reads as valid.

## The four test areas (one run: `--areas US-KY US-TN CA-ON CH`)

| area | parks | pass every test | have flags | top score |
|---|---|---|---|---|
| US-KY (all parks in ky-answer-key.json) | 193 | 120 | 73 | 7 |
| US-TN (us-key/US-TN.json) | 277 | 104 | 173 | 6 |
| CA-ON (ca-key/CA-ON.json) | 1180 | 945 | 235 | 12 |
| CH (world-bounds/CH) | 189 | 125 | 64 | 9 |

- **Time:**
  - First run with an empty cache: Tennessee alone took 4.8 min (every record read live, at 1 request per second per host). Ontario's 765 CPCAD parks took about 12 min. The whole first run of all four areas took 13.5 min.
  - Re-run from the cache: about 1 minute.
- **Resume:** `--max-minutes 0.5` stopped part-way through Tennessee with **exit 3**. `--resume` kept Kentucky, carried on from the next Tennessee park, and finished with **exit 0**.
- **Sources:** no source was down in the final run.

### Tennessee: the 10 worst, with their why
| score | ref | park | why |
|---|---|---|---|
| 6 | US-3960 | Reelfoot State Wildlife Area | CONFLICT: The park is a wma but the record is a state park (+3 more flags). |
| 6 | US-5498 | Pickett State Forest | SPILL: The outline covers 44% of US-6261 Pogue Creek Canyon State Natural Area, with no 2-fer row (maybe the wrong record) (+3 more flags). |
| 6 | US-7581 | Cordell Hull Waterfowl Refuge Wildlife Management Area | MISMATCH: The record name 'Cordell Hull Wildlife Management Area' does not match POTA's name 'Cordell Hull Waterfowl Refuge Wildlife Management Area' (score 0.67) (+3 more flags). |
| 5 | US-0533 | Chickasaw National Wildlife Refuge | OFF: The outline is 1.6 times smaller than the official 42,895 acres (26,905 ac drawn) (+4 more flags). |
| 5 | US-2955 | Wilson Cumberland Trail State Park | NEAR: POTA's pin is 65 m outside the outline (+4 more flags). |
| 5 | US-2971 | Reelfoot Lake State Park | CONFLICT: The park is a state park but the record is a wma (+2 more flags). |
| 5 | US-3928 | Bridgestone/firestone Centennial Wilderness Wildlife Management Area | MISMATCH: The record name 'Bridgestone/Firestone Wildlife Management Area' does not match POTA's name 'Bridgestone/firestone Centennial Wilderness Wildlife Management Area' (score 0.67) (+2 more flags). |
| 5 | US-3934 | Chickasaw State Wildlife Area | CONFLICT: The park is a wma but the record is a state park (+2 more flags). |
| 5 | US-3957 | Natchez Trace State Forest Wildlife Management Area | CONFLICT: The park is a wma but the record is a state park (+2 more flags). |
| 5 | US-6245 | Ghost River State Natural Area | OUTSIDE: POTA's pin is 863 m outside the outline (+2 more flags). |

### What the four areas showed
- **Kentucky:**
  - Daniel Boone NF (score 7) is graded with every tract the key lists, including the proclamation tract, so T4 says CONFLICT. That is the intended catch.
  - Six state parks whose key also lists a WMA tract get CONFLICT (state park vs WMA): Green River Lake, US-1261, -1278, -1280, -1281 and -1282.
  - T2 passes every park, because the Kentucky files' own ACRES figures seem to be worked out from the same shapes. That makes T2 weak for Kentucky.
  - Three multi-state parks (for example George Washington & Jefferson NF, with its pin in Virginia) get a NOTE instead of FAR.
- **Tennessee:**
  - 176 records looked broken in the 1 m GeoJSON read but were fine when read again at full detail as ArcGIS rings. The server's GeoJSON puts an island inside a lake as a separate overlapping piece. These records are not flagged; each one has a note in `problems`.
  - What is still flagged is real at full detail. 33 parks have "ring self-intersection": rings touching at a point, which ArcGIS allows but the OGC rules do not. 61 parks have tiny holes.
  - 45 parks are STALE CHECK: the layer was last edited more than a year before the club's read. 64 layers were edited *after* the read (NOTE).
  - PAD-US gives no last-edit date, so T9 is CAN'T TELL for those parks.
  - 18 parks are pin-only (no outline).
- **Ontario:**
  - 128 parks have only provincial list ids ("Ontario Park:…", "ON-TRCA…"), with no layer known to this tool, so their shapes are CAN'T TELL. 247 are pin-only.
  - Three canada-bounds outlines are saved at 10–20 m detail: TOO COARSE (CA-0050, CA-0078, CA-0134).
  - The worst park is CA-0027, the Georgian Bay Littoral Biosphere Reserve: its pin is 10.7 km out, plus a spill and other flags.
- **Switzerland:**
  - There is no acreage list, so T2 is NO FIGURE.
  - The world-bounds coordinates have 4 decimals (about 7–8 m), so T7 is NOTE (report only).
  - The "Teilraum" parts (for example Säntisgebiet 1–4 and CH-0165…0170) share one identical outline. T8 lists them for KPC 13, and T3 shows the record name has no "Teilraum".

## Not tested
- `--acres acres-list.json` (there is none in sample-data) was not tried against real data. Only its file loader exists.
- Other US states' us-key files and other provinces were not run.
