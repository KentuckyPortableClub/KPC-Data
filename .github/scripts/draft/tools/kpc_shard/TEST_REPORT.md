# kpc_shard TEST_REPORT (Oct 31 2026, America/Chicago)

**Built and tested on synthetic data only.** The real KPC-Data repo, the `data/parkinfo` files, the layer
collector and GitHub Actions were NOT available. Every number below comes from a **local simulation**: a fake
slow collector (`tests/sim/fake_collector.py`) run as parallel local processes on Python 3.12.16, with no network.

## 1. Selftest
`python3 kpc_shard.py --selftest` -> **PASS (23/23 checks)**, offline, Python 3.12.16 and 3.13.5. It covers: kpc_order
import, club order, parkinfo weights (one broken file -> weight 1 and a warning, no crash), plan 1/4/8/12 groups
(every area once, balanced, club order kept), `--resume`, hosts rule (no host in more than 2 groups) and its
expected output, a layer list with URLs, a host used by every area (-> 2 groups), join ok (copy, newest `done` wins,
counts summed, `work/` and non-area files skipped), join with areas left (exit 3, `left=US-KY`), join refusal
(exit 4, nothing copied), and CLI exit codes. Also passes in the real repo layout
(`.github/scripts/tools/kpc_order.py` + `.github/scripts/tools/kpc_shard/`, tests/ copy removed).

## 2. Simulation: 12 synthetic US states, 4 groups vs 1 job (`tests/sim/run_sim.py`, results in `sim_results.json`)
Setup: 52 layer reads over 15 hosts; each state has its own portal (1-6 layers), and three shared hosts
(`edits.nationalmap.gov`, `apps.fs.usda.gov`, `services.arcgis.com`) are each used by 5 states. Per job:
2 s gap per host + 0.3 s simulated latency per request. Weights = 100 x layers per state.

| Acceptance check | Target | Simulation result |
|---|---|---|
| Same output files, byte for byte except dates | identical | **12/12 files identical** after masking dates (0/12 raw: only `read_date`/`collected_at` differ) |
| Time cut | >= 3x | 1 job **54.0 s** -> 4 groups (`hosts`) **16.9 s** = **3.19x** |
| Jobs on one host at once | <= 2 | **max 2** (per request and per area window); per-host timestamps in `tests/sim/host_timestamps_hosts4.csv` |
| Join refusal | refused | US-CA written by parts 1 and 2 -> **exit 4, nothing copied, data dir not created** |
| Chain on exit 3 | next run takes only the left | run 1 `--max-minutes 0.05`: all 4 jobs exit 3, join exit 3 lists 8 left; run 2 plans only those 8, join exit 0, final 12/12 identical |

Extra findings:
- **Weight-only `plan`** on the same data was also 3.19x, but its groups put PAD-US in **4** groups and
  `services.arcgis.com` in 4 (static). The measured overlap stayed at 2 only because the shared requests were short
  and happened not to line up. Only `hosts` *guarantees* the 2-jobs rule; use `hosts` for the collector.
- **A host used by every area** (e.g. if the collector asks PAD-US once per state): `hosts` can only make
  **2 groups**, giving 1.95x (54.2 s -> 27.8 s). Asking for 6, 8 or 12 groups returns fewer groups when shared hosts
  force it. To get 3x+ on the real collector, its PAD-US / EDW / ArcGIS reads must not touch every state in each
  group (e.g. read the national layer once in a separate pre-job), or chat 10 decides that host can take more and
  runs `hosts --max-per-host N`.

## 3. Workflow `kpc-sharded.yml`
- Parses with PyYAML 6 (used only for this check). **actionlint v1.7.12 + shellcheck: 0 findings** on the template and
  on `tests/example-caller.yml`.
- The plan, join and status-board bash steps were run locally against the fixtures (exit 3 -> `left=US-KY`, board line
  written). **Not run on GitHub**: the matrix, artifacts upload/download, `max-parallel`, the job-level concurrency
  group, the push, and `gh workflow run` chaining (needs `actions: write` and a caller with
  `workflow_dispatch` inputs `areas` + `chain`).

## 4. Only on the real layer collector on GitHub
- Byte-identical outputs (depends on the real collector writing only its own areas and being deterministic).
- The real time cut (real latency, GitHub runner start-up ~20-40 s per job, artifact transfer, the real weights).
- The real per-host overlap (the collector must log host timestamps; the simulation's logger is `fake_collector.py`).
- Real `parkinfo` weights (Kentucky etc.), the divert command, and the status-board file format: placeholders here.

## 5. Judgment calls
- Join refusal exits **4** (the contract's "anything else"): nothing was copied, so the workflow should not push data;
  it still writes the status-board line.
- Bare country codes (`CA`, `MX`, `GB`) are not matched by `rank()`'s regex, so they use `kpc_order.rank_cc()` (also imported).
- Area of a part file = file name up to the first `.` or `_` (`US-TX.json`, `US-TX_layers.geojson`); same relative
  path from two parts also counts as a conflict. `work/` and non-area files are not copied (reported as skipped).
- Merged state goes to `<into>/state.json` (or `--state`) and merges with the one already there; `counts` = this run's
  sum, `counts_total` = running total.
- The join job's concurrency group is `<bot group>-join`, not the bot's own name: a reusable workflow that reuses the
  caller's group would wait on itself. The caller keeps its own workflow-level `concurrency:`.
- `tests/kpc_order.py` is a copy kept only so the selftest runs from this folder; the real one is found first.
