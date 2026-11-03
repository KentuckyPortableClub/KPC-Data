#!/usr/bin/env python3
"""kpc_site_check.py: T5 site checker robot (Kentucky Portable Club).

Opens the club's map tools like a guest on a phone (390x844) and on a desktop (1280x900), for a
sample of parks, and reports what a visitor sees: is an outline drawn, does the label match the
key (Official / Approximate / Pin only), is the 2-fer line there word for word, is the
information notice on the page, does the card fit the phone, any console errors.
The steps for each tool are data (tests/recipes.json), not code. It never edits the site.
"""
import argparse, asyncio

__version__ = "0.1.0"
TOOL = "site-check"

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


FERS_LINE = ("⚠️ Parks' boundaries may overlap here, but we can't confirm it. "
             "Check both official boundary maps and make your own call before you count it.")
# PR1 (Nov 2): honest KPC User-Agent, never a browser's (club rule). The phone test still gets a phone-size screen and touch;
# only the site's iPhone-only tweaks (they look for "iPhone" in the User-Agent) are not exercised by this test.
DEVICES = {
    "phone": {"viewport": {"width": 390, "height": 844}, "is_mobile": True, "has_touch": True, "device_scale_factor": 2,
              "user_agent": "KPC-bot/1.0 (+https://github.com/KentuckyPortableClub) KPC-site-check phone"},
    "desktop": {"viewport": {"width": 1280, "height": 900}, "is_mobile": False, "has_touch": False, "device_scale_factor": 1,
                "user_agent": "KPC-bot/1.0 (+https://github.com/KentuckyPortableClub) KPC-site-check desktop"},
}
# Before any page script runs: the guest view (spec: navigator.webdriver = false), and a counter of
# outline shapes Leaflet adds to the map (SVG or canvas; the trail layer's own pane is not counted).
INIT_JS = r"""
Object.defineProperty(Navigator.prototype, 'webdriver', {get: () => false, configurable: true});
window.__kpcShapes = 0; window.__kpcIgnorePanes = [];
(function hook(){
  function patch(L){ if(!L || !L.Map || L.Map.prototype.__kpcHooked) return;
    const add = L.Map.prototype.addLayer;
    L.Map.prototype.addLayer = function(l){ try{ if (L.Path && l instanceof L.Path && !(L.CircleMarker && l instanceof L.CircleMarker)
        && window.__kpcIgnorePanes.indexOf((l.options||{}).pane) < 0) window.__kpcShapes++; }catch(e){} return add.apply(this, arguments); };
    L.Map.prototype.__kpcHooked = true; }
  let _L = window.L;
  if (_L) patch(_L);
  else try { Object.defineProperty(window, 'L', {configurable: true, enumerable: true, get(){ return _L; }, set(v){ _L = v; try{ patch(v); }catch(e){} }}); } catch(e) {}
})();
"""
# order matters: "Pin only (no official outline yet)" and "Approximate outline, not official" both contain
# the words "official outline", so pin and approximate are tested first
LABELS = [("pin", re.compile(r"\b(Pin only|no boundary available|no official map has this park|OpenStreetMap outline \(unofficial\))", re.I)),
          ("approximate", re.compile(r"\bApproximate outline", re.I)),
          ("official", re.compile(r"(?<!no )\bOfficial (outline|trail line|boundary|Kentucky boundary)", re.I))]


def label_class(text):
    for name, rx in LABELS:
        if text and rx.search(text):
            return name
    return None


def norm_expect(e):
    e = str(e or "").lower()
    return {"approx": "approximate", "pin only": "pin", "none": "pin"}.get(e, e)


def load_recipes(path):
    d = json.load(open(path, encoding="utf-8"))
    return {k: v for k, v in d.items() if not k.startswith("_")}


class Pacer:
    """At most one page load every MIN_GAP_S seconds per host (the browser's own sub-requests aside)."""
    def __init__(self, gap):
        self.gap, self.last, self.lock = gap, {}, asyncio.Lock()

    async def wait(self, url):
        host = urllib.parse.urlsplit(url).hostname or ""
        async with self.lock:
            t = time.time() - self.last.get(host, 0)
            if t < self.gap:
                await asyncio.sleep(self.gap - t)
            self.last[host] = time.time()


async def run_recipe(ctx, site, recipe, item, device, out_dir, pacer, log, step_timeout_ms=15000):
    ref = item["ref"]
    fill = lambda s: str(s).replace("{ref}", ref)
    page_url = urllib.parse.urljoin(site, fill(recipe["page"]))
    row = {"ref": ref, "tool": recipe.get("name", ""), "device": device, "page": page_url, "outline_drawn": None,
           "label": "", "label_class": None, "expect": norm_expect(item.get("expect")), "label_ok": None,
           "fers": item.get("fers") or [], "fers_line_ok": None, "notice_ok": None, "fits_phone": None,
           "console_errors": [], "screenshot": None, "steps_failed": [], "dead_buttons": [], "read_date": today(), "source_url": page_url}
    pg = await ctx.new_page()
    errs = row["console_errors"]

    def on_console(m):
        if m.type == "error":
            loc = (m.location or {}).get("url", "")
            if m.text.startswith("Failed to load resource") and not loc:
                return
            errs.append((m.text + (f" ({loc})" if loc and loc not in m.text else ""))[:300])
    pg.on("console", on_console)
    def on_resp(r):   # HQ Nov 1 4:40 PM: list the URL per error (chat 3 fixes the 404s)
        try:
            if r.status >= 400 and not any(r.url in e for e in errs): errs.append(f"HTTP {r.status} {r.url}"[:300])
        except Exception:
            pass
    pg.on("response", on_resp)
    pg.on("pageerror", lambda e: errs.append(f"page error: {str(e)[:280]}"))
    try:
        await pacer.wait(page_url)
        await pg.goto(page_url, wait_until="domcontentloaded", timeout=45000)
        try:
            await pg.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass
        await pg.evaluate("p => { window.__kpcIgnorePanes = p; }", recipe.get("ignore_panes", []))
        if await pg.evaluate("!!document.querySelector('input[type=password]') && !!document.querySelector('input[type=password]').offsetParent"):
            row["steps_failed"].append("the page shows the members' sign-in door to a guest, so the tool can't be checked as a guest")
            row["why"] = "Members-only page: a guest sees the sign-in door, not the tool."
            return row
        paths0 = await pg.evaluate("document.querySelectorAll('.leaflet-container svg path').length")
        shapes0 = await pg.evaluate("window.__kpcShapes || 0")
        async def do_step(st):
            """Run one recipe step; False when it failed and the recipe should stop."""
            do, sel, to = st.get("do"), fill(st.get("sel", "")), int(st.get("timeout", step_timeout_ms))
            try:
                if do == "fill":
                    await pg.fill(sel, fill(st.get("text", "{ref}")), timeout=to)
                elif do == "type":
                    await pg.click(sel, timeout=to)
                    await pg.keyboard.type(fill(st.get("text", "{ref}")), delay=40)
                elif do == "press":
                    await pg.press(sel, st.get("key", "Enter"), timeout=to)
                elif do == "click":
                    loc = pg.locator(sel + " >> visible=true").first
                    await loc.wait_for(state="visible", timeout=to)
                    await pg.wait_for_timeout(int(st.get("settle_ms", 0)))
                    tries = 1 + int(st.get("reclick", 0))
                    for k in range(tries):
                        before = await loc.inner_text(timeout=to) if tries > 1 else ""
                        await loc.click(timeout=to)
                        if k == tries - 1:
                            break
                        # reclick: the button should change (e.g. "LOADING…") or go away; if not, the click was lost
                        await pg.wait_for_timeout(2500)
                        try:
                            if not await loc.is_visible() or (await loc.inner_text(timeout=1000)) != before:
                                break
                        except Exception:
                            break
                        log(f"  [{device}] {ref}: click on {sel} did nothing; clicking again")
                    # still unchanged after every click: a dead button a visitor would hit too
                    if tries > 1:
                        try:
                            dead = await loc.is_visible() and (await loc.inner_text(timeout=1000)) == before
                        except Exception:
                            dead = False
                        if dead:
                            await pg.wait_for_timeout(2500)
                            try:
                                dead = await loc.is_visible() and (await loc.inner_text(timeout=1000)) == before
                            except Exception:
                                dead = False
                        if dead:   # HQ Nov 1 4:40 PM: the outline button on a card whose outline is ALREADY drawn changes nothing: that is fine
                            try:
                                drawn = (await pg.evaluate("window.__kpcShapes || 0")) > shapes0 or \
                                        (await pg.evaluate("document.querySelectorAll('.leaflet-container svg path').length")) > paths0
                                pressed = await loc.evaluate("e => e.getAttribute('aria-pressed') === 'true' || e.classList.contains('on') || e.classList.contains('active') || e.disabled")
                            except Exception:
                                drawn = pressed = False
                            if drawn or pressed:
                                dead = False
                                log(f"  [{device}] {ref}: {sel} changed nothing because the outline is already drawn: fine")
                        if dead:
                            row["dead_buttons"].append(f"'{sel}' did nothing after {tries} clicks")
                            if st.get("if_dead"):
                                log(f"  [{device}] {ref}: {sel} is dead; trying the recipe's if_dead steps")
                                for st2 in st["if_dead"]:
                                    if not await do_step(st2):
                                        break
                elif do == "click_text":
                    loc = pg.locator(sel, has_text=re.compile(r"^\s*" + re.escape(fill(st.get("text", "{ref}"))) + r"\s*$"))
                    await loc.first.wait_for(state="visible", timeout=to)
                    await loc.first.click(timeout=to)
                elif do == "wait_for":
                    await pg.wait_for_selector(sel, state=st.get("state", "visible"), timeout=to)
                elif do == "wait_outline":
                    # until a new outline shape is added, the status changes, or the time runs out
                    end = time.time() + to / 1000
                    s0 = await pg.evaluate(f"(document.querySelector({json.dumps(st.get('status_sel', 'body'))})||{{}}).innerText||''")
                    while time.time() < end:
                        await pg.wait_for_timeout(500)
                        n = await pg.evaluate("window.__kpcShapes || 0")
                        p = await pg.evaluate("document.querySelectorAll('.leaflet-container svg path').length")
                        s1 = await pg.evaluate(f"(document.querySelector({json.dumps(st.get('status_sel', 'body'))})||{{}}).innerText||''")
                        if n > shapes0 or p > paths0 or (st.get("status_sel") and s1 != s0 and label_class(s1)):
                            await pg.wait_for_timeout(int(st.get("settle_ms", 1500)))
                            break
                elif do == "sleep":
                    await pg.wait_for_timeout(int(st.get("ms", 1000)))
                elif do == "goto":
                    u = urllib.parse.urljoin(site, fill(st["url"]))
                    await pacer.wait(u)
                    await pg.goto(u, wait_until="domcontentloaded", timeout=45000)
                else:
                    row["steps_failed"].append(f"unknown step '{do}' in recipes.json")
            except Exception as e:
                row["steps_failed"].append(f"step '{do} {sel}' did not work: {str(e).splitlines()[0][:160]}")
                return bool(st.get("optional"))
            return True

        for st in recipe["steps"]:
            if not await do_step(st):
                break
        rd = recipe.get("read", {})
        card_sel = rd.get("card", "body")
        try:  # a visitor scrolls down to the card: bring it into view before measuring the fit
            await pg.evaluate("s => { const e = s && document.querySelector(s); if (e && !e.closest('.leaflet-container')) e.scrollIntoView({block: 'center'}); }",
                              rd.get("fit") or card_sel)
            await pg.wait_for_timeout(300)
        except Exception:
            pass
        info = await pg.evaluate("""([c, s, l, f, ns, nt]) => {
            const q = x => x ? document.querySelector(x) : null, txt = e => e ? (e.innerText || e.textContent || '').trim() : '';
            const card = q(c), fit = q(f) || card, r = fit ? fit.getBoundingClientRect() : null;
            const notes = ns ? [...document.querySelectorAll(ns)].filter(e => txt(e)) : [];
            return {card: txt(card), status: txt(q(s)), label: txt(q(l)), body: txt(document.body),
                    rect: r ? [r.left, r.top, r.right, r.bottom] : null, vw: innerWidth, vh: innerHeight,
                    sw: document.documentElement.scrollWidth, bw: document.body ? document.body.scrollWidth : 0,
                    notice: notes.length > 0 || (nt ? txt(document.body).indexOf(nt) >= 0 : false),
                    shapes: window.__kpcShapes || 0, paths: document.querySelectorAll('.leaflet-container svg path').length};
        }""", [card_sel, rd.get("status"), rd.get("label"), rd.get("fit"), recipe.get("notice", {}).get("selector"),
               recipe.get("notice", {}).get("text")])
        row["card_text"] = info["card"][:1500]
        row["status_text"] = info["status"][:600]
        row["outline_drawn"] = (info["shapes"] > shapes0) or (info["paths"] > paths0)
        lab = info["label"].strip()
        src = "label"
        if not label_class(lab):
            for nm, t in (("status", info["status"]), ("card", info["card"])):
                if label_class(t):
                    lab, src = next(m.group(0) for _, rx in LABELS for m in [rx.search(t)] if m), nm
                    break
        row["label"], row["label_from"] = lab[:200], src if lab else None
        row["label_class"] = label_class(lab)
        if row["expect"]:
            row["label_ok"] = row["label_class"] == row["expect"]
        if row["fers"]:
            in_card = FERS_LINE in info["card"]
            row["fers_line_ok"] = in_card or FERS_LINE in info["body"]
            row["fers_line_where"] = "card" if in_card else ("page" if row["fers_line_ok"] else None)
        row["notice_ok"] = bool(info["notice"])
        if info["rect"] and device == "phone":
            l, t, r, b = info["rect"]
            # mobile Chrome zooms out to fit a too-wide page, so innerWidth can grow: use the real screen size
            info["vw"] = min(info["vw"], DEVICES[device]["viewport"]["width"])
            info["vh"] = min(info["vh"], DEVICES[device]["viewport"]["height"])
            row["fits_phone"] = l >= -1 and r <= info["vw"] + 1 and t >= -1 and b <= info["vh"] + 1 and \
                max(info["sw"], info["bw"]) <= info["vw"] + 1
            if not row["fits_phone"]:
                row["fit_detail"] = {"card_box": [round(x) for x in info["rect"]], "screen": [info["vw"], info["vh"]],
                                     "page_width": max(info["sw"], info["bw"])}
        # screenshot: JPEG, longest side <= 1600 px, quality 70
        shot = safe_out_path(out_dir, "screens", re.sub(r"[^A-Za-z0-9_.-]+", "_", f"{ref}_{recipe.get('name', 'tool')}_{device}.jpg"))
        os.makedirs(os.path.dirname(shot), exist_ok=True)
        raw = await pg.screenshot(type="jpeg", quality=70)
        from PIL import Image
        im = Image.open(io.BytesIO(raw))
        if max(im.size) > 1600:
            im.thumbnail((1600, 1600))
        im.convert("RGB").save(shot, "JPEG", quality=70, optimize=True)
        row["screenshot"] = os.path.relpath(shot, out_dir)
    except Exception as e:
        row["steps_failed"].append(f"the check broke off: {type(e).__name__}: {str(e).splitlines()[0][:160]}")
    finally:
        try:
            await pg.close()
        except Exception:
            pass
    row["why"] = why_of(row)
    return row


def failures(row):
    f = []
    if row["steps_failed"]:
        f.append("steps failed")
    if row.get("dead_buttons"):
        f.append("a button did nothing when clicked")
    if row["outline_drawn"] is False and row.get("expect") in ("official", "approximate"):
        f.append("no outline drawn")
    if row["label_ok"] is False:
        f.append(f"label '{row['label_class'] or 'none'}' but the key says '{row['expect']}'")
    if row["fers_line_ok"] is False:
        f.append("2-fer line missing")
    if row["notice_ok"] is False:
        f.append("notice missing")
    if row["fits_phone"] is False:
        f.append("card does not fit the phone")
    if row["console_errors"]:
        f.append(f"{len(row['console_errors'])} console error(s)")
    return f


def why_of(row):
    f = failures(row)
    if not f:
        return f"All checks passed on {row['device']}: label '{row['label'] or 'none'}' matches the key."
    return "Problems on " + row["device"] + ": " + "; ".join(f) + "."


def summary_md(results, started, minutes, site):
    rows = [r for lst in results.values() for r in lst]
    bad = [r for r in rows if failures(r)]
    L = [f"# KPC site check — {today()}", "",
         f"Site: {site}  ", f"Checks: {len(rows)} ({len(results)} parks), {len(bad)} with problems; run time {minutes:.1f} min.", ""]
    counts = {}
    for r in bad:
        for x in failures(r):
            k = re.sub(r"'[^']*'", "…", re.sub(r"^\d+ ", "", x))
            counts[k] = counts.get(k, 0) + 1
    if counts:
        L += ["## Problems by kind", ""] + [f"- {k}: {v}" for k, v in sorted(counts.items(), key=lambda kv: -kv[1])] + [""]
    L += ["## Failures first", "", "| ref | tool | device | problem | label seen | screenshot |", "|---|---|---|---|---|---|"]
    for r in sorted(bad, key=lambda r: (r["ref"], r["device"])):
        L.append(f"| {r['ref']} | {r['tool']} | {r['device']} | {'; '.join(failures(r))} | {r['label'] or '—'} | {r['screenshot'] or '—'} |")
    ok = [r for r in rows if not failures(r)]
    L += ["", f"## Passed ({len(ok)})", "", ", ".join(sorted({f"{r['ref']} ({r['device']})" for r in ok})) or "none", ""]
    errs, where = {}, {}
    for r in rows:
        for e in r["console_errors"]:
            errs[e] = errs.get(e, 0) + 1
            where.setdefault(e, set()).add(f"{r['tool']} {r['ref']}")
    if errs:
        L += ["## Console errors seen (most common first; the URL is the file that failed)", ""] + \
             [f"- {v}× {k}  — on: {', '.join(sorted(where[k])[:4])}{' …' if len(where[k]) > 4 else ''}" for k, v in sorted(errs.items(), key=lambda kv: -kv[1])[:30]]
    return "\n".join(L) + "\n"


async def main_async(args, sample, recipes, log):
    from playwright.async_api import async_playwright
    out_dir = args.out
    state = State(out_dir, args.resume)
    res_path = safe_out_path(out_dir, "site_check.json")
    results = {}
    if args.resume and os.path.exists(res_path):
        try:
            results = json.load(open(res_path))
        except ValueError:
            results = {}
    budget = Budget(args.max_minutes)
    t0 = time.time()
    pacer = Pacer(MIN_GAP_S)
    tools = [t for t in args.tools.split(",") if t]
    devices = [d for d in args.devices.split(",") if d]
    for t in tools:
        if t not in recipes:
            log(f"no recipe called '{t}' in {args.recipes}")
            return EXIT_BAD_INPUT
    left = 0
    async with async_playwright() as p:
        launch = {"headless": not args.headed, "args": ["--disable-blink-features=AutomationControlled"]}
        if args.chrome:
            launch["executable_path"] = args.chrome
        try:
            browser = await p.chromium.launch(**launch)
        except Exception:
            alt = next((c for c in ("/usr/bin/google-chrome", "/usr/bin/chromium", "/usr/bin/chromium-browser") if os.path.exists(c)), None)
            if not alt or args.chrome:
                raise
            log(f"Playwright's own Chromium is not installed; using {alt}")
            browser = await p.chromium.launch(**dict(launch, executable_path=alt))

        async def device_worker(device):
            nonlocal left
            # --local-copy: the site's service worker would answer data requests itself, out of reach of the
            # local-copy routes, so it is blocked for that test only
            ctx = await browser.new_context(**DEVICES[device], locale="en-US",
                                            service_workers="block" if args.local_copy else "allow")
            await ctx.add_init_script(INIT_JS)
            if args.local_copy:
                await add_local_routes(ctx, args.local_copy, args.site, log)
            for it in sample:
                for t in tools:
                    key = f"{it['ref']}|{t}|{device}"
                    if state.is_done(key):
                        continue
                    if budget.over():
                        left += 1
                        continue
                    rec = dict(recipes[t], name=t)
                    if rec.get("only_prefixes") and not any(it["ref"].startswith(px) for px in rec["only_prefixes"]):
                        continue
                    if any(it["ref"].startswith(px) for px in rec.get("skip_prefixes", [])):
                        continue
                    row = await run_recipe(ctx, args.site, rec, it, device, out_dir, pacer, log)
                    lst = [r for r in results.get(it["ref"], []) if not (r["tool"] == t and r["device"] == device)]
                    results[it["ref"]] = lst + [row]
                    state.mark(key)
                    write_json(res_path, results)
                    state.save()
                    log(f"[{device}] {it['ref']} {t}: {row['label_class']} (expect {row['expect']}) outline={row['outline_drawn']} "
                        f"fit={row['fits_phone']} errors={len(row['console_errors'])} {'OK' if not failures(row) else 'PROBLEM: ' + '; '.join(failures(row))}")
            await ctx.close()

        await asyncio.gather(*[device_worker(d) for d in devices])
        await browser.close()
    minutes = (time.time() - t0) / 60
    with open(safe_out_path(out_dir, "summary.md"), "w", encoding="utf-8") as f:
        f.write(summary_md(results, t0, minutes, args.site))
    rows = [r for lst in results.values() for r in lst]
    write_json(safe_out_path(out_dir, "summary.json"), {"read_date": today(), "site": args.site, "checks": len(rows),
               "with_problems": sum(1 for r in rows if failures(r)), "minutes": round(minutes, 1), "left": left})
    log(f"done: {len(rows)} checks, {sum(1 for r in rows if failures(r))} with problems, {minutes:.1f} min")
    return EXIT_TIME if left else EXIT_DONE


async def add_local_routes(ctx, local_dir, site, log):
    """--local-copy DIR: answer requests for the club's site and data from DIR when DIR has the file
    (DIR/KPC-Links/<path>, DIR/KPC-Data/<path>); everything else goes to the network as normal."""
    roots = {"https://kentuckyportableclub.github.io/KPC-Links/": os.path.join(local_dir, "KPC-Links"),
             "https://kentuckyportableclub.github.io/KPC-Data/": os.path.join(local_dir, "KPC-Data")}
    if site and site not in roots:
        roots[site] = os.path.join(local_dir, "KPC-Links")
    import mimetypes

    async def handler(route):
        u = route.request.url.split("#")[0]
        for base, d in roots.items():
            if u.startswith(base):
                rel = urllib.parse.unquote(u[len(base):].split("?")[0]) or "index.html"
                f = os.path.realpath(os.path.join(d, rel))
                if f.startswith(os.path.realpath(d) + os.sep) and os.path.isfile(f):
                    ct = mimetypes.guess_type(f)[0] or "application/octet-stream"
                    await route.fulfill(status=200, body=open(f, "rb").read(), headers={"content-type": ct, "access-control-allow-origin": "*"})
                    return
        await route.continue_()
    await ctx.route("**/*", handler)


def load_sample(path):
    d = json.load(open(path, encoding="utf-8"))
    if isinstance(d, dict):
        d = d.get("sample") or d.get("parks") or []
    out = []
    for x in d:
        if isinstance(x, dict) and x.get("ref"):
            out.append({"ref": str(x["ref"]).strip(), "expect": norm_expect(x.get("expect")), "fers": x.get("fers") or []})
    return out


def run(args):
    out_dir = args.out
    os.makedirs(out_dir, exist_ok=True)
    logf = open(safe_out_path(out_dir, "run_log.txt"), "a", encoding="utf-8")

    def log(*a):
        s = " ".join(str(x) for x in a)
        print(s, flush=True)
        logf.write(s + "\n")
        logf.flush()
    if not args.sample or not os.path.exists(args.sample):
        log("--sample file is missing")
        return EXIT_BAD_INPUT
    if banned_reason(args.site):
        log(f"--site is a banned source: {banned_reason(args.site)}")
        return EXIT_BAD_INPUT
    if not args.site.endswith("/"):
        args.site += "/"
    try:
        sample = load_sample(args.sample)
        recipes = load_recipes(args.recipes)
    except (OSError, ValueError) as e:
        log(f"bad input: {e}")
        return EXIT_BAD_INPUT
    if args.areas:
        sample = [s for s in sample if area_ok(s["ref"].split("-")[0], args.areas) or any(s["ref"].startswith(a) for a in args.areas.split(","))]
    if args.limit:
        sample = sample[: args.limit]
    # robots.txt for the site host
    if args.site.startswith("http") and not args.local_copy:
        web = Web(TOOL, log=log)
        rob = web._robots_for(urllib.parse.urlsplit(args.site).scheme, urllib.parse.urlsplit(args.site).netloc)
        if rob is None or not rob.allowed(urllib.parse.urljoin(args.site, "kpc-planner-us.html")):
            log("robots.txt does not allow the site checker on this host")
            return EXIT_DONE
    log(f"KPC site-check {__version__}: {len(sample)} parks × {args.devices} × {args.tools} on {args.site}; read {today()}")
    return asyncio.run(main_async(args, sample, recipes, log))

# ------------------------------------------------------------------ self test (offline: a local page)


def selftest():
    import tempfile, threading, http.server, functools
    here = os.path.dirname(os.path.abspath(__file__))
    fx = os.path.join(here, "tests", "fixture_site")
    with tempfile.TemporaryDirectory() as td:
        class Quiet(http.server.SimpleHTTPRequestHandler):
            def log_message(self, *a, **k):
                pass
        handler = functools.partial(Quiet, directory=fx)
        srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        site = f"http://127.0.0.1:{srv.server_port}/"
        args = build_parser().parse_args(["--site", site, "--sample", os.path.join(here, "tests", "selftest_sample.json"),
                                          "--recipes", os.path.join(here, "tests", "selftest_recipes.json"), "--out", td,
                                          "--tools", "fixture"])
        global MIN_GAP_S
        MIN_GAP_S = 0
        try:
            rc = asyncio.run(main_async(args, load_sample(args.sample), load_recipes(args.recipes), lambda *a: None))
        except Exception as e:
            print(f"FAIL the browser did not start ({type(e).__name__}: {str(e)[:200]}); run 'playwright install chromium' or give --chrome")
            srv.shutdown()
            return 1
        srv.shutdown()
        res = json.load(open(os.path.join(td, "site_check.json")))
        exp = json.load(open(os.path.join(here, "tests", "selftest_expected.json")))
        ok = rc == 0
        for ref, want in exp.items():
            for r in res.get(ref, []):
                good = all(r.get(k) == v for k, v in want.items() if not (k == "fits_phone" and r["device"] != "phone"))
                if r["device"] == "desktop" and r.get("fits_phone") is not None:
                    good = False
                if not r.get("screenshot") or not os.path.exists(os.path.join(td, r["screenshot"])):
                    good = False
                print(("ok   " if good else "FAIL ") + f"{ref} {r['device']}: label={r['label_class']} label_ok={r['label_ok']} outline={r['outline_drawn']} "
                      f"fers={r['fers_line_ok']} notice={r['notice_ok']} fit={r['fits_phone']} errors={len(r['console_errors'])}")
                if not good:
                    print("     want", want)
                ok = ok and good
            if len(res.get(ref, [])) != 2:
                print(f"FAIL {ref}: expected 2 devices")
                ok = False
        for txt, want in (("Pin only (no official outline yet)", "pin"), ("Approximate outline, not official: X", "approximate"),
                          ("Official outline: X (USGS PAD-US)", "official"), ("Official boundary shown: X", "official"),
                          ("Sorry, no boundary available at this time.", "pin"), ("31 spots within 25 miles", None)):
            good = label_class(txt) == want
            print(("ok   " if good else "FAIL ") + f"label of '{txt[:40]}' = {label_class(txt)}")
            ok = ok and good
        md = open(os.path.join(td, "summary.md")).read()
        good = md.index("Failures first") < md.index("Passed")
        print(("ok   " if good else "FAIL ") + "summary.md puts failures first")
        ok = ok and good
        from PIL import Image
        big = max(max(Image.open(os.path.join(td, r["screenshot"])).size) for lst in res.values() for r in lst if r.get("screenshot"))
        print(("ok   " if big <= 1600 else "FAIL ") + f"screenshots ≤1600 px (largest {big})")
        ok = ok and big <= 1600
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


def build_parser():
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser(description="KPC site checker robot (T5)")
    ap.add_argument("--site", default="https://kentuckyportableclub.github.io/KPC-Links/")
    ap.add_argument("--sample", "--in", default="", help="[{ref, expect: official|approximate|pin, fers: [ref,...]}]")
    ap.add_argument("--recipes", default=os.path.join(here, "tests", "recipes.json"))
    ap.add_argument("--tools", default="us_planner", help="comma list of recipe names (see recipes.json)")
    ap.add_argument("--devices", default="phone,desktop")
    ap.add_argument("--local-copy", default="", help="folder with KPC-Links/ and KPC-Data/ files to use instead of the live ones")
    ap.add_argument("--chrome", default="", help="path to a Chrome/Chromium (default: Playwright's own)")
    ap.add_argument("--headed", action="store_true")
    add_common_args(ap)
    return ap


def main():
    args = build_parser().parse_args()
    if args.selftest:
        return selftest()
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
