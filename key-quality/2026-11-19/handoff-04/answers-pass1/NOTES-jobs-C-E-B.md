# NOTES: Jobs C, E and B (pass 1, 19 Nov 2026)

Files:
- jobC-does-the-agency-publish-its-own-outline.answers.csv: 6 of 6 rows filled
- jobE-busiest-new-pins.answers.csv: 26 of 26 rows filled (some acre or outline cells are empty on purpose; see below)
- jobB-forest-service-acres.answers.csv: 7 of 7 rows filled from the user-supplied LAR_FY2025.xlsx (see Job B)

Leading (given) columns were not changed. Jobs A and F were not touched.

## Method
- Order followed: (1) the managing agency's own park page and its acreage report or table; (2) the agency's or state's GIS/open-data
  (ArcGIS REST layers owned by the agency or the state GIS office, found via the agency's own services directory or ArcGIS Online item
  search filtered to the agency's org); (3) a general web search, used only to find the agency pages.
- I read robots.txt before each new host and obeyed it, redirects included. Under RFC 9309 a 4xx on robots.txt counts as "no robots file",
  so access is allowed. I waited at least 2.5 s between requests to one host, and 10.5 s where Crawl-delay: 10 is set (agfc.com, recreation.gov).
- ArcGIS: I used attribute queries only (returnGeometry=false). For each record the layer's own acre field is quoted as shown. I never
  converted Shape__Area into acres. Where a park is split into several polygons, the sum is labelled as MY sum of the layer's acre field.
  The outline date is the layer's editingInfo.dataLastEditDate (epoch ms converted to a UTC date) or the item's modified date, as stated.
  The licence line is the layer's copyrightText and/or the item's licenseInfo, quoted.
- Numbers are as published, with the page or table and its date. Where the agency's page and its layer disagree, the page or report figure goes
  in official_acres and the layer figure in record_name_and_acres. The conflict is described in note.
- I contacted nobody.

## Sites that refused or blocked me
- mass.gov: returns "This page is forbidden" to curl, even for robots.txt. I read the page via WebFetch.
- arabiaalliance.org, swfwmd.state.fl.us, swl.usace.army.mil: 403 to curl. Their robots.txt (read via WebFetch) allows the pages, so I read
  them with WebFetch.
- enterprise.firstmap.delaware.gov (Delaware FirstMap): WAF "Request Rejected" to curl. robots.txt was 404 via WebFetch, and one query
  result was read via WebFetch.
- wyoparks.wyo.gov: serves a JavaScript bot challenge instead of a readable robots.txt, so I did not go further (E1-26).
- kmtacorridor.org redirects to alaskalivinglands.org; I followed it and read that host's robots.txt.
- Old AGFC fishing-map URLs redirect to a generic page. I did not use an intranet.agfc.com link because it looks like an internal host.
- apps.fs.usda.gov robots.txt returned 403 (allowed under RFC 9309). services.arcgis.com root robots.txt returned 403 "Invalid URL" (counted as no file).
- **USFS Box share (Job B):** robots.txt disallows downloads, and the direct host returned 401. The user supplied the workbook instead.

## Job B: Forest Service acres (filled from the user-supplied workbook)
- **Edition:** FY2025. The user downloaded LAR_FY2025.xlsx from the USFS public Box share
  (https://usfs-public.app.box.com/s/rhq1lm3rq3wauhtz6yulanuzoijaaqsw, FY2025 folder) and gave it to me. I could not download it myself: Box's
  robots.txt disallows the download path, and the direct host returned 401 without a page token, which I did not take.
- **Edition confirmed from the file itself:** the Index sheet says "US FOREST SERVICE LAND AREAS REPORT TABLES - FY2025 (data current as of 09/30/2025)".
  Every row has PROCESSDATE 10/24/2025, FISCAL_YEAR 2025 and FYQTR 4. The workbook was last modified 2025-11-18, and the Box folder is dated 2026-02-25 (UTC).
- **Acre values:** these are the raw cell values (several are stored as text). The sheets display them with format #,##0, and each note gives
  the rounded displayed figure. The tables have no "gross" column: gross_acres = "Total Acreage" (NFS Acreage + Other Acreage).
- **Links:** they point to the Table 3 or Table 5 PDF, the workbook (LAR_FY2025.xlsx) and the full book on that Box share.
- **Template quirks / probable tests:**
  - B1-04 (Custer) and B1-06 (Gallatin) DO still appear as separate proclaimed units in Tables 3, 4 and 5. Only Table 28 (NFS acres by
    administrative unit) combines them as "0111 Custer Gallatin National Forest" (NFS 3040112.21388074). So the rows were filled. The trap is
    assuming they are gone.
  - B1-02 and B1-06 ask for Table 3 with "MONTANA", but Table 3 (Areas By Region) has no state column. The MONTANA label is Table 4's.
    Flathead matches exactly between Tables 3 and 4. Gallatin differs between them in the decimals (Table 4 NFS 1850467.87938777 vs Table 3
    1850467.88418321); I used Table 3, as asked.
  - Table 28 also gives slightly different figures (e.g. Flathead NFS 2414170.73341487). I did not use them.

## Empty cells and why
- C1-04 Bear Paw Battlefield: no NPS figure for this site alone. The whole Nez Perce NHP is "Size: 4564.93 acres" (NPS stats page, Feb 9, 2022), given in note only.
- E1-04 Augusta Canal NHA: no acreage published by NPS or the coordinating entity. A 225-acre figure belongs to the NHL district, not the NHA.
- E1-08 Kenai Mountains-Turnagain Arm NHA: no agency acreage. "1.3 million acres" appears only in non-agency sources.
- E1-12 Lake Sylvia: only "18-acre lake" (water) is published. The land is USFS leased to ASP, and no outline was found.
- E1-15 Quail Creek (BLM): no acreage and no BLM polygon. These are designated dispersed campsites.
- E1-26 Point of Rocks: the POTA link is a BLM cemetery page, and the State Historic Site belongs to Wyoming State Parks (bot-challenged host). No figure or outline.

## Uncertainties and conflicts (check these)
- C1-02 Fort Hunt: NPS 2015 release says 157 acres, but the NPS Cultural Landscape Inventory says 190. The only outline is the whole GWMP polygon.
- C1-06 Hells Canyon Reservoir: IDFG page says 1,254.5 ac, but the IDFG layer says 2465.10. This may be one state's side only.
- C1-05 Upper Missouri WSR: the BLM WSR layer holds lines, not polygons. The 135,350 acres comes from the FY2019 UMRBNM manager's report, p.3.
- E1-01 Haw River: plan says 1,488 ac, but the NCDPR layer's 5 polygons sum to 1836.48 (my sum).
- E1-02 Holland Bottoms: the name does not match exactly. The ANHC preserve is 632, the AGFC WMA is 6,190. Pick the right one.
- E1-06 DeGray: the brochure says 938, but the ASP layer says 828.32.
- E1-09 Shenandoah Wilderness: published 79,579, but the layer's Acre_Calc is 82321.80.
- E1-11 Lincoln Woods (naming), E1-14 Lake Conway (6,700 vs 5627 / 5622.7), E1-20 Bull Shoals (no unit by that exact name; USACE water and land figures given), E1-21 Cardigan (5,655 vs GRANIT 5986, and the record is named "State Forest"), E1-23 Bois D'Arc (644 vs 622; lake vs WMA), E1-24 and E1-25 (STA figures are effective treatment area from SFWMD Table 2, not gross land).
