# kpc_acres - official park sizes for the Kentucky Portable Club

Reads the acres research file, downloads each official agency list it names, matches list rows to
POTA parks with three strict rules, and writes official sizes with the source of each one. **The tool
never decides anything.** Its output is a set of candidates for the waiting room (kind `acres`).
Python 3.12, one file, standard library only (`pypdf==5.1.0` is optional and only used for PDF lists).

    export KPC_CONTACT="you@example.org"        # goes into the User-Agent
    python3 kpc_acres.py --selftest             # offline, prints PASS or FAIL
    python3 kpc_acres.py --in acres-us-ca-oct31.json --parkinfo parkinfo/ --keys keys/ \
        --out acres/ --max-minutes 50 [--areas US-KY,CA-ON] [--limit N] [--resume] [--cache DIR] \
        [--answer-key ky-answer-key.json] [--offline] [--no-county-check]

Exit codes: 0 done, 3 time ran out (run again with `--resume`). One bad item is logged, never fatal.
Writes only inside `--out`: `acres.json`, `acres-list.json`, `unmatched.csv`, `report.md`, `work/`.

**Matching:** (a) the park number (US-1234) is in the row, or the row's record id is the one the key
joined to the park; (b) same name + same kind in the same state or province (generic words dropped;
a WMA never matches a state park); (c) for name+kind, any county or point in the list must agree with
the pin (same county via Census TIGERweb, or within 25 km). Otherwise the row goes to `unmatched.csv`
with the reason. Rows are added together (`parts`) only when every one matched the same park.
Flags: under 0.1 ac, over 20 million ac, over 50x the key outline, one row matched to two parks,
another official list differs by more than 10%.

**Research file fields read** (any of these names; case, spaces and `_` ignored). The file may be a
list of rows, `{"agencies": [...]}`, or a dict of `{agency name: row}`.
- agency: `agency agency_name owner organization org department publisher source_agency managing_agency manager`
- state/province: `area area_code state province prov st region jurisdiction code state_code program pota_area` (+ `country nation cc`)
- list link: `list_url download_url data_url download dataset_url api api_url endpoint layer_url service_url rest_url file_url csv_url xlsx_url pdf_url table_url list url link href`
- page: `page page_url list_page source_page home homepage info_url web_page source_url source`
- format (or a kind word): `format file_format file_type source_type list_type kind type how method access`
- size column: `size_column size_col size_field acres_column acres_col acres_field area_column area_field acreage_column size_header column field`
- unit: `unit units size_unit area_unit unit_given uom`; name/id/county/lat/lon/state column: `name_column id_column county_column lat_column lon_column state_column` (and `_col`/`_field` forms)
- status: `status result found list_status finding outcome` ("no list" / "page only" are skipped and reported)
- kind of place: `park_kind place_kind default_kind kind_of_place designation park_type list_kind`
- hand-copied sizes (top level or inside a row): `hand hand_sizes hand_copies manual manual_sizes sizes acres_not_downloadable not_downloadable copied hand_rows`; each row uses `park/name/site/...`, `acres/size/value/hectares/km2/sq_mi`, `unit`, `ref`, `page`.

List formats: CSV, XLSX, HTML tables, ArcGIS REST layers (paged), Socrata, CKAN, JSON/GeoJSON, PDF (optional).
Banned hosts (OSM, Google except storage.googleapis.com, WDPA/Protected Planet, AllTrails, Gaia, Strava,
TripAdvisor, Yelp, Wikipedia) are refused. robots.txt is obeyed, 2 s between calls to a host, 429/503 back off
3 times then the host rests. Sign-in or token pages are reported as "needs sign-in" and skipped.
