# kpc_link_fix (T2): test report

Run on 2026-10-31 (America/Chicago) on the shared Linux box with Python 3.12 and the pinned requirements.txt.
Every number below comes from those runs.

## Self test (offline)
`python kpc_link_fix.py --selftest` prints **PASS** (12 ok lines, 0 FAIL). It uses `tests/fake_site.json`, a fake
agency site with 6 K4TEST dead links, and checks each one:
- found in the sitemap under the same file name;
- found under the same name with the dates and version words removed;
- a wrong-park trap: the file is there but names another park, so the answer is null;
- found on the parent page;
- an AllTrails link: banned, so the answer is null;
- a brochure found on the park's page.

It also checks the name cleaner, the soft-404 test and the banned-source list (AllTrails refused, a government
cloud file allowed).

## Live test: the 3 dead trail maps (spec test)
Input is `tests/dead3.json`. Output went to `runs/t2_dead3/`. The run used 78 web requests and took about 1.5 minutes.

| ref | old link | result |
|---|---|---|
| US-2350 Prairie Spirit | ksoutdoors.com/content/download/28328/…/MAP+B&W+PRAIRIE+SPIRIT+TRAIL+SP.pdf (the real old link, from the Wayback index) | **null**: ksoutdoors.com now redirects to ksoutdoors.gov, which answers HTTP 403 to every plain (non-browser) reader, including a browser User-Agent. The sitemap gave 0 addresses and the pages couldn't be read. |
| US-7836 Ozark Trail | mostateparks.com/sites/mostateparks/files/OzarkTrailBrochure.pdf (stand-in, see gaps) | **null**: the mostateparks.com search is disallowed by robots.txt; the ozarktrail.com sitemap (218 addresses) had no matching file; the parent pages had nothing that named the park. |
| US-9753 Rock Island | mostateparks.com/sites/mostateparks/files/Rock-Island_Leg_Booklet_FINAL.pdf (stand-in) | **fixed**: https://mostateparks.com/park/rock-island-trail-state-park/map. Found on the park's page, confidence 0.45; it opens (200) and names "Rock Island Trail State Park". It is the park's map **web page**, not a PDF. The page shows 2 map pictures for a person to look at (RIT_FullTrail_WEB.png, region-map-small-pastel.png). |

**Acceptance: fixes ≥1 of 3. Met, 1 of 3.** The one fix is a web page, not the map file, and its confidence (0.45)
says so. **Never returns a link that does not name the park: met.** No candidate was returned without passing the
"names the park" check, and in the self test the wrong-park trap stayed null.

## Known gaps / not tested
- **The exact dead links chat 8 found are not stored** in KPC-Data or KPC-Links (chat-10.md only names the
  parks). US-2350 uses the real old address from the Wayback index. US-7836 and US-9753 use old mostateparks.com PDF
  addresses from the Wayback index that 404 now. Those are stand-ins, not necessarily chat 8's links.
- **ksoutdoors.gov blocks non-browser readers (HTTP 403)**, so no Kansas link can be fixed by this tool. The docs
  already mark that host "needs_browser". The tool doesn't use a browser on purpose.
- **Map pictures (PNG/JPG) can't be read for the park's name.** There is no OCR on the box, so they go to
  `pictures_for_a_person` instead of being returned.
- The site search runs only where robots.txt allows it. mostateparks.com disallows `/search`.
- The tool has not been run on a big batch of docs rows with a 404/410 status (none were handed over). Speed and
  hit rate on a big batch are unknown.
