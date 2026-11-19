# T1 tracer accuracy test (Opus, 19 Nov 2026; key-quality.md section 16 T1, section 19 item 6)
- `t1-list.json`: the FIXED list. Seeded draw (seed `t1-tracer-test-2026-11-19`, sha256(seed + ref)) of 60 parks the fresh fact
  check of the published US key calls verified (no flags, all rows in the read; no trails, rivers, byways, shores): 20 small
  (under 100 ac), 20 middle (100-1,000), 20 large (over 1,000), interleaved. 6,825 candidates. Agencies: 30+ hosts.
- `run-<id>/`: one folder per run of KPC-Data `.github/workflows/kpc-trace-test.yml` (by hand, test mode): `t1-summary.md`
  (the sum in the grade's words, 95% ranges), `t1-parks.csv` (every park: traced / official acres, covered, outside, line
  distance middle and worst tenth in feet, failure), `t1-result.json`, `picked.json` (what was picked, what was skipped and
  why = the map find rate), the finder receipt, the tracer log.
- The tracer never sees `outline_acres` or the official outline (no acres file; sizes stripped from its input). The measuring
  script `kpc_trace_measure.py` reads KPC-Links data/outlines only after the tracer is done.
- The maps and traces sit on the THROWAWAY branch `trace-test` (test material only): delete it once Fable has the report.

## Fable's read of run 44530520714 (19 Nov 7:40 AM CST): NOT ENOUGH to rule R-G9 on; run 2 needed
- 60 walked, the finder queued 27 map PDFs (45%), 13 had a usable map page (22%): 0 small, 9 middle, 4 large. The spec asks 10 / 10 / 10.
- 5 drawn, all 5 GOOD by area (traced / official 0.97-1.10, covered 0.92-0.99, outside 0.03-0.10). 8 refused by the tracer's own
  checks (5 NO FIT, 2 NO LINE, 1 clipped at the sheet edge): a refusal is a pin, not a wrong line. 0 WRONG LAND of 5 drawn = 0-43%.
- US-11892 (Colorado): 98.8% covered, yet the line reads 2,759 ft off. Both cannot be true of a clean outline; most likely holes
  inside the trace were measured as line. The measuring script now measures the OUTSIDE rings and counts holes apart.
- The throwaway branch was never written (the save step stopped: GNU find refuses -prune with -delete), so the 13 maps and the 5
  traces are gone and nothing can be looked at. Fixed in kpc-trace-test.yml; the tracer's own report.csv is saved with the report now.
- The tracer ran blind: 0 size fields in its input, no acres file; its only map sources are roads, water and survey lines.
- `t1-list-2.json` (75 parks, 25 per size class, 11-14 map hosts per class): the same seed, drawn from fact-verified parks that
  already have a stored official map PDF link, so the walk can fill 10 / 10 / 10 without a crawl. Run 2 = ONE run by hand with
  input list = t1-list-2.json, on Brandon's go. Fable writes the R-G9 sheet from run 2's report.
