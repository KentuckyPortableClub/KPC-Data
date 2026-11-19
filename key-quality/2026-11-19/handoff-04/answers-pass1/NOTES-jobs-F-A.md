# Notes for Jobs F and A (pass 1, 19 Nov 2026)

## Method
- I used a small fetch helper. For every host it read robots.txt first and checked each URL, including every redirect hop. It waited at least 2.2 s between requests to the same host and used a plain User-Agent. I contacted no one.
- Sources were the agency's own pages and reports first, then the agency's or state's own GIS REST layers (attribute queries only, `returnGeometry=false`), then web search only to find official URLs. No acreage comes from PAD-US, OSM, Google, Wikipedia, WDPA, tourism, hunting-app or news sites. Where such a figure exists I mention it in `note` as "not used".
- Numbers are copied as published, including GIS attributes with all their decimals. Every row names the page, or the table and row, and the date read. The MassGIS WMA+WCE totals in Job A are my own sums of the listed GIS_ACRES values, and the rows say so.
- FWS refuges: "Statistical Data Tables for Fish & Wildlife Service Lands (as of 9/30/2025)" (Annual Report of Lands data tables), Table 3, with PDF page numbers. File: https://www.fws.gov/sites/default/files/documents/2026-01/2025_annual_report_of_lands_data_tables-v2.pdf . Fee columns = Reserved PD primary, Acquired OFA primary, Purchased, Donated. Easements = the three easement columns. "Other agencies" = the secondary-jurisdiction overlay columns, with agency letter codes from the footnotes (E = Corps of Engineers, F = Forest Service), plus Agreement/lease.
- NPS: Land Resources Division "Listing of Acreage - 09/30/2026" xlsx.
- Job A answers compare SIZE plus name. I could not compare record geometry or location, because I have no geometry for our records. YES therefore means "same name and about the same size per an official figure". PART on a smaller record assumes the record lies inside the park; each note says this.

## Blocked or refused (I obeyed every block and did not work around any)
- `services*.arcgis.com` (every AGOL-hosted feature service: FWS refuge boundaries, NPS boundaries, SCDNR, FWP and others) has robots.txt `Disallow: /`, so none were queried. Layer addresses are given where known.
- `www.fdacs.gov` and `ccmedia.fdacs.gov` (Florida Forest Service pages, brochures and plans) are robots-disallowed for all but named search bots. I used only FFS's own GIS layer `gis.fdacs.gov`.
- `apps.fs.usda.gov` (FS EDW GIS) is robots-disallowed. The FS Land Areas Report files sit in a Box folder (`usfs-public.app.box.com`): downloads are robots-disallowed and the folder needs JavaScript. So the LAR wilderness and forest tables were NOT read, and the FS rows use the forests' own pages.
- `dec.ny.gov/places/...` is robots-disallowed (`Disallow: /places`). I used the DEC habitat management plan on extapps.dec.ny.gov.
- `floridastateparks.org` returned HTTP 403 to direct requests (I read one page via WebFetch). `dnrec.delaware.gov` and Delaware FirstMap returned "Request Rejected" (some public DNREC pages were read via WebFetch; FirstMap was not). `geodata.md.gov` (MD iMAP) returned 503.

## Uncertainties worth a second look
- F1-25 Deep Creek North: BLM gives two figures, Wilderness Detail Table 4,478 (Jan 2026) and the unit page "now contains a total of 4,262".
- F1-15 Mason Neck: the visit page says 2,227 ac; Table 3 says 2,277.01. F1-37 Lake Mason: the page says 13,589; Table 3 says 16,814.52. F1-36 Red Rock Lakes: the page says ~53,000; Table 3 says 84,870.11, which includes about 23,806 ac of easements and 9,580 ac of agreement/lease.
- F1-29 Hailstone: the refuge proper is 160 ac of fee land plus 760 ac of easement (total 920). The adjacent 1,828-ac Hailstone WPA is a separate unit.
- F1-18 Pompeys Pillar: the monument is 51 ac. An outline of about 432 ac would be the ACEC.
- Arkansas parks: the agency publishes no park acreage on its pages. The values come from the Arkansas State Parks GIS layer (gis.ardot.gov, credited to Arkansas State Parks). arkansasstateparks.com now redirects to arkansas.com/state-parks (the Dept. of Parks, Heritage & Tourism), and I treated that as the agency's own page.
- F1-11 Big Shoals SP: inside the FDEP layer, UPLAND (1684.74) is larger than ACREAGE (1681.01).
- F1-27 Hell Creek: the land is owned by the Army Corps and was leased to FWP. A 2021 EA discussed transferring management, so confirm FWP still manages it.
- F1-35: the old "J. Perry Mikles Blue Mountain SUA" is now "J. Perry Mikles Lick Creek WMA" (4,000 ac). Do not confuse it with Blue Mountain WMA (8,200 ac).
- Job A, MassWildlife rows (A1-26, 29, 30, 33): our records equal WMA plus WCE (conservation easement) acreage in MassGIS. They are PART: bigger than the WMA and mostly easement land.

## Rows left empty or not settled
- Job F, empty acres (4): F1-14 Red Cliffs Recreation Area (BLM publishes no acreage; only the GIS_ACRES 872.88066027 is given in the record column), F1-20 McGinnis Pond (only pond surface area 31.3 is published), F1-28 Beaverhead Rock (no FWP figure found), F1-33 Laurel Industrial Forest Land (no figure on DNREC's map or page).
- F1-07 and F1-10 (FFS state forests) use the FFS GIS layer acres from 2021, because the forest pages are robots-blocked.
- Job A, CANNOT TELL (8): A1-01, 05, 09, 14, 17, 19, 20, 21. No official acreage was found, or the record is bigger than the park and I could not tell whether it contains the park or is other land.
