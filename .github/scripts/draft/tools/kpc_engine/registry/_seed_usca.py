"""Hand seed for registry/us_ca_sources.json: the national / federal layers and the Kentucky (+ Ontario, BC) agency layers.
discover_usca.py adds per-state / per-province layers (us_ca_discovered.json); merge_usca() joins both, verify.py tests all.
Every entry: id, area (US / CA = nationwide, US-KY ...), ptype (the club's park kinds), use (outline | trail | parking | camping),
kind, url, name_field, geometry, agency, official_basis, pota_words (POTA names used to test it), grade."""
import json, pathlib
S = []
def add(id, area, ptype, use, url, name_field, agency, basis, words=None, geometry='polygon', kind='arcgis', grade='official', **kw):
    e = dict(id=id, area=area, cc=area[:2], ptype=ptype, use=use, kind=kind, url=url, name_field=name_field, geometry=geometry, agency=agency,
             official_basis=basis, pota_words=words, grade=grade, pota_locs=[area] if '-' in area else None); e.update(kw); S.append(e)

NPS = 'https://services1.arcgis.com/fBc8EJBxQRMcHlei/arcgis/rest/services/NPS_Land_Resources_Division_Boundary_and_Tract_Data_Service/FeatureServer'
add('US-NPS-boundary', 'US', 'nps', 'outline', NPS + '/2', 'UNIT_NAME', 'National Park Service', 'NPS ArcGIS org fBc8EJBxQRMcHlei (Land Resources Division)', r'National (Park|Historic|Memorial|Monument|Battlefield|Seashore|Lakeshore|Recreation|Preserve|River|Parkway)')
add('US-NPS-tracts', 'US', 'nps', 'outline', NPS + '/1', None, 'National Park Service', 'NPS Land Resources Division tracts (land the NPS owns)', r'National (Park|Historic)')
FS = 'https://apps.fs.usda.gov/arcx/rest/services/EDW/'
add('US-USFS-ownership', 'US', 'national_forest', 'outline', FS + 'EDW_BasicOwnership_02/MapServer/0', None, 'USDA Forest Service', 'apps.fs.usda.gov Enterprise Data Warehouse (land the FS owns: Rule B1)', r'National Forest|National Grassland')
add('US-USFS-admin', 'US', 'national_forest', 'outline', FS + 'EDW_ForestSystemBoundaries_01/MapServer/0', 'FORESTNAME', 'USDA Forest Service', 'FS EDW administrative boundaries (proclaimed: approximate for B1)', r'National Forest', grade='approximate', note='proclamation line, not owned land (Rule B1)')
add('US-USFS-grassland', 'US', 'national_forest', 'outline', FS + 'EDW_NationalGrassland_01/MapServer/0', None, 'USDA Forest Service', 'FS EDW', r'Grassland')
add('US-USFS-wilderness', 'US', 'wilderness', 'outline', FS + 'EDW_Wilderness_02/MapServer/0', None, 'USDA Forest Service (all NWPS wilderness)', 'FS EDW', r'Wilderness')
add('US-USFS-wsr', 'US', 'river', 'trail', FS + 'EDW_WildScenicRiverSegments_01/MapServer/0', None, 'USDA Forest Service', 'FS EDW', r'Wild and Scenic|Scenic River|Wild & Scenic', geometry='line')
add('US-USFS-trails', 'US', 'trail', 'trail', FS + 'EDW_TrailNFSPublish_01/MapServer/0', 'TRAIL_NAME', 'USDA Forest Service', 'FS EDW', r'Trail', geometry='line')
add('US-USFS-recsites', 'US', 'national_forest', 'parking', FS + 'EDW_RecreationOpportunities_01/MapServer/0', 'RECAREANAME', 'USDA Forest Service', 'FS EDW recreation opportunities (trailheads, campgrounds, boat ramps)', r'National Forest', geometry='point', also='camping')
BLM = 'https://gis.blm.gov/arcgis/rest/services/'
add('US-BLM-sma', 'US', 'blm', 'outline', BLM + 'lands/BLM_Natl_SMA_LimitedScale/MapServer/7', None, 'Bureau of Land Management', 'gis.blm.gov national surface management (BLM land)', r'BLM|Recreation Area|Herd|Wilderness Study')
add('US-BLM-nlcs', 'US', 'blm', 'outline', BLM + 'lands/BLM_Natl_NLCS_NM_NCA_poly/MapServer/0', None, 'Bureau of Land Management', 'gis.blm.gov NLCS monuments / NCAs', r'National Monument|Conservation Area')
add('US-BLM-recs', 'US', 'blm', 'outline', BLM + 'recreation/BLM_Natl_Recs_poly/MapServer/0', None, 'Bureau of Land Management', 'gis.blm.gov recreation areas', r'Recreation Area|RMA|SRMA')
add('US-BLM-recsites', 'US', 'blm', 'parking', BLM + 'recreation/BLM_Natl_Recreation_Sites_Facilities/MapServer/0', None, 'Bureau of Land Management', 'gis.blm.gov recreation sites', r'BLM|Recreation', geometry='point', also='camping')
FWS = 'https://services.arcgis.com/QVENGdaPbd4LUkLV/arcgis/rest/services/'
add('US-FWS-approved', 'US', 'nwr', 'outline', FWS + 'FWSApproved_Authoritative/FeatureServer/0', None, 'US Fish and Wildlife Service', 'FWS ArcGIS org QVENGdaPbd4LUkLV (authoritative approved acquisition boundaries)', r'National Wildlife Refuge|NWR|Wetland Management', grade='approximate', note='approved boundary, not only owned land')
add('US-FWS-interest', 'US', 'nwr', 'outline', FWS + 'FWSInterest_Simplified_Authoritative/FeatureServer/0', None, 'US Fish and Wildlife Service', 'FWS org: land FWS owns / holds interest in (Rule B1)', r'National Wildlife Refuge|NWR|Fish Hatchery')
add('US-FWS-nwrs', 'US', 'nwr', 'outline', FWS + 'National_Wildlife_Refuge_System_Boundaries/FeatureServer/0', None, 'US Fish and Wildlife Service', 'FWS org', r'National Wildlife Refuge|NWR')
add('US-FWS-trails', 'US', 'nwr', 'trail', FWS + 'Refuge_Trails/FeatureServer/0', None, 'US Fish and Wildlife Service', 'FWS org', r'Refuge', geometry='line')
add('US-FWS-huntunits', 'US', 'nwr', 'outline', FWS + 'FWS_NWRS_HQ_PublicHuntUnits_view/FeatureServer/0', None, 'US Fish and Wildlife Service', 'FWS org (public hunt units)', r'Refuge')
add('US-PADUS-fee', 'US', 'any', 'outline', 'https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0', 'Unit_Nm', 'USGS PAD-US 4 (from the managing agencies)', 'USGS The National Map', r'.', note='every manager incl. USACE lakes, states, counties, cities')

KY = 'https://kygisserver.ky.gov/arcgis/rest/services/WGS84WM_Services/'
add('US-KY-stateparks', 'US-KY', 'state_park', 'outline', KY + 'Ky_State_Parks_Features_WGS84WM/MapServer/8', None, 'Kentucky Department of Parks', 'kygisserver.ky.gov (Commonwealth of Kentucky GIS server)', r'State (Park|Resort|Recreation|Historic)')
add('US-KY-sp-campgrounds', 'US-KY', 'state_park', 'camping', KY + 'Ky_State_Parks_Features_WGS84WM/MapServer/6', None, 'Kentucky Department of Parks', 'kygisserver.ky.gov', r'State (Park|Resort)', geometry='point')
add('US-KY-sp-trailheads', 'US-KY', 'state_park', 'parking', KY + 'Ky_State_Parks_Features_WGS84WM/MapServer/0', None, 'Kentucky Department of Parks', 'kygisserver.ky.gov', r'State (Park|Resort)', geometry='point')
add('US-KY-sp-trails', 'US-KY', 'state_park', 'trail', KY + 'Ky_State_Parks_Features_WGS84WM/MapServer/9', None, 'Kentucky Department of Parks', 'kygisserver.ky.gov', r'State (Park|Resort)', geometry='line')
add('US-KY-wma-entrances', 'US-KY', 'fish_wildlife', 'parking', KY + 'Ky_Fish_Wildlife_WGS84WM/MapServer/5', None, 'Kentucky Department of Fish & Wildlife Resources', 'kygisserver.ky.gov', r'WMA|Wildlife', geometry='point')
add('US-KY-boat-ramps', 'US-KY', 'fish_wildlife', 'parking', KY + 'Ky_Fish_Wildlife_WGS84WM/MapServer/0', None, 'Kentucky Department of Fish & Wildlife Resources', 'kygisserver.ky.gov', r'Lake|WMA', geometry='point')
add('US-KY-stateforests', 'US-KY', 'state_forest', 'outline', KY + 'Ky_StateForests_WGS84WM/MapServer/1', None, 'Kentucky Division of Forestry', 'kygisserver.ky.gov', r'State Forest')
add('US-KY-snp', 'US-KY', 'nature_preserve', 'outline', KY + 'Ky_KNP_State_Nature_Preserves_WGS84WM/MapServer/0', None, 'Office of Kentucky Nature Preserves', 'kygisserver.ky.gov', r'Nature Preserve|Natural Area')
add('US-KY-natural-areas', 'US-KY', 'nature_preserve', 'outline', KY + 'Ky_KNP_Natural_Areas_WGS84WM/MapServer/0', None, 'Office of Kentucky Nature Preserves', 'kygisserver.ky.gov', r'Natural Area|Nature Preserve')
add('US-KY-wild-rivers', 'US-KY', 'river', 'outline', KY + 'Ky_KNP_Wild_River_Corridors_WGS84WM/MapServer/0', None, 'Office of Kentucky Nature Preserves (Kentucky Wild Rivers)', 'kygisserver.ky.gov', r'River')
add('US-KY-heritage-land', 'US-KY', 'nature_preserve', 'outline', KY + 'Ky_KNP_Heritage_Land_Conservation_Fund_WGS84WM/MapServer/0', None, 'Kentucky Heritage Land Conservation Fund', 'kygisserver.ky.gov', r'WMA|Preserve|State Forest|Natural Area')
add('US-KY-trails-fed-th', 'US-KY', 'trail', 'parking', KY + 'Ky_Federal_Trailheads_WGS84WM/MapServer/0', None, 'Kentucky (federal trailheads)', 'kygisserver.ky.gov', r'Trail|National Forest', geometry='point')
add('US-KY-rec-trails', 'US-KY', 'trail', 'trail', KY + 'Ky_Recreational_Trails_WGS84WM/MapServer/0', None, 'Kentucky Office of Outdoor Recreation', 'kygisserver.ky.gov', r'Trail', geometry='line')

add('CA-CPCAD', 'CA', 'any', 'outline', 'https://maps-cartes.ec.gc.ca/arcgis/rest/services/CWS_SCF/CPCAD/MapServer/0', 'NAME_E', 'ECCC CPCAD (from every federal / provincial agency)', 'maps-cartes.ec.gc.ca (Environment and Climate Change Canada)', r'.', note='covers NWAs, MBSs, national parks, provincial parks, conservation reserves')
add('CA-PC-np-legal', 'CA', 'national_park', 'outline', 'https://proxyinternet.nrcan-rncan.gc.ca/arcgis/rest/services/CLSS-SATC/CLSS_Administrative_Boundaries/MapServer/1', None, 'Parks Canada (legal boundaries, NRCan CLSS)', 'proxyinternet.nrcan-rncan.gc.ca', r'National Park')
LIO = 'https://ws.lioservices.lrc.gov.on.ca/arcgis1071a/rest/services/LIO_OPEN_DATA/'
add('CA-ON-pp', 'CA-ON', 'provincial_park', 'outline', LIO + 'LIO_Open03/MapServer/4', None, 'Ontario Parks (MNR)', 'Land Information Ontario (ws.lioservices.lrc.gov.on.ca)', r'Provincial Park')
add('CA-ON-cr', 'CA-ON', 'conservation_reserve', 'outline', LIO + 'LIO_Open03/MapServer/2', None, 'Ontario MNR', 'Land Information Ontario', r'Conservation Reserve')
add('CA-ON-nwa', 'CA-ON', 'wildlife_area', 'outline', LIO + 'LIO_Open03/MapServer/9', None, 'ECCC (via LIO)', 'Land Information Ontario', r'Wildlife Area')
add('CA-ON-ca-admin', 'CA-ON', 'conservation_area', 'outline', LIO + 'LIO_Open03/MapServer/11', None, 'Conservation authorities (admin areas: NOT the CA land)', 'Land Information Ontario', r'Conservation Area', grade='approximate', note='admin area of the authority, not the conservation area itself')
add('CA-ON-municipal', 'CA-ON', 'local', 'outline', LIO + 'LIO_Open03/MapServer/3', None, 'Ontario municipalities (via LIO)', 'Land Information Ontario', r'Park')
add('CA-ON-otn-trails', 'CA-ON', 'trail', 'trail', LIO + 'LIO_Open04/MapServer/19', None, 'Ontario Trail Network (via LIO)', 'Land Information Ontario', r'Trail', geometry='line')
add('CA-ON-otn-access', 'CA-ON', 'trail', 'parking', LIO + 'LIO_Open04/MapServer/20', None, 'Ontario Trail Network (via LIO)', 'Land Information Ontario', r'Trail', geometry='point')
add('CA-ON-fishing-access', 'CA-ON', 'any', 'parking', LIO + 'LIO_Open07/MapServer/15', None, 'Ontario MNR', 'Land Information Ontario', r'.', geometry='point')
add('CA-BC-parks', 'CA-BC', 'provincial_park', 'outline', 'https://openmaps.gov.bc.ca/geo/pub/wfs', 'PROTECTED_LANDS_NAME', 'BC Parks', 'openmaps.gov.bc.ca (Government of British Columbia)', r'Park|Protected Area|Ecological Reserve',
    kind='wfs', layer='WHSE_TANTALIS.TA_PARK_ECORES_PA_SVW', srs=3005)

if __name__ == '__main__':
    out = pathlib.Path(__file__).with_name('us_ca_sources.json')
    old = {e['id']: e for e in json.load(open(out)).get('sources', [])} if out.exists() else {}
    disc = pathlib.Path(__file__).with_name('us_ca_discovered.json')
    D = json.load(open(disc)).get('found', []) if disc.exists() else []
    seen = {e['url'] for e in S}
    per = {}
    CAP = 6          # at most 6 discovered layers per (area, park type): one service with 200 trail layers is not 200 sources
    for d in D:
        if d['url'] in seen: continue
        k = (d.get('area'), d.get('ptype'))
        if per.get(k, 0) >= CAP: continue
        per[k] = per.get(k, 0) + 1
        seen.add(d['url'])
        d.setdefault('use', {'polygon': 'outline', 'line': 'trail', 'point': d['ptype'] if d['ptype'] in ('parking', 'camping') else 'parking'}[d['geometry']])
        S.append(d)
    for e in S:
        o = old.get(e['id'], {})
        if o.get('verified'): e['verified'] = o['verified']
        if o.get('name_field') and not e.get('name_field'): e['name_field'] = o['name_field']
    json.dump({'about': 'KPC US + Canada registry: federal / national + state / provincial agency layers, grouped by park type (ptype) and use. '
               'verify.py checks each one live at POTA pins of that area and type.', 'sources': S}, open(out, 'w'), indent=1, ensure_ascii=False)
    print(len(S), 'entries')
