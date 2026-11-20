KPC LINK IDS  (version 2026-11-20a)
===================================

WHAT IT ANSWERS
  What does each park's POTA web link say about the park, without opening the website?

WHY IT MATTERS
  POTA made the link, not a name match. So it is an independent tie between the park number and the agency's own page.

WHAT IT READS
  Only the parks list already saved in KPC-Data: data/parkinfo (one file per state or country).
  Optional: the public key files in KPC-Links: data/us-key (for the name check).

WHAT IT NEVER DOES
  - It opens no website and downloads nothing. There is no network code in the file.
  - It changes no input file. It writes only into a new folder: link-ids-out\link-ids-<date>-<time>

WHAT IT WORKS OUT FOR EVERY PARK
  agency        whose website it is
  page kind     own page / shared link / home page / document / page not confirmed / not an agency site / no link
  id kind       what sort of id the address holds, for websites that have a rule (22 kinds so far)
  id value      the id itself
  usable        yes only when: the park's own page, a known id, no other park has that id, website in the park's state
  web name      the agency's own words for the place, read from the address
  name match    does that fit the park's POTA name: strong / part / none
  web kind      the kind of place the address says it is, and whether that agrees with POTA's type
  state check   is the website's state the park's state

THE NAME CHECK (only with the key folder)
  A CHECK, never a match. It lists every joined record whose full name is ANOTHER park's own name in the same state.
  Short forms are spelled out first (WMA = wildlife management area, SP = state park), because many map records use
  the short form. That is why it finds pairs a plain full-name test misses.
  The list (PRIVATE-name-flags.csv) names parks and records. Keep it with the store. Only its counts go public.

HOW TO RUN IT
  1. Put the four files in one folder on the PC.
  2. Double-click run-self-test.bat. It should end with SELF-TEST PASSED.
  3. Drag the parkinfo folder onto run-link-ids.bat. When it asks for the key folder, press Enter to skip,
     or give KPC-Links\data\us-key to run the name check too.

  By hand:
     py -3 kpc_link_ids.py --parkinfo "D:\path\KPC-Data\data\parkinfo" --areas "US CA"
     py -3 kpc_link_ids.py --parkinfo "...\data\parkinfo" --key "...\KPC-Links\data\us-key" --areas US
     py -3 kpc_link_ids.py --selftest

WHAT COMES OUT
  summary.txt       the short answer in plain words
  link-ids.csv      one line per park. All of it comes from POTA's public park list.
  by-website.csv    one line per website: parks, own pages, ids, id kinds
  PRIVATE-name-flags.csv   only with the key folder

WHAT IT FOUND ON THE REAL LISTS (20 Nov, KPC-Data d30a6fa, KPC-Links 05dda69; US only)
  12,868 parks. 9,644 link to their own page. 1,456 share their link with another park.
  2,284 addresses hold a known id; 2,189 of those are usable.
  464 parks carry a Park Service code (counted once per park); 400 are usable, and 39 ids in all are shared.
  6,037 own pages name the park in full in the address.
  Name check: 30 joined records on 26 parks carry another park's own name. 17 of the 30 were joined by "reviewed".

LIMITS, SAID PLAINLY
  - A link id is ONE agreement. A park still needs a matching size or place before it is tied to land.
  - Only the Park Service code is KNOWN to be the same code on a map layer. Every other id kind is an id on the
    WEBSITE. A web page number usually is not on the map. Check each kind against the ID finder's fields first.
  - Nothing is opened, so a dead link or a link to the wrong park cannot be seen here. The id must still be found
    in the agency's own unit list.
  - "web name" and "web kind" are new facts read from the address. Whether the plan may use them is the reviewer's call.
  - The kind check is a hint. Only a full designation in the place's own words counts ("...-state-park", "...-wma").
  - Websites with no rule yet get a GUESS when the address holds a number. A guess is never "usable".
  - Tested on Linux with Python 3.11, 3.12 and 3.13, on invented parks and on the real parks list and key.
    NOT run on Windows; the two .bat files were written but never run.
