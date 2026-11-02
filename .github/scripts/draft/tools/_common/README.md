# _common: shared source for the KPC tools

- `polite.py`: the one polite web reader (class `Polite`) every tool uses: one honest User-Agent `KPC park tools (<contact>)` (`KPC_CONTACT` replaces the default contact), at least 2 s between requests to the same host, robots.txt read and obeyed, a 4xx on robots.txt alone = no robots rules (RFC 9309), a 403 on the data request itself = blocked, accepted and never retried, disk cache, `polite_selftest()`.
- `t3_src.py` → `kpc_sitemaps/kpc_sitemaps.py`, `t6_src.py` → `kpc_inspire/kpc_inspire.py`, `t4_src.py` → `kpc_parcels/kpc_parcels.py`, `t7_src.py` → `kpc_trail_lines/kpc_trail_lines.py`. kpc_parcel_trace has no copy: it imports kpc_parcels.
- `build.py`: replaces the `#@@POLITE@@` line in each source with `polite.py`, so each tool ships as one file. `python3 build.py` rebuilds every tool folder found next to `_common`; `python3 build.py --check` only says whether the shipped files match. Edit here, rebuild, then run each tool's `--selftest`.
- `t3_measure.py`: measures kpc_sitemaps' T3 acceptance numbers on a finished run (used in kpc_sitemaps/TEST_REPORT.md).
