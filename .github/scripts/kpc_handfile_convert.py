#!/usr/bin/env python3
"""HAND-DOWNLOAD CONVERTER (chat 10, Nov 1 2026; Brandon's Spain + Ireland downloads). No outside libraries: a zip holding
GeoJSON, KML (a .kmz is a zip too) or ESRI shapefiles in a Transverse Mercator grid (UTM: EPSG 25828-25831 / 32628-32631 / 258xx; Irish ITM EPSG 2157;
already-GPS EPSG 4326 / 4258) -> one gzipped WGS84 GeoJSON per layer: file-<AREA>-<name>.geojson.gz, ready for branch
intake-files (the layer collector's 'hand-downloaded files' path).
  * TM inverse = Krueger series to n^3 (Karney 2011): centimetres within a zone; ETRS89 / IRENET95 = WGS84 to under a metre.
  * Lines simplified 2 m (Douglas-Peucker in metres; R-G6 allows 3 m), 6 decimals (~10 cm).
  * Shapefile polygons: outer rings (clockwise) and their holes kept as GeoJSON Polygon / MultiPolygon.
  python3 kpc_handfile_convert.py <zip> <AREA> <outdir> [name]"""
import gzip, io, json, math, pathlib, re, struct, sys, zipfile

GRS80 = (6378137.0, 1 / 298.257222101)
WGS84 = (6378137.0, 1 / 298.257223563)


def tm_params(epsg=None, wkt=''):
    """-> (a, f, k0, lat0, lon0, FE, FN) or None for degrees."""
    if epsg in (4326, 4258, 4230) or (wkt and 'PROJCS' not in wkt): return None
    if epsg:
        if 25828 <= epsg <= 25838: return (*GRS80, 0.9996, 0.0, (epsg - 25800) * 6 - 183.0, 500000.0, 0.0)
        if 32601 <= epsg <= 32660: return (*WGS84, 0.9996, 0.0, (epsg - 32600) * 6 - 183.0, 500000.0, 0.0)
        if epsg == 2157: return (*GRS80, 0.99982, 53.5, -8.0, 600000.0, 750000.0)
        if epsg == 3035: raise ValueError('EPSG:3035 (LAEA Europe) is not a TM grid: not supported')
    p = lambda k: float(re.search(rf'PARAMETER\["{k}",\s*([-\d.eE]+)', wkt, re.I).group(1))
    if 'Transverse_Mercator' not in wkt: raise ValueError('not a Transverse Mercator grid: ' + wkt[:80])
    sph = re.search(r'SPHEROID\["[^"]*",\s*([\d.]+),\s*([\d.]+)', wkt)
    return (float(sph.group(1)), 1 / float(sph.group(2)), p('Scale_Factor'), p('Latitude_Of_Origin'), p('Central_Meridian'), p('False_Easting'), p('False_Northing'))


def make_inverse(P):
    a, f, k0, lat0, lon0, FE, FN = P
    n = f / (2 - f); A = a / (1 + n) * (1 + n * n / 4 + n ** 4 / 64)
    al = (n / 2 - 2 * n * n / 3 + 5 * n ** 3 / 16, 13 * n * n / 48 - 3 * n ** 3 / 5, 61 * n ** 3 / 240)
    be = (n / 2 - 2 * n * n / 3 + 37 * n ** 3 / 96, n * n / 48 + n ** 3 / 15, 17 * n ** 3 / 480)
    de = (2 * n - 2 * n * n / 3 - 2 * n ** 3, 7 * n * n / 3 - 8 * n ** 3 / 5, 56 * n ** 3 / 15)
    e = math.sqrt(f * (2 - f))
    ph0 = math.radians(lat0)
    t0 = math.sinh(math.atanh(math.sin(ph0)) - e * math.atanh(e * math.sin(ph0)))   # conformal latitude of the origin
    xi0 = math.atan(t0); xi0 += sum(al[j] * math.sin(2 * (j + 1) * xi0) for j in range(3))
    N0 = k0 * A * xi0

    def inv(E, N):
        xi = (N - FN + N0) / (k0 * A); eta = (E - FE) / (k0 * A)
        xp = xi - sum(be[j] * math.sin(2 * (j + 1) * xi) * math.cosh(2 * (j + 1) * eta) for j in range(3))
        ep = eta - sum(be[j] * math.cos(2 * (j + 1) * xi) * math.sinh(2 * (j + 1) * eta) for j in range(3))
        chi = math.asin(math.sin(xp) / math.cosh(ep))
        phi = chi + sum(de[j] * math.sin(2 * (j + 1) * chi) for j in range(3))
        lam = math.radians(lon0) + math.atan2(math.sinh(ep), math.cos(xp))
        return math.degrees(lam), math.degrees(phi)
    return inv


TOL_M = 2.0   # R-G6: outlines simplified 3 m at most (never over 5 m); 2 m here


def dp(pts, tol):
    """Douglas-Peucker on a projected ring (metres), iterative."""
    if len(pts) < 5: return pts
    keep = [False] * len(pts); keep[0] = keep[-1] = True; st = [(0, len(pts) - 1)]
    while st:
        i, j = st.pop(); (x1, y1), (x2, y2) = pts[i], pts[j]; dx, dy = x2 - x1, y2 - y1; L = math.hypot(dx, dy) or 1e-9
        k, dm = -1, tol
        for m in range(i + 1, j):
            d = abs(dy * (pts[m][0] - x1) - dx * (pts[m][1] - y1)) / L
            if d > dm: k, dm = m, d
        if k > 0: keep[k] = True; st += [(i, k), (k, j)]
    return [p for p, kp in zip(pts, keep) if kp]


def clean_ring(ring, inv, metric):
    out = []
    if metric:
        pts = [tuple(c[:2]) for c in ring]
        if len(pts) > 4 and pts[0] == pts[-1]:   # a closed ring: split at the point farthest from the start, simplify both halves
            k = max(range(len(pts)), key=lambda i: (pts[i][0] - pts[0][0]) ** 2 + (pts[i][1] - pts[0][1]) ** 2)
            ring = dp(pts[:k + 1], TOL_M) + dp(pts[k:], TOL_M)[1:]
        else: ring = dp(pts, TOL_M)
        if len(ring) < 4: ring = pts   # a tiny area (a 0.6 ha monument) keeps every point
    for x, y in (tuple(c[:2]) for c in ring):
        lo, la = inv(x, y) if inv else (x, y)
        out.append([round(lo, 6), round(la, 6)])
    if out and out[0] != out[-1]: out.append(out[0])
    return out if len(out) >= 4 else None


def fix_geom(g, inv, metric):
    t = g.get('type'); c = g.get('coordinates')
    if t == 'Polygon': polys = [c]
    elif t == 'MultiPolygon': polys = c
    else: return None
    P = []
    for poly in polys:
        rings = [r for r in (clean_ring(rg, inv, metric) for rg in poly) if r]
        if rings: P.append(rings)
    if not P: return None
    return {'type': 'Polygon', 'coordinates': P[0]} if len(P) == 1 else {'type': 'MultiPolygon', 'coordinates': P}


def signed_area(r): return sum(r[i][0] * r[i + 1][1] - r[i + 1][0] * r[i][1] for i in range(len(r) - 1)) / 2


CYRILLIC = {'BG', 'RU', 'UA', 'BY', 'MK', 'RS', 'KZ', 'KG', 'MN', 'TJ'}   # no .cpg: Windows-Cyrillic is the usual DBF text there
LDID = {0x57: 'cp1252', 0x03: 'cp1252', 0xC8: 'cp1250', 0x64: 'cp852', 0xC9: 'cp1251', 0x65: 'cp866', 0xCB: 'cp1253', 0xCA: 'cp1254', 0x13: 'cp932'}


def read_shp(shp, dbf, enc=None):
    """Minimal ESRI shapefile reader: polygons (5 / 15 / 25) + their DBF attributes. enc = the .cpg's word (Poland's GDOS zips:
    windows-1250), else the DBF language byte, else UTF-8 (Nov 1: Polish names)."""
    recs = []
    d = dbf
    enc = enc or LDID.get(d[29]) or 'utf-8'
    try: ''.encode(enc)
    except LookupError: enc = 'utf-8'
    nrec, hlen, rlen = struct.unpack('<IHH', d[4:12]); flds = []; pos = 32
    while d[pos] != 0x0D:
        name = d[pos:pos + 11].split(b'\0')[0].decode('latin-1'); typ = chr(d[pos + 11]); ln = d[pos + 16]
        flds.append((name, typ, ln)); pos += 32
    rows = []
    for i in range(nrec):
        r = d[hlen + i * rlen: hlen + (i + 1) * rlen]
        if not r or r[0:1] == b'*': rows.append(None); continue
        o, row = 1, {}
        for name, typ, ln in flds:
            raw = r[o:o + ln]; o += ln
            try: v = raw.decode(enc).strip()
            except UnicodeDecodeError: v = raw.decode('utf-8' if enc != 'utf-8' else 'cp1252', 'replace').strip()
            if typ in 'NF' and v:
                try: v = float(v) if ('.' in v or 'e' in v.lower()) else int(v)
                except ValueError: pass
            row[name] = v
        rows.append(row)
    pos, k = 100, 0
    while pos + 8 <= len(shp):
        _, clen = struct.unpack('>ii', shp[pos:pos + 8]); body = shp[pos + 8: pos + 8 + clen * 2]; pos += 8 + clen * 2
        st = struct.unpack('<i', body[:4])[0]; props = rows[k] if k < len(rows) else {}; k += 1
        if st not in (5, 15, 25) or props is None: continue
        npart, npt = struct.unpack('<ii', body[36:44])
        parts = list(struct.unpack(f'<{npart}i', body[44:44 + 4 * npart])) + [npt]
        pts = struct.unpack(f'<{2 * npt}d', body[44 + 4 * npart: 44 + 4 * npart + 16 * npt])
        rings = [[(pts[2 * j], pts[2 * j + 1]) for j in range(parts[i], parts[i + 1])] for i in range(npart)]
        polys = []
        for rg in rings:   # shapefile: outer rings clockwise (negative area), holes counter-clockwise
            if signed_area(rg) <= 0 or not polys: polys.append([rg])
            else: polys[-1].append(rg)
        recs.append({'type': 'Feature', 'geometry': {'type': 'MultiPolygon', 'coordinates': polys}, 'properties': props})
    return recs


def read_kml(text):
    """KML / KMZ (Google Earth export, e.g. an ArcGIS 'f=kmz' query: Mississippi MDWFP Nov 1) -> GeoJSON features. Properties = the
    Placemark name + the 'Field Name / Field Value' table ArcGIS writes in the description (or ExtendedData). GPS degrees already."""
    import html as H, xml.etree.ElementTree as ET
    text = re.sub(r'\sxmlns(:\w+)?="[^"]*"', '', text, count=0)   # plain tag names
    text = re.sub(r'\s[\w.-]+:[\w.-]+="[^"]*"', '', re.sub(r'<(/?)[\w.-]+:', r'<\1', text))   # gx: / kml: / xsi: prefixes off
    root = ET.fromstring(text.encode('utf-8'))
    feats = []
    def ring(el):
        pts = [c.split(',') for c in (el.text or '').split()]
        return [[float(x[0]), float(x[1])] for x in pts if len(x) >= 2]
    for pm in root.iter('Placemark'):
        props = {'name': (pm.findtext('name') or '').strip()}
        desc = pm.findtext('description') or ''
        for k, v in re.findall(r'<td>([^<]*)</td>\s*<td>([^<]*)</td>', desc): props[H.unescape(k).strip()] = H.unescape(v).strip()
        for sd in pm.iter('SimpleData'): props[sd.get('name')] = (sd.text or '').strip()
        for d in pm.iter('Data'): props[d.get('name')] = (d.findtext('value') or '').strip()
        polys = []
        for pg in pm.iter('Polygon'):
            outer = [ring(c) for c in pg.iter('outerBoundaryIs') for c in c.iter('coordinates')]
            inner = [ring(c) for b in pg.iter('innerBoundaryIs') for c in b.iter('coordinates')]
            if outer and len(outer[0]) >= 4: polys.append(outer[:1] + [r for r in inner if len(r) >= 4])
        if polys: feats.append({'type': 'Feature', 'properties': props, 'geometry': {'type': 'MultiPolygon', 'coordinates': polys}})
    return feats


def convert(zpath, area, outdir, name=None):
    if not zipfile.is_zipfile(zpath):   # a single file (a saved ArcGIS / GeoJSON / KML answer): wrap it so the loop below reads it
        raw = pathlib.Path(zpath).read_bytes(); buf = io.BytesIO()
        kind = '.kml' if raw.lstrip()[:5] in (b'<?xml', b'<kml ') else '.json'
        with zipfile.ZipFile(buf, 'w') as w: w.writestr(pathlib.Path(zpath).stem + kind, raw)
        z = zipfile.ZipFile(buf)
    else: z = zipfile.ZipFile(zpath)
    made = []
    outdir = pathlib.Path(outdir); outdir.mkdir(parents=True, exist_ok=True)
    for n in z.namelist():
        low = n.lower(); stem = pathlib.Path(n).stem
        if low.endswith(('.json', '.geojson')):
            d = json.load(io.TextIOWrapper(z.open(n), encoding='utf-8'))
            if isinstance(d, dict) and d.get('geometryType') and any('attributes' in f for f in d.get('features') or []):   # ArcGIS's own JSON (f=json)
                sr = d.get('spatialReference') or {}; epsg = sr.get('latestWkid') or sr.get('wkid') or 4326
                feats = []
                for f in d.get('features') or []:
                    rings = (f.get('geometry') or {}).get('rings') or []
                    polys = []
                    for rg in rings:   # ArcGIS: outer rings clockwise, holes counter-clockwise (the same rule as shapefiles)
                        if signed_area(rg) <= 0 or not polys: polys.append([rg])
                        else: polys[-1].append(rg)
                    if polys: feats.append({'type': 'Feature', 'properties': f.get('attributes') or {}, 'geometry': {'type': 'MultiPolygon', 'coordinates': polys}})
            else:
                crs = str(((d.get('crs') or {}).get('properties') or {}).get('name') or 'EPSG:4326')
                m = re.search(r'(\d{4,5})\s*$', crs); epsg = int(m.group(1)) if m else 4326
                feats = d.get('features') or []
            P = tm_params(epsg)
        elif low.endswith('.kml'):
            feats = read_kml(z.read(n).decode('utf-8', 'replace')); P = None
        elif low.endswith('.shp'):
            base = n[:-4]; names = {x.lower(): x for x in z.namelist()}
            prj = z.read(names[(base + '.prj').lower()]).decode('latin-1') if (base + '.prj').lower() in names else ''
            cpg = z.read(names[(base + '.cpg').lower()]).decode('latin-1').strip().lower() if (base + '.cpg').lower() in names else ''
            cpg = {'ansi 1250': 'cp1250', '1250': 'cp1250', 'ansi 1252': 'cp1252', '1252': 'cp1252', 'utf8': 'utf-8', '65001': 'utf-8'}.get(cpg, cpg) or None
            if not cpg and area.split('-')[0] in CYRILLIC: cpg = 'cp1251'   # Nov 2: Bulgaria's register says cp1252 in its header but holds Windows-Cyrillic
            feats = read_shp(z.read(n), z.read(names[(base + '.dbf').lower()]), cpg)
            P = tm_params(None, prj) if prj else None
        else: continue
        inv = make_inverse(P) if P else None
        out = []
        for ft in feats:
            g = fix_geom(ft.get('geometry') or {}, inv, bool(P))
            if g: out.append({'type': 'Feature', 'properties': ft.get('properties') or {}, 'geometry': g})
        if not out: continue
        slug = re.sub(r'[^A-Za-z0-9]+', '-', stem).strip('-').lower()
        if len(slug) < 3 or any(m[0].endswith(f'-{slug}.geojson.gz') for m in made):   # a Japanese / Polish file name, or two with the same name in one zip
            slug = (slug + '-' if slug else '') + __import__('hashlib').md5(n.encode('utf-8', 'replace')).hexdigest()[:6]
        o = outdir / f"file-{area}-{name or pathlib.Path(zpath).stem}-{slug}.geojson.gz"
        with gzip.open(o, 'wt', encoding='utf-8') as fh:
            json.dump({'type': 'FeatureCollection', 'crs': {'type': 'name', 'properties': {'name': 'EPSG:4326'}},
                       'source': f'{pathlib.Path(zpath).name}:{n} (hand download, converted by kpc_handfile_convert.py)', 'features': out}, fh, ensure_ascii=False)
        made.append((o.name, len(out), o.stat().st_size))
    return made


if __name__ == '__main__':
    for m in convert(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else None): print(*m)
