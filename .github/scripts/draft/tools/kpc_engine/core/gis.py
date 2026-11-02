"""One reader for every kind of official map service the registry and the plug-ins use:
ArcGIS REST (MapServer / FeatureServer layers), OGC WFS (1.1 / 2.0, GeoJSON or GML), OGC API - Features, and the Swiss
federal geo.admin.ch identify API. Every call goes through core.polite (manners, cache, BLOCKED classification).

A 'source' is a dict (a registry entry): {kind, url, layer, name_field, srs?, output_format?, cql?, grade, agency, ...}.
Hits come back as {name, attrs, geom (shapely, 4326, may be None), id, source_url}."""
import json, re, urllib.parse, xml.etree.ElementTree as ET

from . import geo

TEXT_SKIP = re.compile(r'^(shape|objectid|fid|gid|globalid|st_area|st_length|area|perimeter|created|last_edited|editor)', re.I)


def _q(d): return urllib.parse.urlencode(d, quote_via=urllib.parse.quote)


# ---------------------------------------------------------------- ArcGIS REST
def arcgis_layer_info(P, url, ref_=''):
    r, j = P.get_json(url.rstrip('/') + '?f=json', ref_=ref_, kind='layer-info', ttl_days=30)
    if j and 'error' in j:
        code = j['error'].get('code')
        if code in (498, 499) or 'token' in json.dumps(j['error']).lower():
            P.log_blocked(P.host(url), ref_, 'layer-info', 'token-only (needs sign-in)', url); return {'_blocked': 'token-only (needs sign-in)'}
        return {'_error': j['error']}
    if r.blocked: return {'_blocked': r.blocked}
    return j or {'_error': f'HTTP {r.status}'}


def arcgis_relocate(P, url, old_name, ref_=''):
    """Lesson 8: a 404 / error on a known layer id = re-read the service's layer list and match by NAME (renumbered)."""
    svc = re.sub(r'/\d+/?$', '', url.rstrip('/'))
    r, j = P.get_json(svc + '?f=json', ref_=ref_, kind='layer-info', ttl_days=1)
    for L in (j or {}).get('layers', []) + (j or {}).get('tables', []):
        if L.get('name', '').lower() == (old_name or '').lower(): return f'{svc}/{L["id"]}'
    return None


def arcgis_query(P, src, params, ref_='', kind='outline'):
    u = src['url'].rstrip('/') + '/query?' + _q({**params, 'f': 'json'})
    r, j = P.get_json(u, ref_=ref_, kind=kind, ttl_days=src.get('ttl_days', 14), timeout=60)
    if r.blocked: return None, r.blocked, u
    if not j: return None, f'HTTP {r.status}', u
    if 'error' in j:
        e = json.dumps(j['error'])
        if '498' in e or '499' in e or 'oken' in e:
            P.log_blocked(P.host(u), ref_, kind, 'token-only (needs sign-in)', u); return None, 'token-only (needs sign-in)', u
        if 'agination is not supported' in e and ('resultRecordCount' in params or 'resultOffset' in params):   # older servers (SEMARNAT)
            return arcgis_query(P, src, {k: v for k, v in params.items() if k not in ('resultRecordCount', 'resultOffset')}, ref_, kind)
        return None, 'error: ' + e[:160], u
    return j.get('features', []), None, u


def _arcgis_hits(src, feats, u):
    nf = src.get('name_field')
    out = []
    for f in feats or []:
        a = f.get('attributes', {})
        nm = a.get(nf) if nf else None
        if nm is None:
            for k, v in a.items():
                if isinstance(v, str) and re.search(r'name|nom|navn|naam|bezeich|denomin|nimi', k, re.I): nm = v; break
        oid = a.get(src.get('id_field') or 'OBJECTID', a.get('objectid', a.get('FID', a.get('fid'))))
        out.append({'name': nm, 'attrs': a, 'geom': geo.esri_to_shape(f.get('geometry')), 'id': oid, 'source_url': u})
    return out


def arcgis_point(P, src, lat, lon, buffer_m=0, geometry=True, ref_=''):
    p = {'geometry': f'{lon},{lat}', 'geometryType': 'esriGeometryPoint', 'inSR': 4326, 'spatialRel': 'esriSpatialRelIntersects',
         'outFields': '*', 'returnGeometry': 'true' if geometry else 'false', 'outSR': 4326, 'resultRecordCount': 25}
    if geometry: p.update({'maxAllowableOffset': src.get('offset', 0.00005), 'geometryPrecision': 6})
    if buffer_m:
        p.update({'distance': buffer_m, 'units': 'esriSRUnit_Meter'})
    if src.get('where'): p['where'] = src['where']
    else: p['where'] = '1=1'
    feats, err, u = arcgis_query(P, src, p, ref_)
    if err and buffer_m and 'error' in err:      # an old server without distance support: use an envelope instead
        bb = geo.bbox_around(lat, lon, buffer_m); p.pop('distance'); p.pop('units')
        p.update({'geometry': ','.join(map(str, bb)), 'geometryType': 'esriGeometryEnvelope'})
        feats, err, u = arcgis_query(P, src, p, ref_)
    return (_arcgis_hits(src, feats, u) if feats is not None else []), err


_NF = {}


_WDPA = {}


def cites_wdpa(P, src, ref_=''):
    """Club, round 3: reject any layer whose address, name, description, licence / copyright or fields cite WDPA /
    Protected Planet. ArcGIS layers are read once (?f=json, cached 30 days; the same page the name-field check reads).
    -> '' (fine) or the reason."""
    from core import rule_g
    u = (src.get('url') or '').rstrip('/')
    if u in _WDPA: return _WDPA[u]
    why = ''
    from core import rules
    if not rules.on('source_policy.wdpa_guard'): return ''          # switched off: kept, but every row from it is stamped non-official
    if rule_g.cites_wdpa(src): why = 'WDPA / Protected Planet copy (address / name / licence): never a source'
    elif '/rest/services/' in u and src.get('kind', 'arcgis') == 'arcgis':
        try:
            r, j = P.get_json(u + '?f=json', ref_=ref_, kind='fields', ttl_days=30)
            if isinstance(j, dict) and rule_g.cites_wdpa(j): why = 'WDPA / Protected Planet copy (layer description / licence / fields): never a source'
        except Exception:  # noqa: BLE001
            pass
    _WDPA[u] = why
    return why


def checked_name_field(P, src, ref_=''):
    """Alberta lesson: read the layer's ?f=json field names before a name search. A missing field gives an empty answer or a
    400, and an empty answer is not 'no record'. Cached per layer."""
    from core import rule_g
    u = src['url'].rstrip('/')
    if u in _NF: return _NF[u]
    nf = src.get('name_field')
    try:
        r, j = P.get_json(u + '?f=json', ref_=ref_, kind='fields', ttl_days=30)
        fields = (j or {}).get('fields') or []
    except Exception:  # noqa: BLE001
        fields = []
    if fields:
        good = rule_g.pick_name_field(fields, nf)
        if good and good != nf:
            src['name_field_note'] = f'name field {nf!r} is not on the layer; using {good!r} (read from ?f=json)'
        nf = good or nf
    _NF[u] = nf
    return nf


def arcgis_name(P, src, words, geometry=True, ref_='', limit=25):
    """Lesson 1: every layer is ALSO searched by name. Title Case LIKE (CPCAD's LIKE is case-sensitive and UPPER() gives 400)."""
    if not words: return [], None
    nf = checked_name_field(P, src, ref_)
    if not nf: return [], None
    w = max(words, key=len).replace("'", "''")
    pats = list(dict.fromkeys([w.title(), w, w.upper(), w.lower()]))
    hits, err = [], None
    for pat in pats:
        where = f"{nf} LIKE '%{pat}%'" + (f" AND ({src['where']})" if src.get('where') else '')
        p = {'where': where, 'outFields': '*', 'returnGeometry': 'true' if geometry else 'false', 'outSR': 4326, 'resultRecordCount': limit}
        if geometry: p.update({'maxAllowableOffset': src.get('offset', 0.0002), 'geometryPrecision': 6})
        feats, err, u = arcgis_query(P, src, p, ref_)
        if feats: hits = _arcgis_hits(src, feats, u); break
        if err and err.startswith(('blocked', 'token')): break
    return hits, err


def arcgis_walk(P, root, depth=2, ref_=''):
    """L1: walk ArcGIS REST folders two deep; keep polygon / line layers with a name-like text field."""
    out, todo = [], [(root.rstrip('/'), 0)]
    while todo:
        u, d = todo.pop(0)
        r, j = P.get_json(u + '?f=json', ref_=ref_, kind='walk', ttl_days=30)
        if not j: continue
        if d < depth:
            for f in j.get('folders', []): todo.append((root.rstrip('/') + '/' + f, d + 1))
        for s in j.get('services', []):
            if s.get('type') not in ('MapServer', 'FeatureServer'): continue
            su = s.get('url') or (re.sub(r'/rest/services.*$', '/rest/services/', root) + s['name'] + '/' + s['type'])
            rr, sj = P.get_json(su + '/layers?f=json', ref_=ref_, kind='walk', ttl_days=30)
            for L in (sj or {}).get('layers', []):
                if L.get('geometryType') not in ('esriGeometryPolygon', 'esriGeometryPolyline'): continue
                tf = [f['name'] for f in L.get('fields') or [] if f.get('type') == 'esriFieldTypeString']
                nf = next((f for f in tf if re.search(r'name|nom|navn|naam|bezeich|denomin|nimi', f, re.I)), None)
                if nf: out.append({'kind': 'arcgis', 'url': f'{su}/{L["id"]}', 'layer_name': L.get('name'), 'name_field': nf,
                                   'geometry': L.get('geometryType'), 'text_fields': tf})
    return out


# ---------------------------------------------------------------- OGC WFS
def _wfs_url(src, extra):
    base = src['url']
    sep = '&' if '?' in base else '?'
    return base + sep + _q(extra)


def wfs_features(P, src, extra, ref_='', kind='outline'):
    ver = src.get('version', '2.0.0')
    tn = 'typeNames' if ver.startswith('2') else 'typeName'
    p = {'service': 'WFS', 'version': ver, 'request': 'GetFeature', tn: src['layer']}
    if src.get('output_format'): p['outputFormat'] = src['output_format']
    p['count' if ver.startswith('2') else 'maxFeatures'] = extra.pop('_count', 25)
    p.update(extra)
    u = _wfs_url(src, p)
    r = P.get(u, ref_=ref_, kind=kind, ttl_days=src.get('ttl_days', 14), timeout=60, accept='application/json,application/gml+xml,text/xml,*/*;q=0.5')
    if r.blocked: return None, r.blocked, u
    if r.status != 200: return None, f'HTTP {r.status}', u
    b = r.body.lstrip()
    if b[:1] in (b'{', b'['):
        try: j = json.loads(b)
        except Exception: return None, 'bad json', u  # noqa: BLE001
        hits = []
        for f in j.get('features', []):
            a = f.get('properties') or {}
            g = f.get('geometry')
            gg = geo.geojson_to_shape(g) if g else None
            crs = (j.get('crs') or {}).get('properties', {}).get('name', '')
            epsg = re.search(r'(\d{4,6})$', crs or '')
            if gg is not None and epsg and epsg.group(1) not in ('4326', 'CRS84', '84', '4258'):
                import pyproj
                from core.geo import _tf as transform
                gg = transform(pyproj.Transformer.from_crs(f'EPSG:{epsg.group(1)}', 'EPSG:4326', always_xy=True).transform, gg)
            hits.append({'name': a.get(src.get('name_field')), 'attrs': a, 'geom': gg, 'id': f.get('id'), 'source_url': u})
        return hits, None, u
    if b'ExceptionReport' in b[:2000] or b'ServiceException' in b[:2000]:
        return None, 'error: ' + re.sub(r'\s+', ' ', b[:300].decode('utf-8', 'replace')), u
    try: root = ET.fromstring(b)
    except Exception: return None, 'bad xml', u  # noqa: BLE001
    hits = []
    for mem in list(root):
        if not mem.tag.endswith(('member', 'featureMember', 'featureMembers')): continue
        for feat in list(mem):
            a, g = {}, None
            for ch in feat.iter():
                if ch is feat: continue
                tag = ch.tag.split('}')[-1]
                if len(ch) == 0 and ch.text and ch.text.strip() and not ch.tag.startswith(('{http://www.opengis.net/gml', )):
                    a.setdefault(tag, ch.text.strip())
            for ch in feat:
                for sub in ch:
                    if sub.tag.startswith(('{http://www.opengis.net/gml', )):
                        g = g or geo.gml_to_shape(sub, src.get('srs_name'))
            nf = src.get('name_field')
            fid = feat.get('{http://www.opengis.net/gml/3.2}id') or feat.get('{http://www.opengis.net/gml}id') or feat.get('fid')
            hits.append({'name': a.get(nf.split(':')[-1]) if nf else None, 'attrs': a, 'geom': g, 'id': fid, 'source_url': u})
    return hits, None, u


def wfs_point(P, src, lat, lon, buffer_m=0, ref_=''):
    epsg = str(src.get('srs', '4326'))
    bb = geo.bbox_around(lat, lon, max(buffer_m, 5))
    x0, y0, x1, y1 = geo.to_crs_bbox(bb, epsg)
    ver = src.get('version', '2.0.0')
    if epsg in ('4326', '4258') and ver.startswith('2') and not src.get('bbox_xy'):
        box = f'{y0},{x0},{y1},{x1},urn:ogc:def:crs:EPSG::{epsg}'          # WFS 2.0 + urn = lat/lon order
    elif epsg in ('4326', '4258') and ver.startswith('1.1') and not src.get('bbox_xy'):
        box = f'{y0},{x0},{y1},{x1},urn:ogc:def:crs:EPSG::{epsg}'
    elif ver.startswith('2') and src.get('bbox_urn', geo.northing_first(epsg)) and not src.get('bbox_xy'):
        # WFS 2 + urn: EPSG axis order (SWEREF99 TM 3006 is northing, easting; an EPSG:xxxx box there silently returns nothing)
        box = (f'{y0},{x0},{y1},{x1}' if geo.northing_first(epsg) else f'{x0},{y0},{x1},{y1}') + f',urn:ogc:def:crs:EPSG::{epsg}'
    else:
        box = f'{x0},{y0},{x1},{y1},EPSG:{epsg}'
    extra = {'bbox': box}
    if src.get('srs_name'): extra['srsName'] = src['srs_name']
    hits, err, u = wfs_features(P, src, extra, ref_)
    return hits or [], err


def wfs_name(P, src, words, ref_=''):
    nf = src.get('name_field')
    if not nf or not words: return [], None
    w = max(words, key=len).replace("'", "''")
    if src.get('cql'):      # GeoServer
        hits, err, u = wfs_features(P, src, {'CQL_FILTER': f"strToLowerCase({nf}) LIKE '%{w.lower()}%'"}, ref_)
        return hits or [], err
    ver = src.get('version', '2.0.0')
    if ver.startswith('2'):
        flt = (f'<fes:Filter xmlns:fes="http://www.opengis.net/fes/2.0"><fes:PropertyIsLike wildCard="*" singleChar="." escapeChar="!" matchCase="false">'
               f'<fes:ValueReference>{nf}</fes:ValueReference><fes:Literal>*{w}*</fes:Literal></fes:PropertyIsLike></fes:Filter>')
    else:
        flt = (f'<ogc:Filter xmlns:ogc="http://www.opengis.net/ogc"><ogc:PropertyIsLike wildCard="*" singleChar="." escapeChar="!" matchCase="false">'
               f'<ogc:PropertyName>{nf}</ogc:PropertyName><ogc:Literal>*{w}*</ogc:Literal></ogc:PropertyIsLike></ogc:Filter>')
    hits, err, u = wfs_features(P, src, {'filter': flt}, ref_)
    return hits or [], err


# ---------------------------------------------------------------- OGC API Features
def ogcapi_point(P, src, lat, lon, buffer_m=0, ref_=''):
    bb = geo.bbox_around(lat, lon, max(buffer_m, 5))
    u = src['url'].rstrip('/') + f'/collections/{src["layer"]}/items?' + _q({'bbox': ','.join(f'{v:.6f}' for v in bb), 'f': 'json', 'limit': 25})
    r, j = P.get_json(u, ref_=ref_, kind='outline', ttl_days=14)
    if r.blocked: return [], r.blocked
    if not j: return [], f'HTTP {r.status}'
    return [{'name': (f.get('properties') or {}).get(src.get('name_field')), 'attrs': f.get('properties') or {},
             'geom': geo.geojson_to_shape(f.get('geometry')), 'id': f.get('id'), 'source_url': u} for f in j.get('features', [])], None


# ---------------------------------------------------------------- geo.admin.ch (Swiss federal)
def geoadmin_point(P, src, lat, lon, buffer_m=0, ref_=''):
    d = 0.001
    p = {'geometry': f'{lon},{lat}', 'geometryType': 'esriGeometryPoint', 'sr': 4326, 'layers': f'all:{src["layer"]}',
         'tolerance': 0 if not buffer_m else 1, 'returnGeometry': 'true', 'geometryFormat': 'geojson',
         'imageDisplay': '1000,1000,96', 'mapExtent': f'{lon - d},{lat - d},{lon + d},{lat + d}'}
    if buffer_m: p['tolerance'] = int(max(1, buffer_m / (2 * d * 111320 / 1000)))
    u = src['url'].rstrip('/') + '/identify?' + _q(p)
    r, j = P.get_json(u, ref_=ref_, kind='outline', ttl_days=14)
    if r.blocked: return [], r.blocked
    if not j: return [], f'HTTP {r.status}'
    out = []
    for f in j.get('results', []):
        a = f.get('attributes') or f.get('properties') or {}
        out.append({'name': a.get(src.get('name_field', 'label')), 'attrs': a, 'geom': geo.geojson_to_shape(f.get('geometry')),
                    'id': f.get('featureId', f.get('id')), 'source_url': u})
    return out, None


def geoadmin_name(P, src, words, ref_=''):
    if not words: return [], None
    w = max(words, key=len)
    u = src['url'].rstrip('/') + '/find?' + _q({'layer': src['layer'], 'searchText': w, 'searchField': src.get('name_field', 'label'),
                                                 'returnGeometry': 'true', 'geometryFormat': 'geojson', 'sr': 4326, 'contains': 'true'})
    r, j = P.get_json(u, ref_=ref_, kind='outline', ttl_days=14)
    if r.blocked: return [], r.blocked
    return [{'name': (f.get('attributes') or f.get('properties') or {}).get(src.get('name_field', 'label')), 'attrs': f.get('attributes') or f.get('properties') or {},
             'geom': geo.geojson_to_shape(f.get('geometry')), 'id': f.get('featureId', f.get('id')), 'source_url': u} for f in (j or {}).get('results', [])[:25]], None


# ---------------------------------------------------------------- dispatch
_DL = {}


def download_layer(P, src, ref_=''):
    """'download' kind: an official shapefile / KML zip (Romania's ministry zip, Japanese prefecture KML). Fetched once through the
    polite fetcher (cached 30 days), parsed locally, reprojected to WGS84 and indexed. Returns (records, error)."""
    if src['url'] in _DL: return _DL[src['url']], None
    import io, zipfile
    r = P.get(src['url'], ref_=ref_, kind='download', ttl_days=30, timeout=300, max_bytes=int(src.get('max_mb', 200)) * 2**20)
    if r.blocked: return None, r.blocked
    if r.status != 200: return None, f'HTTP {r.status}'
    recs = []
    body = r.body or b''
    head = body[:200].lstrip()
    if head.startswith(b'<') or head.startswith(b'{'):          # a bare KML or GeoJSON file (L4 page links)
        recs = _kml_or_geojson(body, src)
        if not recs: return None, 'no polygons in the KML / GeoJSON'
        from shapely.strtree import STRtree
        _DL[src['url']] = (recs, STRtree([x['geom'] for x in recs])); return _DL[src['url']], None
    try:
        z = zipfile.ZipFile(io.BytesIO(body))
    except Exception as ex:  # noqa: BLE001
        return None, f'not a zip ({ex.__class__.__name__})'
    for kn in [n for n in z.namelist() if n.lower().endswith(('.kml', '.geojson', '.json'))]:   # a KMZ
        recs += _kml_or_geojson(z.read(kn), src)
    shps = [n for n in z.namelist() if n.lower().endswith('.shp')]
    if src.get('member'): shps = [n for n in shps if src['member'] in n]
    for shp in shps:
        import shapefile                                   # pyshp
        base = shp[:-4]
        names_ = {n.lower(): n for n in z.namelist()}
        dbf = names_.get((base + '.dbf').lower()); shx = names_.get((base + '.shx').lower())
        rd = shapefile.Reader(shp=io.BytesIO(z.read(shp)), dbf=io.BytesIO(z.read(dbf)) if dbf else None,
                              shx=io.BytesIO(z.read(shx)) if shx else None, encoding=src.get('encoding', 'utf-8'), encodingErrors='replace')
        fields = [f[0] for f in rd.fields[1:]]
        tr = None
        prj = names_.get((base + '.prj').lower())
        if src.get('srs') and int(src['srs']) != 4326:
            from pyproj import Transformer
            tr = Transformer.from_crs(int(src['srs']), 4326, always_xy=True)
        elif not src.get('srs') and prj:                     # no srs given: read the .prj
            try:
                from pyproj import CRS, Transformer
                c = CRS.from_wkt(z.read(prj).decode('utf-8', 'replace'))
                if not c.equals(CRS.from_epsg(4326)): tr = Transformer.from_crs(c, 4326, always_xy=True)
            except Exception: tr = None  # noqa: BLE001
        from shapely.geometry import shape as _shape
        from core.geo import _tf
        for i, sr in enumerate(rd.iterShapeRecords()):
            try:
                g = _shape(sr.shape.__geo_interface__)
                if tr: g = _tf(tr.transform, g)
            except Exception:  # noqa: BLE001
                continue
            a = dict(zip(fields, list(sr.record)))
            recs.append({'name': a.get(src.get('name_field')) if src.get('name_field') else None, 'attrs': {k: (v if isinstance(v, (str, int, float)) else str(v)) for k, v in a.items()},
                         'geom': g, 'id': f'{shp}#{i}', 'source_url': src['url']})
    if not recs: return None, 'no shapefile records in the download'
    from shapely.strtree import STRtree
    _DL[src['url']] = (recs, STRtree([x['geom'] for x in recs]))
    return _DL[src['url']], None


def _kml_or_geojson(body, src):
    """Polygons from KML (Placemark / Polygon, WGS84 by definition) or GeoJSON (RFC 7946: WGS84)."""
    import json as _j
    from shapely.geometry import Polygon as _Poly, MultiPolygon as _MP
    out = []
    t = body.decode('utf-8', 'replace').lstrip('\ufeff').lstrip()
    if t.startswith('{'):
        try: j = _j.loads(t)
        except Exception: return []  # noqa: BLE001
        feats = j.get('features') or ([j] if j.get('type') == 'Feature' else [])
        for i, f in enumerate(feats):
            g = geo.geojson_to_shape(f.get('geometry'))
            if g is None or g.geom_type not in ('Polygon', 'MultiPolygon'): continue
            pr = f.get('properties') or {}
            nm = pr.get(src.get('name_field')) if src.get('name_field') else next((v for k, v in pr.items() if isinstance(v, str) and re.search('name|nom|naam|navn', k, re.I)), None)
            out.append({'name': nm, 'attrs': {k: v for k, v in pr.items() if isinstance(v, (str, int, float))}, 'geom': g, 'id': f'feature#{i}', 'source_url': src['url']})
        return out
    for i, pm in enumerate(re.findall(r'<(?:\w+:)?Placemark\b.*?</(?:\w+:)?Placemark>', t, re.S)):
        nm = re.search(r'<(?:\w+:)?name>\s*(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?\s*</(?:\w+:)?name>', pm, re.S)
        polys = []
        for poly in re.findall(r'<(?:\w+:)?Polygon\b.*?</(?:\w+:)?Polygon>', pm, re.S):
            rings = []
            for part in ('outerBoundaryIs', 'innerBoundaryIs'):
                for blk in re.findall(rf'<(?:\w+:)?{part}>.*?<(?:\w+:)?coordinates>(.*?)</(?:\w+:)?coordinates>', poly, re.S):
                    pts = [tuple(map(float, c.split(',')[:2])) for c in blk.split() if c.count(',') >= 1]
                    if len(pts) >= 4: rings.append((part, pts))
            outer = [p for k, p in rings if k == 'outerBoundaryIs']
            if outer:
                try: polys.append(_Poly(outer[0], [p for k, p in rings if k == 'innerBoundaryIs']).buffer(0))
                except Exception: pass  # noqa: BLE001
        if polys:
            g = polys[0] if len(polys) == 1 else _MP([p for p in polys if p.geom_type == 'Polygon'])
            out.append({'name': nm.group(1).strip() if nm else None, 'attrs': {}, 'geom': g, 'id': f'placemark#{i}', 'source_url': src['url']})
    return out


def download_point(P, src, lat, lon, buffer_m=0, ref_=''):
    from shapely.geometry import Point as _P
    d, err = download_layer(P, src, ref_)
    if err: return [], err
    recs, tree = d
    pt = _P(lon, lat)
    q = pt.buffer(buffer_m / 111000.0) if buffer_m else pt
    return [recs[i] for i in tree.query(q) if recs[i]['geom'].intersects(q)], None


def point(P, src, lat, lon, buffer_m=0, ref_=''):
    k = src['kind']
    if k == 'download': return download_point(P, src, lat, lon, buffer_m, ref_)
    if k == 'arcgis': return arcgis_point(P, src, lat, lon, buffer_m, True, ref_)
    if k == 'wfs': return wfs_point(P, src, lat, lon, buffer_m, ref_)
    if k == 'ogcapi': return ogcapi_point(P, src, lat, lon, buffer_m, ref_)
    if k == 'geoadmin': return geoadmin_point(P, src, lat, lon, buffer_m, ref_)
    return [], f'unknown kind {k}'


def by_name(P, src, words, ref_=''):
    k = src['kind']
    if k == 'arcgis': return arcgis_name(P, src, words, True, ref_)
    if k == 'wfs': return wfs_name(P, src, words, ref_)
    if k == 'geoadmin': return geoadmin_name(P, src, words, ref_)
    return [], None


def record_link(src, hit):
    """A link a person can open to see the record (ArcGIS: the query by id; others: the query that found it)."""
    if src['kind'] == 'arcgis' and hit.get('id') is not None:
        idf = src.get('id_field') or 'OBJECTID'
        return src['url'].rstrip('/') + '/query?' + _q({'where': f'{idf}={hit["id"]}', 'outFields': '*', 'f': 'html'})
    return hit.get('source_url')


def layer_url(src):
    """An address a person can open for the LAYER itself (a bare WFS endpoint answers 400 without parameters)."""
    u = src['url']; k = src.get('kind')
    if k == 'wfs':
        return u + ('&' if '?' in u else '?') + _q({'service': 'WFS', 'request': 'DescribeFeatureType', 'version': src.get('version', '2.0.0'),
                                                    'typeNames' if src.get('version', '2.0.0').startswith('2') else 'typeName': src.get('layer', '')})
    if k == 'ogcapi': return u.rstrip('/') + '/collections/' + urllib.parse.quote(src.get('layer', ''), safe=':') + '?f=html'
    if k == 'geoadmin': return 'https://api3.geo.admin.ch/rest/services/api/MapServer/' + src.get('layer', '')
    if k == 'arcgis': return u.rstrip('/') + '?f=html' if '?' not in u else u
    return u
