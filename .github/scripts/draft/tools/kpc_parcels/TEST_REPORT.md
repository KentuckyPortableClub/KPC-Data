# kpc_parcels (T4): test report, 2026-10-31

## Round 4 (Oct 31)

No code change in this tool. The zip now carries `_common/` (polite.py, the tool sources, `build.py`, which no longer hard-codes a /workspace path, and `README.md`). `python3 _common/build.py --check` confirms the shipped file equals its source + polite.py. `--selftest` PASS on Python 3.11.18 and 3.13.5, here, in the KPC-Data mirror and from a fresh unzip. The live run was not repeated.


## Selftest
`python kpc_parcels.py --selftest` prints **PASS** with no network. It uses a fake county server (`tests/web.json`) and three pins:
- **K4TEST-01** is on a `CITY OF K4TEST` parcel. The owner name is written, plus one same-owner parcel.
- **K4TEST-02** is on a `K4TEST PRIVATE PERSON` parcel. The owner is written only as `"private"`, and the nearby `K4TEST COUNTY FISCAL COURT` parcel 155 m away is listed.
- **K4TEST-03** is a bad row. It is reported and never stops the run.

The test also checks that the private name never appears in any output file, plus the owner-type keywords and the banned-source check. Since Oct 31 it also checks: a zoning layer is refused as a parcel source, Warren County KY is skipped, `--owner-names all` no longer exists, the one honest User-Agent, at least 2 s per host, and that a 403 is accepted (no retry) and the host marked blocked.

## Club decisions applied (Oct 31)
- **Owner names:** government names only. A private owner is written only as `"private"`. An owner of unknown type is not written (`null`, `owner_withheld: true`), to be safe. `--owner-names all` is removed, so no run can write a private name.
- **One User-Agent:** the crawler-style retry is removed. A 403 is accepted, not retried, and the host is marked blocked with the reason in `report.json` (`blocked_hosts`). On shared ArcGIS Online hosts (`services*.arcgis.com`) the 403 was only ever on `robots.txt`; only that address is marked, and the parcel layers there still open with the honest name.
- **2 s per host** (unchanged, now a floor in the code).
- **Zoning is not ownership:** a layer whose name, title or address says zoning / zone is never used. Warren County, KY is skipped with a reason. With the zoning layer gone, the next candidate the search found for Warren was a City of Bowling Green building damage-assessment form layer (`AssessmentForms_gdb/ATC45Parcel`), also not ownership, so such layers are refused too.
- **Re-run of the 20 pins with the new rules** (warm cache, entries fetched under the old crawler-style name thrown away first): exit 0, 62 requests, 0 errors.
- **Correction:** the earlier report said 17/20 (KY 7/10). The run itself had 16/20 (KY 6/10). That was a miscount in the report.

## Live run: 20 pins (`tests/live_20.json`), exit 0 (numbers from the Oct 31 re-run with the club decisions)
- **TEST-KY-01..10** are 10 Kentucky city parks. Their pins are PAD-US interior points, *not POTA pins*, because these parks have no POTA refs to borrow pins from.
- **10 POTA Texas Historical Commission sites** (US-3500, US-6543…US-6607) use their real POTA pins.

| Bar | Result |
|---|---|
| ≥70% of counties get a parcel layer | **15/20 = 75%** (KY 5/10, TX 10/10). Before the club decisions: 16/20, with Warren's zoning layer counted. |

**Owner field.** 11 of the 15 layers give an owner field: all 10 TX (StratMap) plus Kenton KY. The other 4 KY layers (LOJIC, Lexington, Hardin, Henderson) publish parcel ids and acres but **no owner names**, so those parks are `owner_type: unknown`.

**Pins on a private parcel.** 1 of 20. Fort Griffin SHS (US-6557) falls on a parcel the keywords call private (written as `"private"`). No government parcel lies within 300 m of the pin. The other 9 TX sites are on TEXAS HISTORICAL COMMISSION / STATE OF TEXAS / TPWD land.

**Kentucky counties with no layer:**
- Warren (skipped by club decision: its only layers are zoning and a damage-assessment form layer)
- Daviess
- Calloway
- Franklin
- Boyd

**Kentucky layers found, with notes:**
- Jefferson: LOJIC (government host)
- Fayette: the Lexington-Fayette UCG organisation
- Hardin: Hardin County Online GIS
- Kenton: LINK-GIS. Devou Park shows as COVINGTON CITY OF (DEVOU PARK), government.
- Henderson: the Henderson KY GIS organisation, which was accepted because the organisation is named after the county or town

## Things for Brandon to know or decide
1. **Privacy (settled, Oct 31).** Government owner names are written (e.g. TEXAS HISTORICAL COMMISSION); a private owner is written only as `"private"`; unknown-type owners are not written. `--owner-names none` drops government names too.
2. **The cache never holds parcel replies** (`nocache=True`). Only public catalogue replies are cached: Census county lookups, searches, layer info.
3. **The ArcGIS REST robots exemption** follows the club HQ precedent of Oct 27 (`rest_exempt`). Some county servers' robots.txt disallow `/arcgis/rest/services`, but those are public map APIs. Count: 0 in this run.
4. **User-Agent (settled, Oct 31).** Only `KPC park tools (<KPC_CONTACT>)`. services*.arcgis.com answers its `robots.txt` with 403 to that name; the tool accepts it (no robots rules read there) and the layers themselves open normally.
5. **Owner type is by keywords only:** CITY OF, COUNTY, COMMONWEALTH, STATE OF, COMMISSION, … for government; LLC, PROPERTIES, or a person-like name for private. Treat it as a hint, not a decision.
6. **The search depends on ArcGIS Online.** Counties that publish only on their own site with no ArcGIS Online item (Calloway, Boyd) will need a `--known` entry from a person.

## Oct 31 update (parcel tracer decisions)

- **robots.txt 403 is no longer a block.** RFC 9309 says an unavailable robots.txt means no robots rules. Before this change, the robots.txt address was marked blocked (and on a non-shared server the whole host). Now only a 403 on a data request blocks a host, with no retry. A new polite selftest case checks that a host answering 403 only on robots.txt is still read and not blocked.
- **Government owner keywords added** (shared with kpc_parcel_trace): Division of Natural Resources, Department of Conservation, Fish and Wildlife, Game Commission, Water Management District, Conservation Authority, Parks and Recreation. Punctuation, abbreviations (DIV., DEPT., NAT. RES., COMMISSN, DIST, REC) and `&` variants count. Selftest cases were added.
- `python kpc_parcels.py --selftest`: PASS on Python 3.11 and 3.13. The 20-park live test was not re-run for this change.

## Oct 31 update, round 3

- **"Natural Resources" + a state word = the state's agency.** A new rule in `owner_type` (`nr_agency()`): an owner name that has NATURAL RESOURCES (or NAT RES) next to a US state or Canadian province name counts as government, and the word for DIVISION can be spelled any way (DIVISON, DIVSISION, DIV, DEPT, or left out). Misspellings are allowed: 1 letter wrong in words of 6-7 letters, 2 in words of 8 or more (adjacent swaps count as one), same first letter, exact for 5 letters or fewer (IOWA, OHIO, TEXAS). Examples: NATUARL, RESOURSES, VIRGININA. The longest state name wins, so WEST VIRGINIA beats VIRGINIA. A few short forms count (W VA, WVA, WV, VA, KY, TENN, PENN, ONT, BC, ...). Two-letter postal codes that are also words (IN, OR, ME, ...) do not. A name with a company word (LLC, INC, TRUST, ...) is never the agency. Selftest cases added.
- **The shared polite reader** now lives as the one source `_common/polite.py`. kpc_parcels, kpc_sitemaps and kpc_inspire are rebuilt from it with `_common/build.py`, so all three carry the same robots.txt rule. The polite selftest gained cases: robots.txt answering 401 / 403 / 404 / 451 is not a block, and a 403 on data is.
- `python kpc_parcels.py --selftest`: **PASS** on Python 3.11.18 and 3.13.5. The 20-park live test was **not** re-run for this change.
