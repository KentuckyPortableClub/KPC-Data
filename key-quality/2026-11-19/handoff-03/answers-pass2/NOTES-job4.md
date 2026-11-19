# Job 4 notes — POTA's own park pages (hand-off 03B)

Date checked: 2026-11-19 (America/Chicago). Source files written:

- `/workspace/kpc-03B/job4-pota-own-pages.answers.csv`
- `/workspace/kpc-03B/NOTES-job4.md` (this file)

First four columns (`item`, `ref`, `our_name`, `area`) were copied unchanged from the template.

## Method

POTA park pages (`https://pota.app/#/park/US-XXXX`) are a JavaScript app. The public park page loads `https://api.pota.app/park/US-XXXX`. The in-app search box calls `https://api.pota.app/lookup?search=...&size=10`. Those public, unauthenticated endpoints were used (lookup size was 25 so a short-name search would not hide a second US hit). The park page JavaScript (`Park-BTfkcqFx.js`) was read only to see how the site displays the same API fields.

Fields were taken from each park's API record and reported as the site shows them:

- **Name** and **type** are separate fields. The park page heading and the search display both concatenate them as `{name} {parktypeDesc}` (e.g. "Katmai National Park"). The name field itself excludes the type (POTA's own editor hint: "Name of park excluding type"). The answers sheet therefore has name and type in their own columns, exactly as stored/shown in those fields.
- **Comments:** when `parkComments` is null, the page shows the fallback "No comments found for this park". Per the column heading this is recorded as `none`. When comments exist they are copied exactly, including internal double spaces and trailing spaces (US-0040 has one trailing space; US-0665 has two, and double spaces between sentences).
- **Latitude / longitude:** the page shows `{latitude}, {longitude} ({grid6})`. The answers column is lat/long only, so the value is `{latitude}, {longitude}` with the comma-space used on the page, and with the numbers exactly as returned (no added zeros). Maidenhead grid6 values, not placed in the CSV, were: US-0044 BO28cn; US-0953 CN82hc; US-0048 BP20xp; US-0665 DN33ec; US-0040 EL49wt; US-0696 EM98lb; US-0022 BP53nr; US-0069 BP81nm; US-0003 BO16ct; US-0026 BP48cd.
- **Website link:** the park page `href` (same as the API `website` field). The visible label on the page is that URL with the scheme and a trailing slash stripped.
- **Whether that link is for the park, the preserve, or both:** POTA itself does not label this. Each `website` URL was opened (after reading NPS `robots.txt`) and judged from the agency page's own title/heading.

Preserve / counterpart search: for each row, POTA lookup was run first with the exact name given in the brief (for Aniakchak, "Aniakchak National Monument"). If that returned nothing, a shorter distinctive name was also searched so a differently worded listing would not be missed. A broad lookup for "National Preserve" was also run (first 25 hits were non-US parks). No US listing was invented from memory.

## robots.txt and manners

- `https://pota.app/robots.txt` is not a robots file: the host is a single-page app and that path returns the same HTML shell as other routes (HTTP 200, `text/html`). No Disallow rules were found.
- `https://api.pota.app/robots.txt` is not a robots file: the API gateway returns HTTP 403 `{"message":"Missing Authentication Token"}`. No Disallow rules were found. Only public unauthenticated endpoints already used by the website were requested. Nobody was contacted.
- `https://www.nps.gov/robots.txt` (User-agent: *): Disallow `/ns/`, `/search/`, `/loader.cfm`, and `/*loader.cfm*`. The ten park index pages used here are allowed. A crawl-delay of 5 is stated only for bingbot. Requests to one host were spaced at least 2.5 seconds apart. User-Agent identified this as GrokBot research for a Kentucky Portable Club park-maps check.

Nothing was blocked.

## Website coverage (all ten: both)

Every POTA website URL is an NPS unit homepage whose title and H1 name both the park/monument (or historical park) and the preserve:

| ref    | POTA website                              | NPS title / H1 |
|--------|-------------------------------------------|----------------|
| US-0044 | https://www.nps.gov/katm/index.htm       | Katmai National Park & Preserve |
| US-0953 | https://www.nps.gov/orca/index.htm       | Oregon Caves National Monument & Preserve |
| US-0048 | https://www.nps.gov/lacl/index.htm       | Lake Clark National Park & Preserve |
| US-0665 | https://www.nps.gov/crmo/index.htm       | Craters Of The Moon National Monument & Preserve |
| US-0040 | https://www.nps.gov/jela/index.htm       | Jean Lafitte National Historical Park and Preserve (page also names Jean Lafitte's Barataria Preserve as a unit) |
| US-0696 | https://www.nps.gov/neri/index.htm       | New River Gorge National Park & Preserve |
| US-0022 | https://www.nps.gov/dena/index.htm       | Denali National Park & Preserve |
| US-0069 | https://www.nps.gov/wrst/index.htm       | Wrangell - St Elias National Park & Preserve |
| US-0003 | https://www.nps.gov/ania/index.htm       | Aniakchak National Monument & Preserve (same URL is also the website on US-0902) |
| US-0026 | https://www.nps.gov/gaar/index.htm       | Gates Of The Arctic National Park & Preserve |

So `website_link_is_for` is `both` on every row. That is a fact about the linked NPS page, not something POTA states on its own park page.

## Does the preserve (or, for Aniakchak, the monument) have its own POTA number?

Exact-name lookup was empty for all nine "… National Preserve" / "Jean Lafitte's Barataria Preserve" queries. Short-name lookups found only the already-listed park/monument (plus, where noted, an unrelated park), not a second US preserve number.

The exception is Aniakchak. US-0003 is itself listed as type National Preserve. The instructed counterpart search, "Aniakchak National Monument", returns **US-0902 Aniakchak National Monument** (API: name Aniakchak, type National Monument, comments none, same NPS website). Lookup "Aniakchak" also returns US-0878 Aniakchak National Wild and Scenic River, which is a river listing, not the monument or the preserve. The answers column for B4-09 therefore records `US-0902 Aniakchak National Monument`.

## Does the ref's POTA page say the number covers the preserve?

- B4-01–B4-08 and B4-10: **NOT SAID**. Displayed titles are "… National Park", "… National Monument", or "Jean Lafitte National Historical Park". None of the comments name the preserve. US-0040's comments say only that there are "several locations within the Jean Lafitte NHP". US-0665's comments describe monument access only.
- B4-09 US-0003: **YES**. POTA's own type is National Preserve and the displayed title is "Aniakchak National Preserve". The page does not also say that this number covers the monument (the monument is a separate listing, US-0902).

POTA pages were not treated as saying they cover the preserve merely because the linked NPS site is a combined park-and-preserve homepage.

## Uncertainties / judgment calls

- Name vs displayed title: recorded as the separate name and type fields, not the concatenated heading. If a later check wants the heading string, it is `{name} {type}`.
- Comments `none` vs the UI fallback sentence "No comments found for this park": the column heading says "or none"; `none` was used.
- Lat/long column omits the `(grid6)` the page appends; grids are listed above.
- B4-09 column `preserve_has_its_own_pota_number` is slightly awkward because this ref already is the preserve. Per the brief, the searched counterpart (the monument) was recorded there. The note on that row also states that US-0003 itself is the preserve listing.
- Website "both" required opening the NPS page; POTA does not classify the link.

## What was not used

PAD-US, OSM, Wikipedia, and other unofficial sources were not used. No agency or person was contacted. No authenticated POTA endpoints were called.
