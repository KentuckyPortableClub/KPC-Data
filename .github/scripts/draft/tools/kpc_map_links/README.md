# KPC Agency Map-Page Link Extractor

You give it an agency's one "Maps & brochures" style page. It finds the right official map
(PDF, image or map page) for each of that agency's parks and writes `docs_found.json` and
`report.csv`. **It decides nothing on its own.** Rows marked `POSSIBLE` need a person to look at them.
This tool is not wired into any workflow. The club bot hooks it up after Fable's review.

## Install

```bash
python3.11 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python -m playwright install --with-deps chromium   # only needed for script-built index pages
```

If the bundled Chromium is missing, the tool tries the system Chrome instead
(`KPC_BROWSER_CHANNEL=chrome` by default). Add `--no-browser` to never start a browser.

## Run

```bash
python kpc_map_links.py --agencies agency_pages.json            # parks.json is read from the same folder
python kpc_map_links.py --agencies agency_pages.json --resume   # carry on after a time-out or crash
```

| option | meaning |
|---|---|
| `--agencies FILE` | agency list (required) |
| `--parks FILE` | defaults to `parks.json` next to the agencies file |
| `--out DIR` | output folder (default `./out`) |
| `--resume` | skip agencies already `done` in `out/state.json`; re-try failed or partial ones; reuse file checks |
| `--max-minutes N` | stop cleanly after N minutes (default 50, so it fits in a 55-minute GitHub Actions job). Exit code 3 means "not finished, run again with `--resume`" |
| `--chunk i/n` | handle every n-th agency, starting at i, for parallel matrix jobs |
| `--only TEXT` | only agencies whose name contains TEXT |
| `--min-delay S` | minimum seconds between requests to one host (default 1.5) |
| `--no-browser` | never start the headless browser |

Exit codes: `0` finished, `2` bad input, `3` time budget reached (run again with `--resume`).
An agency that fails is logged with its error and the run moves on to the next one.

## Input

`agency_pages.json`
```json
[{"agency": "Lake Simcoe Region Conservation Authority - Trail Maps",
  "state_or_prov": "ON",
  "index_url": "https://lsrca.on.ca/index.php/enjoy-the-outdoors/trail-maps-and-closure-notices/",
  "park_refs": ["CA-6354", "CA-6355"],

  "doc_hosts": ["usfs-public.box.com"],          // optional: the agency's own file hosts on other domains
  "follow_patterns": ["^Region \\d+ WMAs"],       // optional: regexes for link text/URL of sub-pages to follow
  "render": "auto",                               // optional: auto | static | browser
  "wait_for": "#LabelList a",                     // optional: CSS selector to wait for when rendering
  "max_depth": 2, "max_pages": 300,               // optional
  "url_rewrites": [{"pattern": "...", "replace": "..."}]   // optional: used only when checking a file
}]
```
`parks.json`: `{ref: {name, type, lat, lon, alt_names: []}}`. Put the current POTA name and the
agency's own name in `alt_names` where they differ (for example "Hammonasset Beach State **Park**" for
POTA's "...State **Beach**").

## How it works

1. **Crawl.** It fetches the index page as static HTML first. In `auto` mode it starts headless
   Chromium only when no link on the static page matches any park. It follows pagination,
   `follow_patterns` links and links whose text or URL names one of the agency's parks. It stays on
   the **same host** as the index page and goes at most 2 levels deep.
2. **Candidates.** It keeps links to PDFs, images and KMZ/KML files, plus download-style links with
   no file extension (`/media/123/download`, a `mime-application-pdf` class, `(PDF)` in the text, Box
   share links). It also keeps in-page `<img>` maps and links whose text says map, brochure or guide.
   For each one it records the link text, file name, nearest heading, page heading, the link that led
   to the sub-page, and the sentence around the link.
3. **Match.** Names are normalised: case, accents, punctuation and zero-width characters are removed,
   runs of initials are joined (`R. F.` becomes `rf`), and type words are dropped (SP, SHS, SRA, WMA,
   NWR, CA, PP, SF, NF, "State Park", "Wildlife Management Area", "Conservation Area" and others).
   The score is a token-set ratio, **gated by how many of the park's own words appear**, so "Lake"
   cannot match "Lake Cumberland". A score of 0.90 or more is accepted, 0.75 to 0.90 is `POSSIBLE`,
   and anything lower is no match. Some evidence is capped at `POSSIBLE` no matter how high it scores:
   a match found only in the sentence around the link, an image or map page matched only through page
   context, or a type conflict (for example, the park is a State Forest but the document says WMA).
   When several candidates tie, it prefers: own link text or file name > nearest heading > page
   context, then PDF > image > map page, then map words, overview or index sheets, and the most
   specific name.
4. **Shared files.** No file is ever assigned to more than 3 parks. If one file is the best match for
   4 or more parks, all of them get `SHARED`, because a statewide file is not a park map.
5. **Check.** For each OK or POSSIBLE file, it fetches the file and confirms it opens, then checks the
   real type from its magic bytes (PDF/PNG/JPEG/GIF/KMZ/HTML). For PDFs it reads the text on pages
   1-2 and the PDF title to confirm the park name. It records Last-Modified and the PDF
   creation/modification dates. An OK row drops to POSSIBLE if the file won't open, comes back as
   HTML, or has readable text without the park name. Graphic-only PDFs with no text stay OK, and the
   `why` says the name could not be confirmed.

## Output

`docs_found.json`: `{ref: {page_url, map_url, kind, map_date, match_score, status, why,
park_name, agency, matched_text, alternates[≤3], checks{...}}}`

* `kind` is `PDF`, `IMAGE` or `MAP PAGE`, as the spec asks. Two extra values can appear: `KMZ`, and
  `DOC?` for a document link that could not be opened to confirm its type (see `why`).
* `map_date` is the PDF creation date, then the PDF modification date, then HTTP Last-Modified
  (YYYY-MM-DD).
* `status` is `OK`, `POSSIBLE`, `SHARED` or `NONE`. `why` always says which field matched, the
  score, and the result of the file check.

`report.csv` has the same data, one row per ref. `summary.json` has per-agency counts, pages
fetched, whether the browser was used, and notes such as robots.txt blocks or off-host redirects.
`state.json` holds the resume state.

## Rules it follows

* It only requests the index URL's host, its agency domain and any configured `doc_hosts`. For
  example, `app.fw.ky.gov` also allows `fw.ky.gov` and `*.fw.ky.gov`. Redirects are checked hop by
  hop. A redirect off the official hosts is refused and noted.
* It never contacts Google, OpenStreetMap, AllTrails, TripAdvisor, Wikipedia/Wikimedia, Bing,
  MapQuest or Waze. These are blocked in code even if someone configures them, and the headless
  browser aborts any request to them.
* It follows robots.txt per host using RFC 9309: product-token group, longest match wins, Allow
  wins a tie, `*` and `$` wildcards. It honours `Crawl-delay` (capped at 30 s). A robots.txt that
  returns 5xx or can't be reached means the whole host is treated as disallowed.
* It makes **one request at a time**. The whole tool is sequential, with a minimum delay per host
  and exponential back-off on 429/5xx (Retry-After is honoured, max 120 s).
* The User-Agent names the club: `KPC-MapLinkExtractor/<ver> (KPC parks club official-documents
  bot; ...)`. You can override it with the `KPC_USER_AGENT` environment variable. **Please put a
  real contact address in it before production use.**

## Tests

* `python tests/test_offline.py` runs offline unit tests: normalisation, score gate, robots
  longest-match, forbidden hosts, the SHARED rule, the type-conflict cap.
* `sample/` has the live test inputs and outputs. See `TEST_REPORT.md`.
