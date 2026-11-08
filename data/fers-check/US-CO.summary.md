# 2-fer accuracy check: US-CO

Run 2026-11-01T11:54:01Z → 2026-11-08T06:25:41Z (UTC) · tool 0.1.0 (2026-10-31) · complete
Live rows in the file: 57 · checked: 57 · skipped (dropped / merged): 700

| verdict | rows |
|---|---|
| CONFIRMED | 39 |
| SHRUNK | 4 |
| GREW | 3 |
| MOVED | 1 |
| RECORD CHANGED | 8 |
| NOT CHECKED | 2 |

| flag | rows |
|---|---|
| small overlap (under 50 yd across) | 15 |
| trail line from the club saved copy (not re-read live) | 7 |
| water-only | 5 |

## For a person to look at

- **SHRUNK** `US-12682+US-4575@trail@38.496,-107.029`: live overlap is 59% smaller (1.3 ac vs 3.2 ac stored)
- **SHRUNK** `US-12683+US-4575@trail@38.496,-107.029`: live overlap is 59% smaller (1.3 ac vs 3.2 ac stored)
- **SHRUNK** `US-4410+US-9619@area@39.832,-106.220`: live overlap is 36% smaller (2.3 ac vs 3.6 ac stored)
- **SHRUNK** `US-4579+US-9639@trail@38.083,-102.261`: only 47% of the stored overlap is still inside the live overlap (10 m tolerance)
- **GREW** `US-0033+US-4407@area@37.698,-105.480`: live overlap is 81% bigger (4.4 ac vs 2.4 ac stored); 99% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-11938+US-4406@area@40.784,-105.553`: live overlap is 147% bigger (1.4 ac vs 0.6 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-4407+US-8295@area@37.698,-105.480`: live overlap is 81% bigger (4.4 ac vs 2.4 ac stored); 99% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **MOVED** `US-0223+US-9625@same land@40.880,-109.032`: live overlap centre is 470 m from the stored centre; 9% of the stored overlap is still inside it
- **RECORD CHANGED** `US-0222+US-1239@area@37.721,-105.777`: US-1239: record sgcoc719 renamed: key 'San Luis Lakes SWA' -> live 'San Luis Lakes STL' (geometry now: CONFIRMED: live overlap 8.5 ac vs 8.8 ac stored (-4%), 100% of the stored overlap still inside (10 m tolerance))
- **RECORD CHANGED** `US-11884+US-11952@area@38.687,-108.986`: US-11884: 1 key record id(s) no longer in gis.blm.gov/lands/BLM_Natl_NLCS_WLD_WSA/MapServer/1/query: [29863] | US-11884: found by name 'The Palisade' near the spot as new id(s) [None] (geometry now: CONFIRMED: live overlap 32.9 ac vs 33.1 ac stored (-0%), 100% of the stored overlap still inside (10 
- **RECORD CHANGED** `US-11890+US-1223@area@39.058,-108.482`: US-1223: record sgcoc431 renamed: key 'James M. Robb - Colorado River State Park - 34 Road section' -> live 'James M. Robb - Colorado River State Park' | US-1223: record sgcoc434 renamed: key 'James M. Robb - Colorado River State Park - Fruita section' -> live 'James M. Robb - Colorado River State P
- **RECORD CHANGED** `US-11916+US-11952@area@38.287,-108.881`: US-11916: 2 key record id(s) no longer in gis.blm.gov/lands/BLM_Natl_NLCS_WLD_WSA/MapServer/1/query: [29848, 29867] | US-11916: found by name 'Dolores River Canyon' near the spot as new id(s) [None] (geometry now: CONFIRMED: live overlap 13391.1 ac vs 13543.9 ac stored (-1%), 96% of the stored overl
- **RECORD CHANGED** `US-11939+US-4406@area@40.694,-105.680`: US-11939: record sgcoc642 renamed: key 'Poudre River STL' -> live 'Poudre River SFU' (geometry now: CONFIRMED: live overlap 1.2 ac vs 1.2 ac stored (-3%), 99% of the stored overlap still inside (10 m tolerance))
- **RECORD CHANGED** `US-13569+US-4408@area@37.335,-107.933`: US-13569: record sgcoc613 renamed: key 'Perins Peak SWA - Decker Tract' -> live 'Perins Peak SWA' (geometry now: CONFIRMED: live overlap 2.6 ac vs 2.4 ac stored (+9%), 100% of the stored overlap still inside (10 m tolerance))
- **RECORD CHANGED** `US-4402+US-9592@area@38.069,-107.156`: US-9592: 1 key record id(s) no longer in gis.blm.gov/lands/BLM_Natl_NLCS_WLD_WSA/MapServer/1/query: [31102] | US-9592: 1 key record id(s) no longer in gis.blm.gov/lands/BLM_Natl_NLCS_WLD_WSA/MapServer/0/query: [4351] | US-9592: found by name 'Powderhorn' near the spot as new id(s) [None] (geometry n
- **RECORD CHANGED** `US-4575+US-9648@trail@38.752,-108.157`: US-9648: record sgcoc324 renamed: key 'Escalante SWA - Harrison Tract' -> live 'Escalante SWA - Hamilton Tract' (geometry now: CONFIRMED: live overlap 2.4 ac vs 2.0 ac stored (+19%), 100% of the stored overlap still inside (10 m tolerance))
- **NOT CHECKED** `US-11895+US-4404@area@39.227,-105.612`: key has no joined official outline for US-4404 (status 'pin')
- **NOT CHECKED** `US-4404+US-9605@area@39.347,-106.065`: key has no joined official outline for US-4404 (status 'pin')

The 2-fer file was not changed. A person and the club waiting room decide.
