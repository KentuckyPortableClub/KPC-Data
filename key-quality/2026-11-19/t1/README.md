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
