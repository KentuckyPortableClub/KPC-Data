"""THE ONE ADAPTER (Engine spec PART 2): every read of a club file goes through here, so chat 10 can fix a field name or a
path in ONE place. Shapes follow ANSWERS_chat10.md (Nov 1 2026).

Roots (all read-only; nothing here ever writes a club file):
  --data   KPC-Data checkout   (env KPC_DATA)   data/us-key, data/ca-key, data/docs, data/access, data/campsites, data/campinfo,
                                                 data/parkinfo, data/hours, data/closures, data/trails, data/pota/t
  --links  KPC-Links checkout  (env KPC_LINKS)  data/world-key, data/ky-answer-key.json, kpc-ky-data.json
  --pota   a folder of POTA park JSON records (api.pota.app /park/<ref> shape) and/or location lists
           (/location/parks/<loc> or /program/parks/<CC> shape): the fallback park list when the club files are not there.
"""
import glob, json, os, pathlib, re, urllib.parse

# ------------------------------------------------------------------ paths (edit here only)
PATHS = {
    'us_key': 'data/us-key/{area}.json', 'ca_key': 'data/ca-key/{area}.json', 'ca_layers': 'data/ca-key/layers.json',
    'world_key': 'data/world-key/{cc}.json', 'ky_answer': 'data/ky-answer-key.json', 'ky_data': 'kpc-ky-data.json',
    'docs': 'data/docs/{area}.json', 'access': 'data/access/{area}.json', 'campsites': 'data/campsites/{area}.json',
    'campinfo': 'data/campinfo/{area}.json', 'parkinfo': 'data/parkinfo/{area}.json', 'parkinfo_ca': 'data/parkinfo/CA.json',
    'hours': 'data/hours/{area}.json', 'closures': 'data/closures/{area}.json', 'closure_sources': 'data/closures/sources.json',
    'trails_dir': 'data/trails', 'world_tiles': 'data/pota/t/*.json', 'state_gis': 'data/state-gis.json',
    'access_layers': 'data/access-layers.json', 'acres': 'data/acres.json',
    'atlas': '.claude/build/research/agency-atlas/{area}.md',
}
# parkinfo row columns (ANSWERS 1): 0 name, 1 website, 2 type, 3-4 access modes, 5 lat, 6 lon, 7-9 activation numbers, 10 province (CA)
PI = {'name': 0, 'web': 1, 'type': 2, 'acc1': 3, 'acc2': 4, 'lat': 5, 'lon': 6, 'prov': 10}
NOT_AGENCY = re.compile(r'^(work in progress|n/a|kpc\b|just outside the line)', re.I)
CAMP_WORDS = re.compile(r'\b(camp|campground|campsite|camping|cabin|shelter|rv)\b', re.I)
TRAIL_TYPE = re.compile(r'\btrail\b', re.I)
KINDS = ['outline', 'map', 'page', 'parking', 'camping', 'trail', 'hours', 'fees', 'closures']


def _load(p):
    try:
        with open(p, encoding='utf-8') as f: return json.load(f)
    except (OSError, ValueError): return None


class Club:
    def __init__(self, data=None, links=None, pota=None):
        self.data = pathlib.Path(data or os.environ.get('KPC_DATA') or '_no_data_')
        self.links = pathlib.Path(links or os.environ.get('KPC_LINKS') or '_no_links_')
        self.pota = pathlib.Path(pota) if pota else None
        self._c = {}
        self.missing_files = set()

    def _d(self, key, **kw): return self.data / PATHS[key].format(**kw)
    def _l(self, key, **kw): return self.links / PATHS[key].format(**kw)

    def read(self, path):
        path = pathlib.Path(path); k = str(path)
        if k not in self._c:
            self._c[k] = _load(path)
            if self._c[k] is None: self.missing_files.add(k)
        return self._c[k]

    # ---------------------------------------------------------- park lists
    def parks(self, area):
        """{ref: Park dict} for an area: 'US-KY', 'CA-ON', or a world country code 'CH'.
        Park = {ref, n, t, lat, lon, web, area, cc, st, acc, src}."""
        out = {}
        if area == 'US-KY':
            ky = self.read(self._l('ky_data'))
            for p in (ky or {}).get('parks', []):
                out[p['c']] = {'ref': p['c'], 'n': p.get('n'), 't': p.get('t', ''), 'lat': p.get('la'), 'lon': p.get('lo'), 'web': p.get('w', ''),
                               'area': area, 'cc': 'US', 'st': 'KY', 'acc': '', 'src': 'kpc-ky-data.json'}
        elif area.startswith('US-'):
            pi = self.read(self._d('parkinfo', area=area))
            for ref, r in (pi or {}).get('parks', {}).items(): out[ref] = self._pi_row(ref, r, area)
        elif area.startswith('CA-'):
            pi = self.read(self._d('parkinfo_ca'))
            for ref, r in (pi or {}).get('parks', {}).items():
                if len(r) > PI['prov'] and f"CA-{r[PI['prov']]}" == area: out[ref] = self._pi_row(ref, r, area)
        else:
            for f in glob.glob(str(self.data / PATHS['world_tiles'])):
                for row in _load(f) or []:
                    if str(row[0]).split('-')[0] == area:
                        out[row[0]] = {'ref': row[0], 'n': row[1], 't': '', 'lat': row[2], 'lon': row[3], 'web': '', 'area': area, 'cc': area, 'st': '', 'acc': '', 'src': 'pota tiles'}
        if not out and self.pota: out = self._pota_parks(area)
        return out

    def all_areas(self):
        """Every area the club files (or the POTA folder) know about, in the club order (kpc_order): Kentucky first, then the
        rest of the US + Canada, then the rest of North America, then world stages W1-W10, then everyone else. Used when
        --areas / AREAS is left blank: a blank list means EVERY area, never 'do nothing'."""
        found = set()
        if self.read(self._l('ky_data')) is not None: found.add('US-KY')
        for f in glob.glob(str(self.data / 'data/parkinfo/US-*.json')): found.add(pathlib.Path(f).stem)
        ca = self.read(self._d('parkinfo_ca')) if (self.data / PATHS['parkinfo_ca']).exists() else None
        for r in ((ca or {}).get('parks') or {}).values():
            if len(r) > PI['prov'] and r[PI['prov']]: found.add(f"CA-{r[PI['prov']]}")
        for f in glob.glob(str(self.data / PATHS['world_tiles'])):
            for row in _load(f) or []:
                try: cc = str(row[0]).split('-')[0]
                except (IndexError, TypeError): continue
                if cc and cc not in ('US', 'CA'): found.add(cc)
        if self.pota and self.pota.exists():
            for f in self.pota.glob('**/*.json'):
                j = _load(f)
                for p in (j if isinstance(j, list) else [j] if isinstance(j, dict) else []):
                    if not isinstance(p, dict) or not p.get('reference'): continue
                    cc = p['reference'].split('-')[0]
                    locs = [x.strip() for x in (p.get('locationDesc') or '').split(',') if x.strip()]
                    if cc in ('US', 'CA'): found.update(x for x in locs if x.startswith(cc + '-'))
                    else: found.add(cc)
        return order_areas(found)

    def _pi_row(self, ref, r, area):
        g = lambda i: r[i] if len(r) > i else None
        return {'ref': ref, 'n': g(PI['name']), 'web': g(PI['web']) or '', 't': g(PI['type']) or '', 'lat': g(PI['lat']), 'lon': g(PI['lon']),
                'acc': ','.join(x for x in (g(PI['acc1']), g(PI['acc2'])) if x), 'area': area, 'cc': area[:2], 'st': area[3:], 'src': 'parkinfo'}

    def _pota_parks(self, area):
        """Fallback: the POTA JSON folder (one park per file, or location / program lists)."""
        out = {}
        if not self.pota or not self.pota.exists(): return out
        cache = self._c.get('_pota_all')
        if cache is None:
            cache = {}
            for f in self.pota.glob('**/*.json'):
                j = _load(f)
                rows = j if isinstance(j, list) else [j] if isinstance(j, dict) and j.get('reference') else []
                for p in rows:
                    if not isinstance(p, dict) or not p.get('reference'): continue
                    cur = cache.setdefault(p['reference'], {})
                    cur.update({k: v for k, v in p.items() if v not in (None, '')})
            self._c['_pota_all'] = cache
        for ref, p in cache.items():
            locs = (p.get('locationDesc') or '').split(',')
            cc = ref.split('-')[0]
            hit = area in locs if '-' in area else cc == area
            if not hit: continue
            out[ref] = {'ref': ref, 'n': p.get('name'), 't': p.get('parktypeDesc', ''), 'lat': p.get('latitude'), 'lon': p.get('longitude'),
                        'web': p.get('website') or p.get('parkURLs') or '', 'area': area, 'cc': cc, 'st': locs[0][3:] if '-' in locs[0] else '',
                        'acc': ','.join(x for x in (p.get('accessMethods'), p.get('activationMethods')) if x), 'agency': p.get('agencies') or '',
                        'locs': locs, 'src': 'pota json'}
        return out

    # ---------------------------------------------------------- what the club already has
    def key_row(self, area, ref):
        if area.startswith('US-'): k = self.read(self._d('us_key', area=area))
        elif area.startswith('CA-'): k = self.read(self._d('ca_key', area=area))
        else: k = self.read(self._l('world_key', cc=area))
        return ((k or {}).get('parks') or {}).get(ref)

    def outline_status(self, area, ref):
        """'official' | 'approx' | 'pin' (missing). World key: a row with m and no g = official national layer."""
        if area == 'US-KY':
            ak = self.read(self._l('ky_answer'))
            row = ((ak or {}).get('parks') or {}).get(ref) if isinstance((ak or {}).get('parks'), dict) else \
                next((p for p in (ak or {}).get('parks', []) if p.get('c') == ref or p.get('ref') == ref), None)
            if row and row.get('tracts'): return 'official'
        r = self.key_row(area, ref)
        if not r: return 'pin'
        if area.startswith(('US-', 'CA-')):
            return {'official': 'official', 'approx': 'approx', 'approximate': 'approx'}.get(r.get('g'), 'pin')
        if r.get('g'): return 'approx' if str(r['g']).startswith('approx') else str(r['g'])
        return 'official' if r.get('m') else 'pin'

    def docs_row(self, area, ref): return (((self.read(self._d('docs', area=area)) or {}).get('parks')) or {}).get(ref) or {}

    def has_map(self, area, ref): return ((self.docs_row(area, ref).get('map') or {}).get('status') == 'ok')

    def has_page(self, area, ref): return bool(self.docs_row(area, ref).get('page'))

    def access_points(self, area, ref):
        """[(lat, lon, label, agency, how)] official points only (KPC-made labels dropped)."""
        out = []
        if area == 'US-KY':
            ky = self.read(self._l('ky_data'))
            for p in (ky or {}).get('parks', []):
                if p.get('c') != ref: continue
                for a in p.get('ap') or []:
                    lab = str(a[2]) if len(a) > 2 else ''
                    if lab.upper().startswith('KPC'): continue
                    out.append((a[0], a[1], lab, lab.split()[0] if lab else '', 'ky'))
            return out
        acc = self.read(self._d('access', area=area))
        for r in ((acc or {}).get('parks') or {}).get(ref, []):
            ag = agency_of_label(r[2])
            if ag is None: continue
            out.append((r[0], r[1], r[2], ag, r[3] if len(r) > 3 else ''))
        return out

    def campgrounds(self, area, ref):
        cs = self.read(self._d('campsites', area=area)) or {}
        return (cs.get('inside') or {}).get(ref, [])

    def has_trail_line(self, area, ref):
        d = self.data / PATHS['trails_dir']
        return any(d.glob(f'**/{ref}*')) if d.exists() else False

    def hours_row(self, area, ref): return (((self.read(self._d('hours', area=area)) or {}).get('parks')) or {}).get(ref) or {}

    def closures_checked(self, area):
        """{source id: last checked date} from data/closures/<area>.json (assumed shape: {'sources': {id: {'checked': date}}})."""
        c = self.read(self._d('closures', area=area)) or {}
        s = c.get('sources') or {}
        return {k: (v or {}).get('checked') for k, v in s.items()} if isinstance(s, dict) else {}

    # ---------------------------------------------------------- the agency (the GROUP every plug-in works by)
    def agency(self, park):
        r = self.key_row(park['area'], park['ref']) or {}
        mgr = r.get('mgr') or r.get('manager')
        if mgr: return mgr, 'key manager'
        if park.get('agency'): return park['agency'].split(',')[0].strip(), 'POTA agency'
        host = urllib.parse.urlparse(park.get('web') or '').netloc.lower()
        if host:
            host = re.sub(r'^(www\d?|m)\.', '', host)
            return host, 'web domain'
        return (park.get('t') or 'unknown').strip() or 'unknown', 'type word'


def agency_of_label(label):
    """data/access rows: the agency = the label's last brackets, text before ';'. None when not an agency."""
    m = re.findall(r'\(([^()]*)\)', label or '')
    if not m: return ''
    a = m[-1].split(';')[0].strip()
    return None if NOT_AGENCY.match(a) else a


def order_areas(areas):
    """Sort area codes in the club order (kpc_order.rank_cc); Kentucky first, then alphabetical inside each rank."""
    from core import ref
    rank_cc = ref.order().rank_cc
    return sorted(set(areas), key=lambda a: (rank_cc(a.split('-')[0]), a != 'US-KY', a))
