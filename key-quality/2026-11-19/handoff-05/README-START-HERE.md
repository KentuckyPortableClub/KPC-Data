# KPC hand-off 05: the PARK PAGE READER (the "helper bot")

From: Kentucky Portable Club (owner Brandon White, KZ4CP), written by the club's reviewer (Fable), 19 Nov 2026.
For: the outside agent. You build it; the club reviews it, merges it and starts it. You merge nothing and start nothing.

Read in this order: this file, `RULE-SHEET.md`, `CODE-MAP.md`, `known-answers.json`, `example-facts-US-6063.json`.

---

## 1. Why this bot exists (one true story, today)

The club draws park outlines from official map layers. For most parks the name and the pin are enough. For the rest the
rules guess, and a person has to step in. Today the owner stepped in five times and each time the answer was sitting at
the top of the page POTA itself links to:

- Six parks POTA lists as "National Park" / "National Monument" only: the park page's headline says
  "... National Park & Preserve". One look, done.
- Red Cliffs (US-6063): the page says the place is "within the Red Cliffs National Conservation Area". The big area is a
  different park (US-6077). One sentence, done.
- Laurel (US-12938): POTA's link IS the agency's map, with the three tract names printed on it.

A person should not have to do that first look. **The reader does the first look for every park, once, politely, and
stores what it saw with the sentence it saw it in.** Then:

1. the key rules have official facts in front of them before they guess (a later job, by the club, never by this bot);
2. a reviewer gets the evidence row already filled in (who, source, what was seen, date);
3. what a bot cannot read becomes a short tidy list for a person or for an outside agent, never a silent gap.

The owner's words for the standard: "accurate and reliable and very efficient in our time ... bots, schedules, outside
resources, other agents, my pc, build tools I can run on my pc or you all start and come back later and fetch it".

## 2. The four laws (every line of code answers to these)

1. **It reports. It never decides.** It changes no key, no saved answer, no outline, no map, no public page, no issue
   comment. Its files are for reviewers and for other bots. A fact is evidence; a rule or a person decides.
2. **Silent beats wrong.** Every fact carries the address it came from and a short quote. No quote, no fact. When two
   readings are possible it stores neither and asks a question. A missing fact costs a minute; a wrong fact costs a state.
3. **Polite by the house module only.** Every request goes through `kpc_manners.Manners`. No fetch code of its own, no
   second robots reader, no retries of its own, no search engine, no geocoder, no keyed API, no `api.pota.app`.
4. **Nobody has to feed it.** It builds its own worklist from stored files, remembers where it stopped, and can be run
   three ways with the same code and the same output (section 4).

## 3. What you build (four parts, in this order, each sent back on its own)

| Part | What | Must work before the next part |
|---|---|---|
| 1 | The reader: `kpc_park_pages.py read`, the facts file, the questions, the offline tests | yes |
| 2 | The worklist + the by-hand workflow + the summary a chat fetches later | yes |
| 3 | The owner's PC runner + the page a person fills in + the answers intake | yes |
| 4 | Blind two-pass kits for outside agents, made by the bot from what is still open | last |

Send part 1 as soon as it passes its tests. Do not hold it for parts 2 to 4. A finished part 1 is useful by itself.

Files (all in **KPC-Data**):

- `.github/scripts/kpc_park_pages.py` (one file, commands `read`, `worklist`, `report`, `person-page`, `intake`, `kits`,
  `--selftest`); small helper modules only if a file passes about 900 lines (`kpc_park_pages_rules.py` for the reading
  rules is a good split: pure functions, no network, easy to test).
- `.github/workflows/kpc-park-pages.yml`
- `tests/test_park_pages_nov19.py` (+ `tests/fixtures/park-pages/`, small, see section 12)
- `tools/park-pages-pc/` (the PC launcher, part 3)
- `docs/park-pages.md` (one page: what it reads, what it never does, how to run it, how to read the output)

## 4. Three ways to run, one code, one output

1. **GitHub, started by hand** (`workflow_dispatch`). A schedule line is written but COMMENTED OUT with the note
   "switched on only with the owner's GO". Never red, no emails (section 9).
2. **On the owner's PC.** One double-click launcher (`run-park-pages.bat` for Windows, `run-park-pages.sh` for Mac /
   Linux). Python 3.10+ standard library is enough for web pages; `pypdf` and Playwright are optional extras the script
   detects and uses when present, and says in one line when absent. Output: a folder and a zip next to the launcher.
   The owner is a ham, not a developer: the launcher prints plain sentences ("Reading 40 of 300 parks ...", "Done. Send
   the file park-pages-2026-11-19.zip to the chat."), never a stack trace (errors go to `run-log.txt`).
3. **Start now, fetch later.** Every run, on any machine, ends by writing `summary.md` (one phone screen) and
   `run.json`. A club chat reads them the next time it is asked. Nothing waits on the run.

The state file (`state.json`: resting hosts, refused hosts, what was read and when, page fingerprints) travels with the
output, so a PC run continues a GitHub run and the other way round (`--state <file>` in, same file out).

**A refusal is a refusal on every machine.** A host that told the bot no (robots.txt says no, a 401 / 403, a sign-in or
"are you human" wall) is remembered in `state.json` for 30 days and is not asked again from the PC either. Those parks go
to the person list (section 10). The PC runner exists to save run minutes and emails, never to get around a no.

## 5. Inputs (all stored files; zero requests to POTA)

| File | What you take |
|---|---|
| `data/parkinfo/<area>.json` | `parks[ref] = [name, website, type, activation, access, lat, lon, activations, attempts, qsos]`. `website` may hold SEVERAL addresses separated by spaces (see US-0878). This is "POTA's link". |
| `data/parkinfo-web.json` | `parks[ref]`: `web` (the park's page when POTA has none), `agency_page` (a general list: NOT the park's page), `map`, `map_page`, `group_site`, `map_hold` |
| `data/docs/<area>.json` | `parks[ref].page`, the map link and its status (already found by the docs bot: do not find it twice) |
| `data/truth/<area>.json` | `parks[ref].official` (a size already read from the page), `pages` (addresses already tried and their status) |
| KPC-Links `data/us-key/US-XX.json` | `parks[ref] = {n, m: [[record id, name, acres, how]], c: [check rows], g: official / approximate / pin}` for the worklist order (part 2) |
| `--refs-file list.json` | optional: a plain list of park numbers to read first (the club drops lost / shrinking lists here) |

`sample-data/` holds the real rows of these files for the 31 test parks. Check every index against the code that writes
the file (`CODE-MAP.md`) before you rely on it: never trust this page over the code.

## 6. What it reads for one park

Before any request, **read the address itself.** Many map links carry facts in the address
(`marker:-113.405%2C37.224%3B%3BRed%20Cliffs%20Recreation%20Area`, `center:<x>,<y>,102100`, `@37.22,-113.40,15z`,
`?q=37.22,-113.40`). Address facts cost nothing and offend no one (rule R-PR9).

Then at most **4 requests per park** (a switch, default 4):

1. the park's page (POTA's link; else `web`; else the docs page). Several addresses in one field: the first on an
   official host; the others are noted, not opened;
2. one "facts" page when the agency family has one (see the family table below);
3. one "getting there" page, when the first page links one and has no directions of its own;
4. one map document linked from the page, **first 400,000 bytes only** (`rng=`), text of its first 2 pages
   (`pdf_text`). Never the whole file, never saved (saving maps is the PDF finder's job; you list the link for it).

A page that builds itself with scripts: the plain read first; when the visible text is under 400 characters or the
address is a known app shell (`experience.arcgis.com`, `storymaps.arcgis.com`, `*.maps.arcgis.com/apps/`), kind =
`script-built`; with `BROWSER=1` one `browser_text` read is allowed; without it the park goes to the person list.
Remember `services*.arcgis.com` gets no request of any kind (the host rules refuse it; you never see it).

**A picture when there is no file** (the owner, 19 Nov: "should the bot screen shot what it thinks are maps on the
weblinks if it can't download it?"). Yes, inside rule R-PR13: only in a browser run (`BROWSER=1`), only where the site
let the page be read, only for a park that still has an open question or no official outline, one picture per park of
the map part of the page, a small JPEG for the reviewer's eyes. Never when the site said no, never traced, never
published, deleted when the question is answered.

**Agency families** (a small table in the code, one row per family, each row = how to find pages 2 and 3; everything
else uses the general reader). Start with these six; adding a family must be one table row plus one fixture test:

| Family | Park page looks like | Facts page | Notes |
|---|---|---|---|
| National Park Service | `www.nps.gov/<code>/index.htm` | `/<code>/learn/management/statistics.htm`, else `/<code>/planyourvisit/basicinfo.htm` | keep `<code>` (4 letters) as a fact: the key has an NPS-code rule. One page often serves 2 or 3 POTA parks (park, preserve, river). |
| Bureau of Land Management | `www.blm.gov/visit/<slug>` | none | "Contact Us" and "Addresses" hold the FIELD OFFICE, not the park (the trap in the Red Cliffs fixture) |
| Forest Service | `www.fs.usda.gov/<forest>` or `/main/<forest>/home`, `/recarea/...` | `/about-area` when linked | forests span states and districts: never a point location from a forest page. `apps.fs.usda.gov` is never asked (host rules). |
| Fish and Wildlife Service | `www.fws.gov/refuge/<slug>` | `/refuge/<slug>/about-us`, `/visit-us` | acreage often on "about us" |
| Army Corps of Engineers | `www.<district>.usace.army.mil/...` | none | lake projects: land and water figures both appear; label them |
| State park systems | many shapes | none | many are script-built; several redirect to a tourism host (Arkansas) |

Open a real page of each family by hand in your own browser before you write its row. Do not trust this table's
addresses; they are where to look, not a promise.

## 7. The facts (what is stored for one park)

`example-facts-US-6063.json` is the worked example; `RULE-SHEET.md` has the exact reading rule for every block. In short:

- `page`: asked address, final address, status, `kind` (`html`, `pdf`, `script-built`, `refused`, `robots`, `resting`,
  `dead`, `moved`, `none`), date read, fingerprint (first 12 hex of sha256 of the visible text), reader version;
- `own_page`: `own` / `shared` (with the park numbers that share it) / `agency-home` / `list` / `other-unit` /
  `unofficial-host`, and one line why;
- `name`: title, first heading, the best name, and how it compares with POTA's name (`same`, `same-core`, `differs`);
- `designation`: the kind words in the page's OWN NAME, and `combined` + `parts` when the name joins two kinds
  ("National Park & Preserve"), plus `pota_numbers_part`: the park number POTA gives the other part in this area, or
  `null` (a look-up in the stored park list; this is the one thing the club's new rule R-PP1b needs);
- `inside_of` / `contains`: named units the page says this place lies in or holds, with the quote and that unit's park
  number when POTA lists it in the same area;
- `sizes`: every size on the page with its label ("Park", "Preserve", "Total area", "lake"), its sentence, and whether it
  is a total, a part, history or another unit's (reuse the truth checker's reader; add only the label);
- `location`: coordinates (source, role park / office / unknown, kilometres from POTA's pin), addresses with a role,
  the directions text (first 400 characters) and the road names in it, towns and counties named;
- `maps`: links to map documents and map apps, kind, whether the link names the park, not opened / opened / status;
- `parts`: named tracts and units ("Whitesville Tract") from the page or the first two pages of the map;
- `manager`: agency and office;
- `status_words`: closed for good, handed over, renamed (reuse the truth checker's three patterns);
- `questions`: the codes of section 8, each with a plain sentence and the quote.

Keep it small: quotes at most 200 characters, at most 12 quotes per park, no page text stored, about 2 KB per park.

## 8. The questions it asks (plain words, one line each)

A question is the bot saying "a reviewer should look here, and here is the sentence". It is never an answer.

| Code | When | The plain line |
|---|---|---|
| `COMBINED_UNIT` | the page's name joins two kinds and POTA numbers NO separate park for the other part | "The page calls this '<name>'. POTA lists no separate park for the <part> here." |
| `COMBINED_BOTH_NUMBERED` | the same, and POTA does number the other part | "The page covers '<name>'. POTA lists the <part> as <ref>." (information, not a problem) |
| `INSIDE_BIGGER_UNIT` | an `inside_of` unit was found | "The page says this place is within '<unit>'" + " (POTA <ref>)" when numbered |
| `DESIGNATION_DIFFERS` | the page's kind words and POTA's type share no word | "POTA says '<type>'. The page says '<kind>'." |
| `NAME_DIFFERS` | best name and POTA's name differ beyond kind words | "POTA: '<a>'. Page: '<b>'." |
| `SHARED_PAGE` | 2 or more parks of the area list this page | "<n> parks use this page: <refs>." |
| `AGENCY_HOME_ONLY` | the link is an agency's front page or a list | "POTA's link is the agency's front page, not this park's page. Nothing was read from it." |
| `UNOFFICIAL_HOST` | the host is not an agency's or its government's | "The link is not an agency page (<host>). Facts from it are marked unofficial." |
| `OFFICE_ADDRESS_ONLY` | the only address is an office / mailing address | "The only address on the page is the <office>, not the park." |
| `PIN_FAR_FROM_PAGE` | a park-role coordinate is over 5 km and over 2 x the park's own radius from POTA's pin | "The page's map point is <km> km from POTA's pin." |
| `SIZE_LISTED_BY_PART` | sizes carry two or more labels | "The page gives sizes by part: <label a> <n>, <label b> <n>." |
| `MANY_TRACTS` | 2 or more named parts | "<n> named tracts: <names>." |
| `LINK_MOVED` | the final host differs from the asked host | "The link now lands on <host>." |
| `LINK_DEAD` | 404 / 410 / no such host, twice a week apart | "The link does not open." |
| `REFUSED` | robots.txt no, 401 / 403, a wall | "The site does not take automated visitors. For a person." |
| `SCRIPT_BUILT` | script-built and no browser read | "The page builds itself in the browser. For a person or a browser run." |
| `NO_PAGE` | no link in any stored file | "No page on file for this park." |
| `CLOSED_OR_MOVED_WORDS` | a status pattern matched | the truth checker's own line, with the quote |

## 9. Part 2: worklist, workflow, summary

**Worklist** (`kpc_park_pages.py worklist --links <KPC-Links> --data <KPC-Data> [--refs-file ...] [--areas "US-AK US-UT"]`).
Order, best first; a park is taken once:

1. parks on a **list drop** (below) and in `--refs-file`;
2. parks whose key row has check rows (`c` not empty) or grade `approximate`;
3. parks with grade `pin` (no outline) that have a page on file;
4. parks whose page was never read, busiest first (`qsos`);
5. parks whose facts are older than `REFRESH_DAYS` (default 30), oldest first.

A page whose fingerprint did not change keeps its facts and only gets a new `seen` date (no re-parse, no new question).
A changed fingerprint writes one row to `changes.csv` ONLY when a fact changed (name, kind words, a size, the final
host); a changed footer is not a change.

**List drops: other tools hand the reader its list, no person in between** (the owner, 19 Nov: "would it be smart if
the tool I use on the pc that prematches parks and pulls data made a list for the bot ... or the keeper made the list?
Automation helps"). Yes. Any tool may drop a list; the reader picks every list up by itself on its next run:

- where: KPC-Data branch `intake-files`, folder `park-pages/lists/`, one small JSON file per tool and day
  (`<tool>-<date>.json`); the workflow fetches that folder itself; the PC launcher also reads any `*.json` put in its
  own `lists/` folder;
- shape: `{"made_by": "keeper" | "pc-prematch" | "key-run" | "<name>", "date": "2026-11-19", "why": "one plain line",
  "parks": [{"ref": "US-6063", "why": "name matches two records", "want": ["inside_of", "sizes"]}]}`
  (`want` is optional: the blocks that tool most needs; the reader still reads every block);
- the reader validates each file (park numbers exist in `data/parkinfo`, at most 5,000 rows, no other keys run as
  code, unknown keys ignored), reads listed parks FIRST in the order given, and writes back per list
  `park-pages/lists-done/<same name>.json`: for each park `read` / `unchanged` / `refused` / `no page` + its questions,
  so the tool that asked can pick its answers up without a person;
- a list is done when every park on it has an answer row; done lists are not read again;
- you build the reader's side only. The club wires its own tools (the layer keeper, the key run, the owner's PC
  pre-match tool) to write this shape. Put the shape and one example in `docs/park-pages.md` so they can.

**Budget and stops**: `--max-requests` (default 1500), `--max-minutes` (default 50), per host the manners module's own
pace; stop cleanly, save state, say in the summary how many parks are left and that the next run continues.

**Workflow** `kpc-park-pages.yml`: copy the pattern of `kpc-trace-test.yml` and the lessons of pull request 124
(`CODE-MAP.md`, "review lessons"). The hard requirements:

- `on: workflow_dispatch` only, inputs: `areas`, `max_requests`, `refs_file`, `browser` (off by default);
- top-level `permissions: contents: read`; two jobs: `read` (read-only, no write credential in its checkout:
  `persist-credentials: false`) uploads the output as a run artifact; `save` (the only job with `contents: write`,
  runs NO code from a pull request, only checks out `main` and commits the artifact to branch `tools-out` under
  `park-pages/` with `kpc_push_retry.sh`);
- `GH_TOKEN` only on steps that call `gh`; no step that runs the reader holds a write token;
- never red: every step `continue-on-error: true` with an `id`, the "hidden failures" step last (copy it whole);
- no YAML key written twice in one step (pull request 124 had `continue-on-error` twice: the file was invalid). Your
  test loads the workflow with a loader that REFUSES duplicate keys and checks the permissions block;
- `concurrency: group: kpc-park-pages, cancel-in-progress: false`;
- it starts no other workflow, opens no issue, writes no comment, sends nothing.

**Summary** (`summary.md`, at most 40 lines, plain words): parks asked / read / kept unchanged; pages by kind; questions
by code with counts; the 15 most important questions with park number and plain line (worklist order); hosts that
refused; what is left; where the files are. This is the file a chat reads "later", so it must stand alone.

Output folder on `tools-out`: `park-pages/facts/<area>.json`, `park-pages/questions.csv`,
`park-pages/for-a-person.csv`, `park-pages/evidence-drafts/<area>.json`, `park-pages/changes.csv`,
`park-pages/summary.md`, `park-pages/run.json`, `park-pages/state.json`. Whole folder under 15 MB for the US.

**Evidence drafts**: for each question a reviewer may have to rule on (`COMBINED_UNIT`, `INSIDE_BIGGER_UNIT`,
`MANY_TRACTS`, `SIZE_LISTED_BY_PART`), one DRAFT row in the club's evidence shape:
`{"ref": ..., "who": "bot: park page reader v1", "source": <address>, "saw": <the quote>, "date": <day read>,
"question": <code>, "draft": true}`. Drafts live only in `evidence-drafts/`. The bot never writes
`data/us-key/overrides*.json`; a person or the reviewer promotes a draft by hand.

## 10. Part 3: the PC runner, the person page, the intake

**PC runner** `tools/park-pages-pc/`: the two launchers, `README-PC.txt` (ten plain lines), and nothing to install for
the basic run. It asks one question at most ("Which state? (blank = continue the list)"). It reads the worklist file
and the stored rows from a small input zip the club's chat makes (`kpc_park_pages.py pc-kit --areas ... --out
park-pages-pc-kit.zip`: the script, the manners + host-rules modules, the needed rows, the state file; no secrets, no
whole repo). It writes `park-pages-<date>.zip` to send back. `intake` (below) folds that zip in.

**Person page** `for-a-person.html` (`kpc_park_pages.py person-page`): one self-contained file, no network, under
300 KB, works at phone width (390 px, no sideways scroll; the owner works from his phone). One card per park the bot
could not read: park number, POTA's name and type, the link (opens in his browser), and five small fields:

1. the name at the top of the page;
2. tick boxes: "says '& Preserve' (or two kinds)", "says it is inside another named area" + the area's name;
3. size on the page (number + the words around it);
4. named tracts, if a map shows them;
5. "could not tell".

A "Save answers" button makes `person-answers.json` (download, and a "copy" button for the phone). No answer is ever
pre-filled from the bot's guess. Practice call signs never appear; no real call sign is used as an example anywhere.

**Intake** (`kpc_park_pages.py intake <file>`): folds a PC zip or a `person-answers.json` into the facts files. A
person's row is stored with `by: "person"`, `who` (the name typed on the page), `date`, and wins over the bot's row for
the same fact; the bot's row is kept beside it as `bot_saw`. A person's answer that disagrees with a bot fact writes one
row to `disagreements.csv`: that file is how the club measures the bot (section 12).

## 11. Part 4: kits for outside agents

`kpc_park_pages.py kits --n 40 --seed <n> --out kits/` takes the open questions no bot and no person has answered and
writes two blind kits (`pass1`, `pass2`): the same parks in a different order, each with the park number, POTA's
name, type and link, and the questions of the person page. Plus 4 to 8 **plants** per kit: parks whose answer the club
already knows (from `person` rows and from `known-answers.json`), mixed in unmarked. The answer key goes to
`kit-keys/` and is NEVER put in a kit, a zip or a pull request body. One pass never sees the other pass's answers.
`kits score` compares the two passes and the plants: agreed, differ, plant score. Copy the shape of the club's
hand-off 04 (`CODE-MAP.md`).

## 12. Tests and the acceptance bar

All tests offline (the test file refuses network: see how `tests/test_evidence_cards_nov17.py` guards the socket).
Script style of the repo: prints `PASS` / `FAIL` lines, ends `ALL PASS` / `SOME FAILED`; pytest is not the suite.
Before you send anything run the hand-off gate (`tests/HANDOFF-GATE.md`) and paste its last lines in your notes.

Fixtures: SMALL trimmed copies (title, headings, the few sentences read, the link list; under 15 KB each, under 300 KB
in all), made from pages you opened by hand, one per family and one per question code. Do not run the bot against
agency sites to make fixtures. The Red Cliffs page text the owner saved is in `fixtures/` here: use it as is.

What must pass:

1. every reading rule of `RULE-SHEET.md` has a test for the plain case, the trap case and the silent case;
2. `known-answers.json`: every row marked `must` gives exactly the stated fact or status from its fixture;
3. the reader makes no request in `--selftest` and in tests; with an empty state and no fixtures it fails closed;
4. a run stopped half-way and started again reads no park twice and loses no fact;
5. the workflow test (no duplicate keys, permissions, no write token on reader steps, hidden-failures step last);
6. the person page at 390 px: no sideways scroll, every field reachable, the saved file loads in `intake`.

**The accuracy bar** (the reason for law 2). In your notes give a table: for each fact block (name, combined kind,
inside_of, sizes, coordinates, address role, tracts) the number of fixtures tested, facts expected, facts found, facts
WRONG, facts silent. The club's bar: **wrong = 0 on the known answers, and at least 95 in 100 right on any block before
a rule is allowed to use it** (the club measures that later on real runs with `disagreements.csv`). Silent is allowed
and is reported honestly. If a block cannot reach the bar, say so and leave it reporting `unknown`; do not tune it on
the test parks until they pass.

## 13. What is NOT in this job

No change to a key, a rule file, a saved answer, an outline, a site page or a schedule. No geocoding service. No search
engine. No `api.pota.app`. No keyed API (`developer.nps.gov`, `ridb.recreation.gov`: the club's permission for those is
narrow and is not yours to use). No map files saved. No tracing. No issue comments, posts or emails. No secrets, keys or
tokens in any file, and never ask the owner to paste one. Nothing on KPC-Data `main` over 1 MB.

## 14. Send back

- A **draft** pull request to KPC-Data per part, from a branch `prep/park-pages-part<N>`. You do not merge, you do not
  start a club workflow, you do not push to `main` or `tools-out`. If you cannot push, send a zip with the same files.
- `NOTES-park-pages-part<N>.md` in the pull request: what is built; **what is NOT built** (say it first, not last);
  the accuracy table; the gate's last lines; every place you had to guess and what you guessed; every address you
  opened by hand to make a fixture; anything in this hand-off you found wrong.
- The club's last two reviews asked for the same three things, so check them before you send: the workflow file loads
  and has no key twice; every `gh` step has its token and no other step does; read-only everywhere but one last save
  job that runs none of your code.
- Honest numbers only. "36 of 60 within tolerance" was the most useful line in your last notes: write that kind of line.
