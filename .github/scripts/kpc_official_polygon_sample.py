#!/usr/bin/env python3
"""Small sample of Brandon's Nov 4 official-polygon IDEA for pile parks.
Quote provenance: mystery-parks/returned-nov4/IDEA-official-polygon-rule.md
Unique name match within ~15 km -> ledger join proposal (proposed_by=pile-solver).
Ambiguous/multiple -> listed. Misses counted. Robots.txt obeyed; no ArcGIS exemption;
no keyed APIs; responses cached. Nov 6 Part B — lean sample only (dozens)."""
import csv, hashlib, json, math, os, pathlib, re, sys, time, urllib.parse

ROOT = pathlib.Path(os.environ.get('DATA') or '.')
LINKS = pathlib.Path(os.environ.get('LINKS') or '../links')
OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'data/agreement-ledger/polygon-sample'
CACHE = OUT / 'cache'
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import kpc_manners as KM
import kpc_agreement_ledger as AL

os.environ['KPC_ARCGIS_ROBOTS_EXEMPT'] = '0'
UA_JOB = 'KPC-Mapping-agent (Kentucky Portable Club; read-only)'
FIFTEEN_KM = 15.0

# Lean official endpoints (name fields from Brandon's IDEA note)
SERVICES = [
    # (id, kind, url, name_field, id_field, where_template, covers)
    ('eea-cdda', 'arcgis',
     'https://bio.discomap.eea.europa.eu/arcgis/rest/services/ProtectedSites/CDDA_Dyna_WM/MapServer/4',
     'siteName', 'nationalId', "UPPER(siteName) LIKE '%{q}%'", 'EEA CDDA'),
    ('eea-n2k', 'arcgis',
     'https://bio.discomap.eea.europa.eu/arcgis/rest/services/ProtectedSites/Natura2000Sites/MapServer/2',
     'SITENAME', 'SITECODE', "UPPER(SITENAME) LIKE '%{q}%'", 'EEA Natura 2000'),
    ('padus', 'arcgis',
     'https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0',
     'Unit_Nm', 'OBJECTID', "UPPER(Unit_Nm) LIKE '%{q}%'", 'US PAD-US'),
    ('cpcad', 'arcgis',
     'https://maps-cartes.ec.gc.ca/arcgis/rest/services/CWS_SCF/CPCAD/MapServer/0',
     'NAME_E', 'OBJECTID', "UPPER(NAME_E) LIKE '%{q}%'", 'CA CPCAD'),
]

IDEA_QUOTE = (
    'Pattern seen: POTA pins are nearly always on the right land but 2-15 km outside the official line. '
    'Brandon still has to rule on that band. Suggestion: 0-15 km is a join with a flag, and over 15 km '
    'goes to a person as a possible wrong pin.'
)
PROVENANCE = 'mystery-parks/returned-nov4/IDEA-official-polygon-rule.md (Brandon outside agent, Nov 4 2026)'


def haversine_m(lat1, lon1, lat2, lon2):
    R = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def point_in_ring(lon, lat, ring):
    """Ray casting; ring = [[lon,lat], ...]"""
    n = len(ring)
    if n < 4: return False
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = ring[i][0], ring[i][1]
        xj, yj = ring[j][0], ring[j][1]
        if ((yi > lat) != (yj > lat)) and (lon < (xj - xi) * (lat - yi) / (yj - yi + 1e-15) + xi):
            inside = not inside
        j = i
    return inside


def dist_to_boundary_m(lat, lon, rings):
    """0 if inside any ring; else min distance to any vertex (lean proxy for boundary distance)."""
    if not rings: return None
    if any(point_in_ring(lon, lat, r) for r in rings if len(r) >= 4):
        return 0.0
    best = None
    for r in rings:
        for p in r[:: max(1, len(r) // 40)]:  # subsample
            d = haversine_m(lat, lon, p[1], p[0])
            best = d if best is None else min(best, d)
    return best


def cache_get(key):
    CACHE.mkdir(parents=True, exist_ok=True)
    p = CACHE / (hashlib.sha256(key.encode()).hexdigest()[:24] + '.json')
    if p.exists():
        return json.load(open(p)), True
    return None, False


def cache_put(key, obj):
    CACHE.mkdir(parents=True, exist_ok=True)
    p = CACHE / (hashlib.sha256(key.encode()).hexdigest()[:24] + '.json')
    json.dump(obj, open(p, 'w'), ensure_ascii=False)
    return p


def query_name(M, svc, q, log):
    sid, kind, url, nfield, idfield, where_t, label = svc
    where = where_t.format(q=re.sub(r"[^A-Z0-9 ]", " ", q.upper())[:40].replace("'", "''"))
    key = f'{sid}|{where}'
    hit, cached = cache_get(key)
    if cached:
        log.append(f'cache hit {sid} q={q!r}'); return hit, True
    params = {'where': where, 'outFields': f'{nfield},{idfield}', 'returnGeometry': 'true',
              'outSR': '4326', 'f': 'json', 'resultRecordCount': '8', 'maxAllowableOffset': '0.001'}
    full = url.rstrip('/') + '/query?' + urllib.parse.urlencode(params)
    st, h, body, u = M.get(full, timeout=40, accept='application/json,*/*;q=0.5')
    log.append(f'GET {sid} st={st} q={q!r}')
    time.sleep(2.1)
    if st != 200 or not body:
        obj = {'ok': False, 'st': st, 'features': []}
        cache_put(key, obj); return obj, False
    try:
        j = json.loads(body)
    except Exception:
        obj = {'ok': False, 'st': 'bad-json', 'features': []}
        cache_put(key, obj); return obj, False
    feats = []
    for f in (j.get('features') or [])[:8]:
        a = f.get('attributes') or {}
        g = f.get('geometry') or {}
        feats.append({'id': a.get(idfield), 'name': a.get(nfield), 'rings': g.get('rings') or []})
    obj = {'ok': True, 'st': 200, 'features': feats, 'service': label}
    cache_put(key, obj); return obj, False


def core_query(name):
    """Distinctive tokens for LIKE query (drop kind words)."""
    drop = set('state national nature natural preserve park wildlife management area wilderness recreation '
               'historic site forest reserve refuge river lake the and of de la'.split())
    words = [w for w in re.findall(r"[A-Za-z0-9']+", name) if w.lower() not in drop and len(w) > 2]
    if not words: return None
    # use longest 1–2 tokens
    words.sort(key=len, reverse=True)
    return ' '.join(words[:2]).upper()


def pick_services(area):
    if area.startswith('US'): return [s for s in SERVICES if s[0] == 'padus']
    if area.startswith('CA'): return [s for s in SERVICES if s[0] == 'cpcad']
    return [s for s in SERVICES if s[0].startswith('eea')]


def sample_parks(n=36):
    """Mix of needs-person + far solved-join pile parks."""
    rows = []
    for path in (ROOT / 'data/waiting/in/data/pile-solver/needs-person.csv',
                 ROOT / 'data/waiting/in/data/pile-solver/solved-join.csv'):
        if not path.exists(): continue
        with open(path, newline='', encoding='utf-8') as f:
            rows.extend(csv.DictReader(f))
    # diversify by country prefix
    picked, seen = [], set()
    for r in rows:
        cc = (r.get('area') or r.get('ref', '')[:2])[:2]
        if not r.get('pota_name') or not r.get('pota_lat'): continue
        try:
            lat, lon = float(r['pota_lat']), float(r['pota_lon'])
        except ValueError:
            continue
        if abs(lat) < 0.01 and abs(lon) < 0.01: continue
        key = cc
        # allow up to 6 per CC
        if sum(1 for x in picked if (x.get('area') or '')[:2] == cc) >= 6: continue
        picked.append(r)
        if len(picked) >= n: break
    return picked


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    M = KM.Manners(UA_JOB)
    log = []
    parks = sample_parks(36)
    results = []
    hits = amb = miss = 0
    ledger_rows = AL.load_rows()
    for r in parks:
        name = r['pota_name']
        q = core_query(name)
        lat, lon = float(r['pota_lat']), float(r['pota_lon'])
        area = r.get('area') or ''
        cands = []
        if q:
            for svc in pick_services(area):
                obj, _ = query_name(M, svc, q, log)
                for f in obj.get('features') or []:
                    if not f.get('name'): continue
                    d = dist_to_boundary_m(lat, lon, f.get('rings') or [])
                    if d is None: continue
                    cands.append({'service': obj.get('service') or svc[0], 'id': f.get('id'), 'name': f.get('name'),
                                  'distance_m': round(d), 'inside': d == 0})
        # unique within 15 km
        within = [c for c in cands if c['distance_m'] <= FIFTEEN_KM * 1000]
        # unique by normalised name
        by_name = {}
        for c in within:
            k = re.sub(r'[^a-z0-9]', '', (c['name'] or '').lower())
            by_name.setdefault(k, []).append(c)
        status = 'miss'
        chosen = None
        if not within:
            status = 'miss'; miss += 1
        elif len(by_name) == 1 and len(next(iter(by_name.values()))) >= 1:
            # unique name (possibly multiple geometry pieces of same name — take nearest)
            pool = next(iter(by_name.values()))
            chosen = min(pool, key=lambda c: c['distance_m'])
            status = 'hit'; hits += 1
            prop = f"official-polygon: {chosen['service']} {chosen['id']} '{chosen['name']}' at {chosen['distance_m']} m"
            if not any(x.get('park') == r['ref'] and x.get('kind') == 'join' and x.get('proposed_by') == 'pile-solver'
                       and 'official-polygon' in (x.get('proposal') or '') for x in ledger_rows):
                ledger_rows = AL.propose(r['ref'], 'join', 'pile-solver', prop,
                                         source='official-polygon-sample', pota_lat=str(lat), pota_lon=str(lon),
                                         notes='IDEA Nov 4 unique name ≤15 km', rows=ledger_rows)
        else:
            status = 'ambiguous'; amb += 1
        results.append({
            'ref': r['ref'], 'pota_name': name, 'area': area, 'lat': lat, 'lon': lon,
            'query': q or '', 'status': status, 'n_candidates_15km': len(within),
            'chosen_service': (chosen or {}).get('service', ''), 'chosen_id': (chosen or {}).get('id', ''),
            'chosen_name': (chosen or {}).get('name', ''), 'distance_m': (chosen or {}).get('distance_m', ''),
            'candidates': '; '.join(f"{c['name']}[{c['distance_m']}m/{c['service']}]" for c in within[:5]),
        })

    AL.save_rows(ledger_rows)
    with open(OUT / 'polygon-sample.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(results[0].keys()) if results else ['ref', 'status'])
        w.writeheader(); w.writerows(results)
    summary = {
        'idea_quote': IDEA_QUOTE, 'provenance': PROVENANCE,
        'sample_n': len(results), 'hit': hits, 'ambiguous': amb, 'miss': miss,
        'ledger_proposals_added': sum(1 for r in results if r['status'] == 'hit'),
        'auto': False,
        'robots': 'KPC_ARCGIS_ROBOTS_EXEMPT=0; Manners gap 2s; cache under polygon-sample/cache/',
        'services': [s[0] for s in SERVICES],
    }
    json.dump(summary, open(OUT / 'polygon-sample-summary.json', 'w'), indent=1, ensure_ascii=False)
    open(OUT / 'requests-snippet.log', 'w').write('\n'.join(log) + '\n')
    print(json.dumps(summary, indent=1)); return 0


if __name__ == '__main__':
    sys.exit(main())
