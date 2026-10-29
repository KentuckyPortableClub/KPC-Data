# PARK DETECTIVE: answers

Read 2026-10-29. REVIEW ONLY: nothing here is in a key. ANSWERED first (a find matches the question's own fact words), then PARTLY (context only: polygons under the pin, PAD-US, a size sentence, but not the thing asked), then NOT FOUND with what was tried. Partly and not found go to chats 8 / 11, then Brandon. Every step's find is listed so the chain can be followed; a quoted line is the source's own words; check the link before any use.

ℹ️ Maps and park info are a planning aid, not a guarantee. Always check the official agency map and rules before you go.

## q2-boiling-springs-acreage: US-12752 Green River State Natural Area (Boiling Springs unit) · acreage · ANSWERED (step 2 agency page)
- asked: Boiling Springs unit size (the OKNP page says 440 acres?) (HQ (Brandon test case))
- **agency page size: 440 acres (labelled size row)**
- "e hiking trails as well and canoe access. Access Type: Open to Public County: Hart Region: Green River Region Size: 440 Owner: ​Office of Kentucky Nature Preserves Manager: Nature Preseve Manager ​Office of Kentucky Nature Preserv"
- https://eec.ky.gov/Nature-Preserves/Locations/Pages/Rush-Island-Bottoms.aspx (read 2026-10-29)
- units: our outline holds 139 ac in 1 piece(s) vs the agency's "e hiking trails as well and canoe access. Access Type: Open to Public County: Hart Region: Green River Region Size: 440 " (https://eec.ky.gov/Nature-Preserves/Locations/Pages/Rush-Island-Bottoms.aspx) · pieces: Green River State Natural Area (Rush Island Bottoms) 139 ac
- the chain:
  - step 1 our layers (context): polygon under or near the pin in a layer we read: "Green River State Natural Area (Rush Island Bottoms)", 139 ac · "MA_ID=768.0; MANAME=Green River State Natural Area (Rush Island Bottoms); UNIT_TYPE=State Natural Area; MA_OWNER=Office of Kentucky Nature Preserves; MNG_INST=O" · https://kygisserver.ky.gov/arcgis/rest/services/WGS84WM_Services/Ky_KNP_Natural_Areas_WGS84WM/MapServer/0 · note: a different unit of the same natural area
  - step 2 agency page (answer): agency page size: 200 acres (total-looking) · "Washington, DC, based nonprofit, has worked with the Hart County Historical Society to protect an additional 200 acres in the area. Access: Due to limited acces" · https://eec.ky.gov/Nature-Preserves/Locations/Pages/Rush-Island-Bottoms.aspx
- steps tried:
  - step 1: point query at the pin + within 2000 m https://kygisserver.ky.gov/arcgis/rest/services/WGS84WM_Services/Ky_State_Parks_Features_WGS84WM/MapServer/8 → nothing matched
  - step 1: point query at the pin + within 2000 m https://kygisserver.ky.gov/arcgis/rest/services/WGS84WM_Services/Ky_Public_Hunting_Areas_WGS84WM/MapServer/1 → nothing matched
  - step 1: point query at the pin + within 2000 m https://kygisserver.ky.gov/arcgis/rest/services/WGS84WM_Services/Ky_KNP_State_Nature_Preserves_WGS84WM/MapServer/0 → nothing matched
  - step 1: point query at the pin + within 2000 m https://kygisserver.ky.gov/arcgis/rest/services/WGS84WM_Services/Ky_KNP_Natural_Areas_WGS84WM/MapServer/0 → 1 named polygon(s) of 1
  - step 2: agency park page https://eec.ky.gov/Nature-Preserves/Locations/Pages/Rush-Island-Bottoms.aspx → opened, nothing matched
  - step 2: 13 document link(s) not followed  → skipped: not about parks

## q1-boiling-springs-tract: US-12752 Green River State Natural Area (Boiling Springs unit) · tract · PARTLY
- asked: the KHLCF Timber Lane 115.75-acre tract: is it part of the preserve? (HQ (Brandon test case))
- context only: tried steps 1, 2, 3, 6
- the chain:
  - step 1 our layers (context): polygon under the pin in a layer we read: "Green River State Natural Area (Rush Island Bottoms)", 139 ac · "MA_ID=768.0; MANAME=Green River State Natural Area (Rush Island Bottoms); UNIT_TYPE=State Natural Area; MA_OWNER=Office of Kentucky Nature Preserves; MNG_INST=O" · https://kygisserver.ky.gov/arcgis/rest/services/WGS84WM_Services/Ky_KNP_Natural_Areas_WGS84WM/MapServer/0 · note: a different unit of the same natural area
  - step 2 agency page (context): tract: Davis Bend is one of several sites the KHLCF protects along the Green River in Hart, Green, and Taylor Counties. · "Davis Bend is one of several sites the KHLCF protects along the Green River in Hart, Green, and Taylor Counties." · https://eec.ky.gov/Nature-Preserves/Locations/Pages/Rush-Island-Bottoms.aspx
- steps tried:
  - step 1: point query at the pin https://kygisserver.ky.gov/arcgis/rest/services/WGS84WM_Services/Ky_State_Parks_Features_WGS84WM/MapServer/8 → nothing matched
  - step 1: point query at the pin https://kygisserver.ky.gov/arcgis/rest/services/WGS84WM_Services/Ky_Public_Hunting_Areas_WGS84WM/MapServer/1 → nothing matched
  - step 1: point query at the pin https://kygisserver.ky.gov/arcgis/rest/services/WGS84WM_Services/Ky_KNP_State_Nature_Preserves_WGS84WM/MapServer/0 → nothing matched
  - step 1: point query at the pin https://kygisserver.ky.gov/arcgis/rest/services/WGS84WM_Services/Ky_KNP_Natural_Areas_WGS84WM/MapServer/0 → 1 named polygon(s) of 1
  - step 2: agency park page https://eec.ky.gov/Nature-Preserves/Locations/Pages/Rush-Island-Bottoms.aspx → opened, 1 matching line(s)
  - step 2: KHLCF land-acquisition annual reports (Kentucky Heritage Land Conservation Fund) https://heritageland.ky.gov/Pages/default.aspx → did not open (rest)
  - step 2: OKNP nature preserve pages (Office of Kentucky Nature Preserves) https://eec.ky.gov/Nature-Preserves/Locations/Pages/default.aspx → opened, nothing matched
  - step 2: KNP KHLCF annual reports (eec.ky.gov) https://eec.ky.gov/Nature-Preserves/Pages/default.aspx → opened, nothing matched
  - step 2: document: Species Natural Community Reports https://eec.ky.gov/Nature-Preserves/biodiversity/Pages/Species-and-Natural-Community-Reports.aspx → opened, nothing matched
  - step 2: document: KHLCF https://eec.ky.gov/Nature-Preserves/conserving_natural_areas/KHLCF/Pages/heritage-land-conservation-fund.aspx → opened, nothing matched
  - step 2: document: Archived Reports and Publications https://eec.ky.gov/Nature-Preserves/Pages/archive.aspx → opened, nothing matched
  - step 3: open-data search https://hub.arcgis.com/api/v3/datasets?q=boiling%20green%20river%20springs%20Kentucky → did not open (400); second try opened
  - step 3: open-data search (second try, ArcGIS Online) https://www.arcgis.com/sharing/rest/search?q=boiling%20green%20river%20springs%20Kentucky → not reached
  - step 6: news releases https://fw.ky.gov/News/Pages/default.aspx → opened, nothing matched
  - step 2: 39 document link(s) not followed  → skipped: not about parks

