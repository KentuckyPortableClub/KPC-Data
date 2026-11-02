#!/usr/bin/env python3
"""kpc_camp_layers - campground list builder from official campground layers.

Reads the official agency campground layers (ArcGIS REST) named in the camping
file(s) and writes the campgrounds that are not on the club's lists yet, plus a
second list of "activating spots" (day-use areas, picnic shelters, overlooks).
It decides nothing about parks: `park` is always left empty.

Follows the KPC install contract. Standard library only (Python 3.12).
"""
from __future__ import annotations

import argparse
import csv
import difflib
import glob
import gzip
import hashlib
import io
import json
import math
import os
import re
import shutil
import struct
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
import zipfile
from datetime import date

VERSION = "1.0.0"
SRC_LABEL = "official campground layers (outside research E)"
CENSUS_STATES_URL = "https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_state_500k.zip"
DEFAULT_IN = "data/intake/_in/camping/camping-*.json"
DEFAULT_KNOWN = "data/campfed,data/campstate,data/campstate-manual"
MIN_GAP_S = 2.05          # at most 1 request every 2 s per host
DUP_DIST_M = 150.0
DUP_SIM = 0.6
SAME_NAME_M = 1500  # same layer, same exact name: sites of one campground
SIMPLIFY_M = 3.0
PAGE_CAP = 2000
MAX_PAGES = 1000
EXIT_OK, EXIT_TIME = 0, 3

# --------------------------------------------------------------------------
# Sources never used (install contract, rule 6)
# --------------------------------------------------------------------------
FORBIDDEN_HOST_PARTS = (
    "openstreetmap.", "osm.org", "overpass", "geofabrik.",
    "alltrails.", "gaiagps.", "strava.", "tripadvisor.", "yelp.", "wikipedia.", "wikimedia.",
    "protectedplanet.", "unep-wcmc.", "wdpa.", "campendium.", "ioverlander.",
)
GOOGLE_ALLOWED = ("storage.googleapis.com",)


def forbidden_source(url: str) -> str:
    host = (urllib.parse.urlsplit(url).hostname or "").lower()
    for part in FORBIDDEN_HOST_PARTS:
        if part in host:
            return host
    if host in GOOGLE_ALLOWED or host.endswith(".storage.googleapis.com"):
        return ""
    if re.search(r"(^|\.)google(apis|usercontent)?\.[a-z.]+$", host) or re.search(r"(^|\.)gstatic\.com$", host) \
            or re.search(r"(^|\.)goo\.gl$", host):
        return host
    return ""


# --------------------------------------------------------------------------
# Polite HTTP (robots, 1 req / 2 s / host, UA, back-off, cache)
# --------------------------------------------------------------------------
class FetchError(Exception):
    def __init__(self, msg: str, retry_later: bool = False):
        super().__init__(msg)
        self.retry_later = retry_later


def urllib_transport(url: str, headers: dict, timeout: float = 60.0):
    """Returns (status, headers_dict, body_bytes). Raises OSError on network trouble."""
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read()
            hdrs = {k.lower(): v for k, v in r.headers.items()}
            status = r.status
    except urllib.error.HTTPError as e:
        body = e.read() if e.fp else b""
        hdrs = {k.lower(): v for k, v in (e.headers or {}).items()}
        status = e.code
    if hdrs.get("content-encoding", "").lower() == "gzip":
        body = gzip.decompress(body)
    return status, hdrs, body


class Fetcher:
    def __init__(self, contact: str, cache_dir: str | None, cache_days: float = 6.0,
                 transport=urllib_transport, clock=time.monotonic, sleep=time.sleep, log=None):
        self.ua = f"KPC park tools ({contact})"
        self.cache_dir = cache_dir
        self.cache_days = cache_days
        self.transport = transport
        self.clock = clock
        self.sleep = sleep
        self.log = log or (lambda m: None)
        self.last: dict[str, float] = {}
        self.resting: set[str] = set()
        self.robots: dict[str, urllib.robotparser.RobotFileParser] = {}
        self.requests: list[tuple[str, float]] = []   # (url, clock) for tests/diagnostics
        if cache_dir:
            os.makedirs(cache_dir, exist_ok=True)

    def _headers(self):
        return {"User-Agent": self.ua, "Accept-Encoding": "gzip"}

    def _wait_turn(self, host: str):
        now = self.clock()
        prev = self.last.get(host)
        if prev is not None and now - prev < MIN_GAP_S:
            self.sleep(MIN_GAP_S - (now - prev))
        self.last[host] = self.clock()

    def _raw(self, url: str, host: str):
        """One request with retries on 429/503. Returns (status, headers, body)."""
        if host in self.resting:
            raise FetchError(f"host resting ({host} sent 429/503 too often)", retry_later=True)
        net_tries = nf_tries = 0
        for attempt in range(6):           # first try + 3 retries
            self._wait_turn(host)
            self.requests.append((url, self.clock()))
            try:
                status, hdrs, body = self.transport(url, self._headers())
            except (OSError, ValueError) as e:  # URLError, timeouts, resets
                net_tries += 1
                if net_tries <= 2:
                    self.sleep(5 * net_tries)
                    continue
                raise FetchError(f"network error: {type(e).__name__}: {str(e)[:120]}", retry_later=True)
            if status == 404 and nf_tries < 2 and "/rest/services/" in url:
                nf_tries += 1          # some agency servers flap 200/404 behind a load balancer
                self.sleep(5)
                continue
            if status in (429, 503):
                if attempt - nf_tries == 3:
                    self.resting.add(host)
                    self.log(f"  host {host} is resting for this run (HTTP {status})")
                    raise FetchError(f"HTTP {status} after 3 retries; host resting", retry_later=True)
                wait = 15 * (2 ** (attempt - nf_tries))
                ra = hdrs.get("retry-after", "")
                if ra.strip().isdigit():
                    wait = min(int(ra.strip()), 120)
                self.sleep(wait)
                continue
            return status, hdrs, body
        raise FetchError("network error: gave up", retry_later=True)

    def _robots_ok(self, url: str) -> bool:
        sp = urllib.parse.urlsplit(url)
        key = f"{sp.scheme}://{sp.netloc}"
        if key not in self.robots:
            rp = urllib.robotparser.RobotFileParser()
            try:
                status, _h, body = self._raw(key + "/robots.txt", sp.netloc.lower())
            except FetchError:
                status, body = 0, b""
            if status in (401, 403):
                rp.disallow_all = True
            elif 200 <= status < 300:
                rp.parse(body.decode("utf-8", "replace").splitlines())
            else:                      # 404 / other / unreachable: no rules published
                rp.allow_all = True
            self.robots[key] = rp
        return self.robots[key].can_fetch(self.ua, url)

    def _cache_path(self, url: str):
        if not self.cache_dir:
            return None
        return os.path.join(self.cache_dir, hashlib.sha1(url.encode()).hexdigest() + ".bin")

    def drop_cache(self, url: str):
        p = self._cache_path(url)
        if p and os.path.exists(p):
            os.remove(p)

    def get(self, url: str, max_age_days: float | None = None) -> bytes:
        bad = forbidden_source(url)
        if bad:
            raise FetchError(f"forbidden source ({bad}) - never used")
        sp = urllib.parse.urlsplit(url)
        if sp.scheme not in ("http", "https"):
            raise FetchError("not an http(s) URL")
        host = sp.netloc.lower()
        cp = self._cache_path(url)
        age_limit = self.cache_days if max_age_days is None else max_age_days
        if cp and os.path.exists(cp) and (time.time() - os.path.getmtime(cp)) < age_limit * 86400:
            with open(cp, "rb") as f:
                return f.read()
        if host in self.resting:
            raise FetchError(f"host resting ({host} sent 429/503 too often)", retry_later=True)
        if not self._robots_ok(url):
            raise FetchError("robots.txt disallows this URL")
        status, _h, body = self._raw(url, host)
        if status in (401, 407) or (status == 403 and b"token" in body.lower()):
            raise FetchError("needs sign-in")
        if status >= 400:
            raise FetchError(f"HTTP {status}")
        if cp:
            tmp = cp + ".tmp"
            with open(tmp, "wb") as f:
                f.write(body)
            os.replace(tmp, cp)
        return body

    def get_json(self, url: str) -> dict:
        body = self.get(url)
        try:
            data = json.loads(body.decode("utf-8", "replace"))
        except ValueError:
            self.drop_cache(url)
            txt = body[:300].decode("utf-8", "replace").lower()
            if "login" in txt or "sign in" in txt or "token" in txt:
                raise FetchError("needs sign-in")
            raise FetchError("answer was not JSON")
        if isinstance(data, dict) and isinstance(data.get("error"), dict):
            self.drop_cache(url)
            err = data["error"]
            code = err.get("code")
            msg = str(err.get("message") or "")
            if code in (498, 499, 401, 403) or "token" in msg.lower():
                raise FetchError("needs sign-in")
            raise FetchError(f"server error {code}: {msg[:120]}")
        if not isinstance(data, dict):
            raise FetchError("answer was not a JSON object")
        return data


# --------------------------------------------------------------------------
# Geometry helpers
# --------------------------------------------------------------------------
def haversine_m(lat1, lon1, lat2, lon2) -> float:
    r = 6371008.8
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(min(1.0, math.sqrt(a)))


def polygon_centroid(rings):
    """Area-weighted centre over all rings (holes have the opposite winding)."""
    a_sum = cx = cy = 0.0
    pts = [p for r in rings for p in r]
    if not pts:
        return None
    x0, y0 = pts[0][0], pts[0][1]
    for ring in rings:
        for i in range(len(ring) - 1):
            x1, y1 = ring[i][0] - x0, ring[i][1] - y0
            x2, y2 = ring[i + 1][0] - x0, ring[i + 1][1] - y0
            cr = x1 * y2 - x2 * y1
            a_sum += cr
            cx += (x1 + x2) * cr
            cy += (y1 + y2) * cr
    if abs(a_sum) < 1e-18:
        return sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)
    return x0 + cx / (3 * a_sum), y0 + cy / (3 * a_sum)


def _dp(points, tol):
    if len(points) < 3:
        return points
    keep = [False] * len(points)
    keep[0] = keep[-1] = True
    stack = [(0, len(points) - 1)]
    while stack:
        i, j = stack.pop()
        (x1, y1), (x2, y2) = points[i], points[j]
        dx, dy = x2 - x1, y2 - y1
        L2 = dx * dx + dy * dy
        best, bi = -1.0, -1
        for k in range(i + 1, j):
            px, py = points[k]
            t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / L2))
            d = math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))
            if d > best:
                best, bi = d, k
        if best > tol:
            keep[bi] = True
            stack.append((i, bi))
            stack.append((bi, j))
    return [p for p, k in zip(points, keep) if k]


def simplify_rings(rings, tol_m=SIMPLIFY_M):
    """Douglas-Peucker (3 m) in a local metric frame; returns rings as [[lon, lat], ...]."""
    allpts = [p for r in rings for p in r]
    if not allpts:
        return []
    lat0 = sum(p[1] for p in allpts) / len(allpts)
    kx, ky = 111320.0 * math.cos(math.radians(lat0)), 110540.0
    out = []
    for ring in rings:
        if len(ring) < 3:
            continue
        pts = [(p[0] * kx, p[1] * ky) for p in ring]
        body = pts[:-1] if pts[0] == pts[-1] else pts
        if len(body) < 3:
            continue
        far = max(range(len(body)), key=lambda k: (body[k][0] - body[0][0]) ** 2 + (body[k][1] - body[0][1]) ** 2)
        a = _dp(body[:far + 1], tol_m)
        b = _dp(body[far:] + [body[0]], tol_m)
        simp = a[:-1] + b
        if len(simp) < 4:
            simp = body + [body[0]]
        out.append([[round(x / kx, 6), round(y / ky, 6)] for x, y in simp])
    return out


def point_in_rings(x, y, rings) -> bool:
    inside = False
    for ring in rings:
        n = len(ring)
        j = n - 1
        for i in range(n):
            xi, yi = ring[i][0], ring[i][1]
            xj, yj = ring[j][0], ring[j][1]
            if (yi > y) != (yj > y):
                if x < (xj - xi) * (y - yi) / (yj - yi) + xi:
                    inside = not inside
            j = i
    return inside


def seg_dist_deg(x, y, rings, coslat):
    best = float("inf")
    px = x * coslat
    for ring in rings:
        for i in range(len(ring) - 1):
            x1, y1 = ring[i][0] * coslat, ring[i][1]
            x2, y2 = ring[i + 1][0] * coslat, ring[i + 1][1]
            dx, dy = x2 - x1, y2 - y1
            L2 = dx * dx + dy * dy
            t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px - x1) * dx + (y - y1) * dy) / L2))
            best = min(best, math.hypot(px - (x1 + t * dx), y - (y1 + t * dy)))
    return best


# --------------------------------------------------------------------------
# States: Census outline (cartographic boundary file) + bundled approximate boxes
# --------------------------------------------------------------------------
STATE_NAMES = {
    "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR", "california": "CA", "colorado": "CO",
    "connecticut": "CT", "delaware": "DE", "district of columbia": "DC", "florida": "FL", "georgia": "GA",
    "hawaii": "HI", "idaho": "ID", "illinois": "IL", "indiana": "IN", "iowa": "IA", "kansas": "KS",
    "kentucky": "KY", "louisiana": "LA", "maine": "ME", "maryland": "MD", "massachusetts": "MA",
    "michigan": "MI", "minnesota": "MN", "mississippi": "MS", "missouri": "MO", "montana": "MT",
    "nebraska": "NE", "nevada": "NV", "new hampshire": "NH", "new jersey": "NJ", "new mexico": "NM",
    "new york": "NY", "north carolina": "NC", "north dakota": "ND", "ohio": "OH", "oklahoma": "OK",
    "oregon": "OR", "pennsylvania": "PA", "rhode island": "RI", "south carolina": "SC", "south dakota": "SD",
    "tennessee": "TN", "texas": "TX", "utah": "UT", "vermont": "VT", "virginia": "VA", "washington": "WA",
    "west virginia": "WV", "wisconsin": "WI", "wyoming": "WY", "puerto rico": "PR", "guam": "GU",
    "virgin islands": "VI", "united states virgin islands": "VI", "american samoa": "AS",
    "northern mariana islands": "MP", "commonwealth of the northern mariana islands": "MP",
}
STATE_CODES = set(STATE_NAMES.values())

# Approximate state boxes {code: (S, W, N, E)}, rounded from the Census 2024 cartographic
# boundary file. Last-resort fallback only, used when the Census outline cannot be loaded;
# rows placed this way say "state by approx" in their `why`. Overlaps: smallest box wins.
APPROX_BOXES = {
    "AK": (51.22, -179.15, 71.39, 179.78),
    "AL": (30.22, -88.47, 35.01, -84.89),
    "AR": (33.00, -94.62, 36.50, -89.64),
    "AS": (-14.55, -171.09, -11.05, -168.14),
    "AZ": (31.33, -114.82, 37.00, -109.05),
    "CA": (32.53, -124.41, 42.01, -114.13),
    "CO": (36.99, -109.06, 41.00, -102.04),
    "CT": (40.98, -73.73, 42.05, -71.79),
    "DC": (38.79, -77.12, 39.00, -76.91),
    "DE": (38.45, -75.79, 39.84, -75.05),
    "FL": (24.52, -87.63, 31.00, -80.03),
    "GA": (30.36, -85.61, 35.00, -80.84),
    "GU": (13.23, 144.62, 13.65, 144.96),
    "HI": (18.91, -178.33, 28.40, -154.81),
    "IA": (40.38, -96.64, 43.50, -90.14),
    "ID": (41.99, -117.24, 49.00, -111.04),
    "IL": (36.97, -91.51, 42.51, -87.50),
    "IN": (37.77, -88.10, 41.76, -84.78),
    "KS": (36.99, -102.05, 40.00, -94.59),
    "KY": (36.50, -89.57, 39.15, -81.96),
    "LA": (28.93, -94.04, 33.02, -88.82),
    "MA": (41.24, -73.51, 42.89, -69.93),
    "MD": (37.91, -79.49, 39.72, -75.05),
    "ME": (42.98, -71.08, 47.46, -66.95),
    "MI": (41.70, -90.42, 48.24, -82.41),
    "MN": (43.50, -97.24, 49.38, -89.49),
    "MO": (36.00, -95.77, 40.61, -89.10),
    "MP": (14.11, 144.89, 20.55, 146.06),
    "MS": (30.18, -91.66, 35.00, -88.10),
    "MT": (44.36, -116.05, 49.00, -104.04),
    "NC": (33.84, -84.32, 36.59, -75.46),
    "ND": (45.94, -104.05, 49.00, -96.55),
    "NE": (40.00, -104.05, 43.00, -95.31),
    "NH": (42.70, -72.56, 45.31, -70.61),
    "NJ": (38.93, -75.56, 41.36, -73.89),
    "NM": (31.33, -109.05, 37.00, -103.00),
    "NV": (35.00, -120.01, 42.00, -114.04),
    "NY": (40.50, -79.76, 45.02, -71.86),
    "OH": (38.40, -84.82, 41.98, -80.52),
    "OK": (33.62, -103.00, 37.00, -94.43),
    "OR": (41.99, -124.57, 46.29, -116.46),
    "PA": (39.72, -80.52, 42.27, -74.69),
    "PR": (17.88, -67.95, 18.52, -65.22),
    "RI": (41.15, -71.86, 42.02, -71.12),
    "SC": (32.04, -83.35, 35.22, -78.55),
    "SD": (42.48, -104.06, 45.95, -96.44),
    "TN": (34.98, -90.31, 36.68, -81.65),
    "TX": (25.84, -106.65, 36.50, -93.51),
    "UT": (37.00, -114.05, 42.00, -109.04),
    "VA": (36.54, -83.68, 39.47, -75.24),
    "VI": (17.67, -65.09, 18.42, -64.57),
    "VT": (42.73, -73.44, 45.02, -71.46),
    "WA": (45.54, -124.76, 49.00, -116.92),
    "WI": (42.49, -92.89, 47.08, -86.81),
    "WV": (37.20, -82.64, 40.64, -77.72),
    "WY": (40.99, -111.05, 45.01, -104.05),
}


def norm_state(v) -> str:
    if v is None:
        return ""
    s = str(v).strip()
    if not s:
        return ""
    u = s.upper().replace("US-", "")
    if len(u) == 2 and u in STATE_CODES:
        return u
    return STATE_NAMES.get(re.sub(r"\s+", " ", s.lower().replace("state of ", "")).strip(), "")


def read_shp_polygons(shp: bytes):
    """Minimal ESRI shapefile reader for polygon records -> list of ring lists."""
    out = []
    pos, n = 100, len(shp)
    while pos + 8 <= n:
        _rec, clen = struct.unpack(">ii", shp[pos:pos + 8])
        pos += 8
        content = shp[pos:pos + clen * 2]
        pos += clen * 2
        stype = struct.unpack("<i", content[:4])[0] if len(content) >= 4 else 0
        if stype not in (5, 15, 25):
            out.append([])
            continue
        nparts, npts = struct.unpack("<ii", content[36:44])
        parts = list(struct.unpack(f"<{nparts}i", content[44:44 + 4 * nparts]))
        off = 44 + 4 * nparts
        coords = struct.unpack(f"<{2 * npts}d", content[off:off + 16 * npts])
        pts = [(coords[2 * i], coords[2 * i + 1]) for i in range(npts)]
        parts.append(npts)
        out.append([pts[parts[i]:parts[i + 1]] for i in range(nparts)])
    return out


def read_dbf(dbf: bytes):
    nrec, hlen, rlen = struct.unpack("<IHH", dbf[4:12])
    fields, p = [], 32
    while dbf[p] != 0x0D:
        fields.append((dbf[p:p + 11].split(b"\0")[0].decode("ascii", "replace"), dbf[p + 16]))
        p += 32
    rows = []
    for i in range(nrec):
        rec = dbf[hlen + i * rlen: hlen + (i + 1) * rlen]
        q, row = 1, {}
        for name, flen in fields:
            row[name] = rec[q:q + flen].decode("utf-8", "replace").strip()
            q += flen
        rows.append(row)
    return rows


class StateLocator:
    def __init__(self):
        self.shapes: list = []   # (code, bbox, rings)

    def load_census_zip(self, data: bytes):
        z = zipfile.ZipFile(io.BytesIO(data))
        shp_name = next(n for n in z.namelist() if n.lower().endswith(".shp"))
        dbf_name = next(n for n in z.namelist() if n.lower().endswith(".dbf"))
        for rings, row in zip(read_shp_polygons(z.read(shp_name)), read_dbf(z.read(dbf_name))):
            self._add(row.get("STUSPS") or norm_state(row.get("NAME")), rings)

    def load_geojson(self, path: str):
        with open(path, encoding="utf-8") as f:
            gj = json.load(f)
        for feat in gj.get("features", []):
            props = feat.get("properties") or {}
            code = norm_state(props.get("STUSPS") or props.get("code") or props.get("NAME") or props.get("name"))
            g = feat.get("geometry") or {}
            if g.get("type") == "Polygon":
                rings = g["coordinates"]
            elif g.get("type") == "MultiPolygon":
                rings = [r for poly in g["coordinates"] for r in poly]
            else:
                continue
            self._add(code, rings)

    def _add(self, code, rings):
        if not code or not rings:
            return
        xs = [p[0] for r in rings for p in r]
        ys = [p[1] for r in rings for p in r]
        self.shapes.append((code, (min(xs), min(ys), max(xs), max(ys)), rings))

    def locate(self, lat, lon):
        """-> (state_code, how) with how 'outline' | 'outline-near' | 'approx', or ('', '')."""
        if self.shapes:
            for code, (x0, y0, x1, y1), rings in self.shapes:
                if x0 <= lon <= x1 and y0 <= lat <= y1 and point_in_rings(lon, lat, rings):
                    return code, "outline"
            coslat = math.cos(math.radians(lat))   # just off a generalised shoreline / border
            best, bc = float("inf"), ""
            for code, (x0, y0, x1, y1), rings in self.shapes:
                if x0 - 0.1 <= lon <= x1 + 0.1 and y0 - 0.1 <= lat <= y1 + 0.1:
                    d = seg_dist_deg(lon, lat, rings, coslat)
                    if d < best:
                        best, bc = d, code
            if bc and best * 111.0 <= 3.0:
                return bc, "outline-near"
        return approx_state(lat, lon)


def approx_state(lat, lon):
    hits = []
    for code, (s, w, n, e) in APPROX_BOXES.items():
        if code == "AK":   # crosses the antimeridian
            if lat >= 51.0 and (lon <= -129.9 or lon >= 172.0):
                hits.append((1e9, code))
            continue
        if s <= lat <= n and w <= lon <= e:
            hits.append(((n - s) * (e - w), code))
    if not hits:
        return "", ""
    hits.sort()
    return hits[0][1], "approx"


# --------------------------------------------------------------------------
# Name similarity + known campgrounds
# --------------------------------------------------------------------------
ABBREV = {"cg": "campground", "cgd": "campground", "campgrd": "campground", "sp": "state park",
          "spk": "state park", "sra": "state recreation area", "rec": "recreation", "ra": "recreation area",
          "nf": "national forest", "mt": "mount", "mtn": "mountain", "ft": "fort", "lk": "lake",
          "crk": "creek", "pt": "point", "wma": "wildlife management area"}
GENERIC = {"campground", "campgrounds", "camp", "camping", "campsite", "campsites", "site", "sites", "area",
           "recreation", "park", "state", "county", "the", "and", "of", "at", "rv", "unit", "facility",
           "national", "forest", "public", "use", "lean", "to", "leanto", "shelter", "shelters"}
# Landform words do not make two names the same place on their own ("Beaver Bay" / "Lonesome Bay").
TERRAIN = {"lake", "lakes", "bay", "point", "river", "creek", "pond", "island", "falls", "mountain", "mtn", "hill",
           "brook", "stream", "spring", "springs", "ridge", "valley", "north", "south", "east", "west", "upper",
           "lower", "big", "little", "fork", "landing", "beach", "trail", "dam", "mt", "n", "s", "e", "w"}


def name_tokens(s: str):
    s = (s or "").lower().replace("&", " and ")
    s = re.sub(r"[^a-z0-9]+", " ", s)
    toks = []
    for t in s.split():
        toks.extend(ABBREV.get(t, t).split())
    return toks


def name_similarity(a: str, b: str) -> float:
    """0..1. Compares the distinctive words (generic words such as "campground" or
    "state park" removed; whole names when one has nothing else). A name whose
    distinctive words are all inside the other name counts at least 0.8."""
    ta, tb = name_tokens(a), name_tokens(b)
    if not ta or not tb:
        return 0.0
    full = difflib.SequenceMatcher(None, " ".join(ta), " ".join(tb)).ratio()
    ca = [t for t in ta if t not in GENERIC]
    cb = [t for t in tb if t not in GENERIC]
    core = 0.0
    if ca and cb:
        core = difflib.SequenceMatcher(None, " ".join(ca), " ".join(cb)).ratio()
        sa, sb = set(ca), set(cb)
        if (sa <= sb or sb <= sa) and any(len(t) >= 3 for t in (sa & sb)):
            core = max(core, 0.8)
        distinct = lambda ts: {t for t in ts if t not in TERRAIN and not t.isdigit()}
        if (distinct(ca) or distinct(cb)) and not (distinct(ca) & distinct(cb)):
            core = min(core, 0.5)
    return round(core if (ca and cb) else full, 3)


class SpatialIndex:
    CELL = 0.01

    def __init__(self):
        self.cells: dict = {}

    def add(self, lat, lon, item):
        key = (int(math.floor(lat / self.CELL)), int(math.floor(lon / self.CELL)))
        self.cells.setdefault(key, []).append((lat, lon, item))

    def find_dup(self, lat, lon, name):
        """Nearest-best already-listed row within 150 m with name similarity >= 0.6."""
        ci, cj = int(math.floor(lat / self.CELL)), int(math.floor(lon / self.CELL))
        best = None
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                for la, lo, item in self.cells.get((ci + di, cj + dj), ()):
                    d = haversine_m(lat, lon, la, lo)
                    if d > DUP_DIST_M:
                        continue
                    s = name_similarity(name, item["name"])
                    if s >= DUP_SIM and (best is None or (s, -d) > (best[1], -best[0])):
                        best = (d, s, item)
        return best


def _num(v):
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        try:
            return float(v)
        except ValueError:
            return None
    return None


def _known_from_row(row, label):
    if isinstance(row, list):
        if len(row) >= 4 and isinstance(row[1], str):
            la, lo = _num(row[2]), _num(row[3])
            if la is not None and lo is not None and -90 <= la <= 90 and -180 <= lo <= 180:
                return {"name": row[1], "lat": la, "lon": lo, "ref": f"{label}:{row[0]}"}
        return None
    if isinstance(row, dict):
        lk = {str(k).lower(): k for k in row}

        def pick(*names):
            for n in names:
                if n in lk:
                    return row[lk[n]]
            return None
        name = pick("name", "facilityname", "facility_name", "title", "n")
        la = _num(pick("lat", "latitude", "facilitylatitude"))
        lo = _num(pick("lon", "lng", "long", "longitude", "facilitylongitude"))
        if isinstance(name, str) and la is not None and lo is not None:
            return {"name": name, "lat": la, "lon": lo,
                    "ref": f"{label}:{pick('id', 'facilityid', 'ref')}"}
    return None


def load_known(dirs, log) -> SpatialIndex:
    """Reads every *.json under the --known folders. Rows may be lists shaped like
    data/campstate ([id, name, lat, lon, ...]) or objects with name/lat/lon keys."""
    idx = SpatialIndex()
    total = 0
    for d in dirs:
        d = d.strip()
        if not d:
            continue
        if not os.path.exists(d):
            log(f"  known: {d} not found (skipped)")
            continue
        files = [d] if os.path.isfile(d) else sorted(glob.glob(os.path.join(d, "**", "*.json"), recursive=True))
        for fp in files:
            try:
                with open(fp, encoding="utf-8") as f:
                    data = json.load(f)
            except (OSError, ValueError):
                log(f"  known: cannot read {fp} (skipped)")
                continue
            label = os.path.basename(os.path.dirname(fp)) + "/" + os.path.basename(fp)
            stack = [(data, 0)]
            while stack:
                node, depth = stack.pop()
                if depth > 6:
                    continue
                k = _known_from_row(node, label) if depth > 0 else None
                if k:
                    idx.add(k["lat"], k["lon"], k)
                    total += 1
                    continue
                if isinstance(node, dict):
                    stack.extend((v, depth + 1) for v in node.values() if isinstance(v, (list, dict)))
                elif isinstance(node, list):
                    stack.extend((v, depth + 1) for v in node if isinstance(v, (list, dict)))
    log(f"  known campgrounds loaded: {total}")
    return idx


# --------------------------------------------------------------------------
# Classification
# --------------------------------------------------------------------------
CLOSED_RE = re.compile(r"decommission|closed[\s_-]*permanent|permanent(ly)?[\s_-]*closed|closed for good|"
                       r"no longer (open|in service|exists|operat)|removed from service|abandoned|obliterated|"
                       r"demolished")
CAMP_RE = re.compile(r"\bcamp ?grounds?\b|\bcamp-?sites?\b|\bcamping\b|\bcamps?\b|\bcampers?\b|\brv\b|"
                     r"\btent(s|ing)?\b|\bcabins?\b|\byurts?\b|\btipis?\b|\bteepees?\b|\blean-?tos?\b|\bprimitive\b|\bback ?country\b|"
                     r"\bdispersed\b|\bbackpack(ing|ers?)?\b|\bcg\b|\bbivouac\b|"
                     r"\b(adirondack|trail|overnight|camping) shelters?\b|\bgroup areas?\b")
NAME_CAMP_RE = re.compile(r"\bcamp ?grounds?\b|\bcamp-?sites?\b|\bcamping\b|\brv (park|sites?|camp\w*)\b|"
                          r"\btent (sites?|area|pads?)\b|\bcabins?\b|\byurts?\b|\blean-?tos?\b|"
                          r"\b(group|horse|equestrian|primitive|backcountry|dispersed|walk-in|hike-in|boat-in|"
                          r"canoe|backpack|youth|scout|fish|hunt\w*) camps?\b|\bcamp$|\bcg$|"
                          r"\b(adirondack|trail) shelters?\b|"
                          r"\b(primitive|backcountry|dispersed|canoe|backpack|boat-in|walk-in|hike-in) sites?\b")
CAMP_NOISE_RE = re.compile(r"\b(rv )?(dump|sani(tary|tation)?) ?stations?\b|\bday ?camps?\b|"
                           r"\bcamp (road|rd|street|st)\b|\bno camping\b|\bcamping (prohibited|not allowed)\b")
KIND_NOISE_RE = re.compile(r"\bcamping (and|&) cabins\b|\bcabins (and|&) camping\b")
OUT_RE = re.compile(r"\bboat (ramps?|launch(es)?|landings?|access(es)?)\b|\b(ramps?|launch(es)?|boat-?launch(es)?)\b|"
                    r"\btrail ?heads?\b|\b(canoe|kayak|carry-?in|car-?top) (launch|access|put-?in)\w*\b|\bput-?ins?\b")
DAY_RE = re.compile(r"\bday[- ]?use\b|\bpicnic\w*\b|\bshelters?\b|\bpavilions?\b|\bgazebos?\b|\bramadas?\b|"
                    r"\boverlooks?\b|\bscenic (view|vista|overlook)s?\b|\bvista( point)?\b|\bview ?points?\b")
NAME_DAY_STRONG_RE = re.compile(r"\bday[- ]?use\b|\bpicnic\w*\b|\bpavilions?\b|\bgazebos?\b|\bramadas?\b|"
                                r"\boverlooks?\b|\bscenic (view|vista|overlook)s?\b|\bvista( point)?\b")
SHEL_RE = re.compile(r"\bshelters?\b|\bpavilions?\b|\bgazebos?\b|\bramadas?\b")
KIND_RULES = [
    ("horse", re.compile(r"\bhorse ?(camp\w*|sites?|stalls?|corrals?|trail camp)\b|\bwith horses\b|"
                         r"\bequestrian\b|\bequine\b|\bstock camp\b|\bhorseman\b")),
    ("grp", re.compile(r"\bgroups?\b")),
    ("cab", re.compile(r"\bcabins?\b|\byurts?\b|\bcottages?\b|\btipis?\b|\bteepees?\b")),
    ("prim", re.compile(r"\bprimitive\b|\bback ?country\b|\bdispersed\b|\bbackpack\w*\b|\bwalk-?in\b|\bhike-?in\b|"
                        r"\bboat-?in\b|\bcanoe\b|\bkayak\b|\bpaddle\w*\b|\bwater trail\b|\bremote\b|\bwilderness\b|"
                        r"\blean-?tos?\b|\b(adirondack|trail) shelters?\b|\bhammock\b")),
]


def _last_pos(rx, text):
    pos = -1
    for m in rx.finditer(text):
        pos = m.start()
    return pos


def kind_for(text: str) -> str:
    text = KIND_NOISE_RE.sub(" ", CAMP_NOISE_RE.sub(" ", text))
    for k, rx in KIND_RULES:
        if rx.search(text):
            return k
    return "c"


def classify(type_text: str, name: str, status_text: str):
    """-> (cls, kind, why) with cls 'camp' | 'day' | 'out'.
    The type / activity fields decide first; the name breaks ties or decides when they are silent."""
    t = CAMP_NOISE_RE.sub(" ", (type_text or "").lower())
    n_raw = (name or "").lower()
    n = CAMP_NOISE_RE.sub(" ", n_raw)
    st = (status_text or "").lower()
    if CLOSED_RE.search(st) or CLOSED_RE.search(t) or re.search(r"decommission|permanently closed|closed permanently", n_raw):
        return "out", "", "closed for good (decommissioned / closed permanently)"
    t_camp, t_out, t_day = bool(CAMP_RE.search(t)), bool(OUT_RE.search(t)), bool(DAY_RE.search(t))
    n_camp, n_out, n_day = bool(NAME_CAMP_RE.search(n)), bool(OUT_RE.search(n)), bool(DAY_RE.search(n))

    def day(src):
        k = "shel" if (SHEL_RE.search(t) or SHEL_RE.search(n)) else "day"
        label = "picnic shelter / pavilion" if k == "shel" else "day-use / picnic area / overlook"
        return "day", k, f"activating spot: {label} (by {src})"

    def camp(src):
        return "camp", kind_for(t + " | " + n), f"campground (by {src})"

    if t_out and not t_camp:
        return "out", "", "boat ramp / trailhead (type field)"
    if t_camp:
        if n_out and not n_camp:
            return "out", "", "boat ramp / trailhead (name)"
        if n_day and not n_camp and NAME_DAY_STRONG_RE.search(n):
            return day("name, type field mixed")
        if t_day and _last_pos(DAY_RE, t) > _last_pos(CAMP_RE, t) and not n_camp:
            return day("type field")
        return camp("type field")
    if t_day:
        return day("type field")
    if n_camp or n_out or n_day:          # type fields silent: the name decides (last word wins)
        pos = {"camp": _last_pos(NAME_CAMP_RE, n), "out": _last_pos(OUT_RE, n), "day": _last_pos(DAY_RE, n)}
        winner = max(pos, key=lambda k: pos[k])
        if winner == "out":
            return "out", "", "boat ramp / trailhead (name)"
        if winner == "day":
            return day("name")
        return camp("name")
    return "out", "", "not a campground or activating spot"


# --------------------------------------------------------------------------
# ArcGIS layer reading
# --------------------------------------------------------------------------
DROP_PARAMS = {"f", "outsr", "returngeometry", "resultoffset", "resultrecordcount", "outfields",
               "returnidsonly", "returncountonly", "token", "orderbyfields", "objectids"}


def parse_layer_url(url: str):
    """-> (layer base URL, where, other query params kept as given)."""
    sp = urllib.parse.urlsplit(url.strip())
    path = sp.path.rstrip("/")
    is_query = path.lower().endswith("/query")
    base_path = path[: -len("/query")] if is_query else path
    base = urllib.parse.urlunsplit((sp.scheme, sp.netloc, base_path, "", ""))
    where, extra = "1=1", []
    for k, v in urllib.parse.parse_qsl(sp.query, keep_blank_values=True):
        kl = k.lower()
        if kl == "where":
            where = v.strip() or "1=1"
        elif kl not in DROP_PARAMS:
            extra.append((k, v))
    return base, where, extra


def query_url(base, where, extra, **params):
    q = [("where", where)] + list(extra) + [("outFields", "*"), ("returnGeometry", "true"), ("outSR", "4326")]
    q += [(k, str(v)) for k, v in params.items()]
    q.append(("f", "json"))
    return base + "/query?" + urllib.parse.urlencode(q)


def _clean_text(s, limit=120):
    s = re.sub(r"<[^>]+>", " ", str(s if s is not None else ""))
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"^(©|\(c\)|copyright)\s*(\d{4}\s*)?", "", s, flags=re.I).strip()
    return s[:limit]


PATH_AGENCY = [("us_mn_state_dnr", "Minnesota DNR")]
HOST_AGENCY = [("fs.usda.gov", "USDA Forest Service"), ("fs.fed.us", "USDA Forest Service"),
               ("nps.gov", "National Park Service"), ("blm.gov", "Bureau of Land Management"),
               ("usace.army.mil", "US Army Corps of Engineers"), ("fws.gov", "US Fish and Wildlife Service"),
               ("dnr.state.mn.us", "Minnesota DNR"), ("dec.ny.gov", "New York State DEC")]


def agency_for(layer_meta, service_meta, base):
    sm = service_meta or {}
    for src in (layer_meta.get("copyrightText"), sm.get("copyrightText"),
                (sm.get("documentInfo") or {}).get("Author"), (sm.get("documentInfo") or {}).get("Company")):
        t = _clean_text(src)
        if len(t) >= 3:
            return re.split(r"(?<=[a-z\)])\.\s|;|\|", t)[0].strip()[:100]
    host = (urllib.parse.urlsplit(base).hostname or "").lower()
    for part, name in PATH_AGENCY:
        if part in base.lower():
            return name
    for part, name in HOST_AGENCY:
        if host.endswith(part):
            return name
    return host


NAME_PRIORITY = ["name", "sitename", "facilityname", "facname", "recareaname", "campgroundname", "campground",
                 "campname", "poiname", "featname", "featurename", "commonname", "assetname", "locname",
                 "locationname", "signname", "displayname", "recname", "label", "title", "facility"]
NAME_EXCLUDE = re.compile(r"park|county|state|forest|district|region|city|owner|manag|agency|unit|lake|river|road|"
                          r"admin|created|edit|file|photo|image|contact|type|class")
TYPE_FIELD_RE = re.compile(r"type|class|categ|activit|kind|asset|amenit|subtype|sitecat|(^|_)use(_|$)|usage|desig|"
                           r"purpose|rectyp|^feature$|^feat$|^poi$|^camp$|^camping$")
TYPE_EXCLUDE = re.compile(r"name|url|link|web|phone|mail|desc|comment|note|remark|direct|date|time|created|edited|"
                          r"editor|globalid|objectid|shape|fee|season|status|photo|image|(^|_)id$|_id(_|$)|count|"
                          r"num|acre|length|reserv|book|open|closed|capacity|elev|lat|lon|_x$|_y$")
URL_FIELD_RE = re.compile(r"url|link|web|page|homepage|hyperlink|moreinfo")
RES_FIELD_RE = re.compile(r"reserv|booking|book")
STATUS_FIELD_RE = re.compile(r"status|closure|^open$|^closed$|openclosed|open_closed|operational")
STATE_FIELDS = {"state", "st", "stateabbr", "state_abbr", "stusps", "statecode", "state_code", "statename",
                "state_name", "st_abbr", "stabbr", "state_ab", "st_name", "stateabbrev"}
PARKNAME_RE = re.compile(r"park|unit|forest|property|mgmt|manag")
PARK_STRONG_RE = re.compile(r"park|forest|property|mgmt|manag|recarea|rec_area")
YESNO = {"y", "n", "yes", "no", "true", "false", "t", "f", "0", "1", "none", "null", "n/a", "na", "unknown", ""}


def _code_str(v):
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v)


class LayerSchema:
    """What one layer's metadata says: fields and their roles, geometry, page size, code lists."""

    def __init__(self, meta: dict):
        self.fields = [f for f in (meta.get("fields") or []) if isinstance(f, dict) and f.get("name")]
        self.oid = meta.get("objectIdField") or next(
            (f["name"] for f in self.fields if f.get("type") == "esriFieldTypeOID"), None)
        self.gid = next((f["name"] for f in self.fields if f.get("type") == "esriFieldTypeGlobalID"), None)
        self.geom = meta.get("geometryType") or ""
        self.max_rec = int(meta.get("maxRecordCount") or 1000)
        self.paging = (meta.get("advancedQueryCapabilities") or {}).get("supportsPagination", True)
        self.domains = {}
        for f in self.fields:
            d = f.get("domain")
            if isinstance(d, dict) and d.get("type") == "codedValue":
                self.domains[f["name"]] = {_code_str(c.get("code")): c.get("name") for c in d.get("codedValues") or []}
        self.type_field = meta.get("typeIdField") or None
        self.types = {}
        for t in meta.get("types") or []:
            doms = {}
            for fname, d in (t.get("domains") or {}).items():
                if isinstance(d, dict) and d.get("type") == "codedValue":
                    doms[fname] = {_code_str(c.get("code")): c.get("name") for c in d.get("codedValues") or []}
            self.types[_code_str(t.get("id"))] = (t.get("name"), doms)
        squash = {re.sub(r"[^a-z0-9]", "", f["name"].lower()): f["name"] for f in self.fields}
        low = {f["name"].lower(): f["name"] for f in self.fields}
        self.name_f = next((squash[p] for p in NAME_PRIORITY if p in squash), None)
        disp = meta.get("displayField")
        if not self.name_f and disp in low.values() and not TYPE_FIELD_RE.search(disp.lower()) \
                and not NAME_EXCLUDE.search(disp.lower()):
            self.name_f = disp
        if not self.name_f:
            self.name_f = next((f["name"] for f in self.fields if "name" in f["name"].lower()
                                and not NAME_EXCLUDE.search(f["name"].lower())
                                and f.get("type") in (None, "esriFieldTypeString")), None)
        cands = [f["name"] for f in self.fields if "name" in f["name"].lower() and "type" not in f["name"].lower()
                 and PARKNAME_RE.search(f["name"].lower()) and f["name"] != self.name_f]
        strong = [c for c in cands if PARK_STRONG_RE.search(c.lower())]
        self.park_name_f = (strong or cands or [None])[0]
        self.site_name_f = next((f["name"] for f in self.fields if re.search(r"(site|unit|loop)_?(name|no|num)", f["name"].lower())
                                 and "type" not in f["name"].lower()
                                 and f["name"] not in (self.name_f, self.park_name_f)), None)
        self.type_fs = []
        for f in self.fields:
            nl = f["name"].lower()
            if f["name"] in (self.name_f, self.oid, self.gid):
                continue
            telling_codes = f["name"] in self.domains and any(
                CAMP_RE.search(str(v).lower()) or DAY_RE.search(str(v).lower()) or OUT_RE.search(str(v).lower())
                for v in self.domains[f["name"]].values())
            if f["name"] == self.type_field or ((TYPE_FIELD_RE.search(nl) or telling_codes)
                                                and not TYPE_EXCLUDE.search(nl)):
                self.type_fs.append(f["name"])
        self.url_fs = [f["name"] for f in self.fields if URL_FIELD_RE.search(f["name"].lower())
                       and not RES_FIELD_RE.search(f["name"].lower())
                       and not re.search(r"photo|image|img|pic|thumb|map|icon|pdf", f["name"].lower())]
        self.res_fs = [f["name"] for f in self.fields if RES_FIELD_RE.search(f["name"].lower())]
        self.status_fs = [f["name"] for f in self.fields if STATUS_FIELD_RE.search(f["name"].lower())]
        self.state_f = next((low[s] for s in low if s in STATE_FIELDS), None)

    def decode(self, attrs: dict, fname):
        if not fname:
            return None
        v = attrs.get(fname)
        if v is None:
            return None
        sv = _code_str(v)
        if fname == self.type_field and sv in self.types:
            return self.types[sv][0]
        tid = attrs.get(self.type_field) if self.type_field else None
        if tid is not None:
            doms = self.types.get(_code_str(tid), (None, {}))[1]
            if fname in doms and sv in doms[fname]:
                return doms[fname][sv]
        if fname in self.domains and sv in self.domains[fname]:
            return self.domains[fname][sv]
        return v


def first_url(val) -> str:
    """The record's own link, or "" (never made up)."""
    if val is None:
        return ""
    s = str(val).strip()
    m = re.search(r"""href\s*=\s*["']([^"']+)["']""", s, re.I)
    if m:
        s = m.group(1).strip()
    if re.match(r"^https?://\S+$", s, re.I) and not forbidden_source(s):
        return s
    return ""


def geometry_point(geom):
    """-> (lat, lon, loop_rings or None) from an Esri JSON geometry in WGS84."""
    if not isinstance(geom, dict):
        return None
    if "x" in geom and "y" in geom:
        x, y = _num(geom.get("x")), _num(geom.get("y"))
        if x is None or y is None or math.isnan(x) or math.isnan(y):
            return None
        return y, x, None
    if geom.get("points"):
        p = geom["points"][0]
        return p[1], p[0], None
    if geom.get("rings"):
        rings = [r for r in geom["rings"] if len(r) >= 3]
        c = polygon_centroid(rings)
        if not c:
            return None
        return c[1], c[0], simplify_rings(rings)
    if geom.get("paths"):
        path = max(geom["paths"], key=len)
        p = path[len(path) // 2]
        return p[1], p[0], None
    return None


def _check_sr(data, feats):
    if not feats:
        return
    sr = data.get("spatialReference") or {}
    wkid = sr.get("latestWkid") or sr.get("wkid")
    g = feats[0].get("geometry") or {}
    x = g.get("x")
    if x is None and g.get("rings"):
        x = g["rings"][0][0][0]
    if wkid and wkid not in (4326, 4269, 4283, 4258, 104199) and x is not None and abs(x) > 180:
        raise FetchError(f"server did not return WGS84 coordinates (wkid {wkid})")


class LayerReader:
    def __init__(self, fetcher: Fetcher, log, must_stop):
        self.f = fetcher
        self.log = log
        self.must_stop = must_stop   # callable -> True when the run has to stop mid-layer

    def read(self, url: str, parks):
        res = {"layer": url, "status": "read OK", "why": "", "features": 0, "agency": "",
               "camps": [], "dayuse": [], "left_out": [], "retry_later": False}
        base, where, extra = parse_layer_url(url)
        meta = self.f.get_json(base + "?f=json")
        ltype = (meta.get("type") or "").lower()
        if ltype and "feature" not in ltype and ltype != "table":
            raise FetchError(f"not a feature layer ({meta.get('type')})")
        schema = LayerSchema(meta)
        if not schema.fields:
            raise FetchError("layer has no fields in its metadata")
        service_meta = None
        if not _clean_text(meta.get("copyrightText")):
            try:
                service_meta = self.f.get_json(re.sub(r"/\d+$", "", base) + "?f=json")
            except FetchError:
                service_meta = None
        res["agency"] = agency_for(meta, service_meta, base)
        hint_states = sorted(parks_states(parks))
        for feat in self._features(base, where, extra, schema):
            res["features"] += 1
            try:
                self._one(feat, schema, base, res, hint_states)
            except Exception as e:  # one bad record never stops the layer
                res["left_out"].append({"name": "", "source_url": base,
                                        "why": f"bad record: {type(e).__name__}: {e}"[:200]})
        return res

    def _features(self, base, where, extra, schema: LayerSchema):
        page = max(1, min(schema.max_rec or 1000, PAGE_CAP))
        use_ids = schema.paging is False
        if not use_ids:
            offset = 0
            for _ in range(MAX_PAGES):
                if self.must_stop():
                    raise FetchError("time ran out while reading this layer", retry_later=True)
                params = {"resultOffset": offset, "resultRecordCount": page}
                if schema.oid:
                    params["orderByFields"] = schema.oid
                try:
                    data = self.f.get_json(query_url(base, where, extra, **params))
                except FetchError as e:
                    if offset == 0 and "pagination" in str(e).lower():
                        use_ids = True
                        break
                    raise
                feats = data.get("features") or []
                _check_sr(data, feats)
                yield from feats
                offset += len(feats)
                if not feats or (not data.get("exceededTransferLimit") and len(feats) < page):
                    return
            if not use_ids:
                return
        # older servers without pagination: ask for the ids, then fetch them in batches
        q = [("where", where)] + list(extra) + [("returnIdsOnly", "true"), ("f", "json")]
        ids = sorted(self.f.get_json(base + "/query?" + urllib.parse.urlencode(q)).get("objectIds") or [])
        for i in range(0, len(ids), page):
            if self.must_stop():
                raise FetchError("time ran out while reading this layer", retry_later=True)
            chunk = ",".join(str(x) for x in ids[i:i + page])
            data = self.f.get_json(query_url(base, "1=1", [], objectIds=chunk))
            feats = data.get("features") or []
            _check_sr(data, feats)
            yield from feats

    def _one(self, feat, schema: LayerSchema, base, res, hint_states):
        attrs = feat.get("attributes") or {}
        oid = attrs.get(schema.oid) if schema.oid else None
        if isinstance(oid, float) and oid.is_integer():
            oid = int(oid)
        rec_id = attrs.get(schema.gid) if schema.gid and attrs.get(schema.gid) else oid
        source_url = f"{base}/query?objectIds={oid}&outFields=*&f=html" if oid is not None else base
        name = _clean_text(schema.decode(attrs, schema.name_f), 150)
        type_vals = []
        for fname in schema.type_fs:
            v = schema.decode(attrs, fname)
            if v is None or (isinstance(v, (int, float)) and not isinstance(v, bool)):
                continue
            sv = _clean_text(v, 200)
            if sv.lower() in YESNO or len(sv) > 120 or re.fullmatch(r"[\d\s.,:/-]+", sv):
                continue
            type_vals.append(sv)
        type_text = " | ".join(type_vals)
        status_vals = [_clean_text(schema.decode(attrs, f), 80) for f in schema.status_fs]
        status_vals = [s for s in status_vals if s.lower() not in YESNO]
        open_status = status_vals[0] if status_vals else ""
        name_built = False
        if not name:
            park = _clean_text(schema.decode(attrs, schema.park_name_f), 100)
            if park and type_vals:
                site = _clean_text(schema.decode(attrs, schema.site_name_f), 40) if schema.site_name_f else ""
                name, name_built = f"{park} - {type_vals[0]}" + (f" {site}" if site else ""), True
        if not name and schema.site_name_f:
            site = _clean_text(schema.decode(attrs, schema.site_name_f), 100)
            if len(site) >= 4 and re.search(r"[a-z]{3}", site.lower()):
                name, name_built = site + (f" - {type_vals[0]}" if type_vals else ""), True
        cls, kind, why = classify(type_text, name, " | ".join(status_vals))
        if cls == "out":
            res["left_out"].append({"name": name, "source_url": source_url, "why": why})
            return
        if not name:
            res["left_out"].append({"name": "", "source_url": source_url, "why": "no name in the record"})
            return
        pt = geometry_point(feat.get("geometry"))
        if not pt:
            res["left_out"].append({"name": name, "source_url": source_url, "why": "bad record: no usable geometry"})
            return
        lat, lon, loop = pt
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            res["left_out"].append({"name": name, "source_url": source_url, "why": "bad record: coordinates not WGS84"})
            return
        page = next((u for u in (first_url(attrs.get(f)) for f in schema.url_fs) if u), "")
        reserve = next((u for u in (first_url(attrs.get(f)) for f in schema.res_fs) if u), "")
        state = norm_state(schema.decode(attrs, schema.state_f)) if schema.state_f else ""
        rid = hashlib.sha1(f"{base}|{rec_id}".encode()).hexdigest()[:10]
        why_full = why + (f"; type: {type_text[:80]}" if type_text else "") + \
            ("; name built from park name + type" if name_built else "")
        row = {"id": f"L-{rid}", "name": name, "lat": round(lat, 6), "lon": round(lon, 6), "kind": kind,
               "page": page, "reserve": reserve, "agency": res["agency"], "source_url": source_url,
               "open_status": open_status, "loop": loop, "why": why_full, "state": state,
               "state_by": "row" if state else "", "hint_states": hint_states, "name_built": name_built}
        (res["camps"] if cls == "camp" else res["dayuse"]).append(row)


# --------------------------------------------------------------------------
# Inputs
# --------------------------------------------------------------------------
PARKINFO_MAP: dict = {}


def load_parkinfo(d: str):
    """Optional: data/parkinfo/US-XX.json tells the state of each park ref in the camping file."""
    PARKINFO_MAP.clear()
    if not d or not os.path.isdir(d):
        return
    for fp in glob.glob(os.path.join(d, "US-*.json")):
        st = os.path.basename(fp)[3:5]
        try:
            with open(fp, encoding="utf-8") as f:
                for ref in (json.load(f) or {}).get("parks") or {}:
                    PARKINFO_MAP[ref] = st
        except (OSError, ValueError, AttributeError):
            continue


def parks_states(parks) -> set:
    """States named by the parks a layer covers ('US-KY', 'KY' in a state/area key, or park refs via parkinfo)."""
    found = set()

    def walk(x, key=""):
        if isinstance(x, str):
            if key in ("state", "states", "area", "areas") and norm_state(x):
                found.add(norm_state(x))
            for m in re.finditer(r"\bUS-([A-Z]{2})\b", x):
                if m.group(1) in STATE_CODES:
                    found.add(m.group(1))
            for m in re.finditer(r"\b[A-Z]{2}-\d+\b", x):
                if m.group(0) in PARKINFO_MAP:
                    found.add(PARKINFO_MAP[m.group(0)])
        elif isinstance(x, dict):
            for k, v in x.items():
                walk(str(k))
                walk(v, str(k).lower())
        elif isinstance(x, list):
            for v in x:
                walk(v, key)
    walk(parks)
    return found


def load_inputs(patterns):
    files = []
    for p in patterns:
        hits = sorted(glob.glob(p))
        files.extend(hits if hits else ([p] if os.path.isfile(p) else []))
    layers: dict = {}
    for fp in files:
        with open(fp, encoding="utf-8") as f:
            data = json.load(f)
        lay = data.get("layers") if isinstance(data, dict) else data
        if isinstance(lay, dict):
            items = list(lay.items())
        elif isinstance(lay, list):
            items = [(u, []) for u in lay if isinstance(u, str)]
        else:
            continue
        for url, parks in items:
            url = str(url).strip()
            if url:
                layers.setdefault(url, []).extend(parks if isinstance(parks, list) else [parks])
    return files, layers


# --------------------------------------------------------------------------
# Run
# --------------------------------------------------------------------------
REPORT_COLS = ["layer", "parks_covered", "result", "why", "features_read", "campgrounds_kept",
               "activating_spots_kept", "left_out", "duplicates", "duplicates_in_run", "states", "agency"]


def layer_key(url):
    return hashlib.sha1(url.encode()).hexdigest()[:16]


def _write_rows_json(path, doc):
    """Same JSON as json.dump, laid out one row (and one extra entry) per line for small diffs."""
    d = lambda o: json.dumps(o, ensure_ascii=False)
    parts = ['{"src": ' + d(doc["src"]) + ', "read": ' + d(doc["read"]) + ',', ' "camps": [']
    parts.append(",\n".join("  " + d(r) for r in doc["camps"]))
    parts.append(" ],")
    parts.append(' "extra": {')
    parts.append(",\n".join("  " + d(k) + ": " + d(v) for k, v in doc["extra"].items()))
    parts.append(" }")
    parts.append("}")
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write("\n".join(parts) + "\n")
    os.replace(tmp, path)


def _write_json(path, obj, indent=1):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=indent)
        f.write("\n")
    os.replace(tmp, path)


class Runner:
    def __init__(self, args, transport=urllib_transport, clock=time.monotonic, sleep=time.sleep, today=None,
                 log=None):
        self.a = args
        self.clock = clock
        self.t0 = clock()
        self.today = today or date.today().isoformat()
        self.log = log or (lambda m: print(m, file=sys.stderr, flush=True))
        self.out = os.path.abspath(args.out)
        self.work = os.path.join(self.out, "work")
        contact = os.environ.get("KPC_CONTACT", "").strip()
        if not contact:
            self.log("warning: KPC_CONTACT is not set; the User-Agent says 'contact not set'")
            contact = "contact not set"
        self.fetcher = Fetcher(contact, args.cache or os.path.join(self.work, "cache"), args.cache_days,
                               transport=transport, clock=clock, sleep=sleep, log=self.log)
        self.max_s = args.max_minutes * 60.0

    def elapsed(self):
        return self.clock() - self.t0

    def run(self) -> int:
        files, layers = load_inputs(self.a.inputs)
        if not files:
            self.log(f"no camping file matched {self.a.inputs}")
            return 2
        os.makedirs(os.path.join(self.work, "layers"), exist_ok=True)
        load_parkinfo(self.a.parkinfo)
        urls = list(layers)
        if self.a.limit:
            urls = urls[: self.a.limit]
        want = {s for s in (norm_state(x) for x in re.split(r"[,\s]+", self.a.states or "")) if s}
        state_path = os.path.join(self.out, "state.json")
        state = {"version": VERSION, "done": {}}
        if self.a.resume and os.path.exists(state_path):
            with open(state_path, encoding="utf-8") as f:
                state = json.load(f)
            state.setdefault("done", {})
        else:
            for fp in glob.glob(os.path.join(self.work, "layers", "*.json")):
                os.remove(fp)
        reader = LayerReader(self.fetcher, self.log, lambda: self.elapsed() > self.max_s + 240)
        timed_out = False
        self.log(f"kpc_camp_layers {VERSION}: {len(urls)} layer(s) from {len(files)} file(s)")
        for i, url in enumerate(urls, 1):
            if url in state["done"]:
                continue
            if self.elapsed() > self.max_s:
                timed_out = True
                break
            parks = layers[url]
            hint = parks_states(parks)
            if want and hint and not (hint & want):
                res = {"layer": url, "status": "skipped", "why": "covers other states (by its parks list)",
                       "features": 0, "agency": "", "camps": [], "dayuse": [], "left_out": []}
            else:
                self.log(f"[{i}/{len(urls)}] {url[:120]}")
                try:
                    res = reader.read(url, parks)
                except FetchError as e:
                    res = {"layer": url, "status": "failed", "why": str(e), "features": 0, "agency": "",
                           "camps": [], "dayuse": [], "left_out": [], "retry_later": e.retry_later}
                    timed_out = "time ran out" in str(e)
                except Exception as e:  # never stop the run for one layer
                    res = {"layer": url, "status": "failed", "why": f"unexpected: {type(e).__name__}: {e}"[:200],
                           "features": 0, "agency": "", "camps": [], "dayuse": [], "left_out": []}
            res["parks_covered"] = len(parks)
            _write_json(os.path.join(self.work, "layers", layer_key(url) + ".json"), res, indent=None)
            if not res.get("retry_later"):
                state["done"][url] = {"status": res["status"], "key": layer_key(url)}
            state["updated"] = self.today
            _write_json(state_path, state)
            self.log(f"    {res['status']} {res.get('why') or ''}: features={res['features']} "
                     f"camps={len(res['camps'])} dayuse={len(res['dayuse'])} left_out={len(res['left_out'])}")
            if timed_out:
                break
        self.assemble(urls, want)
        left = [u for u in urls if u not in state["done"]]
        if left and (timed_out or self.elapsed() > self.max_s):
            self.log(f"time ran out: {len(left)} layer(s) left; run again with --resume")
            return EXIT_TIME
        self.log("done")
        return EXIT_OK

    def _locator(self):
        loc = StateLocator()
        try:
            if self.a.states_file:
                loc.load_geojson(self.a.states_file)
            elif not self.a.no_census:
                loc.load_census_zip(self.fetcher.get(CENSUS_STATES_URL, max_age_days=365))
        except (FetchError, OSError, ValueError, KeyError, zipfile.BadZipFile, StopIteration, struct.error) as e:
            self.log(f"  state outline not available ({e}); using the approximate state boxes")
        return loc

    def assemble(self, urls, want):
        results = []
        for url in urls:
            fp = os.path.join(self.work, "layers", layer_key(url) + ".json")
            if os.path.exists(fp):
                with open(fp, encoding="utf-8") as f:
                    results.append(json.load(f))
        known = load_known((self.a.known or "").split(","), self.log)
        need_loc = any(not r.get("state") for res in results for r in res["camps"] + res["dayuse"])
        loc = self._locator() if need_loc else StateLocator()
        seen = {"camps": SpatialIndex(), "dayuse": SpatialIndex()}
        out = {"camps": {}, "dayuse": {}}
        extra = {"camps": {}, "dayuse": {}}
        dups, left_rows, report = [], [], []
        for res in results:
            n = {"camps": 0, "dayuse": 0, "dup": 0, "dup_run": 0, "left": len(res["left_out"])}
            states = set()
            same_name = {}   # per layer: site-level layers list every site of one campground under one name
            for listname in ("camps", "dayuse"):
                for r in res[listname]:
                    st, how = r.get("state"), r.get("state_by")
                    if not st:
                        st, how = loc.locate(r["lat"], r["lon"])
                        if how in ("approx", "") and len(r.get("hint_states") or []) == 1:
                            st, how = r["hint_states"][0], "parks list"
                    if not st:
                        n["left"] += 1
                        left_rows.append([res["layer"], r["source_url"], r["name"], "no state found for the point"])
                        continue
                    if listname == "camps":
                        d = known.find_dup(r["lat"], r["lon"], r["name"])
                        if d:
                            n["dup"] += 1
                            dups.append([res["layer"], r["source_url"], r["name"], r["lat"], r["lon"],
                                         d[2]["name"], d[2]["ref"], round(d[0], 1), d[1], "already listed"])
                            continue
                    key = (listname, " ".join(name_tokens(r["name"])))
                    if not r.get("name_built") and key[1]:
                        near = next((o for o in same_name.get(key, ())
                                     if haversine_m(r["lat"], r["lon"], o[0], o[1]) <= SAME_NAME_M), None)
                        if near:
                            n["dup_run"] += 1
                            dups.append([res["layer"], r["source_url"], r["name"], r["lat"], r["lon"],
                                         r["name"], near[2], round(haversine_m(r["lat"], r["lon"], near[0],
                                                                               near[1]), 1), 1.0,
                                         "another site of the same campground in this layer"])
                            continue
                        same_name.setdefault(key, []).append((r["lat"], r["lon"], r["id"]))
                    d = seen[listname].find_dup(r["lat"], r["lon"], r["name"])
                    if d:
                        n["dup_run"] += 1
                        dups.append([res["layer"], r["source_url"], r["name"], r["lat"], r["lon"],
                                     d[2]["name"], d[2]["ref"], round(d[0], 1), d[1],
                                     "same place as an earlier row in this run"])
                        continue
                    seen[listname].add(r["lat"], r["lon"], {"name": r["name"], "ref": r["id"]})
                    if want and st not in want:
                        continue
                    states.add(st)
                    n[listname] += 1
                    out[listname].setdefault(st, []).append(
                        [r["id"], r["name"], r["lat"], r["lon"], r["kind"], "", r["page"], r["reserve"],
                         r["agency"], r["source_url"]])
                    ex = {"why": f"{r['why']}; state by {how}", "read_date": self.today}
                    if r.get("open_status"):
                        ex["open_status"] = r["open_status"]
                    if r.get("loop"):
                        ex["loop"] = r["loop"]
                    extra[listname].setdefault(st, {})[r["id"]] = ex
            for lo in res["left_out"]:
                left_rows.append([res["layer"], lo.get("source_url", ""), lo.get("name", ""), lo.get("why", "")])
            report.append({"layer": res["layer"], "parks_covered": res.get("parks_covered", 0),
                           "result": res["status"], "why": res.get("why", ""), "features_read": res["features"],
                           "campgrounds_kept": n["camps"], "activating_spots_kept": n["dayuse"],
                           "left_out": n["left"], "duplicates": n["dup"], "duplicates_in_run": n["dup_run"],
                           "states": " ".join(sorted(states)), "agency": res.get("agency", "")})
        for sub in ("campgrounds", "dayuse"):
            os.makedirs(os.path.join(self.out, sub), exist_ok=True)
            for fp in glob.glob(os.path.join(self.out, sub, "US-*.json")):
                os.remove(fp)
        for listname, sub in (("camps", "campgrounds"), ("dayuse", "dayuse")):
            for st, rows in sorted(out[listname].items()):
                rows.sort(key=lambda r: (r[1].lower(), r[0]))
                _write_rows_json(os.path.join(self.out, sub, f"US-{st}.json"),
                                 {"src": SRC_LABEL, "read": self.today, "camps": rows,
                                  "extra": dict(sorted(extra[listname][st].items()))})
        with open(os.path.join(self.out, "campgrounds", "report.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=REPORT_COLS, lineterminator="\n")
            w.writeheader()
            w.writerows(report)
        with open(os.path.join(self.out, "campgrounds", "duplicates.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["layer", "source_url", "name", "lat", "lon", "matched_name", "matched_ref", "distance_m",
                        "name_similarity", "why"])
            w.writerows(dups)
        with open(os.path.join(self.work, "left_out.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["layer", "source_url", "name", "why"])
            w.writerows(left_rows)


# --------------------------------------------------------------------------
# Self-test (offline: every web answer comes from tests/fixtures.json)
# --------------------------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))


def _norm_url(url: str) -> str:
    sp = urllib.parse.urlsplit(url)
    q = sorted(urllib.parse.parse_qsl(sp.query, keep_blank_values=True))
    return urllib.parse.urlunsplit((sp.scheme, sp.netloc.lower(), sp.path, urllib.parse.urlencode(q), ""))


class MockWeb:
    def __init__(self, fixtures: dict):
        self.map = {_norm_url(k): v for k, v in fixtures.items()}
        self.calls = []

    def __call__(self, url, headers):
        self.calls.append((url, dict(headers)))
        v = self.map.get(_norm_url(url))
        if v is None:
            return 404, {}, b"not in fixtures"
        body = v.get("text")
        if body is None:
            body = json.dumps(v.get("json", {}))
        return v.get("status", 200), {k.lower(): s for k, s in (v.get("headers") or {}).items()}, body.encode()


class FakeClock:
    def __init__(self):
        self.t = 1000.0

    def __call__(self):
        return self.t

    def sleep(self, s):
        self.t += max(0.0, s)


def _compare_dirs(got_dir, exp_dir, problems, tag):
    for root, _d, fnames in os.walk(exp_dir):
        for fn in fnames:
            rel = os.path.relpath(os.path.join(root, fn), exp_dir)
            gp = os.path.join(got_dir, rel)
            if not os.path.exists(gp):
                problems.append(f"{tag}: missing output {rel}")
                continue
            with open(os.path.join(root, fn), encoding="utf-8") as a, open(gp, encoding="utf-8") as b:
                if a.read() != b.read():
                    problems.append(f"{tag}: output differs from tests/expected/{rel}")


def _st_run(argv, fixtures, quiet):
    web, clock = MockWeb(fixtures), FakeClock()
    runner = Runner(build_parser().parse_args(argv), transport=web, clock=clock, sleep=clock.sleep,
                    today="2026-10-31", log=quiet)
    return runner.run(), web, runner


def selftest(write_expected=False, verbose=False) -> int:
    tdir = os.path.join(HERE, "tests")
    with open(os.path.join(tdir, "fixtures.json"), encoding="utf-8") as f:
        fixtures = json.load(f)["responses"]
    exp_dir = os.path.join(tdir, "expected")
    os.environ["KPC_CONTACT"] = os.environ.get("KPC_CONTACT") or "selftest@example.org"
    contact = os.environ["KPC_CONTACT"]
    base = ["--in", os.path.join(tdir, "sample_input", "camping-*.json"),
            "--known", os.path.join(tdir, "known", "campfed") + "," + os.path.join(tdir, "known", "not-there"),
            "--states-file", os.path.join(tdir, "fixture_states.geojson"), "--parkinfo", ""]
    problems = []
    quiet = (lambda m: print("   ", m)) if verbose else (lambda m: None)
    tmp = tempfile.mkdtemp(prefix="kpc_camp_selftest_")
    before = sorted(os.listdir(tdir))
    try:
        # ---- run 1: full run, compared with tests/expected ----
        out1 = os.path.join(tmp, "run1")
        code, web, runner = _st_run(base + ["--out", out1], fixtures, quiet)
        if code != 0:
            problems.append(f"run 1 exit code {code}, expected 0")
        if write_expected:
            shutil.rmtree(exp_dir, ignore_errors=True)
            for sub in ("campgrounds", "dayuse"):
                shutil.copytree(os.path.join(out1, sub), os.path.join(exp_dir, sub))
            print(f"expected output written to {exp_dir}")
        _compare_dirs(out1, exp_dir, problems, "run 1")
        camps, days = [], []
        for sub, bucket in (("campgrounds", camps), ("dayuse", days)):
            for fp in sorted(glob.glob(os.path.join(out1, sub, "US-*.json"))):
                with open(fp, encoding="utf-8") as f:
                    doc = json.load(f)
                if doc.get("src") != SRC_LABEL or doc.get("read") != "2026-10-31":
                    problems.append(f"bad header in {sub}/{os.path.basename(fp)}")
                bucket.extend(doc["camps"])
                if set(doc["extra"]) != {r[0] for r in doc["camps"]}:
                    problems.append(f"extra ids do not match rows in {sub}/{os.path.basename(fp)}")
        rows = camps + days
        if not camps or not days:
            problems.append("no campgrounds or no activating spots written")
        if any(len(r) != 10 for r in rows):
            problems.append("a row does not have the 10 columns")
        if any(not re.match(r"^L-[0-9a-f]{10}$", r[0]) for r in rows):
            problems.append("bad id format")
        if len({r[0] for r in rows}) != len(rows):
            problems.append("ids are not unique")
        if any(r[5] != "" for r in rows):
            problems.append("park column must be empty")
        if any(r[4] not in ("c", "cab", "prim", "grp", "horse") for r in camps):
            problems.append("bad campground kind")
        if any(r[4] not in ("day", "shel") for r in days):
            problems.append("bad activating-spot kind")
        camp_names = " | ".join(r[1].lower() for r in camps)
        for bad in ("ramp", "launch", "trailhead", "shelter", "pavilion", "picnic", "overlook", "old pine",
                    "beaver flats"):
            if bad in camp_names:
                problems.append(f"'{bad}' got into the campground list")
        if re.search(r"ramp|launch|trailhead|old pine", " | ".join(r[1].lower() for r in days)):
            problems.append("a boat ramp / trailhead / closed place got into the activating-spots list")
        if not any(r[4] == "shel" and r[7] for r in days):
            problems.append("the reservable picnic shelter lost its booking link")
        if not any(r[4] == "day" for r in days):
            problems.append("no day-use area found")
        missing = {"c", "cab", "prim", "grp", "horse"} - {r[4] for r in camps}
        if missing:
            problems.append(f"kinds not produced: {sorted(missing)}")
        if any(r[6] and not r[6].startswith("http") for r in rows):
            problems.append("a page link is not a real URL")
        with open(os.path.join(out1, "campgrounds", "duplicates.csv"), encoding="utf-8") as f:
            dup = list(csv.DictReader(f))
        if not any(d["name"] == "Bear Lake Campground" and d["why"] == "already listed"
                   and "campfed" in d["matched_ref"] for d in dup):
            problems.append("the duplicate of the known Recreation.gov row was not found")
        if not any(r[1] == "Bear Lake Campground" for r in camps):
            problems.append("a name-only match more than 150 m away was wrongly dropped")
        if not any(d["why"].startswith(("same place", "another site")) for d in dup):
            problems.append("repeated EDW rows (one per activity) were not merged")
        with open(os.path.join(out1, "campgrounds", "report.csv"), encoding="utf-8") as f:
            rep = list(csv.DictReader(f))
        if len(rep) != 8:
            problems.append(f"report has {len(rep)} layer lines, expected 8")
        for part, word in (("tokenparks", "needs sign-in"), ("busy.example", "resting"),
                           ("noindex.example", "robots"), ("openstreetmap", "forbidden")):
            if not any(part in r["layer"] and word in (r["result"] + " " + r["why"]) for r in rep):
                problems.append(f"report line for {part} should say '{word}'")
        last = {}
        for url, ts in runner.fetcher.requests:
            host = urllib.parse.urlsplit(url).netloc
            if host in last and ts - last[host] < 2.0:
                problems.append(f"less than 2 s between requests to {host}")
                break
            last[host] = ts
        if any(h.get("User-Agent") != f"KPC park tools ({contact})" for _u, h in web.calls):
            problems.append("wrong User-Agent")
        qcalls = [u for u, _h in web.calls if "/query?" in u]
        for u in qcalls:
            q = dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(u).query))
            if q.get("f") != "json" or q.get("outSR") != "4326" or q.get("returnGeometry") != "true":
                problems.append(f"query without f=json / outSR=4326 / returnGeometry=true: {u[:100]}")
                break
        edw = [u for u in qcalls if "RecreationOpportunities" in u]
        if not edw or not all("FORESTNAME = 'Superior National Forest'" in
                              dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(u).query)).get("where", "")
                              for u in edw):
            problems.append("the EDW query lost its own where")
        if not any("resultOffset=5" in u for u in qcalls):
            problems.append("paging with resultOffset did not happen")
        if any("openstreetmap" in u for u, _h in web.calls):
            problems.append("a forbidden source was fetched")
        busy = [u for u, _h in web.calls if "busy.example" in u and "robots" not in u]
        if len(busy) != 4:
            problems.append(f"the 429 host got {len(busy)} tries, expected 1 + 3 retries")
        if any("noindex.example" in u and "robots" not in u for u, _h in web.calls):
            problems.append("robots.txt was not obeyed")
        loops = []
        for fp in glob.glob(os.path.join(out1, "campgrounds", "US-*.json")):
            with open(fp, encoding="utf-8") as f:
                loops += [ex["loop"] for ex in json.load(f)["extra"].values() if "loop" in ex]
        if not loops or any(len(ring) < 4 for lp in loops for ring in lp):
            problems.append("polygon loop not kept")
        if sorted(os.listdir(tmp)) != ["run1"] or (not write_expected and sorted(os.listdir(tdir)) != before):
            problems.append("something was written outside --out")
        # ---- run 2: time runs out after the first layer (exit 3), then --resume finishes ----
        out2 = os.path.join(tmp, "run2")
        code2, web2, _r = _st_run(base + ["--out", out2, "--max-minutes", "0.01"], fixtures, quiet)
        if code2 != 3:
            problems.append(f"time-out run exit code {code2}, expected 3")
        code3, web3, _r = _st_run(base + ["--out", out2, "--resume"], fixtures, quiet)
        if code3 != 0:
            problems.append(f"resume run exit code {code3}, expected 0")
        first = {u for u, _h in web2.calls if "/query?" in u}
        if not first:
            problems.append("the time-out run did no work")
        if first & {u for u, _h in web3.calls}:
            problems.append("--resume repeated finished work")
        _compare_dirs(out2, exp_dir, problems, "resume")
        # ---- run 3: --limit and --states ----
        out3 = os.path.join(tmp, "run3")
        code4, _w, _r = _st_run(base + ["--out", out3, "--limit", "1", "--states", "US-NY"], fixtures, quiet)
        if code4 != 0 or glob.glob(os.path.join(out3, "*", "US-MN.json")):
            problems.append("--limit / --states not honoured")
        # ---- unit checks ----
        if name_similarity("Bear Lake CG", "Bear Lake Campground") < 0.6:
            problems.append("name similarity too low for CG / Campground")
        if name_similarity("Bear Lake Campground", "Pine Ridge Campground") >= 0.6:
            problems.append("name similarity too high for different names")
        if forbidden_source("https://storage.googleapis.com/x/y.zip") or \
                not forbidden_source("https://maps.google.com/x") or \
                not forbidden_source("https://overpass-api.de/api/interpreter"):
            problems.append("forbidden-source check wrong")
        if approx_state(37.84, -84.27)[0] != "KY" or approx_state(61.2, -149.9)[0] != "AK" \
                or approx_state(44.97, -93.26)[0] != "MN":
            problems.append("approximate state boxes wrong")
        b, w, e = parse_layer_url("https://x.test/arcgis/rest/services/A/MapServer/0/query?where=A%3D1&outFields=X&f=html")
        if b != "https://x.test/arcgis/rest/services/A/MapServer/0" or w != "A=1" or e:
            problems.append("parse_layer_url wrong")
        sq = [[0, 0], [0, 0.001], [0.0005, 0.0010000001], [0.001, 0.001], [0.001, 0], [0, 0]]
        if len(simplify_rings([sq])[0]) != 5:
            problems.append("3 m simplification did not drop the near-straight vertex")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if problems:
        for p in problems:
            print("  -", p)
        print("FAIL")
        return 1
    print("PASS")
    return 0


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------
def build_parser():
    p = argparse.ArgumentParser(prog="kpc_camp_layers.py",
                                description="List campgrounds (plus day-use areas / picnic shelters) "
                                            "from official agency campground layers.")
    p.add_argument("--in", dest="inputs", action="append", default=None,
                   help=f"camping JSON file(s); glob ok; repeat or comma-separate (default {DEFAULT_IN})")
    p.add_argument("--out", default="out/kpc_camp_layers", help="output folder (the only place it writes)")
    p.add_argument("--max-minutes", type=float, default=50.0, help="stop starting new layers after this (default 50)")
    p.add_argument("--resume", action="store_true", help="skip layers that <out>/state.json says are done")
    p.add_argument("--limit", type=int, default=0, help="only the first N layers")
    p.add_argument("--areas", "--states", dest="states", default="", help="e.g. US-KY,US-TN or KY,TN (default: all)")
    p.add_argument("--known", default=DEFAULT_KNOWN, help="comma list of folders with already-listed campgrounds")
    p.add_argument("--cache", default="", help="download cache folder kept between runs (default <out>/work/cache)")
    p.add_argument("--cache-days", type=float, default=6.0, help="re-download layer answers older than this")
    p.add_argument("--states-file", default="", help="local GeoJSON of state outlines (property STUSPS); default: "
                                                      "download the Census cartographic boundary file into the cache")
    p.add_argument("--no-census", action="store_true", help="do not download the Census outline; use approximate boxes")
    p.add_argument("--parkinfo", default="data/parkinfo", help="data/parkinfo folder, to get states from park refs")
    p.add_argument("--selftest", action="store_true", help="run the offline self-test; prints PASS or FAIL")
    p.add_argument("--verbose", action="store_true", help=argparse.SUPPRESS)
    p.add_argument("--write-expected", action="store_true", help=argparse.SUPPRESS)
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    if args.selftest:
        return selftest(write_expected=args.write_expected, verbose=args.verbose)
    pats = []
    for x in (args.inputs or [DEFAULT_IN]):
        pats.extend(s.strip() for s in x.split(",") if s.strip())
    args.inputs = pats
    return Runner(args).run()


if __name__ == "__main__":
    sys.exit(main())
