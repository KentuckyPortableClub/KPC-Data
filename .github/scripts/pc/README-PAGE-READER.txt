KPC bots on this PC (21 Nov 2026)

What this does
  0-INSTALL-PAGE-BROWSER.bat  Once (22 Nov): adds a hidden browser (Playwright + Chromium, about 150 MB) so the page
                            reader can read park pages that build themselves in a browser. Same manners. Asks YES.
  1-MAKE-PRIVATE-LISTS.bat  Measures every park in your store (no internet) and makes two private lists:
                            the likely mismatches (pin far outside its outline, or size way off) and the
                            parks already confirmed by their agency ID.
  2-READ-PARK-PAGES.bat     Runs the park page reader here, reading the likely mismatches first and the
                            confirmed parks last. Polite: robots.txt first, slow on every site.
                            After each run it sorts the "name differs" questions by itself (3-SORT below).
  3-SORT-NAME-QUESTIONS.bat Sorts the "name differs" questions into groups, so only the real differences go to a
                            person (page-reader\out\name-differs-sorted.csv). No internet, changes nothing.
  4-SAVE-PICTURE-MAPS.bat   For parks with no map outline, saves the PDF or picture map from the park's own pages,
                            small, by park number, in Tools\picture-maps. Deleted once the park gets an outline.
                            Needs PyMuPDF once (the file offers to install it). Asks YES before downloading.

21 Nov (later): the size check now merges a park's map pieces instead of adding them up (two records of the same
land counted twice before). Test: tools\test_three_checks_union.py. The easy way to run everything: the control panel
(KPC CONTROL PANEL.bat in the Tools folder). Rules for the research helpers: Tools\RESEARCH-RULES.txt.

Order
  1. Wait for the store run window (RUN-NOV21-FETCH-BUILD) to say Done.
  2. Double-click 1-MAKE-PRIVATE-LISTS.bat. Tell Claude "lists done".
  3. Double-click 2-READ-PARK-PAGES.bat. It runs up to 3 hours; run it again to carry on.
     Each run saves a zip in SEND-BACK. Tell Claude "pages done".

Upload pack (22 Nov)
  5-MAKE-UPLOAD-PACK.bat    Packs the page facts of the areas the page reader has FINISHED (every park of the area read: a
                            part-read area would show the private likely-mismatch list) and, for every agency list whose columns tie
                            (upload-approved-agencies.txt is optional: if you make one, only those), the web id -> map id crosswalk, into SEND-BACK\kpc-upload-pack-<date>.zip.
                            Nothing is uploaded. You carry it up: KPC-Data, branch intake-files, folder pc-upload, Upload files;
                            then Actions, "KPC PC upload pack (by hand)", with the name pc-upload/<zip name>. GitHub checks it
                            first (any problem keeps nothing), then keeps every park it already has and adds the new ones.

Private
  The PRIVATE folder names parks. It stays on this PC: never put it in a repo, a zip or a chat.
  The only file to share is PRIVATE\counts-to-share.txt (counts, no park names).
  The bots refuse a park list kept inside a git folder.

Needs Python 3.10 or newer (the one the store tool uses). Nothing else to install, except PyMuPDF for picture maps and the page browser (0-INSTALL).

22 Nov 2026, 9 PM: to get the addresses, map points and directions, double-click 2b-PULL-ADDRESSES.bat (one quick pass,
several sites at once, same manners). Then 5-MAKE-UPLOAD-PACK.bat and tell Claude "addresses done".

26 Nov 2026: ONE BUTTON. PAGE-READER.bat asks for a number:
  1 = status (PAGE-READER-STATUS.txt: what is read, what is not and why; no internet)
  2 = read the kept pages again with the newest rules (no internet). Do this first after a fix.
  3 = read ONLY what is missing or failed, then the slow sites as slowly as each asks. It can run all night.
The site rule (owner, 26 Nov): only a real robots.txt Disallow line is a "no". Everything else is "not now" and is tried
again on the next run by itself. Every run writes PAGE-READER-STATUS.txt beside this file. The old buttons still work.

Decisions: CONFIRMED by the owner, 27 Nov 2026, 4:15 AM ("yes what wrong with reading?")
Each one is a single value in page-reader\scripts\kpc_net_rule.py (DECISIONS, near the top). Change only that value.
  robots_challenge_page = no-rules : when robots.txt answers with a "verify you are human" or sign-in page, we read the site,
                                     because that page is not a Disallow line. Set it to busy to skip that site for the run instead.
  robots_other_site_page = no-rules: when robots.txt sends us to a page on another site with no robots lines, we read the site.
                                     Set it to busy to skip that site for the run instead.
  wall_max_chars = 3000            : a page counts as an "are you human" wall only when its text is shorter than this, so a long
                                     real page that only mentions "captcha" is still read.

27 Nov 2026 (owner: "sure we are just polite"): a page that answers 401 or 403, or is an "are you human" wall, is THAT PAGE only.
It is not asked again this run, and the site carries on at its slow pace. Five such pages in a row from one site, with nothing
read between, stop that site for the rest of the run (one value: refusals_in_a_row in kpc_net_rule.py). A 429 means the site
says "slow down": that site is stopped for the run at once. All of these are tried again next run. Nothing is saved as blocked.
