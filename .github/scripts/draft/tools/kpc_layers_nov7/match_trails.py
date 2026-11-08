#!/usr/bin/env python3
"""Match POTA trail parks (no outline yet) to the approved trail/byway LINE layers.

Two modes
  --plan   no network. Writes match_plan.csv: every (park, candidate layer) pair the rules select.
  (default) queries each candidate layer and writes
            matches.csv        one row per (park, layer): matched feature names, name score, spatial hit, confidence
            best_per_park.csv  best candidate per park ref (or "none")
            matches_report.txt counts and failures

How a pair is scored (all of it is a *candidate* for review, not a verified match)
  name score  : best difflib ratio between the park's distinctive name and any returned feature name
  spatial hit : (US rows with lat/lon only) a line feature of the layer lies within 2 km of the POTA point
  high        : name score >= 0.85 and spatial hit
  medium      : name score >= 0.70, or spatial hit with name score >= 0.50
  low         : one weak signal only
  Canada rows have no lat/lon in the file, so they can only score on name.

Rules kept from the README: no services.arcgis.com/33TOOklri9xpic7U, no ncnhde.natureserve.org,
robots.txt + crawl delay honoured (convert_layers.polite_get), no bypasses. Writes files only.

Usage: python match_trails.py --parks parks.csv --layers kpc-trail-line-layers-nov7.csv --out matches --plan
       python match_trails.py --parks parks.csv --layers kpc-trail-line-layers-nov7.csv --out matches
       python match_trails.py ... --only US-UT          (state/province prefix filter)
Env  : GITHUB_TOKEN (optional; only for the one raw.githubusercontent.com layer)
"""
import argparse, csv, difflib, gzip, io, json, math, os, re, sys, unicodedata
from urllib.parse import urlencode

from convert_layers import polite_get, BLOCKED

STOP = set("""national scenic historic trail trails wild river rivers state blm recreation management area special
site sites byway byways backcountry back country road parkway heritage canadian geologic natural beauty outstanding
interpretive trailhead trailheads system park the and of for with to in at on a an bike mountain loop access
station railway""".split())

# ---------------------------------------------------------------- layer classes (by URL, not by the area column,
# because some layers are national even though the CSV tags them with one state)
def layer_class(url, title):
    u = url.lower()
    if "edw_trailnfs" in u:                       return "NFS"
    if "edw_wildscenicriversegments" in u:        return "WSR_USFS"
    if "nps_public_trails" in u:                  return "NPS_TRAILS"
    if "usgs_trails" in u:                        return "USGS"
    if "kbxwqrrfwyeylgp4" in u:                   return "NSHT"          # National Scenic & Historic Trails (BLM org)
    if "national_historic_trails" in u:           return "NHT"
    if "fbc8ejbxqrmchlei" in u:                   return "NPS_NATL_TRAIL"  # SSB NHT, NEEN NST, SAFE NHT, NPS boundary
    if "anst_centerline" in u:                    return "NPS_NATL_TRAIL"
    if "gis.blm.gov/natl" in u:                   return "BLM_TRAILS"
    if "geo.dot.gov" in u:                        return "DOT_BYWAY"
    if "scenic" in u and "byway" in u or "scenicbackways" in u or "scenic_byways" in u or "byways" in u:
        return "STATE_BYWAY"
    if "commemorative" in u or "designated_routes" in u or "byway" in title.lower(): return "STATE_BYWAY"
    return "STATE_TRAIL"                          # state / local trail layers apply to their own state


NATIONAL_CLASSES = {"NFS", "WSR_USFS", "NPS_TRAILS", "USGS", "NSHT", "NHT", "NPS_NATL_TRAIL", "BLM_TRAILS"}


def pick_layers(park, layers):
    """Return [(layer_index, reason)] for one park row."""
    ty, st = park["type"], park["state"]
    out = []
    byway = any(k in ty for k in ("Parkway", "Scenic Site", "Outstanding Natural Beauty")) or "byway" in park["name"].lower()
    nat_trail = any(k in ty for k in ("National Historic Trail", "National Scenic Trail", "National Geologic Trail", "BLM Historic Trail"))
    wsr = "Wild" in ty and "Scenic" in ty and "River" in ty
    blm = ty.startswith("BLM")
    for i, L in enumerate(layers):
        c = layer_class(L["url"], L["title"])
        same_state = L["area"] == st
        if L["area"].startswith("W-"):
            continue                                              # other-country layers
        if st.startswith("CA-") != L["area"].startswith("CA-"):
            continue                                              # keep US and Canada apart
        why = None
        if c == "WSR_USFS":
            why = "wild & scenic river type" if wsr else None
        elif c == "NSHT" or c == "NHT" or c == "NPS_NATL_TRAIL":
            why = "national trail type" if nat_trail else None
        elif c == "BLM_TRAILS":
            why = "BLM site: BLM national trails layer" if blm or nat_trail else None
        elif c in ("NFS", "NPS_TRAILS", "USGS"):
            why = "national trail dataset" if not wsr else None
            if byway or ty in ("Historic Site", "State Historic Site", "National Historic Site"):
                why = None
        elif c == "DOT_BYWAY":
            why = "scenic byway type, state-specific layer" if byway and same_state else None
        elif c == "STATE_BYWAY":
            why = "scenic byway type, state layer" if byway and same_state else None
        else:  # STATE_TRAIL and Canadian layers
            if same_state:
                why = "same state/province trail layer"
        if why:
            out.append((i, why))
    return out


# ---------------------------------------------------------------- names
def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9 ]+", " ", s)


def distinctive(name, ptype):
    n = norm(name)
    t = norm(ptype)
    if n.endswith(t):
        n = n[: -len(t)]
    toks = [w for w in n.split() if len(w) >= 3 and w not in STOP]
    return sorted(set(toks), key=lambda w: -len(w))


def clean_name(name, ptype):
    n = norm(name); t = norm(ptype)
    return (n[: -len(t)] if n.endswith(t) else n).strip()


PATHWORDS = {"trail", "trails", "pathway", "path", "walk", "walkway", "greenway", "loop", "route", "byway", "road"}


def is_wsr(ptype):
    t = norm(ptype)
    return "wild" in t and "scenic" in t and "river" in t


def wsr_ok(park_name, ptype, feat):
    """Nov 7 (Brandon's hand test): a Wild and Scenic River park only matches the river itself:
    the feature must hold '<distinctive words> river' and must not be a trail/pathway named after it
    (Black River -> Black Mountain Pathway, Paint -> Paint Creek Trail, Au Sable -> Hartwick Pines Au Sable River Trail)."""
    toks = [w for w in clean_name(park_name, ptype).split() if w not in ("national", "blm", "wild", "and", "scenic", "river")]
    b = norm(feat).split()
    if not toks or PATHWORDS & set(b):
        return False
    return (" ".join(toks) + " river") in " ".join(b)


def name_score(park_name, ptype, feat_names):
    a = clean_name(park_name, ptype)
    wsr = is_wsr(ptype)
    best, bestn = 0.0, ""
    for f in feat_names:
        b = norm(f).strip()
        if not b:
            continue
        if wsr and not wsr_ok(park_name, ptype, f):
            continue                                              # a trail named after the river is not the river
        r = difflib.SequenceMatcher(None, a, b).ratio()
        ta, tb = set(a.split()) - STOP, set(b.split()) - STOP
        if ta and ta <= tb:                                       # every distinctive park word appears in the feature name
            # one shared word is not enough when it is only the first word of a different named path
            # (e.g. 'Paint' -> 'Paint Creek Trail'); it must not be followed by another place word
            if len(ta) == 1 and b.split()[:1] == list(ta) and len(set(b.split()) - STOP - PATHWORDS - ta) >= 1 \
                    and not set(a.split()) - STOP - ta <= set(b.split()):
                r = max(r, 0.6)
            else:
                r = max(r, 0.9)
        if r > best:
            best, bestn = r, f
    return best, bestn


# ---------------------------------------------------------------- querying
def arcgis_query(layer_url, params):
    q = dict(f="json", returnGeometry="false", resultRecordCount="25", **params)
    r = polite_get(layer_url.rstrip("/") + "/query?" + urlencode(q))
    j = r.json()
    if "error" in j:
        raise RuntimeError(str(j["error"].get("message", j["error"]))[:150])
    return [f["attributes"] for f in j.get("features", [])]


def find_field(attrs, field):
    for k in attrs:
        if k.lower() == field.lower():
            return k
    return None


def query_layer(L, park):
    """Return (feature_names, name_hit_names, spatial_names)."""
    field = L["name_field"]
    toks = distinctive(park["name"], park["type"])
    name_names, sp_names = [], []
    if toks:
        for combo in (toks[:2], toks[:1]):
            where = " AND ".join(f"UPPER({field}) LIKE '%{t.upper()}%'" for t in combo)
            rows = arcgis_query(L["url"], {"where": where, "outFields": field})
            if rows:
                k = find_field(rows[0], field)
                name_names = sorted({str(r.get(k)) for r in rows if r.get(k)})
                break
    if park.get("lat") and park.get("lon"):
        rows = arcgis_query(L["url"], {"where": "1=1", "outFields": field, "geometry": f"{park['lon']},{park['lat']}",
                                       "geometryType": "esriGeometryPoint", "inSR": "4326",
                                       "spatialRel": "esriSpatialRelIntersects", "distance": "2000", "units": "esriSRUnit_Meter"})
        if rows:
            k = find_field(rows[0], field)
            sp_names = sorted({str(r.get(k)) for r in rows if r.get(k)})
    return name_names, sp_names


def confidence(score, spatial):
    if score >= 0.85 and spatial: return "high"
    if score >= 0.70 or (spatial and score >= 0.50): return "medium"
    return "low"


def read_github_geojson(L, park):
    """The one non-ArcGIS layer (intake geojson.gz): name match + nearest-vertex test, no server query."""
    import requests  # noqa
    gj = json.load(gzip.open(io.BytesIO(polite_get(L["url"]).content)))
    names, near = set(), set()
    for f in gj.get("features", []):
        nm = (f.get("properties") or {}).get(L["name_field"]) or ""
        names.add(nm)
        if park.get("lat") and park.get("lon"):
            g = f.get("geometry") or {}
            coords = g.get("coordinates", [])
            pts = coords if g.get("type") == "LineString" else [p for part in coords for p in part] if g.get("type") == "MultiLineString" else []
            for lon, lat in pts[:: max(1, len(pts) // 200)]:
                if abs(float(park["lat"]) - lat) < 0.02 and abs(float(park["lon"]) - lon) < 0.025:
                    near.add(nm); break
    return sorted(names), sorted(near)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parks", required=True)
    ap.add_argument("--layers", required=True)
    ap.add_argument("--out", default="matches")
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    layers = list(csv.DictReader(open(a.layers, encoding="utf-8")))
    parks = [p for p in csv.DictReader(open(a.parks, encoding="utf-8")) if p["state"].startswith(a.only)]
    os.makedirs(a.out, exist_ok=True)

    pairs = []
    for p in parks:
        for i, why in pick_layers(p, layers):
            pairs.append((p, i, why))

    if a.plan:
        with open(os.path.join(a.out, "match_plan.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["ref", "state", "park", "type", "layer_row", "layer_title", "layer_class", "layer_url", "name_field", "why"])
            for p, i, why in pairs:
                L = layers[i]
                w.writerow([p["ref"], p["state"], p["name"], p["type"], i, L["title"], layer_class(L["url"], L["title"]), L["url"], L["name_field"], why])
            seen = {p["ref"] for p, _, _ in pairs}
            for p in parks:
                if p["ref"] not in seen:
                    w.writerow([p["ref"], p["state"], p["name"], p["type"], "", "", "", "", "", "no approved line layer fits this park type/area"])
        print(len(pairs), "candidate pairs for", len({p['ref'] + p['state'] for p, _, _ in pairs}), "parks")
        return

    cache, rows, fails = {}, [], []
    for p, i, why in pairs:
        L = layers[i]
        key = (p["ref"], i)
        if key in cache:
            res = cache[key]
        else:
            try:
                if "raw.githubusercontent.com" in L["url"]:
                    allnames, near = read_github_geojson(L, p)
                    toks = distinctive(p["name"], p["type"])
                    nn = [n for n in allnames if toks and all(t in norm(n) for t in toks[:1])]
                    res = (nn, near)
                else:
                    res = query_layer(L, p)
            except Exception as e:
                res = None
                fails.append((p["ref"], i, str(e)[:120]))
            cache[key] = res
        if res is None:
            continue
        name_names, sp_names = res
        sc, best = name_score(p["name"], p["type"], name_names + sp_names)
        spatial = bool(sp_names)
        if not name_names and not sp_names:
            continue
        rows.append({"ref": p["ref"], "state": p["state"], "park": p["name"], "layer_row": i, "layer_title": L["title"],
                     "layer_url": L["url"], "best_feature": best, "name_score": round(sc, 2), "spatial_hit": "yes" if spatial else "no",
                     "n_names": len(set(name_names + sp_names)), "feature_names": "; ".join(sorted(set(name_names + sp_names))[:8]),
                     "confidence": confidence(sc, spatial), "why": why})
    order = {"high": 0, "medium": 1, "low": 2}
    rows.sort(key=lambda r: (r["ref"], order[r["confidence"]], -r["name_score"]))
    cols = ["ref", "state", "park", "layer_row", "layer_title", "layer_url", "best_feature", "name_score", "spatial_hit",
            "n_names", "feature_names", "confidence", "why"]
    with open(os.path.join(a.out, "matches.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
    best = {}
    for r in rows:
        best.setdefault((r["ref"], r["state"]), r)
    with open(os.path.join(a.out, "best_per_park.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
        for p in parks:
            r = best.get((p["ref"], p["state"]))
            w.writerow(r or {"ref": p["ref"], "state": p["state"], "park": p["name"], "confidence": "none"})
    with open(os.path.join(a.out, "matches_report.txt"), "w") as f:
        c = {k: sum(1 for r in best.values() if r["confidence"] == k) for k in order}
        f.write(f"parks {len(parks)}; with a candidate {len(best)}; best-candidate confidence {c}\n")
        f.write(f"query failures {len(fails)}\n" + "\n".join(map(str, fails)))
    print("done:", len(best), "of", len(parks), "parks have a candidate;", len(fails), "query failures")


if __name__ == "__main__":
    main()
