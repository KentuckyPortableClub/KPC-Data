#!/usr/bin/env python3
"""KPC 10: whole-map accuracy audit.

Grades every saved park outline with nine simple tests (T1-T9) and ranks the worst first, so a person looks at them first.
It decides nothing: it only ranks. It never changes a key or an outline, never moves a POTA pin, and never uses OSM / Google / WDPA.

Run:  python kpc_map_audit.py --areas US-KY US-TN CA-ON CH --data data --out audit
Exit: 0 = done, 3 = not finished (run again with --resume), 2 = bad input.
"""
from __future__ import annotations

import argparse
import collections
import csv
import datetime as dt
import hashlib
import json
import math
import re
import sys
import time
import unicodedata
from pathlib import Path
from urllib.parse import urlencode, urlparse
from urllib.robotparser import RobotFileParser

import numpy as np
import requests
import shapely
from pyproj import Geod, Transformer
from rapidfuzz import fuzz
from shapely.geometry import LineString, MultiLineString, MultiPolygon, Point, Polygon, shape
from shapely.ops import unary_union
from shapely.strtree import STRtree

TOOL = "KPC-map-audit"
UA = f"{TOOL} (https://github.com/KentuckyPortableClub)"
ACRE_M2 = 4046.8564224
GEOD = Geod(ellps="WGS84")
DEG_M = 111_320.0   # metres in one degree of latitude (about)

PADUS = "https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0"
CPCAD = "https://maps-cartes.ec.gc.ca/arcgis/rest/services/CWS_SCF/CPCAD/MapServer/0"
POTA_PARK = "https://api.pota.app/park/{ref}"
POTA_LOCATION = "https://api.pota.app/location/parks/{loc}"
POTA_LOCATIONS = "https://api.pota.app/locations"
POTA_LINK = "https://pota.app/#/park/{ref}"
READ_OFFSET_DEG = 0.00001   # ~1 m: records are read with this generalisation (keeps big parks small enough to read)

XMAP = {
    "fws": ["https://services.arcgis.com/QVENGdaPbd4LUkLV/arcgis/rest/services/FWSInterest_Simplified_Authoritative/FeatureServer/0/query", "ORGNAME", "U.S. Fish & Wildlife Service"],
    "wld": ["https://apps.fs.usda.gov/arcx/rest/services/EDW/EDW_Wilderness_02/MapServer/0/query", "wildernessname", "National Wilderness Preservation System"],
    "hma": ["https://gis.blm.gov/arcgis/rest/services/range/BLM_Natl_WHB/MapServer/0/query", "HMA_NAME", "Bureau of Land Management"],
    "rma": ["https://gis.blm.gov/arcgis/rest/services/recreation/BLM_Natl_Recreation/MapServer/9/query", "FET_NAME", "Bureau of Land Management"],
    "rst": ["https://gis.blm.gov/arcgis/rest/services/recreation/BLM_Natl_Recs_poly/MapServer/0/query", "FET_NAME", "Bureau of Land Management"],
    "nca": ["https://gis.blm.gov/arcgis/rest/services/lands/BLM_Natl_NLCS_NM_NCA_poly/MapServer/0/query", "NCA_NAME", "Bureau of Land Management"],
    "wsa": ["https://gis.blm.gov/arcgis/rest/services/lands/BLM_Natl_NLCS_WLD_WSA/MapServer/1/query", "NLCS_NAME", "Bureau of Land Management"],
    "wbl": ["https://gis.blm.gov/arcgis/rest/services/lands/BLM_Natl_NLCS_WLD_WSA/MapServer/0/query", "NLCS_NAME", "Bureau of Land Management"],
    "odw": ["https://services1.arcgis.com/jRf8jjFwxedITdFe/arcgis/rest/services/Public_WMA_Boundaries/FeatureServer/1/query", "WMANAME", "Oklahoma Dept. of Wildlife Conservation"],
}
KY_FILES = {
    "bstate": "ky-state-parks.geojson", "bwma": "ky-hunting-areas.geojson", "bsnp": "ky-nature-preserves.geojson",
    "bsna": "ky-natural-areas.geojson", "bdbnf": "ky-dbnf.geojson", "bdbnfo": "ky-dbnf-owned.geojson",
    "bnps": "ky-nps.geojson", "bwild": "ky-wild-rivers.geojson", "bwilder": "ky-wilderness.geojson",
    "bfws": "ky-fws.geojson", "bpad": "ky-padus-parks.geojson",
}
KY_PROCLAMATION = {"bdbnf"}   # rule 3: a proclamation line is never the park
KY_KIND = {"bstate": "state park", "bwma": "wildlife management area", "bsnp": "state nature preserve", "bsna": "state natural area", "bdbnf": "national forest proclamation boundary", "bdbnfo": "national forest owned land", "bnps": "national park service unit", "bwild": "wild river", "bwilder": "wilderness", "bfws": "national wildlife refuge", "bpad": "pad-us", "trl": "trail"}
class SourceDown(Exception):
    """A source could not be read (logged as SOURCE DOWN, retried next run)."""


class BadInput(Exception):
    """The input files are missing or not in the club's shape (exit 2)."""


def today() -> str:
    return dt.date.today().isoformat()


def log(msg: str) -> None:
    print(msg, flush=True)


class Http:
    """At most 1 request per second per host, our User-Agent, back-off on 429 / 5xx, robots.txt obeyed, disk cache with a date."""

    def __init__(self, cache_dir: Path, offline: bool = False, min_gap: float = 1.0, session=None, sleep=time.sleep, clock=time.monotonic):
        self.cache = Path(cache_dir)
        self.offline = offline
        self.min_gap = min_gap
        self.s = session or requests.Session()
        self.s.headers["User-Agent"] = UA
        self.sleep, self.clock = sleep, clock
        self.last: dict = {}
        self.robots: dict = {}
        self.failed_hosts: collections.Counter = collections.Counter()

    def _wait(self, host: str) -> None:
        now = self.clock()
        gap = self.last.get(host, -1e9) + self.min_gap - now
        if gap > 0:
            self.sleep(gap)
        self.last[host] = self.clock()

    def robots_ok(self, url: str) -> bool:
        u = urlparse(url)
        base = f"{u.scheme}://{u.netloc}"
        if base not in self.robots:
            rp = None
            if not self.offline:
                try:
                    self._wait(u.netloc)
                    r = self.s.get(base + "/robots.txt", timeout=20)
                    if r.status_code == 200 and "html" not in r.headers.get("content-type", "").lower():
                        rp = RobotFileParser()
                        rp.parse(r.text.splitlines())
                except requests.RequestException:
                    rp = None   # no robots file we can read = allowed (RFC 9309)
            self.robots[base] = rp
        rp = self.robots[base]
        return rp is None or rp.can_fetch(UA, url)

    @staticmethod
    def _key(url: str, params) -> str:
        full = url + ("?" + urlencode(sorted((params or {}).items())) if params else "")
        return hashlib.sha1(full.encode()).hexdigest()

    def get(self, url: str, params: dict | None = None, kind: str = "json", max_age_days: float = 30, tries: int = 4, timeout: int = 60):
        """Returns (data, read_date). Raises SourceDown."""
        key = self._key(url, params)
        sub = self.cache / ("tiles" if kind == "bytes" else "json")
        f = sub / (key + (".bin" if kind == "bytes" else ".json"))
        meta = sub / (key + ".date")
        if f.exists() and meta.exists():
            read = meta.read_text().strip()
            try:
                age = (dt.date.today() - dt.date.fromisoformat(read)).days
            except ValueError:
                age = 1e9
            if age <= max_age_days:
                return (f.read_bytes() if kind == "bytes" else json.loads(f.read_text())), read
        if self.offline:
            raise SourceDown(f"offline and not in the cache: {url}")
        host = urlparse(url).netloc
        if self.failed_hosts[host] >= 3:   # this host already failed 3 times this run: don't keep knocking
            raise SourceDown(f"{host}: down for this run (failed 3 times)")
        if not self.robots_ok(url):
            raise SourceDown(f"robots.txt asks bots not to read {url}")
        err = ""
        for i in range(tries):
            self._wait(host)
            try:
                r = self.s.get(url, params=params, timeout=timeout)
            except requests.RequestException as e:
                err = type(e).__name__
                self.sleep(min(60, 2 * 2 ** i))
                continue
            if r.status_code == 429 or r.status_code >= 500:
                err = f"HTTP {r.status_code}"
                ra = str(r.headers.get("Retry-After", ""))
                self.sleep(min(120, float(ra)) if ra.replace(".", "", 1).isdigit() else min(60, 2 * 2 ** i))
                continue
            if r.status_code != 200:
                err = f"HTTP {r.status_code}"
                break
            if kind == "bytes":
                data = r.content
                if not data or r.headers.get("content-type", "").startswith(("text/", "application/json")):
                    err = "not a picture tile"
                    break
                sub.mkdir(parents=True, exist_ok=True)
                f.write_bytes(data)
            else:
                try:
                    data = r.json()
                except ValueError:
                    err = "answer was not JSON"
                    break
                if isinstance(data, dict) and "error" in data and not data.get("features"):
                    e = data["error"]
                    err = f"layer said: {e.get('message', e) if isinstance(e, dict) else e}"
                    break
                sub.mkdir(parents=True, exist_ok=True)
                f.write_text(json.dumps(data))
            meta.write_text(today())
            return data, today()
        self.failed_hosts[host] += 1
        raise SourceDown(f"{host}: {err or 'no answer'}")


def depth(x) -> int:
    d = 0
    while isinstance(x, (list, tuple)) and x:
        d += 1
        x = x[0]
    return d


def ring_area(r) -> float:
    return 0.5 * sum(r[i][0] * r[(i + 1) % len(r)][1] - r[(i + 1) % len(r)][0] * r[i][1] for i in range(len(r)))


def esri_to_shape(g: dict):
    """ArcGIS JSON geometry (rings / paths) -> shapely. Outer rings run clockwise, holes counter-clockwise."""
    if not g:
        return None
    if "rings" in g:
        outers, holes = [], []
        for r in g["rings"]:
            if len(r) < 4:
                continue
            (outers if ring_area(r) < 0 else holes).append(r)
        if not outers and holes:          # some servers send counter-clockwise outers
            outers, holes = holes, []
        polys = [[Polygon(o), []] for o in outers]
        polys.sort(key=lambda p: abs(p[0].area))   # a hole belongs to the SMALLEST outer around it (islands in lakes)
        for h in holes:
            hp = Polygon(h)
            for p in polys:
                try:
                    inside = p[0].covers(hp) if p[0].is_valid and hp.is_valid else p[0].contains(hp.representative_point())
                except shapely.errors.GEOSException:
                    inside = p[0].contains(hp.representative_point())
                if inside:
                    p[1].append(h)
                    break
        out = [Polygon(p[0].exterior.coords, p[1]) for p in polys]
        if not out:
            return None
        return out[0] if len(out) == 1 else MultiPolygon(out)
    if "paths" in g:
        ls = [LineString(p) for p in g["paths"] if len(p) >= 2]
        return ls[0] if len(ls) == 1 else MultiLineString(ls)
    if "x" in g and "y" in g:
        return Point(g["x"], g["y"])
    return None


def to_shape(g):
    """GeoJSON geometry or ArcGIS geometry -> valid shapely geometry (or None)."""
    if not g:
        return None
    try:
        s = shape(g) if "type" in g else esri_to_shape(g)
    except Exception:
        return None
    if s is None or s.is_empty:
        return None
    if not s.is_valid:
        s = shapely.make_valid(s)
    return s


def rings_to_shape(rings):
    """A club 'r' / 'shape' list: one ring, a list of rings, or a list of polygons. A ring inside another ring is a hole."""
    d = depth(rings)
    if d == 2:
        rings = [rings]
    elif d == 4:
        polys = [rings_to_shape(p) for p in rings]
        polys = [p for p in polys if p is not None]
        return unary_union(polys) if polys else None
    polys = []
    for r in rings:
        if len(r) < 4:
            continue
        p = Polygon(r)
        if not p.is_valid:
            p = shapely.make_valid(p)
        hole_of = next((i for i, q in enumerate(polys) if q.contains(p.representative_point()) and q.area > p.area), None)
        if hole_of is not None:
            polys[hole_of] = polys[hole_of].difference(p)
        else:
            polys.append(p)
    if not polys:
        return None
    return unary_union(polys)


def local_proj(lon: float, lat: float):
    """Metric projection centred on a spot (azimuthal equidistant): good for distances and buffers near that spot."""
    crs = f"+proj=aeqd +lat_0={lat} +lon_0={lon} +datum=WGS84 +units=m"
    return Transformer.from_crs(4326, crs, always_xy=True), Transformer.from_crs(crs, 4326, always_xy=True)


def tx(geom, transformer):
    def f(a):
        x, y = transformer.transform(a[:, 0], a[:, 1])
        return np.column_stack([x, y])
    return shapely.transform(geom, f)


def acres(geom) -> float:
    if geom is None or geom.is_empty or geom.area == 0:
        return 0.0
    polys = polys_of(geom)
    return sum(abs(GEOD.geometry_area_perimeter(p)[0]) for p in polys) / ACRE_M2


def pin_distance_m(geom, lon: float, lat: float) -> float:
    """0 when the pin is inside the outline, else metres to the nearest edge."""
    if geom is None or geom.is_empty:
        return float("nan")
    if geom.covers(Point(lon, lat)):
        return 0.0
    fwd, _ = local_proj(lon, lat)
    return tx(geom, fwd).distance(Point(0, 0))


def width_m(geom) -> float:
    """How wide the patch is across at its widest point (2 x the biggest circle that fits), in metres."""
    if geom is None or geom.is_empty or geom.area == 0:
        return 0.0
    c = geom.centroid
    fwd, _ = local_proj(c.x, c.y)
    g = tx(geom, fwd)
    best = 0.0
    for p in sorted(polys_of(g), key=lambda p: -p.area)[:5]:
        if hasattr(shapely, "maximum_inscribed_circle"):
            r = shapely.maximum_inscribed_circle(p, 0.5).length
        else:   # binary search on an inward buffer
            lo, hi = 0.0, math.sqrt(p.area)
            for _ in range(20):
                mid = (lo + hi) / 2
                lo, hi = (mid, hi) if not p.buffer(-mid).is_empty else (lo, mid)
            r = lo
        best = max(best, 2 * r)
    return best


def polys_of(g):
    if g is None or g.is_empty:
        return []
    if isinstance(g, Polygon):
        return [g]
    if hasattr(g, "geoms"):
        return [q for p in g.geoms for q in polys_of(p)]
    return []


def arc_query(http: Http, layer: str, params: dict):
    """Query an ArcGIS layer; returns ([(shapely, properties)], read_date). GeoJSON first, ArcGIS JSON if the server can't."""
    url = layer.rstrip("/")
    if not url.endswith("/query"):
        url += "/query"
    base = {"outSR": 4326, "returnGeometry": "true", "outFields": "*"}
    base.update(params)
    try:
        j, read = http.get(url, dict(base, f="geojson"))
        if isinstance(j, dict) and "features" in j:
            return [(to_shape(f.get("geometry")), f.get("properties") or {}) for f in j["features"]], read
    except SourceDown as e:
        if "layer said" not in str(e) and "not JSON" not in str(e):
            raise
    j, read = http.get(url, dict(base, f="json"))
    return [(to_shape(f.get("geometry")), f.get("attributes") or {}) for f in j.get("features", [])], read


def layer_of(url: str) -> str:
    return re.sub(r"/query/?$", "", (url or "").rstrip("/"))


def name_from(props: dict, name_field=None) -> str:
    for k in [name_field, "Unit_Nm", "NAME_E", "NAME", "Name", "name", "ORGNAME", "PARK_NAME", "Loc_Nm"]:
        if k and props.get(k):
            return str(props[k])
    return ""


def acres_from(props: dict):
    for k in ["GIS_Acres", "ACRES", "Acres", "acres", "GISACRES", "GIS_ACRES", "TOTAL_ACRES", "O_AREA_HA"]:
        v = props.get(k)
        if isinstance(v, (int, float)) and v > 0:
            return v * 2.4710538 if k.endswith("_HA") else float(v)
    return None


def best_acres(rows):
    """Official acres from several records: add the pieces from the same source, then take the biggest source total
    (two sources describing the same park are not added together)."""
    by = collections.defaultdict(float)
    for rid, ac in rows:
        if not isinstance(ac, (int, float)) or ac <= 0:
            continue
        rid = str(rid)
        m = re.match(r"^[a-z]+", rid)
        src = rid.split(":")[0] if ":" in rid else (m.group(0) if m else "main")
        by[src] += ac
    return max(by.values()) if by else None


# ================================================================== the nine tests (pure functions, unit-tested)
SCORE_HARD = {"OUTSIDE", "WAY OFF", "MISMATCH", "CONFLICT", "SPILL"}   # 3 points each
SCORE_FAR = {"FAR"}                                                    # 5 points
SOFT = {"NEAR", "OFF", "WEAK", "INVALID", "SELF-INTERSECTION", "SLIVERS", "TINY HOLES", "SCATTERED", "EMPTY", "TOO COARSE",
        "DUPLICATE", "STALE CHECK"}                                    # 1 point each
NOT_FLAGS = {"PASS", "NO OUTLINE", "NO FIGURE", "N/A", "CAN'T TELL", "NOTE"}


def t1_pin(dist_m: float) -> dict:
    """T1: POTA's pin inside the outline? 0 = PASS, <= 500 m NEAR, > 500 m OUTSIDE, > 10 km FAR."""
    if dist_m is None or dist_m != dist_m:
        return {"flag": "NO OUTLINE"}
    d = round(float(dist_m), 1)
    if d == 0:
        return {"flag": "PASS", "metres": 0}
    if d <= 500:
        return {"flag": "NEAR", "metres": d}
    if d <= 10_000:
        return {"flag": "OUTSIDE", "metres": d}
    return {"flag": "FAR", "metres": d}


def t2_size(outline_acres: float, official_acres, official_from: str = "") -> dict:
    """T2: outline acres (equal-area) vs the official acres. x1.5 PASS, x1.5-5 OFF, > x5 WAY OFF."""
    if not outline_acres:
        return {"flag": "NO OUTLINE"}
    if not official_acres or official_acres <= 0:
        return {"flag": "NO FIGURE", "outline_acres": round(outline_acres, 1)}
    r = max(outline_acres / official_acres, official_acres / outline_acres)
    flag = "PASS" if r <= 1.5 else ("OFF" if r <= 5 else "WAY OFF")
    return {"flag": flag, "outline_acres": round(outline_acres, 1), "official_acres": round(float(official_acres), 1),
            "times": round(r, 2), "official_from": official_from}


# ---- T3 names
TYPE_WORDS = set("""
state provincial national federal county city regional municipal park parks parkway pk wildlife management area areas wma wmas refuge nwr nwa
forest forests nf sf recreation recreational rec ra sra nra natural nature preserve preserves reserve reserves conservation conservancy sanctuary
historic historical site sites shs nhs nhp nhl monument monuments memorial battlefield military scenic river rivers wsr wild trail trails nrt nht
nst greenway wilderness hunting access fishing fish game land lands unit units tract complex lake? of the and at on in a an la le les de du des d
lake lakes reservoir pond parc provinciale aire zone public use mire mires landscape landscapes inventory bln object objects protected protection habitat
""".split()) - {"lake?"}
ABBREV = {"mt": "mount", "mtn": "mountain", "ft": "fort", "st": "saint", "ste": "sainte", "pk": "park", "co": "county", "cr": "creek",
          "natl": "national", "nat": "national", "wl": "wildlife", "mgmt": "management", "hist": "historic", "rd": "road", "is": "island",
          "isl": "island", "pt": "point", "spgs": "springs", "spg": "spring", "lk": "lake", "riv": "river", "&": "and"}


def norm_tokens(s: str) -> list:
    """Normalise a name: case, accents, punctuation, initials joined ('J. W.' -> 'jw'), short forms spelled out."""
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode().lower()
    s = s.replace("&", " and ").replace("'", "").replace("\u2019", "")
    toks = re.findall(r"[a-z0-9]+", s)
    out, run = [], ""
    for t in toks:                      # join runs of single letters: "j w smith" -> "jw smith"
        if len(t) == 1 and t.isalpha():
            run += t
            continue
        if run:
            out.append(run)
            run = ""
        out.append(ABBREV.get(t, t))
    if run:
        out.append(run)
    return out


def own_words(s: str) -> list:
    """The park's own words: its name without the type words (State Park, WMA, National Forest...)."""
    toks = norm_tokens(s)
    own = [t for t in toks if t not in TYPE_WORDS]
    return own or toks


def name_score(park: str, record: str) -> float:
    """Token-set ratio of the own words, gated by how many of the PARK's own words appear in the record."""
    p, r = own_words(park), own_words(record)
    if not p or not r:
        return 0.0
    tsr = fuzz.token_set_ratio(" ".join(p), " ".join(r)) / 100
    rall = set(norm_tokens(record))
    rjoin = "".join(norm_tokens(record))   # "Horsemill" covers "Horse Mill"
    covered = sum(1 for w in p if w in rall or any(fuzz.ratio(w, x) >= 85 for x in rall) or (len(w) >= 4 and w in rjoin))
    return round(min(tsr, covered / len(p)), 3)


def t3_name(pota_name: str, record_names: list) -> dict:
    """T3: the record's name vs POTA's current name. >= 0.9 PASS, 0.75-0.9 WEAK, < 0.75 MISMATCH (best record counts)."""
    names = [n for n in dict.fromkeys(record_names) if n]
    if not names or not pota_name:
        return {"flag": "CAN'T TELL", "note": "no record name" if not names else "no POTA name"}
    scored = sorted(((name_score(pota_name, n), n) for n in names), reverse=True)
    best, bn = scored[0]
    flag = "PASS" if best >= 0.9 else ("WEAK" if best >= 0.75 else "MISMATCH")
    res = {"flag": flag, "score": best, "pota_name": pota_name, "record_name": bn}
    if len(scored) > 1 and scored[-1][0] < 0.75:
        res["worst_record"] = {"name": scored[-1][1], "score": scored[-1][0]}
    return res


# ---- T4 kinds
KIND_RULES = [   # (family, pattern) in order: the first that matches wins
    ("proclamation", r"proclamation|administrative boundary|forest boundary|purchase unit"),
    ("wma", r"\bwma\b|wildlife management|game management|game land|hunting|public hunting|wildlife area\b(?<!national wildlife area)|"
            r"fish and wildlife area|habitat (management|conservation) area|\bwmu\b|twra|wildlife resources agency"),
    ("refuge", r"wildlife refuge|national wildlife area|\bnwr\b|\bnwa\b|migratory bird sanctuary|u\.?s\.? fish"),
    ("state park", r"state park|provincial park|state resort park|\bsp\b|parc provincial|recreational state park"),
    ("national forest", r"national forest|\bnf\b|forest service|national grassland"),
    ("state forest", r"state forest|provincial forest"),
    ("canal", r"\bcanal\b"),
    ("lake", r"\b(lake|reservoir|pond|dam)\s*$|waterbody|water body|reservoir project|\blake project"),
    ("recreation area", r"recreation area|\bsra\b|\bnra\b|campground|day use|picnic area|boat (ramp|launch)|marina|beach|public access area"),
    ("trail", r"\btrail\b|\bnrt\b|\bnht\b|\bnst\b|greenway|\bpath\b"),
    ("river", r"wild (and|&) scenic river|\bwsr\b|wild river|scenic river|water trail|blueway|paddle trail"),
    ("preserve", r"nature preserve|natural area|state natural|\bsna\b|\bsnp\b|ecological reserve|nature reserve|conservation reserve"),
    ("national park", r"national park|national historical park|national monument|national battlefield|national memorial|nps\b|national park service"),
    ("wilderness", r"wilderness"),
]
CANAL_PART = r"\b(section|segment|lock|locks|aqueduct|towpath|basin|unit|feeder|lockhouse)\b"


def kind_of(text: str):
    t = str(text or "").lower()
    for fam, pat in KIND_RULES:
        if re.search(pat, t):
            return fam
    return None


def t4_kind(park_name: str, park_type: str, rec_name: str, rec_type: str = "", rec_category: str = "") -> dict:
    """T4: the record's type vs the park's type. Only clear clashes are a CONFLICT; an unknown kind is never flagged."""
    pk = kind_of(park_type) or kind_of(park_name)
    if str(rec_category).lower() == "proclamation":
        rk = "proclamation"
    else:
        rk = kind_of(rec_type) if rec_type else None
        rk = rk or kind_of(rec_name)
    res = {"park_kind": pk, "record_kind": rk}
    why = ""
    pn, rn = str(park_name or "").lower(), str(rec_name or "").lower()
    if rk == "proclamation":
        why = "the record is a proclamation line, not the land the agency owns"
    elif {pk, rk} == {"wma", "state park"}:
        why = f"the park is a {pk} but the record is a {rk}"
    elif rk == "lake" and pk in ("recreation area", None) and re.search(r"recreation|campground|day use|access|marina|beach|picnic", pn) \
            and not re.search(r"\b(lake|reservoir)\b\s*(state park|park)?$", pn):
        why = "the record is the whole lake but the park is a recreation area on it"
    elif "canal" in rn and "canal" in pn and re.search(CANAL_PART, pn) and not re.search(CANAL_PART, rn):
        why = "the record is the whole canal but the park is one section of it"
    if why:
        res.update(flag="CONFLICT", why=why)
    else:
        res["flag"] = "PASS" if (pk and rk) else "CAN'T TELL"
    return res


# ---- T5 shape health
def t5_health(raw_parts: list, geom) -> dict:
    """T5: invalid, self-intersection, slivers < 10 m wide, holes < 100 m2, > 50 pieces over > 50 km, empty."""
    flags, notes = [], []
    if geom is None or geom.is_empty or not raw_parts:
        return {"flag": "EMPTY", "flags": ["EMPTY"]}
    for g in raw_parts:
        if g is None or g.is_empty or "Polygon" not in g.geom_type:   # (a bow-tie has area 0: don't skip on area)
            continue
        if not g.is_valid:
            reason = shapely.is_valid_reason(g)
            if "self-intersection" in reason.lower() or "ring self-intersection" in reason.lower():
                if "SELF-INTERSECTION" not in flags:
                    flags.append("SELF-INTERSECTION")
                    notes.append(reason)
            elif "INVALID" not in flags:
                flags.append("INVALID")
                notes.append(reason)
    polys = polys_of(geom)
    if not polys:
        return {"flag": "N/A", "note": "a line, not an area"}
    c = geom.centroid
    fwd, _ = local_proj(c.x, c.y)
    gm = tx(geom, fwd)
    pm = polys_of(gm)
    slivers = sum(1 for p in pm if p.area > 0 and 2 * shapely.maximum_inscribed_circle(p, 0.25).length < 10)
    holes = sum(1 for p in pm for r in p.interiors if Polygon(r).area < 100)
    if slivers:
        flags.append("SLIVERS")
        notes.append(f"{slivers} piece(s) under 10 m wide")
    if holes:
        flags.append("TINY HOLES")
        notes.append(f"{holes} hole(s) under 100 m2")
    if len(pm) > 50:
        b = gm.bounds
        span = math.hypot(b[2] - b[0], b[3] - b[1])
        if span > 50_000:
            flags.append("SCATTERED")
            notes.append(f"{len(pm)} pieces spread over {span / 1000:.0f} km")
    res = {"flag": flags[0] if flags else "PASS", "pieces": len(pm)}
    if flags:
        res.update(flags=flags, note="; ".join(notes))
    return res


# ---- T6 spill
def t6_spill(ref: str, name: str, geom, others: list, excused: set, tree=None) -> dict:
    """T6: the outline covers > 30% of ANOTHER POTA park's pin area (its outline, else 500 m around its pin),
    with a different name and no 2-fer row = SPILL."""
    if geom is None or geom.is_empty or geom.area == 0:
        return {"flag": "NO OUTLINE"}
    hits = []
    cand = range(len(others)) if tree is None else tree.query(geom)
    for i in cand:
        oref, oname, oarea = others[int(i)]
        if oref == ref or oarea is None or oarea.is_empty or frozenset((ref, oref)) in excused:
            continue
        try:
            inter = geom.intersection(oarea)
        except shapely.errors.GEOSException:
            inter = geom.buffer(0).intersection(oarea.buffer(0))
        if inter.is_empty or oarea.area == 0:
            continue
        share = inter.area / oarea.area
        if share > 0.30 and name_score(name, oname) < 0.9 and name_score(oname, name) < 0.9:
            hits.append({"ref": oref, "name": oname, "share": round(share, 2)})
    if hits:
        hits.sort(key=lambda h: -h["share"])
        return {"flag": "SPILL", "parks": hits[:10], "count": len(hits)}
    return {"flag": "PASS"}


# ---- T7 detail
def coord_step_m(coords_iter, lat: float) -> float:
    """How coarse the saved coordinates are: the rounding step (e.g. 4 decimals = ~8-11 m), in metres."""
    best, seen = 0, False
    for i, v in enumerate(coords_iter):
        seen = True
        if i > 4000:
            break
        s = repr(float(v))
        d = len(s.split(".")[1].rstrip("0")) if "." in s and "e" not in s else 7
        best = max(best, d)
    if not seen or best >= 7:
        return 0.0   # nothing saved to judge, or 7+ decimals (~1 cm)
    return 10 ** -best * DEG_M * max(math.cos(math.radians(lat)), 0.2)


def flat_numbers(x):
    if isinstance(x, (int, float)):
        yield x
    elif isinstance(x, (list, tuple)):
        for y in x:
            yield from flat_numbers(y)


def vertex_spacing_m(geom) -> float:
    """Median distance between neighbouring corners of the outline (reported, not graded on its own)."""
    if geom is None or geom.is_empty:
        return 0.0
    c = geom.centroid
    fwd, _ = local_proj(c.x, c.y)
    gm = tx(geom, fwd)
    d = []
    for p in polys_of(gm):
        for ring in [p.exterior, *p.interiors]:
            xy = np.asarray(ring.coords)
            if len(xy) > 1:
                d.append(np.hypot(*np.diff(xy, axis=0).T))
    if not d:
        return 0.0
    return float(np.median(np.concatenate(d)))


def t7_detail(declared_m, step_m: float, spacing_m: float, world: bool, live: bool = False) -> dict:
    """T7: the saved outline's detail vs the 3 m rule; over 5 m = TOO COARSE (world parks: report only)."""
    if live:
        return {"flag": "N/A", "note": "read live at full detail, not a saved copy"}
    est = max([v for v in (declared_m, step_m) if isinstance(v, (int, float))] or [0])
    res = {"detail_m": round(est, 2), "declared_m": declared_m, "coordinate_step_m": round(step_m, 2), "median_spacing_m": round(spacing_m, 1)}
    if est > 5:
        res["flag"] = "NOTE" if world else "TOO COARSE"
        res["note"] = f"saved at about {est:.0f} m detail" + (" (world park: report only)" if world else "")
    else:
        res["flag"] = "PASS"
        if est > 3:
            res["note"] = "between 3 and 5 m: allowed, but over the 3 m aim"
    return res


# ---- T8 duplicates
def t8_duplicates(record_ids: dict) -> dict:
    """T8: {ref: [record ids]} -> {ref: [other refs sharing a record id]} for KPC 13 (same land, two park numbers)."""
    by = collections.defaultdict(set)
    for ref, ids in record_ids.items():
        for i in ids:
            by[i].add(ref)
    out = collections.defaultdict(dict)
    for rid, refs in by.items():
        if len(refs) > 1:
            for r in refs:
                for o in refs - {r}:
                    out[r].setdefault(o, []).append(rid)
    return {r: dict(v) for r, v in out.items()}


# ---- T9 age
def t9_age(last_edit, read_date) -> dict:
    """T9: the source's last edit (layer metadata) more than a year before the club read it = STALE CHECK.
    A source edited AFTER the club read it is noted (not scored): the club's copy may be out of date."""
    if not last_edit:
        return {"flag": "CAN'T TELL", "note": "the source gives no last-edit date"}
    try:
        le = dt.date.fromisoformat(str(last_edit)[:10])
        rd = dt.date.fromisoformat(str(read_date)[:10]) if read_date else dt.date.today()
    except ValueError:
        return {"flag": "CAN'T TELL", "note": "unreadable date"}
    res = {"last_edit": le.isoformat(), "read": rd.isoformat()}
    if le < rd - dt.timedelta(days=365):
        res.update(flag="STALE CHECK", note=f"the source was last edited {le.isoformat()}, over a year before the club read it ({rd.isoformat()})")
    elif le > rd:
        res.update(flag="NOTE", note=f"the source changed on {le.isoformat()}, after the club read it ({rd.isoformat()})")
    else:
        res["flag"] = "PASS"
    return res


# ---- score + why
def flags_of(tests: dict) -> list:
    out = []
    for k in sorted(tests):
        t = tests[k]
        fl = t.get("flags") or [t.get("flag")]
        out += [(k, f) for f in fl if f and f not in NOT_FLAGS]
    return out


def score_of(tests: dict) -> int:
    s = 0
    for _, f in flags_of(tests):
        s += 5 if f in SCORE_FAR else 3 if f in SCORE_HARD else 1
    return s


def why_of(ref: str, tests: dict) -> str:
    """One plain sentence naming the worst flag."""
    fl = flags_of(tests)
    if not fl:
        return "All tests pass." if any(t.get("flag") == "PASS" for t in tests.values()) else "Nothing could be tested."
    rank = lambda kf: (5 if kf[1] in SCORE_FAR else 3 if kf[1] in SCORE_HARD else 1)
    k, f = max(fl, key=rank)
    t = tests[k]
    more = f" (+{len(fl) - 1} more flag{'s' if len(fl) > 2 else ''})" if len(fl) > 1 else ""
    if k == "T1":
        m = t["metres"]
        txt = f"POTA's pin is {m / 1000:.1f} km outside the outline" if m >= 1000 else f"POTA's pin is {m:.0f} m outside the outline"
    elif k == "T2":
        big = "bigger" if t["outline_acres"] > t["official_acres"] else "smaller"
        txt = f"the outline is {t['times']:.1f} times {big} than the official {t['official_acres']:,.0f} acres ({t['outline_acres']:,.0f} ac drawn)"
    elif k == "T3":
        txt = f"the record name '{t['record_name']}' does not match POTA's name '{t['pota_name']}' (score {t['score']:.2f})"
    elif k == "T4":
        txt = t.get("why", "the record is a different kind of place")
    elif k == "T5":
        txt = f"the shape has problems: {t.get('note') or f.lower()}"
    elif k == "T6":
        p = t["parks"][0]
        txt = f"the outline covers {p['share']:.0%} of {p['ref']} {p['name']}, with no 2-fer row (maybe the wrong record)"
    elif k == "T7":
        txt = t.get("note", "the saved outline is too coarse")
    elif k == "T8":
        txt = "another park number uses the same record: " + ", ".join(sorted(t.get("parks", {}))[:3])
    elif k == "T9":
        txt = t.get("note", "the source is old")
    else:
        txt = f.lower()
    return f"{f}: {txt[0].upper() + txt[1:]}{more}."


# ================================================================== reading the club's files and the sources (read-only)
def disc(lon: float, lat: float, r_m: float = 500):
    fwd, back = local_proj(lon, lat)
    return tx(Point(0, 0).buffer(r_m, 16), back)


def last_edit_of(meta: dict):
    ms = ((meta or {}).get("editingInfo") or {}).get("lastEditDate")
    if isinstance(ms, (int, float)) and ms > 0:
        return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).date().isoformat()
    return None


def domain_names(meta: dict) -> dict:
    out = {}
    for f in (meta or {}).get("fields", []) or []:
        dm = f.get("domain") or {}
        if dm.get("codedValues"):
            out[f["name"]] = {str(c["code"]): c["name"] for c in dm["codedValues"]}
    return out


def geom_hash(g) -> str:
    return "geom#" + hashlib.sha1(shapely.to_wkb(shapely.set_precision(g, 1e-5), hex=True).encode()).hexdigest()[:16]


class Audit:
    def __init__(self, data: Path, ky_dir, http: Http, acres_list: dict, log_fn=log):
        self.data, self.http, self.ky_dir, self.acres_list, self.log = Path(data), http, (Path(ky_dir) if ky_dir else None), acres_list, log_fn
        self._json, self._meta = {}, {}
        self.layers = dict(XMAP)
        lp = self.data / "us-key" / "layers.json"
        if lp.exists():
            for k, v in self.load(lp).items():
                if isinstance(v, list) and v:
                    self.layers.setdefault(k, v)
        self._locations = None
        self.excused = self.fer_pairs()

    # ---- files
    def load(self, p):
        p = Path(p)
        if p not in self._json:
            try:
                self._json[p] = json.loads(p.read_text(encoding="utf-8"))
            except FileNotFoundError:
                raise BadInput(f"file not found: {p}")
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                raise BadInput(f"not readable JSON: {p} ({e})")
        return self._json[p]

    def fer_pairs(self) -> set:
        """Park pairs that already have a 2-fer row (any row not dropped): a spill between them is expected, not a flag."""
        pairs = set()
        d = self.data / "fers"
        for f in sorted(d.glob("*.json")) if d.exists() else []:
            try:
                rows = self.load(f).get("spots", [])
            except BadInput:
                continue
            for r in rows:
                if not isinstance(r, dict) or str(r.get("status", "")).lower().startswith("dropped"):
                    continue
                refs = r.get("refs") or str(r.get("id", "")).split("@")[0].split("+")
                refs = [x for x in refs if x]
                for i in range(len(refs)):
                    for j in range(i + 1, len(refs)):
                        pairs.add(frozenset((refs[i], refs[j])))
        return pairs

    # ---- sources
    def layer_meta(self, layer: str) -> dict:
        layer = layer_of(layer)
        if layer not in self._meta:
            try:
                self._meta[layer], _ = self.http.get(layer, {"f": "json"}, max_age_days=7)
            except SourceDown as e:
                self.log(f"  layer details not read ({e})")
                self._meta[layer] = {}
        return self._meta[layer]

    def pota_parks(self, area: str) -> dict:
        """POTA's current names and pins for an area (US-KY, CA-ON, or a whole country such as CH). Pins are never moved."""
        if "-" in area:
            locs = [area]
        else:
            if self._locations is None:
                self._locations, _ = self.http.get(POTA_LOCATIONS, max_age_days=30)
            locs = sorted({l.get("locationDesc") for l in self._locations if str(l.get("locationDesc", "")).startswith(area + "-")})
        out = {}
        for loc in locs:
            try:
                rows, read = self.http.get(POTA_LOCATION.format(loc=loc), max_age_days=30)
            except SourceDown as e:
                self.log(f"  POTA list for {loc} not read ({e})")
                continue
            for r in rows or []:
                if r.get("latitude") is not None:
                    out[r["reference"]] = {"name": r.get("name", ""), "lat": float(r["latitude"]), "lon": float(r["longitude"]),
                                           "locs": [x.strip() for x in str(r.get("locationDesc") or loc).split(",") if x.strip()]}
        pi = self.data / "parkinfo" / f"{area}.json"
        if pi.exists():   # the club's copy of POTA's pins, only if POTA did not answer for a park
            for ref, row in self.load(pi).get("parks", {}).items():
                if ref not in out and len(row) > 6 and row[5] is not None:
                    out[ref] = {"name": row[0], "lat": float(row[5]), "lon": float(row[6]), "from": "parkinfo"}
        return out

    def read_records(self, layer: str, ids: list, offset=READ_OFFSET_DEG, esri_only=False) -> dict:
        """{id: (raw geometry, properties, read date)} for a layer, read in batches of 25 (raw = as the source sent it,
        not repaired, so T5 can see its faults). Raises SourceDown."""
        url = layer_of(layer) + "/query"
        out = {}
        for i in range(0, len(ids), 25):
            part = [str(x) for x in ids[i:i + 25]]
            base = {"objectIds": ",".join(part), "outSR": 4326, "returnGeometry": "true", "outFields": "*"}
            if offset:
                base["maxAllowableOffset"] = offset
            feats, gkey = None, "properties"
            try:
                if esri_only:
                    raise SourceDown("not JSON: ArcGIS rings asked for")
                j, read = self.http.get(url, dict(base, f="geojson"))
                if isinstance(j, dict) and "features" in j:
                    feats = j["features"]
            except SourceDown as e:
                if "layer said" not in str(e) and "not JSON" not in str(e):
                    raise
            if feats is None:
                j, read = self.http.get(url, dict(base, f="json"))
                feats, gkey = j.get("features", []), "attributes"
            for f in feats:
                p = f.get(gkey) or {}
                oid = f.get("id", p.get(j.get("objectIdFieldName") or "OBJECTID", p.get("OBJECTID", p.get("objectid", p.get("FID")))))
                g = f.get("geometry")
                try:
                    raw = (shape(g) if "type" in g else esri_to_shape(g)) if g else None
                except Exception:
                    raw = None
                if oid is not None:
                    out[str(oid)] = (raw, p, read)
        return out

    # ---- one record per park, before testing
    @staticmethod
    def blank(ref, area):
        return {"ref": ref, "area": area, "name": "", "key_name": "", "type": "", "grade": "", "pin": None, "records": [],
                "raw": [], "geom": None, "official": None, "official_from": "", "live": False, "declared_m": None,
                "numbers": [], "read": "", "last_edit": None, "last_edit_from": "", "problems": [], "ids": [], "outline_from": []}

    def finish(self, P):
        parts = [g for g in P["raw"] if g is not None and not g.is_empty]
        fixed = []
        for g in parts:
            fixed.append(g if g.is_valid else shapely.make_valid(g))
        if fixed:
            u = unary_union(fixed)
            P["geom"] = u if not u.is_empty else None
        return P

    def ky_park(self, ref, p, area, read):
        """Kentucky: every tract the key lists, from the club's Kentucky outline files (a proclamation tract too: T4 flags it)."""
        P = self.blank(ref, area)
        P.update(key_name=p.get("n", ""), type=p.get("t", ""), grade="Kentucky key", read=read)
        ac_rows = []
        for t in p.get("tracts", []):
            lk, nm = t[0], t[1]
            t_ac = t[2] if len(t) > 2 and isinstance(t[2], (int, float)) else None
            if lk == "trl":
                f = self.data / "trails" / f"{ref}.json"
                if f.exists():
                    j = self.load(f)
                    g = j.get("geometry") if j.get("type") == "Feature" else j
                    P["raw"].append(shape(g))
                    P["numbers"] += list(flat_numbers(g.get("coordinates")))
                    P["records"].append({"id": f"trl:{ref}", "name": nm, "type": "trail", "layer": f"trails/{ref}.json"})
                    P["outline_from"].append(f"trails/{ref}.json")
                    P["ids"].append(f"trl:{ref}")
                else:
                    P["problems"].append(f"trail file trails/{ref}.json not found")
                continue
            fn = KY_FILES.get(lk)
            if not fn or not self.ky_dir or not (self.ky_dir / fn).exists():
                P["problems"].append(f"CAN'T TELL: Kentucky outline file for '{lk}' not found (give --ky-outlines)")
                continue
            fc = self.load(self.ky_dir / fn)
            hits = [f for f in fc.get("features", []) if (f.get("properties") or {}).get("ref") == ref or
                    str((f.get("properties") or {}).get("NAME", "")).strip().lower() == nm.strip().lower()]
            if not hits:
                P["problems"].append(f"tract '{nm}' not found in {fn}")
                continue
            f_ac = 0.0
            for f in hits:
                g = f.get("geometry")
                if not g:
                    continue
                try:
                    P["raw"].append(shape(g))
                except Exception:
                    P["problems"].append(f"a shape in {fn} could not be read")
                    continue
                P["numbers"] += list(flat_numbers(g.get("coordinates")))[:3000]
                a = (f.get("properties") or {}).get("ACRES")
                if isinstance(a, (int, float)) and a > 0:
                    f_ac += a
            typ = " ".join(x for x in [KY_KIND.get(lk, lk), str((hits[0].get("properties") or {}).get("TYPE") or "")] if x)
            if lk in KY_PROCLAMATION:
                typ += " proclamation"
            P["records"].append({"id": f"{lk}:{nm}", "name": nm, "type": typ, "layer": fn, "count": len(hits)})
            P["outline_from"].append(f"club file {fn}")
            P["ids"].append(f"{lk}:{nm.strip().lower()}")
            ac = f_ac or t_ac
            if ac:
                ac_rows.append((lk, ac))
        if ac_rows:
            P["official"] = best_acres(ac_rows)
            P["official_from"] = "the outline files' ACRES / the key's tract acres"
        return self.finish(P)

    def live_records(self, P, groups: dict, default_layer: str, kind: str):
        """Read a park's records live, layer by layer. groups = {layer prefix: [(id, key row)]}."""
        ac_rows = []
        for pre, rows in groups.items():
            if pre and pre not in self.layers:
                P["problems"].append(f"CAN'T TELL: no layer known for record id '{pre}…'")
                continue
            layer = layer_of(self.layers[pre][0]) if pre else default_layer
            name_field = self.layers[pre][1] if pre else None
            desc = self.layers[pre][2] if pre and len(self.layers[pre]) > 2 else ""
            meta = self.layer_meta(layer)
            doms = domain_names(meta)
            le = last_edit_of(meta)
            if le and (not P["last_edit"] or le > P["last_edit"]):
                P["last_edit"], P["last_edit_from"] = le, layer
            try:
                got = self.read_records(layer, [r[0] for r in rows])
            except SourceDown as e:
                P["problems"].append(f"SOURCE DOWN: {e}")
                P["retry"] = True
                continue
            for oid, krow in rows:
                hit = got.get(str(oid))
                if hit is None:
                    P["problems"].append(f"record {pre}{oid} is no longer in {layer}")
                    continue
                raw, props, read = hit
                if raw is not None and not raw.is_valid:
                    # double-check at full detail, as ArcGIS rings: the 1 m read, and the server's own GeoJSON conversion
                    # (it can misplace an island inside a lake), both cause faults that are not in the record
                    try:
                        full = self.read_records(layer, [oid], offset=None, esri_only=True).get(str(oid))
                        if full and full[0] is not None:
                            if full[0].is_valid:
                                P.setdefault("notes", []).append(f"record {pre}{oid}: the fault came from the 1 m / GeoJSON read only; "
                                                                 "the record is fine at full detail")
                            raw = full[0]
                    except SourceDown:
                        pass
                P["raw"].append(raw)
                P["read"] = P["read"] or read
                code = str(props.get("Des_Tp") or "")
                typ = " ".join(x for x in [str(props.get("Loc_Ds") or ""), doms.get("Des_Tp", {}).get(code, code),
                                           str(props.get("TYPE_E") or ""), desc if pre else ""] if x)
                cat = str(props.get("Category") or "")
                cat = doms.get("Category", {}).get(cat, cat)
                nm = name_from(props, name_field) or str(krow[1] if len(krow) > 1 else "")
                ac = acres_from(props)
                src_ac = "GIS_Acres" if props.get("GIS_Acres") else ("O_AREA_HA" if props.get("O_AREA_HA") else "acres field")
                if ac is None and len(krow) > 2 and isinstance(krow[2], (int, float)) and krow[2] > 0:
                    ac, src_ac = float(krow[2]), "the key's acres"
                if ac:
                    ac_rows.append((pre or kind, ac))
                rid = f"{pre}{oid}" if pre else (f"{kind}#{oid}")
                link = f"{layer}/query?objectIds={oid}&outFields=*&returnGeometry=false&f=html"
                P["records"].append({"id": rid, "name": nm, "type": typ, "category": cat, "acres": round(ac, 1) if ac else None,
                                     "acres_from": src_ac if ac else "", "layer": layer, "link": link, "name_field": name_field or ""})
                P["ids"].append(f"{layer}#{oid}")
                if layer not in P["outline_from"]:
                    P["outline_from"].append(layer)
        if ac_rows:
            P["official"] = best_acres(ac_rows)
            P["official_from"] = "the records' own acres fields (PAD-US GIS_Acres / CPCAD official area)"
        P["live"] = True
        return P

    def us_park(self, ref, p, area):
        P = self.blank(ref, area)
        P.update(key_name=p.get("n", ""), type=p.get("t", ""), grade=p.get("g", ""), key_read=p.get("read", ""), pin_in_state=p.get("pin_in_state", ""))
        groups = collections.defaultdict(list)
        for row in p.get("m", []) or []:
            s = str(row[0])
            mm = re.match(r"^[a-z]+", s)
            pre = mm.group(0) if mm else ""
            groups[pre].append((s[len(pre):], row))
        if groups:
            self.live_records(P, groups, PADUS, "padus")
        P["read"] = p.get("read") or P["read"]
        if not P["raw"]:
            f = self.data / "trails" / f"{ref}.json"
            if f.exists():
                j = self.load(f)
                g = j.get("geometry") if j.get("type") == "Feature" else j
                P["raw"].append(shape(g))
                P["numbers"] = list(flat_numbers(g.get("coordinates")))[:6000]
                P["outline_from"].append(f"trails/{ref}.json")
                P["records"].append({"id": f"trl:{ref}", "name": P["key_name"], "type": "trail", "layer": f"trails/{ref}.json"})
        return self.finish(P)

    def ca_park(self, ref, p, area, key_read):
        P = self.blank(ref, area)
        P.update(key_name=p.get("n", ""), type=p.get("t", ""), grade=p.get("g", ""), read=key_read)
        m = p.get("m", []) or []
        ints = [(str(r[0]), r) for r in m if isinstance(r[0], int)]
        strs = [r for r in m if not isinstance(r[0], int)]
        bf = self.data / "canada-bounds" / f"{ref}.json"
        if bf.exists():
            j = self.load(bf)
            props = j.get("properties") or {}
            g = j.get("geometry")
            if g:
                P["raw"].append(shape(g))
                P["numbers"] = list(flat_numbers(g.get("coordinates")))[:6000]
            P["declared_m"] = props.get("detail_m")
            P["read"] = str(props.get("refined", ""))[:10] or key_read
            P["outline_from"].append(f"canada-bounds/{ref}.json")
            for r in m:
                P["records"].append({"id": str(r[0]), "name": r[1] if len(r) > 1 else "", "type": props.get("type", "") if r is m[0] else "",
                                     "acres": r[2] if len(r) > 2 else None, "layer": "CPCAD" if isinstance(r[0], int) else str(r[0]).split(":")[0]})
            if props.get("cpcad"):
                P["records"].insert(0, {"id": "canada-bounds", "name": props["cpcad"], "type": props.get("type", ""), "layer": f"canada-bounds/{ref}.json"})
            P["ids"] = [("cpcad#" if isinstance(r[0], int) else "") + str(r[0]) for r in m]
            rows = [(("cpcad" if isinstance(r[0], int) else str(r[0]).split(":")[0]), r[2]) for r in m if len(r) > 2 and isinstance(r[2], (int, float)) and r[2] > 0]
            if rows:
                P["official"] = best_acres(rows)
                P["official_from"] = "the key's record acres (CPCAD / provincial lists)"
            return self.finish(P)
        if ints:
            self.live_records(P, {"": ints}, CPCAD, "cpcad")
            P["live"] = True
            P["ids"] = ["cpcad#" + i for i, _ in ints]
        if strs:
            P["problems"].append(f"CAN'T TELL: {len(strs)} record(s) on provincial lists this tool can't read live ({', '.join(sorted({str(r[0]).split(':')[0] for r in strs}))})")
            P["ids"] += [str(r[0]) for r in strs]
            if not ints:
                P["records"] += [{"id": str(r[0]), "name": r[1], "acres": r[2] if len(r) > 2 else None, "layer": str(r[0]).split(":")[0]} for r in strs]
            else:
                P["partial"] = True
        return self.finish(P)

    def world_parks(self, country):
        d = self.data / "world-bounds" / country
        if not d.exists():
            raise BadInput(f"no world-bounds folder for {country}: {d}")
        out = {}
        for f in sorted(d.glob("*.json"), key=lambda x: (len(x.stem), x.stem)):
            for ref, row in self.load(f).items():
                if not isinstance(row, dict) or "r" not in row:
                    continue
                P = self.blank(ref, country)
                P.update(key_name=row.get("n", ""), grade="world outline", read=row.get("d", "") or row.get("read", ""))
                g = rings_to_shape(row["r"])
                rr = row["r"] if depth(row["r"]) == 3 else [row["r"]] if depth(row["r"]) == 2 else [r for poly in row["r"] for r in poly]
                P["raw"] = [Polygon(r) for r in rr if len(r) >= 4]   # each ring as saved, unrepaired, for T5
                P["numbers"] = list(flat_numbers(row["r"]))[:6000]
                P["records"].append({"id": f"world-bounds/{country}/{f.name}#{ref}", "name": row.get("n", ""), "type": "", "layer": str(row.get("s", ""))})
                P["outline_from"].append(f"world-bounds/{country}/{f.name} ({row.get('s', '')})")
                P["geom"] = g if g is not None and not g.is_empty else None   # rings inside rings are holes
                if P["geom"] is not None:
                    P["ids"] = [geom_hash(P["geom"])]
                out[ref] = P
        return out



# ================================================================== grading one area
def load_acres_list(path):
    """--acres acres-list.json: {ref: acres}, {ref: {"acres": n}} or [{"ref":..., "acres":...}]."""
    if not path:
        return {}
    try:
        j = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        raise BadInput(f"--acres file not readable: {e}")
    out = {}
    rows = j.items() if isinstance(j, dict) else ((r.get("ref"), r) for r in j if isinstance(r, dict))
    for ref, v in rows:
        if isinstance(v, dict):
            v = v.get("acres", v.get("ac"))
        if ref and isinstance(v, (int, float)) and v > 0:
            out[str(ref)] = float(v)
    return out


def area_kind(data: Path, area: str):
    if area == "US-KY" and (data / "ky-answer-key.json").exists():
        return "ky", data / "ky-answer-key.json"
    if area.startswith("US-"):
        return "us", data / "us-key" / f"{area}.json"
    if area.startswith("CA-"):
        return "ca", data / "ca-key" / f"{area}.json"
    if re.fullmatch(r"[A-Z0-9]{1,3}", area):
        return "world", data / "world-bounds" / area
    raise BadInput(f"area '{area}' is not US-xx, CA-xx or a country prefix such as CH")


def is_area(g) -> bool:
    return g is not None and not g.is_empty and g.area > 0


def grade_park(P, pin, acres_list, world: bool):
    """T1-T5, T7, T9 for one park (T6 and T8 need all parks: done after)."""
    g = P["geom"]
    tests = {}
    down = P.get("retry") and not P["raw"]
    if pin is None:
        tests["T1"] = {"flag": "CAN'T TELL", "note": "POTA has no pin for this park"}
    elif g is None:
        tests["T1"] = {"flag": "NO OUTLINE"}
    else:
        d = pin_distance_m(g, pin["lon"], pin["lat"])
        if not is_area(g) and d <= 30:    # a trail / river line: the pin within 30 m of the line counts as on it
            d = 0.0
        tests["T1"] = t1_pin(d)
        other = P.get("pin_in_state") or ""
        many = [x for x in (pin.get("locs") or []) if x != P["area"]]
        if tests["T1"]["flag"] in ("OUTSIDE", "FAR") and not world and (other and other not in P["area"] or many):
            tests["T1"] = {"flag": "NOTE", "metres": tests["T1"]["metres"], "was": tests["T1"]["flag"],
                           "note": "the park spans several states / provinces (" + ", ".join([P["area"]] + many) +
                                   "): POTA's one pin may be in another part" + (f" (the key says {other})" if other else "")}
    if g is None:
        tests["T2"] = {"flag": "NO OUTLINE"}
    elif not is_area(g):
        tests["T2"] = {"flag": "N/A", "note": "a line, not an area"}
    elif P.get("retry"):
        tests["T2"] = {"flag": "CAN'T TELL", "note": "a source was down: only part of the park could be read"}
    else:
        off, frm = P["official"], P["official_from"]
        if not off and P["ref"] in acres_list and not P.get("partial"):
            off, frm = acres_list[P["ref"]], "the club's acreage list"
        tests["T2"] = t2_size(acres(g), off, frm)
        if P.get("partial"):   # drawn and official acres both come from the records that could be read
            tests["T2"]["note"] = "only the records this tool can read (CPCAD) are drawn and counted"
    pname = (pin or {}).get("name") or ""
    tests["T3"] = t3_name(pname or P["key_name"], [r.get("name", "") for r in P["records"]])
    if not pname and tests["T3"].get("flag") != "CAN'T TELL":
        tests["T3"]["note"] = "POTA did not answer: the key's name was used"
    t4 = [t4_kind(pname or P["key_name"], P["type"] or (pin or {}).get("type", ""), r.get("name", ""), r.get("type", ""), r.get("category", ""))
          for r in P["records"]] if P["records"] else []
    if not t4:
        tests["T4"] = {"flag": "CAN'T TELL", "note": "no record"}
    else:
        bad = [t for t in t4 if t["flag"] == "CONFLICT"]
        tests["T4"] = bad[0] if bad else next((t for t in t4 if t["flag"] == "PASS"), t4[0])
    if down:
        tests["T5"] = {"flag": "CAN'T TELL", "note": "source down"}
    elif not P["raw"] and not P["records"]:
        tests["T5"] = {"flag": "NO OUTLINE", "note": "no outline saved (pin only)"}
    elif not P["raw"]:
        tests["T5"] = {"flag": "CAN'T TELL", "note": "the park's records could not be read (see problems)"}
    else:
        tests["T5"] = t5_health(P["raw"], g)
    if g is None:
        tests["T7"] = {"flag": "NO OUTLINE"}
    else:
        lat = g.centroid.y
        tests["T7"] = t7_detail(P["declared_m"], coord_step_m(P["numbers"], lat), vertex_spacing_m(g), world, live=P["live"])
    if P["live"]:
        tests["T9"] = t9_age(P["last_edit"], P["read"])
        if tests["T9"]["flag"] == "CAN'T TELL":
            tests["T9"]["note"] = "the source's layer details give no last-edit date"
    else:
        tests["T9"] = {"flag": "CAN'T TELL", "note": "a saved club copy: the source's last-edit date is not recorded with it"}
    return tests


def pota_name_for(audit, ref, pota):
    if ref in pota:
        return pota[ref]
    try:
        j, _ = audit.http.get(POTA_PARK.format(ref=ref), max_age_days=30)
        if isinstance(j, dict) and j.get("latitude") is not None:
            pota[ref] = {"name": j.get("name", ""), "lat": float(j["latitude"]), "lon": float(j["longitude"]), "from": "POTA park page",
                         "locs": [x.strip() for x in str(j.get("locationDesc") or "").split(",") if x.strip()]}
            return pota[ref]
    except SourceDown:
        pass
    return None


def run_area(audit: Audit, area: str, acres_list: dict, deadline: float, progress: dict):
    """Returns (records, finished). Parks already graded in `progress` are not graded again (--resume)."""
    kind, path = area_kind(audit.data, area)
    audit.log(f"{area}: {kind} ({path})")
    pota = audit.pota_parks(area)
    audit.log(f"  POTA: {len(pota)} parks with pins")
    parks = {}
    if kind == "world":
        parks = audit.world_parks(area)
        keyparks = {r: None for r in parks}
    else:
        key = audit.load(path)
        keyparks = key.get("parks") or {}
        if not keyparks:
            raise BadInput(f"no parks in {path}")
    done = progress.setdefault("parks", {})
    geoms = progress.setdefault("_geoms", {})
    finished = True
    for n, (ref, p) in enumerate(sorted(keyparks.items())):
        if ref in done:
            continue
        if time.monotonic() > deadline:
            finished = False
            break
        try:
            if kind == "ky":
                P = audit.ky_park(ref, p, area, key.get("updated", ""))
            elif kind == "us":
                P = audit.us_park(ref, p, area)
            elif kind == "ca":
                P = audit.ca_park(ref, p, area, p.get("read", "") or str(key.get("built", ""))[:10])
            else:
                P = parks[ref]
        except Exception as e:   # one bad park never stops the batch
            P = Audit.blank(ref, area)
            P["problems"].append(f"CAN'T TELL: {type(e).__name__}: {e}")
            P["retry"] = True
        pin = pota_name_for(audit, ref, pota)
        tests = grade_park(P, pin, acres_list, kind == "world")
        g = P["geom"]
        done[ref] = {
            "ref": ref, "name": (pin or {}).get("name", "") or P["key_name"], "key_name": P["key_name"], "type": P["type"], "grade": P["grade"],
            "pin": [round(pin["lat"], 6), round(pin["lon"], 6)] if pin else None,
            "outline_from": P["outline_from"], "acres_drawn": round(acres(g), 1) if is_area(g) else None,
            "records": [{k: v for k, v in r.items() if v not in (None, "")} for r in P["records"][:12]],
            "record_ids": P["ids"], "tests": tests, "problems": P["problems"] + P.get("notes", []),
            "status": "SOURCE DOWN: retry next run" if P.get("retry") else "graded",
        }
        geoms[ref] = shapely.to_wkb(g, hex=True) if is_area(g) else None
        if (n + 1) % 50 == 0:
            audit.log(f"  {n + 1}/{len(keyparks)} parks")
    if not finished:
        return None, False
    # ---- T6 spill and T8 duplicates need every park of the area
    others = []
    for ref, pin in pota.items():
        wkb = geoms.get(ref)
        try:
            ga = shapely.from_wkb(wkb) if wkb else disc(pin["lon"], pin["lat"])
        except Exception:
            ga = disc(pin["lon"], pin["lat"])
        others.append((ref, pin["name"], ga))
    for ref, wkb in geoms.items():   # parks in the key that POTA's list for this area doesn't have
        if wkb and ref not in pota:
            others.append((ref, done[ref]["name"], shapely.from_wkb(wkb)))
    tree = STRtree([o[2] for o in others]) if others else None
    for ref, rec in done.items():
        wkb = geoms.get(ref)
        g = shapely.from_wkb(wkb) if wkb else None
        rec["tests"]["T6"] = t6_spill(ref, rec["name"], g, others, audit.excused, tree) if g is not None else {"flag": "NO OUTLINE"}
    dups = t8_duplicates({r: rec["record_ids"] for r, rec in done.items()})
    for ref, rec in done.items():
        if ref in dups:
            rec["tests"]["T8"] = {"flag": "DUPLICATE", "parks": dups[ref], "note": "same record id(s) as another park number: for KPC 13"}
        else:
            rec["tests"]["T8"] = {"flag": "PASS"} if rec["record_ids"] else {"flag": "CAN'T TELL", "note": "no record id"}
    out = []
    for ref in sorted(done):
        rec = done[ref]
        rec["tests"] = {k: rec["tests"][k] for k in sorted(rec["tests"])}
        rec["score"] = score_of(rec["tests"])
        rec["why"] = why_of(ref, rec["tests"])
        if rec["status"] != "graded":
            rec["why"] = "SOURCE DOWN: " + rec["why"]
        out.append(rec)
    return out, True


# ================================================================== outputs (small, plain)
QUESTION_TEXT = ("Is this saved outline right for this park? Check the record against the agency's own map and POTA's park page. "
                 "Answer YES (keep), NO (wrong record or wrong land), or NOT SURE.")


def flag_summary(tests: dict) -> str:
    return ", ".join(f"{k} {f}" for k, f in flags_of(tests)) or "all pass"


def question_of(area: str, rec: dict, built: str) -> dict:
    r0 = next((r for r in rec["records"] if r.get("link")), rec["records"][0] if rec["records"] else {})
    t2 = rec["tests"].get("T2", {})
    return {
        "area": area, "ref": rec["ref"], "park": rec["name"], "tier": "audit", "why": rec["why"],
        "kind": "map accuracy", "record": r0.get("id", ""), "record_name": r0.get("name", ""),
        "acres_approx": rec.get("acres_drawn") or t2.get("official_acres"), "layer": r0.get("layer", ""),
        "agency": "", "record_link": r0.get("link", "") or r0.get("layer", ""), "pota_link": POTA_LINK.format(ref=rec["ref"]),
        "question": QUESTION_TEXT, "answer": None, "checked_by": None, "how": None,
        "source": f"KPC 10 map audit, {built}", "st": area, "url": r0.get("link", ""), "name_field": r0.get("name_field", ""),
        "licence": "", "note": f"score {rec['score']}: {flag_summary(rec['tests'])}", "score": rec["score"], "picture": "",
    }


def write_outputs(out: Path, results: dict, built: str):
    out.mkdir(parents=True, exist_ok=True)
    for area, recs in results.items():
        (out / f"{area}.json").write_text(json.dumps({"area": area, "built": built, "tool": TOOL, "parks": recs},
                                                      indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    rows = [(area, r) for area, recs in results.items() for r in recs]
    rows.sort(key=lambda x: (-x[1]["score"], x[0], x[1]["ref"]))
    with open(out / "worst.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["score", "area", "ref", "park", "why", "flags", "pota_link", "record_link"])
        for area, r in rows:
            if r["score"] <= 0:
                continue
            link = next((x.get("link") for x in r["records"] if x.get("link")), "")
            w.writerow([r["score"], area, r["ref"], r["name"], r["why"], flag_summary(r["tests"]), POTA_LINK.format(ref=r["ref"]), link])
    lines = [f"# KPC 10 map audit: summary ({built})", "",
             "It decides nothing: it ranks. Score 0 = all pass; +3 OUTSIDE / WAY OFF / MISMATCH / CONFLICT / SPILL, +5 FAR, +1 each softer flag.", ""]
    for area, recs in results.items():
        graded = [r for r in recs if r["tests"].get("T5", {}).get("flag") not in ("EMPTY", "NO OUTLINE")]
        flagged = [r for r in recs if r["score"] > 0]
        nooutline = sum(1 for r in recs if r["tests"].get("T5", {}).get("flag") in ("EMPTY", "NO OUTLINE"))
        unread = sum(1 for r in recs if r["tests"].get("T5", {}).get("flag") == "CAN'T TELL")
        down = sum(1 for r in recs if r["status"] != "graded")
        counts = collections.Counter(f for r in recs for _, f in flags_of(r["tests"]))
        lines += [f"## {area}", "",
                  f"- parks: {len(recs)} ({len(graded) - unread} with an outline graded, {nooutline} with no outline, {unread} with records this tool can't read)",
                  f"- pass every test: {len(recs) - len(flagged)}; have flags: {len(flagged)}" + (f"; source down (retry): {down}" if down else ""),
                  "- flags: " + (", ".join(f"{k} {v}" for k, v in counts.most_common()) or "none"), "",
                  "| score | ref | park | why |", "|---|---|---|---|"]
        for r in sorted(recs, key=lambda r: (-r["score"], r["ref"]))[:10]:
            if r["score"] > 0:
                lines.append(f"| {r['score']} | {r['ref']} | {r['name'].replace('|', '/')} | {r['why'].replace('|', '/')} |")
        lines.append("")
    (out / "summary.md").write_text("\n".join(lines), encoding="utf-8")
    qs = []
    for area, recs in results.items():
        top = [r for r in sorted(recs, key=lambda r: (-r["score"], r["ref"])) if r["score"] > 0][:50]
        qs += [question_of(area, r, built) for r in top]
    (out / "questions.json").write_text(json.dumps({"about": "KPC 10 map audit: the 50 worst outlines per area, for a person to check. "
                                                   "answer is null until checked; picture is left empty for KPC 9.",
                                                   "built": built, "open": len(qs), "questions": qs}, indent=1, ensure_ascii=False) + "\n",
                                        encoding="utf-8")


# ================================================================== main
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="KPC 10: grade every saved park outline (T1-T9) and rank the worst first. Decides nothing.")
    ap.add_argument("--areas", nargs="+", required=True, help="US-KY US-TN CA-ON CH ...")
    ap.add_argument("--data", default="data", help="folder with ky-answer-key.json, us-key/, ca-key/, canada-bounds/, world-bounds/, fers/, trails/")
    ap.add_argument("--ky-outlines", default=None, help="folder with the club's ky-*.geojson outline files (Kentucky)")
    ap.add_argument("--acres", default=None, help="acres-list.json (optional): the club's acreage list")
    ap.add_argument("--out", default="audit")
    ap.add_argument("--cache", default=".kpc-cache")
    ap.add_argument("--max-minutes", type=float, default=50)
    ap.add_argument("--resume", action="store_true", help="carry on from where the last run stopped")
    ap.add_argument("--offline", action="store_true", help="use the cache only (no network)")
    a = ap.parse_args(argv)
    t0 = time.monotonic()
    deadline = t0 + a.max_minutes * 60
    data, out, cache = Path(a.data), Path(a.out), Path(a.cache)
    try:
        if not data.exists():
            raise BadInput(f"--data folder not found: {data}")
        for ar in a.areas:
            area_kind(data, ar)
        acres_list = load_acres_list(a.acres)
        http = Http(cache, offline=a.offline)
        http.s.headers["User-Agent"] = UA
        audit = Audit(data, a.ky_outlines, http, acres_list)
    except BadInput as e:
        log(f"BAD INPUT: {e}")
        return 2
    state_f = cache / "audit-state.json"
    state = {}
    if a.resume and state_f.exists():
        try:
            state = json.loads(state_f.read_text())
        except json.JSONDecodeError:
            state = {}
    if state.get("areas_asked") != a.areas:
        state = {"areas_asked": a.areas, "done": {}, "progress": {}}
    built = today()
    results = {}
    for ar in a.areas:
        if ar in state["done"]:
            results[ar] = json.loads((out / f"{ar}.json").read_text())["parks"] if (out / f"{ar}.json").exists() else state["done"][ar]
            log(f"{ar}: already done (resume)")
            continue
        prog = state["progress"].setdefault(ar, {})
        try:
            recs, ok = run_area(audit, ar, acres_list, deadline, prog)
        except BadInput as e:
            log(f"BAD INPUT: {e}")
            return 2
        except SourceDown as e:
            log(f"SOURCE DOWN: {ar}: {e} (try again next run)")
            continue
        if not ok:
            cache.mkdir(parents=True, exist_ok=True)
            state_f.write_text(json.dumps(state))
            write_outputs(out, results, built)
            log(f"time is up after {(time.monotonic() - t0) / 60:.1f} min: run again with --resume")
            return 3
        results[ar] = recs
        state["done"][ar] = True
        state["progress"].pop(ar, None)
        write_outputs(out, {ar: recs}, built)
        log(f"{ar}: {len(recs)} parks, {sum(1 for r in recs if r['score'] > 0)} with flags")
    write_outputs(out, results, built)
    cache.mkdir(parents=True, exist_ok=True)
    state_f.write_text(json.dumps(state))
    log(f"done in {(time.monotonic() - t0) / 60:.1f} min: {out}/summary.md, worst.csv, questions.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
