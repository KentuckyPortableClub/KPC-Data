#!/usr/bin/env python3
"""Seed the registry from the club's source pack (chat 10, Nov 1 2026) instead of re-discovering what the club already approved.

  python3 registry/_seed_pack.py --pack /path/to/sources      (the unzipped 'sources' folder; default: $KPC_SOURCES)

Writes registry/pack_sources.json:
  sources : one entry per layer (url), grouped by area and park type, status 'approved' when chat 11 said YES on a park of
            that layer, 'club' when it comes from a club key / state GIS table / access / trail / camp list (approved lists,
            not graded per park);
  no_rows : chat 11's NO rows as [ref, layer, record] triples. The engine never offers these again;
  deny   : URL fragments a person ruled out (campstate deny list);
  failed_hosts : hosts that failed in outside research, with reasons (Token Required = never use);
  words  : local-language park words per country (world_agencies.json), used by the name matcher and docs finder;
  portals: open-data / GIS portals per state and country (for people and for discovery on gaps only).
Entries that are already in us_ca_sources.json / world_sources.json are NOT duplicated: Registry dedupes by normalised URL."""
import argparse, collections, json, os, pathlib, re

HERE = pathlib.Path(__file__).resolve().parent
US = dict(AL='Alabama', AK='Alaska', AZ='Arizona', AR='Arkansas', CA='California', CO='Colorado', CT='Connecticut', DE='Delaware',
          FL='Florida', GA='Georgia', HI='Hawaii', ID='Idaho', IL='Illinois', IN='Indiana', IA='Iowa', KS='Kansas', KY='Kentucky',
          LA='Louisiana', ME='Maine', MD='Maryland', MA='Massachusetts', MI='Michigan', MN='Minnesota', MS='Mississippi', MO='Missouri',
          MT='Montana', NE='Nebraska', NV='Nevada', NH='New Hampshire', NJ='New Jersey', NM='New Mexico', NY='New York',
          NC='North Carolina', ND='North Dakota', OH='Ohio', OK='Oklahoma', OR='Oregon', PA='Pennsylvania', RI='Rhode Island',
          SC='South Carolina', SD='South Dakota', TN='Tennessee', TX='Texas', UT='Utah', VT='Vermont', VA='Virginia', WA='Washington',
          WV='West Virginia', WI='Wisconsin', WY='Wyoming', DC='District of Columbia')
CA_PROV = {'AB': 'Alberta', 'BC': 'BC|British Columbia', 'MB': 'Manitoba', 'NB': 'NB|New Brunswic', 'NL': 'Newfoundland|NL',
           'NS': 'NS|Nova Scotia', 'NT': 'NT|Northwest', 'NU': 'NU|Nunavut', 'ON': 'ON|Ontario', 'PE': 'PE|Prince Edward',
           'QC': 'Qu[ée]bec|QC', 'SK': 'SK|Saskatchewan', 'YT': 'Yukon|YT'}
NATIONAL_US = re.compile(r'Forest Service|BLM|Bureau of Land|National Park Service|\bNPS\b|Fish and Wildlife Service|USFWS|Army Corps', re.I)
PTYPE = {'park': 'park', 'land': 'land', 'preserve': 'preserve', 'forest': 'forest', 'wild': 'wildlife', 'trail': 'trail'}


def norm(u):
    u = (u or '').strip().rstrip('/')
    u = re.sub(r'/query$', '', u, flags=re.I)
    return re.sub(r'^https?://', '', u).lower()


def area_of(st, area):
    if area and area.startswith('W-'): return area[2:]
    return area or st


def us_state_from(code, desc):
    if code.startswith('sg') and code[2:4].upper() in US: return 'US-' + code[2:4].upper()
    for k, v in US.items():
        if re.search(r'\b' + v + r'\b', desc): return 'US-' + k
    if NATIONAL_US.search(desc): return 'US'
    if code[:2].upper() in US: return 'US-' + code[:2].upper()
    return None


def ca_prov_from(name):
    if re.match(r'(Parks Canada|cpcad)', name, re.I): return 'CA'
    for k, rx in CA_PROV.items():
        if re.match(rf'({rx})\b', name): return 'CA-' + k
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pack', default=os.environ.get('KPC_SOURCES', '/workspace/pota/sources/sources'))
    ap.add_argument('--out', default=str(HERE / 'pack_sources.json'))
    a = ap.parse_args()
    P = pathlib.Path(a.pack)
    J = lambda p: json.load(open(P / p))                     # noqa: E731
    src = {}                                                  # norm(url) -> entry

    def put(url, area, ptype, use, name_field, agency, basis, status, **kw):
        k = (norm(url), use)
        e = src.get(k)
        if e is None:
            e = src[k] = dict(id=f'PACK-{area}-{ptype}-{len(src)}', area=area, cc=area[:2] if area else '', ptype=ptype, use=use,
                              kind='arcgis' if re.search(r'/(Map|Feature)Server/\d+', url, re.I) else kw.pop('kind', 'download'),
                              url=re.sub(r'/query/?$', '', url.strip(), flags=re.I), name_field=name_field, agency=agency, official_basis=basis,
                              grade='approximate' if re.search(r'general area|not a legal', basis or '', re.I) else 'official',
                              verified={'status': status, 'why': basis, 'date': '2026-11-01'}, areas=[area], pack=True,
                              pota_locs=[area] if area and '-' in area else None)
            e.update({k2: v for k2, v in kw.items() if v is not None})
        else:
            if area not in e['areas']: e['areas'].append(area)
            if status == 'approved': e['verified']['status'] = 'approved'
            if not e.get('name_field') and name_field: e['name_field'] = name_field
        return e

    # 1. chat 11 YES rows: the strongest evidence (a person said YES for a named park + record)
    yes = collections.defaultdict(list)
    for f in ('approved-layers-us.json', 'approved-layers-canada.json', 'approved-layers-world.json'):
        for r in J(f'approved/{f}'):
            ar = area_of(r.get('st'), r.get('area'))
            e = put(r['layer'], ar, PTYPE.get(r.get('kind'), r.get('kind') or 'park'), 'outline', r.get('name_field'), r.get('agency'),
                    f"chat 11 YES rows ({r.get('checked_by', 'chat 11')})", 'approved')
            e.setdefault('yes_refs', []).append(r['ref'])
            yes[r['ref']].append([r['layer'], r.get('record'), r.get('record_name')])
    # 2. club keys and state GIS tables (approved layer lists)
    for code, v in J('us/us-key-layers.json').items():
        url, nf, desc = (v + [None, None, None])[:3]
        ar = us_state_from(code, desc or '')
        if not ar: continue
        m = re.search(r'\((park|land|preserve|forest|wild)\b', desc or '')
        put(url, ar, PTYPE.get(m.group(1)) if m else 'land', 'outline', nf, desc, f'US key layer {code} (club approved list)', 'club')
    sg = J('us/state-gis.json')
    for st, rows in sg['states'].items():
        ar = ('US-' + st) if st in US else ('CA-' + st)
        for r in rows:
            put(r['url'], ar, PTYPE.get(r.get('kind'), r.get('kind') or 'land'), 'outline', r.get('nm'), r.get('ag'), 'state GIS table (club approved)', 'club',
                designation=r.get('ds'))
    for name, urls in J('canada/ca-key-layers.json').items():
        ar = ca_prov_from(name) or 'CA'
        for u in urls: put(u, ar, 'park', 'outline', None, name, 'Canada key layer (club approved list)', 'club')
    # 3. access / trail / camp layers
    for r in J('us/access-layers.json')['layers']:
        st = r['st']; ar = ('US-' + st) if st in US else ('CA-' + st if st in CA_PROV else st)
        nf = None if (r.get('area') or '').startswith('none') else re.sub(r'\s*\(.*', '', r.get('area') or '') or None
        put(r['url'], ar, r.get('prog'), 'parking', nf, r.get('agency'), f"access layer list: {r.get('what')} ({r.get('tested')})",
            'club' if str(r.get('tested', '')).startswith('yes') else 'lead', type_field=None if (r.get('typef') or '').startswith('none') else r['typef'].split(';')[0],
            type_values=r.get('vals'), geometry='point')
    tl = J('us/trails-layers.json')
    for k, urls in tl['layers'].items():
        ar = k if '-' in k else 'US-' + k
        for u in urls: put(u, ar, 'trail', 'trail', None, (tl.get('credits') or {}).get(u), 'trail layer list (picked by hand)', 'club', geometry='line')
    cs = J('us/campstate-layers.json')
    for st, urls in cs.get('allow', {}).items():
        for u in urls: put(u, 'US-' + st, 'campground', 'camping', None, None, 'state camps allow list (found by a person)', 'club', geometry='point')
    # 4. the NO rows, deny list, failed hosts, words, portals
    no = [[r['ref'], norm(r['layer']), str(r.get('record')), r.get('record_name')] for r in J('approved/rejected-layer-rows-chat11-NO.json')]
    failed = {}
    for line in (P / 'blocked/failed-layer-hosts.md').read_text().splitlines():
        m = re.match(r'- ([\w.-]+): (\d+) \((.*)\)$', line)
        if m: failed[m.group(1)] = {'count': int(m.group(2)), 'why': m.group(3), 'token': 'Token Required' in m.group(3),
                                    'dead': bool(re.search(r'Service not found|404|Invalid URL', m.group(3)))}
    wa = J('world/world_agencies.json')['countries']
    words = {cc: v.get('words', []) for cc, v in wa.items() if v.get('words')}
    portals = {'world': {cc: v.get('portals', []) for cc, v in wa.items()}, 'us_ca': sg.get('portals', {})}
    leads = J('approved/finder-leads-NOT-approved.json')
    # never use a layer whose host is Token Required only, or that matches the deny list
    deny = cs.get('deny', [])
    FORBID = re.compile(r'openstreetmap|overpass|geofabrik|protectedplanet|wdpa|unep-wcmc|google\.|wikidata|wikipedia|alltrails', re.I)
    excluded = [{'url': e['url'], 'area': e['area'], 'why': 'forbidden source (WDPA / OSM / ... copy), even though listed', 'yes_refs': e.get('yes_refs')}
                for e in src.values() if FORBID.search(e['url'] + ' ' + str(e.get('agency') or ''))]
    out = [e for e in src.values() if not any(d in e['url'] for d in deny) and not FORBID.search(e['url'] + ' ' + str(e.get('agency') or ''))]
    for e in out:
        h = re.sub(r'^https?://([^/]+).*', r'\1', e['url'])
        if h in failed: e['host_note'] = failed[h]['why']
    try:                                               # keep earlier live checks (verify.py writes 'live' on pack entries)
        old = {(norm(e['url']), e['use']): e.get('live') for e in json.load(open(a.out))['sources'] if e.get('live')}
        for e in out:
            if (norm(e['url']), e['use']) in old: e['live'] = old[(norm(e['url']), e['use'])]
    except (OSError, ValueError, KeyError): pass
    yes = {k: [x for x in v if not FORBID.search(x[0])] for k, v in yes.items()}
    yes = {k: v for k, v in yes.items() if v}
    NATIONAL = {'DFRP_PUBLIC': 'CA', 'CPCAD': 'CA', 'NPS_Land_Resources_Division': 'US', 'National_Heritage_Areas': 'US'}   # federal layers: the whole country
    for e in out:
        for key, nat in NATIONAL.items():
            if key in e['url'] and nat not in (e.get('areas') or []):
                e['areas'] = sorted(set((e.get('areas') or []) + [nat])); e['pota_locs'] = None
    json.dump({'about': __doc__.split('\n\n')[0], 'made': '2026-11-01', 'pack': str(P), 'sources': out, 'no_rows': no, 'yes_rows': yes,
               'deny': deny, 'excluded': excluded, 'failed_hosts': failed, 'words': words, 'portals': portals,
               'leads': [{'url': u, **v} for u, v in leads.items()]}, open(a.out, 'w'), indent=1, ensure_ascii=False)
    c = collections.Counter((e['use'], e['verified']['status']) for e in out)
    print(len(out), 'layers;', len(excluded), 'excluded (forbidden);', dict(c), '; NO rows', len(no), '; failed hosts', len(failed), '; word lists', len(words), '; leads', len(leads))
    print('areas:', collections.Counter(e['area'] for e in out).most_common(80))


if __name__ == '__main__':
    main()
