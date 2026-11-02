# KPC Map-Format Converter

`kpc_convert_layers.py` turns official map sources that are **not** ArcGIS REST layers
(WFS, OGC API Features, shapefile / GeoPackage / GeoJSON / KML / KMZ / GML downloads,
CKAN / Socrata / ArcGIS Hub dataset pages) into the same kind of thing the club's layer
collector already tests: a small GeoJSON of the polygon/line records near each park pin,
plus `converted/report.csv`.

It **decides nothing about matching**. The club's collector and a person decide.
It is **not wired into any workflow**. The club's bot chat does that after Fable's review.

## Install

```bash
python3.11 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt   # pyogrio wheels bundle GDAL; no apt packages needed
```

## Run

```bash
python kpc_convert_layers.py --leads leads.json                 # all leads
python kpc_convert_layers.py --leads leads.json --refs DE-0001,GB-0001
python kpc_convert_layers.py --leads leads.json --resume        # skip (ref,url) already in report.csv
python kpc_convert_layers.py --leads leads.json --resume --retry-errors
```

Other options: `--out converted` (output folder), `--cache .kpc_cache` (download cache, keep it
between runs, for example with actions/cache), `--max-minutes 50` (stop starting new URLs after
this, for the 55-minute GitHub job limit), `--max-types 15` (WFS feature types / OGC collections
queried when the lead names none), `--cache-days 7`, `--no-pota`, `--verbose`.
Environment: `KPC_CONTACT` (contact put in the User-Agent; **set this to the club's address or
repo URL**), `KPC_MIN_DELAY` (seconds between requests to one host, default 1), `KPC_MAX_MB`
(file size limit, default 500).

### Input

`leads.json` is either a list `[{ref, area, url, agency, status, note}]` or the club file with key
`other_layer` (`data/intake/leads-oct31.json`). Optional per lead:
- `name_field`: force the name field.
- `layer`: a WFS typeName or OGC collection id. You can also put `TYPENAMES=` in the URL.
- `lat` and `lon`: the park pin. Without them the pin is looked up once at
  `https://api.pota.app/park/<ref>` and cached in `<cache>/pins.json`.
- `kind`: force the kind (`wfs`, `ogcapi`, `file`, `ckan`, `hub`, `socrata`, `html`, `arcgis`).

### Output

- `converted/<area>/<ref>__<sha1(url)[:10]>.geojson`: the records within 2 km of the pin, in
  EPSG:4326, simplified to 3 m in a pin-centred metric projection (AEQD). Each feature's
  properties are `name`, `record_id`, `source_url`, `licence`, `read_date`, `layer`,
  `distance_m` and `ref`.
- `converted/report.csv` has the spec columns `ref, url, kind, n_records_near, name_field,
  licence, status, why`, plus `area, text_fields, output_file, pin_lat, pin_lon, nearest_m,
  searched_km, layers, hosts_used, read_date`.
  - `status` is one of: `OK` (≥1 record within 2 km), `EMPTY` (read fine, nothing within
    2 km; `why` gives the nearest distance), `TOO BIG` (over 500 MB, not downloaded), or `ERROR`
    (`why` says why).
  - `text_fields` lists every text field, so a person can pick a better name field.
  - The licence is copied from the WFS AccessConstraints/Fees, the OGC `rel=license` links,
    the CKAN licence, the Hub `licenseInfo`, the Socrata licence, or a licence/readme file
    inside a zip. If none is found it says `no licence found`.

The report is rewritten (atomically) after **every** URL, so a killed job loses at most one lead,
and `--resume` carries on from it.

## How each kind is handled

| Kind | Detected by | Fetch |
|---|---|---|
| WFS 2.0/1.1/1.0 | `service=WFS`, `/wfs`, `WFSServer`, or capabilities content | GetCapabilities (parsed with OWSLib, with a plain-XML fallback), then GetFeature with a BBOX of 5 km around the pin, widened to 25 km if empty. The BBOX is in the type's default CRS with the correct axis order. GeoJSON output is used if offered, otherwise GML. |
| OGC API Features | `/collections`, `/ogc/features` | `/collections/{id}/items?bbox=` 5 km, then 25 km |
| ArcGIS Hub page | `*.opendata.arcgis.com/datasets/…`, `/datasets/<owner>::<slug>` | Hub API `/api/v3/datasets` gives the service URL and licence, then an envelope query on the layer (`f=geojson`) |
| CKAN page | `/dataset/<slug>` | `package_show` API when robots.txt allows it, otherwise the resource links on the dataset page. Resources are tried in order WFS > OGC API > GPKG > GeoJSON > zip/shapefile > KML/KMZ > GML > ArcGIS REST, up to 4 |
| Socrata page | `/d/xxxx-xxxx` | `/api/views/{id}.json` (licence) and the GeoJSON export (**untested**, see limitations) |
| Direct file | file extension, else content sniffing (zip / SQLite / `<kml` / JSON magic bytes, Content-Disposition) | One download per URL, cached by URL. Revalidated with ETag / Last-Modified, or reused for `--cache-days` when the server gives neither. Files over 500 MB are refused from Content-Length, or stopped mid-stream. Zips are opened in place (`/vsizip/`, one nested zip level, `.gdb` folders). KMZs are read through their inner `.kml` because LIBKML on a `.kmz` loses SchemaData attributes. Every OGR layer is read with a 25 km bbox filter. |

All geometries are reprojected to EPSG:4326. Polygons and lines are kept; points are counted and
dropped, and invalid geometries are repaired with `make_valid`. If the coordinates come back
lat/lon-swapped relative to the pin, they are swapped back. ArcGIS-style KML exports that hide
attributes in an HTML table in `description` are unpacked into fields.

## Rules built in

- **Refused hosts** (checked on the lead URL, on every followed URL and on redirects):
  OpenStreetMap hosts, Geofabrik and Overpass; all Google hosts (`google.*`, `googleapis.com`,
  `googleusercontent.com`, `gstatic.com`, `goo.gl`); Protected Planet, UNEP-WCMC, and anything
  with `wdpa` in the host or path. A refused URL gets `ERROR` with the reason, and no request is made.
- **Official host only.** The tool fetches the lead's own host. Other hosts are used only when
  the official page itself names them: the CKAN resource list (for example data.gov.ie →
  npws.ie), the Hub dataset's service URL (for example the hub site → services.arcgis.com of the
  same organisation), or a link on a generic dataset page under the same registrable domain.
  Every host used is listed in `hosts_used` for review.
- **Polite.** The tool is single-threaded, so there is only ever one request at a time. Each host
  gets at least 1 s between requests. 429 and 5xx responses are retried with exponential back-off
  and `Retry-After`. The tool reads robots.txt per host and obeys it. The User-Agent is
  `KPC-MapFormatConverter/1.0 (KPC parks club official-map research; …; contact: $KPC_CONTACT)`.
- **Headless / CI.** No display and no system GDAL are needed. `--max-minutes` and the
  save-after-each-URL report let a 55-minute job chunk through ~2,250 leads over several runs
  with `--resume`.

## Running on GitHub Actions (sketch only, not committed anywhere)

```yaml
- uses: actions/setup-python@v5
  with: {python-version: "3.11"}
- uses: actions/cache@v4
  with: {path: ".kpc_cache", key: "kpc-cache-${{ github.run_id }}", restore-keys: "kpc-cache-"}
- run: pip install -r requirements.txt
- run: python kpc_convert_layers.py --leads data/intake/leads-oct31.json --resume --max-minutes 50
  env: {KPC_CONTACT: "<club contact>"}
# then commit/upload converted/ so the next job resumes from converted/report.csv
```

## Test files in this folder

- `leads.json`: the 10 spec test leads (3 WFS, 3 shapefile/GPKG, 2 KML/KMZ, 2 Hub/CKAN).
- `leads_extra.json`: extra coverage, one direct GeoPackage and one OGC API Features lead.
- `leads_refusal_test.json`: Protected Planet, Geofabrik (OSM) and Google URLs, all of which must be refused.
- `TEST_REPORT.md`: the results.
