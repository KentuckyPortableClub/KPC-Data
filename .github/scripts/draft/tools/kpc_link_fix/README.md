# kpc_link_fix (T2): dead-link fixer

Give it the official map/page links that now answer 404, 410 or "page not found". For each one, it looks for the
same document at its new address on the same agency's site, in this order:
1. the site's sitemap: T3's `sitemaps/<host>.json` if there is one, otherwise it reads the sitemap itself and
   saves it in T3's shape under `out/work/sitemaps/`. It tries the same file name, then the same name without
   dates or version words, then a close name.
2. the Wayback Machine, used only to read the old page's words, never as an answer.
3. the site's own search page, if robots.txt allows it.
4. the parent folder and the park's own page, looking for links with matching words. For a map, the link
   must look like a map document.

A new link is given only when it opens (HTTP 200, not a soft 404) **and** its PDF first page or page text
names the park. Otherwise `new_url` is null and `why` says what was tried. Image candidates can't be read,
so they are listed under `pictures_for_a_person`.

Install: `python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt`. Set `KPC_CONTACT` for the User-Agent.

Example:

```
KPC_CONTACT=k4test@example.org python kpc_link_fix.py --links dead_links.json \
  --parkinfo KPC-Data/data/parkinfo --docs KPC-Data/data/docs/*.json \
  --sitemaps t3_out/ --cache ~/.kpc_cache --out out/ --max-minutes 50 --resume
```

`dead_links.json` = `[{"ref": "K4TEST-1", "url": "https://agency.example.gov/maps/old_map_2019.pdf", "kind": "map", "agency_host": "agency.example.gov"}]`
(optional fields: `name`, `alt_names`, `page`).

Output: `out/link_fix.json` = `{old_url: {ref, kind, new_url, how, confidence, opens, names_park, checked, tried[],
checked_candidates[], source_url, read_date, why}}`, plus `summary.json` and `run_log.txt`. Exit codes: 0 done,
3 out of time (`--resume`), 2 bad input. Self test, offline: `python kpc_link_fix.py --selftest`.
