# KPC layers, Nov 7 2026 (outside agent's work, reviewed before it went in)

Brandon sent this Nov 7 ~7:39 PM CST ("Enter everything you got"). Grok Bot reviewed it first.

- `convert_layers.py` + `licences.csv`: turn the 55 approved non-layer sources (WFS, GeoJSON / GeoPackage / zip downloads, OGC API,
  the KPC-Data intake files) into polygon GeoJSON + `.meta.json` (EPSG:4326, `name` column). Manual workflow
  `.github/workflows/kpc-convert-sources-nov7.yml` (not the nightly kpc-convert-layers.yml, which is a different converter); the output is a run ARTIFACT for review, nothing is committed.
- `match_trails.py`: candidate matches between the 243 POTA trail parks with no outline (`inputs/kpc-pota-trail-parks-no-outline-nov7.csv`)
  and the 66 approved trail LINE layers (`inputs/kpc-trail-line-layers-nov7.csv`). `--plan` needs no network
  (`reports/match_plan.csv.gz` = 866 pairs for 195 of the 243 parks). Manual workflow `.github/workflows/kpc-match-trails-nov7.yml`, artifact only.
- `reports/conversion_plan.csv`: per row the steps, source CRS, licence (believed) and credit; last column `hold_for_check`.

## Changed in review (Nov 7)
- robots.txt: 200 = its rules, 404/410 = allowed, **401/403/5xx/unreachable = the host is refused** (was: a 403 robots.txt read as
  "no rules" = allowed). Club rule: a services*.arcgis.com robots 403 counts as a disallow. Same reading as `kpc_manners.py`.
- 60 s crawl delay for ArcGIS Hub / open-data portals (club rule); 2 s minimum elsewhere, or the host's Crawl-delay if longer.
- Blocked list matched case-insensitively, extended with the do-not-ingest items of `kpc_research_sources.py`, and checked again
  after every redirect (a redirect is a new request: blocked list + robots + delay again; at most 5).
- Licence holds: `licences.csv` `hold` column. RO, MX, VU, GE, TT, US-MS WMA, BG (no named licence) and rows 38 (SI evrd),
  50 (NL PDOK), 51 (BE am_patdat) (may not be protected-area layers) convert as `ok-held`, `hold_for_check: true`, `publish: false`.
  Every other row: licence believed (verified = no), may go in after the usual review.
- Workflows: inputs passed through env and checked (no shell injection), `permissions: contents: read`, artifact only, no schedule.

## Known limits (from the outside agent, still true)
Neither script has run against the real servers yet. Expect small fixes on the first run. Trail pairs on services*.arcgis.com
(338 of 866) and apps.fs.usda.gov (255) will come back refused: both answer robots.txt with 403.
