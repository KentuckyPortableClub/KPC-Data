# kpc_parcel_trace: test report (Oct 31, 2026, round 4: 2x size limit against the official size, state-gis default, _common in every zip)

## Selftests (no network)

- `python kpc_parcel_trace.py --selftest`: **PASS** on Python 3.11.18 and 3.13.5, in this folder, in the KPC-Data mirror and from a fresh unzip.
- `python ../kpc_parcels/kpc_parcels.py --selftest`: **PASS** on both (kpc_parcels unchanged this round).

New in round 4 (on top of the round-3 checks listed below):

- **Size limit 0.2x-2x:** 2.5x the official size gives NEEDS A PERSON with no outline; 1.9x gives DRAWN with `size_ratio` about 1.9; under 0.2x gives NEEDS A PERSON. The why says "allowed 0.2x-2x".
- **Official acres first:** a park in the official acres list uses it even when its round-14 figure would fail (a round-14 figure of 1 ac is ignored), and the source text "official acres list (acres.json: <agency>, ...)" is in the why, report.csv `known_acres_source` and the feature property. A park not in the list uses the round-14 figure ("the park is not in the official acres list"); with no list given it says "no official acres list given"; with neither, "no official size".
- **List reading:** kpc_acres `acres.json` (dict rows) and `acres-list.json` (numbers) both read; the first file wins; a row without a number is skipped.
- **--state-gis:** a lake-surface layer listed in the given state-gis.json makes the keyed park joined to it stop counting as an official outline (only the HQ file's parcel is left out), and the file path and layer count are recorded.

Mutation checks (round 4): putting the upper limit back at 5x, ignoring the official acres entry, or ignoring the `--state-gis` path each makes the selftest FAIL.

## Live run (Oct 31, 2026, round 4, 23:04-23:06 CT)

```
python kpc_parcel_trace.py --parks tests/parks.json --all --out ../runs/trace_live --cache ../runs/cache_trace \
    --official-dir /workspace/KPC-Data/data --official-dir ../runs/official_extra \
    --state-gis ../runs/state-gis.json --official-acres ../runs/official_acres/acres.json
```

- Exit 0, 93 s, 58 requests (cache kept from round 3). DFRP demo: exit 0, 5 s, 4 requests. Logs: `tests/live_output/trace_live.log`, `tests/live_output/dfrp_demo/trace_dfrp_demo.log`.
- `runs/official_extra` stands in for the website repo's Kentucky folder (`ky-answer-key.json` + ten `ky-*.geojson`), passed with `--official-dir` the way chat 10 will at install. Loaded: 119,621 keyed records, 189 Kentucky parks, 0 file outlines.
- `runs/state-gis.json` is byte-identical (sha1 6ed33702...) to `data/state-gis.json` in KPC-Data HEAD 1623447; 3 lake-surface layers. It is passed with `--state-gis` only because this clone's sparse checkout leaves `data/state-gis.json` off disk; in a full checkout the default finds it.
- Official acres: `runs/official_acres/acres.json` is kpc_acres' Kentucky smoke output (131 KY parks from KDFWR, KY Forestry, Nature Preserves and State Parks layers on kygisserver.ky.gov, Oct 31). It is **not** a club-approved list and it does **not** contain any test park (Salato US-10172 is not in it; the KY answer key lists US-10172 as missing). So every size check below used the round-14 figure.

| ref | name | status | acres | known size | known size source | ratio | why (short) |
|---|---|---|---|---|---|---|---|
| US-10172 | Salato Wildlife Refuge | **NEEDS A PERSON** (was DRAWN) | 921.12 | 229.85 | round-14 figure (not in the official acres list) | 4.01x | size check failed, over 2x; 14 parcels, pin inside |
| US-9739 | Forks of the Coal State Natural Area | DRAWN | 99.60 | – | none (not in the list, no round-14 figure) | – | 12 parcels, pin inside; no size check |
| US-12753 | Joe Hogan State Conservation Area | DRAWN | 269.83 | – | none | – | 2 parcels, pin inside; no size check |
| US-3118 | Halfmoon Pond State Park | NEEDS A PERSON | – | 894 | round-14 figure | – | every agency parcel within 500 m is inside US-3101 Bomoseen SP (pin inside it too): for chat 2 |
| US-8388 | Great Falls Discovery Center SRA | NEEDS A PERSON | – | 1.32 | round-14 figure | – | every agency parcel within 500 m is inside US-2428 Connecticut River Greenway SP: for chat 2 |
| US-10389 | Hiwassee Dam Recreation Park | NEEDS A PERSON | 8132.80 | 829.32 | round-14 figure | 9.81x | cut off at 10 km and over 2x |
| CA-5737, CA-0845, CA-4610, CA-4613, CA-5738 | Yukon recreation parks | NO PARCEL | – | – | none | – | no DFRP property near the pin |
| CA-4937 (DFRP demo) | Dredge No. 4 National Historic Site | DRAWN | 92.56 | – | none | – | 1 DFRP property, pin 4.9 m outside |

Only Salato changed status. Halfmoon and Great Falls are held by the other-park rule before any outline is computed, so they have no acres or ratio.

## Changes in round 4 (Oct 31)

1. Size limit tightened from 0.2x-5x to **0.2x-2x** (`SIZE_LO, SIZE_HI`); the lower bound is unchanged.
2. Known size = the official acres list (`--official-acres`, `$KPC_OFFICIAL_ACRES`, or `acres.json` in the official dirs / KPC-Data `data/`), round-14 `known_acres` only for parks not in it; the source is written per park (why, `known_acres_source`, `size_ratio`).
3. `--state-gis` (default KPC-Data `data/state-gis.json` when on disk); the log names the file used.
4. README: Kentucky outlines via a second `--official-dir` (website repo, set at install); keep the cache between runs.
5. The shared source (`_common`: polite.py, the tool sources, build.py) ships in every zip.

## History: round 3 report, kept as it was (Oct 31, 2026, round 3: other-park rule, WV misspellings, robots.txt rule everywhere)

### Selftests (no network)

- `python kpc_parcel_trace.py --selftest`: **PASS** on Python 3.11.18 and 3.13.5.
- `python ../kpc_parcels/kpc_parcels.py --selftest`: **PASS** on both (the shared keyword list and polite reader changed; see below).

The tracer's selftest runs a fake ArcGIS server of 100 m squares (maxRecordCount 3, so paging is exercised). Besides the earlier checks (owner matching and normalisation, refused sources, the 7-parcel trace, 600 m parcel left out, private name never written, pin 400 m off, OWNER UNCLEAR, bad row and Regrid as ERROR, paging, single parcel, Warren County skip, polite reader), it now checks:

- **Held back:** a size check outside 0.2–5× gives NEEDS A PERSON with no outline, but still reports acres and the pin's distance from the outline. A trace cut off at the km limit also gives NEEDS A PERSON.
- **Canada / DFRP:** custodian = managing agency gives DRAWN with that custodian as owner and grade `approximate (agency parcels)`. A custodian that is not the managing agency gives OWNER UNCLEAR ("not the managing agency"). No DFRP property near the pin gives NO PARCEL.
- **Keywords:** WV DIV. OF NAT. RES., MO DEPT. OF CONSERVATION, U.S. FISH & WILDLIFE, PA GAME COMMISSN, … WATER MANAGEMENT DIST, … CONSERVATION AUTHORITY, … PARKS & REC all count as government.
- **403s:** a 403 on robots.txt alone leaves the host unblocked and the park DRAWN. A 403 on the data request gives ERROR `blocked: …`, marks the host blocked, and the host is not asked again.
- **WV misspellings (round 3):** WEST VIRGINIA DIVSISION / DIVISON / VIRGININA DIVISION OF NATURAL RESOURCES, NATUARL, RESOURSES and an Ontario name all count as the state's agency and match it; VIRGINIA DIVISION OF NATURAL RESOURCES does not match West Virginia; TEXAS NATURAL RESOURCES LLC stays private.
- **Other-park rule (round 3):** a fake official outline layer and an HQ geojson. Excluded: parcel P4_0 (inside an `official-*.geojson` HQ outline) and P0_0 (inside a keyed `g: official` park), both as seed candidates and in growth, with the parcel id, other ref and share recorded. Kept: a parcel only 30% inside; parcels inside approximate-graded outlines; parcels inside the park's own outline; parcels inside keyed parks graded approximate or with an "approx" join. The trace ends with 5 parcels. A big official outline covering everything gives NEEDS A PERSON with "the pin itself is inside". No `--official-dir` gives the "check was not done" note; an area with no key gives "no official outline data covers US-Q9".

Mutation checks: turning off the hold-back, pointing the DFRP owner at the wrong field, or letting a robots.txt 403 block the host each makes the selftest FAIL. Round 3: changing INSIDE_SHARE, dropping the exclusion from growth, dropping the own-ref check or the grade check each makes it FAIL too.

### Live run (Oct 31, 2026, round 3, 22:49–22:50 CT)

```
python kpc_parcel_trace.py --parks tests/parks.json --all --out ../runs/trace_live --cache ../runs/cache_trace \
    --official-dir /workspace/KPC-Data/data --official-dir ../runs/official_extra
```

- Exit 0, 88 s, 58 requests (outline cache already filled). The first run this round (22:32–22:48 CT, before outlines were made lazy, empty outline cache) took 955 s / 523 requests, exit 0, with the same results. Log: `tests/live_output/trace_live.log`.
- Official outlines loaded: 119,621 keyed records (us-key + ca-key), 189 Kentucky parks, 0 `official-*.geojson` outlines. `runs/official_extra` held `ky-answer-key.json`, the ten `ky-*.geojson` files and `state-gis.json` (water layers), which KPC-Data `data/` does not have.
- `KPC_CONTACT` not set: default User-Agent. robots.txt: several hosts answered 403 or 404, each logged "no robots rules (RFC 9309)". No host was blocked.

| ref | name | status | n_parcels | acres | pin distance | excluded by other park | why (short) |
|---|---|---|---|---|---|---|---|
| US-10172 | Salato Wildlife Refuge | DRAWN | 14 | 921.12 | 0 m | none | unchanged; other official outlines nearby: US-3802 Clyde E Buckley Sanctuary, US-3833 T. N. Sullivan WMA (KY files), neither holds a Salato parcel; 4.01× the 229.85 ac (ok) |
| US-9739 | Forks of the Coal State Natural Area | DRAWN | 12 | 99.60 | 0 m | none | owner now lists all four spellings (DIVSISION, DIVISION, VIRGININA, DIVISON); no `owner_withheld`; nearby US-5587 Kanawha SF, US-7051 Hilbert WMA |
| US-12753 | Joe Hogan State Conservation Area | DRAWN | 2 | 269.83 | 0 m | none | no other official outline in the search area |
| US-3118 | Halfmoon Pond State Park | NEEDS A PERSON | 0 | – | – | 300-095-10658 (100%), 300-095-10659 (97%), 300-095-10660 (99%), 300-095-10760 (89%), all in US-3101 Bomoseen State Park | every agency parcel within 500 m is inside Bomoseen; the pin itself is inside US-3101: same land or a 2-fer, check by hand |
| US-8388 | Great Falls Discovery Center SRA | NEEDS A PERSON | 0 | – | – | 04-0-0001 (85%), 04-0-0002 (89%), both in US-2428 Connecticut River Greenway State Park | every agency parcel within 500 m is inside US-2428 |
| US-10389 | Hiwassee Dam Recreation Park | NEEDS A PERSON | 3 (6 records) | 8132.80 | 0 m | none | unchanged: cut off at 10 km, 9.81× the 829.32 ac; nearby US-4509 Nantahala NF, US-4525 Cherokee NF, US-6927 |
| CA-5737 | Big Creek Recreation Park | NO PARCEL | 0 | – | – | – | no DFRP property within 1000 m |
| CA-0845 | Five Mile Lake Recreation Park | NO PARCEL | 0 | – | – | – | same |
| CA-4610 | Kookatsoon Lake Recreation Park | NO PARCEL | 0 | – | – | – | same |
| CA-5738 | Lake Laberge Recreation Park | NO PARCEL | 0 | – | – | – | same |
| CA-4613 | Liard Canyon Recreation Park | NO PARCEL | 0 | – | – | – | same |

Totals: 3 DRAWN, 3 NEEDS A PERSON, 5 NO PARCEL, 0 OWNER UNCLEAR, 0 PIN FAR, 0 ERROR.

#### DFRP demonstration (not part of the 11-park set)

`tests/parks_dfrp_demo.json`, same options. Exit 0, 5 s, 4 requests. Output: `tests/live_output/dfrp_demo/`.

| ref | name | status | n_parcels | acres | pin distance | excluded by other park | why |
|---|---|---|---|---|---|---|---|
| CA-4937 | Dredge No. 4 National Historic Site | DRAWN | 1 | 92.56 | 4.9 m | none | DFRP property 56485, custodian Parks Canada Agency = managing agency; no other park's official outline in the search area |

### What the numbers mean, honestly

- **Halfmoon** was 2933 ac / 8 parcels in round 2. Its pin and every nearby State of Vermont parcel lie inside Bomoseen State Park's official outline. The us-key already lists Halfmoon as `g: pin` with its pin inside Bomoseen. It may be the same land or a 2-fer; a person should decide. Not map-checked here (Chat 11 does that).
- **Salato** did not change (921 ac, 4.01×). No other park's official outline covers its parcels, so this rule cannot shrink it. The KDFWR HQ land, if that is what makes it big, has no official outline of its own in the data used. Not map-checked here (Chat 11).
- **Great Falls** was 1.53 ac in round 2. Both of its parcels are mostly inside the Connecticut River Greenway State Park outline, so it is now held back.
- For held-back parks where nothing was taken in, no outline was computed, so there is no pin distance.
- Each live result depends on what official data covers the area. Where none does, the why says so.

### Changes in round 3 (Oct 31)

1. **Other-park rule:** see README step 6. New `--official-dir`, report column `excluded_by_other_park`, feature property `excluded_other_park`.
2. **WV misspellings:** `match_score` is 1.0 when both names are the same state's Natural Resources agency (`kp.nr_agency`); kpc_parcels' `owner_type` counts them as government.
3. **robots.txt rule:** unchanged here (round 2); now the same in kpc_sitemaps, kpc_inspire and the shared `_common/polite.py`.
4. The 1 km PIN FAR rule is unchanged.

### Previous round (round 2, Oct 31, about 22:06–22:08 CT), for history


```
python kpc_parcel_trace.py --parks tests/parks.json --all --out ../runs/trace_live --cache ../runs/cache_trace
```

- Exit 0, 89 s, 49 requests. Log: `tests/live_output/trace_live.log`.
- `KPC_CONTACT` was not set, so the User-Agent was the default `KPC park tools (https://github.com/KentuckyPortableClub)`.
- robots.txt: services1/services2.arcgis.com answered 403, and services.wvgis.wvu.edu, services.nconemap.gov and the DFRP server answered 404. Each was logged as "no robots rules (RFC 9309)" and the data was read. No host was blocked: no data request was refused.
- Test set as before: Salato first, 5 round-14 US PARCEL rows, and the first 5 round-13 Yukon PARCEL rows. The Yukon rows now use the federal DFRP register, with the managing agency from round 13 ("Government of Yukon").

| ref | name | status | n_parcels | acres | pin distance from final outline | why (short) |
|---|---|---|---|---|---|---|
| US-10172 | Salato Wildlife Refuge | DRAWN | 14 | 921.12 | 0 m (inside) | owner COMMONWEALTH OF KENTUCKY (field `Name`); seed 035-00-00-030.00 under the pin; 4.01× the round-14 229.85 ac (ok) |
| US-9739 | Forks of the Coal State Natural Area | DRAWN | 12 | 99.60 | 0 m (inside) | WV DNR parcels (FullOwnerName); seed 20280015006400010000 under the pin; 2 slivers removed; owner now written as WEST VIRGINIA DIVISION OF NATURAL RESOURCES (+ the "VIRGININA" spelling); two misspelt variants ("DIVISON", "DIVSISION") still withheld; no known acres |
| US-12753 | Joe Hogan State Conservation Area | DRAWN | 2 | 269.83 | 0 m (inside) | owner ARKANSAS GAME & FISH COMMISSN; seed 001-05752-000 under the pin; no known acres |
| US-3118 | Halfmoon Pond State Park | DRAWN | 8 | 2933.05 | 0 m (inside) | owner State of Vermont; seed 300-095-10760 under the pin; 3.28× the round-14 894 ac (ok) |
| US-8388 | Great Falls Discovery Center SRA | DRAWN | 2 | 1.53 | 100.5 m | seed 04-0-0001 101 m from the pin; owner MASSACHUSETTS COMMONWEALTH OF; 1.16× the round-14 1.32 ac (ok) |
| US-10389 | Hiwassee Dam Recreation Park | NEEDS A PERSON | 3 (6 records) | 8132.80 | 0 m (inside) | held back, no outline: trace cut off at the 10 km limit (TVA reservoir parcels), and 9.81× the round-14 829.32 ac |
| CA-5737 | Big Creek Recreation Park | NO PARCEL | 0 | – | – (no outline) | no federal property (DFRP) under the pin or within 1000 m |
| CA-0845 | Five Mile Lake Recreation Park | NO PARCEL | 0 | – | – | same |
| CA-4610 | Kookatsoon Lake Recreation Park | NO PARCEL | 0 | – | – | same |
| CA-5738 | Lake Laberge Recreation Park | NO PARCEL | 0 | – | – | same |
| CA-4613 | Liard Canyon Recreation Park | NO PARCEL | 0 | – | – | same |

Totals: 5 DRAWN, 1 NEEDS A PERSON, 5 NO PARCEL, 0 OWNER UNCLEAR, 0 PIN FAR, 0 ERROR.

The Yukon result is expected. These are territorial park campgrounds on Yukon land, so the federal register has nothing there. A direct DFRP query (1 km around each pin) returned 0 properties for all five. Even if a federal property had been there, its custodian would not be the managing agency (Government of Yukon), so it would not have been used.

##### DFRP demonstration (not part of the 11-park set)

The DFRP path had no positive case in the test set, so it was run on one federal site: `tests/parks_dfrp_demo.json`, CA-4937 Dredge No. 4 National Historic Site, managing agency Parks Canada Agency. Output: `tests/live_output/dfrp_demo/`.

| ref | name | status | n_parcels | acres | pin distance | why |
|---|---|---|---|---|---|---|
| CA-4937 | Dredge No. 4 National Historic Site | DRAWN | 1 | 92.56 | 4.9 m | DFRP property 56485, custodian Parks Canada Agency = managing agency |

#### What the numbers meant then

- **Salato** (921 ac against 229.85) and **Halfmoon** (2933 ac against 894; parcel IDs from three town prefixes) pass the 5× test but probably take in neighbouring state land. Neither has been checked on a map.
- **Forks of the Coal** stays at 99.6 ac of WV DNR parcels. Parcels owned by "FORKS OF COAL STATE NATIONAL (AREA) ETAL" are a different owner and are not joined.
- **Hiwassee** is now held back as NEEDS A PERSON, and no outline is written for it.
- **Great Falls:** the pin sits 100.5 m outside the outline. That is within 1 km, and the pin was not moved.

#### Changes in round 2 (club decisions, Oct 31)

1. **Canada:** the DFRP custodian is the owner (`owner_source: "dfrp"`), used only when it is the managing agency.
2. **NEEDS A PERSON:** a failed size check or a cut-off trace is held back with no outline.
3. **Government keywords** added in kpc_parcels (the shared list): Division of Natural Resources, Department of Conservation, Fish and Wildlife, Game Commission, Water Management District, Conservation Authority, Parks and Recreation.
4. **Pin distance:** `pin_dist_m` (distance from the final outline) is written in features and report.csv for every computed outline, including NEEDS A PERSON and PIN FAR. A new `acres_check` column is added to report.csv.
5. **Contact:** the default is `https://github.com/KentuckyPortableClub`, and `KPC_CONTACT` overrides it (set by the club at install).
6. **403s:** a 403 on robots.txt alone means no robots rules (RFC 9309) and the layer is still read. kpc_parcels used to mark the robots.txt address, or the whole host on non-shared servers, as blocked. Only a refused data request now blocks a host (no retry), and that park is ERROR `blocked: …`.
