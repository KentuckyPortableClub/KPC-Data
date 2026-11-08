# Outline sources ledger

`ledger.json.gz`: one row per POTA park somebody already searched for an outline (who, when, what was found, what the system did
with it). Read it with `.github/scripts/kpc_outline_ledger.py` (`python3 .github/scripts/kpc_outline_ledger.py US-0150`, or
`--summary`). A new search should SKIP a park in the ledger unless its verdict is `nothing found` or `retry` and the row is old.
The nightly missing lists (`kpc_missing_lists.py`) add the ledger verdict to each listed park's `why`, so nobody looks for the same
park twice.

First source: the outside agent's two sheets (Nov 7 2026, 1500 US + 1488 Canada parks), reviewed Nov 7: every URL classified
(ArcGIS layer / bulk dataset / PDF map / junk), new layers read with `?f=json` (robots.txt honoured; services*.arcgis.com 403 = disallow).

`convert-list-nov7.csv`: everything that is real data but not a layer the key can page: the sheets' bulk datasets and robots-403
layers, the 55 approved non-layer sources (converter rows; `hold` column), the land-class and trail layers held for robots 403.

Trail parks (Nov 7 trail matcher, Brandon's hand run, reviewed): every one of the 243 trail parks with no outline has a `trail`
field in its ledger row: `trail line wired` (layer, name field, feature), `blocked host (robots)` (hosts) or `nothing found` (date).
`trail-lines-wired-nov7.csv` = the accepted lines; `trail-parks-todo-nov7.csv` = robots-blocked / nothing-found parks with hosts,
for hand download or the outside agent. Never bypass robots.txt.
