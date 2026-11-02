#!/usr/bin/env python3
"""Live check of the world outline registry (registry/world_sources.json).

For every entry it really queries the service, at the pins of real POTA parks of that country, and records:
  status: verified (a named record holds a POTA pin and its name matches, tier T-1..T-3) | answers (the service answers,
          no POTA pin matched) | blocked (reason) | error (reason);
  name_field (detected when the entry has none: the text field whose values match POTA's names best);
  test: {ref, park, record, tier, field, date};  sample: {asked, hit, matched}.
It never changes 'grade': EU compilation entries stay 'approximate' (Finder3 rule 2), whatever they score.

  python3 registry/verify.py --pota <folder of program/parks/<CC>.json lists> [--cc CH,GB] [--n 10] [--cache .cache]"""
import argparse, concurrent.futures as cf, datetime as dt, json, pathlib, random, re, sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from core import gis, names                      # noqa: E402
from core.polite import Polite                   # noqa: E402

REG = HERE / 'world_sources.json'
BUF = {'polygon': 0, 'line': 200, 'point': 2000}


def pota_parks(pota_dir, cc):
    p = pathlib.Path(pota_dir) / f'{cc}.json'
    try: return json.load(open(p))
    except Exception: return []  # noqa: BLE001


def pick(parks, entry, n, seed=7):
    rx = re.compile(entry.get('pota_words') or '.', re.I)
    loc = entry.get('pota_locs')
    bb = entry.get('pota_bbox')     # [minlon, minlat, maxlon, maxlat] when POTA has no location code for the region (Wales)
    pool = [p for p in parks if p.get('latitude') is not None and (not loc or any(l in (p.get('locationDesc') or '') for l in loc))
            and (not bb or (bb[0] <= p['longitude'] <= bb[2] and bb[1] <= p['latitude'] <= bb[3]))]
    yes = set(entry.get('yes_refs') or [])          # club pack: the parks a person already said YES to are the best liveness test
    first = [p for p in pool if p.get('reference') in yes]
    random.Random(seed).shuffle(first)
    pool = [p for p in pool if p.get('reference') not in yes]
    want = first[: max(1, n // 2)] + [p for p in pool if rx.search(p.get('name') or '')]
    rest = [p for p in pool if p not in want]
    random.Random(seed).shuffle(want); random.Random(seed).shuffle(rest)
    want.sort(key=lambda p: -(p.get('activations') or 0))
    return (want[: max(1, n * 2 // 3)] + rest)[:n] if want else rest[:n]


def best_field(park_name, attrs):
    best = (0.0, None, None)
    for k, v in (attrs or {}).items():
        if not isinstance(v, str) or len(v) < 3 or re.match(r'^(shape|globalid|guid|uuid|wkt|geom)', k, re.I): continue
        s = names.similarity(park_name, v)
        if s > best[0]: best = (s, k, v)
    return best


def check(P, e, parks, n):
    out = {'date': dt.date.today().isoformat(), 'asked': 0, 'hit': 0, 'matched': 0, 'examples': []}
    fields = {}
    if e.get('status_seed'):           # known-bad from our box: keep it listed as blocked, with the reason and where to retry from
        out.update(status=e['status_seed'], why=e.get('why', '') + (f" (retry from {e['retry_from']})" if e.get('retry_from') else '')); return out
    tested = pick(parks, e, n)
    if not tested: out.update(status='error', why='no POTA parks to test with'); return out
    errs = []
    if e.get('kind') == 'arcgis':      # count query: does the layer answer, and how many records
        r, j = P.get_json(e['url'].rstrip('/') + '/query?' + gis._q({'where': e.get('where') or '1=1', 'returnCountOnly': 'true', 'f': 'json'}), kind='count', ttl_days=14)
        out['count'] = (j or {}).get('count')
        if out['count'] is None and (r.blocked or 'error' in (j or {})):
            why = r.blocked or json.dumps(j.get('error'))[:160]
            if 'oken' in why or '499' in why or '498' in why: why = 'token-only (needs sign-in)'
            out.update(status='blocked' if (r.blocked or why.startswith('token')) else 'error', why=why); return out
    geom = e.get('geometry') or 'polygon'
    for p in tested:
        hits, err = gis.point(P, e, p['latitude'], p['longitude'], buffer_m=BUF.get(geom, 0), ref_=p['reference'])
        out['asked'] += 1
        if err:
            errs.append(err)
            if err.startswith(('blocked', 'token')): break
            continue
        if hits: out['hit'] += 1
        for h in hits:
            nm = h.get('name')
            if not nm or names.similarity(p['name'], nm) < 0.5:
                s, k, v = best_field(p['name'], h['attrs'])
                if s >= 0.5: fields[k] = fields.get(k, 0) + 1; nm = v
            inside, d = (True, 0.0) if h.get('geom') is None else __import__('core.geo', fromlist=['x']).pin_relation(p['latitude'], p['longitude'], h['geom'])
            if geom != 'polygon':      # lines / points: the park's core words in any text field of a feature near the pin
                w = names.core_words(p['name'])
                ok = w and names.words_in_text(w, names.all_text(h['attrs'])) >= (len(w) if len(w) <= 2 else -(-2 * len(w) // 3))
                t = 'NEAR+NAME' if ok else None
            else:
                t, sim = names.tier(p['name'], nm or '', h['attrs'], inside if inside is not None else True, d)
            if t in ('T-1', 'T-2', 'T-3', 'NEAR+NAME'):
                out['matched'] += 1
                if len(out['examples']) < 3:
                    out['examples'].append({'ref': p['reference'], 'park': p['name'], 'record': nm, 'tier': t, 'record_id': h.get('id'),
                                            'geometry_read': h.get('geom') is not None})
                break
    blocked = [x for x in errs if x.startswith(('blocked', 'token'))]
    if out['matched']: out['status'] = 'verified'
    elif blocked: out['status'] = 'blocked'; out['why'] = blocked[0]
    elif out['asked'] and len(errs) == out['asked']: out['status'] = 'error'; out['why'] = errs[0][:200]
    else: out['status'] = 'answers'; out['why'] = 'service answers; no sampled POTA pin matched a record by name' + (f' ({errs[0][:80]})' if errs else '')
    if fields and not e.get('name_field'): out['name_field_detected'] = max(fields, key=fields.get)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pota', required=True); ap.add_argument('--cc', default=''); ap.add_argument('--n', type=int, default=10)
    ap.add_argument('--cache', default=str(HERE.parent / '.cache')); ap.add_argument('--only-unverified', action='store_true')
    ap.add_argument('--id', default=''); ap.add_argument('--registry', default=str(REG)); ap.add_argument('--area', default='')
    a = ap.parse_args()
    reg_path = pathlib.Path(a.registry)
    reg = json.load(open(reg_path))
    P = Polite('KPC park engine: world registry check', cache_dir=a.cache)
    todo = [e for e in reg['sources'] if (not a.cc or e['cc'] in a.cc.split(',')) and (not a.id or e['id'] in a.id.split(','))
            and (not a.area or e.get('area', e['cc']) in a.area.split(','))
            and (not a.only_unverified or ((e.get('live') or {}).get('status') if e.get('pack') else (e.get('verified') or {}).get('status')) != 'verified')]
    def run(e):
        try: return e, check(P, e, pota_parks(a.pota, e.get('test_cc') or e['cc']), a.n)
        except Exception as x: return e, {'status': 'error', 'why': f'{type(x).__name__}: {x}'[:200], 'date': dt.date.today().isoformat()}  # noqa: BLE001
    with cf.ThreadPoolExecutor(8) as ex:
        for e, v in ex.map(run, todo):
            if v.get('name_field_detected') and not e.get('name_field'): e['name_field'] = v['name_field_detected']
            if e.get('pack'): e['live'] = v            # pack entries keep the club's status ('approved' / 'club'); the live check sits beside it
            else: e['verified'] = v
            ex0 = (v.get('examples') or [{}])[0]
            print(f"{e.get('area', e['cc']):6} {e['id']:44} n={v.get('count')} {v['status']:9} {v.get('matched',0)}/{v.get('asked',0)}  {ex0.get('park','')} -> {ex0.get('record','')} {v.get('why','')[:90]}", flush=True)
    reg['checked'] = dt.date.today().isoformat()
    json.dump(reg, open(reg_path, 'w'), indent=1, ensure_ascii=False)
    P.write_blocked(HERE)


if __name__ == '__main__':
    main()
