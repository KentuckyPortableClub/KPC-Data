#!/usr/bin/env python3
"""WDPA PHONE BOOK (chat 10, Nov 1 2026; Brandon 7:30 PM: 'we just need to use them as a phone book ... yes use it like that').
WDPA (Protected Planet) as a DIRECTORY, not a map: for every park that still has no OFFICIAL outline, ask WDPA live at the
POTA pin (within 150 m, no shape) which protected area is there and WHO runs it: managing authority, local-language name,
designation, the data provider's metadata id. Those are LEADS: the park-info engine groups its search by that agency (agency-
wide portals / map servers first) and the local name helps the name matching. No WDPA shape is ever stored or passed on
(W-10 terms: no copies, no downloads); only the lookup facts below, on the club's working file.
  data/intake/phonebook.json  {ref: {d: date, h: [{id, name, orig, desig, auth, gov, meta, iso3}]}}   (newest look per park)
  data/intake/phonebook.md    per country: the agencies that run the most parks we still miss (where to look first)
Order: the club's area order (Kentucky, US, Canada, North America, W1-W10, the rest); a park is looked up again after 90 days.
Manners: kpc_manners (one request per 2 s, ArcGIS REST path). MINUTES (45). Never fails.
  python3 .github/scripts/kpc_wdpa_phonebook.py                env LINKS (KPC-Links checkout, for the keys)"""
import collections, datetime as dt, glob, json, os, pathlib, re, sys, time, urllib.parse

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from kpc_manners import Manners  # noqa: E402

FIRST_ERR = []
WAY = [None]
SHAPES = [lambda f: {'outFields': f, 'returnGeometry': 'false', 'resultRecordCount': 5},
          lambda f: {'outFields': f, 'returnGeometry': 'false'},
          lambda f: {'outFields': '*', 'returnGeometry': 'false'},
          lambda f: {'where': '1=1', 'outFields': '*', 'returnGeometry': 'false'}]
M = Manners('KPC WDPA phone book (chat 10): directory lookups only, no shapes')
LAYER = 'https://services5.arcgis.com/Mj0hjvkNtV7NRhA7/arcgis/rest/services/WDPA_v0/FeatureServer/1'   # W-10's approved address
OUT, MD = pathlib.Path('data/intake/phonebook.json'), pathlib.Path('data/intake/phonebook.md')
LINKS = pathlib.Path(os.environ.get('LINKS') or '../links')
LIMIT = float(os.environ.get('MINUTES') or 45) * 60; T0 = time.time(); TODAY = dt.date.today()
WANT = {'id': ('wdpaid', 'wdpa_pid'), 'name': ('name',), 'orig': ('orig_name',), 'desig': ('desig_eng', 'desig'), 'auth': ('mang_auth',),
        'gov': ('gov_type',), 'meta': ('metadataid',), 'iso3': ('iso3',)}


def load(p, d):
    try: return json.load(open(p, encoding='utf-8'))
    except Exception: return d  # noqa: BLE001


def get(params):
    st, hd, body, final = M.get(LAYER + '/query?' + urllib.parse.urlencode({**params, 'f': 'json'}), accept='application/json', timeout=90)
    if not (isinstance(st, int) and st < 400 and body): FIRST_ERR.append(str(st)); return None, str(st)
    try: j = json.loads(body.decode('utf-8', 'replace'))
    except ValueError: FIRST_ERR.append('not json: ' + body[:80].decode('utf-8', 'replace')); return None, 'not json'
    if isinstance(j, dict) and j.get('error'):
        FIRST_ERR.append('error ' + str(j['error'].get('code')) + ': ' + str(j['error'].get('message'))[:80] + ' ' + str(j['error'].get('details') or '')[:80]); return None, str(j['error'].get('message'))[:80]
    return j, ''


def official():
    s = set()
    for f in glob.glob('data/*-key/*.json') + glob.glob(str(LINKS / 'data' / '*-key' / '*.json')):
        for r, v in ((load(f, {}) or {}).get('parks') or {}).items():
            if isinstance(v, dict) and v.get('g') == 'official': s.add(r)
    return s


def parks():
    P = {}
    for f in glob.glob('data/pota/t/*.json'):
        for row in load(f, []) or []:
            if isinstance(row, list) and len(row) >= 4 and row[2] is not None and (row[2], row[3]) != (0, 0): P[row[0]] = (row[2], row[3], row[1])
    return P


def rank(ref):
    try:
        import kpc_order as O
        cc = ref.split('-')[0]
        return (0 if ref.startswith('US-') else 1, O.rank('W-' + cc) if cc not in ('US', 'CA') else 0, ref)
    except Exception: return (9, 0, ref)  # noqa: BLE001


def main():
    B = load(OUT, {}) or {}
    meta, err = None, ''
    st, hd, body, final = M.get(LAYER + '?f=json', accept='application/json', timeout=40)
    try: meta = json.loads(body.decode('utf-8', 'replace')) if isinstance(st, int) and st < 400 else None
    except ValueError: meta = None
    if not meta or not meta.get('fields'): print(f'::notice title=WDPA phone book::the WDPA service did not answer ({st}): nothing looked up'); return
    have = {f['name'].lower(): f['name'] for f in meta['fields']}
    pick = {k: next((have[c] for c in cands if c in have), None) for k, cands in WANT.items()}
    fields = ','.join(v for v in pick.values() if v)
    off, P = official(), parks()
    todo = sorted((r for r in P if r not in off and not (B.get(r) and (TODAY - dt.date.fromisoformat(B[r]['d'])).days < 90)), key=rank)
    n = hits = 0
    for ref in todo:
        if time.time() - T0 > LIMIT: break
        la, lo, _ = P[ref]
        dx, dy = 0.00135 / max(0.2, __import__('math').cos(__import__('math').radians(la))), 0.00135   # about 150 m each way (R-G12)
        env = {'geometry': f'{lo - dx},{la - dy},{lo + dx},{la + dy}', 'geometryType': 'esriGeometryEnvelope', 'inSR': 4326, 'spatialRel': 'esriSpatialRelIntersects'}
        if WAY[0] is None:   # Nov 2: the first lookups failed silently; try the query shapes one after the other and keep the one the service takes
            for i, extra in enumerate(SHAPES):
                j, err = get({**env, **extra(fields)})
                if j is not None: WAY[0] = i; break
            if WAY[0] is None:
                if len(FIRST_ERR) > 12: break
                continue
        else:
            j, err = get({**env, **SHAPES[WAY[0]](fields)})
        if j is None:
            if err in ('rest', 'robots'): break   # the host is resting: stop, next run goes on
            continue
        h = []
        for ft in (j.get('features') or [])[:3]:
            a = ft.get('attributes') or {}
            h.append({k: a.get(v) for k, v in pick.items() if v and a.get(v) not in (None, '', 'Not Reported')})
        B[ref] = {'d': TODAY.isoformat(), 'h': h}; n += 1; hits += bool(h)
    json.dump(B, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    # where to look first: per country, the agencies that run the most parks we still miss
    by = collections.defaultdict(collections.Counter)
    for r, v in B.items():
        if r in off: continue
        for x in (v.get('h') or [])[:1]:
            if x.get('auth'): by[r.split('-')[0]][x['auth']] += 1
    L = ['# WDPA phone book: who runs the parks we still miss', f'Built {TODAY} by kpc_wdpa_phonebook.py (directory lookups only; no WDPA shapes kept).',
         'Per country, the managing agencies of parks with no official outline yet, most parks first: their own portals / map servers are where the official layer lives.', '']
    for cc in sorted(by, key=lambda c: -sum(by[c].values())):
        L.append(f"- **{cc}** ({sum(by[cc].values())} parks): " + '; '.join(f'{a} ({c})' for a, c in by[cc].most_common(5)))
    MD.write_text('\n'.join(L) + '\n', encoding='utf-8')
    left = len(todo) - n
    print(f'::notice title=WDPA phone book::{n} parks looked up ({hits} inside a WDPA area), {left} left; {len(B)} in the book', flush=True)
    if n == 0:   # nothing looked up (the service failing / resting): no chain, try again on the timer
        print(f'::warning title=WDPA phone book::stopped early, the service refused every query shape: {FIRST_ERR[:4]}; the next timed run tries again'); left = 0
    print(f'LEFT={left}')


if __name__ == '__main__':
    try: main()
    except Exception as e: print(f'::notice title=WDPA phone book::stopped ({type(e).__name__}: {e})')  # noqa: BLE001
