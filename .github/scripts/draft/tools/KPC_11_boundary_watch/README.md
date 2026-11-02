# KPC 11: Boundary Change Watcher

Once a week this tool reads every park's outline from the agency's own live map layer and compares it with last
week's. It tells the club which parks GREW, SHRANK, MOVED, lost their record, were renamed, or whose layer moved,
so a person can look before a ham is sent to the wrong place. It is a helper: it never edits a key, an outline or a 2-fer.

## Install
    python -m pip install -r requirements.txt      # Python 3.11 or newer

## Run
    python kpc_boundary_watch.py --data club-data --areas US-KY,US-TN,CA-ON

`--data` is the folder holding the club files (`us-key/`, `ca-key/`, `ky-answer-key.json`, `fers/`, `canada-bounds/`).
The first run only builds fingerprints (every park says FIRST LOOK). From the second run on, changes are reported.

| option | what it does |
|---|---|
| `--areas` | comma list, e.g. `US-KY,US-TN,CA-ON` (default: every key found) |
| `--out` | report folder (default `watch/`) |
| `--state` | fingerprint file (default `watch/state.json`) |
| `--max-minutes 50` | stops cleanly before the time is up and exits 3 |
| `--resume` | carries on with a run that stopped with exit 3 |
| `--cache .kpc-cache` | folder where everything read is kept, with the date it was read |
| `--sources FILE` | extra or corrected layer addresses (JSON, same shape as the tool's built-in list) |
| `--offline` | reads only from the cache (for testing) |
| `--no-outlines` | does not keep last run's live outlines (see "Files") |

Exit codes: **0** done, **3** not finished (run again with `--resume`), **2** bad input (a missing folder, an unknown area,
or an output folder inside the club's live files).

## What it says about each park
| verdict | meaning |
|---|---|
| SAME | outline matches last run (or the layer was not edited since last run, so nothing was downloaded) |
| GREW / SHRANK | area changed by more than 2 % or more than 5 acres (lines: 2 % or 0.5 km) |
| MOVED | about the same size but the outline's box shifted more than 50 m |
| RECORD GONE | a record the key names is no longer on the layer |
| RENAMED | the record's name on the layer changed |
| LAYER MOVED | the layer's address answers "not found"; the tool lists look-alike services on the same server as leads |
| SOURCE DOWN | the server did not answer; tried again next run, no change is assumed |
| CAN'T TELL | the park could not be checked (no layer address, or the name in the Kentucky key is not on the layer) |
| FIRST LOOK | first time this park was seen: fingerprint saved |

For every changed park the report also gives the old and new acres, how much of the old outline is still inside the
new one (10 m slack), and the 2-fer rows that use the park (live or not).

## How it saves time
For each layer it first reads the layer's own page (last-edit date) and a record count. If both are the same as last
run, the layer is UNCHANGED and its parks are not downloaded. Many state MapServer layers do not publish a last-edit
date; then the tool looks for an edit-date field, and failing that it reads every record (small, simplified to 3 m).

## Files it writes (all in `--out`)
- `state.json`: numbers only (acres to 0.1 %, box to about 10 m, point count). No shapes.
- `changes-<date>.json`: only the parks that changed, plus the ones that could not be checked.
- `summary.md`: a short table and plain sentences.
- `outlines/<area>/<ref>.geojson.gz`: last run's live outline, used next week for "how much of the old outline is still
  inside". These are working copies (big): keep them on a throwaway branch or in the Actions cache, not in the data repo.
  Turn off with `--no-outlines` (then only the club's saved `canada-bounds` outlines are used for that figure).
- `.run/`: work in progress for `--resume`; safe to delete after a finished run.

## Manners
At most one request per second per server, User-Agent `KPC-11-boundary-watch (https://github.com/KentuckyPortableClub)`,
waits and retries on 429 / 5xx, obeys robots.txt for web pages, keeps a dated cache. Official agency layers only; no API keys.

## Where the layer addresses come from
- `us-key/layers.json` (the club's own list) for the state layers.
- Built in: PAD-US (integer ids in the US keys), CPCAD (integer ids in the Canadian keys), the three Land Information
  Ontario layers, and the Kentucky key's layer codes (bwma, bstate, bsnp, bsna, bwild, bnps, bfws, bpad, bwilder,
  bdbnf, bdbnfo, trl). The Kentucky key names records instead of giving ids, so the tool finds each record by name once
  and remembers the record number in `state.json` ("resolved").
- Anything missing or wrong can be added with `--sources my-sources.json`, e.g.
  `{"ON-TRCA Toro": {"url": "https://.../MapServer/0", "name_field": "NAME"}}`.

## Tests
    python -m pytest tests

Offline, made-up shapes and a pretend map server; no network.
