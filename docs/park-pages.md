# Park page reader

The reader looks at the page POTA already links, once, and writes down what the page says. It does not decide a key, an outline, or a boundary. A fact is evidence. A rule or a person decides.

## What it reads

Stored files only. It never calls `api.pota.app`.

- `data/parkinfo/<area>.json` gives the name, POTA's link, the type, and the pin. A link field may hold more than one address. The first address on an official host is the one opened. The others are counted and left closed.
- `data/parkinfo-web.json` supplies `web` when POTA has no link. `agency_page` is a list, not the park's page, and is not read.
- `data/docs/<area>.json` supplies a page the documents bot already found. The reader does not search for that page again.
- `data/truth/<area>.json` holds a size already read. A later part can reuse it when the fingerprint matches. This part does not ask the page again for a size it already stored from the same text.

Before any request the reader reads the address itself. A marker, a Web Mercator center, and a Google or Bing pin in the link are facts, and they cost no request.

Then at most four requests for one park: the park's page, one facts page when the family has one (NPS statistics, a linked Forest Service about page, a refuge about page), one directions page when the first page has none, and one map document that names the park (first 400,000 bytes, text of two pages). A map file is not saved.

## What it never does

It changes no key, no saved answer, no outline, no map, and no public page. It opens no issue and sends no mail. It does not geocode, search, or call a keyed API. It does not fetch on its own: every request goes through `kpc_manners.Manners`. A host that says no (robots, 401, 403, a sign-in wall) is remembered for 30 days and is not asked again. `services*.arcgis.com` is never asked, because the host rules already refuse it.

A picture of a map is taken only in a browser run (`BROWSER=1`), only after the site has allowed the page, and only for a park that still has a question. One small JPEG. Nothing is traced from it.

## How to run it

Offline check, no network:

```
python3 .github/scripts/kpc_park_pages.py --selftest
python3 tests/test_park_pages_nov19.py
```

Read stored parks into a folder. With `--fixtures` the pages come from a manifest and nothing is asked of the network. Without it, the reader uses Manners. `KPC_NO_NET=1` with no fixtures reads nothing.

```
python3 .github/scripts/kpc_park_pages.py read --data data --out park-pages --state park-pages/state.json --areas "US-UT"
```

Worklist and report:

```
python3 .github/scripts/kpc_park_pages.py worklist --data data --links /path/to/KPC-Links --lists lists/ --not-sure not-sure --out park-pages
python3 .github/scripts/kpc_park_pages.py read --data data --out park-pages --lists lists/ --not-sure not-sure --fixtures tests/fixtures/park-pages/manifest.json
python3 .github/scripts/kpc_park_pages.py report --out park-pages
```

On the owner's PC, `pc-kit` writes a small zip (the scripts, the rows for the named areas, the state file). `tools/park-pages-pc/` has the two launchers. `person-page` writes one phone page for parks the bot could not read. `intake` folds a PC zip or `person-answers.json` back in. A person's answer wins for that fact. The bot's answer is kept as `bot_saw`. `kits` writes two blind passes. The answer key goes to `kit-keys/` and is not inside either pass. `score` compares the two passes and the plants.

The by-hand workflow is `.github/workflows/kpc-park-pages.yml`. It starts only when someone runs it. The schedule line is written and commented out. The read job holds no token. The save job is the only one that can write. It checks out `main` and copies the folder onto `tools-out`. It does not run this reader.

## List drops

Any club tool may leave a JSON file in `park-pages/lists/` on the `intake-files` branch. The reader takes those parks first, after the not-sure rows. Unknown keys are ignored. A park number must exist. A file with more than 5,000 rows is skipped. A list that already has an answer for every park is not read again.

```json
{
  "made_by": "keeper",
  "date": "2026-11-19",
  "why": "the name matches two records",
  "parks": [
    {"ref": "US-6063", "why": "name matches two records", "want": ["inside_of", "sizes"]}
  ]
}
```

## The not-sure list

The shared list is `kpc_not_sure.py`. It lives on `tools-out` under `not-sure/`, one file per area. This reader does not push that branch. The save job copies the folder there when the club runs the workflow.

One row is one park and one doubt:

```json
{
  "ref": "US-6063",
  "area": "US-UT",
  "name": "Red Cliffs BLM Recreation Management Area",
  "code": "INSIDE_BIGGER_UNIT",
  "how_sure": "unsure",
  "shows_now": "html",
  "why": "The page says this place is within 'Red Cliffs National Conservation Area'.",
  "wants": ["page facts"],
  "found_by": "park page reader",
  "first_seen": "2026-11-19",
  "last_seen": "2026-11-19",
  "evidence": {"source": "https://www.blm.gov/visit/red-cliffs-recreation-area", "saw": "within the Red Cliffs National Conservation Area", "date": "2026-11-19"},
  "tried": [],
  "status": "open",
  "settled": {"by": "", "date": "", "how": "", "link": ""}
}
```

A second example, a group rather than one park. No bot works a class row:

```json
{
  "ref": "(class)",
  "area": "US",
  "name": "every outline that did not change in this release",
  "code": "NOT_SAMPLED",
  "how_sure": "unchecked",
  "shows_now": "outline",
  "why": "only changes were checked; the 1-in-100 bar needs a random sample",
  "wants": ["random sample"],
  "found_by": "release call",
  "first_seen": "2026-11-19",
  "last_seen": "2026-11-19",
  "evidence": {"source": "", "saw": "", "date": ""},
  "tried": [],
  "status": "open",
  "settled": {"by": "", "date": "", "how": "", "link": ""}
}
```

`how_sure` is one of: wrong likely, unsure, incomplete, unchecked, fairly sure. `status` is one of: open, parked, settled, gone. `wants` uses only: page facts, official size, map, official layer, far-join evidence, a person, the owner, random sample. Codes are the ones in `not-sure/README.md`. The page reader may add a row and a tried note. It does not settle a row.

## How to read the output

`facts/<area>.json` holds one object per park. The fields are the ones in the worked example for US-6063: the page, whose page it is, the name, the kind words, `inside_of`, sizes with their labels, location, maps, tracts, the manager, and `questions`. Every fact that can carry a sentence has a quote. A question is the reader saying a person should look, not an answer.

`run.json` records the day and how many requests the run made. `state.json` remembers resting hosts, refused hosts, and the fingerprint of each page, so a later run does not read the same page twice.
