#!/usr/bin/env python3
"""LAYER COLLECTOR (chat 10, Oct 30 2026; HQ 8:10 AM, Brandon 8:06 AM 'automate all we can'). Part of the daily copy run.
Reads every line starting `LAYER |` in KPC-Links .claude/build/research/fable/*.md:
    LAYER | <park ref> | <agency> | <layer URL (…/MapServer/N or …/FeatureServer/N, or a download link)> | name field: <FIELD> | <note>
New lines (by ref + URL) go down the same path as the GIS hunter's hits, Rule G as written:
  REST layer -> layer opens, polygons, the name field exists -> one point query at the POTA pin: pin inside? record name + acres ->
               the name tier (T-1..T-6) -> a SURE / LIKELY hit = one question in data/waiting/questions/layer-collector.json
               (Nov 1 ruling AUTO-1C: a SURE that passes the checks is released by the nightly auto flow, 1 in 10 sampled; LIKELY and the listed exceptions = chat 11) and the layer goes to data/intake/queue.json
               (open-terms / publisher check by the intake bot);
  download   -> straight to the intake queue (the intake probes it), no question yet.
A line that fails gets a short reason in data/intake/collector.json (chat 8 reads it there); never a comment or an email.
  LINKS=links python3 kpc_layer_collector.py [AREA ...]     (AREA = only those fable files, e.g. US-DE). Never fails."""
import datetime as dt, glob, json, math, os, pathlib, re, sys, time, urllib.parse

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import kpc_tiers as T  # noqa: E402
import kpc_order as O  # noqa: E402
try:
    from kpc_manners import Manners
    M = Manners('KPC layer collector (chat 10)')
except Exception:  # noqa: BLE001
    M = None
LINKS = pathlib.Path(os.environ.get('LINKS') or '../links')
LOG = pathlib.Path('data/intake/collector.json.gz')   # Nov 2 (storage): was an 80 MB indented file rewritten every 2 h
OLDLOG = pathlib.Path('data/intake/collector.json')
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
    try: j = json.loads(body.decode('utf-8', 'replace'))
    except ValueError: raise RuntimeError('answer too big (cut off at the read limit)')   # Nov 1: 241 pairs failed on a cut-off answer; one point at a time is smaller
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


NEAR_M = 150   # R-G12 (Brandon Nov 1 12:02 AM)
NEVER_LAYER = re.compile(r'BLM_Natl_SMA|Surface_Management_Agency|/SMA/', re.I)


def external(log, qs, queue, seen, n):
    """Brandon's outside research: each (park or trail, layer) the researcher assigned, tested like a LAYER line: polygon layers =
    one multipoint query per 120 POTA pins (pin inside + name tier); line layers (trails) = the pin within 200 m of a named line.
    SURE / LIKELY -> chat 11 (data/waiting/questions/layers.json); every layer it touched -> the intake queue (publisher + licence test)."""
    D = {}
    for f in sorted(EXT_F.parent.glob('external-sources-*.json')) + sorted((EXT_F.parent / '_in' / 'layers').glob('external-sources-*.json')):   # Brandon Oct 30 7:43 PM: more workbooks coming: every external-sources-<name>.json is read
        for key, urls in (load(f, {}) or {}).items():
            if isinstance(urls, list) and '|' in key: D.setdefault(key, []).extend(u for u in urls if u not in D.get(key, []))
    if not D: return None
    P = ext_index(); KN = known_layers(); t0 = time.time()
    R = load(EXT_OUT, {'about': "Outside research (Oct 30) tested by the layer collector: per park/trail and layer, what the pin test found. 'source assigned, exact feature not verified' until here.", 'pairs': {}, 'layers': {}}) or {}
    R.setdefault('pairs', {}); R.setdefault('layers', {})
    if not R.get('retried_404'):   # Oct 31: 1,172 world pairs failed on a too-long multipoint (404): once, test them again point by point
        for k_ in [k_ for k_, v in R['pairs'].items() if v.get('result') == 'failed' and 'answer 404' in str(v.get('why'))]: del R['pairs'][k_]
        R['retried_404'] = TODAY
    if not R.get('retried_failed_nov1'):   # Brandon Nov 1 6:11 PM 'try again': once, the failures a second try can fix (host resting, a cut-off answer,
        RETRY = re.compile(r'answer rest|Expecting|delimiter|Unterminated|Invalid query|no POTA pin|answer 5\d\d|answer None|timed? ?out|Timeout', re.I)   # a refused multipoint, no pin then, a server error)
        gone = [k_ for k_, v in R['pairs'].items() if v.get('result') == 'failed' and RETRY.search(str(v.get('why')))]
        for k_ in gone: del R['pairs'][k_]
        R['retried_failed_nov1'] = f'{TODAY}: {len(gone)} failed pairs tested again'
        print(f'::notice title=Outside research::{len(gone)} failed pairs tested again (host resting / cut-off answer / refused query / no pin then)', flush=True)
    HINT = {}
    for f in sorted(EXT_F.parent.glob('world-sources-*.json')) + sorted((EXT_F.parent / '_in' / 'layers').glob('world-sources-*.json')):   # HQ Oct 31 1:05 AM: world outside research ('rest' = REST layers; 'other' = leads for chat 9)
        if 'hardlook' in f.name: continue   # Nov 1: the hard look reader (kpc_hardlook.py) asks these exact records; one question per park, not two
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
        if NEVER_LAYER.search(u):   # Nov 1 (US hard look notes): whole-state manager polygons, never a park's outline
            for r, k in todo: R['pairs'][f'{r}|{u}'] = {'ref': r, 'kind': k, 'result': 'failed', 'why': 'never matched: a whole-state surface-management layer'}
            continue
        OIDF = 'OBJECTID'
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
            OIDF = meta.get('objectIdField') or next((f_['name'] for f_ in flds if f_.get('type') == 'esriFieldTypeOID'), 'OBJECTID')   # (e) Nov 1: FID / objectid / OBJECTID_1, not always OBJECTID
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
                                                    'spatialRel': 'esriSpatialRelIntersects', 'distance': NEAR_M, 'units': 'esriSRUnit_Meter',   # R-G12 (Nov 1): records within 150 m too
                                                    'outFields': '*', 'returnGeometry': 'true', 'outSR': 4326, 'maxAllowableOffset': 0.0005, 'geometryPrecision': 5})
                        feats = j.get('features') or []
                    except RuntimeError as e:   # some servers refuse a multipoint: one point at a time
                        if not re.search(r'nvalid|rror|404|414|too long|too big|not supported', str(e)): raise   # Oct 31: a long multipoint GET answered 404 on some servers
                        feats = []
                        for _r, _k, (la1, lo1, _p, _s) in chunk:
                            feats += (get_json(u + '/query', {'geometry': f'{lo1},{la1}', 'geometryType': 'esriGeometryPoint', 'inSR': 4326, 'spatialRel': 'esriSpatialRelIntersects',
                                                              'outFields': '*', 'returnGeometry': 'true', 'outSR': 4326, 'maxAllowableOffset': 0.002}).get('features') or [])
                    for r, k, (la, lo, pn, st) in chunk:
                        best = None
                        for f_ in feats:
                            rings = (f_.get('geometry') or {}).get('rings') or []
                            ins = any(inside(lo, la, rg) for rg in rings)
                            dm = 0 if ins else ring_dist_m(lo, la, rings)
                            if dm is None or dm > NEAR_M: continue
                            a_ = f_.get('attributes') or {}; rn = str(a_.get(fld) or ''); ac = acres(rings)
                            under = sum(1 for _, _, (la2, lo2, _n, _s) in chunk if any(inside(lo2, la2, rg) for rg in rings))
                            tr, why = T.tier(pn, rn, ac, None, under)
                            if not ins:   # R-G12: a record just outside the pin is a candidate only on a name (+ kind) match, never by place alone
                                if tr == 'UNLIKELY': continue
                                why = f'{why}; R-G12: pin {dm} m outside the record (road / entrance)'
                            cand = (('SURE', 'LIKELY', 'UNLIKELY').index(tr) + (0 if ins else 0.5), tr, why, rn, ac, a_.get(OIDF) or a_.get('OBJECTID') or a_.get('objectid') or a_.get('FID'))
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


def ring_dist_m(lo, la, rings):
    kx = 111320 * math.cos(math.radians(la)); best = None
    for rg in rings:
        for i in range(1, len(rg)):
            x1, y1 = (rg[i - 1][0] - lo) * kx, (rg[i - 1][1] - la) * 110540; x2, y2 = (rg[i][0] - lo) * kx, (rg[i][1] - la) * 110540
            dx, dy = x2 - x1, y2 - y1; t = max(0, min(1, -(x1 * dx + y1 * dy) / ((dx * dx + dy * dy) or 1e-12)))
            d = math.hypot(x1 + t * dx, y1 + t * dy); best = d if best is None or d < best else best
    return None if best is None else round(best)


def ext_row(r, k, pn, st, u, fld, best, qs, L):
    if not best: return {'ref': r, 'kind': k, 'result': 'no hit', 'why': 'the pin is not inside (or within 200 m of) any record'}
    _, tr, why, rn, ac, oid = best
    if tr != 'UNLIKELY':
        qs.append({'area': st, 'ref': r, 'park': pn, 'tier': tr, 'why': why, 'kind': 'trail' if k == 'Trail' else kind_of(str(L.get('title') or ''), '', pn), 'record': oid,
                   'record_name': rn[:120], 'acres_approx': ac, 'layer': u, 'agency': str(L.get('title') or '')[:80],
                   'record_link': f'{u}/query?objectIds={oid}&outFields=*&returnGeometry=false&f=html', 'pota_link': f'https://pota.app/#/park/{r}',
                   'question': "Is this official record that park (the agency's own boundary for it)? YES / NO", 'answer': None, 'checked_by': None, 'how': None,
                   'source': 'layer collector (outside research Oct 30)', 'st': st[3:] if st[:3] in ('US-', 'CA-') else st[2:], 'url': u, 'name_field': fld, 'licence': ''})
    return {'ref': r, 'kind': k, 'result': tr, 'why': why[:120], 'record_name': rn[:80], 'acres': ac}


# ------------------------------------------------------------------------------------------------ map-format converter (HQ Oct 31 5:45 PM)
CONV = pathlib.Path(os.environ.get('CONVERT_DIR') or '../out/convert')


def _seg_m(lo, la, a, b):
    k = 111320 * math.cos(math.radians(la)); ax, ay = (a[0] - lo) * k, (a[1] - la) * 110540; bx, by = (b[0] - lo) * k, (b[1] - la) * 110540
    dx, dy = bx - ax, by - ay; L2 = dx * dx + dy * dy
    t = 0 if L2 == 0 else max(0, min(1, -(ax * dx + ay * dy) / L2))
    return math.hypot(ax + t * dx, ay + t * dy)


def converted(log, qs, n):
    """The converter's OK rows (WFS / downloads / Socrata / CKAN turned into GeoJSON near each pin, branch tools-out convert/):
    polygons holding the POTA pin, or named lines within 200 m (trails), judged by the name tiers like every LAYER line ->
    questions for chat 11 in data/waiting/questions/layers.json. Each (ref, file) once."""
    rep = CONV / 'report.csv'
    if not rep.exists(): return 0
    import csv
    P = ext_index(); done = 0
    for r in csv.DictReader(open(rep, encoding='utf-8')):
        if r.get('status') != 'OK' or not r.get('output_file'): continue
        k = f"conv|{r['ref']}|{r['url']}"
        if k in log: continue
        f = CONV / r['output_file'] if not r['output_file'].startswith('/') else pathlib.Path(r['output_file'])
        if not f.exists(): f = CONV / pathlib.Path(r['output_file']).relative_to(pathlib.Path(r['output_file']).parts[0]) if len(pathlib.Path(r['output_file']).parts) > 1 else f
        if not f.exists():
            g = list(CONV.rglob(pathlib.Path(r['output_file']).name)); f = g[0] if g else f
        if not f.exists(): log[k] = {'ref': r['ref'], 'url': r['url'], 'status': 'failed', 'why': 'converter file missing', 'date': TODAY}; continue
        pin = P.get(r['ref'])
        try: la, lo = float(r.get('pin_lat') or pin[0]), float(r.get('pin_lon') or pin[1])
        except Exception: log[k] = {'ref': r['ref'], 'url': r['url'], 'status': 'failed', 'why': 'no pin', 'date': TODAY}; continue  # noqa: BLE001
        pn = (pin or (0, 0, ''))[2] or r['ref']; st = (pin or (0, 0, '', ''))[3] if pin else r.get('area', '')
        best = None
        for ft in (load(f, {}) or {}).get('features') or []:
            g = ft.get('geometry') or {}; pr = ft.get('properties') or {}; t = g.get('type', ''); c = g.get('coordinates') or []
            rn = str(pr.get('name') or '')
            if 'Polygon' in t:
                rings = [rg for poly in (c if t == 'MultiPolygon' else [c]) for rg in poly]
                if not any(inside(lo, la, rg) for rg in rings): continue
                tr, why = T.tier(pn, rn, acres(rings), None, 1)
            elif 'LineString' in t:
                lines = c if t == 'MultiLineString' else [c]
                d = min((_seg_m(lo, la, a, b) for ln in lines for a, b in zip(ln, ln[1:])), default=9e9)
                if d > 200: continue
                tr, why = T.tier(pn, rn, None, None, 1); why += f' (a line {d:.0f} m from the pin)'
            else: continue
            cand = (('SURE', 'LIKELY', 'UNLIKELY').index(tr), tr, why, rn, pr.get('record_id'), pr.get('source_url') or r['url'], pr.get('licence') or r.get('licence', ''))
            if best is None or cand < best: best = cand
        if best and best[1] != 'UNLIKELY':
            _, tr, why, rn, oid, src, lic = best
            qs.append({'area': st, 'ref': r['ref'], 'park': pn, 'tier': tr, 'why': why, 'kind': 'park', 'record': oid, 'record_name': rn[:120], 'acres_approx': None,
                       'layer': src, 'agency': '', 'record_link': src, 'pota_link': f"https://pota.app/#/park/{r['ref']}",
                       'question': "Is this official record that park (the agency's own boundary for it)? YES / NO", 'answer': None, 'checked_by': None, 'how': None,
                       'source': 'layer collector (map-format converter)', 'st': st[3:] if st[:3] in ('US-', 'CA-') else st[2:], 'url': src,
                       'name_field': r.get('name_field', ''), 'licence': lic[:200]})
            n['asked'] = n.get('asked', 0) + 1
        log[k] = {'ref': r['ref'], 'url': r['url'], 'status': 'asked' if best and best[1] != 'UNLIKELY' else 'no match', 'why': (best[2] if best else 'no record at the pin')[:120], 'date': TODAY}
        done += 1
    print(f'::notice title=Layer collector::map-format converter: {done} files tested')
    return done


RAW = 'https://raw.githubusercontent.com/KentuckyPortableClub/KPC-Data/intake-files/'
NAMEF = re.compile(r'^(?:name|nom|nombre|naam|name_en|site_name|sitename|park_name|parkname|area_name|title|label|denominaci\w*|nom_site)$', re.I)


def area_parks(area):
    """{ref: (lat, lon, name)} of every POTA park in an area: US-XX from the state's park list, else the POTA tiles by prefix."""
    out = {}
    if area.startswith('US-'):
        for r, v in ((load(f'data/parkinfo/{area}.json', {}) or {}).get('parks') or {}).items():
            if len(v) > 6 and v[5] is not None: out[r] = (v[5], v[6], v[0])
        return out
    pre = area.split('-')[-1] + '-' if area.startswith('CA-') is False else 'CA-'
    for f in glob.glob('data/pota/t/*.json'):
        for row in load(f, []) or []:
            if isinstance(row, list) and len(row) >= 4 and str(row[0]).startswith(pre) and row[2] is not None: out[row[0]] = (row[2], row[3], row[1])
    return out


def line_dist_m(lo, la, ml):
    kx = 111320 * math.cos(math.radians(la)); best = None
    for l in ml:
        for i in range(len(l) - 1):
            ax, ay = (l[i][0] - lo) * kx, (l[i][1] - la) * 110540; bx, by = (l[i + 1][0] - lo) * kx, (l[i + 1][1] - la) * 110540
            dx, dy = bx - ax, by - ay; t = max(0, min(1, -(ax * dx + ay * dy) / ((dx * dx + dy * dy) or 1e-9)))
            d_ = math.hypot(ax + t * dx, ay + t * dy); best = d_ if best is None or d_ < best else best
    return best


def handlines(f, area, d, lines, log, qs, n):
    """A hand-downloaded TRAIL LINE file (Michigan DNR trails, Brandon Nov 1 10:15 PM): only line parks (trail / path / route ...
    in the POTA name) are tested, by NAME first (one feature per trail name): same proper name and the line within 500 m of the
    pin = SURE; within 5 km = LIKELY; a far pin (a long trail's pin can sit away from the line; MI Pere Marquette 60 km) up to
    100 km = LIKELY with the distance said (chat 11 decides); a partial name with the line within 2 km = LIKELY. Never a
    polygon park. Each (ref, file) once."""
    done = 0
    fld = next((k for k in (lines[0].get('properties') or {}) if NAMEF.match(k)), None) or next((k for k in (lines[0].get('properties') or {}) if 'name' in k.lower()), 'Name')
    for ref, (la, lo, pn) in area_parks(area).items():
        if not re.search(r'\b(trail|trails|path|pathway|byway|greenway|route|coast path|sentier|chemin)\b', str(pn or ''), re.I): continue   # trails only (a scenic river is not a trail line)
        k = f'file|{ref}|{f.name}'
        if k in log: continue
        pw = T.proper(pn); best = None
        for i, ft in enumerate(lines):
            rn = str((ft.get('properties') or {}).get(fld) or ''); rw = T.proper(rn)
            if not pw or not rw: continue
            shared, ponly, ronly = T.match(pw, rw)
            if not shared: continue
            g = ft['geometry']; ml = g['coordinates'] if g['type'] == 'MultiLineString' else [g['coordinates']]
            dm = line_dist_m(lo, la, ml)
            if dm is None: continue
            equal = not ponly
            if equal and dm <= 500: c = (0, 'SURE', f'same trail name, line {dm:.0f} m from the pin')
            elif equal and dm <= 5000: c = (1, 'LIKELY', f'same trail name, line {dm / 1000:.1f} km from the pin')
            elif equal and dm <= 100000: c = (2, 'LIKELY', f'same trail name, but the pin is {dm / 1000:.0f} km from the line (far pin: check)')
            elif dm <= 2000 and any(T.distinctive(w) for w in shared): c = (3, 'LIKELY', f'part of the name ({" ".join(sorted(shared))}), line {dm:.0f} m from the pin')
            else: continue
            c = c + (rn, i)
            if best is None or c < best: best = c
        if best:
            _, tr, why, rn, oid = best
            qs.append({'area': area, 'ref': ref, 'park': pn, 'tier': tr, 'why': why, 'kind': 'Trail', 'record': oid, 'record_name': rn[:120],
                       'acres_approx': None, 'layer': RAW + f.name, 'agency': f'hand download ({f.name})', 'record_link': RAW + f.name,
                       'pota_link': f'https://pota.app/#/park/{ref}', 'question': "Is this official trail line that park? YES / NO",
                       'answer': None, 'checked_by': None, 'how': None, 'source': 'layer collector (hand download on intake-files, lines)',
                       'st': area[3:] if area[:3] in ('US-', 'CA-') else area, 'url': RAW + f.name, 'name_field': fld, 'licence': '', 'geometry': 'line'})
            n['asked'] += 1
        log[k] = {'ref': ref, 'url': RAW + f.name, 'status': best[1] if best else 'no hit', 'why': (best[2] if best else 'no trail of that name in the file')[:120], 'date': TODAY}
        done += 1
    return done


def handfiles(log, qs, n):
    """Files a person downloaded by hand (Brandon Nov 1 6:32 PM: Vanuatu, then Spain / Ireland): on branch intake-files as
    file-<AREA>-<name>.geojson|json (WGS84), read by the intake reader (kind 'files'). Every park of AREA is tested like a LAYER
    line: polygon holding the POTA pin or within 150 m (R-G12), name tiers; SURE / LIKELY = a question in layers.json (AUTO-1C
    then releases a SURE that passes, the rest go to chat 11). The record = the feature number in the file; layer = the file's
    raw address on the branch (public). Each (ref, file) once."""
    done = 0
    for f in sorted(x for x in pathlib.Path('data/intake/_in/files').glob('file-*') if x.name.endswith(('.json', '.geojson', '.geojson.gz'))):   # zips arrive here already unpacked and in GPS degrees (intake reader)
        m = re.match(r'^file-((?:US|CA)-[A-Z]{2}|[A-Z]{2})-', f.name)
        if not m: log[f'file|{f.name}'] = {'status': 'failed', 'why': 'name must be file-<AREA>-<name> (AREA = US-KY, CA-ON or a country code)', 'date': TODAY}; continue
        area = m.group(1)
        if f.name.endswith('.gz'):
            import gzip
            try: d = json.load(gzip.open(f, 'rt', encoding='utf-8'))
            except Exception: d = {}  # noqa: BLE001
        else: d = load(f, {}) or {}
        crs = str(((d.get('crs') or {}).get('properties') or {}).get('name') or '')
        if crs and not re.search(r'4326|CRS84', crs): log[f'file|{f.name}'] = {'status': 'failed', 'why': f'not in GPS degrees ({crs}): convert first', 'date': TODAY}; continue
        feats = [ft for ft in d.get('features') or [] if 'Polygon' in str((ft.get('geometry') or {}).get('type'))]
        lines = [ft for ft in d.get('features') or [] if 'LineString' in str((ft.get('geometry') or {}).get('type'))]
        if lines and not feats: done += handlines(f, area, d, lines, log, qs, n); continue   # Nov 1 10:15 PM: Michigan DNR trails (lines)
        if not feats: log[f'file|{f.name}'] = {'status': 'failed', 'why': 'no polygons in the file', 'date': TODAY}; continue
        props = feats[0].get('properties') or {}
        fld = next((k for k in props if re.match(r'^(?:name|nom|nombre)_?en(?:g|glish)?$', k, re.I)), None) or next((k for k in props if NAMEF.match(k)), None) or next((k for k in props if 'name' in k.lower() or 'nom' in k.lower()), None)   # an English name field first (POTA names are English: Georgia's Name_ENG)
        parks = area_parks(area)
        FEAT = []   # each feature once: its rings and its box (Spain: 2,000+ areas x 2,000+ parks)
        for ft in feats:
            g = ft['geometry']; polys = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
            rings = [rg for poly in polys for rg in poly if rg]
            xs = [c[0] for rg in rings for c in rg]; ys = [c[1] for rg in rings for c in rg]
            if xs: FEAT.append((ft, rings, (min(xs), min(ys), max(xs), max(ys))))
        for ref, (la, lo, pn) in parks.items():
            k = f'file|{ref}|{f.name}'
            if k in log: continue
            best = None
            for i, (ft, rings, bb) in enumerate(FEAT):
                if not (bb[0] - .003 <= lo <= bb[2] + .003 and bb[1] - .003 <= la <= bb[3] + .003): continue   # outside the box (+ about 150-300 m): skip
                ins = any(inside(lo, la, rg) for rg in rings)
                dm = 0 if ins else ring_dist_m(lo, la, rings)
                if dm is None or dm > NEAR_M: continue
                rn = str((ft.get('properties') or {}).get(fld) or '')
                tr, why = T.tier(pn, rn, acres(rings), None, 1)
                if not ins:
                    if tr == 'UNLIKELY': continue
                    why = f'{why}; R-G12: pin {dm} m outside the record (road / entrance)'
                cand = (('SURE', 'LIKELY', 'UNLIKELY').index(tr) + (0 if ins else 0.5), tr, why, rn, acres(rings), (ft.get('properties') or {}).get('FID', ft.get('id', i)))
                if best is None or cand < best: best = cand
            if best and best[1] != 'UNLIKELY':
                _, tr, why, rn, ac, oid = best
                qs.append({'area': area, 'ref': ref, 'park': pn, 'tier': tr, 'why': why, 'kind': kind_of('', '', pn), 'record': oid, 'record_name': rn[:120],
                           'acres_approx': ac, 'layer': RAW + f.name, 'agency': f'hand download ({f.name})', 'record_link': RAW + f.name,
                           'pota_link': f'https://pota.app/#/park/{ref}', 'question': "Is this official record that park (the agency's own boundary for it)? YES / NO",
                           'answer': None, 'checked_by': None, 'how': None, 'source': 'layer collector (hand download on intake-files)',
                           'st': area[3:] if area[:3] in ('US-', 'CA-') else area, 'url': RAW + f.name, 'name_field': fld, 'licence': ''})
                n['asked'] += 1
            log[k] = {'ref': ref, 'url': RAW + f.name, 'status': best[1] if best else 'no hit', 'why': (best[2] if best else 'the pin is not inside (or within 150 m of) any record')[:120], 'date': TODAY}
            done += 1
    if done: print(f'::notice title=Layer collector::hand-downloaded files: {done} park x file pairs tested', flush=True)
    return done


def main():
    want = set(sys.argv[1:])
    import gzip
    try: log = json.load(gzip.open(LOG, 'rt', encoding='utf-8'))
    except Exception: log = load(OLDLOG, {}) or {}  # noqa: BLE001
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
    if not want: external(log, qs, queue, seen, n)   # HQ Oct 30 7:45 PM: Brandon's outside research
    if not want: handfiles(log, qs, n)   # Nov 1 6:32 PM: files a person downloaded by hand (intake-files file-<AREA>-*.geojson)
    if not want: converted(log, qs, n)   # HQ Oct 31 5:45 PM: the map-format converter's OK rows   # Oct 30 (Brandon 10:41 AM): the atlas crawler's layers are tested too, by themselves
    LOG.parent.mkdir(parents=True, exist_ok=True)
    LOG.write_bytes(gzip.compress(json.dumps(log, ensure_ascii=False, separators=(',', ':'), sort_keys=True).encode('utf-8'), 6, mtime=0))
    OLDLOG.unlink(missing_ok=True)
    json.dump(queue, open(QUEUE, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    QF.parent.mkdir(parents=True, exist_ok=True)
    json.dump({'about': "Layers chat 8 wrote as LAYER lines in the Fable files, pin-tested by the layer collector (Rule G: pin inside, name tier, size). Chat 11 answers YES / NO; BOT A joins a YES.",
               'built': TODAY, 'open': sum(1 for q in qs if not q.get('answer')), 'questions': qs}, open(QF, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print(f"::notice title=Layer collector::{crawled} crawler layers tested; {n['new']} new LAYER lines: {n['asked']} asked (chat 11), {n['queued']} queued for the intake only, {n['evidence']} evidence, {n['failed']} failed (reason in data/intake/collector.json)")


if __name__ == '__main__':
    try: main()
    except Exception as e: print(f'::notice title=Layer collector::stopped ({type(e).__name__}: {e})')  # noqa: BLE001
    sys.exit(0)
