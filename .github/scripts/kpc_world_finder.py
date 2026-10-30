#!/usr/bin/env python3
"""WORLD FINDER v2 (chat 10, Opus, Oct 29 2026; replaces the world harvester's way of working). Design: Fable's
KPC-Links .claude/build/research/KPC_WorldHarvester_Redesign_Fable.md (sections 1-6 + Opus 9-10 + Brandon's stages 11-12).
STAGE 1 ONLY (Brandon 10:09 PM): Fable's plan to a T over the WHOLE world list (every POTA country outside the US + Canada),
biggest gap first, France last. W9 (Protected Planet phone book) and W2 (EEA Natura 2000 / CDDA fallback) are OFF here (flags below)
until every country has had its stage-1 pass. Decides nothing; nothing on the site; geometry never stored.

Per country:
 1 GAP     POTA's parks (data/pota/t tiles) minus the world key's matched ones (KPC-Links data/world-key/<CC>.json 'm').
 2 STEP A  (a) keyed countries: the key's own pin-inside rows ('c') of every open park become chat 11 candidates (one record = a
           candidate: name match / name mismatch; several = inside-other); (b) every polygon layer the harvester already found for
           the country (leads-<CC>.json, band A/B) gets ONE multipoint query per 120 open pins (the GIS hunter's step A).
 3 STEP B  the programmed finders (the harvester's own code, re-aimed): seed book + known goods → the agency's servers / OGC / WFS
           (from chat 8's agency table world_agencies.json, grade C = leads to open) → ArcGIS Online orgs → national catalogs (CKAN,
           Hub) → ArcGIS Online search in the LOCAL LANGUAGE (the table's native park words). New polygon layers found are then
           run through step A (b) for this country's open pins, so 'found' is measured in PARKS, not leads.
 4 OUT     candidates → data/waiting/questions/world-finder.json + .md (chat 11 YES / NO, answers kept); leads stay in
           data/harvest/leads-<CC>.json (the intake bot pulls A-band leads nightly); per country data/world-finder/<CC>.json
           (open, candidates, layers tried, 'no-layer' agency groups for chat 8) + a COUNT line 'covered before -> after'.
Env: COUNTRIES (blank = the whole world list in gap order, skipping countries finished in this stage) · LINKS · MINUTES (55)
     · PER_COUNTRY_MIN (25: a big country carries on next chunk) · W9=0 · W2=0 (stage 2 / 3 flags: leave OFF)
Manners: the harvester's (robots.txt, ArcGIS REST exempt, 2 s per host, a day's rest after 3 strikes). Never fails (exit 0)."""
import copy, glob, json, os, pathlib, re, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kpc_world_harvest as H   # noqa: E402  (the harvester's finders, manners and lead format)
import kpc_gis_hunter as G
import kpc_tiers as T  # noqa: E402      # noqa: E402  (step A: multipoint pins on a layer, point in polygon, name words)

W9 = os.environ.get('W9') == '1'; W2 = os.environ.get('W2') == '1'   # Brandon 10:09 PM: stage 2 / 3 only after stage 1 everywhere
LINKS = pathlib.Path(os.environ.get('LINKS') or '../links')
OUT = pathlib.Path('data/world-finder'); QF = pathlib.Path('data/waiting/questions/world-finder.json')
T0 = time.time(); LIMIT = float(os.environ.get('MINUTES') or 55) * 60
PER = float(os.environ.get('PER_COUNTRY_MIN') or 25) * 60
TODAY = time.strftime('%Y-%m-%d')
SKIP = {'US', 'CA'}


def notice(m): print('::notice title=World finder v2::' + str(m).replace('\n', ' ')[:900], flush=True)
def late(): return time.time() - T0 > LIMIT - 180
def load(p, d=None):
    try: return json.load(open(p, encoding='utf-8'))
    except Exception: return d  # noqa: BLE001


def all_pins():
    out = {}
    for f in glob.glob('data/pota/t/*.json'):
        for row in load(f, []) or []:
            if isinstance(row, list) and len(row) >= 4:
                cc = str(row[0]).split('-')[0]
                if cc in SKIP: continue
                out.setdefault(cc, {})[row[0]] = (row[2], row[3], row[1])
    return out


def gap_queue(pins, state):
    rows = []
    for cc, P in pins.items():
        K = (load(LINKS / 'data' / 'world-key' / f'{cc}.json', {}) or {}).get('parks') or {}
        matched = {r for r, v in K.items() if v.get('m')}
        open_ = [r for r in P if r not in matched]
        if open_: rows.append((cc, open_, K))
    # biggest gap first, France last (Fable); Oct 30 (Brandon 6:01 AM, timer 24/7): ROUND ROBIN: countries never touched come first
    # (biggest gap first), a paused big country goes to the back until the others had their turn (oldest touch first)
    def touched(cc): s = state.get(cc) or {}; return s.get('touched') or (s.get('run') if s.get('stage1') else '') or ''
    rows.sort(key=lambda x: (x[0] == 'FR', bool(touched(x[0])), touched(x[0]), -len(x[1])))
    return [r for r in rows if (state.get(r[0]) or {}).get('stage1') != 'done']


def country_cfg(cc, cfg, table):
    c = copy.deepcopy((cfg.get('countries') or {}).get(cc) or {'name': cc, 'names': [cc], 'words': [], 'catalogs': [], 'servers': [], 'ogc': [],
                                                                    'agol_orgs': [], 'known_good': [], 'official_orgs': []})
    t = (table.get('countries') or {}).get(cc) or {}
    c['words'] = list(dict.fromkeys((t.get('words') or []) + (c.get('words') or [])))[:8]          # native park words first (chat 8's table)
    for u in t.get('portals') or []:                                                                 # the agency's own GIS from the table (grade C: open it)
        if re.search(r'/arcgis/rest/services', u, re.I): c.setdefault('servers', []).append(u.split('/rest/services')[0] + '/rest/services')
        elif re.search(r'/ogc/|wfs|service=wfs', u, re.I): c.setdefault('ogc', []).append(u)
        elif re.search(r'\.arcgis\.com|hub\.arcgis', u, re.I): c.setdefault('catalog_pages', []).append(u)
    for k in ('servers', 'ogc'): c[k] = list(dict.fromkeys(c.get(k) or []))
    names = [t.get('agency_local'), t.get('agency_en')] + (t.get('also') or [])
    c['official_orgs'] = list(dict.fromkeys((c.get('official_orgs') or []) + [n for n in names if n and len(n) < 80]))
    if not W2: c['stage'] = 0          # the harvester's 'eea' step (EEA CDDA lead + EEA server walk) runs only for stage 1 configs: W2 OFF
    return c


def key_candidates(cc, open_, K, P):
    """The world key's pin-inside rows ('c'), tiered (Oct 30): SURE / LIKELY = a question, UNLIKELY = evidence. A record under 3+ open parks = container."""
    under = {}
    for r in open_:
        for x in ((K.get(r) or {}).get('c') or []):
            if isinstance(x, list) and len(x) >= 3: k = (str(x[0]), x[2]); under[k] = under.get(k, 0) + 1
    out = {}
    for r in open_:
        rows = [x for x in ((K.get(r) or {}).get('c') or []) if isinstance(x, list) and len(x) >= 3]
        if not rows: continue
        pn = (K.get(r) or {}).get('n') or (P.get(r) or (0, 0, ''))[2]
        best, bt, bw = None, 'UNLIKELY', ''
        for x in rows:
            t, why = T.tier(pn, x[1], None, None, under[(str(x[0]), x[2])])
            if re.search(r'sssi|\bsac\b|\bspa\b|ramsar', str(x[2]), re.I): t, why = 'UNLIKELY', 'a land-class layer (SSSI / SAC / SPA): never the park'
            if t == 'LIKELY' and G.LEARNED.demoted(x[2], cc): t, why = 'UNLIKELY', why + '; layer under 10% YES so far (demoted)'
            if (t == 'SURE') or (t == 'LIKELY' and bt != 'SURE') or best is None: best, bt, bw = x, t, why
            if t == 'SURE': break
        if bt == 'UNLIKELY': out[r] = {'verdict': f'inside-other ({bw}; R-G7 step 4)', 'rows': rows[:4]}; continue
        out[r] = {'verdict': f'candidate: {bt}', 'tier': bt, 'why': bw, 'record': best[0], 'record_name': str(best[1])[:120], 'layer': best[2]}
    return out


def layer_urls(cc):
    L = (load(H.OUT / f'leads-{cc}.json', {}) or {}).get('leads') or {}
    out = []
    for v in L.values():
        if v.get('band') not in ('A', 'B') or str(v.get('publisher', '')).startswith('European Environment Agency') and not W2: continue
        if re.search(r'aerial|photo|imagery|coverage|index|grid|cadastr|parcel|census|tile', str(v.get('title', '')) + ' ' + str(v.get('url', '')), re.I): continue   # Oct 30: never a park layer
        for ly in v.get('layers') or []:
            if re.search(r'aerial|photo|imagery|coverage|index|grid|cadastr|parcel|census|tile', str(ly.get('name', '')), re.I): continue
            if 'olygon' in str(ly.get('geom', '')) and ly.get('id') is not None and str(v.get('url', '')).rstrip('/').endswith(('FeatureServer', 'MapServer')):
                out.append((v['url'].rstrip('/') + f"/{ly['id']}", 'park', (v.get('publisher') or v.get('title') or '')[:60], None))
    return out[:15]


def run_country(cc, open_, K, P, cfg, table, hstate, Q):
    t0 = time.time()
    rec = {'cc': cc, 'run': TODAY, 'parks': len(P), 'open': len(open_), 'key_candidates': 0, 'layer_candidates': 0, 'layers_tried': [], 'no_layer_groups': {}}
    kc = key_candidates(cc, open_, K, P)
    for r, v in kc.items():
        if v['verdict'].startswith('candidate'):
            Q.append({'area': cc, 'ref': r, 'park': (K.get(r) or {}).get('n') or P.get(r, (0, 0, ''))[2], 'tier': v['tier'], 'kind': v['verdict'].split(': ')[1], 'record': v['record'],
                      'record_name': v['record_name'], 'layer': v['layer'], 'source': 'world key (pin inside)', 'why': v['why']})
    rec['key_candidates'] = sum(1 for v in kc.values() if v['verdict'].startswith('candidate'))
    todo = [r for r in open_ if r not in kc]
    before = len(layer_urls(cc))
    # STEP B: the programmed finders (the harvester's run_country, re-aimed with the agency table; a fresh pass per stage-1 run)
    c = country_cfg(cc, cfg, table)
    hstate['countries'][cc] = {'status': 'started', 'started': TODAY, 'done': [], 'log': [], 'steps': []}
    H.LIMIT = (time.time() - H.T0) + max(60, min(PER, LIMIT - (time.time() - T0) - 240))   # this country's share of the chunk
    try: H.run_country(cc, c, cfg, hstate, H.KNOWN)
    except Exception as e: notice(f'{cc} finders stopped: {type(e).__name__}: {str(e)[:120]}')  # noqa: BLE001
    finished_b = len((hstate['countries'][cc].get('steps') or [])) >= 7
    # STEP A (b): every polygon layer known for the country, pins first
    lays = layer_urls(cc)
    rec['layers_tried'] = [u for u, *_ in lays]
    if todo and lays:
        R = {r: {'park': P[r][2], 'area': cc, 'hits': [], 'leads': [], 'tried': []} for r in todo if r in P}
        G.layers = lambda area, _l=lays: _l
        G.step_a(cc, list(R), {r: P[r] for r in R}, R)
        for r, x in R.items():
            h = next((h for h in x['hits'] if h.get('tier') == 'SURE'), None) or next((h for h in x['hits'] if h.get('tier') == 'LIKELY'), None)
            if h:
                Q.append({'area': cc, 'ref': r, 'park': x['park'], 'tier': h['tier'], 'why': h['why'], 'kind': h['verdict'], 'record': h['record'], 'record_name': h['record_name'],
                          'acres_approx': h['acres_approx'], 'layer': h['layer'], 'source': 'world finder (pin on a found layer)'})
                rec['layer_candidates'] += 1
            elif not x['hits']:
                t = (K.get(r) or {}).get('t') or ' '.join(re.findall(r"[^\W\d_]+", x['park'])[-2:])   # the POTA kind words = the agency group (P-4)
                rec['no_layer_groups'].setdefault(t.strip().lower() or 'other', []).append(r)
    elif todo:
        rec['no_layer_groups']['(no polygon layer found yet)'] = todo[:50] + (['…'] if len(todo) > 50 else [])
    rec['layers_found_new'] = len(lays) - before
    rec['stage1'] = 'done' if finished_b else 'paused (time): carries on next chunk'
    rec['seconds'] = round(time.time() - t0)
    OUT.mkdir(parents=True, exist_ok=True)
    json.dump(rec, open(OUT / f'{cc}.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    covered = rec['key_candidates'] + rec['layer_candidates']
    notice(f"{cc} COUNT: POTA {len(P)} / open {len(open_)} / candidates: from the key {rec['key_candidates']}, on found layers {rec['layer_candidates']} "
           f"(open -> {len(open_) - covered} still without a candidate) / polygon layers {len(lays)} (+{rec['layers_found_new']} new) / no-layer groups {len(rec['no_layer_groups'])} / {rec['stage1']}")
    return rec


def write_questions(Q, areas_run):
    old = {(q['ref'], str(q['record']), q['layer']): q for q in (load(QF, {}) or {}).get('questions') or []}
    keep = [q for q in old.values() if q['area'] not in areas_run]
    Q = [q for q in Q if not G.LEARNED.said_no(q['ref'], q['record'], q['layer']) or old.get((q['ref'], str(q['record']), q['layer']))]   # a NO is never re-asked
    for q in Q:
        prev = old.get((q['ref'], str(q['record']), q['layer']))
        q.update({'question': "Is this official record that park (the agency's own boundary for it)? YES / NO", 'answer': None, 'checked_by': None, 'how': None,
                  'pota_link': f"https://pota.app/#/park/{q['ref']}"})
        if prev: q.update({k: prev.get(k) for k in ('answer', 'checked_by', 'how', 'rechecked_by_chat2')})
    qs = keep + Q
    QF.parent.mkdir(parents=True, exist_ok=True)
    json.dump({'about': "World finder v2 candidates (stage 1, Fable's plan): chat 11 answers YES / NO against the agency's own map; chat 2 rechecks. 'name mismatch' = the record's name differs from POTA's. Big countries: answer a random sample first and report the hit rate (HQ).",
               'built': TODAY, 'open': sum(1 for q in qs if not q['answer']), 'questions': qs}, open(QF, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    by = {}
    for q in qs: by.setdefault(q['area'], [0, 0]); by[q['area']][0 if q.get('tier', q['kind']) in ('SURE', 'name match') else 1] += 1
    L = ['# World finder v2: questions for chat 11 (stage 1)', '', f'{len(qs)} candidates. Answer in world-finder.json (answer YES / NO, checked_by, how).', '',
         '| country | SURE (chat 2 rechecks, chat 11 samples 10%) | LIKELY (chat 11 grades) |', '|---|---|---|'] + [f'| {cc} | {a} | {b} |' for cc, (a, b) in sorted(by.items(), key=lambda x: -sum(x[1]))]
    QF.with_suffix('.md').write_text('\n'.join(L) + '\n', encoding='utf-8')


def main():
    state = load(OUT / 'state.json', {}) or {}
    pins = all_pins()
    cfg = load(H.OUT / 'countries.json', {}) or {}
    cfg.setdefault('countries', {}); cfg.setdefault('govwords', [])
    table = load(LINKS / '.claude' / 'build' / 'research' / 'WORLD' / 'world_agencies.json', {}) or {}
    hstate = load(H.OUT / 'state.json', {'countries': {}}) or {'countries': {}}
    H.KNOWN = H.already_read()
    want = [x.upper() for x in (os.environ.get('COUNTRIES') or '').split()]
    queue = gap_queue(pins, state)
    if want: queue = [q for q in queue if q[0] in want] or [(cc, list(pins.get(cc, {})), {}) for cc in want if cc in pins]
    Q, ran = [], []
    for cc, open_, K in queue:
        if late(): break
        rec = run_country(cc, open_, K, pins[cc], cfg, table, hstate, Q)
        state[cc] = {'stage1': rec['stage1'], 'run': TODAY, 'touched': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'open': rec['open'], 'candidates': rec['key_candidates'] + rec['layer_candidates']}
        ran.append(cc)
        H.save(H.OUT / 'state.json', hstate)
        json.dump(state, open(OUT / 'state.json', 'w'), indent=1)
    if ran: write_questions(Q, set(ran))
    left = [q[0] for q in gap_queue(pins, state)]
    print(f'LEFT={len(left)}')
    notice(f"ran {len(ran)} countries ({' '.join(ran)[:300]}); {len(left)} still need their stage-1 pass" + (f" (next: {' '.join(left[:8])})" if left else ': STAGE 1 COMPLETE (report to HQ before W9 / W2)'))


if __name__ == '__main__':
    try: main()
    except Exception as e: notice(f'stopped ({type(e).__name__}: {e})')  # noqa: BLE001
    sys.exit(0)
