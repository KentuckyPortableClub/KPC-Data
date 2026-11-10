"""Polite reading for every plug-in (spec PART 3.1). A thin layer over the club's kpc_manners (imported, never copied):

- the club's host rules first (kpc_host_rules.py through kpc_manners, Nov 10): never-contact hosts, every services*.arcgis.com host
  and the saved-copy-only list get no request of any kind, robots.txt included ('blocked (host rule ...)');
- robots.txt obeyed with NO exemption (Nov 10: the old ArcGIS REST exemption is gone); a 401 / 403 robots.txt is a Disallow;
- a time budget (Nov 10): past Polite.deadline no request is made (the read is 'not read: time budget used up', never 'dead'),
  so a run ends inside its budget instead of being killed half way;
- 1 request / 2 s per host (kpc_manners) + a per-host lock, so this process never has 2 requests on one host at once;
- 429 / 5xx back-off and three strikes = a day's rest (kpc_manners; the rest list is saved in state.json);
- an honest User-Agent naming the club site (kpc_manners; KPC_CONTACT is appended when set). Never spoofed;
- a disk cache with read dates;
- BLOCKED is never NOT FOUND: TLS failures, Cloudflare / robot challenges, token-only services and robots refusals are
  classified here and written to blocked.csv by the engine (domain, ref, kind, reason, date)."""
import datetime as dt, hashlib, json, os, pathlib, re, threading, time, urllib.parse

from . import ref

TODAY = dt.date.today().isoformat()
CF_WORDS = re.compile(rb'(Just a moment\.\.\.|challenge-platform|cf-browser-verification|Attention Required! \| Cloudflare|captcha)', re.I)
TOKEN_WORDS = re.compile(rb'"code"\s*:\s*49[89]|Token Required|Invalid token', re.I)


class Resp:
    __slots__ = ('url', 'status', 'body', 'final_url', 'read_date', 'blocked', 'cached', 'headers')

    def __init__(self, url, status, body=b'', final_url=None, read_date=TODAY, blocked=None, cached=False, headers=None):
        self.url, self.status, self.body, self.final_url = url, status, body, final_url or url
        self.read_date, self.blocked, self.cached, self.headers = read_date, blocked, cached, headers or {}

    @property
    def ok(self): return self.status == 200 and not self.blocked

    def text(self): return self.body.decode('utf-8', 'replace')

    def json(self):
        try: return json.loads(self.body.decode('utf-8', 'replace'))
        except Exception: return None  # noqa: BLE001


DEFAULT_CONTACT = 'https://github.com/KentuckyPortableClub (Kentucky Portable Club ham radio club)'   # the club's own contact (not a secret); KPC_CONTACT overrides it


class Polite:
    def __init__(self, job='KPC park-info engine', cache_dir=None, resting=None, offline=False, gap=2.0, deadline=None):
        M = ref.manners()
        self.m = M.Manners(job, resting, gap=gap)
        contact = os.environ.get('KPC_CONTACT') or DEFAULT_CONTACT
        if contact: self.m.ua = self.m.ua[:-1] + f'; {contact})'
        self.cache = pathlib.Path(cache_dir) if cache_dir else None
        if self.cache: self.cache.mkdir(parents=True, exist_ok=True)
        self.offline = offline
        self.deadline = deadline   # Nov 10: time.time() after which no request is made (the engine sets it from --max-minutes)
        self.locks, self._lk = {}, threading.Lock()
        self.blocked = []          # dicts: domain, ref, kind, reason, date, url
        self.hosts_used = {}

    # ---- helpers ----
    @staticmethod
    def host(u): return urllib.parse.urlparse(u).netloc.lower().split(':')[0]

    def _lock(self, h):
        with self._lk: return self.locks.setdefault(h, threading.Lock())

    def _ck(self, u): return hashlib.sha1(u.encode()).hexdigest()

    def _cache_read(self, u, ttl_days):
        if not self.cache: return None
        p = self.cache / (self._ck(u) + '.json')
        if not p.exists(): return None
        try:
            meta = json.loads(p.read_text())
            if not self.offline and ttl_days is not None:
                age = (dt.date.today() - dt.date.fromisoformat(meta['read_date'])).days
                if age > ttl_days: return None
            body = (self.cache / (self._ck(u) + '.bin')).read_bytes()
            return Resp(u, meta['status'], body, meta.get('final_url'), meta['read_date'], None, True, meta.get('headers'))
        except Exception: return None  # noqa: BLE001

    def _cache_write(self, r):
        if not self.cache or r.status != 200: return
        k = self._ck(r.url)
        (self.cache / (k + '.bin')).write_bytes(r.body)
        (self.cache / (k + '.json')).write_text(json.dumps({'url': r.url, 'status': r.status, 'final_url': r.final_url, 'read_date': r.read_date,
                                                             'headers': {k2: v for k2, v in r.headers.items() if k2 in ('content-type', 'last-modified')}}))

    @staticmethod
    def classify(status, headers, body):
        """None when readable, else the BLOCKED reason (never 'not found')."""
        s = str(status)
        if s == 'robots': return 'blocked (robots)'
        if s == 'robots-unreadable': return 'blocked (robots.txt not readable this run)'
        if s == 'host-rule': return 'blocked (host rule: saved copies only or never contact; on the needs-download list)'
        if s == 'rest': return 'blocked (host resting: 3 strikes)'
        if s.startswith('err'):
            if re.search(r'SSL|CERTIFICATE|TLS|EOF occurred', s, re.I): return 'blocked (TLS failure)'
            if re.search(r'timed out|timeout', s, re.I): return 'blocked (timeout)'
            if re.search(r'Name or service|nodename|getaddrinfo|resolve', s, re.I): return 'blocked (DNS)'
            return 'blocked (network: ' + s[4:60] + ')'
        if status in (403, 503) and ((headers or {}).get('server', '').lower().startswith('cloudflare') or 'cf-ray' in (headers or {}) or CF_WORDS.search(body or b'')):
            return 'blocked (Cloudflare / robot challenge)'
        if status == 403: return 'blocked (HTTP 403: server refuses this client)'
        if status == 200 and body and len(body) < 4000 and CF_WORDS.search(body): return 'blocked (robot challenge page)'
        if status == 200 and body and TOKEN_WORDS.search(body[:600]): return 'token-only (needs sign-in)'
        if status in (401, 499, 498): return 'token-only (needs sign-in)'
        return None

    # ---- the one read call ----
    def get(self, u, ref_='', kind='', ttl_days=7, timeout=40, rng=None, accept=None, max_bytes=None):
        c = self._cache_read(u, ttl_days)
        if c: return c
        if self.offline: return Resp(u, 'offline', blocked='blocked (offline: no cache)')
        if self.deadline and time.time() > self.deadline:   # Nov 10: past the time budget: no request, not 'dead', not logged as blocked
            return Resp(u, 'deadline', blocked='not read (time budget used up; the next run reads it)')
        h = self.host(u)
        self.hosts_used[h] = self.hosts_used.get(h, 0) + 1
        with self._lock(h):
            kw = {'timeout': timeout, 'rng': rng}
            if accept: kw['accept'] = accept
            old = getattr(self.m, 'read_max', None)
            if max_bytes and old is not None: self.m.read_max = max_bytes      # official bulk downloads (zip) are bigger than pages
            try:
                st, hd, body, fu = self.m.get(u, **kw)
            finally:
                if max_bytes and old is not None: self.m.read_max = old
        why = self.classify(st, hd, body)
        r = Resp(u, st, body, fu, TODAY, why, False, hd)
        if why: self.log_blocked(h, ref_, kind, why, u)
        else: self._cache_write(r)
        return r

    def get_json(self, u, **kw):
        r = self.get(u, accept='application/json,*/*;q=0.5', **kw)
        return r, (r.json() if r.status == 200 else None)

    def log_blocked(self, domain, ref_, kind, reason, url=''):
        with self._lk:
            self.blocked.append({'domain': domain, 'ref': ref_, 'kind': kind, 'reason': reason, 'date': TODAY, 'url': url})

    def write_blocked(self, out_dir):
        p = pathlib.Path(out_dir) / 'blocked.csv'; new = not p.exists()
        import csv
        with open(p, 'a', newline='') as f:
            w = csv.DictWriter(f, ['domain', 'ref', 'kind', 'reason', 'date', 'url'])
            if new: w.writeheader()
            seen = set()
            for b in self.blocked:
                k = (b['domain'], b['ref'], b['kind'], b['reason'])
                if k in seen: continue
                seen.add(k); w.writerow(b)

    def resting(self): return self.m.resting()


_MW = None


def manners_mod():
    global _MW
    if _MW is None: _MW = ref.manners()
    return _MW


def page_text(html): return manners_mod().page_text(html)
def links_in(html, base): return manners_mod().links_in(html, base)
def pdf_text(body, pages=2): return manners_mod().pdf_text(body, pages)
