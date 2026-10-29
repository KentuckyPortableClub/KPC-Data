#!/usr/bin/env python3
"""KEYED PULL HOLD FILE v3 (chat 9, Oct 29; HQ rulings 11:22-11:27 AM from Brandon 11:21-11:25). TEMPORARY: delete with
kpc-keyed-v3.yml after the run. NO new calls to Recreation.gov or the Park Service: it rebuilds the hold file from the SAVED
copy (data/access-leads/keyed-pull-raw.json.gz) and tests each point against the park's own outline (the saved outlines the
US key joins, boundary-cache release on KPC-Links).

v3 RULES
  keep  A  NPS parking lot of that park's own nps.gov code (inside or outside)
  keep  C  Recreation.gov facility whose own name holds every main name word of the park (<= 15 km)
  keep  B  Recreation.gov facility whose rec area name holds every main name word (<= 30 km)
  -> every kept point gets 'where': inside / edge (<= 100 m) / outside (km from the outline) / no outline (km from the pin)
  -> OUTSIDE points stay only when tied by name (A/C/B), labelled 'nearby, outside the park line' (Brandon 11:22);
     B outside the line stays only within 5 km of the outline (or 3 km of the pin when the park has no outline)
  keep  lookouts, visitor centers, lodges, campgrounds (Brandon 11:21-11:24); campgrounds = access points only (no camp facts outside KY)
  drop  rule D (nearest thing, no name), offices / headquarters / ranger stations, cabins, museums, hotels
  one facility = one park (best rule, then the park whose outline holds it, then nearest); positive US longitudes flipped (Acadia)
Still HOLD: chat 11 samples it; live only with Brandon's GO."""
import gzip, json, math, os, pathlib, re, sys, time
LIB = pathlib.Path(os.environ.get('LINKS_SCRIPTS') or 'links/.github/scripts')
sys.path.insert(0, str(LIB))
import kpc_match as KM  # noqa: E402
import kpc_near_miss as NM  # noqa: E402

RAW = pathlib.Path('data/access-leads/keyed-pull-raw.json.gz')
OUT = pathlib.Path('data/access-leads/keyed-pull-hold.json')
MISS = os.environ.get('MISS_URL') or 'https://raw.githubusercontent.com/KentuckyPortableClub/KPC-Links/main/.claude/build/research/PARKING_Missing_list.json'
CREDIT = 'Recreation.gov / National Park Service data'
SKIPTYPE = re.compile(r'ticket|permit|tour|timed entry|lottery|library|activity pass|vehicle reservation', re.I)
DROP = re.compile(r'\boffice\b|headquarters|\bhq\b|ranger station|\bcabins?\b|museum|hotel|\binn\b|motel', re.I)
CAMP = re.compile(r'campground|\bcamp\b|camping|group site', re.I)
KIND = set('state national park parks forest forests wildlife management area areas refuge recreation historic historical site '
           'sites scenic river rivers trail trails lake reservoir preserve nature natural wma nwr nf nra sp sra blm the of and at '
           'county regional memorial monument battlefield seashore lakeshore wilderness'.split())
RANK = {'nps-own-park': 0, 'ridb-facility-name': 1, 'ridb-recarea-name': 2}


def notice(m): print('::notice title=Keyed pull v3::' + str(m).replace('\n', ' ')[:900], flush=True)


def words(s): return {w for w in re.sub(r'[^a-z0-9 ]', ' ', str(s).lower().replace("'", '')).split() if len(w) > 2 and w not in KIND}


def km(a, b, c, d):
    p = math.pi / 180
    x = math.sin((c - a) * p / 2) ** 2 + math.cos(a * p) * math.cos(c * p) * math.sin((d - b) * p / 2) ** 2
    return 12742 * math.asin(math.sqrt(min(1, x)))


def main():
    import urllib.request
    with urllib.request.urlopen(MISS, timeout=60) as r: miss = json.loads(r.read())['by_state']
    with gzip.open(RAW, 'rt', encoding='utf-8') as f: raw = json.load(f)
    K = NM.lib('kpc_us_key.py', '\nfor st in STATES:'); K['CACHE'] = NM.CUS
    parks, outl = {}, {}
    for st, rows in miss.items():
        try: P = json.load(open(f'data/parkinfo/US-{st}.json'))['parks']
        except Exception: P = {}  # noqa: BLE001
        try: KEY = json.load(open(f'data/us-key/US-{st}.json'))['parks']
        except Exception: KEY = {}  # noqa: BLE001
        got = K['load_cache'](st)
        recs = {str(a.get('OBJECTID', a.get('oid'))): a for a in (got[0] if got else [])}
        for ref, name, t in rows:
            v = P.get(ref) or []
            la, lo = (v[5], v[6]) if len(v) > 6 else (None, None)
            m = re.search(r'nps\.gov/([a-z]{4})(?:/|$)', str(v[1] if len(v) > 1 else ''), re.I)
            parks[ref] = {'st': st, 'n': name, 't': t, 'la': la, 'lo': lo, 'w': words(name), 'nps': m.group(1).lower() if m else None}
            gs = [recs[str(x[0])]['_g'] for x in (KEY.get(ref) or {}).get('m') or [] if x and str(x[0]) in recs]
            if gs: outl[ref] = gs
    notice(f'{len(parks)} missing parks, {len(outl)} with a saved outline')

    def where(ref, la, lo):
        gs = outl.get(ref)
        p = parks[ref]
        if not gs:
            d = km(p['la'], p['lo'], la, lo) if p['la'] is not None else None
            return ('no outline', round(d, 2) if d is not None else None)
        d = min((KM.km_to(la, lo, g) for g in gs), key=lambda x: 9e9 if x is None else x)
        if d is None: return ('no outline', None)
        return ('inside' if d == 0 else 'edge' if d <= 0.1 else 'outside', round(d, 2))

    cand, drop = [], {'D': 0, 'label': 0, 'B_outside_far': 0, 'shared': 0}
    by_code = {}
    for ref, p in parks.items():
        if p['nps']: by_code.setdefault(p['nps'], []).append(ref)
    for z in raw['nps_parking']:
        if not z.get('la') or not z.get('lo'): continue
        for c in z.get('parks') or []:
            for ref in by_code.get(c, []):
                cand.append((ref, 'nps-own-park', z['la'], z['lo'], f"Parking: {z['name']}", 'NPS API parkinglots ' + str(z['id'])))
    for st, fac in raw['ridb_fac'].items():
        rec = {r['id']: r for r in raw['ridb_rec'].get(st, [])}
        mine = [(r, p) for r, p in parks.items() if p['st'] == st and p['la'] is not None and p['w']]
        for f in fac:
            if not f.get('la') or not f.get('lo') or abs(f['la']) < 1 or SKIPTYPE.search(f'{f.get("ty")} {f.get("n")}'): continue
            fw, rw = words(f['n']), words((rec.get(f.get('ra')) or {}).get('n', ''))
            for ref, p in mine:
                d = km(p['la'], p['lo'], f['la'], f['lo'])
                if d > 30: continue
                rule = 'ridb-recarea-name' if p['w'] <= rw else 'ridb-facility-name' if (p['w'] <= fw and d <= 15) else None
                if not rule:
                    if d <= 1.5: drop['D'] += 1
                    continue
                lab = ('Campground: ' + f['n']) if CAMP.search(f'{f.get("ty")} {f["n"]}') else f"{f.get('ty') or 'Facility'}: {f['n']}"
                cand.append((ref, rule, f['la'], f['lo'], lab, f'RIDB facility {f["id"]}' + (f" (rec area {rec[f['ra']]['n']})" if f.get('ra') in rec else '')))
    rows, flipped = [], 0
    for ref, rule, la, lo, lab, src in cand:
        if lo > 0: lo = -lo; flipped += 1
        if DROP.search(lab): drop['label'] += 1; continue
        w, d = where(ref, la, lo)
        if rule == 'ridb-recarea-name' and ((w == 'outside' and d > 5) or (w == 'no outline' and (d is None or d > 3))): drop['B_outside_far'] += 1; continue
        if w == 'outside': lab += ' (nearby, outside the park line)'
        rows.append({'ref': ref, 'rule': rule, 'la': la, 'lo': lo, 'label': lab, 'src': src, 'where': w, 'km': d})
    best = {}
    for r in rows:
        k = r['src'].split(' (')[0]
        sc = (RANK[r['rule']], 0 if r['where'] in ('inside', 'edge') else 1, r['km'] if r['km'] is not None else 99)
        if k not in best or sc < best[k][0]: best[k] = (sc, r['ref'])
    out_parks, seen = {}, set()
    for r in rows:
        if best[r['src'].split(' (')[0]][1] != r['ref']: drop['shared'] += 1; continue
        key = (r['ref'], round(r['la'], 5), round(r['lo'], 5))
        if key in seen: continue
        seen.add(key)
        ref = r.pop('ref'); out_parks.setdefault(ref, {'n': parks[ref]['n'], 'st': parks[ref]['st'], 'outline': ref in outl, 'pts': []})['pts'].append(r)
    old = json.load(open(OUT)) if OUT.exists() else {}
    by_rule, by_where = {}, {}
    for v in out_parks.values():
        for p in v['pts']:
            by_rule[p['rule']] = by_rule.get(p['rule'], 0) + 1; by_where[p['where']] = by_where.get(p['where'], 0) + 1
    res = {'about': 'HOLD FILE v3: ONE-TIME keyed pull (chat 9), rebuilt from the saved copy with HQ\'s Oct 29 11:22-11:27 rulings '
                    '(no new calls). NOT LIVE. Rules in KPC-Data .github/scripts/kpc_keyed_v3.py (git history). Chat 11 samples; live only with Brandon\'s GO.',
           'made': time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime()), 'credit': CREDIT, 'status': 'HOLD', 'version': 3,
           'summary': {'missing_parks': len(parks), 'with_outline': len(outl), 'parks_with_points': len(out_parks),
                       'points': sum(len(v['pts']) for v in out_parks.values()), 'by_rule': by_rule, 'by_where': by_where,
                       'dropped': drop, 'lon_flipped': flipped, 'v1': (old.get('summary') or {}).get('points')},
           'ky_camps': old.get('ky_camps', []), 'parks': dict(sorted(out_parks.items()))}
    OUT.write_text(json.dumps(res, indent=1, ensure_ascii=False) + '\n')
    notice(json.dumps(res['summary'])[:850])


if __name__ == '__main__':
    try: main()
    except Exception as e: notice(f'stopped: {e}')  # noqa: BLE001
    sys.exit(0)
