# KPC-Data

Hidden, bot-only data for the Kentucky Portable Club website (storage plan Stage 2, Oct 27 2026). Nothing here is shown on the
site; chat 8 (research desk) and HQ review it here. The bots that write it run in THIS repo and read KentuckyPortableClub/KPC-Links
(public) read-only.

| Folder / file | What | Written by |
|---|---|---|
| `data/fers/` | 2-fer finder results per state / province / country (`report*.json`, `missing-*.json`, `same-outline*.json`); files over 20 MB are gzipped | `.github/workflows/kpc-fers.yml` (by hand) |
| `data/outline-leads/` | official outline layers we do not read yet (per state), `tested.json`, `near-miss.json` (parks with no outline + official areas around their pin) | `kpc-parking-explorer.yml` (outline kind), `kpc-watch.yml` (near misses, daily) |
| `data/access-leads/` | parking / trailhead / ramp layers found on the agencies' servers | `kpc-parking-explorer.yml` (monthly) |
| `data/map-observations.json` | the OBSERVATIONS LOG: what changed in the park data and is worth a human look (kept 90 days) | `kpc-watch.yml` (daily) + `kpc-fers.yml` |
| `data/observations/` | older per-bot observation files (Oct 27); new ones go into map-observations.json | - |
| `pdf/` | the big static PDFs, served by GitHub Pages | by hand |

Practice call sign in any example: K4TEST. Maps and park info are a planning aid, not a guarantee.
