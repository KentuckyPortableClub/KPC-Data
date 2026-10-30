#!/usr/bin/env python3
"""TWO GIS FINDERS (chat 10, Oct 30 2026; Brandon 10:44 AM 'All 3'). Leads only: they FIND official layers; the layer collector
pin-tests every one against the area's open parks (name tiers T-1..T-6) and chat 11 says YES. Nothing goes on a map from here.

  viewers  Every ArcGIS map viewer link we already keep (documents bot maps, parkinfo-web, the Fable + atlas notes): the viewer's
           item data (webmap / web app / Experience) lists the real layers behind it -> each polygon-able FeatureServer / MapServer
           layer URL. ArcGIS REST + sharing/rest only (manners exempt path), each item read ONCE.
  portals  Every open-data portal we know (state-gis.json 'portals', the atlas '## Open-data portal' lines, chat 8's world agency
           table 'portals'): searched for park / protected-area / wildlife / forest datasets through the portal's own search API
           (ArcGIS Hub v3, CKAN package_search, Socrata catalog) -> datasets that point at a FeatureServer / MapServer layer.
           Each portal re-searched after 7 days.
Output: data/intake/found-layers.json {url: {area, name, from, source, date}} (the collector reads it), finders-seen.json.
  python3 kpc_gis_finders.py viewers portals        env LINKS (KPC-Links checkout). Never fails."""
import datetime as dt, glob, json, os, pathlib, re, sys, time, urllib.parse

sys.path.insert(0, str(pathlib.Path(__file__).parent))
try:
    from kpc_manners import Manners
    M = Manners('KPC GIS finders (chat 10)')
except Exception:  # noqa: BLE001
    M = None
LINKS = pathlib.Path(os.environ.get('LINKS') or '../links')
OUT, SEEN = pathlib.Path('data/intake/found-layers.json'), pathlib.Path('data/intake/finders-seen.json')
TODAY = dt.date.today()
ITEM_RX = re.compile(r'experience\.arcgis\.com/experience/([0-9a-f]{32})|[?&#](?:appid|webmap|id|itemId)=([0-9a-f]{32})|/(?:apps|home)/[^?#\s]*?[/=]([0-9a-f]{32})', re.I)
SVC_RX = re.compile(r'^(https?://\S+?/(?:FeatureServer|MapServer))(?:/(\d+))?/?$', re.I)
PARKW = re.compile(r'park|parc|boundar|recreation|wildlife|faune|forest|forêt|lands?\b|refuge|reserve|réserve|preserve|natural area|'
                   r'wma|management area|conservation|protected|sanctuary|historic|monument|hatchery|game|natur|schutz|parque|area protegida|'
                   r'riserva|parco|rezerwat|naturreservat|nationalpark', re.I)
QUERIES = ['park boundaries', 'parks', 'protected areas', 'wildlife management areas', 'state forest', 'conservation lands', 'nature reserve']
CAP_VIEWERS, CAP_PORTALS = 60, 20
T0, LIMIT = time.time(), float(os.environ.get('MINUTES') or 40) * 60


def notice(m): print('::notice title=GIS finders::' + str(m)[:900], flush=True)
def late(): return time.time() - T0 > LIMIT


def load(p, d=None):
    try: return json.load(open(p, encoding='utf-8'))
    except Exception: return d  # noqa: BLE001


def get_json(u, params=None):
    if not M: return None
    q = u + (('&' if '?' in u else '?') + urllib.parse.urlencode(params) if params else '')
    try:
        st, hd, body, final = M.get(q, accept='application/json')
        return json.loads(body.decode('utf-8', 'replace')) if isinstance(st, int) and st < 400 and body else None
    except Exception: return None  # noqa: BLE001


def add(found, url, area, name, frm, source):
    m = SVC_RX.match(url.strip())
    if not m: return 0
    base, lay = m.group(1), m.group(2)
    urls = [f'{base}/{lay}'] if lay is not None else []
    if lay is None:   # a whole service: list its polygon-looking layers
        j = get_json(base, {'f': 'json'}) or {}
        urls = [f"{base}/{l['id']}" for l in j.get('layers') or [] if not l.get('subLayerIds') and (PARKW.search(str(l.get('name', ''))) or PARKW.search(base))][:15]
    n = 0
    for u in urls:
        if u not in found:
            found[u] = {'area': area, 'name': name[:100], 'from': frm, 'source': source[:200], 'date': TODAY.isoformat()}; n += 1
    return n


# ------------------------------------------------------------------------------------------------ viewers
def viewer_links():
    """(area, item id, where) for every ArcGIS viewer link we keep."""
    out = {}
    for f in glob.glob('data/docs/US-*.json'):
        area = pathlib.Path(f).stem
        for r, v in ((load(f, {}) or {}).get('parks') or {}).items():
            for m in [v.get('map') or {}] + list(v.get('map_also') or []):
                u = str((m or {}).get('url') or '')
                for g in ITEM_RX.finditer(u):
                    out.setdefault(next(x for x in g.groups() if x), (area, f'documents bot {r}'))
    w = (load('data/parkinfo-web.json', {}) or {}).get('parks') or {}
    for r, v in w.items():
        for key in ('map', 'web', 'agency_page', 'map_page'):
            for g in ITEM_RX.finditer(str(v.get(key) or '')):
                area = ('US-' if r.startswith('US-') else 'CA-' if r.startswith('CA-') else 'W-') + '?'
                out.setdefault(next(x for x in g.groups() if x), (area, f'parkinfo-web {r}'))
    for d in ('fable', 'agency-atlas'):
        for f in glob.glob(str(LINKS / '.claude' / 'build' / 'research' / d / '*.md')):
            for g in ITEM_RX.finditer(open(f, encoding='utf-8').read()):
                out.setdefault(next(x for x in g.groups() if x), (pathlib.Path(f).stem, f'{d} notes'))
    return out


def webmap_layers(item, depth=0):
    """Layer URLs behind an AGOL item (webmap, web app, Experience, dashboard): the item's data JSON, followed one level."""
    data = get_json(f'https://www.arcgis.com/sharing/rest/content/items/{item}/data', {'f': 'json'}) or {}
    urls, nxt = set(), set()
    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k == 'url' and isinstance(v, str) and SVC_RX.match(v): urls.add(v)
                elif k in ('itemId', 'webmap', 'map') and isinstance(v, str) and re.fullmatch(r'[0-9a-f]{32}', v): nxt.add(v)
                else: walk(v)
        elif isinstance(o, list):
            for v in o: walk(v)
    walk(data)
    if depth < 1:
        for i in list(nxt)[:5]: urls |= webmap_layers(i, depth + 1)
    return urls


def viewers(found, seen):
    links = viewer_links(); n_items = n_layers = 0
    for item, (area, where) in links.items():
        if late() or n_items >= CAP_VIEWERS: break
        if f'item:{item}' in seen: continue
        n_items += 1
        meta = get_json(f'https://www.arcgis.com/sharing/rest/content/items/{item}', {'f': 'json'}) or {}
        for u in sorted(webmap_layers(item))[:40]:
            n_layers += add(found, u, area, meta.get('title') or 'map viewer layer', 'map viewer', f"{where}; item {item} ({meta.get('owner', '')})")
        seen[f'item:{item}'] = TODAY.isoformat()
    notice(f'viewers: {len(links)} viewer items known, {n_items} read now, {n_layers} new layers')


# ------------------------------------------------------------------------------------------------ portals
def portal_list():
    out = []
    for st, ps in ((load('data/state-gis.json', {}) or {}).get('portals') or {}).items():
        for p in ps or []:
            if isinstance(p, list) and len(p) > 1: out.append((f'US-{st}' if len(st) == 2 else st, p[1]))
    for f in glob.glob(str(LINKS / '.claude' / 'build' / 'research' / 'agency-atlas' / '*.md')):
        t = open(f, encoding='utf-8').read()
        m = re.search(r'## Open-data portal\n(.*?)(?=\n## |\Z)', t, re.S)
        for u in re.findall(r'https?://[^\s)|<>]+', m.group(1) if m else ''): out.append((pathlib.Path(f).stem, u.rstrip('.,;')))
    T = (load(LINKS / '.claude' / 'build' / 'research' / 'WORLD' / 'world_agencies.json', {}) or {})
    for cc, v in ((T.get('countries') or T) or {}).items():
        for u in (v.get('portals') or []) if isinstance(v, dict) else []:
            if isinstance(u, str) and u.startswith('http'): out.append((f'W-{cc}', u))
    return list(dict.fromkeys(out))


def search_portal(root):
    """-> [(title, service url)] via the portal's own search API (Hub v3, CKAN, Socrata), whichever answers."""
    root = root.rstrip('/'); base = re.match(r'https?://[^/]+', root).group(0)
    res = []
    for q in QUERIES[:4]:
        j = get_json(f'{base}/api/v3/datasets', {'q': q, 'page[size]': 50})   # ArcGIS Hub
        for d in (j or {}).get('data') or []:
            a = d.get('attributes') or {}
            if a.get('url') and SVC_RX.match(str(a['url'])): res.append((a.get('name') or a.get('title') or '', a['url']))
        if j: continue
        j = get_json(f'{base}/api/3/action/package_search', {'q': q, 'rows': 50})   # CKAN
        for p in ((j or {}).get('result') or {}).get('results') or []:
            for r in p.get('resources') or []:
                if SVC_RX.match(str(r.get('url') or '')): res.append((p.get('title') or '', r['url']))
        if j: continue
        j = get_json(f'{base}/api/catalog/v1', {'q': q, 'limit': 50})   # Socrata (rarely ArcGIS; kept for the link it may give)
        for r in (j or {}).get('results') or []:
            u = ((r.get('resource') or {}).get('distribution') or [{}])[0].get('downloadURL', '') if isinstance(r, dict) else ''
            if SVC_RX.match(str(u)): res.append((((r.get('resource') or {}).get('name')) or '', u))
    return res


def portals(found, seen):
    n_p = n_l = 0
    for area, root in portal_list():
        if late() or n_p >= CAP_PORTALS: break
        k = f'portal:{root}'
        try:
            if seen.get(k) and (TODAY - dt.date.fromisoformat(seen[k])).days < 7: continue
        except ValueError: pass
        n_p += 1
        for title, u in search_portal(root)[:60]:
            if PARKW.search(title) or PARKW.search(u): n_l += add(found, u, area, title or 'portal dataset', 'open-data portal', root)
        seen[k] = TODAY.isoformat()
    notice(f'portals: {n_p} searched now, {n_l} new layers')


if __name__ == '__main__':
    found, seen = load(OUT, {}) or {}, load(SEEN, {}) or {}
    for mode in sys.argv[1:] or ['viewers', 'portals']:
        try: {'viewers': viewers, 'portals': portals}[mode](found, seen)
        except Exception as e: notice(f'{mode} stopped ({type(e).__name__}: {e})')  # noqa: BLE001
    OUT.parent.mkdir(parents=True, exist_ok=True)
    json.dump(found, open(OUT, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    json.dump(seen, open(SEEN, 'w', encoding='utf-8'), indent=1)
    sys.exit(0)
