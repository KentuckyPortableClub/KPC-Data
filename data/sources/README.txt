KPC workbook export – clean CSV pack
Made 2026-11-04 from no-boundary-parks_triaged.xlsx, dropped-parks_worked.xlsx and dropped-parks_worked_rest.xlsx.

All files: UTF-8, comma-separated, one header row, plain text, no formulas or formatting.
GIS source files use: country, region, place_or_agency, layer_name, url, format, license, has_boundaries, id_field, name_field, notes, last_checked
Park files use: ref, pota_name, country, region, pin_lat, pin_lon, official_name, official_layer, official_id, distance_km, reason, decision, decided_by, decided_date, notes

FILES (name, data rows, exact-duplicate rows removed)
  duplicates-rest.csv                     8 rows
  duplicates-top20.csv                   15 rows
  found-along-the-way.csv                17 rows
  inside-other-land.csv                3161 rows
  japan-source-plan.csv                   5 rows
  key-builder-fixes-rest.csv              7 rows
  key-builder-fixes-top20.csv             7 rows
  name-mismatch.csv                    1345 rows
  no-boundary.csv                     12594 rows
  override-no.csv                      1581 rows
  patterns-rest.csv                      77 rows
  patterns-top20.csv                    112 rows
  pota-bad-pin.csv                       65 rows
  pota-kind-map.csv                      21 rows
  proposed-new-layers.csv                85 rows
  rule18-doubt.csv                      278 rows
  sources-by-country.csv                207 rows
  to-download.csv                        51 rows
  wrong-kind.csv                          8 rows

Park rows in dropped files: 6438. Refs all match XX-NNNN or XX-NNNNN.

NOT SURE ABOUT / PLEASE CHECK
  - proposed-new-layers.csv: has_boundaries was set from the layer description words (polygon/shapefile = yes, points only/not found = no); blank where the page did not say. country/region parsed from labels like "GB (Scotland)" or "CA-QC"; multi-country rows (e.g. "HU / CO / FI / GR / CL") keep the label in region with country blank.
  - found-along-the-way.csv: these are leads (PDF maps, spec documents, news), not GIS layers; has_boundaries is "no" for picture-only maps and points-only layers.
  - sources-by-country.csv: these were general-knowledge suggestions with no URL; last_checked is blank because nothing was checked live. One row per theme per country.
  - no-boundary.csv: 15 rows share a ref with another row (parks that cross a state line, e.g. US-3424 in ID and MT); both kept and marked "conflict" in notes.
  - override-no.csv: decision is NO from overrides.json, which the handoff says holds only Brandon's decisions. decided_by and decided_date are left blank because the override text does not name a person or a full date; Brandon can fill them in.
  - All dropped and no-boundary files: decision is blank except for override rows. "PROPOSED" sheet answers are not signed, so they are in notes only. distance_km is blank on every row because the source lists carried no candidate distance.
  - Summary/COUNTIF tabs (Summary, Work order, Triage by country, GB/US/Canada triage summary) were not exported: they are formulas over the park files and can be recomputed from them. Prose tab "Start here" (actions, decisions, notes) is not a table and is not exported. "Bad-pin list" and "Decided" repeat rows already in pota-bad-pin.csv and override-no.csv, so they were skipped to avoid duplicate rows.
  - pota-kind-map.csv: what each POTA kind word means per country. Only rows with confidence "from source list" are used for a kind MATCH; "guess – confirm on KPC box" rows are never used. Part B will refill it from approved joins in world-key and the answer sheet. Its columns (country, pota_kind, layer_family, evidence, confidence) are its own, not the GIS or park layout.
  - Park files: notes now carry "REPORT TO POTA" on 23 same-name pairs (15 top-20, 8 rest); duplicates-*.csv has "same candidate site?" and "report to POTA" columns.

Rules kept: nothing invented; blank means unknown. decision is YES/NO/PIN only where an override existed. decided_by is blank everywhere because no row carries a named sign-off.
