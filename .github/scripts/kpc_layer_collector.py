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


def main():
    want = set(sys.argv[1:])
    log = load(LOG, {}) or {}
    D = load(QF, {}) or {}
    qs = D.get('questions') or []
    queue = load(QUEUE, {'rows': []}) or {'rows': []}
    seen = {r.get('url') for r in queue.get('rows') or []}
    n = {'new': 0, 'asked': 0, 'queued': 0, 'failed': 0, 'evidence': 0}
    for f in sorted((LINKS / '.claude' / 'build' / 'research' / 'fable').glob('*.md')):
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
    LOG.parent.mkdir(parents=True, exist_ok=True)
    json.dump(log, open(LOG, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    json.dump(queue, open(QUEUE, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    QF.parent.mkdir(parents=True, exist_ok=True)
    json.dump({'about': "Layers chat 8 wrote as LAYER lines in the Fable files, pin-tested by the layer collector (Rule G: pin inside, name tier, size). Chat 11 answers YES / NO; BOT A joins a YES.",
               'built': TODAY, 'open': sum(1 for q in qs if not q.get('answer')), 'questions': qs}, open(QF, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print(f"::notice title=Layer collector::{n['new']} new LAYER lines: {n['asked']} asked (chat 11), {n['queued']} queued for the intake only, {n['evidence']} evidence, {n['failed']} failed (reason in data/intake/collector.json)")


if __name__ == '__main__':
    try: main()
    except Exception as e: print(f'::notice title=Layer collector::stopped ({type(e).__name__}: {e})')  # noqa: BLE001
    sys.exit(0)
