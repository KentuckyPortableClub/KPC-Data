# Test report: KPC Agency Map-Page Link Extractor v0.1.0

Run date: Sat 31 Oct 2026, 4:01 to 4:04 PM CDT (UTC-5).
Environment: Python 3.13.5 (the code targets 3.11+), requests 2.34, beautifulsoup4 4.15, RapidFuzz 3.14,
pypdf 6.21, Playwright 1.64 using the system Google Chrome (bundled Chromium was not installed on the test box).
Command: `python kpc_map_links.py --agencies sample/agency_pages.json --out sample/out`
Full log: `sample/run_log.txt`. Outputs: `sample/out/{docs_found.json, report.csv, summary.json, state.json}`.
The whole run took about 3 minutes and made 116 HTTP requests, one at a time, at least 1.5 s apart per host. Exit code 0.

## Test inputs

The club's real input files were not available, so I built small samples (`sample/agency_pages.json`, `sample/parks.json`).
Park refs, names and coordinates are real POTA records taken from the public POTA park list, to build the samples only.
The tool itself never contacts POTA. Each agency's index page was found on that agency's own official site.

| # | Spec slot | Index page used | Parks |
|---|---|---|---|
| 1 | Kentucky Fish & Wildlife WMA maps | https://app.fw.ky.gov/public_lands_search/ (KDFWR "WMA & Public Lands Search". KDFWR has no static all-WMA-maps page: the list is built by JavaScript, and each area's map PDF sits on its detail page) | 11 WMAs |
| 2 | New York DEC WMA maps | https://dec.ny.gov/places-to-go/wildlife-management-areas | 12 (11 WMAs + Partridge Run **State Forest** as a same-name trap) |
| 3 | A state parks "park maps" page | https://ctparks.com/park-maps (Connecticut DEEP State Parks) | 11 parks, forests and trails |
| 4 | A Forest Service unit's maps page | https://www.fs.usda.gov/r08/danielboone/maps-guides (Daniel Boone NF). Files are on the USFS Box account `usfs-public.box.com`, configured as a `doc_host` | 4 |
| 5 | A Canadian conservation authority | https://lsrca.on.ca/index.php/enjoy-the-outdoors/trail-maps-and-closure-notices/ (Lake Simcoe Region CA) | 7 conservation areas |

## Results: matched / possible / shared / none

| Agency | OK (matched) | POSSIBLE | SHARED | NONE | Pages | Browser | Time |
|---|---|---|---|---|---|---|---|
| Kentucky DFWR | **11** | 0 | 0 | 0 | 17 | yes (auto) | 47 s |
| New York DEC | 0 | 0 | 0 | **12, blocked by robots.txt** | 0 | – | – |
| Connecticut State Parks | **11** | 0 | 0 | 0 | 24 | no | 77 s |
| Daniel Boone NF (USFS) | 0 | **4** | 0 | 0 | 5 | no | 12 s |
| Lake Simcoe Region CA | **6** | 0 | 0 | 1 | 10 | no | 40 s |
| **Total (45 refs)** | **28** | **4** | **0** | **13** | | | |

### What happened at each agency

**1. Kentucky: 11/11 OK.** The static HTML had no park links. The tool noticed that, rendered the page in
headless Chrome (135 areas listed), followed only the 11 matching detail pages, and took each area's "View Printable
Map (PDF)" from `fw.ky.gov/More/Documents/`. All 11 PDFs opened, and the park name was found in the PDF text
for all 11. Hard names worked: "R. F. Tarter" matched `RFTarterWMA_ALL.pdf`, "Dr. James R. Rich" matched
`Dr.JamesR.RichWMA_ALL.pdf`, and "Kentucky River" was not confused with Kentucky Lake or Kentucky Ridge.
*Needs a person:* POTA's "Burchell-Beech WMA" was matched to KDFWR's **Burchell-Beech Creek** WMA map.
It is probably the same area, but the name differs.

**2. New York DEC: not tested, robots.txt blocks it.** `dec.ny.gov/robots.txt` has `Disallow: /places`.
Under standard prefix matching, that also covers `/places-to-go/wildlife-management-areas` and the
`/places?...` region listings. Only the individual `/places/<wma>` pages are allowed, through `Allow: /places/*`.
The tool refused the index page as the spec requires, logged the reason, and went on to the next agency. A manual
look before the run showed that the WMA pages carry PDF links such as "Bashakill WMA Map"
(`/sites/default/files/...pdf`), so the matcher would probably work. The club needs a robots-allowed NY entry
point, or permission from DEC.

**3. Connecticut: 11/11 OK.** Every link on this page reads "Park Trails Map" and the file URLs are
`/media/NNN/download?inline` with no extension. Matching worked from the nearest heading (the park name),
and the real type came from checking each file. Alt names fixed POTA vs. agency name differences
(Hammonasset Beach State *Beach* / *Park*, Air Line State *Trail* / *State Park Trail*). Name confirmed in
the PDF for 9; Sleeping Giant's PDF has no readable text, so the name could not be confirmed.
*Worth a look:* for **Pachaug State Forest** the tool chose "Pachaug State Forest Hunting Maps" over the
generic "Park Trails Map (Green Falls)". The hunting map is the only link that names the forest itself. The
trail maps are listed under `alternates`.

**4. Daniel Boone NF: 4 POSSIBLE, none could be checked.** The brochures and maps are links on the Forest
Service's own Box account. Red River WSR and Sheltowee Trace matched the link text at 1.00. Clifty Wilderness
and the forest itself matched only through the sentence around the "Rock Bridge, Swift Camp Creek and Wildcat
Trails Map" link, so they were held at POSSIBLE by design. None of the files could be opened: Box redirects
the download to `/public/static/...`, and `usfs-public.box.com/robots.txt` disallows that path for all bots.
The tool stopped at the redirect, so all 4 stay POSSIBLE with the reason in `why`. The forest-wide map is
an ArcGIS viewer on another host, which is out of scope, so no OK was possible for the forest itself.

**5. Lake Simcoe CA: 6 OK, 1 NONE.** Mabel Davis CA is not on the trail-maps page or its sub-pages, so NONE
is the correct result. Two traps were handled:
* The index page links "Thornton Bales" to `rogers.pdf` (the Rogers Reservoir map). The tool followed the
  Thornton Bales sub-page and found `thornton_bales-1.pdf`, with the name confirmed in the PDF.
  `rogers.pdf` shows only as an alternate.
* A link reading "Beaver River Wetland" actually points to the *Bailey Ecological Park* page. The tool
  ignores "came from link" text when the sub-page's own heading disagrees. It picked the Beaver River trailhead
  sign PDF, which is a trail map with the name in its text.

### SHARED

No real file hit the "more than 3 parks" rule in these 5 samples, so SHARED was **not exercised on live
data**. It is covered by the offline unit test `test_shared_and_possible`: one statewide PDF reached from
5 park pages gives 5 SHARED rows. The type-conflict cap (State Forest vs. WMA, which made a POSSIBLE) is
covered offline too, because the NY Partridge Run trap could not run.

## Other checks run

* The NY failure appears in `run_log.txt` as an ERROR with a traceback. That is expected: the agency is
  marked `error` and the run carries on.
* `python tests/test_offline.py`: 6/6 pass (normalisation, score gate, RFC 9309 robots longest-match,
  forbidden hosts and host policy, SHARED rule, type-conflict cap).
* **Time budget and resume:** `--max-minutes 0.6` stopped in the middle of Kentucky with exit 3 and saved
  state. `--resume` then finished every agency. A second `--resume` skipped the 4 finished agencies and
  re-tried only the failed NY one (1 request: its robots.txt). Both passed.
* **Off-host safety:** on ctparks.com, 15 `/node/NNNNN` links redirect to `ctvisit.com`, the state tourism
  site. Each one was refused at the redirect and logged in `summary.json` notes. Google Maps "Get Directions"
  links on the KY and NY pages were never followed.

## Not tested or known gaps

* **GitHub Actions:** the tool was never run on Actions; it was run headless on a Linux box only. The
  Actions-specific pieces (`--max-minutes`, `--chunk`, `--resume`, exit code 3) were tested locally, but no
  workflow file is included, as instructed.
* **Bundled Playwright Chromium** was not installed on the test box, so the system Chrome fallback was used.
  On Actions, run `python -m playwright install --with-deps chromium`.
* **New York DEC** (robots.txt) and **USFS Box files** (robots.txt on Box) could not be fetched. Both are
  real limits of those sites, not tool crashes.
* **SHARED** was tested offline only.
* Only one sample page per agency type was tried. Agencies whose lists need clicks or form posts to appear
  (beyond what loads on its own) are not handled: `render: browser` only loads the page and waits for `wait_for`.
* When the browser renders a page, Chrome loads that page's own JS/CSS in parallel, so "one request at a time"
  holds for every request the tool makes itself, but not inside the browser. Images, fonts and media are
  blocked to keep the load small.
* Before writing the tool, I made about 30 manual requests (curl with the same club UA, one at a time) to
  these 5 hosts to find the index pages and read their robots.txt files.
