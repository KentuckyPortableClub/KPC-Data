# Layer intake review (2026-10-29)

Every lead in data/intake/queue.json, probed politely (metadata and counts only, never geometry). Chat 9 approves a READY row by setting `approved: true` in ready.json; the nightly key rebuild reads approved rows later. LIVE-ONLY = read live, never stored. ASK = the publisher must be asked (nothing stated, or hosted for an agency). WATER-ONLY = lakes / reservoirs: for the 2-fer owner step only, never a park outline. RETRY = the probe did not open (error, rest, robots, 403): probed again next run, three failures → chat 9 checks the url. Terms are read on the publisher's OWN item page first (the Nevada lesson).

| verdict | rows |
|---|---|
| READY | 8 |
| WATER-ONLY | 4 |
| LIVE-ONLY | 1 |
| ASK-THE-PUBLISHER | 15 |
| RETRY | 66 |
| REJECT | 108 |

## READY (8)

### Public/CadastreParcels  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/CadastreParcels/MapServer/0
- WHY: official, credit terms, named polygons; closes 37 (name + pin 2, pin only 35): a pin inside a designation polygon is not a sure match
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST &#169 State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/CadastreParcels/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field PROP_NAME · 439979 records · sample None / None / None
- closes: 37 of 60 tested missing parks (by name 2, pin only 35; 76 of the area's 2871 missing parks lie in the layer's extent)
  - AU-0579 Kent Group National Park → polygon "DEAL ISLAND"
  - AU-10758 Pardoe Northdown Conservation Area → polygon ""
  - AU-11291 Great Lake Water Management Area → polygon ""
  - AU-11292 Arthurs Lake - Water Management Area → polygon ""
  - AU-11293 Romaine Reservoir - Water Management Area → polygon "ROMAINE RESERVE"
  - AU-11294 Lake Sorell - Water Management Area → polygon ""
  - AU-11295 Lake Crescent - Water Management Area → polygon ""
  - AU-11296 Curries River Reservoir - Water Management Area → polygon ""
  - AU-11297 Brandy Pond - Water Management Area → polygon ""
  - AU-11298 Bruins Pond - Water Management Area → polygon ""
  - AU-11299 Four Springs Lake - Water Management Area → polygon ""
  - AU-11300 Brushy Lagoon - Water Management Area → polygon ""
  - AU-11301 Lake Trevallyn - Water Management Area → polygon ""
  - AU-11302 Risdon Brook Reservoir - Water Management Area → polygon ""
  - AU-11303 Waterworks Reservoirs - Water Management Area → polygon "RIDGEWAY PARK"
  - AU-11305 Gordons Reservoir Water Management Area → polygon ""
  - AU-11306 Lake Pedder - Water Management Area → polygon ""
  - AU-11307 Lake Gordon Water Management Area → polygon ""
  - AU-11308 Tooms Lake - Water Management Area → polygon ""
  - AU-11309 Lake Leake - Water Management Area → polygon ""
  - AU-11310 Craigbourne Lake Water Management Area → polygon ""
  - AU-11311 Woods Lake Water Management Area → polygon ""
  - AU-11312 Pet Dam - Water Management Area → polygon "RIDGLEY WATER TREATMENT PLANT"
  - AU-1769 King Island Conservation Reserve → polygon ""
  - AU-8678 Seven Mile Beach - State Beach → polygon ""

### Public/PlanningOnline  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/PlanningOnline/MapServer/2
- WHY: official, credit terms, named polygons; closes 37 (name + pin 0, pin only 37): a pin inside a designation polygon is not a sure match
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST &#169 State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/PlanningOnline/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field FEAT_NAME · 439979 records · sample None / None / None
- closes: 37 of 60 tested missing parks (by name 0, pin only 37; 76 of the area's 2871 missing parks lie in the layer's extent)
  - AU-0579 Kent Group National Park → polygon ""
  - AU-10758 Pardoe Northdown Conservation Area → polygon ""
  - AU-11291 Great Lake Water Management Area → polygon ""
  - AU-11292 Arthurs Lake - Water Management Area → polygon ""
  - AU-11293 Romaine Reservoir - Water Management Area → polygon "Burnie"
  - AU-11294 Lake Sorell - Water Management Area → polygon ""
  - AU-11295 Lake Crescent - Water Management Area → polygon ""
  - AU-11296 Curries River Reservoir - Water Management Area → polygon ""
  - AU-11297 Brandy Pond - Water Management Area → polygon ""
  - AU-11298 Bruins Pond - Water Management Area → polygon ""
  - AU-11299 Four Springs Lake - Water Management Area → polygon ""
  - AU-11300 Brushy Lagoon - Water Management Area → polygon ""
  - AU-11301 Lake Trevallyn - Water Management Area → polygon ""
  - AU-11302 Risdon Brook Reservoir - Water Management Area → polygon ""
  - AU-11303 Waterworks Reservoirs - Water Management Area → polygon "Hobart"
  - AU-11305 Gordons Reservoir Water Management Area → polygon ""
  - AU-11306 Lake Pedder - Water Management Area → polygon ""
  - AU-11307 Lake Gordon Water Management Area → polygon ""
  - AU-11308 Tooms Lake - Water Management Area → polygon "Northern Midlands"
  - AU-11309 Lake Leake - Water Management Area → polygon ""
  - AU-11310 Craigbourne Lake Water Management Area → polygon ""
  - AU-11311 Woods Lake Water Management Area → polygon ""
  - AU-11312 Pet Dam - Water Management Area → polygon ""
  - AU-1769 King Island Conservation Reserve → polygon ""
  - AU-8678 Seven Mile Beach - State Beach → polygon ""

### SSSI units (England)  ·  GB  ·  from harvester
- url: https://services.arcgis.com/JJzESW51TqeY9uat/arcgis/rest/services/SSSI_Units_England/FeatureServer/1
- WHY: official, open terms, named polygons, closes 27 missing park(s)
- publisher: Defra group ArcGIS Online organisation → official (government words: Defra)
- terms: OPEN · source item page · "c access constraints to this data. Use of this data is subject to the Open Government Licence- https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/ © Natural Eng" · item https://www.arcgis.com/home/item.html?id=03fd7a2f8e4e4346bf41ce7879153949 · owner Opendata_NE · org Defra group ArcGIS Online organisation
- facts: arcgis-layer · esriGeometryPolygon · name field SSSI_NAME · 28305 records · last edit 2026-10-22 · sample Haugh and Gundale Slacks / Harwood Dale Moor / Shaw Beck Gill
- closes: 27 of 60 tested missing parks (by name 13, pin only 14; 3357 of the area's 3357 missing parks lie in the layer's extent)
  - GB-0002 Walton Moss SAC (inc Walton Moss NNR) Conservation Reserve → polygon "Bolton Fell and Walton Mosses"
  - GB-0024 Marshside RSPB Reserve → polygon "Ribble Estuary"
  - GB-0027 Broadland SPA - Sutton Fen RSPB Reserve → polygon "Ant Broads and Marshes"
  - GB-0045 Fowlmere RSPB Reserve → polygon "Fowlmere Watercress Beds"
  - GB-0049 Northumbrian Coast SPA - Blyth North Beach Protected Area → polygon "Northumberland Shore"
  - GB-0057 Hodbarrow RSPB Reserve → polygon "Duddon Estuary"
  - GB-0077 West Midlands Mosses SAC Conservation Reserve → polygon "Chartley Moss"
  - GB-0080 Spurn Point National Nature Reserve → polygon "Humber Estuary"
  - GB-0081 Gibralter Point National Nature Reserve → polygon "Gibraltar Point"
  - GB-0082 Ballard Down National Nature Reserve → polygon "Purbeck Ridge (East)"
  - GB-0091 Morecambe Pavements SAC (inc Hutton Roof Crags and Park Wood) National Nature Reserve → polygon "Hutton Roof Crags"
  - GB-0098 Buckenham Marshes RSPB Reserve → polygon "Yare Broads and Marshes"
  - GB-0121 Northumbrian Coast SPA - Spital Point & Carrs Protected Area → polygon "Northumberland Shore"
  - GB-0131 Mersey Narrows and North Wirral Foreshore SPA/SAC/Ramsar Conservation Reserve → polygon "North Wirral Foreshore"
  - GB-0141 Ensor's Pool SAC Conservation Reserve → polygon "Ensor's Pool"
  - GB-0145 Kingley Vale SAC Conservation Reserve → polygon "Kingley Vale"
  - GB-0153 Northumbrian Coast SPA - Cresswell Foreshore Protected Area → polygon "Northumberland Shore"
  - GB-0154 Dorset Heathlands - Stoborough Heath National Nature Reserve → polygon "Stoborough & Creech Heaths"
  - GB-0164 Nor Marsh & Motney Hill RSPB Reserve → polygon "Medway Estuary and Marshes"
  - GB-0172 Thames Basin Heaths SPA - Bagshot Heaths Protected Area → polygon "Broadmoor to Bagshot Woods and Heaths"
  - GB-0176 Benacre Broad to Easton Bavents Lagoons SPA Protected Area → polygon "Pakefield to Easton Bavents"
  - GB-0183 Dorset and East Devon Coast World Heritage Site Provincial Park → polygon "West Dorset Coast"
  - GB-0188 Thames Basin Heaths SPA - Broadmoor & Bagshot Heath Site of Significant Scientific Interest → polygon "Broadmoor to Bagshot Woods and Heaths"
  - GB-0194 Blacktoft Sands RSPB Reserve → polygon "Humber Estuary"
  - GB-0198 Thames Basin Heaths SPA - Yateley Heath Woods Site of Significant Scientific Interest → polygon "Castle Bottom to Yateley and Hawley Commons"
- TEST: ok

### Landgate_Public_Maps/Map_of_Bush_Fire_Prone_Areas_3  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/Landgate_Public_Maps/Map_of_Bush_Fire_Prone_Areas_3/MapServer/7
- WHY: official, credit terms, named polygons; closes 16 (name + pin 1, pin only 15): a pin inside a designation polygon is not a sure match
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- terms: CREDIT · source item page · "Landgate/SLIP/OBRM Landgate/SLIP/OBRM" · item https://public-services.slip.wa.gov.au/public/rest/services/Landgate_Public_Maps/Map_of_Bush_Fire_Prone_Areas_3/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field name · 139 records · sample COOROW, SHIRE OF / KONDININ, SHIRE OF / SHARK BAY, SHIRE OF
- closes: 16 of 60 tested missing parks (by name 1, pin only 15; 2871 of the area's 2871 missing parks lie in the layer's extent)
  - AU-0004 Yawuru Birragun Conservation Park → polygon "BROOME, SHIRE OF"
  - AU-0027 Tunnel Creek National Park → polygon "DERBY/WEST KIMBERLEY, SHIRE OF"
  - AU-0034 Swan Estuary Marine Park → polygon "PERTH, CITY OF"
  - AU-0040 Shoalwater Islands Marine Park → polygon "ROCKINGHAM, CITY OF"
  - AU-0042 Shark Bay Marine Park → polygon "SHARK BAY, SHIRE OF"
  - AU-0058 Ningaloo Marine Park → polygon "CARNARVON, SHIRE OF"
  - AU-0060 Ngari Capes Marine Park → polygon "AUGUSTA MARGARET RIVER, SHIRE OF"
  - AU-0066 Mount Manning - Helena And Aurora Ranges Conservation Park → polygon "YILGARN, SHIRE OF"
  - AU-0093 Lalang-garram / Camden Sound Marine Park → polygon "WYNDHAM-EAST KIMBERLEY, SHIRE OF"
  - AU-0099 Wunaamin Conservation Park → polygon "DERBY/WEST KIMBERLEY, SHIRE OF"
  - AU-0106 Jurien Bay Marine Park → polygon "DANDARAGAN, SHIRE OF"
  - AU-0126 Geikie Gorge National Park → polygon "DERBY/WEST KIMBERLEY, SHIRE OF"
  - AU-0127 Geikie Gorge Conservation Park → polygon "DERBY/WEST KIMBERLEY, SHIRE OF"
  - AU-0135 Eighty Mile Beach Marine Park → polygon "BROOME, SHIRE OF"
  - AU-0162 Brooking Gorge Conservation Park → polygon "DERBY/WEST KIMBERLEY, SHIRE OF"
  - AU-0506 McCorkill State Forest → polygon "NANNUP, SHIRE OF"

### ogc_services/Australian_Marine_Parks  ·  AU  ·  from harvester
- url: https://gis.environment.gov.au/gispubmap/rest/services/ogc_services/Australian_Marine_Parks/MapServer/0
- WHY: official, credit terms, named polygons; closes 2 (name + pin 0, pin only 2): a pin inside a designation polygon is not a sure match
- publisher: gis.environment.gov.au → official (government host gis.environment.gov.au)
- terms: CREDIT · source item page · "Australian Marine Parks © Commonwealth of Australia, Australian Government Department of Climate Change, Energy, th" · item https://gis.environment.gov.au/gispubmap/rest/services/ogc_services/Australian_Marine_Parks/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field NETNAME · 216 records · sample South-west / South-west / Temperate East
- closes: 2 of 60 tested missing parks (by name 0, pin only 2; 2871 of the area's 2871 missing parks lie in the layer's extent)
  - AU-0002 Willis Island National Park → polygon "Coral Sea"
  - AU-0046 Rowley Shoals Marine Park → polygon "North-west"

### ogc_services/Australian_Marine_Parks_Outer_Boundary/0  ·  AU  ·  from harvester
- url: https://gis.environment.gov.au/gispubmap/rest/services/ogc_services/Australian_Marine_Parks_Outer_Boundary/MapServer/0
- WHY: official, open terms, named polygons; closes 2 (name + pin 0, pin only 2): a pin inside a designation polygon is not a sure match
- publisher: gis.environment.gov.au → official (government host gis.environment.gov.au)
- terms: OPEN · source item page · "This dataset is released under Creative Commons by Attribution 4.0 International (CC BY 4.0). Australian Marine Parks © Commonwealth of A" · item https://gis.environment.gov.au/gispubmap/rest/services/ogc_services/Australian_Marine_Parks_Outer_Boundary/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field NETNAME · 61 records · sample South-east / North / North-west
- closes: 2 of 60 tested missing parks (by name 0, pin only 2; 2864 of the area's 2871 missing parks lie in the layer's extent)
  - AU-0002 Willis Island National Park → polygon "Coral Sea"
  - AU-0046 Rowley Shoals Marine Park → polygon "North-west"

### ogc_services/Indigenous_Protected_Areas/0  ·  AU  ·  from harvester
- url: https://gis.environment.gov.au/gispubmap/rest/services/ogc_services/Indigenous_Protected_Areas/FeatureServer/0
- WHY: official, credit terms, named polygons; closes 2 (name + pin 2, pin only 0): a pin inside a designation polygon is not a sure match
- publisher: gis.environment.gov.au → official (government host gis.environment.gov.au)
- terms: CREDIT · source item page · "When using this dataset for analysis or mapping you must always acknowledge the National Indigenous Australians Agency and the Department of Climate Change, Energy," · item https://gis.environment.gov.au/gispubmap/rest/services/ogc_services/Indigenous_Protected_Areas/FeatureServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field NAME · 120 records · sample Angkum / Anindilyakwa / Anindilyakwa
- closes: 2 of 60 tested missing parks (by name 2, pin only 0; 2871 of the area's 2871 missing parks lie in the layer's extent)
  - AU-0004 Yawuru Birragun Conservation Park → polygon "Yawuru"
  - AU-0717 Vernon Islands Conservation Reserve → polygon "Tiwi Islands"

### ogc_services/World_Heritage_Areas/0  ·  AU  ·  from harvester
- url: https://gis.environment.gov.au/gispubmap/rest/services/ogc_services/World_Heritage_Areas/MapServer/0
- WHY: official, open terms, named polygons; closes 2 (name + pin 2, pin only 0): a pin inside a designation polygon is not a sure match
- publisher: gis.environment.gov.au → official (government host gis.environment.gov.au)
- terms: OPEN · source item page · "Creative Commons by Attribution 4.0 International (CC BY 4.0) Australian Government Department of Agricult" · item https://gis.environment.gov.au/gispubmap/rest/services/ogc_services/World_Heritage_Areas/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field NAME · 49 records · sample Australian Convict Sites (Brickendon - Woolmers Buffer Zone) / Australian Convict Sites (Brickendon - Woolmers) / Australian Convict Sites (Old Government House and Domain Bu
- closes: 2 of 60 tested missing parks (by name 2, pin only 0; 2864 of the area's 2871 missing parks lie in the layer's extent)
  - AU-0042 Shark Bay Marine Park → polygon "Shark Bay, Western Australia"
  - AU-0058 Ningaloo Marine Park → polygon "Ningaloo Coast"

## WATER-ONLY (4)

### ogc_services/Ramsar_Wetlands  ·  AU  ·  from harvester
- url: https://gis.environment.gov.au/gispubmap/rest/services/ogc_services/Ramsar_Wetlands/FeatureServer/0
- WHY: water only: for the 2-fer owner step only (lakes / reservoirs / water bodies never go in the key as a park outline); otherwise READY: official, open terms, named polygons; closes 6 (name + pin 2, pin only 4): a pin inside a designation polygon is not a sure match
- publisher: gis.environment.gov.au → official (government host gis.environment.gov.au)
- FLAG: water only: for the 2-fer owner step only
- terms: OPEN · source item page · "Creative Commons by Attribution 4.0 International (CC BY 4.0) Australian Government Department of Agricult" · item https://gis.environment.gov.au/gispubmap/rest/services/ogc_services/Ramsar_Wetlands/FeatureServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field RAMSAR_NAME · 120 records · sample Pitt Water-Orielton Lagoon / Kerang Wetlands / Lavinia
- closes: 6 of 60 tested missing parks (by name 2, pin only 4; 2862 of the area's 2871 missing parks lie in the layer's extent)
  - AU-0004 Yawuru Birragun Conservation Park → polygon "Roebuck Bay"
  - AU-0187 Yaringa Marine National Park → polygon "Western Port"
  - AU-0293 Nooramunga Coastal & Marine Park → polygon "Corner Inlet"
  - AU-0450 Corner Inlet Marine National Park → polygon "Corner Inlet"
  - AU-0451 Corner Inlet Coastal & Marine Park → polygon "Corner Inlet"
  - AU-0460 Churchill Island Marine National Park → polygon "Western Port"

### USACE reservoirs (Army Corps of Engineers)  ·  US  ·  from chat 9
- url: https://services7.arcgis.com/n1YM8pTrFmm7L4hs/arcgis/rest/services/usace_rez/FeatureServer/0
- WHY: water only: for the 2-fer owner step only (lakes / reservoirs / water bodies never go in the key as a park outline); otherwise READY: official, open terms, named polygons, requested by chat 9
- publisher: U.S. Army Corps of Engineers → official (ArcGIS Online org n1YM8pTrFmm7L4hs = U.S. Army Corps of Engineers)
- FLAG: water only: for the 2-fer owner step only
- terms: OPEN · source item page · "This data set is publicly available without any use restrictions; however, this data set was developed for use at a national" · item https://www.arcgis.com/home/item.html?id=03e322d7e89b48a9b48e9c3f4bcaf29e · owner usace_erd_aep
- facts: arcgis-layer · esriGeometryPolygon · name field NAME · 418 records · last edit 2024-04-02 · sample Two Rivers Reservoir / Santa Rosa Reservoir / Conchas Reservoir
- closes: 0 of 60 tested missing parks (by name 0, pin only 0; 1245 of the area's 1274 missing parks lie in the layer's extent)
- TEST: ok

### SLIP_Public_Services/Environment  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Environment/MapServer/3
- WHY: water only: for the 2-fer owner step only (lakes / reservoirs / water bodies never go in the key as a park outline); otherwise ASK-THE-PUBLISHER: official and usable, but no missing parks were tested (none listed for the area or no time)
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- FLAG: water only: for the 2-fer owner step only
- terms: OPEN · source item page · "You are provided access to publicly available data on the terms and conditions of SLIP Transaction - Personal Use Licence, unless you a" · item https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Environment/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field cwt_suite_name
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 2871 of the area's 2871 missing parks lie in the layer's extent)

### SLIP_Public_Services/Environment_WFS  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Environment_WFS/MapServer/3
- WHY: water only: for the 2-fer owner step only (lakes / reservoirs / water bodies never go in the key as a park outline); otherwise ASK-THE-PUBLISHER: official and usable, but no missing parks were tested (none listed for the area or no time)
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- FLAG: water only: for the 2-fer owner step only
- terms: OPEN · source item page · "You are provided access to publicly available data on the terms and conditions of SLIP Transaction - Personal Use Licence, unless you a" · item https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Environment_WFS/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field cwt_suite_name
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 2871 of the area's 2871 missing parks lie in the layer's extent)

## LIVE-ONLY (1)

### Czechia natural parks (AOPK CR, gis.nature.cz, Prirodni park)  ·  CZ  ·  from chat 9
- url: https://gis.nature.cz/arcgis/rest/services/ObecnaOchrana/PrirodniPark/MapServer/0
- WHY: terms allow viewing only: read live, never stored
- publisher: Agentura ochrany prirody a krajiny CR (nature.cz) → official (government host gis.nature.cz)
- terms note: KNOWN_TERMS override: CREDIT read on the service → LIVE-ONLY. AOPK ČR's own pages say the map services are for viewing only (chat 8 WORLD/CZ_desk.md); the service copyrightText is only a credit
- terms: LIVE-ONLY · source known-terms table (the agency states its terms elsewhere) · "© AOPK ČR, podkladová data: Krajské úřady (2022) © krajské úřady ČR a Magistrát hl. m. Prah" · item https://gis.nature.cz/arcgis/rest/services/ObecnaOchrana/PrirodniPark/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field NAZEV · 141 records · sample Hostýnské vrchy / Záhlinické rybníky / Chřiby
- closes: 19 of 19 tested missing parks (by name 18, pin only 1; 19 of the area's 19 missing parks lie in the layer's extent)
  - CZ-0040 Berounka Nature Park → polygon "Berounka"
  - CZ-0041 Rohatiny Nature Park → polygon "Rohatiny"
  - CZ-0042 Manětínská Nature Park → polygon "Manětínská"
  - CZ-0043 Javořická vrchovina Nature Park → polygon "Javořická vrchovina"
  - CZ-0047 Čeřínek Nature Park → polygon "Čeřínek"
  - CZ-0048 Česká Kanada Nature Park → polygon "Česká Kanada"
  - CZ-0055 Homolka – Vojířov Nature Park → polygon "Homolka - Vojířov"
  - CZ-0056 Zelenov Nature Park → polygon "Zelenov"
  - CZ-0063 Radeč Nature Park → polygon "Radeč"
  - CZ-0075 Trhoň Nature Park → polygon "Trhoň"
  - CZ-0076 Džbány-Žebrák Nature Park → polygon "Džbány-Žebrák"
  - CZ-0115 Hostivar-Zabehlice Nature Park → polygon "Hostivař - Záběhlice"
  - CZ-0128 Plánický hřeben Nature Park → polygon "Plánický hřeben"
  - CZ-0129 Kakov - Plánický hřeben Nature Park → polygon "Kakov - Plánický hřeben"
  - CZ-0130 Svratecká hornatina Nature Park → polygon "Svratecká hornatina"
  - CZ-0131 Lysicko Nature Park → polygon "Lysicko"
  - CZ-0132 Halasovo Kunštátsko Nature Park → polygon "Halasovo Kunštátsko"
  - CZ-0138 Pod Stedrym Nature Park → polygon "Pod Štědrým"
  - CZ-0139 Ještěd Nature Park → polygon "Ještěd"
- TEST: ok

## ASK-THE-PUBLISHER (15)

### AerialPhotoViewer/Orthophoto_Coverage_Area  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/AerialPhotoViewer/Orthophoto_Coverage_Area/MapServer/0
- WHY: nothing stated about use on the item page or the service
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: NOTHING STATED · source item page · item https://services.thelist.tas.gov.au/arcgis/rest/services/AerialPhotoViewer/Orthophoto_Coverage_Area/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field PROJ_NAME · 8385 records · sample 42000 Revision 0910 / 42000 Revision 0910 / 42000 Revision 0910
- closes: 40 of 60 tested missing parks (by name 3, pin only 37; 77 of the area's 2871 missing parks lie in the layer's extent)
  - AU-0579 Kent Group National Park → polygon "Bass Strait Is. (Kent Group)"
  - AU-10758 Pardoe Northdown Conservation Area → polygon "Low Water Mark"
  - AU-11291 Great Lake Water Management Area → polygon "42000 Revision 0910"
  - AU-11292 Arthurs Lake - Water Management Area → polygon "42000 Revision 0910"
  - AU-11293 Romaine Reservoir - Water Management Area → polygon "A135 Urban 2011-12"
  - AU-11294 Lake Sorell - Water Management Area → polygon "WOOLNORTH 1:20000 COLOUR"
  - AU-11295 Lake Crescent - Water Management Area → polygon "42000 Revision 0910"
  - AU-11296 Curries River Reservoir - Water Management Area → polygon "NORTH EAST REVISION 2005-06"
  - AU-11297 Brandy Pond - Water Management Area → polygon "West Tamar Municipality 25cm"
  - AU-11298 Bruins Pond - Water Management Area → polygon "West Tamar Municipality 25cm"
  - AU-11299 Four Springs Lake - Water Management Area → polygon "CENTRAL NORTH REVISION  2007-08"
  - AU-11300 Brushy Lagoon - Water Management Area → polygon "CENTRAL NORTH REVISION  2007-08"
  - AU-11301 Lake Trevallyn - Water Management Area → polygon "CENTRAL NORTH REVISION  2007-08"
  - AU-11302 Risdon Brook Reservoir - Water Management Area → polygon "HUON - DERWENT: URBAN ORTHO"
  - AU-11303 Waterworks Reservoirs - Water Management Area → polygon "HUON - DERWENT: URBAN ORTHO"
  - AU-11304 Pipe Clay Lagoon - Water Management Area → polygon "SOUTHERN REVISION 2007"
  - AU-11305 Gordons Reservoir Water Management Area → polygon "HUON - DERWENT : URBAN OPM"
  - AU-11306 Lake Pedder - Water Management Area → polygon "SOUTH WEST REVISION"
  - AU-11307 Lake Gordon Water Management Area → polygon "SOUTH WEST REVISION  2006-07"
  - AU-11308 Tooms Lake - Water Management Area → polygon "CENTRAL EAST REVISION 2005-06"
  - AU-11309 Lake Leake - Water Management Area → polygon "42000 Revision 0910"
  - AU-11310 Craigbourne Lake Water Management Area → polygon "CRAIGBOURNE DAM"
  - AU-11311 Woods Lake Water Management Area → polygon "42000 Revision 0910"
  - AU-11312 Pet Dam - Water Management Area → polygon "NORTH WEST FORESTRY  2006-07"
  - AU-1769 King Island Conservation Reserve → polygon "LWM 2011-12 24000V2"

### AerialPhotoViewer/Aerial_Photo_Coverage_Areas  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/AerialPhotoViewer/Aerial_Photo_Coverage_Areas/MapServer/0
- WHY: nothing stated about use on the item page or the service
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: NOTHING STATED · source item page · item https://services.thelist.tas.gov.au/arcgis/rest/services/AerialPhotoViewer/Aerial_Photo_Coverage_Areas/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field PROJ_NAME · 186461 records · sample SOUTH EAST   FORESTRY 95 / NORTH WEST  FORESTRY 96-97 / NORTH EAST  FORESTRY EXTN.
- closes: 10 of 60 tested missing parks (by name 0, pin only 10; 207 of the area's 2871 missing parks lie in the layer's extent)
  - AU-0579 Kent Group National Park → polygon "LWM 2011-12 24000V3"
  - AU-10147 Bare Back Cove State Beach → polygon "BASS STRAIT"
  - AU-10180 Chinaman Long Beach State Beach → polygon "BASS STRAIT"
  - AU-10185 Cotters Beach State Beach → polygon "BASS STRAIT"
  - AU-10195 Darby Beach State Beach → polygon "BASS STRAIT"
  - AU-10207 Red Bluff Beach State Beach → polygon "BASS STRAIT"
  - AU-10212 Fairy Cove State Beach → polygon "BASS STRAIT"
  - AU-10217 Five Mile Beach National Park → polygon "BASS STRAIT"
  - AU-10247 Johnny Souey Cove State Beach → polygon "BASS STRAIT"
  - AU-10248 Keijsers Beach State Beach → polygon "BASS STRAIT"

### Public/NVAdata  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/NVAdata/MapServer/6
- WHY: nothing stated about use on the item page or the service
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: NOTHING STATED · source item page · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/NVAdata/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field SPECIES_NAME · 5186 records · sample Rubus fruticosus / Ulex europaeus / Hypericum perforatum subsp. veronense
- closes: 4 of 60 tested missing parks (by name 0, pin only 4; 74 of the area's 2871 missing parks lie in the layer's extent)
  - AU-10758 Pardoe Northdown Conservation Area → polygon "Asparagus asparagoides"
  - AU-11304 Pipe Clay Lagoon - Water Management Area → polygon "Brachionichthys hirsutus"
  - AU-8812 Nutgrove Beach - State Beach → polygon "Brachionichthys hirsutus"
  - AU-8858 Howrah Beach - State Beach → polygon "Brachionichthys hirsutus"

### SLIP_Public_Services/DPIRD_Fisheries_Guide_WFS  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/DPIRD_Fisheries_Guide_WFS/MapServer/0
- WHY: nothing stated about use on the item page or the service
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- terms: NOTHING STATED · source item page · item https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/DPIRD_Fisheries_Guide_WFS/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field name · 18 records · sample Kimberley Gillnet and Barramundi Fishery / Kimberley Gillnet and Barramundi Fishery / Kimberley Gillnet and Barramundi Fishery
- closes: 2 of 60 tested missing parks (by name 0, pin only 2; 2871 of the area's 2871 missing parks lie in the layer's extent)
  - AU-0004 Yawuru Birragun Conservation Park → polygon "Kimberley Gillnet and Barramundi Fishery"
  - AU-0058 Ningaloo Marine Park → polygon "Point Maud to Tantabiddi Closure"

### SCDNR managed lands (public viewer) on Clemson's ArcGIS Online account  ·  US-SC  ·  from chat 9
- url: https://services1.arcgis.com/x5wCko8UnSi4h0CB/arcgis/rest/services/SCDNR_Managed_Lands_Public_Viewer/FeatureServer/0
- WHY: hosted for an agency on another account: ask who owns and licenses it
- publisher: Clemson University (hosting for South Carolina DNR) → hosted for an agency (ArcGIS Online org x5wCko8UnSi4h0CB = Clemson University (hosts layers for SCDNR))
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=3f8ed80d29bb4335a6b5cd28bc0f15d7 · owner bneece@clemson.edu_Clemson · org Clemson University
- facts: arcgis-layer · esriGeometryPolygon · name field prop_name · 963 records · last edit 2023-05-04 · sample Altamaha Towne Heritage Preserve / Fish Dam Ford Heritage Preserve / Combahee Island Heritage Preserve / Wildlife Management Area
- closes: 1 of 5 tested missing parks (by name 0, pin only 1; 5 of the area's 5 missing parks lie in the layer's extent)
  - US-9229 Wild Turkey Wildlife Management Area → polygon "Unnamed WMA"
- TEST: ok

### PEI provincial parks (GeoLinc, ENV polygon layer)  ·  CA-PE  ·  from chat 9
- url: https://gis.princeedwardisland.ca/server/rest/services/GeoLincData/GeoLinc_provincial_park_polygon_ENV/MapServer/0
- WHY: nothing stated about use on the item page or the service
- publisher: Government of Prince Edward Island (GeoLinc) → official (government host gis.princeedwardisland.ca)
- terms: NOTHING STATED · source none
- facts: arcgis-layer · esriGeometryPolygon · name field PARK · 46 records · sample PROV / PROV PARK / BRUDENELL
- overlap: same publisher as PE-PP Govern
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 36 missing parks lie in the layer's extent)
- TEST: ok

### Public/CadastreAndAdministrativeV2  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/CadastreAndAdministrativeV2/MapServer/1
- WHY: nothing stated about use on the item page or the service
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: NOTHING STATED · source item page · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/CadastreAndAdministrativeV2/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field NAME · 3601 records · sample None / None / None
- closes: not probed

### Public/CadastreAndAdministrativeV2  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/CadastreAndAdministrativeV2/MapServer/5
- WHY: nothing stated about use on the item page or the service
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: NOTHING STATED · source item page · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/CadastreAndAdministrativeV2/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field NAME · 6 records · sample BB103H HWP2 / CE333C 2SWP / FN029F HWP2
- closes: not probed

### Public/CadastreAndAdministrativeV2  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/CadastreAndAdministrativeV2/MapServer/10
- WHY: nothing stated about use on the item page or the service
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: NOTHING STATED · source item page · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/CadastreAndAdministrativeV2/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field NAME · 44 records · sample Kanamaluka / Taypalaka / Luemerrernanner
- closes: not probed

### Public/NVAdata  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/NVAdata/MapServer/7
- WHY: nothing stated about use on the item page or the service
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: NOTHING STATED · source item page · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/NVAdata/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field SPECIES_NAME · 14 records · sample Digitalis purpurea / Ulex europaeus / Ulex europaeus
- closes: 0 of 2 tested missing parks (by name 0, pin only 0; 18 of the area's 2871 missing parks lie in the layer's extent)

### Public/NaturalEnvironmentV2  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/NaturalEnvironmentV2/MapServer/12
- WHY: nothing stated about use on the item page or the service
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: NOTHING STATED · source item page · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/NaturalEnvironmentV2/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field SCHED_NAME · 50187 records · sample Alkaline pans / Alkaline pans / Alkaline pans
- closes: 0 of 57 tested missing parks (by name 0, pin only 0; 76 of the area's 2871 missing parks lie in the layer's extent)

### Public/PlanningOnline  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/PlanningOnline/MapServer/3
- WHY: official and usable, but no missing parks were tested (none listed for the area or no time)
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/PlanningOnline/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field O_NAME · 57546 records · sample Landslide Hazard Area / Landslide Hazard Area / Landslide Hazard Area
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 46 of the area's 2871 missing parks lie in the layer's extent)

### Public/WildFisheries  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/WildFisheries/MapServer/1
- WHY: nothing stated about use on the item page or the service
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: NOTHING STATED · source item page · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/WildFisheries/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field AREA_NAME · 6 records · sample Ninepin Point Marine Nature Reserve / Port Davey/Bathurst Harbour Marine Nature Reserve - No Fishi / Maria Island Marine Nature Reserve - No Fishing Zone
- closes: 0 of 60 tested missing parks (by name 0, pin only 0; 229 of the area's 2871 missing parks lie in the layer's extent)

### Public/WildFisheries  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/WildFisheries/MapServer/3
- WHY: nothing stated about use on the item page or the service
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: NOTHING STATED · source item page · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/WildFisheries/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field AREA_NAME · 2 records · sample Kent Group Marine Nature Reserve - Restricted Fishing Zone / Port Davey Marine Nature Reserve 
- closes: 0 of 2 tested missing parks (by name 0, pin only 0; 229 of the area's 2871 missing parks lie in the layer's extent)

### SLIP_Public_Services/DPIRD_Fisheries_Guide_WFS  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/DPIRD_Fisheries_Guide_WFS/MapServer/1
- WHY: nothing stated about use on the item page or the service
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- terms: NOTHING STATED · source item page · item https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/DPIRD_Fisheries_Guide_WFS/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field name · 63 records · sample Aquaculture Instrument of Exemption / Aquaculture Instrument of Exemption / Aquaculture Instrument of Exemption
- closes: 0 of 2 tested missing parks (by name 0, pin only 0; 2871 of the area's 2871 missing parks lie in the layer's extent)

## RETRY (66)

### My favorite camping spots (a hobby map)  ·  US-KY  ·  from chat 9
- url: https://services9.arcgis.com/abc123hobby/arcgis/rest/services/My_Favorite_Camping_Spots/FeatureServer/0
- WHY: did not open 3 times (error Invalid URL): chat 9 checks the url
- publisher: hobby account (personal map) → not official (hobby in the publisher words)
- terms: NOTHING STATED · source none
- facts: status error Invalid URL
- closes: not probed
- TEST: ok

### Slovenia protected areas (ARSO, INSPIRE PS WFS)  ·  W-SI  ·  from chat 9
- url: https://prostor4.gov.si/ows2-ins/ps/wfs
- WHY: did not open 3 times (rest): chat 9 checks the url
- publisher: Agencija RS za okolje (ARSO) / Slovenian Environment Agency → official (government host prostor4.gov.si)
- terms: OPEN · source GetCapabilities + queue row · "ATOM feed rights: 'No limitations'"
- facts: wfs · status rest
- closes: not probed: WFS point query not built
- TEST: ok

### Landgate_Public_Maps/Marine_Map_WA_3  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/Landgate_Public_Maps/Marine_Map_WA_3/MapServer/5
- WHY: did not open 3 times (budget): chat 9 checks the url
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- terms: CREDIT · source item page · "WALIS WALIS" · item https://public-services.slip.wa.gov.au/public/rest/services/Landgate_Public_Maps/Marine_Map_WA_3/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### Landgate_Public_Maps/Marine_Map_WA_3  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/Landgate_Public_Maps/Marine_Map_WA_3/MapServer/6
- WHY: did not open 3 times (budget): chat 9 checks the url
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- terms: CREDIT · source item page · "WALIS WALIS" · item https://public-services.slip.wa.gov.au/public/rest/services/Landgate_Public_Maps/Marine_Map_WA_3/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### Landgate_Public_Maps/Marine_Map_WA_3  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/Landgate_Public_Maps/Marine_Map_WA_3/MapServer/10
- WHY: did not open 3 times (budget): chat 9 checks the url
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- terms: CREDIT · source item page · "WALIS WALIS" · item https://public-services.slip.wa.gov.au/public/rest/services/Landgate_Public_Maps/Marine_Map_WA_3/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### Landgate_Public_Maps/Marine_Map_WA_3  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/Landgate_Public_Maps/Marine_Map_WA_3/MapServer/11
- WHY: did not open 3 times (budget): chat 9 checks the url
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- terms: CREDIT · source item page · "WALIS WALIS" · item https://public-services.slip.wa.gov.au/public/rest/services/Landgate_Public_Maps/Marine_Map_WA_3/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### Landgate_Public_Maps/Marine_Map_WA_3  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/Landgate_Public_Maps/Marine_Map_WA_3/MapServer/12
- WHY: did not open 3 times (budget): chat 9 checks the url
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- terms: CREDIT · source item page · "WALIS WALIS" · item https://public-services.slip.wa.gov.au/public/rest/services/Landgate_Public_Maps/Marine_Map_WA_3/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### Landgate_Public_Maps/Marine_Map_WA_3  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/Landgate_Public_Maps/Marine_Map_WA_3/MapServer/14
- WHY: did not open 3 times (budget): chat 9 checks the url
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- terms: CREDIT · source item page · "WALIS WALIS" · item https://public-services.slip.wa.gov.au/public/rest/services/Landgate_Public_Maps/Marine_Map_WA_3/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### Public/NVAdata  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/NVAdata/MapServer/10
- WHY: did not open 3 times (budget): chat 9 checks the url
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: NOTHING STATED · source item page · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/NVAdata/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### Public/NVAdata  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/NVAdata/MapServer/11
- WHY: did not open 3 times (budget): chat 9 checks the url
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: NOTHING STATED · source item page · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/NVAdata/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### Public/NVAdata  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/NVAdata/MapServer/13
- WHY: did not open 3 times (budget): chat 9 checks the url
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: NOTHING STATED · source item page · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/NVAdata/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### Public/NVAdata  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/NVAdata/MapServer/17
- WHY: did not open 3 times (budget): chat 9 checks the url
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: NOTHING STATED · source item page · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/NVAdata/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### Public/NaturalEnvironment  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/NaturalEnvironment/MapServer/6
- WHY: did not open 3 times (budget): chat 9 checks the url
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/NaturalEnvironment/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### Public/NaturalEnvironment  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/NaturalEnvironment/MapServer/7
- WHY: did not open 3 times (budget): chat 9 checks the url
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/NaturalEnvironment/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### Public/NaturalEnvironment  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/NaturalEnvironment/MapServer/10
- WHY: did not open 3 times (budget): chat 9 checks the url
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/NaturalEnvironment/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### Public/NaturalEnvironment  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/NaturalEnvironment/MapServer/12
- WHY: did not open 3 times (budget): chat 9 checks the url
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/NaturalEnvironment/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### Public/NaturalEnvironment  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/NaturalEnvironment/MapServer/16
- WHY: did not open 3 times (budget): chat 9 checks the url
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/NaturalEnvironment/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### Public/OpenDataWFS  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/OpenDataWFS/MapServer/8
- WHY: did not open 3 times (budget): chat 9 checks the url
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/OpenDataWFS/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### Public/PWSPublic  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/PWSPublic/MapServer/2
- WHY: did not open 3 times (budget): chat 9 checks the url
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/PWSPublic/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### Public/PWSPublic  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/PWSPublic/MapServer/3
- WHY: did not open 3 times (budget): chat 9 checks the url
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/PWSPublic/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### Public/PWSPublic  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/PWSPublic/MapServer/4
- WHY: did not open 3 times (budget): chat 9 checks the url
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/PWSPublic/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### Public/PWSPublic  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/PWSPublic/MapServer/5
- WHY: did not open 3 times (budget): chat 9 checks the url
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/PWSPublic/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### Public/PWSPublic  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/PWSPublic/MapServer/8
- WHY: did not open 3 times (budget): chat 9 checks the url
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/PWSPublic/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### Public/PWSPublic  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/PWSPublic/MapServer/10
- WHY: did not open 3 times (budget): chat 9 checks the url
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/PWSPublic/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### Public/TopographyAndRelief  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/TopographyAndRelief/MapServer/20
- WHY: did not open (budget): probed again next run (failed 2 of 3)
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST © State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/TopographyAndRelief/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### Public/TopographyAndRelief  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/TopographyAndRelief/MapServer/21
- WHY: did not open (budget): probed again next run (failed 2 of 3)
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST © State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/TopographyAndRelief/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### Public/TopographyAndRelief  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/TopographyAndRelief/MapServer/22
- WHY: did not open (budget): probed again next run (failed 2 of 3)
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST © State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/TopographyAndRelief/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### Public/TopographyAndRelief  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/TopographyAndRelief/MapServer/23
- WHY: did not open (budget): probed again next run (failed 2 of 3)
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST © State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/TopographyAndRelief/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### Public/TopographyAndRelief  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/TopographyAndRelief/MapServer/27
- WHY: did not open (budget): probed again next run (failed 2 of 3)
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST © State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/TopographyAndRelief/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### Public/TopographyAndRelief  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/TopographyAndRelief/MapServer/35
- WHY: did not open (budget): probed again next run (failed 2 of 3)
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST © State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/TopographyAndRelief/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### Public/WildFisheries  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/WildFisheries/MapServer/2
- WHY: did not open (budget): probed again next run (failed 2 of 3)
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: NOTHING STATED · source item page · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/WildFisheries/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### Public/WildFisheries  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/WildFisheries/MapServer/4
- WHY: did not open (budget): probed again next run (failed 2 of 3)
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: NOTHING STATED · source item page · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/WildFisheries/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### Public/WildFisheries  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/WildFisheries/MapServer/5
- WHY: did not open (budget): probed again next run (failed 2 of 3)
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: NOTHING STATED · source item page · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/WildFisheries/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### Public/WildFisheries  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/WildFisheries/MapServer/6
- WHY: did not open (budget): probed again next run (failed 2 of 3)
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: NOTHING STATED · source item page · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/WildFisheries/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### Public/WildFisheries  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/WildFisheries/MapServer/7
- WHY: did not open (budget): probed again next run (failed 2 of 3)
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: NOTHING STATED · source item page · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/WildFisheries/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### Public/WildFisheries  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/WildFisheries/MapServer/8
- WHY: did not open (budget): probed again next run (failed 2 of 3)
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: NOTHING STATED · source item page · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/WildFisheries/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### SLIP_Public_Services/Boundaries  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Boundaries/MapServer/2
- WHY: did not open (budget): probed again next run (failed 1 of 3)
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- terms: NON-COMMERCIAL · source item page · "sing this data, you agree to only use this data for your personal and non-commercial use. You are not permitted to, in any form, reproduce, distribute, commercialise or creat" · item https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Boundaries/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### SLIP_Public_Services/Boundaries  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Boundaries/MapServer/3
- WHY: did not open (budget): probed again next run (failed 1 of 3)
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- terms: NON-COMMERCIAL · source item page · "sing this data, you agree to only use this data for your personal and non-commercial use. You are not permitted to, in any form, reproduce, distribute, commercialise or creat" · item https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Boundaries/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### SLIP_Public_Services/Boundaries  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Boundaries/MapServer/4
- WHY: did not open (budget): probed again next run (failed 1 of 3)
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- terms: NON-COMMERCIAL · source item page · "sing this data, you agree to only use this data for your personal and non-commercial use. You are not permitted to, in any form, reproduce, distribute, commercialise or creat" · item https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Boundaries/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### SLIP_Public_Services/Boundaries  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Boundaries/MapServer/5
- WHY: did not open (budget): probed again next run (failed 1 of 3)
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- terms: NON-COMMERCIAL · source item page · "sing this data, you agree to only use this data for your personal and non-commercial use. You are not permitted to, in any form, reproduce, distribute, commercialise or creat" · item https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Boundaries/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### SLIP_Public_Services/Boundaries  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Boundaries/MapServer/51
- WHY: did not open (budget): probed again next run (failed 1 of 3)
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- terms: NON-COMMERCIAL · source item page · "sing this data, you agree to only use this data for your personal and non-commercial use. You are not permitted to, in any form, reproduce, distribute, commercialise or creat" · item https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Boundaries/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### SLIP_Public_Services/Boundaries  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Boundaries/MapServer/52
- WHY: did not open (budget): probed again next run (failed 1 of 3)
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- terms: NON-COMMERCIAL · source item page · "sing this data, you agree to only use this data for your personal and non-commercial use. You are not permitted to, in any form, reproduce, distribute, commercialise or creat" · item https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Boundaries/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### SLIP_Public_Services/Boundaries_WFS  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Boundaries_WFS/MapServer/2
- WHY: did not open (budget): probed again next run (failed 1 of 3)
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- terms: NON-COMMERCIAL · source item page · "sing this data, you agree to only use this data for your personal and non-commercial use. You are not permitted to, in any form, reproduce, distribute, commercialise or creat" · item https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Boundaries_WFS/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### SLIP_Public_Services/Boundaries_WFS  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Boundaries_WFS/MapServer/3
- WHY: did not open (budget): probed again next run (failed 1 of 3)
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- terms: NON-COMMERCIAL · source item page · "sing this data, you agree to only use this data for your personal and non-commercial use. You are not permitted to, in any form, reproduce, distribute, commercialise or creat" · item https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Boundaries_WFS/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### SLIP_Public_Services/Boundaries_WFS  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Boundaries_WFS/MapServer/4
- WHY: did not open (budget): probed again next run (failed 1 of 3)
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- terms: NON-COMMERCIAL · source item page · "sing this data, you agree to only use this data for your personal and non-commercial use. You are not permitted to, in any form, reproduce, distribute, commercialise or creat" · item https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Boundaries_WFS/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### SLIP_Public_Services/Boundaries_WFS  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Boundaries_WFS/MapServer/5
- WHY: did not open (budget): probed again next run (failed 1 of 3)
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- terms: NON-COMMERCIAL · source item page · "sing this data, you agree to only use this data for your personal and non-commercial use. You are not permitted to, in any form, reproduce, distribute, commercialise or creat" · item https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Boundaries_WFS/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### SLIP_Public_Services/Boundaries_WFS  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Boundaries_WFS/MapServer/36
- WHY: did not open (budget): probed again next run (failed 1 of 3)
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- terms: NON-COMMERCIAL · source item page · "sing this data, you agree to only use this data for your personal and non-commercial use. You are not permitted to, in any form, reproduce, distribute, commercialise or creat" · item https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Boundaries_WFS/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### SLIP_Public_Services/Boundaries_WFS  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Boundaries_WFS/MapServer/37
- WHY: did not open (budget): probed again next run (failed 1 of 3)
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- terms: NON-COMMERCIAL · source item page · "sing this data, you agree to only use this data for your personal and non-commercial use. You are not permitted to, in any form, reproduce, distribute, commercialise or creat" · item https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Boundaries_WFS/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### SLIP_Public_Services/DPIRD_Fisheries_Guide_WFS  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/DPIRD_Fisheries_Guide_WFS/MapServer/2
- WHY: did not open (budget): probed again next run (failed 1 of 3)
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- terms: NOTHING STATED · source item page · item https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/DPIRD_Fisheries_Guide_WFS/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### SLIP_Public_Services/DPIRD_Fisheries_Guide_WFS  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/DPIRD_Fisheries_Guide_WFS/MapServer/3
- WHY: did not open (budget): probed again next run (failed 1 of 3)
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- terms: NOTHING STATED · source item page · item https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/DPIRD_Fisheries_Guide_WFS/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### SLIP_Public_Services/DPIRD_Fisheries_Guide_WFS  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/DPIRD_Fisheries_Guide_WFS/MapServer/5
- WHY: did not open (budget): probed again next run (failed 1 of 3)
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- terms: NOTHING STATED · source item page · item https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/DPIRD_Fisheries_Guide_WFS/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### SLIP_Public_Services/DPIRD_Fisheries_Guide_WFS  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/DPIRD_Fisheries_Guide_WFS/MapServer/6
- WHY: did not open (budget): probed again next run (failed 1 of 3)
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- terms: NOTHING STATED · source item page · item https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/DPIRD_Fisheries_Guide_WFS/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### SLIP_Public_Services/DPIRD_Fisheries_Guide_WFS  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/DPIRD_Fisheries_Guide_WFS/MapServer/7
- WHY: did not open (budget): probed again next run (failed 1 of 3)
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- terms: NOTHING STATED · source item page · item https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/DPIRD_Fisheries_Guide_WFS/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### SLIP_Public_Services/DPIRD_Fisheries_Guide_WFS  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/DPIRD_Fisheries_Guide_WFS/MapServer/8
- WHY: did not open (budget): probed again next run (failed 1 of 3)
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- terms: NOTHING STATED · source item page · item https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/DPIRD_Fisheries_Guide_WFS/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### SLIP_Public_Services/Environment  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Environment/MapServer/4
- WHY: did not open (budget): probed again next run (failed 1 of 3)
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- terms: NON-COMMERCIAL · source item page · "sing this data, you agree to only use this data for your personal and non-commercial use. You are not permitted to, in any form, reprodu" · item https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Environment/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### SLIP_Public_Services/Environment  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Environment/MapServer/5
- WHY: did not open (budget): probed again next run (failed 1 of 3)
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- terms: NON-COMMERCIAL · source item page · "sing this data, you agree to only use this data for your personal and non-commercial use. You are not permitted to, in any form, reprodu" · item https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Environment/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### SLIP_Public_Services/Environment  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Environment/MapServer/83
- WHY: did not open (budget): probed again next run (failed 1 of 3)
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- terms: NON-COMMERCIAL · source item page · "sing this data, you agree to only use this data for your personal and non-commercial use. You are not permitted to, in any form, reprodu" · item https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Environment/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### SLIP_Public_Services/Environment  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Environment/MapServer/84
- WHY: did not open (budget): probed again next run (failed 1 of 3)
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- terms: NON-COMMERCIAL · source item page · "sing this data, you agree to only use this data for your personal and non-commercial use. You are not permitted to, in any form, reprodu" · item https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Environment/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### SLIP_Public_Services/Environment_WFS  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Environment_WFS/MapServer/4
- WHY: did not open (budget): probed again next run (failed 1 of 3)
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- terms: NON-COMMERCIAL · source item page · "sing this data, you agree to only use this data for your personal and non-commercial use. You are not permitted to, in any form, reprodu" · item https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Environment_WFS/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### SLIP_Public_Services/Environment_WFS  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Environment_WFS/MapServer/5
- WHY: did not open (budget): probed again next run (failed 1 of 3)
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- terms: NON-COMMERCIAL · source item page · "sing this data, you agree to only use this data for your personal and non-commercial use. You are not permitted to, in any form, reprodu" · item https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Environment_WFS/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### SLIP_Public_Services/Environment_WFS  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Environment_WFS/MapServer/83
- WHY: did not open (budget): probed again next run (failed 1 of 3)
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- terms: NON-COMMERCIAL · source item page · "sing this data, you agree to only use this data for your personal and non-commercial use. You are not permitted to, in any form, reprodu" · item https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Environment_WFS/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### SLIP_Public_Services/Environment_WFS  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Environment_WFS/MapServer/84
- WHY: did not open (budget): probed again next run (failed 1 of 3)
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- terms: NON-COMMERCIAL · source item page · "sing this data, you agree to only use this data for your personal and non-commercial use. You are not permitted to, in any form, reprodu" · item https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Environment_WFS/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### SLIP_Public_Services/Farming  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Farming/MapServer/4
- WHY: did not open (budget): probed again next run (failed 1 of 3)
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- terms: CREDIT · source item page · "SLIP SLIP" · item https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Farming/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### SLIP_Public_Services/Farming  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Farming/MapServer/5
- WHY: did not open (budget): probed again next run (failed 1 of 3)
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- terms: CREDIT · source item page · "SLIP SLIP" · item https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Farming/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### SLIP_Public_Services/Farming  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Farming/MapServer/6
- WHY: did not open (budget): probed again next run (failed 1 of 3)
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- terms: CREDIT · source item page · "SLIP SLIP" · item https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Farming/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

### SLIP_Public_Services/Farming  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Farming/MapServer/7
- WHY: did not open (budget): probed again next run (failed 1 of 3)
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- terms: CREDIT · source item page · "SLIP SLIP" · item https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Farming/MapServer/info/iteminfo
- facts: status budget
- closes: not probed

## REJECT (108)

### SLIP_Public_Services/Boundaries  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Boundaries/MapServer/0
- WHY: NOT A PARK LAYER (coverage): closes 60 but only 0 by name (READY needs 3+ name matches and 25%+ of the closes)
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- terms: NON-COMMERCIAL · source item page · "sing this data, you agree to only use this data for your personal and non-commercial use. You are not permitted to, in any form, reproduce, distribute, commercialise or creat" · item https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Boundaries/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field name · 18 records · sample ACT and Jervis Bay / Central Desert / Geraldton
- closes: 60 of 60 tested missing parks (by name 0, pin only 60; 2871 of the area's 2871 missing parks lie in the layer's extent)
  - AU-0002 Willis Island National Park → polygon "Cape York Region"
  - AU-0004 Yawuru Birragun Conservation Park → polygon "Kimberley"
  - AU-0027 Tunnel Creek National Park → polygon "Kimberley"
  - AU-0034 Swan Estuary Marine Park → polygon "South West"
  - AU-0040 Shoalwater Islands Marine Park → polygon "South West"
  - AU-0042 Shark Bay Marine Park → polygon "Geraldton"
  - AU-0046 Rowley Shoals Marine Park → polygon "Kimberley"
  - AU-0058 Ningaloo Marine Park → polygon "Geraldton"
  - AU-0060 Ngari Capes Marine Park → polygon "South West"
  - AU-0066 Mount Manning - Helena And Aurora Ranges Conservation Park → polygon "South West"
  - AU-0082 Marmion Marine Park → polygon "South West"
  - AU-0093 Lalang-garram / Camden Sound Marine Park → polygon "Kimberley"
  - AU-0099 Wunaamin Conservation Park → polygon "Kimberley"
  - AU-0106 Jurien Bay Marine Park → polygon "South West"
  - AU-0126 Geikie Gorge National Park → polygon "Kimberley"
  - AU-0127 Geikie Gorge Conservation Park → polygon "Kimberley"
  - AU-0135 Eighty Mile Beach Marine Park → polygon "Kimberley"
  - AU-0162 Brooking Gorge Conservation Park → polygon "Kimberley"
  - AU-0181 You Yangs Regional Park → polygon "Victoria"
  - AU-0184 Yarrawonga Regional Park → polygon "New South Wales"
  - AU-0187 Yaringa Marine National Park → polygon "Victoria"
  - AU-0196 Woowookarung Regional Park → polygon "Victoria"
  - AU-0197 Wonthaggi Heathlands Nature Conservation Reserve → polygon "Victoria"
  - AU-0199 Wodonga Regional Park → polygon "Victoria"
  - AU-0216 Wandong Regional Park → polygon "Victoria"

### SLIP_Public_Services/Boundaries_WFS  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Boundaries_WFS/MapServer/0
- WHY: NOT A PARK LAYER (coverage): closes 60 but only 0 by name (READY needs 3+ name matches and 25%+ of the closes)
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- terms: NON-COMMERCIAL · source item page · "sing this data, you agree to only use this data for your personal and non-commercial use. You are not permitted to, in any form, reproduce, distribute, commercialise or creat" · item https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Boundaries_WFS/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field name · 18 records · sample ACT and Jervis Bay / Central Desert / Geraldton
- closes: 60 of 60 tested missing parks (by name 0, pin only 60; 2871 of the area's 2871 missing parks lie in the layer's extent)
  - AU-0002 Willis Island National Park → polygon "Cape York Region"
  - AU-0004 Yawuru Birragun Conservation Park → polygon "Kimberley"
  - AU-0027 Tunnel Creek National Park → polygon "Kimberley"
  - AU-0034 Swan Estuary Marine Park → polygon "South West"
  - AU-0040 Shoalwater Islands Marine Park → polygon "South West"
  - AU-0042 Shark Bay Marine Park → polygon "Geraldton"
  - AU-0046 Rowley Shoals Marine Park → polygon "Kimberley"
  - AU-0058 Ningaloo Marine Park → polygon "Geraldton"
  - AU-0060 Ngari Capes Marine Park → polygon "South West"
  - AU-0066 Mount Manning - Helena And Aurora Ranges Conservation Park → polygon "South West"
  - AU-0082 Marmion Marine Park → polygon "South West"
  - AU-0093 Lalang-garram / Camden Sound Marine Park → polygon "Kimberley"
  - AU-0099 Wunaamin Conservation Park → polygon "Kimberley"
  - AU-0106 Jurien Bay Marine Park → polygon "South West"
  - AU-0126 Geikie Gorge National Park → polygon "Kimberley"
  - AU-0127 Geikie Gorge Conservation Park → polygon "Kimberley"
  - AU-0135 Eighty Mile Beach Marine Park → polygon "Kimberley"
  - AU-0162 Brooking Gorge Conservation Park → polygon "Kimberley"
  - AU-0181 You Yangs Regional Park → polygon "Victoria"
  - AU-0184 Yarrawonga Regional Park → polygon "New South Wales"
  - AU-0187 Yaringa Marine National Park → polygon "Victoria"
  - AU-0196 Woowookarung Regional Park → polygon "Victoria"
  - AU-0197 Wonthaggi Heathlands Nature Conservation Reserve → polygon "Victoria"
  - AU-0199 Wodonga Regional Park → polygon "Victoria"
  - AU-0216 Wandong Regional Park → polygon "Victoria"

### Public/NaturalEnvironment  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/NaturalEnvironment/MapServer/4
- WHY: NOT A PARK LAYER (coverage): closes 24 but only 2 by name (READY needs 3+ name matches and 25%+ of the closes)
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/NaturalEnvironment/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field NAME · 138 records · sample Patriarch / Sellars Lagoon / Yarra
- closes: 24 of 57 tested missing parks (by name 2, pin only 22; 57 of the area's 2871 missing parks lie in the layer's extent)
  - AU-11291 Great Lake Water Management Area → polygon "Tamar"
  - AU-11292 Arthurs Lake - Water Management Area → polygon "Tamar"
  - AU-11294 Lake Sorell - Water Management Area → polygon "Derwent"
  - AU-11295 Lake Crescent - Water Management Area → polygon "Derwent"
  - AU-11296 Curries River Reservoir - Water Management Area → polygon "Curries"
  - AU-11297 Brandy Pond - Water Management Area → polygon "Tamar"
  - AU-11298 Bruins Pond - Water Management Area → polygon "Tamar"
  - AU-11299 Four Springs Lake - Water Management Area → polygon "Tamar"
  - AU-11300 Brushy Lagoon - Water Management Area → polygon "Tamar"
  - AU-11301 Lake Trevallyn - Water Management Area → polygon "Tamar"
  - AU-11302 Risdon Brook Reservoir - Water Management Area → polygon "Derwent"
  - AU-11303 Waterworks Reservoirs - Water Management Area → polygon "Derwent"
  - AU-11305 Gordons Reservoir Water Management Area → polygon "Pittwater"
  - AU-11306 Lake Pedder - Water Management Area → polygon "Gordon"
  - AU-11307 Lake Gordon Water Management Area → polygon "Gordon"
  - AU-11308 Tooms Lake - Water Management Area → polygon "Tamar"
  - AU-11309 Lake Leake - Water Management Area → polygon "Tamar"
  - AU-11310 Craigbourne Lake Water Management Area → polygon "Pittwater"
  - AU-11311 Woods Lake Water Management Area → polygon "Tamar"
  - AU-11312 Pet Dam - Water Management Area → polygon "Emu"
  - AU-8811 Bellerive Beach - State Beach → polygon "Derwent"
  - AU-8860 Long Beach - State Beach → polygon "Derwent"
  - AU-8864 Flat Rock Beach - State Beach → polygon "Derwent"
  - AU-8929 ANZAC Park → polygon "Derwent"

### Public/NaturalEnvironment  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/NaturalEnvironment/MapServer/5
- WHY: closes only 1 park(s) by name (READY needs 3+ name matches): a park layer, but too little to gain yet
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/NaturalEnvironment/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field NAME · 192 records · sample Pats / Seal / Chew Tobacco Creek
- closes: 1 of 3 tested missing parks (by name 1, pin only 0; 57 of the area's 2871 missing parks lie in the layer's extent)
  - AU-11291 Great Lake Water Management Area → polygon "Great Lake"

### Public/OpenDataWFS  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/OpenDataWFS/MapServer/2
- WHY: NOT A PARK LAYER (coverage): closes 1 but only 0 by name (READY needs 3+ name matches and 25%+ of the closes)
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST &#169 State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/OpenDataWFS/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field O_NAME · 57546 records · sample Landslide Hazard Area / Landslide Hazard Area / Landslide Hazard Area
- closes: 1 of 46 tested missing parks (by name 0, pin only 1; 46 of the area's 2871 missing parks lie in the layer's extent)
  - AU-8859 Kingston Beach - State Beach → polygon "Heritage Precinct"

### Public/PWSPublic  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/PWSPublic/MapServer/0
- WHY: NOT A PARK LAYER (coverage): closes 1 but only 0 by name (READY needs 3+ name matches and 25%+ of the closes)
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/PWSPublic/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field SITE_NAME · 29 records · sample Leven FC / Lake St Clair FC / Overland Track FC
- closes: 1 of 60 tested missing parks (by name 0, pin only 1; 515 of the area's 2871 missing parks lie in the layer's extent)
  - AU-0579 Kent Group National Park → polygon "Flinders Island FC"

### Nevada State Parks boundaries (Division of State Parks, VS Boundary Map)  ·  US-NV  ·  from chat 9
- url: https://services7.arcgis.com/5hLFVlePaucIMGhw/arcgis/rest/services/VS_Boundary_Map_2_WFL1/FeatureServer/2
- WHY: already read as sgnvc: nothing new to take
- publisher: Nevada Division of State Parks (AGOL org owner NDSP_1PARK; copyright Nevada Division of State Lands) → official (government words: Division)
- terms: CREDIT · source item page · "State of Nevada Department of Conservation and National Resrouces Nevada Division of State Lands" · item https://www.arcgis.com/home/item.html?id=e13c696359584dac85377bde0709bb6e · owner NDSP_1PARK · org Nevada Division of State Parks
- facts: arcgis-layer · esriGeometryPolygon · name field LandName · 1 records · last edit 2026-10-02 · sample Lake Tahoe State Park (Van Sickle Unit/AmackerSchultz)
- overlap: already read as sgnvc
- closes: not probed
- TEST: ok

### Montana FWP state parks  ·  US-MT  ·  from chat 9
- url: https://services3.arcgis.com/Cdxz8r11hT0MGzg1/arcgis/rest/services/FWPLND_STATEPARKS/FeatureServer/0
- WHY: already read as sgmta: nothing new to take
- publisher: Montana Fish, Wildlife & Parks → official (government words: State Parks)
- terms: CREDIT · source item page · "usability of this data for their purposes. This data set is provided "as is" without warranty of any kind. Montana Fish, Wildlife & Parks (FWP) makes no representati" · item https://www.arcgis.com/home/item.html?id=c5b81de66c784da18e75daf96dea3db4 · owner MtFishWildlifeParks
- facts: arcgis-layer · esriGeometryPolygon · name field NAME · 55 records · last edit 2026-09-07 · sample Thompson Chain-of-Lakes / Finley Point / Big Arm
- overlap: already read as sgmta
- closes: not probed
- TEST: ok

### Doorstep Greens (England) polygons  ·  GB  ·  from harvester
- url: https://services.arcgis.com/JJzESW51TqeY9uat/arcgis/rest/services/Doorstep_Greens_Polygons/FeatureServer/0
- WHY: official and usable, but it closes none of the area's missing parks (nothing to gain yet)
- publisher: Defra group ArcGIS Online organisation → official (government words: Defra)
- terms: OPEN · source item page · "c access constraints to this data. Use of this data is subject to the Open Government Licence - https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3 © Natural Eng" · item https://www.arcgis.com/home/item.html?id=673be92a820c48c88ff36e6c2508ba98 · owner Opendata_NE · org Defra group ArcGIS Online organisation
- facts: arcgis-layer · esriGeometryPolygon · name field NAME · 192 records · last edit 2024-02-05 · sample Cookley / Coronation Park / Cumberland Market
- closes: 0 of 60 tested missing parks (by name 0, pin only 0; 3357 of the area's 3357 missing parks lie in the layer's extent)
- TEST: ok

### Millennium Greens (England) polygons  ·  GB  ·  from harvester
- url: https://services.arcgis.com/JJzESW51TqeY9uat/arcgis/rest/services/Millennium_Greens_England_Polygons/FeatureServer/0
- WHY: official and usable, but it closes none of the area's missing parks (nothing to gain yet)
- publisher: Defra group ArcGIS Online organisation → official (government words: Defra)
- terms: OPEN · source item page · "c access constraints to this data. Use of this data is subject to the Open Government Licence - https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/ © Natural En" · item https://www.arcgis.com/home/item.html?id=73247b05a5054fe6b04dcc6b39fd89f2 · owner Opendata_NE · org Defra group ArcGIS Online organisation
- facts: arcgis-layer · esriGeometryPolygon · name field NAME · 255 records · last edit 2018-07-05 · sample Withnell Fold / Woodcote / Woodcote
- closes: 0 of 60 tested missing parks (by name 0, pin only 0; 3357 of the area's 3357 missing parks lie in the layer's extent)
- TEST: ok

### NIAA_Administrative_Boundaries_2020  ·  AU  ·  from harvester
- url: https://services9.arcgis.com/EPcAWuPcSWtfB9jL/arcgis/rest/services/NIAA_Administrative_Boundaries_2020/FeatureServer/0
- WHY: no name field: an outline needs a name to match a park
- publisher: National Indigenous Australians Agency → official (government words: Agency)
- terms: NON-COMMERCIAL · source item page · "Licence: Creative Commons - Attribution-NonCommercial 4.0 International Access rights: Open Security classification: OFFICIAL National Indigeno" · item https://www.arcgis.com/home/item.html?id=1a3b79f01c924a689ee2ec9bf5500ee0 · owner indigenous_aus · org National Indigenous Australians Agency
- facts: arcgis-layer · esriGeometryPolygon · 44 records · last edit 2026-10-21
- closes: not probed

### NIAA_Administrative_Boundaries_2020  ·  AU  ·  from harvester
- url: https://services9.arcgis.com/EPcAWuPcSWtfB9jL/arcgis/rest/services/NIAA_Administrative_Boundaries_2020/FeatureServer/1
- WHY: no name field: an outline needs a name to match a park
- publisher: National Indigenous Australians Agency → official (government words: Agency)
- terms: NON-COMMERCIAL · source item page · "Licence: Creative Commons - Attribution-NonCommercial 4.0 International Access rights: Open Security classification: OFFICIAL National Indigeno" · item https://www.arcgis.com/home/item.html?id=1a3b79f01c924a689ee2ec9bf5500ee0 · owner indigenous_aus · org National Indigenous Australians Agency
- facts: arcgis-layer · esriGeometryPolygon · 44 records · last edit 2026-10-21
- closes: not probed

### NIAA_Administrative_Boundaries_2020  ·  AU  ·  from harvester
- url: https://services9.arcgis.com/EPcAWuPcSWtfB9jL/arcgis/rest/services/NIAA_Administrative_Boundaries_2020/FeatureServer/2
- WHY: no name field: an outline needs a name to match a park
- publisher: National Indigenous Australians Agency → official (government words: Agency)
- terms: NON-COMMERCIAL · source item page · "Licence: Creative Commons - Attribution-NonCommercial 4.0 International Access rights: Open Security classification: OFFICIAL National Indigeno" · item https://www.arcgis.com/home/item.html?id=1a3b79f01c924a689ee2ec9bf5500ee0 · owner indigenous_aus · org National Indigenous Australians Agency
- facts: arcgis-layer · esriGeometryPolygon · 44 records · last edit 2026-10-21
- closes: not probed

### NIAA_Administrative_Boundaries_2020  ·  AU  ·  from harvester
- url: https://services9.arcgis.com/EPcAWuPcSWtfB9jL/arcgis/rest/services/NIAA_Administrative_Boundaries_2020/FeatureServer/3
- WHY: no name field: an outline needs a name to match a park
- publisher: National Indigenous Australians Agency → official (government words: Agency)
- terms: NON-COMMERCIAL · source item page · "Licence: Creative Commons - Attribution-NonCommercial 4.0 International Access rights: Open Security classification: OFFICIAL National Indigeno" · item https://www.arcgis.com/home/item.html?id=1a3b79f01c924a689ee2ec9bf5500ee0 · owner indigenous_aus · org National Indigenous Australians Agency
- facts: arcgis-layer · esriGeometryPolygon · 11 records · last edit 2026-10-21
- closes: not probed

### NIAA_Administrative_Boundaries_2020  ·  AU  ·  from harvester
- url: https://services9.arcgis.com/EPcAWuPcSWtfB9jL/arcgis/rest/services/NIAA_Administrative_Boundaries_2020/FeatureServer/4
- WHY: no name field: an outline needs a name to match a park
- publisher: National Indigenous Australians Agency → official (government words: Agency)
- terms: NON-COMMERCIAL · source item page · "Licence: Creative Commons - Attribution-NonCommercial 4.0 International Access rights: Open Security classification: OFFICIAL National Indigeno" · item https://www.arcgis.com/home/item.html?id=1a3b79f01c924a689ee2ec9bf5500ee0 · owner indigenous_aus · org National Indigenous Australians Agency
- facts: arcgis-layer · esriGeometryPolygon · 11 records · last edit 2026-10-21
- closes: not probed

### NIAA_Administrative_Boundaries_2020  ·  AU  ·  from harvester
- url: https://services9.arcgis.com/EPcAWuPcSWtfB9jL/arcgis/rest/services/NIAA_Administrative_Boundaries_2020/FeatureServer/5
- WHY: no name field: an outline needs a name to match a park
- publisher: National Indigenous Australians Agency → official (government words: Agency)
- terms: NON-COMMERCIAL · source item page · "Licence: Creative Commons - Attribution-NonCommercial 4.0 International Access rights: Open Security classification: OFFICIAL National Indigeno" · item https://www.arcgis.com/home/item.html?id=1a3b79f01c924a689ee2ec9bf5500ee0 · owner indigenous_aus · org National Indigenous Australians Agency
- facts: arcgis-layer · esriGeometryPolygon · 11 records · last edit 2026-10-21
- closes: not probed

### NIAA_Administrative_Boundaries_2020  ·  AU  ·  from harvester
- url: https://services9.arcgis.com/EPcAWuPcSWtfB9jL/arcgis/rest/services/NIAA_Administrative_Boundaries_2020/FeatureServer/6
- WHY: no name field: an outline needs a name to match a park
- publisher: National Indigenous Australians Agency → official (government words: Agency)
- terms: NON-COMMERCIAL · source item page · "Licence: Creative Commons - Attribution-NonCommercial 4.0 International Access rights: Open Security classification: OFFICIAL National Indigeno" · item https://www.arcgis.com/home/item.html?id=1a3b79f01c924a689ee2ec9bf5500ee0 · owner indigenous_aus · org National Indigenous Australians Agency
- facts: arcgis-layer · esriGeometryPolygon · 11 records · last edit 2026-10-21
- closes: not probed

### Landgate_Public_Maps/Map_of_Bush_Fire_Prone_Areas_3  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/Landgate_Public_Maps/Map_of_Bush_Fire_Prone_Areas_3/MapServer/6
- WHY: no name field: an outline needs a name to match a park
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- terms: CREDIT · source item page · "Landgate/SLIP/OBRM Landgate/SLIP/OBRM" · item https://public-services.slip.wa.gov.au/public/rest/services/Landgate_Public_Maps/Map_of_Bush_Fire_Prone_Areas_3/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · 1569895 records
- closes: not probed

### Landgate_Public_Maps/Map_of_Bush_Fire_Prone_Areas_3  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/Landgate_Public_Maps/Map_of_Bush_Fire_Prone_Areas_3/MapServer/11
- WHY: no name field: an outline needs a name to match a park
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- terms: CREDIT · source item page · "Landgate/SLIP/OBRM Landgate/SLIP/OBRM" · item https://public-services.slip.wa.gov.au/public/rest/services/Landgate_Public_Maps/Map_of_Bush_Fire_Prone_Areas_3/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · 148 records
- closes: not probed

### Landgate_Public_Maps/Marine_Map_WA_3  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/Landgate_Public_Maps/Marine_Map_WA_3/MapServer/2
- WHY: official and usable, but it closes none of the area's missing parks (nothing to gain yet)
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- terms: CREDIT · source item page · "WALIS WALIS" · item https://public-services.slip.wa.gov.au/public/rest/services/Landgate_Public_Maps/Marine_Map_WA_3/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field name · 32 records · sample Albany / Barker Bay Albany / Batavia NHL
- closes: 0 of 60 tested missing parks (by name 0, pin only 0; 2871 of the area's 2871 missing parks lie in the layer's extent)

### Landgate_Public_Maps/Marine_Map_WA_3  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/Landgate_Public_Maps/Marine_Map_WA_3/MapServer/3
- WHY: official and usable, but it closes none of the area's missing parks (nothing to gain yet)
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- terms: CREDIT · source item page · "WALIS WALIS" · item https://public-services.slip.wa.gov.au/public/rest/services/Landgate_Public_Maps/Marine_Map_WA_3/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field name · 18 records · sample PORT OF BALLA BALLA / VARANUS ISLAND PORT AUTHORITY / WYNDHAM PORT AUTHORITY
- closes: 0 of 2 tested missing parks (by name 0, pin only 0; 2871 of the area's 2871 missing parks lie in the layer's extent)

### Public/ABS_2011  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/ABS_2011/MapServer/0
- WHY: NOT A PARK LAYER (coverage: parcels / census / index / planning / fire): it covers the whole land, so every pin falls inside (chat 11, Oct 29)
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/ABS_2011/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field SA4_NAME · 4 records · sample Hobart / Launceston and North East / South East
- closes: not probed

### Public/ABS_2011  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/ABS_2011/MapServer/1
- WHY: NOT A PARK LAYER (coverage: parcels / census / index / planning / fire): it covers the whole land, so every pin falls inside (chat 11, Oct 29)
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/ABS_2011/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field SA3_NAME · 15 records · sample Brighton / Hobart - North East / Hobart - North West
- closes: not probed

### Public/ABS_2011  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/ABS_2011/MapServer/2
- WHY: NOT A PARK LAYER (coverage: parcels / census / index / planning / fire): it covers the whole land, so every pin falls inside (chat 11, Oct 29)
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/ABS_2011/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field SA2_NAME · 98 records · sample Bridgewater - Gagebrook / Brighton - Pontville / Old Beach - Otago
- closes: not probed

### Public/ABS_2011  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/ABS_2011/MapServer/3
- WHY: no name field: an outline needs a name to match a park
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/ABS_2011/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · 1445 records
- closes: not probed

### Public/ABS_2011  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/ABS_2011/MapServer/4
- WHY: NOT A PARK LAYER (coverage: parcels / census / index / planning / fire): it covers the whole land, so every pin falls inside (chat 11, Oct 29)
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/ABS_2011/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field SA4_NAME · 4 records · sample Hobart / Launceston and North East / South East
- closes: not probed

### Public/ABS_2011  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/ABS_2011/MapServer/5
- WHY: NOT A PARK LAYER (coverage: parcels / census / index / planning / fire): it covers the whole land, so every pin falls inside (chat 11, Oct 29)
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/ABS_2011/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field SA3_NAME · 15 records · sample Brighton / Hobart - North East / Hobart - North West
- closes: not probed

### Public/ABS_2011  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/ABS_2011/MapServer/6
- WHY: NOT A PARK LAYER (coverage: parcels / census / index / planning / fire): it covers the whole land, so every pin falls inside (chat 11, Oct 29)
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/ABS_2011/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field SA2_NAME · 98 records · sample Bridgewater - Gagebrook / Brighton - Pontville / Old Beach - Otago
- closes: not probed

### Public/ABS_2011  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/ABS_2011/MapServer/7
- WHY: no name field: an outline needs a name to match a park
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/ABS_2011/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · 1445 records
- closes: not probed

### Public/ABS_2016  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/ABS_2016/MapServer/0
- WHY: NOT A PARK LAYER (coverage: parcels / census / index / planning / fire): it covers the whole land, so every pin falls inside (chat 11, Oct 29)
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/ABS_2016/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field SA4_NAME16 · 4 records · sample Hobart / Launceston and North East / South East
- closes: not probed

### Public/ABS_2016  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/ABS_2016/MapServer/1
- WHY: NOT A PARK LAYER (coverage: parcels / census / index / planning / fire): it covers the whole land, so every pin falls inside (chat 11, Oct 29)
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/ABS_2016/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field SA3_NAME16 · 15 records · sample Brighton / Hobart - North East / Hobart - North West
- closes: not probed

### Public/ABS_2016  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/ABS_2016/MapServer/2
- WHY: NOT A PARK LAYER (coverage: parcels / census / index / planning / fire): it covers the whole land, so every pin falls inside (chat 11, Oct 29)
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/ABS_2016/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field SA2_NAME16 · 99 records · sample Bridgewater - Gagebrook / Brighton - Pontville / Old Beach - Otago
- closes: not probed

### Public/ABS_2016  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/ABS_2016/MapServer/3
- WHY: NOT A PARK LAYER (coverage: parcels / census / index / planning / fire): it covers the whole land, so every pin falls inside (chat 11, Oct 29)
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/ABS_2016/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field SA2_NAME16 · 1459 records · sample Bridgewater - Gagebrook / Bridgewater - Gagebrook / Bridgewater - Gagebrook
- closes: not probed

### Public/ABS_2016  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/ABS_2016/MapServer/4
- WHY: NOT A PARK LAYER (coverage: parcels / census / index / planning / fire): it covers the whole land, so every pin falls inside (chat 11, Oct 29)
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/ABS_2016/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field SA4_NAME16 · 4 records · sample Hobart / Launceston and North East / South East
- closes: not probed

### Public/ABS_2016  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/ABS_2016/MapServer/5
- WHY: NOT A PARK LAYER (coverage: parcels / census / index / planning / fire): it covers the whole land, so every pin falls inside (chat 11, Oct 29)
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/ABS_2016/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field SA3_NAME16 · 15 records · sample Brighton / Hobart - North East / Hobart - North West
- closes: not probed

### Public/ABS_2016  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/ABS_2016/MapServer/6
- WHY: NOT A PARK LAYER (coverage: parcels / census / index / planning / fire): it covers the whole land, so every pin falls inside (chat 11, Oct 29)
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/ABS_2016/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field SA2_NAME16 · 99 records · sample Bridgewater - Gagebrook / Brighton - Pontville / Old Beach - Otago
- closes: not probed

### Public/ABS_2016  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/ABS_2016/MapServer/7
- WHY: NOT A PARK LAYER (coverage: parcels / census / index / planning / fire): it covers the whole land, so every pin falls inside (chat 11, Oct 29)
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/ABS_2016/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field SA2_NAME16 · 1459 records · sample Bridgewater - Gagebrook / Bridgewater - Gagebrook / Bridgewater - Gagebrook
- closes: not probed

### Public/CadastreAndAdministrative  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/CadastreAndAdministrative/MapServer/1
- WHY: NOT A PARK LAYER (coverage: parcels / census / index / planning / fire): it covers the whole land, so every pin falls inside (chat 11, Oct 29)
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST &copy; State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/CadastreAndAdministrative/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field FEAT_NAME · 9111 records · sample None / None / None
- closes: not probed

### Public/CadastreAndAdministrative  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/CadastreAndAdministrative/MapServer/2
- WHY: no name field: an outline needs a name to match a park
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST &copy; State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/CadastreAndAdministrative/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · 1250 records
- closes: not probed

### Public/CadastreAndAdministrative  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/CadastreAndAdministrative/MapServer/3
- WHY: no name field: an outline needs a name to match a park
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST &copy; State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/CadastreAndAdministrative/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · 4393 records
- closes: not probed

### Public/CadastreAndAdministrative  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/CadastreAndAdministrative/MapServer/4
- WHY: NOT A PARK LAYER (coverage: parcels / census / index / planning / fire): it covers the whole land, so every pin falls inside (chat 11, Oct 29)
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST &copy; State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/CadastreAndAdministrative/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field NAME · 29 records · sample Burnie / Huon Valley / Flinders
- closes: not probed

### Public/CadastreAndAdministrative  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/CadastreAndAdministrative/MapServer/5
- WHY: NOT A PARK LAYER (coverage: parcels / census / index / planning / fire): it covers the whole land, so every pin falls inside (chat 11, Oct 29)
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST &copy; State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/CadastreAndAdministrative/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field NAME · 6033 records · sample None / None / None
- closes: not probed

### Public/CadastreAndAdministrative  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/CadastreAndAdministrative/MapServer/96
- WHY: NOT A PARK LAYER (coverage: parcels / census / index / planning / fire): it covers the whole land, so every pin falls inside (chat 11, Oct 29)
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST &copy; State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/CadastreAndAdministrative/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field NAME · 1243 records · sample None / None / None
- closes: not probed

### Public/CadastreAndAdministrative  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/CadastreAndAdministrative/MapServer/6
- WHY: NOT A PARK LAYER (coverage: parcels / census / index / planning / fire): it covers the whole land, so every pin falls inside (chat 11, Oct 29)
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST &copy; State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/CadastreAndAdministrative/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field FEAT_NAME · 39951 records · sample None / None / None
- closes: not probed

### Public/CadastreAndAdministrative  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/CadastreAndAdministrative/MapServer/7
- WHY: NOT A PARK LAYER (coverage: parcels / census / index / planning / fire): it covers the whole land, so every pin falls inside (chat 11, Oct 29)
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST &copy; State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/CadastreAndAdministrative/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field NAME · 777 records · sample Mount Stuart / Fitzgerald / Dover
- closes: not probed

### Public/CadastreAndAdministrativeV2  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/CadastreAndAdministrativeV2/MapServer/2
- WHY: no name field: an outline needs a name to match a park
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: NOTHING STATED · source item page · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/CadastreAndAdministrativeV2/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · 8319 records
- closes: not probed

### Public/CadastreAndAdministrativeV2  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/CadastreAndAdministrativeV2/MapServer/3
- WHY: no name field: an outline needs a name to match a park
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: NOTHING STATED · source item page · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/CadastreAndAdministrativeV2/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · 9443 records
- closes: not probed

### Public/CadastreAndAdministrativeV2  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/CadastreAndAdministrativeV2/MapServer/4
- WHY: no name field: an outline needs a name to match a park
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: NOTHING STATED · source item page · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/CadastreAndAdministrativeV2/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · 172 records
- closes: not probed

### Public/CadastreAndAdministrativeV2  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/CadastreAndAdministrativeV2/MapServer/6
- WHY: no name field: an outline needs a name to match a park
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: NOTHING STATED · source item page · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/CadastreAndAdministrativeV2/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · 5849 records
- closes: not probed

### Public/CadastreAndAdministrativeV2  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/CadastreAndAdministrativeV2/MapServer/15
- WHY: no name field: an outline needs a name to match a park
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: NOTHING STATED · source item page · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/CadastreAndAdministrativeV2/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · 117 records
- closes: not probed

### Public/EmergencyManagementPublic  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/EmergencyManagementPublic/MapServer/1
- WHY: NOT A PARK LAYER (coverage: parcels / census / index / planning / fire): it covers the whole land, so every pin falls inside (chat 11, Oct 29)
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST © State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/EmergencyManagementPublic/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field FIRE_NAME · 10427 records · sample Bushfire - 8/12/1988 / Cambridge Street Reserve / Cambridge Street Reserve
- closes: not probed

### Public/EmergencyManagementPublic  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/EmergencyManagementPublic/MapServer/2
- WHY: NOT A PARK LAYER (coverage: parcels / census / index / planning / fire): it covers the whole land, so every pin falls inside (chat 11, Oct 29)
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST © State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/EmergencyManagementPublic/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field FIRE_NAME · 9562 records · sample None / BS122H Bark Heap / Native Plains Road
- closes: not probed

### Public/EmergencyManagementPublic  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/EmergencyManagementPublic/MapServer/8
- WHY: no name field: an outline needs a name to match a park
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST © State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/EmergencyManagementPublic/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · 802 records
- closes: not probed

### Public/EmergencyManagementPublic  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/EmergencyManagementPublic/MapServer/9
- WHY: no name field: an outline needs a name to match a park
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST © State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/EmergencyManagementPublic/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · 3 records
- closes: not probed

### Public/EmergencyManagementPublic  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/EmergencyManagementPublic/MapServer/13
- WHY: NOT A PARK LAYER (coverage: parcels / census / index / planning / fire): it covers the whole land, so every pin falls inside (chat 11, Oct 29)
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST © State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/EmergencyManagementPublic/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field FIRE_NAME · 1994 records · sample None / Enterprise FT - LS16 Part-LS17 / None
- closes: not probed

### Public/EmergencyManagementPublic  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/EmergencyManagementPublic/MapServer/14
- WHY: NOT A PARK LAYER (coverage: parcels / census / index / planning / fire): it covers the whole land, so every pin falls inside (chat 11, Oct 29)
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST © State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/EmergencyManagementPublic/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field FIRE_NAME · 4486 records · sample None / Enterprise FT - LS16 Part-LS17 / Picketts Creek - Holloway
- closes: not probed

### Public/EmergencyManagementPublic  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/EmergencyManagementPublic/MapServer/15
- WHY: no name field: an outline needs a name to match a park
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST © State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/EmergencyManagementPublic/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · 7598 records
- closes: not probed

### Public/EmergencyManagementPublic  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/EmergencyManagementPublic/MapServer/21
- WHY: NOT A PARK LAYER (coverage: parcels / census / index / planning / fire): it covers the whole land, so every pin falls inside (chat 11, Oct 29)
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST © State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/EmergencyManagementPublic/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field NAME · 10 records · sample Midlands / West Coast / Central North
- closes: not probed

### Public/Indexes  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/Indexes/MapServer/0
- WHY: NOT A PARK LAYER (coverage: parcels / census / index / planning / fire): it covers the whole land, so every pin falls inside (chat 11, Oct 29)
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST &#169 State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/Indexes/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field MAP_NAME · 455 records · sample HANLETH / ROGER / ALBINA
- closes: not probed

### Public/Indexes  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/Indexes/MapServer/65
- WHY: NOT A PARK LAYER (coverage: parcels / census / index / planning / fire): it covers the whole land, so every pin falls inside (chat 11, Oct 29)
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST &#169 State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/Indexes/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field MAP_NAME · 95 records · sample AVOCA / LAKE LEAKE / SWANSTON
- closes: not probed

### Public/Indexes  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/Indexes/MapServer/1
- WHY: NOT A PARK LAYER (coverage: parcels / census / index / planning / fire): it covers the whole land, so every pin falls inside (chat 11, Oct 29)
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST &#169 State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/Indexes/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field MAP_NAME · 49 records · sample NIVE / FRANKLIN / ARTHUR RIVER
- closes: not probed

### Public/Indexes  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/Indexes/MapServer/2
- WHY: NOT A PARK LAYER (coverage: parcels / census / index / planning / fire): it covers the whole land, so every pin falls inside (chat 11, Oct 29)
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST &#169 State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/Indexes/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field MAP_NAME · 6 records · sample NORTH WEST / SOUTH WEST / NORTH EAST
- closes: not probed

### Public/Indexes  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/Indexes/MapServer/3
- WHY: NOT A PARK LAYER (coverage: parcels / census / index / planning / fire): it covers the whole land, so every pin falls inside (chat 11, Oct 29)
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST &#169 State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/Indexes/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field MAP_NAME · 275 records · sample Carrick / Latrobe / Bridgewater
- closes: not probed

### Public/Indexes  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/Indexes/MapServer/4
- WHY: NOT A PARK LAYER (coverage: parcels / census / index / planning / fire): it covers the whole land, so every pin falls inside (chat 11, Oct 29)
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST &#169 State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/Indexes/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field MAP_NAME · 18 records · sample PENINSULA WALKS INSET 3 / PENINSULA WALKS INSET 4 / PENINSULA WALKS
- closes: not probed

### Public/Indexes  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/Indexes/MapServer/12
- WHY: NOT A PARK LAYER (coverage: parcels / census / index / planning / fire): it covers the whole land, so every pin falls inside (chat 11, Oct 29)
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/Indexes/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field PROJ_NAME · 433 records · sample Bagdad Mangalore 10cm 2011 / Bothwell 10cm 2011 / Buckland 10cm 2011
- closes: not probed

### Public/Indexes  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/Indexes/MapServer/13
- WHY: no name field: an outline needs a name to match a park
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/Indexes/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · 33665 records
- closes: not probed

### Public/MarineAndCoastal  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/MarineAndCoastal/MapServer/87
- WHY: no name field: an outline needs a name to match a park
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/MarineAndCoastal/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · 199 records
- closes: not probed

### Public/MarineAndCoastal  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/MarineAndCoastal/MapServer/89
- WHY: no name field: an outline needs a name to match a park
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/MarineAndCoastal/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · 14 records
- closes: not probed

### Public/MarineAndCoastal  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/MarineAndCoastal/MapServer/92
- WHY: NOT A PARK LAYER (coverage: parcels / census / index / planning / fire): it covers the whole land, so every pin falls inside (chat 11, Oct 29)
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/MarineAndCoastal/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field GA_NAME · 57 records · sample Pitt Water / Pitt Water / Gardners Bay
- closes: not probed

### Public/MarineAndCoastal  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/MarineAndCoastal/MapServer/97
- WHY: no name field: an outline needs a name to match a park
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/MarineAndCoastal/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · 156 records
- closes: not probed

### Public/MarineAndCoastal  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/MarineAndCoastal/MapServer/96
- WHY: no name field: an outline needs a name to match a park
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/MarineAndCoastal/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · 2321 records
- closes: not probed

### Public/MarineAndCoastal  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/MarineAndCoastal/MapServer/99
- WHY: no name field: an outline needs a name to match a park
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/MarineAndCoastal/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · 42 records
- closes: not probed

### Public/MarineAndCoastal  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/MarineAndCoastal/MapServer/1
- WHY: no name field: an outline needs a name to match a park
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/MarineAndCoastal/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · 67 records
- closes: not probed

### Public/MarineAndCoastal  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/MarineAndCoastal/MapServer/2
- WHY: no name field: an outline needs a name to match a park
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/MarineAndCoastal/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · 1911 records
- closes: not probed

### Public/NaturalEnvironment  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/NaturalEnvironment/MapServer/1
- WHY: no name field: an outline needs a name to match a park
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/NaturalEnvironment/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · 126488 records
- closes: not probed

### Public/NaturalEnvironmentV2  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/NaturalEnvironmentV2/MapServer/7
- WHY: no name field: an outline needs a name to match a park
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: NOTHING STATED · source item page · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/NaturalEnvironmentV2/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · 482138 records
- closes: not probed

### Public/NaturalEnvironmentV2  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/NaturalEnvironmentV2/MapServer/8
- WHY: no name field: an outline needs a name to match a park
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: NOTHING STATED · source item page · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/NaturalEnvironmentV2/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · 482138 records
- closes: not probed

### Public/NaturalEnvironmentV2  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/NaturalEnvironmentV2/MapServer/9
- WHY: no name field: an outline needs a name to match a park
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: NOTHING STATED · source item page · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/NaturalEnvironmentV2/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · 482138 records
- closes: not probed

### Public/NaturalEnvironmentV2  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/NaturalEnvironmentV2/MapServer/10
- WHY: no name field: an outline needs a name to match a park
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: NOTHING STATED · source item page · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/NaturalEnvironmentV2/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · 482138 records
- closes: not probed

### Public/OpenDataWFS  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/OpenDataWFS/MapServer/0
- WHY: no name field: an outline needs a name to match a park
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST &#169 State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/OpenDataWFS/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · 721 records
- closes: not probed

### Public/OpenDataWFS  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/OpenDataWFS/MapServer/1
- WHY: no name field: an outline needs a name to match a park
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST &#169 State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/OpenDataWFS/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · 721 records
- closes: not probed

### Public/OpenDataWFS  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/OpenDataWFS/MapServer/4
- WHY: no name field: an outline needs a name to match a park
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST &#169 State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/OpenDataWFS/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · 744 records
- closes: not probed

### Public/OpenDataWFS  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/OpenDataWFS/MapServer/5
- WHY: no name field: an outline needs a name to match a park
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST &#169 State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/OpenDataWFS/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · 3853 records
- closes: not probed

### Public/OpenDataWFS  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/OpenDataWFS/MapServer/6
- WHY: official and usable, but it closes none of the area's missing parks (nothing to gain yet)
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST &#169 State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/OpenDataWFS/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field TILE_NAME · 22 records · sample e557n5239 / e557n5240 / e557n5241
- closes: 0 of 1 tested missing parks (by name 0, pin only 0; 1 of the area's 2871 missing parks lie in the layer's extent)

### Public/OpenDataWFS  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/OpenDataWFS/MapServer/7
- WHY: official and usable, but it closes none of the area's missing parks (nothing to gain yet)
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST &#169 State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/OpenDataWFS/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field TILE_NAME · 557 records · sample filnd_5835561 / filnd_5835562 / filnd_5845560
- closes: 0 of 4 tested missing parks (by name 0, pin only 0; 56 of the area's 2871 missing parks lie in the layer's extent)

### Public/PWSPublic  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/PWSPublic/MapServer/1
- WHY: official and usable, but it closes none of the area's missing parks (nothing to gain yet)
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/PWSPublic/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field SITE_NAME · 4 records · sample Whole State / Whole State / Whole State
- closes: 0 of 2 tested missing parks (by name 0, pin only 0; 515 of the area's 2871 missing parks lie in the layer's extent)

### Public/Planning  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/Planning/MapServer/1
- WHY: NOT A PARK LAYER (coverage: parcels / census / index / planning / fire): it covers the whole land, so every pin falls inside (chat 11, Oct 29)
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST &#169 State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/Planning/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field PROP_NAME · 439979 records · sample None / None / None
- closes: not probed

### Public/Planning  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/Planning/MapServer/67
- WHY: no name field: an outline needs a name to match a park
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/Planning/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · 54264 records
- closes: not probed

### Public/Planning  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/Planning/MapServer/68
- WHY: no name field: an outline needs a name to match a park
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/Planning/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · 48577 records
- closes: not probed

### Public/Planning  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/Planning/MapServer/69
- WHY: no name field: an outline needs a name to match a park
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/Planning/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · 2305 records
- closes: not probed

### Public/Planning  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/Planning/MapServer/70
- WHY: no name field: an outline needs a name to match a park
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/Planning/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · 65603 records
- closes: not probed

### Public/Planning  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/Planning/MapServer/72
- WHY: no name field: an outline needs a name to match a park
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/Planning/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · 405 records
- closes: not probed

### Public/Planning  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/Planning/MapServer/74
- WHY: NOT A PARK LAYER (coverage: parcels / census / index / planning / fire): it covers the whole land, so every pin falls inside (chat 11, Oct 29)
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/Planning/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field ROAD_NAME · 12022 records · sample Bass Highway / Midland Highway / Midland Highway
- closes: not probed

### Public/Planning  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/Planning/MapServer/77
- WHY: no name field: an outline needs a name to match a park
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/Planning/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · 17 records
- closes: not probed

### Public/TopographyAndRelief  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/TopographyAndRelief/MapServer/18
- WHY: official and usable, but it closes none of the area's missing parks (nothing to gain yet)
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST &copy; State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/TopographyAndRelief/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field NAME · 17965 records · sample None / None / None
- closes: 0 of 60 tested missing parks (by name 0, pin only 0; 80 of the area's 2871 missing parks lie in the layer's extent)

### Public/TopographyAndRelief  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/TopographyAndRelief/MapServer/19
- WHY: official and usable, but it closes none of the area's missing parks (nothing to gain yet)
- publisher: services.thelist.tas.gov.au → official (government host services.thelist.tas.gov.au)
- terms: CREDIT · source item page · "the LIST State of Tasmania the LIST &copy; State of Tasmania" · item https://services.thelist.tas.gov.au/arcgis/rest/services/Public/TopographyAndRelief/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field NAME · 432 records · sample None / None / None
- closes: 0 of 2 tested missing parks (by name 0, pin only 0; 80 of the area's 2871 missing parks lie in the layer's extent)

### SLIP_Public_Services/Boundaries  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Boundaries/MapServer/1
- WHY: official and usable, but it closes none of the area's missing parks (nothing to gain yet)
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- terms: NON-COMMERCIAL · source item page · "sing this data, you agree to only use this data for your personal and non-commercial use. You are not permitted to, in any form, reproduce, distribute, commercialise or creat" · item https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Boundaries/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field name · 107 records · sample Ballidu / Beverley / Boyup Brook
- closes: 0 of 2 tested missing parks (by name 0, pin only 0; 2871 of the area's 2871 missing parks lie in the layer's extent)

### SLIP_Public_Services/Boundaries_WFS  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Boundaries_WFS/MapServer/1
- WHY: official and usable, but it closes none of the area's missing parks (nothing to gain yet)
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- terms: NON-COMMERCIAL · source item page · "sing this data, you agree to only use this data for your personal and non-commercial use. You are not permitted to, in any form, reproduce, distribute, commercialise or creat" · item https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Boundaries_WFS/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field name · 107 records · sample Ballidu / Beverley / Boyup Brook
- closes: 0 of 2 tested missing parks (by name 0, pin only 0; 2871 of the area's 2871 missing parks lie in the layer's extent)

### SLIP_Public_Services/Environment  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Environment/MapServer/0
- WHY: no name field: an outline needs a name to match a park
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- terms: OPEN · source item page · "You are provided access to publicly available data on the terms and conditions of SLIP Transaction - Personal Use Licence, unless you a" · item https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Environment/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · 772 records
- closes: not probed

### SLIP_Public_Services/Environment  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Environment/MapServer/1
- WHY: no name field: an outline needs a name to match a park
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- terms: OPEN · source item page · "You are provided access to publicly available data on the terms and conditions of SLIP Transaction - Personal Use Licence, unless you a" · item https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Environment/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · 18 records
- closes: not probed

### SLIP_Public_Services/Environment  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Environment/MapServer/2
- WHY: official and usable, but it closes none of the area's missing parks (nothing to gain yet)
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- terms: NON-COMMERCIAL · source item page · "sing this data, you agree to only use this data for your personal and non-commercial use. You are not permitted to, in any form, reprodu" · item https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Environment/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field name · 6 records · sample Point Quobba Fish Habitat Protection Area / Abrolhos Islands Fish Habitat Protection Area / Cottesloe Reef Fish Habitat Protection Area
- closes: 0 of 60 tested missing parks (by name 0, pin only 0; 2871 of the area's 2871 missing parks lie in the layer's extent)

### SLIP_Public_Services/Environment_WFS  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Environment_WFS/MapServer/0
- WHY: no name field: an outline needs a name to match a park
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- terms: OPEN · source item page · "You are provided access to publicly available data on the terms and conditions of SLIP Transaction - Personal Use Licence, unless you a" · item https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Environment_WFS/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · 772 records
- closes: not probed

### SLIP_Public_Services/Environment_WFS  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Environment_WFS/MapServer/1
- WHY: no name field: an outline needs a name to match a park
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- terms: OPEN · source item page · "You are provided access to publicly available data on the terms and conditions of SLIP Transaction - Personal Use Licence, unless you a" · item https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Environment_WFS/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · 18 records
- closes: not probed

### SLIP_Public_Services/Environment_WFS  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Environment_WFS/MapServer/2
- WHY: official and usable, but it closes none of the area's missing parks (nothing to gain yet)
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- terms: NON-COMMERCIAL · source item page · "sing this data, you agree to only use this data for your personal and non-commercial use. You are not permitted to, in any form, reprodu" · item https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Environment_WFS/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field name · 6 records · sample Point Quobba Fish Habitat Protection Area / Abrolhos Islands Fish Habitat Protection Area / Cottesloe Reef Fish Habitat Protection Area
- closes: 0 of 60 tested missing parks (by name 0, pin only 0; 2871 of the area's 2871 missing parks lie in the layer's extent)

### SLIP_Public_Services/Farming  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Farming/MapServer/0
- WHY: official and usable, but it closes none of the area's missing parks (nothing to gain yet)
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- terms: CREDIT · source item page · "SLIP SLIP" · item https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Farming/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field name · 30445 records · sample NORTHAMPTON / NORTHAMPTON / WYNDHAM-EAST KIMBERLEY
- closes: 0 of 60 tested missing parks (by name 0, pin only 0; 2871 of the area's 2871 missing parks lie in the layer's extent)

### SLIP_Public_Services/Farming  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Farming/MapServer/1
- WHY: no name field: an outline needs a name to match a park
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- terms: CREDIT · source item page · "SLIP SLIP" · item https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Farming/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · 33713 records
- closes: not probed

### SLIP_Public_Services/Farming  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Farming/MapServer/2
- WHY: no name field: an outline needs a name to match a park
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- terms: CREDIT · source item page · "SLIP SLIP" · item https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Farming/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · 39128 records
- closes: not probed

### SLIP_Public_Services/Farming  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Farming/MapServer/3
- WHY: no name field: an outline needs a name to match a park
- publisher: public-services.slip.wa.gov.au → official (government host public-services.slip.wa.gov.au)
- terms: CREDIT · source item page · "SLIP SLIP" · item https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Farming/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon
- closes: not probed

## Known-answer test rows

| row | expect | got | result |
|---|---|---|---|
| Nevada State Parks boundaries (Division of State Parks, VS Boundary Map) | READY or already read | REJECT | ok |
| USACE reservoirs (Army Corps of Engineers) | WATER-ONLY | WATER-ONLY | ok |
| PEI provincial parks (GeoLinc, ENV polygon layer) | ASK-THE-PUBLISHER | ASK-THE-PUBLISHER | ok |
| Czechia natural parks (AOPK CR, gis.nature.cz, Prirodni park) | LIVE-ONLY | LIVE-ONLY | ok |
| Montana FWP state parks | already read | REJECT | ok |
| Doorstep Greens (England) polygons | READY or REJECT | REJECT | ok |
| Millennium Greens (England) polygons | READY or REJECT | REJECT | ok |
| SSSI units (England) | READY or REJECT | READY | ok |
| My favorite camping spots (a hobby map) | REJECT or did-not-open | RETRY | ok |
| Slovenia protected areas (ARSO, INSPIRE PS WFS) | READY (WFS) or did-not-open | RETRY | ok |
| SCDNR managed lands (public viewer) on Clemson's ArcGIS Online account | ASK-THE-PUBLISHER or already read | ASK-THE-PUBLISHER | ok |

GATE=PASS
