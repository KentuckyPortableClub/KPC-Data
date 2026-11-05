# PARK DETECTIVE: answers

Read 2026-11-05. REVIEW ONLY: nothing here is in a key. ANSWERED first (a find matches the question's own fact words), then PARTLY (context only: polygons under the pin, PAD-US, a size sentence, but not the thing asked), then NOT FOUND with what was tried. Partly and not found go to chats 8 / 11, then Brandon. Every step's find is listed so the chain can be followed; a quoted line is the source's own words; check the link before any use.

ℹ️ Maps and park info are a planning aid, not a guarantee. Always check the official agency map and rules before you go.

## pile-US-1034-tract: US-1034 Blue Springs State Park · tract · ANSWERED (step 2 agency documents)
- asked: pile solver: sgalb111 Blue Springs State Park - West Addition (rule 18: 'west' names only one piece) (pile solver v1)
- **tract: The Blue Springs School was first established in 1920 on land donated by Henry H.**
- "The Blue Springs School was first established in 1920 on land donated by Henry H."
- http://www.alabamapioneers.com/blue-springs-alabama-spring-moved-two-times-settling/ (read 2026-11-05)
- the chain:
  - step 4 PAD-US (context): PAD-US record under the pin: "Blue Springs State Park" managed by SPR, owner SPR, 706 acres · "Unit_Nm=Blue Springs State Park; Mang_Name=SPR; Own_Name=SPR; Own_Type=STAT; Des_Tp=SP; GIS_Acres=706; Category=Fee" · https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0
  - step 2 agency documents (answer): tract: The Blue Springs School was first established in 1920 on land donated by Henry H. · "The Blue Springs School was first established in 1920 on land donated by Henry H." · http://www.alabamapioneers.com/blue-springs-alabama-spring-moved-two-times-settling/
- steps tried:
  - step 1: point query at the pin https://conservationgis.alabama.gov/adcnrweb/rest/services/StateParks/MapServer/0 → nothing matched
  - step 1: point query at the pin https://conservationgis.alabama.gov/adcnrweb/rest/services/ForeverWildTracts/MapServer/0 → nothing matched
  - step 1: point query at the pin https://conservationgis.alabama.gov/adcnrweb/rest/services/WildlifeManagementAreas/MapServer/0 → nothing matched
  - step 1: point query at the pin https://conservationgis.alabama.gov/adcnrweb/rest/services/PublicFishingLakes/MapServer/1 → nothing matched
  - step 3: open-data search https://hub.arcgis.com/api/v3/datasets?q=blue%20springs%20Alabama → did not open (400); second try opened
  - step 3: open-data search (second try, ArcGIS Online) https://www.arcgis.com/sharing/rest/search?q=blue%20springs%20Alabama → 3 dataset(s), none official
  - step 4: PAD-US point query https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0 → 1 record(s)
  - step 2: agency park page https://www.alapark.com/parks/blue-springs-state-park → opened, nothing matched
  - step 2: document: history of Blue Springs State Park. http://www.alabamapioneers.com/blue-springs-alabama-spring-moved-two-times-settling/ → opened, 1 matching line(s)

## pile-US-11866-tract: US-11866 Rio Bonito Acquired Lands: Salazar Tract, BLM Recreation Management Area · tract · ANSWERED (step 1 our layers)
- asked: pile solver: rst13994 Rio Bonito Acquired Lands Tract 4 (the park is the piece 'salazar' of a bigger area; 'Rio Bonito Acquired Lands Tract 4' does not name that piece (rule 18)); rst14069 Rio Bonito Acquired Lands Tract 1 (the park is the piece 'salazar' of a bigger area; 'Rio Bonito Acquired Lands (pile solver v1)
- **polygon under the pin in a layer we read: "Rio Bonito Acquired Lands Tract 1", 261 ac**
- "FET_TYPE=4; FET_SUBTYPE=SRMA; FET_NAME=Rio Bonito Acquired Lands Tract 1; ADM_UNIT_CD=NMP01000; ADMIN_ST=NM; GIS_ACRES=260.60874151; DESCRIPTION=Roswell RMP (1997); WEB_LINK=https://www.blm.gov/office/roswell-field-office; WEB_DISPLAY=YES"
- https://gis.blm.gov/arcgis/rest/services/recreation/BLM_Natl_Recs_poly/MapServer/1 (read 2026-11-05)
- the chain:
  - step 1 our layers (answer): polygon under the pin in a layer we read: "Rio Bonito Acquired Lands Tract 1", 261 ac · "FET_TYPE=4; FET_SUBTYPE=SRMA; FET_NAME=Rio Bonito Acquired Lands Tract 1; ADM_UNIT_CD=NMP01000; ADMIN_ST=NM; GIS_ACRES=260.60874151; DESCRIPTION=Roswell RMP (19" · https://gis.blm.gov/arcgis/rest/services/recreation/BLM_Natl_Recs_poly/MapServer/1 · note: a different unit of the same park
- steps tried:
  - step 1: point query at the pin https://services2.arcgis.com/CjbW1bVhK4dB3WOa/arcgis/rest/services/State_Game_Commission_Lands_view/FeatureServer/6 → did not open
  - step 1: point query at the pin https://services7.arcgis.com/fdxAYNZ9OCyQZXdN/arcgis/rest/services/NM_State_Parks/FeatureServer/0 → did not open
  - step 1: point query at the pin https://gis.blm.gov/arcgis/rest/services/recreation/BLM_Natl_Recs_poly/MapServer/1 → 1 named polygon(s) of 1
  - step 1: point query at the pin https://gis.blm.gov/arcgis/rest/services/lands/BLM_Natl_ACEC/MapServer/0 → nothing matched

## q-green-river-sna-own-page: US-12752 Green River State Natural Area · acreage · ANSWERED (step 2 agency page)
- asked: the park's OWN Office of Kentucky Nature Preserves page and its total acreage over all three units (Davis Bend, Rush Island Bottoms, Boiling Springs); the site links Rush Island Bottoms' page only (chat 10 (Fable item 2))
- **agency page size: 440 acres (labelled size row)**
- "e hiking trails as well and canoe access. Access Type: Open to Public County: Hart Region: Green River Region Size: 440 Owner: ​Office of Kentucky Nature Preserves Manager: Nature Preseve Manager ​Office of Kentucky Nature Preserv"
- https://eec.ky.gov/Nature-Preserves/Locations/Pages/Rush-Island-Bottoms.aspx (read 2026-10-29)
- units: our outline holds 139 ac in 1 piece(s) vs the agency's "e hiking trails as well and canoe access. Access Type: Open to Public County: Hart Region: Green River Region Size: 440 " (https://eec.ky.gov/Nature-Preserves/Locations/Pages/Rush-Island-Bottoms.aspx) · pieces: Green River State Natural Area (Rush Island Bottoms) 139 ac
- the chain:
  - step 1 our layers (context): polygon under or near the pin in a layer we read: "Green River State Natural Area (Rush Island Bottoms)", 139 ac · "MA_ID=768.0; MANAME=Green River State Natural Area (Rush Island Bottoms); UNIT_TYPE=State Natural Area; MA_OWNER=Office of Kentucky Nature Preserves; MNG_INST=O" · https://kygisserver.ky.gov/arcgis/rest/services/WGS84WM_Services/Ky_KNP_Natural_Areas_WGS84WM/MapServer/0
  - step 4 PAD-US (context): PAD-US record under the pin: "Green River State Natural Area (Rush Island Bottoms)" managed by SDC, owner SDC, 139 acres · "Unit_Nm=Green River State Natural Area (Rush Island Bottoms); Mang_Name=SDC; Own_Name=SDC; Own_Type=STAT; Des_Tp=SCA; GIS_Acres=139; Category=Fee" · https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0
  - step 2 agency page (answer): agency page size: 440 acres (labelled size row) · "e hiking trails as well and canoe access. Access Type: Open to Public County: Hart Region: Green River Region Size: 440 Owner: ​Office of Kentucky Nature Preser" · https://eec.ky.gov/Nature-Preserves/Locations/Pages/Rush-Island-Bottoms.aspx
  - step 2 agency page (answer): agency page size: 200 acres (total-looking) · "Washington, DC, based nonprofit, has worked with the Hart County Historical Society to protect an additional 200 acres in the area. Access: Due to limited acces" · https://eec.ky.gov/Nature-Preserves/Locations/Pages/Rush-Island-Bottoms.aspx
- steps tried:
  - step 1: point query at the pin + within 2000 m https://kygisserver.ky.gov/arcgis/rest/services/WGS84WM_Services/Ky_State_Parks_Features_WGS84WM/MapServer/8 → nothing matched
  - step 1: point query at the pin + within 2000 m https://kygisserver.ky.gov/arcgis/rest/services/WGS84WM_Services/Ky_Public_Hunting_Areas_WGS84WM/MapServer/1 → nothing matched
  - step 1: point query at the pin + within 2000 m https://kygisserver.ky.gov/arcgis/rest/services/WGS84WM_Services/Ky_KNP_State_Nature_Preserves_WGS84WM/MapServer/0 → nothing matched
  - step 1: point query at the pin + within 2000 m https://kygisserver.ky.gov/arcgis/rest/services/WGS84WM_Services/Ky_KNP_Natural_Areas_WGS84WM/MapServer/0 → 1 named polygon(s) of 1
  - step 3: open-data search https://hub.arcgis.com/api/v3/datasets?q=green%20river%20Kentucky → did not open (400); second try opened
  - step 3: open-data search (second try, ArcGIS Online) https://www.arcgis.com/sharing/rest/search?q=green%20river%20Kentucky → 6 dataset(s), none official
  - step 4: PAD-US point query https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0 → 1 record(s)
  - step 2: agency park page https://eec.ky.gov/Nature-Preserves/Locations/Pages/Rush-Island-Bottoms.aspx → opened, nothing matched
  - step 2: 13 document link(s) not followed  → skipped: not about parks

## q2-boiling-springs-acreage: US-12752 Green River State Natural Area (Boiling Springs unit) · acreage · ANSWERED (step 2 agency page)
- asked: Boiling Springs unit size (the OKNP page says 440 acres?) (HQ (Brandon test case))
- **agency page size: 440 acres (labelled size row)**
- "e hiking trails as well and canoe access. Access Type: Open to Public County: Hart Region: Green River Region Size: 440 Owner: ​Office of Kentucky Nature Preserves Manager: Nature Preseve Manager ​Office of Kentucky Nature Preserv"
- https://eec.ky.gov/Nature-Preserves/Locations/Pages/Rush-Island-Bottoms.aspx (read 2026-10-29)
- units: our outline holds 139 ac in 1 piece(s) vs the agency's "e hiking trails as well and canoe access. Access Type: Open to Public County: Hart Region: Green River Region Size: 440 " (https://eec.ky.gov/Nature-Preserves/Locations/Pages/Rush-Island-Bottoms.aspx) · pieces: Green River State Natural Area (Rush Island Bottoms) 139 ac
- the chain:
  - step 1 our layers (context): polygon under or near the pin in a layer we read: "Green River State Natural Area (Rush Island Bottoms)", 139 ac · "MA_ID=768.0; MANAME=Green River State Natural Area (Rush Island Bottoms); UNIT_TYPE=State Natural Area; MA_OWNER=Office of Kentucky Nature Preserves; MNG_INST=O" · https://kygisserver.ky.gov/arcgis/rest/services/WGS84WM_Services/Ky_KNP_Natural_Areas_WGS84WM/MapServer/0 · note: a different unit of the same natural area
  - step 4 PAD-US (context): PAD-US record under the pin: "Green River State Natural Area (Rush Island Bottoms)" managed by SDC, owner SDC, 139 acres · "Unit_Nm=Green River State Natural Area (Rush Island Bottoms); Mang_Name=SDC; Own_Name=SDC; Own_Type=STAT; Des_Tp=SCA; GIS_Acres=139; Category=Fee" · https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0
  - step 2 agency page (answer): agency page size: 440 acres (labelled size row) · "e hiking trails as well and canoe access. Access Type: Open to Public County: Hart Region: Green River Region Size: 440 Owner: ​Office of Kentucky Nature Preser" · https://eec.ky.gov/Nature-Preserves/Locations/Pages/Rush-Island-Bottoms.aspx
  - step 2 agency page (answer): agency page size: 200 acres (total-looking) · "Washington, DC, based nonprofit, has worked with the Hart County Historical Society to protect an additional 200 acres in the area. Access: Due to limited acces" · https://eec.ky.gov/Nature-Preserves/Locations/Pages/Rush-Island-Bottoms.aspx
- steps tried:
  - step 1: point query at the pin + within 2000 m https://kygisserver.ky.gov/arcgis/rest/services/WGS84WM_Services/Ky_State_Parks_Features_WGS84WM/MapServer/8 → nothing matched
  - step 1: point query at the pin + within 2000 m https://kygisserver.ky.gov/arcgis/rest/services/WGS84WM_Services/Ky_Public_Hunting_Areas_WGS84WM/MapServer/1 → nothing matched
  - step 1: point query at the pin + within 2000 m https://kygisserver.ky.gov/arcgis/rest/services/WGS84WM_Services/Ky_KNP_State_Nature_Preserves_WGS84WM/MapServer/0 → nothing matched
  - step 1: point query at the pin + within 2000 m https://kygisserver.ky.gov/arcgis/rest/services/WGS84WM_Services/Ky_KNP_Natural_Areas_WGS84WM/MapServer/0 → 1 named polygon(s) of 1
  - step 3: open-data search https://hub.arcgis.com/api/v3/datasets?q=boiling%20green%20river%20springs%20Kentucky → did not open (400); second try opened
  - step 3: open-data search (second try, ArcGIS Online) https://www.arcgis.com/sharing/rest/search?q=boiling%20green%20river%20springs%20Kentucky → not reached
  - step 4: PAD-US point query https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0 → 1 record(s)
  - step 2: agency park page https://eec.ky.gov/Nature-Preserves/Locations/Pages/Rush-Island-Bottoms.aspx → opened, nothing matched
  - step 2: 13 document link(s) not followed  → skipped: not about parks

## pile-US-3000-tract: US-3000 Cooper Lake State Park · tract · ANSWERED (step 1 our layers)
- asked: pile solver: 261824 Cooper Lake State Park - South Sulphur Unit (rule 18: 'south' names only one piece) (pile solver v1)
- **polygon under the pin in a layer we read: "Cooper Lake SP-South Sulphur Unit", 1020 ac**
- "PH_UnitNum=1155; LocName=Cooper Lake SP-South Sulphur Unit; Class=Property Boundary; Active=Yes; Name_Acres=Cooper Lake SP-South Sulphur Unit - 1020 acres; Acres=1020; KMLDescrip=<strong>Cooper Lake SP-South Sulphur Unit - 1020 acres</stron"
- https://tpwd.texas.gov/arcgis/rest/services/Wildlife/TPWD_PublicHuntLocatorMap/MapServer/9 (read 2026-11-05)
- the chain:
  - step 1 our layers (answer): polygon under the pin in a layer we read: "Cooper Lake SP-South Sulphur Unit", 1020 ac · "PH_UnitNum=1155; LocName=Cooper Lake SP-South Sulphur Unit; Class=Property Boundary; Active=Yes; Name_Acres=Cooper Lake SP-South Sulphur Unit - 1020 acres; Acre" · https://tpwd.texas.gov/arcgis/rest/services/Wildlife/TPWD_PublicHuntLocatorMap/MapServer/9
- steps tried:
  - step 1: point query at the pin https://services1.arcgis.com/1mtXwieMId59thmg/arcgis/rest/services/Texas_State_Parks_Boundaries/FeatureServer/0 → did not open
  - step 1: point query at the pin https://tpwd.texas.gov/arcgis/rest/services/Wildlife/TPWD_PublicHuntLocatorMap/MapServer/9 → 1 named polygon(s) of 2
  - step 1: point query at the pin https://services1.arcgis.com/1mtXwieMId59thmg/arcgis/rest/services/WMA_Boundaries_4PublicDistribution/FeatureServer/0 → did not open
  - step 1: point query at the pin https://services1.arcgis.com/1mtXwieMId59thmg/arcgis/rest/services/Public_ConservationLands/FeatureServer/0 → did not open

## pile-US-4343-tract: US-4343 LaSage Unit of Wolf River Bottoms State Wildlife Area · tract · ANSWERED (step 1 our layers)
- asked: pile solver: 273010 Wolf River Bottoms Wildlife Area (the park is the piece 'lasage' of a bigger area; 'Wolf River Bottoms Wildlife Area' does not name that piece (rule 18)); wid713547 Wolf River Bottoms Wildlife Area (the park is the piece 'lasage' of a bigger area; 'Wolf River Bottoms Wildlife Are (pile solver v1)
- **polygon under the pin in a layer we read: "Wolf River Bottoms Wildlife Area", 3138 ac**
- "PROP_NAME=Wolf River Bottoms Wildlife Area; PROP_CODE=8905; PROP_ACRES=3138.17; TRANS_TYPE=1; PROGRAM=WM"
- https://dnrmaps.wi.gov/arcgis/rest/services/LF_DML/LF_AGOL_STAGING_WTM_Ext/MapServer/0 (read 2026-11-05)
- the chain:
  - step 1 our layers (answer): polygon under the pin in a layer we read: "Wolf River Bottoms Wildlife Area", 3138 ac · "PROP_NAME=Wolf River Bottoms Wildlife Area; PROP_CODE=8905; PROP_ACRES=3138.17; TRANS_TYPE=1; PROGRAM=WM" · https://dnrmaps.wi.gov/arcgis/rest/services/LF_DML/LF_AGOL_STAGING_WTM_Ext/MapServer/0
  - step 1 our layers (answer): polygon under the pin in a layer we read: "Wolf River Bottoms Wildlife Area", 60 ac · "TRANS_CONTROL_NO=80790; TRANS_TYPE_CODE=1; PROP_CODE=8905; EASE_USE_CODE=1111; PROP_NAME_CODE=89050000; PROP_NAME=Wolf River Bottoms Wildlife Area; PROP_NAME_LA" · https://dnrmaps.wi.gov/arcgis/rest/services/LF_DML/LF_AGOL_STAGING_WTM_Ext/MapServer/1
- steps tried:
  - step 1: point query at the pin https://dnrmaps.wi.gov/arcgis/rest/services/LF_DML/LF_AGOL_STAGING_WTM_Ext/MapServer/0 → 1 named polygon(s) of 1
  - step 1: point query at the pin https://dnrmaps.wi.gov/arcgis2/rest/services/PR_Recreation/PR_WSPS_Property_Info_WTM_Ext/MapServer/0 → nothing matched
  - step 1: point query at the pin https://dnrmaps.wi.gov/arcgis/rest/services/ER_Biotics/ER_Biotics_WGS84_Managed_Lands/MapServer/1 → nothing matched
  - step 1: point query at the pin https://dnrmaps.wi.gov/arcgis/rest/services/LF_DML/LF_AGOL_STAGING_WTM_Ext/MapServer/1 → 1 named polygon(s) of 1

## pile-US-6010-tract: US-6010 Deep Creek BLM Wilderness Area · tract · ANSWERED (step 2 agency page)
- asked: pile solver: wbl257 Deep Creek North (rule 18: 'north' names only one piece); wbl268 Deep Creek North (rule 18: 'north' names only one piece) (pile solver v1)
- **acreage: Deep Creek Wilderness and Deep Creek North Wilderness These two contiguous units, containing approximately 7,500 acres of public land, are located near the nort**
- "Deep Creek Wilderness and Deep Creek North Wilderness These two contiguous units, containing approximately 7,500 acres of public land, are located near the northeast corner of Zion National Park."
- https://www.blm.gov/visit/deep-creek-wilderness (read 2026-11-05)
- the chain:
  - step 4 PAD-US (context): PAD-US record under the pin: "St. George Field Office" managed by BLM, owner BLM, 629088 acres · "Unit_Nm=St. George Field Office; Mang_Name=BLM; Own_Name=BLM; Own_Type=FED; Des_Tp=PUB; GIS_Acres=629088; Category=Fee" · https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0
- steps tried:
  - step 1: point query at the pin https://services.arcgis.com/ZzrwjTRez6FJiOq4/arcgis/rest/services/Utah_State_Park_Management_Areas/FeatureServer/0 → did not open
  - step 1: point query at the pin https://services.arcgis.com/ZzrwjTRez6FJiOq4/arcgis/rest/services/WMAs_WFL1/FeatureServer/0 → did not open
  - step 1: point query at the pin https://services1.arcgis.com/99lidPhWCzftIe9K/arcgis/rest/services/Utah_National_Historic_Landmarks/FeatureServer/0 → did not open
  - step 1: point query at the pin https://gis.blm.gov/utarcgis/rest/services/Recreation/BLM_UT_RecAreas/MapServer/1 → nothing matched
  - step 3: open-data search https://hub.arcgis.com/api/v3/datasets?q=creek%20deep%20Utah → did not open (400); second try opened
  - step 3: open-data search (second try, ArcGIS Online) https://www.arcgis.com/sharing/rest/search?q=creek%20deep%20Utah → 1 dataset(s), none official
  - step 4: PAD-US point query https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0 → 1 record(s)
  - step 2: agency park page https://www.blm.gov/visit/deep-creek-wilderness → opened, 1 matching line(s)
  - step 2: 4 document link(s) not followed  → skipped: not about parks

## q-little-south-fork-sna-own-page: US-7962 Little South Fork State Natural Area · acreage · ANSWERED (step 2 agency page)
- asked: the park's OWN Office of Kentucky Nature Preserves page and its acreage; the site links the Burnett WWCA page, a different area (chat 10 (Fable item 2))
- **agency page size: 3145.42 acres (labelled size row)**
- "restoration and access issues are completed. Access Type: Open to Public County: Wayne Region: Eastern Region Size: 3145.42 Owner: Office of Kentucky Nature Preserves Manager: Nature Preseve Manager ​Office of Kentucky Nature Preserve"
- https://eec.ky.gov/Nature-Preserves/Locations/Pages/Burnett-WWCA.aspx (read 2026-10-29)
- units: our outline holds 2231 ac in 1 piece(s) vs the agency's "restoration and access issues are completed. Access Type: Open to Public County: Wayne Region: Eastern Region Size: 3145" (https://eec.ky.gov/Nature-Preserves/Locations/Pages/Burnett-WWCA.aspx) · pieces: Little South Fork State Natural Area (Steele Hollow SNA) 2231 ac
- the chain:
  - step 1 our layers (context): polygon under or near the pin in a layer we read: "Little South Fork State Natural Area (Steele Hollow SNA)", 2231 ac · "MA_ID=654.0; MANAME=Little South Fork State Natural Area (Steele Hollow SNA); UNIT_TYPE=State Natural Area; MA_OWNER=Office of Kentucky Nature Preserves; MNG_IN" · https://kygisserver.ky.gov/arcgis/rest/services/WGS84WM_Services/Ky_KNP_Natural_Areas_WGS84WM/MapServer/0
  - step 2 agency page (answer): agency page size: 3145.42 acres (labelled size row) · "restoration and access issues are completed. Access Type: Open to Public County: Wayne Region: Eastern Region Size: 3145.42 Owner: Office of Kentucky Nature Pre" · https://eec.ky.gov/Nature-Preserves/Locations/Pages/Burnett-WWCA.aspx
- steps tried:
  - step 1: point query at the pin + within 2000 m https://kygisserver.ky.gov/arcgis/rest/services/WGS84WM_Services/Ky_State_Parks_Features_WGS84WM/MapServer/8 → nothing matched
  - step 1: point query at the pin + within 2000 m https://kygisserver.ky.gov/arcgis/rest/services/WGS84WM_Services/Ky_Public_Hunting_Areas_WGS84WM/MapServer/1 → opened, nothing matched the name
  - step 1: point query at the pin + within 2000 m https://kygisserver.ky.gov/arcgis/rest/services/WGS84WM_Services/Ky_KNP_State_Nature_Preserves_WGS84WM/MapServer/0 → nothing matched
  - step 1: point query at the pin + within 2000 m https://kygisserver.ky.gov/arcgis/rest/services/WGS84WM_Services/Ky_KNP_Natural_Areas_WGS84WM/MapServer/0 → 1 named polygon(s) of 1
  - step 3: open-data search https://hub.arcgis.com/api/v3/datasets?q=fork%20little%20south%20Kentucky → did not open (400); second try opened
  - step 3: open-data search (second try, ArcGIS Online) https://www.arcgis.com/sharing/rest/search?q=fork%20little%20south%20Kentucky → 4 dataset(s), none official
  - step 4: PAD-US point query https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0 → nothing under the pin
  - step 2: agency park page https://eec.ky.gov/Nature-Preserves/Locations/Pages/Burnett-WWCA.aspx → opened, nothing matched
  - step 2: 13 document link(s) not followed  → skipped: not about parks

## pile-US-0550-tract: US-0550 Lower Rio Grande Valley National Wildlife Refuge · tract · PARTLY
- asked: pile solver: sgtxb1730 Lower Rio Grande Valley NWR-La Casita East (rule 18: 'east' names only one piece) (pile solver v1)
- context only: tried steps 1, 2, 3, 4
- the chain:
  - step 4 PAD-US (context): PAD-US record under the pin: "Lower Rio Grande Valley National Wildlife Refuge" managed by FWS, owner FWS, 88266 acres · "Unit_Nm=Lower Rio Grande Valley National Wildlife Refuge; Mang_Name=FWS; Own_Name=FWS; Own_Type=FED; Des_Tp=NWR; GIS_Acres=88266; Category=Fee" · https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0
  - step 4 PAD-US (context): PAD-US record under the pin: "Lower Rio Grande Valley National Wildlife Refuge" managed by FWS, owner FWS, 89898 acres · "Unit_Nm=Lower Rio Grande Valley National Wildlife Refuge; Mang_Name=FWS; Own_Name=FWS; Own_Type=FED; Des_Tp=NWR; GIS_Acres=89898; Category=Fee" · https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0
- steps tried:
  - step 1: point query at the pin https://services1.arcgis.com/1mtXwieMId59thmg/arcgis/rest/services/Texas_State_Parks_Boundaries/FeatureServer/0 → did not open
  - step 1: point query at the pin https://tpwd.texas.gov/arcgis/rest/services/Wildlife/TPWD_PublicHuntLocatorMap/MapServer/9 → nothing matched
  - step 1: point query at the pin https://services1.arcgis.com/1mtXwieMId59thmg/arcgis/rest/services/WMA_Boundaries_4PublicDistribution/FeatureServer/0 → did not open
  - step 1: point query at the pin https://services1.arcgis.com/1mtXwieMId59thmg/arcgis/rest/services/Public_ConservationLands/FeatureServer/0 → did not open
  - step 3: open-data search https://hub.arcgis.com/api/v3/datasets?q=grande%20lower%20rio%20valley%20Texas → did not open (400); second try opened
  - step 3: open-data search (second try, ArcGIS Online) https://www.arcgis.com/sharing/rest/search?q=grande%20lower%20rio%20valley%20Texas → 6 dataset(s), none official
  - step 4: PAD-US point query https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0 → 2 record(s)
  - step 2: agency park page https://www.fws.gov/refuge/lower-rio-grande-valley → opened, nothing matched
  - step 2: document: Report a Crime https://www.fws.gov/wildlife-crime-tips → opened, nothing matched

## pile-US-0974-tract: US-0974 Tule Springs Fossil Beds National Monument · tract · PARTLY
- asked: pile solver: sgnvd6 Tule Springs Fossil Beds National Monument South (rule 18: 'south' names only one piece); sgnvb6 Tule Springs Fossil Beds National Monument South (rule 18: 'south' names only one piece) (pile solver v1)
- context only: tried steps 1, 2, 3, 4
- the chain:
  - step 4 PAD-US (context): PAD-US record under the pin: "Tule Springs Fossil Beds National Monument" managed by NPS, owner NPS, 22696 acres · "Unit_Nm=Tule Springs Fossil Beds National Monument; Mang_Name=NPS; Own_Name=NPS; Own_Type=FED; Des_Tp=NM; GIS_Acres=22696; Category=Fee" · https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0
- steps tried:
  - step 1: point query at the pin https://services.arcgis.com/RyxlXSfFi87rAosq/arcgis/rest/services/Wildlife_Management_Areas/FeatureServer/0 → did not open
  - step 1: point query at the pin https://arcgis.water.nv.gov/arcgis/rest/services/Hosted/SCORPRecAreas_Master/FeatureServer/0 → nothing matched
  - step 1: point query at the pin https://services7.arcgis.com/5hLFVlePaucIMGhw/arcgis/rest/services/VS_Boundary_Map_2_WFL1/FeatureServer/2 → did not open
  - step 1: point query at the pin https://arcgis.water.nv.gov/arcgis/rest/services/Hosted/SCORP_Recreation_Areas/FeatureServer/0 → nothing matched
  - step 3: open-data search https://hub.arcgis.com/api/v3/datasets?q=beds%20fossil%20springs%20tule%20Nevada → did not open (400); second try opened
  - step 3: open-data search (second try, ArcGIS Online) https://www.arcgis.com/sharing/rest/search?q=beds%20fossil%20springs%20tule%20Nevada → 4 dataset(s), none official
  - step 4: PAD-US point query https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0 → 1 record(s)
  - step 2: agency park page https://www.nps.gov/tusk/index.htm → opened, nothing matched

## pile-US-10565-tract: US-10565 Stuart's Landing North State Conservation Area · tract · PARTLY
- asked: pile solver: 190447 Stuarts Landing Conservation Area (rule 18: 'north' names only one piece) (pile solver v1)
- context only: tried steps 1, 2, 3, 4, 6
- the chain:
  - step 4 PAD-US (context): PAD-US record under the pin: "Stuarts Landing Conservation Area" managed by RWD, owner RWD, 338 acres · "Unit_Nm=Stuarts Landing Conservation Area; Mang_Name=RWD; Own_Name=RWD; Own_Type=DIST; Des_Tp=LCA; GIS_Acres=338; Category=Fee" · https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0
- steps tried:
  - step 1: point query at the pin https://ca.dep.state.fl.us/arcgis/rest/services/OpenData/PARKS_BOUNDARIES/MapServer/0 → nothing matched
  - step 1: point query at the pin https://services3.arcgis.com/XYg2eF8UuxZVuVmF/arcgis/rest/services/Florida_State_Forests/FeatureServer/0 → did not open
  - step 1: point query at the pin https://services1.arcgis.com/59dBAbzYnRk8johU/arcgis/rest/services/SRWMD_LM_Ownership/FeatureServer/0 → did not open
  - step 1: point query at the pin https://services.arcgis.com/s8wtJX9suxFen6TA/arcgis/rest/services/SJRWMD_Management_Area_viewLayer/FeatureServer/0 → did not open
  - step 3: open-data search https://hub.arcgis.com/api/v3/datasets?q=landing%20north%20stuarts%20Florida → did not open (400); second try opened
  - step 3: open-data search (second try, ArcGIS Online) https://www.arcgis.com/sharing/rest/search?q=landing%20north%20stuarts%20Florida → 6 dataset(s), none official
  - step 4: PAD-US point query https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0 → 1 record(s)
  - step 2: agency park page https://map.mysuwanneeriver.com/tracts/stuarts-landing-north/ → opened, nothing matched
  - step 6: news releases https://www.floridastateparks.org/news → did not open (HTTP 403)
  - step 2: 1 document link(s) not followed  → skipped: not about parks

## pile-US-10566-tract: US-10566 Stuart's Landing South State Conservation Area · tract · PARTLY
- asked: pile solver: 190447 Stuarts Landing Conservation Area (rule 18: 'south' names only one piece) (pile solver v1)
- context only: tried steps 1, 2, 3, 4, 6
- the chain:
  - step 4 PAD-US (context): PAD-US record under the pin: "Stuarts Landing Conservation Area" managed by RWD, owner RWD, 338 acres · "Unit_Nm=Stuarts Landing Conservation Area; Mang_Name=RWD; Own_Name=RWD; Own_Type=DIST; Des_Tp=LCA; GIS_Acres=338; Category=Fee" · https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0
- steps tried:
  - step 1: point query at the pin https://ca.dep.state.fl.us/arcgis/rest/services/OpenData/PARKS_BOUNDARIES/MapServer/0 → nothing matched
  - step 1: point query at the pin https://services3.arcgis.com/XYg2eF8UuxZVuVmF/arcgis/rest/services/Florida_State_Forests/FeatureServer/0 → did not open
  - step 1: point query at the pin https://services1.arcgis.com/59dBAbzYnRk8johU/arcgis/rest/services/SRWMD_LM_Ownership/FeatureServer/0 → did not open
  - step 1: point query at the pin https://services.arcgis.com/s8wtJX9suxFen6TA/arcgis/rest/services/SJRWMD_Management_Area_viewLayer/FeatureServer/0 → did not open
  - step 3: open-data search https://hub.arcgis.com/api/v3/datasets?q=landing%20south%20stuarts%20Florida → did not open (400); second try opened
  - step 3: open-data search (second try, ArcGIS Online) https://www.arcgis.com/sharing/rest/search?q=landing%20south%20stuarts%20Florida → 6 dataset(s), none official
  - step 4: PAD-US point query https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0 → 1 record(s)
  - step 2: agency park page https://map.mysuwanneeriver.com/tracts/stuarts-landing-south/ → opened, nothing matched
  - step 6: news releases https://www.floridastateparks.org/news → did not open (HTTP 403)
  - step 2: 1 document link(s) not followed  → skipped: not about parks

## pile-US-10615-tract: US-10615 Cypress Creek South State Conservation Area · tract · PARTLY
- asked: pile solver: 190420 Cypress Creek Conservation Area (rule 18: 'south' names only one piece) (pile solver v1)
- context only: tried steps 1, 2, 3, 4, 6
- the chain:
  - step 4 PAD-US (context): PAD-US record under the pin: "Cypress Creek Conservation Area" managed by RWD, owner RWD, 1339 acres · "Unit_Nm=Cypress Creek Conservation Area; Mang_Name=RWD; Own_Name=RWD; Own_Type=DIST; Des_Tp=LCA; GIS_Acres=1339; Category=Fee" · https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0
  - step 2 agency page (context): tract: On the Cypress Creek South Tract visitors may launch a canoe, enjoy fishing, hiking and wildlife viewing. · "On the Cypress Creek South Tract visitors may launch a canoe, enjoy fishing, hiking and wildlife viewing." · https://map.mysuwanneeriver.com/tracts/cypress-creek-south/
  - step 2 agency page (context): tract: Cypress Creek South Tract from White Springs: · "Cypress Creek South Tract from White Springs:" · https://map.mysuwanneeriver.com/tracts/cypress-creek-south/
- steps tried:
  - step 1: point query at the pin https://ca.dep.state.fl.us/arcgis/rest/services/OpenData/PARKS_BOUNDARIES/MapServer/0 → nothing matched
  - step 1: point query at the pin https://services3.arcgis.com/XYg2eF8UuxZVuVmF/arcgis/rest/services/Florida_State_Forests/FeatureServer/0 → did not open
  - step 1: point query at the pin https://services1.arcgis.com/59dBAbzYnRk8johU/arcgis/rest/services/SRWMD_LM_Ownership/FeatureServer/0 → did not open
  - step 1: point query at the pin https://services.arcgis.com/s8wtJX9suxFen6TA/arcgis/rest/services/SJRWMD_Management_Area_viewLayer/FeatureServer/0 → did not open
  - step 3: open-data search https://hub.arcgis.com/api/v3/datasets?q=creek%20cypress%20south%20Florida → did not open (400); second try opened
  - step 3: open-data search (second try, ArcGIS Online) https://www.arcgis.com/sharing/rest/search?q=creek%20cypress%20south%20Florida → 3 dataset(s), none official
  - step 4: PAD-US point query https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0 → 1 record(s)
  - step 2: agency park page https://map.mysuwanneeriver.com/tracts/cypress-creek-south/ → opened, 2 matching line(s)
  - step 6: news releases https://www.floridastateparks.org/news → did not open (rest)
  - step 2: 1 document link(s) not followed  → skipped: not about parks

## pile-US-10786-tract: US-10786 Siloam Springs Buckhorn Unit State Park · tract · PARTLY
- asked: pile solver: sgila1569 Siloam Springs State Park (the park is the piece 'buckhorn' of a bigger area; 'Siloam Springs State Park' does not name that piece (rule 18)); 70901 Siloam Springs State Park (the park is the piece 'buckhorn' of a bigger area; 'Siloam Springs State Park' does not name that pie (pile solver v1)
- context only: tried steps 1, 2, 3, 4
- the chain:
  - step 1 our layers (context): polygon under the pin in a layer we read: "Siloam Springs", 10194 ac · "CLASSIFICATION=SP; REGION=4; SITE_NAME=Siloam Springs; GIS_ACRES=10193.9610753008" · https://maps.dnr.illinois.gov/geoservices/rest/services/BaseLayers/MapServer/11
  - step 4 PAD-US (context): PAD-US record under the pin: "Siloam Springs State Park" managed by SDNR, owner OTHS, 5854 acres · "Unit_Nm=Siloam Springs State Park; Mang_Name=SDNR; Own_Name=OTHS; Own_Type=STAT; Des_Tp=SP; GIS_Acres=5854; Category=Fee" · https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0
- steps tried:
  - step 1: point query at the pin https://services.arcgis.com/b9DHj1BjfdLLFv11/arcgis/rest/services/IllinoisProtectedLandsDH_1_22/FeatureServer/0 → did not open
  - step 1: point query at the pin https://services.arcgis.com/b9DHj1BjfdLLFv11/arcgis/rest/services/IllinoisProtectedLandsDH_1_22/FeatureServer/3 → did not open
  - step 1: point query at the pin https://maps.dnr.illinois.gov/geoservices/rest/services/BaseLayers/MapServer/11 → 1 named polygon(s) of 1
  - step 3: open-data search https://hub.arcgis.com/api/v3/datasets?q=buckhorn%20siloam%20springs%20Illinois → did not open (400); second try opened
  - step 3: open-data search (second try, ArcGIS Online) https://www.arcgis.com/sharing/rest/search?q=buckhorn%20siloam%20springs%20Illinois → not reached
  - step 4: PAD-US point query https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0 → 1 record(s)
  - step 2: agency park page https://huntillinois.org/sites/siloam-springs-sp/ → opened, nothing matched
  - step 2: document: Printable Map https://ngrrec-hunt-illinois-wordpress-images.s3.amazonaws.com/wp-content/uploads/2023/01/17125724/SiloamSpringsHunterMap.pdf → did not open (robots-unreadable)
  - step 2: document: Conservation Police https://dnr.illinois.gov/content/dam/soi/en/web/dnr/lawenforcement/documents/districtcpophonesandemails.pdf → opened, nothing matched
  - step 2: 1 document link(s) not followed  → skipped: not about parks

## pile-US-1126-tract: US-1126 Anza Borrego Desert State Park · tract · PARTLY
- asked: pile solver: sgcab878 Anza-Borrego Desert SW (rule 18: 'southwest' names only one piece) (pile solver v1)
- context only: tried steps 1, 2, 3, 4
- the chain:
  - step 4 PAD-US (context): PAD-US record under the pin: "Anza-Borrego Desert State Park" managed by SPR, owner SPR, 582519 acres · "Unit_Nm=Anza-Borrego Desert State Park; Mang_Name=SPR; Own_Name=SPR; Own_Type=STAT; Des_Tp=SP; GIS_Acres=582519; Category=Fee" · https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0
- steps tried:
  - step 1: point query at the pin https://services2.arcgis.com/Uq9r85Potqm3MfRV/arcgis/rest/services/biosds3077_fpu/FeatureServer/0 → did not open
  - step 1: point query at the pin https://services2.arcgis.com/Uq9r85Potqm3MfRV/ArcGIS/rest/services/ParkBoundaries/FeatureServer/0 → did not open
  - step 1: point query at the pin https://services.arcgis.com/QVENGdaPbd4LUkLV/arcgis/rest/services/FWSApproved_Authoritative/FeatureServer/0 → did not open
  - step 1: point query at the pin https://services2.arcgis.com/Uq9r85Potqm3MfRV/arcgis/rest/services/biosds3092_fpu/FeatureServer/0 → did not open
  - step 3: open-data search https://hub.arcgis.com/api/v3/datasets?q=anza%20borrego%20desert%20California → did not open (400); second try opened
  - step 3: open-data search (second try, ArcGIS Online) https://www.arcgis.com/sharing/rest/search?q=anza%20borrego%20desert%20California → 6 dataset(s), none official
  - step 4: PAD-US point query https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0 → 1 record(s)
  - step 2: agency park page https://www.parks.ca.gov/?page_id=638 → opened, nothing matched
  - step 2: document: English https://theabf.org/wp-content/uploads/2020/11/7-Principles_8.5x11-AnzaBorrego-English.pdf → did not open (HTTP 404)
  - step 2: document: Spanish https://theabf.org/wp-content/uploads/2020/11/7-Principles_8.5x11-AnzaBorrego-spanish.pdf → did not open (HTTP 404)
  - step 2: document: English https://theabf.org/wp-content/uploads/2020/11/Covid-19-AnzaBorego-8.5x11-English.pdf → did not open (HTTP 404)
  - step 2: 1 document link(s) not followed  → skipped: not about parks

## pile-US-11806-tract: US-11806 Johnson (Gordy's) Hill BLM Recreation Management Area · tract · PARTLY
- asked: pile solver: rst14034 Johnson (Gordy's) Hill North (rule 18: 'north' names only one piece); rst13973 Johnson (Gordy's) Hill South (rule 18: 'south' names only one piece) (pile solver v1)
- context only: tried steps 1, 2, 3, 4
- the chain:
  - step 4 PAD-US (context): PAD-US record under the pin: "Socorro Field Office" managed by BLM, owner BLM, 1508543 acres · "Unit_Nm=Socorro Field Office; Mang_Name=BLM; Own_Name=BLM; Own_Type=FED; Des_Tp=PUB; GIS_Acres=1508543; Category=Fee" · https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0
- steps tried:
  - step 1: point query at the pin https://services2.arcgis.com/CjbW1bVhK4dB3WOa/arcgis/rest/services/State_Game_Commission_Lands_view/FeatureServer/6 → did not open
  - step 1: point query at the pin https://services7.arcgis.com/fdxAYNZ9OCyQZXdN/arcgis/rest/services/NM_State_Parks/FeatureServer/0 → did not open
  - step 1: point query at the pin https://gis.blm.gov/arcgis/rest/services/recreation/BLM_Natl_Recs_poly/MapServer/1 → opened, nothing matched the name
  - step 1: point query at the pin https://gis.blm.gov/arcgis/rest/services/lands/BLM_Natl_ACEC/MapServer/0 → nothing matched
  - step 3: open-data search https://hub.arcgis.com/api/v3/datasets?q=gordys%20hill%20johnson%20New%20Mexico → did not open (400); second try opened
  - step 3: open-data search (second try, ArcGIS Online) https://www.arcgis.com/sharing/rest/search?q=gordys%20hill%20johnson%20New%20Mexico → not reached
  - step 4: PAD-US point query https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0 → 1 record(s)
  - step 2: agency park page https://www.blm.gov/visit/johnson-gordys-hill-ohv-area → opened, nothing matched
  - step 2: document: Johnson (Gordy's) Hill https://www.blm.gov/sites/default/files/docs/2022-11/map-johnson-gordys-hill-socorro-2022.pdf → opened, nothing matched
  - step 2: document: Contracting https://www.blm.gov/services/acquisition/contracting → opened, nothing matched
  - step 2: 4 document link(s) not followed  → skipped: not about parks

## pile-US-11889-tract: US-11889 Piceance State Wildlife Area · tract · PARTLY
- asked: pile solver: sgcoa224 Piceance SWA - North Ridge Unit (rule 18: 'north' names only one piece); sgcoc618 Piceance SWA - North Ridge Unit (rule 18: 'north' names only one piece); sgcod270 Piceance SWA - North Ridge Unit (rule 18: 'north' names only one piece) (pile solver v1)
- context only: tried steps 1, 2, 3, 4
- the chain:
  - step 4 PAD-US (context): PAD-US record under the pin: "White River Field Office" managed by BLM, owner BLM, 1450231 acres · "Unit_Nm=White River Field Office; Mang_Name=BLM; Own_Name=BLM; Own_Type=FED; Des_Tp=PUB; GIS_Acres=1450231; Category=Fee" · https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0
  - step 2 agency page (context): tract: The entire Piceance SWA includes several parcels. · "The entire Piceance SWA includes several parcels." · https://cpw.state.co.us/state-wildlife-areas/piceance-swa
- steps tried:
  - step 1: point query at the pin https://gis.colorado.gov/public/rest/services/OIT/Colorado_State_Basemap/MapServer/30 → nothing matched
  - step 1: point query at the pin https://gis.colorado.gov/public/rest/services/OIT/Colorado_State_Basemap/MapServer/41 → nothing matched
  - step 1: point query at the pin https://services5.arcgis.com/ttNGmDvKQA7oeDQ3/arcgis/rest/services/CPWAdminData/FeatureServer/5 → did not open
  - step 1: point query at the pin https://services1.arcgis.com/fBc8EJBxQRMcHlei/arcgis/rest/services/NPS_Land_Resources_Division_Boundary_and_Tract_Data_Service/FeatureServer/2 → did not open
  - step 3: open-data search https://hub.arcgis.com/api/v3/datasets?q=piceance%20Colorado → did not open (400); second try opened
  - step 3: open-data search (second try, ArcGIS Online) https://www.arcgis.com/sharing/rest/search?q=piceance%20Colorado → 6 dataset(s), none official
  - step 4: PAD-US point query https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0 → 1 record(s)
  - step 2: agency park page https://cpw.state.co.us/state-wildlife-areas/piceance-swa → opened, 1 matching line(s)
  - step 2: document: Download Map https://cpw.state.co.us/sites/default/files/dam/q3uei2ss2z/piceanceswa_geo.pdf → opened, nothing matched
  - step 2: document: Interactive Map http://ndismaps.nrel.colostate.edu/huntingatlas/index.aspx?keyword=public&value=Piceance%20SWA%20-%20Little%20Hills%20Unithttp://ndismaps.nrel.colostate.edu/propertyfinder/index.aspx?keyword=public&value=Piceance%20SWA%20-%20Square%20S%20Summer%20Range%20Unithttp://ndismaps.nrel.colostate.edu/propertyfinder/index.aspx?keyword=public&value=Piceance%20SWA%20-%20Yellow%20Creek%20Unit → opened, nothing matched
  - step 2: document: Recreational Lands Brochure https://cpw.widencollective.com/assets/share/asset/gsnot12u9n → did not open (robots)
  - step 2: 8 document link(s) not followed  → skipped: not about parks

## pile-US-11906-tract: US-11906 Bangs BLM Special Recreation Management Area · tract · PARTLY
- asked: pile solver: rma13830 Bangs - North Zone 2 (rule 18: 'north' names only one piece); rst13830 Bangs - North Zone 2 (rule 18: 'north' names only one piece) (pile solver v1)
- context only: tried steps 1, 2, 3, 4
- the chain:
  - step 4 PAD-US (context): PAD-US record under the pin: "Grand Junction Field Office" managed by BLM, owner BLM, 1275594 acres · "Unit_Nm=Grand Junction Field Office; Mang_Name=BLM; Own_Name=BLM; Own_Type=FED; Des_Tp=PUB; GIS_Acres=1275594; Category=Fee" · https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0
- steps tried:
  - step 1: point query at the pin https://gis.colorado.gov/public/rest/services/OIT/Colorado_State_Basemap/MapServer/30 → nothing matched
  - step 1: point query at the pin https://gis.colorado.gov/public/rest/services/OIT/Colorado_State_Basemap/MapServer/41 → nothing matched
  - step 1: point query at the pin https://services5.arcgis.com/ttNGmDvKQA7oeDQ3/arcgis/rest/services/CPWAdminData/FeatureServer/5 → did not open
  - step 1: point query at the pin https://services1.arcgis.com/fBc8EJBxQRMcHlei/arcgis/rest/services/NPS_Land_Resources_Division_Boundary_and_Tract_Data_Service/FeatureServer/2 → did not open
  - step 3: open-data search https://hub.arcgis.com/api/v3/datasets?q=bangs%20special%20Colorado → did not open (400); second try opened
  - step 3: open-data search (second try, ArcGIS Online) https://www.arcgis.com/sharing/rest/search?q=bangs%20special%20Colorado → 1 dataset(s), none official
  - step 4: PAD-US point query https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0 → 1 record(s)
  - step 2: agency park page https://www.blm.gov/documents/grand-junction-fo/public-room/map/bangs-special-recreation-management-area-overview-map → opened, nothing matched
  - step 2: document: Bangs Special Recreation Management Area: Overview Map (PDF  https://www.blm.gov/sites/default/files/docs/2021-09/GJFO_Bangs_Map_20210910.pdf → opened, nothing matched
  - step 2: document: Contracting https://www.blm.gov/services/acquisition/contracting → opened, nothing matched
  - step 2: 4 document link(s) not followed  → skipped: not about parks

## pile-US-12285-tract: US-12285 Shillapoo South Wildlife Area State Wildlife Area · tract · PARTLY
- asked: pile solver: wdw158 Shillapoo (rule 18: 'south' names only one piece); wdw159 Shillapoo (rule 18: 'south' names only one piece); wdw160 Shillapoo (rule 18: 'south' names only one piece); sgwab181 Shillapoo (rule 18: 'south' names only one piece) (pile solver v1)
- context only: tried steps 1, 2, 3, 4
- the chain:
  - step 1 our layers (context): polygon under the pin in a layer we read: "Shillapoo" · "ManagedPlaceOID=181; ManagedPlaceName=Shillapoo; PlaceTypeID=1; PlaceTypeName=Wildlife Area; Region=Region 5 - Southwest; MilesOfRoadsAndTrails=4.06; ParkingLot" · https://geodataservices.wdfw.wa.gov/arcgis/rest/services/WP_RealEstate/ManagedPlaces/MapServer/0
  - step 1 our layers (context): polygon under the pin in a layer we read: "Shillapoo South" · "ManagedPlaceOID=1432; ManagedPlaceName=Shillapoo South; PlaceTypeID=2; PlaceTypeName=Wildlife Area Unit; Region=Region 5 - Southwest; MilesOfRoadsAndTrails=0.91" · https://geodataservices.wdfw.wa.gov/arcgis/rest/services/WP_RealEstate/ManagedPlaces/MapServer/0
  - step 2 agency page (context): tract: The Shillapoo South Unit was acquired to protect and enhance wintering waterfowl habitat, waterfowl production, and waterfowl hunting. · "The Shillapoo South Unit was acquired to protect and enhance wintering waterfowl habitat, waterfowl production, and waterfowl hunting." · https://wdfw.wa.gov/places-to-go/wildlife-areas/shillapoo-south-wildlife-area-unit
- steps tried:
  - step 1: point query at the pin https://services5.arcgis.com/4LKAHwqnBooVDUlX/arcgis/rest/services/ParkBoundaries/FeatureServer/2 → did not open
  - step 1: point query at the pin https://geodataservices.wdfw.wa.gov/arcgis/rest/services/WP_RealEstate/ManagedPlaces/MapServer/0 → 2 named polygon(s) of 2
  - step 1: point query at the pin https://gis.dnr.wa.gov/site3/rest/services/Public_Boundaries/WADNR_PUBLIC_Cadastre_OpenData/MapServer/6 → nothing matched
  - step 1: point query at the pin https://gis.dnr.wa.gov/site3/rest/services/Public_Boundaries/WADNR_PUBLIC_Major_Public_Lands_NonDNR/MapServer/1 → nothing matched
  - step 3: open-data search https://hub.arcgis.com/api/v3/datasets?q=shillapoo%20south%20Washington → did not open (400); second try opened
  - step 3: open-data search (second try, ArcGIS Online) https://www.arcgis.com/sharing/rest/search?q=shillapoo%20south%20Washington → not reached
  - step 4: PAD-US point query https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0 → nothing under the pin
  - step 2: agency park page https://wdfw.wa.gov/places-to-go/wildlife-areas/shillapoo-south-wildlife-area-unit → opened, 1 matching line(s)
  - step 2: document: 2018 https://wdfw.wa.gov/sites/default/files/2020-01/2017-18_shillapoo_wildlife_area_update.pdf → opened, nothing matched
  - step 2: document: 2017 https://wdfw.wa.gov/sites/default/files/publications/00536/shillapoo_2017update.pdf → opened, nothing matched
  - step 2: document: 2014 https://wdfw.wa.gov/sites/default/files/publications/00536/shillapoo_2014update.pdf → opened, nothing matched
  - step 2: 4 document link(s) not followed  → skipped: not about parks

## pile-US-12286-tract: US-12286 Shillapoo North Wildlife Area State Wildlife Area · tract · PARTLY
- asked: pile solver: wdw158 Shillapoo (rule 18: 'north' names only one piece); wdw159 Shillapoo (rule 18: 'north' names only one piece); wdw160 Shillapoo (rule 18: 'north' names only one piece); sgwab181 Shillapoo (rule 18: 'north' names only one piece) (pile solver v1)
- context only: tried steps 1, 2, 3, 4
- the chain:
  - step 1 our layers (context): polygon under the pin in a layer we read: "Shillapoo" · "ManagedPlaceOID=181; ManagedPlaceName=Shillapoo; PlaceTypeID=1; PlaceTypeName=Wildlife Area; Region=Region 5 - Southwest; MilesOfRoadsAndTrails=4.06; ParkingLot" · https://geodataservices.wdfw.wa.gov/arcgis/rest/services/WP_RealEstate/ManagedPlaces/MapServer/0
  - step 1 our layers (context): polygon under the pin in a layer we read: "Shillapoo North" · "ManagedPlaceOID=1431; ManagedPlaceName=Shillapoo North; PlaceTypeID=2; PlaceTypeName=Wildlife Area Unit; Region=Region 5 - Southwest; MilesOfRoadsAndTrails=1.62" · https://geodataservices.wdfw.wa.gov/arcgis/rest/services/WP_RealEstate/ManagedPlaces/MapServer/0
  - step 2 agency page (context): tract: The Shillapoo North Unit was acquired to protect and enhance wintering waterfowl habitat. · "The Shillapoo North Unit was acquired to protect and enhance wintering waterfowl habitat." · https://wdfw.wa.gov/places-to-go/wildlife-areas/shillapoo-north-wildlife-area-unit
- steps tried:
  - step 1: point query at the pin https://services5.arcgis.com/4LKAHwqnBooVDUlX/arcgis/rest/services/ParkBoundaries/FeatureServer/2 → did not open
  - step 1: point query at the pin https://geodataservices.wdfw.wa.gov/arcgis/rest/services/WP_RealEstate/ManagedPlaces/MapServer/0 → 2 named polygon(s) of 2
  - step 1: point query at the pin https://gis.dnr.wa.gov/site3/rest/services/Public_Boundaries/WADNR_PUBLIC_Cadastre_OpenData/MapServer/6 → nothing matched
  - step 1: point query at the pin https://gis.dnr.wa.gov/site3/rest/services/Public_Boundaries/WADNR_PUBLIC_Major_Public_Lands_NonDNR/MapServer/1 → nothing matched
  - step 3: open-data search https://hub.arcgis.com/api/v3/datasets?q=north%20shillapoo%20Washington → did not open (400); second try opened
  - step 3: open-data search (second try, ArcGIS Online) https://www.arcgis.com/sharing/rest/search?q=north%20shillapoo%20Washington → not reached
  - step 4: PAD-US point query https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0 → nothing under the pin
  - step 2: agency park page https://wdfw.wa.gov/places-to-go/wildlife-areas/shillapoo-north-wildlife-area-unit → opened, 1 matching line(s)
  - step 2: document: 2018 https://wdfw.wa.gov/sites/default/files/2020-01/2017-18_shillapoo_wildlife_area_update.pdf → opened, nothing matched
  - step 2: document: 2017 https://wdfw.wa.gov/sites/default/files/publications/00536/shillapoo_2017update.pdf → opened, nothing matched
  - step 2: document: 2014 https://wdfw.wa.gov/sites/default/files/publications/00536/shillapoo_2014update.pdf → opened, nothing matched
  - step 2: 4 document link(s) not followed  → skipped: not about parks

## q1-boiling-springs-tract: US-12752 Green River State Natural Area (Boiling Springs unit) · tract · PARTLY
- asked: the KHLCF Timber Lane 115.75-acre tract: is it part of the preserve? (HQ (Brandon test case))
- context only: tried steps 1, 2, 3, 4, 6
- the chain:
  - step 1 our layers (context): polygon under the pin in a layer we read: "Green River State Natural Area (Rush Island Bottoms)", 139 ac · "MA_ID=768.0; MANAME=Green River State Natural Area (Rush Island Bottoms); UNIT_TYPE=State Natural Area; MA_OWNER=Office of Kentucky Nature Preserves; MNG_INST=O" · https://kygisserver.ky.gov/arcgis/rest/services/WGS84WM_Services/Ky_KNP_Natural_Areas_WGS84WM/MapServer/0 · note: a different unit of the same natural area
  - step 4 PAD-US (context): PAD-US record under the pin: "Green River State Natural Area (Rush Island Bottoms)" managed by SDC, owner SDC, 139 acres · "Unit_Nm=Green River State Natural Area (Rush Island Bottoms); Mang_Name=SDC; Own_Name=SDC; Own_Type=STAT; Des_Tp=SCA; GIS_Acres=139; Category=Fee" · https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0
  - step 2 agency page (context): other site (context, not this tract): Davis Bend is one of several sites the KHLCF protects along the Green River in Hart, Green, and Taylor Counties. · "Davis Bend is one of several sites the KHLCF protects along the Green River in Hart, Green, and Taylor Counties." · https://eec.ky.gov/Nature-Preserves/Locations/Pages/Rush-Island-Bottoms.aspx
- steps tried:
  - step 1: point query at the pin https://kygisserver.ky.gov/arcgis/rest/services/WGS84WM_Services/Ky_State_Parks_Features_WGS84WM/MapServer/8 → nothing matched
  - step 1: point query at the pin https://kygisserver.ky.gov/arcgis/rest/services/WGS84WM_Services/Ky_Public_Hunting_Areas_WGS84WM/MapServer/1 → nothing matched
  - step 1: point query at the pin https://kygisserver.ky.gov/arcgis/rest/services/WGS84WM_Services/Ky_KNP_State_Nature_Preserves_WGS84WM/MapServer/0 → nothing matched
  - step 1: point query at the pin https://kygisserver.ky.gov/arcgis/rest/services/WGS84WM_Services/Ky_KNP_Natural_Areas_WGS84WM/MapServer/0 → 1 named polygon(s) of 1
  - step 3: open-data search https://hub.arcgis.com/api/v3/datasets?q=boiling%20green%20river%20springs%20Kentucky → did not open (400); second try opened
  - step 3: open-data search (second try, ArcGIS Online) https://www.arcgis.com/sharing/rest/search?q=boiling%20green%20river%20springs%20Kentucky → not reached
  - step 4: PAD-US point query https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0 → 1 record(s)
  - step 2: agency park page https://eec.ky.gov/Nature-Preserves/Locations/Pages/Rush-Island-Bottoms.aspx → opened, 1 matching line(s)
  - step 2: KHLCF land-acquisition annual reports (Kentucky Heritage Land Conservation Fund) https://heritageland.ky.gov/Pages/default.aspx → did not open (rest)
  - step 2: OKNP nature preserve pages (Office of Kentucky Nature Preserves) https://eec.ky.gov/Nature-Preserves/Locations/Pages/default.aspx → opened, nothing matched
  - step 2: KNP KHLCF annual reports (eec.ky.gov) https://eec.ky.gov/Nature-Preserves/Pages/default.aspx → opened, nothing matched
  - step 2: document: Species Natural Community Reports https://eec.ky.gov/Nature-Preserves/biodiversity/Pages/Species-and-Natural-Community-Reports.aspx → opened, nothing matched
  - step 2: document: KHLCF https://eec.ky.gov/Nature-Preserves/conserving_natural_areas/KHLCF/Pages/heritage-land-conservation-fund.aspx → opened, nothing matched
  - step 6: news releases https://fw.ky.gov/News/Pages/default.aspx → opened, nothing matched
  - step 2: 39 document link(s) not followed  → skipped: not about parks

## pile-US-13018-tract: US-13018 Black Rock Range East/West BLM Herd Management Area · tract · PARTLY
- asked: pile solver: hab1 Black Rock Range East (rule 18: 'west' names only one piece) (pile solver v1)
- context only: tried steps 1, 2, 3, 4
- the chain:
  - step 4 PAD-US (context): PAD-US record under the pin: "Humboldt River Field Office" managed by BLM, owner BLM, 6081514 acres · "Unit_Nm=Humboldt River Field Office; Mang_Name=BLM; Own_Name=BLM; Own_Type=FED; Des_Tp=PUB; GIS_Acres=6081514; Category=Fee" · https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0
- steps tried:
  - step 1: point query at the pin https://services.arcgis.com/RyxlXSfFi87rAosq/arcgis/rest/services/Wildlife_Management_Areas/FeatureServer/0 → did not open
  - step 1: point query at the pin https://arcgis.water.nv.gov/arcgis/rest/services/Hosted/SCORPRecAreas_Master/FeatureServer/0 → nothing matched
  - step 1: point query at the pin https://services7.arcgis.com/5hLFVlePaucIMGhw/arcgis/rest/services/VS_Boundary_Map_2_WFL1/FeatureServer/2 → did not open
  - step 1: point query at the pin https://arcgis.water.nv.gov/arcgis/rest/services/Hosted/SCORP_Recreation_Areas/FeatureServer/0 → nothing matched
  - step 3: open-data search https://hub.arcgis.com/api/v3/datasets?q=black%20east%20herd%20range%20rock%20west%20Nevada → did not open (400); second try opened
  - step 3: open-data search (second try, ArcGIS Online) https://www.arcgis.com/sharing/rest/search?q=black%20east%20herd%20range%20rock%20west%20Nevada → 3 dataset(s), none official
  - step 4: PAD-US point query https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0 → 1 record(s)
  - step 2: agency park page https://www.blm.gov/programs/wild-horse-and-burro/herd-management/herd-management-areas/nevada/black-rock → opened, nothing matched
  - step 2: document: Contracting https://www.blm.gov/services/acquisition/contracting → opened, nothing matched
  - step 2: 4 document link(s) not followed  → skipped: not about parks

## pile-US-13203-tract: US-13203 Robert’s-Wickstrom:East Unit Wildlife Management Area · tract · PARTLY
- asked: pile solver: sgmnf5309 Roberts-Wickstrom WMA (the park is the piece 'east' of a bigger area; 'Roberts-Wickstrom WMA' does not name that piece (rule 18)); sgmnf5847 Roberts-Wickstrom WMA (the park is the piece 'east' of a bigger area; 'Roberts-Wickstrom WMA' does not name that piece (rule 18)) (pile solver v1)
- context only: tried steps 1, 2, 3, 4
- the chain:
  - step 1 our layers (context): polygon under the pin in a layer we read: "Roberts-Wickstrom WMA: East Unit", 505 ac · "name=Roberts-Wickstrom WMA: East Unit; unit_name=Roberts-Wickstrom WMA; subunit_name=East Unit; lam_program_project_code=WMA01383; subunit_nbr=01; uniqueid=WMA0" · https://enterprise.gisdata.mn.gov/aghost/rest/services/us_mn_state_dnr/bdry_dnr_wildlife_mgmt_areas_pub/FeatureServer/0 · note: a different unit of the same wildlife management area
- steps tried:
  - step 1: point query at the pin https://enterprise.gisdata.mn.gov/aghost/rest/services/us_mn_state_dnr/bdry_dnr_wildlife_mgmt_areas_pub/FeatureServer/0 → 1 named polygon(s) of 1
  - step 1: point query at the pin https://enterprise.gisdata.mn.gov/aghost/rest/services/us_mn_state_dnr/bdry_state_forest/FeatureServer/4 → nothing matched
  - step 1: point query at the pin https://enterprise.gisdata.mn.gov/aghost/rest/services/us_mn_state_dnr/bdry_scientific_and_nat_areas/FeatureServer/4 → nothing matched
  - step 1: point query at the pin https://services.arcgis.com/8df8p0NlLFEShl0r/ArcGIS/rest/services/MN_State_Parks_and_Recreation_Areas/FeatureServer/2 → did not open
  - step 3: open-data search https://hub.arcgis.com/api/v3/datasets?q=east%20robert%20wickstrom%20Minnesota → did not open (400); second try opened
  - step 3: open-data search (second try, ArcGIS Online) https://www.arcgis.com/sharing/rest/search?q=east%20robert%20wickstrom%20Minnesota → not reached
  - step 4: PAD-US point query https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0 → nothing under the pin
  - step 2: agency park page https://www.dnr.state.mn.us/wmas/detail_report.html?id=WMA0138301 → did not open (robots)

## pile-US-13221-tract: US-13221 Gordon W. Yeager-S.E. Unit Wildlife Management Area · tract · PARTLY
- asked: pile solver: 208844 Gordon W. Yeager State Wildlife Management Area (the park is the piece 'southeast' of a bigger area; 'Gordon W. Yeager State Wildlife Management Area' does not name that piece (rule 18)); sgmnf5017 Gordon W. Yeager WMA (the park is the piece 'southeast' of a bigger area; 'Gordon  (pile solver v1)
- context only: tried steps 1, 2, 3, 4
- the chain:
  - step 1 our layers (context): polygon under the pin in a layer we read: "Gordon W. Yeager WMA: South East Unit", 199 ac · "name=Gordon W. Yeager WMA: South East Unit; unit_name=Gordon W. Yeager WMA; subunit_name=South East Unit; lam_program_project_code=WMA00984; subunit_nbr=04; uni" · https://enterprise.gisdata.mn.gov/aghost/rest/services/us_mn_state_dnr/bdry_dnr_wildlife_mgmt_areas_pub/FeatureServer/0 · note: a different unit of the same wildlife management area
  - step 4 PAD-US (context): PAD-US record under the pin: "Gordon W. Yeager State Wildlife Management Area" managed by SFW, owner SDNR, 241 acres · "Unit_Nm=Gordon W. Yeager State Wildlife Management Area; Mang_Name=SFW; Own_Name=SDNR; Own_Type=STAT; Des_Tp=SCA; GIS_Acres=241; Category=Fee" · https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0
- steps tried:
  - step 1: point query at the pin https://enterprise.gisdata.mn.gov/aghost/rest/services/us_mn_state_dnr/bdry_dnr_wildlife_mgmt_areas_pub/FeatureServer/0 → 1 named polygon(s) of 1
  - step 1: point query at the pin https://enterprise.gisdata.mn.gov/aghost/rest/services/us_mn_state_dnr/bdry_state_forest/FeatureServer/4 → nothing matched
  - step 1: point query at the pin https://enterprise.gisdata.mn.gov/aghost/rest/services/us_mn_state_dnr/bdry_scientific_and_nat_areas/FeatureServer/4 → nothing matched
  - step 1: point query at the pin https://services.arcgis.com/8df8p0NlLFEShl0r/ArcGIS/rest/services/MN_State_Parks_and_Recreation_Areas/FeatureServer/2 → did not open
  - step 3: open-data search https://hub.arcgis.com/api/v3/datasets?q=gordon%20yeager%20Minnesota → did not open (400); second try opened
  - step 3: open-data search (second try, ArcGIS Online) https://www.arcgis.com/sharing/rest/search?q=gordon%20yeager%20Minnesota → not reached
  - step 4: PAD-US point query https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0 → 1 record(s)
  - step 2: agency park page https://www.dnr.state.mn.us/wmas/detail_report.html?id=WMA0098404 → did not open (robots)

## pile-US-13270-tract: US-13270 Otis Pike Pine Barrens State Forest · tract · PARTLY
- asked: pile solver: sgnya67655 Otis Pike Pine Barrens State Forest - East (rule 18: 'east' names only one piece); sgnya67814 Otis Pike Pine Barrens State Forest - West (rule 18: 'west' names only one piece); sgnya67813 Otis Pike Pine Barrens State Forest - West (rule 18: 'west' names only one piece); sgnya (pile solver v1)
- context only: tried steps 1, 2, 3, 4
- the chain:
  - step 4 PAD-US (context): PAD-US record under the pin: "Otis Pike Preserve - West" managed by SDC, owner SDC, 892 acres · "Unit_Nm=Otis Pike Preserve - West; Mang_Name=SDC; Own_Name=SDC; Own_Type=STAT; Des_Tp=SCA; GIS_Acres=892; Category=Fee" · https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0
- steps tried:
  - step 1: point query at the pin https://services6.arcgis.com/DZHaqZm9cxOD4CWM/ArcGIS/rest/services/NYS_DEC_Lands/FeatureServer/0 → did not open
  - step 1: point query at the pin https://services.arcgis.com/1xFZPtKn1wKC6POA/ArcGIS/rest/services/NYS_Park_Polygons/FeatureServer/0 → did not open
  - step 1: point query at the pin https://services1.arcgis.com/fBc8EJBxQRMcHlei/arcgis/rest/services/NPS_Land_Resources_Division_Boundary_and_Tract_Data_Service/FeatureServer/2 → did not open
  - step 3: open-data search https://hub.arcgis.com/api/v3/datasets?q=barrens%20otis%20pike%20pine%20New%20York → did not open (400); second try opened
  - step 3: open-data search (second try, ArcGIS Online) https://www.arcgis.com/sharing/rest/search?q=barrens%20otis%20pike%20pine%20New%20York → not reached
  - step 4: PAD-US point query https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0 → 1 record(s)
  - step 2: agency park page https://dec.ny.gov/places/otis-pike-pine-barrens-state-forest → did not open (robots)

## pile-US-13446-tract: US-13446 North Lake State Fishing Lake · tract · PARTLY
- asked: pile solver: 157269 Northlake Park (rule 18: 'north' names only one piece) (pile solver v1)
- context only: tried steps 1, 2, 3, 4
- the chain:
  - step 1 our layers (context): polygon under the pin in a layer we read: "North Lake" · "ManagedPlaceOID=516; ManagedPlaceName=North Lake; PlaceTypeID=3; PlaceTypeName=Access Area; Region=Region 4 - North Puget Sound; ParkingLots=1; ADAParkingStalls" · https://geodataservices.wdfw.wa.gov/arcgis/rest/services/WP_RealEstate/ManagedPlaces/MapServer/0
  - step 3 open-data portal (context): open-data dataset names the park: "Vegetation Map of North Cascades National Park Service Complex" (NAntonova@nps.gov_nps) · "The Vegetation Mapping Inventory (VMI) is an effort by the National Park Service (NPS) to classify, describe, and map vegetation communities present on NPS unit" · https://tiles.arcgis.com/tiles/fBc8EJBxQRMcHlei/arcgis/rest/services/NOCA_VegMap/MapServer
- steps tried:
  - step 1: point query at the pin https://services5.arcgis.com/4LKAHwqnBooVDUlX/arcgis/rest/services/ParkBoundaries/FeatureServer/2 → did not open
  - step 1: point query at the pin https://geodataservices.wdfw.wa.gov/arcgis/rest/services/WP_RealEstate/ManagedPlaces/MapServer/0 → 1 named polygon(s) of 1
  - step 1: point query at the pin https://gis.dnr.wa.gov/site3/rest/services/Public_Boundaries/WADNR_PUBLIC_Cadastre_OpenData/MapServer/6 → nothing matched
  - step 1: point query at the pin https://gis.dnr.wa.gov/site3/rest/services/Public_Boundaries/WADNR_PUBLIC_Major_Public_Lands_NonDNR/MapServer/1 → opened, nothing matched the name
  - step 3: open-data search https://hub.arcgis.com/api/v3/datasets?q=north%20Washington → did not open (400); second try opened
  - step 3: open-data search (second try, ArcGIS Online) https://www.arcgis.com/sharing/rest/search?q=north%20Washington → opened, dataset "Vegetation Map of North Cascades National Park Service Complex"
  - step 4: PAD-US point query https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0 → nothing under the pin
  - step 2: agency park page https://wdfw.wa.gov/fishing/locations/lowland-lakes/north-lake → opened, nothing matched
  - step 2: 6 document link(s) not followed  → skipped: not about parks

## pile-US-2997-tract: US-2997 Choke Canyon State Park · tract · PARTLY
- asked: pile solver: sgtxa81 Choke Canyon - South Shore Unit (rule 18: 'south' names only one piece); sgtxa82 Choke Canyon - North Shore Unit (rule 18: 'north' names only one piece) (pile solver v1)
- context only: tried steps 1, 2, 3, 4
- the chain:
  - step 4 PAD-US (context): PAD-US record under the pin: "Choke Canyon State Park" managed by SPR, owner BLM, 1103 acres · "Unit_Nm=Choke Canyon State Park; Mang_Name=SPR; Own_Name=BLM; Own_Type=FED; Des_Tp=SP; GIS_Acres=1103; Category=Fee" · https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0
- steps tried:
  - step 1: point query at the pin https://services1.arcgis.com/1mtXwieMId59thmg/arcgis/rest/services/Texas_State_Parks_Boundaries/FeatureServer/0 → did not open
  - step 1: point query at the pin https://tpwd.texas.gov/arcgis/rest/services/Wildlife/TPWD_PublicHuntLocatorMap/MapServer/9 → opened, nothing matched the name
  - step 1: point query at the pin https://services1.arcgis.com/1mtXwieMId59thmg/arcgis/rest/services/WMA_Boundaries_4PublicDistribution/FeatureServer/0 → did not open
  - step 1: point query at the pin https://services1.arcgis.com/1mtXwieMId59thmg/arcgis/rest/services/Public_ConservationLands/FeatureServer/0 → did not open
  - step 3: open-data search https://hub.arcgis.com/api/v3/datasets?q=canyon%20choke%20Texas → did not open (400); second try opened
  - step 3: open-data search (second try, ArcGIS Online) https://www.arcgis.com/sharing/rest/search?q=canyon%20choke%20Texas → not reached
  - step 4: PAD-US point query https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0 → 1 record(s)
  - step 2: agency park page https://tpwd.texas.gov/state-parks/choke-canyon → did not open (robots)

## pile-US-3524-tract: US-3524 Ocotillo Wells State Vehicle Recreational Area · tract · PARTLY
- asked: pile solver: sgcad449 Ocotillo Wells East (rule 18: 'east' names only one piece) (pile solver v1)
- context only: tried steps 1, 2, 3, 4
- the chain:
  - step 4 PAD-US (context): PAD-US record under the pin: "Ocotillo Wells State Vehicular Recreation Area" managed by SPR, owner SPR, 53215 acres · "Unit_Nm=Ocotillo Wells State Vehicular Recreation Area; Mang_Name=SPR; Own_Name=SPR; Own_Type=STAT; Des_Tp=SREC; GIS_Acres=53215; Category=Fee" · https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0
- steps tried:
  - step 1: point query at the pin https://services2.arcgis.com/Uq9r85Potqm3MfRV/arcgis/rest/services/biosds3077_fpu/FeatureServer/0 → did not open
  - step 1: point query at the pin https://services2.arcgis.com/Uq9r85Potqm3MfRV/ArcGIS/rest/services/ParkBoundaries/FeatureServer/0 → did not open
  - step 1: point query at the pin https://services.arcgis.com/QVENGdaPbd4LUkLV/arcgis/rest/services/FWSApproved_Authoritative/FeatureServer/0 → did not open
  - step 1: point query at the pin https://services2.arcgis.com/Uq9r85Potqm3MfRV/arcgis/rest/services/biosds3092_fpu/FeatureServer/0 → did not open
  - step 3: open-data search https://hub.arcgis.com/api/v3/datasets?q=ocotillo%20vehicle%20wells%20California → did not open (400); second try opened
  - step 3: open-data search (second try, ArcGIS Online) https://www.arcgis.com/sharing/rest/search?q=ocotillo%20vehicle%20wells%20California → 2 dataset(s), none official
  - step 4: PAD-US point query https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0 → 1 record(s)
  - step 2: agency park page https://ohv.parks.ca.gov/?page_id=1217 → opened, nothing matched
  - step 2: document: 2026 Ocotillo Wells SVRA Soil Conservation Plan https://ohv.parks.ca.gov/pages/1170/files/2026%20Final%20OWSVRA%20Soil%20Conservation%20Plan.pdf → opened, nothing matched
  - step 2: document: 2020 Soil Conservation Standard Guidelines (PDF, opens in ne https://ohv.parks.ca.gov/pages/1140/files/2020_SoilStandard.pdf → opened, nothing matched
  - step 2: document: Publications / Reports https://ohv.parks.ca.gov/?page_id=26656 → opened, nothing matched

## pile-US-3714-tract: US-3714 Yates Lake Wildlife Management Area · tract · PARTLY
- asked: pile solver: 166141 Yates Lake West Wildlife Management Area (rule 18: 'west' names only one piece); 166140 Yates Lake West Wildlife Management Area (rule 18: 'west' names only one piece) (pile solver v1)
- context only: tried steps 1, 2, 3, 4
- the chain:
  - step 1 our layers (context): polygon under the pin in a layer we read: "Yates Lake West Tract", 3538 ac · "Id=73; Name=FW 73 - Yates Lake West Tract; Source=Deed; NameLookup=Yates Lake West Tract; County=Elmore County; PDFAcres=3,518; Date=December 28, 2009; TractInf" · https://conservationgis.alabama.gov/adcnrweb/rest/services/ForeverWildTracts/MapServer/0
  - step 1 our layers (context): polygon under the pin in a layer we read: "Forever Wild Gothard - AWF Yates Lake WMA", 5970 ac · "Id=0; Name=Forever Wild Gothard - AWF Yates Lake WMA; MapYear=2026-27; DrawnBy=ASP; Acres=5970.484823420001; Link=https://outdooralabama.com/sites/default/files" · https://conservationgis.alabama.gov/adcnrweb/rest/services/WildlifeManagementAreas/MapServer/0
  - step 4 PAD-US (context): PAD-US record under the pin: "Yates Lake West Wildlife Management Area" managed by SDNR, owner OTHS, 3540 acres · "Unit_Nm=Yates Lake West Wildlife Management Area; Mang_Name=SDNR; Own_Name=OTHS; Own_Type=STAT; Des_Tp=SCA; GIS_Acres=3540; Category=Fee" · https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0
- steps tried:
  - step 1: point query at the pin https://conservationgis.alabama.gov/adcnrweb/rest/services/StateParks/MapServer/0 → nothing matched
  - step 1: point query at the pin https://conservationgis.alabama.gov/adcnrweb/rest/services/ForeverWildTracts/MapServer/0 → 1 named polygon(s) of 1
  - step 1: point query at the pin https://conservationgis.alabama.gov/adcnrweb/rest/services/WildlifeManagementAreas/MapServer/0 → 1 named polygon(s) of 1
  - step 1: point query at the pin https://conservationgis.alabama.gov/adcnrweb/rest/services/PublicFishingLakes/MapServer/1 → nothing matched
  - step 3: open-data search https://hub.arcgis.com/api/v3/datasets?q=yates%20Alabama → did not open (400); second try opened
  - step 3: open-data search (second try, ArcGIS Online) https://www.arcgis.com/sharing/rest/search?q=yates%20Alabama → not reached
  - step 4: PAD-US point query https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0 → 1 record(s)
  - step 2: agency park page https://www.alabamaforeverwild.com/yates-lake-wma → opened, nothing matched
  - step 2: document: Download Yates Lake Hiking Trail Map https://www.alabamaforeverwild.com/sites/default/files/Hiking%20Trail%20Maps/Yates_Hiking_Trail_Map.pdf → opened, nothing matched
  - step 2: document: Land Tracts https://www.alabamaforeverwild.com/ → opened, nothing matched
  - step 2: document: Tract List (geographical) https://www.alabamaforeverwild.com/forever-wild-tract-list → opened, nothing matched
  - step 2: 2 document link(s) not followed  → skipped: not about parks

## pile-US-4092-tract: US-4092 Salem Unit of Apple River Canyon State Park · tract · PARTLY
- asked: pile solver: sgila2162 Apple River Canyon State Park (the park is the piece 'salem' of a bigger area; 'Apple River Canyon State Park' does not name that piece (rule 18)); 70840 Apple River Canyon State Park (the park is the piece 'salem' of a bigger area; 'Apple River Canyon State Park' does not nam (pile solver v1)
- context only: tried steps 1, 2, 3, 4
- the chain:
  - step 1 our layers (context): polygon under the pin in a layer we read: "Apple River Canyon", 4068 ac · "CLASSIFICATION=SP; REGION=1; SITE_NAME=Apple River Canyon; GIS_ACRES=4068.2589214126083" · https://maps.dnr.illinois.gov/geoservices/rest/services/BaseLayers/MapServer/11
  - step 4 PAD-US (context): PAD-US record under the pin: "Apple River Canyon State Park" managed by SDNR, owner OTHS, 1931 acres · "Unit_Nm=Apple River Canyon State Park; Mang_Name=SDNR; Own_Name=OTHS; Own_Type=STAT; Des_Tp=SCA; GIS_Acres=1931; Category=Fee" · https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0
- steps tried:
  - step 1: point query at the pin https://services.arcgis.com/b9DHj1BjfdLLFv11/arcgis/rest/services/IllinoisProtectedLandsDH_1_22/FeatureServer/0 → did not open
  - step 1: point query at the pin https://services.arcgis.com/b9DHj1BjfdLLFv11/arcgis/rest/services/IllinoisProtectedLandsDH_1_22/FeatureServer/3 → did not open
  - step 1: point query at the pin https://maps.dnr.illinois.gov/geoservices/rest/services/BaseLayers/MapServer/11 → 1 named polygon(s) of 1
  - step 3: open-data search https://hub.arcgis.com/api/v3/datasets?q=apple%20canyon%20river%20salem%20Illinois → did not open (400); second try opened
  - step 3: open-data search (second try, ArcGIS Online) https://www.arcgis.com/sharing/rest/search?q=apple%20canyon%20river%20salem%20Illinois → not reached
  - step 4: PAD-US point query https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0 → 1 record(s)
  - step 2: agency park page https://dnr.illinois.gov/parks/park.applerivercanyon.html → opened, nothing matched
  - step 2: document: Apple River Canyon Brochure https://dnr.illinois.gov/content/dam/soi/en/web/dnr/publications/documents/00000016.pdf → opened, nothing matched
  - step 2: document: Extractive resources https://dnr.illinois.gov/mines.html → opened, nothing matched
  - step 2: 8 document link(s) not followed  → skipped: not about parks

## pile-US-5750-tract: US-5750 Black Ridge Canyons Wilderness Area · tract · PARTLY
- asked: pile solver: wsa130 Black Ridge Canyons West E (rule 18: 'west' names only one piece) (pile solver v1)
- context only: tried steps 1, 2, 3, 4
- the chain:
  - step 4 PAD-US (context): PAD-US record under the pin: "Moab Field Office" managed by BLM, owner BLM, 1860872 acres · "Unit_Nm=Moab Field Office; Mang_Name=BLM; Own_Name=BLM; Own_Type=FED; Des_Tp=PUB; GIS_Acres=1860872; Category=Fee" · https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0
- steps tried:
  - step 1: point query at the pin https://gis.colorado.gov/public/rest/services/OIT/Colorado_State_Basemap/MapServer/30 → nothing matched
  - step 1: point query at the pin https://gis.colorado.gov/public/rest/services/OIT/Colorado_State_Basemap/MapServer/41 → nothing matched
  - step 1: point query at the pin https://services5.arcgis.com/ttNGmDvKQA7oeDQ3/arcgis/rest/services/CPWAdminData/FeatureServer/5 → did not open
  - step 1: point query at the pin https://services1.arcgis.com/fBc8EJBxQRMcHlei/arcgis/rest/services/NPS_Land_Resources_Division_Boundary_and_Tract_Data_Service/FeatureServer/2 → did not open
  - step 3: open-data search https://hub.arcgis.com/api/v3/datasets?q=black%20canyons%20ridge%20Colorado → did not open (400); second try opened
  - step 3: open-data search (second try, ArcGIS Online) https://www.arcgis.com/sharing/rest/search?q=black%20canyons%20ridge%20Colorado → 6 dataset(s), none official
  - step 4: PAD-US point query https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0 → 1 record(s)
  - step 2: agency park page https://www.blm.gov/programs/national-conservation-lands/colorado/black-ridge-canyons-wilderness → did not open (HTTP 404)

## pile-US-5846-tract: US-5846 Horseshoe Canyon (South) BLM Wilderness Area · tract · PARTLY
- asked: pile solver: wsa978 Horseshoe Canyon (North) (rule 18: 'south' vs 'north' are different pieces (both names carry a different bracketed piece)) (pile solver v1)
- context only: tried steps 1, 2, 3, 4
- the chain:
  - step 4 PAD-US (context): PAD-US record under the pin: "Richfield Field Office" managed by BLM, owner BLM, 2127022 acres · "Unit_Nm=Richfield Field Office; Mang_Name=BLM; Own_Name=BLM; Own_Type=FED; Des_Tp=PUB; GIS_Acres=2127022; Category=Fee" · https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0
- steps tried:
  - step 1: point query at the pin https://services.arcgis.com/ZzrwjTRez6FJiOq4/arcgis/rest/services/Utah_State_Park_Management_Areas/FeatureServer/0 → did not open
  - step 1: point query at the pin https://services.arcgis.com/ZzrwjTRez6FJiOq4/arcgis/rest/services/WMAs_WFL1/FeatureServer/0 → did not open
  - step 1: point query at the pin https://services1.arcgis.com/99lidPhWCzftIe9K/arcgis/rest/services/Utah_National_Historic_Landmarks/FeatureServer/0 → did not open
  - step 1: point query at the pin https://gis.blm.gov/utarcgis/rest/services/Recreation/BLM_UT_RecAreas/MapServer/1 → nothing matched
  - step 3: open-data search https://hub.arcgis.com/api/v3/datasets?q=canyon%20horseshoe%20south%20Utah → did not open (400); second try opened
  - step 3: open-data search (second try, ArcGIS Online) https://www.arcgis.com/sharing/rest/search?q=canyon%20horseshoe%20south%20Utah → not reached
  - step 4: PAD-US point query https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0 → 1 record(s)
  - step 2: agency park page https://www.blm.gov/visit/horseshoe-canyon-south → opened, nothing matched
  - step 2: document: Contracting https://www.blm.gov/services/acquisition/contracting → opened, nothing matched
  - step 2: 4 document link(s) not followed  → skipped: not about parks

## pile-US-6011-tract: US-6011 Deep Creek North BLM Wilderness Area · tract · PARTLY
- asked: pile solver: wbl303 Deep Creek (rule 18: 'north' names only one piece) (pile solver v1)
- context only: tried steps 1, 2, 3, 4
- the chain:
  - step 4 PAD-US (context): PAD-US record under the pin: "St. George Field Office" managed by BLM, owner BLM, 629088 acres · "Unit_Nm=St. George Field Office; Mang_Name=BLM; Own_Name=BLM; Own_Type=FED; Des_Tp=PUB; GIS_Acres=629088; Category=Fee" · https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0
- steps tried:
  - step 1: point query at the pin https://services.arcgis.com/ZzrwjTRez6FJiOq4/arcgis/rest/services/Utah_State_Park_Management_Areas/FeatureServer/0 → did not open
  - step 1: point query at the pin https://services.arcgis.com/ZzrwjTRez6FJiOq4/arcgis/rest/services/WMAs_WFL1/FeatureServer/0 → did not open
  - step 1: point query at the pin https://services1.arcgis.com/99lidPhWCzftIe9K/arcgis/rest/services/Utah_National_Historic_Landmarks/FeatureServer/0 → did not open
  - step 1: point query at the pin https://gis.blm.gov/utarcgis/rest/services/Recreation/BLM_UT_RecAreas/MapServer/1 → nothing matched
  - step 3: open-data search https://hub.arcgis.com/api/v3/datasets?q=creek%20deep%20north%20Utah → did not open (deferred); second try opened
  - step 3: open-data search (second try, ArcGIS Online) https://www.arcgis.com/sharing/rest/search?q=creek%20deep%20north%20Utah → not reached
  - step 4: PAD-US point query https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0 → 1 record(s)
  - step 2: agency park page https://www.blm.gov/visit/deep-creek-north-wilderness-0 → opened, nothing matched
  - step 2: document: Contracting https://www.blm.gov/services/acquisition/contracting → opened, nothing matched
  - step 2: 4 document link(s) not followed  → skipped: not about parks

## pile-US-7722-tract: US-7722 Scarborough North State Beach · tract · PARTLY
- asked: pile solver: 57199 Scarborough State Beach (rule 18: 'north' names only one piece) (pile solver v1)
- context only: tried steps 1, 2, 3, 4
- the chain:
  - step 1 our layers (context): polygon under the pin in a layer we read: "Scarborough Beach", 29 ac · "DEM_ID=7075; DEM_DIV=Parks & Recreation; DEM_AREA=Scarborough Beach State Park; NAME=Scarborough Beach; ACQ_TYPE=Fee Title; HUNTING=No; FISHING=Yes; Pub_Access=" · https://risegis.ri.gov/hosting/rest/services/RIDEM/State_Conservation_Land/MapServer/0
  - step 1 our layers (context): polygon under the pin in a layer we read: "Scarborough Beach", 29 ac · "DEM_ID=7075; DEM_DIV=Parks & Recreation; DEM_AREA=Scarborough Beach State Park; NAME=Scarborough Beach; ACQ_TYPE=Fee Title; HUNTING=No; FISHING=Yes; Pub_Access=" · https://risegis.ri.gov/hosting/rest/services/RIDEM/Conserved_Land_in_RI_v2/FeatureServer/3
  - step 4 PAD-US (context): PAD-US record under the pin: "Scarborough Beach" managed by UNK, owner SDNR, 30 acres · "Unit_Nm=Scarborough Beach; Mang_Name=UNK; Own_Name=SDNR; Own_Type=STAT; Des_Tp=SP; GIS_Acres=30; Category=Fee" · https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0
- steps tried:
  - step 1: point query at the pin https://risegis.ri.gov/hosting/rest/services/RIDEM/State_Conservation_Land/MapServer/0 → 1 named polygon(s) of 1
  - step 1: point query at the pin https://services2.arcgis.com/S8zZg9pg23JUEexQ/ArcGIS/rest/services/ENV_Conservation_Lands_State_spf/FeatureServer/0 → did not open
  - step 1: point query at the pin https://services1.arcgis.com/fBc8EJBxQRMcHlei/arcgis/rest/services/NPS_Land_Resources_Division_Boundary_and_Tract_Data_Service/FeatureServer/2 → did not open
  - step 1: point query at the pin https://risegis.ri.gov/hosting/rest/services/RIDEM/Conserved_Land_in_RI_v2/FeatureServer/3 → 1 named polygon(s) of 1
  - step 3: open-data search https://hub.arcgis.com/api/v3/datasets?q=beach%20north%20scarborough%20Rhode%20Island → did not open (deferred); second try opened
  - step 3: open-data search (second try, ArcGIS Online) https://www.arcgis.com/sharing/rest/search?q=beach%20north%20scarborough%20Rhode%20Island → not reached
  - step 4: PAD-US point query https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0 → 1 record(s)
  - step 2: agency park page https://riparks.com/beach/scarborough-north.php → did not open (HTTP 404)

## pile-US-7906-tract: US-7906 Chattahoochee Fall Line Almo Tract Wildlife Management Area · tract · PARTLY
- asked: pile solver: 195025 Chattahoochee Fall Line Wildlife Management Area (the park is the piece 'almo' of a bigger area; 'Chattahoochee Fall Line Wildlife Management Area' does not name that piece (rule 18)); 194888 Chattahoochee Fall Line Wildlife Management Area (the park is the piece 'almo' of a bigg (pile solver v1)
- context only: tried steps 1, 2, 3, 4, 6
- the chain:
  - step 4 PAD-US (context): PAD-US record under the pin: "Almo/Blackjack" managed by NGO, owner NGO, 8328 acres · "Unit_Nm=Almo/Blackjack; Mang_Name=NGO; Own_Name=NGO; Own_Type=NGO; Des_Tp=PCON; GIS_Acres=8328; Category=Fee" · https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0
  - step 4 PAD-US (context): PAD-US record under the pin: "Chattahoochee Fall Line Wildlife Management Area" managed by SDNR, owner SDNR, 16192 acres · "Unit_Nm=Chattahoochee Fall Line Wildlife Management Area; Mang_Name=SDNR; Own_Name=SDNR; Own_Type=STAT; Des_Tp=SCA; GIS_Acres=16192; Category=Fee" · https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0
- steps tried:
  - step 1: point query at the pin https://services6.arcgis.com/9QlSLDqa0P1cHLhu/arcgis/rest/services/Georgia_Licenses_by_District/FeatureServer/9 → did not open
  - step 1: point query at the pin https://services6.arcgis.com/9QlSLDqa0P1cHLhu/ArcGIS/rest/services/State_Parks_Boundary/FeatureServer/0 → did not open
  - step 1: point query at the pin https://services6.arcgis.com/9QlSLDqa0P1cHLhu/arcgis/rest/services/WRD_WMA_Public/FeatureServer/14 → did not open
  - step 1: point query at the pin https://apps.fs.usda.gov/arcx/rest/services/EDW/EDW_SpecialInterestManagementArea_01/MapServer/0 → did not open
  - step 3: open-data search https://hub.arcgis.com/api/v3/datasets?q=almo%20chattahoochee%20fall%20line%20tract%20Georgia → did not open (deferred); second try opened
  - step 3: open-data search (second try, ArcGIS Online) https://www.arcgis.com/sharing/rest/search?q=almo%20chattahoochee%20fall%20line%20tract%20Georgia → not reached
  - step 4: PAD-US point query https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0 → 2 record(s)
  - step 2: agency park page https://georgiawildlife.com/chattahoochee-fall-line-wma-almo-tract → did not open (rest)
  - step 6: news releases https://georgiawildlife.com/news → did not open (rest)

## pile-US-8400-tract: US-8400 Beaver Brook State Reserve · tract · PARTLY
- asked: pile solver: sgmaa700052 Beaver Brook North Reservation (rule 18: 'north' names only one piece); sgmaa692087 Beaver Brook North Reservation (rule 18: 'north' names only one piece); sgmaa692035 Beaver Brook North Reservation (rule 18: 'north' names only one piece); sgmaa691858 Beaver Brook North Rese (pile solver v1)
- context only: tried steps 1, 2, 3, 4
- the chain:
  - step 4 PAD-US (context): PAD-US record under the pin: "Beaver Brook Reservation" managed by SPR, owner SPR, 13 acres · "Unit_Nm=Beaver Brook Reservation; Mang_Name=SPR; Own_Name=SPR; Own_Type=STAT; Des_Tp=SRMA; GIS_Acres=13; Category=Fee" · https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0
  - step 4 PAD-US (context): PAD-US record under the pin: "Beaver Brook Reservation" managed by UNK, owner SPR, 58 acres · "Unit_Nm=Beaver Brook Reservation; Mang_Name=UNK; Own_Name=SPR; Own_Type=STAT; Des_Tp=SP; GIS_Acres=58; Category=Fee" · https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0
- steps tried:
  - step 1: point query at the pin https://arcgisserver.digital.mass.gov/arcgisserver/rest/services/AGOL/openspace/FeatureServer/0 → did not open
  - step 1: point query at the pin https://services1.arcgis.com/7iJyYTjCtKsZS1LR/arcgis/rest/services/Search_DCRownManOS_SitenameDiss/FeatureServer/0 → did not open
  - step 1: point query at the pin https://services1.arcgis.com/fBc8EJBxQRMcHlei/arcgis/rest/services/NPS_Land_Resources_Division_Boundary_and_Tract_Data_Service/FeatureServer/2 → did not open
  - step 1: point query at the pin https://services1.arcgis.com/fBc8EJBxQRMcHlei/arcgis/rest/services/National_Park_Property_Boundaries/FeatureServer/0 → did not open
  - step 3: open-data search https://hub.arcgis.com/api/v3/datasets?q=beaver%20brook%20Massachusetts → did not open (deferred); second try opened
  - step 3: open-data search (second try, ArcGIS Online) https://www.arcgis.com/sharing/rest/search?q=beaver%20brook%20Massachusetts → not reached
  - step 4: PAD-US point query https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0 → 2 record(s)
  - step 2: agency park page https://www.mass.gov/locations/beaver-brook-reservation → opened, nothing matched
  - step 2: 2 document link(s) not followed  → skipped: not about parks

## pile-US-9462-tract: US-9462 Fallsville South State Wildlife Area · tract · PARTLY
- asked: pile solver: 71724 Fallsville Wildlife Area (rule 18: 'south' names only one piece); sgohb74 FALLSVILLE (FallsvllWA) (rule 18: 'south' names only one piece) (pile solver v1)
- context only: tried steps 1, 2, 3, 4, 6
- the chain:
  - step 4 PAD-US (context): PAD-US record under the pin: "Fallsville Wildlife Area" managed by SDNR, owner SDNR, 1785 acres · "Unit_Nm=Fallsville Wildlife Area; Mang_Name=SDNR; Own_Name=SDNR; Own_Type=STAT; Des_Tp=SCA; GIS_Acres=1785; Category=Fee" · https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0
- steps tried:
  - step 1: point query at the pin https://gis.ohiodnr.gov/arcgis/rest/services/OIT_Services/ODNR_ODNR_Lands_Public_nolakes/FeatureServer/5 → did not open
  - step 1: point query at the pin https://gis.ohiodnr.gov/arcgis/rest/services/OIT_Services/ODNR_ODNR_Lands_Public_nolakes/FeatureServer/7 → did not open
  - step 1: point query at the pin https://gis.ohiodnr.gov/arcgis/rest/services/OIT_Services/ODNR_ODNR_Lands_Public_nolakes/FeatureServer/6 → did not open
  - step 1: point query at the pin https://gis.ohiodnr.gov/arcgis/rest/services/OIT_Services/ODNR_ODNR_Lands_Public_nolakes/FeatureServer/8 → did not open
  - step 3: open-data search https://hub.arcgis.com/api/v3/datasets?q=fallsville%20south%20Ohio → did not open (deferred); second try opened
  - step 3: open-data search (second try, ArcGIS Online) https://www.arcgis.com/sharing/rest/search?q=fallsville%20south%20Ohio → not reached
  - step 4: PAD-US point query https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0 → 1 record(s)
  - step 2: agency park page https://ohiodnr.gov/go-and-do/plan-a-visit/find-a-property/fallsville-south-wildlife-area → did not open (HTTP 404)
  - step 6: news releases https://ohiodnr.gov/discover-and-learn/news → did not open (HTTP 404)

## pile-US-9629-tract: US-9629 Cherokee State Wildlife Area · tract · PARTLY
- asked: pile solver: sgcoa63 Cherokee SWA - Upper Unit (rule 18: 'upper' names only one piece); sgcoc204 Cherokee SWA - Upper Unit (rule 18: 'upper' names only one piece); sgcoa61 Cherokee SWA - Middle Unit (rule 18: 'middle' names only one piece); sgcoc202 Cherokee SWA - Middle Unit (rule 18: 'middle' name (pile solver v1)
- context only: tried steps 1, 2, 3, 4
- the chain:
  - step 1 our layers (context): polygon under the pin in a layer we read: "Cherokee SWA - Lone Pine Unit", 6636 ac · "PropName=Cherokee SWA - Lone Pine Unit; PropType=SWA; Acres=6636.01157732; LastUpdate=Generated from CPWParcels on 02/06/2024" · https://gis.colorado.gov/public/rest/services/OIT/Colorado_State_Basemap/MapServer/30
  - step 4 PAD-US (context): PAD-US record under the pin: "Cherokee State Wildlife Area - Lone Pine Unit" managed by SFW, owner SFW, 6663 acres · "Unit_Nm=Cherokee State Wildlife Area - Lone Pine Unit; Mang_Name=SFW; Own_Name=SFW; Own_Type=STAT; Des_Tp=SCA; GIS_Acres=6663; Category=Fee" · https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0
- steps tried:
  - step 1: point query at the pin https://gis.colorado.gov/public/rest/services/OIT/Colorado_State_Basemap/MapServer/30 → 1 named polygon(s) of 1
  - step 1: point query at the pin https://gis.colorado.gov/public/rest/services/OIT/Colorado_State_Basemap/MapServer/41 → nothing matched
  - step 1: point query at the pin https://services5.arcgis.com/ttNGmDvKQA7oeDQ3/arcgis/rest/services/CPWAdminData/FeatureServer/5 → did not open
  - step 1: point query at the pin https://services1.arcgis.com/fBc8EJBxQRMcHlei/arcgis/rest/services/NPS_Land_Resources_Division_Boundary_and_Tract_Data_Service/FeatureServer/2 → did not open
  - step 3: open-data search https://hub.arcgis.com/api/v3/datasets?q=cherokee%20Colorado → did not open (deferred); second try opened
  - step 3: open-data search (second try, ArcGIS Online) https://www.arcgis.com/sharing/rest/search?q=cherokee%20Colorado → 5 dataset(s), none official
  - step 4: PAD-US point query https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0 → 1 record(s)
  - step 2: agency park page https://cpw.state.co.us/learn/Maps/CherokeeSWA_LowerUnits_geo.pdf → did not open (HTTP 404)

## pile-US-9648-tract: US-9648 Escalante State Wildlife Area · tract · PARTLY
- asked: pile solver: sgcoa116 Escalante SWA - Lower Roubideau Tract (rule 18: 'lower' names only one piece); sgcoc325 Escalante SWA - Lower Roubideau Tract (rule 18: 'lower' names only one piece); 189137 Escalante State Wildlife Area - Lower Roubideau Tract (rule 18: 'lower' names only one piece); sgcoa119  (pile solver v1)
- context only: tried steps 1, 2, 3, 4
- the chain:
  - step 4 PAD-US (context): PAD-US record under the pin: "Uncompahgre Field Office" managed by BLM, owner BLM, 880205 acres · "Unit_Nm=Uncompahgre Field Office; Mang_Name=BLM; Own_Name=BLM; Own_Type=FED; Des_Tp=PUB; GIS_Acres=880205; Category=Fee" · https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0
- steps tried:
  - step 1: point query at the pin https://gis.colorado.gov/public/rest/services/OIT/Colorado_State_Basemap/MapServer/30 → nothing matched
  - step 1: point query at the pin https://gis.colorado.gov/public/rest/services/OIT/Colorado_State_Basemap/MapServer/41 → nothing matched
  - step 1: point query at the pin https://services5.arcgis.com/ttNGmDvKQA7oeDQ3/arcgis/rest/services/CPWAdminData/FeatureServer/5 → did not open
  - step 1: point query at the pin https://services1.arcgis.com/fBc8EJBxQRMcHlei/arcgis/rest/services/NPS_Land_Resources_Division_Boundary_and_Tract_Data_Service/FeatureServer/2 → did not open
  - step 3: open-data search https://hub.arcgis.com/api/v3/datasets?q=escalante%20Colorado → did not open (deferred); second try opened
  - step 3: open-data search (second try, ArcGIS Online) https://www.arcgis.com/sharing/rest/search?q=escalante%20Colorado → 6 dataset(s), none official
  - step 4: PAD-US point query https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0 → 1 record(s)
  - step 2: agency park page https://cpw.state.co.us/learn/Maps/EscalanteSWA_geo.pdf → did not open (HTTP 404)

## pile-US-9795-tract: US-9795 Sandhills West Wildlife Management Area · tract · PARTLY
- asked: pile solver: sggaa90 SANDHILLS WMA (rule 18: 'west' names only one piece); sggac821 SANDHILLS WMA (rule 18: 'west' names only one piece); sggaa34 SANDHILLS WMA (rule 18: 'west' names only one piece); sggac768 SANDHILLS WMA (rule 18: 'west' names only one piece) (pile solver v1)
- context only: tried steps 1, 2, 3, 4, 6
- the chain:
  - step 4 PAD-US (context): PAD-US record under the pin: "133-001" managed by OTHS, owner OTHS, 735 acres · "Unit_Nm=133-001; Mang_Name=OTHS; Own_Name=OTHS; Own_Type=STAT; Des_Tp=SCA; GIS_Acres=735; Category=Fee" · https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0
  - step 4 PAD-US (context): PAD-US record under the pin: "Fall Line Sandhills Wildlife Management Area" managed by SDNR, owner OTHS, 733 acres · "Unit_Nm=Fall Line Sandhills Wildlife Management Area; Mang_Name=SDNR; Own_Name=OTHS; Own_Type=STAT; Des_Tp=SCA; GIS_Acres=733; Category=Fee" · https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0
- steps tried:
  - step 1: point query at the pin https://services6.arcgis.com/9QlSLDqa0P1cHLhu/arcgis/rest/services/Georgia_Licenses_by_District/FeatureServer/9 → did not open
  - step 1: point query at the pin https://services6.arcgis.com/9QlSLDqa0P1cHLhu/ArcGIS/rest/services/State_Parks_Boundary/FeatureServer/0 → did not open
  - step 1: point query at the pin https://services6.arcgis.com/9QlSLDqa0P1cHLhu/arcgis/rest/services/WRD_WMA_Public/FeatureServer/14 → did not open
  - step 1: point query at the pin https://apps.fs.usda.gov/arcx/rest/services/EDW/EDW_SpecialInterestManagementArea_01/MapServer/0 → did not open
  - step 3: open-data search https://hub.arcgis.com/api/v3/datasets?q=sandhills%20west%20Georgia → did not open (deferred); second try opened
  - step 3: open-data search (second try, ArcGIS Online) https://www.arcgis.com/sharing/rest/search?q=sandhills%20west%20Georgia → not reached
  - step 4: PAD-US point query https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0 → 2 record(s)
  - step 2: agency park page https://georgiawildlife.com/sandhills-wma-west → did not open (rest)
  - step 6: news releases https://georgiawildlife.com/news → did not open (rest)

## pile-US-9916-tract: US-9916 Blackwater River State Nature Preserve · tract · PARTLY
- asked: pile solver: sgalb193 Blackwater River - South (rule 18: 'south' names only one piece) (pile solver v1)
- context only: tried steps 1, 2, 3, 4
- the chain:
  - step 1 our layers (context): polygon under the pin in a layer we read: "Blackwater River - South", 2309 ac · "Id=188; Name=FW 188 - Blackwater River - South; Grant=NFWF; Source=Deed; NameLookup=Blackwater River - South; County=Baldwin County; PDFAcres=2,269.1; Date=Marc" · https://conservationgis.alabama.gov/adcnrweb/rest/services/ForeverWildTracts/MapServer/0
- steps tried:
  - step 1: point query at the pin https://conservationgis.alabama.gov/adcnrweb/rest/services/StateParks/MapServer/0 → nothing matched
  - step 1: point query at the pin https://conservationgis.alabama.gov/adcnrweb/rest/services/ForeverWildTracts/MapServer/0 → 1 named polygon(s) of 1
  - step 1: point query at the pin https://conservationgis.alabama.gov/adcnrweb/rest/services/WildlifeManagementAreas/MapServer/0 → nothing matched
  - step 1: point query at the pin https://conservationgis.alabama.gov/adcnrweb/rest/services/PublicFishingLakes/MapServer/1 → nothing matched
  - step 3: open-data search https://hub.arcgis.com/api/v3/datasets?q=blackwater%20river%20Alabama → did not open (deferred); second try opened
  - step 3: open-data search (second try, ArcGIS Online) https://www.arcgis.com/sharing/rest/search?q=blackwater%20river%20Alabama → 3 dataset(s), none official
  - step 4: PAD-US point query https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0 → nothing under the pin
  - step 2: agency park page https://conservationgis.alabama.gov/dcnr/ → opened, nothing matched
  - step 2: document: Click Here https://conservationgis.alabama.gov/dcnr/{TractInfoL} → did not open (HTTP 404)

## pile-US-9940-tract: US-9940 Brush Mountain Wilderness Area · tract · PARTLY
- asked: pile solver: wld45 Brush Mountain East Wilderness (rule 18: 'east' names only one piece); sgvae500504 Brush Mountain East NF Wilderness Area (rule 18: 'east' names only one piece) (pile solver v1)
- context only: tried steps 1, 2, 3, 4, 6
- the chain:
  - step 4 PAD-US (context): PAD-US record under the pin: "Jefferson National Forest" managed by USFS, owner USFS, 711975 acres · "Unit_Nm=Jefferson National Forest; Mang_Name=USFS; Own_Name=USFS; Own_Type=FED; Des_Tp=NF; GIS_Acres=711975; Category=Fee" · https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0
- steps tried:
  - step 1: point query at the pin https://services1.arcgis.com/zdPnl7ASQIo6PX54/arcgis/rest/services/VDOF_State_Forests/FeatureServer/0 → did not open
  - step 1: point query at the pin https://services1.arcgis.com/PxUNqSbaWFvFgHnJ/arcgis/rest/services/VSP_Natural_Area_Preserves/FeatureServer/1 → did not open
  - step 1: point query at the pin https://services1.arcgis.com/PxUNqSbaWFvFgHnJ/arcgis/rest/services/bclsp_State_Parks/FeatureServer/0 → did not open
  - step 1: point query at the pin https://services1.arcgis.com/PxUNqSbaWFvFgHnJ/arcgis/rest/services/SP_Boundary_-_Tracts/FeatureServer/0 → did not open
  - step 3: open-data search https://hub.arcgis.com/api/v3/datasets?q=brush%20mountain%20Virginia → did not open (deferred); second try opened
  - step 3: open-data search (second try, ArcGIS Online) https://www.arcgis.com/sharing/rest/search?q=brush%20mountain%20Virginia → 2 dataset(s), none official
  - step 4: PAD-US point query https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0 → 1 record(s)
  - step 2: agency park page https://www.fs.usda.gov/detail/gwj/home/?cid=stelprdb5312424 → opened, nothing matched
  - step 2: document: Report Fraud on USDA Contracts https://usdaoig.oversight.gov/resources/contractor-fraud → did not open (robots-unreadable)
  - step 6: news releases https://dwr.virginia.gov/news/ → did not open (HTTP 404)
  - step 6: news releases https://www.dcr.virginia.gov/news → did not open (HTTP 404)

## pile-US-9941-tract: US-9941 Brush Mountain East Wilderness Area · tract · PARTLY
- asked: pile solver: wld46 Brush Mountain Wilderness (rule 18: 'east' names only one piece) (pile solver v1)
- context only: tried steps 1, 2, 3, 4, 6
- the chain:
  - step 4 PAD-US (context): PAD-US record under the pin: "Jefferson National Forest" managed by USFS, owner USFS, 711975 acres · "Unit_Nm=Jefferson National Forest; Mang_Name=USFS; Own_Name=USFS; Own_Type=FED; Des_Tp=NF; GIS_Acres=711975; Category=Fee" · https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0
- steps tried:
  - step 1: point query at the pin https://services1.arcgis.com/zdPnl7ASQIo6PX54/arcgis/rest/services/VDOF_State_Forests/FeatureServer/0 → did not open
  - step 1: point query at the pin https://services1.arcgis.com/PxUNqSbaWFvFgHnJ/arcgis/rest/services/VSP_Natural_Area_Preserves/FeatureServer/1 → did not open
  - step 1: point query at the pin https://services1.arcgis.com/PxUNqSbaWFvFgHnJ/arcgis/rest/services/bclsp_State_Parks/FeatureServer/0 → did not open
  - step 1: point query at the pin https://services1.arcgis.com/PxUNqSbaWFvFgHnJ/arcgis/rest/services/SP_Boundary_-_Tracts/FeatureServer/0 → did not open
  - step 3: open-data search https://hub.arcgis.com/api/v3/datasets?q=brush%20east%20mountain%20Virginia → did not open (deferred); second try opened
  - step 3: open-data search (second try, ArcGIS Online) https://www.arcgis.com/sharing/rest/search?q=brush%20east%20mountain%20Virginia → 1 dataset(s), none official
  - step 4: PAD-US point query https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0 → 1 record(s)
  - step 2: agency park page https://www.fs.usda.gov/detail/gwj/home/?cid=stelprdb5312424 → opened, nothing matched
  - step 2: document: Report Fraud on USDA Contracts https://usdaoig.oversight.gov/resources/contractor-fraud → did not open (robots-unreadable)
  - step 6: news releases https://dwr.virginia.gov/news/ → did not open (HTTP 404)
  - step 6: news releases https://www.dcr.virginia.gov/news → did not open (HTTP 404)

## pile-CA-4030-tract: CA-4030 Roche Lake Provincial Park · tract · NOT FOUND
- asked: pile solver: BC recreatio:1014986 ROCHE LAKE NE. (rule 18: 'northeast' names only one piece) (pile solver v1)
- no official source answered; tried steps 1, 2, 3, 4
- steps tried:
  - step 1: point query at the pin https://maps.gov.bc.ca/arcgis/rest/services/whse/bcgw_pub_whse_human_cultural_economic/MapServer/82 → did not open
  - step 1: point query at the pin https://maps.gov.bc.ca/arcgis/rest/services/whse/bcgw_pub_whse_human_cultural_economic/MapServer/46 → did not open
  - step 1: point query at the pin https://gis.burnaby.ca/arcgis/rest/services/OpenData/OpenData1/MapServer/6 → nothing matched
  - step 1: point query at the pin https://services6.arcgis.com/56eqCzQ5SZhBaDST/arcgis/rest/services/RegionalParksBoundaries_OpenData/FeatureServer/0 → did not open
  - step 3: open-data search https://hub.arcgis.com/api/v3/datasets?q=roche%20 → did not open (400); second try opened
  - step 3: open-data search (second try, ArcGIS Online) https://www.arcgis.com/sharing/rest/search?q=roche%20 → 6 dataset(s), none official
  - step 4: PAD-US point query https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0 → nothing under the pin
  - step 2: agency park page https://bcparks.ca/roche-lake-park → opened, nothing matched
  - step 2: document: Park Map [PDF] https://nrs.objectstore.gov.bc.ca/kuwyyf/roche_lake_park_map_aeca1d613b.pdf → opened, nothing matched

## pile-US-0654-tract: US-0654 National Capital Parks - East Park · tract · NOT FOUND
- asked: pile solver: 3536 National Capital Parks (rule 18: 'east' names only one piece) (pile solver v1)
- no official source answered; tried steps 2, 3, 4
- steps tried:
  - step 3: open-data search https://hub.arcgis.com/api/v3/datasets?q=capital%20east%20District%20of%20Columbia → did not open (400); second try opened
  - step 3: open-data search (second try, ArcGIS Online) https://www.arcgis.com/sharing/rest/search?q=capital%20east%20District%20of%20Columbia → 6 dataset(s), none official
  - step 4: PAD-US point query https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0 → nothing under the pin
  - step 2: agency park page https://www.nps.gov/nace/index.htm → opened, nothing matched

## pile-US-12685-tract: US-12685 Mallard Marsh:Gombold Unit Wildlife Management Area · tract · NOT FOUND
- asked: pile solver: sgmnf5469 Mallard Marsh WMA (the park is the piece 'gombold' of a bigger area; 'Mallard Marsh WMA' does not name that piece (rule 18)) (pile solver v1)
- no official source answered; tried steps 1, 2, 3, 4
- steps tried:
  - step 1: point query at the pin https://enterprise.gisdata.mn.gov/aghost/rest/services/us_mn_state_dnr/bdry_dnr_wildlife_mgmt_areas_pub/FeatureServer/0 → nothing matched
  - step 1: point query at the pin https://enterprise.gisdata.mn.gov/aghost/rest/services/us_mn_state_dnr/bdry_state_forest/FeatureServer/4 → nothing matched
  - step 1: point query at the pin https://enterprise.gisdata.mn.gov/aghost/rest/services/us_mn_state_dnr/bdry_scientific_and_nat_areas/FeatureServer/4 → nothing matched
  - step 1: point query at the pin https://services.arcgis.com/8df8p0NlLFEShl0r/ArcGIS/rest/services/MN_State_Parks_and_Recreation_Areas/FeatureServer/2 → did not open
  - step 3: open-data search https://hub.arcgis.com/api/v3/datasets?q=gombold%20mallard%20marsh%20Minnesota → did not open (400); second try opened
  - step 3: open-data search (second try, ArcGIS Online) https://www.arcgis.com/sharing/rest/search?q=gombold%20mallard%20marsh%20Minnesota → not reached
  - step 4: PAD-US point query https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0 → nothing under the pin
  - step 2: agency park page https://www.dnr.state.mn.us/wmas/detail_report.html?id=wma0122400 → did not open (robots)

## pile-US-6367-tract: US-6367 Ouachita McCurtain Unit Wildlife Management Area · tract · NOT FOUND
- asked: pile solver: sgokb300 Ouachita Wildlife Management Area (the park is the piece 'mccurtain' of a bigger area; 'Ouachita Wildlife Management Area' does not name that piece (rule 18)) (pile solver v1)
- no official source answered; tried steps 1, 2, 3, 4
- steps tried:
  - step 1: point query at the pin https://services6.arcgis.com/RBtoEUQ2lmN0K3GY/arcgis/rest/services/OklahomaRecreationalAreas/FeatureServer/3 → did not open
  - step 1: point query at the pin https://services6.arcgis.com/RBtoEUQ2lmN0K3GY/arcgis/rest/services/OklahomaRecreationalAreas/FeatureServer/0 → did not open
  - step 1: point query at the pin https://services1.arcgis.com/jRf8jjFwxedITdFe/arcgis/rest/services/Public_WMA_Boundaries/FeatureServer/1 → did not open
  - step 3: open-data search https://hub.arcgis.com/api/v3/datasets?q=mccurtain%20ouachita%20Oklahoma → did not open (deferred); second try opened
  - step 3: open-data search (second try, ArcGIS Online) https://www.arcgis.com/sharing/rest/search?q=mccurtain%20ouachita%20Oklahoma → not reached
  - step 4: PAD-US point query https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0 → 1 record(s)
  - step 2: agency park page https://www.wildlifedepartment.com/hunting/wma/southeast/ouachita-mccurtain-unit → opened, nothing matched
  - step 2: document: Ouachita WMA – North McCurtain Tiak Units Map https://www.wildlifedepartment.com/sites/default/files/wma-maps/Ouachita%20McCurtain%20Unit%20North%20WMA%20Atlas_2018.pdf → opened, nothing matched
  - step 2: document: Ouachita WMA – South McCurtain Tiak Units Map https://www.wildlifedepartment.com/sites/default/files/wma-maps/Ouachita%20McCurtain%20Unit%20South%20WMA%20Atlas_2018.pdf → opened, nothing matched
  - step 2: document: Ouachita WMA – West McCurtain Tiak Units Map https://www.wildlifedepartment.com/sites/default/files/wma-maps/Ouachita%20McCurtain%20Unit%20West%20WMA%20Atlas_2018.pdf → opened, nothing matched
  - step 2: 1 document link(s) not followed  → skipped: not about parks

## pile-US-6571-tract: US-6571 Las Palomas , Anacua Unit Wildlife Management Area · tract · NOT FOUND
- asked: pile solver: 263433 Las Palomas Wildlife Management Area (the park is the piece 'anacua' of a bigger area; 'Las Palomas Wildlife Management Area' does not name that piece (rule 18)); sgtxd1146 Las Palomas WMA - Taormina Unit (the park is the piece 'anacua' of a bigger area; 'Las Palomas WMA - Taormi (pile solver v1)
- no official source answered; tried steps 1, 2, 3, 4
- steps tried:
  - step 1: point query at the pin https://services1.arcgis.com/1mtXwieMId59thmg/arcgis/rest/services/Texas_State_Parks_Boundaries/FeatureServer/0 → did not open
  - step 1: point query at the pin https://tpwd.texas.gov/arcgis/rest/services/Wildlife/TPWD_PublicHuntLocatorMap/MapServer/9 → nothing matched
  - step 1: point query at the pin https://services1.arcgis.com/1mtXwieMId59thmg/arcgis/rest/services/WMA_Boundaries_4PublicDistribution/FeatureServer/0 → did not open
  - step 1: point query at the pin https://services1.arcgis.com/1mtXwieMId59thmg/arcgis/rest/services/Public_ConservationLands/FeatureServer/0 → did not open
  - step 3: open-data search https://hub.arcgis.com/api/v3/datasets?q=anacua%20las%20palomas%20Texas → did not open (deferred); second try opened
  - step 3: open-data search (second try, ArcGIS Online) https://www.arcgis.com/sharing/rest/search?q=anacua%20las%20palomas%20Texas → not reached
  - step 4: PAD-US point query https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0 → nothing under the pin
  - step 2: agency park page https://tpwd.texas.gov/huntwild/hunt/wma/find_a_wma/list/?id=103 → opened, nothing matched
  - step 2: document: Fishing Reports https://tpwd.texas.gov/fishboat/fish/recreational/fishreport.phtml → skipped: the title names no park / land / acquisition
  - step 2: document: Wildlife Fact Sheets https://tpwd.texas.gov/huntwild/wild/species/ → opened, nothing matched
  - step 2: document: Contract Reports https://tpwd.texas.gov/business/bidops/contracts/ → opened, nothing matched
  - step 2: 2 document link(s) not followed  → skipped: not about parks

## pile-US-6596-tract: US-6596 Richland Creek Wildlife Management Area · tract · NOT FOUND
- asked: pile solver: sgtxb1677 Richland Creek WMA - South Unit (rule 18: 'south' names only one piece) (pile solver v1)
- no official source answered; tried steps 1, 2, 3, 4
- steps tried:
  - step 1: point query at the pin https://services1.arcgis.com/1mtXwieMId59thmg/arcgis/rest/services/Texas_State_Parks_Boundaries/FeatureServer/0 → did not open
  - step 1: point query at the pin https://tpwd.texas.gov/arcgis/rest/services/Wildlife/TPWD_PublicHuntLocatorMap/MapServer/9 → nothing matched
  - step 1: point query at the pin https://services1.arcgis.com/1mtXwieMId59thmg/arcgis/rest/services/WMA_Boundaries_4PublicDistribution/FeatureServer/0 → did not open
  - step 1: point query at the pin https://services1.arcgis.com/1mtXwieMId59thmg/arcgis/rest/services/Public_ConservationLands/FeatureServer/0 → did not open
  - step 3: open-data search https://hub.arcgis.com/api/v3/datasets?q=creek%20richland%20Texas → did not open (deferred); second try opened
  - step 3: open-data search (second try, ArcGIS Online) https://www.arcgis.com/sharing/rest/search?q=creek%20richland%20Texas → 2 dataset(s), none official
  - step 4: PAD-US point query https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0 → nothing under the pin
  - step 2: agency park page https://tpwd.texas.gov/huntwild/hunt/wma/find_a_wma/list/?id=23 → opened, nothing matched
  - step 2: document: Fishing Reports https://tpwd.texas.gov/fishboat/fish/recreational/fishreport.phtml → skipped: the title names no park / land / acquisition
  - step 2: document: Wildlife Fact Sheets https://tpwd.texas.gov/huntwild/wild/species/ → opened, nothing matched
  - step 2: document: Contract Reports https://tpwd.texas.gov/business/bidops/contracts/ → opened, nothing matched
  - step 2: 2 document link(s) not followed  → skipped: not about parks

## pile-US-7914-tract: US-7914 Sandhills East Wildlife Management Area · tract · NOT FOUND
- asked: pile solver: sggaa90 SANDHILLS WMA (rule 18: 'east' names only one piece); sggac821 SANDHILLS WMA (rule 18: 'east' names only one piece); sggaa34 SANDHILLS WMA (rule 18: 'east' names only one piece); sggac768 SANDHILLS WMA (rule 18: 'east' names only one piece) (pile solver v1)
- no official source answered; tried steps 1, 2, 3, 4, 6
- steps tried:
  - step 1: point query at the pin https://services6.arcgis.com/9QlSLDqa0P1cHLhu/arcgis/rest/services/Georgia_Licenses_by_District/FeatureServer/9 → did not open
  - step 1: point query at the pin https://services6.arcgis.com/9QlSLDqa0P1cHLhu/ArcGIS/rest/services/State_Parks_Boundary/FeatureServer/0 → did not open
  - step 1: point query at the pin https://services6.arcgis.com/9QlSLDqa0P1cHLhu/arcgis/rest/services/WRD_WMA_Public/FeatureServer/14 → did not open
  - step 1: point query at the pin https://apps.fs.usda.gov/arcx/rest/services/EDW/EDW_SpecialInterestManagementArea_01/MapServer/0 → did not open
  - step 3: open-data search https://hub.arcgis.com/api/v3/datasets?q=east%20sandhills%20Georgia → did not open (deferred); second try opened
  - step 3: open-data search (second try, ArcGIS Online) https://www.arcgis.com/sharing/rest/search?q=east%20sandhills%20Georgia → not reached
  - step 4: PAD-US point query https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0 → nothing under the pin
  - step 2: agency park page https://georgiawildlife.com/sandhills-wma-east → did not open (rest)
  - step 6: news releases https://georgiawildlife.com/news → did not open (rest)

## pile-US-9797-tract: US-9797 Chattahoochee Fall Line Hilliard Tract Wildlife Management Area · tract · NOT FOUND
- asked: pile solver: 195025 Chattahoochee Fall Line Wildlife Management Area (the park is the piece 'hilliard' of a bigger area; 'Chattahoochee Fall Line Wildlife Management Area' does not name that piece (rule 18)); 194888 Chattahoochee Fall Line Wildlife Management Area (the park is the piece 'hilliard' o (pile solver v1)
- no official source answered; tried steps 1, 2, 3, 4, 6
- steps tried:
  - step 1: point query at the pin https://services6.arcgis.com/9QlSLDqa0P1cHLhu/arcgis/rest/services/Georgia_Licenses_by_District/FeatureServer/9 → did not open
  - step 1: point query at the pin https://services6.arcgis.com/9QlSLDqa0P1cHLhu/ArcGIS/rest/services/State_Parks_Boundary/FeatureServer/0 → did not open
  - step 1: point query at the pin https://services6.arcgis.com/9QlSLDqa0P1cHLhu/arcgis/rest/services/WRD_WMA_Public/FeatureServer/14 → did not open
  - step 1: point query at the pin https://apps.fs.usda.gov/arcx/rest/services/EDW/EDW_SpecialInterestManagementArea_01/MapServer/0 → did not open
  - step 3: open-data search https://hub.arcgis.com/api/v3/datasets?q=chattahoochee%20fall%20hilliard%20line%20tract%20Georgia → did not open (deferred); second try opened
  - step 3: open-data search (second try, ArcGIS Online) https://www.arcgis.com/sharing/rest/search?q=chattahoochee%20fall%20hilliard%20line%20tract%20Georgia → not reached
  - step 4: PAD-US point query https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0 → nothing under the pin
  - step 2: agency park page https://georgiawildlife.com/chattahoochee-fall-line-wma-hilliard-plantation-tract → did not open (rest)
  - step 6: news releases https://georgiawildlife.com/news → did not open (rest)

