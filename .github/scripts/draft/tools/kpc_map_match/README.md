# kpc_map_match (T1): map-match second opinion

For each open question "is this official record that park?" (KPC-Data `data/waiting/questions/*.json`), the tool
fetches the candidate record from its ArcGIS layer (outSR 4326, about 3 m simplify) and scores it:
is the POTA pin inside it (or how far outside), geodesic acres against the acres the park's own page gives,
how well the names match, and whether another record within 2 km matches the name better. When there is an
agency picture map, it also saves a JPEG with the record drawn on aerial imagery so a person can compare.
Each row lands in a band: **STRONG**, **WEAK** or **CONFLICT**, with the reasons. **It never writes YES or NO.**
The club's rules decide, and a person grades.

Install: `python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt`. Set `KPC_CONTACT` (an email or
URL) for the User-Agent.

Example (the call sign is a test one):

```
KPC_CONTACT=k4test@example.org python kpc_map_match.py \
  --questions KPC-Data/data/waiting/questions/*.json --parkinfo KPC-Data/data/parkinfo \
  --docs KPC-Data/data/docs/*.json --pictures-index picture-maps/index.json \
  --areas US-KY,US-TN --cache ~/.kpc_cache --out out/ --max-minutes 50 --resume
```

Output goes in `out/`:
- `map_match.json`: one row per question, keyed `ref|record`, with pin_inside, pin_dist_m, acres_record,
  acres_park, acres_ratio, name_score, better_nearby[], picture, iou (when an agency outline is given), band, source_url, read_date and why (the band reasons).
- `pictures/`: JPEGs, 1600 px or less, quality 70 or less.
- `summary.json`, `run_log.txt`, `state.json`.

Exit codes: 0 done, 3 out of time (run again with `--resume`), 2 bad input. Self test, offline:
`python kpc_map_match.py --selftest`. Test-only flags: `--include-answered --refs keys.txt`.
Also available: `--no-pictures`, `--no-pages`, `--no-neighbours`, `--no-pota-api`.
