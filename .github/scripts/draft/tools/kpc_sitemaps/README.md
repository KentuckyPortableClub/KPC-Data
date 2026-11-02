# kpc_sitemaps (T3): read agency sitemaps for map files and park pages

Reads each agency's own sitemap (robots.txt `Sitemap:` lines, then `/sitemap.xml`, `/sitemap_index.xml`, gzip, image sitemaps). It lists every URL that looks like a map (PDF, image, `…/map`, brochure, trail guide) or a park's own page, with **every** POTA park the URL might belong to (`refs:[{ref,score}]`). It decides nothing.

Two small extras fill gaps the sitemaps leave. The tool reads the agency's maps page from the club's agency list once. It also opens up to `--follow` (default 150) park or map pages that the sitemap lists, once each, for the map files they link. Every URL's `why` says which of the three routes found it.

```
pip install -r requirements.txt          # Python 3.12
export KPC_CONTACT="K4TEST <k4test@example.org>"
python kpc_sitemaps.py --in data/intake/us-agency-maps-index.csv --docs data/docs \
    --parkinfo data/parkinfo --areas US-TN --out out/ --cache cache/
python kpc_sitemaps.py --selftest        # no network, prints PASS or FAIL
```

Output:
- `out/sitemaps/<host>.json` = `{host, read_date, n_urls, maps:[{url,lastmod,refs:[{ref,score}],words}], pages:[...]}`
- `out/sitemaps/<host>.sources.json` = `{url: {source_url, read_date, why}}`
- `out/report.json`: one line per host, with the reason when a host failed
- `out/state.json`: used by `--resume`

Flags: `--max-minutes 50`, `--resume`, `--limit N` (hosts), `--areas US-TN,US-KY`, `--cache DIR`, `--follow N` (0 = sitemaps and the agency maps page only), `--no-index-pages`.

Exit codes: 0 done, 3 time ran out (run again with `--resume`), 2 bad input. A host that fails is written to report.json and never stops the run.

Manners: obeys robots.txt (including Crawl-delay), at least 2 s between requests to one host, and always the one User-Agent `KPC park tools (<KPC_CONTACT>)`, never another. On a 429 or 503 it retries 3 times, then rests the host. A 403 on a data request is accepted with no retry: the host is marked `blocked` with the reason in `report.json` (`blocked_hosts`), and the run goes on. A 403 (or any other 4xx) on `robots.txt` alone is not a block: per RFC 9309 it means there are no robots rules, so the host's sitemaps and pages are still read (club decision, Oct 31). It never reads the banned sources. It writes only inside `--out` (and `--cache` if you give one).

## Club decisions applied (Oct 31)
- Removed the retry with a crawler-style User-Agent. Only `KPC park tools (<KPC_CONTACT>)` is ever sent.
- A 403 on data is accepted: no retry, host marked `blocked` with `403 Forbidden on <url>`. A 4xx on robots.txt alone = no robots rules, keep reading (RFC 9309; Oct 31).
- At least 2 s between requests to one host (checked by `--selftest`).

## Shared source (`_common`)

The polite web reader (User-Agent, 2 s per host, robots.txt, 403 handling, cache) is one shared file, `_common/polite.py`, built into this tool from `_common/t3_src.py` by `_common/build.py`. The zip carries `_common/`. Edit the source there, never the built `kpc_sitemaps.py`, then run `python3 _common/build.py` (or `--check` to only compare) and this tool's `--selftest`.
