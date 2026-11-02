# 2-fer accuracy check: US-ID

Run 2026-11-01T00:38:17Z → 2026-11-01T12:15:36Z (UTC) · tool 0.1.0 (2026-10-31) · complete
Live rows in the file: 66 · checked: 66 · skipped (dropped / merged): 1154

| verdict | rows |
|---|---|
| CONFIRMED | 36 |
| SHRUNK | 6 |
| GREW | 4 |
| MOVED | 5 |
| GONE | 4 |
| RECORD CHANGED | 11 |

| flag | rows |
|---|---|
| small overlap (under 50 yd across) | 6 |
| trail line from the club saved copy (not re-read live) | 22 |

## For a person to look at

- **SHRUNK** `US-10006+US-10382@trail@45.705,-115.714`: live overlap is 28% smaller (171.1 ac vs 238.1 ac stored)
- **SHRUNK** `US-10006+US-10429@trail@46.104,-115.046`: live overlap is 60% smaller (1.4 ac vs 3.4 ac stored)
- **SHRUNK** `US-10006+US-10429@trail@46.231,-115.413`: live overlap is 57% smaller (6.1 ac vs 14.0 ac stored)
- **SHRUNK** `US-10006+US-4574@trail@46.421,-115.308`: live overlap is 43% smaller (5.0 ac vs 8.6 ac stored)
- **SHRUNK** `US-10381+US-4500@area@45.650,-114.525`: only 61% of the stored overlap is still inside the live overlap (10 m tolerance)
- **SHRUNK** `US-10429+US-4476@river@46.393,-115.215`: only 47% of the stored overlap is still inside the live overlap (10 m tolerance)
- **GREW** `US-10006+US-10381@trail@44.994,-115.069`: live overlap is 34% bigger (11.2 ac vs 8.3 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-10006+US-4474@trail@44.573,-115.304`: live overlap is 33% bigger (14.0 ac vs 10.6 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-2241+US-4480@area@44.414,-114.363`: live overlap is 717% bigger (1.4 ac vs 0.2 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-4478+US-4574@trail@45.692,-116.419`: live overlap is 25% bigger (9.2 ac vs 7.4 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **MOVED** `US-0890+US-10006@trail@45.490,-115.329`: live overlap centre is 369 m from the stored centre; 0% of the stored overlap is still inside it
- **MOVED** `US-10006+US-4476@trail@46.823,-114.907`: live overlap centre is 62698 m from the stored centre; 0% of the stored overlap is still inside it
- **MOVED** `US-10381+US-10429@river@45.617,-114.704`: live overlap centre is 3468 m from the stored centre; 4% of the stored overlap is still inside it
- **MOVED** `US-10429+US-4478@river@46.092,-115.110`: live overlap centre is 1150 m from the stored centre; 15% of the stored overlap is still inside it
- **MOVED** `US-4476+US-7994@area@46.017,-114.984`: live overlap centre is 50220 m from the stored centre; 0% of the stored overlap is still inside it
- **GONE** `US-0890+US-4476@area@45.381,-115.511`: no overlap between the live official outlines near this spot
- **GONE** `US-10381+US-4476@area@45.621,-115.083`: no overlap between the live official outlines near this spot
- **GONE** `US-10382+US-4476@area@45.534,-115.787`: no overlap between the live official outlines near this spot
- **GONE** `US-12298+US-4477@area@48.217,-116.468`: no overlap between the live official outlines near this spot
- **RECORD CHANGED** `US-0276+US-7363@area@43.299,-116.536`: US-7363: 1 key record id(s) no longer in gis.blm.gov/lands/BLM_Natl_NLCS_NM_NCA_poly/MapServer/0/query: [353] | US-7363: found by name 'MORLEY NELSON SNAKE RIVER BIRDS OF PREY NATIONAL CONSERVATION AREA' near the spot as new id(s) [None] (geometry now: CONFIRMED: live overlap 22.5 ac vs 22.8 ac stor
- **RECORD CHANGED** `US-10006+US-10336@trail@42.180,-115.466`: US-10336: 2 key record id(s) no longer in gis.blm.gov/lands/BLM_Natl_NLCS_WLD_WSA/MapServer/0/query: [4921, 4922] | US-10336: found by name 'Bruneau-Jarbidge Rivers Wilderness' near the spot as new id(s) [None, None] (geometry now: CONFIRMED: live overlap 14.6 ac vs 15.2 ac stored (-4%), 100% of the
- **RECORD CHANGED** `US-10336+US-12224@river@42.559,-115.627`: US-10336: 2 key record id(s) no longer in gis.blm.gov/lands/BLM_Natl_NLCS_WLD_WSA/MapServer/0/query: [4921, 4922] | US-10336: found by name 'Bruneau-Jarbidge Rivers Wilderness' near the spot as new id(s) [None, None] (geometry now: MOVED: live overlap centre is 24267 m from the stored centre; 17% of
- **RECORD CHANGED** `US-10344+US-7363@area@43.282,-116.585`: US-7363: 1 key record id(s) no longer in gis.blm.gov/lands/BLM_Natl_NLCS_NM_NCA_poly/MapServer/0/query: [353] | US-7363: found by name 'MORLEY NELSON SNAKE RIVER BIRDS OF PREY NATIONAL CONSERVATION AREA' near the spot as new id(s) [None] (geometry now: CONFIRMED: live overlap 2477.8 ac vs 2479.8 ac 
- **RECORD CHANGED** `US-10348+US-10383@area@44.118,-114.145`: US-10383: 1 key record id(s) no longer in gis.blm.gov/lands/BLM_Natl_NLCS_WLD_WSA/MapServer/0/query: [4346] | US-10383: found by name 'Jim McClure-Jerry Peak Wilderness' near the spot as new id(s) [None] (geometry now: CONFIRMED: live overlap 9821.2 ac vs 9819.8 ac stored (+0%), 100% of the stored o
- **RECORD CHANGED** `US-10383+US-13296@area@44.131,-114.397`: US-10383: 1 key record id(s) no longer in gis.blm.gov/lands/BLM_Natl_NLCS_WLD_WSA/MapServer/0/query: [4346] | US-10383: found by name 'Jim McClure-Jerry Peak Wilderness' near the spot as new id(s) [None] (geometry now: CONFIRMED: live overlap 233.0 ac vs 233.6 ac stored (-0%), 100% of the stored ove
- **RECORD CHANGED** `US-10383+US-4480@area@44.020,-114.198`: US-10383: 1 key record id(s) no longer in gis.blm.gov/lands/BLM_Natl_NLCS_WLD_WSA/MapServer/0/query: [4346] | US-10383: found by name 'Jim McClure-Jerry Peak Wilderness' near the spot as new id(s) [None] (geometry now: CONFIRMED: live overlap 53559.6 ac vs 42893.9 ac stored (row acres; the stored sh
- **RECORD CHANGED** `US-10383+US-4481+US-7362@area@43.960,-114.398`: US-10383: 1 key record id(s) no longer in gis.blm.gov/lands/BLM_Natl_NLCS_WLD_WSA/MapServer/0/query: [4346] | US-10383: found by name 'Jim McClure-Jerry Peak Wilderness' near the spot as new id(s) [None] (geometry now: CONFIRMED: live overlap 3.1 ac vs 4.1 ac stored (-25%), 100% of the stored overla
- **RECORD CHANGED** `US-10383+US-4481@area@44.005,-114.375`: US-10383: 1 key record id(s) no longer in gis.blm.gov/lands/BLM_Natl_NLCS_WLD_WSA/MapServer/0/query: [4346] | US-10383: found by name 'Jim McClure-Jerry Peak Wilderness' near the spot as new id(s) [None] (geometry now: CONFIRMED: live overlap 39672.8 ac vs 39722.6 ac stored (row acres; the stored sh
- **RECORD CHANGED** `US-12180+US-7363@area@43.144,-116.527`: US-7363: 1 key record id(s) no longer in gis.blm.gov/lands/BLM_Natl_NLCS_NM_NCA_poly/MapServer/0/query: [353] | US-7363: found by name 'MORLEY NELSON SNAKE RIVER BIRDS OF PREY NATIONAL CONSERVATION AREA' near the spot as new id(s) [None] (geometry now: CONFIRMED: live overlap 1587.2 ac vs 1588.8 ac 
- **RECORD CHANGED** `US-2229+US-7363@area@42.914,-115.705`: US-7363: 1 key record id(s) no longer in gis.blm.gov/lands/BLM_Natl_NLCS_NM_NCA_poly/MapServer/0/query: [353] | US-7363: found by name 'MORLEY NELSON SNAKE RIVER BIRDS OF PREY NATIONAL CONSERVATION AREA' near the spot as new id(s) [None] (geometry now: CONFIRMED: live overlap 163.0 ac vs 162.3 ac st

The 2-fer file was not changed. A person and the club waiting room decide.
