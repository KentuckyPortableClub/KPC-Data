# Job 2 notes (hand-off 03B independent check), 19 Nov 2026 (US Central time)

Output: `job2-official-acres-and-outline.answers.csv`. All 10 rows are attempted. The first 7 columns are copied unchanged from the template, and a script checked that.

## Method
- I went in the README's order: (1) the agency's open data and catalog. I used the www.arcgis.com search and item API only, which robots.txt allows (`User-agent: *` with no Disallow). (2) The agency's own park page, acreage table, map PDF or GIS server. (3) A general web search, used only to find agency URLs.
- I read robots.txt for every host before using it: nps.gov, irma.nps.gov, irmaservices.nps.gov, mapservices.nps.gov, ohiodnr.gov, gis.ohiodnr.gov, gis2.ohiodnr.gov, dam.assets.ohio.gov, wildlifedepartment.com, blm.gov, gis.blm.gov, agfc.com, arkansasheritage.com, gis.arkansas.gov, oregon.gov and gisapps.odf.oregon.gov. I waited at least 2 s between requests to one host.
- NPS acres come from the NPS Land Resources Division "Listing of Acreage - 09/30/2026" xlsx, the latest quarterly table. The values are copied exactly.
- An outline counts as found only when I queried the agency's or state GIS office's own server and found the park by name or code. I recorded the attribute values exactly as returned. Every acre figure marked "my sum" or "my conversion" is my own arithmetic, not a published number.
- I contacted nobody, logged in nowhere and submitted nothing.

## Blocked or not opened
- **services*.arcgis.com: opened after a follow-up on 2026-11-19, 09:07 CST.** These hosts serve no robots.txt (GET /robots.txt returns 403 "Invalid URL"; I re-checked this myself). Under RFC 9309 a 4xx means no restrictions, and the user, who owns the README, approved opening the layers. I opened the agency-owned layers with query endpoints only (returnGeometry=false, plus one geometry query for the NPS polygons to compute areas), keeping >=2 s between requests.
  - NPS LRD "nps_boundary" (FeatureServer/2): the serviceItemId is a2848257cf5541338bab9b656440bd0c, owner karndt@nps.gov_nps, copyright "National Park Service Land Resources Division". This is the agency's own layer, not the Esri_US_Federal_Data copy.
  - ODWC "Public_WMA_Boundaries_11172026" (FeatureServer/1): the serviceItemId is 25e889952822414d8431fec19d68e289, owner ODWC_GIS.
  - Rows B2-01, 03, 04, 06 and 09 are now VERIFIED, and the "NEEDS_A_HUMAN_DOWNLOAD: YES" flags are removed.
  - The NPS boundary layer has no acres field. The acres shown for those polygons are my geodesic computations (WGS84), labelled as such.
  - I did not open the AGFC copy (26fe65ce…) or the OR_FRAMEWORK item (04ef00d4…). B2-07 already uses the state GIS office layer, and B2-10 already uses ODF's own zip.
- **irmaservices.nps.gov** has a robots.txt of `Disallow: /`, and **irma.nps.gov** disallows /DataStore/DownloadFile/. I did not use the NPS DataStore download.
- **gis.ohiodnr.gov** has a robots.txt of `Disallow: /`, so I did not use it. I used gis2.ohiodnr.gov, which has no robots.txt.
- **mapservices.nps.gov** (NPS's own server) has no boundary service; the old LandResourcesDivision service there returns 404.
- **Plain curl from my box failed on some agency pages:**
  - agfc.com returned a Cloudflare 403.
  - wildlifedepartment.com failed TLS after the robots.txt read.
  - ohiodnr.gov served its 404 page to curl.

  I read these public pages through the fetch tool instead.

## What I'm unsure of / catches
- **B2-04 Tallgrass and B2-09 Timucuan look like test rows.** POTA calls both a "National Conservation Area", but NPS units are "Tallgrass Prairie National Preserve" and "Timucuan Ecological & Historic Preserve", and neither is an NCA. Both are mostly land NPS does not own: Tallgrass is 33.12 of 10,882.67 ac, and Timucuan is 15,792.67 of 46,262.76 ac.
- **B2-01 Craters and B2-06 Great Sand Dunes risk a containing area.** NPS lists the monument or park and the preserve as separate rows. POTA's name matches only the NM or NP row. The Craters NPRES row includes 273,488.22 ac of "Other Federal Fee" land. Someone has to decide which polygon or polygons belong to the park number.
- **B2-03 Osage WMA is two units** (Western Wall and Rock Creek), and ODWC publishes no whole-WMA total. ODWC's own pages conflict on Western Wall: 7,329 vs 5,950 ac. The POTA link opens the Western Wall page only.
- **B2-05 Diamond HMA** matched by exact name (NV0609). The similar names Diamond Hills North and South are different HMAs. The layer's BLM_ACRES (166,305.43) contradicts the page's 145,341 ac of BLM land.
- **B2-07 and B2-08 Longview Saline (WMA and Natural Area) are the same land per official pages.** AGFC says the WMA is owned by ANHC, and ANHC names the WMA. Their polygons on the Arkansas GIS Office server differ by under 10 ac by my area conversion. No page says the boundaries are identical. AGFC publishes no acres for the WMA.
- **B2-10 Tillamook SF has no official outline by name.** ODF's ownership data is split by district, and the forest spans the Tillamook and Forest Grove districts, so a district polygon would be a containing or partial area. The 364,000 ac figure is from the April 2010 plan, and the current ODF page gives no acreage.
- **B2-02 Acadia Cliffs:** the page says 273 ac, while the layer and the 2022 map say 275.25 ac. That total includes a 107.77-ac dedicated nature preserve parcel.

## Added after opening the services*.arcgis.com layers
- **B2-09 Timucuan:** the TIMU record has Status "Legacy", not "Official". Its polygon is about 45,361 ac (my computation), versus 46,262.76 gross in the acreage table. Fort Caroline (FOCA) is a separate polygon, and only about 29% of it overlaps TIMU.
- **B2-06 Great Sand Dunes:** the Park and the Preserve share UNIT_CODE "GRSA". Select the Park by UNIT_NAME or OBJECTID 960, not by unit code.
- **B2-01 Craters:** the NM (CRMO) and Preserve (CRMP) are separate polygons. Use OBJECTID 1181 for the NM-only name.
- **B2-03 Osage:** the layer holds two unit polygons, Western Wall at 7316.69642931 ac and Rock Creek at 3729.49292555 ac, both OWNERSHIP " ODWC". The layer supports 7,329 for Western Wall, not 5,950.
- Every polygon area I computed is within about 2% of the agency's published acres. The exception is TIMU, which is about 2% low.
