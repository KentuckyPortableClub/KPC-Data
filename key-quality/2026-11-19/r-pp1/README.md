# R-PP1 park and preserve (Opus, 19 Nov 2026; KPC-Links draft PR, branch prep/r-pp1-park-preserve)
Offline builds of AK and ID from the saved shapes (boundary-cache), main's rules 7c6e01e1bc2b (OLD) against R-PP1 98b1f03ec6ed
(NEW), both with KPC_KEY_REMATCH_IDS=1 + GEO_CACHE_MODE=only + KPC_KEY_OFFLINE=1 (the scorecard's fixed settings), both started
from the published key. No shapely in the chat box: SIZE_BIG / BIG_PIECE mean nothing here.
- `parks-changed.csv`: every park whose records changed (5; nothing else moves in AK or ID).
- `factcheck-AK-ID-old.txt` / `-new.txt`: kpc_key_factcheck.py on both builds, same inputs.
- `gold-old.txt` / `gold-new.txt`: kpc_key_grade.py gold (77 parks; SEALED as numbers only). Unchanged.
- `all-area-scan.txt`: the published key, all 50 areas: every joined row where a National park / monument / preserve name and its
  record disagree on 'preserve' (where the rule could act at all).
