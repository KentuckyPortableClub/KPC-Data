# kpc_inspire (T6): test report (2026-10-31)

## Round 4 (Oct 31)

No code change in this tool. The zip now carries `_common/` (polite.py, the tool sources, `build.py`, which no longer hard-codes a /workspace path, and `README.md`). `python3 _common/build.py --check` confirms the shipped file equals its source + polite.py. `--selftest` PASS on Python 3.11.18 and 3.13.5, here, in the KPC-Data mirror and from a fresh unzip. The live run was not repeated.


## Selftest
`python kpc_inspire.py --selftest` prints **PASS** and needs no network. It uses `tests/web.json` and the `tests/web/` fixtures to fake data.europa.eu SPARQL, a disabled CSW, a WFS, ArcGIS, OGC API, and zip files. It checks that:
- K4TEST records land in AT
- a flood "Schutzgebiet" is dropped (not an area)
- a record from another country's catalogue is dropped
- a WMS-only record has no links to open
- a broken WFS shows `opens:false` and the reason
- the Natura 2000 record goes in `"EU"` with `eu_compilation:true`
- `link_kind` cases are right
- banned hosts are refused

The output is compared with `tests/expected/inspire.json`.

## Club decisions applied (Oct 31)
- **One User-Agent:** the crawler-style retry is removed. Only `KPC park tools (<KPC_CONTACT>)` is sent.
- **403 accepted:** no retry. The host goes into `report.json` `blocked_hosts` with the reason, is not asked again this run, and its links stay in `inspire.json` with `opens: false`, `status: "blocked from here"`, `why: "blocked from here (403): 403 Forbidden on <url>"`.
- **2 s per host** (unchanged, now a floor in the code).
- **Spain's national WFS** (`geoserver.iepnb.es`, MITECO ENP and the international-instruments WFS) stays in the list as "blocked from here (403)" for the club to try from GitHub. The selftest checks exactly this.
- **Re-run of AT, DE, ES with the new rules** (warm cache, entries fetched under the old crawler-style name thrown away first): exit 0, about 15 min, 180 requests. **WFS links that open are unchanged: AT 74, DE 51, ES 11**, so all three bars are still met. Three hosts now answer 403 to the honest name and are marked blocked: `e-gov.ooe.gv.at` (3 Oberösterreich zip downloads no longer open), `ideib.caib.es` (the Balearic ArcGIS service no longer opens) and `geoserver.iepnb.es` (already not opening). Links that open in all: 215 before, 211 now.

## Live acceptance: AT, DE, ES
Command: `--areas AT,DE,ES --out runs/t6_oct31 --cache runs/cache_oct31`, exit 0 (Oct 31 re-run with the club decisions; the first acceptance run was `runs/t6b`). The run took about 36 min with a warm SPARQL cache; the first, cold run took about 20 min. Bar: find each country's national or state protected-area WFS.

### AT: met
- 80 records kept out of 135 AT datasets.
- 74 WFS links open; 19 don't; 16 were not opened because the link budget ran out.
- **National:** "Downloaddienst WFS Schutzgebiete Österreich 2025" on haleconnect org.711 opens. Its ATOM and OGC API sister records are listed too.
- **State:** Niederösterreich (sdi.noe.gv.at), Wien (data.wien.gv.at), and several Länder on haleconnect open.
- Oberösterreich's records are listed, but their zip downloads on e-gov.ooe.gv.at are "blocked from here (403)": that host refuses the honest User-Agent.

### DE: met
- 80 records kept out of 919 DE datasets.
- 51 WFS links open.
- **National:** BfN `https://geodienste.bfn.de/ogc/wfs/schutzgebiet` opens, plus `INSPIRE_PS_DE`, the marine and international layers, and NSG_AWZ.
- **State:** 15 hosts open WFS, including Bayern LfU, NRW, BW (LUBW/LGL), SH, Hamburg, Saarland, Sachsen-Anhalt and MV. www.geodaten-mv.de later answered 503 three times and was rested.

### ES: state met; national found but does not open from this box
- 42 records: 34 from data.europa.eu and 8 from the IDEE national CSW.
- **Regional services that open:**
  - 11 WFS links: Madrid (idem.comunidad.madrid, including ENP_ES30), Valencia (terramapas.icv.gva.es) and Bizkaia
  - Catalonia: an OGC API Features service and ATOM feeds for Natura 2000, ENPE and PEIN
  - Illes Balears: the ArcGIS service on ideib.caib.es is listed but "blocked from here (403)"
- **National:** MITECO "Espacios Naturales Protegidos" is found, with WFS `https://geoserver.iepnb.es/geoserver/ENP/wms?service=WFS&request=GetCapabilities`. It is kept in the list with `opens: false` and `status: "blocked from here"` (`why: "blocked from here (403): 403 Forbidden on https://geoserver.iepnb.es/robots.txt"`): that host returns 403 for every path, robots.txt included. This looks like a block on datacenter or non-Spanish IPs; the club will try it from GitHub.
- The MITECO zip downloads on www.mapama.gob.es fail with an SSLError, which looks like an incomplete certificate chain.
- The MITECO Natura 2000 zip on www.miteco.gob.es does open (9.5 MB).
- The fact that iepnb is the national ENP WFS is reported as found, not as working.

### EU list
1 record: "Natura 2000 (vector) - version end 2024", from the EEA catalogue, with `eu_compilation:true`. CDDA did not make the cut because of the 30-id EU limit and the word filter.

## Web totals
- 180 requests and 227 cache hits (Oct 31 re-run)
- robots.txt refused 8; 0 banned
- 26 link errors (each is recorded in `why`)
- 1 rested host
- 3 blocked hosts (403, accepted): e-gov.ooe.gv.at, geoserver.iepnb.es, ideib.caib.es

## Notes and caveats
- **INSPIRE Geoportal** was retired on 1 Jul 2026, so it is not used.
- **data.europa.eu:** robots.txt disallows the GET search pages. The tool sends POST requests to the public `/sparql` endpoint instead, and those are cached.
  - Big joined queries time out at 60 s, so lookups run in three small steps.
- **Translated titles:** data.europa.eu machine-translates every title. The tool keeps only native-language titles plus `en`, because some national records tag a German title as `en`.
- **National CSWs:**
  - AT (geometadatensuche) answers but returns 0 for "Schutzgebiet". It may not index AnyText.
  - DE GDK fails with an SSLError.
  - ES IDEE works with an OGC Filter. CQL with `%` crashes its Java server, so the tool now sends FILTER encoding.
- **Publisher** is blank on many AT/DE records, where data.europa.eu has no `dct:publisher` for the dataset.
- **User-Agent (settled, Oct 31):** no second User-Agent; a 403 is accepted and the host marked blocked.
- **Link budget:** 60 opened per country, so some links show `opens:null` (not tried).

## Oct 31 (round 3): robots.txt rule, same as kpc_parcels
- Changed in the shared polite reader (`_common/polite.py`, built into this file by `_common/build.py`): a 403 (or any other 4xx) on `robots.txt` alone now means **no robots rules** (RFC 9309 s2.3.1.3) and the host is still read. Only a 403 on a data request marks the host blocked, with no retry, and its links keep `status: "blocked from here"`.
- Selftest: new polite cases (robots.txt answering 401 / 403 / 404 / 451 must not block; a 403 on data must block with no retry). The existing Spain case (403 on the data itself) still reads "blocked from here (403)". `python kpc_inspire.py --selftest`: **PASS** on Python 3.11.18 and 3.13.5. A mutation check (putting the old rule back) makes it FAIL.
- **The AT / DE / ES live run above was NOT re-run** with this change. Its numbers are from before it. geoserver.iepnb.es answered 403 on every path, so it should stay blocked; e-gov.ooe.gv.at and ideib.caib.es may differ if only their robots.txt refused.
