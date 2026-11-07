#!/usr/bin/env python3
"""kpc_gpspacks: build the KPC state GPS packs (spec KPC_10_GPS_Download_Spec.md part C).

For each area (US-KY, US-TN, ...) it writes, only inside --out:
  data/gps/<area>.gpx.zip         every park: POTA pin, official parking/access, outline (GPX 1.1)
  data/gps/<area>.kml.zip         the same as KML 2.2 (real polygons; folders Parking / Trails / Outline / 2-fers)
  data/gps/<area>-trails.gpx.zip  the official trail lines, kept apart so the main pack stays small
  data/gps/index.json             what was built, sizes, sources (for the "GPS downloads" page, which is on HOLD)
  report.md, state.json, work/    run report, resume state, working files

Run:      python kpc_gpspacks.py --parkinfo data/parkinfo/US-KY.json --access data/access/US-KY.json \\
              --keys data/us-key/US-KY.json --outlines outlines/ --trails trails/ --out out --areas US-KY
Selftest: python kpc_gpspacks.py --selftest      (offline; prints PASS or FAIL)
Exit codes: 0 all done, 3 time ran out with work left (run again with --resume), anything else a crash.
The label texts and the simplifier are the same as kpc_gps_site/kpc-gps.js; keep the two in step.
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import hashlib
import io
import json
import math
import os
import re
import shutil
import sys
import tempfile
import time
import zipfile
from xml.sax.saxutils import escape as _esc

VERSION = "0.1.0"
# ---- the exact texts from the spec; do not reword ----
NOTICE = "\u2139\ufe0f Maps and park info are a planning aid, not a guarantee. Always check the official agency map and rules before you go."
SITE_URL = "https://kentuckyportableclub.github.io/KPC-Links/"   # default site link (ruled Oct 31 2026); --site-url / KPC_SITE_URL override
PARKING_NO_AGENCY = "Parking (from an official access list; check the agency\u2019s map before you go)"   # ruled Oct 31 2026
FER_NOTICE = "\u26a0\ufe0f Parks' boundaries may overlap here, but we can't confirm it. Check both official boundary maps and make your own call before you count it."
PIN_LABEL = "POTA pin (activations happen inside the boundary, not at the pin)"
NEARBY_LABEL = "Nearby public access, not the park's own"
PULLOFF_LABEL = "Possible pull-off (aerial photo, not official)"
NO_OUTLINE = "No official outline yet"
SYM = {"pin": "Flag, Green", "parking": "Parking Area", "trailhead": "Trail Head", "boat": "Boat Ramp",
       "entrance": "Information", "pulloff": "Parking Area", "other": "Information"}
MAX_PTS = 2000
TOLS = [5, 10, 15, 20, 30, 50, 75, 100, 150, 200, 300, 500, 750, 1000, 1500, 2000, 3000, 5000]
REF_RE = re.compile(r"^[A-Z0-9]{1,4}-\d{1,6}$")
BANNED = re.compile(r"openstreetmap|overpass|geofabrik|google|alltrails|gaia|strava|tripadvisor|yelp|wikipedia|protectedplanet|wdpa|unep-wcmc", re.I)
HERE = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------- helpers
def num(v):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return f if math.isfinite(f) else None


def ok_ll(lat, lon):
    return lat is not None and lon is not None and abs(lat) <= 90 and abs(lon) <= 180 and not (lat == 0 and lon == 0)


def f7(x):
    r = round(x * 1e7) / 1e7
    s = repr(r)
    if "e" in s or "E" in s:
        s = f"{r:.7f}".rstrip("0").rstrip(".")
    return s[:-2] if s.endswith(".0") else s


_BAD = re.compile("[\x00-\x08\x0b\x0c\x0e-\x1f\ufffe\uffff]")


def xesc(s):
    return _esc(_BAD.sub("", "" if s is None else str(s)), {'"': "&quot;"})


def file_agency(d):
    """Agency named once for a whole access file (ASSUMED keys: agency, meta.agency, source.agency)."""
    if not isinstance(d, dict):
        return None
    for v in (d.get("agency"), (d.get("meta") or {}).get("agency") if isinstance(d.get("meta"), dict) else None,
              (d.get("source") or {}).get("agency") if isinstance(d.get("source"), dict) else None):
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None


def _parking_label(agency):
    return f"Parking (from {agency})" if agency else PARKING_NO_AGENCY


def cut(s, n):
    s = str(s).strip()
    if len(s) <= n:
        return s
    c = s[:n]
    i = c.rfind(" ")
    return (c[:i] if i >= n - 8 else c).strip()


def short_name(name):
    import unicodedata
    s = unicodedata.normalize("NFD", str(name or "park"))
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"[^A-Za-z0-9]+", "-", s.replace("&", " and ")).strip("-")
    if len(s) > 40:
        s = s[:40]
        if s.rfind("-") > 20:
            s = s[:s.rfind("-")]
    return s or "park"


# ---------------------------------------------------------------- geometry (same algorithm as kpc-gps.js)
def close_ring(r):
    out = []
    for p in r or []:
        if not isinstance(p, (list, tuple)) or len(p) < 2 or num(p[0]) is None or num(p[1]) is None:
            continue
        q = [num(p[0]), num(p[1])]
        if out and out[-1] == q:
            continue
        out.append(q)
    if out and out[0] != out[-1]:
        out.append(list(out[0]))
    return out if len(out) >= 4 else None


def polygons_of(geom):
    if not isinstance(geom, dict):
        return []
    t = geom.get("type")
    if t == "FeatureCollection":
        return [p for f in geom.get("features") or [] for p in polygons_of(f)]
    if t == "Feature":
        return polygons_of(geom.get("geometry"))
    if t == "GeometryCollection":
        return [p for gg in geom.get("geometries") or [] for p in polygons_of(gg)]
    polys = [geom.get("coordinates")] if t == "Polygon" else (geom.get("coordinates") if t == "MultiPolygon" else [])
    res = []
    for rings in polys or []:
        rr = [x for x in (close_ring(r) for r in rings or []) if x]
        if rr:
            res.append(rr)
    return res


def poly_tracts(geom, n):
    """Nov 7: the tract id of each polygon polygons_of() returns, when every feature carries properties.tract; else None."""
    if not isinstance(geom, dict) or geom.get("type") != "FeatureCollection":
        return None
    out, anyt = [], False
    for f in geom.get("features") or []:
        t = ((f or {}).get("properties") or {}).get("tract")
        anyt = anyt or bool(t)
        out += [t or ""] * len(polygons_of(f))
    return out if anyt and len(out) == n else None


def lines_of(geom):
    if not isinstance(geom, dict):
        return []
    t = geom.get("type")
    if t == "FeatureCollection":
        return [l for f in geom.get("features") or [] for l in lines_of(f)]
    if t == "Feature":
        return lines_of(geom.get("geometry"))
    ls = [geom.get("coordinates")] if t == "LineString" else (geom.get("coordinates") if t == "MultiLineString" else [])
    out = []
    for l in ls or []:
        pts = [[num(p[0]), num(p[1])] for p in l or [] if isinstance(p, (list, tuple)) and len(p) >= 2 and num(p[0]) is not None and num(p[1]) is not None]
        if len(pts) >= 2:
            out.append(pts)
    return out


def proj(pts):
    lat0 = sum(p[1] for p in pts) / len(pts) * math.pi / 180
    kx, ky = 111320 * math.cos(lat0), 110540
    return [(p[0] * kx, p[1] * ky) for p in pts]


def seg_dist(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = dx * dx + dy * dy
    t = 0.0
    if L > 0:
        t = ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L
        t = 0.0 if t < 0 else 1.0 if t > 1 else t
    x, y = a[0] + t * dx - p[0], a[1] + t * dy - p[1]
    return math.sqrt(x * x + y * y)


def dp_idx(xy, i0, i1, tol, keep):
    stack = [(i0, i1)]
    while stack:
        a, b = stack.pop()
        dmax, k = -1.0, -1
        for i in range(a + 1, b):
            d = seg_dist(xy[i], xy[a], xy[b])
            if d > dmax:
                dmax, k = d, i
        if k > 0 and dmax > tol:
            keep[k] = 1
            stack.append((a, k))
            stack.append((k, b))


def simplify_line(pts, tol):
    if len(pts) <= 2:
        return list(pts)
    xy = proj(pts)
    keep = bytearray(len(pts))
    keep[0] = keep[-1] = 1
    dp_idx(xy, 0, len(pts) - 1, tol, keep)
    return [p for i, p in enumerate(pts) if keep[i]]


def simplify_ring(ring, tol):
    n = len(ring)
    if n <= 4:
        return list(ring)
    xy = proj(ring)
    k, dmax = 1, -1.0
    for i in range(1, n - 1):
        dx, dy = xy[i][0] - xy[0][0], xy[i][1] - xy[0][1]
        d = dx * dx + dy * dy
        if d > dmax:
            dmax, k = d, i
    keep = bytearray(n)
    keep[0] = keep[k] = keep[n - 1] = 1
    dp_idx(xy, 0, k, tol, keep)
    dp_idx(xy, k, n - 1, tol, keep)
    out = [p for i, p in enumerate(ring) if keep[i]]
    if len(out) < 4:
        m, dm = -1, -1.0
        for j in range(1, n - 1):
            if j == k:
                continue
            dd = seg_dist(xy[j], xy[0], xy[k])
            if dd > dm:
                dm, m = dd, j
        if m < 0:
            return list(ring)
        idx = sorted([0, k, m])
        out = [ring[idx[0]], ring[idx[1]], ring[idx[2]], ring[0]]
    return out


def count_pts(polys):
    return sum(len(r) for p in polys for r in p)


def ring_area(r):
    xy = proj(r)
    return abs(sum(xy[i][0] * xy[i + 1][1] - xy[i + 1][0] * xy[i][1] for i in range(len(xy) - 1)) / 2)


def simplify_outline(polys, max_pts=MAX_PTS, tracts=None):
    """<= max_pts points for the whole outline: 5 m first, then coarser. -> (polys, tol, dropped, points)
    Nov 7 (KPC-Links tracts Part 1, mirrors kpc-gps.js simplifyOutline): `tracts` = the tract id of each polygon (only when the outline's
    features carry properties.tract, i.e. the hidden tract switch was on where it was read). Then every tract keeps its biggest outer
    ring before the size trim, so a small tract is never left out whole. Without it: exactly as before."""
    res, tol = polys, TOLS[0]
    for tol in TOLS:
        res = [[simplify_ring(r, tol) for r in p] for p in polys]
        if count_pts(res) <= max_pts:
            return res, tol, 0, count_pts(res)
    pieces = sorted(((pi, ri, ring_area(r), len(r)) for pi, p in enumerate(res) for ri, r in enumerate(p)), key=lambda x: -x[2])
    total, keep, dropped = 0, set(), 0
    if tracts is not None and len(tracts) == len(res):
        first = {}
        for pi, ri, _a, n in pieces:
            if ri == 0 and str(tracts[pi]) not in first: first[str(tracts[pi])] = (pi, ri, n)
        for pi, ri, n in first.values():
            total += n
            keep.add((pi, ri))
        pieces = [x for x in pieces if (x[0], x[1]) not in keep]
    for pi, ri, _a, n in pieces:
        if total + n <= max_pts:
            total += n
            keep.add((pi, ri))
        else:
            dropped += 1
    out = [[r for ri, r in enumerate(p) if (pi, ri) in keep] for pi, p in enumerate(res) if (pi, 0) in keep]
    return out, tol, dropped, count_pts(out)


def simplify_lines(lines, max_pts=MAX_PTS):
    res, tol = lines, TOLS[0]
    for tol in TOLS:
        res = [simplify_line(l, tol) for l in lines]
        if sum(len(l) for l in res) <= max_pts:
            break
    return res, tol, sum(len(l) for l in res)


# ---------------------------------------------------------------- tolerant readers (shapes assumed; see README)
def access_kind(label):
    s = str(label or "")
    i = s.find(":")
    text = (s[i + 1:] if i >= 0 else s).strip()
    l = text.lower()
    if re.search(r"pull-?off|candidate", l):
        return "pulloff", text
    if re.search(r"boat|ramp|launch", l):
        return "boat", text
    if re.search(r"trail ?head", l):
        return "trailhead", text
    if re.search(r"entrance|entry|gate", l):
        return "entrance", text
    if re.search(r"parking|lot\b", l):
        return "parking", text
    return "other", text or "Access point"


def outside_flag(o):
    if not isinstance(o, dict):
        return False
    if o.get("outside") is True or o.get("out") is True or o.get("nearby") is True or o.get("inside") is False or o.get("own") is False:
        return True
    return str(o.get("where") or o.get("side") or o.get("position") or "").lower() in ("outside", "out", "nearby")


NOT_AGENCY = re.compile(r"^(work in progress|n/?a|none|unknown|all managers|tbd|\d+)$|^(kpc|just outside|outside|inside|near)\b", re.I)


def label_agency(label):
    """chat 10 Oct 31 (real files): the club's access rows are [lat, lon, label, how] with the agency in the label's last brackets,
    e.g. 'Parking (Tennessee Wildlife Resources Agency)', 'Boat ramp / launch: Gallaher (TWRA; all managers)'; no agency field."""
    m = re.search(r"\(([^()]*)\)\s*$", str(label or ""))
    a = (m.group(1).split(";")[0].strip() if m else "")
    return "" if not a or NOT_AGENCY.match(a) else a


def _pt(lat, lon, label, o):
    o = o if isinstance(o, dict) else {}
    return {"lat": lat, "lon": lon, "label": label or "", "agency": o.get("agency") or label_agency(label), "outside": outside_flag(o),
            "grade": o.get("grade") or o.get("answer"), "source_url": o.get("source_url"), "read_date": o.get("read_date")}


def read_access(obj):
    """-> {ref: [point]}; accepts {"parks": {ref: [[lat, lon, "Park: Parking", {..}], ..]}}, Kentucky's {"ap": ..},
    GeoJSON points with properties.ref, and dict rows with lat/lon."""
    out = {}

    def add(ref, p):
        if ref:
            out.setdefault(ref, []).append(p)

    def walk(o, ref, depth):
        if depth > 10 or o is None:
            return
        if isinstance(o, list):
            if len(o) >= 2 and all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in o[:2]):
                a, b = float(o[0]), float(o[1])
                if abs(a) <= 90 and (abs(b) > 90 or (a > 0 > b)):
                    lat, lon = a, b
                else:
                    lon, lat = a, b
                strs = [v for v in o[2:] if isinstance(v, str)]
                lab = next((v for v in strs if not re.match(r"^(outside|out|nearby|inside)$", v, re.I)), "")
                extra = next((v for v in o[2:] if isinstance(v, dict)), {})
                p = _pt(lat, lon, lab, extra)
                p["outside"] = p["outside"] or any(re.match(r"^(outside|out|nearby)$", v, re.I) for v in strs)
                if ok_ll(lat, lon):
                    add(ref, p)
                return
            for v in o:
                walk(v, ref, depth + 1)
            return
        if isinstance(o, dict):
            if o.get("type") == "FeatureCollection":
                for f in o.get("features") or []:
                    walk(f, ref, depth + 1)
                return
            if o.get("type") == "Feature" and isinstance(o.get("geometry"), dict) and o["geometry"].get("type") == "Point":
                pr, c = o.get("properties") or {}, o["geometry"].get("coordinates") or []
                lat, lon = (num(c[1]), num(c[0])) if len(c) > 1 else (None, None)
                if ok_ll(lat, lon):
                    add(pr.get("ref") or pr.get("park") or ref, _pt(lat, lon, pr.get("label") or pr.get("name") or pr.get("kind") or pr.get("type"), pr))
                return
            la = num(o.get("lat", o.get("latitude")))
            lo = num(o.get("lon", o.get("lng", o.get("longitude"))))
            if ok_ll(la, lo):
                add(o.get("ref") or o.get("park") or ref, _pt(la, lo, o.get("label") or o.get("name") or o.get("kind") or o.get("type"), o))
                return
            for k, v in o.items():
                if isinstance(v, (dict, list)):
                    walk(v, k if isinstance(k, str) and REF_RE.match(k) else ref, depth + 1)

    walk(obj["ap"] if isinstance(obj, dict) and "ap" in obj and "parks" not in obj else obj, None, 0)
    return out


def read_parkinfo(obj, stem):
    """-> list of (area, park dict) from data/parkinfo/US-XX.json, CA.json (column 10 = province) or data/pota/t/*.json."""
    out = []
    parks = obj.get("parks", obj) if isinstance(obj, dict) else obj
    if isinstance(parks, dict):
        items = parks.items()
    elif isinstance(parks, list):          # world rows [ref, name, lat, lon]
        items = [(r[0], r) for r in parks if isinstance(r, list) and r and isinstance(r[0], str)]
    else:
        items = []
    for ref, row in items:
        if isinstance(row, list):
            if row and row[0] == ref:
                p = {"ref": ref, "name": row[1] if len(row) > 1 else ref, "lat": num(row[2]) if len(row) > 2 else None, "lon": num(row[3]) if len(row) > 3 else None}
                area = ref.split("-")[0]
            else:
                p = {"ref": ref, "name": row[0] if row else ref, "lat": num(row[5]) if len(row) > 5 else None, "lon": num(row[6]) if len(row) > 6 else None}
                area = stem
                if stem == "CA" and len(row) > 10 and isinstance(row[10], str) and row[10]:
                    area = "CA-" + row[10]
        elif isinstance(row, dict):
            p = {"ref": ref, "name": row.get("name") or row.get("n") or ref, "lat": num(row.get("lat")), "lon": num(row.get("lon", row.get("lng")))}
            area = stem
        else:
            continue
        out.append((area, p))
    return out


def read_fers(obj):
    out = []

    def refs_of(o):
        r = [o[k] for k in ("a", "b", "ref", "ref_a", "ref_b", "park", "other", "with") if isinstance(o.get(k), str) and REF_RE.match(o[k])]
        for k in ("refs", "parks", "pair"):
            if isinstance(o.get(k), list):
                r += [x for x in o[k] if isinstance(x, str) and REF_RE.match(x)]
        return list(dict.fromkeys(r))

    def walk(o, key, depth):
        if depth > 8 or not isinstance(o, (dict, list)):
            return
        if isinstance(o, list):
            if len(o) >= 4 and isinstance(o[0], str) and isinstance(o[1], str) and REF_RE.match(o[0]) and REF_RE.match(o[1]):
                la, lo = num(o[2]), num(o[3])
                if ok_ll(la, lo):
                    out.append({"refs": [o[0], o[1]], "lat": la, "lon": lo, "note": o[4] if len(o) > 4 and isinstance(o[4], str) else ""})
                return
            for v in o:
                walk(v, key, depth + 1)
            return
        la, lo = num(o.get("lat")), num(o.get("lon", o.get("lng")))
        if o.get("type") == "Feature" and isinstance(o.get("geometry"), dict) and o["geometry"].get("type") == "Point":
            c = o["geometry"]["coordinates"]
            la, lo = num(c[1]), num(c[0])
            o = dict(o.get("properties") or {})
        rs = refs_of(o)
        if key and REF_RE.match(key) and key not in rs:
            rs.insert(0, key)
        if ok_ll(la, lo) and len(rs) >= 2:
            out.append({"refs": rs, "lat": la, "lon": lo, "note": o.get("note") or o.get("name") or "", "source_url": o.get("source_url")})
            return
        for k, v in o.items():
            walk(v, k if isinstance(k, str) and REF_RE.match(k) else key, depth + 1)

    walk(obj, None, 0)
    return out


def norm_status(s):
    s = str(s or "").lower()
    if s.startswith("off"):
        return "official"
    if s.startswith("appr") or s.startswith("trace") or "picture" in s:
        return "approximate"
    return "pin"


def outline_label(st, agency, why):
    if st == "official":
        return f"Official boundary ({(agency or '').strip() or 'the managing agency'})"
    if st == "approximate":
        return f"Approximate outline ({why or 'no official file yet'})"
    return NO_OUTLINE


# ---------------------------------------------------------------- model (mirrors kpc-gps.js model())
def model(park, opts):
    ref, name = park["ref"], park.get("name") or park["ref"]
    o = park.get("outline") or {}
    st = norm_status(o.get("status") or park.get("g"))
    polys = [] if st == "pin" else polygons_of(o.get("geojson"))
    m = {"ref": ref, "name": name, "lat": park.get("lat"), "lon": park.get("lon"), "status": st, "agency": o.get("agency"), "why": o.get("why")}
    m["outline_label"] = outline_label(st, m["agency"], m["why"])
    m["polys"] = polys
    m["poly_tracts"] = None if st == "pin" else poly_tracts(o.get("geojson"), len(polys))   # Nov 7: None unless tract-labelled
    m["outline_missing"] = st != "pin" and not polys
    acc, counts = [], {}
    for a in park.get("access") or []:
        kind, text = access_kind(a.get("label"))
        if kind == "pulloff" and (not opts.get("pulloffs") or str(a.get("grade") or "").upper() != "YES"):
            continue
        if kind == "parking":
            label = text if re.match(r"^parking\s*\(from .+\)$", text, re.I) else \
                _parking_label((a.get('agency') or '').strip() or (a.get('file_agency') or '').strip())  # access data's own agency only, never the outline's (ruled Oct 31 2026 9:41 PM CT)
        else:
            label = {"entrance": "Entrance", "boat": "Boat ramp", "trailhead": "Trailhead", "pulloff": PULLOFF_LABEL}.get(kind, text)
        short = {"parking": "Parking", "entrance": "Entrance", "boat": "Boat ramp", "trailhead": "Trailhead", "pulloff": "Pull-off?"}.get(kind) or cut(text, 14)
        if a.get("outside"):
            short = "Nearby " + short.lower()
        counts[short] = counts.get(short, 0) + 1
        acc.append({"lat": a["lat"], "lon": a["lon"], "kind": kind, "label": label, "outside": bool(a.get("outside")), "sym": SYM[kind],
                    "short": short, "n": counts[short], "source_url": a.get("source_url") or park.get("access_source")})
    for a in acc:
        if counts[a["short"]] < 2:
            a["n"] = 0
    m["access"] = acc
    m["trails"] = []
    for t in park.get("trails") or []:
        lines = lines_of(t.get("geojson"))
        if lines:
            nm = t.get("name") or "Trail"
            m["trails"].append({"name": nm, "lines": lines, "label": f"{nm} (official line, {(t.get('agency') or '').strip() or 'the managing agency'})"})
    m["fers"] = list(park.get("fers") or []) if opts.get("fers") else []
    return m


def wname(m, a):
    return cut(f"{m['ref']} {a['short']}" + (f" {a['n']}" if a["n"] else ""), 30)


def pin_desc(m):
    d = f"{m['ref']} {m['name']}. {PIN_LABEL}."
    if m["status"] == "pin":
        d += f" {NO_OUTLINE}."
    elif m["outline_missing"]:
        d += f" Outline: {m['outline_label']}, not in this file (see the park card)."
    else:
        d += f" Outline: {m['outline_label']}."
    return d


def file_desc(o, any_fers):
    d = f"{NOTICE}\nData built: {o['built']}\nSite: {o['site']}"
    if any_fers:
        d += "\n" + FER_NOTICE
    return d


# ---------------------------------------------------------------- writers
def gpx_doc(ms, o, what="parks"):
    """what: 'parks' (pins, access, outlines, 2-fers) or 'trails' (trail lines only)."""
    any_fers = what == "parks" and any(m["fers"] for m in ms)
    L = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<gpx version="1.1" creator="KPC kpc_gpspacks.py" xmlns="http://www.topografix.com/GPX/1/1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
         'xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">',
         f"<metadata><name>{xesc(o['title'])}</name><desc>{xesc(file_desc(o, any_fers))}</desc>"]
    if re.match(r"^https?://", o["site"]):
        L.append(f'<link href="{xesc(o["site"])}"><text>Kentucky Portable Club</text></link>')
    L.append(f"<time>{o['time']}</time>")
    pts = [(m["lat"], m["lon"]) for m in ms if ok_ll(m["lat"], m["lon"])] + [(a["lat"], a["lon"]) for m in ms for a in m["access"]]
    if pts and what == "parks":
        L.append(f'<bounds minlat="{f7(min(p[0] for p in pts))}" minlon="{f7(min(p[1] for p in pts))}" maxlat="{f7(max(p[0] for p in pts))}" maxlon="{f7(max(p[1] for p in pts))}"/>')
    L.append("</metadata>")
    stats = {"wpt": 0, "trk": 0, "outline_points": [], "tols": []}

    def wpt(lat, lon, name, desc, src, sym, typ):
        stats["wpt"] += 1
        L.append(f'<wpt lat="{f7(lat)}" lon="{f7(lon)}"><name>{xesc(cut(name, 30))}</name><desc>{xesc(desc)}</desc>'
                 + (f"<src>{xesc(src)}</src>" if src else "") + (f"<sym>{xesc(sym)}</sym>" if sym else "") + (f"<type>{xesc(typ)}</type>" if typ else "") + "</wpt>")

    if what == "parks":
        for m in ms:
            if ok_ll(m["lat"], m["lon"]):
                wpt(m["lat"], m["lon"], f"{m['ref']} {m['name']}", pin_desc(m), "POTA park pin (data/parkinfo)", SYM["pin"], "POTA pin")
            for a in m["access"]:
                desc = (f"{NEARBY_LABEL}: {a['label']}" if a["outside"] else a["label"]) + f". {m['ref']} {m['name']}."
                wpt(a["lat"], a["lon"], wname(m, a), desc, a.get("source_url") or "KPC access file (data/access)", a["sym"],
                    "Nearby access" if a["outside"] else "Possible pull-off" if a["kind"] == "pulloff" else "Official access")
            for f in m["fers"]:
                wpt(f["lat"], f["lon"], "2-fer " + "+".join(f["refs"]), f"{FER_NOTICE} Possible 2-fer spot: {' + '.join(f['refs'])}" + (f". {f['note']}" if f.get("note") else "") + ".",
                    f.get("source_url") or "KPC 2-fer rows (data/fers)", None, "2-fer spot")
        for m in ms:
            if not m["polys"]:
                continue
            polys, tol, dropped, npts = simplify_outline(m["polys"], o["max_points"], m.get("poly_tracts"))
            stats["trk"] += 1
            stats["outline_points"].append(npts)
            stats["tols"].append(tol)
            kind = "Official" if m["status"] == "official" else "Approximate"
            L.append(f"<trk><name>{xesc(m['ref'] + ' boundary (' + kind + ')')}</name><desc>"
                     + xesc(f"{m['outline_label']}. {m['ref']} {m['name']}. Simplified to ~{tol} m for GPS units ({npts} points)" + (f"; {dropped} small pieces left out" if dropped else "") + ".")
                     + f"</desc><type>{'Official boundary' if m['status'] == 'official' else 'Approximate outline'}</type>")
            for p in polys:
                for r in p:
                    L.append("<trkseg>" + "".join(f'<trkpt lat="{f7(c[1])}" lon="{f7(c[0])}"/>' for c in r) + "</trkseg>")
            L.append("</trk>")
    else:
        for m in ms:
            for t in m["trails"]:
                lines, tol, npts = simplify_lines(t["lines"], o["max_points"])
                stats["trk"] += 1
                desc = f"{t['label']}. {m['ref']} {m['name']}. Simplified to ~{tol} m for GPS units ({npts} points)."
                L.append(f"<trk><name>{xesc(cut(t['name'], 30))}</name><desc>{xesc(desc)}</desc><type>Trail</type>")
                for l in lines:
                    L.append("<trkseg>" + "".join(f'<trkpt lat="{f7(c[1])}" lon="{f7(c[0])}"/>' for c in l) + "</trkseg>")
                L.append("</trk>")
    L.append("</gpx>")
    return "\n".join(L) + "\n", stats


KSTYLE = [
    '<Style id="pin"><IconStyle><color>ff00c000</color><scale>1.3</scale></IconStyle><LabelStyle><scale>0.9</scale></LabelStyle></Style>',
    '<Style id="parking"><IconStyle><color>ffff6600</color><scale>1.0</scale></IconStyle></Style>',
    '<Style id="entrance"><IconStyle><color>ffffffff</color><scale>1.0</scale></IconStyle></Style>',
    '<Style id="boat"><IconStyle><color>ffffff00</color><scale>1.0</scale></IconStyle></Style>',
    '<Style id="trailhead"><IconStyle><color>ff2f6b8b</color><scale>1.0</scale></IconStyle></Style>',
    '<Style id="other"><IconStyle><color>ffcccccc</color><scale>0.9</scale></IconStyle></Style>',
    '<Style id="nearby"><IconStyle><color>ff888888</color><scale>0.8</scale></IconStyle></Style>',
    '<Style id="pulloff"><IconStyle><color>ff0080ff</color><scale>0.8</scale></IconStyle></Style>',
    '<Style id="fer"><IconStyle><color>ffff00ff</color><scale>1.0</scale></IconStyle></Style>',
    '<Style id="official"><LineStyle><color>ff00ffff</color><width>3</width></LineStyle><PolyStyle><color>3300ffff</color><outline>1</outline></PolyStyle></Style>',
    '<Style id="approxfill"><LineStyle><color>0000ffff</color><width>0</width></LineStyle><PolyStyle><color>2200ffff</color><outline>0</outline></PolyStyle></Style>',
    '<Style id="dash"><LineStyle><color>ff00ffff</color><width>3</width></LineStyle></Style>',
    '<Style id="trail"><LineStyle><color>ff1e3cdc</color><width>3</width></LineStyle></Style>',
]


def kc(r):
    return " ".join(f"{f7(c[0])},{f7(c[1])}" for c in r)


def dashes(ring):
    """KML has no dashed line style, so an approximate outline is drawn as short dashes."""
    xy = proj(ring)
    per = sum(math.hypot(xy[i + 1][0] - xy[i][0], xy[i + 1][1] - xy[i][1]) for i in range(len(xy) - 1))
    dash = max(15.0, min(400.0, per / 120))
    out, cur, on, left = [], [ring[0]], True, dash
    for i in range(len(xy) - 1):
        a, b = ring[i], ring[i + 1]
        seg_l = math.hypot(xy[i + 1][0] - xy[i][0], xy[i + 1][1] - xy[i][1])
        pos = 0.0
        while seg_l - pos > left:
            pos += left
            t = pos / seg_l
            p = [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t]
            if on:
                cur.append(p)
                out.append(cur)
                cur = []
            else:
                cur = [p]
            on, left = not on, dash
        left -= seg_l - pos
        if on:
            cur.append(b)
    if on and len(cur) >= 2:
        out.append(cur)
    return [d for d in out if len(d) >= 2]


def kml_doc(ms, o):
    any_fers = any(m["fers"] for m in ms)
    L = ['<?xml version="1.0" encoding="UTF-8"?>',
         f'<kml xmlns="http://www.opengis.net/kml/2.2"><Document><name>{xesc(o["title"])}</name><open>1</open><description>{xesc(file_desc(o, any_fers))}</description>']
    L += KSTYLE

    def pm(name, desc, style, geom):
        L.append(f"<Placemark><name>{xesc(name)}</name><description>{xesc(desc)}</description><styleUrl>#{style}</styleUrl>{geom}</Placemark>")

    def pt(lat, lon):
        return f"<Point><coordinates>{f7(lon)},{f7(lat)}</coordinates></Point>"

    L.append("<Folder><name>Park pins</name>")
    for m in ms:
        if ok_ll(m["lat"], m["lon"]):
            pm(f"{m['ref']} {m['name']}", pin_desc(m), "pin", pt(m["lat"], m["lon"]))
    L.append(f"</Folder><Folder><name>Parking</name><description>Official parking and access points from the club's access files. Grey points: {xesc(NEARBY_LABEL)}.</description>")
    for m in ms:
        for a in m["access"]:
            pm(NEARBY_LABEL if a["outside"] else a["label"], (f"{NEARBY_LABEL}: {a['label']}" if a["outside"] else a["label"]) + f". {m['ref']} {m['name']}.",
               "nearby" if a["outside"] else a["kind"], pt(a["lat"], a["lon"]))
    L.append("</Folder><Folder><name>Trails</name><description>Trail lines are in the separate trails pack (&lt;area&gt;-trails.gpx.zip).</description></Folder><Folder><name>Outline</name>")
    for m in ms:
        if not m["polys"]:
            if m["status"] == "pin":
                L.append(f"<Placemark><name>{xesc(m['ref'] + ': ' + NO_OUTLINE)}</name><description>{xesc(m['ref'] + ' ' + m['name'] + '. ' + NO_OUTLINE + '. No outline is drawn.')}</description></Placemark>")
            continue
        polys, tol, dropped, npts = simplify_outline(m["polys"], o["max_points"], m.get("poly_tracts"))
        extra = f" Simplified to ~{tol} m ({npts} points)" + (f"; {dropped} small pieces left out" if dropped else "") + "."
        pg = "".join("<Polygon><tessellate>1</tessellate><outerBoundaryIs><LinearRing><coordinates>" + kc(p[0]) + "</coordinates></LinearRing></outerBoundaryIs>"
                     + "".join("<innerBoundaryIs><LinearRing><coordinates>" + kc(r) + "</coordinates></LinearRing></innerBoundaryIs>" for r in p[1:]) + "</Polygon>" for p in polys)
        desc = f"{m['outline_label']}. {m['ref']} {m['name']}.{extra}"
        nm = f"{m['ref']} boundary ({'Official' if m['status'] == 'official' else 'Approximate'})"
        if m["status"] == "official":
            pm(nm, desc, "official", f"<MultiGeometry>{pg}</MultiGeometry>")
        else:
            ds = [d for p in polys for r in p for d in dashes(r)]
            pm(nm, desc + " Dashed line: approximate.", "approxfill", f"<MultiGeometry>{pg}</MultiGeometry>")
            pm(nm + " line", desc + " Dashed line: approximate.", "dash",
               "<MultiGeometry>" + "".join(f"<LineString><tessellate>1</tessellate><coordinates>{kc(d)}</coordinates></LineString>" for d in ds) + "</MultiGeometry>")
    L.append("</Folder>")
    if any_fers:
        L.append(f"<Folder><name>2-fers</name><description>{xesc(FER_NOTICE)}</description>")
        for m in ms:
            for f in m["fers"]:
                pm("2-fer " + " + ".join(f["refs"]), f"{FER_NOTICE} Possible 2-fer spot: {' + '.join(f['refs'])}" + (f". {f['note']}" if f.get("note") else "") + ".", "fer", pt(f["lat"], f["lon"]))
        L.append("</Folder>")
    L.append("</Document></kml>")
    return "\n".join(L) + "\n"


def zip_bytes(members):
    bio = io.BytesIO()
    with zipfile.ZipFile(bio, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name, text in members:
            zi = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            zi.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(zi, text.encode("utf-8"))
    return bio.getvalue()


# ---------------------------------------------------------------- inputs
def area_of_file(path):
    stem = os.path.splitext(os.path.basename(path))[0]
    if stem.lower().startswith("kpc-ky-data"):
        return "US-KY"
    return stem


def expand(paths, exts=(".json", ".geojson")):
    out = []
    for p in paths or []:
        for q in sorted(glob.glob(p)) or [p]:
            if os.path.isdir(q):
                out += sorted(os.path.join(q, f) for f in os.listdir(q) if f.lower().endswith(exts))
            else:
                out.append(q)
    return out


def load_json(path, problems):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception as e:  # noqa: BLE001 - a bad file is reported, never fatal
        problems.append(f"input `{path}` not read: {e}")
        return None


def _features(d, f):
    if not isinstance(d, dict):
        return []
    if d.get("type") == "FeatureCollection":
        return d.get("features") or []
    if d.get("type") == "Feature":
        return [d]
    if d.get("type") in ("Polygon", "MultiPolygon", "LineString", "MultiLineString"):   # bare geometry: ref from the file name
        return [{"type": "Feature", "properties": {"ref": os.path.splitext(os.path.basename(f))[0].split("_")[0]}, "geometry": d}]
    return []


def load_inputs(a, problems):
    I = {"parks": {}, "access": {}, "keys": {}, "outlines": {}, "trails": {}, "fers": {}, "files": {}, "shared": set()}
    for f in expand(a.parkinfo):
        d = load_json(f, problems)
        if d is None:
            continue
        for area, p in read_parkinfo(d, area_of_file(f)):
            I["parks"].setdefault(area, []).append(p)
            I["files"].setdefault(area, set()).add(f)
    for f in expand(a.access):
        d = load_json(f, problems)
        if d is None:
            continue
        for ref, pts in read_access(d).items():
            for p in pts:
                p["source_url"] = p.get("source_url") or f"data/access/{os.path.basename(f)}"
                p["file_agency"] = file_agency(d)
            I["access"].setdefault(ref, []).extend(pts)
        I["files"].setdefault(area_of_file(f), set()).add(f)
    for f in expand(a.keys):
        d = load_json(f, problems)
        if isinstance(d, dict) and isinstance(d.get("parks"), dict):
            I["keys"].update(d["parks"])
            I["files"].setdefault(area_of_file(f), set()).add(f)
    for f in expand(a.outlines):
        d = load_json(f, problems)
        for ft in _features(d, f):
            pr = ft.get("properties") or {}
            ref = str(pr.get("ref") or pr.get("reference") or "")
            I["shared"].add(f)
            if not REF_RE.match(ref):
                problems.append(f"outline feature in `{f}` has no park ref; skipped")
                continue
            cur = I["outlines"].get(ref)
            if cur:
                cur["geojson"]["features"].append(ft)
            else:
                I["outlines"][ref] = {"status": pr.get("status") or pr.get("g"), "agency": pr.get("agency"), "why": pr.get("why"),
                                      "geojson": {"type": "FeatureCollection", "features": [ft]}}
    for f in expand(a.trails):
        I["shared"].add(f)
        d = load_json(f, problems)
        for ft in _features(d, f):
            pr = ft.get("properties") or {}
            if REF_RE.match(str(pr.get("ref") or "")):
                I["trails"].setdefault(pr["ref"], []).append({"name": pr.get("name") or "Trail", "agency": pr.get("agency"), "geojson": ft})
    if a.include_fers:
        for f in expand(a.fers):
            d = load_json(f, problems)
            if d is None:
                continue
            for row in read_fers(d):
                for r in row["refs"]:
                    I["fers"].setdefault(r, []).append(row)
            I["files"].setdefault(area_of_file(f), set()).add(f)
    return I


def park_record(p, I):
    ref = p["ref"]
    key = I["keys"].get(ref) or {}
    ol = I["outlines"].get(ref) or {}
    st = key.get("g") or ol.get("status") or ("official" if ol else "pin")
    agency = ol.get("agency")
    src = key.get("src") or []
    if not agency and src:
        s0 = src[0]
        agency = s0.get("agency") if isinstance(s0, dict) else s0 if isinstance(s0, str) and not s0.startswith("http") else None
    why = ol.get("why")
    if not why and key.get("m") and isinstance(key["m"][0], list) and len(key["m"][0]) > 3:
        why = key["m"][0][3]
    if not why and re.search(r"trace|picture", str(st), re.I):
        why = "traced from the agency's picture map"
    return dict(p, outline={"status": st, "agency": agency, "why": why, "geojson": ol.get("geojson")},
                access=I["access"].get(ref, []), trails=I["trails"].get(ref, []), fers=I["fers"].get(ref, []))


def inputs_hash(area, I):
    h = hashlib.sha256()
    if "shared_hash" not in I:          # outline / trail files serve every area: hash them once a run
        hs = hashlib.sha256()
        for f in sorted(I["shared"]):
            try:
                with open(f, "rb") as fh:
                    for chunk in iter(lambda: fh.read(1 << 20), b""):
                        hs.update(chunk)
            except OSError:
                pass
        I["shared_hash"] = hs.hexdigest()
    h.update(I["shared_hash"].encode())
    for f in sorted(I["files"].get(area, ())):
        try:
            with open(f, "rb") as fh:
                h.update(fh.read())
        except OSError:
            pass
    for p in I["parks"].get(area, []):
        h.update(json.dumps([I["outlines"].get(p["ref"], {}).get("geojson"), I["trails"].get(p["ref"])], sort_keys=True).encode())
    return h.hexdigest()[:16]


# ---------------------------------------------------------------- one area
def split_groups(ms, max_tracks):
    """Garmin units hold about 200 tracks: split the GPX so no file has more outline tracks than that."""
    n_out = sum(1 for m in ms if m["polys"])
    parts = max(1, math.ceil(n_out / max_tracks))
    per = math.ceil(n_out / parts) if n_out else 1
    groups, cur, cnt = [], [], 0
    for m in ms:
        if m["polys"] and cnt == per:
            groups.append(cur)
            cur, cnt = [], 0
        cur.append(m)
        cnt += 1 if m["polys"] else 0
    groups.append(cur)
    return groups


def build_area(area, I, a, opts, deadline, report):
    parks = I["parks"].get(area, [])
    if a.limit:
        parks = parks[: a.limit]
    ms, bad = [], []
    for i, p in enumerate(parks):
        if i % 25 == 0 and time.time() > deadline:
            return None
        try:
            if not ok_ll(p.get("lat"), p.get("lon")):
                bad.append((p["ref"], "no usable lat/lon in the parkinfo row"))
                continue
            m = model(park_record(p, I), opts)
            if m["outline_missing"]:
                report["problems"].append(f"{p['ref']}: key says {m['status']} but no outline geometry was given; pin + parking only")
            ms.append(m)
        except Exception as e:  # noqa: BLE001 - one bad park never stops the run
            bad.append((p["ref"], f"{type(e).__name__}: {e}"))
    for ref, why in bad:
        report["problems"].append(f"{ref}: left out ({why})")
    if not ms:
        report["problems"].append(f"{area}: no parks to write")
        return {"area": area, "parks": 0, "files": []}
    seen = set()                      # a 2-fer spot shared by two parks goes in once
    for m in ms:
        keep = []
        for f in m["fers"]:
            k = ("+".join(sorted(f["refs"])), f7(f["lat"]), f7(f["lon"]))
            if k not in seen:
                seen.add(k)
                keep.append(f)
        m["fers"] = keep
    gps = os.path.join(a.out, "data", "gps")
    os.makedirs(gps, exist_ok=True)
    max_bytes = int(a.max_mb * 1024 * 1024)
    res = {"area": area, "parks": len(ms), "files": [], "pin_only": sum(1 for m in ms if m["status"] == "pin"),
           "official": sum(1 for m in ms if m["status"] == "official" and m["polys"]),
           "approximate": sum(1 for m in ms if m["status"] == "approximate" and m["polys"]),
           "access_points": sum(len(m["access"]) for m in ms), "fers": sum(len(m["fers"]) for m in ms)}
    for max_pts in (MAX_PTS, 1000, 500, 250):
        o = dict(opts, max_points=max_pts)
        groups = split_groups(ms, a.max_tracks)
        members, stats_all = [], []
        for k, grp in enumerate(groups):
            many = len(groups) > 1
            suffix = f"_part{k + 1}of{len(groups)}" if many else ""
            title = f"KPC {area} parks {opts['date']}" + (f" (part {k + 1} of {len(groups)})" if many else "")
            text, st = gpx_doc(grp, dict(o, title=title))
            members.append((f"KPC_{area}_parks_{opts['date']}{suffix}.gpx", text))
            stats_all.append(st)
        gz = zip_bytes(members)
        kz = zip_bytes([(f"KPC_{area}_parks_{opts['date']}.kml", kml_doc(ms, dict(o, title=f"KPC {area} parks {opts['date']}")))])
        if len(gz) <= max_bytes and len(kz) <= max_bytes:
            break
        report["problems"].append(f"{area}: pack over {a.max_mb} MB with {max_pts} points per outline; trying coarser")
    else:
        report["problems"].append(f"{area}: pack still over {a.max_mb} MB at 250 points per outline (written anyway; needs a split)")
    for name, data in ((f"{area}.gpx.zip", gz), (f"{area}.kml.zip", kz)):
        with open(os.path.join(gps, name), "wb") as fh:
            fh.write(data)
        res["files"].append({"file": f"data/gps/{name}", "bytes": len(data)})
    pts = [n for st in stats_all for n in st["outline_points"]]
    res.update({"gpx_parts": len(members), "max_points_per_outline": max_pts, "outline_points_max": max(pts) if pts else 0,
                "tracks_per_file_max": max(st["trk"] for st in stats_all)})
    res["trails"] = 0
    if any(m["trails"] for m in ms):
        ttext, tst = gpx_doc(ms, dict(opts, max_points=MAX_PTS, title=f"KPC {area} trails {opts['date']}"), what="trails")
        tz = zip_bytes([(f"KPC_{area}_trails_{opts['date']}.gpx", ttext)])
        with open(os.path.join(gps, f"{area}-trails.gpx.zip"), "wb") as fh:
            fh.write(tz)
        res["files"].append({"file": f"data/gps/{area}-trails.gpx.zip", "bytes": len(tz)})
        res["trails"] = tst["trk"]
        if len(tz) > max_bytes:
            report["problems"].append(f"{area}: trails pack is over {a.max_mb} MB")
        if tst["trk"] > a.max_tracks:
            report["problems"].append(f"{area}: trails pack holds {tst['trk']} tracks (> {a.max_tracks}); older Garmins may not load them all")
    srcs = ", ".join(sorted("/".join(x.replace("\\", "/").split("/")[-3:]) for x in set(I["files"].get(area, ())) | I["shared"]))
    for f in res["files"]:
        f.update({"source_url": srcs, "read_date": opts["read_date"], "why": "GPS pack built from the club's parkinfo, key, access, outline and trail files listed in source_url"})
    return res


# ---------------------------------------------------------------- main
def parse(argv):
    ap = argparse.ArgumentParser(description="Build KPC state GPS packs (GPX/KML zips) into --out.")
    ap.add_argument("--parkinfo", nargs="*", default=[], help="data/parkinfo/US-XX.json (area = file name), CA.json, or data/pota/t/*.json")
    ap.add_argument("--access", nargs="*", default=[], help="data/access/<area>.json or kpc-ky-data.json ('ap')")
    ap.add_argument("--keys", nargs="*", default=[], help="data/us-key/US-XX.json (official / approximate / pin)")
    ap.add_argument("--outlines", nargs="*", default=[], help="GeoJSON outline files or folders (properties.ref; agency, why optional)")
    ap.add_argument("--trails", nargs="*", default=[], help="GeoJSON trail lines (properties.ref, name, agency)")
    ap.add_argument("--fers", nargs="*", default=[], help="data/fers/US-XX.json (used only with --include-fers)")
    ap.add_argument("--include-fers", action="store_true", help="add the 2-fer spots (default OFF); adds the 2-fer notice")
    ap.add_argument("--in", dest="inp", help="(contract option) JSON file {parkinfo:[..], access:[..], keys:[..], outlines:[..], trails:[..], fers:[..]}")
    ap.add_argument("--out", help="output folder (the only place it writes)")
    ap.add_argument("--areas", default="", help="e.g. US-KY,US-TN (default: every area in --parkinfo)")
    ap.add_argument("--max-minutes", type=float, default=50.0)
    ap.add_argument("--resume", action="store_true", help="skip areas <out>/state.json says are done")
    ap.add_argument("--changed-only", action="store_true", help="with --resume: rebuild a done area only if its inputs changed (nightly job)")
    ap.add_argument("--limit", type=int, default=0, help="only the first N parks of each area (tests)")
    ap.add_argument("--cache", help="(contract option; this tool reads local files only, so it is not used)")
    ap.add_argument("--site-url", default=os.environ.get("KPC_SITE_URL", ""), help=f"site link written into every file (or env KPC_SITE_URL; default {SITE_URL})")
    ap.add_argument("--built", default="", help="date the data was built, YYYY-MM-DD (default today)")
    ap.add_argument("--max-mb", type=float, default=5.0, help="size target per zipped pack")
    ap.add_argument("--max-tracks", type=int, default=200, help="most outline tracks in one GPX file (Garmin units hold about 200)")
    ap.add_argument("--pulloffs", action="store_true", help="include club-graded YES pull-off candidates (later, after chat 11)")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.inp:
        with open(a.inp, encoding="utf-8") as fh:
            spec = json.load(fh)
        for k in ("parkinfo", "access", "keys", "outlines", "trails", "fers"):
            if not getattr(a, k) and spec.get(k):
                setattr(a, k, spec[k] if isinstance(spec[k], list) else [spec[k]])
    return a


def run(argv):
    a = parse(argv)
    if a.selftest:
        return selftest()
    if not a.out:
        print("--out is required", file=sys.stderr)
        return 2
    t0 = time.time()
    deadline = t0 + a.max_minutes * 60
    os.makedirs(os.path.join(a.out, "work"), exist_ok=True)
    report = {"problems": [], "areas": []}
    today = dt.date.today().isoformat()
    built = a.built or today
    site = a.site_url or SITE_URL
    opts = {"built": built, "site": site, "date": today, "read_date": today, "fers": a.include_fers, "pulloffs": a.pulloffs,
            "time": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
    I = load_inputs(a, report["problems"])
    areas = [x.strip() for x in a.areas.split(",") if x.strip()] or sorted(I["parks"])
    state_p = os.path.join(a.out, "state.json")
    index_p = os.path.join(a.out, "data", "gps", "index.json")
    state, index = {"done": {}}, {"packs": {}}
    if a.resume:
        for path, name in ((state_p, "state"), (index_p, "index")):
            if os.path.exists(path):
                try:
                    with open(path, encoding="utf-8") as fh:
                        (state if name == "state" else index).update(json.load(fh))
                except Exception as e:  # noqa: BLE001
                    report["problems"].append(f"{os.path.basename(path)} not read ({e}); starting over")
    left = []
    for area in areas:
        hsh = inputs_hash(area, I)
        done = state["done"].get(area)
        if a.resume and done and (not a.changed_only or done.get("inputs") == hsh):
            report["areas"].append({"area": area, "skipped": "done in an earlier run" + (" and inputs unchanged" if a.changed_only else "")})
            continue
        if area not in I["parks"]:
            report["problems"].append(f"{area}: no parkinfo file for this area")
            continue
        if time.time() > deadline:
            left.append(area)
            continue
        res = build_area(area, I, a, opts, deadline, report)
        if res is None:
            left.append(area)
            continue
        report["areas"].append(res)
        index["packs"][area] = res
        state["done"][area] = {"inputs": hsh, "date": today, "parks": res["parks"]}
        with open(state_p, "w", encoding="utf-8") as fh:
            json.dump(state, fh, indent=1)
    index.update({"notice": NOTICE, "built": built, "site": site, "generated": opts["time"], "tool": f"kpc_gpspacks {VERSION}",
                  "hold": "The GPS downloads page stays members-only and out of the menu until Brandon's GO."})
    os.makedirs(os.path.dirname(index_p), exist_ok=True)
    with open(index_p, "w", encoding="utf-8") as fh:
        json.dump(index, fh, indent=1, ensure_ascii=False)
    with open(state_p, "w", encoding="utf-8") as fh:
        json.dump(state, fh, indent=1)
    write_report(a, report, left, time.time() - t0)
    return 3 if left else 0


def write_report(a, report, left, secs):
    L = [f"# kpc_gpspacks run report ({dt.date.today().isoformat()})", "", NOTICE, "",
         f"Run time {secs:.1f} s. Areas left for the next run: {', '.join(left) or 'none'}.", "", "## Areas", ""]
    for r in report["areas"]:
        if "skipped" in r:
            L.append(f"- {r['area']}: skipped ({r['skipped']})")
            continue
        files = ", ".join(f"`{f['file']}` {f['bytes'] / 1024:.0f} KB" for f in r["files"])
        L.append(f"- {r['area']}: {r['parks']} parks ({r.get('official', 0)} official outline, {r.get('approximate', 0)} approximate, "
                 f"{r.get('pin_only', 0)} pin only), {r.get('access_points', 0)} access points, {r.get('trails', 0)} trail lines, "
                 f"{r.get('fers', 0)} 2-fer spots; largest outline {r.get('outline_points_max', 0)} points; {r.get('gpx_parts', 1)} GPX file(s); {files}")
    L += ["", "## Problems (each item left out or changed, with the reason)", ""] + [f"- {p}" for p in report["problems"] or ["none"]]
    with open(os.path.join(a.out, "report.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")


# ---------------------------------------------------------------- selftest (offline)
def summary(gpx, kml, tgpx):
    """Day-independent summary of the sample run, compared with tests/expected_output.json."""
    w = re.findall(r"<wpt [^>]*><name>([^<]*)</name><desc>([^<]*)</desc>(?:<src>[^<]*</src>)?(?:<sym>([^<]*)</sym>)?", gpx)
    t = re.findall(r"<trk><name>([^<]*)</name><desc>([^<]*)</desc>", gpx)
    return {"wpt": [[n, d, s] for n, d, s in w], "trk": [[n, d] for n, d in t],
            "kml_placemarks": kml.count("<Placemark>"), "trails": re.findall(r"<trk><name>([^<]*)</name>", tgpx)}


def _zip_texts(zpath):
    with zipfile.ZipFile(zpath) as z:
        return {n: z.read(n).decode("utf-8") for n in z.namelist()}


def _big_fixture(folder):
    parks, feats = {}, []
    for i in range(260):
        lat, lon = 36.6 + (i // 20) * 0.12, -89.0 + (i % 20) * 0.35
        ref = f"US-{5000 + i}"
        parks[ref] = [f"Synthetic Park {i}", "", "SP", "", "", lat, lon]
        ring = []
        for j in range(400):
            t = j / 400 * 2 * math.pi
            r = 0.03 * (1 + 0.2 * math.sin(7 * t))
            ring.append([round(lon + r * math.cos(t), 7), round(lat + r * math.sin(t), 7)])
        ring.append(ring[0])
        feats.append({"type": "Feature", "properties": {"ref": ref, "agency": "Synthetic Agency", "status": "official"},
                      "geometry": {"type": "Polygon", "coordinates": [ring]}})
    os.makedirs(os.path.join(folder, "parkinfo"))
    with open(os.path.join(folder, "parkinfo", "US-ZZ.json"), "w") as fh:
        json.dump({"parks": parks}, fh)
    with open(os.path.join(folder, "outlines.geojson"), "w") as fh:
        json.dump({"type": "FeatureCollection", "features": feats}, fh)


def selftest():
    tdir = os.path.join(HERE, "tests")
    checks = []

    def ok(cond, what):
        checks.append((bool(cond), what))

    try:
        from lxml import etree
        gpx_schema = etree.XMLSchema(etree.parse(os.path.join(tdir, "gpx.xsd")))
        kml_schema = etree.XMLSchema(etree.parse(os.path.join(tdir, "kml22", "ogckml22.xsd")))
    except Exception as e:  # noqa: BLE001
        print(f"FAIL: lxml or the bundled schemas are not available ({e}); pip install -r requirements.txt")
        return 1

    def valid(text, schema):
        try:
            doc = etree.fromstring(text.encode("utf-8"))
        except etree.XMLSyntaxError as e:
            return f"not well formed: {e}"
        return None if schema.validate(doc) else str(schema.error_log.last_error)

    ns = {"g": "http://www.topografix.com/GPX/1/1"}
    kns = {"k": "http://www.opengis.net/kml/2.2"}
    D = os.path.join(tdir, "data")
    base = ["--parkinfo", os.path.join(D, "parkinfo"), "--access", os.path.join(D, "access"), "--keys", os.path.join(D, "us-key"),
            "--outlines", os.path.join(tdir, "outlines.geojson"), "--trails", os.path.join(tdir, "trails.geojson"),
            "--fers", os.path.join(D, "fers"), "--built", "2026-10-31"]
    day = dt.date.today().isoformat()
    work = tempfile.mkdtemp(prefix="kpc_gpspacks_test_")
    try:
        # 1. full run, 2-fers off
        out = os.path.join(work, "out")
        before = sorted(os.walk(tdir))
        rc = run(base + ["--out", out])
        ok(rc == 0, f"full run exits 0 (got {rc})")
        gdir = os.path.join(out, "data", "gps")
        names = sorted(os.listdir(gdir))
        ok(names == ["US-KY-trails.gpx.zip", "US-KY.gpx.zip", "US-KY.kml.zip", "US-TN.gpx.zip", "US-TN.kml.zip", "index.json"], f"packs written: {names}")
        ok(sorted(os.walk(tdir)) == before, "nothing written outside --out")
        g = _zip_texts(os.path.join(gdir, "US-KY.gpx.zip"))
        ok(list(g) == [f"KPC_US-KY_parks_{day}.gpx"], f"file name KPC_<state>_parks_<date>.gpx: {list(g)}")
        gpx = next(iter(g.values()))
        kml = next(iter(_zip_texts(os.path.join(gdir, "US-KY.kml.zip")).values()))
        tgpx = next(iter(_zip_texts(os.path.join(gdir, "US-KY-trails.gpx.zip")).values()))
        tn = next(iter(_zip_texts(os.path.join(gdir, "US-TN.gpx.zip")).values()))
        tnk = next(iter(_zip_texts(os.path.join(gdir, "US-TN.kml.zip")).values()))
        for nm, txt, sch, sn in (("US-KY parks GPX", gpx, gpx_schema, "GPX 1.1"), ("US-KY trails GPX", tgpx, gpx_schema, "GPX 1.1"),
                                 ("US-TN GPX", tn, gpx_schema, "GPX 1.1"), ("US-KY KML", kml, kml_schema, "OGC KML 2.2"), ("US-TN KML", tnk, kml_schema, "OGC KML 2.2")):
            err = valid(txt, sch)
            ok(err is None, f"{nm} passes the {sn} XSD {err or ''}")
        doc = etree.fromstring(gpx.encode())
        meta = doc.find("g:metadata/g:desc", ns).text
        ok(meta.startswith(NOTICE) and "Data built: 2026-10-31" in meta and "Site: https://kentuckyportableclub.github.io/KPC-Links/" in meta,
           "GPX description: notice first, then build date and the default site link (KPC-Links page, ruled Oct 31 2026)")
        ok(FER_NOTICE not in gpx and FER_NOTICE not in kml and "2-fer" not in gpx, "no 2-fers and no 2-fer notice without --include-fers")
        wpts = doc.findall("g:wpt", ns)
        wn = [w.find("g:name", ns).text for w in wpts]
        wd = [w.find("g:desc", ns).text for w in wpts]
        ws = [(w.find("g:sym", ns).text if w.find("g:sym", ns) is not None else None) for w in wpts]
        ok(all(len(n) <= 30 for n in wn), "every wpt name <= 30 characters")
        ok(len(set(wn)) == len(wn), "wpt names unique")
        ok(any(d.startswith("US-9001 Sample Lake Wildlife Management Area. " + PIN_LABEL) for d in wd), "pin: '<ref> <park name>' + POTA pin text")
        ok(ws.count("Flag, Green") == 3, f"3 park pins with 'Flag, Green' (broken row left out): {ws.count('Flag, Green')}")
        ok(sum(1 for d in wd if d.startswith("Parking (from KDFWR)")) == 2, "'Parking (from <agency>)'")
        ok(any(s == "Parking Area" and d.startswith("Parking (from an official access list; check the agency\u2019s map before you go).") for d, s in zip(wd, ws)),
           "no agency named: exact ruled parking label, curly apostrophe")
        ok("Parking (from an official access list; check the agency\u2019s map before you go)" in kml, "ruled parking label also in the KML")
        ok(any(d.startswith("Boat ramp.") for d, s in zip(wd, ws) if s == "Boat Ramp"), "Boat ramp + 'Boat Ramp' symbol")
        ok(any(d.startswith("Entrance.") for d, s in zip(wd, ws) if s == "Information"), "Entrance + 'Information' symbol")
        ok(any(d.startswith("Trailhead.") for d, s in zip(wd, ws) if s == "Trail Head"), "Trailhead + 'Trail Head' symbol")
        ok(sum(1 for d in wd if d.startswith(NEARBY_LABEL)) == 1, "outside point labelled 'Nearby public access, not the park's own'")
        ok(not any("pull-off" in d.lower() for d in wd), "ungraded pull-off candidate left out")
        ok(any(d.startswith("US-9003 Sample Ridge Preserve.") and NO_OUTLINE in d for d in wd), "pin-only park says 'No official outline yet'")
        trks = doc.findall("g:trk", ns)
        tnames = [x.find("g:name", ns).text for x in trks]
        ok(tnames == ["US-9001 boundary (Official)", "US-9002 boundary (Approximate)"], f"outline tracks '<ref> boundary (...)', none for pin-only: {tnames}")
        for x in trks:
            nm = x.find("g:name", ns).text
            pts = [[(p.get("lat"), p.get("lon")) for p in s.findall("g:trkpt", ns)] for s in x.findall("g:trkseg", ns)]
            ok(all(len(s) >= 4 and s[0] == s[-1] for s in pts), f"{nm}: every trkseg closed")
            ok(sum(len(s) for s in pts) <= 2000, f"{nm}: <= 2000 points ({sum(len(s) for s in pts)})")
            ok(re.search(r"Simplified to ~\d+ m for GPS units", x.find("g:desc", ns).text), f"{nm}: detail stated in desc")
        ok(trks[0].find("g:desc", ns).text.startswith("Official boundary (Kentucky Dept. of Fish & Wildlife Resources)"), "'Official boundary (<agency>)'")
        ok(trks[1].find("g:desc", ns).text.startswith("Approximate outline (traced from the agency's picture map)"), "'Approximate outline (<why>)'")
        ok(len(trks[0].findall("g:trkseg", ns)) == 3, "one trkseg per ring (outer + hole + second piece)")
        kd = etree.fromstring(kml.encode())
        ok(kd.find("k:Document/k:description", kns).text.startswith(NOTICE), "KML document description starts with the notice")
        folders = [f.find("k:name", kns).text for f in kd.findall("k:Document/k:Folder", kns)]
        ok(folders == ["Park pins", "Parking", "Trails", "Outline"], f"KML folders, no 2-fers folder without the option: {folders}")
        ok("<styleUrl>#official</styleUrl><MultiGeometry><Polygon>" in kml and '<Style id="official"><LineStyle><color>ff00ffff' in kml, "KML official outline: Polygon, yellow line")
        ok("<styleUrl>#dash</styleUrl>" in kml and kml.count("<LineString>") > 50, "KML approximate outline drawn dashed")
        ok(NO_OUTLINE in kml and kml.count("<Polygon>") == 3, "KML pin-only: no polygon, label present")
        td = etree.fromstring(tgpx.encode())
        tt = td.findall("g:trk", ns)
        ok(len(tt) == 1 and tt[0].find("g:desc", ns).text.startswith("Sample Lake Loop Trail (official line, Kentucky Dept. of Fish & Wildlife Resources)"),
           "trail label '<trail name> (official line, <agency>)'")
        ok(td.find("g:metadata/g:desc", ns).text.startswith(NOTICE), "trails pack starts with the notice")
        ok(not td.findall("g:wpt", ns) and "boundary" not in tgpx, "trails pack holds only trail lines")
        for nm, txt in (("parks GPX", gpx), ("KML", kml), ("trails GPX", tgpx)):
            ok(not BANNED.search(txt), f"no OSM / Google / banned-source text in the {nm}")
        sizes = {f: os.path.getsize(os.path.join(gdir, f)) for f in names if f.endswith(".zip")}
        ok(all(s <= 5 * 1024 * 1024 for s in sizes.values()), f"every pack <= 5 MB zipped: {sizes}")
        with open(os.path.join(out, "report.md"), encoding="utf-8") as fh:
            rep = fh.read()
        ok("US-9004: left out (no usable lat/lon" in rep, "broken park row reported with a reason; run not stopped")
        with open(os.path.join(gdir, "index.json"), encoding="utf-8") as fh:
            idx = json.load(fh)
        ok(idx["notice"] == NOTICE and "Brandon's GO" in idx["hold"], "index.json carries the notice and the HOLD note")
        ok(all(f.get("source_url") and f.get("read_date") and f.get("why") for p in idx["packs"].values() for f in p["files"]), "every pack row has source_url, read_date, why")
        # 2. 2-fers on
        out2 = os.path.join(work, "out2")
        rc = run(base + ["--out", out2, "--areas", "US-KY", "--include-fers"])
        g2 = next(iter(_zip_texts(os.path.join(out2, "data", "gps", "US-KY.gpx.zip")).values()))
        k2 = next(iter(_zip_texts(os.path.join(out2, "data", "gps", "US-KY.kml.zip")).values()))
        d2 = etree.fromstring(g2.encode())
        ok(rc == 0 and d2.find("g:metadata/g:desc", ns).text.endswith(FER_NOTICE), "--include-fers: 2-fer notice in the description, word for word")
        fw = [w for w in d2.findall("g:wpt", ns) if w.find("g:name", ns).text.startswith("2-fer")]
        ok(len(fw) == 1 and fw[0].find("g:desc", ns).text.startswith(FER_NOTICE), f"--include-fers: the shared 2-fer spot appears once, with the notice ({len(fw)})")
        ok("<Folder><name>2-fers</name><description>" + xesc(FER_NOTICE) in k2, "--include-fers: KML 2-fers folder with the notice")
        ok(valid(g2, gpx_schema) is None and valid(k2, kml_schema) is None, "--include-fers files pass their XSDs")
        ok(sorted(os.listdir(os.path.join(out2, "data", "gps"))) == ["US-KY-trails.gpx.zip", "US-KY.gpx.zip", "US-KY.kml.zip", "index.json"], "--areas US-KY builds only Kentucky")
        # 3. time limit, resume, changed-only, limit
        out3 = os.path.join(work, "out3")
        rc = run(base + ["--out", out3, "--max-minutes", "0"])
        ok(rc == 3, f"--max-minutes 0: exit 3 with work left (got {rc})")
        rc = run(base + ["--out", out3, "--resume"])
        ok(rc == 0 and os.path.exists(os.path.join(out3, "data", "gps", "US-TN.gpx.zip")), "--resume finishes the work, exit 0")
        rc = run(base + ["--out", out3, "--resume", "--changed-only"])
        with open(os.path.join(out3, "report.md"), encoding="utf-8") as fh:
            rep3 = fh.read()
        ok(rc == 0 and rep3.count("skipped (done in an earlier run and inputs unchanged)") == 2, "--resume --changed-only skips unchanged areas")
        ocopy = os.path.join(work, "outlines_copy.geojson")
        shutil.copy(os.path.join(tdir, "outlines.geojson"), ocopy)
        b2 = [ocopy if x == os.path.join(tdir, "outlines.geojson") else x for x in base]
        run(b2 + ["--out", os.path.join(work, "out6")])
        with open(ocopy, encoding="utf-8") as fh:
            od = json.load(fh)
        od["features"][0]["properties"]["agency"] = "Changed Agency"
        with open(ocopy, "w", encoding="utf-8") as fh:
            json.dump(od, fh)
        rc = run(b2 + ["--out", os.path.join(work, "out6"), "--resume", "--changed-only"])
        with open(os.path.join(work, "out6", "report.md"), encoding="utf-8") as fh:
            rep6 = fh.read()
        ok(rc == 0 and "skipped (done" not in rep6, "--changed-only rebuilds when an outline file changes")
        out4 = os.path.join(work, "out4")
        rc = run(base + ["--out", out4, "--areas", "US-KY", "--limit", "1"])
        g4 = next(iter(_zip_texts(os.path.join(out4, "data", "gps", "US-KY.gpx.zip")).values()))
        ok(rc == 0 and g4.count("<sym>Flag, Green</sym>") == 1, "--limit 1 writes one park")
        # 4. synthetic state with 260 outlines: <= 200 tracks a file, size target
        big = os.path.join(work, "big")
        _big_fixture(big)
        out5 = os.path.join(work, "out5")
        rc = run(["--parkinfo", os.path.join(big, "parkinfo"), "--outlines", os.path.join(big, "outlines.geojson"), "--out", out5, "--site-url", "https://example.org/kpc/"])
        z5 = _zip_texts(os.path.join(out5, "data", "gps", "US-ZZ.gpx.zip"))
        ok(rc == 0 and sorted(z5) == [f"KPC_US-ZZ_parks_{day}_part1of2.gpx", f"KPC_US-ZZ_parks_{day}_part2of2.gpx"], f"260 outlines split into 2 GPX files: {sorted(z5)}")
        ok(all(v.count("<trk>") <= 200 for v in z5.values()) and sum(v.count("<trk>") for v in z5.values()) == 260
           and sum(v.count("Flag, Green") for v in z5.values()) == 260, "every park once, <= 200 tracks per file")
        ok(all(valid(v, gpx_schema) is None for v in z5.values()), "split GPX files pass the XSD")
        ok(all("Site: https://example.org/kpc/" in v for v in z5.values()), "--site-url still overrides the default site link")
        ok(os.path.getsize(os.path.join(out5, "data", "gps", "US-ZZ.gpx.zip")) <= 5 * 1024 * 1024, "260-park pack <= 5 MB zipped")
        # 4b. ruling Oct 31 2026 9:41 PM CT: parking uses the access data's own agency only, never the outline's
        ag = os.path.join(work, "agency")
        os.makedirs(os.path.join(ag, "parkinfo")); os.makedirs(os.path.join(ag, "access")); os.makedirs(os.path.join(ag, "access2"))
        with open(os.path.join(ag, "parkinfo", "US-YY.json"), "w") as fh:
            json.dump({"parks": {"US-9050": ["Outline Agency Test Park", "", "SP", "", "", 37.005, -83.995],
                                 "US-9051": ["File Agency Test Park", "", "SP", "", "", 37.105, -83.995]}}, fh)
        with open(os.path.join(ag, "access", "US-YY.json"), "w") as fh:
            json.dump({"parks": {"US-9050": [[37.004, -83.996, "Test: Parking"]]}}, fh)
        with open(os.path.join(ag, "access2", "US-YY.json"), "w") as fh:
            json.dump({"agency": "Access File Agency", "parks": {"US-9051": [[37.104, -83.996, "Test: Parking"], [37.106, -83.996, "Test: Parking", {"agency": "Row Agency"}]]}}, fh)
        rg = [[-84.0, 37.0], [-83.99, 37.0], [-83.99, 37.01], [-84.0, 37.01], [-84.0, 37.0]]
        with open(os.path.join(ag, "outlines.geojson"), "w") as fh:
            json.dump({"type": "FeatureCollection", "features": [
                {"type": "Feature", "properties": {"ref": "US-9050", "agency": "Outline Only Agency", "status": "official"}, "geometry": {"type": "Polygon", "coordinates": [rg]}},
                {"type": "Feature", "properties": {"ref": "US-9051", "agency": "Outline Only Agency", "status": "official"},
                 "geometry": {"type": "Polygon", "coordinates": [[[x, y + 0.1] for x, y in rg]]}}]}, fh)
        out7 = os.path.join(work, "out7")
        rc = run(["--parkinfo", os.path.join(ag, "parkinfo"), "--access", os.path.join(ag, "access"), os.path.join(ag, "access2"),
                  "--outlines", os.path.join(ag, "outlines.geojson"), "--out", out7])
        g7 = next(iter(_zip_texts(os.path.join(out7, "data", "gps", "US-YY.gpx.zip")).values()))
        k7 = next(iter(_zip_texts(os.path.join(out7, "data", "gps", "US-YY.kml.zip")).values()))
        d7 = etree.fromstring(g7.encode())
        p7 = {w.find("g:name", ns).text: w.find("g:desc", ns).text for w in d7.findall("g:wpt", ns) if (w.find("g:sym", ns) is not None and w.find("g:sym", ns).text == "Parking Area")}
        ok(rc == 0 and p7.get("US-9050 Parking", "").startswith(PARKING_NO_AGENCY + ".") and "Parking (from Outline Only Agency" not in g7 + k7,
           f"outline has an agency, access data none: new wording, outline agency NOT used (GPX+KML) {p7}")
        ok("Official boundary (Outline Only Agency)" in g7, "outline agency still labels the outline itself")
        ok(sorted(v.split(".")[0] for k, v in p7.items() if k.startswith("US-9051")) == ["Parking (from Access File Agency)", "Parking (from Row Agency)"],
           "access file's agency used when the row names none; the row's agency wins")
        ok(valid(g7, gpx_schema) is None and valid(k7, kml_schema) is None, "agency-test pack passes the XSDs")
        # 5. simplifier
        tri = [[[[-84, 37], [-84.001, 37], [-84, 37.001], [-84, 37]]]]
        ok(len(simplify_outline(tri)[0][0][0]) == 4, "tiny triangle kept")
        many = [[[[-84 + i * 0.01, 37], [-84 + i * 0.01 + 0.001, 37], [-84 + i * 0.01, 37.001], [-84 + i * 0.01, 37]]] for i in range(1500)]
        sp = simplify_outline(many)
        ok(sp[3] <= 2000 and sp[2] > 0, f"1500 small pieces: <= 2000 points, smallest left out ({sp[3]} points, {sp[2]} dropped)")
        # Nov 7 (tracts): with tract ids every tract keeps a ring; without them, the same answer as before
        tr = [[[[-84 + i * 0.1, 37], [-84 + i * 0.1 + 0.0001, 37], [-84 + i * 0.1, 37.0001], [-84 + i * 0.1, 37]]] for i in range(4)]
        big = [[[-85 + 0.05 * math.cos(i / 400 * 6.283), 37 + 0.05 * math.sin(i / 400 * 6.283)] for i in range(400)] + [[-84.95, 37.0]]]
        off, on = simplify_outline([big] + tr, 12), simplify_outline([big] + tr, 12, ["a", "b", "c", "d", "e"])
        ok(len(off[0]) < 5 and len(on[0]) == 5 and simplify_outline(many) == simplify_outline(many, MAX_PTS, None),
           f"tract ids: every tract keeps a ring ({len(on[0])} of 5; {len(off[0])} without ids, as before)")
        fc = {"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {"tract": "US-1#1"}, "geometry": {"type": "Polygon", "coordinates": big}},
                                                         {"type": "Feature", "properties": {"tract": "US-1#2"}, "geometry": {"type": "MultiPolygon", "coordinates": tr[:2]}}]}
        bare = {"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {}, "geometry": fc["features"][0]["geometry"]}]}
        ok(poly_tracts(fc, 3) == ["US-1#1", "US-1#2", "US-1#2"] and poly_tracts(bare, 1) is None,
           "poly_tracts: one id per polygon, None without tract labels")
        # 6. expected output
        with open(os.path.join(tdir, "expected_output.json"), encoding="utf-8") as fh:
            exp = json.load(fh)
        got = summary(gpx, kml, tgpx)
        if os.environ.get("KPC_WRITE_EXPECTED"):
            with open(os.path.join(tdir, "expected_output.json"), "w", encoding="utf-8") as fh:
                json.dump(got, fh, indent=1, ensure_ascii=False)
            exp = got
        ok(got == exp, "matches tests/expected_output.json" + ("" if got == exp else f": {json.dumps(got)[:300]}"))
    finally:
        shutil.rmtree(work, ignore_errors=True)
    bad = [w for c, w in checks if not c]
    for c, w in checks:
        print(("  ok    " if c else "  FAIL  ") + w)
    print(f"{'FAIL' if bad else 'PASS'}: {len(checks) - len(bad)} of {len(checks)} checks passed")
    return 1 if bad else 0


if __name__ == "__main__":
    try:
        sys.exit(run(sys.argv[1:]))
    except KeyboardInterrupt:
        sys.exit(130)
