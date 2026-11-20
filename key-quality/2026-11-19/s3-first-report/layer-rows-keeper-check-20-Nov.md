# The 156 layer rows against the keeper's store (Opus, 20 Nov 2026)

Plan step 2b asked whether the keeper (KPC-Store) can write its own records into the saved copies for the 156 rows of
`ready-report-round3.json` (27 hand, 68 missing, 61 short). Read from files only; nothing fetched, nothing built, no copy changed.

Inputs: the 50 US saved copies on KPC-Links' boundary-cache release (read 20 Nov ~6 AM CST); the 51 US store files on
KPC-Store `store-data` e9856be (keeper run of 19 Nov); KPC-Store `engine/verified-layers.csv` at main ba25064;
KPC-Links `data/state-gis.json` at main.

**Result: the keeper can add 0 records to any of the 156 rows.** Every record the store holds for these layers is already in
the copy. The store keeps only the records joined to parks, not whole layers.

| Reason (column `reason`) | hand | missing | short | All |
|---|---|---|---|---|
| withheld (the store's licence row says publishable = no) | 22 | 26 | 2 | 50 |
| same layer under another id (the copy holds it under the id the key first gave that address; the report counts it under the state's own id) | 3 | 27 | 4 | 34 |
| keeper holds only joined records (all already in the copy; the rest of the layer was never fetched by the keeper) | 0 | 0 | 39 | 39 |
| not on the keeper list (the address is not in verified-layers.csv) | 0 | 14 | 16 | 30 |
| keeper holds none here | 2 | 1 | 0 | 3 |
| keeper can add | 0 | 0 | 0 | **0** |

The two hand downloads: the Army Corps layer is withheld (licence not recorded); the NPS tract layer is in the copies under
`sgakd` where the keeper has it (HI, NY, SD), and the keeper holds none of it in CA and TX.

The layers report was not rerun: no copy changed, so it would give round 3's numbers again.
