#!/usr/bin/env python3
"""kpc_link_fix.py: T2 dead-link fixer (Kentucky Portable Club).

When an official map or page link answers 404 / 410 / "page not found", it looks for the same
document on the same agency's site at its new address:
  1. the site's sitemap (T3's <out>/sitemaps/<host>.json if present, else it reads the sitemap
     itself): same file name, or the same name without dates and version numbers;
  2. the site's own search page;
  3. the Wayback Machine, ONLY to read the old page's title and words (never as an answer);
  4. the parent folder / the park's own page, for a link with the same title words.
A new link is only given when it opens (HTTP 200) and its PDF first page or page text names the
park. Otherwise new_url is null with the reason. It decides nothing and never edits club files.
"""
import argparse, glob, unicodedata
import importlib.util as _ilu, os as _os   # noqa: E402  (owner rule, 2026-11-10: the club's one host check, before any request)
_hs = _ilu.spec_from_file_location("kpc_host_rules", _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "..", "..", "kpc_host_rules.py"))
_hr = _ilu.module_from_spec(_hs); _hs.loader.exec_module(_hr); _hr.install()

__version__ = "0.1.0"
TOOL = "link-fix"

# ---------------------------------------------------------------------------
# KPC shared core (the same block is in every KPC outside tool).
# Polite web reader, banned sources, robots.txt, cache, state, time budget.
# ---------------------------------------------------------------------------
import gzip, hashlib, io, json, os, re, sys, time, datetime, urllib.parse

import requests

EXIT_DONE, EXIT_BAD_INPUT, EXIT_TIME = 0, 2, 3
CLUB_URL = "https://github.com/KentuckyPortableClub"
MIN_GAP_S = 2.0          # PART A: at most 1 request every 2 seconds per host
RETRIES = 3              # PART A: on 429 / 503 wait and retry 3 times, then the host is "resting"

# PART A rule 6 + HOW_WE_WORK rule 1: never used, enforced here for every request.
BANNED_HOST_SUFFIXES = (
    "openstreetmap.org", "openstreetmap.fr", "openstreetmap.de", "osm.org", "overpass-api.de",
    "overpass.kumi.systems", "overpass.private.coffee", "geofabrik.de", "osmfoundation.org",
    "openmaptiles.org", "tile.osm.ch",
    "alltrails.com", "gaiagps.com", "strava.com", "tripadvisor.com", "tripadvisor.ca",
    "tripadvisor.co.uk", "yelp.com", "yelp.ca", "wikipedia.org", "wikimedia.org", "wikidata.org",
    "protectedplanet.net", "unep-wcmc.org", "wdpa.org",
)
BANNED_HOST_RE = re.compile(
    r"(^|\.)(google\.[a-z.]+|googleapis\.com|gstatic\.com|googleusercontent\.com|ggpht\.com|"
    r"overpass[^.]*\.[a-z.]+|tripadvisor\.[a-z.]+|yelp\.[a-z.]+)$")
# A government's own file on cloud storage IS allowed (PART A rule 6).
ALLOWED_CLOUD_RE = re.compile(r"(^|\.)(storage\.googleapis\.com|s3[.-][a-z0-9.-]*amazonaws\.com|"
                              r"amazonaws\.com|blob\.core\.windows\.net)$")
BANNED_PATH_RE = re.compile(r"(google\.[a-z.]+/maps|/maps/d/|mymaps|wdpa|protectedplanet)", re.I)


def banned_reason(url):
    """Return a plain reason if the URL is a banned source, else ''."""
    try:
        p = urllib.parse.urlsplit(url)
    except ValueError:
        return "not a valid web address"
    host = (p.hostname or "").lower().rstrip(".")
    if not host:
        return "not a valid web address"
    if ALLOWED_CLOUD_RE.search(host):
        return ""
    for suf in BANNED_HOST_SUFFIXES:
        if host == suf or host.endswith("." + suf):
            return f"banned source ({suf}): the club never uses it"
    if BANNED_HOST_RE.search(host):
        return f"banned source ({host}): the club never uses Google / OSM / review sites"
    if BANNED_PATH_RE.search(host + p.path):
        return "banned source (Google My Maps / Protected Planet / WDPA)"
    return ""


def today():
    return datetime.date.today().isoformat()


def contact():
    return os.environ.get("KPC_CONTACT", "").strip() or CLUB_URL


class Robots:
    """robots.txt per RFC 9309: product-token group, longest match wins, Allow wins a tie,
    * and $ wildcards, Crawl-delay honoured (capped at 30 s)."""

    def __init__(self, text, agent_token):
        self.rules, self.delay = [], None
        groups, cur, last_was_agent = [], None, False
        for raw in (text or "").splitlines():
            line = raw.split("#", 1)[0].strip()
            if ":" not in line:
                continue
            k, v = line.split(":", 1)
            k, v = k.strip().lower(), v.strip()
            if k == "user-agent":
                if not last_was_agent:
                    cur = {"agents": [], "rules": [], "delay": None}
                    groups.append(cur)
                cur["agents"].append(v.lower())
                last_was_agent = True
                continue
            last_was_agent = False
            if cur is None:
                continue
            if k in ("allow", "disallow"):
                cur["rules"].append((k == "allow", v))
            elif k == "crawl-delay":
                try:
                    cur["delay"] = min(30.0, float(v))
                except ValueError:
                    pass
        tok = agent_token.lower()
        mine = [g for g in groups if any(a != "*" and a in tok for a in g["agents"])]
        if not mine:
            mine = [g for g in groups if "*" in g["agents"]]
        for g in mine:
            self.rules += [(a, p) for a, p in g["rules"] if p != "" or a]
            if g["delay"] is not None:
                self.delay = g["delay"]

    @staticmethod
    def _match_len(pattern, path):
        if not pattern:
            return -1
        rx = "".join(".*" if c == "*" else ("$" if (c == "$" and i == len(pattern) - 1) else re.escape(c))
                     for i, c in enumerate(pattern))
        m = re.match(rx, path)
        return len(pattern) if m else -1

    def allowed(self, url):
        p = urllib.parse.urlsplit(url)
        path = (p.path or "/") + (("?" + p.query) if p.query else "")
        best_len, best_allow = -1, True
        for allow, pat in self.rules:
            if not pat:            # "Disallow:" with nothing = allow all
                continue
            n = self._match_len(pat, path)
            if n > best_len or (n == best_len and allow):
                best_len, best_allow = n, allow
        return best_allow


class Web:
    """One polite web reader for the whole run (one request at a time)."""

    def __init__(self, tool, cache_dir=None, offline=False, log=None, min_gap=MIN_GAP_S):
        self.tool = tool
        self.ua = f"KPC park tools ({contact()}) KPC-{tool}"
        self.s = requests.Session()
        self.s.headers.update({"User-Agent": self.ua, "Accept-Language": "en"})
        self.cache_dir = cache_dir
        if cache_dir:
            os.makedirs(cache_dir, exist_ok=True)
        self.offline = offline
        self.last = {}          # host -> last request time
        self.robots = {}        # host -> Robots | None (None = whole host off limits)
        self.resting = {}       # host -> reason
        self.min_gap = min_gap
        self.n_requests = 0
        self.log = log or (lambda *a: None)

    # -- helpers ------------------------------------------------------------
    def _wait(self, host, extra=0.0):
        gap = max(self.min_gap, extra)
        r = self.robots.get(host)
        if r is not None and r.delay:
            gap = max(gap, r.delay)
        dt = time.time() - self.last.get(host, 0)
        if dt < gap:
            time.sleep(gap - dt)
        self.last[host] = time.time()

    def _cache_path(self, key):
        return os.path.join(self.cache_dir, hashlib.sha1(key.encode()).hexdigest()[:24])

    def _robots_for(self, scheme, host):
        if host in self.robots:
            return self.robots[host]
        url = f"{scheme}://{host}/robots.txt"
        txt, ok = "", True
        try:
            for _ in range(5):                 # follow up to 5 redirects (RFC 9309)
                self._wait(host)
                self.n_requests += 1
                r = self.s.get(url, timeout=30, allow_redirects=False)
                if r.status_code in (301, 302, 303, 307, 308) and r.headers.get("Location"):
                    url = urllib.parse.urljoin(url, r.headers["Location"])
                    if banned_reason(url):
                        break
                    continue
                if 200 <= r.status_code < 300:
                    txt = r.text if "html" not in r.headers.get("Content-Type", "") else ""
                elif r.status_code >= 500:
                    ok = False             # 5xx = treat the whole host as off limits
                break                      # 4xx = no robots file = allowed
        except requests.RequestException:
            ok = False
        rob = Robots(txt, self.ua) if ok else None
        self.robots[host] = rob
        return rob

    # -- the one way to read the web ---------------------------------------
    def get(self, url, params=None, max_bytes=40_000_000, use_cache=True, ttl_days=30,
            check_robots=True, method="GET", timeout=60):
        """Returns dict(status, url, final_url, headers, content, error). Never raises."""
        full = url
        if params:
            full = url + ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
        res = {"status": None, "url": full, "final_url": full, "headers": {}, "content": b"", "error": ""}
        why = banned_reason(full)
        if why:
            res["error"] = why
            return res
        key = method + " " + full
        if self.cache_dir and use_cache:
            cp = self._cache_path(key)
            if os.path.exists(cp + ".json"):
                try:
                    meta = json.load(open(cp + ".json"))
                    age = (time.time() - meta.get("t", 0)) / 86400
                    if age <= ttl_days or self.offline:
                        with open(cp + ".bin", "rb") as f:
                            meta["content"] = f.read()
                        meta["cached"] = True
                        return meta
                except (OSError, ValueError):
                    pass
        if self.offline:
            res["error"] = "offline (no cached copy)"
            return res
        cur = full
        for hop in range(8):
            p = urllib.parse.urlsplit(cur)
            host = (p.hostname or "").lower()
            if host in self.resting:
                res["error"] = f"host resting for this run ({self.resting[host]})"
                return res
            if check_robots:
                rob = self._robots_for(p.scheme or "https", p.netloc.lower())
                if rob is None:
                    res["error"] = "robots.txt could not be read (server error), so the host is off limits"
                    return res
                if not rob.allowed(cur):
                    res["error"] = "robots.txt says no"
                    res["status"] = "robots"
                    return res
            r = None
            for attempt in range(RETRIES + 1):
                self._wait(host)
                self.n_requests += 1
                try:
                    r = self.s.request(method, cur, timeout=timeout, allow_redirects=False, stream=True)
                except requests.RequestException as e:
                    r = None
                    res["error"] = f"could not connect ({type(e).__name__})"
                    if attempt < RETRIES:
                        time.sleep(3 * (attempt + 1))
                        continue
                    self.resting[host] = f"could not connect after {RETRIES} retries"
                    return res
                if r.status_code in (429, 503) or (r.status_code >= 500 and r.status_code != 501):
                    if attempt < RETRIES:
                        ra = r.headers.get("Retry-After", "")
                        wait = min(30, int(ra)) if ra.isdigit() else 5 * (3 ** attempt)
                        self.log(f"  {r.status_code} from {host}; waiting {wait}s")
                        r.close()
                        time.sleep(wait)
                        continue
                    self.resting[host] = f"HTTP {r.status_code} after {RETRIES} retries"
                break
            if r.status_code in (301, 302, 303, 307, 308) and r.headers.get("Location"):
                nxt = urllib.parse.urljoin(cur, r.headers["Location"])
                r.close()
                why = banned_reason(nxt)
                if why:
                    res["error"] = f"redirected to a banned source: {why}"
                    return res
                cur = nxt
                if r.status_code == 303:
                    method = "GET"
                continue
            buf = io.BytesIO()
            try:
                for chunk in r.iter_content(65536):
                    buf.write(chunk)
                    if buf.tell() > max_bytes:
                        res["error"] = f"file bigger than {max_bytes // 1_000_000} MB, not read in full"
                        break
            except requests.RequestException as e:
                res["error"] = f"read broke off ({type(e).__name__})"
            res.update(status=r.status_code, final_url=cur,
                       headers={k.lower(): v for k, v in r.headers.items()}, content=buf.getvalue())
            r.close()
            if self.cache_dir and use_cache and r.status_code in (200, 404, 410):
                cp = self._cache_path(key)
                with open(cp + ".bin", "wb") as f:
                    f.write(res["content"])
                meta = {k: v for k, v in res.items() if k != "content"}
                meta["t"] = time.time()
                meta["read_date"] = today()
                json.dump(meta, open(cp + ".json", "w"))
            return res
        res["error"] = "too many redirects"
        return res

    def get_json(self, url, params=None, **kw):
        r = self.get(url, params=params, **kw)
        if r["status"] == 200:
            try:
                return json.loads(r["content"].decode("utf-8", "replace")), r
            except ValueError:
                r["error"] = "the answer was not JSON"
        return None, r


class Budget:
    def __init__(self, minutes):
        self.t0 = time.time()
        self.minutes = minutes

    def left(self):
        return self.minutes * 60 - (time.time() - self.t0)

    def over(self):
        return self.left() <= 0


class State:
    """<out>/state.json: {done: {key: date}}; saved after every item."""

    def __init__(self, out_dir, resume):
        self.path = os.path.join(out_dir, "state.json")
        self.data = {"done": {}}
        if resume and os.path.exists(self.path):
            try:
                self.data = json.load(open(self.path))
            except ValueError:
                pass
        self.data.setdefault("done", {})

    def is_done(self, key):
        return key in self.data["done"]

    def mark(self, key):
        self.data["done"][key] = today()

    def save(self, **extra):
        self.data.update(extra)
        write_json(self.path, self.data)


def write_json(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def safe_out_path(out_dir, *parts):
    """Every write goes through here: it refuses any path outside --out (PART A rule 4)."""
    base = os.path.realpath(out_dir)
    p = os.path.realpath(os.path.join(base, *parts))
    if p != base and not p.startswith(base + os.sep):
        raise ValueError(f"refusing to write outside --out: {p}")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p


def add_common_args(ap, areas=True):
    ap.add_argument("--out", default="out", help="output folder (the tool writes only here)")
    ap.add_argument("--max-minutes", type=float, default=50, help="stop starting new work after this")
    ap.add_argument("--resume", action="store_true", help="skip what <out>/state.json says is done")
    ap.add_argument("--limit", type=int, default=0, help="only the first N items (tests)")
    if areas:
        ap.add_argument("--areas", default="", help="comma list, e.g. US-KY,US-TN (US-* allowed)")
    ap.add_argument("--cache", default="", help="download cache folder kept between runs")
    ap.add_argument("--selftest", action="store_true", help="run the offline test and print PASS or FAIL")
    return ap


def area_ok(area, areas_arg):
    if not areas_arg:
        return True
    a = (area or "").upper()
    for want in [x.strip().upper() for x in areas_arg.split(",") if x.strip()]:
        if want.endswith("*") and a.startswith(want[:-1]):
            return True
        if a == want:
            return True
    return False

# ------------------------------- end of shared core -------------------------


from rapidfuzz import fuzz

MAP_DOC = re.compile(r"(map|brochure|booklet|guide|atlas|boundary)", re.I)
MAP_WORDS = re.compile(r"(map|brochure|guide|trail|boundary|atlas|plan|\.pdf|\.jpe?g|\.png|\.gif)", re.I)
FILE_EXT = re.compile(r"\.(pdf|jpe?g|png|gif|tiff?|kmz|kml|zip)$", re.I)
SOFT_404 = re.compile(r"(page not found|404|not found|no longer available|can.t be found|cannot be found|"
                      r"doesn.t exist|does not exist|page you requested|we couldn.t find|error 404)", re.I)
ARCHIVE_HOSTS = ("archive.org", "archive.today", "archive.ph", "archive.is", "webcache")
MAX_SITEMAPS = 80
MAX_SITEMAP_URLS = 400_000
SEARCH_TEMPLATES = ["/search?q={q}", "/search?keys={q}", "/search/node?keys={q}", "/?s={q}",
                    "/search?query={q}", "/search?search_api_fulltext={q}"]

TYPE_WORDS = set("""state park parks trail trails forest national wildlife management area areas preserve nature
natural reserve refuge recreation historic historical site sp sf wma nwr the of and at in on""".split())


def norm(s):
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode().lower()
    s = s.replace("&", " and ").replace("'", "")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", s)).strip()


def core_words(name):
    w = [x for x in norm(name).split() if x not in TYPE_WORDS and (len(x) > 1 or x.isdigit())]
    return w or norm(name).split()


def text_names_park(text, names):
    """True when every distinctive word of one of the park's names is in the text, and they sit
    close together (inside one 40-word window)."""
    toks = norm(text).split()
    if not toks:
        return False, ""
    for nm in names:
        cw = core_words(nm)
        if not cw:
            continue
        pos = {w: [i for i, t in enumerate(toks) if t == w or (len(w) >= 6 and t.startswith(w[:-1]))] for w in cw}
        if any(not p for p in pos.values()):
            continue
        firsts = sorted(pos[cw[0]])
        for i in firsts:
            if all(any(abs(j - i) <= 40 for j in pos[w]) for w in cw):
                return True, nm
    return False, ""


def basename(url):
    p = urllib.parse.urlsplit(url).path
    return urllib.parse.unquote_plus(p.rstrip("/").rsplit("/", 1)[-1])


def stem_norm(fname):
    """File name without extension, dates, version numbers and 'final/draft' words."""
    s = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", FILE_EXT.sub("", fname)).lower()   # OzarkTrailBrochure
    s = re.sub(r"(19|20)\d\d[-_. ]?(0[1-9]|1[0-2])[-_. ]?([0-3]\d)(?!\d)", " ", s)
    s = re.sub(r"(?<!\d)\d{1,2}[-_.]\d{1,2}[-_.](\d{4}|\d{2})(?!\d)", " ", s)
    s = re.sub(r"[^a-z0-9]+", " ", s)
    s = re.sub(r"\b(19|20)\d\d\b", " ", s)
    s = re.sub(r"\b(v|ver|version|rev|r)\s?\d+\b", " ", s)
    s = re.sub(r"\b(final|draft|new|updated|update|web|print|copy|rev|revised|lowres|hires|small|large)\b", " ", s)
    s = re.sub(r"(\s\d{1,2})+$", " ", s)        # _0, -1 suffixes
    return re.sub(r"\s+", " ", s).strip()


def same_page(a, b):
    def k(u):
        p = urllib.parse.urlsplit(u)
        path = re.sub(r"/(index\.(php|html?|aspx?))?$", "", p.path)
        return ((p.hostname or "").lower().removeprefix("www."), path.rstrip("/"), p.query)
    return k(a) == k(b)


def reg_domain(host):
    parts = (host or "").lower().split(".")
    if len(parts) >= 3 and parts[-2] in ("gov", "com", "org", "net", "ac", "co", "gc", "gob", "gouv", "govt") and len(parts[-1]) == 2:
        return ".".join(parts[-3:])
    return ".".join(parts[-2:])


def is_archive(url):
    h = (urllib.parse.urlsplit(url).hostname or "").lower()
    return any(h == a or h.endswith("." + a) for a in ARCHIVE_HOSTS)

# ------------------------------------------------------------------ reading pages and files


def html_text(html):
    t = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", html)
    t = re.sub(r"(?s)<[^>]+>", " ", t)
    t = re.sub(r"&nbsp;|&#160;", " ", t)
    import html as _h
    return re.sub(r"\s+", " ", _h.unescape(t)).strip()


def html_title(html):
    import html as _h
    m = re.search(r"(?is)<h1[^>]*>(.*?)</h1>", html)
    h1 = _h.unescape(re.sub(r"(?s)<[^>]+>", " ", m.group(1))).strip() if m else ""
    m = re.search(r"(?is)<title[^>]*>(.*?)</title>", html)
    tt = _h.unescape(re.sub(r"\s+", " ", m.group(1))).strip() if m else ""
    return re.sub(r"\s+", " ", h1), tt


def html_links(html, base):
    import html as _h
    out = []
    for m in re.finditer(r'(?is)<a\b[^>]*?href\s*=\s*["\']([^"\'#]+)["\'][^>]*>(.*?)</a>', html):
        href = _h.unescape(m.group(1).strip())
        if href.lower().startswith(("javascript:", "mailto:", "tel:")):
            continue
        txt = re.sub(r"\s+", " ", _h.unescape(re.sub(r"(?s)<[^>]+>", " ", m.group(2)))).strip()
        out.append((urllib.parse.urljoin(base, href), txt[:200]))
    return out


def html_imgs(html, base):
    import html as _h
    out = []
    for m in re.finditer(r'(?is)<img\b[^>]*>', html):
        tag = m.group(0)
        src = re.search(r'src\s*=\s*["\']([^"\']+)', tag)
        alt = re.search(r'alt\s*=\s*["\']([^"\']*)', tag)
        if src:
            out.append((urllib.parse.urljoin(base, _h.unescape(src.group(1))), _h.unescape(alt.group(1)) if alt else ""))
    return out


def pdf_first_page(content):
    """(text of page 1, title from the PDF's own info). Needs pypdfium2."""
    try:
        import pypdfium2 as pdfium
        d = pdfium.PdfDocument(content)
        title = ""
        try:
            title = (d.get_metadata_dict() or {}).get("Title", "") or ""
        except Exception:
            pass
        txt = ""
        if len(d):
            pg = d[0]
            tp = pg.get_textpage()
            txt = tp.get_text_bounded()
            tp.close()
            pg.close()
        d.close()
        return txt or "", title
    except Exception:
        return "", ""


def kind_of(res):
    c, ct = res["content"][:8], res["headers"].get("content-type", "").lower()
    if c.startswith(b"%PDF-"):
        return "pdf"
    if c[:3] == b"\xff\xd8\xff" or c[:8] == b"\x89PNG\r\n\x1a\n" or c[:4] == b"GIF8":
        return "image"
    if "html" in ct or b"<html" in res["content"][:2000].lower() or b"<!doctype" in res["content"][:200].lower():
        return "html"
    return ct.split(";")[0] or "unknown"


def is_soft_404(res):
    if res["status"] != 200 or kind_of(res) != "html":
        return False
    html = res["content"][:300_000].decode("utf-8", "replace")
    h1, tt = html_title(html)
    return bool(SOFT_404.search(h1) or SOFT_404.search(tt))

# ------------------------------------------------------------------ sitemaps (T3 shape)


def t3_sitemap(paths, host):
    for d in paths:
        for h in (host, host[4:] if host.startswith("www.") else "www." + host):
            f = os.path.join(d, "sitemaps", h + ".json") if not d.endswith("sitemaps") else os.path.join(d, h + ".json")
            if os.path.exists(f):
                try:
                    j = json.load(open(f, encoding="utf-8"))
                except (OSError, ValueError):
                    continue
                urls = [(m.get("url"), m.get("lastmod")) for m in (j.get("maps") or []) + (j.get("pages") or [])
                        if isinstance(m, dict) and m.get("url")]
                return urls, f, j.get("read_date", "")
    return None, "", ""


def parse_sitemap_xml(content):
    if content[:2] == b"\x1f\x8b":
        try:
            content = gzip.decompress(content)
        except OSError:
            return [], []
    txt = content.decode("utf-8", "replace")
    is_index = bool(re.search(r"<sitemapindex", txt[:3000], re.I))
    locs = []
    for m in re.finditer(r"(?is)<(url|sitemap)>(.*?)</\1>", txt):
        block = m.group(2)
        lm = re.search(r"(?is)<loc>\s*(.*?)\s*</loc>", block)
        if not lm:
            continue
        mod = re.search(r"(?is)<lastmod>\s*(.*?)\s*</lastmod>", block)
        import html as _h
        locs.append((_h.unescape(lm.group(1)), mod.group(1)[:10] if mod else None))
    if is_index:
        return [], [u for u, _ in locs]
    return locs, []


def read_sitemaps(web, host, scheme, log):
    """Our own fallback when T3 has not run: robots.txt Sitemap: lines, else the usual names."""
    starts = []
    r = web.get(f"{scheme}://{host}/robots.txt", check_robots=False, ttl_days=7)
    if r["status"] == 200:
        for line in r["content"].decode("utf-8", "replace").splitlines():
            if line.lower().startswith("sitemap:"):
                starts.append(line.split(":", 1)[1].strip())
    if not starts:
        starts = [f"{scheme}://{host}/sitemap.xml", f"{scheme}://{host}/sitemap_index.xml", f"{scheme}://{host}/wp-sitemap.xml"]
    seen, queue, urls, read = set(), list(starts), [], 0
    while queue and read < MAX_SITEMAPS and len(urls) < MAX_SITEMAP_URLS:
        sm = queue.pop(0)
        if sm in seen or banned_reason(sm):
            continue
        seen.add(sm)
        r = web.get(sm, max_bytes=60_000_000, ttl_days=7)
        read += 1
        if r["status"] != 200:
            continue
        locs, subs = parse_sitemap_xml(r["content"])
        urls += locs
        queue += [s for s in subs if s not in seen]
    log(f"  sitemap {host}: {read} sitemap files, {len(urls)} addresses")
    return urls, read


def save_t3_shape(out_dir, host, urls):
    maps = [{"url": u, "lastmod": lm, "refs": [], "words": stem_norm(basename(u))} for u, lm in urls
            if FILE_EXT.search(urllib.parse.urlsplit(u).path) or MAP_WORDS.search(basename(u))]
    pages = [{"url": u, "lastmod": lm} for u, lm in urls
             if not (FILE_EXT.search(urllib.parse.urlsplit(u).path) or MAP_WORDS.search(basename(u)))]
    p = safe_out_path(out_dir, "work", "sitemaps", host + ".json")
    write_json(p, {"host": host, "read_date": today(), "n_urls": len(urls), "maps": maps, "pages": pages,
                   "made_by": f"kpc_link_fix {__version__} (fallback reader; T3 kpc_sitemaps is the full one)"})
    return p

# ------------------------------------------------------------------ the fixer


class Fixer:
    def __init__(self, web, args, names_for, park_page_for, log):
        self.web, self.args, self.log = web, args, log
        self.names_for, self.park_page_for = names_for, park_page_for
        self.sitemap_cache = {}

    def host_sitemap(self, host, scheme):
        if host in self.sitemap_cache:
            return self.sitemap_cache[host]
        dirs = [d for d in [self.args.sitemaps, self.args.out] if d]
        urls, src, rd = t3_sitemap(dirs, host)
        how = f"T3 sitemap file {src}" if urls is not None else ""
        if urls is None and self.args.read_sitemaps:
            urls, n = read_sitemaps(self.web, host, scheme, self.log)
            src = save_t3_shape(self.args.out, host, urls) if urls else ""
            how = f"read {n} sitemap files on {host}" if urls else f"no sitemap found on {host}"
        self.sitemap_cache[host] = (urls or [], how)
        return self.sitemap_cache[host]

    def verify(self, url, names, kind_wanted):
        """Opens (200, not a 'not found' page) and names the park? Returns a dict."""
        if is_archive(url):
            return {"opens": False, "names_park": False, "why": "an archive copy is never an answer"}
        if banned_reason(url):
            return {"opens": False, "names_park": False, "why": banned_reason(url)}
        r = self.web.get(url, max_bytes=20_000_000, ttl_days=1)
        if r["status"] != 200:
            return {"opens": False, "names_park": False, "why": r["error"] or f"HTTP {r['status']}"}
        if is_soft_404(r):
            return {"opens": False, "names_park": False, "why": "the page says 'not found'"}
        k = kind_of(r)
        final = r["final_url"]
        if is_archive(final) or banned_reason(final):
            return {"opens": False, "names_park": False, "why": "it redirects off the agency's site"}
        if k == "pdf":
            text, title = pdf_first_page(r["content"])
            ok, nm = text_names_park(text, names)
            if ok:
                return {"opens": True, "names_park": True, "kind": "pdf", "final_url": final,
                        "why": f"the PDF's first page names the park ('{nm}')"}
            if not text.strip():
                return {"opens": True, "names_park": False, "kind": "pdf", "final_url": final,
                        "why": "the PDF opens but its first page has no readable words, so it can't be shown to name the park"}
            return {"opens": True, "names_park": False, "kind": "pdf", "final_url": final,
                    "why": "the PDF opens but its first page does not name the park"}
        if k == "html":
            html = r["content"].decode("utf-8", "replace")
            ok, nm = text_names_park(html_text(html), names)
            return {"opens": True, "names_park": ok, "kind": "page", "final_url": final, "html": html,
                    "why": f"the page names the park ('{nm}')" if ok else "the page opens but does not name the park"}
        if k == "image":
            return {"opens": True, "names_park": False, "kind": "image", "final_url": final,
                    "why": "a picture with no words to read, so it can't be shown to name the park (a person can look)"}
        return {"opens": True, "names_park": False, "kind": k, "final_url": final, "why": f"opens as {k}, not a map or page"}

    def score_link(self, url, text, terms, old_stem, names):
        fn = basename(url)
        hay = norm(text + " " + fn + " " + urllib.parse.unquote(urllib.parse.urlsplit(url).path))
        ht = set(hay.split())
        s = 0.0
        if old_stem and stem_norm(fn) == old_stem:
            s += 3
        elif old_stem and fuzz.token_set_ratio(stem_norm(fn), old_stem) >= 90:
            s += 2
        for nm in names:
            cw = core_words(nm)
            if cw and all(w in ht for w in cw):
                s += 2
                break
        s += 0.3 * len(ht & set(terms))
        if MAP_WORDS.search(hay):
            s += 0.5
        return s

    def fix(self, item):
        old = item["url"]
        ref = item.get("ref", "")
        kind = item.get("kind", "map")
        names = self.names_for(item)
        out = {"ref": ref, "kind": kind, "new_url": None, "how": None, "confidence": 0.0, "checked": today(),
               "opens": False, "names_park": False, "read_date": today(), "source_url": old, "tried": []}
        if banned_reason(old):
            out["why"] = f"the old link is a banned source ({banned_reason(old)}); not looked for."
            return out
        p = urllib.parse.urlsplit(old)
        scheme, old_host = p.scheme or "https", (p.hostname or "").lower()
        # 0. is it really dead? (and where does the old host send us now?)
        r0 = self.web.get(old, max_bytes=20_000_000, ttl_days=1)
        new_host = (urllib.parse.urlsplit(r0["final_url"]).hostname or old_host).lower()
        if r0["status"] == 200 and not is_soft_404(r0):
            v = self.verify(r0["final_url"], names, kind)
            out.update(opens=True, names_park=v["names_park"], how="old link still opens",
                       why=f"The old link opens again (HTTP 200); {v['why']}. Nothing to fix." +
                       ("" if r0["final_url"] == old else f" It now lands on {r0['final_url']}."))
            if r0["final_url"] != old and v["names_park"]:
                out.update(new_url=r0["final_url"], how="old link redirects", confidence=0.9)
            out["old_status"] = 200
            return out
        out["old_status"] = r0["status"] or r0["error"]
        hosts = []
        for h in [new_host, old_host, (item.get("agency_host") or "").lower()]:
            if h and h not in hosts and not banned_reason("https://" + h + "/"):
                hosts.append(h)
        page = self.park_page_for(item)
        if page:
            ph = (urllib.parse.urlsplit(page).hostname or "").lower()
            if ph and ph not in hosts and not banned_reason(page):
                hosts.append(ph)        # the park's own site (its sitemap is read too)
        domains = {reg_domain(h) for h in hosts}
        if page:
            domains.add(reg_domain(urllib.parse.urlsplit(page).hostname or ""))
        old_name = basename(old)
        old_stem = stem_norm(old_name)
        terms = [w for w in old_stem.split() if len(w) > 2]
        cands = []      # (score, url, how, source)

        def add(url, how, src, score):
            u = url.split("#")[0]
            h = (urllib.parse.urlsplit(u).hostname or "").lower()
            if not h or reg_domain(h) not in domains or is_archive(u) or banned_reason(u) or u == old:
                return
            if any(c[1] == u for c in cands):
                return
            cands.append((score, u, how, src))

        # 1. sitemap: same file name, or the same name without dates and versions
        for h in hosts:
            urls, smhow = self.host_sitemap(h, scheme)
            out["tried"].append({"step": "sitemap", "host": h, "result": smhow})
            for u, lm in urls:
                fn = basename(u)
                if not fn:
                    continue
                if fn.lower() == old_name.lower():
                    add(u, "sitemap same name", smhow, 10)
                elif old_stem and len(old_stem) >= 5 and stem_norm(fn) == old_stem:
                    add(u, "sitemap same name without dates/versions", smhow, 8)
                elif old_stem and len(old_stem) >= 8 and FILE_EXT.search(fn) and \
                        fuzz.token_set_ratio(stem_norm(fn), old_stem) >= 92:
                    add(u, "sitemap similar name", smhow, 6)
        # 3. (read before 2 and 4) the Wayback Machine, only for the old title and words
        title_words = []
        if self.args.wayback:
            tw, wb_how = self.wayback_words(old)
            out["tried"].append({"step": "wayback (old words only)", "result": wb_how})
            title_words = tw
        terms_all = list(dict.fromkeys(terms + title_words))
        # 2. the site's own search page
        if self.args.site_search and not self.good_enough(cands):
            qwords = core_words(names[0]) if names else terms
            queries = [" ".join(qwords + ["map"])]
            if title_words:
                queries.append(" ".join(title_words[:6]))
            for h in hosts[:2]:
                got = self.site_search(h, scheme, queries, terms_all, old_stem, names, add)
                out["tried"].append({"step": "site search", "host": h, "result": got})
        # 4. the parent folder or page, and the park's own page
        if not self.good_enough(cands):
            parents = []
            path = urllib.parse.urlsplit(old).path
            segs = [s for s in path.split("/") if s]
            for depth in (1, 2):
                if len(segs) > depth:
                    parents.append(f"{scheme}://{new_host}/" + "/".join(segs[:-depth]) + "/")
            if page:
                parents.append(page)
            for pu in parents[:3]:
                r = self.web.get(pu, max_bytes=5_000_000, ttl_days=7)
                res = f"HTTP {r['status']}" if r["status"] else r["error"]
                n0 = len(cands)
                if r["status"] == 200 and kind_of(r) == "html":
                    for u, txt in html_links(r["content"].decode("utf-8", "replace"), r["final_url"]):
                        sc = self.score_link(u, txt, terms_all, old_stem, names)
                        is_doc = FILE_EXT.search(urllib.parse.urlsplit(u).path) or MAP_WORDS.search(txt + " " + basename(u))
                        if kind == "map" and not MAP_DOC.search(txt + " " + urllib.parse.unquote(u)):
                            continue
                        if same_page(u, pu) or (page and same_page(u, page)):
                            continue
                        sc += 1.5       # a map link on the park's own page (or the old file's folder)
                        if sc >= 2.3 and is_doc:
                            add(u, "park page" if pu == page else "parent page", pu, sc)
                out["tried"].append({"step": "park page" if pu == page else "parent page", "url": pu,
                                     "result": f"{res}; {len(cands) - n0} links worth opening"})
        # verify, best first
        cands.sort(key=lambda c: -c[0])
        checked = []
        page_hit = None
        queue = list(cands[: self.args.max_candidates])
        dug = 0
        while queue:
            sc, u, how, src = queue.pop(0)
            if any(c["url"] == u for c in checked) or (page and same_page(u, page)) or same_page(u, old):
                continue
            v = self.verify(u, names, kind)
            checked.append({"url": u, "how": how, "opens": v["opens"], "names_park": v["names_park"], "why": v["why"]})
            if not (v["opens"] and v["names_park"]):
                continue
            conf = {"sitemap same name": 0.95, "sitemap same name without dates/versions": 0.85,
                    "sitemap similar name": 0.7, "site search": 0.65, "parent page": 0.65, "park page": 0.6}.get(how.split(" → ")[0], 0.5)
            if kind == "map" and v.get("kind") in ("pdf", "image"):
                conf += 0.05
            if kind == "map" and v.get("kind") == "page":
                # a page, not the map itself: look on it for the map document first
                conf -= 0.15
                if dug < 2 and v.get("html"):
                    dug += 1
                    docs_on = []
                    for lu, lt in html_links(v["html"], v.get("final_url", u)):
                        if FILE_EXT.search(urllib.parse.urlsplit(lu).path) and MAP_DOC.search(lt + " " + urllib.parse.unquote(lu)):
                            docs_on.append((self.score_link(lu, lt, terms_all, old_stem, names) + 1, lu, how + " → document on it", u))
                    for iu, alt in html_imgs(v["html"], v.get("final_url", u)):
                        if MAP_DOC.search(alt + " " + basename(iu)) and not re.search(r"(logo|icon|button|megamenu)", iu, re.I):
                            out.setdefault("pictures_for_a_person", [])
                            if iu not in out["pictures_for_a_person"]:
                                out["pictures_for_a_person"].append(iu)
                    docs_on.sort(key=lambda c: -c[0])
                    for c in docs_on[:4]:
                        h = (urllib.parse.urlsplit(c[1]).hostname or "").lower()
                        if reg_domain(h) in domains and not is_archive(c[1]):
                            queue.insert(0, c)
                if page_hit is None:
                    page_hit = (v, u, how, src, conf)
                continue
            out.update(new_url=v.get("final_url", u), how=how, confidence=round(min(1.0, conf), 2), opens=True,
                       names_park=True, source_url=src if str(src).startswith("http") else u,
                       why=f"Found by {how}; it opens and {v['why']}.")
            out["checked_candidates"] = checked
            return out
        if page_hit:
            v, u, how, src, conf = page_hit
            out.update(new_url=v.get("final_url", u), how=how, confidence=round(max(0.3, conf), 2), opens=True,
                       names_park=True, source_url=src if str(src).startswith("http") else u,
                       why=f"Found by {how}; it is a web page, not the map file itself, but it opens and {v['why']} (no map document on it could be shown to name the park)." +
                       (f" It shows {len(out['pictures_for_a_person'])} map picture(s) a person can look at." if out.get("pictures_for_a_person") else ""))
            out["checked_candidates"] = checked
            return out
        out["checked_candidates"] = checked[:10]
        if not cands:
            out["why"] = "No new address found: nothing in the sitemap, the site search or the parent pages looked like the same document."
        else:
            out["why"] = f"No new address given: {len(checked)} possible links were opened but none both opened and named the park."
        return out

    @staticmethod
    def good_enough(cands):
        return any(c[0] >= 8 for c in cands)

    def wayback_words(self, old):
        cdx = "https://web.archive.org/cdx/search/cdx"
        data, r = self.web.get_json(cdx, params={"url": old, "output": "json", "fl": "timestamp,mimetype",
                                                 "filter": "statuscode:200", "limit": "-1"}, ttl_days=30)
        if not data or len(data) < 2:
            return [], "no archived copy" if r["status"] == 200 else f"archive not reachable ({r['error'] or r['status']})"
        ts, mime = data[-1][0], data[-1][1]
        r = self.web.get(f"https://web.archive.org/web/{ts}id_/{old}", max_bytes=20_000_000, ttl_days=365)
        if r["status"] != 200:
            return [], f"archived copy {ts} did not open"
        words = ""
        if kind_of(r) == "pdf":
            text, title = pdf_first_page(r["content"])
            words = (title + " " + " ".join(text.split()[:40]))
        elif kind_of(r) == "html":
            h1, tt = html_title(r["content"].decode("utf-8", "replace"))
            words = h1 + " " + tt
        ws = [w for w in norm(words).split() if len(w) > 2 and w not in TYPE_WORDS and not w.isdigit()]
        ws = list(dict.fromkeys(ws))[:12]
        return ws, f"archived copy of {ts[:8]} read for its words: {' '.join(ws) or '(none)'}"

    def site_search(self, host, scheme, queries, terms, old_stem, names, add):
        for tpl in SEARCH_TEMPLATES[: self.args.search_tries]:
            any_ok = False
            for q in queries:
                u = f"{scheme}://{host}" + tpl.format(q=urllib.parse.quote_plus(q))
                r = self.web.get(u, max_bytes=5_000_000, ttl_days=7)
                if r["status"] != 200 or kind_of(r) != "html":
                    if r["status"] == "robots":
                        return "robots.txt says no to the search page"
                    break
                any_ok = True
                n = 0
                for link, txt in html_links(r["content"].decode("utf-8", "replace"), r["final_url"]):
                    if re.search(r"[?&](q|s|keys|query|page)=", link):
                        continue
                    sc = self.score_link(link, txt, terms, old_stem, names)
                    if sc >= 2.3:
                        add(link, "site search", u, sc)
                        n += 1
                if n:
                    return f"{tpl.split('{')[0]} gave {n} links worth opening"
            if any_ok:
                return f"{tpl.split('{')[0]} answered but gave nothing useful"
        return "no search page answered"

# ------------------------------------------------------------------ main


def load_names(parkinfo_dir, docs_patterns):
    names, pages = {}, {}
    for f in sorted(glob.glob(os.path.join(parkinfo_dir, "*.json"))) if parkinfo_dir else []:
        try:
            d = json.load(open(f, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        for ref, row in (d.get("parks") or {}).items():
            if isinstance(row, list) and row:
                names.setdefault(ref, []).append(str(row[0]))
                if len(row) > 1 and str(row[1]).startswith("http"):
                    pages.setdefault(ref, row[1])
    for pat in docs_patterns or []:
        for f in sorted(glob.glob(pat)):
            try:
                d = json.load(open(f, encoding="utf-8"))
            except (OSError, ValueError):
                continue
            for ref, v in (d.get("parks") or {}).items():
                if isinstance(v, dict):
                    if v.get("n"):
                        names.setdefault(ref, []).append(v["n"])
                    if str(v.get("page", "")).startswith("http"):
                        pages[ref] = v["page"]
    return names, pages


def run(args):
    out_dir = args.out
    os.makedirs(out_dir, exist_ok=True)
    logf = open(safe_out_path(out_dir, "run_log.txt"), "a", encoding="utf-8")

    def log(*a):
        s = " ".join(str(x) for x in a)
        print(s, flush=True)
        logf.write(s + "\n")
        logf.flush()

    if not args.links or not os.path.exists(args.links):
        log("--links file is missing")
        return EXIT_BAD_INPUT
    try:
        items = json.load(open(args.links, encoding="utf-8"))
    except ValueError as e:
        log(f"--links is not valid JSON: {e}")
        return EXIT_BAD_INPUT
    if isinstance(items, dict):
        items = items.get("links") or list(items.values())
    items = [x for x in items if isinstance(x, dict) and x.get("url")]
    items = [x for x in items if area_ok(x.get("area", ""), args.areas) or not x.get("area")] if args.areas else items
    if args.limit:
        items = items[: args.limit]
    names, pages = load_names(args.parkinfo, args.docs)

    def names_for(item):
        n = list(item.get("alt_names") or [])
        if item.get("name"):
            n.insert(0, item["name"])
        n += names.get(item.get("ref", ""), [])
        return list(dict.fromkeys([x for x in n if x]))

    page_titles = {}

    def park_page_for(item):
        return item.get("page") or pages.get(item.get("ref", ""))

    web = Web(TOOL, cache_dir=args.cache or None, log=log)
    fixer = Fixer(web, args, names_for, park_page_for, log)

    # the agency's own name for the park: the <h1> of the park's own page
    def names_with_page(item):
        base = names_for(item)
        pg = park_page_for(item)
        if pg and pg not in page_titles:
            r = web.get(pg, max_bytes=5_000_000, ttl_days=7)
            h1 = html_title(r["content"].decode("utf-8", "replace"))[0] if r["status"] == 200 and kind_of(r) == "html" else ""
            page_titles[pg] = h1 if 3 <= len(h1) <= 120 and not SOFT_404.search(h1) else ""
        if pg and page_titles.get(pg):
            base.append(page_titles[pg])
        return list(dict.fromkeys(base))

    fixer.names_for = names_with_page
    state = State(out_dir, args.resume)
    res_path = safe_out_path(out_dir, "link_fix.json")
    results = {}
    if args.resume and os.path.exists(res_path):
        try:
            results = json.load(open(res_path))
        except ValueError:
            pass
    log(f"KPC link-fix {__version__}: {len(items)} links; read {today()}")
    budget, left = Budget(args.max_minutes), 0
    for i, it in enumerate(items):
        if state.is_done(it["url"]) and it["url"] in results:
            continue
        if budget.over():
            left = len([x for x in items[i:] if not state.is_done(x["url"])])
            break
        try:
            row = fixer.fix(it)
        except Exception as e:
            row = {"ref": it.get("ref"), "new_url": None, "how": None, "confidence": 0.0, "checked": today(),
                   "opens": False, "names_park": False, "read_date": today(), "source_url": it["url"],
                   "why": f"CAN'T TELL: the tool hit an error ({type(e).__name__}: {e})."}
        results[it["url"]] = row
        state.mark(it["url"])
        write_json(res_path, results)
        state.save(requests=web.n_requests)
        log(f"[{i + 1}/{len(items)}] {it.get('ref')} {it['url'][:90]} -> {row.get('new_url')} ({row.get('how')}, {row.get('confidence')})")
    fixed = sum(1 for r in results.values() if r.get("new_url"))
    write_json(safe_out_path(out_dir, "summary.json"), {"read_date": today(), "links": len(results), "fixed": fixed,
                                                        "requests": web.n_requests, "resting_hosts": web.resting, "left": left})
    log(f"done: {fixed} of {len(results)} fixed; {web.n_requests} requests")
    return EXIT_TIME if left else EXIT_DONE

# ------------------------------------------------------------------ self test


def selftest():
    here = os.path.dirname(os.path.abspath(__file__))
    fx = json.load(open(os.path.join(here, "tests", "fake_site.json")))
    expected = json.load(open(os.path.join(here, "tests", "expected.json")))
    ok = True

    class FakeWeb(Web):
        def get(self, url, params=None, **kw):
            full = url + ("?" + urllib.parse.urlencode(params) if params else "")
            res = {"status": 404, "url": full, "final_url": full, "headers": {"content-type": "text/html"},
                   "content": b"<html><title>Page not found</title></html>", "error": ""}
            if banned_reason(full):
                res.update(status=None, error=banned_reason(full), content=b"")
                return res
            page = fx["web"].get(full)
            if page is None:
                return res
            if page.get("redirect"):
                return self.get(page["redirect"])
            body = page.get("body", "")
            if page.get("pdf_text") is not None:
                body = make_pdf(page["pdf_text"])
                res["headers"]["content-type"] = "application/pdf"
            elif page.get("xml"):
                res["headers"]["content-type"] = "application/xml"
            res.update(status=page.get("status", 200), content=body if isinstance(body, bytes) else body.encode())
            return res

    import tempfile
    with tempfile.TemporaryDirectory() as td:
        lf = os.path.join(td, "links.json")
        json.dump(fx["links"], open(lf, "w"))
        out = os.path.join(td, "out")
        os.makedirs(os.path.join(out, "sitemaps"))
        json.dump(fx["t3_sitemap"], open(os.path.join(out, "sitemaps", "parks.fake.gov.json"), "w"))
        args = build_parser().parse_args(["--links", lf, "--out", out, "--parkinfo", ""])
        web = FakeWeb(TOOL, min_gap=0)

        def names_for(it):
            return [it["name"]] + it.get("alt_names", [])
        fx_pages = {it["url"]: it.get("page") for it in fx["links"]}
        fixer = Fixer(web, args, names_for, lambda it: fx_pages.get(it["url"]), lambda *a: None)
        for it in fx["links"]:
            row = fixer.fix(it)
            want = expected[it["url"]]
            good = row.get("new_url") == want["new_url"] and (want.get("how") is None or row.get("how") == want["how"])
            for fld in ("source_url", "read_date", "why"):
                if not row.get(fld):
                    good = False
                    print(f"FAIL missing {fld}")
            if row.get("new_url") and is_archive(row["new_url"]):
                good = False
            print(("ok   " if good else "FAIL ") + f"{it['url']} -> {row.get('new_url')} ({row.get('how')}); {row.get('why', '')[:90]}")
            ok = ok and good
    checks = [
        (stem_norm("Prairie_Spirit_Trail_Map_2019_v2.pdf") == stem_norm("prairie-spirit-trail-map-2024.pdf"), "dates and versions dropped"),
        (text_names_park("Map of Prairie Spirit Trail State Park, Kansas", ["Prairie Spirit Trail State Trail"])[0], "park named"),
        (not text_names_park("Flint Hills Trail map", ["Prairie Spirit Trail State Trail"])[0], "other park not named"),
        (is_archive("https://web.archive.org/web/2020/x.pdf"), "archive links never answers"),
        (banned_reason("https://www.alltrails.com/trail/us/kansas/prairie-spirit") != "", "AllTrails banned"),
        (banned_reason("https://storage.googleapis.com/ks-gov/map.pdf") == "", "government cloud file allowed"),
    ]
    for good, label in checks:
        print(("ok   " if good else "FAIL ") + label)
        ok = ok and good
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


def make_pdf(text):
    """A tiny one-page PDF with the given words (for the offline test)."""
    t = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    stream = f"BT /F1 12 Tf 50 700 Td ({t}) Tj ET".encode()
    objs = [b"<< /Type /Catalog /Pages 2 0 R >>", b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>",
            b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"]
    out, offs = b"%PDF-1.4\n", []
    for i, o in enumerate(objs, 1):
        offs.append(len(out))
        out += f"{i} 0 obj\n".encode() + o + b"\nendobj\n"
    x = len(out)
    out += f"xref\n0 {len(objs) + 1}\n0000000000 65535 f \n".encode()
    out += b"".join(f"{o:010d} 00000 n \n".encode() for o in offs)
    out += f"trailer\n<< /Size {len(objs) + 1} /Root 1 0 R >>\nstartxref\n{x}\n%%EOF\n".encode()
    return out


def build_parser():
    ap = argparse.ArgumentParser(description="KPC dead-link fixer (T2)")
    ap.add_argument("--links", "--in", default="", help="[{ref, url, kind: map|page, agency_host?, name?, page?}]")
    ap.add_argument("--parkinfo", default="data/parkinfo", help="park pins/names folder")
    ap.add_argument("--docs", nargs="*", default=[], help="data/docs/*.json (park names and own pages)")
    ap.add_argument("--sitemaps", default="", help="folder holding T3's sitemaps/<host>.json (default: --out)")
    ap.add_argument("--no-sitemap-read", dest="read_sitemaps", action="store_false",
                    help="only use T3's files; never read a sitemap ourselves")
    ap.add_argument("--no-wayback", dest="wayback", action="store_false")
    ap.add_argument("--no-site-search", dest="site_search", action="store_false")
    ap.add_argument("--search-tries", type=int, default=3, help="how many search-page forms to try per host")
    ap.add_argument("--max-candidates", type=int, default=8, help="links opened per dead link")
    add_common_args(ap)
    return ap


def main():
    args = build_parser().parse_args()
    if args.selftest:
        return selftest()
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
