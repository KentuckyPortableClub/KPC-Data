"""Seed list for world_sources.json (run once; verify.py then fills 'verified' and detected name fields).
Kept so chat 10 can see where every entry came from (discovered_via). Re-running keeps earlier 'verified' blocks."""
import json, pathlib
S = []
def add(id, cc, country, agency, kind, url, layer=None, name_field=None, designation='', grade='official', pota_words=None, via='', **kw):
    e = dict(id=id, cc=cc, country=country, agency=agency, kind=kind, url=url, layer=layer, name_field=name_field, designation=designation,
             grade=grade, pota_words=pota_words, discovered_via=via); e.update(kw); S.append(e)

GA = 'https://api3.geo.admin.ch/rest/services/api/MapServer'
for lid, des, w in [('ch.bafu.schutzgebiete-paerke_nationaler_bedeutung', 'Parks of national importance (regional nature parks, national park, nature discovery parks)', 'Nature Park|Park'),
                                        ('ch.bafu.bundesinventare-bln', 'Federal Inventory of Landscapes (BLN)', 'Landscape|BLN'),
                    ('ch.bafu.bundesinventare-jagdbanngebiete', 'Federal hunting reserves', 'Hunting|Wildlife|Reserve'),
                    ('ch.bafu.bundesinventare-vogelreservate', 'Waterbird and migratory bird reserves', 'Bird'),
                    ('ch.bafu.bundesinventare-auen', 'Floodplains of national importance', 'Floodplain|Aue'),
                    ('ch.bafu.bundesinventare-moorlandschaften', 'Mire landscapes', 'Mire|Moor'),
                    ('ch.bafu.schutzgebiete-ramsar', 'Ramsar sites', 'Ramsar'),
                    ('ch.bafu.schutzgebiete-smaragd', 'Emerald network', 'Emerald')]:
    add('CH-' + lid.split('.')[-1], 'CH', 'Switzerland', 'FOEN / BAFU (via swisstopo geo.admin.ch federal API)', 'geoadmin', GA, lid, 'label', des, pota_words=w,
        via='geo.admin.ch federal geoportal (POTA CH pages link s.geo.admin.ch)')

NE = 'https://services.arcgis.com/JJzESW51TqeY9uat/arcgis/rest/services/{}/FeatureServer/0'
for svc, des, w in [('National_Nature_Reserves_England', 'National Nature Reserves', 'Nature Reserve|NNR'), ('Local_Nature_Reserves_England', 'Local Nature Reserves', 'Nature Reserve|LNR'),
                    ('Country_Parks_England', 'Country Parks', 'Country Park'), ('National_Parks_England', 'National Parks', 'National Park'),
                    ('Areas_of_Outstanding_Natural_Beauty_England', 'National Landscapes (AONB)', 'AONB|Outstanding|National Landscape'),
                    ('Sites_of_Special_Scientific_Interest_England', 'SSSI', 'SSSI|Scientific'), ('Special_Protection_Areas_England', 'SPA', 'SPA|Protection Area'),
                    ('Special_Areas_of_Conservation_England', 'SAC', 'SAC|Conservation'), ('Ramsar_England', 'Ramsar', 'Ramsar'),
                    ('Millennium_Greens_England_Polygons', 'Millennium Greens', 'Green'), ('Doorstep_Greens_England', 'Doorstep Greens', 'Green'),
                    ('National_Trails_England', 'National Trails (lines)', 'Trail|Way|Path')]:
    add('GB-ENG-' + svc, 'GB', 'United Kingdom (England)', 'Natural England (verified ArcGIS org JJzESW51TqeY9uat)', 'arcgis', NE.format(svc), None, None, des,
        pota_words=w, via='Natural England ArcGIS org service list', region='ENG')

W = 'https://datamap.gov.wales/geoserver/ows'
for ly, des, w in [('inspire-nrw:NRW_NATIONAL_PARK', 'National Parks', 'National Park'), ('inspire-nrw:NRW_NNR', 'National Nature Reserves', 'Nature Reserve|NNR'),
                   ('inspire-nrw:NRW_SSSI', 'SSSI', 'SSSI'), ('geonode:country_parks', 'Country Parks', 'Country Park'),
                   ('geonode:GWC21_Area_of_Outstanding_Natural_Beauty', 'National Landscapes (AONB)', 'AONB|Outstanding')]:
    add('GB-WLS-' + ly.split(':')[1], 'GB', 'United Kingdom (Wales)', 'Natural Resources Wales / Welsh Government (DataMapWales)', 'wfs', W, ly, None, des, srs=27700,
        pota_words=w, via='DataMapWales GeoServer WFS capabilities', region='WLS', pota_bbox=[-5.4, 51.35, -2.95, 53.45])

SC = 'https://ogc.nature.scot/geoserver/protectedareas/wfs'
for ly, des, w in [('protectedareas:nnr', 'National Nature Reserves', 'Nature Reserve|NNR'), ('protectedareas:sssi', 'SSSI', 'SSSI'),
                   ('protectedareas:cpk', 'Country Parks', 'Country Park'), ('protectedareas:rp', 'Regional Parks', 'Regional Park'),
                   ('protectedareas:lnr', 'Local Nature Reserves', 'Local Nature'), ('protectedareas:sac', 'SAC', 'SAC'), ('protectedareas:spa', 'SPA', 'SPA'),
                   ('protectedareas:ramsar', 'Ramsar', 'Ramsar')]:
    add('GB-SCT-' + ly.split(':')[1], 'GB', 'United Kingdom (Scotland)', 'NatureScot', 'wfs', SC, ly, None, des, srs=27700, pota_words=w,
        via='NatureScot GeoServer WFS capabilities', region='SCT', pota_bbox=[-8.7, 55.0, -0.7, 60.9])

# Round 3 (Nov 1): NatureScot's own NNR layer on ArcGIS (geometry readable), linked from NatureScot's metadata record. Live-checked at GB-0889.
add('GB-SCT-National_Nature_Reserves_ArcGIS', 'GB', 'United Kingdom (Scotland)', 'NatureScot', 'arcgis',
    'https://services1.arcgis.com/LM9GyVFsughzHdbO/arcgis/rest/services/National_Nature_Reserves/FeatureServer/0', None, 'NAME',
    'National Nature Reserves (Scotland)', pota_words='Nature Reserve|NNR', via='spatialdata.gov.scot metadata (NatureScot)', region='SCT',
    pota_bbox=[-8.7, 55.0, -0.7, 60.9])

add('NO-naturvern_omrade', 'NO', 'Norway', 'Miljødirektoratet (Norwegian Environment Agency)', 'arcgis', 'https://kart.miljodirektoratet.no/arcgis/rest/services/vern/MapServer/0',
    None, 'navn', 'All protected areas (nasjonalpark, naturreservat, landskapsvernområde ...)', via='agency ArcGIS server')
BFN = 'https://geodienste.bfn.de/ogc/wfs/schutzgebiet'
for ly, des, w in [('Nationalparke', 'National parks', 'National'), ('Naturparke', 'Nature parks', 'Naturpark|Nature Park'), ('Naturschutzgebiete', 'Nature reserves (NSG)', 'Naturschutz|Nature Reserve|NSG'),
                   ('Landschaftsschutzgebiete', 'Landscape protection areas (LSG)', 'Landschaft|LSG'), ('Biosphaerenreservate', 'Biosphere reserves', 'Biosph'),
                   ('Fauna_Flora_Habitat_Gebiete', 'FFH / SAC (national copy)', 'FFH'), ('Vogelschutzgebiete', 'Bird protection areas (SPA)', 'Vogel'),
                   ('Nationale_Naturmonumente', 'National natural monuments', 'Monument')]:
    add('DE-BfN-' + ly, 'DE', 'Germany', 'Bundesamt für Naturschutz (BfN, federal agency; data from the Länder)', 'wfs', BFN, 'schutzgebiet:' + ly, None, des, srs=25832,
        pota_words=w, via='BfN geodienste WFS capabilities')
add('NL-natura2000', 'NL', 'Netherlands', 'RVO / Ministry of Agriculture, Nature and Food Quality (PDOK)', 'wfs', 'https://service.pdok.nl/rvo/natura2000/wfs/v1_0',
    'natura2000:natura2000', None, 'Natura 2000 (national publication)', srs=28992, via='PDOK national geoportal')
add('AU-CAPAD-terrestrial', 'AU', 'Australia', 'DCCEEW (Australian Government) CAPAD 2024, from the state and territory agencies', 'arcgis',
    'https://gis.environment.gov.au/gispubmap/rest/services/ogc_services/CAPAD/MapServer/0', None, 'NAME', 'All terrestrial protected areas (national + state parks, reserves)', via='DCCEEW ArcGIS server')
add('AU-CAPAD-marine', 'AU', 'Australia', 'DCCEEW CAPAD 2024', 'arcgis', 'https://gis.environment.gov.au/gispubmap/rest/services/ogc_services/CAPAD/MapServer/1', None, 'NAME',
    'Marine protected areas', pota_words='Marine', via='DCCEEW ArcGIS server')
add('NZ-DOC-PCL', 'NZ', 'New Zealand', 'Department of Conservation (verified ArcGIS org 3JjYDyG3oajxU6HO)', 'arcgis',
    'https://services1.arcgis.com/3JjYDyG3oajxU6HO/arcgis/rest/services/DOC_Public_Conservation_Land/FeatureServer/0', None, 'Name', 'Public conservation land (national parks, conservation areas, reserves)', via='DOC ArcGIS org')
add('NZ-DOC-marine', 'NZ', 'New Zealand', 'Department of Conservation', 'arcgis',
    'https://services1.arcgis.com/3JjYDyG3oajxU6HO/arcgis/rest/services/DOC_Marine_Reserves/FeatureServer/0', None, None, 'Marine reserves', pota_words='Marine', via='DOC ArcGIS org')
for lid, des in [(3, 'Large-area specially protected areas (national parks, protected landscape areas)'), (0, 'Small-area specially protected areas (reserves, monuments)')]:
    add(f'CZ-AOPK-{lid}', 'CZ', 'Czechia', 'AOPK ČR (Nature Conservation Agency of the Czech Republic)', 'arcgis',
        f'https://gis.nature.cz/arcgis/rest/services/UzemniOchrana/ChranUzemi/MapServer/{lid}', None, None, des, via='AOPK ArcGIS server')
add('EE-kaitseala', 'EE', 'Estonia', 'Keskkonnaagentuur (EELIS, Estonian Environment Agency)', 'wfs', 'https://gsavalik.envir.ee/geoserver/eelis/ows', 'eelis:kr_kaitseala', None,
    'Protected areas (kaitsealad)', srs=3301, via='EELIS GeoServer capabilities')
add('BR-ICMBio-UC', 'BR', 'Brazil', 'ICMBio (federal conservation units) via INDE', 'wfs', 'https://geoservicos.inde.gov.br/geoserver/ICMBio/ows', 'ICMBio:limiteucsfederais_a', None,
    'Federal conservation units', srs=4674, via='INDE national SDI GeoServer')
add('BE-WAL-natura2000', 'BE', 'Belgium (Wallonia)', 'SPW (Service public de Wallonie)', 'arcgis', 'https://geoservices.wallonie.be/arcgis/rest/services/FAUNE_FLORE/NATURA2000/MapServer/10',
    None, None, 'Natura 2000 (regional publication)', via='Géoportail de la Wallonie ArcGIS')
add('FR-IGN-parc_ou_reserve', 'FR', 'France', 'IGN (national mapping agency) BD TOPO via Géoplateforme', 'wfs', 'https://data.geopf.fr/wfs/ows', 'BDTOPO_V3:parc_ou_reserve', 'toponyme',
    'Parks and reserves in BD TOPO (national, regional parks, reserves)', srs=4326, via='Géoplateforme WFS capabilities')
add('CA-CPCAD', 'CA', 'Canada', 'ECCC CPCAD (national protected-areas layer)', 'arcgis', 'https://maps-cartes.ec.gc.ca/arcgis/rest/services/CWS_SCF/CPCAD/MapServer/0', None, 'NAME_E',
    'All protected and conserved areas (national + provincial)', via='spec (CPCAD)', note='FINDINGS: answers python oddly; honest UA only, never spoofed')
add('US-PADUS', 'US', 'United States', 'USGS PAD-US 4 (The National Map)', 'arcgis', 'https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0', None, None,
    'PAD-US fee managers', via='USGS The National Map ArcGIS')

EEA = 'https://bio.discomap.eea.europa.eu/arcgis/rest/services/ProtectedSites/{}/MapServer/{}'
add('EU-EEA-Natura2000', 'EU', 'EU / EEA (all member states)', 'European Environment Agency (EU compilation)', 'arcgis', EEA.format('Natura2000_Dyna_WM', 0), None, 'SITENAME',
    'Natura 2000 (EU compilation)', grade='approximate', eu_compilation=True, test_cc='DE', via='EEA discomap')
add('EU-EEA-CDDA', 'EU', 'EU / EEA (all member states)', 'European Environment Agency (EU compilation of national data)', 'arcgis', EEA.format('CDDA_Dyna_WM', 4), None, 'siteName',
    'Nationally designated areas (CDDA / NatDA)', grade='approximate', eu_compilation=True, test_cc='DE', via='EEA discomap')

add('ES-MITECO-ENP', 'ES', 'Spain', 'MITECO (Banco de Datos de la Naturaleza)', 'wfs', 'https://wms.mapama.gob.es/sig/Biodiversidad/ENP/wfs.aspx', None, None,
    'Espacios Naturales Protegidos', via='ANSWERS_chat10 (INSPIRE 403 on the club box)', retry_from='github')
add('PL-GDOS', 'PL', 'Poland', 'GDOŚ (General Directorate for Environmental Protection)', 'wfs', 'https://sdi.gdos.gov.pl/wfs', None, None,
    'Parki narodowe, rezerwaty, parki krajobrazowe, OChK, Natura 2000', retry_from='github', via='known national SDI')
add('IT-MASE-EUAP', 'IT', 'Italy', 'MASE Geoportale Nazionale (EUAP official list)', 'wfs', 'http://wms.pcn.minambiente.it/ogc?map=/ms_ogc/WFS/Vettoriali/EUAP.map', None, None,
    'EUAP official protected areas', retry_from='github', via='known national geoportal')

# ---- hunt-order additions (PARK_KINDS_AND_WORLD_RANK.md: NA first - MX, Central America, Caribbean - then GB DE RO AU NL SI ES IE FR DK AT CH BE ...)
add('MX-SEMARNAT-ANP', 'MX', 'Mexico', 'SEMARNAT / CONANP federal protected natural areas (geomatica.semarnat.gob.mx)', 'arcgis',
    'https://geomatica.semarnat.gob.mx/arcgis/rest/services/CAME/Areas_Naturales/MapServer/1', None, 'NOMBRE', 'Federal ANP (national parks, biosphere reserves, APFF, santuarios)',
    pota_words='Parque|Reserva|Area|Santuario|Monumento|Biosfera|National|Biosphere', via='SEMARNAT ArcGIS server (government .gob.mx)')
add('CR-SINAC-ASP', 'CR', 'Costa Rica', 'SINAC (sirefor.go.cr)', 'wfs', 'https://geos1pne.sirefor.go.cr/wfs', 'PNE:areas_silvestres_protegidas', None, 'Areas silvestres protegidas',
    pota_words='Reserve|National Park|Natural Park|Nature|Biosphere|Protected|Wildlife', via='SINAC SIREFOR geoserver', note='GetCapabilities gave HTTP 500 once on 2026-11-01; GetFeature works')
add('IE-NPWS-NP', 'IE', 'Ireland', 'National Parks & Wildlife Service (ArcGIS org Jhij7i46ouO8Cc0N)', 'arcgis',
    'https://services-eu1.arcgis.com/Jhij7i46ouO8Cc0N/arcgis/rest/services/NationalParkBoundaries/FeatureServer/0', None, 'SITE_NAME', 'National parks', pota_words='National Park', via='NPWS open data')
for i, des, w in [(0, 'SPA', 'SPA|Protection|Bird'), (1, 'pNHA', 'Heritage|NHA|Bog|Lough|Wood'), (2, 'NHA', 'Heritage|NHA|Bog'), (3, 'SAC', 'SAC|Conservation|Lough|Wood|Bog')]:
    add(f'IE-NPWS-designated-{i}', 'IE', 'Ireland', 'National Parks & Wildlife Service', 'arcgis',
        f'https://services-eu1.arcgis.com/Jhij7i46ouO8Cc0N/arcgis/rest/services/NPWSDesignatedAreas/FeatureServer/{i}', None, None, des, pota_words=w, via='NPWS open data')
add('DK-MST-fredninger', 'DK', 'Denmark', 'Miljøstyrelsen / Danmarks Miljøportal (CC0)', 'wfs', 'https://arealeditering-dist-geo.miljoeportal.dk/geoserver/wfs', 'dai:fredede_omr', None,
    'Fredede områder (protected areas, no name field: Link column points at the decision)', srs=25832, pota_words='Reserve|National Park|Natural Park|Nature|Biosphere|Protected|Wildlife', via='Danmarks Miljøportal geoserver')
add('SE-NV-skyddade', 'SE', 'Sweden', 'Naturvårdsverket (Naturvårdsregistret)', 'wfs', 'https://geodata.naturvardsverket.se/naturvardsregistret/wfs', 'Naturvardsregistret_WFS:SkyddadeOmraden',
    'NAMN', 'National parks, nature reserves, biotope areas', srs=3006, pota_words='Reserve|National Park|Natural Park|Nature|Biosphere|Protected|Wildlife', via='Naturvårdsverket WFS (the /arcgis path answers 403; /wfs answers)')
add('SE-NV-n2000', 'SE', 'Sweden', 'Naturvårdsverket', 'wfs', 'https://geodata.naturvardsverket.se/n2000/wfs', 'N2000_WFS:N2000', None, 'Natura 2000', srs=3006, pota_words='Reserve|National Park|Natural Park|Nature|Biosphere|Protected|Wildlife', via='Naturvårdsverket WFS')
add('BE-VLG-ANB-reserves', 'BE', 'Belgium (Flanders)', 'Agentschap Natuur en Bos (Mercator, Flemish government)', 'ogcapi',
    'https://mercator.vlaanderen.be/raadpleegdienstenmercatorpubliek/ogc/features/v1', 'ps:ps_uznres_anb', 'resnaam', 'Recognised + Flemish nature reserves', pota_words='Reserve|National Park|Natural Park|Nature|Biosphere|Protected|Wildlife',
    via='Mercator OGC API (vlaanderen.be)', region='VLG', pota_bbox=[2.54, 50.75, 5.9, 51.5])
add('SI-ARSO-zavarovana', 'SI', 'Slovenia', 'ARSO (Slovenian Environment Agency)', 'wfs', 'https://gis.arso.gov.si/geoserver/ows', None, None, 'Zavarovana območja (poligoni)',
    pota_words='Reserve|National Park|Natural Park|Nature|Biosphere|Protected|Wildlife', via='ARSO geoserver', status_seed='blocked', why='service answers with a "temporarily unavailable" page from our box (2026-11-01)', retry_from='github')
add('RO-MMAP-arii', 'RO', 'Romania', 'Ministry of Environment, Waters and Forests (mmediu.ro)', 'download',
    'https://www.mmediu.ro/app/webroot/uploads/files/Limite_arii_naturale_protejate.zip', None, 'text', 'Protected natural areas (shapefile, Stereo 70 / EPSG 3844)', srs=3844,
    pota_words='Reserve|National Park|Natural Park|Nature|Biosphere|Protected|Wildlife', via='mmediu.ro open data page')
add('JP-MOE-biodic', 'JP', 'Japan', 'Ministry of the Environment (biodic.go.jp)', 'wfs', 'https://gis.biodic.go.jp/webgis/', None, None, 'National / quasi-national parks',
    pota_words='Reserve|National Park|Natural Park|Nature|Biosphere|Protected|Wildlife', via='MOE biodiversity centre', status_seed='blocked', why='HTTP 500 / unreachable from our box (2026-11-01)', retry_from='github')

WAL = 'https://geoservices.wallonie.be/arcgis/rest/services/FAUNE_FLORE/'
for path, des, w in [('CONSNAT/MapServer/1', 'Réserves forestières', 'Forest|Reserve'), ('CONSNAT/MapServer/2', 'Réserves naturelles domaniales', 'Reserve|Nature'),
                     ('CONSNAT/MapServer/3', 'Réserves naturelles agréées', 'Reserve|Nature'), ('CONSNAT/MapServer/4', "Zones humides d'intérêt biologique", 'Wetland|Marsh|Nature'),
                     ('CONSNAT/MapServer/5', 'Parcs naturels', 'Natural Park|Nature Park|Parc'), ('PARCS_NATIONAUX/MapServer/3', 'Parcs nationaux (périmètres)', 'National Park')]:
    add('BE-WAL-' + path.split('/')[0] + '-' + path.split('/')[-1], 'BE', 'Belgium (Wallonia)', 'SPW (Service public de Wallonie, geoservices.wallonie.be)', 'arcgis', WAL + path, None, None, des,
        pota_words=w, via='geoservices.wallonie.be service list', region='WAL', pota_bbox=[2.84, 49.49, 6.41, 50.82])

if __name__ == '__main__':
    out = pathlib.Path(__file__).with_name('world_sources.json')
    old = {}
    if out.exists():
        for e in json.load(open(out)).get('sources', []): old[e['id']] = e
    for e in S:
        o = old.get(e['id'], {})
        if o.get('verified'): e['verified'] = o['verified']
        if o.get('name_field') and not e.get('name_field'): e['name_field'] = o['name_field']
    json.dump({'about': 'KPC world outline registry: official national / regional protected-area layers. verify.py checks each one live at POTA pins. '
               'grade approximate = EU compilation (never a full YES). Never WDPA / OSM / Google / Wikidata.', 'sources': S}, open(out, 'w'), indent=1, ensure_ascii=False)
    print(len(S), 'entries')
