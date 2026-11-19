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

`worklist`, `report`, `person-page`, `intake`, `kits`, and `pc-kit` are later parts. Until those parts land, each of them prints one line and changes nothing.

## How to read the output

`facts/<area>.json` holds one object per park. The fields are the ones in the worked example for US-6063: the page, whose page it is, the name, the kind words, `inside_of`, sizes with their labels, location, maps, tracts, the manager, and `questions`. Every fact that can carry a sentence has a quote. A question is the reader saying a person should look, not an answer.

`run.json` records the day and how many requests the run made. `state.json` remembers resting hosts, refused hosts, and the fingerprint of each page, so a later run does not read the same page twice.
