#!/usr/bin/env python3
"""kpc_map_match.py: T1 map-match second opinion (Kentucky Portable Club).

For each open question "is this official record that park?", it scores how well the candidate
record's outline matches the park (pin inside, size, name, nearby better records, an agency-map
picture) and puts the row in a band: STRONG, WEAK, NOT SURE or CONFLICT. It decides nothing: the club's
rules decide and a person grades. It never writes YES or NO.
"""
import argparse, glob, math, unicodedata

__version__ = "0.1.0"
TOOL = "map-match"

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
from shapely.geometry import Point, Polygon, MultiLineString, LineString, MultiPoint, shape, mapping
import numpy as np
import shapely
from shapely.ops import unary_union
from shapely.validation import make_valid
from pyproj import Geod, Transformer, CRS

GEOD = Geod(ellps="WGS84")
SIMPLIFY_DEG = 0.00003          # about 3 m
NEAR_M = 2000                   # neighbours within 2 km
LINE_NEAR_M = 200               # a line record "has" the pin when the pin is within 200 m of it
M2_PER_ACRE = 4046.8564224

# ------------------------------------------------------------------ names
TYPE_PHRASES = [
    # longest first; removed from both names before comparing
    "public land use zone", "provincial recreation area", "national wildlife refuge", "national wildlife area",
    "national historic site", "national historical park", "national historic park", "national historic trail",
    "national scenic trail", "national recreation area", "national recreation trail", "national natural landmark",
    "national battlefield park", "national battlefield", "national memorial", "national monument", "national preserve",
    "national seashore", "national lakeshore", "national park", "national forest", "national grassland",
    "state conservation area", "state wildlife management area", "wildlife management area", "state natural area",
    "state nature preserve", "state historic site", "state historical park", "state recreation area", "state park",
    "state forest", "state trail", "state fishing lake", "state wildlife area", "state beach", "state reserve",
    "state game land", "state game lands", "game land", "game lands", "conservation area", "conservation park",
    "conservation reserve", "nature reserve", "nature preserve", "natural area", "provincial park",
    "provincial forest", "ecological reserve", "biological reserve", "wilderness area", "wilderness study area",
    "special area of conservation", "special protection area", "site of community importance", "natura 2000",
    "natura2000", "regional park", "county park", "city park", "municipal park", "metro park", "memorial park",
    "recreation area", "recreation park", "recreation site", "historic site", "historical park", "heritage area",
    "marine park", "marine reserve", "marine protected area", "forest reserve", "game reserve", "wildlife refuge",
    "wildlife sanctuary", "bird sanctuary", "protected area", "protected landscape", "landscape park",
    "parque nacional", "parque natural", "reserva natural", "reserva biologica", "area de proteccion",
    "monumento natural", "parc national", "parc naturel", "reserve naturelle", "naturschutzgebiet",
    "landschaftsschutzgebiet", "nationalpark", "naturpark",
    "flora and fauna reserve", "flora and fauna protection area", "natural monument", "scientific reserve",
    "national reserve", "landscape reserve", "local nature reserve", "national nature reserve",
    "recreation management area", "natural features reserve", "naturreservat", "riserva naturale",
    "riserva naturale regionale", "biosphere reserve", "reserva de la biosfera", "reserva de biosfera",
    "taman nasional", "national", "provincial", "regional", "natural", "nature", "monument", "scientific",
    "aboriginal", "blm", "usfs", "nps", "och", "di", "da", "e", "der", "und", "van", "het", "en", "tn", "br", "pn",
    "wma", "nwr", "nwa", "sp", "nf", "np", "nhs", "nm", "sra", "shs", "sna", "spa", "sac", "sci", "pp",
    "park", "parks", "reserve", "preserve", "forest", "trail", "refuge", "sanctuary", "area", "site",
    "the", "of", "and", "de", "la", "le", "du", "del", "des", "et", "y",
]
_TYPE_RX = re.compile(r"\b(" + "|".join(re.escape(p) for p in sorted(TYPE_PHRASES, key=len, reverse=True)) + r")\b")


def fix_mojibake(s):
    s = str(s or "")
    for _ in range(3):
        if not re.search("[\u00c2\u00c3][\u0080-\u00ff]", s):
            break
        try:
            s = s.encode("latin-1").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            break
    return s


def norm(s):
    s = unicodedata.normalize("NFKD", fix_mojibake(s)).encode("ascii", "ignore").decode().lower()
    s = s.replace("&", " and ").replace("'", "")
    s = re.sub(r"\b(st|ste)\.?\s", "saint ", s)
    s = re.sub(r"\bmt\.?\s", "mount ", s)
    s = re.sub(r"\bft\.?\s", "fort ", s)
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def core_words(s):
    n = _TYPE_RX.sub(" ", norm(s))
    w = [x for x in n.split() if len(x) > 1 or x.isdigit()]
    if not w:                                  # name made only of type words: keep them
        w = norm(s).split()
    return w


def _word_in(w, words):
    for x in words:
        if w == x:
            return True
        if len(w) >= 5 and len(x) >= 5 and (fuzz.ratio(w, x) >= 88 or x.startswith(w) or w.startswith(x)):
            return True
    return False


# A record that is a road, track or firebreak is not the park, whatever its name says.
ROADISH = re.compile(r"\b(road|roads|rd|drive|track|tracks|firebreak|firebreaks|fire break|fireline|firelines|"
                     r"break|highway|hwy|street|access|parking|car park|trailhead|ohv|atv|lane|avenue|boundary break|"
                     r"powerline|pipeline|easement|corridor road)\b")
# Designation families: a different family on each side caps the score (Narcisse PP vs Narcisse WMA).
DESIG = [
    ("wma", r"wildlife management area|\bwma\b|game land|state wildlife area|wildlife area"),
    ("refuge", r"wildlife refuge|\bnwr\b|national wildlife area|\bnwa\b"),
    ("forest", r"state forest|national forest|provincial forest|\bsf\b|forest reserve"),
    ("n2k", r"natura 2000|natura2000|special area of conservation|\bsac\b|special protection area|\bspa\b|\bsci\b"),
    ("park", r"state park|provincial park|national park|\bparque nacional\b|\bparc national\b|nationalpark|\bpn\b"),
    ("landscape", r"cultural landscape|world heritage"),
    ("scenic", r"national scenic area|scenic area"),
    ("trail", r"\btrail\b|\bsendero\b|\bweg\b"),
    # Nov 3 (Mapping, remake after Quality's grade): the kinds the hand-join drops turned on. Without them, "X State Natural Area"
    # vs "X Wildlife Area" scored 1.0 and came out STRONG. "natural heritage area" lands in both natural and historic; that is fine,
    # because the families are sets and only a pair with NO shared family counts.
    ("natural", r"state natural area|natural area|nature preserve|dedicated nature preserve|scientific area|natural heritage area"),
    ("historic", r"historic site|historical site|historic park|historical park|national monument|state monument|heritage area|"
                 r"heritage corridor"),
    ("recreation", r"state recreation area|recreation area|\bsra\b|recreation park|recreational area"),
]
# Kind pairs where agencies rename the same place or name a piece after the park (Koreshan State Historic Site -> Koreshan State
# Park, Whitefish Dunes SNA inside Whitefish Dunes State Park, Waterloo Unit State Game Land = the Waterloo Wildlife Unit of
# Waterloo SRA). Any pair that touches the three Nov 3 families is a question for a person (NOT SURE: "possible rename, check the
# agency page"), never a lower score, because a cap would turn a rename into WEAK and could be read as backing a drop (Quality,
# Nov 3). The one Nov 3 pair that keeps the cap is natural <-> wma/refuge (Millington, Acadia Cliffs, Lodi Marsh, Dewey Marsh).
# Pairs between the older families (Narcisse PP vs Narcisse WMA) keep the cap as before.
NEW_KINDS = {"natural", "historic", "recreation"}
CAPPED_NEW_PAIRS = {frozenset(p) for p in (("natural", "wma"), ("natural", "refuge"))}


def _rename_prone(a, b):
    return bool({a, b} & NEW_KINDS) and frozenset((a, b)) not in CAPPED_NEW_PAIRS


def desig_family(s):
    n = norm(s)
    return {k for k, rx in DESIG if re.search(rx, n)}


def kind_pair(park, text):
    """None when the two names share a designation family (or one side has none). Otherwise ("rename", "park <-> historic") for
    a rename-prone pair (any pair touching natural / historic / recreation except natural <-> wma/refuge), or
    ("different", "natural <-> wma") for a real kind difference (the cap stays for these)."""
    fp, fr = desig_family(park), desig_family(text)
    if not fp or not fr or (fp & fr):
        return None
    pairs = sorted(f"{a} <-> {b}" for a in sorted(fp) for b in sorted(fr) if _rename_prone(a, b))
    if pairs:
        return "rename", pairs[0]
    return "different", f"{'/'.join(sorted(fp))} <-> {'/'.join(sorted(fr))}"


def name_score(park, text):
    """0-1. token-set similarity of the names without type words, gated by how many of the
    park's own words are in the record text (so "Lake" can't match "Lake Cumberland"), with
    a cap when the record is a road / firebreak or a different kind of designation."""
    pw, rw = core_words(park), core_words(text)
    if not pw or not rw:
        return 0.0
    ts = fuzz.token_set_ratio(" ".join(pw), " ".join(rw)) / 100.0
    cp = sum(_word_in(w, rw) for w in pw) / len(pw)
    cr = sum(_word_in(w, pw) for w in rw) / len(rw)
    sc = ts * (0.5 + 0.5 * cp) * (0.6 + 0.4 * cr)
    if ROADISH.search(norm(text)) and not ROADISH.search(norm(park)):
        sc = min(sc, 0.6)
    kp = kind_pair(park, text)
    if kp and kp[0] == "different":       # natural <-> wma/refuge and the like: a real kind difference, capped (STRONG -> WEAK)
        sc = min(sc, 0.75)
    return round(sc, 3)


NAMEISH_FIELD = re.compile(r"(name|nm$|_nm|alias|unit|desig|title|label|estate|site_?n|area_?n|park|loc_?n|"
                           r"nom|nombre|bezeich|gebiet|sitename)", re.I)
SKIP_FIELD = re.compile(r"(objectid|fid$|shape|globalid|code$|_id$|^id$|date|url|link|status|gis_|created|edited)", re.I)


def record_texts(attrs, name_field, record_name):
    texts = []
    if record_name:
        texts.append(("record name", str(record_name)))
    if name_field and attrs.get(name_field) not in (None, ""):
        texts.append((name_field, str(attrs[name_field])))
    desig = ""
    for k, v in (attrs or {}).items():
        if not isinstance(v, str) or not v.strip() or len(v) > 200:
            continue
        if SKIP_FIELD.search(k) or not NAMEISH_FIELD.search(k):
            continue
        texts.append((k, v))
        if re.search(r"desig|type", k, re.I) and not desig:
            desig = v
    if desig and record_name:
        texts.append(("name + designation", f"{record_name} {desig}"))
    seen, out = set(), []
    for k, v in texts:
        if v.lower() not in seen:
            seen.add(v.lower())
            out.append((k, v))
    return out


def best_name(park, attrs, name_field, record_name):
    best = (0.0, "", "")
    for k, v in record_texts(attrs, name_field, record_name):
        sc = name_score(park, v)
        if sc > best[0]:
            best = (sc, k, v)
    return best

# ------------------------------------------------------------------ geometry


def esri_to_shape(g):
    """ArcGIS JSON geometry (outSR 4326) -> shapely geometry, or None."""
    if not g:
        return None
    try:
        if "rings" in g:
            geom = None
            for ring in g["rings"]:
                if len(ring) < 4:
                    continue
                p = Polygon([(c[0], c[1]) for c in ring])
                if not p.is_valid:
                    p = make_valid(p)
                geom = p if geom is None else geom.symmetric_difference(p)
            return make_valid(geom) if geom is not None and not geom.is_valid else geom
        if "paths" in g:
            return MultiLineString([[(c[0], c[1]) for c in path] for path in g["paths"] if len(path) >= 2])
        if "x" in g and "y" in g and g["x"] is not None:
            return Point(g["x"], g["y"])
        if "points" in g:
            return MultiPoint([(c[0], c[1]) for c in g["points"]])
    except Exception:
        return None
    return None


def local_proj(lat, lon):
    crs = CRS.from_proj4(f"+proj=aeqd +lat_0={lat} +lon_0={lon} +datum=WGS84 +units=m")
    return Transformer.from_crs("EPSG:4326", crs, always_xy=True)


def shp_transform(tr, geom):
    """lon/lat geometry -> local metres, with a pyproj Transformer."""
    def f(xy):
        x, y = tr.transform(xy[:, 0], xy[:, 1])
        return np.column_stack([x, y])
    return shapely.transform(geom, f)


def pin_metrics(geom, lat, lon):
    """(pin_inside, pin_dist_m). Areas: inside the polygon. Lines: within 200 m of the line."""
    if geom is None or geom.is_empty:
        return None, None
    to_m = local_proj(lat, lon)
    gm = shp_transform(to_m, geom)
    p0 = Point(0, 0)
    d = round(gm.distance(p0), 1)
    if geom.geom_type in ("Polygon", "MultiPolygon", "GeometryCollection") and gm.area > 0:
        inside = gm.buffer(0).contains(p0) or d == 0
        return bool(inside), (0.0 if inside else d)
    return d <= LINE_NEAR_M, d


def geod_acres(geom):
    if geom is None or geom.is_empty or geom.geom_type not in ("Polygon", "MultiPolygon", "GeometryCollection"):
        return None
    try:
        a, _ = GEOD.geometry_area_perimeter(geom)
        return round(abs(a) / M2_PER_ACRE, 1)
    except Exception:
        return None


def iou(a, b):
    try:
        lat, lon = a.centroid.y, a.centroid.x
        f = local_proj(lat, lon)
        am, bm = shp_transform(f, a).buffer(0), shp_transform(f, b).buffer(0)
        u = am.union(bm).area
        return round(am.intersection(bm).area / u, 3) if u else None
    except Exception:
        return None

# ------------------------------------------------------------------ acres on a page
ACRE_RX = re.compile(r"(\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)\s*[- ]?\s*(acres?|ac\b|hectares?|ha\b|"
                     r"square\s+miles?|sq\.?\s*mi(?:les)?\b|km2|km²|square\s+kilomet(?:er|re)s?)", re.I)
UNIT_TO_ACRE = {"acre": 1, "ac": 1, "hectare": 2.4710538, "ha": 2.4710538, "square mile": 640, "sq mi": 640,
                "km2": 247.10538, "square kilometer": 247.10538}


def _unit_factor(u):
    u = u.lower().replace("²", "2").replace(".", "")
    u = re.sub(r"\s+", " ", u)
    if u.startswith("acre") or u == "ac":
        return 1
    if u.startswith("hectare") or u == "ha":
        return 2.4710538
    if "mi" in u:
        return 640
    return 247.10538


def page_acres(html, park):
    """The park's size stated on its own page: the largest acre figure in a sentence that names
    the park (or says the park/area covers ...). None if the page gives no clear figure."""
    txt = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", html)
    txt = re.sub(r"(?s)<[^>]+>", " ", txt)
    txt = re.sub(r"&nbsp;|&#160;", " ", txt)
    txt = re.sub(r"\s+", " ", txt)
    words = set(core_words(park))
    best = None
    for sent in re.split(r"(?<=[.!?])\s+|\s{2,}|\|", txt):
        if len(sent) > 600:
            continue
        ms = list(ACRE_RX.finditer(sent))
        if not ms:
            continue
        sn = set(norm(sent).split())
        names_it = bool(words & sn)
        covers = re.search(r"\b(covers?|encompass\w*|spans?|totals?|consists? of|comprises?|"
                           r"the (park|area|preserve|refuge|forest|reserve) (is|has|includes))\b", sent, re.I)
        if not (names_it or covers):
            continue
        for m in ms:
            try:
                v = float(m.group(1).replace(",", "")) * _unit_factor(m.group(2))
            except ValueError:
                continue
            if v >= 0.5 and (best is None or v > best[0]):
                best = (round(v, 1), sent.strip()[:160])
    return best

# ------------------------------------------------------------------ club files


def load_pins(parkinfo_dir, pota_tiles):
    pins = {}
    for f in sorted(glob.glob(os.path.join(parkinfo_dir, "*.json"))) if parkinfo_dir else []:
        try:
            d = json.load(open(f, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        for ref, row in (d.get("parks") or {}).items():
            try:
                pins[ref] = {"name": row[0], "website": row[1], "lat": float(row[5]), "lon": float(row[6]),
                             "src": os.path.basename(f)}
            except (TypeError, ValueError, IndexError):
                pass
    for f in sorted(glob.glob(os.path.join(pota_tiles, "*.json"))) if pota_tiles else []:
        try:
            d = json.load(open(f, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        rows = d if isinstance(d, list) else (d.get("rows") or d.get("parks") or [])
        for row in rows:
            try:
                if row[0] not in pins:
                    pins[row[0]] = {"name": row[1], "website": "", "lat": float(row[2]), "lon": float(row[3]),
                                    "src": "pota/t/" + os.path.basename(f)}
            except (TypeError, ValueError, IndexError):
                pass
    return pins


def load_docs(patterns):
    docs = {}
    for pat in patterns or []:
        for f in sorted(glob.glob(pat)):
            try:
                d = json.load(open(f, encoding="utf-8"))
            except (OSError, ValueError):
                continue
            for ref, v in (d.get("parks") or {}).items():
                if isinstance(v, dict):
                    docs[ref] = v
    return docs


def load_pictures(path):
    if not path:
        return {}
    try:
        d = json.load(open(path, encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    out = {}
    for m in d.get("maps", []):
        if m.get("ref") and m.get("files"):
            out.setdefault(m["ref"], m)
    return out


def load_questions(patterns, include_answered):
    rows, seen = [], set()
    scripts = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    from kpc_json_any import glob_json_any, load_json_any
    for pat in patterns:
        for f in glob_json_any(pat):
            try:
                d = load_json_any(f)
            except (OSError, ValueError):
                continue
            qs = d.get("questions") if isinstance(d, dict) else d
            for q in qs or []:
                if not isinstance(q, dict) or not q.get("ref") or not q.get("layer") or \
                        (q.get("record") in (None, "") and not q.get("record_name")):
                    continue
                if q.get("answer") not in (None, "") and not include_answered:
                    continue
                k = qkey(q)
                if k in seen:                  # the same question twice: score it once
                    continue
                seen.add(k)
                q = dict(q)
                q["_file"] = os.path.basename(f)
                rows.append(q)
    return rows

# ------------------------------------------------------------------ ArcGIS reads


def qkey(q):
    """'ref|record'; a question with no record number is keyed by its record name and layer."""
    if q.get("record") not in (None, ""):
        return f"{q['ref']}|{q['record']}"
    parts = layer_url(q).split("/")
    tail = f"{parts[-3]}/{parts[-1]}" if len(parts) >= 3 else layer_url(q)
    return f"{q['ref']}|name:{q.get('record_name', '')}@{tail}"


def fetch_by_name(web, lyr, q, pin):
    """No record number: find the record by its name (and the pin when the name is shared)."""
    rn = str(q.get("record_name") or "")
    tries = []
    if q.get("name_field"):
        tries.append({"where": f"{q['name_field']} = '" + rn.replace("'", "''") + "'"})
    if pin:
        tries.append({"where": "1=1", "geometry": f"{pin['lon']},{pin['lat']}", "geometryType": "esriGeometryPoint",
                      "inSR": 4326, "spatialRel": "esriSpatialRelIntersects"})
    last = (None, None, lyr, "no record number and no way to find the record")
    for t in tries:
        params = dict(t, outFields="*", returnGeometry="true", outSR=4326, maxAllowableOffset=SIMPLIFY_DEG,
                      geometryPrecision=6, resultRecordCount=50, f="json")
        data, r = web.get_json(lyr + "/query", params=params)
        if data is None or "error" in (data or {}):
            msg = (data or {}).get("error", {}).get("message", "") if data else (r["error"] or f"HTTP {r['status']}")
            if re.search(r"token|sign.?in|not authorized|permission", str(msg), re.I):
                return None, None, r["final_url"], "needs sign-in"
            last = (None, None, r["final_url"], f"the layer refused: {str(msg)[:80]}")
            continue
        feats = data.get("features") or []
        best, best_s = None, -1.0
        for f in feats:
            a = f.get("attributes") or {}
            s = max([name_score(rn, t) for _, t in record_texts(a, q.get("name_field"), None)] or [0.0])
            g = esri_to_shape(f.get("geometry"))
            if pin and g is not None:
                try:
                    if pin_metrics(g, pin["lat"], pin["lon"])[0]:
                        s += 0.01
                except Exception:
                    pass
            if s > best_s:
                best, best_s = f, s
        if best is not None and best_s >= 0.85:
            return esri_to_shape(best.get("geometry")), best.get("attributes") or {}, r["final_url"], ""
        last = (None, None, r["final_url"], f"no record named '{rn[:60]}' found in the layer")
    return last


def layer_url(q):
    u = (q.get("layer") or q.get("url") or "").split("?")[0].rstrip("/")
    return re.sub(r"/query$", "", u)


def fetch_record(web, lyr, oid):
    params = {"objectIds": oid, "outFields": "*", "returnGeometry": "true", "outSR": 4326,
              "maxAllowableOffset": SIMPLIFY_DEG, "geometryPrecision": 6, "f": "json"}
    data, r = web.get_json(lyr + "/query", params=params)
    if data is None:
        return None, None, r["final_url"], (r["error"] or f"HTTP {r['status']}")
    if "error" in data:
        msg = str(data["error"].get("message", "server error"))
        if re.search(r"token|sign.?in|not authorized|permission", msg, re.I):
            return None, None, r["final_url"], "needs sign-in"
        return None, None, r["final_url"], f"the layer refused: {msg[:80]}"
    feats = data.get("features") or []
    if not feats:
        return None, None, r["final_url"], "the layer has no record with that number"
    f = feats[0]
    return esri_to_shape(f.get("geometry")), f.get("attributes") or {}, r["final_url"], ""


def fetch_nearby(web, lyr, lat, lon):
    dlat = NEAR_M / 111_320.0
    dlon = NEAR_M / (111_320.0 * max(0.05, math.cos(math.radians(lat))))
    env = f"{lon - dlon},{lat - dlat},{lon + dlon},{lat + dlat}"
    params = {"geometry": env, "geometryType": "esriGeometryEnvelope", "inSR": 4326,
              "spatialRel": "esriSpatialRelIntersects", "outFields": "*", "returnGeometry": "false",
              "resultRecordCount": 200, "f": "json", "where": "1=1"}
    data, r = web.get_json(lyr + "/query", params=params)
    if data is None or "error" in (data or {}):
        return None, r["final_url"]
    return data.get("features") or [], r["final_url"]


def oid_of(attrs):
    for k, v in attrs.items():
        if k.lower() in ("objectid", "fid", "objectid_1", "oid", "esri_oid"):
            return v
    return None

# ------------------------------------------------------------------ pictures


def government_imagery(web, lat, lon, half_m, px):
    """USGS National Map imagery (US only). Returns a PIL image or None."""
    if not (17 < lat < 72 and -180 < lon < -64):
        return None
    dlat = half_m / 111_320.0
    dlon = half_m / (111_320.0 * max(0.05, math.cos(math.radians(lat))))
    url = "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/export"
    params = {"bbox": f"{lon - dlon},{lat - dlat},{lon + dlon},{lat + dlat}", "bboxSR": 4326, "imageSR": 4326,
              "size": f"{px},{px}", "format": "jpg", "f": "image"}
    r = web.get(url, params=params, max_bytes=8_000_000)
    if r["status"] != 200 or not r["content"][:3] == b"\xff\xd8\xff":
        return None
    from PIL import Image
    try:
        return Image.open(io.BytesIO(r["content"])).convert("RGB")
    except Exception:
        return None


def agency_page_image(web, q, pic, doc, picture_dir):
    """The agency map page: a saved picture map first, else page 1 of the docs PDF map."""
    from PIL import Image
    if pic:
        f = pic["files"][0]
        if picture_dir and os.path.exists(os.path.join(picture_dir, f)):
            try:
                return Image.open(os.path.join(picture_dir, f)).convert("RGB"), pic.get("source_url", ""), "saved picture map"
            except Exception:
                pass
        raw = "https://raw.githubusercontent.com/KentuckyPortableClub/KPC-Data/picture-maps/" + f
        r = web.get(raw, max_bytes=10_000_000, check_robots=False)
        if r["status"] == 200:
            try:
                return Image.open(io.BytesIO(r["content"])).convert("RGB"), pic.get("source_url", ""), "saved picture map"
            except Exception:
                pass
    m = (doc or {}).get("map") or {}
    if m.get("url") and m.get("status") == "ok" and (m.get("kind") == "pdf" or m["url"].lower().split("?")[0].endswith(".pdf")):
        r = web.get(m["url"], max_bytes=20_000_000)
        if r["status"] == 200 and r["content"][:5] == b"%PDF-":
            try:
                import pypdfium2 as pdfium
                d = pdfium.PdfDocument(r["content"])
                pg = d[0]
                w, h = pg.get_size()
                img = pg.render(scale=min(3.0, 1400 / max(w, h))).to_pil().convert("RGB")
                return img, m["url"], "agency PDF map, page 1"
            except Exception:
                return None, m["url"], ""
    return None, "", ""


def pdf_is_georeferenced(content):
    head = content[:4_000_000]
    return bool(re.search(rb"/LGIDict|/GPTS|/Measure\s*<<[^>]*?/Subtype\s*/GEO", head))


def draw_side_by_side(out_dir, key, geom, lat, lon, sat, agency_img, title, note):
    from PIL import Image, ImageDraw
    size = 800
    left = sat.resize((size, size)) if sat is not None else Image.new("RGB", (size, size), (235, 235, 228))
    d = ImageDraw.Draw(left)
    # frame = the outline's box (at least 1 km) around the pin
    to_m = local_proj(lat, lon)
    gm = shp_transform(to_m, geom)
    minx, miny, maxx, maxy = gm.bounds
    half = max(500.0, abs(minx), abs(maxx), abs(miny), abs(maxy)) * 1.1
    half = min(half, 60_000.0)

    def px(x, y):
        return ((x + half) / (2 * half) * size, (half - y) / (2 * half) * size)

    def draw_line(coords, width=4):
        pts = [px(x, y) for x, y in coords]
        if len(pts) >= 2:
            d.line(pts, fill=(255, 230, 0), width=width)

    parts = getattr(gm, "geoms", [gm])
    for g in parts:
        if g.geom_type == "Polygon":
            draw_line(list(g.exterior.coords))
            for h in g.interiors:
                draw_line(list(h.coords), 2)
        elif g.geom_type in ("LineString", "LinearRing"):
            draw_line(list(g.coords))
        elif g.geom_type == "MultiLineString":
            for ls in g.geoms:
                draw_line(list(ls.coords))
    cx, cy = px(0, 0)
    d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], outline=(255, 0, 0), width=4)
    d.rectangle([0, 0, size, 28], fill=(0, 0, 0))
    d.text((8, 8), (title + ("" if sat is not None else "  (no government satellite image here)"))[:110], fill=(255, 255, 255))
    d.text((8, size - 20), f"yellow = record outline, red = POTA pin, box ~{2 * half / 1000:.1f} km", fill=(255, 255, 0))
    if agency_img is not None:
        r = agency_img.copy()
        r.thumbnail((size, size))
        right = Image.new("RGB", (size, size), (255, 255, 255))
        right.paste(r, ((size - r.width) // 2, (size - r.height) // 2))
    else:
        right = None
    W = size * (2 if right is not None else 1)
    canvas = Image.new("RGB", (W, size + 30), (255, 255, 255))
    canvas.paste(left, (0, 0))
    if right is not None:
        canvas.paste(right, (size, 0))
    ImageDraw.Draw(canvas).text((8, size + 8), note[:200], fill=(0, 0, 0))
    canvas.thumbnail((1600, 1600))
    name = re.sub(r"[^A-Za-z0-9_-]+", "_", key)[:80] + ".jpg"
    path = safe_out_path(out_dir, "pictures", name)
    canvas.save(path, "JPEG", quality=70)
    return "pictures/" + name

# ------------------------------------------------------------------ bands


def band_of(m):
    reasons_conf, reasons_weak = [], []
    if m["pin_inside"] is False:
        reasons_conf.append(f"the POTA pin is {m['pin_dist_m']:.0f} m outside the record")
    ratio = m.get("acres_ratio")
    if ratio is not None and ratio >= 10:
        reasons_conf.append(f"the sizes are {ratio:.0f}x apart")
    if m.get("better_nearby"):
        b = m["better_nearby"][0]
        reasons_conf.append(f"record {b['record']} ('{b['name']}') nearby matches the park name better")
    if reasons_conf:
        return "CONFLICT", reasons_conf
    if m.get("kind_rename"):
        # Nov 3: a rename-prone kind pair is a question, never WEAK, and never a reason to drop a record.
        return "NOT SURE", [f"possible rename ({m['kind_rename']}): check the agency page; this never backs a drop"]
    if m.get("kind_cap") and m.get("pin_inside") is True and ratio is not None and ratio <= 1.1:
        # Nov 3 re-cut (Quality should-fix, kind_pairs_check): one place under two labels - AR "Natural Area WMA" (Nacatoch, Sweden
        # Creek, Railroad Prairie), MS Theodore A. Mars Jr. Memorial Wildlife Refuge = WMA, Sam Parr SP = SFWA, Cardigan SP/SF.
        # The same acres within 10% AND the pin inside: a question for a person, never WEAK, never a drop reason.
        return "NOT SURE", [f"one place, two labels? ({m['kind_cap']}; same acres within 10%, pin inside): check the agency page; this never backs a drop"]
    if m["pin_inside"] is None:
        reasons_weak.append("the pin could not be checked")
    if m["name_score"] < 0.85:
        reasons_weak.append(f"the names only partly match ({m['name_score']:.2f})")
    if ratio is not None and ratio > 2:
        reasons_weak.append(f"the sizes are {ratio:.1f}x apart")
    if m.get("nearby_checked") is False:
        reasons_weak.append("nearby records could not be checked")
    if reasons_weak:
        return "WEAK", reasons_weak
    return "STRONG", ["pin inside, names match, sizes agree (or no size to compare), no better record nearby"]

# ------------------------------------------------------------------ one row


def match_row(web, q, pins, docs, pictures, args, out_dir):
    key = qkey(q)
    lyr = layer_url(q)
    base = {"ref": q["ref"], "park": q.get("park", ""), "record": q["record"], "record_name": q.get("record_name", ""),
            "layer": lyr, "question_file": q.get("_file", ""), "read_date": today()}
    pin = pins.get(q["ref"])
    if pin is None and args.pota_api:
        data, r = web.get_json(f"https://api.pota.app/park/{q['ref']}", ttl_days=30)
        if data and data.get("latitude") is not None:
            pin = {"name": data.get("name", ""), "website": data.get("website", "") or "",
                   "lat": float(data["latitude"]), "lon": float(data["longitude"]), "src": "api.pota.app"}
            pins[q["ref"]] = pin
    if q.get("record") not in (None, ""):
        rec_geom, attrs, src, err = fetch_record(web, lyr, q["record"])
    else:
        rec_geom, attrs, src, err = fetch_by_name(web, lyr, q, pin)
        if not err:
            base["record_found_by_name"] = oid_of(attrs)
    base["source_url"] = src
    if err:
        return key, dict(base, pin_inside=None, pin_dist_m=None, acres_record=None, acres_park=None, acres_ratio=None,
                         name_score=None, iou=None, better_nearby=[], picture=None, band="WEAK",
                         why=f"Could not read the record: {err}.", error=err)
    park_name = q.get("park") or (pin or {}).get("name", "")
    ns, ns_field, ns_text = best_name(park_name, attrs, q.get("name_field"), q.get("record_name"))
    if pin is None:
        inside, dist = None, None
    else:
        inside, dist = pin_metrics(rec_geom, pin["lat"], pin["lon"])
    acres_rec = geod_acres(rec_geom)
    # the park's stated size, from its own page
    acres_park, acres_how = None, ""
    if args.read_pages:
        pages = []
        doc = docs.get(q["ref"]) or {}
        for u in [doc.get("page"), (pin or {}).get("website")]:
            if u and u.startswith("http") and u not in pages:
                pages.append(u)
        for u in pages[:2]:
            r = web.get(u, max_bytes=5_000_000)
            ctype = r["headers"].get("content-type", "")
            if r["status"] == 200 and "html" in ctype:
                got = page_acres(r["content"].decode("utf-8", "replace"), park_name)
                if got:
                    acres_park, acres_how = got[0], f"the park page {u} says: \"{got[1]}\""
                    break
    ratio = None
    if acres_rec and acres_park:
        ratio = round(max(acres_rec, acres_park) / max(0.1, min(acres_rec, acres_park)), 2)
    # neighbours
    better, nearby_checked = [], None
    if pin is not None and args.neighbours:
        feats, nsrc = fetch_nearby(web, lyr, pin["lat"], pin["lon"])
        nearby_checked = feats is not None
        for f in feats or []:
            a = f.get("attributes") or {}
            oid = oid_of(a)
            if oid is None or str(oid) == str(q["record"] if q.get("record") not in (None, "") else oid_of(attrs)):
                continue
            rn = a.get(q.get("name_field") or "", "") or ""
            sc, fld, txt = best_name(park_name, a, q.get("name_field"), rn)
            if sc >= 0.85 and sc >= ns + 0.10:
                better.append({"record": oid, "name": str(rn or txt)[:80], "name_score": sc, "field": fld})
        better.sort(key=lambda b: -b["name_score"])
        better = better[:5]
    kp = kind_pair(park_name, ns_text or "")
    m = {"kind_rename": kp[1] if kp and kp[0] == "rename" else None,
         "kind_cap": kp[1] if kp and kp[0] == "different" else None,   # informational: the cap alone never backs a drop
         "pin_inside": inside, "pin_dist_m": dist, "acres_record": acres_rec, "acres_park": acres_park,
         "acres_ratio": ratio, "name_score": ns, "iou": None, "better_nearby": better, "nearby_checked": nearby_checked}
    # agency map: picture + overlap
    picture, iou_note = None, ""
    pic, doc = pictures.get(q["ref"]), docs.get(q["ref"])
    if args.pictures and pin is not None and rec_geom is not None and (pic or ((doc or {}).get("map") or {}).get("url")):
        img, img_src, img_kind = agency_page_image(web, q, pic, doc, args.picture_dir)
        if img is not None:
            to_m = local_proj(pin["lat"], pin["lon"])
            b = shp_transform(to_m, rec_geom).bounds
            half = min(60_000.0, max(500.0, *[abs(v) for v in b]) * 1.1)
            sat = government_imagery(web, pin["lat"], pin["lon"], half, 800)
            picture = draw_side_by_side(out_dir, key, rec_geom, pin["lat"], pin["lon"], sat, img,
                                        f"{q['ref']} {park_name} / record {q['record']} {q.get('record_name', '')}",
                                        f"right: {img_kind} {img_src}")
            m["picture_source"] = img_src
            iou_note = "the agency map has no coordinates, so no overlap was computed"
    if args.agency_outlines:
        f = os.path.join(args.agency_outlines, q["ref"] + ".geojson")
        if os.path.exists(f) and rec_geom is not None:
            try:
                gj = json.load(open(f))
                feats = gj.get("features") or [gj]
                ag = unary_union([shape(x.get("geometry") or x) for x in feats])
                m["iou"] = iou(rec_geom, ag)
                iou_note = f"overlap with the georeferenced agency outline {os.path.basename(f)}: IoU {m['iou']}"
            except Exception:
                pass
    band, reasons = band_of(m)
    why_bits = [f"{band}: " + "; ".join(reasons) + "."]
    if inside is not None:
        why_bits.append(("Pin inside the record." if inside else f"Pin {dist:.0f} m from the record.")
                        if rec_geom is not None and rec_geom.geom_type not in ("LineString", "MultiLineString")
                        else f"Pin {dist:.0f} m from the line (counted as 'inside' within {LINE_NEAR_M} m).")
    why_bits.append(f"Best name match {ns:.2f} on {ns_field} '{ns_text[:60]}'.")
    if acres_park:
        why_bits.append(f"Record about {acres_rec} acres, {acres_how[:200]}")
    elif acres_rec:
        why_bits.append(f"Record about {acres_rec} acres; no park size found to compare.")
    if iou_note:
        why_bits.append(iou_note + ".")
    if pin is None:
        why_bits.append("No POTA pin found for this park.")
    out = dict(base, **m, picture=picture, band=band, why=" ".join(why_bits))
    out.pop("nearby_checked", None)
    return key, out

# ------------------------------------------------------------------ main


def run(args):
    out_dir = args.out
    os.makedirs(out_dir, exist_ok=True)
    log_path = safe_out_path(out_dir, "run_log.txt")
    logf = open(log_path, "a", encoding="utf-8")

    def log(*a):
        s = " ".join(str(x) for x in a)
        print(s, flush=True)
        logf.write(s + "\n")
        logf.flush()

    qpats = args.questions
    rows = load_questions(qpats, args.include_answered)
    if args.refs:
        want = set(x.strip() for x in open(args.refs, encoding="utf-8").read().splitlines() if x.strip() and not x.startswith("#"))
        rows = [q for q in rows if qkey(q) in want or q["ref"] in want]
    rows = [q for q in rows if area_ok(q.get("area") or q.get("st", ""), args.areas)]
    if args.limit:
        rows = rows[: args.limit]
    if not rows and not qpats:
        log("no question files given")
        return EXIT_BAD_INPUT
    pins = load_pins(args.parkinfo, args.pota_tiles)
    docs = load_docs(args.docs)
    pictures = load_pictures(args.pictures_index)
    log(f"KPC map-match {__version__}: {len(rows)} rows, {len(pins)} pins, {len(docs)} docs rows, "
        f"{len(pictures)} picture maps; read {today()}")
    web = Web(TOOL, cache_dir=args.cache or None, log=log)
    state = State(out_dir, args.resume)
    res_path = safe_out_path(out_dir, "map_match.json")
    results = {}
    if args.resume and os.path.exists(res_path):
        try:
            results = json.load(open(res_path))
        except ValueError:
            results = {}
    budget = Budget(args.max_minutes)
    left = 0
    for i, q in enumerate(rows):
        key = qkey(q)
        if state.is_done(key) and key in results:
            continue
        if budget.over():
            left = sum(1 for r in rows[i:] if not state.is_done(qkey(r)))
            break
        try:
            k, row = match_row(web, q, pins, docs, pictures, args, out_dir)
        except Exception as e:           # one bad row never stops the batch
            k, row = key, {"ref": q["ref"], "record": q["record"], "band": "WEAK", "read_date": today(),
                           "source_url": layer_url(q), "why": f"CAN'T TELL: the tool hit an error ({type(e).__name__}: {e})."}
        results[k] = row
        state.mark(k)
        write_json(res_path, results)
        state.save(requests=web.n_requests)
        log(f"[{i + 1}/{len(rows)}] {k} {row.get('band')} name={row.get('name_score')} pin_in={row.get('pin_inside')} "
            f"dist={row.get('pin_dist_m')} ratio={row.get('acres_ratio')} better={len(row.get('better_nearby') or [])}")
    summary = {"read_date": today(), "rows": len(results),
               "bands": {b: sum(1 for r in results.values() if r.get("band") == b) for b in ("STRONG", "WEAK", "NOT SURE", "CONFLICT")},
               "requests": web.n_requests, "resting_hosts": web.resting, "left": left}
    write_json(safe_out_path(out_dir, "summary.json"), summary)
    log(json.dumps(summary))
    if left:
        log(f"time is up: {left} rows left; run again with --resume")
        return EXIT_TIME
    return EXIT_DONE

# ------------------------------------------------------------------ self test


def selftest():
    """Offline: made-up layer answers, run the real code, compare bands with tests/expected.json."""
    here = os.path.dirname(os.path.abspath(__file__))
    tdir = os.path.join(here, "tests")
    fx = json.load(open(os.path.join(tdir, "fake_layer.json")))
    expected = json.load(open(os.path.join(tdir, "expected.json")))
    ok = True

    class FakeWeb(Web):
        def get(self, url, params=None, **kw):
            params = params or {}
            full = url + "?" + urllib.parse.urlencode(params)
            res = {"status": 200, "url": full, "final_url": full, "headers": {"content-type": "application/json"},
                   "content": b"", "error": ""}
            if banned_reason(full):
                res.update(status=None, error=banned_reason(full))
                return res
            if url.startswith("https://fake.gov/page/"):
                res["headers"]["content-type"] = "text/html"
                res["content"] = fx["pages"].get(url, "<p>nothing</p>").encode()
                return res
            if "objectIds" in params:
                f = fx["records"].get(str(params["objectIds"]))
                res["content"] = json.dumps({"features": [f] if f else []}).encode()
                return res
            if "geometry" in params:
                res["content"] = json.dumps({"features": [{"attributes": a} for a in fx["nearby"]]}).encode()
                return res
            res.update(status=404, error="not in the fixture")
            return res

    import tempfile
    with tempfile.TemporaryDirectory() as td:
        qf = os.path.join(td, "q.json")
        json.dump({"questions": fx["questions"]}, open(qf, "w"))
        pd = os.path.join(td, "parkinfo")
        os.makedirs(pd)
        json.dump({"parks": fx["pins"]}, open(os.path.join(pd, "US-ZZ.json"), "w"))
        out = os.path.join(td, "out")
        args = build_parser().parse_args(["--questions", qf, "--parkinfo", pd, "--out", out, "--no-pictures",
                                          "--no-pota-api", "--include-answered"])
        global Web_class
        pins = load_pins(pd, None)
        web = FakeWeb(TOOL, offline=False, min_gap=0)
        got = {}
        for q in load_questions([qf], True):
            k, row = match_row(web, q, pins, {}, {}, args, out)
            got[k] = row
            for fld in ("source_url", "read_date", "why"):
                if not row.get(fld):
                    print(f"FAIL {k}: missing {fld}")
                    ok = False
            if re.search(r"\b(YES|NO)\b", json.dumps(row)):
                print(f"FAIL {k}: wrote YES/NO")
                ok = False
        for k, band in expected["bands"].items():
            g = got.get(k, {}).get("band")
            flag = "ok  " if g == band else "FAIL"
            if g != band:
                ok = False
            print(f"{flag} {k}: expected {band}, got {g}  ({got.get(k, {}).get('why', '')[:110]})")
    # unit checks
    checks = [
        (name_score("Athabasca Ranch Public Land Use Zone Recreation Park", "Athabasca Ranch") >= 0.85, "type words dropped"),
        (name_score("Fort Dunvegan National Historic Site", "Dunvegan") < 0.85, "half the name is not enough"),
        (name_score("Lake Cumberland State Resort Park", "Lake") < 0.85, "'Lake' alone is not a match"),
        (banned_reason("https://overpass-api.de/api/interpreter") != "", "Overpass banned"),
        (banned_reason("https://www.google.com/maps/d/viewer?mid=1") != "", "Google My Maps banned"),
        (banned_reason("https://storage.googleapis.com/state-gov/parks.pdf") == "", "government file on cloud storage allowed"),
        (banned_reason("https://en.wikipedia.org/wiki/X") != "", "Wikipedia banned"),
        (banned_reason("https://www.protectedplanet.net/1") != "", "Protected Planet banned"),
        (Robots("User-agent: *\nDisallow: /a\nAllow: /a/b", "KPC").allowed("https://x/a/b/c"), "robots longest match"),
        (not Robots("User-agent: *\nDisallow: /", "KPC").allowed("https://x/y"), "robots disallow all"),
        (page_acres("<p>The 1,250-acre Barren Fork park covers hills.</p>", "Barren Fork State Park")[0] == 1250, "acres from page"),
        (kind_pair("Koreshan State Park", "Koreshan State Historic Site") == ("rename", "park <-> historic"),
         "park <-> historic is a possible rename (NOT SURE)"),
        (name_score("Koreshan State Park", "Koreshan State Historic Site") > 0.75, "a rename is not capped"),
        (name_score("Millington State Natural Area", "Millington Wildlife Area") <= 0.75, "natural <-> wma is still capped"),
        (kind_pair("Narcisse Wildlife Management Area", "Narcisse Provincial Park")[0] == "different", "wma <-> park stays different"),
        (kind_pair("Waterloo Unit State Game Land", "Waterloo Wildlife Unit of Waterloo State Recreation Area")[0] == "rename",
         "wma <-> recreation is a question, not a cap (US-6804)"),
        (kind_pair("Cache River State Natural Area", "Cache River Natural Area WMA") is None, "a shared family is not a kind clash"),
        (band_of({"pin_inside": True, "name_score": 1.0, "kind_rename": "park <-> historic"})[0] == "NOT SURE",
         "a rename pair bands NOT SURE, not WEAK"),
        (band_of({"pin_inside": False, "pin_dist_m": 900.0, "name_score": 1.0, "kind_rename": "park <-> historic"})[0] == "CONFLICT",
         "a pin conflict still wins"),
        (band_of({"pin_inside": True, "name_score": 0.75, "kind_cap": "natural <-> wma", "acres_ratio": 1.04})[0] == "NOT SURE",
         "dual label (Natural Area WMA): same acres + pin inside is NOT SURE, not WEAK"),
        (band_of({"pin_inside": True, "name_score": 0.75, "kind_cap": "wma <-> refuge", "acres_ratio": 1.0})[0] == "NOT SURE",
         "Theodore Mars WMA = memorial refuge: NOT SURE"),
        (band_of({"pin_inside": True, "name_score": 0.75, "kind_cap": "natural <-> wma", "acres_ratio": 1.5})[0] == "WEAK",
         "natural <-> wma with different acres keeps the cap (Millington, Lodi Marsh)"),
        (band_of({"pin_inside": None, "name_score": 0.75, "kind_cap": "park <-> wma", "acres_ratio": 1.0})[0] == "WEAK",
         "pin not checked: the cap stays"),
    ]
    for good, label in checks:
        print(("ok   " if good else "FAIL ") + label)
        ok = ok and good
    try:
        safe_out_path("/tmp/kpc_out_test", "..", "x.json")
        print("FAIL writes outside --out are refused")
        ok = False
    except ValueError:
        print("ok   writes outside --out are refused")
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


def build_parser():
    ap = argparse.ArgumentParser(description="KPC map-match second opinion (T1)")
    ap.add_argument("--questions", "--in", nargs="*", default=[], help="question files (globs ok)")
    ap.add_argument("--parkinfo", default="data/parkinfo", help="folder of park pin files")
    ap.add_argument("--pota-tiles", default="", help="data/pota/t folder (world pins), optional")
    ap.add_argument("--docs", nargs="*", default=[], help="data/docs/*.json (agency map links)")
    ap.add_argument("--pictures-index", default="", help="picture-maps index.json, optional")
    ap.add_argument("--picture-dir", default="", help="local checkout of the picture-maps branch, optional")
    ap.add_argument("--agency-outlines", default="", help="folder of <ref>.geojson georeferenced agency outlines (IoU)")
    ap.add_argument("--include-answered", action="store_true", help="also score rows already answered (tests)")
    ap.add_argument("--refs", default="", help="file of 'ref|record' keys or refs to run (tests)")
    ap.add_argument("--no-pictures", dest="pictures", action="store_false")
    ap.add_argument("--no-pages", dest="read_pages", action="store_false", help="do not read park pages for acres")
    ap.add_argument("--no-neighbours", dest="neighbours", action="store_false")
    ap.add_argument("--no-pota-api", dest="pota_api", action="store_false", help="never ask api.pota.app for a pin")
    add_common_args(ap)
    return ap


def main():
    args = build_parser().parse_args()
    if args.selftest:
        return selftest()
    try:
        return run(args)
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
