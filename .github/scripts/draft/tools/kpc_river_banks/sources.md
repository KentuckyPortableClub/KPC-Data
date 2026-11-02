# Official water sources used by KPC 12 (river banks)

Finest official layer first. Never OpenStreetMap, Google, or imagery-made global sets (JRC etc.).

| Where | Source | Owner | Licence | Grade | Notes |
|---|---|---|---|---|---|
| Canada: British Columbia | BC Freshwater Atlas (FWA_RIVERS_POLY, FWA_LAKES_POLY, FWA_MANMADE_WATERBODIES_POLY; lines FWA_STREAM_NETWORKS_SP) | Province of British Columbia (GeoBC) | Open Government Licence - British Columbia | official | 1:20,000; finest official water for BC. |
| Canada: Ontario | Ontario Hydro Network (OHN) Waterbody; lines OHN Watercourse | Ontario Ministry of Natural Resources (Land Information Ontario) | Open Government Licence - Ontario | official | 1:10,000 south, 1:20,000 north, 1:50,000 far north. |
| Canada: Quebec | Geobase du reseau hydrographique du Quebec (GRHQ-HR) Hydrographie surfacique; lines Hydrographie lineaire | Gouvernement du Quebec (MRNF / MELCCFP) | Creative Commons Attribution 4.0 (CC BY 4.0) | official | 1:20,000 south (BDTQ), 1:50,000 north; wetlands left out. |
| Canada: every province (fallback; AB, MB and the rest until their own layer is wired) | Canadian Hydrospatial Network (CHN, NRCan; the NHN's successor) Waterbody; lines Flowline (large-scale) | Natural Resources Canada | Open Government Licence - Canada | official | National; only the work units NRCan has finished. Used where no finer provincial layer is wired. |
| Canada: every province (second fallback) | National Hydro Network (NHN) GeoBase waterbodies (local GeoPackage given with --nhn-gpkg) | Natural Resources Canada | Open Government Licence - Canada | official | NRCan offers NHN only as a 3.5 GB national download or a picture service (WMS), so the club downloads it once. |
| Switzerland | swisstopo swissTLM3D land cover (TLM_BODENBEDECKUNG: Fliessgewaesser, Stehende Gewaesser); lines swissTLM3D Gewaessernetz | Federal Office of Topography swisstopo | swisstopo Open Government Data (free use, source must be named: © swisstopo) | official | 1-3 m. Read once from the national download (about 1 GB of the 3.3 GB zip) and cut to water only in the cache. |
| France | IGN BD TOPO V3 hydrography = BD TOPAGE (surface_hydrographique; lines troncon_hydrographique) | Institut national de l'information geographique et forestiere (IGN) with OFB | Licence Ouverte Etalab 2.0 | official | Metre-level; BD TOPAGE is the hydro theme of BD TOPO. |
| Other EEA39 countries (incl. UK) | EU-Hydro River Network Database v1.3 (River_Net_polygon + InlandWater; lines River_Net_lines) | European Environment Agency / Copernicus Land Monitoring Service | Copernicus data policy (free, full and open; credit Copernicus / EEA) | Approximate (EU compilation) | Photo-interpreted 2006-2012, coarser than national layers. Used only where no national layer is wired. |
| Australia | Geoscience Australia Surface Hydrology Polygons (National); lines Surface Hydrology Lines (National) | Geoscience Australia | Creative Commons Attribution 4.0 International | official | Compiled from state agencies; 'Land Subject to Inundation' and swamps left out. |

## No national bank source read

- **NZ:** LINZ river polygons need an API key and the spec names none, so they are not read.
- **JP:** GSI water areas are published only as map tiles, and this tool has no reader for them yet.
- **GB:** Ordnance Survey Open Rivers is lines only and OS MasterMap water is not open data, so UK stretches get EU-Hydro (Approximate) instead.
- **US:** US stretches use the club's own USGS NHD reader, not this tool.
- **Everywhere else:** no official national water polygons wired yet: NO OFFICIAL BANK SOURCE.

## Not wired yet (finer national layers the club may add)

- Alberta (GeoDiscover Alberta hydrography) and Manitoba (Manitoba Land Initiative) provincial hydro layers: CHN / NHN is used meanwhile.
- Netherlands Kadaster TOP10NL, Sweden Lantmateriet, other national agencies: EU-Hydro (Approximate) is used meanwhile.
- New Zealand LINZ river polygons (needs a free API key: the club must approve one).
