#!/usr/bin/env python3
"""GIS HUNTER (chat 10, Opus, Oct 29 2026, from Fable's design .claude/build/research/KPC_GisHunter_Design_Fable.md; Brandon 9:32 PM
'build it run US 1st ... then run Canada'). Searches the US + Canada Fable lists (parks with no outline) for OFFICIAL GIS layers,
inside Rule G (R-G7 steps 2-3, P-2 polygons before pages, P-4 per agency). It DECIDES NOTHING: it writes candidates with evidence
for chat 11 (YES / NO), new layers for the intake queue, and WORK LOG rows. No tracing, no key edits, no pin moves, nothing on the
site (freeze). Geometry is never stored (envelopes + rough acres only).

STEP A (polygons first): for each area, every layer we already know (data/state-gis.json for a US state + PAD-US; for Canada the
  province's layers in data/ca-key/layers.json + CPCAD + Parks Canada) is asked ONCE per 120 pins with a multipoint query
  (outSR 4326, geometry generalised ~200 m); the hit polygons are matched to the pins here (point in polygon). Verdicts per hit:
    name match     the record's name shares a core word with POTA's name     -> candidate for chat 11
    name mismatch  park-type layer, no shared word (the BLM / state name differs from POTA's) -> candidate for chat 11
    inside-other   PAD-US / land layer with another name (a bigger area: R-G7 step 4 ownership later) -> noted, never offered
STEP B (layers we do not have): a park with no candidate after A gets ONE ArcGIS Online search by its name (feature / map services);
  results whose title shares 2+ core words are LEADS appended to data/intake/queue.json (from 'gis-hunter'), which the intake bot
  probes and judges (READY rules). Capped per area per run.
OUT  data/gis-hunter/<area>.json (per park: hits, verdict, tried) · data/gis-hunter/worklog-<area>.md (rows in the Fable file's
     WORK LOG format, for chats 3 / 8 / HQ to paste) · data/waiting/questions/gis-hunter.json + .md (candidates, one YES / NO question
     each, answers kept across runs) · COUNT line per area · status board + 'grade me' line.
Env: AREAS ('US-IA US-RI' / 'CA-PE'; blank = every US area with open parks, fewest first) · COUNTRY (US | CA, used when AREAS is
     blank) · LINKS (KPC-Links checkout: the Fable pools + keys) · MINUTES (55) · BMAX (searches per area per run, 40) · NET=1
Manners: kpc_manners.py (robots.txt; ArcGIS REST exempt; 2 s per host; three strikes = a day's rest). Never fails (exit 0)."""
import json, math, os, pathlib, re, sys, time, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kpc_manners import Manners  # noqa: E402

LINKS = pathlib.Path(os.environ.get('LINKS') or '../links')
OUT = pathlib.Path('data/gis-hunter'); QDIR = pathlib.Path('data/waiting/questions')
T0 = time.time(); LIMIT = float(os.environ.get('MINUTES') or 55) * 60
BMAX = int(os.environ.get('BMAX') or 40)
TODAY = time.strftime('%Y-%m-%d')
M = Manners('GIS hunter (official park layers)')
PADUS = 'https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0'
CA_NATIONAL = ['https://maps-cartes.ec.gc.ca/arcgis/rest/services/CWS_SCF/CPCAD/MapServer/0',
               'https://services2.arcgis.com/wCOMu5IS7YdSyPNx/arcgis/rest/services/vw_Places_Public_lieux_public_APCA/FeatureServer/0']
PROV = {'AB': 'alberta', 'BC': 'bc ', 'MB': 'manitoba', 'NB': 'new brunswic', 'NS': 'nova scotia', 'NT': 'nt ', 'NU': 'nu-', 'ON': 'ontario',
        'PE': 'pe ', 'QC': 'québec', 'SK': 'saskatchewan', 'YT': 'yukon', 'NL': 'newfoundland'}
STOP = set('state park parks national forest wildlife management area wma the of and nature preserve recreation lake river natural historic site '
           'county city regional reserve conservation memorial trail wilderness refuge nwr sp sf creek fish game public lands land unit at on in '
           'de la le du des provincial parc réserve aire faunique écologique ecological protected habitat blm herd hma rma sra wa'.split())
NAME_RX = re.compile(r'(^|_)(unit_?nm|loc_?nm|name|nom|nm|label|title|site|park|prop|area_?name|parkname|propname)', re.I)


def notice(m): print('::notice title=GIS hunter::' + str(m).replace('\n', ' ')[:900], flush=True)
def late(): return time.time() - T0 > LIMIT - 120
def load(p, d=None):
    try: return json.load(open(p, encoding='utf-8'))
    except Exception: return d  # noqa: BLE001
def words(s): return {w for w in re.findall(r'[a-zà-ÿ0-9]+', str(s or '').lower()) if len(w) > 2 and w not in STOP}


# ------------------------------------------------------------------------------------------------ inputs
def us_pool():
    W = (load(LINKS / 'data' / 'us-key' / 'why-not.json', {}) or {}).get('parks') or {}
    out = {}
    for ref, v in W.items():
        if v.get('tag') in ('private', 'picture-map-only'): continue
        out.setdefault('US-' + v['st'], []).append((ref, v.get('tag')))
    return out


def ca_pool():
    M_ = load(LINKS / '.claude' / 'build' / 'research' / 'missing-after-key-canada.json', {}) or {}
    refs = {r: k for k in ('PIN INSIDE', 'CHECK', 'NOTHING NEAR') for r in (M_.get(k) or [])}
    prov = {}
    for f in (LINKS / 'data' / 'ca-key').glob('CA-*.json'):
        for r in ((load(f, {}) or {}).get('parks') or {}): prov[r] = f.stem
    out = {}
    for r, k in refs.items():
        if prov.get(r): out.setdefault(prov[r], []).append((r, k.lower()))
    return out


def pins(area):
    if area.startswith('US-'):
        P = (load(f'data/parkinfo/{area}.json', {}) or load(LINKS / 'data' / 'parkinfo' / f'{area}.json', {}) or {}).get('parks') or {}
        out = {r: (v[5], v[6], v[0]) for r, v in P.items() if len(v) > 6 and v[5] is not None}
        if area == 'US-KY':
            for x in (load(LINKS / 'kpc-ky-data.json', {}) or {}).get('parks', []):
                if x.get('c') and x.get('la') is not None: out.setdefault(x['c'], (x['la'], x['lo'], x.get('n', '')))
        return out
    return {r[1]: (r[3], r[4], r[2]) for r in (load('data/canada.json', {}) or {}).get('rows') or [] if r[0] == 'POTA' and (r[3], r[4]) != (0, 0)}


def layers(area):
    if area.startswith('US-'):
        L = [(x['url'], x.get('kind', ''), x.get('ag', ''), x.get('nm')) for x in ((load('data/state-gis.json', {}) or {}).get('states') or {}).get(area[3:], []) if x.get('url')]
        return L + [(PADUS, 'padus', 'USGS PAD-US', 'Unit_Nm')]
    st = area[3:]; key = PROV.get(st, '#')
    out = []
    for label, urls in (load('data/ca-key/layers.json', {}) or {}).items():
        lab = label.lower()
        if lab.startswith(st.lower() + '-') or lab.startswith(st.lower() + ' ') or lab.startswith(key):
            out += [(u, 'park', label, None) for u in urls]
    return out + [(u, 'national', 'CPCAD / Parks Canada', None) for u in CA_NATIONAL]


# ------------------------------------------------------------------------------------------------ geometry helpers
def inside(x, y, ring):
    c = False; j = len(ring) - 1
    for i in range(len(ring)):
        xi, yi = ring[i][0], ring[i][1]; xj, yj = ring[j][0], ring[j][1]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-12) + xi: c = not c
        j = i
    return c


def acres(rings):
    tot = 0.0
    for r in rings:
        if len(r) < 3: continue
        la0 = sum(p[1] for p in r) / len(r); kx = 111320 * math.cos(math.radians(la0)); ky = 110540
        a = sum((r[i][0] * kx) * (r[(i + 1) % len(r)][1] * ky) - (r[(i + 1) % len(r)][0] * kx) * (r[i][1] * ky) for i in range(len(r))) / 2
        tot += a   # rings: outer clockwise in Esri (negative here), holes the other way; the sign sorts it out
    return round(abs(tot) / 4046.86)


def arc(u, params):
    q = urllib.parse.urlencode({**params, 'f': 'json'})
    st, hd, body, final = M.get(u.rstrip('/') + '/query?' + q, accept='application/json', timeout=120)
    if not (isinstance(st, int) and st < 400): raise RuntimeError(f'no answer ({st})')
    j = json.loads(body.decode('utf-8', 'replace'))
    if isinstance(j, dict) and j.get('error'): raise RuntimeError(str(j['error'])[:140])
    return j


def name_of(a, nm):
    if nm and a.get(nm): return str(a[nm])
    for k, v in a.items():
        if isinstance(v, str) and v.strip() and NAME_RX.search(k): return v
    return ''


# ------------------------------------------------------------------------------------------------ step A
def step_a(area, todo, P, R):
    for url, kind, ag, nm in layers(area):
        if late(): break
        pts = [(r, P[r]) for r in todo if r in P]
        for i in range(0, len(pts), 120):
            chunk = pts[i:i + 120]
            mp = {'points': [[round(p[1], 5), round(p[0], 5)] for _, p in chunk], 'spatialReference': {'wkid': 4326}}
            try:
                j = arc(url, {'geometry': json.dumps(mp, separators=(',', ':')), 'geometryType': 'esriGeometryMultipoint', 'inSR': 4326,
                              'spatialRel': 'esriSpatialRelIntersects', 'outFields': '*', 'returnGeometry': 'true', 'outSR': 4326,
                              'maxAllowableOffset': 0.002, 'geometryPrecision': 5})
            except Exception as e:  # noqa: BLE001
                for r, _ in chunk: R[r]['tried'].append(f'A {ag[:40]}: {str(e)[:60]}')
                continue
            feats = j.get('features') or []
            for r, (la, lo, pn) in chunk:
                hit = False
                for f in feats:
                    rings = (f.get('geometry') or {}).get('rings') or []
                    if not any(inside(lo, la, rg) for rg in rings): continue
                    a = f.get('attributes') or {}; rn = name_of(a, nm); hit = True
                    oid = a.get('OBJECTID') or a.get('objectid') or a.get('FID')
                    share = bool(words(rn) & words(pn))
                    if kind == 'padus':
                        v = 'name match' if share else 'inside-other'
                        extra = {k: a.get(k) for k in ('Mang_Name', 'Des_Tp', 'Own_Type', 'GIS_Acres') if k in a}
                    else:
                        line = re.search(r'trail|river|byway|parkway|greenway|canal|route|corridor', pn, re.I)   # a trail crossing a park is not that park
                        v = 'name match' if share else ('name mismatch' if kind in ('park', 'preserve', 'national') and not line else 'inside-other')
                        extra = {}
                    R[r]['hits'].append({'verdict': v, 'layer': url, 'agency': ag, 'record': oid, 'record_name': rn[:120], 'acres_approx': acres(rings), **extra})
                R[r]['tried'].append(f"A {ag[:40]}: {'hit' if hit else 'no polygon at the pin'}")


# ------------------------------------------------------------------------------------------------ step B
def step_b(area, todo, P, R, queue):
    n = 0
    for r in todo:
        if late() or n >= BMAX: break
        if any(h['verdict'] in ('name match', 'name mismatch') for h in R[r]['hits']) or r not in P: continue
        pn = P[r][2]; core = words(pn)
        if len(core) < 1: continue
        q = ' '.join(sorted(core, key=len, reverse=True)[:3])
        n += 1
        try:
            st, hd, body, final = M.get('https://www.arcgis.com/sharing/rest/search?' + urllib.parse.urlencode(
                {'q': f'{q} (type:"Feature Service" OR type:"Map Service")', 'num': 8, 'f': 'json'}), accept='application/json')
            res = (json.loads(body.decode('utf-8', 'replace')) if isinstance(st, int) and st < 400 else {}).get('results') or []
        except Exception as e:  # noqa: BLE001
            R[r]['tried'].append(f'B ArcGIS Online search: {str(e)[:60]}'); continue
        leads = [x for x in res if len(words(x.get('title')) & core) >= min(2, len(core)) and x.get('url')]
        R[r]['tried'].append(f'B ArcGIS Online search "{q}": {len(leads)} lead(s)')
        for x in leads[:3]:
            R[r]['leads'].append({'title': x.get('title'), 'url': x.get('url'), 'owner': x.get('owner'), 'type': x.get('type')})
            if x['url'] not in queue['seen']:
                queue['rows'].append({'url': x['url'], 'title': (x.get('title') or '')[:120], 'from': 'gis-hunter', 'added': TODAY,
                                      'closes': [r], 'note': f"ArcGIS Online search for {pn[:60]} (owner {x.get('owner')})"})
                queue['seen'].add(x['url'])


# ------------------------------------------------------------------------------------------------ outputs
def verdict(rec):
    v = [h['verdict'] for h in rec['hits']]
    if 'name match' in v: return 'candidate: name match'
    if v.count('name mismatch') == 1: return 'candidate: name mismatch'   # one park-type record under the pin; two or more = unclear, R-G7 step 4
    if 'name mismatch' in v: return 'inside-other (several park records under the pin: R-G7 step 4)'
    if rec['leads']: return 'lead: new layer queued for intake'
    if 'inside-other' in v: return 'inside-other (bigger area with another name: R-G7 step 4 ownership)'
    return 'no layer found'


def write_area(area, R):
    OUT.mkdir(parents=True, exist_ok=True)
    json.dump({'area': area, 'run': TODAY, 'about': 'GIS hunter (Fable design, Opus build): per park, hits on the official layers at the POTA pin, leads, what was tried. Candidates go to data/waiting/questions/gis-hunter.json for chat 11.',
               'parks': R}, open(OUT / f'{area}.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    L = [f'## {area} — GIS hunter {TODAY} (paste into the Fable file WORK LOG)', '', '| ref | park | step | what was found | result | date | by |', '|---|---|---|---|---|---|---|']
    for r, rec in sorted(R.items()):
        best = next((h for h in rec['hits'] if h['verdict'] in ('name match', 'name mismatch')), rec['hits'][0] if rec['hits'] else None)
        found = (f"{best['agency']}: '{best['record_name']}' (record {best['record']}, ~{best['acres_approx']:,} ac, pin inside)" if best
                 else '; '.join(f"lead {x['title']} ({x['url']})" for x in rec['leads'][:2]) or 'nothing')
        L.append(f"| {r} | {rec['park']} | R-G7 step {'2' if best else '3'} | {found[:300]} | {rec['verdict']} | {TODAY} | gis-hunter |")
    (OUT / f'worklog-{area}.md').write_text('\n'.join(L) + '\n', encoding='utf-8')


def write_questions(all_R):
    QDIR.mkdir(parents=True, exist_ok=True)
    old = {(q['ref'], str(q['record']), q['layer']): q for q in (load(QDIR / 'gis-hunter.json', {}) or {}).get('questions') or []}
    keep = [q for q in old.values() if q['area'] not in all_R]   # areas not run this time keep their questions
    qs = []
    for area, R in all_R.items():
        for r, rec in R.items():
            for h in rec['hits']:
                if h['verdict'] not in ('name match', 'name mismatch') or not rec['verdict'].startswith('candidate'): continue
                if rec['verdict'] == 'candidate: name match' and h['verdict'] != 'name match': continue
                q = {'area': area, 'ref': r, 'park': rec['park'], 'kind': h['verdict'], 'record': h['record'], 'record_name': h['record_name'],
                     'acres_approx': h['acres_approx'], 'layer': h['layer'], 'agency': h['agency'],
                     'record_link': f"{h['layer']}/query?objectIds={h['record']}&outFields=*&returnGeometry=false&f=html" if h['record'] is not None else h['layer'],
                     'pota_link': f'https://pota.app/#/park/{r}',
                     'question': "Is this official record that park (the agency's own boundary for it)? YES / NO",
                     'answer': None, 'checked_by': None, 'how': None, 'source': 'gis-hunter'}
                prev = old.get((r, str(h['record']), h['layer']))
                if prev: q.update({k: prev.get(k) for k in ('answer', 'checked_by', 'how', 'rechecked_by_chat2')})
                qs.append(q)
    qs = keep + qs
    D = {'about': "GIS hunter candidates (Rule G R-G7 steps 2-3): chat 11 answers YES / NO + checked_by + how (the agency map looked at); chat 2 rechecks (G-4) and joins in the key. 'name mismatch' = the official record's name differs from POTA's.",
         'built': TODAY, 'open': sum(1 for q in qs if not q['answer']), 'questions': qs}
    json.dump(D, open(QDIR / 'gis-hunter.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    L = ['# GIS hunter questions for chat 11', '', f"{len(qs)} candidates, {D['open']} open. Answer in gis-hunter.json.", '',
         '| area | park | kind | official record | ~acres | answer | links |', '|---|---|---|---|---|---|---|']
    for q in qs:
        L.append(f"| {q['area']} | {q['ref']} {q['park'][:40]} | {q['kind']} | {q['record_name'][:50]} ({q['agency'][:30]}) | {q['acres_approx']:,} | {q['answer'] or 'OPEN'} | [record]({q['record_link']}) · [POTA]({q['pota_link']}) |")
    (QDIR / 'gis-hunter.md').write_text('\n'.join(L) + '\n', encoding='utf-8')


def main():
    want = (os.environ.get('AREAS') or '').split()
    pool = {}
    if not want or any(a.startswith('US-') for a in want): pool.update(us_pool())
    if not want and os.environ.get('COUNTRY') == 'CA': pool = ca_pool()
    elif any(a.startswith('CA-') for a in want): pool.update(ca_pool())
    state = load(OUT / 'state.json', {}) or {}
    areas = [a for a in want if a in pool] if want else sorted((a for a in pool if (state.get(a) or {}).get('run') != TODAY), key=lambda a: len(pool[a]))
    queue = load('data/intake/queue.json', {'rows': []}) or {'rows': []}
    queue['seen'] = {r.get('url') for r in queue.get('rows') or []}
    done_R = {}
    for area in areas:
        if late(): break
        P = pins(area); todo = [r for r, _ in pool[area]]
        R = {r: {'park': (P.get(r) or (0, 0, ''))[2], 'why_not': t, 'hits': [], 'leads': [], 'tried': []} for r, t in pool[area]}
        step_a(area, todo, P, R)
        step_b(area, todo, P, R, queue)
        for rec in R.values(): rec['verdict'] = verdict(rec)
        write_area(area, R); done_R[area] = R
        c = {}
        for rec in R.values(): c[rec['verdict'].split(':')[0].split(' (')[0]] = c.get(rec['verdict'].split(':')[0].split(' (')[0], 0) + 1
        nm = sum(1 for x in R.values() if x['verdict'] == 'candidate: name match'); mm = sum(1 for x in R.values() if x['verdict'] == 'candidate: name mismatch')
        notice(f"{area} COUNT: open {len(R)} / step A: name match {nm}, name mismatch {mm}, inside-other {sum(1 for x in R.values() if x['verdict'].startswith('inside'))} / step B leads {sum(1 for x in R.values() if x['verdict'].startswith('lead'))} / nothing {sum(1 for x in R.values() if x['verdict'] == 'no layer found')}")
        empty = [r for r, x in R.items() if x['verdict'] == 'no layer found' and not x['tried']]
        if empty: notice(f'{area} BUG: {len(empty)} parks say no layer with nothing tried, e.g. {empty[0]}')
        state[area] = {'run': TODAY, 'open': len(R), 'candidates': nm + mm}
    if done_R: write_questions(done_R)
    queue.pop('seen', None)
    json.dump(queue, open('data/intake/queue.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    OUT.mkdir(parents=True, exist_ok=True); json.dump(state, open(OUT / 'state.json', 'w'), indent=1)
    left = [a for a in (pool if not want else want) if a in pool and (state.get(a) or {}).get('run') != TODAY]
    print(f'LEFT={len(left)}')
    notice(f"done {len(done_R)} areas ({', '.join(done_R)[:300]}); {len(left)} left; manners {M.stat}")


if __name__ == '__main__':
    try: main()
    except Exception as e: notice(f'stopped ({type(e).__name__}: {e})')  # noqa: BLE001
    sys.exit(0)
