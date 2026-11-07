#!/usr/bin/env python3
"""KPC county land-owner finder (T4, kpc_parcels).

For parks with no official park layer, find the county's own parcel (land-ownership) map and read who owns the
land under the POTA pin, so the club's ownership rule (R-G7) can work. It decides nothing: it writes what the
county's map says, an owner type by keywords, and why.

  python kpc_parcels.py --parks parks.json --known data/intake/parcel-layers.json --out out/
  python kpc_parcels.py --selftest

In:  --parks  [{ref, name, lat, lon, county_fips?}]   (also {"parks": [...]} or a CSV with those columns)
     --known  {county_fips: layer_url}  (or the parcel-layers.json this tool writes; may be missing / empty)
Out: <out>/parcels.json       {ref: {county, layer_url, owner, owner_type, parcel_id, acres,
                                     same_owner_parcels: [{parcel_id, acres, dist_m}], why, source_url, read_date}}
     <out>/parcel-layers.json {county_fips: {layer_url, county, source_url, read_date, why}}  (feed it back as --known)
     <out>/report.json, <out>/state.json (for --resume)
Privacy (club rule 9, club decision Oct 31): an owner's name is written ONLY when the keywords say it is a
government body (city, county, state, federal, school / utility bodies). A private owner is written only as
"owner": "private", never with the name; an owner of unknown type is not written either ("owner": null,
"owner_withheld": true). No option writes a private name. The raw parcel replies are never put in the --cache folder.
Zoning layers are not ownership: a layer whose name, title or address says zoning / zone is never used.
Exit: 0 all done, 3 time ran out (run again with --resume), 2 bad input, anything else = a crash.
"""
import argparse, csv, hashlib, json, math, os, re, sys, time
from datetime import datetime
from urllib.parse import urlparse, urlencode, quote

import requests

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
from urllib.parse import urljoin as _polite_urljoin


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
        if cache:
            os.makedirs(cache, exist_ok=True)

    def _wait(self, host, extra=0.0):
        gap = self.gap
        rb = self.robots.get(host)
        if rb is not None and rb.delay:
            gap = max(gap, rb.delay)          # Nov 7: honoured in full (was capped at 30 s)
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
        if not self.robots_for(url).allowed(url):     # Nov 7: obeyed on every path, ArcGIS REST included
            self.stats['robots_refused'] += 1
            return 'robots', {}, b'', url
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
    w.get('https://services9.arcgis.com/x/arcgis/rest/services/A/FeatureServer/0')
    n2 = len(calls)
    w.get('https://services9.arcgis.com/x/arcgis/rest/services/B/FeatureServer/0')
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

    # robots.txt 401 / 403 (any host, services*.arcgis.com included), 5xx, 429 or no answer = STOP, no data request
    for code in (401, 403, 500, 503, 429, 'err:ConnectionError'):
        for host in ('services1.arcgis.com', 'services9.arcgis.com', 'services.arcgis.com', 'gis.example.gov'):
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

    # banned: NC NHDE (not even robots.txt) and the Grant County, NM ArcGIS org
    w5, calls5 = Polite(cache=None, gap=1.0), []
    w5.gap = 0
    w5._raw = lambda url, method='GET', data=None, headers=None: (calls5.append(url), (200, {}, b'', url))[1]
    for u in ('https://ncnhde.natureserve.org/arcgis/rest/services/x/MapServer/0',
              'https://NCNHDE.natureserve.org/robots.txt',
              'https://services.arcgis.com/33TOOklri9xpic7U/arcgis/rest/services/P/FeatureServer/0',
              'https://services.arcgis.com/33TOOklri9xpic7U?f=json'):
        if w5.get(u)[0] != 'banned':
            problems.append(f'{u} must be banned')
    if calls5:
        problems.append(f'a banned source must get no request at all, robots.txt included: {calls5}')
    if banned('https://services.arcgis.com/33TOOklri9xpic7Uabc/arcgis/rest/services') or \
            banned('https://services.arcgis.com/OtherOrg/arcgis/rest/services'):
        problems.append('only the Grant County org path is banned on services.arcgis.com, not the whole host')

    # redirects: a hop to a banned or robots-blocked address is never requested
    w6, calls6 = Polite(cache=None, gap=1.0), []
    w6.gap = 0
    hops = {'https://a.example.gov/x': 'https://ncnhde.natureserve.org/x',
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
    return problems
# ---------------------------------------------------------------- end of polite web reader

HERE = os.path.dirname(os.path.abspath(__file__))

STATES = {  # fips: (postal, name)
    '01': ('AL', 'Alabama'), '02': ('AK', 'Alaska'), '04': ('AZ', 'Arizona'), '05': ('AR', 'Arkansas'),
    '06': ('CA', 'California'), '08': ('CO', 'Colorado'), '09': ('CT', 'Connecticut'), '10': ('DE', 'Delaware'),
    '11': ('DC', 'District of Columbia'), '12': ('FL', 'Florida'), '13': ('GA', 'Georgia'), '15': ('HI', 'Hawaii'),
    '16': ('ID', 'Idaho'), '17': ('IL', 'Illinois'), '18': ('IN', 'Indiana'), '19': ('IA', 'Iowa'),
    '20': ('KS', 'Kansas'), '21': ('KY', 'Kentucky'), '22': ('LA', 'Louisiana'), '23': ('ME', 'Maine'),
    '24': ('MD', 'Maryland'), '25': ('MA', 'Massachusetts'), '26': ('MI', 'Michigan'), '27': ('MN', 'Minnesota'),
    '28': ('MS', 'Mississippi'), '29': ('MO', 'Missouri'), '30': ('MT', 'Montana'), '31': ('NE', 'Nebraska'),
    '32': ('NV', 'Nevada'), '33': ('NH', 'New Hampshire'), '34': ('NJ', 'New Jersey'), '35': ('NM', 'New Mexico'),
    '36': ('NY', 'New York'), '37': ('NC', 'North Carolina'), '38': ('ND', 'North Dakota'), '39': ('OH', 'Ohio'),
    '40': ('OK', 'Oklahoma'), '41': ('OR', 'Oregon'), '42': ('PA', 'Pennsylvania'), '44': ('RI', 'Rhode Island'),
    '45': ('SC', 'South Carolina'), '46': ('SD', 'South Dakota'), '47': ('TN', 'Tennessee'), '48': ('TX', 'Texas'),
    '49': ('UT', 'Utah'), '50': ('VT', 'Vermont'), '51': ('VA', 'Virginia'), '53': ('WA', 'Washington'),
    '54': ('WV', 'West Virginia'), '55': ('WI', 'Wisconsin'), '56': ('WY', 'Wyoming'), '72': ('PR', 'Puerto Rico')}

TIGER_COUNTY = 'https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/State_County/MapServer/1/query'
TIGER_PLACE = 'https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/Places_CouSub_ConCity_SubMCD/MapServer/4/query'
AGOL_SEARCH = 'https://www.arcgis.com/sharing/rest/search'
AGOL_PORTAL = 'https://www.arcgis.com/sharing/rest/portals/'

# Statewide parcel services run by the state itself (step 2: "the state's parcel service").
STATEWIDE = {
    '48': ('https://feature.geographic.texas.gov/arcgis/rest/services/Parcels/stratmap_land_parcels_48_most_recent/MapServer/0',
           'Texas StratMap statewide land parcels (Texas Geographic Information Office, TxGIO)'),
}

GOV_WORDS = re.compile(
    r"\b(CITY|CITIES|TOWN|VILLAGE|BOROUGH|COUNTY|COUNTIES|PARISH|COMMONWEALTH|STATE|STATES|UNITED STATES|USA|U S A|"
    r"FEDERAL|GOVERNMENT|GOVT|GOV|METRO|METROPOLITAN|URBAN COUNTY|LFUCG|FISCAL COURT|MUNICIPAL|MUNICIPALITY|"
    r"DEPARTMENT|DEPT|DNR|PARKS?|RECREATION|BOARD OF EDUCATION|BD OF ED|SCHOOL|SCHOOLS|ISD|UNIVERSITY|COLLEGE|"
    r"AUTHORITY|COMMISSION|COMMISSIONERS|HISTORICAL COMMISSION|DISTRICT|WATER|SEWER|UTILITY|UTILITIES|"
    r"CORPS OF ENGINEERS|TVA|TENNESSEE VALLEY|NATIONAL PARK SERVICE|FOREST SERVICE|FISH (AND|&) WILDLIFE|"
    r"WILDLIFE|TPWD|TXDOT|HOUSING AUTHORITY|PUBLIC|TRANSPORTATION CABINET|CABINET|ST OF|TEXAS|KENTUCKY|"
    r"KY|TX|US|NAVY|ARMY|AIR FORCE)\b")
GOV_STRONG = re.compile(r"\b(CITY OF|TOWN OF|VILLAGE OF|COUNTY OF|STATE OF|ST OF|COMMONWEALTH|UNITED STATES|USA|U S A|"
                        r"GOVERNMENT|GOVT|METRO|LFUCG|FISCAL COURT|BOARD OF EDUCATION|BD OF ED|PARKS?( AND| &)? REC|"
                        r"PARKS? (BOARD|DEPT|DEPARTMENT|COMMISSION)|HISTORICAL COMMISSION|DEPARTMENT|DEPT|DNR|"
                        r"AUTHORITY|COMMISSION|SCHOOL DISTRICT|ISD|UNIVERSITY|COLLEGE|CORPS OF ENGINEERS|TVA|"
                        r"MUNICIPAL|URBAN COUNTY|NATIONAL PARK SERVICE|FOREST SERVICE|FISH (AND|&) WILDLIFE|TPWD|"
                        r"TXDOT|CABINET|WATER (DISTRICT|DEPT|COMMISSION)|UTILITIES|UTILITY|SANITATION|SEWER|"
                        # club decision, Oct 31: agency phrases that carry no STATE OF / DEPARTMENT word on their own
                        r"DIV(ISION)? OF NAT(URAL)? RES(OURCES)?|DEP(ARTMEN)?T OF CONSERVATION|"
                        r"FISH ?(AND|&) ?WILDLIFE|GAME COMM(ISSION|ISSN|ISN)?|WATER MANAGEMENT DIST(RICT)?|"
                        r"CONSERVATION AUTHORITY|PARKS? ?(AND|&) ?REC(REATION)?)\b|"
                        r"\bCOUNTY\b|\bCITY\b")
PRIVATE_WORDS = re.compile(r"\b(LLC|L L C|INC|CORP|CORPORATION|COMPANY|CO|LP|LLP|LTD|TRUST|TRUSTEE|TR|ETUX|ET UX|"
                           r"ET AL|ETAL|ESTATE|EST|CHURCH|MINISTRIES|PARTNERS|PARTNERSHIP|HOLDINGS|PROPERTIES|"
                           r"INVESTMENTS|REALTY|ASSOCIATION|ASSN|CLUB|FOUNDATION|LIVING|FAMILY|HEIRS)\b")


def owner_type(name):
    """government / private / unknown, by keywords only (the club's rule decides; a person grades)."""
    if not name or not str(name).strip():
        return 'unknown', 'no owner name in the county map'
    n = re.sub(r'[^A-Z0-9& ]+', ' ', str(name).upper())
    n = re.sub(r'\s+', ' ', n).strip()
    m = GOV_STRONG.search(n)
    if m:
        return 'government', f'the owner name says "{m.group(0).strip()}"'
    st = nr_agency(n)
    if st:
        return 'government', f'the owner name says NATURAL RESOURCES with the state word {st} (club decision, Oct 31)'
    m = PRIVATE_WORDS.search(n)
    if m:
        return 'private', f'the owner name says "{m.group(0).strip()}" and has no government word'
    ws = n.split()
    if 1 < len(ws) <= 5 and not GOV_WORDS.search(n):
        return 'private', 'the owner name looks like a person\'s name (no government word)'
    return 'unknown', 'the owner name has no clear government or private word'


# club decision, Oct 31 (round 3): an owner name that has NATURAL RESOURCES together with a state or province word is
# that state's natural resources agency, however it is spelled on the county roll ('WEST VIRGININA DIVSISION OF
# NATURAL RESOURCES', 'W VA DIVISON OF NATUARL RESOURSES'). The word for DIVISION / DEPARTMENT does not matter.
PROVINCES = ('Alberta', 'British Columbia', 'Manitoba', 'New Brunswick', 'Newfoundland and Labrador', 'Newfoundland',
             'Labrador', 'Nova Scotia', 'Ontario', 'Prince Edward Island', 'Quebec', 'Saskatchewan', 'Yukon',
             'Northwest Territories', 'Nunavut')
_REGION_WORDS = sorted({n.upper() for _, n in STATES.values() if n != 'District of Columbia'} |
                       {p.upper() for p in PROVINCES}, key=lambda x: -len(x.split()))
# short forms that are not ordinary words (postal codes such as IN / OR / ME are left out on purpose)
_REGION_SHORT = {'W VA': 'WEST VIRGINIA', 'WVA': 'WEST VIRGINIA', 'W VIRGINIA': 'WEST VIRGINIA', 'VA': 'VIRGINIA',
                 'WV': 'WEST VIRGINIA', 'KY': 'KENTUCKY', 'TENN': 'TENNESSEE', 'PENN': 'PENNSYLVANIA',
                 'MASS': 'MASSACHUSETTS', 'ARK': 'ARKANSAS', 'N C': 'NORTH CAROLINA', 'S C': 'SOUTH CAROLINA',
                 'NC': 'NORTH CAROLINA', 'SC': 'SOUTH CAROLINA', 'TX': 'TEXAS', 'MICH': 'MICHIGAN', 'MINN': 'MINNESOTA',
                 'WIS': 'WISCONSIN', 'ONT': 'ONTARIO', 'SASK': 'SASKATCHEWAN', 'ALTA': 'ALBERTA', 'BC': 'BRITISH COLUMBIA',
                 'NFLD': 'NEWFOUNDLAND', 'PEI': 'PRINCE EDWARD ISLAND', 'QUE': 'QUEBEC'}


def _edits(a, b, cap=3):
    """Damerau-Levenshtein distance (adjacent swaps count as one), stops counting past cap."""
    if abs(len(a) - len(b)) > cap:
        return cap + 1
    prev2, prev = None, list(range(len(b) + 1))
    for i in range(1, len(a) + 1):
        cur = [i] + [0] * len(b)
        for j in range(1, len(b) + 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (a[i - 1] != b[j - 1]))
            if prev2 is not None and i > 1 and j > 1 and a[i - 1] == b[j - 2] and a[i - 2] == b[j - 1]:
                cur[j] = min(cur[j], prev2[j - 2] + 1)
        prev2, prev = prev, cur
    return prev[-1]


def _near(word, target):
    """A misspelling: exact for words of 5 letters or fewer, 1 edit for 6-7 letters, 2 edits for 8 or more."""
    if word == target:
        return True
    n = len(target)
    allow = 0 if n <= 5 else 1 if n <= 7 else 2
    return allow > 0 and word[:1] == target[:1] and _edits(word, target, allow) <= allow


def nr_agency(name):
    """'WEST VIRGINIA' when the name has NATURAL RESOURCES (or NAT RES, misspellings allowed) and a state / province
    word (misspellings allowed), else None. Picks the longest state name, so 'WEST VIRGINIA' wins over 'VIRGINIA'."""
    if not name:
        return None
    n = re.sub(r'[^A-Z0-9& ]+', ' ', str(name).upper())
    w = re.sub(r'\s+', ' ', n).strip().split()
    nr = any((a == 'NAT' or _near(a, 'NATURAL')) and (b == 'RES' or _near(b, 'RESOURCES') or _near(b, 'RESOURCE'))
             for a, b in zip(w, w[1:]))
    if not nr and 'DNR' not in w:
        return None
    if PRIVATE_WORDS.search(' '.join(w)):     # 'TEXAS NATURAL RESOURCES LLC' is a company, not the agency
        return None
    for region in _REGION_WORDS:          # longest names first
        rw = region.split()
        for i in range(len(w) - len(rw) + 1):
            if all(_near(x, y) for x, y in zip(w[i:i + len(rw)], rw)):
                return region
    for short, region in sorted(_REGION_SHORT.items(), key=lambda kv: -len(kv[0])):
        sw = short.split()
        for i in range(len(w) - len(sw) + 1):
            if w[i:i + len(sw)] == sw:
                return region
    return None


# ------------------------------------------------------------------ geometry (pure Python, small and good enough)
def _xy(lon, lat, lat0):
    return lon * 111320.0 * math.cos(math.radians(lat0)), lat * 110574.0


def rings_of(g):
    if not g:
        return []
    if 'rings' in g:
        return g['rings']
    return []


def area_acres(g, lat0):
    tot = 0.0
    for r in rings_of(g):
        pts = [_xy(p[0], p[1], lat0) for p in r]
        s = 0.0
        for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]):
            s += x1 * y2 - x2 * y1
        tot += s / 2.0
    return abs(tot) / 4046.8564224


def centroid(g):
    pts = [p for r in rings_of(g) for p in r]
    if not pts:
        return None
    return sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)


def dist_m(lon1, lat1, lon2, lat2):
    x1, y1 = _xy(lon1, lat1, lat1)
    x2, y2 = _xy(lon2, lat2, lat1)
    return math.hypot(x2 - x1, y2 - y1)


# ------------------------------------------------------------------ ArcGIS helpers
def jget(web, url, params=None, nocache=False):
    u = url + ('?' + urlencode(params) if params else '')
    st, hd, body, final = web.get(u, nocache=nocache)
    if st != 200:
        return None, f'{st}', u
    try:
        d = json.loads(body)
    except ValueError:
        return None, 'not JSON', u
    if isinstance(d, dict) and d.get('error'):
        e = d['error']
        return None, f"error {e.get('code')}: {e.get('message')}", u
    return d, 'ok', u


OWNER_F = [re.compile(p, re.I) for p in (
    r'^(owner_?name|ownername1?|own_?name1?|owner1?|ownernme1?|own1|ownnam1?|owner_name_?1)$',
    r'^(deeded_?owner|taxpayer_?name|taxpayer|prop_?owner|current_?owner|ownr_?name|grantee)$',
    r'^(?!.*(addr|city|state|zip|street|mail|type|ship|_2|2$|code|count|occ|pct|percent|date|id$)).*own.*$')]
PID_F = [re.compile(p, re.I) for p in (
    r'^(parcel_?id|parcelid|parcel_?no|parcel_?num(ber)?|pid|pidn|pin|apn|prop_?id|propid|map_?no|mapno|'
    r'parcel|pvanum|pva_?id|account|acct|geo_?id|tax_?id|taxid|parcelnumb|parcel_number|mapblocklot|stateid)$',
    r'^.*(parcel|pin$|pidn).*$')]
ACRE_F = [re.compile(p, re.I) for p in (r'^(acres?|acreage|calc_?acres?|gis_?acres?|deed_?acres?|deeded_?acres|'
                                          r'total_?acres?|ac|acres_?calc|legal_?acres?)$', r'^.*acre.*$')]


def pick_field(names, pats):
    for p in pats:
        for n in names:
            if p.search(n):
                return n
    return None


def attr(a, name):
    if name is None:
        return None
    if name in a:
        return a[name]
    for k, v in a.items():
        if k.lower() == name.lower():
            return v
    return None


def clean(v):
    if v is None:
        return None
    if isinstance(v, str):
        v = v.strip()
        return v if v and v.upper() not in ('NULL', 'NONE', '<NULL>') else None
    return v


class Layer:
    """One parcel layer: url .../MapServer/<id> or .../FeatureServer/<id>, with its fields and how to ask it."""
    def __init__(self, url, info):
        self.url = url.rstrip('/')
        self.info = info
        self.fields = [f['name'] for f in info.get('fields') or []]
        aliases = [f.get('alias') or f['name'] for f in info.get('fields') or []]
        self.alias = dict(zip(self.fields, aliases))
        self.owner_f = pick_field(self.fields, OWNER_F)
        self.pid_f = pick_field(self.fields, PID_F)
        self.acre_f = pick_field(self.fields, ACRE_F)
        self.mode = None      # 'plain' | 'json+where' | 'identify'
        self.name = info.get('name') or ''

    def service(self):
        return re.sub(r'/\d+$', '', self.url)

    def layer_id(self):
        m = re.search(r'/(\d+)$', self.url)
        return m.group(1) if m else '0'


def query_point(web, L, lon, lat):
    """The parcel(s) under the pin. Plain form first; then the JSON point + where=1=1 (Texas needs it);
    then MapServer identify when a server has 'query' switched off. Returns (features, how, url)."""
    base = {'geometryType': 'esriGeometryPoint', 'inSR': '4326', 'spatialRel': 'esriSpatialRelIntersects',
            'outFields': '*', 'returnGeometry': 'true', 'outSR': '4326', 'f': 'json'}
    tries = []
    if L.mode in (None, 'plain'):
        tries.append(('plain', dict(base, geometry=f'{lon},{lat}')))
    if L.mode in (None, 'json+where'):
        tries.append(('json+where', dict(base, where='1=1', geometry=json.dumps(
            {'x': lon, 'y': lat, 'spatialReference': {'wkid': 4326}}, separators=(',', ':')))))
    last = ''
    for how, p in tries:
        d, st, u = jget(web, L.url + '/query', p, nocache=True)
        if d is not None and 'features' in d:
            L.mode = how
            return d['features'], how, u
        last = st
    if L.mode in (None, 'identify') and '/MapServer' in L.url:
        d = 0.0005
        p = {'geometry': f'{lon},{lat}', 'geometryType': 'esriGeometryPoint', 'sr': '4326',
             'layers': f'all:{L.layer_id()}', 'tolerance': '1', 'mapExtent': f'{lon-d},{lat-d},{lon+d},{lat+d}',
             'imageDisplay': '400,400,96', 'returnGeometry': 'true', 'maxAllowableOffset': '0.00001', 'f': 'json'}
        r, st, u = jget(web, L.service() + '/identify', p, nocache=True)
        if r is not None and 'results' in r:
            L.mode = 'identify'
            feats = [{'attributes': x.get('attributes', {}), 'geometry': x.get('geometry')} for x in r['results']
                     if str(x.get('layerId')) == L.layer_id()]
            return feats, 'identify', u
        last = st
    return None, last, L.url + '/query'


def nearby(web, L, lon, lat, radius, owner=None):
    """Parcels within `radius` m of the pin (all, or only those with exactly this owner name).
    Returns [(attributes, geometry, dist_m)] or None when the server did not answer."""
    dlat = radius / 110574.0
    dlon = radius / (111320.0 * max(0.2, math.cos(math.radians(lat))))
    feats = None
    if L.mode in ('plain', 'json+where'):
        where = '1=1'
        if owner is not None:
            where = f"{L.owner_f} = '" + str(owner).replace("'", "''") + "'"
        p = {'where': where, 'geometry': f'{lon-dlon},{lat-dlat},{lon+dlon},{lat+dlat}',
             'geometryType': 'esriGeometryEnvelope', 'inSR': '4326', 'spatialRel': 'esriSpatialRelIntersects',
             'outFields': ','.join(x for x in (L.owner_f, L.pid_f, L.acre_f) if x) or '*', 'returnGeometry': 'true',
             'outSR': '4326', 'maxAllowableOffset': '0.00005', 'resultRecordCount': '300', 'f': 'json'}
        d, st, u = jget(web, L.url + '/query', p, nocache=True)
        if d is None:
            p.pop('resultRecordCount')
            d, st, u = jget(web, L.url + '/query', p, nocache=True)
        feats = d.get('features') if d else None
    elif L.mode == 'identify':
        p = {'geometry': f'{lon},{lat}', 'geometryType': 'esriGeometryPoint', 'sr': '4326',
             'layers': f'all:{L.layer_id()}', 'tolerance': '200',
             'mapExtent': f'{lon-dlon},{lat-dlat},{lon+dlon},{lat+dlat}', 'imageDisplay': '400,400,96',
             'returnGeometry': 'true', 'maxAllowableOffset': '0.00005', 'f': 'json'}
        r, st, u = jget(web, L.service() + '/identify', p, nocache=True)
        if r is not None:
            feats = [{'attributes': x.get('attributes', {}), 'geometry': x.get('geometry')} for x in r.get('results', [])
                     if str(x.get('layerId')) == L.layer_id()]
    if feats is None:
        return None
    out = []
    for f in feats:
        c = centroid(f.get('geometry'))
        if not c:
            continue
        dm = dist_m(lon, lat, c[0], c[1])
        if dm <= radius:
            out.append((f.get('attributes') or {}, f.get('geometry'), dm))
    return out


def fval(L, a, field):
    if not field:
        return None
    v = clean(attr(a, field))
    if v is None:
        v = clean(attr(a, L.alias.get(field)))
    return v


def same_owner(web, L, owner, lon, lat, own_pid):
    """Parcels with exactly the same owner name within 1 km of the pin (the park's other pieces)."""
    got = nearby(web, L, lon, lat, 1000, owner)
    if got is None:
        return None
    out, seen = [], {str(own_pid)}
    for a, g, dm in got:
        ow = fval(L, a, L.owner_f)
        if ow is None or str(ow).strip().upper() != str(owner).strip().upper():
            continue
        pid = fval(L, a, L.pid_f)
        if str(pid) in seen:
            continue
        seen.add(str(pid))
        out.append({'parcel_id': pid, 'acres': acres_of(L, a, g, lat)[0], 'dist_m': round(dm)})
    out.sort(key=lambda x: x['dist_m'])
    return out


def near_government(web, L, lon, lat, own_pid, radius=300):
    """When the pin's own parcel is not a government's: government-owned parcels within 300 m (the pin may sit
    just off the park). Government names only; private names are never kept."""
    got = nearby(web, L, lon, lat, radius)
    if not got:
        return []
    out, seen = [], {str(own_pid)}
    for a, g, dm in got:
        ow = fval(L, a, L.owner_f)
        if owner_type(ow)[0] != 'government':
            continue
        pid = fval(L, a, L.pid_f)
        if str(pid) in seen:
            continue
        seen.add(str(pid))
        out.append({'parcel_id': pid, 'owner': ow, 'acres': acres_of(L, a, g, lat)[0], 'dist_m': round(dm)})
    out.sort(key=lambda x: x['dist_m'])
    return out[:5]


def acres_of(L, a, geom, lat):
    v = clean(attr(a, L.acre_f)) if L.acre_f else None
    if v is None and L.acre_f:
        v = clean(attr(a, L.alias.get(L.acre_f)))
    try:
        if v is not None and float(v) > 0:
            return round(float(v), 2), f'the county map\'s {L.acre_f} field'
    except (TypeError, ValueError):
        pass
    if geom and rings_of(geom):
        return round(area_acres(geom, lat), 2), 'worked out from the parcel outline'
    return None, 'no acres'


# ------------------------------------------------------------------ finding a county's parcel layer
GOV_HOST = re.compile(r'(\.gov|\.us|\.mil)$|(^|[.-])(gis|maps?|webgis|arcgis)\.(co|city|cityof|county)[a-z-]*\.|'
                      r'county|parish|cityof|city-of|townof|lojic|linkgis|lfucg', re.I)
GOV_ORG = re.compile(r'\b(city|town|village|borough|county|counties|parish|commonwealth|state of|government|govt|'
                     r'metro|urban county|lfucg|lojic|link-?gis|pva|property valuation|assessor|appraisal district|'
                     r'fiscal court|planning|department|dept|authority|commission|consortium|municipal|'
                     r'geographic information office|txgio|tnris|kygeonet|division of geographic|office of)\b', re.I)
NOT_GOV = re.compile(r'\b(university|univ|college|student|school of|esri|regrid|reportall|loveland|impervious|'
                     r'demo|sample|training|tutorial|class|course|copy|test|practice|hackathon|story ?map|'
                     r'realtor|realty|llc|inc|corp|consult|engineer(ing|s)|associates)\b', re.I)
# layers that are about buildings / damage forms, not land ownership, even when they carry parcel outlines
NOT_OWNERSHIP = re.compile(r'impervious|summary|analysis|damage|inspection|atc-?45|assessmentforms', re.I)
# counties the club skips for now (club decision, Oct 31). A person can still give a real parcel layer with --known.
CLUB_SKIP = {
    '21227': 'skipped by club decision (Oct 31) until a real parcel layer turns up: the only layers found for Warren '
             'County, KY are a zoning layer (zoning is not ownership) and a building damage-assessment form layer. '
             'Give a real parcel layer with --known to use one',
}
ZONING = re.compile(r'(?<![a-z])zon(e|es|ing)(?![a-z])', re.I)   # zoning is not ownership (club decision, Oct 31)
PARCEL_NAME = re.compile(r'parcel|tax ?(map|lot|parcel)|pva|propert(y|ies)|cadast|ownership|land ?records|lots?\b', re.I)


def county_at(web, lat, lon):
    p = {'geometry': f'{lon},{lat}', 'geometryType': 'esriGeometryPoint', 'inSR': '4326',
         'spatialRel': 'esriSpatialRelIntersects', 'outFields': 'GEOID,NAME,STATE,BASENAME',
         'returnGeometry': 'false', 'f': 'json'}
    d, st, u = jget(web, TIGER_COUNTY, p)
    if not d or not d.get('features'):
        return None, u, st
    a = d['features'][0]['attributes']
    return {'fips': a['GEOID'], 'name': a['NAME'], 'base': a.get('BASENAME') or a['NAME'].replace(' County', ''),
            'state': a['STATE']}, u, 'ok'


def place_at(web, lat, lon):
    p = {'geometry': f'{lon},{lat}', 'geometryType': 'esriGeometryPoint', 'inSR': '4326',
         'spatialRel': 'esriSpatialRelIntersects', 'outFields': 'NAME,BASENAME', 'returnGeometry': 'false', 'f': 'json'}
    d, st, u = jget(web, TIGER_PLACE, p)
    if d and d.get('features'):
        return d['features'][0]['attributes'].get('BASENAME')
    return None


class Finder:
    def __init__(self, web, log):
        self.web, self.log = web, log
        self.orgs = {}
        self.zoning_skipped = []

    def org_name(self, org_id):
        if not org_id:
            return ''
        if org_id not in self.orgs:
            d, st, u = jget(self.web, AGOL_PORTAL + org_id, {'f': 'json'})
            self.orgs[org_id] = (d or {}).get('name') or ''
        return self.orgs[org_id]

    def item_org(self, it):
        """The ArcGIS organisation that owns an item: from a hosted-service address, else from the item record."""
        url = it.get('url') or ''
        m = re.search(r'//(?:services\d*|tiles\d*|services-[a-z0-9]+)\.arcgis\.com/([A-Za-z0-9]+)/', url)
        oid = m.group(1) if m else it.get('orgId')
        if not oid and it.get('id'):
            d, st, u = jget(self.web, 'https://www.arcgis.com/sharing/rest/content/items/' + it['id'], {'f': 'json'})
            oid = (d or {}).get('orgId')
        return oid, self.org_name(oid)

    def search(self, cty, place, lat, lon):
        """ArcGIS Online / Hub search with the county name + 'parcels' (and the town name), kept only when the
        item covers the pin, is county-sized, and belongs to a government (host or organisation name).
        Also returns the government servers / organisations seen there, for a look at their own service list."""
        self.zoning_skipped = []
        st_name = STATES.get(cty['state'], ('', ''))[1]
        base = cty['base']
        qs = [f'{base} County parcels', f'parcels "{base} County" {st_name}']
        if place and place.lower() != base.lower():
            qs.append(f'{place} {st_name} parcels')
        cands, seen, roots = [], set(), {}
        local = {base.lower()} | ({place.lower()} if place else set())
        for q in qs:
            p = {'q': q + ' AND (type:"Feature Service" OR type:"Map Service")', 'num': '50', 'f': 'json'}
            d, st, u = jget(self.web, AGOL_SEARCH, p)
            for it in (d or {}).get('results', []):
                url = (it.get('url') or '').strip()
                if not url or url in seen:
                    continue
                seen.add(url)
                ext = it.get('extent') or []
                if len(ext) != 2:
                    continue
                (x1, y1), (x2, y2) = ext
                if not (x1 - 0.01 <= lon <= x2 + 0.01 and y1 - 0.01 <= lat <= y2 + 0.01):
                    continue
                if (x2 - x1) * (y2 - y1) > 25:     # bigger than a big state: not a county layer
                    continue
                text = ' '.join(str(it.get(k) or '') for k in ('title', 'snippet', 'tags', 'name'))
                host = (urlparse(url).hostname or '').lower()
                if ZONING.search(str(it.get('title') or '') + ' ' + str(it.get('name') or '') + ' ' + url):
                    self.zoning_skipped.append(f'"{it.get("title")}" ({url})')
                    continue
                parcelish = bool(PARCEL_NAME.search(text + ' ' + url))
                oid, org = (self.item_org(it) if (parcelish or GOV_HOST.search(host)) else (None, ''))
                who = ' '.join([org, str(it.get('accessInformation') or '')])
                score, why = 0, []
                if GOV_HOST.search(host) and not host.endswith('arcgis.com'):
                    score += 2
                    why.append(f'government host {host}')
                if GOV_ORG.search(who) or GOV_ORG.search(str(it.get('owner') or '')):
                    score += 2
                    why.append(f'published by "{(org or it.get("accessInformation") or it.get("owner") or "")[:80]}"')
                elif org and any(w in org.lower() for w in local) and not NOT_GOV.search(org):
                    score += 2
                    why.append(f'published by the organisation "{org[:60]}", named after this county / town')
                if NOT_GOV.search(who + ' ' + str(it.get('title') or '') + ' ' + str(it.get('owner') or '')):
                    score -= 4
                    why.append('looks like a copy (university / vendor / test)')
                if score >= 2:
                    # a government server or organisation: worth one look at its own list of services
                    m = re.match(r'(https?://[^/]+/[^/]+/rest/services)', url, re.I) or \
                        re.match(r'(https?://[^/]+/[A-Za-z0-9]+/arcgis/rest/services)', url, re.I)
                    if m:
                        roots.setdefault(m.group(1), '; '.join(why))
                if not parcelish or score < 2:
                    continue
                if any(w in text.lower() for w in local):
                    score += 1
                if NOT_OWNERSHIP.search(str(it.get('title') or '') + ' ' + url):
                    continue
                if re.search(r'impervious|tornado|census|address|summary|analysis', text, re.I):
                    score -= 1
                cands.append((score, url, it, '; '.join(why), u))
        cands.sort(key=lambda c: -c[0])
        return cands, roots

    def scan_root(self, root, max_folders=12):
        """The government server's own list of services (and its folders): the ones named like parcels."""
        out = []
        d, st, u = jget(self.web, root, {'f': 'json'})
        if not d:
            return out
        svcs = list(d.get('services') or [])
        for fo in (d.get('folders') or [])[:max_folders]:
            if re.search(r'parcel|pva|propert|cadast|tax|land|assess|plan|base|public|open|gis|county|city', fo, re.I):
                d2, st2, u2 = jget(self.web, root + '/' + quote(fo), {'f': 'json'})
                svcs += list((d2 or {}).get('services') or [])
        for sv in svcs:
            nm = sv.get('name') or ''
            if sv.get('type') in ('MapServer', 'FeatureServer') and PARCEL_NAME.search(nm.split('/')[-1]) and \
                    not NOT_OWNERSHIP.search(nm) and not ZONING.search(nm):
                out.append(f"{root}/{nm}/{sv['type']}")
        return out

    def layers_of(self, url):
        """The parcel polygon layers of a service URL (or the layer itself)."""
        url = url.rstrip('/')
        if re.search(r'/(MapServer|FeatureServer)/\d+$', url):
            return [url]
        if not re.search(r'/(MapServer|FeatureServer)$', url):
            return []
        d, st, u = jget(self.web, url, {'f': 'json'})
        if not d:
            return []
        ls = [l for l in d.get('layers') or [] if not l.get('subLayerIds')]
        ls = [l for l in ls if not ZONING.search(l.get('name') or '') and not NOT_OWNERSHIP.search(l.get('name') or '')]
        good = [l for l in ls if PARCEL_NAME.search(l.get('name') or '')]
        good.sort(key=lambda l: (0 if re.search(r'parcel', l.get('name') or '', re.I) else 1, l['id']))
        if not good and len(ls) == 1 and not ZONING.search(str(d.get('mapName') or d.get('serviceDescription') or '')):
            good = ls
        return [f"{url}/{l['id']}" for l in good[:3]]

    def verify(self, url, lat, lon):
        """Open the layer: polygons, and the pin falls on a parcel. Returns (Layer, features, how) or (None, why)."""
        if ZONING.search(url):
            return None, None, 'a zoning layer (zoning is not ownership; never used as a parcel source)'
        d, st, u = jget(self.web, url, {'f': 'json'})
        if not d:
            return None, None, f'layer did not open ({st})'
        if ZONING.search(str(d.get('name') or '') + ' ' + str(d.get('description') or '')[:300]):
            return None, None, 'a zoning layer (zoning is not ownership; never used as a parcel source)'
        if d.get('geometryType') and d['geometryType'] != 'esriGeometryPolygon':
            return None, None, f'not polygons ({d.get("geometryType")})'
        L = Layer(url, d)
        feats, how, qu = query_point(self.web, L, lon, lat)
        if feats is None:
            return None, None, f'could not ask it at the pin ({how})'
        if not feats:
            return None, None, 'no parcel under the pin'
        return L, feats, how


def load_known(path):
    if not path or not os.path.exists(path):
        return {}
    d = json.load(open(path))
    out = {}
    for k, v in (d or {}).items():
        if isinstance(v, str):
            out[k] = v
        elif isinstance(v, dict) and v.get('layer_url'):
            out[k] = v['layer_url']
    return out


def load_parks(path):
    if path.lower().endswith('.csv'):
        rows = list(csv.DictReader(open(path, newline='', encoding='utf-8-sig')))
    else:
        d = json.load(open(path))
        rows = d.get('parks', d) if isinstance(d, dict) else d
        if isinstance(rows, dict):
            rows = [dict(ref=k, **(v if isinstance(v, dict) else {})) for k, v in rows.items()]
    out = []
    for r in rows:
        try:
            out.append({'ref': str(r['ref']), 'name': r.get('name') or '', 'lat': float(r['lat']), 'lon': float(r['lon']),
                        'county_fips': (str(r['county_fips']).zfill(5) if r.get('county_fips') else None)})
        except (KeyError, TypeError, ValueError):
            out.append({'ref': str(r.get('ref', '?')), 'bad': True})
    return out


def run(args, web=None):
    t0 = time.time()
    deadline = t0 + args.max_minutes * 60
    out = args.out
    os.makedirs(out, exist_ok=True)
    log = (lambda *a: print(*a, flush=True)) if not args.quiet else (lambda *a: None)
    # The download cache only ever holds public catalogue replies (county lookups, searches, layer info);
    # parcel replies (which carry owner names) are asked with nocache=True.
    web = web or Polite(cache=args.cache, log=log)
    web.log = log
    read_date = today()
    try:
        parks = load_parks(args.parks)
        known = load_known(args.known)
    except (OSError, ValueError) as e:
        print(f'bad input: {e}', file=sys.stderr)
        return 2
    areas = {a.strip().split('-')[-1].upper() for a in (args.areas or '').split(',') if a.strip()}
    if args.limit:
        parks = parks[:args.limit]
    pj, lj, sj, rj = (os.path.join(out, n) for n in ('parcels.json', 'parcel-layers.json', 'state.json', 'report.json'))
    resume = args.resume and os.path.exists(sj)
    result = json.load(open(pj)) if resume and os.path.exists(pj) else {}
    layers = json.load(open(lj)) if resume and os.path.exists(lj) else {}
    state = json.load(open(sj)) if resume else {'done': {}}
    report = json.load(open(rj)) if resume and os.path.exists(rj) else {'parks': {}, 'counties': {}}
    finder = Finder(web, log)
    no_layer = {}          # fips -> why (this run)
    left = 0
    for pk in parks:
        ref = pk['ref']
        if ref in state['done']:
            continue
        if time.time() > deadline:
            left += 1
            continue
        if pk.get('bad'):
            report['parks'][ref] = {'status': 'bad row', 'why': 'needs ref, lat and lon'}
            state['done'][ref] = read_date
            continue
        try:
            row = do_park(pk, web, finder, known, layers, no_layer, read_date, args, areas, log)
            if row is not None:
                result[ref] = row
                report['parks'][ref] = {'status': 'ok' if row.get('layer_url') else 'no layer', 'why': row['why']}
            else:
                report['parks'][ref] = {'status': 'skipped', 'why': 'outside --areas'}
        except Exception as e:  # noqa: BLE001  (one bad park never stops the run)
            report['parks'][ref] = {'status': 'failed', 'why': f'{type(e).__name__}: {e}'}
            log(f'  {ref}: failed: {e}')
        state['done'][ref] = read_date
        for f, d in ((pj, result), (lj, layers), (sj, state)):
            json.dump(d, open(f, 'w'), indent=1)
    for fips, why in no_layer.items():
        report['counties'][fips] = {'layer_url': None, 'why': why}
    for fips, v in layers.items():
        report['counties'][fips] = {'layer_url': v['layer_url'], 'why': v['why']}
    report['read_date'] = read_date
    report['requests'] = web.stats
    report['blocked_hosts'] = dict(sorted({**report.get('blocked_hosts', {}), **web.blocked}.items()))
    report['left'] = left
    report['owner_names'] = args.owner_names
    for f, d in ((pj, result), (lj, layers), (sj, state), (rj, report)):
        json.dump(d, open(f, 'w'), indent=1)
    return 3 if left else 0


def do_park(pk, web, finder, known, layers, no_layer, read_date, args, areas, log):
    ref, lat, lon = pk['ref'], pk['lat'], pk['lon']
    cty, cu, cst = county_at(web, lat, lon)
    if not cty:
        return {'county': None, 'layer_url': None, 'owner': None, 'owner_type': 'unknown', 'parcel_id': None,
                'acres': None, 'same_owner_parcels': [], 'source_url': cu, 'read_date': read_date,
                'why': f'the Census county map did not answer for the pin ({cst}).'}
    postal = STATES.get(cty['state'], ('??',))[0]
    if areas and postal not in areas:
        return None
    fips = pk.get('county_fips') or cty['fips']
    county = f"{cty['name']}, {postal} ({fips})"
    log(f'{ref} {pk.get("name", "")}: {county}')
    why = []
    L = feats = how = None
    tried = []
    # 1. a layer we already know for this county (--known, or found earlier in this run)
    for src, url in (('the --known list', known.get(fips)), ('found earlier in this run', (layers.get(fips) or {}).get('layer_url'))):
        if url and not L:
            L, feats, how = finder.verify(url, lat, lon)
            if L:
                why.append(f'parcel layer from {src}')
            else:
                tried.append(f'{url}: {how}')
    if not L and fips in CLUB_SKIP:
        no_layer[fips] = CLUB_SKIP[fips] + ('; ' + '; '.join(tried) if tried else '')
    # 2. the state's own statewide parcel service
    if not L and cty['state'] in STATEWIDE and fips not in CLUB_SKIP:
        url, label = STATEWIDE[cty['state']]
        L, feats, how = finder.verify(url, lat, lon)
        if L:
            why.append(f'parcel layer = {label}')
            layers[fips] = {'layer_url': url, 'county': county, 'source_url': url, 'read_date': read_date,
                            'why': f'{label}; it answered at a pin in this county'}
        else:
            tried.append(f'{url}: {how}')
    # 3. search (ArcGIS Online / Hub) for the county name + parcels, government publishers only
    if not L and fips not in no_layer:
        place = place_at(web, lat, lon)
        cands, roots = finder.search(cty, place, lat, lon)
        n = 0
        for score, url, it, cwhy, su in cands:
            if n >= args.max_tries:
                break
            for lu in finder.layers_of(url):
                n += 1
                L, feats, how = finder.verify(lu, lat, lon)
                if L:
                    why.append(f'parcel layer found by searching ArcGIS Online for "{cty["base"]} County parcels": '
                               f'"{it.get("title")}" ({cwhy})')
                    layers[fips] = {'layer_url': lu, 'county': county, 'source_url': su, 'read_date': read_date,
                                    'why': f'"{it.get("title")}", {cwhy}; the pin of {ref} falls on one of its parcels'}
                    break
                tried.append(f'{lu}: {how}')
            if L:
                break
        # 4. the county / city government's own server (or ArcGIS organisation): its list of services
        if not L:
            for root, rwhy in list(roots.items())[:4]:
                for su in finder.scan_root(root)[:4]:
                    for lu in finder.layers_of(su):
                        L, feats, how = finder.verify(lu, lat, lon)
                        if L:
                            why.append(f'parcel layer found in the service list of {root} ({rwhy})')
                            layers[fips] = {'layer_url': lu, 'county': county, 'source_url': root, 'read_date': read_date,
                                            'why': f'listed by the government server {root} ({rwhy}); the pin of {ref} '
                                                   f'falls on one of its parcels'}
                            break
                        tried.append(f'{lu}: {how}')
                    if L:
                        break
                if L:
                    break
        if not L:
            zs = finder.zoning_skipped
            if zs:
                tried.insert(0, f'{len(zs)} zoning layer(s) skipped because zoning is not ownership ({"; ".join(zs[:2])})')
            no_layer[fips] = (f'searched ArcGIS Online ({len(cands)} government candidate(s) covering the pin, '
                              f'{len(roots)} government server(s) listed); '
                              + ('; '.join(tried[:4]) if tried else 'none answered'))
    if not L:
        return {'county': county, 'layer_url': None, 'owner': None, 'owner_type': 'unknown', 'parcel_id': None,
                'acres': None, 'same_owner_parcels': [], 'source_url': cu, 'read_date': read_date,
                'why': 'no government parcel layer found for this county: ' + (no_layer.get(fips) or '; '.join(tried) or 'none') + '.'}
    # the parcel under the pin (if several overlap, the smallest one)
    best = None
    for f in feats:
        a = f.get('attributes') or {}
        ac = acres_of(L, a, f.get('geometry'), lat)
        if best is None or (ac[0] or 1e12) < (best[1][0] or 1e12):
            best = (f, ac)
    f, (acres, acres_how) = best
    a = f.get('attributes') or {}
    owner = clean(attr(a, L.owner_f)) or (clean(attr(a, L.alias.get(L.owner_f))) if L.owner_f else None)
    pid = clean(attr(a, L.pid_f)) if L.pid_f else None
    if pid is None and L.pid_f:
        pid = clean(attr(a, L.alias.get(L.pid_f)))
    otype, owhy = owner_type(owner)
    if not L.owner_f:
        owhy = 'this county map has no owner field'
    same = []
    if owner and L.owner_f:
        s = same_owner(web, L, owner, lon, lat, pid)
        if s is None:
            why.append('the same-owner search did not answer')
        else:
            same = s
    near_gov = []
    if otype != 'government' and L.owner_f:
        near_gov = near_government(web, L, lon, lat, pid)
        if near_gov:
            why.append(f'the pin\'s own parcel is not a government\'s, but {len(near_gov)} government-owned parcel(s) '
                       f'lie within 300 m (nearest {near_gov[0]["dist_m"]} m): the pin may sit just off the park')
        if args.owner_names == 'none':
            for x in near_gov:
                x['owner'] = None
    show = args.owner_names == 'gov' and otype == 'government'     # no option ever shows a private name
    why.append(f'asked at the pin ({how}); parcel {pid if pid is not None else "(no id field)"}; owner type '
               f'{otype} because {owhy}; acres: {acres_how}')
    if same:
        why.append(f'{len(same)} more parcel(s) with the same owner name within 1 km')
    shown = owner if show else ('private' if otype == 'private' else None)
    row = {'county': county, 'layer_url': L.url, 'owner': shown, 'owner_type': otype,
           'parcel_id': pid, 'acres': acres, 'same_owner_parcels': same, 'why': '; '.join(why) + '.',
           'source_url': (L.service() + '/identify') if how == 'identify' else (L.url + '/query'), 'read_date': read_date}
    if near_gov:
        row['nearby_government_parcels'] = near_gov
    if owner and not show:
        row['owner_withheld'] = True
        row['why'] += (' The owner is written only as "private" (club rule 9: no names of private owners).'
                       if otype == 'private' else ' The owner name is not written (club rule 9: only government names are written).')
    return row


# ------------------------------------------------------------------ self test (no network)
class FakeWeb(Polite):
    def __init__(self, routes):
        super().__init__(cache=None, gap=0)
        self.routes = routes

    def _raw(self, url, method='GET', data=None, headers=None):
        self.stats['requests'] += 1
        from urllib.parse import unquote_plus
        u = unquote_plus(url)
        for r in self.routes:
            if all(m in u for m in r['match']):
                return 200, {}, open(os.path.join(HERE, 'tests', r['file']), 'rb').read(), url
        return 404, {}, b'', url


def selftest():
    import tempfile, shutil
    T = os.path.join(HERE, 'tests')
    routes = json.load(open(os.path.join(T, 'web.json')))['routes']
    tmp = tempfile.mkdtemp(prefix='kpc_parcels_test_')
    try:
        a = argparse.Namespace(parks=os.path.join(T, 'parks.json'), known=os.path.join(T, 'known.json'), out=tmp,
                               cache=None, max_minutes=5, resume=False, limit=0, areas='', quiet=True,
                               owner_names='gov', max_tries=6)
        code = run(a, web=FakeWeb(routes))
        ok = code == 0
        got = json.load(open(os.path.join(tmp, 'parcels.json')))
        exp = json.load(open(os.path.join(T, 'expected', 'parcels.json')))
        for d in (got, exp):
            for v in d.values():
                v['read_date'] = 'X'
        if got != exp:
            ok = False
            print('parcels.json differs from tests/expected/parcels.json:')
            print(json.dumps(got, indent=1)[:3000])
        txt = open(os.path.join(tmp, 'parcels.json')).read() + open(os.path.join(tmp, 'parcel-layers.json')).read()
        if 'K4TEST PRIVATE PERSON' in txt.upper():
            ok = False
            print('a private owner name was written')
        for name, want in (('CITY OF K4TEST', 'government'), ('K4TEST COUNTY FISCAL COURT', 'government'),
                           ('SMITH JOHN A', 'private'), ('ACME HOLDINGS LLC', 'private'), ('', 'unknown'),
                           ('COMMONWEALTH OF KENTUCKY', 'government'), ('TEXAS HISTORICAL COMMISSION', 'government'),
                           # club decision, Oct 31: agency phrases, with punctuation and '&' variants
                           ('WEST VIRGINIA DIVISION OF NATURAL RESOURCES', 'government'),
                           ('W.VA. DIV. OF NAT. RES.', 'government'),
                           ('MISSOURI DEPARTMENT OF CONSERVATION', 'government'), ('MO DEPT. OF CONSERVATION', 'government'),
                           ('U.S. FISH & WILDLIFE', 'government'), ('FISH&WILDLIFE SVC', 'government'),
                           ('PENNSYLVANIA GAME COMMISSION', 'government'), ('PA GAME COMMISSN', 'government'),
                           ('SOUTHWEST FLORIDA WATER MANAGEMENT DISTRICT', 'government'),
                           ('S.F.W.M.D. WATER MANAGEMENT DIST', 'government'),
                           ('GRAND RIVER CONSERVATION AUTHORITY', 'government'),
                           ('TOWNSHIP PARKS & RECREATION', 'government'), ('PARKS AND RECREATION BOARD', 'government'),
                           # club decision, Oct 31 (round 3): NATURAL RESOURCES + a state word, misspellings allowed
                           ('WEST VIRGINIA DIVISON OF NATURAL RESOURCES', 'government'),
                           ('WEST VIRGINIA DIVSISION OF NATURAL RESOURCES', 'government'),
                           ('WEST VIRGININA DIV OF NATUARL RESOURSES', 'government'),
                           ('ONTARIO MINISTRY OF NATURAL RESOURCES', 'government'),
                           ('TEXAS NATURAL RESOURCES LLC', 'private')):
            if owner_type(name)[0] != want:
                ok = False
                print(f'owner type of "{name}" should be {want}, got {owner_type(name)[0]}')
        for name, want in (('WEST VIRGININA DIVSISION OF NATURAL RESOURCES', 'WEST VIRGINIA'),
                           ('W VA DIV OF NAT RES', 'WEST VIRGINIA'), ('VIRGINIA DEPT OF NATURAL RESOURCES', 'VIRGINIA'),
                           ('NORTH CAROLINA DIVISION OF NATRUAL RESOURCES', 'NORTH CAROLINA'),
                           ('FORKS OF COAL STATE NATIONAL ETAL', None), ('NATURAL RESOURCES CONSERVATION SERVICE', None)):
            if nr_agency(name) != want:
                ok = False
                print(f'nr_agency("{name}") should be {want}, got {nr_agency(name)}')
        if not banned('https://overpass-api.de/api') or banned('https://storage.googleapis.com/x.zip'):
            ok = False
            print('banned-source check wrong')
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    for m in polite_selftest():
        ok = False
        print(m)
    for t in ('Warren County City County Planning Commission Zoning Parcels', 'CCPC_Zoning', 'Zone Districts'):
        if not ZONING.search(t):
            ok = False
            print(f'"{t}" should count as a zoning layer')
    for t in ('Parcels', 'Hardin_Parcels_08_11_22', 'Amazon Parcels', 'Ozone'):
        if ZONING.search(t):
            ok = False
            print(f'"{t}" should not count as a zoning layer')
    if '21227' not in CLUB_SKIP or not all(NOT_OWNERSHIP.search(t) for t in ('AssessmentForms_gdb', 'ATC45Parcel')) \
            or NOT_OWNERSHIP.search('PVA Parcels'):
        ok = False
        print('Warren County KY must be skipped, and damage-assessment layers are not ownership')
    zl = Finder(FakeWeb([]), lambda *a: None).verify(
        'https://webgis.bgky.org/server/rest/services/CCPC/CCPC_Zoning/FeatureServer/0', 37.0, -86.4)
    if zl[0] is not None or 'zoning' not in zl[2]:
        ok = False
        print('a zoning layer was accepted as a parcel source')
    try:
        import contextlib, io
        with contextlib.redirect_stderr(io.StringIO()):
            main(['--parks', 'x', '--out', 'y', '--owner-names', 'all'])
        ok = False
        print('--owner-names all must not exist')
    except SystemExit:
        pass
    print('PASS' if ok else 'FAIL')
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description='KPC county land-owner finder (T4)')
    ap.add_argument('--parks', '--in', dest='parks', help='[{ref, name, lat, lon, county_fips?}] (JSON or CSV)')
    ap.add_argument('--known', help='{county_fips: layer_url} (may be missing or empty)')
    ap.add_argument('--out', help='output folder')
    ap.add_argument('--cache', help='download cache folder (public catalogue replies only, never parcel replies)')
    ap.add_argument('--max-minutes', type=float, default=50)
    ap.add_argument('--resume', action='store_true')
    ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--areas', help='only pins in these states, e.g. US-KY,US-TX')
    ap.add_argument('--owner-names', choices=('gov', 'none'), default='gov',
                    help='gov (default): write the owner name only when it is a government body; none: write no '
                         'government names either. A private owner is always written only as "private".')
    ap.add_argument('--no-owner-names', action='store_const', const='none', dest='owner_names', help='same as --owner-names none')
    ap.add_argument('--max-tries', type=int, default=6, help='layers to try per county from the search')
    ap.add_argument('--quiet', action='store_true')
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if not args.parks or not args.out:
        ap.print_usage(sys.stderr)
        print('bad input: --parks and --out are needed', file=sys.stderr)
        return 2
    return run(args)


if __name__ == '__main__':
    sys.exit(main())
