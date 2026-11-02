# kpc_pulloffs: possible pull-offs near a park, seen on an aerial photo

Finds gravel or paved spots next to a public road, in or just outside a park's
**official** outline, where a car could probably stop. It uses only public
government sources: Census **TIGERweb** roads, the USGS **NAIP** aerial photo
(4 bands, with infrared) and FEMA **USA Structures** building outlines (to drop house
and farm yards). Every result is labelled *"Possible pull-off (seen on an
aerial photo, not official)."* It is a planning aid, not a guarantee.

**Install (Python 3.12):** `pip install -r requirements.txt`

**Run:**
```
export KPC_CONTACT="you@example.org"      # goes into the User-Agent
python kpc_pulloffs.py --parks parks.json --access data/access/*.json \
    --pictures picture_maps/index.json --out out/ --areas US-KY --max-minutes 50
python kpc_pulloffs.py --parks parks.json ... --out out/ --resume   # carry on next time
python kpc_pulloffs.py --selftest                                  # offline, prints PASS/FAIL
```
Options: `--limit N` (first N parks), `--cache DIR` (keep downloads between
runs; default `out/work/cache`), `--hints` (DOT/USGS turnout or overlook points),
`--cut 0.5` (score cut).

**Exit codes:** 0 = done · 3 = time ran out with work left (run again with
`--resume`) · anything else = a crash. A bad park never stops the run; it goes
into `report.md` with the reason.

**Output (all inside `--out`):** `pulloffs/<area>.json` (rows with lat/lon,
inside/outside, score, road, photo year, `source_url`, `read_date`, `why`),
`pulloffs/chips/*.jpg` (yellow = park line, white = road, red = the patch),
`pulloffs/review.md` (best first, for checking by eye), `report.md` (recall line,
problems, web manners), `work/log/kept_out.jsonl` (everything left out, with the reason).
Parks with no official outline get no output.

**How it decides:** 100 m band around the outline (400 m when a park has no
official access and no approved pull-off, ruling G-P2) → points along public roads
every 150 m → NAIP photo → bare, not water, not a roof (NDVI < 0.15), one patch ≥ 300 m²
touching the road and at least about 8 m deep (ruling G-P1: shoulders never count) →
score 0–1, cut 0.5 → drop anything within 50 m of an official access point.
Dry grass/hay, lots next to buildings outside the park, and long strips running along
the road (an offset road line) are logged, not shown. See TEST_REPORT.md for what was tested.
