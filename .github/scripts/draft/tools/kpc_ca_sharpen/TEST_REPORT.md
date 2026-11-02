# kpc_ca_sharpen (T8): test report

Run on 2026-10-31 (America/Chicago), live against the official servers, Python 3.12 (`/tmp/v312`) and 3.13. The selftest is offline and prints **PASS**.

## Acceptance (measured live)

| Bar | Result | Pass? |
|---|---|---|
| ≥200 of the 273 (no `detail_m`) at ≤5 m | **214 of 273** at 3 m with the spec cap (1,500 points per piece). 272 of 273 without the cap (`--cap-points 0`). | PASS |
| CA-2242 back with its real shape | Old file: 12 points. New file: **1,484 points at 3 m**, 193,926 acres. The official area is 781.65 km² (≈193,148 ac), a 0.4% difference. Source: MRNF TRQ MapServer/11, read by `NOM_OFFICIEL`. | PASS |

Detail across the 273 (capped run): 3 m: 214, 6 m: 12, 12 m: 21, 24 m: 25, not done: 1.
The 33 extras (old `detail_m` > 5): 3 m: 3, 6 m: 14, 12 m: 11, 24 m: 5. None is coarser than its old detail.

Not done (keeps the old outline): **CA-3427 Douglas Park (BC)**. The BC greenspaces WFS has no "Douglas Park" near the saved outline (-123.356, 49.514). The nearest Douglas Parks are in Vancouver, Surrey and Langley. The key's record looks wrong.

Files: `live_run/index.json` (capped run), `live_run/index_nocap.json`, `live_run/run.log`, and `live_run/CA-2242.json`. The largest output file is 7.6 MB (uncapped 7.9 MB), under the 20 MB limit.

## Runs
1. First full run: 306 parks, about 2 h with an empty cache. It ended with 8 not done: 5 hit a GEOS TopologyException in `set_precision` and 3 were name mismatches.
2. Fixes:
   - `round6`: rounding piece by piece, with a pointwise fallback.
   - Name fields now include `TOPONYME`, `prop_nam` and the layer's `displayField`.
   - Ran again with `--resume`. 7 of the 8 were then written. CA-1299 Bannockburn (ABCA id 4) and CA-2023 Grande-Rivière (QC id 24) were read by their key ids with the name checked.
3. Uncapped comparison from the cache (`--cap-points 0`) into a separate out dir.

## Caveats and questions for Brandon
- **Cap per piece or per park?** The spec says "every piece at 3 m if it fits 1,500 points", and that is what the tool does. So CA-1474 Lac Seul Islands is 63,677 points at 3 m (many small pieces). If you meant per park, more parks would step down.
- **Cap vs the ≤5 m bar:** 58 of the 273 step to 6–24 m under the cap. Most are ZECs, réserves fauniques and large Ontario conservation reserves. Is a 1–3k-point ZEC "very big"? The full 3 m copy is always in `OUT/work/full/`.
- **Key groups records:** CA-0304 Mississagi PP and CA-0306 Mississagi River PP both list the same CPCAD/LIO records, Mississagi River waterway included. Both come out at about 250k acres. That comes from `ca-key`, not the tool.
- **Acreage flags:** 78 parks differ from the key's acres by more than 2×, and each `why` says "worth a look". Most are small BC parks where the key's acres were rough. Wood Buffalo is 11.27M ac, which matches the official 44,807 km² (the key says 2.26M).
- **Sources:**
  - Québec ZEC and réserves fauniques use the MRNF TRQ REST service, a Données Québec resource, not the FGDB download.
  - Some TRQ object ids are unstable (id 12 returned Laurentides), so those are read by name.
  - GRCA: the ArcGIS URL I first had was UK data, so I used GRCA's own `GRCA_Parks.zip`.
  - BC key ids are stale, so BC parks are matched by `PARK_NAME` near the old outline.
- **Twin rule:** nsgiwa.novascotia.ca's robots.txt disallows us. A park whose same-named record on another official layer answered, e.g. CA-0120 Sable Island and CA-1754, is written, and `why` says so.
- **Inputs I built:** `parks.json` (306 parks, 498 records) came from `data/canada-bounds` plus `data/ca-key` via `--make-list`. Politeness follows the spec (2 s per host, spec UA), not HOW_WE_WORK where they differ.

## Club decisions applied (Oct 31)
- Always the one User-Agent `KPC park tools (<KPC_CONTACT>)`. This tool never had a second one; nothing to remove.
- At least 2 s between requests to one host. It was already 2 s; it is now a floor in the code (a smaller `gap` is raised to 2 s), checked by `--selftest`.
- **New:** a 403 is accepted with no retry. The host is marked blocked with the reason (`403 Forbidden on <url>`): the item's `why` says `BLOCKED: ...`, the host is not asked again this run (on a shared ArcGIS Online host only that one address), and the run prints a `blocked:` line per host. The live run had no 403s, so its results and acceptance numbers are unchanged.
- Owner names, zoning layers and the Spain WFS decisions do not apply to this tool.
