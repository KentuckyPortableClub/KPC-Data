#!/usr/bin/env python3
"""KPC 12: River-Bank Library (Canada + the world).

For each water-trail stretch the club sends, this helper reads the OFFICIAL water
polygons of the river the trail follows and writes:
  - the water polygon (the river as the government maps it), and
  - the 100 ft band: the strip within 30.48 m of the WATER'S EDGE, on both sides
    of the edge (the bank buffered outward and inward), never a centre line.

It is a HELPER. It writes reports into its own output folder only and never edits
the club's live files (keys, outlines, 2-fers, site).

Exit codes: 0 = done, 3 = not finished (run again with --resume), 2 = bad input.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import logging
import os
import re
import sys
import time
import unicodedata
import urllib.parse
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable

import requests
from pyproj import Transformer
import shapely
from shapely.geometry import (GeometryCollection, LineString, MultiLineString,
                              MultiPolygon, Point, Polygon, box, mapping, shape)
from shapely.ops import unary_union
from shapely.validation import make_valid

TOOL = "river-banks"
USER_AGENT = f"KPC-{TOOL} (https://github.com/KentuckyPortableClub)"
BAND_M = 30.48          # 100 ft
MATCH_M = 200.0         # spec: touching the trail line within 200 m
PAD_M = 1000.0          # spec: bbox + 1 km
SIMPLIFY_M = 1.0        # spec: simplify to 1 m
TOUCH_M = 1.0           # "touching" another kept polygon / the river's own line
CENTER_ONLY_HALF_M = 0.0  # a stretch with only a centre point: the window is the point + 1 km
EXIT_DONE, EXIT_NOT_FINISHED, EXIT_BAD_INPUT = 0, 3, 2

STATUS_OK = "OK"
STATUS_LINE = "LINE ONLY"
STATUS_NOSRC = "NO OFFICIAL BANK SOURCE"
STATUS_DOWN = "SOURCE DOWN"
STATUS_CANT = "CAN'T TELL"   # house rule wording, used when the official layer shows no such water
FINAL_STATUSES = {STATUS_OK, STATUS_LINE, STATUS_NOSRC, STATUS_CANT}

# The club's live files: this tool refuses to write into them.
LIVE_NAMES = {"us-key", "ca-key", "world-key", "ky-answer-key.json", "canada-bounds",
              "world-bounds", "fers", "parkinfo", "trails"}

log = logging.getLogger("kpc12")


class SourceDown(Exception):
    """An official source did not answer (after polite retries)."""


class BadInput(Exception):
    """The stretches file is unusable."""


# --------------------------------------------------------------------------- HTTP

class Fetcher:
    """Polite HTTP: 1 request/second/host, KPC User-Agent, back-off on 429/5xx,
    and a dated on-disk cache. Only data/API endpoints are read (no web pages),
    so robots.txt does not come into play; `page=True` fetches check it."""

    def __init__(self, cache_dir: Path, cache_days: float = 30.0, offline: bool = False,
                 min_gap_s: float = 1.0, retries: int = 4, timeout: float = 90.0):
        self.cache_dir = Path(cache_dir)
        (self.cache_dir / "http").mkdir(parents=True, exist_ok=True)
        (self.cache_dir / "big").mkdir(parents=True, exist_ok=True)
        self.cache_days = cache_days
        self.offline = offline
        self.min_gap_s = min_gap_s
        self.retries = retries
        self.timeout = timeout
        self._last: dict[str, float] = {}
        self._robots: dict[str, Any] = {}
        self.s = requests.Session()
        self.s.headers["User-Agent"] = USER_AGENT
        self.requests_made = 0
        self.opts_keep_raw = False

    # -- politeness
    def _wait(self, url: str) -> None:
        host = urllib.parse.urlsplit(url).netloc
        gap = time.monotonic() - self._last.get(host, -1e9)
        if gap < self.min_gap_s:
            time.sleep(self.min_gap_s - gap)
        self._last[host] = time.monotonic()

    def _robots_ok(self, url: str) -> bool:
        import urllib.robotparser
        parts = urllib.parse.urlsplit(url)
        root = f"{parts.scheme}://{parts.netloc}"
        if root not in self._robots:
            rp = urllib.robotparser.RobotFileParser()
            try:
                r = self._request("GET", root + "/robots.txt")
                rp.parse(r.text.splitlines() if r.status_code == 200 else [])
            except SourceDown:
                rp.parse([])
            self._robots[root] = rp
        return self._robots[root].can_fetch(USER_AGENT, url)

    def _request(self, method: str, url: str, **kw) -> requests.Response:
        if self.offline:
            raise SourceDown(f"offline mode, not in cache: {url[:120]}")
        delay = 2.0
        last_err = ""
        for attempt in range(self.retries + 1):
            self._wait(url)
            try:
                self.requests_made += 1
                r = self.s.request(method, url, timeout=self.timeout, **kw)
            except requests.RequestException as e:
                last_err = f"{type(e).__name__}"
            else:
                if r.status_code == 429 or r.status_code >= 500:
                    last_err = f"HTTP {r.status_code}"
                    ra = r.headers.get("Retry-After")
                    if ra and ra.isdigit():
                        delay = max(delay, min(float(ra), 120.0))
                else:
                    return r
            if attempt < self.retries:
                time.sleep(delay)
                delay = min(delay * 2, 120.0)
        raise SourceDown(f"{last_err} from {urllib.parse.urlsplit(url).netloc}")

    # -- cached JSON GET
    def _key(self, url: str) -> Path:
        return self.cache_dir / "http" / (hashlib.sha1(url.encode()).hexdigest() + ".json")

    def get_json(self, url: str, params: dict | None = None, max_age_days: float | None = None,
                 page: bool = False) -> tuple[Any, str]:
        """Return (json, read_date 'YYYY-MM-DD')."""
        full = url + ("?" + urllib.parse.urlencode(params, safe=",:") if params else "")
        p = self._key(full)
        age_limit = self.cache_days if max_age_days is None else max_age_days
        if p.exists():
            try:
                c = json.loads(p.read_text())
                read = dt.datetime.fromisoformat(c["read_at"])
                if self.offline or (dt.datetime.now(dt.timezone.utc) - read).total_seconds() < age_limit * 86400:
                    return c["body"], read.date().isoformat()
            except Exception:
                pass
        if page and not self._robots_ok(full):
            raise SourceDown(f"robots.txt says no for {full[:100]}")
        r = self._request("GET", full)
        if r.status_code >= 400:
            raise SourceDown(f"HTTP {r.status_code} from {urllib.parse.urlsplit(url).netloc}")
        try:
            body = r.json()
        except ValueError:
            raise SourceDown(f"not JSON from {urllib.parse.urlsplit(url).netloc}")
        if isinstance(body, dict) and "error" in body and not body.get("features"):
            raise SourceDown(f"service error from {urllib.parse.urlsplit(url).netloc}: {str(body['error'])[:80]}")
        now = dt.datetime.now(dt.timezone.utc)
        tmp = p.with_suffix(".tmp")
        tmp.write_text(json.dumps({"url": full, "read_at": now.isoformat(), "body": body}))
        tmp.replace(p)
        return body, now.date().isoformat()

    # -- big files: pull single members out of a remote zip with HTTP range reads
    def zip_members(self, url: str, members: Iterable[str], dest: Path) -> str:
        """Download only the named members of a (huge) remote zip into dest.
        Returns the read date. Members already in dest are kept (cache)."""
        dest.mkdir(parents=True, exist_ok=True)
        stamp = dest / "_read_date.txt"
        want = [m for m in members if not (dest / _flat(m)).exists()]
        if not want:
            return stamp.read_text().strip() if stamp.exists() else "unknown"
        if self.offline:
            raise SourceDown("offline mode and the big file is not in the cache")
        rf = _RangeFile(self, url)
        with zipfile.ZipFile(rf) as z:
            names = {i.filename: i for i in z.infolist()}
            for m in want:
                if m not in names:
                    raise SourceDown(f"{m} not found inside {url.rsplit('/', 1)[-1]}")
                out = dest / _flat(m)
                tmp = out.with_suffix(out.suffix + ".part")
                with z.open(names[m]) as src, open(tmp, "wb") as dst:
                    while True:
                        b = src.read(1 << 22)
                        if not b:
                            break
                        dst.write(b)
                tmp.replace(out)
        today = dt.date.today().isoformat()
        stamp.write_text(today)
        return today


def _flat(member: str) -> str:
    return member.replace("\\", "/").rsplit("/", 1)[-1]


class _RangeFile:
    """A read-only, seekable file over HTTP range requests (big reads in 8 MB blocks)."""
    BLOCK = 8 << 20

    def __init__(self, f: Fetcher, url: str):
        self.f, self.url, self.pos = f, url, 0
        r = f._request("HEAD", url, allow_redirects=True)
        if r.status_code >= 400 or "content-length" not in r.headers:
            raise SourceDown(f"HTTP {r.status_code} from {urllib.parse.urlsplit(url).netloc}")
        self.size = int(r.headers["content-length"])
        self._buf_start, self._buf = -1, b""

    def seekable(self): return True
    def readable(self): return True
    def tell(self): return self.pos

    def seek(self, off, whence=0):
        self.pos = off if whence == 0 else (self.pos + off if whence == 1 else self.size + off)
        return self.pos

    def read(self, n=-1):
        if n is None or n < 0:
            n = self.size - self.pos
        n = min(n, self.size - self.pos)
        if n <= 0:
            return b""
        bs, be = self._buf_start, self._buf_start + len(self._buf)
        if bs <= self.pos and self.pos + n <= be:
            out = self._buf[self.pos - bs:self.pos - bs + n]
        else:
            want = max(n, self.BLOCK) if n < self.BLOCK else n
            end = min(self.size, self.pos + want) - 1
            r = self.f._request("GET", self.url, headers={"Range": f"bytes={self.pos}-{end}"})
            if r.status_code not in (200, 206):
                raise SourceDown(f"HTTP {r.status_code} on a range read")
            self._buf_start, self._buf = self.pos, r.content
            out = self._buf[:n]
        self.pos += len(out)
        return out


# --------------------------------------------------------------------------- names

_STOP = {"the", "la", "le", "les", "l", "de", "du", "des", "d", "of", "et", "and", "a", "au", "aux"}
_RIVER_WORDS = {"river", "riviere", "fleuve", "fluss", "rio", "r", "creek", "brook", "stream",
                "ruisseau", "bach", "rhein"} - {"rhein"}
_STILL_WORDS = {"lake", "lac", "see", "lago", "reservoir", "pond", "bassin", "etang", "lagoon",
                "loch", "lough", "mare", "basin"}


def _fold(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c)).lower()


def name_core(name: str) -> tuple[frozenset, bool]:
    """('cowichan',), is_still_water. Generic river words and little words drop out."""
    toks = re.findall(r"[a-z0-9]+", _fold(name or ""))
    still = any(t in _STILL_WORDS for t in toks)
    core = frozenset(t for t in toks if t not in _STOP and t not in _RIVER_WORDS and t not in _STILL_WORDS)
    return core, still


def split_names(raw: Any) -> list[str]:
    """A name field may hold several names ('Aare | L'Aar', 'A / B')."""
    if raw is None:
        return []
    out = []
    for part in re.split(r"\s*[|/;]\s*", str(raw)):
        part = part.strip()
        if part and part.lower() not in {"<nul>", "none", "null", "unnamed", "sans nom"}:
            out.append(part)
    return out


def names_match(wanted: Iterable[str], found: Iterable[str]) -> bool:
    w = [name_core(n) for n in wanted if n]
    for f in found:
        fc, fs = name_core(f)
        if not fc:
            continue
        for wc, ws in w:
            if wc and wc == fc and ws == fs:
                return True
    return False


# --------------------------------------------------------------------------- geometry helpers

def utm_epsg(lon: float, lat: float) -> int:
    zone = int((lon + 180) // 6) + 1
    zone = min(max(zone, 1), 60)
    return (32600 if lat >= 0 else 32700) + zone


class Proj:
    def __init__(self, lon: float, lat: float):
        self.epsg = utm_epsg(lon, lat)
        self.fwd = Transformer.from_crs(4326, self.epsg, always_xy=True)
        self.inv = Transformer.from_crs(self.epsg, 4326, always_xy=True)

    def to_m(self, g):
        return shapely.transform(g, lambda xy: _tx(self.fwd, xy))

    def to_ll(self, g):
        return shapely.transform(g, lambda xy: _tx(self.inv, xy))


def _tx(t: Transformer, xy):
    import numpy as np
    x, y = t.transform(xy[:, 0], xy[:, 1])
    return np.column_stack([x, y])


def polygonal(g) -> Polygon | MultiPolygon | None:
    if g is None or g.is_empty:
        return None
    if not g.is_valid:
        g = make_valid(g)
    if isinstance(g, (Polygon, MultiPolygon)):
        return g
    if isinstance(g, GeometryCollection):
        polys = [p for p in g.geoms if isinstance(p, (Polygon, MultiPolygon)) and not p.is_empty]
        return unary_union(polys) if polys else None
    return None


def lineal(g):
    if g is None or g.is_empty:
        return None
    if isinstance(g, (LineString, MultiLineString)):
        return g
    if isinstance(g, GeometryCollection):
        ls = [p for p in g.geoms if isinstance(p, (LineString, MultiLineString))]
        return unary_union(ls) if ls else None
    if isinstance(g, (Polygon, MultiPolygon)):
        return g.boundary
    return None


def round_geom(g, nd: int = 7):
    return shapely.set_precision(g, 10 ** -nd) if g is not None and not g.is_empty else g


def parse_line(obj: Any, base_dir: Path | None = None):
    """Accepts a GeoJSON geometry / Feature / FeatureCollection, a list of [lon, lat]
    points, a list of such lists, or a path to a club trails/<ref>.json file."""
    if obj is None:
        return None
    if isinstance(obj, str):
        p = Path(obj)
        if not p.is_absolute() and base_dir is not None:
            p = base_dir / p
        obj = json.loads(p.read_text())
    if isinstance(obj, dict):
        t = obj.get("type")
        if t == "Feature":
            return parse_line(obj.get("geometry"))
        if t == "FeatureCollection":
            parts = [parse_line(f) for f in obj.get("features", [])]
            parts = [p for p in parts if p is not None]
            return unary_union(parts) if parts else None
        return lineal(shape(obj))
    if isinstance(obj, list) and obj:
        if isinstance(obj[0][0], (int, float)):
            return LineString(obj) if len(obj) >= 2 else None
        parts = [LineString(p) for p in obj if len(p) >= 2]
        return MultiLineString(parts) if parts else None
    raise ValueError("line is not a geometry, a coordinate list or a file path")


# --------------------------------------------------------------------------- sources

@dataclass
class Water:
    geom: Any                      # shapely, EPSG:4326
    names: list[str]
    fid: str = ""
    kind: str = ""


@dataclass
class Found:
    polys: list[Water]
    lines: list[Water]
    read_date: str


@dataclass
class Source:
    key: str
    title: str
    owner: str
    licence: str
    url: str
    grade: str = "official"
    note: str = ""
    fetch: Callable[["Source", Fetcher, tuple, dict], Found] | None = None
    opts: dict = field(default_factory=dict)


def _arcgis_query(f: Fetcher, layer_url: str, bbox: tuple, out_fields: str, where: str = "1=1",
                  page: int = 1000, max_pages: int = 40) -> tuple[list[dict], str]:
    feats, offset, read = [], 0, ""
    for _ in range(max_pages):
        params = {
            "where": where, "geometry": ",".join(f"{v:.6f}" for v in bbox),
            "geometryType": "esriGeometryEnvelope", "inSR": "4326",
            "spatialRel": "esriSpatialRelIntersects", "outFields": out_fields,
            "returnGeometry": "true", "outSR": "4326", "f": "geojson",
            "resultOffset": str(offset), "resultRecordCount": str(page),
        }
        body, read = f.get_json(layer_url + "/query", params)
        got = body.get("features", []) if isinstance(body, dict) else []
        feats.extend(got)
        more = body.get("exceededTransferLimit") or (body.get("properties") or {}).get("exceededTransferLimit")
        if not more or not got:
            break
        offset += len(got)
    return feats, read


def _wfs_get(f: Fetcher, url: str, typename: str, bbox: tuple, extra: dict | None = None,
             page: int = 1000, max_pages: int = 40, lat_first: bool = True) -> tuple[list[dict], str]:
    w, s, e, n = bbox
    bb = f"{s:.6f},{w:.6f},{n:.6f},{e:.6f},urn:ogc:def:crs:EPSG::4326" if lat_first else \
         f"{w:.6f},{s:.6f},{e:.6f},{n:.6f},urn:ogc:def:crs:EPSG::4326"
    feats, start, read = [], 0, ""
    for _ in range(max_pages):
        params = {"service": "WFS", "version": "2.0.0", "request": "GetFeature",
                  "typeNames": typename, "outputFormat": "application/json",
                  "srsName": "EPSG:4326", "bbox": bb, "count": str(page), "startIndex": str(start)}
        if extra:
            params.update(extra)
        body, read = f.get_json(url, params)
        got = body.get("features", []) if isinstance(body, dict) else []
        feats.extend(got)
        if len(got) < page:
            break
        start += len(got)
    return feats, read


def _to_water(feats: list[dict], name_fields: list[str], keep: Callable[[dict], bool] | None = None,
              kind_field: str | None = None, id_field: str | None = None, want: str = "poly") -> list[Water]:
    out = []
    for ft in feats:
        g = ft.get("geometry")
        if not g:
            continue
        props = ft.get("properties") or {}
        if keep and not keep(props):
            continue
        try:
            geom = shape(g)
        except Exception:
            continue
        geom = polygonal(geom) if want == "poly" else lineal(geom)
        if geom is None or geom.is_empty:
            continue
        names = []
        for nf in name_fields:
            names += split_names(props.get(nf))
        out.append(Water(geom, names, str(props.get(id_field, ft.get("id", ""))) if id_field else str(ft.get("id", "")),
                         str(props.get(kind_field, "")) if kind_field else ""))
    return out


# ---- Canada

BC_WFS = "https://openmaps.gov.bc.ca/geo/pub/wfs"


def fetch_bc(src: Source, f: Fetcher, bbox: tuple, st: dict) -> Found:
    polys, read = [], ""
    for tn in ("WHSE_BASEMAPPING.FWA_RIVERS_POLY", "WHSE_BASEMAPPING.FWA_LAKES_POLY",
               "WHSE_BASEMAPPING.FWA_MANMADE_WATERBODIES_POLY"):
        feats, read = _wfs_get(f, BC_WFS, tn, bbox)
        polys += _to_water(feats, ["GNIS_NAME_1", "GNIS_NAME_2", "GNIS_NAME_3"], id_field="WATERBODY_KEY",
                           kind_field="FEATURE_CODE")
    feats, read = _wfs_get(f, BC_WFS, "WHSE_BASEMAPPING.FWA_STREAM_NETWORKS_SP", bbox,
                           extra={"propertyName": "GNIS_NAME,LINEAR_FEATURE_ID,GEOMETRY"})
    lines = _to_water(feats, ["GNIS_NAME"], id_field="LINEAR_FEATURE_ID", want="line")
    return Found(polys, lines, read)


OHN = "https://ws.lioservices.lrc.gov.on.ca/arcgis2/rest/services/LIO_OPEN_DATA/LIO_Open01/MapServer"


def fetch_on(src: Source, f: Fetcher, bbox: tuple, st: dict) -> Found:
    feats, read = _arcgis_query(f, OHN + "/25", bbox, "OBJECTID,OFFICIAL_NAME_LABEL,WATERBODY_TYPE")
    polys = _to_water(feats, ["OFFICIAL_NAME_LABEL"], id_field="OBJECTID", kind_field="WATERBODY_TYPE",
                      keep=lambda p: (p.get("WATERBODY_TYPE") or "").lower() not in {"wetland", "marsh"})
    feats, read2 = _arcgis_query(f, OHN + "/26", bbox, "OBJECTID,OFFICIAL_NAME_LABEL,WATERCOURSE_TYPE")
    lines = _to_water(feats, ["OFFICIAL_NAME_LABEL"], id_field="OBJECTID", want="line")
    return Found(polys, lines, read or read2)


GRHQ = "https://servicescarto.mrnf.gouv.qc.ca/pes/rest/services/Territoire/GRHQ_HR_REST/MapServer"
# TYPECE: 10 river, 21 lake, 22 pool, 23 reservoir, 42 canal, 48 lock, 51 estuary (wetland / theoretical left out)
GRHQ_WATER = {10, 21, 22, 23, 42, 48, 51}


def fetch_qc(src: Source, f: Fetcher, bbox: tuple, st: dict) -> Found:
    feats, read = _arcgis_query(f, GRHQ + "/1", bbox, "OBJECTID,TOPONYME,TYPECE")
    polys = _to_water(feats, ["TOPONYME"], id_field="OBJECTID", kind_field="TYPECE",
                      keep=lambda p: p.get("TYPECE") in GRHQ_WATER)
    feats, _ = _arcgis_query(f, GRHQ + "/0", bbox, "OBJECTID,TOPONYME,TYPECE")
    lines = _to_water(feats, ["TOPONYME"], id_field="OBJECTID", want="line")
    return Found(polys, lines, read)


CHN = "https://maps-cartes.services.geo.ca/server_serveur/rest/services/NRCan/chn_en/MapServer"


def fetch_chn(src: Source, f: Fetcher, bbox: tuple, st: dict) -> Found:
    feats, read = _arcgis_query(f, CHN + "/12", bbox, "OBJECTID,name_en,name_fr,feature_type_en")
    polys = _to_water(feats, ["name_en", "name_fr"], id_field="OBJECTID", kind_field="feature_type_en",
                      keep=lambda p: "wetland" not in str(p.get("feature_type_en", "")).lower())
    feats, _ = _arcgis_query(f, CHN + "/5", bbox, "OBJECTID,name_en,name_fr")
    lines = _to_water(feats, ["name_en", "name_fr"], id_field="OBJECTID", want="line")
    return Found(polys, lines, read)


def fetch_nhn_local(src: Source, f: Fetcher, bbox: tuple, st: dict) -> Found:
    """NHN GeoPackage the club downloaded (national file stays in the cache, never in the output)."""
    path = src.opts.get("path")
    if not path or not Path(path).exists():
        return Found([], [], "")
    import pyogrio
    polys, lines = [], []
    for layer in pyogrio.list_layers(path)[:, 0]:
        lname = str(layer).upper()
        if "WATERBODY" not in lname and "SLWATER" not in lname:
            continue
        cols = [c for c in pyogrio.read_info(path, layer=layer)["fields"]]
        meta, _, geoms, fields = pyogrio.raw.read(path, layer=layer, bbox=bbox, return_fids=False)
        names_idx = [i for i, c in enumerate(cols) if c.lower().startswith(("name", "geonamedb", "nameen", "namefr"))]
        crs = meta.get("crs")
        tr = Transformer.from_crs(crs, 4326, always_xy=True) if crs and "4326" not in str(crs) else None
        for k, wkb in enumerate(geoms):
            if wkb is None:
                continue
            g = shapely.from_wkb(wkb)
            if tr is not None:
                g = shapely.transform(g, lambda xy: _tx(tr, xy))
            nm = []
            for i in names_idx:
                nm += split_names(fields[i][k])
            pg = polygonal(g)
            if pg is not None:
                polys.append(Water(pg, nm, f"{layer}:{k}"))
    mt = dt.date.fromtimestamp(Path(path).stat().st_mtime).isoformat()
    return Found(polys, lines, mt)


# ---- Europe

GEOADMIN = "https://api3.geo.admin.ch/rest/services/api/MapServer"
TLM_STAC = "https://data.geo.admin.ch/api/stac/v0.9/collections/ch.swisstopo.swisstlm3d/items"
TLM_WATER = ("Fliessgewaesser", "Stehende Gewaesser")


def _tlm_latest_shp_zip(f: Fetcher) -> str:
    body, _ = f.get_json(TLM_STAC, {"limit": "100"}, max_age_days=30)
    items = sorted(body.get("features", []), key=lambda it: it.get("id", ""))
    for it in reversed(items):
        for a in it.get("assets", {}).values():
            href = a.get("href", "")
            if href.endswith(".shp.zip"):
                return href
    raise SourceDown("swisstopo STAC lists no swissTLM3D shapefile zip")


def _tlm_water_gpkg(f: Fetcher) -> tuple[Path, str]:
    """swissTLM3D land cover (TLM_BODENBEDECKUNG) water polygons, cut once from the
    national file into a small cached GeoPackage. The national file never reaches the output."""
    import pyogrio
    big = f.cache_dir / "big" / "swisstlm3d"
    out = big / "tlm_water.gpkg"
    stamp = big / "tlm_water_read_date.txt"
    if out.exists() and stamp.exists():
        return out, stamp.read_text().strip()
    url = _tlm_latest_shp_zip(f)
    raw = big / "raw"
    parts = []
    for half in ("WEST", "OST"):
        base = f"TLM_BB\\swissTLM3D_TLM_BODENBEDECKUNG_{half}"
        members = [base + ext for ext in (".shp", ".shx", ".dbf", ".prj", ".CPG")]
        log.info("swissTLM3D: reading %s land cover from the national file (one time, cached)", half)
        read = f.zip_members(url, members, raw)
        parts.append(raw / _flat(base + ".shp"))
    where = "OBJEKTART IN ('" + "','".join(TLM_WATER) + "')"
    first = True
    for shp in parts:
        meta, _, geoms, fields = pyogrio.raw.read(str(shp), where=where, columns=["OBJEKTART", "UUID"],
                                                  encoding="UTF-8")
        pyogrio.raw.write(str(out), geometry=geoms, field_data=fields, fields=meta["fields"],
                          crs="EPSG:2056", geometry_type="Unknown", driver="GPKG", layer="water",
                          append=not first)
        first = False
    stamp.write_text(read)
    if not f.opts_keep_raw:
        for p in raw.glob("swissTLM3D_TLM_BODENBEDECKUNG_*"):
            p.unlink()
    return out, read


def fetch_ch(src: Source, f: Fetcher, bbox: tuple, st: dict) -> Found:
    import pyogrio
    gpkg, read = _tlm_water_gpkg(f)
    to_lv95 = Transformer.from_crs(4326, 2056, always_xy=True)
    to_ll = Transformer.from_crs(2056, 4326, always_xy=True)
    w, s, e, n = bbox
    xs, ys = to_lv95.transform([w, e, w, e], [s, s, n, n])
    bb = (min(xs), min(ys), max(xs), max(ys))
    meta, _, geoms, fields = pyogrio.raw.read(str(gpkg), layer="water", bbox=bb)
    col = {str(c): i for i, c in enumerate(meta["fields"])}   # field order follows the file, not the request
    polys = []
    for k, wkb in enumerate(geoms):
        if wkb is None:
            continue
        g = shapely.force_2d(shapely.from_wkb(wkb))
        g = shapely.transform(g, lambda xy: _tx(to_ll, xy))
        pg = polygonal(g)
        if pg is not None:
            polys.append(Water(pg, [], str(fields[col["UUID"]][k]), str(fields[col["OBJEKTART"]][k])))
    lines = []
    w_, s_, e_, n_ = bbox
    offset = 0
    for _ in range(20):
        params = {"geometryType": "esriGeometryEnvelope", "geometry": f"{w_},{s_},{e_},{n_}", "sr": "4326",
                  "imageDisplay": "1000,1000,96", "mapExtent": f"{w_},{s_},{e_},{n_}", "tolerance": "0",
                  "layers": "all:ch.swisstopo.swisstlm3d-gewaessernetz", "returnGeometry": "true",
                  "geometryFormat": "geojson", "limit": "200", "offset": str(offset), "lang": "de"}
        body, _ = f.get_json(GEOADMIN + "/identify", params)
        res = body.get("results", [])
        lines += _to_water(res, ["name"], id_field="gwl_nr", want="line")
        if len(res) < 200:
            break
        offset += len(res)
    return Found(polys, lines, read)


GEOPF_WFS = "https://data.geopf.fr/wfs/ows"


def fetch_fr(src: Source, f: Fetcher, bbox: tuple, st: dict) -> Found:
    feats, read = _wfs_get(f, GEOPF_WFS, "BDTOPO_V3:troncon_hydrographique", bbox, lat_first=True)
    lines, surf_names = [], {}
    for ft in feats:
        p = ft.get("properties") or {}
        nm = split_names(p.get("cpx_toponyme_de_cours_d_eau"))
        for sid in str(p.get("liens_vers_surface_hydrographique") or "").split("/"):
            if sid and nm:
                surf_names.setdefault(sid, set()).update(nm)
    lines = _to_water(feats, ["cpx_toponyme_de_cours_d_eau"], id_field="cleabs", want="line")
    feats, read = _wfs_get(f, GEOPF_WFS, "BDTOPO_V3:surface_hydrographique", bbox, lat_first=True)
    polys = []
    for w in _to_water(feats, ["cpx_toponyme_de_cours_d_eau", "cpx_toponyme_de_plan_d_eau"], id_field="cleabs",
                       kind_field="nature", keep=lambda p: "glacier" not in str(p.get("nature", "")).lower()):
        if not w.names and w.fid in surf_names:
            w.names = sorted(surf_names[w.fid])
        polys.append(w)
    return Found(polys, lines, read)


EUHYDRO = "https://image.discomap.eea.europa.eu/arcgis/rest/services/EUHydro/EUHydro_RiverNetworkDatabase/MapServer"


def fetch_euhydro(src: Source, f: Fetcher, bbox: tuple, st: dict) -> Found:
    feats, read = _arcgis_query(f, EUHYDRO + "/19", bbox, "OBJECTID,OBJECT_ID,DFDD")
    polys = _to_water(feats, [], id_field="OBJECT_ID", kind_field="DFDD")
    feats, _ = _arcgis_query(f, EUHYDRO + "/2", bbox, "OBJECTID,OBJECT_ID,NAM,DFDD")
    polys += _to_water(feats, ["NAM"], id_field="OBJECT_ID", kind_field="DFDD")
    lines = []
    for lid in range(5, 14):
        feats, _ = _arcgis_query(f, EUHYDRO + f"/{lid}", bbox, "OBJECTID,OBJECT_ID,nameText")
        lines += _to_water(feats, ["nameText"], id_field="OBJECT_ID", want="line")
    return Found(polys, lines, read)


# ---- Australia

GA = "https://services.ga.gov.au/gis/rest/services/Surface_Hydrology/MapServer"
GA_WATER = {"watercourse area", "lake", "reservoir", "canal area", "pondage area", "town rural storage"}


def fetch_au(src: Source, f: Fetcher, bbox: tuple, st: dict) -> Found:
    feats, read = _arcgis_query(f, GA + "/4", bbox, "objectid,name,featuretype")
    polys = _to_water(feats, ["name"], id_field="objectid", kind_field="featuretype",
                      keep=lambda p: str(p.get("featuretype", "")).lower() in GA_WATER)
    feats, _ = _arcgis_query(f, GA + "/2", bbox, "objectid,name,featuretype")
    lines = _to_water(feats, ["name"], id_field="objectid", want="line")
    return Found(polys, lines, read)


OGL_CA = "Open Government Licence - Canada"
SOURCES: dict[str, Source] = {
    "bc_fwa": Source("bc_fwa", "BC Freshwater Atlas (FWA_RIVERS_POLY, FWA_LAKES_POLY, FWA_MANMADE_WATERBODIES_POLY; lines FWA_STREAM_NETWORKS_SP)",
                     "Province of British Columbia (GeoBC)", "Open Government Licence - British Columbia",
                     BC_WFS, note="1:20,000; finest official water for BC.", fetch=fetch_bc),
    "on_ohn": Source("on_ohn", "Ontario Hydro Network (OHN) Waterbody; lines OHN Watercourse",
                     "Ontario Ministry of Natural Resources (Land Information Ontario)", "Open Government Licence - Ontario",
                     OHN + "/25", note="1:10,000 south, 1:20,000 north, 1:50,000 far north.", fetch=fetch_on),
    "qc_grhq": Source("qc_grhq", "Geobase du reseau hydrographique du Quebec (GRHQ-HR) Hydrographie surfacique; lines Hydrographie lineaire",
                      "Gouvernement du Quebec (MRNF / MELCCFP)", "Creative Commons Attribution 4.0 (CC BY 4.0)",
                      GRHQ + "/1", note="1:20,000 south (BDTQ), 1:50,000 north; wetlands left out.", fetch=fetch_qc),
    "ca_chn": Source("ca_chn", "Canadian Hydrospatial Network (CHN, NRCan; the NHN's successor) Waterbody; lines Flowline (large-scale)",
                     "Natural Resources Canada", OGL_CA, CHN + "/12",
                     note="National; only the work units NRCan has finished. Used where no finer provincial layer is wired.",
                     fetch=fetch_chn),
    "ca_nhn": Source("ca_nhn", "National Hydro Network (NHN) GeoBase waterbodies (local GeoPackage given with --nhn-gpkg)",
                     "Natural Resources Canada", OGL_CA,
                     "https://ftp.maps.canada.ca/pub/nrcan_rncan/vector/geobase_nhn_rhn/gpkg_en/CA/",
                     note="NRCan offers NHN only as a 3.5 GB national download or a picture service (WMS), so the club downloads it once.",
                     fetch=fetch_nhn_local),
    "ch_tlm": Source("ch_tlm", "swisstopo swissTLM3D land cover (TLM_BODENBEDECKUNG: Fliessgewaesser, Stehende Gewaesser); lines swissTLM3D Gewaessernetz",
                     "Federal Office of Topography swisstopo", "swisstopo Open Government Data (free use, source must be named: \u00a9 swisstopo)",
                     "https://data.geo.admin.ch/ch.swisstopo.swisstlm3d/",
                     note="1-3 m. Read once from the national download (about 1 GB of the 3.3 GB zip) and cut to water only in the cache.",
                     fetch=fetch_ch),
    "fr_bdtopo": Source("fr_bdtopo", "IGN BD TOPO V3 hydrography = BD TOPAGE (surface_hydrographique; lines troncon_hydrographique)",
                        "Institut national de l'information geographique et forestiere (IGN) with OFB", "Licence Ouverte Etalab 2.0",
                        GEOPF_WFS, note="Metre-level; BD TOPAGE is the hydro theme of BD TOPO.", fetch=fetch_fr),
    "eu_hydro": Source("eu_hydro", "EU-Hydro River Network Database v1.3 (River_Net_polygon + InlandWater; lines River_Net_lines)",
                       "European Environment Agency / Copernicus Land Monitoring Service",
                       "Copernicus data policy (free, full and open; credit Copernicus / EEA)", EUHYDRO + "/19",
                       grade="Approximate (EU compilation)",
                       note="Photo-interpreted 2006-2012, coarser than national layers. Used only where no national layer is wired.",
                       fetch=fetch_euhydro),
    "au_ga": Source("au_ga", "Geoscience Australia Surface Hydrology Polygons (National); lines Surface Hydrology Lines (National)",
                    "Geoscience Australia", "Creative Commons Attribution 4.0 International", GA + "/4",
                    note="Compiled from state agencies; 'Land Subject to Inundation' and swamps left out.", fetch=fetch_au),
}

# EEA39 countries that EU-Hydro covers (ISO codes as POTA uses them).
EEA39 = set("AL AT BA BE BG CH CY CZ DE DK EE ES FI FR GR HR HU IE IS IT LI LT LU LV ME MK MT NL NO PL PT RO RS SE SI SK TR GB XK".split())

NO_SOURCE_WHY = {
    "NZ": "LINZ river polygons need an API key and the spec names none, so they are not read.",
    "JP": "GSI water areas are published only as map tiles, and this tool has no reader for them yet.",
    "GB": "Ordnance Survey Open Rivers is lines only and OS MasterMap water is not open data, so UK stretches get EU-Hydro (Approximate) instead.",
    "US": "US stretches use the club's own USGS NHD reader, not this tool.",
}


def route(country: str, prov: str | None) -> list[str]:
    """Which official sources to try, finest first."""
    c = (country or "").upper()
    p = (prov or "").upper()
    if c == "CA":
        chain = {"CA-BC": ["bc_fwa"], "CA-ON": ["on_ohn"], "CA-QC": ["qc_grhq"]}.get(p, [])
        return chain + ["ca_chn", "ca_nhn"]
    if c == "CH":
        return ["ch_tlm"]
    if c == "FR":
        return ["fr_bdtopo"]
    if c == "AU":
        return ["au_ga"]
    if c in EEA39:   # incl. GB: OS has no open water polygons, see NO_SOURCE_WHY
        return ["eu_hydro"]
    return []


# --------------------------------------------------------------------------- one stretch

@dataclass
class Result:
    id: str
    refs: list[str]
    source: str
    status: str
    why: str
    details: dict = field(default_factory=dict)


def window_for(st: dict, line) -> tuple[float, float, float, float]:
    """lon/lat bbox of the stretch (its bbox, else its line, else its centre)."""
    if st.get("bbox"):
        b = [float(v) for v in st["bbox"]]
        if len(b) != 4:
            raise ValueError("bbox must be [west, south, east, north]")
        w, s, e, n = b
        if s > n or abs(s) > 90 or abs(n) > 90:  # given as [s, w, n, e]? refuse rather than guess
            raise ValueError("bbox must be [west, south, east, north] in degrees")
        return (w, s, e, n)
    if line is not None:
        return line.bounds
    lat, lon = st["center"]
    return (lon, lat, lon, lat)


def build_bank(st: dict, found: Found, line_ll, proj: Proj, win_m) -> dict:
    """Pick the river's polygons, merge, repair, simplify, and make the band. Pure geometry."""
    wanted = [st.get("river") or st.get("river_name") or ""] + list(st.get("also_names") or [])
    wanted = [w for w in wanted if w]
    line_m = proj.to_m(line_ll) if line_ll is not None else None
    if line_m is not None:
        line_m = line_m.intersection(win_m.buffer(MATCH_M))
        if line_m.is_empty:
            line_m = None
    # the river's own official centre line(s), by name
    river_lines = [proj.to_m(l.geom) for l in found.lines if wanted and names_match(wanted, l.names)]
    river_line_m = unary_union(river_lines).intersection(win_m.buffer(MATCH_M)) if river_lines else None
    if river_line_m is not None and river_line_m.is_empty:
        river_line_m = None
    ref_line = line_m if line_m is not None else river_line_m

    kept, cands, out_named, out_far = [], [], [], 0
    for wtr in found.polys:
        g = polygonal(proj.to_m(wtr.geom))
        if g is None:
            continue
        if wtr.names:
            if wanted and names_match(wanted, wtr.names):
                kept.append(g)
            elif g.distance(ref_line if ref_line is not None else win_m) <= MATCH_M:
                out_named.append(wtr.names[0])
        else:
            if ref_line is not None and g.distance(ref_line) <= MATCH_M:
                cands.append(g)
            else:
                out_far += 1
    # unnamed water near the line: keep it when the river's own line runs through it or it
    # joins water already kept; a pond that only sits near the line stays out.
    guard = river_line_m is not None or bool(kept)
    dropped_ponds = 0
    if guard:
        changed = True
        pool = cands[:]
        while changed and pool:
            changed = False
            base = unary_union(kept) if kept else None
            rest = []
            for g in pool:
                through = river_line_m is not None and g.distance(river_line_m) <= TOUCH_M
                joins = base is not None and g.distance(base) <= TOUCH_M
                if through or joins:
                    kept.append(g)
                    changed = True
                    base = unary_union(kept)
                else:
                    rest.append(g)
            pool = rest
        dropped_ponds = len(pool)
    else:
        kept += cands

    det = {"wanted_names": wanted, "polygons_read": len(found.polys), "lines_read": len(found.lines),
           "polygons_kept": len(kept), "named_other_water_left_out": sorted(set(out_named))[:20],
           "unnamed_ponds_left_out": dropped_ponds, "river_line_found": river_line_m is not None,
           "trail_line_given": line_m is not None, "name_check_of_unnamed_water": "river line / joins kept water" if guard else "200 m only"}
    if not kept:
        det["line_m"] = river_line_m
        return det

    water = polygonal(make_valid(unary_union(kept)))
    water = polygonal(water.simplify(SIMPLIFY_M, preserve_topology=True))
    edge = water.boundary.intersection(win_m.buffer(100.0))
    band = polygonal(edge.buffer(BAND_M, quad_segs=8).intersection(win_m))
    water_w = polygonal(water.intersection(win_m))
    det.update({"water_m": water_w, "band_m": band})
    return det


def run_one(st: dict, fetcher: Fetcher, out_dir: Path, base_dir: Path, nhn_gpkg: str | None) -> Result:
    sid = str(st.get("id", "")).strip()
    refs = [str(r) for r in (st.get("refs") or [])]
    try:
        if not sid:
            raise ValueError("the row has no id")
        if not st.get("center") or len(st["center"]) != 2:
            raise ValueError("the row has no center [lat, lon]")
        lat, lon = float(st["center"][0]), float(st["center"][1])
        if abs(lat) > 90 or abs(lon) > 180:
            raise ValueError("center is not [lat, lon] in degrees")
        line_ll = parse_line(st.get("line"), base_dir) if st.get("line") is not None else None
        if line_ll is not None and line_ll.is_empty:
            line_ll = None
        w, s, e, n = window_for(st, line_ll)
    except Exception as ex:
        return Result(sid or "?", refs, "", STATUS_CANT, f"Bad row in the stretches file: {ex}.")

    country = (st.get("country") or (refs[0].split("-")[0] if refs and "-" in refs[0] else "")).upper()
    prov = st.get("prov") or st.get("province")
    if country == "CA" and not prov:
        try:
            prov = pota_prov(fetcher, refs)
        except SourceDown as ex:
            return Result(sid, refs, "POTA park page", STATUS_DOWN,
                          f"Could not read POTA's park page to learn the province ({ex}); will try again next run.")
    chain = route(country, prov)
    if not chain:
        why = NO_SOURCE_WHY.get(country, f"No official national water polygons are known for {country or 'this place'}.")
        return Result(sid, refs, "", STATUS_NOSRC, why)

    proj = Proj((w + e) / 2, (s + n) / 2)
    win_m = proj.to_m(box(w, s, e, n))
    win_m = win_m.envelope.buffer(PAD_M, join_style="mitre")
    win_ll = proj.to_ll(win_m)
    qbox = win_ll.bounds

    tried = []
    for key in chain:
        src = SOURCES[key]
        if key == "ca_nhn":
            src.opts["path"] = nhn_gpkg
            if not nhn_gpkg:
                tried.append("NHN download not given")
                continue
        try:
            found = src.fetch(src, fetcher, qbox, st)
        except SourceDown as ex:
            return Result(sid, refs, src.title.split(" (")[0], STATUS_DOWN,
                          f"{src.owner} did not answer ({ex}); will try again next run.")
        if not found.polys and not found.lines:
            tried.append(f"{src.title.split(' (')[0]} has no water here")
            continue
        det = build_bank(st, found, line_ll, proj, win_m)
        return finish(sid, refs, st, src, found, det, proj, out_dir)
    why = "; ".join(tried) if tried else "nothing to try"
    return Result(sid, refs, "", STATUS_CANT,
                  f"The official water layers show no water in this box ({why}).")


def finish(sid, refs, st, src: Source, found: Found, det: dict, proj: Proj, out_dir: Path) -> Result:
    river = (det["wanted_names"] or ["the river"])[0]
    base_props = {"id": sid, "refs": refs, "river": river, "source": src.title, "source_url": src.url,
                  "owner": src.owner, "licence": src.licence, "read_date": found.read_date, "grade": src.grade}
    short = src.title.split(" (")[0]
    safe = re.sub(r"[^A-Za-z0-9._+@-]", "_", sid)
    path = out_dir / "banks" / f"{safe}.geojson"
    public = {k: v for k, v in det.items() if not k.endswith("_m")}
    if det.get("water_m") is not None and det.get("band_m") is not None:
        water_ll = round_geom(proj.to_ll(det["water_m"]))
        band_ll = round_geom(proj.to_ll(det["band_m"]))
        feats = [
            {"type": "Feature", "geometry": mapping(water_ll),
             "properties": {**base_props, "part": "water", "method": "polygon",
                            "area_m2": round(det["water_m"].area)}},
            {"type": "Feature", "geometry": mapping(band_ll),
             "properties": {**base_props, "part": "band_100ft", "method": "polygon", "band_m": BAND_M,
                            "area_m2": round(det["band_m"].area),
                            "note": "within 100 ft (30.48 m) of the water's edge, both sides of the edge"}},
        ]
        write_geojson(path, feats, base_props)
        grade_note = "" if src.grade == "official" else f" Graded {src.grade}."
        extra = ""
        if det.get("named_other_water_left_out"):
            extra = f" Left out other named water nearby: {', '.join(det['named_other_water_left_out'][:3])}."
        why = (f"Bank of {river} from {short}, {det['polygons_kept']} official water polygon(s) merged; "
               f"band is 100 ft each side of the water's edge.{grade_note}{extra}")
        return Result(sid, refs, short, STATUS_OK, why, public)
    if det.get("line_m") is not None:
        line_ll = round_geom(proj.to_ll(det["line_m"]))
        feats = [{"type": "Feature", "geometry": mapping(line_ll),
                  "properties": {**base_props, "part": "centre_line", "method": "line-only",
                                 "note": "no official water polygon here: use the line rule and mark it so; no width is invented"}}]
        write_geojson(path, feats, base_props)
        why = (f"{short} maps {river} here as a centre line only (no water polygon), so the club uses the line rule.")
        return Result(sid, refs, short, STATUS_LINE, why, public)
    if path.exists():
        path.unlink()
    left = det.get("named_other_water_left_out") or []
    hint = f" Nearby named water: {', '.join(left[:3])}." if left else ""
    return Result(sid, refs, short, STATUS_CANT,
                  f"{short} has water here, but none of it is named {river} or joins the trail line.{hint}", public)


def write_geojson(path: Path, feats: list[dict], props: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fc = {"type": "FeatureCollection", "crs_note": "EPSG:4326 (lon, lat)", "properties": props, "features": feats}
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(fc, separators=(",", ":"), ensure_ascii=False))
    tmp.replace(path)


def pota_prov(f: Fetcher, refs: list[str]) -> str | None:
    for r in refs:
        if not r.upper().startswith("CA-"):
            continue
        body, _ = f.get_json(f"https://api.pota.app/park/{urllib.parse.quote(r)}", max_age_days=30)
        if isinstance(body, dict) and body.get("locationDesc"):
            return str(body["locationDesc"]).split(",")[0].strip()
    return None


# --------------------------------------------------------------------------- batch

def load_stretches(path: Path) -> list[dict]:
    try:
        data = json.loads(Path(path).read_text())
    except FileNotFoundError:
        raise BadInput(f"can't find {path}")
    except json.JSONDecodeError as e:
        raise BadInput(f"{path} is not valid JSON ({e.msg}, line {e.lineno})")
    if isinstance(data, dict) and isinstance(data.get("stretches"), list):
        data = data["stretches"]
    if not isinstance(data, list) or not all(isinstance(x, dict) for x in data):
        raise BadInput("stretches file must be a list of {id, refs, river, center, bbox or line}")
    ids = [str(x.get("id")) for x in data]
    dup = {i for i in ids if ids.count(i) > 1}
    if dup:
        raise BadInput(f"the same id is used twice: {', '.join(sorted(dup))}")
    return data


def check_out_dir(out: Path) -> None:
    parts = {p.lower() for p in out.resolve().parts}
    bad = parts & LIVE_NAMES
    if bad:
        raise BadInput(f"refusing to write inside the club's live files ({', '.join(sorted(bad))})")


def write_report(out: Path, rows: list[dict]) -> None:
    p = out / "banks" / "report.csv"
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    with open(tmp, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "refs", "source used", "status", "why"])
        for r in rows:
            w.writerow([r["id"], " ".join(r["refs"]), r["source"], r["status"], r["why"]])
    tmp.replace(p)


def write_sources_md(out: Path) -> None:
    lines = ["# Official water sources used by KPC 12 (river banks)", "",
             "Finest official layer first. Never OpenStreetMap, Google, or imagery-made global sets (JRC etc.).", "",
             "| Where | Source | Owner | Licence | Grade | Notes |", "|---|---|---|---|---|---|"]
    where = [("Canada: British Columbia", "bc_fwa"), ("Canada: Ontario", "on_ohn"), ("Canada: Quebec", "qc_grhq"),
             ("Canada: every province (fallback; AB, MB and the rest until their own layer is wired)", "ca_chn"),
             ("Canada: every province (second fallback)", "ca_nhn"),
             ("Switzerland", "ch_tlm"), ("France", "fr_bdtopo"),
             ("Other EEA39 countries (incl. UK)", "eu_hydro"), ("Australia", "au_ga")]
    for label, key in where:
        s = SOURCES[key]
        lines.append(f"| {label} | {s.title} | {s.owner} | {s.licence} | {s.grade} | {s.note} |")
    lines += ["", "## No national bank source read", ""]
    for c, why in NO_SOURCE_WHY.items():
        lines.append(f"- **{c}:** {why}")
    lines += ["- **Everywhere else:** no official national water polygons wired yet: NO OFFICIAL BANK SOURCE.", "",
              "## Not wired yet (finer national layers the club may add)", "",
              "- Alberta (GeoDiscover Alberta hydrography) and Manitoba (Manitoba Land Initiative) provincial hydro layers: CHN / NHN is used meanwhile.",
              "- Netherlands Kadaster TOP10NL, Sweden Lantmateriet, other national agencies: EU-Hydro (Approximate) is used meanwhile.",
              "- New Zealand LINZ river polygons (needs a free API key: the club must approve one).", ""]
    (out / "sources.md").write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="KPC 12: build official river-bank polygons and 100 ft bands for water-trail stretches.")
    ap.add_argument("--stretches", required=True, help="stretches.json: [{id, refs, river, center [lat, lon], bbox or line}]")
    ap.add_argument("--out", default=".", help="output folder (banks/ and sources.md go here)")
    ap.add_argument("--cache", default=None, help="cache folder (default <out>/cache)")
    ap.add_argument("--max-minutes", type=float, default=50.0, help="stop cleanly after this many minutes (exit 3)")
    ap.add_argument("--resume", action="store_true", help="carry on from the last run; SOURCE DOWN rows are retried")
    ap.add_argument("--only", action="append", default=None, help="run only this id (repeat the flag for more)")
    ap.add_argument("--nhn-gpkg", default=None, help="optional local NHN GeoPackage (Canada fallback)")
    ap.add_argument("--cache-days", type=float, default=30.0)
    ap.add_argument("--offline", action="store_true", help="use the cache only, no network")
    ap.add_argument("--keep-raw", action="store_true", help="keep the raw national swissTLM3D files in the cache")
    ap.add_argument("-v", "--verbose", action="store_true")
    a = ap.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if a.verbose else logging.INFO, format="%(message)s")
    t0 = time.monotonic()
    out = Path(a.out)
    try:
        check_out_dir(out)
        stretches = load_stretches(Path(a.stretches))
    except BadInput as e:
        log.error("BAD INPUT: %s", e)
        return EXIT_BAD_INPUT
    all_ids = [str(s.get("id", "?")) for s in stretches]
    if a.only:
        keep = {x.strip() for x in a.only}
        stretches = [s for s in stretches if str(s.get("id")) in keep]
    out.mkdir(parents=True, exist_ok=True)
    (out / "banks").mkdir(exist_ok=True)
    state_p = out / "banks" / "_progress.json"
    state: dict[str, dict] = {}
    if a.resume and state_p.exists():
        state = json.loads(state_p.read_text()).get("rows", {})
    fetcher = Fetcher(Path(a.cache) if a.cache else out / "cache", a.cache_days, a.offline)
    fetcher.opts_keep_raw = a.keep_raw
    write_sources_md(out)
    base_dir = Path(a.stretches).resolve().parent
    unfinished = False
    for st in stretches:
        sid = str(st.get("id", "?"))
        prev = state.get(sid)
        if prev and prev["status"] in FINAL_STATUSES:
            continue
        if (time.monotonic() - t0) / 60 > a.max_minutes:
            unfinished = True
            log.info("Time is up (%s min): stopping cleanly. Run again with --resume.", a.max_minutes)
            break
        try:
            r = run_one(st, fetcher, out, base_dir, a.nhn_gpkg)
        except SourceDown as ex:
            r = Result(sid, [str(x) for x in st.get("refs") or []], "", STATUS_DOWN, f"A source did not answer ({ex}); will try again next run.")
        except Exception as ex:  # one failure never stops a batch
            log.debug("trace", exc_info=True)
            r = Result(sid, [str(x) for x in st.get("refs") or []], "", STATUS_CANT, f"Could not work this one out ({type(ex).__name__}: {str(ex)[:120]}).")
        state[sid] = {"id": r.id, "refs": r.refs, "source": r.source, "status": r.status, "why": r.why,
                      "details": r.details, "done_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
        state_p.write_text(json.dumps({"tool": TOOL, "rows": state}, indent=1, default=str))
        log.info("%-40s %-24s %s", sid, r.status, r.why)
    # report: every row of the stretches file that has a result (ids no longer in the file drop out)
    rows = [state[i] for i in all_ids if i in state]
    write_report(out, rows)
    if unfinished or any(r["status"] == STATUS_DOWN for r in rows):
        return EXIT_NOT_FINISHED
    return EXIT_DONE


if __name__ == "__main__":
    sys.exit(main())
