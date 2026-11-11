#!/usr/bin/env python3
"""KPC European protected-area service finder (T6, kpc_inspire).

For each European country, find the government's own protected-area services (WFS, OGC API, ArcGIS) and
downloads in the public open-data catalogues, and open each link once to see if it works. It decides nothing.

  python kpc_inspire.py --areas AT,DE,ES --out out/
  python kpc_inspire.py --selftest

Catalogues read:
  1. data.europa.eu (the EU open-data portal; it took over the INSPIRE Geoportal's harvest when that closed on
     1 Jul 2026): its SPARQL endpoint, asked with POST to https://data.europa.eu/sparql (robots.txt allows that
     path; it forbids the GET search pages /*search?* and /*?query=*).
  2. the country's national INSPIRE catalogue (CSW), from a short built-in list, when it answers.
Out: <out>/inspire.json  {CC: [{title, publisher, licence, date, links: [{url, kind, opens, layers}],
                              source_url, read_date, why, catalogue}],
                          "EU": [... the EEA Natura 2000 / CDDA compilations, each with eu_compilation: true]}
     <out>/report.json, <out>/state.json (for --resume)
Exit: 0 all done, 3 time ran out (run again with --resume), 2 bad input, anything else = a crash.
"""
from xml.sax.saxutils import escape as xml_escape
import argparse, csv, hashlib, json, os, re, sys, time
import xml.etree.ElementTree as ET
from datetime import datetime
from urllib.parse import urlparse, urlencode, quote, parse_qsl, urlunparse

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
    return problems
# ---------------------------------------------------------------- end of polite web reader

HERE = os.path.dirname(os.path.abspath(__file__))
SPARQL = 'https://data.europa.eu/sparql'
DATASET_PAGE = 'https://data.europa.eu/data/datasets/'

# country: (ISO3 used by the EU country list, languages)
COUNTRIES = {
    'AT': ('AUT', ['de']), 'BE': ('BEL', ['nl', 'fr', 'de']), 'BG': ('BGR', ['bg']), 'HR': ('HRV', ['hr']),
    'CY': ('CYP', ['el']), 'CZ': ('CZE', ['cs']), 'DK': ('DNK', ['da']), 'EE': ('EST', ['et']),
    'FI': ('FIN', ['fi', 'sv']), 'FR': ('FRA', ['fr']), 'DE': ('DEU', ['de']), 'GR': ('GRC', ['el']),
    'HU': ('HUN', ['hu']), 'IE': ('IRL', ['ga']), 'IT': ('ITA', ['it']), 'LV': ('LVA', ['lv']),
    'LT': ('LTU', ['lt']), 'LU': ('LUX', ['fr', 'de']), 'MT': ('MLT', []), 'NL': ('NLD', ['nl']),
    'PL': ('POL', ['pl']), 'PT': ('PRT', ['pt']), 'RO': ('ROU', ['ro']), 'SK': ('SVK', ['sk']),
    'SI': ('SVN', ['sl']), 'ES': ('ESP', ['es', 'ca', 'eu', 'gl']), 'SE': ('SWE', ['sv']),
    'NO': ('NOR', ['no']), 'IS': ('ISL', ['is']), 'LI': ('LIE', ['de']), 'CH': ('CHE', ['de', 'fr', 'it']),
}
# words for "protected area" (and the main kinds) in each language; English and Natura 2000 are always added
WORDS = {
    'en': ['protected site', 'protected area', 'nature reserve', 'national park', 'natura 2000', 'conservation area',
           'special area of conservation', 'special protection area', 'nature conservation', 'cdda',
           'designated areas'],
    'de': ['schutzgebiet', 'naturschutz', 'nationalpark', 'naturpark', 'biosphärenreservat', 'natura 2000',
           'europaschutzgebiet', 'ffh-gebiet', 'vogelschutzgebiet', 'naturdenkmal'],
    'es': ['espacios naturales protegidos', 'espacio natural protegido', 'espacios protegidos', 'áreas protegidas',
           'zonas protegidas', 'parque nacional', 'parques nacionales', 'parque natural', 'reserva natural',
           'red natura', 'lugares protegidos', 'zepa', 'lic '],
    'ca': ['espais naturals protegits', 'espais protegits', "espais d'interès natural", 'parc natural'],
    'eu': ['babestutako', 'natura sarea'],
    'gl': ['espazos naturais protexidos', 'espazos protexidos'],
    'fr': ['aires protégées', 'aire protégée', 'espaces protégés', 'espace naturel protégé', 'parc national',
           'parc naturel', 'réserve naturelle', 'sites protégés', 'zones protégées'],
    'nl': ['beschermde gebieden', 'beschermde natuur', 'natuurgebied', 'nationaal park', 'beschermde sites'],
    'it': ['aree protette', 'area protetta', 'parco nazionale', 'parchi', 'riserva naturale', 'siti protetti'],
    'pl': ['obszary chronione', 'formy ochrony przyrody', 'park narodowy', 'park krajobrazowy', 'rezerwat'],
    'pt': ['áreas protegidas', 'área protegida', 'rede natura', 'sítios protegidos', 'parque natural'],
    'cs': ['chráněná území', 'zvláště chráněn', 'národní park', 'chráněné krajinné'],
    'sk': ['chránené územia', 'chránené územie', 'národný park', 'chránené vtáčie'],
    'hu': ['védett természeti', 'védett terület', 'nemzeti park', 'természetvédelmi'],
    'ro': ['arii protejate', 'arii naturale protejate', 'arie protejată', 'parc național', 'parc natural'],
    'bg': ['защитени територии', 'защитени зони', 'защитена територия'],
    'el': ['προστατευόμεν', 'περιοχές natura'],
    'hr': ['zaštićena područja', 'zaštićeno područje', 'nacionalni park', 'park prirode'],
    'sl': ['zavarovana območja', 'zavarovano območje', 'naravne vrednote'],
    'da': ['beskyttede områder', 'beskyttet natur', 'fredede', 'fredning', 'nationalpark', 'habitatområde'],
    'sv': ['skyddade områden', 'skyddad natur', 'naturreservat', 'nationalpark', 'naturvårdsområde'],
    'fi': ['suojelualue', 'luonnonsuojelualue', 'kansallispuisto', 'suojellut'],
    'et': ['kaitsealad', 'kaitseala', 'kaitstavad loodusobjektid'],
    'lv': ['aizsargājamās', 'īpaši aizsargājamās dabas teritorijas'],
    'lt': ['saugomos teritorijos', 'saugoma teritorija'],
    'no': ['verneområde', 'verneområder', 'naturvern', 'nasjonalpark'],
    'is': ['friðlýst', 'verndarsvæði'],
    'ga': ['protected sites', 'láithreáin chosanta'],
}
# national INSPIRE catalogues (CSW 2.0.2) known to the club; each run checks whether they answer
NATIONAL_CSW = {
    'AT': 'https://geometadatensuche.inspire.gv.at/metadatensuche/srv/ger/csw',
    'DE': 'https://gdk.gdi-de.org/gdi-de/srv/ger/csw',
    'ES': 'https://www.idee.es/csw-codsi-idee/srv/spa/csw',
    'NL': 'https://nationaalgeoregister.nl/geonetwork/srv/dut/csw',
    'BE': 'https://metadata.vlaanderen.be/srv/dut/csw',
    'CZ': 'https://micka.cenia.cz/csw/',
    'DK': 'https://geodata-info.dk/srv/dan/csw',
    'FI': 'https://paikkatietohakemisto.fi/geonetwork/srv/eng/csw',
    'IT': 'https://geodati.gov.it/RNDT/csw',
    'PT': 'https://snig.dgterritorio.gov.pt/rndg/srv/por/csw',
    'SE': 'https://www.geodata.se/geodataportalen/srv/eng/csw',
    'NO': 'https://www.geonorge.no/geonetwork/srv/nor/csw',
    'CH': 'https://www.geocat.ch/geonetwork/srv/eng/csw',
}
CSW_WORDS = {'AT': ['Schutzgebiet'], 'DE': ['Schutzgebiet'], 'ES': ['espacios naturales protegidos', 'red natura'],
             'NL': ['beschermde gebieden', 'Natura 2000'], 'BE': ['beschermde gebieden'], 'CZ': ['chráněná území'],
             'DK': ['beskyttede områder', 'Natura 2000'], 'FI': ['suojelualue'], 'IT': ['aree protette'],
             'PT': ['áreas protegidas'], 'SE': ['skyddade områden', 'naturreservat'], 'NO': ['verneområder'],
             'CH': ['Schutzgebiet']}
EU_BODY = re.compile(r'european environment agency|\beea\b|eea\.europa\.eu|european commission|joint research centre',
                     re.I)
EU_CATALOGUE = 'eea-sdi'
EU_NAME = re.compile(r'natura ?2000|\bcdda\b|common database on designated areas|nationally designated areas', re.I)
NOT_AREA = re.compile(r'\b(report|bericht|informe|rapport|statisti|budget|haushalt|presupuesto|förder|subvenc|'
                      r'ausgaben|kosten|besucher|visitors|monitoring of|stellungnahme|press|noise|lärm|wasserschutz|'
                      r'trinkwasser|grundwasser|hochwasser|überschwemmung|inundación|lawinen|wasserschutzgebiet|'
                      r'heilquellen|quellschutz|trinkwasserschutz|flood|water protection)\b', re.I)


def today():
    return datetime.now().strftime('%Y-%m-%d')


def ln(tag):
    return tag.rsplit('}', 1)[-1]


def link_kind(url, fmt=''):
    """wfs | ogcapi | arcgis | download | wms | None (a web page), from the address and the catalogue's format."""
    u, f = url.lower(), (fmt or '').lower()
    q = dict((k.lower(), v.lower()) for k, v in parse_qsl(urlparse(url).query))
    if q.get('service') == 'wfs' or 'wfs' in f or re.search(r'/wfs\b|_wfs\b|wfs\?|/ows/services/.*wfs', u):
        return 'wfs'
    if q.get('service') in ('wms', 'wmts') or re.search(r'\bwms|wmts', f) or re.search(r'/wms\b|_wms\b|wms\?|wmts', u):
        return 'wms'
    if re.search(r'/rest/services/', u):
        return 'arcgis'
    if re.search(r'/collections\b|/ogcapi|/ogc/features|ogc ?api|/features/v1', u) or 'ogc_api' in f or 'ogcapi' in f:
        return 'ogcapi'
    if re.search(r'\.(zip|gpkg|geojson|json|shp|gml|kml|kmz|xml|7z|gz)(\?|$)', u) or \
            re.search(r'\b(zip|shp|shapefile|gpkg|geopackage|geojson|gml|kml|esri)\b', f) or \
            re.search(r'atom|download|/files/|downloadservice', u):
        return 'download'
    return None


def kind_from_iri(fmt):
    return fmt.rsplit('/', 1)[-1].replace('_', ' ') if fmt else ''


def caps_url(url, service='WFS'):
    p = urlparse(url)
    q = [(k, v) for k, v in parse_qsl(p.query) if k.lower() not in ('request', 'service', 'version', 'typename',
                                                                     'typenames', 'outputformat', 'acceptversions')]
    q += [('SERVICE', service), ('REQUEST', 'GetCapabilities')]
    return urlunparse(p._replace(query=urlencode(q)))


def base_key(url, kind):
    p = urlparse(url)
    if kind in ('wfs', 'wms'):
        q = [(k.lower(), v) for k, v in parse_qsl(p.query) if k.lower() not in
             ('request', 'service', 'version', 'typename', 'typenames', 'outputformat', 'acceptversions', 'layers')]
        return (p.netloc.lower() + p.path.rstrip('/') + '?' + urlencode(sorted(q))).lower()
    if kind == 'arcgis':
        m = re.match(r'(.*/rest/services/.*?/(MapServer|FeatureServer))', url, re.I)
        return (m.group(1) if m else url).lower()
    if kind == 'ogcapi':
        return (p.netloc + re.sub(r'/collections.*$', '', p.path)).lower()
    return url


class Opener:
    """Opens each link once: WFS GetCapabilities (feature types), OGC API /collections, ArcGIS ?f=json (layers),
    a download's first bytes."""
    def __init__(self, web):
        self.web = web
        self.done = {}

    def _fail(self, what, st, url):
        """A link that does not open. A 403 is accepted as it is (club decision, Oct 31): 'blocked from here'."""
        if st == 403:
            k = self.web._block_key(url)
            return False, [], f'blocked from here (403): {self.web.blocked.get(k) or "403 Forbidden on " + url}'
        return False, [], f'{what} -> {st}'

    def open(self, url, kind):
        key = (kind, base_key(url, kind))
        if key not in self.done:
            try:
                self.done[key] = getattr(self, '_' + kind)(url)
            except Exception as e:                       # one bad link never stops the run
                self.done[key] = (False, [], f'could not read: {type(e).__name__}')
        return self.done[key]

    def _wfs(self, url):
        cu = caps_url(url)
        st, hd, body, fin = self.web.get(cu)
        if st != 200:
            return self._fail('GetCapabilities', st, cu)
        try:
            root = ET.fromstring(body)
        except ET.ParseError:
            return False, [], 'GetCapabilities is not XML'
        if 'exception' in ln(root.tag).lower():
            return False, [], 'GetCapabilities answered with an error'
        names = []
        for ft in root.iter():
            if ln(ft.tag) == 'FeatureType':
                nm = tt = None
                for c in ft:
                    if ln(c.tag) == 'Name':
                        nm = (c.text or '').strip()
                    elif ln(c.tag) == 'Title':
                        tt = (c.text or '').strip()
                if nm:
                    names.append(nm if not tt or tt == nm else f'{nm} ({tt})')
        if not names:
            return False, [], 'GetCapabilities lists no feature types'
        return True, names[:40], f'GetCapabilities {cu} lists {len(names)} feature type(s)'

    def _wms(self, url):
        return None, [], 'a picture service (WMS), not opened: it has no outlines to read'

    def _ogcapi(self, url):
        p = urlparse(url)
        path = re.sub(r'/collections.*$', '', p.path).rstrip('/')
        cu = urlunparse(p._replace(path=path + '/collections', query='f=json'))
        st, hd, body, fin = self.web.get(cu, headers={'Accept': 'application/json'})
        if st != 200:
            return self._fail('/collections', st, cu)
        try:
            d = json.loads(body)
        except ValueError:
            return False, [], '/collections is not JSON'
        names = [c.get('id') + (f" ({c.get('title')})" if c.get('title') and c.get('title') != c.get('id') else '')
                 for c in d.get('collections', []) if c.get('id')]
        return bool(names), names[:40], f'{cu} lists {len(names)} collection(s)'

    def _arcgis(self, url):
        m = re.match(r'(.*/rest/services/.*?/(MapServer|FeatureServer))', url, re.I)
        su = m.group(1) if m else url.split('?')[0]
        st, hd, body, fin = self.web.get(su + '?f=json')
        if st != 200:
            return self._fail(f'{su}?f=json', st, su + '?f=json')
        try:
            d = json.loads(body)
        except ValueError:
            return False, [], 'not JSON'
        if d.get('error'):
            return False, [], f"error {d['error'].get('code')}"
        names = [f"{l.get('id')}: {l.get('name')}" for l in d.get('layers', [])]
        return bool(names), names[:40], f'{su}?f=json lists {len(names)} layer(s)'

    def _download(self, url):
        old = self.web.max_bytes
        self.web.max_bytes = 200_000
        try:
            st, hd, body, fin = self.web.get(url, headers={'Range': 'bytes=0-65535'}, nocache=True)
        finally:
            self.web.max_bytes = old
        if st not in (200, 206):
            return self._fail('download', st, url)
        ct = (hd.get('Content-Type') or hd.get('content-type') or '').lower()
        head = body[:600].lower()
        if 'html' in ct or head.lstrip().startswith(b'<!doctype html') or head.lstrip().startswith(b'<html'):
            return False, [], 'the address gives a web page, not a file'
        layers = []
        if b'<feed' in head:     # an INSPIRE Atom download feed: the entries name the files
            try:
                root = ET.fromstring(body)
                layers = [(e.findtext('{http://www.w3.org/2005/Atom}title') or '').strip()
                          for e in root.findall('{http://www.w3.org/2005/Atom}entry')][:40]
            except ET.ParseError:
                pass
        size = hd.get('Content-Range', '').split('/')[-1] or hd.get('Content-Length', '')
        return True, layers, f'the file starts to download ({ct or "no type"}{", " + size + " bytes" if size else ""})'


def sparql(web, q):
    st, hd, body, fin = web.get(SPARQL, method='POST', data={'query': q},
                                headers={'Accept': 'application/sparql-results+json'})
    if st != 200:
        return None, st
    if str(hd.get('X-SQL-State') or hd.get('x-sql-state') or '').upper() == 'S1TAT':
        return None, 'partial answer (the server ran out of time)'
    try:
        return json.loads(body)['results']['bindings'], 200
    except (ValueError, KeyError):
        return None, 'not JSON'


def sq(s):
    return s.replace('\\', '\\\\').replace('"', '\\"')


# words for the catalogue's full-text index (whole words; a trailing * = any ending, at least 4 letters before it)
TEXT_WORDS = {
    'de': ['schutzgebiet*', 'naturschutzgebiet*', 'landschaftsschutzgebiet*', 'vogelschutzgebiet*',
           'europaschutzgebiet*', 'nationalpark*', 'naturpark*', 'biosphärenreservat*', 'ffh gebiet*', 'natura 2000'],
    'es': ['espacios naturales protegidos', 'espacio natural protegido', 'espacios protegidos', 'áreas protegidas',
           'zonas protegidas', 'parque nacional', 'parques nacionales', 'parque natural', 'parques naturales',
           'reserva natural', 'red natura', 'lugares de importancia comunitaria', 'zepa'],
    'ca': ['espais naturals protegits', 'espais protegits', 'parc natural'],
    'eu': ['natura sarea'], 'gl': ['espazos naturais protexidos'],
    'fr': ['aires protégées', 'espaces protégés', 'espaces naturels protégés', 'parc national', 'parcs nationaux',
           'parc naturel', 'réserve naturelle', 'réserves naturelles', 'sites protégés', 'natura 2000'],
    'nl': ['beschermde gebieden', 'beschermde natuur', 'nationaal park', 'nationale parken', 'natura 2000'],
    'it': ['aree protette', 'area protetta', 'parco nazionale', 'parchi nazionali', 'riserva naturale',
           'riserve naturali', 'siti protetti', 'natura 2000'],
    'pl': ['obszary chronione', 'formy ochrony przyrody', 'park narodowy', 'parki narodowe', 'park krajobrazowy',
           'rezerwat*', 'natura 2000'],
    'pt': ['áreas protegidas', 'área protegida', 'rede natura', 'sítios protegidos', 'parque natural'],
    'cs': ['chráněná území', 'zvláště chráněná území', 'národní park', 'chráněná krajinná oblast', 'natura 2000'],
    'sk': ['chránené územia', 'chránené územie', 'národný park', 'natura 2000'],
    'hu': ['védett természeti területek', 'védett területek', 'nemzeti park', 'natura 2000'],
    'ro': ['arii protejate', 'arii naturale protejate', 'parc național', 'parc natural', 'natura 2000'],
    'bg': ['защитени територии', 'защитени зони', 'натура 2000'],
    'el': ['προστατευόμενες περιοχές', 'natura 2000'],
    'hr': ['zaštićena područja', 'zaštićeno područje', 'nacionalni park', 'park prirode', 'natura 2000'],
    'sl': ['zavarovana območja', 'zavarovano območje', 'natura 2000'],
    'da': ['beskyttede områder', 'fredede områder', 'fredning*', 'nationalpark*', 'natura 2000'],
    'sv': ['skyddade områden', 'naturreservat*', 'nationalpark*', 'natura 2000'],
    'fi': ['suojelualue*', 'luonnonsuojelualue*', 'kansallispuisto*', 'natura 2000'],
    'et': ['kaitsealad', 'kaitseala*', 'natura 2000'], 'lv': ['aizsargājamās dabas teritorijas', 'natura 2000'],
    'lt': ['saugomos teritorijos', 'natura 2000'], 'no': ['verneområde*', 'naturvern*', 'nasjonalpark*'],
    'is': ['friðlýst*', 'verndarsvæði*'],
    'ga': ['protected sites', 'protected areas', 'special areas of conservation', 'natura 2000'],
    'en': ['protected sites', 'protected areas', 'special areas of conservation', 'nature reserves', 'natura 2000'],
}
PFX = ('PREFIX dcat: <http://www.w3.org/ns/dcat#> PREFIX dct: <http://purl.org/dc/terms/> '
       'PREFIX foaf: <http://xmlns.com/foaf/0.1/> ')


def batched(xs, n):
    for i in range(0, len(xs), n):
        yield xs[i:i + n]


def europa_records(web, cc, log, words):
    """data.europa.eu in three steps that its server answers quickly (one big joined query times out):
    1. its full-text index: datasets whose title has a protected-area word of the country's languages;
    2. which of them sit in a catalogue of this country; 3. publisher, date, licence and links of those."""
    iso3, langs = COUNTRIES[cc]
    tl = [l for l in (langs or [])] + (['en'] if (not langs or 'ga' in langs) else [])
    tw = list(dict.fromkeys(sum((TEXT_WORDS.get(l, []) for l in tl), [])))
    # the portal machine-translates every title into all EU languages (tagged e.g. "de-t-en-t0-mtec"); only titles
    # in the country's own languages as published (plain "de") are searched, else every country's data comes back
    # titles tagged "en" are searched too: some national records carry a German / Spanish title tagged "en"
    # (e.g. Umweltbundesamt's "Schutzgebiete Österreich 2025")
    lang_f = 'FILTER(LANG(?title) IN (' + ', '.join(f'"{l}"' for l in dict.fromkeys(tl + ['en'])) + '))'
    notes, titles = [], {}
    for chunk in batched(tw, 4):
        expr = ' OR '.join('"' + w.replace('"', '') + '"' for w in chunk)
        for page in range(3):
            q = PFX + (f"SELECT DISTINCT ?d ?title WHERE {{ ?d dct:title ?title . ?title bif:contains '{expr}' . "
                       f"?d a dcat:Dataset . {lang_f} }} LIMIT 10000 OFFSET {page * 10000}")
            rows, st = sparql(web, q)
            if rows is None:
                notes.append(f'text search {chunk} -> {st}')
                break
            for r in rows:
                titles.setdefault(r['d']['value'], set()).add(r['title']['value'])
            if len(rows) < 10000:
                break
    cand = [d for d, ts in titles.items() if not NOT_AREA.search(' | '.join(ts))]
    mine, eu = [], []
    n_bad = 0
    for b in batched(cand, 100):
        vals = ' '.join(f'<{d}>' for d in b)
        rows, st = sparql(web, PFX + f'SELECT ?d ?cat ?c WHERE {{ VALUES ?d {{ {vals} }} ?cat dcat:dataset ?d . '
                                     f'OPTIONAL {{ ?cat dct:spatial ?c }} }}')
        if rows is None:
            n_bad += 1
            continue
        mine += [r['d']['value'] for r in rows if r.get('c', {}).get('value', '').endswith('/' + iso3)]
        eu += [r['d']['value'] for r in rows if r['cat']['value'].rstrip('/').endswith('/' + EU_CATALOGUE)
               and EU_NAME.search(' '.join(titles[r['d']['value']]))]
    mine = list(dict.fromkeys(mine))
    eu = [d for d in dict.fromkeys(eu) if d not in mine][:30]
    recs = {d: {'id': d, 'titles': titles[d], 'publisher': None, 'date': None, 'licence': None, 'links': {},
                'eu': d in eu} for d in mine + eu}
    for b in batched(mine + eu, 40):
        vals = ' '.join(f'<{d}>' for d in b)
        q = PFX + (f'SELECT ?d ?pub ?mod ?lic ?url ?fmt WHERE {{ VALUES ?d {{ {vals} }} '
                   f'OPTIONAL {{ ?d dct:publisher ?p . ?p foaf:name ?pub }} OPTIONAL {{ ?d dct:modified ?mod }} '
                   f'OPTIONAL {{ ?d dcat:distribution ?x . ?x dcat:accessURL ?url . OPTIONAL {{ ?x dct:format ?fmt }} '
                   f'OPTIONAL {{ ?x dct:license ?lic }} }} }}')
        rows, st = sparql(web, q)
        if rows is None:
            n_bad += 1
            continue
        for r in rows:
            rec = recs[r['d']['value']]
            if r.get('pub'):
                rec['publisher'] = rec['publisher'] or r['pub']['value']
            if r.get('mod'):
                rec['date'] = max(rec['date'] or '', r['mod']['value'][:10])
            if r.get('lic') and r['lic'].get('type') == 'uri':
                rec['licence'] = rec['licence'] or r['lic']['value']
            if r.get('url'):
                rec['links'].setdefault(r['url']['value'], kind_from_iri(r.get('fmt', {}).get('value', '')))
    notes.insert(0, f'data.europa.eu SPARQL: {len(titles)} dataset(s) in Europe with a protected-area word '
                    f'({", ".join(tw)}), {len(mine)} in a catalogue of {cc}, {len(eu)} in the EEA catalogue' +
                 (f'; {n_bad} batch(es) did not answer' if n_bad else ''))
    return list(recs.values()), '; '.join(notes)


def csw_records(web, cc, log):
    url = NATIONAL_CSW.get(cc)
    if not url:
        return [], 'no national catalogue in the built-in list'
    out, notes = [], []
    for w in CSW_WORDS.get(cc, []):
        p = {'service': 'CSW', 'version': '2.0.2', 'request': 'GetRecords', 'typeNames': 'csw:Record',
             'resultType': 'results', 'elementSetName': 'full', 'outputSchema': 'http://www.opengis.net/cat/csw/2.0.2',
             'constraintLanguage': 'FILTER', 'constraint_language_version': '1.1.0',
             'constraint': ('<Filter xmlns="http://www.opengis.net/ogc"><PropertyIsLike wildCard="*" '
                            'singleChar="_" escapeChar="\\"><PropertyName>AnyText</PropertyName>'
                            f'<Literal>*{xml_escape(w)}*</Literal></PropertyIsLike></Filter>'),
             'maxRecords': '100'}
        u = url + '?' + urlencode(p)
        st, hd, body, fin = web.get(u)
        if st != 200:
            notes.append(f'{url} -> {st}')
            break
        try:
            root = ET.fromstring(body)
        except ET.ParseError:
            notes.append(f'{url}: not XML')
            break
        if 'exception' in ln(root.tag).lower():
            msg = ' '.join(t.strip() for t in root.itertext() if t.strip())[:120]
            notes.append(f'{url}: {msg}')
            break
        n = 0
        for rec in root.iter():
            if ln(rec.tag) != 'Record':
                continue
            n += 1
            r = {'id': None, 'titles': set(), 'publisher': None, 'date': None, 'licence': None, 'links': {},
                 'csw': u}
            for c in rec:
                t, v = ln(c.tag), (c.text or '').strip()
                if t == 'identifier' and v:
                    r['id'] = r['id'] or v
                elif t == 'title' and v:
                    r['titles'].add(v)
                elif t in ('publisher', 'creator') and v:
                    r['publisher'] = r['publisher'] or v
                elif t in ('modified', 'date') and v:
                    r['date'] = r['date'] or v[:10]
                elif t in ('rights', 'license', 'accessRights') and v:
                    r['licence'] = r['licence'] or v[:200]
                elif t in ('URI', 'references') and v.startswith('http'):
                    proto = ' '.join(str(x) for x in c.attrib.values())
                    r['links'].setdefault(v, proto)
            if r['id']:
                out.append(r)
        notes.append(f'{url}: "{w}" -> {n} record(s)')
    return out, '; '.join(notes)


def make_records(raw, cc, words, catalogue, opener, read_date, deadline, max_links, log):
    """Keep datasets with a service or download link; open each link once."""
    rx = re.compile('|'.join(re.escape(w) for w in words), re.I)
    keep = []
    for r in raw:
        title = sorted(r['titles'], key=len)[0] if r['titles'] else ''
        alltitles = ' | '.join(sorted(r['titles']))
        if not rx.search(alltitles) or NOT_AREA.search(alltitles):
            continue
        links = []
        for u, fmt in r['links'].items():
            if not u.startswith('http') or banned(u):
                continue
            k = link_kind(u, fmt)
            if k:
                links.append((u, k))
        if not links:
            continue
        eu = r.get('eu') or (bool(EU_BODY.search(r.get('publisher') or '') or
                                  any('eea.europa.eu' in u for u, k in links)) and bool(EU_NAME.search(alltitles)))
        prio = (0 if any(k == 'wfs' for u, k in links) else 1 if any(k in ('ogcapi', 'arcgis') for u, k in links)
                else 2 if any(k == 'download' for u, k in links) else 3)
        keep.append((prio, title, r, links, eu))
    keep.sort(key=lambda x: (x[0], x[1]))
    out, opened = [], 0
    for prio, title, r, links, eu in keep:
        rows = []
        for u, k in links[:8]:
            if k == 'wms':
                continue
            if time.time() > deadline or opened >= max_links:
                rows.append({'url': u, 'kind': k, 'opens': None, 'layers': [], 'why': 'not opened (link budget used)'})
                continue
            fresh = (k, base_key(u, k)) not in opener.done
            ok, layers, how = opener.open(u, k)
            opened += fresh
            row = {'url': u, 'kind': k, 'opens': ok, 'layers': layers, 'why': how}
            if not ok and str(how).startswith('blocked from here'):
                row['status'] = 'blocked from here'   # kept in the list: the club tries it again from GitHub
            rows.append(row)
        if not rows:
            continue
        src = (DATASET_PAGE + r['id'].rsplit('/', 1)[-1]) if catalogue == 'data.europa.eu' else r.get('csw')
        why = [f'listed in {catalogue} for {cc}' + (f' (record {r["id"]})' if catalogue != 'data.europa.eu' else ''),
               'its title names ' + ', '.join(sorted({m.group(0).lower() for m in rx.finditer(' '.join(r['titles']))}))]
        if eu:
            why.append('in the European Environment Agency\'s catalogue (or published by an EU body) about Natura '
                       '2000 / CDDA: a Europe-wide compilation, not the country\'s own file')
        rec = {'title': title, 'publisher': r.get('publisher'), 'licence': r.get('licence'), 'date': r.get('date'),
               'links': rows, 'source_url': src, 'read_date': read_date, 'why': '; '.join(why) + '.',
               'catalogue': catalogue}
        if eu:
            rec['eu_compilation'] = True
        out.append(rec)
    return out


def run(args, web=None):
    t0 = time.time()
    deadline = t0 + args.max_minutes * 60
    log = (lambda *a: print(*a, flush=True)) if not args.quiet else (lambda *a: None)
    areas = [a.strip().upper().split('-')[-1] for a in (args.areas or ','.join(COUNTRIES)).split(',') if a.strip()]
    bad = [a for a in areas if a not in COUNTRIES]
    if bad:
        print(f'bad input: unknown country code(s) {", ".join(bad)}; known: {", ".join(COUNTRIES)}', file=sys.stderr)
        return 2
    if args.limit:
        areas = areas[:args.limit]
    out = args.out
    os.makedirs(out, exist_ok=True)
    web = web or Polite(cache=args.cache, log=log)
    web.log = log
    read_date = today()
    ij, sj, rj = (os.path.join(out, n) for n in ('inspire.json', 'state.json', 'report.json'))
    resume = args.resume and os.path.exists(sj)
    result = json.load(open(ij)) if resume and os.path.exists(ij) else {}
    state = json.load(open(sj)) if resume else {'done': {}}
    report = json.load(open(rj)) if resume and os.path.exists(rj) else {'countries': {}}
    opener = Opener(web)
    left = 0
    for cc in areas:
        if cc in state['done']:
            continue
        if time.time() > deadline:
            left += 1
            continue
        langs = COUNTRIES[cc][1]
        words = list(dict.fromkeys(sum((WORDS.get(l, []) for l in langs), []) + WORDS['en']))
        log(f'{cc}: searching ({", ".join(langs) or "en"})')
        notes, recs = [], []
        try:
            raw, note = europa_records(web, cc, log, words)
            notes.append(note)
            if raw:
                recs += make_records(raw, cc, words, 'data.europa.eu', opener, read_date, deadline, args.max_links, log)
            raw2, note2 = csw_records(web, cc, log)
            notes.append('national catalogue: ' + note2)
            if raw2:
                seen = {l['url'] for r in recs for l in r['links']}
                more = make_records(raw2, cc, words, 'national catalogue ' + urlparse(NATIONAL_CSW[cc]).hostname,
                                    opener, read_date, deadline, args.max_links, log)
                recs += [r for r in more if not all(l['url'] in seen for l in r['links'])]
        except Exception as e:      # one bad country never stops the run
            notes.append(f'stopped early: {type(e).__name__}: {e}')
        eu = [r for r in recs if r.get('eu_compilation')]
        own = [r for r in recs if not r.get('eu_compilation')]
        # the most useful first: a WFS that opens, then any service that opens, then the rest
        def rank(r):
            ks = [(l['kind'], l['opens']) for l in r['links']]
            return (0 if ('wfs', True) in ks else 1 if any(o for k, o in ks) else 2, r['title'].lower())
        own.sort(key=rank)
        own = own[:args.max_records]
        result[cc] = own
        if eu:
            have = {r['title'] for r in result.get('EU', [])}
            result.setdefault('EU', []).extend(r for r in eu if r['title'] not in have)
        wfs_ok = sum(1 for r in own for l in r['links'] if l['kind'] == 'wfs' and l['opens'])
        report['countries'][cc] = {'records': len(own), 'eu_compilation_records': len(eu),
                                   'wfs_links_that_open': wfs_ok, 'notes': notes, 'read_date': read_date}
        log(f'  {len(own)} record(s), {wfs_ok} WFS link(s) that open; {len(eu)} EU compilation record(s)')
        state['done'][cc] = read_date
        for path, obj in ((ij, result), (sj, state), (rj, report)):
            tmp = path + '.tmp'
            json.dump(obj, open(tmp, 'w'), ensure_ascii=False, indent=1)
            os.replace(tmp, path)
    report['web'] = dict(web.stats)
    report['resting_hosts'] = sorted(web.resting)
    report['blocked_hosts'] = dict(sorted({**report.get('blocked_hosts', {}), **web.blocked}.items()))
    json.dump(report, open(rj, 'w'), ensure_ascii=False, indent=1)
    if left:
        log(f'time is up: {left} countr(ies) left; run again with --resume')
        return 3
    return 0


class FakeWeb(Polite):
    def __init__(self, routes):
        super().__init__(cache=None, gap=0)
        self.routes = routes

    def _raw(self, url, method='GET', data=None, headers=None):
        self.stats['requests'] += 1
        from urllib.parse import unquote_plus
        u = unquote_plus(url) + ' ' + unquote_plus(urlencode(data) if isinstance(data, dict) else str(data or ''))
        for r in self.routes:
            if all(m in u for m in r['match']):
                return r.get('status', 200), r.get('headers', {}), open(os.path.join(HERE, 'tests', r['file']), 'rb').read(), url
        return 404, {}, b'', url


def selftest():
    import tempfile, shutil
    T = os.path.join(HERE, 'tests')
    routes = json.load(open(os.path.join(T, 'web.json')))['routes']
    tmp = tempfile.mkdtemp(prefix='kpc_inspire_test_')
    ok = True
    try:
        a = argparse.Namespace(areas='AT', out=tmp, cache=None, max_minutes=5, resume=False, limit=0, quiet=True,
                               max_links=60, max_records=80)
        code = run(a, web=FakeWeb(routes))
        if code != 0:
            ok = False
            print('exit code', code)
        got = json.load(open(os.path.join(tmp, 'inspire.json')))
        exp = json.load(open(os.path.join(T, 'expected', 'inspire.json')))
        for d in (got, exp):
            for v in d.values():
                for r in v:
                    r['read_date'] = 'X'
        if got != exp:
            ok = False
            print('inspire.json differs from tests/expected/inspire.json:')
            print(json.dumps(got, indent=1, ensure_ascii=False)[:4000])
        for u, k in (('https://x.gv.at/wfs?service=WFS&request=GetCapabilities', 'wfs'),
                     ('https://x.de/arcgis/rest/services/A/MapServer', 'arcgis'),
                     ('https://x.es/ogcapi/collections', 'ogcapi'), ('https://x.es/enp.zip', 'download'),
                     ('https://x.es/wms?service=WMS', 'wms'), ('https://x.es/about.html', None)):
            if link_kind(u) != k:
                ok = False
                print(f'link kind of {u} should be {k}, got {link_kind(u)}')
        if not banned('https://www.protectedplanet.net/en') or not banned('https://overpass-api.de/api'):
            ok = False
            print('banned-source check wrong')
        # Spain's national WFS answers 403 from here (robots.txt too). Nov 7 standing rule: a robots 401/403 is a STOP,
        # so the link is kept, opens=false, and the reason names robots or the block; no data request is read.
        bw = FakeWeb([{'match': ['geoserver.iepnb.es'], 'status': 403, 'file': routes[0]['file']}])
        bo = Opener(bw).open('https://geoserver.iepnb.es/geoserver/ENP/wms?service=WFS&request=GetCapabilities', 'wfs')
        if bo[0] is not False or not any(w in str(bo[2]).lower() for w in ('robots', 'blocked')):
            ok = False
            print('a robots-403 link should be kept closed with a robots/blocked reason, got', bo)
        if bw.stats['requests'] > 1:
            ok = False
            print('a robots-403 host was asked', bw.stats['requests'], 'times (only robots.txt allowed)')
        if not os.path.exists(os.path.join(tmp, 'state.json')):
            ok = False
            print('no state.json')
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    for m in polite_selftest():
        ok = False
        print(m)
    print('PASS' if ok else 'FAIL')
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description='KPC European protected-area service finder (T6)')
    ap.add_argument('--areas', help='country codes, e.g. AT,DE,ES (default: all %d)' % len(COUNTRIES))
    ap.add_argument('--in', dest='inp', help='(optional) a text / CSV file of country codes, one per line')
    ap.add_argument('--out', help='output folder (the tool writes only here)')
    ap.add_argument('--cache', help='download cache folder (public catalogue replies only)')
    ap.add_argument('--max-minutes', type=float, default=50)
    ap.add_argument('--resume', action='store_true', help='carry on from <out>/state.json')
    ap.add_argument('--limit', type=int, default=0, help='only the first N countries')
    ap.add_argument('--max-links', type=int, default=60, help='links opened per country (default 60)')
    ap.add_argument('--max-records', type=int, default=80, help='records kept per country (default 80)')
    ap.add_argument('--quiet', action='store_true')
    ap.add_argument('--selftest', action='store_true', help='run the built-in test (no network) and print PASS / FAIL')
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.out:
        print('bad input: --out is needed', file=sys.stderr)
        return 2
    if a.inp:
        try:
            codes = [l.strip().split(',')[0] for l in open(a.inp, encoding='utf-8') if l.strip() and not l.startswith('#')]
        except OSError as e:
            print(f'bad input: {e}', file=sys.stderr)
            return 2
        a.areas = ','.join(c for c in codes if c.lower() not in ('cc', 'country'))
    return run(a)


if __name__ == '__main__':
    sys.exit(main())
