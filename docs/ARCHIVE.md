# KPC-Archive: what moved out of KPC-Data, and how the bots still find it

KPC-Data keeps what the site and the bots read every day. Bulk history moves to **KentuckyPortableClub/KPC-Archive**
(public, same paths, under 500 MB). KPC-Data's git history is NOT rewritten; a history cleanup is a separate decision for Brandon.

## What moves (kpc_archive_move.py groups)
| group | folder | default | why |
|---|---|---|---|
| `previous` | `data/waiting/previous/` | yes (rotation: older than 14 days) | undo copies of replaced live files |
| `archive` | `archive/` | yes | old dated batches |
| `fers-review` | `data/fers/review/` | yes | per-run review dumps, no reader |
| `sources-review` | `data/sources/review/` | **no** (name it in `--groups`) | writer/readers not confirmed |

**Never moves:** anything under `data/waiting/` except `previous/` (held items wait for grading and approval), the key folders
(`data/us-key`, `ca-key`, `world-key`; rules hashes), switch files, `.github/`, and the Event Photo Archive PDF. The script refuses them.

## How a reader finds a moved file
`data/archive-manifest.json` (in KPC-Data) lists every moved path with sha256, bytes and the source commit.
`.github/scripts/kpc_archive.py`: `fetch(rel, DATA)` downloads `https://raw.githubusercontent.com/KentuckyPortableClub/KPC-Archive/main/<rel>`,
checks the sha256, and returns bytes (or `None`: skip cleanly). It only reaches for the network for a path the manifest lists, so before the
first move nothing changes. `KPC_ARCHIVE_FETCH=off` turns it off. Today the readers are the waiting room's `undo` and `undo-bot`.

## Commands
    python3 .github/scripts/kpc_archive_move.py --data . --archive ../KPC-Archive                  # dry run: prints the MB saved
    python3 .github/scripts/kpc_archive_move.py --data . --archive ../KPC-Archive --apply          # one-time move (copy, verify, manifests, delete)
    python3 .github/scripts/kpc_archive_move.py --data . --archive ../KPC-Archive --verify         # archive vs manifest
Rotation (by hand, no cron): Actions > "KPC archive rotate (by hand)"; needs the repo secret `KPC_ARCHIVE_TOKEN` (Contents read/write on KPC-Archive only).

## Undo of the move
KPC-Data history still has every file: `git revert` the move commit restores them. The archive copy stays.
