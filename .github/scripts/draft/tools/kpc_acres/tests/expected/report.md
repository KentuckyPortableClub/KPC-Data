# kpc_acres report (2026-10-31)

- tool version 1.0.0; areas: US-KY,US-TN,CA-ON
- work items: 11 done of 11 - complete
- parks with an official size: 14; flagged: 5; unmatched rows: 7
- web requests this run: 18

## One line per agency

- US-KY | Blocked agency | failed: blocked by robots.txt | rows read 0, matched 0, unmatched 0, flagged 0 | https://blocked.ky.example/secret/list.csv
- US-KY | KDFWR | read OK (html) | rows read 6, matched 5, unmatched 1, flagged 3 | https://fw.ky.example/wma-list.html
- US-KY | KDFWR | read OK (arcgis) | rows read 3, matched 2, unmatched 1, flagged 0 | https://gis.ky.example/arcgis/rest/services/KDFWR/Lands/MapServer/0
- US-KY | KY open data | read OK (socrata) | rows read 4, matched 0, unmatched 4, flagged 0 | https://data.ky.example/resource/abcd-1234.json
- US-KY | Kentucky State Parks | read OK (csv) | rows read 1, matched 1, unmatched 0, flagged 0 | https://parks.ky.example/acreage.csv
- US-KY | Mystery list | read OK (json) | rows read 1, matched 0, unmatched 1, flagged 0 | https://misc.ky.example/list.json
- US-KY | Page-only agency | skipped: page only, no list to read (research says so) | rows read 0, matched 0, unmatched 0, flagged 0 | https://pageonly.ky.example/
- US-KY | KY Office of Nature Preserves (hand copy) | read OK (hand sizes) | rows read 2, matched 2, unmatched 0, flagged 1 | https://eec.ky.example/preserves/bad-branch
- US-TN | TN no-list agency | skipped: no list (research says so) | rows read 0, matched 0, unmatched 0, flagged 0
- US-TN | Tennessee State Parks | read OK (xlsx) | rows read 2, matched 2, unmatched 0, flagged 0 | https://tn.example/park-sizes.xlsx
- CA-ON | Ontario Parks | read OK (ckan) | rows read 2, matched 2, unmatched 0, flagged 1 | https://data.on.example/api/3/action/datastore_search?resource_id=abc

## Checks

- WMA matched to a state park (must be 0): 0
- flags: over 20 million acres: 1; over 50x the current outline: 1; same row matched to two parks: 2; under 0.1 acres: 1
- answer key: 3 matched parks have a hand-checked size; 2 agree within 10% (66.7%; pass mark 95%)
  - US-1006 Yellowbank WMA: list 247 ac vs key 300 ac (KDFWR, name+kind)

These sizes are candidates for the waiting room (kind `acres`); the club's rules and chat 11 decide.
