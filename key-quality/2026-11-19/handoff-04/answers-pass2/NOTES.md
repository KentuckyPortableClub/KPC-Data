# Handoff 04 — notes (Grok Bot, 2026-11-19)

## Method
- Order worked: Job F, then A, C, E, B. Busiest parks first within each sheet.
- Sources: only the managing agency's own pages, annual land tables and GIS layers (or the state GIS office). PAD-US, OSM, Google, Wikipedia, WDPA, tourism and news sites were not used as evidence. Web search was used only to find agency URLs, and every number was then read from the agency page or file itself.
- Numbers are copied exactly as published. GIS attribute values are labelled as GIS attributes (not published tables). Where a page and its layer disagree, both are given.
- Main tables used:
  - FWS Annual Report of Lands as of 9/30/2025 (2025_annual_report_of_lands_data_tables-v2.pdf)
  - NPS Listing of Acreage 09/30/2026 (xlsx)
  - BLM Public Land Statistics 2025 (Table 5-6)
  - NC Systemwide Plan 2023 Table 2.2 (as of Dec 2022)
  - SCDNR 2024 harvest report Table 4
- Job A rule: YES = official acres within about 6% and the same unit. PART = the record is clearly only part of the park, or clearly contains extra land (e.g. fee plus easements, or a fund class). CANNOT TELL = the record is much bigger with no containment evidence, or the source was blocked. Counts: YES 17, PART 13, CANNOT TELL 5, NO 0.
- Similar names were not treated as proof. Where only a same-name record exists, the note says so (e.g. E2-02 Holland Bottoms SNA vs the AGFC WMA).

## Manners
- A script fetcher checked robots.txt for every host, including every redirect hop. Rules were applied with RFC 9309 longest-match (Protego). A robots.txt that returned 4xx was treated as allow; 5xx/429 was treated as disallow.
- At least 2.5 s between requests to one host, and crawl-delay was honoured (10 s on agfc.com and map.mysuwanneeriver.com). Responses were cached so nothing was re-fetched.
- Slip: on map.mysuwanneeriver.com the first two requests went out before I applied its crawl-delay of 10 (they were still spaced at least 2.5 s apart). Fixed after that; see the F2-27 note.
- Early on I briefly used first-match robots parsing. It was over-strict (it blocked more, never less), and I replaced it.
- No one was contacted. No other agents' folders were opened.

## Blocked / refused (noted and moved on)
- fdacs.gov / ccmedia.fdacs.gov: robots.txt says Disallow / for all bots.
- Delaware (destateparks.com, dnrec.delaware.gov, FirstMap): "Request Rejected" firewall. Delaware rows were left empty or marked CANNOT TELL.
- www2.dnr.sc.gov: robots.txt returned 500, treated as disallow.
- aws.sjrwmd.com: disallowed by robots.txt.
- idfg.idaho.gov: the robots check gave disallow-all, so IDFG was not read (C2-05 left empty).
- usfs-public.app.box.com: the download endpoint is disallowed by robots.txt (only /s/ pages are allowed). Job B acres were therefore NOT read and are left empty.
- 403 to my direct fetcher, robots allows, read through the WebFetch tool instead: floridastateparks.org, mass.gov, tn.gov, swfwmd.state.fl.us (Terra Ceia page).
- Other failures: arabiaalliance.org 403 (not read); townoffosterri.gov SSL error (not read); some old POTA URLs 404; AGFC fishing-map URLs now redirect to a generic page.

## Job B
- Newest edition found: Land Areas of the National Forest System, FY2025 (USFS Box folder FY2025, created 2026-01-12, files updated 2026-02-25). Links point to the Box file pages for LARTable3.pdf and LARTable5.pdf.
- Acres empty because the robots rules block the download (see above). Someone who may download it can fill them from Table 3 or Table 5.

## Unsure / worth a second look
- E2-04 Augusta Canal NHA: the NPS layer gives 133 acres, which looks small for the designated area.
- E2-07 Colonial: the NPS page says 10,221 acres; the 2026 listing gives 8,675.04 gross.
- E2-05: the SWFWMD page says 128; the layer says 119.48.
- C2-02 / C2-04: the NPS publishes outlines only as part of the parent unit (GWMP; NEPE, Legacy 2013). No acres for the site alone.
- C2-06: the BLM page URL was not opened in this run. The figure is from PLS 2025 Table 5-6.
- E2-21 Bull Shoals Lake (USACE): not researched in time. E2-17 (DE) and E2-23 (Foster RI) were blocked.
- Many outline columns in Job E are empty where I did not find or check an agency layer. Empty means not found, not "doesn't exist".

## Pass 2: user-supplied files (2026-11-19, about 1:15 PM CST)
- The user-supplied files I was pointed to (three PDFs, two .txt files and two screenshots, which should be the USFS LAR FY2025 Table 3/Table 5 and the Delaware park maps) are NOT on the box. Their attachment folder has only the original task zip and a copy of my own pass-1 handoff zip, and a search of the whole box found none of the file names. Nothing could be read from them.
- I tried the two URLs the user gave once each with the same polite fetcher (robots checked, at least 2.5 s apart):
  - https://www.destateparks.com/wp-content/uploads/2026/08/maps_Trap_Pond.pdf -> HTTP 403
  - https://www.destateparks.com/wp-content/uploads/2025/05/maps_Delaware_Seashore.pdf -> HTTP 403
  The Delaware block from pass 1 still stands.
- The screenshots were described as Google map embeds with no acres, so they would not support a figure or an official outline anyway.
- No answer cells changed in pass 2. Job B acres and the Delaware rows (A2-01, E2-17) remain as in pass 1.

## Pass 3: user-supplied USFS tables (2026-11-19, about 1:20 PM CST)
- The user supplied two PDFs, read with pdftotext -layout:
  - '2025 Land Areas Report, Table 5 - Areas in Multiple States' (5 pages)
  - '2025 Land Areas Report, Table 3 - Areas by Region' (18 pages)
  Every page prints 'Refresh Date: 10/24/2025', and the PDFs were created 2025-10-28. This is the FY2025 edition that sits in the USFS Box folder 'FY2025'.
- Job B is filled for all 7 rows:
  - 'Portion' rows use the state sub-row under the unit in Table 5.
  - Flathead and Gallatin use the whole-forest unit rows under 'Northern Region (01) > National Forest' in Table 3.
  - Gross = 'Total Acreage' as published (the report's columns are NFS Acreage / Other Acreage / Total Acreage).
- Naming: every unit name appears verbatim. Custer and Gallatin are printed as the separate proclaimed units, not 'Custer Gallatin NF'. Table 3 has no state column, so 'MONTANA' is not printed for B2-02 and B2-05.
- Each changed row notes that its PDF was supplied by the user. My own fetcher is still blocked from Box downloads by robots.txt.
- Delaware: the user reports the Delaware map PDFs would not download for them either. They had only screenshots of the Google map embeds, which show no acres. A2-01 and E2-17 are unchanged.

## Pass 4: Jerimoth Hill map (user-supplied)
- E2-23: the user supplied the Town of Foster PDF "Jerimoth Hill map" (2018-04-25, 1 page). It is a picture-only trail map with no acres and no boundary, and it states the Jerimoth Hill area is NOT Foster Land Trust property. Acres and outline stay empty; note updated.
