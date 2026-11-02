# kpc_ca_sharpen (T8): Canada outline sharpener

Re-reads each coarse Canadian park outline from its **official** records at 3 m detail, never coarser than 5 m. Each saved outline is one shape that merges all of the park's records (R-G6). It is written only when every record answered. If any record fails, the park keeps its old outline and the tool says why.

| Source | How it is read |
|---|---|
| CPCAD and provincial or conservation-authority ArcGIS layers | `objectIds` query at `maxAllowableOffset` 0.00003. If refused, 0.00005, then stop. The record's name is always checked. A record saved with no number, or with a number that now holds another name, is found by name near the old outline. |
| BC local and regional parks | BC Data Catalogue WFS (`openmaps.gov.bc.ca`, `GBA_LOCAL_REG_GREENSPACES_SP`) by `PARK_NAME`, at full detail, simplified by 3 m |
| Québec heritage sites (QC-SPC, QC-IPC) | Données Québec GeoJSON downloads, full detail, simplified by 3 m |
| Québec ZEC, réserves fauniques and parcs régionaux | MRNF TRQ map service, a Données Québec resource, by `NOM_OFFICIEL` |
| Grand River CA (ON-GRCA) | GRCA open-data shapefile (`GRCA_Parks.zip`), full detail, simplified by 3 m |

**Cap rule (Brandon, Oct 31):** each piece stays at 3 m if it fits 1,500 points. Otherwise it steps to 6, 12, then 24 m and is labelled "simplified to about N m: a very big park". The uncapped copy goes to `OUT/work/full/<ref>.json.gz`, because 2-fers use full detail. `--cap-points N` changes the 1,500 (`--cap-points 0` turns the cap off).

**Twin records:** a record that cannot be read (for example, robots.txt says no) is allowed only when a record with the same core name on another official layer answered. This is noted in `why`. Otherwise the park is not done.

**Install:** Python 3.12, `pip install -r requirements.txt` (shapely, pyproj, numpy, pyshp; wheels only).

**Run**
```
python kpc_ca_sharpen.py --selftest                                    # no network, PASS / FAIL
python kpc_ca_sharpen.py --make-list --bounds data/canada-bounds --key data/ca-key --out OUT   # builds OUT/parks.json
python kpc_ca_sharpen.py --parks OUT/parks.json --out OUT --max-minutes 50 [--resume] [--limit N] [--areas QC,BC] [--cache DIR] [--cap-points 1500]
```

**Parks list:** `parks.json` holds one row per official record: `{ref, layer_url, record_id, current_detail_m, record_name, old_bbox, ...}`. `--make-list` selects the files with no `detail_m` (the 273) or with `detail_m > 5` (33 more).

**Exit codes:** 0 done, 3 time ran out (run again with `--resume`, which uses `OUT/state.json`), 2 bad input. A single bad park never fails the run.

**Output:** `OUT/canada/<ref>.json` holds:
- `ref`, `name` and `rings` (Esri order: outer ring clockwise, then its holes), plus a GeoJSON `geometry`;
- `detail_m`, `detail_label`, `points`, `pieces`, `acres` and `old_points`;
- `source_url`, `sources`, `read_date` and `why`.

`OUT/canada/index.json` holds the counts, every park written and every park not done with its reason.

**Politeness:** the same polite reader as the other KPC tools: robots.txt is obeyed (Données Québec's Crawl-delay of 10 s is honoured), at most 1 request every 2 s per host, the `KPC park tools ($KPC_CONTACT)` User-Agent, backoff on 429 and 503, a 403 accepted with no retry (host marked blocked with the reason), and a dated cache. No banned sources and no keys. It writes only inside `--out` and decides nothing.

## Club decisions applied (Oct 31)
- Always the one User-Agent `KPC park tools (<KPC_CONTACT>)`. This tool never had a second one; nothing to remove.
- At least 2 s between requests to one host. It was already 2 s; it is now a floor in the code (a smaller `gap` is raised to 2 s), checked by `--selftest`.
- **New:** a 403 is accepted with no retry. The host is marked blocked with the reason (`403 Forbidden on <url>`): the item's `why` says `BLOCKED: ...`, the host is not asked again this run (on a shared ArcGIS Online host only that one address), and the run prints a `blocked:` line per host. The live run had no 403s, so its results and acceptance numbers are unchanged.
- Owner names, zoning layers and the Spain WFS decisions do not apply to this tool.
