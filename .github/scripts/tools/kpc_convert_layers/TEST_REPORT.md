# TEST REPORT: KPC Map-Format Converter

The test was run on Saturday, Oct 31, 2026, at about 3:55–4:02 PM CDT, on the shared Linux box
with Python 3.13.5, pyogrio 0.13.0 (bundled GDAL 3.12.4), shapely 2.2.0, pyproj 3.8.0 and OWSLib 0.36.0.
The command was `python kpc_convert_layers.py --leads leads.json`, from a clean `converted/`
folder. Some files came from the download cache of earlier runs the same afternoon. A cold
run of all 10 leads took about 85 s.

The club's real `data/intake/leads-oct31.json` was **not available**. `leads.json` holds 10 test
leads built from real official sources found on the web. The pins are the POTA coordinates for
each ref, fetched from api.pota.app.

## Result: 9 OK, 0 EMPTY, 0 TOO BIG, 1 ERROR

| # | Ref | Type | Source (agency) | Status | Records ≤2 km | Name field | Licence found | Why / notes |
|---|---|---|---|---|---|---|---|---|
| 1 | DE-0001 Berchtesgaden NP | WFS 2.0.0 | BfN `geodienste.bfn.de/ogc/wfs/schutzgebiet`, type `Nationalparke` | **OK** | 1 (Berchtesgaden, contains pin) | NAME | yes: "Nicht für Planungszwecke geeignet…" + GeoNutzV terms | Found in the 5 km bbox, native CRS |
| 2 | DK-0001 Skagen Gren | WFS 2.0.0 | Danmarks Miljøportal GeoServer, `dai:fredede_omr` | **OK** | 2 (Skagen Gren contains pin; Sønderstrand at 1.5 km) | Fred_navn | **no licence found** (caps say AccessConstraints NONE / Fees NONE) | The name heuristic correctly skipped `Temanavn` (the same theme label on every record) |
| 3 | FI-0003 Oulanka NP | WFS 2.0.0 | SYKE INSPIRE PS, `PS.ProtectedSitesValtionOmistamaLuonnonsuojelualue` | **OK** | 1 (Oulangan kansallispuisto, contains pin) | nimi | weak: caps only say "Lisenssi / Maksuton" (licence / free of charge) | EPSG:3067 reprojected |
| 4 | RO-0001 Avenul Betfia | GeoPackage | data.gov.ro, Ministerul Mediului `AriiNaturaleProtejate.gpkg` | **ERROR** | 0 | – | – | `SSLError … UNEXPECTED_EOF_WHILE_READING`. The TLS handshake to data.gov.ro fails from this box with both Python and curl, on every retry across 4 runs. The dataset page loads fine from another network, so this is a host/network problem, not a tool bug. It may work on GitHub runners. It will be retried with `--resume --retry-errors`. |
| 5 | CH-0010 Gantrisch Nature Park | Shapefile zip (LV95, EPSG:2056) | BAFU on data.geo.admin.ch | **OK** | 2 (Naturpark Gantrisch, park + perimeter layers, both contain pin) | Name | **no licence found** (zip holds no licence file) | ETag/Last-Modified cache revalidation worked |
| 6 | MX-0040 Cañón del Sumidero | Shapefile zip | CONANP `sig.conanp.gob.mx` | **OK** | 1 (Cañón del Sumidero, contains pin) | NOMBRE | **no licence found** | The server sends no ETag/Last-Modified, so the cached copy is reused for 7 days |
| 7 | US-1134 Calaveras Big Trees SP | KML (served as zip → `.kmz` → `.kml`, no file extension in URL) | California State Parks, `csparks.maps.arcgis.com/.../data` (the "ParkBoundaries.kml" link on parks.ca.gov) | **OK** | 1 (Calaveras Big Trees SP, contains pin) | UNITNAME | **no licence found** (the CC-BY licence is on the data.ca.gov page, not in the file) | Kind found by sniffing the content. The Esri KML hides its attributes in an HTML `description` table, which the tool unpacks. |
| 8 | MX-0007 Desierto de los Leones | KMZ | CONANP `.../kml/232-ANP_ITRF08_19162026.kmz` | **OK** | 1 (Desierto de los Leones, contains pin) | NOMBRE | **no licence found** | The KMZ is read through its inner `doc.kml`, because LIBKML drops the SchemaData fields |
| 9 | GB-0001 Cassop Vale NNR | ArcGIS Hub page | Natural England Open Data Geoportal `Defra::national-nature-reserves-england` | **OK** | 1 (CASSOP, 1,267 m from pin) | NAME | yes: Open Government Licence v3 (Hub licenseInfo) | Hub API → `services.arcgis.com/JJzESW51TqeY9uat/…/FeatureServer/0`, envelope query. The pin is outside the polygon, and the collector or a person decides whether it matches. |
| 10 | IE-0001 Killarney NP | CKAN page | data.gov.ie `killarney-national-park-boundary-map` (NPWS) | **OK** | 1 (Killarney National Park, contains pin) | SITE_NAME | yes: data.gov.ie Open Data Licence + CC BY 4.0 | robots.txt disallows `/api/` on data.gov.ie, so the tool read the dataset page's resource list instead. The listed WFS (`dservices-eu1.arcgis.com`) is also disallowed by that host's robots.txt, so it was skipped. The tool used the NPWS shapefile zip on `www.npws.ie` (30 KB) instead. |

Every output geometry was checked afterwards. Each one sits at the pin: 9 of 11 polygons contain
the pin, and the other two are 1.3 km and 1.5 km away. None came out swapped or mis-projected.
Simplification to 3 m kept the outputs small (21 to 3,707 vertices).

## Extra checks (not among the 10)

| Check | Result |
|---|---|
| Direct GeoPackage: SI-0001 Triglav, podatki.gov.si `evrd.gpkg` (48 MB) | OK. 4 records ≤2 km (e.g. "Julijske Alpe - Triglavski narodni park"), name field IME |
| OGC API Features: GB-0001, `environment.data.gov.uk/.../ogc/features/v1/collections` | OK. 1 record (CASSOP, 1,267 m). Licence: **no licence found**, because the service has no rel=license link (the Hub route found OGL) |
| Refused hosts (`leads_refusal_test.json`): protectedplanet.net WDPA page, download.geofabrik.de OSM shapefile, google.com My Maps KML | All 3 got ERROR "refused host …" with **no request sent** |
| TOO BIG: `KPC_MAX_MB=1` on the 5.8 MB CONANP zip | TOO BIG "file is 6 MB (limit 1 MB); not downloaded". The decision comes from Content-Length before the download, and a streaming cut-off also exists for servers that send none. |
| `--refs DE-0001,GB-0001` | Ran only those 2 |
| `--resume` after a full run | "10 leads, 0 to do" |
| `--resume --retry-errors` | Re-ran only the ERROR rows (RO-0001, plus US-1134 before its fix) |
| Report saved after every URL | Yes (atomic rewrite of `converted/report.csv`) |

## Bugs found and fixed while testing

1. Reading a `.kmz` directly through LIBKML lost all attributes (CONANP). It is now read through the inner `.kml`.
2. A zip holding a `.kmz` (California) needed GDAL's brace syntax for nested `/vsizip/`.
3. The California KML has `Name = "NULL"` and keeps its attributes in a description HTML table. Null-like values are now ignored, and the table is unpacked.
4. In the Danish layer, the name guess picked `Temanavn`, which is the same value on every record. Constant-valued fields are now penalised, and the guess picked `Fred_navn`.
5. KML record IDs fell back to the internal feature id because the empty KML `id` field matched first. The ID field is now chosen only from fields that have values.

## Known limitations

- **Not tested at all:** Socrata pages, GML file downloads, WFS 1.0/1.1-only servers, OGC API
  paging (only the first 1,000 items per collection, which is fine inside a 25 km box), and `.gdb`
  inside zips. The code paths exist but have not run against a real server.
- **Feature caps:** a WFS query is capped at 2,000 features per type and per bbox. When the cap
  is hit, the `why` column says so. When a lead names no type, only the first 15 types are queried
  (`--max-types`).
- **Big files:** a file is downloaded whole, up to 500 MB, even though only the 25 km around the
  pin is read. Several leads on the same URL share one cached copy.
- **robots.txt is obeyed strictly.** Some official hosts (data.gov.ie `/api/`, ArcGIS
  `dservices*` WFS) disallow bots, so the tool falls back to other listed resources or reports ERROR.
- **Licence:** the licence is copied, not judged. Plain files rarely carry one, so 6 of the 10
  leads say "no licence found". A person should take the licence from the agency's dataset page.
  In WFS capabilities, "NONE" is treated as no licence.
- **Name field:** the tool guesses the name field from a list of common names plus a heuristic.
  Always check `text_fields`, and use `name_field` in the lead to override the guess.
- **Pins:** pins come from the lead's `lat`/`lon`, or from api.pota.app. A wrong pin gives
  EMPTY or the wrong record.
- **Python version:** written for Python 3.11+, but only run on 3.13 here. It has not been run
  on an actual GitHub Actions runner.
- **data.gov.ro** could not be reached from this box (TLS failure).
