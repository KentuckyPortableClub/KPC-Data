# kpc_acres - test report (2026-10-31)

## What was tested and passed
- `python3 kpc_acres.py --selftest`: **PASS**, fully offline. Checked under Python 3.13 and Python 3.12,
  without pypdf ("PDF file test skipped, line parser tested") and with pypdf 5.1.0 ("PDF file read with pypdf").
- The selftest runs the whole tool on synthetic fixtures (`tests/fixtures`, built by `tests/make_fixtures.py`)
  through an injected fake network, then compares the four outputs with `tests/expected/`. It covers:
  - unit conversions: ha x 2.47105, km² x 247.105, sq mi x 640, m² x 0.000247105; units in the size text, the column header, the research row
  - CSV (title row, Total row skipped), HTML table (menu table ignored), ArcGIS JSON with paging, Socrata, CKAN (Ontario, km²), XLSX (stdlib reader), JSON features, PDF lines
  - match by park number, by key record id, by name + kind; a WMA never matches a state park ("Taylor Lake WMA" vs Taylor Lake State Park goes to unmatched)
  - two WMA tracts added together with `parts: 2`; a row naming two parks gets both plus the flag
  - rule c: county agrees (fake TIGERweb answer), county disagrees -> unmatched, point over 25 km -> unmatched
  - flags: under 0.1 ac, over 20 million ac, over 50x the key outline, same row matched to two parks
  - unmatched.csv reasons: ambiguous (two parks fit), no park, unknown unit, different kind, kind unknown
  - research reader: list of rows, `{"agencies": ...}` and dict-of-dicts shapes, varied field names, hand-copy lists, "no list"/"page only" rows
  - robots.txt obeyed, User-Agent from KPC_CONTACT, 2 s gap per host, banned hosts refused, sign-in/token answers skipped, 429/503 backoff
  - `--max-minutes` exit 3 with a PARTIAL report, `--resume` gives the same result, `--limit`, nothing written outside `--out`
  - US parks listed before Canadian ones (kpc_order.rank)
  - answer-key agreement line in report.md (synthetic: 3 parks, 2 agree)
- A live smoke run against Kentucky (not part of the spec criteria; my own 4-row research file
  `tests/ky-live-smoke-research.json`, four official kygisserver.ky.gov ArcGIS layers: KDFWR hunting areas,
  nature preserves, state forests, state parks; real KY POTA pins; the real `ky-answer-key.json` found on the box):
  4 of 4 agencies read OK in about 10 s, 290 rows read, 131 parks got a size, 79 rows unmatched with reasons,
  0 WMA-to-state-park matches, **120 of 131 within 10% of the answer key (91.6%)**. The 11 disagreements are real
  source differences (e.g. the hunting-area layer covers only part of Daniel Boone NF and the refuges; state park
  ABSOLUTE_ACREAGE vs the key's tract), so the score depends on which lists and size fields the research file picks.

## What could NOT be tested here (the acceptance criteria)
- **95% agreement within 10% on the Kentucky answer key using the real research file**: the real
  `acres-us-ca-oct31.json` was not available to me. The smoke run above (91.6%) used my own research rows, so it
  is not this criterion. Run: `python3 kpc_acres.py --in acres-us-ca-oct31.json --areas US-KY --answer-key ky-answer-key.json`
  and read the "answer key" line in report.md.
- **Chat 11 checks 30 random matches, 28 or more right**: needs a person (chat 11); not done.
- **All US + Canada in 3 runs or fewer, each 50 minutes or less**: not run (no real research file; a full run hits
  hundreds of hosts). Timing, `--max-minutes`, exit 3 and `--resume` were tested only on fixtures.
- Real key files (`us-key/`, `ca-key/`): the tool reads `{"parks": {ref: {"m": [[id, name, acres, how], ...]}}}` and
  answer-key `tracts`; the real US/CA key format was not on the box, so record-id matching was only tested on fixtures.
- Old `.xls` (not `.xlsx`) files, ArcGIS Hub pages that need resolving to a layer, scanned PDFs: not supported, reported as failed with the reason.
- The county check (rule c) uses Census TIGERweb, so it works for US states only; Canadian rows fall back to the 25 km point check or "county not checked".
