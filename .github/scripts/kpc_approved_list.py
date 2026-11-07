#!/usr/bin/env python3
"""APPROVED BUT NOT ON THE MAP (chat 10, Nov 2 2026; Brandon 4:51 AM 'keys and layers ... something we missing there ... a bot
that is matching that or labeling them'). Chat 11's YES answers live in the question files; the key builders only turn a YES into
an outline when the YES is on a layer that key already reads (US answers writer) or on the world finder file (world answers
writer). Every other YES (collector, second look, gis hunter on a new layer; ALL Canadian collector YES; the world collector YES)
never reaches a key. This bot is the ledger: per area, every park chat 11 said YES to whose key does not show it as official yet,
with the exact record (layer + record id + name field + record name), so the key builders can join BY RECORD ID, not by name.
  data/approved/<AREA>.json   {ref: {layer, record, name_field, record_name, answer, checked_by, from_file, key_now}}
  data/approved/index.json    per area: approved, already official, waiting (the gap), top layers
Reads data/waiting/questions/*.json, the keys (KPC-Links data/us-key + ca-key, KPC-Data data/world-key). Decides nothing. Never fails.
  python3 .github/scripts/kpc_approved_list.py      env LINKS (KPC-Links checkout)"""
import collections, datetime as dt, glob, json, os, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from kpc_json_any import glob_json_any, load_json_any  # noqa: E402
LINKS = pathlib.Path(os.environ.get('LINKS') or '../links')
OUT = pathlib.Path(os.environ.get('APPROVED_OUT') or 'data/approved')   # nightly: branch missing-lists approved/ (replaced each night, no history)


def load(p, d):
    try: return load_json_any(p)
    except Exception: return d  # noqa: BLE001


def key_state():
    import kpc_scoreboard_bot as S
    st = {}
    for f in glob.glob(str(LINKS / 'data/us-key/US-*.json')) + glob.glob(str(LINKS / 'data/ca-key/CA-*.json')) + glob.glob('data/world-key/*.json'):
        for r, v in ((load(f, {}) or {}).get('parks') or {}).items():
            if isinstance(v, dict):
                try: st[r] = S.outline_kind(v)[0]
                except Exception: st[r] = v.get('g') or '?'  # noqa: BLE001
    return st


def area_of(q):
    r = str(q.get('ref') or '')
    if r.startswith(('US-', 'CA-')):
        st = str(q.get('st') or q.get('area') or '')
        st = st[3:] if st[:3] in ('US-', 'CA-') else st
        return f'{r[:2]}-{st}' if len(st) == 2 else r[:2]
    return r.split('-')[0]


def main():
    K = key_state(); A = collections.defaultdict(dict)
    for f in glob_json_any('data/waiting/questions/*.json'):
        d = load(f, None); qs = d.get('questions') if isinstance(d, dict) else d
        if not isinstance(qs, list): continue
        for q in qs:
            if not (isinstance(q, dict) and q.get('ref') and str(q.get('answer') or '').upper().startswith('YES')): continue
            if K.get(q['ref']) == 'official': continue
            lay = str(q.get('layer') or q.get('url') or '')
            A[area_of(q)].setdefault(q['ref'], {'park': q.get('park'), 'layer': lay, 'record': q.get('record'), 'name_field': q.get('name_field'),
                                               'record_name': q.get('record_name'), 'kind': q.get('kind'), 'answer': str(q.get('answer'))[:80],
                                               'checked_by': q.get('checked_by'), 'from_file': pathlib.Path(f).name, 'key_now': K.get(q['ref'], 'not in key')})
    OUT.mkdir(parents=True, exist_ok=True)
    idx = []
    for a, rows in sorted(A.items()):
        json.dump(rows, open(OUT / f'{a}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
        lay = collections.Counter(v['layer'] for v in rows.values()).most_common(3)
        idx.append({'area': a, 'waiting': len(rows), 'key_now': dict(collections.Counter(v['key_now'] for v in rows.values())), 'top_layers': lay})
    for f in OUT.glob('*.json'):
        if f.stem != 'index' and f.stem not in A: f.unlink()
    idx.sort(key=lambda r: -r['waiting'])
    tot = sum(r['waiting'] for r in idx)
    json.dump({'about': __doc__.split('\n')[0], 'built': dt.date.today().isoformat(), 'waiting': tot, 'areas': idx}, open(OUT / 'index.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    reg = collections.Counter(('US' if r['area'].startswith('US') else 'CA' if r['area'].startswith('CA') else 'world') for r in idx for _ in range(r['waiting']))
    print(f'::notice title=Approved, not on the map::{tot} parks chat 11 said YES to are not official in their key yet ({dict(reg)}); per area in data/approved/', flush=True)


if __name__ == '__main__':
    try: main()
    except Exception as e: print(f'::notice title=Approved list::stopped ({type(e).__name__}: {e})')  # noqa: BLE001
