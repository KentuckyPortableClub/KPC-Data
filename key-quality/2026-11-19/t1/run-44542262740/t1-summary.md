# T1 tracer accuracy test: result

Parks traced: 30 (list ../work/t1-list.json). Skipped while walking the list: 7; picture-map find rate 30 of 37 parks walked (81%).

Grade words: WRONG LAND = most of the trace outside the official outline; TOO BIG = over 1.25 x the official acres; MISSING PIECES = covers under 0.8 of it; FAILED = no trace, no boundary on the map, or the wrong feature. Ranges are 95% (Wilson).

| size | n | WRONG LAND | TOO BIG | MISSING PIECES | GOOD | FAILED |
|---|---|---|---|---|---|---|
| small | 10 | 0 (0%-28%) | 1 (2%-40%) | 1 (2%-40%) | 3 (11%-60%) | 5 (24%-76%) |
| middle | 10 | 0 (0%-28%) | 1 (2%-40%) | 1 (2%-40%) | 2 (6%-51%) | 6 (31%-83%) |
| large | 10 | 0 (0%-28%) | 0 (0%-28%) | 0 (0%-28%) | 2 (6%-51%) | 8 (49%-94%) |
| all | 30 | 0 (0%-11%) | 2 (2%-21%) | 2 (2%-21%) | 7 (12%-41%) | 19 (46%-78%) |

Line distance (feet, traced line to official line), per size class: middle of the parks' middles / worst tenth

- small: middle 73 ft (range 48-933); worst tenth 199 ft (range 86-3814)
- middle: middle 41 ft (range 20-52); worst tenth 256 ft (range 74-3893)
- large: middle 45 ft (range 36-54); worst tenth 519 ft (range 108-930)

Every park: `t1-parks.csv`. Skipped parks and why: `t1-result.json` (skipped). Nothing here touches a map or a key.
