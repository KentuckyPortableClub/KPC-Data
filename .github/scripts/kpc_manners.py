#!/usr/bin/env python3
"""KPC BOT MANNERS (Fable, chat 10 'bot workshop', Oct 28 2026). ONE small module every workshop bot imports, so the house
rules are written once: the host rules first (kpc_host_rules.py, Nov 10: never-contact hosts, every services*.arcgis.com host
and the saved-copy-only list get no request of any kind, robots.txt included), robots.txt obeyed with NO exemption (the old ArcGIS
REST exemption is gone, Nov 10; a robots.txt 401 / 403 is a Disallow), 1 request / 2 s per host, back-off on 429 / 5xx, three strikes
= that host rests a day (remembered across runs in the bot's state file), range reads for PDFs, a User-Agent that names the club
site and never an email. Nothing here decides anything about a park: it only fetches politely.

Use:  M = Manners('KPC park truth checker', state.get('hosts'))   # a name for the UA (what the bot reads)
      st, headers, body, final_url = M.get(url)                   # st = int HTTP status, or 'rest' / 'robots' / 'err:...'
      state['hosts'] = M.resting()                                 # save before the run ends
"""
import atexit, hashlib, importlib.util, json, os, re, threading, time, urllib.error, urllib.parse, urllib.request, urllib.robotparser


def _load_host_rules():
    """kpc_host_rules.py next to this file (the engine loads this module by path, so no sys.path is assumed)."""
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kpc_host_rules.py')
    spec = importlib.util.spec_from_file_location('kpc_host_rules', p); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


HR = _load_host_rules()   # no fallback: a fetch module without the host rules must not run

SITE = 'https://kentuckyportableclub.github.io/KPC-Links/'
# Oct 29 9:34 + 9:37 AM (Brandon, CLAUDE.md 'KEYED GOVERNMENT APIS'): the API key is permission for ONLY these two documented API
# paths (never their web pages), well under their rate limits; robots.txt is obeyed everywhere else (ArcGIS REST as before).
KEYED_API = {'ridb.recreation.gov': '/api/', 'developer.nps.gov': '/api/'}
# Nov 3 (Mapping, bots-first review): house rule is "never bypass robots.txt". Nov 10: the ArcGIS REST exemption (opt-in since
# Nov 3 through KPC_ARCGIS_ROBOTS_EXEMPT) is DELETED; no variable turns it back on. Crawl-delay is obeyed (longer of it and our 2 s
# gap). A 403 on a page is retried once after a pause, then handed to a person (no strike-and-forget, no third try).
MAX_CRAWL_DELAY = 120   # a host asking for more than this is skipped for the run and listed for a person
# Nov 3 (Super, answer-sheet task): ArcGIS Hub asks for Crawl-delay 60. Obeying it must not stall a nightly run, so:
#  * KPC_MANNERS_CACHE=<dir> keeps plain 200 GET answers on disk (the workflow saves the dir with actions/cache). A cached answer
#    younger than KPC_MANNERS_CACHE_DAYS (default 7) is returned with no request at all. By default only SLOW hosts (Crawl-delay of
#    KPC_SLOW_HOST_DELAY s or more, default 10) are cached; KPC_MANNERS_CACHE_ALL=1 caches every host. robots.txt itself is cached
#    a day in the same dir, so a host's rules are not re-read every run. No cache dir set = no disk cache, but Crawl-delay, the
#    slow-host budget and 'deferred' still apply (Quality A11).
#  * KPC_SLOW_HOST_BUDGET (default 10) live requests per slow host per run; past that a read returns 'deferred' (not a strike,
#    nothing rests): the bot carries the URL to the next run instead of sleeping for an hour.
CACHE_DIR = os.environ.get('KPC_MANNERS_CACHE') or ''
CACHE_DAYS = float(os.environ.get('KPC_MANNERS_CACHE_DAYS') or 7)
CACHE_ALL = os.environ.get('KPC_MANNERS_CACHE_ALL', '0') == '1'
SLOW_DELAY = float(os.environ.get('KPC_SLOW_HOST_DELAY') or 10)
SLOW_BUDGET = int(os.environ.get('KPC_SLOW_HOST_BUDGET') or 10)
# Nov 3 (Quality grade-bots-first A4): statuses that mean "not this run, try again next run" - never a failure, never a strike.
# 'rest' = the host struck out today; 'deferred' = a slow host's live budget is used up; 'crawl-delay' = the host asks for more
# than MAX_CRAWL_DELAY s between requests (also listed for a person). Callers use next_run(st).
# Nov 3 re-cut (Quality A13): 'robots-unreadable' = robots.txt answered 5xx or could not be reached. That is NOT a Disallow
# ('robots'): nothing is fetched this run, but the next run asks again. Nov 10: a robots.txt 401 / 403 IS a Disallow ('robots').
NEXT_RUN = ('rest', 'deferred', 'crawl-delay', 'robots-unreadable')
def next_run(st): return isinstance(st, str) and st in NEXT_RUN
# Nov 3 addendum (Quality spot-check, 7:05 PM CST): the two robots statuses. 'robots' = robots.txt says no (a Disallow for this URL,
# or for the whole site); 'robots-unreadable' = robots.txt could not be read (A13, retried next run). A caller (or a grader) that
# only wants to know "robots stopped this read" uses robots_block(st), which is True for BOTH words; 'robots' alone is a Disallow.
# Nov 10: 'host-rule' = kpc_host_rules.py says no request of any kind (counted as a robots block, never retried next run).
ROBOTS_BLOCK = ('robots', 'robots-unreadable', 'host-rule')
def robots_block(st): return isinstance(st, str) and st in ROBOTS_BLOCK
# Nov 3 (A3): query parameters that carry a secret. They never reach the cache key or the stored url.
SECRET_Q = re.compile(r'^(key|api_key|apikey|api-key|token|access_token|auth|signature|sig|client_secret|password)$', re.I)


def safe_url(u):
    """u without secret query parameters (A3): for cache keys, stored urls and lists for a person."""
    try:
        p = urllib.parse.urlsplit(u)
        q = [(k, v) for k, v in urllib.parse.parse_qsl(p.query, keep_blank_values=True) if not SECRET_Q.match(k)]
        return urllib.parse.urlunsplit((p.scheme, p.netloc, p.path, urllib.parse.urlencode(q), p.fragment))
    except Exception: return u.split('?')[0]  # noqa: BLE001


class Manners:
    def __init__(self, job, resting=None, gap=2.0, strikes_out=3, rest_s=86400, read_max=3_000_000):
        self.ua = f'KPC bot: {job} ({SITE}; ham radio club; 1 request per 2 s per host; reads page text and metadata only)'
        self.gap, self.strikes_out, self.rest_s, self.read_max = gap, strikes_out, rest_s, read_max
        self.last, self.robots, self.strike = {}, {}, {}
        self.dead = {h: t for h, t in (resting or {}).items() if t > time.time()}
        self.stat = {'requests': 0, 'robots': 0, 'strikes': 0, 'errors': 0, 'rested': 0, 'host_rule': 0}
        self.job = job
        self.area = ''                # Nov 10: the bot sets the area it works on; a refused layer goes on the needs-download list with it
        self.needs = []               # Nov 10: [(area, url, status, why)] a layer url this run may not or could not fetch
        _ALL.append(self)
        self.refused = {}
        self.slow_used = {}
        self.blocked = {}             # addendum: host:port -> (status, why) once robots.txt says no to the whole site or is unreadable
        self.dropped = []             # addendum: [(url without secrets, status)] queued requests dropped without any request
        self.for_person = []          # A2: [(url without secrets, why)] - every second 403 and every Crawl-delay skip, never only a count
        self.stat['for_person_urls'] = self.for_person   # saved with M.stat by the bots that keep it (detective, truth)
        self._rlk = threading.Lock()  # A12: one robots.txt read per host:port even with threads
        self._lk = threading.Lock()   # A12: pacing is thread-safe; the rest of the module is still meant for one thread per Manners

    @staticmethod
    def host(u): return urllib.parse.urlparse(u).netloc.lower().split(':')[0]

    def resting(self): return {h: t for h, t in self.dead.items() if t > time.time()}

    @staticmethod
    def rkey(u): return urllib.parse.urlparse(u).netloc.lower()   # A10: robots rules are per host AND port

    def keyed(self, u):
        h, pp = self.host(u), urllib.parse.urlparse(u)
        return bool(KEYED_API.get(h)) and (pp.path or '').startswith(KEYED_API[h])

    def robots_ok(self, u):
        """Nov 3 (Quality A1, RFC 9309): robots.txt 200 = its rules; 404/410 = no rules (allowed); anything else (401/403/5xx,
        a time-out, no connection) = we cannot know the rules, so this run does NOT fetch from that host:port, and the failure is
        never cached. The cache keeps the real status (200/404/410). The robots read is a request like any other (A5)."""
        h = self.host(u)
        if not HR.host_ok(u)[0]: return False                # Nov 10: the host rules first; robots.txt of a blocked host is never read
        if self.keyed(u):
            self.stat['keyed_api'] = self.stat.get('keyed_api', 0) + 1; return True   # Brandon Oct 29 9:34 AM: key = permission, /api/ only
        rk = self.rkey(u)
        with self._rlk:
            if rk not in self.robots: self._load_robots(u, rk, h)
        rp = self.robots[rk]
        if rp is False: ok = False
        else:
            # can_fetch(self.ua) already falls back to the '*' group; OR-ing '*' let a '*' allow override a rule aimed at us.
            try: ok = rp is None or rp.can_fetch(self.ua, u)
            except Exception: ok = False  # noqa: BLE001  (rules we cannot apply = do not fetch)
        if not ok: self.stat['robots'] += 1; self.refused[h] = self.refused.get(h, 0) + 1
        return ok

    def _load_robots(self, u, rk, h):
        pu = urllib.parse.urlparse(u)
        ru = f'{pu.scheme or "https"}://{pu.netloc}/robots.txt'
        c = self._cache_read('robots ' + ru, 1.0)
        st, txt = (c[0], c[2]) if c is not None and c[0] in (200, 404, 410) else (None, None)
        if st is None:
            self._pace(h, 0.0)
            try:
                with urllib.request.urlopen(urllib.request.Request(ru, headers={'User-Agent': self.ua}), timeout=15) as r:
                    st, txt = r.status, r.read(512_000)   # RFC 9309: parse at least 500 KiB (Quality: was 40,000 bytes)
            except urllib.error.HTTPError as e:
                st, txt = e.code, b''
            except Exception:  # noqa: BLE001
                st, txt = 'unreachable', b''
            if st in (200, 404, 410): self._cache_write('robots ' + ru, st, {}, txt)
        if st == 200:
            rp = urllib.robotparser.RobotFileParser(); rp.parse(txt.decode('utf-8', 'replace').splitlines()); self.robots[rk] = rp
            try: all_no = not rp.can_fetch(self.ua, f'{pu.scheme or "https"}://{pu.netloc}/')
            except Exception: all_no = True  # noqa: BLE001
            if all_no: self.blocked[rk] = ('robots', 'robots.txt disallows the whole site for us')
        elif st in (404, 410): self.robots[rk] = None          # no rules
        elif st in (401, 403):                                  # Nov 10: a robots.txt 401 / 403 counts as a Disallow (not retried as unreadable)
            self.robots[rk] = False; self.robots_disallow = getattr(self, 'robots_disallow', set()) | {rk}
            self.blocked[rk] = ('robots', f'robots.txt answered {st}: counted as a Disallow')
            self.for_person.append((ru, f'robots.txt answered {st} (counted as a Disallow): a person downloads what is needed from {rk}'))
        else:
            self.robots[rk] = False                             # unknown rules: refuse this run (not cached)
            self.blocked[rk] = ('robots-unreadable', f'robots.txt answered {st}')   # addendum: every queued request to it is dropped
            self.stat['robots_unreadable'] = self.stat.get('robots_unreadable', 0) + 1
            self.for_person.append((ru, f'robots.txt answered {st}: nothing fetched from {rk} this run'))

    def need(self, u, status, why):
        """Nov 10: a layer url this run may not fetch -> the needs-download list (only layer urls: ArcGIS REST, a data download)."""
        if not re.search(r'/(rest/services|FeatureServer|MapServer)/|\.(geojson|json|zip|kml|kmz|gpkg)(\?|$)', str(u), re.I): return
        su = safe_url(u).split('?')[0]
        su = re.sub(r'/query/?$', '', su)
        if any(x[1] == su for x in self.needs): return
        self.needs.append((self.area or '', su, status, why))

    @staticmethod
    def _cache_path(key): return os.path.join(CACHE_DIR, hashlib.sha256(key.encode()).hexdigest()[:40] + '.json')

    def _cache_read(self, key, days):
        if not CACHE_DIR: return None
        try:
            with open(self._cache_path(key), encoding='utf-8') as f: c = json.load(f)
            if c.get('key') != key or time.time() - c['t'] > days * 86400: return None
            return c['st'], c['hdr'], bytes.fromhex(c['body']), c.get('url') or key
        except Exception: return None  # noqa: BLE001

    def _cache_write(self, key, st, hdr, body, url=None):
        if not CACHE_DIR or len(body) >= self.read_max: return   # A8: a body cut off at read_max is never cached as complete
        try:
            os.makedirs(CACHE_DIR, exist_ok=True); tmp = self._cache_path(key) + '.tmp'
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump({'key': key, 't': time.time(), 'st': st, 'hdr': {k: v for k, v in hdr.items() if k in ('content-type', 'last-modified', 'etag')},
                           'body': body.hex(), 'url': safe_url(url) if url else url}, f)
            os.replace(tmp, self._cache_path(key))
        except Exception: pass  # noqa: BLE001  (a cache that cannot be written is only slower)

    def crawl_delay(self, h):
        """h = a url, or a host:port / host key of self.robots."""
        rp = self.robots.get(self.rkey(h) if '://' in str(h) else h)
        try: d = (rp.crawl_delay(self.ua) or rp.crawl_delay('*')) if rp else None
        except Exception: d = None  # noqa: BLE001
        return float(d) if d else 0.0

    def _pace(self, h, cd, strike=0):
        """Wait until this host may be asked again: max(gap, Crawl-delay), doubled per strike (A5, A6, A12)."""
        with self._lk:
            w = max(self.gap, cd) * (2 ** strike) - (time.time() - self.last.get(h, 0))
            self.last[h] = time.time() + max(0.0, w)
        if w > 0: time.sleep(w)   # never cut a Crawl-delay short
        self.stat['requests'] += 1

    def _budget(self, h, slow):
        """A9: the slow-host budget counts REQUESTS (a 403 retry or a 5xx retry uses one more), not calls."""
        if not slow: return True
        if self.slow_used.get(h, 0) >= SLOW_BUDGET:
            self.stat['deferred'] = self.stat.get('deferred', 0) + 1; return False
        self.slow_used[h] = self.slow_used.get(h, 0) + 1; return True

    def get(self, u, rng=None, timeout=40, head=False, accept='text/html,application/pdf,application/json,*/*;q=0.8'):
        """Polite GET. Returns (status, headers dict, body bytes, final url). rng=(a,b) reads only those bytes.
        status = int HTTP status, or 'rest' / 'robots' / 'robots-unreadable' / 'deferred' / 'crawl-delay' / 'err:...' (next_run() tells which mean
        'try again next run')."""
        h = self.host(u)
        hok, hwhy = HR.host_ok(u)
        if not hok:   # Nov 10: the ONE pre-request check (kpc_host_rules.py), before rest / robots / pacing / cache: no request of any kind
            self.stat['host_rule'] += 1; self.need(u, 'host-rule', hwhy)
            return 'host-rule', {}, b'', u
        if self.dead.get(h, 0) > time.time(): self.stat['rested'] += 1; return 'rest', {}, b'', u
        bl = self.blocked.get(self.rkey(u))
        if bl and not self.keyed(u):
            # addendum (Quality's api.pota.app slip, Nov 3): once robots.txt said no to the site or could not be read, a request
            # already queued for that host is dropped here, before any pacing or network
            self.stat['dropped_queued'] = self.stat.get('dropped_queued', 0) + 1; self.dropped.append((safe_url(u), bl[0]))
            if bl[0] == 'robots': self.need(u, 'robots', bl[1])
            return bl[0], {}, b'', u
        if not self.robots_ok(u):   # A13: a robots.txt we could not read (5xx / unreachable) is a next-run status; 401 / 403 / a Disallow is 'robots'
            rk = self.rkey(u)
            st = 'robots-unreadable' if self.robots.get(rk) is False and rk not in getattr(self, 'robots_disallow', set()) else 'robots'
            if st == 'robots': self.need(u, 'robots', 'robots.txt does not allow it (a 403 counts as no)')
            return st, {}, b'', u
        cd = self.crawl_delay(u)
        if cd > MAX_CRAWL_DELAY:
            self.stat['crawl_delay_skip'] = self.stat.get('crawl_delay_skip', 0) + 1
            self.for_person.append((safe_url(u), f'Crawl-delay {cd:g} s is over {MAX_CRAWL_DELAY} s: not read'))
            return 'crawl-delay', {}, b'', u
        slow = cd >= SLOW_DELAY
        # A3: a keyed API answer is never written to disk, and secrets never reach the cache key
        cacheable = bool(CACHE_DIR) and not rng and not head and (slow or CACHE_ALL) and not self.keyed(u)
        ck = 'GET ' + safe_url(u)
        if cacheable:
            c = self._cache_read(ck, CACHE_DAYS)
            if c is not None: self.stat['cache_hits'] = self.stat.get('cache_hits', 0) + 1; return c
        tried403 = False
        hdr = {'User-Agent': self.ua, 'Accept': accept, 'Accept-Language': 'en-US,en;q=0.8,fr;q=0.5'}
        if rng: hdr['Range'] = f'bytes={rng[0]}-{rng[1]}'
        for attempt in range(3):
            if not self._budget(h, slow): return 'deferred', {}, b'', u
            self._pace(h, cd, self.strike.get(h, 0))
            try:
                req = urllib.request.Request(u, headers=hdr, method='HEAD' if head else 'GET')
                with urllib.request.urlopen(req, timeout=timeout) as r:
                    body = b'' if head else r.read(self.read_max)
                    hd = {k.lower(): v for k, v in r.headers.items()}
                    if cacheable and r.status == 200: self._cache_write(ck, r.status, hd, body, r.geturl())
                    return r.status, hd, body, r.geturl()
            except urllib.error.HTTPError as e:
                ra = 0
                try: ra = int((e.headers or {}).get('Retry-After') or 0)
                except Exception: ra = 0  # noqa: BLE001
                ehd = {k.lower(): v for k, v in (e.headers or {}).items()}
                if e.code == 403:   # A2: handled BEFORE the strike-out check, so every second 403 reaches a person
                    self.strike[h] = self.strike.get(h, 0) + 1; self.stat['strikes'] += 1
                    wait = max(ra, 30, self.gap, cd)
                    if not tried403 and attempt < 2 and wait <= max(120, cd):   # A7: a longer Retry-After goes to a person instead
                        tried403 = True; self.stat['retry403'] = self.stat.get('retry403', 0) + 1
                        time.sleep(wait); self.last[h] = 0; continue   # the pause above already covered the gap
                    self.stat['for_person'] = self.stat.get('for_person', 0) + 1
                    self.for_person.append((safe_url(u), 'HTTP 403 twice' if tried403 else f'HTTP 403, Retry-After {ra} s is too long to wait'))
                    if self.strike[h] >= self.strikes_out: self.dead[h] = time.time() + self.rest_s
                    return 403, ehd, b'', u
                if e.code in (429, 500, 502, 503, 504):
                    self.strike[h] = self.strike.get(h, 0) + 1; self.stat['strikes'] += 1
                    if self.strike[h] >= self.strikes_out: self.dead[h] = time.time() + self.rest_s; return 'rest', {}, b'', u
                    time.sleep(min(max(ra, 20 * (attempt + 1)), max(120, cd))); continue
                if e.code == 416 and rng: return self.get(u, None, timeout, head, accept)
                return e.code, ehd, b'', u
            except (urllib.error.URLError, TimeoutError, OSError, ValueError) as e:
                self.strike[h] = self.strike.get(h, 0) + 1; self.stat['strikes'] += 1; self.stat['errors'] += 1
                if self.strike[h] >= self.strikes_out: self.dead[h] = time.time() + self.rest_s; return 'rest', {}, b'', u
                if attempt == 2: return 'err:' + str(e)[:60], {}, b'', u
                time.sleep(10 * (attempt + 1))
        return 'err', {}, b'', u


    def fetch_all(self, urls, **kw):
        """Read a QUEUE of urls politely (addendum, Nov 3: Quality's spot-check had one api.pota.app lookup run after its
        robots.txt answered 403, because it was already queued). Yields (url, (status, headers, body, final url)) in order.
        Once robots.txt refuses a host:port as a WHOLE (unreadable: 401/403/5xx/unreachable, or a whole-site Disallow), every url
        still queued for that host:port is DROPPED for this run: no robots read, no request, status 'robots' / 'robots-unreadable'
        (robots_block() is True), listed once per host for a person with the count.
        Quality grade of the addendum (7:33 PM CST Nov 3): a Disallow for ONE PATH drops only the queued urls whose paths it
        matches; they still get status 'robots' (from the cached rules, no request) and the host's other urls are read."""
        stop, n_drop = {}, {}
        for u in urls:
            rk = self.rkey(u)
            if rk in stop:
                self.stat['dropped_queued'] = self.stat.get('dropped_queued', 0) + 1; self.dropped.append((safe_url(u), stop[rk]))
                n_drop[rk] = n_drop.get(rk, 0) + 1
                yield u, (stop[rk], {}, b'', u); continue
            r = self.get(u, **kw)
            if robots_block(r[0]) and (rk in self.blocked or r[0] == 'robots-unreadable'): stop[rk] = r[0]   # whole host only
            yield u, r
        for rk, k in n_drop.items():
            self.for_person.append((rk, f'{k} queued request(s) dropped: robots.txt said {stop[rk]!r} for {rk} this run'))


def page_text(html):
    """Visible text of an HTML page (no parser library needed)."""
    html = re.sub(r'<(script|style|noscript|svg|nav|footer)\b.*?</\1>', ' ', html, flags=re.I | re.S)
    t = re.sub(r'<br\s*/?>|</p>|</li>|</h\d>|</div>|</tr>', '\n', html, flags=re.I)
    t = re.sub(r'<[^>]+>', ' ', t)
    t = re.sub(r'&nbsp;|&#160;', ' ', t); t = t.replace('&amp;', '&').replace('&#39;', "'").replace('&quot;', '"')
    t = re.sub(r'&#(\d+);', lambda m: chr(int(m.group(1))) if int(m.group(1)) < 0x110000 else ' ', t)
    return '\n'.join(' '.join(l.split()) for l in t.split('\n') if l.strip())


def links_in(html, base):
    """[(absolute url, link text)] from an HTML page."""
    out = []
    for m in re.finditer(r'<a\b[^>]*?href\s*=\s*["\']([^"\'#]+)["\'][^>]*>(.*?)</a>', html, re.I | re.S):
        href = m.group(1).strip()
        if href.lower().startswith(('javascript:', 'mailto:', 'tel:')): continue
        txt = re.sub(r'<[^>]+>', ' ', m.group(2)); txt = ' '.join(re.sub(r'&[a-z]+;|&#\d+;', ' ', txt).split())[:120]
        try: out.append((urllib.parse.urljoin(base, href), txt))
        except Exception: pass  # noqa: BLE001
    return out


def looks_binary(txt):
    """True when 'text' is really compressed bytes (a partial PDF read gives this): few letters and spaces."""
    t = txt[:4000]
    if not t.strip(): return True
    good = sum(1 for ch in t if ch.isascii() and (ch.isalnum() or ch in ' .,;:-()$/\'\n'))
    return good / max(1, len(t)) < 0.85


_BROWSER = {}


def browser_text(u, M, timeout_ms=30000):
    """Oct 28: visible text of a page that builds itself with scripts (parks.ky.gov 'Explore | … Skip to Main Content'),
    read in headless Chromium when Playwright is installed and BROWSER=1. Same manners: robots.txt, 2 s per host, the rest
    of the host when it struck out. Returns '' when there is no browser or the page did not open."""
    import os, time as _t
    if os.environ.get('BROWSER') != '1': return ''
    h = M.host(u)
    if M.dead.get(h, 0) > _t.time() or not M.robots_ok(u): return ''
    cd = M.crawl_delay(u)   # A6: the browser obeys Crawl-delay and the slow-host budget too
    if cd > MAX_CRAWL_DELAY: M.for_person.append((safe_url(u), f'Crawl-delay {cd:g} s: browser read skipped')); return ''
    if not M._budget(h, cd >= SLOW_DELAY): return ''
    try:
        if 'pw' not in _BROWSER:
            from playwright.sync_api import sync_playwright
            _BROWSER['pw'] = sync_playwright().start(); _BROWSER['b'] = _BROWSER['pw'].chromium.launch()
            _BROWSER['ctx'] = _BROWSER['b'].new_context(user_agent=M.ua)
        M._pace(h, cd); M.stat['browser'] = M.stat.get('browser', 0) + 1
        pg = _BROWSER['ctx'].new_page()
        try:
            pg.goto(u, timeout=timeout_ms, wait_until='domcontentloaded')
            try: pg.wait_for_load_state('networkidle', timeout=12000)
            except Exception: pass  # noqa: BLE001  (busy pages never go idle: read what is there)
            pg.wait_for_timeout(1500)
            return ' '.join((pg.inner_text('body') or '').split('\n'))[:200000]
        finally: pg.close()
    except Exception as e:  # noqa: BLE001  (no Playwright on this runner, or the page failed): say so ONCE, never silently
        if not _BROWSER.get('warned'):
            _BROWSER['warned'] = True
            print('::notice title=Browser read::' + f'{type(e).__name__}: {str(e)[:300]}'.replace('\n', ' '), flush=True)
        return ''


def pdf_text(body, pages=2):
    """Text of the first pages of a (possibly partial) PDF: pypdf when installed, else the literal strings in the stream."""
    txt = ''
    try:
        import io, pypdf
        rd = pypdf.PdfReader(io.BytesIO(body), strict=False)
        for i in range(min(pages, len(rd.pages))):
            try: txt += (rd.pages[i].extract_text() or '') + '\n'
            except Exception: break  # noqa: BLE001
    except Exception: pass  # noqa: BLE001
    if len(txt.strip()) < 20:
        txt = ' '.join(re.findall(r'\(([^()\\]{2,120})\)', body.decode('latin-1', 'replace'))[:800])
    return '' if looks_binary(txt) else txt   # Oct 28: never hand compressed bytes on as text


# Nov 10: the ONE needs-download list. With KPC_NEEDS_FILE set (the hunter / finder / harvester / collector / engine workflows set it to
# data/needs-download.json and commit it with their other files), every layer url a Manners refused this run is added there as a
# row (who = brandon / never from the host rules, or brandon for a robots Disallow). Bots never save a layer; they only add rows.
_ALL = []


def write_needs(path=None):
    path = path or os.environ.get('KPC_NEEDS_FILE')
    if not path: return 0
    rows = []
    try: ND = importlib.util.spec_from_file_location('kpc_needs_download', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kpc_needs_download.py'))
    except Exception: return 0  # noqa: BLE001
    nd = importlib.util.module_from_spec(ND); ND.loader.exec_module(nd)
    for m in _ALL:
        for area, u, st, why in m.needs:
            rows.append(nd.row(area, u, f'{m.job}: {why}', m.job, who=None if st == 'host-rule' else 'brandon'))
    if not rows: return 0
    a, upd, saved = nd.add(rows, path)
    print(f'::notice title=needs-download::{len(rows)} layer(s) this run may not fetch -> {path} ({a} new, {upd} updated)', flush=True)
    return len(rows)


atexit.register(lambda: write_needs())
