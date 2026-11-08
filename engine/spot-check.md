# Spot check: all kinds (20 random rows of 7565)

For chat 11: open each link and say YES / NO. The engine decides nothing.

## CA-5631 Cavan Swamp Wildlife Area (CA-ON)
- status: candidate
- tier: T-3
- band: WEAK
- record_name: Cavan Swamp Wildlife Area - Mount Pleasant Block
- url: https://maps2.grca.on.ca/server/rest/services/ORCA_Public/ORCA_Annual_Report_CAs/MapServer/2?f=html
- record_link: https://maps2.grca.on.ca/server/rest/services/ORCA_Public/ORCA_Annual_Report_CAs/MapServer/2/query?where=OBJECTID%3D95&outFields=%2A&f=html
- source_url: https://maps2.grca.on.ca/server/rest/services/ORCA_Public/ORCA_Annual_Report_CAs/MapServer/2/query?geometry=-78.4557%2C44.2829&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=true&outSR=4326&resultRecordCount=25&maxAllowableOffset=5e-05&geometryPrecision=6&distance=150&units=esriSRUnit_Meter&where=1%3D1&f=json
- pin_m: 9
- why: record 'Cavan Swamp Wildlife Area - Mount Pleasant Block' (PACK-CA-ON-land-407); pin 9 m from the edge; about 278.9 acres; Rule G: LIKELY (names overlap); size unknown; confidence: likely
- answer: 

## US-4171 Paynetown on Monroe Lake State Recreation Area (US-IN)
- status: candidate
- tier: T-6
- band: WEAK
- record_name: Monroe Lake
- url: https://gisdata.in.gov/server/rest/services/Hosted/ManagedLands_DNR_Open/FeatureServer/0?f=html
- record_link: https://gisdata.in.gov/server/rest/services/Hosted/ManagedLands_DNR_Open/FeatureServer/0/query?where=OBJECTID%3D4579&outFields=%2A&f=html
- source_url: https://gisdata.in.gov/server/rest/services/Hosted/ManagedLands_DNR_Open/FeatureServer/0/query?geometry=-86.4238%2C39.0931&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=true&outSR=4326&resultRecordCount=25&maxAllowableOffset=5e-05&geometryPrecision=6&distance=150&units=esriSRUnit_Meter&where=1%3D1&f=json
- pin_m: 29
- why: same land also in PACK-US-IN-land-387 'Monroe Lake': merged, counted once; record 'Monroe Lake' (PACK-US-IN-land-191); pin 29 m from the edge; about 482.2 acres; Rule G: LIKELY (names overlap); size unknown; confidence: weak
- answer: 

## CA-4339 Pontoon Lake Territorial Park (CA-NT)
- status: candidate
- tier: T-6
- band: WEAK
- record_name: Pontoon Lake
- url: https://www.apps.geomatics.gov.nt.ca/arcgis/rest/services/GNWT/PlanningCadastre_LCC/MapServer/16?f=html
- record_link: https://www.apps.geomatics.gov.nt.ca/arcgis/rest/services/GNWT/PlanningCadastre_LCC/MapServer/16/query?where=OBJECTID%3D31512&outFields=%2A&f=html
- source_url: https://www.apps.geomatics.gov.nt.ca/arcgis/rest/services/GNWT/PlanningCadastre_LCC/MapServer/16/query?geometry=-114.026%2C62.5531&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=true&outSR=4326&resultRecordCount=25&maxAllowableOffset=5e-05&geometryPrecision=6&distance=150&units=esriSRUnit_Meter&where=1%3D1&f=json
- pin_m: 6
- why: record 'Pontoon Lake' (PACK-CA-NT-park-85); pin 6 m from the edge; about 5.0 acres; Rule G: LIKELY (names overlap); size unknown; confidence: weak
- answer: 

## CA-4889 Trent - Severn Waterway National Historic Site (CA-ON)
- status: found
- tier: T-1
- band: STRONG
- record_name: Trent-Severn Waterway National Historic Site
- url: https://idgsi-rpgdi-arcgis.spac-pspc.gc.ca/gisserver/rest/services/Hosted/DFRP_PUBLIC/FeatureServer/4?f=html
- record_link: https://idgsi-rpgdi-arcgis.spac-pspc.gc.ca/gisserver/rest/services/Hosted/DFRP_PUBLIC/FeatureServer/4/query?where=OBJECTID%3D2260&outFields=%2A&f=html
- source_url: https://idgsi-rpgdi-arcgis.spac-pspc.gc.ca/gisserver/rest/services/Hosted/DFRP_PUBLIC/FeatureServer/4/query?geometry=-78.305%2C44.2991&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=true&outSR=4326&resultRecordCount=25&maxAllowableOffset=5e-05&geometryPrecision=6&distance=150&units=esriSRUnit_Meter&where=1%3D1&f=json
- pin_m: 0
- why: record 'Trent-Severn Waterway National Historic Site' (PACK-CA-NB-land-73); pin inside; about 138745.6 acres; Rule G: SURE (names equal once kind words are stripped); size unknown; confidence: sure
- answer: 

## GB-3747 Central Park (GB)
- status: candidate
- tier: T-2
- band: WEAK
- record_name: Central Sanday
- url: https://ogc.nature.scot/geoserver/protectedareas/wfs?service=WFS&request=DescribeFeatureType&version=2.0.0&typeNames=protectedareas%3Asssi
- record_link: https://ogc.nature.scot/geoserver/protectedareas/wfs?service=WFS&version=2.0.0&request=GetFeature&typeNames=protectedareas%3Asssi&count=25&filter=%3Cfes%3AFilter%20xmlns%3Afes%3D%22http%3A%2F%2Fwww.opengis.net%2Ffes%2F2.0%22%3E%3Cfes%3APropertyIsLike%20wildCard%3D%22%2A%22%20singleChar%3D%22.%22%20escapeChar%3D%22%21%22%20matchCase%3D%22false%22%3E%3Cfes%3AValueReference%3ENAME%3C%2Ffes%3AValueReference%3E%3Cfes%3ALiteral%3E%2Acentral%2A%3C%2Ffes%3ALiteral%3E%3C%2Ffes%3APropertyIsLike%3E%3C%2Ffes%3AFilter%3E
- source_url: https://ogc.nature.scot/geoserver/protectedareas/wfs?service=WFS&version=2.0.0&request=GetFeature&typeNames=protectedareas%3Asssi&count=25&filter=%3Cfes%3AFilter%20xmlns%3Afes%3D%22http%3A%2F%2Fwww.opengis.net%2Ffes%2F2.0%22%3E%3Cfes%3APropertyIsLike%20wildCard%3D%22%2A%22%20singleChar%3D%22.%22%20escapeChar%3D%22%21%22%20matchCase%3D%22false%22%3E%3Cfes%3AValueReference%3ENAME%3C%2Ffes%3AValueReference%3E%3Cfes%3ALiteral%3E%2Acentral%2A%3C%2Ffes%3ALiteral%3E%3C%2Ffes%3APropertyIsLike%3E%3C%2Ffes%3AFilter%3E
- pin_m: 0
- why: record 'Central Sanday' (GB-SCT-sssi); pin inside; Rule G: LIKELY (names overlap); size unknown; confidence: likely
- answer: 

## GB-1000 Clwydian Range and Dee Valley Area of Outstanding Natural Beauty (GB)
- status: candidate
- tier: T-3
- band: WEAK
- record_name: BRYNIAU CLWYD A DYFFRYN DYFRDWY/CLWYDIAN RANGE AND DEE VALLEY
- url: https://datamap.gov.wales/geoserver/ows?service=WFS&request=DescribeFeatureType&version=2.0.0&typeNames=geonode%3AGWC21_Area_of_Outstanding_Natural_Beauty
- record_link: https://datamap.gov.wales/geoserver/ows?service=WFS&version=2.0.0&request=GetFeature&typeNames=geonode%3AGWC21_Area_of_Outstanding_Natural_Beauty&count=25&bbox=324798.8161270783%2C361310.3743271993%2C325104.03755836404%2C361614.88032258034%2CEPSG%3A27700
- source_url: https://datamap.gov.wales/geoserver/ows?service=WFS&version=2.0.0&request=GetFeature&typeNames=geonode%3AGWC21_Area_of_Outstanding_Natural_Beauty&count=25&bbox=324798.8161270783%2C361310.3743271993%2C325104.03755836404%2C361614.88032258034%2CEPSG%3A27700
- pin_m: 0
- why: record 'BRYNIAU CLWYD A DYFFRYN DYFRDWY/CLWYDIAN RANGE AND DEE VALLEY' (GB-WLS-GWC21_Area_of_Outstanding_Natural_Beauty); pin inside; Rule G: LIKELY (names overlap); size unknown; confidence: likely
- answer: 

## CA-4900 Cartier-Brébeuf National Historic Site (CA-QC)
- status: found
- tier: T-1
- band: STRONG
- record_name: Cartier-Brébeuf National Historic Site
- url: https://idgsi-rpgdi-arcgis.spac-pspc.gc.ca/gisserver/rest/services/Hosted/DFRP_PUBLIC/FeatureServer/4?f=html
- record_link: https://idgsi-rpgdi-arcgis.spac-pspc.gc.ca/gisserver/rest/services/Hosted/DFRP_PUBLIC/FeatureServer/4/query?where=OBJECTID%3D1838&outFields=%2A&f=html
- source_url: https://idgsi-rpgdi-arcgis.spac-pspc.gc.ca/gisserver/rest/services/Hosted/DFRP_PUBLIC/FeatureServer/4/query?geometry=-71.2392%2C46.8258&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=true&outSR=4326&resultRecordCount=25&maxAllowableOffset=5e-05&geometryPrecision=6&distance=150&units=esriSRUnit_Meter&where=1%3D1&f=json
- pin_m: 0
- why: record 'Cartier-Brébeuf National Historic Site' (PACK-CA-NB-land-73); pin inside; about 13.1 acres; Rule G: SURE (names equal once kind words are stripped); size unknown; confidence: sure
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

## GB-1003 Gwydir Forest Park (GB)
- status: candidate
- tier: T-2
- band: WEAK
- record_name: Gwydir Bay
- url: https://datamap.gov.wales/geoserver/ows?service=WFS&request=DescribeFeatureType&version=2.0.0&typeNames=inspire-nrw%3ANRW_SSSI
- record_link: https://datamap.gov.wales/geoserver/ows?service=WFS&version=2.0.0&request=GetFeature&typeNames=inspire-nrw%3ANRW_SSSI&count=25&filter=%3Cfes%3AFilter%20xmlns%3Afes%3D%22http%3A%2F%2Fwww.opengis.net%2Ffes%2F2.0%22%3E%3Cfes%3APropertyIsLike%20wildCard%3D%22%2A%22%20singleChar%3D%22.%22%20escapeChar%3D%22%21%22%20matchCase%3D%22false%22%3E%3Cfes%3AValueReference%3Esssi_name%3C%2Ffes%3AValueReference%3E%3Cfes%3ALiteral%3E%2Agwydir%2A%3C%2Ffes%3ALiteral%3E%3C%2Ffes%3APropertyIsLike%3E%3C%2Ffes%3AFilter%3E
- source_url: https://datamap.gov.wales/geoserver/ows?service=WFS&version=2.0.0&request=GetFeature&typeNames=inspire-nrw%3ANRW_SSSI&count=25&filter=%3Cfes%3AFilter%20xmlns%3Afes%3D%22http%3A%2F%2Fwww.opengis.net%2Ffes%2F2.0%22%3E%3Cfes%3APropertyIsLike%20wildCard%3D%22%2A%22%20singleChar%3D%22.%22%20escapeChar%3D%22%21%22%20matchCase%3D%22false%22%3E%3Cfes%3AValueReference%3Esssi_name%3C%2Ffes%3AValueReference%3E%3Cfes%3ALiteral%3E%2Agwydir%2A%3C%2Ffes%3ALiteral%3E%3C%2Ffes%3APropertyIsLike%3E%3C%2Ffes%3AFilter%3E
- pin_m: 0
- why: record 'Gwydir Bay' (GB-WLS-NRW_SSSI); pin inside; Rule G: LIKELY (names overlap); size unknown; confidence: likely
- answer: 

## US-11700 Wolsfeld Woods SNA State Sanctuary (US-MN)
- status: candidate
- tier: T-6
- band: WEAK
- record_name: Wolsfeld Woods
- url: https://apps.bwsr.state.mn.us/arcgis/rest/services/DNR_Management_Units/MapServer/0?f=html
- record_link: https://apps.bwsr.state.mn.us/arcgis/rest/services/DNR_Management_Units/MapServer/0/query?where=OBJECTID%3D4431&outFields=%2A&f=html
- source_url: https://apps.bwsr.state.mn.us/arcgis/rest/services/DNR_Management_Units/MapServer/0/query?geometry=-93.5741%2C44.9997&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=true&outSR=4326&resultRecordCount=25&maxAllowableOffset=5e-05&geometryPrecision=6&distance=150&units=esriSRUnit_Meter&where=1%3D1&f=json
- pin_m: 25
- why: same land also in PACK-US-MN-preserve-278 'Wolsfeld Woods': merged, counted once; record 'Wolsfeld Woods' (PACK-US-MN-forest-27); pin 25 m from the edge; about 221.5 acres; Rule G: SURE (names equal once kind words are stripped (R-G12: pin within 150 m)); size unknown; confidence: weak
- answer: 

## CA-6261 Tombstone Mountain Campground Recreation Site (CA-YT)
- status: candidate
- tier: T-3
- band: WEAK
- record_name: Tombstone
- url: https://mapservices.gov.yk.ca/arcgis/rest/services/GeoYukon/GY_ParksProtectedAreas/MapServer/3?f=html
- record_link: https://mapservices.gov.yk.ca/arcgis/rest/services/GeoYukon/GY_ParksProtectedAreas/MapServer/3/query?where=OBJECTID%3D20&outFields=%2A&f=html
- source_url: https://mapservices.gov.yk.ca/arcgis/rest/services/GeoYukon/GY_ParksProtectedAreas/MapServer/3/query?geometry=-138.22%2C64.506&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=true&outSR=4326&resultRecordCount=25&maxAllowableOffset=5e-05&geometryPrecision=6&distance=150&units=esriSRUnit_Meter&where=1%3D1&f=json
- pin_m: 0
- why: record 'Tombstone' (PACK-CA-YT-park-456); pin inside; about 506547.2 acres; Rule G: LIKELY (names overlap); size unknown; confidence: likely
- answer: 

## US-2218 Nu'uanu Pali Wayside State Park (US-HI)
- status: candidate
- tier: T-2
- band: WEAK
- record_name: NUUANU PALI STATE WAYSIDE
- url: https://geodata.hawaii.gov/arcgis/rest/services/Infrastructure/MapServer/16?f=html
- record_link: https://geodata.hawaii.gov/arcgis/rest/services/Infrastructure/MapServer/16/query?where=OBJECTID%3D12&outFields=%2A&f=html
- source_url: https://geodata.hawaii.gov/arcgis/rest/services/Infrastructure/MapServer/16/query?geometry=-157.793%2C21.3668&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=true&outSR=4326&resultRecordCount=25&maxAllowableOffset=5e-05&geometryPrecision=6&distance=150&units=esriSRUnit_Meter&where=1%3D1&f=json
- pin_m: 0
- why: record 'NUUANU PALI STATE WAYSIDE' (PACK-US-HI-park-251); pin inside; about 4.0 acres; Rule G: SURE (names equal once kind words are stripped); size unknown; confidence: likely
- answer: 

## US-8550 Missouri-Yellowstone Confluence Interpretive Center State Historic Site (US-ND)
- status: candidate
- tier: T-3
- band: WEAK
- record_name: SW of Williston at confluence of Yellowstone and Missouri Rivers
- url: https://mapservices.nps.gov/arcgis/rest/services/cultural_resources/nrhp_locations/MapServer/1?f=html
- record_link: https://mapservices.nps.gov/arcgis/rest/services/cultural_resources/nrhp_locations/MapServer/1/query?where=OBJECTID%3D400132&outFields=%2A&f=html
- source_url: https://mapservices.nps.gov/arcgis/rest/services/cultural_resources/nrhp_locations/MapServer/1/query?geometry=-103.989%2C47.9851&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=true&outSR=4326&resultRecordCount=25&maxAllowableOffset=5e-05&geometryPrecision=6&distance=150&units=esriSRUnit_Meter&where=1%3D1&f=json
- pin_m: 0
- why: record 'SW of Williston at confluence of Yellowstone and Missouri Rivers' (PACK-US-AK-land-41); pin inside; about 636.1 acres; Rule G: LIKELY (names overlap); size unknown; confidence: likely
- answer: 

## US-7370 Ravinia Woods State Forest (US-IN)
- status: candidate
- tier: T-6
- band: WEAK
- record_name: Ravinia State Forest
- url: https://gisdata.in.gov/server/rest/services/Hosted/ManagedLands_DNR_Open/FeatureServer/0?f=html
- record_link: https://gisdata.in.gov/server/rest/services/Hosted/ManagedLands_DNR_Open/FeatureServer/0/query?where=OBJECTID%3D4917&outFields=%2A&f=html
- source_url: https://gisdata.in.gov/server/rest/services/Hosted/ManagedLands_DNR_Open/FeatureServer/0/query?geometry=-86.5448%2C39.4347&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=true&outSR=4326&resultRecordCount=25&maxAllowableOffset=5e-05&geometryPrecision=6&distance=150&units=esriSRUnit_Meter&where=1%3D1&f=json
- pin_m: 4
- why: record 'Ravinia State Forest' (PACK-US-IN-land-191); pin 4 m from the edge; about 1368.6 acres; Rule G: LIKELY (names overlap); size unknown; confidence: weak
- answer: 

## US-5709 Nodaway State Conservation Area (US-MO)
- status: candidate
- tier: T-2
- band: WEAK
- record_name: Nodaway Valley CA
- url: https://gisblue.mdc.mo.gov/arcgis/rest/services/Discover_Nature/MDC_Administrative_Areas/FeatureServer/5?f=html
- record_link: https://gisblue.mdc.mo.gov/arcgis/rest/services/Discover_Nature/MDC_Administrative_Areas/FeatureServer/5/query?where=OBJECTID%3D735&outFields=%2A&f=html
- source_url: https://gisblue.mdc.mo.gov/arcgis/rest/services/Discover_Nature/MDC_Administrative_Areas/FeatureServer/5/query?geometry=-95.078%2C40.0875&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=true&outSR=4326&resultRecordCount=25&maxAllowableOffset=5e-05&geometryPrecision=6&distance=150&units=esriSRUnit_Meter&where=1%3D1&f=json
- pin_m: 0
- why: record 'Nodaway Valley CA' (PACK-US-MO-land-283); pin inside; about 3960.6 acres; Rule G: LIKELY (names overlap); size unknown; confidence: likely
- answer: 

## US-10751 Idylwild Natural Area (US-MD)
- status: found
- tier: T-2
- band: STRONG
- record_name: Idywild
- url: https://dnr.geodata.md.gov/dnrdata/rest/services/Environment/MDNaturalAreasGuide/MapServer/0?f=html
- record_link: https://dnr.geodata.md.gov/dnrdata/rest/services/Environment/MDNaturalAreasGuide/MapServer/0/query?where=OBJECTID%3D16&outFields=%2A&f=html
- source_url: https://dnr.geodata.md.gov/dnrdata/rest/services/Environment/MDNaturalAreasGuide/MapServer/0/query?geometry=-75.7606%2C38.733&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=true&outSR=4326&resultRecordCount=25&maxAllowableOffset=5e-05&geometryPrecision=6&distance=150&units=esriSRUnit_Meter&where=1%3D1&f=json
- pin_m: 0
- why: same land also in PACK-US-MD-land-195 'IDYLWILD WMA': merged, counted once; record 'Idywild' (PACK-US-MD-preserve-272); pin inside; about 1494.8 acres; Rule G: SURE (names equal once kind words are stripped); size unknown; confidence: sure
- answer: 

## US-6326 T.M. Goodwin Wildlife Management Area (US-FL)
- status: found
- tier: T-2
- band: STRONG
- record_name: T. M. Goodwin Waterfowl Management Area
- url: https://gis.myfwc.com/mapping/rest/services/Open_Data/Wildlife_Management_Areas_Florida/MapServer/1?f=html
- record_link: https://gis.myfwc.com/mapping/rest/services/Open_Data/Wildlife_Management_Areas_Florida/MapServer/1/query?where=OBJECTID%3D12&outFields=%2A&f=html
- source_url: https://gis.myfwc.com/mapping/rest/services/Open_Data/Wildlife_Management_Areas_Florida/MapServer/1/query?geometry=-80.7125%2C27.845&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=true&outSR=4326&resultRecordCount=25&maxAllowableOffset=5e-05&geometryPrecision=6&distance=150&units=esriSRUnit_Meter&where=1%3D1&f=json
- pin_m: 0
- why: same land also in PACK-US-FL-land-246 'USJR Project - Federal Flood Control Project': merged, counted once; record 'T. M. Goodwin Waterfowl Management Area' (PACK-US-FL-wildlife-247); pin inside; about 3450.7 acres; Rule G: SURE (names equal once kind words are stripped); size unknown; confidence: sure
- answer: 

## CA-6398 Craigflower Manor House National Historic Site (CA-BC)
- status: candidate
- tier: T-3
- band: WEAK
- record_name: Craigflower Manor
- url: https://maps.gov.bc.ca/arcgis/rest/services/whse/bcgw_pub_whse_human_cultural_economic/MapServer/82?f=html
- record_link: https://maps.gov.bc.ca/arcgis/rest/services/whse/bcgw_pub_whse_human_cultural_economic/MapServer/82/query?where=OBJECTID%3D6127684&outFields=%2A&f=html
- source_url: https://maps.gov.bc.ca/arcgis/rest/services/whse/bcgw_pub_whse_human_cultural_economic/MapServer/82/query?geometry=-123.424%2C48.4517&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=true&outSR=4326&resultRecordCount=25&maxAllowableOffset=5e-05&geometryPrecision=6&distance=150&units=esriSRUnit_Meter&where=1%3D1&f=json
- pin_m: 0
- why: same land also in PACK-CA-BC-park-420 'Craigflower Farm Historic Site': merged, counted once; record 'Craigflower Manor' (PACK-CA-BC-land-416); pin inside; about 1.5 acres; Rule G: LIKELY (names overlap); size unknown; confidence: likely
- answer: 

## US-13269 Lake Tahoe-Eastshore Dr Byway Area of Outstanding Natural Beauty (US-NV)
- status: candidate
- tier: T-6
- band: WEAK
- record_name: Lake Tahoe Basin Management Unit
- url: https://apps.fs.usda.gov/arcx/rest/services/EDW/EDW_BasicOwnership_02/MapServer/0?f=html
- record_link: https://apps.fs.usda.gov/arcx/rest/services/EDW/EDW_BasicOwnership_02/MapServer/0/query?where=OBJECTID%3D109&outFields=%2A&f=html
- source_url: https://apps.fs.usda.gov/arcx/rest/services/EDW/EDW_BasicOwnership_02/MapServer/0/query?geometry=-119.942%2C38.9593&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=true&outSR=4326&resultRecordCount=25&maxAllowableOffset=5e-05&geometryPrecision=6&distance=150&units=esriSRUnit_Meter&where=1%3D1&f=json
- pin_m: 0
- why: record 'Lake Tahoe Basin Management Unit' (US-USFS-ownership); pin inside; about 176285.6 acres; Rule G: LIKELY (names overlap); size unknown; confidence: weak
- answer: 

## CA-5022 Parc du Mont-Bellevue Regional Park (CA-QC)
- status: candidate
- tier: T-3
- band: WEAK
- record_name: Réserve naturelle universitaire du Parc-du-Mont-Bellevue (Secteur de l'Université-de-Sherbrooke)
- url: https://geo.environnement.gouv.qc.ca/donnees/rest/services/Biodiversite/Aires_protegees/MapServer/23?f=html
- record_link: https://geo.environnement.gouv.qc.ca/donnees/rest/services/Biodiversite/Aires_protegees/MapServer/23/query?where=OBJECTID%3D1400&outFields=%2A&f=html
- source_url: https://geo.environnement.gouv.qc.ca/donnees/rest/services/Biodiversite/Aires_protegees/MapServer/23/query?geometry=-71.9087%2C45.3773&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=true&outSR=4326&resultRecordCount=25&maxAllowableOffset=5e-05&geometryPrecision=6&distance=150&units=esriSRUnit_Meter&where=1%3D1&f=json
- pin_m: 44
- why: same land also in PACK-CA-QC-park-448 'Réserve naturelle universitaire du Parc-du-Mont-Bellevue (Secteur de l'Université-de-Sherbrooke)': merged, counted once; record 'Réserve naturelle universitaire du Parc-du-Mont-Bellevue (Secteur de l'Université-de-Sherbrooke)' (PACK-CA-QC-park-447); pin 44 m from the edge; about 309.6 acres; Rule G: LIKELY (names overlap); size unknown; confidence: likely
- answer: 

