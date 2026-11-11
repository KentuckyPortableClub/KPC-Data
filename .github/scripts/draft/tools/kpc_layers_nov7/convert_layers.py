#!/usr/bin/env python3
"""Convert the KPC non-layer park sources into polygon GeoJSON files the key can load.

Input : kpc-non-layer-urls-to-convert-nov7.csv  (area,title,url,name_field,approved_by)
Output: <out>/<slug>.geojson   EPSG:4326, Polygon/MultiPolygon only, property "name" = name_field value
        <out>/<slug>.meta.json source URL, licence, credit, retrieved date, feature count
        <out>/report.csv       one line per row: ok / failed / why
Nothing is pushed anywhere; the workflow uploads <out> as an artifact for review.

Rules enforced here (from the README):
  * never request services.arcgis.com/33TOOklri9xpic7U or ncnhde.natureserve.org
  * robots.txt is read for every host; disallowed URLs are skipped, Crawl-delay is honoured
    (default delay between requests to one host: 2 s)
  * no bypasses: no alternate mirrors, no header spoofing, no retry loops past 3 tries

Needs: pip install geopandas pyogrio shapely pyproj requests
Env  : GITHUB_TOKEN (optional) - sent only to raw.githubusercontent.com for the intake files
Usage: python convert_layers.py --csv kpc-non-layer-urls-to-convert-nov7.csv --out converted
       python convert_layers.py --csv ... --out converted --only 4,5,39     (row numbers, 0-based)
       python convert_layers.py --csv ... --list                            (show the plan, fetch nothing)
"""
import argparse, csv, gzip, io, json, os, re, sys, tempfile, time, zipfile
from datetime import date
from urllib.parse import urlparse, urlencode, parse_qsl, urlunparse
from urllib import robotparser

import requests
import importlib.util as _ilu  # noqa: E402
# Nov 11 2026 (host rules, review package A): the club's ONE pre-request host check (.github/scripts/kpc_host_rules.py), loaded by path
# like tools/kpc_convert_layers does, no fallback. services*.arcgis.com, apps.fs.usda.gov and the never-contact hosts get NO request of
# any kind, robots.txt included: _blocked() below asks it before robots.txt and before every redirect hop; install() also wraps
# requests' adapter, so no other call in this process can reach those hosts either.
_hs = _ilu.spec_from_file_location("kpc_host_rules", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "kpc_host_rules.py"))
HR = _ilu.module_from_spec(_hs); _hs.loader.exec_module(HR); HR.install()

UA = "KPC-Data-layer-converter/1.0 (+https://github.com/KentuckyPortableClub/KPC-Data)"
# Nov 7 review (Grok Bot): the club's never-request list (Grant County NM parcels, NC NHP MAREA) plus the do-not-ingest items
# of .github/scripts/kpc_research_sources.py BANNED (services.arcgis.com itself is handled by its robots.txt 403 below). Matched
# case-insensitively, on the URL asked for AND on the final URL after redirects.
BLOCKED = ("services.arcgis.com/33TOOklri9xpic7U", "ncnhde.natureserve.org", "gisportaldev.dot.ny.gov", "State_Parks_2024",
           "76bc620b19e34d24b2b4936f73b239c7", "aT1T0pU1ZdpuDk1t", "YgrExeJfxG5F4At7", "Coillte_Biodiversity",
           "DEV_-_SCDNR_Public_Lands_Viewer")
HUB_DELAY = 60.0     # club rule: ArcGIS Hub / open-data portals get a 60 s crawl delay
DEFAULT_DELAY = 2.0
PAGE = 1000          # WFS / OGC API page size
MAX_TRIES = 3

# Source CRS when the file does not declare one. Only used if the data are clearly not lon/lat.
CRS_HINT = {"IE": 2157,   # Irish Transverse Mercator
            "RO": 3844,   # Stereo 70
            "DK": 25832, "SE": 3006, "MX": None, "DE": None}

# Per-row licence / credit. believed = from memory of the publisher's terms, NOT yet confirmed
# on the publisher's page. The workflow copies it into meta.json with verified=false.
LICENCE = {}  # filled from licences.csv next to this script if present (row,licence,credit,verified)


# ----------------------------------------------------------------------------- polite HTTP
_robots, _last = {}, {}


def _blocked(url):
    u = (url or "").lower()
    return not HR.host_ok(url)[0] or any(b.lower() in u for b in BLOCKED)   # Nov 11: the host rules first (no robots.txt read either)


def _robots_for(url):
    """Nov 7 review (RFC 9309 as kpc_manners.py reads it, and the club rule 'a services*.arcgis.com robots 403 counts as a
    disallow'): 200 = its rules; 404/410 = no rules (allowed); 401/403/5xx/unreachable = the whole host is refused."""
    p = urlparse(url)
    host = f"{p.scheme}://{p.netloc}"
    if host not in _robots:
        rp = robotparser.RobotFileParser()
        try:
            r = requests.get(host + "/robots.txt", headers={"User-Agent": UA}, timeout=30, allow_redirects=True)
            if r.status_code == 200:
                rp.parse(r.text.splitlines())
            elif r.status_code in (404, 410):
                rp.parse([])                                  # no rules published: allowed
            else:
                rp.parse(["User-agent: *", "Disallow: /"])    # 401 / 403 / 5xx: refused
        except requests.RequestException:
            rp.parse(["User-agent: *", "Disallow: /"])        # unreachable: refused (try again another day)
        _robots[host] = rp
    return _robots[host]


def _host_delay(url, rp):
    h = urlparse(url).netloc.lower()
    d = max(DEFAULT_DELAY, float(rp.crawl_delay(UA) or 0))
    if h.endswith(".hub.arcgis.com") or h.endswith("opendata.arcgis.com") or "/hub" in urlparse(url).path.lower():
        d = max(d, HUB_DELAY)
    return d


def polite_get(url, stream=False, token_host=None, _depth=0):
    if _depth > 5:
        raise RuntimeError("too many redirects")
    if _blocked(url):
        hok, hwhy = HR.host_ok(url)
        raise RuntimeError(f"BLOCKED host, saved copy only, not asked: {hwhy}" if not hok else "URL is on the blocked list")
    rp = _robots_for(url)
    if not rp.can_fetch(UA, url):
        raise RuntimeError("robots.txt disallows this URL (or robots.txt answered 401/403/5xx)")
    host = urlparse(url).netloc
    delay = _host_delay(url, rp)
    headers = {"User-Agent": UA}
    tok = os.environ.get("GITHUB_TOKEN")
    if tok and host == "raw.githubusercontent.com":
        headers["Authorization"] = f"Bearer {tok}"
    last_err = None
    for i in range(MAX_TRIES):
        wait = _last.get(host, 0) + delay - time.time()
        if wait > 0:
            time.sleep(wait)
        try:
            r = requests.get(url, headers=headers, timeout=300, stream=stream, allow_redirects=False)
            _last[host] = time.time()
            if r.status_code in (301, 302, 303, 307, 308) and r.headers.get("Location"):
                # a redirect is a new request: blocked list + robots + delay are checked again for it, and the token is only
                # ever added for raw.githubusercontent.com (never carried to another host)
                nxt = requests.compat.urljoin(url, r.headers["Location"])
                return polite_get(nxt, stream=stream, _depth=_depth + 1)
            if r.status_code == 200:
                return r
            last_err = f"HTTP {r.status_code}"
            if r.status_code in (401, 403, 404, 410):
                break                      # not going to change; do not hammer
        except requests.RequestException as e:
            last_err = str(e)
        time.sleep(delay * (i + 1))
    raise RuntimeError(last_err or "fetch failed")


def with_params(url, **kw):
    p = urlparse(url)
    q = dict(parse_qsl(p.query, keep_blank_values=True))
    low = {k.lower(): k for k in q}
    for k, v in kw.items():
        q[low.get(k.lower(), k)] = v
    return urlunparse(p._replace(query=urlencode(q, safe=":/")))


# ----------------------------------------------------------------------------- fetchers
def fetch_wfs(url):
    """WFS 2.0 GetFeature -> list of GeoJSON features, paged, WGS84."""
    base = with_params(url, outputFormat="application/json", srsName="EPSG:4326")
    feats, start = [], 0
    while True:
        page = with_params(base, count=str(PAGE), startIndex=str(start))
        gj = polite_get(page).json()
        got = gj.get("features", [])
        feats += got
        if len(got) < PAGE:
            return feats
        start += PAGE


def fetch_ogc_api(url):
    """OGC API Features (PDOK, Mercator Vlaanderen) -> features; follows rel=next links."""
    nxt = with_params(url.split("?")[0] + "/items", f="json", limit=str(PAGE))
    feats = []
    while nxt:
        gj = polite_get(nxt).json()
        feats += gj.get("features", [])
        nxt = next((l["href"] for l in gj.get("links", []) if l.get("rel") == "next"), None)
    return feats


def fetch_file(url, workdir):
    r = polite_get(url, stream=True)
    name = re.sub(r"[^A-Za-z0-9._-]", "_", urlparse(url).path.split("/")[-1] or "download")
    path = os.path.join(workdir, name)
    with open(path, "wb") as f:
        for chunk in r.iter_content(1 << 20):
            f.write(chunk)
    # name by content, not by URL (some download links have no extension)
    head = open(path, "rb").read(16)
    ext = (".gz" if head[:2] == b"\x1f\x8b" else ".zip" if head[:2] == b"PK" else
           ".gpkg" if head[:6] == b"SQLite" else ".geojson")
    if not path.lower().endswith(ext):
        os.rename(path, path + ext)
        path += ext
    return path


# ----------------------------------------------------------------------------- reading to GeoDataFrame
def read_any(path, area_cc, member=None):
    import geopandas as gpd
    if path.endswith(".gz") and not path.endswith(".tar.gz"):
        raw = gzip.open(path, "rb").read()
        path = path[:-3]
        open(path, "wb").write(raw)
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as z:
            z.extractall(path + "_x")
        cands = [os.path.join(d, f) for d, _, fs in os.walk(path + "_x") for f in fs
                 if f.lower().endswith((".shp", ".gpkg", ".geojson", ".json"))]
        if member:
            cands = [c for c in cands if member.lower() in c.lower()] or cands
        if not cands:
            raise RuntimeError("zip holds no .shp/.gpkg/.geojson")
        # several members: take the biggest; the report names what was chosen
        path = max(cands, key=os.path.getsize)
    if path.endswith(".gpkg"):
        import pyogrio
        polys = []
        for lname, _ in pyogrio.list_layers(path):
            info = pyogrio.read_info(path, layer=lname)
            if "Polygon" in (info.get("geometry_type") or ""):
                polys.append((info["features"], lname))
        if not polys:
            raise RuntimeError("gpkg has no polygon layer")
        gdf = gpd.read_file(path, layer=max(polys)[1])        # biggest polygon layer
    else:
        gdf = gpd.read_file(path)
    return gdf, path


def finish(gdf, name_field, area_cc):
    """Reproject to 4326, keep polygons, make valid, add a clean `name` column."""
    import geopandas as gpd
    from shapely import make_valid
    if gdf.crs is None:
        b = gdf.total_bounds
        if abs(b).max() <= 180:
            gdf = gdf.set_crs(4326)
        elif CRS_HINT.get(area_cc):
            gdf = gdf.set_crs(CRS_HINT[area_cc])
        else:
            raise RuntimeError(f"no CRS in file and bounds {list(b)} are not lon/lat; add a hint")
    gdf = gdf.to_crs(4326)
    cols = {c.lower(): c for c in gdf.columns}
    nf = cols.get(name_field.lower())
    if nf is None:
        raise RuntimeError(f"name field '{name_field}' not found; columns: {list(gdf.columns)[:25]}")
    gdf = gdf[gdf.geometry.notna() & ~gdf.geometry.is_empty].copy()
    gdf["geometry"] = gdf.geometry.apply(make_valid)
    gdf = gdf.explode(index_parts=False)
    gdf = gdf[gdf.geometry.geom_type.isin(["Polygon", "MultiPolygon"])]
    gdf["name"] = gdf[nf].astype(str).str.strip()
    gdf = gdf[gdf["name"].ne("") & gdf["name"].ne("None") & gdf["name"].ne("nan")]
    return gdf


def slug(row, i):
    base = row["title"] or row["url"]
    m = re.search(r"file-([A-Za-z0-9_-]+?)\.geojson", base)
    if m:
        return m.group(1)[:60]
    host = urlparse(row["url"]).netloc.split(".")[-2] if "." in row["url"] else "src"
    tn = re.search(r"typenames?=([^&]+)", row["url"], re.I)
    tail = (tn.group(1) if tn else urlparse(row["url"]).path.split("/")[-1]) or str(i)
    return re.sub(r"[^A-Za-z0-9]+", "-", f"{row['area']}-{host}-{tail}")[:60].strip("-").lower()


def kind(url):
    u = url.lower()
    if "raw.githubusercontent.com" in u:
        return "intake"
    if "request=getfeature" in u:
        return "wfs"
    if "/ogc/features/" in u or "/ogc/v1/collections/" in u:
        return "ogcapi"
    return "file"


# ----------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--out", default="converted")
    ap.add_argument("--only", default="")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()

    rows = list(csv.DictReader(open(a.csv, encoding="utf-8")))
    only = {int(x) for x in a.only.split(",") if x.strip()}
    lic = {}
    lp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "licences.csv")
    if os.path.exists(lp):
        lic = {int(r["row"]): r for r in csv.DictReader(open(lp, encoding="utf-8"))}
    os.makedirs(a.out, exist_ok=True)
    report = []

    for i, row in enumerate(rows):
        if only and i not in only:
            continue
        k, sl = kind(row["url"]), slug(row, i)
        if a.list:
            print(i, k, sl, row["url"][:100])
            continue
        status, note, n = "ok", "", 0
        try:
            cc = row["area"].split("-")[-1] if row["area"].startswith("W-") else row["area"].split("-")[0]
            with tempfile.TemporaryDirectory() as wd:
                if k == "wfs":
                    feats = fetch_wfs(row["url"])
                    if not feats:
                        raise RuntimeError("WFS returned 0 features (wrong typeName?)")
                    import geopandas as gpd
                    gdf = gpd.GeoDataFrame.from_features(feats, crs=4326)
                elif k == "ogcapi":
                    feats = fetch_ogc_api(row["url"])
                    if not feats:
                        raise RuntimeError("OGC API returned 0 features")
                    import geopandas as gpd
                    gdf = gpd.GeoDataFrame.from_features(feats, crs=4326)
                else:
                    path = fetch_file(row["url"], wd)
                    gdf, used = read_any(path, cc)
                    note = f"read {os.path.basename(used)}"
                gdf = finish(gdf, row["name_field"], cc)
                n = len(gdf)
                if n == 0:
                    raise RuntimeError("no polygon features with a name after cleaning")
                keep = ["name"] + [c for c in gdf.columns if c not in ("name", "geometry")][:12]
                gdf[keep + ["geometry"]].to_file(os.path.join(a.out, sl + ".geojson"), driver="GeoJSON")
                L = lic.get(i, {})
                json.dump({"row": i, "area": row["area"], "source_url": row["url"], "name_field": row["name_field"],
                           "features": n, "retrieved": date.today().isoformat(),
                           "licence": L.get("licence", ""), "credit": L.get("credit", ""),
                           "licence_verified": L.get("verified", "no"),
                           # Nov 7 (Brandon): licences are believed, not confirmed; the rows with a 'hold' reason are converted
                           # for review only and are NOT published until a person checks them
                           "hold_for_check": bool(L.get("hold")), "hold_why": L.get("hold", ""),
                           "publish": False if L.get("hold") else "after review"},
                          open(os.path.join(a.out, sl + ".meta.json"), "w"), indent=1)
        except Exception as e:                      # one bad source must not stop the rest
            status, note = "failed", str(e)[:300]
        if status == "ok" and lic.get(i, {}).get("hold"):
            status, note = "ok-held", ("hold-for-check: " + lic[i]["hold"] + "; " + note).strip("; ")
        report.append({"row": i, "area": row["area"], "slug": sl, "status": status, "features": n, "note": note})
        print(i, status, sl, n, note)

    if not a.list:
        with open(os.path.join(a.out, "report.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["row", "area", "slug", "status", "features", "note"])
            w.writeheader(); w.writerows(report)
        bad = sum(r["status"] not in ("ok", "ok-held") for r in report)
        print(f"{len(report)-bad} ok, {bad} failed (see {a.out}/report.csv)")


if __name__ == "__main__":
    main()
