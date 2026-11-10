# KPC Park Engine

The KPC Park Engine is a helper for the club. It looks up facts about POTA parks on **official government websites and map
services only**. Those facts are a park's outline (its boundary), its official web page and map, parking spots, campgrounds,
trails, and, for Kentucky only, hours, fees and closures.

**The engine never decides anything.** Everything it finds goes into a **question** (`answer: ""`, `checked_by: ""`) for a club
member to say YES or NO to, in the waiting room. It never edits the club's files and it never moves a POTA pin.

This guide is written for club members who are not programmers. You can copy and paste every command in it.

**Doing research by hand or with an agent?** Read [AGENT_TIPS.md](AGENT_TIPS.md): practical tricks for finding official
layers and park pages, each one marked as checked or untested.

---

## Contents

> **Tuning or switching rules?** Read [TUNING.md](TUNING.md): every knob, safe ranges, worked examples, how to regrade without the web, and the on/off switches in `config/rules.json`.
1. [What the engine does, in plain words](#1-what-the-engine-does-in-plain-words)
2. [Install it (one time)](#2-install-it-one-time)
3. [Run it](#3-run-it)
4. [Run it on GitHub Actions, step by step](#4-run-it-on-github-actions-step-by-step)
5. [The source list (registry): add or fix a source](#5-the-source-list-registry-add-or-fix-a-source)
6. [Re-check (verify) the sources](#6-re-check-verify-the-sources)
7. [Add a new country, state or province](#7-add-a-new-country-state-or-province)
8. [Add a new plug-in](#8-add-a-new-plug-in)
9. [Read the results and the waiting room](#9-read-the-results-and-the-waiting-room)
10. [Troubleshooting](#10-troubleshooting)
11. [The rules sheet](#11-the-rules-sheet)
    - [Agency contacts (there are none on purpose)](#11b-agency-contacts-there-are-none-on-purpose)
12. [Folder map](#12-folder-map)
13. [Key doctor, bot patches and storage (v0.5.0)](#13-key-doctor-bot-patches-and-storage-v050)

---

## 1. What the engine does, in plain words

Each night the engine works through these steps:

1. **It makes the "missing list" (`gaps.json`).** It reads the club's files to see which parks are missing something:
   - an outline;
   - a page or map;
   - parking;
   - camping;
   - trails;
   - for Kentucky only, hours, fees or closures.
2. **It groups the missing parks by agency** (for example the National Park Service, Kentucky State Parks or Natural England).
   Biggest groups go first, because one agency site often answers hundreds of parks at once.
3. **It runs a plug-in for each kind of fact:**

   | plug-in | what it looks for | where |
   |---|---|---|
   | `outline` | the park's boundary record in an official map layer | US, Canada, the world |
   | `docs` | the official park page and its own map (PDF / picture) | US, Canada, the world |
   | `parking` | official parking lots, entrances, trailheads, boat ramps | US + Canada |
   | `camping` | official campgrounds in or near the park | US + Canada |
   | `trail` | official trail lines | US + Canada |
   | `hours`, `fees`, `closures` | copied **word for word** from the agency page | **Kentucky only** |

4. **It makes two passes.**
   - Pass 1 is quick.
   - Pass 2 goes back over the parks that are still missing or weak. It uses what the other workers learned in the meantime
     (`findings.jsonl`), and it adds the slower searches: government open-data catalogues and ArcGIS Online.
5. **It checks its own work.** Every link must open. The park name and reference must match the club's list. Copied page
   clutter (cookie banners, "page not found") is thrown out. 20 random rows go into `spot-check.md` for a person to look at.
6. **It writes one board** (`board.md`): what was missing yesterday, what was found today, what is still missing and why,
   and which websites blocked us.

### How the outline finder climbs its "ladder"

For each park the outline finder tries these steps in order, and stops at the first good answer:

| step | what it tries |
|---|---|
| **L0** | Layers we already know and have tested (the registry and `found-layers.json`). It asks "what is at the POTA pin, within 150 m?" **and** searches by the park's name, in every text field. |
| **L1** | The agency's own map server, walked folder by folder. |
| **L2** | Government open-data catalogues (data.gov, open.canada.ca). Pass 2 only. |
| **L3** | ArcGIS Online search. A result is kept only when its owner is a government organisation. Pass 2 only. |
| **L4** | The official park page: KML, KMZ, shapefile or GeoJSON links on it are opened and checked. Picture maps are listed in `picture-maps.json`; nobody traces them. |
| **L5** | Parcels (US and Canada): the land parcel under the POTA pin, from an official statewide parcel layer the club listed in its agency atlas (today: NE, RI, TX, WV, in `registry/parcel_sources.json`). It is never an outline: it gives a **WEAK "PARCEL lead"** with the parcel's record number and owner, for a person to check. This is the Hard Look "record-number and parcel" trick, and it pays off most for historic sites and small city parks. The county-by-county parcel finder (`kpc_parcels`) is still not wired in. |

### Which parks it works on first (US and Canada)

The club ranked the US and Canada parks still missing an outline by how often hams activate them (Nov 1). The engine works
them in that order, so if a run stops at the time limit, the busiest parks are already done:

1. **State trails** (and provincial trails). National scenic and historic trails are left to the club's separate trail-line
   tool, so they go last.
2. **State parks and state recreation areas** (and provincial parks).
3. **Historic sites**, national and state. The L5 parcel step helps most here.
4. Everything else (state forests, wildlife areas, heritage areas, national parks, refuges and so on).
5. **County, city and regional parks.**
6. **BLM areas.**
7. National scenic and historic trails.

The rank comes from the park's name (`core/priority.py`); each result row carries it as `park_class`. Other countries keep the
middle rank. The order changes only *when* a park is worked on, never what is found.

### How each find is graded

- **Tier:**
  - **T-1**: same name, pin inside;
  - **T-2**: every main word matches, pin inside;
  - **T-3**: most words match, or the pin is within 150 m of the edge;
  - **T-4**: the name matches but the pin is far away (could be a pin typo);
  - **T-6**: only a weak or partial match.
- **Band:**
  - **STRONG**: T-1 or T-2, pin inside, official source, sensible size and kind;
  - **WEAK**: anything less than STRONG;
  - **CONFLICT**: two different official records disagree.
- **Kind check:** if the park is a *trail* and the record is a *park* (or a lake versus a state park, and so on), the tier
  drops one step.
- **Notes on every row:**
  - where it looked;
  - what it solved (PIN OFF, NAME SOLVED, WRONG KIND);
  - why it chose this record;
  - how sure it is (sure / likely / weak) and what a checker should double-check.

### Rule G: SURE, LIKELY, UNLIKELY (chat 11's bar, added Nov 1)

On top of the tier and band, every outline row gets one of three words. They come from chat 11's grading bar and from
18 real misses. The code is in `core/rule_g.py`, and each miss is a test in `tests/test_misses.py`.

- **SURE**:
  - the pin is inside the record, or at most 150 m outside with a name match (rule R-G12: pins often sit on the road);
  - the proper words match both ways once kind words (park, state, WMA, natural area ...) are removed;
  - the kinds match (a WMA only matches a WMA, a state park only a state park);
  - it is not a line matched to a polygon (or the other way round);
  - it is not a container (one record under 2 or more parks, or a "management district");
  - the size is within 1.5 times the park's acres, or the acres are unknown.

  Only SURE can be STRONG. Chat 11 checks 1 in 10 of these.
- **LIKELY**: 2 or more shared words, or the whole shorter name, and not a line and not a container. Chat 11 grades it.
- **UNLIKELY**: everything else. It is **evidence only**. It goes into `evidence.json` and **never** into `questions.json`.

**Size bands:**
- PASS: within 1.5 times;
- OFF: 1.5 to 5 times;
- WAY OFF: more than 5 times.

A parcel lead is held for a person whenever it is outside 0.2 to 2 times the park's size. It is also held when it lies inside
another POTA park's outline.

**Never moved:** POTA pins (R-G12 / R-G13). A pin that looks like a typing slip (for example latitude 62 typed for 61) becomes a
note in `pin_typos.json`, never a change.

**Never automatic:**
- CONFLICT is never an automatic NO;
- 2-fers are never automatic.

**Names:**
- Renamed parks are known: Prairie Coulees = Hargrave Coulees.
- Indigenous names are known: Colony Farm = ƛ̓éxətəm, Mount Douglas = PKOLS.

**Name fields:** the engine reads a layer's field list (`?f=json`) before a name search. In Alberta the field is `NAME`, not
`PARK_NAME`.

**Never matched:** BLM's surface-manager layer (BLM_Natl_SMA). It names the owner, not the park.

### The grade each plug-in gives (grades.md / grades.json)

Each kind gets:
- PASS or FAIL against the bar;
- what was measured;
- why it fails;
- the top 5 miss reasons;
- 5 example parks;
- what chat 11 still has to sample.

The bars:

| Kind | Bar |
|---|---|
| outline | Rule G above. Chat 11 samples 30 joins per key file and needs 30/30. Finder: at least 95% re-found, 25% or more extra parks, at least 85% YES |
| docs | The link opens and names the park. The same file is not used by more than 3 parks, is not a sign, logo or letterhead, never replaces a map marked ok, and is never Wikipedia, tourism or an app |
| parking | About 30 sampled points with 27-28/30 right. Zero on the wrong park, zero positive west longitudes, zero duplicate facilities (one facility listed under 2+ parks). No wilderness, office, hotel or road-number labels |
| camping | About 97% of facts match the agency page. A fact from golf, a marina, a pool or a picnic shelter fails. Camp layers: at least 95% real campgrounds, 0 picnic shelters, 0 boat ramps |
| hours / fees (KY only) | A 12-row sample, 12/12 to pass. No marina or scuba hours, no bare "10 AM - 4 PM" fragments, no "Open seasonally" under hunting hours |
| trail | The managing agency's own line, the name matches, the POTA pin within 200 m (`grader.trail_pin_m`). National historic trails the agency marks approximate stay approximate. A trail in two parks is "Overlapping boundaries", not a failure |
| 2-fers | Never automatic: the waiting room only (`fers-waiting-room.json`, chat 8 + chat 11). Parks that only touch do not count; a trail with no land boundary counts within 100 ft of its line (water trails: the water's edge); a wild / scenic river corridor uses its own boundary; a 3-fer needs a spot within 100 ft of the trail inside the overlap patch |

---

## 2. Install it (one time)

You need **Python 3.12** (3.11 or newer works). Then run:

```bash
cd kpc_engine
python3 -m venv .venv && source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python kpc_engine.py selftest                              # should say "15 passed"
```

**Optional:** some park pages only fill in their text with JavaScript. To read those, add the headless browser:

```bash
pip install playwright && python -m playwright install --with-deps chromium
export KPC_BROWSER=1
```

The browser is never used to get past a robot check, a certificate warning or a sign-in.

**The contact in the User-Agent.** Agencies can see who is asking: the engine adds the club's contact to its honest
User-Agent. It is already set, both in the engine and in the workflow, to:

```
https://github.com/KentuckyPortableClub (Kentucky Portable Club ham radio club)
```

This is not a secret, so you have nothing to set. Only set `KPC_CONTACT` if the club ever changes it:

```bash
export KPC_CONTACT="https://github.com/KentuckyPortableClub (Kentucky Portable Club ham radio club)"
```

**Where the club's files come from:** two read-only folders, plus an optional POTA folder.
- `--data`: a KPC-Data checkout.
- `--links`: a KPC-Links checkout (`KentuckyPortableClub/KPC-Links`, read-only).
- `--pota` (optional): a folder of POTA park lists, used when the club files are not there. These are saved
  `https://api.pota.app/program/parks/<CC>` or `/location/parks/<US-KY>` lists.

---

## 3. Run it

### The whole thing

```bash
python kpc_engine.py run --data ../KPC-Data --links ../KPC-Links --out engine-out \
    --areas US-KY,US-TN,CA-ON,GB,MX --max-minutes 52 --resume
```

### One plug-in at a time

Add `--kinds` (one or more, comma separated):

```bash
python kpc_engine.py run ... --kinds outline            # boundaries only
python kpc_engine.py run ... --kinds docs               # park page + map
python kpc_engine.py run ... --kinds parking            # parking / trailheads / boat ramps (US + Canada)
python kpc_engine.py run ... --kinds camping            # campgrounds (US + Canada)
python kpc_engine.py run ... --kinds trail              # trail lines (US + Canada)
python kpc_engine.py run ... --kinds hours,fees,closures --areas US-KY   # Kentucky only; other areas are refused
```

### Only the missing list

```bash
python kpc_engine.py gaps --data ../KPC-Data --links ../KPC-Links --out engine-out --areas US-KY
```

### Useful switches

| switch | what it does |
|---|---|
| `--areas US-KY,CA-ON,GB` | which states, provinces or countries. The environment variable `AREAS` does the same (for kpc_shard / Actions). **Left out or blank = every area the club files know, in the club order** (Kentucky, rest of US + Canada, rest of North America, W1-W10, everyone else). A blank list never means "do nothing". |
| `--kinds outline,docs` | which plug-ins (default: all of them) |
| `--max-minutes 52` | stop safely after 52 minutes and **exit with code 3**; run again with `--resume` to carry on |
| `--resume` | skip parks that are already done (read from `work/*/state-*.json`) |
| `--limit 20` | only the first 20 parks per area (handy for a try-out) |
| `--workers 8` | parallel workers (8 is the agreed maximum) |
| `--steps L0,L1,L4` | turn ladder steps on or off (for example skip the slow ArcGIS Online search) |
| `--cache DIR` | where downloaded pages are kept (pages 7 days, layers and sitemaps 30 days) |
| `--offline` | use the cache only, no internet (for testing) |

**Exit codes:**
- `0`: finished.
- `3`: stopped at `--max-minutes`. Run the same command again with `--resume`.

### Club switches (config/rules.json), regrading and rulings (round 3, Nov 1)

* **Switches.** `config/rules.json` holds per-plug-in on/off and areas (hours / fees / closures: `US-KY`; parking / camping /
  trail: `US-*`, `CA-*`; outline / docs: `*`), the KY hours parsing rules, the optional checks, the source-policy rules and the
  grader numbers. Defaults are today's rules exactly. Per run: `--scope hours=US-KY,US-TN`, `--disable closures`,
  `--disable hours_rules.reject_fragments`, `--set grader.rg12_m=200`. Every run writes `active-config.json` and a rules banner
  on `grades.md` / `board.md`; anything off its default is shown as a WARNING. Switching OFF a source-policy rule stamps every
  affected row `source_policy: non-official: ...` with grade `approx`, so it never passes as official. The safety rules (honest
  User-Agent, no bypassing robots / Cloudflare / captchas / sign-in, no tokens from public maps, no TLS click-through) are
  LOCKED: no switch exists. Full table: [TUNING.md](TUNING.md#6-turning-rules-on-and-off).
* **Regrade without the web:** `python3 kpc_engine.py grade --out OUT [--kinds parking]` reruns `postprocess()` + the graders on
  saved rows and writes `grades-regrade.md` / `.json`.
* **`--check-all camping,trail`:** check these kinds on every park in scope, not only gap rows (audit / sample runs).
* **Club rulings (`registry/rulings.json`).** `pin only` (US-0658, US-1879, US-6281: official layers exist (W-10), listed in
  `official_found`; a find is only a candidate for chat 11), `note` (US-0896: the club's YES WSR line stands) and `hold`
  (GB-0889 Glen Nant: held by the club; the NatureScot record is kept as evidence).
* **WDPA guard + rule W-10 (round 4).** A layer that cites WDPA / Protected Planet / UNEP-WCMC (name, address, description,
  licence, fields) is never an ordinary source. It is rejected whenever an official layer has a record for the park. Only
  when nothing official answered and nothing was blocked, `registry/last_resort.json` may be asked: always g='approx',
  labelled 'WDPA (last resort)', never SURE or found (switch `source_policy.wdpa_last_resort`).
* **EU compilation rule.** EEA CDDA / discomap layers are always *approximate* and ranked after national layers. When the
  national agency's own layer is found and verified, it replaces the EU row and the park becomes official.
* **Exports match the club's sample files** (`fixtures/handback_samples/`, checked by `tests/test_export_shapes.py`). 
  `docs-pagefix` (round 4) is two files in the club's exact shapes: `docs-pagefix-us-<name>.csv` keyed by the hours-fees
  workbook's Parks-sheet row (`config/handback.json` / `KPC_HF_WORKBOOK_US`; no workbook or no row = the ref + "mapping
  needed") and `docs-pagefix-ca-<name>.csv` keyed by POTA ref (`tests/test_pagefix.py`).

### Hand the finds back to the club (export)

```
python kpc_engine.py export --out engine-out --name nov1
```

This writes `engine-out/handback/` in the shapes from HANDBACK_FORMATS.md. The bots read these files from KPC-Data
branch `intake-files`. Copy them there by hand: the engine never pushes.

| File | What is in it | Shape |
|---|---|---|
| `external-sources-<name>.json` | US/CA layers: `{"Parks\|US-1234": [url], "Trail\|US-4567": [url]}` | exact |
| `world-sources-<name>.json` | world layers: `{"rest": {ref: {"layer", "field"}}, "other": {...}}` | exact |
| `hardlook-<name>.xlsx` | Park number, NEW official layer URL, Name field, Record id / name, Status, Notes | exact |
| `docs-found-<name>.json` | `{ref: {st, page, map, map_page, kind, agency}}` | exact |
| `docs-pagefix-<name>.csv` | ref, st, page, page_title, page_how, date | closest (no example) |
| `parking-hunt-<name>.json` | the `data/access/<area>.json` shape, by area | closest (no oct31 example) |
| `camping-<name>.json` | the `campgrounds/<area>.json` shape (inside / nearby), by area | closest (no oct31 example) |
| `acres-<name>.json` | `{ref: {acres, source_layer, record, ...}}`, only SURE US/CA rows | closest (no oct31 example) |
| `portals-<name>.json` | the `state-gis.json` "portals" shape `{ST: [[label, url]]}`, from the club atlas | closest |

How the rows are chosen:
- Only `found` and `candidate` rows are exported. UNLIKELY rows never are.
- All answer columns stay blank for chat 11.
- Files with a closest shape carry a `_shape_note`, and `handback/README.txt` lists them.

### A try-out without the club repos

Use a POTA list folder only:

```bash
python kpc_engine.py run --pota /path/to/pota-lists --out try --areas US-KY --limit 10 --kinds outline
```

---

## 4. Run it on GitHub Actions, step by step

A ready-made workflow is in `.github/workflows/kpc-engine.yml`.

1. **Where it lives (club answer, round 3).** The engine runs inside **`KentuckyPortableClub/KPC-Data`**:
   - put this folder at `kpc_engine/` in KPC-Data, and the workflow file at `.github/workflows/kpc-engine.yml` there;
   - it **reads** KPC-Data (club data, never edited);
   - it **writes** its results **only** to KPC-Data's **`tools-out`** branch (folder `engine-out/part-N/`, hand-back files included);
   - it **reads, never writes,** **`KentuckyPortableClub/KPC-Links`** (the website: world maps and Kentucky's files).
     The engine refuses an `--out` folder inside the KPC-Links checkout.
2. **Nothing to set.** Both repo names are written into the workflow (`KPC_DATA_REPO`, `KPC_LINKS_REPO`) and into
   `core/config.py`, together with `KPC_CONTACT`. The workflow asks for `contents: write` only so its last step can push
   to `tools-out` with GitHub's own built-in job token. No keys, no other tokens.
   - For a fork or a try-out, set the environment variables `KPC_DATA_REPO` / `KPC_LINKS_REPO` / `KPC_RESULTS_BRANCH`.
3. **Check the parts.** The `matrix` lists up to 8 parts. Each part is a list of areas, and they run side by side:
   - Kentucky on its own;
   - the neighbouring states;
   - Canada;
   - two world groups.
   Change the area lists to suit. Keep parts that hit the **same** national servers few, since each part keeps its own
   2-second-per-host pace.
4. **Run it.** Go to **Actions → kpc-engine → Run workflow**. It also runs every night at 07:17 UTC.
5. **Each job:**
   - installs Python 3.12;
   - restores the cache (pages and the `state-*.json` resume files);
   - runs the tests;
   - runs the engine for 50 minutes.
   If time runs out it exits 3, and the **next run carries on** where it stopped (`--resume` plus the cache).
6. **Get the results.** Open the `tools-out` branch of KPC-Data → `engine-out/part-<N>/` (also kept 14 days as the run's
   **Artifacts** → `engine-out-<part>`). Start with `board.md`, then the waiting-room
   files (section 9).

---

## 5. The source list (registry): add or fix a source

The registry is the engine's list of official map layers, already tested. It lives in two files:

- `registry/us_ca_sources.json`: the US and Canada, made by `registry/_seed_usca.py`, plus the layers that discovery found
  (`registry/us_ca_discovered.json`).
- `registry/world_sources.json`: the world, made by `registry/_seed_world.py`.

- `registry/pack_sources.json`: **the club's own approved lists**, read first. It is made by
  `python registry/_seed_pack.py --pack <the unzipped sources folder>` and includes:
  - every layer chat 11 said YES to;
  - the club keys;
  - the state GIS tables;
  - the access, trail and camp lists;
  - chat 11's NO rows (never offered again);
  - the failed hosts;
  - the local-language park words.
  Re-run it whenever the club updates the pack.

**Always edit the `_seed_*.py` file, not the JSON.** Then rebuild the JSON and re-verify (section 6). Re-building keeps every
earlier verify result.

### What one entry holds

| field | meaning |
|---|---|
| `id` | a short unique name, e.g. `US-KY-stateparks` |
| `area` / `cc` | `US-KY`, `CA-ON`, or a country code like `GB`. National layers use `US` or `CA`. |
| `ptype` | park type (state_park, wma, nwr, nature_preserve, state_forest, provincial_park ...) |
| `use` | `outline`, `parking`, `camping` or `trail` (`also` = a second use) |
| `kind` | `arcgis`, `wfs`, `ogcapi`, `geoadmin` or `download` |
| `url` | the layer address (ArcGIS: ends in `/MapServer/<n>` or `/FeatureServer/<n>`) |
| `layer` | WFS / OGC API: the layer (type) name |
| `name_field` | the field that holds the park name |
| `srs` | the layer's coordinate system number (WFS / download), e.g. 27700 for Great Britain |
| `agency`, `official_basis` | who publishes it, and why we count it as official |
| `grade` | `official`, or `approximate` (EU compilation, proclamation lines). **Approximate is never a full YES.** |
| `pota_words` | a pattern for which POTA parks verify should test with (e.g. `State Park|State Resort`) |
| `verified` | written by verify.py: status, test hits and date. Do not type this by hand. |

### Worked example 1: adding an ArcGIS layer

Say you found Kentucky's state park boundaries at
`https://kygisserver.ky.gov/arcgis/rest/services/WGS84WM_Services/Ky_State_Parks_Features_WGS84WM/MapServer/8`.

1. **Open the layer page in a browser** (that exact address). Check three things:
   - **Geometry type** is *Polygon* (for an outline), *Point* (parking or camping) or *Polyline* (trails).
   - **Fields:** find the text field with the park name (here `PUBLIC_NAM`).
   - The publisher is a **government body**. The server name or the ArcGIS organisation must be official.
2. **Check it answers.** Add `/query?where=1%3D1&returnCountOnly=true&f=json` to the address. You should see `{"count": 49}`
   or similar. If you get `"Token Required"` or a sign-in page, **stop**. That layer is "needs sign-in" and we skip it.
3. **Add one line** to `registry/_seed_usca.py`, near the other Kentucky lines:
   ```python
   add('US-KY-stateparks', 'US-KY', 'state_park', 'outline',
       'https://kygisserver.ky.gov/arcgis/rest/services/WGS84WM_Services/Ky_State_Parks_Features_WGS84WM/MapServer/8',
       'PUBLIC_NAM', 'Kentucky Department of Parks', 'kygisserver.ky.gov (Commonwealth of Kentucky GIS server)',
       r'State (Park|Resort|Historic)')
   ```
   The order is: id, area, park type, use, url, name field, agency, why it is official, and which POTA names to test with.
4. **Rebuild and verify:**
   ```bash
   python registry/_seed_usca.py
   python registry/verify.py --registry registry/us_ca_sources.json --pota /path/to/pota-lists --id US-KY-stateparks
   ```
   You want to see `verified 4/8` (or better). That means 4 of 8 test parks matched a record by name with their pin inside.

**Fixing an ArcGIS entry:**
- Wrong name field: change the 6th value.
- The layer moved to a new number (`/MapServer/8` became `/9`): fix the url.
- Rebuild and verify again.

**Do not** fix a source by adding a `token=` you found inside a public web map. That is not allowed.

### Worked example 2: adding a WFS layer

Say Sweden's protected-area service is at `https://geodata.naturvardsverket.se/naturvardsregistret/wfs`.

1. **Find the layer name.** Open `<url>?service=WFS&request=GetCapabilities` in a browser and look for a `<Name>` such as
   `Naturvardsregistret_WFS:SkyddadeOmraden`. Note its coordinate system (`EPSG:3006`).
2. **Find the name field.** Open
   `<url>?service=WFS&request=DescribeFeatureType&typeNames=<layer>` and look for the name field (here `NAMN`).
3. **Add the entry** to `registry/_seed_world.py`:
   ```python
   add('SE-NV-skyddade', 'SE', 'Sweden', 'Naturvårdsverket (Swedish EPA)', 'wfs',
       'https://geodata.naturvardsverket.se/naturvardsregistret/wfs', 'Naturvardsregistret_WFS:SkyddadeOmraden', 'NAMN',
       'nature reserves, national parks', srs=3006, pota_words=r'Naturreservat|Nationalpark')
   ```
   The engine handles the axis order by itself. Some systems (Sweden 3006, Romania 3844 and others) list north first, and the
   engine works that out from the EPSG number.
4. **Rebuild and verify:**
   ```bash
   python registry/_seed_world.py
   python registry/verify.py --pota /path/to/pota-lists --id SE-NV-skyddade
   ```

The other kinds work the same way:
- **OGC API:** `kind='ogcapi'`, `url` = the service base (the part before `/collections`), `layer` = the collection id.
- **Download:** `kind='download'`, `url` = an official zip of shapefiles or KML, `srs`, `name_field`.

---

### Round 5: the master workbook import and the retry list

`registry/master_nov1.json` (built by `registry/import_master.py` from a read-only copy of the club's master workbook) is
loaded last: its new sources are ranked after ours, and rows we already had keep the workbook's status / notes under `wb`.
`registry/retry.json` (from `registry/import_retry.py`) is the retry list; each run copies it to `retry-list.json` for the
areas it ran. `config/work_order.json` seeds the work order with the Mapping handoff's biggest gaps. See AGENT_TIPS.md
"Round 5" before touching any of these. Never write to the workbook.

## 6. Re-check (verify) the sources

`registry/verify.py` really queries each source:
1. a count query;
2. a query at the pins of real POTA parks of that area and type;
3. a name match.

It writes `verified: {status, matched/asked, examples, date}` into the registry. Possible statuses:

| status | meaning |
|---|---|
| `verified` | a named record holds a POTA pin and the names match. The engine uses it. |
| `answers` | the service works but no test park matched. The engine still uses it, lower in the order; check the name field or `pota_words`. |
| `blocked` | refused us (robots, TLS, 403, needs sign-in). Not used. The reason is written down; retry later. |
| `error` | broken (bad URL, wrong layer number). Fix it. |

```bash
# everything in the world list
python registry/verify.py --pota /path/to/pota-lists --n 10
# only the US / Canada list, only what is not yet verified
python registry/verify.py --registry registry/us_ca_sources.json --pota /path/to/pota-lists --only-unverified
# one area, or one source
python registry/verify.py --registry registry/us_ca_sources.json --pota /path/to/pota-lists --area US-KY
python registry/verify.py --pota /path/to/pota-lists --id GB-SCT-nnr
# the same thing through the main command
python kpc_engine.py verify-registry --pota /path/to/pota-lists --cc GB,DE
```

Re-verify about once a month. Agencies renumber and move layers; the engine also notes renumbered layers in
`findings.jsonl`.

**Finding new US / Canada layers by itself** (searches ArcGIS Online and keeps only government organisations):

```bash
python registry/discover_usca.py --areas US-OH,US-IN     # writes registry/us_ca_discovered.json
python registry/discover_usca.py --world hunt            # the world, in the club's hunt order
python registry/_seed_usca.py                             # merges what was found (max 6 per area and park type)
python registry/verify.py --registry registry/us_ca_sources.json --pota /path/to/pota-lists --only-unverified
```

---

## 7. Add a new country, state or province

1. **Get the POTA park list.** Save `https://api.pota.app/program/parks/<CC>` as `<CC>.json` in your POTA folder. For one US
   state: `https://api.pota.app/location/parks/US-XX`.
2. **Find the official layers.** Start with the national protected-areas agency, then the regional ones. Good places:
   - the agency's own ArcGIS server or GeoServer;
   - the national INSPIRE geoportal (Europe);
   - the national open-data portal.
   **Not allowed:** OSM, Google, Wikipedia or Wikidata, WDPA / Protected Planet, AllTrails, blogs.
3. **Add each layer** to `_seed_world.py` (or `_seed_usca.py`) as in section 5, then rebuild and verify.
4. **Add the agency's web domain** so the page finder trusts it:
   - in `plugins/docs.py`, under `AREA_DOMAINS`;
   - and, if it is not a `.gov` / `.gouv` / `.gob` style domain, in `official_domain()` in `core/agencies.py`.
5. **Do a short try-out:**
   `python kpc_engine.py run --pota <folder> --out try --areas <CC> --limit 10 --kinds outline,docs`.
6. **Read `try/board.md` and `try/whynot.json`.** If many rows say `no-layer`, the country still needs a layer. If they say
   `blocked`, see section 10.

EU countries also get the EU compilation of national data, always graded **approximate**. Replace it with the national layer
as soon as you find one.

---

## 8. Add a new plug-in

A plug-in is one Python file in `plugins/` with a class that has five parts:

```python
from .base import Plugin, dump, today
from core.notes import Notes

class Lighthouses(Plugin):
    KIND = 'lighthouse'              # its name (also add it to core/scope.py: which areas it may work on)
    GAP_KINDS = ('lighthouse',)      # which "missing" kinds it answers (core/gaps.py decides when a park is missing it)

    def work_row(self, agency, row, eng, pass_no):
        p = eng.park(row); nt = Notes()
        # ... look things up with eng.P.get(...) (the polite fetcher) and eng.registry.for_area(...) ...
        nt.looked('some official source', 'no hit')
        return {'ref': row['ref'], 'area': row['area'], 'park': p.get('n'), 'kind': self.KIND,
                'status': 'not found', 'whynot': {'tag': 'no official source yet'}, 'notes': nt.as_dict()}

    def write(self, results, out_dir, eng=None):
        dump({r['ref']: r for r in results if r.get('status') == 'found'}, f'{out_dir}/lighthouses.json')

    # grade() comes from Plugin (rows, found, blocked, hit rate); override it to add your own checks.
```

Then:
1. Add it to `PLUGINS` and `ORDER` in `kpc_engine.py`.
2. Add it to the scope sets in `core/scope.py`.
3. Add a test in `tests/`.

The engine already gives it the agency grouping, 8 workers, the two passes, resume, the checks and the board.

**House rules for a plug-in:**
- Fetch only through `eng.P` (that keeps the 2-second pace, robots.txt and the cache).
- Write only into `out_dir`.
- Say "blocked" when a site refuses. Never say "not found" for that.

---

## 9. Read the results and the waiting room

Everything is in the `--out` folder.

| file | what it is | who uses it |
|---|---|---|
| `board.md` | **start here.** Missing yesterday, then found today, then still missing, per kind and area; the top why-not reasons; blocked hosts; pass 1 vs pass 2 | everyone |
| `questions.json` | outline **questions**: `{ref, st, url, name_field, agency, kind, licence, answer:"", checked_by:""}`, plus evidence (record, `where`, `record_link`, `pin_m`, acres, tier, band, rule, notes) | the waiting room (`data/waiting/questions/layers.json` shape) |
| `whynot.json` | why each still-missing park is missing (`no-layer`, `blocked (...)`, `approximate only` ...), and the last ladder step reached | finder work list |
| `found-layers.json` | new official layers found by L1-L3 (used at L0 next time) | registry upkeep |
| `picture-maps.json` | official PDF / picture maps found on park pages (never traced) | the picture-map saver |
| `parcels.json` | L5 parcel leads (record number, owner, layer) and the areas with no parcel layer yet | a person checking historic sites and small parks |
| `docs-found-<area>.json` | official page + map per park: `{ref: {st, page, map, map_page, kind, date, agency, notes}}` | the documents merge |
| `access/<area>.json` | parking / trailheads / boat ramps `[lat, lon, "Label (Agency)", how]` (`how` = `name` or `place`) | the access merge |
| `campgrounds/<area>.json` | campgrounds `inside` / `nearby` per park | the camping merge |
| `trails/<area>.json` | official trail lines per park (name, agency, length, envelope) | trails |
| `hours/US-KY.json`, `closures/US-KY.json` | Kentucky hours, fees and closures, word for word, with the page link | KY info |
| `pin-typos.json` | **R-G13**: a name match far from the pin **and** an official point with that name on the record. A question for the club. **Pins never move.** | the club |
| `fixes.csv` | POTA website links that are dead, moved or point at the wrong park, with the correct official page when found | the club |
| `blocked.csv` | every refusal: domain, park, kind, reason, date, url. Retried next run. | anyone retrying |
| `spot-check.md` (+ `spot-check-<kind>.md`) | 20 random rows to check by hand: open the link, write YES or NO | chat 11 / checkers |
| `check-problems-<kind>.json` | rows the engine's own checks threw out (dead link, name mismatch, page clutter) | debugging |
| `grades.md`, `grades.json` | **one grade per kind, in chat 11's shape:** PASS or FAIL against the bar in the instructions, what was measured, the top reasons for misses, and 5 example parks (plus the plug-in's own counts under `details`) | chat 11 |
| `gaps.json`, `gaps-summary.md` | the missing list | everyone |
| `findings.jsonl` | the shared notebook of tricks learned (odd name fields, renumbered layers, blocked hosts) | the engine and people |
| `agencies.json` | each agency's servers, domains and the date they were last read (re-read after 30 days) | the engine |
| `work/<kind>/` | resume state and raw results per worker | resume |

### How to answer a question in the waiting room

For each row:
1. Open `record_link`. That is the official record.
2. Open `url`. That is the layer.
3. Read `notes.why_this_record` and `notes.confidence.double_check`.
4. If it is the right park, write `answer: "YES"`; if not, `"NO"`. Put your name in `checked_by`.

Some things to keep in mind:
- A **WEAK** or **CONFLICT** band, or an `approximate` grade, needs a closer look. Approximate is never a full YES.
- **R-G12** (the pin is just outside, within 150 m) is only a candidate.

---

## 10. Troubleshooting

| what you see | what it means | what to do |
|---|---|---|
| `blocked (robots)` | the site's robots.txt says no | Nothing. We obey it. It stays blocked and is never marked "not found". |
| `blocked (HTTP 403: server refuses this client)` | the server refuses scripts | Leave it. With `KPC_BROWSER=1` the engine may read a plain page through the browser. **Never** change the User-Agent to look like a browser. |
| `blocked (Cloudflare / robot challenge)` | a robot check | Stop. We never get around robot checks. Log it; a person can look at the page. |
| `blocked (TLS failure)` | a certificate problem | We never click through certificate warnings. Retry another day. |
| `token-only (needs sign-in)` | the layer wants a key or login | Skip it. Mark it "needs sign-in". Never use a token found in a public web map. |
| `blocked (timeout)` / `blocked (host resting: 3 strikes)` | the server is slow or down; after 3 failures a host rests for a day | Run again tomorrow; `--resume` keeps your place. |
| `HTTP 400` / `error: Invalid or missing input parameters` in verify | wrong layer number, a group layer, or a wrong field | Open the layer page and fix the url or name field (section 5). |
| `Pagination is not supported` | an old ArcGIS server | Already handled: the engine retries without paging. |
| WFS gives no hits but the layer works | axis order | Already handled for EPSG codes that list north first. Check the `srs` in the entry. |
| the run stopped with exit code 3 | the time limit (`--max-minutes`) | Run the same command with `--resume`. |
| a row says `no verified layer for XX in the registry yet` | no tested source for that area | Add one (sections 5 and 7). |
| `note: using vendor/kpc_manners.py` | the club's own copy of the tool modules was not found | Set `KPC_TOOLS_DIR` to the folder with the club's `kpc_manners.py`, `kpc_order.py` and `kpc_intake_reader.py`. |
| tests fail | something in the code changed | `python -m pytest -q tests -x` shows the first failure. |

**Starting fresh:**
- Delete the `--out` folder, or just `work/`, to redo everything.
- Delete the `--cache` folder to fetch every page again.

---

## 11. The rules sheet

1. **Official sources only.** Government or agency sites and their map services.
   **Never:** OSM / Overpass / Geofabrik, Google, AllTrails, Gaia, Strava, TripAdvisor, Yelp, Wikipedia / Wikidata, blogs,
   WDPA / Protected Planet / UNEP-WCMC, or search-engine snippets.
2. **We never spoof a User-Agent, never click through certificate warnings, never sign in, never get around a robot check,
   and never use an access token found inside a public web map.**
3. **No keys, no tokens.** A source that needs one is written down as "needs sign-in" and skipped.
4. **Every link must open. Never guess a URL.** Copy text **word for word**, in its own language.
5. **Blocked is not "not found."** Blocked rows are logged in `blocked.csv` and retried.
6. **Be polite:** at most 1 request every 2 seconds per website, and never more than 2 workers on one agency's site. Obey
   robots.txt with no exception (Nov 10: the old ArcGIS REST exemption is gone; a 401 / 403 robots.txt is a no). Before any
   request, the club's host rules (`kpc_host_rules.py`) apply. Never-contact hosts, every `services*.arcgis.com` host
   (`services-eu1` too) and `apps.fs.usda.gov` get no request at all, robots.txt included. Those layers go on the one
   needs-download list (`data/needs-download.json`), and the engine never saves a layer.
7. **Write only inside `--out`.** Never edit the club's data.
8. **POTA pins never move.**
   - **R-G12:** a record whose edge is within 150 m of the pin is a candidate only.
   - **R-G13:** a likely pin typo goes to `pin-typos.json` as a question.
9. **The EU compilation is approximate**, never a full YES.
10. **Hours, fees and closures are Kentucky only.** Parking, camping and trails are US and Canada only. The engine refuses
    anything else.
11. **The engine decides nothing.** Every find is a question for a person.

---

## 11b. Agency contacts (there are none on purpose)

The engine keeps **no agency contacts** and the README lists **no people**. **Bots never send email.**

When a source is wrong, moved or gone, a person opens the agency's own open-data or GIS portal and uses the contact link the
agency publishes there, if it publishes one. Where to look:
- `registry/AGENCY_CONTACT_PAGES.md` lists the portals the club wrote in `tips/agency-atlas/` (15 areas so far; most US/CA
  atlas pages still say "(add)"). Rebuild it with `python registry/_seed_contacts.py --pack <sources folder>`.
- For any other source, the right portal is the home of the server the registry entry points to (for example the agency's
  own `.../arcgis/rest/services` site). Look for its "Contact" link. Never guess an address.

## 12. Folder map

```
kpc_engine/
  kpc_engine.py            the one command: gaps / run / selftest / verify-registry / export / grade / doctor
  core/key_doctor.py       v0.5.0 key doctor (read-only check-up of the answer-key line)
  patches/                 v0.5.0 bot fixes for KPC-Links / KPC-Data (NOT applied), orig/ files, patch_tests/, STORAGE_PLAN.md
  core/                    the engine's parts
    adapters.py            THE ONE place that reads club files (fix a path or field name here)
    polite.py  read.py     polite fetching (robots, 2 s per host, cache) and the page-reading ladder
    gis.py  geo.py         ArcGIS / WFS / OGC API / downloads; pins, distances, acres
    names.py               name matching in many languages, tiers T-1..T-6, kind check
    gaps.py  agencies.py   the missing list; grouping by agency
    workers.py  passes.py  8 workers with resume; two passes
    checks.py  board.py    link / identity / clutter checks, spot-check; the board
    findings.py  notes.py  shared findings log; the notes standard
    registry.py  scope.py  the source list; the KY-only / NA-only scope guard
  plugins/                 outline, docs (page + map), points (parking / camping / trail), ky_info (hours / fees / closures), stubs
  registry/                source lists, their builders, verify.py, discover_usca.py
  tests/  fixtures/        offline tests and small sample club files (made from the ANSWERS rows)
  vendor/                  fallback copies of kpc_manners / kpc_order (the club's own copies are used when found)
  .github/workflows/       the sample GitHub Actions workflow
```

## 13. Key doctor, bot patches and storage (v0.5.0)

### The key doctor

The key doctor is a check-up of the answer-key line. It only **reads** your KPC-Links and KPC-Data checkouts, and it
writes only to `OUT/key-doctor/`.

```
python3 kpc_engine.py doctor --links ../links --data ../kpcdata --out out
python3 kpc_engine.py doctor --links ../links --data ../kpcdata --out out --tasks nos,storage
python3 kpc_engine.py doctor ... --enable key_doctor.per_park_release     # also write the per-park release copies
```

| File in `out/key-doctor/` | What it tells you |
|---|---|
| `nos.json` | How many of chat 11's NOs landed in `overrides.json`, which are missing, and which came back in a built key. |
| `overrides.fixed.json` | A copy of `overrides.json` with the missing NOs put back. A person copies it over after looking. |
| `release.json` (+ `release/`) | For a LIVE-FILTERED key, which parks pass and which are held. The filtered files appear only with the switch on. |
| `approvals.json` | YES approvals missing a field (`chat2` on the Canada key, `path` on the world key). |
| `fers-ids.json` | The stable 2-fer ids, and which old ids carry over. |
| `line.json` | Each area's stage (build, check, grade, save, release, fers, review), with the frozen build stamp while it is graded. |
| `stuck-YYYY-MM-DD.md` | Today's stuck list, with who should act. |
| `storage.json` | Files over 80 MiB (WARN) or 95 MiB (RED), and held copies that live already has. |

The exit code is 1 when something is red: a missing NO, a NO that came back, or a RED file. That makes it usable as a
nightly Action step.

### The bot fixes (patches)

`patches/` holds the fixes for the key, 2-fer and tracer bots as **patch files, not applied**. See
[patches/README.md](patches/README.md) for:
- what each one fixes;
- the switch for each new rule (the defaults match today);
- how to try them on a test build first;
- what needs Brandon's OK.

Run their tests with `python3 -m pytest -q patches/patch_tests`.

### Storage

GitHub refuses any file over 100 MiB. The doctor's size guard warns at 80 MiB and goes red at 95 MiB.
`US-AK.json.gz` (103.5 MB ≈ 98.7 MiB) is already red.

The plan for splitting big files, or moving them to LFS or a release asset, is in
[patches/STORAGE_PLAN.md](patches/STORAGE_PLAN.md). It is **not applied**, because it changes how the site reads the
files, so it needs Brandon's OK.
