#!/usr/bin/env python3
"""KPC map-format converter.

Turns official non-ArcGIS-REST map sources (WFS, OGC API Features, shapefile /
GeoPackage / GeoJSON / KML / KMZ / GML downloads, CKAN / Socrata / ArcGIS Hub
dataset pages) into small GeoJSON files of the records near each park pin, plus
a report.csv.  It decides nothing about matching.

Usage:
  python kpc_convert_layers.py --leads leads.json [--refs DE-0001,GB-0001] [--resume]
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import html
import io
import json
import os
import re
import sys
import tempfile
import time
import traceback
import urllib.robotparser
import zipfile
import importlib.util
from urllib.parse import parse_qsl, urlencode, urljoin, urlparse, urlunparse

import requests

try:  # heavy geo deps
    import pyogrio
    from pyogrio import raw as ogr_raw
    import shapely
    from shapely.geometry import box, mapping, Point
    import numpy as np
    from pyproj import CRS, Transformer
except ImportError as e:  # pragma: no cover
    sys.exit(f"missing dependency: {e}. pip install -r requirements.txt")

VERSION = "1.0"
CONTACT = os.environ.get("KPC_CONTACT", "see https://github.com/ (KPC club repo)")
USER_AGENT = f"KPC-MapFormatConverter/{VERSION} (KPC parks club official-map research; one request at a time; contact: {CONTACT})"

MAX_BYTES = int(float(os.environ.get("KPC_MAX_MB", "500")) * 1024 * 1024)
NEAR_M = 2000.0
BBOX_STEPS_KM = (5.0, 25.0)
SIMPLIFY_M = 3.0
MIN_DELAY_S = float(os.environ.get("KPC_MIN_DELAY", "1.0"))
MAX_FEATURES_PER_QUERY = 2000

REPORT_FIELDS = ["ref", "url", "kind", "n_records_near", "name_field", "licence",
                 "status", "why", "area", "text_fields", "output_file", "pin_lat",
                 "pin_lon", "nearest_m", "searched_km", "layers", "hosts_used", "read_date"]

# ---------------------------------------------------------------- host rules
BANNED_HOST_PATTERNS = [
    r"(^|\.)openstreetmap\.(org|fr|de|com)$", r"(^|\.)osm\.org$", r"(^|\.)openstreetmap\.",
    r"(^|\.)geofabrik\.de$", r"(^|\.)overpass-api\.de$", r"(^|\.)overpass\.",
    r"(^|\.)google\.[a-z.]+$", r"(^|\.)googleapis\.com$", r"(^|\.)googleusercontent\.com$",
    r"(^|\.)gstatic\.com$", r"(^|\.)goo\.gl$", r"(^|\.)g\.co$",
    r"(^|\.)protectedplanet\.net$", r"(^|\.)unep-wcmc\.org$", r"(^|\.)wdpa\.", r"wdpa",
]
BANNED_PATH_PATTERNS = [r"wdpa", r"protected[-_]?planet", r"openstreetmap", r"/osm[-_/.]"]

SECOND_LEVEL = {"gov", "gob", "co", "com", "org", "ac", "gv", "govt", "nic", "net", "edu", "gouv", "go", "or"}


def host_of(url: str) -> str:
    return (urlparse(url).hostname or "").lower()


# Oct 31 (RULINGS 5:34 PM): a GOVERNMENT's own file on cloud storage (Montreal's open data on storage.googleapis.com) is allowed
# when the lead came from the government's own page / portal (the lead names its agency). Google Maps / My Maps / tiles stay refused.
CLOUD_STORAGE = re.compile(r"^(storage\.googleapis\.com|[a-z0-9.-]+\.storage\.googleapis\.com|[a-z0-9.-]*s3[a-z0-9.-]*\.amazonaws\.com|[a-z0-9-]+\.blob\.core\.windows\.net)$")
ALLOW_CLOUD = {"on": False}


def banned(url: str) -> str | None:
    h = host_of(url)
    if ALLOW_CLOUD["on"] and CLOUD_STORAGE.match(h):
        return None
    for p in BANNED_HOST_PATTERNS:
        if re.search(p, h):
            return f"refused host {h} (OSM / Google / Protected Planet / WDPA are never used)"
    path = urlparse(url).path.lower() + "?" + urlparse(url).query.lower()
    for p in BANNED_PATH_PATTERNS:
        if re.search(p, path):
            return f"refused URL {url[:80]} (looks like a WDPA / Protected Planet / OSM download)"
    return None


def reg_domain(host: str) -> str:
    parts = host.split(".")
    if len(parts) >= 3 and (parts[-2] in SECOND_LEVEL or len(parts[-2]) <= 2):
        return ".".join(parts[-3:])
    return ".".join(parts[-2:])


def _load_host_rules():
    """Nov 10: the club's ONE pre-request host check (.github/scripts/kpc_host_rules.py). No fallback: without it nothing is fetched."""
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "kpc_host_rules.py")
    spec = importlib.util.spec_from_file_location("kpc_host_rules", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


HR = _load_host_rules()
MAX_HOPS = 5
STOP_ROBOTS = ["User-agent: *", "Disallow: /"]


def refusal(url: str, hop_from: str | None = None) -> str | None:
    """Why this address may get no request of any kind (robots.txt included), or None. Asked before every request and every hop."""
    ok, why = HR.host_ok(url)
    if not ok:
        return "host rule: " + why
    if hop_from and urlparse(hop_from).scheme.lower() == "https" and urlparse(url).scheme.lower() != "https":
        return f"redirect from https to a plain address ({url[:80]})"
    return banned(url)


# ---------------------------------------------------------------- polite HTTP
class PoliteSession:
    """One request at a time (the tool is single-threaded), per-host minimum
    delay, back-off on 429/5xx, robots.txt respected, club User-Agent."""

    def __init__(self):
        self.s = requests.Session()
        self.s.headers["User-Agent"] = USER_AGENT
        self.last = {}
        self.robots = {}

    def allowed_by_robots(self, url: str) -> bool:
        if refusal(url):   # Nov 10: the host rules first; a refused host's robots.txt is never asked for
            return False
        p = urlparse(url)
        root = f"{p.scheme}://{p.netloc}"
        if root not in self.robots:
            rp = urllib.robotparser.RobotFileParser()
            try:
                r = self._follow(root + "/robots.txt", timeout=20)
                if r.status_code == 200 and "text/html" not in r.headers.get("content-type", ""):
                    rp.parse(r.text.splitlines())
                elif r.status_code in (200, 404, 410):
                    rp.parse([])  # no robots file (or an HTML page) = no rules
                else:
                    rp.parse(STOP_ROBOTS)  # Nov 10: 401 / 403 / other 4xx / 5xx = disallow (fail closed)
            except (requests.RequestException, Refused):
                rp.parse(STOP_ROBOTS)  # no answer, or a refused redirect = disallow
            self.robots[root] = rp
        return self.robots[root].can_fetch(USER_AGENT, url)

    def _follow(self, url, *, params=None, stream=False, timeout=90, headers=None, robots=False):
        """One GET, redirects followed one hop at a time: each hop is checked (host rules, https downgrade, banned list and,
        for data, that host's robots.txt) BEFORE it is requested."""
        self._wait(urlparse(url).netloc)
        r = self.s.get(url, params=params, stream=stream, timeout=timeout, headers=headers or {}, allow_redirects=False)
        for _ in range(MAX_HOPS):
            if not r.is_redirect:
                return r
            nxt = urljoin(r.url, r.headers.get("location", ""))
            r.close()
            why = refusal(nxt, hop_from=r.url)
            if not why and robots and not self.allowed_by_robots(nxt):
                why = f"robots.txt on {host_of(nxt)} disallows {urlparse(nxt).path}"
            if why:
                raise Refused("redirect not followed: " + why)
            self._wait(urlparse(nxt).netloc)
            r = self.s.get(nxt, stream=stream, timeout=timeout, headers=headers or {}, allow_redirects=False)
        r.close()
        raise Refused(f"more than {MAX_HOPS} redirects from {url[:80]}")

    def _wait(self, netloc):
        t = self.last.get(netloc, 0) + MIN_DELAY_S - time.time()
        if t > 0:
            time.sleep(t)
        self.last[netloc] = time.time()

    def get(self, url, *, params=None, stream=False, timeout=90, headers=None, tries=4, check_robots=True):
        b = refusal(url)
        if b:
            raise Refused(b)
        if check_robots and not self.allowed_by_robots(url):
            raise Refused(f"robots.txt on {host_of(url)} disallows {urlparse(url).path}")
        delay = 3.0
        for i in range(tries):
            try:
                r = self._follow(url, params=params, stream=stream, timeout=timeout, headers=headers, robots=check_robots)
            except requests.RequestException as e:
                if i == tries - 1:
                    raise
                time.sleep(delay); delay *= 2
                continue
            if b2 := banned(r.url):
                r.close()
                raise Refused("redirected to " + b2)
            if r.status_code in (429, 500, 502, 503, 504) and i < tries - 1:
                ra = r.headers.get("Retry-After")
                wait = float(ra) if ra and ra.isdigit() else delay
                r.close()
                time.sleep(min(wait, 120)); delay *= 2
                continue
            return r
        return r


class Refused(Exception):
    pass


class TooBig(Exception):
    pass


class LeadError(Exception):
    pass


# ---------------------------------------------------------------- geometry helpers
def shp_transform(func, g):
    """Apply a pyproj-style (x, y) -> (x, y) function to a shapely geometry."""
    def f(c):
        x, y = func(c[:, 0], c[:, 1])
        return np.column_stack([x, y])
    return shapely.transform(g, f)


def local_crs(lat, lon):
    return CRS.from_proj4(f"+proj=aeqd +lat_0={lat} +lon_0={lon} +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs")


def bbox_ll(lat, lon, km):
    """lon/lat bbox (minx,miny,maxx,maxy) of a square of half-side km around the pin."""
    t = Transformer.from_crs(local_crs(lat, lon), 4326, always_xy=True)
    m = km * 1000
    sq = shapely.segmentize(box(-m, -m, m, m), m / 8)
    return shp_transform(t.transform, sq).bounds


def bbox_in(crs, lat, lon, km):
    """Bounds of the pin square in an arbitrary CRS (x/y = traditional GIS order)."""
    t = Transformer.from_crs(local_crs(lat, lon), crs, always_xy=True)
    m = km * 1000
    sq = shapely.segmentize(box(-m, -m, m, m), m / 8)
    return shp_transform(t.transform, sq).bounds


def crs_axis_is_yx(crs: CRS) -> bool:
    try:
        ai = crs.axis_info
        return len(ai) >= 2 and ai[0].direction.lower() in ("north", "south")
    except Exception:
        return False


def to_crs(value) -> CRS | None:
    if value in (None, ""):
        return None
    try:
        return CRS.from_user_input(value)
    except Exception:
        m = re.search(r"EPSG[:/]+(?:[0-9.]*:)?(\d{4,6})", str(value), re.I)
        if m:
            try:
                return CRS.from_epsg(int(m.group(1)))
            except Exception:
                return None
    return None


KEEP_TYPES = ("Polygon", "MultiPolygon", "LineString", "MultiLineString", "LinearRing")


def keep_parts(g):
    if g is None or g.is_empty:
        return None
    if g.geom_type in KEEP_TYPES:
        return g
    if g.geom_type == "GeometryCollection":
        parts = [p for p in (keep_parts(x) for x in g.geoms) if p is not None]
        if not parts:
            return None
        polys = [p for p in parts if "Polygon" in p.geom_type]
        if polys:
            return shapely.union_all(polys)
        return shapely.union_all(parts)
    return None  # points etc.


# ---------------------------------------------------------------- name / id fields
NAME_CANDIDATES = ["NAME", "NAAM", "NOM", "NOMBRE", "NOME", "SITE_NAME", "SITENAME", "NAME_E", "NAME_EN",
                   "NAME_ENG", "ENGLISH_NAME", "BEZEICHNUNG", "BEZEICH", "DENOMINAZIONE", "DENOMINACION",
                   "NAZWA", "NAZEV", "NIMI", "NIMI_SUOMI", "NAMN", "NAVN", "NEV", "NUME", "IME", "NAZOV",
                   "UNIT_NAME", "PARK_NAME", "PARKNAME", "AREA_NAME", "SITE_NAME_", "LABEL", "TITLE",
                   "TEXT", "DESIG_NAME", "NAMEN", "NOM_SITE", "NOMBRE_ANP", "NOMBRE_DEL", "NAZIV", "PAVADINIMAS",
                   "SUOJELUALUEEN_NIMI", "UNITNAME", "FRED_NAVN", "NAVN_", "OMR_NAVN", "STEDNAVN", "NAMEOFSITE", "SITENAME_", "NAME1", "NAME_1", "TEXTSTRING"]
ID_CANDIDATES = ["SITECODE", "SITE_CODE", "SITEID", "SITE_ID", "ID", "IDENTIFIER", "INSPIREID", "LOCALID",
                 "CODE", "CODIGO", "CODE_SITE", "OBJECTID", "FID", "GML_ID", "GLOBALID", "UNITCODE", "REF",
                 "KENNUNG", "CDDA_ID", "NUMMER", "NR", "ID_ANP", "PERMANENTID"]


NULLISH = {"", "null", "none", "nan", "nat", "<null>", "n/a"}


def is_nullish(v):
    return v is None or (isinstance(v, str) and v.strip().lower() in NULLISH)


def expand_description(props):
    """ArcGIS/Esri KML exports hide attributes in an HTML table in 'description'."""
    d = props.get("description")
    if isinstance(d, str) and "<td" in d.lower():
        cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", d, re.I | re.S)
        rows = re.findall(r"<tr[^>]*>(.*?)</tr>", d, re.I | re.S)
        for row in rows:
            c = [clean_text(x) for x in re.findall(r"<td[^>]*>(.*?)</td>", row, re.I | re.S)]
            if len(c) == 2 and c[0] and c[0] not in props and len(c[0]) < 40:
                props[c[0]] = None if is_nullish(c[1]) else c[1]
        props["description"] = None
    return props


def pick_field(fields, candidates, given=None):
    up = {f.upper(): f for f in fields}
    if given:
        if given in fields:
            return given
        if given.upper() in up:
            return up[given.upper()]
    for c in candidates:
        if c in up:
            return up[c]
    return None


def guess_name_field(text_fields, field_values):
    useful = [t for t in text_fields if any(not is_nullish(v) for v in field_values.get(t, []))]
    f = pick_field(useful, NAME_CANDIDATES)
    if f:
        return f
    text_fields = useful
    scored = []
    for t in text_fields:
        u = t.upper()
        score = 0
        if any(k in u for k in ("NAME", "NAAM", "NOM", "BEZEICH", "DENOMIN", "NIMI", "NAMN", "NAVN", "NAZ", "TITLE")):
            score += 5
        vals = [v for v in field_values.get(t, []) if isinstance(v, str) and not is_nullish(v)]
        if not vals:
            continue
        if len(vals) >= 3 and len(set(vals)) == 1:
            score -= 3  # same value on every record: a theme/agency label, not a site name
        elif len(set(vals)) > 1:
            score += 1
        if vals:
            avg = sum(len(v) for v in vals) / len(vals)
            alpha = sum(any(ch.isalpha() for ch in v) for v in vals) / len(vals)
            if 4 <= avg <= 80 and alpha > 0.9:
                score += 2
            if u.endswith("ID") or "CODE" in u or "DATE" in u or "URL" in u or "HTTP" in str(vals[:1]):
                score -= 3
        scored.append((score, t))
    scored.sort(reverse=True)
    return scored[0][1] if scored and scored[0][0] > 2 else None


# ---------------------------------------------------------------- reading OGR sources
def ogr_layers(path):
    try:
        return [l[0] for l in pyogrio.list_layers(path)]
    except Exception as e:
        raise LeadError(f"GDAL cannot open the file: {str(e)[:160]}")


def read_layer_near(path, layer, lat, lon, km, assume_crs=None):
    """Read features of one OGR layer inside the pin square; return list of
    (geom4326, props, fid) plus field list."""
    info = pyogrio.read_info(path, layer=layer)
    lcrs = to_crs(info.get("crs")) or to_crs(assume_crs) or CRS.from_epsg(4326)
    bb = bbox_in(lcrs, lat, lon, km)
    meta, fids, geoms, fdata = ogr_raw.read(path, layer=layer, bbox=bb, return_fids=True, force_2d=True)
    if (geoms is None or len(geoms) == 0) and meta.get("crs") is None and assume_crs is None:
        pass
    names = list(meta["fields"])
    t = Transformer.from_crs(lcrs, 4326, always_xy=True)
    out = []
    for i in range(len(fids)):
        wkb = geoms[i] if geoms is not None else None
        if wkb is None:
            continue
        try:
            g = shapely.from_wkb(wkb)
        except Exception:
            continue
        props = {}
        for n, col in zip(names, fdata):
            v = col[i]
            if hasattr(v, "item"):
                try:
                    v = v.item()
                except Exception:
                    v = str(v)
            if isinstance(v, bytes):
                v = v.decode("utf8", "ignore")
            if v is not None and not isinstance(v, (str, int, float, bool)):
                v = str(v)
            if isinstance(v, float) and v != v:
                v = None
            props[n] = v
        if not lcrs.equals(CRS.from_epsg(4326)):
            g = shp_transform(t.transform, g)
        out.append((g, props, int(fids[i])))
    dtypes = dict(zip(meta["fields"], [str(d) for d in meta["dtypes"]]))
    return out, names, dtypes


def fix_axis(records, lat, lon):
    """If coordinates look lat/lon-swapped relative to the pin, swap them."""
    if not records:
        return records
    c = shapely.union_all([r[0].envelope for r in records[:200]]).centroid
    d_ok = abs(c.x - lon) + abs(c.y - lat)
    d_sw = abs(c.y - lon) + abs(c.x - lat)
    if d_sw < d_ok and d_sw < 2:
        return [(shapely.transform(g, lambda c: c[:, ::-1]), p, f) for g, p, f in records]
    return records


# ---------------------------------------------------------------- converter
class Converter:
    def __init__(self, args):
        self.args = args
        self.http = PoliteSession()
        self.out = args.out
        self.cache = os.path.abspath(args.cache)
        os.makedirs(self.out, exist_ok=True)
        os.makedirs(self.cache, exist_ok=True)
        self.pins_path = os.path.join(self.cache, "pins.json")
        self.pins = json.load(open(self.pins_path)) if os.path.exists(self.pins_path) else {}

    # ---------- pins
    def pin(self, lead):
        for a, b in (("lat", "lon"), ("latitude", "longitude"), ("pin_lat", "pin_lon")):
            if lead.get(a) is not None and lead.get(b) is not None:
                return float(lead[a]), float(lead[b])
        ref = lead["ref"]
        if ref in self.pins:
            return tuple(self.pins[ref])
        if self.args.no_pota:
            raise LeadError("no pin: lead has no lat/lon and --no-pota is set")
        r = self.http.get(f"https://api.pota.app/park/{ref}", timeout=30)
        try:
            j = r.json()
        except Exception:
            j = None
        if not j or j.get("latitude") is None:
            raise LeadError(f"no pin: POTA has no coordinates for {ref}")
        self.pins[ref] = [float(j["latitude"]), float(j["longitude"])]
        json.dump(self.pins, open(self.pins_path, "w"))
        return tuple(self.pins[ref])

    # ---------- kind detection
    def detect(self, url):
        u = url.lower()
        p = urlparse(u)
        q = dict((k.lower(), v.lower()) for k, v in parse_qsl(p.query))
        if q.get("service") == "wfs" or re.search(r"/wfs(server)?/?($|\?)|wfsserver|/ows/?$|/wfs/", u) or p.path.endswith("/wfs"):
            return "wfs"
        if re.search(r"/collections(/|$)|/ogc/features|/ogcapi|/features/v1", p.path) or q.get("f") in ("application/geo+json",) and "/items" in p.path:
            return "ogcapi"
        if "opendata.arcgis.com" in p.netloc or "hub.arcgis.com" in p.netloc and "/datasets/" in p.path or re.search(r"/datasets/[^/]+::", p.path):
            if "/api/download/" not in p.path:
                return "hub"
        ext = os.path.splitext(p.path)[1]
        if ext in (".zip", ".gpkg", ".geojson", ".kml", ".kmz", ".gml", ".shp", ".fgb", ".sqlite"):
            return "file"
        if ("/d/" in p.path or "/dataset/" in p.path) and re.search(r"/([a-z0-9]{4}-[a-z0-9]{4})(/|$)", p.path):
            return "socrata"
        if re.search(r"/resource/[a-z0-9]{4}-[a-z0-9]{4}(\.[a-z]+)?$", p.path):   # Oct 31: Socrata API URL (Calgary, Winnipeg)
            return "socrata"
        if "/dataset/" in p.path and "/resource/" not in p.path:
            return "ckan"
        if ext in (".json", ".xml"):
            return "file"
        return "unknown"

    # ---------- main per-lead
    def run_lead(self, lead):
        url = lead["url"].strip()
        rec = {k: "" for k in REPORT_FIELDS}
        rec.update(ref=lead["ref"], url=url, area=lead.get("area", ""), read_date=dt.date.today().isoformat())
        self.hosts_used = set()
        ALLOW_CLOUD["on"] = bool(str(lead.get("agency") or "").strip())   # the lead came from a named government page / portal
        try:
            if b := banned(url):
                rec.update(kind=self.detect(url), status="ERROR", why=b, n_records_near=0)
                return rec
            lat, lon = self.pin(lead)
            rec.update(pin_lat=lat, pin_lon=lon)
            kind = lead.get("kind") or self.detect(url)
            if kind == "unknown":
                kind = self.sniff(url)
            rec["kind"] = kind
            fn = {"wfs": self.do_wfs, "ogcapi": self.do_ogcapi, "hub": self.do_hub, "ckan": self.do_ckan,
                  "socrata": self.do_socrata, "file": self.do_file, "html": self.do_html,
                  "arcgis": self.do_arcgis}.get(kind)
            if not fn:
                raise LeadError(f"could not tell what kind of source this is ({kind})")
            res = fn(url, lat, lon, lead)
            self.finish(rec, lead, res, lat, lon)
        except Refused as e:
            rec.update(status="ERROR", why=str(e), n_records_near=0)
        except TooBig as e:
            rec.update(status="TOO BIG", why=str(e), n_records_near=0)
        except LeadError as e:
            rec.update(status="ERROR", why=str(e), n_records_near=0)
        except requests.RequestException as e:
            rec.update(status="ERROR", why=f"network: {type(e).__name__}: {str(e)[:160]}", n_records_near=0)
        except Exception as e:  # never stop the batch
            rec.update(status="ERROR", why=f"bug/unexpected: {type(e).__name__}: {str(e)[:160]}", n_records_near=0)
            if self.args.verbose:
                traceback.print_exc()
        rec["hosts_used"] = " ".join(sorted(self.hosts_used))
        return rec

    def sniff(self, url):
        r = self.http.get(url, stream=True, timeout=60)
        self.hosts_used.add(host_of(r.url))
        head = next(r.iter_content(4096), b"")
        ct = r.headers.get("content-type", "").lower()
        cd = r.headers.get("content-disposition", "").lower()
        r.close()
        if b"WFS_Capabilities" in head:
            return "wfs"
        if head.startswith(b"PK") or head.startswith(b"SQLite format 3") or b"<kml" in head or head.lstrip().startswith(b"{") \
                or any(x in cd for x in (".zip", ".kml", ".kmz", ".gpkg", ".geojson")) or "zip" in ct or "kml" in ct:
            return "file"
        if "html" in ct:
            return "html"
        return "file"

    # ---------- result assembly
    def finish(self, rec, lead, res, lat, lon):
        records = res["records"]  # list of (geom4326, props, fid, layer)
        licence = res.get("licence") or lead.get("licence") or ""
        licence = clean_text(licence)
        rec["licence"] = licence[:600] if licence else "no licence found"
        rec["layers"] = "; ".join(res.get("layers", []))[:400]
        rec["searched_km"] = res.get("searched_km", "")
        if res.get("kind_detail"):
            rec["kind"] = f"{rec['kind']}:{res['kind_detail']}"
        notes = list(res.get("notes", []))
        # keep polygons + lines
        kept, dropped = [], 0
        for g, p, fid, lay in records:
            g2 = keep_parts(g)
            if g2 is None:
                dropped += 1
                continue
            if not g2.is_valid:
                g2 = shapely.make_valid(g2)
                g2 = keep_parts(g2) or g2
            kept.append((g2, p, fid, lay))
        if dropped:
            notes.append(f"{dropped} point/empty records ignored")
        kept = [(g, expand_description(p), fid, lay) for g, p, fid, lay in kept]
        # text fields
        text_fields, values = [], {}
        for _, p, _, _ in kept:
            for k, v in p.items():
                if isinstance(v, str):
                    if k not in values:
                        values[k] = []
                        text_fields.append(k)
                    if len(values[k]) < 50:
                        values[k].append(v)
        rec["text_fields"] = "|".join(text_fields)
        name_field = None
        if kept:
            allf = list(dict.fromkeys(k for _, p, _, _ in kept for k in p))
            name_field = pick_field(allf, [], lead.get("name_field")) if lead.get("name_field") else None
            if lead.get("name_field") and not name_field:
                notes.append(f"given name_field {lead['name_field']} not in data")
            name_field = name_field or guess_name_field(text_fields, values)
            filled = [k for k in allf if any(not is_nullish(p.get(k)) for _, p, _, _ in kept)]
            id_field = pick_field(filled, ID_CANDIDATES)
        rec["name_field"] = name_field or ("" if not kept else "none found")
        # distance filter in local metric CRS
        lc = local_crs(lat, lon)
        to_m = Transformer.from_crs(4326, lc, always_xy=True).transform
        to_ll = Transformer.from_crs(lc, 4326, always_xy=True).transform
        pin = Point(0, 0)
        near, nearest = [], None
        for g, p, fid, lay in kept:
            gm = shp_transform(to_m, g)
            d = gm.distance(pin)
            nearest = d if nearest is None else min(nearest, d)
            if d <= NEAR_M:
                near.append((gm, p, fid, lay, d))
        rec["nearest_m"] = "" if nearest is None else round(nearest)
        rec["n_records_near"] = len(near)
        if not near:
            rec["status"] = "EMPTY"
            if kept:
                notes.insert(0, f"{len(kept)} polygon/line records found within {res.get('searched_km')} km, none within 2 km of the pin (nearest {round(nearest)} m)")
            else:
                notes.insert(0, f"no polygon/line records within {res.get('searched_km')} km of the pin")
            rec["why"] = "; ".join(notes)
            return
        feats = []
        for gm, p, fid, lay, d in sorted(near, key=lambda x: x[4]):
            gs = gm.simplify(SIMPLIFY_M, preserve_topology=True)
            gll = shp_transform(to_ll, gs)
            gll = shapely.set_precision(gll, 1e-7) if not gll.is_empty else gll
            nm = p.get(name_field) if name_field else None
            nm = None if is_nullish(nm) else nm
            rid = p.get(id_field) if id_field else None
            feats.append({"type": "Feature", "geometry": mapping(gll), "properties": {
                "name": nm, "record_id": rid if rid not in (None, "") else f"{lay}#{fid}",
                "source_url": rec["url"], "licence": rec["licence"], "read_date": rec["read_date"],
                "layer": lay, "distance_m": round(d), "ref": rec["ref"]}})
        area = re.sub(r"[^A-Za-z0-9_.-]+", "_", rec["area"] or "unknown")
        h = hashlib.sha1(rec["url"].encode()).hexdigest()[:10]
        os.makedirs(os.path.join(self.out, area), exist_ok=True)
        fp = os.path.join(self.out, area, f"{rec['ref']}__{h}.geojson")
        with open(fp + ".tmp", "w") as f:
            json.dump({"type": "FeatureCollection", "name": f"{rec['ref']} {rec['url']}", "features": feats}, f, ensure_ascii=False)
        os.replace(fp + ".tmp", fp)
        rec["output_file"] = os.path.relpath(fp, self.out)
        rec["status"] = "OK"
        names = sorted({str(x["properties"]["name"]) for x in feats if x["properties"]["name"]})[:6]
        notes.insert(0, f"{len(near)} record(s) within 2 km" + (": " + ", ".join(names) if names else ""))
        rec["why"] = "; ".join(notes)[:800]

    # ---------- WFS
    def do_wfs(self, url, lat, lon, lead):
        p = urlparse(url)
        q = parse_qsl(p.query, keep_blank_values=True)
        drop = {"service", "request", "version", "acceptversions", "typename", "typenames", "outputformat",
                "bbox", "count", "maxfeatures", "srsname", "startindex"}
        want_types = [v for k, v in q if k.lower() in ("typename", "typenames")]
        want_types = [t for v in want_types for t in v.split(",") if t]
        if lead.get("layer"):
            want_types = [lead["layer"]]
        base_q = [(k, v) for k, v in q if k.lower() not in drop]
        base = urlunparse(p._replace(query=urlencode(base_q)))
        caps, ver = None, None
        for v in ("2.0.0", "1.1.0", "1.0.0"):
            r = self.http.get(base, params={"service": "WFS", "request": "GetCapabilities", "version": v}, timeout=90)
            self.hosts_used.add(host_of(r.url))
            if r.ok and b"Capabilities" in r.content[:5000] and b"ExceptionReport" not in r.content[:600]:
                caps, ver = r.content, v
                break
        if caps is None:
            raise LeadError(f"WFS GetCapabilities failed (HTTP {r.status_code})")
        meta = parse_wfs_caps(caps, base, ver)
        ver = meta["version"] or ver
        types = meta["types"]
        if not types:
            raise LeadError("WFS has no feature types")
        if want_types:
            sel = [t for t in types if t["name"] in want_types or t["name"].split(":")[-1] in [w.split(":")[-1] for w in want_types]]
            if not sel:
                raise LeadError(f"feature type(s) {want_types} not in capabilities")
        else:
            sel = types[: self.args.max_types]
        notes = []
        if not want_types and len(types) > self.args.max_types:
            notes.append(f"only first {self.args.max_types} of {len(types)} feature types queried")
        fmt = pick_json_format(meta["formats"])
        records, used_km, layers = [], None, []
        for km in BBOX_STEPS_KM:
            records, layers, errs = [], [], []
            for t in sel:
                try:
                    recs = self.wfs_getfeature(base, ver, t, fmt, lat, lon, km)
                except LeadError as e:
                    errs.append(f"{t['name']}: {e}")
                    continue
                if len(recs) >= MAX_FEATURES_PER_QUERY:
                    notes.append(f"{t['name']}: hit {MAX_FEATURES_PER_QUERY}-feature cap")
                records += [(g, pr, fid, t["name"]) for g, pr, fid in recs]
                layers.append(f"{t['name']}({len(recs)})")
            used_km = km
            if errs and not layers:
                raise LeadError("GetFeature failed: " + " | ".join(errs)[:300])
            if errs:
                notes += errs[:3]
            if records:
                break
        return dict(records=records, licence=meta["licence"], layers=layers, searched_km=used_km,
                    notes=notes, kind_detail=f"WFS {ver}")

    def wfs_getfeature(self, base, ver, t, fmt, lat, lon, km):
        crs = to_crs(t.get("crs")) or CRS.from_epsg(4326)
        epsg = crs.to_epsg() or 4326
        minx, miny, maxx, maxy = bbox_in(crs, lat, lon, km)
        if ver.startswith("1.0"):
            bbox = f"{minx},{miny},{maxx},{maxy}"
            srs = f"EPSG:{epsg}"
            params = {"service": "WFS", "version": ver, "request": "GetFeature", "typeName": t["name"],
                      "maxFeatures": MAX_FEATURES_PER_QUERY, "bbox": bbox, "srsName": srs}
        else:
            urn = f"urn:ogc:def:crs:EPSG::{epsg}"
            if crs_axis_is_yx(crs):
                bbox = f"{miny},{minx},{maxy},{maxx},{urn}"
            else:
                bbox = f"{minx},{miny},{maxx},{maxy},{urn}"
            params = {"service": "WFS", "version": ver, "request": "GetFeature", "bbox": bbox, "srsName": urn}
            if ver.startswith("2"):
                params.update(typeNames=t["name"], count=MAX_FEATURES_PER_QUERY)
            else:
                params.update(typeName=t["name"], maxFeatures=MAX_FEATURES_PER_QUERY)
        if fmt:
            params["outputFormat"] = fmt
        r = self.http.get(base, params=params, timeout=180)
        if (not r.ok or b"ExceptionReport" in r.content[:800] or b"ServiceException" in r.content[:800]) and fmt:
            params.pop("outputFormat")  # retry with default GML
            r = self.http.get(base, params=params, timeout=180)
        if not r.ok or b"ExceptionReport" in r.content[:800] or b"ServiceException" in r.content[:800]:
            msg = re.sub(r"\s+", " ", re.sub(rb"<[^>]+>", b" ", r.content[:1500]).decode("utf8", "ignore")).strip()
            raise LeadError(f"HTTP {r.status_code} {msg[:160]}")
        if len(r.content) > MAX_BYTES:
            raise TooBig("WFS response over 500 MB")
        is_json = r.content.lstrip()[:1] in (b"{", b"[")
        return read_bytes_near(r.content, ".geojson" if is_json else ".gml", lat, lon, km, assume_crs=crs)

    # ---------- OGC API Features
    def do_ogcapi(self, url, lat, lon, lead):
        p = urlparse(url)
        path = p.path.rstrip("/")
        m = re.search(r"^(.*?)/collections(?:/([^/]+))?(?:/items)?$", path)
        if m:
            root, coll = m.group(1), m.group(2)
        else:
            root, coll = path, None
        rootu = urlunparse(p._replace(path=root, query=""))
        licence = ""
        try:
            lj = self.http.get(rootu, params={"f": "json"}, headers={"Accept": "application/json"}).json()
            licence = links_licence(lj)
        except Exception:
            pass
        r = self.http.get(rootu + "/collections", params={"f": "json"}, headers={"Accept": "application/json"})
        self.hosts_used.add(host_of(r.url))
        try:
            cj = r.json()
        except Exception:
            raise LeadError(f"/collections did not return JSON (HTTP {r.status_code})")
        colls = cj.get("collections", [])
        if coll:
            colls = [c for c in colls if c.get("id") == coll] or [{"id": coll}]
        if lead.get("layer"):
            colls = [c for c in colls if c.get("id") == lead["layer"]] or [{"id": lead["layer"]}]
        notes = []
        if len(colls) > self.args.max_types:
            notes.append(f"only first {self.args.max_types} of {len(colls)} collections queried")
            colls = colls[: self.args.max_types]
        licence = licence or " ".join(filter(None, (links_licence(c) for c in colls)))
        for km in BBOX_STEPS_KM:
            records, layers = [], []
            minx, miny, maxx, maxy = bbox_ll(lat, lon, km)
            for c in colls:
                cid = c["id"]
                rr = self.http.get(f"{rootu}/collections/{cid}/items",
                                   params={"bbox": f"{minx},{miny},{maxx},{maxy}", "limit": 1000, "f": "json"},
                                   headers={"Accept": "application/geo+json, application/json"}, timeout=180)
                if not rr.ok:
                    notes.append(f"{cid}: HTTP {rr.status_code}")
                    continue
                recs = read_bytes_near(rr.content, ".geojson", lat, lon, km)
                records += [(g, pr, fid, cid) for g, pr, fid in recs]
                layers.append(f"{cid}({len(recs)})")
            if records:
                break
        return dict(records=records, licence=licence, layers=layers, searched_km=km, notes=notes)

    # ---------- ArcGIS REST layer (only reached via Hub/CKAN pages)
    def do_arcgis(self, url, lat, lon, lead, licence=""):
        u = url.split("?")[0].rstrip("/")
        layers_urls = []
        if re.search(r"/(FeatureServer|MapServer)/\d+$", u):
            layers_urls = [u]
        else:
            j = self.http.get(u, params={"f": "json"}).json()
            layers_urls = [f"{u}/{l['id']}" for l in j.get("layers", []) if l.get("type", "Feature Layer") == "Feature Layer"][: self.args.max_types]
            if not layers_urls:
                raise LeadError("ArcGIS service lists no feature layers")
        for km in BBOX_STEPS_KM:
            minx, miny, maxx, maxy = bbox_ll(lat, lon, km)
            records, layers = [], []
            for lu in layers_urls:
                r = self.http.get(lu + "/query", params={
                    "geometry": f"{minx},{miny},{maxx},{maxy}", "geometryType": "esriGeometryEnvelope", "inSR": 4326,
                    "spatialRel": "esriSpatialRelIntersects", "outFields": "*", "outSR": 4326, "f": "geojson",
                    "resultRecordCount": MAX_FEATURES_PER_QUERY}, timeout=180)
                self.hosts_used.add(host_of(r.url))
                if not r.ok or b'"error"' in r.content[:200]:
                    raise LeadError(f"ArcGIS query failed: {r.text[:160]}")
                recs = read_bytes_near(r.content, ".geojson", lat, lon, km)
                records += [(g, pr, fid, lu.rsplit('/', 2)[-2] + "/" + lu.rsplit('/', 1)[-1]) for g, pr, fid in recs]
                layers.append(f"{lu.rsplit('/', 3)[-3]}/{lu.rsplit('/', 1)[-1]}({len(recs)})")
            if records:
                break
        return dict(records=records, licence=licence, layers=layers, searched_km=km, kind_detail="ArcGIS REST")

    # ---------- ArcGIS Hub dataset page
    def do_hub(self, url, lat, lon, lead):
        p = urlparse(url)
        m = re.search(r"/datasets/([^/?#]+)", p.path)
        if not m:
            raise LeadError("Hub URL has no /datasets/<id or slug>")
        key = m.group(1)
        site = f"{p.scheme}://{p.netloc}"
        r = self.http.get(url, timeout=60)  # the page itself (licence fallback / proof it exists)
        page = r.text if r.ok else ""
        attrs = None
        if re.fullmatch(r"[0-9a-f]{32}(_\d+)?", key):
            j = self.http.get(f"{site}/api/v3/datasets/{key}").json()
            attrs = (j.get("data") or {}).get("attributes")
        else:
            j = self.http.get(f"{site}/api/v3/datasets", params={"filter[slug]": key}).json()
            d = j.get("data") or []
            attrs = d[0]["attributes"] if d else None
        if not attrs:
            raise LeadError("Hub API did not resolve the dataset")
        svc = attrs.get("url")
        lic = attrs.get("licenseInfo") or (attrs.get("structuredLicense") or {}).get("text") or ""
        if not svc:
            raise LeadError("Hub dataset has no service URL (file-only item?)")
        if b := banned(svc):
            raise Refused(b)
        res = self.do_arcgis(svc, lat, lon, lead, licence=lic)
        res["kind_detail"] = "Hub->ArcGIS REST " + host_of(svc)
        res.setdefault("notes", []).append(f"Hub '{attrs.get('name')}' by {attrs.get('orgName') or attrs.get('owner')}")
        return res

    # ---------- CKAN dataset page
    def do_ckan(self, url, lat, lon, lead):
        p = urlparse(url)
        m = re.search(r"^(.*?)/dataset/([^/?#]+)", p.path)
        if not m:
            raise LeadError("not a CKAN /dataset/ URL")
        prefix, slug = m.group(1), m.group(2)
        api = f"{p.scheme}://{p.netloc}{prefix}/api/3/action/package_show"
        self.hosts_used.add(p.netloc)
        pkg, api_note = None, ""
        if self.http.allowed_by_robots(api + "?id=" + slug):
            r = self.http.get(api, params={"id": slug})
            try:
                pkg = r.json()["result"]
            except Exception:
                api_note = f"CKAN API HTTP {r.status_code}"
        else:
            api_note = "CKAN API disallowed by robots.txt; read the dataset page instead"
        if pkg is None:
            pkg = self.ckan_from_page(url)
            if pkg is None:
                return self.do_html(url, lat, lon, lead)
        lic = " ".join(filter(None, [pkg.get("license_title"), pkg.get("license_url")]))
        for ex in pkg.get("extras", []) or []:
            if re.search(r"licen|rights|access_constraints|use_constraints", ex.get("key", ""), re.I):
                lic += " " + str(ex.get("value", ""))[:300]
        res_list = pkg.get("resources", [])
        cands = []
        for rsc in res_list:
            ru, fmt = rsc.get("url", ""), (rsc.get("format") or "").lower()
            if not ru.startswith("http") or banned(ru):
                continue
            k = classify_resource(ru, fmt)
            if k:
                cands.append((k[0], k[1], ru, rsc.get("name") or fmt))
        cands.sort(key=lambda x: x[0])
        if not cands:
            raise LeadError(f"CKAN dataset has {len(res_list)} resources but none in a readable map format")
        errs = []
        for _, kind, ru, nm in cands[:4]:
            try:
                if kind == "wfs":
                    res = self.do_wfs(ru, lat, lon, lead)
                elif kind == "ogcapi":
                    res = self.do_ogcapi(ru, lat, lon, lead)
                elif kind == "arcgis":
                    res = self.do_arcgis(ru, lat, lon, lead)
                else:
                    res = self.do_file(ru, lat, lon, lead)
                res["licence"] = lic.strip() or res.get("licence", "")
                res["kind_detail"] = f"CKAN->{kind} ({nm[:40]})"
                if api_note:
                    res.setdefault("notes", []).append(api_note)
                if errs:
                    res.setdefault("notes", []).append("earlier resources failed: " + " | ".join(errs)[:200])
                return res
            except (LeadError, requests.RequestException, Refused) as e:
                errs.append(f"{kind}: {str(e)[:100]}")
        raise LeadError("all CKAN map resources failed: " + " | ".join(errs)[:400])

    def ckan_from_page(self, url):
        """Build a minimal CKAN package dict from the dataset HTML page: the
        resource links the official catalog lists, plus its licence link."""
        from bs4 import BeautifulSoup
        r = self.http.get(url, timeout=60)
        if not r.ok:
            return None
        soup = BeautifulSoup(r.text, "html.parser")
        res, lic = [], []
        for a in soup.find_all("a", href=True):
            hu = html.unescape(urljoin(r.url, a["href"]))
            txt = a.get_text(" ", strip=True)
            if re.search(r"creativecommons\.org/licen|opendatacommons|open-government-licen|/licen[cs]e", hu, re.I):
                lic.append(f"{txt} {hu}".strip())
                continue
            if hu.startswith("http") and classify_resource(hu, txt.lower()):
                res.append({"url": hu, "format": txt[:30], "name": txt[:60] or hu.rsplit("/", 1)[-1]})
        m = soup.find(string=re.compile(r"Licen[cs]e", re.I))
        return {"license_title": " ".join(dict.fromkeys(lic)), "resources": res, "extras": []}

    # ---------- Socrata dataset page
    def do_socrata(self, url, lat, lon, lead):
        p = urlparse(url)
        m = re.search(r"/([a-z0-9]{4}-[a-z0-9]{4})(?:/|\.[a-z]+$|$)", p.path)
        vid = m.group(1)
        site = f"{p.scheme}://{p.netloc}"
        r = self.http.get(f"{site}/api/views/{vid}.json")
        if not r.ok:
            if "/dataset/" in p.path:
                return self.do_ckan(url, lat, lon, lead)
            raise LeadError(f"Socrata view metadata HTTP {r.status_code}")
        v = r.json()
        lic = " ".join(filter(None, [(v.get("license") or {}).get("name"), (v.get("license") or {}).get("termsLink"), v.get("attribution")]))
        child = (v.get("metadata") or {}).get("geo", {}).get("owsUrl")
        dl = f"{site}/api/geospatial/{vid}?method=export&format=GeoJSON"
        try:
            res = self.do_file(dl, lat, lon, lead, ext_hint=".geojson")
        except Exception:  # noqa: BLE001  (Oct 31: newer Socrata sites only answer the resource GeoJSON)
            res = self.do_file(f"{site}/resource/{vid}.geojson?$limit=200000", lat, lon, lead, ext_hint=".geojson")
        res["licence"] = lic
        res["kind_detail"] = "Socrata export"
        return res

    # ---------- generic HTML dataset page (find a download link on the same agency host)
    def do_html(self, url, lat, lon, lead):
        from bs4 import BeautifulSoup
        r = self.http.get(url, timeout=60)
        if not r.ok:
            raise LeadError(f"dataset page HTTP {r.status_code}")
        soup = BeautifulSoup(r.text, "html.parser")
        home = reg_domain(host_of(r.url))
        links = []
        for a in soup.find_all("a", href=True):
            hu = urljoin(r.url, a["href"])
            if banned(hu) or reg_domain(host_of(hu)) != home:
                continue
            k = classify_resource(hu, a.get_text(" ", strip=True).lower())
            if k:
                links.append((k[0], k[1], hu))
        lic = ""
        for a in soup.find_all("a", href=True):
            if re.search(r"licen|lizenz|licence|terms|creativecommons|open-government", a["href"] + " " + a.get_text(), re.I):
                lic = f"{a.get_text(' ', strip=True)} {urljoin(r.url, a['href'])}"
                break
        if not links:
            raise LeadError("no map download/API link on the dataset page (same agency host)")
        links.sort(key=lambda x: x[0])
        _, kind, hu = links[0]
        res = {"wfs": self.do_wfs, "ogcapi": self.do_ogcapi, "arcgis": self.do_arcgis}.get(kind, self.do_file)(hu, lat, lon, lead)
        res["licence"] = res.get("licence") or lic
        res["kind_detail"] = f"page->{kind}"
        return res

    # ---------- direct file
    def download(self, url, ext_hint=None):
        key = hashlib.sha1(url.encode()).hexdigest()
        meta_p = os.path.join(self.cache, key + ".json")
        meta = json.load(open(meta_p)) if os.path.exists(meta_p) else None
        hdr = {}
        if meta and os.path.exists(meta["path"]) and not (meta.get("etag") or meta.get("last_modified")):
            age_d = (time.time() - os.path.getmtime(meta["path"])) / 86400
            if age_d < self.args.cache_days:  # server gives no validators: reuse a recent copy
                meta["cached"] = True
                return meta
        if meta and os.path.exists(meta["path"]):
            if meta.get("etag"):
                hdr["If-None-Match"] = meta["etag"]
            if meta.get("last_modified"):
                hdr["If-Modified-Since"] = meta["last_modified"]
        r = self.http.get(url, stream=True, timeout=180, headers=hdr)
        self.hosts_used.add(host_of(r.url))
        if r.status_code == 304 and meta:
            r.close()
            meta["cached"] = True
            return meta
        if not r.ok:
            r.close()
            raise LeadError(f"download HTTP {r.status_code}")
        cl = r.headers.get("content-length")
        if cl and cl.isdigit() and int(cl) > MAX_BYTES:
            r.close()
            raise TooBig(f"file is {int(cl) / 1e6:.0f} MB (limit {MAX_BYTES / 1048576:.0f} MB); not downloaded")
        ct = r.headers.get("content-type", "").lower()
        cd = r.headers.get("content-disposition", "")
        fname = ""
        m = re.search(r"filename\*?=(?:UTF-8'')?\"?([^\";]+)", cd, re.I)
        if m:
            fname = m.group(1)
        ext = os.path.splitext(fname or urlparse(r.url).path)[1].lower() or ext_hint or ""
        tmp = os.path.join(self.cache, key + ".part")
        n = 0
        with open(tmp, "wb") as f:
            for chunk in r.iter_content(1 << 20):
                n += len(chunk)
                if n > MAX_BYTES:
                    r.close(); f.close(); os.remove(tmp)
                    raise TooBig(f"download passed {MAX_BYTES / 1048576:.0f} MB; stopped and skipped")
                f.write(chunk)
        with open(tmp, "rb") as f:
            head = f.read(4096)
        if head.startswith(b"PK"):
            ext = ".kmz" if ext == ".kmz" else ".zip"
        elif head.startswith(b"SQLite format 3"):
            ext = ".gpkg"
        elif b"<kml" in head:
            ext = ".kml"
        elif head.lstrip()[:1] in (b"{", b"["):
            ext = ".geojson"
        elif b"<html" in head.lower() or b"<!doctype html" in head.lower():
            os.remove(tmp)
            raise LeadError("URL returned an HTML page, not a map file")
        elif b"FeatureCollection" in head or b"gml" in head[:2000]:
            ext = ".gml"
        path = os.path.join(self.cache, key + (ext or ".bin"))
        os.replace(tmp, path)
        meta = {"url": url, "final_url": r.url, "path": path, "bytes": n, "etag": r.headers.get("etag"),
                "last_modified": r.headers.get("last-modified"), "content_type": ct, "filename": fname,
                "fetched": dt.datetime.now(dt.timezone.utc).isoformat()}
        json.dump(meta, open(meta_p, "w"))
        return meta

    def do_file(self, url, lat, lon, lead, ext_hint=None):
        meta = self.download(url, ext_hint)
        self.hosts_used.add(host_of(meta.get("final_url") or url))
        path = meta["path"]
        sz = f"{meta['bytes'] / 1e6:.1f} MB" if meta["bytes"] >= 1e5 else f"{meta['bytes'] / 1e3:.0f} KB"
        notes = [sz + (" (from cache)" if meta.get("cached") else "")]
        licence = ""
        targets = []
        if path.endswith(".zip"):
            zf = zipfile.ZipFile(path)
            names = zf.namelist()
            for nm in names:
                low = nm.lower()
                if re.search(r"(licen[cs]e|lizenz|nutzungsbed|terms|readme|leame|lisez|copyright)[^/]*\.(txt|md|html?)$", low) and not licence:
                    licence = zf.read(nm)[:1500].decode("utf8", "ignore")
                if low.endswith((".shp", ".gpkg", ".geojson", ".json", ".kml", ".kmz", ".gml", ".fgb", ".sqlite", ".tab")):
                    targets.append(f"/vsizip/{path}/{nm}")
                elif low.endswith(".zip"):  # one level of nesting
                    inner = zipfile.ZipFile(io.BytesIO(zf.read(nm)))
                    for nm2 in inner.namelist():
                        if nm2.lower().endswith((".shp", ".gpkg", ".geojson", ".kml", ".gml")):
                            targets.append(f"/vsizip/{{/vsizip/{path}/{nm}}}/{nm2}")
            gdbs = sorted({re.match(r"(.*?\.gdb)/", n, re.I).group(1) for n in names if re.match(r".*?\.gdb/", n, re.I)})
            targets += [f"/vsizip/{path}/{g}" for g in gdbs]
            if not targets:
                raise LeadError(f"zip holds no map file ({', '.join(names[:5])})")
        else:
            targets = [path]
        targets = expand_kmz(targets)
        records, layers = [], []
        km = BBOX_STEPS_KM[-1]
        for tgt in targets:
            for lay in ogr_layers(tgt):
                try:
                    recs, _, _ = read_layer_near(tgt, lay, lat, lon, km)
                except Exception as e:
                    notes.append(f"layer {lay}: {str(e)[:80]}")
                    continue
                recs = fix_axis(recs, lat, lon)
                records += [(g, p, fid, lay) for g, p, fid in recs]
                layers.append(f"{lay}({len(recs)})")
        if len(layers) > 12:
            nz = [l for l in layers if not l.endswith("(0)")]
            layers = nz[:12] + [f"+{len(layers) - len(nz[:12])} more layers"]
        return dict(records=records, licence=licence, layers=layers, searched_km=km, notes=notes,
                    kind_detail=os.path.splitext(path)[1].lstrip(".") + ("" if len(targets) != 1 or targets[0] == path else "->" + os.path.splitext(targets[0])[1].lstrip(".")))


# ---------------------------------------------------------------- helpers
def expand_kmz(targets):
    """Open .kmz as a zip and read its .kml members with GDAL (reading the .kmz
    directly through LIBKML loses ExtendedData/SchemaData attributes)."""
    out = []
    for t in targets:
        if not t.lower().endswith(".kmz"):
            out.append(t)
            continue
        try:
            if t.startswith("/vsizip/"):
                outer, inner = re.match(r"/vsizip/(.+?\.zip)/(.+)$", t).groups()
                names = zipfile.ZipFile(io.BytesIO(zipfile.ZipFile(outer).read(inner))).namelist()
                out += [f"/vsizip/{{/vsizip/{outer}/{inner}}}/{n}" for n in names if n.lower().endswith(".kml")]
            else:
                names = zipfile.ZipFile(t).namelist()
                out += [f"/vsizip/{t}/{n}" for n in names if n.lower().endswith(".kml")]
        except Exception:
            out.append(t)
    return out


def read_bytes_near(content, ext, lat, lon, km, assume_crs=None):
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as f:
        f.write(content)
        tp = f.name
    try:
        out = []
        for lay in ogr_layers(tp):
            info = pyogrio.read_info(tp, layer=lay)
            if info.get("features", 0) == 0:
                continue
            # service already filtered by bbox; read all, then reproject
            lcrs = to_crs(info.get("crs")) or assume_crs or CRS.from_epsg(4326)
            meta, fids, geoms, fdata = ogr_raw.read(tp, layer=lay, return_fids=True, force_2d=True)
            t = Transformer.from_crs(lcrs, 4326, always_xy=True)
            names = list(meta["fields"])
            for i in range(len(fids)):
                if geoms is None or geoms[i] is None:
                    continue
                g = shapely.from_wkb(geoms[i])
                if not lcrs.equals(CRS.from_epsg(4326)):
                    g = shp_transform(t.transform, g)
                props = {}
                for n, col in zip(names, fdata):
                    v = col[i]
                    if hasattr(v, "item"):
                        try:
                            v = v.item()
                        except Exception:
                            v = str(v)
                    if v is not None and not isinstance(v, (str, int, float, bool)):
                        v = str(v)
                    if isinstance(v, float) and v != v:
                        v = None
                    props[n] = v
                out.append((g, props, int(fids[i])))
        return fix_axis(out, lat, lon)
    finally:
        os.remove(tp)


def parse_wfs_caps(xml_bytes, base, ver):
    """Feature types (+default CRS), output formats, licence text. Uses OWSLib,
    falls back to a plain XML parse when OWSLib chokes."""
    out = {"types": [], "formats": [], "licence": "", "version": ver}
    try:
        from owslib.wfs import WebFeatureService
        w = WebFeatureService(base, version=ver, xml=xml_bytes)
        for name, c in w.contents.items():
            crs = None
            if getattr(c, "crsOptions", None):
                co = c.crsOptions[0]
                crs = getattr(co, "getcodeurn", lambda: None)() or str(co)
            out["types"].append({"name": name, "title": getattr(c, "title", ""), "crs": crs})
        try:
            op = w.getOperationByName("GetFeature")
            vals = (op.parameters.get("outputFormat") or {}).get("values") or getattr(op, "formatOptions", []) or []
            out["formats"] = list(vals)
        except Exception:
            pass
        idn = w.identification
        lic = " ".join(filter(None, [getattr(idn, "accessconstraints", None), getattr(idn, "fees", None)]))
        out["licence"] = lic
    except Exception:
        pass
    if not out["types"]:
        from lxml import etree
        root = etree.fromstring(xml_bytes)
        for ft in root.iter("{*}FeatureType"):
            nm = ft.findtext("{*}Name")
            crs = ft.findtext("{*}DefaultCRS") or ft.findtext("{*}DefaultSRS") or ft.findtext("{*}SRS")
            if nm:
                out["types"].append({"name": nm, "title": ft.findtext("{*}Title") or "", "crs": crs})
        for p in root.iter("{*}Parameter"):
            if (p.get("name") or "").lower() == "outputformat":
                out["formats"] = [v.text for v in p.iter("{*}Value")]
        out["licence"] = " ".join(filter(None, [root.findtext(".//{*}AccessConstraints"), root.findtext(".//{*}Fees")]))
    lic = out["licence"].strip()
    if lic.lower() in ("none", "none none", "", "keine", "keine keine"):
        out["licence"] = ""  # 'NONE' is not a licence
    return out


def pick_json_format(formats):
    fl = [f for f in formats if f]
    for pref in ("application/json", "application/geo+json", "json", "geojson", "application/vnd.geo+json"):
        for f in fl:
            if f.lower() == pref:
                return f
    for f in fl:
        if "json" in f.lower() and "subtype" not in f.lower():
            return f
    return None  # default GML


def links_licence(j):
    out = []
    for l in (j or {}).get("links", []) or []:
        if l.get("rel") in ("license", "licence"):
            out.append(f"{l.get('title', '')} {l.get('href', '')}".strip())
    return " ".join(out)


def classify_resource(u, fmt):
    """(priority, kind) for a catalog resource or page link, None if not map data."""
    ul = u.lower()
    fl = fmt.lower()
    path = urlparse(ul).path
    if "wfs" in fl or "service=wfs" in ul or "wfsserver" in ul or path.endswith("/wfs"):
        return (0, "wfs")
    if "ogc api" in fl or "/collections" in path or "ogc/features" in path:
        return (1, "ogcapi")
    if path.endswith((".gpkg",)) or "gpkg" in fl or "geopackage" in fl:
        return (2, "file")
    if path.endswith((".geojson",)) or fl in ("geojson", "geo+json"):
        return (3, "file")
    if path.endswith(".zip") and any(x in fl or x in ul for x in ("shp", "shape", "gpkg", "geojson", "gml", "kml", "gdb", "zip")):
        return (4, "file")
    if "shp" in fl or "shapefile" in fl:
        return (4, "file")
    if path.endswith((".kml", ".kmz")) or fl in ("kml", "kmz"):
        return (5, "file")
    if path.endswith(".gml") or fl == "gml":
        return (6, "file")
    if re.search(r"/(featureserver|mapserver)(/\d+)?/?$", path) or "esri rest" in fl or "arcgis geoservice" in fl:
        return (7, "arcgis")
    return None


def clean_text(s):
    s = html.unescape(re.sub(r"<[^>]+>", " ", str(s)))
    return re.sub(r"\s+", " ", s).strip()


# ---------------------------------------------------------------- report I/O
def load_report(path):
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf8") as f:
        return list(csv.DictReader(f))


def save_report(path, rows):
    tmp = path + ".tmp"
    with open(tmp, "w", newline="", encoding="utf8") as f:
        w = csv.DictWriter(f, fieldnames=REPORT_FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    os.replace(tmp, path)


def load_leads(path):
    j = json.load(open(path, encoding="utf8"))
    if isinstance(j, dict):  # club file: key other_layer
        j = j.get("other_layer") or j.get("leads") or []
    out = []
    for x in j:
        if not x.get("ref") or not x.get("url"):
            continue
        out.append(x)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--leads", required=True, help="leads.json (list, or club file with key other_layer)")
    ap.add_argument("--refs", help="comma-separated park refs to run (default: all)")
    ap.add_argument("--resume", action="store_true", help="skip (ref,url) pairs already in converted/report.csv")
    ap.add_argument("--retry-errors", action="store_true", help="with --resume, re-run rows whose status is ERROR")
    ap.add_argument("--out", default="converted", help="output folder (default converted/)")
    ap.add_argument("--cache", default=".kpc_cache", help="download cache folder")
    ap.add_argument("--max-minutes", type=float, default=50.0, help="stop starting new URLs after this (GitHub job limit 55)")
    ap.add_argument("--cache-days", type=float, default=7.0, help="reuse a cached file without ETag/Last-Modified for this many days")
    ap.add_argument("--max-types", type=int, default=15, help="max WFS feature types / collections per URL when none named")
    ap.add_argument("--no-pota", action="store_true", help="never look pins up on api.pota.app; leads must carry lat/lon")
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args(argv)

    leads = load_leads(a.leads)
    if a.refs:
        want = {r.strip() for r in a.refs.split(",") if r.strip()}
        leads = [l for l in leads if l["ref"] in want]
    conv = Converter(a)
    rpath = os.path.join(a.out, "report.csv")
    rows = load_report(rpath) if a.resume else []
    done = {(r["ref"], r["url"]): i for i, r in enumerate(rows)}
    t0 = time.time()
    todo = []
    for l in leads:
        k = (l["ref"], l["url"].strip())
        if a.resume and k in done and not (a.retry_errors and rows[done[k]]["status"] == "ERROR"):
            continue
        todo.append(l)
    print(f"{len(leads)} leads, {len(todo)} to do", flush=True)
    for n, l in enumerate(todo, 1):
        if (time.time() - t0) / 60 > a.max_minutes:
            print(f"time budget reached; {len(todo) - n + 1} leads left for the next run (--resume)", flush=True)
            break
        rec = conv.run_lead(l)
        k = (rec["ref"], rec["url"])
        if k in done:
            rows[done[k]] = rec
        else:
            done[k] = len(rows)
            rows.append(rec)
        save_report(rpath, rows)  # save after each URL
        print(f"[{n}/{len(todo)}] {rec['ref']:<9} {rec['status']:<7} {rec['kind']:<28} n={rec['n_records_near']} {rec['why'][:110]}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
