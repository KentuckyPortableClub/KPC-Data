"""The escalation ladder for reading a page (PART 3.2, method §4):
  1. a plain fetch (polite.py: robots, 2 s per host, cache);
  2. a structured data file behind the page, when one is KNOWN (NPS: https://www.nps.gov/<code>/structured_data_<code>.json);
  3. the headless browser (Playwright Chromium) for script-filled pages: only when KPC_BROWSER=1 and Playwright is installed;
  4. still blocked -> blocked.csv (domain, ref, kind, reason, date), retried at the end of the run and on the next nights.
Returns a Page; page.blocked says why when nothing could be read (then nobody may write NOT FOUND for it)."""
import os, re, threading, urllib.parse
from . import polite


class Page:
    __slots__ = ('url', 'final_url', 'html', 'text', 'title', 'how', 'blocked', 'status', 'read_date', 'body')

    def __init__(self, url, **kw):
        self.url = url
        for k in self.__slots__[1:]: setattr(self, k, kw.get(k))


TITLE = re.compile(r'<title[^>]*>(.*?)</title>', re.I | re.S)


def _title(html):
    m = TITLE.search(html or '')
    return re.sub(r'\s+', ' ', m.group(1)).strip() if m else ''


def structured_for(url):
    """Known structured-data files behind a page (never guessed: only patterns an agency publishes for every park)."""
    u = urllib.parse.urlsplit(url)
    if u.netloc.endswith('nps.gov'):
        m = re.match(r'/([a-z]{4})(/|$)', u.path)
        if m: return f'https://www.nps.gov/{m.group(1)}/structured_data_{m.group(1)}.json'
    return None


def read(P, url, ref_='', kind='page', allow_browser=None):
    r = P.get(url, ref_=ref_, kind=kind, ttl_days=7)
    if r.ok:
        ct = (r.headers or {}).get('content-type', '') if isinstance(r.headers, dict) else ''
        if 'pdf' in ct.lower() or r.body[:5] == b'%PDF-':
            txt = polite.pdf_text(r.body)
            return Page(url, final_url=r.final_url, html='', text=txt, title=(txt or '')[:120], how='pdf', status=200, read_date=r.read_date, body=r.body)
        html = r.text()
        txt = polite.page_text(html)
        if len(txt) < 400 and re.search(r'<script', html, re.I):
            s = structured_for(url)
            if s:
                r2, j = P.get_json(s, ref_=ref_, kind=kind)
                if j: return Page(url, final_url=r.final_url, html=html, text=json_text(j), title=_title(html), how='structured data', status=200, read_date=r.read_date, body=r.body)
            if browser_on(allow_browser):
                b = browser(P, url)
                if b: return Page(url, final_url=r.final_url, html=html, text=b, title=_title(html), how='browser', status=200, read_date=r.read_date, body=r.body)
        return Page(url, final_url=r.final_url, html=html, text=txt, title=_title(html), how='fetch', status=200, read_date=r.read_date, body=r.body)
    if r.blocked and browser_on(allow_browser) and not re.search(r'robots|resting|tls|certificate|token', r.blocked, re.I):
        b = browser(P, url)   # only for script walls; never for robots refusals, TLS errors or robot checks
        if b and not re.search(r'cf-challenge|captcha|are you a robot', b, re.I):
            return Page(url, final_url=url, html='', text=b, title=b[:120], how='browser', status=200, read_date=r.read_date, body=b.encode())
    return Page(url, final_url=r.final_url, html='', text='', title='', how='blocked' if r.blocked else 'http', blocked=r.blocked or f'HTTP {r.status}',
                status=r.status, read_date=r.read_date, body=b'')


def json_text(j, depth=0):
    if depth > 6: return ''
    if isinstance(j, dict): return ' '.join(json_text(v, depth + 1) for v in j.values())
    if isinstance(j, list): return ' '.join(json_text(v, depth + 1) for v in j)
    return str(j) if isinstance(j, str) else ''


def browser_on(flag=None):
    if flag is not None: return flag
    if '1' not in (os.environ.get('KPC_BROWSER'), os.environ.get('BROWSER')): return False
    try:
        import playwright  # noqa: F401
        return True
    except ImportError:
        return False


_BL = threading.Lock()     # Playwright's sync API is one-thread: the 8 workers take turns


def browser(P, url):
    os.environ.setdefault('BROWSER', '1')
    try:
        with _BL: return polite.manners_mod().browser_text(url, P.m)
    except Exception:  # noqa: BLE001
        return None
