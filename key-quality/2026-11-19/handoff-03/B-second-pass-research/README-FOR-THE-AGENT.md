# Outside research, hand-off 03B: an independent check (Kentucky Portable Club, 19 Nov 2026)

We build park boundary maps for a ham radio club. Three answer sheets below (`*.answers-template.csv`). Fill them in and save
each as `<same name>.answers.csv` (drop "-template"). The first columns come from our data: do not change them.

**This is a CHECK. Be hard to convince.** Claims that "an official map layer exists for this park" are often wrong in one of
three ways: (1) the layer holds a bigger area that only CONTAINS the park, (2) it holds a different place with a similar name,
(3) it is a copy published by someone other than the agency that manages the land. Answer YES / GIS only when you opened the
agency's own layer or its catalog entry and found THIS park in it by name, and write the record's name and acres exactly as the
layer shows them. If you cannot show that, the honest answer is NOTHING, PICTURE or an empty cell with the reason in `note`.
A similar name is not evidence. Some rows are tests with known answers.

**Where to look, in this order:** (1) the state's or agency's open-data portal (ArcGIS Hub, Socrata, CKAN); (2) the managing
agency's own park page, its "Maps" or "GIS data" section; (3) only then a general web search. Official = published by the agency
that manages the land, or the state GIS office for it. NOT official: PAD-US, OpenStreetMap, Google, Wikipedia, protectedplanet /
WDPA, tourism and hobby sites.

**Manners:** read each site's robots.txt first and obey it, redirects included; at least 2 seconds between requests to one site;
contact nobody. If robots.txt forbids a host (services*.arcgis.com does), do not open the layer: cite its catalog entry
(www.arcgis.com item page: owner account, date, licence) and write YES in `needs_a_human_download`.

## Job 2: official acres and where the outline lives (`job2-official-acres-and-outline`, 10 parks)
For each park: its official page; its official acres exactly as the agency publishes them, the WHOLE unit and, where the agency
gives it, the government-owned part (some park units are mostly land the agency does not own); the page or table and its date;
where the official outline lives and that record's name and acres. `same_land_as`: only when an OFFICIAL page says two park
numbers are the same land; give that page.

## Job 3: is there an official GIS boundary layer for this park? (`job3-busy-parks-is-there-official-gis`, 58 parks)
GIS = the agency's own boundary layer holds this park (give the layer address, the record's name and acres as shown, who
publishes it). PICTURE = only a picture map (PDF, brochure) that shows the boundary. NOTHING = neither.

## Job 4: POTA's own park pages (`job4-pota-own-pages`, 10 park numbers)
Open POTA's own page for each number (pota.app). Report, exactly as POTA shows them: the name, the type, the comments text, the
latitude and longitude, the website link, and whether that link is for the park, the preserve or both. Search pota.app for the
preserve's name: does the preserve have its own number? Does POTA's page say the number covers the preserve? POTA's pages are
fine as a source for THIS job only.

Do the rows in the order given and stop when your time is up: a partial sheet is fine. Return the three answers.csv files and a
short NOTES file (method, anything you were blocked from, anything you are unsure of).
