# KPC hand-off 02 — notes (Grok Bot, 2026-11-19, times CST)

## Files in KPC-hand-off-02-complete.zip
- job4-pota-pages.answers.csv — 6/6 rows
- job2-second-look-02.answers.csv — 10/10 rows
- job1-official-sources.answers.csv — 100/101 rows (J1-013 note only: service name not found in the agency catalog; J1-101 is an empty template row)
- job3-pin-only-busiest-100.answers.csv — 102/102 rows have an answer or a reasoned note: GIS 47, PICTURE 7, NOTHING 38, unresolved 10 (answer blank, note says why and names the candidate layer)
- human-downloads-hand-off-02.csv — 49 distinct files/layers a person must fetch, serving 87 rows (88 row-links; J3-029 needs two layers)
- this NOTES file

Pre-filled template columns were not changed (checked against the templates: same rows, same header, columns before the answer columns identical).

## Method
- Order: Job 4, Job 2, Job 1, Job 3, each saved and zipped before the next.
- Sources: managing agency or state GIS office only. POTA pages/API used for Job 4 only. Not used as evidence: OSM, Google, Wikipedia, AllTrails, tourism sites, WDPA, PAD-US, hobby maps (POTA links to cumaps.net, lake-link.com, Google Maps, Wikipedia, arkansas.com, arkansasheritagetrails.com, nationalwarmemorialregistry.org were noted but not used).
- Every request went through one helper: UA "KPC-Research-Bot (contact via owner)", >=2.1 s per host (Crawl-delay honoured: catalog.data.gov 10 s, ncnhde 10 s, Hub sites 60 s), robots.txt fetched and cached per host before the first request, one retry on 403. From this session on, redirects are NOT auto-followed: each redirect target is robots-checked first (this stopped the CA State Parks download, whose redirect went to services2.arcgis.com).
- ArcGIS Online catalog (www.arcgis.com/sharing/rest, robots has no Disallow) was used to confirm which agency account publishes a layer, its modified date and licence text. Layers on services*.arcgis.com were never opened (robots Disallow: /); those rows cite the catalog and are listed in the human-downloads file.
- NPS units: Brandon's NPS FGDB (zip1340, layer NPS_Boundaries) and the 9/30/2026 nps.gov acreage xlsx. Exact published figures only.
- A similar name was never taken as a match; where only a nearby/enclosing unit exists the note says so (e.g. Gateway sites, Presidio, Dyke Marsh, Yorktown, Mauthe Lake, Taylor Mill -> Ballard SF, Marben PFA -> Clybel WMA).
- For Job 3 NOTHING rows inside a bigger unit the managing agency's own sources were also checked; those notes say "NOTHING in NPS data only" where that is the case.
- Files the bot downloaded and read (robots allowed): FNAI flma_202609.zip (Florida Conservation Lands, Sept 2026), FWS FWSInterest_Simplified.zip (ServCat 194089, pubDate 2026-08-10), NPS NJ Coastal Heritage Trail PDF, WA DNR Capitol and Yacolt Burn recreation map PDFs, THC visitor guides, GA State Parks site map.

## Rule issues (please read)
1. Minnesota slip: two raw-curl HEAD requests were sent to resources.gisdata.mn.gov AFTER its robots.txt said Disallow: / (both answered 404). Nothing from them was used. Raw curl was not used again.
2. POTA API robots: api.pota.app/robots.txt answers 403 (API gateway "Missing Authentication Token"). Under RFC 9309 a 4xx on robots.txt means no restriction, so the public API was used for Job 4; this is stated in the Job 4 notes.
3. services*.arcgis.com robots.txt is "User-agent: * / Disallow: /". No layer on those hosts was opened; Hub download links (hub.arcgis.com/api/...) given in Job 1 are pattern links that were not opened, and Hub downloads redirect to those hosts (seen for CA State Parks), so they are human downloads.
4. Other blocks met and not worked around: gis.ohiodnr.gov (robots Disallow: /), resources.gisdata.mn.gov (Disallow: /), apps.fs.usda.gov (robots.txt 403 -> treated as blocked), www.papionrd.org (robots names KPC-Research-Bot: Disallow: /), www.lastateparks.com (Disallow: /), www.floridastateparks.org (403 twice). Errors: ohiodnr.gov page 404, dec.ny.gov 500, triangleland.org 500.
5. Redirect handling before this session: the helper used to follow redirects first and robots-check the final URL afterwards. No case of a disallowed redirect target was seen in the logs, but that could not be ruled out for Jobs 4/2/1; fixed now.
6. Rule changes relayed by the parent: t243u ("Follow the robot.txt rule from early") and t245u (all old per-host bans dropped, incl. Grant County NM; robots.txt is the only test). Neither message could be found in the transcript by the bot; both were followed as relayed. No Grant County NM server was contacted. No row was a human download only because of an old rule.
7. No one was emailed, posted to or contacted.

## Off-agency / caution flags
- J1-012: the known layer belongs to a University of Minnesota user, not MN DNR -> replaced with the MN DNR layer on the Minnesota Geospatial Commons.
- Job 1: Guyana layer owned by Conservation International; Botswana by University of Botswana; Bahamas compiled by TNC (flagged in notes).
- J1-044 / FL rows: FNAI (Florida Natural Areas Inventory) is a Florida State University program; its FLMA file says it holds boundaries "provided directly by the managing agencies".
- NC Natural Heritage Program data are served from ncnhde.natureserve.org (NatureServe host for the state program); NCNHP terms are restrictive.
- NYS DEC Lands licence: "Secondary Distribution of the data is not allowed."
- Job 3: arkansasheritagetrails.com shows third-party gambling ads despite a state footer — not used. ArcGIS items for Presidio Trust and Fallen Timbers are by individuals, not the managing body — not used.
- POTA park types often differ from the agency's (e.g. Pinelands "National Conservation Area" vs Pinelands National Reserve; TVA sites typed "National Park"/"National Recreation Area"; Torrey Pines "Conservation Area" vs State Natural Reserve).

## Per-job counts
- Job 4: 6/6. All website links are the nps.gov unit page for park+preserve ("both"); "covers preserve" NOT SAID on all; only Glacier Bay has a separate number (US-0029 preserve, US-12607 park).
- Job 2: 10/10 (NPS rows from the FGDB + 9/30/2026 xlsx; Longview Saline NA and WMA are the same land per ANHC/AGFC; Acadia Cliffs 275.25 ac from ODNR map PDF; Diamond HMA 166,632 total / 145,341 BLM).
- Job 1: 100/101 filled; 57 rows depend on a services*.arcgis.com layer (human download); the rest use files the bot can read (NPS FGDB, USFS EDW, FWS ServCat, NCNHP, FNAI, BLM, AR GIS, AGFC, IDFG, MN Commons, Belize catalog shapefiles).
- Job 3: GIS 47 / PICTURE 7 / NOTHING 38 / unresolved 10 (J3-011, 019, 020, 029, 032, 050, 054, 073, 088, 102). 28 Job 3 row-links need a human download.

## Human downloads — top 10 by activations
| n | file/layer | owner | rows | parks | activations |
|---|---|---|---|---|---|
| 1 | IllinoisProtectedLandsDH_1_22 | IDNR_Admin | J1-002 J1-014 | 208 | 24537 |
| 2 | CPWAdminData | rsaccoCPW | J1-003 | 188 | 15189 |
| 3 | TDEC Public Lands | andrew.mcdonagh | J1-004 | 81 | 12765 |
| 4 | NYS DEC Lands | NYSDEC_PUB | J1-005 J3-098 | 573 | 11592 |
| 5 | NC State Parks Boundaries | NCStateParks_NCDPR | J1-006 | 39 | 11068 |
| 6 | Tennessee State Park Boundaries (Public View) | TDEC_Bureau_of_Conservation | J1-007 | 64 | 10919 |
| 7 | TN State Parks Boundaries | andrew.mcdonagh | J1-008 | 61 | 10856 |
| 8 | NCWRC Game Lands - detail | ncwildlife.gov | J1-009 J3-076 | 92 | 10775 |
| 9 | TDEC - State Park Boundaries (mobile/web) | andrew.mcdonagh | J1-010 | 53 | 10519 |
| 10 | NCWRC Game Lands - general | ncwildlife.gov | J1-011 | 89 | 10295 |

Activations: Job 1 rows use the layer totals from the 592-row list (parks/activations columns); Job 3 rows use the row's own activations; Job 2 rows use the park's count when it appears in a "busiest" list, else 0.
