# kpc-gps.js — the "⬇ GPS" download (spec parts A + B) — notes for chat 3 / the outside coder

One small browser file, no libraries, no server. It builds GPX 1.1, KML 2.2 and GeoJSON **in the browser** from the data the
cards already load, and saves the file (iPhone: share sheet; others: normal download). Built without access to the KPC site
code or KPC-Data, so **the adapters below are guesses and must be wired up by whoever has the site code.**

Files: `kpc-gps.js` (the builder + button) · `demo.html` + `sample-data.js` (made-up parks US-9001..9003, stubbed `KPC`/`KPCB`;
open demo.html straight from disk) · `test/run_tests.js` (plain node, 159 checks) · `test/browser_check_390.js` (Chrome phone-width check).

## API
```js
KPCGPS.config({ siteUrl, builtDate, siteBase, dataUrl, outline, parkInfo, trails, fetch });   // once per page, all optional
KPCGPS.park(ref | {ref, area, name, lat, lon, outline, access, trails}, opts)
      .then(r => r.gpx / r.kml / r.geojson  (text),  r.files.gpx / .kml / .geojson  (file names))
KPCGPS.trip([ref | {ref, area} | {name, lat, lon}, ...], opts)      // stop order kept as a GPX <rte>; same return shape
KPCGPS.download(text, filename, mime)                               // Promise -> "shared" | "downloaded" | "cancelled"
KPCGPS.button(containerEl, {ref, area} | {stops: () => [...], area}) // the ⬇ GPS button + chooser, CSS injected once
```
opts: `area` ("US-KY"; needed to find data files unless `KPC.area` is set), `fers` (2-fer spots, default **false**),
`outlines` (trip only, default true), `trails` (default true), `pulloffs` (default false; YES-graded only — later, after chat 11),
`fileDate`. File names: `KPC_<ref>_<short-name>_<YYYY-MM-DD>.<ext>`, `KPC_trip_<date>.<ext>`.

## Adapters (ASSUMED — check against the real site)
| What | Default it tries | Override |
|---|---|---|
| Data files (KPC-Data first, then the site's copy) | `window.KPC.dataUrl(path)` → url or [urls], then `siteBase + path` | `config({dataUrl})` |
| Files read | `data/parkinfo/<area>.json`, `data/us-key/<area>.json`, `data/access/<area>.json` (KY falls back to `kpc-ky-data.json` `ap`), `data/fers/<area>.json` only when the box is ticked | — |
| Outline | `KPCB.gpsOutline / outline / get / geojson / feature / lookup (ref)`, then `KPCB[ref]` / `KPCB.parks[ref]`; return GeoJSON or `{status, agency, why, geojson}` (Promise ok) | `config({outline: (ref, park) => ...})` |
| Trails | `KPCB.trails(ref)` → `[{name, agency, geojson}]` | `config({trails})` |
| Park name/pin | `data/parkinfo` row `[name, website, type, access, access2, lat, lon, …]` | `config({parkInfo})` or pass `{ref,name,lat,lon}` |
| Site link in every file | `https://kentuckyportableclub.github.io/KPC-Links/` (ruled Oct 31 2026; `KPCGPS.SITE_URL`) | `config({siteUrl})` or `opts.siteUrl` |

The cheapest wiring is usually: pass what the card already has (`KPCGPS.button(el, {ref, area})`) and set
`config({outline: ref => <whatever kpc-bounds.js exposes>})`.

## Where to put the button (spec A) — one line each
Add `<script src="kpc-gps.js"></script>` once (after kpc-bounds.js), then on each card, after it renders:
- **Park Info card:** `KPCGPS.button(cardFooterEl, {ref: currentRef, area: currentArea})` — do this one first (order of work #1).
- **Kit card:** same call with the kit's park ref.
- **Am I in the Park card:** same call with the park it found.
- **Overlap Finder card:** `KPCGPS.button(el, {stops: () => [refA, refB], area})` (both parks; the user can tick 2-fers), or one button per park.
- **US / KY trip planner card:** `KPCGPS.button(el, {stops: () => planner.stops.map(s => s.ref ? {ref: s.ref, area: s.area} : {name: s.name, lat: s.lat, lon: s.lon})})`.

## Replacing the old GPX code (spec: "no copies in other scripts")
- **`finder.js` `gpx()`** (KY rove file): delete its XML string-building; call
  `KPCGPS.trip(roveRefs, {area: "US-KY"}).then(r => KPCGPS.download(r.gpx, r.files.gpx))`. Old file name/contents will change (now
  with notice, parking, outlines, `<rte>`); tell members.
- **Planners' trip GPX:** same, via `KPCGPS.trip(stops)`; or replace their GPX link with the button above.

## Tested / not tested
Tested here: 159 node checks (labels, symbols, ≤30-char unique names, notices, folders, closed outlines ≤2,000 points, 2-fers only
when ticked, no OSM/Google text), every GPX passes the GPX 1.1 XSD and every KML the OGC KML 2.2 XSD (xmllint);
`demo.html` in headless Chrome emulating a 390 px phone: no sideways scroll, downloads work, files validate.
**Not tested:** real iPhone Safari (share sheet), real Android Chrome, Garmin BaseCamp / units, phone map apps, Google Earth, and the
real KPC site/data. Run `XMLLINT=xmllint node test/run_tests.js` and `node test/browser_check_390.js` (Node 22+, google-chrome).

## Open questions (for Brandon / chat 3)
1. ~~Site URL~~ — ruled, see below. 2. The real `KPCB` function name and outline shape.
3. How `data/access` marks a point outside the park (reader accepts `outside/out/nearby` strings or flags, `inside:false`, `own:false`).
4. `data/fers` row shape (reader takes any row with two refs + lat/lon). 5. ~~Parking label with no agency~~ — ruled, see below. 6. 2-fer waypoints have no `<sym>` (none is in the
spec list); unknown access kinds use "Information". 7. KML icons are tinted default pins (no Google icon URLs); "dashed" approximate
lines are drawn as short yellow dashes (KML has no dash style). 8. Trails are open lines (closing them would draw a false segment).
9. The site's GeoJSON keeps full outline detail; GPX/KML are simplified. 10. The MIME type for KML is the standard
`application/vnd.google-earth.kml+xml` — it is only a type name, no Google data.

## Brandon's rulings (Oct 31 2026, 9:37 PM CT) — applied
1. Default site link in every file: `https://kentuckyportableclub.github.io/KPC-Links/` (override still works: `config({siteUrl})` / `opts.siteUrl`).
2. Pack name `KPC_US-KY_parks_YYYY-MM-DD.gpx` is OK.
3. Parking label: superseded by ruling 5 below.
4. GPS downloads page notice: placeholder only — the club pastes its own notice word for word (see `../GPS_NOTES_README.md`).
5. **(9:41 PM CT)** Parking label "Parking (from <agency>)" uses the access data's own agency only — the access row's `agency`, then the agency named once for the whole access file
   (assumed keys `agency`, `meta.agency` or `source.agency`). **Never the outline's agency.** If the access data names none:
   "Parking (from an official access list; check the agency’s map before you go)".
   On the site, an `accessAgency` on the park object (or the loaded access file) counts as the access file's agency.
