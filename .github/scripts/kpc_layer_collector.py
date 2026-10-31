#!/usr/bin/env python3
"""LAYER COLLECTOR (chat 10, Oct 30 2026; HQ 8:10 AM, Brandon 8:06 AM 'automate all we can'). Part of the daily copy run.
Reads every line starting `LAYER |` in KPC-Links .claude/build/research/fable/*.md:
    LAYER | <park ref> | <agency> | <layer URL (…/MapServer/N or …/FeatureServer/N, or a download link)> | name field: <FIELD> | <note>
New lines (by ref + URL) go down the same path as the GIS hunter's hits, Rule G as written:
  REST layer -> layer opens, polygons, the name field exists -> one point query at the POTA pin: pin inside? record name + acres ->
               the name tier (T-1..T-6) -> a SURE / LIKELY hit = one question in data/waiting/questions/layer-collector.json
               (chat 11 YES; AUTO-1 rules do NOT apply to these: a person answers) and the layer goes to data/intake/queue.json
               (open-terms / publisher check by the intake bot);
  download   -> straight to the intake queue (the intake probes it), no question yet.
A line that fails gets a short reason in data/intake/collector.json (chat 8 reads it there); never a comment or an email.
  LINKS=links python3 kpc_layer_collector.py [AREA ...]     (AREA = only those fable files, e.g. US-DE). Never fails."""
import datetime as dt, json, math, os, pathlib, re, sys, time, urllib.parse

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import kpc_tiers as T  # noqa: E402
import kpc_order as O  # noqa: E402
try:
    from kpc_manners import Manners
    M = Manners('KPC layer collector (chat 10)')
except Exception:  # noqa: BLE001
    M = None
LINKS = pathlib.Path(os.environ.get('LINKS') or '../links')
LOG = pathlib.Path('data/intake/collector.json')
QF = pathlib.Path('data/waiting/questions/layers.json')   # chat 2 (Oct 30 8:20 AM): kpc_key_layers.py wires every YES row into state-gis.json
QUEUE = pathlib.Path('data/intake/queue.json')
TODAY = dt.date.today().isoformat()
LINE = re.compile(r'^LAYER\s*\|\s*([A-Z0-9]{1,4}-\d{4,5})\s*\|\s*([^|]*)\|\s*(\S+)\s*\|\s*name field:\s*([^|]*)\|?(.*)$', re.I)


def load(p, d=None):
    try: return json.load(open(p, encoding='utf-8'))
    except Exception: return d  # noqa: BLE001


def get_json(u, params=None):
    if not M: raise RuntimeError('no manners module')
    q = u.rstrip('/') + ('&' if '?' in u else '?') + urllib.parse.urlencode({**(params or {}), 'f': 'json'})
    st, hd, body, final = M.get(q, accept='application/json')
    if not (isinstance(st, int) and st < 400 and body): raise RuntimeError(f'answer {st}')
    j = json.loads(body.decode('utf-8', 'replace'))
    if isinstance(j, dict) and j.get('error'): raise RuntimeError(str(j['error'].get('message') or j['error'])[:80])
    return j


def pin(ref):
    if ref.startswith('US-'):
        import glob
        for f in glob.glob('data/parkinfo/US-*.json'):
            v = ((load(f, {}) or {}).get('parks') or {}).get(ref)
            if v and len(v) > 6 and v[5] is not None: return v[5], v[6], v[0]
    for r in (load('data/canada.json', {}) or {}).get('rows') or []:
        if r and r[0] == 'POTA' and r[1] == ref: return r[3], r[4], r[2]
    import glob
    for f in glob.glob('data/pota/t/*.json'):   # the rest of the world (HQ 8:45 AM (3): top-15 W files)
        for row in load(f, []) or []:
            if isinstance(row, list) and len(row) >= 4 and row[0] == ref: return row[2], row[3], row[1]
    return None


def kind_of(agency, note, name):
    s = f'{agency} {note} {name}'.lower()
    if re.search(r'wildlife|fish|game|hunting|waterfowl|faune', s): return 'wild'
    if re.search(r'forest|forêt', s): return 'forest'
    if re.search(r'preserve|natural area|nature reserve|conservation', s): return 'preserve'
    if re.search(r'park|parc|recreation', s): return 'park'
    return 'land'


def acres(rings):
    tot = 0.0
    for r in rings:
        if len(r) < 3: continue
        la0 = sum(p[1] for p in r) / len(r); kx = 111320 * math.cos(math.radians(la0)); ky = 110540
        tot += sum((r[i][0] * kx) * (r[(i + 1) % len(r)][1] * ky) - (r[(i + 1) % len(r)][0] * kx) * (r[i][1] * ky) for i in range(len(r))) / 2
    return round(abs(tot) / 4046.86)


def check(ref, agency, url, field):
    """-> (status, why, question or None, queue row or None)"""
    p = pin(ref)
    if not p: return 'failed', 'no POTA pin on file for this park number', None, None
    la, lo, pn = p
    if not re.search(r'/(MapServer|FeatureServer)/\d+/?$', url, re.I):
        if re.search(r'^https?://', url) and re.search(r'\.(zip|geojson|json|kml|kmz|gpkg|shp)\b|download|/items/|opendata|hub\.arcgis', url, re.I):
            return 'queued', 'a download / catalogue link: the intake bot probes it (no pin test until it is a query layer)', None, {'url': url}
        return 'failed', 'not a layer URL (…/MapServer/N or …/FeatureServer/N) or a download link', None, None
    try: meta = get_json(url)
    except Exception as e: return 'failed', f'the layer did not open ({str(e)[:60]})', None, None  # noqa: BLE001
    if 'olygon' not in str(meta.get('geometryType', '')): return 'failed', f"not a polygon layer ({meta.get('geometryType')})", None, None
    names = {f.get('name') for f in meta.get('fields') or []}
    if field not in names:
        alt = next((n for n in names if n and n.lower() == field.lower()), None)
        if not alt: return 'failed', f"no field '{field}' on the layer (fields: {', '.join(sorted(n for n in names if n)[:8])}…)", None, None
        field = alt
    try:
        j = get_json(url.rstrip('/') + '/query', {'geometry': f'{lo},{la}', 'geometryType': 'esriGeometryPoint', 'inSR': 4326, 'spatialRel': 'esriSpatialRelIntersects',
                                                  'outFields': '*', 'returnGeometry': 'true', 'outSR': 4326, 'maxAllowableOffset': 0.0005})
    except Exception as e: return 'failed', f'the pin query failed ({str(e)[:60]})', None, None  # noqa: BLE001
    feats = j.get('features') or []
    if not feats: return 'failed', 'pin outside: no polygon of this layer holds the POTA pin', None, {'url': url}
    f = feats[0]; a = f.get('attributes') or {}
    rn = str(a.get(field) or ''); ac = acres((f.get('geometry') or {}).get('rings') or [])
    oid = a.get('OBJECTID') or a.get('objectid') or a.get('FID')
    tier, why = T.tier(pn, rn, ac, None, 1)
    q = {'area': f"{ref[:2]}-?", 'ref': ref, 'park': pn, 'tier': tier, 'why': why, 'kind': 'layer line (chat 8)', 'record': oid, 'record_name': rn[:120],
         'acres_approx': ac, 'layer': url, 'agency': agency, 'record_link': f'{url}/query?objectIds={oid}&outFields=*&returnGeometry=false&f=html',
         'pota_link': f'https://pota.app/#/park/{ref}', 'question': "Is this official record that park (the agency's own boundary for it)? YES / NO",
         'answer': None, 'checked_by': None, 'how': None, 'source': 'layer collector (fable LAYER line)',
         'st': ref[3:5] if False else '', 'url': url, 'name_field': field, 'kind_layer': kind_of(agency, '', pn), 'licence': ''}
    if tier == 'UNLIKELY': return 'evidence', f"pin inside '{rn[:50]}' ({ac:,} ac) but {why}: kept as evidence, not asked", None, {'url': url}
    return 'asked', f"pin inside '{rn[:50]}' ({ac:,} ac), {tier}: question for chat 11", q, {'url': url}


# ------------------------------------------------------------------------------------------------ crawler layers (Brandon Oct 30 10:41 AM)
ATLAS_LINE = re.compile(r'^\s+- (.+?): (https?://\S+?/(?:MapServer|FeatureServer)/\d+) \(name field ([^)]*)\)')
CRAWL_MAX = int(os.environ.get('CRAWL_MAX') or 40)


def open_parks(area):
    """Parks of an area still WITHOUT an official outline, with their POTA pins: {ref: (la, lo, name)}."""
    import glob
    if area.startswith('US-'):
        K = (load(LINKS / 'data' / 'us-key' / f'{area}.json', {}) or {}).get('parks') or {}
        P = (load(f'data/parkinfo/{area}.json', {}) or {}).get('parks') or {}
        return {r: (v[5], v[6], v[0]) for r, v in P.items() if len(v) > 6 and v[5] is not None and (K.get(r) or {}).get('g') != 'official'}
    if area.startswith('CA-'):
        K = (load(LINKS / 'data' / 'ca-key' / f'{area}.json', {}) or {}).get('parks') or {}
        rows = {r[1]: (r[3], r[4], r[2]) for r in (load('data/canada.json', {}) or {}).get('rows') or [] if r and r[0] == 'POTA'}
        return {r: rows[r] for r, v in K.items() if r in rows and (v or {}).get('g') != 'official'}
    cc = area[2:] if area.startswith('W-') else area
    K = (load(LINKS / 'data' / 'world-key' / f'{cc}.json', {}) or {}).get('parks') or {}
    out = {}
    for f in glob.glob('data/pota/t/*.json'):
        for row in load(f, []) or []:
            if isinstance(row, list) and len(row) >= 4 and str(row[0]).startswith(cc + '-') and not (K.get(row[0]) or {}).get('m'):
                out[row[0]] = (row[2], row[3], row[1])
    return out


def inside(x, y, ring):
    c = False; j = len(ring) - 1
    for i in range(len(ring)):
        xi, yi = ring[i][0], ring[i][1]; xj, yj = ring[j][0], ring[j][1]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-12) + xi: c = not c
        j = i
    return c


def crawled_layers(want):
    """Every polygon layer the atlas crawler listed (agency-atlas/<area>.md '## Layers on these servers')."""
    out = []
    for f in sorted((LINKS / '.claude' / 'build' / 'research' / 'agency-atlas').glob('*.md')):
        if want and f.stem not in want: continue
        m = re.search(r'\n## Layers on these servers \(atlas crawler[^\n]*\n(.*?)(?=\n## |\Z)', f.read_text(encoding='utf-8'), re.S)
        for l in (m.group(1).split('\n') if m else []):
            a = ATLAS_LINE.match(l)
            if a: out.append((f.stem, a.group(1).strip(), a.group(2), a.group(3).strip()))
    found = {**(load('data/intake/found-layers-stage2.json', {}) or {}), **(load('data/intake/found-layers.json', {}) or {})}   # + world stage 2 (phone book)
    for u, v in found.items():   # the two GIS finders (map viewers, open-data portals) + the world finder's stage 2
        area = str(v.get('area') or '')
        if '?' in area or not area or (want and area not in want): continue
        out.append((area, f"{v.get('name', '')} ({v.get('from', '')})", u, '?'))
    return list(dict.fromkeys(out))


def test_crawled(want, log, qs, queue, seen, n):
    """Each crawler-listed layer, once: ONE query per 120 open pins of its area (multipoint), the hit polygons judged by the name
    tiers; SURE / LIKELY = a question for chat 11 (same file + shape as the LAYER lines) and the layer to the intake queue."""
    done = 0
    for area, lname, url, field in sorted(crawled_layers(want), key=lambda x: O.rank(x[0])):   # US + CA first (Brandon Oct 30 12:44 PM)
        k = f'crawl|{area}|{url}'
        if k in log: continue
        if done >= CRAWL_MAX: break
        done += 1
        P = open_parks(area)
        if not P: log[k] = {'area': area, 'url': url, 'status': 'skipped', 'why': 'no open parks in this area', 'date': TODAY}; continue
        try:
            meta = get_json(url)
            if 'olygon' not in str(meta.get('geometryType', '')): raise RuntimeError(f"not polygons ({meta.get('geometryType')})")
            names = {f_.get('name') for f_ in meta.get('fields') or []}
            fld = field if field in names else next((nm for nm in names if nm and re.search(r'(^|_)(name|nom|unit_?nm|prop_?name|park_?name|site_?name|label)$', nm, re.I)), None)
            if not fld: raise RuntimeError('no name field')
            pts = list(P.items()); hits = 0
            for i in range(0, len(pts), 120):
                chunk = pts[i:i + 120]
                mp = {'points': [[round(v[1], 5), round(v[0], 5)] for _, v in chunk], 'spatialReference': {'wkid': 4326}}
                j = get_json(url.rstrip('/') + '/query', {'geometry': json.dumps(mp, separators=(',', ':')), 'geometryType': 'esriGeometryMultipoint', 'inSR': 4326,
                                                          'spatialRel': 'esriSpatialRelIntersects', 'outFields': '*', 'returnGeometry': 'true', 'outSR': 4326,
                                                          'maxAllowableOffset': 0.002, 'geometryPrecision': 5})
                feats = j.get('features') or []
                for r, (la, lo, pn) in chunk:
                    for f_ in feats:
                        rings = (f_.get('geometry') or {}).get('rings') or []
                        if not any(inside(lo, la, rg) for rg in rings): continue
                        a_ = f_.get('attributes') or {}; rn = str(a_.get(fld) or ''); ac = acres(rings)
                        oid = a_.get('OBJECTID') or a_.get('objectid') or a_.get('FID')
                        under = sum(1 for _, (la2, lo2, _n) in chunk if any(inside(lo2, la2, rg) for rg in rings))
                        tier, why = T.tier(pn, rn, ac, None, under)
                        if tier == 'UNLIKELY': continue
                        hits += 1
                        qs.append({'area': area, 'ref': r, 'park': pn, 'tier': tier, 'why': why, 'kind': 'park', 'record': oid, 'record_name': rn[:120], 'acres_approx': ac,
                                   'layer': url, 'agency': lname[:80], 'record_link': f'{url}/query?objectIds={oid}&outFields=*&returnGeometry=false&f=html',
                                   'pota_link': f'https://pota.app/#/park/{r}', 'question': "Is this official record that park (the agency's own boundary for it)? YES / NO",
                                   'answer': None, 'checked_by': None, 'how': None, 'source': 'layer collector (atlas crawler layer)',
                                   'st': area[3:] if area[:3] in ('US-', 'CA-') else area.replace('W-', ''), 'url': url, 'name_field': fld,
                                   'kind_layer': None, 'licence': ''})
                        qs[-1]['kind'] = kind_of(lname, '', pn); qs[-1].pop('kind_layer', None)
            if hits and url not in seen:
                queue['rows'].append({'url': url, 'title': f'{lname[:60]} (atlas crawler, {area})', 'from': 'atlas crawler', 'added': TODAY, 'closes': sorted({q['ref'] for q in qs if q.get('url') == url})[:50], 'note': f'{hits} SURE / LIKELY park(s) at the pins'})
                seen.add(url)
            log[k] = {'area': area, 'url': url, 'status': 'asked' if hits else 'no match', 'why': f'{len(P)} open parks tested, {hits} SURE / LIKELY hit(s)', 'date': TODAY}
            n['asked' if hits else 'evidence'] = n.get('asked' if hits else 'evidence', 0) + hits
        except Exception as e:  # noqa: BLE001
            log[k] = {'area': area, 'url': url, 'status': 'failed', 'why': f'{type(e).__name__}: {str(e)[:70]}', 'date': TODAY}; n['failed'] += 1
    return done


# ------------------------------------------------------------------------------------------------ outside research (HQ Oct 30 7:45 PM)
EXT_F = pathlib.Path('data/intake/external-sources-oct30.json')
EXT_OUT = pathlib.Path('data/intake/external-results.json')
EXT_MIN = float(os.environ.get('EXT_MINUTES') or 55)
NAMEF = re.compile(r'(^|_)(name|nom|unit_?nm|unit_?name|prop_?name|park_?name|site_?name|area_?name|loc_?nm|label|trail_?name|trl_?name|rec_?name)$', re.I)


def ext_index():
    """{ref: (la, lo, name, 'US-XX')} for every US park, built once (pin() reads every file per call)."""
    out = {}
    for f in pathlib.Path('data/parkinfo').glob('US-*.json'):
        for r, v in ((load(f, {}) or {}).get('parks') or {}).items():
            if v and len(v) > 6 and v[5] is not None: out[r] = (v[5], v[6], v[0], f.stem)
    for r, v in ((load('data/parkinfo/CA.json', {}) or {}).get('parks') or {}).items():   # HQ 8:50 PM: Canada too
        if v and len(v) > 10 and v[5] is not None: out[r] = (v[5], v[6], v[0], f'CA-{v[10]}')
    for f in pathlib.Path('data/pota/t').glob('*.json'):   # the world: POTA's own pins
        for row in load(f, []) or []:
            if row and len(row) > 3 and row[0] not in out and not str(row[0]).startswith(('US-', 'CA-')): out[row[0]] = (row[2], row[3], row[1], 'W-' + str(row[0]).split('-')[0])
    return out


def known_layers():
    k = set()
    for pat in ('data/us-key/layers.json', 'data/ca-key/layers.json'):
        d = load(LINKS / pat, {}) or {}
        k |= {str(u).rstrip('/').lower() for u in (d.values() if isinstance(d, dict) else d) if isinstance(u, str)}
        k |= {str(u).rstrip('/').lower() for u in (d.keys() if isinstance(d, dict) else []) if str(u).startswith('http')}
    try: k |= {str(u).rstrip('/').lower() for u in re.findall(r'https?://[^"\s]+?/(?:MapServer|FeatureServer)/\d+', open(LINKS / 'data' / 'state-gis.json', encoding='utf-8').read())}
    except Exception: pass  # noqa: BLE001
    return k


def external(log, qs, queue, seen, n):
    """Brandon's outside research: each (park or trail, layer) the researcher assigned, tested like a LAYER line: polygon layers =
    one multipoint query per 120 POTA pins (pin inside + name tier); line layers (trails) = the pin within 200 m of a named line.
    SURE / LIKELY -> chat 11 (data/waiting/questions/layers.json); every layer it touched -> the intake queue (publisher + licence test)."""
    D = {}
    for f in sorted(EXT_F.parent.glob('external-sources-*.json')):   # Brandon Oct 30 7:43 PM: more workbooks coming: every external-sources-<name>.json is read
        for key, urls in (load(f, {}) or {}).items():
            if isinstance(urls, list) and '|' in key: D.setdefault(key, []).extend(u for u in urls if u not in D.get(key, []))
    if not D: return None
    P = ext_index(); KN = known_layers(); t0 = time.time()
    R = load(EXT_OUT, {'about': "Outside research (Oct 30) tested by the layer collector: per park/trail and layer, what the pin test found. 'source assigned, exact feature not verified' until here.", 'pairs': {}, 'layers': {}}) or {}
    R.setdefault('pairs', {}); R.setdefault('layers', {})
    if not R.get('retried_404'):   # Oct 31: 1,172 world pairs failed on a too-long multipoint (404): once, test them again point by point
        for k_ in [k_ for k_, v in R['pairs'].items() if v.get('result') == 'failed' and 'answer 404' in str(v.get('why'))]: del R['pairs'][k_]
        R['retried_404'] = TODAY
    HINT = {}
    for f in sorted(EXT_F.parent.glob('world-sources-*.json')):   # HQ Oct 31 1:05 AM: world outside research ('rest' = REST layers; 'other' = leads for chat 9)
        for ref, v in ((load(f, {}) or {}).get('rest') or {}).items():
            if isinstance(v, dict) and v.get('layer'):
                D.setdefault(f'Parks|{ref}', [])
                if v['layer'] not in D[f'Parks|{ref}']: D[f'Parks|{ref}'].append(v['layer'])
                if v.get('field'): HINT[v['layer'].rstrip('/')] = v['field']
    by = {}
    for key, urls in D.items():
        kind, ref = key.split('|', 1)
        for u in urls or []: by.setdefault(u.rstrip('/'), []).append((ref, kind))
    # a service ROOT (…/MapServer with no layer number): its polygon / line layers, each tested (Oct 31: 31 roots had 'no name field')
    roots = R.setdefault('roots', {})
    for u in [x for x in list(by) if re.search(r'/(MapServer|FeatureServer)$', x, re.I)]:
        if u not in roots:
            try:
                j = get_json(u)
                roots[u] = [f"{u}/{l['id']}" for l in j.get('layers') or [] if not l.get('subLayerIds') and 'oint' not in str(l.get('geometryType', ''))][:12]
            except Exception as e: roots[u] = []; R['layers'].setdefault(u, {})['error'] = f'service root did not open: {str(e)[:60]}'  # noqa: BLE001
        kids = roots[u]
        if kids:
            for c in kids: by.setdefault(c, []).extend(x for x in by[u] if x not in by.get(c, []))
            for r, k in by.pop(u): R['pairs'].setdefault(f'{r}|{u}', {'ref': r, 'kind': k, 'result': 'split', 'why': f'service root: tested on its {len(kids)} layers'})
    def order(u):   # Delaware first (the small test), then US, Canada, North America, W1-W10, the rest (kpc_order)
        sts = sorted({(P.get(r) or (0, 0, '', 'ZZ-ZZ'))[3] for r, _ in by[u]})
        return (0 if 'US-DE' in sts else 1, 0 if any(x.startswith('US-') for x in sts) else 1, min((O.rank(x) for x in sts), default=(9, 0)), sts[0] if sts else 'ZZ', u)
    for u in sorted(by, key=order):
        if time.time() - t0 > EXT_MIN * 60: break   # the rest next run (pairs already done are skipped)
        todo = [(r, k) for r, k in by[u] if f'{r}|{u}' not in R['pairs']]
        if not todo: continue
        L = R['layers'].setdefault(u, {'new_to_us': u.lower() not in KN, 'host': urllib.parse.urlsplit(u).hostname})
        try:
            meta = get_json(u); gt = str(meta.get('geometryType', ''))
            L['geometry'] = gt; L['title'] = meta.get('name', '')
            flds = [f_ for f_ in meta.get('fields') or [] if f_.get('name')]
            names = [f_['name'] for f_ in flds]
            strs = [f_['name'] for f_ in flds if 'String' in str(f_.get('type', ''))] or names
            df = meta.get('displayField')
            fld = ((HINT.get(u) if HINT.get(u) in names else None)   # the researcher's own field
                   or next((nm for nm in names if NAMEF.search(nm)), None)
                   or (df if df in strs else None)   # the layer's own display field
                   or next((nm for nm in strs if re.search(r'name|_nm$|nm$|^nom|titre|title|label|desc', nm, re.I) and not re.search(r'file|admin|agency|owner|county|state|type|code', nm, re.I)), None)
                   or next((nm for nm in strs if re.search(r'name|_nm$|nm$', nm, re.I)), None))
            if not names and meta.get('subLayers'): raise RuntimeError('a group layer (its sub-layers hold the data)')
            if not fld: raise RuntimeError('no name field (' + ', '.join(names[:8]) + ')')
            L['name_field'] = fld
        except Exception as e:  # noqa: BLE001
            L['error'] = f'{type(e).__name__}: {str(e)[:80]}'; L['tries'] = L.get('tries', 0) + 1
            if L['tries'] < 3 and 'no name field' not in L['error']: continue   # a layer that did not open gets two more runs before its pairs fail
            for r, k in todo: R['pairs'][f'{r}|{u}'] = {'ref': r, 'kind': k, 'result': 'failed', 'why': L['error']}
            continue
        pts = [(r, k, P[r]) for r, k in todo if r in P]
        for r, k in todo:
            if r not in P: R['pairs'][f'{r}|{u}'] = {'ref': r, 'kind': k, 'result': 'failed', 'why': 'no POTA pin on file'}
        hits = 0
        try:
            if 'olygon' in gt:
                for i in range(0, len(pts), 60):
                    chunk = pts[i:i + 60]
                    mp = {'points': [[round(v[1], 5), round(v[0], 5)] for _, _, v in chunk], 'spatialReference': {'wkid': 4326}}
                    try:
                        j = get_json(u + '/query', {'geometry': json.dumps(mp, separators=(',', ':')), 'geometryType': 'esriGeometryMultipoint', 'inSR': 4326,
                                                    'spatialRel': 'esriSpatialRelIntersects', 'outFields': '*', 'returnGeometry': 'true', 'outSR': 4326,
                                                    'maxAllowableOffset': 0.002, 'geometryPrecision': 5})
                        feats = j.get('features') or []
                    except RuntimeError as e:   # some servers refuse a multipoint: one point at a time
                        if not re.search(r'nvalid|rror|404|414|too long|not supported', str(e)): raise   # Oct 31: a long multipoint GET answered 404 on some servers
                        feats = []
                        for _r, _k, (la1, lo1, _p, _s) in chunk:
                            feats += (get_json(u + '/query', {'geometry': f'{lo1},{la1}', 'geometryType': 'esriGeometryPoint', 'inSR': 4326, 'spatialRel': 'esriSpatialRelIntersects',
                                                              'outFields': '*', 'returnGeometry': 'true', 'outSR': 4326, 'maxAllowableOffset': 0.002}).get('features') or [])
                    for r, k, (la, lo, pn, st) in chunk:
                        best = None
                        for f_ in feats:
                            rings = (f_.get('geometry') or {}).get('rings') or []
                            if not any(inside(lo, la, rg) for rg in rings): continue
                            a_ = f_.get('attributes') or {}; rn = str(a_.get(fld) or ''); ac = acres(rings)
                            under = sum(1 for _, _, (la2, lo2, _n, _s) in chunk if any(inside(lo2, la2, rg) for rg in rings))
                            tr, why = T.tier(pn, rn, ac, None, under)
                            cand = (('SURE', 'LIKELY', 'UNLIKELY').index(tr), tr, why, rn, ac, a_.get('OBJECTID') or a_.get('objectid') or a_.get('FID'))
                            if best is None or cand < best: best = cand
                        R['pairs'][f'{r}|{u}'] = ext_row(r, k, pn, st, u, fld, best, qs, L)
                        hits += bool(best and best[1] != 'UNLIKELY')
            elif 'olyline' in gt:
                for r, k, (la, lo, pn, st) in pts:
                    j = get_json(u + '/query', {'geometry': f'{lo},{la}', 'geometryType': 'esriGeometryPoint', 'inSR': 4326, 'spatialRel': 'esriSpatialRelIntersects',
                                                'distance': 200, 'units': 'esriSRUnit_Meter', 'outFields': '*', 'returnGeometry': 'false'})
                    best = None
                    for f_ in j.get('features') or []:
                        a_ = f_.get('attributes') or {}; rn = str(a_.get(fld) or '')
                        tr, why = T.tier(pn, rn, None, None, 1)
                        cand = (('SURE', 'LIKELY', 'UNLIKELY').index(tr), tr, why + ' (a line within 200 m of the pin)', rn, None, a_.get('OBJECTID') or a_.get('objectid') or a_.get('FID'))
                        if best is None or cand < best: best = cand
                    R['pairs'][f'{r}|{u}'] = ext_row(r, k, pn, st, u, fld, best, qs, L)
                    hits += bool(best and best[1] != 'UNLIKELY')
            else:
                for r, k, _v in pts: R['pairs'][f'{r}|{u}'] = {'ref': r, 'kind': k, 'result': 'failed', 'why': f'not polygons or lines ({gt})'}
        except Exception as e:  # noqa: BLE001
            for r, k, _v in pts:
                R['pairs'].setdefault(f'{r}|{u}', {'ref': r, 'kind': k, 'result': 'failed', 'why': f'query failed: {str(e)[:70]}'})
        if u not in seen:
            queue['rows'].append({'url': u, 'title': f"{str(L.get('title') or '')[:60]} (outside research Oct 30)", 'from': 'outside research Oct 30', 'added': TODAY,
                                  'closes': sorted({r for r, _ in by[u]})[:50], 'note': f'{hits} SURE / LIKELY of {len(by[u])} assigned parks/trails'})
            seen.add(u)
        json.dump(R, open(EXT_OUT, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)   # saved as it goes (a timeout loses nothing)
    c = {}
    for v in R['pairs'].values():
        g = 'US' if v['ref'].startswith('US-') else 'Canada' if v['ref'].startswith('CA-') else 'World'
        c[(f"{g} {v['kind']}", v['result'])] = c.get((f"{g} {v['kind']}", v['result']), 0) + 1
    R['summary'] = {f'{k} {r}': x for (k, r), x in sorted(c.items())}
    R['summary']['pairs left'] = sum(1 for u in by for r, _ in by[u] if f'{r}|{u}' not in R['pairs'])
    R['summary']['new layers'] = sum(1 for l in R['layers'].values() if l.get('new_to_us'))
    R['built'] = TODAY
    json.dump(R, open(EXT_OUT, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print('::notice title=Outside research::' + '; '.join(f'{k} {v}' for k, v in R['summary'].items()))
    return R['summary']['pairs left']


def ext_row(r, k, pn, st, u, fld, best, qs, L):
    if not best: return {'ref': r, 'kind': k, 'result': 'no hit', 'why': 'the pin is not inside (or within 200 m of) any record'}
    _, tr, why, rn, ac, oid = best
    if tr != 'UNLIKELY':
        qs.append({'area': st, 'ref': r, 'park': pn, 'tier': tr, 'why': why, 'kind': 'trail' if k == 'Trail' else kind_of(str(L.get('title') or ''), '', pn), 'record': oid,
                   'record_name': rn[:120], 'acres_approx': ac, 'layer': u, 'agency': str(L.get('title') or '')[:80],
                   'record_link': f'{u}/query?objectIds={oid}&outFields=*&returnGeometry=false&f=html', 'pota_link': f'https://pota.app/#/park/{r}',
                   'question': "Is this official record that park (the agency's own boundary for it)? YES / NO", 'answer': None, 'checked_by': None, 'how': None,
                   'source': 'layer collector (outside research Oct 30)', 'st': st[3:], 'url': u, 'name_field': fld, 'licence': ''})
    return {'ref': r, 'kind': k, 'result': tr, 'why': why[:120], 'record_name': rn[:80], 'acres': ac}


def main():
    want = set(sys.argv[1:])
    log = load(LOG, {}) or {}
    D = load(QF, {}) or {}
    qs = D.get('questions') or []
    queue = load(QUEUE, {'rows': []}) or {'rows': []}
    seen = {r.get('url') for r in queue.get('rows') or []}
    n = {'new': 0, 'asked': 0, 'queued': 0, 'failed': 0, 'evidence': 0}
    for f in sorted((LINKS / '.claude' / 'build' / 'research' / 'fable').glob('*.md'), key=lambda f: (O.rank(f.stem), f.stem)):
        if want and f.stem not in want: continue
        for line in f.read_text(encoding='utf-8').splitlines():
            m = LINE.match(line.strip())
            if not m: continue
            ref, agency, url, field, note = m.group(1).upper(), m.group(2).strip(), m.group(3).strip(), m.group(4).strip(), m.group(5).strip()
            k = f'{ref}|{url}'
            if k in log: continue
            n['new'] += 1
            try: status, why, q, qrow = check(ref, agency, url, field)
            except Exception as e: status, why, q, qrow = 'failed', f'{type(e).__name__}: {str(e)[:60]}', None, None  # noqa: BLE001
            if q:
                q['area'] = f.stem; q['st'] = f.stem[3:] if f.stem[:3] in ('US-', 'CA-') else f.stem.replace('W-', '')
                q['kind'] = q.pop('kind_layer'); q['note'] = note[:200]   # chat 2's shape: ref, st, url, name_field, agency, kind, licence, answer, checked_by
                qs.append(q)
            if qrow and url not in seen:
                queue['rows'].append({'url': url, 'title': f'{agency[:60]} (LAYER line, {f.stem})', 'from': 'chat 8 LAYER line', 'added': TODAY, 'closes': [ref], 'note': note[:200]})
                seen.add(url)
            log[k] = {'ref': ref, 'area': f.stem, 'url': url, 'field': field, 'status': status, 'why': why, 'date': TODAY}
            n[status] = n.get(status, 0) + 1
    crawled = test_crawled(want, log, qs, queue, seen, n)
    if not want: external(log, qs, queue, seen, n)   # HQ Oct 30 7:45 PM: Brandon's outside research   # Oct 30 (Brandon 10:41 AM): the atlas crawler's layers are tested too, by themselves
    LOG.parent.mkdir(parents=True, exist_ok=True)
    json.dump(log, open(LOG, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    json.dump(queue, open(QUEUE, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    QF.parent.mkdir(parents=True, exist_ok=True)
    json.dump({'about': "Layers chat 8 wrote as LAYER lines in the Fable files, pin-tested by the layer collector (Rule G: pin inside, name tier, size). Chat 11 answers YES / NO; BOT A joins a YES.",
               'built': TODAY, 'open': sum(1 for q in qs if not q.get('answer')), 'questions': qs}, open(QF, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print(f"::notice title=Layer collector::{crawled} crawler layers tested; {n['new']} new LAYER lines: {n['asked']} asked (chat 11), {n['queued']} queued for the intake only, {n['evidence']} evidence, {n['failed']} failed (reason in data/intake/collector.json)")


if __name__ == '__main__':
    try: main()
    except Exception as e: print(f'::notice title=Layer collector::stopped ({type(e).__name__}: {e})')  # noqa: BLE001
    sys.exit(0)
