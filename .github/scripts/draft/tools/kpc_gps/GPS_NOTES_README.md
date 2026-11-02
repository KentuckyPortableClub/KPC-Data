# GPS download — what was built, what is left (Oct 31 2026, for Brandon)

Built from `KPC_10_GPS_Download_Spec.md` + `KPC_Install_Contract.md` **without** the KPC site code or KPC-Data, on made-up
sample parks. Everything works and validates on that sample data; nothing has touched real KPC data, a real phone or a Garmin.

## Brandon's rulings (Oct 31 2026, 9:37 PM CT; parking updated 9:41 PM CT) — applied to kpc-gps.js and kpc_gpspacks
1. **Site link:** every file's description says `Site: https://kentuckyportableclub.github.io/KPC-Links/` by default
   (override: `KPCGPS.config({siteUrl})` on the site, `--site-url` or `KPC_SITE_URL` for the packs).
2. **Pack name OK:** `KPC_US-KY_parks_YYYY-MM-DD.gpx` (parts: `_part1of2` … when over 200 tracks).
3. **Parking label** (updated 9:41 PM CT): "Parking (from <agency>)" using the access data's own agency only — the access row's `agency`, then the agency named once for the whole access file
   (assumed keys `agency`, `meta.agency` or `source.agency`). **Never the outline's agency.** If the access data names none:
   "Parking (from an official access list; check the agency’s map before you go)".
4. **Page notice:** the GPS downloads page gets a placeholder; the club pastes its own notice word for word (below).

## GPS downloads page — placeholder (page on HOLD until Brandon's GO; members-only until then)
When the page is built, its top must hold the club's own full information notice, pasted word for word:
```
<!-- CLUB NOTICE GOES HERE: the club pastes its own full information notice, word for word. Do not write or edit it. -->
```
Then the pack list, read from `data/gps/index.json` (file, size, date, sources). Do not publish or add to the menu before Brandon's GO.

## Built
| Spec part | Folder | State |
|---|---|---|
| A. One-park "⬇ GPS" button + chooser, `KPCGPS.park/trip/download` | `kpc_gps_site/` | done, 159 node checks PASS, GPX/KML pass XSDs, 390 px Chrome-emulated check PASS |
| B. Trip download (`KPCGPS.trip`, stop order as `<rte>`, outlines optional) | `kpc_gps_site/` | done (same tests) |
| C. State packs bot (`data/gps/<area>.gpx.zip`, `.kml.zip`, `-trails.gpx.zip`) | `kpc_gpspacks/` | done, `--selftest` 71/71 PASS, xmllint PASS, same output as kpc-gps.js |
| GPS downloads page | — | **NOT built — on HOLD until Brandon's GO** (members-only until then; club's own notice at top — placeholder above). `data/gps/index.json` is ready for it to read. |
| Pull-off candidates in the files | both (`pulloffs` option, off) | waits for the pull-off rule sheet + chat 11 grades; only YES rows ever go in |

## Left for chat 3 (website / outside coder) — see `kpc_gps_site/README.md`
1. Wire the adapters to the real site: `KPC.dataUrl`, the real `KPCB` outline/trail function, `siteUrl`.
2. Add the button: Park Info first, then Kit, Am I in the Park, Overlap Finder, US/KY trip planner (one line each, in the README).
3. Replace `finder.js` `gpx()` and the planners' trip GPX with `KPCGPS.trip()` (no other GPX code left on the site).
4. Real-phone test: Android Chrome + iPhone Safari (share sheet). Note: if the share sheet refuses because the tap "expired"
   while data loaded, the code falls back to a normal download — needs checking on a real iPhone.
5. The GPS downloads page — only after Brandon's GO.

## Left for chat 10 (packs bot)
1. Run `kpc_gpspacks.py` on the real Kentucky files; read `report.md` (skipped rows + reasons) and check the zipped size (≤ 5 MB).
2. Confirm the guessed input shapes: access "outside the park" flag, where an access file names its agency once (`agency` / `meta.agency` / `source.agency`), `data/fers` rows, outline GeoJSON properties
   (`ref`, `agency`, `status`, `why`), trail GeoJSON (`ref`, `name`, `agency`).
3. Set up the nightly KPC-Data job (`--resume --changed-only`, exit 3 = run again) and the `gps-packs` side branch
   (rebuilt + squashed weekly) — not built, no KPC-Data access here.
4. Then the US, Canada (`CA.json`), the world (`data/pota/t/*.json`).

## Tests still owed before Brandon's GO (spec "Testing")
- Real devices: one park, one trip, Kentucky's pack into Garmin BaseCamp or a unit + one phone app (icons, closed outlines, names).
- Check 10 real parks' labels against their cards.
- Phone download on Android Chrome and iPhone Safari.
Done already: GPX 1.1 XSD (xmllint), KML (OGC 2.2 XSD, offline instead of an online validator), no OSM/Google text,
2-fers only when ticked and always with the 2-fer notice, 390 px no sideways scroll (Chrome emulation, not a real phone).

## Decisions I made that you may want to change
GPX split into `_partNofM` at 200 tracks (Garmin limit);
pack retries at 1,000/500/250 points per outline if over 5 MB; trails are open lines; 2-fer points have no symbol;
KML "dashed" approximate outline drawn as short yellow dashes. Full list: the two README files.
