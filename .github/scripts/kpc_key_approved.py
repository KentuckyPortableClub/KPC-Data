#!/usr/bin/env python3
"""JOIN BY RECORD NUMBER: chat 11's YES answers -> the WORLD keys (chat 10, Nov 2 2026; Brandon 4:51 AM 'keys and layers ... something
we missing there ... a bot that is matching that or labeling them', GO 4:58 AM 'Chat 10 builds it now').
The world key builder joins by NAME on its own fixed source list, and its answers writer only reads the world-finder file, so a YES
on any other layer (the collector, the second look, the gis hunter, a hand-downloaded country) never reached a key: about 2,450
world parks chat 11 approved still had no outline (Nov 2 count). This bot adds each one BY RECORD NUMBER, the same way the site
already reads a world key entry: parks[ref].m = [[record id, record name, <label>, 'name (chat 11 YES)']] and
data/world-key/layers.json[<label>] = the layer address (kpc-bounds.js worldKey() asks that layer for that id).
Only when ALL hold: the answer is a plain YES; the layer is an ArcGIS REST layer (…/MapServer/N or /FeatureServer/N); the record
is a whole number; the park has NO outline in the newest copy of its key (the held copy in the waiting room when there is one,
else the live one). A park with an outline is never touched (no swaps here). The changed key files go back INTO THE WAITING
ROOM (held, checked, released only with chat 11's file YES, as Brandon kept it Nov 2). Never fails.
  python3 .github/scripts/kpc_key_approved.py [--dry]"""
import collections, datetime as dt, glob, json, pathlib, re, sys, urllib.parse

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import kpc_scoreboard_bot as S  # noqa: E402

DRY = '--dry' in sys.argv
WK, HELD = pathlib.Path('data/world-key'), pathlib.Path('data/waiting/in/data/world-key')
REST = re.compile(r'^https?://[^?\s]+/(?:MapServer|FeatureServer)/\d+$', re.I)
TODAY = dt.date.today().isoformat()


def load(p, d):
    try: return json.load(open(p, encoding='utf-8'))
    except Exception: return d  # noqa: BLE001


def newest(name):
    h = HELD / name
    return (h, load(h, None)) if h.exists() else (WK / name, load(WK / name, None))


def drawn(v):
    try: return S.outline_kind(v)[0] in ('official', 'padus', 'osm-unofficial')
    except Exception: return bool((v or {}).get('m'))  # noqa: BLE001


def main():
    yes = collections.defaultdict(dict)
    for f in sorted(glob.glob('data/waiting/questions/*.json')):
        d = load(f, None); qs = d.get('questions') if isinstance(d, dict) else d
        if not isinstance(qs, list): continue
        for q in qs:
            if not (isinstance(q, dict) and q.get('ref') and str(q.get('answer') or '').upper().startswith('YES')): continue
            ref = str(q['ref']); cc = ref.split('-')[0]
            if cc in ('US', 'CA') or not re.match(r'^[A-Z0-9]{1,3}$', cc): continue
            lay = str(q.get('layer') or q.get('url') or '').rstrip('/')
            rid = q.get('record')
            if not REST.match(lay) or not (isinstance(rid, int) or (isinstance(rid, str) and rid.isdigit())): continue
            yes[cc].setdefault(ref, (lay, int(rid), str(q.get('record_name') or ''), str(q.get('park') or ''), str(q.get('agency') or ''), pathlib.Path(f).name))
    lp, L = newest('layers.json'); L = L if isinstance(L, dict) else {}
    by_url = {str(u).rstrip('/'): k for k, u in L.items() if isinstance(u, str)}
    pinfo = {}
    added, files, newlab = collections.Counter(), [], 0
    for cc, rows in sorted(yes.items()):
        path, K = newest(f'{cc}.json')
        if not isinstance(K, dict): K = {'cc': cc, 'parks': {}, 'sources': [], 'counts': {}}
        P = K.setdefault('parks', {}); ch = 0
        if cc not in pinfo: pinfo[cc] = (load(f'data/parkinfo/{cc}.json', {}) or {}).get('parks') or {}
        for ref, (lay, rid, rn, pn, ag, src) in rows.items():
            v = P.get(ref)
            if isinstance(v, dict) and drawn(v): continue
            lab = by_url.get(lay)
            if not lab:
                host = urllib.parse.urlsplit(lay).hostname or 'agency'
                lid = lay.rsplit('/', 1)[-1]
                lab = f'{cc}: {(ag or host)[:60]} (approved layer {lid})'
                L[lab] = lay; by_url[lay] = lab; newlab += 1
            pi = pinfo[cc].get(ref) or []
            v = v if isinstance(v, dict) else {'c': [], 'n': pn or (pi[0] if pi else ref), 't': ''}
            v['m'] = [[rid, rn or v.get('n'), lab, 'name (chat 11 YES)']]
            v['approved'] = {'by': 'chat 11 YES', 'from': src, 'joined': TODAY, 'how': 'record number (kpc_key_approved.py)'}
            P[ref] = v; ch += 1
        if ch:
            added[cc] = ch
            if not DRY:
                (WK).mkdir(parents=True, exist_ok=True)
                json.dump(K, open(WK / f'{cc}.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
                files.append(str(WK / f'{cc}.json'))
    if newlab and not DRY:
        json.dump(L, open(WK / 'layers.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1); files.append(str(WK / 'layers.json'))
    print(f'::notice title=Key join by record number::{"(dry) " if DRY else ""}{sum(added.values())} approved world parks added to their keys '
          f'({", ".join(f"{k} {v}" for k, v in added.most_common(12))}); {newlab} new layer labels; the key files go to the waiting room for chat 11', flush=True)
    print('FILES=' + ' '.join(files))


if __name__ == '__main__':
    try: main()
    except Exception as e: print(f'::notice title=Key join by record number::stopped ({type(e).__name__}: {e})')  # noqa: BLE001
