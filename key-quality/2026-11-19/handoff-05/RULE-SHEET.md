# RULE SHEET R-PR: what the park page reader may say (Fable, 19 Nov 2026, draft for the build)

The reader is a reviewer's tool. Nothing it writes is shown to members or guests and nothing it writes decides a park.
The rules below are about one thing only: when the reader may store a fact, and when it must stay silent.

Format of every rule: what counts, what does not, what happens when unsure. The examples are real (19 Nov).

## R-PR1. The park's own page
- **Counts:** POTA's link (first address on an official host), else the stored `web` page, else the docs page.
- **Official host** = the agency's own host, or a host of the same government (use the docs bot's own judgment:
  `CODE-MAP.md`). A support group, a tourism article, a wiki, a reservation seller = `unofficial-host`: name and
  kind words may be stored marked unofficial; sizes, locations and "inside of" are NOT stored from it.
- **Not the park's page:** an address with no path (an agency's front page), a list of parks, a search result, a page
  that 3 or more parks of the area share unless it is an agency family page that names them all (NPS park + preserve +
  river). From an agency front page nothing is read: `AGENCY_HOME_ONLY`.
- **Unsure:** `own_page: "unknown"`, facts stored, question `SHARED_PAGE` or `NAME_DIFFERS` as fits.
- Examples: US-11524 links `www.idfg.idaho.gov` (front page: nothing read). US-8295 links a colorado.com article
  (unofficial). US-0902, US-0003 and US-0878 all link `nps.gov/ania` (shared, family page, read once for all three).

## R-PR2. The name on the page
- **Counts:** the first main heading; else the title with the site's tail cut off ("(U.S. National Park Service)",
  "| Bureau of Land Management", "| Utah", "- Arkansas State Parks"); else `og:title`; else a JSON-LD `name`.
- **Does not count:** a menu entry, a breadcrumb, an image caption, a headline of a news item on the page.
- **Compare with POTA's name** on the truth checker's `core()` (kind words removed): `same` (equal as written, case
  and punctuation aside), `same-core` (equal after kind words are removed), `differs`.
- **Unsure** (heading and title disagree on the core): store both, `best: null`, question `NAME_DIFFERS`.

## R-PR3. Kind words, and a combined unit
- **Kind words** come from a closed list in the code (National Park, National Preserve, National Monument, National
  Historical Park, National Recreation Area, National Conservation Area, National Forest, National Wildlife Refuge,
  Wilderness, Wilderness Study Area, Recreation Area, Special Recreation Management Area, State Park, State Forest,
  State Wildlife Area, Wildlife Management Area, State Trail, State Fishing Lake, ... build it from the `type` values
  in `data/parkinfo` so no kind POTA uses is missing).
- **Combined counts** only when the page's OWN NAME (R-PR2) joins two kinds with "&", "and" or "/":
  "Denali National Park & Preserve" = parts [National Park, National Preserve].
- **Does not count:** two kinds in the body text; a sentence about a neighbour; a "Parks & Recreation" department name;
  "Fish and Wildlife"; "Wild and Scenic River" (one kind); "Lake and Dam" (not kinds).
- **`pota_numbers_part`:** look in the stored park list of the same area for a park whose core name is the same and
  whose type is the OTHER part. Found = its number (question `COMBINED_BOTH_NUMBERED`, information only). Not found =
  `null` (question `COMBINED_UNIT`). The reader reports this; the key's rule R-PP1b decides what is drawn.
- Examples: US-0022, US-0026, US-0044, US-0048, US-0069, US-0665 = combined, no separate number. US-12607 Glacier Bay
  National Park = combined, the preserve is US-0029. US-0033 Great Sand Dunes = combined, the preserve is US-8295.

## R-PR4. Inside another named unit / holds another named unit
- **Counts:** a sentence about THIS place with one of: "within the X", "inside the X", "part of the X", "located in
  the X", "a unit of the X", "managed as part of the X", "surrounded by the X", where X is a proper name that ends in
  a kind word of R-PR3 (or matches the truth checker's `NAMED_UNIT`).
- **Does not count:** plain geography (a state, a county, a city, a desert, a mountain range, a river basin, "the
  National Park System", "the National Wildlife Refuge System", "the Bureau of Land Management"); a sentence whose
  subject is something else (a trail, a campground, a visitor centre); history ("was once part of"); a rule line
  ("as you explore the X please follow all posted regulations": that names X but does not say this place is in it).
- **Same core, different kind is still another unit:** "Red Cliffs Recreation Area ... within the Red Cliffs
  National Conservation Area".
- Store the quote, the unit's name, and its park number when POTA lists that unit in the same area (name core + kind).
- **Unsure:** store nothing in `inside_of`; put the sentence in `maybe_inside` (for a person).

## R-PR5. Sizes
- Reuse the truth checker's reader (`sizes_in`, its history / part / other-unit judgments). Do not write a second one.
- **New here, the label:** when a size sits in a labelled line or table ("Park: 4,740,091 acres", "Preserve: 1,334,118
  acres", "Total area: ..."), keep the label. Two or more labels = `SIZE_LISTED_BY_PART`.
- Round words are kept as said and marked not clean ("2.4-million-acre", "nearly 11,000 acres").
- **Never:** add sizes up, pick "the biggest", convert a lake's size into the park's, read a size from an unofficial
  host or from a page that is not the park's own (R-PR1).

## R-PR6. Coordinates
- **Counts, in this order:** JSON-LD `geo`; meta tags (`place:location:latitude` / `longitude`, `geo.position`,
  `ICBM`); a map link on the page (R-PR9); a labelled line in the text ("Geographic Coordinates", "GPS", "Lat / Long").
- **Checks:** latitude and longitude in range, the point inside the park's area (state / province box from the stored
  area tables) or within 300 km of POTA's pin; otherwise dropped and counted in `dropped_points`.
- **Role:** `office` when the point sits in a block headed Contact / Office / Headquarters / Address(es) / Mailing, or
  the link text names an office or visitor centre; `park` when the label or link names the park or says "location",
  "map", "directions to the park"; else `unknown`.
- Only a `park` point is compared with the pin (`PIN_FAR_FROM_PAGE`). Never "fix" the pin. The owner: "pins are only
  references, they are not always right"; the same is true of a point on a page.
- A forest, a trail, a river or a multi-unit refuge page gives no park point (kind word in a "no single point" list).

## R-PR7. Addresses and directions
- **An address** = street line + town + state + ZIP, or a P.O. box. Role by the heading above it and the words in it:
  "Field Office", "District Office", "Ranger District", "Headquarters", "Mailing", "P.O. Box" = `office` / `mailing`;
  "Park address", "Physical address", "Location", "Entrance", "Visitor Center" = `park` / `visitor-centre`; else
  `unknown`. An office address is never the park's location: `OFFICE_ADDRESS_ONLY` when it is the only one.
- **Directions** = the first 400 characters under a heading "Directions", "Getting here", "How to get there",
  "Driving directions"; plus the road names in it (I-15, exit 22, UT-228, US-71, "Old Highway 91") and towns named.
- **Never** turn an address or directions into coordinates. No geocoder, ever. They are text for a person.
- The owner asked for this block in these words: "location better than direction but directions should give us an
  address or location at least".

## R-PR8. Maps and named tracts
- **A map link** = a link whose text or address says map, brochure, boundary, GIS, "view map", or ends in pdf / kmz /
  kml / geojson / zip with such a word, or goes to a map app. Kind: `pdf`, `image`, `gis`, `web-map`.
- Open at most one map document (the first that names the park), first 400,000 bytes, text of 2 pages. Others are
  listed `not opened`. Nothing is saved; a row goes to `map-candidates.csv` for the club's PDF finder.
- **Named tracts** = proper names followed by Tract, Unit, Section, Block, Division, Parcel, "Area <number>", printed
  on the page or in the map's text, at least 2 different ones, each at most 5 words. History and legend lines do not
  count. `MANY_TRACTS` with the names. Example: Laurel (US-12938): Whitesville Tract, Edwin Bell Tract, Ralph's Corner.
- **Never** read an outline, a size or a location off a picture. The club traces nothing from pictures (rule R-G9).

## R-PR9. Facts in an address (no request)
- `marker:<lon>,<lat>;;<label>` and `marker=<lon>,<lat>` (ArcGIS: LONGITUDE FIRST); `center:<x>,<y>,102100` and
  `center=<x>,<y>,102100` (Web Mercator metres: convert); `center=<lon>,<lat>`; Google `@<lat>,<lon>,<zoom>z`,
  `?q=<lat>,<lon>`, `ll=<lat>,<lon>`, `destination=<lat>,<lon>`; Bing `cp=<lat>~<lon>`.
- Percent-escapes are decoded first. A marker with a label is a `park` point only when the label's core equals the
  park's core; a `center` alone is role `unknown` (it is where the map was looking, not where the park is).
- Worked example in `known-answers.json` ("address-facts").

## R-PR10. Refusals, walls and rests
- robots.txt is the only test of whether a page may be asked, read by the manners module. `robots` / 401 / 403 / a
  sign-in or "are you human" page = `refused`, remembered 30 days, no second try from any machine, the park goes to
  the person list. A 5xx or no answer = `resting` per the manners module, tried on a later run.
- Never change the User-Agent, never add headers to look like a browser, never use a cache, mirror or archive copy.

## R-PR11. Unsure
- Two readings possible = store neither as fact, keep both quotes under `maybe_*`, ask a question.
- A fact with no quote is a bug. A quote over 200 characters is cut at a sentence end.
- A park with nothing read is a normal result, with its reason. It is never dropped from the output.

## R-PR12. What people see
- Reviewers see `summary.md`, `questions.csv`, the person page. Members and guests see nothing from this bot.
- Any later use on the site (a "last checked" line, a link) is a separate job with the owner's GO and the club's
  notices; it is not built here.

## R-PR13. A picture of a map that has no file (the owner's idea, 19 Nov)
- **Counts:** the park's own page (R-PR1) was read with the site's leave, it shows a map that is drawn in the browser
  (a map app, a map panel, an image with no link to a file), AND the park has an open question or no official outline.
- **What is taken:** in a browser run only, ONE picture of the map part of the page (the map element, else the first
  screen), JPEG, long side at most 1600 px, quality about 70, at most 250 KB. Its row: park number, page address, date,
  what the element was, "picture for a reviewer, not a source".
- **Where it goes:** `park-pages/pictures/<ref>.jpg` in the RUN'S OUTPUT (the run artifact / the PC zip), shown beside
  the park's card on the person page. Not on `main`, not on the site, not in `picture-maps` (that branch is for the
  agency's own map documents). The club's rule: screenshots are small JPEGs, deleted after use; `intake` deletes the
  picture when the park's question gets an answer.
- **Does not count:** a site that said no (R-PR10): no picture, the link goes to the person list as before; a map file
  that exists but is big (list the link for the PDF finder, do not photograph it); a page that is not the park's own;
  a sign-in or cookie wall; a photo gallery.
- **Never:** a line, a size or a point read off the picture by the bot (R-G9: nothing is traced from a picture); more
  than one picture per park per 30 days; pictures for parks with no open question (cost, storage, no use).
- **Unsure whether the element is a map:** no picture; the page is listed `SCRIPT_BUILT` for a person.

## Grey areas (Fable's defaults; the owner may overrule)
- **G-PR4** map pictures stay in the run's output and are deleted after use; they never go on a branch or the site
  (default: yes; many web maps sit on a map company's background that the club may not hand on).
- **G-PR1** the PC run never asks a host that refused the cloud run (default: yes, a refusal holds everywhere).
- **G-PR2** no key rule reads these facts until a block shows 95 in 100 right on real runs and a reviewed rule change
  says so (default: yes).
- **G-PR3** the schedule stays off until the owner says GO (default: yes; by hand until then).
