# Layer intake review (2026-10-28)

Every lead in data/intake/queue.json, probed politely (metadata and counts only, never geometry). Chat 9 approves a READY row by setting `approved: true` in ready.json; the nightly key rebuild reads approved rows later. LIVE-ONLY = read live, never stored. ASK = the publisher must be asked (nothing stated, or hosted for an agency). Terms are read on the publisher's OWN item page first (the Nevada lesson).

| verdict | rows |
|---|---|
| READY | 3 |
| LIVE-ONLY | 0 |
| ASK-THE-PUBLISHER | 1 |
| REJECT | 7 |

## READY (3)

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

### Czechia natural parks (AOPK CR, gis.nature.cz, Prirodni park)  ·  CZ  ·  from chat 9
- url: https://gis.nature.cz/arcgis/rest/services/ObecnaOchrana/PrirodniPark/MapServer/0
- WHY: official, credit terms, named polygons, closes 19 missing park(s)
- publisher: Agentura ochrany prirody a krajiny CR (nature.cz) → official (government host gis.nature.cz)
- terms: CREDIT · source service copyrightText · "© krajské úřady ČR a Magistrát hl. m. Prahy, sjednoceno AOPK ČR, 2022"
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
- TEST: MISS LIVE-ONLY vs READY

### USACE reservoirs (Army Corps of Engineers)  ·  US  ·  from chat 9
- url: https://services7.arcgis.com/n1YM8pTrFmm7L4hs/arcgis/rest/services/usace_rez/FeatureServer/0
- WHY: official, open terms, named polygons, requested by chat 9
- publisher: U.S. Army Corps of Engineers → official (a federal / national agency named)
- terms: OPEN · source item page · "This data set is publicly available without any use restrictions; however, this data set was developed for use at a national" · item https://www.arcgis.com/home/item.html?id=03e322d7e89b48a9b48e9c3f4bcaf29e · owner usace_erd_aep
- facts: arcgis-layer · esriGeometryPolygon · name field NAME · 418 records · last edit 2024-04-02 · sample Two Rivers Reservoir / Santa Rosa Reservoir / Conchas Reservoir
- closes: 0 of 60 tested missing parks (by name 0, pin only 0; 1245 of the area's 1274 missing parks lie in the layer's extent)
- TEST: ok

## ASK-THE-PUBLISHER (1)

### PEI provincial parks (GeoLinc, ENV polygon layer)  ·  CA-PE  ·  from chat 9
- url: https://gis.princeedwardisland.ca/server/rest/services/GeoLincData/GeoLinc_provincial_park_polygon_ENV/MapServer/0
- WHY: nothing stated about use on the item page or the service
- publisher: Government of Prince Edward Island (GeoLinc) → official (government host gis.princeedwardisland.ca)
- terms: NOTHING STATED · source none
- facts: arcgis-layer · esriGeometryPolygon · name field PARK · 46 records · sample PROV / PROV PARK / BRUDENELL
- overlap: same publisher as PE-PP Govern
- closes: 0 of 0 tested missing parks (by name 0, pin only 0; 0 of the area's 36 missing parks lie in the layer's extent)
- TEST: ok

## REJECT (7)

### Nevada State Parks boundaries (Division of State Parks, VS Boundary Map)  ·  US-NV  ·  from chat 9
- url: https://services7.arcgis.com/5hLFVlePaucIMGhw/arcgis/rest/services/VS_Boundary_Map_2_WFL1/FeatureServer/2
- WHY: already read as sgnvc: nothing new to take
- publisher: Nevada Division of State Parks (AGOL org owner NDSP_1PARK; copyright Nevada Division of State Lands) → official (government words: Division)
- terms: CREDIT · source item page · "State of Nevada Department of Conservation and National Resrouces Nevada Division of State Lands" · item https://www.arcgis.com/home/item.html?id=e13c696359584dac85377bde0709bb6e · owner NDSP_1PARK · org Nevada Division of State Parks
- facts: arcgis-layer · esriGeometryPolygon · name field LandName · 1 records · last edit 2026-10-02 · sample Lake Tahoe State Park (Van Sickle Unit/AmackerSchultz)
- overlap: already read as sgnvc
- closes: not probed
- TEST: ok

### SCDNR managed lands (public viewer) on Clemson's ArcGIS Online account  ·  US-SC  ·  from chat 9
- url: https://services.arcgis.com/acgZYxoN5Oj8pDLa/arcgis/rest/services/SCDNR_Managed_Lands_Public_Viewer/FeatureServer/0
- WHY: did not open (error Invalid URL): url to confirm
- publisher: Clemson University (hosting for South Carolina DNR) → hosted for an agency (a university account holds an agency layer)
- terms: NOTHING STATED · source none
- facts: status error Invalid URL
- overlap: same publisher as sgsca
- closes: not probed
- TEST: MISS ASK-THE-PUBLISHER or already read vs REJECT

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

### My favorite camping spots (a hobby map)  ·  US-KY  ·  from chat 9
- url: https://services9.arcgis.com/abc123hobby/arcgis/rest/services/My_Favorite_Camping_Spots/FeatureServer/0
- WHY: did not open (error Invalid URL): url to confirm
- publisher: hobby account (personal map) → not official (hobby in the publisher words)
- terms: NOTHING STATED · source none
- facts: status error Invalid URL
- closes: not probed
- TEST: ok

### Slovenia protected areas (ARSO, INSPIRE PS WFS)  ·  W-SI  ·  from chat 9
- url: https://prostor4.gov.si/ows2-ins/ps/wfs
- WHY: did not open (rest): url to confirm
- publisher: Agencija RS za okolje (ARSO) / Slovenian Environment Agency → official (government host prostor4.gov.si)
- terms: OPEN · source GetCapabilities + queue row · "ATOM feed rights: 'No limitations'"
- facts: wfs · status rest
- closes: not probed: WFS point query not built
- TEST: MISS READY (WFS) or did-not-open vs REJECT

## Known-answer test rows

| row | expect | got | result |
|---|---|---|---|
| Nevada State Parks boundaries (Division of State Parks, VS Boundary Map) | READY or already read | REJECT | ok |
| USACE reservoirs (Army Corps of Engineers) | READY or already read | READY | ok |
| SCDNR managed lands (public viewer) on Clemson's ArcGIS Online account | ASK-THE-PUBLISHER or already read | REJECT | MISS ASK-THE-PUBLISHER or already read vs REJECT |
| PEI provincial parks (GeoLinc, ENV polygon layer) | ASK-THE-PUBLISHER | ASK-THE-PUBLISHER | ok |
| Czechia natural parks (AOPK CR, gis.nature.cz, Prirodni park) | LIVE-ONLY | READY | MISS LIVE-ONLY vs READY |
| Montana FWP state parks | already read | REJECT | ok |
| Doorstep Greens (England) polygons | READY or REJECT | REJECT | ok |
| Millennium Greens (England) polygons | READY or REJECT | REJECT | ok |
| SSSI units (England) | READY or REJECT | READY | ok |
| My favorite camping spots (a hobby map) | REJECT | REJECT | ok |
| Slovenia protected areas (ARSO, INSPIRE PS WFS) | READY (WFS) or did-not-open | REJECT | MISS READY (WFS) or did-not-open vs REJECT |

GATE=FAIL
