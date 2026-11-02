# ---------------------------------------------------------------- polite web reader (same block in every KPC tool)
BANNED_HOSTS = re.compile(
    r'(^|\.)(openstreetmap\.(org|fr|de)|osm\.org|overpass-api\.de|overpass\.[a-z.]+|geofabrik\.de|'
    r'maps\.google\.[a-z.]+|maps\.googleapis\.com|mt\d?\.google\.com|khms?\d?\.google\.com|mymaps\.google\.com|'
    r'tile\.googleapis\.com|alltrails\.com|gaiagps\.com|strava\.com|tripadvisor\.[a-z.]+|yelp\.[a-z.]+|'
    r'wikipedia\.org|wikimedia\.org|wikidata\.org|protectedplanet\.net|unep-wcmc\.org|wdpa\.[a-z.]+)$', re.I)
BANNED_URL = re.compile(r'google\.[a-z.]+/maps|/maps/d/|protectedplanet|wdpa', re.I)


def banned(url):
    """True for the sources the club never uses (KPC rules 1 + handoff Part A.6)."""
    h = (urlparse(url).hostname or '').lower()
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
    is dropped). A 403 (or any 4xx) on robots.txt alone is NOT a block: RFC 9309 s2.3.1.3 says an unavailable
    robots.txt means no robots rules, so the data is still read (club decision, Oct 31)."""
    MIN_GAP = 2.0       # club decision (Oct 31): at least 2 seconds between two requests to one host, every tool
    SHARED_RX = re.compile(r'(^|\.)(arcgis\.com|storage\.googleapis\.com)$', re.I)
    # The club's kpc_manners.py (HQ, Oct 27) treats the documented ArcGIS REST paths as an API, not pages:
    # a robots.txt 'Disallow' there is not applied. Only tools that set rest_exempt=True use this.
    REST_RX = re.compile(r'/(rest/services|sharing/rest)(/|$)', re.I)

    def __init__(self, cache=None, gap=2.0, timeout=60, max_bytes=60_000_000, cache_days=30, log=None, rest_exempt=False):
        contact = os.environ.get('KPC_CONTACT') or 'https://github.com/KentuckyPortableClub'
        self.ua = f'KPC park tools ({contact})'
        self.blocked = {}          # host (or, on a shared host, the address) -> why: "403 Forbidden on <url>"
        self.gap = max(gap, self.MIN_GAP) if gap else gap      # gap=0 only in the no-network selftest
        self.timeout, self.max_bytes, self.cache_days = timeout, max_bytes, cache_days
        self.cache = cache
        self.last, self.robots, self.resting = {}, {}, set()
        self.rest_exempt = rest_exempt
        self.stats = {'requests': 0, 'cache_hits': 0, 'robots_refused': 0, 'rested': 0, 'banned': 0, 'errors': 0, 'blocked': 0}
        self.log = log or (lambda *a: None)
        self.s = requests.Session()
        if cache:
            os.makedirs(cache, exist_ok=True)

    def _wait(self, host, extra=0.0):
        gap = self.gap
        rb = self.robots.get(host)
        if rb is not None and rb.delay:
            gap = max(gap, min(rb.delay, 30.0))
        t = self.last.get(host, 0) + gap + extra - time.time()
        if t > 0:
            time.sleep(t)
        self.last[host] = time.time()

    def _cache_path(self, url, method='GET', body=None):
        key = hashlib.sha1((method + ' ' + url + ' ' + (body or '')).encode()).hexdigest()
        return os.path.join(self.cache, key[:2], key)

    def _raw(self, url, method='GET', data=None, headers=None):
        host = (urlparse(url).hostname or '').lower()
        tries = 0
        while True:
            self._wait(host)
            h = dict(headers or {})
            h['User-Agent'] = self.ua          # the one honest name, always
            self.stats['requests'] += 1
            try:
                r = self.s.request(method, url, data=data, headers=h, timeout=self.timeout, stream=True, allow_redirects=True)
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
        if host not in self.robots:
            self.robots[host] = None  # placeholder while reading
            st, hd, body, _ = self._cached(f'{p.scheme or "https"}://{p.netloc}/robots.txt', robots=False)
            if st == 200 and b'<html' not in body[:500].lower():
                self.robots[host] = Robots(body.decode('utf-8', 'replace'))
            else:
                if isinstance(st, int) and 400 <= st < 500:
                    self.log(f'  {host}/robots.txt answered {st}: no robots rules (RFC 9309); the data is still read')
                self.robots[host] = Robots('')   # no robots file (or not readable) = allowed
        return self.robots[host]

    def _cached(self, url, method='GET', data=None, headers=None, robots=True, nocache=False):
        if self.cache and not nocache:
            cp = self._cache_path(url, method, data if isinstance(data, str) else (json.dumps(data, sort_keys=True) if data else None))
            if os.path.exists(cp + '.json'):
                try:
                    meta = json.load(open(cp + '.json'))
                    age = (time.time() - meta['t']) / 86400
                    if age < self.cache_days:
                        self.stats['cache_hits'] += 1
                        return meta['status'], meta.get('headers', {}), open(cp, 'rb').read(), meta.get('final', url)
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
        if not self.robots_for(url).allowed(url):
            if self.rest_exempt and self.REST_RX.search(urlparse(url).path or ''):
                self.stats['robots_rest_exempt'] = self.stats.get('robots_rest_exempt', 0) + 1
            else:
                self.stats['robots_refused'] += 1
                return 'robots', {}, b'', url
        return self._cached(url, method, data, headers, nocache=nocache)


def polite_selftest():
    """No network: one honest User-Agent, >= 2 s per host, a 403 on data is accepted (no retry) and the host marked
    blocked; a 403 on robots.txt alone means no robots rules and the data is still read."""
    problems, calls = [], []
    w = Polite(cache=None, gap=1.0)
    if w.gap < 2.0:
        problems.append(f'gap between requests to one host is {w.gap} s, must be >= 2 s')
    if not re.fullmatch(r'KPC park tools \(.+\)', w.ua) or hasattr(w, 'ua_compat'):
        problems.append('User-Agent must be exactly "KPC park tools (<KPC_CONTACT>)", with no second one')
    w.gap = 0

    def fake(url, method='GET', data=None, headers=None):
        calls.append(url)
        return 403, {}, b'', url
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
    w.get('https://services9.arcgis.com/x/arcgis/rest/services/A/FeatureServer/0')
    n2 = len(calls)
    w.get('https://services9.arcgis.com/x/arcgis/rest/services/B/FeatureServer/0')
    if len(calls) == n2:
        problems.append('on a shared ArcGIS host only the one refused address may be dropped')
    # robots.txt 403 alone = no robots rules (RFC 9309): the data request still goes out and is not blocked
    for code in (401, 403, 404, 451):      # any 4xx on robots.txt alone: no robots rules, keep reading
        w2, calls2 = Polite(cache=None, gap=1.0), []
        w2.gap = 0

        def fake2(url, method='GET', data=None, headers=None, code=code):
            calls2.append(url)
            return (code if url.endswith('/robots.txt') else 200), {}, b'{}', url
        w2._raw = fake2
        st = w2.get('https://robots4xx.example.gov/arcgis/rest/services/P/MapServer/0?f=json')[0]
        st_b = w2.get('https://robots4xx.example.gov/data/parks.xml')[0]
        if st != 200 or st_b != 200 or w2.blocked or len(calls2) != 3:
            problems.append(f'a {code} on robots.txt alone must not block the host or stop reading '
                            f'(got {st}, {st_b}, {w2.blocked}, {calls2})')
    # ... while a 403 on a data request on a non-shared host blocks that host, with no retry
    w3, calls3 = Polite(cache=None, gap=1.0), []
    w3.gap = 0

    def fake3(url, method='GET', data=None, headers=None):
        calls3.append(url)
        return (404 if url.endswith('/robots.txt') else 403), {}, b'', url
    w3._raw = fake3
    w3.get('https://datablock.example.gov/a.xml'); n3 = len(calls3)
    w3.get('https://datablock.example.gov/b.xml')
    if 'datablock.example.gov' not in w3.blocked or len(calls3) != n3:
        problems.append(f'a 403 on the data must block the host with no retry ({w3.blocked}, {calls3})')
    return problems
# ---------------------------------------------------------------- end of polite web reader
