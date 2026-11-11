# kpc_parcels (T4): who owns the land under a park pin

For parks with no official park layer, this tool finds the county's own parcel map. It then reads the parcel under the POTA pin:
- parcel id
- acres
- owner type (government / private / unknown, by keywords)
- the other parcels with the same owner within 1 km

When the pin's parcel is not a government's, it also lists government parcels within 300 m. It decides nothing.

How it looks for a parcel layer, in order:
1. `--known`
2. the state's own statewide service (Texas StratMap)
3. an ArcGIS Online search for "<County> County parcels", kept only for government publishers whose item covers the pin
4. that government's own list of services

A layer counts only if the pin actually falls on one of its parcels. A zoning layer (name, title or address says zoning / zone) or a building damage-assessment layer never counts: zoning is not ownership. Warren County, KY (21227) is skipped by club decision until a real parcel layer turns up (a person can give one with `--known`).

```
pip install -r requirements.txt          # Python 3.12
export KPC_CONTACT="K4TEST <k4test@example.org>"
python kpc_parcels.py --parks parks.json --known data/intake/parcel-layers.json --out out/ --cache cache/
python kpc_parcels.py --selftest         # no network, prints PASS or FAIL
```

Input formats:
- `parks.json`: `[{"ref":"K4TEST-0001","name":"…","lat":37.5,"lon":-85.0,"county_fips":"21111"?}]`. CSV with the same columns also works.
- `--known`: `{fips: layer_url}`, or a `parcel-layers.json` from an earlier run.

Output:
- `parcels.json`: `{ref:{county, layer_url, owner, owner_type, parcel_id, acres, same_owner_parcels:[{parcel_id,acres,dist_m}], why, source_url, read_date, nearby_government_parcels?, owner_withheld?}}`
- `parcel-layers.json`: `{fips:{layer_url,county,source_url,read_date,why}}`. Feed it back as `--known`.
- `report.json` and `state.json`

**Privacy (club rule 9, club decision Oct 31):** an owner name is written only when it is a government body (city, county, state, federal, school / utility bodies). A private owner is written only as `"owner": "private"` (with `"owner_withheld": true`), never with the name. An owner of unknown type is not written either (`"owner": null, "owner_withheld": true`). `same_owner_parcels` holds only parcel ids, acres and distances, never names; `nearby_government_parcels` holds only government names. There is no option that writes a private name (`--owner-names all` is gone). `--owner-names none` (or `--no-owner-names`) also drops government names. Parcel replies are never put in `--cache`.

Flags: `--max-minutes 50`, `--resume`, `--limit`, `--areas US-KY,US-TX`, `--max-tries 6`.

Exit codes: 0 done, 3 time out, 2 bad input. One bad pin never stops the run.

Manners: same polite reader as the other KPC tools (robots.txt, at least 2 s per host, always the one `KPC park tools (<KPC_CONTACT>)` UA, 429/503 back-off). A 403 on a data request is accepted with no retry; the host is marked blocked with the reason in `report.json` (`blocked_hosts`). On a shared ArcGIS Online host only the refused address is dropped. A 403 (or other 4xx) on `robots.txt` alone is not a block: per RFC 9309 it means there are no robots rules, so the layer is still read (club decision, Oct 31). No keys.

## Club decisions applied (Oct 31)
- Owner names: government names only; a private owner is written as `"private"`; unknown-type owners are not written; `--owner-names all` removed.
- Removed the retry with a crawler-style User-Agent; a 403 is accepted and the host marked blocked.
- Oct 31 (parcel tracer decisions): a 403 on robots.txt alone no longer marks anything blocked (RFC 9309: no robots rules; only a refused data request blocks a host). Government owner keywords added: Division of Natural Resources, Department of Conservation, Fish and Wildlife, Game Commission, Water Management District, Conservation Authority, Parks and Recreation (punctuation, abbreviations and '&' variants count). Selftest cases added for both; PASS.
- Oct 31 (round 3): an owner name with NATURAL RESOURCES + a state / province word (misspellings allowed, DIVISION spelled any way) is that state's agency, a government owner (`nr_agency()`); the shared polite code is now one source (`_common/polite.py`) built into each tool.
- At least 2 s between requests to one host.
- Zoning layers are never a parcel source; Warren County, KY is skipped until a real parcel layer turns up.

## Shared source (`_common`)

The polite web reader (User-Agent, 2 s per host, robots.txt, 403 handling, cache) is one shared file, `_common/polite.py`, built into this tool from `_common/t4_src.py` by `_common/build.py`. The zip carries `_common/`. Edit the source there, never the built `kpc_parcels.py`, then run `python3 _common/build.py` (or `--check` to only compare) and this tool's `--selftest`.

## Nov 11 (KPC owner, 2026-11-11)
- The never-contact guard of Data #63 (services*.arcgis.com, apps.fs.usda.gov: no request of any kind, robots.txt included) now lives in the shared `_common/polite.py`, so `_common/build.py` keeps it, and kpc_sitemaps, kpc_inspire and kpc_trail_lines have it too.
- A search hit on a never-contact host is dropped before it is tried, so it no longer uses up `--max-tries`; a hit (or a service in a government server's list) whose own title / name / address names only another state is dropped the same way (Indiana's statewide parcels for a Kentucky county). A "no layer" reason says how many of each were skipped. What counts as a parcel layer is unchanged: a government publisher, not zoning, and the pin falls on one of its parcels.
