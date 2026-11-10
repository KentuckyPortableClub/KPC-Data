# Research tips for the club's agents

These are practical tricks for finding **official** park boundaries and park pages. They were learned while building and
live-checking the KPC Park Engine (Oct 31 – Nov 1, 2026).

Each tip carries a label:
- **[checked]**: we did it and it worked on a live server this week.
- **[untested]**: a sound idea we have not yet run ourselves.

Rules first (they override every tip): see the rules sheet in [README.md](README.md#11-the-rules-sheet).
- Official sources only. Never OSM, Google, Wikipedia / Wikidata, AllTrails or blogs. WDPA / Protected Planet only under rule W-10:
  a last resort when no official layer exists (check Florida's conservation lands and PAD-US under other names first), approx,
  labelled 'WDPA (last resort)'.
- No tokens, no sign-ins, no faked User-Agent, no clicking through certificate warnings, no getting around robot checks.
- Blocked is not the same as "not found".

---

## 1. Before you search: read what the club already has  [checked]
The club's source pack is the starting point.
- `approved/approved-layers-*.json`: about 2,900 YES rows covering 190 distinct layers.
- `approved/rejected-layer-rows-chat11-NO.json`: 506 NO rows.
- `tips/agency-atlas/<area>.md`: server roots per area.

`registry/_seed_pack.py` turns all of this into `registry/pack_sources.json`, and the engine reads that file **first**:
- A park with a YES row is skipped ("already approved").
- A park + layer + record that chat 11 answered NO is never offered again.
- Spend new search time only on the areas the pack does not cover. `python registry/_seed_pack.py` prints the count per area.

**Watch out:** the pack had one approved US-FL layer that is a **WDPA copy** (`.../WDPA_v0/FeatureServer/1`, YES rows
US-0658 and US-1879). Approved lists can still hold forbidden copies, so the seeder now drops them. See section 6.

## 2. Is this layer alive? Two cheap checks  [checked]

**ArcGIS: count the records.** Ask for a count before downloading anything:

```
<layer>/query?where=1%3D1&returnCountOnly=true&f=json      ->  {"count": 437}
```

- `{"error":{"code":499,"message":"Token Required"}}` (or 498) means the layer **needs sign-in**. Stop there and write it down.
- `{"error":{"code":400,"message":"Invalid URL"}}` / `Service not found` means a dead address. Re-list the server (section 4).

**WFS / OGC: look at the service description.** Use `?service=WFS&request=GetCapabilities` (or `/collections?f=json` for OGC API)
to get the layer names and coordinate systems. Then use `DescribeFeatureType&typeNames=<layer>` to find the name field.
- An HTML error page or a `403` on GetCapabilities means **blocked**. It does not mean "no layer".

## 3. Query at the pin first, then by name  [checked]
POTA names rarely match an agency's spelling. A spatial query at the POTA pin is far more reliable, so do it first:

```
<layer>/query?geometry=<lon>,<lat>&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects
        &distance=150&units=esriSRUnit_Meter&outFields=*&returnGeometry=true&outSR=4326&f=json
```

- **Buffer sizes:** 150 m for polygons, 200 m for lines and points. When the polygon's edge is within 150 m of the pin, the
  match is a candidate only (R-G12). The pin is never moved.
- Search **by name** only if nothing at the pin matches. Use the park's core words, with "State Park", "Nationalpark",
  "Naturschutzgebiet" and similar words removed: `UPPER(name) LIKE '%TRIVALEA%'`.
- **The name is not always in a `NAME` field.** Some examples:
  - `PUBLIC_NAM` (KY state parks);
  - `UNIT_NAME` (NPS);
  - `ORGNAME` (FWS);
  - `NAMN` (Sweden);
  - `PLUZ_NAME` (Alberta).
  When a layer's hit has no obvious name, check every text field for the best match to the park name. The engine does this
  and logs the field it found in `findings.jsonl`.
- **Some layers have no name field at all.** Denmark's MST *fredninger* layer is one. Such a layer can confirm *where* a
  park is, but it cannot give a T-1 or T-2 match.

## 4. A dead URL is usually a renamed service: re-list the server  [checked]
Read the server's own directory and walk one folder level:

```
https://<host>/arcgis/rest/services?f=json             -> {"folders": [...], "services": [...]}
https://<host>/arcgis/rest/services/<Folder>?f=json
```

Use the server roots that the agency atlas already lists for that host. The standard roots are `/arcgis/rest/services` and
`/server/rest/services`.

`registry/relist_failed.py` does this for the 45 failed hosts in the pack and writes **leads** (not approvals) to
`registry/relisted.json`. On Nov 1:
- `gis.blm.gov` re-listed fine (8 + 11 folders) and gave new park-like services.
- `geohub.gov.si` gave **404 on both standard roots**. Its services moved somewhere we have not found; ask ARSO / GURS.
- AGOL hosts (`servicesN.arcgis.com`, `services-eu1.arcgis.com` and the like) are **never read by a bot** (Nov 10 host
  rules, robots.txt included). Their layers come from saved copies; a person downloads them (the needs-download list).

## 5. ArcGIS Online search: keep only government owners  [checked, with care]
Use `https://www.arcgis.com/sharing/rest/search?q=<words> type:"Feature Service"&f=json`. Keep a result only when its
**owner org** is a government body.

Discovery also brings back a lot of junk that still "answers" at a park pin. All of these were seen this week:
- staff directories (Tennessee "Staff Directory" matched Cedars of Lebanon State Forest to *Cedars of Lebanon Forestry Office*);
- species ranges (Kentucky SWAP / SGCN);
- county boundaries ("Scott State Forest" → *Scott County*);
- bike inventories (Illinois BIS);
- shooting ranges;
- NHD streams.

The engine filters these by service name (`core/registry.py` JUNK). Also check the **geometry type** (an outline needs
polygons) and that **a record name, not just a place, matches**.

## 6. Spotting a WDPA (or OSM) copy re-hosted by someone official  [checked once]
Government ArcGIS orgs sometimes re-host WDPA. Clues:
- service names like `WDPA_v0`, `WDPA_*`, `Protected_Planet`;
- fields `WDPAID`, `WDPA_PID`, `DESIG_ENG`, `IUCN_CAT`, `REP_AREA`, `GIS_AREA`, `ISO3`, `PARENT_ISO`;
- a licence or description that mentions UNEP-WCMC or protectedplanet.net.

Any of these makes it a copy, and copies are **not allowed**, whoever hosts them. The same goes for fields such as
`osm_id` / `@id` / `way/123`, which mark an OSM copy.

We caught the US-FL case by its service name. The field / licence check is **[untested]** as an automatic rule; do it by eye.

## 7. Europe: the national layer beats the EU compilation  [checked]
The EEA Natura 2000 / CDDA layers (bio.discomap.eea.europa.eu) cover EU and EEA countries only.
- They are graded **approximate** and never give a full YES, **even when a chat 11 YES row approved one** (the pack holds
  approved CDDA layers for DE, ES, BE, IT and SI; the engine forces them back to approximate).
- They are also mostly points for some layers: the pack lists 55 "points" failures on that host.
- **Replace them with the national WFS** as soon as you can.

Ones that worked:
- **Sweden.** Naturvårdsverket `https://geodata.naturvardsverket.se/naturvardsregistret/wfs`, layer
  `Naturvardsregistret_WFS:SkyddadeOmraden`, name field `NAMN`, **8 of 10** test parks verified. The `/arcgis` path on the
  same host answers **403**; the `/wfs` path answers.
- **Germany:** BfN `geodienste.bfn.de` WFS capabilities list one layer per designation.
- **Wales / Scotland:** GeoServer WFS (DataMapWales `inspire-nrw:*`, NatureScot) in **EPSG:27700**.
- **Flanders:** an OGC API (Mercator).

## 8. WFS axis order (the silent killer)  [checked]
WFS 2.0 with a `urn:ogc:def:crs:EPSG::<code>` bbox uses the axis order of that EPSG code.
- For **3006 (Sweden), 3844 (Romania)** and EPSG:4326 itself, **north comes first**.
- Send east-first by mistake and you get zero hits with no error.
- Read the order from pyproj (`CRS.from_epsg(code).axis_info[0].direction`) instead of hard-coding it. This is what `core/gis.py`
  does.

## 9. Old ArcGIS servers  [checked]
- **`Pagination is not supported`:** drop `resultOffset` / `resultRecordCount` and retry.
- **`Invalid query parameters` on a valid layer:** usually a group layer, a raster or a wrong layer number. Open
  `<service>?f=json` and pick a layer whose `geometryType` is `esriGeometryPolygon`.
- **Very large answers (3 MB+ JSON cut off):** ask for fewer fields, `returnGeometry=false` for name checks, and use
  `maxAllowableOffset` / a smaller `resultRecordCount`. The pack shows this on gis.blm.gov and arcgis.mma.gob.cl.

## 10. Catalogue (CKAN) search  [checked for US / Canada; untested in local languages]
`https://catalog.data.gov/api/3/action/package_search?q=<park words> res_format:"Esri REST"` and
`https://open.canada.ca/data/api/3/action/package_search?q=...` both work and return resource URLs you can query.

**[untested]:** European national portals that run CKAN (for example data.gov.ie, data.gov.ro, data.gov.si). Search them in
the **local language**, using the words in `world/world_agencies.json`, e.g. `q=rezervație naturală`,
`q=Naturschutzgebiet`, `q=parc naturel régional`. The English words find very little.

## 11. INSPIRE "Protected sites" (PS) discovery  [untested by us]
Every EU country must publish protected sites under the INSPIRE theme **PS**. The national INSPIRE geoportal or the EU
INSPIRE Geoportal lists the country's PS download / view services. Look for a WFS whose layer is `PS.ProtectedSite`, and
then:
- run GetCapabilities (section 2);
- find the name field (often `siteName` / `text` nested inside `GeographicalName`);
- test at a pin.

Spain's MITECO INSPIRE endpoint answered **403 from our box** and went to "host resting" after 3 strikes. Retry it from
GitHub Actions, never by disguising the client.

## 12. Finding the official park page  [checked]
- **Start with the POTA website link.** Keep it only when it is on an official domain, it opens, and the page names the park.
  A dead link or a link to the wrong park goes into `fixes.csv`.
- **Next, the agency's sitemap.** Read the `Sitemap:` lines in robots.txt (or `/sitemap.xml`), then match the slug against the
  park's core words. This beats any search engine and needs no Google.
- **NPS pages:** hours and fees come cleanly from `https://www.nps.gov/<code>/structured_data_<code>.json`. Copy text word
  for word.
- **POTA links to the EU viewer.** Some RO / EU parks link `natura2000.eea.europa.eu`. That viewer is official but it is a
  viewer, not the park manager's page. Note it.

## 13. Being refused: what to write  [checked]

| what happens | what you write | then |
|---|---|---|
| robots.txt disallows it | `blocked (robots)` | stop |
| 403, a Cloudflare page, a captcha | `blocked (HTTP 403 ...)` / `blocked (robot challenge)` | stop; retry from GitHub another day; never change the User-Agent |
| TLS / certificate error | `blocked (TLS failure)` | stop; never click through |
| `Token Required` (499 / 498) | `token-only (needs sign-in)` | never use, even if a public web map carries a token |
| 429 / 5xx three times | `blocked (host resting: 3 strikes)` | the host rests for a day |
| page says "temporarily unavailable" (Slovenia ARSO, Nov 1) | `blocked (...)` with the date | retry from GitHub |

Never mark a blocked park "not found". `blocked.csv` keeps every refusal so it can be retried.
This also applies when **only some** sources were refused: if one official source went unread and the others had nothing, the
park is still `blocked`, not `not found`. (We found the engine getting this wrong on Nov 1 and fixed it in all plug-ins.)

## 13b. US / Canada: work the busiest kinds first  [checked: from the club's numbers, Nov 1]
The club ranked the 3,617 US and Canada parks still missing an outline by share of activations: trails 45% (national historic
trails 21%, state trails 13%, national scenic trails 11%), state parks 5%, state recreation areas 4%, national historic
sites 4%, county / city / regional parks about 4%, state historic sites 3%, BLM 2%, state forests 2%.
- **State trails first.** Look for a state **trail line** layer (often "State Trails", "Rail Trails", "Trail centerlines"
  from the state parks or transportation office). A trail outline is a line, so test it at the pin with a 200 m buffer,
  not "pin inside".
- National scenic and historic trails are covered by the club's trail-line tool; do not spend time on them here.
- **Historic sites are small.** The pin often sits on the building, and many boundary layers have no name. Use the Hard Look
  tricks:
  - the parcel under the pin, with its record (parcel) number and owner [checked for NE / RI / TX / WV statewide layers;
    untested in other states];
  - the Canadian federal property layer (DFRP_PUBLIC, `name_en`, `custodian_en`) for Parks Canada national historic
    sites [checked in the Hard Look];
  - a parcel is a **lead**, never the outline: it is always WEAK.
- BLM and county / city parks are a long tail: leave them for last.

## 14. Per-country notes we actually hit

| area | note | status |
|---|---|---|
| US-KY | `kygisserver.ky.gov` state parks layer 8, name field `PUBLIC_NAM`; 4/8 test parks verified | checked |
| US (NPS) | NPS Land Resources boundary layer: `UNIT_NAME`; Mammoth Cave pin → *Mammoth Cave National Park* (T-1) | checked |
| US-TN | AGOL discovery picked up a staff-directory layer as "state forest"; it is filtered now | checked |
| US-VA | Potomac Heritage NST layers: several answer `400 Invalid query parameters` (group or bad layers) | checked |
| GB | Natural England SSSI layer → `token-only (needs sign-in)` | checked |
| GB (Wales) | DataMapWales WFS (EPSG:27700): National Parks 2/6, NNR 3/6, SSSI 1/6 verified on Nov 1 (Cors Caron NNR → CORS CARON); an earlier run had no GB park list to test with | checked |
| SE | `/wfs` works, `/arcgis` is 403; EPSG:3006 is north first | checked |
| DK | MST fredninger has no name field, so the EU approximation wins; the official MST Natura 2000 layer is still needed | open |
| RO | Natura 2000 names carry site codes and Romanian designation words ("ROSCI0123", "Situl", "Rezervația Naturală"); the matcher now drops them and strips accents (ă→a) | checked offline |
| ES | MITECO INSPIRE: 403, then host resting | blocked |
| PL | GDOŚ: HTTP 403 | blocked |
| IT | MASE EUAP WFS: host resting after timeouts | blocked |
| SI | `geohub.gov.si`: Service not found on 936 pairs; both standard roots 404 on Nov 1 | blocked / moved |
| JP | MOE biodiversity centre: HTTP 500 from our box | blocked |
| MX | SEMARNAT / CONANP is the only national source in the registry; `sig.conanp.gob.mx` is a portal lead | partly |
| BB, CU, LC | no official layer found yet (Caribbean). Try each government's GIS unit or national physical-planning office; there is no fallback to WDPA | open |
| CA | CPCAD and Parks Canada work; Alberta / BC / Ontario / NS layers are in the approved pack | checked |

## 14. Chat 11's 18 misses, as habits (checked: each one is a passing test in tests/test_misses.py)

- **Strip the kind words, then compare. Never let a WMA answer for a state park.**
  - Yatesville Lake SP vs WMA.
  - Monument BLM RMA vs the 1-acre "Monument GS".
- **One record under several pins is a container.**
  - A "Wetland Management District" is a container too (Oxford Slough).
  - Containers are evidence, never a question.
- **Size tells.**
  - More than 1.5x is OFF and more than 5x is WAY OFF (Hiwassee 9.8x, Green Gables = all of PEI NP).
  - A parcel outside 0.2-2x is held (Salato 921 vs 229.85 ac).
  - 789 vs 796 ac is fine (Cedar Creek).
- **Never absorb another POTA park's land into a parcel answer** (Halfmoon Pond inside Bomoseen SP).
- **Same land twice** (the Big South Fork copy): merge it, don't count it twice.
- **Pins sit on the road.**
  - Within 150 m with a name match is fine (R-G12, Ontario conservation areas).
  - A pin 111 km off is a typing slip to report (Fort Providence, latitude 62 for 61). Never move it (R-G13).
- **Names change.**
  - Prairie Coulees = Hargrave Coulees.
  - Colony Farm = ƛ̓éxətəm.
  - Mount Douglas = PKOLS.
  - Same person, different place: Denys Fort vs Nicholas Denys Site (check the distance).
- **Read the layer's field list before a name search.** Alberta's field is `NAME`, not `PARK_NAME`. An empty answer from a
  wrong field is not "no record".
- **Never match BLM_Natl_SMA.** It names the land manager, not the park.
- **A layer label can be wrong.** Lighthouse Park was filed as "Trails Park". A name that doesn't match is UNLIKELY even
  when the pin is inside.
- *Untested on a live run:* the effect of these rules on a full key file. Chat 11's 30-join sample is the real check.

## 15. State trail lines (checked Nov 1)

- **Discovery is noisy.** An AGOL search for "state trail" across 63 states and provinces returned 333 line layers.
  - 209 of them were one regional planning commission's bike-plan inventory.
  - 55 were DOT right-of-way drawings.
  - After curating by hand, 24 were kept (`registry/us_ca_trails.json`). Planning, proposed, road, right-of-way and
    public-comment layers were dropped.
- **Give every state entry `pota_locs: ["US-XX"]`.** Without it, verify samples parks from the whole country and every layer
  scores 0. Checked: 0/24 before the fix, 6 verified after it.
- **Many "trail" layers carry the park name, not the trail name** (Texas State Parks Trails, the NJ park trail system).
  - They verify against state parks, but Rule G keeps a state park matched to a line UNLIKELY. That is correct: a trail
    line is not a park outline.
  - The layers that really help state-trail parks so far are KY Recreational Trails (Pine Mountain State Scenic Trail) and
    WA State Parks Trails (Spokane River Centennial State Park Trail).
- *Untested:* the 18 layers that only "answer". They stay usable and Rule G gates them, but no sampled pin matched yet.

## Round 3 (Nov 1)
- **Scotland NNRs:** use NatureScot's own layer, `services1.arcgis.com/LM9GyVFsughzHdbO/.../National_Nature_Reserves/FeatureServer/0`
  (found through the spatialdata.gov.scot metadata record), not Forestry and Land Scotland forest blocks, which are the wrong kind.
- **WDPA copies hide inside agency ArcGIS orgs** (e.g. a `WDPA_v0` service). The guard reads the layer's own `?f=json`
  (description, copyright, licence, fields); still check the name before adding anything. Pack refs US-0896 and US-6281 also hit one.
- **Before tuning, read TUNING.md** and regrade with `kpc_engine.py grade` on saved output instead of rerunning the web.

## Round 5 (Nov 1): the master workbook and the retry list  [checked]

- The master workbook `KPC_All_GIS_Sources_plus_mapping-nov1.xlsx` is READ ONLY for the engine. Copy it to a scratch path and
  run `python3 registry/import_master.py <copy>.xlsx`: it opens the copy read-only, checks its sha256 before and after, and
  writes only `registry/master_nov1.json`. Never save the workbook, never run `world_keys/merge.py` or the trails round-1
  merge, and never add finds to its "Outside agent help" tab (the Mapping note asks; the user said no).
- Workbook rows we already had are not copied: the workbook's status / notes are kept on our entry (`wb`). New rows come in
  as `WB-<sheet>-<row>` with status `imported` (ranked after ours; `verify.py` should check them). WDPA / HDX rows go to
  last resort only; never-use / sign-in / token rows are refused and listed in `master_nov1.json` `refused`.
  56 were refused on Nov 1; most look like false positives for a person (MITECO files on storage.googleapis.com; Vermont
  ANR layers named "TOURISM").
- "Outside agent help" rows are LEADS, not answers: `park_leads` with the check note ("name only" = needs a person or a
  location check before use).
- `python3 registry/import_retry.py <retry csv>` builds `registry/retry.json` (tag 'retry from GitHub network'). A 403 is
  retried ONCE with the same honest request; a second 403 goes to a person. Never get past a 403 or a robot check. Spain's
  enp.zip is a person-downloads item.
- Trail pieces with their own name: look for a trail system / route field on the same record, or the managing agency's page
  that lists the piece. Being on the trail is not enough.

