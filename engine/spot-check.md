# Spot check: all kinds (20 random rows of 14283)

For chat 11: open each link and say YES / NO. The engine decides nothing.

## US-6468 Iron Range OHV State Recreation Area (US-MN)
- status: candidate
- tier: T-3
- band: WEAK
- record_name: Iron Range Off-Highway Vehicle
- url: https://apps.bwsr.state.mn.us/arcgis/rest/services/DNR_Management_Units/MapServer/0?f=html
- record_link: https://apps.bwsr.state.mn.us/arcgis/rest/services/DNR_Management_Units/MapServer/0/query?where=OBJECTID%3D4192&outFields=%2A&f=html
- source_url: https://apps.bwsr.state.mn.us/arcgis/rest/services/DNR_Management_Units/MapServer/0/query?geometry=-92.4434%2C47.4825&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=true&outSR=4326&resultRecordCount=25&maxAllowableOffset=5e-05&geometryPrecision=6&distance=150&units=esriSRUnit_Meter&where=1%3D1&f=json
- pin_m: 0
- why: record 'Iron Range Off-Highway Vehicle' (PACK-US-MN-forest-27); pin inside; about 3531.3 acres; Rule G: LIKELY (names overlap); size unknown; confidence: likely
- answer: 

## US-9872 White River State Wildlife Area (US-WI)
- status: candidate
- tier: T-2
- band: WEAK
- record_name: White River Wildlife Area-Ashland
- url: https://dnrmaps.wi.gov/arcgis/rest/services/LF_DML/LF_AGOL_STAGING_WTM_Ext/MapServer/0?f=html
- record_link: https://dnrmaps.wi.gov/arcgis/rest/services/LF_DML/LF_AGOL_STAGING_WTM_Ext/MapServer/0/query?where=OBJECTID%3D713543&outFields=%2A&f=html
- source_url: https://dnrmaps.wi.gov/arcgis/rest/services/LF_DML/LF_AGOL_STAGING_WTM_Ext/MapServer/0/query?geometry=-90.8326%2C46.5054&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=true&outSR=4326&resultRecordCount=25&maxAllowableOffset=5e-05&geometryPrecision=6&distance=150&units=esriSRUnit_Meter&where=1%3D1&f=json
- pin_m: 0
- why: same land also in PACK-US-WI-preserve-59 'White River Boreal Forest': merged, counted once; record 'White River Wildlife Area-Ashland' (PACK-US-WI-land-370); pin inside; about 1273.1 acres; Rule G: LIKELY (names overlap); size unknown; confidence: likely
- answer: 

## US-12064 Henderson Swamp State Wilderness Area (US-TN)
- status: candidate
- tier: T-3
- band: WEAK
- record_name: Henderson Swamp
- url: https://tnmap.tn.gov/arcgis/rest/services/ENVIRONMENTAL/TWRA/MapServer/3?f=html
- record_link: https://tnmap.tn.gov/arcgis/rest/services/ENVIRONMENTAL/TWRA/MapServer/3/query?where=OBJECTID%3D29&outFields=%2A&f=html
- source_url: https://tnmap.tn.gov/arcgis/rest/services/ENVIRONMENTAL/TWRA/MapServer/3/query?geometry=-82.5799%2C36.2794&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=true&outSR=4326&resultRecordCount=25&maxAllowableOffset=5e-05&geometryPrecision=6&distance=150&units=esriSRUnit_Meter&where=1%3D1&f=json
- pin_m: 33
- why: record 'Henderson Swamp' (PACK-US-TN-wildlife-345); pin 33 m from the edge; about 24.1 acres; Rule G: SURE (names equal once kind words are stripped (R-G12: pin within 150 m)); size unknown; confidence: likely
- answer: 

## US-13651 Zim Wildlife Management Area (US-MN)
- status: found
- tier: T-2
- band: STRONG
- record_name: Zim WMA
- url: https://apps.bwsr.state.mn.us/arcgis/rest/services/DNR_Management_Units/MapServer/0?f=html
- record_link: https://apps.bwsr.state.mn.us/arcgis/rest/services/DNR_Management_Units/MapServer/0/query?where=OBJECTID%3D6177&outFields=%2A&f=html
- source_url: https://apps.bwsr.state.mn.us/arcgis/rest/services/DNR_Management_Units/MapServer/0/query?geometry=-92.6024%2C47.2157&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=true&outSR=4326&resultRecordCount=25&maxAllowableOffset=5e-05&geometryPrecision=6&distance=150&units=esriSRUnit_Meter&where=1%3D1&f=json
- pin_m: 0
- why: record 'Zim WMA' (PACK-US-MN-forest-27); pin inside; about 612.1 acres; Rule G: SURE (names equal once kind words are stripped); size unknown; confidence: sure
- answer: 

## CA-3334 Chukachida Protected Area (CA-BC)
- status: found
- tier: T-1
- band: STRONG
- record_name: CHUKACHIDA PROTECTED AREA
- url: https://openmaps.gov.bc.ca/geo/pub/wfs?service=WFS&request=DescribeFeatureType&version=2.0.0&typeNames=WHSE_TANTALIS.TA_PARK_ECORES_PA_SVW
- record_link: https://openmaps.gov.bc.ca/geo/pub/wfs?service=WFS&version=2.0.0&request=GetFeature&typeNames=WHSE_TANTALIS.TA_PARK_ECORES_PA_SVW&count=25&filter=%3Cfes%3AFilter%20xmlns%3Afes%3D%22http%3A%2F%2Fwww.opengis.net%2Ffes%2F2.0%22%3E%3Cfes%3APropertyIsLike%20wildCard%3D%22%2A%22%20singleChar%3D%22.%22%20escapeChar%3D%22%21%22%20matchCase%3D%22false%22%3E%3Cfes%3AValueReference%3EPROTECTED_LANDS_NAME%3C%2Ffes%3AValueReference%3E%3Cfes%3ALiteral%3E%2Achukachida%2A%3C%2Ffes%3ALiteral%3E%3C%2Ffes%3APropertyIsLike%3E%3C%2Ffes%3AFilter%3E
- source_url: https://openmaps.gov.bc.ca/geo/pub/wfs?service=WFS&version=2.0.0&request=GetFeature&typeNames=WHSE_TANTALIS.TA_PARK_ECORES_PA_SVW&count=25&filter=%3Cfes%3AFilter%20xmlns%3Afes%3D%22http%3A%2F%2Fwww.opengis.net%2Ffes%2F2.0%22%3E%3Cfes%3APropertyIsLike%20wildCard%3D%22%2A%22%20singleChar%3D%22.%22%20escapeChar%3D%22%21%22%20matchCase%3D%22false%22%3E%3Cfes%3AValueReference%3EPROTECTED_LANDS_NAME%3C%2Ffes%3AValueReference%3E%3Cfes%3ALiteral%3E%2Achukachida%2A%3C%2Ffes%3ALiteral%3E%3C%2Ffes%3APropertyIsLike%3E%3C%2Ffes%3AFilter%3E
- pin_m: 0
- why: record 'CHUKACHIDA PROTECTED AREA' (CA-BC-parks); pin inside; Rule G: SURE (names equal once kind words are stripped); size unknown; confidence: sure
- answer: 

## CA-4921 Saint Louis Forts and Chateaux National Historic Site (CA-QC)
- status: candidate
- tier: T-3
- band: CONFLICT
- record_name: Lieu historique national des Forts-et-Châteaux- Saint-Louis - Jardin du Gouverneur
- url: https://idgsi-rpgdi-arcgis.spac-pspc.gc.ca/gisserver/rest/services/Hosted/DFRP_PUBLIC/FeatureServer/4?f=html
- record_link: https://idgsi-rpgdi-arcgis.spac-pspc.gc.ca/gisserver/rest/services/Hosted/DFRP_PUBLIC/FeatureServer/4/query?where=OBJECTID%3D1819&outFields=%2A&f=html
- source_url: https://idgsi-rpgdi-arcgis.spac-pspc.gc.ca/gisserver/rest/services/Hosted/DFRP_PUBLIC/FeatureServer/4/query?geometry=-71.2045%2C46.811&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=true&outSR=4326&resultRecordCount=25&maxAllowableOffset=5e-05&geometryPrecision=6&distance=150&units=esriSRUnit_Meter&where=1%3D1&f=json
- pin_m: 34
- why: same land also in PACK-CA-QC-land-393 'Site patrimonial du Vieux-Québec': merged, counted once; record 'Lieu historique national des Forts-et-Châteaux- Saint-Louis - Jardin du Gouverneur' (Q-1781); pin 34 m from the edge; about 1.9 acres; Rule G: LIKELY (names overlap); size unknown; confidence: likely
- answer: 

## US-6409 Waimea State Recreation Area (US-HI)
- status: candidate
- tier: T-3
- band: WEAK
- record_name: WAIMEA STATE RECREATION PIER
- url: https://geodata.hawaii.gov/arcgis/rest/services/Infrastructure/MapServer/16?f=html
- record_link: https://geodata.hawaii.gov/arcgis/rest/services/Infrastructure/MapServer/16/query?where=OBJECTID%3D49&outFields=%2A&f=html
- source_url: https://geodata.hawaii.gov/arcgis/rest/services/Infrastructure/MapServer/16/query?geometry=-159.67%2C21.9548&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=true&outSR=4326&resultRecordCount=25&maxAllowableOffset=5e-05&geometryPrecision=6&distance=150&units=esriSRUnit_Meter&where=1%3D1&f=json
- pin_m: 32
- why: same land also in PACK-US-HI-wildlife-252 'WAIMEA STATE RECREATION PIER': merged, counted once; record 'WAIMEA STATE RECREATION PIER' (PACK-US-HI-park-251); pin 32 m from the edge; about 1.2 acres; Rule G: LIKELY (names overlap); size unknown; confidence: likely
- answer: 

## CA-1020 RécréoParc de Sainte-Catherine Regional Park (CA-QC)
- status: candidate
- tier: T-3
- band: WEAK
- record_name: Sainte-Catherine
- url: https://idgsi-rpgdi-arcgis.spac-pspc.gc.ca/gisserver/rest/services/Hosted/DFRP_PUBLIC/FeatureServer/4?f=html
- record_link: https://idgsi-rpgdi-arcgis.spac-pspc.gc.ca/gisserver/rest/services/Hosted/DFRP_PUBLIC/FeatureServer/4/query?where=OBJECTID%3D1986&outFields=%2A&f=html
- source_url: https://idgsi-rpgdi-arcgis.spac-pspc.gc.ca/gisserver/rest/services/Hosted/DFRP_PUBLIC/FeatureServer/4/query?geometry=-73.5755%2C45.4092&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=true&outSR=4326&resultRecordCount=25&maxAllowableOffset=5e-05&geometryPrecision=6&distance=150&units=esriSRUnit_Meter&where=1%3D1&f=json
- pin_m: 0
- why: record 'Sainte-Catherine' (PACK-CA-NB-land-73); pin inside; about 4395.3 acres; Rule G: LIKELY (names overlap); size unknown; confidence: likely
- answer: 

## CA-4908 Fort Temiscamingue National Historic Site (CA-QC)
- status: candidate
- tier: T-2
- band: WEAK
- record_name: Obadjiwan–Fort Témiscamingue National Historic Site
- url: https://idgsi-rpgdi-arcgis.spac-pspc.gc.ca/gisserver/rest/services/Hosted/DFRP_PUBLIC/FeatureServer/4?f=html
- record_link: https://idgsi-rpgdi-arcgis.spac-pspc.gc.ca/gisserver/rest/services/Hosted/DFRP_PUBLIC/FeatureServer/4/query?where=OBJECTID%3D4684&outFields=%2A&f=html
- source_url: https://idgsi-rpgdi-arcgis.spac-pspc.gc.ca/gisserver/rest/services/Hosted/DFRP_PUBLIC/FeatureServer/4/query?geometry=-79.4569%2C47.2903&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=true&outSR=4326&resultRecordCount=25&maxAllowableOffset=5e-05&geometryPrecision=6&distance=150&units=esriSRUnit_Meter&where=1%3D1&f=json
- pin_m: 0
- why: record 'Obadjiwan–Fort Témiscamingue National Historic Site' (Q-1781); pin inside; about 65.8 acres; Rule G: LIKELY (names overlap); size unknown; confidence: likely
- answer: 

## US-7821 Magic Reservoir Airstrip State Recreation Area (US-ID)
- status: candidate
- tier: T-3
- band: WEAK
- record_name: Magic Reservoir
- url: https://gis.blm.gov/idarcgis/rest/services/recreation/BLM_ID_Recreation_Area_Poly/MapServer/0?f=html
- record_link: https://gis.blm.gov/idarcgis/rest/services/recreation/BLM_ID_Recreation_Area_Poly/MapServer/0/query?where=OBJECTID%3D830&outFields=%2A&f=html
- source_url: https://gis.blm.gov/idarcgis/rest/services/recreation/BLM_ID_Recreation_Area_Poly/MapServer/0/query?geometry=-114.396%2C43.2807&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=true&outSR=4326&resultRecordCount=25&maxAllowableOffset=5e-05&geometryPrecision=6&distance=150&units=esriSRUnit_Meter&where=1%3D1&f=json
- pin_m: 0
- why: same land also in PACK-US-land-208 'Magic Reservoir', PACK-US-AK-land-214 'Magic Reservoir': merged, counted once; record 'Magic Reservoir' (PACK-US-ID-land-259); pin inside; about 21305.1 acres; Rule G: LIKELY (names overlap); size unknown; confidence: likely
- answer: 

## US-2810 Alderwood Wayside State Park (US-OR)
- status: candidate
- tier: T-3
- band: WEAK
- record_name: Alderwood
- url: https://maps.prd.state.or.us/arcgis/rest/services/Land_ownership/Oregon_State_Parks/FeatureServer/0?f=html
- record_link: https://maps.prd.state.or.us/arcgis/rest/services/Land_ownership/Oregon_State_Parks/FeatureServer/0/query?where=OBJECTID%3D41&outFields=%2A&f=html
- source_url: https://maps.prd.state.or.us/arcgis/rest/services/Land_ownership/Oregon_State_Parks/FeatureServer/0/query?geometry=-123.424%2C44.154&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=true&outSR=4326&resultRecordCount=25&maxAllowableOffset=5e-05&geometryPrecision=6&distance=150&units=esriSRUnit_Meter&where=1%3D1&f=json
- pin_m: 0
- why: same land also in PACK-US-OR-park-322 'Alderwood': merged, counted once; record 'Alderwood' (PACK-US-OR-land-206); pin inside; about 79.8 acres; Rule G: LIKELY (names overlap); size unknown; confidence: likely
- answer: 

## US-4168 Frances Slocum on Mississinewa Lake State Recreation Area (US-IN)
- status: candidate
- tier: T-3
- band: WEAK
- record_name: Mississinewa Lake
- url: https://gisdata.in.gov/server/rest/services/Hosted/ManagedLands_DNR_Open/FeatureServer/0?f=html
- record_link: https://gisdata.in.gov/server/rest/services/Hosted/ManagedLands_DNR_Open/FeatureServer/0/query?where=OBJECTID%3D4563&outFields=%2A&f=html
- source_url: https://gisdata.in.gov/server/rest/services/Hosted/ManagedLands_DNR_Open/FeatureServer/0/query?geometry=-85.923%2C40.7126&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=true&outSR=4326&resultRecordCount=25&maxAllowableOffset=5e-05&geometryPrecision=6&distance=150&units=esriSRUnit_Meter&where=1%3D1&f=json
- pin_m: 0
- why: same land also in PACK-US-IN-land-387 'Mississinewa Lake': merged, counted once; record 'Mississinewa Lake' (PACK-US-IN-land-191); pin inside; about 13068.9 acres; Rule G: LIKELY (names overlap); size unknown; confidence: likely
- answer: 

## US-7821 Magic Reservoir Airstrip State Recreation Area (US-ID)
- status: candidate
- tier: T-3
- band: WEAK
- record_name: Magic Reservoir
- url: https://gis.blm.gov/idarcgis/rest/services/recreation/BLM_ID_Recreation_Area_Poly/MapServer/0?f=html
- record_link: https://gis.blm.gov/idarcgis/rest/services/recreation/BLM_ID_Recreation_Area_Poly/MapServer/0/query?where=OBJECTID%3D830&outFields=%2A&f=html
- source_url: https://gis.blm.gov/idarcgis/rest/services/recreation/BLM_ID_Recreation_Area_Poly/MapServer/0/query?geometry=-114.396%2C43.2807&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=true&outSR=4326&resultRecordCount=25&maxAllowableOffset=5e-05&geometryPrecision=6&distance=150&units=esriSRUnit_Meter&where=1%3D1&f=json
- pin_m: 0
- why: same land also in PACK-US-land-208 'Magic Reservoir', PACK-US-AK-land-214 'Magic Reservoir': merged, counted once; record 'Magic Reservoir' (PACK-US-ID-land-259); pin inside; about 21305.1 acres; Rule G: LIKELY (names overlap); size unknown; confidence: likely
- answer: 

## US-11544 Twenty Four Mile Reservoir State Fishing Lake (US-ID)
- status: candidate
- tier: T-3
- band: WEAK
- record_name: Twentyfour Mile Reservoir
- url: https://services.arcgis.com/FjJI5xHF2dUPVrgK/arcgis/rest/services/Hydrography_Public/FeatureServer/0?f=html
- record_link: https://services.arcgis.com/FjJI5xHF2dUPVrgK/arcgis/rest/services/Hydrography_Public/FeatureServer/0/query?where=OBJECTID%3D1939071&outFields=%2A&f=html
- source_url: https://services.arcgis.com/FjJI5xHF2dUPVrgK/arcgis/rest/services/Hydrography_Public/FeatureServer/0/query?geometry=-111.888%2C42.9058&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=true&outSR=4326&resultRecordCount=25&maxAllowableOffset=5e-05&geometryPrecision=6&distance=150&units=esriSRUnit_Meter&where=1%3D1&f=json
- pin_m: 0
- why: record 'Twentyfour Mile Reservoir' (PACK-US-ID-land-258); pin inside; about 42.4 acres; Rule G: LIKELY (names overlap); size unknown; confidence: likely
- answer: 

## US-13640 Hole-In-Mountain Wildlife Management Area (US-MN)
- status: found
- tier: T-2
- band: STRONG
- record_name: Hole-In-Mountain WMA
- url: https://apps.bwsr.state.mn.us/arcgis/rest/services/DNR_Management_Units/MapServer/0?f=html
- record_link: https://apps.bwsr.state.mn.us/arcgis/rest/services/DNR_Management_Units/MapServer/0/query?where=OBJECTID%3D6120&outFields=%2A&f=html
- source_url: https://apps.bwsr.state.mn.us/arcgis/rest/services/DNR_Management_Units/MapServer/0/query?geometry=-96.3167%2C44.2256&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=true&outSR=4326&resultRecordCount=25&maxAllowableOffset=5e-05&geometryPrecision=6&distance=150&units=esriSRUnit_Meter&where=1%3D1&f=json
- pin_m: 0
- why: record 'Hole-In-Mountain WMA' (PACK-US-MN-forest-27); pin inside; about 637.5 acres; Rule G: SURE (names equal once kind words are stripped); size unknown; confidence: sure
- answer: 

## US-1263 Lake Malone State Park (US-KY)
- status: candidate
- tier: T-3
- band: WEAK
- record_name: Lake Malone
- url: https://kygisserver.ky.gov/arcgis/rest/services/WGS84WM_Services/Ky_State_Parks_Features_WGS84WM/MapServer/8?f=html
- record_link: https://kygisserver.ky.gov/arcgis/rest/services/WGS84WM_Services/Ky_State_Parks_Features_WGS84WM/MapServer/8/query?where=OBJECTID%3D4&outFields=%2A&f=html
- source_url: https://kygisserver.ky.gov/arcgis/rest/services/WGS84WM_Services/Ky_State_Parks_Features_WGS84WM/MapServer/8/query?geometry=-87.05195%2C37.07386&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=true&outSR=4326&resultRecordCount=25&maxAllowableOffset=5e-05&geometryPrecision=6&distance=150&units=esriSRUnit_Meter&where=1%3D1&f=json
- pin_m: 0
- why: record 'Lake Malone' (US-KY-stateparks); pin inside; about 376.4 acres; Rule G: SURE (names equal once kind words are stripped); size unknown; confidence: likely
- answer: 

## US-13398 Beginner's Hole State Recreation Site (US-WA)
- status: found
- tier: T-2
- band: STRONG
- record_name: Beginners' Hole
- url: https://geodataservices.wdfw.wa.gov/arcgis/rest/services/WP_RealEstate/ManagedPlaces/MapServer/0?f=html
- record_link: https://geodataservices.wdfw.wa.gov/arcgis/rest/services/WP_RealEstate/ManagedPlaces/MapServer/0/query?geometry=-122.807%2C46.0469&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=true&outSR=4326&resultRecordCount=25&maxAllowableOffset=5e-05&geometryPrecision=6&distance=150&units=esriSRUnit_Meter&where=1%3D1&f=json
- source_url: https://geodataservices.wdfw.wa.gov/arcgis/rest/services/WP_RealEstate/ManagedPlaces/MapServer/0/query?geometry=-122.807%2C46.0469&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=true&outSR=4326&resultRecordCount=25&maxAllowableOffset=5e-05&geometryPrecision=6&distance=150&units=esriSRUnit_Meter&where=1%3D1&f=json
- pin_m: 0
- why: record 'Beginners' Hole' (PACK-US-WA-wildlife-364); pin inside; about 2.3 acres; Rule G: SURE (names equal once kind words are stripped); size unknown; confidence: sure
- answer: 

## US-11534 Lamont Reservoir State Fishing Lake (US-ID)
- status: candidate
- tier: T-3
- band: WEAK
- record_name: Lamont Reservoir
- url: https://services.arcgis.com/FjJI5xHF2dUPVrgK/arcgis/rest/services/Hydrography_Public/FeatureServer/0?f=html
- record_link: https://services.arcgis.com/FjJI5xHF2dUPVrgK/arcgis/rest/services/Hydrography_Public/FeatureServer/0/query?where=OBJECTID%3D1938667&outFields=%2A&f=html
- source_url: https://services.arcgis.com/FjJI5xHF2dUPVrgK/arcgis/rest/services/Hydrography_Public/FeatureServer/0/query?geometry=-111.814%2C42.108&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=true&outSR=4326&resultRecordCount=25&maxAllowableOffset=5e-05&geometryPrecision=6&distance=150&units=esriSRUnit_Meter&where=1%3D1&f=json
- pin_m: 0
- why: same land also in US-FWS-approved 'BEAR RIVER WATERSHED CONSERVATION AREA', US-FWS-approved 'BEAR RIVER WATERSHED CONSERVATION AREA': merged, counted once; record 'Lamont Reservoir' (PACK-US-ID-land-258); pin inside; about 84.6 acres; Rule G: LIKELY (names overlap); size unknown; confidence: likely
- answer: 

## US-7782 Ben Doane Parcel of Nanjemoy Wildlife Management Area (US-MD)
- status: candidate
- tier: T-6
- band: WEAK
- record_name: NANJEMOY WMA
- url: https://mdgeodata.md.gov/imap/rest/services/Environment/MD_ProtectedLands/FeatureServer/0?f=html
- record_link: https://mdgeodata.md.gov/imap/rest/services/Environment/MD_ProtectedLands/FeatureServer/0/query?where=OBJECTID%3D293&outFields=%2A&f=html
- source_url: https://mdgeodata.md.gov/imap/rest/services/Environment/MD_ProtectedLands/FeatureServer/0/query?geometry=-77.2453%2C38.5213&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=true&outSR=4326&resultRecordCount=25&maxAllowableOffset=5e-05&geometryPrecision=6&distance=150&units=esriSRUnit_Meter&where=1%3D1&f=json
- pin_m: 0
- why: record 'NANJEMOY WMA' (PACK-US-MD-land-195); pin inside; about 1634.4 acres; Rule G: LIKELY (names overlap); size unknown; confidence: weak
- answer: 

## CA-5199 Marysville Historic District National Historic Site (CA-NB)
- status: candidate
- tier: T-4
- band: WEAK
- record_name: Heritage Heritage Center Park / Parc centre Marysville Heritage
- url: https://services2.arcgis.com/iLWAxhpxafhOza2U/arcgis/rest/services/Parks_Public_View/FeatureServer/0?f=html
- record_link: https://services2.arcgis.com/iLWAxhpxafhOza2U/arcgis/rest/services/Parks_Public_View/FeatureServer/0/query?where=OBJECTID%3D98&outFields=%2A&f=html
- source_url: https://services2.arcgis.com/iLWAxhpxafhOza2U/arcgis/rest/services/Parks_Public_View/FeatureServer/0/query?geometry=-66.5901%2C45.9763&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=true&outSR=4326&resultRecordCount=25&maxAllowableOffset=5e-05&geometryPrecision=6&distance=150&units=esriSRUnit_Meter&where=1%3D1&f=json
- pin_m: 0
- why: same land also in PACK-CA-NB-park-427 '': merged, counted once; record 'Heritage Heritage Center Park / Parc centre Marysville Heritage' (PACK-CA-NB-preserve-78); pin inside; about 2.1 acres; Rule G: SURE (names equal once kind words are stripped); size unknown; confidence: weak
- answer: 

