# Changelog

## 0.5.0: 2026-11-02 (key doctor, bot fixes as patches, storage guard)

### Added
- **Key doctor** (`core/key_doctor.py`, `python3 kpc_engine.py doctor --links L --data D --out OUT [--tasks ...]`). It is read only:
  it writes nothing but `OUT/key-doctor/`, and it refuses an `--out` inside either checkout. Its tasks:
  - `nos`: checks that chat 11's NOs landed in `overrides.json`. A missing NO is re-applied to a **copy**
    (`overrides.fixed.json`). It also lists NO'd records that came back in a built key.
  - `release`: a per-park split of a LIVE-FILTERED key (failing parks keep their live version). It is report only unless
    `key_doctor.per_park_release` is on (default **off**), in which case the filtered copy goes to `OUT/key-doctor/release/`.
  - `approvals`: flags YES approvals with missing fields (the Canada key with no `chat2`, the world key with no `path`).
  - `fers-ids`: stable 2-fer ids (sorted refs + kind + centre rounded to 0.01). Old ids are carried forward within
    `fer_carry_km` of the old centre.
  - `line`: the assembly-line tracker per area in club order (build → check → grade → save → release → fers → review).
    It stamps a freeze (sha) while a build is graded, flags a held copy that changed mid-grade, and counts "done" only
    when the build is live.
  - `stuck`: a daily stuck list with owners (`stuck-YYYY-MM-DD.md`, after `stuck_days`).
  - `storage`: the **size guard**. WARN at 80 MiB, RED at 95 MiB for any file (GitHub refuses files over 100 MiB).
    `US-AK.json.gz` (103.5 MB ≈ 98.7 MiB) shows RED. It also lists held waiting-room copies that live has already
    replaced.
  - The exit code is 1 when a NO is missing or came back, or a file is RED.
- New settings in `config/rules.json`, under `key_doctor.*` (see TUNING.md 1.16). `rules.value(name)` reads any setting.
- **Bot fixes as local patches** in `patches/`: six patch files against the KPC-Links and KPC-Data bots, the exact
  originals, and their own tests (`patches/patch_tests`). Nothing was applied to the club repos. See `patches/README.md`.
- **Storage plan** (`patches/STORAGE_PLAN.md`), written but **not applied**: split big state files by region or 2-fer
  kind (recommended), or use Git LFS or a release asset; keep generated output on `tools-out` with overwrite commits;
  squash `tools-out` monthly as an option.
- `pytest.ini` runs the engine tests and the patch tests together: **155 tests** (109 old + 13 doctor + 33 patch).

### Unchanged
- Every existing rule default (`rules.changed()` is still empty). The doctor's new behaviour is behind switches that
  match current practice.

## 0.4.1: 2026-11-01 (club fixes)

### Fixed
- `openpyxl` added to `requirements.txt` (the page-fix test and the .xlsx hand-back files need it).
- Blank areas: leaving out `--areas` (or a blank `AREAS`) now runs **every area in the club order** (`Club.all_areas()`,
  sorted by `kpc_order.rank_cc`, Kentucky first) instead of nothing. Areas come from the club files (KY data, parkinfo,
  Canada parkinfo, world tiles) and the POTA folder. New tests: `tests/test_blank_areas.py` (109 passing).

## 0.4.0: 2026-11-01 (round 5: master workbook import, retry list, seeded work order, HDX = WDPA, game reserves, club trail rulings)

### Added
- **Master workbook import** (`registry/import_master.py` -> `registry/master_nov1.json`), read only from a scratch copy
  (sha256 checked before and after; the workbook is never written). New 30,174 rows / duplicate of ours 2,863 / duplicate
  inside the workbook 21 / refused 56 / WDPA last resort 0. 432 new sources (384 imported, 48 not queryable); 29,395 park
  leads (17,390 name only); 207 campground pages, 52 portals, 16 picture maps, 72 new failed hosts. Duplicates keep the
  workbook's status / notes on our entry (672 entries annotated). Engine registry: 1,374 sources.
- **Retry list** (`registry/import_retry.py` -> `registry/retry.json`): 24 items tagged 'retry from GitHub network'
  (14 retry, 6 blocked 403 retried once plainly, 2 person, 1 needs sign-in, 1 person downloads: Spain enp.zip). Never past a
  403 or robot check. Runs write `retry-list.json`.
- **Seeded work order** (`config/work_order.json`, `priority.seed_of`): 18 seeds from the Mapping handoff sections 3 + 4.
  Seeds order rows inside each club class; the club's class order is unchanged. Workflow matrix parts 5 and 6 add the seeded
  areas. Runs write `work-order.json`.
- **Club trail rulings**: a named trail piece passes the name test only with an official tie (trail system / route field on
  the same record, or the agency's own page listing it), never on location. State mapping agency compilations (KyGovMaps,
  TN STS) count as official when the managing agency has no line of its own; the agency's line wins when it turns up
  (switch `source_policy.state_mapping_compilations`, on). KY+TN regrade: 4 of the 18 held trails released.
- **Game reserves are not POTA parks** (`rule_g.is_game_reserve`, switch `checks.game_reserve_not_park`, on).
- **US-6281**: `US-FL-USFS-WSR-segments` (USFS Wild and Scenic River segments) in the Florida list; the row now picks
  record 730 'Loxahatchee Wild and Scenic River' (pin only, 699 m), not Jonathan Dickinson SP.
- Tests: `tests/test_round5.py` (13).

### Changed
- HDX (data.humdata.org) protected-area / WDPA copies are recognised as WDPA and follow W-10 (last resort, approx).
  CONFLICT FLAGGED: the Mapping note says "never WDPA incl. HDX"; the user's confirmed W-10 is kept as the default.
- Outline names: description fields and sentence-like values are never used as a record's name; same-kind records win ties.
- Registry `for_area` puts the exact-area entry first when two share a URL.

## 0.3.0: 2026-11-01 (round 4: trail bar, Overlapping boundaries, 2-fer / 3-fer rules, WDPA rule W-10, docs-pagefix shapes)

### Added
- **Trail bar** (`rule_g.trail_bar`, `apply_trail_bar`): a trail passes only when it is the managing agency's own line
  (aggregated inventories such as KyGovMaps / USGS aggregated trails never count), its name matches, and the POTA pin is within
  `grader.trail_pin_m` (200 m, tunable) of the line. Rows that miss become `candidate` with the reasons. National historic
  trails the agency marks approximate stay approximate. The trail plug-in now measures `pin_line_m` per feature.
- **Overlapping boundaries + 2-fer / 3-fer rules** (`core/fers.py`): one trail feature under 2+ parks is labelled
  "Overlapping boundaries" (not a failure) and a suggestion goes to `fers-waiting-room.json` (never automatic: chat 8 +
  chat 11). Geometry helpers: parks that only touch never count; a trail with no land boundary counts within
  `grader.fer_line_ft` (100 ft) of its line (water trails: of the water's edge); a WSR corridor uses its own boundary; a
  3-fer needs a spot within 100 ft of the trail inside the overlap patch; the patch must hold a 50-yard spot.
- **WDPA rule W-10**: WDPA is rejected whenever an official layer has a record for the park; otherwise
  `registry/last_resort.json` may be asked as a last resort (switch `source_policy.wdpa_last_resort`, default on): always
  g='approx', labelled 'WDPA (last resort)', never SURE / STRONG / found, never asked while a source is blocked.
  US-0896, US-6281, US-0658 and US-1879 were re-checked live: all four have official layers, so WDPA stays rejected
  (`registry/rulings.json` lists each park's `official_found` records for chat 11).
- **docs-pagefix in the club's two shapes**: `docs-pagefix-us-<name>.csv` (`row,park,old F URL,correct URL,why column F
  was replaced`, row = the hours-fees workbook's Parks-sheet row; no workbook / no row = the ref + "mapping needed") and
  `docs-pagefix-ca-<name>.csv` (`row,POTA ref,park,column F URL,issue,correct official URL (if found),note`). Workbook paths
  in `config/handback.json` or `KPC_HF_WORKBOOK_US` / `_CA`. Samples in `fixtures/handback_samples/`. No CLOSEST shapes remain.
- Tests: `tests/test_round4.py` (trail bar, NHT, aggregators, Overlapping boundaries, fers geometry, W-10, renamed switches),
  `tests/test_pagefix.py` (exact headers, workbook rows, mapping-needed path).

### Changed
- "shared" is gone from outputs, graders and docs. Trail: "Overlapping boundaries" (info only). Parking / camping: "duplicate
  facilities (one facility listed under 2+ parks)", still a failure. Docs: "the same file is used by N parks".
  Switches renamed `checks.resolve_duplicate_facilities` and `grader.docs_same_file_max` (old names still accepted).
- The trail grader no longer fails on overlaps; it fails on rows marked found without meeting the bar, positive west
  longitudes or bad labels. Measured: rows meeting the bar, rows held as candidates, approx NHTs, overlapping boundaries.
- `export` runs `postprocess()` so the hand-back files match the grades; `rules.stamp` is idempotent.
- Rulings: US-0658 / US-1879 tags now say "official layer exists (W-10)"; US-6281 added (pin only, candidate for chat 11);
  US-0896 recorded as a `note` (the club's YES WSR line stands).

### Not changed (club, round 4)
- Bad Branch (already on the club's 2-fer list) and the Pennyrile pair (with chat 8): no changes; they only appear in the
  waiting room as evidence.

## 0.2.0: 2026-11-01 (round 3: club answers, switches, tuning guide)

### Added
- **Switches** (`config/rules.json`, `core/rules.py`): per-plug-in on/off + areas, KY hours parsing rules, optional checks,
  source-policy rules, grader numbers. Defaults = the rules before this change (tested). CLI `--enable`, `--disable`,
  `--scope kind=AREAS`, `--set grader.x=N`, `--rules FILE`. Every run writes `active-config.json` and a rules banner on
  `grades.md` / `board.md`; changes from default are logged loudly.
- Switched-off source rules **stamp** affected rows `source_policy: non-official: <rule>`, grade `approx`, STRONG→WEAK,
  found→candidate. LOCKED safety rules (User-Agent, robots / Cloudflare / captcha / sign-in, found tokens, TLS) have no switch;
  a rules file naming them, or any unknown switch, is refused.
- **TUNING.md** (linked from README): every knob with default, effect, safe range and symptom; worked example per grader;
  regrade without the web; chat 11 miss → regression test; do-not-loosen list; switch table.
- **`grade` command**: regrade saved output (`postprocess()` + graders), no web requests.
- **`--check-all KINDS`**: check kinds on every park in scope (audit runs).
- **WDPA guard**: any layer citing WDPA / Protected Planet / UNEP-WCMC (name, URL, description, licence, copyright, fields) is
  rejected in the registry, in Rule G and live from the layer's metadata. US-0658 and US-1879 stay pin only, tagged
  "no official layer found yet" (`registry/rulings.json`).
- **Kind guard**: forestry / woodland / compartment layers only match forests; new kind `nature_reserve` (NNR / LNR).
- **NatureScot National Nature Reserves** (ArcGIS FeatureServer, found via spatialdata.gov.scot) added to the registry, live-verified
  at Glen Nant: record 728, pin inside, SURE, 387.09 ha. GB-0889 stays **held** by the club ruling.
- `core/config.py`: KPC-Data (writes only to `tools-out`), KPC-Links read-only; `--out` inside `--links` refused.
- Tests: `test_round3.py`, `test_export_shapes.py`, `test_rules.py`.

### Changed
- Exports rebuilt to the club's sample shapes (world-sources, docs-found, parking-hunt, camping US / CA, acres, portals);
  `docs-pagefix` has no sample yet and stays in the closest shape.
- Workflow lives in KPC-Data, pushes results to the `tools-out` branch only, KPC-Links checked out read-only.
- `resolve_shared` and the containers check run in `postprocess()` after both passes (also on regrade).
- EU CDDA (EEA / discomap) documented: always approximate, ranked after national layers, replaced by the national layer when found.

## 0.1.0: 2026-11-01 (first build)

### Added
- **Engine core:**
  - one adapter for club files;
  - the missing list (`gaps.json`);
  - agency grouping (`agencies.json`, re-read after 30 days);
  - polite fetcher (robots, 2 s per host, cache, honest User-Agent with `KPC_CONTACT`);
  - page-reading ladder (fetch → PDF → NPS structured data → optional browser → blocked);
  - shared `findings.jsonl`, seeded from FINDINGS_LOG;
  - the notes standard;
  - 8 workers with resume and `--max-minutes` (exit 3);
  - two passes;
  - checks (links open, identity, clutter) and `spot-check.md`;
  - `board.md`, `blocked.csv`, `fixes.csv`, `pin-typos.json`.
- **Plug-ins:**
  - `outline` (ladder L0-L5, tiers / bands, kind-clash downgrade, R-G12 / R-G13, question rows, found-layers, why-not,
    picture maps);
  - `docs` (official page + map; POTA link check → `fixes.csv`; agency sitemaps);
  - `parking`, `camping`, `trail`;
  - `hours`, `fees`, `closures` (Kentucky only);
  - stubs for cell coverage, acres, missed 2-fers, GPS packs and boundary changes.
- **Registries:**
  - World (`world_sources.json`), in the club's hunt order. It includes national layers for GB (England, Wales, Scotland),
    DE, RO (ministry download), AU, NL, ES, IE, FR, DK, AT, CH, BE (Flanders, Wallonia), SE, MX, CR and more.
  - US + Canada (`us_ca_sources.json`):
    - PAD-US, NPS, USFS, FWS, BLM;
    - Kentucky and its neighbours' state layers;
    - CPCAD, Parks Canada, Ontario LIO, BC TANTALIS;
    - parking, camping and trail point / line layers;
    - layers found by ArcGIS Online discovery (government organisations only).
- `registry/verify.py`: a live check of every source (count, test pins, name match).
- Generic support for WFS 2 north-first axis order (EPSG 3006, 3844, ...).
- ArcGIS servers without pagination.
- Official shapefile / KML / KMZ / GeoJSON downloads.
- Transliteration for Nordic and German letters (ø → oe, æ → ae, ß → ss).
- Natura 2000 / SAC / SPA words treated as generic.
- The EU compilation is used only for EU / EEA countries.
- Discovered layers that are not park land (staff directories, species ranges, county lines) are filtered out.
- Offline tests, fixtures, `requirements.txt`, and a sample GitHub Actions workflow.

### Added (Nov 1, after the club source pack arrived)
- `registry/_seed_pack.py` seeds the registry from the club's pack and writes `registry/pack_sources.json`. It reads:
  - the approved YES layers (US 307, Canada 105, world 2,464 rows);
  - the club key layers;
  - the state GIS tables;
  - the access, trail and camp lists.
  `pack_sources.json` holds 729 layers and is read first, with "approved" ranked above everything else.
- Parks with a YES row are skipped as "already approved". Chat 11's 506 NO rows (park + layer + record) are never offered
  again.
- The campstate deny list and the forbidden-source rule are applied to the pack. One approved US-FL layer is a WDPA copy; it
  is dropped and listed under `excluded`.
- `registry/relist_failed.py` re-lists the servers of the 45 failed hosts and writes leads to `registry/relisted.json`.
- Name matching:
  - local-language park words from `world_agencies.json` (non-English countries) are treated as designations;
  - Natura 2000 site codes (ROSCI0123 ...) are dropped.
- The page finder trusts the agency domains from the pack (state park / wildlife sites, world agency portals).
- `AGENT_TIPS.md`: tricks for the club's research agents, each marked as checked or untested.

### Added / fixed (Nov 1, late)

- `export` command (`core/export.py`) writes the club hand-back files in HANDBACK_FORMATS.md shapes. Five of them use the closest
  shape, flagged, because the oct31 examples were not available.
- `registry/us_ca_trails.json`: 24 state trail line layers, curated from 333 discovered.
  - 6 are live-verified: KY Recreational Trails, NJ x2, TX State Parks Trails, WA State Parks Trails.
  - The other 18 only "answer": the service is up, but no sampled pin matched.
- Rule G:
  - a park name holding two kinds ("... Rail Trail State Park") may match either kind;
  - rivers may be lines or corridor polygons.
- The outline name search first reads the layer's field list (`?f=json`) and fixes a wrong name field.
- Fixed: the docs grader crashed when `map` was an object.
- Fixed: a grader with nothing to grade said PASS. It now says "NO HITS (nothing to grade)".

## Added (Nov 1, 02:04 steering: chat 11's grading bar)

- `core/rule_g.py`: Rule G (SURE / LIKELY / UNLIKELY). It covers:
  - kind words stripped and kinds matched;
  - line vs polygon;
  - containers;
  - size bands (1.5x / 5x);
  - the 0.2-2x parcel hold;
  - R-G12 (150 m);
  - R-G13 pin typos (pins never move);
  - known renames and Indigenous names;
  - the name field read from the layer;
  - the BLM_Natl_SMA deny rule;
  - the document, point, camp and hours rules.
- In the outline plug-in, UNLIKELY rows become status `evidence` (in `evidence.json`) and never become questions. Only SURE can
  be STRONG. Each row carries `rule_g`, `rule_g_why` and `size_band`.
- Post-pass: one record under 2 or more parks is a container, so evidence only.
- Parking and camping:
  - a facility under 2 or more parks stays only with the nearest pin;
  - points with a positive west longitude or a road / office / hotel / wilderness label are dropped;
  - picnic shelters, boat ramps and other businesses are dropped from camping.
- KY hours and fees: marina / scuba lines, bare time fragments and "Open seasonally" under hunting hours are dropped.
- `core/grading.py` now uses chat 11's exact bars per kind (30-point parking sample, 12-row hours / fees sample, camp 95%,
  docs rules, 2-fers never automatic). The output adds a `fails` list.
- `tests/test_misses.py`: the 18 misses plus the grader bars (23 tests, all passing).
- `registry/AGENCY_CONTACT_PAGES.md` (from the agency atlas) and README section 11b: no contacts, no people, bots never email.

## Added (Nov 1, club priority list and fixes)
- **US / Canada work order** (`core/priority.py`, from the club's PRIORITY_US_CA list): state trails first, then state parks and
  recreation areas, then historic sites, then the rest, then county / city / regional parks, then BLM; national trails last
  (the club's trail-line tool covers them). Each row carries `park_class`.
- **Grades in chat 11's shape** (`core/grading.py`): one report per kind in `grades.md` / `grades.json` with PASS or FAIL against
  the bar, what was measured, the top miss reasons and 5 example parks.
- **L5 parcels, first version:** the parcel under the pin from the official statewide parcel layers in the club's agency
  atlas (NE, RI, TX, WV; `registry/parcel_sources.json`). It always gives a WEAK "PARCEL lead" with the record number and owner.
- **State trail discovery:** an ArcGIS Online search for state and provincial trail line layers in every state and province
  (government organisations only); the results are in `registry/us_ca_trails_discovered.json`.
- `KPC_CONTACT` is now built in: `https://github.com/KentuckyPortableClub (Kentucky Portable Club ham radio club)` is the default
  in the engine and in the workflow. It is not a secret.
- `registry/verify.py` checks the pack layers live: the parks already marked YES are tested first, and the result is saved in
  `live` beside the club's status. A pack layer whose address is dead is marked `dead` and is not used.

### Fixed
- The `shapely.ops.transform` deprecation (`core/geo._tf` now uses `shapely.transform`).
- The EU compilation (EEA / discomap) stays "approximate" even when a club YES row approved it.
- A line or point record no longer crashes a row while its size is being worked out.

### Known gaps
- L5 has statewide parcel layers for 4 states only; the county parcel finder (`kpc_parcels`) is not wired.
- The cell / acres / 2-fers / GPS / boundary-change plug-ins are stubs.
- No KPC-Data / KPC-Links repos were available, so the club-file paths were tested on fixtures only.

### Fixed (Nov 1, final)
- Parking: a number used as a point label no longer crashes the run (`str()` in `point_problems`).
- Parking/camping: one shared facility is kept only for the park with the nearest pin (`rule_g.resolve_shared`), also in partial grades.
- Sample run (capped): outline PASS, docs PASS, KY hours/fees/closures PASS by auto checks (short samples: 3/5 rows). Camping and trail were not reached; marked untested.
