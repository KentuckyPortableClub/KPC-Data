#!/usr/bin/env python3
"""Discovery for the US + Canada registry (registry/us_ca_sources.json), one search per state/province per PARK TYPE.

Route (Finder3 L3, run once offline to build the registry, then re-run monthly):
  ArcGIS Online search (sharing/rest, robots-exempt) "<type words> <state name>" -> keep Feature/Map services whose
  OWNER ORGANISATION is a government body (org name read from sharing/rest/portals/<orgId>), or whose owner account is a
  government e-mail (.gov / .gc.ca / gov.<prov>.ca) -> keep polygon (outline), line (trail/river) or point (parking,
  camping) layers -> verify.py checks them live at POTA pins of that state and type.
Orgs that are not plainly government (universities, NGOs, companies, Esri, land trusts) are dropped; land-trust layers
are only kept when the org is a government body (user rule 'land trusts only if government-owned/official').

  python3 registry/discover_usca.py --cache .cache [--areas US-KY,US-TN,CA-ON] [--types state_park,fish_wildlife]"""
import argparse, json, pathlib, re, sys, urllib.parse

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from core.polite import Polite          # noqa: E402

STATES = dict(AL='Alabama', AK='Alaska', AZ='Arizona', AR='Arkansas', CA='California', CO='Colorado', CT='Connecticut', DE='Delaware',
              FL='Florida', GA='Georgia', HI='Hawaii', ID='Idaho', IL='Illinois', IN='Indiana', IA='Iowa', KS='Kansas', KY='Kentucky',
              LA='Louisiana', ME='Maine', MD='Maryland', MA='Massachusetts', MI='Michigan', MN='Minnesota', MS='Mississippi', MO='Missouri',
              MT='Montana', NE='Nebraska', NV='Nevada', NH='New Hampshire', NJ='New Jersey', NM='New Mexico', NY='New York',
              NC='North Carolina', ND='North Dakota', OH='Ohio', OK='Oklahoma', OR='Oregon', PA='Pennsylvania', RI='Rhode Island',
              SC='South Carolina', SD='South Dakota', TN='Tennessee', TX='Texas', UT='Utah', VT='Vermont', VA='Virginia', WA='Washington',
              WV='West Virginia', WI='Wisconsin', WY='Wyoming')
PROVS = dict(AB='Alberta', BC='British Columbia', MB='Manitoba', NB='New Brunswick', NL='Newfoundland', NS='Nova Scotia', NT='Northwest Territories',
             NU='Nunavut', ON='Ontario', PE='Prince Edward Island', QC='Quebec', SK='Saskatchewan', YT='Yukon')
KY_NEIGHBOURS = ['KY', 'TN', 'OH', 'IN', 'IL', 'MO', 'VA', 'WV']

# park types the club activates (user, Nov 1): search words, wanted geometry, and the POTA name words used to test them
US_TYPES = {
    'state_park':      (['"state park" boundary', 'state parks'], 'polygon', r'State Park|State Recreation|State Resort'),
    'fish_wildlife':   (['"wildlife management area"', '"public hunting" areas', '"fish and wildlife area"'], 'polygon', r'Wildlife|WMA|Game|Hunting|Fish'),
    'nature_preserve': (['"nature preserve"', '"natural area" state'], 'polygon', r'Preserve|Natural Area'),
    'state_forest':    (['"state forest" boundary'], 'polygon', r'State Forest'),
    'historic':        (['"state historic site"'], 'polygon', r'Historic'),
    'trail':           (['"state trail"', 'state trails', '"rail trail"', 'trails state parks'], 'line', r'Trail|Trace|Greenway|Rail'),
    'river':           (['"water trail"', '"scenic river"'], 'line', r'River|Water Trail'),
    'parking':         (['"boat ramp" access', 'trailhead', 'parking wildlife area'], 'point', None),
    'camping':         (['campground state park'], 'point', None),
}
CA_TYPES = {
    'provincial_park':      (['"provincial park" boundary', 'provincial parks'], 'polygon', r'Provincial Park|Territorial Park'),
    'conservation_reserve': (['"conservation reserve"', '"protected area"'], 'polygon', r'Conservation Reserve|Protected Area|Conservation Area'),
    'ecological_reserve':   (['"ecological reserve"'], 'polygon', r'Ecological Reserve'),
    'wildlife_area':        (['"wildlife management area"', '"wildlife area"'], 'polygon', r'Wildlife'),
    'trail':                (['trails provincial', '"provincial trail"', '"rail trail"'], 'line', r'Trail|Sentier|Greenway|Rail'),
    'parking':              (['"boat launch"', 'trailhead'], 'point', None),
    'camping':              (['campground provincial park'], 'point', None),
}
GOV = re.compile(r'\b(state of|commonwealth|department|dept|division|commission|agency|bureau|office|ministry|minist[eè]re|government|gouvernement|'
                 r'county|city of|authority|dnr|dcr|dep|deq|fish (and|&) (wildlife|game)|wildlife resources|parks|forestry|natural resources|'
                 r'geographic information|gis|geospatial|nrcan|environment|canada|gov)\b', re.I)
NOT_GOV = re.compile(r'universit|college|school|inc\b|llc|ltd|corp|company|esri|consult|club|conservancy|land trust|foundation|society|'
                     r'association|alliance|friends of|audubon|sierra|trout unlimited|ducks unlimited|nature conservancy', re.I)
# world mode (Finder3 L3 in the local language): hunt order = NA first, then the club's world-hunt list (Nov 1), then W1-W10 rest
WORLD_WORDS = {
    'MX': ['"área natural protegida"', 'parque estatal', 'parque nacional México'], 'CR': ['"área silvestre protegida"', 'parque nacional Costa Rica'],
    'BB': ['Barbados park', 'Barbados national park'], 'CU': ['Cuba área protegida'], 'LC': ['Saint Lucia forest reserve', 'Saint Lucia protected area'],
    'DO': ['República Dominicana área protegida'], 'PR': ['Puerto Rico reserva natural', 'Puerto Rico bosque estatal'], 'GT': ['Guatemala área protegida'],
    'PA': ['Panamá área protegida'], 'BZ': ['Belize protected area'], 'JM': ['Jamaica protected area'], 'TT': ['Trinidad Tobago protected area'],
    'GB': ['"country park"', '"local nature reserve"', 'nature reserve council'], 'DE': ['Naturschutzgebiet', 'Landschaftsschutzgebiet', 'Naturpark'],
    'RO': ['arii naturale protejate', 'rezervatie naturala'], 'AU': ['"national park" boundary', '"conservation park"', '"state forest" Australia'],
    'NL': ['natuurgebied', 'Natuurnetwerk Nederland', 'nationaal park'], 'SI': ['zavarovana območja', 'krajinski park'],
    'ES': ['espacios naturales protegidos', 'parque natural', 'red natura 2000 comunidad'], 'IE': ['national park Ireland', 'nature reserve Ireland'],
    'FR': ['réserve naturelle', 'parc naturel régional', 'espace naturel sensible'], 'DK': ['fredede områder', 'naturpark Danmark'],
    'AT': ['Naturschutzgebiet Österreich', 'Schutzgebiete Land'], 'CH': ['Naturschutzgebiet Kanton', 'Schutzgebiet Kanton'],
    'BE': ['natuurreservaat', 'réserve naturelle Wallonie'], 'JP': ['自然公園', '国立公園', '県立自然公園', '鳥獣保護区'],
    'PL': ['rezerwat przyrody', 'park krajobrazowy', 'park narodowy'], 'IT': ['aree protette', 'parco regionale', 'riserva naturale'],
    'NO': ['verneområder', 'naturreservat'], 'KR': ['국립공원', '도립공원', '군립공원'], 'NZ': ['regional park', 'reserve council New Zealand'],
    'TH': ['อุทยานแห่งชาติ', 'national park Thailand'], 'BR': ['unidades de conservação', 'parque estadual'], 'TR': ['milli park', 'tabiat parkı'],
    'AR': ['área protegida provincial', 'parque provincial'], 'GR': ['προστατευόμενες περιοχές', 'Natura 2000 Ελλάδα'], 'PH': ['protected area Philippines'],
    'FI': ['luonnonsuojelualue', 'retkeilyalue'], 'SE': ['naturreservat', 'nationalpark Sverige'], 'CZ': ['chráněná území', 'přírodní rezervace'],
    'SK': ['chránené územia'], 'HR': ['zaštićena područja'], 'HU': ['védett terület', 'nemzeti park'], 'PT': ['áreas protegidas', 'parque natural'],
    'ZA': ['nature reserve South Africa', 'provincial nature reserve'], 'CL': ['áreas protegidas Chile', 'parque nacional Chile'],
}
WORLD_HUNT = ['MX', 'CR', 'BB', 'CU', 'LC', 'DO', 'PR', 'GT', 'PA', 'BZ', 'JM', 'TT',
              'GB', 'DE', 'RO', 'AU', 'NL', 'SI', 'ES', 'IE', 'FR', 'DK', 'AT', 'CH', 'BE', 'JP', 'PL', 'IT', 'NO',
              'KR', 'NZ', 'TH', 'BR', 'TR', 'AR', 'GR', 'PH', 'FI', 'SE', 'CZ', 'SK', 'HR', 'HU', 'PT', 'ZA', 'CL']
GOV_WORLD = re.compile(r'県|府|都|道庁|市|町|村|省|庁|政府|군|시|도청|공단|gob|gouv|gov|regierung|landes|ministeri|bundesamt|kommun|provinc|gemeente|'
                       r'regi[oó]n|junta|generalitat|regione|comune|wojew|urz[aą]d|council|government|minist|agenc|authority|direcci|secretar|'
                       r'instituto|departament|kanton|canton|amt\b|stadt|kreis|landkreis|county|municipal|ayuntamiento|prefecture|parks victoria|'
                       r'national parks|nationalpark|natuur|natur|metsähallitus|naturvård|styrelsen|lg\.jp', re.I)
GOV_MAIL = re.compile(r'@[\w.-]*(\.gov|\.gc\.ca|\.gov\.[a-z]{2}\.ca|gov\.(ab|bc|mb|nb|nl|ns|nt|nu|on|pe|sk|yk|yt)\.ca|\.gouv\.qc\.ca|\.mil)$', re.I)


def org_info(P, oid, cache):
    if oid in cache: return cache[oid]
    r, j = P.get_json(f'https://www.arcgis.com/sharing/rest/portals/{oid}?f=json', kind='org', ttl_days=60)
    cache[oid] = {'name': (j or {}).get('name') or '', 'urlKey': (j or {}).get('urlKey') or '',
                  'description': re.sub(r'<[^>]+>', ' ', (j or {}).get('description') or '')[:300]}
    return cache[oid]


def official(P, item, cache, region_name):
    """-> (basis or None, why_not)."""
    owner = item.get('owner') or ''
    if GOV_MAIL.search(owner): return f'owner account is a government e-mail ({owner}); not in a verified org: a person should confirm', None
    oid = item.get('orgId')
    if not oid and owner:
        r, j = P.get_json(f'https://www.arcgis.com/sharing/rest/community/users/{urllib.parse.quote(owner)}?f=json', kind='owner', ttl_days=60)
        oid = (j or {}).get('orgId')
        if (j or {}).get('email') and GOV_MAIL.search(j['email']):
            return f'owner account e-mail is a government address; a person should confirm', None
    if not oid: return None, 'no organisation (personal / public account)'
    item['orgId'] = oid
    o = org_info(P, oid, cache)
    nm = o['name']
    if NOT_GOV.search(nm): return None, f'org "{nm}" is not a government body'
    if region_name == '*world*' and GOV_WORLD.search(nm + ' ' + o['urlKey']):
        return f'ArcGIS org "{nm}" ({o["urlKey"]}.maps.arcgis.com, orgId {oid})', None
    if GOV.search(nm) or GOV.search(o['urlKey']) or re.search(r'gov|\.mil|gc\.ca|gouv', (nm + ' ' + o['urlKey']).lower()) or GOV.search(o.get('description', '')):
        return f'ArcGIS org "{nm}" ({o["urlKey"]}.maps.arcgis.com, orgId {oid})', None
    return None, f'org "{nm}" not plainly government'


def layers(P, url, want):
    r, j = P.get_json(url.rstrip('/') + '/layers?f=json', kind='layers', ttl_days=30)
    out = []
    gt = {'polygon': 'esriGeometryPolygon', 'line': 'esriGeometryPolyline', 'point': 'esriGeometryPoint'}[want]
    for L in (j or {}).get('layers', []):
        if L.get('geometryType') != gt: continue
        tf = [f['name'] for f in L.get('fields') or [] if f.get('type') == 'esriFieldTypeString']
        nf = next((f for f in tf if re.search(r'^(name|.*_name|name_.*|.*name|nom.*|unit_?nm|label|site|area_?name|propname|title)$', f, re.I)), None)
        out.append({'url': f'{url.rstrip("/")}/{L["id"]}', 'layer_name': L.get('name'), 'name_field': nf, 'geometry': want, 'text_fields': tf[:25]})
    return out


def search(P, q, n=30):
    u = 'https://www.arcgis.com/sharing/rest/search?' + urllib.parse.urlencode(
        {'q': f'{q} (type:"Feature Service" OR type:"Map Service")', 'num': n, 'f': 'json', 'sortField': 'numviews', 'sortOrder': 'desc'})
    r, j = P.get_json(u, kind='search', ttl_days=30)
    return (j or {}).get('results', []) if not r.blocked else []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cache', default=str(HERE.parent / '.cache')); ap.add_argument('--areas', default='')
    ap.add_argument('--types', default=''); ap.add_argument('--out', default=str(HERE / 'us_ca_discovered.json'))
    ap.add_argument('--world', default='', help='comma list of CC, or "hunt" for the full world-hunt order')
    a = ap.parse_args()
    if a.world: return world(a)
    P = Polite('KPC park engine: US/CA registry discovery', cache_dir=a.cache)
    want_areas = [x for x in a.areas.split(',') if x]
    areas = want_areas or ([f'US-{s}' for s in KY_NEIGHBOURS] + [f'CA-{p}' for p in PROVS] + [f'US-{s}' for s in STATES if s not in KY_NEIGHBOURS])
    orgs, found, dropped, seen = {}, [], [], set()
    for area in areas:
        cc, code = area.split('-')
        region = STATES.get(code) if cc == 'US' else PROVS.get(code)
        types = US_TYPES if cc == 'US' else CA_TYPES
        for ptype, (qs, geom, words) in types.items():
            if a.types and ptype not in a.types.split(','): continue
            for q in qs:
                for it in search(P, f'{q} {region}'):
                    url = (it.get('url') or '').split('?')[0]
                    if not re.search(r'/(MapServer|FeatureServer)$', url): continue
                    text = f"{it.get('title','')} {it.get('snippet','') or ''} {' '.join(it.get('tags') or [])}"
                    if region.lower() not in text.lower() and code.lower() not in [t.lower() for t in it.get('tags') or []]: continue
                    key = (url, ptype)
                    if key in seen: continue
                    seen.add(key)
                    basis, why = official(P, it, orgs, region)
                    if not basis:
                        dropped.append({'area': area, 'ptype': ptype, 'title': it.get('title'), 'url': url, 'why': why}); continue
                    for L in layers(P, url, geom):
                        found.append({'id': f'{area}-{ptype}-{re.sub(r"[^A-Za-z0-9]+", "_", it.get("title",""))[:40]}-{L["url"].rsplit("/",1)[1]}',
                                      'area': area, 'cc': cc, 'region': code, 'ptype': ptype, 'kind': 'arcgis', 'url': L['url'],
                                      'layer_name': L['layer_name'], 'name_field': L['name_field'], 'geometry': geom, 'item_title': it.get('title'),
                                      'item_id': it.get('id'), 'agency': orgs.get(it.get('orgId'), {}).get('name') or it.get('owner'),
                                      'official_basis': basis, 'grade': 'official', 'pota_words': words, 'pota_locs': [area],
                                      'discovered_via': f'ArcGIS Online search "{q} {region}"'})
            print(area, ptype, sum(1 for f in found if f['area'] == area and f['ptype'] == ptype), flush=True)
        json.dump({'found': found, 'dropped': dropped, 'orgs': orgs}, open(a.out, 'w'), indent=1, ensure_ascii=False)
    P.write_blocked(HERE)


def world(a):
    P = Polite('KPC park engine: world registry discovery', cache_dir=a.cache)
    ccs = WORLD_HUNT if a.world == 'hunt' else a.world.split(',')
    out = pathlib.Path(a.out if a.out != str(HERE / 'us_ca_discovered.json') else HERE / 'world_discovered.json')
    orgs, found, dropped, seen = {}, [], [], set()
    for cc in ccs:
        for q in WORLD_WORDS.get(cc, []):
            for it in search(P, q):
                url = (it.get('url') or '').split('?')[0]
                if not re.search(r'/(MapServer|FeatureServer)$', url) or url in seen: continue
                seen.add(url)
                basis, why = official(P, it, orgs, '*world*')
                if not basis: dropped.append({'cc': cc, 'title': it.get('title'), 'url': url, 'why': why}); continue
                for L in layers(P, url, 'polygon'):
                    found.append({'id': f'{cc}-L3-{re.sub(r"[^0-9A-Za-z]+", "_", it.get("id",""))[:12]}-{L["url"].rsplit("/",1)[1]}', 'cc': cc,
                                  'country': cc, 'kind': 'arcgis', 'url': L['url'], 'layer_name': L['layer_name'], 'name_field': L['name_field'],
                                  'item_title': it.get('title'), 'agency': orgs.get(it.get('orgId'), {}).get('name') or it.get('owner'),
                                  'official_basis': basis, 'grade': 'official', 'pota_words': None, 'discovered_via': f'ArcGIS Online search "{q}" (L3)'})
        print(cc, sum(1 for f in found if f['cc'] == cc), flush=True)
        json.dump({'found': found, 'dropped': dropped, 'orgs': orgs}, open(out, 'w'), indent=1, ensure_ascii=False)
    P.write_blocked(HERE)


if __name__ == '__main__':
    main()
