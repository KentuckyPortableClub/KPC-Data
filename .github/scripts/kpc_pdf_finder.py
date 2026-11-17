#!/usr/bin/env python3
"""PDF FINDER - FIND ONLY (KPC owner, 2026-11-17; Handoff 3). For a park with no official record, look on the managing agency's own
site for a park map, brochure, boundary PDF or GeoPDF, and QUEUE the URL, the park reference and the terms it found. That is all.
It never traces, never decides, never writes an outline, never saves a map (the existing picture-maps rule does that later, from
the queue: kpc_lookup.py save-map, a JPEG named by park number + one index.json row).

WHERE IT LOOKS, in this order, stopping at the first step that queues a PDF:
  0. stored copies first: a map already on branch picture-maps, then the docs bot's stored map link (data/docs), then the
     finder's saved pages (--saved). A stored answer costs no request.
  1. the state's open-data portal search API (ArcGIS Hub / Socrata / CKAN; .github/kpc-pdf-finder-portals.json)
  2. the managing agency's own park page, its "Maps" section: links, data-* attributes and PDF addresses inside scripts / JSON
     (sections filled in by script), and at most one "Maps" sub-page
  3. only then a general web search (only when KPC_FINDER_SEARCH_URL is set; off by default)

MANNERS: every request goes through kpc_manners.Manners (robots.txt per URL path, the host rules, pacing, back-off, three strikes)
with the gap and strike count read from the store's fetch-settings.json. No manners code of its own. Before a request it also
applies, from the same settings: requests per host per hour / per day, a host's own longer gap, and never-contact lists
(extra-blocked-hosts.txt, robots-disallowed-layers.csv, kpc_host_rules saved-copy-only hosts: no request, not even robots.txt).
A 429, or a host parked after three failures, stops every later request to that host this run; nothing is queued from it.
A park needs one or two requests; one that would need more than --park-max (default 6, robots.txt reads included; robots.txt is
read once per host per run) stops and is listed for a person.
POTA is never asked here (a *.pota.app address is refused: the POTA door in KPC-Links is the only way in); the receipt counts it.

  python3 kpc_pdf_finder.py find --parks parks.json --settings fetch-settings.json --blocked extra-blocked-hosts.txt \
      --disallowed robots-disallowed-layers.csv [--saved DIR] [--picture-maps index.json] [--docs-dir data/docs] \
      --queue-dir OUT [--dry-run]
  python3 kpc_pdf_finder.py --selftest
parks.json: [{"ref","name","area","website"?,"agency"?}]  (kpc_trace_hold.py writes it from the keeper's list)
OUT/queue.json        [{"ref","name","area","url","terms","found_by","found_on","agency","date","robots"}]
OUT/save-map/<ref>.json  a kpc_lookup.py save-map request per queued PDF (the picture-maps rule, unchanged)
OUT/receipt.json      parks, queued, per step, requests made, served from stored copies, refused (blocked / robots / 429 / caps)"""
import csv, datetime as _dt, hashlib, html as _html, json, os, pathlib, re, sys, time, urllib.parse

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
PORTALS_FILE = HERE.parent / 'kpc-pdf-finder-portals.json'

# House never-contact list (KPC owner rules; kpc_host_rules.py already holds the Grant County NM server and ncnhde.natureserve.org)
HOUSE_NEVER = ('gis.nature.cz', 'gis-hub.bremen.de', 'ncnhde.natureserve.org', 'protectedplanet.net')
WDPA_RX = re.compile(r'protectedplanet|\bwdpa\b|wdpa[_-]', re.I)
CROWD_RX = re.compile(r'openstreetmap|(?:^|\.)google\.|alltrails|gaiagps|strava|ioverlander|wikipedia|wikimedia|wikiloc|komoot|outdooractive|'
                      r'trailforks|caltopo|onxmaps|tripadvisor|yelp', re.I)
MAPWORD = re.compile(r'\bmaps?\b|brochure|boundar(?:y|ies)|geo-?pdf|site plan|park guide|trail ?map|area map|\bplan\b|carte|d[ée]pliant', re.I)
MAPS_LINK = re.compile(r'^\s*(park )?maps?\s*$|maps? (and|&) (brochures?|directions)|park maps?|cartes?', re.I)
PDF_RX = re.compile(r'''(?:https?:)?//[^\s"'<>()\\]+?\.pdf(?:\?[^\s"'<>()\\]*)?|(?<![\w.])/[^\s"'<>()\\]+?\.pdf(?:\?[^\s"'<>()\\]*)?''', re.I)
ATTR_RX = re.compile(r'''\b(?:href|data-href|data-src|data-url|data-file|data-pdf|src)\s*=\s*["']([^"']+)["']''', re.I)
A_RX = re.compile(r'<a\b([^>]*)>(.*?)</a\s*>', re.I | re.S)
TERMS_RX = re.compile(r'terms of use|terms and conditions|licen[cs]e|copyright|public domain|open government|disclaimer|conditions d.utilisation|droits', re.I)
TAG_RX = re.compile(r'<[^>]+>')


class SettingsError(Exception):
    pass


def _flat(d, pre=''):
    for k, v in (d.items() if isinstance(d, dict) else []):
        if isinstance(v, dict): yield from _flat(v, f'{pre}{k}.')
        else: yield f'{pre}{k}', k, v


HOST_RX = re.compile(r'^[a-z0-9-]+(\.[a-z0-9-]+)+$', re.I)


def load_settings(path):
    """fetch-settings.json -> {per_hour, per_day, gap_s, strikes, host_gap: {host: s}}. The store's own file; key names are matched
    loosely (requests_per_hour / per_hour / hourly ...). Any of the four missing = SettingsError (a live run does not start)."""
    try: d = json.load(open(path, encoding='utf-8'))
    except Exception as e: raise SettingsError(f'fetch-settings.json not readable ({path}): {type(e).__name__}')  # noqa: BLE001
    out, host_gap = {}, {}
    for full, k, v in _flat(d):
        kl = k.lower()
        if HOST_RX.match(k) and isinstance(v, (int, float)): host_gap[k.lower()] = float(v); continue
        if not isinstance(v, (int, float)) or isinstance(v, bool): continue
        if 'hour' in kl and 'per_hour' not in out: out['per_hour'] = int(v)
        elif 'day' in kl and 'per_day' not in out: out['per_day'] = int(v)
        elif re.search(r'gap|between|interval|delay|seconds', kl) and 'gap_s' not in out: out['gap_s'] = float(v)
        elif re.search(r'fail|strike|park', kl) and 'strikes' not in out: out['strikes'] = int(v)
    for v in (d.get('hosts') or d.get('host_gaps') or []) if isinstance(d, dict) and isinstance(d.get('hosts') or d.get('host_gaps'), list) else []:
        if isinstance(v, dict) and v.get('host'):
            s = v.get('seconds') or v.get('gap_s') or v.get('gap')
            if isinstance(s, (int, float)): host_gap[str(v['host']).lower()] = float(s)
    miss = [k for k in ('per_hour', 'per_day', 'gap_s', 'strikes') if k not in out]
    if miss: raise SettingsError(f'fetch-settings.json lacks {", ".join(miss)}: the finder does not start')
    out['gap_s'] = max(2.0, out['gap_s'])   # never under the club's 2 s
    out['host_gap'] = host_gap
    return out


def load_blocked_hosts(path):
    """extra-blocked-hosts.txt: one host per line ('#' comments). A listed host and all its sub-hosts get no request."""
    if not path or not os.path.exists(path): raise SettingsError(f'extra-blocked-hosts.txt not found ({path}): the finder does not start')
    out = set()
    for line in open(path, encoding='utf-8'):
        h = line.split('#')[0].strip().lower().rstrip('.')
        if h: out.add(urllib.parse.urlsplit(h if '://' in h else 'https://' + h).hostname or h)
    return out


def load_disallowed_layers(path):
    """robots-disallowed-layers.csv: every cell that is an address is a refused prefix (layer and everything under it)."""
    if not path or not os.path.exists(path): raise SettingsError(f'robots-disallowed-layers.csv not found ({path}): the finder does not start')
    out = []
    for row in csv.reader(open(path, encoding='utf-8')):
        out += [c.strip().rstrip('/') for c in row if re.match(r'^https?://', c.strip(), re.I)]
    return out


def host_of(u):
    try: return (urllib.parse.urlsplit(u).hostname or '').lower().rstrip('.')
    except ValueError: return ''


def site_of(h):
    """The registrable part of a host, roughly: the last two labels (three for gov.xx.ca / state.xx.us / co.uk style names)."""
    p = h.split('.')
    if len(p) >= 3 and (p[-2] in ('gov', 'gc', 'gouv', 'state', 'co', 'org', 'on', 'qc', 'bc', 'ab', 'mb', 'sk', 'ns', 'nb', 'nl', 'pe', 'yk', 'nt', 'nu')
                        or p[-1] == 'us'):
        return '.'.join(p[-3:])
    return '.'.join(p[-2:])


def official_host(h):
    return bool(re.search(r'\.gov$|\.gov\.[a-z]{2}$|\.gc\.ca$|\.gouv\.[a-z.]+$|\.state\.[a-z]{2}\.us$|\.[a-z]{2}\.us$|(^|\.)gov\.[a-z]{2}\.ca$|\.mil$', h))


class SavedCopies:
    """Saved pages, keyed by address: <dir>/index.json {url: file}. Read before any request; a live page is saved after."""

    def __init__(self, d):
        self.d = pathlib.Path(d) if d else None
        self.idx = {}
        if self.d and (self.d / 'index.json').exists():
            try: self.idx = json.load(open(self.d / 'index.json', encoding='utf-8'))
            except ValueError: self.idx = {}

    def get(self, u):
        f = self.idx.get(u)
        if not f or not self.d or not (self.d / f).exists(): return None
        return (self.d / f).read_bytes()

    def put(self, u, body):
        if not self.d or not body or len(body) > 900_000: return
        self.d.mkdir(parents=True, exist_ok=True)
        f = hashlib.sha256(u.encode()).hexdigest()[:32] + '.html'
        (self.d / f).write_bytes(body); self.idx[u] = f
        (self.d / 'index.json').write_text(json.dumps(self.idx, indent=1, sort_keys=True) + '\n', encoding='utf-8', newline='\n')


class Finder:
    def __init__(self, settings, blocked_hosts, disallowed, saved=None, manners=None, dry_run=False, park_max=6, portals=None,
                 search_url=None, picture_maps=None, docs_dir=None, state=None, today=None, job='KPC PDF finder (find only)'):
        self.S, self.blocked, self.disallowed = settings, set(blocked_hosts or ()), list(disallowed or ())
        self.saved = saved or SavedCopies(None)
        self.dry, self.park_max = dry_run, park_max
        self.portals = portals if portals is not None else (json.load(open(PORTALS_FILE, encoding='utf-8')).get('portals', {}) if PORTALS_FILE.exists() else {})
        self.search_url = search_url if search_url is not None else (os.environ.get('KPC_FINDER_SEARCH_URL') or '')
        self.pic = picture_maps or {}
        self.docs_dir = pathlib.Path(docs_dir) if docs_dir else None
        self._docs = {}
        self.state = state if state is not None else {}
        self.today = today or _dt.date.today().isoformat()
        self.parked = {}        # host -> why (429 / three failures / caps): no more requests this run
        self.last_host = {}
        self.M = manners
        if self.M is None and not dry_run:
            import kpc_manners
            self.M = kpc_manners.Manners(job, (self.state.get('resting') or {}), gap=settings['gap_s'], strikes_out=settings['strikes'])
        self.r = {'parks': 0, 'queued': 0, 'by_step': {'stored': 0, 'portal': 0, 'agency page': 0, 'web search': 0}, 'nothing_found': 0,
                  'requests_made': 0, 'served_from_stored_copy': 0, 'planned_dry_run': 0, 'pota_requests': 0,
                  'refused': {'blocked host': 0, 'disallowed path': 0, '429 / host parked': 0, 'robots unreadable': 0, 'host caps': 0,
                              'park budget': 0, 'not the agency site': 0, 'other': 0},
                  'for_person': [], 'web_search': 'on' if self.search_url else 'off (KPC_FINDER_SEARCH_URL not set)'}
        self.queue, self.requests_log = [], []

    # ---------- the checks before any request ----------
    def check_url(self, u):
        """(ok, why). ok False = no request of any kind (robots.txt included) and nothing queued from it."""
        import kpc_host_rules as HR
        h = host_of(u)
        if not h or not re.match(r'^https?://', str(u), re.I): return False, 'blocked host: not a plain http(s) address'
        if h == 'pota.app' or h.endswith('.pota.app'): return False, 'blocked host: POTA is read only through the POTA door'
        if any(h == b or h.endswith('.' + b) for b in self.blocked): return False, f'blocked host: {h} is on extra-blocked-hosts.txt'
        if any(h == b or h.endswith('.' + b) for b in HOUSE_NEVER) or WDPA_RX.search(u): return False, f'blocked host: {h} is never contacted (house rule)'
        ok, why = HR.host_ok(u)
        if not ok: return False, f'blocked host: {why}'
        if CROWD_RX.search(h): return False, f'blocked host: {h} is an app / crowd map site, never a source'
        su = u.split('?')[0].rstrip('/')
        for p in self.disallowed:
            if su.lower().startswith(p.lower()): return False, f'disallowed path: {p} is on robots-disallowed-layers.csv'
        return True, ''

    def _caps_ok(self, h):
        now = time.time(); t = [x for x in (self.state.setdefault('host_times', {}).get(h) or []) if now - x < 86400]
        self.state['host_times'][h] = t
        if len([x for x in t if now - x < 3600]) >= self.S['per_hour']: return f'{h}: {self.S["per_hour"]} requests this hour (fetch-settings.json)'
        if len(t) >= self.S['per_day']: return f'{h}: {self.S["per_day"]} requests today (fetch-settings.json)'
        return ''

    def get(self, u, park):
        """(status, body, how). how = 'stored' | 'live' | 'dry-run' | 'refused'. status 200 = a page to read."""
        ok, why = self.check_url(u)
        if not ok:
            k = 'disallowed path' if why.startswith('disallowed') else 'blocked host'
            self.r['refused'][k] += 1; park['_log'].append(f'refused {u[:120]}: {why}'); return k, b'', 'refused'
        b = self.saved.get(u)
        if b is not None:
            self.r['served_from_stored_copy'] += 1; park['_log'].append(f'stored copy {u[:120]}'); return 200, b, 'stored'
        h = host_of(u)
        if h in self.parked:
            self.r['refused']['429 / host parked'] += 1; park['_log'].append(f'refused {u[:120]}: {self.parked[h]}'); return '429', b'', 'refused'
        if park['_live'] >= self.park_max:
            self.r['refused']['park budget'] += 1; park['_over'] = True
            park['_log'].append(f'not asked {u[:120]}: the park already used {self.park_max} requests'); return 'budget', b'', 'refused'
        if self.dry:
            self.r['planned_dry_run'] += 1; park['_live'] += 1; park['_log'].append(f'dry run, would ask {u[:120]}'); return 'dry-run', b'', 'dry-run'
        c = self._caps_ok(h)
        if c:
            self.r['refused']['host caps'] += 1; self.parked[h] = c; park['_log'].append(f'refused {u[:120]}: {c}'); return 'caps', b'', 'refused'
        g = self.S['host_gap'].get(h, 0.0)
        if g > self.S['gap_s']:
            w = g - (time.time() - self.last_host.get(h, 0)); time.sleep(max(0.0, w))
        n0 = self.M.stat.get('requests', 0)
        st, hd, body, final = self.M.get(u)
        made = self.M.stat.get('requests', 0) - n0
        self.last_host[h] = time.time()
        self.r['requests_made'] += made; park['_live'] += made
        self.state['host_times'].setdefault(h, []).extend([time.time()] * made)
        self.requests_log.append((u, st, made))
        if st == 200 and body:
            self.saved.put(u, body); return 200, body, 'live'
        if st in (429, 'rest'):
            self.parked[h] = f'{h} answered 429 (or failed {self.S["strikes"]} times): backed off, no more requests to it this run'
            self.r['refused']['429 / host parked'] += 1; park['_log'].append(f'refused {u[:120]}: {self.parked[h]}'); return '429', b'', 'refused'
        if st == 'robots':
            self.r['refused']['disallowed path'] += 1; park['_log'].append(f'refused {u[:120]}: robots.txt disallows this path'); return 'robots', b'', 'refused'
        if st in ('robots-unreadable', 'crawl-delay', 'deferred'):
            self.r['refused']['robots unreadable'] += 1; park['_log'].append(f'not read {u[:120]}: {st} (next run)'); return st, b'', 'refused'
        if st == 'host-rule':
            self.r['refused']['blocked host'] += 1; park['_log'].append(f'refused {u[:120]}: host rules'); return 'blocked host', b'', 'refused'
        self.r['refused']['other'] += 1; park['_log'].append(f'not read {u[:120]}: answer {st}'); return st, b'', 'refused'

    # ---------- reading what came back ----------
    @staticmethod
    def page_terms(txt):
        vis = TAG_RX.sub(' ', re.sub(r'<(script|style)\b.*?</\1>', ' ', txt, flags=re.I | re.S))
        vis = _html.unescape(re.sub(r'[ \t]+', ' ', vis))
        for line in re.split(r'[\r\n]+', vis):
            if TERMS_RX.search(line) and 8 < len(line.strip()) < 400: return line.strip()[:200]
        return ''

    @staticmethod
    def pdf_links(txt, base):
        """[(url, text)] every PDF named on a page: anchors (with their text), data-* attributes, and addresses inside scripts / JSON."""
        out, seen = [], set()
        def add(u, t):
            u = _html.unescape(u.replace('\\/', '/')).strip()
            if not re.search(r'\.pdf(\?|$)', u, re.I): return
            u = urllib.parse.urljoin(base, u)
            if u not in seen: seen.add(u); out.append((u, re.sub(r'\s+', ' ', TAG_RX.sub(' ', t or '')).strip()[:160]))
        for attrs, inner in A_RX.findall(txt):
            for v in ATTR_RX.findall(attrs): add(v, inner)
        for v in ATTR_RX.findall(txt): add(v, '')
        for v in PDF_RX.findall(txt.replace('\\/', '/')): add(v, '')
        return out

    @staticmethod
    def maps_page_link(txt, base):
        for attrs, inner in A_RX.findall(txt):
            t = re.sub(r'\s+', ' ', TAG_RX.sub(' ', inner)).strip()
            hv = ATTR_RX.findall(attrs)
            if hv and MAPS_LINK.search(t) and not re.search(r'\.pdf(\?|$)', hv[0], re.I):
                return urllib.parse.urljoin(base, _html.unescape(hv[0]))
        return ''

    def pick(self, links, park, page_host=''):
        """The most map-like PDF on the agency's own site, or None. Off-site PDFs are listed, never queued."""
        words = [w for w in re.findall(r'[a-z]{4,}', str(park.get('name') or '').lower()) if w not in ('park', 'state', 'provincial', 'area', 'national', 'wildlife', 'management', 'recreation', 'conservation')]
        best, bs = None, 0
        for u, t in links:
            h = host_of(u); hay = (u + ' ' + t).lower()
            if page_host and site_of(h) != site_of(page_host) and not official_host(h):
                self.r['refused']['not the agency site'] += 1; park['_log'].append(f'off-site PDF not queued: {u[:120]}'); continue
            s = 1 + 3 * bool(MAPWORD.search(hay)) + 2 * sum(w in hay for w in words)
            if s > bs: best, bs = (u, t), s
        return best if best and bs >= 3 else None

    # ---------- the three steps ----------
    def step_stored(self, park):
        ref = park['ref']
        if ref in self.pic:
            self.r['served_from_stored_copy'] += 1
            park['_log'].append('already on picture-maps: nothing to find'); return {'url': self.pic[ref].get('source_url') or '', 'terms': '', 'found_by': 'stored', 'found_on': 'picture-maps', 'already_saved': True}
        d = self._docs_for(park.get('area') or '').get(ref) or {}
        mu = (d.get('map') or {}).get('url') or ''
        if mu and re.search(r'\.pdf(\?|$)', mu, re.I):
            ok, why = self.check_url(mu)
            if not ok:
                k = 'disallowed path' if why.startswith('disallowed') else 'blocked host'
                self.r['refused'][k] += 1; park['_log'].append(f'stored map link refused {mu[:120]}: {why}'); return None
            self.r['served_from_stored_copy'] += 1
            park['_log'].append(f'stored docs-bot map link {mu[:120]}')
            return {'url': mu, 'terms': '', 'found_by': 'stored', 'found_on': f"data/docs ({d.get('page') or 'docs bot'})", 'agency': d.get('agency') or ''}
        return None

    def _docs_for(self, area):
        if area not in self._docs:
            p = self.docs_dir / f'{area}.json' if self.docs_dir else None
            try: self._docs[area] = (json.load(open(p, encoding='utf-8')).get('parks') or {}) if p and p.exists() else {}
            except ValueError: self._docs[area] = {}
        return self._docs[area]

    def portal_url(self, p, q):
        k, h = p.get('kind'), p.get('host')
        qq = urllib.parse.quote(q)
        if k == 'arcgis-hub': return f'https://{h}/api/search/v1/collections/all/items?q={qq}&limit=10'
        if k == 'socrata': return f'https://{h}/api/catalog/v1?q={qq}&limit=10'
        if k == 'ckan': return f"https://{h}{p.get('api') or '/api/3/action'}/package_search?q={qq}&rows=10"
        return ''

    def step_portal(self, park):
        p = self.portals.get(park.get('area') or '')
        if not p: park['_log'].append('no open-data portal listed for this area'); return None
        u = self.portal_url(p, f"{park.get('name')} map")
        if not u: return None
        st, body, how = self.get(u, park)
        if st != 200: return None
        try: d = json.loads(body.decode('utf-8', 'replace'))
        except ValueError: park['_log'].append('portal answer is not JSON'); return None
        cands = []
        for it in (d.get('features') or []):                       # ArcGIS Hub (OGC records)
            pr = it.get('properties') or {}
            url = pr.get('url') or ''
            if str(pr.get('type') or '').upper() == 'PDF' or re.search(r'\.pdf(\?|$)', url, re.I):
                cands.append((url, f"{pr.get('title') or ''} {pr.get('snippet') or ''}", pr.get('licenseInfo') or pr.get('license') or ''))
        for it in (d.get('results') or []) if isinstance(d.get('results'), list) else []:   # Socrata
            res, meta = it.get('resource') or {}, it.get('metadata') or {}
            url = it.get('link') or it.get('permalink') or ''
            if re.search(r'\.pdf(\?|$)', url, re.I) or 'pdf' in str(res.get('name') or '').lower():
                cands.append((url, f"{res.get('name') or ''} {res.get('description') or ''}", meta.get('license') or ''))
        rs = (d.get('result') or {}).get('results') if isinstance(d.get('result'), dict) else None   # CKAN
        for pk in rs or []:
            for res in pk.get('resources') or []:
                if str(res.get('format') or '').upper() == 'PDF' or re.search(r'\.pdf(\?|$)', str(res.get('url') or ''), re.I):
                    cands.append((res.get('url') or '', f"{pk.get('title') or ''} {res.get('name') or ''}", pk.get('license_title') or pk.get('license_id') or ''))
        best = self.pick([(c[0], c[1]) for c in cands if c[0]], park, page_host='')
        if not best: park['_log'].append(f'portal {p.get("host")}: no map PDF for this park'); return None
        terms = next((c[2] for c in cands if c[0] == best[0]), '')
        return {'url': best[0], 'terms': terms or f'portal record on {p.get("host")}: no licence field', 'found_by': 'portal', 'found_on': u}

    def step_page(self, park):
        u = park.get('website') or (self._docs_for(park.get('area') or '').get(park['ref']) or {}).get('page') or ''
        if not u: park['_log'].append('no agency park page on file'); return None
        st, body, how = self.get(u, park)
        if st != 200: return None
        txt = body.decode('utf-8', 'replace')
        terms = self.page_terms(txt)
        best = self.pick(self.pdf_links(txt, u), park, page_host=host_of(u))
        if not best:
            mp = self.maps_page_link(txt, u)
            if mp and mp != u:
                st2, body2, _ = self.get(mp, park)
                if st2 == 200:
                    t2 = body2.decode('utf-8', 'replace'); terms = terms or self.page_terms(t2)
                    best = self.pick(self.pdf_links(t2, mp), park, page_host=host_of(u)); u = mp if best else u
        if not best: park['_log'].append('agency page: no map PDF found'); return None
        return {'url': best[0], 'terms': terms or "not stated on the agency page (the agency's own published map)", 'found_by': 'agency page', 'found_on': u}

    def step_search(self, park):
        if not self.search_url: return None
        site = host_of(park.get('website') or '')
        q = f'"{park.get("name")}" map pdf' + (f' site:{site_of(site)}' if site else '')
        st, body, how = self.get(self.search_url.replace('{q}', urllib.parse.quote(q)), park)
        if st != 200: return None
        best = self.pick(self.pdf_links(body.decode('utf-8', 'replace'), self.search_url), park, page_host=site)
        if not best: return None
        return {'url': best[0], 'terms': 'found by web search: terms not read (check the agency page)', 'found_by': 'web search', 'found_on': 'web search'}

    def robots_for_queue(self, u, park):
        if self.dry or self.M is None: return 'not checked (dry run)'
        h = host_of(u)
        if h in self.parked: return 'no'
        n0 = self.M.stat.get('requests', 0)
        try: ok = self.M.robots_ok(u)
        except Exception: ok = False  # noqa: BLE001
        made = self.M.stat.get('requests', 0) - n0
        self.r['requests_made'] += made; park['_live'] += made
        if made: self.requests_log.append((f'{u.split("://")[0]}://{host_of(u)}/robots.txt', 'robots', made))
        return 'yes' if ok else 'no'

    def find(self, park):
        park = dict(park, _log=[], _live=0, _over=False)
        self.r['parks'] += 1
        hit = None
        for step in (self.step_stored, self.step_portal, self.step_page, self.step_search):
            hit = step(park)
            if hit or park['_over']: break
        row = {'ref': park['ref'], 'name': park.get('name') or '', 'area': park.get('area') or '', 'log': park['_log'][:12], 'requests': park['_live']}
        if park['_over'] and not hit:
            self.r['for_person'].append({'ref': park['ref'], 'why': f'needs more than {self.park_max} requests: stopped, not crawled'})
        if hit and not hit.get('already_saved'):
            rb = self.robots_for_queue(hit['url'], park)
            if rb == 'no':
                self.r['refused']['disallowed path'] += 1; park['_log'].append(f'found {hit["url"][:120]} but robots.txt does not allow it: not queued'); hit = None
            else:
                q = {'ref': park['ref'], 'name': park.get('name') or '', 'area': park.get('area') or '', 'url': hit['url'], 'terms': hit.get('terms') or '',
                     'found_by': hit['found_by'], 'found_on': hit.get('found_on') or '', 'agency': park.get('agency') or hit.get('agency') or host_of(hit['url']),
                     'date': self.today, 'robots': rb}
                self.queue.append(q); self.r['queued'] += 1; self.r['by_step'][hit['found_by']] += 1
                row['queued'] = q
        elif hit:
            self.r['by_step']['stored'] += 1; row['already_saved'] = True
        if not hit: self.r['nothing_found'] += 1
        return row

    def save_map_request(self, q):
        """The existing picture-maps rule's request (kpc_lookup.py save-map), unchanged."""
        hint = ' '.join(w for w in re.findall(r'[a-z]{4,}', q['name'].lower())[:3])
        return {'chat': 'pdf-finder', 'kind': 'save-map', 'ref': q['ref'], 'name': q['name'], 'agency': q['agency'], 'url': q['url'], 'pages': 1, 'hint': hint}

    def write(self, out):
        out = pathlib.Path(out); out.mkdir(parents=True, exist_ok=True)
        w = lambda p, o: p.write_text(json.dumps(o, indent=1, ensure_ascii=False) + '\n', encoding='utf-8', newline='\n')
        w(out / 'queue.json', self.queue)
        (out / 'save-map').mkdir(exist_ok=True)
        for q in self.queue: w(out / 'save-map' / f"pdf-finder-{q['ref']}.json", self.save_map_request(q))
        if self.M is not None: self.state['resting'] = self.M.resting()
        w(out / 'receipt.json', self.receipt())

    def receipt(self):
        pota = sum(m for u, st, m in self.requests_log if host_of(u) == 'pota.app' or host_of(u).endswith('.pota.app'))
        return dict(self.r, pota_requests=pota, made=self.today, dry_run=self.dry)


def _selftest():
    ok = True
    def chk(c, w):
        nonlocal ok; ok &= bool(c); print(('PASS ' if c else 'FAIL ') + w)
    S = {'per_hour': 200, 'per_day': 1500, 'gap_s': 2.0, 'strikes': 3, 'host_gap': {}}
    f = Finder(S, {'bad.example.gov'}, ['https://gis.example.gov/arcgis/rest/services/Secret'], dry_run=True, portals={})
    chk(not f.check_url('https://x.bad.example.gov/a.pdf')[0], 'a sub-host of a blocked host is refused')
    chk(not f.check_url('https://gis.example.gov/arcgis/rest/services/Secret/MapServer/0')[0], 'a disallowed layer prefix is refused')
    chk(not f.check_url('https://services2.arcgis.com/x/a.pdf')[0], 'a saved-copy-only host is refused (kpc_host_rules)')
    chk(not f.check_url('https://gis.nature.cz/a.pdf')[0] and not f.check_url('https://www.protectedplanet.net/a.pdf')[0], 'house never-contact hosts and WDPA refused')
    chk(not f.check_url('https://pota.app/#/park/US-0001')[0] and not f.check_url('https://www.pota.app/x')[0], 'POTA refused (the POTA door only)')
    links = Finder.pdf_links('<a href="/maps/pine-lake-map.pdf">Park Map</a><script>var m={"file":"https:\\/\\/parks.example.gov\\/docs\\/pine-lake-brochure.pdf"}</script>', 'https://parks.example.gov/pine-lake')
    chk(len(links) == 2 and links[0][0] == 'https://parks.example.gov/maps/pine-lake-map.pdf', 'PDF links from anchors and from script JSON')
    try: load_settings('/nonexistent.json'); chk(False, 'missing settings refused')
    except SettingsError: chk(True, 'missing fetch-settings.json: the finder does not start')
    print('SELFTEST PASS' if ok else 'SELFTEST FAIL')
    return 0 if ok else 1


def main(argv):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['find'])
    ap.add_argument('--parks', required=True); ap.add_argument('--settings', default=os.environ.get('KPC_FETCH_SETTINGS'))
    ap.add_argument('--blocked', default=os.environ.get('KPC_EXTRA_BLOCKED_HOSTS')); ap.add_argument('--disallowed', default=os.environ.get('KPC_ROBOTS_DISALLOWED_LAYERS'))
    ap.add_argument('--saved'); ap.add_argument('--picture-maps'); ap.add_argument('--docs-dir'); ap.add_argument('--state')
    ap.add_argument('--queue-dir', required=True); ap.add_argument('--dry-run', action='store_true'); ap.add_argument('--park-max', type=int, default=6)
    ap.add_argument('--max-parks', type=int, default=200)
    a = ap.parse_args(argv)
    try:
        S = load_settings(a.settings); B = load_blocked_hosts(a.blocked); D = load_disallowed_layers(a.disallowed)
    except SettingsError as e:
        print(f'::error title=PDF finder::{e}'); return 2
    pic = {}
    if a.picture_maps and os.path.exists(a.picture_maps):
        idx = json.load(open(a.picture_maps, encoding='utf-8')); pic = {m['ref']: m for m in (idx.get('maps') if isinstance(idx, dict) else idx) or [] if m.get('ref')}
    state = json.load(open(a.state, encoding='utf-8')) if a.state and os.path.exists(a.state) else {}
    F = Finder(S, B, D, SavedCopies(a.saved), dry_run=a.dry_run, park_max=a.park_max, picture_maps=pic, docs_dir=a.docs_dir, state=state)
    parks = json.load(open(a.parks, encoding='utf-8'))
    rows = [F.find(p) for p in parks[:a.max_parks]]
    F.write(a.queue_dir)
    json.dump(rows, open(pathlib.Path(a.queue_dir) / 'parks-log.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    if a.state: json.dump(state, open(a.state, 'w', encoding='utf-8'))
    print(f"::notice title=PDF finder::{F.r['parks']} parks, {F.r['queued']} PDFs queued, {F.r['requests_made']} requests, "
          f"{F.r['served_from_stored_copy']} served from stored copies{', dry run' if a.dry_run else ''}")
    return 0


if __name__ == '__main__':
    if '--selftest' in sys.argv[1:]: sys.exit(_selftest())
    sys.exit(main(sys.argv[1:]))
