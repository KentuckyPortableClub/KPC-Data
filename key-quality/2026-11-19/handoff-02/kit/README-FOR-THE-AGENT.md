# Outside research, hand-off 02: official map sources (Kentucky Portable Club, 19 Nov 2026)

We build park boundary maps for a ham radio club. Each park needs its OFFICIAL boundary: the managing agency's own GIS layer or
boundary file. Four jobs below, one answer sheet each (`*.answers-template.csv`). Fill them in and save each as
`<same name>.answers.csv` (drop "-template"). The first columns are filled in from our data: do not change them.

**Where to look, in this order (our research rule):** (1) the state's or agency's OPEN-DATA PORTAL (ArcGIS Hub, Socrata, CKAN:
search the park or agency name); (2) the managing agency's own park page, its "Maps" or "GIS data" section (often loaded by
script: use a real browser); (3) only then a general web search. Official = published by the agency that manages the land (or the
state GIS office for it). PAD-US, OpenStreetMap, Google, Wikipedia, protectedplanet / WDPA and map-hobby sites are NOT official.

**Rules for every answer:** a similar name is not evidence; write only what the source shows; give the page or layer address you
opened and its date; when you cannot find it, leave the cell empty and say why in `note`. Some rows are tests with known answers.
Do the rows in the order given (busiest parks first) and stop when your time is up: a partial sheet is fine.

## Job 1: the official source for each layer or park we cannot get (`job1-official-sources`)
Each row is a layer our bots may not read (a blocked site, a download-only file) or a park whose real boundary is in no layer we
hold. Find the official source. `official_layer_address_or_file_link`: the ArcGIS REST layer address (ends in `/MapServer/<n>` or
`/FeatureServer/<n>`) or the direct download link (zip / shapefile / GeoJSON / KML). `licence_line`: the use terms as the source
states them (for example "public domain", "CC BY 4.0", "credit: <agency>"), or "none stated".

## Job 2: second look 02 (`job2-second-look-02`)
Ten parks. For each: the park's official page, its official acres (the agency's own figure, exactly as published, with the page
and date), and where its official outline lives (layer address or file). `same_land_as`: only when an official page says two
POTA park numbers are the same land; give that page.

## Job 3: the 100 busiest parks with no outline yet (`job3-pin-only-busiest-100`)
For each park: is there an official GIS boundary layer (GIS), only a picture map such as a PDF brochure with the boundary drawn
(PICTURE), or nothing (NOTHING)? Give the layer address or the map link. A picture map counts only when it shows the boundary.

## Job 4: POTA's own pages (`job4-pota-pages`)
Six park numbers. Open POTA's own page for each (pota.app, the park's page), and report its name exactly, its website link and
whether that link is for the park, the preserve or both, whether the preserve has its own POTA number (search pota.app for the
preserve's name), and whether the page says the number covers the preserve. POTA's pages are fine for THIS job only.

Return: the four answers.csv files only.
