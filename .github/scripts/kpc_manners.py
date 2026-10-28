#!/usr/bin/env python3
"""KPC BOT MANNERS (Fable, chat 10 'bot workshop', Oct 28 2026). ONE small module every workshop bot imports, so the house
rules are written once: robots.txt obeyed (the ONLY exemption, per HQ's Oct 27 ruling, is ArcGIS's documented REST API by
path: /rest/services/ and /sharing/rest/ metadata and queries), 1 request / 2 s per host, back-off on 429 / 5xx, three strikes
= that host rests a day (remembered across runs in the bot's state file), range reads for PDFs, a User-Agent that names the club
site and never an email. Nothing here decides anything about a park: it only fetches politely.

Use:  M = Manners('KPC park truth checker', state.get('hosts'))   # a name for the UA (what the bot reads)
      st, headers, body, final_url = M.get(url)                   # st = int HTTP status, or 'rest' / 'robots' / 'err:...'
      state['hosts'] = M.resting()                                 # save before the run ends
"""
import re, time, urllib.error, urllib.parse, urllib.request, urllib.robotparser

SITE = 'https://kentuckyportableclub.github.io/KPC-Links/'
ARCGIS_API = re.compile(r'/(rest/services|sharing/rest)/', re.I)


class Manners:
    def __init__(self, job, resting=None, gap=2.0, strikes_out=3, rest_s=86400, read_max=3_000_000):
        self.ua = f'KPC bot: {job} ({SITE}; ham radio club; 1 request per 2 s per host; reads page text and metadata only)'
        self.gap, self.strikes_out, self.rest_s, self.read_max = gap, strikes_out, rest_s, read_max
        self.last, self.robots, self.strike = {}, {}, {}
        self.dead = {h: t for h, t in (resting or {}).items() if t > time.time()}
        self.stat = {'requests': 0, 'robots': 0, 'strikes': 0, 'errors': 0, 'rested': 0, 'arcgis_exempt': 0}
        self.refused = {}

    @staticmethod
    def host(u): return urllib.parse.urlparse(u).netloc.lower().split(':')[0]

    def resting(self): return {h: t for h, t in self.dead.items() if t > time.time()}

    def robots_ok(self, u):
        h = self.host(u)
        if ARCGIS_API.search(urllib.parse.urlparse(u).path or ''):
            self.stat['arcgis_exempt'] += 1; return True      # HQ Oct 27 10:57 PM: documented REST API paths only
        if h not in self.robots:
            rp = urllib.robotparser.RobotFileParser()
            try:
                ru = f'{urllib.parse.urlparse(u).scheme or "https"}://{h}/robots.txt'
                with urllib.request.urlopen(urllib.request.Request(ru, headers={'User-Agent': self.ua}), timeout=15) as r:
                    rp.parse(r.read(40000).decode('utf-8', 'replace').splitlines())
                self.robots[h] = rp
            except Exception:  # noqa: BLE001  (no robots file = allowed)
                self.robots[h] = None
        rp = self.robots[h]
        try: ok = rp is None or rp.can_fetch(self.ua, u) or rp.can_fetch('*', u)
        except Exception: ok = True  # noqa: BLE001
        if not ok: self.stat['robots'] += 1; self.refused[h] = self.refused.get(h, 0) + 1
        return ok

    def get(self, u, rng=None, timeout=40, head=False, accept='text/html,application/pdf,application/json,*/*;q=0.8'):
        """Polite GET. Returns (status, headers dict, body bytes, final url). rng=(a,b) reads only those bytes."""
        h = self.host(u)
        if self.dead.get(h, 0) > time.time(): self.stat['rested'] += 1; return 'rest', {}, b'', u
        if not self.robots_ok(u): return 'robots', {}, b'', u
        hdr = {'User-Agent': self.ua, 'Accept': accept, 'Accept-Language': 'en-US,en;q=0.8,fr;q=0.5'}
        if rng: hdr['Range'] = f'bytes={rng[0]}-{rng[1]}'
        for attempt in range(3):
            w = self.gap * (2 ** self.strike.get(h, 0)) - (time.time() - self.last.get(h, 0))
            if w > 0: time.sleep(min(w, 20))
            self.last[h] = time.time(); self.stat['requests'] += 1
            try:
                req = urllib.request.Request(u, headers=hdr, method='HEAD' if head else 'GET')
                with urllib.request.urlopen(req, timeout=timeout) as r:
                    body = b'' if head else r.read(self.read_max)
                    return r.status, {k.lower(): v for k, v in r.headers.items()}, body, r.geturl()
            except urllib.error.HTTPError as e:
                if e.code in (403, 429, 500, 502, 503, 504):   # 403 too: fw.ky.gov answered 403 after three bots read it in one hour
                    self.strike[h] = self.strike.get(h, 0) + 1; self.stat['strikes'] += 1
                    if self.strike[h] >= self.strikes_out: self.dead[h] = time.time() + self.rest_s; return 'rest', {}, b'', u
                    ra = 0
                    try: ra = int((e.headers or {}).get('Retry-After') or 0)
                    except Exception: ra = 0  # noqa: BLE001
                    if e.code == 403: return 403, {k.lower(): v for k, v in (e.headers or {}).items()}, b'', u   # no retry on 403, only the strike
                    time.sleep(min(max(ra, 20 * (attempt + 1)), 120)); continue
                if e.code == 416 and rng: return self.get(u, None, timeout, head, accept)
                return e.code, {k.lower(): v for k, v in (e.headers or {}).items()}, b'', u
            except (urllib.error.URLError, TimeoutError, OSError, ValueError) as e:
                self.strike[h] = self.strike.get(h, 0) + 1; self.stat['strikes'] += 1; self.stat['errors'] += 1
                if self.strike[h] >= self.strikes_out: self.dead[h] = time.time() + self.rest_s; return 'rest', {}, b'', u
                if attempt == 2: return 'err:' + str(e)[:60], {}, b'', u
                time.sleep(10 * (attempt + 1))
        return 'err', {}, b'', u


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
    try:
        if 'pw' not in _BROWSER:
            from playwright.sync_api import sync_playwright
            _BROWSER['pw'] = sync_playwright().start(); _BROWSER['b'] = _BROWSER['pw'].chromium.launch()
            _BROWSER['ctx'] = _BROWSER['b'].new_context(user_agent=M.ua)
        w = M.gap - (_t.time() - M.last.get(h, 0))
        if w > 0: _t.sleep(w)
        M.last[h] = _t.time(); M.stat['requests'] += 1; M.stat['browser'] = M.stat.get('browser', 0) + 1
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
