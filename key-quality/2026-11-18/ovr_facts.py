"""Fact sheet for every hand-checked answer in overrides.json (KPC owner 2026-11-18: those answers are not his and not
trusted; Sonnet checks them). Per join / no: the record's name, size, owner, whether the POTA pin is inside it, how far
off, whether the names agree, the official acreage when known. Class GOOD = names agree and pin inside or within 1 km;
else CHECK. A 'no' is SUSPECT when names agree and the pin is inside (it may block the right record)."""
import csv, glob, gzip, json, math, os, re, sys
L = '/home/claude/kpc-links'; D = '/home/claude/kpc-data'; C = '/home/claude/sc/cache'
sys.path.insert(0, L + '/.github/scripts')
import kpc_key_rules as KR, kpc_overrides as KO, pathlib

ovr = KO.load(pathlib.Path(L + '/data/us-key/overrides.json'))['parks']
pins, web = {}, {}
for f in glob.glob(D + '/data/parkinfo/*.json'):
    for ref, r in (json.load(open(f)).get('parks') or {}).items():
        if ref in ovr and len(r) > 6 and r[5] is not None: pins[ref] = (r[0], r[5], r[6]); web[ref] = r[1]
area_of = {}
for f in glob.glob(L + '/data/us-key/US-*.json'):
    try: k = json.load(open(f))
    except Exception: continue
    a = os.path.basename(f)[:-5]
    for ref in (k.get('parks') or k if isinstance(k, dict) else {}):
        if isinstance(ref, str) and '-' in ref: area_of.setdefault(ref, a)
off = {}
for f in glob.glob(D + '/data/truth/US-*.json'):
    for ref, p in (json.load(open(f)).get('parks') or {}).items():
        o = p.get('official')
        if isinstance(o, dict): o = o.get('acres')
        if o: off[ref] = o
recs = {}
def load(a):
    if a in recs: return recs[a]
    f = f'{C}/{a}.json.gz'; m = {}
    if os.path.exists(f):
        for r in json.load(gzip.open(f))['recs']:
            m[str(r.get('OBJECTID'))] = r; m.setdefault('name:' + str(r.get('Unit_Nm') or '').lower(), r)
    recs[a] = m; return m
def rings(g):
    if isinstance(g, list) and g and isinstance(g[0], (int, float)): return []
    if isinstance(g, list) and g and isinstance(g[0], list) and g[0] and isinstance(g[0][0], (int, float)): return [g]
    out = []
    for x in g or []: out += rings(x)
    return out
def inside(lat, lon, rr):
    c = False
    for ring in rr:
        n = len(ring)
        for i in range(n):
            x1, y1 = ring[i][:2]; x2, y2 = ring[i - 1][:2]
            if (y1 > lat) != (y2 > lat) and lon < (x2 - x1) * (lat - y1) / ((y2 - y1) or 1e-12) + x1: c = not c
    return c
def km(lat, lon, rr):
    best = 1e9
    for ring in rr:
        for p in ring[::max(1, len(ring) // 400)]:
            dx = (p[0] - lon) * 111.3 * math.cos(math.radians(lat)); dy = (p[1] - lat) * 111.3
            best = min(best, math.hypot(dx, dy))
    return best
TW = '|'.join(rx for _k, rx in KR.TYPE_WORDS)
def core(n): return set(KR._full(re.sub(TW, ' ', str(n or '').lower())).split()) - {'the', 'of', 'and', 'at', 'on'}
def agree(a, b):
    x, y = core(a), core(b)
    return bool(x and y and (x <= y or y <= x))

out = []
for ref, v in sorted(ovr.items()):
    pin = pins.get(ref); pname = pin[0] if pin else ''
    st = area_of.get(ref) or ''
    cands = [st] if st else []
    for kind in ('join', 'no'):
        for rid in v.get(kind) or []:
            r = None
            for a in cands or []:
                m = load(a); r = m.get(str(rid)) or m.get('name:' + str(rid).lower())
                if r: break
            fp = (v.get('fp') or {}).get(str(rid))
            rn = (r or {}).get('Unit_Nm') or (fp[0] if fp else (str(rid) if not re.fullmatch(r'[a-z]*\d+', str(rid)) else ''))
            ac = (r or {}).get('GIS_Acres') or (fp[1] if fp else '')
            ins = dk = ''
            if r and pin:
                rr = rings(r.get('_r')); ins = inside(pin[1], pin[2], rr) if rr else ''
                dk = 0 if ins else (round(km(pin[1], pin[2], rr), 2) if rr else '')
            ag = agree(pname, rn) if rn else ''
            o = off.get(ref, '')
            if kind == 'join':
                cls = 'GOOD' if ag and (ins is True or (dk != '' and dk <= 1)) else 'CHECK'
            else:
                cls = 'SUSPECT' if ag and ins is True else 'OK'
            out.append({'class': cls, 'kind': kind, 'ref': ref, 'area': st, 'pota_name': pname, 'record_id': rid, 'record_name': rn,
                        'record_acres': round(float(ac)) if ac not in ('', None) else '', 'official_acres': o,
                        'owner': (r or {}).get('Mang_Name') or '', 'pin_inside': ins, 'km_off': dk, 'names_agree': ag,
                        'found_in_cache': bool(r), 'park_web': web.get(ref, ''), 'why_saved': (v.get('why') or '')[:120]})
w = csv.DictWriter(open('/home/claude/sc/ovr-facts.csv', 'w', newline=''), list(out[0]))
w.writeheader(); w.writerows(out)
import collections
print(collections.Counter((x['kind'], x['class']) for x in out), collections.Counter(x['found_in_cache'] for x in out))
