# ---------------------------------------------------------------- polite web reader (same block in every KPC tool)
BANNED_HOSTS = re.compile(
    r'(^|\.)(openstreetmap\.(org|fr|de)|osm\.org|overpass-api\.de|overpass\.[a-z.]+|geofabrik\.de|'
    r'maps\.google\.[a-z.]+|maps\.googleapis\.com|mt\d?\.google\.com|khms?\d?\.google\.com|mymaps\.google\.com|'
    r'tile\.googleapis\.com|alltrails\.com|gaiagps\.com|strava\.com|tripadvisor\.[a-z.]+|yelp\.[a-z.]+|'
    r'wikipedia\.org|wikimedia\.org|wikidata\.org|protectedplanet\.net|unep-wcmc\.org|wdpa\.[a-z.]+|'
    r'ncnhde\.natureserve\.org)$', re.I)    # Nov 7: NC NHDE disallows AI bots: no requests at all, robots.txt included
# Nov 7: services.arcgis.com/33TOOklri9xpic7U (Grant County, NM) is never used (standing rule)
BANNED_URL = re.compile(r'google\.[a-z.]+/maps|/maps/d/|protectedplanet|wdpa|'
                        r'services\.arcgis\.com/33TOOklri9xpic7U(/|$|\?)', re.I)
# Nov 10 (owner rule, 2026-11-10): every services*.arcgis.com host and apps.fs.usda.gov are saved-copy only: no request of any
# kind, robots.txt and redirect hops included. KPC_SAVED_ONLY_HOSTS adds hosts; it never drops these.
NEVER_LIVE = re.compile(r'^(services(\d+|-[a-z0-9]+)?\.arcgis\.com|apps\.fs\.usda\.gov|ncnhde\.natureserve\.org)$', re.I)
from urllib.parse import urljoin as _polite_urljoin
from urllib.parse import unquote as _polite_unquote


def _no_net(*a, **k):
    """KPC_NO_NET=1 (set by the test gate): any real request raises instead of touching a socket. Mocked tests replace _raw / _one / the session."""
    raise RuntimeError('network disabled (KPC_NO_NET=1)')


def banned(url):
    """True for the sources the club never uses (KPC rules 1 + handoff Part A.6) and the saved-copy-only hosts. Fail closed:
    not a plain http(s) address with a host = banned. The host is the one really dialled (no port, user@ or trailing dot)."""
    try:
        p = urlparse(str(url or '').strip())
        h = _polite_unquote(p.hostname or '').lower().rstrip('.')
    except ValueError:
        return True
    if p.scheme.lower() not in ('http', 'https') or not h:
        return True
    extra = {x.strip().lower().rstrip('.') for x in (os.environ.get('KPC_SAVED_ONLY_HOSTS') or '').split(',') if x.strip()}
    if NEVER_LIVE.match(h) or h in extra:
        return True
    if h == 'storage.googleapis.com':          # a government's own file on cloud storage is allowed
        return False
    return bool(BANNED_HOSTS.search(h) or BANNED_URL.search(url))


def today():
    return datetime.now().strftime('%Y-%m-%d')


class Robots:
    """Small RFC 9309 robots.txt reader: our group (token 'kpc') or '*', longest match wins, Allow wins ties."""
    def __init__(self, text, token='kpc'):
        self.rules, self.sitemaps, self.delay = [], [], None
        groups, cur, last_ua = [], None, False
        for raw in (text or '').splitlines():
            line = raw.split('#', 1)[0].strip()
            if ':' not in line:
                continue
            k, v = line.split(':', 1)
            k, v = k.strip().lower(), v.strip()
            if k == 'sitemap':
                if v:
                    self.sitemaps.append(v)
                continue
            if k == 'user-agent':
                if not last_ua:
                    cur = {'agents': [], 'rules': [], 'delay': None}
                    groups.append(cur)
                cur['agents'].append(v.lower())
                last_ua = True
                continue
            last_ua = False
            if cur is None:
                continue
            if k in ('allow', 'disallow'):
                cur['rules'].append((k == 'allow', v))
            elif k == 'crawl-delay':
                try:
                    cur['delay'] = float(v)
                except ValueError:
                    pass
        tok = token.lower()
        mine = [g for g in groups if any(a != '*' and (a == tok or a.startswith(tok)) for a in g['agents'])]
        star = [g for g in groups if '*' in g['agents']]
        chosen = mine or star
        for g in chosen:
            self.rules += g['rules']
            if g['delay'] is not None:
                self.delay = g['delay']

    @staticmethod
    def _match(pat, path):
        if not pat:
            return -1
        rx = re.escape(pat).replace(r'\*', '.*')
        if rx.endswith(r'\$'):
            rx = rx[:-2] + '$'
        return len(pat) if re.match(rx, path) else -1

    def allowed(self, url):
        p = urlparse(url)
        path = (p.path or '/') + (('?' + p.query) if p.query else '')
        best, ok = -1, True
        for allow, pat in self.rules:
            n = self._match(pat, path)
            if n > best or (n == best and n >= 0 and allow):
                best, ok = n, allow
        return ok if best >= 0 else True


class Polite:
    """One request at a time, >= 2 s per host, robots.txt obeyed, 429/503 -> wait and retry 3 times,
    then the host 'rests' for the rest of the run. Optional download cache (--cache).
    Always the one honest User-Agent "KPC park tools (<KPC_CONTACT>)", never another one (club decision, Oct 31).
    A 403 on a DATA request is accepted: no retry, the host is marked 'blocked' with the reason and is not asked
    again this run (on a shared ArcGIS Online / cloud-storage host the 403 belongs to that one address, so only it
    is dropped).
    robots.txt (standing rule, Nov 7; replaces the Oct 31 'robots 403 = no rules' decision):
      200 = its rules are obeyed for every path, ArcGIS REST included (there is no API/REST exemption any more);
      401 / 403 = STOP: the whole host is treated as 'Disallow: /' and nothing is read from it;
      5xx / 429 / no answer = STOP for this run too (fail closed);
      404 / 410 / other 4xx = no robots file, read normally.
    Redirects are followed one hop at a time; every hop is checked against the banned list and that host's robots.
    ArcGIS Hub portals get at least 60 s between requests; a robots Crawl-delay is always honoured in full."""
    MIN_GAP = 2.0       # club decision (Oct 31): at least 2 seconds between two requests to one host, every tool
    HUB_GAP = 60.0      # standing rule: ArcGIS Hub portals need at least a 60-second crawl delay
    MAX_DELAY = 300.0   # Nov 7 review: a robots Crawl-delay is honoured in full up to this; above it the host RESTS for the run (no request
    #                     at all still obeys robots) instead of sleeping inside a time-budgeted job
    HUB_RX = re.compile(r'(^|\.)(hub\.arcgis\.com|opendata\.arcgis\.com)$', re.I)
    SHARED_RX = re.compile(r'(^|\.)(arcgis\.com|storage\.googleapis\.com)$', re.I)
    MAX_HOPS = 5
    STOP_ROBOTS = 'User-agent: *\nDisallow: /\n'

    def __init__(self, cache=None, gap=2.0, timeout=60, max_bytes=60_000_000, cache_days=30, log=None, rest_exempt=False):
        # rest_exempt is still accepted so older callers keep working, but it does nothing: no REST robots exemption.
        contact = os.environ.get('KPC_CONTACT') or 'https://github.com/KentuckyPortableClub'
        self.ua = f'KPC park tools ({contact})'
        self.blocked = {}          # host (or, on a shared host, the address) -> why: "403 Forbidden on <url>"
        self.gap = max(gap, self.MIN_GAP) if gap else gap      # gap=0 only in the no-network selftest
        self.timeout, self.max_bytes, self.cache_days = timeout, max_bytes, cache_days
        self.cache = cache
        self.last, self.robots, self.resting = {}, {}, set()
        self.rest_exempt = False
        self.robots_stop = {}      # host -> why robots.txt says STOP ("robots.txt answered 403")
        self.stats = {'requests': 0, 'cache_hits': 0, 'robots_refused': 0, 'rested': 0, 'banned': 0, 'errors': 0, 'blocked': 0}
        self.log = log or (lambda *a: None)
        self.s = requests.Session()
        if os.environ.get('KPC_NO_NET') == '1': self.s.request = _no_net
        if cache:
            os.makedirs(cache, exist_ok=True)

    def _wait(self, host, extra=0.0):
        gap = self.gap
        rb = self.robots.get(host)
        if rb is not None and rb.delay:
            gap = max(gap, min(rb.delay, self.MAX_DELAY))   # Nov 7: honoured in full up to MAX_DELAY (was capped at 30 s)
        if gap and self.HUB_RX.search(host):
            gap = max(gap, self.HUB_GAP)
        t = self.last.get(host, 0) + gap + extra - time.time()
        if t > 0:
            time.sleep(t)
        self.last[host] = time.time()

    def _cache_path(self, url, method='GET', body=None):
        key = hashlib.sha1((method + ' ' + url + ' ' + (body or '')).encode()).hexdigest()
        return os.path.join(self.cache, key[:2], key)

    def _refusal(self, url, robots=True):
        """Why this address may not be asked (banned / blocked / robots), or None. robots=False skips robots
        (the robots.txt read itself)."""
        if banned(url):
            self.stats['banned'] += 1
            return 'banned'
        if self._block_key(url) in self.blocked:
            return 403
        if robots and not self.robots_for(url).allowed(url):
            self.stats['robots_refused'] += 1
            return 'robots'
        return None

    def _raw(self, url, method='GET', data=None, headers=None):
        """One request, following redirects one hop at a time: every hop is checked first (banned list, blocked
        hosts, that host's robots.txt), so a redirect can never lead to a source we may not read.
        (A robots.txt read checks only the banned list and blocked hosts on its own redirects.)"""
        robots = not (urlparse(url).path or '').endswith('/robots.txt')
        for _hop in range(self.MAX_HOPS + 1):
            st, hd, body, final = self._one(url, method, data, headers)
            loc = hd.get('Location') or hd.get('location') if isinstance(st, int) else None
            if not (isinstance(st, int) and st in (301, 302, 303, 307, 308) and loc):
                return st, hd, body, final
            nxt = _polite_urljoin(url, loc)
            why = self._refusal(nxt, robots=robots)
            if why is not None:
                self.log(f'  redirect from {url} to {nxt} not followed ({why})')
                return why, {}, b'', nxt
            if st == 303 or (st in (301, 302) and method == 'POST'):
                method, data = 'GET', None
            url = nxt
        self.stats['errors'] += 1
        return 'err:TooManyRedirects', {}, b'', url

    def _one(self, url, method='GET', data=None, headers=None):
        if banned(url):   # Nov 11 (owner rule, 2026-11-11): the last door before the socket. get() and every redirect hop refuse first; this
            #                makes services*.arcgis.com / apps.fs.usda.gov (NEVER_LIVE) unreachable even for a future caller that skips get(), robots.txt included
            self.stats['banned'] += 1
            return 'banned', {}, b'', url
        host = (urlparse(url).hostname or '').lower()
        tries = 0
        while True:
            self._wait(host)
            h = dict(headers or {})
            h['User-Agent'] = self.ua          # the one honest name, always
            self.stats['requests'] += 1
            try:
                r = self.s.request(method, url, data=data, headers=h, timeout=self.timeout, stream=True, allow_redirects=False)
                body = b''
                for chunk in r.iter_content(65536):
                    body += chunk
                    if len(body) > self.max_bytes:
                        break
                r.close()
            except requests.RequestException as e:
                tries += 1
                if tries <= 2:
                    self._wait(host, extra=3.0 * tries)
                    continue
                self.stats['errors'] += 1
                return f'err:{type(e).__name__}', {}, b'', url
            if r.status_code in (429, 503):
                tries += 1
                if tries > 3:
                    self.resting.add(host)
                    self.log(f'  {host}: busy (HTTP {r.status_code}) 3 times, resting it for this run')
                    return r.status_code, dict(r.headers), body, r.url
                ra = r.headers.get('Retry-After', '')
                wait = float(ra) if ra.isdigit() else 5.0 * (2 ** (tries - 1))
                time.sleep(min(wait, 60.0))
                continue
            return r.status_code, dict(r.headers), body, r.url

    def robots_for(self, url):
        p = urlparse(url)
        host = (p.hostname or '').lower()
        if banned(url):   # Nov 11: a never-live host is not even asked for robots.txt; it reads as Disallow: / for this run
            self.robots_stop.setdefault(host, 'saved-copy only host (never contacted)')
            return Robots(self.STOP_ROBOTS)
        if host not in self.robots:
            self.robots[host] = None  # placeholder while reading
            st, hd, body, _ = self._cached(f'{p.scheme or "https"}://{p.netloc}/robots.txt', robots=False)
            if st == 200 and b'<html' not in body[:500].lower():
                self.robots[host] = Robots(body.decode('utf-8', 'replace'))
            elif st == 200 or (isinstance(st, int) and 400 <= st < 500 and st not in (401, 403, 429)):
                self.robots[host] = Robots('')   # no robots file (404 / 410 / an HTML page) = no rules
            else:
                # Nov 7 standing rule: a robots 401/403 is a STOP (disallow), never permission; 5xx / 429 /
                # no answer / refused = STOP for this run too (fail closed). No other user-agent or API path is tried.
                why = f'robots.txt answered {st}'
                self.robots_stop[host] = why
                self.log(f'  {host}/robots.txt answered {st}: treated as Disallow: / (STOP); nothing is read from this host')
                self.robots[host] = Robots(self.STOP_ROBOTS)
        return self.robots[host]

    def _cached(self, url, method='GET', data=None, headers=None, robots=True, nocache=False):
        if self.cache and not nocache:
            cp = self._cache_path(url, method, data if isinstance(data, str) else (json.dumps(data, sort_keys=True) if data else None))
            if os.path.exists(cp + '.json'):
                try:
                    meta = json.load(open(cp + '.json'))
                    age = (time.time() - meta['t']) / 86400
                    if age < self.cache_days:
                        fin = meta.get('final', url)
                        # Nov 7: a cached answer that came through a redirect is only reused if that address is
                        # still allowed today (an old cache must not bring back a banned / robots-blocked source)
                        why = self._refusal(fin, robots=robots) if fin != url else None
                        if why is not None:
                            return why, {}, b'', fin
                        self.stats['cache_hits'] += 1
                        return meta['status'], meta.get('headers', {}), open(cp, 'rb').read(), fin
                except (OSError, ValueError, KeyError):
                    pass
        st, hd, body, final = self._raw(url, method, data, headers)
        if st == 403 and robots:       # robots=False is the robots.txt read itself: a 403 there is not a block
            self._block(url)
        if self.cache and st == 200 and not nocache:
            os.makedirs(os.path.dirname(cp), exist_ok=True)
            with open(cp, 'wb') as f:
                f.write(body)
            keep = {k: v for k, v in hd.items() if k.lower() in ('content-type', 'last-modified', 'content-length')}
            json.dump({'url': url, 't': time.time(), 'date': today(), 'status': st, 'headers': keep, 'final': final}, open(cp + '.json', 'w'))
        return st, hd, body, final

    def _block_key(self, url):
        p = urlparse(url)
        host = (p.hostname or '').lower()
        return (host + p.path) if self.SHARED_RX.search(host) else host

    def _block(self, url):
        k = self._block_key(url)
        if k not in self.blocked:
            self.blocked[k] = f'403 Forbidden on {url}'
            self.log(f'  {k}: blocked (403 Forbidden on {url}); accepted, not asked again this run')
        self.stats['blocked'] += 1

    def get(self, url, method='GET', data=None, headers=None, nocache=False):
        """Returns (status, headers, body, final_url). status is an int, or 'banned' / 'robots' / 'resting' / 'err:...'.
        A blocked host answers 403 from here without being asked again (see self.blocked for why)."""
        if banned(url):
            self.stats['banned'] += 1
            return 'banned', {}, b'', url
        host = (urlparse(url).hostname or '').lower()
        if host in self.resting:
            self.stats['rested'] += 1
            return 'resting', {}, b'', url
        if self._block_key(url) in self.blocked:
            return 403, {}, b'', url
        rb = self.robots_for(url)
        if not rb.allowed(url):     # Nov 7: obeyed on every path, ArcGIS REST included
            self.stats['robots_refused'] += 1
            return 'robots', {}, b'', url
        if rb.delay and rb.delay > self.MAX_DELAY and host not in self.resting:
            self.resting.add(host)      # Nov 7 review: a Crawl-delay we cannot honour inside a time budget = rest the host, do not sleep for it
            self.log(f'  {host}: robots Crawl-delay {rb.delay:g} s is over {self.MAX_DELAY:g} s; resting it for this run (no requests)')
            self.stats['rested'] += 1
            return 'resting', {}, b'', url
        return self._cached(url, method, data, headers, nocache=nocache)


def polite_selftest():
    """No network: one honest User-Agent, >= 2 s per host, a 403 on data is accepted (no retry) and the host marked
    blocked. Nov 7 standing rules: a robots.txt 401/403 (or 5xx / no answer) is a STOP with no data request; robots
    Disallow is obeyed on ArcGIS REST paths too (rest_exempt does nothing); the banned list holds NC NHDE and the
    Grant County ArcGIS org; redirects to a banned or robots-blocked address are not followed (nor reused from the
    cache); ArcGIS Hub portals get >= 60 s between requests."""
    problems, calls = [], []
    w = Polite(cache=None, gap=1.0)
    if w.gap < 2.0:
        problems.append(f'gap between requests to one host is {w.gap} s, must be >= 2 s')
    if not re.fullmatch(r'KPC park tools \(.+\)', w.ua) or hasattr(w, 'ua_compat'):
        problems.append('User-Agent must be exactly "KPC park tools (<KPC_CONTACT>)", with no second one')
    w.gap = 0

    def fake(url, method='GET', data=None, headers=None):
        calls.append(url)
        return (404 if url.endswith('/robots.txt') else 403), {}, b'', url
    w._raw = fake
    st1 = w.get('https://blocked.example.gov/a.xml')[0]
    n1 = len(calls)
    st2 = w.get('https://blocked.example.gov/b.xml')[0]
    if st1 != 403 or st2 != 403:
        problems.append('a 403 must come back as 403')
    if len(calls) != n1:
        problems.append('a blocked host was asked again')
    if not w.blocked.get('blocked.example.gov', '').startswith('403 Forbidden on https://blocked.example.gov/'):
        problems.append(f'blocked host not marked with the reason: {w.blocked}')
    w.get('https://tiles.arcgis.com/x/arcgis/rest/services/A/FeatureServer/0')
    n2 = len(calls)
    w.get('https://tiles.arcgis.com/x/arcgis/rest/services/B/FeatureServer/0')
    if len(calls) == n2:
        problems.append('on a shared ArcGIS host only the one refused address may be dropped')

    # robots.txt 404 / 410 = no robots file: the data is read
    for code in (404, 410):
        w2, calls2 = Polite(cache=None, gap=1.0), []
        w2.gap = 0

        def fake2(url, method='GET', data=None, headers=None, code=code):
            calls2.append(url)
            return (code if url.endswith('/robots.txt') else 200), {}, b'{}', url
        w2._raw = fake2
        st = w2.get('https://robots404.example.gov/arcgis/rest/services/P/MapServer/0?f=json')[0]
        if st != 200 or w2.blocked or len(calls2) != 2:
            problems.append(f'a {code} on robots.txt means no robots file: the data must be read ({st}, {calls2})')

    # robots.txt 401 / 403 (any host), 5xx, 429 or no answer = STOP, no data request
    for code in (401, 403, 500, 503, 429, 'err:ConnectionError'):
        for host in ('tiles.arcgis.com', 'www.arcgis.com', 'gis.example.gov'):
            w2, calls2 = Polite(cache=None, gap=1.0), []
            w2.gap = 0

            def fake3(url, method='GET', data=None, headers=None, code=code):
                calls2.append(url)
                return (code if url.endswith('/robots.txt') else 200), {}, b'{}', url
            w2._raw = fake3
            st = w2.get(f'https://{host}/abc/arcgis/rest/services/P/FeatureServer/0/query?f=json')[0]
            st_b = w2.get(f'https://{host}/abc/arcgis/rest/services/Q/FeatureServer/0?f=json')[0]
            if st != 'robots' or st_b != 'robots' or any(not u.endswith('/robots.txt') for u in calls2) \
                    or len(calls2) != 1 or host not in w2.robots_stop:
                problems.append(f'robots.txt {code} on {host} must STOP with no data request ({st}, {st_b}, {calls2})')

    # robots Disallow on a REST path is obeyed, even if a caller still passes rest_exempt=True
    w4, calls4 = Polite(cache=None, gap=1.0, rest_exempt=True), []
    w4.gap = 0

    def fake4(url, method='GET', data=None, headers=None):
        calls4.append(url)
        if url.endswith('/robots.txt'):
            return 200, {}, b'User-agent: *\nDisallow: /arcgis/rest/\n', url
        return 200, {}, b'{}', url
    w4._raw = fake4
    if w4.get('https://gis.example.gov/arcgis/rest/services/P/MapServer/0?f=json')[0] != 'robots' or len(calls4) != 1:
        problems.append(f'a robots Disallow on an ArcGIS REST path must be obeyed (no REST exemption): {calls4}')

    # banned: NC NHDE, the Grant County, NM ArcGIS org, every services*.arcgis.com host and apps.fs.usda.gov (any port /
    # user@ / trailing-dot form), not even robots.txt; an address with no plain http(s) host fails closed
    w5, calls5 = Polite(cache=None, gap=1.0), []
    w5.gap = 0
    w5._raw = lambda url, method='GET', data=None, headers=None: (calls5.append(url), (200, {}, b'', url))[1]
    for u in ('https://ncnhde.natureserve.org/arcgis/rest/services/x/MapServer/0',
              'https://NCNHDE.natureserve.org/robots.txt',
              'https://services.arcgis.com/33TOOklri9xpic7U/arcgis/rest/services/P/FeatureServer/0',
              'https://services.arcgis.com/33TOOklri9xpic7U?f=json',
              'https://services.arcgis.com/OtherOrg/arcgis/rest/services/P/FeatureServer/0',
              'https://services1.arcgis.com:443/x/arcgis/rest/services/P/FeatureServer/0',
              'https://u@services9.arcgis.com/x', 'https://services-eu1.arcgis.com./x', 'https://apps.fs.usda.gov./arcx/rest/services',
              '//services2.arcgis.com/x', 'ftp://gis.example.gov/x'):
        if w5.get(u)[0] != 'banned':
            problems.append(f'{u} must be banned')
    if calls5:
        problems.append(f'a banned source must get no request at all, robots.txt included: {calls5}')
    if banned('https://www.arcgis.com/sharing/rest/content/items/x') or banned('https://hub.arcgis.com/datasets/x'):
        problems.append('www.arcgis.com / hub.arcgis.com are not saved-copy-only hosts')

    # redirects: a hop to a banned or robots-blocked address is never requested
    w6, calls6 = Polite(cache=None, gap=1.0), []
    w6.gap = 0
    hops = {'https://a.example.gov/x': 'https://services3.arcgis.com:443/x',
            'https://a.example.gov/y': 'https://b.example.gov/private/y',
            'https://a.example.gov/z': 'https://c.example.gov/z'}

    def fake6(url, method='GET', data=None, headers=None):
        calls6.append(url)
        if url == 'https://b.example.gov/robots.txt':
            return 200, {}, b'User-agent: *\nDisallow: /private/\n', url
        if url.endswith('/robots.txt'):
            return 404, {}, b'', url
        if url in hops:
            return 302, {'Location': hops[url]}, b'', url
        return 200, {}, b'ok', url
    w6._one = fake6
    for src, want in (('https://a.example.gov/x', 'banned'), ('https://a.example.gov/y', 'robots')):
        st, _, _, fin = w6.get(src)
        if st != want or fin != hops[src] or hops[src] in calls6:
            problems.append(f'a redirect {src} -> {hops[src]} must stop as {want} with no request ({st}, {calls6})')
    st, _, body, fin = w6.get('https://a.example.gov/z')
    if st != 200 or fin != 'https://c.example.gov/z' or body != b'ok':
        problems.append(f'an allowed redirect must still be followed ({st}, {fin})')

    # cache: an old cached answer that came through a now-refused redirect is not reused
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        w7 = Polite(cache=td, gap=1.0)
        w7.gap = 0
        u = 'https://d.example.gov/data.json'
        cp = w7._cache_path(u)
        os.makedirs(os.path.dirname(cp), exist_ok=True)
        open(cp, 'wb').write(b'{"old": 1}')
        json.dump({'url': u, 't': time.time(), 'status': 200, 'headers': {}, 'final': 'https://ncnhde.natureserve.org/q'},
                  open(cp + '.json', 'w'))
        w7._raw = lambda url, method='GET', data=None, headers=None: (404, {}, b'', url)
        if w7.get(u)[0] != 'banned':
            problems.append('a cached answer from a banned redirect target must not be reused')

    # ArcGIS Hub portals: >= 60 s between two requests; a robots Crawl-delay above 30 s is honoured in full
    w8 = Polite(cache=None, gap=2.0)
    slept = []
    real_sleep = time.sleep
    try:
        time.sleep = lambda t: slept.append(t)
        now = time.time()
        w8.last['data-kygeonet.opendata.arcgis.com'] = now
        w8._wait('data-kygeonet.opendata.arcgis.com')
        w8.last['x.hub.arcgis.com'] = now
        w8._wait('x.hub.arcgis.com')
        w8.robots['slow.example.gov'] = Robots('User-agent: *\nCrawl-delay: 90\n')
        w8.last['slow.example.gov'] = time.time()
        w8._wait('slow.example.gov')
    finally:
        time.sleep = real_sleep
    if len(slept) != 3 or min(slept[:2]) < 59 or slept[2] < 89:
        problems.append(f'ArcGIS Hub must wait >= 60 s and a 90 s Crawl-delay must be honoured: {slept}')
    # a Crawl-delay over MAX_DELAY rests the host: no request, no sleep (a run must not stall for an hour on one host)
    w10, calls10 = Polite(cache=None, gap=1.0), []
    w10.gap = 0
    w10.robots['slow2.example.gov'] = Robots('User-agent: *\nCrawl-delay: 3600\n')
    w10._raw = lambda url, method='GET', data=None, headers=None: (calls10.append(url), (200, {}, b'{}', url))[1]
    slept2 = []
    try:
        time.sleep = lambda t: slept2.append(t)
        st10 = w10.get('https://slow2.example.gov/data.json')[0]
    finally:
        time.sleep = real_sleep
    if st10 != 'resting' or calls10 or slept2 or 'slow2.example.gov' not in w10.resting:
        problems.append(f'a Crawl-delay over {Polite.MAX_DELAY:g} s must rest the host with no request and no sleep: {st10} {calls10} {slept2}')
    # KPC_NO_NET=1: a real request raises, no socket is opened
    old = os.environ.get('KPC_NO_NET')
    os.environ['KPC_NO_NET'] = '1'
    try:
        w9 = Polite(cache=None, gap=1.0)
        w9.gap = 0
        try:
            w9._one('https://no-net.example.invalid/x')
            problems.append('KPC_NO_NET=1 must stop a real request')
        except RuntimeError:
            pass
    finally:
        if old is None: os.environ.pop('KPC_NO_NET', None)
        else: os.environ['KPC_NO_NET'] = old
    # Nov 11 (owner rule, 2026-11-11): services*.arcgis.com and apps.fs.usda.gov get NO request of any kind - not the data, not robots.txt,
    # not a redirect hop - even from a caller that skips get() (robots_for, _cached, _raw, _one called directly).
    sent = []

    class _R:
        def __init__(self, st, hd=None): self.status_code, self.headers, self.url = st, hd or {}, ''
        def iter_content(self, n): return [b'']
        def close(self): pass

    def _rec(method, url, **k):
        sent.append(url)
        if 'hop.example.invalid' in url and not url.endswith('/robots.txt'):
            return _R(302, {'Location': 'https://services2.arcgis.com/x/arcgis/rest/services/P/FeatureServer/0?f=json'})
        return _R(404)
    wn = Polite(cache=None, log=lambda m: None); wn.s.request = _rec; wn._wait = lambda *a, **k: None
    never = ['https://services1.arcgis.com/a/arcgis/rest/services/P/FeatureServer/0/query?f=json', 'https://services.arcgis.com/b/x',
             'https://SERVICES9.arcgis.com./c/x', 'https://services-eu1.arcgis.com/d/x', 'https://apps.fs.usda.gov/arcx/rest/services/x']
    for u in never:
        if wn.get(u)[0] != 'banned': problems.append(f'get() must refuse {u} before any request')
        wn.robots_for(u); wn._cached(u); wn._raw(u); wn._one(u)
    wn.get('https://hop.example.invalid/layer')
    if [x for x in sent if banned(x)]:
        problems.append(f'a never-live host was contacted (robots.txt / data / redirect hop): {[x for x in sent if banned(x)]}')
    if any('arcgis.com' in x or 'fs.usda.gov' in x for x in sent):
        problems.append(f'no request may reach services*.arcgis.com / apps.fs.usda.gov: {sent}')
    return problems
# ---------------------------------------------------------------- end of polite web reader
