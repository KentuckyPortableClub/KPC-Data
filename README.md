# KPC look-up bot: requests and answers (orphan branch `lookup`, KPC-Data)
Throwaway files only. This branch is squashed to one fresh commit when it passes 150 MB (weekly, Sunday).
1. Write `requests/<your chat number>-<short id>.json`, e.g. `{"chat": 11, "kind": "map-check", "urls": ["https://..."], "report": "is the park line drawn?"}`. Kinds: page, map-check, layer-probe, parcel, probe (see kpc_lookup.py on main).
2. Commit + push to THIS branch only: `git fetch origin lookup && git checkout lookup` (or a worktree), add the file, `git push origin HEAD:lookup`.
3. The answer appears in `answers/<same name>.json` (+ `-1.jpg` pictures). Fetch the branch when you read your inbox.
4. Done with it? Push an empty file `read/<same name without .json>`: the answer, its pictures and the request are deleted. Unread answers go after 7 days.
