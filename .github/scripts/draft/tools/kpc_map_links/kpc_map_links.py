#!/usr/bin/env python3
"""
KPC Agency Map-Page Link Extractor
==================================

Given an agency's single "maps & brochures" style index page, find the right
map document (PDF / image / map page) for each of that agency's parks.

Usage:
    python kpc_map_links.py --agencies agency_pages.json [--parks parks.json]
                            [--out out/] [--resume] [--max-minutes 50]
                            [--chunk 1/4] [--only "agency name"]

Inputs
  agency_pages.json : [{agency, state_or_prov, index_url, park_refs:[...],
                        (optional) doc_hosts, follow_patterns, render,
                        wait_for, url_rewrites, max_pages}]
  parks.json        : {ref: {name, type, lat, lon, alt_names:[]}}

Outputs (in --out)
  docs_found.json   : {ref: {page_url, map_url, kind, map_date, match_score,
                             status, why, ...}}
  report.csv        : one row per park ref
  summary.json      : per-agency counts, errors, timings
  state.json        : resume state (per agency + per verified URL)

Rules baked in (from the build spec):
  * only the index URL's host, its agency domain and configured doc_hosts are
    ever requested; Google / OSM / AllTrails / TripAdvisor / Wikipedia are
    hard-blocked even if configured;
  * robots.txt (RFC 9309, longest-match) is honoured for every host, including
    Crawl-delay;
  * strictly one request at a time (the whole tool is sequential), a minimum
    delay per host, exponential back-off on 429/5xx with Retry-After;
  * User-Agent names the club;
  * nothing is final: POSSIBLE rows are for a person to review.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import logging
import os
import re
import sys
import time
import unicodedata
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any, Iterable
from urllib.parse import urljoin, urlparse, urlunparse, unquote

import requests
from bs4 import BeautifulSoup
from rapidfuzz import fuzz

try:  # optional: PDF text check
    from pypdf import PdfReader
except Exception:  # pragma: no cover
    PdfReader = None

VERSION = "0.1.0"
USER_AGENT = os.environ.get(
    "KPC_USER_AGENT",
    f"KPC-MapLinkExtractor/{VERSION} (KPC parks club official-documents bot; "
    "contact: club admins via the KPC website)",
)
UA_TOKEN = "kpc-maplinkextractor"  # product token matched against robots.txt groups

ACCEPT = 0.90
POSSIBLE = 0.75
MAX_PARKS_PER_FILE = 3
DEFAULT_MAX_DEPTH = 2
DEFAULT_MAX_PAGES = 300
DEFAULT_MIN_DELAY = float(os.environ.get("KPC_MIN_DELAY", "1.5"))
MAX_CRAWL_DELAY = 30.0
MAX_DOWNLOAD_BYTES = 60 * 1024 * 1024
TIMEOUT = (15, 60)

FORBIDDEN_HOST_PARTS = (
    "google.", "googleapis.", "goo.gl", "g.co", "gstatic.", "openstreetmap.", "osm.org",
    "alltrails.", "tripadvisor.", "wikipedia.", "wikimedia.", "wikidata.", "bing.com",
    "mapquest.", "waze.", "apple.com/maps", "maps.apple.",
)

DOC_EXT = {".pdf": "PDF", ".jpg": "IMAGE", ".jpeg": "IMAGE", ".png": "IMAGE", ".gif": "IMAGE",
           ".webp": "IMAGE", ".tif": "IMAGE", ".tiff": "IMAGE", ".kmz": "KMZ", ".kml": "KMZ"}
SKIP_EXT = {".zip", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".mp4", ".mp3", ".css", ".js",
            ".ics", ".xml", ".rss", ".svg", ".gpx"}

log = logging.getLogger("kpc_map_links")


# ----------------------------------------------------------------------------------------------
# Name normalisation and scoring
# ----------------------------------------------------------------------------------------------

# Multi-word type phrases first (longest first), mapped to a type family.
TYPE_PHRASES = [
    ("national wild and scenic river", "wsr"), ("wild and scenic river", "wsr"),
    ("national recreation trail", "trail"), ("national scenic trail", "trail"),
    ("state resort park", "park"), ("state historic site", "historic"), ("state historic park", "historic"),
    ("state recreation area", "park"), ("state natural area", "natural"), ("state nature preserve", "natural"),
    ("wildlife management area", "wma"), ("fish and wildlife management area", "wma"),
    ("national wildlife refuge", "nwr"), ("national forest", "nf"), ("state forest", "forest"),
    ("provincial park", "park"), ("conservation area", "ca"), ("conservation reserve", "ca"),
    ("wilderness area", "wilderness"), ("state park trail", "park"), ("state park", "park"),
    ("state beach", "park"), ("state trail", "trail"), ("recreation area", "park"),
    ("outdoor recreation area", "park"), ("hunting access area", "haa"), ("unique area", "unique"),
    ("multiple use area", "unique"), ("geological area", "natural"), ("scenic area", "natural"),
    ("research reserve", "natural"), ("national historical park", "historic"),
]
TYPE_ABBR = {
    "sp": "park", "srp": "park", "shs": "historic", "sra": "park", "wma": "wma", "fwma": "wma",
    "nwr": "nwr", "ca": "ca", "pp": "park", "sf": "forest", "nf": "nf", "wsr": "wsr", "nrt": "trail",
    "haa": "haa", "ua": "unique", "ora": "park", "snp": "natural", "sna": "natural",
}
TYPE_SINGLE = {"wilderness": "wilderness", "preserve": "natural", "refuge": "nwr"}
STOP = {"the", "of", "and", "at", "a", "an", "on", "in", "for", "to", "de", "du", "la", "le", "des"}
GENERIC = {  # words that say nothing about WHICH park a link is for
    "map", "maps", "pdf", "brochure", "brochures", "guide", "guides", "download", "inline", "view",
    "printable", "print", "all", "file", "files", "click", "here", "trail", "trails", "trailmap",
    "campground", "camping", "hunting", "hunt", "quota", "fishing", "boundary", "index", "overview",
    "mobile", "web", "version", "updated", "new", "info", "information", "page", "pages", "sheet",
    "fact", "factsheet", "documents", "document", "media", "upload", "uploads", "wp", "content",
    "sites", "default", "kb", "mb", "area", "areas", "park", "parks", "state", "loc", "location",
    "interactive", "visitor", "general", "regulations", "rules", "jpg", "png", "gif", "jpeg", "kmz",
    "aspx", "html", "htm", "php", "www", "http", "https", "doc", "img", "image", "images", "website",
    "final", "copy", "rev", "revised", "draft", "small", "large", "hi", "res", "lowres", "hires",
}
ZW_RE = re.compile("[\u200b-\u200f\u2060\ufeff\u00ad]")
MAP_WORDS = re.compile(r"\b(map|maps|brochure|trail ?map|guide)\b", re.I)


def _strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


def split_camel(s: str) -> str:
    s = re.sub(r"([a-z])([A-Z])", r"\1 \2", s)
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", s)
    s = re.sub(r"([A-Za-z])(\d)", r"\1 \2", s)
    s = re.sub(r"(\d)([A-Za-z])", r"\1 \2", s)
    return s


def filename_text(url: str) -> str:
    p = urlparse(url)
    name = unquote(p.path.rstrip("/").rsplit("/", 1)[-1])
    name = re.sub(r"\.[A-Za-z0-9]{2,5}$", "", name)
    if re.fullmatch(r"[\d_\-]*|download|index|default|detail", name, re.I):
        name = ""
    return split_camel(name)


def norm_tokens(s: str, drop_generic: bool = False) -> tuple[list[str], set[str]]:
    """Normalise a name -> (tokens, type families found)."""
    if not s:
        return [], set()
    s = ZW_RE.sub("", s)
    s = _strip_accents(s)
    s = s.replace("&", " and ").replace("’", "'")
    s = re.sub(r"'s\b", "s", s)
    s = s.replace("'", "")
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    s = f" {s} "
    families: set[str] = set()
    for phrase, fam in TYPE_PHRASES:
        if f" {phrase} " in s:
            families.add(fam)
            s = s.replace(f" {phrase} ", " ")
    toks = s.split()
    # join runs of single letters: "r f tarter" -> "rf tarter"
    joined: list[str] = []
    buf = ""
    for t in toks:
        if len(t) == 1 and t.isalpha():
            buf += t
        else:
            if buf:
                joined.append(buf)
                buf = ""
            joined.append(t)
    if buf:
        joined.append(buf)
    out = []
    for t in joined:
        if t in TYPE_ABBR:
            families.add(TYPE_ABBR[t]); continue
        if t in TYPE_SINGLE:
            families.add(TYPE_SINGLE[t]); continue
        if t in STOP:
            continue
        if drop_generic and (t in GENERIC or t.isdigit()):
            continue
        out.append(t)
    return out, families


def _tok_match(a: str, b: str) -> bool:
    if a == b:
        return True
    if len(a) >= 5 and len(b) >= 5:
        return fuzz.ratio(a, b) >= 88
    return False


def score_name_vs_field(name_toks: list[str], field_toks: list[str]) -> float:
    """token-set ratio, gated by how many of the park's own tokens appear in the field.

    Plain token_set_ratio gives 100 when EITHER side is a subset of the other, so
    "Lake" would match "Lake Cumberland". Gating by park-token coverage stops that.
    """
    if not name_toks or not field_toks:
        return 0.0
    tsr = fuzz.token_set_ratio(" ".join(name_toks), " ".join(field_toks)) / 100.0
    covered = sum(1 for t in name_toks if any(_tok_match(t, f) for f in field_toks))
    cov = covered / len(name_toks)
    return min(tsr, cov)


# ----------------------------------------------------------------------------------------------
# robots.txt (RFC 9309: group selection by product token, longest match, allow wins ties)
# ----------------------------------------------------------------------------------------------

class Robots:
    def __init__(self, text: str | None, allow_all: bool = False, disallow_all: bool = False):
        self.allow_all = allow_all
        self.disallow_all = disallow_all
        self.rules: list[tuple[bool, str]] = []
        self.crawl_delay: float | None = None
        if text is not None:
            self._parse(text)

    def _parse(self, text: str) -> None:
        groups: list[tuple[list[str], list[tuple[bool, str]], float | None]] = []
        agents: list[str] = []
        rules: list[tuple[bool, str]] = []
        delay: float | None = None
        last_was_agent = False
        for raw in text.splitlines():
            line = raw.split("#", 1)[0].strip()
            if not line or ":" not in line:
                continue
            k, v = line.split(":", 1)
            k = k.strip().lower(); v = v.strip()
            if k == "user-agent":
                if not last_was_agent and agents:
                    groups.append((agents, rules, delay))
                    agents, rules, delay = [], [], None
                agents.append(v.lower())
                last_was_agent = True
            else:
                last_was_agent = False
                if not agents:
                    continue
                if k in ("allow", "disallow"):
                    if v == "" and k == "disallow":
                        continue
                    rules.append((k == "allow", v))
                elif k == "crawl-delay":
                    try:
                        delay = float(v)
                    except ValueError:
                        pass
        if agents:
            groups.append((agents, rules, delay))
        mine = [g for g in groups if any(a != "*" and a in UA_TOKEN for a in g[0])]
        chosen = mine or [g for g in groups if "*" in g[0]]
        for g in chosen:  # RFC 9309: multiple matching groups are merged
            self.rules.extend(g[1])
            if g[2] is not None:
                self.crawl_delay = max(self.crawl_delay or 0, g[2])

    @staticmethod
    def _pat_to_re(p: str) -> re.Pattern:
        end = p.endswith("$")
        if end:
            p = p[:-1]
        rx = "".join(".*" if c == "*" else re.escape(c) for c in p)
        return re.compile("^" + rx + ("$" if end else ""))

    def allowed(self, url: str) -> bool:
        if self.disallow_all:
            return False
        if self.allow_all or not self.rules:
            return True
        p = urlparse(url)
        path = (p.path or "/") + (("?" + p.query) if p.query else "")
        best_len, best_allow = -1, True
        for allow, pat in self.rules:
            if self._pat_to_re(pat).match(path):
                ln = len(pat)
                if ln > best_len or (ln == best_len and allow):
                    best_len, best_allow = ln, allow
        return best_allow


# ----------------------------------------------------------------------------------------------
# Polite sequential HTTP client
# ----------------------------------------------------------------------------------------------

class Blocked(Exception):
    pass


def host_forbidden(host: str) -> bool:
    h = host.lower()
    return any(part in h for part in FORBIDDEN_HOST_PARTS)


class Fetcher:
    def __init__(self, min_delay: float = DEFAULT_MIN_DELAY):
        self.s = requests.Session()
        self.s.headers.update({"User-Agent": USER_AGENT, "Accept-Language": "en"})
        self.min_delay = min_delay
        self.last: dict[str, float] = {}
        self.robots: dict[str, Robots] = {}
        self.requests_made = 0

    def _wait(self, host: str) -> None:
        r = self.robots.get(host)
        delay = self.min_delay
        if r and r.crawl_delay:
            delay = max(delay, min(r.crawl_delay, MAX_CRAWL_DELAY))
        last = self.last.get(host)
        if last is not None:
            gap = time.monotonic() - last
            if gap < delay:
                time.sleep(delay - gap)
        self.last[host] = time.monotonic()

    def robots_for(self, scheme: str, host: str) -> Robots:
        if host in self.robots:
            return self.robots[host]
        url = f"{scheme}://{host}/robots.txt"
        self._wait(host)
        try:
            r = self.s.get(url, timeout=TIMEOUT, allow_redirects=True)
            self.requests_made += 1
            if r.status_code == 200 and "html" not in r.headers.get("content-type", "").lower():
                rob = Robots(r.text)
            elif r.status_code == 200:  # an HTML page served as robots.txt -> treat as none
                rob = Robots(None, allow_all=True)
            elif 400 <= r.status_code < 500:
                rob = Robots(None, allow_all=True)
            else:
                rob = Robots(None, disallow_all=True)
        except requests.RequestException as e:
            log.warning("robots.txt unreachable for %s (%s) -> treating host as disallowed", host, e)
            rob = Robots(None, disallow_all=True)
        self.robots[host] = rob
        return rob

    def check(self, url: str, allowed_hosts: "HostPolicy") -> None:
        p = urlparse(url)
        if p.scheme not in ("http", "https"):
            raise Blocked(f"scheme not allowed: {url}")
        host = p.hostname or ""
        if host_forbidden(host):
            raise Blocked(f"forbidden host by club rule: {host}")
        if not allowed_hosts.ok(host):
            raise Blocked(f"host not an official agency host for this agency: {host}")
        if not self.robots_for(p.scheme, host).allowed(url):
            raise Blocked(f"robots.txt disallows {url}")

    def get(self, url: str, policy: "HostPolicy", method: str = "GET", stream: bool = False,
            max_redirects: int = 6) -> requests.Response:
        """Sequential request with manual redirects (every hop is policy+robots checked)."""
        for _ in range(max_redirects + 1):
            self.check(url, policy)
            host = urlparse(url).hostname or ""
            resp = None
            for attempt in range(5):
                self._wait(host)
                try:
                    resp = self.s.request(method, url, timeout=TIMEOUT, allow_redirects=False, stream=stream)
                    self.requests_made += 1
                except requests.RequestException as e:
                    if attempt == 4:
                        raise
                    back = min(2 ** attempt * 3, 60)
                    log.info("network error %s on %s; backing off %ss", e.__class__.__name__, url, back)
                    time.sleep(back)
                    continue
                if resp.status_code in (429, 500, 502, 503, 504) and attempt < 4:
                    ra = resp.headers.get("Retry-After", "")
                    back = int(ra) if ra.isdigit() else min(2 ** attempt * 5, 120)
                    back = min(back, 120)
                    log.info("HTTP %s on %s; backing off %ss", resp.status_code, url, back)
                    resp.close()
                    time.sleep(back)
                    continue
                break
            assert resp is not None
            if resp.status_code in (301, 302, 303, 307, 308) and resp.headers.get("Location"):
                nxt = urljoin(url, resp.headers["Location"])
                resp.close()
                if resp.status_code == 303:
                    method = "GET"
                url = nxt
                continue
            return resp
        raise Blocked(f"too many redirects: {url}")


@dataclass
class HostPolicy:
    index_host: str
    extra: set[str] = field(default_factory=set)

    @property
    def base(self) -> str:
        parts = self.index_host.split(".")
        if parts[0] in ("www", "app", "apps", "www2") and len(parts) >= 3:
            return ".".join(parts[1:])
        if len(parts) >= 4:
            return ".".join(parts[1:])
        return self.index_host

    def ok(self, host: str) -> bool:
        host = host.lower()
        if host_forbidden(host):
            return False
        b = self.base
        if host == self.index_host or host == b or host.endswith("." + b):
            return True
        return any(host == h or host.endswith("." + h) for h in self.extra)

    def same_site(self, host: str) -> bool:
        """Sub-pages are only followed on the SAME host as the index page (spec step 1)."""
        return host.lower() == self.index_host


# ----------------------------------------------------------------------------------------------
# Crawl and candidate collection
# ----------------------------------------------------------------------------------------------

@dataclass
class Candidate:
    url: str
    kind: str              # PDF / IMAGE / KMZ / MAP PAGE / DOC? (unknown ext, decided on verify)
    text: str
    heading: str
    page_heading: str
    via_text: str
    page_url: str
    depth: int
    nearby: str = ""


def clean_url(u: str, base: str) -> str | None:
    u = (u or "").strip()
    if not u or u.startswith(("mailto:", "tel:", "javascript:", "#", "data:")):
        return None
    full = urljoin(base, u)
    p = urlparse(full)
    if p.scheme not in ("http", "https"):
        return None
    path = re.sub(r"\s+", "%20", p.path.strip())
    return urlunparse((p.scheme, (p.netloc or "").lower(), path or "/", "", p.query.strip(), ""))


def ext_of(url: str) -> str:
    path = urlparse(url).path.lower()
    m = re.search(r"(\.[a-z0-9]{2,5})$", path)
    return m.group(1) if m else ""


def looks_like_doc(a, url: str) -> str | None:
    """Return a kind if this anchor looks like a document/map link, else None."""
    ext = ext_of(url)
    if ext in DOC_EXT:
        return DOC_EXT[ext]
    if ext in SKIP_EXT:
        return None
    cls = " ".join(a.get("class", [])) + " " + (a.get("type") or "")
    if re.search(r"application[-/]pdf|mime-application-pdf|\bpdf\b", cls, re.I):
        return "PDF"
    if re.search(r"image[-/](png|jpe?g|gif)", cls, re.I):
        return "IMAGE"
    path = urlparse(url).path.lower()
    q = urlparse(url).query.lower()
    if re.search(r"/(download|downloads|documents?|files?|media|uploads|shared/static)/", path + "/") or \
       "download" in path or "dl=1" in q or re.match(r"^/s/[a-z0-9]{16,}$", path):
        return "DOC?"
    txt = a.get_text(" ", strip=True)
    if re.search(r"\(pdf\)|\bpdf\b", txt, re.I):
        return "DOC?"
    return None


def nearest_heading(el) -> str:
    h = el.find_previous(["h1", "h2", "h3", "h4", "h5"])
    return h.get_text(" ", strip=True)[:200] if h else ""


def nearby_text(el) -> str:
    """Text of the smallest enclosing block (sentence/list item/table row) around a link."""
    for parent in el.parents:
        if parent.name in ("p", "li", "td", "tr", "dd", "figcaption", "div", "section"):
            t = parent.get_text(" ", strip=True)
            if len(t) > len(el.get_text(" ", strip=True)) + 3:
                return t[:400] if len(t) <= 600 else ""
        if parent.name in ("body", "main", "article"):
            break
    return ""


def page_heading_of(soup) -> str:
    main = soup.find("main") or soup
    for tag in ("h1", "h2"):
        h = main.find(tag)
        if h and h.get_text(strip=True):
            return h.get_text(" ", strip=True)[:200]
    return ""


def is_pagination(a, url: str, cur: str) -> bool:
    t = a.get_text(" ", strip=True).lower()
    if "next" in (a.get("rel") or []) or a.get("aria-label", "").lower().startswith(("next", "page")):
        return True
    if re.fullmatch(r"(next( page)?|›|»|>|>>|\d{1,3}|last|older( entries)?|more results)\s*[›»>]*", t):
        return True
    qa, qb = urlparse(url), urlparse(cur)
    if qa.path == qb.path and re.search(r"(^|&)(page|p|pg|start|offset)=\d+", qa.query):
        return True
    return False


class Crawler:
    def __init__(self, fetcher: Fetcher, agency: dict, park_names: dict[str, list[list[str]]],
                 deadline: float, use_browser: bool = True):
        self.f = fetcher
        self.a = agency
        self.index = agency["index_url"].strip()
        ih = urlparse(self.index).hostname or ""
        self.policy = HostPolicy(ih.lower(), {h.lower() for h in agency.get("doc_hosts", [])})
        self.max_depth = int(agency.get("max_depth", DEFAULT_MAX_DEPTH))
        self.max_pages = int(agency.get("max_pages", DEFAULT_MAX_PAGES))
        self.follow_res = [re.compile(p, re.I) for p in agency.get("follow_patterns", [])]
        self.render = agency.get("render", "auto")  # auto | static | browser
        self.wait_for = agency.get("wait_for")
        self.park_names = park_names
        self.deadline = deadline
        self.use_browser = use_browser
        self.pages_seen: set[str] = set()
        self.cands: list[Candidate] = []
        self.notes: list[str] = []
        self.pages_fetched = 0
        self.rendered_with_browser = False

    # -- helpers ---------------------------------------------------------------------------
    def best_park_score(self, text: str) -> float:
        toks, _ = norm_tokens(text, drop_generic=True)
        if not toks:
            return 0.0
        best = 0.0
        for names in self.park_names.values():
            for n in names:
                best = max(best, score_name_vs_field(n, toks))
        return best

    def fetch_html(self, url: str) -> tuple[str, str] | None:
        try:
            r = self.f.get(url, self.policy)
        except Blocked as e:
            self.notes.append(f"skipped {url}: {e}")
            return None
        except requests.RequestException as e:
            self.notes.append(f"error {url}: {e.__class__.__name__}")
            return None
        if r.status_code != 200:
            self.notes.append(f"HTTP {r.status_code} {url}")
            return None
        ct = r.headers.get("content-type", "").lower()
        if "html" not in ct and "xml" not in ct:
            return None
        r.encoding = r.encoding or r.apparent_encoding
        return r.url if hasattr(r, "url") else url, r.text

    def render_browser(self, url: str) -> str | None:
        if not self.use_browser:
            self.notes.append("browser rendering needed but disabled (--no-browser)")
            return None
        try:
            self.f.check(url, self.policy)
        except Blocked as e:
            self.notes.append(f"browser render skipped: {e}")
            return None
        try:
            from playwright.sync_api import sync_playwright
        except Exception:
            self.notes.append("playwright not installed; cannot render script-built page")
            return None
        host = urlparse(url).hostname or ""
        self.f._wait(host)
        policy = self.policy
        try:
            with sync_playwright() as p:
                browser = None
                errs = []
                for kw in ({}, {"channel": os.environ.get("KPC_BROWSER_CHANNEL", "chrome")}):
                    try:
                        browser = p.chromium.launch(headless=True, **kw)
                        break
                    except Exception as e:  # bundled chromium missing -> try system chrome
                        errs.append(str(e).splitlines()[0])
                if browser is None:
                    self.notes.append("could not launch Chromium: " + " | ".join(errs))
                    return None
                ctx = browser.new_context(user_agent=USER_AGENT)
                page = ctx.new_page()

                def route(rt):
                    req = rt.request
                    h = urlparse(req.url).hostname or ""
                    # never touch forbidden hosts; skip heavy media; stay on official hosts for XHR/docs
                    if host_forbidden(h) or req.resource_type in ("image", "media", "font"):
                        return rt.abort()
                    if req.resource_type in ("document", "xhr", "fetch") and not policy.ok(h):
                        return rt.abort()
                    return rt.continue_()

                page.route("**/*", route)
                page.goto(url, wait_until="networkidle", timeout=90000)
                if self.wait_for:
                    try:
                        page.wait_for_selector(self.wait_for, timeout=30000)
                    except Exception:
                        self.notes.append(f"wait_for selector {self.wait_for!r} never appeared")
                html = page.content()
                browser.close()
                self.f.requests_made += 1
                self.rendered_with_browser = True
                return html
        except Exception as e:
            self.notes.append(f"browser render failed: {e.__class__.__name__}: {str(e)[:160]}")
            return None

    def extract(self, html: str, page_url: str, depth: int, via_text: str
                ) -> list[tuple[str, str, int, bool]]:
        """Collect candidates from one page; return sub-pages to visit (url, text, depth, is_pagination)."""
        soup = BeautifulSoup(html, "html.parser")
        for bad in soup(["script", "style", "noscript", "template"]):
            bad.decompose()
        ph = page_heading_of(soup)
        to_visit: list[tuple[str, str, int, bool]] = []
        for a in soup.find_all("a", href=True):
            url = clean_url(a["href"], page_url)
            if not url:
                continue
            host = urlparse(url).hostname or ""
            if host_forbidden(host):
                continue
            text = a.get_text(" ", strip=True) or a.get("title", "") or a.get("aria-label", "")
            if not text:
                img = a.find("img")
                if img is not None:
                    text = img.get("alt", "")
            kind = looks_like_doc(a, url)
            if kind and self.policy.ok(host):
                self.cands.append(Candidate(url, kind, text[:300], nearest_heading(a), ph, via_text, page_url, depth,
                                            nearby_text(a)))
                continue
            if not self.policy.same_site(host):
                continue
            ext = ext_of(url)
            if ext in SKIP_EXT or ext in DOC_EXT:
                continue
            # a page link whose text mentions a map can itself be a "MAP PAGE" candidate
            if MAP_WORDS.search(text) and url != page_url:
                self.cands.append(Candidate(url, "MAP PAGE", text[:300], nearest_heading(a), ph, via_text, page_url, depth,
                                            nearby_text(a)))
            if depth >= self.max_depth or url in self.pages_seen:
                continue
            pag = is_pagination(a, url, page_url)
            follow = pag or any(r.search(text) or r.search(url) for r in self.follow_res)
            if not follow:
                slug = filename_text(url).replace("-", " ")
                follow = max(self.best_park_score(text), self.best_park_score(slug)) >= POSSIBLE
            if follow:
                to_visit.append((url, text, depth if pag else depth + 1, pag))
        # in-page map images (e.g. <img alt="Map of X">)
        for img in soup.find_all("img"):
            src = img.get("src") or img.get("data-src") or ""
            alt = img.get("alt", "") or ""
            if not src or not re.search(r"map", alt + " " + src, re.I):
                continue
            url = clean_url(src, page_url)
            if url and self.policy.ok(urlparse(url).hostname or "") and ext_of(url) != ".svg":
                self.cands.append(Candidate(url, "IMAGE", alt[:300], nearest_heading(img), ph, via_text, page_url, depth))
        return to_visit

    def run(self) -> None:
        queue: list[tuple[str, str, int]] = [(self.index, "", 0)]
        while queue:
            if time.monotonic() > self.deadline:
                raise TimeoutError("time budget reached during crawl")
            if self.pages_fetched >= self.max_pages:
                self.notes.append(f"max_pages ({self.max_pages}) reached; crawl truncated")
                break
            url, via, depth = queue.pop(0)
            if url in self.pages_seen:
                continue
            self.pages_seen.add(url)
            html = None
            final_url = url
            if depth == 0 and self.render == "browser":
                html = self.render_browser(url)
            if html is None:
                got = self.fetch_html(url)
                if got is None:
                    if depth == 0:
                        raise RuntimeError("index page could not be fetched: " + "; ".join(self.notes[-2:]))
                    continue
                final_url, html = got
            self.pages_fetched += 1
            n_before = len(self.cands)
            nxt = self.extract(html, final_url, depth, via)
            # auto mode: index page that yields nothing usable is probably built by script
            if depth == 0 and self.render == "auto" and not self.rendered_with_browser:
                useful = any(self.best_park_score(" ".join([c.text, filename_text(c.url), c.heading])) >= POSSIBLE
                             for c in self.cands[n_before:]) or any(not p for _, _, _, p in nxt)
                if not useful:
                    self.notes.append(f"index page static HTML ({len(html)} chars, {len(self.cands) - n_before} doc links) "
                                      "had no park-matching links; rendering with headless browser")
                    rhtml = self.render_browser(url)
                    if rhtml:
                        del self.cands[n_before:]
                        nxt = self.extract(rhtml, final_url, depth, via)
            for u, t, d, _pag in nxt:
                if u not in self.pages_seen:
                    queue.append((u, t if not _pag else via, d))


# ----------------------------------------------------------------------------------------------
# Matching
# ----------------------------------------------------------------------------------------------

def candidate_fields(c: Candidate, repeated: bool) -> list[tuple[str, str]]:
    f = [("link text", c.text), ("file name", filename_text(c.url)), ("heading", c.heading)]
    if not repeated:  # page-level context is meaningless for a link that sits on every page
        f += [("page heading", c.page_heading), ("came from link", c.via_text), ("nearby text", c.nearby)]
    return f


EVIDENCE = {"link text": 3, "file name": 3, "heading": 2, "page heading": 1, "came from link": 1, "nearby text": 0}


def match_agency(parks: dict[str, dict], refs: list[str], cands: list[Candidate]) -> dict[str, dict]:
    # how many distinct pages carry each URL (site-wide boilerplate links)
    pages_per_url: dict[str, set[str]] = {}
    for c in cands:
        pages_per_url.setdefault(c.url, set()).add(c.page_url)
    # dedupe identical (url, context) candidates
    seen = set(); uniq: list[Candidate] = []
    for c in cands:
        k = (c.url, c.text, c.heading, c.page_heading, c.via_text)
        if k not in seen:
            seen.add(k); uniq.append(c)
    cand_toks = []
    for c in uniq:
        repeated = len(pages_per_url[c.url]) > MAX_PARKS_PER_FILE
        fl = []
        fams: set[str] = set()
        for label, txt in candidate_fields(c, repeated):
            toks, fam = norm_tokens(txt, drop_generic=True)
            if label in ("link text", "file name", "heading"):
                fams |= fam
            if toks:
                fl.append((label, txt, toks))
        cand_toks.append((c, fl, fams, repeated))

    results: dict[str, dict] = {}
    for ref in refs:
        p = parks.get(ref)
        if not p:
            results[ref] = {"status": "NONE", "why": "ref not found in parks.json", "match_score": 0.0}
            continue
        names = [p.get("name", "")] + list(p.get("alt_names") or [])
        name_sets = []
        park_fams: set[str] = set()
        for n in names:
            toks, fam = norm_tokens(n)
            park_fams |= fam
            if toks:
                name_sets.append((n, toks))
        if p.get("type"):
            park_fams |= norm_tokens(p["type"])[1]
        scored = []
        for c, fl, fams, repeated in cand_toks:
            best = (0.0, "", "", "")
            ph_score = None
            for label, txt, toks in fl:
                if label == "page heading":
                    ph_score = max(score_name_vs_field(nt, toks) for _, nt in name_sets)
            for label, txt, toks in fl:
                # the link that led to a sub-page only counts if the sub-page's own heading agrees
                if label == "came from link" and ph_score is not None and ph_score < POSSIBLE:
                    continue
                for n, nt in name_sets:
                    s = score_name_vs_field(nt, toks)
                    if s > best[0] or (s == best[0] and s > 0 and EVIDENCE[label] > EVIDENCE.get(best[1], -1)):
                        best = (s, label, txt, n)
            if best[0] < POSSIBLE:
                continue
            s = best[0]
            conflict = bool(fams) and bool(park_fams) and not (fams & park_fams)
            if conflict and s >= ACCEPT:
                s = min(s, 0.89)
            # weak evidence can never be accepted on its own -> POSSIBLE for a person
            weak = None
            if best[1] == "nearby text":
                weak = "matched only on the sentence around the link"
            elif c.kind in ("IMAGE", "MAP PAGE") and best[1] not in ("link text", "file name"):
                weak = f"{c.kind.lower()} matched only on page context (no own name, cannot be text-checked)"
            if weak and s >= ACCEPT:
                s = min(s, 0.89)
            mapish = 1 if MAP_WORDS.search(c.text + " " + c.url) else 0
            if mapish and re.search(r"\b(index|overview|main|full|all)\b", c.text, re.I):
                mapish = 2  # among several maps for one park prefer the overview/index sheet
            if re.search(r"\b(mobile|closure|closed|notice)\b", c.text + " " + c.heading, re.I):
                mapish -= 1
            kind_rank = {"PDF": 3, "DOC?": 2, "IMAGE": 2, "KMZ": 1, "MAP PAGE": 0}.get(c.kind, 0)
            # specificity: fewer extra tokens in the matched field = more specific
            extra = len(norm_tokens(best[2], drop_generic=True)[0])
            scored.append((round(s, 3), EVIDENCE[best[1]], kind_rank, mapish, -extra, c, best, conflict, repeated, weak))
        scored.sort(key=lambda x: x[:5], reverse=True)  # score, evidence, kind, map-word, specificity
        if not scored:
            results[ref] = {"status": "NONE", "match_score": 0.0, "park_name": p.get("name"),
                            "why": f"no candidate link scored >= {POSSIBLE} against the park name(s) "
                                   f"({len(uniq)} candidate links on {len({c.page_url for c in uniq})} pages)"}
            continue
        top = scored[0]
        s, c, best, conflict = top[0], top[5], top[6], top[7]
        alts = []
        seen_u = {c.url}
        for t in scored[1:]:
            if t[5].url in seen_u:
                continue
            seen_u.add(t[5].url)
            alts.append({"url": t[5].url, "score": t[0], "text": t[5].text[:120], "kind": t[5].kind})
            if len(alts) >= 3:
                break
        status = "OK" if s >= ACCEPT else "POSSIBLE"
        why = f"{best[1]} '{best[2][:100]}' ~ park name '{best[3]}' (score {s:.2f})"
        if conflict:
            why += "; park type differs from the type named on the document -> held at POSSIBLE"
        if top[9]:
            why += f"; {top[9]} -> held at POSSIBLE"
        if top[8]:
            why += "; link appears on many pages (site-wide)"
        results[ref] = {"page_url": c.page_url, "map_url": c.url, "kind": c.kind, "map_date": None,
                        "match_score": s, "status": status, "why": why, "park_name": p.get("name"),
                        "matched_text": c.text[:200], "alternates": alts}
    # SHARED: one file may never be assigned to more than MAX_PARKS_PER_FILE parks
    by_url: dict[str, list[str]] = {}
    for ref, r in results.items():
        if r.get("map_url") and r["status"] in ("OK", "POSSIBLE"):
            by_url.setdefault(r["map_url"], []).append(ref)
    for url, rs in by_url.items():
        if len(rs) > MAX_PARKS_PER_FILE:
            for ref in rs:
                results[ref]["status"] = "SHARED"
                results[ref]["why"] = (f"same file is the best match for {len(rs)} parks "
                                       f"(> {MAX_PARKS_PER_FILE}); a shared/statewide file is not a park map. "
                                       + results[ref]["why"])
    return results


# ----------------------------------------------------------------------------------------------
# Verification (HEAD/GET, type sniff, PDF page 1-2 text, dates)
# ----------------------------------------------------------------------------------------------

def apply_rewrites(url: str, rewrites: list[dict]) -> str:
    for rw in rewrites or []:
        new = re.sub(rw["pattern"], rw["replace"], url)
        if new != url:
            return new
    return url


def _pdf_date(v: Any) -> str | None:
    if not v:
        return None
    s = str(v)
    m = re.search(r"(\d{4})(\d{2})?(\d{2})?", s.replace("D:", ""))
    if not m:
        return None
    y, mo, d = m.group(1), m.group(2) or "01", m.group(3) or "01"
    return f"{y}-{mo}-{d}"


def verify(fetcher: Fetcher, policy: HostPolicy, url: str, rewrites: list[dict],
           park_names: list[str], cache: dict) -> dict:
    key = url
    if key in cache:
        info = dict(cache[key])
    else:
        info = _verify_fetch(fetcher, policy, url, rewrites)
        cache[key] = {k: v for k, v in info.items() if k != "_text"}
        if "_text" in info:
            cache[key]["text_sample"] = info["_text"][:4000]
        info = dict(cache[key])
    text = info.get("text_sample")
    if text is not None and info.get("text_chars", 0) > 40:
        found = None
        t_toks = norm_tokens(text, drop_generic=False)[0]
        for n in park_names:
            nt = norm_tokens(n)[0]
            if nt and score_name_vs_field(nt, t_toks) >= ACCEPT:
                found = n
                break
        info["name_in_pdf"] = found is not None
        info["name_in_pdf_as"] = found
    return info


def _verify_fetch(fetcher: Fetcher, policy: HostPolicy, url: str, rewrites: list[dict]) -> dict:
    real = apply_rewrites(url, rewrites)
    out: dict[str, Any] = {"checked_url": real, "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    try:
        r = fetcher.get(real, policy, stream=True)
    except Blocked as e:
        out.update(ok=False, error=f"blocked: {e}")
        return out
    except requests.RequestException as e:
        out.update(ok=False, error=f"{e.__class__.__name__}")
        return out
    out["http_status"] = r.status_code
    out["final_url"] = r.url
    ct = r.headers.get("content-type", "").split(";")[0].strip().lower()
    out["content_type"] = ct
    lm = r.headers.get("Last-Modified")
    if lm:
        try:
            out["last_modified"] = parsedate_to_datetime(lm).date().isoformat()
        except Exception:
            out["last_modified"] = lm
    if r.status_code != 200:
        r.close()
        out.update(ok=False, error=f"HTTP {r.status_code}")
        return out
    buf = io.BytesIO()
    too_big = False
    try:
        for chunk in r.iter_content(65536):
            buf.write(chunk)
            if buf.tell() > MAX_DOWNLOAD_BYTES:
                too_big = True
                break
    except requests.RequestException as e:
        out.update(ok=False, error=f"download failed: {e.__class__.__name__}")
        return out
    finally:
        r.close()
    data = buf.getvalue()
    out["bytes"] = len(data) if not too_big else f">{MAX_DOWNLOAD_BYTES}"
    head = data[:16]
    if head.startswith(b"%PDF") or (b"%PDF" in data[:1024]):
        out["sniffed"] = "PDF"
    elif head.startswith(b"\x89PNG"):
        out["sniffed"] = "IMAGE"
    elif head[:3] == b"\xff\xd8\xff":
        out["sniffed"] = "IMAGE"
    elif head[:4] in (b"GIF8",) or head[:4] == b"RIFF":
        out["sniffed"] = "IMAGE"
    elif head[:2] == b"PK":
        out["sniffed"] = "KMZ" if real.lower().endswith((".kmz",)) or "kmz" in ct else "ZIP"
    elif b"<html" in data[:2048].lower() or "html" in ct:
        out["sniffed"] = "HTML"
    else:
        out["sniffed"] = "UNKNOWN"
    out["ok"] = out["sniffed"] in ("PDF", "IMAGE", "KMZ", "HTML")
    if out["sniffed"] == "PDF" and PdfReader is not None and not too_big:
        try:
            rd = PdfReader(io.BytesIO(data))
            out["pdf_pages"] = len(rd.pages)
            meta = rd.metadata or {}
            out["pdf_created"] = _pdf_date(meta.get("/CreationDate"))
            out["pdf_modified"] = _pdf_date(meta.get("/ModDate"))
            txt = ""
            for pg in rd.pages[:2]:
                try:
                    txt += (pg.extract_text() or "") + "\n"
                except Exception:
                    pass
            # PDF titles often carry the park name even when the map is pure graphics
            title = str(meta.get("/Title") or "")
            out["pdf_title"] = title[:200] or None
            out["_text"] = (title + "\n" + txt)
            out["text_chars"] = len(txt.strip())
        except Exception as e:
            out["pdf_error"] = f"{e.__class__.__name__}: {str(e)[:100]}"
    elif out["sniffed"] == "HTML":
        try:
            soup = BeautifulSoup(data.decode("utf-8", "ignore"), "html.parser")
            t = (soup.title.get_text(" ", strip=True) if soup.title else "") + "\n" + page_heading_of(soup)
            out["_text"] = t
            out["text_chars"] = len(t.strip())
        except Exception:
            pass
    return out


def finalize_with_verification(res: dict, info: dict) -> dict:
    res["checks"] = {k: v for k, v in info.items() if k not in ("text_sample",)}
    if not info.get("ok"):
        if res["status"] == "OK":
            res["status"] = "POSSIBLE"
        res["why"] += f"; file check failed ({info.get('error') or info.get('sniffed')}) -> needs a person"
        return res
    sniff = info.get("sniffed")
    if res["kind"] in ("DOC?",) or (res["kind"] != "MAP PAGE" and sniff in ("PDF", "IMAGE", "KMZ")):
        res["kind"] = sniff
    if sniff == "HTML" and res["kind"] in ("PDF", "IMAGE", "DOC?"):
        res["kind"] = "MAP PAGE"
        if res["status"] == "OK":
            res["status"] = "POSSIBLE"
        res["why"] += "; link expected a file but returned an HTML page"
    res["map_date"] = info.get("pdf_created") or info.get("pdf_modified") or info.get("last_modified")
    if "name_in_pdf" in info:
        if info["name_in_pdf"]:
            res["why"] += "; park name found in the document text (page 1-2/title)"
        elif sniff == "PDF":
            if res["status"] == "OK":
                res["status"] = "POSSIBLE"
            res["why"] += "; park name NOT found in PDF page 1-2 text -> needs a person"
    elif sniff == "PDF":
        res["why"] += "; no extractable text on PDF page 1-2 (graphic map), name not confirmed"
    return res


# ----------------------------------------------------------------------------------------------
# Orchestration, state, output
# ----------------------------------------------------------------------------------------------

def agency_key(a: dict) -> str:
    h = hashlib.sha1((a.get("agency", "") + "|" + a.get("index_url", "")).encode()).hexdigest()[:10]
    return f"{re.sub(r'[^A-Za-z0-9]+', '_', a.get('agency', 'agency'))[:40]}_{h}"


def load_json(path: str, default):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    return default


def save_json(path: str, obj) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


def process_agency(a: dict, parks: dict, fetcher: Fetcher, state: dict, deadline: float,
                   use_browser: bool) -> dict:
    t0 = time.monotonic()
    refs = list(dict.fromkeys(a.get("park_refs", [])))
    park_names = {}
    for ref in refs:
        p = parks.get(ref)
        if p:
            names = [p.get("name", "")] + list(p.get("alt_names") or [])
            park_names[ref] = [t for t in (norm_tokens(n)[0] for n in names) if t]
    cr = Crawler(fetcher, a, park_names, deadline, use_browser=use_browser)
    cr.run()
    results = match_agency(parks, refs, cr.cands)
    cache = state.setdefault("verified", {})
    for ref, r in results.items():
        if r.get("status") in ("OK", "POSSIBLE") and r.get("map_url"):
            if time.monotonic() > deadline:
                raise TimeoutError("time budget reached during verification")
            p = parks.get(ref, {})
            names = [p.get("name", "")] + list(p.get("alt_names") or [])
            info = verify(fetcher, cr.policy, r["map_url"], a.get("url_rewrites", []), names, cache)
            finalize_with_verification(r, info)
        r["agency"] = a.get("agency")
        r.setdefault("page_url", a["index_url"])
        r.setdefault("map_url", None)
        r.setdefault("kind", None)
        r.setdefault("map_date", None)
    counts = {k: sum(1 for r in results.values() if r["status"] == k) for k in ("OK", "POSSIBLE", "SHARED", "NONE")}
    return {
        "status": "done", "agency": a.get("agency"), "index_url": a.get("index_url"),
        "results": results, "counts": counts, "pages_fetched": cr.pages_fetched,
        "candidates": len(cr.cands), "browser_used": cr.rendered_with_browser,
        "notes": cr.notes[:50], "seconds": round(time.monotonic() - t0, 1),
        "finished_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def write_outputs(out_dir: str, state: dict, agencies: list[dict], parks: dict | None = None) -> dict:
    docs: dict[str, dict] = {}
    rank = {"OK": 3, "POSSIBLE": 2, "SHARED": 1, "NONE": 0}
    for a in agencies:
        st = state["agencies"].get(agency_key(a))
        if not st:
            continue
        if st.get("status") != "done":
            for ref in a.get("park_refs", []):
                docs.setdefault(ref, {"park_name": (parks or {}).get(ref, {}).get("name"),
                                      "page_url": a["index_url"], "map_url": None, "kind": None, "map_date": None,
                                      "match_score": 0.0, "status": "NONE", "agency": a.get("agency"),
                                      "why": f"agency not processed: {st.get('error', st.get('status'))}"})
            continue
        for ref, r in st["results"].items():
            if ref not in docs or rank[r["status"]] > rank[docs[ref]["status"]]:
                docs[ref] = r
    save_json(os.path.join(out_dir, "docs_found.json"), docs)
    cols = ["ref", "park_name", "agency", "status", "match_score", "kind", "map_url", "page_url", "map_date", "why"]
    with open(os.path.join(out_dir, "report.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for ref in sorted(docs):
            r = docs[ref]
            w.writerow([ref] + [r.get(c) for c in cols[1:]])
    summary = {"generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "agencies": []}
    tot = {"OK": 0, "POSSIBLE": 0, "SHARED": 0, "NONE": 0}
    for r in docs.values():
        tot[r["status"]] += 1
    summary["totals"] = tot
    for a in agencies:
        st = state["agencies"].get(agency_key(a), {"status": "not started"})
        summary["agencies"].append({k: st.get(k) for k in ("agency", "index_url", "status", "counts", "pages_fetched",
                                                           "candidates", "browser_used", "seconds", "error", "notes")}
                                   | {"agency": a.get("agency"), "index_url": a.get("index_url")})
    save_json(os.path.join(out_dir, "summary.json"), summary)
    return summary


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="KPC agency map-page link extractor")
    ap.add_argument("--agencies", required=True, help="agency_pages.json")
    ap.add_argument("--parks", default=None, help="parks.json (default: parks.json next to --agencies)")
    ap.add_argument("--out", default="out", help="output directory (default ./out)")
    ap.add_argument("--resume", action="store_true", help="skip agencies already finished in out/state.json")
    ap.add_argument("--max-minutes", type=float, default=50.0,
                    help="stop cleanly after this many minutes (GitHub Actions job limit is 55)")
    ap.add_argument("--chunk", default=None, help="process chunk i of n, e.g. 2/5 (for parallel jobs)")
    ap.add_argument("--only", default=None, help="only agencies whose name contains this text")
    ap.add_argument("--no-browser", action="store_true", help="never launch the headless browser")
    ap.add_argument("--min-delay", type=float, default=DEFAULT_MIN_DELAY, help="seconds between requests to one host")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S")

    agencies = load_json(args.agencies, None)
    if not isinstance(agencies, list):
        print("agency_pages.json must be a JSON list", file=sys.stderr)
        return 2
    parks_path = args.parks or os.path.join(os.path.dirname(os.path.abspath(args.agencies)), "parks.json")
    parks = load_json(parks_path, {})
    if args.only:
        agencies = [a for a in agencies if args.only.lower() in a.get("agency", "").lower()]
    if args.chunk:
        i, n = (int(x) for x in args.chunk.split("/"))
        agencies = [a for k, a in enumerate(agencies) if k % n == i - 1]
    os.makedirs(args.out, exist_ok=True)
    state_path = os.path.join(args.out, "state.json")
    state = load_json(state_path, {}) if args.resume else {}
    state.setdefault("agencies", {})
    state.setdefault("verified", {})
    state["version"] = VERSION
    deadline = time.monotonic() + args.max_minutes * 60
    fetcher = Fetcher(min_delay=args.min_delay)
    incomplete = False
    for a in agencies:
        key = agency_key(a)
        if args.resume and state["agencies"].get(key, {}).get("status") == "done":
            log.info("skip (done): %s", a.get("agency"))
            continue
        if time.monotonic() > deadline:
            incomplete = True
            break
        log.info("agency: %s  %s", a.get("agency"), a.get("index_url"))
        try:
            state["agencies"][key] = process_agency(a, parks, fetcher, state, deadline, not args.no_browser)
            log.info("  -> %s", state["agencies"][key]["counts"])
        except TimeoutError as e:
            state["agencies"][key] = {"status": "partial", "agency": a.get("agency"), "error": str(e)}
            incomplete = True
            save_json(state_path, state)
            break
        except Exception as e:  # one failure never stops the run
            log.exception("agency failed: %s", a.get("agency"))
            state["agencies"][key] = {"status": "error", "agency": a.get("agency"),
                                      "error": f"{e.__class__.__name__}: {str(e)[:300]}"}
        save_json(state_path, state)
    summary = write_outputs(args.out, state, agencies, parks)
    log.info("totals: %s  (requests made: %d)", summary["totals"], fetcher.requests_made)
    if incomplete:
        log.warning("time budget reached; re-run with --resume to continue")
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
