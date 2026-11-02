"""Agency grouping (PART 3.3). Gap rows are grouped by AGENCY, biggest first (method §2: one agency-wide page often covers
hundreds of parks). agencies.json keeps per agency: server roots, folders, portal search address, page pattern, agency-wide
pages, domains; each entry is re-read after 30 days. Seeded from the Agency Atlas (KPC-Links .claude/build/research/
agency-atlas/<area>.md) when it is there, and from the registries (world_sources.json, us_ca_sources.json)."""
import datetime as dt, json, pathlib, re, urllib.parse

URL = re.compile(r'https?://[^\s)>\]"\'`]+')
REREAD_DAYS = 30

# official page domains per agency (used by the docs plug-in; a page must be on one of these to count)
AGENCY_DOMAINS = {
    'National Park Service': ['nps.gov'], 'USDA Forest Service': ['fs.usda.gov'], 'US Fish and Wildlife Service': ['fws.gov'],
    'Bureau of Land Management': ['blm.gov'], 'US Army Corps of Engineers': ['usace.army.mil', 'recreation.gov'],
    'Tennessee Valley Authority': ['tva.com', 'tva.gov'], 'Parks Canada': ['parks.canada.ca', 'pc.gc.ca'],
    'Kentucky Department of Parks': ['parks.ky.gov'], 'Kentucky Department of Fish & Wildlife Resources': ['fw.ky.gov'],
    'Kentucky Division of Forestry': ['forestry.ky.gov'], 'Office of Kentucky Nature Preserves': ['eec.ky.gov', 'naturepreserves.ky.gov'],
    'Ontario Parks': ['ontarioparks.ca', 'ontario.ca'], 'BC Parks': ['bcparks.ca', 'gov.bc.ca'],
    'Tennessee State Parks': ['tnstateparks.com', 'tn.gov'],
}


def _pack_domains():
    """Agency web domains from the club pack: state park / wildlife pages (us/campstate-sources.json) and the world agency
    portals (world_agencies.json), per area. Read from registry/pack_sources.json + the pack folder when present."""
    import json, os, pathlib
    out = {}
    pk = pathlib.Path(os.environ.get('KPC_SOURCES', '/workspace/pota/sources/sources'))
    host = lambda u: re.sub(r'^https?://(www\.)?([^/:]+).*', r'\2', u or '').lower()   # noqa: E731
    bad = re.compile(r'protectedplanet|wdpa|openstreetmap|google|wikipedia|wikidata|alltrails|arcgis\.com$', re.I)
    try:
        for cc, v in json.load(open(pathlib.Path(__file__).resolve().parent.parent / 'registry' / 'pack_sources.json'))['portals']['world'].items():
            out.setdefault(cc, []).extend(h for h in map(host, v) if h and not bad.search(h))
    except (OSError, ValueError, KeyError): pass
    try:
        for st, v in json.load(open(pk / 'us' / 'campstate-sources.json'))['states'].items():
            out.setdefault('US-' + st, []).extend(h for h in map(host, [v.get('parks'), v.get('wildlife')]) if h and not bad.search(h))
    except (OSError, ValueError, KeyError): pass
    return {k: list(dict.fromkeys(v)) for k, v in out.items()}


PACK_DOMAINS = _pack_domains()


def official_domain(host):
    """A government / agency web domain (the page finder only keeps these)."""
    h = (host or '').lower()
    return bool(re.search(r'(\.gov|\.mil|\.gc\.ca|\.gov\.[a-z]{2}|\.gouv\.[a-z]{2}|\.gob\.[a-z]{2}|\.go\.[a-z]{2}|\.govt\.nz|\.admin\.ch|'
                          r'\.ky\.gov|parks\.canada\.ca|ontarioparks\.ca|bcparks\.ca|sepaq\.com|albertaparks\.ca|'
                          r'\.lg\.jp|\.bund\.de|\.europa\.eu|naturalengland\.org\.uk|nature\.scot|naturalresources\.wales|'
                          r'npws\.ie|\.gv\.at|\.vlaanderen\.be|\.wallonie\.be|naturvardsverket\.se|lansstyrelsen\.se|naturstyrelsen\.dk|mst\.dk|staatsbosbeheer\.nl|'
                          r'natuurenbos\.be|nationalparks\.fi|miljodirektoratet\.no|bfn\.de|ofb\.gouv\.fr|nationalparksaustria\.at|sepaq\.com|novascotia\.ca|'
                          r'gov\.uk|gov\.si|gov\.bb|govt\.lc|gob\.mx|go\.cr|cu\.gob|snap\.cu)$', h)) or h.endswith('.gov') or \
        any(h == d or h.endswith('.' + d) for ds in list(AGENCY_DOMAINS.values()) + list(PACK_DOMAINS.values()) for d in ds)


class AgencyBook:
    def __init__(self, out_dir, registries=(), atlas_dir=None):
        self.p = pathlib.Path(out_dir) / 'agencies.json'
        self.d = json.load(open(self.p)) if self.p.exists() else {}
        for reg in registries: self.seed_registry(reg)
        if atlas_dir: self.seed_atlas(atlas_dir)

    def entry(self, agency):
        e = self.d.setdefault(agency, {'roots': [], 'folders': [], 'portal': None, 'page_pattern': None, 'wide_pages': [], 'domains': [],
                                        'layers': [], 'read': None})
        for k, ds in AGENCY_DOMAINS.items():
            if k.lower() == agency.lower():
                for x in ds:
                    if x not in e['domains']: e['domains'].append(x)
        return e

    def seed_registry(self, path):
        try: reg = json.load(open(path))
        except (OSError, ValueError): return
        for s in reg.get('sources', []):
            ag = s.get('agency') or 'unknown'
            e = self.entry(ag)
            u = s.get('url') or ''
            m = re.match(r'(https?://[^/]+/[^?]*?/rest/services)/', u)
            root = m.group(1) if m else urllib.parse.urlsplit(u)._replace(path='', query='').geturl()
            if root and root not in e['roots']: e['roots'].append(root)
            if s.get('id') not in e['layers']: e['layers'].append(s.get('id'))

    def seed_atlas(self, atlas_dir):
        for f in pathlib.Path(atlas_dir).glob('*.md'):
            area = f.stem
            text = f.read_text(encoding='utf-8', errors='replace')
            cur = None
            for ln in text.splitlines():
                h = re.match(r'#+\s+(.*)', ln)
                if h: cur = h.group(1).strip(); continue
                for u in URL.findall(ln):
                    e = self.entry(cur or f'atlas {area}')
                    e.setdefault('areas', [])
                    if area not in e['areas']: e['areas'].append(area)
                    key = 'roots' if '/rest/services' in u or '/geoserver' in u or 'wfs' in u.lower() else 'wide_pages'
                    if u not in e[key]: e[key].append(u)

    def stale(self, agency, today=None):
        r = (self.d.get(agency) or {}).get('read')
        if not r: return True
        return ((today or dt.date.today()) - dt.date.fromisoformat(r)).days > REREAD_DAYS

    def mark_read(self, agency): self.entry(agency)['read'] = dt.date.today().isoformat()

    def save(self): json.dump(self.d, open(self.p, 'w'), indent=1, ensure_ascii=False)


def group(gap_rows):
    """[(agency, [row, ...])] biggest group first. A row is {area, ref, park, kinds, agency, ...}."""
    g = {}
    for r in gap_rows: g.setdefault(r.get('agency') or 'unknown', []).append(r)
    return sorted(g.items(), key=lambda kv: (-len(kv[1]), kv[0]))
