#!/usr/bin/env python3
"""ONE-TIME KEYED PULL (chat 9; HQ Oct 29 9:50 AM GO, Brandon 9:49 AM 'Go but have sonnet review for accuracy..waiting room
not done'). TEMPORARY: delete this file + kpc-keyed-pull.yml after the run. Never on a schedule, never repeated.

What it asks (ONLY the documented API paths the key covers, via kpc_manners: 2 s per host, back-off, three strikes):
  * developer.nps.gov/api/v1/parkinglots + /campgrounds: only for Park Service units that are on chat 9's MISSING list
    (KPC-Links .claude/build/research/PARKING_Missing_list.json), plus Mammoth Cave campgrounds (Houchin Ferry).
  * ridb.recreation.gov/api/v1/facilities + /recareas: paged per state, only the states that have missing parks (+ KY / TN
    for the Land Between the Lakes self-service camps, Fenton and Breaks).
What it keeps: ONLY points that look like they belong to a MISSING park (rules below); everything goes to a HOLD file
(data/access-leads/keyed-pull-hold.json), NEVER live and never through the waiting room's promote step. Chat 11 checks it
(Sonnet, accuracy), then Brandon's GO.

MATCH RULES (a lead only; chat 11 decides):
  A  NPS parking lot whose relatedParks parkCode = the missing park's own nps.gov code          -> 'nps-own-park'
  B  RIDB facility whose rec area name holds every main name word of the park, within 30 km   -> 'ridb-recarea-name'
  C  RIDB facility whose own name holds every main name word of the park, within 15 km         -> 'ridb-facility-name'
  D  RIDB facility within 1.5 km of the park's POTA pin, no name agreement                     -> 'ridb-near-pin-only' (weak)
  Never kept: ticket / permit / tour / timed-entry / lottery facilities; points at 0,0; points over 30 km from the pin.
Credit on every row: 'Recreation.gov / National Park Service data'."""
import gzip, json, math, os, pathlib, re, sys, time, urllib.parse, urllib.request
sys.path.insert(0, os.path.dirname(__file__))
from kpc_manners import Manners  # noqa: E402

OUT = pathlib.Path('data/access-leads/keyed-pull-hold.json')
RAW = pathlib.Path('data/access-leads/keyed-pull-raw.json.gz')   # the saved copy, so it is never pulled again
MISS = 'https://raw.githubusercontent.com/KentuckyPortableClub/KPC-Links/main/.claude/build/research/PARKING_Missing_list.json'
NK, RK = os.environ.get('NPS_API_KEY', ''), os.environ.get('RIDB_API_KEY', '')
CREDIT = 'Recreation.gov / National Park Service data'
SKIPTYPE = re.compile(r'ticket|permit|tour|timed entry|lottery|library|activity pass|vehicle reservation', re.I)
KIND = set('state national park parks forest forests wildlife management area areas refuge recreation historic historical site '
           'sites scenic river rivers trail trails lake reservoir preserve nature natural wma nwr nf nra sp sra blm the of and at '
           'county regional memorial monument battlefield seashore lakeshore wilderness'.split())
KYCAMPS = ['Fenton', 'Cravens Bay', 'Nickell Branch', 'Birmingham Ferry', 'Smith Bay', 'Sugar Bay', 'Taylor Bay', 'Redd Hollow',
           'Boswell Landing', 'Gatlin Point', 'Turkey Bay', 'Breaks']


def notice(m): print('::notice title=Keyed pull::' + str(m).replace('\n', ' ')[:900], flush=True)


def words(s): return {w for w in re.sub(r'[^a-z0-9 ]', ' ', str(s).lower().replace("'", '')).split() if len(w) > 2 and w not in KIND}


def km(a, b, c, d):
    p = math.pi / 180
    x = math.sin((c - a) * p / 2) ** 2 + math.cos(a * p) * math.cos(c * p) * math.sin((d - b) * p / 2) ** 2
    return 12742 * math.asin(math.sqrt(min(1, x)))


def fnum(v):
    try: return float(v)
    except (TypeError, ValueError): return None


def jget(M, url):
    st, _, body, _ = M.get(url, accept='application/json')
    if st != 200: return None, st
    try: return json.loads(body.decode('utf-8', 'replace')), st
    except Exception: return None, 'badjson'  # noqa: BLE001


def main():
    M = Manners('KPC one-time keyed pull (missing parking points)')
    with urllib.request.urlopen(MISS, timeout=60) as r: miss = json.loads(r.read())['by_state']
    parks = {}   # ref -> dict
    for st, rows in miss.items():
        try: P = json.load(open(f'data/parkinfo/US-{st}.json'))['parks']
        except Exception: P = {}  # noqa: BLE001
        for ref, name, t in rows:
            v = P.get(ref) or []
            la, lo = (v[5], v[6]) if len(v) > 6 else (None, None)
            m = re.search(r'nps\.gov/([a-z]{4})(?:/|$)', str(v[1] if len(v) > 1 else ''), re.I)
            parks[ref] = {'st': st, 'n': name, 't': t, 'la': la, 'lo': lo, 'w': words(name), 'nps': m.group(1).lower() if m else None}
    notice(f'missing parks read: {len(parks)} in {len(miss)} states; NPS units among them: {sum(1 for p in parks.values() if p["nps"])}')
    raw = {'nps_parking': [], 'nps_camps': [], 'ridb_fac': {}, 'ridb_rec': {}}
    stat = {'nps_calls': 0, 'ridb_calls': 0, 'errors': []}

    # ---- NPS: parking lots for the missing Park Service units only (codes in batches of 20) + Mammoth Cave campgrounds
    codes = sorted({p['nps'] for p in parks.values() if p['nps']})
    if NK:
        for i in range(0, len(codes), 20):
            q = urllib.parse.urlencode({'parkCode': ','.join(codes[i:i + 20]), 'limit': 500, 'api_key': NK})
            j, st = jget(M, 'https://developer.nps.gov/api/v1/parkinglots?' + q); stat['nps_calls'] += 1
            if j is None: stat['errors'].append(f'nps parkinglots batch {i}: {st}'); continue
            for z in j.get('data') or []:
                raw['nps_parking'].append({'name': z.get('name'), 'la': fnum(z.get('latitude')), 'lo': fnum(z.get('longitude')),
                                           'parks': [x.get('parkCode') for x in z.get('relatedParks') or []], 'id': z.get('id')})
        j, st = jget(M, 'https://developer.nps.gov/api/v1/campgrounds?' + urllib.parse.urlencode({'parkCode': 'maca', 'limit': 50, 'api_key': NK}))
        stat['nps_calls'] += 1
        for z in (j or {}).get('data') or []:
            raw['nps_camps'].append({'name': z.get('name'), 'la': fnum(z.get('latitude')), 'lo': fnum(z.get('longitude')), 'park': 'maca', 'id': z.get('id')})
    else: stat['errors'].append('no NPS key in the run')

    # ---- RIDB: facilities + rec areas, paged per state (only states with missing parks, + KY/TN for the KY camps)
    sts = sorted(set(miss) | {'KY', 'TN', 'VA'})
    if RK:
        for st in sts:
            for kind, key in (('recareas', 'ridb_rec'), ('facilities', 'ridb_fac')):
                off, rows = 0, []
                while off < 10000:
                    q = urllib.parse.urlencode({'state': st, 'limit': 50, 'offset': off, 'apikey': RK})
                    j, s = jget(M, f'https://ridb.recreation.gov/api/v1/{kind}?' + q); stat['ridb_calls'] += 1
                    if j is None: stat['errors'].append(f'ridb {kind} {st} @{off}: {s}'); break
                    d = j.get('RECDATA') or []
                    for z in d:
                        if kind == 'recareas':
                            rows.append({'id': z.get('RecAreaID'), 'n': z.get('RecAreaName'), 'la': fnum(z.get('RecAreaLatitude')), 'lo': fnum(z.get('RecAreaLongitude'))})
                        else:
                            rows.append({'id': z.get('FacilityID'), 'n': z.get('FacilityName'), 'ty': z.get('FacilityTypeDescription'),
                                         'la': fnum(z.get('FacilityLatitude')), 'lo': fnum(z.get('FacilityLongitude')), 'ra': z.get('ParentRecAreaID')})
                    tot = int(((j.get('METADATA') or {}).get('RESULTS') or {}).get('TOTAL_COUNT') or 0)
                    off += 50
                    if not d or off >= tot: break
                raw[key][st] = rows
            notice(f'RIDB {st}: {len(raw["ridb_rec"].get(st, []))} rec areas, {len(raw["ridb_fac"].get(st, []))} facilities')
    else: stat['errors'].append('no RIDB key in the run')
    RAW.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(RAW, 'wt', encoding='utf-8') as f: json.dump({'made': time.strftime('%Y-%m-%d'), 'credit': CREDIT, **raw}, f, separators=(',', ':'))

    # ---- match (leads only)
    leads, seen = {}, set()

    def add(ref, row):
        k = (ref, round(row['la'], 5), round(row['lo'], 5))
        if k in seen: return
        seen.add(k); leads.setdefault(ref, []).append(row)

    by_code = {}
    for ref, p in parks.items():
        if p['nps']: by_code.setdefault(p['nps'], []).append(ref)
    for z in raw['nps_parking']:
        if not z['la'] or not z['lo']: continue
        for c in z['parks']:
            for ref in by_code.get(c, []):
                p = parks[ref]
                d = km(p['la'], p['lo'], z['la'], z['lo']) if p['la'] is not None else None
                add(ref, {'la': z['la'], 'lo': z['lo'], 'label': f"Parking: {z['name']}", 'src': 'NPS API parkinglots ' + str(z['id']),
                          'rule': 'nps-own-park', 'km': round(d, 2) if d is not None else None})
    for st, fac in raw['ridb_fac'].items():
        rec = {r['id']: r for r in raw['ridb_rec'].get(st, [])}
        mine = [(r, p) for r, p in parks.items() if p['st'] == st and p['la'] is not None and p['w']]
        for f in fac:
            if not f['la'] or not f['lo'] or abs(f['la']) < 1 or SKIPTYPE.search(f'{f.get("ty")} {f.get("n")}'): continue
            fw, rw = words(f['n']), words((rec.get(f.get('ra')) or {}).get('n', ''))
            for ref, p in mine:
                d = km(p['la'], p['lo'], f['la'], f['lo'])
                if d > 30: continue
                rule = ('ridb-recarea-name' if p['w'] <= rw else 'ridb-facility-name' if (p['w'] <= fw and d <= 15)
                        else 'ridb-near-pin-only' if d <= 1.5 else None)
                if rule:
                    add(ref, {'la': f['la'], 'lo': f['lo'], 'label': f"{f.get('ty') or 'Facility'}: {f['n']}", 'src': f'RIDB facility {f["id"]}'
                              + (f" (rec area {rec[f['ra']]['n']})" if f.get('ra') in rec else ''), 'rule': rule, 'km': round(d, 2)})
    # the four KY campgrounds (names only; chat 9 places them by hand after chat 11's check)
    ky = []
    for z in raw['nps_camps']:
        if re.search(r'houchin', z['name'] or '', re.I): ky.append({'camp': 'houchin-ferry-campground', **z, 'src': 'NPS API campgrounds ' + str(z['id'])})
    for st in ('KY', 'TN', 'VA'):
        for f in raw['ridb_fac'].get(st, []):
            for n in KYCAMPS:
                if n.lower() in (f['n'] or '').lower():
                    ky.append({'camp': n, 'name': f['n'], 'type': f.get('ty'), 'la': f['la'], 'lo': f['lo'], 'src': f'RIDB facility {f["id"]}'})
    rules = {}
    for rows in leads.values():
        for r in rows: rules[r['rule']] = rules.get(r['rule'], 0) + 1
    out = {'about': 'HOLD FILE: ONE-TIME keyed pull (chat 9, HQ Oct 29 9:50 AM GO). NOT LIVE. Leads for the US parks on the '
                    'MISSING list (no parking/access point). Chat 11 checks accuracy; live only after chat 11 PASS + Brandon GO. '
                    'Rules in .github/scripts/kpc_keyed_pull.py (A-D).',
           'made': time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime()), 'credit': CREDIT, 'status': 'HOLD',
           'summary': {'missing_parks': len(parks), 'parks_with_leads': len(leads), 'points': sum(len(v) for v in leads.values()),
                       'by_rule': rules, 'nps_calls': stat['nps_calls'], 'ridb_calls': stat['ridb_calls'], 'errors': stat['errors'][:30],
                       'manners': M.stat},
           'ky_camps': ky, 'parks': {r: {'n': parks[r]['n'], 'st': parks[r]['st'], 'pts': v} for r, v in sorted(leads.items())}}
    OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False) + '\n')
    notice(json.dumps(out['summary'])[:850])
    notice('KY camps found: ' + '; '.join(f"{k['camp']} = {k.get('name')} {k.get('la')},{k.get('lo')}" for k in ky)[:800])


if __name__ == '__main__':
    try: main()
    except Exception as e: notice(f'stopped: {e}')  # noqa: BLE001
    sys.exit(0)
