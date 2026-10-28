#!/usr/bin/env python3
"""ONE-OFF PROBE (chat 2, Oct 28 2026): find the official Hart County PVA parcel owned by the Commonwealth of Kentucky at the
Boiling Springs unit of Green River State Natural Area (US-12752), Brandon's point 37.2953451, -85.8320279 (Green River between
KY 2185 and KY 88 near Boyd Knob). Writes data/probe/hart-pva.json (+ screenshots). Never raises."""
import json, os, re, sys, time, traceback
import requests

LAT, LON = 37.2953451, -85.8320279
OUT = 'data/probe'; os.makedirs(OUT, exist_ok=True)
R = {'when': time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime()), 'point': [LAT, LON], 'steps': {}}
UA = 'KPC-probe/1.0 (Kentucky Portable Club; ham radio club map check; brandonwhite42166@gmail.com)'
H = {'User-Agent': UA}

def note(s): print(f'::notice title=hart-pva::{s[:3900]}')
def save():
    with open(f'{OUT}/hart-pva.json', 'w') as f: json.dump(R, f, indent=1)

def step(name, fn):
    t = time.time()
    try: R['steps'][name] = fn()
    except Exception as e:  # noqa: BLE001
        R['steps'][name] = {'error': repr(e)[:500], 'trace': traceback.format_exc()[-1500:]}
    R['steps'][name + '_s'] = round(time.time() - t, 1); save()

def arc_point(url, layer=0, fields='*'):
    """Point-in-polygon query on an ArcGIS layer; returns the answer dict (features w/ attributes + geometry)."""
    q = {'geometry': f'{LON},{LAT}', 'geometryType': 'esriGeometryPoint', 'inSR': 4326, 'spatialRel': 'esriSpatialRelIntersects',
         'outFields': fields, 'returnGeometry': 'true', 'outSR': 4326, 'f': 'json'}
    r = requests.get(f'{url.rstrip("/")}/{layer}/query', params=q, headers=H, timeout=90)
    return r.json()

def arc_near(url, layer=0, km=3):
    d = km / 111.0
    q = {'geometry': json.dumps({'xmin': LON - d, 'ymin': LAT - d, 'xmax': LON + d, 'ymax': LAT + d, 'spatialReference': {'wkid': 4326}}),
         'geometryType': 'esriGeometryEnvelope', 'inSR': 4326, 'spatialRel': 'esriSpatialRelIntersects', 'outFields': '*',
         'returnGeometry': 'false', 'f': 'json', 'resultRecordCount': 500}
    r = requests.get(f'{url.rstrip("/")}/{layer}/query', params=q, headers=H, timeout=120)
    return r.json()

# ---- 1. the state server: any parcel service at all? (earlier probe: only Webster)
def s1():
    out = {}
    for folder in ['WGS84WM_Services', 'KYPVAMAPPING', 'Cadastral', '']:
        try:
            r = requests.get(f'https://kygisserver.ky.gov/arcgis/rest/services/{folder}?f=json', headers=H, timeout=60); d = r.json()
            names = [s['name'] for s in d.get('services', [])] + d.get('folders', [])
            out[folder or 'root'] = [n for n in names if re.search(r'arcel|PVA|adast', n, re.I)] or names[:60]
        except Exception as e: out[folder or 'root'] = repr(e)[:200]  # noqa: BLE001
    # every parcel service found: ask the point
    hits = {}
    for folder, names in out.items():
        if not isinstance(names, list): continue
        for n in names:
            if not re.search(r'arcel|PVA', n, re.I): continue
            for kind in ('MapServer', 'FeatureServer'):
                u = f'https://kygisserver.ky.gov/arcgis/rest/services/{n}/{kind}'
                try:
                    a = arc_point(u)
                    if a.get('features'): hits[u] = a['features'][:5]
                    elif 'error' not in a: hits[u] = 'no feature at the point'
                except Exception as e: hits[u] = repr(e)[:150]  # noqa: BLE001
    return {'services': out, 'point_hits': hits}
step('ky_server', s1)

# ---- 2. ArcGIS Online: anything for Hart County parcels / Kentucky statewide parcels
def s2():
    out = {}
    for q in ['Hart County Kentucky parcels', 'Kentucky statewide parcels PVA', 'Hart County KY PVA', 'Kentucky parcel boundaries']:
        r = requests.get('https://www.arcgis.com/sharing/rest/search', params={'q': q + ' type:("Feature Service" OR "Map Service")', 'f': 'json', 'num': 25}, headers=H, timeout=60)
        out[q] = [{'title': i.get('title'), 'owner': i.get('owner'), 'url': i.get('url'), 'id': i.get('id'), 'access': i.get('access')} for i in r.json().get('results', [])]
    # try every url that looks like a parcel service: point query layer 0..3
    hits = {}
    seen = set()
    for lst in out.values():
        for i in lst:
            u = i.get('url') or ''
            if not u or u in seen or not re.search(r'arcel|PVA|adast', (i.get('title') or '') + u, re.I): continue
            seen.add(u)
            try:
                meta = requests.get(u, params={'f': 'json'}, headers=H, timeout=60).json()
                layers = [l['id'] for l in meta.get('layers', [])][:6] or [0]
                for L in layers:
                    a = arc_point(u, L)
                    if a.get('features'): hits[f'{u}/{L}'] = a['features'][:5]; break
            except Exception as e: hits[u] = repr(e)[:150]  # noqa: BLE001
    return {'search': out, 'point_hits': hits}
step('agol', s2)

# ---- 3. qPublic (Schneider) Hart County, KY PVA: a browser, capture the map's data services + search the owner
def s3():
    from playwright.sync_api import sync_playwright
    base = 'https://qpublic.schneidercorp.com/Application.aspx?App=HartCountyKY'
    out = {'requests': [], 'json_hits': [], 'inputs': [], 'owner_results': [], 'reports': [], 'text': {}}
    cap = {}
    def on_resp(resp):
        try:
            u = resp.url
            if 'schneidercorp' in u and re.search(r'\.(png|jpg|gif|css|js|woff2?|svg|ico)(\?|$)', u): return
            key = re.sub(r'([?&])[^&]*', '', u)[:200]
            if key not in cap: cap[key] = 0
            cap[key] += 1
            if cap[key] <= 3: out['requests'].append(u[:600])
            ct = resp.headers.get('content-type', '')
            if ('json' in ct or 'javascript' in ct) and resp.status == 200:
                b = resp.body()
                if len(b) < 3_000_000:
                    t = b.decode('utf-8', 'ignore')
                    if re.search(r'COMMONWEALTH|"rings"|"coordinates"|MapServer|FeatureServer', t):
                        out['json_hits'].append({'url': u[:600], 'len': len(t), 'head': t[:1500]})
        except Exception: pass  # noqa: BLE001
    with sync_playwright() as p:
        b = p.chromium.launch(); ctx = b.new_context(user_agent=UA, viewport={'width': 1400, 'height': 1000}); pg = ctx.new_page()
        pg.on('response', on_resp)
        pg.goto(base + '&PageType=Search', timeout=90000, wait_until='domcontentloaded'); pg.wait_for_timeout(4000)
        # disclaimer
        for sel in ['text=Agree', 'text=I Agree', 'text=Accept', 'button:has-text("Agree")', 'a:has-text("Agree")']:
            try:
                if pg.locator(sel).first.is_visible(timeout=1500): pg.locator(sel).first.click(); pg.wait_for_timeout(3000); out['agreed'] = sel; break
            except Exception: pass  # noqa: BLE001
        pg.screenshot(path=f'{OUT}/hart-search.png', full_page=False)
        out['text']['search'] = pg.inner_text('body')[:4000]
        for el in pg.locator('input').all()[:60]:
            try: out['inputs'].append({k: el.get_attribute(k) for k in ('id', 'name', 'placeholder', 'type', 'aria-label')})
            except Exception: pass  # noqa: BLE001
        # owner search: the input whose id/name/placeholder/label says owner / name
        tgt = None
        for el in pg.locator('input[type=text], input:not([type])').all():
            try:
                a = ' '.join(str(el.get_attribute(k) or '') for k in ('id', 'name', 'placeholder', 'aria-label'))
                if re.search(r'owner|name', a, re.I) and not re.search(r'street|road|parcel|address|subdiv', a, re.I): tgt = el; out['owner_input'] = a; break
            except Exception: pass  # noqa: BLE001
        if tgt is None:
            try:
                lab = pg.get_by_text(re.compile(r'Owner', re.I)).first; lab.scroll_into_view_if_needed(); tgt = pg.locator('input[type=text]').nth(1); out['owner_input'] = 'guess nth(1)'
            except Exception: pass  # noqa: BLE001
        if tgt is not None:
            tgt.fill('COMMONWEALTH OF KENTUCKY'); tgt.press('Enter'); pg.wait_for_timeout(6000)
            pg.screenshot(path=f'{OUT}/hart-owner.png', full_page=True)
            out['text']['owner'] = pg.inner_text('body')[:12000]
            links = []
            for a in pg.locator('a[href*="KeyValue="]').all()[:200]:
                try: links.append({'href': a.get_attribute('href'), 'text': (a.inner_text() or '').strip()[:80]})
                except Exception: pass  # noqa: BLE001
            out['owner_results'] = links
            # rows of the result table
            try:
                rows = pg.locator('table tr').all()
                out['owner_rows'] = [r.inner_text().replace('\n', ' | ')[:300] for r in rows[:150]]
            except Exception: pass  # noqa: BLE001
            # open up to 40 reports (owner, address, acres, legal) + the map page for the data services
            keys = []
            for l in links:
                m = re.search(r'KeyValue=([^&]+)', l['href'] or '')
                if m and m.group(1) not in keys: keys.append(m.group(1))
            out['keys'] = keys
            for k in keys[:40]:
                try:
                    pg.goto(f'{base}&PageType=Report&KeyValue={k}', timeout=60000, wait_until='domcontentloaded'); pg.wait_for_timeout(2500)
                    t = pg.inner_text('body')
                    rep = {'key': k, 'text': t[:5000]}
                    for fld in ('Owner', 'Acres', 'Legal', 'Location', 'Address', 'Deed', 'Class', 'District'):
                        m = re.search(fld + r'[^\n]*\n([^\n]{0,160})', t)
                        if m: rep[fld.lower()] = m.group(1).strip()
                    out['reports'].append(rep)
                except Exception as e: out['reports'].append({'key': k, 'error': repr(e)[:150]})  # noqa: BLE001
            # the map page once: what services does it call?
            if keys:
                try:
                    pg.goto(f'{base}&PageType=Map&KeyValue={keys[0]}', timeout=90000, wait_until='domcontentloaded'); pg.wait_for_timeout(12000)
                    pg.screenshot(path=f'{OUT}/hart-map.png', full_page=False)
                    out['text']['map'] = pg.inner_text('body')[:2000]
                except Exception as e: out['map_error'] = repr(e)[:200]  # noqa: BLE001
        b.close()
    # any ArcGIS service seen in the traffic: ask it for the point
    svcs = set()
    for u in out['requests'] + [h['url'] for h in out['json_hits']]:
        m = re.search(r'(https?://[^"\s]+?/(?:MapServer|FeatureServer))', u)
        if m: svcs.add(m.group(1))
    for h in out['json_hits']:
        for m in re.finditer(r'(https?://[^"\s\\]+?/(?:MapServer|FeatureServer))', h['head']): svcs.add(m.group(1))
    hits = {}
    for u in sorted(svcs):
        try:
            meta = requests.get(u, params={'f': 'json'}, headers=H, timeout=60).json()
            layers = [l['id'] for l in meta.get('layers', [])][:12] or [0]
            for L in layers:
                a = arc_point(u, L)
                if a.get('features'): hits[f'{u}/{L}'] = a['features'][:5]
        except Exception as e: hits[u] = repr(e)[:150]  # noqa: BLE001
    out['services'] = sorted(svcs); out['point_hits'] = hits
    return out
step('qpublic', s3)

# ---- 4. the short answer for the annotations
try:
    found = []
    for k in ('ky_server', 'agol', 'qpublic'):
        s = R['steps'].get(k) or {}
        for u, f in (s.get('point_hits') or {}).items():
            if isinstance(f, list): found.append(f'{u}: {json.dumps(f[0].get("attributes", {}))[:400]}')
    q = R['steps'].get('qpublic') or {}
    note(f'parcel at the point: {found[:3] if found else "NONE"} · qPublic owner rows: {len(q.get("owner_results") or [])} · services seen: {q.get("services")} · err: {q.get("error")}')
except Exception as e: note('summary failed ' + repr(e))  # noqa: BLE001
save()
