# Storage plan for big generated files (WRITTEN, NOT APPLIED)

Status: a plan only. Nothing in it is switched on, and nothing in the club repos was changed. **It needs Brandon's OK**,
because options A to C change how the site reads the files.

## The problem

- GitHub refuses a push with any single file over **100 MiB** (104,857,600 bytes). It warns at 50 MiB.
- `US-AK.json.gz` was reported at **103.5 MB**. That is 103,500,000 bytes, or about **98.7 MiB**. It is about 1.36 MB
  under the hard limit. If Alaska grows by about 1.3 %, the save is rejected and the key stops updating for every state in
  that run.
- Each overwrite of a big generated file adds a full new copy to the repo history (a gzip barely deltas), so the repo
  keeps growing.

## Step 0 (built in v0.5.0): the size guard

`kpc_engine.py doctor --tasks storage` checks every file in both checkouts:

- **WARN** at 80 MiB;
- **RED** at 95 MiB, with exit code 1.

The levels live in `config/rules.json` under `key_doctor.size_warn_mib` and `size_red_mib`, behind the switch
`key_doctor.size_guard`, which is on. Under the guard, `US-AK.json.gz` shows **RED** today. The guard is the early
warning. It does not fix anything.

## Options (pick one; A is the recommendation)

| | What | Site change | Pros | Cons |
|---|---|---|---|---|
| **A. Split** (recommended) | Write `US-AK/index.json` + parts. Split **by region** (for example the Alaska boroughs, or a fixed lat/lon grid of 4 to 8 tiles) or **by 2-fer kind** (`same land`, `area`, `trail`, `river`/`water`). | The page first reads `index.json`, then only the parts it needs (the tiles in view, or the kind being shown). | Stays plain git and Pages, with no new service. A smaller file loads faster on phones. Each part changes less, so history grows less. | It needs a loader change in the site JS, plus a writer change in the key or 2-fer bot. |
| B. Git LFS | Track `*.json.gz` over 50 MiB in LFS. | **GitHub Pages does not serve LFS content.** It serves the small pointer file, so the site would have to fetch from `media.githubusercontent.com` instead. | No splitting. | Free LFS bandwidth and storage quotas are small. Every clone and Action needs `lfs: true`. It changes the site URL. Not recommended. |
| C. Release asset | Upload the big file to a GitHub Release (up to 2 GiB per file). | The page fetches it from a `releases/download/...` URL. Browsers usually can't read that URL directly from another site, because it is not served with open CORS headers. Test it before relying on it. Otherwise it needs a proxy or an Action that copies the file into Pages. | No limit worth worrying about. | Uploading needs a token with write access, plus a new upload step. The URL changes at every release unless the "latest" tag is used. |
| D. Leaner file (do it anyway) | Round coordinates to 5 decimals (about 1 m), drop unused fields, simplify outlines within POTA's tolerance. | None, if the fields kept are the ones the page reads. | Often 20 to 40 % smaller. | Must be checked against the page's fields first. |

**Suggested order:** D now (no site change), then A for any file the guard shows as WARN, starting with `US-AK`. Do it on
a **test build** first: a copy of the page that reads the split files, checked against today's page for the same parks.

## Held waiting-room copies (built, OFF)

`kpc_waiting_room.py mode_tidy()` runs at the start of every check:

- `WAITING_TIDY=1` removes a held copy in `data/waiting/in/` once the live file already has the same build. A newer
  build replaced it, or it was released.
- `WAITING_KEEP_GENS=N` also removes `previous-<g>` folders older than N generations.

Both are **off by default** (`WAITING_TIDY` unset, `WAITING_KEEP_GENS=0`), which is today's behaviour. The doctor's
storage task lists these copies (`superseded_held`) without deleting anything, so you can see what tidy *would* remove
before turning it on.

## Generated output only on `tools-out`, with overwrite commits

- Engine and bot output that nobody hand-edits (doctor reports, `release/` copies, grade lists, review pages) goes to
  a branch named `tools-out`, never to `main`.
- Each run **overwrites** the files: fetch, reset to `origin/tools-out`, copy the new files in, commit, then push.
  This is the same pattern as `kpc_save_overwrite.sh` in patch 01. There is never a merge or a rebase on generated files.
- **Squash (optional, needs Brandon's OK, because it rewrites that branch's history):** once a month, replace
  `tools-out` with a single fresh commit:
  `git checkout --orphan tmp && git add -A && git commit -m "tools-out <date>" && git push --force origin tmp:tools-out`.
  Old copies stop counting once GitHub cleans up unreachable objects. Only `tools-out` is ever squashed. `main` never is.

## FERS_ALGO

The FERS_ALGO change is **in** (patch 04): `FERS_ALGO = 'fers-2026-11-02.1'` in `kpc_fers.py`.

- With `KPC_FERS_REUSE_KEY=algo`, the 2-fer bot reuses earlier pair results while the *algorithm* is unchanged, rather than
  re-running everything whenever any byte of the script changes (`CODE_HASH`, which stays the default).
- Bump `FERS_ALGO` by hand whenever the pairing logic changes.
