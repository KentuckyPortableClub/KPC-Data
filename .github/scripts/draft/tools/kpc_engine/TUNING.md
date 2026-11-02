# TUNING.md: how to tune the KPC park-info engine (for other agents)

Read this before changing any threshold. The engine **decides nothing**: every knob below only changes what is *offered* to the
club's checker chats, how it is ranked and how it is graded. Tune in small steps, rerun **only the graders** on saved output
(section 3), and add a regression test for every miss chat 11 reports (section 4).

Contents: 1 knobs · 2 worked examples · 3 regrade without the web · 4 regression tests from chat 11 misses ·
5 do-not-loosen list · 6 turning rules on and off (switch table, LOCKED rules)

---------------------------------------------------------------------------------------------------------------------------
## 1. Every tunable knob

Legend: **where** = file and setting · **default** · **what it does** · **safe range** · **symptom that says change it**.
Knobs marked (switch) live in `config/rules.json` and can be changed per run with `--set` / `--enable` / `--disable` /
`--scope` without editing code (section 6). Everything else is a constant in code: change it in a pull request with a test.

### 1.1 Rule G tiers (outline matching): `core/rule_g.py`, `tier_g()`

The order of checks is fixed; the first one that fails returns UNLIKELY:

1. `DENY_LAYER` (surface-manager layers, e.g. BLM SMA) · 2. WDPA guard (`cites_wdpa`) · 3. never-use list · 4. forestry kind
guard · 5. distance (R-G12) · 6. containers · 7. line vs polygon · 8. kind match · 9. size WAY OFF.
Then **SURE** = names equal once kind words are stripped AND size PASS/unknown; **LIKELY** = names equal or overlap (size OFF
adds "a person looks"); else **UNLIKELY**.

| knob | where | default | what it does | safe range | symptom to change |
|---|---|---|---|---|---|
| SURE needs "equal" names | `tier_g`, `name_level()` | equal after strip | only exact core names are SURE | do not loosen | chat 11 finds a SURE that is a different park |
| LIKELY needs "overlap" | `name_level()` | 1+ shared core word, not generic | what becomes LIKELY | 1-2 words | too many LIKELY on generic words (add the word to `names.GENERIC` instead) |
| kind-word strip list | `KIND_STRIP` (rule_g) + `names.GENERIC` | district, management, unit, complex, … nnr, lnr | words removed before names are compared | add words, never remove "state"/"national" | "X WMA Unit 2" not matching "X WMA" → add the word |
| kind table | `KINDS` (rule_g:16) | state_park, state_forest, wma, nature_reserve, … (last kind in the name wins) | two places of different kinds never match | add kinds only | "Trail of Tears Park" vs the National Historic Trail → kinds already differ; a new pair clashing wrongly → add to `COMPAT` |
| compatible kinds | `COMPAT` (rule_g:39) | {state_park, state_rec_area}, {nature_preserve, natural_area, nature_reserve}, {national_park, nra} | kinds treated as the same | add pairs only with a chat 11 example | an official renamed kind (SRA→SP) shows UNLIKELY |
| aliases | `ALIASES` (rule_g:51) | official renames, Indigenous / French names | names that count as equal | official renames only, cite the source in a comment | a renamed park keeps failing name match |

### 1.2 Size bands (switch)

| knob | where | default | what it does | safe range | symptom |
|---|---|---|---|---|---|
| `grader.size_pass_max` | rules.json → `rule_g.size_band` | 1.5 | ratio (either way) still PASS | 1.2-2.0 | real outlines with GIS-vs-deed acreage drift land as OFF |
| `grader.size_off_max` | same | 5.0 | above this = WAY OFF → UNLIKELY | 3-8 | the whole-county/forest record still shows LIKELY (lower it) |
| `grader.parcel_low` / `parcel_high` | rules.json → `rule_g.parcel_hold` | 0.2 / 2.0 | parcel tracer holds anything outside | 0.2-0.5 / 1.5-2.0 | Salato (921 vs 229.85 ac) or Hiwassee (9.8x) style parcels getting through |

### 1.3 R-G12 distance (switch)

`grader.rg12_m` = **150** m. Used in `tier_g` (pin within N m + name match counts as "near"), `names._tier` (T-3 just
outside), `outline` STRONG/WEAK note, and the outline grader (`rg12_far`). Safe range **50-250**. Symptom: linear parks /
river-access pins that sit just outside a valid polygon fail → raise a little; chat 11 finds neighbours matched → lower.

### 1.4 Containers and line-vs-polygon (switches `checks.containers`, `checks.line_vs_polygon`)

* Containers: a record under 2+ parks' pins (or a management district) is UNLIKELY and, after the run, `postprocess()`
  re-marks every row sharing one record as `not found` with the evidence kept. Default **on**. Symptom to look at: a genuine
  2-in-1 park pair (POTA has two refs for one polygon) — handle that with a club ruling (`registry/rulings.json`), not by
  turning the check off.
* Line vs polygon: a trail / wild-river park only matches a line record, and the other way round. Default **on**.
  `LINE_KINDS = {trail, wild_river}`. Symptom: trails published as thin polygons → add the layer to the registry with
  `geom: line` rather than turning the check off.
* Forestry kind guard (`checks.forestry_kind_guard`, default on, `FORESTRY_LAYER` + `FOREST_KINDS`): forestry / woodland /
  compartment layers only match state or national forests (GB-0889 Glen Nant lesson).

### 1.5 Name normalization: `core/names.py`

| knob | default | what it does | symptom |
|---|---|---|---|
| `TRANS` + accent stripping | æ→ae, ø→oe, ß→ss, ł→l … then NFKD | "Pădurea" = "padurea" | a name in Romanian / Nordic letters fails to match → add the letter to `TRANS` |
| `GENERIC` | park, state, national, area, reserve … | words that never count as an overlap | LIKELY on "Lake" / "Creek" only → add the word |
| `LOCAL_WORDS` (from the pack per country) | Naturschutzgebiet, réserve naturelle, parc, Nationalpark … | local-language park words removed | a country's park word not stripped → add it in the pack, it loads automatically |
| `SITE_CODE` | `ROSCI0123`, `DE4321301` … | Natura 2000 codes stripped from names | a new code shape left in names |
| `KIND_WORDS` + `DOWN` | kind clash pushes a tier down one step | same words, other kind | — |

### 1.6 Map-match bands (outline tiers T-1..T-6 and bands): `core/names.py::_tier`, `plugins/outline.py::_finish`

| tier | meaning | band rules |
|---|---|---|
| T-1 | same normalised name, pin inside | STRONG if official + inside + no size flag + no clash |
| T-2 | every core word, pin inside | STRONG (same conditions) |
| T-3 | most words inside, or every word and within `rg12_m` | WEAK |
| T-4 | every word, pin outside | WEAK, never STRONG |
| T-5/T-6 | some words / words only in other fields | evidence only |
| CONFLICT | two official records name different parks | always a question |

`TIER_ORDER` (outline:349) sets which candidate is shown first. Safe change: none without a chat 11 example; these are the
spec's bands.

### 1.7 Docs bars (switches in `grader.*`)

| knob | default | does | safe range | symptom |
|---|---|---|---|---|
| `grader.docs_same_file_max` (old name `docs_shared_file_max` still accepted) | 3 | one map file used by more than N parks = "the same file is used by N parks" problem | 2-5 | a statewide brochure offered as a park map (lower) / a real 4-unit complex map flagged (raise, with a test) |
| `grader.docs_ky_tn_share` | 0.20 | bar: new map/page in ≥ 20% of KY+TN parks without one | spec value | — (only chat 11 changes bars) |
| `DOC_LOGO` regex (rule_g) | logo, letterhead, signage, sign, banner, icon, favicon, seal, header | image is a sign/logo, not a map | add words | logos offered as maps |
| `DOC_NOT_OFFICIAL` + never-use list | Wikipedia, tourism, app pages … | not official | do not loosen | — |
| `MAP_WORD`, `MAP_FILE` (docs.py) | maps, brochure, carte, karte, mapa, kaart, kort | what counts as a map link | add languages | a country's map links missed |

### 1.7b Trail bar and Overlapping boundaries (round 4)

| knob | where | default | symptom |
|---|---|---|---|
| `grader.trail_pin_m` | `rule_g.trail_bar` | 200 m | good trails held as candidates only because the pin sits a little further away (raise with `--set`, regrade, then ask chat 11) |
| agency's own line | `rule_g.agency_own`, `AGGREGATOR`, `agencies.AGENCY_DOMAINS`, `STATE_MAPPING` | the feature's agency must map to the park's agency domain; aggregated inventories (USGS aggregated trails) never count; a state mapping agency compilation (KyGovMaps, TN STS) counts only while the managing agency publishes no line of its own (switch `source_policy.state_mapping_compilations`) | a real agency layer held as "not the managing agency's own line": add the agency name -> domain in `AGENCY_DOMAINS`, with a test |
| name match | `rule_g.name_level` | equal or overlap | a trail with its own name (not the park's) is held as a candidate; a person looks |
| NHT approximate | `rule_g.trail_approx`, `APPROX_MARK` | national historic trails the agency marks approximate stay approx | — |
| Overlapping boundaries | `fers.from_trail_rows` | one trail feature under 2+ parks is labelled "Overlapping boundaries" (never "shared"), not a failure; a suggestion goes to `fers-waiting-room.json` | never auto: chat 8 + chat 11 |
| `grader.fer_line_ft` | `fers.zone` | 100 ft | trail with no land boundary: line + 100 ft (water trail: the water's edge + 100 ft); WSR corridor: its own boundary, no 100 ft; parks that only touch never count; 3-fer = a spot within 100 ft of the trail inside the overlap patch |

### 1.8 Parking filters

| knob | where | default | symptom |
|---|---|---|---|
| bad labels (`checks.point_label_filter`, `BAD_LABEL`) | rule_g:258 | wilderness, office, hotel, motel, lodge, headquarters, bare road numbers (US 60, KY 80, SR, CR …) | chat 11 marks a point label as wrong → add the word + a test |
| duplicate facilities (`checks.resolve_duplicate_facilities`; old name `resolve_shared_facilities` still accepted) | `rule_g.resolve_duplicates`, `postprocess` | one facility listed under 2+ parks stays only with the park whose pin is nearer | bar: 0 duplicate facilities. If "only a duplicate facility" misses look wrong, check pins first |
| wrong park | grader sample + `place` ties | point must be tied to the park by name or by sitting in its outline | chat 11's "0 on the wrong park" fails → tighten name ties, never loosen |
| west longitudes | `point_problems` (always on) | US/CA lon > 0 = error | — |
| `grader.parking_right_of_30` | 27 | bar: 27-28 of 30 right | spec value |
| `grader.parking_ky_tn_share` | 0.10 | bar: new points in ≥ 10% of KY+TN parks | spec value |

### 1.9 Camping

| knob | default | does | symptom |
|---|---|---|---|
| `grader.camp_layer_ok` | 0.95 | at least 95% of offered features must really be campgrounds | spec bar |
| `checks.camp_feature_filter` + `OTHER_BUSINESS` (rule_g:300) | golf, marina, pool, picnic shelter, shelter house, boat ramp/launch, scuba, restaurant, dining … | not a campground | a non-campground passes → add the word |
| fact match | the plug-in writes YES only from an official campground feature or the agency's camping page; otherwise NEARBY ONLY; never NO | — | — |
| `CAMP_WORDS` (adapters) | camp, campground, campsite, camping, cabin, shelter, rv | which parks are camping gaps (without `--check-all`) | — |

### 1.10 Kentucky hours / fees / closures parsing (switches `hours_rules.*`)

| switch | default | rule | symptom to change |
|---|---|---|---|
| `hours_rules.separate_marina_scuba` | on | lines naming marina, scuba, pool, golf, restaurant, dining, gift shop, lodge, front desk, pro shop, boat rental are not park hours (`HOURS_OTHER`) | (Oct 31 sample failed on this) |
| `hours_rules.reject_fragments` | on | a bare "10 AM - 4 PM" with no subject is rejected (`BARE_TIME`) | — |
| `hours_rules.hunting_hours_apart` | on | hunting / season lines (deer, turkey, dove, waterfowl) are not park hours (`HUNTING`) | — |
| `TIME`, `FEE`, `CLOSE`, `SUB` (ky_info.py) | — | what a line must contain; which sub-pages are read | a park's hours page uses a new word ("sunrise to sunset" style) |
| lines kept | 8 read, 4 kept per kind | — | — |
| closures freshness | 7 days (`gaps.py`) | closures older than a week are a gap | — |

### 1.11 Politeness (LOCKED floor; you may only make it gentler)

| knob | where | default | safe range |
|---|---|---|---|
| per-host gap | `Polite(gap=2.0)` → `kpc_manners.Manners` | 1 request / 2 s per host | **≥ 2.0 only** (club rule) |
| retries / back-off | kpc_manners | 429/5xx back-off; 3 strikes = host rests a day (saved in `state.json`) | never lower |
| timeout | `Polite.get(timeout=40)` | 40 s | 30-90 |
| cache TTLs | `ttl_days` per call: pages 7, layer info / fields 30, `REREAD_DAYS` 30 | 7-60 |
| robots.txt | obeyed; ArcGIS REST exempt as kpc_manners says | locked |
| User-Agent | names the job + `KPC_CONTACT` | **LOCKED** |

Symptom: many "blocked (host resting: 3 strikes)" → do NOT speed up; rerun tomorrow with `--resume`.

### 1.12 Workers and shards

| knob | default | safe range | symptom |
|---|---|---|---|
| `--workers` | 8 | 2-12 | the per-host gap is enforced across workers, so more workers only help when many hosts are involved |
| workflow `matrix.part` | 8 parts (AREAS + `KPC_SHARD_I`) | 4-12 | a part runs out of time every night → split its areas |
| workflow `max-parallel` | 4 | ≤ 4 | parts hitting the same national hosts (NPS, USFS) stay few |

### 1.13 Time caps and resume

`--max-minutes N` stops cleanly with **exit 3** after saving (`core/workers.py SAVE_EVERY = 25` rows). `--resume` continues from
`work/` in the same `--out`. Workflow uses 50 minutes and caches `engine-out-N` between nights. Symptom: exit 3 every night →
more shards, not a longer cap.

### 1.14 Order and priority weights: `core/priority.py CLASSES`, `kpc_engine.ORDER`

US/CA rank 1 state trails · 2 state parks / rec areas · 3 historic sites · 4 everything else (and world rows) · 5 county / city ·
6 BLM · 7 national trails. `ORDER` runs outline first (its shapes feed the place ties). Changing ranks changes only the ORDER of
work, never what is found. Change only when the club's priority file changes.

### 1.15 The `--check-all` flag

`--check-all camping,trail` treats every park in scope as missing those kinds (audit / sample runs). Off by default.

---------------------------------------------------------------------------------------------------------------------------
### 1.16 Key doctor (v0.5.0): `config/rules.json` → `key_doctor`
| Setting | Default | Safe range | What it does |
|---|---|---|---|
| `reapply_nos` | true | on/off | Write `overrides.fixed.json` with the missing NOs (a copy; the checkout is never written) |
| `per_park_release` | **false** | on only after Brandon's OK | Write per-park release copies of a LIVE-FILTERED key |
| `require_chat2` / `require_path` | us-key, ca-key, world-key, fers-* | add kinds, never remove | YES approvals missing these fields are flagged |
| `fer_carry_km` | 1.0 | 0.5-2 | How far a 2-fer centre may move and keep its old id |
| `freeze_while_graded` | true | on | Stamp the build's sha while chat 11 grades it; flag a change mid-grade |
| `stuck_days` | 2 | 1-7 | Days at one stage before an area is on the stuck list |
| `size_guard` | true | on | Check file sizes |
| `size_warn_mib` / `size_red_mib` | 80 / 95 | warn 50-90, red <= 98 | GitHub refuses files over 100 MiB |
| `list_superseded_held` | true | on/off | List held copies that live already has (never deletes) |

Change one with `--set key_doctor.stuck_days=3`, `--enable key_doctor.per_park_release`.
The bot-side switches (env / repo variables) are listed in `patches/README.md`.

## 2. Worked tuning examples (one per grader)

**Outline.** chat 11: "US-1234 offered SURE but the pin is 180 m outside a riverside polygon; it is the right park."
1. Regrade with a wider R-G12 to see the effect without the web:
   `python3 kpc_engine.py grade --out OUT --kinds outline --set grader.rg12_m=200`
2. Read `OUT/grades-regrade.md`: the banner shows `grader.rg12_m: default 150, now 200`; compare `rg12_far` and the
   wrong-park count with the default regrade.
3. If nothing wrong comes in, change the default in `config/rules.json`, add the regression test (section 4), note it in CHANGELOG.

**Docs.** chat 11: "the state's 'All parks brochure' was offered for 3 parks." Lower the same-file bar:
`grade --kinds docs --set grader.docs_same_file_max=2`; check the "the same file is used by N parks" count in the regrade.

**Parking.** chat 11: "'Visitor Center Office' marked as parking." Add `visitor center office` to `BAD_LABEL`, add a test
`assert rule_g.point_problems([37.1,-86.1,'Visitor Center Office'], 'US-KY')`, regrade parking.

**Camping.** chat 11: "a 'Group Shelter' counted as a campground." Add `group shelter` to `OTHER_BUSINESS`; test
`assert not rule_g.camp_feature_ok('Group Shelter 3')`; regrade camping and read `campground_share`.

**Trail.** chat 11: "a trailhead point was offered as the trail line." Trails must be line records (line-vs-polygon check and
`LINE_KINDS`); add the layer to `registry/us_ca_trails.json` with the right `geom`, never turn the check off.

**KY hours.** chat 11: "'Lodge front desk 24 hours' taken as park hours." `HOURS_OTHER` already has lodge/front desk: find why
the line passed (usually split across two lines) and add a test with the exact line.

---------------------------------------------------------------------------------------------------------------------------
## 3. Rerun only the graders on saved output (no web)

```
python3 kpc_engine.py grade --out /path/to/engine-out --kinds parking            # one kind
python3 kpc_engine.py grade --out /path/to/engine-out                            # every kind found in the output
python3 kpc_engine.py grade --out OUT --kinds outline --set grader.rg12_m=200     # try a knob
```
It reads the saved rows, runs `postprocess()` (duplicate facilities, containers, trail bar + Overlapping boundaries, source-policy stamping) and writes
`grades-regrade.md` / `grades-regrade.json` (with the active config). No network requests are made. The original
`grades.md` is not touched.

---------------------------------------------------------------------------------------------------------------------------
## 4. Turning a chat 11 miss into a regression test

1. Copy the exact inputs from the miss (park name, ref, the record's name / attributes, pin, distance, layer URL, or the exact
   page line) — word for word, no paraphrase.
2. Add a test in `tests/test_round3.py` (or a new `tests/test_chat11_<date>.py`) that calls the smallest function that decides it:
   `rule_g.tier_g`, `names.tier`, `rule_g.point_problems`, `rule_g.camp_feature_ok`, `rule_g.hours_line_ok`, `rule_g.doc_problems`.
   ```python
   def test_chat11_2026_11_02_glen_nant_forestry():     # chat 11 miss, Nov 2: forestry record offered for an NNR
       park = {'n': 'Glen Nant National Nature Reserve'}
       assert rule_g.tier_g(park, {'name': 'Glen Nant'}, True, layer='FLS Forest Blocks')[0] == 'UNLIKELY'
   ```
3. Run it, watch it FAIL, fix the rule, watch it pass, run all tests (`python3 -m pytest -q`).
4. Regrade the saved output (section 3) and note the before/after in CHANGELOG.

---------------------------------------------------------------------------------------------------------------------------
## 5. Do-not-loosen list

* **Official sources only.** Never OSM / Overpass / Geofabrik, Google, AllTrails, Gaia, Strava, TripAdvisor, Yelp, Wikipedia /
  Wikidata, blogs, search snippets.
* **The WDPA guard + rule W-10 (round 4).** WDPA / Protected Planet / UNEP-WCMC is rejected whenever an official layer exists
  for the park. Only when the official ladder found nothing (Florida's conservation lands and PAD-US under other names
  checked first: WDPA's US data is a copy of PAD-US) and nothing was blocked may WDPA be used, as a LAST RESORT: always
  g='approx', labelled 'WDPA (last resort)', never SURE / STRONG / found, a question for chat 11. Do not widen this.
  Round-4 check: US-0896, US-6281, US-0658 and US-1879 all have official layers, so WDPA stays rejected for all four
  (see `registry/rulings.json`).
* **2-fers are never automatic.** At most suggestions in the waiting room.
* **KY-only scope** for hours / fees / closures unless the club changes it (a scope choice, see section 6).
* EU compilation (EEA CDDA / discomap) stays approximate until the national agency layer replaces it.
* POTA pins never move; the engine decides nothing; KPC-Links is read-only; write only inside `--out`.
* Politeness: 1 request / 2 s per host, honest User-Agent, robots / Cloudflare / captcha / sign-in never bypassed, no tokens
  from public maps, no TLS click-through (LOCKED: no switch exists).

---------------------------------------------------------------------------------------------------------------------------
## 6. Turning rules on and off

All switches are in **`config/rules.json`**. Every default is today's rule; with the file untouched the engine behaves
exactly as before (tested in `tests/test_rules.py::test_defaults_are_todays_rules_exactly`). Per run you can override
without editing the file:

```
--scope hours=US-KY,US-TN          # plug-in areas (repeat per plug-in); patterns: US-KY, US-*, CA-*, *
--disable closures                 # a plug-in off
--disable hours_rules.reject_fragments
--enable  hours_rules.reject_fragments
--disable source_policy.never_use.google      (or source_policy.never_use for the whole list)
--set grader.rg12_m=200
--rules my-rules.json              # another rules file (or env KPC_RULES)
```

Every run (and `grade`) prints the active rules first, writes **`active-config.json`** in `--out`, and puts a rules banner at
the top of **`grades.md`**, `grades-regrade.md` and **`board.md`**. Anything changed from the default is shown as a loud
WARNING list (`!!` lines in the log).

### Examples

* **Expand hours to Tennessee:** `kpc_engine.py run ... --areas US-KY,US-TN --scope hours=US-KY,US-TN`
  (or in rules.json: `"hours": {"enabled": true, "areas": ["US-KY", "US-TN"]}`). Fees and closures stay KY.
* **Turn off a plug-in:** `--disable closures` (or `"closures": {"enabled": false, ...}`).
* **Disable a parsing rule:** `--disable hours_rules.reject_fragments` (bare "10 AM - 4 PM" lines are then kept).

### Club scope choices vs safety rules

* **Scope choices (switchable, nothing stamped):** `plugins.*` enabled / areas, `hours_rules.*`, `checks.*`, `grader.*`.
* **Source-policy rules (switchable, but switching one OFF stamps every affected row):** `source_policy.*`. Rows that only exist
  because of a switched-off source rule get `source_policy: "non-official: <rule>"`, `grade` / `g` = `approx`, STRONG → WEAK and
  found → candidate, so they can **never pass as official**. The banner and `active-config.json` list them.
* **LOCKED safety rules (no switch at all):** honest User-Agent (never spoofed); never bypass Cloudflare / robots.txt / captchas /
  sign-in; never use tokens found inside public web maps; never click through TLS warnings. A rules file or flag that names any of
  them (user agent, tls / ssl / cert / verify, token, bypass, captcha, robots, cloudflare, sign-in, login, cookie, spoof) is refused
  with an error, as is any unknown switch name.

### Every switch

| switch | default | what it does | risk if changed |
|---|---|---|---|
| `plugins.outline` (enabled, areas) | on, `*` | outline plug-in and where it runs | off: no outline work |
| `plugins.docs` | on, `*` | official page + map (also `map`, `page` gaps) | off: no docs work |
| `plugins.parking` | on, `US-*`, `CA-*` | parking / access points | wider areas: no world sources verified yet |
| `plugins.camping` | on, `US-*`, `CA-*` | campgrounds | same |
| `plugins.trail` | on, `US-*`, `CA-*` | trail lines | same |
| `plugins.hours` | on, `US-KY` | KY hours | other states: rules tuned on KY pages only; check chat 11 grades |
| `plugins.fees` | on, `US-KY` | KY fees | same |
| `plugins.closures` | on, `US-KY` | KY closures / alerts | same |
| `hours_rules.separate_marina_scuba` | on | marina / scuba / lodge … lines are not park hours | off: Oct 31 failure comes back |
| `hours_rules.reject_fragments` | on | bare time fragments rejected | off: subjectless times offered |
| `hours_rules.hunting_hours_apart` | on | hunting-season lines are not park hours | off: "open seasonally" under hunting |
| `checks.resolve_duplicate_facilities` | on | one facility listed under 2+ parks stays only with the nearest park | off: parking bar "0 duplicate facilities" fails |
| `checks.containers` | on | records under 2+ parks are UNLIKELY / not found | off: districts offered as parks |
| `checks.line_vs_polygon` | on | line parks only match lines | off: trail ↔ polygon mismatches |
| `checks.forestry_kind_guard` | on | forestry layers only match forests | off: Glen Nant-type wrong kind |
| `checks.point_label_filter` | on | bad parking labels rejected | off: offices / road numbers as parking |
| `checks.camp_feature_filter` | on | non-campground features rejected | off: camping bar 95% fails |
| `source_policy.wdpa_guard` | on (blocked) | WDPA / Protected Planet never an ordinary source | off: WDPA treated like any layer, rows stamped `non-official: WDPA`, approx |
| `source_policy.wdpa_last_resort` | on (W-10) | with the guard on, WDPA may be asked only when no official layer had a record and nothing was blocked; rows g='approx', labelled 'WDPA (last resort)', never SURE / found | off: WDPA never used at all (round-3 rule) |
| `source_policy.never_use.openstreetmap` | on (blocked) | OSM / Overpass / Geofabrik rejected | off: stamped `non-official: openstreetmap` |
| `source_policy.never_use.google` | on (blocked) | Google links / My Maps rejected | off: stamped `non-official: google` |
| `source_policy.never_use.alltrails` | on (blocked) | AllTrails / Gaia / Strava rejected | off: stamped |
| `source_policy.never_use.wikidata` | on (blocked) | Wikidata rejected | off: stamped |
| `source_policy.never_use.wikipedia` | on (blocked) | Wikipedia / Wikimedia rejected | off: stamped |
| `source_policy.never_use.tourism_app_pages` | on (blocked) | TripAdvisor, Yelp, visit…/tourism, app stores rejected | off: stamped |
| `source_policy.eu_compilation_approximate` | on | EEA CDDA / discomap rows approximate | off: still approximate (rows stamped `non-official: EU compilation`); never official until the national layer |
| `source_policy.parcels_approximate` | on | parcel-traced outlines approximate | off: rows stamped, still approx |
| `source_policy.unofficial_docs_kept_apart` | on | docs only from official domains | off: other domains (not never-use) allowed, rows stamped `non-official: unofficial doc` |
| `source_policy.state_mapping_compilations` | on (club ruling, Nov 1) | a state mapping agency's compilation line (KyGovMaps / kygisserver / opengisdata.ky.gov, KY Div. of Geographic Information, TN STS / tnmap) counts as official when the managing agency publishes no line of its own; the agency's own line wins as soon as it turns up (the compilation is then not used); stream lines count only for river / water-trail parks | off: compilations never count (round-4 rule); those rows become candidates |
| `checks.game_reserve_not_park` | on (Nov 1) | game / hunting / private reserves, hunting blocks and concessions are not POTA parks: such a record is UNLIKELY for a park that is not itself a game reserve | off: game reserves next to national parks can be offered |
| `source_policy.two_fers_never_auto` | on | 2-fers never automatic | off: grader may auto-SUGGEST; everything still goes to the waiting room (2-fer finder is a stub) |
| `grader.size_pass_max` | 1.5 | size PASS band | > 2: wrong-size records look fine |
| `grader.size_off_max` | 5.0 | size WAY OFF limit | > 8: containers slip to LIKELY |
| `grader.parcel_low` / `parcel_high` | 0.2 / 2.0 | parcel hold band | wider: wrong parcels offered |
| `grader.rg12_m` | 150 | R-G12 distance | > 250: neighbours matched |
| `grader.docs_ky_tn_share` | 0.20 | docs bar | bars are chat 11's; change only on their word |
| `grader.docs_same_file_max` | 3 | same-file limit | higher: brochures offered as park maps |
| `grader.trail_pin_m` | 200 | trail bar: POTA pin within N m of the agency's own line | higher: trails of a neighbouring park pass |
| `grader.fer_line_ft` | 100 | 2-fer / 3-fer rule: a trail with no land boundary counts within N ft of its line (water trails: of the water's edge) | club rule: change only on the club's word |
| `grader.parking_right_of_30` | 27 | parking sample bar | same as bars |
| `grader.parking_ky_tn_share` | 0.10 | parking bar | same |
| `grader.camp_layer_ok` | 0.95 | camping bar | same |

## 7. Round 5 (Nov 1) additions

- **Trail-piece name test (club ruling).** A trail piece with its own name (e.g. Clifty Creek) passes the name test ONLY when
  something official ties it to the POTA trail: another field on the same record names the trail system (a trail system /
  route field such as 'Sheltowee Trace', captured as `system_names`), or the managing agency's own page lists the piece
  (`agency_page_lists` = that page's URL, set by a person). Never on location alone. Not a switch: a club rule.
- **W-10 vs the Mapping note.** `round5_note.txt` says "never WDPA (incl. HDX copies)". The user's newer W-10 (confirmed Nov 1)
  wins: WDPA is a last resort only, approx, labelled 'WDPA (last resort)'. HDX (data.humdata.org) protected-area / WDPA copies
  are now recognised as WDPA (`rules.WDPA`) and follow exactly the same rule. Flagged for chat 11.
- **Seeded work order** `config/work_order.json` (`"enabled": true`): rows in a seeded area are worked first inside each club
  class (lowest `w` first); a seed never jumps the club's class order (state trails first ... BLM last). Set `enabled` to false
  to go back to the plain class order. Each run writes `work-order.json` and `retry-list.json`.

