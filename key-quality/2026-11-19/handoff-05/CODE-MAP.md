# CODE MAP: what already exists in KPC-Data and must be reused, not rewritten

Checked against KPC-Data `main` on 19 Nov 2026. Line numbers drift: search by name.

## Fetching: `.github/scripts/kpc_manners.py` (the ONLY way out to the web)

```python
from kpc_manners import Manners, page_text, links_in, pdf_text, browser_text
M = Manners('KPC park page reader', state.get('hosts'))   # name for the User-Agent; resting hosts from the state file
st, headers, body, final_url = M.get(url)                 # st = int HTTP status, or a word (below)
st, headers, body, final_url = M.get(pdf_url, rng=(0, 399_999))   # range read: first 400,000 bytes
state['hosts'] = M.resting()                              # save before the run ends
```

- `st` words: `'rest'`, `'robots'`, `'robots-unreadable'`, `'deferred'`, `'crawl-delay'`, `'err:...'`. Use the module's
  own `next_run(st)` ("try again next run") and `robots_block(st)` ("the site says no") to sort them. Do not write your
  own list of words.
- `Manners(job, resting=None, gap=2.0, strikes_out=3, rest_s=86400, read_max=3_000_000)`: 2 s per host, three strikes
  = the host rests a day. Leave the defaults.
- The module asks `kpc_host_rules.py` before every request (never-contact hosts, every `services*.arcgis.com`, the
  saved-copy-only list such as `apps.fs.usda.gov`). You never call those hosts and never see a body from them.
- `page_text(html)` visible text; `links_in(html, base)` -> `[(absolute url, link text)]`; `pdf_text(body, pages=2)`;
  `browser_text(url, M)` -> text of a script-built page, `''` unless `BROWSER=1` and Playwright is installed;
  `write_needs()` leaves the "needs a person" list the house way.
- A picture (rule R-PR13) needs a small addition NEXT TO `browser_text` in this module (`browser_picture(url, M, ...)`,
  same checks in the same order: resting host, `robots_ok`, pace), not a second browser path in your script. Put that
  addition in its own commit so the reviewer can read it alone.

## Reading sizes and status words: `.github/scripts/kpc_truth_bot.py` ("park truth checker", 1,127 lines)

Has an `if __name__ == '__main__'` guard, so it can be imported. Reuse by import:

- `sizes_in(text, name, other_unit=False, is_pdf=False)`: every size with its sentence and why it is / is not a total
  (history, part of a sum, another unit named in the sentence, a lake's size, ...). `to_acres(n, unit)`.
- `core(name)`, `low(name)`, `name_rx(name)`, `other_unit_named(sentence, me)`, `NAMED_UNIT` (named units of many kinds).
- `HANDOVER`, `MANAGED`, `CLOSED`, `NEWNAME` (status and manager sentences).
- `SHARED` logic: a page three or more parks of an area call their own is an index page.
- `PDF_FIRST = 400_000`.

It keeps per-area module state (`DESIG`, `MULTI`, `OTHER_CORES`, ...). If importing a reader drags that state along
and you cannot call it cleanly, the right fix is to MOVE the pure readers into a small shared module in the same pull
request and have the truth checker import them back, with the truth checker's own tests still passing. Copying the
patterns into your file is the wrong fix: two readers drift apart.

Its stored output (`data/truth/<area>.json`, `parks[ref]`: `official` {acres, as, line, sent, url, why, clean},
`pages` [{url, status, why}], `sizes`, `verdict`, ...) is in `sample-data/truth-rows.json`. Where a truth row already
holds a size from the same page with the same fingerprint date, take it; do not ask the page again for it.

## Official hosts and map links: `.github/scripts/kpc_docs_bot.py` (1,256 lines)

- `GOVFAM` + `gov_of(host)`: hosts of the same government count as the agency's (tourism and asset hosts).
- `map_score(url, text, agency_host)`, `find_on_page(page, agency_host)`, `via_of(...)`: how a link is judged a map
  and how official it is. The reader's `maps` block uses these, it does not invent a second judgment.
- Its output `data/docs/<area>.json` (`parks[ref]`: `n`, `t`, `page`, `checked`, `map` {url, status, how}, `rules`).

## Cards made from stored files: `kpc_evidence_card.py` + `kpc_card_rules.py`

One card per park on the keeper's list, from stored files only. The reader is what was missing under it: the card has
no way to know what the park's own page says beyond a size. Do not build a second card. In `docs/park-pages.md` say in
five lines how a card would read `park-pages/facts/<area>.json` (the club wires it).

## The row every reader starts from: `data/parkinfo/<area>.json`

Written by KPC-Links `.github/scripts/kpc_state_links.py`:
`{state, updated, stateSite, parks: {ref: [name, website, type, activation, access, lat, lon, activations, attempts, qsos]}}`.
The stored copy only: never `api.pota.app`.

## Workflow pattern: `.github/workflows/kpc-trace-test.yml`

By hand only, never red: every step has an `id` and `continue-on-error: true`; the last step ("hidden failures") reads
`${{ toJSON(steps) }}` and `$RUNNER_TEMP/kpc-hidden.txt` and prints what failed while the job stayed green. Copy that
last step whole. Pushes go through `.github/scripts/kpc_push_retry.sh`. That file has ONE job with `contents: write`;
yours must be stricter (below).

## Review lessons (pull requests 124 and 125, your own; read them again)

1. A step with `continue-on-error` written twice makes the whole file invalid. Load the YAML in your test with a loader
   that refuses duplicate keys.
2. A `gh` step without `GH_TOKEN` fetches nothing and the run looks fine with an empty result. Every `gh` step gets
   the token; no other step does.
3. Read-only everywhere. One last `save` job holds `contents: write`, checks out `main` only and runs none of the
   branch's code. `persist-credentials: false` on every other checkout. No `actions: write` anywhere.
4. The reader's steps never hold a token of any kind.
5. Say in the notes what was not built and which checks were not run. "Wired but not run" is not "tested".
6. Give real counts ("36 of 60 within 2%"), not "matches".

## Tests and the gate

- Style: `tests/test_evidence_cards_nov17.py` (script, `PASS` / `FAIL` lines, ends `ALL PASS` / `SOME FAILED`, blocks the
  network with a socket guard).
- Gate: `tests/HANDOFF-GATE.md` ->
  `LINKS=<KPC-Links checkout> DATA=<KPC-Data checkout> python3 .github/scripts/kpc_full_suite.py --report tests.txt`
  must end `GATE PASS` (every failure is already a failure of `main`, listed in `tests/known-fail-main.txt`).
- Fixtures live under `tests/fixtures/park-pages/`, trimmed and small.

## Kits for outside agents (part 4)

The club's hand-off 04 is the shape: KPC-Data branch `tools-out`,
`key-quality/2026-11-19/handoff-04/` (`README.md`, `scripts/make_kits.py`, the two pass folders). The answer key sits
in `kit-keys/` there: do NOT open it, copy it or ship it; build your own key the same way and keep it out of every kit.

## Where output goes

Branch `tools-out` (orphan, squashable), folder `park-pages/`. Lists other tools drop: branch `intake-files`, folder
`park-pages/lists/`. Nothing of this on `main`. Nothing in KPC-Links at all.
