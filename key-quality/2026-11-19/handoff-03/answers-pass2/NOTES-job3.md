# NOTES – Job 3 (hand-off 03B): is there an official GIS boundary layer for each park?
Kentucky Portable Club check, done 19 Nov 2026 (America/Chicago). Output: `job3-busy-parks-is-there-official-gis.answers.csv` (all 58 rows filled in order, first 7 columns left as given).

## Counts (58 rows) - UPDATED after the follow-up pass (see "Follow-up 19 Nov 2026" below)
| answer | rows | notes |
|---|---|---|
| GIS | 22 (19 distinct parks) | B3-01, 04, 05, 12, 14, 15, 17, 20, 23, 24, 26, 28, 29, 30, 34, 35, 38, 46, 48, 53, 55, 56. The 3 Manhattan Project rows count as one park, and so do the 2 Cibola rows. Every GIS row now has a record name and an acres (or Shape__Area) value read from the agency's own layer. |
| PICTURE | 0 | |
| NOTHING | 30 | |
| empty | 6 | B3-02 and B3-44 need a decision (see below). B3-32, 40, 42 and 50 are still blocked (needs-human YES). |
| needs_a_human_download = YES | 4 | B3-32 (USACE PDF 403), B3-40 and B3-50 (gis2.ncdcr.gov robots-disallowed), B3-42 (FirstMap firewall) |

Before the follow-up the counts were GIS 20 / PICTURE 0 / NOTHING 10 / empty 28, with 30 rows needs-human YES.

## Method
1. Search: I searched the ArcGIS Online catalog through `www.arcgis.com/sharing/rest/search` (robots allows it; ArcGIS Hub sites set Crawl-delay 60, so I used the catalog API instead). I then read item JSON and saved item `/data` (layer lists, renderer classes) from www.arcgis.com, plus CKAN where available.
2. Agency servers: where the agency serves its layer from its own server, I queried the record directly (attributes only, no geometry). These servers were apps.fs.usda.gov (USFS EDW), gisdata.in.gov, gis.eea.mass.gov, nhgeodata.unh.edu, www45.swfwmd.state.fl.us, dnrmaps.wi.gov, maps.prd.state.or.us, risegis.ri.gov, geodata.hawaii.gov, irma.nps.gov profile pages, and OSU/ODWC servers.
3. Agency pages: I read the agency park pages and opened their PDF maps. I rendered the PDFs to check whether a boundary is actually drawn.
4. Politeness: one polite fetcher with robots.txt checked per host and on redirects, ≥2.2 s between requests to the same host, and a cache. The log of about 210 requests is in `fetchlog.txt`. I contacted nobody.
5. Robots rule I used: hosts whose robots.txt returns 4xx (e.g. apps.fs.usda.gov returns 403) were treated as "no rules = allowed", per RFC 9309. Python's old robotparser would have treated 403 as disallow-all. **If the club wants the stricter reading, the 7 USFS rows (B3-05, 14, 17, 24, 26, 28, 29) would become "needs human".**
6. Official sources: I counted only the managing agency or the state GIS office (MassGIS/EEA, NH GRANIT, Hawaii Statewide GIS, IndianaMap). Not counted: NC Natural Heritage Program (a compiler), PAD-US, Esri Federal Data copies, university or personal copies, tourism sites.

## Blocked / not opened
- **services*.arcgis.com:** opened in the follow-up pass with the user's approval (see below). Not opened: RIGIS State Conservation Lands (only an optional double-check for B3-18/37) and NC DOA State-Owned Land (another agency, a pointer only for B3-40/50).
- **Disallowed by robots.txt:** gis2.ncdcr.gov (NC HPO), widnr.widen.net (WI DNR map PDFs), data.ca.gov API, and irma.nps.gov `/DataStore/DownloadFile/` (so the NPS shapefile zips are not downloaded).
- **Firewall or 403 responses (I did not try to get around them):** enterprise.firstmap.delaware.gov ("Request Rejected"), destateparks.com (403), the USACE Vicksburg Arkabutla map PDF (403), wildlifedepartment.com fishing page (SSL error), gisservices.its.ny.gov (TLS refused).
- **Dead link:** the MI DNR webappviewer that POTA gives (item 2c8a3ec7…) returns "Item does not exist or is inaccessible".


## Follow-up 19 Nov 2026 (user approved; owner message "Yes update all files etc")
**Why these hosts were opened:** the user checked that services*.arcgis.com (ArcGIS Online hosted feature services) serves no robots.txt. The request returns HTTP 403 'Invalid URL', which under RFC 9309 means no rules, and the user explicitly approved opening the agency layers there. The same polite fetcher was used: attributes only (`returnGeometry=false`, `f=json`), ≥2.2 s per host, cached, and logged in `fetchlog.txt`. For each layer I confirmed that the item owner is the managing agency, not Esri or a copy. Hosts with real robots disallows (gis2.ncdcr.gov, widnr.widen.net, data.ca.gov API, NPS DataStore download path) and the firewalled hosts stayed off-limits. I contacted nobody.

**Changes:**
- **NPS LRD boundary layer** (services1.arcgis.com/fBc8EJBxQRMcHlei/.../NPS_Land_Resources_Division_Boundary_and_Tract_Data_Service/FeatureServer/2, owner karndt@nps.gov_nps):
  - B3-12/46/55: record 'Manhattan Project National Historical Park' (MAPR).
  - B3-23: record 'Fort Vancouver National Historic Site' (FOVA).
  - The layer has no acres field, so Shape__Area is quoted instead.
  - **B3-02 changed from GIS to EMPTY (decision needed).** The layer has no 'National Mall and Memorial Parks' record, only 'National Mall' (MALL) plus separate units for each memorial (LINC, WAMO, JEFM, WWII, VIVE, KOWA, FRDE, MLKM, …). The club must decide whether to union those or use MALL alone.
- **NJ Pinelands (B3-48), still GIS:** the layer holds one polygon, OBJECTID 1. There is no name field, and Shape__Area is 7904479022.13 (Web Mercator m²).
- **NPS WSR Boundaries Official (cor_nps), all NOTHING:**
  - B3-08 Taunton, B3-21 Wekiva and B3-47 Farmington (West Branch, RIVER_ID 156) appear in NPS's table 'Rivers_With_Protection_Areas_or_Without_WSR_Boundaries', i.e. officially *no boundary*.
  - B3-22/58 Nashua and the Lower Farmington & Salmon Brook WSR appear in no layer or table.
  - NPS's Taunton text mistakenly mentions "The Lamprey" (a copy-paste error in the source).
- **FWS Realty boundaries, B3-11 → NOTHING:**
  - No feature is named for Minnesota Valley WMD.
  - 9 county WPA records share CostCenter FF03RMVW00 and are probably the WMD's WPAs. This is an optional human decision.
  - The trap 'MINNESOTA VALLEY NATIONAL WILDLIFE REFUGE' was avoided.
- **TVA layers, B3-03/19/31/39/43/49 → NOTHING:**
  - TVA's Reservoir Plan parcels carry no park names.
  - The dam rows fall in 'Hiwassee Dam reservation', 'Blue Ridge Dam reservation' and 'Fontana dam reservation' parcels (Nottely's is unnamed). I quoted them in the record column as a pointer. A human may decide those dam-reservation parcels count.
- **Other layers:**

  | Row | Agency layer | Result |
  |---|---|---|
  | B3-09 | ODWC | NOTHING. Absent; only 'Lake Carl Etling', a different place. |
  | B3-07 | WVDNR | NOTHING. The only 'Forks of Coal' record is a 0.83-ac WVDOH public access site, a trap. |
  | B3-36 | CT DEEP | NOTHING. Absent. |
  | B3-45 | NYSDEC | NOTHING. Absent; this confirms the PIPC/OPRHP manager trap. |
  | B3-30 | CDPR | **GIS.** 'Torrey Pines SNR', UNITNBR '630' (not 'Torrey Pines SB' 631). |
  | B3-56 | NCWRC | **GIS.** Tract "Jessup's Millpond", 1195.55 ac (not the whole Suggs Mill Pond GL). |
  | B3-13 | NCWRC | NOTHING. The lake lies inside the 1021-ac 'Upchurch-Williams' tract of Nicholson Creek GL, a bigger containing area. |
  | B3-44 | GA WRD | Stays EMPTY (decision needed). The Boundary layer has no Marben or Charlie Elliott polygon. The WRD PDF's 'Boundary' line encloses the archery and shooting ranges, campground and clubhouse, i.e. it looks like the whole 6,400-ac Charlie Elliott tract, so PICTURE would be a bigger-area answer. |

- **Finished rows:**
  - **B3-38 → GIS:** 'LOWER LAKE' at 'DEGRAY LAKE' in USACE's national 'USACE Recreation Areas' layer (owner usace_crrel_als), 2 polygons, managed by the Corps. The trap 'DEGRAY LAKE RESORT STATE PARK' was avoided, and so was a BRADD_Admin listing of the same service.
  - **B3-27 → NOTHING:** NCWRC Lake Rim Boating Access Area exists only as a point.
  - **B3-51 → NOTHING:** a City of Hope lake in Fair Park, built with AGFC and listed as an AGFC Family Fishing water. It is in neither AGFC layer.
  - **B3-57 → NOTHING:** no Arkansas State Parks or AR GIS Office polygon exists. AGOL copies by wlgardnerjr, TN TDEC and rmeeks are non-managing. The park PDFs return 404.
- **B3-32 (still blocked):** the same USACE layer has about 23 separate 'ARKABUTLA LAKE' recreation-site polygons but no lake-wide area, so the PDF check is still needed.

## Notable catches (traps)
- **Bigger containing area:**
  - Pike NF (B3-29): the USFS admin record is "Pike and San Isabel National Forests", so I used the proclaimed "Pike National Forest" record.
  - Cibola NF (B3-24/26): the admin record of the same name has 3.2 M ac because it includes the National Grasslands. The proclaimed record is 2.1 M ac.
  - Quakertown (B3-01): use the subunit (663 ac), not "Brookville Lake" (13,201 ac).
  - Kil-So-Quah (B3-33): only J.E. Roush FWA exists, and the PDF merely labels it.
  - Mauthe Lake (B3-41): it sits inside Kettle Moraine SF-Northern Unit.
  - Taylor Mill (B3-06): it is on Ballard State Forest.
  - Beach Pond (B3-37): the land is filed under Arcadia Management Area, which is also the page POTA links.
  - Jessups Mill Pond (B3-56): part of Suggs Mill Pond Game Land, so I used only its own tract record.
  - Upchurch Lake (B3-13): inside the Upchurch-Williams tract of Nicholson Creek GL.
  - TVA dam rows: dam-reservation parcels only.
  - Marben PFA (B3-44): inside the 6,400-ac Charlie Elliott tract.
  - Michigan's named state forests (B3-10/16/25/52): exist only as groupings of FMUs, so they come out NOTHING.
  - Farnham-Connolly (B3-54): probably inside Neponset River Reservation.
- **Similar name, different place:**
  - Abigail Adams Green and Abigail Adams Park (municipal) vs Abigail Adams *State* Park (B3-04).
  - Minnesota Valley NWR vs the WMD (B3-11).
  - Farmington (B3-47): two separate WSRs, West Branch (1994) and Lower Farmington & Salmon Brook (2019).
  - Hillsdale (B3-18): the only "Hillsdale" record is a private easement of 111 ac, not the 45-ac DEM parcel.
  - "Ballard Town Forest" vs Ballard State Forest (B3-06).
  - Torrey Pines SNR vs Torrey Pines State Beach (B3-30).
  - Pinelands National Reserve vs the state "Pinelands Area" layer (B3-48).
  - DeGray Lower Lake vs DeGray Lake Resort SP (B3-38).
  - "Columbia River Gorge National Forest" does not exist; the USFS unit is the National Scenic Area (B3-14, flagged unsure).
- **Copy by a non-managing publisher:**
  - NCNHP "Tennessee Valley Authority – Hiwassee Dam" (B3-31).
  - The USFS-served national WSR *line* dataset for NPS rivers (B3-08/21/22/47/58).
  - The UConn CLEAR copy of DEEP Property (B3-36).
  - Esri_US_Federal_Data and Federal_User_Community copies of the USFS and NPS layers.
- **Wrong state or multi-site:** Fort Vancouver is mainly in WA; only McLoughlin House is in OR (B3-23). Manhattan Project spans NM, TN and WA (B3-12/46/55). Sawtooth NF is mostly in Idaho (B3-17). Nashua is mostly in MA (B3-22/58).
- **Wrong manager suspected:**
  - Lake Carl Blackwell is OSU land (B3-09).
  - Iona Island is part of Bear Mountain SP, run by PIPC/OPRHP rather than a DEC WMA (B3-45).
  - Na Ala Hele is a statewide trail programme, so its layer is 157 trail lines, not a polygon (B3-15).

## Unsure
- B3-14 (CRGNSA used for a misnamed POTA unit).
- B3-15 (a line layer accepted as GIS).
- B3-06 (whether to accept Ballard SF).
- The robots reading for apps.fs.usda.gov (see point 5).
- NPS rows are now verified in the LRD layer. FOVA was last edited in 2011 and MAPR in 2016.
- The Farmington FRCC attribution (B3-47) is from memory.
- The Mount Magazine/USFS land note (B3-57) is from memory, but it does not change the answer.
- B3-38 is published by USACE ERDC-CRREL, not Vicksburg District itself (both are USACE).
- B3-13 and the TVA dam rows are strict by-name NOTHINGs that a human could reasonably flip to GIS.
- B3-02 and B3-44 are left empty for a club decision.
- Duplicate rows (B3-26, B3-46, B3-55, B3-58) were answered the same as their first occurrence.
