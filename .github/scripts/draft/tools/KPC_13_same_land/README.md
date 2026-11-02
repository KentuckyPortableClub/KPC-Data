# KPC 13: "Same land, two park numbers" finder

Sometimes POTA gives two park numbers to what is really one piece of land. This tool looks at every pair of parks whose
outlines overlap, runs five simple tests, and lists the pairs that may be the same land as questions for the checker.
It is a helper: it never relabels a 2-fer and never edits a key, an outline or a 2-fer.

## Install
    python -m pip install -r requirements.txt      # Python 3.11 or newer

## Run
    python kpc_same_land.py --data club-data --areas US-KY,US-TN,CA-ON

`--data` is the folder holding the club files (`us-key/`, `ca-key/`, `ky-answer-key.json`, `canada-bounds/`,
`world-bounds/`, `fers/`, `parkinfo/`). World countries are run by their folder name in `world-bounds`, e.g. `--areas CH`.

| option | what it does |
|---|---|
| `--areas` | comma list (default: every key and every world-bounds country) |
| `--out` | report folder (default `sameland/`) |
| `--max-minutes 50` | stops cleanly before the time is up and exits 3 |
| `--resume` | carries on with a run that stopped with exit 3 (finished areas are kept) |
| `--cache .kpc-cache` | folder where everything read is kept, with the date it was read (records 7 days, POTA pins 30 days) |
| `--sources FILE` | extra or corrected layer addresses or agency fields (JSON) |
| `--offline` | reads only from the cache (for testing) |

Exit codes: **0** done, **3** not finished (run again with `--resume`), **2** bad input.

## The five tests (for each overlapping pair)
| test | passes when |
|---|---|
| S1 same record | both parks point to the same record(s) on the same layer (SAME RECORD); sharing only some = SHARES A RECORD |
| S2 shape | overlap is at least 95 % of the smaller park AND at least 80 % of the larger = SAME SHAPE. 95 % with 50-80 % = ONE INSIDE THE OTHER (listed apart). Under 50 % = SMALL ONE INSIDE. Otherwise PART OVERLAP |
| S3 name family | names with initials, accents and type words dropped score 85 or more (token-set), or one name sits inside the other |
| S4 pins | both POTA pins within 200 m |
| S5 agency | the managing agency read from each record (agency field, or the layer's agency) is the same |

Verdicts:
- **SAME LAND: likely** = S1, or SAME SHAPE with S3 or S4 and the same agency.
- **CHECK** = SAME SHAPE with a different (or unreadable) agency; S3 + S4 without SAME SHAPE; or the parks share some but not all records.
- **NOT SAME** = everything else.
- A pair where either outline is not graded "official", or an outline came from the saved simplified copy, never gets
  more than CHECK.

Outlines are built from the full live detail of the records the key names (never the saved simplified copy, unless the
live layer did not answer, and then the row says so). Trail and river-line parks and pin-only parks are left out.
For national forests in Kentucky the agency-owned land is used, not the proclamation line.

## Files it writes (all in `--out`)
- `<area>.json`: every overlapping pair with the five test results, the verdict, one plain sentence why, and any
  existing 2-fer rows for the pair. Also `club_same_land_rows`: how each row the club already calls "same land" came out.
- `questions.json`: the SAME LAND and CHECK pairs as questions (`answer` null). Answers already filled in are kept when
  the tool runs again.
- `summary.md`: counts per area and the top 10 candidates.

## Manners
At most one request per second per server, User-Agent `KPC-13-same-land (https://github.com/KentuckyPortableClub)`,
waits and retries on 429 / 5xx, obeys robots.txt for web pages, keeps a dated cache. Official agency layers only
(POTA's own park API is read only for pins); no API keys.

## Tests
    python -m pytest tests

Offline, made-up shapes and a pretend map server; no network. A checker answering in `questions.json` would write
e.g. `"answer": "YES", "checked_by": "K4TEST"`.
