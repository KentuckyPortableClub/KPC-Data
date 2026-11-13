#!/usr/bin/env python3
"""Nov 13 (KPC owner): the post-line check fails when any live pair is gone with no dropped or not-sure row.

  python3 kpc_fers_postline_gate.py --data . [--report data/status/fers-postline/latest.json]
Exit 1 when any area has a (gone) pair. Exit 0 when every lost live pair has a row with a reason.
"""
import argparse, json, gzip, pathlib, sys

LIVE = ('candidate', 'very tight', 'water only')


def load(p):
    p = pathlib.Path(p)
    for q in ((p, pathlib.Path(str(p) + '.gz')) if not str(p).endswith('.gz') else (p, pathlib.Path(str(p)[:-3]))):
        if not q.is_file(): continue
        try:
            return json.loads((gzip.open(q, 'rt', encoding='utf-8').read() if str(q).endswith('.gz') else q.read_text(encoding='utf-8')))
        except (OSError, ValueError): continue
    return None


def pair_key(refs):
    return '+'.join(sorted(map(str, refs or [])))


def live_pairs(doc):
    out = set()
    for s in (doc or {}).get('spots') or []:
        if isinstance(s, dict) and len(s.get('refs') or []) >= 2 and str(s.get('status') or '').startswith(LIVE):
            out.add(pair_key(s['refs']))
    return out


def rows_for(doc, key):
    return [s for s in (doc or {}).get('spots') or [] if isinstance(s, dict) and pair_key(s.get('refs') or []) == key]


def is_explained(rows):
    for s in rows:
        st = str(s.get('status') or '')
        if st.startswith(('dropped', 'not sure', 'merged')): return True
        if st and not st.startswith(('gone', 'candidate', 'very tight', 'water only')): return True
    return False


def hidden_and_live(data):
    data = pathlib.Path(data)
    hidden = data / 'data/waiting/in/data/fers'
    live = data / 'data/fers'
    areas = set()
    for folder in (hidden, live):
        if not folder.is_dir(): continue
        for f in folder.glob('CA-*.json*') + folder.glob('US-*.json*') if False else list(folder.glob('CA-*.json')) + list(folder.glob('CA-*.json.gz')) + list(folder.glob('US-*.json')) + list(folder.glob('US-*.json.gz')):
            name = f.name[:-8] if f.name.endswith('.json.gz') else f.stem
            if name.startswith(('CA-', 'US-')): areas.add(name)
    return hidden, live, sorted(areas)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data', default='.')
    a = ap.parse_args()
    hidden, live, areas = hidden_and_live(a.data)
    gone = []
    for area in areas:
        new = load(hidden / f'{area}.json') or load(hidden / f'{area}.json.gz')
        if new is None: continue  # no hidden file for this area: not this run
        old = load(live / f'{area}.json') or load(live / f'{area}.json.gz') or {}
        for k in sorted(live_pairs(old)):
            rows = rows_for(new, k)
            if not is_explained(rows) and not any(str(s.get('status') or '').startswith(LIVE) for s in rows):
                gone.append(f"{area}: {k} (gone)")
    if gone:
        print('::error title=2-fer post-line::live pair(s) disappeared with no dropped or not-sure row:')
        for g in gone: print('  ' + g)
        return 1
    print('::notice title=2-fer post-line::no silent gone pairs')
    return 0


if __name__ == '__main__':
    sys.exit(main())
