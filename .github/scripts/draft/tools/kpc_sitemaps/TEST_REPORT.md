# kpc_sitemaps (T3): test report, 2026-10-31

## Round 4 (Oct 31)

No code change in this tool. The zip now carries `_common/` (polite.py, the tool sources, `build.py`, which no longer hard-codes a /workspace path, and `README.md`). `python3 _common/build.py --check` confirms the shipped file equals its source + polite.py. `--selftest` PASS on Python 3.11.18 and 3.13.5, here, in the KPC-Data mirror and from a fresh unzip. The live run was not repeated.


## Selftest
`python kpc_sitemaps.py --selftest` prints **PASS** under Python 3.12 with no network. The fixture site in `tests/` covers:
- robots.txt with a `Sitemap:` line pointing to a sitemap index
- a gzipped child sitemap and an image sitemap
- a maps page from the agency list, plus a one-step park page
- three fake parks (K-ZZ01..03)

The output must equal `tests/expected/parks.example.gov.json`.

## Club decisions applied (Oct 31)
- **One honest User-Agent only.** The retry with a crawler-style User-Agent is gone. Every request sends exactly `KPC park tools (<KPC_CONTACT>)`.
- **A 403 is accepted.** No retry. The host is marked `blocked` with the reason (`403 Forbidden on <url>`) in `report.json` (`hosts.<host>.status` and `blocked_hosts`), and the tool goes on with the next host.
- **2 seconds between requests to one host** (already the case; now also enforced as a floor in the code and checked by the selftest).
- Re-run on US-TN with the new rules (warm cache, entries fetched under the old crawler-style name thrown away first). **Result:** still 21/26 = 81%, same five misses. Map files drop from 602 to **383**, still well over the bar of 50, because tnstateparks.com and www.tn.gov now answer 403 to the honest name and are marked blocked.

## Live acceptance run: US-TN
Command: `--in KPC-Data/data/intake/us-agency-maps-index.csv --docs KPC-Data/data/docs --parkinfo KPC-Data/data/parkinfo --areas US-TN`. 10 hosts, exit 0. Measured with `_common/t3_measure.py`. Numbers below are from the Oct 31 re-run with the club decisions applied.

| Bar | Result |
|---|---|
| ≥80% of the club's own TN map links (docs/US-TN.json) found | **21/26 = 81%** (13 from sitemaps, 8 from one-step reads) |
| ≥50 map files | **383** map files (PDF/JPG/PNG) naming a TN park; 1,264 map items in all (before the club decisions: 602 and 1,503) |

Sitemaps alone (`--follow 0`) give 13/26 = 50%, which misses the bar. The one-step reads are what bring it to 81%.

The 5 misses, and why each one is out of reach:
- `hmdb.org/results.asp?Search=…`: a search-results page, not a map. It is in no sitemap.
- `murfreesborotn.gov/DocumentCenter/View/370`: Cloudflare answers robots.txt with 403. The host is marked blocked, and the tool does not try to get around it.
- `nashville.gov/…BeamanBrochure….pdf`: the site's sitemap.xml is broken. It lists one URL, `http://default//`.
- `fs.usda.gov/r08/cherokee/maps-guides`: not in the 48,126-URL sitemap the tool read.
- `trails.nc.gov/maps/map-pdfs-mountains-sea-state-trail/open`: not in the sitemap. The tool found the trail's page, but not this link.

Hosts read:

| Host | Status | URLs | Maps | Pages |
|---|---|---|---|---|
| tnstateparks.com | blocked (403 Forbidden on robots.txt) | 0 | 0 | 0 |
| nps.gov | ok | 190,377 | 744 | 14 |
| fws.gov | ok | 11,623 | 478 | 110 |
| fs.usda.gov | ok | 48,126 | 27 | 0 |
| landbetweenthelakes.us | ok | 863 | 97 | 43 |
| trails.nc.gov | ok | 39 | 37 | 0 |
| hmdb.org | ok | 290,574 | 4 | 0 |
| tn.gov | blocked (403 Forbidden on robots.txt) | 0 | 0 | 0 |
| nashville.gov | broken sitemap | 1 | 0 | 0 |
| murfreesborotn.gov | blocked (Cloudflare 403) | 0 | 0 | 0 |

## Things for Brandon to know or decide
1. **Blocked hosts (settled, Oct 31).** tnstateparks.com and tn.gov refuse the honest User-Agent with 403 (their firewalls want a browser-like name). Per the club decision the tool accepts that and marks them blocked. Their map files (287 + 21 before) are no longer found from here.
2. **Rate and name (settled, Oct 31).** 2 s per host, User-Agent `KPC park tools (<KPC_CONTACT>)`.
3. **fws.gov robots.txt** has `Disallow: *page=`, which blocks its paginated sitemaps (`?page=2`…). The tool obeys this. It reaches the refuge `/map` pages through one-step reads from the refuge pages instead.
4. **Matching is by words.** `refs` lists every candidate park with a score. Paths learned from the club's own links (e.g. nps `/cuga/`, fws `/refuge/chickasaw`) score 1.0. National hosts (nps, fws, fs.usda, hmdb) keep only URLs that name a park in `--areas`.
5. **http:// URLs** are tried as https first, because tnstateparks.com returns 500 on http.
6. **Rerun time:** about 10–15 minutes per state with an empty cache; the big sitemaps (nps, hmdb) dominate.

## Oct 31 (round 3): robots.txt rule, same as kpc_parcels
- Changed in the shared polite reader (`_common/polite.py`, built into this file by `_common/build.py`): a 403 (or any other 4xx) on `robots.txt` alone now means **no robots rules** (RFC 9309 s2.3.1.3) and the host is still read. Only a 403 on a data request (a sitemap, page or map file) marks the host `blocked`, with no retry. Before, a 403 on robots.txt marked the whole host blocked.
- Selftest: new cases (robots.txt answering 401 / 403 / 404 / 451 must not block and the next request must go out; a 403 on data must block with no retry). `python kpc_sitemaps.py --selftest`: **PASS** on Python 3.11.18 and 3.13.5. A mutation check (putting the old rule back) makes it FAIL.
- **The US-TN live acceptance run above was NOT re-run** with this change. Its numbers are from before it. tnstateparks.com and tn.gov were listed as "blocked (403 Forbidden on robots.txt)": they will now be asked for their sitemaps. If they also refuse the data with 403 they stay blocked; if not, the map-file count can go up. murfreesborotn.gov (Cloudflare 403 on robots.txt) is in the same position.
