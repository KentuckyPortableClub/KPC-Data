#!/usr/bin/env python3
"""NPS PARK TRAILS (Nov 8 2026; Brandon: 'NPS offers trails'). Pulls trail LINES for NPS units from the NPS's own public service
  mapservices.nps.gov/arcgis/rest/services/NationalDatasets/NPS_Public_Trails_Geographic/FeatureServer/0
(no key; robots.txt answers 404 = nothing disallowed; checked again at start, a 401/403/5xx robots answer = refused, stop).
Lines whose MAPSOURCE names OpenStreetMap / OSM are dropped (Brandon: no OSM lines). Only PUBLICDISPLAY='Public Map Display'
and DATAACCESS='Unrestricted' lines are kept. Writes <out>/<UNITCODE>.geojson.gz (simplified ~3 m, 6 decimals) + <out>/index.json
[{unit, name, lines, kb, bbox}], for an in-park trail map layer or a trail park tied to an NPS unit.
The NPS DataStore (irma.nps.gov /DataStore/DownloadFile/, irmaservices.nps.gov: robots Disallow) is NOT used: hand download only.
  python3 kpc_nps_park_trails.py --units GRSM,BUFF --out /tmp/nps-trails
  python3 kpc_nps_park_trails.py --out /tmp/nps-trails    (no --units = every NPS unit, ~1 request a second)
  python3 kpc_nps_park_trails.py --list            (unit codes + names the service holds)"""
import argparse, gzip, json, os, re, sys, time, urllib.error, urllib.parse, urllib.request, urllib.robotparser

HOST = 'https://mapservices.nps.gov'
LAYER = HOST + '/arcgis/rest/services/NationalDatasets/NPS_Public_Trails_Geographic/FeatureServer/0'
UA = {'User-Agent': 'KPC park trails (kentuckyportableclub.github.io)'}
OSM = re.compile(r'open\s*street\s*map|\bosm\b', re.I)
TOL = 0.00003


def robots_ok(url, fetch=None):
    """robots.txt: 404/410 = allowed; 401/403/5xx or an error = refused; else robotparser decides."""
    try:
        if fetch: code, body = fetch(HOST + '/robots.txt')
        else:
            try:
                with urllib.request.urlopen(urllib.request.Request(HOST + '/robots.txt', headers=UA), timeout=30) as f:
                    code, body = f.status, f.read().decode('utf-8', 'replace')
            except urllib.error.HTTPError as e: code, body = e.code, ''
    except Exception: return False  # noqa: BLE001
    if code in (404, 410): return True
    if code != 200: return False
    rp = urllib.robotparser.RobotFileParser(); rp.parse(body.splitlines())
    return rp.can_fetch(UA['User-Agent'], url)


PACE = float(os.environ.get('NPS_PACE') or 1.0)   # Nov 8: about one request per second to mapservices.nps.gov
_last = [0.0]


def get(url):
    w = PACE - (time.time() - _last[0])
    if w > 0: time.sleep(w)
    _last[0] = time.time()
    for i in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=180) as f: return json.loads(f.read())
        except Exception as e: err = e; time.sleep(3 + 3 * i)  # noqa: BLE001
    raise err


def keep(props):
    p = props or {}
    if OSM.search(str(p.get('MAPSOURCE') or '')) or OSM.search(str(p.get('ORIGINATOR') or '')): return False
    if (p.get('PUBLICDISPLAY') or 'Public Map Display') != 'Public Map Display': return False
    if (p.get('DATAACCESS') or 'Unrestricted') != 'Unrestricted': return False
    return True


def lines_of(g):
    t, c = (g or {}).get('type'), (g or {}).get('coordinates') or []
    return [c] if t == 'LineString' else c if t == 'MultiLineString' else []


def unit_lines(unit):
    if not re.fullmatch(r'[A-Z]{4}', unit): raise ValueError(f'bad unit code {unit!r}')
    feats, off = [], 0
    while True:
        q = urllib.parse.urlencode({'where': f"UNITCODE='{unit}'", 'outFields': 'TRLNAME,MAPLABEL,MAPSOURCE,ORIGINATOR,PUBLICDISPLAY,DATAACCESS,UNITNAME,TRLSTATUS',
                                    'returnGeometry': 'true', 'outSR': 4326, 'maxAllowableOffset': TOL, 'geometryPrecision': 6,
                                    'resultOffset': off, 'resultRecordCount': 2000, 'f': 'geojson'})
        j = get(f'{LAYER}/query?{q}'); fs = j.get('features') or []
        feats += fs; off += len(fs)
        if len(fs) < 2000 or off > 60000: break
    return feats


def build(feats, unit):
    out, name = [], ''
    for f in feats:
        p = f.get('properties') or {}
        name = name or p.get('UNITNAME') or ''
        if not keep(p) or str(p.get('TRLSTATUS') or 'Existing') != 'Existing': continue
        ls = [[[round(x[0], 6), round(x[1], 6)] for x in l] for l in lines_of(f.get('geometry'))]
        ls = [l for l in ls if len(l) > 1]
        if ls: out.append({'type': 'Feature', 'properties': {'name': (p.get('TRLNAME') or p.get('MAPLABEL') or '').strip()},
                           'geometry': {'type': 'MultiLineString', 'coordinates': ls}})
    return {'type': 'FeatureCollection', 'properties': {'unit': unit, 'name': name, 'src': LAYER, 'no_osm': True}, 'features': out}


def bbox(fc):
    xs = [p[0] for f in fc['features'] for l in f['geometry']['coordinates'] for p in l]
    ys = [p[1] for f in fc['features'] for l in f['geometry']['coordinates'] for p in l]
    return [round(min(xs), 4), round(min(ys), 4), round(max(xs), 4), round(max(ys), 4)] if xs else None


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--units', default=''); ap.add_argument('--out', default='nps-trails'); ap.add_argument('--list', action='store_true')
    a = ap.parse_args()
    if not robots_ok(LAYER + '/query'):
        print('::warning title=NPS trails::robots.txt refuses mapservices.nps.gov: nothing fetched'); return 0
    def all_units():
        j = get(LAYER + '/query?' + urllib.parse.urlencode({'where': '1=1', 'outFields': 'UNITCODE,UNITNAME', 'returnDistinctValues': 'true', 'returnGeometry': 'false', 'f': 'json'}))
        return sorted({(f['attributes']['UNITCODE'], f['attributes']['UNITNAME']) for f in j.get('features', []) if f['attributes'].get('UNITCODE')}, key=str)
    if a.list:
        for r in all_units(): print(*r, sep='\t')
        return 0
    if a.units.strip().upper() in ('', 'ALL'):   # Nov 8: no unit codes = every NPS unit the service holds
        a.units = ','.join(u for u, _ in all_units() if re.fullmatch(r'[A-Z]{4}', str(u)))
        print(f"all NPS units: {a.units.count(',') + 1 if a.units else 0}")
    os.makedirs(a.out, exist_ok=True); index = []
    for unit in [u.strip().upper() for u in a.units.split(',') if u.strip()]:
        try:
            fc = build(unit_lines(unit), unit)
            if not fc['features']: print(f'{unit}: no non-OSM public lines'); continue
            fn = os.path.join(a.out, f'{unit}.geojson.gz')
            with open(fn, 'wb') as fh, gzip.GzipFile(fileobj=fh, mode='wb', mtime=0) as z: z.write(json.dumps(fc, separators=(',', ':')).encode())
            index.append({'unit': unit, 'name': fc['properties']['name'], 'lines': len(fc['features']), 'kb': os.path.getsize(fn) // 1024, 'bbox': bbox(fc)})
            print(f"{unit}: {len(fc['features'])} lines, {index[-1]['kb']} KB")
        except Exception as e: print(f'::warning title=NPS trails::{unit}: {e}')  # noqa: BLE001
    with open(os.path.join(a.out, 'index.json'), 'w', newline='') as f: json.dump(index, f, indent=0)
    return 0


if __name__ == '__main__':
    sys.exit(main())
