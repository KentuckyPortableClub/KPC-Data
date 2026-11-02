# kpc_inspire (T6): European protected-area services, per country

The tool searches Europe's open-data catalogue (data.europa.eu) for each country's protected-area datasets. It also checks the country's national INSPIRE catalogue (CSW), if one is in its list. Each service link it finds is opened to confirm it works, and the layers it offers are listed. The INSPIRE Geoportal shut down on 1 Jul 2026, so the tool does not use it. The tool decides nothing.

Link kinds:
- `wfs`: a GetCapabilities request that lists feature types
- `ogcapi`: an OGC API service that lists `/collections`
- `arcgis`: an ArcGIS REST service that lists layers through `?f=json`
- `download`: a file that starts to download, read with a Range request

WMS links are not opened, because they serve pictures, not shapes.

Records from the EEA catalogue, or from an EU body, about Natura 2000 or CDDA go in a separate `"EU"` list with `eu_compilation: true`. That keeps the Europe-wide compilations apart from each country's own file.

```
pip install -r requirements.txt          # Python 3.12
export KPC_CONTACT="K4TEST <k4test@example.org>"
python kpc_inspire.py --areas AT,DE,ES --out out/ --cache cache/
python kpc_inspire.py --selftest         # no network, prints PASS or FAIL
```

Output in `--out`:
- `inspire.json`: `{cc:[{title,publisher,licence,date,links:[{url,kind,opens,layers,why,status?}],source_url,read_date,why,catalogue}], "EU":[… eu_compilation:true]}`. Within each country, records with a WFS that opens come first.
- `report.json`: per-country counts and notes, request counts, hosts that were rested, and `blocked_hosts` (host → `403 Forbidden on <url>`)
- `state.json`, for `--resume`

Flags:
- `--areas` (31 country codes are built in) or `--in codes.txt`
- `--max-minutes 50`, `--resume`, `--limit N`
- `--max-links 60` (links opened per country) and `--max-records 80`

Exit codes: 0 done, 3 time out, 2 bad input. One bad record or a dead host never stops the run.

How it reads data.europa.eu: robots.txt blocks the GET search pages, so the tool sends POST requests to the public `/sparql` endpoint instead. Manners are the same as the other KPC tools: robots.txt, at least 2 s per host, always the one `KPC park tools (<KPC_CONTACT>)` UA, and on 429/503 it retries 3 times, then rests the host. A 403 on a data request is accepted with no retry: the host is marked blocked, and each of its links stays in the list with `opens: false`, `status: "blocked from here"` and `why: "blocked from here (403): 403 Forbidden on <url>"`. No keys are used.

## Club decisions applied (Oct 31)
- Removed the retry with a crawler-style User-Agent. Only `KPC park tools (<KPC_CONTACT>)` is sent.
- A 403 on data is accepted: no retry, host marked blocked, links kept with `status: "blocked from here"`. A 4xx on robots.txt alone = no robots rules, keep reading (RFC 9309; club decision Oct 31).
- At least 2 s between requests to one host.
- Spain's national WFS (`geoserver.iepnb.es`) stays in the list as "blocked from here (403)", so the club can try it from GitHub.

## Shared source (`_common`)

The polite web reader (User-Agent, 2 s per host, robots.txt, 403 handling, cache) is one shared file, `_common/polite.py`, built into this tool from `_common/t6_src.py` by `_common/build.py`. The zip carries `_common/`. Edit the source there, never the built `kpc_inspire.py`, then run `python3 _common/build.py` (or `--check` to only compare) and this tool's `--selftest`.
