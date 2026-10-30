# Layer intake review (2026-10-30)

Every lead in data/intake/queue.json, probed politely (metadata and counts only, never geometry). Chat 9 approves a READY row by setting `approved: true` in ready.json; the nightly key rebuild reads approved rows later. LIVE-ONLY = read live, never stored. ASK = the publisher must be asked (nothing stated, or hosted for an agency). WATER-ONLY = lakes / reservoirs: for the 2-fer owner step only, never a park outline. RETRY = the probe did not open (error, rest, robots, 403): probed again next run, three failures → chat 9 checks the url. Terms are read on the publisher's OWN item page first (the Nevada lesson).

| verdict | rows |
|---|---|
| READY | 2 |
| WATER-ONLY | 9 |
| LIVE-ONLY | 1 |
| ASK-THE-PUBLISHER | 74 |
| RETRY | 90 |
| REJECT | 528 |

## READY (2)

### Local and Regional Greenspaces (bcgw_pub_whse_basemapping layer 39)  ·  CA-BC  ·  from chat 9
- url: https://maps.gov.bc.ca/arcgis/rest/services/whse/bcgw_pub_whse_basemapping/MapServer/39
- WHY: official, credit terms, named polygons; closes 42 (name + pin 39, pin only 3): a pin inside a designation polygon is not a sure match
- publisher: Province of British Columbia (B.C. Map Hub) → official (government host maps.gov.bc.ca)
- terms: CREDIT · source item page · "access information? © 2024 Government of British Columbia" · item https://maps.gov.bc.ca/arcgis/rest/services/whse/bcgw_pub_whse_basemapping/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field PARK_NAME · 9682 records · sample 5th Avenue Park / Terra Nova South Park / Thompson Park
- overlap: same publisher as BC recreatio
- closes: 42 of 60 tested missing parks (by name 39, pin only 3; 128 of the area's 128 missing parks lie in the layer's extent)
  - CA-3178 A.H.P. Matthew Park → polygon "A.H.P. Matthew Park"
  - CA-3180 Allco Park → polygon "Allco Park"
  - CA-3183 Ambleside Park → polygon "Ambleside Park"
  - CA-3200 Barnet Marine Park → polygon "Barnet Marine Park"
  - CA-3258 Bright Angel Regional Park → polygon "Bright Angel Park"
  - CA-3267 Buckingham Park Protected Area → polygon "Buckingham Park"
  - CA-3278 Burnaby Mountain Conservation Area → polygon "Burnaby Mountain Conservation Area"
  - CA-3282 Delta Nature Reserve → polygon "Burns Bog Ecological Conservancy Area"
  - CA-3300 Cariboo Park → polygon "Cariboo Park"
  - CA-3304 Castle Park → polygon "Castle Park"
  - CA-3307 Cedar Creek Park Conservation Area → polygon "Cedar Creek Park"
  - CA-3310 Cates Park → polygon "Cates Park/ Whey-Ah-Wichen"
  - CA-3313 Cedar Greens Park → polygon "Cedar Greens Park"
  - CA-3339 Citadel Heights Park → polygon "Citadel Heights Park"
  - CA-3358 Colony Farm Community Gardens at ƛ̓éxətəm Regional Park → polygon "Colony Farm Regional Park"
  - CA-3359 ƛ̓éxətəm Regional Park → polygon "Colony Farm Regional Park"
  - CA-3376 Coutts Park → polygon "Coutts Park"
  - CA-3394 Dacre Park → polygon "Dacre Park"
  - CA-3407 Deer Lake Park → polygon "Deer Lake Park"
  - CA-3415 Devonian Harbour Park → polygon "Devonian Harbour Park"
  - CA-3422 Discovery Town Park → polygon "Discovery Town Park"
  - CA-3427 Douglas Park → polygon "Douglas Park"
  - CA-3453 Eastern Drive Park → polygon "Eastern Drive Park"
  - CA-3469 Elks Park Protected Area → polygon "Elks Park"
  - CA-3513 Burnaby Fraser Foreshore Park → polygon "Burnaby Fraser Foreshore Park"

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

## WATER-ONLY (9)

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

### Local Authority Districts (May 2021) Boundaries UK BGC  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/ESMARspQHYMw9BZ9/arcgis/rest/services/Local_Authority_Districts_May_2021_UK_BGC_2022/FeatureServer/0
- WHY: water only: for the 2-fer owner step only (lakes / reservoirs / water bodies never go in the key as a park outline); otherwise ASK-THE-PUBLISHER: official and usable, but no missing parks were tested (none listed for the area or no time)
- publisher: ? → official (government words: Authority)
- FLAG: water only: for the 2-fer owner step only
- terms: CREDIT · source item page · "https://www.ons.gov.uk/methodology/geography/licences Office for National Statistics" · item https://www.arcgis.com/home/item.html?id=a3fde13bfea541408f7fa0ef088e7e00 · owner ONSGeography_data · org Office for National Statistics
- facts: arcgis-layer · esriGeometryPolygon · name field LAD21NM · 374 records · last edit 2023-03-21 · sample Hartlepool / Middlesbrough / Redcar and Cleveland
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### Local Authority Districts (May 2022) Boundaries UK BFE (V3)  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/ESMARspQHYMw9BZ9/arcgis/rest/services/Local_Authority_Districts_May_2022_UK_BFE_V3_2022/FeatureServer/0
- WHY: water only: for the 2-fer owner step only (lakes / reservoirs / water bodies never go in the key as a park outline); otherwise ASK-THE-PUBLISHER: official and usable, but no missing parks were tested (none listed for the area or no time)
- publisher: ? → official (government words: Authority)
- FLAG: water only: for the 2-fer owner step only
- terms: CREDIT · source item page · "https://www.ons.gov.uk/methodology/geography/licences Office for National Statistics" · item https://www.arcgis.com/home/item.html?id=196d1a072aaa4882a50be333679d4f63 · owner ONSGeography_data · org Office for National Statistics
- facts: arcgis-layer · esriGeometryPolygon · name field LAD22NM · 374 records · last edit 2023-03-21 · sample Hartlepool / Middlesbrough / Redcar and Cleveland
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### Potomac Heritage National Scenic Trail of Northern Virginia - August 2021 Version  ·    ·  from gis-hunter
- url: https://services5.arcgis.com/6MUPhDX27Ne3DNOw/arcgis/rest/services/Northern_Virginia_Potomac_River_Corridor/FeatureServer/4
- WHY: water only: for the 2-fer owner step only (lakes / reservoirs / water bodies never go in the key as a park outline); otherwise ASK-THE-PUBLISHER: official and usable, but no missing parks were tested (none listed for the area or no time)
- publisher: ? → official (government words: Commission)
- FLAG: water only: for the 2-fer owner step only
- terms: CREDIT · source item page · "Northern Virginia Regional Commission (NVRC) is not liable for any use of or reliance upon this map or data, or any information contained herein. Wh" · item https://www.arcgis.com/home/item.html?id=af7cf26b7be74b57a19fa8174eea6e7b · owner jkaneff_NVRC · org Northern Virginia Regional Commission 
- facts: arcgis-layer · esriGeometryPolygon · name field NAME · 947 records · last edit 2024-06-26 · sample Accotink Stream Valley / African American Heritage / Alabama Drive
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### San Pablo Bay Ridgway's Rail Call Count 200m Buffers  ·    ·  from gis-hunter
- url: https://services.arcgis.com/QVENGdaPbd4LUkLV/arcgis/rest/services/San_Pablo_Bay_Rail_Call_Count_200m_Buffers/FeatureServer/0
- WHY: water only: for the 2-fer owner step only (lakes / reservoirs / water bodies never go in the key as a park outline); otherwise ASK-THE-PUBLISHER: official and usable, but no missing parks were tested (none listed for the area or no time)
- publisher: ? → official (a federal / national agency named)
- FLAG: water only: for the 2-fer owner step only
- terms: CREDIT · source item page · "herein. While the Service makes every reasonable effort to ensure the accuracy and completeness of data provided for distribution, it may not have the necessary accurac" · item https://www.arcgis.com/home/item.html?id=bf50309c8b0146e29b167dcb128bfcc5 · owner madison_pitman@fws.gov_fws · org U.S. Fish & Wildlife Service
- facts: arcgis-layer · esriGeometryPolygon · name field SITENAME · 45 records · last edit 2026-01-08 · sample TOLAY CREEK / TOLAY CREEK / TOLAY CREEK
- overlap: same publisher as sgazd
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### Great Salt Lake Basin  ·    ·  from gis-hunter
- url: https://services.arcgis.com/ZzrwjTRez6FJiOq4/arcgis/rest/services/Great_Salt_Lake_Basin/FeatureServer/2
- WHY: water only: for the 2-fer owner step only (lakes / reservoirs / water bodies never go in the key as a park outline); otherwise ASK-THE-PUBLISHER: official and usable, but no missing parks were tested (none listed for the area or no time)
- publisher: ? → official (government words: DNR)
- FLAG: water only: for the 2-fer owner step only
- terms: OPEN · source item page · "CC BY-SA Disclaimer: For reference use only. Although this product represents the work of natur" · item https://www.arcgis.com/home/item.html?id=ceb4e87f7f664fe8a81e8418cafb226a · owner dnrwres · org Utah DNR Online Maps
- facts: arcgis-layer · esriGeometryPolygon · name field NAME · 5 records · last edit 2025-06-25 · sample JORDAN RIVER / WEBER RIVER / UTAH LAKE
- overlap: same publisher as sguta
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

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

## ASK-THE-PUBLISHER (74)

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

### Centennial Industrial Business Activity  ·    ·  from gis-hunter
- url: https://services7.arcgis.com/S7DHOirgbYgdtrbR/arcgis/rest/services/Centennial_Industrial_Business_Activity/FeatureServer/0
- WHY: official and usable, but no missing parks were tested (none listed for the area or no time)
- publisher: ? → official (government words: District)
- terms: OPEN · source item page · "This work is licensed under a Creative Commons Attribution 4.0 International License Taupō District Council (CC BY 4.0)" · item https://www.arcgis.com/home/item.html?id=4bebb77bbe5a4a52b4ffda07bc9e19eb · owner TaupoDistrictCouncil
- facts: arcgis-layer · esriGeometryPolygon · name field ZoneName · 1 records · last edit 2025-06-03 · sample Heavy industrial zone
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### Fallen Timbers Battlefield  ·    ·  from gis-hunter
- url: https://services2.arcgis.com/i7Ls2H4uQGTYzm5D/arcgis/rest/services/Fallen_Timbers_Battlefield/FeatureServer/2
- WHY: publisher unsure: no government word found, ask who publishes it
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: CREDIT · source item page · "Old Topopgrapher Old Topopgrapher" · item https://www.arcgis.com/home/item.html?id=74707366cc3a4cc589611603da9044ea · owner topographer · org   The Old Topographer
- facts: arcgis-layer · esriGeometryPolygon · name field Name · 4 records · last edit 2016-01-09 · sample Western Confederacy Line & Downed Timbers Area / US Casuatlies & Skirmish Area / 1st & 3rd Sub-Legion Battle Line
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### Fallen Timbers Battlefield  ·    ·  from gis-hunter
- url: https://services2.arcgis.com/i7Ls2H4uQGTYzm5D/arcgis/rest/services/Fallen_Timbers_Battlefield/FeatureServer/3
- WHY: publisher unsure: no government word found, ask who publishes it
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: CREDIT · source item page · "Old Topopgrapher Old Topopgrapher" · item https://www.arcgis.com/home/item.html?id=74707366cc3a4cc589611603da9044ea · owner topographer · org   The Old Topographer
- facts: arcgis-layer · esriGeometryPolygon · name field Name · 1 records · last edit 2023-11-30 · sample Fallen Timbers Battlefield and Fort Miamis NHS
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### Fallen Timbers Battlefield  ·    ·  from gis-hunter
- url: https://services2.arcgis.com/i7Ls2H4uQGTYzm5D/arcgis/rest/services/Fallen_Timbers_Battlefield/FeatureServer/4
- WHY: publisher unsure: no government word found, ask who publishes it
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: CREDIT · source item page · "Old Topopgrapher Old Topopgrapher" · item https://www.arcgis.com/home/item.html?id=74707366cc3a4cc589611603da9044ea · owner topographer · org   The Old Topographer
- facts: arcgis-layer · esriGeometryPolygon · name field Name · 3 records · last edit 2015-12-30 · sample Fort Miamis / Foot Of The Rapids / Battle of Fallen Timbers Battle Space
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### Pinelands Management Areas  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/nCm6SZaiGMuGX35l/arcgis/rest/services/Pinelands_ManagementAreas/FeatureServer/0
- WHY: official and usable, but no missing parks were tested (none listed for the area or no time)
- publisher: ? → official (government words: Commission)
- terms: CREDIT · source item page · "The geodetic accuracy and precision of data contained within the coverage has not been developed nor verified b" · item https://www.arcgis.com/home/item.html?id=d94ed3f13d784a8ab57486b003c5478d · owner NJPinelands · org New Jersey Pinelands Commission
- facts: arcgis-layer · esriGeometryPolygon · name field NAME · 365 records · last edit 2026-05-22 · sample None / None / None
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### Palmetto Bay Municipal Boundary  ·    ·  from gis-hunter
- url: https://services.arcgis.com/8Pc9XBTAsYuxx9Ny/arcgis/rest/services/Municipal_Boundary_33/FeatureServer/0
- WHY: official and usable, but no missing parks were tested (none listed for the area or no time)
- publisher: ? → official (government words: County)
- terms: CREDIT · source item page · "Miami-Dade County provides this data for use &quot;as is&quot;. The areas depicted by this map/data are approximate, and are not accurate to surve" · item https://www.arcgis.com/home/item.html?id=7f80f7083a6540138e50f2cd457644e3 · owner MDPublisher · org Miami-Dade County, Florida
- facts: arcgis-layer · esriGeometryPolygon · name field NAME · 1 records · last edit 2026-06-02 · sample PALMETTO BAY
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### Local Authority Districts (May 2024) Boundaries UK BFC  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/ESMARspQHYMw9BZ9/arcgis/rest/services/Local_Authority_Districts_May_2024_Boundaries_UK_BFC/FeatureServer/0
- WHY: official and usable, but no missing parks were tested (none listed for the area or no time)
- publisher: ? → official (government words: Authority)
- terms: CREDIT · source item page · "https://www.ons.gov.uk/methodology/geography/licences Office for National Statistics Office for National Statistics" · item https://www.arcgis.com/home/item.html?id=f23beaa3769a4488b6a5f0cfb7980f51 · owner ONSGeography_data · org Office for National Statistics
- facts: arcgis-layer · esriGeometryPolygon · name field LAD24NM · 361 records · last edit 2024-07-16 · sample Hartlepool / Middlesbrough / Redcar and Cleveland
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### Lower Delaware Watershed  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/HERT3Lrqxe0YUfxz/arcgis/rest/services/Lower_Delaware_Watershed/FeatureServer/0
- WHY: nothing stated about use on the item page or the service
- publisher: ? → official (government words: Commission)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=5eb7a54208fa44fc9e71457c45e81866 · owner karenreavy · org Delaware River Basin Commission
- facts: arcgis-layer · esriGeometryPolygon · name field Name · 1 records · last edit 2016-06-03 · sample Special Protection Waters - Lower
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### First Nation Heritage Sites  ·    ·  from gis-hunter
- url: https://mapservices.gov.yk.ca/arcgis/rest/services/GeoYukon/GY_CultureHeritage/MapServer/15
- WHY: official and usable, but no missing parks were tested (none listed for the area or no time)
- publisher: ? → official (government host mapservices.gov.yk.ca)
- terms: CREDIT · source item page · "Government of Yukon" · item https://mapservices.gov.yk.ca/arcgis/rest/services/GeoYukon/GY_CultureHeritage/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field SITE_NAME · 62 records · sample 12 / 16 / 10
- overlap: same publisher as Yukon campgr
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### Pinelands Area  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/nCm6SZaiGMuGX35l/arcgis/rest/services/Pinelands_Area/FeatureServer/0
- WHY: official and usable, but no missing parks were tested (none listed for the area or no time)
- publisher: ? → official (government words: Commission)
- terms: CREDIT · source item page · "The geodetic accuracy and precision of data contained within the coverage has not been developed nor verified b" · item https://www.arcgis.com/home/item.html?id=a997d8634d9e4ad4935a5342b21a9b7b · owner NJPinelands · org New Jersey Pinelands Commission
- facts: arcgis-layer · esriGeometryPolygon · name field Name · 1 records · last edit 2025-05-22 · sample New Jersey Pinelands Area
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### GWMP Mount Vernon Trail Polygon  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/fBc8EJBxQRMcHlei/arcgis/rest/services/GWMP_Mount_Vernon_Trail_Polygon/FeatureServer/2
- WHY: official and usable, but no missing parks were tested (none listed for the area or no time)
- publisher: ? → official (a federal / national agency named)
- terms: CREDIT · source item page · "to use the related graphics as data. The National Park Service gives no warranty, expressed or implied, as to t National Capital Region, National Park Service" · item https://www.arcgis.com/home/item.html?id=93765f81f2b74e479aef9d4a814ab77f · owner CWanschura@nps.gov_nps · org National Park Service
- facts: arcgis-layer · esriGeometryPolygon · name field UNITNAME · 86 records · last edit 2023-05-03 · sample George Washington Memorial Parkway / George Washington Memorial Parkway / George Washington Memorial Parkway
- overlap: same publisher as akht
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### GWMP Mount Vernon Trail Polygon  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/fBc8EJBxQRMcHlei/arcgis/rest/services/GWMP_Mount_Vernon_Trail_Polygon/FeatureServer/1
- WHY: official and usable, but no missing parks were tested (none listed for the area or no time)
- publisher: ? → official (a federal / national agency named)
- terms: CREDIT · source item page · "to use the related graphics as data. The National Park Service gives no warranty, expressed or implied, as to t National Capital Region, National Park Service" · item https://www.arcgis.com/home/item.html?id=93765f81f2b74e479aef9d4a814ab77f · owner CWanschura@nps.gov_nps · org National Park Service
- facts: arcgis-layer · esriGeometryPolygon · name field UNITNAME · 1 records · last edit 2023-05-03 · sample George Washington Memorial Parkway
- overlap: same publisher as akht
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### Adults with Daily Sugar-Sweetened Beverage Consumption  ·    ·  from gis-hunter
- url: https://services.arcgis.com/RmCCgQtiZLDCtblq/arcgis/rest/services/Sweet_Beverages_Adults/FeatureServer/0
- WHY: official and usable, but no missing parks were tested (none listed for the area or no time)
- publisher: ? → official (government words: County)
- terms: CREDIT · source item page · "of Public Health; [2] Population and Poverty Estimates (Provisional), prepared by Hedderson Demographic Services for Los Angeles County," · item https://www.arcgis.com/home/item.html?id=df7d8ddb85674e0caa211c5067231ae1 · owner VElmore@ph.lacounty.gov_lacounty · org County of Los Angeles
- facts: arcgis-layer · esriGeometryPolygon · name field Geo_Name · 379 records · last edit 2024-04-23 · sample City of Agoura Hills / City of Alhambra / City of Arcadia
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### Children with Daily Sugar-Sweetened Beverage Consumption  ·    ·  from gis-hunter
- url: https://services.arcgis.com/RmCCgQtiZLDCtblq/arcgis/rest/services/Sweet_Beverages_Children/FeatureServer/0
- WHY: official and usable, but no missing parks were tested (none listed for the area or no time)
- publisher: ? → official (government words: County)
- terms: CREDIT · source item page · "of Public Health; [2] Population and Poverty Estimates (Provisional), prepared by Hedderson Demographic Services for Los Angeles County," · item https://www.arcgis.com/home/item.html?id=5627dc4c1ee8428aa37550a2fc59d128 · owner VElmore@ph.lacounty.gov_lacounty · org County of Los Angeles
- facts: arcgis-layer · esriGeometryPolygon · name field Geo_Name · 379 records · last edit 2024-04-23 · sample City of Agoura Hills / City of Alhambra / City of Arcadia
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### Hawaii Capital Historic District  ·    ·  from gis-hunter
- url: https://services5.arcgis.com/LjEpKgpks2lYdrmt/arcgis/rest/services/Hawaii_Capital_Historic_District/FeatureServer/0
- WHY: nothing stated about use on the item page or the service
- publisher: ? → official (government words: District)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=86d8ee97b55b4edcaa0d9ced800b1624 · owner nyokoi_CSH
- facts: arcgis-layer · esriGeometryPolygon · name field Feat_Name · 1 records · last edit 2018-09-12 · sample Hawaii Capital Historic District
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### Manhattan Project National Historical Park Sites - INTERIM  ·    ·  from gis-hunter
- url: https://services8.arcgis.com/0fu8WGujjdRBAiQR/arcgis/rest/services/NHPSITES_INTERIM/FeatureServer/0
- WHY: official and usable, but no missing parks were tested (none listed for the area or no time)
- publisher: ? → official (a government word of the country: National)
- terms: CREDIT · source item page · "ly referred to as the &quot;Information&quot;), are provided on &quot;AS IS&quot;, &quot;AS AVAILABLE&quot; and &quot;WITH ALL FAULTS&quot; bases. Neither the Depart" · item https://www.arcgis.com/home/item.html?id=30fba16c94c54a419786811d3b7d742a · owner h5265664@rl.gov_hanfordsite · org Hanford Site
- facts: arcgis-layer · esriGeometryPolygon · name field Name · 5 records · last edit 2025-12-12 · sample White Bluffs Bank / B Reactor / Bruggemann's Warehouse
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### Johnson City Adjusted Urban Area 2025 (Johnson City MTPO)  ·    ·  from gis-hunter
- url: https://services2.arcgis.com/sFeLdas1ukfB6i8T/arcgis/rest/services/Johnson_City_Adjusted_Urban_Area_2025_(Johnson_City_MTPO)/FeatureServer/2
- WHY: official and usable, but no missing parks were tested (none listed for the area or no time)
- publisher: ? → official (government words: City of)
- terms: CREDIT · source item page · "Johnson City MTPO Glenn K. Berry, Micha Bray, Michael Thompson" · item https://www.arcgis.com/home/item.html?id=50c321fa78a54eb3839b79ad8b29aee2 · owner jcgis_publisher · org City of Johnson City, TN 
- facts: arcgis-layer · esriGeometryPolygon · name field NAME20 · 1 records · last edit 2025-09-18 · sample Johnson City, TN
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### Pleasant_Valley_Siren_Coverage_Range_(Points)  ·    ·  from gis-hunter
- url: https://services3.arcgis.com/VDLfos9gESU44Yus/arcgis/rest/services/Pleasant_Valley_Siren_Coverage_Range_(Points)/FeatureServer/0
- WHY: nothing stated about use on the item page or the service
- publisher: ? → official (a government word of the country: National)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=2623aa8f8a5946d2989cc61801eabe45 · owner APoelzl_NFCA_USA · org National Fusion Center Association
- facts: arcgis-layer · esriGeometryPolygon · name field TITLE · 1 records · last edit 2023-03-28 · sample 8108 Pleasant Valley Rd, Pleasant Valley, Missouri, 64068
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### Pleasant Valley Maps  ·    ·  from gis-hunter
- url: https://services5.arcgis.com/kxeQ182ZV0PBfBVA/arcgis/rest/services/Pleasant_Valley_Maps/FeatureServer/1
- WHY: publisher unsure: no government word found, ask who publishes it
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: CREDIT · source item page · "California Protected Areas Database (CPAD - www.calands.org). December 2022." · item https://www.arcgis.com/home/item.html?id=5464ac78a3714d868ab853b2c91e7201 · owner KTUA_Planner · org KTU & A Planning & Landscape Architecture
- facts: arcgis-layer · esriGeometryPolygon · name field UNIT_NAME · 29 records · last edit 2024-01-25 · sample Springville Park / Trailside Park / Valle Lindo Park
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### 202108_Capital_Projects  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/0mhlGDIUKwQF6tnJ/arcgis/rest/services/202105_Capital_Projects/FeatureServer/5
- WHY: official and usable, but no missing parks were tested (none listed for the area or no time)
- publisher: ? → official (government words: Authority)
- terms: CREDIT · source item page · "This feature service is publicly accessible. NYCHA Performance Tracking & Analytics Department (PTAD) NYCHA Performance Tracking & Analytics Department (PTAD)" · item https://www.arcgis.com/home/item.html?id=294925feabbb469c95fdfb535bfb1ab2 · owner cheungy · org New York City Housing Authority
- facts: arcgis-layer · esriGeometryPolygon · name field BLDG_LABEL · 2396 records · last edit 2021-11-16 · sample 1 / 1 / 1
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### 202108_Capital_Projects  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/0mhlGDIUKwQF6tnJ/arcgis/rest/services/202105_Capital_Projects/FeatureServer/7
- WHY: official and usable, but no missing parks were tested (none listed for the area or no time)
- publisher: ? → official (government words: Authority)
- terms: CREDIT · source item page · "This feature service is publicly accessible. NYCHA Performance Tracking & Analytics Department (PTAD) NYCHA Performance Tracking & Analytics Department (PTAD)" · item https://www.arcgis.com/home/item.html?id=294925feabbb469c95fdfb535bfb1ab2 · owner cheungy · org New York City Housing Authority
- facts: arcgis-layer · esriGeometryPolygon · name field boro_name · 5 records · last edit 2021-11-16 · sample Manhattan / Bronx / Brooklyn
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### Chimney Rock Ranch_WFL1  ·    ·  from gis-hunter
- url: https://services5.arcgis.com/vV1o91P0uxdOGCax/arcgis/rest/services/Chimney_Rock_Ranch_WFL1/FeatureServer/0
- WHY: nothing stated about use on the item page or the service
- publisher: ? → official (a government word of the country: Land )
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=5fee25c09b6a45afa0f3f8a96a07a079 · owner LISsystems · org Land Information Systems
- facts: arcgis-layer · esriGeometryPolygon · name field NAME · 1 records · last edit 2021-12-14 · sample CADDY LAND & LIVESTOCK LLC
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### Chimney Rock Ranch_WFL1  ·    ·  from gis-hunter
- url: https://services5.arcgis.com/vV1o91P0uxdOGCax/arcgis/rest/services/Chimney_Rock_Ranch_WFL1/FeatureServer/1
- WHY: nothing stated about use on the item page or the service
- publisher: ? → official (a government word of the country: Land )
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=5fee25c09b6a45afa0f3f8a96a07a079 · owner LISsystems · org Land Information Systems
- facts: arcgis-layer · esriGeometryPolygon · name field NAME · 1 records · last edit 2021-12-14 · sample CADDY LAND & LIVESTOCK LLC
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### Lone Star College School District View  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/PRoAPGnMSUqvTrzq/arcgis/rest/services/Lone_Star_College_School_Districts/FeatureServer/0
- WHY: hosted for an agency on another account: ask who owns and licenses it
- publisher: ? → hosted for an agency (a university account holds an agency layer)
- terms: CREDIT · source item page · "y Central Appraisal District. Users are responsible for verifying the accuracy and currency of the data for their intended use. Montgomery Central Appraisal District" · item https://www.arcgis.com/home/item.html?id=cecdf2364d0446e9b70838cc63b29c6c · owner GIS.Data_MOCO · org Montgomery County, Texas IT-GIS
- facts: arcgis-layer · esriGeometryPolygon · name field NAME · 9 records · last edit 2024-02-20 · sample LSC-CyFair / LSC-North Harris / LSC-Houston North Fairbanks
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### CSKT Bison Range  ·    ·  from gis-hunter
- url: https://services2.arcgis.com/HRY6x8qt5qjGnAA9/arcgis/rest/services/CSKT_Bison_Range/FeatureServer/0
- WHY: nothing stated about use on the item page or the service
- publisher: ? → official (a government word of the country: Institut)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=3d49345660ee4d5b8771701bc7554bba · owner ShamonH_SI · org Smithsonian Institution
- facts: arcgis-layer · esriGeometryPolygon · name field Name · 1 records · last edit 2024-11-11 · sample BISON RANGE
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### AB617 Richmond-San Pablo Monitoring Boundary  ·    ·  from gis-hunter
- url: https://services6.arcgis.com/xCuDJnRShQmTqPGL/arcgis/rest/services/AB617_Richmond_San_Pablo_Community_Boundary/FeatureServer/0
- WHY: official and usable, but no missing parks were tested (none listed for the area or no time)
- publisher: ? → official (a government word of the country: ign)
- terms: CREDIT · source item page · "2019 BAAQMD/Richmond-San Pablo Community Design Team - Community Boundary and Focus Areas" · item https://www.arcgis.com/home/item.html?id=4bf66f78890c481290a68b82da8a684d · owner llouie
- facts: arcgis-layer · esriGeometryPolygon · name field Name · 8 records · last edit 2020-06-29 · sample Hilltop & Parchester / North Richmond, Shields-Reid, Western San Pablo / Belding-Woods, Coronado, Pullman, Cortez-Stege
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### Urban Design Standards - North Highline  ·    ·  from gis-hunter
- url: https://services.arcgis.com/Ej0PsM5Aw677QF1W/arcgis/rest/services/URBAN_DESIGN_STANDARDS_AREA_3009/FeatureServer/0
- WHY: official and usable, but no missing parks were tested (none listed for the area or no time)
- publisher: ? → official (government words: County)
- terms: CREDIT · source item page · "dept/kcit/data-information-services/gis-center/about/terms-conditions-copyrights King County" · item https://www.arcgis.com/home/item.html?id=307cbc71c14c4efeb189ad8ef4f3a059 · owner KingCounty · org King County
- facts: arcgis-layer · esriGeometryPolygon · name field Community_Service_Area_Name · 255 records · last edit 2026-10-14 · sample North Highline / North Highline / North Highline
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### Fairfax County Boundary  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/ioennV6PpG5Xodq0/arcgis/rest/services/Fairfax_County_Boundary/FeatureServer/0
- WHY: official and usable, but no missing parks were tested (none listed for the area or no time)
- publisher: ? → official (a federal / national agency named)
- terms: CREDIT · source item page · "https://www.fairfaxcounty.gov/maps/disclaimer Fairfax County, Virginia; Fairfax County Department of Information Technology GIS Divisio" · item https://www.arcgis.com/home/item.html?id=e6e10e55d29642238d4d03b1a4a11b09 · owner FX.AuthData · org County of Fairfax
- facts: arcgis-layer · esriGeometryPolygon · name field NAME · 1 records · last edit 2026-07-01 · sample FAIRFAX COUNTY
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### Fairfax County Water Resources Monitoring Network monitoring watersheds  ·    ·  from gis-hunter
- url: https://services.arcgis.com/v01gqwM5QqNysAAi/arcgis/rest/services/Fairfax_monitoring_watersheds/FeatureServer/0
- WHY: official and usable, but no missing parks were tested (none listed for the area or no time)
- publisher: ? → official (a federal / national agency named)
- terms: CREDIT · source item page · "ccessfully on a computer system at the U.S. Geological Survey (USGS), no warranty expressed or implied is made regarding the display or utility of the data on any other sy" · item https://www.arcgis.com/home/item.html?id=eac6297498f640f0b896e3cf4a7a31f9 · owner ckandel@usgs.gov_USGS · org U.S. Geological Survey
- facts: arcgis-layer · esriGeometryPolygon · name field site_no · 20 records · last edit 2023-10-19 · sample 01645704 / 01656903 / 01654500
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### Great Salt Lake Basin  ·    ·  from gis-hunter
- url: https://services.arcgis.com/ZzrwjTRez6FJiOq4/arcgis/rest/services/Great_Salt_Lake_Basin/FeatureServer/1
- WHY: official and usable, but no missing parks were tested (none listed for the area or no time)
- publisher: ? → official (government words: DNR)
- terms: OPEN · source item page · "CC BY-SA Disclaimer: For reference use only. Although this product represents the work of natur" · item https://www.arcgis.com/home/item.html?id=ceb4e87f7f664fe8a81e8418cafb226a · owner dnrwres · org Utah DNR Online Maps
- facts: arcgis-layer · esriGeometryPolygon · name field NAME · 1 records · last edit 2025-06-25 · sample BEAR RIVER
- overlap: same publisher as sguta
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### m216_pine_grove_land_rds  ·    ·  from gis-hunter
- url: https://services3.arcgis.com/wid5AQd6BHjWWq1h/arcgis/rest/services/m216_pine_grove_land_rds/FeatureServer/1
- WHY: official and usable, but no missing parks were tested (none listed for the area or no time)
- publisher: ? → official (government words: Town of)
- terms: CREDIT · source item page · "CMRPC and the Town of Northbridge, MA CMRPC and the Town of Northbridge, MA" · item https://www.arcgis.com/home/item.html?id=009abaacfaac4d558b78f2b5991b1f51 · owner mfranz_cmrpc · org CMRPC
- facts: arcgis-layer · esriGeometryPolygon · name field LND_NAME · 56 records · last edit 2017-04-13 · sample None / SECTION 2 / Del Barnes
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### Vegetation Map of North Cascades National Park Service Complex  ·    ·  from gis-hunter
- url: https://tiles.arcgis.com/tiles/fBc8EJBxQRMcHlei/arcgis/rest/services/NOCA_VegMap/MapServer/1
- WHY: hosted for an agency on another account: ask who owns and licenses it
- publisher: ? → hosted for an agency (a university account holds an agency layer)
- terms: CREDIT · source item page · "general and these data in particular. The National Park Service gives no warranty, expressed or implied, as to the accuracy, reliability, or completeness of these data. Al" · item https://www.arcgis.com/home/item.html?id=bdc4943bc34243d99a2f3dec508237ec · owner NAntonova@nps.gov_nps · org National Park Service
- facts: arcgis-layer · esriGeometryPolygon · name field Name
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### Vegetation Map of North Cascades National Park Complex (polygons)  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/fBc8EJBxQRMcHlei/arcgis/rest/services/NOCA_VegMap/FeatureServer/1
- WHY: hosted for an agency on another account: ask who owns and licenses it
- publisher: ? → hosted for an agency (a university account holds an agency layer)
- terms: CREDIT · source item page · "general and these data in particular. The National Park Service gives no warranty, expressed or implied, as to the accuracy, reliability, or completeness of these data. Al" · item https://www.arcgis.com/home/item.html?id=6788df6beb774a608c9dcc04df3a99e6 · owner NAntonova@nps.gov_nps · org National Park Service
- facts: arcgis-layer · esriGeometryPolygon · name field Name · 897771 records · last edit 2022-11-15 · sample S49 Alpine heather shrubland / C13 Mountain hemlock, silver fir and Cascade azalea forest / R73 Bedrock barren
- overlap: same publisher as akht
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### Cornelius Impervious Tiers_WFL1  ·    ·  from gis-hunter
- url: https://services.arcgis.com/BWD3gDuaqc7SQmy7/arcgis/rest/services/Cornelius_Impervious_Tiers_WFL1/FeatureServer/0
- WHY: nothing stated about use on the item page or the service
- publisher: ? → official (government words: County)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=7b666e40a4ac4636aedb6023197dd8c7 · owner Nir.Josipovich@mecklenburgcountync.gov_meckgov · org Mecklenburg County GIS
- facts: arcgis-layer · esriGeometryPolygon · name field name · 2 records · last edit 2020-10-02 · sample Cornelius / Cornelius
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### Cornelius Impervious Tiers_WFL1  ·    ·  from gis-hunter
- url: https://services.arcgis.com/BWD3gDuaqc7SQmy7/arcgis/rest/services/Cornelius_Impervious_Tiers_WFL1/FeatureServer/3
- WHY: nothing stated about use on the item page or the service
- publisher: ? → official (government words: County)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=7b666e40a4ac4636aedb6023197dd8c7 · owner Nir.Josipovich@mecklenburgcountync.gov_meckgov · org Mecklenburg County GIS
- facts: arcgis-layer · esriGeometryPolygon · name field stname · 6152 records · last edit 2020-10-02 · sample ISLAND VIEW                    / JETTON                         / META                          
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### Smyth Multimodal - Mount Rogers National Recreation Area  ·    ·  from gis-hunter
- url: https://services9.arcgis.com/Wl3c8iIqFcIDE29g/arcgis/rest/services/smyth_multimodal_mount_rogers_nra_b8a8410/FeatureServer/0
- WHY: official and usable, but no missing parks were tested (none listed for the area or no time)
- publisher: ? → official (a government word of the country: National)
- terms: CREDIT · source item page · "Public planning/reference use subject to source limitations and attribution. EPR PC; canonical source and public REST provenance documented in item resources. Source" · item https://www.arcgis.com/home/item.html?id=56fbdebc9cea44b9880069874870c26c · owner EPRGIS · org EPR PC
- facts: arcgis-layer · esriGeometryPolygon · name field area_name · 1 records · last edit 2026-07-31 · sample Mount Rogers National Recreation Area
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### ACTGOV Horse Paddock Assets  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/E5n4f1VY84i0xSjy/arcgis/rest/services/ACTGOV_Horse_Paddock_Assets/FeatureServer/1
- WHY: official and usable, but no missing parks were tested (none listed for the area or no time)
- publisher: ? → official (government words: Government)
- terms: OPEN · source item page · "Creative Commons By Attribution 4.0 (Australian Capital Territory) Please read Data Terms and Conditions s" · item https://www.arcgis.com/home/item.html?id=1f1d01466ad14b4f9fa3930fa0497a66 · owner cityoperationsactgov · org Australian Capital Territory Government
- facts: arcgis-layer · esriGeometryPolygon · name field ASSET_NAME · 283 records · last edit 2026-08-10 · sample PARKWOOD PINE PL / HACKETT 1 / NEIGHBOUR 9
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### BLM Natl Wild Horse and Burro Herd Mgmt Area Polygons  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/KbxwQRRfWyEYLgp4/arcgis/rest/services/BLM_Natl_Wild_Horse_and_Burro_Heard_Mgmt_Area_Polygons/FeatureServer/0
- WHY: official and usable, but no missing parks were tested (none listed for the area or no time)
- publisher: ? → official (a federal / national agency named)
- terms: CREDIT · source item page · "These data are provided by Bureau of Land Management (BLM) “as is” and might contain errors or omissions. The User a" · item https://www.arcgis.com/home/item.html?id=ef82f4b7e972466498b30ed51d4d73ac · owner blm_arcgis_hub_natl · org Bureau of Land Management
- facts: arcgis-layer · esriGeometryPolygon · name field HMA_NAME · 181 records · last edit 2026-10-13 · sample Lahontan / Sinbad / Callaghan
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### Lincoln City Boundaries  ·    ·  from gis-hunter
- url: https://services2.arcgis.com/j80Jz20at6Bi0thr/arcgis/rest/services/lincoln/FeatureServer/0
- WHY: official and usable, but no missing parks were tested (none listed for the area or no time)
- publisher: ? → official (government words: Department)
- terms: OPEN · source item page · "m its original source, https://opendata.lincoln.ne.gov/, the official open data website of the City of Lincoln. The City of Lincoln makes no claims as to the content, ac" · item https://www.arcgis.com/home/item.html?id=21bf2342fc0541fe978549e9453bb1a8 · owner Learn_ArcGIS · org Esri Tutorials
- facts: arcgis-layer · esriGeometryPolygon · name field NAME · 1 records · last edit 2016-06-07 · sample Lincoln
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### Empire State Trail  ·    ·  from gis-hunter
- url: https://services.arcgis.com/1xFZPtKn1wKC6POA/arcgis/rest/services/EST_Public/FeatureServer/5
- WHY: official and usable, but no missing parks were tested (none listed for the area or no time)
- publisher: ? → official (government words: Office of)
- terms: NON-COMMERCIAL · source item page · "its use. The data and applications are provided for informational and non-commercial purposes. Any maps, reports, or other m New York State Office of Parks, Recreation, and H" · item https://www.arcgis.com/home/item.html?id=42193621bed6494a86a5cc343ee9a854 · owner Christina.Croll@parks.ny.gov_nysparks · org NYS OPRHP
- facts: arcgis-layer · esriGeometryPolygon · name field ParentLegName · 2 records · last edit 2026-10-14 · sample Erie Canalway Trail (Rome to Utica) / Erie Canalway Trail (Rome to Utica)
- overlap: same publisher as sgnyb
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### Pre Clear Vegetation 2021 view  ·    ·  from gis-hunter
- url: https://services-ap1.arcgis.com/lnVW0dLI3fvST2hd/arcgis/rest/services/Pre_Clear_Vegetation_2021_view/FeatureServer/1
- WHY: official and usable, but no missing parks were tested (none listed for the area or no time)
- publisher: ? → official (government words: State of)
- terms: OPEN · source item page · "This data is licensed under CC BY 4.0 © State of Queensland (Department of Environment and Science) 2023." · item https://www.arcgis.com/home/item.html?id=4abcb88bb1724c6fb32682827794e3f9 · owner CoGC_Admin
- facts: arcgis-layer · esriGeometryPolygon · name field RE_LABEL · 3377 records · last edit 2026-08-20 · sample 12.3.11 / 12.1.2 / 12.3.8
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### State Aquatic Management Area (AMA) Aquisitions  ·    ·  from gis-hunter
- url: https://enterprise.gisdata.mn.gov/aghost/rest/services/us_mn_state_dnr/plan_mndnr_fisheries_acquisition/FeatureServer/0
- WHY: official and usable, but no missing parks were tested (none listed for the area or no time)
- publisher: ? → official (government host enterprise.gisdata.mn.gov)
- terms: CREDIT · source item page · "ly representative of acquired lands, but they are not of survey-grade accuracy. Do not use for boundary disputes or legal applications. Use of the data are constrained" · item https://enterprise.gisdata.mn.gov/home/item.html?id=5e8a2e67f2954268ac8f88cefb09f0df · owner commonsAdmin
- facts: arcgis-layer · esriGeometryPolygon · name field unit_name · 1587 records · sample Trout Run Creek AMA / Trout Run Creek AMA / Trout Run Creek AMA
- overlap: same publisher as sgmna
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### LSL_Basemap_View- Two Harbors  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/Fxir0Ov4y8APKoU8/arcgis/rest/services/LSL_Basemap_view_e5a577fedbb6490a8904de07161b0321/FeatureServer/0
- WHY: nothing stated about use on the item page or the service
- publisher: ? → official (government words: City of)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=76a27ef4a10a4b13baec30bfd7d2f8ba · owner BoltonMenk_TwoHarbors · org City of Two Harbors
- facts: arcgis-layer · esriGeometryPolygon · name field TAX_TAXNAME · 2916 records · last edit 2024-05-09 · sample WISCONSIN CENTRAL LTD / BRENNA RANDALL ALAN / MYRDAL PROPERTIES LLC
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### Two Harbors Zoning With NSMB Boundary_WFL1  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/XcwN27e6wZ49zF8i/arcgis/rest/services/Two_Harbors_Zoning_With_NSMB_Boundary_WFL1/FeatureServer/1
- WHY: nothing stated about use on the item page or the service
- publisher: ? → official (government words: Commission)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=4af73b03aace45ddabeefa93483b167a · owner ARDCGIS · org Arrowhead Regional Development Commission
- facts: arcgis-layer · esriGeometryPolygon · name field ST_NAME · 4620 records · last edit 2024-08-29 · sample HWY 61 / None / None
- closes: not probed

### Two Harbors Zoning With NSMB Boundary_WFL1  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/XcwN27e6wZ49zF8i/arcgis/rest/services/Two_Harbors_Zoning_With_NSMB_Boundary_WFL1/FeatureServer/3
- WHY: nothing stated about use on the item page or the service
- publisher: ? → official (government words: Commission)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=4af73b03aace45ddabeefa93483b167a · owner ARDCGIS · org Arrowhead Regional Development Commission
- facts: arcgis-layer · esriGeometryPolygon · name field Name · 1 records · last edit 2024-08-29 · sample Two Harbors
- closes: not probed

### Two Harbors Zoning With NSMB Boundary_WFL1  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/XcwN27e6wZ49zF8i/arcgis/rest/services/Two_Harbors_Zoning_With_NSMB_Boundary_WFL1/FeatureServer/4
- WHY: nothing stated about use on the item page or the service
- publisher: ? → official (government words: Commission)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=4af73b03aace45ddabeefa93483b167a · owner ARDCGIS · org Arrowhead Regional Development Commission
- facts: arcgis-layer · esriGeometryPolygon · name field ST_NAME · 4620 records · last edit 2024-08-29 · sample HWY 61 / None / None
- closes: not probed

### Two Harbors Zoning With NSMB Boundary_WFL1  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/XcwN27e6wZ49zF8i/arcgis/rest/services/Two_Harbors_Zoning_With_NSMB_Boundary_WFL1/FeatureServer/5
- WHY: nothing stated about use on the item page or the service
- publisher: ? → official (government words: Commission)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=4af73b03aace45ddabeefa93483b167a · owner ARDCGIS · org Arrowhead Regional Development Commission
- facts: arcgis-layer · esriGeometryPolygon · name field ST_NAME · 4620 records · last edit 2024-08-29 · sample HWY 61 / None / None
- closes: not probed

### Gitchi Gami Shoulder Widths_WFL1  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/XcwN27e6wZ49zF8i/arcgis/rest/services/Gitchi_Gami_Shoulder_Widths_WFL1/FeatureServer/7
- WHY: nothing stated about use on the item page or the service
- publisher: ? → official (government words: Commission)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=d5adfddb4b6e45a19c7ce4f54a31cd28 · owner ARDCGIS · org Arrowhead Regional Development Commission
- facts: arcgis-layer · esriGeometryPolygon · name field CTY_NAME · 19 records · last edit 2025-03-06 · sample Koochiching / St. Louis / Cook
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### NCDOT Hellers_Blazing_Star_Potential_Habitat  ·    ·  from gis-hunter
- url: https://services.arcgis.com/NuWFvHYDMVmmxMeM/arcgis/rest/services/Hellers_Blazing_Star_Potential_Habitat/FeatureServer/0
- WHY: official and usable, but no missing parks were tested (none listed for the area or no time)
- publisher: ? → official (government words: Department)
- terms: CREDIT · source item page · "rrors concerning the content of the data, and relative and positional accuracy of the data. This data cannot be construed to be a legal document. Primary sources from w" · item https://www.arcgis.com/home/item.html?id=24057f8c62604c25ab46dc0f6c4b3d79 · owner Atlas.NCDOT.GOV · org North Carolina Department of Transportation
- facts: arcgis-layer · esriGeometryPolygon · name field SciName · 3267 records · last edit 2021-12-21 · sample Liatris helleri / Liatris helleri / Liatris helleri
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### Turtle Mountain  ·    ·  from gis-hunter
- url: https://services.arcgis.com/Qmnh5K1IrqlBQ9WP/arcgis/rest/services/Turtle_Mountain/FeatureServer/0
- WHY: hosted for an agency on another account: ask who owns and licenses it
- publisher: ? → hosted for an agency (a university account holds an agency layer)
- terms: CREDIT · source item page · "rative and reference purposes only and should not be used, and is not intended for legal, survey, engineering or navigation purposes. No warranty is made by the Bureau of I" · item https://www.arcgis.com/home/item.html?id=3dc49a9e8c1b4e4ab0c8292e660d231e · owner rmeyer@smumn.edu_SMUMN · org Saint Mary's University of Minnesota
- facts: arcgis-layer · esriGeometryPolygon · name field LARName · 1 records · last edit 2024-04-19 · sample Turtle Mountain LAR
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### Prebles Meadow Jumping Mouse Critical Habitat  ·    ·  from gis-hunter
- url: https://services.arcgis.com/XG15cJAlne2vxtgt/arcgis/rest/services/Prebles_Meadow_Jumping_Mouse_Critical_Habitat/FeatureServer/0
- WHY: official and usable, but no missing parks were tested (none listed for the area or no time)
- publisher: ? → official (a federal / national agency named)
- terms: CREDIT · source item page · "None. Users are advised to read the data set's metadata thoroughly to understand appropriate use and data limitations. USFWS USFWS" · item https://www.arcgis.com/home/item.html?id=55555f14f6df42ed84af19d4658862df · owner FEMA_Region8_GIS · org FEMA AGOL
- facts: arcgis-layer · esriGeometryPolygon · name field PMJM_Unit · 80 records · last edit 2022-01-07 · sample Unit 1 / Unit 1 / Unit 1
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### Prebles Meadow Jumping Mouse Habitat  ·    ·  from gis-hunter
- url: https://maps.bouldercounty.org/arcgis/rest/services/PLANNING/BCCP_PMJM/FeatureServer/0
- WHY: official and usable, but no missing parks were tested (none listed for the area or no time)
- publisher: ? → official (government words: County)
- terms: CREDIT · source item page · "Boulder County Parks and Open Space" · item https://maps.bouldercounty.org/arcgis/rest/services/PLANNING/BCCP_PMJM/FeatureServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field PMJMZoneName · 246 records · sample Suitable, Noncontiguous Habitat / Suitable, Noncontiguous Habitat / Suitable, Noncontiguous Habitat
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### Jessie Family Cemetery  ·    ·  from gis-hunter
- url: https://services6.arcgis.com/LledJs8ADlUCS7Cz/arcgis/rest/services/Jessie_Family_Cemetery/FeatureServer/2
- WHY: official and usable, but no missing parks were tested (none listed for the area or no time)
- publisher: ? → official (government words: District)
- terms: CREDIT · source item page · "This general-purpose content was derived from digital databases maintained by the Barren River Area Development District (BRADD) GIS Department or an external source." · item https://www.arcgis.com/home/item.html?id=d5f8b321b3594651833b90fe794a43c3 · owner BRADD_Admin · org Barren River Area Development District
- facts: arcgis-layer · esriGeometryPolygon · name field Surname · 20 records · last edit 2021-04-09 · sample England / Fields / Fields
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### Jessie Family Cemetery  ·    ·  from gis-hunter
- url: https://services6.arcgis.com/LledJs8ADlUCS7Cz/arcgis/rest/services/Jessie_Family_Cemetery/FeatureServer/3
- WHY: official and usable, but no missing parks were tested (none listed for the area or no time)
- publisher: ? → official (government words: District)
- terms: CREDIT · source item page · "This general-purpose content was derived from digital databases maintained by the Barren River Area Development District (BRADD) GIS Department or an external source." · item https://www.arcgis.com/home/item.html?id=d5f8b321b3594651833b90fe794a43c3 · owner BRADD_Admin · org Barren River Area Development District
- facts: arcgis-layer · esriGeometryPolygon · name field Name · 1 records · last edit 2021-04-09 · sample None
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### HOA Subdiv SHerry  ·    ·  from gis-hunter
- url: https://services6.arcgis.com/ZcuYjGGvzsyH5Zu7/arcgis/rest/services/HOA_Subdiv_SHerry/FeatureServer/0
- WHY: nothing stated about use on the item page or the service
- publisher: ? → official (government words: City of)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=34a1b741cd3b4ce8b94cebe7137b8335 · owner WashougalStorm · org City of Washougal
- facts: arcgis-layer · esriGeometryPolygon · name field NAME · 164 records · last edit 2026-10-23 · sample SUNSET RIDGE PH2 / TURTLE COVE / LOOKOUT RIDGE PH 1A
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### Bighorn Sheep Herd Units - CDFW [ds3400]  ·    ·  from gis-hunter
- url: https://services2.arcgis.com/Uq9r85Potqm3MfRV/arcgis/rest/services/biosds3400_fpu/FeatureServer/0
- WHY: official and usable, but no missing parks were tested (none listed for the area or no time)
- publisher: ? → official (government words: Department)
- terms: OPEN · source item page · "nvironmental Quality Act (CEQA). License: This work is licensed under Creative Commons Attribution 4.0 International License ( https://creativecommons.org/l Paige Young; Statew" · item https://www.arcgis.com/home/item.html?id=c6b08834c64c4c1e9271c9017ca383e0 · owner BIOS_Admin · org California Department of Fish and Wildlife
- facts: arcgis-layer · esriGeometryPolygon · name field NAME · 96 records · last edit 2026-08-18 · sample DEBS - Deeps Springs / DEBS - Last Chance / Dry Mountain / DEBS - Grapevine Mountains - North
- overlap: same publisher as sgcaa
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### FEIS Pacific Crest National Scenic Trail Management Area Alternatives C & E  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/gGHDlz6USftL5Pau/arcgis/rest/services/FEIS_Pacific_Crest_Trail_Management_Corridor_Alternatives_C_and_E/FeatureServer/0
- WHY: official and usable, but no missing parks were tested (none listed for the area or no time)
- publisher: ? → official (a federal / national agency named)
- terms: CREDIT · source item page · "SDA Forest Service makes no claims, promises, or guarantees about the accuracy, completeness, or adequacy of the content; and expressly disclaims liability for errors a" · item https://www.arcgis.com/home/item.html?id=b52c4f0398734c559eb206c2fc88f991 · owner USFSRegion05 · org U.S. Forest Service
- facts: arcgis-layer · esriGeometryPolygon · name field FORESTNAME · 2 records · last edit 2022-06-02 · sample Sierra National Forest / Sequoia National Forest
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### FEIS Pacific Crest National Scenic Trail Management Area Alternatives B & B Modified  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/gGHDlz6USftL5Pau/arcgis/rest/services/FEIS_Pacific_Crest_Trail_Alternative_B_and_B_Modified/FeatureServer/0
- WHY: official and usable, but no missing parks were tested (none listed for the area or no time)
- publisher: ? → official (a federal / national agency named)
- terms: CREDIT · source item page · "SDA Forest Service makes no claims, promises, or guarantees about the accuracy, completeness, or adequacy of the content; and expressly disclaims liability for errors a" · item https://www.arcgis.com/home/item.html?id=e524f97eb43f494089a97020c24270cb · owner USFSRegion05 · org U.S. Forest Service
- facts: arcgis-layer · esriGeometryPolygon · name field FORESTNAME · 2 records · last edit 2022-06-02 · sample Sierra National Forest / Sequoia National Forest
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### Little Pend Oreille Wildlife refuge  ·    ·  from gis-hunter
- url: https://services.arcgis.com/v01gqwM5QqNysAAi/arcgis/rest/services/Little_Pend_Oreille_Wildlife_refuge/FeatureServer/0
- WHY: official and usable, but no missing parks were tested (none listed for the area or no time)
- publisher: ? → official (a federal / national agency named)
- terms: CREDIT · source item page · "ly on a computer system at the U.S. Fish and Wildlife Service, USFWS, no warranty expressed or implied is made regarding the accuracy or utility of the data and informatio" · item https://www.arcgis.com/home/item.html?id=06526e3bdf3f431cb114018be0b921f2 · owner ammartinez@usgs.gov_USGS · org U.S. Geological Survey
- facts: arcgis-layer · esriGeometryPolygon · name field ORGNAME · 1 records · last edit 2019-10-22 · sample LITTLE PEND OREILLE NATIONAL WILDLIFE REFUGE
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

## RETRY (90)

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

### Black Marble High Definition (BMHD) in Porto Alegre for the May 2024 Brasil Floods  ·    ·  from gis-hunter
- url: https://maps.disasters.nasa.gov/ags03/rest/services/brasil_flood_202405/blackmarble_hd/MapServer
- WHY: did not open (404): probed again next run (failed 1 of 3)
- publisher: ? → unsure (did not open)
- terms: NOTHING STATED · source none
- facts: status 404

### Cypremort_Point_State_Park  ·    ·  from gis-hunter
- url: https://services6.arcgis.com/p1YcgwPVVSqE29MG/arcgis/rest/services/Cypremort_Point_State_Park/FeatureServer
- WHY: did not open (error Token Required): probed again next run (failed 1 of 3)
- publisher: ? → unsure (did not open)
- terms: NOTHING STATED · source none
- facts: status error Token Required

### Jimmie_Davis_State_Park  ·    ·  from gis-hunter
- url: https://services6.arcgis.com/p1YcgwPVVSqE29MG/arcgis/rest/services/Jimmie_Davis_State_Park/FeatureServer
- WHY: did not open (error Token Required): probed again next run (failed 1 of 3)
- publisher: ? → unsure (did not open)
- terms: NOTHING STATED · source none
- facts: status error Token Required

### Bog Brook Road to Bog Pond Snowmobile Trail 35 Foot Right-Of-Way  ·  None  ·  from gis-hunter
- url: https://services4.arcgis.com/ctnv3S90gv4qdwQ1/arcgis/rest/services/Bog Brook Road to Bog Pond Snowmobile Trail 35 Foot Right-Of-Way/FeatureServer
- WHY: did not open (bot error URL can't contain control characters. '/ctnv3S90gv4qdwQ1/arcgis/rest/services/Bog Brook Road to Bog Pond Snowmobile Trai): probed again next run (failed 1 of 3)
- publisher: ? → unsure ()
- terms: ? · source ?
- facts: status bot error URL can't contain control characters. '/ctnv3S90gv4qdwQ1/arcgis/rest/services/Bog Brook Road to Bog Pond Snowmobile Trai

### Bog Brook Road to Lost River Self Storage 35 Foot Right-Of-Way  ·  None  ·  from gis-hunter
- url: https://services4.arcgis.com/ctnv3S90gv4qdwQ1/arcgis/rest/services/Bog Brook Road to Lost River Self Storage 35 Foot Right-Of-Way/FeatureServer
- WHY: did not open (bot error URL can't contain control characters. '/ctnv3S90gv4qdwQ1/arcgis/rest/services/Bog Brook Road to Lost River Self Storage ): probed again next run (failed 1 of 3)
- publisher: ? → unsure ()
- terms: ? · source ?
- facts: status bot error URL can't contain control characters. '/ctnv3S90gv4qdwQ1/arcgis/rest/services/Bog Brook Road to Lost River Self Storage 

### Civil War Battlefields  ·  None  ·  from gis-hunter
- url: https://services7.arcgis.com/iFGeGXTAJXnjq0YN/arcgis/rest/services/Civil War Battlefields Plus/FeatureServer
- WHY: did not open (bot error URL can't contain control characters. '/iFGeGXTAJXnjq0YN/arcgis/rest/services/Civil War Battlefields Plus/FeatureServer?): probed again next run (failed 1 of 3)
- publisher: ? → unsure ()
- terms: ? · source ?
- facts: status bot error URL can't contain control characters. '/iFGeGXTAJXnjq0YN/arcgis/rest/services/Civil War Battlefields Plus/FeatureServer?

### Civil War Battlefields (time-enabled)  ·  None  ·  from gis-hunter
- url: https://services7.arcgis.com/iFGeGXTAJXnjq0YN/arcgis/rest/services/Civil War Battlefields (time-enabled)/FeatureServer
- WHY: did not open (bot error URL can't contain control characters. '/iFGeGXTAJXnjq0YN/arcgis/rest/services/Civil War Battlefields (time-enabled)/Feat): probed again next run (failed 1 of 3)
- publisher: ? → unsure ()
- terms: ? · source ?
- facts: status bot error URL can't contain control characters. '/iFGeGXTAJXnjq0YN/arcgis/rest/services/Civil War Battlefields (time-enabled)/Feat

### Walnut Woods Park JWT  ·    ·  from gis-hunter
- url: https://services.arcgis.com/XORNS2fPFySPlBgy/arcgis/rest/services/Walnut_Woods_Park_JWT/FeatureServer
- WHY: did not open (error Invalid URL): probed again next run (failed 1 of 3)
- publisher: ? → unsure (did not open)
- terms: NOTHING STATED · source none
- facts: status error Invalid URL

### Canyon De Chelly National Monument, AZ (Data Basin Dataset)  ·    ·  from gis-hunter
- url: http://biology.usgs.gov/arcgis/rest/services/nvcp/Canyon_De_Chelly_NM/MapServer
- WHY: did not open (not json): probed again next run (failed 1 of 3)
- publisher: ? → unsure (did not open)
- terms: NOTHING STATED · source none
- facts: status not json

### Iceland Honeymoon 2024_WFL1  ·    ·  from gis-hunter
- url: https://services6.arcgis.com/v4iVHCxJx9aueHAS/arcgis/rest/services/Iceland_Honeymoon_2024_WFL1/FeatureServer
- WHY: did not open (error Token Required): probed again next run (failed 1 of 3)
- publisher: ? → unsure (did not open)
- terms: NOTHING STATED · source none
- facts: status error Token Required

### Iceland Honeymoon 2024_WFL  ·    ·  from gis-hunter
- url: https://services6.arcgis.com/v4iVHCxJx9aueHAS/arcgis/rest/services/Iceland_Honeymoon_2024_WFL/FeatureServer
- WHY: did not open (error Token Required): probed again next run (failed 1 of 3)
- publisher: ? → unsure (did not open)
- terms: NOTHING STATED · source none
- facts: status error Token Required

### Spencer_Ramp_Sidewalk  ·    ·  from gis-hunter
- url: https://services9.arcgis.com/BPqQmonW4XsiPHS3/arcgis/rest/services/Spencer_Ramp_Sidewalk/FeatureServer
- WHY: did not open (error Token Required): probed again next run (failed 1 of 3)
- publisher: ? → unsure (did not open)
- terms: NOTHING STATED · source none
- facts: status error Token Required

### Little Turtle_WFL1  ·    ·  from gis-hunter
- url: https://services7.arcgis.com/V2n9y2bh8WyGKmfd/arcgis/rest/services/Little_Turtle_WFL1/FeatureServer
- WHY: did not open (error Token Required): probed again next run (failed 1 of 3)
- publisher: ? → unsure (did not open)
- terms: NOTHING STATED · source none
- facts: status error Token Required

### Little Turtle_WTL1  ·    ·  from gis-hunter
- url: https://tiles.arcgis.com/tiles/V2n9y2bh8WyGKmfd/arcgis/rest/services/Little_Turtle_WTL1/MapServer
- WHY: did not open (error Token Required.): probed again next run (failed 1 of 3)
- publisher: ? → unsure (did not open)
- terms: NOTHING STATED · source none
- facts: status error Token Required.

### Lieber  ·    ·  from gis-hunter
- url: https://services2.arcgis.com/eEZvYWeDAf8dVYvQ/arcgis/rest/services/Lieber/FeatureServer
- WHY: did not open (error Token Required): probed again next run (failed 1 of 3)
- publisher: ? → unsure (did not open)
- terms: NOTHING STATED · source none
- facts: status error Token Required

### Florida National Scenic Trail Line  ·  None  ·  from gis-hunter
- url: https://services9.arcgis.com/soy9dtLUh5hYXg8U/arcgis/rest/services/FNST Master/FeatureServer
- WHY: did not open (bot error URL can't contain control characters. '/soy9dtLUh5hYXg8U/arcgis/rest/services/FNST Master/FeatureServer?f=json' (found a): probed again next run (failed 1 of 3)
- publisher: ? → unsure ()
- terms: ? · source ?
- facts: status bot error URL can't contain control characters. '/soy9dtLUh5hYXg8U/arcgis/rest/services/FNST Master/FeatureServer?f=json' (found a

### Lincoln_forestplan_alts_wilderness_AltE  ·    ·  from gis-hunter
- url: https://services9.arcgis.com/4ikJ2iF3itbByOVD/arcgis/rest/services/Lincoln_forestplan_alts_wilderness_AltE/FeatureServer
- WHY: did not open (error Token Required): probed again next run (failed 1 of 3)
- publisher: ? → unsure (did not open)
- terms: NOTHING STATED · source none
- facts: status error Token Required

### Flint River Access  ·    ·  from gis-hunter
- url: https://geoengine.utc.edu:6443/arcgis/rest/services/UTC/TVAwaterAccess/FeatureServer
- WHY: did not open (rest): probed again next run (failed 1 of 3)
- publisher: ? → unsure (did not open)
- terms: NOTHING STATED · source none
- facts: status rest

### Captain John Smith Chesapeake National Historic Trail  ·    ·  from gis-hunter
- url: https://services6.arcgis.com/UbKyMceXgEVeTOEF/arcgis/rest/services/Captain_John_Smith_Chesapeake_National_Historic_Trail/FeatureServer
- WHY: did not open (error Invalid URL): probed again next run (failed 1 of 3)
- publisher: ? → unsure (did not open)
- terms: NOTHING STATED · source none
- facts: status error Invalid URL

### Red Rocks Insta360 Oriented Imagery Video  ·  None  ·  from gis-hunter
- url: https://services1.arcgis.com/uujCiiEZAflDbdxE/arcgis/rest/services/Red Rocks Insta360 Video/FeatureServer
- WHY: did not open (bot error URL can't contain control characters. '/uujCiiEZAflDbdxE/arcgis/rest/services/Red Rocks Insta360 Video/FeatureServer?f=j): probed again next run (failed 1 of 3)
- publisher: ? → unsure ()
- terms: ? · source ?
- facts: status bot error URL can't contain control characters. '/uujCiiEZAflDbdxE/arcgis/rest/services/Red Rocks Insta360 Video/FeatureServer?f=j

### State Aquatic Management Area (AMA) Aquisitions  ·    ·  from gis-hunter
- url: https://enterprise-dev.gisdata.mn.gov/aghost/rest/services/us_mn_state_dnr/plan_mndnr_fisheries_acquisition/FeatureServer
- WHY: did not open (rest): probed again next run (failed 1 of 3)
- publisher: ? → unsure (did not open)
- terms: NOTHING STATED · source none
- facts: status rest

### Travel from Jessie's Office (45 Minutes - Mon@1730)  ·  None  ·  from gis-hunter
- url: https://services2.arcgis.com/VNo0ht0YPXJoI4oE/arcgis/rest/services/Travel from Jessie's Office (45 Minutes - Mon@1730)/FeatureServer
- WHY: did not open (bot error URL can't contain control characters. "/VNo0ht0YPXJoI4oE/arcgis/rest/services/Travel from Jessie's Office (45 Minutes - ): probed again next run (failed 1 of 3)
- publisher: ? → unsure ()
- terms: ? · source ?
- facts: status bot error URL can't contain control characters. "/VNo0ht0YPXJoI4oE/arcgis/rest/services/Travel from Jessie's Office (45 Minutes - 

### Travel from Jessie's Office (45 Minutes - no traffic)  ·  None  ·  from gis-hunter
- url: https://services2.arcgis.com/VNo0ht0YPXJoI4oE/arcgis/rest/services/Travel from Jessie's Office (45 Minutes - no traffic)/FeatureServer
- WHY: did not open (bot error URL can't contain control characters. "/VNo0ht0YPXJoI4oE/arcgis/rest/services/Travel from Jessie's Office (45 Minutes - ): probed again next run (failed 1 of 3)
- publisher: ? → unsure ()
- terms: ? · source ?
- facts: status bot error URL can't contain control characters. "/VNo0ht0YPXJoI4oE/arcgis/rest/services/Travel from Jessie's Office (45 Minutes - 

### Watershed of the Blanchard River  ·  None  ·  from gis-hunter
- url: https://services.arcgis.com/0c8NSBwqhllp50N7/arcgis/rest/services/Watershed of the Blanchard River/FeatureServer
- WHY: did not open (bot error URL can't contain control characters. '/0c8NSBwqhllp50N7/arcgis/rest/services/Watershed of the Blanchard River/FeatureSe): probed again next run (failed 1 of 3)
- publisher: ? → unsure ()
- terms: ? · source ?
- facts: status bot error URL can't contain control characters. '/0c8NSBwqhllp50N7/arcgis/rest/services/Watershed of the Blanchard River/FeatureSe

## REJECT (528)

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

### Public/CadastreParcels  ·  AU  ·  from harvester
- url: https://services.thelist.tas.gov.au/arcgis/rest/services/Public/CadastreParcels/MapServer/0
- WHY: judged again by the Oct 29 READY rule: closes 37, by name 2 (READY needs 3+ name matches and 25%+; never a coverage layer)
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
- WHY: judged again by the Oct 29 READY rule: closes 37, by name 0 (READY needs 3+ name matches and 25%+; never a coverage layer)
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

### Landgate_Public_Maps/Map_of_Bush_Fire_Prone_Areas_3  ·  AU  ·  from harvester
- url: https://public-services.slip.wa.gov.au/public/rest/services/Landgate_Public_Maps/Map_of_Bush_Fire_Prone_Areas_3/MapServer/7
- WHY: judged again by the Oct 29 READY rule: closes 16, by name 1 (READY needs 3+ name matches and 25%+; never a coverage layer)
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
- WHY: judged again by the Oct 29 READY rule: closes 2, by name 0 (READY needs 3+ name matches and 25%+; never a coverage layer)
- publisher: gis.environment.gov.au → official (government host gis.environment.gov.au)
- terms: CREDIT · source item page · "Australian Marine Parks © Commonwealth of Australia, Australian Government Department of Climate Change, Energy, th" · item https://gis.environment.gov.au/gispubmap/rest/services/ogc_services/Australian_Marine_Parks/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field NETNAME · 216 records · sample South-west / South-west / Temperate East
- closes: 2 of 60 tested missing parks (by name 0, pin only 2; 2871 of the area's 2871 missing parks lie in the layer's extent)
  - AU-0002 Willis Island National Park → polygon "Coral Sea"
  - AU-0046 Rowley Shoals Marine Park → polygon "North-west"

### ogc_services/Australian_Marine_Parks_Outer_Boundary/0  ·  AU  ·  from harvester
- url: https://gis.environment.gov.au/gispubmap/rest/services/ogc_services/Australian_Marine_Parks_Outer_Boundary/MapServer/0
- WHY: judged again by the Oct 29 READY rule: closes 2, by name 0 (READY needs 3+ name matches and 25%+; never a coverage layer)
- publisher: gis.environment.gov.au → official (government host gis.environment.gov.au)
- terms: OPEN · source item page · "This dataset is released under Creative Commons by Attribution 4.0 International (CC BY 4.0). Australian Marine Parks © Commonwealth of A" · item https://gis.environment.gov.au/gispubmap/rest/services/ogc_services/Australian_Marine_Parks_Outer_Boundary/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field NETNAME · 61 records · sample South-east / North / North-west
- closes: 2 of 60 tested missing parks (by name 0, pin only 2; 2864 of the area's 2871 missing parks lie in the layer's extent)
  - AU-0002 Willis Island National Park → polygon "Coral Sea"
  - AU-0046 Rowley Shoals Marine Park → polygon "North-west"

### ogc_services/Indigenous_Protected_Areas/0  ·  AU  ·  from harvester
- url: https://gis.environment.gov.au/gispubmap/rest/services/ogc_services/Indigenous_Protected_Areas/FeatureServer/0
- WHY: judged again by the Oct 29 READY rule: closes 2, by name 2 (READY needs 3+ name matches and 25%+; never a coverage layer)
- publisher: gis.environment.gov.au → official (government host gis.environment.gov.au)
- terms: CREDIT · source item page · "When using this dataset for analysis or mapping you must always acknowledge the National Indigenous Australians Agency and the Department of Climate Change, Energy," · item https://gis.environment.gov.au/gispubmap/rest/services/ogc_services/Indigenous_Protected_Areas/FeatureServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field NAME · 120 records · sample Angkum / Anindilyakwa / Anindilyakwa
- closes: 2 of 60 tested missing parks (by name 2, pin only 0; 2871 of the area's 2871 missing parks lie in the layer's extent)
  - AU-0004 Yawuru Birragun Conservation Park → polygon "Yawuru"
  - AU-0717 Vernon Islands Conservation Reserve → polygon "Tiwi Islands"

### ogc_services/World_Heritage_Areas/0  ·  AU  ·  from harvester
- url: https://gis.environment.gov.au/gispubmap/rest/services/ogc_services/World_Heritage_Areas/MapServer/0
- WHY: judged again by the Oct 29 READY rule: closes 2, by name 2 (READY needs 3+ name matches and 25%+; never a coverage layer)
- publisher: gis.environment.gov.au → official (government host gis.environment.gov.au)
- terms: OPEN · source item page · "Creative Commons by Attribution 4.0 International (CC BY 4.0) Australian Government Department of Agricult" · item https://gis.environment.gov.au/gispubmap/rest/services/ogc_services/World_Heritage_Areas/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field NAME · 49 records · sample Australian Convict Sites (Brickendon - Woolmers Buffer Zone) / Australian Convict Sites (Brickendon - Woolmers) / Australian Convict Sites (Old Government House and Domain Bu
- closes: 2 of 60 tested missing parks (by name 2, pin only 0; 2864 of the area's 2871 missing parks lie in the layer's extent)
  - AU-0042 Shark Bay Marine Park → polygon "Shark Bay, Western Australia"
  - AU-0058 Ningaloo Marine Park → polygon "Ningaloo Coast"

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

### Recreation Sites, Reserves and Interpretive Forests (details + closures)  ·  CA-BC  ·  from chat 9
- url: https://services6.arcgis.com/ubm4tcTYICKBpist/arcgis/rest/services/RecSitesReservesInterpForests_DetailsClosures_publicView/FeatureServer/0
- WHY: no polygons (esriGeometryPoint)
- publisher: Province of British Columbia (Recreation Sites and Trails BC) → official (government words: Province of)
- terms: CREDIT · source item page · "The content provided by this item is 'Copyright ©, Province of British Columbia. All rights reserved. The B.C.’s" · item https://www.arcgis.com/home/item.html?id=d6281a4d6a2044ec865d79cd1007e2f5 · owner databcfme · org B.C.'s Map Hub
- facts: arcgis-layer · esriGeometryPoint · name field PROJECT_NAME · 2285 records · last edit 2026-10-30
- closes: not probed

### Centennial Entertainment District Overlay (public view)  ·    ·  from gis-hunter
- url: https://services.arcgis.com/0H6bQdxd9223gQB5/arcgis/rest/services/CEDO_Collab/FeatureServer/1
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → official (government words: City of)
- terms: CREDIT · source item page · "of its format or the means of its transmission. THE DATA IS PROVIDED “AS IS” WITH NO GUARANTEE OR REPRESENTATION ABOUT THE ACCURACY, CURRENCY, SUITABILITY, PERFORMAN" · item https://www.arcgis.com/home/item.html?id=a045f22fd04f4e6cb7d6da61fbe1f265 · owner comadmin_comgis · org City of Midland-GIS 
- facts: arcgis-layer · esriGeometryPolygon · 1 records · last edit 2025-11-10
- closes: not probed

### OC Centennial Farm  ·    ·  from gis-hunter
- url: https://gisservices.oakgov.com/arcgisds/rest/services/Hosted/Centennial_Farm/FeatureServer/1
- WHY: NOT A PARK LAYER (coverage: parcels / census / index / planning / fire): it covers the whole land, so every pin falls inside (chat 11, Oct 29)
- publisher: ? → official (government words: County)
- terms: CREDIT · source item page · "http://www.oakgov.com/it/gis/Documents/GISDataPolicies.pdf" · item https://www.arcgis.com/home/item.html?id=68977e9f75534609989044a58e172fba · owner OCAGOAdmin · org Oakland County, Michigan
- facts: arcgis-layer · esriGeometryPolygon · name field sitezip · 18 records · last edit 2024-08-15 · sample 48301 / 48442 / 48363
- closes: not probed

### Fallen Timbers Battlefield Points of Interest  ·    ·  from gis-hunter
- url: https://services2.arcgis.com/i7Ls2H4uQGTYzm5D/arcgis/rest/services/Fallen_Timbers_Battlefield_Points_of_Interest/FeatureServer/0
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: CREDIT · source item page · "Old Topopgrapher Old Topopgrapher" · item https://www.arcgis.com/home/item.html?id=12d321a474394c189186d989973dd7b1 · owner topographer · org   The Old Topographer
- facts: arcgis-layer · esriGeometryPoint · name field Name · 27 records · last edit 2016-01-09
- closes: not probed

### LECL Lewis and Clark National Historic Trail Congressionally Designated Route  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/fBc8EJBxQRMcHlei/arcgis/rest/services/Lewis_and_Clark_National_Historic_Trail_Congressionally_Designated_Route/FeatureServer/0
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → official (a federal / national agency named)
- terms: CREDIT · source item page · "to use the related graphics as data. The National Park Service gives no warranty, expressed or implied, as to This centerline was created by the National Park Service Lew" · item https://www.arcgis.com/home/item.html?id=862abcecaa114974845b9ebe5bfa6e2f · owner rmcooper@nps.gov_nps · org National Park Service
- facts: arcgis-layer · esriGeometryPolyline · 62 records · last edit 2025-09-30
- overlap: same publisher as akht
- closes: not probed

### LECL Lewis and Clark NHT High Potential Historic Sites  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/fBc8EJBxQRMcHlei/arcgis/rest/services/HPHS/FeatureServer/0
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → official (a federal / national agency named)
- terms: CREDIT · source item page · "to use the related graphics as data. The National Park Service gives no warranty, expressed or implied, as to National Park Service National Park Service" · item https://www.arcgis.com/home/item.html?id=d3cb1870cd244ec1b1871d80371b1e70 · owner rmcooper@nps.gov_nps · org National Park Service
- facts: arcgis-layer · esriGeometryPoint · name field NAME · 93 records · last edit 2026-03-02
- overlap: same publisher as akht
- closes: not probed

### LECL Lewis and Clark Trail Visitor Centers and Museums  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/fBc8EJBxQRMcHlei/arcgis/rest/services/Lewis_and_Clark_Trail_Visitor_Centers_and_Museums/FeatureServer/0
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → official (a federal / national agency named)
- terms: CREDIT · source item page · "to use the related graphics as data. The National Park Service gives no warranty, expressed or implied, as to t National Park Service" · item https://www.arcgis.com/home/item.html?id=d234be9257b84fea91666c9c4c52b9c9 · owner rmcooper@nps.gov_nps · org National Park Service
- facts: arcgis-layer · esriGeometryPoint · name field SITE_NAME · 172 records · last edit 2026-10-01
- overlap: same publisher as akht
- closes: not probed

### Mormon Pioneer Trail  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/fBc8EJBxQRMcHlei/arcgis/rest/services/MOPI_NHT/FeatureServer/0
- WHY: the publisher closed it (internal / sign-in / by request)
- publisher: ? → official (a federal / national agency named)
- terms: CLOSED · source item page · "cal boundary, that crosses many ownership jurisdictions. Do not cross private land without permission. This data set should not be displayed or used at scales that exc" · item https://www.arcgis.com/home/item.html?id=fd6b3e2bb43f4854aa82b41117959de3 · owner ntirres_nps · org National Park Service
- facts: arcgis-layer · esriGeometryPolyline · 1 records · last edit 2025-08-04
- overlap: same publisher as akht
- closes: not probed

### Mormon Pioneer Trail (View Layer)  ·    ·  from gis-hunter
- url: https://services.arcgis.com/mMBpeYj0vPFotzbe/arcgis/rest/services/Mormon_Pioneer_Trail_view/FeatureServer/0
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=87b07395225240d1972a5b3cfa27702f · owner CameronScharrer · org Salt Lake City
- facts: arcgis-layer · esriGeometryPolyline · name field TRAIL_NAME · 3 records · last edit 2026-10-26
- closes: not probed

### Hillsdale flood pool _ LiDAR 2018  ·    ·  from gis-hunter
- url: https://services2.arcgis.com/ZOdjAzAQ2B0f85zi/arcgis/rest/services/Hillsdale_flood_pool___LiDAR_2018/FeatureServer/0
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=bcc610b6b67a43c78965c2af49570fc2 · owner ks_biosurvey · org  The University of Kansas
- facts: arcgis-layer · esriGeometryPolygon · 1 records · last edit 2023-01-23
- closes: not probed

### Hillsdale conservation pool _ LiDAR 2018  ·    ·  from gis-hunter
- url: https://services2.arcgis.com/ZOdjAzAQ2B0f85zi/arcgis/rest/services/Hillsdale_conservation_pool___LiDAR_2018/FeatureServer/0
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → hosted for an agency (a university account holds an agency layer)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=1ef882b8aa0e4b6c89d7558de6ac1bd0 · owner ks_biosurvey · org  The University of Kansas
- facts: arcgis-layer · esriGeometryPolygon · 1 records · last edit 2023-01-23
- closes: not probed

### Hillsdale Lake contours _ LiDAR 2018  ·    ·  from gis-hunter
- url: https://services2.arcgis.com/ZOdjAzAQ2B0f85zi/arcgis/rest/services/Hillsdale_Lake_contours___LiDAR_2018/FeatureServer/0
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=512a99ac168f4753a6832e51babccb4d · owner ks_biosurvey · org  The University of Kansas
- facts: arcgis-layer · esriGeometryPolyline · 6379 records · last edit 2023-01-23
- closes: not probed

### Federal Civilian Employment of George Washington PDC  ·    ·  from gis-hunter
- url: https://services5.arcgis.com/6MUPhDX27Ne3DNOw/arcgis/rest/services/Federal_Civilian_Employment_of_George_Washington_PDC_WFL1/FeatureServer/0
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → official (government words: Commission)
- terms: CREDIT · source item page · "Northern Virginia Regional Commission (NVRC) is not liable for any use of or reliance upon this map or data, or any information contained herein. Wh" · item https://www.arcgis.com/home/item.html?id=3b783d5545ff465e9073e7799b3f8489 · owner jkaneff_NVRC · org Northern Virginia Regional Commission 
- facts: arcgis-layer · esriGeometryPolygon · 7 records · last edit 2025-05-12
- closes: not probed

### Federal Civilian Employment of George Washington PDC  ·    ·  from gis-hunter
- url: https://services5.arcgis.com/6MUPhDX27Ne3DNOw/arcgis/rest/services/Federal_Civilian_Employment_of_George_Washington_PDC_WFL1/FeatureServer/1
- WHY: NOT A PARK LAYER (coverage: parcels / census / index / planning / fire): it covers the whole land, so every pin falls inside (chat 11, Oct 29)
- publisher: ? → official (government words: Commission)
- terms: CREDIT · source item page · "Northern Virginia Regional Commission (NVRC) is not liable for any use of or reliance upon this map or data, or any information contained herein. Wh" · item https://www.arcgis.com/home/item.html?id=3b783d5545ff465e9073e7799b3f8489 · owner jkaneff_NVRC · org Northern Virginia Regional Commission 
- facts: arcgis-layer · esriGeometryPolygon · name field LABEL1 · 5 records · last edit 2025-05-12 · sample GW / GW / GW
- closes: not probed

### Federal Civilian Employment of George Washington PDC  ·    ·  from gis-hunter
- url: https://services5.arcgis.com/6MUPhDX27Ne3DNOw/arcgis/rest/services/Federal_Civilian_Employment_of_George_Washington_PDC_WFL1/FeatureServer/2
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → official (government words: Commission)
- terms: CREDIT · source item page · "Northern Virginia Regional Commission (NVRC) is not liable for any use of or reliance upon this map or data, or any information contained herein. Wh" · item https://www.arcgis.com/home/item.html?id=3b783d5545ff465e9073e7799b3f8489 · owner jkaneff_NVRC · org Northern Virginia Regional Commission 
- facts: arcgis-layer · esriGeometryPolygon · 31 records · last edit 2025-05-12
- closes: not probed

### Federal Civilian Employment of George Washington PDC  ·    ·  from gis-hunter
- url: https://services5.arcgis.com/6MUPhDX27Ne3DNOw/arcgis/rest/services/Federal_Civilian_Employment_of_George_Washington_PDC_WFL1/FeatureServer/3
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → official (government words: Commission)
- terms: CREDIT · source item page · "Northern Virginia Regional Commission (NVRC) is not liable for any use of or reliance upon this map or data, or any information contained herein. Wh" · item https://www.arcgis.com/home/item.html?id=3b783d5545ff465e9073e7799b3f8489 · owner jkaneff_NVRC · org Northern Virginia Regional Commission 
- facts: arcgis-layer · esriGeometryPolygon · 31 records · last edit 2025-05-12
- closes: not probed

### CAFRA and Coastal Centers of New Jersey  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/QWdNfRs7lkPq4g4Q/arcgis/rest/services/CAFRA_and_Coastal_Centers_2023_of_New_Jersey/FeatureServer/9
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → official (government words: Bureau)
- terms: CREDIT · source item page · "of or to update the data. Terms of Agreement 1. All data is provided, as is, without any representation or warranty of any kind, implied, expressed or statutory incl" · item https://www.arcgis.com/home/item.html?id=be952e21e18b452cab435b19c8e0246e · owner NJDEPBGIS · org NJDEP Bureau of GIS
- facts: arcgis-layer · esriGeometryPolygon · 92 records · last edit 2026-07-28
- overlap: same publisher as sgnjb
- closes: not probed

### Coastal Area Facilities Review Act Boundary for New Jersey (polygon)  ·    ·  from gis-hunter
- url: https://mapsdep.nj.gov/arcgis/rest/services/Features/Land_CAFRA_coast/MapServer/0
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → official (government host mapsdep.nj.gov)
- terms: CREDIT · source item page · "NJDEP NJDEP" · item https://mapsdep.nj.gov/arcgis/rest/services/Features/Land_CAFRA_coast/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · 158 records
- overlap: same publisher as sgnja
- closes: not probed

### Coastal Area Facilities Review Act Boundary for New Jersey (linear)  ·    ·  from gis-hunter
- url: https://mapsdep.nj.gov/arcgis/rest/services/Features/Land_CAFRA_coast/MapServer/1
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → official (government host mapsdep.nj.gov)
- terms: CREDIT · source item page · "NJDEP" · item https://mapsdep.nj.gov/arcgis/rest/services/Features/Land_CAFRA_coast/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolyline · 299 records
- overlap: same publisher as sgnja
- closes: not probed

### Pinelands Wetlands 300 foot Buffer  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/nCm6SZaiGMuGX35l/arcgis/rest/services/Pinelands_Wetlands_Buffers_300_feet/FeatureServer/0
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → official (government words: Commission)
- terms: CREDIT · source item page · "bsequent field verification by the Pinelands Commission. The geodetic accuracy and precision of data contained within the coverage has not been developed nor verified b" · item https://www.arcgis.com/home/item.html?id=dac1159a961c41eeb416e0a42222f7d0 · owner NJPinelands · org New Jersey Pinelands Commission
- facts: arcgis-layer · esriGeometryPolygon · 5028 records · last edit 2025-05-22
- closes: not probed

### Pinelands Wetlands  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/nCm6SZaiGMuGX35l/arcgis/rest/services/Pinelands_Wetlands/FeatureServer/0
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → official (government words: Commission)
- terms: CREDIT · source item page · "The geodetic accuracy and precision of data contained within the coverage has not been developed nor verified b" · item https://www.arcgis.com/home/item.html?id=44510d394a5949bab46439c6fdff2721 · owner NJPinelands · org New Jersey Pinelands Commission
- facts: arcgis-layer · esriGeometryPolygon · 76023 records · last edit 2025-05-22
- closes: not probed

### Audubon Pine Island Sanctuary  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/lDFzr3JyGEn5Eymu/arcgis/rest/services/Audubon_Pine_Island_Sanctuary/FeatureServer/1
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (audubon in the publisher words)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=c59fa6fc121a48e2bcdae01df90a80c0 · owner joanna.grand@audubon.org_audubon · org National Audubon Society
- facts: arcgis-layer · esriGeometryPolygon · name field MUNIT · 56 records · last edit 2020-04-02 · sample   /   /  
- closes: not probed

### Maryland Highways to Black History  ·    ·  from gis-hunter
- url: https://services.arcgis.com/njFNhDsUCentVYJW/arcgis/rest/services/Black_History_Month_Tour/FeatureServer/0
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → official (government words: Department)
- terms: CREDIT · source item page · "This data is provided “AS IS” without warranty of any kind, either expressed or implied. The Maryland Department of Tr" · item https://www.arcgis.com/home/item.html?id=57d46b7424e04b36b56f49e400c7b2db · owner MDOTSHA.GIS · org ArcGIS Online for Maryland
- facts: arcgis-layer · esriGeometryPoint · name field NAME · 62 records · last edit 2026-02-11
- closes: not probed

### Historical County Population (1969 - 2019) by Race (White, Black, Other Race)  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/4yjifSiIG17X0gW4/arcgis/rest/services/Historical_County_Population_1969_2019/FeatureServer
- WHY: the service lists no polygon layers
- publisher: ? → unsure (no layers)
- terms: NOTHING STATED · source none
- facts: arcgis-service

### Benchmarks - City of Palmetto  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/L2Neyx2ylSeTBS0F/arcgis/rest/services/Palmetto_Benchmarks/FeatureServer/0
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → official (government words: City of)
- terms: CREDIT · source item page · "GIS Staff City of Palmetto, FL This map was developed by the GIS Staff at the Palmetto CRA. It is provided for general reference and it is not war" · item https://www.arcgis.com/home/item.html?id=cb4b08cf67ff43bf805a757723b1eae2 · owner CityofPalmettoFl · org City of Palmetto, Florida
- facts: arcgis-layer · esriGeometryPoint · name field BMNAME · 447 records · last edit 2018-07-22
- closes: not probed

### Wild Turkey Transfer_WFL1  ·    ·  from gis-hunter
- url: https://services.arcgis.com/QVENGdaPbd4LUkLV/arcgis/rest/services/Wild_Turkey_Transfer_WFL1/FeatureServer/5
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → official (a federal / national agency named)
- terms: CREDIT · source item page · "herein. While the Service makes every reasonable effort to ensure the accuracy and completeness of data provided for distribution, it may not have the necessary accurac" · item https://www.arcgis.com/home/item.html?id=ac8f560b1f4c4f889c2e76691be5a33e · owner elena_campbell@fws.gov_fws · org U.S. Fish & Wildlife Service
- facts: arcgis-layer · esriGeometryPolygon · 1 records · last edit 2026-05-14
- overlap: same publisher as sgazd
- closes: not probed

### Wild Turkey Transfer_WFL1  ·    ·  from gis-hunter
- url: https://services.arcgis.com/QVENGdaPbd4LUkLV/arcgis/rest/services/Wild_Turkey_Transfer_WFL1/FeatureServer/6
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → official (a federal / national agency named)
- terms: CREDIT · source item page · "herein. While the Service makes every reasonable effort to ensure the accuracy and completeness of data provided for distribution, it may not have the necessary accurac" · item https://www.arcgis.com/home/item.html?id=ac8f560b1f4c4f889c2e76691be5a33e · owner elena_campbell@fws.gov_fws · org U.S. Fish & Wildlife Service
- facts: arcgis-layer · esriGeometryPolygon · 1 records · last edit 2026-05-14
- overlap: same publisher as sgazd
- closes: not probed

### Wild Turkey Transfer_WFL1  ·    ·  from gis-hunter
- url: https://services.arcgis.com/QVENGdaPbd4LUkLV/arcgis/rest/services/Wild_Turkey_Transfer_WFL1/FeatureServer/7
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → official (a federal / national agency named)
- terms: CREDIT · source item page · "herein. While the Service makes every reasonable effort to ensure the accuracy and completeness of data provided for distribution, it may not have the necessary accurac" · item https://www.arcgis.com/home/item.html?id=ac8f560b1f4c4f889c2e76691be5a33e · owner elena_campbell@fws.gov_fws · org U.S. Fish & Wildlife Service
- facts: arcgis-layer · esriGeometryPolygon · 14 records · last edit 2026-05-14
- overlap: same publisher as sgazd
- closes: not probed

### Wild Turkey Transfer_WFL1  ·    ·  from gis-hunter
- url: https://services.arcgis.com/QVENGdaPbd4LUkLV/arcgis/rest/services/Wild_Turkey_Transfer_WFL1/FeatureServer/12
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → official (a federal / national agency named)
- terms: CREDIT · source item page · "herein. While the Service makes every reasonable effort to ensure the accuracy and completeness of data provided for distribution, it may not have the necessary accurac" · item https://www.arcgis.com/home/item.html?id=ac8f560b1f4c4f889c2e76691be5a33e · owner elena_campbell@fws.gov_fws · org U.S. Fish & Wildlife Service
- facts: arcgis-layer · esriGeometryPolygon · 2 records · last edit 2026-05-14
- overlap: same publisher as sgazd
- closes: not probed

### Wild Turkey Transfer_WFL1  ·    ·  from gis-hunter
- url: https://services.arcgis.com/QVENGdaPbd4LUkLV/arcgis/rest/services/Wild_Turkey_Transfer_WFL1/FeatureServer/13
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → official (a federal / national agency named)
- terms: CREDIT · source item page · "herein. While the Service makes every reasonable effort to ensure the accuracy and completeness of data provided for distribution, it may not have the necessary accurac" · item https://www.arcgis.com/home/item.html?id=ac8f560b1f4c4f889c2e76691be5a33e · owner elena_campbell@fws.gov_fws · org U.S. Fish & Wildlife Service
- facts: arcgis-layer · esriGeometryPolygon · 1 records · last edit 2026-05-14
- overlap: same publisher as sgazd
- closes: not probed

### Wild Turkey Program in Vermont - Hunting Zones  ·    ·  from gis-hunter
- url: https://services.arcgis.com/QVENGdaPbd4LUkLV/arcgis/rest/services/Wild_Turkey_Program_in_Vermont_WFL1/FeatureServer/12
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → official (a federal / national agency named)
- terms: CREDIT · source item page · "herein. While the Service makes every reasonable effort to ensure the accuracy and completeness of data provided for distribution, it may not have the necessary accurac" · item https://www.arcgis.com/home/item.html?id=6cab8c11e8414522b8ce9a0692bcb27d · owner elena_campbell@fws.gov_fws · org U.S. Fish & Wildlife Service
- facts: arcgis-layer · esriGeometryPolygon · 3 records · last edit 2026-05-20
- overlap: same publisher as sgazd
- closes: not probed

### Wild Turkey Program in Vermont - Hunting Zones  ·    ·  from gis-hunter
- url: https://services.arcgis.com/QVENGdaPbd4LUkLV/arcgis/rest/services/Wild_Turkey_Program_in_Vermont_WFL1/FeatureServer/11
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → official (a federal / national agency named)
- terms: CREDIT · source item page · "herein. While the Service makes every reasonable effort to ensure the accuracy and completeness of data provided for distribution, it may not have the necessary accurac" · item https://www.arcgis.com/home/item.html?id=6cab8c11e8414522b8ce9a0692bcb27d · owner elena_campbell@fws.gov_fws · org U.S. Fish & Wildlife Service
- facts: arcgis-layer · esriGeometryPolygon · 4 records · last edit 2026-05-20
- overlap: same publisher as sgazd
- closes: not probed

### Wild Turkey Program in Vermont - Hunting Zones  ·    ·  from gis-hunter
- url: https://services.arcgis.com/QVENGdaPbd4LUkLV/arcgis/rest/services/Wild_Turkey_Program_in_Vermont_WFL1/FeatureServer/4
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → official (a federal / national agency named)
- terms: CREDIT · source item page · "herein. While the Service makes every reasonable effort to ensure the accuracy and completeness of data provided for distribution, it may not have the necessary accurac" · item https://www.arcgis.com/home/item.html?id=6cab8c11e8414522b8ce9a0692bcb27d · owner elena_campbell@fws.gov_fws · org U.S. Fish & Wildlife Service
- facts: arcgis-layer · esriGeometryPolygon · 1 records · last edit 2026-03-24
- overlap: same publisher as sgazd
- closes: not probed

### Wild Turkey Program in Vermont - Hunting Zones  ·    ·  from gis-hunter
- url: https://services.arcgis.com/QVENGdaPbd4LUkLV/arcgis/rest/services/Wild_Turkey_Program_in_Vermont_WFL1/FeatureServer/1
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → official (a federal / national agency named)
- terms: CREDIT · source item page · "herein. While the Service makes every reasonable effort to ensure the accuracy and completeness of data provided for distribution, it may not have the necessary accurac" · item https://www.arcgis.com/home/item.html?id=6cab8c11e8414522b8ce9a0692bcb27d · owner elena_campbell@fws.gov_fws · org U.S. Fish & Wildlife Service
- facts: arcgis-layer · esriGeometryPolygon · 1 records · last edit 2026-03-24
- overlap: same publisher as sgazd
- closes: not probed

### Wild Turkey Program in Vermont - Hunting Zones  ·    ·  from gis-hunter
- url: https://services.arcgis.com/QVENGdaPbd4LUkLV/arcgis/rest/services/Wild_Turkey_Program_in_Vermont_WFL1/FeatureServer/0
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → official (a federal / national agency named)
- terms: CREDIT · source item page · "herein. While the Service makes every reasonable effort to ensure the accuracy and completeness of data provided for distribution, it may not have the necessary accurac" · item https://www.arcgis.com/home/item.html?id=6cab8c11e8414522b8ce9a0692bcb27d · owner elena_campbell@fws.gov_fws · org U.S. Fish & Wildlife Service
- facts: arcgis-layer · esriGeometryPolygon · 14 records · last edit 2026-03-24
- overlap: same publisher as sgazd
- closes: not probed

### Wild Turkey Program in Vermont - Hunting Zones  ·    ·  from gis-hunter
- url: https://services.arcgis.com/QVENGdaPbd4LUkLV/arcgis/rest/services/Wild_Turkey_Program_in_Vermont_WFL1/FeatureServer/5
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → official (a federal / national agency named)
- terms: CREDIT · source item page · "herein. While the Service makes every reasonable effort to ensure the accuracy and completeness of data provided for distribution, it may not have the necessary accurac" · item https://www.arcgis.com/home/item.html?id=6cab8c11e8414522b8ce9a0692bcb27d · owner elena_campbell@fws.gov_fws · org U.S. Fish & Wildlife Service
- facts: arcgis-layer · esriGeometryPolygon · 2 records · last edit 2026-03-24
- overlap: same publisher as sgazd
- closes: not probed

### Wild Turkey Program in Vermont - Hunting Zones  ·    ·  from gis-hunter
- url: https://services.arcgis.com/QVENGdaPbd4LUkLV/arcgis/rest/services/Wild_Turkey_Program_in_Vermont_WFL1/FeatureServer/6
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → official (a federal / national agency named)
- terms: CREDIT · source item page · "herein. While the Service makes every reasonable effort to ensure the accuracy and completeness of data provided for distribution, it may not have the necessary accurac" · item https://www.arcgis.com/home/item.html?id=6cab8c11e8414522b8ce9a0692bcb27d · owner elena_campbell@fws.gov_fws · org U.S. Fish & Wildlife Service
- facts: arcgis-layer · esriGeometryPolygon · 1 records · last edit 2026-03-24
- overlap: same publisher as sgazd
- closes: not probed

### Wild Turkey Brood Survey  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/BEFhRGD6ppzvv08z/arcgis/rest/services/service_e65232a5431142abbdb7bb7489b7804e/FeatureServer/0
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → official (government words: Department)
- terms: CREDIT · source item page · "Although all data in this data set have been compiled by the Missouri Department of Conservation, no warranty, expressed or implied, is made by th" · item https://www.arcgis.com/home/item.html?id=78dc1369ea074ad196d32ca9e27c650d · owner MDC_Resource_Science · org Missouri Department of Conservation Mapping Service
- facts: arcgis-layer · esriGeometryPoint · last edit 2026-10-29
- closes: not probed

### Audubon Chapter Boundaries Public View  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/lDFzr3JyGEn5Eymu/arcgis/rest/services/Audubon_Chapter_Boundaries_Public_View/FeatureServer/0
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (Audubon in the publisher words)
- terms: CREDIT · source item page · "Compiled by Connor Bailey Compiled by Connor Bailey" · item https://www.arcgis.com/home/item.html?id=d0dbf1767d2b4f2ea6020666d37b884c · owner Audubon_GIS · org National Audubon Society
- facts: arcgis-layer · esriGeometryPolygon · name field Website · 422 records · last edit 2026-10-25 · sample https://www.prairiefalconaudubon.com / https://www.putnamhighlandsaudubon.org/ / http://www.clearwateraudubonsociety.org/
- closes: not probed

### Audubon's Cottontail Range - CWHR M047 [ds1841]  ·    ·  from gis-hunter
- url: https://services2.arcgis.com/Uq9r85Potqm3MfRV/arcgis/rest/services/biosds1841_fpu/FeatureServer/0
- WHY: NOT A PARK LAYER (coverage: parcels / census / index / planning / fire): it covers the whole land, so every pin falls inside (chat 11, Oct 29)
- publisher: ? → official (government words: Department)
- terms: OPEN · source item page · "License: This work is licensed under Creative Commons Attribution 4.0 International License ( https://creativecommons.org/licenses/by/4.0/ ). U" · item https://www.arcgis.com/home/item.html?id=d1454d917b554f08a60cac9e4e51fffa · owner BIOS_Admin · org California Department of Fish and Wildlife
- facts: arcgis-layer · esriGeometryPolygon · name field SName · 1 records · last edit 2020-03-11 · sample Sylvilagus audubonii
- overlap: same publisher as sgcaa
- closes: not probed

### Audubon Coast Sites  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/lDFzr3JyGEn5Eymu/arcgis/rest/services/Coast_Sites_GV/FeatureServer/0
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (Audubon in the publisher words)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=bf8072135f87465386c0117411fa73cc · owner GIS_Help_audubon · org National Audubon Society
- facts: arcgis-layer · esriGeometryPoint · name field SiteName · 1090 records · last edit 2019-04-23
- closes: not probed

### Saint Bernard Preparatory School Trail Map  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/RpVCghfSj7XHqAKQ/arcgis/rest/services/Saint_Bernard_Preparatory_School_Trail_Map/FeatureServer/2
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=b14468de6e4545b68b3ed20c086cc81c · owner sandecm0 · org University of the South GIS
- facts: arcgis-layer · esriGeometryPolygon · name field Name · 24 records · last edit 2024-04-15 · sample Fazi-Richard Athletic Center / Soccer Concessions / Field Storage
- closes: not probed

### Saint Bernard Preparatory School Trail Map  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/RpVCghfSj7XHqAKQ/arcgis/rest/services/Saint_Bernard_Preparatory_School_Trail_Map/FeatureServer/3
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=b14468de6e4545b68b3ed20c086cc81c · owner sandecm0 · org University of the South GIS
- facts: arcgis-layer · esriGeometryPolygon · name field FULLNAME · 2932 records · last edit 2024-04-15 · sample   /   /  
- closes: not probed

### Saint Bernard  ·    ·  from gis-hunter
- url: https://services5.arcgis.com/uVUBD3VA9JxTzTy4/arcgis/rest/services/Saint_Bernard/FeatureServer/0
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=bc40bac80be448d28eba41ed5742a778 · owner philhaas
- facts: arcgis-layer · esriGeometryPolygon · 1 records · last edit 2021-05-11
- closes: not probed

### First Nation Heritage Routes  ·    ·  from gis-hunter
- url: https://mapservices.gov.yk.ca/arcgis/rest/services/GeoYukon/GY_CultureHeritage/MapServer/1
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → official (government host mapservices.gov.yk.ca)
- terms: CREDIT · source item page · "Government of Yukon" · item https://mapservices.gov.yk.ca/arcgis/rest/services/GeoYukon/GY_CultureHeritage/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolyline · name field ROUTE_NAME · 398 records
- overlap: same publisher as Yukon campgr
- closes: not probed

### Junction & Breakwater  ·    ·  from gis-hunter
- url: https://services7.arcgis.com/sbCtNPX9WTwhwh3s/arcgis/rest/services/DNREC_Trails_2021/FeatureServer/0
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=666d59f285a747009ff7f475f0f2a33f · owner DelawareGreenwaysInc
- facts: arcgis-layer · esriGeometryPolyline · name field TRAIL_NAME · 6129 records · last edit 2021-11-12
- closes: not probed

### Northern Delaware Greenway Trail  ·    ·  from gis-hunter
- url: https://services7.arcgis.com/sbCtNPX9WTwhwh3s/arcgis/rest/services/FTND_Northern_Delaware_Greenway_Trail/FeatureServer/0
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=edfbb20142434123bb1ef76ac8cd9c13 · owner DelawareGreenwaysInc
- facts: arcgis-layer · esriGeometryPolyline · name field NAME · 12 records · last edit 2019-10-08
- closes: not probed

### Northern_Delaware_Greenway  ·    ·  from gis-hunter
- url: https://services7.arcgis.com/sbCtNPX9WTwhwh3s/arcgis/rest/services/Northern_Delaware_Greenway/FeatureServer/0
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=504b9399a7c0416d9b2c66c4ea24f71d · owner DelawareGreenwaysInc
- facts: arcgis-layer · esriGeometryPolyline · name field NAME · 13 records · last edit 2018-10-08
- closes: not probed

### Pomeroy_Trail_and_other_Trails_in_Newark  ·    ·  from gis-hunter
- url: https://services.arcgis.com/DCPX1PuggGH4Tici/arcgis/rest/services/Pomeroy_Trail_and_other_Trails_in_Newark/FeatureServer/0
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=c540a4d7cea44a6a92c008bbe2c5d3d9 · owner swingel_udel · org University of Delaware
- facts: arcgis-layer · esriGeometryPoint · name field name · 17 records · last edit 2017-04-27
- closes: not probed

### PLANNINGCADASTRE_overlay_capitol_view_corridors  ·    ·  from gis-hunter
- url: https://services.arcgis.com/0L95CJ0VTaxqcmED/arcgis/rest/services/PLANNINGCADASTRE_overlay_capitol_view_corridors/FeatureServer/0
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (Geospatial Services in the publisher words)
- terms: CREDIT · source item page · "imate relative location of property boundaries. This product has been produced by the City of Austin for the sole purpose of geographic reference. No warranty is made by t" · item https://www.arcgis.com/home/item.html?id=38fd0435ccc54b499610c4913ccc9866 · owner CTM.Publisher · org City of Austin
- facts: arcgis-layer · esriGeometryPolygon · name field ZONING_OVERLAY_NAME · 35 records · last edit 2025-08-26 · sample CAPITOL VIEW CORRIDORS / CAPITOL VIEW CORRIDORS / CAPITOL VIEW CORRIDORS
- closes: not probed

### Capitol Campus points  ·    ·  from gis-hunter
- url: https://services9.arcgis.com/VatvCKAYJJVi8sva/arcgis/rest/services/Capitol_Campus_points/FeatureServer/0
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → official (government words: Department)
- terms: CREDIT · source item page · "e to include accurate Data, DES makes no representation regarding the accuracy, adequacy, reliability, or completeness of the Data. Accordingly, prior to taking any act" · item https://www.arcgis.com/home/item.html?id=3b4c19f5ebf045c6bb0e5db13a37ceeb · owner DES_GIS_Support · org Washington State Department of Enterprise Services
- facts: arcgis-layer · esriGeometryPoint · name field TITLE · 26 records · last edit 2026-03-31
- closes: not probed

### Capitol Campus points  ·    ·  from gis-hunter
- url: https://services9.arcgis.com/VatvCKAYJJVi8sva/arcgis/rest/services/Capitol_Campus_points/FeatureServer/1
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → official (government words: Department)
- terms: CREDIT · source item page · "e to include accurate Data, DES makes no representation regarding the accuracy, adequacy, reliability, or completeness of the Data. Accordingly, prior to taking any act" · item https://www.arcgis.com/home/item.html?id=3b4c19f5ebf045c6bb0e5db13a37ceeb · owner DES_GIS_Support · org Washington State Department of Enterprise Services
- facts: arcgis-layer · esriGeometryPoint · name field TITLE · 3 records · last edit 2025-08-27
- closes: not probed

### Capitol Campus points  ·    ·  from gis-hunter
- url: https://services9.arcgis.com/VatvCKAYJJVi8sva/arcgis/rest/services/Capitol_Campus_points/FeatureServer/16
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → official (government words: Department)
- terms: CREDIT · source item page · "e to include accurate Data, DES makes no representation regarding the accuracy, adequacy, reliability, or completeness of the Data. Accordingly, prior to taking any act" · item https://www.arcgis.com/home/item.html?id=3b4c19f5ebf045c6bb0e5db13a37ceeb · owner DES_GIS_Support · org Washington State Department of Enterprise Services
- facts: arcgis-layer · esriGeometryPoint · name field TITLE · 12 records · last edit 2025-08-16
- closes: not probed

### Capitol Campus points  ·    ·  from gis-hunter
- url: https://services9.arcgis.com/VatvCKAYJJVi8sva/arcgis/rest/services/Capitol_Campus_points/FeatureServer/17
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → official (government words: Department)
- terms: CREDIT · source item page · "e to include accurate Data, DES makes no representation regarding the accuracy, adequacy, reliability, or completeness of the Data. Accordingly, prior to taking any act" · item https://www.arcgis.com/home/item.html?id=3b4c19f5ebf045c6bb0e5db13a37ceeb · owner DES_GIS_Support · org Washington State Department of Enterprise Services
- facts: arcgis-layer · esriGeometryPoint · name field TITLE · 49 records · last edit 2025-08-27
- closes: not probed

### Capitol Campus points  ·    ·  from gis-hunter
- url: https://services9.arcgis.com/VatvCKAYJJVi8sva/arcgis/rest/services/Capitol_Campus_points/FeatureServer/4
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → official (government words: Department)
- terms: CREDIT · source item page · "e to include accurate Data, DES makes no representation regarding the accuracy, adequacy, reliability, or completeness of the Data. Accordingly, prior to taking any act" · item https://www.arcgis.com/home/item.html?id=3b4c19f5ebf045c6bb0e5db13a37ceeb · owner DES_GIS_Support · org Washington State Department of Enterprise Services
- facts: arcgis-layer · esriGeometryPoint · name field TITLE · 26 records · last edit 2026-03-30
- closes: not probed

### Capitol Campus points  ·    ·  from gis-hunter
- url: https://services9.arcgis.com/VatvCKAYJJVi8sva/arcgis/rest/services/Capitol_Campus_points/FeatureServer/5
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → official (government words: Department)
- terms: CREDIT · source item page · "e to include accurate Data, DES makes no representation regarding the accuracy, adequacy, reliability, or completeness of the Data. Accordingly, prior to taking any act" · item https://www.arcgis.com/home/item.html?id=3b4c19f5ebf045c6bb0e5db13a37ceeb · owner DES_GIS_Support · org Washington State Department of Enterprise Services
- facts: arcgis-layer · esriGeometryPoint · name field TITLE · 13 records · last edit 2026-03-30
- closes: not probed

### Capitol Campus points  ·    ·  from gis-hunter
- url: https://services9.arcgis.com/VatvCKAYJJVi8sva/arcgis/rest/services/Capitol_Campus_points/FeatureServer/6
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → official (government words: Department)
- terms: CREDIT · source item page · "e to include accurate Data, DES makes no representation regarding the accuracy, adequacy, reliability, or completeness of the Data. Accordingly, prior to taking any act" · item https://www.arcgis.com/home/item.html?id=3b4c19f5ebf045c6bb0e5db13a37ceeb · owner DES_GIS_Support · org Washington State Department of Enterprise Services
- facts: arcgis-layer · esriGeometryPoint · name field TITLE · 4 records · last edit 2025-03-25
- closes: not probed

### Capitol Campus points  ·    ·  from gis-hunter
- url: https://services9.arcgis.com/VatvCKAYJJVi8sva/arcgis/rest/services/Capitol_Campus_points/FeatureServer/3
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → official (government words: Department)
- terms: CREDIT · source item page · "e to include accurate Data, DES makes no representation regarding the accuracy, adequacy, reliability, or completeness of the Data. Accordingly, prior to taking any act" · item https://www.arcgis.com/home/item.html?id=3b4c19f5ebf045c6bb0e5db13a37ceeb · owner DES_GIS_Support · org Washington State Department of Enterprise Services
- facts: arcgis-layer · esriGeometryPoint · name field LABEL · 1 records · last edit 2025-03-25
- closes: not probed

### PLANNINGCADASTRE_overlay_capitol_dominance  ·    ·  from gis-hunter
- url: https://services.arcgis.com/0L95CJ0VTaxqcmED/arcgis/rest/services/PLANNINGCADASTRE_overlay_capitol_dominance/FeatureServer/0
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (Geospatial Services in the publisher words)
- terms: CREDIT · source item page · "imate relative location of property boundaries. This product has been produced by the City of Austin for the sole purpose of geographic reference. No warranty is made by t" · item https://www.arcgis.com/home/item.html?id=3a07c9d56a99421e9d3e2346180b49ca · owner CTM.Publisher · org City of Austin
- facts: arcgis-layer · esriGeometryPolygon · name field ZONING_OVERLAY_NAME · 1 records · last edit 2023-09-11 · sample CAPITOL DOMINANCE
- closes: not probed

### Two Foot Topographic Contours - Bow Bog Brook-Merrimack River (0107000603) - smoothed  ·    ·  from gis-hunter
- url: https://nhgeodata.unh.edu/hosting/rest/services/Hosted/EDP_LiDAR_Contours_2ft_01070006_smooth/FeatureServer/5
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: NOTHING STATED · source item page · item https://nhgeodata.unh.edu/hosting/rest/services/Hosted/EDP_LiDAR_Contours_2ft_01070006_smooth/FeatureServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolyline · 127755 records
- overlap: same publisher as nhc
- closes: not probed

### Mahoosuc_Ridge_to_The_River_Challenge_Race_Map  ·    ·  from gis-hunter
- url: https://services5.arcgis.com/lqtrRsdwvTbuk1xO/arcgis/rest/services/Mahoosuc_Ridge_to_The_River_Challenge_Race_Map/FeatureServer/0
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=845af8032b2f4a368f121d66af378a60 · owner kirksiegel
- facts: arcgis-layer · esriGeometryPoint · name field name · 16 records · last edit 2019-09-08
- closes: not probed

### Wild and Scenic Designated Buffer  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/yzNawWwHQXYQkxUq/arcgis/rest/services/Wild_and_Scenic_Designated_Buffer/FeatureServer/3
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=2b4e8b5bf9964a3bb95951da9c20af4b · owner wrwa_staff1 · org Westfield State University
- facts: arcgis-layer · esriGeometryPolygon · 1 records · last edit 2022-01-29
- closes: not probed

### Wild and Scenic Core Habitat  ·    ·  from gis-hunter
- url: https://services8.arcgis.com/481TDj9veSRE1m1c/arcgis/rest/services/Wild_and_Scenic_Core_Habitat/FeatureServer/0
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: CREDIT · source item page · "https://docs.digital.mass.gov/dataset/massgis-data-layers" · item https://www.arcgis.com/home/item.html?id=929e6959f3bb4e2f8722f71c897ba9f5 · owner khartlage
- facts: arcgis-layer · esriGeometryPolygon · 34 records · last edit 2020-07-24
- closes: not probed

### Wild and Scenic Aquatic Core  ·    ·  from gis-hunter
- url: https://services8.arcgis.com/481TDj9veSRE1m1c/arcgis/rest/services/Wild_and_Scenic_Aquatic_Core/FeatureServer/0
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: CREDIT · source item page · "https://docs.digital.mass.gov/dataset/massgis-data-layers" · item https://www.arcgis.com/home/item.html?id=7cc9ff251f6243ce81dddfb5362b900c · owner khartlage
- facts: arcgis-layer · esriGeometryPolygon · 33 records · last edit 2020-07-24
- closes: not probed

### Nashua River Wild and Scenic Towns  ·    ·  from gis-hunter
- url: https://services8.arcgis.com/481TDj9veSRE1m1c/arcgis/rest/services/Nashua_River_Wild_and_Scenic_Towns/FeatureServer/0
- WHY: nothing stated about use on the item page or the service
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=e913fb5a50974c979c4823b2794eb02b · owner khartlage
- facts: arcgis-layer · esriGeometryPolygon · name field pbpNAME · 11 records · last edit 2020-04-13 · sample   / Hollis / Brookline
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### East Brainard Elementary School Walkshed_WFL1  ·    ·  from gis-hunter
- url: https://services2.arcgis.com/OIAIimblRxPs0xxc/arcgis/rest/services/East_Brainard_Elementary_School_Walkshed_WFL1/FeatureServer/1
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (School in the publisher words)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=1d990cad93754a628cf51cc46f185594 · owner Kayla.Ferguson_CHATTGIS · org City of Chattanooga
- facts: arcgis-layer · esriGeometryPolygon · name field zone_name · 1 records · last edit 2022-03-14 · sample Residential Zone
- closes: not probed

### East Brainard Elementary School Walkshed_WFL1  ·    ·  from gis-hunter
- url: https://services2.arcgis.com/OIAIimblRxPs0xxc/arcgis/rest/services/East_Brainard_Elementary_School_Walkshed_WFL1/FeatureServer/2
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (School in the publisher words)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=1d990cad93754a628cf51cc46f185594 · owner Kayla.Ferguson_CHATTGIS · org City of Chattanooga
- facts: arcgis-layer · esriGeometryPolygon · name field label · 7878 records · last edit 2022-03-14 · sample None / None / None
- closes: not probed

### East Brainard Elementary School Walkshed_WFL1  ·    ·  from gis-hunter
- url: https://services2.arcgis.com/OIAIimblRxPs0xxc/arcgis/rest/services/East_Brainard_Elementary_School_Walkshed_WFL1/FeatureServer/3
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (School in the publisher words)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=1d990cad93754a628cf51cc46f185594 · owner Kayla.Ferguson_CHATTGIS · org City of Chattanooga
- facts: arcgis-layer · esriGeometryPolygon · name field Name · 1 records · last edit 2022-03-14 · sample 0 - 2640
- closes: not probed

### Brainard Cemetery Aerial Image 2012  ·    ·  from gis-hunter
- url: https://tiles.arcgis.com/tiles/McQ0OlIABe29rJJy/arcgis/rest/services/Brainard_Cemetery_Aerial_Image_2012/MapServer/0
- WHY: no polygons (no geometry)
- publisher: ? → official (a government word of the country: Parks)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=a34fb42e27784f06a19905ad29cb0192 · owner OregonMetro.ParksNature · org Metro
- facts: arcgis-layer
- closes: not probed

### Shavano_Tabeguache_WFL1  ·    ·  from gis-hunter
- url: https://services2.arcgis.com/RQcpPaCpMAXzUI5g/arcgis/rest/services/Shavano_Tabeguache_WFL1/FeatureServer/1
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=cc333297358d416bbb6d087840dc7e89 · owner rre4601@rit.edu_RITArcGIS
- facts: arcgis-layer · esriGeometryPolyline · 1 records · last edit 2021-12-09
- closes: not probed

### Shavano_Tabeguache_WFL1  ·    ·  from gis-hunter
- url: https://services2.arcgis.com/RQcpPaCpMAXzUI5g/arcgis/rest/services/Shavano_Tabeguache_WFL1/FeatureServer/2
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=cc333297358d416bbb6d087840dc7e89 · owner rre4601@rit.edu_RITArcGIS
- facts: arcgis-layer · esriGeometryPolyline · 1 records · last edit 2021-12-09
- closes: not probed

### Shavano_Tabeguache_WFL1  ·    ·  from gis-hunter
- url: https://services2.arcgis.com/RQcpPaCpMAXzUI5g/arcgis/rest/services/Shavano_Tabeguache_WFL1/FeatureServer/3
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=cc333297358d416bbb6d087840dc7e89 · owner rre4601@rit.edu_RITArcGIS
- facts: arcgis-layer · esriGeometryPolyline · 1 records · last edit 2021-12-09
- closes: not probed

### Shavano_Tabeguache_WFL1  ·    ·  from gis-hunter
- url: https://services2.arcgis.com/RQcpPaCpMAXzUI5g/arcgis/rest/services/Shavano_Tabeguache_WFL1/FeatureServer/4
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=cc333297358d416bbb6d087840dc7e89 · owner rre4601@rit.edu_RITArcGIS
- facts: arcgis-layer · esriGeometryPolyline · 1 records · last edit 2021-12-09
- closes: not probed

### Shavano_Tabeguache_WFL1  ·    ·  from gis-hunter
- url: https://services2.arcgis.com/RQcpPaCpMAXzUI5g/arcgis/rest/services/Shavano_Tabeguache_WFL1/FeatureServer/5
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=cc333297358d416bbb6d087840dc7e89 · owner rre4601@rit.edu_RITArcGIS
- facts: arcgis-layer · esriGeometryPolyline · 1 records · last edit 2021-12-09
- closes: not probed

### Kremmling_Label_2  ·    ·  from gis-hunter
- url: https://services.arcgis.com/VfpeCk3ouKVuEwug/arcgis/rest/services/Kremmling_Label_2/FeatureServer/0
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=97c712a5b86649aebd065d3a1bad2db5 · owner paigesinger
- facts: arcgis-layer · esriGeometryPoint · name field Name · 1 records
- closes: not probed

### Map of Potential Locations for Housing in the Town of Kremmling_WFL1  ·    ·  from gis-hunter
- url: https://services7.arcgis.com/uSdJCyZB78QSJIZf/arcgis/rest/services/Map_of_Potential_Locations_for_Housing_in_the_Town_of_Kremmling_WFL1/FeatureServer/3
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (LLC in the publisher words)
- terms: CREDIT · source item page · "Derived from Grand County parcel data pulled from their GIS hub on 07.30.2024." · item https://www.arcgis.com/home/item.html?id=4801bc37006e4c3984244c941dd3d25a · owner CPSLLC · org Community Planning Strategies, LLC
- facts: arcgis-layer · esriGeometryPolygon · name field UNIT · 826 records · last edit 2024-08-02 · sample   /   /  
- closes: not probed

### Map of Potential Locations for Housing in the Town of Kremmling_WFL1  ·    ·  from gis-hunter
- url: https://services7.arcgis.com/uSdJCyZB78QSJIZf/arcgis/rest/services/Map_of_Potential_Locations_for_Housing_in_the_Town_of_Kremmling_WFL1/FeatureServer/4
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (LLC in the publisher words)
- terms: CREDIT · source item page · "Derived from Grand County parcel data pulled from their GIS hub on 07.30.2024." · item https://www.arcgis.com/home/item.html?id=4801bc37006e4c3984244c941dd3d25a · owner CPSLLC · org Community Planning Strategies, LLC
- facts: arcgis-layer · esriGeometryPolygon · name field UNIT · 826 records · last edit 2024-08-02 · sample   /   /  
- closes: not probed

### CO Kremmling_WFL1  ·    ·  from gis-hunter
- url: https://services8.arcgis.com/e8UG0RPWTF6kZDZd/arcgis/rest/services/CO_Kremmling_WFL1/FeatureServer/2
- WHY: nothing stated about use on the item page or the service
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=200d8feb7e434de584133a64d6d2713f · owner ViaVista
- facts: arcgis-layer · esriGeometryPolygon · name field Title · 1052 records · last edit 2022-09-18 · sample None / None / None
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### CO Kremmling_WFL1  ·    ·  from gis-hunter
- url: https://services8.arcgis.com/e8UG0RPWTF6kZDZd/arcgis/rest/services/CO_Kremmling_WFL1/FeatureServer/5
- WHY: nothing stated about use on the item page or the service
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=200d8feb7e434de584133a64d6d2713f · owner ViaVista
- facts: arcgis-layer · esriGeometryPolygon · name field Title · 3 records · last edit 2022-09-18 · sample Flag Area / Utility Building  / Pavilion 
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### CO Kremmling_WFL1  ·    ·  from gis-hunter
- url: https://services8.arcgis.com/e8UG0RPWTF6kZDZd/arcgis/rest/services/CO_Kremmling_WFL1/FeatureServer/8
- WHY: nothing stated about use on the item page or the service
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=200d8feb7e434de584133a64d6d2713f · owner ViaVista
- facts: arcgis-layer · esriGeometryPolygon · name field SectionName · 5 records · last edit 2022-09-18 · sample None / None / None
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### CO Kremmling_WFL1  ·    ·  from gis-hunter
- url: https://services8.arcgis.com/e8UG0RPWTF6kZDZd/arcgis/rest/services/CO_Kremmling_WFL1/FeatureServer/9
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=200d8feb7e434de584133a64d6d2713f · owner ViaVista
- facts: arcgis-layer · esriGeometryPolygon · 1761 records · last edit 2022-09-18
- closes: not probed

### CO Kremmling_WFL1  ·    ·  from gis-hunter
- url: https://services8.arcgis.com/e8UG0RPWTF6kZDZd/arcgis/rest/services/CO_Kremmling_WFL1/FeatureServer/10
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=200d8feb7e434de584133a64d6d2713f · owner ViaVista
- facts: arcgis-layer · esriGeometryPolygon · 1 records · last edit 2022-09-18
- closes: not probed

### CO Kremmling_WFL1  ·    ·  from gis-hunter
- url: https://services8.arcgis.com/e8UG0RPWTF6kZDZd/arcgis/rest/services/CO_Kremmling_WFL1/FeatureServer/18
- WHY: nothing stated about use on the item page or the service
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=200d8feb7e434de584133a64d6d2713f · owner ViaVista
- facts: arcgis-layer · esriGeometryPolygon · name field LotName · 0 records · last edit 2022-09-18
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### CO Kremmling_WFL1  ·    ·  from gis-hunter
- url: https://services8.arcgis.com/e8UG0RPWTF6kZDZd/arcgis/rest/services/CO_Kremmling_WFL1/FeatureServer/19
- WHY: nothing stated about use on the item page or the service
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=200d8feb7e434de584133a64d6d2713f · owner ViaVista
- facts: arcgis-layer · esriGeometryPolygon · name field Title · 0 records · last edit 2022-09-18
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### George Mason University Police and Safety Disposal Box Locations  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/ioennV6PpG5Xodq0/arcgis/rest/services/George_Mason_University_Police_and_Safety_Disposal_Box_Locations/FeatureServer/0
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → hosted for an agency (a university account holds an agency layer)
- terms: CREDIT · source item page · "Please review the Fairfax County GIS Division disclaimer . Fairfax County, Virginia; Opioid and Substance Abuse (OSA) Task Force Coordinator Fairf" · item https://www.arcgis.com/home/item.html?id=b31cd85526034c519faf26887d8e45f4 · owner FairfaxCounty · org County of Fairfax
- facts: arcgis-layer · esriGeometryPoint · name field NAME · 1 records · last edit 2026-02-25
- closes: not probed

### Potomac Heritage National Scenic Trail of Northern Virginia_ August 2021 Version  ·    ·  from gis-hunter
- url: https://services5.arcgis.com/6MUPhDX27Ne3DNOw/arcgis/rest/services/Potomac_Heritage_National_Scenic_Trail_of_Northern_Virginia__August_2021_Version/FeatureServer/0
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → official (government words: Commission)
- terms: CREDIT · source item page · "Northern Virginia Regional Commission (NVRC) is not liable for any use of or reliance upon this map or data, or any information contained herein. Wh" · item https://www.arcgis.com/home/item.html?id=aee787ce35874194972e4ff5f1d3c3df · owner jkaneff_NVRC · org Northern Virginia Regional Commission 
- facts: arcgis-layer · esriGeometryPoint · name field Project_Name · 33 records · last edit 2022-04-26
- closes: not probed

### Potomac Heritage National Scenic Trail of Northern Virginia_ August 2021 Version  ·    ·  from gis-hunter
- url: https://services5.arcgis.com/6MUPhDX27Ne3DNOw/arcgis/rest/services/Potomac_Heritage_National_Scenic_Trail_of_Northern_Virginia__August_2021_Version/FeatureServer/1
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → official (government words: Commission)
- terms: CREDIT · source item page · "Northern Virginia Regional Commission (NVRC) is not liable for any use of or reliance upon this map or data, or any information contained herein. Wh" · item https://www.arcgis.com/home/item.html?id=aee787ce35874194972e4ff5f1d3c3df · owner jkaneff_NVRC · org Northern Virginia Regional Commission 
- facts: arcgis-layer · esriGeometryPoint · name field Project_Name · 5 records · last edit 2022-04-26
- closes: not probed

### Potomac Heritage National Scenic Trail of Northern Virginia_ August 2021 Version  ·    ·  from gis-hunter
- url: https://services5.arcgis.com/6MUPhDX27Ne3DNOw/arcgis/rest/services/Potomac_Heritage_National_Scenic_Trail_of_Northern_Virginia__August_2021_Version/FeatureServer/2
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → official (government words: Commission)
- terms: CREDIT · source item page · "Northern Virginia Regional Commission (NVRC) is not liable for any use of or reliance upon this map or data, or any information contained herein. Wh" · item https://www.arcgis.com/home/item.html?id=aee787ce35874194972e4ff5f1d3c3df · owner jkaneff_NVRC · org Northern Virginia Regional Commission 
- facts: arcgis-layer · esriGeometryPoint · name field Name · 27 records · last edit 2022-04-26
- closes: not probed

### Potomac Heritage National Scenic Trail of Northern Virginia_ August 2021 Version  ·    ·  from gis-hunter
- url: https://services5.arcgis.com/6MUPhDX27Ne3DNOw/arcgis/rest/services/Potomac_Heritage_National_Scenic_Trail_of_Northern_Virginia__August_2021_Version/FeatureServer/3
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → official (government words: Commission)
- terms: CREDIT · source item page · "Northern Virginia Regional Commission (NVRC) is not liable for any use of or reliance upon this map or data, or any information contained herein. Wh" · item https://www.arcgis.com/home/item.html?id=aee787ce35874194972e4ff5f1d3c3df · owner jkaneff_NVRC · org Northern Virginia Regional Commission 
- facts: arcgis-layer · esriGeometryPolyline · name field Name · 79 records · last edit 2022-04-26
- closes: not probed

### Potomac Heritage National Scenic Trail - Viewshed Scenic Locations  ·    ·  from gis-hunter
- url: https://services5.arcgis.com/6MUPhDX27Ne3DNOw/arcgis/rest/services/Scenic_Locations/FeatureServer/0
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → official (government words: Commission)
- terms: CREDIT · source item page · "Northern Virginia Regional Commission (NVRC) is not liable for any use of or reliance upon this map or data, or any information contained herein. Wh" · item https://www.arcgis.com/home/item.html?id=e8d418f004184664ac3d9d0368165277 · owner jkaneff_NVRC · org Northern Virginia Regional Commission 
- facts: arcgis-layer · esriGeometryPoint · name field name · 12 records · last edit 2023-08-21
- closes: not probed

### Star-Spangled Banner National Historic Trail Official Centerline  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/fBc8EJBxQRMcHlei/arcgis/rest/services/Sta_Spangled_Banner_National_Historic_Trail_Official_Centerline/FeatureServer/0
- WHY: the publisher closed it (internal / sign-in / by request)
- publisher: ? → official (a federal / national agency named)
- terms: CLOSED · source item page · "cal boundary, that crosses many ownership jurisdictions. Do not cross private land without permission. This data set should not be displayed or used at scales that exc" · item https://www.arcgis.com/home/item.html?id=2bd7685b7292431c9e3561f1ea1ad113 · owner JEFARRELL@nps.gov_nps · org National Park Service
- facts: arcgis-layer · esriGeometryPolyline · name field Unit_Name · 1 records · last edit 2018-06-01
- overlap: same publisher as akht
- closes: not probed

### Star Spangled Banner Trail  ·    ·  from gis-hunter
- url: https://services7.arcgis.com/xBaYvpTc0JtqK5u2/arcgis/rest/services/StarSpangledBannerTrail/FeatureServer/0
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → official (government words: City of)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=5731a536b6e143a1ba79831312fe2974 · owner mauryt_havredegracemd · org City of Havre de Grace
- facts: arcgis-layer · esriGeometryPolyline · name field NAME · 1 records · last edit 2025-04-09
- closes: not probed

### Mount Vernon Police  ·    ·  from gis-hunter
- url: https://services6.arcgis.com/UyHjUN3YlQIsXJA1/arcgis/rest/services/Mount_Vernon_Police/FeatureServer/0
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: CREDIT · source item page · "This dataset is provided by MCCD for support purposes related to emergency services. This dataset is informational an" · item https://www.arcgis.com/home/item.html?id=50a8e521bad64f05949dd944f276befb · owner abowler911
- facts: arcgis-layer · esriGeometryPolygon · 2 records · last edit 2026-05-26
- closes: not probed

### Impact Analysis of Natural Gas Infrastructure on Mount Vernon_s Viewshed_WFL1  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/qTQ6qYkHpxlu0G82/arcgis/rest/services/Impact_Analysis_of_Natural_Gas_Infrastructure_on_Mount_Vernon_s_Viewshed_WFL1/FeatureServer/4
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=3d7dcb15a34a4b1b8febf9de18b760ff · owner pfobrien_UofMD · org University of Maryland
- facts: arcgis-layer · esriGeometryPolygon · name field Name · 6 records · last edit 2021-05-16 · sample 73 Glymont Road : 5 - 10 / 73 Glymont Road : 0 - 5 / 3099 Livingston Road : 5 - 10
- closes: not probed

### Rush Springs Hydrologic Study (Open Data)  ·    ·  from gis-hunter
- url: https://owrb.csa.ou.edu/server/rest/services/Open_Data_Only/Rush_Springs_Study/MapServer/0
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: CREDIT · source item page · "OWRB Oklahoma Water Resources Board - Jon Sanford, Technical Studies" · item https://owrb.csa.ou.edu/server/rest/services/Open_Data_Only/Rush_Springs_Study/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field Name · 1 records · sample Rush Springs
- closes: not probed

### Rush Springs Hydrologic Study (Open Data)  ·    ·  from gis-hunter
- url: https://owrb.csa.ou.edu/server/rest/services/Open_Data_Only/Rush_Springs_Study/MapServer/3
- WHY: no polygons (no geometry)
- publisher: ? → hosted for an agency (a university account holds an agency layer)
- terms: CREDIT · source item page · "OWRB Oklahoma Water Resources Board – Planning & Management Division, Technical Studies Section Stanley, T.M., 2002, Geologic map of the Woodward 30’ x 60’ quad" · item https://owrb.csa.ou.edu/server/rest/services/Open_Data_Only/Rush_Springs_Study/MapServer/info/iteminfo
- facts: arcgis-layer
- closes: not probed

### Rush Springs Hydrologic Study (Open Data)  ·    ·  from gis-hunter
- url: https://owrb.csa.ou.edu/server/rest/services/Open_Data_Only/Rush_Springs_Study/MapServer/4
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: CREDIT · source item page · "OWRB Oklahoma Water Resources Board - Derrick L. Wagner, Technical Studies" · item https://owrb.csa.ou.edu/server/rest/services/Open_Data_Only/Rush_Springs_Study/MapServer/info/iteminfo
- facts: arcgis-layer
- closes: not probed

### Rush Springs Hydrologic Study (Open Data)  ·    ·  from gis-hunter
- url: https://owrb.csa.ou.edu/server/rest/services/Open_Data_Only/Rush_Springs_Study/MapServer/5
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: CREDIT · source item page · "OWRB Oklahoma Water Resources Board - Technical Studies" · item https://owrb.csa.ou.edu/server/rest/services/Open_Data_Only/Rush_Springs_Study/MapServer/info/iteminfo
- facts: arcgis-layer
- closes: not probed

### Rush Springs Hydrologic Study (Open Data)  ·    ·  from gis-hunter
- url: https://owrb.csa.ou.edu/server/rest/services/Open_Data_Only/Rush_Springs_Study/MapServer/6
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: CREDIT · source item page · "OWRB Oklahoma Water Resources Board - Technical Studies" · item https://owrb.csa.ou.edu/server/rest/services/Open_Data_Only/Rush_Springs_Study/MapServer/info/iteminfo
- facts: arcgis-layer
- closes: not probed

### Rush Springs Hydrologic Study (Open Data)  ·    ·  from gis-hunter
- url: https://owrb.csa.ou.edu/server/rest/services/Open_Data_Only/Rush_Springs_Study/MapServer/7
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: CREDIT · source item page · "OWRB Oklahoma Water Resources Board - Technical Studies" · item https://owrb.csa.ou.edu/server/rest/services/Open_Data_Only/Rush_Springs_Study/MapServer/info/iteminfo
- facts: arcgis-layer
- closes: not probed

### Rush Hour / Night Restriction Zone  ·    ·  from gis-hunter
- url: https://services.arcgis.com/qWbGMYB49y8mLbRt/arcgis/rest/services/MetroRushHourZone_2021/FeatureServer/0
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → official (government words: Department)
- terms: CREDIT · source item page · "ission. There is no guarantee or representation to the user as to the accuracy, currency, suitability, or reliability of this data for any purpose. The user accepts the" · item https://www.arcgis.com/home/item.html?id=a60d070d8afb458faee25a584460daf7 · owner lindsey.savage_mndot · org Minnesota Department of Transportation
- facts: arcgis-layer · esriGeometryPolyline · name field ROUTE_NAME · 119 records · last edit 2021-08-05
- closes: not probed

### Rush Springs Hydrologic Study  ·    ·  from gis-hunter
- url: https://owrb.csa.ou.edu/server/rest/services/Special_Studies/Rush_Springs/MapServer/1
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: CREDIT · source item page · "OWRB Oklahoma Water Resources Board - Jon Sanford, Technical Studies" · item https://owrb.csa.ou.edu/server/rest/services/Special_Studies/Rush_Springs/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · 1 records
- closes: not probed

### Rush Springs Hydrologic Study  ·    ·  from gis-hunter
- url: https://owrb.csa.ou.edu/server/rest/services/Special_Studies/Rush_Springs/MapServer/4
- WHY: no polygons (no geometry)
- publisher: ? → hosted for an agency (a university account holds an agency layer)
- terms: CREDIT · source item page · "OWRB Oklahoma Water Resources Board – Planning & Management Division, Technical Studies Section Stanley, T.M., 2002, Geologic map of the Woodward 30’ x 60’ quad" · item https://owrb.csa.ou.edu/server/rest/services/Special_Studies/Rush_Springs/MapServer/info/iteminfo
- facts: arcgis-layer
- closes: not probed

### Rush Springs Hydrologic Study  ·    ·  from gis-hunter
- url: https://owrb.csa.ou.edu/server/rest/services/Special_Studies/Rush_Springs/MapServer/5
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: CREDIT · source item page · "OWRB Oklahoma Water Resources Board - Derrick L. Wagner, Technical Studies" · item https://owrb.csa.ou.edu/server/rest/services/Special_Studies/Rush_Springs/MapServer/info/iteminfo
- facts: arcgis-layer
- closes: not probed

### Rush Springs Hydrologic Study  ·    ·  from gis-hunter
- url: https://owrb.csa.ou.edu/server/rest/services/Special_Studies/Rush_Springs/MapServer/6
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: CREDIT · source item page · "OWRB Oklahoma Water Resources Board - Technical Studies" · item https://owrb.csa.ou.edu/server/rest/services/Special_Studies/Rush_Springs/MapServer/info/iteminfo
- facts: arcgis-layer
- closes: not probed

### Rush Springs Hydrologic Study  ·    ·  from gis-hunter
- url: https://owrb.csa.ou.edu/server/rest/services/Special_Studies/Rush_Springs/MapServer/7
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: CREDIT · source item page · "OWRB Oklahoma Water Resources Board - Technical Studies" · item https://owrb.csa.ou.edu/server/rest/services/Special_Studies/Rush_Springs/MapServer/info/iteminfo
- facts: arcgis-layer
- closes: not probed

### Rush Springs Hydrologic Study  ·    ·  from gis-hunter
- url: https://owrb.csa.ou.edu/server/rest/services/Special_Studies/Rush_Springs/MapServer/8
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: CREDIT · source item page · "OWRB Oklahoma Water Resources Board - Technical Studies" · item https://owrb.csa.ou.edu/server/rest/services/Special_Studies/Rush_Springs/MapServer/info/iteminfo
- facts: arcgis-layer
- closes: not probed

### World War 1  ·    ·  from gis-hunter
- url: https://services9.arcgis.com/WGilu1i2IRlWIWQG/arcgis/rest/services/World_War_1/FeatureServer/0
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=c1cf87cbc03843d7b8c43ce8ef05469d · owner janet.owen.earth · org The Earth Museum
- facts: arcgis-layer · esriGeometryPoint · 46 records · last edit 2020-11-07
- closes: not probed

### Ozark Hellbender Locations  ·    ·  from gis-hunter
- url: https://services.arcgis.com/ue9rwulIoeLEI9bj/arcgis/rest/services/Ozark_Hellbender_locations/FeatureServer/0
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (Esri in the publisher words)
- terms: NON-COMMERCIAL · source item page · "ional. Use of this Data is restricted to training, demonstration, and educational purposes only. This Data cannot be sold or used for marketing without the express written consent of En" · item https://www.arcgis.com/home/item.html?id=ab424731c64e49f9b8dbcd646fd76137 · owner EsriTrainingSvc · org Esri Training Services
- facts: arcgis-layer · esriGeometryPoint · 6 records · last edit 2025-02-27
- closes: not probed

### Ozark Aquifer  ·    ·  from gis-hunter
- url: https://services2.arcgis.com/ZOdjAzAQ2B0f85zi/arcgis/rest/services/Ozark_Aquifer/FeatureServer/1
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: CREDIT · source item page · "None. Users should determine that the data are appropriate for their uses. KGS" · item https://www.arcgis.com/home/item.html?id=58374a144fbe4b5790559710aed29082 · owner KS_Geological_Survey · org  The University of Kansas
- facts: arcgis-layer · esriGeometryPolygon · 2 records · last edit 2020-09-25
- closes: not probed

### Ozark National Forest Service Management Area (Polygon)  ·    ·  from gis-hunter
- url: https://gis.arkansas.gov/arcgis/rest/services/FEATURESERVICES/Boundaries/FeatureServer/25
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → official (government host gis.arkansas.gov)
- terms: NOTHING STATED · source item page · item https://gis.arkansas.gov/arcgis/rest/services/FEATURESERVICES/Boundaries/FeatureServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · 3200 records
- overlap: same service as sgara (another layer of it)
- closes: not probed

### Rock_Island_GIS_ESRI  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/51R1xnARnjq5iyz9/arcgis/rest/services/GIS_ESRI/FeatureServer/8
- WHY: nothing stated about use on the item page or the service
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=5f92b16062ae438c98d5dda6d290c25c · owner CACC2013 · org Columbia Area Career Center
- facts: arcgis-layer · esriGeometryPolygon · name field NAME · 115 records · last edit 2017-05-19 · sample Clark / Atchison / Scotland
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### Rock_Island_GIS_ESRI  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/51R1xnARnjq5iyz9/arcgis/rest/services/GIS_ESRI/FeatureServer/9
- WHY: nothing stated about use on the item page or the service
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=5f92b16062ae438c98d5dda6d290c25c · owner CACC2013 · org Columbia Area Career Center
- facts: arcgis-layer · esriGeometryPolygon · name field NAME · 13 records · last edit 2017-05-19 · sample Jackson / Pettis / Johnson
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### Essex Wildlife Trust Winter Wetland Bird Surveys 2021 to 22  ·    ·  from gis-hunter
- url: https://services.arcgis.com/36oR7fxwYZcqhQIh/arcgis/rest/services/Essex_Wildlife_Trust_Winter_Wetland_Bird_Surveys_2021_to_22/FeatureServer/0
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (Trust in the publisher words)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=2b1b56f8a6594be39c4f433178b379cb · owner CharlotteM_EWTConsTeam
- facts: arcgis-layer · esriGeometryPoint · 4263 records · last edit 2025-09-04
- closes: not probed

### Elk Migration Corridors - East Shasta Valley - 1999-2001, 2016-2020 [ds2903]  ·    ·  from gis-hunter
- url: https://services2.arcgis.com/Uq9r85Potqm3MfRV/arcgis/rest/services/biosds2903_fpu/FeatureServer/0
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → official (government words: Department)
- terms: CREDIT · source item page · "The user accepts sole responsibility for the correct interpretation of this report and the correct use of its accompanying dataset. Prior to using this dataset," · item https://www.arcgis.com/home/item.html?id=8880cc3dcc0e4fd88ebbd7fd973a70e1 · owner BIOS_Admin · org California Department of Fish and Wildlife
- facts: arcgis-layer · esriGeometryPolygon · 4 records · last edit 2025-07-21
- overlap: same publisher as sgcaa
- closes: not probed

### Elk Migration Corridors - West Goose Lake - 1999-2002, 2018-2020 [ds2901]  ·    ·  from gis-hunter
- url: https://services2.arcgis.com/Uq9r85Potqm3MfRV/arcgis/rest/services/biosds2901_fpu/FeatureServer/0
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → official (government words: Department)
- terms: CREDIT · source item page · "The user accepts sole responsibility for the correct interpretation of this report and the correct use of its accompanying dataset. Prior to using this dataset," · item https://www.arcgis.com/home/item.html?id=c32c3819df974d62a0b1e9b40b9e8283 · owner BIOS_Admin · org California Department of Fish and Wildlife
- facts: arcgis-layer · esriGeometryPolygon · 4 records · last edit 2025-07-18
- overlap: same publisher as sgcaa
- closes: not probed

### Elk Migration Corridors - Egg Lake - 2001-2002, 2017-2020 [ds2908]  ·    ·  from gis-hunter
- url: https://services2.arcgis.com/Uq9r85Potqm3MfRV/arcgis/rest/services/biosds2908_fpu/FeatureServer/0
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → official (government words: Department)
- terms: CREDIT · source item page · "The user accepts sole responsibility for the correct interpretation of this report and the correct use of its accompanying dataset. Prior to using this dataset," · item https://www.arcgis.com/home/item.html?id=eaf41110576d47189a80e4a11df4f9a1 · owner BIOS_Admin · org California Department of Fish and Wildlife
- facts: arcgis-layer · esriGeometryPolygon · 4 records · last edit 2025-07-21
- overlap: same publisher as sgcaa
- closes: not probed

### WSOR West Bend Sub North of Junction with WSOR Milwaukee Sub  ·    ·  from gis-hunter
- url: https://services3.arcgis.com/dZlu5nJgfmCUXRzB/arcgis/rest/services/WSOR_West_Bend_Sub_North_of_Junction_with_WSOR_Milwaukee_Sub/FeatureServer/0
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=4abf42b442e04abc83da16f0ba0e698b · owner ejohnson_SEWRPC
- facts: arcgis-layer · esriGeometryPolyline · 1 records · last edit 2023-10-03
- closes: not probed

### North Bend Rail Trail_WFL1  ·    ·  from gis-hunter
- url: https://services5.arcgis.com/Y41A3MtSGCNYWW3x/arcgis/rest/services/North_Bend_Rail_Trail_WFL1/FeatureServer/0
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → official (government words: DNR)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=285b28cd46514f0a812e0260df7430dc · owner DNRPEM · org WV DNR Planning, Engineering and Maintenance
- facts: arcgis-layer · esriGeometryPoint · name field Name · 20589 records · last edit 2026-03-13
- closes: not probed

### North Bend Rail Trail 1_WFL1  ·    ·  from gis-hunter
- url: https://services5.arcgis.com/Y41A3MtSGCNYWW3x/arcgis/rest/services/North_Bend_Rail_Trail_1_WFL1/FeatureServer/0
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → official (government words: DNR)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=79335d56cee7404594140d4ba12c3ef1 · owner DNRPEM · org WV DNR Planning, Engineering and Maintenance
- facts: arcgis-layer · esriGeometryPoint · name field Name · 20589 records · last edit 2026-02-05
- closes: not probed

### Greenbrier Future Land Use Framework  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/OAphVRUvJVpBRovs/arcgis/rest/services/Greenbrier_Future_Land_Use_Framework/FeatureServer/0
- WHY: NOT A PARK LAYER (coverage: parcels / census / index / planning / fire): it covers the whole land, so every pin falls inside (chat 11, Oct 29)
- publisher: ? → official (government words: City of)
- terms: CREDIT · source item page · "For reference only. Contact the Planning Department by telephone at 757-382-6176 or by E-mail at planning@cityofchesapeake.net for more information. Planning Pl" · item https://www.arcgis.com/home/item.html?id=aa588ffc264c4f03802a6ac2b53f0cff · owner jvuturobrady@cityofchesapeake.net · org City of Chesapeake, VA
- facts: arcgis-layer · esriGeometryPolygon · name field unit · 1 records · last edit 2025-07-31 · sample  
- closes: not probed

### Greenbrier Future Land Use Framework  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/OAphVRUvJVpBRovs/arcgis/rest/services/Greenbrier_Future_Land_Use_Framework/FeatureServer/1
- WHY: NOT A PARK LAYER (coverage: parcels / census / index / planning / fire): it covers the whole land, so every pin falls inside (chat 11, Oct 29)
- publisher: ? → official (government words: City of)
- terms: CREDIT · source item page · "For reference only. Contact the Planning Department by telephone at 757-382-6176 or by E-mail at planning@cityofchesapeake.net for more information. Planning Pl" · item https://www.arcgis.com/home/item.html?id=aa588ffc264c4f03802a6ac2b53f0cff · owner jvuturobrady@cityofchesapeake.net · org City of Chesapeake, VA
- facts: arcgis-layer · esriGeometryPolygon · name field NAME · 5 records · last edit 2025-07-31 · sample Health Village / Recreation District / Central District
- closes: not probed

### Greenbrier Future Land Use Framework  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/OAphVRUvJVpBRovs/arcgis/rest/services/Greenbrier_Future_Land_Use_Framework/FeatureServer/2
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → official (government words: City of)
- terms: CREDIT · source item page · "For reference only. Contact the Planning Department by telephone at 757-382-6176 or by E-mail at planning@cityofchesapeake.net for more information. Planning Pl" · item https://www.arcgis.com/home/item.html?id=aa588ffc264c4f03802a6ac2b53f0cff · owner jvuturobrady@cityofchesapeake.net · org City of Chesapeake, VA
- facts: arcgis-layer · esriGeometryPolygon · 4 records · last edit 2025-07-31
- closes: not probed

### Greenbrier Future Land Use Framework  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/OAphVRUvJVpBRovs/arcgis/rest/services/Greenbrier_Future_Land_Use_Framework/FeatureServer/3
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → official (government words: City of)
- terms: CREDIT · source item page · "For reference only. Contact the Planning Department by telephone at 757-382-6176 or by E-mail at planning@cityofchesapeake.net for more information. Planning Pl" · item https://www.arcgis.com/home/item.html?id=aa588ffc264c4f03802a6ac2b53f0cff · owner jvuturobrady@cityofchesapeake.net · org City of Chesapeake, VA
- facts: arcgis-layer · esriGeometryPolygon · 7 records · last edit 2025-10-24
- closes: not probed

### Greenbrier_Addressing_Service  ·    ·  from gis-hunter
- url: https://services3.arcgis.com/nJbIFHiSnaX0z0hS/arcgis/rest/services/Greenbrier_Addressing_Service/FeatureServer/3
- WHY: nothing stated about use on the item page or the service
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=ca467689db16438895f14ba39c3411ae · owner tpenegar
- facts: arcgis-layer · esriGeometryPolygon · name field name · 30756 records · last edit 2024-08-13 · sample JKD / None / None
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### Two Foot Topographic Contours - Upper Ammonoosuc River (0108010304) - smoothed  ·    ·  from gis-hunter
- url: https://nhgeodata.unh.edu/hosting/rest/services/Hosted/EDP_LiDAR_Contours_2ft_01080103_smooth/FeatureServer/5
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: NOTHING STATED · source item page · item https://nhgeodata.unh.edu/hosting/rest/services/Hosted/EDP_LiDAR_Contours_2ft_01080103_smooth/FeatureServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolyline · 214303 records
- overlap: same publisher as nhc
- closes: not probed

### Two Foot Topographic Contours - Lower Ammonoosuc River (0108010305) - smoothed  ·    ·  from gis-hunter
- url: https://nhgeodata.unh.edu/hosting/rest/services/Hosted/EDP_LiDAR_Contours_2ft_01080103_smooth/FeatureServer/6
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: NOTHING STATED · source item page · item https://nhgeodata.unh.edu/hosting/rest/services/Hosted/EDP_LiDAR_Contours_2ft_01080103_smooth/FeatureServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolyline · 219942 records
- overlap: same publisher as nhc
- closes: not probed

### Two Foot Topographic Contours - Upper Ammonoosuc River (0108010107) - smoothed  ·    ·  from gis-hunter
- url: https://nhgeodata.unh.edu/hosting/rest/services/Hosted/EDP_LiDAR_Contours_2ft_01080101_smooth/FeatureServer/7
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: NOTHING STATED · source item page · item https://nhgeodata.unh.edu/hosting/rest/services/Hosted/EDP_LiDAR_Contours_2ft_01080101_smooth/FeatureServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolyline · 338081 records
- overlap: same publisher as nhc
- closes: not probed

### Sugar Maple (Acer saccharum) Distribution in Minnesota  ·    ·  from gis-hunter
- url: https://tiles.arcgis.com/tiles/8df8p0NlLFEShl0r/arcgis/rest/services/itsp_i318_sugarmaple/MapServer/0
- WHY: no polygons (no geometry)
- publisher: ? → hosted for an agency (a university account holds an agency layer)
- terms: CREDIT · source item page · "s is derived from USDA Forest Service data: Use of this data requires acknowledgement of the USDA Forest Service Users must comply with the original ITSP data usage terms You" · item https://www.arcgis.com/home/item.html?id=7531a80e0d0e4aa1adaef853de2ac646 · owner jeli0026_UMN · org University of Minnesota
- facts: arcgis-layer
- closes: not probed

### Health_Care_Clinics_Crispin_Nakoa_WFL1  ·    ·  from gis-hunter
- url: https://services3.arcgis.com/0OPQIK59PJJqLK0A/arcgis/rest/services/Health_Care_Clinics_Crispin_Nakoa_WFL1/FeatureServer/2
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=866fe51fb41047b4a956a53fb5ebceab · owner jnakoa_asu · org Arizona State University
- facts: arcgis-layer · esriGeometryPolygon · 6 records · last edit 2024-01-16
- closes: not probed

### Health_Care_Clinics_Crispin_Nakoa_WFL1  ·    ·  from gis-hunter
- url: https://services3.arcgis.com/0OPQIK59PJJqLK0A/arcgis/rest/services/Health_Care_Clinics_Crispin_Nakoa_WFL1/FeatureServer/3
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=866fe51fb41047b4a956a53fb5ebceab · owner jnakoa_asu · org Arizona State University
- facts: arcgis-layer · esriGeometryPolygon · name field NAME · 1 records · last edit 2024-01-16 · sample PITTSBURGH CITY
- closes: not probed

### Health_Care_Clinics_Crispin_Nakoa_WFL1  ·    ·  from gis-hunter
- url: https://services3.arcgis.com/0OPQIK59PJJqLK0A/arcgis/rest/services/Health_Care_Clinics_Crispin_Nakoa_WFL1/FeatureServer/4
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=866fe51fb41047b4a956a53fb5ebceab · owner jnakoa_asu · org Arizona State University
- facts: arcgis-layer · esriGeometryPolygon · name field NAME · 1 records · last edit 2024-01-16 · sample Allegheny
- closes: not probed

### Health_Care_Clinics_Crispin_Nakoa_WFL1  ·    ·  from gis-hunter
- url: https://services3.arcgis.com/0OPQIK59PJJqLK0A/arcgis/rest/services/Health_Care_Clinics_Crispin_Nakoa_WFL1/FeatureServer/5
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=866fe51fb41047b4a956a53fb5ebceab · owner jnakoa_asu · org Arizona State University
- facts: arcgis-layer · esriGeometryPolygon · name field LANDNAME · 36 records · last edit 2024-01-16 · sample   / Lampher Reservation / Locks
- closes: not probed

### Health_Care_Clinics_Crispin_Nakoa_WFL1  ·    ·  from gis-hunter
- url: https://services3.arcgis.com/0OPQIK59PJJqLK0A/arcgis/rest/services/Health_Care_Clinics_Crispin_Nakoa_WFL1/FeatureServer/6
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=866fe51fb41047b4a956a53fb5ebceab · owner jnakoa_asu · org Arizona State University
- facts: arcgis-layer · esriGeometryPolygon · 1 records · last edit 2024-01-16
- closes: not probed

### Health_Care_Clinics_Crispin_Nakoa_WFL1  ·    ·  from gis-hunter
- url: https://services3.arcgis.com/0OPQIK59PJJqLK0A/arcgis/rest/services/Health_Care_Clinics_Crispin_Nakoa_WFL1/FeatureServer/7
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=866fe51fb41047b4a956a53fb5ebceab · owner jnakoa_asu · org Arizona State University
- facts: arcgis-layer · esriGeometryPolygon · 1 records · last edit 2024-01-16
- closes: not probed

### Health_Care_Clinics_Crispin_Nakoa_WFL1  ·    ·  from gis-hunter
- url: https://services3.arcgis.com/0OPQIK59PJJqLK0A/arcgis/rest/services/Health_Care_Clinics_Crispin_Nakoa_WFL1/FeatureServer/8
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=866fe51fb41047b4a956a53fb5ebceab · owner jnakoa_asu · org Arizona State University
- facts: arcgis-layer · esriGeometryPolygon · name field NAME · 130 records · last edit 2024-01-16 · sample Coraopolis / West Deer / East Pittsburgh
- closes: not probed

### Health_Care_Clinics_Crispin_Nakoa_WFL1  ·    ·  from gis-hunter
- url: https://services3.arcgis.com/0OPQIK59PJJqLK0A/arcgis/rest/services/Health_Care_Clinics_Crispin_Nakoa_WFL1/FeatureServer/9
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=866fe51fb41047b4a956a53fb5ebceab · owner jnakoa_asu · org Arizona State University
- facts: arcgis-layer · esriGeometryPolygon · 402 records · last edit 2024-01-16
- closes: not probed

### Aiea Loop  ·    ·  from gis-hunter
- url: https://services8.arcgis.com/tblHe99qQFMcNzpC/arcgis/rest/services/Aiea_Loop/FeatureServer/0
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=68c098df72f248ce8c8dc472dd2926f5 · owner tommyphammy
- facts: arcgis-layer · esriGeometryPolyline · name field Trail_Name · 1 records · last edit 2018-06-12
- closes: not probed

### Na Ala Hele Trails  ·    ·  from gis-hunter
- url: https://geodata.hawaii.gov/arcgis/rest/services/Terrestrial/MapServer/34
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → official (government host geodata.hawaii.gov)
- terms: CREDIT · source item page · "DISCLAIMER: Information contained in these files is derived from public records that are constantly" · item https://geodata.hawaii.gov/arcgis/rest/services/Terrestrial/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolyline · name field trailname · 157 records
- overlap: same service as sghib (another layer of it)
- closes: not probed

### Na Ala Hele Hiking Trails  ·    ·  from gis-hunter
- url: https://services.arcgis.com/tNJpAOha4mODLkXz/arcgis/rest/services/Hiking_Trails/FeatureServer/0
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → official (government words: County)
- terms: CREDIT · source item page · "and do not replace a site survey, and is not warranted for content or accuracy. The City does not guarantee the positional or thematic accuracy of the GIS data. The GIS" · item https://www.arcgis.com/home/item.html?id=1a0e0024938d46908f9aca9ff255369f · owner holisgis · org City & County of Honolulu GIS
- facts: arcgis-layer · esriGeometryPolyline · name field Trail_Name · 46 records
- closes: not probed

### Na Ala Hele Trails 2019  ·    ·  from gis-hunter
- url: https://services.arcgis.com/HQ0xoN0EzDPBOEci/arcgis/rest/services/Na_Ala_Hele_Trails_2019/FeatureServer/0
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → official (government words: Department)
- terms: CREDIT · source item page · "This dataset is a graphical representation of trails and access locations. It may not overlay well on various satellite imagery datasets at certain scales. DO N" · item https://www.arcgis.com/home/item.html?id=063bc636ce704f85a94dcaa0a84110e9 · owner dlnr_dmatsuwaki · org Hawaiʻi Statewide GIS Program
- facts: arcgis-layer · esriGeometryPolyline · name field Trailname · 152 records · last edit 2020-01-08
- overlap: same publisher as sghic
- closes: not probed

### Hawaii Capital Historic District map tour route  ·    ·  from gis-hunter
- url: https://services5.arcgis.com/LjEpKgpks2lYdrmt/arcgis/rest/services/Hawaii_Capital_District_map_tour_route/FeatureServer/0
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → official (government words: District)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=0c177a1485604ed1a4163968cfc9bd2e · owner nyokoi_CSH
- facts: arcgis-layer · esriGeometryPolyline · 53 records · last edit 2018-12-22
- closes: not probed

### Capital District Historic Sites  ·    ·  from gis-hunter
- url: https://services5.arcgis.com/LjEpKgpks2lYdrmt/arcgis/rest/services/Capital_District_Historic_Sites/FeatureServer/0
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → official (government words: District)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=c5bf37aa9636415eb6428e8ebb29b2b4 · owner nyokoi_CSH
- facts: arcgis-layer · esriGeometryPoint · name field name · 33 records · last edit 2019-02-25
- closes: not probed

### Sheltowee Trace  ·    ·  from gis-hunter
- url: https://services3.arcgis.com/0g1gZyTiQ9uGlDEb/arcgis/rest/services/Sheltowee_Trace/FeatureServer/0
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=ce07978068f944aebff968ebabf0e3fb · owner eonealKY
- facts: arcgis-layer · esriGeometryPolyline · 1 records · last edit 2025-03-12
- closes: not probed

### Johnson County, IA Buildings  ·    ·  from gis-hunter
- url: https://services6.arcgis.com/Do88DoK2xjTUCXd1/arcgis/rest/services/Johnson_County_IA_Buildings/FeatureServer/0
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (Esri in the publisher words)
- terms: OPEN · source item page · "This work is licensed under a Creative Commons by Attribution (CC BY 4.0) license. See Credits for Attribution. View License Deed | View" · item https://www.arcgis.com/home/item.html?id=69a7fe954dcf4c6ab69421596a5c4c82 · owner dkensok_osm · org OpenStreetMap
- facts: arcgis-layer · esriGeometryPolygon · name field name · 75525 records · last edit 2021-01-08 · sample  /  / 
- closes: not probed

### Johnson City MTPO 2025 Metropolitan Planning Area (Johnson City MTPO)  ·    ·  from gis-hunter
- url: https://services2.arcgis.com/sFeLdas1ukfB6i8T/arcgis/rest/services/Johnson_City_MTPO_2025_Metropolitan_Planning_Area_(Johnson_City_MTPO)/FeatureServer/0
- WHY: NOT A PARK LAYER (coverage: parcels / census / index / planning / fire): it covers the whole land, so every pin falls inside (chat 11, Oct 29)
- publisher: ? → official (government words: City of)
- terms: CREDIT · source item page · "Johnson City MPTO Glenn K. Berry, Micha Bray, Michael Thompson" · item https://www.arcgis.com/home/item.html?id=1ae4d1e4367b4c04be61fb158ce14a71 · owner jcgis_publisher · org City of Johnson City, TN 
- facts: arcgis-layer · esriGeometryPolygon · name field Name · 1 records · last edit 2025-09-18 · sample Johnson City MTPO MPA
- closes: not probed

### Pleasant Valley Maps  ·    ·  from gis-hunter
- url: https://services5.arcgis.com/kxeQ182ZV0PBfBVA/arcgis/rest/services/Pleasant_Valley_Maps/FeatureServer/2
- WHY: nothing stated about use on the item page or the service
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=5464ac78a3714d868ab853b2c91e7201 · owner KTUA_Planner · org KTU & A Planning & Landscape Architecture
- facts: arcgis-layer · esriGeometryPolygon · name field NAME · 1 records · last edit 2024-01-25 · sample Camarillo
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### ng_meynen_schmit  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/DbPykcCwUUYq5zKg/arcgis/rest/services/ng_meynen_schmit/FeatureServer/0
- WHY: nothing stated about use on the item page or the service
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=f7fe0bcf3790471a8d423eb9e16f66c8 · owner Muellhalde
- facts: arcgis-layer · esriGeometryPolygon · name field NAME · 96 records · last edit 2020-08-28 · sample Hinterer Bregenzer Wald / Allgäuer Hochalpen / Oberstdorfer Becken
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### Long Term Care Facilities of New Jersey  ·    ·  from gis-hunter
- url: https://services2.arcgis.com/XVOqAjTOJ5P6ngMu/arcgis/rest/services/NJ_Long_Term_Care_Facilities/FeatureServer/0
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → official (government words: Office of)
- terms: CREDIT · source item page · "e of this metadata record for conditions that limit appropriate uses. Acknowledgement of the data set providers, NJ Office of Information Technology, Office of GIS (NJOGIS), a" · item https://www.arcgis.com/home/item.html?id=1f80a9e6aab8410cafd3f6b61bf3e457 · owner NJOGIS · org New Jersey Office of GIS
- facts: arcgis-layer · esriGeometryPoint · name field FacilityName · 730 records · last edit 2020-08-08
- closes: not probed

### Bathymetric Contours in Meters for Long Island Sound  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/FjPcSmEFuDYlIdKC/arcgis/rest/services/Bathymetric_Contours_in_Meters_for_long_Island_Sound/FeatureServer/0
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → official (government words: Department)
- terms: OPEN · source item page · "CC0 CTDEEP CTDEEP" · item https://www.arcgis.com/home/item.html?id=2d08a5e623bd4b3eb107815511344f1a · owner deepgis · org Department of Energy & Environmental Protection
- facts: arcgis-layer · esriGeometryPolyline · 9839 records · last edit 2019-01-09
- overlap: same publisher as ctd
- closes: not probed

### Long Island Sound Quaternary Geology Set  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/FjPcSmEFuDYlIdKC/arcgis/rest/services/Long_Island_Sound_Quaternary_Geology_Set/FeatureServer/0
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → official (government words: Department)
- terms: OPEN · source item page · "CC0 CTDEEP CTDEEP" · item https://www.arcgis.com/home/item.html?id=6c9cfffad21c46eca249c51e59595fda · owner deepgis · org Department of Energy & Environmental Protection
- facts: arcgis-layer · esriGeometryPolygon · 142 records · last edit 2019-10-23
- overlap: same publisher as ctd
- closes: not probed

### Long Island Sound Quaternary Geology Set  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/FjPcSmEFuDYlIdKC/arcgis/rest/services/Long_Island_Sound_Quaternary_Geology_Set/FeatureServer/1
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → official (government words: Department)
- terms: OPEN · source item page · "CC0 CTDEEP CTDEEP" · item https://www.arcgis.com/home/item.html?id=6c9cfffad21c46eca249c51e59595fda · owner deepgis · org Department of Energy & Environmental Protection
- facts: arcgis-layer · esriGeometryPolygon · 51 records · last edit 2019-10-23
- overlap: same publisher as ctd
- closes: not probed

### Long Island Sound Quaternary Geology Set  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/FjPcSmEFuDYlIdKC/arcgis/rest/services/Long_Island_Sound_Quaternary_Geology_Set/FeatureServer/2
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → official (government words: Department)
- terms: OPEN · source item page · "CC0 CTDEEP CTDEEP" · item https://www.arcgis.com/home/item.html?id=6c9cfffad21c46eca249c51e59595fda · owner deepgis · org Department of Energy & Environmental Protection
- facts: arcgis-layer · esriGeometryPolygon · 458 records · last edit 2019-10-23
- overlap: same publisher as ctd
- closes: not probed

### Long Island Sound Quaternary Geology Set  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/FjPcSmEFuDYlIdKC/arcgis/rest/services/Long_Island_Sound_Quaternary_Geology_Set/FeatureServer/3
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → official (government words: Department)
- terms: OPEN · source item page · "CC0 CTDEEP CTDEEP" · item https://www.arcgis.com/home/item.html?id=6c9cfffad21c46eca249c51e59595fda · owner deepgis · org Department of Energy & Environmental Protection
- facts: arcgis-layer · esriGeometryPolygon · 5 records · last edit 2019-10-23
- overlap: same publisher as ctd
- closes: not probed

### Long Island Sound Quaternary Geology Set  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/FjPcSmEFuDYlIdKC/arcgis/rest/services/Long_Island_Sound_Quaternary_Geology_Set/FeatureServer/4
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → official (government words: Department)
- terms: OPEN · source item page · "CC0 CTDEEP CTDEEP" · item https://www.arcgis.com/home/item.html?id=6c9cfffad21c46eca249c51e59595fda · owner deepgis · org Department of Energy & Environmental Protection
- facts: arcgis-layer · esriGeometryPolygon · 1 records · last edit 2019-10-23
- overlap: same publisher as ctd
- closes: not probed

### Manitoba Capital Plans Project Status  ·    ·  from gis-hunter
- url: https://services.arcgis.com/mMUesHYPkXjaFGfS/arcgis/rest/services/Manitoba_Capital_Plans_Project_Status/FeatureServer/0
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → official (government words: Government)
- terms: OPEN · source item page · "Manitoba Open Data Licence Manitoba Government" · item https://www.arcgis.com/home/item.html?id=e8d3f8dc1b1842068ca789b6326f0f22 · owner Manitoba_Government · org Manitoba Maps
- facts: arcgis-layer · esriGeometryPoint · name field Municipality_Name · 988 records · last edit 2026-10-06
- overlap: same publisher as Manitoba Par
- closes: not probed

### 202108_Capital_Projects  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/0mhlGDIUKwQF6tnJ/arcgis/rest/services/202105_Capital_Projects/FeatureServer/6
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → official (government words: Authority)
- terms: CREDIT · source item page · "This feature service is publicly accessible. NYCHA Performance Tracking & Analytics Department (PTAD) NYCHA Performance Tracking & Analytics Department (PTAD)" · item https://www.arcgis.com/home/item.html?id=294925feabbb469c95fdfb535bfb1ab2 · owner cheungy · org New York City Housing Authority
- facts: arcgis-layer · esriGeometryPolygon · 285 records · last edit 2021-11-16
- closes: not probed

### 2025-2034 Capital Highway Investment Plan Feature_Layers  ·    ·  from gis-hunter
- url: https://services.arcgis.com/qWbGMYB49y8mLbRt/arcgis/rest/services/2025_2034_10_Year_Capital_Highway_Investment_Plan_WFL1/FeatureServer/56
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → official (government words: Department)
- terms: CREDIT · source item page · "ission. There is no guarantee or representation to the user as to the accuracy, currency, suitability, or reliability of this data for any purpose. The user accepts the" · item https://www.arcgis.com/home/item.html?id=dc47ede4df1849d8bff3783497828367 · owner gwen.reoch_mndot · org Minnesota Department of Transportation
- facts: arcgis-layer · esriGeometryPoint · 310 records · last edit 2026-03-09
- closes: not probed

### 2025-2034 Capital Highway Investment Plan Feature_Layers  ·    ·  from gis-hunter
- url: https://services.arcgis.com/qWbGMYB49y8mLbRt/arcgis/rest/services/2025_2034_10_Year_Capital_Highway_Investment_Plan_WFL1/FeatureServer/1
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → official (government words: Department)
- terms: CREDIT · source item page · "ission. There is no guarantee or representation to the user as to the accuracy, currency, suitability, or reliability of this data for any purpose. The user accepts the" · item https://www.arcgis.com/home/item.html?id=dc47ede4df1849d8bff3783497828367 · owner gwen.reoch_mndot · org Minnesota Department of Transportation
- facts: arcgis-layer · esriGeometryPoint · 429 records · last edit 2026-03-09
- closes: not probed

### 2025-2034 Capital Highway Investment Plan Feature_Layers  ·    ·  from gis-hunter
- url: https://services.arcgis.com/qWbGMYB49y8mLbRt/arcgis/rest/services/2025_2034_10_Year_Capital_Highway_Investment_Plan_WFL1/FeatureServer/68
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → official (government words: Department)
- terms: CREDIT · source item page · "ission. There is no guarantee or representation to the user as to the accuracy, currency, suitability, or reliability of this data for any purpose. The user accepts the" · item https://www.arcgis.com/home/item.html?id=dc47ede4df1849d8bff3783497828367 · owner gwen.reoch_mndot · org Minnesota Department of Transportation
- facts: arcgis-layer · esriGeometryPolyline · 551 records · last edit 2026-03-09
- closes: not probed

### 2025-2034 Capital Highway Investment Plan Feature_Layers  ·    ·  from gis-hunter
- url: https://services.arcgis.com/qWbGMYB49y8mLbRt/arcgis/rest/services/2025_2034_10_Year_Capital_Highway_Investment_Plan_WFL1/FeatureServer/67
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → official (government words: Department)
- terms: CREDIT · source item page · "ission. There is no guarantee or representation to the user as to the accuracy, currency, suitability, or reliability of this data for any purpose. The user accepts the" · item https://www.arcgis.com/home/item.html?id=dc47ede4df1849d8bff3783497828367 · owner gwen.reoch_mndot · org Minnesota Department of Transportation
- facts: arcgis-layer · esriGeometryPolyline · 436 records · last edit 2026-03-09
- closes: not probed

### Green Circle Trail Sections  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/kkX9mRo34fTGAX96/arcgis/rest/services/Green_Circle_Trail_Sections/FeatureServer/28
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: CREDIT · source item page · "UW-Stevens Point GIS Center Technicians: Chase Bayer, Nicolaus Anderson, and Stephen Schuessler PI: Christine Koeller UW-Stevens Point GIS Center Technicians: C" · item https://www.arcgis.com/home/item.html?id=d2e0718bdbe0488fb8d73af3138a3769 · owner jbuchhol@uwsp.edu_UWSP · org University of Wisconsin-Stevens Point
- facts: arcgis-layer · esriGeometryPolyline · name field Name · 30 records · last edit 2022-08-11
- closes: not probed

### Green Circle Trail Spurs  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/kkX9mRo34fTGAX96/arcgis/rest/services/Green_Circle_Trail_Spurs/FeatureServer/29
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: CREDIT · source item page · "UW-Stevens Point GIS Center Technicians: Chase Bayer, Nicolaus Anderson, and Stephen Schuessler PI: Christine Koeller UW-Stevens Point GIS Center Technicians: C" · item https://www.arcgis.com/home/item.html?id=00b73cc10dcc4434a220ac04d9f09e15 · owner jbuchhol@uwsp.edu_UWSP · org University of Wisconsin-Stevens Point
- facts: arcgis-layer · esriGeometryPolyline · name field Name · 23 records · last edit 2024-12-13
- closes: not probed

### Green Circle Trail Surfaces  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/kkX9mRo34fTGAX96/arcgis/rest/services/Green_Circle_Trail_Surfaces/FeatureServer/27
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: CREDIT · source item page · "UW-Stevens Point GIS Center Technicians: Chase Bayer, Nicolaus Anderson, and Stephen Schuessler PI: Christine Koeller UW-Stevens Point GIS Center Technicians: C" · item https://www.arcgis.com/home/item.html?id=58a3889ec2f644bfa052dac8ed17bd7b · owner jbuchhol@uwsp.edu_UWSP · org University of Wisconsin-Stevens Point
- facts: arcgis-layer · esriGeometryPolyline · name field Name · 30 records · last edit 2022-09-14
- closes: not probed

### Little Libraries - Millcreek Promise  ·    ·  from gis-hunter
- url: https://services9.arcgis.com/XRrSFvEwSsReIxuA/arcgis/rest/services/LittleLibrariesGeocoded/FeatureServer/0
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: CREDIT · source item page · "Millcreek Promise" · item https://www.arcgis.com/home/item.html?id=6110061f7c604737ade658bb032e7116 · owner GISMillcreek · org Millcreek 
- facts: arcgis-layer · esriGeometryPoint · name field StName · 32 records · last edit 2026-08-31
- closes: not probed

### Two Foot Topographic Contours - Little Cohas Brook-Merrimack River (0107000608) - smoothed  ·    ·  from gis-hunter
- url: https://nhgeodata.unh.edu/hosting/rest/services/Hosted/EDP_LiDAR_Contours_2ft_01070006_smooth/FeatureServer/10
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: NOTHING STATED · source item page · item https://nhgeodata.unh.edu/hosting/rest/services/Hosted/EDP_LiDAR_Contours_2ft_01070006_smooth/FeatureServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolyline · 147344 records
- overlap: same publisher as nhc
- closes: not probed

### Little_Tokyo_August_Geofence_Events  ·    ·  from gis-hunter
- url: https://services5.arcgis.com/7nsPwEMP38bSkCjy/arcgis/rest/services/Little_Tokyo_August_Geofence_Events/FeatureServer/0
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: CREDIT · source item page · "General License usage LADOT: Transportation Technology/New Mobility LADOT: Transportation Technology/New Mobility" · item https://www.arcgis.com/home/item.html?id=aacd9d69a78f43cd94fc8c812441197f · owner Vlad_inthecity
- facts: arcgis-layer · esriGeometryPolygon · 1 records · last edit 2019-07-24
- closes: not probed

### Little_Tokyo_August_Geofence_Events  ·    ·  from gis-hunter
- url: https://services5.arcgis.com/7nsPwEMP38bSkCjy/arcgis/rest/services/Little_Tokyo_August_Geofence_Events/FeatureServer/1
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: CREDIT · source item page · "General License usage LADOT: Transportation Technology/New Mobility LADOT: Transportation Technology/New Mobility" · item https://www.arcgis.com/home/item.html?id=aacd9d69a78f43cd94fc8c812441197f · owner Vlad_inthecity
- facts: arcgis-layer · esriGeometryPolygon · 1 records · last edit 2019-07-24
- closes: not probed

### Stephen F Austin slopes  ·    ·  from gis-hunter
- url: https://tiles.arcgis.com/tiles/gGHDlz6USftL5Pau/arcgis/rest/services/Stephen_F_Austin_slopes/MapServer/1
- WHY: no polygons (no geometry)
- publisher: ? → official (a federal / national agency named)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=756d7ad031e24f01a523e5ca52dd22d2 · owner USFS_SouthernResearchStation · org U.S. Forest Service
- facts: arcgis-layer
- closes: not probed

### Stephen F Austin aspects  ·    ·  from gis-hunter
- url: https://tiles.arcgis.com/tiles/gGHDlz6USftL5Pau/arcgis/rest/services/Stephen_F_Austin_aspects/MapServer/1
- WHY: no polygons (no geometry)
- publisher: ? → official (a federal / national agency named)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=0d4b00551b62450c9cf736db606f50d9 · owner USFS_SouthernResearchStation · org U.S. Forest Service
- facts: arcgis-layer
- closes: not probed

### Stephen F Austin NLCD  ·    ·  from gis-hunter
- url: https://tiles.arcgis.com/tiles/gGHDlz6USftL5Pau/arcgis/rest/services/Stephen_F_Austin_NLCD/MapServer/1
- WHY: no polygons (no geometry)
- publisher: ? → official (a federal / national agency named)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=13ff684fba224d3f87fd5b48bc14f21f · owner USFS_SouthernResearchStation · org U.S. Forest Service
- facts: arcgis-layer
- closes: not probed

### El Camino Real de Tierra Adentro National Historic Trail  ·    ·  from gis-hunter
- url: https://services7.arcgis.com/p0Gk2nDbPs7KEqSZ/arcgis/rest/services/ELCA_TRANS_CULT_ElCaminoRealdeTierraAdentroNHT_1/FeatureServer/0
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → official (government words: City of)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=252c1724e3f74ed0865414df4d9fb8fa · owner Jay.puckett_wsp5 · org City of Santa Fe
- facts: arcgis-layer · esriGeometryPolyline · name field UNITNAME · 5 records · last edit 2025-10-24
- closes: not probed

### El Camino Real de Tierra Adentro NHT  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/fBc8EJBxQRMcHlei/arcgis/rest/services/ELCA_NHT/FeatureServer/0
- WHY: the publisher closed it (internal / sign-in / by request)
- publisher: ? → official (a federal / national agency named)
- terms: CLOSED · source item page · "cal boundary, that crosses many ownership jurisdictions. Do not cross private land without permission. This data set should not be displayed or used at scales that exc" · item https://www.arcgis.com/home/item.html?id=0346eb3bab3b4a408e07cf120b58b292 · owner ntirres_nps · org National Park Service
- facts: arcgis-layer · esriGeometryPolyline · name field UNITNAME · 5 records · last edit 2021-08-02
- overlap: same publisher as akht
- closes: not probed

### Camino Real de Tierra Adentro  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/44C95LOqZjbh8Row/arcgis/rest/services/Camino_Real_de_Tierra_Adentro/FeatureServer/0
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=639a24d46b85400ba1d9722137598ae6 · owner Keelan.Vargas@du.edu_dugis
- facts: arcgis-layer · esriGeometryPolyline · 687 records · last edit 2022-09-10
- closes: not probed

### Mission_Dolores  ·    ·  from gis-hunter
- url: https://services8.arcgis.com/A76GjgcBUTTcwFGS/arcgis/rest/services/Mission_Dolores/FeatureServer/0
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=bb95b32ff1644ad780c5d0f7c9dfc661 · owner 014653886_SJSUGIS · org San Jose State University
- facts: arcgis-layer · esriGeometryPolygon · 1 records · last edit 2022-02-27
- closes: not probed

### GMUG Wild and Scenic River Evaluation  ·    ·  from gis-hunter
- url: https://services.arcgis.com/VfpeCk3ouKVuEwug/arcgis/rest/services/GMUG_Wild_and_Scenic_River_Evaluation/FeatureServer/1
- WHY: nothing stated about use on the item page or the service
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=29ffd76091dd4d7eb4567b989fd8e526 · owner AlisonGallensky
- facts: arcgis-layer · esriGeometryPolygon · name field Label · 50 records · last edit 2021-02-16 · sample 14 - Tabeguache Creek / 1A/B/C/D - Oh-be-joyful Creek and tributaries / 7 - West Elk Creek
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### San Felipe de Austin Buildings 1824  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/YWG34dhJxrbxQWdF/arcgis/rest/services/San_Felipe_de_Austin_Buildings_1824/FeatureServer/0
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=fd2f090270434b029e71d17ffe2687fb · owner lynnette.cen@glo.texas.gov
- facts: arcgis-layer · esriGeometryPoint · 17 records · last edit 2023-10-09
- closes: not probed

### San Felipe de Austin Buildings 1830  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/YWG34dhJxrbxQWdF/arcgis/rest/services/San_Felipe_de_Austin_Buildings_1830/FeatureServer/8
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=e949dd94fe4144dab8678a983888ab45 · owner lynnette.cen@glo.texas.gov
- facts: arcgis-layer · esriGeometryPoint · 71 records · last edit 2023-10-09
- closes: not probed

### San Felipe de Austin Buildings 1835  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/YWG34dhJxrbxQWdF/arcgis/rest/services/San_Felipe_de_Austin_Buildings_1835/FeatureServer/9
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=a67afa1d50a84dfc9496e01ea1970b6b · owner lynnette.cen@glo.texas.gov
- facts: arcgis-layer · esriGeometryPoint · 24 records · last edit 2023-10-09
- closes: not probed

### Chimney Rock Layer  ·    ·  from gis-hunter
- url: https://tiles.arcgis.com/tiles/C8EMgrsFcRFL6LrL/arcgis/rest/services/Map_3D4_WTL1/MapServer/0
- WHY: no polygons (no geometry)
- publisher: ? → official (a federal / national agency named)
- terms: OPEN · source item page · "tial copyright and related rights in these data worldwide through the Creative Commons Universal Public Domain Dedication (CC0-1.0) . NOAA, USGS NOAA, USGS" · item https://www.arcgis.com/home/item.html?id=5270b7713e974de69232456d842ded2d · owner sydney.luce_noaa · org NOAA GeoPlatform
- facts: arcgis-layer
- closes: not probed

### Chimney Rock Layer  ·    ·  from gis-hunter
- url: https://tiles.arcgis.com/tiles/C8EMgrsFcRFL6LrL/arcgis/rest/services/Map_3D4_WTL1/MapServer/1
- WHY: no polygons (no geometry)
- publisher: ? → official (a federal / national agency named)
- terms: OPEN · source item page · "tial copyright and related rights in these data worldwide through the Creative Commons Universal Public Domain Dedication (CC0-1.0) . NOAA, USGS NOAA, USGS" · item https://www.arcgis.com/home/item.html?id=5270b7713e974de69232456d842ded2d · owner sydney.luce_noaa · org NOAA GeoPlatform
- facts: arcgis-layer
- closes: not probed

### Chimney Rock Layer  ·    ·  from gis-hunter
- url: https://tiles.arcgis.com/tiles/C8EMgrsFcRFL6LrL/arcgis/rest/services/Map_3D4_WTL1/MapServer/2
- WHY: no polygons (no geometry)
- publisher: ? → official (a federal / national agency named)
- terms: OPEN · source item page · "tial copyright and related rights in these data worldwide through the Creative Commons Universal Public Domain Dedication (CC0-1.0) . NOAA, USGS NOAA, USGS" · item https://www.arcgis.com/home/item.html?id=5270b7713e974de69232456d842ded2d · owner sydney.luce_noaa · org NOAA GeoPlatform
- facts: arcgis-layer
- closes: not probed

### Chimney Rock Layer  ·    ·  from gis-hunter
- url: https://tiles.arcgis.com/tiles/C8EMgrsFcRFL6LrL/arcgis/rest/services/Map_3D4_WTL1/MapServer/3
- WHY: no polygons (no geometry)
- publisher: ? → official (a federal / national agency named)
- terms: OPEN · source item page · "tial copyright and related rights in these data worldwide through the Creative Commons Universal Public Domain Dedication (CC0-1.0) . NOAA, USGS NOAA, USGS" · item https://www.arcgis.com/home/item.html?id=5270b7713e974de69232456d842ded2d · owner sydney.luce_noaa · org NOAA GeoPlatform
- facts: arcgis-layer
- closes: not probed

### Chimney Rock Layer  ·    ·  from gis-hunter
- url: https://tiles.arcgis.com/tiles/C8EMgrsFcRFL6LrL/arcgis/rest/services/Map_3D4_WTL1/MapServer/4
- WHY: no polygons (no geometry)
- publisher: ? → official (a federal / national agency named)
- terms: OPEN · source item page · "tial copyright and related rights in these data worldwide through the Creative Commons Universal Public Domain Dedication (CC0-1.0) . NOAA, USGS NOAA, USGS" · item https://www.arcgis.com/home/item.html?id=5270b7713e974de69232456d842ded2d · owner sydney.luce_noaa · org NOAA GeoPlatform
- facts: arcgis-layer
- closes: not probed

### Chimney Rock Layer  ·    ·  from gis-hunter
- url: https://tiles.arcgis.com/tiles/C8EMgrsFcRFL6LrL/arcgis/rest/services/Map_3D4_WTL1/MapServer/5
- WHY: no polygons (no geometry)
- publisher: ? → official (a federal / national agency named)
- terms: OPEN · source item page · "tial copyright and related rights in these data worldwide through the Creative Commons Universal Public Domain Dedication (CC0-1.0) . NOAA, USGS NOAA, USGS" · item https://www.arcgis.com/home/item.html?id=5270b7713e974de69232456d842ded2d · owner sydney.luce_noaa · org NOAA GeoPlatform
- facts: arcgis-layer
- closes: not probed

### Chimney Rock Layer  ·    ·  from gis-hunter
- url: https://tiles.arcgis.com/tiles/C8EMgrsFcRFL6LrL/arcgis/rest/services/Map_3D4_WTL1/MapServer/6
- WHY: no polygons (no geometry)
- publisher: ? → official (a federal / national agency named)
- terms: OPEN · source item page · "tial copyright and related rights in these data worldwide through the Creative Commons Universal Public Domain Dedication (CC0-1.0) . NOAA, USGS NOAA, USGS" · item https://www.arcgis.com/home/item.html?id=5270b7713e974de69232456d842ded2d · owner sydney.luce_noaa · org NOAA GeoPlatform
- facts: arcgis-layer
- closes: not probed

### Chimney Rock Layer  ·    ·  from gis-hunter
- url: https://tiles.arcgis.com/tiles/C8EMgrsFcRFL6LrL/arcgis/rest/services/Map_3D4_WTL1/MapServer/7
- WHY: no polygons (no geometry)
- publisher: ? → official (a federal / national agency named)
- terms: OPEN · source item page · "tial copyright and related rights in these data worldwide through the Creative Commons Universal Public Domain Dedication (CC0-1.0) . NOAA, USGS NOAA, USGS" · item https://www.arcgis.com/home/item.html?id=5270b7713e974de69232456d842ded2d · owner sydney.luce_noaa · org NOAA GeoPlatform
- facts: arcgis-layer
- closes: not probed

### Chimney Rock_WFL1  ·    ·  from gis-hunter
- url: https://services5.arcgis.com/vTj647Rtyurkop78/arcgis/rest/services/Chimney_Rock_WFL1/FeatureServer/0
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=4c60630f985047afa89a7997df78a066 · owner jjbbrewer_WEIC
- facts: arcgis-layer · esriGeometryPoint · name field Name · 7 records · last edit 2025-04-22
- closes: not probed

### Chimney Rock_WFL1  ·    ·  from gis-hunter
- url: https://services5.arcgis.com/vTj647Rtyurkop78/arcgis/rest/services/Chimney_Rock_WFL1/FeatureServer/2
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=4c60630f985047afa89a7997df78a066 · owner jjbbrewer_WEIC
- facts: arcgis-layer · esriGeometryPolyline · 1 records · last edit 2025-04-22
- closes: not probed

### Chimney Rock_WFL1  ·    ·  from gis-hunter
- url: https://services5.arcgis.com/vTj647Rtyurkop78/arcgis/rest/services/Chimney_Rock_WFL1/FeatureServer/3
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=4c60630f985047afa89a7997df78a066 · owner jjbbrewer_WEIC
- facts: arcgis-layer · esriGeometryPolyline · 1 records · last edit 2025-04-22
- closes: not probed

### Chimney Rock_WFL1  ·    ·  from gis-hunter
- url: https://services5.arcgis.com/vTj647Rtyurkop78/arcgis/rest/services/Chimney_Rock_WFL1/FeatureServer/4
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=4c60630f985047afa89a7997df78a066 · owner jjbbrewer_WEIC
- facts: arcgis-layer · esriGeometryPolyline · 1 records · last edit 2025-04-22
- closes: not probed

### Chimney Rock_WFL1  ·    ·  from gis-hunter
- url: https://services5.arcgis.com/vTj647Rtyurkop78/arcgis/rest/services/Chimney_Rock_WFL1/FeatureServer/5
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=4c60630f985047afa89a7997df78a066 · owner jjbbrewer_WEIC
- facts: arcgis-layer · esriGeometryPolyline · 1 records · last edit 2025-04-22
- closes: not probed

### Chimney Rock_WFL1  ·    ·  from gis-hunter
- url: https://services5.arcgis.com/vTj647Rtyurkop78/arcgis/rest/services/Chimney_Rock_WFL1/FeatureServer/6
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=4c60630f985047afa89a7997df78a066 · owner jjbbrewer_WEIC
- facts: arcgis-layer · esriGeometryPolyline · 1 records · last edit 2025-04-22
- closes: not probed

### Chimney Rock_WFL1  ·    ·  from gis-hunter
- url: https://services5.arcgis.com/vTj647Rtyurkop78/arcgis/rest/services/Chimney_Rock_WFL1/FeatureServer/7
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=4c60630f985047afa89a7997df78a066 · owner jjbbrewer_WEIC
- facts: arcgis-layer · esriGeometryPolyline · 6 records · last edit 2025-04-22
- closes: not probed

### Chalco Hills Rec Area Features  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/VthbbMDEQLq4F9GE/arcgis/rest/services/Chalco_Hills_Rec_Area_Features/FeatureServer/0
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=b7d5b4eaa3d049a3831cd0f74f6d0f4c · owner jriebe0623 · org Papio-Missouri River NRD
- facts: arcgis-layer · esriGeometryPoint · 8 records · last edit 2024-08-21
- closes: not probed

### Chalco Hills Rec Area Features  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/VthbbMDEQLq4F9GE/arcgis/rest/services/Chalco_Hills_Rec_Area_Features/FeatureServer/1
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=b7d5b4eaa3d049a3831cd0f74f6d0f4c · owner jriebe0623 · org Papio-Missouri River NRD
- facts: arcgis-layer · esriGeometryPoint · name field name · 7 records · last edit 2025-04-01
- closes: not probed

### Chalco Hills Rec Area Features  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/VthbbMDEQLq4F9GE/arcgis/rest/services/Chalco_Hills_Rec_Area_Features/FeatureServer/2
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=b7d5b4eaa3d049a3831cd0f74f6d0f4c · owner jriebe0623 · org Papio-Missouri River NRD
- facts: arcgis-layer · esriGeometryPoint · 14 records · last edit 2024-08-21
- closes: not probed

### Chalco Hills Rec Area Features  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/VthbbMDEQLq4F9GE/arcgis/rest/services/Chalco_Hills_Rec_Area_Features/FeatureServer/3
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=b7d5b4eaa3d049a3831cd0f74f6d0f4c · owner jriebe0623 · org Papio-Missouri River NRD
- facts: arcgis-layer · esriGeometryPoint · name field Name · 3 records · last edit 2024-08-21
- closes: not probed

### Chalco Hills NatureTrails  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/VthbbMDEQLq4F9GE/arcgis/rest/services/Chalco_NatureTrails/FeatureServer/0
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → official (a government word of the country: Nature)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=7da54bdf814248afb733b6e7890d0901 · owner jriebe0623 · org Papio-Missouri River NRD
- facts: arcgis-layer · esriGeometryPolyline · 24 records · last edit 2024-07-01
- closes: not probed

### Chalco Hills Park Benches  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/VthbbMDEQLq4F9GE/arcgis/rest/services/Park_Benches/FeatureServer/0
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=7b0527baddd7489fa55c5d8c24114e47 · owner jriebe0623 · org Papio-Missouri River NRD
- facts: arcgis-layer · esriGeometryPoint · 57 records · last edit 2024-02-09
- closes: not probed

### Buckley SFB Accident Potential Zone  ·    ·  from gis-hunter
- url: https://ags.auroragov.org/aurora/rest/services/OpenData/MapServer/26
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → official (government words: City of)
- terms: CREDIT · source item page · "City of Aurora Colorado" · item https://ags.auroragov.org/aurora/rest/services/OpenData/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · 9 records
- closes: not probed

### HP_003_Buckley_WFL1  ·    ·  from gis-hunter
- url: https://services3.arcgis.com/1V8429k2MaAcIZUa/arcgis/rest/services/HP_003_Buckley_WFL1/FeatureServer/0
- WHY: nothing stated about use on the item page or the service
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=1a5451eadf474850b69ee7b1ab72ecd3 · owner louis_pino
- facts: arcgis-layer · esriGeometryPolygon · name field NAME10 · 64 records · last edit 2021-09-21 · sample Larimer / Las Animas / Fremont
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### HP_003_Buckley_WFL1  ·    ·  from gis-hunter
- url: https://services3.arcgis.com/1V8429k2MaAcIZUa/arcgis/rest/services/HP_003_Buckley_WFL1/FeatureServer/1
- WHY: nothing stated about use on the item page or the service
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=1a5451eadf474850b69ee7b1ab72ecd3 · owner louis_pino
- facts: arcgis-layer · esriGeometryPolygon · name field NAME20 · 478 records · last edit 2021-09-21 · sample Pritchett / Walsh / Palisade
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### HP_003_Buckley_WFL1  ·    ·  from gis-hunter
- url: https://services3.arcgis.com/1V8429k2MaAcIZUa/arcgis/rest/services/HP_003_Buckley_WFL1/FeatureServer/2
- WHY: nothing stated about use on the item page or the service
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=1a5451eadf474850b69ee7b1ab72ecd3 · owner louis_pino
- facts: arcgis-layer · esriGeometryPolygon · name field LONGNAME · 65 records · last edit 2021-09-21 · sample District 1 / District 2 / District 3
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### SP.003.Buckley  ·    ·  from gis-hunter
- url: https://services3.arcgis.com/1V8429k2MaAcIZUa/arcgis/rest/services/SP_003_Buckley_Renumbered/FeatureServer/0
- WHY: nothing stated about use on the item page or the service
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=1bf7cfc60e95413386ea042f87dd528c · owner louis_pino
- facts: arcgis-layer · esriGeometryPolygon · name field LONGNAME · 35 records · last edit 2021-09-21 · sample District 1 / District 2 / District 3
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### Vectorborne Surveillance Lone Star Ticks (2021)  ·    ·  from gis-hunter
- url: https://services6.arcgis.com/tuxY7TQIaDhLWARO/arcgis/rest/services/Vectorborne_Surveillance_Lone_Star_Ticks_2021/FeatureServer/0
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → official (government words: Department)
- terms: CREDIT · source item page · "Ohio Department of Health, Bureau of Infectious Diseases, Zoonotic Disease Program" · item https://www.arcgis.com/home/item.html?id=22de397cc27e4f9db3532f13d4f2aa40 · owner kxadmin
- facts: arcgis-layer · esriGeometryPolygon · 88 records · last edit 2021-12-08
- closes: not probed

### Appalachian_National_Scenic_Trail  ·    ·  from gis-hunter
- url: https://services6.arcgis.com/9tSn0MQDcjQ12ht2/arcgis/rest/services/Appalachian_National_Scenic_Trail/FeatureServer/0
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → official (a federal / national agency named)
- terms: CREDIT · source item page · "Although a large portion of this data is quite accurate, the information depicted is for general reference purposes only. These data are not legal documents and" · item https://www.arcgis.com/home/item.html?id=3594671562014d9e978c3b433f9b5bb7 · owner freemand
- facts: arcgis-layer · esriGeometryPolyline · name field Name · 3021 records · last edit 2022-05-05
- closes: not probed

### Appalachian National Scenic Trail  ·    ·  from gis-hunter
- url: https://services6.arcgis.com/krSNOBBGf8rF7cNp/arcgis/rest/services/Appalachian_National_Scenic_Trail/FeatureServer/0
- WHY: the publisher closed it (internal / sign-in / by request)
- publisher: ? → official (a federal / national agency named)
- terms: CLOSED · source item page · "es. Also please be aware that some of the features depicted may be on private land and showing them does not authorize, expressed or implied, the right to cross privat" · item https://www.arcgis.com/home/item.html?id=0da31740ce4b4ee290f2d828411b26a3 · owner jen.kern
- facts: arcgis-layer · esriGeometryPolyline · name field Name · 3029 records · last edit 2025-02-12
- closes: not probed

### Appalachian National Scenic Trail Centerline copy  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/qTQ6qYkHpxlu0G82/arcgis/rest/services/Appalachian_National_Scenic_Trail_Centerline_copy/FeatureServer/0
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=5e7f9a75d7d440d0816c45ede615b3ec · owner dff416_UofMD · org University of Maryland
- facts: arcgis-layer · esriGeometryPolyline · name field FEAT_NAME · 3208 records · last edit 2022-03-31
- closes: not probed

### Hitchiti EF aspects  ·    ·  from gis-hunter
- url: https://tiles.arcgis.com/tiles/gGHDlz6USftL5Pau/arcgis/rest/services/Hitchiti_aspects_2/MapServer/1
- WHY: no polygons (no geometry)
- publisher: ? → official (a federal / national agency named)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=68b9497d522e41cf93b5c3f2a29db521 · owner USFS_SouthernResearchStation · org U.S. Forest Service
- facts: arcgis-layer
- closes: not probed

### Hitchiti NLCD  ·    ·  from gis-hunter
- url: https://tiles.arcgis.com/tiles/gGHDlz6USftL5Pau/arcgis/rest/services/Hitchiti_NLCD/MapServer/1
- WHY: no polygons (no geometry)
- publisher: ? → official (a federal / national agency named)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=4131f468bfe14591b4501f0766e5920f · owner USFS_SouthernResearchStation · org U.S. Forest Service
- facts: arcgis-layer
- closes: not probed

### Hitchiti slopes  ·    ·  from gis-hunter
- url: https://tiles.arcgis.com/tiles/gGHDlz6USftL5Pau/arcgis/rest/services/Hitchiti_slopes_2/MapServer/1
- WHY: no polygons (no geometry)
- publisher: ? → official (a federal / national agency named)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=21517992c649446d872441ff36ff7c9b · owner USFS_SouthernResearchStation · org U.S. Forest Service
- facts: arcgis-layer
- closes: not probed

### CSKT Bison Range SSURGO Data  ·    ·  from gis-hunter
- url: https://services6.arcgis.com/PAUSLTOljlTRpN3n/arcgis/rest/services/CSKT_Bison_Range_SSURGO_Data/FeatureServer/0
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (Institute in the publisher words)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=2ad28e2e177c43a1b7e7000ffaebee72 · owner Kyle.Bocinsky_DRIGIS4 · org Desert Research Institute
- facts: arcgis-layer · esriGeometryPolygon · name field Subbasin_name · 1 records · last edit 2023-05-16 · sample LowerFlathead
- closes: not probed

### CSKT Bison Range SSURGO Data  ·    ·  from gis-hunter
- url: https://services6.arcgis.com/PAUSLTOljlTRpN3n/arcgis/rest/services/CSKT_Bison_Range_SSURGO_Data/FeatureServer/1
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (Institute in the publisher words)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=2ad28e2e177c43a1b7e7000ffaebee72 · owner Kyle.Bocinsky_DRIGIS4 · org Desert Research Institute
- facts: arcgis-layer · esriGeometryPolygon · name field muname · 17519 records · last edit 2023-05-16 · sample Andic Dystrochrepts-Umbric Vitrandepts complex, kames and ke / Courville-Winfall complex, 4 to 15 percent slopes / McCay family, broadly convex ridges, weakly weathered metamo
- closes: not probed

### PGF2020_HSCLIP_Devils_Elbow  ·    ·  from gis-hunter
- url: https://tiles.arcgis.com/tiles/ISqEHdhr3detVO9I/arcgis/rest/services/PGF2020_HSCLIP_Devils_Elbow/MapServer/1
- WHY: no polygons (no geometry)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=9210ab70e2074bfabbfa5ee77ed86c03 · owner jro156_UCNZ
- facts: arcgis-layer
- closes: not probed

### UC2024_HSCLIP_Devils_Elbow  ·    ·  from gis-hunter
- url: https://tiles.arcgis.com/tiles/ISqEHdhr3detVO9I/arcgis/rest/services/UC2024_HSCLIP_Devils_Elbow/MapServer/1
- WHY: no polygons (no geometry)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=234f087292a647329c92168fdc640277 · owner jro156_UCNZ
- facts: arcgis-layer
- closes: not probed

### Big_Horn_Study_Area  ·    ·  from gis-hunter
- url: https://services.arcgis.com/xYjDUN35YwdCEcMm/arcgis/rest/services/Big_Horn_Study_Area/FeatureServer/1
- WHY: nothing stated about use on the item page or the service
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=cae8bba75c5048408904daaec08f559b · owner BGIS_ON_F21_Luigi_Ralph_Malinis
- facts: arcgis-layer · esriGeometryPolygon · name field PRNAME · 1 records · last edit 2022-08-15 · sample British Columbia / Colombie-Britannique
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### Map of Big Horn Co WY 1908ca _low0_jpg  ·    ·  from gis-hunter
- url: https://tiles.arcgis.com/tiles/KbxwQRRfWyEYLgp4/arcgis/rest/services/Map_of_Big_Horn_Co_WY_1908ca__low0_jpg/MapServer/0
- WHY: the publisher closed it (internal / sign-in / by request)
- publisher: ? → official (a federal / national agency named)
- terms: CLOSED · source item page · "NON-BLM DATA - FOR INTERNAL USE ONLY. Users assume the entire risk associated with use of these data. The BLM has no liability" · item https://www.arcgis.com/home/item.html?id=09998ddf05fb482fafb6d0fba93152b8 · owner BLM_WY_Public · org Bureau of Land Management
- facts: arcgis-layer
- closes: not probed

### NinePipe_Map5  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/ERdCHt0sNM6dENSD/arcgis/rest/services/NinePipe_Map5/FeatureServer/1
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=937de526c84642e2bb43d0bc55b2a76d · owner mr119648_umontana · org University of Montana | Academic and Research Site
- facts: arcgis-layer · esriGeometryPolygon · 8 records · last edit 2025-10-01
- closes: not probed

### San Pablo Bay NWR Ridgway's Rail Call Count Stations  ·    ·  from gis-hunter
- url: https://services.arcgis.com/QVENGdaPbd4LUkLV/arcgis/rest/services/San_Pablo_Bay_Rail_Call_Count_Stations/FeatureServer/0
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → official (a federal / national agency named)
- terms: CREDIT · source item page · "herein. While the Service makes every reasonable effort to ensure the accuracy and completeness of data provided for distribution, it may not have the necessary accurac" · item https://www.arcgis.com/home/item.html?id=491a34a783fa412faa87b5a2358a8d70 · owner madison_pitman@fws.gov_fws · org U.S. Fish & Wildlife Service
- facts: arcgis-layer · esriGeometryPoint · name field SITENAME · 45 records · last edit 2026-01-08
- overlap: same publisher as sgazd
- closes: not probed

### Urban Design Standards Designated Streets - North Highline  ·    ·  from gis-hunter
- url: https://services.arcgis.com/Ej0PsM5Aw677QF1W/arcgis/rest/services/URBAN_DESIGN_STANDARDS_STREETS_LINE_3008/FeatureServer/0
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → official (government words: County)
- terms: CREDIT · source item page · "dept/kcit/data-information-services/gis-center/about/terms-conditions-copyrights King County" · item https://www.arcgis.com/home/item.html?id=d96068b5e84143e8b8293db7c6390cde · owner KingCounty · org King County
- facts: arcgis-layer · esriGeometryPolyline · name field FULLNAME · 863 records · last edit 2026-10-14
- closes: not probed

### Government_Highline_Canal  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/QjiQKkFtXufcXWpu/arcgis/rest/services/Government_Highline_Canal/FeatureServer/0
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → official (a government word of the country: Government)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=8f08d789d5b944beb2fc5e7c2b746df1 · owner KaseyDH
- facts: arcgis-layer · esriGeometryPoint · 2248 records · last edit 2016-04-22
- closes: not probed

### Government_Highline_Canal  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/QjiQKkFtXufcXWpu/arcgis/rest/services/Government_Highline_Canal/FeatureServer/1
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → official (a government word of the country: Government)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=8f08d789d5b944beb2fc5e7c2b746df1 · owner KaseyDH
- facts: arcgis-layer · esriGeometryPoint · 281 records · last edit 2016-04-22
- closes: not probed

### Government_Highline_Canal  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/QjiQKkFtXufcXWpu/arcgis/rest/services/Government_Highline_Canal/FeatureServer/2
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → official (a government word of the country: Government)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=8f08d789d5b944beb2fc5e7c2b746df1 · owner KaseyDH
- facts: arcgis-layer · esriGeometryPoint · 253 records · last edit 2016-04-22
- closes: not probed

### Government_Highline_Canal  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/QjiQKkFtXufcXWpu/arcgis/rest/services/Government_Highline_Canal/FeatureServer/3
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → official (a government word of the country: Government)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=8f08d789d5b944beb2fc5e7c2b746df1 · owner KaseyDH
- facts: arcgis-layer · esriGeometryPoint · 28 records · last edit 2016-04-22
- closes: not probed

### Government_Highline_Canal  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/QjiQKkFtXufcXWpu/arcgis/rest/services/Government_Highline_Canal/FeatureServer/4
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → official (a government word of the country: Government)
- terms: CREDIT · source item page · "GVDD, GVWUA" · item https://www.arcgis.com/home/item.html?id=8f08d789d5b944beb2fc5e7c2b746df1 · owner KaseyDH
- facts: arcgis-layer · esriGeometryPoint · 74 records · last edit 2016-04-22
- closes: not probed

### Government_Highline_Canal  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/QjiQKkFtXufcXWpu/arcgis/rest/services/Government_Highline_Canal/FeatureServer/5
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → official (a government word of the country: Government)
- terms: CREDIT · source item page · "GVWUA" · item https://www.arcgis.com/home/item.html?id=8f08d789d5b944beb2fc5e7c2b746df1 · owner KaseyDH
- facts: arcgis-layer · esriGeometryPoint · 235 records · last edit 2016-05-04
- closes: not probed

### Government_Highline_Canal  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/QjiQKkFtXufcXWpu/arcgis/rest/services/Government_Highline_Canal/FeatureServer/6
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → official (a government word of the country: Government)
- terms: CREDIT · source item page · "GVWUA, GVDD" · item https://www.arcgis.com/home/item.html?id=8f08d789d5b944beb2fc5e7c2b746df1 · owner KaseyDH
- facts: arcgis-layer · esriGeometryPoint · name field NAME · 13 records · last edit 2016-04-22
- closes: not probed

### Government_Highline_Canal  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/QjiQKkFtXufcXWpu/arcgis/rest/services/Government_Highline_Canal/FeatureServer/7
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → official (a government word of the country: Government)
- terms: CREDIT · source item page · "GVWUA" · item https://www.arcgis.com/home/item.html?id=8f08d789d5b944beb2fc5e7c2b746df1 · owner KaseyDH
- facts: arcgis-layer · esriGeometryPolyline · 445 records · last edit 2016-04-22
- closes: not probed

### OLSP Native Trails StoryMap Dominguez and Escalante Map Image  ·    ·  from gis-hunter
- url: https://tiles.arcgis.com/tiles/zbiOJznElr9EGpUY/arcgis/rest/services/DominguezEscalante/MapServer/0
- WHY: no polygons (no geometry)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=a5aa2c6876b34532addefe3a696b2caf · owner jscala_univofnm
- facts: arcgis-layer
- closes: not probed

### Black Canyon Golf Course_view  ·    ·  from gis-hunter
- url: https://services3.arcgis.com/arjIZiPnUOHQnhsl/arcgis/rest/services/Black_Canyon_Golf_Course_/FeatureServer/1
- WHY: the publisher closed it (internal / sign-in / by request)
- publisher: ? → official (government words: City of)
- terms: CLOSED · source item page · "LIMITED DISTRIBUTION This data is intended for official use only, pursuant to the needs of the City of Montrose and authorized staff operating on its beha" · item https://www.arcgis.com/home/item.html?id=057d0f0ab1634eb4aeae5d7e47bf5a95 · owner GISAdmin_Montrose
- facts: arcgis-layer · esriGeometryPolygon · 21 records · last edit 2026-02-18
- closes: not probed

### Black Canyon Golf Course_view  ·    ·  from gis-hunter
- url: https://services3.arcgis.com/arjIZiPnUOHQnhsl/arcgis/rest/services/Black_Canyon_Golf_Course_/FeatureServer/2
- WHY: the publisher closed it (internal / sign-in / by request)
- publisher: ? → official (government words: City of)
- terms: CLOSED · source item page · "LIMITED DISTRIBUTION This data is intended for official use only, pursuant to the needs of the City of Montrose and authorized staff operating on its beha" · item https://www.arcgis.com/home/item.html?id=057d0f0ab1634eb4aeae5d7e47bf5a95 · owner GISAdmin_Montrose
- facts: arcgis-layer · esriGeometryPolygon · 20 records · last edit 2026-02-18
- closes: not probed

### Black Canyon Golf Course_view  ·    ·  from gis-hunter
- url: https://services3.arcgis.com/arjIZiPnUOHQnhsl/arcgis/rest/services/Black_Canyon_Golf_Course_/FeatureServer/3
- WHY: the publisher closed it (internal / sign-in / by request)
- publisher: ? → official (government words: City of)
- terms: CLOSED · source item page · "LIMITED DISTRIBUTION This data is intended for official use only, pursuant to the needs of the City of Montrose and authorized staff operating on its beha" · item https://www.arcgis.com/home/item.html?id=057d0f0ab1634eb4aeae5d7e47bf5a95 · owner GISAdmin_Montrose
- facts: arcgis-layer · esriGeometryPolygon · 5 records · last edit 2026-02-18
- closes: not probed

### Black Canyon Golf Course_view  ·    ·  from gis-hunter
- url: https://services3.arcgis.com/arjIZiPnUOHQnhsl/arcgis/rest/services/Black_Canyon_Golf_Course_/FeatureServer/4
- WHY: the publisher closed it (internal / sign-in / by request)
- publisher: ? → official (government words: City of)
- terms: CLOSED · source item page · "LIMITED DISTRIBUTION This data is intended for official use only, pursuant to the needs of the City of Montrose and authorized staff operating on its beha" · item https://www.arcgis.com/home/item.html?id=057d0f0ab1634eb4aeae5d7e47bf5a95 · owner GISAdmin_Montrose
- facts: arcgis-layer · esriGeometryPolygon · 26 records · last edit 2026-02-18
- closes: not probed

### Black Canyon Golf Course_view  ·    ·  from gis-hunter
- url: https://services3.arcgis.com/arjIZiPnUOHQnhsl/arcgis/rest/services/Black_Canyon_Golf_Course_/FeatureServer/5
- WHY: the publisher closed it (internal / sign-in / by request)
- publisher: ? → official (government words: City of)
- terms: CLOSED · source item page · "LIMITED DISTRIBUTION This data is intended for official use only, pursuant to the needs of the City of Montrose and authorized staff operating on its beha" · item https://www.arcgis.com/home/item.html?id=057d0f0ab1634eb4aeae5d7e47bf5a95 · owner GISAdmin_Montrose
- facts: arcgis-layer · esriGeometryPolygon · 56 records · last edit 2026-02-18
- closes: not probed

### Black Canyon City and Arizona Water_WFL1  ·    ·  from gis-hunter
- url: https://services3.arcgis.com/0OPQIK59PJJqLK0A/arcgis/rest/services/Black_Canyon_City_and_Arizona_Water_WFL1/FeatureServer/1
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=624399e229c14166b6cce81f5c594ff9 · owner estreber_asu · org Arizona State University
- facts: arcgis-layer · esriGeometryPolygon · name field NAME · 35 records · last edit 2025-10-01 · sample Colorado Plateaus aquifers / Coconino-De Chelly aquifer / EIW
- closes: not probed

### Black Canyon City and Arizona Water_WFL1  ·    ·  from gis-hunter
- url: https://services3.arcgis.com/0OPQIK59PJJqLK0A/arcgis/rest/services/Black_Canyon_City_and_Arizona_Water_WFL1/FeatureServer/2
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=624399e229c14166b6cce81f5c594ff9 · owner estreber_asu · org Arizona State University
- facts: arcgis-layer · esriGeometryPolygon · name field BASIN_NAME · 10 records · last edit 2025-10-01 · sample SANTA CRUZ AMA / HUALAPAI VALLEY INA / JOSEPH CITY INA
- closes: not probed

### Black Canyon City and Arizona Water_WFL1  ·    ·  from gis-hunter
- url: https://services3.arcgis.com/0OPQIK59PJJqLK0A/arcgis/rest/services/Black_Canyon_City_and_Arizona_Water_WFL1/FeatureServer/3
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=624399e229c14166b6cce81f5c594ff9 · owner estreber_asu · org Arizona State University
- facts: arcgis-layer · esriGeometryPolygon · 85 records · last edit 2025-10-01
- closes: not probed

### Black Canyon City and Arizona Water_WFL1  ·    ·  from gis-hunter
- url: https://services3.arcgis.com/0OPQIK59PJJqLK0A/arcgis/rest/services/Black_Canyon_City_and_Arizona_Water_WFL1/FeatureServer/4
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=624399e229c14166b6cce81f5c594ff9 · owner estreber_asu · org Arizona State University
- facts: arcgis-layer · esriGeometryPolygon · name field NAME · 15 records · last edit 2025-10-01 · sample APACHE / COCHISE / COCONINO
- closes: not probed

### Black Canyon City and Arizona Water_WFL1  ·    ·  from gis-hunter
- url: https://services3.arcgis.com/0OPQIK59PJJqLK0A/arcgis/rest/services/Black_Canyon_City_and_Arizona_Water_WFL1/FeatureServer/5
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=624399e229c14166b6cce81f5c594ff9 · owner estreber_asu · org Arizona State University
- facts: arcgis-layer · esriGeometryPolygon · 1 records · last edit 2025-10-01
- closes: not probed

### Black Canyon City and Arizona Water_WFL1  ·    ·  from gis-hunter
- url: https://services3.arcgis.com/0OPQIK59PJJqLK0A/arcgis/rest/services/Black_Canyon_City_and_Arizona_Water_WFL1/FeatureServer/6
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=624399e229c14166b6cce81f5c594ff9 · owner estreber_asu · org Arizona State University
- facts: arcgis-layer · esriGeometryPolygon · 85 records · last edit 2025-10-01
- closes: not probed

### Black Canyon City_ Arizona_WFL1  ·    ·  from gis-hunter
- url: https://services3.arcgis.com/0OPQIK59PJJqLK0A/arcgis/rest/services/Black_Canyon_City__Arizona_WFL1/FeatureServer/1
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=7dd7b4558eb94913ac8ff685439e6386 · owner estreber_asu · org Arizona State University
- facts: arcgis-layer · esriGeometryPolygon · name field Name · 91 records · last edit 2025-10-01 · sample Dewey-Humboldt / Wickenburg / Casa Grande
- closes: not probed

### Black Canyon City_ Arizona_WFL1  ·    ·  from gis-hunter
- url: https://services3.arcgis.com/0OPQIK59PJJqLK0A/arcgis/rest/services/Black_Canyon_City__Arizona_WFL1/FeatureServer/2
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=7dd7b4558eb94913ac8ff685439e6386 · owner estreber_asu · org Arizona State University
- facts: arcgis-layer · esriGeometryPolygon · name field GNIS_NAME · 1699 records · last edit 2025-10-01 · sample   /   /  
- closes: not probed

### Black Canyon City_ Arizona_WFL1  ·    ·  from gis-hunter
- url: https://services3.arcgis.com/0OPQIK59PJJqLK0A/arcgis/rest/services/Black_Canyon_City__Arizona_WFL1/FeatureServer/3
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=7dd7b4558eb94913ac8ff685439e6386 · owner estreber_asu · org Arizona State University
- facts: arcgis-layer · esriGeometryPolygon · name field NAME · 15 records · last edit 2025-10-01 · sample APACHE / COCHISE / COCONINO
- closes: not probed

### Black Canyon City_ Arizona_WFL1  ·    ·  from gis-hunter
- url: https://services3.arcgis.com/0OPQIK59PJJqLK0A/arcgis/rest/services/Black_Canyon_City__Arizona_WFL1/FeatureServer/4
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=7dd7b4558eb94913ac8ff685439e6386 · owner estreber_asu · org Arizona State University
- facts: arcgis-layer · esriGeometryPolygon · 1 records · last edit 2025-10-01
- closes: not probed

### Arizona_National_Scenic_Trail_Feature_Layers_view  ·    ·  from gis-hunter
- url: https://services3.arcgis.com/IKBBLZOXy58PXgpl/arcgis/rest/services/Arizona_National_Scenic_Trail_Feature_Layers_view/FeatureServer/6
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → official (a government word of the country: National)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=4ce205e6acff49a698fa2d012c727f95 · owner AZTrail · org Arizona Trail Association
- facts: arcgis-layer · esriGeometryPolygon · 138 records · last edit 2026-09-04
- closes: not probed

### Arizona National Scenic Trail Scenic Resources view  ·    ·  from gis-hunter
- url: https://services3.arcgis.com/IKBBLZOXy58PXgpl/arcgis/rest/services/Scenic_Resources_AGOL_view/FeatureServer/8
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → official (a government word of the country: National)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=24fb6ad8459e4177b70bf91e696776b7 · owner AZTrail · org Arizona Trail Association
- facts: arcgis-layer · esriGeometryPoint · name field name · 26 records · last edit 2026-09-04
- closes: not probed

### Arizona National Scenic Trail Scenic Resources view  ·    ·  from gis-hunter
- url: https://services3.arcgis.com/IKBBLZOXy58PXgpl/arcgis/rest/services/Scenic_Resources_AGOL_view/FeatureServer/0
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → official (a government word of the country: National)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=24fb6ad8459e4177b70bf91e696776b7 · owner AZTrail · org Arizona Trail Association
- facts: arcgis-layer · esriGeometryPoint · name field name · 2117 records · last edit 2026-09-04
- closes: not probed

### Arizona National Scenic Trail Scenic Resources view  ·    ·  from gis-hunter
- url: https://services3.arcgis.com/IKBBLZOXy58PXgpl/arcgis/rest/services/Scenic_Resources_AGOL_view/FeatureServer/1
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → official (a government word of the country: National)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=24fb6ad8459e4177b70bf91e696776b7 · owner AZTrail · org Arizona Trail Association
- facts: arcgis-layer · esriGeometryPoint · name field name · 305 records · last edit 2026-09-04
- closes: not probed

### Arizona National Scenic Trail Scenic Resources view  ·    ·  from gis-hunter
- url: https://services3.arcgis.com/IKBBLZOXy58PXgpl/arcgis/rest/services/Scenic_Resources_AGOL_view/FeatureServer/2
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → official (a government word of the country: National)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=24fb6ad8459e4177b70bf91e696776b7 · owner AZTrail · org Arizona Trail Association
- facts: arcgis-layer · esriGeometryPoint · name field name · 230 records · last edit 2026-09-04
- closes: not probed

### Honeymoon_Photos_20230609  ·    ·  from gis-hunter
- url: https://services7.arcgis.com/OQmrTvuHcbVXxUp1/arcgis/rest/services/Honeymoon_Photos_20230609/FeatureServer/0
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=c4ad72a067844392b09c13109b976d07 · owner mstotts22
- facts: arcgis-layer · esriGeometryPoint · name field Site · 46 records · last edit 2023-06-23
- closes: not probed

### Spencer's Tract Air Photo Collection  ·    ·  from gis-hunter
- url: https://services.arcgis.com/rGKxabTU9mcXMw7k/arcgis/rest/services/ST/FeatureServer/0
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: NON-COMMERCIAL · source item page · "This work is licensed under a Creative Commons Attribution-NonCommercial 4.0 International License." · item https://www.arcgis.com/home/item.html?id=680702d194ed453e823a85e9c6313dfc · owner jfulle32 · org Western University
- facts: arcgis-layer · esriGeometryPoint · name field Legend_Label · 240 records · last edit 2021-08-27
- closes: not probed

### Spencer_Asset_Management_Dec2024  ·    ·  from gis-hunter
- url: https://services8.arcgis.com/ZybleXItoWGv9yUU/arcgis/rest/services/Spencer_Asset_Management_Dec2024/FeatureServer/4
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=ee2442d4f6de4e8a998c24d8effa7756 · owner mgeorge2382
- facts: arcgis-layer · esriGeometryPolygon · 1 records · last edit 2025-10-15
- closes: not probed

### Spencer_Asset_Management_Dec2024  ·    ·  from gis-hunter
- url: https://services8.arcgis.com/ZybleXItoWGv9yUU/arcgis/rest/services/Spencer_Asset_Management_Dec2024/FeatureServer/5
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → official (government words: Town of)
- terms: CREDIT · source item page · "Applied Geographics, Boston, MA; CGIS Mapping, Marion, MA; Town of Spencer Assessor's Office, Spencer, MA." · item https://www.arcgis.com/home/item.html?id=ee2442d4f6de4e8a998c24d8effa7756 · owner mgeorge2382
- facts: arcgis-layer · esriGeometryPolygon · 5226 records · last edit 2025-10-15
- closes: not probed

### Lieber  ·    ·  from gis-hunter
- url: https://services-eu1.arcgis.com/de9awAHJGTPtVVLW/arcgis/rest/services/Lieber/FeatureServer/5
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=3ce129da783a49fda68d8e1dd3ed2ae9 · owner g.foliot · org IR* HUMA-NUM
- facts: arcgis-layer · esriGeometryPolygon · 1 records · last edit 2022-11-23
- closes: not probed

### Lieber  ·    ·  from gis-hunter
- url: https://services-eu1.arcgis.com/de9awAHJGTPtVVLW/arcgis/rest/services/Lieber/FeatureServer/6
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=3ce129da783a49fda68d8e1dd3ed2ae9 · owner g.foliot · org IR* HUMA-NUM
- facts: arcgis-layer · esriGeometryPolygon · 1 records · last edit 2022-11-23
- closes: not probed

### Fairfax County Water Resources Monitoring Network monitoring stations  ·    ·  from gis-hunter
- url: https://services.arcgis.com/v01gqwM5QqNysAAi/arcgis/rest/services/Fairfax_monitoring_sites/FeatureServer/0
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → official (a federal / national agency named)
- terms: CREDIT · source item page · "ccessfully on a computer system at the U.S. Geological Survey (USGS), no warranty expressed or implied is made regarding the display or utility of the data on any other sy" · item https://www.arcgis.com/home/item.html?id=57a54f9f4d994fe6b82a5630058e0f1e · owner ckandel@usgs.gov_USGS · org U.S. Geological Survey
- facts: arcgis-layer · esriGeometryPoint · name field site_no · 21 records · last edit 2024-01-12
- closes: not probed

### Salt Water Limit  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/FjPcSmEFuDYlIdKC/arcgis/rest/services/Salt_Water_Limit/FeatureServer/0
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → official (government words: Department)
- terms: OPEN · source item page · "CC0 CTDEEP CTDEEP" · item https://www.arcgis.com/home/item.html?id=cf96fdfbd01b42bca3b8350c35c29169 · owner deepgis · org Department of Energy & Environmental Protection
- facts: arcgis-layer · esriGeometryPolyline · name field QUAD_NAME · 453 records · last edit 2021-02-19
- overlap: same publisher as ctd
- closes: not probed

### Mule Deer Migration Corridors - Salt Springs - 2018-2020 [ds2975]  ·    ·  from gis-hunter
- url: https://services2.arcgis.com/Uq9r85Potqm3MfRV/arcgis/rest/services/biosds2975_fpu/FeatureServer/0
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → official (government words: Department)
- terms: OPEN · source item page · "License: This work is licensed under Creative Commons Attribution 4.0 International License ( https://creativecommons.org/licenses/by/4.0/ ). U" · item https://www.arcgis.com/home/item.html?id=219912a6bd714ea4a49c9a191eb11309 · owner BIOS_Admin · org California Department of Fish and Wildlife
- facts: arcgis-layer · esriGeometryPolygon · 3 records · last edit 2025-07-30
- overlap: same publisher as sgcaa
- closes: not probed

### Great Salt Lake Basin  ·    ·  from gis-hunter
- url: https://services.arcgis.com/ZzrwjTRez6FJiOq4/arcgis/rest/services/Great_Salt_Lake_Basin/FeatureServer/3
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → official (government words: DNR)
- terms: OPEN · source item page · "CC BY-SA Disclaimer: For reference use only. Although this product represents the work of natur" · item https://www.arcgis.com/home/item.html?id=ceb4e87f7f664fe8a81e8418cafb226a · owner dnrwres · org Utah DNR Online Maps
- facts: arcgis-layer · esriGeometryPolygon · 2 records · last edit 2023-02-07
- overlap: same publisher as sguta
- closes: not probed

### Pine Grove_WFL1  ·    ·  from gis-hunter
- url: https://services.arcgis.com/aMv9lrl6jFsuGNu8/arcgis/rest/services/Pine_Grove_WFL1/FeatureServer/0
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=4e057fd44e1b4af987aa42862ea85f9b · owner heschmidt_smithcollege · org Smith College Spatial Analysis Lab
- facts: arcgis-layer · esriGeometryPolygon · 15 records · last edit 2021-12-01
- closes: not probed

### Pine Grove_WFL1  ·    ·  from gis-hunter
- url: https://services.arcgis.com/aMv9lrl6jFsuGNu8/arcgis/rest/services/Pine_Grove_WFL1/FeatureServer/1
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=4e057fd44e1b4af987aa42862ea85f9b · owner heschmidt_smithcollege · org Smith College Spatial Analysis Lab
- facts: arcgis-layer · esriGeometryPolygon · 24 records · last edit 2021-12-01
- closes: not probed

### Pine Grove_WFL1  ·    ·  from gis-hunter
- url: https://services.arcgis.com/aMv9lrl6jFsuGNu8/arcgis/rest/services/Pine_Grove_WFL1/FeatureServer/2
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=4e057fd44e1b4af987aa42862ea85f9b · owner heschmidt_smithcollege · org Smith College Spatial Analysis Lab
- facts: arcgis-layer · esriGeometryPolygon · name field SITE · 1 records · last edit 2021-12-01 · sample  
- closes: not probed

### Pine Grove_WFL1  ·    ·  from gis-hunter
- url: https://services.arcgis.com/aMv9lrl6jFsuGNu8/arcgis/rest/services/Pine_Grove_WFL1/FeatureServer/4
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=4e057fd44e1b4af987aa42862ea85f9b · owner heschmidt_smithcollege · org Smith College Spatial Analysis Lab
- facts: arcgis-layer · esriGeometryPolygon · 34 records · last edit 2021-12-01
- closes: not probed

### DEEP_State_Cartop_Boat_Launches (In Use)  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/FjPcSmEFuDYlIdKC/arcgis/rest/services/DEEP_State_Cartop_Boat_Launches/FeatureServer/0
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → official (government words: Department)
- terms: CREDIT · source item page · "CT DEEP CT DEEP" · item https://www.arcgis.com/home/item.html?id=02fdebe5bce44352aefaac5e704285be · owner deepgis · org Department of Energy & Environmental Protection
- facts: arcgis-layer · esriGeometryPoint · name field PROPERTY · 25 records · last edit 2024-01-02
- overlap: same publisher as ctd
- closes: not probed

### Cartop Boat Launches  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/FjPcSmEFuDYlIdKC/arcgis/rest/services/CT_Cartop_Boat_Launches/FeatureServer/0
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → official (government words: Department)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=f4342d7be28a4aefb718ff1d7ee626da · owner deepgis · org Department of Energy & Environmental Protection
- facts: arcgis-layer · esriGeometryPoint · name field PROPERTY · 30 records
- overlap: same publisher as ctd
- closes: not probed

### New Harmony Water Courses  ·    ·  from gis-hunter
- url: https://services3.arcgis.com/m5XxgtLpUcsjOiD1/arcgis/rest/services/New_Harmony_Water_Courses/FeatureServer/2
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → official (government words: County)
- terms: CREDIT · source item page · "nties with regard to the use of this dataset. Users are encouraged to attribute content to: State of Utah, SGID.This product is for informational purposes and may not ha" · item https://www.arcgis.com/home/item.html?id=edaec38ca60148618bde9921c9fcf6d5 · owner giswashco · org Washington County AGOL
- facts: arcgis-layer · esriGeometryPolyline · name field NAME · 575 records · last edit 2023-12-11
- closes: not probed

### 147 - Cape Henry, VA (44099)  ·    ·  from gis-hunter
- url: https://services6.arcgis.com/2DGR1sZBUvcPcd8Z/arcgis/rest/services/147_Cape_Henry_VA_44099_/FeatureServer/0
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: CREDIT · source item page · ""The data may be used and redistributed for free but is not intended for legal use, since it may contain inaccuracies. Neither the data Contributor, ERD, NOAA, no" · item https://www.arcgis.com/home/item.html?id=14db4f644ae44f10a2ca445e5af24330 · owner jerad.king · org GCOOS
- facts: arcgis-layer · esriGeometryPoint · 514099 records · last edit 2025-03-20
- closes: not probed

### Vegetation Map of North Cascades National Park Service Complex  ·    ·  from gis-hunter
- url: https://tiles.arcgis.com/tiles/fBc8EJBxQRMcHlei/arcgis/rest/services/NOCA_VegMap/MapServer/0
- WHY: no polygons (no geometry)
- publisher: ? → hosted for an agency (a university account holds an agency layer)
- terms: CREDIT · source item page · "general and these data in particular. The National Park Service gives no warranty, expressed or implied, as to the accuracy, reliability, or completeness of these data. Al" · item https://www.arcgis.com/home/item.html?id=bdc4943bc34243d99a2f3dec508237ec · owner NAntonova@nps.gov_nps · org National Park Service
- facts: arcgis-layer
- closes: not probed

### North Cascades NP Vegetation  ·    ·  from gis-hunter
- url: https://tiles.arcgis.com/tiles/qboYD3ru0louQq4F/arcgis/rest/services/North_Cascades_NP_Vegetation/MapServer/0
- WHY: no polygons (no geometry)
- publisher: ? → hosted for an agency (a university account holds an agency layer)
- terms: CREDIT · source item page · "general and these data in particular. The National Park Service gives no warranty, expressed or implied, as to the accuracy, reliability, or completeness of these data. Al" · item https://www.arcgis.com/home/item.html?id=e9e7a8e8267d4490a6e7f85f446e0627 · owner szegedk_wwu · org Western Washington University (Academic)
- facts: arcgis-layer · name field NAME
- closes: not probed

### Cornelius Impervious Tiers_WFL1  ·    ·  from gis-hunter
- url: https://services.arcgis.com/BWD3gDuaqc7SQmy7/arcgis/rest/services/Cornelius_Impervious_Tiers_WFL1/FeatureServer/1
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → official (government words: County)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=7b666e40a4ac4636aedb6023197dd8c7 · owner Nir.Josipovich@mecklenburgcountync.gov_meckgov · org Mecklenburg County GIS
- facts: arcgis-layer · esriGeometryPolygon · 33253 records · last edit 2020-10-02
- closes: not probed

### Cornelius Impervious Tiers_WFL1  ·    ·  from gis-hunter
- url: https://services.arcgis.com/BWD3gDuaqc7SQmy7/arcgis/rest/services/Cornelius_Impervious_Tiers_WFL1/FeatureServer/2
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → official (government words: County)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=7b666e40a4ac4636aedb6023197dd8c7 · owner Nir.Josipovich@mecklenburgcountync.gov_meckgov · org Mecklenburg County GIS
- facts: arcgis-layer · esriGeometryPolygon · 16718 records · last edit 2022-06-15
- closes: not probed

### Cornelius Bike Ped Public Comments  ·    ·  from gis-hunter
- url: https://services2.arcgis.com/ZkOsbg84o8DsPPaP/arcgis/rest/services/Cornelius_Bike_Ped_Public_Comments/FeatureServer/0
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=6fcb7bb455774f8e9de653fbdbde45c2 · owner Davidsa_BMI
- facts: arcgis-layer · esriGeometryPoint · name field Name · 118 records · last edit 2026-04-07
- closes: not probed

### Cornelius Bike Ped Public Comments 20260309  ·    ·  from gis-hunter
- url: https://services2.arcgis.com/ZkOsbg84o8DsPPaP/arcgis/rest/services/Cornelius_Bike_Ped_Public_Comments_20260309/FeatureServer/0
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=6308c0512fa0431da5c3e6fb503172b9 · owner evan.saunderspearce_bmi
- facts: arcgis-layer · esriGeometryPoint · name field Name · 83 records · last edit 2026-03-19
- closes: not probed

### Massanutten_Mountain_CLuster_GW_VMT  ·    ·  from gis-hunter
- url: https://services4.arcgis.com/Py6dhyuhygVOz2EZ/arcgis/rest/services/Massanutten_Mountain_CLuster_GW_VMT/FeatureServer/0
- WHY: nothing stated about use on the item page or the service
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=bc66c94fe6954e3c8e6dda87a83396fa · owner Kasten7
- facts: arcgis-layer · esriGeometryPolygon · name field NAME · 6 records · last edit 2022-05-17 · sample brownsrun / greenmtn / northmassanutten
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### Massanutten Strategic  ·    ·  from gis-hunter
- url: https://tiles.arcgis.com/tiles/HRY6x8qt5qjGnAA9/arcgis/rest/services/Massanutten_Strategic/MapServer/0
- WHY: no polygons (no geometry)
- publisher: ? → official (a government word of the country: Institut)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=4a806647a2a24688bce27ce96b9edbef · owner FergusC_SI6 · org Smithsonian Institution
- facts: arcgis-layer
- closes: not probed

### Massanutten Reactive  ·    ·  from gis-hunter
- url: https://tiles.arcgis.com/tiles/HRY6x8qt5qjGnAA9/arcgis/rest/services/Massanutten_Reactive/MapServer/0
- WHY: no polygons (no geometry)
- publisher: ? → official (a government word of the country: Institut)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=aa94f964f0be4864aea15d4f625c2f5a · owner FergusC_SI6 · org Smithsonian Institution
- facts: arcgis-layer
- closes: not probed

### Rec_Site_Mount_Rogers_NRA  ·    ·  from gis-hunter
- url: https://services8.arcgis.com/QMq4T6DXbKtwLZHa/arcgis/rest/services/Rec_Site_Mount_Rogers_NRA_Test/FeatureServer/0
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=06a60ab1fda54e38a372b062556a27f4 · owner davidcohen@wildernessstewards.org
- facts: arcgis-layer · esriGeometryPoint · name field Rec_Site_Number · 15 records · last edit 2026-04-14
- closes: not probed

### Virginia Creeper Trail Trestle Status EDITING VIEW  ·    ·  from gis-hunter
- url: https://services3.arcgis.com/qVupYidwzMKkDQzr/arcgis/rest/services/Virginia_Creeper_Trail_Trestle_Status_EDITING_VIEW/FeatureServer/0
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → official (government words: Department)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=be866ce8b465408eb768ba03e2cc7b88 · owner gis.vdem · org Virginia Department of Emergency Management
- facts: arcgis-layer · esriGeometryPoint · name field sub_name · last edit 2024-11-21
- closes: not probed

### Virginia Creeper Trail  ·    ·  from gis-hunter
- url: https://services2.arcgis.com/ChUbz2hk6xRj7wYw/arcgis/rest/services/Virginia_Creeper_Trail/FeatureServer/1
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (Consultation in the publisher words)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=80d194e971dd4d45ad7b2a0458a4edb0 · owner alex_Equinox · org Equinox Environmental Consultation and Design
- facts: arcgis-layer · esriGeometryPolyline · name field LABEL · 87 records · last edit 2021-11-19
- closes: not probed

### Virginia Creeper Trail Alignment 082825  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/nWsjONL9B4B0DLnV/arcgis/rest/services/Virginia_Creeper_Trail_Alignment_082825/FeatureServer/4
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → official (a government word of the country: ign)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=3478db018eb34aa18434745cde53c5af · owner jtrainor.rkk · org Rummel Klepper & Kahl
- facts: arcgis-layer · esriGeometryPoint · name field RefName · 995 records · last edit 2025-08-28
- closes: not probed

### Virginia Creeper Trail Alignment 082825  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/nWsjONL9B4B0DLnV/arcgis/rest/services/Virginia_Creeper_Trail_Alignment_082825/FeatureServer/2
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → official (a government word of the country: ign)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=3478db018eb34aa18434745cde53c5af · owner jtrainor.rkk · org Rummel Klepper & Kahl
- facts: arcgis-layer · esriGeometryPolyline · name field RefName · 1 records · last edit 2025-08-28
- closes: not probed

### Virginia Creeper Trail Alignment 082825  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/nWsjONL9B4B0DLnV/arcgis/rest/services/Virginia_Creeper_Trail_Alignment_082825/FeatureServer/3
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → official (a government word of the country: ign)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=3478db018eb34aa18434745cde53c5af · owner jtrainor.rkk · org Rummel Klepper & Kahl
- facts: arcgis-layer · esriGeometryPolyline · name field RefName · 3978 records · last edit 2025-08-28
- closes: not probed

### Beaches to Bluegrass_2023_gdb  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/PxUNqSbaWFvFgHnJ/arcgis/rest/services/Beaches_to_Bluegrass_2023_gdb/FeatureServer/0
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → official (government words: Department)
- terms: CREDIT · source item page · "Southside PDC" · item https://www.arcgis.com/home/item.html?id=894791d859464915b4cae1cb62743203 · owner allison.tillett_vdcr · org Virginia Department of Conservation and Recreation
- facts: arcgis-layer · esriGeometryPolyline · 5 records · last edit 2024-02-02
- overlap: same publisher as sgvab
- closes: not probed

### Beaches to Bluegrass_2023_gdb  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/PxUNqSbaWFvFgHnJ/arcgis/rest/services/Beaches_to_Bluegrass_2023_gdb/FeatureServer/1
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → official (government words: Department)
- terms: CREDIT · source item page · "Southside PDC" · item https://www.arcgis.com/home/item.html?id=894791d859464915b4cae1cb62743203 · owner allison.tillett_vdcr · org Virginia Department of Conservation and Recreation
- facts: arcgis-layer · esriGeometryPolyline · name field Name · 5 records · last edit 2024-02-02
- overlap: same publisher as sgvab
- closes: not probed

### Beaches to Bluegrass_2023_gdb  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/PxUNqSbaWFvFgHnJ/arcgis/rest/services/Beaches_to_Bluegrass_2023_gdb/FeatureServer/2
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → official (government words: Department)
- terms: CREDIT · source item page · "Southside PDC" · item https://www.arcgis.com/home/item.html?id=894791d859464915b4cae1cb62743203 · owner allison.tillett_vdcr · org Virginia Department of Conservation and Recreation
- facts: arcgis-layer · esriGeometryPolyline · name field Label_ESRI · 122 records · last edit 2024-02-02
- overlap: same publisher as sgvab
- closes: not probed

### Beaches to Bluegrass_2023_gdb view  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/PxUNqSbaWFvFgHnJ/arcgis/rest/services/Beaches_to_Bluegrass_2023_gdb_view/FeatureServer/0
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → official (government words: Department)
- terms: CREDIT · source item page · "Southside PDC" · item https://www.arcgis.com/home/item.html?id=9d5904c1b0414be48276b55ef88f313d · owner allison.tillett_vdcr · org Virginia Department of Conservation and Recreation
- facts: arcgis-layer · esriGeometryPolyline · 5 records · last edit 2024-02-02
- overlap: same publisher as sgvab
- closes: not probed

### Beaches to Bluegrass_2023_gdb view  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/PxUNqSbaWFvFgHnJ/arcgis/rest/services/Beaches_to_Bluegrass_2023_gdb_view/FeatureServer/1
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → official (government words: Department)
- terms: CREDIT · source item page · "Southside PDC" · item https://www.arcgis.com/home/item.html?id=9d5904c1b0414be48276b55ef88f313d · owner allison.tillett_vdcr · org Virginia Department of Conservation and Recreation
- facts: arcgis-layer · esriGeometryPolyline · name field Name · 5 records · last edit 2024-02-02
- overlap: same publisher as sgvab
- closes: not probed

### Beaches to Bluegrass_2023_gdb view  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/PxUNqSbaWFvFgHnJ/arcgis/rest/services/Beaches_to_Bluegrass_2023_gdb_view/FeatureServer/2
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → official (government words: Department)
- terms: CREDIT · source item page · "Southside PDC" · item https://www.arcgis.com/home/item.html?id=9d5904c1b0414be48276b55ef88f313d · owner allison.tillett_vdcr · org Virginia Department of Conservation and Recreation
- facts: arcgis-layer · esriGeometryPolyline · name field Label_ESRI · 122 records · last edit 2024-02-02
- overlap: same publisher as sgvab
- closes: not probed

### Florida_Scenic_Highways  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/O1JpcwDW8sjYuddV/arcgis/rest/services/Florida_Scenic_Highways/FeatureServer/0
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → official (government words: Department)
- terms: CREDIT · source item page · "NO WARRANTIES: This site and its content is made available by the Florida Department of Transportation" · item https://www.arcgis.com/home/item.html?id=f5452aba5cd644558ea20a2791ebd357 · owner GeoMap_Publisher · org Florida Department of Transportation
- facts: arcgis-layer · esriGeometryPolyline · 232 records · last edit 2022-05-10
- closes: not probed

### [2024 FWP] OGT – Florida National Scenic Trail  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/nRHtyn3uE1kyzoYc/arcgis/rest/services/FNST/FeatureServer/0
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → official (government words: Department)
- terms: CREDIT · source item page · "DISCLAIMER (for maps) The boundaries depicted on this map document are approximate. This map documen" · item https://www.arcgis.com/home/item.html?id=413f963e21904d8aa48d55c8d9429f33 · owner Stephen.Clapp@FloridaDEP.gov_FDEP · org Florida Department of Environmental Protection
- facts: arcgis-layer · esriGeometryPolyline · name field Trail_Name · 711 records · last edit 2024-10-04
- closes: not probed

### FRMP_Wysong_Add  ·    ·  from gis-hunter
- url: https://services8.arcgis.com/pX44G7gzoOvJ5JiJ/arcgis/rest/services/FRMP_Wysong_Add/FeatureServer/0
- WHY: nothing stated about use on the item page or the service
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=e86ca639e2d7472c8eb6bfb3f7180f5c · owner orchideric
- facts: arcgis-layer · esriGeometryPolygon · name field VNAME · 1 records · last edit 2026-05-28 · sample TROTWOOD 4-A
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### Stephen Foster SP  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/fuy3eYDIPUqhqR2U/arcgis/rest/services/Stephen_Foster_SP/FeatureServer/0
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=b9afaa9aa519424789333ea997dc5563 · owner billparken
- facts: arcgis-layer · esriGeometryPoint · name field Name · 1 records · last edit 2021-02-17
- closes: not probed

### Horse Trailheads in Kentucky  ·    ·  from gis-hunter
- url: https://services3.arcgis.com/ghsX9CKghMvyYjBU/arcgis/rest/services/Ky_KDFWR_Horse_Trailheads_WM_gdb/FeatureServer/0
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: CREDIT · source item page · "LIMITATION OF LIABILITY: The Kentucky Division of Geographic Information (DGI) has no indication or reason to bel" · item https://www.arcgis.com/home/item.html?id=3137d5c2c8b7444e8fc7e9712f095099 · owner Kentucky_DGI · org KyGovMaps
- facts: arcgis-layer · esriGeometryPoint · name field WMANAME · 26 records · last edit 2025-07-03
- closes: not probed

### Inscripción Plataforma Logística los Luceros - SAA_form  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/yZQ9rZaq1vRYxnvY/arcgis/rest/services/service_c5936e86e6b2456e990c28d085077821_form/FeatureServer/0
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=2dd78d89acc94f18aa54224806a70368 · owner deraa_sdde · org Sec
- facts: arcgis-layer · esriGeometryPoint · name field USERNAME · last edit 2026-10-27
- closes: not probed

### Zoning_City_Of_Lincoln_Burleigh_County_ND  ·    ·  from gis-hunter
- url: https://services2.arcgis.com/8r0lsT7QHelkANsD/arcgis/rest/services/Zoning_City_Of_Lincoln_Burleigh_County_ND/FeatureServer/1
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: CREDIT · source item page · "s data is for representation only and does not represent a survey. No liability is assumed as to the accuracy of the data delineated herein. Data digitized from PDF zoni" · item https://www.arcgis.com/home/item.html?id=d87387d0c86f430a8f35d4ec397c06cb · owner BurleighCounty
- facts: arcgis-layer · esriGeometryPolygon · 73 records · last edit 2026-06-01
- closes: not probed

### PSF_Perea  ·    ·  from gis-hunter
- url: https://tiles.arcgis.com/tiles/6fH0bIcGPz3YuOKY/arcgis/rest/services/PSF_Perea/MapServer/0
- WHY: no polygons (no geometry)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=aaf3d5d07e30479d83f357b3e8ac781e · owner CastDron
- facts: arcgis-layer
- closes: not probed

### Practica2_perea_villar_WFL1  ·    ·  from gis-hunter
- url: https://services7.arcgis.com/jj1NqXxfLjbkZQH0/arcgis/rest/services/Practica2_perea_villar_WFL1/FeatureServer/2
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=6a09b4f2d9e74d2eb98f3cda46eff8fb · owner GJN9731_unisevilla · org Universidad de Sevilla
- facts: arcgis-layer · esriGeometryPolygon · 4111 records · last edit 2025-03-19
- closes: not probed

### Practica2_perea_villar_WFL1  ·    ·  from gis-hunter
- url: https://services7.arcgis.com/jj1NqXxfLjbkZQH0/arcgis/rest/services/Practica2_perea_villar_WFL1/FeatureServer/3
- WHY: nothing stated about use on the item page or the service
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=6a09b4f2d9e74d2eb98f3cda46eff8fb · owner GJN9731_unisevilla · org Universidad de Sevilla
- facts: arcgis-layer · esriGeometryPolygon · name field NOMBRE · 2 records · last edit 2025-03-19 · sample CASTILBLANCO DE LOS ARROYOS / VENTAS QUEMADAS
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### Practica2_perea_villar_WTL1  ·    ·  from gis-hunter
- url: https://tiles.arcgis.com/tiles/jj1NqXxfLjbkZQH0/arcgis/rest/services/Practica2_perea_villar_WTL1/MapServer/0
- WHY: no polygons (no geometry)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=b374507fa8d547bfb491713e5c2bc178 · owner GJN9731_unisevilla · org Universidad de Sevilla
- facts: arcgis-layer
- closes: not probed

### Practica2_perea_villar_WTL1  ·    ·  from gis-hunter
- url: https://tiles.arcgis.com/tiles/jj1NqXxfLjbkZQH0/arcgis/rest/services/Practica2_perea_villar_WTL1/MapServer/1
- WHY: no polygons (no geometry)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=b374507fa8d547bfb491713e5c2bc178 · owner GJN9731_unisevilla · org Universidad de Sevilla
- facts: arcgis-layer
- closes: not probed

### Practica2_perea_villar_WTL1  ·    ·  from gis-hunter
- url: https://tiles.arcgis.com/tiles/jj1NqXxfLjbkZQH0/arcgis/rest/services/Practica2_perea_villar_WTL1/MapServer/2
- WHY: no polygons (no geometry)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=b374507fa8d547bfb491713e5c2bc178 · owner GJN9731_unisevilla · org Universidad de Sevilla
- facts: arcgis-layer
- closes: not probed

### Practica2_perea_villar_WTL1  ·    ·  from gis-hunter
- url: https://tiles.arcgis.com/tiles/jj1NqXxfLjbkZQH0/arcgis/rest/services/Practica2_perea_villar_WTL1/MapServer/3
- WHY: no polygons (no geometry)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=b374507fa8d547bfb491713e5c2bc178 · owner GJN9731_unisevilla · org Universidad de Sevilla
- facts: arcgis-layer
- closes: not probed

### Practica2_perea_villar_WTL1  ·    ·  from gis-hunter
- url: https://tiles.arcgis.com/tiles/jj1NqXxfLjbkZQH0/arcgis/rest/services/Practica2_perea_villar_WTL1/MapServer/4
- WHY: no polygons (no geometry)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=b374507fa8d547bfb491713e5c2bc178 · owner GJN9731_unisevilla · org Universidad de Sevilla
- facts: arcgis-layer
- closes: not probed

### Practica2_perea_villar_WTL1  ·    ·  from gis-hunter
- url: https://tiles.arcgis.com/tiles/jj1NqXxfLjbkZQH0/arcgis/rest/services/Practica2_perea_villar_WTL1/MapServer/5
- WHY: no polygons (no geometry)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=b374507fa8d547bfb491713e5c2bc178 · owner GJN9731_unisevilla · org Universidad de Sevilla
- facts: arcgis-layer
- closes: not probed

### Fort_Morgan_Encumbrances_TeagueRanch  ·    ·  from gis-hunter
- url: https://services5.arcgis.com/rqsYvPKZmvSrSWbw/arcgis/rest/services/Fort_Morgan_Encumbrances_TeagueRanch/FeatureServer/2
- WHY: nothing stated about use on the item page or the service
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=1ba4bb8818d548d6b4766af46e36c85e · owner martinwi
- facts: arcgis-layer · esriGeometryPolygon · name field Parcel_Name · 48 records · last edit 2021-04-29 · sample A / B / C
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### Fort_Morgan_Encumbrances_TeagueRanch  ·    ·  from gis-hunter
- url: https://services5.arcgis.com/rqsYvPKZmvSrSWbw/arcgis/rest/services/Fort_Morgan_Encumbrances_TeagueRanch/FeatureServer/3
- WHY: nothing stated about use on the item page or the service
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=1ba4bb8818d548d6b4766af46e36c85e · owner martinwi
- facts: arcgis-layer · esriGeometryPolygon · name field Name · 74 records · last edit 2021-04-29 · sample EX 16 / EX 28 / EX 37
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### Fort_Morgan_Encumbrances_TeagueRanch  ·    ·  from gis-hunter
- url: https://services5.arcgis.com/rqsYvPKZmvSrSWbw/arcgis/rest/services/Fort_Morgan_Encumbrances_TeagueRanch/FeatureServer/4
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=1ba4bb8818d548d6b4766af46e36c85e · owner martinwi
- facts: arcgis-layer · esriGeometryPolygon · 1 records · last edit 2021-04-29
- closes: not probed

### 10PPM_Contours_Fort_Morgan_LDP  ·    ·  from gis-hunter
- url: https://services.arcgis.com/czCXlxn6hYtK4vdg/arcgis/rest/services/10PPM_Contours_Fort_Morgan_LDP/FeatureServer/0
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=af4b298c343549a385c5560f44b822d5 · owner jstone@denverwater.org_DW · org Denver Water
- facts: arcgis-layer · esriGeometryPolyline · 33 records · last edit 2020-04-10
- closes: not probed

### Fort_Morgan_LDP_Draft  ·    ·  from gis-hunter
- url: https://tiles.arcgis.com/tiles/czCXlxn6hYtK4vdg/arcgis/rest/services/Fort_Morgan_LDP_Draft/MapServer/0
- WHY: no polygons (no geometry)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=a56b0baff6074ea08f6f37a1d3db7492 · owner jstone@denverwater.org_DW · org Denver Water
- facts: arcgis-layer
- closes: not probed

### Butler County, PA Bridge Conditions Feature Layer  ·    ·  from gis-hunter
- url: https://services9.arcgis.com/5VOhDgerxIw33LoH/arcgis/rest/services/BridgeConditions/FeatureServer/0
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → official (government words: County)
- terms: CREDIT · source item page · "This feature layer was created with the intent for in to be used by Kevin Gray, of Butler County, PA Bridges." · item https://www.arcgis.com/home/item.html?id=0c70caeb82a44468a8eeb81983bce841 · owner AHumes
- facts: arcgis-layer · esriGeometryPoint · name field FACILITY · 150 records · last edit 2024-04-09
- closes: not probed

### Butler County, PA Bridge Conditions Feature Layer  ·    ·  from gis-hunter
- url: https://services9.arcgis.com/5VOhDgerxIw33LoH/arcgis/rest/services/BridgeConditions/FeatureServer/1
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → official (government words: County)
- terms: CREDIT · source item page · "This feature layer was created with the intent for in to be used by Kevin Gray, of Butler County, PA Bridges." · item https://www.arcgis.com/home/item.html?id=0c70caeb82a44468a8eeb81983bce841 · owner AHumes
- facts: arcgis-layer · esriGeometryPoint · 427 records · last edit 2024-04-09
- closes: not probed

### Butler County, PA Bridge Locations Feature Layer  ·    ·  from gis-hunter
- url: https://services9.arcgis.com/5VOhDgerxIw33LoH/arcgis/rest/services/AllBridges/FeatureServer/0
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → official (government words: County)
- terms: CREDIT · source item page · "This Feature Layer was created with the intent for it to be used by Kevin Gray of Butler County, PA Bridges." · item https://www.arcgis.com/home/item.html?id=f1e0d6a8c7bf4a2b849d2cb4caf3fec7 · owner AHumes
- facts: arcgis-layer · esriGeometryPoint · name field FACILITY · 577 records · last edit 2024-04-11
- closes: not probed

### Trees_Butler_Hike_and_Bike_Trail  ·    ·  from gis-hunter
- url: https://services.arcgis.com/0L95CJ0VTaxqcmED/arcgis/rest/services/Trees_Butler_Hike_and_Bike_Trail/FeatureServer/0
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → official (government words: City of)
- terms: CREDIT · source item page · "GIS Disclaimer: This product is for informational purposes and may not have been prepared for or be suit" · item https://www.arcgis.com/home/item.html?id=49bfdff293bd48e78a7a271188980264 · owner ACAR.Administrator · org City of Austin
- facts: arcgis-layer · esriGeometryPoint · name field Name · 25 records · last edit 2026-09-24
- closes: not probed

### Adirondack Park Boundary  ·    ·  from gis-hunter
- url: https://services2.arcgis.com/8krRUWgifzA4cgL3/arcgis/rest/services/AdirondackParkBoundary/FeatureServer/0
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → official (government words: Agency)
- terms: CREDIT · source item page · "This data is not intended for legal jurisdictional determinations. Contact the Adirondack Park Agency for all boundary" · item https://www.arcgis.com/home/item.html?id=2308970e941d47eea01150eb9e4e1007 · owner APA_Administrator · org New York State Adirondack Park Agency
- facts: arcgis-layer · esriGeometryPolyline · 107 records · last edit 2026-03-19
- closes: not probed

### Historic Adirondack Railroads  ·    ·  from gis-hunter
- url: https://services2.arcgis.com/8krRUWgifzA4cgL3/arcgis/rest/services/HistoricAdirondackRailroads/FeatureServer/0
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → official (government words: Agency)
- terms: CREDIT · source item page · "This data is not intended for legal jurisdictional determinations. Contact the Adirondack Park Agency for all boundary" · item https://www.arcgis.com/home/item.html?id=6f7a95b5ce734fbb8d6aa39d7face3cd · owner jwbarge · org New York State Adirondack Park Agency
- facts: arcgis-layer · esriGeometryPolyline · name field NAME · 188 records · last edit 2024-07-17
- closes: not probed

### Adirondack Park Boundary Polygon  ·    ·  from gis-hunter
- url: https://services2.arcgis.com/8krRUWgifzA4cgL3/arcgis/rest/services/BluelinePolygon/FeatureServer/0
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → official (government words: Agency)
- terms: CREDIT · source item page · "This data is not intended for legal jurisdictional determinations. Contact the Adirondack Park Agency for all boundary" · item https://www.arcgis.com/home/item.html?id=e281dffa9eab4806825861bb5e8eef98 · owner APA_Administrator · org New York State Adirondack Park Agency
- facts: arcgis-layer · esriGeometryPolygon · 1 records · last edit 2026-03-18
- closes: not probed

### Capt. John Smith Trail  ·    ·  from gis-hunter
- url: https://services.arcgis.com/nzS0F0zdNLvs7nc8/arcgis/rest/services/Capt__John_Smith_Trail/FeatureServer/0
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (Conservancy in the publisher words)
- terms: CREDIT · source item page · "Contact the Chesapeake Conservancy for reuse rights: Phone: 443.321.3610, Email: info@chesapeakeconservancy.org, Website: www.chesapeakeconservancy.org Chesapea" · item https://www.arcgis.com/home/item.html?id=11c9835968c249a092a347760bc38c4c · owner StoryMaps · org ArcGIS StoryMaps
- facts: arcgis-layer · esriGeometryPolyline · name field NAME · 838 records · last edit 2014-10-21
- closes: not probed

### CAJO Captain John Smith Chesapeake NHT Centerline ln  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/fBc8EJBxQRMcHlei/arcgis/rest/services/CAJO_Captain_John_Smith_Chesapeake_NHT_Centerline_ln/FeatureServer/0
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → official (a federal / national agency named)
- terms: CREDIT · source item page · "to use the related graphics as data. The National Park Service gives no warranty, expressed or implied, as to t NPS IR1_NAA (NER) GIS NPS IR1_NAA (NER) GIS" · item https://www.arcgis.com/home/item.html?id=afbf0619398b4e298c8f839c3c54b7b4 · owner JEFARRELL@nps.gov_nps · org National Park Service
- facts: arcgis-layer · esriGeometryPolyline · name field CNCT_NAME · 832 records · last edit 2026-05-14
- overlap: same publisher as akht
- closes: not probed

### Washington Rochambeau Auto Tour_WFL1  ·    ·  from gis-hunter
- url: https://services.arcgis.com/p5v98VHDX9Atv3l7/arcgis/rest/services/Washington_Rochambeau_Auto_Tour_WFL1/FeatureServer/0
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → official (government words: Department)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=4cc479e2d95f459b989498b95bd07a8c · owner David.Alley@vdot.virginia.gov_VDOT · org Virginia Department of Transportation
- facts: arcgis-layer · esriGeometryPoint · 94 records · last edit 2023-05-04
- closes: not probed

### Washington Rochambeau Auto Tour_WFL1  ·    ·  from gis-hunter
- url: https://services.arcgis.com/p5v98VHDX9Atv3l7/arcgis/rest/services/Washington_Rochambeau_Auto_Tour_WFL1/FeatureServer/1
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → official (government words: Department)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=4cc479e2d95f459b989498b95bd07a8c · owner David.Alley@vdot.virginia.gov_VDOT · org Virginia Department of Transportation
- facts: arcgis-layer · esriGeometryPoint · name field Route_Name · 47 records · last edit 2023-05-04
- closes: not probed

### Washington Rochambeau Auto Tour_WFL1  ·    ·  from gis-hunter
- url: https://services.arcgis.com/p5v98VHDX9Atv3l7/arcgis/rest/services/Washington_Rochambeau_Auto_Tour_WFL1/FeatureServer/2
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → official (government words: Department)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=4cc479e2d95f459b989498b95bd07a8c · owner David.Alley@vdot.virginia.gov_VDOT · org Virginia Department of Transportation
- facts: arcgis-layer · esriGeometryPoint · name field Route_Name · 51 records · last edit 2023-05-04
- closes: not probed

### Washington Rochambeau Auto Tour_WFL1  ·    ·  from gis-hunter
- url: https://services.arcgis.com/p5v98VHDX9Atv3l7/arcgis/rest/services/Washington_Rochambeau_Auto_Tour_WFL1/FeatureServer/3
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → official (government words: Department)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=4cc479e2d95f459b989498b95bd07a8c · owner David.Alley@vdot.virginia.gov_VDOT · org Virginia Department of Transportation
- facts: arcgis-layer · esriGeometryPolyline · 1 records · last edit 2023-05-04
- closes: not probed

### Washington Rochambeau Auto Tour_WFL1  ·    ·  from gis-hunter
- url: https://services.arcgis.com/p5v98VHDX9Atv3l7/arcgis/rest/services/Washington_Rochambeau_Auto_Tour_WFL1/FeatureServer/4
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → official (government words: Department)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=4cc479e2d95f459b989498b95bd07a8c · owner David.Alley@vdot.virginia.gov_VDOT · org Virginia Department of Transportation
- facts: arcgis-layer · esriGeometryPolyline · 3 records · last edit 2023-05-04
- closes: not probed

### Washington Rochambeau Auto Tour_WFL1  ·    ·  from gis-hunter
- url: https://services.arcgis.com/p5v98VHDX9Atv3l7/arcgis/rest/services/Washington_Rochambeau_Auto_Tour_WFL1/FeatureServer/5
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → official (government words: Department)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=4cc479e2d95f459b989498b95bd07a8c · owner David.Alley@vdot.virginia.gov_VDOT · org Virginia Department of Transportation
- facts: arcgis-layer · esriGeometryPoint · name field Route_Name · 21 records · last edit 2023-05-04
- closes: not probed

### Washington Rochambeau Auto Tour_WFL1  ·    ·  from gis-hunter
- url: https://services.arcgis.com/p5v98VHDX9Atv3l7/arcgis/rest/services/Washington_Rochambeau_Auto_Tour_WFL1/FeatureServer/6
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → official (government words: Department)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=4cc479e2d95f459b989498b95bd07a8c · owner David.Alley@vdot.virginia.gov_VDOT · org Virginia Department of Transportation
- facts: arcgis-layer · esriGeometryPoint · name field Route_Name · 20 records · last edit 2023-05-04
- closes: not probed

### Washington Rochambeau Auto Tour_WFL1  ·    ·  from gis-hunter
- url: https://services.arcgis.com/p5v98VHDX9Atv3l7/arcgis/rest/services/Washington_Rochambeau_Auto_Tour_WFL1/FeatureServer/7
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → official (government words: Department)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=4cc479e2d95f459b989498b95bd07a8c · owner David.Alley@vdot.virginia.gov_VDOT · org Virginia Department of Transportation
- facts: arcgis-layer · esriGeometryPolyline · 1 records · last edit 2023-05-04
- closes: not probed

### Washington-Rochambeau Trail  ·    ·  from gis-hunter
- url: https://services7.arcgis.com/xBaYvpTc0JtqK5u2/arcgis/rest/services/WARO_Trail/FeatureServer/0
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → official (government words: City of)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=d7658c0e74024306b24e5f6dec60b8e8 · owner mauryt_havredegracemd · org City of Havre de Grace
- facts: arcgis-layer · esriGeometryPolyline · name field NAME · 1 records · last edit 2025-04-09
- closes: not probed

### Catskill Park  ·    ·  from gis-hunter
- url: https://services6.arcgis.com/EbVsqZ18sv1kVJ3k/arcgis/rest/services/Catskill_Park/FeatureServer/0
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (Geospatial Services in the publisher words)
- terms: CREDIT · source item page · "or reliance on the Data provided. The User accepts the Data provided “as is” with no guarantees that it is error free, complete, accurate, current or fit for any par" · item https://www.arcgis.com/home/item.html?id=4016eef4b979480aa01402f4883a9335 · owner NYSGIS_GPO · org ShareGIS NY
- facts: arcgis-layer · esriGeometryPoint · name field NAME · 5 records · last edit 2023-03-23
- closes: not probed

### Catskill Park  ·    ·  from gis-hunter
- url: https://services6.arcgis.com/EbVsqZ18sv1kVJ3k/arcgis/rest/services/Catskill_Park/FeatureServer/1
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (Geospatial Services in the publisher words)
- terms: CREDIT · source item page · "or reliance on the Data provided. The User accepts the Data provided “as is” with no guarantees that it is error free, complete, accurate, current or fit for any par" · item https://www.arcgis.com/home/item.html?id=4016eef4b979480aa01402f4883a9335 · owner NYSGIS_GPO · org ShareGIS NY
- facts: arcgis-layer · esriGeometryPoint · 35 records · last edit 2023-03-23
- closes: not probed

### Catskill Park Boundary  ·    ·  from gis-hunter
- url: https://services6.arcgis.com/DZHaqZm9cxOD4CWM/arcgis/rest/services/Catskill_Park_Boundary/FeatureServer/7
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → official (government words: Department)
- terms: CREDIT · source item page · "1. The NYS DEC asks to be credited in derived products. 2. Secondary distribution of the data is not allowed. 3. Any docum" · item https://www.arcgis.com/home/item.html?id=ab287e5835e44b83b17c6c031ffce158 · owner srvDECGISPub@srv_cld.ny.gov_nysdec · org New York State Department of Environmental Conservation
- facts: arcgis-layer · esriGeometryPolygon · 1 records · last edit 2025-03-25
- overlap: same publisher as sgnya
- closes: not probed

### catskill_park_firetowers  ·    ·  from gis-hunter
- url: https://services8.arcgis.com/gHHsN1i8OISt9wMD/arcgis/rest/services/catskill_park_firetowers/FeatureServer/0
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=ef891467f70f4ed4980cc65d0db3c0d7 · owner Timothy.Ozmon_GISBSC
- facts: arcgis-layer · esriGeometryPoint · name field NAME · 5 records · last edit 2021-02-28
- closes: not probed

### British Empire 2  ·    ·  from gis-hunter
- url: https://services.arcgis.com/8df8p0NlLFEShl0r/arcgis/rest/services/Major_Empires/FeatureServer/0
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: CREDIT · source item page · "ay be freely downloaded for research, study, or teaching, but must be cited appropriately. Re-release of the data, or incorporation of the data into a commercial pr" · item https://www.arcgis.com/home/item.html?id=1bb885a34b44491eb06c5681dd009d11 · owner University_of_Minnesota · org University of Minnesota
- facts: arcgis-layer · esriGeometryPolygon · name field Name · 3 records · last edit 2016-10-31 · sample Roman Empire / Mongol Empire / British Empire
- overlap: same publisher as sgmnd
- closes: not probed

### Mint locations of the Roman Empire  ·    ·  from gis-hunter
- url: https://services3.arcgis.com/nwUScSWGt2wNe9dC/arcgis/rest/services/OCRE_Mintlocations_Roman_Empire/FeatureServer/0
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (Corpora in the publisher words)
- terms: CREDIT · source item page · "errors or omissions in the contents of the service. GISGILDE may use copyrighted material which has not always been specifically authorized by the copyright owner. The" · item https://www.arcgis.com/home/item.html?id=78681a3e64f341348c51b3457e3fc39f · owner GISGILDE.Admin
- facts: arcgis-layer · esriGeometryPoint · name field AncientName · 46 records · last edit 2023-01-18
- closes: not probed

### Flint Hills Trail  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/VineY8LQ39gOVtTz/arcgis/rest/services/Flint_Hills_Trail/FeatureServer/0
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=a9ca3514c634470dae89f2bc28dec0b0 · owner ModernEarthTech · org KC Mapping & GIS
- facts: arcgis-layer · esriGeometryPolyline · 13 records · last edit 2022-02-09
- closes: not probed

### Mount Laguna and Carrizo Mountain  ·    ·  from gis-hunter
- url: https://services6.arcgis.com/zX3RUXcV2Ha1zcWA/arcgis/rest/services/Mount_Laguna_and_Carrizo_Mountain/FeatureServer/4
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=94abab29263645009533fd67e9fbc2fe · owner GMF2020
- facts: arcgis-layer · esriGeometryPolygon · 685 records · last edit 2025-12-05
- closes: not probed

### Hagerstown Regional Airport Clear Zones  ·    ·  from gis-hunter
- url: https://services2.arcgis.com/uxxyl33jRTSmjre5/arcgis/rest/services/Airport_Clear_Zones/FeatureServer/28
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → official (government words: County)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=53ebd2c23ff640ae9b7df1ecfd55e006 · owner jrathvon@washco_md.net_washcomd · org Washington County, Maryland
- facts: arcgis-layer · esriGeometryPolygon · 4 records · last edit 2026-10-29
- closes: not probed

### Clear Creek County, CO Buildings  ·    ·  from gis-hunter
- url: https://services6.arcgis.com/Do88DoK2xjTUCXd1/arcgis/rest/services/Clear_Creek_County_CO_Buildings/FeatureServer/0
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (Esri in the publisher words)
- terms: OPEN · source item page · "This work is licensed under a Creative Commons by Attribution (CC BY 4.0) license. See Credits for Attribution. View License Deed | View" · item https://www.arcgis.com/home/item.html?id=aa392e0b55bf4db896f63159a544d849 · owner dkensok_osm · org OpenStreetMap
- facts: arcgis-layer · esriGeometryPolygon · 5725 records · last edit 2021-06-16
- closes: not probed

### Existing Vegetation at the Presidio  ·    ·  from gis-hunter
- url: https://services5.arcgis.com/KS6joEEoa0G4EO56/arcgis/rest/services/Existing_Vegetation_at_the_Presidio/FeatureServer/0
- WHY: nothing stated about use on the item page or the service
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=adad816b2b574b8ba1e30b8011d8f744 · owner petronilamandeno
- facts: arcgis-layer · esriGeometryPolygon · name field FS_UNIT_NA · 33 records · last edit 2018-03-27 · sample   /   /  
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### Presidio Trust Boundary  ·    ·  from gis-hunter
- url: https://services5.arcgis.com/KS6joEEoa0G4EO56/arcgis/rest/services/Presidio_Trust_Boundary/FeatureServer/0
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (Trust in the publisher words)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=4f8b01fb61904cb697c879ddb0f708f3 · owner petronilamandeno
- facts: arcgis-layer · esriGeometryPolygon · 1 records · last edit 2018-03-27
- closes: not probed

### 1797 Plano del Presidio de San Agustin  ·    ·  from gis-hunter
- url: https://tiles.arcgis.com/tiles/9lVOGNODRgsFxu7n/arcgis/rest/services/Castillo_Berrio_1797/MapServer/0
- WHY: no polygons (no geometry)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=0352257effe24ad2b6e8a09985178c2e · owner bmittler_DHHC · org Center for Digital Heritage and Geospatial Information
- facts: arcgis-layer
- closes: not probed

### Fun Places by MIGIZI Interns_form  ·    ·  from gis-hunter
- url: https://services4.arcgis.com/4O9OEYNKkrhmwigg/arcgis/rest/services/survey123_d43f5c819a2844fbab154440b7678f4f_form/FeatureServer/0
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=5986b47831ab4b709c73bbc9707af040 · owner Tedi-MIGIZI · org MIGIZI Communications
- facts: arcgis-layer · esriGeometryPoint · name field name_the_place · last edit 2023-06-29
- closes: not probed

### LSL_Basemap_View- Two Harbors  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/Fxir0Ov4y8APKoU8/arcgis/rest/services/LSL_Basemap_view_e5a577fedbb6490a8904de07161b0321/FeatureServer/1
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → official (government words: City of)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=76a27ef4a10a4b13baec30bfd7d2f8ba · owner BoltonMenk_TwoHarbors · org City of Two Harbors
- facts: arcgis-layer · esriGeometryPolygon · 1 records · last edit 2024-05-09
- closes: not probed

### Two Harbors Zoning With NSMB Boundary_WFL1  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/XcwN27e6wZ49zF8i/arcgis/rest/services/Two_Harbors_Zoning_With_NSMB_Boundary_WFL1/FeatureServer/0
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → official (government words: Commission)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=4af73b03aace45ddabeefa93483b167a · owner ARDCGIS · org Arrowhead Regional Development Commission
- facts: arcgis-layer · esriGeometryPolygon · 1 records · last edit 2024-08-29
- closes: not probed

### Two Harbors Zoning With NSMB Boundary_WFL1  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/XcwN27e6wZ49zF8i/arcgis/rest/services/Two_Harbors_Zoning_With_NSMB_Boundary_WFL1/FeatureServer/2
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → official (government words: Commission)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=4af73b03aace45ddabeefa93483b167a · owner ARDCGIS · org Arrowhead Regional Development Commission
- facts: arcgis-layer · esriGeometryPolygon · 4 records · last edit 2024-08-29
- closes: not probed

### Two Harbors Zoning With NSMB Boundary_WFL1  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/XcwN27e6wZ49zF8i/arcgis/rest/services/Two_Harbors_Zoning_With_NSMB_Boundary_WFL1/FeatureServer/6
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → official (government words: Commission)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=4af73b03aace45ddabeefa93483b167a · owner ARDCGIS · org Arrowhead Regional Development Commission
- facts: arcgis-layer · esriGeometryPolygon · 36 records · last edit 2024-08-29
- closes: not probed

### Two_Harbors_Bicycle_Destinations_and_Recommendations  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/XcwN27e6wZ49zF8i/arcgis/rest/services/Two_Harbors_Bicycle_Destinations_and_Recommendations/FeatureServer/0
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → official (government words: Commission)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=47485e441c544d63b12aed6eff8c02fb · owner rpintern · org Arrowhead Regional Development Commission
- facts: arcgis-layer · esriGeometryPolyline · 18 records · last edit 2017-02-02
- closes: not probed

### North Country Scenic Trail in Wisconsin  ·    ·  from gis-hunter
- url: https://dnrmaps.wi.gov/arcgis/rest/services/LF_DML/LF_DNR_REC_OPPS_WTM_Ext/MapServer/3
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → official (government host dnrmaps.wi.gov)
- terms: CREDIT · source item page · "Department of Natural Resources, Bureau of Facilities and Lands North Country Trail Association" · item https://dnrmaps.wi.gov/arcgis/rest/services/LF_DML/LF_DNR_REC_OPPS_WTM_Ext/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolyline · 1 records
- overlap: same publisher as sgwia
- closes: not probed

### North Country NST Shapefile  ·    ·  from gis-hunter
- url: https://services8.arcgis.com/WyuHwdftppQLa5KO/arcgis/rest/services/North_Country_NST_Shapefile/FeatureServer/0
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: CREDIT · source item page · "sponsible for use or misuse of this data. Please see the Distribution_Liability section for more detailed information North Country Trail Association" · item https://www.arcgis.com/home/item.html?id=fca18681755a4f73a6af3900500616cb · owner Field_Programs_CDTC · org Continental Divide Trail Coalition
- facts: arcgis-layer · esriGeometryPolyline · name field prop_name · 4311 records · last edit 2026-02-10
- closes: not probed

### North Country Trail  ·    ·  from gis-hunter
- url: https://services.arcgis.com/jDGuO8tYggdCCnUJ/arcgis/rest/services/North_Country_Trail/FeatureServer/0
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=fa2c079c78f64b868f7fe9d4e23ec513 · owner FTKaren
- facts: arcgis-layer · esriGeometryPolyline · 1 records
- closes: not probed

### Gitchi Gami Shoulder Widths_WFL1  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/XcwN27e6wZ49zF8i/arcgis/rest/services/Gitchi_Gami_Shoulder_Widths_WFL1/FeatureServer/6
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → official (government words: Commission)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=d5adfddb4b6e45a19c7ce4f54a31cd28 · owner ARDCGIS · org Arrowhead Regional Development Commission
- facts: arcgis-layer · esriGeometryPolygon · 1 records · last edit 2025-03-06
- closes: not probed

### Gitchi Gami State Trail  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/NlvHF2FHoAfPIDvG/arcgis/rest/services/Gitchi_Gami_State_Trail/FeatureServer/9
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=425fbba9b72f44ac847c3192d1fa1748 · owner amy.lewis_lakecountymn
- facts: arcgis-layer · esriGeometryPolyline · name field road_name · 68 records · last edit 2025-01-14
- closes: not probed

### Paul Bunyan Data  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/ROSiDsWkQXhsUAs0/arcgis/rest/services/Paul_Bunyan_Data/FeatureServer/0
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=cf2efb523bae49a9be1cc8fa453d66c4 · owner cstults_BSUMaps · org Ball State University ArcGIS Online 
- facts: arcgis-layer · esriGeometryPoint · name field Paul_Bunyan_Place_Names_and_Statues · 29 records · last edit 2019-04-30
- closes: not probed

### Suitability Map for Blazing Star  ·    ·  from gis-hunter
- url: https://services.arcgis.com/aScBVpZOvioggfOZ/arcgis/rest/services/Suitability_Map_for_Blazing_Star/FeatureServer/0
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=360e40f4d7aa4b55a1d20e7e53776442 · owner LouisLee2026@u.northwestern.edu_Northwestern · org Northwestern University
- facts: arcgis-layer · esriGeometryPolygon · 11627 records · last edit 2024-05-17
- closes: not probed

### Douglas County Boundary  ·    ·  from gis-hunter
- url: https://services.arcgis.com/pDAi2YK0L0QxVJHj/arcgis/rest/services/Douglas_County_Boundary/FeatureServer/0
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → official (government words: County)
- terms: CREDIT · source item page · "), as well as their respective employees, agents, and personnel, MAKE NO WARRANTY OF MERCHANTABILITY OR WARRANTY FOR FITNESS FOR A PARTICULAR PURPOSE, EXPRESS OR IMPLIED," · item https://www.arcgis.com/home/item.html?id=37cc7c208c2b49c09a0cee892cc28b8f · owner Nataliya2 · org Douglas County
- facts: arcgis-layer · esriGeometryPolygon · 1 records · last edit 2022-12-27
- closes: not probed

### Douglas County, Kansas Boundary  ·    ·  from gis-hunter
- url: https://gis.dgcoks.gov/server/rest/services/County_Boundary/FeatureServer/0
- WHY: NOT A PARK LAYER (coverage: parcels / census / index / planning / fire): it covers the whole land, so every pin falls inside (chat 11, Oct 29)
- publisher: ? → official (government host gis.dgcoks.gov)
- terms: CREDIT · source item page · "limits of the current state of the art, Douglas County cannot assume liability for any damages caused by any errors or omissions in the data, nor as a result of the fai" · item https://gis.dgcoks.gov/server/rest/services/County_Boundary/FeatureServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolygon · name field NAMELSAD · 1 records · sample Douglas County
- closes: not probed

### Douglas County, NE Buildings  ·    ·  from gis-hunter
- url: https://services6.arcgis.com/Do88DoK2xjTUCXd1/arcgis/rest/services/Douglas_County_NE_Buildings/FeatureServer/0
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (Esri in the publisher words)
- terms: OPEN · source item page · "This work is licensed under a Creative Commons by Attribution (CC BY 4.0) license. See Credits for Attribution. View License Deed | View" · item https://www.arcgis.com/home/item.html?id=938153f868db4014a4ed7c7e13cc0595 · owner dkensok_osm · org OpenStreetMap
- facts: arcgis-layer · esriGeometryPolygon · 239292 records · last edit 2021-05-21
- closes: not probed

### Active Faults and Folds Central Otago and Queenstown Lakes  ·    ·  from gis-hunter
- url: https://services6.arcgis.com/ALxeDxaeNjQo1Mf0/arcgis/rest/services/Active_Faults_and_Folds_Central_Otago_and_Queenstown_Lakes/FeatureServer/59
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (Consultancy in the publisher words)
- terms: CREDIT · source item page · "sure Analysis Map Viewer. Otago Regional Council does not warrant its accuracy and disclaims all liability whatsoever for any error, inaccuracy or incompleteness of the" · item https://www.arcgis.com/home/item.html?id=6a8e2338bc8d443fb3f2b2d2a00f2728 · owner OTAGOREGIONALCOUNCIL_ORCNZ · org Otago Regional Council
- facts: arcgis-layer · esriGeometryPolyline · name field NAME · 1502 records · last edit 2025-06-03
- closes: not probed

### Active Faults and Folds Central Otago and Queenstown Lakes  ·    ·  from gis-hunter
- url: https://services6.arcgis.com/ALxeDxaeNjQo1Mf0/arcgis/rest/services/Active_Faults_and_Folds_Central_Otago_and_Queenstown_Lakes/FeatureServer/60
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (Consultancy in the publisher words)
- terms: CREDIT · source item page · "sure Analysis Map Viewer. Otago Regional Council does not warrant its accuracy and disclaims all liability whatsoever for any error, inaccuracy or incompleteness of the" · item https://www.arcgis.com/home/item.html?id=6a8e2338bc8d443fb3f2b2d2a00f2728 · owner OTAGOREGIONALCOUNCIL_ORCNZ · org Otago Regional Council
- facts: arcgis-layer · esriGeometryPolyline · name field NAME · 7 records · last edit 2025-06-03
- closes: not probed

### Central Hawke's Bay Lakes-CMP  ·    ·  from gis-hunter
- url: https://services.arcgis.com/DN2fPfpggEPlLhP6/arcgis/rest/services/Lakes/FeatureServer/0
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → official (government words: District)
- terms: CREDIT · source item page · "This data has been prepared based on information provided by others. Stantec has not verified the accuracy and/or completeness of this information and" · item https://www.arcgis.com/home/item.html?id=c98c70b522cb46edb34e6e893660c68c · owner cillian.adamson@stantec.com_stantec · org Stantec
- facts: arcgis-layer · esriGeometryPolygon · 1 records · last edit 2022-11-18
- closes: not probed

### Rencana_Infrastruktur_Pengelolaan_Air_Limbah_dan_Persampahan  ·    ·  from gis-hunter
- url: https://services-ap1.arcgis.com/7jIYowrTWizM57Ga/arcgis/rest/services/Rencana_Infrastruktur_Pengelolaan_Air_Limbah_dan_Persampahan/FeatureServer/0
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: CREDIT · source item page · "Rencana_Infrastruktur_Pengelolaan_Air_Limbah_dan_Persampahan Rencana_Infrastruktur_Pengelolaan_Air_Limbah_dan_Persampahan Rencana_Infrastruktur_Pengelolaan_Air_" · item https://www.arcgis.com/home/item.html?id=13d08621e2ef49f7b56ede92b5598403 · owner DPUPRKendari · org DPUPR Kota Kendari 
- facts: arcgis-layer · esriGeometryPoint · 3 records · last edit 2023-02-23
- closes: not probed

### Rencana_Infrastruktur_Pengelolaan_Air_Limbah_dan_Persampahan  ·    ·  from gis-hunter
- url: https://services-ap1.arcgis.com/7jIYowrTWizM57Ga/arcgis/rest/services/Rencana_Infrastruktur_Pengelolaan_Air_Limbah_dan_Persampahan/FeatureServer/1
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: CREDIT · source item page · "Rencana_Infrastruktur_Pengelolaan_Air_Limbah_dan_Persampahan Rencana_Infrastruktur_Pengelolaan_Air_Limbah_dan_Persampahan Rencana_Infrastruktur_Pengelolaan_Air_" · item https://www.arcgis.com/home/item.html?id=13d08621e2ef49f7b56ede92b5598403 · owner DPUPRKendari · org DPUPR Kota Kendari 
- facts: arcgis-layer · esriGeometryPoint · 17 records · last edit 2023-02-23
- closes: not probed

### Dan Beebe and Brad Freeman Trail Additions_gdb  ·    ·  from gis-hunter
- url: https://services.arcgis.com/aa38u6OgfNoCkTJ6/arcgis/rest/services/Dan_Beebe_and_Brad_Freeman_Trail_Additions_gdb/FeatureServer/0
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: CREDIT · source item page · "LCB-KGoff" · item https://www.arcgis.com/home/item.html?id=cc55e56ce2904841b6499af8fb59dc98 · owner Asif.Ali@water.ca.gov_DWR
- facts: arcgis-layer · esriGeometryPolyline · name field TrailName · 6 records · last edit 2026-09-25
- closes: not probed

### Brumley  ·    ·  from gis-hunter
- url: https://services8.arcgis.com/OcpsbB1t6G1k007e/arcgis/rest/services/Brumley/FeatureServer/0
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=c8c523f92d9c426889c8a2106b9b50eb · owner MSI.forest
- facts: arcgis-layer · esriGeometryPoint · 4 records · last edit 2022-10-27
- closes: not probed

### Justin Brumley _Ski Run_69__WFL1  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/8DJsAMKuU5pXLFcd/arcgis/rest/services/Justin_Brumley__Ski_Run_69__WFL1/FeatureServer/0
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=ba05d640a213422d834fc3b025881e5d · owner jlbrumley_flc
- facts: arcgis-layer · esriGeometryPolyline · 1 records · last edit 2023-03-07
- closes: not probed

### Overmountain Victory National Historic Trail Official Temp  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/fBc8EJBxQRMcHlei/arcgis/rest/services/Overmountain_Victory_National_Historic_Trail_Official_Temp/FeatureServer/0
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → official (a federal / national agency named)
- terms: CREDIT · source item page · "Please contact the National Park Service for suggestions on use of this data set. The National Park Service funded creation of this data set. The National Park " · item https://www.arcgis.com/home/item.html?id=919d006b46594e4e911fa02e67eb37ed · owner cor_nps · org National Park Service
- facts: arcgis-layer · esriGeometryPolyline · name field TrailName · 43 records · last edit 2025-05-30
- overlap: same publisher as akht
- closes: not probed

### Overmountain Victory Trail Historic Route  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/PwLrOgCfU0cYShcG/arcgis/rest/services/Overmountain_Victory_Trail_Historic_Route/FeatureServer/0
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: CREDIT · source item page · "Restricted for use. Please contact Blue Ridge Forever at http://www.blueridgeforever.org/ for access information and proper use of this data." · item https://www.arcgis.com/home/item.html?id=1c46a1ced80d42cda2e7c0ed71ef1090 · owner ijohnson_nemac · org University of North Carolina at Asheville
- facts: arcgis-layer · esriGeometryPolyline · name field UnitName · 43 records · last edit 2017-02-21
- closes: not probed

### Overmountain Victory Trail - Designated Corridor  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/PwLrOgCfU0cYShcG/arcgis/rest/services/OVVI_BND_OVNHT_Corridor/FeatureServer/0
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: CREDIT · source item page · "Restricted for use. Please contact Blue Ridge Forever at http://www.blueridgeforever.org/ for access information and proper use of this data." · item https://www.arcgis.com/home/item.html?id=ab75d6dd216043ad928bfa7685f6b4b3 · owner ijohnson_nemac · org University of North Carolina at Asheville
- facts: arcgis-layer · esriGeometryPolygon · name field UnitName · 1 records · last edit 2017-02-21 · sample Overmountain Victory National Historic Trail
- closes: not probed

### Habitat Model: Palm Springs Pocket Mouse  ·    ·  from gis-hunter
- url: https://services9.arcgis.com/CBx4dpJSQTY7NvOy/arcgis/rest/services/PalmSpringsPocketMouse_Model/FeatureServer/38
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → official (government words: Conservation)
- terms: CREDIT · source item page · "Disclaimer: Maps and data are to be used for reference purposes only. Map features are approximate," · item https://www.arcgis.com/home/item.html?id=b928ccef48524cd98a8957c854c2c062 · owner kwarack_CVAG · org Coachella Valley Association of Governments
- facts: arcgis-layer · esriGeometryPolygon · 27 records · last edit 2022-07-21
- closes: not probed

### NDGISHUB Sheyenne River Contours 1ft 2002  ·    ·  from gis-hunter
- url: https://ndgishub.nd.gov/arcgis/rest/services/All_Elevation/MapServer/9
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → official (government host ndgishub.nd.gov)
- terms: CREDIT · source item page · "errors, inaccuracies, or viruses, and disclaims any responsibility or liability for interpretations or decisions based on this data. North Dakota state agencies and the" · item https://ndgishub.nd.gov/arcgis/rest/services/All_Elevation/MapServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolyline · name field REFNAME · 393527 records
- closes: not probed

### Sheyenne Lead Service Public Survey  ·    ·  from gis-hunter
- url: https://services.arcgis.com/U5e5v7pUT7BNl3dr/arcgis/rest/services/service_0de3d9623ebb4d35b0c45c4d4e5b5a55/FeatureServer/0
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → official (a government word of the country: Environment)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=368aed2fee5a4697a0870e09008c8bd9 · owner Dan.Lissick@AE2S.com_AE2S · org Advanced Engineering and Environmental Services
- facts: arcgis-layer · esriGeometryPoint · name field pocname · last edit 2024-03-25
- closes: not probed

### David Thompson 1785 to 1812  ·    ·  from gis-hunter
- url: https://services8.arcgis.com/cAtF2MSEHqBnNwgn/arcgis/rest/services/David_Thompson_1785_to_1812/FeatureServer/0
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=84dfd86e8d784aa49e23e7e969518475 · owner Bear.Watchers.Eye
- facts: arcgis-layer · esriGeometryPolyline · 1 records · last edit 2025-05-28
- closes: not probed

### David_Thompson  ·    ·  from gis-hunter
- url: https://services6.arcgis.com/avXuZG0wAqMng22B/arcgis/rest/services/David_Thompson/FeatureServer/0
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: CREDIT · source item page · "Nipissing University Centre for Understanding Semi-Peripheries Nipissing University Centre for Understanding Semi-Peripheries" · item https://www.arcgis.com/home/item.html?id=9ef61675148b41b68a859528047995a4 · owner NU_HGIS
- facts: arcgis-layer · esriGeometryPoint · name field Name_as_Gi · 8 records · last edit 2020-06-17
- closes: not probed

### Fort_Clark_Road  ·    ·  from gis-hunter
- url: https://services8.arcgis.com/S9FfA3ZHtXhdx1pq/arcgis/rest/services/Fort_Clark_Road/FeatureServer/7
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → official (a government word of the country: Survey)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=27883fef4c994bf999c9f8c6a703f003 · owner ALandSurveyor
- facts: arcgis-layer · esriGeometryPolyline · 4 records · last edit 2023-08-01
- closes: not probed

### Oak Lawn Churches  ·    ·  from gis-hunter
- url: https://services7.arcgis.com/HIWDYyvTtvtoCVn0/arcgis/rest/services/Oak_Lawn_Churches/FeatureServer/0
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=d5ed26c73c1742d29b3771239918da4a · owner OakLawnRitter · org Village of Oak Lawn
- facts: arcgis-layer · esriGeometryPolygon · 32 records · last edit 2016-06-06
- closes: not probed

### Govan_Sold_Prices  ·    ·  from gis-hunter
- url: https://services3.arcgis.com/C58X9R7Tu8cPpRcB/arcgis/rest/services/Govan_Sold_Prices/FeatureServer/0
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=88ab2c7d3302448eac2ff7f046b4d68c · owner 2806332S_Glasgow_Uni
- facts: arcgis-layer · esriGeometryPolygon · 31 records · last edit 2024-06-02
- closes: not probed

### skookum_ortho_wgs84_tif  ·    ·  from gis-hunter
- url: https://tiles.arcgis.com/tiles/C8EMgrsFcRFL6LrL/arcgis/rest/services/skookum_ortho_wgs84_tif/MapServer/0
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (LLC in the publisher words)
- terms: CREDIT · source item page · "This drone imagery was collected and processed by Russ and Brad McMillan of Aerial Images Northwest LLC in Spring of 2021 on behalf of EarthCorps and the Commen" · item https://www.arcgis.com/home/item.html?id=a5f26d7cd31047d2a314092606e3ef69 · owner patrick.pope_noaa · org NOAA GeoPlatform
- facts: arcgis-layer
- closes: not probed

### Skookum Archers  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/LCWc46UbpFlCIbVN/arcgis/rest/services/Skookum_Archers/FeatureServer/2
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: CREDIT · source item page · "ArcGIS, Collector, GRC, Skookum Archers ArcGIS, Collector, GRC, Skookum Archers" · item https://www.arcgis.com/home/item.html?id=0d6391157e614214832e70824cd42b6f · owner tbontempo_GRC_NATRS
- facts: arcgis-layer · esriGeometryPolygon · 3 records · last edit 2018-06-01
- closes: not probed

### Storymap_Skookum_Muck  ·    ·  from gis-hunter
- url: https://services7.arcgis.com/buuvDFFARQiOEbVZ/arcgis/rest/services/Storymap_Skookum_Muck/FeatureServer/2
- WHY: nothing stated about use on the item page or the service
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=4b41c514fd6f4e9db94d04f1042b916b · owner SPSSEG_GIS · org South Puget Sound Salmon Enhancement Group
- facts: arcgis-layer · esriGeometryPolygon · name field WRP_NAME · 1 records · last edit 2023-04-25 · sample Muck Creek
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### Peninsular Bighorn Sheep Habitat Vegetation Map [ds2660]  ·    ·  from gis-hunter
- url: https://services2.arcgis.com/Uq9r85Potqm3MfRV/arcgis/rest/services/biosds2660_fpu/FeatureServer/0
- WHY: NOT A PARK LAYER (coverage: parcels / census / index / planning / fire): it covers the whole land, so every pin falls inside (chat 11, Oct 29)
- publisher: ? → official (government words: Department)
- terms: OPEN · source item page · "License: This work is licensed under Creative Commons Attribution 4.0 International License (https://creativecommons.org/licenses/by/4.0/). Usi" · item https://www.arcgis.com/home/item.html?id=e564c04b7fe840feb9c5d849013d02c7 · owner BIOS_Admin · org California Department of Fish and Wildlife
- facts: arcgis-layer · esriGeometryPolygon · name field NVCSName · 4952 records · last edit 2022-04-12 · sample Quercus chrysolepis (tree) / Quercus chrysolepis (tree) / Quercus chrysolepis (tree)
- overlap: same publisher as sgcaa
- closes: not probed

### Utah Rocky Mountain Bighorn Sheep Habitat  ·    ·  from gis-hunter
- url: https://services.arcgis.com/ZzrwjTRez6FJiOq4/arcgis/rest/services/Utah_Rocky_Mtn_Bighorn_Sheep_Habitat/FeatureServer/0
- WHY: no name field: an outline needs a name to match a park
- publisher: ? → official (government words: DNR)
- terms: CREDIT · source item page · "None, but the UDWR provides no warranty nor accepts any responsibility or liability for any inaccurate or incomplete data associa" · item https://www.arcgis.com/home/item.html?id=82b1e7ce1ec74920bcd40cd7e729c9b3 · owner dwrdata · org Utah DNR Online Maps
- facts: arcgis-layer · esriGeometryPolygon · 11 records · last edit 2024-04-23
- overlap: same publisher as sguta
- closes: not probed

### Manitoba_Co_Packer_Services  ·    ·  from gis-hunter
- url: https://services.arcgis.com/mMUesHYPkXjaFGfS/arcgis/rest/services/Manitoba_Co_Packer_Services/FeatureServer/0
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → official (government words: Government)
- terms: OPEN · source item page · "Manitoba Open Data Licence Manitoba Government" · item https://www.arcgis.com/home/item.html?id=420d169c9349437789d202b302bc2732 · owner Manitoba_Government · org Manitoba Maps
- facts: arcgis-layer · esriGeometryPoint · name field Website · 73 records · last edit 2026-09-18
- overlap: same publisher as Manitoba Par
- closes: not probed

### Packer Township  ·    ·  from gis-hunter
- url: https://services6.arcgis.com/b4SgqAPC2VGq0h6n/arcgis/rest/services/Packer_Township/FeatureServer/0
- WHY: nothing stated about use on the item page or the service
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=d4add900fefa430c8f72114f6024131a · owner dbackenstoes_bia
- facts: arcgis-layer · esriGeometryPolygon · name field middlename · 809 records · last edit 2025-06-17 · sample   /   / M
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### Troop Positions _C Duffy_  ·    ·  from gis-hunter
- url: https://services5.arcgis.com/KEZIbVsXEvL1ZLY5/arcgis/rest/services/Troop_Positions__C_Duffy_/FeatureServer/259
- WHY: nothing stated about use on the item page or the service
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=a63bf231c20642758aaa1e4bc547e0ef · owner aocarchaeology · org AOC Archaeology Group
- facts: arcgis-layer · esriGeometryPolygon · name field Name · 57 records · last edit 2024-05-09 · sample Perth / Glenbucket / Glengarry and Macleod
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### ancient_long_established_woodland Senan Duffy  ·    ·  from gis-hunter
- url: https://services-eu1.arcgis.com/fj8SedOMxfUDzrBI/arcgis/rest/services/ancient_long_established_woodland_Senan_Duffy/FeatureServer/0
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=591fcec330ed40e7bba19362a03d69cf · owner senan.duffy2@mail.dcu.ie_DCU_Student · org Dublin City University
- facts: arcgis-layer · esriGeometryPolygon · name field SITE_NAME · 2738 records · last edit 2026-10-02 · sample Derrygoul Wood / Derrygoul Wood / Glengarriff
- closes: not probed

### Earthquake_and_Volcano_Risk_Canada__(Dylan_Duffy)  ·    ·  from gis-hunter
- url: https://services.arcgis.com/QI0dObYawrKkuwDp/arcgis/rest/services/Earthquake_and_Volcano_Risk_Canada__(Dylan_Duffy)/FeatureServer/0
- WHY: nothing stated about use on the item page or the service
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=7e43c0af7e2446de95399a7e47fe2047 · owner 556122 · org   ArcGIS Online for Ontario Schools
- facts: arcgis-layer · esriGeometryPolygon · name field Name_EN · 2 records · last edit 2019-03-31 · sample British Columbia / Yukon
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### Fiber Hand Holes  ·    ·  from gis-hunter
- url: https://services6.arcgis.com/iZ6GmQZ9zaRNfvWH/arcgis/rest/services/Fiber_Hand_Holes/FeatureServer/3
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (Consulting in the publisher words)
- terms: CREDIT · source item page · "Water system assets owned and maintained by the City of Silvis, Illinois. The information depicted here has been gathered by City sta" · item https://www.arcgis.com/home/item.html?id=2b25e5c35a014564860db7e72c3e23b6 · owner QCGIS_LisaM · org QCGIS Consulting, LLC
- facts: arcgis-layer · esriGeometryPoint · 10 records · last edit 2019-04-26
- closes: not probed

### 2021 Hand Crew Roster  ·    ·  from gis-hunter
- url: https://services5.arcgis.com/ELI1iJkCzTIagHkp/arcgis/rest/services/2021_Hand_Crew_Roster/FeatureServer/0
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → official (a federal / national agency named)
- terms: CREDIT · source item page · "This item was created by Lone Star State Hand Crew Leadership and is intended for use in internal or external presentations to educate others on the capabilities and accom" · item https://www.arcgis.com/home/item.html?id=a93ce061daf64a88b7177dca7dfd7052 · owner emily.turner_tfsgis · org Texas A&M Forest Service
- facts: arcgis-layer · esriGeometryPoint · 29 records · last edit 2021-10-20
- closes: not probed

### D-10, MGS Hand Samples and Thin Sections  ·    ·  from gis-hunter
- url: https://services.arcgis.com/8df8p0NlLFEShl0r/arcgis/rest/services/MGS_Hand_Samples_and_Thin_Sections/FeatureServer/0
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: OPEN · source item page · "There is no restrictions with the use of this data. Please reference the Minnesota Geological Survey when using. M" · item https://www.arcgis.com/home/item.html?id=3560dcffd41f4ea1a30e4d0015e33cdf · owner mgsgis_UMN · org University of Minnesota
- facts: arcgis-layer · esriGeometryPoint · name field rk_name · 21695 records · last edit 2023-10-12
- overlap: same publisher as sgmnd
- closes: not probed

### D-10, MGS Hand Samples and Thin Sections  ·    ·  from gis-hunter
- url: https://services.arcgis.com/8df8p0NlLFEShl0r/arcgis/rest/services/MGS_Hand_Samples_and_Thin_Sections/FeatureServer/1
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: OPEN · source item page · "There is no restrictions with the use of this data. Please reference the Minnesota Geological Survey when using. M" · item https://www.arcgis.com/home/item.html?id=3560dcffd41f4ea1a30e4d0015e33cdf · owner mgsgis_UMN · org University of Minnesota
- facts: arcgis-layer · esriGeometryPoint · name field rk_name · 46038 records · last edit 2023-10-12
- overlap: same publisher as sgmnd
- closes: not probed

### D-10, MGS Hand Samples and Thin Sections  ·    ·  from gis-hunter
- url: https://services.arcgis.com/8df8p0NlLFEShl0r/arcgis/rest/services/MGS_Hand_Samples_and_Thin_Sections/FeatureServer/2
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: OPEN · source item page · "There is no restrictions with the use of this data. Please reference the Minnesota Geological Survey when using. M" · item https://www.arcgis.com/home/item.html?id=3560dcffd41f4ea1a30e4d0015e33cdf · owner mgsgis_UMN · org University of Minnesota
- facts: arcgis-layer · esriGeometryPoint · name field rk_name · 6686 records · last edit 2023-10-12
- overlap: same publisher as sgmnd
- closes: not probed

### D-10, MGS Hand Samples and Thin Sections  ·    ·  from gis-hunter
- url: https://services.arcgis.com/8df8p0NlLFEShl0r/arcgis/rest/services/MGS_Hand_Samples_and_Thin_Sections/FeatureServer/3
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: OPEN · source item page · "There is no restrictions with the use of this data. Please reference the Minnesota Geological Survey when using. M" · item https://www.arcgis.com/home/item.html?id=3560dcffd41f4ea1a30e4d0015e33cdf · owner mgsgis_UMN · org University of Minnesota
- facts: arcgis-layer · esriGeometryPoint · 1786 records · last edit 2023-10-12
- overlap: same publisher as sgmnd
- closes: not probed

### Mount St_ Helens National Volcanic Monument_WFL1  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/rCcfuAf877pT4w3i/arcgis/rest/services/Mount_St__Helens_National_Volcanic_Monument_WFL1/FeatureServer/1
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=d690001da89b4f7d8ba2634c7f14ad16 · owner jasmine.ortiz@wsu.edu_wsuniv · org Washington State University
- facts: arcgis-layer · esriGeometryPolygon · 2 records · last edit 2026-04-26
- closes: not probed

### Mount St_ Helens National Volcanic Monument_WFL1  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/rCcfuAf877pT4w3i/arcgis/rest/services/Mount_St__Helens_National_Volcanic_Monument_WFL1/FeatureServer/3
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=d690001da89b4f7d8ba2634c7f14ad16 · owner jasmine.ortiz@wsu.edu_wsuniv · org Washington State University
- facts: arcgis-layer · esriGeometryPolygon · 3 records · last edit 2026-04-26
- closes: not probed

### Mount St_ Helens National Volcanic Monument_WTL3  ·    ·  from gis-hunter
- url: https://tiles.arcgis.com/tiles/rCcfuAf877pT4w3i/arcgis/rest/services/Mount_St__Helens_National_Volcanic_Monument_WTL3/MapServer/0
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (a university account)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=8dd465a573c84a39949694c7a2ef2376 · owner jasmine.ortiz@wsu.edu_wsuniv · org Washington State University
- facts: arcgis-layer
- closes: not probed

### Pacific Crest Trail Corridor INF LMP 2019  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/gGHDlz6USftL5Pau/arcgis/rest/services/PacificCrestTrailCorridor_INF_LMP2019_gdb/FeatureServer/0
- WHY: the publisher closed it (internal / sign-in / by request)
- publisher: ? → official (a federal / national agency named)
- terms: CLOSED · source item page · "urisdiction, or restrictions that may be in place on either public or private land. Natural hazards may or may not be depicted on the data and maps, and land users sho" · item https://www.arcgis.com/home/item.html?id=95e1c8cecd0a48cebc57cf50758ca119 · owner USFSRegion05 · org U.S. Forest Service
- facts: arcgis-layer · esriGeometryPolygon · name field FORESTNAME · 2 records · last edit 2021-06-18 · sample Inyo National Forest / None
- closes: not probed

### Blanchard School Board Wards  ·    ·  from gis-hunter
- url: https://services2.arcgis.com/gdgYLKfxoJmkNxos/arcgis/rest/services/Blanchard_School_Board_Wards/FeatureServer/0
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (School in the publisher words)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=5d6f540ae550434f9c1f11f25025c351 · owner OKHouse1 · org Oklahoma House of Representatives
- facts: arcgis-layer · esriGeometryPolygon · 5 records · last edit 2022-08-10
- closes: not probed

### Teanaway Cutthroat Slam  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/754BERmVIq3RqSf8/arcgis/rest/services/survey123_69bcc2270aae41babd6c3019ca8e1f53/FeatureServer/0
- WHY: no polygons (esriGeometryPoint)
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=f274dfeeddc946e0924153eba2c9800e · owner mmayfield_tu · org Trout Unlimited
- facts: arcgis-layer · esriGeometryPoint · 7 records · last edit 2020-11-20
- closes: not probed

### Teanaway_Projects  ·    ·  from gis-hunter
- url: https://services2.arcgis.com/VmLllxPKgIzlr2id/arcgis/rest/services/Teanaway_Projects/FeatureServer/0
- WHY: not an official publisher: we take outlines only from the managing agency
- publisher: ? → not official (Trust in the publisher words)
- terms: CREDIT · source item page · "Washington Water Trust" · item https://www.arcgis.com/home/item.html?id=19a9b1c172e74502a5f324133f43e4aa · owner BlueWaterGIS · org Blue Water GIS
- facts: arcgis-layer · esriGeometryPoint · name field Name · 8 records · last edit 2016-11-27
- closes: not probed

### Teanaway_HUC10  ·    ·  from gis-hunter
- url: https://services2.arcgis.com/VmLllxPKgIzlr2id/arcgis/rest/services/Teanaway_HUC10/FeatureServer/0
- WHY: nothing stated about use on the item page or the service
- publisher: ? → unsure (no government word in the publisher, owner, organisation or credit)
- terms: NOTHING STATED · source item page · item https://www.arcgis.com/home/item.html?id=7eecb5005fba47b4be0eca0b5184f6db · owner BlueWaterGIS · org Blue Water GIS
- facts: arcgis-layer · esriGeometryPolygon · name field HU_10_NAME · 1 records · sample Middle ForkTenaway River-Tenaway River
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 0 missing parks lie in the layer's extent)

### Wood / Pawcatuck National Wild and Scenic Rivers System  ·    ·  from gis-hunter
- url: https://services2.arcgis.com/S8zZg9pg23JUEexQ/arcgis/rest/services/HYDRO_WoodPaw_WildScenic_Rivers_spf/FeatureServer/3
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → official (government words: Department)
- terms: CREDIT · source item page · "cense agreement, which can be viewed below: This dataset is provided 'as is.’ The producer(s) of this dataset, contributors to this dataset, the Rhode Island Geograp" · item https://www.arcgis.com/home/item.html?id=0f5d45cee9c3469296d5cc070e162f42 · owner URIEDC_RIGIS · org Environmental Data Center
- facts: arcgis-layer · esriGeometryPolyline · name field NAME · 297 records · last edit 2024-11-14
- overlap: same publisher as sgrib
- closes: not probed

### BLM UT Designated Wild and Scenic Rivers  ·    ·  from gis-hunter
- url: https://gis.blm.gov/utarcgis/rest/services/NLCS/BLM_UT_WSR/FeatureServer/0
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → official (government host gis.blm.gov)
- terms: CREDIT · source item page · "These data are provided by Bureau of Land Management (BLM) “as is” and may contain errors or omissions. The User ass" · item https://gis.blm.gov/utarcgis/rest/services/NLCS/BLM_UT_WSR/FeatureServer/info/iteminfo
- facts: arcgis-layer · esriGeometryPolyline · name field NLCS_NAME · 148 records
- overlap: same publisher as hab
- closes: not probed

### BLM UT  Wild and Scenic Rivers  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/KbxwQRRfWyEYLgp4/arcgis/rest/services/BLM_UT___Wild_and_Scenic_Rivers/FeatureServer/1
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → official (a federal / national agency named)
- terms: CREDIT · source item page · "These data are provided by Bureau of Land Management (BLM) “as is” and may contain errors or omissions. The User ass" · item https://www.arcgis.com/home/item.html?id=37d48aa2fb6a47bfac2cd6ac4a75918a · owner rarnold@blm.gov_BLM_EGIS · org Bureau of Land Management
- facts: arcgis-layer · esriGeometryPolyline · name field NLCS_NAME · 1058 records · last edit 2026-06-16
- closes: not probed

### Iditarod National Historic Trail BLM Official Temp  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/fBc8EJBxQRMcHlei/arcgis/rest/services/Iditarod_National_Historic_Trail_BLM_Official_Temp/FeatureServer/0
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → official (a federal / national agency named)
- terms: CREDIT · source item page · "Should provide/reference 'supplemental information' when data is presented or published. Kevin Keeler - Bureau of Land Management Kevin Keeler - Bureau of Land " · item https://www.arcgis.com/home/item.html?id=37787244e85c450c8247c34eb221954c · owner cor_nps · org National Park Service
- facts: arcgis-layer · esriGeometryPolyline · name field Website · 26 records · last edit 2023-04-03
- overlap: same publisher as akht
- closes: not probed

### Iditarod National Historic Trails Story Map Public Layer  ·    ·  from gis-hunter
- url: https://services1.arcgis.com/gGHDlz6USftL5Pau/arcgis/rest/services/Iditarod_National_Historic_Trails_Story_Map_Public_Layer/FeatureServer/0
- WHY: the publisher closed it (internal / sign-in / by request)
- publisher: ? → official (a federal / national agency named)
- terms: CLOSED · source item page · "urisdiction, or restrictions that may be in place on either public or private land. Natural hazards may or may not be depicted on the data and maps, and land users sho" · item https://www.arcgis.com/home/item.html?id=de4cb1f4ecf144e6a7f70731c46b8700 · owner ChugachNF · org U.S. Forest Service
- facts: arcgis-layer · esriGeometryPolyline · name field NAME · 161 records · last edit 2026-02-23
- closes: not probed

### Juneau DOT&PF Sidewalks Winter Maintenance Priority  ·    ·  from gis-hunter
- url: https://services.arcgis.com/r4A0V7UzH9fcLVvv/arcgis/rest/services/Juneau_Sidewalks_Winter_Maintenance_public_priority/FeatureServer/0
- WHY: no polygons (esriGeometryPolyline)
- publisher: ? → official (government words: Department)
- terms: CREDIT · source item page · "ignia. Nothing in these terms limits uses otherwise permitted by law. Attribution. Published maps, reports, applications, and redistributed datasets that use the Data must" · item https://www.arcgis.com/home/item.html?id=59c2402277ac4af88b17071e2c04fe27 · owner AKDOT_GIS · org Alaska Department of Transportation & Public Facilities
- facts: arcgis-layer · esriGeometryPolyline · name field Route_Name · 268 records · last edit 2025-12-22
- closes: not probed

### Juneau Co Historical Imagery  ·    ·  from gis-hunter
- url: https://gismap.co.juneau.wi.us/server/rest/services/JuneauCo_Historical_Imagery/MapServer/0
- WHY: no polygons (no geometry)
- publisher: ? → official (government host gismap.co.juneau.wi.us)
- terms: CREDIT · source item page · "For use by the general public Juneau county, WI Juneau county, WI" · item https://gismap.co.juneau.wi.us/server/rest/services/JuneauCo_Historical_Imagery/MapServer/info/iteminfo
- facts: arcgis-layer
- closes: not probed

### Juneau Co Historical Imagery  ·    ·  from gis-hunter
- url: https://gismap.co.juneau.wi.us/server/rest/services/JuneauCo_Historical_Imagery/MapServer/1
- WHY: no polygons (no geometry)
- publisher: ? → official (government host gismap.co.juneau.wi.us)
- terms: CREDIT · source item page · "For use by the general public Juneau county, WI Juneau county, WI" · item https://gismap.co.juneau.wi.us/server/rest/services/JuneauCo_Historical_Imagery/MapServer/info/iteminfo
- facts: arcgis-layer
- closes: not probed

### Juneau Co Historical Imagery  ·    ·  from gis-hunter
- url: https://gismap.co.juneau.wi.us/server/rest/services/JuneauCo_Historical_Imagery/MapServer/2
- WHY: no polygons (no geometry)
- publisher: ? → official (government host gismap.co.juneau.wi.us)
- terms: CREDIT · source item page · "For use by the general public Juneau county, WI Juneau county, WI" · item https://gismap.co.juneau.wi.us/server/rest/services/JuneauCo_Historical_Imagery/MapServer/info/iteminfo
- facts: arcgis-layer
- closes: not probed

### Juneau Co Historical Imagery  ·    ·  from gis-hunter
- url: https://gismap.co.juneau.wi.us/server/rest/services/JuneauCo_Historical_Imagery/MapServer/3
- WHY: no polygons (no geometry)
- publisher: ? → official (government host gismap.co.juneau.wi.us)
- terms: CREDIT · source item page · "For use by the general public Juneau county, WI Juneau county, WI" · item https://gismap.co.juneau.wi.us/server/rest/services/JuneauCo_Historical_Imagery/MapServer/info/iteminfo
- facts: arcgis-layer
- closes: not probed

### Juneau Co Historical Imagery  ·    ·  from gis-hunter
- url: https://gismap.co.juneau.wi.us/server/rest/services/JuneauCo_Historical_Imagery/MapServer/4
- WHY: no polygons (no geometry)
- publisher: ? → official (government host gismap.co.juneau.wi.us)
- terms: CREDIT · source item page · "For use by the general public Juneau county, WI Juneau county, WI" · item https://gismap.co.juneau.wi.us/server/rest/services/JuneauCo_Historical_Imagery/MapServer/info/iteminfo
- facts: arcgis-layer
- closes: not probed

### Juneau Co Historical Imagery  ·    ·  from gis-hunter
- url: https://gismap.co.juneau.wi.us/server/rest/services/JuneauCo_Historical_Imagery/MapServer/5
- WHY: no polygons (no geometry)
- publisher: ? → official (government host gismap.co.juneau.wi.us)
- terms: CREDIT · source item page · "For use by the general public Juneau county, WI Juneau county, WI" · item https://gismap.co.juneau.wi.us/server/rest/services/JuneauCo_Historical_Imagery/MapServer/info/iteminfo
- facts: arcgis-layer
- closes: not probed

### Juneau Co Historical Imagery  ·    ·  from gis-hunter
- url: https://gismap.co.juneau.wi.us/server/rest/services/JuneauCo_Historical_Imagery/MapServer/6
- WHY: no polygons (no geometry)
- publisher: ? → official (government host gismap.co.juneau.wi.us)
- terms: CREDIT · source item page · "For use by the general public Juneau county, WI Juneau county, WI" · item https://gismap.co.juneau.wi.us/server/rest/services/JuneauCo_Historical_Imagery/MapServer/info/iteminfo
- facts: arcgis-layer
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
