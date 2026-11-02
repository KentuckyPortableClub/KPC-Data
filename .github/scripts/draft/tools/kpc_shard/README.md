# kpc_shard: run a map bot over several areas at once

A small library + command line + reusable workflow (`kpc-sharded.yml`) that splits ANY KPC bot's areas into
parallel GitHub jobs and joins the results back with one push. Python 3.12, standard library only.

- `plan --areas all --groups 8 [--weights w.json | --parkinfo data/parkinfo]`: greedy biggest-first balance by parks
  per area, club order (`kpc_order.rank()`) kept inside each group. Prints `[{"i":1,"areas":"US-TX,US-RI"},...]`.
- `hosts --areas all --groups 8 --map layer_list.json [--max-per-host 2]`: same, but no shared host is used by more
  than 2 groups, so at most 2 jobs ever hit one host at once. Algorithm: hosts used by more than 2 areas are
  "shared". (A) greedy biggest-first, each area into the lightest group that keeps every shared host in at most
  2 groups (ties: the group already using its hosts). (B) always valid fallback: areas linked by shared hosts form a
  component, each component is cut into at most 2 bundles, bundles are packed whole. Both get a move/swap local
  search on the heaviest group; the better balanced valid one wins. A host used by EVERY area means only 2 groups.
- `join --parts parts --into data [--areas LIST] [--state FILE]`: copies `parts/<i>/` area files (file name starts with
  the area code; `work/` and non-area files are skipped) into the data dir and merges `state-<i>.json` into
  `<into>/state.json` (newest `done` per area wins, `counts` summed). If two parts wrote the same area it copies
  NOTHING and exits 4. Prints `left=...` and exits 3 when areas are left, else 0.
- Contract flags: `--out` (reports), `--limit`, `--areas`, `--resume --state` (plan skips done areas),
  `--max-minutes` (accepted; these steps take seconds). `python kpc_shard.py --selftest` prints PASS/FAIL offline.

**kpc_order.py is imported, not copied.** It is looked for in `$KPC_ORDER_DIR`, the script's dir, its parent
(KPC-Data `.github/scripts/tools/kpc_order.py` next to this folder), the grandparent, then `tests/kpc_order.py`
(a copy kept ONLY so the selftest runs from this folder; a warning is printed when it is used).

**Bot side** (chat 10's small edits): read `AREAS` from the env (`kpc_shard.areas_from_env()`), write only its own
areas' files into `--out`, and finish with `kpc_shard.write_part_state(out, {area: {"done": ts|None, "counts": {}}},
counts)` (writes `state-$KPC_SHARD_I.json`). Exit 0 done, 3 time ran out.

Example: `python3 kpc_shard.py hosts --areas US-TX,US-CA,US-KY --groups 2 --weights tests/fixtures/weights.json --map tests/fixtures/hosts.json`
Workflow: see `tests/example-caller.yml` (keeps the bot's own `concurrency:`; join uses `<group>-join`).
Simulation: `python3 tests/sim/run_sim.py` (fake slow collector, ~3 min).
