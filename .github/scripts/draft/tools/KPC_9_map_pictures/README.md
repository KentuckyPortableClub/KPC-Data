# KPC 9: Map Picture Maker

Makes one small map picture per item (a question, a 2-fer row, or a park outline) so the checker can grade by looking.
Each picture is a JPEG of 900 × 700 px and under 150 KB. It comes with a one-line caption and a line in `pictures/index.json`.

## What is on each picture
- **The base map** comes from government sources only:
  - US: USGS The National Map, USGSTopo (`--imagery` switches to USGSImageryTopo).
  - Canada: Natural Resources Canada CBMT. The tool tries `maps-cartes.services.geo.ca` first, then `geoappext.nrcan.gc.ca`.
  - Switzerland: swisstopo. France: IGN Géoplateforme. Austria: basemap.at.
  - Anywhere else, or when a tile server is down or its robots.txt says no: a plain background with Natural Earth coastlines and lakes.
  - It never uses OSM or Google. The tile credit is in the bottom-right corner.
- **The outline being graded** is gold, 2 px. Neighbours on the same layer are thin grey, with their names.
- **POTA's pin** is a red dot with the park number. If the pin falls off the picture, a red arrow on the edge points to it.
- **2-fers:**
  - The parks are gold, blue, green and purple. The overlap patch is orange at 40%.
  - Trail rows: the 100 ft band from the trail line is dashed.
  - River (water-trail) rows: the 100 ft band from the river bank is dashed, and the bank (USGS NHD water) is thin blue.
  - When a row's stored `shape` is a stretch of line rather than an area, it is drawn as a thick orange line.
- **Also on every picture:**
  - A scale bar, a north arrow, and a 2-line title.
  - The title gives the park number, name and grade, the record name, the acres (record vs drawn) and "pin inside / N m outside".
  - A small inset at 4× zoom-out (leave it off with `--no-inset`).

## Install
```
pip install -r requirements.txt
```
You need Python 3.11 or newer. No API keys are needed.

## Use (K4TEST examples)
```
# one picture per question (records read live)
python kpc_map_pictures.py --questions data/waiting/questions/layers.json --out pictures

# only the NO answers for US parks, at most 20 pictures
python kpc_map_pictures.py --questions data/waiting/questions/layers.json --answer NO --ref-prefix US- --limit 20

# one picture per live Kentucky 2-fer row (Kentucky outlines come from the club's ky-*.geojson files)
python kpc_map_pictures.py --fers data/fers/US-KY.json --ky-outlines . --out pictures
python kpc_map_pictures.py --fers data/fers/US-KY.json --kind trail,river

# chosen park outlines from a key, or from a world-bounds country folder
python kpc_map_pictures.py --refs US-0019,US-0050 --key data/us-key/US-TN.json
python kpc_map_pictures.py --refs CA-0006,CA-0010 --key data/ca-key/CA-ON.json
python kpc_map_pictures.py --refs CH-0306,CH-0104 --key data/world-bounds/CH

# carry on after a time-out, and clean old pictures
python kpc_map_pictures.py --fers data/fers/US-KY.json --resume --max-minutes 50
python kpc_map_pictures.py --out pictures --clean-older-than 7
```
- `--ids` keeps only the listed items: 2-fer row ids or question refs. Separate them with `;`, because 2-fer ids already contain a comma. You can also give `@file` with one id per line.
- `--data` is the club's data folder. It is normally found from the input file's path.

## Exit codes
- 0 = all done.
- 3 = not finished: time ran out, `--limit` was reached, or some items failed and will be retried. Run again with `--resume`.
- 2 = bad input.

## Outputs
- `pictures/<kind>/<id>.jpg` and `pictures/<kind>/<id>.json` (the caption). `<kind>` is `questions`, `fers` or `outlines`.
- `pictures/index.json`: one line per item, with `{id, file, caption, read_date, sources, warnings, status}`.
- Items that failed get `status: "retry"` and a "SOURCE DOWN" or "CAN'T TELL" reason. They are tried again on the next run.
- **Warnings** are written when:
  - the pin is more than 2 km outside the outline;
  - the outline is tiny next to the record's acres;
  - the 2-fer patch is under 50 yards across;
  - the record geometry is empty;
  - a tile server failed.
- The pictures folder is made to be pushed to a **throwaway branch** and deleted after grading. Never put a picture in the main report.

## How it behaves
- At most 1 request per second per host. The User-Agent is `KPC-map-pictures (https://github.com/KentuckyPortableClub)`.
- It backs off on 429 and 5xx (and honours Retry-After), and it obeys robots.txt.
- After 3 failures on a host it stops asking that host for the rest of the run.
- Everything it reads is cached under `.kpc-cache/` with the date it was read. Tiles and records are kept 30 days, POTA pins 30 days and Natural Earth 1 year.
- It never writes to the club's files. It only reads them.
- Proclamation lines (`bdbnf`, the Daniel Boone NF proclamation) are never drawn as the park. The owned land (`bdbnfo`) is drawn instead.

## Tests
```
python -m pytest -q tests
```
The tests run offline on made-up shapes and use a fake web session.
