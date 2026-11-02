#!/usr/bin/env python3
"""KPC agency sitemap reader (T3, kpc_sitemaps).

Reads each agency's own sitemap(s) and lists every map PDF / map image / park page on the site, with the
POTA parks each URL might belong to (all candidates, never one pick). It decides nothing.

  python kpc_sitemaps.py --agencies data/intake/us-agency-maps-index.csv --docs data/docs --areas US-TN --out out/
  python kpc_sitemaps.py --selftest

Out: <out>/sitemaps/<host>.json = {host, read_date, n_urls, maps: [{url, lastmod, refs: [{ref, score}], words}], pages: [...]}
     (exactly the handoff shape; T2 reads it), plus <out>/sitemaps/<host>.sources.json (where each URL came from + why),
     <out>/report.json (one line per host, with a reason when it failed) and <out>/state.json (for --resume).
Exit: 0 all done, 3 time ran out (run again with --resume), 2 bad input, anything else = a crash.
"""
import argparse, csv, glob, gzip, hashlib, io, json, os, re, sys, time, unicodedata
from datetime import datetime
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse, urldefrag, unquote
import xml.etree.ElementTree as ET

import requests

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

HERE = os.path.dirname(os.path.abspath(__file__))
MAP_TOKENS = {'map', 'maps', 'mapping', 'mapbook', 'brochure', 'brochures', 'guide', 'guides', 'trail', 'trails',
              'trailmap', 'trailmaps', 'boundary', 'boundaries', 'atlas'}
MAP_ENDS = ('map', 'maps', 'brochure', 'brochures')


def map_words(url):
    """The words in the address that say map / brochure / guide / trail / boundary / atlas (whole words, so the
    NPS park code 'mapr' or the name 'Mapp' do not count), plus the file kind."""
    p = urlparse(url)
    ws = [w for w in url_words(url) if w in MAP_TOKENS or (len(w) > 4 and w.endswith(MAP_ENDS))]
    m = FILE_EXT.search(unquote(p.path or ''))
    if m:
        ws.append(m.group(1).lower())
    return sorted(set(ws))
FILE_EXT = re.compile(r'\.(pdf|jpe?g|png)$', re.I)
PAGE_EXT = re.compile(r'(\.(html?|php|aspx?|cfm)|/[^./]*)$', re.I)
# words that say nothing about WHICH park a URL is about
GENERIC = set('''state park parks national natural area areas historic historical site sites wildlife management
recreation recreational forest forests refuge the of and at in on for a an to sp nwr nf nra wma nha nhp nhs nm np
battlefield memorial preserve reserve monument center centre conservation tennessee kentucky texas tn ky tx us usa
united states county city wilderness byway seashore parkway scenic route trail trails heritage corridor museum
department dept office www com gov org net html htm php aspx index default page pages files sites content dam
documents document upload uploads images image web pdf jpg jpeg png media visit planyourvisit learn en home
map maps brochure brochures guide guides atlas boundary boundaries'''.split())
WEAK = set('''lake lakes river rivers creek mountain mountains mount mt cove falls fall island islands rock rocks hill hills
spring springs valley gap fort cave caves bay point ridge hollow branch fork bend run pond ponds bluff bluffs knob
north south east west upper lower big little old new great grand'''.split())
PARK_PATH_SEGS = {'parks', 'park', 'state-parks', 'stateparks', 'refuge', 'refuges', 'wma', 'wmas', 'natural-areas',
                  'recarea', 'recreation-areas', 'forests', 'state-natural-areas', 'wildlife-management-areas'}
FOLDER_SEGS = PARK_PATH_SEGS | {'en', 'content', 'visit', 'home', 'us', 'locations', 'places', 'sites', 'lands',
                                'fish-hatchery', 'national-fish-hatchery', 'destinations', 'files', 'uploads',
                                'documents', 'media', 'default', 'images', 'wp-content', 'documentcenter', 'assets',
                                'pdf', 'pdfs', 'download', 'downloads', 'maps', 'map'}


def norm_url(u):
    u = urldefrag((u or '').strip())[0]
    p = urlparse(u)
    host = (p.hostname or '').lower()
    if host.startswith('www.'):
        host = host[4:]
    path = re.sub(r'/+$', '', p.path or '') or '/'
    path = re.sub(r'/index\.(html?|php|aspx?)$', '', path, flags=re.I) or '/'
    return host + path.lower() + (('?' + p.query) if p.query else '')


def tokens(text):
    text = unicodedata.normalize('NFKD', text or '').encode('ascii', 'ignore').decode()
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)            # SavageGulf -> Savage Gulf
    text = re.sub(r'([A-Za-z])(\d)', r'\1 \2', text)
    text = re.sub(r'(\d)([A-Za-z])', r'\1 \2', text)
    text = text.replace('&', ' and ').replace("'", '')
    out = [t for t in re.split(r'[^a-z0-9]+', text.lower()) if t]
    return [{'mt': 'mount', 'ft': 'fort', 'st': 'saint'}.get(t, t) for t in out]


def url_words(url):
    p = urlparse(url)
    return tokens(unquote(p.path or '') + ' ' + unquote(p.query or ''))


class Matcher:
    """Name words of the state's POTA parks -> candidate refs for a URL. Keeps every candidate (max 5)."""
    def __init__(self, parks):
        self.parks = {}
        self.index = {}
        for ref, name in parks.items():
            ws = [w for w in tokens(name) if w not in GENERIC]
            strong = [w for w in ws if w not in WEAK and len(w) > 2]
            weak = [w for w in ws if w in WEAK]
            if not strong and len(weak) < 2:
                continue        # e.g. "Big Lake": too vague to match by words; learned paths still work
            self.parks[ref] = (name, strong, weak)
            for w in (strong or weak):
                self.index.setdefault(w, set()).add(ref)

    def match(self, url):
        words = url_words(url)
        ws = set(words)
        cands = set()
        for w in ws:
            cands |= self.index.get(w, set())
        out = []
        for ref in cands:
            name, strong, weak = self.parks[ref]
            ms = [w for w in strong if w in ws]
            mw = [w for w in weak if w in ws]
            if strong and len(ms) < len(strong) - (1 if len(strong) >= 3 else 0):
                continue
            if not strong and len(mw) < len(weak):
                continue
            denom = len(strong) + 0.5 * len(weak)
            score = (len(ms) + 0.5 * len(mw)) / denom if denom else 0
            seq = strong + weak
            joined = ' '.join(words)
            if len(seq) > 1 and ' '.join(w for w in tokens(name) if w in set(seq)) in joined:
                score += 0.1    # the words appear together, in order
            score = round(min(score, 1.0), 2)
            if score >= 0.5:
                out.append({'ref': ref, 'score': score, '_w': ms + mw})
        out.sort(key=lambda r: (-r['score'], r['ref']))
        return out[:5]


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        for k in ('href', 'src', 'data-src'):
            if a.get(k):
                self.links.append(a[k])


def learn_prefixes(host, urls_by_ref, names=None):
    """From the club's own links on this host (docs page / map links, POTA website), learn which path starts
    belong to which park: e.g. nps.gov /cuga/... -> US-0019, fws.gov /refuge/chickasaw -> US-0533."""
    pref = {}
    templates = set()
    for ref, urls in urls_by_ref.items():
        for u in urls:
            p = urlparse(u)
            if (p.hostname or '').lower().replace('www.', '') != host.replace('www.', ''):
                continue
            segs = [s for s in (p.path or '').lower().split('/') if s]
            if not segs:
                continue
            # the park's own segment = the first one that shares a word with the park's name (fws /refuge/chickasaw),
            # else the first that is not a folder word and not a region code (NPS park codes: /cuga/)
            nw = {w for w in tokens((names or {}).get(ref, '')) if w not in GENERIC and len(w) > 2}
            cand = [i for i, sgm in enumerate(segs) if '.' not in sgm and sgm not in FOLDER_SEGS and set(tokens(sgm)) & nw]
            if not cand:
                # (only when a further folder follows it: /cuga/planyourvisit/maps.htm, not /files/x.pdf)
                cand = [i for i, sgm in enumerate(segs[:2]) if sgm not in FOLDER_SEGS and '.' not in sgm
                        and not re.match(r'^[a-z]?\d+$', sgm) and len(sgm) >= 3
                        and i + 1 < len(segs) and ('.' not in segs[i + 1] or i + 2 < len(segs))]
            if not cand:
                continue
            i = cand[0]
            key = '/' + '/'.join(segs[:i + 1])
            pref.setdefault(key, set()).add(ref)
            templates.add(tuple(segs[:i]) + ('*',))
    # a prefix shared by many parks is a folder, not a park
    pref = {k: v for k, v in pref.items() if len(v) <= 3}
    return pref, templates


class SitemapReader:
    def __init__(self, web, log, max_files=300, max_urls=600_000):
        self.web, self.log, self.max_files, self.max_urls = web, log, max_files, max_urls

    def read(self, host, deadline):
        """Returns (entries [(url, lastmod, source_sitemap)], notes[])"""
        base = f'https://{host}'
        rb = self.web.robots_for(base + '/')
        starts = list(dict.fromkeys(rb.sitemaps))
        notes = []
        if starts:
            notes.append(f'robots.txt lists {len(starts)} sitemap(s)')
        else:
            starts = [base + '/sitemap.xml', base + '/sitemap_index.xml', base + '/wp-sitemap.xml']
            notes.append('robots.txt lists no sitemap; tried /sitemap.xml, /sitemap_index.xml, /wp-sitemap.xml')
        todo, seen, out, nfiles, fails = [(u, 0) for u in starts], set(), [], 0, []
        found_any = False
        while todo and nfiles < self.max_files and len(out) < self.max_urls:
            if time.time() > deadline:
                notes.append('time ran out while reading this host')
                return out, notes, False
            u, depth = todo.pop(0)
            if u in seen:
                continue
            seen.add(u)
            st, hd, body, final = self.web.get(u, headers={'Accept': 'application/xml,text/xml,*/*'})
            nfiles += 1
            if st != 200 or not body:
                fails.append(f'{u} -> {st}')
                continue
            if body[:2] == b'\x1f\x8b':
                try:
                    body = gzip.decompress(body)
                except OSError:
                    fails.append(f'{u} -> bad gzip')
                    continue
            try:
                root = ET.fromstring(body)
            except ET.ParseError:
                fails.append(f'{u} -> not XML')
                continue
            tag = root.tag.split('}')[-1].lower()
            if tag == 'sitemapindex':
                found_any = True
                for sm in root:
                    loc = next((c.text for c in sm if c.tag.split('}')[-1] == 'loc' and c.text), None)
                    if loc and depth < 4:
                        todo.append((loc.strip(), depth + 1))
            elif tag == 'urlset':
                found_any = True
                for el in root:
                    loc = lm = None
                    imgs = []
                    for c in el:
                        t = c.tag.split('}')[-1]
                        if t == 'loc' and c.text:
                            loc = c.text.strip()
                        elif t == 'lastmod' and c.text:
                            lm = c.text.strip()[:10]
                        elif t == 'image':
                            for ic in c:
                                if ic.tag.split('}')[-1] == 'loc' and ic.text:
                                    imgs.append(ic.text.strip())
                    if loc:
                        out.append((loc, lm, u, 'sitemap'))
                    for im in imgs:
                        out.append((im, lm, u, 'sitemap'))
        if fails:
            notes.append(f'{len(fails)} sitemap file(s) did not read, e.g. ' + '; '.join(fails[:3]))
        if nfiles >= self.max_files:
            notes.append(f'stopped after {self.max_files} sitemap files (cap)')
        return out, notes, found_any


def read_index_page(web, url, via='index page'):
    """The agency's own 'maps & brochures' page from the input list (or a park page found in the sitemap):
    one page, its links on the same site. (Sitemaps often list http:// addresses that only work as https://.)"""
    st = None
    if url.startswith('http://'):
        st, hd, body, final = web.get('https://' + url[7:])
    if st != 200:
        st, hd, body, final = web.get(url)
    if st != 200:
        return [], f'{via} {url} -> {st}'
    p = Links()
    try:
        p.feed(body.decode('utf-8', 'replace'))
    except Exception as e:  # noqa: BLE001
        return [], f'index page {url} -> could not parse ({e})'
    host = (urlparse(final).hostname or '').lower()
    out = []
    for l in p.links:
        a = urldefrag(urljoin(final, l.strip()))[0]
        if (urlparse(a).hostname or '').lower() == host and urlparse(a).scheme in ('http', 'https'):
            out.append((a, None, final, via))
    return out, f'{via} {url}: {len(out)} links on the same site'


def load_parks(areas, parkinfo_dir, web, cache_note):
    """{area: {ref: (name, website)}} from the club's parkinfo files, else POTA's own list (api.pota.app)."""
    parks = {}
    for a in areas:
        f = os.path.join(parkinfo_dir, f'{a}.json') if parkinfo_dir else None
        if f and os.path.exists(f):
            d = json.load(open(f))['parks']
            parks[a] = {r: (v[0], v[1] if len(v) > 1 else '') for r, v in d.items()}
            cache_note.append(f'{a} parks: {f} ({len(d)})')
            continue
        st, hd, body, _ = web.get(f'https://api.pota.app/location/parks/{a}')
        if st == 200:
            rows = json.loads(body)
            parks[a] = {r['reference']: (r['name'], r.get('website') or '') for r in rows}
            cache_note.append(f'{a} parks: api.pota.app ({len(rows)})')
        else:
            parks[a] = {}
            cache_note.append(f'{a} parks: could not read ({st})')
    return parks


def load_docs(areas, docs_dir):
    """{ref: [urls]} and {host: n links} from the club's data/docs/US-XX.json map links (+ the park pages)."""
    by_ref, hosts = {}, {}
    if not docs_dir:
        return by_ref, hosts
    for a in areas:
        f = os.path.join(docs_dir, f'{a}.json')
        if not os.path.exists(f):
            continue
        for ref, v in json.load(open(f)).get('parks', {}).items():
            m = v.get('map') or {}
            urls = [x for x in (m.get('url'), m.get('page'), v.get('page')) if x]
            by_ref.setdefault(ref, []).extend(urls)
            if m.get('url'):
                h = (urlparse(m['url']).hostname or '').lower()
                if h:
                    hosts[h] = hosts.get(h, 0) + 1
    return by_ref, hosts


def pick_hops(maps, pages, prefixes, cap):
    """Which sitemap pages to open once: park pages named by a learned path first, then map-named HTML pages
    (maps.htm, /map, brochures) that name a park. Files (PDF / images) are never opened."""
    roots = set(prefixes)
    first, second, third = [], [], []
    for p in pages:
        if not p['refs']:
            continue
        lp = (urlparse(p['url']).path or '').lower().rstrip('/')
        lp = re.sub(r'/index\.(html?|php|aspx?)$', '', lp)
        (first if lp in roots else third).append(p['url'])
    for m in maps:
        u = m['url']
        pth = unquote(urlparse(u).path or '/')
        if not m['refs'] or FILE_EXT.search(pth) or not PAGE_EXT.search(pth):
            continue
        if set(m['words']) & {'map', 'maps', 'brochure', 'brochures', 'trailmap', 'trailmaps', 'mapbook'}:
            second.append(u)
    return list(dict.fromkeys(first + second + third))[:cap]


def is_page_url(url, templates):
    segs = [s for s in (urlparse(url).path or '').lower().split('/') if s]
    if not segs:
        return False
    if segs[-1].startswith('index.'):
        segs = segs[:-1]
    if FILE_EXT.search(segs[-1] if segs else ''):
        return False
    for t in templates:
        if len(t) == len(segs) and all(a == '*' or a == b for a, b in zip(t, segs)):
            return True
    return len(segs) == 2 and segs[0] in PARK_PATH_SEGS


def process_host(host, entries, matcher, prefixes, templates, national, read_date, extra_note=''):
    maps, pages, src = [], [], {}
    seen = set()
    for url, lm, source, via in entries:
        if banned(url):
            continue
        key = norm_url(url)
        if key in seen:
            continue
        seen.add(key)
        path = urlparse(url).path or ''
        fname = path.rsplit('/', 1)[-1]
        mw = map_words(url)
        mapword = bool(mw)
        refs = matcher.match(url)
        learned = None
        lp = path.lower().rstrip('/')
        for pre, rs in prefixes.items():
            if lp == pre or lp.startswith(pre + '/') or lp.startswith(pre + '.'):
                if learned is None or len(pre) > len(learned[0]):
                    learned = (pre, rs)
        if learned:
            have = {r['ref'] for r in refs}
            for r in sorted(learned[1]):
                if r in have:
                    for x in refs:
                        if x['ref'] == r:
                            x['score'] = 1.0
                else:
                    refs.insert(0, {'ref': r, 'score': 1.0, '_w': [f'path {learned[0]}']})
            refs.sort(key=lambda r: (-r['score'], r['ref']))
        page = not FILE_EXT.search(unquote(fname)) and bool(is_page_url(url, templates) or (learned and lp == learned[0]))
        if not mapword and not page:
            continue
        if national and not refs:
            continue     # a nationwide site: keep only URLs that name a park of the areas asked for
        words = mw
        matched = sorted({w for r in refs for w in r['_w']})
        item = {'url': url, 'lastmod': lm, 'refs': [{'ref': r['ref'], 'score': r['score']} for r in refs],
                'words': words + [w for w in matched if w not in words]}
        why = [{'sitemap': 'listed in the site\'s own sitemap',
                'index page': 'linked from the agency\'s maps page in the club\'s agency list',
                'one step': 'linked from a park page / map page that the sitemap lists (one step)'}.get(via, via)]
        if mapword:
            why.append('the address says ' + ', '.join(words or ['map']))
        if page:
            why.append('the address looks like one park\'s page on this site')
        if refs:
            why.append('it names ' + ', '.join(f"{r['ref']} ({r['score']})" for r in item['refs']) +
                       (' by name words' if not learned else ' (path learned from the club\'s own links)'))
        else:
            why.append('no park name found in the address')
        (pages if page else maps).append(item)
        src[url] = {'source_url': source, 'read_date': read_date, 'why': '; '.join(why) + '.'}
    return maps, pages, src


def run(args, web=None, now=None):
    t0 = now or time.time()
    deadline = t0 + args.max_minutes * 60
    out = args.out
    os.makedirs(os.path.join(out, 'sitemaps'), exist_ok=True)
    log = (lambda *a: print(*a, flush=True)) if not args.quiet else (lambda *a: None)
    web = web or Polite(cache=args.cache, log=log)
    web.log = log
    read_date = today()
    areas = [a.strip() for a in (args.areas or '').split(',') if a.strip()]
    rows = []
    if args.agencies:
        try:
            rows = list(csv.DictReader(open(args.agencies, newline='', encoding='utf-8-sig')))
        except OSError as e:
            print(f'bad input: {e}', file=sys.stderr)
            return 2
    if not areas:
        areas = sorted({f"US-{r['state'].strip()}" for r in rows if r.get('state')})
    states = {a.split('-', 1)[1] for a in areas if '-' in a}
    notes = []
    parks_by_area = load_parks(areas, args.parkinfo, web, notes)
    all_parks = {r: v[0] for a in parks_by_area.values() for r, v in a.items()}
    docs_by_ref, docs_hosts = load_docs(areas, args.docs)
    # all of a state's own links (club docs + POTA website) feed the learned park paths
    known = {}
    for a in parks_by_area.values():
        for r, (n, w) in a.items():
            if w:
                known.setdefault(r, []).append(w)
    for r, us in docs_by_ref.items():
        if r in all_parks:
            known.setdefault(r, []).extend(us)
    # the hosts: the agency list rows of those states + the hosts of the club's map links
    hosts, index_pages, agency_states = {}, {}, {}
    for r in rows:
        u = (r.get('url') or '').strip()
        h = (urlparse(u).hostname or '').lower()
        if not h:
            continue
        agency_states.setdefault(h, set()).add(r.get('state', '').strip())
        if r.get('state', '').strip() in states:
            hosts.setdefault(h, set()).add('agency list: ' + (r.get('agency') or '').strip())
            index_pages.setdefault(h, []).append(u)
    for h, n in docs_hosts.items():
        hosts.setdefault(h, set()).add(f'{n} map link(s) in the club docs')
    hosts = {h: v for h, v in hosts.items() if not banned('https://' + h + '/')}
    order = sorted(hosts)
    if args.limit:
        order = order[:args.limit]
    state_p = os.path.join(out, 'state.json')
    state = json.load(open(state_p)) if (args.resume and os.path.exists(state_p)) else {'done': {}}
    report_p = os.path.join(out, 'report.json')
    report = json.load(open(report_p)) if (args.resume and os.path.exists(report_p)) else {'hosts': {}}
    report.update({'read_date': read_date, 'areas': areas, 'inputs': notes})
    matcher = Matcher(all_parks)
    left = 0
    for h in order:
        if h in state['done']:
            continue
        if time.time() > deadline:
            left += 1
            continue
        log(f'{h}: reading sitemaps ({"; ".join(sorted(hosts[h]))})')
        reader = SitemapReader(web, log)
        try:
            entries, hnotes, found = reader.read(h, deadline)
            if time.time() > deadline:
                left += 1
                continue
            if not args.no_index_pages:
                for ip in index_pages.get(h, []):
                    e2, n2 = read_index_page(web, ip, via='index page')
                    entries += e2
                    hnotes.append(n2)
            # a site used by agencies of several states (nps.gov, fws.gov ...) is nationwide
            national = len(agency_states.get(h, set())) > 1 or h in ('www.nps.gov', 'www.fws.gov', 'www.fs.usda.gov', 'www.blm.gov')
            prefixes, templates = learn_prefixes(h, known, all_parks)
            maps, pages, src = process_host(h, entries, matcher, prefixes, templates, national, read_date)
            if args.follow > 0:
                hop = pick_hops(maps, pages, prefixes, args.follow)
                nh = 0
                for hu in hop:
                    if time.time() > deadline:
                        hnotes.append('time ran out during the one-step reads')
                        break
                    e2, _ = read_index_page(web, hu, via='one step')
                    entries += [e for e in e2 if set(map_words(e[0])) - {'pdf', 'jpg', 'jpeg', 'png'}]
                    nh += 1
                if nh:
                    hnotes.append(f'opened {nh} park / map page(s) from the sitemap once each, for the map files they link')
                    maps, pages, src = process_host(h, entries, matcher, prefixes, templates, national, read_date)
            n_urls = len(entries)
            doc = {'host': h, 'read_date': read_date, 'n_urls': n_urls, 'maps': maps, 'pages': pages}
            json.dump(doc, open(os.path.join(out, 'sitemaps', f'{h}.json'), 'w'), indent=0)
            json.dump(src, open(os.path.join(out, 'sitemaps', f'{h}.sources.json'), 'w'), indent=0)
            status = 'ok' if found else ('index page only' if entries else 'no sitemap readable')
            if h in web.blocked:      # a 403 is accepted, never worked around (club decision, Oct 31)
                hnotes.insert(0, f'blocked: {web.blocked[h]}')
                if not found and not entries:
                    status = 'blocked'
            report['hosts'][h] = {'status': status, 'n_urls': n_urls, 'maps': len(maps), 'pages': len(pages),
                                  'maps_with_refs': sum(1 for m in maps if m['refs']), 'national': national,
                                  'learned_paths': len(prefixes), 'why': '; '.join(hnotes), 'read_date': read_date}
            log(f'  {status}: {n_urls} urls, {len(maps)} maps, {len(pages)} pages')
        except Exception as e:  # noqa: BLE001  (one bad host never stops the run)
            report['hosts'][h] = {'status': 'SOURCE DOWN', 'why': f'{type(e).__name__}: {e}', 'read_date': read_date}
            log(f'  failed: {e}')
        state['done'][h] = read_date
        json.dump(state, open(state_p, 'w'), indent=1)
        json.dump(report, open(report_p, 'w'), indent=1)
    report['requests'] = web.stats
    report['blocked_hosts'] = dict(sorted({**report.get('blocked_hosts', {}), **web.blocked}.items()))
    report['left'] = left
    json.dump(report, open(report_p, 'w'), indent=1)
    json.dump(state, open(state_p, 'w'), indent=1)
    return 3 if left else 0


# ------------------------------------------------------------------ self test (no network)
class FakeWeb(Polite):
    def __init__(self, files):
        super().__init__(cache=None, gap=0)
        self.files = files

    def _raw(self, url, method='GET', data=None, headers=None):
        self.stats['requests'] += 1
        if url in self.files:
            b = self.files[url]
            b = b if isinstance(b, bytes) else b.encode()
            return 200, {}, b, url
        return 404, {}, b'', url


def selftest():
    T = os.path.join(HERE, 'tests')
    files = {}
    for f in json.load(open(os.path.join(T, 'web.json')))['files']:
        p = os.path.join(T, f['file'])
        b = open(p, 'rb').read()
        if f.get('gzip'):
            b = gzip.compress(b)
        files[f['url']] = b
    import tempfile
    import shutil
    tmp = tempfile.mkdtemp(prefix='kpc_sitemaps_test_')
    try:
        return _selftest(T, files, tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _selftest(T, files, tmp):
    a = argparse.Namespace(agencies=os.path.join(T, 'agencies.csv'), docs=os.path.join(T, 'docs'),
                           parkinfo=os.path.join(T, 'parkinfo'), areas='US-ZZ', out=tmp, cache=None,
                           max_minutes=5, resume=False, limit=0, no_index_pages=False, quiet=True, follow=150)
    code = run(a, web=FakeWeb(files))
    ok = code == 0
    exp = json.load(open(os.path.join(T, 'expected', 'parks.example.gov.json')))
    got = json.load(open(os.path.join(tmp, 'sitemaps', 'parks.example.gov.json')))
    got['read_date'] = exp['read_date'] = 'X'
    if got != exp:
        ok = False
        print('output differs from tests/expected/parks.example.gov.json:')
        print(json.dumps(got, indent=1)[:3000])
    src = json.load(open(os.path.join(tmp, 'sitemaps', 'parks.example.gov.sources.json')))
    if not all(v.get('source_url') and v.get('why') and re.match(r'\d{4}-\d\d-\d\d$', v.get('read_date', '')) for v in src.values()):
        ok = False
        print('a row is missing source_url / read_date / why')
    rb = Robots('User-agent: *\nDisallow: /private\nAllow: /private/maps\n')
    if rb.allowed('https://x/private/a') or not rb.allowed('https://x/private/maps/a.pdf'):
        ok = False
        print('robots.txt rules read wrong')
    if not banned('https://www.openstreetmap.org/x') or banned('https://storage.googleapis.com/a.pdf'):
        ok = False
        print('banned-source check wrong')
    for m in polite_selftest():
        ok = False
        print(m)
    print('PASS' if ok else 'FAIL')
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description='KPC agency sitemap reader (T3)')
    ap.add_argument('--agencies', '--in', dest='agencies', help='agency list CSV (state, agency, url)')
    ap.add_argument('--docs', help='folder with the club docs files (data/docs); their map-link hosts are read too')
    ap.add_argument('--parkinfo', help='folder with data/parkinfo/US-XX.json (else POTA\'s own park list is read)')
    ap.add_argument('--areas', help='e.g. US-KY,US-TN (default: every state in the agency list)')
    ap.add_argument('--out', default='out')
    ap.add_argument('--cache', help='download cache folder kept between runs')
    ap.add_argument('--max-minutes', type=float, default=50)
    ap.add_argument('--resume', action='store_true')
    ap.add_argument('--limit', type=int, default=0, help='only the first N hosts')
    ap.add_argument('--no-index-pages', action='store_true', help='read sitemaps only, not the agency list\'s own maps page')
    ap.add_argument('--follow', type=int, default=150, help='open up to N park / map pages per host once each, for the '
                    'map files they link (0 = sitemaps and the agency maps page only)')
    ap.add_argument('--quiet', action='store_true')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.agencies and not a.docs:
        print('bad input: give --agencies and/or --docs', file=sys.stderr)
        return 2
    return run(a)


if __name__ == '__main__':
    sys.exit(main())
