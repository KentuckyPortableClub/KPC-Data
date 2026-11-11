#!/usr/bin/env python3
"""
KPC 8: the NO RECHECKER
=======================

Re-reads the club's NO answers ("this official record is NOT that POTA park")
against POTA's own park page and the official layer named in the row, and
writes QUESTIONS for a person where a NO looks wrong.

**It never changes an answer.** Input files are opened read-only and are never
written. Every question it writes carries ``answer: null`` plus ``old_answer``.

Usage:
    python3 kpc_no_recheck.py --files gis-hunter.json layers.json key-pieces.json \
        [--in-dir data/waiting/questions] [--areas US-KY US-TN] [--limit N]
        [--out no_recheck] [--max-minutes 50] [--resume] [--offline]

Per NO row (spec "KPC 8"):
  1. POTA's side: https://api.pota.app/park/<ref> (name, pin, website), cached
     30 days; the <title> of the POTA-listed website is an extra name
     (robots.txt obeyed).
  2. The record: layer/query?objectIds=<id>&outFields=*&returnGeometry=true
     &outSR=4326&f=geojson. Pin test (inside / metres away in a local metric
     projection; lines and points: within 100 ft), name test against EVERY text
     field, size test (equal-area acres), kind test (the record's type field).
  3. Neighbours within 2 km of the pin on the same layer, scored the same way.
  4. Verdict: LOOK AGAIN / BETTER RECORD / KEEP NO / CAN'T TELL.
  5. Safety cap: a batch (one file, or one area of a file) that comes out more
     than 15% LOOK AGAIN is stopped: "too loose: check the scoring".

House rules: official layers from the input rows only (OSM / Google / AllTrails
/ Protected Planet hosts refused in code), POTA pins are only compared, never
moved; at most 1 request per second per host; the club User-Agent; back-off on
429 / 5xx; robots.txt for web pages; one failure never stops a batch.

Exit codes: 0 finished, 3 not finished (run again with --resume), 2 bad input.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import html as html_lib
import json
import logging
import math
import os
import re
import sys
import time
import unicodedata
from datetime import datetime, timezone
from typing import Any, Callable, Iterable
from urllib.parse import urlencode, urljoin, urlparse

import requests
from pyproj import Transformer
from rapidfuzz import fuzz
from shapely.geometry import Point, shape
import numpy as np
import shapely
from shapely.ops import unary_union
import importlib.util as _ilu, os as _os   # noqa: E402  (owner rule, 2026-11-10: the club's one host check, before any request)
_hs = _ilu.spec_from_file_location("kpc_host_rules", _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "..", "..", "kpc_host_rules.py"))
_hr = _ilu.module_from_spec(_hs); _hs.loader.exec_module(_hr); _hr.install()

VERSION = "0.1.0"
USER_AGENT = "KPC-no-recheck (https://github.com/KentuckyPortableClub)"
UA_TOKEN = "kpc-no-recheck"  # product token matched against robots.txt groups

POTA_API = "https://api.pota.app/park/"
LINE_TOL_M = 30.48          # 100 ft
NEIGHBOUR_M = 2000.0        # step 3 radius, and the "pin far away" KEEP NO rule
NAME_YES = 0.90
NAME_MAYBE = 0.75
SIZE_MAYBE = 3.0            # the 0.75..0.90 band needs acres within 3x
SIZE_OFF = 10.0             # KEEP NO when the size is off by more than 10x
CAP_SHARE = 0.15            # safety cap
CAP_MIN = 3                 # ... a batch needs at least 3 LOOK AGAIN to trip it
SQM_PER_ACRE = 4046.8564224
POTA_TTL_DAYS = 30
LAYER_TTL_DAYS = 30
TIMEOUT = (15, 90)
MAX_TITLE_BYTES = 300_000

VERDICTS = ("LOOK AGAIN", "BETTER RECORD", "KEEP NO", "CAN'T TELL")
CANT = "CAN'T TELL"

FORBIDDEN_HOST_PARTS = (
    "openstreetmap.", "osm.org", "overpass", "google.", "googleapis.", "gstatic.", "goo.gl",
    "alltrails.", "protectedplanet.", "unep-wcmc", "bing.com", "mapquest.",
    "wikipedia.", "wikimedia.", "wikidata.", "tripadvisor.",
)

log = logging.getLogger("kpc_no_recheck")


class TimeUp(Exception):
    """The run's time budget ran out in the middle of a row."""


class BadInput(Exception):
    pass


# ----------------------------------------------------------------------------------------------
# Name normalisation and scoring.
# Adapted from the map-page link extractor (kpc_map_links.py: norm_tokens /
# score_name_vs_field), with the extra type words this spec lists (Wayside,
# Recreation Site, SRS, Natural Area, Preserve, ...) and a guard for weak words.
# ----------------------------------------------------------------------------------------------

# Multi-word type phrases (longest first) -> type family.
TYPE_PHRASES = sorted([
    ("national wild and scenic river", "wsr"), ("wild and scenic river", "wsr"),
    ("national recreation trail", "trail"), ("national scenic trail", "trail"),
    ("national historic trail", "trail"),
    ("state resort park", "park"), ("state historic site", "historic"), ("state historic park", "historic"),
    ("state historical park", "historic"), ("state historic area", "historic"),
    ("national historic site", "historic"), ("national historical park", "historic"),
    ("national historic park", "historic"), ("historic site", "historic"),
    ("national military park", "historic"), ("national battlefield", "historic"),
    ("national memorial", "historic"), ("national monument", "monument"),
    ("state recreation area", "park"), ("state recreation site", "park"), ("state recreational area", "park"),
    ("recreation site", "park"), ("recreation area", "park"), ("recreational area", "park"),
    ("outdoor recreation area", "park"), ("state wayside", "park"),
    ("state natural area", "natural"), ("state nature preserve", "natural"), ("nature preserve", "natural"),
    ("natural area", "natural"), ("nature reserve", "natural"), ("ecological reserve", "natural"),
    ("research natural area", "natural"), ("natural area preserve", "natural"),
    ("state preserve", "natural"), ("scientific and natural area", "natural"),
    ("geological area", "natural"), ("scenic area", "natural"), ("research reserve", "natural"),
    ("fish and wildlife management area", "wma"), ("wildlife management area", "wma"),
    ("state fish and wildlife area", "wma"), ("fish and wildlife area", "wma"),
    ("state wildlife area", "wma"), ("wildlife area", "wma"), ("waterfowl management area", "wma"),
    ("waterfowl production area", "wma"), ("game land", "wma"), ("game lands", "wma"),
    ("state game land", "wma"), ("state game lands", "wma"), ("hunting access area", "wma"),
    ("national wildlife refuge", "nwr"), ("wildlife refuge", "nwr"), ("national wildlife area", "nwr"),
    ("migratory bird sanctuary", "nwr"), ("bird sanctuary", "nwr"),
    ("national forest", "nf"), ("national grassland", "nf"), ("state forest", "forest"),
    ("provincial forest", "forest"), ("demonstration forest", "forest"), ("forest reserve", "forest"),
    ("community forest", "forest"),
    ("provincial park", "park"), ("territorial park", "park"), ("national park", "park"),
    ("state park", "park"), ("state beach", "park"), ("county park", "park"), ("regional park", "park"),
    ("state park trail", "park"), ("state trail", "trail"),
    ("conservation area", "ca"), ("conservation reserve", "ca"), ("conservation easement", "ca"),
    ("wilderness study area", "wilderness"), ("wilderness area", "wilderness"),
    ("special recreation management area", "blm"), ("extensive recreation management area", "blm"),
    ("recreation management area", "blm"), ("area of critical environmental concern", "blm"),
    ("herd management area", "blm"), ("national conservation area", "blm"),
    ("unique area", "unique"), ("multiple use area", "unique"), ("state fishing lake", "water"),
    ("fishing lake", "water"), ("national preserve", "park"), ("national seashore", "park"),
    ("national lakeshore", "park"), ("national river", "wsr"), ("scenic river", "wsr"), ("wild river", "wsr"),
    ("alaska native village statistical area", "tribal"), ("native village statistical area", "tribal"),
    ("statistical area", "tribal"), ("native american land area", "tribal"), ("indian reservation", "tribal"),
    ("tribal land", "tribal"), ("first nation reserve", "tribal"), ("indian reserve", "tribal"),
    ("field office", "office"), ("district office", "office"), ("ranger district", "office"),
    ("administrative site", "office"), ("fish hatchery", "office"), ("national fish hatchery", "office"),
    ("state historical monument", "historic"), ("state historic monument", "historic"),
    ("historical monument", "historic"), ("historic monument", "historic"),
    ("national historic landmark", "historic"),
    ("national guard", "military"), ("military reservation", "military"), ("air force base", "military"),
    ("naval air station", "military"), ("army ammunition plant", "military"),
    ("historic preservation site", "historic"), ("national heritage site", "historic"),
    ("heritage lighthouse", "lighthouse"), ("lighthouse", "lighthouse"), ("light station", "lighthouse"),
    ("registered heritage area", "natural"), ("natural heritage area", "natural"),
    ("boat launch", "facility"), ("boat ramp", "facility"), ("trailhead", "facility"), ("day use area", "facility"),
    ("internal roads", "road"), ("boundary break", "road"), ("fire break", "road"), ("firebreak", "road"),
    ("world heritage site", "heritage"), ("world heritage area", "heritage"), ("cultural landscape", "heritage"),
    ("suaka margasatwa", "nwr"), ("cagar alam", "natural"), ("taman nasional", "park"),
], key=lambda p: -len(p[0]))
TYPE_ABBR = {
    "sp": "park", "srp": "park", "shs": "historic", "shp": "historic", "nhs": "historic", "sra": "park",
    "srs": "park", "srec": "park", "wma": "wma", "fwma": "wma", "fwa": "wma", "swa": "wma", "wpa": "wma",
    "nwr": "nwr", "nwa": "nwr", "pp": "park", "sf": "forest", "nf": "nf", "wsr": "wsr", "nrt": "trail",
    "nst": "trail", "haa": "wma", "ua": "unique", "ora": "park", "snp": "natural", "sna": "natural",
    "srma": "blm", "erma": "blm", "rma": "blm", "acec": "blm", "hma": "blm", "nca": "blm", "wsa": "wilderness",
    "np": "park", "nm": "monument", "sm": "nwr", "anvsa": "tribal", "otsa": "tribal", "sdtsa": "tribal",
}
TYPE_SINGLE = {"wilderness": "wilderness", "preserve": "natural", "refuge": "nwr", "wayside": "park"}
STOP = {"the", "of", "and", "at", "a", "an", "on", "in", "for", "to", "de", "du", "la", "le", "des", "del",
        "y", "et"}
# Words too common to identify a place on their own. Matching only these never scores >= 0.75
# ("Lake" vs "Lake Cumberland"); an unmatched one on the record side costs little.
WEAK = {
    "lake", "lakes", "river", "rivers", "creek", "creeks", "brook", "run", "fork", "forks", "branch",
    "mountain", "mountains", "mount", "mt", "hill", "hills", "island", "islands", "isle", "bay", "point",
    "falls", "canyon", "valley", "spring", "springs", "pond", "ponds", "beach", "ridge", "rock", "rocks",
    "gap", "cove", "harbor", "harbour", "marsh", "swamp", "bog", "meadow", "meadows", "prairie", "woods",
    "wood", "forest", "north", "south", "east", "west", "northern", "southern", "eastern", "western",
    "upper", "lower", "little", "big", "great", "old", "new", "county", "city", "memorial", "national",
    "provincial", "state", "regional", "public", "area", "areas", "unit", "units", "tract", "access",
    "site", "park", "parks", "reserve", "conservation", "management", "wildlife", "recreation", "lands",
    "land", "trail", "historic", "historical", "natural", "center", "centre", "road", "dam", "reservoir",
    "sound", "head", "flats", "field", "fields", "grove", "glen", "landing", "trace", "fishing", "fish",
    "hunting", "game", "waterfowl", "boat", "ramp", "launch", "camp", "campground", "picnic", "day", "use",
    "section", "segment", "parcel", "addition", "annex", "complex", "system", "district", "office",
    "headquarters", "dnr", "blm", "usfs", "fws", "nps", "usace", "no", "inc", "corp", "trust",
}
ZW_RE = re.compile("[\u200b-\u200f\u2060\ufeff\u00ad]")

# Kind groups: two places conflict when both kinds are known and share no group.
FAMILY_GROUP = {
    "park": "park", "historic": "park", "monument": "park", "unique": "park",
    "natural": "natural", "wma": "wildlife", "nwr": "wildlife", "nf": "forest", "forest": "forest",
    "wilderness": "wilderness", "wsr": "river", "trail": "trail", "ca": "conservation", "blm": "blm",
    "water": "water", "office": "office", "tribal": "tribal", "military": "military", "road": "road",
    "facility": "facility", "heritage": "heritage", "lighthouse": "lighthouse",
}
# Words that only count when they are the WHOLE value of a record's type field.
TYPE_VALUE_WORDS = {
    "lake": "water", "lakes": "water", "reservoir": "water", "water": "water", "waterbody": "water",
    "canal": "water", "office": "office", "headquarters": "office", "administrative site": "office",
    "fish hatchery": "office", "hatchery": "office", "national memorials": "historic",
    "national monuments": "monument", "national parks": "park",
    # PAD-US Des_Tp codes that are not parks at all
    "mil": "military", "military": "military", "military land": "military", "tribl": "tribal",
    "native american land area": "tribal",
}
# The LAST word of a record's name, used for its kind only when its type fields say nothing
# ("Milford Lake", "Milford Outlet Park", "Swasey Drive").
NAME_TAIL_WORDS = {
    "park": "park", "parks": "park", "lake": "water", "lakes": "water", "reservoir": "water", "pond": "water",
    "trail": "trail", "trails": "trail", "drive": "road", "road": "road", "roads": "road", "highway": "road",
    "byway": "road", "break": "road", "launch": "facility", "ramp": "facility",
    "river": "wsr", "creek": "wsr",
}


def _strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


def _basic(s: str) -> str:
    s = ZW_RE.sub("", s or "")
    s = _strip_accents(s)
    s = s.replace("&", " and ").replace("\u2019", "'")
    s = re.sub(r"'s\b", "s", s)
    s = s.replace("'", "")
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return f" {s.strip()} "


def norm_tokens(s: str) -> tuple[list[str], set[str]]:
    """Normalise a name -> (tokens, type families found).

    Lower case, accents and punctuation removed, runs of initials joined
    ("R. F. Tarter" -> "rf tarter"), type words dropped (State Park, SP, SRA, SRS,
    WMA, NWR, NF, SF, Wayside, Recreation Site / Area, Natural Area, Preserve ...).
    """
    if not s:
        return [], set()
    s = _basic(s)
    families: set[str] = set()
    for phrase, fam in TYPE_PHRASES:
        while f" {phrase} " in s:
            families.add(fam)
            s = s.replace(f" {phrase} ", " ")
    toks = s.split()
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
        out.append(t)
    # a lone trailing "state" left by a truncated POTA name ("Chena Wayside State")
    while len(out) > 1 and out[-1] in ("state", "provincial", "national"):
        out.pop()
    return out, families


def _tok_match(a: str, b: str) -> bool:
    if a == b:
        return True
    if len(a) >= 5 and len(b) >= 5:
        return fuzz.ratio(a, b) >= 88
    return False


def score_tokens(name_toks: list[str], field_toks: list[str]) -> float:
    """Token-set ratio, gated by how many of the park's own words appear in the field.

    * plain token_set_ratio is 1.0 when either side is a subset of the other, so the
      score is capped by park-word coverage ("Lake Cumberland" vs "Lake" -> 0.5);
    * when only weak words match ("Lake" vs "Lake Cumberland") the score is capped
      at 0.60, below the 0.75 floor;
    * each record word the park doesn't have costs 0.05 (0.02 for a weak word),
      at most 0.40, so a long free-text field can't match on a subset.
    """
    if not name_toks or not field_toks:
        return 0.0
    tsr = fuzz.token_set_ratio(" ".join(name_toks), " ".join(field_toks)) / 100.0
    matched = [t for t in name_toks if any(_tok_match(t, f) for f in field_toks)]
    cov = len(matched) / len(name_toks)
    s = min(tsr, cov)
    if matched and all(t in WEAK or t.isdigit() for t in matched):
        s = min(s, 0.60)
    extras = [f for f in field_toks if not any(_tok_match(f, t) for t in name_toks)]
    pen = sum(0.02 if (f in WEAK or f.isdigit()) else 0.05 for f in extras)
    s -= min(pen, 0.40)
    return round(max(s, 0.0), 3)


def name_score(park_name: str, text: str) -> float:
    return score_tokens(norm_tokens(park_name)[0], norm_tokens(text)[0])


SKIP_FIELD_RE = re.compile(
    r"(^|_)(objectid|fid|oid|gid|globalid|guid|uid|id|shape|st_area|st_length|area|length|perimeter|"
    r"date|dt|created|edited|updated|url|link|web|website|weblink|metadata|src|source|gis_src|agg_src|"
    r"acres|hectares|ha|sqkm|parcel|pin|apn|irma)($|_|\(|\.)",
    re.I,
)


PRIVATE_FIELD_RE = re.compile(
    r"(owner|own_?name|ownnm|taxpayer|grantor|grantee|deeded|mail|addr|street|phone|email|contact|person)", re.I)


def text_fields(props: dict) -> list[tuple[str, str]]:
    """Every text field of a record that can carry a name (ids, dates, urls and codes left out)."""
    out = []
    for k, v in (props or {}).items():
        if not isinstance(v, str):
            continue
        v = v.strip()
        if not v or len(v) > 160:
            continue
        if re.match(r"^(https?:|www\.|\{)", v, re.I):
            continue
        if not re.search(r"[A-Za-z]{3}", v):
            continue
        if SKIP_FIELD_RE.search(k) and not re.search(r"name|nm|label|title", k, re.I):
            continue
        if PRIVATE_FIELD_RE.search(k):  # club privacy rule: a parcel owner's name never leaves the tool
            continue
        out.append((k, v))
    return out


def best_name_match(park_names: list[str], props: dict) -> tuple[float, str | None, str | None, str | None]:
    """-> (score, best_field, best_text, park name that scored)."""
    best: tuple[float, str | None, str | None, str | None] = (0.0, None, None, None)
    pn = [(n, norm_tokens(n)[0]) for n in park_names if n]
    for k, v in text_fields(props):
        ft = norm_tokens(v)[0]
        for n, nt in pn:
            sc = score_tokens(nt, ft)
            if sc > best[0]:
                best = (sc, k, v, n)
    return best


# ----------------------------------------------------------------------------------------------
# Kind test
# ----------------------------------------------------------------------------------------------

TYPE_FIELD_RE = re.compile(r"(type|typ|desig|des_tp|loc_ds|class|categ|kind|prktyp|status_e)", re.I)
NOT_TYPE_FIELD_RE = re.compile(r"(own|mang|manag|agency|org|interest|feat|access|gap|iucn|src|geom|shape|use)",
                               re.I)


def families_of_text(s: str) -> set[str]:
    fams = set(norm_tokens(s)[1])
    b = _basic(s).strip()
    if b in TYPE_VALUE_WORDS:
        fams.add(TYPE_VALUE_WORDS[b])
    return fams


NAME_FIELD_RE = re.compile(r"(name|nm$|_nm_|label|title)", re.I)


def record_kind(props: dict) -> tuple[set[str], str | None]:
    """The record's kind. -> (families, 'FIELD=value' shown in the output).

    From the record's own type field(s) when it has any; when they say nothing, from the type
    words in its name fields ("Aniakchak National Preserve", "Alatna ANVSA")."""
    fams: set[str] = set()
    shown = None
    for k, v in (props or {}).items():
        if not isinstance(v, str) or not v.strip():
            continue
        if not TYPE_FIELD_RE.search(k) or NOT_TYPE_FIELD_RE.search(k):
            continue
        f = families_of_text(v)
        if groups(f):
            fams |= f
            shown = shown or f"{k}={v.strip()}"
    if groups(fams):
        return fams, shown
    for k, v in (props or {}).items():
        if not isinstance(v, str) or not v.strip() or not NAME_FIELD_RE.search(k):
            continue
        if re.search(r"(own|mang|manag|agency|org|src|state|county|region)", k, re.I):
            continue
        f = families_of_text(v)
        if not groups(f):
            words = _basic(v).split()
            if words and words[-1] in NAME_TAIL_WORDS:
                f = {NAME_TAIL_WORDS[words[-1]]}
        if groups(f):
            fams |= f
            shown = shown or f"{k}={v.strip()}"
    return fams, shown


def groups(fams: Iterable[str]) -> set[str]:
    return {FAMILY_GROUP[f] for f in fams if f in FAMILY_GROUP}


def text_kind(s: str | None) -> set[str]:
    """Families from one name: its type words, else its last word ("Milford Lake", "... Falls Trail")."""
    if not s:
        return set()
    f = families_of_text(s)
    if not groups(f):
        words = _basic(s).split()
        if words and words[-1] in NAME_TAIL_WORDS:
            f = {NAME_TAIL_WORDS[words[-1]]}
    return f


def pair_conflict(park_fams: set[str], park_name: str | None, text: str | None) -> bool:
    """The kind test on the matched pair itself: the matched record text's own type words against
    the park's kinds and against the matched park name's type words ("Galena Creek Fish Hatchery"
    vs "Galena Creek Regional Park", "Wolf Creek Recreation Area" vs "Wolf Creek Falls Trail")."""
    tf = text_kind(text)
    if not groups(tf):
        return False
    if kind_conflict(park_fams, tf):
        return True
    return kind_conflict(text_kind(park_name), tf)


LINE_GROUPS = {"trail", "river", "road"}


def shape_conflict(park_fams: set[str], geom) -> bool:
    """A line or point record (a road, a fire break, a boat ramp) is never an AREA park.
    It can only be a park whose kind is a trail or a river."""
    return geom is not None and is_line(geom) and not (groups(park_fams) & LINE_GROUPS)


def kind_conflict(park_fams: set[str], rec_fams: set[str]) -> bool:
    """WMA vs State Park, a whole lake vs a recreation area on it ... (both kinds must be known)."""
    pg, rg = groups(park_fams), groups(rec_fams)
    return bool(pg) and bool(rg) and not (pg & rg)


# ----------------------------------------------------------------------------------------------
# Geometry
# ----------------------------------------------------------------------------------------------

def esri_to_geojson(g: dict | None) -> dict | None:
    if not g:
        return None
    if "rings" in g:
        rings = g["rings"]
        if not rings:
            return None
        if len(rings) == 1:
            return {"type": "Polygon", "coordinates": rings}
        return {"type": "MultiPolygon", "coordinates": [[r] for r in rings], "_esri_rings": True}
    if "paths" in g:
        return {"type": "MultiLineString", "coordinates": g["paths"]} if g["paths"] else None
    if "x" in g and "y" in g and g["x"] is not None:
        return {"type": "Point", "coordinates": [g["x"], g["y"]]}
    if "points" in g:
        return {"type": "MultiPoint", "coordinates": g["points"]} if g["points"] else None
    return None


def to_shape(geojson_geom: dict | None):
    if not geojson_geom or not geojson_geom.get("coordinates"):
        return None
    esri = geojson_geom.get("_esri_rings")
    g = shape({"type": geojson_geom["type"], "coordinates": geojson_geom["coordinates"]})
    if g.is_empty:
        return None
    if esri:  # Esri rings: outer rings and holes come as one list -> even-odd fill
        parts = [p.buffer(0) for p in g.geoms]
        acc = parts[0]
        for p in parts[1:]:
            acc = acc.symmetric_difference(p)
        g = acc if not acc.is_empty else unary_union(parts)
    elif g.geom_type in ("Polygon", "MultiPolygon") and not g.is_valid:
        g = g.buffer(0)
    return None if g.is_empty else g


def shp_transform(fn, geom):
    """Project a shapely geometry with a pyproj transform function (shapely 2 vectorised)."""
    def _xy(coords):
        x, y = fn(coords[:, 0], coords[:, 1])
        return np.column_stack([x, y])
    return shapely.transform(geom, _xy)


def local_metric(lat: float, lon: float) -> Transformer:
    """Azimuthal equidistant centred on the pin: distances from the pin are true metres."""
    return Transformer.from_crs("EPSG:4326", f"+proj=aeqd +lat_0={lat} +lon_0={lon} +datum=WGS84 +units=m",
                                always_xy=True)


def equal_area(lat: float, lon: float) -> Transformer:
    return Transformer.from_crs("EPSG:4326", f"+proj=laea +lat_0={lat} +lon_0={lon} +datum=WGS84 +units=m",
                                always_xy=True)


def is_line(geom) -> bool:
    return geom.geom_type in ("LineString", "MultiLineString", "Point", "MultiPoint") or geom.area == 0


def pin_test(geom, lat: float, lon: float) -> tuple[bool, float]:
    """-> (pin_inside, pin_dist_m). Line (and point) records count as 'inside' within 100 ft."""
    tr = local_metric(lat, lon)
    gm = shp_transform(tr.transform, geom)
    pin = Point(0.0, 0.0)
    if not is_line(geom):
        if gm.covers(pin):
            return True, 0.0
        return False, round(gm.distance(pin), 1)
    d = gm.distance(pin)
    return d <= LINE_TOL_M, round(d, 1)


def geom_acres(geom) -> float | None:
    if geom is None or is_line(geom):
        return None
    c = geom.representative_point()
    tr = equal_area(c.y, c.x)
    return round(shp_transform(tr.transform, geom).area / SQM_PER_ACRE, 2)


def envelope(lat: float, lon: float, metres: float) -> tuple[float, float, float, float]:
    dlat = metres / 111_320.0
    dlon = metres / (111_320.0 * max(math.cos(math.radians(lat)), 0.01))
    return (lon - dlon, lat - dlat, lon + dlon, lat + dlat)


# ----------------------------------------------------------------------------------------------
# robots.txt (RFC 9309; same parser as the map-page link extractor)
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
        groups_: list[tuple[list[str], list[tuple[bool, str]], float | None]] = []
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
                    groups_.append((agents, rules, delay))
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
            groups_.append((agents, rules, delay))
        mine = [g for g in groups_ if any(a != "*" and a in UA_TOKEN for a in g[0])]
        chosen = mine or [g for g in groups_ if "*" in g[0]]
        for g in chosen:
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
# Polite HTTP client with a disk cache
# ----------------------------------------------------------------------------------------------

def host_forbidden(host: str) -> bool:
    h = (host or "").lower()
    return any(p in h for p in FORBIDDEN_HOST_PARTS)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class FetchError(Exception):
    """A request failed after back-off; the message is the plain reason."""


class Fetcher:
    def __init__(self, cache_dir: str, offline: bool = False, min_interval: float = 1.0,
                 hard_deadline: float | None = None, session: requests.Session | None = None,
                 sleep: Callable[[float], None] = time.sleep, max_attempts: int = 5):
        self.dead_web_hosts: set[str] = set()  # web pages that did not answer this run
        self.cache_dir = cache_dir
        self.offline = offline
        self.min_interval = max(1.0, min_interval)
        self.hard_deadline = hard_deadline
        self.s = session or requests.Session()
        self.s.headers.update({"User-Agent": USER_AGENT, "Accept-Language": "en"})
        self.sleep = sleep
        self.max_attempts = max_attempts
        self.last: dict[str, float] = {}
        self.robots: dict[str, Robots] = {}
        self.requests_made = 0
        self.cache_hits = 0

    # --- cache ---
    def _cache_path(self, key: str) -> str:
        h = hashlib.sha1(key.encode()).hexdigest()
        return os.path.join(self.cache_dir, h[:2], h + ".json")

    def cache_get(self, key: str, ttl_days: float) -> dict | None:
        try:
            with open(self._cache_path(key), "r", encoding="utf-8") as f:
                obj = json.load(f)
        except (OSError, ValueError):
            return None
        if not self.offline and time.time() - obj.get("t", 0) > ttl_days * 86400:
            return None
        self.cache_hits += 1
        return obj

    def cache_put(self, key: str, body: Any) -> None:
        p = self._cache_path(key)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        tmp = p + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({"key": key, "t": time.time(), "read_date": utc_now(), "body": body}, f)
        os.replace(tmp, p)

    # --- politeness ---
    def _wait(self, host: str) -> None:
        delay = self.min_interval
        r = self.robots.get(host)
        if r and r.crawl_delay:
            delay = max(delay, min(r.crawl_delay, 30.0))
        last = self.last.get(host)
        if last is not None:
            gap = time.monotonic() - last
            if gap < delay:
                self.sleep(delay - gap)
        self.last[host] = time.monotonic()

    def _check_time(self, extra: float = 0.0) -> None:
        if self.hard_deadline is not None and time.time() + extra > self.hard_deadline:
            raise TimeUp()

    def request(self, url: str, stream: bool = False, timeout=TIMEOUT, allow_redirects: bool = True,
                attempts: int | None = None) -> requests.Response:
        """One polite GET: 1 req/s per host, back-off on network errors, 429 and 5xx (Retry-After honoured)."""
        if self.offline:
            raise FetchError("not in the cache (--offline)")
        host = urlparse(url).hostname or ""
        if host_forbidden(host):
            raise FetchError(f"host refused by club rule: {host}")
        last_err = "no answer"
        back = 0.0
        max_attempts = attempts or self.max_attempts
        for attempt in range(max_attempts):
            self._check_time()
            self._wait(host)
            try:
                resp = self.s.get(url, timeout=timeout, stream=stream, allow_redirects=allow_redirects)
                self.requests_made += 1
            except requests.RequestException as e:
                last_err = f"network error ({e.__class__.__name__})"
                back = min(3 * 2 ** attempt, 60)
            else:
                if resp.status_code == 429 or 500 <= resp.status_code < 600:
                    last_err = f"HTTP {resp.status_code}"
                    ra = resp.headers.get("Retry-After", "")
                    back = min(int(ra) if ra.isdigit() else 5 * 2 ** attempt, 120)
                    resp.close()
                else:
                    return resp
            if attempt == max_attempts - 1:
                break
            self._check_time(back)
            log.info("%s on %s; backing off %ss", last_err, url, back)
            self.sleep(back)
        raise FetchError(f"{last_err} after {max_attempts} tries")

    def get_json(self, url: str, ttl_days: float, arcgis: bool = False) -> tuple[Any, str]:
        """GET a JSON document, cached. -> (body, read_date). An ArcGIS 200-with-error body backs off too
        and is never cached, so it is retried next run."""
        c = self.cache_get(url, ttl_days)
        if c is not None:
            return c["body"], c.get("read_date", "")
        tries = 0
        while True:
            resp = self.request(url)
            if resp.status_code != 200:
                raise FetchError(f"HTTP {resp.status_code}")
            try:
                body = resp.json()
            except ValueError:
                raise FetchError("the answer was not JSON")
            if arcgis and isinstance(body, dict) and isinstance(body.get("error"), dict):
                code = body["error"].get("code")
                if code in (429, 500, 502, 503, 504) and tries < 2:
                    tries += 1
                    self._check_time(10 * tries)
                    self.sleep(10 * tries)
                    continue
                return body, utc_now()
            self.cache_put(url, body)
            return body, utc_now()

    def robots_for(self, scheme: str, host: str) -> Robots:
        if host in self.robots:
            return self.robots[host]
        key = f"robots:{scheme}://{host}"
        c = self.cache_get(key, 7)
        if c is not None:
            b = c["body"]
        else:
            if self.offline:
                raise FetchError("robots.txt not in the cache (--offline)")
            try:
                r = self.request(f"{scheme}://{host}/robots.txt", timeout=(10, 30), attempts=2)
                if r.status_code == 200 and "html" not in r.headers.get("content-type", "").lower():
                    b = {"text": r.text[:500_000]}
                elif 400 <= r.status_code < 500:
                    b = {"allow_all": True}
                else:
                    b = {"disallow_all": True}
            except FetchError as e:
                log.info("robots.txt unreachable for %s (%s): treating the site as disallowed", host, e)
                b = {"disallow_all": True, "transient": True}
            if not b.get("transient"):
                self.cache_put(key, b)
        rob = Robots(b.get("text"), allow_all=b.get("allow_all", False), disallow_all=b.get("disallow_all", False))
        self.robots[host] = rob
        return rob

    def page_title(self, url: str, ttl_days: float = POTA_TTL_DAYS) -> tuple[str | None, str]:
        """The <title> of a web page, obeying robots.txt on every hop. -> (title or None, note)."""
        key = f"title:{url}"
        c = self.cache_get(key, ttl_days)
        if c is not None:
            return c["body"].get("title"), c["body"].get("note", "cached")
        if self.offline:
            return None, "not in the cache (--offline)"
        cur = url
        title = None
        note = "too many redirects"
        try:
            for _hop in range(6):
                p = urlparse(cur)
                if p.scheme not in ("http", "https") or not p.hostname:
                    note = "not a web address"; break
                if host_forbidden(p.hostname):
                    note = f"host refused by club rule: {p.hostname}"; break
                if p.hostname in self.dead_web_hosts:
                    return None, "the website did not answer earlier in this run"
                if not self.robots_for(p.scheme, p.hostname).allowed(cur):
                    note = "robots.txt disallows it"; break
                try:
                    resp = self.request(cur, stream=True, timeout=(10, 30), allow_redirects=False, attempts=2)
                except (FetchError, requests.RequestException):
                    self.dead_web_hosts.add(p.hostname)
                    raise
                if resp.status_code in (301, 302, 303, 307, 308) and resp.headers.get("Location"):
                    cur = urljoin(cur, resp.headers["Location"]); resp.close(); continue
                if resp.status_code != 200:
                    note = f"HTTP {resp.status_code}"; resp.close(); break
                ctype = resp.headers.get("content-type", "").lower()
                if ctype and "html" not in ctype:
                    note = f"not a web page ({ctype.split(';')[0]})"; resp.close(); break
                raw = b""
                for chunk in resp.iter_content(16384):
                    raw += chunk
                    if len(raw) > MAX_TITLE_BYTES or b"</title>" in raw.lower():
                        break
                resp.close()
                txt = raw.decode(resp.encoding or "utf-8", errors="replace")
                m = re.search(r"<title[^>]*>(.*?)</title>", txt, re.I | re.S)
                if m:
                    title = re.sub(r"\s+", " ", html_lib.unescape(m.group(1))).strip() or None
                note = "ok" if title else "no <title>"
                break
        except FetchError as e:
            return None, str(e)  # transient: not cached, tried again next run
        except requests.RequestException as e:
            return None, f"network error ({e.__class__.__name__})"
        self.cache_put(key, {"title": title, "note": note})
        return title, note


# ----------------------------------------------------------------------------------------------
# ArcGIS reads (official layers from the input rows only)
# ----------------------------------------------------------------------------------------------

LAYER_RE = re.compile(r"^https?://\S+/(MapServer|FeatureServer)/\d+/?$", re.I)


def layer_of(row: dict) -> str | None:
    for k in ("layer", "url"):
        v = row.get(k)
        if isinstance(v, str) and LAYER_RE.match(v.strip()):
            return v.strip().rstrip("/")
    return None


def object_id_of(row: dict) -> int | None:
    r = row.get("record")
    if isinstance(r, bool):
        return None
    if isinstance(r, int):
        return r
    if isinstance(r, float) and r.is_integer():
        return int(r)
    if isinstance(r, str) and re.fullmatch(r"\s*\d+\s*", r):
        return int(r)
    return None


def layer_key(layer: str) -> str:
    return re.sub(r"/(mapserver|featureserver)/", "/s/", layer.lower())


def feature_oid(ft: dict) -> Any:
    if ft.get("id") is not None:
        return ft["id"]
    for k, v in (ft.get("properties") or {}).items():
        if k.lower() in ("objectid", "fid", "oid", "objectid_1"):
            return v
    return None


class LayerReader:
    """Reads one record and its neighbours from an ArcGIS REST layer (GeoJSON, Esri JSON fallback)."""

    def __init__(self, fetcher: Fetcher):
        self.f = fetcher

    def _features(self, layer: str, params: dict) -> tuple[list[dict], str]:
        """-> ([{'id', 'properties', 'geometry'(geojson)}], read_date). Raises FetchError."""
        q = dict(params)
        q.setdefault("outFields", "*")
        q["outSR"] = "4326"
        url = f"{layer}/query?" + urlencode({**q, "f": "geojson"})
        body, rd = self.f.get_json(url, LAYER_TTL_DAYS, arcgis=True)
        if isinstance(body, dict) and body.get("type") == "FeatureCollection":
            feats = [{"id": ft.get("id"), "properties": ft.get("properties") or {}, "geometry": ft.get("geometry")}
                     for ft in body.get("features") or []]
            return feats, rd
        # older servers have no f=geojson: Esri JSON
        url = f"{layer}/query?" + urlencode({**q, "f": "json"})
        body, rd = self.f.get_json(url, LAYER_TTL_DAYS, arcgis=True)
        if isinstance(body, dict) and isinstance(body.get("error"), dict):
            e = body["error"]
            raise FetchError(f"layer error {e.get('code')}: {e.get('message') or ''}".strip())
        if not isinstance(body, dict) or "features" not in body:
            raise FetchError("the layer's answer had no features list")
        oidf = body.get("objectIdFieldName")
        feats = []
        for ft in body.get("features") or []:
            a = ft.get("attributes") or {}
            oid = a.get(oidf) if oidf else next((v for k, v in a.items()
                                                 if k.lower() in ("objectid", "fid", "oid")), None)
            feats.append({"id": oid, "properties": a, "geometry": esri_to_geojson(ft.get("geometry"))})
        return feats, rd

    def record(self, layer: str, oid: int) -> tuple[dict | None, str]:
        """The spec's query: objectIds=<id>&outFields=*&returnGeometry=true&outSR=4326&f=geojson."""
        try:
            feats, rd = self._features(layer, {"objectIds": str(oid), "returnGeometry": "true"})
        except FetchError as e:
            if "network error" not in str(e) and "HTTP 5" not in str(e):
                raise
            # a very big shape can time out: ask once more, generalised to about 5 m
            feats, rd = self._features(layer, {"objectIds": str(oid), "returnGeometry": "true",
                                               "maxAllowableOffset": "0.00005"})
        return (feats[0] if feats else None), rd

    def neighbours(self, layer: str, lat: float, lon: float) -> list[dict]:
        """Records within 2 km of the pin (envelope query, outFields=*), attributes only."""
        x0, y0, x1, y1 = envelope(lat, lon, NEIGHBOUR_M)
        feats, _ = self._features(layer, {
            "geometry": f"{x0:.6f},{y0:.6f},{x1:.6f},{y1:.6f}", "geometryType": "esriGeometryEnvelope",
            "inSR": "4326", "spatialRel": "esriSpatialRelIntersects", "returnGeometry": "false",
        })
        return feats

    def shapes(self, layer: str, oids: list) -> dict[Any, dict]:
        feats, _ = self._features(layer, {"objectIds": ",".join(str(o) for o in oids), "returnGeometry": "true",
                                          "maxAllowableOffset": "0.00005"})
        return {feature_oid(f): f for f in feats}


# ----------------------------------------------------------------------------------------------
# POTA (pins are only read and compared, never moved)
# ----------------------------------------------------------------------------------------------

def title_names(title: str | None, anchor_names: list[str]) -> list[str]:
    """Useful name pieces of a web page <title>.

    The title is split on | - : and similar separators. A piece is kept only if it
    shares a non-weak word with POTA's or the club's name, so an agency's own name
    ("Alaska Department of Natural Resources") can't match an agency field.
    """
    if not title:
        return []
    anchor: set[str] = set()
    for n in anchor_names:
        anchor |= {t for t in norm_tokens(n)[0] if t not in WEAK and not t.isdigit()}
    title = re.sub(r"\([^)]*\)", " ", title)
    pieces = [p.strip() for p in re.split(r"\s+[|\-\u2013\u2014:\u00b7\u2022]\s+|\s*\|\s*", title) if p.strip()]
    out: list[str] = []
    for p in pieces:
        toks = norm_tokens(p)[0]
        if any(any(_tok_match(t, a) for a in anchor) for t in toks if t not in WEAK):
            if p not in out:
                out.append(p)
    return out[:3]


def pota_info(fetcher: Fetcher, ref: str) -> tuple[dict | None, str]:
    """-> (park dict, read date) or (None, reason)."""
    try:
        body, rd = fetcher.get_json(POTA_API + ref, POTA_TTL_DAYS)
    except FetchError as e:
        return None, f"POTA's park page did not answer ({e})."
    if not isinstance(body, dict) or body.get("latitude") is None or body.get("longitude") is None:
        return None, f"POTA has no pin for {ref}."
    return body, rd


# ----------------------------------------------------------------------------------------------
# The verdict (pure; unit tested)
# ----------------------------------------------------------------------------------------------

def size_ratio(rec_acres: float | None, park_acres: float | None) -> float | None:
    if not rec_acres or not park_acres or rec_acres <= 0 or park_acres <= 0:
        return None
    return round(max(rec_acres, park_acres) / min(rec_acres, park_acres), 2)


def qualifies(pin_ok: bool, name: float, ratio: float | None, conflict: bool) -> bool:
    """LOOK AGAIN test: pin inside (or within 100 ft of a line), AND name >= 0.90, or 0.75..0.90 with
    acres within 3x. A kind conflict or a size off by more than 10x always keeps it NO."""
    if not pin_ok or conflict:
        return False
    if ratio is not None and ratio > SIZE_OFF:
        return False
    if name >= NAME_YES:
        return True
    return name >= NAME_MAYBE and ratio is not None and ratio <= SIZE_MAYBE


def decide(ev: dict, better: dict | None) -> tuple[str, str]:
    """ev keys: pin_inside, pin_dist_m, name_score, size_ratio, kind_conflict, line, best_text,
    park_kind, record_kind. -> (verdict, why)."""
    pin_ok = bool(ev.get("pin_inside"))
    name = ev.get("name_score") or 0.0
    ratio = ev.get("size_ratio")
    conflict = bool(ev.get("kind_conflict"))
    if qualifies(pin_ok, name, ratio, conflict):
        where = "within 100 ft of the line" if ev.get("line") else "inside the record"
        if name >= NAME_YES:
            return "LOOK AGAIN", (f"POTA's pin is {where} and the name scores {name:.2f} "
                                  f"against '{ev.get('best_text')}'.")
        return "LOOK AGAIN", (f"POTA's pin is {where}, the name scores {name:.2f} against "
                              f"'{ev.get('best_text')}' and the acres are within {ratio:.1f}x.")
    if better:
        return "BETTER RECORD", (f"A nearby record on the same layer fits better: object id {better['id']} "
                                 f"'{better['name']}' (pin inside, name {better['score']:.2f}).")
    d = ev.get("pin_dist_m")
    if not pin_ok and d is not None and d > NEIGHBOUR_M:
        return "KEEP NO", f"POTA's pin is {d / 1000:.1f} km outside the record."
    if name < NAME_MAYBE:
        return "KEEP NO", f"The best name score is only {name:.2f}" + (
            f" ('{ev.get('best_text')}')." if ev.get("best_text") else ".")
    if conflict:
        return "KEEP NO", (f"A kind conflict: the park is {ev.get('park_kind')} but the record is "
                           f"{ev.get('record_kind')}.")
    if ratio is not None and ratio > SIZE_OFF:
        return "KEEP NO", f"The size is off by {ratio:.0f}x."
    if not pin_ok:
        return "KEEP NO", (f"The name scores {name:.2f} but POTA's pin is {d:.0f} m outside the record."
                           if d is not None else f"The name scores {name:.2f} but the pin test failed.")
    if ratio is None:
        return "KEEP NO", f"The name scores {name:.2f}, under 0.90, and there are no park acres to back it up."
    return "KEEP NO", f"The name scores {name:.2f}, under 0.90, and the acres are {ratio:.1f}x apart."


def evidence_line(rec: dict) -> str:
    """One plain line a person can judge."""
    who = f"{rec['ref']} '{rec.get('pota_name') or rec.get('park')}'"
    if rec.get("verdict") == "BETTER RECORD" and rec.get("better"):
        b = rec["better"]
        return (f"{who}: answered NO for record {rec['record']} '{rec.get('record_name')}'; record {b['id']} "
                f"'{b['name']}' on the same layer has POTA's pin inside, name {b['score']:.2f}"
                + (f", {b['acres']} ac" if b.get("acres") else "") + ".")
    if rec.get("pin_inside"):
        pin = "POTA pin inside" if rec.get("pin_dist_m") == 0 else f"POTA pin {rec.get('pin_dist_m')} m from the line"
    elif rec.get("pin_dist_m") is not None:
        pin = f"POTA pin {rec['pin_dist_m']:.0f} m outside"
    else:
        pin = "pin not tested"
    parts = [f"{who} vs record {rec['record']} '{rec.get('record_name')}': {pin}",
             f"name {rec.get('name_score') or 0:.2f} on {rec.get('best_field')}='{rec.get('best_text')}'"]
    if rec.get("record_acres"):
        parts.append(f"record {rec['record_acres']:.0f} ac")
    if rec.get("size_ratio"):
        parts.append(f"size {rec['size_ratio']}x")
    if rec.get("park_kind") and rec.get("record_kind") and not rec.get("kind_conflict"):
        parts.append(f"kinds agree ({rec['park_kind']})")
    return ", ".join(parts) + "."


# ----------------------------------------------------------------------------------------------
# One row
# ----------------------------------------------------------------------------------------------

PARK_ACRE_KEYS = ("park_acres", "pota_acres", "park_acres_approx")


def park_acres_of(row: dict, pota: dict | None) -> float | None:
    """The PARK's acres, if the row or POTA gives them. (acres_approx / acres in the rows are the
    RECORD's size, so they are not used here.)"""
    for k in PARK_ACRE_KEYS:
        v = row.get(k)
        if isinstance(v, (int, float)) and not isinstance(v, bool) and v > 0:
            return float(v)
    for k in ("acres", "areaAcres", "area_acres"):
        v = (pota or {}).get(k)
        if isinstance(v, (int, float)) and not isinstance(v, bool) and v > 0:
            return float(v)
    return None


def answered_records(all_rows: Iterable[dict]) -> dict[str, set[tuple[str, int]]]:
    """ref -> {(layer, oid)} for every row that already has an answer, so a 'better' neighbour that was
    already asked about is not asked again."""
    out: dict[str, set[tuple[str, int]]] = {}
    for r in all_rows:
        if not str(r.get("answer") or "").strip():
            continue
        lay, oid = layer_of(r), object_id_of(r)
        if lay and oid is not None:
            out.setdefault(r.get("ref"), set()).add((layer_key(lay), oid))
    return out


def blank_record(row: dict) -> dict:
    return {
        "ref": row.get("ref"), "area": row.get("area"), "park": row.get("park"),
        "layer": row.get("layer") or row.get("url"), "record": row.get("record"),
        "record_name": row.get("record_name"),
        "verdict": None, "why": None, "pin_inside": None, "pin_dist_m": None, "name_score": None,
        "best_field": None, "best_text": None, "size_ratio": None, "kind_conflict": None, "better": None,
        "read_date": utc_now(), "old_answer": row.get("answer"),
    }


def check_row(row: dict, fetcher: Fetcher, reader: LayerReader,
              already: dict[str, set[tuple[str, int]]] | None = None) -> dict:
    ref = row.get("ref")
    rec = blank_record(row)

    def done(verdict: str, why: str) -> dict:
        rec["verdict"], rec["why"] = verdict, why
        return rec

    layer = layer_of(row)
    if not layer:
        lv = row.get("layer") or row.get("url") or ""
        return done(CANT, f"The row names no ArcGIS layer URL (layer: '{lv}'), so there is no official record to read."
                    if lv else "The row names no layer at all, so there is no official record to read.")
    oid = object_id_of(row)
    if oid is None:
        return done(CANT, f"The record id '{row.get('record')}' is not an object id on the layer.")
    if host_forbidden(urlparse(layer).hostname or ""):
        return done(CANT, "The layer's host is not an official source by club rule.")

    pota, rd = pota_info(fetcher, ref)
    if pota is None:
        return done(CANT, rd)
    lat, lon = float(pota["latitude"]), float(pota["longitude"])
    rec["pota_name"] = pota.get("name")
    rec["pota_pin"] = [lat, lon]
    rec["pota_type"] = pota.get("parktypeDesc")
    rec["pota_website"] = pota.get("website")
    anchor = [n for n in (pota.get("name"), row.get("park")) if n]
    title = None
    if isinstance(pota.get("website"), str) and pota["website"].strip():
        title, tnote = fetcher.page_title(pota["website"].strip().split()[0])
        rec["website_title"] = title
        rec["website_note"] = tnote
    names: list[str] = []
    for n in [pota.get("name")] + title_names(title, anchor) + [row.get("park")]:
        if n and n not in names:
            names.append(n)
    rec["names_used"] = names

    try:
        ft, rd = reader.record(layer, oid)
    except FetchError as e:
        return done(CANT, f"The layer did not answer ({e}).")
    rec["read_date"] = rd or rec["read_date"]
    if ft is None:
        return done(CANT, f"The record is gone: object id {oid} is not on the layer any more.")
    geom = to_shape(ft.get("geometry"))
    if geom is None:
        return done(CANT, f"Record {oid} has no geometry.")
    props = ft.get("properties") or {}

    # the pin test
    inside, dist = pin_test(geom, lat, lon)
    line = is_line(geom)
    rec["pin_inside"], rec["pin_dist_m"], rec["record_geom"] = inside, dist, geom.geom_type
    # the name test (every text field)
    sc, bf, bt, bn = best_name_match(names, props)
    rec["name_score"], rec["best_field"], rec["best_text"], rec["best_park_name"] = sc, bf, bt, bn
    # the size test
    rec["record_acres"] = geom_acres(geom)
    rec["row_acres"] = row.get("acres_approx", row.get("acres"))
    park_acres = park_acres_of(row, pota)
    rec["park_acres"] = park_acres
    rec["size_ratio"] = size_ratio(rec["record_acres"], park_acres)
    # the kind test
    park_fams: set[str] = set()
    for n in (pota.get("name") or "", row.get("park") or ""):
        park_fams |= norm_tokens(n)[1]
    if pota.get("parktypeDesc"):
        park_fams |= families_of_text(str(pota["parktypeDesc"]))
    rec_fams, rec_kind_shown = record_kind(props)
    rec["park_kind"] = ", ".join(sorted(groups(park_fams))) or None
    rec["record_kind"] = (", ".join(sorted(groups(rec_fams))) + (f" ({rec_kind_shown})" if rec_kind_shown else "")
                          ) if groups(rec_fams) else None
    rec["kind_conflict"] = kind_conflict(park_fams, rec_fams)
    if not rec["kind_conflict"] and shape_conflict(park_fams, geom):
        rec["kind_conflict"] = True
        rec["record_kind"] = f"a line or point, not an area ({geom.geom_type})"
    if not rec["kind_conflict"] and pair_conflict(park_fams, bn, bt):
        rec["kind_conflict"] = True
        rec["record_kind"] = ", ".join(sorted(groups(text_kind(bt)))) + f" ({bf}={bt})"
        if text_kind(bn) and groups(text_kind(bn)):
            rec["park_kind"] = ", ".join(sorted(groups(text_kind(bn)))) + f" ('{bn}')"

    # the neighbours: names first (attributes only), shapes only for names >= 0.90
    better = None
    if not qualifies(inside, sc, rec["size_ratio"], rec["kind_conflict"]):
        try:
            neigh = reader.neighbours(layer, lat, lon)
            rec["neighbours_read"] = len(neigh)
            asked = (already or {}).get(ref, set())
            cands = []
            for nf in neigh:
                noid = feature_oid(nf)
                if noid is None or noid == oid or (layer_key(layer), noid) in asked:
                    continue
                nsc, _nbf, nbt, nbn = best_name_match(names, nf.get("properties") or {})
                if nsc >= NAME_YES and nsc > sc and not pair_conflict(park_fams, nbn, nbt):
                    cands.append((nsc, noid, nbt))
            cands.sort(key=lambda c: -c[0])
            if cands:
                shp = reader.shapes(layer, [c[1] for c in cands[:5]])
                for nsc, noid, nbt in cands[:5]:
                    nft = shp.get(noid)
                    g2 = to_shape(nft.get("geometry")) if nft else None
                    if g2 is None:
                        continue
                    ins2, _d2 = pin_test(g2, lat, lon)
                    a2 = geom_acres(g2)
                    r2 = size_ratio(a2, park_acres)
                    f2, _ = record_kind(nft.get("properties") or {})
                    if ins2 and not kind_conflict(park_fams, f2) and not shape_conflict(park_fams, g2) and (r2 is None or r2 <= SIZE_OFF):
                        better = {"id": noid, "name": nbt, "acres": a2, "score": nsc, "pin_inside": True}
                        break
        except FetchError as e:
            rec["neighbours_read"] = None
            rec["neighbours_note"] = f"the neighbour query failed ({e})"
    else:
        rec["neighbours_read"] = "skipped (the record itself already fits)"
    rec["better"] = better
    return done(*decide(dict(rec, line=line), better))


# ----------------------------------------------------------------------------------------------
# Selection, batches and the safety cap
# ----------------------------------------------------------------------------------------------

def is_no(answer: Any, answers: list[str]) -> bool:
    """'NO', 'NO: a different place', 'NO (names only)' -> True; 'NOT SURE' -> False."""
    a = str(answer or "").strip().upper()
    for w in answers:
        w = w.strip().upper()
        if a == w or re.match(re.escape(w) + r"(?![A-Z0-9])", a):
            return True
    return False


NORTH_AMERICA = {
    "MX", "GT", "BZ", "SV", "HN", "NI", "CR", "PA", "CU", "JM", "HT", "DO", "BS", "BB", "TT", "PR", "VI", "VG",
    "BM", "KY", "AG", "DM", "GD", "KN", "LC", "VC", "AI", "AW", "CW", "BQ", "SX", "MF", "BL", "GP", "MQ", "TC",
    "MS", "GL", "PM",
}


def area_rank(area: str | None) -> int:
    """The club's order of work: Kentucky first, then the rest of the US and Canada, then the rest of
    North America (Mexico, Central America, the Caribbean, Greenland), then the world."""
    a = (area or "").upper()
    if a == "US-KY":
        return 0
    if a.startswith("US-") or a.startswith("CA-"):
        return 1
    if re.sub(r"^W-", "", a).split("-")[0] in NORTH_AMERICA:
        return 2
    return 3


def area_match(area: str | None, wanted: list[str]) -> bool:
    a = re.sub(r"^W-", "", (area or "").upper())
    return any(a == re.sub(r"^W-", "", w.upper()) for w in wanted)


class Cap:
    """Safety cap: more than 15% LOOK AGAIN in a batch (one file, or one area of a file) stops it.
    The share is of the rows judged so far (CAN'T TELL rows are not judged), and a batch needs at
    least CAP_MIN LOOK AGAIN rows before it can trip, so one hit in a 5-row area does not stop it."""

    def __init__(self, share: float = CAP_SHARE, minimum: int = CAP_MIN):
        self.share, self.minimum = share, minimum
        self.counts: dict[str, dict[str, int]] = {}
        self.stopped: dict[str, str] = {}

    def add(self, batch: str, verdict: str) -> None:
        c = self.counts.setdefault(batch, {"judged": 0, "look": 0})
        if verdict == CANT:
            return
        c["judged"] += 1
        if verdict == "LOOK AGAIN":
            c["look"] += 1
        if batch not in self.stopped and c["look"] >= self.minimum and c["look"] > self.share * c["judged"]:
            self.stopped[batch] = (f"too loose: check the scoring ({c['look']} LOOK AGAIN of {c['judged']} "
                                   f"judged rows = {100 * c['look'] / c['judged']:.0f}%, over 15%)")

    def is_stopped(self, *batches: str) -> str | None:
        for b in batches:
            if b in self.stopped:
                return self.stopped[b]
        return None


def batches_of(fname: str, area: str | None) -> tuple[str, str]:
    return f"file|{fname}", f"area|{fname}|{area}"


# ----------------------------------------------------------------------------------------------
# Input and output
# ----------------------------------------------------------------------------------------------

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json_atomic(path: str, obj: Any) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)
    os.replace(tmp, path)


def load_inputs(files: list[str], in_dir: str) -> list[tuple[str, str, dict]]:
    """-> [(file name, path, parsed)]. Raises BadInput. Files are only ever opened for reading."""
    out = []
    scripts = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    from kpc_json_any import load_json_any
    for f in files:
        path = f if os.path.isfile(f) or os.path.isfile(str(f) + '.gz') else os.path.join(in_dir, f)
        if not os.path.isfile(path) and not os.path.isfile(str(path) + '.gz'):
            raise BadInput(f"input file not found: {f} (also looked in {in_dir})")
        try:
            data = load_json_any(path)
        except (OSError, ValueError, UnicodeDecodeError) as e:
            raise BadInput(f"{f} is not valid JSON: {e}")
        if not isinstance(data, dict) or not isinstance(data.get("questions"), list):
            raise BadInput(f"{f} has no 'questions' list")
        for i, q in enumerate(data["questions"]):
            if not isinstance(q, dict) or not q.get("ref"):
                raise BadInput(f"{f}: question {i} has no 'ref'")
        name = os.path.basename(path[:-3] if str(path).endswith('.gz') else path)
        out.append((name, path, data))
    names = [o[0] for o in out]
    if len(set(names)) != len(names):
        raise BadInput("two input files have the same name")
    if any(n in ("questions.json", "state.json") for n in names):
        raise BadInput("an input file is named questions.json or state.json, which the outputs use")
    return out


def row_key(row: dict, idx: int) -> str:
    return f"{idx}|{row.get('ref')}|{row.get('layer') or row.get('url') or ''}|{row.get('record')}"


def build_question(row: dict, rec: dict, fname: str) -> dict:
    """Same shape as the input question, plus old_answer, evidence and suggested_record; answer: null."""
    q = json.loads(json.dumps(row))  # a deep copy: the input row itself is never touched
    q["old_answer"] = row.get("answer")
    q["old_checked_by"] = row.get("checked_by")
    q["old_how"] = row.get("how")
    q["answer"] = None
    q["checked_by"] = None
    q["how"] = None
    q["recheck_verdict"] = rec["verdict"]
    q["evidence"] = evidence_line(rec)
    q["source_file"] = fname
    layer = layer_of(row)
    if rec["verdict"] == "BETTER RECORD" and rec.get("better"):
        b = rec["better"]
        q["suggested_record"] = {
            "layer": layer, "record": b["id"], "record_name": b["name"], "acres": b.get("acres"),
            "record_link": f"{layer}/query?objectIds={b['id']}&outFields=*&returnGeometry=false&f=html",
        }
        q["question"] = ("This was answered NO for the record above. Is the suggested record on the same layer "
                         "(POTA's pin is inside it) that park instead? YES / NO")
    else:
        q["suggested_record"] = {
            "layer": layer, "record": rec["record"], "record_name": rec.get("best_text") or rec.get("record_name"),
            "acres": rec.get("record_acres"),
            "record_link": row.get("record_link") or (f"{layer}/query?objectIds={rec['record']}&outFields=*"
                                                      f"&returnGeometry=false&f=html"),
        }
        q["question"] = ("This was answered NO, but POTA's pin is inside the record and the names match. "
                         "Look at the agency map: is this official record that park? YES / NO")
    return q


def _counts(recs: Iterable[dict]) -> dict[str, int]:
    c = {v: 0 for v in VERDICTS}
    for r in recs:
        c[r["verdict"]] += 1
    return c


def _pct(c: dict[str, int]) -> str:
    judged = sum(c.values()) - c[CANT]
    fl = c["LOOK AGAIN"] + c["BETTER RECORD"]
    return f"{100 * fl / judged:.1f}%" if judged else "-"


def write_outputs(out: str, inputs: list[tuple[str, str, dict]], state: dict, cap: Cap, finished: bool) -> dict:
    built = utc_now()
    per_fa: dict[tuple[str, str], list[dict]] = {}
    questions: list[dict] = []
    withheld = 0
    cant_reasons: dict[str, int] = {}
    seen_q: dict[tuple, dict] = {}
    for fname, _path, data in inputs:
        st = state["files"].get(fname, {})
        recs = sorted(st.get("rows", {}).values(),
                      key=lambda r: (area_rank(r.get("area")), r.get("area") or "", r.get("_idx", 0)))
        write_json_atomic(os.path.join(out, fname), {
            "about": ("KPC 8 NO rechecker: one record per NO row. The input file was NOT changed; "
                      "verdicts are questions for a person, never answers."),
            "tool": f"kpc_no_recheck {VERSION}", "built": built, "input_file": fname,
            "input_sha256": st.get("input_sha256"), "finished": finished,
            "rows_selected": st.get("selected"), "rows_done": len(recs),
            "batches_stopped": {b: m for b, m in cap.stopped.items() if b.split("|")[1] == fname},
            "records": [{k: v for k, v in r.items() if not k.startswith("_")} for r in recs],
        })
        rows = data["questions"]
        for r in recs:
            per_fa.setdefault((fname, r.get("area") or "?"), []).append(r)
            if r["verdict"] == CANT:
                reason = re.sub(r"'[^']*'", "'…'", r["why"])
                reason = re.sub(r"\b\d+\b", "N", reason)
                cant_reasons[reason] = cant_reasons.get(reason, 0) + 1
            if r["verdict"] in ("LOOK AGAIN", "BETTER RECORD"):
                if cap.is_stopped(*batches_of(fname, r.get("area"))):
                    withheld += 1
                    continue
                q = build_question(rows[r["_idx"]], r, fname)
                sr = q["suggested_record"]
                dkey = (q.get("ref"), str(sr.get("record")), " ".join(norm_tokens(sr.get("record_name") or "")[0]))
                if dkey in seen_q:  # the same record served by another copy of the layer: one question
                    seen_q[dkey].setdefault("also_on_layers", []).append(sr.get("layer"))
                    continue
                seen_q[dkey] = q
                questions.append(q)
    write_json_atomic(os.path.join(out, "questions.json"), {
        "about": ("NO answers that may be wrong (KPC 8 NO rechecker). answer is null: a person answers YES / NO "
                  "after looking at the agency map. old_answer is the answer being questioned, evidence is one "
                  "plain line, suggested_record is the record to look at. The tool never changes an answer."),
        "built": built, "open": len(questions), "questions": questions,
    })
    fa_sorted = sorted(per_fa.items(), key=lambda x: (x[0][0], area_rank(x[0][1]), x[0][1]))
    with open(os.path.join(out, "report.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["file", "area", "rows", *VERDICTS, "flagged_pct_of_judged", "batch_stopped"])
        for (fname, area), recs in fa_sorted:
            c = _counts(recs)
            w.writerow([fname, area, len(recs), *[c[v] for v in VERDICTS], _pct(c).rstrip("%"),
                        cap.is_stopped(*batches_of(fname, area)) or ""])
    lines = ["# NO recheck summary", "",
             f"Built {built} by kpc_no_recheck {VERSION}. "
             + ("Finished." if finished else "**Not finished: run again with --resume.**"), "",
             "The tool never changes an answer. The input files were only read; their SHA-256 is in each output file.",
             "Flagged = LOOK AGAIN + BETTER RECORD, as a share of the rows judged (CAN'T TELL rows are not judged).", "",
             "## Verdicts per file", "",
             "| file | NO rows selected | done | LOOK AGAIN | BETTER RECORD | KEEP NO | CAN'T TELL | flagged |",
             "|---|---|---|---|---|---|---|---|"]
    allc = {v: 0 for v in VERDICTS}
    for fname, _p, _d in inputs:
        st = state["files"].get(fname, {})
        c = _counts(st.get("rows", {}).values())
        for v in VERDICTS:
            allc[v] += c[v]
        lines.append(f"| {fname} | {st.get('selected', 0)} | {sum(c.values())} | {c['LOOK AGAIN']} | "
                     f"{c['BETTER RECORD']} | {c['KEEP NO']} | {c[CANT]} | {_pct(c)} |")
    lines.append(f"| **all** | | {sum(allc.values())} | {allc['LOOK AGAIN']} | {allc['BETTER RECORD']} | "
                 f"{allc['KEEP NO']} | {allc[CANT]} | {_pct(allc)} |")
    lines += ["", "## Verdicts per file and area", "",
              "| file | area | rows | LOOK AGAIN | BETTER RECORD | KEEP NO | CAN'T TELL |", "|---|---|---|---|---|---|---|"]
    for (fname, area), recs in fa_sorted:
        c = _counts(recs)
        lines.append(f"| {fname} | {area} | {len(recs)} | {c['LOOK AGAIN']} | {c['BETTER RECORD']} | "
                     f"{c['KEEP NO']} | {c[CANT]} |")
    if cap.stopped:
        lines += ["", "## Batches stopped by the 15% safety cap", ""]
        for b, m in cap.stopped.items():
            lines.append(f"* `{b}`: {m}. Its flagged rows were NOT put in questions.json.")
    if cant_reasons:
        lines += ["", "## CAN'T TELL reasons (these rows are retried next run)", ""]
        for reason, n in sorted(cant_reasons.items(), key=lambda x: -x[1]):
            lines.append(f"* {n} × {reason}")
    lines += ["", f"## Questions written ({len(questions)}, all with answer: null)", ""]
    for q in questions:
        lines.append(f"* **{q['recheck_verdict']}** ({q['source_file']}, old answer {q['old_answer']!r}) {q['evidence']}")
    with open(os.path.join(out, "summary.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return {"totals": allc, "questions": len(questions), "withheld": withheld}


# ----------------------------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------------------------

def main(argv: list[str] | None = None, fetcher: Fetcher | None = None) -> int:
    ap = argparse.ArgumentParser(description="KPC 8 NO rechecker: writes questions for a person, never answers.")
    ap.add_argument("--files", nargs="+", required=True, help="question files (gis-hunter.json layers.json ...)")
    ap.add_argument("--in-dir", default="data/waiting/questions", help="where --files are looked for if not paths")
    ap.add_argument("--areas", nargs="+", help="only these areas (US-KY, CA-AB, AU ...)")
    ap.add_argument("--refs", nargs="+", help="only these POTA refs")
    ap.add_argument("--answers", nargs="+", default=["NO"],
                    help="answers to recheck (default: NO only; 'NOT SURE' is not a NO)")
    ap.add_argument("--limit", type=int, help="check at most this many rows in this run")
    ap.add_argument("--out", default="no_recheck")
    ap.add_argument("--resume", action="store_true", help="keep rows already done (CAN'T TELL rows are retried)")
    ap.add_argument("--max-minutes", type=float, default=50.0)
    ap.add_argument("--offline", action="store_true", help="cache only, no network")
    ap.add_argument("--min-interval", type=float, default=1.0, help="seconds between requests to one host (>= 1)")
    ap.add_argument("--cache-dir", help="default: <out>/cache")
    ap.add_argument("-v", "--verbose", action="store_true")
    a = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO if a.verbose else logging.WARNING, format="%(levelname)s %(message)s")
    deadline = time.time() + a.max_minutes * 60
    if a.min_interval < 1.0:
        print("bad input: --min-interval must be at least 1 second (club rule)", file=sys.stderr)
        return 2
    if a.limit is not None and a.limit < 0:
        print("bad input: --limit must be 0 or more", file=sys.stderr)
        return 2
    try:
        inputs = load_inputs(a.files, a.in_dir)
    except BadInput as e:
        print(f"bad input: {e}", file=sys.stderr)
        return 2
    out = a.out
    out_abs = os.path.abspath(out)
    for fname, path, _ in inputs:  # an output must never land on an input file
        if os.path.dirname(os.path.abspath(path)) == out_abs:
            print(f"bad input: --out {out} is the folder of the input {fname}; outputs would overwrite it",
                  file=sys.stderr)
            return 2
    os.makedirs(out, exist_ok=True)
    state_path = os.path.join(out, "state.json")
    state: dict = {"version": VERSION, "files": {}}
    if a.resume and os.path.exists(state_path):
        try:
            with open(state_path, encoding="utf-8") as fh:
                state = json.load(fh)
        except ValueError:
            print(f"bad input: {state_path} is not valid JSON", file=sys.stderr)
            return 2
    # the safety cap works on whole batches; a hand-picked --refs list is not a batch
    cap = Cap(minimum=10 ** 9) if a.refs else Cap()

    already = answered_records(r for _, _, d in inputs for r in d["questions"])
    queue = []
    for fi, (fname, path, data) in enumerate(inputs):
        st = state["files"].setdefault(fname, {"rows": {}})
        sha = sha256_file(path)
        if st.get("input_sha256") and st["input_sha256"] != sha:
            log.warning("%s changed since the last run: starting it again", fname)
            st["rows"] = {}
        st["input_sha256"] = sha
        sel = 0
        for idx, row in enumerate(data["questions"]):
            if not is_no(row.get("answer"), a.answers):
                continue
            if a.areas and not area_match(row.get("area"), a.areas):
                continue
            if a.refs and row.get("ref") not in a.refs:
                continue
            sel += 1
            queue.append((area_rank(row.get("area")), fi, idx, fname, row))
        st["selected"] = sel
    queue.sort(key=lambda x: (x[0], x[1], x[2]))
    for fname, st in state["files"].items():  # cap counts carry over on --resume
        for r in st.get("rows", {}).values():
            for b in batches_of(fname, r.get("area")):
                cap.add(b, r["verdict"])

    f = fetcher or Fetcher(a.cache_dir or os.path.join(out, "cache"), offline=a.offline,
                           min_interval=a.min_interval, hard_deadline=deadline + 240)
    if a.offline:
        f.offline = True
    reader = LayerReader(f)
    done_now = 0
    unfinished = False
    last_save = time.time()
    for _rank, _fi, idx, fname, row in queue:
        st = state["files"][fname]
        key = row_key(row, idx)
        prev = st["rows"].get(key)
        if prev and prev["verdict"] != CANT:
            continue
        if cap.is_stopped(*batches_of(fname, row.get("area"))):
            continue
        if (a.limit is not None and done_now >= a.limit) or time.time() > deadline:
            unfinished = True
            break
        try:
            rec = check_row(row, f, reader, already)
        except TimeUp:
            unfinished = True
            break
        except Exception as e:  # one failure never stops a batch
            log.exception("row %s failed", row.get("ref"))
            rec = blank_record(row)
            rec["verdict"] = CANT
            rec["why"] = f"The tool hit an error on this row ({e.__class__.__name__}: {str(e)[:120]})."
        rec["_idx"] = idx
        rec["file"] = fname
        st["rows"][key] = rec
        done_now += 1
        for b in batches_of(fname, row.get("area")):
            cap.add(b, rec["verdict"])
        print(f"[{done_now}] {fname} {row.get('area')} {row.get('ref')}: {rec['verdict']}: {rec['why']}", flush=True)
        if time.time() - last_save > 60:
            write_json_atomic(state_path, state)
            last_save = time.time()

    write_json_atomic(state_path, state)
    res = write_outputs(out, inputs, state, cap, finished=not unfinished)
    t = res["totals"]
    print(f"done {done_now} rows this run; totals: " + ", ".join(f"{k} {v}" for k, v in t.items())
          + f"; {res['questions']} questions written; {f.requests_made} requests, {f.cache_hits} cache hits")
    for b, m in cap.stopped.items():
        print(f"STOPPED {b}: {m}")
    if unfinished:
        print("not finished: run again with --resume")
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
