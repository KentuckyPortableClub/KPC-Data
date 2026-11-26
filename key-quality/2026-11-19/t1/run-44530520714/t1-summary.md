# T1 tracer accuracy test: result

Parks traced: 13 (list ../work/t1-list.json). Skipped while walking the list: 47; picture-map find rate 13 of 60 parks walked (22%).

Grade words: WRONG LAND = most of the trace outside the official outline; TOO BIG = over 1.25 x the official acres; MISSING PIECES = covers under 0.8 of it; FAILED = no trace, no boundary on the map, or the wrong feature. Ranges are 95% (Wilson).

| size | n | WRONG LAND | TOO BIG | MISSING PIECES | GOOD | FAILED |
|---|---|---|---|---|---|---|
| small | 0 | 0 (0%-0%) | 0 (0%-0%) | 0 (0%-0%) | 0 (0%-0%) | 0 (0%-0%) |
| middle | 9 | 0 (0%-30%) | 0 (0%-30%) | 0 (0%-30%) | 3 (12%-65%) | 6 (35%-88%) |
| large | 4 | 0 (0%-49%) | 0 (0%-49%) | 0 (0%-49%) | 2 (15%-85%) | 2 (15%-85%) |
| all | 13 | 0 (0%-23%) | 0 (0%-23%) | 0 (0%-23%) | 5 (18%-64%) | 8 (36%-82%) |

Line distance (feet, traced line to official line), per size class: middle of the parks' middles / worst tenth

- middle: middle 52 ft (range 43-2759); worst tenth 337 ft (range 174-7648)
- large: middle 45 ft (range 36-54); worst tenth 519 ft (range 108-930)

Every park: `t1-parks.csv`. Skipped parks and why: `t1-result.json` (skipped). Nothing here touches a map or a key.
