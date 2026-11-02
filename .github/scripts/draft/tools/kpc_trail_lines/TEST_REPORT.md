# T7 kpc_trail_lines: test report (live run, 2026-10-31, America/Chicago)

## Round 4 (Oct 31, 23:07-23:19 CT): shared polite reader and the robots.txt rule

- The tool's own urllib reader was replaced by the shared `_common/polite.py` (source `_common/t7_src.py`, built by `_common/build.py`).
- `--selftest`: **PASS** on Python 3.11.18 and 3.13.5, here, in the KPC-Data mirror and from a fresh unzip. New checks: a 403 on robots.txt plus a 403 on the data request gives a block named by the data URL (2 calls); robots.txt answering 401/403/404/451 leaves the layer read and the host not blocked. Mutation check: letting a robots.txt 403 block the host makes the selftest FAIL.
- **Live re-run of all 31 trails** with an empty cache (the old cache format is not reused): `--trails trails_list.json --state-gis ../runs/state-gis.json --acceptance`. Exit 0, 31 of 31 done, 0 failed, 375 web requests, 11.6 min. robots.txt answered 403 on 5 ArcGIS Online hosts, each logged "no robots rules (RFC 9309); the data is still read"; nothing blocked.
- Every trail's states, km, water km, points and segment values in `index.json` are **identical** to the earlier run. AT Virginia acceptance: worst of the 40 checks = **1.169 m** (earlier 1.05 m; the 20 random points differ per run), PASS. `live_run/` now holds this run.
- The tables below are from the earlier run; they still hold.


**Self test:** `--selftest` prints PASS on Python 3.13.5 (box) and on Python 3.12.16 in a clean venv with the pinned requirements.txt.

**Live run:** all 31 national trails in `trails_list.json`.
- Command: `--trails trails_list.json --state-gis data/state-gis.json --acceptance`
- Result: 31 of 31 done, 0 failed, 375 web requests, 11.6 min.
- Output size: 25 MB in total, the biggest single file well under 20 MB.
- Saved files: `live_run/run.log`, `live_run/index.json` and `live_run/acceptance.json`.

## Acceptance

| Bar | Measured | Result |
|---|---|---|
| AT across Virginia within 3 m of the official line at 20 random points | worst of 40 checks (20 official→saved, 20 saved→official) = **1.05 m**. Official 169,353 pts / 873.5 km vs saved 31,758 pts / 866.6 km | met |
| Lewis & Clark water segments labelled `route_type: water` | every feature whose official `TRAIL_TYPE = "RIVER"` is `water` (30 state pieces, 7,257 km); `OVERLAND` → `land` (4 pieces) | met |
| Trail of Tears water segments labelled `route_type: water` | every feature with official `TRTYPE = "Water Trail"` is `water` (15 state pieces, 2,167 km of 8,181 km); the rest `land` | met |

Also checked in the selftest: every vertex of the source lies within 3 m of the saved piece (max 1.88 m on the fixture). Every row has source_url, read_date and why, and none says YES or NO.

## All trails (live)

| ref | trail | states | points | km | water km | segment status |
|---|---|---|---|---|---|---|
| US-3791 | Trail of Tears National Historic Trail | 10 | 32396 | 8180.7 | 2166.6 | NHTCERTSTATUS=Not Certified |
| US-4238 | Ice Age National Scenic Trail | 1 | 36559 | 1122.5 | 0.0 | not given |
| US-4239 | North Country National Scenic Trail | 8 | 155959 | 7318.4 | 0.0 | cert_doc=05_08_77 | trail_stat=NCT, cert_doc=05_08_77 | trai |
| US-4556 | Appalachian National Scenic Trail | 14 | 136258 | 3446.1 | 0.0 | Status=Official A.T. Route |
| US-4557 | Arizona National Scenic Trail | 2 | 49837 | 1336.0 | 0.0 | not given |
| US-4558 | Continental Divide National Scenic Trail | 5 | 149052 | 4883.0 | 0.0 | not given |
| US-4559 | Florida National Scenic Trail | 2 | 53036 | 2515.3 | 0.0 | Trail_Stat=<Null> | Open_Statu=Open, Trail_Stat=EXISITING |  |
| US-4560 | Natchez Trace National Scenic Trail | 3 | 8708 | 831.6 | 0.0 | TRLSTATUS=Existing |
| US-4561 | New England National Scenic Trail | 3 | 13489 | 375.8 | 0.0 | not given |
| US-4562 | Pacific Crest National Scenic Trail | 3 | 110996 | 3994.8 | 0.0 | not given |
| US-4563 | Pacific Northwest National Scenic Trail | 3 | 31415 | 1961.5 | 0.0 | not given |
| US-4564 | Potomac Heritage National Scenic Trail | 4 | 20321 | 1373.9 | 29.8 | TRSTATUS=Existing | NHTCERTSTATUS=Not Certified |
| US-4565 | Ala Kahakai National Historic Trail | 1 | 5901 | 667.1 | 0.0 | not given |
| US-4566 | California National Historic Trail | 10 | 61042 | 12810.5 | 0.0 | not given |
| US-4567 | Captain John Smith Chesapeake National Historic  | 6 | 14386 | 3260.0 | 3260.0 | not given |
| US-4568 | El Camino Real de los Tejas National Historic Tr | 2 | 5467 | 1053.5 | 0.0 | not given |
| US-4569 | El Camino Real de Tierra Adentro National Histor | 2 | 4694 | 4050.4 | 0.0 | not given |
| US-4570 | Iditarod National Historic Trail | 1 | 3577 | 1501.7 | 0.0 | not given |
| US-4571 | Juan Bautista de Anza National Historic Trail | 2 | 1293 | 2120.4 | 0.0 | NHTCERTSTA=Not Certified | NHTHIGHPOT=No |
| US-4572 | Lewis and Clark National Historic Trail | 16 | 47373 | 10139.9 | 7257.3 | not given |
| US-4573 | Mormon Pioneer National Historic Trail | 5 | 12038 | 2223.4 | 0.0 | not given |
| US-4574 | Nez Perce (Nee-Me-Poo) National Historic Trail | 4 | 21136 | 2031.1 | 0.0 | TRAIL_STATUS=DE - DECOMMISSIONED, TRAIL_STATUS=EX - EXISTING |
| US-4575 | Old Spanish National Historic Trail | 6 | 14599 | 4433.6 | 0.0 | not given |
| US-4576 | Oregon National Historic Trail | 7 | 17619 | 3634.6 | 0.0 | not given |
| US-4577 | Overmountain Victory National Historic Trail | 4 | 4719 | 520.7 | 0.0 | not given |
| US-4578 | Pony Express National Historic Trail | 8 | 16191 | 3236.7 | 0.0 | not given |
| US-4579 | Santa Fe National Historic Trail | 5 | 13466 | 3115.6 | 0.0 | not given |
| US-4580 | Selma to Montgomery National Historic Trail | 1 | 241 | 81.8 | 0.0 | not given |
| US-4581 | Star-Spangled Banner National Historic Trail | 3 | 5097 | 1034.6 | 0.0 | not given |
| US-4582 | Washington-Rochambeau Revolutionary Route Nation | 10 | 6985 | 1368.1 | 0.0 | not given |
| US-9757 | Butterfield Overland National Historic Trail | 7 | 27503 | 5076.3 | 0.0 | not given |

## Notes and caveats (questions for Brandon)

1. **State trail layers:** `data/state-gis.json` lists no state trail *line* layers today, so only the national layers were read. The tool supports `kind: trail` rows when they are added.
2. **Inputs I built:**
   - The spec's `--trails` input did not exist as a file, so I built `trails_list.json` (31 rows) from the KPC-Links `kpc_us_trails.json` list. Every source_url is the official ArcGIS service.
   - Some lines are hosted by the agency's trail partner and are the lines the agency links to, not NPS/USFS/BLM servers: North Country (North Country Trail Association), Ice Age (Ice Age Trail Alliance), Florida (Florida Trail Association, USFS partner) and Arizona (Arizona Trail Association). Please confirm these count as official.
3. **Captain John Smith (US-4567):** its layer has no land/water field, so the list marks the whole trail `water` (`default_route_type`). Is that right?
4. **Ala Kahakai (US-4565):** published as a polygon corridor, so it is saved as `shape: corridor`, not a line.
5. **Status fields vary:** some layers carry no certification or high-potential field, so `segment` says "not given" or shows the raw value. For example, Trail of Tears and Lewis & Clark only say `NHTCERTSTATUS=Not Certified` or nothing. The tool reports what the layer says and decides nothing.
6. **Rule conflict:** KPC_HOW_WE_WORK.md says 1 request/s and UA `KPC-<tool> (github URL)`. The handoff (authoritative) says 1 request per 2 s and `KPC park tools (KPC_CONTACT)`. I followed the handoff. With `KPC_CONTACT` unset, the UA falls back to the club GitHub URL.

## Club decisions applied (Oct 31)
- Always the one User-Agent `KPC park tools (<KPC_CONTACT>)`. This tool never had a second one; nothing to remove.
- At least 2 s between requests to one host. It was already 2 s; it is now a floor in the code (a smaller `gap` is raised to 2 s), checked by `--selftest`.
- **New:** a 403 is accepted with no retry. The host is marked blocked with the reason (`403 Forbidden on <url>`): the item's `why` says `BLOCKED: ...`, the host is not asked again this run (on a shared ArcGIS Online host only that one address), and the run prints a `blocked:` line per host. The live run had no 403s, so its results and acceptance numbers are unchanged.
- Owner names, zoning layers and the Spain WFS decisions do not apply to this tool.
